/*
 * Tyrian3D: depth-layer capture of the 2D game screen. See layer3d.h.
 */
#include "layer3d.h"

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

void l3d_set_filter(int hue, int brightness)
{
	l3d_frame.filter_hue = hue;
	l3d_frame.filter_brightness = brightness;
}
