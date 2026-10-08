/*
 * Tyrian3D: GPU presentation through the BTBH renderer. See render_gpu.h.
 */
#include "render_gpu.h"

#include "background3d.h"
#include "backgrnd.h"
#include "config.h"
#include "devtools.h"
#include "font.h"
#include "fonthand.h"
#include "mainint.h"
#include "player.h"
#include "models3d.h"
#include "palette.h"
#include "particles3d.h"
#include "picload.h"
#include "paths3d.h"
#include "settings3d.h"
#include "sprite.h"
#include "varz.h"
#include "volume3d.h"

#include <btbh_gpu/btbh_gpu.h>

#include "cgltf.h"
#include "pcxmast.h"

#include <zlib.h>

#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define SCREEN_W 320
#define SCREEN_H 200

// Each layer gets a slot in one atlas texture; the padding rows keep nearest sampling at the
// slot edges from picking up the neighbouring layer.
#define ATLAS_SLOT_H (L3D_ROWS + 8)
#define ATLAS_H (ATLAS_SLOT_H * L3D_MAX_LAYERS)

// Layer heights increase in draw order by at least this much, so layers of equal nominal height
// don't fight in the depth buffer (with room for the background tiles just below each layer).
#define LAYER_STEP 0.1f

// Background map tiles and starfield pixels drawn per frame, at most.
#define MAX_TILES 6144
#define MAX_STARS 4096
#define DEEP_STARS 720  // the deep starfield's stars, all layers (add_deep_star_batch)
// Wrecks (L3DObject.wreck): their height and brightness.
#define WRECK_SLUMP 0.45f
#define WRECK_SHADE 0.3f
#define MAX_CLOUD_PUFFS 4096  // the clouds' puffs (add_cloud_puffs)
#define MAX_PLANTS 12000      // plants drawn per frame (vegetation)

// Direction the sun's light travels: from above and the top left of the screen, as the sprites
// are lit. TYR3D_SUN=<x>,<y>,<z> overrides it, for tuning.
static float sun_direction[3] = { 0.6f, -1.0f, 0.6f };

// The models' light: a strong sun and a dim sky, for contrast like the sprites' shading. Energies
// relative to the sky's irradiance (set_environment); TYR3D_LIGHTING=<sun>,<sky> overrides them.
#define SUN_ENERGY 4.0f
#define SKY_FILL 0.3f

RGPUCamera rgpu_camera = {
	.tilt_degrees = 20.0f,
	.fov_degrees = 30.0f,
	.height_scale = 1.0f,
};

static BTBHGPUDevice *device = NULL;
static BTBHGPUWindow *window = NULL;
static BTBHGPUShaderFormat shader_format;

static BTBHGPUTexture *screen_texture = NULL;  // 2D screen / HUD overlay, 320x200
// The HUD panel in the 3D view, four times the screen's resolution (hud_panel_hd).
#define PANEL_HD_SCALE 4
#define PANEL_HD_W ((SCREEN_W - L3D_PLAYFIELD_W) * PANEL_HD_SCALE)
#define PANEL_HD_H (SCREEN_H * PANEL_HD_SCALE)
static BTBHGPUTexture *panel_texture = NULL;
static BTBHGPUTexture *panel_art = NULL;  // an upscaled picture of the panel, or NULL (hud_panel_hd)
static BTBHGPUTexture *layer_atlas = NULL;     // 3D layers, 320 x ATLAS_H
static BTBHGPUTexture *tile_atlas = NULL;      // background map tiles (background3d.h)
static BTBHGPUTexture *white_texture = NULL;   // 1x1, for flat-coloured quads
static BTBHGPUTexture *particle_texture = NULL;  // a soft round dot
static BTBHGPUTexture *fire_texture = NULL;      // a billowing puff (fire and smoke particles)
static BTBHGPUTexture *ring_texture = NULL;      // a soft ring (shock waves)
static BTBHGPUCustomMesh *billboard_mesh = NULL;  // unit quad in the XY plane, centred
// Filtered backgrounds composed on the CPU (background3d.h): a square slot per background.
#define COMPOSED_SIZE 1024
static BTBHGPUTexture *composed_texture = NULL;
static BTBHGPUCustomMesh *quad_mesh = NULL;    // unit quad in the XZ plane
// The unit quad darkening by B3D_BEYOND_FADE towards its left or right edge.
static BTBHGPUCustomMesh *fade_meshes[2] = { NULL, NULL };

typedef struct
{
	BTBHGPUModel *gpu;
	bool load_attempted;
	uint32_t material_count;
	BTBHGPUModelMaterialInfo materials[16];
	int palette_index[16];  // per material: the palette index that colours it, or -1
	float center[3];
	float half[3];    // half the size of its bounds, model units
	float footprint;  // larger of width and depth, model units
} LoadedModel;

// What an up-facing surface shows of its albedo in the models' light (tools/blender/tyrkit.py
// calibrates materials with the same value).
#define MODEL_UP_FACING_LIGHT 1.16f

static LoadedModel loaded_models[M3D_MAX_MODELS];

typedef struct VolumeSheet VolumeSheet;
static void forget_volume_sheets(void);
static void forget_hd_sheets(void);
static Uint32 hash_colors(const Uint32 colors[256]);
static void forget_terrain(void);
static float cloud_noise(float x, float z, float cell, Uint32 seed);

static Uint32 screen_rgba[SCREEN_W * SCREEN_H];

// Darkness over the whole window on spotlight levels (see build_spotlight).
#define SPOT_W 320
#define SPOT_H 200
static BTBHGPUTexture *spot_texture = NULL;
static BTBHGPUTexture *showcase_texture = NULL;  // the store's picture under its ship (rgpu_present_showcase)

// The modern HUD's quads (build_modern_hud), drawn over the screen's: coloured, or from the HUD's
// text texture (white text, tinted).
typedef struct
{
	float x, y, w, h;
	float u0, v0, u1, v1;
	float left[4], right[4];  // colours at the left and right edges
	bool text;
} HudQuad;

#define MAX_HUD_QUADS 160
#define HUD_TEXT_W 256  // the text texture's size in the fonts' pixels (it holds them at 4x)
#define HUD_TEXT_H 64
static HudQuad hud_quads[MAX_HUD_QUADS];
static int hud_quad_count = 0;
static BTBHGPUTexture *hud_text_texture = NULL;
static Uint32 spot_rgba[SPOT_W * SPOT_H];
static Uint32 atlas_rgba[L3D_WIDTH * ATLAS_H];

// Water glints (the renderer's GLINTS surface): masks of the water in the layers and the tiles,
// in the blue channel, laid out as layer_atlas and tile_atlas.
static BTBHGPUTexture *layer_water = NULL;
static BTBHGPUTexture *tile_water = NULL;
static BTBHGPUTexture *composed_water = NULL;
#define CLOUD_TEXELS 512   // canvas size in texels
#define CLOUD_SCALE 3      // game pixels per texel
#define MAX_CLOUD_CANVASES 2
static BTBHGPUTexture *cloud_texture = NULL;  // CLOUD_TEXELS x CLOUD_TEXELS * MAX_CLOUD_CANVASES
static BTBHGPUTexture *puff_texture = NULL;   // a cumulus puff (create_puff_texture)
static Uint32 layer_water_rgba[L3D_WIDTH * ATLAS_H];
static float glint_time = 0;  // seconds of game time, for the waves

// Frames shown between the game's ticks (rgpu_present_3d_ahead) show the last captured frame moved
// on by `ahead` ticks: backgrounds scroll on, objects and particles keep their velocity.
static float ahead = 0;
static float background_speed[4];  // by map set 1-3: game pixels a tick down the screen

// Wave scale, strength, sharpness and tilt; TYR3D_GLINTS=<scale>,<strength>,<sharpness>,<tilt>
// overrides them, for tuning.
static float glint_parameters[4] = { 1.0f, 0.5f, 140.0f, 3.0f };

// Bloom (M7): light from what the scene shows brighter than white (shots' glows, explosions,
// emissive parts, highlights), spread around it. The palette's colours never get past white, so
// the ground, sprites and HUD don't bloom. Intensity, threshold, knee and radius;
// TYR3D_BLOOM=<intensity>,<threshold>,<knee>,<radius> overrides them (intensity 0: none).
static float bloom_parameters[4] = { 0.5f, 1.0f, 0.1f, 1.2f };

// Whether a colour is water: blue to cyan and fairly bright (Tyrian's water and ice).
static bool water_color(Uint32 color)
{
	const Uint8 *c = (const Uint8 *)&color;
	const int r = c[0], g = c[1], b = c[2];
	const int max = SDL_max(r, SDL_max(g, b)), min = SDL_min(r, SDL_min(g, b));
	if (max < 90 || max - min < max / 4 || b < r)
		return false;
	// Hue in degrees, for blue-dominant colours: from cyan (180) to blue (240).
	const float hue = max == b ? 240.0f - 60.0f * (g - r) / (float)(max - min) : 180.0f - 60.0f * (b - r) / (float)(max - min);
	return hue >= 175.0f && hue <= 235.0f;
}

static Uint32 water_mask(Uint32 color)
{
	const Uint8 rgba[4] = { 0, 0, water_color(color) ? 255 : 0, 255 };
	Uint32 mask;
	memcpy(&mask, rgba, 4);
	return mask;
}

// Layers of background maps (where water is), as opposed to sprites and text.
static bool background_layer(L3DLayerType type)
{
	return type == L3D_GROUND || type == L3D_BG2_LOW || type == L3D_BG2 || type == L3D_BG3 ||
	       type == L3D_BG2_OVER || type == L3D_BG3_OVER;
}

// Backgrounds' surfaces with the Effects setting: the sun's glints on water (where mask says), and
// a gentle relief from the pixels' brightness that the explosions' lights bring out (a negative
// normal scale, see the fork's shader).
#define BACKGROUND_RELIEF 3.0f

// The level's water colour (linear), for the procedural water.
static float water_rgb[3] = { 0.02f, 0.06f, 0.12f };

static void set_glints(BTBHGPUSceneGeometryBatch *b, BTBHGPUTexture *mask)
{
	if (!settings3d.effects)
		return;
	b->normal_scale = -BACKGROUND_RELIEF;
	// Water (where mask says) is procedural water: waves, the sky, the sun's highlights, foam.
	b->surface_variant = BTBH_GPU_SCENE_SURFACE_PIXEL_WATER;
	b->orm_texture = mask;
	b->surface_time = glint_time;
	b->surface_parameters0[0] = 1.0f;    // wave scale
	b->surface_parameters0[1] = SDL_getenv("TYR3D_WATER_SUN") != NULL ? (float)SDL_atof(SDL_getenv("TYR3D_WATER_SUN")) : 1.0f;  // highlights
	b->surface_parameters0[2] = 900.0f;  // their sharpness
	memcpy(b->surface_parameters1, water_rgb, sizeof(water_rgb));
	b->surface_parameters1[3] = 0.3f;    // how much of the tiles' own waves show
	if (SDL_getenv("TYR3D_DEBUG_WATER") != NULL)  // the water red, to see where it is
	{
		b->surface_parameters1[0] = 1.0f;
		b->surface_parameters1[1] = 0.0f;
		b->surface_parameters1[2] = 0.0f;
	}
}

// The tile atlas has pages coloured with different palettes: the frame's colours, and those
// colours as recoloured by a level's filters (water, lava, ice).
#define TILE_PAGES 4
static Uint8 tile_indices[B3D_ATLAS_W * B3D_ATLAS_H];
static Uint8 tile_opaque[B3D_ATLAS_W * B3D_ATLAS_H];
static Uint8 tile_ground[B3D_ATLAS_W * B3D_ATLAS_H];
static Uint32 tile_rgba[B3D_ATLAS_W * B3D_ATLAS_H];
static bool tile_indices_valid = false;
static unsigned int tile_indices_generation;  // b3d_map_generation of tile_indices
static struct
{
	bool valid;
	unsigned int generation;  // b3d_map_generation it was coloured for
	Uint32 colors_hash;
	bool ground_zero;         // colour 0 of background 1 is drawn (a filter recolours it)
	unsigned int used;        // frame it was last used in
} tile_pages[TILE_PAGES];
static unsigned int tile_frame = 0;

static Uint8 *readback_rgba = NULL;
static size_t readback_capacity = 0;

static char shader_dir[1024];

enum
{
	SH_MODEL_VERT,
	SH_ANIMATED_MODEL_VERT,
	SH_SHADOW_FAST_VERT,
	SH_SHADOW_FAST_FRAG,
	SH_SHADOW_VERT,
	SH_ANIMATED_SHADOW_VERT,
	SH_SHADOW_FRAG,
	SH_MODEL_FRAG,
	SH_MODEL_UNSHADOWED_FRAG,
	SH_POST_VERT,
	SH_POST_FRAG,
	SH_CANVAS_VERT,
	SH_CANVAS_FRAG,
	SH_CANVAS_TEXTURED_FRAG,
	SH_COUNT
};

static const char *const shader_names[SH_COUNT] = {
	[SH_MODEL_VERT]            = "production_model.vert",
	[SH_ANIMATED_MODEL_VERT]   = "production_animated_model.vert",
	[SH_SHADOW_FAST_VERT]      = "production_shadow_fast.vert",
	[SH_SHADOW_FAST_FRAG]      = "production_shadow_fast.frag",
	[SH_SHADOW_VERT]           = "production_shadow.vert",
	[SH_ANIMATED_SHADOW_VERT]  = "production_animated_shadow.vert",
	[SH_SHADOW_FRAG]           = "production_shadow.frag",
	[SH_MODEL_FRAG]            = "production_model.frag",
	[SH_MODEL_UNSHADOWED_FRAG] = "production_model_unshadowed.frag",
	[SH_POST_VERT]             = "production_post.vert",
	[SH_POST_FRAG]             = "production_post.frag",
	[SH_CANVAS_VERT]           = "production_canvas.vert",
	[SH_CANVAS_FRAG]           = "production_canvas.frag",
	[SH_CANVAS_TEXTURED_FRAG]  = "production_canvas_textured.frag",
};

static char shader_paths[SH_COUNT][1200];

static void die(const char *what, const char *message)
{
	fprintf(stderr, "error: %s: %s\n", what, message);
	exit(EXIT_FAILURE);
}

static BTBHGPUTexture *create_texture_filtered(int width, int height, BTBHGPUTextureColorSpace color_space,
                                               BTBHGPUTextureFilter filter)
{
	Uint32 *zeroes = calloc((size_t)width * height, sizeof(Uint32));
	if (zeroes == NULL)
		die("failed to create GPU texture", "out of memory");
	BTBHGPUTextureReport report;
	BTBHGPUTexture *texture = btbh_gpu_window_texture_create_rgba8_ex(
		window, (const uint8_t *)zeroes, width, height, 0,
		filter, BTBH_GPU_TEXTURE_WRAP_CLAMP, color_space, &report);
	free(zeroes);
	if (texture == NULL)
		die("failed to create GPU texture", report.message);
	return texture;
}

static BTBHGPUTexture *create_texture(int width, int height, BTBHGPUTextureColorSpace color_space)
{
	return create_texture_filtered(width, height, color_space, BTBH_GPU_TEXTURE_FILTER_NEAREST);
}

// The maps' tiles and the layers smoothly filtered (TYR3D_FILTER=0: as pixels).
static BTBHGPUTextureFilter map_filter(void)
{
	const char *value = SDL_getenv("TYR3D_FILTER");
	return value != NULL && SDL_atoi(value) == 0 ? BTBH_GPU_TEXTURE_FILTER_NEAREST : BTBH_GPU_TEXTURE_FILTER_LINEAR;
}

// Filtered, a tile's texture is sampled from its first pixel's centre to its last's (half a pixel in
// from its cell's edges), so the cell's border, which repeats the tile's edge rather than going on
// into the tile beside it in the map, never shows as a seam.
static float tile_inset(void)
{
	return map_filter() == BTBH_GPU_TEXTURE_FILTER_LINEAR ? 0.5f : 0.0f;
}

// Gives clear pixels the colour of an opaque neighbour (still clear), so filtering doesn't darken
// the edges of what is drawn towards the clear pixels' black.
static void bleed_into_clear(Uint32 *rgba, int width, int first_row, int rows)
{
	static Uint32 *copy = NULL;
	static size_t capacity = 0;
	const size_t size = (size_t)width * (size_t)rows;
	if (capacity < size)
	{
		free(copy);
		copy = malloc(size * sizeof(Uint32));
		capacity = copy != NULL ? size : 0;
		if (copy == NULL)
			return;
	}
	Uint32 *const area = rgba + (size_t)first_row * width;
	memcpy(copy, area, size * sizeof(Uint32));
	for (int y = 0; y < rows; ++y)
		for (int x = 0; x < width; ++x)
		{
			Uint32 *p = &area[(size_t)y * width + x];
			if ((*p >> 24) != 0)
				continue;
			const Uint32 *c = &copy[(size_t)y * width + x];
			const Uint32 n = x > 0 && (c[-1] >> 24) != 0 ? c[-1]
			               : x + 1 < width && (c[1] >> 24) != 0 ? c[1]
			               : y > 0 && (c[-width] >> 24) != 0 ? c[-width]
			               : y + 1 < rows && (c[width] >> 24) != 0 ? c[width] : 0;
			*p = n & 0x00ffffff;
		}
}

static BTBHGPUCustomMesh *create_quad_mesh(float left_brightness, float right_brightness)
{
	typedef struct
	{
		float position[3];
		float normal[3];
		float uv[2];
		float tangent[4];
		float color[4];
		float joints[4];
		float weights[4];
	} Vertex;

	const float l = left_brightness, r = right_brightness;
	const Vertex vertices[4] = {
		{ { 0, 0, 0 }, { 0, 1, 0 }, { 0, 0 }, { 1, 0, 0, 1 }, { l, l, l, 1 }, { 0 }, { 0 } },
		{ { 1, 0, 0 }, { 0, 1, 0 }, { 1, 0 }, { 1, 0, 0, 1 }, { r, r, r, 1 }, { 0 }, { 0 } },
		{ { 1, 0, 1 }, { 0, 1, 0 }, { 1, 1 }, { 1, 0, 0, 1 }, { r, r, r, 1 }, { 0 }, { 0 } },
		{ { 0, 0, 1 }, { 0, 1, 0 }, { 0, 1 }, { 1, 0, 0, 1 }, { l, l, l, 1 }, { 0 }, { 0 } },
	};
	const uint32_t indices[6] = { 0, 1, 2, 0, 2, 3 };

	BTBHGPUCustomMeshReport report;
	BTBHGPUCustomMesh *mesh = btbh_gpu_window_custom_mesh_create(window, vertices, sizeof(vertices), 4, indices, 6, &report);
	if (mesh == NULL)
		die("failed to create quad mesh", report.message);
	return mesh;
}

// The unit quad in the XY plane centred on the origin, for camera-facing billboards.
static BTBHGPUCustomMesh *create_billboard_mesh(void)
{
	typedef struct
	{
		float position[3];
		float normal[3];
		float uv[2];
		float tangent[4];
		float color[4];
		float joints[4];
		float weights[4];
	} Vertex;

	const Vertex vertices[4] = {
		{ { -0.5f, -0.5f, 0 }, { 0, 0, 1 }, { 0, 1 }, { 1, 0, 0, 1 }, { 1, 1, 1, 1 }, { 0 }, { 0 } },
		{ { 0.5f, -0.5f, 0 }, { 0, 0, 1 }, { 1, 1 }, { 1, 0, 0, 1 }, { 1, 1, 1, 1 }, { 0 }, { 0 } },
		{ { 0.5f, 0.5f, 0 }, { 0, 0, 1 }, { 1, 0 }, { 1, 0, 0, 1 }, { 1, 1, 1, 1 }, { 0 }, { 0 } },
		{ { -0.5f, 0.5f, 0 }, { 0, 0, 1 }, { 0, 0 }, { 1, 0, 0, 1 }, { 1, 1, 1, 1 }, { 0 }, { 0 } },
	};
	const uint32_t indices[6] = { 0, 1, 2, 0, 2, 3 };
	BTBHGPUCustomMeshReport report;
	BTBHGPUCustomMesh *mesh = btbh_gpu_window_custom_mesh_create(window, vertices, sizeof(vertices), 4, indices, 6, &report);
	if (mesh == NULL)
		die("failed to create billboard mesh", report.message);
	return mesh;
}

// White, with an alpha that falls off smoothly from the middle: particles take their colour from
// their instances.
static BTBHGPUTexture *create_particle_texture(void)
{
	enum { SIZE = 64 };
	static Uint32 pixels[SIZE * SIZE];
	for (int y = 0; y < SIZE; ++y)
		for (int x = 0; x < SIZE; ++x)
		{
			const float dx = (x + 0.5f) / SIZE * 2 - 1, dy = (y + 0.5f) / SIZE * 2 - 1;
			const float d = SDL_min(1.0f, sqrtf(dx * dx + dy * dy));
			const float a = (1 - d) * (1 - d) * (1 + 2 * d);  // smooth falloff to 0 at the edge
			const Uint8 rgba[4] = { 255, 255, 255, (Uint8)(255 * a) };
			memcpy(&pixels[y * SIZE + x], rgba, 4);
		}
	BTBHGPUTexture *texture = create_texture_filtered(SIZE, SIZE, BTBH_GPU_TEXTURE_COLOR_SPACE_LINEAR, BTBH_GPU_TEXTURE_FILTER_LINEAR);
	btbh_gpu_texture_update_rgba8(texture, (const uint8_t *)pixels, 0, 0, SIZE, SIZE);
	return texture;
}

// A cumulus puff: a cluster of round lobes, lit from the top left towards the viewer (puffs face
// the camera), brighter on top, greyer underneath, with soft wispy edges. Instances colour it, and
// turn, flip and stretch it, so that the puffs differ.
#define PUFF_VARIANTS 1

static BTBHGPUTexture *create_puff_texture(void)
{
	enum { CELL = 128, SIZE = CELL };
	static Uint32 pixels[SIZE * SIZE];
	static const float light[3] = { -0.5f, -0.62f, 0.6f };  // towards the light: left, up the texture, out
	for (int v = 0; v < PUFF_VARIANTS; ++v)
	{
		// Lobes: a big one in the middle, smaller ones round it and above (cumulus heap up).
		float lobes[5][3];
		Uint32 seed = 0x9e3779b9u * (Uint32)(v + 1);
		int count = 0;
		lobes[count][0] = 0.0f;
		lobes[count][1] = 0.08f;
		lobes[count][2] = 0.52f;
		++count;
		for (; count < 5; ++count)
		{
			seed = seed * 1664525u + 1013904223u;
			const float a = (seed >> 8) / 16777216.0f * 6.2831853f;
			seed = seed * 1664525u + 1013904223u;
			const float r = 0.25f + 0.15f * ((seed >> 8) / 16777216.0f);
			lobes[count][0] = cosf(a) * (0.62f - r);
			lobes[count][1] = SDL_min(sinf(a) * (0.55f - r) - 0.08f, 0.2f);  // fewer below: a flatter base
			lobes[count][2] = r;
		}
		const int ox = (v % 2) * CELL, oy = (v / 2) * CELL;
		for (int y = 0; y < CELL; ++y)
			for (int x = 0; x < CELL; ++x)
			{
				const float px = (x + 0.5f) / CELL * 2 - 1, py = (y + 0.5f) / CELL * 2 - 1;
				// The lobe nearest the viewer here gives the surface.
				float top = -1, n[3] = { 0, 0, 1 }, edge = 0;
				for (int k = 0; k < count; ++k)
				{
					const float dx = px - lobes[k][0], dy = py - lobes[k][1], r = lobes[k][2];
					const float d2 = dx * dx + dy * dy;
					edge = SDL_max(edge, 1.0f - sqrtf(d2) / r);
					if (d2 >= r * r)
						continue;
					const float h = sqrtf(r * r - d2) + 0.3f * (1 - k / (float)count);
					if (h > top)
					{
						top = h;
						const float hz = sqrtf(r * r - d2);
						n[0] = dx / r;
						n[1] = dy / r;
						n[2] = hz / r;
					}
				}
				float alpha = SDL_clamp(edge / 0.6f, 0.0f, 1.0f);
				alpha = alpha * alpha * (3 - 2 * alpha);
				// Wisps: the edges broken up by a little noise.
				const float wisp = cloud_noise((float)x + v * 211.0f, (float)y, 9.0f, 7) * 0.6f +
				                   cloud_noise((float)x + v * 211.0f, (float)y, 4.0f, 8) * 0.4f;
				alpha *= SDL_clamp(0.55f + 0.9f * wisp - (1 - alpha) * 0.4f, 0.0f, 1.0f);
				const float lambert = SDL_max(0.0f, n[0] * light[0] + n[1] * light[1] + n[2] * light[2]);
				const float base = 0.86f + 0.14f * (1 - (py + 1) / 2);  // greyer towards the bottom
				const float shade = SDL_clamp((0.7f + 0.33f * lambert) * base, 0.0f, 1.0f);
				const Uint8 rgba[4] = { (Uint8)(255 * shade), (Uint8)(255 * shade), (Uint8)(255 * SDL_min(1.0f, shade * 1.03f)),
				                        (Uint8)(255 * alpha) };
				memcpy(&pixels[(oy + y) * SIZE + ox + x], rgba, 4);
			}
	}
	BTBHGPUTexture *texture = create_texture_filtered(SIZE, SIZE, BTBH_GPU_TEXTURE_COLOR_SPACE_SRGB, BTBH_GPU_TEXTURE_FILTER_LINEAR);
	btbh_gpu_texture_update_rgba8(texture, (const uint8_t *)pixels, 0, 0, SIZE, SIZE);
	return texture;
}

// A billowing puff: lumps of noise inside a soft round edge, brighter towards the middle (fire is
// hotter inside). White; instances colour it.
static BTBHGPUTexture *create_fire_texture(void)
{
	enum { SIZE = 128 };
	static Uint32 pixels[SIZE * SIZE];
	for (int y = 0; y < SIZE; ++y)
		for (int x = 0; x < SIZE; ++x)
		{
			const float dx = (x + 0.5f) / SIZE * 2 - 1, dy = (y + 0.5f) / SIZE * 2 - 1;
			const float noise = 0.5f * cloud_noise((float)x, (float)y, 22.0f, 31) + 0.3f * cloud_noise((float)x, (float)y, 11.0f, 32) +
			                    0.2f * cloud_noise((float)x, (float)y, 5.0f, 33);
			const float d = sqrtf(dx * dx + dy * dy) * (0.8f + 0.45f * noise);
			const float edge = SDL_clamp(1.0f - d, 0.0f, 1.0f);
			const float a = edge * edge * (3 - 2 * edge) * (0.55f + 0.45f * noise);
			const float v = 0.75f + 0.25f * edge;
			const Uint8 rgba[4] = { (Uint8)(255 * v), (Uint8)(255 * v), (Uint8)(255 * v), (Uint8)(255 * SDL_clamp(a, 0.0f, 1.0f)) };
			memcpy(&pixels[y * SIZE + x], rgba, 4);
		}
	BTBHGPUTexture *texture = create_texture_filtered(SIZE, SIZE, BTBH_GPU_TEXTURE_COLOR_SPACE_LINEAR, BTBH_GPU_TEXTURE_FILTER_LINEAR);
	btbh_gpu_texture_update_rgba8(texture, (const uint8_t *)pixels, 0, 0, SIZE, SIZE);
	return texture;
}

// A soft ring, brightest at 85% of the radius.
static BTBHGPUTexture *create_ring_texture(void)
{
	enum { SIZE = 128 };
	static Uint32 pixels[SIZE * SIZE];
	for (int y = 0; y < SIZE; ++y)
		for (int x = 0; x < SIZE; ++x)
		{
			const float dx = (x + 0.5f) / SIZE * 2 - 1, dy = (y + 0.5f) / SIZE * 2 - 1;
			const float d = sqrtf(dx * dx + dy * dy);
			const float t = (d - 0.85f) / (d < 0.85f ? 0.25f : 0.12f);
			const float a = d > 1.0f ? 0.0f : expf(-t * t * 3.0f);
			const Uint8 rgba[4] = { 255, 255, 255, (Uint8)(255 * a) };
			memcpy(&pixels[y * SIZE + x], rgba, 4);
		}
	BTBHGPUTexture *texture = create_texture_filtered(SIZE, SIZE, BTBH_GPU_TEXTURE_COLOR_SPACE_LINEAR, BTBH_GPU_TEXTURE_FILTER_LINEAR);
	btbh_gpu_texture_update_rgba8(texture, (const uint8_t *)pixels, 0, 0, SIZE, SIZE);
	return texture;
}

static void init_shader_paths(BTBHGPUBackendRequest backend)
{
	tyr3d_resource_dir("TYR3D_SHADER_DIR", TYR3D_SHADER_DIR, "shaders", shader_dir, sizeof(shader_dir));

	const char *ext = backend == BTBH_GPU_BACKEND_METAL ? "metallib" : "spv";
	for (int i = 0; i < SH_COUNT; ++i)
		snprintf(shader_paths[i], sizeof(shader_paths[i]), "%s/%s.%s", shader_dir, shader_names[i], ext);
}

void rgpu_apply_camera_overrides(void)
{
	const char *value;
	if ((value = SDL_getenv("TYR3D_TILT")) != NULL)
		rgpu_camera.tilt_degrees = (float)SDL_atof(value);
	if ((value = SDL_getenv("TYR3D_FOV")) != NULL)
		rgpu_camera.fov_degrees = (float)SDL_atof(value);
	if ((value = SDL_getenv("TYR3D_HEIGHT_SCALE")) != NULL)
		rgpu_camera.height_scale = (float)SDL_atof(value);
	if ((value = SDL_getenv("TYR3D_SUN")) != NULL)
		sscanf(value, "%f,%f,%f", &sun_direction[0], &sun_direction[1], &sun_direction[2]);
	if ((value = SDL_getenv("TYR3D_GLINTS")) != NULL)
		sscanf(value, "%f,%f,%f,%f", &glint_parameters[0], &glint_parameters[1], &glint_parameters[2], &glint_parameters[3]);
	if ((value = SDL_getenv("TYR3D_BLOOM")) != NULL)
		sscanf(value, "%f,%f,%f,%f", &bloom_parameters[0], &bloom_parameters[1], &bloom_parameters[2], &bloom_parameters[3]);
}

SDL_Window *rgpu_init(const char *title, int width, int height)
{
	BTBHGPUBackendRequest backend;
#ifdef __APPLE__
	backend = BTBH_GPU_BACKEND_METAL;
#else
	backend = BTBH_GPU_BACKEND_VULKAN;
#endif
	const char *requested = SDL_getenv("TYR3D_GPU_BACKEND");
	if (requested != NULL)
		backend = SDL_strcasecmp(requested, "vulkan") == 0 ? BTBH_GPU_BACKEND_VULKAN : BTBH_GPU_BACKEND_METAL;

	BTBHGPUDeviceDescriptor device_desc = { 0 };
	device_desc.backend = backend;
	device_desc.required_features = BTBH_GPU_PHASE2_REQUIRED_FEATURES;
	BTBHGPUDeviceReport device_report;
	device = btbh_gpu_device_create(&device_desc, &device_report);
	if (device == NULL)
		die("failed to create GPU device", device_report.message);

	BTBHGPUWindowDescriptor window_desc = { 0 };
	window_desc.title = title;
	window_desc.width = width;
	window_desc.height = height;
	window_desc.hidden = 1;
	window_desc.high_pixel_density = 1;
	BTBHGPUWindowReport window_report;
	window = btbh_gpu_window_create(&window_desc, &window_report);
	if (window == NULL)
		die("failed to create window", window_report.message);
	if (btbh_gpu_window_claim(device, window, &window_report) != BTBH_GPU_OK)
		die("failed to claim window for GPU", window_report.message);

	printf("GPU backend: %s (%s)\n", device_report.capabilities.driver_name,
	       backend == BTBH_GPU_BACKEND_METAL ? "metal" : "vulkan");

	shader_format = btbh_gpu_backend_shader_format(backend);
	init_shader_paths(backend);
	rgpu_apply_camera_overrides();

	screen_texture = create_texture(SCREEN_W, SCREEN_H, BTBH_GPU_TEXTURE_COLOR_SPACE_LINEAR);
	panel_texture = create_texture_filtered(PANEL_HD_W, PANEL_HD_H, BTBH_GPU_TEXTURE_COLOR_SPACE_LINEAR,
	                                        BTBH_GPU_TEXTURE_FILTER_LINEAR);
	spot_texture = create_texture_filtered(SPOT_W, SPOT_H, BTBH_GPU_TEXTURE_COLOR_SPACE_LINEAR, BTBH_GPU_TEXTURE_FILTER_LINEAR);
	showcase_texture = create_texture(SCREEN_W, SCREEN_H, BTBH_GPU_TEXTURE_COLOR_SPACE_SRGB);
	hud_text_texture = create_texture_filtered(HUD_TEXT_W * 4, HUD_TEXT_H * 4, BTBH_GPU_TEXTURE_COLOR_SPACE_LINEAR,
	                                           BTBH_GPU_TEXTURE_FILTER_LINEAR);
	layer_atlas = create_texture_filtered(L3D_WIDTH, ATLAS_H, BTBH_GPU_TEXTURE_COLOR_SPACE_SRGB, map_filter());
	layer_water = create_texture(L3D_WIDTH, ATLAS_H, BTBH_GPU_TEXTURE_COLOR_SPACE_LINEAR);
	tile_atlas = create_texture_filtered(B3D_ATLAS_W, B3D_ATLAS_H * TILE_PAGES, BTBH_GPU_TEXTURE_COLOR_SPACE_SRGB, map_filter());
	tile_water = create_texture(B3D_ATLAS_W, B3D_ATLAS_H * TILE_PAGES, BTBH_GPU_TEXTURE_COLOR_SPACE_LINEAR);
	white_texture = create_texture(1, 1, BTBH_GPU_TEXTURE_COLOR_SPACE_SRGB);
	composed_texture = create_texture(COMPOSED_SIZE, COMPOSED_SIZE * L3D_MAX_BACKGROUNDS, BTBH_GPU_TEXTURE_COLOR_SPACE_SRGB);
	composed_water = create_texture(COMPOSED_SIZE, COMPOSED_SIZE * L3D_MAX_BACKGROUNDS, BTBH_GPU_TEXTURE_COLOR_SPACE_LINEAR);
	puff_texture = create_puff_texture();
	cloud_texture = create_texture_filtered(CLOUD_TEXELS, CLOUD_TEXELS * MAX_CLOUD_CANVASES, BTBH_GPU_TEXTURE_COLOR_SPACE_SRGB,
	                                        BTBH_GPU_TEXTURE_FILTER_LINEAR);
	const Uint32 white = 0xffffffff;
	btbh_gpu_texture_update_rgba8(white_texture, (const uint8_t *)&white, 0, 0, 1, 1);
	quad_mesh = create_quad_mesh(1, 1);
	billboard_mesh = create_billboard_mesh();
	particle_texture = create_particle_texture();
	fire_texture = create_fire_texture();
	ring_texture = create_ring_texture();
	fade_meshes[0] = create_quad_mesh(B3D_BEYOND_FADE, 1);
	fade_meshes[1] = create_quad_mesh(1, B3D_BEYOND_FADE);

	SDL_Window *sdl_window = btbh_gpu_window_sdl_window(window);
	SDL_SetWindowResizable(sdl_window, true);
	SDL_SetWindowMinimumSize(sdl_window, SCREEN_W, SCREEN_H);
	return sdl_window;
}

