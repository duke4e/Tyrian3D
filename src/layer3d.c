/*
 * Tyrian3D: depth-layer capture of the 2D game screen. See layer3d.h.
 */
#include "layer3d.h"

#include "debugmode.h"

#include "models3d.h"
#include "volume3d.h"

#include "sprite.h"
#include "video.h"

#include <assert.h>
#include <math.h>
#include <string.h>

bool l3d_enabled = false;
bool l3d_capturing = false;
static bool frame_ready = false;

L3DFrame l3d_frame;
Uint32 l3d_frame_number = 0;

typedef enum
{
	PHASE_NONE,
	PHASE_FULL,
	PHASE_DRAW,
	PHASE_MODIFY,
} PhaseKind;

static PhaseKind phase_kind = PHASE_NONE;
static L3DLayerType phase_type;

static Uint8 snapshot[L3D_WIDTH * L3D_ROWS];
static Uint8 owner[L3D_WIDTH * L3D_ROWS];  // topmost layer per pixel, 0xff for none

_Static_assert(L3D_OVERSCAN == SCREEN_OVERSCAN_MAX, "layer rows must cover the screen overscan");

// First row of the current drawing surface, including its overscan rows.
static const Uint8 *surface_rows(const SDL_Surface *surface)
{
	assert(surface_has_overscan(surface));
	return (const Uint8 *)surface->pixels - L3D_OVERSCAN * surface->pitch;
}

static const struct
{
	const char *name;
	float height;
} layer_info[L3D_LAYER_TYPE_COUNT] = {
	[L3D_GROUND]       = { "ground",       0.0f },
	[L3D_BG2_LOW]      = { "bg2-low",      6.0f },
	[L3D_GROUND_ENEMY] = { "ground-enemy", 4.0f },
	[L3D_BG2]          = { "bg2",         12.0f },
	[L3D_SKY_ENEMY]    = { "sky-enemy",   22.0f },
	[L3D_BG3]          = { "bg3",         32.0f },
	[L3D_TOP_ENEMY]    = { "top-enemy",   38.0f },
	[L3D_PLAYER]       = { "player",      44.0f },
	[L3D_EXPLOSION]    = { "explosion",   46.0f },
	[L3D_BG2_OVER]     = { "bg2-over",    52.0f },
	[L3D_BG3_OVER]     = { "bg3-over",    56.0f },
	[L3D_OVERLAY]      = { "overlay",      0.0f },
};

float l3d_terrain_headroom = 0;

float l3d_layer_height(L3DLayerType type)
{
	// Above the ground and its enemies, room for the terrain's raised ground (render_gpu.c).
	const bool above = type != L3D_GROUND && type != L3D_GROUND_ENEMY && type != L3D_OVERLAY;
	return layer_info[type].height + (above ? l3d_terrain_headroom : 0.0f);
}

const char *l3d_layer_name(L3DLayerType type)
{
	return layer_info[type].name;
}

// The surface the current phase began on (VGAScreen then: the game's screen, or VGAScreen2 while
// smoothies draw), for ending a frame a menu interrupts (menus switch VGAScreen; l3d_frame_end_early).
static const SDL_Surface *phase_surface = NULL;
static bool ending_early = false;

static void take_snapshot(void)
{
	const SDL_Surface *surface = VGAScreen;
	phase_surface = surface;
	const Uint8 *rows = surface_rows(surface);
	for (int y = 0; y < L3D_ROWS; ++y)
		memcpy(snapshot + y * L3D_WIDTH, rows + y * surface->pitch, L3D_WIDTH);
}

static L3DLayer *new_layer(L3DLayerType type)
{
	L3DFrame *frame = &l3d_frame;

	// Consecutive phases of the same type share a layer.
	if (frame->layer_count > 0 && frame->layers[frame->layer_count - 1].type == type)
		return &frame->layers[frame->layer_count - 1];

	// Out of layers: fold into the topmost one, which keeps the draw order intact.
	if (frame->layer_count == L3D_MAX_LAYERS)
		return &frame->layers[L3D_MAX_LAYERS - 1];

	L3DLayer *layer = &frame->layers[frame->layer_count++];
	layer->type = type;
	memset(layer->cover, 0, sizeof(layer->cover));
	layer->min_y = L3D_ROWS;
	layer->max_y = 0;
	return layer;
}

