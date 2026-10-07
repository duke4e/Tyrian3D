/*
 * Tyrian3D: depth-layer capture of the 2D game screen. See layer3d.h.
 */
#include "layer3d.h"

#include "sprite.h"
#include "video.h"

#include <assert.h>
#include <string.h>

bool l3d_enabled = false;
bool l3d_capturing = false;
static bool frame_ready = false;

L3DFrame l3d_frame;

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

float l3d_layer_height(L3DLayerType type)
{
	return layer_info[type].height;
}

const char *l3d_layer_name(L3DLayerType type)
{
	return layer_info[type].name;
}

static void take_snapshot(void)
{
	const SDL_Surface *surface = VGAScreen;
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
	const SDL_Surface *surface = VGAScreen;
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
	if (!l3d_enabled)
		return;

	l3d_frame.layer_count = 0;
	l3d_frame.object_count = 0;
	l3d_frame.background_count = 0;
	l3d_frame.star_count = 0;
	l3d_frame.glow_count = 0;
	l3d_frame.filter_hue = -99;
	l3d_frame.filter_brightness = -99;
	memset(owner, 0xff, sizeof(owner));

	l3d_capturing = true;
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

// The palette index of a 1x1 sprite's brightest pixel (by the palette's shade within its ramp,
// then by the ramp's own brightness), cached per sheet and sprite.
static Uint8 sprite_glow_color(const Sprite2_array *sheet, unsigned int sprite)
{
	enum { SHEETS = 4, SPRITES = 1024 };
	static const void *cached_sheet[SHEETS];
	static const Uint8 *cached_data[SHEETS];
	static Uint8 cached_color[SHEETS][SPRITES];
	static bool cached[SHEETS][SPRITES];
	static SDL_Surface *scratch = NULL;

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
		return 0;
	if (cached[slot][sprite])
		return cached_color[slot][sprite];

	if (scratch == NULL)
		scratch = SDL_CreateSurface(32, 32, SDL_PIXELFORMAT_INDEX8);
	Uint8 best = 0;
	if (scratch != NULL)
	{
		SDL_FillSurfaceRect(scratch, NULL, 0);
		blit_sprite2(scratch, 8, 8, *sheet, sprite);
		int best_score = -1;
		for (int y = 0; y < scratch->h; ++y)
			for (int x = 0; x < scratch->w; ++x)
			{
				const Uint8 index = ((const Uint8 *)scratch->pixels)[y * scratch->pitch + x];
				const int score = (index & 0x0f) * 16 + (index >> 4 != 0);  // a bright shade, coloured if possible
				if (index != 0 && score > best_score)
				{
					best_score = score;
					best = index;
				}
			}
	}
	cached[slot][sprite] = true;
	cached_color[slot][sprite] = best;
	return best;
}

void l3d_add_glow(const void *sheet, unsigned int sprite, int x, int y)
{
	if (!l3d_capturing || l3d_frame.glow_count == L3D_MAX_GLOWS)
		return;
	const Uint8 color = sprite_glow_color(sheet, sprite);
	if (color == 0)
		return;
	L3DGlow *glow = &l3d_frame.glows[l3d_frame.glow_count++];
	glow->x = x + 6.0f;
	glow->y = y + 7.0f;
	glow->layer = (Uint8)phase_type;
	glow->color = color;
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