void rgpu_shutdown(void)
{
	memset(loaded_models, 0, sizeof(loaded_models));  // owned by the window
	forget_volume_sheets();
	forget_hd_sheets();
	forget_terrain();

	if (window != NULL)
		btbh_gpu_window_destroy(window);  // releases every resource the window owns
	window = NULL;
	screen_texture = NULL;
	panel_texture = NULL;
	panel_art = NULL;
	layer_atlas = NULL;
	layer_water = NULL;
	tile_water = NULL;
	composed_water = NULL;
	tile_atlas = NULL;
	white_texture = NULL;
	particle_texture = NULL;
	fire_texture = NULL;
	ring_texture = NULL;
	puff_texture = NULL;
	billboard_mesh = NULL;
	composed_texture = NULL;
	cloud_texture = NULL;
	tile_indices_valid = false;
	memset(tile_pages, 0, sizeof(tile_pages));
	quad_mesh = NULL;
	fade_meshes[0] = fade_meshes[1] = NULL;

	if (device != NULL)
		btbh_gpu_device_destroy(device);
	device = NULL;

	free(readback_rgba);
	readback_rgba = NULL;
	readback_capacity = 0;
}

/* --- Helpers ------------------------------------------------------------------------------- */

static bool begin_frame(BTBHGPUWindowReport *report)
{
	BTBHGPUPlatformSnapshot snapshot;
	if (btbh_gpu_window_begin_frame(window, report, &snapshot) != BTBH_GPU_OK)
		return false;
	return report->drawable_width > 0 && report->drawable_height > 0 && !report->minimized;
}

static void convert_screen(const SDL_Surface *screen, Uint32 *dst)
{
	for (int y = 0; y < SCREEN_H; ++y)
	{
		const Uint8 *row = (const Uint8 *)screen->pixels + y * screen->pitch;
		for (int x = 0; x < SCREEN_W; ++x)
			dst[y * SCREEN_W + x] = rgb_palette[row[x]];
	}
}

// A menu or message shown over the 3D view's last frame (rgpu_present_3d_menu), while it presents.
static struct
{
	bool on;
	const Uint8 *backdrop;    // the screen as it was when the frame showed (SCREEN_W x SCREEN_H)
	const int (*shades)[4];   // the boxes the menu darkened: x1, y1, x2, y2 (JE_barShade's)
	int shade_count;
} menu;

// A colour over the whole window (straight alpha), drawn last: a menu's or the store's fade.
static float canvas_fade[4];


// A rectangle of the screen texture (in screen pixels) drawn to a rectangle of the window.
typedef struct
{
	float x, y, w, h;
	float source_x, source_y, source_w, source_h;
	bool panel;  // from the high-resolution HUD panel (its source rectangle in screen pixels)
} CanvasQuad;

static CanvasQuad whole_screen_quad(const SDL_Rect *dst)
{
	return (CanvasQuad){ (float)dst->x, (float)dst->y, (float)dst->w, (float)dst->h, 0, 0, SCREEN_W, SCREEN_H };
}

// texture_w/h: the size of the texture the quad's source rectangle is in.
static void push_quad(BTBHGPUCanvasVertex *v, const CanvasQuad *q, float texture_w, float texture_h)
{
	const float x = q->x, y = q->y, w = q->w, h = q->h;
	const float u0 = q->source_x / texture_w, u1 = (q->source_x + q->source_w) / texture_w;
	const float v0 = q->source_y / texture_h, v1 = (q->source_y + q->source_h) / texture_h;
	const BTBHGPUCanvasVertex corners[4] = {
		{ x,     y,     u0, v0, 1, 1, 1, 1 },
		{ x + w, y,     u1, v0, 1, 1, 1, 1 },
		{ x + w, y + h, u1, v1, 1, 1, 1, 1 },
		{ x,     y + h, u0, v1, 1, 1, 1, 1 },
	};
	v[0] = corners[0];
	v[1] = corners[1];
	v[2] = corners[2];
	v[3] = corners[0];
	v[4] = corners[2];
	v[5] = corners[3];
}

#define MAX_CANVAS_QUADS 4

// Draws parts of the screen texture over the window and presents. Composites a pending 3D scene
// first. A spotlight overlay (spot_texture over the whole window) goes under the screen's parts.
static void present_canvas(const CanvasQuad *quads, int quad_count, bool spotlight, bool clear,
                           const BTBHGPUWindowReport *frame)
{
	static BTBHGPUCanvasVertex vertices[6 * (MAX_CANVAS_QUADS + 3 + MAX_HUD_QUADS)];
	BTBHGPUCanvasBatch batches_2d[MAX_CANVAS_QUADS + 3 + MAX_HUD_QUADS] = { { 0 } };
	int batch_count_2d = 0;
	uint32_t vertex_count = 0;

	if (spotlight)
	{
		const CanvasQuad whole = { 0, 0, (float)frame->logical_width, (float)frame->logical_height, 0, 0, SPOT_W, SPOT_H };
		push_quad(vertices, &whole, SPOT_W, SPOT_H);
		BTBHGPUCanvasBatch *b = &batches_2d[batch_count_2d++];
		b->first_vertex = vertex_count;
		b->vertex_count = 6;
		b->texture = spot_texture;
		b->blend_mode = BTBH_GPU_CANVAS_BLEND_ALPHA;
		vertex_count += 6;
	}

	quad_count = SDL_min(quad_count, MAX_CANVAS_QUADS);
	for (int i = 0; i < quad_count; ++i)
	{
		BTBHGPUCanvasBatch *batch = &batches_2d[batch_count_2d++];
		batch->first_vertex = vertex_count;
		batch->vertex_count = 6;
		batch->blend_mode = BTBH_GPU_CANVAS_BLEND_ALPHA;
		if (quads[i].panel)
		{
			// The upscaled picture of the panel under it (its size whatever the upscale's).
			if (panel_art != NULL)
			{
				const CanvasQuad art = { quads[i].x, quads[i].y, quads[i].w, quads[i].h, 0, 0, 1, 1 };
				push_quad(vertices + vertex_count, &art, 1, 1);
				batch->texture = panel_art;
				vertex_count += 6;
				batch = &batches_2d[batch_count_2d++];
				batch->first_vertex = vertex_count;
				batch->vertex_count = 6;
				batch->blend_mode = BTBH_GPU_CANVAS_BLEND_ALPHA;
			}
			// The panel texture holds the screen from the panel's column on, scaled up.
			CanvasQuad q = quads[i];
			q.source_x = (q.source_x - L3D_PLAYFIELD_W) * PANEL_HD_SCALE;
			q.source_y *= PANEL_HD_SCALE;
			q.source_w *= PANEL_HD_SCALE;
			q.source_h *= PANEL_HD_SCALE;
			push_quad(vertices + vertex_count, &q, PANEL_HD_W, PANEL_HD_H);
			batch->texture = panel_texture;
		}
		else
		{
			push_quad(vertices + vertex_count, &quads[i], SCREEN_W, SCREEN_H);
			batch->texture = screen_texture;
		}
		vertex_count += 6;
	}

	// The modern HUD, in batches of quads with the same texture.
	for (int i = 0; i < hud_quad_count; ++i)
	{
		const HudQuad *q = &hud_quads[i];
		const BTBHGPUCanvasVertex corners[4] = {
			{ q->x,        q->y,        q->u0, q->v0, q->left[0], q->left[1], q->left[2], q->left[3] },
			{ q->x + q->w, q->y,        q->u1, q->v0, q->right[0], q->right[1], q->right[2], q->right[3] },
			{ q->x + q->w, q->y + q->h, q->u1, q->v1, q->right[0], q->right[1], q->right[2], q->right[3] },
			{ q->x,        q->y + q->h, q->u0, q->v1, q->left[0], q->left[1], q->left[2], q->left[3] },
		};
		BTBHGPUCanvasVertex *v = vertices + vertex_count;
		v[0] = corners[0];
		v[1] = corners[1];
		v[2] = corners[2];
		v[3] = corners[0];
		v[4] = corners[2];
		v[5] = corners[3];
		BTBHGPUTexture *texture = q->text ? hud_text_texture : NULL;
		if (i > 0 && hud_quads[i - 1].text == q->text)
			batches_2d[batch_count_2d - 1].vertex_count += 6;
		else
		{
			BTBHGPUCanvasBatch *b = &batches_2d[batch_count_2d++];
			b->first_vertex = vertex_count;
			b->vertex_count = 6;
			b->texture = texture;
			b->blend_mode = BTBH_GPU_CANVAS_BLEND_ALPHA;
		}
		vertex_count += 6;
	}

	// A fade (the palette's) over everything.
	if (canvas_fade[3] > 0)
	{
		const CanvasQuad whole = { 0, 0, (float)frame->logical_width, (float)frame->logical_height, 0, 0, 1, 1 };
		push_quad(vertices + vertex_count, &whole, 1, 1);
		for (int i = 0; i < 6; ++i)
		{
			BTBHGPUCanvasVertex *v = &vertices[vertex_count + i];
			v->red = canvas_fade[0];
			v->green = canvas_fade[1];
			v->blue = canvas_fade[2];
			v->alpha = canvas_fade[3];
		}
		BTBHGPUCanvasBatch *b = &batches_2d[batch_count_2d++];
		b->first_vertex = vertex_count;
		b->vertex_count = 6;
		b->texture = NULL;
		b->blend_mode = BTBH_GPU_CANVAS_BLEND_ALPHA;
		vertex_count += 6;
	}

	BTBHGPUCanvasPass pass = { 0 };
	pass.first_batch = 0;
	pass.batch_count = (uint32_t)batch_count_2d;
	pass.target = NULL;
	pass.clear_enabled = clear;
	pass.clear_alpha = 255;

	// Frames shown between ticks don't count as the game's frames (dumps, TYR3D_EXIT_AFTER).
	static int dump_ahead = -1;  // TYR3D_DUMP_AHEAD=1: they do, to check them
	if (dump_ahead < 0)
		dump_ahead = SDL_getenv("TYR3D_DUMP_AHEAD") != NULL;
	const bool tick_frame = ahead == 0 || dump_ahead;
	const bool capture = tick_frame && dev_capture_next_frame();
	if (capture)
		btbh_gpu_window_request_presented_frame_readback(window);

	hud_quad_count = 0;  // made again for each 3D frame

	BTBHGPUCanvasReport report;
	if (btbh_gpu_window_canvas_present(window,
	        shader_paths[SH_CANVAS_VERT], shader_paths[SH_CANVAS_FRAG], shader_paths[SH_CANVAS_TEXTURED_FRAG],
	        shader_format, vertices, vertex_count, batches_2d, (uint32_t)batch_count_2d, &pass, 1, &report) != BTBH_GPU_OK)
	{
		fprintf(stderr, "warning: canvas present failed: %s\n", report.message);
	}

	if (capture)
	{
		const size_t needed = (size_t)frame->drawable_width * frame->drawable_height * 4;
		if (needed > readback_capacity)
		{
			free(readback_rgba);
			readback_rgba = malloc(needed);
			readback_capacity = readback_rgba != NULL ? needed : 0;
		}
		BTBHGPUCanvasReport readback_report;
		if (readback_rgba != NULL &&
		    btbh_gpu_window_readback_presented_frame(window, readback_rgba, (uint32_t)readback_capacity, &readback_report) == BTBH_GPU_OK)
		{
			dev_on_frame_presented(readback_rgba, readback_report.drawable_width, readback_report.drawable_height,
			                       readback_report.drawable_width * 4);
			return;
		}
	}
	if (tick_frame)
		dev_on_frame_presented(NULL, 0, 0, 0);
}

/* --- 2D ------------------------------------------------------------------------------------ */

void rgpu_present_2d(const SDL_Surface *screen, const SDL_Rect *dst)
{
	BTBHGPUWindowReport frame;
	if (!begin_frame(&frame))
		return;

	convert_screen(screen, screen_rgba);
	btbh_gpu_texture_update_rgba8(screen_texture, (const uint8_t *)screen_rgba, 0, 0, SCREEN_W, SCREEN_H);

	const CanvasQuad quad = whole_screen_quad(dst);
	present_canvas(&quad, 1, false, true, &frame);
}

/* --- 3D ------------------------------------------------------------------------------------ */

typedef struct { float m[16]; } Mat4;  // column-major

static Mat4 mat4_identity(void)
{
	Mat4 r = { { 0 } };
	r.m[0] = r.m[5] = r.m[10] = r.m[15] = 1;
	return r;
}

static Mat4 mat4_translation(float x, float y, float z)
{
	Mat4 r = mat4_identity();
	r.m[12] = x;
	r.m[13] = y;
	r.m[14] = z;
	return r;
}

static Mat4 mat4_scaling(float s)
{
	Mat4 r = mat4_identity();
	r.m[0] = r.m[5] = r.m[10] = s;
	return r;
}

// Right-handed rotations about the X, Y and Z axes (degrees).
static Mat4 mat4_rotation(int axis, float degrees)
{
	const float a = degrees * (float)M_PI / 180.0f, c = cosf(a), s = sinf(a);
	Mat4 r = mat4_identity();
	const int i = (axis + 1) % 3, j = (axis + 2) % 3;
	r.m[i * 4 + i] = c;
	r.m[i * 4 + j] = s;
	r.m[j * 4 + i] = -s;
	r.m[j * 4 + j] = c;
	return r;
}

static Mat4 mat4_mul(const Mat4 *a, const Mat4 *b);

static Mat4 mat4_chain(int count, const Mat4 *matrices)
{
	Mat4 r = matrices[0];
	for (int i = 1; i < count; ++i)
		r = mat4_mul(&r, &matrices[i]);
	return r;
}

static Mat4 mat4_mul(const Mat4 *a, const Mat4 *b)
{
	Mat4 r;
	for (int c = 0; c < 4; ++c)
		for (int row = 0; row < 4; ++row)
		{
			float sum = 0;
			for (int k = 0; k < 4; ++k)
				sum += a->m[k * 4 + row] * b->m[c * 4 + k];
			r.m[c * 4 + row] = sum;
		}
	return r;
}

typedef struct
{
	Mat4 view_projection;
	float position[3];
	float right[3];
	float up[3];
	float forward[3];
	// A window position in NDC maps to the view ray with slopes (along right and up)
	// (ndc - ndc_offset) / ndc_scale * tan_half.
	float ndc_scale[2], ndc_offset[2];
	float tan_half[2];
} Camera3D;

/*
 * World space: X = game x, Y = height above the ground, Z = game y (towards the bottom of the
 * screen). The camera looks towards -Z and down by the tilt angle.
 *
 * The camera is fitted so that the playfield's bottom edge, at the player's height, spans the
 * playfield viewport exactly; the perspective then reveals extra world towards the top.
 * The projection is shifted so that the fitted view lands on the playfield's rectangle within
 * the window, letting the scene continue under the HUD and into any letterbox area.
 */
// upside_down mirrors the view vertically within the playfield's rectangle, as the game flips the
// playfield on upside-down levels.
static Camera3D fit_camera(float reference_height, float viewport_aspect, const float ndc_rect[4], bool upside_down)
{
	const float theta = rgpu_camera.tilt_degrees * (float)M_PI / 180.0f;
	const float t = tanf(rgpu_camera.fov_degrees * (float)M_PI / 360.0f);
	const float c = cosf(theta), s = sinf(theta);

	const float forward[3] = { 0, -c, -s };
	const float up[3] = { 0, s, -c };
	const float right[3] = { 1, 0, 0 };

	// Camera-space depth and height of the bottom edge's centre.
	const float half_width = L3D_PLAYFIELD_W / 2.0f;
	const float depth = half_width / (t * viewport_aspect);
	const float height = -t * depth;

	const float bottom[3] = { L3D_PLAYFIELD_X + half_width, reference_height, L3D_PLAYFIELD_H };
	Camera3D camera;
	for (int i = 0; i < 3; ++i)
		camera.position[i] = bottom[i] - (height * up[i] + depth * forward[i]);
	memcpy(camera.right, right, sizeof(right));
	memcpy(camera.up, up, sizeof(up));

	Mat4 view = { { 0 } };
	for (int i = 0; i < 3; ++i)
	{
		view.m[i * 4 + 0] = right[i];
		view.m[i * 4 + 1] = up[i];
		view.m[i * 4 + 2] = forward[i];
	}
	float dot_r = 0, dot_u = 0, dot_f = 0;
	for (int i = 0; i < 3; ++i)
	{
		dot_r += right[i] * camera.position[i];
		dot_u += up[i] * camera.position[i];
		dot_f += forward[i] * camera.position[i];
	}
	view.m[12] = -dot_r;
	view.m[13] = -dot_u;
	view.m[14] = -dot_f;
	view.m[15] = 1;

	const float near_plane = 1.0f, far_plane = 10000.0f;
	Mat4 projection = { { 0 } };
	projection.m[0] = 1.0f / (t * viewport_aspect);
	projection.m[5] = 1.0f / t;
	projection.m[10] = far_plane / (far_plane - near_plane);
	projection.m[11] = 1.0f;
	projection.m[14] = -near_plane * far_plane / (far_plane - near_plane);

	// Map NDC [-1, 1] onto the playfield's rectangle within the window:
	// x' = sx * x + ox * w (the clip-space w is multiplied by column 3).
	const float sx = (ndc_rect[2] - ndc_rect[0]) / 2, ox = (ndc_rect[0] + ndc_rect[2]) / 2;
	const float sy = (ndc_rect[3] - ndc_rect[1]) / 2, oy = (ndc_rect[1] + ndc_rect[3]) / 2;
	Mat4 post = { { 0 } };
	post.m[0] = sx;
	post.m[5] = upside_down ? -sy : sy;
	post.m[10] = 1;
	post.m[12] = ox;
	post.m[13] = oy;
	post.m[15] = 1;

	Mat4 projected = mat4_mul(&projection, &view);
	camera.view_projection = mat4_mul(&post, &projected);

	memcpy(camera.forward, forward, sizeof(forward));
	camera.ndc_scale[0] = sx;
	camera.ndc_scale[1] = sy;
	camera.ndc_offset[0] = ox;
	camera.ndc_offset[1] = oy;
	camera.tan_half[0] = t * viewport_aspect;
	camera.tan_half[1] = t;
	return camera;
}

// How far up the level the background maps are drawn (game pixels above the screen's top edge),
// and the distance over which they fade out before that.
#define BACKGROUND_AHEAD 640.0f
#define BACKGROUND_FADE 160.0f

// The view last shown, for mapping the mouse pointer onto the player's plane.
typedef struct
{
	bool valid;
	Camera3D camera;
	float reference;           // the player's plane's height
	float window_w, window_h;  // window points
	bool upside_down;
} ShownView;

static ShownView shown_view;

/*
 * Layer alignment. The game draws every layer in the same screen coordinates, but in the view the
 * layers are planes at different heights, and with perspective the same position would be seen
 * at different places on different layers: a turret's shots and its explosion away from the
 * turret, a ground enemy's shadow off its sprite. So each plane is scaled about the point below
 * the camera by its distance from the camera relative to the player's plane: a position on any
 * layer is seen where the same position on the player's plane is, as in the game. Objects scale
 * with the plane they stand on, so they keep their sprites' size; depth still decides what is in
 * front, and light and shadows are 3D. TYR3D_LAYER_PARALLAX=1 shows the planes unscaled.
 */
static struct
{
	bool on;
	float cx, cy, cz;  // the camera's position
	float reference;   // the player's plane's height
} align;

static void set_alignment(const Camera3D *camera, float reference_height)
{
	static int parallax = -1;
	if (parallax < 0)
		parallax = SDL_getenv("TYR3D_LAYER_PARALLAX") != NULL && SDL_atoi(SDL_getenv("TYR3D_LAYER_PARALLAX")) != 0;
	align.on = !parallax;
	align.cx = camera->position[0];
	align.cy = camera->position[1];
	align.cz = camera->position[2];
	align.reference = reference_height;
}

// How much larger the plane at the given height is drawn.
static float align_scale(float height)
{
	return align.on ? (align.cy - height) / (align.cy - align.reference) : 1.0f;
}

// The transform of something standing on the plane at its translation's height, aligned.
static Mat4 aligned(const Mat4 *transform)
{
	const float height = transform->m[13];
	const float k = align_scale(height);
	if (k == 1.0f)
		return *transform;
	Mat4 a = mat4_identity();
	a.m[0] = a.m[5] = a.m[10] = k;
	a.m[12] = align.cx * (1 - k);
	a.m[13] = height * (1 - k);
	a.m[14] = align.cz * (1 - k);
	return mat4_mul(&a, transform);
}

// The part of the horizontal plane at the given height that the window shows, in world
// coordinates, as far as the given z.
static void plane_footprint_world(const Camera3D *camera, float height, float far_z, float rect[4])
{
	rect[0] = rect[1] = INFINITY;
	rect[2] = rect[3] = -INFINITY;
	for (int corner = 0; corner < 4; ++corner)
	{
		const float ndc[2] = { (corner & 1) ? 1.0f : -1.0f, (corner & 2) ? 1.0f : -1.0f };
		float slope[2], ray[3];
		for (int i = 0; i < 2; ++i)
			slope[i] = (ndc[i] - camera->ndc_offset[i]) / camera->ndc_scale[i] * camera->tan_half[i];
		for (int i = 0; i < 3; ++i)
			ray[i] = camera->forward[i] + camera->right[i] * slope[0] + camera->up[i] * slope[1];

		// Where the ray meets the plane; rays that miss it reach the furthest drawn row.
		float s;
		if (ray[1] < -1e-6f)
			s = (height - camera->position[1]) / ray[1];
		else if (ray[2] < -1e-6f)
			s = (far_z - camera->position[2]) / ray[2];
		else
			continue;
		const float x = camera->position[0] + ray[0] * s;
		const float z = SDL_max(camera->position[2] + ray[2] * s, far_z);
		rect[0] = SDL_min(rect[0], x);
		rect[1] = SDL_min(rect[1], z);
		rect[2] = SDL_max(rect[2], x);
		rect[3] = SDL_max(rect[3], z);
	}
}

// The part of the horizontal plane at the given height that the window shows (the playfield
// and everything around it), as a rectangle {x0, z0, x1, z1} in game screen coordinates.
static void plane_footprint(const Camera3D *camera, float height, float rect[4])
{
	const float k = align_scale(height);
	plane_footprint_world(camera, height, align.cz + (-BACKGROUND_AHEAD - align.cz) * k, rect);
	if (k == 1.0f || rect[0] > rect[2])
		return;
	rect[0] = align.cx + (rect[0] - align.cx) / k;
	rect[2] = align.cx + (rect[2] - align.cx) / k;
	rect[1] = align.cz + (rect[1] - align.cz) / k;
	rect[3] = align.cz + (rect[3] - align.cz) / k;
}

// Palette colours for this frame, with JE_filterScreen applied as a palette-index remap.
static void frame_colors(const L3DFrame *frame, Uint32 colors[256])
{
	Uint8 remap[256];
	for (int i = 0; i < 256; ++i)
	{
		int index = i;
		if (frame->filter_hue != -99)
			index = (frame->filter_hue << 4) | (index & 0x0f);
		if (frame->filter_brightness != -99)
		{
			const int value = (index & 0x0f) + frame->filter_brightness;
			index = (index & 0xf0) | (value < 0 || value >= 0x1f ? 0 : (value >= 0x0f ? 0x0f : value));
		}
		remap[i] = (Uint8)index;
	}

	for (int i = 0; i < 256; ++i)
		colors[i] = rgb_palette[remap[i]];
}

// Converts the layers to colour, one atlas slot each. Layers drawn over background map tiles
// (native) keep only the playfield, where the game drew them; the tiles show everything else.
static bool cloud_background(const L3DBackground *background, bool composed);
static bool water_overlay(const L3DBackground *background);
static bool relief_frame(const L3DFrame *frame, const bool *composed);
static bool terrain_background(const L3DFrame *frame, const L3DBackground *background);
static float solid_top(int set);
static const B3DTerrain *frame_terrains[B3D_SETS + 1];
static float terrain_lift(float x, float y);

static void build_layer_atlas(const L3DFrame *frame, const Uint32 colors[256], const bool *native,
                              const bool *composed_layer, int *slot_of_layer, int *slot_count)
{
	// The world ends at the edges of the layers; fade towards the black clear colour there so the
	// tilted camera doesn't show a hard border.
	static Uint8 edge_fade[L3D_ROWS][L3D_WIDTH];
	static bool edge_fade_ready = false;
	if (!edge_fade_ready)
	{
		const int fade = 20;
		for (int y = 0; y < L3D_ROWS; ++y)
			for (int x = 0; x < L3D_WIDTH; ++x)
			{
				const int edge = SDL_min(SDL_min(x, L3D_WIDTH - 1 - x), y);
				const float f = edge >= fade ? 1.0f : (float)edge / fade;
				edge_fade[y][x] = (Uint8)(255.0f * f * f * (3 - 2 * f));
			}
		edge_fade_ready = true;
	}

	// In space (the game's starfield is on) colour 0 of the stars' layer is empty space, where the
	// game draws its stars: it lets the deep starfield through (add_deep_star_batch).
	const bool space = frame->star_count > 0 && settings3d.effects && frame->filter_hue == -99 &&
	                   frame->filter_brightness == -99;

	int slots = 0;
	for (int l = 0; l < frame->layer_count; ++l)
	{
		const L3DLayer *layer = &frame->layers[l];
		if (layer->type == L3D_OVERLAY)
		{
			slot_of_layer[l] = -1;
			continue;
		}
		const bool empty_zero = space && l == frame->star_layer;
		slot_of_layer[l] = slots;
		Uint32 *dst = atlas_rgba + slots * ATLAS_SLOT_H * L3D_WIDTH;
		if (native[l])
		{
			// A filtered (composed) background outside the playfield only approximates the game's
			// filters, so the playfield's edge fades into it, dithered, rather than showing a seam.
			static const Uint8 bayer[4][4] = { { 0, 8, 2, 10 }, { 12, 4, 14, 6 }, { 3, 11, 1, 9 }, { 15, 7, 13, 5 } };
			const int feather = composed_layer[l] ? 10 : 0;
			memset(dst, 0, L3D_WIDTH * L3D_ROWS * sizeof(Uint32));
			// Pixels of cloud tiles: the clouds are puffs (add_cloud_batches).
			static Uint8 cloud_mask[L3D_WIDTH * L3D_ROWS];
			bool clouds = false;
			{
				bool composed[L3D_MAX_BACKGROUNDS];
				b3d_composed_backgrounds(frame, composed);
				const bool relief = relief_frame(frame, composed);
				for (int i = 0; i < frame->background_count; ++i)
					if (frame->backgrounds[i].layer == l &&
					    (water_overlay(&frame->backgrounds[i]) || (relief && frame->backgrounds[i].set == 1) ||
					     terrain_background(frame, &frame->backgrounds[i]) ||
					     (b3d_terrain_ground && frame->backgrounds[i].blend &&
					      !cloud_background(&frame->backgrounds[i], composed[i]))))
					{
						memset(cloud_mask, 1, sizeof(cloud_mask));  // none of it is drawn
						clouds = true;
					}
					else if (frame->backgrounds[i].layer == l && cloud_background(&frame->backgrounds[i], composed[i]))
					{
						if (!clouds)
							memset(cloud_mask, 0, sizeof(cloud_mask));
						clouds = true;
						b3d_cloud_mask(&frame->backgrounds[i], cloud_mask);
					}
			}
			for (int y = L3D_OVERSCAN; y < L3D_OVERSCAN + L3D_PLAYFIELD_H; ++y)
				for (int x = L3D_PLAYFIELD_X; x < L3D_PLAYFIELD_X + L3D_PLAYFIELD_W; ++x)
				{
					const int i = y * L3D_WIDTH + x;
					if (!layer->cover[i] || (empty_zero && layer->index[i] == 0) || (clouds && cloud_mask[i]))
						continue;
					if (feather > 0)
					{
						const int edge = SDL_min(SDL_min(x - L3D_PLAYFIELD_X, L3D_PLAYFIELD_X + L3D_PLAYFIELD_W - 1 - x),
						                         y - L3D_OVERSCAN);
						if (edge < feather && bayer[y & 3][x & 3] * feather >= edge * 16)
							continue;
					}
					dst[i] = colors[layer->index[i]];
				}
			// Water: the pixels of the layer's backgrounds' water tiles (b3d_water_mask).
			static Uint8 water_tiles[L3D_WIDTH * L3D_ROWS];
			memset(water_tiles, 0, sizeof(water_tiles));
			for (int i = 0; i < frame->background_count; ++i)
				if (frame->backgrounds[i].layer == l)
					b3d_water_mask(&frame->backgrounds[i], water_tiles);
			Uint32 *water = layer_water_rgba + (slots) * ATLAS_SLOT_H * L3D_WIDTH;
			static const Uint8 water_on[4] = { 0, 0, 255, 255 };
			Uint32 water_value;
			memcpy(&water_value, water_on, 4);
			for (int i = 0; i < L3D_WIDTH * L3D_ROWS; ++i)
				water[i] = dst[i] != 0 && water_tiles[i] ? water_value : 0;
			++slots;
			continue;
		}
		const Uint8 *fade = &edge_fade[0][0];
		for (int i = 0; i < L3D_WIDTH * L3D_ROWS; ++i)
		{
			if (!layer->cover[i] || (empty_zero && layer->index[i] == 0))
			{
				dst[i] = 0;
				continue;
			}
			Uint32 color = colors[layer->index[i]];
			if (fade[i] != 255)
			{
				Uint8 *c = (Uint8 *)&color;
				c[0] = (Uint8)(c[0] * fade[i] / 255);
				c[1] = (Uint8)(c[1] * fade[i] / 255);
				c[2] = (Uint8)(c[2] * fade[i] / 255);
			}
			dst[i] = color;
		}
		Uint32 *water = layer_water_rgba + slots * ATLAS_SLOT_H * L3D_WIDTH;
		for (int i = 0; i < L3D_WIDTH * L3D_ROWS; ++i)
			water[i] = background_layer(layer->type) && layer->cover[i] ? water_mask(colors[layer->index[i]]) : 0;
		++slots;
	}
	*slot_count = slots;
}

// HUD with a transparent playfield, plus the overlay layers drawn into the playfield.
/*
 * The 3D view's layout of the window: the HUD panel (the original screen's right column) at the
 * window's right edge, as tall as the window, and the playfield as large as fits in the rest,
 * centred in it; the bar below the playfield is left out (its messages are shown in the
 * playfield, see build_hud). The scene fills the window around and under all of it.
 */
#define PANEL_X L3D_PLAYFIELD_W  // the panel's column of the screen

typedef struct
{
	bool split;        // panel and playfield placed separately (else the whole screen at dst)
	float playfield[4];  // x, y, w, h in logical window pixels
	float panel[4];
} Layout3D;

// The modern HUD: a few gauges over the scene instead of the panel (not for two players, whose
// panel holds both).
static bool modern_hud(void)
{
	return settings3d.hud_modern && !twoPlayerMode;
}

static Layout3D layout_3d(float window_w, float window_h, const SDL_Rect *dst)
{
	Layout3D layout = { .split = true };
	if (modern_hud())
	{
		// The playfield as large as the window holds it, centred; no panel.
		const float scale = SDL_min(window_h / L3D_PLAYFIELD_H, window_w / L3D_PLAYFIELD_W);
		layout.playfield[2] = L3D_PLAYFIELD_W * scale;
		layout.playfield[3] = L3D_PLAYFIELD_H * scale;
		layout.playfield[0] = (window_w - layout.playfield[2]) / 2;
		layout.playfield[1] = (window_h - layout.playfield[3]) / 2;
		return layout;
	}
	if (!layout.split)
	{
		layout.playfield[0] = dst->x;
		layout.playfield[1] = dst->y;
		layout.playfield[2] = dst->w * (float)L3D_PLAYFIELD_W / SCREEN_W;
		layout.playfield[3] = dst->h * (float)L3D_PLAYFIELD_H / SCREEN_H;
		return layout;
	}

	const float panel_w = (SCREEN_W - PANEL_X) * window_h / SCREEN_H;
	layout.panel[0] = window_w - panel_w;
	layout.panel[1] = 0;
	layout.panel[2] = panel_w;
	layout.panel[3] = window_h;

	const float room = window_w - panel_w;
	const float scale = SDL_min(window_h / L3D_PLAYFIELD_H, room / L3D_PLAYFIELD_W);
	layout.playfield[2] = L3D_PLAYFIELD_W * scale;
	layout.playfield[3] = L3D_PLAYFIELD_H * scale;
	layout.playfield[0] = (room - layout.playfield[2]) / 2;
	layout.playfield[1] = (window_h - layout.playfield[3]) / 2;
	return layout;
}

static int layout_quads(const Layout3D *layout, const SDL_Rect *dst, CanvasQuad quads[MAX_CANVAS_QUADS])
{
	if (!layout->split)
	{
		quads[0] = whole_screen_quad(dst);
		return 1;
	}
	const float *p = layout->panel, *f = layout->playfield;
	if (p[2] <= 0)
	{
		quads[0] = (CanvasQuad){ f[0], f[1], f[2], f[3], 0, 0, L3D_PLAYFIELD_W, L3D_PLAYFIELD_H };
		return 1;
	}
	quads[0] = (CanvasQuad){ p[0], p[1], p[2], p[3], PANEL_X, 0, SCREEN_W - PANEL_X, SCREEN_H, .panel = true };
	quads[1] = (CanvasQuad){ f[0], f[1], f[2], f[3], 0, 0, L3D_PLAYFIELD_W, L3D_PLAYFIELD_H };
	return 2;
}

// In-game messages (JE_drawTextWindow) are written over the bar below the playfield, which the
// split layout leaves out. While one shows, it is drawn again, as the game draws it, near the
// bottom of the playfield, with a shadow.
#define MESSAGE_Y 189
#define MESSAGE_H 10
#define MESSAGE_AT (modern_hud() ? L3D_PLAYFIELD_H - 34 : L3D_PLAYFIELD_H - 22)  // above the modern HUD's gauges

static void add_message(void)
{
	if (textErase == 0 || text_window_message[0] == '\0')
		return;

	static SDL_Surface *text = NULL;
	if (text == NULL && (text = SDL_CreateSurface(SCREEN_W, SCREEN_H, SDL_PIXELFORMAT_INDEX8)) == NULL)
		return;
	SDL_FillSurfaceRect(text, NULL, 0xff);  // the text's colours are greys, 0x00-0x0f
	JE_outText(text, 20, MESSAGE_Y + 1, text_window_message, 0, 4);

	const Uint32 shadow = pack_rgba(0, 0, 0);
	for (int pass = 0; pass < 2; ++pass)
		for (int y = 0; y < MESSAGE_H; ++y)
			for (int x = 0; x < L3D_PLAYFIELD_W - 1; ++x)
			{
				const Uint8 index = ((const Uint8 *)text->pixels)[(MESSAGE_Y + y) * text->pitch + x];
				if (index == 0xff)
					continue;
				if (pass == 0)
					screen_rgba[(MESSAGE_AT + y + 1) * SCREEN_W + x + 1] = shadow;
				else
					screen_rgba[(MESSAGE_AT + y) * SCREEN_W + x] = rgb_palette[index];
			}
}