static void end_phase(void)
{
	const SDL_Surface *surface = ending_early && phase_surface != NULL ? phase_surface : VGAScreen;
	assert(surface->w == L3D_WIDTH && surface->h == L3D_HEIGHT);
	const Uint8 *rows = surface_rows(surface);

	switch (phase_kind)
	{
	case PHASE_NONE:
		break;

	case PHASE_FULL:
	{
		L3DLayer *layer = new_layer(phase_type);
		const Uint8 layer_id = (Uint8)(layer - l3d_frame.layers);
		for (int y = 0; y < L3D_ROWS; ++y)
			memcpy(layer->index + y * L3D_WIDTH, rows + y * surface->pitch, L3D_WIDTH);
		memset(layer->cover, 1, sizeof(layer->cover));
		memset(owner, layer_id, sizeof(owner));
		layer->min_y = 0;
		layer->max_y = L3D_ROWS;
		break;
	}

	case PHASE_DRAW:
	case PHASE_MODIFY:
	{
		L3DLayer *layer = NULL;
		Uint8 layer_id = 0xff;

		for (int y = 0; y < L3D_ROWS; ++y)
		{
			const Uint8 *row = rows + y * surface->pitch;
			const Uint8 *old_row = snapshot + y * L3D_WIDTH;

			if (memcmp(row, old_row, L3D_WIDTH) == 0)
				continue;

			for (int x = 0; x < L3D_WIDTH; ++x)
			{
				if (row[x] == old_row[x])
					continue;

				const int i = y * L3D_WIDTH + x;

				if (phase_kind == PHASE_DRAW)
				{
					if (layer == NULL)
					{
						layer = new_layer(phase_type);
						layer_id = (Uint8)(layer - l3d_frame.layers);
					}
					layer->index[i] = row[x];
					layer->cover[i] = 1;
					owner[i] = layer_id;
					if (y < layer->min_y)
						layer->min_y = y;
					if (y + 1 > layer->max_y)
						layer->max_y = y + 1;
				}
				else if (owner[i] != 0xff)
				{
					l3d_frame.layers[owner[i]].index[i] = row[x];
				}
			}
		}
		break;
	}
	}
}

void l3d_frame_begin(L3DLayerType first_type)
{
	frame_ready = false;
	if (!l3d_enabled || debug_flight_replaying())
		return;

	++l3d_frame_number;
	l3d_frame.layer_count = 0;
	l3d_frame.object_count = 0;
	l3d_frame.background_count = 0;
	l3d_frame.star_count = 0;
	l3d_frame.glow_count = 0;
	l3d_frame.filter_hue = -99;
	l3d_frame.filter_brightness = -99;
	memset(owner, 0xff, sizeof(owner));

	l3d_capturing = true;
	phase_surface = VGAScreen;
	phase_kind = PHASE_FULL;
	phase_type = first_type;
}

void l3d_phase(L3DLayerType type)
{
	if (!l3d_capturing)
		return;

	end_phase();
	take_snapshot();
	phase_kind = PHASE_DRAW;
	phase_type = type;
}

void l3d_modify(void)
{
	if (!l3d_capturing)
		return;

	end_phase();
	take_snapshot();
	phase_kind = PHASE_MODIFY;
}

void l3d_frame_end_early(void)
{
	ending_early = true;
	l3d_frame_end();
	ending_early = false;
}

void l3d_frame_end(void)
{
	if (!l3d_capturing)
		return;

	end_phase();
	phase_kind = PHASE_NONE;
	l3d_capturing = false;
	frame_ready = true;
}

bool l3d_take_frame(void)
{
	const bool ready = frame_ready;
	frame_ready = false;
	return ready;
}

L3DLayerType l3d_current_layer(void)
{
	return phase_type;
}

bool l3d_add_object(int model, float x, float y, float height, float yaw, float roll, Uint8 filter)
{
	if (!l3d_capturing)
		return false;
	if (l3d_frame.object_count == L3D_MAX_OBJECTS)
		return true;  // drop it rather than mixing a sprite into the frame

	L3DObject *object = &l3d_frame.objects[l3d_frame.object_count++];
	memset(object, 0, sizeof(*object));
	object->model = model;
	object->x = x;
	object->y = y;
	object->layer = phase_type;
	object->height = height;
	object->yaw = yaw;
	object->roll = roll;
	object->filter = filter;
	return true;
}

void l3d_wreck_last_object(void)
{
	if (l3d_capturing && l3d_frame.object_count > 0)
		l3d_frame.objects[l3d_frame.object_count - 1].wreck = true;
}

void l3d_ghost_last_object(void)
{
	if (l3d_capturing && l3d_frame.object_count > 0)
		l3d_frame.objects[l3d_frame.object_count - 1].ghost = true;
}

// Where keyed objects were in the frames they were last seen in (open addressing by key).
#define MOTION_SLOTS 2048
#define MOTION_MAX_STEP 24.0f  // game pixels a frame; more is a jump

static struct
{
	Uint32 key;    // 0 = free
	Uint32 frame;  // l3d_frame_number when seen
	float x, y;
} motion[MOTION_SLOTS];

static bool last_key_new = false;

void l3d_key_last_object(Uint32 key, float *vx, float *vy)
{
	last_key_new = false;
	float dx = 0, dy = 0;
	if (l3d_capturing && l3d_frame.object_count > 0 && key != 0)
	{
		L3DObject *object = &l3d_frame.objects[l3d_frame.object_count - 1];
		Uint32 slot = (key * 2654435761u) % MOTION_SLOTS;
		for (int probe = 0; probe < 16; ++probe, slot = (slot + 1) % MOTION_SLOTS)
		{
			const bool stale = motion[slot].frame + 2 < l3d_frame_number;
			if (motion[slot].key == key || motion[slot].key == 0 || stale)
			{
				last_key_new = !(motion[slot].key == key && motion[slot].frame + 1 == l3d_frame_number);
				if (motion[slot].key == key && motion[slot].frame + 1 == l3d_frame_number)
				{
					dx = object->x - motion[slot].x;
					dy = object->y - motion[slot].y;
					if (fabsf(dx) > MOTION_MAX_STEP || fabsf(dy) > MOTION_MAX_STEP)
						dx = dy = 0;
				}
				motion[slot].key = key;
				motion[slot].frame = l3d_frame_number;
				motion[slot].x = object->x;
				motion[slot].y = object->y;
				break;
			}
		}
		object->vx = dx;
		object->vy = dy;
	}
	if (vx != NULL)
		*vx = dx;
	if (vy != NULL)
		*vy = dy;
}

float l3d_pointer_lead[2];

void l3d_open_last_object(Uint8 sides)
{
	if (l3d_capturing && l3d_frame.object_count > 0)
		l3d_frame.objects[l3d_frame.object_count - 1].open_sides = sides;
}

void l3d_layer_last_object(L3DLayerType type)
{
	if (l3d_capturing && l3d_frame.object_count > 0)
		l3d_frame.objects[l3d_frame.object_count - 1].layer = type;
}

void l3d_pointer_last_object(void)
{
	if (l3d_capturing && l3d_frame.object_count > 0)
		l3d_frame.objects[l3d_frame.object_count - 1].pointer = true;
}

void l3d_new_object_velocity(float vx, float vy, float *out_vx, float *out_vy)
{
	L3DObject *object = l3d_capturing && l3d_frame.object_count > 0 ? &l3d_frame.objects[l3d_frame.object_count - 1] : NULL;
	if (object != NULL && last_key_new)
	{
		object->vx = vx;
		object->vy = vy;
	}
	if (out_vx != NULL)
		*out_vx = object != NULL ? object->vx : 0;
	if (out_vy != NULL)
		*out_vy = object != NULL ? object->vy : 0;
}

bool l3d_key_position(Uint32 key, float *x, float *y)
{
	Uint32 slot = (key * 2654435761u) % MOTION_SLOTS;
	for (int probe = 0; probe < 16; ++probe, slot = (slot + 1) % MOTION_SLOTS)
		if (motion[slot].key == key)
		{
			*x = motion[slot].x;
			*y = motion[slot].y;
			return true;
		}
	return false;
}

bool l3d_key_seen(Uint32 key)
{
	Uint32 slot = (key * 2654435761u) % MOTION_SLOTS;
	for (int probe = 0; probe < 16; ++probe, slot = (slot + 1) % MOTION_SLOTS)
		if (motion[slot].key == key)
			return motion[slot].frame + 1 >= l3d_frame_number;
	return false;
}

bool l3d_add_shot(const void *sheet, unsigned int sprite, int x, int y, Uint32 key)
{
	if (!l3d_capturing || !m3d_enabled)
		return false;
	// A model of its own (models.cfg "shot" lines), or the sprite with volume.
	M3DAppearance look;
	if (m3d_shot_appearance(sheet == &spriteSheet12, sprite, &look))
	{
		const float yaw = look.yaw + (look.spin != 0 ? fmodf(look.spin * l3d_frame_number + (float)(key & 63) * 47.0f, 360.0f) : 0.0f);
		if (!l3d_add_object(look.model, x + 6.0f, y + 7.0f, look.height, yaw, 0.0f, 0))
			return false;
	}
	else if (!l3d_add_volume(sheet, sprite, false, V3D_STYLE_FLAT, x + 6.0f, y + 7.0f, 0.0f, 0.0f, 0.0f, 0))
		return false;
	float vx, vy;
	l3d_key_last_object(key, &vx, &vy);
	l3d_add_glow(sheet, sprite, x, y);
	l3d_last_glow_velocity(vx, vy);
	return true;
}