#define MENU_SHADE 0.45f  // what's left of the scene's light under each box it darkens

// What the menu changed of the playfield: drawn over the scene; what it darkened darkens it.
static void add_menu(const SDL_Surface *screen)
{
	static Uint8 level[L3D_PLAYFIELD_W * L3D_PLAYFIELD_H];
	memset(level, 0, sizeof(level));
	for (int i = 0; i < menu.shade_count; ++i)
	{
		const int *r = menu.shades[i];
		for (int y = SDL_max(r[1], 0); y <= SDL_min(r[3], L3D_PLAYFIELD_H - 1); ++y)
			for (int x = SDL_max(r[0], 0); x <= SDL_min(r[2], L3D_PLAYFIELD_W - 1); ++x)
				++level[y * L3D_PLAYFIELD_W + x];
	}
	Uint32 shade[8];
	for (int k = 0; k < 8; ++k)
	{
		const Uint8 rgba[4] = { 0, 0, 0, (Uint8)(255 * (1 - powf(MENU_SHADE, (float)k))) };
		memcpy(&shade[k], rgba, sizeof(rgba));
	}
	for (int y = 0; y < L3D_PLAYFIELD_H; ++y)
		for (int x = 0; x < L3D_PLAYFIELD_W; ++x)
		{
			const Uint8 now = ((const Uint8 *)screen->pixels)[y * screen->pitch + x];
			const int k = SDL_min(level[y * L3D_PLAYFIELD_W + x], 7);
			Uint8 expected = menu.backdrop[y * SCREEN_W + x];
			for (int i = 0; i < k; ++i)
				expected = ((expected & 0x0f) >> 1) | (expected & 0xf0);
			Uint32 *out = &screen_rgba[y * SCREEN_W + x];
			if (now != expected)
				*out = rgb_palette[now];
			else if (k > 0)
				*out = shade[k];
		}
}

static void build_hud(const SDL_Surface *hud, const L3DFrame *frame, bool split)
{
	convert_screen(hud, screen_rgba);
	for (int y = 0; y < L3D_PLAYFIELD_H; ++y)
		memset(screen_rgba + y * SCREEN_W, 0, L3D_PLAYFIELD_W * sizeof(Uint32));
	if (split)
		add_message();

	for (int l = 0; l < frame->layer_count; ++l)
	{
		const L3DLayer *layer = &frame->layers[l];
		if (layer->type != L3D_OVERLAY)
			continue;
		for (int y = 0; y < L3D_PLAYFIELD_H; ++y)
		{
			const int row = y + L3D_OVERSCAN;
			if (row < layer->min_y || row >= layer->max_y)
				continue;
			for (int x = 0; x < L3D_PLAYFIELD_W; ++x)
			{
				const int i = row * L3D_WIDTH + x + L3D_PLAYFIELD_X;
				if (layer->cover[i])
					screen_rgba[y * SCREEN_W + x] = rgb_palette[layer->index[i]];
			}
		}
	}
	if (menu.on)
		add_menu(hud);
}

/*
 * The HUD panel at four times the screen's resolution: the game's own drawing of it, magnified
 * with Scale2x twice (each pixel becomes four, rounding diagonal edges and keeping straight ones
 * and the colours as they are), and shown smoothly scaled. Made again only when the panel changes.
 */
static void scale2x(const Uint32 *src, int w, int h, Uint32 *dst)
{
	for (int y = 0; y < h; ++y)
		for (int x = 0; x < w; ++x)
		{
			const Uint32 p = src[y * w + x];
			const Uint32 a = y > 0 ? src[(y - 1) * w + x] : p;      // above
			const Uint32 b = x < w - 1 ? src[y * w + x + 1] : p;    // right
			const Uint32 c = x > 0 ? src[y * w + x - 1] : p;        // left
			const Uint32 d = y < h - 1 ? src[(y + 1) * w + x] : p;  // below
			Uint32 *out = dst + (2 * y) * (2 * w) + 2 * x;
			out[0] = c == a && c != d && a != b ? a : p;
			out[1] = a == b && a != c && b != d ? b : p;
			out[2 * w] = d == c && d != b && c != a ? c : p;
			out[2 * w + 1] = b == d && b != a && d != c ? d : p;
		}
}

/*
 * With an upscaled picture of the panel (upscale/out/hud_1p.png or hud_2p.png, see
 * tools/make_atlases.py), the panel's unchanging parts come from it: the magnified panel keeps only
 * what differs from the game's own picture of it (gauges, icons, text) and goes over it.
 */
static int panel_art_picture = 0;          // which picture it shows (3 or 6), 0 if none
static Uint8 panel_picture[SCREEN_W * SCREEN_H];

static void load_panel_art(int picture)
{
	if (panel_art_picture == picture)
		return;
	panel_art_picture = picture;
	panel_art = NULL;  // a texture made before stays with the window

	char dir[1024], path[1200];
	snprintf(path, sizeof(path), "%s/%s.png",
	         tyr3d_resource_dir("TYR3D_UPSCALE_DIR", TYR3D_UPSCALE_DIR, "upscale", dir, sizeof(dir)),
	         picture == 6 ? "hud_2p" : "hud_1p");
	if (!SDL_GetPathInfo(path, NULL))
		return;
	BTBHGPUTextureReport report;
	panel_art = btbh_gpu_window_texture_load_ex(window, path, 1, BTBH_GPU_TEXTURE_FILTER_LINEAR,
	                                            BTBH_GPU_TEXTURE_WRAP_CLAMP, BTBH_GPU_TEXTURE_COLOR_SPACE_LINEAR, &report);
	if (panel_art == NULL)
		return;
	SDL_Surface *surface = SDL_CreateSurface(SCREEN_W, SCREEN_H, SDL_PIXELFORMAT_INDEX8);
	if (surface == NULL)
	{
		panel_art = NULL;
		return;
	}
	JE_loadPic(surface, (JE_byte)picture, false);
	for (int y = 0; y < SCREEN_H; ++y)
		memcpy(panel_picture + y * SCREEN_W, (const Uint8 *)surface->pixels + y * surface->pitch, SCREEN_W);
	SDL_DestroySurface(surface);
	printf("hud: the panel's picture from %s\n", path);
}

static void hud_panel_hd(const SDL_Surface *hud)
{
	enum { W = SCREEN_W - L3D_PLAYFIELD_W, H = SCREEN_H };
	static Uint32 panel[W * H], twice[W * 2 * H * 2], hd[PANEL_HD_W * PANEL_HD_H];
	static Uint32 last_hash = 0;
	static bool made = false;

	load_panel_art(twoPlayerMode ? 6 : 3);

	Uint32 hash = panel_art != NULL ? 1u : 2u;
	for (int y = 0; y < H; ++y)
		for (int x = 0; x < W; ++x)
		{
			Uint32 c = screen_rgba[y * SCREEN_W + L3D_PLAYFIELD_W + x];
			// Over the upscaled picture: only what the game drew over its own picture, and the
			// green labels and their boxes (FRONT GUN, SHIELD...), which upscalers smear.
			const Uint8 *rgb = (const Uint8 *)&c;
			const bool label = rgb[1] > rgb[0] + 12 && rgb[1] > rgb[2] + 12;
			if (panel_art != NULL && !label &&
			    ((const Uint8 *)hud->pixels)[y * hud->pitch + L3D_PLAYFIELD_W + x] ==
			    panel_picture[y * SCREEN_W + L3D_PLAYFIELD_W + x])
				c = 0;
			panel[y * W + x] = c;
			hash = (hash ^ c) * 16777619u;
		}
	if (made && hash == last_hash)
		return;
	scale2x(panel, W, H, twice);
	scale2x(twice, W * 2, H * 2, hd);
	btbh_gpu_texture_update_rgba8(panel_texture, (const uint8_t *)hd, 0, 0, PANEL_HD_W, PANEL_HD_H);
	last_hash = hash;
	made = true;
}

/*
 * The modern HUD (settings3d.hud_modern): instead of the panel beside the playfield, a few slim
 * gauges over the scene, from the game's state. Bottom left: shield, armor and the generator's
 * power; bottom right: the guns' power levels and the sidekicks' ammunition; at the top, the
 * level's name as it starts. Sizes in u, the window's height over 200 (a pixel of the original
 * screen). Text in the game's fonts, magnified as the panel is (Scale2x twice) and tinted.
 */
typedef struct
{
	char text[24];
	int font;               // large_font, normal_font, small_font
	int x, y, w, h;         // in the text texture (font pixels)
} HudText;

enum { HUD_SHIELD, HUD_ARMOR, HUD_POWER, HUD_FRONT, HUD_REAR, HUD_LEVEL, HUD_TEXTS };

static HudText hud_texts[HUD_TEXTS];

// Writes the texts into the text texture when they change.
static void update_hud_texts(void)
{
	static char made[HUD_TEXTS][24];
	bool same = true;
	for (int i = 0; i < HUD_TEXTS; ++i)
		same = same && strcmp(made[i], hud_texts[i].text) == 0;
	static bool once = false;
	if (same && once)
		return;
	once = true;

	static SDL_Surface *surface = NULL;
	if (surface == NULL && (surface = SDL_CreateSurface(HUD_TEXT_W, HUD_TEXT_H, SDL_PIXELFORMAT_INDEX8)) == NULL)
		return;
	SDL_FillSurfaceRect(surface, NULL, 0);
	int x = 1, y = 1, row_h = 0;
	for (int i = 0; i < HUD_TEXTS; ++i)
	{
		HudText *t = &hud_texts[i];
		static const int heights[3] = { 15, 10, 7 };
		t->w = JE_textWidth(t->text, t->font) + 1;
		t->h = heights[t->font];
		if (x + t->w >= HUD_TEXT_W)
		{
			x = 1;
			y += row_h + 2;
			row_h = 0;
		}
		t->x = x;
		t->y = y;
		draw_font_hv(surface, x, y, t->text, (Font)t->font, left_aligned, 15, 0);
		x += t->w + 2;
		row_h = SDL_max(row_h, t->h);
		memcpy(made[i], t->text, sizeof(made[i]));
	}

	// White, as bright as the glyph's shading, then magnified.
	static Uint32 mask[HUD_TEXT_W * HUD_TEXT_H], twice[HUD_TEXT_W * 2 * HUD_TEXT_H * 2], big[HUD_TEXT_W * 4 * HUD_TEXT_H * 4];
	for (int j = 0; j < HUD_TEXT_H; ++j)
		for (int i = 0; i < HUD_TEXT_W; ++i)
		{
			const Uint8 index = ((const Uint8 *)surface->pixels)[j * surface->pitch + i];
			const Uint8 grey = (Uint8)(150 + 105 * (index & 0x0f) / 15);
			const Uint8 rgba[4] = { grey, grey, grey, 255 };
			if (index != 0)
				memcpy(&mask[j * HUD_TEXT_W + i], rgba, sizeof(rgba));
			else
				mask[j * HUD_TEXT_W + i] = 0;
		}
	scale2x(mask, HUD_TEXT_W, HUD_TEXT_H, twice);
	scale2x(twice, HUD_TEXT_W * 2, HUD_TEXT_H * 2, big);
	btbh_gpu_texture_update_rgba8(hud_text_texture, (const uint8_t *)big, 0, 0, HUD_TEXT_W * 4, HUD_TEXT_H * 4);
}

static void hud_quad(float x, float y, float w, float h, const float left[4], const float right[4])
{
	if (hud_quad_count == MAX_HUD_QUADS)
		return;
	HudQuad *q = &hud_quads[hud_quad_count++];
	*q = (HudQuad){ x, y, w, h, 0, 0, 1, 1 };
	memcpy(q->left, left, sizeof(q->left));
	memcpy(q->right, right != NULL ? right : left, sizeof(q->right));
}

// A text at (x, y), u per font pixel, with a shadow; alpha fades it.
static void hud_text(int which, float x, float y, float u, const float color[4], bool right_aligned)
{
	const HudText *t = &hud_texts[which];
	if (t->w <= 0)
		return;
	if (right_aligned)
		x -= t->w * u;
	const float u0 = (float)t->x / HUD_TEXT_W, v0 = (float)t->y / HUD_TEXT_H;
	const float u1 = (float)(t->x + t->w) / HUD_TEXT_W, v1 = (float)(t->y + t->h) / HUD_TEXT_H;
	for (int pass = 0; pass < 2 && hud_quad_count < MAX_HUD_QUADS; ++pass)
	{
		const float shadow[4] = { 0, 0, 0, 0.75f * color[3] };
		const float *c = pass == 0 ? shadow : color;
		const float d = pass == 0 ? 0.6f * u : 0;
		HudQuad *q = &hud_quads[hud_quad_count++];
		*q = (HudQuad){ x + d, y + d, t->w * u, t->h * u, u0, v0, u1, v1, .text = true };
		memcpy(q->left, c, sizeof(q->left));
		memcpy(q->right, c, sizeof(q->right));
	}
}

// A gauge: its track, the fill (darker to brighter), a sheen along its top.
static void hud_bar(float x, float y, float w, float h, float fraction, const float color[4])
{
	const float track[4] = { 0.02f, 0.03f, 0.05f, 0.55f };
	hud_quad(x - 1, y - 1, w + 2, h + 2, track, NULL);
	fraction = SDL_clamp(fraction, 0.0f, 1.0f);
	if (fraction <= 0)
		return;
	const float dark[4] = { color[0] * 0.55f, color[1] * 0.55f, color[2] * 0.55f, color[3] };
	hud_quad(x, y, w * fraction, h, dark, color);
	const float sheen[4] = { 1, 1, 1, 0.25f * color[3] };
	hud_quad(x, y, w * fraction, h * 0.35f, sheen, NULL);
}

// Quads from first on fade when the ship is under them (within reach of their box).
static void hud_fade(int first, float x0, float y0, float x1, float y1, float ship_x, float ship_y, float reach)
{
	const float dx = SDL_max(SDL_max(x0 - ship_x, ship_x - x1), 0.0f);
	const float dy = SDL_max(SDL_max(y0 - ship_y, ship_y - y1), 0.0f);
	const float distance = sqrtf(dx * dx + dy * dy);
	static float fade[2] = { 1, 1 };  // eased, per group (top or bottom of the window)
	float *shown = &fade[y0 > 1 ? 0 : 1];
	const float target = distance < reach ? 0.3f + 0.7f * distance / reach : 1.0f;
	*shown += (target - *shown) * 0.2f;
	for (int i = first; i < hud_quad_count; ++i)
	{
		hud_quads[i].left[3] *= *shown;
		hud_quads[i].right[3] *= *shown;
	}
}

static void build_modern_hud(float window_w, float window_h)
{
	hud_quad_count = 0;
	if (!modern_hud())
		return;
	const Player *p = &player[0];

	// The level's name, for a few seconds as a level starts.
	static char shown_level[11] = "";
	static Uint64 level_since = 0;
	if (strcmp(shown_level, levelName) != 0)
	{
		SDL_strlcpy(shown_level, levelName, sizeof(shown_level));
		level_since = SDL_GetTicks();
	}
	SDL_strlcpy(hud_texts[HUD_SHIELD].text, "SHIELD", sizeof(hud_texts[0].text));
	SDL_strlcpy(hud_texts[HUD_ARMOR].text, "ARMOR", sizeof(hud_texts[0].text));
	SDL_strlcpy(hud_texts[HUD_POWER].text, "POWER", sizeof(hud_texts[0].text));
	SDL_strlcpy(hud_texts[HUD_FRONT].text, "FRONT", sizeof(hud_texts[0].text));
	SDL_strlcpy(hud_texts[HUD_REAR].text, "REAR", sizeof(hud_texts[0].text));
	SDL_strlcpy(hud_texts[HUD_LEVEL].text, levelName, sizeof(hud_texts[0].text));
	for (int i = 0; i < HUD_TEXTS; ++i)
		hud_texts[i].font = i == HUD_LEVEL ? large_font : small_font;
	update_hud_texts();

	const float u = window_h / 200.0f;
	const float label_u = 0.7f * u;  // the labels' font pixel
	const float label_color[4] = { 0.85f, 0.88f, 0.95f, 0.9f };
	const float backing[4] = { 0, 0, 0, 0.28f };
	const float row_h = 6 * u;

	// Shown values ease towards the game's, so gauges slide.
	static float shown[3] = { -1, -1, -1 };
	const float target[3] = {
		p->shield_max > 0 ? (float)p->shield / p->shield_max : 0,
		p->armor / 28.0f,
		power / 900.0f,
	};
	for (int i = 0; i < 3; ++i)
		shown[i] = shown[i] < 0 ? target[i] : shown[i] + (target[i] - shown[i]) * 0.25f;

	// Where the ship is, so the gauges over it fade.
	float ship_wx = -1e9f, ship_wy = -1e9f;
	rgpu_playfield_to_window(p->x + 7.0f, p->y + 7.0f, &ship_wx, &ship_wy);

	// Bottom right: shield, armor, the generator's power.
	const bool generator = !onePlayerAction && !twoPlayerMode;
	const int rows = generator ? 3 : 2;
	const float bar_w = 64 * u, label_w = 24 * u;
	const float x1 = window_w - 6 * u, x0 = x1 - bar_w - label_w;
	const float y0 = window_h - 5 * u - rows * row_h;
	int first = hud_quad_count;
	hud_quad(x0 - 3 * u, y0 - 2.5f * u, x1 - x0 + 6 * u, rows * row_h + 3 * u, backing, NULL);
	const float shield_color[4] = { 0.35f, 0.75f, 1.0f, 1 };
	float armor_color[4] = { 1.0f, 0.55f, 0.25f, 1 };
	if (target[1] < 0.25f && (SDL_GetTicks() / 250) % 2 == 0)  // low armor flashes
	{
		armor_color[1] = 0.15f;
		armor_color[2] = 0.1f;
	}
	const float power_color[4] = { 1.0f, 0.85f, 0.3f, 1 };
	const float bar_x = x1 - bar_w;
	hud_text(HUD_SHIELD, x0, y0, label_u, label_color, false);
	hud_bar(bar_x, y0 + 0.8f * u, bar_w, 3 * u, shown[0], shield_color);
	hud_text(HUD_ARMOR, x0, y0 + row_h, label_u, label_color, false);
	hud_bar(bar_x, y0 + row_h + 0.8f * u, bar_w, 3 * u, shown[1], armor_color);
	if (generator)
	{
		hud_text(HUD_POWER, x0, y0 + 2 * row_h, label_u, label_color, false);
		hud_bar(bar_x, y0 + 2 * row_h + 1.2f * u, bar_w, 2 * u, shown[2], power_color);
	}
	hud_fade(first, x0 - 3 * u, y0 - 2.5f * u, x1 + 3 * u, window_h, ship_wx, ship_wy, 18 * u);

	// Top right: the guns' power levels (pips), the sidekicks' ammunition.
	const float pip = 3.4f * u, gap = 1.0f * u;
	const float pips_w = 11 * pip + 10 * gap;
	int sidekick_rows = 0;
	for (int i = 0; i < 2; ++i)
		sidekick_rows += p->items.sidekick[i] > 0 && p->sidekick[i].ammo_max > 0;
	const int right_rows = 2 + (sidekick_rows > 0);
	const float ry0 = 5 * u, px0 = x1 - pips_w;
	first = hud_quad_count;
	hud_quad(px0 - label_w - 3 * u, ry0 - 2.5f * u, pips_w + label_w + 6 * u, right_rows * row_h + 3 * u, backing, NULL);
	static const float gun_colors[2][4] = { { 0.45f, 1.0f, 0.55f, 1 }, { 1.0f, 0.75f, 0.35f, 1 } };
	for (int g = 0; g < 2; ++g)
	{
		const float y = ry0 + g * row_h;
		hud_text(g == 0 ? HUD_FRONT : HUD_REAR, px0 - label_w, y, label_u, label_color, false);
		const int level = p->items.weapon[g].id > 0 ? p->items.weapon[g].power : 0;
		for (int k = 0; k < 11; ++k)
		{
			const float off[4] = { 0.1f, 0.12f, 0.16f, 0.6f };
			const float *c = k < level ? gun_colors[g] : off;
			const float dim[4] = { c[0] * 0.6f, c[1] * 0.6f, c[2] * 0.6f, c[3] };
			hud_quad(px0 + k * (pip + gap), y + 0.6f * u, pip, 3.2f * u, k < level ? dim : c, c);
		}
	}
	if (sidekick_rows > 0)
	{
		const float y = ry0 + 2 * row_h + 0.8f * u;
		const float w = (pips_w - 2 * u) / 2;
		const float ammo_color[4] = { 0.8f, 0.6f, 1.0f, 1 };
		for (int i = 0; i < 2; ++i)
			if (p->items.sidekick[i] > 0 && p->sidekick[i].ammo_max > 0)
				hud_bar(px0 + i * (w + 2 * u), y, w, 2.5f * u, (float)p->sidekick[i].ammo / p->sidekick[i].ammo_max, ammo_color);
	}
	hud_fade(first, px0 - label_w - 3 * u, 0, x1 + 3 * u, ry0 + right_rows * row_h + 0.5f * u, ship_wx, ship_wy, 18 * u);

	// The level's name.
	const float since = (SDL_GetTicks() - level_since) / 1000.0f;
	if (since < 4.0f && levelName[0] != '\0' && !menu.on)
	{
		const float alpha = SDL_clamp(SDL_min(since / 0.5f, (4.0f - since) / 1.0f), 0.0f, 1.0f);
		const float title[4] = { 1.0f, 0.92f, 0.75f, alpha };
		const float scale = 0.9f * u;
		hud_text(HUD_LEVEL, window_w / 2 + hud_texts[HUD_LEVEL].w * scale / 2, 30 * u, scale, title, true);
	}
}

static void present_3d(const SDL_Surface *hud, const L3DFrame *frame, const SDL_Rect *dst);

void rgpu_present_3d_ahead(const SDL_Surface *hud, const L3DFrame *frame, const SDL_Rect *dst, float ticks)
{
	ahead = ticks;
	present_3d(hud, frame, dst);
	ahead = 0;
}

bool rgpu_window_to_playfield(float wx, float wy, float *x, float *y)
{
	if (!shown_view.valid)
		return false;
	const Camera3D *camera = &shown_view.camera;
	const float ndc[2] = { wx / shown_view.window_w * 2 - 1, 1 - wy / shown_view.window_h * 2 };
	float slope[2], ray[3];
	for (int i = 0; i < 2; ++i)
		slope[i] = (ndc[i] - camera->ndc_offset[i]) / camera->ndc_scale[i] * camera->tan_half[i];
	if (shown_view.upside_down)
		slope[1] = -slope[1];
	for (int i = 0; i < 3; ++i)
		ray[i] = camera->forward[i] + camera->right[i] * slope[0] + camera->up[i] * slope[1];
	if (ray[1] > -1e-6f)
		return false;  // above the horizon
	const float s = (shown_view.reference - camera->position[1]) / ray[1];
	*x = camera->position[0] + ray[0] * s;
	*y = camera->position[2] + ray[2] * s;
	return true;
}

bool rgpu_playfield_to_window(float x, float y, float *wx, float *wy)
{
	if (!shown_view.valid)
		return false;
	const float *m = shown_view.camera.view_projection.m;
	const float p[4] = { x, shown_view.reference, y, 1 };
	float clip[4];
	for (int r = 0; r < 4; ++r)
		clip[r] = m[r] * p[0] + m[4 + r] * p[1] + m[8 + r] * p[2] + m[12 + r] * p[3];
	if (clip[3] <= 1e-6f)
		return false;
	*wx = (clip[0] / clip[3] + 1) / 2 * shown_view.window_w;
	*wy = (1 - clip[1] / clip[3]) / 2 * shown_view.window_h;
	return true;
}

void rgpu_present_3d_menu(const SDL_Surface *screen, const Uint8 *backdrop, const int (*shades)[4], int shade_count,
                          const float fade[4], const L3DFrame *frame, const SDL_Rect *dst, SDL_Rect *screen_rect)
{
	menu.on = true;
	menu.backdrop = backdrop;
	menu.shades = shades;
	menu.shade_count = shade_count;
	memcpy(canvas_fade, fade, sizeof(canvas_fade));
	ahead = 0;
	present_3d(screen, frame, dst);
	menu.on = false;
	canvas_fade[3] = 0;

	// The screen's pixels where the playfield's part of them shows.
	int w = 0, h = 0;
	SDL_GetWindowSize(btbh_gpu_window_sdl_window(window), &w, &h);
	const Layout3D layout = layout_3d((float)w, (float)h, dst);
	if (!layout.split)
	{
		*screen_rect = *dst;
		return;
	}
	screen_rect->x = (int)layout.playfield[0];
	screen_rect->y = (int)layout.playfield[1];
	screen_rect->w = (int)(layout.playfield[2] * SCREEN_W / L3D_PLAYFIELD_W + 0.5f);
	screen_rect->h = (int)(layout.playfield[3] * SCREEN_H / L3D_PLAYFIELD_H + 0.5f);
}

float rgpu_playfield_scale(void)
{
	int w = 0, h = 0;
	SDL_GetWindowSize(btbh_gpu_window_sdl_window(window), &w, &h);
	const SDL_Rect none = { 0, 0, 0, 0 };
	const Layout3D layout = layout_3d((float)w, (float)h, &none);
	const float scale = layout.playfield[2] / L3D_PLAYFIELD_W;
	return scale > 0 ? scale : 1;
}

void rgpu_present_3d(const SDL_Surface *hud, const L3DFrame *frame, const SDL_Rect *dst)
{
	static Uint64 total_ticks = 0;
	static int frames = 0;
	const Uint64 start = SDL_GetPerformanceCounter();

	present_3d(hud, frame, dst);

	total_ticks += SDL_GetPerformanceCounter() - start;
	if (++frames == 300)
	{
		if (SDL_getenv("TYR3D_PROFILE") != NULL)
			printf("3d present: %.2f ms/frame (%d layers)\n",
			       (double)total_ticks * 1000.0 / SDL_GetPerformanceFrequency() / frames, frame->layer_count);
		total_ticks = 0;
		frames = 0;
	}
}

// Drops loaded models when models.cfg was reloaded (indices may now mean other models).
static void sync_model_cache(void)
{
	static unsigned int generation = 0;
	if (generation == m3d_generation)
		return;
	generation = m3d_generation;
	for (int i = 0; i < M3D_MAX_MODELS; ++i)
		if (loaded_models[i].gpu != NULL)
			btbh_gpu_model_destroy(loaded_models[i].gpu);
	memset(loaded_models, 0, sizeof(loaded_models));
}

static float srgb_to_linear(Uint8 value);

// Palette materials are named "<name>@<palette index>" (tyrkit.material(palette=...)): the game
// colours them with the palette, as it does their sprites, so they follow the level's palette,
// its fades and filters. The renderer's material slot 0 is its default material, so glTF
// material i is slot i + 1.
static void read_palette_materials(const char *path, LoadedModel *loaded)
{
	for (size_t m = 0; m < COUNTOF(loaded->palette_index); ++m)
		loaded->palette_index[m] = -1;

	cgltf_options options;
	memset(&options, 0, sizeof(options));
	cgltf_data *data = NULL;
	if (cgltf_parse_file(&options, path, &data) != cgltf_result_success)
		return;
	for (cgltf_size i = 0; i < data->materials_count && i + 1 < COUNTOF(loaded->palette_index); ++i)
	{
		const char *name = data->materials[i].name;
		const char *at = name != NULL ? SDL_strrchr(name, '@') : NULL;
		if (at != NULL && SDL_isdigit((unsigned char)at[1]))
			loaded->palette_index[i + 1] = SDL_clamp(SDL_atoi(at + 1), 0, 255);
	}
	cgltf_free(data);
}

static Uint8 palette_albedo(Uint8 value)
{
	return (Uint8)SDL_min(255.0f, srgb_to_linear(value) / MODEL_UP_FACING_LIGHT * 255.0f + 0.5f);
}

static LoadedModel *get_model(int index)
{
	LoadedModel *loaded = &loaded_models[index];
	if (!loaded->load_attempted)
	{
		loaded->load_attempted = true;
		const M3DModel *model = &m3d_models[index];
		BTBHGPUModelReport report;
		loaded->gpu = btbh_gpu_window_model_load(window, model->path, &report);
		if (loaded->gpu == NULL)
		{
			fprintf(stderr, "warning: failed to load model %s: %s\n", model->path, report.message);
			return loaded;
		}
		loaded->center[0] = (report.minimum_x + report.maximum_x) / 2;
		loaded->center[1] = (report.minimum_y + report.maximum_y) / 2;
		loaded->center[2] = (report.minimum_z + report.maximum_z) / 2;
		loaded->half[0] = (report.maximum_x - report.minimum_x) / 2;
		loaded->half[1] = (report.maximum_y - report.minimum_y) / 2;
		loaded->half[2] = (report.maximum_z - report.minimum_z) / 2;
		loaded->footprint = SDL_max(report.maximum_x - report.minimum_x, report.maximum_z - report.minimum_z);
		loaded->material_count = SDL_min(report.material_count, (uint32_t)COUNTOF(loaded->materials));
		for (uint32_t m = 0; m < loaded->material_count; ++m)
			btbh_gpu_model_material_info(loaded->gpu, m, &loaded->materials[m]);
		read_palette_materials(model->path, loaded);
		printf("model %s: %u meshes, %u materials, footprint %.2f\n", model->name, report.mesh_count,
		       report.material_count, loaded->footprint);
	}
	return loaded->gpu != NULL ? loaded : NULL;
}

// Where an object is drawn in a frame shown `ahead` of its tick: moved on by its velocity, or,
// the ship the mouse moves directly, where the mouse has moved it so far.
static float object_x(const L3DObject *object)
{
	return object->x + (object->pointer ? l3d_pointer_lead[0] : object->vx * ahead);
}

static float object_y(const L3DObject *object)
{
	return object->y + (object->pointer ? l3d_pointer_lead[1] : object->vy * ahead);
}

// An instance at world coordinates.
static void write_instance_world(float *instance, const Mat4 *transform, float brightness)
{
	memcpy(instance, transform->m, 16 * sizeof(float));
	instance[16] = instance[17] = instance[18] = brightness;
	instance[19] = 1;
	instance[20] = instance[21] = instance[22] = instance[23] = 0;
}

// An instance at game coordinates on its plane (aligned, see align).
static void write_instance(float *instance, const Mat4 *transform, float brightness)
{
	const Mat4 world = aligned(transform);
	write_instance_world(instance, &world, brightness);
}

static void init_batch(BTBHGPUSceneGeometryBatch *b)
{
	memset(b, 0, sizeof(*b));
	b->material_slot = -1;
	b->albedo_red = b->albedo_green = b->albedo_blue = b->albedo_alpha = 255;
	b->uv_scale_x = b->uv_scale_y = 1.0f;
	b->normal_scale = 1;
	b->occlusion = 1;
	b->roughness = 1;
	b->cull_mode = BTBH_GPU_SCENE_CULL_NONE;
	b->depth_compare = BTBH_GPU_SCENE_DEPTH_LESS_EQUAL;
	b->stencil_compare = BTBH_GPU_SCENE_DEPTH_ALWAYS;
	b->stencil_pass = BTBH_GPU_SCENE_STENCIL_REPLACE;
	b->stencil_mask = 0xff;
	b->billboard_mode = BTBH_GPU_SCENE_BILLBOARD_DISABLED;
	b->blend_mode = BTBH_GPU_SCENE_BLEND_ALPHA;
}

#define MAX_INSTANCES (L3D_MAX_LAYERS + L3D_MAX_OBJECTS + MAX_TILES + MAX_STARS + L3D_MAX_BACKGROUNDS + P3D_MAX_PARTICLES + \
                       L3D_MAX_GLOWS + DEEP_STARS + MAX_PLANTS + MAX_CLOUD_PUFFS)
// Background tiles: per background, a batch for each of its cells mirrored or not and fading
// either way or not at all (B3D_ATLAS_CELLS covers the cells of all three backgrounds).
// Terrain: rows of the three backgrounds' maps drawn at most.
#define MAX_TERRAIN_ROW_DRAWS 192
#define MAX_BATCHES (L3D_MAX_LAYERS + M3D_MAX_MODELS * 4 + L3D_MAX_OBJECTS + B3D_ATLAS_CELLS * 12 + 1 + L3D_MAX_BACKGROUNDS + P3D_KIND_COUNT + 1 + 1 + MAX_TERRAIN_ROW_DRAWS + 8)

static float instances[MAX_INSTANCES * 24];
static BTBHGPUSceneGeometryBatch batches[MAX_BATCHES];

// Appends instances and batches for the frame's model objects, grouped by model. colors are the
// frame's palette colours, for palette materials.
// mirror turns the models left for right: in a vertically mirrored view (upside-down levels) that
// makes them look turned round rather than mirrored, so their triangles still face the camera the
// right way round for the renderer's lighting.
static void add_object_batches(const L3DFrame *frame, const Uint32 colors[256], bool mirror, int *instance_count,
                               int *batch_count)
{
	sync_model_cache();

	for (int model_index = 0; model_index < m3d_model_count; ++model_index)
	{
		// Objects of the model in each state (sprite filter, ghost) share batches.
		bool done[L3D_MAX_OBJECTS] = { false };
		for (int f = 0; f < frame->object_count; ++f)
		{
			const L3DObject *state = &frame->objects[f];
			if (done[f] || state->model != model_index)
				continue;

			const int first_instance = *instance_count;
			const LoadedModel *loaded = get_model(model_index);
			for (int o = f; o < frame->object_count; ++o)
			{
				const L3DObject *object = &frame->objects[o];
				if (done[o] || object->model != model_index || object->filter != state->filter || object->ghost != state->ghost)
					continue;
				done[o] = true;
				if (loaded == NULL || *instance_count >= MAX_INSTANCES)
					continue;

				const M3DModel *model = &m3d_models[model_index];
				const float scale = model->size > 0 && loaded->footprint > 0 ? model->size / loaded->footprint : 1.0f;
				const float height = l3d_layer_height(object->layer) * rgpu_camera.height_scale + object->height +
				                     (object->layer == L3D_GROUND_ENEMY ? terrain_lift(object->x, object->y) : 0.0f);
				Mat4 mirror_x = mat4_identity();
				if (mirror)
					mirror_x.m[0] = -1;
				const Mat4 chain[] = {
					mat4_translation(object_x(object), height, object_y(object)),
					mirror_x,
					mat4_rotation(1, -object->yaw),
					mat4_rotation(2, -object->roll),
					mat4_rotation(1, model->yaw),
					mat4_rotation(0, model->pitch),
					mat4_rotation(2, model->roll),
					mat4_scaling(scale),
					// Models authored in game pixels keep their origin (the sprite's centre) on the
					// screen; others are centred on their bounds. Both are centred in height.
					mat4_translation(model->size > 0 ? -loaded->center[0] : 0.0f, model->keep_origin ? 0.0f : -loaded->center[1],
					                 model->size > 0 ? -loaded->center[2] : 0.0f),
				};
				Mat4 transform = mat4_chain((int)COUNTOF(chain), chain);
				if (object->wreck)  // slumped to under half its height
					for (int k = 1; k < 12; k += 4)
						transform.m[k] *= WRECK_SLUMP;
				// Nothing sinks into the ground: models centred on their layer's height (items on
				// the ground enemies' layer) are lifted by what their turned bounds reach below it.
				const float reach = fabsf(transform.m[1]) * loaded->half[0] + fabsf(transform.m[5]) * loaded->half[1] +
				                    fabsf(transform.m[9]) * loaded->half[2];
				if (!model->keep_origin && height - reach < 0.3f)
					transform.m[13] += 0.3f - (height - reach);
				write_instance(instances + *instance_count * 24, &transform, object->wreck ? WRECK_SHADE : 1.0f);
				++*instance_count;
			}

			const int count = *instance_count - first_instance;
			if (count == 0 || loaded == NULL)
				continue;

			const uint32_t material_count = loaded->material_count > 0 ? loaded->material_count : 1;
			for (uint32_t m = 0; m < material_count && *batch_count < MAX_BATCHES; ++m)
			{
				BTBHGPUSceneGeometryBatch *b = &batches[(*batch_count)++];
				init_batch(b);
				b->kind = BTBH_GPU_SCENE_GEOMETRY_MODEL;
				b->model = loaded->gpu;
				b->first_instance = first_instance;
				b->instance_count = count;
				if (loaded->material_count > 0)
				{
					const BTBHGPUModelMaterialInfo *info = &loaded->materials[m];
					b->material_slot = (int32_t)m;
					b->albedo_texture = info->albedo_texture;
					b->albedo_red = info->albedo_red;
					b->albedo_green = info->albedo_green;
					b->albedo_blue = info->albedo_blue;
					b->albedo_alpha = info->albedo_alpha;
					b->normal_texture = info->normal_texture;
					b->orm_texture = info->orm_texture;
					b->normal_scale = info->normal_scale;
					b->occlusion = info->occlusion;
					b->roughness = info->roughness;
					b->metalness = info->metalness;
					b->emission_texture = info->emission_texture;
					b->emission_red = info->emission_red;
					b->emission_green = info->emission_green;
					b->emission_blue = info->emission_blue;
					b->emission_alpha = info->emission_alpha;
					b->emission_energy = info->emission_energy;
					if (loaded->palette_index[m] >= 0)
					{
						// Palette materials take the sprite filter as the sprite does: index = filter | shade.
						const int index = state->filter != 0 ? state->filter | (loaded->palette_index[m] & 0x0f)
						                                     : loaded->palette_index[m];
						const Uint8 *c = (const Uint8 *)&colors[index];
						b->albedo_red = palette_albedo(c[0]);
						b->albedo_green = palette_albedo(c[1]);
						b->albedo_blue = palette_albedo(c[2]);
					}
				}
				if (b->albedo_alpha < 255)  // see-through materials (glass)
					b->transparency_enabled = 1;
				if (state->ghost)
				{
					b->transparency_enabled = 1;
					b->albedo_alpha = (Uint8)(b->albedo_alpha / 2);
				}
			}
		}
	}
}

/* --- Volumetric sprites -------------------------------------------------------------------- */

#define MAX_VOLUME_SHEETS 12
#define SHEET_SPRITES (V3D_COLUMNS * V3D_ROWS)

struct VolumeSheet
{
	const Uint8 *data;  // sheet data this entry was decoded from; NULL = free slot
	Uint8 indices[V3D_ATLAS_W * V3D_ATLAS_H];
	Uint8 cover[V3D_ATLAS_W * V3D_ATLAS_H];
	BTBHGPUTexture *texture;
	Uint32 colors_hash;  // palette the texture was coloured with
	struct
	{
		Uint8 filter;  // 0 = free
		Uint32 colors_hash;
		BTBHGPUTexture *texture;
	} filtered[4];  // the sheet with a sprite filter applied (index = filter | shade)
	// [style][large][open sides][sprite index]
	BTBHGPUCustomMesh *meshes[V3D_STYLE_COUNT][2][16][SHEET_SPRITES + 1];
	bool mesh_built[V3D_STYLE_COUNT][2][16][SHEET_SPRITES + 1];
};

static VolumeSheet volume_sheets[MAX_VOLUME_SHEETS];
static unsigned int volume_generation = 0;

// The GPU objects are owned by the window and released with it.
static void forget_volume_sheets(void)
{
	memset(volume_sheets, 0, sizeof(volume_sheets));
}

static void release_volume_sheet(VolumeSheet *entry)
{
	for (int s = 0; s < V3D_STYLE_COUNT; ++s)
		for (int l = 0; l < 2; ++l)
			for (int o = 0; o < 16; ++o)
				for (int i = 0; i <= SHEET_SPRITES; ++i)
					if (entry->meshes[s][l][o][i] != NULL)
						btbh_gpu_custom_mesh_destroy(entry->meshes[s][l][o][i]);
	if (entry->texture != NULL)
		btbh_gpu_texture_destroy(entry->texture);
	for (size_t f = 0; f < COUNTOF(entry->filtered); ++f)
		if (entry->filtered[f].texture != NULL)
			btbh_gpu_texture_destroy(entry->filtered[f].texture);
	memset(entry, 0, sizeof(*entry));
}

// The sheet's texture with a sprite filter applied, as blit_sprite2_filter colours it.
static BTBHGPUTexture *filtered_volume_texture(VolumeSheet *entry, const Uint32 colors[256], Uint32 colors_hash, Uint8 filter)
{
	if (filter == 0)
		return entry->texture;
	size_t slot = 0;
	for (size_t f = 0; f < COUNTOF(entry->filtered); ++f)
	{
		if (entry->filtered[f].filter == filter && entry->filtered[f].texture != NULL)
		{
			slot = f;
			if (entry->filtered[f].colors_hash == colors_hash)
				return entry->filtered[f].texture;
			break;
		}
		if (entry->filtered[f].filter == 0)
			slot = f;
	}
	static Uint32 rgba[V3D_ATLAS_W * V3D_ATLAS_H];
	for (int i = 0; i < V3D_ATLAS_W * V3D_ATLAS_H; ++i)
		rgba[i] = entry->cover[i] ? colors[filter | (entry->indices[i] & 0x0f)] : 0;
	if (entry->filtered[slot].texture == NULL)
	{
		BTBHGPUTextureReport report;
		entry->filtered[slot].texture = btbh_gpu_window_texture_create_rgba8_ex(window, (const uint8_t *)rgba, V3D_ATLAS_W,
			V3D_ATLAS_H, 0, BTBH_GPU_TEXTURE_FILTER_NEAREST, BTBH_GPU_TEXTURE_WRAP_CLAMP, BTBH_GPU_TEXTURE_COLOR_SPACE_SRGB, &report);
		if (entry->filtered[slot].texture == NULL)
			return entry->texture;
	}
	else
	{
		btbh_gpu_texture_update_rgba8(entry->filtered[slot].texture, (const uint8_t *)rgba, 0, 0, V3D_ATLAS_W, V3D_ATLAS_H);
	}
	entry->filtered[slot].filter = filter;
	entry->filtered[slot].colors_hash = colors_hash;
	return entry->filtered[slot].texture;
}

static Uint32 hash_colors(const Uint32 colors[256])
{
	Uint32 hash = 2166136261u;
	const Uint8 *bytes = (const Uint8 *)colors;
	for (int i = 0; i < 256 * 4; ++i)
		hash = (hash ^ bytes[i]) * 16777619u;
	return hash;
}

static VolumeSheet *get_volume_sheet(const Sprite2_array *sheet, const Uint32 colors[256], Uint32 colors_hash)
{
	// Sheets are reloaded between levels; drop everything decoded from old data.
	if (volume_generation != sprite2_generation)
	{
		for (int i = 0; i < MAX_VOLUME_SHEETS; ++i)
			if (volume_sheets[i].data != NULL)
				release_volume_sheet(&volume_sheets[i]);
		volume_generation = sprite2_generation;
	}
	if (sheet == NULL || sheet->data == NULL)
		return NULL;

	VolumeSheet *entry = NULL;
	for (int i = 0; i < MAX_VOLUME_SHEETS && entry == NULL; ++i)
		if (volume_sheets[i].data == sheet->data)
			entry = &volume_sheets[i];
	if (entry == NULL)
	{
		for (int i = 0; i < MAX_VOLUME_SHEETS && entry == NULL; ++i)
			if (volume_sheets[i].data == NULL)
				entry = &volume_sheets[i];
		if (entry == NULL)
		{
			entry = &volume_sheets[0];
			release_volume_sheet(entry);
		}
		entry->data = sheet->data;
		v3d_decode_sheet(sheet, entry->indices, entry->cover);
	}

	if (entry->texture == NULL || entry->colors_hash != colors_hash)
	{
		static Uint32 rgba[V3D_ATLAS_W * V3D_ATLAS_H];
		for (int i = 0; i < V3D_ATLAS_W * V3D_ATLAS_H; ++i)
			rgba[i] = entry->cover[i] ? colors[entry->indices[i]] : 0;
		if (entry->texture == NULL)
		{
			BTBHGPUTextureReport report;
			entry->texture = btbh_gpu_window_texture_create_rgba8_ex(window, (const uint8_t *)rgba, V3D_ATLAS_W, V3D_ATLAS_H, 0,
				BTBH_GPU_TEXTURE_FILTER_NEAREST, BTBH_GPU_TEXTURE_WRAP_CLAMP, BTBH_GPU_TEXTURE_COLOR_SPACE_SRGB, &report);
			if (entry->texture == NULL)
				fprintf(stderr, "warning: volumetric sprite texture: %s\n", report.message);
		}
		else
		{
			btbh_gpu_texture_update_rgba8(entry->texture, (const uint8_t *)rgba, 0, 0, V3D_ATLAS_W, V3D_ATLAS_H);
		}
		entry->colors_hash = colors_hash;
	}
	return entry->texture != NULL ? entry : NULL;
}

static BTBHGPUCustomMesh *get_volume_mesh(VolumeSheet *entry, unsigned int sprite, bool large, int style, Uint8 open)
{
	if (sprite == 0 || sprite > SHEET_SPRITES || style < 0 || style >= V3D_STYLE_COUNT)
		return NULL;
	open &= 15;
	BTBHGPUCustomMesh **mesh = &entry->meshes[style][large][open][sprite];
	if (!entry->mesh_built[style][large][open][sprite])
	{
		entry->mesh_built[style][large][open][sprite] = true;
		static V3DVertex vertices[V3D_MAX_VERTICES];
		static Uint32 indices[V3D_MAX_INDICES];
		int vertex_count = 0;
		const float length = sqrtf(sun_direction[0] * sun_direction[0] + sun_direction[1] * sun_direction[1] +
		                           sun_direction[2] * sun_direction[2]);
		const float light[3] = { -sun_direction[0] / length, -sun_direction[1] / length, -sun_direction[2] / length };
		const int index_count = v3d_build_mesh(entry->indices, entry->cover, sprite, large, (V3DStyle)style, open,
		                                       light, vertices, &vertex_count, indices);
		if (index_count > 0)
		{
			BTBHGPUCustomMeshReport report;
			*mesh = btbh_gpu_window_custom_mesh_create(window, vertices,
				(uint32_t)(vertex_count * sizeof(V3DVertex)), (uint32_t)vertex_count, indices, (uint32_t)index_count, &report);
			if (*mesh == NULL)
				fprintf(stderr, "warning: volumetric sprite mesh: %s\n", report.message);
		}
	}
	return *mesh;
}

/*
 * HD volumes: sheets upscaled 4x (tools/hd_sheets.py, in TYR3D_UPSCALE_DIR/sheets) give the volumes
 * a smooth outline and the upscale's detail (v3d_build_hd_mesh). Their pictures are in the levels'
 * palette: the frame's palette (fades) tints them; filtered sprites and sprites the upscale lacks
 * keep the original pixels. TYR3D_HD=0 turns them off.
 */
#define MAX_HD_SHEETS 24

typedef struct
{
	char name[16];
	bool tried;
	Uint8 *rgba;
	int w, h;
	BTBHGPUTexture *texture;
	Sint8 has[SHEET_SPRITES + 1][2];  // -1 unknown, 0 no, 1 yes; by sprite and large
	BTBHGPUCustomMesh *meshes[V3D_STYLE_COUNT][2][16][SHEET_SPRITES + 1];
	bool mesh_built[V3D_STYLE_COUNT][2][16][SHEET_SPRITES + 1];
} HDSheet;

static HDSheet *hd_sheets[MAX_HD_SHEETS];
static int hd_sheet_count = 0;

static bool hd_enabled(void)
{
	static int enabled = -1;
	if (enabled < 0)
		enabled = SDL_getenv("TYR3D_HD") == NULL || SDL_atoi(SDL_getenv("TYR3D_HD")) != 0;
	return enabled != 0;
}

static HDSheet *get_hd_sheet(const Sprite2_array *sheet)
{
	const char *name = v3d_sheet_name(sheet);
	if (name == NULL || !hd_enabled())
		return NULL;
	for (int i = 0; i < hd_sheet_count; ++i)
		if (strcmp(hd_sheets[i]->name, name) == 0)
			return hd_sheets[i]->texture != NULL ? hd_sheets[i] : NULL;
	if (hd_sheet_count == MAX_HD_SHEETS)
		return NULL;
	HDSheet *hd = calloc(1, sizeof(HDSheet));
	if (hd == NULL)
		return NULL;
	hd_sheets[hd_sheet_count++] = hd;
	SDL_strlcpy(hd->name, name, sizeof(hd->name));
	memset(hd->has, -1, sizeof(hd->has));

	char dir[1024], path[1200];
	snprintf(path, sizeof(path), "%s/sheets/%s.hd",
	         tyr3d_resource_dir("TYR3D_UPSCALE_DIR", TYR3D_UPSCALE_DIR, "upscale", dir, sizeof(dir)), name);
	FILE *f = fopen(path, "rb");
	if (f == NULL)
		return NULL;
	Uint8 header[12];
	Uint8 *packed = NULL;
	long packed_size = 0;
	if (fread(header, 1, sizeof(header), f) == sizeof(header) && memcmp(header, "TYHD", 4) == 0)
	{
		fseek(f, 0, SEEK_END);
		packed_size = ftell(f) - (long)sizeof(header);
		fseek(f, (long)sizeof(header), SEEK_SET);
		packed = packed_size > 0 ? malloc((size_t)packed_size) : NULL;
		if (packed != NULL && fread(packed, 1, (size_t)packed_size, f) != (size_t)packed_size)
		{
			free(packed);
			packed = NULL;
		}
	}
	fclose(f);
	if (packed == NULL)
		return NULL;
	Uint32 size_values[2];
	memcpy(size_values, header + 4, sizeof(size_values));
	hd->w = (int)SDL_Swap32LE(size_values[0]);
	hd->h = (int)SDL_Swap32LE(size_values[1]);
	uLongf size = (uLongf)hd->w * (uLongf)hd->h * 4;
	hd->rgba = malloc(size);
	if (hd->rgba == NULL || uncompress(hd->rgba, &size, packed, (uLong)packed_size) != Z_OK || size != (uLongf)hd->w * hd->h * 4)
	{
		free(packed);
		free(hd->rgba);
		hd->rgba = NULL;
		return NULL;
	}
	free(packed);
	BTBHGPUTextureReport report;
	hd->texture = btbh_gpu_window_texture_create_rgba8_ex(window, hd->rgba, (uint32_t)hd->w, (uint32_t)hd->h, 1,
		BTBH_GPU_TEXTURE_FILTER_LINEAR, BTBH_GPU_TEXTURE_WRAP_CLAMP, BTBH_GPU_TEXTURE_COLOR_SPACE_SRGB, &report);
	if (hd->texture == NULL)
		fprintf(stderr, "warning: HD sheet %s: %s\n", name, report.message);
	else
		printf("hd: %s (%d x %d)\n", path, hd->w, hd->h);
	return hd->texture != NULL ? hd : NULL;
}

// The GPU objects go with the window; the pictures stay.
static void forget_hd_sheets(void)
{
	for (int i = 0; i < hd_sheet_count; ++i)
	{
		free(hd_sheets[i]->rgba);
		free(hd_sheets[i]);
	}
	hd_sheet_count = 0;
}

static BTBHGPUCustomMesh *get_hd_mesh(HDSheet *hd, unsigned int sprite, bool large, int style, Uint8 open)
{
	if (sprite == 0 || sprite > SHEET_SPRITES || style < 0 || style >= V3D_STYLE_COUNT)
		return NULL;
	if (hd->has[sprite][large] < 0)
		hd->has[sprite][large] = (Sint8)v3d_hd_has_sprite(hd->rgba, hd->w, hd->h, sprite, large);
	if (!hd->has[sprite][large])
		return NULL;
	open &= 15;
	BTBHGPUCustomMesh **mesh = &hd->meshes[style][large][open][sprite];
	if (!hd->mesh_built[style][large][open][sprite])
	{
		hd->mesh_built[style][large][open][sprite] = true;
		static V3DVertex vertices[V3D_HD_MAX_VERTICES];
		static Uint32 indices[V3D_HD_MAX_INDICES];
		int vertex_count = 0;
		const float length = sqrtf(sun_direction[0] * sun_direction[0] + sun_direction[1] * sun_direction[1] +
		                           sun_direction[2] * sun_direction[2]);
		const float light[3] = { -sun_direction[0] / length, -sun_direction[1] / length, -sun_direction[2] / length };
		const int index_count = v3d_build_hd_mesh(hd->rgba, hd->w, hd->h, sprite, large, (V3DStyle)style, open, light,
		                                          vertices, &vertex_count, indices);
		if (index_count > 0)
		{
			BTBHGPUCustomMeshReport report;
			*mesh = btbh_gpu_window_custom_mesh_create(window, vertices, (uint32_t)(vertex_count * sizeof(V3DVertex)),
			                                           (uint32_t)vertex_count, indices, (uint32_t)index_count, &report);
			if (*mesh == NULL)
				fprintf(stderr, "warning: HD volume mesh: %s\n", report.message);
		}
	}
	return *mesh;
}

// How the frame's palette differs from the levels' palette the HD pictures are in, per channel
// (fades to black or white), as a tint.
static void hd_tint(const Uint32 colors[256], float tint[3])
{
	const SDL_Color *reference = palettes[pcxpal[3 - 1]];
	float now[3] = { 0, 0, 0 }, then[3] = { 0, 0, 0 };
	for (int i = 0; i < 256; ++i)
	{
		const Uint8 *c = (const Uint8 *)&colors[i];
		now[0] += c[0];
		now[1] += c[1];
		now[2] += c[2];
		then[0] += reference[i].r;
		then[1] += reference[i].g;
		then[2] += reference[i].b;
	}
	for (int k = 0; k < 3; ++k)
		tint[k] = SDL_clamp((now[k] + 1) / (then[k] + 1), 0.0f, 2.0f);
}

static void add_volume_batches(const L3DFrame *frame, int *instance_count, int *batch_count)
{
	Uint32 colors[256];
	frame_colors(frame, colors);
	const Uint32 colors_hash = hash_colors(colors);
	float tint[3];
	hd_tint(colors, tint);

	bool done[L3D_MAX_OBJECTS] = { false };
	for (int o = 0; o < frame->object_count; ++o)
	{
		const L3DObject *first = &frame->objects[o];
		if (done[o] || first->model != L3D_VOLUME)
			continue;

		VolumeSheet *entry = get_volume_sheet(first->sheet, colors, colors_hash);
		BTBHGPUCustomMesh *mesh = NULL;
		HDSheet *hd = first->filter == 0 ? get_hd_sheet(first->sheet) : NULL;
		if (hd != NULL)
			mesh = get_hd_mesh(hd, first->sprite, first->large, first->style, first->open_sides);
		if (mesh == NULL)
		{
			hd = NULL;
			mesh = entry != NULL ? get_volume_mesh(entry, first->sprite, first->large, first->style, first->open_sides) : NULL;
		}

		// All objects showing the same sprite in the same state share one batch.
		const int first_instance = *instance_count;
		for (int p = o; p < frame->object_count; ++p)
		{
			const L3DObject *object = &frame->objects[p];
			if (done[p] || object->model != L3D_VOLUME || object->sheet != first->sheet ||
			    object->sprite != first->sprite || object->large != first->large || object->style != first->style ||
			    object->filter != first->filter || object->ghost != first->ghost || object->open_sides != first->open_sides)
				continue;
			done[p] = true;
			if (mesh == NULL || *instance_count >= MAX_INSTANCES)
				continue;

			const float height = l3d_layer_height(object->layer) * rgpu_camera.height_scale + object->height +
			                     (object->layer == L3D_GROUND_ENEMY ? terrain_lift(object->x, object->y) : 0.0f);
			const Mat4 chain[] = {
				mat4_translation(object_x(object), height, object_y(object)),
				mat4_rotation(1, -object->yaw),
				mat4_rotation(2, -object->roll),
			};
			const Mat4 transform = mat4_chain((int)COUNTOF(chain), chain);
			float *instance = instances + *instance_count * 24;
			write_instance(instance, &transform, 1.0f);
			if (hd != NULL)
				memcpy(instance + 16, tint, sizeof(tint));
			++*instance_count;
		}

		const int count = *instance_count - first_instance;
		if (count == 0 || *batch_count >= MAX_BATCHES)
			continue;

		BTBHGPUSceneGeometryBatch *b = &batches[(*batch_count)++];
		init_batch(b);
		b->kind = BTBH_GPU_SCENE_GEOMETRY_CUSTOM_MESH;
		b->custom_mesh = mesh;
		b->first_instance = first_instance;
		b->instance_count = count;
		b->albedo_texture = hd != NULL ? hd->texture : filtered_volume_texture(entry, colors, colors_hash, first->filter);
		b->unlit_enabled = 1;  // shaded by the mesh's vertex colours (v3d_build_mesh)
		b->alpha_cutoff = hd != NULL ? 0.1f : 0.5f;  // HD: the mesh has the outline
		if (first->ghost)
		{
			b->transparency_enabled = 1;
			b->albedo_alpha = 128;
			b->alpha_cutoff = 0.2f;
		}
	}
}

/* --- Clouds --------------------------------------------------------------------------------------- */

/*
 * Cloud tiles (b3d_tile_is_cloud) of backgrounds 2 and 3 are soft clouds: add_background_batches
 * collects them instead of drawing them, and for each background they are drawn into a canvas at
 * half resolution, blurred into soft edges and shaded by their thickness from the light's side.
 * The canvas is drawn as two translucent slices at the background's height (some depth in
 * perspective) and once more, dark and faint, on the ground where the sun casts its shadow.
 */
typedef struct
{
	Uint8 set, tile;
	bool flipped, blended;  // blended: the game mixes these clouds half with what is below
	int layer;
	float x, z;
	const Uint32 *colors;
	int map_row, map_column;  // where in the map (the puffs' places are fixed to it)
} CloudTile;

#define MAX_CLOUD_TILES 1024
static CloudTile cloud_tiles[MAX_CLOUD_TILES];
static int cloud_tile_count = 0;
static Uint32 cloud_page_colors[4][256];  // by set: the colours its tiles are drawn in

static struct
{
	bool used, blended;
	int set, layer;
	float x0, z0;  // game pixels, the canvas's top left
	int w, h;      // texels
	// A tile of the map the canvas was made with, and where it was then and is now (the canvas is
	// remade every other tick; between, it moves with the map).
	int ref_row, ref_column;
	float ref_x, ref_z, dx, dz;
} cloud_canvases[MAX_CLOUD_CANVASES];

// Puffs: the clouds' volume, heaped on their canvases (cloud_puffs, made with each canvas).
typedef struct
{
	float x, z;        // game pixels, where the canvas was made
	float rise;        // above the clouds' layer
	float radius;      // game pixels
	float color[3];    // linear
	float alpha;
	Uint8 variant, canvas;  // variant: how the puff is turned and mirrored
} CloudPuff;

static CloudPuff cloud_puffs[MAX_CLOUD_PUFFS];
static int cloud_puff_count = 0;

static bool clouds_enabled(void)
{
	return m3d_enabled;
}

// How far each map has scrolled (game pixels, by set), so the clouds' detail stays with the map.
static float map_scroll[4];

// Smooth value noise, 0-1, with a lattice of `cell` pixels.
static float cloud_noise(float x, float z, float cell, Uint32 seed)
{
	const float fx = x / cell, fz = z / cell;
	const int ix = (int)floorf(fx), iz = (int)floorf(fz);
	float tx = fx - ix, tz = fz - iz;
	tx = tx * tx * (3 - 2 * tx);
	tz = tz * tz * (3 - 2 * tz);
	float corner[4];
	for (int k = 0; k < 4; ++k)
	{
		Uint32 h = (Uint32)(ix + (k & 1)) * 73856093u ^ (Uint32)(iz + (k >> 1)) * 19349663u ^ seed * 83492791u;
		h ^= h >> 13;
		h *= 0x5bd1e995u;
		h ^= h >> 15;
		corner[k] = (h & 0xffffu) / 65535.0f;
	}
	const float top = corner[0] + (corner[1] - corner[0]) * tx, bottom = corner[2] + (corner[3] - corner[2]) * tx;
	return top + (bottom - top) * tz;
}

// Billowing detail: a few octaves of noise.
static float cloud_billows(float x, float z)
{
	return 0.5f * cloud_noise(x, z, 26.0f, 1) + 0.3f * cloud_noise(x, z, 11.0f, 2) + 0.2f * cloud_noise(x, z, 5.0f, 3);
}

// The clouds' noise fields over a canvas, worked out every CLOUD_COARSE texels and filled in
// between (the noise is smooth at that scale; per texel it would cost a frame's time).
#define CLOUD_COARSE 4
enum { CLOUD_WARP_X, CLOUD_WARP_Z, CLOUD_ERODE, CLOUD_BILLOW };

static float cloud_field_at(int which, float x, float z)
{
	switch (which)
	{
	case CLOUD_WARP_X: return cloud_noise(x, z, 40.0f, 13);
	case CLOUD_WARP_Z: return cloud_noise(x, z, 40.0f, 14);
	case CLOUD_ERODE:  return 0.6f * cloud_noise(x, z, 34.0f, 11) + 0.4f * cloud_noise(x, z, 15.0f, 12);
	default:           return cloud_billows(x, z);
	}
}

static void cloud_field(float *out, int w, int h, float x0, float z0, int which)
{
	enum { MAX_COARSE = CLOUD_TEXELS / CLOUD_COARSE + 2 };
	static float coarse[MAX_COARSE * MAX_COARSE];
	const int gw = w / CLOUD_COARSE + 2, gh = h / CLOUD_COARSE + 2;
	for (int gy = 0; gy < gh; ++gy)
		for (int gx = 0; gx < gw; ++gx)
			coarse[gy * gw + gx] = cloud_field_at(which, x0 + (gx * CLOUD_COARSE + 0.5f) * CLOUD_SCALE,
			                                      z0 + (gy * CLOUD_COARSE + 0.5f) * CLOUD_SCALE);
	for (int y = 0; y < h; ++y)
	{
		const int gy = y / CLOUD_COARSE;
		const float ty = (y % CLOUD_COARSE) / (float)CLOUD_COARSE;
		for (int x = 0; x < w; ++x)
		{
			const int gx = x / CLOUD_COARSE;
			const float tx = (x % CLOUD_COARSE) / (float)CLOUD_COARSE;
			const float *c = &coarse[gy * gw + gx];
			const float top = c[0] + (c[1] - c[0]) * tx, bottom = c[gw] + (c[gw + 1] - c[gw]) * tx;
			out[y * w + x] = top + (bottom - top) * ty;
		}
	}
}

// A background whose cloud tiles are clouds: above the ground's objects. Light tiles that the game
// blends low over the ground (BG2_LOW: SAVARA's foam on its waves) aren't clouds: over the
// procedural water they aren't drawn (it has foam of its own).
static const L3DFrame *cloud_frame = NULL;

static bool low_background(const L3DBackground *background)
{
	return cloud_frame != NULL && cloud_frame->layers[background->layer].type == L3D_BG2_LOW;
}

// A low blended background over water that becomes procedural water (SAVARA's foam and sun
// glare on the waves): the water draws its own, so this one isn't drawn at all.
static bool water_overlay(const L3DBackground *background)
{
	Uint8 rgb[3];
	return settings3d.effects && clouds_enabled() && background->blend && low_background(background) &&
	       b3d_water_color(1, rgb);
}

static bool cloud_background(const L3DBackground *background, bool composed)
{
	return clouds_enabled() && background->set >= 2 && background->effect_count == 0 && !composed &&
	       b3d_set_has_clouds(background->set);
}

static void box_blur(float *values, float *scratch, int w, int h, int radius)
{
	for (int y = 0; y < h; ++y)  // rows
	{
		float sum = 0;
		for (int x = -radius; x <= radius; ++x)
			sum += values[y * w + SDL_clamp(x, 0, w - 1)];
		for (int x = 0; x < w; ++x)
		{
			scratch[y * w + x] = sum / (2 * radius + 1);
			sum += values[y * w + SDL_min(x + radius + 1, w - 1)] - values[y * w + SDL_max(x - radius, 0)];
		}
	}
	// Columns, a row at a time (in memory order): a running sum per column.
	static float sums[CLOUD_TEXELS];
	memset(sums, 0, sizeof(float) * (size_t)w);
	for (int y = -radius; y <= radius; ++y)
	{
		const float *row = &scratch[SDL_clamp(y, 0, h - 1) * w];
		for (int x = 0; x < w; ++x)
			sums[x] += row[x];
	}
	const float scale = 1.0f / (2 * radius + 1);
	for (int y = 0; y < h; ++y)
	{
		float *out = &values[y * w];
		const float *add = &scratch[SDL_min(y + radius + 1, h - 1) * w], *sub = &scratch[SDL_max(y - radius, 0) * w];
		for (int x = 0; x < w; ++x)
		{
			out[x] = sums[x] * scale;
			sums[x] += add[x] - sub[x];
		}
	}
}