#define MAX_DEPARTED 96
#define DEPARTED_FAR (-280)  // game pixels: where they are gone for good
#define L3D_KEY_DEPARTED 0x60000u

static struct
{
	const void *sheet;
	Uint16 sprite;
	float x, y, vx, vy;
	bool live;
} departed[MAX_DEPARTED];

void l3d_shot_departed(const void *sheet, unsigned int sprite, int x, int y, int vx, int vy)
{
	if (!l3d_enabled || vy >= 0)
		return;
	for (int i = 0; i < MAX_DEPARTED; ++i)
		if (!departed[i].live)
		{
			departed[i].sheet = sheet;
			departed[i].sprite = (Uint16)sprite;
			departed[i].x = (float)x;
			departed[i].y = (float)y;
			departed[i].vx = (float)vx;
			departed[i].vy = (float)vy;
			departed[i].live = true;
			return;
		}
}

void l3d_draw_departed_shots(void)
{
	for (int i = 0; i < MAX_DEPARTED; ++i)
	{
		if (!departed[i].live)
			continue;
		departed[i].x += departed[i].vx;
		departed[i].y += departed[i].vy;
		if (departed[i].y < DEPARTED_FAR || !l3d_capturing)
		{
			departed[i].live = false;
			continue;
		}
		if (l3d_add_volume(departed[i].sheet, departed[i].sprite, false, V3D_STYLE_FLAT, departed[i].x + 6.0f,
		                   departed[i].y + 7.0f, 0.0f, 0.0f, 0.0f, 0))
		{
			l3d_key_last_object(L3D_KEY_DEPARTED + (Uint32)i, NULL, NULL);
			l3d_add_glow(departed[i].sheet, departed[i].sprite, (int)departed[i].x, (int)departed[i].y);
			l3d_last_glow_velocity(departed[i].vx, departed[i].vy);
		}
	}
}

void l3d_clear_departed_shots(void)
{
	memset(departed, 0, sizeof(departed));
}

void l3d_last_glow_velocity(float vx, float vy)
{
	if (l3d_capturing && l3d_frame.glow_count > 0)
	{
		l3d_frame.glows[l3d_frame.glow_count - 1].vx = vx;
		l3d_frame.glows[l3d_frame.glow_count - 1].vy = vy;
	}
}

bool l3d_add_volume(const void *sheet, unsigned int sprite, bool large, int style, float x, float y, float height,
                    float yaw, float roll, Uint8 filter)
{
	if (!l3d_add_object(L3D_VOLUME, x, y, height, yaw, roll, filter))
		return false;
	if (l3d_frame.object_count > 0)
	{
		L3DObject *object = &l3d_frame.objects[l3d_frame.object_count - 1];
		if (object->model == L3D_VOLUME)
		{
			object->sheet = sheet;
			object->sprite = (Uint16)sprite;
			object->large = large;
			object->style = (Uint8)style;
		}
	}
	return true;
}

void l3d_add_background(int set, Uint8 **top_row, Uint8 **position, Uint8 **wrap, Uint8 **wrap_to,
                        int x, int top_y, bool blend)
{
	if (!l3d_capturing || l3d_frame.background_count == L3D_MAX_BACKGROUNDS)
		return;

	L3DBackground *background = &l3d_frame.backgrounds[l3d_frame.background_count++];
	// The phase's layer exists from here on, even if the background changes no pixel on screen.
	background->layer = (int)(new_layer(phase_type) - l3d_frame.layers);
	background->set = (Uint8)set;
	background->blend = blend;
	background->top_row = top_row;
	background->position = position;
	background->wrap = wrap;
	background->wrap_to = wrap_to;
	background->x = x;
	background->top_y = top_y;
	background->effect_count = 0;
}

void l3d_add_star(Uint16 position, Uint8 color, bool bright)
{
	if (!l3d_capturing || l3d_frame.star_count == L3D_MAX_STARS)
		return;

	if (l3d_frame.star_count == 0)
		l3d_frame.star_layer = (int)(new_layer(phase_type) - l3d_frame.layers);
	L3DStar *star = &l3d_frame.stars[l3d_frame.star_count++];
	star->position = position;
	star->color = color;
	star->bright = bright;
}

// What the 3D view needs to know of a sprite's colours, cached per sheet and sprite.
typedef struct
{
	Uint8 glow;  // palette index of the brightest pixel (by the shade within its ramp, then
	             // coloured over grey), or 0
	Uint8 ramp;  // ramp of the main colour
} SpriteColors;