// Draws one background's cloud tiles into canvas `c` (on the game's ticks).
static void build_cloud_canvas(int c, int set, int layer, bool blended)
{
	enum { N = CLOUD_TEXELS * CLOUD_TEXELS };
	static float cover[N], red[N], green[N], blue[N], scratch[N];
	static float sharp_cover[N], sharp_red[N], sharp_green[N], sharp_blue[N], wide[N], field_a[N], field_b[N];
	static Uint32 rgba[N];

	float x0 = 1e9f, z0 = 1e9f, x1 = -1e9f, z1 = -1e9f;
	for (int t = 0; t < cloud_tile_count; ++t)
		if (cloud_tiles[t].set == set)
		{
			x0 = SDL_min(x0, cloud_tiles[t].x);
			z0 = SDL_min(z0, cloud_tiles[t].z);
			x1 = SDL_max(x1, cloud_tiles[t].x + B3D_TILE_W);
			z1 = SDL_max(z1, cloud_tiles[t].z + B3D_TILE_H);
		}
	const int margin = 40;  // room for the soft edges and their wander (game pixels)
	x0 -= margin;
	z0 -= margin;
	x1 += margin;
	z1 += margin;
	const float size = CLOUD_TEXELS * CLOUD_SCALE;
	if (x1 - x0 > size)
	{
		const float centre = L3D_PLAYFIELD_X + L3D_PLAYFIELD_W / 2.0f;
		x0 = SDL_max(x0, centre - size / 2);
		x1 = x0 + size;
	}
	if (z1 - z0 > size)
		z0 = z1 - size;  // keep the near part
	const int w = SDL_min(CLOUD_TEXELS, (int)ceilf((x1 - x0) / CLOUD_SCALE));
	const int h = SDL_min(CLOUD_TEXELS, (int)ceilf((z1 - z0) / CLOUD_SCALE));
	cloud_canvases[c].used = true;
	cloud_canvases[c].blended = blended;
	cloud_canvases[c].set = set;
	cloud_canvases[c].layer = layer;
	cloud_canvases[c].x0 = floorf(x0);
	cloud_canvases[c].z0 = floorf(z0);
	cloud_canvases[c].w = w;
	cloud_canvases[c].h = h;
	cloud_canvases[c].dx = cloud_canvases[c].dz = 0;
	for (int t = 0; t < cloud_tile_count; ++t)
		if (cloud_tiles[t].set == set)
		{
			cloud_canvases[c].ref_row = cloud_tiles[t].map_row;
			cloud_canvases[c].ref_column = cloud_tiles[t].map_column;
			cloud_canvases[c].ref_x = cloud_tiles[t].x;
			cloud_canvases[c].ref_z = cloud_tiles[t].z;
			break;
		}
	x0 = floorf(x0);
	z0 = floorf(z0);

	memset(cover, 0, sizeof(float) * w * h);
	memset(red, 0, sizeof(float) * w * h);
	memset(green, 0, sizeof(float) * w * h);
	memset(blue, 0, sizeof(float) * w * h);
	for (int t = 0; t < cloud_tile_count; ++t)
	{
		const CloudTile *tile = &cloud_tiles[t];
		const Uint8 *data = tile->set == set ? b3d_tile_pixels(tile->set, tile->tile) : NULL;
		if (data == NULL)
			continue;
		for (int y = 0; y < B3D_TILE_H; ++y)
		{
			const int ty = (int)(tile->z + y - z0) / CLOUD_SCALE;
			if (ty < 0 || ty >= h)
				continue;
			for (int x = 0; x < B3D_TILE_W; ++x)
			{
				const Uint8 value = data[y * B3D_TILE_W + (tile->flipped ? B3D_TILE_W - 1 - x : x)];
				const int tx = (int)(tile->x + x - x0) / CLOUD_SCALE;
				if (value == 0 || tx < 0 || tx >= w)
					continue;
				const Uint8 *color = (const Uint8 *)&tile->colors[value];
				const int i = ty * w + tx;
				cover[i] += 1.0f / (CLOUD_SCALE * CLOUD_SCALE);
				red[i] += color[0];
				green[i] += color[1];
				blue[i] += color[2];
			}
		}
	}
	// Soft edges: the cover blurred (about a gaussian); colours blurred by cover, so that the edges
	// take their neighbours' colours.
	for (int i = 0; i < w * h; ++i)
	{
		const float n = cover[i] * CLOUD_SCALE * CLOUD_SCALE;
		if (n > 0)
		{
			red[i] = red[i] / n * cover[i];
			green[i] = green[i] / n * cover[i];
			blue[i] = blue[i] / n * cover[i];
		}
	}
	// The cloud's own texture, lightly softened, inside; widely blurred colours at the soft edges.
	memcpy(sharp_cover, cover, sizeof(float) * w * h);
	memcpy(sharp_red, red, sizeof(float) * w * h);
	memcpy(sharp_green, green, sizeof(float) * w * h);
	memcpy(sharp_blue, blue, sizeof(float) * w * h);
	box_blur(sharp_cover, scratch, w, h, 1);
	box_blur(sharp_red, scratch, w, h, 1);
	box_blur(sharp_green, scratch, w, h, 1);
	box_blur(sharp_blue, scratch, w, h, 1);
	for (int pass = 0; pass < 2; ++pass)
	{
		box_blur(red, scratch, w, h, 2);
		box_blur(green, scratch, w, h, 2);
		box_blur(blue, scratch, w, h, 2);
		box_blur(cover, scratch, w, h, 2);
	}
	// How deep inside the cloud: its cover blurred widely. The edges (where it is low) are eaten
	// away by large noise, so that clouds don't keep the tiles' straight borders.
	// (Blurred at a quarter of the resolution: it is wide and smooth.)
	{
		enum { Q = 4 };
		const int qw = (w + Q - 1) / Q, qh = (h + Q - 1) / Q;
		static float small[(CLOUD_TEXELS / Q + 1) * (CLOUD_TEXELS / Q + 1)], small_scratch[(CLOUD_TEXELS / Q + 1) * (CLOUD_TEXELS / Q + 1)];
		for (int qy = 0; qy < qh; ++qy)
			for (int qx = 0; qx < qw; ++qx)
			{
				float sum = 0;
				int n = 0;
				for (int y = qy * Q; y < SDL_min(qy * Q + Q, h); ++y)
					for (int x = qx * Q; x < SDL_min(qx * Q + Q, w); ++x, ++n)
						sum += cover[y * w + x];
				small[qy * qw + qx] = n ? sum / n : 0;
			}
		for (int pass = 0; pass < 3; ++pass)
			box_blur(small, small_scratch, qw, qh, 1);
		for (int y = 0; y < h; ++y)
		{
			const float fy = SDL_clamp((y + 0.5f) / Q - 0.5f, 0.0f, (float)(qh - 1));
			const int y0 = (int)fy, y1 = SDL_min(y0 + 1, qh - 1);
			const float ty = fy - y0;
			for (int x = 0; x < w; ++x)
			{
				const float fx = SDL_clamp((x + 0.5f) / Q - 0.5f, 0.0f, (float)(qw - 1));
				const int x0i = (int)fx, x1 = SDL_min(x0i + 1, qw - 1);
				const float tx = fx - x0i;
				const float top = small[y0 * qw + x0i] + (small[y0 * qw + x1] - small[y0 * qw + x0i]) * tx;
				const float bottom = small[y1 * qw + x0i] + (small[y1 * qw + x1] - small[y1 * qw + x0i]) * tx;
				wide[y * w + x] = top + (bottom - top) * ty;
			}
		}
	}
	// The edges wander too: the cover is looked up a little way off, by noise (up to 12 texels).
	memcpy(scratch, cover, sizeof(float) * w * h);
	const float map_z0 = z0 - map_scroll[set & 3];
	cloud_field(field_a, w, h, x0, map_z0, CLOUD_WARP_X);
	cloud_field(field_b, w, h, x0, map_z0, CLOUD_WARP_Z);
	for (int i = 0; i < w * h; ++i)
	{
		const int wx = (int)lroundf((field_a[i] - 0.5f) * 48.0f / CLOUD_SCALE);
		const int wz = (int)lroundf((field_b[i] - 0.5f) * 48.0f / CLOUD_SCALE);
		const int sx = SDL_clamp(i % w + wx, 0, w - 1), sz = SDL_clamp(i / w + wz, 0, h - 1);
		cover[i] = scratch[sz * w + sx];
	}
	cloud_field(field_a, w, h, x0, map_z0, CLOUD_ERODE);
	cloud_field(field_b, w, h, x0 + glint_time * 3.0f, map_z0, CLOUD_BILLOW);
	for (int i = 0; i < w * h; ++i)
	{
		const float erode = field_a[i];
		cover[i] = SDL_max(0.0f, cover[i] - 0.7f * erode * (1 - SDL_min(1.0f, wide[i])) * SDL_min(1.0f, cover[i] * 3));
		// Nothing at the canvas's edges (where a cloud the canvas cuts off would end in a line).
		const int edge = SDL_min(SDL_min(i % w, w - 1 - i % w), SDL_min(i / w, h - 1 - i / w));
		cover[i] *= SDL_clamp(edge / 6.0f, 0.0f, 1.0f);
	}
	for (int y = 0; y < h; ++y)
		for (int x = 0; x < w; ++x)
		{
			const int i = y * w + x;
			const float thickness = cover[i];
			if (thickness < 0.02f)
			{
				rgba[i] = 0;
				continue;
			}
			// Billows: thicker and thinner patches that drift slowly with the wind, fixed to the map.
			const float billow = field_b[i];
			// Lit from the upper left: brighter where the cloud thins towards the light, darker on the
			// far side; thin parts let more of the ground through.
			const float towards = cover[SDL_max(y - 3, 0) * w + SDL_max(x - 3, 0)];
			const float away = cover[SDL_min(y + 3, h - 1) * w + SDL_min(x + 3, w - 1)];
			const float shade = SDL_clamp(1.0f + 1.8f * (away - towards), 0.68f, 1.25f) * (0.8f + 0.4f * billow);
			const float t = SDL_clamp((thickness * (0.55f + 0.9f * billow) - 0.06f) / 0.55f, 0.0f, 1.0f);
			const float alpha = t * t * (3 - 2 * t) * 0.85f;
			Uint8 *out = (Uint8 *)&rgba[i];
			float base[3] = { red[i] / thickness, green[i] / thickness, blue[i] / thickness };
			if (sharp_cover[i] > 0.15f)
			{
				const float k = SDL_min(1.0f, (sharp_cover[i] - 0.15f) / 0.3f);
				base[0] += (sharp_red[i] / sharp_cover[i] - base[0]) * k;
				base[1] += (sharp_green[i] / sharp_cover[i] - base[1]) * k;
				base[2] += (sharp_blue[i] / sharp_cover[i] - base[2]) * k;
			}
			for (int k = 0; k < 3; ++k)
			{
				const float whiter = base[k] + (255.0f - base[k]) * 0.3f;  // clouds whiter than the tiles
				out[k] = (Uint8)SDL_clamp(whiter * shade, 0.0f, 255.0f);
			}
			out[3] = (Uint8)(alpha * 255.0f);
		}
	btbh_gpu_texture_update_rgba8(cloud_texture, (const uint8_t *)rgba, 0, c * CLOUD_TEXELS, w, h);

	// Puffs where the cloud is thick, at places fixed to the map: a few per tile, jittered, heaped
	// highest in the middle of the cloud (`wide`), small and sparse at its edges.
	for (int t = 0; t < cloud_tile_count; ++t)
	{
		const CloudTile *tile = &cloud_tiles[t];
		if (tile->set != set)
			continue;
		for (int k = 0; k < 4 && cloud_puff_count < MAX_CLOUD_PUFFS; ++k)
		{
			Uint32 hash = (Uint32)tile->map_row * 73856093u ^ (Uint32)tile->map_column * 19349663u ^ (Uint32)(k + 1) * 83492791u ^
			              (Uint32)set * 2654435761u;
			hash ^= hash >> 13;
			hash *= 0x5bd1e995u;
			hash ^= hash >> 15;
			const float jx = (hash & 0xff) / 255.0f, jz = (hash >> 8 & 0xff) / 255.0f, jr = (hash >> 16 & 0xff) / 255.0f;
			const float px = tile->x + ((k % 2) + jx) * (B3D_TILE_W / 2.0f), pz = tile->z + ((k / 2) + jz) * (B3D_TILE_H / 2.0f);
			const int tx = (int)((px - x0) / CLOUD_SCALE), tz = (int)((pz - z0) / CLOUD_SCALE);
			if (tx < 0 || tx >= w || tz < 0 || tz >= h)
				continue;
			const int i = tz * w + tx;
			const float thickness = cover[i], heap = SDL_min(1.0f, wide[i]);
			// Ragged edges: where the cloud thins, only some places get a puff.
			const float edge_noise = cloud_noise(px, pz - map_scroll[set & 3], 19.0f, 5);
			if (thickness < 0.35f + 0.35f * edge_noise * (1 - heap))
				continue;
			CloudPuff *puff = &cloud_puffs[cloud_puff_count++];
			puff->x = px;
			puff->z = pz;
			puff->rise = 1.0f + 15.0f * heap * heap + 2.5f * jr;
			puff->radius = 5.0f + 11.0f * heap + 3.0f * jr;
			for (int ch = 0; ch < 3; ++ch)
			{
				const float value = (ch == 0 ? red[i] : ch == 1 ? green[i] : blue[i]) / thickness;
				puff->color[ch] = srgb_to_linear((Uint8)SDL_clamp(value + (255.0f - value) * 0.45f, 0.0f, 255.0f));
			}
			puff->alpha = SDL_clamp((thickness - 0.35f) * 2.0f, 0.0f, 1.0f) * (0.55f + 0.45f * heap) * (blended ? 0.5f : 0.7f);
			// Lower puffs a little greyer: the clouds' undersides.
			for (int ch = 0; ch < 3; ++ch)
				puff->color[ch] *= 0.82f + 0.18f * SDL_min(1.0f, puff->rise / 12.0f);
			puff->variant = (Uint8)(hash >> 24 & 15);
			puff->canvas = (Uint8)c;
		}
	}

	// A clear texel beyond the canvas's right and bottom edges, so filtering there fades out.
	static Uint32 clear[CLOUD_TEXELS + 1];
	if (w < CLOUD_TEXELS)
		btbh_gpu_texture_update_rgba8(cloud_texture, (const uint8_t *)clear, w, c * CLOUD_TEXELS, 1, SDL_min(h + 1, CLOUD_TEXELS));
	if (h < CLOUD_TEXELS)
		btbh_gpu_texture_update_rgba8(cloud_texture, (const uint8_t *)clear, 0, c * CLOUD_TEXELS + h, SDL_min(w + 1, CLOUD_TEXELS), 1);
	if (SDL_getenv("TYR3D_LOG_CLOUDS") != NULL)
		printf("clouds: canvas %d set %d layer %d at %.0f,%.0f, %dx%d texels (frame %u)\n", c, set, layer, x0, z0, w, h,
		       l3d_frame_number);
}

static void add_cloud_quad(int c, float height, float x_shift, float z_shift, float shade, float alpha, int *instance_count,
                           int *batch_count)
{
	if (*instance_count >= MAX_INSTANCES || *batch_count >= MAX_BATCHES)
		return;
	const float speed = background_speed[cloud_canvases[c].set & 3] * ahead;
	Mat4 transform = mat4_identity();
	transform.m[0] = (float)(cloud_canvases[c].w * CLOUD_SCALE);
	transform.m[10] = (float)(cloud_canvases[c].h * CLOUD_SCALE);
	transform.m[12] = cloud_canvases[c].x0 + cloud_canvases[c].dx + x_shift;
	transform.m[13] = height;
	transform.m[14] = cloud_canvases[c].z0 + cloud_canvases[c].dz + z_shift + speed;
	float *instance = instances + *instance_count * 24;
	write_instance(instance, &transform, shade);
	instance[19] = alpha;

	BTBHGPUSceneGeometryBatch *b = &batches[(*batch_count)++];
	init_batch(b);
	b->kind = BTBH_GPU_SCENE_GEOMETRY_CUSTOM_MESH;
	b->custom_mesh = quad_mesh;
	b->first_instance = (*instance_count)++;
	b->instance_count = 1;
	b->albedo_texture = cloud_texture;
	b->uv_scale_x = (float)cloud_canvases[c].w / CLOUD_TEXELS;
	b->uv_scale_y = (float)cloud_canvases[c].h / (CLOUD_TEXELS * MAX_CLOUD_CANVASES);
	b->uv_offset_y = (float)c / MAX_CLOUD_CANVASES;
	b->unlit_enabled = 1;
	b->transparency_enabled = 1;
	b->blend_mode = BTBH_GPU_SCENE_BLEND_ALPHA;
}

static float srgb_to_linear(Uint8 value);

// The puffs, farthest first (they are blended), as billboards facing the camera.
static void add_cloud_puffs(const float *heights, const Camera3D *camera, int *instance_count, int *batch_count)
{
	if (cloud_puff_count == 0 || *batch_count >= MAX_BATCHES)
		return;
	static float depth[MAX_CLOUD_PUFFS];
	static int order[MAX_CLOUD_PUFFS];
	static float position[MAX_CLOUD_PUFFS][3];
	for (int i = 0; i < cloud_puff_count; ++i)
	{
		const CloudPuff *puff = &cloud_puffs[i];
		const float speed = background_speed[cloud_canvases[puff->canvas].set & 3] * ahead;
		// Drifting a little with the wind, bobbing slowly.
		position[i][0] = puff->x + cloud_canvases[puff->canvas].dx + sinf(glint_time * 0.4f + puff->z * 0.05f) * 1.2f;
		position[i][1] = heights[cloud_canvases[puff->canvas].layer] + puff->rise;
		// Under background 3's solids (drawn over the clouds), the puffs stay below their tops.
		if (cloud_canvases[puff->canvas].set == 2 && frame_terrains[3] != NULL)
			position[i][1] = SDL_min(position[i][1], solid_top(3) - 1.5f - puff->radius * 0.5f);
		position[i][2] = puff->z + cloud_canvases[puff->canvas].dz + speed;
		const float d[3] = { position[i][0] - camera->position[0], position[i][1] - camera->position[1],
		                     position[i][2] - camera->position[2] };
		depth[i] = d[0] * camera->forward[0] + d[1] * camera->forward[1] + d[2] * camera->forward[2];
		order[i] = i;
	}
	// Farthest first (insertion sort: the order changes little from frame to frame).
	for (int i = 1; i < cloud_puff_count; ++i)
	{
		const int o = order[i];
		int j = i - 1;
		while (j >= 0 && depth[order[j]] < depth[o])
		{
			order[j + 1] = order[j];
			--j;
		}
		order[j + 1] = o;
	}
	const int first = *instance_count;
	for (int n = 0; n < cloud_puff_count && *instance_count < MAX_INSTANCES; ++n)
	{
		const CloudPuff *puff = &cloud_puffs[order[n]];
		// Turned a little, mirrored or not, wider than tall.
		const float angle = ((puff->variant & 7) - 3.5f) * 0.09f;
		const float sx = puff->radius * 2.3f * ((puff->variant & 8) ? -1.0f : 1.0f), sy = puff->radius * 1.8f;
		Mat4 transform = mat4_identity();
		transform.m[0] = sx * cosf(angle);
		transform.m[1] = sx * sinf(angle);
		transform.m[4] = -sy * sinf(angle);
		transform.m[5] = sy * cosf(angle);
		transform.m[10] = puff->radius * 2;
		transform.m[12] = position[order[n]][0];
		transform.m[13] = position[order[n]][1];
		transform.m[14] = position[order[n]][2];
		float *instance = instances + *instance_count * 24;
		write_instance(instance, &transform, 1.0f);
		instance[16] = puff->color[0];
		instance[17] = puff->color[1];
		instance[18] = puff->color[2];
		instance[19] = puff->alpha;
		++*instance_count;
	}
	BTBHGPUSceneGeometryBatch *b = &batches[(*batch_count)++];
	init_batch(b);
	b->kind = BTBH_GPU_SCENE_GEOMETRY_CUSTOM_MESH;
	b->custom_mesh = billboard_mesh;
	b->first_instance = first;
	b->instance_count = *instance_count - first;
	b->albedo_texture = puff_texture;
	b->billboard_mode = BTBH_GPU_SCENE_BILLBOARD_FRONT;
	b->unlit_enabled = 1;
	b->transparency_enabled = 1;
	b->blend_mode = BTBH_GPU_SCENE_BLEND_ALPHA;
}

static void add_cloud_batches(const float *heights, const Camera3D *camera, bool new_frame, int *instance_count,
                              int *batch_count)
{
	// On every other tick the canvases of the tick before move with their maps instead of being
	// made again (it takes milliseconds), unless a canvas's map tile is gone or its background changed.
	static unsigned int cloud_ticks = 0;
	bool rebuild = new_frame && (++cloud_ticks & 1) == 0;
	if (new_frame && !rebuild)
	{
		bool seen[4] = { false };
		for (int t = 0; t < cloud_tile_count; ++t)
			seen[cloud_tiles[t].set & 3] = true;
		for (int c = 0; c < MAX_CLOUD_CANVASES && !rebuild; ++c)
		{
			if (!cloud_canvases[c].used)
				continue;
			bool found = false;
			for (int t = 0; t < cloud_tile_count && !found; ++t)
				if (cloud_tiles[t].set == cloud_canvases[c].set && cloud_tiles[t].map_row == cloud_canvases[c].ref_row &&
				    cloud_tiles[t].map_column == cloud_canvases[c].ref_column && cloud_tiles[t].layer == cloud_canvases[c].layer)
				{
					found = true;
					cloud_canvases[c].dx = cloud_tiles[t].x - cloud_canvases[c].ref_x;
					cloud_canvases[c].dz = cloud_tiles[t].z - cloud_canvases[c].ref_z;
				}
			rebuild = !found;
			seen[cloud_canvases[c].set & 3] = false;
		}
		for (int set = 0; set < 4; ++set)
			rebuild |= seen[set];  // a background with clouds and no canvas
	}
	if (rebuild)
	{
		cloud_puff_count = 0;
		for (int c = 0; c < MAX_CLOUD_CANVASES; ++c)
			cloud_canvases[c].used = false;
		int canvases = 0;
		for (int t = 0; t < cloud_tile_count && canvases < MAX_CLOUD_CANVASES; ++t)
		{
			bool done = false;
			for (int c = 0; c < canvases; ++c)
				done |= cloud_canvases[c].set == cloud_tiles[t].set;
			if (!done)
			{
				const Uint64 start = SDL_GetTicksNS();
				build_cloud_canvas(canvases, cloud_tiles[t].set, cloud_tiles[t].layer, cloud_tiles[t].blended);
				if (SDL_getenv("TYR3D_PROFILE") != NULL)
				{
					static Uint64 total = 0;
					static int count = 0;
					total += SDL_GetTicksNS() - start;
					if (++count % 175 == 0)
						printf("clouds: a canvas takes %.2f ms\n", total / 175 / 1e6);
					if (count % 175 == 0)
						total = 0;
				}
				++canvases;
			}
		}
	}

	const float length = sqrtf(sun_direction[0] * sun_direction[0] + sun_direction[1] * sun_direction[1] +
	                           sun_direction[2] * sun_direction[2]);
	const float sun[3] = { sun_direction[0] / length, sun_direction[1] / length, sun_direction[2] / length };
	for (int c = 0; c < MAX_CLOUD_CANVASES; ++c)
	{
		if (!cloud_canvases[c].used)
			continue;
		const float height = heights[cloud_canvases[c].layer];
		// The shadow on the ground, where the sun's light through the cloud lands.
		const float ground = heights[0] + 0.15f, drop = height - ground + 30.0f;  // clouds float higher than their layer
		add_cloud_quad(c, ground, sun[0] * drop / -sun[1], sun[2] * drop / -sun[1], 0.0f, cloud_canvases[c].blended ? 0.22f : 0.3f,
		               instance_count, batch_count);
		// The cloud: two slices, a little apart, for some depth; clouds the game blends with what is
		// below let about half of it through.
		const float opacity = cloud_canvases[c].blended ? 0.42f : 0.7f;
		add_cloud_quad(c, height - 1.5f, 0, 0, 0.94f, opacity, instance_count, batch_count);
		add_cloud_quad(c, height + 1.5f, 0, 0, 1.0f, opacity, instance_count, batch_count);
	}
	// Their volume: puffs heaped on them.
	add_cloud_puffs(heights, camera, instance_count, batch_count);
}

/* --- Terrain relief --------------------------------------------------------------------------- */

/*
 * The ground as terrain (polish): background 1's tiles are heightfields instead of flat quads,
 * their height from the pixels' brightness (light ground high, dark crevices low), shaded by the
 * sun into their vertex colours (faces up keep the pixels' colours) and with skirts down to the
 * tile's base where neighbours don't meet. The tiles then show everything of background 1, inside
 * the playfield too (its captured layer isn't drawn). Water stays flat (procedural water); levels
 * with filters, the starfield or other specials keep the flat ground. TYR3D_RELIEF=<height> sets
 * the relief's height (0 off).
 */
#define RELIEF_GRID_W B3D_TILE_W  // vertices per tile row, minus one
#define RELIEF_GRID_H B3D_TILE_H

static BTBHGPUCustomMesh *relief_meshes[B3D_CELLS];
static bool relief_built[B3D_CELLS];
static unsigned int relief_generation = ~0u;

static float relief_height(void)
{
	static float height = -1;
	if (height < 0)
		height = SDL_getenv("TYR3D_RELIEF") != NULL ? (float)SDL_atof(SDL_getenv("TYR3D_RELIEF")) : 8.0f;
	return height;
}

// Whether a frame's ground is shown as terrain: background 1 not composed (filters), no starfield.
static bool relief_frame(const L3DFrame *frame, const bool *composed)
{
	if (!m3d_enabled || relief_height() <= 0 || frame->star_count > 0)
		return false;
	for (int i = 0; i < frame->background_count; ++i)
		if (frame->backgrounds[i].set == 1)
			return !composed[i] && frame->backgrounds[i].effect_count == 0;
	return false;
}

static BTBHGPUCustomMesh *relief_mesh(int cell)
{
	if (relief_generation != b3d_map_generation)
	{
		for (int c = 0; c < B3D_CELLS; ++c)
		{
			if (relief_meshes[c] != NULL)
				btbh_gpu_custom_mesh_destroy(relief_meshes[c]);
			relief_meshes[c] = NULL;
			relief_built[c] = false;
		}
		relief_generation = b3d_map_generation;
	}
	if (cell < 0 || cell >= B3D_CELLS)
		return NULL;
	if (relief_built[cell])
		return relief_meshes[cell];
	relief_built[cell] = true;

	const int set = cell / B3D_TILES_PER_SET + 1, tile = cell % B3D_TILES_PER_SET;
	const Uint8 *data = b3d_tile_pixels(set, tile);
	if (data == NULL || b3d_tile_is_water(set, tile))
		return NULL;
	// Tiles with holes (space showing through) stay flat: their edges would be jagged cliffs.
	for (int i = 0; i < B3D_TILE_W * B3D_TILE_H; ++i)
		if (data[i] == 0)
			return NULL;

	// Brightness, softened, per pixel; heights at the pixels' corners.
	enum { W = B3D_TILE_W, H = B3D_TILE_H };
	static float lum[W * H], soft[W * H], corner[(W + 1) * (H + 1)];
	for (int i = 0; i < W * H; ++i)
	{
		const Uint8 *c = (const Uint8 *)&rgb_palette[data[i]];
		lum[i] = data[i] == 0 ? 0.0f : (0.299f * c[0] + 0.587f * c[1] + 0.114f * c[2]) / 255.0f;
	}
	for (int y = 0; y < H; ++y)
		for (int x = 0; x < W; ++x)
		{
			float sum = 0, weight = 0;
			for (int dy = -1; dy <= 1; ++dy)
				for (int dx = -1; dx <= 1; ++dx)
				{
					const int sx = SDL_clamp(x + dx, 0, W - 1), sy = SDL_clamp(y + dy, 0, H - 1);
					const float w = (dx == 0 && dy == 0) ? 4.0f : (dx == 0 || dy == 0) ? 2.0f : 1.0f;
					sum += lum[sy * W + sx] * w;
					weight += w;
				}
			soft[y * W + x] = sum / weight;
		}
	const float scale = relief_height();
	for (int y = 0; y <= H; ++y)
		for (int x = 0; x <= W; ++x)
		{
			float sum = 0;
			int n = 0;
			for (int dy = -1; dy <= 0; ++dy)
				for (int dx = -1; dx <= 0; ++dx)
				{
					const int sx = x + dx, sy = y + dy;
					if (sx >= 0 && sx < W && sy >= 0 && sy < H)
					{
						sum += soft[sy * W + sx];
						++n;
					}
				}
			// Carved down from the ground's plane, so what stands on the ground stays on top.
			corner[y * (W + 1) + x] = scale * ((n > 0 ? sum / n : 0.0f) - 1.0f);
		}

	const float length = sqrtf(sun_direction[0] * sun_direction[0] + sun_direction[1] * sun_direction[1] +
	                           sun_direction[2] * sun_direction[2]);
	const float light[3] = { -sun_direction[0] / length, -sun_direction[1] / length, -sun_direction[2] / length };
	const float up = SDL_max(light[1], 0.0f);
	#define RELIEF_FILL 0.5f

	// The grid (unit square in x and z; heights in game pixels), then skirts along the four sides.
	static V3DVertex vertices[(W + 1) * (H + 1) + 4 * 2 * (W + H + 2)];
	static Uint32 indices[W * H * 6 + 4 * 6 * (W + H)];
	int vc = 0, ic = 0;
	for (int y = 0; y <= H; ++y)
		for (int x = 0; x <= W; ++x)
		{
			const float hl = corner[y * (W + 1) + SDL_max(x - 1, 0)], hr = corner[y * (W + 1) + SDL_min(x + 1, W)];
			const float hu = corner[SDL_max(y - 1, 0) * (W + 1) + x], hd = corner[SDL_min(y + 1, H) * (W + 1) + x];
			float n[3] = { -(hr - hl) / (float)(SDL_min(x + 1, W) - SDL_max(x - 1, 0)), 1.0f,
			               -(hd - hu) / (float)(SDL_min(y + 1, H) - SDL_max(y - 1, 0)) };
			const float nl = sqrtf(n[0] * n[0] + n[1] * n[1] + n[2] * n[2]);
			for (int k = 0; k < 3; ++k)
				n[k] /= nl;
			const float lambert = n[0] * light[0] + n[1] * light[1] + n[2] * light[2];
			const float shade = (RELIEF_FILL + (1 - RELIEF_FILL) * SDL_max(lambert, 0.0f)) / (RELIEF_FILL + (1 - RELIEF_FILL) * up);
			V3DVertex *v = &vertices[vc++];
			memset(v, 0, sizeof(*v));
			v->position[0] = (float)x / W;
			v->position[1] = corner[y * (W + 1) + x];
			v->position[2] = (float)y / H;
			memcpy(v->normal, n, sizeof(n));
			v->uv[0] = (float)x / W;
			v->uv[1] = (float)y / H;
			v->tangent[0] = 1;
			v->tangent[3] = 1;
			v->color[0] = v->color[1] = v->color[2] = shade;
			v->color[3] = 1;
		}
	for (int y = 0; y < H; ++y)
		for (int x = 0; x < W; ++x)
		{
			const Uint32 a = y * (W + 1) + x, b = a + 1, c = a + W + 2, d = a + W + 1;
			indices[ic++] = a;
			indices[ic++] = b;
			indices[ic++] = c;
			indices[ic++] = a;
			indices[ic++] = c;
			indices[ic++] = d;
		}
	// Skirts: each side's edge down to the base, a little darker.
	for (int side = 0; side < 4; ++side)
	{
		const int count = side % 2 == 0 ? W : H;
		const Uint32 base = (Uint32)vc;
		for (int i = 0; i <= count; ++i)
		{
			int x, y;
			switch (side)
			{
			case 0:  x = i;     y = 0;     break;  // top
			case 1:  x = W;     y = i;     break;  // right
			case 2:  x = W - i; y = H;     break;  // bottom
			default: x = 0;     y = H - i; break;  // left
			}
			for (int level = 0; level < 2; ++level)
			{
				V3DVertex *v = &vertices[vc++];
				*v = vertices[y * (W + 1) + x];
				if (level == 1)
					v->position[1] = -scale;
				v->color[0] = v->color[1] = v->color[2] = vertices[y * (W + 1) + x].color[0] * 0.7f;
			}
		}
		for (int i = 0; i < count; ++i)
		{
			const Uint32 top0 = base + i * 2, bottom0 = top0 + 1, top1 = top0 + 2, bottom1 = top0 + 3;
			indices[ic++] = top0;
			indices[ic++] = bottom0;
			indices[ic++] = top1;
			indices[ic++] = top1;
			indices[ic++] = bottom0;
			indices[ic++] = bottom1;
		}
	}
	#undef RELIEF_FILL

	BTBHGPUCustomMeshReport report;
	relief_meshes[cell] = btbh_gpu_window_custom_mesh_create(window, vertices, (uint32_t)(vc * sizeof(V3DVertex)),
	                                                         (uint32_t)vc, indices, (uint32_t)ic, &report);
	if (relief_meshes[cell] == NULL)
		fprintf(stderr, "warning: terrain mesh: %s\n", report.message);
	return relief_meshes[cell];
}

/* --- Terrain ------------------------------------------------------------------------------------ */

/*
 * Terrain from assets (b3d_terrain): the ground map's rows as meshes on the precomputed heights,
 * a vertex every sample (2 game pixels), each tile textured with its atlas cell (water keeps the
 * procedural water), shaded by the sun and the terrain's hollows into the vertex colours, and
 * casting shadows. The layers above the ground's enemies move up by TERRAIN_HEADROOM, so raised
 * ground stays under the air.
 */
#define TERRAIN_HEADROOM 36.0f
#define TERRAIN_ROWS_CACHED 192
// How far the ground's walls go down where it has holes (black space).
#define TERRAIN_HOLE_DEPTH 21.0f
// Samples in from a surface's edge that its walls take their colours from.
#define TERRAIN_WALL_INSET 3
// Map rows a terrain texture holds (terrain_ring), more than are ever drawn at once.
#define TERRAIN_RING_ROWS 80

static struct
{
	int set, map_row;
	float hole_depth;
	unsigned int generation;  // b3d_map_generation + 1, or 0 for a free slot
	Uint32 used;
	BTBHGPUCustomMesh *mesh;
} terrain_rows[TERRAIN_ROWS_CACHED];
static Uint32 terrain_clock = 0;
static bool terrain_batch[MAX_BATCHES];  // batches of terrain (they cast shadows)

static bool terrain_background(const L3DFrame *frame, const L3DBackground *background)
{
	// Backgrounds 2 and 3 as solids only when drawn over the ground's enemies (under them, a
	// solid would bury them); solid, they aren't blended.
	if (background->set < 1 || background->set > B3D_SETS || frame_terrains[background->set] == NULL)
		return false;
	return background->set == 1 || frame->layers[background->layer].type != L3D_BG2_LOW;
}

// Solids stand below what flies (sky enemies and above) so nothing flies through them: background 3's
// a little below the sky enemies (in the game it is drawn over them, or over the player), background
// 2's lower still.
#define SOLID_BELOW_AIR 6.0f
#define SOLID_BG2_BELOW_BG3 12.0f

// How high solids stand, as a share of the room below what flies (the user found them too deep at
// full height).
#define SOLID_EXTRUDE 0.4f

static float solid_top(int set)
{
	const float top = l3d_layer_height(L3D_SKY_ENEMY) * rgpu_camera.height_scale - SOLID_BELOW_AIR;
	return SOLID_EXTRUDE * (set == 3 ? top : top - SOLID_BG2_BELOW_BG3);
}

static const L3DBackground *lift_ground = NULL;  // this frame's ground when it is terrain (present_3d)

// What stands on the ground (its enemies, their explosions) stands on the terrain: the terrain's
// height at a game position, 0 over a hole or off the map. Their game positions stay as they are
// (aligned scales by height).
static float terrain_lift(float x, float y)
{
	const B3DTerrain *t = frame_terrains[1];
	int mx, my;
	if (t == NULL || lift_ground == NULL || !b3d_map_point(lift_ground, x, y, &mx, &my))
		return 0.0f;
	const float fx = mx / (float)t->sample, fy = my / (float)t->sample;
	const int sx = (int)floorf(fx), sy = (int)floorf(fy);
	float h[4];
	for (int k = 0; k < 4; ++k)
	{
		const int ix = SDL_clamp(sx + (k & 1), 0, t->width - 1), iy = SDL_clamp(sy + (k >> 1), 0, t->height - 1);
		const Sint8 value = t->heights[iy * t->width + ix];
		h[k] = t->holes && value == B3D_TERRAIN_HOLE ? 0.0f : value;
	}
	const float ax = fx - sx, ay = fy - sy;
	return (h[0] * (1 - ax) + h[1] * ax) * (1 - ay) + (h[2] * (1 - ax) + h[3] * ax) * ay;
}

static bool terrain_hole(const B3DTerrain *t, int sx, int sy)
{
	sx = SDL_clamp(sx, 0, t->width - 1);
	sy = SDL_clamp(sy, 0, t->height - 1);
	return t->holes && t->heights[sy * t->width + sx] == B3D_TERRAIN_HOLE;
}

static float terrain_height(const B3DTerrain *t, int sx, int sy, float hole_depth)
{
	sx = SDL_clamp(sx, 0, t->width - 1);
	sy = SDL_clamp(sy, 0, t->height - 1);
	const Sint8 h = t->heights[sy * t->width + sx];
	return t->holes && h == B3D_TERRAIN_HOLE ? -hole_depth : (float)h;
}

static BTBHGPUCustomMesh *build_terrain_row(const B3DTerrain *t, int set, int map_row, float hole_depth)
{
	const int per_x = B3D_TILE_W / t->sample, per_y = B3D_TILE_H / t->sample;  // samples a tile
	const int columns = (t->width - 1) / per_x;
	const int vertices_per_tile = (per_x + 1) * (per_y + 1);
	const int max_vertices = columns * vertices_per_tile;
	static V3DVertex *vertices = NULL;
	static Uint32 *indices = NULL;
	static int capacity = 0;
	if (capacity < max_vertices)
	{
		free(vertices);
		free(indices);
		vertices = malloc(sizeof(V3DVertex) * (size_t)max_vertices);
		indices = malloc(sizeof(Uint32) * (size_t)columns * per_x * per_y * 6);
		capacity = vertices != NULL && indices != NULL ? max_vertices : 0;
		if (capacity == 0)
			return NULL;
	}

	const float length = sqrtf(sun_direction[0] * sun_direction[0] + sun_direction[1] * sun_direction[1] +
	                           sun_direction[2] * sun_direction[2]);
	const float light[3] = { -sun_direction[0] / length, -sun_direction[1] / length, -sun_direction[2] / length };
	const float up = SDL_max(light[1], 0.0f);
	int vc = 0, ic = 0;
	for (int c = 0; c < columns; ++c)
	{
		bool flipped;
		if (b3d_map_cell(set, map_row, c - t->side_columns, &flipped) < 0)
			continue;
		const Uint32 base = (Uint32)vc;
		bool any_surface = false;
		for (int j = 0; j <= per_y; ++j)
			for (int i = 0; i <= per_x; ++i)
			{
				const int sx = c * per_x + i, sy = map_row * per_y + j;
				const float h = terrain_height(t, sx, sy, hole_depth);
				float n[3] = { -(terrain_height(t, sx + 1, sy, hole_depth) - terrain_height(t, sx - 1, sy, hole_depth)) /
				                   (2.0f * t->sample),
				               1.0f,
				               -(terrain_height(t, sx, sy + 1, hole_depth) - terrain_height(t, sx, sy - 1, hole_depth)) /
				                   (2.0f * t->sample) };
				const float nl = sqrtf(n[0] * n[0] + n[1] * n[1] + n[2] * n[2]);
				for (int k = 0; k < 3; ++k)
					n[k] /= nl;
				// Hollows darker: how far the ground round about stands above this point.
				float around = 0;
				for (int k = 0; k < 8; ++k)
				{
					static const int dx[8] = { 4, -4, 0, 0, 3, -3, 3, -3 }, dy[8] = { 0, 0, 4, -4, 3, 3, -3, -3 };
					around += terrain_height(t, sx + dx[k], sy + dy[k], hole_depth);
				}
				const float hollow = SDL_clamp((around / 8 - h) / 24.0f, 0.0f, 0.4f);
				const float lambert = n[0] * light[0] + n[1] * light[1] + n[2] * light[2];
				// Deeper is darker: walls fade into the depths.
				const float deep = h < 0 ? SDL_max(1.0f + h / 70.0f, 0.3f) : 1.0f;
				const float shade = (0.42f + 0.58f * SDL_max(lambert, 0.0f)) / (0.42f + 0.58f * up) * (1.0f - hollow) * deep;
				// A hole's corner, at the foot of a wall, takes the colour of the surface a little way in
				// from its edge (in this tile), past the edge's dark outline, so the wall shows the
				// surface's own colours down to its foot.
				int pi = i, pj = j;
				const bool hole = terrain_hole(t, sx, sy);
				any_surface |= !hole;
				for (int k = 0; hole && k < 8; ++k)
				{
					static const int dx[8] = { 1, -1, 0, 0, 1, -1, 1, -1 }, dy[8] = { 0, 0, 1, -1, 1, 1, -1, -1 };
					int step = 0;
					for (int n = 1; n <= TERRAIN_WALL_INSET; ++n)
					{
						const int ni = i + dx[k] * n, nj = j + dy[k] * n;
						if (ni < 0 || ni > per_x || nj < 0 || nj > per_y || terrain_hole(t, sx + dx[k] * n, sy + dy[k] * n))
							break;
						step = n;
					}
					if (step > 0)
					{
						pi = i + dx[k] * step;
						pj = j + dy[k] * step;
						break;
					}
				}
				V3DVertex *v = &vertices[vc++];
				memset(v, 0, sizeof(*v));
				v->position[0] = (float)(c * B3D_TILE_W + i * t->sample);
				v->position[1] = h;
				v->position[2] = (float)(j * t->sample);
				memcpy(v->normal, n, sizeof(n));
				const float px = (float)(pi * t->sample), py = (float)(pj * t->sample);
				// In the map's texture (terrain_ring): the row's slot, the tile's place in it.
				v->uv[0] = (c * B3D_TILE_W + px) / (float)((t->width - 1) * t->sample);
				v->uv[1] = ((map_row % TERRAIN_RING_ROWS) * B3D_TILE_H + py) / (float)(TERRAIN_RING_ROWS * B3D_TILE_H);
				v->tangent[0] = 1;
				v->tangent[3] = 1;
				v->color[0] = v->color[1] = v->color[2] = shade;
				v->color[3] = 1;
			}
		if (!any_surface)
		{
			vc = (int)base;  // all holes: nothing of this tile
			continue;
		}
		for (int j = 0; j < per_y; ++j)
			for (int i = 0; i < per_x; ++i)
			{
				const Uint32 a = base + j * (per_x + 1) + i, b = a + 1, d = a + per_x + 1, e = d + 1;
				const int sx = c * per_x + i, sy = map_row * per_y + j;
				const bool ha = terrain_hole(t, sx, sy), hb = terrain_hole(t, sx + 1, sy);
				const bool hd = terrain_hole(t, sx, sy + 1), he = terrain_hole(t, sx + 1, sy + 1);
				if (!(ha && hb && he))
				{
					indices[ic++] = a;
					indices[ic++] = b;
					indices[ic++] = e;
				}
				if (!(ha && he && hd))
				{
					indices[ic++] = a;
					indices[ic++] = e;
					indices[ic++] = d;
				}
			}
	}
	if (ic == 0)
		return NULL;
	BTBHGPUCustomMeshReport report;
	BTBHGPUCustomMesh *mesh = btbh_gpu_window_custom_mesh_create(window, vertices, (uint32_t)(vc * sizeof(V3DVertex)),
	                                                             (uint32_t)vc, indices, (uint32_t)ic, &report);
	if (mesh == NULL)
		fprintf(stderr, "warning: terrain row mesh: %s\n", report.message);
	return mesh;
}

static BTBHGPUCustomMesh *terrain_row_mesh(const B3DTerrain *t, int set, int map_row, float hole_depth)
{
	++terrain_clock;
	int slot = 0;
	for (int i = 0; i < TERRAIN_ROWS_CACHED; ++i)
	{
		if (terrain_rows[i].generation == b3d_map_generation + 1 && terrain_rows[i].set == set &&
		    terrain_rows[i].map_row == map_row && terrain_rows[i].hole_depth == hole_depth)
		{
			terrain_rows[i].used = terrain_clock;
			return terrain_rows[i].mesh;
		}
		const bool stale = terrain_rows[i].generation != b3d_map_generation + 1;
		const bool slot_stale = terrain_rows[slot].generation != b3d_map_generation + 1;
		if ((stale && !slot_stale) || (stale == slot_stale && terrain_rows[i].used < terrain_rows[slot].used))
			slot = i;
	}
	if (terrain_rows[slot].mesh != NULL)
		btbh_gpu_custom_mesh_destroy(terrain_rows[slot].mesh);
	terrain_rows[slot].mesh = build_terrain_row(t, set, map_row, hole_depth);
	terrain_rows[slot].set = set;
	terrain_rows[slot].map_row = map_row;
	terrain_rows[slot].hole_depth = hole_depth;
	terrain_rows[slot].generation = b3d_map_generation + 1;
	terrain_rows[slot].used = terrain_clock;
	return terrain_rows[slot].mesh;
}

/* --- Background maps ----------------------------------------------------------------------- */

// Background tiles sit this far below their layer, so that the captured layer, which is exact
// inside the playfield (filters and all), is drawn over them.
#define TILE_BELOW_LAYER 0.05f

// Atlas page coloured with the given colours, reusing one that already is. Returns its index.
static int tile_page(const Uint32 colors[256], bool ground_zero)
{
	if (!tile_indices_valid || tile_indices_generation != b3d_map_generation)
	{
		b3d_build_atlas(tile_indices, tile_opaque, tile_ground);
		tile_indices_valid = true;
		tile_indices_generation = b3d_map_generation;
	}

	const Uint32 hash = hash_colors(colors);
	int page = 0;
	for (int p = 0; p < TILE_PAGES; ++p)
	{
		if (tile_pages[p].valid && tile_pages[p].generation == b3d_map_generation && tile_pages[p].colors_hash == hash &&
		    tile_pages[p].ground_zero == ground_zero)
		{
			tile_pages[p].used = tile_frame;
			return p;
		}
		// Otherwise refill an unused page, or the least recently used one.
		const unsigned int age = tile_pages[p].valid ? tile_frame - tile_pages[p].used : ~0u;
		const unsigned int page_age = tile_pages[page].valid ? tile_frame - tile_pages[page].used : ~0u;
		if (age > page_age)
			page = p;
	}

	for (int i = 0; i < B3D_ATLAS_W * B3D_ATLAS_H; ++i)
		tile_rgba[i] = tile_opaque[i] || (ground_zero && tile_ground[i]) ? colors[tile_indices[i]] : 0;
	bleed_into_clear(tile_rgba, B3D_ATLAS_W, 0, B3D_ATLAS_H);
	btbh_gpu_texture_update_rgba8(tile_atlas, (const uint8_t *)tile_rgba, 0, page * B3D_ATLAS_H, B3D_ATLAS_W, B3D_ATLAS_H);
	// Water: the opaque pixels of water tiles (b3d_tile_is_water), with their cells' borders.
	{
		static const Uint8 water_rgba[4] = { 0, 0, 255, 255 };
		Uint32 water;
		memcpy(&water, water_rgba, 4);
		memset(tile_rgba, 0, sizeof(Uint32) * B3D_ATLAS_W * B3D_ATLAS_H);
		for (int set = 1; set <= B3D_SETS; ++set)
			for (int t = 0; t < B3D_TILES_PER_SET; ++t)
			{
				if (!b3d_tile_is_water(set, t))
					continue;
				int ox, oy;
				b3d_cell_origin((set - 1) * B3D_TILES_PER_SET + t, &ox, &oy);
				for (int y = -1; y <= B3D_TILE_H; ++y)
					for (int x = -1; x <= B3D_TILE_W; ++x)
					{
						const int i = (oy + y) * B3D_ATLAS_W + ox + x;
						if (tile_opaque[i] && b3d_water_pixel(set, t, tile_indices[i]))
							tile_rgba[i] = water;
					}
			}
	}
	btbh_gpu_texture_update_rgba8(tile_water, (const uint8_t *)tile_rgba, 0, page * B3D_ATLAS_H, B3D_ATLAS_W, B3D_ATLAS_H);
	tile_pages[page].valid = true;
	tile_pages[page].generation = b3d_map_generation;
	tile_pages[page].colors_hash = hash;
	tile_pages[page].ground_zero = ground_zero;
	tile_pages[page].used = tile_frame;
	return page;
}

static Uint8 composed_index[COMPOSED_SIZE * COMPOSED_SIZE];
static Uint8 composed_owner[COMPOSED_SIZE * COMPOSED_SIZE];
static Uint8 composed_images[L3D_MAX_BACKGROUNDS][COMPOSED_SIZE * COMPOSED_SIZE];
static Uint8 composed_shades[L3D_MAX_BACKGROUNDS][COMPOSED_SIZE * COMPOSED_SIZE];
static Uint32 composed_rgba[COMPOSED_SIZE * COMPOSED_SIZE];

// Appends a textured quad for each background composed on the CPU (the ones the game filters),
// covering the area the camera sees.
static void add_composed_batches(const L3DFrame *frame, const bool *composed, const Camera3D *camera,
                                 const float *heights, const Uint32 colors[256], bool new_frame, int *instance_count,
                                 int *batch_count)
{
	int first = -1;
	for (int i = 0; i < frame->background_count && first < 0; ++i)
		if (composed[i])
			first = i;
	if (first < 0)
		return;

	// The lowest composed plane sees the most; the others are drawn over the same area.
	float rect[4];
	plane_footprint(camera, heights[frame->backgrounds[first].layer] - TILE_BELOW_LAYER, rect);
	if (rect[0] > rect[2])
		return;
	int x0 = (int)floorf(rect[0]), z0 = (int)floorf(rect[1]);
	int w = (int)ceilf(rect[2]) - x0 + 1, h = (int)ceilf(rect[3]) - z0 + 1;
	if (w > COMPOSED_SIZE)
	{
		x0 = L3D_PLAYFIELD_X + L3D_PLAYFIELD_W / 2 - COMPOSED_SIZE / 2;
		w = COMPOSED_SIZE;
	}
	if (h > COMPOSED_SIZE)
	{
		z0 += h - COMPOSED_SIZE;  // keep the near part
		h = COMPOSED_SIZE;
	}

	// Frames between ticks reuse the images composed for the frame's tick, moved on.
	static int composed_area[4];
	if (!new_frame)
	{
		x0 = composed_area[0];
		z0 = composed_area[1];
		w = composed_area[2];
		h = composed_area[3];
	}
	else
	{
		composed_area[0] = x0;
		composed_area[1] = z0;
		composed_area[2] = w;
		composed_area[3] = h;
		Uint8 *images[L3D_MAX_BACKGROUNDS], *shades[L3D_MAX_BACKGROUNDS];
		for (int i = 0; i < L3D_MAX_BACKGROUNDS; ++i)
		{
			images[i] = composed_images[i];
			shades[i] = composed_shades[i];
		}
		b3d_compose(frame, composed, x0, z0, w, h, composed_index, composed_owner, images, shades);
	}

	const float texture_h = (float)(COMPOSED_SIZE * L3D_MAX_BACKGROUNDS);
	for (int i = 0; i < frame->background_count; ++i)
	{
		if (!composed[i] || *instance_count >= MAX_INSTANCES || *batch_count >= MAX_BATCHES)
			continue;

		// Pixels on top of the screen show the filtered screen; pixels that a higher background
		// covers keep this background's own drawing in the filters' colours.
		const L3DBackground *background = &frame->backgrounds[i];
		Uint8 remap[256];
		b3d_effect_remap(background, remap);
		const Uint8 *image = composed_images[i], *shade = composed_shades[i];
		for (int p = 0; p < w * h && new_frame; ++p)
		{
			Uint32 color;
			if (composed_owner[p] == i)
				color = colors[composed_index[p]];
			else if (image[p] != 0 || background->set == 1)
				color = colors[remap[image[p]]];
			else
			{
				composed_rgba[p] = 0;
				continue;
			}
			if (shade[p] != 255)
			{
				Uint8 *c = (Uint8 *)&color;
				for (int k = 0; k < 3; ++k)
					c[k] = (Uint8)(c[k] * shade[p] / 255);
			}
			composed_rgba[p] = color;
		}
		if (new_frame)
			btbh_gpu_texture_update_rgba8(composed_texture, (const uint8_t *)composed_rgba, 0, i * COMPOSED_SIZE, w, h);
		const bool glints = settings3d.effects;
		if (glints && new_frame)
		{
			for (int p = 0; p < w * h; ++p)
				composed_rgba[p] = composed_rgba[p] != 0 ? water_mask(composed_rgba[p]) : 0;
			btbh_gpu_texture_update_rgba8(composed_water, (const uint8_t *)composed_rgba, 0, i * COMPOSED_SIZE, w, h);
		}

		Mat4 transform = mat4_identity();
		transform.m[0] = (float)w;
		transform.m[10] = (float)h;
		transform.m[12] = (float)x0;
		transform.m[13] = heights[frame->backgrounds[i].layer] - TILE_BELOW_LAYER;
		transform.m[14] = (float)z0 + background_speed[background->set & 3] * ahead;
		write_instance(instances + *instance_count * 24, &transform, 1.0f);

		BTBHGPUSceneGeometryBatch *b = &batches[(*batch_count)++];
		init_batch(b);
		b->kind = BTBH_GPU_SCENE_GEOMETRY_CUSTOM_MESH;
		b->custom_mesh = quad_mesh;
		b->first_instance = (*instance_count)++;
		b->instance_count = 1;
		b->albedo_texture = composed_texture;
		b->uv_scale_x = (float)w / COMPOSED_SIZE;
		b->uv_scale_y = h / texture_h;
		b->uv_offset_y = i * COMPOSED_SIZE / texture_h;
		b->unlit_enabled = 1;
		b->alpha_cutoff = 0.5f;
		if (glints)
			set_glints(b, composed_water);
	}
}

// Appends instances and batches for the background maps: every tile the camera sees on each
// background's plane, grouped into one batch per atlas cell. Composed backgrounds are skipped.
/*
 * Terrain textures: a map itself, as the game shows it, in a ring of rows (a map row in slot
 * map_row % TERRAIN_RING_ROWS), so that filtering carries on across tiles as the map has them (a
 * tile atlas cell's border can only repeat the tile's own edge, which shows as seams). The texture
 * repeats vertically: the last slot's bottom edge filters into the first, which holds the next row.
 * For the ground also where its water is (set_glints).
 */
typedef struct
{
	BTBHGPUTexture *texture, *water;
	int width;                    // pixels
	int rows[TERRAIN_RING_ROWS];  // the map row each slot holds, or -1
	unsigned int generation;      // b3d_map_generation + 1 that the slots are of
	Uint32 colors_hash;
	bool ground_zero;
} TerrainRing;

static TerrainRing terrain_rings[B3D_SETS + 1];

static struct
{
	unsigned int generation;  // b3d_map_generation + 1 the meshes were made for
	BTBHGPUCustomMesh *meshes[B3D_PLANT_KINDS];
} plant_meshes;  // (vegetation)

static void forget_plants(void)
{
	memset(&plant_meshes, 0, sizeof(plant_meshes));
}

// The terrain's meshes and textures go with the window.
static void forget_terrain(void)
{
	memset(terrain_rings, 0, sizeof(terrain_rings));
	memset(terrain_rows, 0, sizeof(terrain_rows));
	forget_plants();
}

// A background's ring, emptied when its map or colours change.
static TerrainRing *terrain_ring(const B3DTerrain *t, int set, const Uint32 colors[256], bool ground_zero)
{
	TerrainRing *ring = &terrain_rings[set];
	const int width = (t->width - 1) * t->sample;
	if (ring->texture == NULL || ring->width != width)
	{
		if (ring->texture != NULL)
			btbh_gpu_texture_destroy(ring->texture);
		if (ring->water != NULL)
			btbh_gpu_texture_destroy(ring->water);
		BTBHGPUTextureReport report;
		Uint32 *zeroes = calloc((size_t)width * TERRAIN_RING_ROWS * B3D_TILE_H, sizeof(Uint32));
		ring->texture = zeroes == NULL ? NULL : btbh_gpu_window_texture_create_rgba8_ex(window, (const uint8_t *)zeroes, width,
			TERRAIN_RING_ROWS * B3D_TILE_H, 0, map_filter(), BTBH_GPU_TEXTURE_WRAP_REPEAT, BTBH_GPU_TEXTURE_COLOR_SPACE_SRGB, &report);
		ring->water = zeroes == NULL || set != 1 ? NULL : btbh_gpu_window_texture_create_rgba8_ex(window, (const uint8_t *)zeroes,
			width, TERRAIN_RING_ROWS * B3D_TILE_H, 0, BTBH_GPU_TEXTURE_FILTER_NEAREST, BTBH_GPU_TEXTURE_WRAP_REPEAT,
			BTBH_GPU_TEXTURE_COLOR_SPACE_LINEAR, &report);
		free(zeroes);
		if (ring->texture == NULL)
			fprintf(stderr, "warning: terrain texture: %s\n", report.message);
		ring->width = width;
		ring->generation = 0;
	}
	const Uint32 hash = hash_colors(colors);
	if (ring->generation != b3d_map_generation + 1 || ring->colors_hash != hash || ring->ground_zero != ground_zero)
	{
		for (int i = 0; i < TERRAIN_RING_ROWS; ++i)
			ring->rows[i] = -1;
		ring->generation = b3d_map_generation + 1;
		ring->colors_hash = hash;
		ring->ground_zero = ground_zero;
	}
	return ring->texture != NULL ? ring : NULL;
}

// Under the 3D palms, the palms painted in the map give way to the ground round them: their green
// pixels take the average colour of the other pixels just outside the palm.
static void erase_painted_palms(Uint32 *rgba, int width, int map_row)
{
	const B3DVegetation *veg = b3d_vegetation();
	if (veg == NULL || map_row < 0 || map_row >= veg->rows)
		return;
	const int top = map_row * B3D_TILE_H;
	for (int r = SDL_max(map_row - 1, 0); r <= SDL_min(map_row + 1, veg->rows - 1); ++r)
		for (int i = veg->row_start[r]; i < veg->row_start[r + 1]; ++i)
		{
			const B3DPlant *p = &veg->plants[i];
			if (p->kind != B3D_PALM)
				continue;
			const float radius = p->size / 8.0f * 1.15f;
			const int cx = p->x, cy = p->y - top;
			// The ground round the palm.
			float sum[3] = { 0, 0, 0 };
			int n = 0;
			const int ring_r = (int)radius + 3;
			for (int y = SDL_max(cy - ring_r, 0); y <= SDL_min(cy + ring_r, B3D_TILE_H - 1); ++y)
				for (int x = SDL_max(cx - ring_r, 0); x <= SDL_min(cx + ring_r, width - 1); ++x)
				{
					const float d = sqrtf((float)((x - cx) * (x - cx) + (y - cy) * (y - cy)));
					const Uint8 *c = (const Uint8 *)&rgba[y * width + x];
					if (d < radius || d > radius + 3 || c[3] == 0 || (c[1] > c[0] && c[1] > c[2]) || c[0] + c[1] + c[2] < 150)
						continue;
					sum[0] += c[0];
					sum[1] += c[1];
					sum[2] += c[2];
					++n;
				}
			if (n == 0)
				continue;
			for (int y = SDL_max(cy - (int)radius, 0); y <= SDL_min(cy + (int)radius, B3D_TILE_H - 1); ++y)
				for (int x = SDL_max(cx - (int)radius, 0); x <= SDL_min(cx + (int)radius, width - 1); ++x)
				{
					Uint8 *c = (Uint8 *)&rgba[y * width + x];
					const bool green = c[1] > c[0] && c[1] > c[2];
					const bool dark = c[0] + c[1] + c[2] < 150;  // the palm's outline and shadow
					if (c[3] == 0 || (!green && !dark) || (x - cx) * (x - cx) + (y - cy) * (y - cy) > radius * radius)
						continue;
					for (int k = 0; k < 3; ++k)
						c[k] = (Uint8)(sum[k] / n);
				}
		}
}

// Puts a map row into its slot of the ring, unless it is there already.
static void terrain_ring_row(TerrainRing *ring, const B3DTerrain *t, int set, int map_row, const Uint32 colors[256])
{
	const int slot = map_row % TERRAIN_RING_ROWS;
	if (map_row < 0 || ring->rows[slot] == map_row)
		return;
	ring->rows[slot] = map_row;
	static Uint32 rgba[(15 + 2 * 32) * B3D_TILE_W * B3D_TILE_H], water[(15 + 2 * 32) * B3D_TILE_W * B3D_TILE_H];
	const int columns = SDL_min(ring->width / B3D_TILE_W, (int)(COUNTOF(rgba) / (B3D_TILE_W * B3D_TILE_H)));
	static const Uint8 water_rgba[4] = { 0, 0, 255, 255 };
	Uint32 water_color;
	memcpy(&water_color, water_rgba, 4);
	for (int c = 0; c < columns; ++c)
	{
		bool flipped;
		const int cell = b3d_map_cell(set, map_row, c - t->side_columns, &flipped);
		int ox = 0, oy = 0;
		if (cell >= 0)
			b3d_cell_origin(cell, &ox, &oy);
		const int tile = cell >= 0 ? cell % B3D_TILES_PER_SET : 0;
		const bool water_tile = cell >= 0 && ring->water != NULL && b3d_tile_is_water(set, tile);
		for (int y = 0; y < B3D_TILE_H; ++y)
			for (int x = 0; x < B3D_TILE_W; ++x)
			{
				Uint32 *out = &rgba[y * ring->width + c * B3D_TILE_W + x];
				Uint32 *wet = &water[y * ring->width + c * B3D_TILE_W + x];
				*out = *wet = 0;
				if (cell < 0)
					continue;
				const int i = (oy + y) * B3D_ATLAS_W + ox + (flipped ? B3D_TILE_W - 1 - x : x);
				if (tile_opaque[i] || (ring->ground_zero && tile_ground[i]))
					*out = colors[tile_indices[i]];
				if (water_tile && tile_opaque[i] && b3d_water_pixel(set, tile, tile_indices[i]))
					*wet = water_color;
			}
	}
	if (set == 1)
		erase_painted_palms(rgba, ring->width, map_row);
	bleed_into_clear(rgba, ring->width, 0, B3D_TILE_H);
	btbh_gpu_texture_update_rgba8(ring->texture, (const uint8_t *)rgba, 0, (Uint32)(slot * B3D_TILE_H), (Uint32)ring->width,
	                              B3D_TILE_H);
	if (ring->water != NULL)
		btbh_gpu_texture_update_rgba8(ring->water, (const uint8_t *)water, 0, (Uint32)(slot * B3D_TILE_H), (Uint32)ring->width,
		                              B3D_TILE_H);
}

/*
 * Vegetation (b3d_vegetation): palms, trees and grass clumps as models on the terrain, made here
 * for each map in its plants' colours (unit size: the plant's size in pixels scales them), shaded
 * by the sun into their vertex colours, swaying in the wind (grass most). They cast shadows.
 */
#define PLANT_VERTICES 4096


typedef struct
{
	V3DVertex *vertices;
	Uint32 *indices;
	int vc, ic;
	float light[3];
} PlantBuilder;

static float plant_shade(const float n[3], const float light[3])
{
	const float lambert = n[0] * light[0] + n[1] * light[1] + n[2] * light[2];
	const float up = SDL_max(light[1], 0.0f);
	return (0.5f + 0.5f * SDL_max(lambert, 0.0f)) / (0.5f + 0.5f * up);
}

static Uint32 plant_vertex(PlantBuilder *b, float x, float y, float z, const float n_in[3], const float rgb[3])
{
	if (b->vc >= PLANT_VERTICES)
		return 0;
	float n[3] = { n_in[0], n_in[1], n_in[2] };
	const float l = sqrtf(n[0] * n[0] + n[1] * n[1] + n[2] * n[2]);
	for (int k = 0; k < 3; ++k)
		n[k] = l > 0 ? n[k] / l : (k == 1);
	V3DVertex *v = &b->vertices[b->vc];
	memset(v, 0, sizeof(*v));
	v->position[0] = x;
	v->position[1] = y;
	v->position[2] = z;
	memcpy(v->normal, n, sizeof(n));
	v->uv[0] = v->uv[1] = 0.5f;
	v->tangent[0] = 1;
	v->tangent[3] = 1;
	// Leaves lit from both sides: the better of the two.
	float back[3] = { -n[0], -n[1], -n[2] };
	const float shade = SDL_max(plant_shade(n, b->light), 0.8f * plant_shade(back, b->light));
	for (int k = 0; k < 3; ++k)
		v->color[k] = rgb[k] * shade;
	v->color[3] = 1;
	return (Uint32)b->vc++;
}

static void plant_triangle(PlantBuilder *b, Uint32 a, Uint32 c, Uint32 d)
{
	b->indices[b->ic++] = a;
	b->indices[b->ic++] = c;
	b->indices[b->ic++] = d;
}

static void linear_rgb(const Uint8 rgb[3], float scale, float out[3])
{
	for (int k = 0; k < 3; ++k)
		out[k] = srgb_to_linear(rgb[k]) * scale;
}

static float plant_random(Uint32 *seed)
{
	*seed = *seed * 1664525u + 1013904223u;
	return (*seed >> 8) / 16777216.0f;
}

// A palm: a leaning, tapering trunk with rings, and drooping fronds (unit: the crown's radius).
static void build_palm(PlantBuilder *b, const B3DVegetation *veg)
{
	float leaf[3], trunk[3], dark[3];
	linear_rgb(veg->colors[0], 1.15f, leaf);
	linear_rgb(veg->colors[1], 1.0f, trunk);
	for (int k = 0; k < 3; ++k)
		dark[k] = trunk[k] * 0.7f;
	enum { SIDES = 6, RINGS = 7 };
	const float top_y = 1.55f, lean = 0.3f;
	Uint32 ring[RINGS][SIDES];
	for (int r = 0; r < RINGS; ++r)
	{
		const float t = r / (float)(RINGS - 1);
		const float cx = lean * t * t, cy = top_y * t, radius = 0.11f - 0.05f * t;
		for (int s = 0; s < SIDES; ++s)
		{
			const float a = 6.2831853f * s / SIDES;
			const float n[3] = { cosf(a), 0, sinf(a) };
			ring[r][s] = plant_vertex(b, cx + radius * cosf(a), cy, radius * sinf(a), n, (r & 1) ? trunk : dark);
		}
	}
	for (int r = 0; r + 1 < RINGS; ++r)
		for (int s = 0; s < SIDES; ++s)
		{
			const int s2 = (s + 1) % SIDES;
			plant_triangle(b, ring[r][s], ring[r + 1][s], ring[r + 1][s2]);
			plant_triangle(b, ring[r][s], ring[r + 1][s2], ring[r][s2]);
		}
	// Fronds: strips from the top, arching out and drooping, folded along their midrib.
	enum { FRONDS = 8, STEPS = 7 };
	Uint32 seed = 1234;
	for (int f = 0; f < FRONDS; ++f)
	{
		const float a = 6.2831853f * (f + 0.3f * plant_random(&seed)) / FRONDS;
		const float dx = cosf(a), dz = sinf(a), length = 1.15f + 0.25f * plant_random(&seed);
		Uint32 left[STEPS + 1], mid[STEPS + 1], right[STEPS + 1];
		for (int i = 0; i <= STEPS; ++i)
		{
			const float t = i / (float)STEPS;
			const float out = length * t, y = top_y + 0.28f * sinf(3.14159f * t * 0.7f) - 0.75f * t * t;
			const float width = 0.2f * sinf(3.14159f * SDL_min(t * 1.15f, 1.0f));
			const float px = lean + dx * out, pz = dz * out;
			float shade_rgb[3];
			for (int k = 0; k < 3; ++k)
				shade_rgb[k] = leaf[k] * (0.75f + 0.35f * t);
			const float n[3] = { 0, 1, 0 };
			mid[i] = plant_vertex(b, px, y + 0.04f, pz, n, shade_rgb);
			left[i] = plant_vertex(b, px - dz * width, y - 0.05f * width / 0.2f, pz + dx * width, n, shade_rgb);
			right[i] = plant_vertex(b, px + dz * width, y - 0.05f * width / 0.2f, pz - dx * width, n, shade_rgb);
		}
		for (int i = 0; i < STEPS; ++i)
		{
			plant_triangle(b, mid[i], left[i], left[i + 1]);
			plant_triangle(b, mid[i], left[i + 1], mid[i + 1]);
			plant_triangle(b, mid[i], mid[i + 1], right[i + 1]);
			plant_triangle(b, mid[i], right[i + 1], right[i]);
		}
	}
}

// A tree seen from above: a lumpy round crown on a short trunk (unit: the crown's radius).
static void build_tree(PlantBuilder *b, const B3DVegetation *veg)
{
	float leaf[3], light[3];
	linear_rgb(veg->colors[2], 1.0f, leaf);
	linear_rgb(veg->colors[3], 1.0f, light);
	static const float lobes[4][4] = { { 0, 1.0f, 0, 0.85f }, { 0.45f, 0.85f, 0.2f, 0.55f }, { -0.4f, 0.8f, 0.3f, 0.5f },
	                                   { 0.05f, 0.9f, -0.45f, 0.5f } };
	enum { SEG = 12, BANDS = 7 };
	for (int l = 0; l < 4; ++l)
	{
		Uint32 grid[BANDS + 1][SEG];
		for (int r = 0; r <= BANDS; ++r)
		{
			const float phi = 3.14159f * r / BANDS;  // from the top down
			for (int s = 0; s < SEG; ++s)
			{
				const float theta = 6.2831853f * s / SEG;
				float n[3] = { sinf(phi) * cosf(theta), cosf(phi), sinf(phi) * sinf(theta) };
				Uint32 seed = (Uint32)(l * 977 + r * 131 + s * 17);
				const float bump = 1.0f + 0.16f * (plant_random(&seed) - 0.5f);
				const float radius = lobes[l][3] * bump;
				// Lighter on top, darker underneath; speckled like leaves.
				const float up = (n[1] + 1) * 0.5f;
				float rgb[3];
				const float speckle = 0.85f + 0.3f * plant_random(&seed);
				for (int k = 0; k < 3; ++k)
					rgb[k] = (leaf[k] + (light[k] - leaf[k]) * up * up) * speckle * (0.55f + 0.45f * up);
				grid[r][s] = plant_vertex(b, lobes[l][0] + n[0] * radius, lobes[l][1] + n[1] * radius * 0.75f,
				                          lobes[l][2] + n[2] * radius, n, rgb);
			}
		}
		for (int r = 0; r < BANDS; ++r)
			for (int s = 0; s < SEG; ++s)
			{
				const int s2 = (s + 1) % SEG;
				plant_triangle(b, grid[r][s], grid[r + 1][s2], grid[r + 1][s]);
				plant_triangle(b, grid[r][s], grid[r][s2], grid[r + 1][s2]);
			}
	}
}

// A clump of grass: blades from the ground, leaning out (unit: the blades' height).
static void build_grass(PlantBuilder *b, const B3DVegetation *veg)
{
	float base[3], tip[3];
	linear_rgb(veg->colors[4], 1.0f, base);
	linear_rgb(veg->colors[5], 1.0f, tip);
	Uint32 seed = 99;
	for (int i = 0; i < 7; ++i)
	{
		const float a = 6.2831853f * plant_random(&seed), r = 0.3f * plant_random(&seed);
		const float x = cosf(a) * r, z = sinf(a) * r;
		const float h = 0.6f + 0.4f * plant_random(&seed), lean = 0.25f + 0.3f * plant_random(&seed);
		const float facing = 6.2831853f * plant_random(&seed);
		const float wx = cosf(facing) * 0.09f, wz = sinf(facing) * 0.09f;
		const float n[3] = { -wz, 0.3f, wx };
		const float mid_rgb[3] = { (base[0] + tip[0]) / 2, (base[1] + tip[1]) / 2, (base[2] + tip[2]) / 2 };
		const Uint32 b0 = plant_vertex(b, x - wx, 0, z - wz, n, base);
		const Uint32 b1 = plant_vertex(b, x + wx, 0, z + wz, n, base);
		const Uint32 m0 = plant_vertex(b, x + cosf(a) * lean * 0.4f - wx * 0.7f, h * 0.55f, z + sinf(a) * lean * 0.4f - wz * 0.7f, n, mid_rgb);
		const Uint32 m1 = plant_vertex(b, x + cosf(a) * lean * 0.4f + wx * 0.7f, h * 0.55f, z + sinf(a) * lean * 0.4f + wz * 0.7f, n, mid_rgb);
		const Uint32 t0 = plant_vertex(b, x + cosf(a) * lean, h, z + sinf(a) * lean, n, tip);
		plant_triangle(b, b0, b1, m1);
		plant_triangle(b, b0, m1, m0);
		plant_triangle(b, m0, m1, t0);
	}
}

static void make_plant_meshes(const B3DVegetation *veg)
{
	if (plant_meshes.generation == b3d_map_generation + 1)
		return;
	plant_meshes.generation = b3d_map_generation + 1;
	static V3DVertex vertices[PLANT_VERTICES];
	static Uint32 indices[PLANT_VERTICES * 6];
	const float length = sqrtf(sun_direction[0] * sun_direction[0] + sun_direction[1] * sun_direction[1] +
	                           sun_direction[2] * sun_direction[2]);
	for (int kind = 0; kind < B3D_PLANT_KINDS; ++kind)
	{
		if (plant_meshes.meshes[kind] != NULL)
			btbh_gpu_custom_mesh_destroy(plant_meshes.meshes[kind]);
		plant_meshes.meshes[kind] = NULL;
		PlantBuilder b = { vertices, indices, 0, 0,
		                   { -sun_direction[0] / length, -sun_direction[1] / length, -sun_direction[2] / length } };
		if (kind == B3D_PALM)
			build_palm(&b, veg);
		else if (kind == B3D_TREE)
			build_tree(&b, veg);
		else
			build_grass(&b, veg);
		if (b.ic == 0)
			continue;
		BTBHGPUCustomMeshReport report;
		plant_meshes.meshes[kind] = btbh_gpu_window_custom_mesh_create(window, vertices, (uint32_t)(b.vc * sizeof(V3DVertex)),
		                                                               (uint32_t)b.vc, indices, (uint32_t)b.ic, &report);
		if (plant_meshes.meshes[kind] == NULL)
			fprintf(stderr, "warning: plant mesh: %s\n", report.message);
	}
}

static float terrain_height_at(const B3DTerrain *t, float mx, float my)
{
	const float fx = mx / t->sample, fy = my / t->sample;
	const int sx = (int)floorf(fx), sy = (int)floorf(fy);
	float h[4];
	for (int k = 0; k < 4; ++k)
	{
		const int ix = SDL_clamp(sx + (k & 1), 0, t->width - 1), iy = SDL_clamp(sy + (k >> 1), 0, t->height - 1);
		const Sint8 value = t->heights[iy * t->width + ix];
		h[k] = t->holes && value == B3D_TERRAIN_HOLE ? 0.0f : value;
	}
	const float ax = fx - sx, ay = fy - sy;
	return (h[0] * (1 - ax) + h[1] * ax) * (1 - ay) + (h[2] * (1 - ax) + h[3] * ax) * ay;
}