static SpriteColors sprite_colors(const Sprite2_array *sheet, unsigned int sprite, bool large)
{
	enum { SHEETS = 6, SPRITES = 1024 };
	static const void *cached_sheet[SHEETS];
	static const Uint8 *cached_data[SHEETS];
	static SpriteColors cached_colors[SHEETS][2][SPRITES];
	static bool cached[SHEETS][2][SPRITES];
	static SDL_Surface *scratch = NULL;

	const SpriteColors none = { 0, 0 };
	int slot = -1;
	for (int i = 0; i < SHEETS; ++i)
		if (cached_sheet[i] == sheet && cached_data[i] == sheet->data)
			slot = i;
	if (slot < 0)
	{
		static int next = 0;
		slot = next;
		next = (next + 1) % SHEETS;
		cached_sheet[slot] = sheet;
		cached_data[slot] = sheet->data;
		memset(cached[slot], 0, sizeof(cached[slot]));
	}
	if (sprite >= SPRITES)
		return none;
	if (cached[slot][large][sprite])
		return cached_colors[slot][large][sprite];

	if (scratch == NULL)
		scratch = SDL_CreateSurface(48, 48, SDL_PIXELFORMAT_INDEX8);
	SpriteColors result = none;
	if (scratch != NULL)
	{
		SDL_FillSurfaceRect(scratch, NULL, 0);
		(large ? blit_sprite2x2 : blit_sprite2)(scratch, 8, 8, *sheet, sprite);
		int best_score = -1;
		unsigned int ramp_use[16] = { 0 };
		for (int y = 0; y < scratch->h; ++y)
			for (int x = 0; x < scratch->w; ++x)
			{
				const Uint8 index = ((const Uint8 *)scratch->pixels)[y * scratch->pitch + x];
				if (index == 0)
					continue;
				const int score = (index & 0x0f) * 16 + (index >> 4 != 0);  // a bright shade, coloured if possible
				if (score > best_score)
				{
					best_score = score;
					result.glow = index;
				}
				if ((index & 0x0f) >= 3)
					++ramp_use[index >> 4];
			}
		for (int r = 1; r < 16; ++r)
			if (ramp_use[r] > ramp_use[result.ramp])
				result.ramp = (Uint8)r;
	}
	cached[slot][large][sprite] = true;
	cached_colors[slot][large][sprite] = result;
	return result;
}

static void add_glow(float x, float y, float size, float strength, Uint8 color)
{
	if (!l3d_capturing || l3d_frame.glow_count == L3D_MAX_GLOWS || color == 0)
		return;
	L3DGlow *glow = &l3d_frame.glows[l3d_frame.glow_count++];
	glow->x = x;
	glow->y = y;
	glow->vx = glow->vy = 0;
	glow->size = size;
	glow->strength = strength;
	glow->layer = (Uint8)phase_type;
	glow->color = color;
}

bool l3d_add_color_glow(float x, float y, float size, float strength, Uint8 color, float vx, float vy)
{
	if (!l3d_capturing || l3d_frame.glow_count == L3D_MAX_GLOWS || color == 0)
		return false;
	add_glow(x, y, size, strength, color);
	l3d_last_glow_velocity(vx, vy);
	return true;
}

void l3d_add_glow(const void *sheet, unsigned int sprite, int x, int y)
{
	if (l3d_capturing)
		add_glow(x + 6.0f, y + 7.0f, 13.0f, 0.7f, sprite_colors(sheet, sprite, false).glow);
}

void l3d_add_sprite_glow(const void *sheet, unsigned int sprite, bool large, float x, float y, float size,
                         float strength)
{
	// A light shade of the main colour: the brightest pixel is often a white highlight.
	if (l3d_capturing)
		add_glow(x, y, size, strength, (Uint8)(sprite_colors(sheet, sprite, large).ramp << 4 | 11));
}

Uint8 l3d_sprite_ramp(const void *sheet, unsigned int sprite, bool large)
{
	return sprite_colors(sheet, sprite, large).ramp;
}

void l3d_add_effect(L3DEffect effect, int param)
{
	if (!l3d_capturing)
		return;

	for (int i = 0; i < l3d_frame.background_count; ++i)
	{
		L3DBackground *background = &l3d_frame.backgrounds[i];
		if (background->effect_count == L3D_MAX_EFFECTS)
			continue;
		background->effects[background->effect_count] = (Uint8)effect;
		background->effect_params[background->effect_count] = (Uint8)param;
		++background->effect_count;
	}
}

void l3d_set_filter(int hue, int brightness)
{
	l3d_frame.filter_hue = hue;
	l3d_frame.filter_brightness = brightness;
}