static void add_background_batches(const L3DFrame *frame, const bool *composed, const Camera3D *camera,
                                   const float *heights, const Uint32 colors[256], int *instance_count, int *batch_count)
{
	cloud_tile_count = 0;
	if (frame->background_count == 0)
		return;
	++tile_frame;
	const bool relief_ground = relief_frame(frame, composed) && frame_terrains[1] == NULL;
	typedef struct
	{
		int set, map_row;
		float x, z, height, hole_depth;
		int page;
		float brightness;
	} TerrainRowDraw;
	TerrainRowDraw terrain_row_draws[MAX_TERRAIN_ROW_DRAWS];
	int terrain_row_count = 0;

	static B3DTile tiles[MAX_TILES];
	static float tile_height[MAX_TILES];
	static int tile_key[MAX_TILES];
	const int capacity = SDL_min(MAX_TILES, MAX_INSTANCES - *instance_count);
	int tile_count = 0;

	// TYR3D_BACKGROUNDS: which maps get tiles, e.g. "13" for backgrounds 1 and 3 (default all).
	const char *only = SDL_getenv("TYR3D_BACKGROUNDS");

	for (int i = 0; i < frame->background_count; ++i)
	{
		const L3DBackground *background = &frame->backgrounds[i];
		if (only != NULL && SDL_strchr(only, '0' + background->set) == NULL)
			continue;
		if (water_overlay(background))
			continue;
		// A composed (filtered) background covers only so much; its tiles, in the filters' colours,
		// go on beyond it, a little below so that the composed image wins where it is.
		float height = heights[background->layer] - TILE_BELOW_LAYER - (composed[i] ? 0.1f : 0.0f);
		if (background->set > 1 && terrain_background(frame, background))
			height = SDL_min(height, solid_top(background->set));
		const float shift = background_speed[background->set & 3] * ahead;
		float rect[4];
		plane_footprint(camera, height, rect);
		if (rect[0] > rect[2])
			continue;
		rect[1] -= shift;  // what has scrolled into view
		rect[3] -= shift;

		b3d_tile_is_cloud(background->set, 0);  // classifies the set's tiles (logged with TYR3D_LOG_CLOUDS)
		// Tiles take the colours the game gives them through blending and the level's filters.
		Uint8 remap[256];
		Uint32 page_colors[256];
		if (background->set > 1 && terrain_background(frame, background))
			b3d_effect_remap(background, remap);
		else
			b3d_tile_remap(background, remap);
		for (int c = 0; c < 256; ++c)
			page_colors[c] = colors[remap[c]];
		// The game clears the screen to colour 0 under background 1; a filter that recolours it
		// shows there too (lava, ice).
		const bool ground_zero = background->set == 1 && remap[0] != 0;
		const int page = tile_page(page_colors, ground_zero);

		const int first = tile_count;
		tile_count += b3d_collect_tiles(background, ground_zero, rect[0], rect[1], rect[2], rect[3],
		                                tiles + tile_count, capacity - tile_count);
		// Cloud tiles are clouds (add_cloud_batches).
		if (cloud_background(background, composed[i]))
		{
			memcpy(cloud_page_colors[background->set], page_colors, sizeof(page_colors));
			int kept = first;
			for (int t = first; t < tile_count; ++t)
			{
				const int tile = tiles[t].cell % B3D_TILES_PER_SET;
				if (tiles[t].cell < B3D_CELLS && tiles[t].cell / B3D_TILES_PER_SET + 1 == background->set &&
				    b3d_tile_is_cloud(background->set, tile))
				{
					if (cloud_tile_count < MAX_CLOUD_TILES && !low_background(background))
						cloud_tiles[cloud_tile_count++] = (CloudTile){
							(Uint8)background->set, (Uint8)tile, tiles[t].flipped, background->blend, background->layer,
							tiles[t].x, tiles[t].z, cloud_page_colors[background->set], tiles[t].map_row, tiles[t].map_column };
					continue;
				}
				tiles[kept++] = tiles[t];
			}
			tile_count = kept;
		}
		// Terrain: the map's rows are meshes (the tiles beyond its columns stay tiles).
		if (terrain_background(frame, background))
		{
			const B3DTerrain *terrain = frame_terrains[background->set];
			TerrainRing *ring = terrain_ring(terrain, background->set, page_colors, ground_zero);
			// Holes: in the ground, chasms; in backgrounds 2 and 3, the walls of their solids go
			// down to below the ground.
			const float hole_depth = background->set == 1 ? TERRAIN_HOLE_DEPTH : height * 1.5f + 8.0f;
			const int columns = (terrain->width - 1) / (B3D_TILE_W / terrain->sample);
			int kept = first;
			for (int t = first; t < tile_count; ++t)
			{
				const int column = tiles[t].map_column + terrain->side_columns;
				if (column < 0 || column >= columns)
				{
					tiles[kept++] = tiles[t];
					continue;
				}
				bool seen = false;
				for (int r = 0; r < terrain_row_count && !seen; ++r)
					seen = terrain_row_draws[r].set == background->set && terrain_row_draws[r].map_row == tiles[t].map_row;
				if (seen || terrain_row_count == (int)COUNTOF(terrain_row_draws))
					continue;
				float brightness = 1.0f;
				const float distance = -(tiles[t].z + shift);
				if (distance > BACKGROUND_AHEAD - BACKGROUND_FADE)
					brightness = SDL_max(0.0f, (BACKGROUND_AHEAD - distance) / BACKGROUND_FADE);
				if (ring == NULL)
					continue;
				// The row and the one below it (that its bottom edge filters into).
				terrain_ring_row(ring, terrain, background->set, tiles[t].map_row, page_colors);
				terrain_ring_row(ring, terrain, background->set, tiles[t].map_row + 1, page_colors);
				terrain_row_draws[terrain_row_count++] = (TerrainRowDraw){
					background->set, tiles[t].map_row, tiles[t].x - column * B3D_TILE_W, tiles[t].z + shift, height, hole_depth,
					page, brightness };
			}
			tile_count = kept;
		}
		for (int t = first; t < tile_count; ++t)
		{
			tiles[t].z += shift;
			tile_height[t] = height;
			// Batch key: atlas page and cell, mirrored, fading.
			// Terrain: background 1's tiles, not mirrored, when the frame's ground is terrain.
			const bool relief = relief_ground && background->set == 1 && !tiles[t].flipped &&
			                    tiles[t].cell < B3D_CELLS && relief_mesh(tiles[t].cell) != NULL;
			tile_key[t] = (((page * B3D_ATLAS_CELLS + tiles[t].cell) * 2 + tiles[t].flipped) * 3 + tiles[t].fade + 1) * 2 +
			              relief;
		}
	}

	enum { KEYS = TILE_PAGES * B3D_ATLAS_CELLS * 12 };
	static int key_count[KEYS], key_next[KEYS];
	memset(key_count, 0, sizeof(key_count));
	for (int t = 0; t < tile_count; ++t)
		++key_count[tile_key[t]];
	int next = *instance_count;
	for (int key = 0; key < KEYS; ++key)
	{
		key_next[key] = next;
		next += key_count[key];
	}

	for (int t = 0; t < tile_count; ++t)
	{
		const B3DTile *tile = &tiles[t];

		// Fade out towards the furthest drawn row.
		float brightness = tile->brightness;
		const float ahead = -tile->z;
		if (ahead > BACKGROUND_AHEAD - BACKGROUND_FADE)
			brightness *= SDL_max(0.0f, (BACKGROUND_AHEAD - ahead) / BACKGROUND_FADE);

		Mat4 transform = mat4_identity();
		transform.m[0] = B3D_TILE_W;
		transform.m[10] = B3D_TILE_H;
		transform.m[12] = tile->x;
		transform.m[13] = tile_height[t];
		transform.m[14] = tile->z;
		write_instance(instances + key_next[tile_key[t]]++ * 24, &transform, brightness);
	}

	const float atlas_h = (float)(B3D_ATLAS_H * TILE_PAGES);
	for (int key = 0; key < KEYS; ++key)
	{
		if (key_count[key] == 0 || *batch_count >= MAX_BATCHES)
			continue;
		const bool relief = (key & 1) != 0;
		const int tile_key_value = key / 2;
		const int fade = tile_key_value % 3 - 1;
		const bool flipped = (tile_key_value / 3 & 1) != 0;
		const int cell = tile_key_value / 6 % B3D_ATLAS_CELLS, page = tile_key_value / 6 / B3D_ATLAS_CELLS;
		int ox, oy;
		b3d_cell_origin(cell, &ox, &oy);
		oy += page * B3D_ATLAS_H;

		BTBHGPUSceneGeometryBatch *b = &batches[(*batch_count)++];
		init_batch(b);
		b->kind = BTBH_GPU_SCENE_GEOMETRY_CUSTOM_MESH;
		b->custom_mesh = relief ? relief_mesh(cell) : fade == 0 ? quad_mesh : fade_meshes[fade > 0];
		b->first_instance = key_next[key] - key_count[key];
		b->instance_count = key_count[key];
		b->albedo_texture = tile_atlas;
		const float inset = tile_inset();
		b->uv_scale_x = (flipped ? -1.0f : 1.0f) * (B3D_TILE_W - 2 * inset) / B3D_ATLAS_W;
		b->uv_scale_y = (B3D_TILE_H - 2 * inset) / atlas_h;
		b->uv_offset_x = (ox + (flipped ? B3D_TILE_W - inset : inset)) / B3D_ATLAS_W;
		b->uv_offset_y = (oy + inset) / atlas_h;
		b->unlit_enabled = 1;
		b->alpha_cutoff = 0.5f;
		set_glints(b, tile_water);
	}
	*instance_count = next;

	// The terrain's rows.
	for (int r = 0; r < terrain_row_count && *instance_count < MAX_INSTANCES && *batch_count < MAX_BATCHES; ++r)
	{
		const TerrainRowDraw *row = &terrain_row_draws[r];
		BTBHGPUCustomMesh *mesh = terrain_row_mesh(frame_terrains[row->set], row->set, row->map_row, row->hole_depth);
		if (mesh == NULL)
			continue;
		const Mat4 transform = mat4_translation(row->x, row->height, row->z);
		write_instance(instances + *instance_count * 24, &transform, row->brightness);
		terrain_batch[*batch_count] = true;
		BTBHGPUSceneGeometryBatch *b = &batches[(*batch_count)++];
		init_batch(b);
		b->kind = BTBH_GPU_SCENE_GEOMETRY_CUSTOM_MESH;
		b->custom_mesh = mesh;
		b->first_instance = (*instance_count)++;
		b->instance_count = 1;
		b->albedo_texture = terrain_rings[row->set].texture;
		b->unlit_enabled = 1;
		b->alpha_cutoff = 0.5f;
		if (terrain_rings[row->set].water != NULL)
			set_glints(b, terrain_rings[row->set].water);
		else if (settings3d.effects)
			b->normal_scale = -BACKGROUND_RELIEF;  // the relief the lights bring out (see set_glints)
	}

	// The ground's plants, on the rows drawn.
	const B3DVegetation *veg = frame_terrains[1] != NULL ? b3d_vegetation() : NULL;
	if (veg == NULL || !m3d_enabled)
		return;
	make_plant_meshes(veg);
	const B3DTerrain *ground = frame_terrains[1];
	for (int kind = 0; kind < B3D_PLANT_KINDS && *batch_count < MAX_BATCHES; ++kind)
	{
		if (plant_meshes.meshes[kind] == NULL)
			continue;
		const int first = *instance_count;
		for (int r = 0; r < terrain_row_count; ++r)
		{
			const TerrainRowDraw *row = &terrain_row_draws[r];
			if (row->set != 1 || row->map_row < 0 || row->map_row >= veg->rows)
				continue;
			const Mat4 base = aligned(&(Mat4){ .m = { 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, row->x, row->height, row->z, 1 } });
			for (int i = veg->row_start[row->map_row]; i < veg->row_start[row->map_row + 1] && *instance_count < MAX_INSTANCES; ++i)
			{
				const B3DPlant *p = &veg->plants[i];
				if (p->kind != kind)
					continue;
				const float size = p->size / 8.0f, turn = p->turn / 256.0f * 6.2831853f;
				const float x = p->x, z = p->y - row->map_row * (float)B3D_TILE_H;
				const float h = terrain_height_at(ground, p->x, p->y);
				// The wind: gusts rolling over the map, the grass bending most.
				const float wind = sinf(glint_time * 1.6f + p->x * 0.045f + p->y * 0.03f) * 0.6f +
				                   sinf(glint_time * 3.7f + p->x * 0.11f) * 0.25f;
				const float bend = (kind == B3D_GRASS ? 0.35f : kind == B3D_PALM ? 0.05f : 0.015f) * wind;
				Mat4 local = mat4_identity();
				const float c = cosf(turn), s = sinf(turn);
				local.m[0] = c * size;
				local.m[2] = -s * size;
				local.m[8] = s * size;
				local.m[10] = c * size;
				local.m[5] = size;
				local.m[4] = bend * size;          // up bends towards +x...
				local.m[6] = bend * 0.4f * size;   // ...and a little down the screen
				local.m[12] = x;
				local.m[13] = h;
				local.m[14] = z;
				// base only scales (alike on all axes) and moves: base * local, worked out directly.
				Mat4 world;
				for (int k = 0; k < 12; ++k)
					world.m[k] = base.m[0] * local.m[k];
				world.m[12] = base.m[0] * local.m[12] + base.m[12];
				world.m[13] = base.m[0] * local.m[13] + base.m[13];
				world.m[14] = base.m[0] * local.m[14] + base.m[14];
				world.m[15] = 1;
				float *instance = instances + *instance_count * 24;
				write_instance_world(instance, &world, row->brightness * p->shade / 128.0f);
				++*instance_count;
			}
		}
		if (*instance_count == first)
			continue;
		terrain_batch[*batch_count] = true;  // they cast shadows
		BTBHGPUSceneGeometryBatch *b = &batches[(*batch_count)++];
		init_batch(b);
		b->kind = BTBH_GPU_SCENE_GEOMETRY_CUSTOM_MESH;
		b->custom_mesh = plant_meshes.meshes[kind];
		b->first_instance = first;
		b->instance_count = (uint32_t)(*instance_count - first);
		b->albedo_texture = white_texture;
		b->unlit_enabled = 1;
	}
}

// The starfield sits below background 1, whose colour 0 lets it through as in the game.
#define STARS_BELOW_LAYER 0.3f

// The game's stars: below the ground, or below its chasms where its terrain has holes.
static float stars_below_layer(void)
{
	return STARS_BELOW_LAYER + (frame_terrains[1] != NULL && frame_terrains[1]->holes ? TERRAIN_HOLE_DEPTH + 4.0f : 0.0f);
}

static float srgb_to_linear(Uint8 value)
{
	const float c = value / 255.0f;
	return c <= 0.04045f ? c / 12.92f : powf((c + 0.055f) / 1.055f, 2.4f);
}

/*
 * Deep space (M8, procedural stars): while the game's starfield is on, more stars lie in a few
 * layers far below the ground and scroll with the game's stars, so space shows depth as the level
 * moves: the deeper layers creep by slower and look finer. Like the game's stars they show only
 * through what background 1 leaves empty. They only show (the Effects setting).
 */
#define DEEP_STAR_LAYERS 3

static const struct
{
	float depth;       // game pixels below the game's stars
	int count;
	float size;        // game pixels
	float brightness;  // shade of the starfield's palette ramp, 0-1
} deep_star_layers[DEEP_STAR_LAYERS] = {
	{ 40.0f, 110, 0.8f, 0.75f },
	{ 130.0f, 170, 1.0f, 0.6f },
	{ 340.0f, 280, 1.3f, 0.45f },
};

static float deep_star_scroll = 0;  // game pixels the deep stars have moved down the screen

static Uint32 hash32(Uint32 x)
{
	x ^= x >> 16;
	x *= 0x7feb352du;
	x ^= x >> 15;
	x *= 0x846ca68bu;
	x ^= x >> 16;
	return x;
}

static float hash_unit(Uint32 x)
{
	return (hash32(x) >> 8) / 16777216.0f;
}

#define STARFIELD_RAMP 0x90  // the game's stars' palette ramp (STARFIELD_HUE)

static void add_deep_star_batch(const L3DFrame *frame, const Camera3D *camera, const float *heights,
                                const Uint32 colors[256], int *instance_count, int *batch_count)
{
	if (frame->star_count == 0 || !settings3d.effects || *batch_count >= MAX_BATCHES)
		return;

	// As fast as the game's slowest stars (2 + starfield_speed pixels a frame).
	static Uint32 scrolled_frame = 0;
	if (scrolled_frame != l3d_frame_number)
	{
		scrolled_frame = l3d_frame_number;
		deep_star_scroll += 2.0f + starfield_speed;
	}
	const float scroll = deep_star_scroll + (2.0f + starfield_speed) * ahead;
	const float twinkle_time = (l3d_frame_number + ahead) / 35.0f;

	const int first = *instance_count;
	const float ground = heights[frame->star_layer] - stars_below_layer();
	for (int k = 0; k < DEEP_STAR_LAYERS; ++k)
	{
		const float height = ground - deep_star_layers[k].depth * rgpu_camera.height_scale;
		float rect[4];
		plane_footprint_world(camera, height, -BACKGROUND_AHEAD, rect);
		if (rect[0] > rect[2] || rect[1] >= rect[3])
			continue;
		const float w = rect[2] - rect[0], h = rect[3] - rect[1];
		const float size = deep_star_layers[k].size;
		for (int i = 0; i < deep_star_layers[k].count && *instance_count < MAX_INSTANCES; ++i)
		{
			const Uint32 seed = (Uint32)(k * 7919 + i) * 4u;
			const float x = rect[0] + hash_unit(seed) * w;
			const float z = rect[1] + fmodf(hash_unit(seed + 1) * h + scroll, h);
			const float scale = size * (0.6f + 0.8f * hash_unit(seed + 2));

			Mat4 transform = mat4_identity();
			transform.m[0] = transform.m[10] = scale;
			transform.m[12] = x - scale / 2;
			transform.m[13] = height;
			transform.m[14] = z - scale / 2;
			float *instance = instances + *instance_count * 24;
			write_instance_world(instance, &transform, 1.0f);

			const float shade = SDL_clamp(deep_star_layers[k].brightness + 0.35f * (hash_unit(seed + 3) - 0.5f), 0.2f, 1.0f);
			const float twinkle = 0.8f + 0.2f * sinf(twinkle_time * (1.5f + 3.0f * hash_unit(seed + 2)) + 6.28f * hash_unit(seed + 3));
			const Uint8 *rgba = (const Uint8 *)&colors[STARFIELD_RAMP | (int)(shade * 15.0f + 0.5f)];
			for (int c = 0; c < 3; ++c)
				instance[16 + c] = srgb_to_linear(rgba[c]) * twinkle;
			++*instance_count;
		}
	}
	if (*instance_count == first)
		return;

	BTBHGPUSceneGeometryBatch *b = &batches[(*batch_count)++];
	init_batch(b);
	b->kind = BTBH_GPU_SCENE_GEOMETRY_CUSTOM_MESH;
	b->custom_mesh = quad_mesh;
	b->first_instance = first;
	b->instance_count = *instance_count - first;
	b->albedo_texture = white_texture;
	b->unlit_enabled = 1;
}

// Appends the starfield outside the playfield (inside it, the captured layer has the stars).
// A composed background 1 has the stars in it already.
static void add_star_batch(const L3DFrame *frame, const bool *composed, const Camera3D *camera,
                           const float *heights, const Uint32 colors[256], int *instance_count, int *batch_count)
{
	if (frame->star_count == 0 || *batch_count >= MAX_BATCHES)
		return;
	for (int i = 0; i < frame->background_count; ++i)
		if (composed[i] && frame->backgrounds[i].layer == frame->star_layer)
			return;

	const float height = heights[frame->star_layer] - stars_below_layer();
	float rect[4];
	plane_footprint(camera, height, rect);
	if (rect[0] > rect[2])
		return;

	static B3DStar stars[MAX_STARS];
	const int count = b3d_collect_stars(frame, rect[0], rect[1], rect[2], rect[3], stars,
	                                    SDL_min(MAX_STARS, MAX_INSTANCES - *instance_count));
	if (count == 0)
		return;

	for (int s = 0; s < count; ++s)
	{
		Mat4 transform = mat4_identity();
		transform.m[12] = stars[s].x;
		transform.m[13] = height;
		transform.m[14] = stars[s].z;
		float *instance = instances + (*instance_count + s) * 24;
		write_instance(instance, &transform, 1.0f);
		const Uint8 *rgba = (const Uint8 *)&colors[stars[s].color];
		for (int c = 0; c < 3; ++c)
			instance[16 + c] = srgb_to_linear(rgba[c]);
	}

	BTBHGPUSceneGeometryBatch *b = &batches[(*batch_count)++];
	init_batch(b);
	b->kind = BTBH_GPU_SCENE_GEOMETRY_CUSTOM_MESH;
	b->custom_mesh = quad_mesh;
	b->first_instance = *instance_count;
	b->instance_count = count;
	b->albedo_texture = white_texture;
	b->unlit_enabled = 1;
	*instance_count += count;
}

/* --- Environment ------------------------------------------------------------------------------ */

// What the models are lit by besides the sun, and reflect (BTBH's procedural sky IBL): a light
// sky above, a dark ground below. Neutral, so that the models' colours stay the sprites' colours.
// Linear colours.
static const float sky_top[3] = { 0.52f, 0.52f, 0.54f };
static const float sky_horizon[3] = { 0.46f, 0.46f, 0.46f };
static const float ground_horizon[3] = { 0.26f, 0.24f, 0.22f };
static const float ground_bottom[3] = { 0.14f, 0.13f, 0.12f };

// The sky's radiance in a direction, as the model shader computes it (sample_procedural_sky,
// without the sun's disc; both gradient curves are 1).
static void sky_radiance(const float d[3], float out[3])
{
	const float angle = acosf(SDL_clamp(d[1], -1.0f, 1.0f));
	const float half_pi = (float)M_PI / 2;
	const float t = d[1] >= 0 ? 1 - angle / half_pi : (angle - half_pi) / half_pi;
	for (int c = 0; c < 3; ++c)
		out[c] = d[1] >= 0 ? sky_horizon[c] + (sky_top[c] - sky_horizon[c]) * t
		                   : ground_horizon[c] + (ground_bottom[c] - ground_horizon[c]) * t;
}

// The sky's irradiance in the shader's SH9 basis (evaluate_irradiance_sh): the radiance projected
// onto the basis and convolved with the cosine lobe, divided by pi as the shader multiplies the
// irradiance by the albedo directly.
static void sky_irradiance_sh(float sh[27])
{
	memset(sh, 0, 27 * sizeof(float));
	const int rows = 64, columns = 128;
	const float band[9] = { 1, 2.0f / 3, 2.0f / 3, 2.0f / 3, 0.25f, 0.25f, 0.25f, 0.25f, 0.25f };
	for (int i = 0; i < rows; ++i)
	{
		const float theta = (float)M_PI * (i + 0.5f) / rows;
		const float d_area = (float)(M_PI / rows) * (float)(2 * M_PI / columns) * sinf(theta);
		for (int j = 0; j < columns; ++j)
		{
			const float phi = 2 * (float)M_PI * (j + 0.5f) / columns;
			const float d[3] = { sinf(theta) * cosf(phi), cosf(theta), sinf(theta) * sinf(phi) };
			const float x = d[0], y = d[1], z = d[2];
			const float basis[9] = {
				0.2820948f, 0.48860252f * y, 0.48860252f * z, 0.48860252f * x, 1.0925485f * x * y,
				1.0925485f * y * z, 0.31539157f * (3 * z * z - 1), 1.0925485f * x * z, 0.54627424f * (x * x - y * y),
			};
			float radiance[3];
			sky_radiance(d, radiance);
			for (int k = 0; k < 9; ++k)
				for (int c = 0; c < 3; ++c)
					sh[k * 3 + c] += radiance[c] * basis[k] * d_area * band[k];
		}
	}
}

static void set_environment(BTBHGPUSceneLighting *lighting)
{
	static float sh[27];
	static bool sh_ready = false;
	if (!sh_ready)
	{
		sky_irradiance_sh(sh);
		sh_ready = true;
	}
	lighting->ibl_enabled = 1;
	memcpy(lighting->irradiance_sh, sh, sizeof(sh));
	lighting->sky_top_red = sky_top[0];
	lighting->sky_top_green = sky_top[1];
	lighting->sky_top_blue = sky_top[2];
	lighting->sky_horizon_red = sky_horizon[0];
	lighting->sky_horizon_green = sky_horizon[1];
	lighting->sky_horizon_blue = sky_horizon[2];
	lighting->ground_horizon_red = ground_horizon[0];
	lighting->ground_horizon_green = ground_horizon[1];
	lighting->ground_horizon_blue = ground_horizon[2];
	lighting->ground_bottom_red = ground_bottom[0];
	lighting->ground_bottom_green = ground_bottom[1];
	lighting->ground_bottom_blue = ground_bottom[2];
	// Reflections of the sky stay dim: the sprites show highlights from the sun, not a mirrored
	// sky, which would grey dark colours. (The irradiance above is the full sky's.)
	lighting->sky_energy = lighting->ground_energy = 0.3f;
	lighting->sky_horizon_curve = lighting->ground_horizon_curve = 1.0f;
	lighting->sun_curve = 1.0f;  // the sun's disc is off (sun_energy 0): the directional light is the sun
}

/*
 * Spotlight levels (starShowVGASpecialCode 2): the game darkens the playfield outside a cone of
 * light that opens up the screen from the player's ship (JE_starShowVGA): inside it full
 * brightness, then an edge 5 pixels wide, and elsewhere a quarter of each colour's shade. The 3D
 * view darkens the whole window the same way with a black overlay, in playfield pixels.
 */
static void build_spotlight(const Layout3D *layout, float window_w, float window_h)
{
	const float scale = layout->playfield[2] / L3D_PLAYFIELD_W;
	const float apex_x = player[0].x - 17.0f;  // playfield column and row of the cone's apex
	const float apex_y = player[0].y + 12.0f;
	for (int j = 0; j < SPOT_H; ++j)
	{
		const float row = ((j + 0.5f) * window_h / SPOT_H - layout->playfield[1]) / scale;
		for (int i = 0; i < SPOT_W; ++i)
		{
			const float column = ((i + 0.5f) * window_w / SPOT_W - layout->playfield[0]) / scale;
			const float outside = fabsf(column - apex_x) - (apex_y - row);  // pixels outside the cone
			float brightness = 0.25f;
			if (row <= apex_y && outside < 0)
				brightness = 1.0f;
			else if (row <= apex_y && outside < 5)
				brightness = 0.25f + 0.5f * (5 - outside) / 5;
			const Uint8 rgba[4] = { 0, 0, 0, (Uint8)(255 * (1 - brightness)) };
			memcpy(&spot_rgba[j * SPOT_W + i], rgba, sizeof(rgba));
		}
	}
	btbh_gpu_texture_update_rgba8(spot_texture, (const uint8_t *)spot_rgba, 0, 0, SPOT_W, SPOT_H);
}

// Appends the particles (particles3d.h): glowing ones added to what is behind them, smoke blended.
static void add_particle_batches(int *instance_count, int *batch_count)
{
	for (int kind = 0; kind < P3D_KIND_COUNT && *batch_count < MAX_BATCHES; ++kind)
	{
		const int first = *instance_count;
		for (int i = 0; i < p3d_particle_count && *instance_count < MAX_INSTANCES; ++i)
		{
			const P3DParticle *p = &p3d_particles[i];
			if (p->kind != kind || p->age < 0)
				continue;
			float t = SDL_clamp(p->age / p->life, 0.0f, 1.0f);
			if (kind == P3D_FIRE)
				t *= t;  // fire stays hot, then cools quickly
			Mat4 transform = mat4_identity();
			transform.m[0] = transform.m[5] = transform.m[10] = p->size;
			if (kind == P3D_RING)
			{
				// Lying on the ground: the quad's up along the screen's down.
				transform.m[5] = 0;
				transform.m[6] = p->size;
			}
			else if (kind != P3D_GLOW)
			{
				// Puffs turned each their own way (their life is their own random number), slowly turning.
				const float angle = p->life * 2.39996f + (p->age + ahead) * 0.02f;
				transform.m[0] = cosf(angle) * p->size;
				transform.m[1] = sinf(angle) * p->size;
				transform.m[4] = -sinf(angle) * p->size;
				transform.m[5] = cosf(angle) * p->size;
			}
			const float age = SDL_max(0.0f, SDL_min(ahead, p->age + ahead));  // not before it appears
			transform.m[12] = p->x + p->vx * age;
			transform.m[13] = SDL_max(0.0f, p->height + p->vheight * age) * rgpu_camera.height_scale +
			                  (p->air ? l3d_terrain_headroom : terrain_lift(p->x, p->y));
			transform.m[14] = p->y + (p->vy + explodeMove) * age;
			float *instance = instances + *instance_count * 24;
			write_instance(instance, &transform, 1.0f);
			for (int c = 0; c < 3; ++c)
				instance[16 + c] = srgb_to_linear((Uint8)(p->color[c] + (p->end_color[c] - p->color[c]) * t));
			instance[19] = (p->color[3] + (p->end_color[3] - p->color[3]) * t) / 255.0f;
			++*instance_count;
		}
		if (*instance_count == first)
			continue;

		BTBHGPUSceneGeometryBatch *b = &batches[(*batch_count)++];
		init_batch(b);
		b->kind = BTBH_GPU_SCENE_GEOMETRY_CUSTOM_MESH;
		b->custom_mesh = billboard_mesh;
		b->first_instance = first;
		b->instance_count = *instance_count - first;
		b->albedo_texture = kind == P3D_RING ? ring_texture : kind == P3D_GLOW ? particle_texture : fire_texture;
		b->billboard_mode = kind == P3D_RING ? BTBH_GPU_SCENE_BILLBOARD_DISABLED : BTBH_GPU_SCENE_BILLBOARD_FRONT;
		b->unlit_enabled = 1;
		b->transparency_enabled = 1;
		b->blend_mode = kind == P3D_SMOKE ? BTBH_GPU_SCENE_BLEND_ALPHA : BTBH_GPU_SCENE_BLEND_ADDITIVE;
		// Fire and light aren't cut by the ground or the models they burst against (as the game
		// draws explosions over everything); smoke is.
		if (kind != P3D_SMOKE)
			b->depth_compare = BTBH_GPU_SCENE_DEPTH_ALWAYS;
	}
}

// Shots and items glow (L3DGlow): additive light around each, in its colour, a little above its
// layer.

static void add_glow_batch(const L3DFrame *frame, const Uint32 colors[256], int *instance_count, int *batch_count)
{
	const int first = *instance_count;
	for (int g = 0; g < frame->glow_count && *instance_count < MAX_INSTANCES; ++g)
	{
		const L3DGlow *glow = &frame->glows[g];
		Mat4 transform = mat4_identity();
		transform.m[0] = transform.m[5] = transform.m[10] = glow->size;
		transform.m[12] = glow->x + glow->vx * ahead;
		transform.m[13] = l3d_layer_height(glow->layer) * rgpu_camera.height_scale + 0.5f;
		transform.m[14] = glow->y + glow->vy * ahead;
		float *instance = instances + *instance_count * 24;
		write_instance(instance, &transform, 1.0f);
		const Uint8 *c = (const Uint8 *)&colors[glow->color];
		for (int i = 0; i < 3; ++i)
			instance[16 + i] = srgb_to_linear(c[i]) * glow->strength;
		instance[19] = 1.0f;
		++*instance_count;
	}
	if (*instance_count == first || *batch_count >= MAX_BATCHES)
		return;

	BTBHGPUSceneGeometryBatch *b = &batches[(*batch_count)++];
	init_batch(b);
	b->kind = BTBH_GPU_SCENE_GEOMETRY_CUSTOM_MESH;
	b->custom_mesh = billboard_mesh;
	b->first_instance = first;
	b->instance_count = *instance_count - first;
	b->albedo_texture = particle_texture;
	b->billboard_mode = BTBH_GPU_SCENE_BILLBOARD_FRONT;
	b->unlit_enabled = 1;
	b->transparency_enabled = 1;
	b->blend_mode = BTBH_GPU_SCENE_BLEND_ADDITIVE;
}

// The scene's point lights: the explosions' (particles3d.h) and the glows of shots and other
// lit things (their sprites' colour, a little above them, reaching the ground), the most
// important of them (energy times reach) up to the fork's limit, placed as everything else on
// their plane (aligned). Shots light the ground and the models they pass, with the ground's
// relief (see set_glints).
#define GLOW_LIGHT_ENERGY 2.4f   // per unit of the glow's strength
#define GLOW_LIGHT_LOW 0.35f     // the light at this fraction of the glow's height (under it: it lights the
                                 // ground, not the shot's own model, seen from above)
#define GLOW_LIGHT_REACH 2.6f    // the light reaches this many glow diameters beyond the ground below it

typedef struct
{
	float position[3], radius, color[3], energy;
} PointLight;

static void add_explosion_lights(BTBHGPUSceneLighting *lighting, const L3DFrame *frame, const Uint32 colors[256],
                                 bool glow_lights)
{
	enum { MAX_CANDIDATES = 512 };
	static PointLight candidates[MAX_CANDIDATES];
	static float importance[MAX_CANDIDATES];
	int candidate_count = 0;

	for (int i = 0; i < p3d_light_count && candidate_count < MAX_CANDIDATES; ++i)
	{
		const P3DLight *l = &p3d_lights[i];
		const float energy = p3d_light_energy(l, ahead);
		if (energy <= 0.02f)
			continue;
		const float height = l->height * rgpu_camera.height_scale + (l->air ? l3d_terrain_headroom : terrain_lift(l->x, l->y));
		const float k = align_scale(height);
		PointLight *out = &candidates[candidate_count];
		out->position[0] = align.on ? align.cx + (l->x - align.cx) * k : l->x;
		out->position[1] = height;
		const float y = l->y + explodeMove * ahead;
		out->position[2] = align.on ? align.cz + (y - align.cz) * k : y;
		out->radius = l->radius * k;
		for (int c = 0; c < 3; ++c)
			out->color[c] = l->color[c] / 255.0f;
		out->energy = energy;
		importance[candidate_count++] = energy * l->radius * 4.0f;  // explosions first
	}

	for (int g = 0; glow_lights && g < frame->glow_count && candidate_count < MAX_CANDIDATES; ++g)
	{
		const L3DGlow *glow = &frame->glows[g];
		if (glow->strength <= 0.05f || glow->size <= 1.0f)
			continue;
		const float height = l3d_layer_height(glow->layer) * rgpu_camera.height_scale * GLOW_LIGHT_LOW;
		const float k = align_scale(height);
		const float x = glow->x + glow->vx * ahead, y = glow->y + glow->vy * ahead;
		PointLight *out = &candidates[candidate_count];
		out->position[0] = align.on ? align.cx + (x - align.cx) * k : x;
		out->position[1] = height;
		out->position[2] = align.on ? align.cz + (y - align.cz) * k : y;
		out->radius = (height + glow->size * GLOW_LIGHT_REACH) * k;
		const Uint8 *c = (const Uint8 *)&colors[glow->color];
		// The sprite's colour, saturated a little (a dark red shot still throws red light).
		const float peak = SDL_max(SDL_max(c[0], c[1]), SDL_max(c[2], 1));
		for (int i = 0; i < 3; ++i)
			out->color[i] = c[i] / peak;
		out->energy = glow->strength * GLOW_LIGHT_ENERGY;
		importance[candidate_count++] = out->energy * glow->size;
	}

	// The most important, in order.
	int count = 0;
	int chosen[BTBH_GPU_SCENE_POINT_LIGHTS];
	for (int i = 0; i < candidate_count; ++i)
	{
		int at = count < BTBH_GPU_SCENE_POINT_LIGHTS ? count : BTBH_GPU_SCENE_POINT_LIGHTS - 1;
		if (count == BTBH_GPU_SCENE_POINT_LIGHTS && importance[i] <= importance[chosen[at]])
			continue;
		while (at > 0 && importance[chosen[at - 1]] < importance[i])
		{
			chosen[at] = chosen[at - 1];
			--at;
		}
		chosen[at] = i;
		if (count < BTBH_GPU_SCENE_POINT_LIGHTS)
			++count;
	}
	for (int n = 0; n < count; ++n)
	{
		const PointLight *l = &candidates[chosen[n]];
		float *out = lighting->point_lights[n];
		memcpy(out, l->position, 3 * sizeof(float));
		out[3] = l->radius;
		memcpy(out + 4, l->color, 3 * sizeof(float));
		out[7] = l->energy;
	}
	lighting->point_light_count = (uint32_t)count;
	if (SDL_getenv("TYR3D_LOG_LIGHTS") != NULL && ahead == 0)
	{
		printf("lights: %d candidates (%d glows in the frame), %d used:", candidate_count, frame->glow_count, count);
		for (int n = 0; n < SDL_min(count, 6); ++n)
		{
			const float *o = lighting->point_lights[n];
			printf(" [%.0f,%.0f,%.0f r%.0f e%.2f]", o[0], o[1], o[2], o[3], o[7]);
		}
		printf("\n");
	}

	// TYR3D_TEST_LIGHT=<x>,<y>,<height>,<radius>,<energy>: one more light, to check the lighting.
	const char *test = SDL_getenv("TYR3D_TEST_LIGHT");
	float t[5];
	if (test != NULL && count < BTBH_GPU_SCENE_POINT_LIGHTS &&
	    sscanf(test, "%f,%f,%f,%f,%f", &t[0], &t[1], &t[2], &t[3], &t[4]) == 5)
	{
		const float k = align_scale(t[2]);
		float *out = lighting->point_lights[count];
		out[0] = align.on ? align.cx + (t[0] - align.cx) * k : t[0];
		out[1] = t[2];
		out[2] = align.on ? align.cz + (t[1] - align.cz) * k : t[1];
		out[3] = t[3] * k;
		out[4] = 1.0f;
		out[5] = 0.6f;
		out[6] = 0.25f;
		out[7] = t[4];
		lighting->point_light_count = (uint32_t)count + 1;
	}
}

static bool shadows_enabled(void)
{
	return settings3d.shadows;
}

// The sun's shadow map covers the ground the window shows around the playfield (an orthographic
// view along the sun's light; further away nothing is shadowed).
#define SHADOW_REACH_UP 160.0f    // game pixels above the playfield's top edge
#define SHADOW_REACH_SIDE 120.0f  // and beside it

static void shadow_view_projection(const Camera3D *camera, float out[16])
{
	float rect[4];
	plane_footprint_world(camera, 0.0f, -BACKGROUND_AHEAD, rect);
	rect[0] = SDL_max(rect[0], L3D_PLAYFIELD_X - SHADOW_REACH_SIDE);
	rect[2] = SDL_min(rect[2], L3D_PLAYFIELD_X + L3D_PLAYFIELD_W + SHADOW_REACH_SIDE);
	rect[1] = SDL_max(rect[1], -SHADOW_REACH_UP);
	rect[3] = SDL_min(rect[3], L3D_PLAYFIELD_H + SHADOW_REACH_SIDE);
	const float centre[3] = { (rect[0] + rect[2]) / 2, 0.0f, (rect[1] + rect[3]) / 2 };
	const float radius = 0.5f * sqrtf((rect[2] - rect[0]) * (rect[2] - rect[0]) + (rect[3] - rect[1]) * (rect[3] - rect[1]));

	const float length = sqrtf(sun_direction[0] * sun_direction[0] + sun_direction[1] * sun_direction[1] +
	                           sun_direction[2] * sun_direction[2]);
	const float forward[3] = { sun_direction[0] / length, sun_direction[1] / length, sun_direction[2] / length };
	// right = normalize(hint x forward), up = forward x right, with the hint pointing up the screen.
	const float hint[3] = { 0.0f, 0.0f, -1.0f };
	float right[3] = {
		hint[1] * forward[2] - hint[2] * forward[1],
		hint[2] * forward[0] - hint[0] * forward[2],
		hint[0] * forward[1] - hint[1] * forward[0],
	};
	const float right_length = sqrtf(right[0] * right[0] + right[1] * right[1] + right[2] * right[2]);
	for (int i = 0; i < 3; ++i)
		right[i] /= right_length;
	const float up[3] = {
		forward[1] * right[2] - forward[2] * right[1],
		forward[2] * right[0] - forward[0] * right[2],
		forward[0] * right[1] - forward[1] * right[0],
	};

	const float depth = 400.0f;  // from the eye to the centre, along the light
	float eye[3];
	for (int i = 0; i < 3; ++i)
		eye[i] = centre[i] - forward[i] * depth;

	Mat4 view = mat4_identity();
	float dots[3] = { 0, 0, 0 };
	for (int i = 0; i < 3; ++i)
	{
		view.m[i * 4 + 0] = right[i];
		view.m[i * 4 + 1] = up[i];
		view.m[i * 4 + 2] = forward[i];
		view.m[i * 4 + 3] = 0;
		dots[0] += right[i] * eye[i];
		dots[1] += up[i] * eye[i];
		dots[2] += forward[i] * eye[i];
	}
	view.m[12] = -dots[0];
	view.m[13] = -dots[1];
	view.m[14] = -dots[2];
	view.m[15] = 1;

	const float near_plane = 0.0f, far_plane = 2 * depth;
	Mat4 projection = { { 0 } };
	projection.m[0] = 1.0f / radius;
	projection.m[5] = 1.0f / radius;
	projection.m[10] = 1.0f / (far_plane - near_plane);
	projection.m[14] = -near_plane / (far_plane - near_plane);
	projection.m[15] = 1.0f;

	const Mat4 result = mat4_mul(&projection, &view);
	memcpy(out, result.m, sizeof(result.m));
}

// The sun and the sky: models are lit by them; layers and volumetric sprites are unlit. The sun is
// strong against the sky, as in the sprites' own shading: lit from the upper left, with clear
// highlights and shadows.
static void scene_lighting(BTBHGPUSceneLighting *lighting, const Camera3D *camera, bool shadows)
{
	memset(lighting, 0, sizeof(*lighting));
	lighting->spot_falloff = 1.0f;
	lighting->spot_inner_cutoff = 0.92388f;
	lighting->spot_outer_cutoff = 0.70711f;
	lighting->spot_range = 50.0f;
	lighting->ambient_red = 0.55f;
	lighting->ambient_green = 0.58f;
	lighting->ambient_blue = 0.68f;
	lighting->ambient_energy = 0.6f;
	const float *sun = sun_direction;
	const float sun_length = sqrtf(sun[0] * sun[0] + sun[1] * sun[1] + sun[2] * sun[2]);
	lighting->directional_x = sun[0] / sun_length;
	lighting->directional_y = sun[1] / sun_length;
	lighting->directional_z = sun[2] / sun_length;
	lighting->directional_energy = SUN_ENERGY;
	lighting->directional_red = 1.0f;
	lighting->directional_green = 0.98f;
	lighting->directional_blue = 0.94f;
	set_environment(lighting);
	const char *energies = SDL_getenv("TYR3D_LIGHTING");
	float sky_fill = SKY_FILL;
	if (energies != NULL)
		sscanf(energies, "%f,%f", &lighting->directional_energy, &sky_fill);
	for (int i = 0; i < 27; ++i)
		lighting->irradiance_sh[i] *= sky_fill;
	if (shadows)
	{
		lighting->directional_shadow_enabled = 1;
		lighting->directional_shadow_softness = 1.0f;
		shadow_view_projection(camera, lighting->directional_shadow_view_projection);
	}
}

// Tone mapping, bloom, the render scale and anti-aliasing.
static void scene_post(BTBHGPUScenePost *post, const BTBHGPUWindowReport *window_frame, Uint32 *render_w, Uint32 *render_h)
{
	memset(post, 0, sizeof(*post));
	post->tonemap_mode = BTBH_GPU_SCENE_TONEMAP_REINHARD;
	post->tonemap_white = 1.0f;
	post->exposure = 1.0f;
	post->contrast = 1.0f;
	post->saturation = 1.0f;
	post->blur_curve = 1.0f;
	post->focus_half_width = 0.05f;
	post->focus_point_x = 0.5f;
	post->focus_point_y = 0.55f;
	post->focus_direction_x = 1.0f;
	post->highlight_threshold = 0.7f;
	if (settings3d.effects)
	{
		post->bloom_intensity = bloom_parameters[0];
		post->bloom_threshold = bloom_parameters[1];
		post->bloom_knee = bloom_parameters[2];
		post->bloom_radius = bloom_parameters[3];
	}

	// The scene is rendered at the window's size in points (on a high-density display, half its
	// pixels each way) and scaled up to the window: at 4K the GPU couldn't show a frame on every
	// refresh, and the game's art is 320x200 anyway. The HUD is drawn at full resolution.
	// TYR3D_RENDER_SCALE=<0.25..1> sets the scale of the window's pixels instead.
	static float scale_override = -1;
	if (scale_override < 0)
	{
		const char *value = SDL_getenv("TYR3D_RENDER_SCALE");
		scale_override = value != NULL ? SDL_clamp((float)SDL_atof(value), 0.25f, 1.0f) : 0;
	}
	const float render_scale = scale_override > 0 ? scale_override
		: SDL_min(1.0f, (float)window_frame->logical_width / (float)window_frame->drawable_width);
	*render_w = SDL_max(1u, (Uint32)(window_frame->drawable_width * render_scale + 0.5f));
	*render_h = SDL_max(1u, (Uint32)(window_frame->drawable_height * render_scale + 0.5f));
	post->upscale_mode = BTBH_GPU_SCENE_UPSCALE_LANCZOS;
	// SMAA (high) smooths the models' edges; the pixel art keeps its look (TYR3D_AA=0 off, 1 SMAA
	// low, 2 high, 3 FXAA).
	static int anti_aliasing = -1;
	if (anti_aliasing < 0)
		anti_aliasing = SDL_getenv("TYR3D_AA") != NULL ? SDL_clamp(SDL_atoi(SDL_getenv("TYR3D_AA")), 0, 3) : 2;
	post->anti_aliasing = (Uint8)anti_aliasing;
}

static void present_3d(const SDL_Surface *hud, const L3DFrame *frame, const SDL_Rect *dst)
{
	BTBHGPUWindowReport window_frame;
	if (!begin_frame(&window_frame))
		return;

	Uint32 colors[256];
	frame_colors(frame, colors);

	// A frame the game has just captured, or one of those shown between ticks (rgpu_present_3d_ahead),
	// which reuse what was made of the frame.
	static Uint32 presented_frame = 0;
	const bool new_frame = presented_frame != l3d_frame_number || (ahead == 0 && !menu.on);
	b3d_clouds = clouds_enabled();  // blended backgrounds of clouds aren't composed
	cloud_frame = frame;
	{
		// The backgrounds as terrain where their maps have one. The ground: in its colours (a filter
		// as its colours, without its waver), over stars only with holes for them to show through;
		// the backgrounds over it are then their tiles, not composed with it (the blended background 2
		// in the colours the blend gives it). Backgrounds 2 and 3 over a flat ground: as for the relief,
		// not composed nor filtered.
		frame_terrains[1] = m3d_enabled ? b3d_terrain(1) : NULL;
		if (frame_terrains[1] != NULL && frame->star_count > 0 && !frame_terrains[1]->holes)
			frame_terrains[1] = NULL;
		b3d_terrain_ground = frame_terrains[1] != NULL;
		lift_ground = NULL;
		for (int i = 0; i < frame->background_count && frame_terrains[1] != NULL; ++i)
			if (frame->backgrounds[i].set == 1)
				lift_ground = &frame->backgrounds[i];
		b3d_solids = m3d_enabled;
		bool composed_now[L3D_MAX_BACKGROUNDS];
		b3d_composed_backgrounds(frame, composed_now);
		bool ok[B3D_SETS + 1] = { false, true, m3d_enabled, m3d_enabled };
		for (int i = 0; i < frame->background_count; ++i)
		{
			const int set = frame->backgrounds[i].set;
			if (set >= 2 && set <= B3D_SETS)
				ok[set] = ok[set] && !composed_now[i] && frame->backgrounds[i].effect_count == 0;
		}
		bool any = frame_terrains[1] != NULL;
		for (int set = 2; set <= B3D_SETS; ++set)
		{
			frame_terrains[set] = ok[set] ? b3d_terrain(set) : NULL;
			any |= frame_terrains[set] != NULL;
		}
		l3d_terrain_headroom = any ? TERRAIN_HEADROOM : 0.0f;
		if (SDL_getenv("TYR3D_DEBUG_TERRAIN") != NULL)
		{
			printf("terrain debug: ok %d %d %d stars %d ->", ok[1], ok[2], ok[3], frame->star_count);
			for (int i = 0; i < frame->background_count; ++i)
				printf(" [set %d blend %d effects %d layer %s composed %d]", frame->backgrounds[i].set, frame->backgrounds[i].blend,
				       frame->backgrounds[i].effect_count, l3d_layer_name(frame->layers[frame->backgrounds[i].layer].type),
				       composed_now[i]);
			printf("\n");
		}
		memset(terrain_batch, 0, sizeof(terrain_batch));
	}
	for (int set = 1; set <= B3D_SETS; ++set)  // the level's water colour, for the procedural water
	{
		Uint8 rgb[3];
		if (b3d_water_color(set, rgb))
		{
			for (int k = 0; k < 3; ++k)
				water_rgb[k] = srgb_to_linear(rgb[k]);
			break;
		}
	}
	presented_frame = l3d_frame_number;

	// Layers that background maps were drawn into get the map's tiles beneath them.
	bool native[L3D_MAX_LAYERS] = { false };
	for (int i = 0; i < frame->background_count; ++i)
		native[frame->backgrounds[i].layer] = true;

	static int slot_of_layer[L3D_MAX_LAYERS];
	static int slot_count = 0;
	static float layer_speed[L3D_MAX_LAYERS];
	if (new_frame)
	{
		bool composed_backgrounds[L3D_MAX_BACKGROUNDS];
		bool composed_layer[L3D_MAX_LAYERS] = { false };
		b3d_composed_backgrounds(frame, composed_backgrounds);
		for (int i = 0; i < frame->background_count; ++i)
			composed_layer[frame->backgrounds[i].layer] |= composed_backgrounds[i];
		build_layer_atlas(frame, colors, native, composed_layer, slot_of_layer, &slot_count);
		if (slot_count > 0)
		{
			// (Each layer's rows with pixels, and the row on either side.)
			if (map_filter() == BTBH_GPU_TEXTURE_FILTER_LINEAR)
				for (int l = 0; l < frame->layer_count; ++l)
				{
					const L3DLayer *layer = &frame->layers[l];
					if (slot_of_layer[l] < 0 || layer->max_y <= layer->min_y)
						continue;
					const int first = SDL_max(layer->min_y - 1, 0), last = SDL_min(layer->max_y + 1, ATLAS_SLOT_H);
					bleed_into_clear(atlas_rgba + (size_t)slot_of_layer[l] * ATLAS_SLOT_H * L3D_WIDTH, L3D_WIDTH, first, last - first);
				}
			btbh_gpu_texture_update_rgba8(layer_atlas, (const uint8_t *)atlas_rgba, 0, 0, L3D_WIDTH, slot_count * ATLAS_SLOT_H);
			btbh_gpu_texture_update_rgba8(layer_water, (const uint8_t *)layer_water_rgba, 0, 0, L3D_WIDTH, slot_count * ATLAS_SLOT_H);
		}
		glint_time += 1.0f / 35.0f;  // about the game's frame rate

		// How fast things move on: the maps at their scroll speeds, explosions drift with them.
		background_speed[0] = 0;
		background_speed[1] = backMove;
		background_speed[2] = backMove2;
		background_speed[3] = backMove3;
		for (int set = 0; set < 4; ++set)
			map_scroll[set] += background_speed[set];
		for (int l = 0; l < frame->layer_count; ++l)
			layer_speed[l] = frame->layers[l].type == L3D_EXPLOSION ? explodeMove : 0;
		for (int i = 0; i < frame->background_count; ++i)
			layer_speed[frame->backgrounds[i].layer] = background_speed[frame->backgrounds[i].set & 3];
	}

	const float logical_w = (float)window_frame.logical_width, logical_h = (float)window_frame.logical_height;
	const Layout3D layout = layout_3d(logical_w, logical_h, dst);
	CanvasQuad quads[MAX_CANVAS_QUADS];
	const int quad_count = layout_quads(&layout, dst, quads);
	build_modern_hud(logical_w, logical_h);

	if (new_frame || menu.on)
	{
		build_hud(hud, frame, layout.split);
		btbh_gpu_texture_update_rgba8(screen_texture, (const uint8_t *)screen_rgba, 0, 0, SCREEN_W, SCREEN_H);
		hud_panel_hd(hud);
	}

	// Levels with a special view, as JE_starShowVGA shows them.
	const bool upside_down = starShowVGASpecialCode == 1;
	const bool spotlight = starShowVGASpecialCode == 2 && processorType >= 2;
	if (spotlight && new_frame)
		build_spotlight(&layout, logical_w, logical_h);

	if (slot_count == 0)
	{
		present_canvas(quads, quad_count, spotlight, true, &window_frame);
		return;
	}

	// Playfield rectangle in NDC (y up) of the whole window.
	const float px0 = layout.playfield[0], px1 = layout.playfield[0] + layout.playfield[2];
	const float py0 = layout.playfield[1], py1 = layout.playfield[1] + layout.playfield[3];
	const float ndc_rect[4] = {
		px0 / logical_w * 2 - 1,
		1 - py1 / logical_h * 2,
		px1 / logical_w * 2 - 1,
		1 - py0 / logical_h * 2,
	};
	const float viewport_aspect = (px1 - px0) / (py1 - py0);

	// Layer heights increase in draw order, so depth agrees with the 2D drawing order.
	float heights[L3D_MAX_LAYERS];
	float reference_height = l3d_layer_height(L3D_PLAYER) * rgpu_camera.height_scale;
	for (int l = 0; l < frame->layer_count; ++l)
	{
		float height = l3d_layer_height(frame->layers[l].type) * rgpu_camera.height_scale;
		if (l > 0 && height < heights[l - 1] + LAYER_STEP)
			height = heights[l - 1] + LAYER_STEP;
		heights[l] = height;
	}

	const Camera3D camera = fit_camera(reference_height, viewport_aspect, ndc_rect, upside_down);
	set_alignment(&camera, reference_height);
	shown_view = (ShownView){ true, camera, reference_height, logical_w, logical_h, upside_down };

	int instance_count = 0;
	int batch_count = 0;
	for (int l = 0; l < frame->layer_count; ++l)
	{
		const int slot = slot_of_layer[l];
		if (slot < 0)
			continue;
		// TYR3D_TILES_ONLY: background layers are left out, so only the map's tiles show them.
		static int tiles_only = -1;
		if (tiles_only < 0)
			tiles_only = SDL_getenv("TYR3D_TILES_ONLY") != NULL;
		if (tiles_only && native[l])
			continue;

		Mat4 transform = mat4_identity();
		transform.m[0] = L3D_WIDTH;
		transform.m[10] = L3D_ROWS;
		transform.m[13] = heights[l];
		transform.m[14] = -L3D_OVERSCAN + layer_speed[l] * ahead;
		write_instance(instances + instance_count * 24, &transform, 1.0f);

		// Layers are opaque with an alpha cutoff, so they and the models occlude each other by depth.
		BTBHGPUSceneGeometryBatch *b = &batches[batch_count++];
		init_batch(b);
		b->kind = BTBH_GPU_SCENE_GEOMETRY_CUSTOM_MESH;
		b->custom_mesh = quad_mesh;
		b->first_instance = instance_count++;
		b->instance_count = 1;
		b->albedo_texture = layer_atlas;
		b->uv_scale_y = (float)L3D_ROWS / ATLAS_H;
		b->uv_offset_y = (float)(slot * ATLAS_SLOT_H) / ATLAS_H;
		b->unlit_enabled = 1;
		b->alpha_cutoff = 0.5f;
		if (background_layer(frame->layers[l].type))
			set_glints(b, layer_water);
	}

	bool composed[L3D_MAX_BACKGROUNDS];
	b3d_composed_backgrounds(frame, composed);
	add_composed_batches(frame, composed, &camera, heights, colors, new_frame, &instance_count, &batch_count);
	add_background_batches(frame, composed, &camera, heights, colors, &instance_count, &batch_count);
	add_star_batch(frame, composed, &camera, heights, colors, &instance_count, &batch_count);
	add_deep_star_batch(frame, &camera, heights, colors, &instance_count, &batch_count);
	add_cloud_batches(heights, &camera, new_frame, &instance_count, &batch_count);
	const int first_object_batch = batch_count;
	add_object_batches(frame, colors, upside_down, &instance_count, &batch_count);
	add_volume_batches(frame, &instance_count, &batch_count);

	// Shadows: objects (models and volumetric sprites) cast the sun's shadow; the unlit surfaces
	// (layers, background tiles, volumetric sprites) darken in it, lit models are shaded by it.
	static Uint8 casts_shadow[MAX_BATCHES];
	const bool shadows = shadows_enabled();
	for (int i = 0; i < batch_count; ++i)
	{
		casts_shadow[i] = shadows && (i >= first_object_batch || terrain_batch[i]);
		if (shadows && batches[i].unlit_enabled == 1)
			batches[i].unlit_enabled = 2;
	}

	// Particles last: they neither cast nor receive shadows.
	const int first_particle_batch = batch_count;
	if (settings3d.effects)
	{
		add_particle_batches(&instance_count, &batch_count);
		add_glow_batch(frame, colors, &instance_count, &batch_count);
	}
	for (int i = first_particle_batch; i < batch_count; ++i)
		casts_shadow[i] = 0;

	BTBHGPUSceneLighting lighting;
	scene_lighting(&lighting, &camera, shadows);
	// On spotlight levels the ship carries a lamp: a spot light up the screen through the cone the
	// game leaves lit (the darkness itself is the overlay, build_spotlight), lighting the models in it.
	if (starShowVGASpecialCode == 2 && processorType >= 2)
	{
		const float ship_x = player[0].x + 7.0f, ship_y = player[0].y + 7.0f;
		const float height = l3d_layer_height(L3D_PLAYER) * rgpu_camera.height_scale + 6.0f;
		const float k = align_scale(height);
		lighting.spot_position_x = align.on ? align.cx + (ship_x - align.cx) * k : ship_x;
		lighting.spot_position_y = height;
		lighting.spot_position_z = align.on ? align.cz + (ship_y - align.cz) * k : ship_y;
		// Up the screen and a little down, as the cone (slope 1: 45 degrees each side) opens.
		const float dir[3] = { 0.0f, -0.25f, -1.0f };
		const float length = sqrtf(dir[0] * dir[0] + dir[1] * dir[1] + dir[2] * dir[2]);
		lighting.spot_direction_x = dir[0] / length;
		lighting.spot_direction_y = dir[1] / length;
		lighting.spot_direction_z = dir[2] / length;
		lighting.spot_range = 260.0f;
		lighting.spot_energy = 2.5f;
		lighting.spot_red = 1.0f;
		lighting.spot_green = 0.95f;
		lighting.spot_blue = 0.85f;
		lighting.spot_falloff = 1.0f;
		lighting.spot_inner_cutoff = cosf(38.0f * (float)M_PI / 180.0f);
		lighting.spot_outer_cutoff = cosf(46.0f * (float)M_PI / 180.0f);
	}

	static int explosion_lights = -1;  // TYR3D_EXPLOSION_LIGHTS=0 leaves them out
	if (explosion_lights < 0)
		explosion_lights = SDL_getenv("TYR3D_EXPLOSION_LIGHTS") == NULL || SDL_atoi(SDL_getenv("TYR3D_EXPLOSION_LIGHTS")) != 0;
	static int glow_lights = -1;  // TYR3D_GLOW_LIGHTS=0: shots and other glows don't light their surroundings
	if (glow_lights < 0)
		glow_lights = SDL_getenv("TYR3D_GLOW_LIGHTS") == NULL || SDL_atoi(SDL_getenv("TYR3D_GLOW_LIGHTS")) != 0;
	if (settings3d.effects && explosion_lights)
		add_explosion_lights(&lighting, frame, colors, glow_lights);

	BTBHGPUScenePost post;
	Uint32 render_w, render_h;
	scene_post(&post, &window_frame, &render_w, &render_h);

	BTBHGPUSceneReport scene_report;
	if (btbh_gpu_window_scene_present_instances_with_visibility(window,
	        shader_paths[SH_MODEL_VERT], shader_paths[SH_ANIMATED_MODEL_VERT],
	        shader_paths[SH_SHADOW_FAST_VERT], shader_paths[SH_SHADOW_FAST_FRAG],
	        shader_paths[SH_SHADOW_VERT], shader_paths[SH_ANIMATED_SHADOW_VERT], shader_paths[SH_SHADOW_FRAG],
	        shader_paths[SH_MODEL_FRAG], shader_paths[SH_MODEL_UNSHADOWED_FRAG],
	        shader_paths[SH_POST_VERT], shader_paths[SH_POST_FRAG],
	        shader_format, render_w, render_h,
	        camera.view_projection.m, camera.right, camera.up, camera.position,
	        &lighting, &post, instances, instance_count, instance_count, batches, NULL, casts_shadow, batch_count,
	        0, 0, 0, 255, &scene_report) != BTBH_GPU_OK)
	{
		fprintf(stderr, "warning: scene present failed: %s\n", scene_report.message);
		present_canvas(quads, quad_count, spotlight, true, &window_frame);
		return;
	}

	present_canvas(quads, quad_count, spotlight, false, &window_frame);
}

/* --- The store's ship ---------------------------------------------------------------------- */

/*
 * A box of the store's screen as a scene (see RGPUShowcase): its picture lies on the ground, seen
 * from straight above as the box shows it, models over it lit by the sun and casting their shadows.
 *
 * World: the box spans the playfield's width on the ground (fit_camera with no tilt fits that
 * width exactly at height 0), its bottom on the playfield's bottom edge.
 */
// footprint: world units, or 0 for the model's own size times k (world units per game pixel).
static void add_showcase_model(int model_index, float x, float z, float height, float footprint, float k, float yaw,
                               float pitch, float roll, const Uint32 colors[256], int *instance_count, int *batch_count)
{
	const LoadedModel *loaded = model_index >= 0 && model_index < m3d_model_count ? get_model(model_index) : NULL;
	if (loaded == NULL || loaded->footprint <= 0 || *batch_count >= MAX_BATCHES || *instance_count >= MAX_INSTANCES)
		return;
	const M3DModel *model = &m3d_models[model_index];
	if (footprint <= 0)
		footprint = (model->size > 0 ? model->size : loaded->footprint) * k;
	const Mat4 chain[] = {
		mat4_translation(x, height, z),
		mat4_rotation(1, -yaw),
		mat4_rotation(0, pitch),
		mat4_rotation(2, -roll),
		mat4_rotation(1, model->yaw),
		mat4_rotation(0, model->pitch),
		mat4_rotation(2, model->roll),
		mat4_scaling(footprint / loaded->footprint),
		mat4_translation(-loaded->center[0], -loaded->center[1], -loaded->center[2]),
	};
	const Mat4 transform = mat4_chain((int)COUNTOF(chain), chain);
	const int instance = (*instance_count)++;
	write_instance_world(instances + instance * 24, &transform, 1.0f);

	const uint32_t material_count = loaded->material_count > 0 ? loaded->material_count : 1;
	for (uint32_t m = 0; m < material_count && *batch_count < MAX_BATCHES; ++m)
	{
		BTBHGPUSceneGeometryBatch *b = &batches[(*batch_count)++];
		init_batch(b);
		b->kind = BTBH_GPU_SCENE_GEOMETRY_MODEL;
		b->model = loaded->gpu;
		b->first_instance = instance;
		b->instance_count = 1;
		if (loaded->material_count == 0)
			continue;
		const BTBHGPUModelMaterialInfo *info = &loaded->materials[m];
		b->material_slot = (int32_t)m;
		b->albedo_texture = info->albedo_texture;
		b->albedo_red = info->albedo_red;
		b->albedo_green = info->albedo_green;
		b->albedo_blue = info->albedo_blue;
		b->albedo_alpha = info->albedo_alpha;
		b->normal_texture = info->normal_texture;
		b->orm_texture = info->orm_texture;
		b->normal_scale = info->normal_scale;
		b->occlusion = info->occlusion;
		b->roughness = info->roughness;
		b->metalness = info->metalness;
		b->emission_texture = info->emission_texture;
		b->emission_red = info->emission_red;
		b->emission_green = info->emission_green;
		b->emission_blue = info->emission_blue;
		b->emission_alpha = info->emission_alpha;
		b->emission_energy = info->emission_energy;
		if (loaded->palette_index[m] >= 0)
		{
			const Uint8 *c = (const Uint8 *)&colors[loaded->palette_index[m]];
			b->albedo_red = palette_albedo(c[0]);
			b->albedo_green = palette_albedo(c[1]);
			b->albedo_blue = palette_albedo(c[2]);
		}
		if (b->albedo_alpha < 255)
			b->transparency_enabled = 1;
	}
}

void rgpu_present_showcase(const SDL_Surface *screen, const RGPUShowcase *show, const SDL_Rect *dst)
{
	BTBHGPUWindowReport window_frame;
	if (!begin_frame(&window_frame))
		return;

	// The screen over everything but where it still shows the illustration; the box's picture
	// without the ship beneath.
	const SDL_Rect *p = &show->pane;
	static Uint32 picture[SCREEN_W * SCREEN_H];
	convert_screen(screen, screen_rgba);
	for (int y = 0; y < p->h; ++y)
		for (int x = 0; x < p->w; ++x)
		{
			const int i = (p->y + y) * SCREEN_W + p->x + x;
			picture[y * p->w + x] = rgb_palette[show->backdrop[i]];
			if (((const Uint8 *)screen->pixels)[(p->y + y) * screen->pitch + p->x + x] == show->transparent[i])
				screen_rgba[i] = 0;
		}
	btbh_gpu_texture_update_rgba8(screen_texture, (const uint8_t *)screen_rgba, 0, 0, SCREEN_W, SCREEN_H);
	btbh_gpu_texture_update_rgba8(showcase_texture, (const uint8_t *)picture, 0, 0, p->w, p->h);
	const CanvasQuad quad = whole_screen_quad(dst);
	memcpy(canvas_fade, show->fade, sizeof(canvas_fade));

	// The camera: straight down at the box.
	const float logical_w = (float)window_frame.logical_width, logical_h = (float)window_frame.logical_height;
	const float sx = dst->w / (float)SCREEN_W, sy = dst->h / (float)SCREEN_H;
	const float wx0 = dst->x + p->x * sx, wy0 = dst->y + p->y * sy;
	const float wx1 = wx0 + p->w * sx, wy1 = wy0 + p->h * sy;
	const float ndc_rect[4] = { wx0 / logical_w * 2 - 1, 1 - wy1 / logical_h * 2, wx1 / logical_w * 2 - 1, 1 - wy0 / logical_h * 2 };
	const float tilt = rgpu_camera.tilt_degrees;
	rgpu_camera.tilt_degrees = 0;
	const Camera3D camera = fit_camera(0.0f, (wx1 - wx0) / (wy1 - wy0), ndc_rect, false);
	rgpu_camera.tilt_degrees = tilt;
	shown_view.valid = false;

	const float k = (float)L3D_PLAYFIELD_W / p->w;  // world units per screen pixel
	const float top = L3D_PLAYFIELD_H - p->h * k;
#define SHOWCASE_X(px) (L3D_PLAYFIELD_X + ((px) - p->x) * k)
#define SHOWCASE_Z(py) (top + ((py) - p->y) * k)

	Uint32 colors[256];
	memcpy(colors, rgb_palette, sizeof(colors));
	sync_model_cache();
	int instance_count = 0, batch_count = 0;

	// The picture on the ground.
	{
		Mat4 transform = mat4_identity();
		transform.m[0] = L3D_PLAYFIELD_W;
		transform.m[10] = p->h * k;
		transform.m[12] = L3D_PLAYFIELD_X;
		transform.m[14] = top;
		write_instance_world(instances + instance_count * 24, &transform, 1.0f);
		BTBHGPUSceneGeometryBatch *b = &batches[batch_count++];
		init_batch(b);
		b->kind = BTBH_GPU_SCENE_GEOMETRY_CUSTOM_MESH;
		b->custom_mesh = quad_mesh;
		b->first_instance = instance_count++;
		b->instance_count = 1;
		b->albedo_texture = showcase_texture;
		b->uv_scale_x = (float)p->w / SCREEN_W;
		b->uv_scale_y = (float)p->h / SCREEN_H;
		b->unlit_enabled = 1;
	}

	const int first_model_batch = batch_count;
	for (int i = 0; i < show->object_count; ++i)
	{
		const RGPUShowcaseObject *o = &show->objects[i];
		add_showcase_model(o->model, SHOWCASE_X(o->x), SHOWCASE_Z(o->y), o->height * k, o->size * k, k, o->yaw, o->pitch,
		                   o->roll, colors, &instance_count, &batch_count);
	}
#undef SHOWCASE_X
#undef SHOWCASE_Z

	static Uint8 casts_shadow[MAX_BATCHES];
	const bool shadows = shadows_enabled();
	for (int i = 0; i < batch_count; ++i)
	{
		casts_shadow[i] = shadows && i >= first_model_batch;
		if (shadows && batches[i].unlit_enabled == 1)
			batches[i].unlit_enabled = 2;
	}

	BTBHGPUSceneLighting lighting;
	scene_lighting(&lighting, &camera, shadows);
	BTBHGPUScenePost post;
	Uint32 render_w, render_h;
	scene_post(&post, &window_frame, &render_w, &render_h);

	BTBHGPUSceneReport scene_report;
	const bool drawn = btbh_gpu_window_scene_present_instances_with_visibility(window,
	        shader_paths[SH_MODEL_VERT], shader_paths[SH_ANIMATED_MODEL_VERT],
	        shader_paths[SH_SHADOW_FAST_VERT], shader_paths[SH_SHADOW_FAST_FRAG],
	        shader_paths[SH_SHADOW_VERT], shader_paths[SH_ANIMATED_SHADOW_VERT], shader_paths[SH_SHADOW_FRAG],
	        shader_paths[SH_MODEL_FRAG], shader_paths[SH_MODEL_UNSHADOWED_FRAG],
	        shader_paths[SH_POST_VERT], shader_paths[SH_POST_FRAG],
	        shader_format, render_w, render_h,
	        camera.view_projection.m, camera.right, camera.up, camera.position,
	        &lighting, &post, instances, instance_count, instance_count, batches, NULL, casts_shadow, batch_count,
	        0, 0, 0, 255, &scene_report) == BTBH_GPU_OK;
	if (!drawn)
		fprintf(stderr, "warning: scene present failed: %s\n", scene_report.message);
	present_canvas(&quad, 1, false, !drawn, &window_frame);
	canvas_fade[3] = 0;
}
