/*
 * Tyrian3D: GPU presentation through the BTBH renderer. See render_gpu.h.
 */
#include "render_gpu.h"

#include "background3d.h"
#include "backgrnd.h"
#include "config.h"
#include "debugmode.h"
#include "destruct3d.h"
#include "devtools.h"
#include "jukebox3d.h"
#include "font.h"
#include "fonthand.h"
#include "keyboard.h"
#include "mainint.h"
#include "mouse.h"
#include "player.h"
#include "model_icons.h"
#include "models3d.h"
#include "palette.h"
#include "pcxmast.h"
#include "particles3d.h"
#include "picload.h"
#include "file.h"
#include "paths3d.h"
#include "rogue.h"
#include "settings3d.h"
#include "sprite.h"
#include "text_record.h"
#include "ui.h"
#include "varz.h"
#include "volume3d.h"

#include <btbh_gpu/btbh_gpu.h>

#include "cgltf.h"
#include "pcxmast.h"

#include <zlib.h>

#include <limits.h>
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
// Background tiles sit this far below their layer, so that the captured layer, which is exact
// inside the playfield (filters and all), is drawn over them.
#define TILE_BELOW_LAYER 0.05f

// Background map tiles and starfield pixels drawn per frame, at most.
#define MAX_TILES 6144
#define MAX_STARS 4096
#define DEEP_STARS 720  // the deep starfield's stars, all layers (add_deep_star_batch)
#define NEBULA_PATCHES 6  // the nebula's patches deep under the stars (add_nebula_batch)
#define WEATHER_FLAKES 350  // the weather's flakes or embers (add_weather_batch: WEATHER_BANDS * WEATHER_PER_BAND)
#define MAX_CLOUD_PUFFS 4096  // the clouds' puffs (add_cloud_puffs)
#define MAX_PLANTS 12000      // plants drawn per frame (vegetation)
// Stand-ins for a painting that has no model yet (L3D_STANDIN_PLACEHOLDER): the enemy's own model, this
// much of its height and this bright.
#define STANDIN_SLUMP 0.45f
#define STANDIN_SHADE 0.35f

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
static BTBHGPUTexture *nebula_texture = NULL;    // a patch of nebula (add_nebula_batch)
static BTBHGPUTexture *leaf_texture = NULL;      // a leaf (add_weather_batch's leaves)
static BTBHGPUTexture *gull_texture = NULL;      // a gull seen from above (add_bird_batch)
static BTBHGPUTexture *world_textures[J3D_TEXTURES];  // the distant planets' surfaces, wrapping round (add_planet_batch)
static BTBHGPUCustomMesh *world_mesh = NULL;
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
static void forget_ui_textures(void);
static void forget_model_icons(void);
static void forget_jukebox_scene(void);
static void forget_destruct_scene(void);
static bool present_destruct(void);
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
	BTBHGPUTexture *texture;  // NULL: plain colour
	bool graded;              // the bottom edge in below (left and right are then its top's)
	float below[4];
	bool poly;                // any four corners (px, py) in black of opacities pa (no texture)
	float px[4], py[4], pa[4];
	bool free;                // any four corners as given (the UI's shapes, ui.c), from the texture or not
	BTBHGPUCanvasVertex corner[4];
	bool picture;             // from the screen's picture, sharp where it is magnified (rgpu_ui_picture)
	bool premultiplied;       // the texture's colours are multiplied by its alpha (and so are the quad's: the items'
	                          // icons from their models, rgpu_ui_model_icon)
} HudQuad;

// As many as a frame needs (a help page's letters take two each, the letter and its shadow): the
// room grows when a frame needs more and is kept, so frames don't allocate once the busiest has shown.
#define HUD_QUADS_FIRST 2048
static HudQuad *hud_quads = NULL;
static int hud_quad_count = 0, hud_quad_room = 0;
// The first so many are drawn under the screen's quads rather than over them (the HUD's gauges under a
// menu the game shows over the level).
static int hud_under = 0;

// Room for n more quads after hud_quad_count (false without the memory for them).
static bool hud_quads_room(int n)
{
	if (hud_quad_count + n <= hud_quad_room)
		return true;
	int room = SDL_max(hud_quad_room, HUD_QUADS_FIRST);
	while (room < hud_quad_count + n)
		room *= 2;
	HudQuad *grown = SDL_realloc(hud_quads, sizeof(*grown) * (size_t)room);
	if (grown == NULL)
		return false;
	hud_quads = grown;
	hud_quad_room = room;
	return true;
}

// A new quad after the others (NULL without the memory for it).
static HudQuad *hud_quad_add(void)
{
	return hud_quads_room(1) ? &hud_quads[hud_quad_count++] : NULL;
}
static Uint32 spot_rgba[SPOT_W * SPOT_H];
static Uint32 atlas_rgba[L3D_WIDTH * ATLAS_H];

// Water glints (the renderer's GLINTS surface): masks of the water in the layers and the tiles,
// in the blue channel, laid out as layer_atlas and tile_atlas.
static BTBHGPUTexture *layer_water = NULL;
static BTBHGPUTexture *tile_water = NULL;
static BTBHGPUTexture *composed_water = NULL;
#define CLOUD_TEXELS 512   // canvas size in texels
#define CLOUD_SCALE 3      // game pixels per texel
#define CLOUD_FINE 2       // the texture's texels a canvas texel, each way
#define MAX_CLOUD_CANVASES 2
static BTBHGPUTexture *cloud_texture = NULL;  // CLOUD_TEXELS x CLOUD_TEXELS * MAX_CLOUD_CANVASES, CLOUD_FINE times that
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
	       type == L3D_BG2_OVER || type == L3D_BG3_OVER || type == L3D_BG3_LOW;
}

// Backgrounds' surfaces with the Effects setting: the sun's glints on water (where mask says), and
// a gentle relief from the pixels' brightness that the explosions' lights bring out (a negative
// normal scale, see the fork's shader).
#define BACKGROUND_RELIEF 3.0f

// The level's water colour (linear), for the procedural water.
static float water_rgb[3] = { 0.02f, 0.06f, 0.12f };
static float tile_fade;  // (the palette's fade the tiles are dimmed by: dim_by_fade)
static float filter_dim = 1.0f;  // (and the game's darkening filter, for the water and the clouds: tile_filter_dim the tiles')

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
	// (The water's colour and the sun's highlights fade with the palette and the game's darkening filter as the
	// tiles do: a level starting comes up from dark by the filter, and its water showed at full brightness over
	// dark tiles.)
	const float fade = powf(SDL_clamp(tile_fade, 0.0f, 1.0f), 2.2f) * filter_dim;
	b->surface_parameters0[1] = (SDL_getenv("TYR3D_WATER_SUN") != NULL ? (float)SDL_atof(SDL_getenv("TYR3D_WATER_SUN")) : 1.0f) * fade;  // highlights
	b->surface_parameters0[2] = 900.0f;  // their sharpness
	for (int k = 0; k < 3; ++k)
		b->surface_parameters1[k] = water_rgb[k] * fade;
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
/*
 * HD tiles (b3d_hd_scale): a second atlas texture, hd_scale times larger and laid out the same (its
 * cells, borders and pages scaled), so the tiles' texture coordinates hold for both. Colouring HD
 * pages and terrain rows takes long, so while the frame's colours keep changing (fades, the flare's
 * flicker) the tiles show at their own size, and the HD ones are coloured once the colours have held
 * for a moment, a few a frame (hd_budget).
 */
static int hd_scale = 1;  // the scale tile_atlas_hd has (1: there is none)
static BTBHGPUTexture *tile_atlas_hd = NULL;
static Uint8 *hd_indices = NULL, *hd_opaque = NULL, *hd_ground = NULL;
static Uint32 *hd_rgba = NULL;
static size_t hd_capacity = 0;
static unsigned int hd_generation = 0;  // b3d_map_generation + 1 of hd_indices
static int hd_budget = 0;               // HD terrain rows still to colour this frame (an atlas page takes all)
static int colors_stable = 0;           // frames the frame's colours have held
#define HD_ROWS_PER_FRAME 2             // (a row takes a millisecond or two, a page a few)
#define HD_STABLE_FRAMES 2
static struct
{
	bool valid;
	unsigned int generation;  // b3d_map_generation it was coloured for
	Uint32 colors_hash;
	bool ground_zero;         // colour 0 of background 1 is drawn (a filter recolours it)
	unsigned int used;        // frame it was last used in
	bool hd;                  // tile_atlas_hd's page holds it too
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

// Value noise for the nebula (its own hash: the renderer's comes later), wrapping every `period` cells.
static float nebula_noise(float x, float y, int period, Uint32 seed)
{
	const int xi = (int)floorf(x), yi = (int)floorf(y);
	const float fx = x - xi, fy = y - yi;
	const float ux = fx * fx * (3 - 2 * fx), uy = fy * fy * (3 - 2 * fy);
	float c[4];
	for (int k = 0; k < 4; ++k)
	{
		Uint32 h = (Uint32)((((xi + (k & 1)) % period + period) % period) * 7919 + (((yi + (k >> 1)) % period + period) % period) * 104729) ^ seed;
		h ^= h >> 16;
		h *= 0x7feb352du;
		h ^= h >> 15;
		h *= 0x846ca68bu;
		h ^= h >> 16;
		c[k] = (h >> 8) / 16777216.0f;
	}
	const float top = c[0] + (c[1] - c[0]) * ux, bottom = c[2] + (c[3] - c[2]) * ux;
	return top + (bottom - top) * uy;
}

static float nebula_fbm(float x, float y, int period, Uint32 seed)
{
	float sum = 0, amp = 1, total = 0;
	for (int o = 0, f = 1; o < 5; ++o, f *= 2)
	{
		sum += nebula_noise(x * f, y * f, period * f, seed + (Uint32)o) * amp;
		total += amp;
		amp *= 0.5f;
	}
	return sum / total;
}

// A patch of nebula: wispy gas with brighter filaments, fading out towards a ragged edge (white: the
// instances colour it; alpha its density).
static BTBHGPUTexture *create_nebula_texture(void)
{
	enum { SIZE = 256 };
	static Uint32 pixels[SIZE * SIZE];
	for (int y = 0; y < SIZE; ++y)
		for (int x = 0; x < SIZE; ++x)
		{
			const float u = (x + 0.5f) / SIZE, v = (y + 0.5f) / SIZE;
			const float gas = nebula_fbm(u * 4, v * 4, 4, 11u);
			const float ridge = 1 - fabsf(2 * nebula_fbm(u * 3 + gas, v * 3 - gas, 3, 23u) - 1);
			const float density = 0.65f * gas + 0.35f * ridge * ridge * ridge;
			const float dx = u * 2 - 1, dy = v * 2 - 1;
			const float r = sqrtf(dx * dx + dy * dy) * (0.8f + 0.4f * nebula_fbm(u * 3, v * 3, 3, 37u));
			const float edge = 1 - SDL_clamp((r - 0.35f) / 0.6f, 0.0f, 1.0f);
			const float a = SDL_clamp((density - 0.3f) / 0.45f, 0.0f, 1.0f) * edge * edge * (3 - 2 * edge);
			const Uint8 rgba[4] = { 255, 255, 255, (Uint8)(255 * a) };
			memcpy(&pixels[y * SIZE + x], rgba, 4);
		}
	BTBHGPUTexture *texture = create_texture_filtered(SIZE, SIZE, BTBH_GPU_TEXTURE_COLOR_SPACE_LINEAR, BTBH_GPU_TEXTURE_FILTER_LINEAR);
	btbh_gpu_texture_update_rgba8(texture, (const uint8_t *)pixels, 0, 0, SIZE, SIZE);
	return texture;
}

// A leaf (white: the instances colour it): pointed at both ends, along the texture's x, a darker midrib and
// veins, a soft edge.
static BTBHGPUTexture *create_leaf_texture(void)
{
	enum { SIZE = 64 };
	static Uint32 pixels[SIZE * SIZE];
	for (int y = 0; y < SIZE; ++y)
		for (int x = 0; x < SIZE; ++x)
		{
			const float u = (x + 0.5f) / SIZE * 2 - 1, v = (y + 0.5f) / SIZE * 2 - 1;
			// Its half-width along it: widest a little behind the middle, a point at each end.
			const float half = 0.42f * sinf((float)M_PI * SDL_clamp((u + 1) / 2, 0.0f, 1.0f)) * (1.0f - 0.25f * u);
			const float inside = half - fabsf(v);
			const float a = SDL_clamp(inside / 0.06f, 0.0f, 1.0f) * (fabsf(u) < 0.98f);
			const float rib = fabsf(v) < 0.035f ? 0.7f : 1.0f;
			const float vein = fabsf(fmodf(u * 4.0f + fabsf(v) * 3.0f + 8.0f, 1.0f) - 0.5f) < 0.06f ? 0.85f : 1.0f;
			const Uint8 shade = (Uint8)(255 * rib * vein);
			const Uint8 rgba[4] = { shade, shade, shade, (Uint8)(255 * a) };
			memcpy(&pixels[y * SIZE + x], rgba, 4);
		}
	BTBHGPUTexture *texture = create_texture_filtered(SIZE, SIZE, BTBH_GPU_TEXTURE_COLOR_SPACE_LINEAR, BTBH_GPU_TEXTURE_FILTER_LINEAR);
	btbh_gpu_texture_update_rgba8(texture, (const uint8_t *)pixels, 0, 0, SIZE, SIZE);
	return texture;
}

// A gull seen from above (white: the instances colour it), its wings spread along the texture's x, its head up
// the texture (towards -y): swept-back wings narrowing to dark tips, its body, head and tail across them.
static BTBHGPUTexture *create_gull_texture(void)
{
	enum { W = 64, H = 32 };
	static Uint32 pixels[W * H];
	for (int y = 0; y < H; ++y)
		for (int x = 0; x < W; ++x)
		{
			const float u = (x + 0.5f) / W * 2 - 1, v = (y + 0.5f) / H * 2 - 1;  // u across, v down the texture
			// Its wings: the leading edge swept back towards the tips, more so past the wrist; narrowing out.
			const float au = fabsf(u);
			const float edge = -0.35f + 0.25f * au + (au > 0.5f ? 0.5f * (au - 0.5f) : 0.0f);
			const float chord = 0.7f * (1 - au * 0.7f);
			const float wing = SDL_min(v - edge, edge + chord - v) / 0.5f;  // (v's units are half as many pixels)
			// Its body, head and tail along v.
			const float body = 1 - sqrtf((u / 0.09f) * (u / 0.09f) + (v / 0.85f) * (v / 0.85f));
			const float inside = SDL_max(wing * 0.25f, body * 0.06f) * (au < 0.97f);
			const float a = SDL_clamp(inside / 0.03f, 0.0f, 1.0f);
			const Uint8 shade = (Uint8)(255 * (au > 0.8f ? 0.5f : 1.0f));  // (dark wingtips)
			const Uint8 rgba[4] = { shade, shade, shade, (Uint8)(255 * a) };
			memcpy(&pixels[y * W + x], rgba, 4);
		}
	BTBHGPUTexture *texture = create_texture_filtered(W, H, BTBH_GPU_TEXTURE_COLOR_SPACE_LINEAR, BTBH_GPU_TEXTURE_FILTER_LINEAR);
	btbh_gpu_texture_update_rgba8(texture, (const uint8_t *)pixels, 0, 0, W, H);
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
	layer_atlas = create_texture_filtered(L3D_WIDTH, ATLAS_H, BTBH_GPU_TEXTURE_COLOR_SPACE_SRGB, map_filter());
	layer_water = create_texture(L3D_WIDTH, ATLAS_H, BTBH_GPU_TEXTURE_COLOR_SPACE_LINEAR);
	tile_atlas = create_texture_filtered(B3D_ATLAS_W, B3D_ATLAS_H * TILE_PAGES, BTBH_GPU_TEXTURE_COLOR_SPACE_SRGB, map_filter());
	tile_water = create_texture(B3D_ATLAS_W, B3D_ATLAS_H * TILE_PAGES, BTBH_GPU_TEXTURE_COLOR_SPACE_LINEAR);
	white_texture = create_texture(1, 1, BTBH_GPU_TEXTURE_COLOR_SPACE_SRGB);
	composed_texture = create_texture(COMPOSED_SIZE, COMPOSED_SIZE * L3D_MAX_BACKGROUNDS, BTBH_GPU_TEXTURE_COLOR_SPACE_SRGB);
	composed_water = create_texture(COMPOSED_SIZE, COMPOSED_SIZE * L3D_MAX_BACKGROUNDS, BTBH_GPU_TEXTURE_COLOR_SPACE_LINEAR);
	puff_texture = create_puff_texture();
	cloud_texture = create_texture_filtered(CLOUD_TEXELS * CLOUD_FINE, CLOUD_TEXELS * CLOUD_FINE * MAX_CLOUD_CANVASES,
	                                        BTBH_GPU_TEXTURE_COLOR_SPACE_SRGB, BTBH_GPU_TEXTURE_FILTER_LINEAR);
	const Uint32 white = 0xffffffff;
	btbh_gpu_texture_update_rgba8(white_texture, (const uint8_t *)&white, 0, 0, 1, 1);
	quad_mesh = create_quad_mesh(1, 1);
	billboard_mesh = create_billboard_mesh();
	particle_texture = create_particle_texture();
	fire_texture = create_fire_texture();
	ring_texture = create_ring_texture();
	nebula_texture = create_nebula_texture();
	leaf_texture = create_leaf_texture();
	gull_texture = create_gull_texture();
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
	nebula_texture = NULL;
	leaf_texture = NULL;
	gull_texture = NULL;
	memset(world_textures, 0, sizeof(world_textures));
	world_mesh = NULL;
	puff_texture = NULL;
	billboard_mesh = NULL;
	composed_texture = NULL;
	cloud_texture = NULL;
	tile_indices_valid = false;
	memset(tile_pages, 0, sizeof(tile_pages));
	hd_scale = 1;
	tile_atlas_hd = NULL;
	hd_generation = 0;
	quad_mesh = NULL;
	fade_meshes[0] = fade_meshes[1] = NULL;
	forget_ui_textures();
	forget_jukebox_scene();
	forget_destruct_scene();

	if (device != NULL)
		btbh_gpu_device_destroy(device);
	device = NULL;

	free(readback_rgba);
	readback_rgba = NULL;
	readback_capacity = 0;
}

/* --- Helpers ------------------------------------------------------------------------------- */

static float text_density = 1;  // the window's pixels per point in the frame being made (text_raster_for)
static Uint32 text_frames = 0;  // frames begun, for the text rasters' use (forget_idle_text_rasters)

static bool begin_frame(BTBHGPUWindowReport *report)
{
	BTBHGPUPlatformSnapshot snapshot;
	if (btbh_gpu_window_begin_frame(window, report, &snapshot) != BTBH_GPU_OK)
		return false;
	if (report->logical_height > 0)
		text_density = (float)report->drawable_height / report->logical_height;
	++text_frames;
	return report->drawable_width > 0 && report->drawable_height > 0 && !report->minimized;
}

static void convert_pixels(const Uint8 *pixels, Uint32 *dst)
{
	for (int i = 0; i < SCREEN_W * SCREEN_H; ++i)
		dst[i] = rgb_palette[pixels[i]];
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
	float map[4];             // where the playfield is in the window: x, y, and window pixels per screen pixel
	bool modern;              // the screen published over the level, in the modern UI's style (ui.h), instead
} menu;

static const Uint8 *screen_without_texts(const SDL_Surface *screen);
// Pictures drawn anew (data/hd/pictures, rgpu_ui_picture's section).
static int hd_picture;
static int match_hd_picture(const Uint8 *picture, Uint32 *rgba);
static void add_hd_picture(float sx, float sy, float sw, float sh, float x, float y, float w, float h, float alpha);
static void find_hd_logos(const Uint8 *picture, Uint32 *rgba);
static void add_hd_logos(const SDL_Rect *dst);
static int hd_face;  // (the data cube's face drawn anew this frame: find_hd_face)
static bool hd_frame_shown;  // (and the portrait's frame)
static void find_hd_face(const Uint8 *picture, Uint32 *rgba);
static void add_hd_face(float sx, float sy, float sw, float sh, float x, float y, float w, float h, float alpha);
static void screen_text_quads(float ox, float oy, float kx, float ky, int clip_w, int clip_h);
static bool fonts_enabled(void);
static const TextRecord *frame_texts[32];
static int frame_text_count;

// A colour over the whole window (straight alpha), drawn last: a menu's or the store's fade.
static float canvas_fade[4];


// A rectangle of the screen texture (in screen pixels) drawn to a rectangle of the window.
typedef struct
{
	float x, y, w, h;
	float source_x, source_y, source_w, source_h;
	bool panel;  // from the high-resolution HUD panel (its source rectangle in screen pixels)
	bool sharp;  // the whole screen magnified in whole steps first, then smoothly to its size (sharp_steps)
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

/*
 * The whole screen shown at a size that isn't a whole number of window pixels per screen pixel (the
 * modern UI's screens fill the window's height): magnified in whole steps with sharp pixels into a
 * target first, then drawn from it smoothly at its size, so the pixels stay sharp and even ("sharp
 * bilinear") instead of a nearest scale's uneven rows and columns.
 */
static BTBHGPUTexture *sharp_target = NULL;
static int sharp_w = 0, sharp_h = 0;
// The largest magnification of the screen's picture asked for this frame (window pixels per screen
// pixel, rgpu_ui_picture), for its sharp copy (present_canvas).
static float picture_magnification = 0;

// The whole steps for a screen h points tall, or 0 when its size is a whole step anyway.
static int sharp_steps(float h)
{
	const float pixels = h * text_density / SCREEN_H;
	const int k = (int)floorf(pixels + 1e-3f);
	return k < 1 || pixels - k < 1e-3f ? 0 : k;
}

static BTBHGPUTexture *sharp_texture(int k)
{
	if (sharp_target != NULL && sharp_w == SCREEN_W * k && sharp_h == SCREEN_H * k)
		return sharp_target;
	if (sharp_target != NULL)
		btbh_gpu_texture_destroy(sharp_target);
	BTBHGPUTextureReport report;
	sharp_target = btbh_gpu_window_render_target_create(window, (uint32_t)(SCREEN_W * k), (uint32_t)(SCREEN_H * k),
	                                                    BTBH_GPU_TEXTURE_FILTER_LINEAR, &report);
	sharp_w = sharp_target != NULL ? SCREEN_W * k : 0;
	sharp_h = sharp_target != NULL ? SCREEN_H * k : 0;
	return sharp_target;
}

/*
 * The 3D scene blurred for the frosted glass of the screens over a level (the in-game options, help,
 * the level's end): the scene as composited is copied (scene_capture, after it is drawn), then made
 * smaller in halves into SCENE_BLUR_STEPS targets in passes of the canvas; the last, an eighth of the
 * window's size or so, is what the glass shows. Made again only when the scene does (scene_blur_key).
 */
#define SCENE_BLUR_STEPS 4
static BTBHGPUTexture *scene_blur[SCENE_BLUR_STEPS];
static int scene_blur_w[SCENE_BLUR_STEPS], scene_blur_h[SCENE_BLUR_STEPS];
static BTBHGPUTexture *scene_capture = NULL;  // this frame's copy of the scene, when the blur is made again
static bool scene_blur_valid = false;
static Uint64 scene_blur_key = 0;

// The targets for a window w x h (points), made when its size changes; false if they can't be.
static bool scene_blur_targets(float w, float h)
{
	int tw = (int)(w / 2), th = (int)(h / 2);
	if (scene_blur[0] != NULL && scene_blur_w[0] == SDL_max(tw, 1) && scene_blur_h[0] == SDL_max(th, 1))
		return true;
	for (int i = 0; i < SCENE_BLUR_STEPS; ++i)
	{
		if (scene_blur[i] != NULL)
			btbh_gpu_texture_destroy(scene_blur[i]);
		scene_blur[i] = NULL;
	}
	scene_blur_valid = false;
	for (int i = 0; i < SCENE_BLUR_STEPS; ++i)
	{
		tw = SDL_max(tw, 1);
		th = SDL_max(th, 1);
		BTBHGPUTextureReport report;
		scene_blur[i] = btbh_gpu_window_render_target_create(window, (uint32_t)tw, (uint32_t)th, BTBH_GPU_TEXTURE_FILTER_LINEAR, &report);
		if (scene_blur[i] == NULL)
			return false;
		scene_blur_w[i] = tw;
		scene_blur_h[i] = th;
		tw /= 2;
		th /= 2;
	}
	return true;
}

// The HUD's quads first to last as batches (one per run of quads from the same texture).
static void hud_batches(int first, int last, BTBHGPUCanvasVertex *vertices, uint32_t *vertex_count,
                        BTBHGPUCanvasBatch *batches, int *batch_count)
{
	for (int i = first; i < last; ++i)
	{
		const HudQuad *q = &hud_quads[i];
		BTBHGPUCanvasVertex corners[4] = {
			{ q->x,        q->y,        q->u0, q->v0, q->left[0], q->left[1], q->left[2], q->left[3] },
			{ q->x + q->w, q->y,        q->u1, q->v0, q->right[0], q->right[1], q->right[2], q->right[3] },
			{ q->x + q->w, q->y + q->h, q->u1, q->v1, q->right[0], q->right[1], q->right[2], q->right[3] },
			{ q->x,        q->y + q->h, q->u0, q->v1, q->left[0], q->left[1], q->left[2], q->left[3] },
		};
		if (q->graded)
			for (int k = 2; k < 4; ++k)
			{
				corners[k].red = q->below[0];
				corners[k].green = q->below[1];
				corners[k].blue = q->below[2];
				corners[k].alpha = q->below[3];
			}
		if (q->poly)
			for (int k = 0; k < 4; ++k)
				corners[k] = (BTBHGPUCanvasVertex){ q->px[k], q->py[k], 0, 0, 0, 0, 0, q->pa[k] };
		if (q->free)
			memcpy(corners, q->corner, sizeof(corners));
		BTBHGPUCanvasVertex *v = vertices + *vertex_count;
		v[0] = corners[0];
		v[1] = corners[1];
		v[2] = corners[2];
		v[3] = corners[0];
		v[4] = corners[2];
		v[5] = corners[3];
		if (i > first && hud_quads[i - 1].texture == q->texture && hud_quads[i - 1].premultiplied == q->premultiplied)
			batches[*batch_count - 1].vertex_count += 6;
		else
		{
			BTBHGPUCanvasBatch *b = &batches[(*batch_count)++];
			b->first_vertex = *vertex_count;
			b->vertex_count = 6;
			b->texture = q->texture;
			b->blend_mode = q->premultiplied ? BTBH_GPU_CANVAS_BLEND_PREMULTIPLIED_ALPHA : BTBH_GPU_CANVAS_BLEND_ALPHA;
		}
		*vertex_count += 6;
	}
}

// Draws parts of the screen texture over the window and presents. Composites a pending 3D scene
// first. A spotlight overlay (spot_texture over the whole window) goes under the screen's parts.
static void present_canvas(const CanvasQuad *quads, int quad_count, bool spotlight, bool clear,
                           const BTBHGPUWindowReport *frame)
{
	// Six vertices and at most a batch for each quad: the sharp screen's step, the spotlight, the
	// screen's (a panel's two: its picture and the panel), the HUD's, the fade. Grown as a frame needs
	// more, and kept.
	static BTBHGPUCanvasVertex *vertices = NULL;
	static BTBHGPUCanvasBatch *batches_2d = NULL;
	static int room = 0;
	const int fixed = 3 + 2 * MAX_CANVAS_QUADS + SCENE_BLUR_STEPS;
	if (fixed + hud_quad_count > room)
	{
		const int grown = SDL_max(fixed + hud_quad_count, SDL_max(2 * room, fixed + HUD_QUADS_FIRST));
		BTBHGPUCanvasVertex *v = SDL_realloc(vertices, sizeof(*v) * 6 * (size_t)grown);
		if (v != NULL)
			vertices = v;
		BTBHGPUCanvasBatch *b = SDL_realloc(batches_2d, sizeof(*b) * (size_t)grown);
		if (b != NULL)
			batches_2d = b;
		if (v != NULL && b != NULL)
			room = grown;
		else if (room < fixed)
		{
			hud_quad_count = 0;
			return;
		}
		else
			hud_quad_count = room - fixed;  // (no memory for more: the last of them go)
	}
	memset(batches_2d, 0, sizeof(*batches_2d) * (size_t)(fixed + hud_quad_count));
	int batch_count_2d = 0;
	uint32_t vertex_count = 0;
	hud_under = SDL_min(hud_under, hud_quad_count);

	// The 3D scene made smaller in halves, blurred, for frosted glass over it (scene_blur): passes of
	// their own, first.
	const int blur_passes = scene_capture != NULL ? SCENE_BLUR_STEPS : 0;
	for (int i = 0; i < blur_passes; ++i)
	{
		const CanvasQuad whole = { 0, 0, (float)scene_blur_w[i], (float)scene_blur_h[i], 0, 0, 1, 1 };
		push_quad(vertices + vertex_count, &whole, 1, 1);
		BTBHGPUCanvasBatch *b = &batches_2d[batch_count_2d++];
		b->first_vertex = vertex_count;
		b->vertex_count = 6;
		b->texture = i == 0 ? scene_capture : scene_blur[i - 1];
		b->blend_mode = BTBH_GPU_CANVAS_BLEND_PREMULTIPLIED_ALPHA;  // (onto opaque black: the colour as it is, opaque)
		vertex_count += 6;
	}

	// The sharp screen's whole steps, into its target (a pass of its own, first): for the whole screen
	// shown at a size between whole steps, or parts of its picture (rgpu_ui_picture) magnified so.
	quad_count = SDL_min(quad_count, MAX_CANVAS_QUADS);
	BTBHGPUTexture *sharp = NULL;
	int sharp_k = 0;
	for (int i = 0; i < quad_count && sharp_k == 0; ++i)
		sharp_k = quads[i].sharp && !quads[i].panel ? sharp_steps(quads[i].h) : 0;
	if (sharp_k == 0 && picture_magnification >= 2)
	{
		const int k = (int)floorf(picture_magnification + 1e-3f);
		if (picture_magnification - k > 1e-3f)
			sharp_k = SDL_min(k, 8);
	}
	if (sharp_k > 0 && (sharp = sharp_texture(sharp_k)) != NULL)
	{
		const CanvasQuad whole = { 0, 0, (float)sharp_w, (float)sharp_h, 0, 0, SCREEN_W, SCREEN_H };
		push_quad(vertices + vertex_count, &whole, SCREEN_W, SCREEN_H);
		BTBHGPUCanvasBatch *b = &batches_2d[batch_count_2d++];
		b->first_vertex = vertex_count;
		b->vertex_count = 6;
		b->texture = screen_texture;
		b->blend_mode = BTBH_GPU_CANVAS_BLEND_ALPHA;
		vertex_count += 6;
	}
	const int prepass = sharp != NULL ? 1 : 0;
	// The picture's parts from its sharp copy.
	if (sharp != NULL)
		for (int i = 0; i < hud_quad_count; ++i)
			if (hud_quads[i].picture)
				hud_quads[i].texture = sharp;
	picture_magnification = 0;

	if (spotlight)
	{
		const CanvasQuad whole = { 0, 0, (float)frame->logical_width, (float)frame->logical_height, 0, 0, SPOT_W, SPOT_H };
		push_quad(vertices + vertex_count, &whole, SPOT_W, SPOT_H);
		BTBHGPUCanvasBatch *b = &batches_2d[batch_count_2d++];
		b->first_vertex = vertex_count;
		b->vertex_count = 6;
		b->texture = spot_texture;
		b->blend_mode = BTBH_GPU_CANVAS_BLEND_ALPHA;
		vertex_count += 6;
	}

	// The HUD's quads that go under the screen's.
	hud_batches(0, hud_under, vertices, &vertex_count, batches_2d, &batch_count_2d);

	for (int i = 0; i < quad_count; ++i)
	{
		BTBHGPUCanvasBatch *batch = &batches_2d[batch_count_2d++];
		batch->first_vertex = vertex_count;
		batch->vertex_count = 6;
		batch->blend_mode = BTBH_GPU_CANVAS_BLEND_ALPHA;
		if (quads[i].sharp && sharp != NULL)
		{
			// (The target holds the screen with its alpha multiplied in.)
			CanvasQuad q = quads[i];
			q.source_x = q.source_y = 0;
			q.source_w = q.source_h = 1;
			push_quad(vertices + vertex_count, &q, 1, 1);
			batch->texture = sharp;
			batch->blend_mode = BTBH_GPU_CANVAS_BLEND_PREMULTIPLIED_ALPHA;
		}
		else if (quads[i].panel)
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

	// The modern HUD (and the UI's quads), in batches of quads with the same texture.
	hud_batches(hud_under, hud_quad_count, vertices, &vertex_count, batches_2d, &batch_count_2d);

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

	BTBHGPUCanvasPass passes[2 + SCENE_BLUR_STEPS];
	memset(passes, 0, sizeof(passes));
	int pass_count = 0;
	for (int i = 0; i < blur_passes; ++i)
	{
		passes[pass_count].first_batch = (uint32_t)i;
		passes[pass_count].batch_count = 1;
		passes[pass_count].target = scene_blur[i];
		passes[pass_count].clear_enabled = 1;
		passes[pass_count].clear_alpha = 255;
		++pass_count;
	}
	if (prepass)
	{
		passes[pass_count].first_batch = (uint32_t)blur_passes;
		passes[pass_count].batch_count = 1;
		passes[pass_count].target = sharp;
		passes[pass_count].clear_enabled = 1;
		passes[pass_count].clear_alpha = 0;
		++pass_count;
	}
	BTBHGPUCanvasPass *screen_pass = &passes[pass_count++];
	screen_pass->first_batch = (uint32_t)(blur_passes + prepass);
	screen_pass->batch_count = (uint32_t)(batch_count_2d - blur_passes - prepass);
	screen_pass->target = NULL;
	screen_pass->clear_enabled = clear;
	screen_pass->clear_alpha = 255;

	// Frames shown between ticks don't count as the game's frames (dumps, TYR3D_EXIT_AFTER).
	static int dump_ahead = -1;  // TYR3D_DUMP_AHEAD=1: they do, to check them
	if (dump_ahead < 0)
		dump_ahead = SDL_getenv("TYR3D_DUMP_AHEAD") != NULL;
	const bool tick_frame = ahead == 0 || dump_ahead;
	const bool capture = tick_frame && dev_capture_next_frame();
	if (capture)
		btbh_gpu_window_request_presented_frame_readback(window);

	hud_quad_count = 0;  // made again for each 3D frame
	hud_under = 0;

	BTBHGPUCanvasReport report;
	if (btbh_gpu_window_canvas_present(window,
	        shader_paths[SH_CANVAS_VERT], shader_paths[SH_CANVAS_FRAG], shader_paths[SH_CANVAS_TEXTURED_FRAG],
	        shader_format, vertices, vertex_count, batches_2d, (uint32_t)batch_count_2d, passes, (uint32_t)pass_count,
	        &report) != BTBH_GPU_OK)
	{
		fprintf(stderr, "warning: canvas present failed: %s\n", report.message);
	}
	if (scene_capture != NULL)
	{
		// (Released once the GPU is done with it.)
		btbh_gpu_texture_destroy(scene_capture);
		scene_capture = NULL;
		scene_blur_valid = true;
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

/*
 * The modern UI's screens (ui.h): the screen's picture blurred, a quarter of its size and softened,
 * for the window round the picture (instead of black bars) and the frosted glass under the UI's
 * panels. It is mapped over the window as the picture would cover it (cover_map).
 */
#define BLUR_W 80
#define BLUR_H 50
#define BLUR_RADIUS 2  // of each of the three box blurs (about a Gaussian), blurred pixels
static BTBHGPUTexture *blur_texture = NULL;
static bool blur_ready = false;  // made for the frame being drawn
static float cover_map[4];       // where the blurred picture lies: x, y, w, h (points)
static BTBHGPUTexture *frost_texture = NULL;  // what frosted glass shows: blur_texture, or the 3D scene's (scene_blur)
static bool blur_ready_once = false;  // blur_texture holds a blurred picture (forget_ui_textures)

// A box blur of a line of RGB triplets (n of them, stride apart, in triplets) with the edges held.
static void blur_line(Uint32 *v, int n, int stride, Uint32 *line)
{
	for (int i = 0; i < n; ++i)
		for (int k = 0; k < 3; ++k)
			line[i * 3 + k] = v[i * stride * 3 + k];
	Uint32 sum[3] = { 0, 0, 0 };
	for (int i = -BLUR_RADIUS; i <= BLUR_RADIUS; ++i)
	{
		const int j = SDL_clamp(i, 0, n - 1);
		for (int k = 0; k < 3; ++k)
			sum[k] += line[j * 3 + k];
	}
	for (int i = 0; i < n; ++i)
	{
		const int in = SDL_min(i + BLUR_RADIUS + 1, n - 1) * 3, out = SDL_max(i - BLUR_RADIUS, 0) * 3;
		for (int k = 0; k < 3; ++k)
		{
			v[i * stride * 3 + k] = sum[k] / (2 * BLUR_RADIUS + 1);
			sum[k] += line[in + k] - line[out + k];
		}
	}
}

// The picture (SCREEN_W x SCREEN_H, RGBA) blurred into blur_texture: a quarter of its size, softened.
// Not made again while the picture stays as it was (a sparse hash); when only its content changes, at
// most every 50 ms (a screen that animates: about every third frame; it's soft and dimmed, the lag
// doesn't show); when the palette changes (fades), at once.
static void make_blur(const Uint32 *rgba, float window_w, float window_h)
{
	const Uint64 start = SDL_GetPerformanceCounter();
	if (blur_texture == NULL)
		blur_texture = create_texture_filtered(BLUR_W, BLUR_H, BTBH_GPU_TEXTURE_COLOR_SPACE_LINEAR, BTBH_GPU_TEXTURE_FILTER_LINEAR);
	static Uint32 c[BLUR_W * BLUR_H * 3];
	static Uint32 line[(BLUR_W > BLUR_H ? BLUR_W : BLUR_H) * 3];
	static Uint32 out[BLUR_W * BLUR_H];
	static Uint32 last_picture = 0, last_palette = 0;
	static Uint64 made_at = 0;
	Uint32 picture = 2166136261u, palette = 2166136261u;
	for (int i = 0; i < SCREEN_W * SCREEN_H; i += 7)
		picture = (picture ^ rgba[i]) * 16777619u;
	for (int i = 0; i < 256; ++i)
		palette = (palette ^ rgb_palette[i]) * 16777619u;
	const Uint64 now = SDL_GetTicks();
	const bool due = !blur_ready_once || palette != last_palette || (picture != last_picture && now - made_at >= 50);
	if (due)
	{
		// (Transparent pixels are black.)
		for (int y = 0; y < BLUR_H; ++y)
			for (int x = 0; x < BLUR_W; ++x)
			{
				Uint32 sum[3] = { 0, 0, 0 };
				for (int dy = 0; dy < 4; ++dy)
				{
					const Uint8 *p = (const Uint8 *)&rgba[(4 * y + dy) * SCREEN_W + 4 * x];
					sum[0] += (Uint32)p[0] + p[4] + p[8] + p[12];
					sum[1] += (Uint32)p[1] + p[5] + p[9] + p[13];
					sum[2] += (Uint32)p[2] + p[6] + p[10] + p[14];
				}
				Uint32 *o = &c[(y * BLUR_W + x) * 3];
				o[0] = sum[0] / 16;
				o[1] = sum[1] / 16;
				o[2] = sum[2] / 16;
			}
		for (int pass = 0; pass < 3; ++pass)
		{
			for (int y = 0; y < BLUR_H; ++y)
				blur_line(&c[y * BLUR_W * 3], BLUR_W, 1, line);
			for (int x = 0; x < BLUR_W; ++x)
				blur_line(&c[x * 3], BLUR_H, BLUR_W, line);
		}
		for (int i = 0; i < BLUR_W * BLUR_H; ++i)
			out[i] = pack_rgba((Uint8)SDL_min(c[i * 3], 255u), (Uint8)SDL_min(c[i * 3 + 1], 255u), (Uint8)SDL_min(c[i * 3 + 2], 255u));
		btbh_gpu_texture_update_rgba8(blur_texture, (const uint8_t *)out, 0, 0, BLUR_W, BLUR_H);
		last_picture = picture;
		last_palette = palette;
		made_at = now;
		blur_ready_once = true;
	}
	const float s = SDL_max(window_w / SCREEN_W, window_h / SCREEN_H);
	cover_map[0] = (window_w - SCREEN_W * s) / 2;
	cover_map[1] = (window_h - SCREEN_H * s) / 2;
	cover_map[2] = SCREEN_W * s;
	cover_map[3] = SCREEN_H * s;
	frost_texture = blur_texture;
	blur_ready = true;
	static Uint64 spent = 0;
	static int made = 0;
	spent += SDL_GetPerformanceCounter() - start;
	if (++made == 120)
	{
		if (SDL_getenv("TYR3D_PROFILE") != NULL)
			printf("blur: %.3f ms a frame\n", (double)spent * 1000.0 / SDL_GetPerformanceFrequency() / made);
		spent = 0;
		made = 0;
	}
}

// A quad from the blurred picture where it lies under it, a colour each corner (times the picture).
static void frost_quad(const float x[4], const float y[4], const float (*tint)[4])
{
	if (!blur_ready || frost_texture == NULL)
		return;
	HudQuad *q = hud_quad_add();
	if (q == NULL)
		return;
	*q = (HudQuad){ .free = true, .texture = frost_texture };
	for (int k = 0; k < 4; ++k)
		q->corner[k] = (BTBHGPUCanvasVertex){ x[k], y[k], (x[k] - cover_map[0]) / cover_map[2], (y[k] - cover_map[1]) / cover_map[3],
		                                      tint[k][0], tint[k][1], tint[k][2], tint[k][3] };
}

static void colour_quad(const float x[4], const float y[4], const float (*rgba)[4])
{
	HudQuad *q = hud_quad_add();
	if (q == NULL)
		return;
	*q = (HudQuad){ .free = true };
	for (int k = 0; k < 4; ++k)
		q->corner[k] = (BTBHGPUCanvasVertex){ x[k], y[k], 0, 0, rgba[k][0], rgba[k][1], rgba[k][2], rgba[k][3] };
}

/*
 * Round a screen filling the window's height (ui_fill_screens): the blurred picture in the rest of the
 * window, dimmed, darker towards the window's edges, and a soft shadow round the picture.
 */
#define SURROUND_LIGHT 0.42f  // the blurred picture's brightness beside the picture
#define SURROUND_EDGE 0.2f    // and at the window's edges
#define SURROUND_SHADOW 0.032f  // the picture's shadow on it, of the window's height

static void add_surround(const SDL_Rect *dst, float window_w, float window_h)
{
	const float x0 = (float)dst->x, y0 = (float)dst->y, x1 = (float)(dst->x + dst->w), y1 = (float)(dst->y + dst->h);
	const float light[4] = { SURROUND_LIGHT, SURROUND_LIGHT * 0.96f, SURROUND_LIGHT * 0.92f, 1 };
	const float edge[4] = { SURROUND_EDGE, SURROUND_EDGE * 0.96f, SURROUND_EDGE * 0.92f, 1 };
	if (x0 > 0.5f)  // left and right
	{
		const float lx[4] = { 0, x0, x0, 0 }, ly[4] = { 0, 0, window_h, window_h };
		const float lt[4][4] = { { edge[0], edge[1], edge[2], 1 }, { light[0], light[1], light[2], 1 },
		                         { light[0], light[1], light[2], 1 }, { edge[0], edge[1], edge[2], 1 } };
		frost_quad(lx, ly, lt);
		const float rx[4] = { x1, window_w, window_w, x1 }, ry[4] = { 0, 0, window_h, window_h };
		const float rt[4][4] = { { light[0], light[1], light[2], 1 }, { edge[0], edge[1], edge[2], 1 },
		                         { edge[0], edge[1], edge[2], 1 }, { light[0], light[1], light[2], 1 } };
		frost_quad(rx, ry, rt);
	}
	if (y0 > 0.5f)  // above and below
	{
		const float tx[4] = { x0, x1, x1, x0 }, ty[4] = { 0, 0, y0, y0 };
		const float tt[4][4] = { { edge[0], edge[1], edge[2], 1 }, { edge[0], edge[1], edge[2], 1 },
		                         { light[0], light[1], light[2], 1 }, { light[0], light[1], light[2], 1 } };
		frost_quad(tx, ty, tt);
		const float bx[4] = { x0, x1, x1, x0 }, by[4] = { y1, y1, window_h, window_h };
		const float bt[4][4] = { { light[0], light[1], light[2], 1 }, { light[0], light[1], light[2], 1 },
		                         { edge[0], edge[1], edge[2], 1 }, { edge[0], edge[1], edge[2], 1 } };
		frost_quad(bx, by, bt);
	}
	// The picture's shadow: a band along each edge with the blurred picture beyond it.
	const float d = SURROUND_SHADOW * window_h;
	const float dark[4] = { 0, 0, 0, 0.6f }, clear[4] = { 0, 0, 0, 0 };
	if (x0 > 0.5f)
	{
		const float lx[4] = { x0 - d, x0, x0, x0 - d }, ly[4] = { y0, y0, y1, y1 };
		const float lc[4][4] = { { clear[0], clear[1], clear[2], clear[3] }, { dark[0], dark[1], dark[2], dark[3] },
		                         { dark[0], dark[1], dark[2], dark[3] }, { clear[0], clear[1], clear[2], clear[3] } };
		colour_quad(lx, ly, lc);
		const float rx[4] = { x1, x1 + d, x1 + d, x1 }, ry[4] = { y0, y0, y1, y1 };
		const float rc[4][4] = { { dark[0], dark[1], dark[2], dark[3] }, { clear[0], clear[1], clear[2], clear[3] },
		                         { clear[0], clear[1], clear[2], clear[3] }, { dark[0], dark[1], dark[2], dark[3] } };
		colour_quad(rx, ry, rc);
	}
	if (y0 > 0.5f)
	{
		const float tx[4] = { x0, x1, x1, x0 }, ty[4] = { y0 - d, y0 - d, y0, y0 };
		const float tc[4][4] = { { clear[0], clear[1], clear[2], clear[3] }, { clear[0], clear[1], clear[2], clear[3] },
		                         { dark[0], dark[1], dark[2], dark[3] }, { dark[0], dark[1], dark[2], dark[3] } };
		colour_quad(tx, ty, tc);
		const float bx[4] = { x0, x1, x1, x0 }, by[4] = { y1, y1, y1 + d, y1 + d };
		const float bc[4][4] = { { dark[0], dark[1], dark[2], dark[3] }, { dark[0], dark[1], dark[2], dark[3] },
		                         { clear[0], clear[1], clear[2], clear[3] }, { clear[0], clear[1], clear[2], clear[3] } };
		colour_quad(bx, by, bc);
	}
}

/*
 * The window behind a screen laid out over the whole of it (the store): the picture blurred over it,
 * dimmed, darker towards the window's edges; hole (points: x, y, w, h), if any, left for a 3D scene.
 */
#define BACKDROP_LIGHT 0.40f
#define BACKDROP_EDGE 0.18f

static void add_backdrop(float window_w, float window_h, const float *hole)
{
	if (!blur_ready)
		return;
	// Rows: above the hole, beside it (left and right), below it; each darker towards the window's top
	// and bottom, and its sides.
	const float hx0 = hole != NULL ? hole[0] : window_w / 2, hx1 = hole != NULL ? hole[0] + hole[2] : window_w / 2;
	const float hy0 = hole != NULL ? hole[1] : window_h / 2, hy1 = hole != NULL ? hole[1] + hole[3] : window_h / 2;
	const float xs[4] = { 0, hx0, hx1, window_w }, ys[4] = { 0, hy0, hy1, window_h };
	for (int r = 0; r < 3; ++r)
		for (int c = 0; c < 3; ++c)
		{
			if (r == 1 && c == 1 && hole != NULL)
				continue;
			if (xs[c + 1] - xs[c] < 0.5f || ys[r + 1] - ys[r] < 0.5f)
				continue;
			const float x[4] = { xs[c], xs[c + 1], xs[c + 1], xs[c] }, y[4] = { ys[r], ys[r], ys[r + 1], ys[r + 1] };
			float tint[4][4];
			for (int k = 0; k < 4; ++k)
			{
				// Lighter in the middle of the window, darker at its edges.
				const float u = SDL_fabsf(x[k] / window_w - 0.5f) * 2, v = SDL_fabsf(y[k] / window_h - 0.5f) * 2;
				const float e = SDL_clamp(SDL_max(u, v * 1.15f), 0.0f, 1.0f);
				const float l = BACKDROP_LIGHT + (BACKDROP_EDGE - BACKDROP_LIGHT) * e * e;
				tint[k][0] = l;
				tint[k][1] = l * 0.95f;
				tint[k][2] = l * 0.9f;
				tint[k][3] = 1;
			}
			frost_quad(x, y, tint);
		}
}

void rgpu_present_blank(void)
{
	BTBHGPUWindowReport frame;
	if (!begin_frame(&frame))
		return;
	hud_quad_count = 0;
	canvas_fade[3] = 0;
	present_canvas(NULL, 0, false, true, &frame);
}

void rgpu_present_2d(const SDL_Surface *screen, const SDL_Rect *dst)
{
	BTBHGPUWindowReport frame;
	if (!begin_frame(&frame))
		return;

	// With the 3D view on, the game's screens (menus, the store) show their texts in Oxanium.
	hud_quad_count = 0;
	blur_ready = false;
	const bool whole = screen->w == SCREEN_W && screen->h >= SCREEN_H;
	const Uint8 *pixels = NULL;
	if (l3d_enabled && whole)
	{
		pixels = screen_without_texts(screen);
		convert_pixels(pixels, screen_rgba);
	}
	else
		convert_screen(screen, screen_rgba);

	CanvasQuad quad = whole_screen_quad(dst);
	if (whole && ui_fill_screens())
	{
		// Filling the window's height: sharp, over its blurred copy.
		make_blur(screen_rgba, (float)frame.logical_width, (float)frame.logical_height);
		add_surround(dst, (float)frame.logical_width, (float)frame.logical_height);
		quad.sharp = true;
	}
	// A picture drawn anew (the logos as the game starts, the title before its menu): under the screen,
	// which keeps only what the game drew over it.
	hd_picture = pixels != NULL ? match_hd_picture(pixels, screen_rgba) : 0;
	if (hd_picture != 0)
	{
		find_hd_logos(pixels, screen_rgba);
		add_hd_picture(0, 0, SCREEN_W, SCREEN_H, (float)dst->x, (float)dst->y, (float)dst->w, (float)dst->h, 1);
		add_hd_logos(dst);
		hud_under = hud_quad_count;
	}
	// (A data cube's face drawn anew, and the texts in Oxanium, over the screen: after the quads under it.)
	if (pixels != NULL)
	{
		find_hd_face(pixels, screen_rgba);
		add_hd_face(0, 0, SCREEN_W, SCREEN_H, (float)dst->x, (float)dst->y, (float)dst->w, (float)dst->h, 1);
		screen_text_quads(dst->x, dst->y, dst->w / (float)SCREEN_W, dst->h / (float)SCREEN_H, SCREEN_W, SCREEN_H);
	}
	btbh_gpu_texture_update_rgba8(screen_texture, (const uint8_t *)screen_rgba, 0, 0, SCREEN_W, SCREEN_H);
	present_canvas(&quad, 1, false, true, &frame);
	blur_ready = false;
	hd_picture = 0;
	hd_face = -1;
	hd_frame_shown = false;
}

/* --- The UI's drawing (ui.c) ----------------------------------------------------------------- */

void rgpu_ui_quad(const float x[4], const float y[4], const float rgba[4][4])
{
	colour_quad(x, y, rgba);
}

void rgpu_ui_frost(const float x[4], const float y[4], const float tint[4])
{
	const float t[4][4] = { { tint[0], tint[1], tint[2], tint[3] }, { tint[0], tint[1], tint[2], tint[3] },
	                        { tint[0], tint[1], tint[2], tint[3] }, { tint[0], tint[1], tint[2], tint[3] } };
	frost_quad(x, y, t);
}

bool rgpu_ui_frost_ready(void)
{
	return blur_ready;
}

int rgpu_ui_mark(void)
{
	return hud_quad_count;
}

void rgpu_ui_fade_since(int mark, float alpha)
{
	for (int i = SDL_max(mark, 0); i < hud_quad_count; ++i)
	{
		HudQuad *q = &hud_quads[i];
		for (int k = 0; k < (q->premultiplied ? 3 : 0); ++k)
		{
			q->left[k] *= alpha;
			q->right[k] *= alpha;
		}
		q->left[3] *= alpha;
		q->right[3] *= alpha;
		q->below[3] *= alpha;
		for (int k = 0; k < 4; ++k)
		{
			q->pa[k] *= alpha;
			q->corner[k].alpha *= alpha;
		}
	}
}

// A picture of the UI's own (the pointer, ui_pointer_image) in a rectangle: RGBA (straight alpha), at most
// IMAGE_SIZE square, uploaded again when its key changes.
#define IMAGE_SIZE 128
static BTBHGPUTexture *image_texture = NULL;
static Uint32 image_key = 0;

void rgpu_ui_image(Uint32 key, const Uint32 *rgba, int w, int h, float x, float y, float dw, float dh)
{
	if (w <= 0 || h <= 0 || w > IMAGE_SIZE || h > IMAGE_SIZE)
		return;
	if (image_texture == NULL)
		image_texture = create_texture_filtered(IMAGE_SIZE, IMAGE_SIZE, BTBH_GPU_TEXTURE_COLOR_SPACE_LINEAR,
		                                        BTBH_GPU_TEXTURE_FILTER_LINEAR);
	if (key != image_key)
	{
		btbh_gpu_texture_update_rgba8(image_texture, (const uint8_t *)rgba, 0, 0, (uint32_t)w, (uint32_t)h);
		image_key = key;
	}
	HudQuad *q = hud_quad_add();
	if (q == NULL)
		return;
	*q = (HudQuad){ x, y, dw, dh, 0, 0, (float)w / IMAGE_SIZE, (float)h / IMAGE_SIZE, { 1, 1, 1, 1 }, { 1, 1, 1, 1 },
	                .texture = image_texture };
}

/*
 * Sprites of the game as the UI's icons (the special weapon, lives, bombs, the store's items, data
 * cubes): drawn into slots of a small texture in the current palette, made again when it changes.
 */
#define ICON_SLOT 48
#define ICON_SLOTS 24
static BTBHGPUTexture *icon_texture = NULL;
static struct
{
	const void *sheet;  // a Sprite2_array, or NULL for a sprite table's (table)
	unsigned int table;
	unsigned int sprite;
	bool large;
	Uint32 palette;     // hash of the palette it was drawn in
	Uint32 used;        // text_frames when last drawn
	int w, h;           // its picture's size in the slot (from its top left, ICON_PAD in)
	int x0, y0;
} icon_slots[ICON_SLOTS];

// (The window owns them: they go with it.)
static void forget_ui_textures(void)
{
	sharp_target = NULL;
	sharp_w = sharp_h = 0;
	blur_texture = NULL;
	frost_texture = NULL;
	blur_ready_once = false;
	icon_texture = NULL;
	memset(icon_slots, 0, sizeof(icon_slots));
	image_texture = NULL;
	image_key = 0;
	for (int i = 0; i < SCENE_BLUR_STEPS; ++i)
		scene_blur[i] = NULL;
	scene_capture = NULL;
	scene_blur_valid = false;
	forget_model_icons();
}

static Uint32 palette_hash(void)
{
	Uint32 h = 2166136261u;
	for (int i = 0; i < 256; ++i)
		h = (h ^ rgb_palette[i]) * 16777619u;
	return h;
}

// The slot holding a sprite in the current palette (drawn into it if it isn't), or -1.
static int icon_slot(const void *sheet, unsigned int table, unsigned int sprite, bool large)
{
	if (icon_texture == NULL)
		icon_texture = create_texture(ICON_SLOT * ICON_SLOTS, ICON_SLOT, BTBH_GPU_TEXTURE_COLOR_SPACE_LINEAR);
	static Uint32 hash_frame = 0, hash = 0;
	if (hash_frame != text_frames || hash == 0)
	{
		hash = palette_hash();
		hash_frame = text_frames;
	}
	int slot = -1, oldest = 0;
	for (int i = 0; i < ICON_SLOTS && slot < 0; ++i)
		if (icon_slots[i].sheet == sheet && icon_slots[i].table == table && icon_slots[i].sprite == sprite &&
		    icon_slots[i].large == large && icon_slots[i].w > 0)
			slot = i;
	for (int i = 1; i < ICON_SLOTS; ++i)
		if (icon_slots[i].used < icon_slots[oldest].used)
			oldest = i;
	if (slot < 0 || icon_slots[slot].palette != hash)
	{
		if (slot < 0)
			slot = oldest;
		// (As wide as the screen: the game's sprite drawing steps its rows by the screen's pitch.)
		static SDL_Surface *canvas = NULL;
		if (canvas == NULL && (canvas = SDL_CreateSurface(SCREEN_W, ICON_SLOT + 8, SDL_PIXELFORMAT_INDEX8)) == NULL)
			return -1;
		SDL_FillSurfaceRect(canvas, NULL, 0);
		int x0, y0, w, h;
		if (sheet != NULL)
		{
			x0 = large ? 4 : 10, y0 = large ? 2 : 9, w = large ? 24 : 12, h = large ? 28 : 14;
			if (large)
				blit_sprite2x2(canvas, x0, y0, *(const Sprite2_array *)sheet, sprite);
			else
				blit_sprite2(canvas, x0, y0, *(const Sprite2_array *)sheet, sprite);
		}
		else
		{
			if (!sprite_exists(table, sprite))
				return -1;
			x0 = y0 = 2;
			w = SDL_min((int)get_sprite_width(table, sprite), ICON_SLOT - 4);
			h = SDL_min((int)get_sprite_height(table, sprite), ICON_SLOT - 4);
			blit_sprite(canvas, x0, y0, table, sprite);
		}
		static Uint32 rgba[ICON_SLOT * ICON_SLOT];
		for (int py = 0; py < ICON_SLOT; ++py)
			for (int px = 0; px < ICON_SLOT; ++px)
			{
				const Uint8 index = ((const Uint8 *)canvas->pixels)[py * canvas->pitch + px];
				rgba[py * ICON_SLOT + px] = index == 0 ? 0 : rgb_palette[index];
			}
		btbh_gpu_texture_update_rgba8(icon_texture, (const uint8_t *)rgba, (uint32_t)(slot * ICON_SLOT), 0, ICON_SLOT, ICON_SLOT);
		icon_slots[slot].sheet = sheet;
		icon_slots[slot].table = table;
		icon_slots[slot].sprite = sprite;
		icon_slots[slot].large = large;
		icon_slots[slot].palette = hash;
		icon_slots[slot].x0 = x0;
		icon_slots[slot].y0 = y0;
		icon_slots[slot].w = w;
		icon_slots[slot].h = h;
	}
	icon_slots[slot].used = text_frames;
	return slot;
}

static void icon_quad(int slot, float x, float y, float w, float h, float alpha)
{
	HudQuad *q = hud_quad_add();
	if (q == NULL)
		return;
	const float sx = (float)icon_slots[slot].x0, sy = (float)icon_slots[slot].y0;
	const float sw = (float)icon_slots[slot].w, sh = (float)icon_slots[slot].h;
	const float u0 = (slot * ICON_SLOT + sx) / (ICON_SLOT * ICON_SLOTS), u1 = (slot * ICON_SLOT + sx + sw) / (ICON_SLOT * ICON_SLOTS);
	const float v0 = sy / ICON_SLOT, v1 = (sy + sh) / ICON_SLOT;
	*q = (HudQuad){ x, y, w, h, u0, v0, u1, v1, { 1, 1, 1, alpha }, { 1, 1, 1, alpha }, .texture = icon_texture };
}

/*
 * The modern UI's icons drawn anew (data/hd/icons, TYR3D_EXPORT_PICTURES' icons/ through tools/upscale_sprites.py):
 * shop_<sprite>.png for the store's items (shopSpriteSheet's 2x2 sprites, as its cards show them), ship_, shipt_
 * (T2000's), ship_s_ (small), special_, option_ (the data cube icons) and planet_<sprite>.png for the planets of its
 * map (PLANET_SHAPES); where one is there, it is drawn instead of the
 * sprite's pixels, in the same rectangle (each loaded as it is first drawn).
 */
#define HD_ICONS 384
static struct
{
	const void *sheet;
	unsigned int table, sprite;
	bool large;
	BTBHGPUTexture *texture;  // (NULL: none drawn anew)
} hd_icons[HD_ICONS];
static int hd_icon_count = 0;

static BTBHGPUTexture *hd_icon(const void *sheet, unsigned int table, unsigned int sprite, bool large)
{
	// (The kinds TYR3D_EXPORT_PICTURES' icons/ has: the store's items, the ships, the HUD's small ship and bomb,
	// the specials, the data cube icons, the planets.)
	const char *kind = NULL;
	if (sheet == (const void *)&shopSpriteSheet && large)
		kind = "shop";
	else if (sheet == (const void *)&spriteSheet9)
		kind = large ? "ship" : "ship_s";
	else if (sheet == (const void *)&spriteSheetT2000 && large)
		kind = "shipt";
	else if (sheet == (const void *)&spriteSheet10 && large)
		kind = "special";
	else if (sheet == NULL && table == PLANET_SHAPES)
		kind = "planet";
	else if (sheet == NULL && table == OPTION_SHAPES)
		kind = "option";
	if (kind == NULL || window == NULL)
		return NULL;
	for (int i = 0; i < hd_icon_count; ++i)
		if (hd_icons[i].sheet == sheet && hd_icons[i].table == table && hd_icons[i].sprite == sprite && hd_icons[i].large == large)
			return hd_icons[i].texture;
	if (hd_icon_count >= HD_ICONS)
		return NULL;
	char dir[1024], path[1200];
	const char *base = tyr3d_resource_dir("TYR3D_UPSCALE_DIR", TYR3D_UPSCALE_DIR, "upscale", dir, sizeof(dir));
	snprintf(path, sizeof(path), "%s/icons/%s_%u.png", base, kind, sprite);
	BTBHGPUTexture *texture = NULL;
	if (SDL_GetPathInfo(path, NULL))
	{
		BTBHGPUTextureReport report;
		texture = btbh_gpu_window_texture_load_ex(window, path, 1, BTBH_GPU_TEXTURE_FILTER_LINEAR, BTBH_GPU_TEXTURE_WRAP_CLAMP,
		                                          BTBH_GPU_TEXTURE_COLOR_SPACE_LINEAR, &report);
	}
	hd_icons[hd_icon_count].sheet = sheet;
	hd_icons[hd_icon_count].table = table;
	hd_icons[hd_icon_count].sprite = sprite;
	hd_icons[hd_icon_count].large = large;
	hd_icons[hd_icon_count++].texture = texture;
	return texture;
}

static void hd_icon_quad(BTBHGPUTexture *texture, float x, float y, float w, float h, float alpha)
{
	HudQuad *q = hud_quad_add();
	if (q != NULL)
		*q = (HudQuad){ x, y, w, h, 0, 0, 1, 1, { 1, 1, 1, alpha }, { 1, 1, 1, alpha }, .texture = texture };
}

void rgpu_ui_sprite(const void *sheet, unsigned int sprite, bool large, float x, float y, float w, float h, float alpha)
{
	if (sheet == NULL || ((const Sprite2_array *)sheet)->data == NULL)
		return;
	BTBHGPUTexture *hd = hd_icon(sheet, 0, sprite, large);
	if (hd != NULL)
	{
		hd_icon_quad(hd, x, y, w, h, alpha);
		return;
	}
	const int slot = icon_slot(sheet, 0, sprite, large);
	if (slot >= 0)
		icon_quad(slot, x, y, w, h, alpha);
}

/*
 * The map's turning planets as 3D spheres (data/hd/planets/planet3d_<first sprite>.png, tools/planets3d.py: the
 * planet's surface put together from its 15 frames, rendered anew as a lit, turning sphere with its atmosphere, in
 * PLANET3D_FRAMES frames): wherever the UI shows one of a turning planet's frames (the store's map, the rogue run's
 * map), its sphere turns there instead, a turn every PLANET3D_TURN seconds, frame to frame crossfaded.
 */
#define PLANET3D_FRAMES 48
#define PLANET3D_COLUMNS 8
#define PLANET3D_ROWS 6
#define PLANET3D_RADIUS 0.78f  // the disc's radius, of a frame's half
#define PLANET3D_TURN 40.0f

static const int planet3d_first[] = { 3, 19, 35, 51, 67, 83, 99, 115, 131 };
static struct
{
	bool looked;
	BTBHGPUTexture *texture;
} planet3d[SDL_arraysize(planet3d_first)];

static bool planet3d_quad(unsigned int sprite, float x, float y, float w, float h, float alpha)
{
	int g = -1;
	for (int i = 0; i < (int)SDL_arraysize(planet3d_first) && g < 0; ++i)
		if ((int)sprite >= planet3d_first[i] - (i > 0) && (int)sprite <= planet3d_first[i] + 14)  // (16 a planet but the first's)
			g = i;
	if (g < 0 || window == NULL)
		return false;
	if (!planet3d[g].looked)
	{
		planet3d[g].looked = true;
		char dir[1024], path[1200];
		const char *base = tyr3d_resource_dir("TYR3D_UPSCALE_DIR", TYR3D_UPSCALE_DIR, "upscale", dir, sizeof(dir));
		snprintf(path, sizeof(path), "%s/planets/planet3d_%d.png", base, planet3d_first[g]);
		if (SDL_GetPathInfo(path, NULL))
		{
			BTBHGPUTextureReport report;
			planet3d[g].texture = btbh_gpu_window_texture_load_ex(window, path, 1, BTBH_GPU_TEXTURE_FILTER_LINEAR,
			                                                      BTBH_GPU_TEXTURE_WRAP_CLAMP, BTBH_GPU_TEXTURE_COLOR_SPACE_LINEAR, &report);
		}
	}
	if (planet3d[g].texture == NULL)
		return false;
	// The disc as wide as the sprite's (its mean size), the frame round it room for the halo; each planet its own
	// place in the turn.
	const float d = (w + h) / 2 / PLANET3D_RADIUS;
	const float qx = x + w / 2 - d / 2, qy = y + h / 2 - d / 2;
	const float turn = fmodf(SDL_GetTicks() / 1000.0f / PLANET3D_TURN + g * 0.37f, 1.0f) * PLANET3D_FRAMES;
	const int k0 = (int)turn % PLANET3D_FRAMES, k1 = (k0 + 1) % PLANET3D_FRAMES;
	const float f = turn - floorf(turn);
	for (int i = 0; i < 2; ++i)
	{
		const int k = i == 0 ? k0 : k1;
		const float a = i == 0 ? alpha : alpha * f;
		if (a <= 0.001f)
			continue;
		HudQuad *q = hud_quad_add();
		if (q == NULL)
			return true;
		const float u0 = (float)(k % PLANET3D_COLUMNS) / PLANET3D_COLUMNS, v0 = (float)(k / PLANET3D_COLUMNS) / PLANET3D_ROWS;
		*q = (HudQuad){ qx, qy, d, d, u0, v0, u0 + 1.0f / PLANET3D_COLUMNS, v0 + 1.0f / PLANET3D_ROWS, { 1, 1, 1, a }, { 1, 1, 1, a },
		                .texture = planet3d[g].texture };
	}
	return true;
}

void rgpu_ui_table_sprite(unsigned int table, unsigned int sprite, float x, float y, float w, float h, float alpha)
{
	if (table == PLANET_SHAPES && planet3d_quad(sprite, x, y, w, h, alpha))
		return;
	const int slot = icon_slot(NULL, table, sprite, false);
	if (slot < 0)
		return;
	// Fitted in the rectangle at its own aspect.
	const float aspect = (float)icon_slots[slot].w / SDL_max(icon_slots[slot].h, 1);
	float dw = w, dh = w / aspect;
	if (dh > h)
	{
		dh = h;
		dw = h * aspect;
	}
	BTBHGPUTexture *hd = hd_icon(NULL, table, sprite, false);
	if (hd != NULL)
		hd_icon_quad(hd, x + (w - dw) / 2, y + (h - dh) / 2, dw, dh, alpha);
	else
		icon_quad(slot, x + (w - dw) / 2, y + (h - dh) / 2, dw, dh, alpha);
}

/*
 * Pictures drawn anew (data/hd/pictures/pic_NN.png: tyrian.pic's pictures as TYR3D_EXPORT_PICTURES exports
 * them, drawn again at any size in the same frame, 16:10): where the modern UI shows one of the game's
 * pictures much as the game loaded it (the title, the menus' backgrounds, a story's picture), the new
 * picture shows under the screen's, which keeps only what the game drew on its picture (the logo, texts),
 * in the palette's colours; the new picture fades with the palette.
 */
#define HD_PICTURE_SAME 0.45f  // the share of the picture's own pixels the screen shows as loaded for the new one to show (a story's text covers some)

#define HD_PICTURE_TSHP2 (PCX_NUM + 1)  // tshp2.pcx, a story picture (]P0), after tyrian.pic's

static struct
{
	BTBHGPUTexture *texture;
	Uint8 *original;         // the picture as the game loads it
	SDL_Color palette[256];  // in its palette
	int uses[256];           // how many of its pixels have each colour
} hd_pictures[HD_PICTURE_TSHP2 + 1];

// tshp2.pcx as JE_loadPCX reads it: 320 x 200 run-length pixels after the header, its palette at the end.
static bool load_tshp2(Uint8 *pixels, SDL_Color *palette)
{
	char path[1024];
	snprintf(path, sizeof(path), "%s/tshp2.pcx", data_dir());
	size_t size = 0;
	Uint8 *data = SDL_LoadFile(path, &size);
	if (data == NULL || size < 128 + 769)
	{
		SDL_free(data);
		return false;
	}
	const Uint8 *pal = data + size - 769;
	for (int i = 0; i < 256; ++i)
		palette[i] = pal[0] == 12 ? (SDL_Color){ pal[1 + i * 3], pal[2 + i * 3], pal[3 + i * 3], 255 } : (SDL_Color){ 0, 0, 0, 255 };
	size_t at = 128;
	for (int i = 0; i < SCREEN_W * SCREEN_H && at < size;)
	{
		const Uint8 p = data[at++];
		if ((p & 0xc0) == 0xc0 && at < size)
		{
			const Uint8 v = data[at++];
			for (int k = 0; k < (p & 0x3f) && i < SCREEN_W * SCREEN_H; ++k)
				pixels[i++] = v;
		}
		else
			pixels[i++] = p;
	}
	SDL_free(data);
	return true;
}
static int hd_picture = 0;  // the picture shown anew this frame (0: none)
static float hd_picture_brightness = 1;  // how bright the palette is against the picture's own
static float hd_picture_white = 0;       // or how far it has faded to white

static void find_hd_pictures(void)
{
	static bool found = false;
	if (found || window == NULL)
		return;
	found = true;
	char dir[1024], path[1200];
	const char *base = tyr3d_resource_dir("TYR3D_UPSCALE_DIR", TYR3D_UPSCALE_DIR, "upscale", dir, sizeof(dir));
	SDL_Surface *surface = NULL;
	for (int n = 1; n <= HD_PICTURE_TSHP2; ++n)
	{
		if (n == HD_PICTURE_TSHP2)
			snprintf(path, sizeof(path), "%s/pictures/tshp2.png", base);
		else
			snprintf(path, sizeof(path), "%s/pictures/pic_%02d.png", base, n);
		if (!SDL_GetPathInfo(path, NULL))
			continue;
		BTBHGPUTextureReport report;
		BTBHGPUTexture *texture = btbh_gpu_window_texture_load_ex(window, path, 1, BTBH_GPU_TEXTURE_FILTER_LINEAR,
		                                                          BTBH_GPU_TEXTURE_WRAP_CLAMP, BTBH_GPU_TEXTURE_COLOR_SPACE_LINEAR,
		                                                          &report);
		if (surface == NULL)
			surface = SDL_CreateSurface(SCREEN_W, SCREEN_H, SDL_PIXELFORMAT_INDEX8);
		Uint8 *original = malloc(SCREEN_W * SCREEN_H);
		if (texture == NULL || surface == NULL || original == NULL)
		{
			free(original);
			fprintf(stderr, "warning: picture %s: %s\n", path, texture == NULL ? report.message : "no memory");
			continue;
		}
		if (n == HD_PICTURE_TSHP2)
		{
			if (!load_tshp2(original, hd_pictures[n].palette))
			{
				fprintf(stderr, "warning: picture %s: can't read tshp2.pcx in %s\n", path, data_dir());
				free(original);
				continue;
			}
		}
		else
		{
			// (JE_loadPic sets the game's colors too: kept as they were. Its palette is read when it is matched:
			// this may run before the game has loaded its palettes.)
			Palette kept;
			memcpy(kept, colors, sizeof(kept));
			JE_loadPic(surface, (JE_byte)n, false);
			memcpy(colors, kept, sizeof(kept));
			for (int y = 0; y < SCREEN_H; ++y)
				memcpy(original + y * SCREEN_W, (const Uint8 *)surface->pixels + y * surface->pitch, SCREEN_W);
		}
		hd_pictures[n].texture = texture;
		hd_pictures[n].original = original;
		for (int i = 0; i < SCREEN_W * SCREEN_H; ++i)
			++hd_pictures[n].uses[original[i]];
		printf("picture %d drawn anew: %s\n", n, path);
	}
	if (surface != NULL)
		SDL_DestroySurface(surface);
}

// The median of n values, each counted weight times (empty: none).
static float weighted_median(const float *v, const int *weight, int n, float none)
{
	long total = 0;
	for (int i = 0; i < n; ++i)
		total += weight[i];
	if (total == 0)
		return none;
	// (Few values: a selection by repeated minimum is fast enough.)
	static bool used[256];
	memset(used, 0, sizeof(used));
	long seen = 0;
	for (int k = 0; k < n; ++k)
	{
		int m = -1;
		for (int i = 0; i < n; ++i)
			if (!used[i] && (m < 0 || v[i] < v[m]))
				m = i;
		used[m] = true;
		seen += weight[m];
		if (seen * 2 >= total)
			return v[m];
	}
	return none;
}

// The picture drawn anew that the screen's picture is (0: none) and, if one, the screen's pixels in rgba
// only where the game drew over it (the rest clear).
static int match_hd_picture(const Uint8 *picture, Uint32 *rgba)
{
	find_hd_pictures();
	// (Counting the picture's own pixels, not its empty colour 0: a black screen is no picture.)
	int best = 0;
	float best_share = HD_PICTURE_SAME;
	for (int n = 1; n <= HD_PICTURE_TSHP2; ++n)
	{
		if (hd_pictures[n].original == NULL)
			continue;
		int same = 0, own = 0;
		for (int i = 0; i < SCREEN_W * SCREEN_H; ++i)
			if (hd_pictures[n].original[i] != 0)
			{
				++own;
				same += picture[i] == hd_pictures[n].original[i];
			}
		const float share = own > 0 ? same / (float)own : 0.0f;
		if (share > best_share)
		{
			best = n;
			best_share = share;
		}
	}
	if (SDL_getenv("TYR3D_DEBUG_PICTURES") != NULL)
		for (int n = 1; n <= HD_PICTURE_TSHP2; ++n)
			if (hd_pictures[n].original != NULL)
			{
				int same = 0;
				for (int i = 0; i < SCREEN_W * SCREEN_H; ++i)
					same += picture[i] == hd_pictures[n].original[i];
				printf("debug picture %d: same %.3f\n", n, same / (float)(SCREEN_W * SCREEN_H));
			}
	if (best == 0)
		return 0;
	const Uint8 *original = hd_pictures[best].original;
	for (int i = 0; i < SCREEN_W * SCREEN_H; ++i)
		if (picture[i] == original[i])
			rgba[i] = 0;
	// (The palette's fade since the picture was loaded in its own: towards black or white, the median over the
	// colours it has, weighed by their pixels, so that colours the screen animates (the title's) don't count.)
	const SDL_Color *own = best == HD_PICTURE_TSHP2 ? hd_pictures[best].palette : palettes[pcxpal[best - 1]];
	float dark[256], light[256];
	int weight[256], n = 0;
	for (int i = 0; i < 256; ++i)
	{
		const SDL_Color o = own[i];
		const int sum = o.r + o.g + o.b;
		if (hd_pictures[best].uses[i] == 0 || sum < 60 || sum > 3 * 230)
			continue;
		const Uint8 *c = (const Uint8 *)&rgb_palette[i];
		dark[n] = SDL_min((c[0] + c[1] + c[2]) / (float)sum, 1.0f);
		light[n] = SDL_clamp(((c[0] + c[1] + c[2]) - sum) / (float)(3 * 255 - sum), 0.0f, 1.0f);
		weight[n++] = hd_pictures[best].uses[i];
	}
	hd_picture_brightness = weighted_median(dark, weight, n, 1.0f);
	hd_picture_white = weighted_median(light, weight, n, 0.0f);
	if (hd_picture_white < 0.02f)
		hd_picture_white = 0;
	if (SDL_getenv("TYR3D_DEBUG_PICTURES") != NULL)
		printf("debug picture shown %d: share %.3f brightness %.3f white %.3f (%d colours)\n", best, best_share, hd_picture_brightness,
		       hd_picture_white, n);
	return best;
}

// A part of the picture drawn anew (screen pixels sx, sy, sw, sh) at x, y, w, h.
static void add_hd_picture(float sx, float sy, float sw, float sh, float x, float y, float w, float h, float alpha)
{
	HudQuad *q = hud_quad_add();
	if (q == NULL)
		return;
	const float b = hd_picture_brightness;
	*q = (HudQuad){ x, y, w, h, sx / SCREEN_W, sy / SCREEN_H, (sx + sw) / SCREEN_W, (sy + sh) / SCREEN_H, { b, b, b, alpha },
	                { b, b, b, alpha }, .texture = hd_pictures[hd_picture].texture };
	if (hd_picture_white > 0 && (q = hud_quad_add()) != NULL)  // (a fade to white over it)
		*q = (HudQuad){ x, y, w, h, 0, 0, 1, 1, { 1, 1, 1, alpha * hd_picture_white }, { 1, 1, 1, alpha * hd_picture_white } };
}

/*
 * The title's logo drawn anew (data/hd/pictures/logo_tyrian.png and logo_2000.png, from the export's logo_*.png,
 * redrawn in the same frame at any size): over the title's picture (4), where the screen shows the logo's sprite
 * (PLANET_SHAPES 146 at x 11, its 2000(tm) 151 at x 155, at any height: they fly in), the new logo shows in its
 * box, the screen's pixels of the sprite taken off.
 */
#define HD_LOGO_PICTURE 4
#define HD_LOGO_SAME 0.85f  // the share of the sprite's pixels the screen shows for the new logo to show

static struct
{
	const char *file;
	unsigned int sprite;
	int x;
	BTBHGPUTexture *texture;
	Uint8 *pixels, *mask;  // the sprite as drawn (made when first needed: the shapes load late)
	int w, h;
	bool made;
	int shown_y;  // where it shows this frame, or INT_MIN
} hd_logos[] = { { "logo_tyrian.png", 146, 11 }, { "logo_2000.png", 151, 155 } };

static void load_hd_logos(void)
{
	static bool loaded = false;
	if (loaded || window == NULL)
		return;
	loaded = true;
	char dir[1024], path[1200];
	const char *base = tyr3d_resource_dir("TYR3D_UPSCALE_DIR", TYR3D_UPSCALE_DIR, "upscale", dir, sizeof(dir));
	for (size_t l = 0; l < COUNTOF(hd_logos); ++l)
	{
		snprintf(path, sizeof(path), "%s/pictures/%s", base, hd_logos[l].file);
		if (!SDL_GetPathInfo(path, NULL))
			continue;
		BTBHGPUTextureReport report;
		hd_logos[l].texture = btbh_gpu_window_texture_load_ex(window, path, 1, BTBH_GPU_TEXTURE_FILTER_LINEAR, BTBH_GPU_TEXTURE_WRAP_CLAMP,
		                                                      BTBH_GPU_TEXTURE_COLOR_SPACE_LINEAR, &report);
		if (hd_logos[l].texture != NULL)
			printf("logo drawn anew: %s\n", path);
	}
}

// The sprite's pixels as blit_sprite draws them.
static bool make_logo_sprite(size_t l)
{
	if (hd_logos[l].made)
		return hd_logos[l].pixels != NULL;
	if (!sprite_exists(PLANET_SHAPES, hd_logos[l].sprite))
		return false;  // (not loaded yet: tried again)
	hd_logos[l].made = true;
	const Sprite *sp = sprite(PLANET_SHAPES, hd_logos[l].sprite);
	SDL_Surface *surface = SDL_CreateSurface(SCREEN_W, SCREEN_H, SDL_PIXELFORMAT_INDEX8);
	if (surface == NULL || sp->width > SCREEN_W || sp->height > SCREEN_H)
	{
		SDL_DestroySurface(surface);
		return false;
	}
	SDL_FillSurfaceRect(surface, NULL, 0);
	blit_sprite(surface, 0, 0, PLANET_SHAPES, hd_logos[l].sprite);
	const int w = sp->width, h = sp->height;
	hd_logos[l].pixels = malloc((size_t)w * h);
	hd_logos[l].mask = malloc((size_t)w * h);
	if (hd_logos[l].pixels == NULL || hd_logos[l].mask == NULL)
	{
		SDL_DestroySurface(surface);
		return false;
	}
	for (int y = 0; y < h; ++y)
		for (int x = 0; x < w; ++x)
		{
			const Uint8 v = ((const Uint8 *)surface->pixels)[y * surface->pitch + x];
			hd_logos[l].pixels[y * w + x] = v;
			hd_logos[l].mask[y * w + x] = v != 0;
		}
	hd_logos[l].w = w;
	hd_logos[l].h = h;
	SDL_DestroySurface(surface);
	return true;
}

// Where the screen (picture: its pixels) shows the logos, their pixels taken off rgba.
static void find_hd_logos(const Uint8 *picture, Uint32 *rgba)
{
	load_hd_logos();
	for (size_t l = 0; l < COUNTOF(hd_logos); ++l)
	{
		hd_logos[l].shown_y = INT_MIN;
		if (hd_picture != HD_LOGO_PICTURE || hd_logos[l].texture == NULL || !make_logo_sprite(l))
			continue;
		const int w = hd_logos[l].w, h = hd_logos[l].h, x0 = hd_logos[l].x;
		if (x0 < 0 || x0 + w > SCREEN_W)
			continue;
		int best_y = INT_MIN;
		float best = HD_LOGO_SAME;
		for (int y0 = 0; y0 + h <= SCREEN_H; ++y0)
		{
			int same = 0, all = 0;
			for (int y = 0; y < h; y += 3)  // (every third row: enough to find it)
				for (int x = 0; x < w; ++x)
					if (hd_logos[l].mask[y * w + x])
					{
						++all;
						same += picture[(y0 + y) * SCREEN_W + x0 + x] == hd_logos[l].pixels[y * w + x];
					}
			if (all > 0 && same / (float)all > best)
			{
				best = same / (float)all;
				best_y = y0;
			}
		}
		if (best_y == INT_MIN)
			continue;
		hd_logos[l].shown_y = best_y;
		for (int y = 0; y < h; ++y)
			for (int x = 0; x < w; ++x)
				if (hd_logos[l].mask[y * w + x] && picture[(best_y + y) * SCREEN_W + x0 + x] == hd_logos[l].pixels[y * w + x])
					rgba[(best_y + y) * SCREEN_W + x0 + x] = 0;
	}
}

// The logos found, drawn anew in their boxes on the screen shown at dst.
static void add_hd_logos(const SDL_Rect *dst)
{
	const float kx = dst->w / (float)SCREEN_W, ky = dst->h / (float)SCREEN_H;
	// (Where the picture is cut at the top to fill a wide window, the logo resting near its top comes down as much
	// as it takes to show whole.)
	float top = (float)INT_MAX;
	for (size_t l = 0; l < COUNTOF(hd_logos); ++l)
		if (hd_logos[l].shown_y != INT_MIN)
			top = SDL_min(top, dst->y + hd_logos[l].shown_y * ky);
	const float down = SDL_max(dst->h * 0.012f - top, 0.0f);
	for (size_t l = 0; l < COUNTOF(hd_logos); ++l)
	{
		if (hd_logos[l].shown_y == INT_MIN)
			continue;
		HudQuad *q = hud_quad_add();
		if (q == NULL)
			return;
		const float b = hd_picture_brightness;
		*q = (HudQuad){ dst->x + hd_logos[l].x * kx, dst->y + hd_logos[l].shown_y * ky + down, hd_logos[l].w * kx, hd_logos[l].h * ky, 0, 0, 1, 1,
		                { b, b, b, 1 }, { b, b, b, 1 }, .texture = hd_logos[l].texture };
	}
}

/*
 * The data cubes' faces drawn anew (data/hd/pictures/face_NN.png, tools/hd_pictures.py: each over the store's
 * portrait, FACE_BOX, clear but for the portrait's window, cut to its shape): where the screen shows a face as the
 * store draws it (FACE_SHAPES centred on FACE_CENTRE: game_menu.c), its pixels give way to the window's colour and
 * the face is drawn over the portrait, as bright as the palette has faded its own colours.
 */
#define FACE_BOX_X 1
#define FACE_BOX_Y 1
#define FACE_BOX_W 145
#define FACE_BOX_H 170
#define FACE_CENTRE_X 77
#define FACE_CENTRE_Y 92
#define FACE_WINDOW_X 76  // a pixel of the window above every face (its colour, the window's)
#define FACE_WINDOW_Y 47
#define HD_FACES 32
#define HD_FACE_SAME 0.9f  // the share of the face's pixels the screen shows for the new one to show
static struct
{
	char path[1200];  // its picture ("": none)
	bool looked;
	BTBHGPUTexture *texture;  // (loaded as it first shows)
	bool loaded;
	bool made;
	Uint8 *pixels;  // the face as blit_sprite draws it (0: clear)
	int w, h;
} hd_faces[HD_FACES + 1];
#define HD_FACE_NONE HD_FACES  // (pictures/face_none.png: what the window shows for a cube without a face)
static int hd_face = -1;  // the face drawn anew this frame (-1: none)
static float hd_face_brightness = 1;
// The portrait's frame drawn anew (data/hd/pictures/portrait_frame.png, tools/hd_pictures.py --frame-hd: over the
// whole portrait, clear in its window): where the screen shows the frame as the store draws it (OPTION_SHAPES 20 at
// FACE_BOX's corner), it is drawn over it, under the face.
#define FRAME_SPRITE 20
static struct
{
	char path[1200];
	bool looked, made, loaded;
	BTBHGPUTexture *texture;
	Uint8 *pixels;  // the frame in the portrait's box as blit_sprite draws it (0: clear)
} hd_frame;
static bool hd_frame_shown = false;
static float hd_frame_brightness = 1;

// The frame's pixels in the portrait's box (false: not there, or no frame drawn anew).
static bool make_hd_frame(void)
{
	if (!hd_frame.looked)
	{
		hd_frame.looked = true;
		char dir[1024];
		const char *base = tyr3d_resource_dir("TYR3D_UPSCALE_DIR", TYR3D_UPSCALE_DIR, "upscale", dir, sizeof(dir));
		snprintf(hd_frame.path, sizeof(hd_frame.path), "%s/pictures/portrait_frame.png", base);
		if (!SDL_GetPathInfo(hd_frame.path, NULL))
			hd_frame.path[0] = '\0';
	}
	if (hd_frame.path[0] == '\0')
		return false;
	if (hd_frame.made)
		return hd_frame.pixels != NULL;
	if (!sprite_exists(OPTION_SHAPES, FRAME_SPRITE))
		return false;  // (not loaded yet: tried again)
	hd_frame.made = true;
	SDL_Surface *surface = SDL_CreateSurface(SCREEN_W, SCREEN_H, SDL_PIXELFORMAT_INDEX8);
	hd_frame.pixels = surface != NULL ? malloc((size_t)FACE_BOX_W * FACE_BOX_H) : NULL;
	if (hd_frame.pixels != NULL)
	{
		SDL_FillSurfaceRect(surface, NULL, 0);
		blit_sprite(surface, FACE_BOX_X, FACE_BOX_Y, OPTION_SHAPES, FRAME_SPRITE);
		for (int y = 0; y < FACE_BOX_H; ++y)
			memcpy(&hd_frame.pixels[y * FACE_BOX_W], (const Uint8 *)surface->pixels + (FACE_BOX_Y + y) * surface->pitch + FACE_BOX_X,
			       FACE_BOX_W);
	}
	SDL_DestroySurface(surface);
	return hd_frame.pixels != NULL;
}

// Whether the screen shows the frame; if so its brightness against the store's palette, its picture loaded.
static void find_hd_frame(const Uint8 *picture)
{
	hd_frame_shown = false;
	if (!make_hd_frame())
		return;
	int same = 0, own = 0;
	int uses[256] = { 0 };
	for (int y = 0; y < FACE_BOX_H; y += 2)
		for (int x = 0; x < FACE_BOX_W; ++x)
		{
			const Uint8 v = hd_frame.pixels[y * FACE_BOX_W + x];
			if (v == 0)
				continue;
			++own;
			++uses[v];
			same += picture[(FACE_BOX_Y + y) * SCREEN_W + FACE_BOX_X + x] == v;
		}
	if (own == 0 || same < own * HD_FACE_SAME)
		return;
	if (!hd_frame.loaded && window != NULL)
	{
		hd_frame.loaded = true;
		BTBHGPUTextureReport report;
		hd_frame.texture = btbh_gpu_window_texture_load_ex(window, hd_frame.path, 1, BTBH_GPU_TEXTURE_FILTER_LINEAR,
		                                                   BTBH_GPU_TEXTURE_WRAP_CLAMP, BTBH_GPU_TEXTURE_COLOR_SPACE_LINEAR, &report);
		if (hd_frame.texture != NULL)
			printf("portrait frame drawn anew: %s\n", hd_frame.path);
	}
	if (hd_frame.texture == NULL)
		return;
	const SDL_Color *store = palettes[pcxpal[0]];
	float dark[256];
	int weight[256], n = 0;
	for (int i = 1; i < 256; ++i)
	{
		const int sum = store[i].r + store[i].g + store[i].b;
		if (uses[i] == 0 || sum < 60)
			continue;
		const Uint8 *c = (const Uint8 *)&rgb_palette[i];
		dark[n] = SDL_min((c[0] + c[1] + c[2]) / (float)sum, 1.0f);
		weight[n++] = uses[i];
	}
	hd_frame_brightness = weighted_median(dark, weight, n, 1.0f);
	hd_frame_shown = true;
}

// The face's pixels as blit_sprite draws them (false: not there, or no face drawn anew for it).
static bool make_hd_face(int i)
{
	if (!hd_faces[i].looked)
	{
		hd_faces[i].looked = true;
		char dir[1024];
		const char *base = tyr3d_resource_dir("TYR3D_UPSCALE_DIR", TYR3D_UPSCALE_DIR, "upscale", dir, sizeof(dir));
		snprintf(hd_faces[i].path, sizeof(hd_faces[i].path), "%s/pictures/face_%02d.png", base, i + 1);
		if (!SDL_GetPathInfo(hd_faces[i].path, NULL))
			hd_faces[i].path[0] = '\0';
	}
	if (hd_faces[i].path[0] == '\0')
		return false;
	if (hd_faces[i].made)
		return hd_faces[i].pixels != NULL;
	if (!sprite_exists(FACE_SHAPES, (unsigned int)i))
		return false;  // (not loaded yet: tried again)
	hd_faces[i].made = true;
	const Sprite *sp = sprite(FACE_SHAPES, (unsigned int)i);
	SDL_Surface *surface = SDL_CreateSurface(SCREEN_W, SCREEN_H, SDL_PIXELFORMAT_INDEX8);
	if (surface == NULL || sp->width > FACE_BOX_W || sp->height > FACE_BOX_H)
	{
		SDL_DestroySurface(surface);
		return false;
	}
	SDL_FillSurfaceRect(surface, NULL, 0);
	blit_sprite(surface, 0, 0, FACE_SHAPES, (unsigned int)i);
	const int w = sp->width, h = sp->height;
	hd_faces[i].pixels = malloc((size_t)w * h);
	if (hd_faces[i].pixels != NULL)
		for (int y = 0; y < h; ++y)
			memcpy(&hd_faces[i].pixels[y * w], (const Uint8 *)surface->pixels + y * surface->pitch, (size_t)w);
	hd_faces[i].w = w;
	hd_faces[i].h = h;
	SDL_DestroySurface(surface);
	return hd_faces[i].pixels != NULL;
}

static void find_hd_face(const Uint8 *picture, Uint32 *rgba)
{
	find_hd_frame(picture);
	hd_face = -1;
	const int count = SDL_min((int)sprite_table[FACE_SHAPES].count, HD_FACES);
	for (int i = 0; i < count && hd_face < 0; ++i)
	{
		if (!make_hd_face(i))
			continue;
		const int w = hd_faces[i].w, h = hd_faces[i].h, x0 = FACE_CENTRE_X - w / 2, y0 = FACE_CENTRE_Y - h / 2;
		int same = 0, own = 0;
		for (int y = 0; y < h; y += 2)
			for (int x = 0; x < w; ++x)
				if (hd_faces[i].pixels[y * w + x] != 0)
				{
					++own;
					same += picture[(y0 + y) * SCREEN_W + x0 + x] == hd_faces[i].pixels[y * w + x];
				}
		if (own > 0 && same >= own * HD_FACE_SAME)
			hd_face = i;
	}
	// A data cube without a face (a message, a guide): the frame round an empty window; its picture there.
	if (hd_face < 0 && hd_frame_shown)
	{
		// (The window's glass has a few highlights of its own; a face covers most of it.)
		const Uint8 empty = picture[FACE_WINDOW_Y * SCREEN_W + FACE_WINDOW_X];
		int other = 0, all = 0;
		for (int y = FACE_CENTRE_Y - 40; y <= FACE_CENTRE_Y + 40; y += 2)
			for (int x = FACE_CENTRE_X - 30; x <= FACE_CENTRE_X + 30; ++x, ++all)
				other += picture[y * SCREEN_W + x] != empty;
		const bool clear = other * 8 < all;
		if (clear)
		{
			if (!hd_faces[HD_FACE_NONE].looked)
			{
				hd_faces[HD_FACE_NONE].looked = true;
				char dir[1024];
				const char *base = tyr3d_resource_dir("TYR3D_UPSCALE_DIR", TYR3D_UPSCALE_DIR, "upscale", dir, sizeof(dir));
				snprintf(hd_faces[HD_FACE_NONE].path, sizeof(hd_faces[0].path), "%s/pictures/face_none.png", base);
				if (!SDL_GetPathInfo(hd_faces[HD_FACE_NONE].path, NULL))
					hd_faces[HD_FACE_NONE].path[0] = '\0';
			}
			if (hd_faces[HD_FACE_NONE].path[0] != '\0')
				hd_face = HD_FACE_NONE;
		}
	}
	if (hd_face >= 0 && !hd_faces[hd_face].loaded && window != NULL)
	{
		hd_faces[hd_face].loaded = true;
		BTBHGPUTextureReport report;
		hd_faces[hd_face].texture = btbh_gpu_window_texture_load_ex(window, hd_faces[hd_face].path, 1, BTBH_GPU_TEXTURE_FILTER_LINEAR,
		                                                            BTBH_GPU_TEXTURE_WRAP_CLAMP, BTBH_GPU_TEXTURE_COLOR_SPACE_LINEAR, &report);
		if (hd_faces[hd_face].texture != NULL)
			printf("face drawn anew: %s\n", hd_faces[hd_face].path);
	}
	if (hd_face < 0 || hd_faces[hd_face].texture == NULL)
	{
		hd_face = -1;
		return;
	}
	if (hd_face == HD_FACE_NONE)
	{
		hd_face_brightness = hd_frame_brightness;  // (in the store's palette, as the frame)
		return;
	}
	const int w = hd_faces[hd_face].w, h = hd_faces[hd_face].h, x0 = FACE_CENTRE_X - w / 2, y0 = FACE_CENTRE_Y - h / 2;
	// (Its palette's fade, as a picture's: the median over its colours, weighed by their pixels.)
	const SDL_Color *own = palettes[hd_face < (int)COUNTOF(facepal) ? facepal[hd_face] : 0];
	int uses[256] = { 0 };
	for (int i = 0; i < w * h; ++i)
		++uses[hd_faces[hd_face].pixels[i]];
	float dark[256];
	int weight[256], n = 0;
	for (int i = 1; i < 256; ++i)
	{
		const int sum = own[i].r + own[i].g + own[i].b;
		if (uses[i] == 0 || sum < 60)
			continue;
		const Uint8 *c = (const Uint8 *)&rgb_palette[i];
		dark[n] = SDL_min((c[0] + c[1] + c[2]) / (float)sum, 1.0f);
		weight[n++] = uses[i];
	}
	hd_face_brightness = weighted_median(dark, weight, n, 1.0f);
	const Uint32 window_colour = rgba[FACE_WINDOW_Y * SCREEN_W + FACE_WINDOW_X];
	for (int y = 0; y < h; ++y)
		for (int x = 0; x < w; ++x)
			rgba[(y0 + y) * SCREEN_W + x0 + x] = window_colour;
}

// The face found drawn anew over the portrait, in the part of the screen (sx, sy, sw, sh) drawn at x, y, w, h.
static void add_hd_face(float sx, float sy, float sw, float sh, float x, float y, float w, float h, float alpha)
{
	if (sw <= 0 || sh <= 0)
		return;
	const float kx = w / sw, ky = h / sh;
	const float bx = x + (FACE_BOX_X - sx) * kx, by = y + (FACE_BOX_Y - sy) * ky, bw = FACE_BOX_W * kx, bh = FACE_BOX_H * ky;
	// (The frame first, the face in its window over it.)
	if (hd_frame_shown)
	{
		HudQuad *q = hud_quad_add();
		if (q == NULL)
			return;
		const float b = hd_frame_brightness;
		*q = (HudQuad){ bx, by, bw, bh, 0, 0, 1, 1, { b, b, b, alpha }, { b, b, b, alpha }, .texture = hd_frame.texture };
	}
	if (hd_face < 0)
		return;
	HudQuad *q = hud_quad_add();
	if (q == NULL)
		return;
	const float b = hd_face_brightness;
	*q = (HudQuad){ bx, by, bw, bh, 0, 0, 1, 1, { b, b, b, alpha }, { b, b, b, alpha }, .texture = hd_faces[hd_face].texture };
}

void rgpu_ui_picture(float sx, float sy, float sw, float sh, float x, float y, float w, float h, float alpha)
{
	if (sw <= 0 || sh <= 0)
		return;
	if (hd_picture != 0)
		add_hd_picture(sx, sy, sw, sh, x, y, w, h, alpha);
	HudQuad *q = hud_quad_add();
	if (q == NULL)
		return;
	*q = (HudQuad){ x, y, w, h, sx / SCREEN_W, sy / SCREEN_H, (sx + sw) / SCREEN_W, (sy + sh) / SCREEN_H, { 1, 1, 1, alpha }, { 1, 1, 1, alpha },
	                .texture = screen_texture, .picture = true };
	picture_magnification = SDL_max(picture_magnification, h * text_density / sh);
	// (A face drawn anew over the store's portrait, when the part holds it.)
	if (sx <= FACE_BOX_X && sy <= FACE_BOX_Y && sx + sw >= FACE_BOX_X + FACE_BOX_W && sy + sh >= FACE_BOX_Y + FACE_BOX_H)
		add_hd_face(sx, sy, sw, sh, x, y, w, h, alpha);
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
	// (ndc - ndc_offset) / ndc_scale * tan_half (ndc_slopes).
	float ndc_scale[2], ndc_offset[2];
	float tan_half[2];
	bool sideways;  // the view turned clockwise: its up is the window's right
} Camera3D;

// The view ray's slopes (along the camera's right and up) through a window position in NDC.
static void ndc_slopes(const Camera3D *camera, const float ndc[2], float slope[2])
{
	if (camera->sideways)
	{
		// Window x = ndc_scale[0] * view y + ndc_offset[0]; window y = -ndc_scale[1] * view x + ...
		slope[0] = (camera->ndc_offset[1] - ndc[1]) / camera->ndc_scale[1] * camera->tan_half[0];
		slope[1] = (ndc[0] - camera->ndc_offset[0]) / camera->ndc_scale[0] * camera->tan_half[1];
		return;
	}
	for (int i = 0; i < 2; ++i)
		slope[i] = (ndc[i] - camera->ndc_offset[i]) / camera->ndc_scale[i] * camera->tan_half[i];
}

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
// playfield on upside-down levels; sideways turns it clockwise into the rectangle (which is then
// as tall as the playfield is wide), so the level scrolls from left to right.
static Camera3D fit_camera(float reference_height, float viewport_aspect, const float ndc_rect[4], bool upside_down,
                           bool sideways)
{
	const float theta = rgpu_camera.tilt_degrees * (float)M_PI / 180.0f;
	const float t = tanf(rgpu_camera.fov_degrees * (float)M_PI / 360.0f);
	const float c = cosf(theta), s = sinf(theta);

	const float forward[3] = { 0, -c, -s };
	const float up[3] = { 0, s, -c };
	const float right[3] = { 1, 0, 0 };

	// Camera-space depth and height of the bottom edge's centre (the playfield's: wide or the
	// original's, l3d_field_x/w).
	const float half_width = l3d_field_w() / 2.0f;
	const float depth = half_width / (t * viewport_aspect);
	const float height = -t * depth;

	const float bottom[3] = { l3d_field_x() + half_width, reference_height, L3D_PLAYFIELD_H };
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
	if (sideways)
	{
		post.m[4] = sx;   // window x from the view's y
		post.m[1] = -sy;  // window y from the view's x
	}
	else
	{
		post.m[0] = sx;
		post.m[5] = upside_down ? -sy : sy;
	}
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
	camera.sideways = sideways;
	return camera;
}

// How far up the level the background maps are drawn (game pixels above the screen's top edge),
// and the distance over which they fade out before that.
// (Seen from the side, the window shows further ahead.)
#define BACKGROUND_AHEAD (l3d_sideways ? 1100.0f : 640.0f)
#define BACKGROUND_FADE 160.0f

/*
 * What the game plays in is its playfield only (264 x 184, and l3d_field_ahead above it: shots,
 * hits, enemies are there); the view shows the world around it too. Around the playfield as the
 * window shows it (its corners on the player's plane, the same on every layer as the layers are
 * aligned), the view is darkened, a soft edge first, so what can be played is what is bright:
 * what is outside it (enemies coming, leaving) shows dimmed. Black quads put first among the
 * HUD's, under its gauges and texts; not over the classic panel (clip_x, the panel's left edge).
 */
#define OUTSIDE_SHADE 0.5f    // opacity of the black outside the playfield
#define OUTSIDE_EDGE 0.15f    // the soft edge's width, of the window's height (wide: with 0.65 over 0.022 of it,
                              // uniform ground (sea, ice, snow) read as a lit table top over a dark void)

static int shade_quads(HudQuad *out, int max, float (*pts)[3], int n, float clip_x)
{
	// Clipped to x <= clip_x (Sutherland-Hodgman, opacity along), then a fan of triangles.
	float clipped[8][3];
	int m = 0;
	for (int i = 0; i < n && m < 7; ++i)
	{
		const float *a = pts[i], *b = pts[(i + 1) % n];
		const bool ina = a[0] <= clip_x, inb = b[0] <= clip_x;
		if (ina)
			memcpy(clipped[m++], a, sizeof(clipped[0]));
		if (ina != inb && m < 8)
		{
			const float t = (clip_x - a[0]) / (b[0] - a[0]);
			for (int k = 0; k < 3; ++k)
				clipped[m][k] = a[k] + (b[k] - a[k]) * t;
			++m;
		}
	}
	int count = 0;
	for (int i = 1; i + 1 < m && count < max; ++i)
	{
		const float *v[4] = { clipped[0], clipped[i], clipped[i + 1], clipped[i + 1] };
		HudQuad *q = &out[count++];
		*q = (HudQuad){ .poly = true };
		for (int k = 0; k < 4; ++k)
		{
			q->px[k] = v[k][0];
			q->py[k] = v[k][1];
			q->pa[k] = v[k][2];
		}
	}
	return count;
}

static void add_outside_shade(const Camera3D *camera, float reference, float clip_x, float window_w, float window_h)
{
	const float top = (float)-l3d_field_ahead, x0 = (float)l3d_field_x(), x1 = (float)(l3d_field_x() + l3d_field_w());
	const float game[4][2] = { { x0, top }, { x1, top }, { x1, L3D_PLAYFIELD_H }, { x0, L3D_PLAYFIELD_H } };
	float p[4][2], centre[2] = { 0, 0 };
	for (int i = 0; i < 4; ++i)
	{
		const float *m = camera->view_projection.m;
		const float v[4] = { game[i][0], reference, game[i][1], 1 };
		float clip[4];
		for (int r = 0; r < 4; ++r)
			clip[r] = m[r] * v[0] + m[4 + r] * v[1] + m[8 + r] * v[2] + m[12 + r] * v[3];
		if (clip[3] <= 1e-6f)
			return;
		p[i][0] = (clip[0] / clip[3] + 1) / 2 * window_w;
		p[i][1] = (1 - clip[1] / clip[3]) / 2 * window_h;
		centre[0] += p[i][0] / 4;
		centre[1] += p[i][1] / 4;
	}
	// Each edge's outward normal.
	float normal[4][2];
	for (int i = 0; i < 4; ++i)
	{
		const float *a = p[i], *b = p[(i + 1) % 4];
		float nx = b[1] - a[1], ny = a[0] - b[0];
		const float len = SDL_max(sqrtf(nx * nx + ny * ny), 1e-3f);
		nx /= len, ny /= len;
		if ((a[0] - centre[0]) * nx + (a[1] - centre[1]) * ny < 0)
			nx = -nx, ny = -ny;
		normal[i][0] = nx;
		normal[i][1] = ny;
	}
	const float soft = OUTSIDE_EDGE * window_h, far = 4.0f * (window_w + window_h), a = OUTSIDE_SHADE;
	HudQuad made[64];
	int count = 0;
	for (int i = 0; i < 4; ++i)
	{
		const float *pa = p[i], *pb = p[(i + 1) % 4], *n = normal[i], *np = normal[(i + 3) % 4];
		float band[4][3] = { { pa[0], pa[1], 0 }, { pb[0], pb[1], 0 },
		                     { pb[0] + soft * n[0], pb[1] + soft * n[1], a }, { pa[0] + soft * n[0], pa[1] + soft * n[1], a } };
		float solid[4][3] = { { band[3][0], band[3][1], a }, { band[2][0], band[2][1], a },
		                      { pb[0] + far * n[0], pb[1] + far * n[1], a }, { pa[0] + far * n[0], pa[1] + far * n[1], a } };
		// The corner at pa, between the edge before's extrusion and this one's.
		float corner_soft[3][3] = { { pa[0], pa[1], 0 }, { pa[0] + soft * np[0], pa[1] + soft * np[1], a },
		                            { pa[0] + soft * n[0], pa[1] + soft * n[1], a } };
		float corner[4][3] = { { pa[0] + soft * np[0], pa[1] + soft * np[1], a }, { pa[0] + far * np[0], pa[1] + far * np[1], a },
		                       { pa[0] + far * n[0], pa[1] + far * n[1], a }, { pa[0] + soft * n[0], pa[1] + soft * n[1], a } };
		count += shade_quads(made + count, (int)COUNTOF(made) - count, band, 4, clip_x);
		count += shade_quads(made + count, (int)COUNTOF(made) - count, solid, 4, clip_x);
		count += shade_quads(made + count, (int)COUNTOF(made) - count, corner_soft, 3, clip_x);
		count += shade_quads(made + count, (int)COUNTOF(made) - count, corner, 4, clip_x);
	}
	if (count <= 0 || !hud_quads_room(count))
		return;
	memmove(hud_quads + count, hud_quads, sizeof(hud_quads[0]) * (size_t)hud_quad_count);
	memcpy(hud_quads, made, sizeof(made[0]) * (size_t)count);
	hud_quad_count += count;
	if (hud_under > 0)
		hud_under += count;  // (with the HUD's, under a menu)
}

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

// How an object leans (ObjectLean), applied to it as placed in the world (aligned): turned about its pivot
// so that its base lies along the ground's slope (its yaw stays), then each point moved along the camera's
// ray through the pivot by as much as the lean raised it, so that it is seen where the game draws it, as
// alignment keeps what stands higher (to first order; what stands up from it leans with it).
static Mat4 lean_matrix(float sx, float sz, float x, float y, float height)
{
	const float k = align_scale(height);
	const float px = align.cx + (x - align.cx) * k, py = height, pz = align.cz + (y - align.cz) * k;
	const float length = sqrtf(sx * sx + 1 + sz * sz);
	const float nx = -sx / length, ny = 1 / length, nz = -sz / length;  // (the ground's normal)
	const float f = 1 / (1 + ny);
	// The turn taking up to the normal, about the axis across both (column-major: m[column * 4 + row]).
	Mat4 r = mat4_identity();
	r.m[0] = ny + f * nz * nz;
	r.m[1] = -nx;
	r.m[2] = -f * nx * nz;
	r.m[4] = nx;
	r.m[5] = ny;
	r.m[6] = nz;
	r.m[8] = -f * nx * nz;
	r.m[9] = -nz;
	r.m[10] = ny + f * nx * nx;
	r.m[12] = px - (r.m[0] * px + r.m[4] * py + r.m[8] * pz);
	r.m[13] = py - (r.m[1] * px + r.m[5] * py + r.m[9] * pz);
	r.m[14] = pz - (r.m[2] * px + r.m[6] * py + r.m[10] * pz);
	// Raised by sx (x - px) + sz (z - pz): that much along the ray towards the camera.
	const float d = SDL_max(align.cy - py, 1.0f);
	const float dx = align.on ? -(px - align.cx) / d : 0.0f, dz = align.on ? -(pz - align.cz) / d : 0.0f;
	Mat4 c = mat4_identity();
	c.m[0] = 1 + dx * sx;
	c.m[8] = dx * sz;
	c.m[12] = -dx * (sx * px + sz * pz);
	c.m[2] = dz * sx;
	c.m[10] = 1 + dz * sz;
	c.m[14] = -dz * (sx * px + sz * pz);
	return mat4_mul(&c, &r);
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
		ndc_slopes(camera, ndc, slope);
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

// Palette colours with JE_filterScreen's hue and brightness (-99: none) applied as a palette-index remap,
// from the given palette (rgb_palette's packing).
static void filter_colors(int hue, int brightness, const Uint32 palette[256], Uint32 colors[256])
{
	Uint8 remap[256];
	for (int i = 0; i < 256; ++i)
	{
		int index = i;
		if (hue != -99)
			index = (hue << 4) | (index & 0x0f);
		if (brightness != -99)
		{
			const int value = (index & 0x0f) + brightness;
			index = (index & 0xf0) | (value < 0 || value >= 0x1f ? 0 : (value >= 0x0f ? 0x0f : value));
		}
		remap[i] = (Uint8)index;
	}

	for (int i = 0; i < 256; ++i)
		colors[i] = palette[remap[i]];
}

// The palette as the frame shows it (the level's filters), from the given palette.
static void frame_colors_of(const L3DFrame *frame, const Uint32 palette[256], Uint32 colors[256])
{
	filter_colors(frame->filter_hue, frame->filter_brightness, palette, colors);
}

static float srgb_to_linear(Uint8 value);

// The colours' brightness against others', in linear light.
static double linear_ratio(const Uint32 colors[256], const Uint32 against[256])
{
	double now = 0, full = 0;
	for (int i = 1; i < 256; ++i)
	{
		const Uint8 *a = (const Uint8 *)&colors[i], *b = (const Uint8 *)&against[i];
		for (int k = 0; k < 3; ++k)
		{
			now += srgb_to_linear(a[k]);
			full += srgb_to_linear(b[k]);
		}
	}
	return full > 0 ? now / full : 1.0;
}

static void frame_colors(const L3DFrame *frame, Uint32 colors[256])
{
	frame_colors_of(frame, rgb_palette, colors);
}

/*
 * During a palette fade (palette_fading) the map's tiles, terrain and clouds keep the colours of
 * the palette at full brightness and are dimmed by tile_fade instead: colouring them anew at every
 * step of the fade takes long with HD tiles. The game steps every colour by a share of its
 * distance, so the palette is (nearly) a uniform part of the full one.
 */
static float tile_fade = 1.0f;  // (declared above, for set_glints)
/*
 * And under the game's brightness filter (the Flare special's flicker, stepping every tick; a level coming up from
 * dark) the tiles, terrain and plants keep the frame's colours without it and are dimmed by tile_filter_dim instead
 * (not brightened): coloured anew at every step, they showed at their own size all through it (the user: the
 * Flare shows the old textures).
 */
static float tile_filter_dim = 1.0f;

static bool uniform_fade(float *fade)
{
	if (!palette_fading)
		return false;
	double now = 0, full = 0;
	for (int i = 0; i < 256; ++i)
	{
		const Uint8 *a = (const Uint8 *)&rgb_palette[i], *b = (const Uint8 *)&palette_fade_full[i];
		now += a[0] + a[1] + a[2];
		full += b[0] + b[1] + b[2];
	}
	if (full <= 0)
		return false;
	const float f = (float)(now / full);
	if (f > 1.02f)
		return false;
	for (int i = 0; i < 256; ++i)
	{
		const Uint8 *a = (const Uint8 *)&rgb_palette[i], *b = (const Uint8 *)&palette_fade_full[i];
		for (int k = 0; k < 3; ++k)
			if (fabsf(a[k] - f * b[k]) > 12.0f)
				return false;  // (a fade between two palettes)
	}
	*fade = SDL_min(f, 1.0f);
	return true;
}

// The clouds by the game's darkening filter too (their colours are the full palette's).
static void dim_by_filter(BTBHGPUSceneGeometryBatch *b)
{
	if (filter_dim >= 1.0f)
		return;
	const Uint8 k = (Uint8)lroundf(255.0f * SDL_clamp(filter_dim, 0.0f, 1.0f));
	b->albedo_red = (Uint8)(b->albedo_red * k / 255);
	b->albedo_green = (Uint8)(b->albedo_green * k / 255);
	b->albedo_blue = (Uint8)(b->albedo_blue * k / 255);
}

static void dim_by_fade(BTBHGPUSceneGeometryBatch *b)
{
	if (tile_fade >= 1.0f)
		return;
	// (the factor applies to linear colour; the palette's are sRGB)
	const Uint8 k = (Uint8)lroundf(255.0f * powf(SDL_max(tile_fade, 0.0f), 2.2f));
	b->albedo_red = (Uint8)(b->albedo_red * k / 255);
	b->albedo_green = (Uint8)(b->albedo_green * k / 255);
	b->albedo_blue = (Uint8)(b->albedo_blue * k / 255);
}

// The map's tiles, terrain and plants: by the palette's fade and the brightness filter (tile_filter_dim).
static void dim_tiles(BTBHGPUSceneGeometryBatch *b)
{
	dim_by_fade(b);
	if (tile_filter_dim >= 1.0f)
		return;
	const Uint8 k = (Uint8)lroundf(255.0f * SDL_max(tile_filter_dim, 0.0f));
	b->albedo_red = (Uint8)(b->albedo_red * k / 255);
	b->albedo_green = (Uint8)(b->albedo_green * k / 255);
	b->albedo_blue = (Uint8)(b->albedo_blue * k / 255);
}

// A background drawn as its tiles while they have HD versions (b3d_hd_scale): the tiles show it all,
// in the playfield too, rather than the game's picture of it at its own size covering them there.
// Not one the game's filters changed after it was drawn: the waver of lava, water and ice
// (effect_count) and the screen's darkening (modified) are only in its picture. (The game's plain
// blur, blur_filter, doesn't count: the tiles show those backgrounds sharp, as the terrain does
// the ground.)
static bool hd_tile_background(const L3DFrame *frame, const L3DBackground *background, bool composed)
{
	return b3d_hd_scale() > 1 && !composed && background->effect_count == 0 &&
	       !frame->layers[background->layer].modified;
}

// Converts the layers to colour, one atlas slot each. Layers drawn over background map tiles
// (native) keep only the playfield, where the game drew them; the tiles show everything else (and
// all of it for backgrounds whose HD tiles show, hd_tile_background).
static bool cloud_background(const L3DBackground *background, bool composed);
static bool water_overlay(const L3DBackground *background);
static bool relief_frame(const L3DFrame *frame, const bool *composed);
static bool terrain_background(const L3DFrame *frame, const L3DBackground *background);
static float solid_top(int set);
static const B3DTerrain *frame_terrains[B3D_SETS + 1];
static const L3DBackground *lift_ground = NULL;  // this frame's ground when it is terrain (present_3d)
static const B3DTerrain *lift_terrain = NULL;    // and its terrain
static float stand_lift(float x, float y, float base, const float footprint[4]);
static float object_lifts[L3D_MAX_OBJECTS];  // how high the frame's objects stand on the ground (compute_object_lifts)
static float object_bases[L3D_MAX_OBJECTS];  // and the heights their layers put them at (layer_base)
// How the frame's objects lean with the ground under them (compute_object_lifts, lean_matrix): the slope
// of the ground as drawn under them (world rise per world unit across x and z; 0, 0: upright), the point
// they lean about (game position as drawn, and its height before alignment), and how much higher than
// its object's plane through that point a piece stands (world; lean_group).
typedef struct
{
	float sx, sz;
	float x, y, height;
	float offset;
} ObjectLean;
static ObjectLean object_leans[L3D_MAX_OBJECTS];
static float object_shown[L3D_MAX_OBJECTS];  // how much of each is shown: 0 hidden in a solid (hide_in_solids), 1 all

// A piece standing `offset` higher than its object's plane at the translation height `height` is that
// piece placed on the plane and moved along the camera's rays (scaled about the camera by this), so its
// object's lean turns it with the others before: they still meet on screen (lean_matrix keeps rays only
// about its pivot).
static float lean_offset_scale(float height, float offset)
{
	return align.on ? (align.cy - height) / SDL_max(align.cy - (height - offset), 1.0f) : 1.0f;
}

// How much its lean raises what leans at the world point p (its base there, over its pivot's height), for
// an object at the translation height `height`.
static float lean_rise(const ObjectLean *lean, float height, const float p[3])
{
	const float k = align_scale(lean->height), m = lean_offset_scale(height, lean->offset);
	const float x = align.cx + (p[0] - align.cx) / m, z = align.cz + (p[2] - align.cz) / m;
	return m * (lean->sx * (x - (align.cx + (lean->x - align.cx) * k)) + lean->sz * (z - (align.cz + (lean->y - align.cz) * k)));
}

// An object's instance as placed at game coordinates on its plane (aligned), leaning as the frame's ground
// has it.
static Mat4 object_world(int o, const Mat4 *transform)
{
	Mat4 world = aligned(transform);
	const ObjectLean *lean = &object_leans[o];
	if (lean->sx != 0 || lean->sz != 0)
	{
		Mat4 turn = lean_matrix(lean->sx, lean->sz, lean->x, lean->y, lean->height);
		const float m = lean_offset_scale(transform->m[13], lean->offset);
		if (m != 1.0f)
		{
			// (turned as placed on its object's plane: scaled back to it about the camera, turned, scaled up)
			Mat4 down = mat4_identity(), up = mat4_identity();
			down.m[0] = down.m[5] = down.m[10] = 1 / m;
			up.m[0] = up.m[5] = up.m[10] = m;
			for (int a = 0; a < 3; ++a)
			{
				const float c = a == 0 ? align.cx : a == 1 ? align.cy : align.cz;
				down.m[12 + a] = c * (1 - 1 / m);
				up.m[12 + a] = c * (1 - m);
			}
			const Mat4 chain[] = { up, turn, down };
			turn = mat4_chain((int)COUNTOF(chain), chain);
		}
		world = mat4_mul(&turn, &world);
	}
	return world;
}

// The ground is terrain over the game's stars with no holes for them to show through (its map has
// no black space: MINERS): they don't show at all.
static bool stars_covered(void)
{
	return frame_terrains[1] != NULL && frame_terrains[1]->holes && frame_terrains[1]->hole_count == 0;
}

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
	const bool space = frame->space && settings3d.effects && frame->filter_hue == -99 &&
	                   frame->filter_brightness == -99;

	int slots = 0;
	for (int l = 0; l < frame->layer_count; ++l)
	{
		const L3DLayer *layer = &frame->layers[l];
		if (layer->type == L3D_OVERLAY || layer->type == L3D_HUD)
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
					      !cloud_background(&frame->backgrounds[i], composed[i])) ||
					     hd_tile_background(frame, &frame->backgrounds[i], composed[i])))
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
			const int field_x0 = l3d_field_x(), field_x1 = l3d_field_x() + l3d_field_w();
			for (int y = L3D_OVERSCAN; y < L3D_OVERSCAN + L3D_PLAYFIELD_H; ++y)
				for (int x = field_x0; x < field_x1; ++x)
				{
					const int i = y * L3D_WIDTH + x;
					if (!layer->cover[i] || (empty_zero && layer->index[i] == 0) || (clouds && cloud_mask[i]))
						continue;
					if (feather > 0)
					{
						const int edge = SDL_min(SDL_min(x - field_x0, field_x1 - 1 - x), y - L3D_OVERSCAN);
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

// The modern HUD: a few gauges over the scene instead of the panel (two players: a panel each).
static bool modern_hud(void)
{
	return settings3d.hud_modern;
}

bool rgpu_modern_hud(void)
{
	return modern_hud();
}

static Layout3D layout_3d(float window_w, float window_h, const SDL_Rect *dst)
{
	Layout3D layout = { .split = true };
	if (modern_hud())
	{
		// The playfield as large as the window holds it, centred; no panel.
		const float scale = SDL_min(window_h / L3D_PLAYFIELD_H, window_w / l3d_field_w());
		layout.playfield[2] = l3d_field_w() * scale;
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
	const float scale = SDL_min(window_h / L3D_PLAYFIELD_H, room / l3d_field_w());
	layout.playfield[2] = l3d_field_w() * scale;
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
	// The screen's playfield part (the overlay: game x 24-287) where those columns are in the
	// playfield shown (wider on the wide playfield).
	const float k = f[2] / l3d_field_w();
	const float ox = f[0] + (L3D_PLAYFIELD_X - l3d_field_x()) * k, ow = L3D_PLAYFIELD_W * k;
	if (p[2] <= 0)
	{
		quads[0] = (CanvasQuad){ ox, f[1], ow, f[3], 0, 0, L3D_PLAYFIELD_W, L3D_PLAYFIELD_H };
		return 1;
	}
	quads[0] = (CanvasQuad){ p[0], p[1], p[2], p[3], PANEL_X, 0, SCREEN_W - PANEL_X, SCREEN_H, .panel = true };
	quads[1] = (CanvasQuad){ ox, f[1], ow, f[3], 0, 0, L3D_PLAYFIELD_W, L3D_PLAYFIELD_H };
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
	const Uint8 *pixels = screen_without_texts(screen);
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
			const Uint8 now = pixels[y * SCREEN_W + x];
			const int k = SDL_min(level[y * L3D_PLAYFIELD_W + x], 7);
			Uint8 expected = menu.backdrop[y * SCREEN_W + x];
			for (int i = 0; i < k; ++i)
				expected = ((expected & 0x0f) >> 1) | (expected & 0xf0);
			Uint32 *out = &screen_rgba[y * SCREEN_W + x];
			if (now == expected)
			{
				if (k > 0)
					*out = shade[k];
			}
			else if ((now & 0xf0) == (expected & 0xf0) && (now & 0x0f) < (expected & 0x0f))
			{
				// Darkened in its own hue (text shadows): darkens the scene as much.
				const Uint8 rgba[4] = { 0, 0, 0, (Uint8)(255 * (1 - ((now & 0x0f) + 1.0f) / ((expected & 0x0f) + 1.0f))) };
				memcpy(out, rgba, sizeof(rgba));
			}
			else
				*out = rgb_palette[now];
		}
	screen_text_quads(menu.map[0], menu.map[1], menu.map[2], menu.map[3], L3D_PLAYFIELD_W, L3D_PLAYFIELD_H);
}

static void build_hud(const SDL_Surface *hud, const L3DFrame *frame, bool split)
{
	convert_screen(hud, screen_rgba);
	for (int y = 0; y < L3D_PLAYFIELD_H; ++y)
		memset(screen_rgba + y * SCREEN_W, 0, L3D_PLAYFIELD_W * sizeof(Uint32));
	// The game's texts on the playfield are drawn in Oxanium (playfield_text_quads): their pixels
	// stay out of the overlay.
	static Uint8 text_pixels[L3D_PLAYFIELD_W * L3D_PLAYFIELD_H];
	memset(text_pixels, 0, sizeof(text_pixels));
	frame_text_count = fonts_enabled() ? text_records_frame(frame_texts, (int)COUNTOF(frame_texts)) : 0;
	for (int i = 0; i < frame_text_count; ++i)
	{
		const TextRecord *r = frame_texts[i];
		for (int y = 0; y < r->h; ++y)
			for (int x = 0; x < r->w; ++x)
			{
				const int px = r->x + x - L3D_PLAYFIELD_X, py = r->y + y;
				if (px >= 0 && px < L3D_PLAYFIELD_W && py >= 0 && py < L3D_PLAYFIELD_H &&
				    r->after[y * r->w + x] != r->before[y * r->w + x])
					text_pixels[py * L3D_PLAYFIELD_W + px] = 1;
			}
	}
	if (split && !fonts_enabled())
		add_message();

	for (int l = 0; l < frame->layer_count; ++l)
	{
		const L3DLayer *layer = &frame->layers[l];
		// (The game's own displays only without the modern HUD, which shows them its way.)
		if (layer->type != L3D_OVERLAY && (layer->type != L3D_HUD || modern_hud()))
			continue;
		for (int y = 0; y < L3D_PLAYFIELD_H; ++y)
		{
			const int row = y + L3D_OVERSCAN;
			if (row < layer->min_y || row >= layer->max_y)
				continue;
			for (int x = 0; x < L3D_PLAYFIELD_W; ++x)
			{
				const int i = row * L3D_WIDTH + x + L3D_PLAYFIELD_X;
				if (layer->cover[i] && !text_pixels[y * L3D_PLAYFIELD_W + x])
					screen_rgba[y * SCREEN_W + x] = rgb_palette[layer->index[i]];
			}
		}
	}
	if (menu.on && !menu.modern)
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
 * With an upscaled picture of the panel (data/hd/hud_1p.png or hud_2p.png, see
 * TYRIAN3D.md "HD resources"), the panel's unchanging parts come from it: the magnified panel keeps only
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
static void hud_quad(float x, float y, float w, float h, const float left[4], const float right[4])
{
	HudQuad *q = hud_quad_add();
	if (q == NULL)
		return;
	*q = (HudQuad){ x, y, w, h, 0, 0, 1, 1 };
	memcpy(q->left, left, sizeof(q->left));
	memcpy(q->right, right != NULL ? right : left, sizeof(q->right));
}

/*
 * Text in Oxanium (assets/fonts, OFL), for the HUD and the game's own texts over the 3D view: the
 * game's three fonts as three weights (large: bold, normal: semibold, tiny: medium), drawn from the
 * fork's glyph atlases at any size. Sizes by cap height (the height of a capital letter).
 *
 * Texts are laid out with each font's metrics at one size (text_sizes), and their glyphs drawn from
 * rasters of the font at sizes a sixth of an octave apart (text_raster), each made the first time a
 * text needs it: the smallest at or above the size the text shows at in the window's pixels, so
 * glyphs are shrunk by less than a step, at whole pixels of the window (a single raster for all
 * sizes, without mipmaps, shrank small text 4-5 times, roughly, and magnified big text, softly).
 */
enum { TEXT_LARGE, TEXT_NORMAL, TEXT_TINY, TEXT_FONTS };
#define TEXT_GLYPHS 95  // ASCII 32-126
#define TEXT_RASTER_OCTAVE 6    // raster sizes a sixth of an octave apart (12 %) ...
#define TEXT_RASTER_FIRST -18  // ... from 1/8 of the layout size ...
#define TEXT_RASTER_LAST 8     // ... to 2.5 times
#define TEXT_RASTERS (TEXT_RASTER_LAST - TEXT_RASTER_FIRST + 1)

static const char *const text_files[TEXT_FONTS] = { "Oxanium-Bold.ttf", "Oxanium-SemiBold.ttf", "Oxanium-Medium.ttf" };
static const uint32_t text_sizes[TEXT_FONTS] = { 72, 60, 52 };  // the layout's (pixel heights)
static BTBHGPUFontGlyph text_glyphs[TEXT_FONTS][TEXT_GLYPHS];   // the layout's metrics
static float text_cap[TEXT_FONTS];  // cap height in the layout's pixels
static bool text_loaded = false, text_ok = false;

typedef struct
{
	bool tried;
	BTBHGPUFont *font;
	float scale;  // its pixels per layout pixel
	Uint32 used;  // text_frames when text was last drawn from it
	BTBHGPUFontGlyph glyphs[TEXT_GLYPHS];
} TextRaster;
static TextRaster text_rasters[TEXT_FONTS][TEXT_RASTERS];
#define TEXT_RASTER_IDLE 600  // frames a raster isn't drawn from before it may go

// Rasters no text has been drawn from for a while (sizes the window no longer shows: it was resized)
// go when another is made, so they don't pile up. (Not the layout's: the fallback.)
static void forget_idle_text_rasters(void)
{
	for (int f = 0; f < TEXT_FONTS; ++f)
		for (int i = 0; i < TEXT_RASTERS; ++i)
		{
			TextRaster *r = &text_rasters[f][i];
			if (r->font != NULL && i != -TEXT_RASTER_FIRST && text_frames - r->used > TEXT_RASTER_IDLE)
			{
				btbh_gpu_font_destroy(r->font);
				r->font = NULL;
				r->tried = false;
			}
		}
}

// A font's raster `step` steps from its layout size (loaded the first time; NULL if it can't be).
static TextRaster *text_raster(int font, int step)
{
	TextRaster *r = &text_rasters[font][step - TEXT_RASTER_FIRST];
	if (r->tried)
		return r->font != NULL ? r : NULL;
	forget_idle_text_rasters();
	r->tried = true;
	const uint32_t size = (uint32_t)SDL_max(lroundf(text_sizes[font] * exp2f(step / (float)TEXT_RASTER_OCTAVE)), 4L);
	uint32_t codepoints[TEXT_GLYPHS];
	for (int i = 0; i < TEXT_GLYPHS; ++i)
		codepoints[i] = 32u + (uint32_t)i;
	char dir[1024], path[1200];
	tyr3d_resource_dir("TYR3D_FONT_DIR", TYR3D_FONT_DIR, "fonts", dir, sizeof(dir));
	snprintf(path, sizeof(path), "%s/%s", dir, text_files[font]);
	BTBHGPUFontReport report;
	r->font = btbh_gpu_window_font_load(window, path, size, codepoints, TEXT_GLYPHS, &report);
	if (r->font == NULL)
	{
		fprintf(stderr, "warning: font %s at %u px: %s\n", path, size, report.message);
		return NULL;
	}
	for (int i = 0; i < TEXT_GLYPHS; ++i)
		btbh_gpu_font_glyph(r->font, codepoints[i], &r->glyphs[i]);
	r->scale = (float)size / text_sizes[font];
	printf("text: %s at %u px (atlas %u x %u)\n", text_files[font], size, report.atlas_width, report.atlas_height);
	return r;
}

static bool load_text_fonts(void)
{
	if (text_loaded)
		return text_ok;
	text_loaded = true;
	for (int f = 0; f < TEXT_FONTS; ++f)
	{
		const TextRaster *layout = text_raster(f, 0);
		if (layout == NULL)
			return false;
		memcpy(text_glyphs[f], layout->glyphs, sizeof(text_glyphs[f]));
		const BTBHGPUFontGlyph *h = &text_glyphs[f]['H' - 32];
		text_cap[f] = h->height > 0 ? h->height : text_sizes[f] * 0.7f;
	}
	text_ok = true;
	return true;
}

static const BTBHGPUFontGlyph *text_glyph(int font, char c)
{
	const int i = (unsigned char)c - 32;
	return i >= 0 && i < TEXT_GLYPHS ? &text_glyphs[font][i] : NULL;
}

// A position in points at the nearest of the window's pixels.
static float snap_to_pixel(float points)
{
	return roundf(points * text_density) / text_density;
}

// The raster to draw a font's glyphs from when a layout pixel is `scale` points.
static const TextRaster *text_raster_for(int font, float scale)
{
	const float pixels = scale * text_density;  // window pixels per layout pixel
	int step = pixels > 0 ? (int)ceilf(TEXT_RASTER_OCTAVE * log2f(pixels) - 0.08f) : 0;  // (1 % over one: that one)
	step = SDL_clamp(step, TEXT_RASTER_FIRST, TEXT_RASTER_LAST);
	TextRaster *r = text_raster(font, step);
	if (r == NULL)
		r = text_raster(font, 0);
	r->used = text_frames;
	return r;
}

// A string's width at a cap height ('~' toggles the game's highlight and takes no room).
static float text_width(int font, const char *s, float cap)
{
	if (!load_text_fonts())
		return 0;
	float width = 0;
	for (; *s != '\0'; ++s)
	{
		const BTBHGPUFontGlyph *g = *s == '~' ? NULL : text_glyph(font, *s);
		if (g != NULL)
			width += g->advance;
	}
	return width * cap / text_cap[font];
}

// A string with its top (of capitals) at y; a shadow beneath it if shadow > 0 (its offset).
// Text shaded from top (the capitals' tops) to bottom (the baseline and below), as the game's fonts
// are drawn.
static void text_quads_graded(int font, const char *s, float x, float y, float cap, const float top[4],
                              const float bottom[4], float shadow)
{
	if (!load_text_fonts())
		return;
	const float scale = cap / text_cap[font];
	// Laid out in the layout's metrics, drawn from the raster for the size it shows at.
	const TextRaster *raster = text_raster_for(font, scale);
	BTBHGPUTexture *atlas = btbh_gpu_font_atlas(raster->font);
	const float points = scale / raster->scale;  // per raster pixel
	for (int pass = shadow > 0 ? 0 : 1; pass < 2; ++pass)
	{
		const float shade[4] = { 0, 0, 0, 0.7f * top[3] };
		const float d = pass == 0 ? shadow : 0;
		float pen = x;
		const float baseline = y + cap;
		for (const char *p = s; *p != '\0'; ++p)
		{
			const BTBHGPUFontGlyph *g = *p == '~' ? NULL : text_glyph(font, *p);
			if (g == NULL)
				continue;
			const BTBHGPUFontGlyph *drawn = &raster->glyphs[g - text_glyphs[font]];
			if (*p != ' ' && drawn->width > 0 && drawn->height > 0)  // (a space's glyph is blank)
			{
				HudQuad *q = hud_quad_add();
				if (q == NULL)
					return;
				// (At whole pixels, so the raster's pixels fall on the window's rather than across two.)
				*q = (HudQuad){ snap_to_pixel(pen + drawn->offset_x * points + d),
				                snap_to_pixel(baseline + drawn->offset_y * points + d), drawn->width * points,
				                drawn->height * points, drawn->u0, drawn->v0, drawn->u1, drawn->v1, .texture = atlas,
				                .graded = true };
				const float t0 = SDL_clamp((q->y - d - y) / cap, 0.0f, 1.0f);
				const float t1 = SDL_clamp((q->y - d + q->h - y) / cap, 0.0f, 1.0f);
				for (int k = 0; k < 4; ++k)
				{
					q->left[k] = pass == 0 ? shade[k] : top[k] + (bottom[k] - top[k]) * t0;
					q->below[k] = pass == 0 ? shade[k] : top[k] + (bottom[k] - top[k]) * t1;
				}
				memcpy(q->right, q->left, sizeof(q->right));
			}
			pen += g->advance * scale;
		}
	}
}

static void text_quads(int font, const char *s, float x, float y, float cap, const float color[4], float shadow)
{
	text_quads_graded(font, s, x, y, cap, color, color, shadow);
}

bool rgpu_ui_text_ready(void)
{
	return load_text_fonts();
}

float rgpu_ui_text_width(int font, const char *s, float cap)
{
	return text_width(SDL_clamp(font, 0, TEXT_FONTS - 1), s, cap);
}

void rgpu_ui_text(int font, const char *s, float x, float y, float cap, const float top[4], const float bottom[4], float shadow)
{
	text_quads_graded(SDL_clamp(font, 0, TEXT_FONTS - 1), s, x, y, cap, top, bottom, shadow);
}

/*
 * The game's own texts over the 3D view (menus, messages, the store) in Oxanium: those a screen still
 * shows (text_record.h) are taken back off a copy of it (their pixels as before each was drawn,
 * newest first), and drawn again as text. TYR3D_FONTS=0: the game's pixel fonts.
 */
#define SCREEN_TEXTS 256

static Uint8 untexted[SCREEN_W * SCREEN_H];
static const TextRecord *screen_texts[SCREEN_TEXTS];
static int screen_text_count = 0;

static bool fonts_enabled(void)
{
	static int on = -1;
	if (on < 0)
		on = SDL_getenv("TYR3D_FONTS") == NULL || SDL_atoi(SDL_getenv("TYR3D_FONTS")) != 0;
	return on && l3d_enabled && load_text_fonts();
}

static const Uint8 *screen_without_texts(const SDL_Surface *screen)
{
	if (fonts_enabled())
		screen_text_count = text_records_on(screen, screen_texts, SCREEN_TEXTS, untexted);
	else
	{
		screen_text_count = 0;
		for (int y = 0; y < SCREEN_H; ++y)
			memcpy(untexted + y * SCREEN_W, (const Uint8 *)screen->pixels + y * screen->pitch, SCREEN_W);
	}
	return untexted;
}

// The kept texts as text, a screen pixel (x, y) at window (ox + x * kx, oy + y * ky); only those
// within the first clip_w x clip_h of the screen.
static void text_record_quads(const TextRecord *const *texts, int count, int x_offset, float ox, float oy, float kx, float ky,
                              int clip_w, int clip_h)
{
	static const int fonts[3] = { TEXT_LARGE, TEXT_NORMAL, TEXT_TINY };
	for (int i = 0; i < count; ++i)
	{
		const TextRecord *r = texts[i];
		const int text_x = r->text_x - x_offset;
		if (r->shadow_only || text_x < 0 || r->text_y < 0 || text_x + r->text_w > clip_w + 2 ||
		    r->text_y + r->text_h > clip_h + 2 || r->text_h <= 0)
			continue;
		// Its colours, as the game shades its glyphs: of the pixels it drew (not the shadow's), the
		// colour most of them have (the glyphs' body), the brightest (their top edge) and the darkest
		// (their lower edges). Drawn from the body lit by the highlight at the top to the body
		// darkened at the bottom.
		int count[256] = { 0 };
		float brightest = 0;
		for (int k = 0; k < r->w * r->h; ++k)
			if (r->after[k] != r->before[k])
			{
				++count[r->after[k]];
				const Uint8 *c = (const Uint8 *)&rgb_palette[r->after[k]];
				brightest = SDL_max(brightest, 0.299f * c[0] + 0.587f * c[1] + 0.114f * c[2]);
			}
		int total = 0, body = -1, light = -1, dark = -1;
		float light_lum = -1, dark_lum = 1e9f;
		for (int index = 0; index < 256; ++index)
		{
			const Uint8 *c = (const Uint8 *)&rgb_palette[index];
			const float lum = 0.299f * c[0] + 0.587f * c[1] + 0.114f * c[2];
			if (count[index] == 0 || lum < brightest * 0.35f)
				continue;  // (the shadow)
			total += count[index];
			if (body < 0 || count[index] > count[body])
				body = index;
		}
		if (body < 0)
			continue;
		for (int index = 0; index < 256; ++index)
		{
			const Uint8 *c = (const Uint8 *)&rgb_palette[index];
			const float lum = 0.299f * c[0] + 0.587f * c[1] + 0.114f * c[2];
			if (count[index] * 25 < total || lum < brightest * 0.35f)
				continue;  // (a few stray pixels)
			if (lum > light_lum)
				light_lum = lum, light = index;
			if (lum < dark_lum)
				dark_lum = lum, dark = index;
		}
		const Uint8 *cb = (const Uint8 *)&rgb_palette[body], *cl = (const Uint8 *)&rgb_palette[light],
		            *cd = (const Uint8 *)&rgb_palette[dark];
		float top[4] = { 0, 0, 0, 1 }, bottom[4] = { 0, 0, 0, 1 };
		for (int j = 0; j < 3; ++j)
		{
			top[j] = (cb[j] + 0.6f * (cl[j] - cb[j])) / 255.0f;
			bottom[j] = (cb[j] + 0.35f * (cd[j] - cb[j])) / 255.0f;
		}
		char text[sizeof(r->text)];
		int t = 0;
		for (const char *c = r->text; *c != '\0' && t < (int)sizeof(text) - 1; ++c)
			if (*c != '~')
				text[t++] = *c;
		text[t] = '\0';
		const int font = fonts[SDL_clamp(r->font, 0, 2)];
		// One size per font (the game's glyphs' height), smaller where it would run past the
		// game's text (menus place things after it).
		static const float caps[3] = { 10.5f, 7.6f, 5.2f };  // screen pixels
		float cap = SDL_min(caps[SDL_clamp(r->font, 0, 2)], r->text_h * 0.95f) * ky;
		const float width = text_width(font, text, cap);
		if (width > r->text_w * kx * 1.08f)
			cap *= r->text_w * kx * 1.08f / width;
		// The game's capitals' tops and ours alike (descenders make some texts taller).
		const float game_cap = caps[SDL_clamp(r->font, 0, 2)] * ky;
		const float ours = text_width(font, text, cap);
		const float x = r->align == 1 ? ox + (text_x + r->text_w * 0.5f) * kx - ours * 0.5f
		              : r->align == 2 ? ox + (text_x + r->text_w) * kx - ours : ox + text_x * kx;
		text_quads_graded(font, text, x, oy + r->text_y * ky + (game_cap - cap) * 0.5f, cap, top, bottom, cap * 0.09f);
	}
}

static void screen_text_quads(float ox, float oy, float kx, float ky, int clip_w, int clip_h)
{
	text_record_quads(screen_texts, screen_text_count, 0, ox, oy, kx, ky, clip_w, clip_h);
}

static void fade_under_ship(int first, float x0, float y0, float x1, float y1, float ship_x, float ship_y, float reach,
                            float *shown);

// The texts the game drew on the playfield in the frame shown (the overlay: score, lives...), and
// its message, in Oxanium where the playfield is in the window.
static void playfield_text_quads(const Layout3D *layout)
{
	if (!fonts_enabled())
		return;
	const float kx = layout->playfield[2] / l3d_field_w(), ky = layout->playfield[3] / L3D_PLAYFIELD_H;
	// The ship flies under them (the cash at the bottom left): each fades when it is near.
	float ship_x = -1e9f, ship_y = -1e9f;
	if (!menu.on)
		rgpu_playfield_to_window(player[0].x + 7.0f, player[0].y + 7.0f, &ship_x, &ship_y);
	static struct { int x, y; float shown; } fades[8];  // by where the text is
	static int next_fade = 0;
	for (int i = 0; i < frame_text_count; ++i)
	{
		const TextRecord *r = frame_texts[i];
		if (r->hud && modern_hud())
			continue;  // (the modern HUD shows the game's displays its own way)
		const int first = hud_quad_count;
		text_record_quads(&frame_texts[i], 1, l3d_field_x(), layout->playfield[0], layout->playfield[1], kx, ky,
		                  l3d_field_w(), L3D_PLAYFIELD_H);
		if (first == hud_quad_count)
			continue;
		int f = 0;
		while (f < (int)COUNTOF(fades) && (fades[f].x != r->text_x || fades[f].y != r->text_y || fades[f].shown <= 0))
			++f;
		if (f == (int)COUNTOF(fades))
		{
			f = next_fade;
			next_fade = (next_fade + 1) % (int)COUNTOF(fades);
			fades[f].x = r->text_x;
			fades[f].y = r->text_y;
			fades[f].shown = 1;
		}
		// (the text's box grown by half the ship's sprite, 24 x 28, so any part of the ship counts)
		const float x0 = layout->playfield[0] + (r->text_x - l3d_field_x()) * kx, y0 = layout->playfield[1] + r->text_y * ky;
		fade_under_ship(first, x0 - 12 * kx, y0 - 14 * ky, x0 + (r->text_w + 12) * kx, y0 + (r->text_h + 14) * ky, ship_x,
		                ship_y, 8 * ky, &fades[f].shown);
	}
	if (layout->split && textErase > 0 && text_window_message[0] != '\0' && !menu.on && !modern_hud())
	{
		const float color[4] = { 0.86f, 0.86f, 0.9f, 1.0f };
		const float cap = 5.4f * ky;
		text_quads(TEXT_TINY, text_window_message, layout->playfield[0] + 20 * kx,
		           layout->playfield[1] + (MESSAGE_AT + 1) * ky, cap, color, cap * 0.09f);
	}
}

// Quads from first on fade when the ship is under them (within reach of their box), eased in *shown.
static void fade_under_ship(int first, float x0, float y0, float x1, float y1, float ship_x, float ship_y, float reach,
                            float *shown)
{
	const float dx = SDL_max(SDL_max(x0 - ship_x, ship_x - x1), 0.0f);
	const float dy = SDL_max(SDL_max(y0 - ship_y, ship_y - y1), 0.0f);
	const float distance = sqrtf(dx * dx + dy * dy);
	const float target = distance < reach ? 0.3f + 0.7f * distance / reach : 1.0f;
	*shown += (target - *shown) * 0.2f;
	for (int i = first; i < hud_quad_count; ++i)
	{
		hud_quads[i].left[3] *= *shown;
		hud_quads[i].right[3] *= *shown;
		hud_quads[i].below[3] *= *shown;
	}
}

/*
 * Twin-stick's aim lines (mainint.h twin_stick_aim_lines): while the pointer aims the turret, a line
 * across the playfield and one down it through the pointer, brass on a dark edge, fading towards the
 * playfield's edges, apart round the crosshair; under the HUD.
 */
static void aim_line_quads(const Layout3D *layout)
{
	float px, py;
	mouse_pointer_window(&px, &py);  // (where it is, the keys pressed since too)
	const float x0 = layout->playfield[0], y0 = layout->playfield[1];
	const float x1 = x0 + layout->playfield[2], y1 = y0 + layout->playfield[3];
	if (menu.on || !twin_stick_aim_lines() || px < x0 || px > x1 || py < y0 || py > y1)
		return;
	const float pixel = 1.0f / text_density, gap = ui_pointer_points() * 0.6f + 6 * pixel;
	for (int pass = 0; pass < 2; ++pass)
	{
		// The dark edge, then the brass line over it.
		const float t = (pass == 0 ? 5.0f : 2.5f) * pixel;
		const float near[4] = { pass == 0 ? 0.0f : 0.98f, pass == 0 ? 0.0f : 0.82f, pass == 0 ? 0.0f : 0.46f, pass == 0 ? 0.4f : 0.75f };
		const float far[4] = { near[0], near[1], near[2], near[3] * 0.3f };
		if (px - gap > x0)
			hud_quad(x0, py - t / 2, px - gap - x0, t, far, near);
		if (px + gap < x1)
			hud_quad(px + gap, py - t / 2, x1 - px - gap, t, near, far);
		for (int k = 0; k < 2; ++k)
		{
			const float top = k == 0 ? y0 : py + gap, bottom = k == 0 ? py - gap : y1;
			HudQuad *q = bottom > top ? hud_quad_add() : NULL;
			if (q == NULL)
				continue;
			*q = (HudQuad){ px - t / 2, top, t, bottom - top, 0, 0, 1, 1 };
			memcpy(q->left, k == 0 ? far : near, sizeof(q->left));
			memcpy(q->right, k == 0 ? far : near, sizeof(q->right));
			q->graded = true;
			memcpy(q->below, k == 0 ? near : far, sizeof(q->below));
		}
	}
}

/*
 * The modern HUD (settings3d.hud_modern): instead of the panel beside the playfield, gauges and the
 * game's displays over the scene from the game's state, in the 16:9 area round the playfield (ui.c
 * ui_build_hud). Under a menu the game shows over the level, it is drawn under the menu's boxes.
 */
static void build_modern_hud(float window_w, float window_h, const Layout3D *layout)
{
	hud_quad_count = 0;
	aim_line_quads(layout);  // (Tyrian3D twin-stick, with either HUD)
	if (!modern_hud())
		return;
	const UIView view = { .w = window_w, .h = window_h, .pixel = 1.0f / text_density,
	                      .playfield = { layout->playfield[0], layout->playfield[1], layout->playfield[2], layout->playfield[3] },
	                      .menu_over = menu.on };
	ui_build_hud(&view);
	if (menu.on)
		hud_under = hud_quad_count;
}

// The debug flight's line at the top: the level, its time, the speed; the keys under it.
static void debug_status_quads(float window_w, float window_h)
{
	const char *status = debug_flight_status();
	if (status[0] == '\0')
		return;
	const float u = window_h / 200.0f, cap = 3.6f * u;
	const char *keys = debug_flight_keys(), *loadout = debug_flight_loadout();
	const float width = SDL_max(text_width(TEXT_TINY, status, cap),
	                            SDL_max(text_width(TEXT_TINY, keys, cap * 0.8f), text_width(TEXT_TINY, loadout, cap * 0.8f)));
	const float backing[4] = { 0, 0, 0, 0.45f };
	hud_quad((window_w - width) / 2 - 3 * u, 1.5f * u, width + 6 * u, 18 * u, backing, NULL);
	const float color[4] = { 1.0f, 0.86f, 0.45f, 1 }, dim[4] = { 0.8f, 0.82f, 0.88f, 0.85f };
	text_quads(TEXT_TINY, status, (window_w - text_width(TEXT_TINY, status, cap)) / 2, 3 * u, cap, color, 0.3f * u);
	text_quads(TEXT_TINY, keys, (window_w - text_width(TEXT_TINY, keys, cap * 0.8f)) / 2, 9 * u, cap * 0.8f, dim, 0.3f * u);
	text_quads(TEXT_TINY, loadout, (window_w - text_width(TEXT_TINY, loadout, cap * 0.8f)) / 2, 14 * u, cap * 0.8f, dim,
	           0.3f * u);
}

static void present_3d(const SDL_Surface *hud, const L3DFrame *frame, const SDL_Rect *dst);

/*
 * TYR3D_PROFILE=gpu: the GPU's time for each 3D frame, from its submission to its completion, the frames
 * before it waited for first so that none overlaps it (which slows the game down a little); rgpu_present_3d
 * prints the median and the mean every 300 frames.
 */
static double gpu_frame_ms[1024];
static int gpu_frame_count = 0;

static bool gpu_profile(void)
{
	static int on = -1;
	if (on < 0)
	{
		on = SDL_getenv("TYR3D_PROFILE") != NULL && SDL_strcasecmp(SDL_getenv("TYR3D_PROFILE"), "gpu") == 0;
		if (on)
			btbh_gpu_window_set_frame_telemetry_enabled(window, 1);
	}
	return on;
}

static void gpu_profiled_present_3d(const SDL_Surface *hud, const L3DFrame *frame, const SDL_Rect *dst)
{
	if (!gpu_profile())
	{
		present_3d(hud, frame, dst);
		return;
	}
	BTBHGPUFrameTelemetrySample samples[16];
	(void)btbh_gpu_window_finish_frame_telemetry(window, samples, 16);  // (the GPU idle before this frame)
	present_3d(hud, frame, dst);
	const Uint32 n = btbh_gpu_window_finish_frame_telemetry(window, samples, 16);
	Uint32 last = 0;
	for (Uint32 i = 1; i < n; ++i)
		if (samples[i].frame_serial > samples[last].frame_serial)
			last = i;
	if (n > 0 && gpu_frame_count < (int)COUNTOF(gpu_frame_ms))
		gpu_frame_ms[gpu_frame_count++] = samples[last].fence_completion_milliseconds;
}

void rgpu_present_3d_ahead(const SDL_Surface *hud, const L3DFrame *frame, const SDL_Rect *dst, float ticks)
{
	ahead = ticks;
	gpu_profiled_present_3d(hud, frame, dst);
	ahead = 0;
}

bool rgpu_window_to_playfield(float wx, float wy, float *x, float *y)
{
	if (!shown_view.valid)
		return false;
	const Camera3D *camera = &shown_view.camera;
	const float ndc[2] = { wx / shown_view.window_w * 2 - 1, 1 - wy / shown_view.window_h * 2 };
	float slope[2], ray[3];
	ndc_slopes(camera, ndc, slope);
	if (shown_view.upside_down && !camera->sideways)
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
                          const float fade[4], const L3DFrame *frame, const SDL_Rect *dst, SDL_Rect *screen_rect, bool modern)
{
	menu.on = true;
	menu.modern = modern;
	menu.backdrop = backdrop;
	menu.shades = shades;
	menu.shade_count = shade_count;
	memcpy(canvas_fade, fade, sizeof(canvas_fade));
	ahead = 0;
	present_3d(screen, frame, dst);
	menu.on = false;
	menu.modern = false;
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
	// (Where the menu's boxes and texts are shown: the screen's playfield columns at game x 24 and on,
	// as the original's, whatever part of the wide playfield the 2D view showed; see layout_quads.)
	const float k = layout.playfield[2] / l3d_field_w();
	screen_rect->x = (int)(layout.playfield[0] + (L3D_PLAYFIELD_X - l3d_field_x()) * k);
	screen_rect->y = (int)layout.playfield[1];
	screen_rect->w = (int)(k * SCREEN_W + 0.5f);
	screen_rect->h = (int)(layout.playfield[3] * SCREEN_H / L3D_PLAYFIELD_H + 0.5f);
}

float rgpu_playfield_scale(void)
{
	int w = 0, h = 0;
	SDL_GetWindowSize(btbh_gpu_window_sdl_window(window), &w, &h);
	const SDL_Rect none = { 0, 0, 0, 0 };
	const Layout3D layout = layout_3d((float)w, (float)h, &none);
	const float scale = layout.playfield[2] / l3d_field_w();
	return scale > 0 ? scale : 1;
}

static Uint64 profile_rows_ticks = 0;  // (TYR3D_PROFILE: time making terrain rows)
static int profile_rows = 0;
static Uint64 profile_lift_ticks = 0;  // (and finding where objects stand: setup_stand, compute_object_lifts)

static int compare_doubles(const void *a, const void *b)
{
	const double x = *(const double *)a, y = *(const double *)b;
	return x < y ? -1 : x > y;
}

void rgpu_present_3d(const SDL_Surface *hud, const L3DFrame *frame, const SDL_Rect *dst)
{
	static Uint64 total_ticks = 0, most_ticks = 0;
	static int frames = 0;
	const Uint64 start = SDL_GetPerformanceCounter();

	gpu_profiled_present_3d(hud, frame, dst);

	const Uint64 spent = SDL_GetPerformanceCounter() - start;
	total_ticks += spent;
	most_ticks = SDL_max(most_ticks, spent);
	if (++frames == 300)
	{
		if (SDL_getenv("TYR3D_PROFILE") != NULL)
			printf("3d present: %.2f ms/frame, at most %.2f (%d layers); terrain rows: %d, %.2f ms/frame; lifts %.3f ms/frame\n",
			       (double)total_ticks * 1000.0 / SDL_GetPerformanceFrequency() / frames,
			       (double)most_ticks * 1000.0 / SDL_GetPerformanceFrequency(), frame->layer_count, profile_rows,
			       (double)profile_rows_ticks * 1000.0 / SDL_GetPerformanceFrequency() / frames,
			       (double)profile_lift_ticks * 1000.0 / SDL_GetPerformanceFrequency() / frames);
		if (gpu_profile() && gpu_frame_count > 0)
		{
			double sum = 0;
			for (int i = 0; i < gpu_frame_count; ++i)
				sum += gpu_frame_ms[i];
			qsort(gpu_frame_ms, (size_t)gpu_frame_count, sizeof(gpu_frame_ms[0]), compare_doubles);
			printf("3d gpu: median %.3f ms/frame, mean %.3f, at most %.3f (%d frames)\n", gpu_frame_ms[gpu_frame_count / 2],
			       sum / gpu_frame_count, gpu_frame_ms[gpu_frame_count - 1], gpu_frame_count);
		}
		gpu_frame_count = 0;
		profile_rows = 0;
		profile_rows_ticks = 0;
		profile_lift_ticks = 0;
		total_ticks = most_ticks = 0;
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

// A palette material glows as its surface is coloured: its GLB's emission colour (linear) was baked from the levels'
// palette (the in-game panel picture's, as tools/blender/tyrkit.py's level_palette), so the frame's colour of its
// index (the level's own palette, a fade, a sprite filter) carries it as far as it lies from that palette's colour.
static Uint8 palette_emission(Uint8 emission, Uint8 now, Uint8 then)
{
	return (Uint8)SDL_min(255.0f, emission * (srgb_to_linear(now) + 0.002f) / (srgb_to_linear(then) + 0.002f) + 0.5f);
}

static void palette_emission_of(BTBHGPUSceneGeometryBatch *b, const Uint8 now[3], int index)
{
	const SDL_Color then = palettes[pcxpal[3 - 1]][index];
	b->emission_red = palette_emission(b->emission_red, now[0], then.r);
	b->emission_green = palette_emission(b->emission_green, now[1], then.g);
	b->emission_blue = palette_emission(b->emission_blue, now[2], then.b);
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
		if (report.material_count > loaded->material_count)
			fprintf(stderr, "warning: model %s has %u materials, only the first %u are drawn\n", model->path,
			        report.material_count, loaded->material_count);
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
                       L3D_MAX_GLOWS + DEEP_STARS + NEBULA_PATCHES + 2 + WEATHER_FLAKES + 32 + 64 + MAX_PLANTS + MAX_CLOUD_PUFFS)
// Background tiles: per background, a batch for each of its cells mirrored or not and fading
// either way or not at all (B3D_ATLAS_CELLS covers the cells of all three backgrounds).
// Terrain: rows of the three backgrounds' maps drawn at most.
#define MAX_TERRAIN_ROW_DRAWS 192
#define MAX_BATCHES (L3D_MAX_LAYERS + M3D_MAX_MODELS * 4 + L3D_MAX_OBJECTS + B3D_ATLAS_CELLS * 12 + 1 + L3D_MAX_BACKGROUNDS + P3D_KIND_COUNT + 1 + 1 + MAX_TERRAIN_ROW_DRAWS + 20)

static float instances[MAX_INSTANCES * 24];
static BTBHGPUSceneGeometryBatch batches[MAX_BATCHES];

// TYR3D_LOG_CLIP (log_clipping): what the frame draws where, kept only while the switch is on. Each
// model object's transform as add_object_batches draws it (before aligned()), and each background
// as add_background_batches draws it: as terrain (the ground's, or a solid) or flat.
typedef struct
{
	const L3DBackground *background;
	const B3DTerrain *terrain;  // NULL: drawn flat
	float height;               // its plane's height (its tiles' and its terrain rows')
	float hole_depth;           // how far its terrain's walls go down where it has nothing
	float shift;                // how far it has scrolled on since the tick (game pixels)
	bool clouds;                // its cloud tiles are clouds (add_cloud_batches), not on its plane
} ClipSurface;

static Mat4 clip_transforms[L3D_MAX_OBJECTS];
static Mat4 clip_worlds[L3D_MAX_OBJECTS];  // (and as placed in the world: aligned, leaning)
static bool clip_drawn[L3D_MAX_OBJECTS];
static ClipSurface clip_surfaces[L3D_MAX_BACKGROUNDS];
static int clip_surface_count = 0;

static bool clip_log_on(void)
{
	static int on = -1;
	if (on < 0)
		on = SDL_getenv("TYR3D_LOG_CLIP") != NULL;
	return on != 0;
}

// Appends instances and batches for the frame's model objects, grouped by model. colors are the
// frame's palette colours, for palette materials.
// mirror turns the models left for right: in a vertically mirrored view (upside-down levels) that
// makes them look turned round rather than mirrored, so their triangles still face the camera the
// right way round for the renderer's lighting.
#define SIDE_ROLL 90.0f  // degrees about the scroll axis, seen from the side

// How opaque an object fading in is at its step (L3DObject.appear).
static float appear_alpha(Uint8 step)
{
	return (float)step / (L3D_APPEAR_STEPS + 1);
}

// How much of an object is shown, in steps (object_shown): 0 none, SHOWN_STEPS all.
#define SHOWN_STEPS 8

static int shown_step(int o)
{
	return (int)(object_shown[o] * SHOWN_STEPS + 0.5f);
}

// A model object's transform at the given height (its translation's), on its plane before aligned():
// where it is drawn, turned, scaled and centred (add_object_batches; what would sink is raised,
// after this).
static Mat4 object_transform(const L3DObject *object, const LoadedModel *loaded, bool mirror, float height)
{
	const M3DModel *model = &m3d_models[object->model];
	const float scale = (model->size > 0 && loaded->footprint > 0 ? model->size / loaded->footprint : 1.0f) *
	                    (object->scale > 0 ? object->scale : 1.0f);
	Mat4 mirror_x = mat4_identity();
	if (mirror)
		mirror_x.m[0] = -1;
	// Seen from the side (l3d_sideways), every model lies on its side, its top towards
	// the window's top: the level's craft are seen in profile.
	const Mat4 chain[] = {
		mat4_translation(object_x(object), height, object_y(object)),
		mirror_x,
		mat4_rotation(2, l3d_sideways ? SIDE_ROLL : 0.0f),
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
	return mat4_chain((int)COUNTOF(chain), chain);
}

static void add_object_batches(const L3DFrame *frame, const Uint32 colors[256], bool mirror, int *instance_count,
                               int *batch_count)
{
	sync_model_cache();
	const bool clip_log = clip_log_on();
	if (clip_log)
		memset(clip_drawn, 0, sizeof(clip_drawn));

	for (int model_index = 0; model_index < m3d_model_count; ++model_index)
	{
		// Objects of the model in each state (sprite filter, ghost, fading in) share batches.
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
				if (done[o] || object->model != model_index || object->filter != state->filter || object->ghost != state->ghost ||
				    object->appear != state->appear || shown_step(o) != shown_step(f))
					continue;
				done[o] = true;
				if (loaded == NULL || *instance_count >= MAX_INSTANCES || shown_step(o) == 0)
					continue;

				const M3DModel *model = &m3d_models[model_index];
				const float height = object_bases[o] + object->height + object_lifts[o];
				Mat4 transform = object_transform(object, loaded, mirror, height);
				if (object->standin == L3D_STANDIN_PLACEHOLDER)  // (a wreck's place, until it has a model)
					for (int k = 1; k < 12; k += 4)
						transform.m[k] *= STANDIN_SLUMP;
				// Nothing sinks into the ground: models centred on their layer's height (items on
				// the ground enemies' layer) are lifted by what their turned bounds reach below it
				// (the ground under them: as high above it as they would stand above a flat ground).
				const float reach = fabsf(transform.m[1]) * loaded->half[0] + fabsf(transform.m[5]) * loaded->half[1] +
				                    fabsf(transform.m[9]) * loaded->half[2];
				if (!model->keep_origin && height - reach < 0.3f + object_lifts[o])
					transform.m[13] += 0.3f + object_lifts[o] - (height - reach);
				const Mat4 world = object_world(o, &transform);
				write_instance_world(instances + *instance_count * 24, &world,
				                     object->standin == L3D_STANDIN_PLACEHOLDER ? STANDIN_SHADE : 1.0f);
				++*instance_count;
				if (clip_log)  // (where it is drawn)
				{
					clip_transforms[o] = transform;
					clip_worlds[o] = world;
					clip_drawn[o] = true;
				}
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
						palette_emission_of(b, c, loaded->palette_index[m]);
					}
				}
				if (b->albedo_alpha < 255)  // see-through materials (glass)
					b->transparency_enabled = 1;
				if (state->ghost)
				{
					b->transparency_enabled = 1;
					b->albedo_alpha = (Uint8)(b->albedo_alpha / 2);
				}
				if (state->appear != 0)
				{
					b->transparency_enabled = 1;
					b->albedo_alpha = (Uint8)(b->albedo_alpha * appear_alpha(state->appear));
					b->emission_energy *= appear_alpha(state->appear);
				}
				if (shown_step(f) < SHOWN_STEPS)
				{
					const float shown = (float)shown_step(f) / SHOWN_STEPS;
					b->transparency_enabled = 1;
					b->albedo_alpha = (Uint8)(b->albedo_alpha * shown);
					b->emission_energy *= shown;
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
			    object->filter != first->filter || object->ghost != first->ghost || object->open_sides != first->open_sides ||
			    object->appear != first->appear || shown_step(p) != shown_step(o))
				continue;
			done[p] = true;
			if (mesh == NULL || *instance_count >= MAX_INSTANCES || shown_step(p) == 0)
				continue;

			const float height = object_bases[p] + object->height + object_lifts[p];
			const Mat4 chain[] = {
				mat4_translation(object_x(object), height, object_y(object)),
				mat4_rotation(1, -object->yaw),
				mat4_rotation(2, -object->roll),
			};
			const Mat4 transform = mat4_chain((int)COUNTOF(chain), chain);
			float *instance = instances + *instance_count * 24;
			const Mat4 world = object_world(p, &transform);
			write_instance_world(instance, &world, 1.0f);
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
		if (first->appear != 0)
		{
			b->transparency_enabled = 1;
			b->albedo_alpha = (Uint8)(b->albedo_alpha * appear_alpha(first->appear));
			b->alpha_cutoff = 0.05f;
		}
		if (shown_step(o) < SHOWN_STEPS)
		{
			b->transparency_enabled = 1;
			b->albedo_alpha = (Uint8)(b->albedo_alpha * shown_step(o) / SHOWN_STEPS);
			b->alpha_cutoff = 0.05f;
		}
	}
}

/* --- Clouds --------------------------------------------------------------------------------------- */

/*
 * Cloud tiles (b3d_tile_is_cloud) of backgrounds 2 and 3 are soft clouds: add_background_batches
 * leaves them out of the tiles it draws, and collect_cloud_tiles takes them from the map over the view
 * and a margin round it (as far as their soft edges, puffs and shadows reach into the view), so that
 * clouds are whole before they come into view. For each background they are drawn into a canvas,
 * blurred into soft edges and shaded by their thickness from the light's side, worked out every
 * CLOUD_SCALE game pixels on a lattice fixed to the map (each texel is made of the same pixels of the
 * map every time the canvas is made again), then put into the texture at CLOUD_FINE times that, the
 * edges' ramps smooth (build_cloud_canvas). The canvas is drawn as two translucent slices at the
 * background's height (some depth in perspective), and once more, dark and faint, where the sun casts
 * its shadow, over the highest ground drawn under it (on the plane, raised ground would hide it).
 * Puffs heaped on the canvas give the clouds volume. The clouds stay above the ground drawn under them,
 * and solids that the game draws over the clouds but the 3D view below them clear the clouds where they
 * stand (note_cloud_ground).
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

#define MAX_CLOUD_TILES 2048
static CloudTile cloud_tiles[MAX_CLOUD_TILES];
static int cloud_tile_count = 0;
static Uint32 cloud_page_colors[4][256];  // by set: the colours its tiles are drawn in
// By set: the view its clouds were collected for and what they were collected over (game pixels at
// the tick: the view and the margins), how far the sun moves their shadow, and where its map's first
// column and row are on the screen (the canvas's lattice and its noise go with the map).
static float cloud_view[4][4], cloud_rect[4][4], cloud_shift[4][2], cloud_origin[4][2];

// Room round the view whose clouds are made too (game pixels): their soft edges, wander and puffs
// reach this far into it, their shadows as far again from the side the sun shines from. What is seen
// of them is worked out a little further than the view (CLOUD_SEEN; their shadows' too): puffs reach
// that far into it.
#define CLOUD_MARGIN 60.0f
#define CLOUD_SEEN 30.0f
// How far above the highest ground drawn under them the clouds float at least (their lower slice and
// puffs reach 1.5 below their height).
#define CLOUD_CLEARANCE 4.0f
// The canvas's coarse fields (its noise, the depth inside its clouds, their colours) are worked out
// every CLOUD_COARSE texels: the lattice the canvas is fixed to the map by.
#define CLOUD_COARSE 4

static struct
{
	bool used, blended;
	int set, layer;
	float x0, z0;  // game pixels, the canvas's top left
	int w, h;      // texels (CLOUD_SCALE game pixels; CLOUD_FINE times as many in the texture)
	float base;    // the height its clouds float at (cloud_base)
	// A tile of the map the canvas was made with, and where it was then and is now (the canvas is
	// remade every other tick; between, it moves with the map).
	int ref_row, ref_column;
	float ref_x, ref_z, dx, dz;
} cloud_canvases[MAX_CLOUD_CANVASES];

// Puffs: the clouds' volume, heaped on their canvases (cloud_puffs, made with each canvas).
typedef struct
{
	float x, z;        // game pixels, where the canvas was made
	float rise;        // above the clouds' height
	float radius;      // game pixels
	float color[3];    // linear
	float alpha;
	Uint8 variant, canvas;  // variant: how the puff is turned and mirrored
} CloudPuff;

static CloudPuff cloud_puffs[MAX_CLOUD_PUFFS];
static int cloud_puff_count = 0;

// What the frame draws under its clouds (note_cloud_ground): the top of the highest ground (the
// ground's terrain or relief, solids; world height), and the solids (backgrounds 2 and 3 as terrain,
// below what flies), which the game may draw over clouds that the 3D view draws above them.
typedef struct
{
	const L3DBackground *background;
	float top;
} CloudSolid;

static float cloud_ground_top = -1e9f;
static CloudSolid cloud_solids[L3D_MAX_BACKGROUNDS];
static int cloud_solid_count = 0;

static bool clouds_enabled(void)
{
	return m3d_enabled;
}

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

// The clouds' noise fields over a canvas (x0, z0: its top left on the map), worked out every
// CLOUD_COARSE texels and filled in between (the noise is smooth at that scale; per texel it would
// cost a frame's time); with `live` (by CLOUD_COARSE x CLOUD_COARSE texels, `qw` across), only there.
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

static void cloud_field(float *out, int w, int h, float x0, float z0, int which, const Uint8 *live, int qw)
{
	enum { MAX_COARSE = CLOUD_TEXELS / CLOUD_COARSE + 2 };
	static float coarse[MAX_COARSE * MAX_COARSE], row[MAX_COARSE];
	const int gw = w / CLOUD_COARSE + 2, gh = h / CLOUD_COARSE + 2;
	for (int gy = 0; gy < gh; ++gy)
		for (int gx = 0; gx < gw; ++gx)
			coarse[gy * gw + gx] = cloud_field_at(which, x0 + (gx * CLOUD_COARSE + 0.5f) * CLOUD_SCALE,
			                                      z0 + (gy * CLOUD_COARSE + 0.5f) * CLOUD_SCALE);
	for (int y = 0; y < h; ++y)
	{
		// (between the lattice's rows, then along the row a lattice step at a time)
		const float ty = (y % CLOUD_COARSE) * (1.0f / CLOUD_COARSE);
		const float *top = &coarse[y / CLOUD_COARSE * gw], *bottom = top + gw;
		for (int g = 0; g < gw; ++g)
			row[g] = top[g] + (bottom[g] - top[g]) * ty;
		float *o = &out[y * w];
		const Uint8 *live_row = live != NULL ? &live[y / CLOUD_COARSE * qw] : NULL;
		for (int x = 0, g = 0; x < w; x += CLOUD_COARSE, ++g)
		{
			if (live_row != NULL && !live_row[g])
				continue;
			const float step = (row[g + 1] - row[g]) * (1.0f / CLOUD_COARSE);
			const int end = x + CLOUD_COARSE < w ? x + CLOUD_COARSE : w;
			float value = row[g];
			for (int k = x; k < end; ++k, value += step)
				o[k] = value;
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

// Where the clouds of a layer float: at its height, but above the ground drawn under them.
static float cloud_base(const float *heights, int layer)
{
	return SDL_max(heights[layer], cloud_ground_top + CLOUD_CLEARANCE);
}

// How far the sun's light moves a cloud's shadow from under it (game pixels across and down the
// screen), for a cloud `drop` above the ground.
static void cloud_shadow_shift(float drop, float shift[2])
{
	const float down = SDL_max(-sun_direction[1], 0.05f);
	shift[0] = sun_direction[0] * drop / down;
	shift[1] = sun_direction[2] * drop / down;
}

// Takes a background's cloud tiles from its map, over the view (game pixels at the tick) and the
// margins round it, for its canvas; `drop`: how high its clouds are above the ground their shadows
// fall on.
static void collect_cloud_tiles(const L3DBackground *background, const float view[4], float drop)
{
	static B3DTile found[MAX_CLOUD_TILES * 2];
	const int set = background->set & 3;
	float shift[2];
	cloud_shadow_shift(drop, shift);
	memcpy(cloud_view[set], view, sizeof(cloud_view[set]));
	memcpy(cloud_shift[set], shift, sizeof(cloud_shift[set]));
	float *rect = cloud_rect[set];
	rect[0] = view[0] - CLOUD_MARGIN - SDL_max(shift[0], 0.0f);
	rect[1] = view[1] - CLOUD_MARGIN - SDL_max(shift[1], 0.0f);
	rect[2] = view[2] + CLOUD_MARGIN + SDL_max(-shift[0], 0.0f);
	rect[3] = view[3] + CLOUD_MARGIN + SDL_max(-shift[1], 0.0f);
	const int count = b3d_collect_tiles(background, false, rect[0], rect[1], rect[2], rect[3], found, (int)COUNTOF(found));
	for (int t = 0; t < count; ++t)
	{
		const B3DTile *tile = &found[t];
		if (t == 0)
		{
			// (From the rows the game drew, which follow each other in the map.)
			cloud_origin[set][0] = tile->x - tile->map_column * B3D_TILE_W;
			cloud_origin[set][1] = tile->z - tile->map_row * B3D_TILE_H;
		}
		const int index = tile->cell % B3D_TILES_PER_SET;
		if (tile->cell >= B3D_CELLS || tile->cell / B3D_TILES_PER_SET + 1 != background->set ||
		    !b3d_tile_is_cloud(background->set, index) || cloud_tile_count == MAX_CLOUD_TILES)
			continue;
		cloud_tiles[cloud_tile_count++] = (CloudTile){
			(Uint8)background->set, (Uint8)index, tile->flipped, background->blend, background->layer,
			tile->x, tile->z, cloud_page_colors[background->set], tile->map_row, tile->map_column };
	}
}

// Puts a tile's pixels at the texels' middles onto a canvas of w x h texels (the tile's top left
// `left`, `top` game pixels from the canvas's): 1 into `cover` where it has a pixel; with `tint`,
// their colours and how many into its sums by CLOUD_COARSE x CLOUD_COARSE texels (`qw` across), and
// their brightness into `light`.
static void cloud_point_raster(const Uint8 *data, bool flipped, int left, int top, int w, int h, float *cover,
                               float *const tint[4], float *light, const Uint32 *colors, int qw)
{
	enum { MID = CLOUD_SCALE / 2 };  // (the pixel at a texel's middle)
	const int x_first = SDL_max(0, (int)ceilf((left - MID) / (float)CLOUD_SCALE));
	const int x_last = SDL_min(w - 1, (int)floorf((left + B3D_TILE_W - 1 - MID) / (float)CLOUD_SCALE));
	const int y_first = SDL_max(0, (int)ceilf((top - MID) / (float)CLOUD_SCALE));
	const int y_last = SDL_min(h - 1, (int)floorf((top + B3D_TILE_H - 1 - MID) / (float)CLOUD_SCALE));
	for (int ty = y_first; ty <= y_last; ++ty)
	{
		const Uint8 *row = &data[(ty * CLOUD_SCALE + MID - top) * B3D_TILE_W];
		float *out = &cover[ty * w], *bright = light != NULL ? &light[ty * w] : NULL;
		const int q_row = ty / CLOUD_COARSE * qw;
		for (int tx = x_first; tx <= x_last; ++tx)
		{
			const int px = tx * CLOUD_SCALE + MID - left;
			const Uint8 value = row[flipped ? B3D_TILE_W - 1 - px : px];
			if (value == 0)
				continue;
			out[tx] = 1.0f;
			if (tint != NULL)
			{
				const Uint8 *rgb = (const Uint8 *)&colors[value];
				const int q = q_row + tx / CLOUD_COARSE;
				tint[0][q] += rgb[0];
				tint[1][q] += rgb[1];
				tint[2][q] += rgb[2];
				tint[3][q] += 1;
				bright[tx] = 0.299f * rgb[0] + 0.587f * rgb[1] + 0.114f * rgb[2];
			}
		}
	}
}

// Marks (0-1, blurred) where on a canvas the solids stand that the game draws over the clouds of
// `layer` while the 3D view draws them lower than the clouds (at `base`): the clouds clear there, as
// the game shows those solids over them. False when there is none.
static bool cloud_solid_mask(int layer, float base, float x0, float z0, int w, int h, float *mask, float *scratch)
{
	static B3DTile tiles[MAX_CLOUD_TILES * 2];
	bool any = false;
	for (int s = 0; s < cloud_solid_count; ++s)
	{
		const CloudSolid *solid = &cloud_solids[s];
		if (solid->background->layer <= layer || solid->top > base - 1.5f)
			continue;
		if (!any)
			memset(mask, 0, sizeof(float) * (size_t)(w * h));
		any = true;
		const int count = b3d_collect_tiles(solid->background, false, x0, z0, x0 + w * CLOUD_SCALE, z0 + h * CLOUD_SCALE,
		                                    tiles, (int)COUNTOF(tiles));
		for (int t = 0; t < count; ++t)
		{
			const B3DTile *tile = &tiles[t];
			const Uint8 *data = tile->cell < B3D_CELLS
			                        ? b3d_tile_pixels(tile->cell / B3D_TILES_PER_SET + 1, tile->cell % B3D_TILES_PER_SET)
			                        : NULL;
			if (data != NULL)
				cloud_point_raster(data, tile->flipped, (int)lroundf(tile->x - x0), (int)lroundf(tile->z - z0), w, h, mask,
				                   NULL, NULL, NULL, 0);
		}
	}
	if (any)
		box_blur(mask, scratch, w, h, 2);
	return any;
}

// A canvas row upsampled across into the texture's CLOUD_FINE (2) texels a texel: the alpha's ramp
// (field 0) through a quadratic B-spline (weights 0.28125, 0.6875, 0.03125 for the texture texel a
// quarter of a texel left of the middle, mirrored right of it: smooth, so that magnified no texel's
// edge shows), the colours (fields 1-3) linearly. A row that isn't `live` is clear.
_Static_assert(CLOUD_FINE == 2, "cloud_upsample_row makes two texture texels of a canvas texel");

static void cloud_upsample_row(float *const fields[4], int w, int y, bool live, float out[4][CLOUD_TEXELS * CLOUD_FINE])
{
	if (!live)  // (far from the clouds: clear)
	{
		memset(out[0], 0, sizeof(float) * (size_t)(w * CLOUD_FINE));
		return;
	}
	for (int k = 0; k < 4; ++k)
	{
		const float *f = fields[k] + y * w;
		float *o = out[k];
		const float a = k == 0 ? 0.28125f : 0.25f, b = k == 0 ? 0.6875f : 0.75f, c = k == 0 ? 0.03125f : 0.0f;
		float left = f[0], mid = f[0];
		for (int x = 0; x < w; ++x)
		{
			const float right = f[x + 1 < w ? x + 1 : x];
			o[2 * x] = a * left + b * mid + c * right;
			o[2 * x + 1] = c * left + b * mid + a * right;
			left = mid;
			mid = right;
		}
	}
}

// Draws one background's cloud tiles into canvas `c` (on the game's ticks); `base`: where its clouds
// float (cloud_base).
static void build_cloud_canvas(int c, int set, int layer, bool blended, float base)
{
	enum { N = CLOUD_TEXELS * CLOUD_TEXELS, Q = CLOUD_COARSE, QS = CLOUD_TEXELS / CLOUD_COARSE + 1, FW = CLOUD_TEXELS * CLOUD_FINE };
	static float cover[N], scratch[N], wide[N], field_a[N], field_b[N], solid[N], ramp[N], red[N], green[N], blue[N];
	static float light[N], local[N];
	static float small[QS * QS], small_scratch[QS * QS], tint_sums[4][QS * QS];
	static Uint8 live[QS * QS], nearby[QS * QS];
	static float up[3][4][FW];
	static Uint32 rgba[N * CLOUD_FINE * CLOUD_FINE];

	// What the canvas covers: its tiles and room for their soft edges round them, as far as the clouds
	// were collected (beyond, they don't reach into the view).
	float x0 = 1e9f, z0 = 1e9f, x1 = -1e9f, z1 = -1e9f;
	int ref = -1;
	for (int t = 0; t < cloud_tile_count; ++t)
		if (cloud_tiles[t].set == set)
		{
			if (ref < 0)
				ref = t;
			x0 = SDL_min(x0, cloud_tiles[t].x);
			z0 = SDL_min(z0, cloud_tiles[t].z);
			x1 = SDL_max(x1, cloud_tiles[t].x + B3D_TILE_W);
			z1 = SDL_max(z1, cloud_tiles[t].z + B3D_TILE_H);
		}
	const float *rect = cloud_rect[set & 3];
	const float margin = 40;  // room for the soft edges and their wander (game pixels)
	x0 = SDL_max(x0 - margin, rect[0]);
	z0 = SDL_max(z0 - margin, rect[1]);
	x1 = SDL_min(x1 + margin, rect[2]);
	z1 = SDL_min(z1 + margin, rect[3]);
	const float size = CLOUD_TEXELS * CLOUD_SCALE - CLOUD_SCALE * CLOUD_COARSE;  // (room to snap to the lattice)
	if (x1 - x0 > size)
	{
		const float centre = l3d_field_x() + l3d_field_w() / 2.0f;
		x0 = SDL_max(x0, centre - size / 2);
		x1 = x0 + size;
	}
	if (z1 - z0 > size)
		z0 = z1 - size;  // keep the near part
	// On the lattice fixed to the map.
	const float lattice = CLOUD_SCALE * CLOUD_COARSE, ox = cloud_origin[set & 3][0], oz = cloud_origin[set & 3][1];
	x0 = ox + floorf((x0 - ox) / lattice) * lattice;
	z0 = oz + floorf((z0 - oz) / lattice) * lattice;
	const int w = SDL_min(CLOUD_TEXELS, (int)ceilf((x1 - x0) / CLOUD_SCALE));
	const int h = SDL_min(CLOUD_TEXELS, (int)ceilf((z1 - z0) / CLOUD_SCALE));
	cloud_canvases[c].set = set;
	cloud_canvases[c].layer = layer;
	cloud_canvases[c].used = ref >= 0 && w > 0 && h > 0;
	if (!cloud_canvases[c].used)
		return;
	cloud_canvases[c].blended = blended;
	cloud_canvases[c].x0 = x0;
	cloud_canvases[c].z0 = z0;
	cloud_canvases[c].w = w;
	cloud_canvases[c].h = h;
	cloud_canvases[c].base = base;
	cloud_canvases[c].dx = cloud_canvases[c].dz = 0;
	cloud_canvases[c].ref_row = cloud_tiles[ref].map_row;
	cloud_canvases[c].ref_column = cloud_tiles[ref].map_column;
	cloud_canvases[c].ref_x = cloud_tiles[ref].x;
	cloud_canvases[c].ref_z = cloud_tiles[ref].z;
	const float map_x0 = x0 - ox, map_z0 = z0 - oz;  // the canvas's top left on the map

	// The tiles' pixels at the texels' middles, their colours by CLOUD_COARSE x CLOUD_COARSE texels.
	const int qw = (w + Q - 1) / Q, qh = (h + Q - 1) / Q;
	float *const tint[4] = { tint_sums[0], tint_sums[1], tint_sums[2], tint_sums[3] };
	memset(cover, 0, sizeof(float) * (size_t)(w * h));
	memset(light, 0, sizeof(float) * (size_t)(w * h));
	for (int k = 0; k < 4; ++k)
		memset(tint[k], 0, sizeof(float) * (size_t)(qw * qh));
	for (int t = 0; t < cloud_tile_count; ++t)
	{
		const CloudTile *tile = &cloud_tiles[t];
		const Uint8 *data = tile->set == set ? b3d_tile_pixels(tile->set, tile->tile) : NULL;
		if (data != NULL)
			cloud_point_raster(data, tile->flipped, (int)lroundf(tile->x - x0), (int)lroundf(tile->z - z0), w, h, cover, tint,
			                   light, tile->colors, qw);
	}
	// The tiles' own light and shade, lightly softened: how bright they are round each texel, and how
	// much of it they cover.
	memcpy(local, cover, sizeof(float) * (size_t)(w * h));
	box_blur(local, scratch, w, h, 1);
	box_blur(light, scratch, w, h, 1);
	for (int i = 0; i < w * h; ++i)
		light[i] = local[i] > 0.2f ? light[i] / local[i] : 0.0f;
	// Soft edges: the cover blurred (about a gaussian).
	box_blur(cover, scratch, w, h, 2);
	box_blur(cover, scratch, w, h, 2);
	// How deep inside the cloud: its cover blurred widely (at a quarter of the resolution: it is wide
	// and smooth); the clouds' colours, as widely (with the cover's edges eaten away and wandering
	// below, the tiles' own colours at a texel need not be the cloud's there).
	for (int qy = 0; qy < qh; ++qy)
		for (int qx = 0; qx < qw; ++qx)
		{
			const int y_end = SDL_min(qy * Q + Q, h), x_end = SDL_min(qx * Q + Q, w);
			float sum = 0;
			for (int y = qy * Q; y < y_end; ++y)
				for (int x = qx * Q; x < x_end; ++x)
					sum += cover[y * w + x];
			small[qy * qw + qx] = sum / ((y_end - qy * Q) * (x_end - qx * Q));
		}
	// What is worked out: blocks of CLOUD_COARSE x CLOUD_COARSE texels as near a cloud as its edges'
	// wander and shading reach (4 blocks), where they can be seen (the view, and where their shadows
	// fall in it, a little beyond: CLOUD_SEEN); the rest of the canvas stays clear.
	memset(nearby, 0, (size_t)(qw * qh));
	for (int qy = 0; qy < qh; ++qy)
		for (int qx = 0; qx < qw; ++qx)
			if (small[qy * qw + qx] > 1e-4f)
				memset(&nearby[qy * qw + SDL_max(qx - 4, 0)], 1, (size_t)(SDL_min(qx + 4, qw - 1) - SDL_max(qx - 4, 0) + 1));
	for (int qy = 0; qy < qh; ++qy)
		for (int qx = 0; qx < qw; ++qx)
		{
			Uint8 any = 0;
			for (int k = SDL_max(qy - 4, 0); k <= SDL_min(qy + 4, qh - 1) && !any; ++k)
				any = nearby[k * qw + qx];
			live[qy * qw + qx] = any;
		}
	{
		const float *view = cloud_view[set & 3], *shift = cloud_shift[set & 3];
		const float seen[4] = { SDL_min(view[0], view[0] - shift[0]) - CLOUD_SEEN, SDL_min(view[1], view[1] - shift[1]) - CLOUD_SEEN,
		                        SDL_max(view[2], view[2] - shift[0]) + CLOUD_SEEN, SDL_max(view[3], view[3] - shift[1]) + CLOUD_SEEN };
		const float block = CLOUD_SCALE * Q;
		for (int qy = 0; qy < qh; ++qy)
			for (int qx = 0; qx < qw; ++qx)
				if (x0 + (qx + 1) * block < seen[0] || x0 + qx * block > seen[2] || z0 + (qy + 1) * block < seen[1] ||
				    z0 + qy * block > seen[3])
					live[qy * qw + qx] = 0;
	}
	for (int pass = 0; pass < 3; ++pass)
	{
		box_blur(small, small_scratch, qw, qh, 1);
		for (int k = 0; k < 4; ++k)
			box_blur(tint[k], small_scratch, qw, qh, 1);
	}
	{
		double all[4] = { 0, 0, 0, 0 };  // (where no tile is near: the canvas's colour)
		for (int q = 0; q < qw * qh; ++q)
			for (int k = 0; k < 4; ++k)
				all[k] += tint[k][q];
		for (int q = 0; q < qw * qh; ++q)
		{
			const float n = tint[3][q];
			for (int k = 0; k < 3; ++k)
				tint[k][q] = n > 0.02f ? tint[k][q] / n : all[3] > 0 ? (float)(all[k] / all[3]) : 255.0f;
		}
	}
	{
		// (bilinearly: between rows first, then along them, the columns' weights worked out once)
		static int column[CLOUD_TEXELS];
		static float across[CLOUD_TEXELS], between[QS];
		for (int x = 0; x < w; ++x)
		{
			float fx = (x + 0.5f) / Q - 0.5f;
			fx = fx < 0 ? 0 : fx > qw - 1 ? (float)(qw - 1) : fx;
			column[x] = SDL_min((int)fx, qw - 2 > 0 ? qw - 2 : 0);
			across[x] = qw > 1 ? fx - column[x] : 0.0f;
		}
		const float *const quarter[4] = { small, tint[0], tint[1], tint[2] };
		float *const full[4] = { wide, red, green, blue };
		for (int y = 0; y < h; ++y)
		{
			const Uint8 *live_row = &live[y / Q * qw];
			float fy = (y + 0.5f) / Q - 0.5f;
			fy = fy < 0 ? 0 : fy > qh - 1 ? (float)(qh - 1) : fy;
			const int y0 = (int)fy, y1 = SDL_min(y0 + 1, qh - 1);
			const float ty = fy - y0;
			for (int k = 0; k < 4; ++k)
			{
				const float *a = quarter[k] + y0 * qw, *b = quarter[k] + y1 * qw;
				for (int g = 0; g < qw; ++g)
					between[g] = a[g] + (b[g] - a[g]) * ty;
				between[qw] = between[qw - 1];
				float *o = full[k] + y * w;
				for (int x = 0; x < w; ++x)
					if (live_row[x / Q])
					{
						const float *v = &between[column[x]];
						o[x] = v[0] + (v[1] - v[0]) * across[x];
					}
			}
		}
	}
	// The tiles' own light and shade as a factor on the clouds' colour, where the tiles are (`light`).
	for (int y = 0; y < h; ++y)
	{
		const Uint8 *live_row = &live[y / Q * qw];
		for (int x = 0; x < w; ++x)
		{
			const int i = y * w + x;
			if (!live_row[x / Q])
				continue;
			float inside = (local[i] - 0.35f) * 2.0f, factor = 1;
			if (inside > 0)
			{
				inside = inside < 1 ? inside * inside * (3 - 2 * inside) : 1;
				const float own = 0.299f * red[i] + 0.587f * green[i] + 0.114f * blue[i];
				float ratio = light[i] / (own > 1 ? own : 1);
				ratio = ratio < 0.6f ? 0.6f : ratio > 1.4f ? 1.4f : ratio;
				factor = 1 + (ratio - 1) * inside;
			}
			light[i] = factor;
		}
	}
	// The edges wander too: the cover is looked up a little way off, by noise (up to 8 texels), between
	// texels (looked up at the nearest, its edges would step); the tiles' light and shade with it.
	memcpy(scratch, cover, sizeof(float) * (size_t)(w * h));
	memset(cover, 0, sizeof(float) * (size_t)(w * h));
	cloud_field(field_a, w, h, map_x0, map_z0, CLOUD_WARP_X, live, qw);
	cloud_field(field_b, w, h, map_x0, map_z0, CLOUD_WARP_Z, live, qw);
	const float reach = 48.0f / CLOUD_SCALE, right = (float)(w - 1), bottom_row = (float)(h - 1);
	for (int y = 0; y < h; ++y)
	{
		const float *warp_x = &field_a[y * w], *warp_z = &field_b[y * w];
		const Uint8 *live_row = &live[y / Q * qw];
		float *out = &cover[y * w];
		for (int x = 0; x < w; ++x)
		{
			if (!live_row[x / Q])
				continue;
			float sx = x + (warp_x[x] - 0.5f) * reach, sz = y + (warp_z[x] - 0.5f) * reach;
			sx = sx < 0 ? 0 : sx > right ? right : sx;
			sz = sz < 0 ? 0 : sz > bottom_row ? bottom_row : sz;
			const int ix = (int)sx, iz = (int)sz;
			const int ix1 = ix + 1 < w ? ix + 1 : ix, iz1 = iz + 1 < h ? iz + 1 : iz;
			const float fx = sx - ix, fz = sz - iz;
			const int a = iz * w + ix, b = iz * w + ix1, d = iz1 * w + ix, e = iz1 * w + ix1;
			const float wa = (1 - fx) * (1 - fz), wb = fx * (1 - fz), wd = (1 - fx) * fz, we = fx * fz;
			out[x] = scratch[a] * wa + scratch[b] * wb + scratch[d] * wd + scratch[e] * we;
			ramp[y * w + x] = light[a] * wa + light[b] * wb + light[d] * wd + light[e] * we;
		}
	}
	// The edges (where it is low) are eaten away by large noise, so that clouds don't keep the tiles'
	// straight borders. Nothing at the canvas's edges (where a cloud the canvas cuts off would end in a
	// line), and the clouds fade out towards the furthest drawn row as the tiles do.
	cloud_field(field_a, w, h, map_x0, map_z0, CLOUD_ERODE, live, qw);
	cloud_field(field_b, w, h, map_x0 + glint_time * 3.0f, map_z0, CLOUD_BILLOW, live, qw);
	for (int y = 0; y < h; ++y)
	{
		float far = (BACKGROUND_AHEAD + z0 + (y + 0.5f) * CLOUD_SCALE) * (1.0f / BACKGROUND_FADE);
		far = far < 0 ? 0 : far > 1 ? 1 : far;
		const float edge_y = SDL_min(y, h - 1 - y) * (1.0f / 6);  // (6 texels in from the edges)
		float *out = &cover[y * w];
		const float *erode = &field_a[y * w], *deep = &wide[y * w];
		const Uint8 *live_row = &live[y / Q * qw];
		for (int x = 0; x < w; ++x)
		{
			if (!live_row[x / Q])
				continue;
			const float c0 = out[x], outer = deep[x] < 1 ? 1 - deep[x] : 0, thin = c0 * 3 < 1 ? c0 * 3 : 1;
			const float thick = c0 - 0.7f * erode[x] * outer * thin;
			float edge = SDL_min(x, w - 1 - x) * (1.0f / 6);
			edge = edge < edge_y ? edge : edge_y;
			out[x] = thick <= 0 ? 0 : thick * (edge < 1 ? edge : 1) * far;
		}
	}
	// Clear where solids stand that the game draws over these clouds (a little round them too).
	const bool cleared = cloud_solid_mask(layer, base, x0, z0, w, h, solid, scratch);
	if (cleared)
		for (int i = 0; i < w * h; ++i)
		{
			const float k = SDL_clamp((solid[i] - 0.12f) / 0.4f, 0.0f, 1.0f);
			cover[i] *= 1 - k * k * (3 - 2 * k);
		}

	// Puffs where the cloud is thick, at places fixed to the map: a few per tile, jittered, heaped
	// highest in the middle of the cloud (`wide`), small and sparse at its edges; those that can reach
	// into the view.
	const float *view = cloud_view[set & 3];
	for (int t = 0; t < cloud_tile_count; ++t)
	{
		const CloudTile *tile = &cloud_tiles[t];
		if (tile->set != set || tile->x + B3D_TILE_W < view[0] - CLOUD_SEEN || tile->x > view[2] + CLOUD_SEEN ||
		    tile->z + B3D_TILE_H < view[1] - CLOUD_SEEN || tile->z > view[3] + CLOUD_SEEN)
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
			const float edge_noise = cloud_noise(px - ox, pz - oz, 19.0f, 5);
			if (thickness < 0.35f + 0.35f * edge_noise * (1 - heap))
				continue;
			CloudPuff *puff = &cloud_puffs[cloud_puff_count++];
			puff->x = px;
			puff->z = pz;
			puff->rise = 1.0f + 15.0f * heap * heap + 2.5f * jr;
			puff->radius = 5.0f + 11.0f * heap + 3.0f * jr;
			for (int ch = 0; ch < 3; ++ch)
			{
				const float value = ch == 0 ? red[i] : ch == 1 ? green[i] : blue[i];
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

	// Each texel's alpha ramp (into `scratch`) and colour: the clouds' colour, with the tiles' own light
	// and shade (`ramp`). Billows: thicker and thinner patches that drift slowly with the wind, fixed to
	// the map. Lit from the upper left: brighter where the cloud thins towards the light, darker on the
	// far side; thin parts let more of the ground through.
	memset(scratch, 0, sizeof(float) * (size_t)(w * h));
	for (int y = 0; y < h; ++y)
	{
		const float *towards_row = &cover[(y >= 3 ? y - 3 : 0) * w], *away_row = &cover[(y + 3 < h ? y + 3 : h - 1) * w];
		const Uint8 *live_row = &live[y / Q * qw];
		for (int x = 0; x < w; ++x)
		{
			if (!live_row[x / Q])
				continue;
			const int i = y * w + x;
			float r = red[i] * ramp[i], g = green[i] * ramp[i], b = blue[i] * ramp[i];
			const float thickness = cover[i], billow = field_b[i];
			const float towards = towards_row[x >= 3 ? x - 3 : 0], away = away_row[x + 3 < w ? x + 3 : w - 1];
			float light = 1.0f + 1.8f * (away - towards);
			light = light < 0.68f ? 0.68f : light > 1.25f ? 1.25f : light;
			const float shade = light * (0.8f + 0.4f * billow);
			float t = (thickness * (0.55f + 0.9f * billow) - 0.06f) * (1 / 0.55f);
			scratch[i] = t < 0 ? 0 : t > 1 ? 1 : t;
			// Clouds whiter than the tiles.
			r = (r + (255.0f - r) * 0.3f) * shade;
			g = (g + (255.0f - g) * 0.3f) * shade;
			b = (b + (255.0f - b) * 0.3f) * shade;
			red[i] = r < 255 ? r : 255;
			green[i] = g < 255 ? g : 255;
			blue[i] = b < 255 ? b : 255;
		}
	}
	// Into the texture at CLOUD_FINE times the resolution (cloud_upsample_row across, the same down).
	const int fw = w * CLOUD_FINE, fh = h * CLOUD_FINE;
	float *const fields[4] = { scratch, red, green, blue };
	static Uint8 row_live[QS];
	for (int qy = 0; qy < qh; ++qy)
		row_live[qy] = memchr(&live[qy * qw], 1, (size_t)qw) != NULL;
	for (int y = 0; y < h && y < 2; ++y)
		cloud_upsample_row(fields, w, y, row_live[y / Q], up[y]);
	for (int y = 0; y < h; ++y)
	{
		if (y >= 1 && y + 1 < h)
			cloud_upsample_row(fields, w, y + 1, row_live[(y + 1) / Q], up[(y + 1) % 3]);
		float(*above)[FW] = up[SDL_max(y - 1, 0) % 3], (*mid)[FW] = up[y % 3], (*below)[FW] = up[SDL_min(y + 1, h - 1) % 3];
		const float *ta = above[0], *tm = mid[0], *tb = below[0];
		const float *ra = above[1], *rm = mid[1], *rb = below[1], *ga = above[2], *gm = mid[2], *gb = below[2];
		const float *ba = above[3], *bm = mid[3], *bb = below[3];
		Uint32 *upper_row = &rgba[(size_t)(2 * y) * fw];
		memset(upper_row, 0, sizeof(Uint32) * (size_t)(2 * fw));
		const Uint8 *live_row = &live[y / Q * qw];
		for (int qx = 0; qx < qw; ++qx)
		{
			if (!live_row[qx])
				continue;
			const int x_end = SDL_min((qx + 1) * Q * CLOUD_FINE, fw);
			for (int x = qx * Q * CLOUD_FINE; x < x_end; ++x)
			{
				Uint8 *upper = (Uint8 *)&upper_row[x], *lower = (Uint8 *)&upper_row[fw + x];
				// (alpha: the ramp smoothed, at most 0.85)
				float t = 0.28125f * ta[x] + 0.6875f * tm[x] + 0.03125f * tb[x];
				upper[3] = (Uint8)(t * t * (3 - 2 * t) * (0.85f * 255.0f) + 0.5f);
				t = 0.03125f * ta[x] + 0.6875f * tm[x] + 0.28125f * tb[x];
				lower[3] = (Uint8)(t * t * (3 - 2 * t) * (0.85f * 255.0f) + 0.5f);
				upper[0] = (Uint8)(0.25f * ra[x] + 0.75f * rm[x] + 0.5f);
				lower[0] = (Uint8)(0.75f * rm[x] + 0.25f * rb[x] + 0.5f);
				upper[1] = (Uint8)(0.25f * ga[x] + 0.75f * gm[x] + 0.5f);
				lower[1] = (Uint8)(0.75f * gm[x] + 0.25f * gb[x] + 0.5f);
				upper[2] = (Uint8)(0.25f * ba[x] + 0.75f * bm[x] + 0.5f);
				lower[2] = (Uint8)(0.75f * bm[x] + 0.25f * bb[x] + 0.5f);
			}
		}
	}
	btbh_gpu_texture_update_rgba8(cloud_texture, (const uint8_t *)rgba, 0, c * CLOUD_TEXELS * CLOUD_FINE, fw, fh);
	// A clear texel beyond the canvas's right and bottom edges, so filtering there fades out.
	static Uint32 clear[CLOUD_TEXELS * CLOUD_FINE + 1];
	if (fw < CLOUD_TEXELS * CLOUD_FINE)
		btbh_gpu_texture_update_rgba8(cloud_texture, (const uint8_t *)clear, fw, c * CLOUD_TEXELS * CLOUD_FINE, 1,
		                              SDL_min(fh + 1, CLOUD_TEXELS * CLOUD_FINE));
	if (fh < CLOUD_TEXELS * CLOUD_FINE)
		btbh_gpu_texture_update_rgba8(cloud_texture, (const uint8_t *)clear, 0, c * CLOUD_TEXELS * CLOUD_FINE + fh,
		                              SDL_min(fw + 1, CLOUD_TEXELS * CLOUD_FINE), 1);
	if (SDL_getenv("TYR3D_LOG_CLOUDS") != NULL)
		printf("clouds: canvas %d set %d layer %d at %.0f,%.0f, %dx%d texels, height %.1f over ground %.1f%s (frame %u)\n", c,
		       set, layer, x0, z0, w, h, base, cloud_ground_top, cleared ? ", solids over it" : "", l3d_frame_number);
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
	dim_by_fade(b);
	dim_by_filter(b);
	b->uv_scale_x = (float)cloud_canvases[c].w / CLOUD_TEXELS;
	b->uv_scale_y = (float)cloud_canvases[c].h / (CLOUD_TEXELS * MAX_CLOUD_CANVASES);
	b->uv_offset_y = (float)c / MAX_CLOUD_CANVASES;
	b->unlit_enabled = 1;
	b->transparency_enabled = 1;
	b->blend_mode = BTBH_GPU_SCENE_BLEND_ALPHA;
}

static float srgb_to_linear(Uint8 value);

// The puffs, farthest first (they are blended), as billboards facing the camera.
static void add_cloud_puffs(const Camera3D *camera, int *instance_count, int *batch_count)
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
		position[i][1] = cloud_canvases[puff->canvas].base + puff->rise;
		position[i][2] = puff->z + cloud_canvases[puff->canvas].dz + speed;
		const float d[3] = { position[i][0] - camera->position[0], position[i][1] - camera->position[1],
		                     position[i][2] - camera->position[2] };
		depth[i] = d[0] * camera->forward[0] + d[1] * camera->forward[1] + d[2] * camera->forward[2];
		order[i] = i;
	}
	// Farthest first (insertion sort: they are made in about that order, compare_cloud_puffs).
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
	dim_by_fade(b);
	dim_by_filter(b);
	b->billboard_mode = BTBH_GPU_SCENE_BILLBOARD_FRONT;
	b->unlit_enabled = 1;
	b->transparency_enabled = 1;
	b->blend_mode = BTBH_GPU_SCENE_BLEND_ALPHA;
}

// The puffs by how far up the screen they are: about the order of their depth.
static int compare_cloud_puffs(const void *a, const void *b)
{
	const float za = ((const CloudPuff *)a)->z, zb = ((const CloudPuff *)b)->z;
	return za < zb ? -1 : za > zb;
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
				build_cloud_canvas(canvases, cloud_tiles[t].set, cloud_tiles[t].layer, cloud_tiles[t].blended,
				                   cloud_base(heights, cloud_tiles[t].layer));
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
		qsort(cloud_puffs, (size_t)cloud_puff_count, sizeof(cloud_puffs[0]), compare_cloud_puffs);
	}

	for (int c = 0; c < MAX_CLOUD_CANVASES; ++c)
	{
		if (!cloud_canvases[c].used)
			continue;
		// Where the clouds float: above the ground drawn under them.
		const float height = cloud_base(heights, cloud_canvases[c].layer);
		cloud_canvases[c].base = height;
		// The shadow, where the sun's light through the cloud lands on the ground (as from clouds floating
		// higher than their layer), drawn over the highest ground under it: on the plane, raised ground
		// would hide it.
		const float ground = heights[0] + 0.15f;
		float shift[2];
		cloud_shadow_shift(height - ground + 30.0f, shift);
		add_cloud_quad(c, SDL_max(ground, SDL_min(cloud_ground_top + 0.5f, height - 3.0f)), shift[0], shift[1], 0.0f,
		               cloud_canvases[c].blended ? 0.22f : 0.3f, instance_count, batch_count);
		// The cloud: two slices, a little apart, for some depth; clouds the game blends with what is
		// below let about half of it through.
		const float opacity = cloud_canvases[c].blended ? 0.42f : 0.7f;
		add_cloud_quad(c, height - 1.5f, 0, 0, 0.94f, opacity, instance_count, batch_count);
		add_cloud_quad(c, height + 1.5f, 0, 0, 1.0f, opacity, instance_count, batch_count);
	}
	// Their volume: puffs heaped on them.
	add_cloud_puffs(camera, instance_count, batch_count);
}

static float relief_height(void);

// Notes what the frame draws of a background under the clouds (add_background_batches): its plane at
// `height` as terrain (its relief drawn align_scale times as high about the plane), in relief by tiles,
// or flat; and whether it is a solid. The ground, background 2 drawn with it and the solids are under
// the clouds (the clouds stay above them, their shadows over them).
static void note_cloud_ground(const L3DFrame *frame, const L3DBackground *background, float height, bool solid, bool relief)
{
	float top = height;
	if (terrain_background(frame, background))
		top += SDL_max(frame_terrains[background->set]->highest, 0) * align_scale(height);
	else if (relief)
		top += relief_height() * align_scale(height);
	if (background->set == 1 || solid || frame->layers[background->layer].type == L3D_BG2_LOW)
		cloud_ground_top = SDL_max(cloud_ground_top, top);
	if (solid && cloud_solid_count < (int)COUNTOF(cloud_solids))
		cloud_solids[cloud_solid_count++] = (CloudSolid){ background, top };
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
// Background 2 drawn under the ground enemies and opaque all over (APPROACH's sea, ICESECRET's ice)
// hides the ground: the ground stays flat under it (no terrain, no relief), and its enemies stand on
// background 2, which is the ground then (its own terrain, where its map has one: ICESECRET).
static const L3DBackground *covering_ground(const L3DFrame *frame)
{
	for (int i = 0; i < frame->background_count; ++i)
		if (frame->backgrounds[i].set >= 2 && !frame->backgrounds[i].blend &&
		    frame->layers[frame->backgrounds[i].layer].type == L3D_BG2_LOW && b3d_map_opaque(frame->backgrounds[i].set))
			return &frame->backgrounds[i];
	return NULL;
}

static bool ground_covered(const L3DFrame *frame)
{
	return covering_ground(frame) != NULL;
}

static bool relief_frame(const L3DFrame *frame, const bool *composed)
{
	if (!m3d_enabled || relief_height() <= 0 || frame->space || ground_covered(frame))
		return false;
	for (int i = 0; i < frame->background_count; ++i)
		if (frame->backgrounds[i].set == 1)
			return !composed[i] && frame->backgrounds[i].effect_count == 0;
	return false;
}

// TYR3D_LOG_GROUND_MODE: how the ground is drawn whenever that changes: as terrain (its map and heights),
// in relief by tiles, or flat and why.
static void log_ground(const L3DFrame *frame, const bool *composed)
{
	static char last[192];
	char now[192];
	int g = -1;
	for (int i = 0; i < frame->background_count; ++i)
		if (frame->backgrounds[i].set == 1)
			g = i;
	const unsigned long long map = g >= 0 ? (unsigned long long)b3d_map_hash(1) : 0;
	const B3DTerrain *t = g >= 0 ? b3d_terrain(1) : NULL;
	const L3DBackground *cover = covering_ground(frame);
	if (cover != NULL && cover == lift_ground)
		SDL_snprintf(now, sizeof(now), "terrain %016llx of background %d %d..%d", (unsigned long long)b3d_map_hash(cover->set),
		             cover->set, lift_terrain->lowest, lift_terrain->highest);
	else if (g < 0)
		SDL_snprintf(now, sizeof(now), "none");
	else if (frame_terrains[1] != NULL)
		SDL_snprintf(now, sizeof(now), "terrain %016llx %d..%d%s", map, t->lowest, t->highest, t->hole_count > 0 ? " holes" : "");
	else if (relief_frame(frame, composed))
		SDL_snprintf(now, sizeof(now), "relief %016llx%s", map, t != NULL ? " (terrain not drawn)" : "");
	else
	{
		char terrain[64] = "";
		if (t != NULL)
			SDL_snprintf(terrain, sizeof(terrain), "; terrain %d..%d%s", t->lowest, t->highest, t->holes ? " v2" : " v1");
		SDL_snprintf(now, sizeof(now), "flat %016llx (%s%s)", map,
		             frame->star_count > 0 ? "stars" : composed[g] ? "composed" : frame->backgrounds[g].effect_count > 0 ? "filter" :
		             !m3d_enabled ? "models off" : "relief off", terrain);
	}
	if (SDL_strcmp(now, last) != 0)
	{
		printf("ground mode: %s (3D frame %u)\n", now, l3d_frame_number);
		SDL_strlcpy(last, now, sizeof(last));
	}
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
// Map rows a terrain texture holds (terrain_ring), more than are ever drawn at once; fewer with HD
// tiles (the texture is b3d_hd_scale() times larger each way).
#define TERRAIN_RING_ROWS 80
#define TERRAIN_RING_ROWS_HD 40

static int terrain_ring_rows(void)
{
	return b3d_hd_scale() > 1 ? TERRAIN_RING_ROWS_HD : TERRAIN_RING_ROWS;
}

static struct
{
	int set, map_row;
	float hole_depth;
	unsigned int generation;  // b3d_map_generation + 1, or 0 for a free slot
	Uint32 used;
	BTBHGPUCustomMesh *mesh;
	BTBHGPUCustomMesh *lid;  // a solid's: its top alone (solid_lids)
} terrain_rows[TERRAIN_ROWS_CACHED];
static Uint32 terrain_clock = 0;
static bool terrain_batch[MAX_BATCHES];  // batches of terrain (they cast shadows)

static bool terrain_background(const L3DFrame *frame, const L3DBackground *background)
{
	// Backgrounds 2 and 3 as solids only when drawn over the ground's enemies (under them, a
	// solid would bury them); solid, they aren't blended. Background 2 covering the ground is the
	// ground: its terrain is the ground's (covering_ground).
	if (background->set < 1 || background->set > B3D_SETS || frame_terrains[background->set] == NULL)
		return false;
	return background->set == 1 || frame->layers[background->layer].type != L3D_BG2_LOW ||
	       background == covering_ground(frame);
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

// How far a terrain's walls go down where it has holes, drawn at the given height: in the ground,
// chasms; in backgrounds 2 and 3 (solid), the walls of their solids go down to below the ground.
static float terrain_hole_depth(bool solid, float height)
{
	return solid ? height * 1.5f + 8.0f : TERRAIN_HOLE_DEPTH;
}

// The ground's terrain as stored at a game position (0 over a hole or off the map), not as drawn (what
// the lift was before stand_lift; TYR3D_LOG_CLIP=2 prints it beside the lift).
static float terrain_lift(float x, float y)
{
	const B3DTerrain *t = lift_terrain;
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

/*
 * What stands on the ground (its enemies, explosions and lights) stands on the ground as
 * it is drawn. The ground's terrain rows are drawn aligned on their plane (aligned(): k times as large
 * about the point below the camera, so the relief is drawn k times as high, about 1.23), and an object
 * is aligned at its own height, a little less enlarged: the world point under it is the drawn ground of
 * a game position nearer the point below the camera than its own (on a 28 pixel plateau some 10 % of
 * the way there: up to 30 pixels at the screen's top). An object's lift is how far above background 1's
 * plane the ground is drawn under it (0 on a flat ground), found in a few steps (the point under it moves
 * with the lift): it stands as high above what is drawn under it as it would above a flat ground. Game
 * positions stay as they are.
 *
 * The ground: the ground's terrain (background 1's, or that of a background 2 covering the ground),
 * else background 1 flat; a flat background 2 drawn under the ground enemies (the game draws them over
 * it) lifts what stands where it has a pixel onto its plane (APPROACH's sea, 2 pixels up).
 */
#define STAND_STEPS 3
// On a slope a thing stands on the ground drawn under the edge of its footprint that the camera sees, but
// at most this much relief (game pixels) above or below the ground under its middle (by a cliff).
#define STAND_FOOTPRINT_RISE 4.0f

typedef struct
{
	const L3DBackground *background;
	bool valid;
	float x, z;       // a tile's top-left corner, game screen coordinates at the tick
	int row, column;  // its place in the map (map_row, map_column)
} MapAnchor;

static struct
{
	bool on;                          // set up for the frame (setup_stand)
	const L3DBackground *background;  // the ground: its terrain's background, else background 1 (flat); NULL: none
	const B3DTerrain *terrain;        // its terrain, or NULL: flat
	float height, k;                  // its plane (its rows' and tiles') and align_scale there
	float plane;                      // background 1's plane, which the lifts are reckoned from
	float rise;                       // the ground's plane above it (a background 2 covering the ground)
	float shift;                      // how far the ground has scrolled on since the tick (game pixels)
	const L3DBackground *low;         // a flat background 2 drawn under the ground enemies, or NULL
	float low_k, low_rise, low_shift; // its align_scale, its plane above background 1's, its scroll
	Uint32 stamp;                     // (the frame's anchors, stand_anchor)
} stand;

// The tile of a background under the game point x, y as drawn (scrolled on by shift since the tick):
// its rows and columns go on from it for points nearby. Kept for each row of tiles for the frame.
static bool stand_anchor(const L3DBackground *b, float shift, float x, float y, MapAnchor *anchor)
{
	enum { CACHED = 32 };
	static struct
	{
		Uint32 stamp;
		const L3DBackground *background;
		int row;
		MapAnchor anchor;
	} cache[CACHED];
	const float gy = y - shift;
	const int row = (int)floorf((gy - b->top_y) / B3D_TILE_H);
	const int slot = row & (CACHED - 1);
	if (cache[slot].stamp == stand.stamp && cache[slot].background == b && cache[slot].row == row)
	{
		*anchor = cache[slot].anchor;
		return anchor->valid;
	}
	B3DTile tiles[32];
	const int count = b3d_collect_tiles(b, true, x, gy, x, gy, tiles, (int)COUNTOF(tiles));
	anchor->background = b;
	anchor->valid = false;
	for (int i = 0; i < count && !anchor->valid; ++i)
		if (gy >= tiles[i].z && gy < tiles[i].z + B3D_TILE_H)
		{
			anchor->valid = true;
			anchor->x = tiles[i].x;
			anchor->z = tiles[i].z;
			anchor->row = tiles[i].map_row;
			anchor->column = tiles[i].map_column;
		}
	cache[slot].stamp = stand.stamp;
	cache[slot].background = b;
	cache[slot].row = row;
	cache[slot].anchor = *anchor;
	return anchor->valid;
}

// The ground's relief (its terrain's own height; over holes, and beyond its columns, its plane) at the
// game point x, y of its plane as drawn, by a tile near it: between the samples as its rows' triangles
// have it (build_terrain_row). Off its rows (before the level's start, past its end) nothing is drawn:
// false.
static bool stand_relief_at(const MapAnchor *a, float x, float y, float *relief)
{
	const B3DTerrain *t = stand.terrain;
	*relief = 0.0f;
	if (t == NULL || !a->valid)
		return false;
	const int per_x = B3D_TILE_W / t->sample;
	const float mx = a->column * B3D_TILE_W + (x - a->x), my = a->row * B3D_TILE_H + (y - stand.shift - a->z);
	const float fx = mx / t->sample + (float)(t->side_columns * per_x), fy = my / t->sample;
	if (!(fy >= 0 && fy < (float)(t->height - 1)))
		return false;
	if (!(fx >= 0 && fx < (float)((t->width - 1) / per_x * per_x)))
		return true;  // (flat tiles beyond its columns)
	const int sx = (int)fx, sy = (int)fy;
	const float ax = fx - sx, ay = fy - sy;
	float h[4];  // the cell's corners a (sx, sy), b (sx + 1, sy), d (sx, sy + 1), e (sx + 1, sy + 1)
	for (int c = 0; c < 4; ++c)
	{
		const Sint8 value = t->heights[(sy + (c >> 1)) * t->width + sx + (c & 1)];
		h[c] = t->holes && value == B3D_TERRAIN_HOLE ? 0.0f : (float)value;
	}
	// (its triangles a b e and a e d)
	*relief = ax >= ay ? h[0] + ax * (h[1] - h[0]) + ay * (h[3] - h[1]) : h[0] + ay * (h[2] - h[0]) + ax * (h[3] - h[2]);
	return true;
}

static float stand_relief(const MapAnchor *a, float x, float y)
{
	float relief;
	stand_relief_at(a, x, y, &relief);
	return relief;
}

// Whether the ground (the frame's, stand) is water at the game point x, y as drawn: its tile's pixel there
// is one of the level's water (b3d_water_pixel).
static bool ground_water_at(float x, float y)
{
	MapAnchor a;
	if (!stand.on || stand.background == NULL || !stand_anchor(stand.background, stand.shift, x, y, &a))
		return false;
	const float mx = a.column * B3D_TILE_W + (x - a.x), my = a.row * B3D_TILE_H + (y - stand.shift - a.z);
	const int column = (int)floorf(mx / B3D_TILE_W), row = (int)floorf(my / B3D_TILE_H);
	bool flipped;
	const int cell = b3d_map_cell(stand.background->set, row, column, &flipped);
	if (cell < 0 || cell >= B3D_CELLS)
		return false;
	const int set = cell / B3D_TILES_PER_SET + 1, tile = cell % B3D_TILES_PER_SET;
	const Uint8 *pixels = b3d_tile_pixels(set, tile);
	if (pixels == NULL)
		return false;
	const int px = SDL_clamp((int)floorf(mx - column * B3D_TILE_W), 0, B3D_TILE_W - 1);
	const int py = SDL_clamp((int)floorf(my - row * B3D_TILE_H), 0, B3D_TILE_H - 1);
	return b3d_water_pixel(set, tile, pixels[py * B3D_TILE_W + (flipped ? B3D_TILE_W - 1 - px : px)]);
}

// Whether a flat background has a pixel at the game point x, y of its plane as drawn (scrolled on by
// shift since the tick), by a tile near it.
static bool plane_has_pixel(const MapAnchor *a, float shift, float x, float y)
{
	if (!a->valid)
		return false;
	const float mx = a->column * B3D_TILE_W + (x - a->x), my = a->row * B3D_TILE_H + (y - shift - a->z);
	const int column = (int)floorf(mx / B3D_TILE_W), row = (int)floorf(my / B3D_TILE_H);
	bool flipped;
	const int cell = b3d_map_cell(a->background->set, row, column, &flipped);
	if (cell < 0 || cell >= B3D_CELLS)
		return false;
	const Uint8 *pixels = b3d_tile_pixels(cell / B3D_TILES_PER_SET + 1, cell % B3D_TILES_PER_SET);
	if (pixels == NULL)
		return false;
	const int px = SDL_clamp((int)floorf(mx - column * B3D_TILE_W), 0, B3D_TILE_W - 1);
	const int py = SDL_clamp((int)floorf(my - row * B3D_TILE_H), 0, B3D_TILE_H - 1);
	return pixels[py * B3D_TILE_W + (flipped ? B3D_TILE_W - 1 - px : px)] != 0;
}

// The frame's ground for standing on (present_3d, once heights and the camera are known).
static void setup_stand(const L3DFrame *frame, const bool *composed, const float *heights)
{
	const Uint32 stamp = stand.stamp + 1;
	memset(&stand, 0, sizeof(stand));
	stand.stamp = stamp;
	stand.on = true;
	const L3DBackground *ground = NULL;
	for (int i = 0; i < frame->background_count; ++i)
		if (frame->backgrounds[i].set == 1)
			ground = &frame->backgrounds[i];
	stand.plane = ground != NULL ? heights[ground->layer] - TILE_BELOW_LAYER : -TILE_BELOW_LAYER;
	stand.background = lift_ground != NULL ? lift_ground : ground;
	stand.terrain = lift_ground != NULL ? lift_terrain : NULL;
	stand.height = lift_ground != NULL ? heights[lift_ground->layer] - TILE_BELOW_LAYER : stand.plane;
	stand.k = align_scale(stand.height);
	stand.rise = stand.height - stand.plane;
	stand.shift = stand.background != NULL ? background_speed[stand.background->set & 3] * ahead : 0.0f;
	for (int i = 0; i < frame->background_count; ++i)
	{
		const L3DBackground *b = &frame->backgrounds[i];
		if (b == lift_ground || b->set < 2 || b->blend || frame->layers[b->layer].type != L3D_BG2_LOW)
			continue;
		const float height = heights[b->layer] - TILE_BELOW_LAYER - (composed[i] ? 0.1f : 0.0f);
		stand.low = b;
		stand.low_k = align_scale(height);
		stand.low_rise = height - stand.plane;
		stand.low_shift = background_speed[b->set & 3] * ahead;
	}
}

// How far above background 1's plane the ground is drawn under a thing standing at the game point x, y
// (as drawn) when it stands at `base + lift` (it is aligned there, which places the world point under
// it): the ground's under the edge of its footprint the camera sees (stand_lift), or a flat background
// 2 drawn under the ground enemies where it has a pixel under it.
typedef struct
{
	MapAnchor ground, low;
	bool on_ground, on_low;
	float x, y, base;
	const float *footprint;  // {x0, y0, x1, y1} round x, y (game pixels as drawn), or NULL for a point
	const float *slope;      // how it leans: its base rises this much (world) a game pixel of its footprint
	                         // across x and z (ObjectLean's slope times align_scale); NULL: upright
} StandQuery;

// The edge of a footprint that faces the camera (towards the point below it), from the game point of the
// ground's plane under its middle: its samples are (i, j) on the footprint's 3 x 3 grid, n = 0..2.
static void stand_front(float mx, float my, int n, int *i, int *j)
{
	const float dx = align.cx - mx, dz = align.cz - my;
	const bool rows = fabsf(dz) >= fabsf(dx);
	*i = rows ? n : dx > 0 ? 2 : 0;
	*j = rows ? (dz > 0 ? 2 : 0) : n;
}

static float stand_under(const StandQuery *q, float lift)
{
	static const float point[4] = { 0, 0, 0, 0 };
	const float *f = q->footprint != NULL ? q->footprint : point;
	const int samples = q->footprint != NULL ? 3 : 1;
	const float kb = align_scale(q->base + lift);
	float under = stand.rise;
	if (q->on_ground)
	{
		// The game points of the ground's plane under it: its own, a little nearer the point below
		// the camera.
		const float r = kb / stand.k;
		const float gx = align.cx + (q->x - align.cx) * r, gy = align.cz + (q->y - align.cz) * r;
		const float mx = gx + (f[0] + f[2]) / 2 * r, my = gy + (f[1] + f[3]) / 2 * r;
		// (Leaning, its base at a point of its footprint is that much higher than at its position: the
		// ground there counts that much lower, in its relief's units.)
		const float tx = q->slope != NULL ? q->slope[0] / stand.k : 0.0f;
		const float tz = q->slope != NULL ? q->slope[1] / stand.k : 0.0f;
		const float middle = stand_relief(&q->ground, mx, my) - tx * (f[0] + f[2]) / 2 - tz * (f[1] + f[3]) / 2;
		// On a slope, on the ground under the edge of its footprint that faces the camera (towards the
		// point below the camera; its three samples' mean): no gap shows under that edge, nor ground over
		// it; its far side floats or sinks behind it.
		float front = middle;
		if (samples > 1)
		{
			float sum = 0;
			int counted = 0;  // (not where nothing is drawn)
			for (int n = 0; n < 3; ++n)
			{
				int i, j;
				stand_front(mx, my, n, &i, &j);
				const float u = f[0] + (f[2] - f[0]) * i / 2, v = f[1] + (f[3] - f[1]) * j / 2;
				float relief;
				if (stand_relief_at(&q->ground, gx + u * r, gy + v * r, &relief))
				{
					sum += relief - tx * u - tz * v;
					++counted;
				}
			}
			if (counted > 0)
				front = sum / counted;
		}
		under += stand.k * SDL_clamp(front, middle - STAND_FOOTPRINT_RISE, middle + STAND_FOOTPRINT_RISE);
	}
	if (q->on_low)
	{
		const float r = kb / stand.low_k;
		const float gx = align.cx + (q->x - align.cx) * r, gy = align.cz + (q->y - align.cz) * r;
		bool over = false;
		for (int j = 0; j < samples && !over; ++j)
			for (int i = 0; i < samples && !over; ++i)
			{
				const float u = samples > 1 ? (f[0] + (f[2] - f[0]) * i / 2) : 0.0f;
				const float v = samples > 1 ? (f[1] + (f[3] - f[1]) * j / 2) : 0.0f;
				over = plane_has_pixel(&q->low, stand.low_shift, gx + u * r, gy + v * r);
			}
		if (over)
			under = SDL_max(under, stand.low_rise);
	}
	return under;
}

// What stand_lift asks about a thing (StandQuery): false if neither the ground's terrain nor a flat background 2
// drawn under the ground enemies is under it.
static bool stand_query(float x, float y, float base, const float footprint[4], const float slope[2], StandQuery *q)
{
	q->on_ground = stand.terrain != NULL && stand_anchor(stand.background, stand.shift, x, y, &q->ground);
	q->on_low = stand.low != NULL && stand_anchor(stand.low, stand.low_shift, x, y, &q->low);
	q->x = x;
	q->y = y;
	q->base = base;
	q->footprint = footprint;
	q->slope = slope;
	return q->on_ground || q->on_low;
}

// The ground drawn under a thing's footprint (its 3 x 3 grid: corners, edges' middles and middle) when it
// stands at base + lift: how far above background 1's plane (world), at the points (u, v: game pixels as
// drawn round its position) where the ground's terrain is drawn. Returns how many there are.
static int stand_samples(const StandQuery *q, float lift, float *h, float *u, float *v)
{
	if (!q->on_ground || q->footprint == NULL)
		return 0;
	const float *f = q->footprint;
	const float kb = align_scale(q->base + lift), r = kb / stand.k;
	const float gx = align.cx + (q->x - align.cx) * r, gy = align.cz + (q->y - align.cz) * r;
	const float rl = q->on_low ? kb / stand.low_k : 0.0f;
	const float lx = align.cx + (q->x - align.cx) * rl, ly = align.cz + (q->y - align.cz) * rl;
	int count = 0;
	for (int j = 0; j < 3; ++j)
		for (int i = 0; i < 3; ++i)
		{
			const float su = f[0] + (f[2] - f[0]) * i / 2, sv = f[1] + (f[3] - f[1]) * j / 2;
			float relief;
			if (!stand_relief_at(&q->ground, gx + su * r, gy + sv * r, &relief))
				continue;
			h[count] = stand.rise + stand.k * relief;
			// (a flat background 2 drawn under the ground enemies covers the terrain where it has a pixel)
			if (q->on_low && plane_has_pixel(&q->low, stand.low_shift, lx + su * rl, ly + sv * rl))
				h[count] = SDL_max(h[count], stand.low_rise);
			u[count] = su;
			v[count] = sv;
			++count;
		}
	return count;
}

// How high a thing standing at the game point x, y (as drawn) stands on the ground: how far above
// background 1's plane the ground is drawn under it, when its height before the lift is `base` (where
// its translation is). footprint: what it covers round x, y (game pixels as drawn, relative: x0, y0, x1,
// y1), or NULL for a point; leaning (StandQuery.slope, stand_lift_query), its base along the slope. Where
// it stands depends on how high it stands (the point under it moves with its height), so a few steps find
// where the two agree; by the far edge of raised ground they may never agree (placed at the plateau's
// height the point under it is past the edge, placed lower it is not): then the lowest height at which the
// ground drawn under it is no higher than its base (it hugs the cliff rather than sink into it).
#define STAND_SEARCH 6       // halvings of the search between the last two steps
#define STAND_TOLERANCE 0.05f

static float stand_lift_query(const StandQuery *query);

static float stand_lift(float x, float y, float base, const float footprint[4])
{
	if (!stand.on || stand.background == NULL)
		return 0.0f;
	StandQuery q;
	if (!stand_query(x, y, base, footprint, NULL, &q))
		return stand.rise;
	return stand_lift_query(&q);
}

static float stand_lift_query(const StandQuery *query)
{
	const StandQuery q = *query;
	const float x = q.x, y = q.y;
	// (first guess: the ground drawn at its own game position)
	float lift = stand.rise + (q.on_ground ? stand.k * stand_relief(&q.ground, x, y) : 0.0f);
	float next = lift;
	for (int step = 0; step < STAND_STEPS; ++step)
	{
		next = stand_under(&q, lift);
		if (fabsf(next - lift) < STAND_TOLERANCE)
			return next;
		if (step + 1 < STAND_STEPS)
			lift = next;
	}
	float low = SDL_min(lift, next), high = SDL_max(lift, next);
	if (stand_under(&q, low) <= low + STAND_TOLERANCE)
		return low;
	if (stand_under(&q, high) > high + STAND_TOLERANCE)
		return high;
	for (int n = 0; n < STAND_SEARCH; ++n)
	{
		const float middle = (low + high) / 2;
		if (stand_under(&q, middle) > middle + STAND_TOLERANCE)
			low = middle;
		else
			high = middle;
	}
	return high;
}

// How far above background 1's plane the ground is drawn under a world point (x, z): the ground's
// lift there (TYR3D_LOG_CLIP's float).
static float stand_ground_at(float x, float z)
{
	if (!stand.on || stand.background == NULL)
		return 0.0f;
	float under = stand.rise;
	MapAnchor a;
	if (stand.terrain != NULL)
	{
		const float gx = align.cx + (x - align.cx) / stand.k, gy = align.cz + (z - align.cz) / stand.k;
		if (stand_anchor(stand.background, stand.shift, gx, gy, &a))
			under += stand.k * stand_relief(&a, gx, gy);
	}
	if (stand.low != NULL)
	{
		const float gx = align.cx + (x - align.cx) / stand.low_k, gy = align.cz + (z - align.cz) / stand.low_k;
		if (stand_anchor(stand.low, stand.low_shift, gx, gy, &a) && plane_has_pixel(&a, stand.low_shift, gx, gy))
			under = SDL_max(under, stand.low_rise);
	}
	return under;
}

// The height a layer puts what is drawn in it at (an object, a glow): l3d_layer_height; but what
// flies, drawn after a flat background that the 3D view puts higher (background 3 drawn under the
// player or over it before the sky or top enemies are: events 21 and 29, 73), stands above that
// background as far as it stands above the one under it in the usual order (background 2 for the sky
// enemies, background 3 for the top enemies), not under its plane. phase: the draw phase it was
// recorded in (L3DObject.phase).
static float layer_base(const L3DFrame *frame, const float *heights, L3DLayerType layer, int phase)
{
	const float hs = rgpu_camera.height_scale;
	float base = l3d_layer_height(layer) * hs;
	const L3DLayerType under = layer == L3D_SKY_ENEMY ? L3D_BG2 : layer == L3D_TOP_ENEMY ? L3D_BG3 : L3D_OVERLAY;
	if (under == L3D_OVERLAY)
		return base;
	const float over = (l3d_layer_height(layer) - l3d_layer_height(under)) * hs;
	for (int i = 0; i < frame->background_count; ++i)
	{
		const L3DBackground *b = &frame->backgrounds[i];
		// (Solids stand low, below what flies.)
		if (b->phase >= phase || l3d_layer_height(frame->layers[b->layer].type) <= l3d_layer_height(layer) ||
		    (b->set > 1 && terrain_background(frame, b) && b != lift_ground))
			continue;
		base = SDL_max(base, heights[b->layer] + over);
	}
	return base;
}

// What an object covers of the ground round its position (game pixels as drawn, relative: x0, y0, x1,
// y1) and how high it is (footprint[4], before alignment): a model's bounds as it is turned and scaled,
// a volumetric sprite's sprite (nearly flat). False: nothing known.
static bool object_footprint(const L3DObject *object, bool mirror, float footprint[5])
{
	if (object->model == L3D_VOLUME)
	{
		const float w = object->large ? 12.0f : 6.0f, h = object->large ? 14.0f : 7.0f;
		footprint[0] = -w;
		footprint[1] = -h;
		footprint[2] = w;
		footprint[3] = h;
		footprint[4] = 2.0f;
		return true;
	}
	const LoadedModel *loaded = object->model >= 0 && object->model < m3d_model_count ? get_model(object->model) : NULL;
	if (loaded == NULL)
		return false;
	const Mat4 t = object_transform(object, loaded, mirror, 0.0f);
	footprint[0] = footprint[1] = INFINITY;
	footprint[2] = footprint[3] = -INFINITY;
	float y0 = INFINITY, y1 = -INFINITY;
	for (int c = 0; c < 8; ++c)
	{
		const float p[3] = { loaded->center[0] + ((c & 1) ? loaded->half[0] : -loaded->half[0]),
		                     loaded->center[1] + ((c & 2) ? loaded->half[1] : -loaded->half[1]),
		                     loaded->center[2] + ((c & 4) ? loaded->half[2] : -loaded->half[2]) };
		const float x = t.m[0] * p[0] + t.m[4] * p[1] + t.m[8] * p[2] + t.m[12] - object_x(object);
		const float y = t.m[1] * p[0] + t.m[5] * p[1] + t.m[9] * p[2];
		const float z = t.m[2] * p[0] + t.m[6] * p[1] + t.m[10] * p[2] + t.m[14] - object_y(object);
		footprint[0] = SDL_min(footprint[0], x);
		footprint[1] = SDL_min(footprint[1], z);
		footprint[2] = SDL_max(footprint[2], x);
		footprint[3] = SDL_max(footprint[3], z);
		y0 = SDL_min(y0, y);
		y1 = SDL_max(y1, y);
	}
	footprint[4] = y1 - y0;
	return true;
}

// Pieces with one link made this many ticks apart at most are one object (a row of 28 pixels every 28
// ticks at a pixel a tick, longer on slow maps).
#define PIECES_LINK_TICKS 100
#define STANDIN_STEP 6.0f      // a wreck's stand-ins whose own ground differs more than this (pixels) stand apart

// A piece of one object: a ground enemy whose model is drawn at its own origin, side by side with the
// others' on the sprites' grid (L3DObject.group: which object).
static bool lifted_piece(const L3DObject *object)
{
	return object->layer == L3D_GROUND_ENEMY && object->group != 0 && object->model >= 0 &&
	       object->model < m3d_model_count && m3d_models[object->model].keep_origin;
}

// Tyrian3D dev (TYR3D_LOG_GROUND): what the models of ground enemies cover round their positions, for
// tools/terrain/make_terrain.py (the game's "ground:" lines name each enemy's sheet and first sprite):
// "groundmodel: <sheet> <first sprite> <model> <x0> <y0> <x1> <y1> <height> <bottom> <top>", for each
// sheet and sprite the union of what its models have covered so far (object_footprint: game pixels as
// drawn, round the position; the height, and how high its bottom and top are over the ground's plane
// before it is lifted, before alignment), printed whenever it grows.
static bool ground_model_log_on(void)
{
	static int on = -1;
	if (on < 0)
		on = SDL_getenv("TYR3D_LOG_GROUND") != NULL;
	return on != 0;
}

static void log_ground_model(const L3DObject *object, bool mirror, float base, const float footprint[5])
{
	if (!ground_model_log_on() || object->enemy_sheet == 0 || object->standin != 0 || object->model < 0 ||
	    object->model >= m3d_model_count)
		return;
	const LoadedModel *loaded = get_model(object->model);
	if (loaded == NULL)
		return;
	const Mat4 t = object_transform(object, loaded, mirror, 0.0f);
	float bottom = INFINITY, top = -INFINITY;
	for (int c = 0; c < 8; ++c)
	{
		const float p[3] = { loaded->center[0] + ((c & 1) ? loaded->half[0] : -loaded->half[0]),
		                     loaded->center[1] + ((c & 2) ? loaded->half[1] : -loaded->half[1]),
		                     loaded->center[2] + ((c & 4) ? loaded->half[2] : -loaded->half[2]) };
		const float y = t.m[1] * p[0] + t.m[5] * p[1] + t.m[9] * p[2] + base;
		bottom = SDL_min(bottom, y);
		top = SDL_max(top, y);
	}
	static struct
	{
		Uint32 key;
		float box[7];
	} seen[2048];
	static int seen_count = 0;
	const Uint32 key = ((Uint32)(Uint8)object->enemy_sheet << 16) | object->enemy_sprite;
	int k = 0;
	while (k < seen_count && seen[k].key != key)
		++k;
	if (k == seen_count)
	{
		if (seen_count == (int)SDL_arraysize(seen))
			return;
		seen[k].key = key;
		seen[k].box[0] = seen[k].box[1] = INFINITY;
		seen[k].box[2] = seen[k].box[3] = -INFINITY;
		seen[k].box[4] = 0.0f;
		seen[k].box[5] = INFINITY;
		seen[k].box[6] = -INFINITY;
		++seen_count;
	}
	float *box = seen[k].box;
	const float slack = 0.25f;
	if (footprint[0] >= box[0] - slack && footprint[1] >= box[1] - slack && footprint[2] <= box[2] + slack &&
	    footprint[3] <= box[3] + slack && footprint[4] <= box[4] + slack && bottom >= box[5] - slack && top <= box[6] + slack)
		return;
	box[0] = SDL_min(box[0], footprint[0]);
	box[1] = SDL_min(box[1], footprint[1]);
	box[2] = SDL_max(box[2], footprint[2]);
	box[3] = SDL_max(box[3], footprint[3]);
	box[4] = SDL_max(box[4], footprint[4]);
	box[5] = SDL_min(box[5], bottom);
	box[6] = SDL_max(box[6], top);
	printf("groundmodel: %u %u %s %.1f %.1f %.1f %.1f %.1f %.1f %.1f\n", (unsigned int)(Uint8)object->enemy_sheet,
	       (unsigned int)object->enemy_sprite, m3d_models[object->model].name, box[0], box[1], box[2], box[3], box[4], box[5],
	       box[6]);
}

static int lift_group_root(int *group, int o)
{
	while (group[o] != o)
		o = group[o] = group[group[o]];
	return o;
}

/*
 * Leaning with the ground. On terrain, what stands on the ground leans with the ground drawn under it, by
 * pitch and roll (its yaw stays), at most LEAN_MOST degrees:
 * - a thing alone by the plane that fits the ground under its footprint best (its 3 x 3 grid, least
 *   squares), where that ground is a plane rather than a step (LEAN_STEP_*), still standing on the edge of
 *   its footprint that faces the camera (stand_lift, leaning);
 * - the pieces of one object (a boss, an ore tug and its load) all on one plane, so that they stay one as
 *   the game draws them: the lean that fits the ground under their edges facing the camera best (near the
 *   plane of the ground under all of them), and at its height their lifts' mean, but no piece deeper in the
 *   ground under it anywhere than half its height (lean_group, lean_pieces). (Each piece standing on its own
 *   ground would still meet the others on screen, each being aligned at its own height, but their light and
 *   shadows show the steps between them, and their edges crack.)
 * The lean follows the ground smoothly (LEAN_TICKS of the game's time), so nothing jitters as the map
 * scrolls under it. Where it leans about stays where the game puts it, and what leans is moved along the
 * camera's ray by what the lean raised it, so it is seen where the game draws it (lean_matrix). Game
 * positions stay as they are; a flat ground gives no lean.
 */
#define LEAN_MOST 12.0f       // degrees
#define LEAN_TICKS 4.0f       // the time it takes to follow the ground (its time constant, game ticks)
#define LEAN_FORGET 30.0      // ticks an object not drawn keeps its lean
#define LEAN_STEP_FROM 1.5f   // a thing alone leans less where the ground under it is further than this from a
#define LEAN_STEP_ALL 3.0f    // plane (root mean square, game pixels of relief), not at all from this on
#define PIECE_SINK 0.5f       // the share of its height a piece may stand in the ground under it anywhere
#define LEAN_PRIOR 50.0f      // what leaning otherwise than the ground's plane costs, per piece and slope squared
                              // (against the world pixels the pieces float or sink)
#define LEAN_STAY 10.0f       // and otherwise than it leant before (so that it doesn't swap between two)

// The lean each object had when it was last drawn, by its key (L3DObject.key; every piece of an object
// keeps the object's).
#define LEAN_STATES 2048
static struct
{
	Uint32 key;   // 0: free
	double time;  // when: l3d_frame_number + ahead
	float sx, sz;
} lean_states[LEAN_STATES];

static double lean_now(void)
{
	return (double)l3d_frame_number + ahead;
}

static bool lean_fresh(double time)
{
	const double now = lean_now();
	return time >= now - LEAN_FORGET && time <= now;
}

static int lean_slot(Uint32 key, bool make)
{
	Uint32 slot = (key * 2654435761u) % LEAN_STATES;
	int free_slot = -1;
	for (int probe = 0; probe < 16; ++probe, slot = (slot + 1) % LEAN_STATES)
	{
		if (lean_states[slot].key == key)
			return (int)slot;
		if (free_slot < 0 && (lean_states[slot].key == 0 || !lean_fresh(lean_states[slot].time)))
			free_slot = (int)slot;
	}
	if (!make || free_slot < 0)
		return -1;
	lean_states[free_slot].key = key;
	lean_states[free_slot].time = -1e30;
	return free_slot;
}

// The lean an object had (any of its pieces' keys), and how many ticks ago; false if none.
static bool lean_recall(const Uint32 *keys, int count, float lean[2], double *ago)
{
	for (int i = 0; i < count; ++i)
	{
		const int slot = keys[i] != 0 ? lean_slot(keys[i], false) : -1;
		if (slot < 0 || !lean_fresh(lean_states[slot].time))
			continue;
		lean[0] = lean_states[slot].sx;
		lean[1] = lean_states[slot].sz;
		*ago = lean_now() - lean_states[slot].time;
		return true;
	}
	return false;
}

static void lean_remember(const Uint32 *keys, int count, const float lean[2])
{
	for (int i = 0; i < count; ++i)
	{
		const int slot = keys[i] != 0 ? lean_slot(keys[i], true) : -1;
		if (slot < 0)
			continue;
		lean_states[slot].time = lean_now();
		lean_states[slot].sx = lean[0];
		lean_states[slot].sz = lean[1];
	}
}

// From the lean it had towards the one the ground gives, smoothly in the game's time.
static void lean_toward(bool had, const float was[2], double ago, const float target[2], float out[2])
{
	const float a = had ? 1.0f - expf(-(float)ago / LEAN_TICKS) : 1.0f;
	for (int i = 0; i < 2; ++i)
		out[i] = had ? was[i] + a * (target[i] - was[i]) : target[i];
}

static void lean_limit(float lean[2])
{
	const float most = tanf(LEAN_MOST * (float)M_PI / 180.0f);
	const float length = sqrtf(lean[0] * lean[0] + lean[1] * lean[1]);
	if (length > most)
	{
		lean[0] *= most / length;
		lean[1] *= most / length;
	}
}

// The plane h = a + b (u - mu) + c (v - mv) through points by least squares (mu, mv their mean):
// out = { mu, mv, a, b, c, how far the points are from it (root mean square) }; false if they don't span one.
static bool fit_plane(const float *h, const float *u, const float *v, int count, float out[6])
{
	if (count < 3)
		return false;
	float mu = 0, mv = 0, mh = 0;
	for (int i = 0; i < count; ++i)
	{
		mu += u[i];
		mv += v[i];
		mh += h[i];
	}
	mu /= count;
	mv /= count;
	mh /= count;
	float suu = 0, suv = 0, svv = 0, suh = 0, svh = 0;
	for (int i = 0; i < count; ++i)
	{
		const float du = u[i] - mu, dv = v[i] - mv, dh = h[i] - mh;
		suu += du * du;
		suv += du * dv;
		svv += dv * dv;
		suh += du * dh;
		svh += dv * dh;
	}
	const float det = suu * svv - suv * suv;
	if (!(det > 1e-3f * SDL_max(suu * svv, 1e-6f)))
		return false;
	out[0] = mu;
	out[1] = mv;
	out[2] = mh;
	out[3] = (suh * svv - svh * suv) / det;
	out[4] = (svh * suu - suh * suv) / det;
	float off = 0;
	for (int i = 0; i < count; ++i)
	{
		const float e = h[i] - mh - out[3] * (u[i] - mu) - out[4] * (v[i] - mv);
		off += e * e;
	}
	out[5] = sqrtf(off / count);
	return true;
}

// A thing alone on the terrain: its lean (by the plane under its footprint) and its lift with it.
static void lean_alone(const L3DObject *object, int o, const float *footprint)
{
	const float base = object_bases[o] + object->height;
	StandQuery q;
	if (!stand_query(object_x(object), object_y(object), base, footprint, NULL, &q) || !q.on_ground)
		return;
	float was[2] = { 0, 0 };
	double ago = 0;
	const bool had = lean_recall(&object->key, 1, was, &ago);
	float lift = object_lifts[o], k = align_scale(base + lift);
	float slope[2] = { was[0] * k, was[1] * k };
	q.slope = slope;
	if (had && (was[0] != 0 || was[1] != 0))
		lift = stand_lift_query(&q);
	// The ground under it there: where it is a slope, not a step (by a cliff it stands as upright things do).
	float h[9], u[9], v[9], plane[6], target[2] = { 0, 0 };
	k = align_scale(base + lift);
	if (fit_plane(h, u, v, stand_samples(&q, lift, h, u, v), plane))
	{
		const float plain = SDL_clamp((LEAN_STEP_ALL - plane[5] / stand.k) / (LEAN_STEP_ALL - LEAN_STEP_FROM), 0.0f, 1.0f);
		target[0] = plain * plane[3] / k;
		target[1] = plain * plane[4] / k;
		lean_limit(target);
	}
	float lean[2];
	lean_toward(had, was, ago, target, lean);
	lean_remember(&object->key, 1, lean);
	if (had ? fabsf(lean[0] - was[0]) + fabsf(lean[1] - was[1]) > 1e-4f : lean[0] != 0 || lean[1] != 0)
	{
		slope[0] = lean[0] * k;
		slope[1] = lean[1] * k;
		lift = stand_lift_query(&q);
	}
	object_lifts[o] = lift;
	object_leans[o] = (ObjectLean){ lean[0], lean[1], object_x(object), object_y(object), base + lift, 0.0f };
}

// A piece of an object leaning together (lean_group).
typedef struct
{
	int object;
	float x, y;          // its position (game, as drawn)
	float base;          // its height before its lift
	float lift;          // what it would stand at alone, upright: the ground under its edge facing the camera
	float fx, fy;        // that edge's middle, from its position (game pixels as drawn)
	int first, samples;  // the ground under it (lean_group's h, u, v)
	float sink;          // how deep in the ground under it it may stand anywhere (world)
} LeanPiece;

// Where the pieces of an object stand leaning by `lean` (world rise per world unit) about (x0, y0) (k:
// align_scale there): all on one plane, its height at (x0, y0) in *height: their lifts' mean, but no piece
// deeper in the ground under it than it may (PIECE_SINK of its height); returns what it costs: how far the
// pieces stand from their own ground in all (world pixels), and leaning otherwise than `prior` (the plane of
// the ground under them) or than `was` (the lean before; NULL: none).
static float lean_pieces(const LeanPiece *pieces, int count, float x0, float y0, float k, const float lean[2],
                         const float prior[2], const float *was, const float *h, const float *u, const float *v,
                         float *height)
{
	static float own[L3D_MAX_OBJECTS];
	float mean = 0, least = -INFINITY;
	for (int i = 0; i < count; ++i)
	{
		const LeanPiece *p = &pieces[i];
		own[i] = p->lift - k * (lean[0] * (p->x + p->fx - x0) + lean[1] * (p->y + p->fy - y0));
		mean += own[i];
		for (int s = p->first; s < p->first + p->samples; ++s)
			least = SDL_max(least, h[s] - k * (lean[0] * (u[s] - x0) + lean[1] * (v[s] - y0)) - p->sink);
	}
	*height = SDL_max(mean / count, least);
	float wrong = 0;  // (floating and sinking)
	for (int i = 0; i < count; ++i)
		wrong += fabsf(*height - own[i]);
	const float dx = lean[0] - prior[0], dz = lean[1] - prior[1];
	const float sx = was != NULL ? lean[0] - was[0] : 0.0f, sz = was != NULL ? lean[1] - was[1] : 0.0f;
	return wrong + count * (LEAN_PRIOR * (dx * dx + dz * dz) + LEAN_STAY * (sx * sx + sz * sz));
}

// The pieces of one object on the terrain (members: their objects; footprints by object): one plane, one
// lean, so that they stay one as the game draws them.
static void lean_group(const L3DFrame *frame, const int *members, int count, float (*footprints)[5])
{
	static LeanPiece pieces[L3D_MAX_OBJECTS];
	static Uint32 keys[L3D_MAX_OBJECTS];
	static float h[L3D_MAX_OBJECTS * 9], u[L3D_MAX_OBJECTS * 9], v[L3D_MAX_OBJECTS * 9];
	int samples = 0;
	float x0 = 0, y0 = 0, base0 = 0, lift0 = 0;
	for (int i = 0; i < count; ++i)
	{
		const int o = members[i];
		const L3DObject *object = &frame->objects[o];
		const float *f = footprints[o];
		LeanPiece *p = &pieces[i];
		p->object = o;
		p->x = object_x(object);
		p->y = object_y(object);
		p->base = object_bases[o] + object->height;
		p->lift = object_lifts[o];
		int fi[3], fj[3];
		for (int n = 0; n < 3; ++n)
			stand_front(p->x + (f[0] + f[2]) / 2, p->y + (f[1] + f[3]) / 2, n, &fi[n], &fj[n]);
		p->fx = f[0] + (f[2] - f[0]) * (fi[0] + fi[1] + fi[2]) / 6.0f;
		p->fy = f[1] + (f[3] - f[1]) * (fj[0] + fj[1] + fj[2]) / 6.0f;
		keys[i] = object->key;
		x0 += p->x;
		y0 += p->y;
		base0 += p->base;
		lift0 += p->lift;
		// The ground under it, for the plane under them all and how deep it stands.
		StandQuery q;
		p->first = samples;
		p->samples = 0;
		p->sink = PIECE_SINK * f[4] * align_scale(p->base + p->lift);
		if (stand_query(p->x, p->y, p->base, f, NULL, &q))
		{
			const int n = stand_samples(&q, p->lift, h + samples, u + samples, v + samples);
			for (int s = samples; s < samples + n; ++s)
			{
				u[s] += p->x;
				v[s] += p->y;
			}
			samples += n;
			p->samples = n;
		}
	}
	x0 /= count;
	y0 /= count;
	base0 /= count;
	lift0 /= count;
	const float k = align_scale(base0 + lift0);

	// The plane of the ground under them, and the lean near it that fits their own ground best.
	float plane[6], prior[2] = { 0, 0 };
	if (fit_plane(h, u, v, samples, plane))
	{
		prior[0] = plane[3] / k;
		prior[1] = plane[4] / k;
		lean_limit(prior);
	}
	float was[2] = { 0, 0 };
	double ago = 0;
	const bool had = lean_recall(keys, count, was, &ago);
	const float *stay = had ? was : NULL;
	float best[2] = { prior[0], prior[1] }, height;
	float best_cost = lean_pieces(pieces, count, x0, y0, k, best, prior, stay, h, u, v, &height);
	const float most = tanf(LEAN_MOST * (float)M_PI / 180.0f);
	const float starts[2][2] = { { 0, 0 }, { was[0], was[1] } };
	for (int c = 0; c < 2; ++c)
	{
		const float cost = lean_pieces(pieces, count, x0, y0, k, starts[c], prior, stay, h, u, v, &height);
		if (cost < best_cost)
		{
			best_cost = cost;
			best[0] = starts[c][0];
			best[1] = starts[c][1];
		}
	}
	// A grid over the leans allowed, then finer round the best.
	float centre[2] = { 0, 0 }, step = most / 3;
	for (int round = 0; round < 4; ++round)
	{
		const int reach = round == 0 ? 3 : 1;
		for (int b = -reach; b <= reach; ++b)
			for (int a = -reach; a <= reach; ++a)
			{
				float lean[2] = { centre[0] + a * step, centre[1] + b * step };
				if (lean[0] * lean[0] + lean[1] * lean[1] > most * most * 1.0001f)
					continue;
				const float cost = lean_pieces(pieces, count, x0, y0, k, lean, prior, stay, h, u, v, &height);
				if (cost < best_cost)
				{
					best_cost = cost;
					best[0] = lean[0];
					best[1] = lean[1];
				}
			}
		centre[0] = best[0];
		centre[1] = best[1];
		step /= 2;
	}
	float lean[2];
	lean_toward(had, was, ago, best, lean);
	lean_remember(keys, count, lean);
	lean_pieces(pieces, count, x0, y0, k, lean, prior, NULL, h, u, v, &height);
	for (int i = 0; i < count; ++i)
	{
		const int o = pieces[i].object;
		object_lifts[o] = height;
		object_leans[o] = (ObjectLean){ lean[0], lean[1], x0, y0, base0 + height, pieces[i].base - base0 };
	}
}

// The heights the frame's objects' layers put them at (layer_base), and how high those on the ground
// stand on it (stand_lift). The pieces of one object (L3DObject.group, group_link: made by the level's
// events at one time, or with one link not long apart; side by side on the sprites' grid, moving alike:
// MINERS's ore tug and its load, eight enemies; CAMANIS's boss, made row by row) stand together, so that
// they don't come apart where the ground under them changes height: on one plane, their lifts' mean, but no
// piece sunk more than half its height (by its edge, part of it overhangs rather than be buried); on
// terrain the plane leans with the ground (lean_group). Pieces of different objects never join, however
// near and alike (TYRIAN's walkers did, into one chain lifted at its middle). On terrain things alone lean
// with the ground too (lean_alone).
static void compute_object_lifts(const L3DFrame *frame, const float *heights, bool mirror)
{
	static int group[L3D_MAX_OBJECTS], pieces[L3D_MAX_OBJECTS];
	static float piece_heights[L3D_MAX_OBJECTS];
	static float footprints[L3D_MAX_OBJECTS][5];
	static bool covers[L3D_MAX_OBJECTS];
	int piece_count = 0;
	const bool leaning = stand.on && stand.terrain != NULL;
	for (int o = 0; o < frame->object_count; ++o)
	{
		const L3DObject *object = &frame->objects[o];
		group[o] = o;
		object_bases[o] = layer_base(frame, heights, object->layer, object->phase);
		object_lifts[o] = 0.0f;
		object_leans[o] = (ObjectLean){ 0 };
		covers[o] = false;
		if (object->layer != L3D_GROUND_ENEMY || !stand.on || stand.background == NULL)
			continue;
		float *footprint = footprints[o];
		if (stand.terrain == NULL && stand.low == NULL)
		{
			object_lifts[o] = stand.rise;  // (a flat ground)
			if (ground_model_log_on() && object_footprint(object, mirror, footprint))
				log_ground_model(object, mirror, object_bases[o] + object->height, footprint);
			continue;
		}
		covers[o] = object_footprint(object, mirror, footprint);
		if (covers[o])
			log_ground_model(object, mirror, object_bases[o] + object->height, footprint);
		else
			memset(footprint, 0, sizeof(footprints[o]));
		piece_heights[o] = covers[o] ? footprint[4] * align_scale(object_bases[o] + object->height) : 0.0f;
		object_lifts[o] = stand_lift(object_x(object), object_y(object), object_bases[o] + object->height,
		                             covers[o] ? footprint : NULL);
		if (lifted_piece(object))
			pieces[piece_count++] = o;
	}
	// Neighbours on the 24 x 28 grid (a few pixels' slack: events shift some pieces) moving alike, made
	// at one time, or with one link not long apart (a boss made row by row as the map scrolls).
	for (int i = 0; i < piece_count; ++i)
		for (int j = i + 1; j < piece_count; ++j)
		{
			const L3DObject *a = &frame->objects[pieces[i]], *b = &frame->objects[pieces[j]];
			const bool together = a->group == b->group ||
			                      (a->group_link != 0 && a->group_link == b->group_link &&
			                       abs((int)a->group - (int)b->group) <= PIECES_LINK_TICKS);
			if (together && fabsf(a->x - b->x) <= 28.0f && fabsf(a->y - b->y) <= 32.0f && fabsf(a->vx - b->vx) < 0.01f &&
			    fabsf(a->vy - b->vy) < 0.01f)
				group[lift_group_root(group, pieces[j])] = lift_group_root(group, pieces[i]);
		}
	// A wreck's stand-ins (the pieces lying where the game paints them) over a step in the ground, the edge of a
	// pillar or a cliff: each piece on its own ground, not all at their mean, which floated the ones off the
	// step (SAVARA V's airship in its slot on a rock in the sea, up to 16 pixels over the water).
	{
		static float lo[L3D_MAX_OBJECTS], hi[L3D_MAX_OBJECTS];
		static bool all_standins[L3D_MAX_OBJECTS];
		for (int i = 0; i < piece_count; ++i)
		{
			lo[pieces[i]] = INFINITY;
			hi[pieces[i]] = -INFINITY;
			all_standins[pieces[i]] = true;
		}
		for (int i = 0; i < piece_count; ++i)
		{
			const int root = lift_group_root(group, pieces[i]);
			lo[root] = SDL_min(lo[root], object_lifts[pieces[i]]);
			hi[root] = SDL_max(hi[root], object_lifts[pieces[i]]);
			all_standins[root] &= frame->objects[pieces[i]].standin != 0;
		}
		static bool apart[L3D_MAX_OBJECTS];
		for (int i = 0; i < piece_count; ++i)
		{
			const int root = lift_group_root(group, pieces[i]);
			apart[pieces[i]] = all_standins[root] && hi[root] - lo[root] > STANDIN_STEP;
		}
		for (int i = 0; i < piece_count; ++i)
			if (apart[pieces[i]])
				group[pieces[i]] = pieces[i];
	}
	static int n[L3D_MAX_OBJECTS];
	for (int i = 0; i < piece_count; ++i)
		n[pieces[i]] = 0;
	for (int i = 0; i < piece_count; ++i)
		++n[lift_group_root(group, pieces[i])];
	if (leaning)
	{
		// Each object of pieces together; each thing alone by itself.
		static int members[L3D_MAX_OBJECTS];
		for (int i = 0; i < piece_count; ++i)
		{
			const int root = lift_group_root(group, pieces[i]);
			if (root != pieces[i] && n[root] > 1)
				continue;
			int count = 0;
			for (int j = 0; j < piece_count; ++j)
				if (lift_group_root(group, pieces[j]) == root)
					members[count++] = pieces[j];
			if (count > 1)
				lean_group(frame, members, count, footprints);
		}
		for (int o = 0; o < frame->object_count; ++o)
		{
			const L3DObject *object = &frame->objects[o];
			if (object->layer == L3D_GROUND_ENEMY && covers[o] && (!lifted_piece(object) || n[lift_group_root(group, o)] < 2))
				lean_alone(object, o, footprints[o]);
		}
		return;
	}
	static float sum[L3D_MAX_OBJECTS], least[L3D_MAX_OBJECTS];
	for (int i = 0; i < piece_count; ++i)
	{
		least[pieces[i]] = -INFINITY;
		sum[pieces[i]] = 0;
	}
	for (int i = 0; i < piece_count; ++i)
	{
		const int root = lift_group_root(group, pieces[i]);
		least[root] = SDL_max(least[root], object_lifts[pieces[i]] - piece_heights[pieces[i]] / 2);
		sum[root] += object_lifts[pieces[i]];
	}
	for (int i = 0; i < piece_count; ++i)
	{
		const int root = lift_group_root(group, pieces[i]);
		object_lifts[pieces[i]] = SDL_max(sum[root] / n[root], least[root]);
	}
}

/*
 * What the game draws under a solid (backgrounds 2 and 3 as solids, drawn over the ground's enemies) and
 * that is mostly inside it is hidden, as the game hides it under the background: the red balls SAWBLADES's
 * and IXMUCANE's launchers roll through the rock showed their tops above it and their sides at its walls.
 * Inside: where the solid has rock under the thing's footprint (its 3 x 3 grid as drawn) standing above
 * its middle. It fades out between SOLID_HIDE_FROM and SOLID_HIDE_ALL of its footprint inside: half in a
 * wall it still shows, cut by the wall as the game's background cuts it.
 */
#define SOLID_HIDE_FROM 0.5f
#define SOLID_HIDE_ALL 0.85f

// The bottom and top of a ground object's bounds (game pixels before alignment, from its translation).
static void object_span(const L3DObject *object, bool mirror, float *bottom, float *top)
{
	*bottom = 0.0f;
	*top = 2.0f;
	const LoadedModel *loaded = object->model >= 0 && object->model < m3d_model_count ? get_model(object->model) : NULL;
	if (loaded == NULL)
		return;
	const Mat4 t = object_transform(object, loaded, mirror, 0.0f);
	*bottom = INFINITY;
	*top = -INFINITY;
	for (int c = 0; c < 8; ++c)
	{
		const float p[3] = { loaded->center[0] + ((c & 1) ? loaded->half[0] : -loaded->half[0]),
		                     loaded->center[1] + ((c & 2) ? loaded->half[1] : -loaded->half[1]),
		                     loaded->center[2] + ((c & 4) ? loaded->half[2] : -loaded->half[2]) };
		const float y = t.m[1] * p[0] + t.m[5] * p[1] + t.m[9] * p[2];
		*bottom = SDL_min(*bottom, y);
		*top = SDL_max(*top, y);
	}
}

// Whether a solid has rock at the game point x, y of its plane as drawn (scrolled on by shift since the tick),
// by a tile near it, and how high (its own relief).
static bool solid_rock_at(const B3DTerrain *t, const MapAnchor *a, float shift, float x, float y, float *relief)
{
	if (!a->valid)
		return false;
	const int per_x = B3D_TILE_W / t->sample;
	const float mx = a->column * B3D_TILE_W + (x - a->x), my = a->row * B3D_TILE_H + (y - shift - a->z);
	const int sx = (int)floorf(mx / t->sample + 0.5f) + t->side_columns * per_x, sy = (int)floorf(my / t->sample + 0.5f);
	if (sy < 0 || sy >= t->height || sx < 0 || sx >= t->width)
		return false;
	const Sint8 value = t->heights[sy * t->width + sx];
	if (t->holes && value == B3D_TERRAIN_HOLE)
		return false;
	*relief = (float)value;
	return true;
}

static void hide_in_solids(const L3DFrame *frame, const float *heights, bool mirror)
{
	for (int o = 0; o < frame->object_count; ++o)
		object_shown[o] = 1.0f;
	struct
	{
		const L3DBackground *background;
		const B3DTerrain *terrain;
		float height, k, shift;  // its plane, align_scale there, its scroll since the tick
	} solids[L3D_MAX_BACKGROUNDS];
	int solid_count = 0;
	for (int i = 0; i < frame->background_count; ++i)
	{
		const L3DBackground *b = &frame->backgrounds[i];
		if (b->set < 2 || !terrain_background(frame, b) || b == lift_ground)
			continue;
		const float height = SDL_min(heights[b->layer] - TILE_BELOW_LAYER, solid_top(b->set));
		solids[solid_count].background = b;
		solids[solid_count].terrain = frame_terrains[b->set];
		solids[solid_count].height = height;
		solids[solid_count].k = align_scale(height);
		solids[solid_count].shift = background_speed[b->set & 3] * ahead;
		++solid_count;
	}
	if (solid_count == 0)
		return;
	for (int o = 0; o < frame->object_count; ++o)
	{
		const L3DObject *object = &frame->objects[o];
		float footprint[5];
		if (object->layer != L3D_GROUND_ENEMY || !object_footprint(object, mirror, footprint))
			continue;
		float bottom, top;
		object_span(object, mirror, &bottom, &top);
		float height = object_bases[o] + object->height + object_lifts[o];
		if (object->model >= 0 && !m3d_models[object->model].keep_origin)
			height = SDL_max(height, 0.3f + object_lifts[o] - bottom);  // (nothing sinks: add_object_batches)
		const float k = align_scale(height);
		const float middle = height + k * (bottom + top) / 2;
		const float x = object_x(object), y = object_y(object);
		for (int s = 0; s < solid_count; ++s)
		{
			if (solids[s].background->phase <= object->phase)
				continue;  // (drawn under it)
			// The game points of the solid's plane under its footprint as drawn: a little further from the
			// point below the camera (the solid's plane is higher, less enlarged).
			const float r = k / solids[s].k;
			int inside = 0;
			for (int j = 0; j < 3; ++j)
				for (int i = 0; i < 3; ++i)
				{
					const float gx = align.cx + (x + footprint[0] + (footprint[2] - footprint[0]) * i / 2 - align.cx) * r;
					const float gy = align.cz + (y + footprint[1] + (footprint[3] - footprint[1]) * j / 2 - align.cz) * r;
					MapAnchor anchor;
					float relief;
					if (stand_anchor(solids[s].background, solids[s].shift, gx, gy, &anchor) &&
					    solid_rock_at(solids[s].terrain, &anchor, solids[s].shift, gx, gy, &relief) &&
					    solids[s].height + solids[s].k * relief > middle)
						++inside;
				}
			const float share = inside / 9.0f;
			const float t = SDL_clamp((share - SOLID_HIDE_FROM) / (SOLID_HIDE_ALL - SOLID_HIDE_FROM), 0.0f, 1.0f);
			object_shown[o] = SDL_min(object_shown[o], 1.0f - t * t * (3 - 2 * t));
		}
	}
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

// A terrain row's mesh; for a solid (lid not NULL) also its top alone, without its walls, in *lid.
static BTBHGPUCustomMesh *build_terrain_row(const B3DTerrain *t, int set, int map_row, float hole_depth,
                                            BTBHGPUCustomMesh **lid)
{
	const int ring_rows = terrain_ring_rows();
	const int per_x = B3D_TILE_W / t->sample, per_y = B3D_TILE_H / t->sample;  // samples a tile
	const int columns = (t->width - 1) / per_x;
	const int vertices_per_tile = (per_x + 1) * (per_y + 1);
	const int max_vertices = columns * vertices_per_tile;
	static V3DVertex *vertices = NULL;
	static Uint32 *indices = NULL, *lid_indices = NULL;
	static int capacity = 0;
	if (capacity < max_vertices)
	{
		free(vertices);
		free(indices);
		free(lid_indices);
		vertices = malloc(sizeof(V3DVertex) * (size_t)max_vertices);
		indices = malloc(sizeof(Uint32) * (size_t)columns * per_x * per_y * 6);
		lid_indices = malloc(sizeof(Uint32) * (size_t)columns * per_x * per_y * 6);
		capacity = vertices != NULL && indices != NULL && lid_indices != NULL ? max_vertices : 0;
		if (capacity == 0)
			return NULL;
	}

	const float length = sqrtf(sun_direction[0] * sun_direction[0] + sun_direction[1] * sun_direction[1] +
	                           sun_direction[2] * sun_direction[2]);
	const float light[3] = { -sun_direction[0] / length, -sun_direction[1] / length, -sun_direction[2] / length };
	const float up = SDL_max(light[1], 0.0f);
	int vc = 0, ic = 0, lc = 0;
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
				v->uv[1] = ((map_row % ring_rows) * B3D_TILE_H + py) / (float)(ring_rows * B3D_TILE_H);
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
				if (!ha && !hb && !he)  // (the top: no corner in a hole)
				{
					lid_indices[lc++] = a;
					lid_indices[lc++] = b;
					lid_indices[lc++] = e;
				}
				if (!ha && !he && !hd)
				{
					lid_indices[lc++] = a;
					lid_indices[lc++] = e;
					lid_indices[lc++] = d;
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
	if (lid != NULL)
		*lid = mesh != NULL && lc > 0 ? btbh_gpu_window_custom_mesh_create(window, vertices, (uint32_t)(vc * sizeof(V3DVertex)),
		                                                                    (uint32_t)vc, lid_indices, (uint32_t)lc, &report)
		                              : NULL;
	return mesh;
}

// A terrain row's mesh (and a solid's (backgrounds 2 and 3) top alone in *lid, if asked: NULL without one).
static BTBHGPUCustomMesh *terrain_row_mesh(const B3DTerrain *t, int set, int map_row, float hole_depth,
                                           BTBHGPUCustomMesh **lid)
{
	++terrain_clock;
	int slot = 0;
	for (int i = 0; i < TERRAIN_ROWS_CACHED; ++i)
	{
		if (terrain_rows[i].generation == b3d_map_generation + 1 && terrain_rows[i].set == set &&
		    terrain_rows[i].map_row == map_row && terrain_rows[i].hole_depth == hole_depth)
		{
			terrain_rows[i].used = terrain_clock;
			if (lid != NULL)
				*lid = terrain_rows[i].lid;
			return terrain_rows[i].mesh;
		}
		const bool stale = terrain_rows[i].generation != b3d_map_generation + 1;
		const bool slot_stale = terrain_rows[slot].generation != b3d_map_generation + 1;
		if ((stale && !slot_stale) || (stale == slot_stale && terrain_rows[i].used < terrain_rows[slot].used))
			slot = i;
	}
	if (terrain_rows[slot].mesh != NULL)
		btbh_gpu_custom_mesh_destroy(terrain_rows[slot].mesh);
	if (terrain_rows[slot].lid != NULL)
		btbh_gpu_custom_mesh_destroy(terrain_rows[slot].lid);
	terrain_rows[slot].lid = NULL;
	terrain_rows[slot].mesh = build_terrain_row(t, set, map_row, hole_depth, set > 1 ? &terrain_rows[slot].lid : NULL);
	terrain_rows[slot].set = set;
	terrain_rows[slot].map_row = map_row;
	terrain_rows[slot].hole_depth = hole_depth;
	terrain_rows[slot].generation = b3d_map_generation + 1;
	terrain_rows[slot].used = terrain_clock;
	if (lid != NULL)
		*lid = terrain_rows[slot].lid;
	return terrain_rows[slot].mesh;
}

/* --- Solids over the ground (add_background_batches) ---------------------------------------- */

// The stencil value of the solids' tops.
#define SOLID_STENCIL 1

// A batch not drawn where a solid's top has been (the ground and its plants).
static void not_on_solids(BTBHGPUSceneGeometryBatch *b)
{
	b->stencil_reference = SOLID_STENCIL;
	b->stencil_compare = BTBH_GPU_SCENE_DEPTH_NOT_EQUAL;
	b->stencil_pass = BTBH_GPU_SCENE_STENCIL_KEEP;
}

// A solid's row where it is drawn, for finding what of the ground it covers.
typedef struct
{
	const B3DTerrain *t;
	float x, z;      // the row as drawn on its plane
	float inv_k;     // 1 / how much larger its plane is drawn (align_scale)
	float z0, z1;    // the world's z it covers
	int map_row, per_y;
} SolidPlace;

static SolidPlace solid_places[192];
static int solid_place_count = 0;

static void note_solid_place(SolidPlace *p, const B3DTerrain *t, float x, float z, float height, int map_row)
{
	const float k = align_scale(height);
	p->t = t;
	p->x = x;
	p->z = z;
	p->inv_k = 1.0f / k;
	p->z0 = align.cz + (z - align.cz) * k;
	p->z1 = align.cz + (z + B3D_TILE_H - align.cz) * k;
	p->map_row = map_row;
	p->per_y = B3D_TILE_H / t->sample;
}

// Whether a world point lies under a solid's top now.
static bool under_solid(float wx, float wz)
{
	for (int i = 0; i < solid_place_count; ++i)
	{
		const SolidPlace *p = &solid_places[i];
		if (wz < p->z0 || wz > p->z1)
			continue;
		const float gx = align.cx + (wx - align.cx) * p->inv_k - p->x, gz = align.cz + (wz - align.cz) * p->inv_k - p->z;
		const int sx = (int)lroundf(gx / p->t->sample), j = (int)lroundf(gz / p->t->sample);
		const int sy = p->map_row * p->per_y + j;
		if (sx < 0 || sx >= p->t->width || j < 0 || j > p->per_y || sy < 0 || sy >= p->t->height)
			continue;
		if (!(p->t->holes && p->t->heights[sy * p->t->width + sx] == B3D_TERRAIN_HOLE))
			return true;
	}
	return false;
}

/* --- Background maps ----------------------------------------------------------------------- */

// HD textures: three mip levels (down to the tiles' own size, where their cells' borders are a
// pixel wide as in tile_atlas), blended between when filtered.
#define HD_MIP_LEVELS 3
static BTBHGPUTextureFilter hd_filter(void)
{
	return map_filter() == BTBH_GPU_TEXTURE_FILTER_LINEAR ? BTBH_GPU_TEXTURE_FILTER_TRILINEAR : map_filter();
}

// The HD atlas texture at the scale of the maps' HD tiles, and their pixels; before anything of the
// frame uses the texture (it is made again when the scale changes).
static void prepare_tile_atlas(void)
{
	const int scale = b3d_hd_scale();
	if (scale != hd_scale && window != NULL)
	{
		if (tile_atlas_hd != NULL)
			btbh_gpu_texture_destroy(tile_atlas_hd);
		tile_atlas_hd = NULL;
		if (scale > 1)
		{
			const int w = B3D_ATLAS_W * scale, h = B3D_ATLAS_H * TILE_PAGES * scale;
			Uint32 *zeroes = calloc((size_t)w * h, sizeof(Uint32));
			BTBHGPUTextureReport report;
			if (zeroes != NULL)
				tile_atlas_hd = btbh_gpu_window_texture_create_rgba8_ex(window, (const uint8_t *)zeroes, w, h, HD_MIP_LEVELS,
					hd_filter(), BTBH_GPU_TEXTURE_WRAP_CLAMP, BTBH_GPU_TEXTURE_COLOR_SPACE_SRGB, &report);
			free(zeroes);
			if (tile_atlas_hd == NULL)
				fprintf(stderr, "warning: HD tile atlas: %s\n", zeroes == NULL ? "out of memory" : report.message);
		}
		hd_scale = scale;
		hd_generation = 0;
		for (int p = 0; p < TILE_PAGES; ++p)
			tile_pages[p].hd = false;
	}
	if (hd_scale > 1 && hd_generation != b3d_map_generation + 1)
	{
		const size_t n = (size_t)B3D_ATLAS_W * B3D_ATLAS_H * hd_scale * hd_scale;
		if (hd_capacity < n)
		{
			free(hd_indices);
			free(hd_opaque);
			free(hd_ground);
			free(hd_rgba);
			hd_indices = malloc(n);
			hd_opaque = malloc(n);
			hd_ground = malloc(n);
			hd_rgba = malloc(n * sizeof(Uint32));
			hd_capacity = hd_indices && hd_opaque && hd_ground && hd_rgba ? n : 0;
		}
		if (hd_capacity >= n)
		{
			b3d_build_atlas_hd(hd_indices, hd_opaque, hd_ground);
			hd_generation = b3d_map_generation + 1;
			for (int p = 0; p < TILE_PAGES; ++p)
				tile_pages[p].hd = false;
		}
	}
}

static bool hd_ready(void)
{
	return hd_scale > 1 && tile_atlas_hd != NULL && hd_generation == b3d_map_generation + 1;
}

// Colours tile_atlas_hd's page as the page of tile_atlas is, if the colours have held and the
// frame's budget allows.
static void hd_tile_page(int page, const Uint32 colors[256], bool ground_zero)
{
	if (tile_pages[page].hd || !hd_ready() || colors_stable < HD_STABLE_FRAMES || hd_budget < HD_ROWS_PER_FRAME)
		return;
	hd_budget = 0;
	const int w = B3D_ATLAS_W * hd_scale, h = B3D_ATLAS_H * hd_scale;
	for (size_t i = 0; i < (size_t)w * h; ++i)
		hd_rgba[i] = hd_opaque[i] || (ground_zero && hd_ground[i]) ? colors[hd_indices[i]] : 0;
	bleed_into_clear(hd_rgba, w, 0, h);
	btbh_gpu_texture_update_rgba8(tile_atlas_hd, (const uint8_t *)hd_rgba, 0, (Uint32)(page * h), (Uint32)w, (Uint32)h);
	tile_pages[page].hd = true;
}

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
			hd_tile_page(p, colors, ground_zero);
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
	// Water: the water pixels of tiles with water (b3d_tile_has_water), with their cells' borders.
	{
		static const Uint8 water_rgba[4] = { 0, 0, 255, 255 };
		Uint32 water;
		memcpy(&water, water_rgba, 4);
		memset(tile_rgba, 0, sizeof(Uint32) * B3D_ATLAS_W * B3D_ATLAS_H);
		for (int set = 1; set <= B3D_SETS; ++set)
			for (int t = 0; t < B3D_TILES_PER_SET; ++t)
			{
				if (!b3d_tile_has_water(set, t))
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
	tile_pages[page].hd = false;
	hd_tile_page(page, colors, ground_zero);
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
		x0 = l3d_field_x() + l3d_field_w() / 2 - COMPOSED_SIZE / 2;
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
		b->ssao_mode = BTBH_GPU_SCENE_SSAO_RECEIVE_ONLY;
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
	BTBHGPUTexture *texture, *water;  // the rows at the tiles' size
	BTBHGPUTexture *hd;           // and with the HD tiles (b3d_hd_scale() times larger), or NULL
	int width;                    // pixels at the tiles' size
	int scale;                    // hd's
	int ring_rows;                // terrain_ring_rows()
	int rows[TERRAIN_RING_ROWS];  // the map row each slot holds, or -1
	bool hd_rows[TERRAIN_RING_ROWS];  // hd holds the slot's row
	bool stale[TERRAIN_RING_ROWS], hd_stale[TERRAIN_RING_ROWS];  // in earlier colours than the ring's (texture, hd)
	unsigned int generation;      // b3d_map_generation + 1 that the slots are of
	Uint32 colors_hash;
	bool ground_zero;
} TerrainRing;

static TerrainRing terrain_rings[B3D_SETS + 1];

static struct
{
	unsigned int generation;  // b3d_map_generation + 1 the meshes were made for
	int tint;                 // and the tint they took (make_plant_meshes)
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
	const int scale = b3d_hd_scale(), ring_rows = terrain_ring_rows();
	if (ring->texture == NULL || ring->width != width || ring->scale != scale || ring->ring_rows != ring_rows)
	{
		if (ring->texture != NULL)
			btbh_gpu_texture_destroy(ring->texture);
		if (ring->hd != NULL)
			btbh_gpu_texture_destroy(ring->hd);
		if (ring->water != NULL)
			btbh_gpu_texture_destroy(ring->water);
		BTBHGPUTextureReport report;
		const int height = ring_rows * B3D_TILE_H;
		Uint32 *zeroes = calloc((size_t)width * scale * height * scale, sizeof(Uint32));
		ring->texture = zeroes == NULL ? NULL : btbh_gpu_window_texture_create_rgba8_ex(window, (const uint8_t *)zeroes, width,
			height, 0, map_filter(), BTBH_GPU_TEXTURE_WRAP_REPEAT, BTBH_GPU_TEXTURE_COLOR_SPACE_SRGB, &report);
		ring->hd = zeroes == NULL || scale <= 1 ? NULL : btbh_gpu_window_texture_create_rgba8_ex(window, (const uint8_t *)zeroes,
			width * scale, height * scale, 0, map_filter(), BTBH_GPU_TEXTURE_WRAP_REPEAT, BTBH_GPU_TEXTURE_COLOR_SPACE_SRGB,
			&report);  // (no mip levels: they are made again for all of it at every row)
		ring->water = zeroes == NULL || set != 1 ? NULL : btbh_gpu_window_texture_create_rgba8_ex(window, (const uint8_t *)zeroes,
			width, height, 0, BTBH_GPU_TEXTURE_FILTER_NEAREST, BTBH_GPU_TEXTURE_WRAP_REPEAT,
			BTBH_GPU_TEXTURE_COLOR_SPACE_LINEAR, &report);
		free(zeroes);
		if (ring->texture == NULL)
			fprintf(stderr, "warning: terrain texture: %s\n", report.message);
		ring->width = width;
		ring->scale = scale;
		ring->ring_rows = ring_rows;
		ring->generation = 0;
	}
	const Uint32 hash = hash_colors(colors);
	if (ring->generation != b3d_map_generation + 1)
	{
		for (int i = 0; i < ring->ring_rows; ++i)
		{
			ring->rows[i] = -1;
			ring->hd_rows[i] = false;
		}
		ring->generation = b3d_map_generation + 1;
		ring->colors_hash = hash;
		ring->ground_zero = ground_zero;
	}
	if (ring->colors_hash != hash || ring->ground_zero != ground_zero)
	{
		// (a row's HD one shows in the earlier colours till it is coloured anew, a few a frame: emptied, the rows
		// showed at the tiles' size for a moment whenever a filter's hue came or went, the Flare's at its start and end)
		for (int i = 0; i < ring->ring_rows; ++i)
			ring->stale[i] = ring->hd_stale[i] = true;
		ring->colors_hash = hash;
		ring->ground_zero = ground_zero;
	}
	return ring->texture != NULL ? ring : NULL;
}

// Puts a map row into its slot of the ring, unless it is there already.
// A map pixel's palette index (the exported map's pixels, the generated columns included), or -1
// where it is clear.
static int map_pixel(const B3DTerrain *t, int set, int x, int y)
{
	if (x < 0 || y < 0)
		return -1;
	bool flipped;
	const int cell = b3d_map_cell(set, y / B3D_TILE_H, x / B3D_TILE_W - t->side_columns, &flipped);
	if (cell < 0)
		return -1;
	int ox, oy;
	b3d_cell_origin(cell, &ox, &oy);
	const int tx = x % B3D_TILE_W;
	const int i = (oy + y % B3D_TILE_H) * B3D_ATLAS_W + ox + (flipped ? B3D_TILE_W - 1 - tx : tx);
	return tile_opaque[i] ? tile_indices[i] : -1;
}

// The objects of ground enemies painted into the map's tiles under their models (b3d_erasures):
// replaced in a row of the map's texture by the map's own ground further away.
static void erase_painted_enemies(Uint32 *rgba, int width, const B3DTerrain *t, int set, int map_row,
                                  const Uint32 colors[256])
{
	const B3DErasures *erasures = b3d_erasures(set);
	if (erasures == NULL)
		return;
	const int top = map_row * B3D_TILE_H, bottom = top + B3D_TILE_H;
	for (int i = 0; i < erasures->count; ++i)
	{
		const B3DErasure *e = &erasures->erasures[i];
		if (e->y >= bottom)
			break;  // in order of y
		if (e->y + e->h <= top)
			continue;
		for (int y = SDL_max(e->y, top); y < SDL_min(e->y + e->h, bottom); ++y)
			for (int x = e->x; x < SDL_min(e->x + e->w, width); ++x)
			{
				if (!e->mask[(y - e->y) * e->w + (x - e->x)])
					continue;
				const int index = map_pixel(t, set, x + e->dx, y + e->dy);
				if (index >= 0)
					rgba[(y - top) * width + x] = colors[index];
			}
	}
}

// map_pixel among the HD tiles (hd_indices): x, y in pixels of the HD map.
static int map_pixel_hd(const B3DTerrain *t, int set, int x, int y, int scale)
{
	const int tw = B3D_TILE_W * scale, th = B3D_TILE_H * scale;
	if (x < 0 || y < 0)
		return -1;
	bool flipped;
	const int cell = b3d_map_cell(set, y / th, x / tw - t->side_columns, &flipped);
	if (cell < 0)
		return -1;
	int ox, oy;
	b3d_cell_origin(cell, &ox, &oy);
	const int tx = x % tw;
	const int i = (oy * scale + y % th) * (B3D_ATLAS_W * scale) + ox * scale + (flipped ? tw - 1 - tx : tx);
	return hd_opaque[i] ? hd_indices[i] : -1;
}

// erase_painted_enemies in a row of HD tiles: each erased pixel's block from the same place of the
// tile it is taken from (the erasures move by whole tiles).
static void erase_painted_enemies_hd(Uint32 *rgba, int width, const B3DTerrain *t, int set, int map_row,
                                     const Uint32 colors[256], int scale)
{
	const B3DErasures *erasures = b3d_erasures(set);
	if (erasures == NULL)
		return;
	const int top = map_row * B3D_TILE_H, bottom = top + B3D_TILE_H;
	for (int i = 0; i < erasures->count; ++i)
	{
		const B3DErasure *e = &erasures->erasures[i];
		if (e->y >= bottom)
			break;  // in order of y
		if (e->y + e->h <= top)
			continue;
		for (int y = SDL_max(e->y, top); y < SDL_min(e->y + e->h, bottom); ++y)
			for (int x = e->x; x < SDL_min(e->x + e->w, width / scale); ++x)
			{
				if (!e->mask[(y - e->y) * e->w + (x - e->x)])
					continue;
				for (int sy = 0; sy < scale; ++sy)
					for (int sx = 0; sx < scale; ++sx)
					{
						const int index = map_pixel_hd(t, set, (x + e->dx) * scale + sx, (y + e->dy) * scale + sy, scale);
						if (index >= 0)
							rgba[((y - top) * scale + sy) * width + x * scale + sx] = colors[index];
					}
			}
	}
}

static void terrain_ring_row_made(TerrainRing *ring, const B3DTerrain *t, int set, int map_row, const Uint32 colors[256]);

static void terrain_ring_row_hd(TerrainRing *ring, const B3DTerrain *t, int set, int map_row, const Uint32 colors[256]);

// Puts a map row into its slot of the ring (at the tiles' size), unless it is there already; and
// with the HD tiles when the colours have held and the frame's budget allows.
static void terrain_ring_row(TerrainRing *ring, const B3DTerrain *t, int set, int map_row, const Uint32 colors[256])
{
	const int slot = map_row % ring->ring_rows;
	if (map_row < 0)
		return;
	const Uint64 start = SDL_GetPerformanceCounter();
	if (ring->rows[slot] != map_row || ring->stale[slot])
	{
		if (ring->rows[slot] != map_row)
			ring->hd_rows[slot] = false;
		terrain_ring_row_made(ring, t, set, map_row, colors);
		ring->stale[slot] = false;
		++profile_rows;
	}
	if (ring->hd != NULL && (!ring->hd_rows[slot] || ring->hd_stale[slot]) && hd_ready() &&
	    colors_stable >= HD_STABLE_FRAMES && hd_budget > 0)
	{
		terrain_ring_row_hd(ring, t, set, map_row, colors);
		ring->hd_rows[slot] = true;
		ring->hd_stale[slot] = false;
		--hd_budget;
	}
	profile_rows_ticks += SDL_GetPerformanceCounter() - start;
}

// Whether a row can be drawn with the HD tiles: they hold it and the row below (its bottom edge
// filters into it).
static bool terrain_row_hd(const TerrainRing *ring, int map_row)
{
	if (ring == NULL || ring->hd == NULL)
		return false;
	for (int r = map_row; r <= map_row + 1; ++r)
	{
		const int slot = r % ring->ring_rows;
		if (ring->rows[slot] != r || !ring->hd_rows[slot])
			return false;
	}
	return true;
}

static void terrain_ring_row_made(TerrainRing *ring, const B3DTerrain *t, int set, int map_row, const Uint32 colors[256])
{
	const int slot = map_row % ring->ring_rows;
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
		const bool water_tile = cell >= 0 && ring->water != NULL && b3d_tile_has_water(set, tile);
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
	erase_painted_enemies(rgba, ring->width, t, set, map_row, colors);
	bleed_into_clear(rgba, ring->width, 0, B3D_TILE_H);
	btbh_gpu_texture_update_rgba8(ring->texture, (const uint8_t *)rgba, 0, (Uint32)(slot * B3D_TILE_H), (Uint32)ring->width,
	                              B3D_TILE_H);
	if (ring->water != NULL)
		btbh_gpu_texture_update_rgba8(ring->water, (const uint8_t *)water, 0, (Uint32)(slot * B3D_TILE_H), (Uint32)ring->width,
		                              B3D_TILE_H);
}

// The row with the HD tiles (hd_indices), into hd's slot: as terrain_ring_row_made at the HD scale.
static void terrain_ring_row_hd(TerrainRing *ring, const B3DTerrain *t, int set, int map_row, const Uint32 colors[256])
{
	static Uint32 *hd = NULL;
	static size_t capacity = 0;
	const int scale = ring->scale, slot = map_row % ring->ring_rows;
	const int w = ring->width * scale, h = B3D_TILE_H * scale, tw = B3D_TILE_W * scale;
	if (capacity < (size_t)w * h)
	{
		free(hd);
		hd = malloc((size_t)w * h * sizeof(Uint32));
		capacity = hd != NULL ? (size_t)w * h : 0;
		if (hd == NULL)
			return;
	}
	const int columns = ring->width / B3D_TILE_W;
	for (int c = 0; c < columns; ++c)
	{
		bool flipped;
		const int cell = b3d_map_cell(set, map_row, c - t->side_columns, &flipped);
		int ox = 0, oy = 0;
		if (cell >= 0)
			b3d_cell_origin(cell, &ox, &oy);
		for (int y = 0; y < h; ++y)
		{
			Uint32 *out = &hd[y * w + c * tw];
			if (cell < 0)
			{
				memset(out, 0, (size_t)tw * sizeof(Uint32));
				continue;
			}
			const size_t row = (size_t)(oy * scale + y) * (B3D_ATLAS_W * scale) + (size_t)ox * scale;
			for (int x = 0; x < tw; ++x)
			{
				const size_t i = row + (flipped ? tw - 1 - x : x);
				out[x] = hd_opaque[i] || (ring->ground_zero && hd_ground[i]) ? colors[hd_indices[i]] : 0;
			}
		}
	}
	erase_painted_enemies_hd(hd, w, t, set, map_row, colors, scale);
	bleed_into_clear(hd, w, 0, h);
	btbh_gpu_texture_update_rgba8(ring->hd, (const uint8_t *)hd, 0, (Uint32)(slot * h), (Uint32)w, (Uint32)h);
}

// Whether a ground object has moved over the map since it was first seen (by its key): standing ones
// don't (the vegetation tool keeps the plants off their footprints), objects without a key count as moving.
static Uint32 plants_frame = 0;

static bool moves_on_map(Uint32 key, int mx, int my)
{
	enum { SLOTS = 1024, FORGET = 600 };
	static struct
	{
		Uint32 key, seen;
		int x, y;
		bool moved;
	} first[SLOTS];
	if (key == 0)
		return true;
	unsigned int at = (key * 2654435761u) % SLOTS;
	for (int probe = 0; probe < 16; ++probe, at = (at + 1) % SLOTS)
	{
		if (first[at].key == key && plants_frame - first[at].seen < FORGET)
		{
			first[at].seen = plants_frame;
			first[at].moved |= abs(first[at].x - mx) > 2 || abs(first[at].y - my) > 2;
			return first[at].moved;
		}
		if (first[at].key == 0 || plants_frame - first[at].seen >= FORGET)
		{
			first[at].key = key;
			first[at].seen = plants_frame;
			first[at].x = mx;
			first[at].y = my;
			first[at].moved = false;
			return false;
		}
	}
	return true;
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

// The plants in their colours, or tinted as the ground is (tint_hue >= 0: b3d_tint_overlay; TIME WAR's
// palms under its blue): the hue's palette colour at the brightness halfway between theirs and the tint's.
static void make_plant_meshes(const B3DVegetation *veg, int tint_hue, int tint_brightness, const Uint32 colors[256])
{
	const int tint = tint_hue < 0 ? -1 : tint_hue * 16 + tint_brightness;
	if (plant_meshes.generation == b3d_map_generation + 1 && plant_meshes.tint == tint)
		return;
	plant_meshes.generation = b3d_map_generation + 1;
	plant_meshes.tint = tint;
	B3DVegetation tinted = *veg;
	for (int c = 0; c < B3D_PLANT_KINDS * 2 && tint_hue >= 0; ++c)
	{
		const Uint8 *rgb = veg->colors[c];
		const int brightness = (int)((0.299f * rgb[0] + 0.587f * rgb[1] + 0.114f * rgb[2]) / 255.0f * 15.0f + 0.5f);
		memcpy(tinted.colors[c], &colors[(tint_hue << 4) | ((brightness + tint_brightness) / 2)], 3);
	}
	veg = &tinted;
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
	cloud_ground_top = -1e9f;
	cloud_solid_count = 0;
	if (clip_log_on())
		clip_surface_count = 0;
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
		bool hd;     // with the HD tiles (terrain_row_hd)
		bool solid;  // a solid's (background 2 or 3)
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

	// A blended background opaque all over tints a ground of terrain instead (b3d_tint_overlay).
	int tint_set = 0, tint_brightness = 0;
	Uint8 tint_hue = 0;
	for (int i = 0; i < frame->background_count && b3d_terrain_ground; ++i)
	{
		const L3DBackground *b = &frame->backgrounds[i];
		if (b->set > 1 && b->blend && !water_overlay(b) && !cloud_background(b, composed[i]) &&
		    b3d_tint_overlay(b->set, &tint_hue, &tint_brightness))
			tint_set = b->set;
	}

	for (int i = 0; i < frame->background_count; ++i)
	{
		const L3DBackground *background = &frame->backgrounds[i];
		if (only != NULL && SDL_strchr(only, '0' + background->set) == NULL)
			continue;
		// (An empty map shows nothing; blended, its blank tiles would darken all under it.)
		if (b3d_map_empty(background->set))
			continue;
		if (water_overlay(background) || background->set == tint_set)
			continue;
		// A composed (filtered) background covers only so much; its tiles, in the filters' colours,
		// go on beyond it, a little below so that the composed image wins where it is.
		float height = heights[background->layer] - TILE_BELOW_LAYER - (composed[i] ? 0.1f : 0.0f);
		const bool solid = background->set > 1 && terrain_background(frame, background) && background != lift_ground;
		if (solid)
			height = SDL_min(height, solid_top(background->set));
		note_cloud_ground(frame, background, height, solid, relief_ground && background->set == 1);  // (the clouds stay above)
		const float shift = background_speed[background->set & 3] * ahead;
		float rect[4];
		plane_footprint(camera, height, rect);
		// Ground of terrain below its plane (sunken ground, chasms) shows further up the level at the
		// window's top edge. Its rows are drawn aligned at the plane's height (aligned(): x, y and z
		// scaled about the plane), so its lowest ground is that much lower in the world.
		const B3DTerrain *ground = background == lift_ground ? lift_terrain : NULL;
		const float deepest = ground == NULL ? 0.0f
		                                     : SDL_max(ground->hole_count > 0 ? TERRAIN_HOLE_DEPTH : 0.0f, (float)-ground->lowest);
		if (deepest > 0)
		{
			const float k = align_scale(height);
			float low[4];
			plane_footprint_world(camera, height - deepest * k, align.cz + (-BACKGROUND_AHEAD - align.cz) * k, low);
			if (low[0] <= low[2])
			{
				low[0] = align.cx + (low[0] - align.cx) / k;
				low[2] = align.cx + (low[2] - align.cx) / k;
				low[1] = align.cz + (low[1] - align.cz) / k;
				low[3] = align.cz + (low[3] - align.cz) / k;
				if (rect[0] > rect[2])
					memcpy(rect, low, sizeof(low));
				else
					for (int c = 0; c < 4; ++c)
						rect[c] = c < 2 ? SDL_min(rect[c], low[c]) : SDL_max(rect[c], low[c]);
			}
		}
		if (rect[0] > rect[2])
			continue;
		rect[1] -= shift;  // what has scrolled into view
		rect[3] -= shift;
		if (clip_log_on() && clip_surface_count < L3D_MAX_BACKGROUNDS)  // (what is drawn where, for log_clipping)
		{
			const bool terrain = terrain_background(frame, background);
			clip_surfaces[clip_surface_count++] = (ClipSurface){
				background, terrain ? frame_terrains[background->set] : NULL, height, terrain_hole_depth(solid, height), shift,
				cloud_background(background, composed[i]) };
		}

		b3d_tile_is_cloud(background->set, 0);  // classifies the set's tiles (logged with TYR3D_LOG_CLOUDS)
		// Tiles take the colours the game gives them through blending and the level's filters.
		Uint8 remap[256];
		Uint32 page_colors[256];
		if (solid)
			b3d_effect_remap(background, remap);
		else
			b3d_tile_remap(background, remap);
		for (int c = 0; c < 256; ++c)
			page_colors[c] = background->set == 1 && tint_set != 0
			                     ? colors[(tint_hue << 4) | (((remap[c] & 0x0f) + tint_brightness) / 2)]
			                     : colors[remap[c]];
		// The game clears the screen to colour 0 under background 1; a filter that recolours it
		// shows there too (lava, ice), and so does a ground of terrain over stars with no holes for
		// them (no black space, only dark specks: MINERS's lava), black as the empty space it is.
		const bool ground_zero = background->set == 1 && (remap[0] != 0 || stars_covered() || tint_set != 0);
		if (background->set == 1 && remap[0] == 0 && stars_covered() && tint_set == 0)
		{
			static const Uint8 black[4] = { 0, 0, 0, 255 };
			memcpy(&page_colors[0], black, 4);
		}
		const int page = tile_page(page_colors, ground_zero);

		const int first = tile_count;
		tile_count += b3d_collect_tiles(background, ground_zero, rect[0], rect[1], rect[2], rect[3],
		                                tiles + tile_count, capacity - tile_count);
		// Cloud tiles are clouds (add_cloud_batches), taken over the view and a margin round it.
		if (cloud_background(background, composed[i]))
		{
			memcpy(cloud_page_colors[background->set], page_colors, sizeof(page_colors));
			int kept = first;
			for (int t = first; t < tile_count; ++t)
			{
				const int tile = tiles[t].cell % B3D_TILES_PER_SET;
				if (tiles[t].cell < B3D_CELLS && tiles[t].cell / B3D_TILES_PER_SET + 1 == background->set &&
				    b3d_tile_is_cloud(background->set, tile))
					continue;
				tiles[kept++] = tiles[t];
			}
			tile_count = kept;
			if (!low_background(background))
				collect_cloud_tiles(background, rect, cloud_base(heights, background->layer) - (heights[0] + 0.15f) + 30.0f);
		}
		// Terrain: the map's rows are meshes (the tiles beyond its columns stay tiles).
		if (terrain_background(frame, background))
		{
			const B3DTerrain *terrain = frame_terrains[background->set];
			TerrainRing *ring = terrain_ring(terrain, background->set, page_colors, ground_zero);
			const float hole_depth = terrain_hole_depth(solid, height);
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
					page, brightness, terrain_row_hd(ring, tiles[t].map_row), solid };
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
		float *instance = instances + key_next[tile_key[t]]++ * 24;
		write_instance(instance, &transform, brightness);
		// TYR3D_DEBUG_TILES: flat tiles of backgrounds 2 (magenta) and 3 (cyan) show up.
		static int debug_tiles = -1;
		if (debug_tiles < 0)
			debug_tiles = SDL_getenv("TYR3D_DEBUG_TILES") != NULL;
		if (debug_tiles && tile->cell < B3D_CELLS && tile->cell / B3D_TILES_PER_SET + 1 >= 2)
			instance[tile->cell / B3D_TILES_PER_SET + 1 == 2 ? 17 : 16] = 0;
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
		const bool hd = tile_pages[page].hd && hd_ready();
		b->albedo_texture = hd ? tile_atlas_hd : tile_atlas;
		dim_tiles(b);
		const float inset = tile_inset() / (hd ? hd_scale : 1);  // (half a pixel of the atlas texture)
		b->uv_scale_x = (flipped ? -1.0f : 1.0f) * (B3D_TILE_W - 2 * inset) / B3D_ATLAS_W;
		b->uv_scale_y = (B3D_TILE_H - 2 * inset) / atlas_h;
		b->uv_offset_x = (ox + (flipped ? B3D_TILE_W - inset : inset)) / B3D_ATLAS_W;
		b->uv_offset_y = (oy + inset) / atlas_h;
		b->unlit_enabled = 1;
		b->alpha_cutoff = 0.5f;
		b->ssao_mode = relief ? BTBH_GPU_SCENE_SSAO_FULL : BTBH_GPU_SCENE_SSAO_RECEIVE_ONLY;
		set_glints(b, tile_water);
	}
	*instance_count = next;

	// The terrain's rows. (Their textures hold terrain_ring_rows() rows: more drawn at once would
	// take turns in the ring's slots every frame.)
	{
		static bool warned = false;
		for (int set = 1; set <= B3D_SETS && !warned; ++set)
		{
			int lo = 1 << 30, hi = -1;
			for (int r = 0; r < terrain_row_count; ++r)
				if (terrain_row_draws[r].set == set)
				{
					lo = SDL_min(lo, terrain_row_draws[r].map_row);
					hi = SDL_max(hi, terrain_row_draws[r].map_row + 1);  // (and the row below it)
				}
			if (hi >= lo && hi - lo + 1 > terrain_ring_rows())
			{
				fprintf(stderr, "warning: terrain: %d rows drawn at once, the ring holds %d\n", hi - lo + 1, terrain_ring_rows());
				warned = true;
			}
		}
	}
	// Solids over the ground (backgrounds 2 and 3 drawn as solids, over the ground's enemies) scroll at their
	// own speed, faster than the ground (TYRIAN's stone platforms three times as fast as its ground), so the
	// ground's raised terrain under them would stand up through their tops, and its plants with it. Their
	// tops alone (lids) are drawn first, marking their pixels (stencil 1); the ground and its plants aren't
	// drawn there (the game draws the solids over the ground); then the solids whole, walls and all, over
	// the ground as drawn (their walls go down into it). Plants under solids aren't drawn at all.
	solid_place_count = 0;
	bool lids = false;
	for (int pass = 0; pass < 2; ++pass)
		for (int r = 0; r < terrain_row_count && *instance_count < MAX_INSTANCES && *batch_count < MAX_BATCHES; ++r)
		{
			const TerrainRowDraw *row = &terrain_row_draws[r];
			if (!row->solid || frame_terrains[1] == NULL)
				continue;
			BTBHGPUCustomMesh *lid = NULL;
			if (terrain_row_mesh(frame_terrains[row->set], row->set, row->map_row, row->hole_depth, &lid) == NULL || lid == NULL)
				continue;
			if (pass == 1)  // (where they are, for the plants)
			{
				if (solid_place_count < (int)COUNTOF(solid_places))
					note_solid_place(&solid_places[solid_place_count++], frame_terrains[row->set], row->x, row->z, row->height,
					                 row->map_row);
				continue;
			}
			const Mat4 transform = mat4_translation(row->x, row->height, row->z);
			write_instance(instances + *instance_count * 24, &transform, row->brightness);
			BTBHGPUSceneGeometryBatch *b = &batches[(*batch_count)++];
			init_batch(b);
			b->kind = BTBH_GPU_SCENE_GEOMETRY_CUSTOM_MESH;
			b->custom_mesh = lid;
			b->first_instance = (*instance_count)++;
			b->instance_count = 1;
			b->albedo_texture = row->hd ? terrain_rings[row->set].hd : terrain_rings[row->set].texture;
			dim_tiles(b);
			b->unlit_enabled = 1;
			b->alpha_cutoff = 0.5f;
			b->stencil_reference = SOLID_STENCIL;
			lids = true;
		}
	for (int r = 0; r < terrain_row_count && *instance_count < MAX_INSTANCES && *batch_count < MAX_BATCHES; ++r)
	{
		const TerrainRowDraw *row = &terrain_row_draws[r];
		BTBHGPUCustomMesh *mesh = terrain_row_mesh(frame_terrains[row->set], row->set, row->map_row, row->hole_depth, NULL);
		if (mesh == NULL)
			continue;
		const Mat4 transform = mat4_translation(row->x, row->height, row->z);
		write_instance(instances + *instance_count * 24, &transform, row->brightness);
		terrain_batch[*batch_count] = true;
		BTBHGPUSceneGeometryBatch *b = &batches[(*batch_count)++];
		init_batch(b);
		b->kind = BTBH_GPU_SCENE_GEOMETRY_CUSTOM_MESH;
		b->custom_mesh = mesh;
		if (row->set == 1 && lids)
			not_on_solids(b);
		b->first_instance = (*instance_count)++;
		b->instance_count = 1;
		b->albedo_texture = row->hd ? terrain_rings[row->set].hd : terrain_rings[row->set].texture;
		dim_tiles(b);
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
	make_plant_meshes(veg, tint_set != 0 ? tint_hue : -1, tint_brightness, colors);
	const B3DTerrain *ground = frame_terrains[1];

	// No plants under ground enemies that move over the map, where they are now (the vegetation tool
	// keeps them off the models' footprints where enemies and stand-ins stand still): a circle round each,
	// in the map's pixels.
	enum { MAX_CLEARINGS = 128 };
	float clearings[MAX_CLEARINGS][3];
	int clearing_count = 0;
	++plants_frame;
	for (int o = 0; o < frame->object_count && clearing_count < MAX_CLEARINGS && lift_ground != NULL; ++o)
	{
		const L3DObject *object = &frame->objects[o];
		if (object->layer != L3D_GROUND_ENEMY || object->standin != 0)
			continue;
		int mx, my;
		if (!b3d_map_point(lift_ground, object->x, object->y, &mx, &my) || !moves_on_map(object->key, mx, my))
			continue;
		const M3DModel *model = object->model >= 0 && object->model < m3d_model_count ? &m3d_models[object->model] : NULL;
		const float radius = (model != NULL && model->size > 0 ? model->size / 2.0f : 13.0f) + 3.0f;
		clearings[clearing_count][0] = (float)mx;
		clearings[clearing_count][1] = (float)my;
		clearings[clearing_count][2] = radius * radius;
		++clearing_count;
	}

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
				bool cleared = false;
				for (int c = 0; c < clearing_count && !cleared; ++c)
				{
					const float dx = p->x - clearings[c][0], dy = p->y - clearings[c][1];
					cleared = dx * dx + dy * dy < clearings[c][2];
				}
				if (cleared)
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
				if (solid_place_count > 0 && under_solid(world.m[12], world.m[14]))
					continue;  // (it would stand up through the solid)
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
		dim_tiles(b);  // (the plants' colours are the full palette's)
		b->unlit_enabled = 1;
		// (The grass's blades, small and many, would darken it all in a grain: they take the ambient occlusion only.)
		b->ssao_mode = kind == B3D_GRASS ? BTBH_GPU_SCENE_SSAO_RECEIVE_ONLY : BTBH_GPU_SCENE_SSAO_FULL;
		if (solid_place_count > 0)
			not_on_solids(b);
	}
}

/*
 * TYR3D_LOG_CLIP=1 (dev): where raised ground or a background hides part of an enemy's model that
 * should show, or shows part the game hides. In every CLIP_LOG_EVERY of the game's frames, the first
 * shown (as captured, not moved on between ticks), and in every frame dumped: each enemy drawn as a model (not volumes or the
 * side decor) has its model's triangles placed as add_object_batches draws them (lifted, turned,
 * scaled, aligned) and rasterized as the camera sees them (clip_view_model): the points of it that
 * would show with nothing else drawn. Each of those is checked, in world space as the depth test
 * checks it, against what add_background_batches drew (clip_surfaces):
 *   terrain               the ground's terrain (background 1, or a background 2 covering it): the way
 *                         from the point to the camera passes below its surface, so it hides the point
 *   bg2-solid, bg3-solid  backgrounds 2 and 3 as solids: the same
 *   ground                background 1 drawn flat: the point is below it and its pixel hides it
 *   bg2-plane, bg3-plane  backgrounds 2 and 3 drawn flat (not their clouds), the game drawing them under
 *                         the enemy: the point is below the plane and its pixel hides it
 *   bg2-over, bg3-over    the same, the game drawing them over the enemy: the point shows above the
 *                         plane where the plane has a pixel, which in the game covers the enemy
 *   float                 a ground enemy on a ground that isn't flat (terrain, or a background 2 drawn
 *                         under the ground enemies): its lowest points the camera sees (CLIP_FLOAT_BAND
 *                         of the lowest) stand higher above the ground drawn under them than they would
 *                         above a flat ground (its lift against the ground's under them, stand_ground_at);
 *                         area: the share of those points; and its gap: how far above that ground the
 *                         worst of them is
 * (Parts of a model inside the ground that nothing shows, such as its underside, don't count.)
 * A line for each kind that reaches deeper than CLIP_LOG_MIN somewhere: the deepest, in the model's
 * game pixels (how far below the terrain the way to the camera passes, or how far the point is from
 * the plane); the height of its bounds; the share of what shows of the model that is affected that
 * deep, and of that the share where the model is inside a terrain or solid (sunk, rather than hidden
 * by raised ground in front of it); where its middle is in the window (0 to 1 across and down, to find it in a frame dump: the
 * "dump:" lines say which 3D frame a dump shows):
 *   clip: <kind> frame <3D frame> layer <layer> sheet <sheet> sprite <first sprite> model <name>
 *         at <x>,<y> depth <pixels> of <pixels> area <percent> inside <percent> screen <x>,<y> [gap <pixels>]
 * TYR3D_LOG_CLIP=2 also prints where the deepest point of each is:
 *   clip-cell: <kind> point <world x,y,z> (<x>,<z> from the middle, game pixels) of <cells seen>,
 *              <cells affected> deep, base <the model's translation height>, lift <compute_object_lifts'>
 *              (the ground drawn under its middle <stand_ground_at>, the terrain stored at its position
 *              <terrain_lift>)
 */
#define CLIP_LOG_EVERY 10
#define CLIP_LOG_MIN 2.0f
#define CLIP_FLOAT_BAND 1.5f  // the lowest points seen of a model: this far above its lowest (game pixels)
#define CLIP_GRID_MAX 128   // cells across at most (larger models get larger cells)

enum { CLIP_TERRAIN, CLIP_BG2_SOLID, CLIP_BG3_SOLID, CLIP_GROUND, CLIP_BG2_PLANE, CLIP_BG3_PLANE, CLIP_BG2_OVER, CLIP_BG3_OVER,
       CLIP_KINDS };
static const char *const clip_kind_names[CLIP_KINDS] = {
	"terrain", "bg2-solid", "bg3-solid", "ground", "bg2-plane", "bg3-plane", "bg2-over", "bg3-over"
};

// (over: a flat background the game draws over the enemy)
static int clip_kind(const ClipSurface *s, bool over)
{
	const int set = s->background->set;
	if (s->terrain != NULL)
		return set == 1 || s->background == lift_ground ? CLIP_TERRAIN : set == 2 ? CLIP_BG2_SOLID : CLIP_BG3_SOLID;
	if (over)
		return set == 3 ? CLIP_BG3_OVER : CLIP_BG2_OVER;
	return set == 1 ? CLIP_GROUND : set == 2 ? CLIP_BG2_PLANE : CLIP_BG3_PLANE;
}

// A model's triangles on the CPU, read as btbh_gpu_window_model_load reads them: every mesh node's
// triangle primitives at the node's world transform (skinned ones as they are).
typedef struct
{
	bool tried;
	int vertex_count, index_count;
	float *positions;  // x, y, z a vertex, model units
	Uint32 *indices;   // three a triangle
} ClipMesh;

static ClipMesh clip_meshes[M3D_MAX_MODELS];

static const ClipMesh *clip_mesh(int model)
{
	static unsigned int generation = 0;  // m3d_generation + 1 of the meshes read
	if (generation != m3d_generation + 1)
	{
		for (int i = 0; i < M3D_MAX_MODELS; ++i)
		{
			free(clip_meshes[i].positions);
			free(clip_meshes[i].indices);
		}
		memset(clip_meshes, 0, sizeof(clip_meshes));
		generation = m3d_generation + 1;
	}
	ClipMesh *mesh = &clip_meshes[model];
	if (mesh->tried)
		return mesh->index_count > 0 ? mesh : NULL;
	mesh->tried = true;

	cgltf_options options;
	memset(&options, 0, sizeof(options));
	cgltf_data *data = NULL;
	if (cgltf_parse_file(&options, m3d_models[model].path, &data) != cgltf_result_success ||
	    cgltf_load_buffers(&options, data, m3d_models[model].path) != cgltf_result_success)
	{
		cgltf_free(data);
		return NULL;
	}
	// Counted, then read.
	for (int pass = 0; pass < 2; ++pass)
	{
		int vertices = 0, indices = 0;
		for (cgltf_size n = 0; n < data->nodes_count; ++n)
		{
			const cgltf_node *node = &data->nodes[n];
			if (node->mesh == NULL)
				continue;
			float world[16];
			cgltf_node_transform_world(node, world);
			for (cgltf_size p = 0; p < node->mesh->primitives_count; ++p)
			{
				const cgltf_primitive *primitive = &node->mesh->primitives[p];
				const cgltf_accessor *position = NULL;
				for (cgltf_size a = 0; a < primitive->attributes_count; ++a)
					if (primitive->attributes[a].type == cgltf_attribute_type_position)
						position = primitive->attributes[a].data;
				if (primitive->type != cgltf_primitive_type_triangles || position == NULL)
					continue;
				const int count = (int)(primitive->indices != NULL ? primitive->indices->count : position->count);
				if (pass == 1)
				{
					for (cgltf_size v = 0; v < position->count; ++v)
					{
						float in[3] = { 0, 0, 0 };
						cgltf_accessor_read_float(position, v, in, 3);
						float *out = &mesh->positions[(vertices + (int)v) * 3];
						for (int k = 0; k < 3; ++k)
							out[k] = node->skin != NULL ? in[k]
							                            : world[k] * in[0] + world[4 + k] * in[1] + world[8 + k] * in[2] + world[12 + k];
					}
					for (int i = 0; i < count; ++i)
						mesh->indices[indices + i] = (Uint32)vertices +
							(Uint32)(primitive->indices != NULL ? cgltf_accessor_read_index(primitive->indices, (cgltf_size)i) : (cgltf_size)i);
				}
				vertices += (int)position->count;
				indices += count;
			}
		}
		if (pass == 0)
		{
			mesh->positions = malloc(sizeof(float) * 3 * (size_t)SDL_max(vertices, 1));
			mesh->indices = malloc(sizeof(Uint32) * (size_t)SDL_max(indices, 1));
			if (mesh->positions == NULL || mesh->indices == NULL)
				break;
		}
		else
		{
			mesh->vertex_count = vertices;
			mesh->index_count = indices / 3 * 3;
		}
	}
	cgltf_free(data);
	return mesh->index_count > 0 ? mesh : NULL;
}

// A model as drawn, as the camera sees it: rasterized into a grid of the window (window points),
// each cell keeping the nearest of its points there (its depth and world position), as the depth
// test leaves it with nothing else in the scene.
typedef struct
{
	float u0, v0, cell;  // the window position of cell 0's corner, the cells' side
	int w, h;
	float depth[CLIP_GRID_MAX * CLIP_GRID_MAX];      // clip-space w of the nearest point; INFINITY: none
	float point[CLIP_GRID_MAX * CLIP_GRID_MAX][3];   // its world position
} ClipView;

static bool clip_view_model(ClipView *g, const ClipMesh *mesh, const Mat4 *world, const float vp[16], float window_w,
                            float window_h, float cell)
{
	// The vertices placed (world x, y, z) and projected (window u, v and clip-space w).
	static float *placed = NULL;
	static int capacity = 0;
	if (capacity < mesh->vertex_count)
	{
		free(placed);
		placed = malloc(sizeof(float) * 6 * (size_t)mesh->vertex_count);
		capacity = placed != NULL ? mesh->vertex_count : 0;
		if (placed == NULL)
			return false;
	}
	const float *m = world->m;
	float u0 = INFINITY, v0 = INFINITY, u1 = -INFINITY, v1 = -INFINITY;
	for (int i = 0; i < mesh->vertex_count; ++i)
	{
		const float *p = &mesh->positions[i * 3];
		float *out = &placed[i * 6];
		for (int k = 0; k < 3; ++k)
			out[k] = m[k] * p[0] + m[4 + k] * p[1] + m[8 + k] * p[2] + m[12 + k];
		float clip[4];
		for (int r = 0; r < 4; ++r)
			clip[r] = vp[r] * out[0] + vp[4 + r] * out[1] + vp[8 + r] * out[2] + vp[12 + r];
		out[5] = clip[3];
		if (clip[3] <= 0.1f)
			continue;  // (behind the camera)
		out[3] = (clip[0] / clip[3] + 1) / 2 * window_w;
		out[4] = (1 - clip[1] / clip[3]) / 2 * window_h;
		u0 = SDL_min(u0, out[3]);
		u1 = SDL_max(u1, out[3]);
		v0 = SDL_min(v0, out[4]);
		v1 = SDL_max(v1, out[4]);
	}
	// (What the window shows of it.)
	u0 = SDL_max(u0, 0.0f);
	v0 = SDL_max(v0, 0.0f);
	u1 = SDL_min(u1, window_w);
	v1 = SDL_min(v1, window_h);
	if (!(u0 < u1 && v0 < v1))
		return false;
	g->cell = SDL_max(cell, SDL_max(u1 - u0, v1 - v0) / (CLIP_GRID_MAX - 1));
	g->u0 = u0;
	g->v0 = v0;
	g->w = SDL_min((int)((u1 - u0) / g->cell) + 1, CLIP_GRID_MAX);
	g->h = SDL_min((int)((v1 - v0) / g->cell) + 1, CLIP_GRID_MAX);
	for (int c = 0; c < g->w * g->h; ++c)
		g->depth[c] = INFINITY;
	for (int t = 0; t + 2 < mesh->index_count; t += 3)
	{
		const float *a = &placed[mesh->indices[t] * 6], *b = &placed[mesh->indices[t + 1] * 6],
		            *c = &placed[mesh->indices[t + 2] * 6];
		if (a[5] <= 0.1f || b[5] <= 0.1f || c[5] <= 0.1f)
			continue;
		const float area = (b[3] - a[3]) * (c[4] - a[4]) - (c[3] - a[3]) * (b[4] - a[4]);
		if (fabsf(area) < 1e-9f)
			continue;
		const int i0 = SDL_max((int)floorf((SDL_min(a[3], SDL_min(b[3], c[3])) - g->u0) / g->cell), 0);
		const int i1 = SDL_min((int)floorf((SDL_max(a[3], SDL_max(b[3], c[3])) - g->u0) / g->cell), g->w - 1);
		const int j0 = SDL_max((int)floorf((SDL_min(a[4], SDL_min(b[4], c[4])) - g->v0) / g->cell), 0);
		const int j1 = SDL_min((int)floorf((SDL_max(a[4], SDL_max(b[4], c[4])) - g->v0) / g->cell), g->h - 1);
		for (int j = j0; j <= j1; ++j)
			for (int i = i0; i <= i1; ++i)
			{
				const float pu = g->u0 + (i + 0.5f) * g->cell, pv = g->v0 + (j + 0.5f) * g->cell;
				const float lb = ((pu - a[3]) * (c[4] - a[4]) - (c[3] - a[3]) * (pv - a[4])) / area;
				const float lc = ((b[3] - a[3]) * (pv - a[4]) - (pu - a[3]) * (b[4] - a[4])) / area;
				const float la = 1 - lb - lc;
				if (la < -1e-4f || lb < -1e-4f || lc < -1e-4f)
					continue;
				// Perspective-correct: what varies linearly across the window is a quantity over w.
				const float inv = la / a[5] + lb / b[5] + lc / c[5];
				const float w = 1 / inv;
				const int cell_index = j * g->w + i;
				if (w >= g->depth[cell_index])
					continue;
				g->depth[cell_index] = w;
				for (int k = 0; k < 3; ++k)
					g->point[cell_index][k] = (la * a[k] / a[5] + lb * b[k] / b[5] + lc * c[k] / c[5]) * w;
			}
	}
	return true;
}

// Where a surface's map lies under the world point x, z: from the tile there, the map pixel of any
// world point near it (its plane is aligned: k times its size about the point below the camera;
// and has scrolled on by shift). False off its map.
typedef struct
{
	float k;            // the plane's align_scale
	float x, z;         // the tile's top-left corner, game screen coordinates
	int row, column;    // the tile's place in the map (map_row, map_column)
} ClipAnchor;

static bool clip_anchor(const ClipSurface *s, float x, float z, ClipAnchor *anchor)
{
	anchor->k = align_scale(s->height);
	const float gx = align.cx + (x - align.cx) / anchor->k, gy = align.cz + (z - align.cz) / anchor->k - s->shift;
	// (Above the topmost drawn row the tiles come row by row from the one above it up to the
	// point's: the point's is the one containing it.)
	B3DTile tiles[32];
	const int count = b3d_collect_tiles(s->background, true, gx, gy, gx, gy, tiles, (int)COUNTOF(tiles));
	for (int i = 0; i < count; ++i)
		if (gy >= tiles[i].z && gy < tiles[i].z + B3D_TILE_H)
		{
			anchor->x = tiles[i].x;
			anchor->z = tiles[i].z;
			anchor->row = tiles[i].map_row;
			anchor->column = tiles[i].map_column;
			return true;
		}
	return false;
}

// The world height of what a surface draws at the world point x, z (near its anchor); false where
// it draws nothing there (holes all round in its terrain, a clear pixel or a cloud of a flat one, no
// tile). *local: a terrain's own height there.
static bool clip_surface_height(const ClipSurface *s, const ClipAnchor *anchor, float x, float z, float *height,
                                float *local)
{
	const float gx = align.cx + (x - align.cx) / anchor->k, gy = align.cz + (z - align.cz) / anchor->k - s->shift;
	// Map pixels from the map's column 0 and row 0.
	const float mx = anchor->column * B3D_TILE_W + (gx - anchor->x), my = anchor->row * B3D_TILE_H + (gy - anchor->z);
	const int column = (int)floorf(mx / B3D_TILE_W), row = (int)floorf(my / B3D_TILE_H);
	bool flipped;
	const int cell = b3d_map_cell(s->background->set, row, column, &flipped);
	if (cell < 0 || cell >= B3D_CELLS)
		return false;
	if (s->terrain == NULL)
	{
		const int set = cell / B3D_TILES_PER_SET + 1, index = cell % B3D_TILES_PER_SET;
		const Uint8 *pixels = b3d_tile_pixels(set, index);
		if (pixels == NULL || (s->clouds && b3d_tile_is_cloud(set, index)))
			return false;
		const int px = SDL_clamp((int)floorf(mx - column * B3D_TILE_W), 0, B3D_TILE_W - 1);
		const int py = SDL_clamp((int)floorf(my - row * B3D_TILE_H), 0, B3D_TILE_H - 1);
		if (pixels[py * B3D_TILE_W + (flipped ? B3D_TILE_W - 1 - px : px)] == 0)
			return false;
		*height = s->height;
		*local = 0;
		return true;
	}
	// The terrain as its rows' meshes have it (add_background_batches, build_terrain_row): beyond
	// its columns the tiles are flat; holes at their walls' feet.
	const B3DTerrain *t = s->terrain;
	if (column + t->side_columns < 0 || column + t->side_columns >= (t->width - 1) / (B3D_TILE_W / t->sample))
		return false;
	const float fx = (mx + t->side_columns * B3D_TILE_W) / t->sample, fy = my / t->sample;
	const int sx = (int)floorf(fx), sy = (int)floorf(fy);
	float h[4];
	int holes = 0;
	for (int c = 0; c < 4; ++c)
	{
		const int ix = SDL_clamp(sx + (c & 1), 0, t->width - 1), iy = SDL_clamp(sy + (c >> 1), 0, t->height - 1);
		const Sint8 value = t->heights[iy * t->width + ix];
		const bool hole = t->holes && value == B3D_TERRAIN_HOLE;
		holes += hole;
		h[c] = hole ? -s->hole_depth : (float)value;
	}
	if (holes == 4)
		return false;
	const float ax = fx - sx, ay = fy - sy;
	*local = (h[0] * (1 - ax) + h[1] * ax) * (1 - ay) + (h[2] * (1 - ax) + h[3] * ax) * ay;
	*height = s->height + anchor->k * *local;
	return true;
}

// The highest a terrain or solid stands (world, a little over) round a model's bounds (world x0..x1,
// z0..z1) and on the way from them to the camera, `reach` world units towards it: what can hide any of
// the model. Sampled every couple of world units at most CLIP_TOP_SAMPLES each way.
#define CLIP_TOP_SAMPLES 12

static float clip_local_top(const ClipSurface *s, const ClipAnchor *anchor, const float *camera, float x0, float z0,
                            float x1, float z1, float reach)
{
	const float mx = (x0 + x1) / 2, mz = (z0 + z1) / 2;
	const float dx = camera[0] - mx, dz = camera[2] - mz, length = sqrtf(dx * dx + dz * dz);
	if (length > 0)
	{
		const float rx = dx / length * reach, rz = dz / length * reach;
		x0 = SDL_min(x0, x0 + rx);
		x1 = SDL_max(x1, x1 + rx);
		z0 = SDL_min(z0, z0 + rz);
		z1 = SDL_max(z1, z1 + rz);
	}
	const int nx = SDL_clamp((int)ceilf((x1 - x0) / 2.0f), 1, CLIP_TOP_SAMPLES);
	const int nz = SDL_clamp((int)ceilf((z1 - z0) / 2.0f), 1, CLIP_TOP_SAMPLES);
	float top = -INFINITY;
	for (int j = 0; j <= nz; ++j)
		for (int i = 0; i <= nx; ++i)
		{
			float height, local;
			if (clip_surface_height(s, anchor, x0 + (x1 - x0) * i / nx, z0 + (z1 - z0) * j / nz, &height, &local))
				top = SDL_max(top, height);
		}
	// (between the samples: a slope of the terrain's steepest)
	return top + 0.5f * SDL_max(x1 - x0, z1 - z0) / SDL_max(nx, nz) * 2.0f;
}

// A sheet as models.cfg names it (parse_sheet): its letter in lower case, coins, powerups, or x and
// the hex code of a sign.
static const char *clip_sheet_name(char sheet, char name[8])
{
	if (sheet == M3D_SHEET_COINS)
		return "coins";
	if (sheet == M3D_SHEET_POWERUPS)
		return "powerups";
	if (SDL_isalnum((unsigned char)sheet))
		SDL_snprintf(name, 8, "%c", SDL_tolower((unsigned char)sheet));
	else
		SDL_snprintf(name, 8, "x%02x", (unsigned char)sheet);
	return name;
}

static void log_clipping(const L3DFrame *frame)
{
	// (and every frame dumped: TYR3D_DUMP_DIR)
	static Uint32 checked = 0;  // the frame last looked at
	if (!clip_log_on() || ahead != 0 || menu.on || !shown_view.valid || l3d_frame_number == checked ||
	    (l3d_frame_number / CLIP_LOG_EVERY == checked / CLIP_LOG_EVERY && !dev_dumping_frame()))
		return;
	checked = l3d_frame_number;
	static int verbose = -1;
	if (verbose < 0)
		verbose = SDL_atoi(SDL_getenv("TYR3D_LOG_CLIP")) >= 2;

	const Camera3D *camera = &shown_view.camera;
	const float *vp = camera->view_projection.m;
	const float window_w = shown_view.window_w, window_h = shown_view.window_h;
	static ClipView view;
	bool printed = false;
	for (int o = 0; o < frame->object_count; ++o)
	{
		const L3DObject *object = &frame->objects[o];
		if (!clip_drawn[o] || object->enemy_sheet == 0 || object->model < 0 || object->model >= m3d_model_count)
			continue;
		const LoadedModel *loaded = &loaded_models[object->model];
		const float *centre = loaded->center, *half = loaded->half;
		const Mat4 world = clip_worlds[o];
		const float k = align_scale(clip_transforms[o].m[13]);  // world units to the model's game pixels

		// The model's bounds as drawn: its middle, how far they reach up and down (world).
		const float middle[3] = {
			world.m[0] * centre[0] + world.m[4] * centre[1] + world.m[8] * centre[2] + world.m[12],
			world.m[1] * centre[0] + world.m[5] * centre[1] + world.m[9] * centre[2] + world.m[13],
			world.m[2] * centre[0] + world.m[6] * centre[1] + world.m[10] * centre[2] + world.m[14],
		};
		const float reach = fabsf(world.m[1]) * half[0] + fabsf(world.m[5]) * half[1] + fabsf(world.m[9]) * half[2];

		// The surfaces that may hide some of it: a terrain whose highest point stands above its
		// bottom, a flat background the game draws under the enemy above its bottom, one it draws over
		// the enemy below its top.
		const ClipSurface *surfaces[L3D_MAX_BACKGROUNDS];
		bool over[L3D_MAX_BACKGROUNDS];
		ClipAnchor anchors[L3D_MAX_BACKGROUNDS];
		float tops[L3D_MAX_BACKGROUNDS];  // a terrain's highest round the model (clip_local_top)
		int count = 0;
		const float half_x = fabsf(world.m[0]) * half[0] + fabsf(world.m[4]) * half[1] + fabsf(world.m[8]) * half[2];
		const float half_z = fabsf(world.m[2]) * half[0] + fabsf(world.m[6]) * half[1] + fabsf(world.m[10]) * half[2];
		for (int s = 0; s < clip_surface_count; ++s)
		{
			const ClipSurface *surface = &clip_surfaces[s];
			const bool drawn_over = surface->terrain == NULL && surface->background->phase > object->phase;
			float top = surface->terrain != NULL
			                ? surface->height + align_scale(surface->height) * SDL_max(surface->terrain->highest, 0)
			                : surface->height;
			const float bottom = middle[1] - reach;
			float room = drawn_over ? middle[1] + reach - top : top - bottom;
			if (room <= CLIP_LOG_MIN * k || !clip_anchor(surface, middle[0], middle[2], &anchors[count]))
				continue;
			if (surface->terrain != NULL)
			{
				// What stands round it and between it and the camera: the way from its lowest point up to
				// the terrain's highest goes about as far across as the camera is away across for its height.
				const float *eye = shown_view.camera.position;
				const float across = sqrtf((eye[0] - middle[0]) * (eye[0] - middle[0]) + (eye[2] - middle[2]) * (eye[2] - middle[2]));
				const float reach_across = (top - bottom) * across / SDL_max(eye[1] - bottom, 1.0f);
				top = clip_local_top(surface, &anchors[count], eye, middle[0] - half_x, middle[2] - half_z, middle[0] + half_x,
				                     middle[2] + half_z, reach_across);
				room = top - bottom;
				if (room <= CLIP_LOG_MIN * k)
					continue;
			}
			surfaces[count] = surface;
			tops[count] = top;
			over[count++] = drawn_over;
		}
		// (Ground enemies on a ground that isn't flat may float.)
		const bool may_float = object->layer == L3D_GROUND_ENEMY && stand.on && stand.background != NULL &&
		                       (stand.terrain != NULL || stand.low != NULL);
		const ClipMesh *mesh = count > 0 || may_float ? clip_mesh(object->model) : NULL;
		// (cells of about two thirds of a game pixel where the playfield's bottom edge is)
		if (mesh == NULL || !clip_view_model(&view, mesh, &world, vp, window_w, window_h, window_w / l3d_field_w() / 1.5f))
			continue;

		// Each point of the model the camera would see, against each surface: hidden by a terrain (the
		// way to the camera passes below its surface) or by a flat background the game draws under the
		// enemy, or shown above one the game draws over it, where it has a pixel. How far (world), and
		// how much of what is seen of the model.
		float deepest[CLIP_KINDS];
		int cells_of[CLIP_KINDS] = { 0 }, inside_of[CLIP_KINDS] = { 0 }, deepest_cell[CLIP_KINDS] = { 0 };
		for (int kind = 0; kind < CLIP_KINDS; ++kind)
			deepest[kind] = -INFINITY;
		int seen = 0;
		for (int c = 0; c < view.w * view.h; ++c)
		{
			if (view.depth[c] == INFINITY)
				continue;
			++seen;
			const float *p = view.point[c];
			float to_camera[3] = { camera->position[0] - p[0], camera->position[1] - p[1], camera->position[2] - p[2] };
			const float length = sqrtf(to_camera[0] * to_camera[0] + to_camera[1] * to_camera[1] + to_camera[2] * to_camera[2]);
			if (length <= 0 || to_camera[1] <= 0)
				continue;
			for (int a = 0; a < 3; ++a)
				to_camera[a] /= length;
			bool counted[CLIP_KINDS] = { false }, inside[CLIP_KINDS] = { false };
			for (int s = 0; s < count; ++s)
			{
				const ClipSurface *surface = surfaces[s];
				const int kind = clip_kind(surface, over[s]);
				float d = -INFINITY, height, local;
				bool in = false;  // the point inside the terrain (below its surface where it is)
				if (surface->terrain != NULL)
				{
					in = clip_surface_height(surface, &anchors[s], p[0], p[2], &height, &local) && height > p[1] + 0.3f;
					// Along the way to the camera, from a little off the point, until above the terrain's top
					// round the model.
					for (float t = 0.3f; p[1] + t * to_camera[1] < tops[s] && t < 80.0f; t += 1.0f)
					{
						const float x = p[0] + t * to_camera[0], y = p[1] + t * to_camera[1], z = p[2] + t * to_camera[2];
						if (clip_surface_height(surface, &anchors[s], x, z, &height, &local))
							d = SDL_max(d, height - y);
					}
				}
				else if (!over[s] ? p[1] < surface->height : p[1] > surface->height)
				{
					// Where the way to the camera crosses the plane (one drawn over the enemy: behind the
					// point, where the game's plane would cover it).
					const float t = (surface->height - p[1]) / to_camera[1];
					if (clip_surface_height(surface, &anchors[s], p[0] + t * to_camera[0], p[2] + t * to_camera[2], &height, &local))
						d = fabsf(surface->height - p[1]);
				}
				if (d <= 0)
					continue;
				if (d > deepest[kind])
				{
					deepest[kind] = d;
					deepest_cell[kind] = c;
				}
				if (d > CLIP_LOG_MIN * k && !counted[kind])
				{
					counted[kind] = true;
					++cells_of[kind];
				}
				if (d > CLIP_LOG_MIN * k && in && !inside[kind])
				{
					inside[kind] = true;
					++inside_of[kind];
				}
			}
		}

		// Floating: the lowest points of it the camera sees (within CLIP_FLOAT_BAND of the lowest), against
		// the ground drawn under each: how much higher above it they stand than they would above a flat
		// ground (its lift, against the ground's there). Leaning (object_leans), its lowest points are those
		// lowest above its leaning base, and its lift at each is what the lean adds there.
		float floats_by = -INFINITY, gap = 0;
		int bottom = 0, floating = 0, floating_cell = 0;
		const ObjectLean *lean = &object_leans[o];
		if (may_float)
		{
			float lowest = INFINITY;
			for (int c = 0; c < view.w * view.h; ++c)
				if (view.depth[c] != INFINITY)
					lowest = SDL_min(lowest, view.point[c][1] - lean_rise(lean, clip_transforms[o].m[13], view.point[c]));
			for (int c = 0; c < view.w * view.h; ++c)
			{
				if (view.depth[c] == INFINITY || view.point[c][1] - lean_rise(lean, clip_transforms[o].m[13], view.point[c]) > lowest + CLIP_FLOAT_BAND * k)
					continue;
				const float under = stand_ground_at(view.point[c][0], view.point[c][2]);
				const float excess = object_lifts[o] + lean_rise(lean, clip_transforms[o].m[13], view.point[c]) - under;
				++bottom;
				if (excess > floats_by)
				{
					floats_by = excess;
					gap = view.point[c][1] - (stand.plane + under);
					floating_cell = c;
				}
				floating += excess > CLIP_LOG_MIN * k;
			}
		}

		// Where its middle is in the window (as rgpu_playfield_to_window finds it).
		float clip[4];
		for (int r = 0; r < 4; ++r)
			clip[r] = vp[r] * middle[0] + vp[4 + r] * middle[1] + vp[8 + r] * middle[2] + vp[12 + r];
		const float w = clip[3] > 1e-6f ? clip[3] : 1e-6f;
		char sheet[8];
		for (int kind = 0; kind <= CLIP_KINDS; ++kind)
		{
			const bool is_float = kind == CLIP_KINDS;  // (after the surfaces' kinds)
			if (is_float ? !(floats_by > CLIP_LOG_MIN * k) : !(deepest[kind] > CLIP_LOG_MIN * k) || cells_of[kind] == 0)
				continue;
			printf("clip: %s frame %u layer %s sheet %s sprite %u model %s at %.0f,%.0f depth %.1f of %.1f area %.1f inside %.0f screen %.3f,%.3f",
			       is_float ? "float" : clip_kind_names[kind], l3d_frame_number, l3d_layer_name(object->layer),
			       clip_sheet_name(object->enemy_sheet, sheet), (unsigned int)object->enemy_sprite,
			       m3d_models[object->model].name, object->x, object->y, (is_float ? floats_by : deepest[kind]) / k, 2 * reach / k,
			       is_float ? 100.0f * floating / SDL_max(bottom, 1) : 100.0f * cells_of[kind] / SDL_max(seen, 1),
			       is_float ? 0.0f : 100.0f * inside_of[kind] / cells_of[kind], (clip[0] / w + 1) / 2, (1 - clip[1] / w) / 2);
			if (is_float)
				printf(" gap %.1f", gap / k);
			printf("\n");
			if (verbose)
			{
				const float *p = view.point[is_float ? floating_cell : deepest_cell[kind]];
				printf("clip-cell: %s point %.2f,%.2f,%.2f (%.1f,%.1f from the middle, game pixels) of %d seen, %d deep, base %.2f, "
				       "lift %.1f (the ground drawn under its middle %.1f, the terrain stored at its position %.1f), lean %.1f,%.1f\n",
				       is_float ? "float" : clip_kind_names[kind], p[0], p[1], p[2], (p[0] - middle[0]) / k, (p[2] - middle[2]) / k,
				       is_float ? bottom : seen, is_float ? floating : cells_of[kind], clip_transforms[o].m[13], object_lifts[o],
				       stand_ground_at(middle[0], middle[2]), terrain_lift(object->x, object->y),
				       atanf(lean->sx) * 180.0f / (float)M_PI, atanf(lean->sz) * 180.0f / (float)M_PI);
			}
			printed = true;
		}
	}
	if (printed)
		fflush(stdout);  // (runs are often ended by killing the game)
}

// The starfield sits below background 1, whose colour 0 lets it through as in the game.
#define STARS_BELOW_LAYER 0.3f

// The game's stars: below the ground; where it is terrain, below its chasms (where it has holes)
// and its lowest ground.
static float stars_below_layer(void)
{
	const B3DTerrain *t = frame_terrains[1];
	if (t == NULL)
		return STARS_BELOW_LAYER;
	return STARS_BELOW_LAYER + SDL_max(t->holes ? TERRAIN_HOLE_DEPTH : 0.0f, (float)-t->lowest) + 4.0f;
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
#define DEEP_STAR_LAYERS 4

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
	// Seen from the side only: near, bright stars ahead of the playfield too (the game's own
	// stars are only on the playfield).
	{ 8.0f, 150, 1.1f, 0.95f },
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
	if (!frame->space || !settings3d.effects || *batch_count >= MAX_BATCHES || stars_covered())
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
	for (int k = 0; k < DEEP_STAR_LAYERS - (l3d_sideways ? 0 : 1); ++k)
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

/*
 * Deep space's nebula: a few patches of glowing gas far under the deepest stars, in two hues of the
 * level's own (by its background 1 map), drifting by slower still as the stars scroll. Like the stars
 * they show through what background 1 leaves empty, and only with the Effects setting. Faint: the
 * game's shots must read over them.
 */
#define NEBULA_DEPTH 900.0f  // game pixels below the game's stars

static void add_nebula_batch(const L3DFrame *frame, const Camera3D *camera, const float *heights,
                             int *instance_count, int *batch_count)
{
	if (!frame->space || !settings3d.effects || *batch_count >= MAX_BATCHES || stars_covered())
		return;

	static const float hues[][2][3] = {
		{ { 0.16f, 0.26f, 0.85f }, { 0.52f, 0.18f, 0.78f } },  // blue and violet
		{ { 0.08f, 0.50f, 0.62f }, { 0.22f, 0.30f, 0.85f } },  // teal and blue
		{ { 0.78f, 0.24f, 0.30f }, { 0.80f, 0.48f, 0.18f } },  // rose and amber
		{ { 0.20f, 0.60f, 0.38f }, { 0.12f, 0.38f, 0.72f } },  // green and sea blue
		{ { 0.62f, 0.20f, 0.62f }, { 0.20f, 0.42f, 0.86f } },  // magenta and blue
	};
	static unsigned int seeded_for = 0;  // b3d_map_generation + 1
	static Uint32 level = 0;
	if (seeded_for != b3d_map_generation + 1)
	{
		seeded_for = b3d_map_generation + 1;
		const Uint64 map = b3d_map_hash(1);
		level = (Uint32)map ^ (Uint32)(map >> 32);
	}
	const float (*hue)[3] = hues[hash32(level) % SDL_arraysize(hues)];

	const float height = heights[frame->star_layer] - stars_below_layer() - NEBULA_DEPTH * rgpu_camera.height_scale;
	float rect[4];
	plane_footprint_world(camera, height, -BACKGROUND_AHEAD, rect);
	if (rect[0] > rect[2] || rect[1] >= rect[3])
		return;
	const float w = rect[2] - rect[0], h = rect[3] - rect[1];
	// (They scroll as the deep stars do; deeper, they seem to drift slower.)
	const float scroll = deep_star_scroll + (2.0f + starfield_speed) * ahead;

	const int first = *instance_count;
	for (int i = 0; i < NEBULA_PATCHES && *instance_count < MAX_INSTANCES; ++i)
	{
		const Uint32 seed = hash32(level + (Uint32)i * 977u);
		const float size = w * (0.35f + 0.45f * hash_unit(seed + 1));
		// (Each comes round again past the far end, out of sight: the span is the view and a patch.)
		const float span = h + size;
		const float cx = rect[0] + hash_unit(seed + 2) * w;
		const float cz = rect[1] - size / 2 + fmodf(hash_unit(seed + 3) * span + scroll, span);
		const float turn = hash_unit(seed + 4) * 6.2832f, stretch = 0.7f + 0.6f * hash_unit(seed + 5);
		const float c = cosf(turn), sn = sinf(turn);
		const float sx = size * stretch, sz = size / stretch;

		Mat4 transform = mat4_identity();
		transform.m[0] = c * sx;
		transform.m[2] = -sn * sx;
		transform.m[8] = sn * sz;
		transform.m[10] = c * sz;
		// (The quad's corner at the origin: its middle at cx, cz.)
		transform.m[12] = cx - (transform.m[0] + transform.m[8]) / 2;
		transform.m[13] = height;
		transform.m[14] = cz - (transform.m[2] + transform.m[10]) / 2;
		float *instance = instances + *instance_count * 24;
		write_instance_world(instance, &transform, 1.0f);
		const float strength = 0.05f + 0.06f * hash_unit(seed + 6);
		for (int k = 0; k < 3; ++k)
			instance[16 + k] = hue[i & 1][k] * strength;
		++*instance_count;
	}
	if (*instance_count == first)
		return;

	BTBHGPUSceneGeometryBatch *b = &batches[(*batch_count)++];
	init_batch(b);
	b->kind = BTBH_GPU_SCENE_GEOMETRY_CUSTOM_MESH;
	b->custom_mesh = quad_mesh;
	b->first_instance = first;
	b->instance_count = *instance_count - first;
	b->albedo_texture = nebula_texture;
	b->unlit_enabled = 1;
	b->transparency_enabled = 1;
	b->blend_mode = BTBH_GPU_SCENE_BLEND_ADDITIVE;
}

/*
 * The level's weather (b3d_weather, Effects only): snow falling and drifting over the ice planets, at every
 * depth between the ground and the camera, so the air itself shows depth; embers rising from the lava,
 * flickering and fading as they climb; pollen floating and glinting low over the meadows and jungles; in
 * open space (the starfield on) faint dust streaming by. Each lies in a band of heights, spread over what the camera sees
 * there, and comes round again within it.
 */
#define WEATHER_BANDS 5
#define WEATHER_PER_BAND 70

static void add_weather_batch(const L3DFrame *frame, const Camera3D *camera, const float *heights,
                              int *instance_count, int *batch_count)
{
	const B3DWeather weather = b3d_weather();
	// In open space, dust drifting by.
	const bool dust = weather == B3D_WEATHER_NONE && frame->space && !stars_covered();
	if ((weather == B3D_WEATHER_NONE && !dust) || !settings3d.effects || *batch_count >= MAX_BATCHES)
		return;
	float ground = heights[0];
	for (int l = 0; l < frame->layer_count; ++l)
		if (frame->layers[l].type == L3D_GROUND)
			ground = heights[l];
	const bool snow = weather == B3D_WEATHER_SNOW, pollen = weather == B3D_WEATHER_POLLEN;
	const bool sand = weather == B3D_WEATHER_SAND, leaves = weather == B3D_WEATHER_LEAVES;
	const bool bubbles = weather == B3D_WEATHER_BUBBLES;
	// (Snow and dust from high up, below the camera; embers only up from the lava; pollen low; sand lowest.)
	const float top = ground + (snow || dust ? 130.0f : pollen || leaves ? 60.0f : sand ? 26.0f : 80.0f) * rgpu_camera.height_scale;
	const float band = (top - ground) / WEATHER_BANDS;
	const float t = (l3d_frame_number + ahead) / 35.0f;

	const int first = *instance_count;
	for (int k = 0; k < WEATHER_BANDS; ++k)
	{
		const float low = ground + band * k + 4.0f;
		float rect[4];
		plane_footprint_world(camera, low + band / 2, -BACKGROUND_AHEAD, rect);
		if (rect[0] > rect[2] || rect[1] >= rect[3])
			continue;
		const float w = rect[2] - rect[0], h = rect[3] - rect[1];
		const int count = snow || sand ? WEATHER_PER_BAND : dust || pollen ? WEATHER_PER_BAND / 2 : leaves || bubbles ? WEATHER_PER_BAND / 3
		                : WEATHER_PER_BAND * 2 / 3;
		for (int i = 0; i < count && *instance_count < MAX_INSTANCES; ++i)
		{
			const Uint32 seed = hash32((Uint32)(k * 131 + i) * 2654435761u + (snow ? 17u : dust ? 41u : 29u));
			const float r0 = hash_unit(seed), r1 = hash_unit(seed + 1), r2 = hash_unit(seed + 2), r3 = hash_unit(seed + 3);
			if (dust)
			{
				// Still in height, streaming down the screen as the ship flies on; faint, bluish.
				const float x = rect[0] + r0 * w;
				const float z = rect[1] + fmodf(r1 * h + t * (34.0f + 22.0f * r2), h);
				const float size = 0.8f + 0.9f * r3;
				Mat4 transform = mat4_identity();
				transform.m[0] = transform.m[5] = transform.m[10] = size;
				transform.m[12] = x;
				transform.m[13] = low + band * r3;
				transform.m[14] = z;
				float *instance = instances + *instance_count * 24;
				write_instance_world(instance, &transform, 1.0f);
				const float a = 0.22f + 0.2f * r2;
				instance[16] = 0.6f * a;
				instance[17] = 0.68f * a;
				instance[18] = 0.85f * a;
				++*instance_count;
				continue;
			}
			if (bubbles)
			{
				// Rising from the floor, wobbling, swelling a little as they go; drifting with the water.
				const float speed = 6.0f + 6.0f * r2;
				const float through = fmodf(r3 * band * WEATHER_BANDS + t * speed, band * WEATHER_BANDS) / (band * WEATHER_BANDS);
				const float wobble = sinf(t * (2.0f + 2.0f * r1) + r0 * 6.2832f) * 1.5f;
				Mat4 transform = mat4_identity();
				const float size = (1.2f + 1.8f * r1) * (0.8f + 0.4f * through);
				transform.m[0] = transform.m[5] = transform.m[10] = size;
				transform.m[12] = rect[0] + fmodf(r0 * w + wobble + w, w);
				transform.m[13] = ground + 2.0f + band * WEATHER_BANDS * through;
				transform.m[14] = rect[1] + fmodf(r1 * h + t * 1.5f, h);
				float *instance = instances + *instance_count * 24;
				write_instance_world(instance, &transform, 1.0f);
				const float a = 0.5f * sinf(through * 3.14159f);
				instance[16] = 0.7f * a;
				instance[17] = 0.92f * a;
				instance[18] = 1.0f * a;
				++*instance_count;
				continue;
			}
			if (sand || leaves)
			{
				// Blown along by the wind, to the right and a little down the screen: sand in streaks low over the
				// ground, fast; leaves slower, fluttering (their width beating as they turn), bobbing up and down.
				const float speed = sand ? 70.0f + 50.0f * r2 : 22.0f + 16.0f * r2;
				const float x = rect[0] + fmodf(r0 * w + t * speed, w);
				const float z = rect[1] + fmodf(r1 * h + t * speed * 0.18f, h);
				const float bob = leaves ? sinf(t * (1.5f + r3) + r0 * 6.2832f) * band * 0.4f : 0.0f;
				const float size = sand ? 1.4f + 0.8f * r3 : 4.5f + 2.0f * r3;
				const float flutter = leaves ? 0.35f + 0.65f * fabsf(sinf(t * (3.0f + 3.0f * r2) + r1 * 6.2832f)) : 3.5f;
				Mat4 transform = mat4_identity();
				transform.m[0] = size * flutter;
				transform.m[5] = transform.m[10] = size;
				if (leaves)
				{
					// Turned its own way, turning slowly as it goes; fluttering across its width.
					const float angle = r0 * 6.2832f + t * (0.8f + 1.2f * r1) * (i % 2 ? 1 : -1);
					const float ca = cosf(angle), sa = sinf(angle);
					transform.m[0] = ca * size;
					transform.m[1] = sa * size;
					transform.m[4] = -sa * size * flutter;
					transform.m[5] = ca * size * flutter;
				}
				transform.m[12] = x;
				transform.m[13] = low + band * (0.5f + 0.4f * (r3 - 0.5f)) + bob;
				transform.m[14] = z;
				float *instance = instances + *instance_count * 24;
				write_instance_world(instance, &transform, 1.0f);
				// (Blended, not added: pale sand over the ground, autumn leaves over the grass.)
				static const float sand_rgb[3] = { 0.86f, 0.7f, 0.46f };
				static const float leaf_rgb[3][3] = { { 0.78f, 0.56f, 0.1f }, { 0.62f, 0.28f, 0.06f }, { 0.5f, 0.56f, 0.12f } };
				const float *rgb = sand ? sand_rgb : leaf_rgb[i % 3];
				for (int c = 0; c < 3; ++c)
					instance[16 + c] = rgb[c] * (0.8f + 0.4f * r2);
				instance[19] = sand ? 0.45f + 0.25f * r1 : 1.0f;
				++*instance_count;
				continue;
			}
			if (pollen)
			{
				// Floating up and down in its band, wandering slowly; glinting now and then.
				const float x = rect[0] + fmodf(r0 * w + sinf(t * (0.3f + 0.3f * r2) + r1 * 6.2832f) * 8.0f + w, w);
				const float z = rect[1] + fmodf(r1 * h + t * (2.0f + 2.0f * r3), h);
				const float glint = 0.5f + 0.5f * sinf(t * (1.2f + 1.6f * r1) + r3 * 6.2832f);
				Mat4 transform = mat4_identity();
				transform.m[0] = transform.m[5] = transform.m[10] = 1.2f + 0.9f * r2;
				transform.m[12] = x;
				transform.m[13] = low + band * (0.5f + 0.4f * sinf(t * (0.4f + 0.4f * r0) + r2 * 6.2832f));
				transform.m[14] = z;
				float *instance = instances + *instance_count * 24;
				write_instance_world(instance, &transform, 1.0f);
				const float a = (0.15f + 0.5f * glint * glint) * (0.7f + 0.3f * r0);
				instance[16] = 1.0f * a;
				instance[17] = 0.95f * a;
				instance[18] = 0.45f * a;
				++*instance_count;
				continue;
			}
			// Through its band: snow down, embers up; faint at the band's ends, where it comes round.
			const float speed = snow ? 4.0f + 3.0f * r2 : 7.0f + 6.0f * r2;
			const float through = fmodf(r3 * band + t * speed, band) / band;
			const float height = snow ? low + band * (1 - through) : low + band * through;
			const float fade = sinf(through * 3.14159f);
			// Snow drifts down the screen with a little sway; embers waver as they climb.
			const float drift = snow ? t * (9.0f + 5.0f * r1) : t * 2.0f;
			const float sway = sinf(t * (0.6f + 0.8f * r2) + r0 * 6.2832f) * (snow ? 5.0f : 3.0f);
			const float x = rect[0] + fmodf(r0 * w + sway + w, w);
			const float z = rect[1] + fmodf(r1 * h + drift, h);
			const float size = snow ? 2.0f + 1.8f * r2 : 1.8f + 1.4f * r3;

			Mat4 transform = mat4_identity();
			transform.m[0] = transform.m[5] = transform.m[10] = size;
			transform.m[12] = x;
			transform.m[13] = height;
			transform.m[14] = z;
			float *instance = instances + *instance_count * 24;
			write_instance_world(instance, &transform, 1.0f);
			if (snow)
			{
				const float a = (0.6f + 0.35f * r3) * fade;
				instance[16] = 0.9f * a;
				instance[17] = 0.94f * a;
				instance[18] = 1.0f * a;
			}
			else
			{
				// Bright as they leave the lava, dimmer as they climb; flickering.
				const float flicker = 0.7f + 0.3f * sinf(t * (9.0f + 7.0f * r1) + r0 * 6.2832f);
				const float a = (0.55f + 0.3f * r0) * fade * (1.1f - 0.6f * (float)k / WEATHER_BANDS) * flicker;
				instance[16] = 1.5f * a;
				instance[17] = 0.6f * a;
				instance[18] = 0.12f * a;
			}
			++*instance_count;
		}
	}
	if (*instance_count == first)
		return;

	BTBHGPUSceneGeometryBatch *b = &batches[(*batch_count)++];
	init_batch(b);
	b->kind = BTBH_GPU_SCENE_GEOMETRY_CUSTOM_MESH;
	b->custom_mesh = billboard_mesh;
	b->first_instance = first;
	b->instance_count = *instance_count - first;
	b->albedo_texture = leaves ? leaf_texture : bubbles ? ring_texture : particle_texture;
	b->billboard_mode = BTBH_GPU_SCENE_BILLBOARD_FRONT;
	b->unlit_enabled = 1;
	b->transparency_enabled = 1;
	b->blend_mode = sand || leaves ? BTBH_GPU_SCENE_BLEND_ALPHA : BTBH_GPU_SCENE_BLEND_ADDITIVE;
}

/*
 * A distant planet under deep space, deeper than the nebula: a sphere with one of the jukebox's planet surfaces
 * (by the level's background 1 map: which surface, its tint, size and place), its axis lying along the screen so its
 * bands run across, turning slowly (its texture wraps round), drifting by far slower than the stars and coming round
 * again after a long while. Lit as the models are lit, from the sun, its shading baked into the mesh's colours (it is
 * unlit, so no shadow of the level falls so deep); a halo of its atmosphere round it. Effects only.
 */
#define WORLD_DEPTH 1700.0f  // game pixels below the game's stars
#define WORLD_TILT 0.35f     // its axis leans this much towards the camera

static void world_axes(float x[3], float y[3], float z[3])
{
	// Local y (the poles) up the screen and a little towards the camera, local x along the screen's x.
	const float len = sqrtf(1 + WORLD_TILT * WORLD_TILT);
	x[0] = 1, x[1] = 0, x[2] = 0;
	y[0] = 0, y[1] = WORLD_TILT / len, y[2] = -1 / len;
	z[0] = x[1] * y[2] - x[2] * y[1];
	z[1] = x[2] * y[0] - x[0] * y[2];
	z[2] = x[0] * y[1] - x[1] * y[0];
}

static BTBHGPUCustomMesh *create_world_mesh(void)
{
	enum { SLICES = 64, STACKS = 32, VERTICES = (SLICES + 1) * (STACKS + 1) };
	static float vertices[VERTICES * 24];
	static uint32_t indices[SLICES * STACKS * 6];
	float ax[3], ay[3], az[3];
	world_axes(ax, ay, az);
	float light[3] = { -sun_direction[0], -sun_direction[1], -sun_direction[2] };
	const float ll = sqrtf(light[0] * light[0] + light[1] * light[1] + light[2] * light[2]);
	for (int c = 0; c < 3; ++c)
		light[c] /= ll;
	int v = 0;
	for (int j = 0; j <= STACKS; ++j)
		for (int i = 0; i <= SLICES; ++i, ++v)
		{
			const float lat = (float)M_PI * j / STACKS, lon = 2 * (float)M_PI * i / SLICES;
			const float n[3] = { sinf(lat) * cosf(lon), cosf(lat), sinf(lat) * sinf(lon) };
			float *out = &vertices[v * 24];
			memset(out, 0, 24 * sizeof(float));
			memcpy(out, n, sizeof(n));
			memcpy(out + 3, n, sizeof(n));
			out[6] = (float)i / SLICES;
			out[7] = (float)j / STACKS;
			out[8] = 1, out[11] = 1;
			// Lit by the sun: its normal in the world (as the instance turns it), a soft terminator, a faint night.
			const float wn[3] = { ax[0] * n[0] + ay[0] * n[1] + az[0] * n[2], ax[1] * n[0] + ay[1] * n[1] + az[1] * n[2],
			                      ax[2] * n[0] + ay[2] * n[1] + az[2] * n[2] };
			const float d = wn[0] * light[0] + wn[1] * light[1] + wn[2] * light[2];
			const float t = SDL_clamp((d + 0.15f) / 0.6f, 0.0f, 1.0f);
			const float lit = 0.05f + 0.95f * t * t * (3 - 2 * t);
			out[12] = out[13] = out[14] = lit;
			out[15] = 1;
		}
	int k = 0;
	for (int j = 0; j < STACKS; ++j)
		for (int i = 0; i < SLICES; ++i)
		{
			const uint32_t a = (uint32_t)(j * (SLICES + 1) + i), b = a + 1, c = a + SLICES + 1, d = c + 1;
			indices[k++] = a, indices[k++] = c, indices[k++] = b;
			indices[k++] = b, indices[k++] = c, indices[k++] = d;
		}
	BTBHGPUCustomMeshReport report;
	BTBHGPUCustomMesh *mesh = btbh_gpu_window_custom_mesh_create(window, vertices, sizeof(vertices), VERTICES, indices,
	                                                             (uint32_t)k, &report);
	if (mesh == NULL)
		fprintf(stderr, "warning: planet mesh: %s\n", report.message);
	return mesh;
}

static void add_planet_batch(const L3DFrame *frame, const Camera3D *camera, const float *heights,
                             int *instance_count, int *batch_count)
{
	if (!frame->space || !settings3d.effects || *batch_count + 2 > MAX_BATCHES || stars_covered() ||
	    *instance_count + 2 > MAX_INSTANCES)
		return;

	// The level's planet, and where its drift began (the deep stars' scroll when the level's map came).
	static unsigned int seeded_for = 0;  // b3d_map_generation + 1
	static Uint32 level = 0;
	static float scroll_start = 0;
	if (seeded_for != b3d_map_generation + 1)
	{
		seeded_for = b3d_map_generation + 1;
		const Uint64 map = b3d_map_hash(1);
		level = hash32((Uint32)map ^ (Uint32)(map >> 32) ^ 0x5bd1e995u);
		scroll_start = deep_star_scroll;
	}
	static const struct
	{
		J3DTexture texture;
		float tint[3];
	} kinds[] = {
		{ J3D_TEXTURE_GAS_GIANT, { 1.0f, 1.0f, 1.0f } },
		{ J3D_TEXTURE_GAS_GIANT, { 1.15f, 0.8f, 0.6f } },   // rust and cream
		{ J3D_TEXTURE_GAS_GIANT, { 0.85f, 0.75f, 1.15f } }, // violet
		{ J3D_TEXTURE_TERRAN, { 1.0f, 1.0f, 1.0f } },
		{ J3D_TEXTURE_TERRAN, { 1.1f, 0.9f, 0.7f } },       // an arid world
	};
	const int kind = (int)(level % SDL_arraysize(kinds));
	const J3DTexture texture = kinds[kind].texture;
	if (world_textures[texture] == NULL)
	{
		int tw, th;
		const Uint32 *pixels = jukebox3d_planet_texture(texture, &tw, &th);
		BTBHGPUTextureReport report;
		world_textures[texture] = btbh_gpu_window_texture_create_rgba8_ex(
			window, (const uint8_t *)pixels, (uint32_t)tw, (uint32_t)th, 1, BTBH_GPU_TEXTURE_FILTER_LINEAR,
			BTBH_GPU_TEXTURE_WRAP_REPEAT, BTBH_GPU_TEXTURE_COLOR_SPACE_SRGB, &report);
	}
	if (world_mesh == NULL)
		world_mesh = create_world_mesh();
	if (world_textures[texture] == NULL || world_mesh == NULL)
		return;

	const float height = heights[frame->star_layer] - stars_below_layer() - WORLD_DEPTH * rgpu_camera.height_scale;
	float rect[4];
	plane_footprint_world(camera, height, -BACKGROUND_AHEAD, rect);
	if (rect[0] > rect[2] || rect[1] >= rect[3])
		return;
	const float w = rect[2] - rect[0], h = rect[3] - rect[1];
	const float radius = w * (0.11f + 0.08f * hash_unit(level + 1));
	// Down the screen at a tenth of the stars' pace, a long gap before it comes round; first seen up the view.
	const float span = h + 2 * radius + h;
	const float drift = (deep_star_scroll - scroll_start + (2.0f + starfield_speed) * ahead) * 0.1f;
	const float cx = rect[0] + w * (0.2f + 0.6f * hash_unit(level + 2));
	const float cz = rect[1] - radius + fmodf(radius + h * 0.35f + drift, span);
	if (cz - radius > rect[3] || cz + radius < rect[1])
		return;

	float ax[3], ay[3], az[3];
	world_axes(ax, ay, az);
	Mat4 transform = mat4_identity();
	for (int c = 0; c < 3; ++c)
	{
		transform.m[c] = ax[c] * radius;
		transform.m[4 + c] = ay[c] * radius;
		transform.m[8 + c] = az[c] * radius;
	}
	transform.m[12] = cx;
	transform.m[13] = height;
	transform.m[14] = cz;
	const int first = *instance_count;
	float *instance = instances + *instance_count * 24;
	write_instance_world(instance, &transform, 1.0f);
	for (int c = 0; c < 3; ++c)
		instance[16 + c] = kinds[kind].tint[c];
	++*instance_count;

	BTBHGPUSceneGeometryBatch *b = &batches[(*batch_count)++];
	init_batch(b);
	b->kind = BTBH_GPU_SCENE_GEOMETRY_CUSTOM_MESH;
	b->custom_mesh = world_mesh;
	b->first_instance = first;
	b->instance_count = 1;
	b->albedo_texture = world_textures[texture];
	b->uv_offset_x = fmodf((l3d_frame_number + ahead) * 0.00004f, 1.0f);  // (turning)
	b->unlit_enabled = 1;
	b->cull_mode = BTBH_GPU_SCENE_CULL_BACK;

	// Its atmosphere's halo, in its own light.
	Mat4 halo = mat4_identity();
	halo.m[0] = halo.m[5] = halo.m[10] = radius * 2.5f;
	halo.m[12] = cx;
	halo.m[13] = height;
	halo.m[14] = cz;
	instance = instances + *instance_count * 24;
	write_instance_world(instance, &halo, 1.0f);
	const float glow[3] = { 0.35f, 0.55f, 0.85f };
	for (int c = 0; c < 3; ++c)
		instance[16 + c] = glow[c] * kinds[kind].tint[c] * 0.22f;
	instance[19] = 1;
	b = &batches[(*batch_count)++];
	init_batch(b);
	b->kind = BTBH_GPU_SCENE_GEOMETRY_CUSTOM_MESH;
	b->custom_mesh = billboard_mesh;
	b->first_instance = (*instance_count)++;
	b->instance_count = 1;
	b->albedo_texture = particle_texture;
	b->billboard_mode = BTBH_GPU_SCENE_BILLBOARD_FRONT;
	b->unlit_enabled = 1;
	b->transparency_enabled = 1;
	b->blend_mode = BTBH_GPU_SCENE_BLEND_ADDITIVE;
}

/*
 * Shooting stars in deep space (the starfield on, Effects only): now and then a meteor streaks across the deep
 * space under the stars, a bright head and a tail fading behind it, gone in under a second; when, where and which way
 * by the time, so they come unevenly.
 */
#define METEOR_SLOTS 2       // that many may fly at once
#define METEOR_PERIOD 4.5f   // seconds: each slot's turn comes round
#define METEOR_LIFE 0.7f     // seconds a meteor flies
#define METEOR_DEPTH 500.0f  // game pixels below the game's stars
#define METEOR_GLOWS 32      // along its tail

static void add_meteor_batch(const L3DFrame *frame, const Camera3D *camera, const float *heights, int *instance_count,
                             int *batch_count)
{
	if (!frame->space || !settings3d.effects || *batch_count >= MAX_BATCHES || stars_covered())
		return;
	const float height = heights[frame->star_layer] - stars_below_layer() - METEOR_DEPTH * rgpu_camera.height_scale;
	float rect[4];
	plane_footprint_world(camera, height, -BACKGROUND_AHEAD, rect);
	if (rect[0] > rect[2] || rect[1] >= rect[3])
		return;
	const float w = rect[2] - rect[0], h = rect[3] - rect[1];
	const float t = (l3d_frame_number + ahead) / 35.0f;
	const int first = *instance_count;
	for (int m = 0; m < METEOR_SLOTS; ++m)
	{
		const float slot_t = t + m * METEOR_PERIOD * 0.5f;
		const Uint32 turn = (Uint32)floorf(slot_t / METEOR_PERIOD);
		const Uint32 seed = hash32(turn * 2654435761u + (Uint32)m * 97u);
		if (hash_unit(seed) < 0.35f)
			continue;  // (not every turn: they come unevenly)
		// Its start within the period, so they don't keep time.
		const float start = hash_unit(seed + 1) * (METEOR_PERIOD - METEOR_LIFE);
		const float age = (fmodf(slot_t, METEOR_PERIOD) - start) / METEOR_LIFE;
		if (age < 0 || age > 1)
			continue;
		const float angle = (hash_unit(seed + 2) < 0.5f ? 0.35f : (float)M_PI - 0.35f) + (hash_unit(seed + 3) - 0.5f) * 0.8f;
		const float dx = cosf(angle), dz = sinf(angle);
		const float x0 = rect[0] + w * (0.15f + 0.7f * hash_unit(seed + 4)), z0 = rect[1] + h * (0.1f + 0.5f * hash_unit(seed + 5));
		const float travel = w * (0.35f + 0.25f * hash_unit(seed + 6));
		const float hx = x0 + dx * travel * age, hz = z0 + dz * travel * age;
		const float tail = travel * 0.45f * SDL_min(1.0f, age * 3);
		const float fade = SDL_min(1.0f, (1 - age) * 4) * SDL_min(1.0f, age * 8);
		for (int g = 0; g < METEOR_GLOWS && *instance_count < MAX_INSTANCES; ++g)
		{
			const float k = (float)g / (METEOR_GLOWS - 1);  // 0 the head, 1 the tail's end
			Mat4 transform = mat4_identity();
			const float size = (g == 0 ? 14.0f : 9.0f * (1 - k * 0.75f)) * rgpu_camera.height_scale;
			transform.m[0] = transform.m[5] = transform.m[10] = size;
			transform.m[12] = hx - dx * tail * k;
			transform.m[13] = height;
			transform.m[14] = hz - dz * tail * k;
			float *instance = instances + *instance_count * 24;
			write_instance_world(instance, &transform, 1.0f);
			const float a = fade * (g == 0 ? 1.0f : 0.45f * (1 - k) * (1 - k));
			instance[16] = 0.75f * a;
			instance[17] = 0.85f * a;
			instance[18] = 1.0f * a;
			instance[19] = 1;
			++*instance_count;
		}
	}
	if (*instance_count == first)
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

/*
 * Gulls over the sea levels (b3d_birds, Effects only): a few flocks, each in a loose V, flying their own heading over
 * the water at a height of their own, wings beating and gliding by turns; they come round again across the view.
 */
#define BIRD_FLOCKS 3
#define BIRDS_PER_FLOCK 5

static void add_bird_batch(const L3DFrame *frame, const Camera3D *camera, const float *heights, int *instance_count,
                           int *batch_count)
{
	if (!b3d_birds() || !settings3d.effects || *batch_count >= MAX_BATCHES)
		return;
	float ground = heights[0];
	for (int l = 0; l < frame->layer_count; ++l)
		if (frame->layers[l].type == L3D_GROUND)
			ground = heights[l];
	const float t = (l3d_frame_number + ahead) / 35.0f;
	const int first = *instance_count;
	for (int f = 0; f < BIRD_FLOCKS; ++f)
	{
		const Uint32 seed = hash32((Uint32)f * 7919u + 1234u);
		const float height = ground + (26.0f + 16.0f * hash_unit(seed)) * rgpu_camera.height_scale;
		float rect[4];
		plane_footprint_world(camera, height, -BACKGROUND_AHEAD, rect);
		if (rect[0] > rect[2] || rect[1] >= rect[3])
			continue;
		const float w = rect[2] - rect[0], h = rect[3] - rect[1];
		// Its heading: across the screen, one way or the other, a little up or down it.
		const float heading = (hash_unit(seed + 1) < 0.5f ? 0.0f : (float)M_PI) + (hash_unit(seed + 2) - 0.5f) * 1.2f;
		const float dx = cosf(heading), dz = sinf(heading);
		const float speed = 14.0f + 8.0f * hash_unit(seed + 3);
		// Round again after crossing the view and as much again (the scroll carries them down the screen too).
		const float span_x = w * 2, span_z = h * 2;
		const float cx = rect[0] - w * 0.5f + fmodf(hash_unit(seed + 4) * span_x + dx * speed * t + span_x * 64, span_x);
		const float cz = rect[1] - h * 0.5f + fmodf(hash_unit(seed + 5) * span_z + dz * speed * t + span_z * 64, span_z);
		for (int b = 0; b < BIRDS_PER_FLOCK && *instance_count < MAX_INSTANCES; ++b)
		{
			const Uint32 bs = hash32(seed + (Uint32)b * 31u);
			// A loose V behind the leader.
			const int rank = (b + 1) / 2, side = b % 2 ? 1 : -1;
			const float back = rank * 14.0f + hash_unit(bs) * 4.0f, out = side * rank * 12.0f + (hash_unit(bs + 1) - 0.5f) * 4.0f;
			const float x = cx - dx * back - dz * out, z = cz - dz * back + dx * out;
			// Beating its wings a while, then gliding (the span squeezes as the wings beat).
			const float phase = t * 1.3f + hash_unit(bs + 2) * 6.2832f;
			const float beating = sinf(phase * 0.35f) > -0.2f ? 1.0f : 0.0f;
			const float flap = beating * sinf(phase * 6.0f);
			const float span = 15.0f + 4.0f * hash_unit(bs + 3);
			Mat4 transform = mat4_identity();
			// (The texture's x along the wings, its -y the head: turned to the heading.)
			const float fx = -dz, fz = dx;  // its right
			transform.m[0] = fx * span * (0.75f + 0.25f * flap);
			transform.m[2] = fz * span * (0.75f + 0.25f * flap);
			transform.m[4] = dx * span * 0.5f;
			transform.m[6] = dz * span * 0.5f;
			transform.m[5] = 0;
			transform.m[8] = 0, transform.m[9] = 1, transform.m[10] = 0;
			transform.m[12] = x;
			transform.m[13] = height + flap * 0.6f;
			transform.m[14] = z;
			float *instance = instances + *instance_count * 24;
			write_instance_world(instance, &transform, 1.0f);
			for (int c = 0; c < 3; ++c)
				instance[16 + c] = 0.82f;
			instance[19] = 1;
			++*instance_count;
			// Its shadow on the water, cast along the sun's light.
			if (*instance_count < MAX_INSTANCES)
			{
				const float drop = (transform.m[13] - ground) / SDL_max(-sun_direction[1], 0.2f);
				transform.m[12] += sun_direction[0] * drop;
				transform.m[13] = ground + 0.5f;
				transform.m[14] += sun_direction[2] * drop;
				instance = instances + *instance_count * 24;
				write_instance_world(instance, &transform, 1.0f);
				instance[16] = instance[17] = instance[18] = 0;
				instance[19] = 0.28f;
				++*instance_count;
			}
		}
	}
	if (*instance_count == first)
		return;
	BTBHGPUSceneGeometryBatch *b = &batches[(*batch_count)++];
	init_batch(b);
	b->kind = BTBH_GPU_SCENE_GEOMETRY_CUSTOM_MESH;
	b->custom_mesh = billboard_mesh;
	b->first_instance = first;
	b->instance_count = *instance_count - first;
	b->albedo_texture = gull_texture;
	b->unlit_enabled = 1;
	b->transparency_enabled = 1;
	b->blend_mode = BTBH_GPU_SCENE_BLEND_ALPHA;
}

// Appends the starfield outside the playfield (inside it, the captured layer has the stars).
// A composed background 1 has the stars in it already.
static void add_star_batch(const L3DFrame *frame, const bool *composed, const Camera3D *camera,
                           const float *heights, const Uint32 colors[256], int *instance_count, int *batch_count)
{
	if (frame->star_count == 0 || *batch_count >= MAX_BATCHES || stars_covered())
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
	const float scale = layout->playfield[2] / l3d_field_w();
	const float apex_x = player[0].x + 7.0f - l3d_field_x();  // playfield column and row of the cone's apex
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

// Appends the particles (particles3d.h): glowing ones added to what is behind them, smoke and scorch marks
// blended (a scorch mark on water is foam instead, gone in FOAM_FRAMES).
#define FOAM_FRAMES 70.0f

static void add_particle_batches(bool space, int *instance_count, int *batch_count)
{
	for (int kind = 0; kind < P3D_KIND_COUNT && *batch_count < MAX_BATCHES; ++kind)
	{
		if (kind == P3D_DEBRIS)
			continue;  // (lit chunks among the objects: add_debris_batch)
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
			bool foam = false;  // a scorch mark on water: foam spreading where the blast hit it, soon gone
			if (kind == P3D_SCORCH && space)
				continue;  // (nothing to burn: it would hang over deep space)
			if (kind == P3D_SCORCH)
			{
				// Lying on the ground, turned its own way (by its life).
				foam = ground_water_at(p->x, p->y + explodeMove * ahead);
				const float since = (p->age + ahead) / FOAM_FRAMES;
				if (foam && (since >= 1))
					continue;
				const float size = foam ? p->size * (0.7f + 0.7f * sqrtf(SDL_max(0.0f, since))) : p->size;
				// (The quad's x and up along the ground.)
				const float angle = p->life * 2.39996f;
				transform.m[0] = cosf(angle) * size;
				transform.m[2] = sinf(angle) * size;
				transform.m[4] = -sinf(angle) * size;
				transform.m[5] = 0;
				transform.m[6] = cosf(angle) * size;
			}
			else if (kind == P3D_RING)
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
			transform.m[14] = p->y + (p->vy + (p->screen ? 0 : explodeMove)) * age;
			const float height = SDL_max(0.0f, p->height + p->vheight * age) * rgpu_camera.height_scale;
			transform.m[13] = height + (p->air ? l3d_terrain_headroom : stand_lift(transform.m[12], transform.m[14], height, NULL));
			float *instance = instances + *instance_count * 24;
			write_instance(instance, &transform, 1.0f);
			for (int c = 0; c < 3; ++c)
				instance[16 + c] = srgb_to_linear((Uint8)(p->color[c] + (p->end_color[c] - p->color[c]) * t));
			instance[19] = (p->color[3] + (p->end_color[3] - p->color[3]) * t) / 255.0f;
			if (space && kind == P3D_SMOKE)
			{
				// In open space smoke thins out pale and blue-grey (dark, it shows as soot over the nebula and the
				// planet far below).
				static const float pale[3] = { 0.36f, 0.39f, 0.46f };
				for (int c = 0; c < 3; ++c)
					instance[16 + c] = instance[16 + c] * 0.25f + pale[c] * 0.75f;
				instance[19] *= 0.4f;
			}
			if (foam)
			{
				// White foam, fading as it spreads; on the water.
				const float since = SDL_clamp((p->age + ahead) / FOAM_FRAMES, 0.0f, 1.0f);
				instance[16] = 0.78f;
				instance[17] = 0.86f;
				instance[18] = 0.9f;
				instance[19] = 0.6f * (1 - since) * (1 - since);
				instance[13] += 0.8f;
			}
			else if (kind == P3D_SCORCH)
			{
				// Burnt in at once, holding, then fading in its last third; just above the ground.
				instance[19] = p->color[3] / 255.0f * SDL_min(1.0f, (1 - t) / 0.35f);
				instance[13] += 0.8f;
			}
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
		b->billboard_mode = kind == P3D_RING || kind == P3D_SCORCH ? BTBH_GPU_SCENE_BILLBOARD_DISABLED
		                                                           : BTBH_GPU_SCENE_BILLBOARD_FRONT;
		b->unlit_enabled = 1;
		b->transparency_enabled = 1;
		const bool blended = kind == P3D_SMOKE || kind == P3D_SCORCH;
		b->blend_mode = blended ? BTBH_GPU_SCENE_BLEND_ALPHA : BTBH_GPU_SCENE_BLEND_ADDITIVE;
		// Fire and light aren't cut by the ground or the models they burst against (as the game
		// draws explosions over everything); smoke and scorch marks are.
		if (!blended)
			b->depth_compare = BTBH_GPU_SCENE_DEPTH_ALWAYS;
	}
}

static BTBHGPUCustomMesh *jukebox_mesh(J3DShape shape);

// The explosions' debris (P3D_DEBRIS): lit chunks, each its own odd shape, tumbling while they fly,
// casting shadows as the objects do; shrinking away at the end of their life, or gone once down on water.
static void add_debris_batch(int *instance_count, int *batch_count)
{
	if (*batch_count >= MAX_BATCHES)
		return;
	const int first = *instance_count;
	for (int i = 0; i < p3d_particle_count && *instance_count < MAX_INSTANCES; ++i)
	{
		const P3DParticle *p = &p3d_particles[i];
		if (p->kind != P3D_DEBRIS || p->age < 0)
			continue;
		const float t = SDL_clamp(p->age / p->life, 0.0f, 1.0f);
		const float size = p->size * (t > 0.8f ? (1 - t) / 0.2f : 1.0f);
		// Its shape (its life is its own random number): a flake or a lump.
		const float u = p->life * 0.618034f - floorf(p->life * 0.618034f);
		const float sx = size * (0.7f + 0.6f * u), sy = size * (0.35f + 0.4f * (1 - u)), sz = size * (0.8f + 0.3f * u);
		const float age = SDL_max(0.0f, SDL_min(ahead, p->age + ahead));
		// (Down on water it has sunk.)
		if (p->height + p->vheight * age <= 0 && ground_water_at(p->x + p->vx * age, p->y + (p->vy + explodeMove) * age))
			continue;
		const float a = p->turn + (p->height > 0 ? p->spin * age : 0.0f), b = a * 0.73f + u * 3.0f;
		const float ca = cosf(a), sa = sinf(a), cb = cosf(b), sb = sinf(b);
		// Turned about x by a, then about y by b; scaled along its own axes.
		Mat4 transform = mat4_identity();
		transform.m[0] = cb * sx;
		transform.m[1] = 0;
		transform.m[2] = -sb * sx;
		transform.m[4] = sb * sa * sy;
		transform.m[5] = ca * sy;
		transform.m[6] = cb * sa * sy;
		transform.m[8] = sb * ca * sz;
		transform.m[9] = -sa * sz;
		transform.m[10] = cb * ca * sz;
		transform.m[12] = p->x + p->vx * age;
		transform.m[14] = p->y + (p->vy + explodeMove) * age;
		const float height = SDL_max(0.0f, p->height + p->vheight * age) * rgpu_camera.height_scale + sy / 2;
		transform.m[13] = height + (p->air ? l3d_terrain_headroom : stand_lift(transform.m[12], transform.m[14], height, NULL));
		float *instance = instances + *instance_count * 24;
		write_instance(instance, &transform, 1.0f);
		for (int c = 0; c < 3; ++c)
			instance[16 + c] = srgb_to_linear(p->color[c]);
		++*instance_count;
	}
	if (*instance_count == first)
		return;

	BTBHGPUSceneGeometryBatch *b = &batches[(*batch_count)++];
	init_batch(b);
	b->kind = BTBH_GPU_SCENE_GEOMETRY_CUSTOM_MESH;
	b->custom_mesh = jukebox_mesh(J3D_BOX);
	b->first_instance = first;
	b->instance_count = *instance_count - first;
	b->albedo_texture = white_texture;
	b->roughness = 0.7f;
	b->metalness = 0.2f;
}

// Shots and items glow (L3DGlow): additive light around each, in its colour, a little above its
// layer.

static void add_glow_batch(const L3DFrame *frame, const Uint32 colors[256], const float *heights, int *instance_count,
                           int *batch_count)
{
	const int first = *instance_count;
	for (int g = 0; g < frame->glow_count && *instance_count < MAX_INSTANCES; ++g)
	{
		const L3DGlow *glow = &frame->glows[g];
		Mat4 transform = mat4_identity();
		transform.m[0] = transform.m[5] = transform.m[10] = glow->size;
		transform.m[12] = glow->x + (glow->pointer ? l3d_pointer_lead[0] : glow->vx * ahead);
		transform.m[14] = glow->y + (glow->pointer ? l3d_pointer_lead[1] : glow->vy * ahead);
		// As high as what glows: its layer's height in the game's order, on the ground as drawn.
		const float base = layer_base(frame, heights, (L3DLayerType)glow->layer, glow->phase) + 0.5f;
		transform.m[13] = base + (glow->layer == L3D_GROUND_ENEMY ? stand_lift(transform.m[12], transform.m[14], base, NULL) : 0.0f);
		float *instance = instances + *instance_count * 24;
		write_instance(instance, &transform, 1.0f);
		const Uint8 *c = glow->has_rgb ? glow->rgb : (const Uint8 *)&colors[glow->color];
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
#define MERGE_REACH 0.45f        // lights nearer than this share of the smaller one's radius merge
#define MERGE_ENERGY_MAX 8.0f    // a merged light's energy at most (a dozen shots in a stream don't burn white)

typedef struct
{
	float position[3], radius, color[3], energy;
} PointLight;

// The point lights a frame takes from its candidates (importance: each one's), written to lighting; returns how many.
static int merge_point_lights(BTBHGPUSceneLighting *lighting, const PointLight *candidates, const float *importance,
                              int candidate_count)
{
	// The most important first, lights close together merged into one (a stream of shots, a ring of them: each pixel
	// adds up every light the scene has, so their number is what costs; 32 lights took half the frame), at most
	// max_lights (TYR3D_POINT_LIGHTS) of them. A light within MERGE_REACH of its radius from one taken already joins
	// it: the energy adds up, position and colour weighted by energy, the radius grows to reach both.
	static int max_lights = -1;
	if (max_lights < 0)
		max_lights = SDL_clamp(SDL_getenv("TYR3D_POINT_LIGHTS") != NULL ? SDL_atoi(SDL_getenv("TYR3D_POINT_LIGHTS")) : 12, 0,
		                       BTBH_GPU_SCENE_POINT_LIGHTS);
	static int order[512];
	candidate_count = SDL_min(candidate_count, 512);
	for (int i = 0; i < candidate_count; ++i)
	{
		int at = i;
		while (at > 0 && importance[order[at - 1]] < importance[i])
		{
			order[at] = order[at - 1];
			--at;
		}
		order[at] = i;
	}
	PointLight merged[BTBH_GPU_SCENE_POINT_LIGHTS];
	int count = 0;
	for (int n = 0; n < candidate_count; ++n)
	{
		const PointLight *l = &candidates[order[n]];
		int into = -1;
		for (int m = 0; m < count && into < 0; ++m)
		{
			const float dx = merged[m].position[0] - l->position[0], dz = merged[m].position[2] - l->position[2];
			const float reach = MERGE_REACH * SDL_min(merged[m].radius, l->radius);
			if (dx * dx + dz * dz < reach * reach && fabsf(merged[m].position[1] - l->position[1]) < reach)
				into = m;
		}
		if (into < 0)
		{
			if (count < max_lights)
				merged[count++] = *l;
			continue;
		}
		PointLight *m = &merged[into];
		const float total = m->energy + l->energy, a = m->energy / total, b = l->energy / total;
		const float dx = l->position[0] - m->position[0], dz = l->position[2] - m->position[2];
		for (int c = 0; c < 3; ++c)
		{
			m->position[c] = m->position[c] * a + l->position[c] * b;
			m->color[c] = m->color[c] * a + l->color[c] * b;
		}
		m->radius = SDL_max(m->radius, l->radius) + 0.5f * sqrtf(dx * dx + dz * dz);
		m->energy = SDL_min(total, MERGE_ENERGY_MAX);
	}
	for (int n = 0; n < count; ++n)
	{
		const PointLight *l = &merged[n];
		float *out = lighting->point_lights[n];
		memcpy(out, l->position, 3 * sizeof(float));
		out[3] = l->radius;
		memcpy(out + 4, l->color, 3 * sizeof(float));
		out[7] = l->energy;
	}
	return count;
}

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
		const float y = l->y + explodeMove * ahead;
		const float own = l->height * rgpu_camera.height_scale;
		const float height = own + (l->air ? l3d_terrain_headroom : stand_lift(l->x, y, own, NULL));
		const float k = align_scale(height);
		PointLight *out = &candidates[candidate_count];
		out->position[0] = align.on ? align.cx + (l->x - align.cx) * k : l->x;
		out->position[1] = height;
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
		const float x = glow->x + (glow->pointer ? l3d_pointer_lead[0] : glow->vx * ahead);
		const float y = glow->y + (glow->pointer ? l3d_pointer_lead[1] : glow->vy * ahead);
		PointLight *out = &candidates[candidate_count];
		out->position[0] = align.on ? align.cx + (x - align.cx) * k : x;
		out->position[1] = height;
		out->position[2] = align.on ? align.cz + (y - align.cz) * k : y;
		out->radius = (height + glow->size * GLOW_LIGHT_REACH) * k;
		const Uint8 *c = glow->has_rgb ? glow->rgb : (const Uint8 *)&colors[glow->color];
		// The sprite's colour, saturated a little (a dark red shot still throws red light).
		const float peak = SDL_max(SDL_max(c[0], c[1]), SDL_max(c[2], 1));
		for (int i = 0; i < 3; ++i)
			out->color[i] = c[i] / peak;
		out->energy = glow->strength * GLOW_LIGHT_ENERGY;
		importance[candidate_count++] = out->energy * glow->size;
	}

	const int count = merge_point_lights(lighting, candidates, importance, candidate_count);
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

/*
 * The sun's shadow map: an orthographic view along the sun's light over what the window shows of all that
 * takes shadows (the ground and what stands over it, SHADOW_BOTTOM to SHADOW_TOP high, no further than the
 * reach round the playfield; beyond it nothing is shadowed), fitted to that in the light's own plane, the
 * world's x across the map, its texels square: the map has SHADOW_MAP_TEXELS in the region's shape (sides in
 * steps of SHADOW_MAP_STEP, so it is made anew only when the view itself changes: the camera, the window).
 * Its texel's size is quantized and its corner lies on whole texels, so the shadows' edges keep their place
 * while the view moves (shaking) or the box changes. The penumbrae are the renderer's (soft, wider the
 * further a blocker stands above what it shadows: production_model.frag.hlsl).
 */
#define SHADOW_MAP_TEXELS (3072.0f * 1536.0f)
#define SHADOW_MAP_STEP 256
#define SHADOW_REACH_UP 160.0f    // game pixels above the playfield's top edge
#define SHADOW_REACH_SIDE 120.0f  // and beside it
#define SHADOW_BOTTOM (-12.0f)    // world units: the lowest that takes shadows (the terrain's hollows)
#define SHADOW_TOP 110.0f         // game pixels: the highest (the top layers and what stands on them)
#define SHADOW_CASTERS 320.0f     // and what casts them, up to this high

// The window's corners seen on the horizontal plane at the given height, clipped to a rectangle {x0, z0,
// x1, z1} (rays that miss the plane reach the rectangle's far edge); the polygon's points (x, z).
static int view_on_plane(const Camera3D *camera, float height, const float rect[4], float out[8][2])
{
	float points[8][2];
	int n = 0;
	static const float corners[4][2] = { { -1, -1 }, { 1, -1 }, { 1, 1 }, { -1, 1 } };
	for (int corner = 0; corner < 4; ++corner)
	{
		float slope[2], ray[3];
		ndc_slopes(camera, corners[corner], slope);
		for (int i = 0; i < 3; ++i)
			ray[i] = camera->forward[i] + camera->right[i] * slope[0] + camera->up[i] * slope[1];
		float s;
		if (ray[1] < -1e-6f && height < camera->position[1])
			s = (height - camera->position[1]) / ray[1];
		else if (ray[2] < -1e-6f)
			s = (rect[1] - camera->position[2]) / ray[2];
		else
			continue;
		points[n][0] = camera->position[0] + ray[0] * s;
		points[n][1] = SDL_max(camera->position[2] + ray[2] * s, rect[1]);
		++n;
	}
	// Clipped to each of the rectangle's edges in turn (Sutherland-Hodgman).
	for (int edge = 0; edge < 4; ++edge)
	{
		const int axis = edge & 1;               // x, z, x, z
		const float limit = rect[edge];
		const float sign = edge < 2 ? 1.0f : -1.0f;  // inside: >= the near edges, <= the far ones
		float kept[8][2];
		int m = 0;
		for (int i = 0; i < n && m < 7; ++i)
		{
			const float *a = points[i], *b = points[(i + 1) % n];
			const bool in_a = (a[axis] - limit) * sign >= 0, in_b = (b[axis] - limit) * sign >= 0;
			if (in_a)
			{
				kept[m][0] = a[0];
				kept[m][1] = a[1];
				++m;
			}
			if (in_a != in_b)
			{
				const float t = (limit - a[axis]) / (b[axis] - a[axis]);
				kept[m][0] = a[0] + (b[0] - a[0]) * t;
				kept[m][1] = a[1] + (b[1] - a[1]) * t;
				++m;
			}
		}
		memcpy(points, kept, sizeof(kept[0]) * (size_t)m);
		n = m;
	}
	memcpy(out, points, sizeof(points[0]) * (size_t)n);
	return n;
}

static void shadow_view_projection(const Camera3D *camera, float out[16], int size[2])
{
	const float length = sqrtf(sun_direction[0] * sun_direction[0] + sun_direction[1] * sun_direction[1] +
	                           sun_direction[2] * sun_direction[2]);
	const float forward[3] = { sun_direction[0] / length, sun_direction[1] / length, sun_direction[2] / length };
	// right: the world's x across the light; up = forward x right (the handedness the culling expects).
	float right[3] = { 1.0f - forward[0] * forward[0], -forward[0] * forward[1], -forward[0] * forward[2] };
	float right_length = sqrtf(right[0] * right[0] + right[1] * right[1] + right[2] * right[2]);
	if (right_length < 1e-3f)
	{
		// (A light along x: the world's z across it instead.)
		right[0] = -forward[2] * forward[0];
		right[1] = -forward[2] * forward[1];
		right[2] = 1.0f - forward[2] * forward[2];
		right_length = sqrtf(right[0] * right[0] + right[1] * right[1] + right[2] * right[2]);
	}
	for (int i = 0; i < 3; ++i)
		right[i] /= right_length;
	const float up[3] = {
		forward[1] * right[2] - forward[2] * right[1],
		forward[2] * right[0] - forward[0] * right[2],
		forward[0] * right[1] - forward[1] * right[0],
	};

	// What takes shadows, in the light's frame: its extent across (u, v) and along the light; what casts them
	// stands further towards the light, up to SHADOW_CASTERS high.
	const float reach[4] = { l3d_field_x() - SHADOW_REACH_SIDE, -SHADOW_REACH_UP, l3d_field_x() + l3d_field_w() + SHADOW_REACH_SIDE,
	                         L3D_PLAYFIELD_H + SHADOW_REACH_SIDE };
	const float heights[2] = { SHADOW_BOTTOM, SHADOW_TOP * rgpu_camera.height_scale };
	const float rise = -forward[1] > 0.05f ? 1.0f / -forward[1] : 20.0f;  // along the light per unit of height
	float lo[2] = { INFINITY, INFINITY }, hi[2] = { -INFINITY, -INFINITY }, nearest = INFINITY, furthest = -INFINITY;
	for (int h = 0; h < 2; ++h)
	{
		float points[8][2];
		const int n = view_on_plane(camera, heights[h], reach, points);
		for (int i = 0; i < n; ++i)
		{
			const float p[3] = { points[i][0], heights[h], points[i][1] };
			const float u = right[0] * p[0] + right[1] * p[1] + right[2] * p[2];
			const float v = up[0] * p[0] + up[1] * p[1] + up[2] * p[2];
			const float d = forward[0] * p[0] + forward[1] * p[1] + forward[2] * p[2];
			lo[0] = SDL_min(lo[0], u);
			hi[0] = SDL_max(hi[0], u);
			lo[1] = SDL_min(lo[1], v);
			hi[1] = SDL_max(hi[1], v);
			nearest = SDL_min(nearest, d - (SHADOW_CASTERS * rgpu_camera.height_scale - heights[h]) * rise);
			furthest = SDL_max(furthest, d);
		}
	}
	if (!(lo[0] < hi[0]) || !(lo[1] < hi[1]))
	{
		// (Nothing of it in view: the reach itself.)
		lo[0] = reach[0], hi[0] = reach[2], lo[1] = reach[1], hi[1] = reach[3];
		nearest = -1000.0f, furthest = 1000.0f;
	}

	// The map in the region's shape (and a margin round it); square texels fitting it, their size quantized; the
	// box's corner on whole texels.
	const float margin = 4.0f;
	const float extent[2] = { hi[0] - lo[0] + 2 * margin, hi[1] - lo[1] + 2 * margin };
	const float aspect = SDL_clamp(extent[0] / extent[1], 0.25f, 4.0f);
	size[0] = SDL_clamp((int)(sqrtf(SHADOW_MAP_TEXELS * aspect) / SHADOW_MAP_STEP + 0.5f), 2, 32) * SHADOW_MAP_STEP;
	size[1] = SDL_clamp((int)(SHADOW_MAP_TEXELS / size[0] / SHADOW_MAP_STEP + 0.5f), 2, 32) * SHADOW_MAP_STEP;
	float texel = SDL_max(extent[0] / size[0], extent[1] / size[1]);
	texel = ceilf(texel * 512.0f) / 512.0f;
	const float u0 = floorf(((lo[0] + hi[0]) / 2 - texel * size[0] / 2) / texel) * texel;
	const float v0 = floorf(((lo[1] + hi[1]) / 2 - texel * size[1] / 2) / texel) * texel;
	const float near_plane = nearest - 8.0f, far_plane = furthest + 8.0f;

	// NDC x = 2 (u - u0) / (W texel) - 1, y likewise, depth = (d - near) / (far - near); column-major.
	const float su = 2.0f / (size[0] * texel), sv = 2.0f / (size[1] * texel), sd = 1.0f / (far_plane - near_plane);
	memset(out, 0, sizeof(float) * 16);
	for (int i = 0; i < 3; ++i)
	{
		out[i * 4 + 0] = right[i] * su;
		out[i * 4 + 1] = up[i] * sv;
		out[i * 4 + 2] = forward[i] * sd;
	}
	out[12] = -u0 * su - 1.0f;
	out[13] = -v0 * sv - 1.0f;
	out[14] = -near_plane * sd;
	out[15] = 1.0f;
}

#define LIGHT_CEILING 1.0f  // the luminance the point lights ease out under (scene_lighting)

// The sun and the sky: models are lit by them; layers and volumetric sprites are unlit. The sun is
// strong against the sky, as in the sprites' own shading: lit from the upper left, with clear
// highlights and shadows.
// level: a level's scene (its own sunlight, by its climate).
static void scene_lighting(BTBHGPUSceneLighting *lighting, const Camera3D *camera, bool shadows, bool level)
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
	// The shots' and explosions' lights ease out under this luminance (TYR3D_LIGHT_CEILING; 0 none): a stream of
	// shots over pale ice or snow lit it white (3:10's ground, 8 % of the screen pure white).
	static float light_ceiling = -1.0f;
	if (light_ceiling < 0.0f)
		light_ceiling = SDL_getenv("TYR3D_LIGHT_CEILING") != NULL ? SDL_max((float)SDL_atof(SDL_getenv("TYR3D_LIGHT_CEILING")), 0.0f)
		                                                          : LIGHT_CEILING;
	lighting->point_light_ceiling = light_ceiling;
	// A level's own sunlight, by its climate (b3d_weather): cold over the ice, the lava's glow, desert sun.
	if (level && settings3d.effects)
	{
		static const float climate[][3] = {
			[B3D_WEATHER_SNOW] = { 0.86f, 0.95f, 1.08f },
			[B3D_WEATHER_EMBERS] = { 1.1f, 0.86f, 0.7f },
			[B3D_WEATHER_SAND] = { 1.06f, 0.97f, 0.84f },
		};
		const B3DWeather w = b3d_weather();
		if (w == B3D_WEATHER_SNOW || w == B3D_WEATHER_EMBERS || w == B3D_WEATHER_SAND)
		{
			lighting->directional_red *= climate[w][0];
			lighting->directional_green *= climate[w][1];
			lighting->directional_blue *= climate[w][2];
		}
	}
	set_environment(lighting);
	const char *energies = SDL_getenv("TYR3D_LIGHTING");
	float sky_fill = SKY_FILL;
	if (energies != NULL)
		sscanf(energies, "%f,%f", &lighting->directional_energy, &sky_fill);
	for (int i = 0; i < 27; ++i)
		lighting->irradiance_sh[i] *= sky_fill;
	if (shadows)
	{
		int size[2];
		shadow_view_projection(camera, lighting->directional_shadow_view_projection, size);
		btbh_gpu_window_scene_set_directional_shadow_size(window, (uint32_t)size[0], (uint32_t)size[1]);
		lighting->directional_shadow_enabled = 1;
		// The sun's apparent size, how soft its shadows grow with the height of what casts them (1: the
		// renderer's BTBH_SUN_PENUMBRA; TYR3D_SHADOW_SOFTNESS=<n> for tuning, 0 sharp).
		static float softness = -1;
		if (softness < 0)
			softness = SDL_getenv("TYR3D_SHADOW_SOFTNESS") != NULL ? SDL_max(0.0f, (float)SDL_atof(SDL_getenv("TYR3D_SHADOW_SOFTNESS"))) : 1.0f;
		lighting->directional_shadow_softness = softness;
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

/*
 * Screen-space ambient occlusion (the 3D setting Ambient Occlusion: [tyrian3d] ssao, TYR3D_SSAO=0/1): contact shading
 * where things meet and in the hollows, worked out by the renderer from the opaque surfaces' depth and normals and laid
 * over them before the see-through ones are drawn (production_ssao*.frag.hlsl), so clouds, smoke and glows keep their
 * light. It darkens all of a surface's light but its glow, the pixel art's too (the contact mode), from what stands within
 * SSAO_RADIUS world units of it (unit: world units per game pixel; a level's 1). How each batch takes part is its
 * ssao_mode: flat layers take it but cast none (they would darken what lies round their edges, planes apart), painted
 * sprites and deep space neither, procedural water never takes it.
 * TYR3D_SSAO_TUNE=<radius>,<intensity>,<power>,<bias> (game pixels) and TYR3D_SSAO_DEBUG=1 (the occlusion alone, grey)
 * for tuning; TYR3D_SSAO_DEBUG=2 leaves it out of every other scene drawn (before and after in one run).
 */
#define SSAO_RADIUS 14.0f
#define SSAO_INTENSITY 3.5f
#define SSAO_POWER 1.0f
#define SSAO_BIAS 0.05f

static void scene_ssao(BTBHGPUScenePost *post, float unit)
{
	if (!settings3d.ssao)
		return;
	static float tune[4] = { -1, -1, -1, -1 };
	static int debug = -1;
	if (debug < 0)
	{
		tune[0] = SSAO_RADIUS, tune[1] = SSAO_INTENSITY, tune[2] = SSAO_POWER, tune[3] = SSAO_BIAS;
		if (SDL_getenv("TYR3D_SSAO_TUNE") != NULL)
			sscanf(SDL_getenv("TYR3D_SSAO_TUNE"), "%f,%f,%f,%f", &tune[0], &tune[1], &tune[2], &tune[3]);
		for (int i = 0; i < 4; ++i)
			tune[i] = SDL_max(tune[i], 0.0f);
		debug = SDL_getenv("TYR3D_SSAO_DEBUG") != NULL ? SDL_clamp(SDL_atoi(SDL_getenv("TYR3D_SSAO_DEBUG")), 0, 2) : 0;
	}
	// (TYR3D_SSAO_DEBUG=2: every other scene drawn without it, to compare in one run.)
	static Uint32 scenes = 0;
	if (debug == 2 && (scenes++ & 1) != 0)
		return;
	post->ssao_enabled = 1;
	post->ssao_contact = 1;
	post->ssao_radius = SDL_max(tune[0] * unit, 0.0001f);
	post->ssao_intensity = SDL_max(tune[1], 0.0001f);
	post->ssao_power = SDL_max(tune[2], 0.0001f);
	post->ssao_bias = SDL_max(tune[3] * unit, 0.0001f);
	post->ssao_debug_view = debug == 1;
}

// The fork's radiance cascades (holographic): light from everything that glows spreads over the
// playfield and bounces off the ground and the models, on top of the scene's own lighting (the
// fork's additive mode; the pixel art takes the light rather than giving it, see present_3d).
// With the Effects setting; TYR3D_RC=off|low|high (default low).
static BTBHGPUSceneRadianceCascadesTier radiance_cascades_tier(void)
{
	static int tier = -1;
	if (tier < 0)
	{
		const char *value = SDL_getenv("TYR3D_RC");
		tier = value != NULL && (SDL_strcasecmp(value, "off") == 0 || strcmp(value, "0") == 0) ? BTBH_GPU_SCENE_RC_OFF
		     : value != NULL && SDL_strcasecmp(value, "high") == 0 ? BTBH_GPU_SCENE_RC_HIGH : BTBH_GPU_SCENE_RC_LOW;
	}
	return settings3d.effects ? (BTBHGPUSceneRadianceCascadesTier)tier : BTBH_GPU_SCENE_RC_OFF;
}

// The field: square, a power of two (as the holographic cascades need), covering the playfield
// and what the camera sees above it, without occluders.
#define RC_CELLS 128
#define RC_CELL 4.0f  // world units (game pixels)

static void add_radiance_cascades(BTBHGPUScenePost *post)
{
	const BTBHGPUSceneRadianceCascadesTier tier = radiance_cascades_tier();
	if (tier == BTBH_GPU_SCENE_RC_OFF)
		return;
	static float samples[RC_CELLS * RC_CELLS * 2];
	static bool filled = false;
	if (!filled)
	{
		for (int i = 0; i < RC_CELLS * RC_CELLS; ++i)
		{
			samples[i * 2] = 1000000.0f;
			samples[i * 2 + 1] = 0.0f;
		}
		filled = true;
	}
	static float intensity = -1;
	if (intensity < 0)
		intensity = SDL_getenv("TYR3D_RC_INTENSITY") != NULL ? (float)SDL_atof(SDL_getenv("TYR3D_RC_INTENSITY")) : 1.0f;
	BTBHGPUSceneRadianceCascades *rc = &post->radiance_cascades;
	rc->tier = tier;
	rc->backend = BTBH_GPU_SCENE_RC_BACKEND_HOLOGRAPHIC;
	rc->indirect_intensity = SDL_clamp(intensity, 0.0f, 2.0f);
	rc->hero_omni_emitter_index = -1;
	rc->additive = 1;  // the scene's own lighting stays; glows add their light
	rc->occlusion_cascade_count = 1;
	BTBHGPUSceneRadianceCascadesOcclusionCascade *field = &rc->occlusion_cascades[0];
	field->origin_world_x = floorf((l3d_field_x() + l3d_field_w() / 2.0f - RC_CELLS * RC_CELL / 2) / RC_CELL) * RC_CELL;
	field->origin_world_z = floorf((L3D_PLAYFIELD_H / 2.0f - RC_CELLS * RC_CELL / 2) / RC_CELL) * RC_CELL;
	field->cell_size = RC_CELL;
	field->width = RC_CELLS;
	field->height = RC_CELLS;
	field->revision = 1;
	field->samples = samples;
}

// Spotlight levels (the game draws them dark but for a cone ahead of the ship): really dark, lit
// by the ship's lamp (a spot light), explosions and shots; the brightest pixels glow on. With the
// Effects setting; TYR3D_DARK_LIGHTING=0: the game's cone as an overlay instead (build_spotlight).
#define DARK_LEVEL_DARKNESS 0.95f
#define DARK_LEVEL_GLOW 0.7f  // linear luminance

static bool dark_lighting(void)
{
	static int on = -1;
	if (on < 0)
		on = SDL_getenv("TYR3D_DARK_LIGHTING") == NULL || SDL_atoi(SDL_getenv("TYR3D_DARK_LIGHTING")) != 0;
	return on && settings3d.effects;
}

static void present_3d(const SDL_Surface *hud, const L3DFrame *frame, const SDL_Rect *dst)
{
	BTBHGPUWindowReport window_frame;
	if (!begin_frame(&window_frame))
		return;

	Uint32 colors[256];
	frame_colors(frame, colors);
	// The colours the map's tiles are coloured with (and dimmed by tile_fade and tile_filter_dim).
	Uint32 tile_colors[256];
	tile_fade = 1.0f;
	// The game's darkening filter (a level comes up from dark by it): how much darker its colours are, in linear light.
	filter_dim = 1.0f;
	if (frame->filter_brightness != -99 && frame->filter_brightness < 0)
		filter_dim = (float)SDL_min(linear_ratio(colors, rgb_palette), 1.0);
	// The brightness filter: the tiles in the colours without it, dimmed by it (tile_filter_dim).
	const bool fading = uniform_fade(&tile_fade);
	filter_colors(frame->filter_hue, -99, fading ? palette_fade_full : rgb_palette, tile_colors);
	tile_filter_dim = 1.0f;
	if (frame->filter_brightness != -99)
	{
		Uint32 without[256];
		filter_colors(frame->filter_hue, -99, rgb_palette, without);
		tile_filter_dim = (float)SDL_min(linear_ratio(colors, without), 1.0);
	}
	// The HD tiles are coloured when the colours have held (hd_tile_page, terrain_ring_row).
	static Uint32 last_tile_colors_hash = 0;
	const Uint32 tile_colors_hash = hash_colors(tile_colors);
	colors_stable = tile_colors_hash == last_tile_colors_hash ? SDL_min(colors_stable + 1, 1000) : 0;
	last_tile_colors_hash = tile_colors_hash;
	hd_budget = HD_ROWS_PER_FRAME;

	// A frame the game has just captured, or one of those shown between ticks (rgpu_present_3d_ahead),
	// which reuse what was made of the frame.
	static Uint32 presented_frame = 0;
	const bool new_frame = presented_frame != l3d_frame_number || (ahead == 0 && !menu.on);
	b3d_clouds = clouds_enabled();  // blended backgrounds of clouds aren't composed
	cloud_frame = frame;
	{
		// The backgrounds as terrain where their maps have one. The ground: in its colours (a filter
		// as its colours, without its waver), over stars only where they show through its holes alone
		// (version 2); the backgrounds over it are then their tiles, not composed with it (the blended
		// background 2 in the colours the blend gives it). Backgrounds 2 and 3 over a flat ground: as
		// for the relief, not composed nor filtered.
		frame_terrains[1] = m3d_enabled ? b3d_terrain(1) : NULL;
		if (frame_terrains[1] != NULL && frame->space && !frame_terrains[1]->holes)
			frame_terrains[1] = NULL;
		if (ground_covered(frame))
			frame_terrains[1] = NULL;
		b3d_terrain_ground = frame_terrains[1] != NULL;
		lift_ground = NULL;
		lift_terrain = NULL;
		for (int i = 0; i < frame->background_count && frame_terrains[1] != NULL; ++i)
			if (frame->backgrounds[i].set == 1)
			{
				lift_ground = &frame->backgrounds[i];
				lift_terrain = frame_terrains[1];
			}
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
		// Background 2 covering the ground with a terrain of its own is the ground (ICESECRET's ice).
		const L3DBackground *cover = covering_ground(frame);
		if (cover != NULL && frame_terrains[cover->set] != NULL)
		{
			lift_ground = cover;
			lift_terrain = frame_terrains[cover->set];
		}
		if (SDL_getenv("TYR3D_LOG_GROUND_MODE") != NULL)
			log_ground(frame, composed_now);
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
		for (int l = 0; l < frame->layer_count; ++l)
			layer_speed[l] = frame->layers[l].type == L3D_EXPLOSION ? explodeMove : 0;
		for (int i = 0; i < frame->background_count; ++i)
			layer_speed[frame->backgrounds[i].layer] = background_speed[frame->backgrounds[i].set & 3];
	}

	const float logical_w = (float)window_frame.logical_width, logical_h = (float)window_frame.logical_height;
	const Layout3D layout = layout_3d(logical_w, logical_h, dst);
	CanvasQuad quads[MAX_CANVAS_QUADS];
	const int quad_count = layout_quads(&layout, dst, quads);
	build_modern_hud(logical_w, logical_h, &layout);

	if (menu.on)
	{
		// The menu's texts where its boxes are (layout_quads shows the screen's playfield columns at
		// game x 24 and on, the original's place, wherever on the wide playfield the 2D view was).
		menu.map[2] = layout.playfield[2] / l3d_field_w();
		menu.map[0] = layout.playfield[0] + (L3D_PLAYFIELD_X - l3d_field_x()) * menu.map[2];
		menu.map[1] = layout.playfield[1];
		menu.map[3] = layout.playfield[3] / L3D_PLAYFIELD_H;
	}
	if (new_frame || menu.on)
	{
		build_hud(hud, frame, layout.split);
		btbh_gpu_texture_update_rgba8(screen_texture, (const uint8_t *)screen_rgba, 0, 0, SCREEN_W, SCREEN_H);
		hud_panel_hd(hud);
	}
	playfield_text_quads(&layout);
	debug_status_quads(logical_w, logical_h);

	// A screen over the level in the modern UI's style: over the scene, its glass showing the scene
	// blurred (made again only when the scene changes: the game is halted under it).
	bool blur_scene = false;
	if (menu.on && menu.modern)
	{
		const Uint64 key = ((Uint64)l3d_frame_number << 24) ^ ((Uint64)settings3d.shadows << 1) ^ ((Uint64)settings3d.effects << 2) ^
		                   ((Uint64)settings3d.models << 3) ^ ((Uint64)settings3d.camera << 4) ^ ((Uint64)settings3d.ssao << 8) ^
		                   ((Uint64)settings3d.hud_modern << 9) ^ ((Uint64)(int)logical_w << 10) ^ ((Uint64)(int)logical_h << 40);
		if (scene_blur_targets(logical_w, logical_h))
		{
			blur_scene = !scene_blur_valid || key != scene_blur_key;
			scene_blur_key = key;
			frost_texture = scene_blur[SCENE_BLUR_STEPS - 1];
			cover_map[0] = cover_map[1] = 0;
			cover_map[2] = logical_w;
			cover_map[3] = logical_h;
			blur_ready = true;
		}
		const UIView view = { .w = logical_w, .h = logical_h, .pixel = 1.0f / text_density,
		                      .playfield = { layout.playfield[0], layout.playfield[1], layout.playfield[2], layout.playfield[3] },
		                      .menu_over = true };
		ui_build_screen(&view);
		static int software_pointer = -1;
		if (software_pointer < 0)
			software_pointer = SDL_getenv("TYR3D_SOFTWARE_POINTER") != NULL;
		float pointer_x, pointer_y;
		if (software_pointer && mouse_pointer_window(&pointer_x, &pointer_y))
			ui_build_pointer(&view, pointer_x, pointer_y, mouseCursor);
	}

	// Levels with a special view, as JE_starShowVGA shows them.
	const bool upside_down = starShowVGASpecialCode == 1;
	const bool spotlight = starShowVGASpecialCode == 2 && processorType >= 2 && !dark_lighting() && !l3d_sideways;
	if (spotlight && new_frame)
		build_spotlight(&layout, logical_w, logical_h);

	if (slot_count == 0)
	{
		present_canvas(quads, quad_count, spotlight, true, &window_frame);
		blur_ready = false;
		return;
	}

	// Playfield rectangle in NDC (y up) of the whole window. Seen from the side, the view turned
	// a quarter is fitted to the window (beside the panel) from a little way in on the left: the
	// playfield's bottom edge there, as tall as the window, and the window's rest ahead of it (a
	// view as wide as the window, so the far right still looks down onto the level).
	float px0 = layout.playfield[0], px1 = layout.playfield[0] + layout.playfield[2];
	float py0 = layout.playfield[1], py1 = layout.playfield[1] + layout.playfield[3];
	const bool sideways = l3d_sideways && !menu.on;
	if (sideways)
	{
		const float room_w = layout.panel[2] > 0 ? layout.panel[0] : logical_w;
		px0 = room_w * 0.06f;
		px1 = room_w;
		py0 = 0;
		py1 = logical_h;
	}
	const float ndc_rect[4] = {
		px0 / logical_w * 2 - 1,
		1 - py1 / logical_h * 2,
		px1 / logical_w * 2 - 1,
		1 - py0 / logical_h * 2,
	};
	// (The view's own aspect: seen from the side, the rectangle's height is its width.)
	const float viewport_aspect = sideways ? (py1 - py0) / (px1 - px0) : (px1 - px0) / (py1 - py0);

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

	// The view shakes (p3d_shake): its picture moves a little, a new way every frame (the mouse still finds
	// the game's points in the steady view).
	float shaken[4];
	memcpy(shaken, ndc_rect, sizeof(shaken));
	if (p3d_shake > 0 && settings3d.effects)
	{
		const Uint32 k = hash32(l3d_frame_number * 2654435761u);
		const float amount = p3d_shake * p3d_shake * 0.012f;
		const float sx = (hash_unit(k) - 0.5f) * 2 * amount, sy = (hash_unit(k + 1) - 0.5f) * 2 * amount;
		shaken[0] += sx, shaken[2] += sx;
		shaken[1] += sy, shaken[3] += sy;
	}
	const Camera3D camera = fit_camera(reference_height, viewport_aspect, shaken, upside_down, sideways);
	set_alignment(&camera, reference_height);
	shown_view = (ShownView){ true, fit_camera(reference_height, viewport_aspect, ndc_rect, upside_down, sideways),
	                          reference_height, logical_w, logical_h, upside_down };
	bool composed[L3D_MAX_BACKGROUNDS];
	b3d_composed_backgrounds(frame, composed);
	// What stands on the ground stands on it as drawn, the layers' objects in the game's order
	// (stand_lift, layer_base): with the planes' heights and the camera known.
	const Uint64 lift_start = SDL_GetPerformanceCounter();
	setup_stand(frame, composed, heights);
	compute_object_lifts(frame, heights, upside_down);
	hide_in_solids(frame, heights, upside_down);
	profile_lift_ticks += SDL_GetPerformanceCounter() - lift_start;
	add_outside_shade(&camera, reference_height, layout.panel[2] > 0 ? layout.panel[0] : logical_w, logical_w, logical_h);
	prepare_tile_atlas();

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
		b->ssao_mode = background_layer(frame->layers[l].type) ? BTBH_GPU_SCENE_SSAO_RECEIVE_ONLY : BTBH_GPU_SCENE_SSAO_NONE;
		if (background_layer(frame->layers[l].type))
			set_glints(b, layer_water);
	}

	add_composed_batches(frame, composed, &camera, heights, colors, new_frame, &instance_count, &batch_count);
	add_background_batches(frame, composed, &camera, heights, tile_colors, &instance_count, &batch_count);
	const int first_star_batch = batch_count;
	add_star_batch(frame, composed, &camera, heights, colors, &instance_count, &batch_count);
	// (Deep space lies far under all that casts shadows: none falls on it.)
	const int first_space_batch = batch_count;
	add_planet_batch(frame, &camera, heights, &instance_count, &batch_count);
	add_nebula_batch(frame, &camera, heights, &instance_count, &batch_count);
	add_meteor_batch(frame, &camera, heights, &instance_count, &batch_count);
	add_deep_star_batch(frame, &camera, heights, colors, &instance_count, &batch_count);
	const int end_space_batch = batch_count;
	add_cloud_batches(heights, &camera, new_frame, &instance_count, &batch_count);
	add_weather_batch(frame, &camera, heights, &instance_count, &batch_count);
	add_bird_batch(frame, &camera, heights, &instance_count, &batch_count);
	const int first_object_batch = batch_count;
	add_object_batches(frame, colors, upside_down, &instance_count, &batch_count);
	add_volume_batches(frame, &instance_count, &batch_count);
	if (settings3d.effects)
		add_debris_batch(&instance_count, &batch_count);
	log_clipping(frame);  // TYR3D_LOG_CLIP

	// Shadows: objects (models and volumetric sprites) cast the sun's shadow; the unlit surfaces
	// (layers, background tiles, volumetric sprites) darken in it, lit models are shaded by it. The
	// see-through ones (clouds, weather), drawn over one another many times, through the plain filter
	// (unlit_enabled 3): the soft one's search would cost too much there.
	static Uint8 casts_shadow[MAX_BATCHES];
	const bool shadows = shadows_enabled();
	for (int i = 0; i < batch_count; ++i)
	{
		casts_shadow[i] = shadows && (i >= first_object_batch || terrain_batch[i]);
		if (shadows && batches[i].unlit_enabled == 1 && (i < first_space_batch || i >= end_space_batch))
			batches[i].unlit_enabled = batches[i].transparency_enabled ? 3 : 2;
	}

	// Particles last: they neither cast nor receive shadows.
	const int first_particle_batch = batch_count;
	if (settings3d.effects)
	{
		add_particle_batches(frame->space && !stars_covered(), &instance_count, &batch_count);
		add_glow_batch(frame, colors, heights, &instance_count, &batch_count);
	}
	for (int i = first_particle_batch; i < batch_count; ++i)
		casts_shadow[i] = 0;
	// Dark levels: what the shader's darkness doesn't reach (see-through unlit surfaces: clouds,
	// smoke) darkens as much.
	if (starShowVGASpecialCode == 2 && processorType >= 2 && dark_lighting())
		for (int i = 0; i < first_particle_batch; ++i)
			if (batches[i].unlit_enabled != 0 && batches[i].transparency_enabled)
			{
				const float keep = 1.0f - DARK_LEVEL_DARKNESS * 0.8f;
				batches[i].albedo_red = (Uint8)(batches[i].albedo_red * keep);
				batches[i].albedo_green = (Uint8)(batches[i].albedo_green * keep);
				batches[i].albedo_blue = (Uint8)(batches[i].albedo_blue * keep);
			}
	// With the radiance cascades, the pixel art (unlit) takes their light instead of giving it:
	// the light comes from what glows (particles, glows, emissive parts of models).
	if (radiance_cascades_tier() != BTBH_GPU_SCENE_RC_OFF)
		for (int i = 0; i < first_particle_batch; ++i)
			if (batches[i].unlit_enabled != 0)
				batches[i].rc_receiver = 1;

	// The ambient occlusion: none in the stars and deep space, the clouds, weather and gulls (painted, see-through), the
	// particles and glows.
	for (int i = first_star_batch; i < batch_count; ++i)
		if (i < first_object_batch || i >= first_particle_batch)
			batches[i].ssao_mode = BTBH_GPU_SCENE_SSAO_NONE;

	BTBHGPUSceneLighting lighting;
	scene_lighting(&lighting, &shown_view.camera, shadows, true);  // (the steady view: the shadows don't shake)
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
		if (dark_lighting())
		{
			// The level is dark: the lamp lights it, explosions and shots light their
			// surroundings, the brightest pixels (lava, lamps) glow on; the models keep a little
			// of the sky's light.
			lighting.unlit_darkness = DARK_LEVEL_DARKNESS;
			lighting.unlit_glow_threshold = DARK_LEVEL_GLOW;
			lighting.spot_energy = 2.6f;
			lighting.spot_range = 280.0f;
			lighting.spot_falloff = 1.2f;
			lighting.directional_energy *= 1.0f - DARK_LEVEL_DARKNESS;
			lighting.ambient_energy *= 1.0f - DARK_LEVEL_DARKNESS;
			for (int i = 0; i < 27; ++i)
				lighting.irradiance_sh[i] *= 1.0f - DARK_LEVEL_DARKNESS;
		}
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
	scene_ssao(&post, 1.0f);
	add_radiance_cascades(&post);

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
		blur_ready = false;
		return;
	}
	if (blur_scene)
	{
		BTBHGPUTextureReport capture_report;
		scene_capture = btbh_gpu_window_capture_pending_scene_texture(window, &capture_report);
		if (scene_capture == NULL)
			scene_blur_valid = false;
	}
	if (SDL_getenv("TYR3D_LOG_RC") != NULL && ahead == 0 && l3d_frame_number % 100 == 0)
		printf("rc: requested %d active %d backend %d fallback %d, %ux%u\n", scene_report.radiance_cascades.requested_tier,
		       scene_report.radiance_cascades.active_tier, scene_report.radiance_cascades.active_backend,
		       scene_report.radiance_cascades.fallback_reason, scene_report.radiance_cascades.internal_width,
		       scene_report.radiance_cascades.internal_height);

	present_canvas(quads, quad_count, spotlight, false, &window_frame);
	blur_ready = false;
}

/* --- The store's ship ---------------------------------------------------------------------- */

/*
 * A box of the store's screen as a scene (see RGPUShowcase): its picture lies on the ground, seen
 * from straight above as the box shows it, models over it lit by the sun and casting their shadows.
 *
 * World: the box spans the playfield's width on the ground (fit_camera with no tilt fits that
 * width exactly at height 0), its bottom on the playfield's bottom edge.
 */
// The placement of a showcase object (its position and turn, before its model's own): on its
// parent's, if it has one.
static Mat4 showcase_placement(const RGPUShowcaseObject *o, const Mat4 *parent, float x, float z, float k)
{
	const Mat4 chain[] = {
		parent != NULL ? mat4_translation(o->x * k, o->height * k, o->y * k) : mat4_translation(x, o->height * k, z),
		mat4_rotation(1, -o->yaw),
		mat4_rotation(0, o->pitch),
		mat4_rotation(2, -o->roll),
	};
	const Mat4 local = mat4_chain((int)COUNTOF(chain), chain);
	return parent != NULL ? mat4_mul(parent, &local) : local;
}

// A model at a placement: footprint in world units, centred on its bounds; or 0, its own size in
// screen pixels (times k, world units per screen pixel) at its own origin.
static void add_showcase_model(int model_index, const Mat4 *placement, float footprint, float k, const Uint32 colors[256],
                               int *instance_count, int *batch_count)
{
	const LoadedModel *loaded = model_index >= 0 && model_index < m3d_model_count ? get_model(model_index) : NULL;
	if (loaded == NULL || loaded->footprint <= 0 || *batch_count >= MAX_BATCHES || *instance_count >= MAX_INSTANCES)
		return;
	const M3DModel *model = &m3d_models[model_index];
	const bool centred = footprint > 0;
	const float scale = centred ? footprint / loaded->footprint : (model->size > 0 ? model->size / loaded->footprint : 1.0f) * k;
	const Mat4 chain[] = {
		*placement,
		mat4_rotation(1, model->yaw),
		mat4_rotation(0, model->pitch),
		mat4_rotation(2, model->roll),
		mat4_scaling(scale),
		centred ? mat4_translation(-loaded->center[0], -loaded->center[1], -loaded->center[2]) : mat4_identity(),
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
			palette_emission_of(b, c, loaded->palette_index[m]);
		}
		if (b->albedo_alpha < 255)
			b->transparency_enabled = 1;
	}
}

/*
 * What a showcase's scene shows besides models, as a level's 3D view shows it (the weapon simulator's shots without a
 * model, their glows and the missiles' smoke; the store's ship's engines and shield): placed by the screen's pixels,
 * world x = ox + px * k, z = oz + py * k, heights times k (k world units per screen pixel).
 */
// The sprites with volume (RGPUShowcaseObject.model M3D_VOLUME) at their placements, as add_volume_batches draws them:
// their HD volumes where the 4x sheets have them, unlit, shaded by the mesh; those showing the same sprite share a batch.
static void add_showcase_volumes(const RGPUShowcase *show, const Mat4 *placements, int count, float k, const Uint32 colors[256],
                                 int *instance_count, int *batch_count)
{
	const Uint32 colors_hash = hash_colors(colors);
	float tint[3];
	hd_tint(colors, tint);
	const Mat4 scaling = mat4_scaling(k);
	static bool done[160];
	count = SDL_min(count, (int)COUNTOF(done));
	memset(done, 0, sizeof(done));
	for (int i = 0; i < count; ++i)
	{
		const RGPUShowcaseObject *o = &show->objects[i];
		if (done[i] || o->model != M3D_VOLUME || o->sheet == NULL || *batch_count >= MAX_BATCHES)
			continue;
		VolumeSheet *entry = get_volume_sheet(o->sheet, colors, colors_hash);
		HDSheet *hd = get_hd_sheet(o->sheet);
		BTBHGPUCustomMesh *mesh = hd != NULL ? get_hd_mesh(hd, o->sprite, o->large, o->style, 0) : NULL;
		if (mesh == NULL)
		{
			hd = NULL;
			mesh = entry != NULL ? get_volume_mesh(entry, o->sprite, o->large, o->style, 0) : NULL;
		}
		const int first = *instance_count;
		for (int j = i; j < count; ++j)
		{
			const RGPUShowcaseObject *p = &show->objects[j];
			if (done[j] || p->model != M3D_VOLUME || p->sheet != o->sheet || p->sprite != o->sprite || p->large != o->large ||
			    p->style != o->style)
				continue;
			done[j] = true;
			if (mesh == NULL || *instance_count >= MAX_INSTANCES)
				continue;
			const Mat4 world = mat4_mul(&placements[j], &scaling);
			float *instance = instances + *instance_count * 24;
			write_instance_world(instance, &world, 1.0f);
			if (hd != NULL)
				memcpy(instance + 16, tint, sizeof(tint));
			++*instance_count;
		}
		if (*instance_count == first)
			continue;
		BTBHGPUSceneGeometryBatch *b = &batches[(*batch_count)++];
		init_batch(b);
		b->kind = BTBH_GPU_SCENE_GEOMETRY_CUSTOM_MESH;
		b->custom_mesh = mesh;
		b->first_instance = first;
		b->instance_count = *instance_count - first;
		b->albedo_texture = hd != NULL ? hd->texture : entry->texture;
		b->unlit_enabled = 1;
		b->alpha_cutoff = hd != NULL ? 0.1f : 0.5f;
	}
}

// The glows (RGPUShowcaseGlow), as add_glow_batch draws a level's: soft dots added to what is behind them, facing the
// camera.
static void add_showcase_glows(const RGPUShowcase *show, float ox, float oz, float k, const Uint32 colors[256],
                               int *instance_count, int *batch_count)
{
	const int first = *instance_count;
	for (int g = 0; g < show->glow_count && *instance_count < MAX_INSTANCES; ++g)
	{
		const RGPUShowcaseGlow *glow = &show->glows[g];
		Mat4 transform = mat4_identity();
		transform.m[0] = transform.m[5] = transform.m[10] = glow->size * k;
		transform.m[12] = ox + glow->x * k;
		transform.m[13] = glow->height * k + 0.5f;
		transform.m[14] = oz + glow->y * k;
		float *instance = instances + *instance_count * 24;
		write_instance_world(instance, &transform, 1.0f);
		const Uint8 *c = glow->color != 0 ? (const Uint8 *)&colors[glow->color] : glow->rgb;
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

// The particles (particles3d.h) in screen pixels, as add_particle_batches draws a level's in open space: smoke (pale,
// thin) blended, sparks and fire added; turned each its own way.
static void add_showcase_particles(float ox, float oz, float k, int *instance_count, int *batch_count)
{
	for (int kind = 0; kind < P3D_KIND_COUNT && *batch_count < MAX_BATCHES; ++kind)
	{
		if (kind == P3D_DEBRIS || kind == P3D_SCORCH || kind == P3D_RING)
			continue;  // (nothing bursts in the simulator)
		const int first = *instance_count;
		for (int i = 0; i < p3d_particle_count && *instance_count < MAX_INSTANCES; ++i)
		{
			const P3DParticle *p = &p3d_particles[i];
			if (p->kind != kind || p->age < 0)
				continue;
			float t = SDL_clamp(p->age / p->life, 0.0f, 1.0f);
			if (kind == P3D_FIRE)
				t *= t;
			Mat4 transform = mat4_identity();
			const float size = p->size * k;
			transform.m[0] = transform.m[5] = transform.m[10] = size;
			if (kind != P3D_GLOW)
			{
				const float angle = p->life * 2.39996f + p->age * 0.02f;
				transform.m[0] = cosf(angle) * size;
				transform.m[1] = sinf(angle) * size;
				transform.m[4] = -sinf(angle) * size;
				transform.m[5] = cosf(angle) * size;
			}
			transform.m[12] = ox + p->x * k;
			transform.m[13] = SDL_max(0.0f, p->height) * k;
			transform.m[14] = oz + p->y * k;
			float *instance = instances + *instance_count * 24;
			write_instance_world(instance, &transform, 1.0f);
			for (int c = 0; c < 3; ++c)
				instance[16 + c] = srgb_to_linear((Uint8)(p->color[c] + (p->end_color[c] - p->color[c]) * t));
			instance[19] = (p->color[3] + (p->end_color[3] - p->color[3]) * t) / 255.0f;
			if (kind == P3D_SMOKE)
			{
				static const float pale[3] = { 0.36f, 0.39f, 0.46f };
				for (int c = 0; c < 3; ++c)
					instance[16 + c] = instance[16 + c] * 0.25f + pale[c] * 0.75f;
				instance[19] *= 0.4f;
			}
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
		b->albedo_texture = kind == P3D_GLOW ? particle_texture : fire_texture;
		b->billboard_mode = BTBH_GPU_SCENE_BILLBOARD_FRONT;
		b->unlit_enabled = 1;
		b->transparency_enabled = 1;
		b->blend_mode = kind == P3D_SMOKE ? BTBH_GPU_SCENE_BLEND_ALPHA : BTBH_GPU_SCENE_BLEND_ADDITIVE;
		if (kind != P3D_SMOKE)
			b->depth_compare = BTBH_GPU_SCENE_DEPTH_ALWAYS;
	}
}

// The strongest glows light what is near them, as a level's shots do (add_explosion_lights; TYR3D_GLOW_LIGHTS=0 none):
// a little above the picture under them, reaching round them.
static void add_showcase_lights(BTBHGPUSceneLighting *lighting, const RGPUShowcase *show, float ox, float oz, float k,
                                const Uint32 colors[256])
{
	static int glow_lights = -1;
	if (glow_lights < 0)
		glow_lights = SDL_getenv("TYR3D_GLOW_LIGHTS") == NULL || SDL_atoi(SDL_getenv("TYR3D_GLOW_LIGHTS")) != 0;
	if (!glow_lights)
		return;
	// Its glows as candidates, merged and chosen as a level's (merge_point_lights).
	static PointLight candidates[512];
	static float importance[512];
	int candidate_count = 0;
	for (int g = 0; g < show->glow_count && candidate_count < 512; ++g)
	{
		const RGPUShowcaseGlow *glow = &show->glows[g];
		if (glow->strength <= 0.05f || glow->size <= 1.0f)
			continue;
		const float height = glow->height * k * GLOW_LIGHT_LOW;
		PointLight *out = &candidates[candidate_count];
		out->position[0] = ox + glow->x * k;
		out->position[1] = height;
		out->position[2] = oz + glow->y * k;
		out->radius = height + glow->size * k * GLOW_LIGHT_REACH;
		const Uint8 *c = glow->color != 0 ? (const Uint8 *)&colors[glow->color] : glow->rgb;
		const float peak = SDL_max(SDL_max(c[0], c[1]), SDL_max(c[2], 1));
		for (int i = 0; i < 3; ++i)
			out->color[i] = c[i] / peak;
		out->energy = glow->strength * GLOW_LIGHT_ENERGY;
		importance[candidate_count++] = glow->strength * glow->size;
	}
	const int count = merge_point_lights(lighting, candidates, importance, candidate_count);
	lighting->point_light_count = (uint32_t)count;
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
	const Uint8 *pixels = screen_without_texts(screen);
	convert_pixels(pixels, screen_rgba);
	for (int y = 0; y < p->h; ++y)
		for (int x = 0; x < p->w; ++x)
		{
			const int i = (p->y + y) * SCREEN_W + p->x + x;
			picture[y * p->w + x] = rgb_palette[show->backdrop[i]];
			if (pixels[i] == show->transparent[i])
				screen_rgba[i] = 0;
		}
	btbh_gpu_texture_update_rgba8(screen_texture, (const uint8_t *)screen_rgba, 0, 0, SCREEN_W, SCREEN_H);
	btbh_gpu_texture_update_rgba8(showcase_texture, (const uint8_t *)picture, 0, 0, p->w, p->h);
	CanvasQuad quad = whole_screen_quad(dst);
	memcpy(canvas_fade, show->fade, sizeof(canvas_fade));
	hud_quad_count = 0;
	blur_ready = false;
	if (ui_fill_screens())
	{
		// Filling the window's height over its blurred copy (the box's picture where the scene shows).
		static Uint32 whole[SCREEN_W * SCREEN_H];
		for (int i = 0; i < SCREEN_W * SCREEN_H; ++i)
			whole[i] = (screen_rgba[i] >> 24) != 0 ? screen_rgba[i] : rgb_palette[show->backdrop[i]];
		make_blur(whole, (float)window_frame.logical_width, (float)window_frame.logical_height);
		add_surround(dst, (float)window_frame.logical_width, (float)window_frame.logical_height);
		quad.sharp = true;
	}
	screen_text_quads(dst->x, dst->y, dst->w / (float)SCREEN_W, dst->h / (float)SCREEN_H, SCREEN_W, SCREEN_H);

	// The camera: straight down at the box.
	const float logical_w = (float)window_frame.logical_width, logical_h = (float)window_frame.logical_height;
	const float sx = dst->w / (float)SCREEN_W, sy = dst->h / (float)SCREEN_H;
	const float wx0 = dst->x + p->x * sx, wy0 = dst->y + p->y * sy;
	const float wx1 = wx0 + p->w * sx, wy1 = wy0 + p->h * sy;
	const float ndc_rect[4] = { wx0 / logical_w * 2 - 1, 1 - wy1 / logical_h * 2, wx1 / logical_w * 2 - 1, 1 - wy0 / logical_h * 2 };
	const float tilt = rgpu_camera.tilt_degrees;
	rgpu_camera.tilt_degrees = 0;
	const Camera3D camera = fit_camera(0.0f, (wx1 - wx0) / (wy1 - wy0), ndc_rect, false, false);
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
		b->ssao_mode = BTBH_GPU_SCENE_SSAO_RECEIVE_ONLY;
	}

	const int first_model_batch = batch_count;
	enum { MAX_SHOWCASE_OBJECTS = 160 };
	static Mat4 placements[MAX_SHOWCASE_OBJECTS];
	for (int i = 0; i < show->object_count && i < MAX_SHOWCASE_OBJECTS; ++i)
	{
		const RGPUShowcaseObject *o = &show->objects[i];
		const Mat4 *parent = o->parent >= 0 && o->parent < i ? &placements[o->parent] : NULL;
		placements[i] = showcase_placement(o, parent, SHOWCASE_X(o->x), SHOWCASE_Z(o->y), k);
		const float scale = o->scale > 0 ? o->scale : 1.0f;
		if (o->model != M3D_VOLUME)
			add_showcase_model(o->model, &placements[i], o->size * k * scale, k * scale, colors, &instance_count, &batch_count);
	}
	add_showcase_volumes(show, placements, SDL_min(show->object_count, MAX_SHOWCASE_OBJECTS), k, colors, &instance_count,
	                     &batch_count);
	const float ox = SHOWCASE_X(0), oz = SHOWCASE_Z(0);
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
	// The glows and particles last, as a level's: they neither cast nor take shadows.
	const int first_light_batch = batch_count;
	if (settings3d.effects)
	{
		if (show->particles)
			add_showcase_particles(ox, oz, k, &instance_count, &batch_count);
		add_showcase_glows(show, ox, oz, k, colors, &instance_count, &batch_count);
	}
	for (int i = first_light_batch; i < batch_count; ++i)
	{
		casts_shadow[i] = 0;
		batches[i].ssao_mode = BTBH_GPU_SCENE_SSAO_NONE;
	}

	BTBHGPUSceneLighting lighting;
	scene_lighting(&lighting, &camera, shadows, false);
	if (settings3d.effects)
		add_showcase_lights(&lighting, show, ox, oz, k, colors);
	BTBHGPUScenePost post;
	Uint32 render_w, render_h;
	scene_post(&post, &window_frame, &render_w, &render_h);
	scene_ssao(&post, k);

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
	blur_ready = false;
}

/* --- The jukebox's visuals (jukebox3d.h) -------------------------------------------------- */

static BTBHGPUCustomMesh *jukebox_meshes[J3D_SHAPES];
static BTBHGPUTexture *planet_textures[J3D_TEXTURES];

static void forget_jukebox_scene(void)
{
	memset(jukebox_meshes, 0, sizeof(jukebox_meshes));  // (the window's)
	memset(planet_textures, 0, sizeof(planet_textures));
}

static BTBHGPUCustomMesh *jukebox_mesh(J3DShape shape)
{
	if (shape == J3D_GLOW || shape == J3D_RING || shape == J3D_DOT)
		return billboard_mesh;
	if (jukebox_meshes[shape] == NULL)
	{
		const float *vertices;
		const Uint32 *indices;
		int vertex_count, index_count;
		jukebox3d_mesh(shape, &vertices, &vertex_count, &indices, &index_count);
		BTBHGPUCustomMeshReport report;
		jukebox_meshes[shape] = btbh_gpu_window_custom_mesh_create(window, vertices, (size_t)vertex_count * 24 * sizeof(float),
		                                                           (uint32_t)vertex_count, indices, (uint32_t)index_count, &report);
		if (jukebox_meshes[shape] == NULL)
			fprintf(stderr, "warning: jukebox mesh: %s\n", report.message);
	}
	return jukebox_meshes[shape];
}

// The order the items are drawn in batches: by shape, look and texture (models each their own).
static int jukebox_key(const J3DItem *it)
{
	return (it->shape * 3 + it->look) * J3D_TEXTURES + (it->textured < J3D_TEXTURES ? it->textured : 0);
}

#define JUKEBOX_SSAO_UNIT 0.15f  // (the jukebox's world units per game pixel, for the ambient occlusion: scene_ssao)

// The jukebox's scene over the whole window, under its panel (whose glass shows it blurred). True if
// it was drawn.
static bool present_jukebox_scene(const BTBHGPUWindowReport *frame)
{
	const float w = (float)frame->logical_width, h = (float)frame->logical_height;
	const UIMenu *published = ui_published();
	const J3DScene *js = ui_published_is(UI_SCREEN_ENDING) ? jukebox3d_ending_frame(w, h)
	                   : jukebox3d_frame(w, h, published != NULL && !published->jukebox.hidden);
	for (int i = 0; i < js->item_count; ++i)
	{
		const int t = js->items[i].textured;
		if (t > J3D_UNTEXTURED && t < J3D_TEXTURES && planet_textures[t] == NULL)
		{
			int tw, th;
			const Uint32 *pixels = jukebox3d_planet_texture((J3DTexture)t, &tw, &th);
			planet_textures[t] = create_texture_filtered(tw, th, BTBH_GPU_TEXTURE_COLOR_SPACE_SRGB, BTBH_GPU_TEXTURE_FILTER_LINEAR);
			btbh_gpu_texture_update_rgba8(planet_textures[t], (const uint8_t *)pixels, 0, 0, (uint32_t)tw, (uint32_t)th);
		}
	}

	// The items in batches of the same shape, look and texture.
	enum { KEYS = J3D_SHAPES * 3 * J3D_TEXTURES };
	static int order[J3D_MAX_ITEMS];
	int starts[KEYS + 1] = { 0 };
	for (int i = 0; i < js->item_count; ++i)
		++starts[jukebox_key(&js->items[i]) + 1];
	for (int k = 0; k < KEYS; ++k)
		starts[k + 1] += starts[k];
	int fill[KEYS];
	memcpy(fill, starts, sizeof(fill));
	for (int i = 0; i < js->item_count; ++i)
		order[fill[jukebox_key(&js->items[i])]++] = i;

	// (The ships' palette colours as the store shows them.)
	Uint32 colors[256];
	const SDL_Color *store = palettes[pcxpal[0]];
	for (int i = 0; i < 256; ++i)
		colors[i] = pack_rgba(store[i].r, store[i].g, store[i].b);
	sync_model_cache();
	int instance_count = 0, batch_count = 0;
	for (int k = 0; k < KEYS; ++k)
	{
		if (starts[k] == starts[k + 1])
			continue;
		const J3DItem *first = &js->items[order[starts[k]]];
		if (first->shape == J3D_MODEL)
		{
			for (int n = starts[k]; n < starts[k + 1]; ++n)
			{
				const J3DItem *it = &js->items[order[n]];
				Mat4 placement;
				memcpy(placement.m, it->m, sizeof(placement.m));
				add_showcase_model(it->model, &placement, 1.0f, 1.0f, colors, &instance_count, &batch_count);
			}
			continue;
		}
		BTBHGPUCustomMesh *mesh = jukebox_mesh((J3DShape)first->shape);
		if (mesh == NULL || batch_count >= MAX_BATCHES)
			continue;
		const int first_instance = instance_count;
		for (int n = starts[k]; n < starts[k + 1] && instance_count < MAX_INSTANCES; ++n)
		{
			const J3DItem *it = &js->items[order[n]];
			Mat4 m;
			memcpy(m.m, it->m, sizeof(m.m));
			if (it->shape == J3D_RING || it->shape == J3D_DOT)
			{
				// (The quad's y along the shape's z: lying in its XZ plane.)
				for (int c = 0; c < 4; ++c)
				{
					const float t = m.m[4 + c];
					m.m[4 + c] = m.m[8 + c];
					m.m[8 + c] = t;
				}
			}
			float *instance = instances + instance_count * 24;
			write_instance_world(instance, &m, 1.0f);
			memcpy(instance + 16, it->color, 4 * sizeof(float));
			++instance_count;
		}
		BTBHGPUSceneGeometryBatch *b = &batches[batch_count++];
		init_batch(b);
		b->kind = BTBH_GPU_SCENE_GEOMETRY_CUSTOM_MESH;
		b->custom_mesh = mesh;
		b->first_instance = (uint32_t)first_instance;
		b->instance_count = (uint32_t)(instance_count - first_instance);
		b->roughness = js->roughness;
		b->metalness = js->metalness;
		if (first->textured > J3D_UNTEXTURED && first->textured < J3D_TEXTURES)
			b->albedo_texture = planet_textures[first->textured];
		if (first->look != J3D_LIT)
			b->unlit_enabled = 1;
		if (first->look == J3D_ADDITIVE)
		{
			b->transparency_enabled = 1;
			b->blend_mode = BTBH_GPU_SCENE_BLEND_ADDITIVE;
			b->albedo_texture = first->shape == J3D_RING ? ring_texture : particle_texture;
			if (first->shape == J3D_GLOW)
				b->billboard_mode = BTBH_GPU_SCENE_BILLBOARD_FRONT;
		}
	}

	BTBHGPUSceneLighting lighting;
	memset(&lighting, 0, sizeof(lighting));
	lighting.spot_falloff = 1.0f;
	lighting.spot_inner_cutoff = 0.92388f;
	lighting.spot_outer_cutoff = 0.70711f;
	lighting.spot_range = 50.0f;
	lighting.ambient_red = js->ambient[0];
	lighting.ambient_green = js->ambient[1];
	lighting.ambient_blue = js->ambient[2];
	lighting.ambient_energy = js->ambient_energy;
	lighting.directional_x = js->sun[0];
	lighting.directional_y = js->sun[1];
	lighting.directional_z = js->sun[2];
	lighting.directional_energy = js->sun_energy;
	lighting.directional_red = js->sun_color[0];
	lighting.directional_green = js->sun_color[1];
	lighting.directional_blue = js->sun_color[2];
	lighting.point_light_count = (uint32_t)SDL_min(js->light_count, BTBH_GPU_SCENE_POINT_LIGHTS);
	memcpy(lighting.point_lights, js->lights, sizeof(float) * 8 * lighting.point_light_count);

	BTBHGPUScenePost post;
	Uint32 render_w, render_h;
	scene_post(&post, frame, &render_w, &render_h);
	scene_ssao(&post, JUKEBOX_SSAO_UNIT);
	post.bloom_intensity = settings3d.effects ? js->bloom : 0;
	post.bloom_threshold = js->bloom_threshold;
	post.bloom_knee = 0.25f;
	post.bloom_radius = 1.4f;
	// (Fading in and out as the jukebox's palette does.)
	post.exposure = js->exposure * ui_screen_fade();

	// The panel's glass: the scene blurred, made again each frame (it moves).
	if (scene_blur_targets(w, h))
	{
		frost_texture = scene_blur[SCENE_BLUR_STEPS - 1];
		cover_map[0] = cover_map[1] = 0;
		cover_map[2] = w;
		cover_map[3] = h;
		blur_ready = true;
	}
	BTBHGPUSceneReport report;
	const bool drawn = btbh_gpu_window_scene_present_instances_with_visibility(window,
	        shader_paths[SH_MODEL_VERT], shader_paths[SH_ANIMATED_MODEL_VERT],
	        shader_paths[SH_SHADOW_FAST_VERT], shader_paths[SH_SHADOW_FAST_FRAG],
	        shader_paths[SH_SHADOW_VERT], shader_paths[SH_ANIMATED_SHADOW_VERT], shader_paths[SH_SHADOW_FRAG],
	        shader_paths[SH_MODEL_FRAG], shader_paths[SH_MODEL_UNSHADOWED_FRAG],
	        shader_paths[SH_POST_VERT], shader_paths[SH_POST_FRAG],
	        shader_format, render_w, render_h,
	        js->view_projection, js->right, js->up, js->position,
	        &lighting, &post, instances, (uint32_t)instance_count, (uint32_t)instance_count, batches, NULL, NULL, (uint32_t)batch_count,
	        0, 0, 1, 255, &report) == BTBH_GPU_OK;  // (linear: a blue-black)
	if (!drawn)
	{
		fprintf(stderr, "warning: jukebox scene failed: %s\n", report.message);
		return false;
	}
	if (blur_ready)
	{
		BTBHGPUTextureReport capture_report;
		scene_capture = btbh_gpu_window_capture_pending_scene_texture(window, &capture_report);
		if (scene_capture == NULL)
			blur_ready = false;
	}
	static int profile = -1;
	if (profile < 0)
		profile = SDL_getenv("TYR3D_PROFILE") != NULL;
	static int frames = 0;
	static Uint64 since = 0;
	if (profile && ++frames % 240 == 0)
	{
		const Uint64 now = SDL_GetTicksNS();
		printf("jukebox: %.1f frames a second, %d items, %d instances, %d batches, %d lights; cpu prepare %.2f ms, encode %.2f ms\n",
		       since != 0 ? 240 * 1e9 / (double)(now - since) : 0.0, js->item_count, instance_count, batch_count, js->light_count,
		       report.cpu_prepare_milliseconds, report.cpu_geometry_encode_milliseconds);
		since = now;
	}
	return true;
}

/* --- Destruct (destruct3d.h) ------------------------------------------------------------------- */

static BTBHGPUCustomMesh *destruct_chunks[D3_CHUNKS];
static unsigned int destruct_chunks_made[D3_CHUNKS];
static BTBHGPUCustomMesh *destruct_land = NULL, *destruct_sphere = NULL;
static unsigned int destruct_land_made = 0;
static BTBHGPUTexture *destruct_sky = NULL, *destruct_planet = NULL, *destruct_glow = NULL;
static unsigned int destruct_glow_made = 0;

static void forget_destruct_scene(void)
{
	// (The window's.)
	memset(destruct_chunks, 0, sizeof(destruct_chunks));
	memset(destruct_chunks_made, 0, sizeof(destruct_chunks_made));
	destruct_land = destruct_sphere = NULL;
	destruct_land_made = destruct_glow_made = 0;
	destruct_sky = destruct_planet = destruct_glow = NULL;
}

// A mesh of destruct3d's on the GPU, made again or updated (NULL when it is empty).
static BTBHGPUCustomMesh *destruct_mesh(BTBHGPUCustomMesh *mesh, const D3Mesh *m)
{
	if (m->vertex_count == 0 || m->index_count == 0)
	{
		if (mesh != NULL)
			btbh_gpu_custom_mesh_destroy(mesh);
		return NULL;
	}
	BTBHGPUCustomMeshReport report;
	const uint32_t bytes = (uint32_t)m->vertex_count * 24 * sizeof(float);
	if (mesh != NULL && btbh_gpu_custom_mesh_update(mesh, m->vertices, bytes, m->indices, (uint32_t)m->index_count, &report) == BTBH_GPU_OK)
		return mesh;
	if (mesh != NULL)
		btbh_gpu_custom_mesh_destroy(mesh);
	mesh = btbh_gpu_window_custom_mesh_create(window, m->vertices, bytes, (uint32_t)m->vertex_count, m->indices, (uint32_t)m->index_count,
	                                          &report);
	if (mesh == NULL)
		fprintf(stderr, "warning: destruct mesh: %s\n", report.message);
	return mesh;
}

static BTBHGPUTexture *destruct_texture(const Uint32 *rgba, int w, int h)
{
	BTBHGPUTexture *t = create_texture_filtered(w, h, BTBH_GPU_TEXTURE_COLOR_SPACE_SRGB, BTBH_GPU_TEXTURE_FILTER_LINEAR);
	btbh_gpu_texture_update_rgba8(t, (const uint8_t *)rgba, 0, 0, (uint32_t)w, (uint32_t)h);
	return t;
}

// A batch of one mesh, lit, its colours the mesh's.
static BTBHGPUSceneGeometryBatch *destruct_batch(BTBHGPUCustomMesh *mesh, const Mat4 *world, float brightness, int *instance_count,
                                                 int *batch_count)
{
	if (mesh == NULL || *batch_count >= MAX_BATCHES || *instance_count >= MAX_INSTANCES)
		return NULL;
	write_instance_world(instances + *instance_count * 24, world, brightness);
	BTBHGPUSceneGeometryBatch *b = &batches[(*batch_count)++];
	init_batch(b);
	b->kind = BTBH_GPU_SCENE_GEOMETRY_CUSTOM_MESH;
	b->custom_mesh = mesh;
	b->first_instance = (uint32_t)(*instance_count)++;
	b->instance_count = 1;
	return b;
}

// The quad mesh (unit, in its XZ plane) over corners a (its uv 0,0), b (1,0) and d (0,1).
static Mat4 destruct_quad(const float a[3], const float b[3], const float d[3])
{
	Mat4 m = mat4_identity();
	for (int i = 0; i < 3; ++i)
	{
		m.m[0 + i] = b[i] - a[i];
		m.m[8 + i] = d[i] - a[i];
		m.m[12 + i] = a[i];
	}
	// (Its y: across it, for its normal.)
	const float *x = &m.m[0], *z = &m.m[8];
	m.m[4] = x[1] * z[2] - x[2] * z[1];
	m.m[5] = x[2] * z[0] - x[0] * z[2];
	m.m[6] = x[0] * z[1] - x[1] * z[0];
	const float length = sqrtf(m.m[4] * m.m[4] + m.m[5] * m.m[5] + m.m[6] * m.m[6]);
	for (int i = 4; i < 7; ++i)
		m.m[i] = length > 0 ? m.m[i] / length : 0;
	return m;
}

// A glow facing the camera (additive): at x, y, z, size across, its colour (linear, may be over 1).
static void destruct_glow_at(float x, float y, float z, float size, const float colour[3], BTBHGPUTexture *texture, int *instance_count)
{
	if (*instance_count >= MAX_INSTANCES)
		return;
	Mat4 m = mat4_identity();
	m.m[0] = m.m[5] = m.m[10] = size;
	m.m[12] = x;
	m.m[13] = y;
	m.m[14] = z;
	float *instance = instances + *instance_count * 24;
	write_instance_world(instance, &m, 1.0f);
	memcpy(instance + 16, colour, 3 * sizeof(float));
	instance[19] = 1;
	(void)texture;
	++*instance_count;
}

static void destruct_glow_batch(int first, int count, BTBHGPUTexture *texture, int *batch_count)
{
	if (count <= 0 || *batch_count >= MAX_BATCHES)
		return;
	BTBHGPUSceneGeometryBatch *b = &batches[(*batch_count)++];
	init_batch(b);
	b->kind = BTBH_GPU_SCENE_GEOMETRY_CUSTOM_MESH;
	b->custom_mesh = billboard_mesh;
	b->first_instance = (uint32_t)first;
	b->instance_count = (uint32_t)count;
	b->albedo_texture = texture;
	b->unlit_enabled = 1;
	b->transparency_enabled = 1;
	b->blend_mode = BTBH_GPU_SCENE_BLEND_ADDITIVE;
	b->billboard_mode = BTBH_GPU_SCENE_BILLBOARD_FRONT;
}

// The sun's shadow over the field and the ridge (an orthographic view along the light).
static void destruct_shadow(const float sun[3], float out[16])
{
	const float centre[3] = { D3_W / 2.0f, 100.0f, -30.0f };
	const float radius = 260.0f, depth = 600.0f;
	const float hint[3] = { 0, 0, -1 };
	float right[3] = { hint[1] * sun[2] - hint[2] * sun[1], hint[2] * sun[0] - hint[0] * sun[2], hint[0] * sun[1] - hint[1] * sun[0] };
	const float rl = sqrtf(right[0] * right[0] + right[1] * right[1] + right[2] * right[2]);
	for (int i = 0; i < 3; ++i)
		right[i] /= rl;
	const float up[3] = { sun[1] * right[2] - sun[2] * right[1], sun[2] * right[0] - sun[0] * right[2], sun[0] * right[1] - sun[1] * right[0] };
	float eye[3];
	for (int i = 0; i < 3; ++i)
		eye[i] = centre[i] - sun[i] * depth;
	Mat4 view = mat4_identity();
	float dots[3] = { 0, 0, 0 };
	for (int i = 0; i < 3; ++i)
	{
		view.m[i * 4 + 0] = right[i];
		view.m[i * 4 + 1] = up[i];
		view.m[i * 4 + 2] = sun[i];
		view.m[i * 4 + 3] = 0;
		dots[0] += right[i] * eye[i];
		dots[1] += up[i] * eye[i];
		dots[2] += sun[i] * eye[i];
	}
	view.m[12] = -dots[0];
	view.m[13] = -dots[1];
	view.m[14] = -dots[2];
	view.m[15] = 1;
	Mat4 projection = { { 0 } };
	projection.m[0] = 1.0f / radius;
	projection.m[5] = 1.0f / radius;
	projection.m[10] = 1.0f / (2 * depth);
	projection.m[15] = 1.0f;
	const Mat4 result = mat4_mul(&projection, &view);
	memcpy(out, result.m, sizeof(result.m));
}

// Destruct's scene over the whole window and its screen's panels over it; false if it couldn't be drawn.
static bool present_destruct(void)
{
	BTBHGPUWindowReport frame;
	if (!begin_frame(&frame))
		return true;  // (nothing to show this time)
	const Uint64 started = SDL_GetPerformanceCounter();
	hud_quad_count = 0;
	canvas_fade[3] = 0;
	shown_view.valid = false;
	const float w = (float)frame.logical_width, h = (float)frame.logical_height;
	const D3Tick *tick = destruct3d_state();
	D3Camera camera;
	destruct3d_camera(w / SDL_max(h, 1.0f), &camera);

	// The GPU's copies: the ridge's chunks that changed, the land, the pictures.
	for (int c = 0; c < D3_CHUNKS; ++c)
	{
		D3Mesh m;
		const unsigned int made = destruct3d_chunk(c, &m);
		if (made != destruct_chunks_made[c])
		{
			destruct_chunks[c] = destruct_mesh(destruct_chunks[c], &m);
			destruct_chunks_made[c] = made;
		}
	}
	{
		D3Mesh m;
		const unsigned int made = destruct3d_back(&m);
		if (made != destruct_land_made)
		{
			destruct_land = destruct_mesh(destruct_land, &m);
			destruct_land_made = made;
		}
	}
	float planet_centre[3], planet_radius;
	{
		D3Mesh m;
		destruct3d_planet(&camera, &m, planet_centre, &planet_radius);
		if (destruct_sphere == NULL)
			destruct_sphere = destruct_mesh(NULL, &m);
	}
	if (destruct_sky == NULL)
	{
		int tw, th;
		const Uint32 *rgba = destruct3d_sky(&tw, &th);
		destruct_sky = destruct_texture(rgba, tw, th);
		rgba = destruct3d_planet_texture(&tw, &th);
		destruct_planet = destruct_texture(rgba, tw, th);
		destruct_glow = create_texture_filtered(D3_W, D3_H, BTBH_GPU_TEXTURE_COLOR_SPACE_SRGB, BTBH_GPU_TEXTURE_FILTER_LINEAR);
	}
	const Uint32 *glow_rgba;
	bool glowing;
	const Uint64 meshes_made = SDL_GetPerformanceCounter();
	const unsigned int glow_made = destruct3d_glow(&glow_rgba, &glowing);
	if (glow_made != destruct_glow_made)
	{
		btbh_gpu_texture_update_rgba8(destruct_glow, (const uint8_t *)glow_rgba, 0, 0, D3_W, D3_H);
		destruct_glow_made = glow_made;
	}

	int instance_count = 0, batch_count = 0;
	static Uint8 casts_shadow[MAX_BATCHES];
	memset(casts_shadow, 0, sizeof(casts_shadow));
	const bool shadows = shadows_enabled();
	// The sky, far away.
	{
		const Mat4 m = destruct_quad(camera.sky[0], camera.sky[1], camera.sky[3]);
		BTBHGPUSceneGeometryBatch *b = destruct_batch(quad_mesh, &m, 1.0f, &instance_count, &batch_count);
		if (b != NULL)
		{
			b->albedo_texture = destruct_sky;
			b->unlit_enabled = 1;
			b->ssao_mode = BTBH_GPU_SCENE_SSAO_NONE;
		}
	}
	// The planet, lit by the sun.
	{
		const Mat4 chain[] = { mat4_translation(planet_centre[0], planet_centre[1], planet_centre[2]), mat4_scaling(planet_radius),
		                       mat4_rotation(0, 18.0f) };
		const Mat4 m = mat4_chain((int)COUNTOF(chain), chain);
		BTBHGPUSceneGeometryBatch *b = destruct_batch(destruct_sphere, &m, 1.0f, &instance_count, &batch_count);
		if (b != NULL)
		{
			b->albedo_texture = destruct_planet;
			b->roughness = 0.95f;
			b->ssao_mode = BTBH_GPU_SCENE_SSAO_NONE;
		}
	}
	// The land behind, the ridge.
	{
		const Mat4 m = mat4_identity();
		BTBHGPUSceneGeometryBatch *b = destruct_batch(destruct_land, &m, 1.0f, &instance_count, &batch_count);
		if (b != NULL)
		{
			b->roughness = 0.95f;
		}
		for (int c = 0; c < D3_CHUNKS; ++c)
		{
			b = destruct_batch(destruct_chunks[c], &m, 1.0f, &instance_count, &batch_count);
			if (b != NULL)
			{
				b->roughness = 0.92f;
				casts_shadow[batch_count - 1] = shadows;
			}
		}
	}
	// The units and the walls: their models (tools/blender/models/destruct), facing the other side, the
	// parts that aim turned by the unit's angle, a helicopter's rotor turning; the game's sprites with
	// volume where a model is missing.
	{
		enum { UNIT_KINDS = 8, HELI = 7 };
		static const char *const names[UNIT_KINDS] = { "tank", "nuke", "dirt", "satellite", "magnet", "laser", "jumper", "heli" };
		// The part that aims (or a rotor that turns) and its pivot in the unit's model (game pixels).
		static const struct { const char *name; float x, z; bool sided; } parts[UNIT_KINDS] = {
			{ "tank_barrel", 0.6f, 7.0f, false }, { "nuke_rail", -0.4f, 5.4f, false }, { "dirt_tube", -0.6f, 5.6f, true },
			{ NULL, 0, 0, false }, { NULL, 0, 0, false }, { "laser_head", 0.0f, 10.0f, false }, { NULL, 0, 0, false },
			{ "heli_rotor", 0.4f, 9.9f, false },
		};
		static unsigned int found = ~0u;
		static int unit_models[UNIT_KINDS][2], part_models[UNIT_KINDS][2], wall_model = -1;
		if (found != m3d_generation)
		{
			char name[48];
			for (int t = 0; t < UNIT_KINDS; ++t)
				for (int side = 0; side < 2; ++side)
				{
					snprintf(name, sizeof(name), "destruct_%s_%c", names[t], side == 0 ? 'l' : 'r');
					unit_models[t][side] = m3d_find_model(name);
					part_models[t][side] = -1;
					if (parts[t].name != NULL)
					{
						if (parts[t].sided)
							snprintf(name, sizeof(name), "destruct_%s_%c", parts[t].name, side == 0 ? 'l' : 'r');
						else
							snprintf(name, sizeof(name), "destruct_%s", parts[t].name);
						part_models[t][side] = m3d_find_model(name);
					}
				}
			wall_model = m3d_find_model("destruct_wall");
			found = m3d_generation;
		}
		sync_model_cache();
		const float seconds = SDL_GetTicks() / 1000.0f;
		const Uint32 colors_hash = hash_colors(rgb_palette);
		VolumeSheet *entry = NULL;
		for (int i = 0; i < tick->unit_count + tick->wall_count; ++i)
		{
			const bool wall = i >= tick->unit_count;
			const D3Unit *u = wall ? NULL : &tick->units[i];
			const int model = wall ? wall_model : (u->type >= 0 && u->type < UNIT_KINDS ? unit_models[u->type][u->side] : -1);
			const int first_batch = batch_count;
			if (model >= 0 && wall)
			{
				const D3Wall *w = &tick->walls[i - tick->unit_count];
				const Mat4 m = mat4_translation(w->x + 6.0f, 200.0f - (w->y + 14), -D3_PLANE);
				add_showcase_model(model, &m, 0, 1, rgb_palette, &instance_count, &batch_count);
			}
			else if (model >= 0)
			{
				// (A little larger than the game's sprite, about its foot. A helicopter faces the way it
				// flies and dips its nose as it speeds up.)
				bool facing_right = u->side == 0;
				float tilt = 0;
				if (u->type == HELI)
				{
					if (u->last_move > 2 || u->last_move < -2)
						facing_right = u->last_move > 0;
					tilt = -3.0f * SDL_abs(u->last_move);
				}
				Mat4 mirror = mat4_identity();
				if (!facing_right)
					mirror.m[0] = -1;
				const Mat4 chain[] = { mat4_translation(u->x + 6.0f, 200.0f - u->y, -D3_PLANE), mirror, mat4_rotation(2, tilt), mat4_scaling(1.25f) };
				const Mat4 placement = mat4_chain((int)COUNTOF(chain), chain);
				add_showcase_model(model, &placement, 0, 1, rgb_palette, &instance_count, &batch_count);
				const int part = part_models[u->type][u->side];
				if (part >= 0)
				{
					const Mat4 turn = u->type == HELI ? mat4_rotation(1, seconds * 1440.0f)
					                                  : mat4_rotation(2, u->angle * 180.0f / (float)M_PI);
					const Mat4 part_chain[] = { placement, mat4_translation(parts[u->type].x, parts[u->type].z, 0), turn };
					const Mat4 m = mat4_chain((int)COUNTOF(part_chain), part_chain);
					add_showcase_model(part, &m, 0, 1, rgb_palette, &instance_count, &batch_count);
				}
			}
			else
			{
				if (entry == NULL && (entry = get_volume_sheet(&destructSpriteSheet, rgb_palette, colors_hash)) == NULL)
					continue;
				const float x = wall ? tick->walls[i - tick->unit_count].x : u->x;
				const float top = wall ? tick->walls[i - tick->unit_count].y : u->y - 13;
				const int sprite = wall ? 42 : u->sprite;
				BTBHGPUCustomMesh *mesh = get_volume_mesh(entry, (unsigned int)sprite, false, V3D_STYLE_RAISED, 0);
				const float k = wall ? 1.0f : 1.25f;
				const Mat4 chain[] = { mat4_translation(x + 6, 200 - (top + 14) + 7 * k, -D3_PLANE), mat4_scaling(k), mat4_rotation(0, 90.0f) };
				const Mat4 m = mat4_chain((int)COUNTOF(chain), chain);
				BTBHGPUSceneGeometryBatch *b = destruct_batch(mesh, &m, 1.0f, &instance_count, &batch_count);
				if (b != NULL)
				{
					b->albedo_texture = filtered_volume_texture(entry, rgb_palette, colors_hash, 0);
					b->unlit_enabled = 1;
					b->alpha_cutoff = 0.5f;
				}
			}
			for (int b = first_batch; b < batch_count; ++b)
				casts_shadow[b] = shadows;
		}
	}
	// The field's fire in the game's plane.
	if (glowing)
	{
		const float a[3] = { 0, 200, -D3_PLANE + 1.5f }, b3[3] = { D3_W, 200, -D3_PLANE + 1.5f }, d[3] = { 0, 0, -D3_PLANE + 1.5f };
		const Mat4 m = destruct_quad(a, b3, d);
		BTBHGPUSceneGeometryBatch *b = destruct_batch(quad_mesh, &m, 2.4f, &instance_count, &batch_count);
		if (b != NULL)
		{
			b->albedo_texture = destruct_glow;
			b->unlit_enabled = 1;
			b->transparency_enabled = 1;
			b->blend_mode = BTBH_GPU_SCENE_BLEND_ADDITIVE;
		}
	}
	// The shots, glowing, with their trails; the crosshairs.
	{
		int first = instance_count;
		for (int i = 0; i < tick->shot_count; ++i)
		{
			const D3Shot *s = &tick->shots[i];
			const bool laser = s->type >= 11 && s->type <= 14;  // (the lasers' blue)
			const float hot[3] = { laser ? 0.8f : 4.0f, laser ? 2.2f : 3.0f, laser ? 6.0f : 1.4f };
			for (int k = 0; k < 4; ++k)
			{
				const float f = 1.0f - k * 0.24f;
				const float colour[3] = { hot[0] * f * f, hot[1] * f * f * f, hot[2] * f * f * f };
				destruct_glow_at(s->x - s->xmov * k * 1.4f, 200 - (s->y - s->ymov * k * 1.4f), -D3_PLANE, (k == 0 ? 7.0f : 5.5f) * f,
				                 colour, particle_texture, &instance_count);
			}
		}
		destruct_glow_batch(first, instance_count - first, particle_texture, &batch_count);
		first = instance_count;
		for (int s = 0; s < 2; ++s)
			if (tick->aim[s])
			{
				const float gold[3] = { 1.6f, 1.15f, 0.55f };
				destruct_glow_at(tick->aim_x[s], 200 - tick->aim_y[s], -D3_PLANE + 2, 9.0f, gold, ring_texture, &instance_count);
			}
		destruct_glow_batch(first, instance_count - first, ring_texture, &batch_count);
	}

	// The effects (destruct3d's particles): smoke and clods blended, fire, sparks and shock waves added.
	{
		const D3Particle *particles;
		const int count = destruct3d_particles(&particles);
		for (int kind = 0; kind < D3P_KINDS && batch_count < MAX_BATCHES; ++kind)
		{
			const int first = instance_count;
			for (int i = 0; i < count && instance_count < MAX_INSTANCES; ++i)
			{
				const D3Particle *p = &particles[i];
				if (p->kind != kind)
					continue;
				const float t = SDL_clamp(p->age / SDL_max(p->life, 1.0f), 0.0f, 1.0f);
				Mat4 m = mat4_identity();
				// (Puffs each turned their own way, turning slowly.)
				const float angle = kind == D3P_SMOKE || kind == D3P_FIRE ? p->life * 2.39996f + p->age * 0.03f : 0.0f;
				m.m[0] = cosf(angle) * p->size;
				m.m[1] = sinf(angle) * p->size;
				m.m[4] = -sinf(angle) * p->size;
				m.m[5] = cosf(angle) * p->size;
				m.m[10] = p->size;
				m.m[12] = p->x;
				m.m[13] = p->y;
				m.m[14] = p->z;
				float *instance = instances + instance_count * 24;
				write_instance_world(instance, &m, 1.0f);
				for (int c = 0; c < 4; ++c)
					instance[16 + c] = p->colour[c] + (p->end_colour[c] - p->colour[c]) * t;
				++instance_count;
			}
			if (instance_count == first)
				continue;
			BTBHGPUSceneGeometryBatch *b = &batches[batch_count++];
			init_batch(b);
			b->kind = BTBH_GPU_SCENE_GEOMETRY_CUSTOM_MESH;
			b->custom_mesh = billboard_mesh;
			b->first_instance = (uint32_t)first;
			b->instance_count = (uint32_t)(instance_count - first);
			b->albedo_texture = kind == D3P_SMOKE || kind == D3P_FIRE ? fire_texture : kind == D3P_RING ? ring_texture : particle_texture;
			b->billboard_mode = BTBH_GPU_SCENE_BILLBOARD_FRONT;
			b->unlit_enabled = 1;
			b->transparency_enabled = 1;
			b->blend_mode = kind == D3P_SMOKE || kind == D3P_DEBRIS ? BTBH_GPU_SCENE_BLEND_ALPHA : BTBH_GPU_SCENE_BLEND_ADDITIVE;
		}
	}

	BTBHGPUSceneLighting lighting;
	memset(&lighting, 0, sizeof(lighting));
	lighting.spot_falloff = 1.0f;
	lighting.spot_inner_cutoff = 0.92388f;
	lighting.spot_outer_cutoff = 0.70711f;
	lighting.spot_range = 50.0f;
	lighting.ambient_red = 0.55f;
	lighting.ambient_green = 0.56f;
	lighting.ambient_blue = 0.72f;
	lighting.ambient_energy = 0.55f;
	float sun[3] = { 0.5f, -0.78f, -0.45f };
	const float sun_length = sqrtf(sun[0] * sun[0] + sun[1] * sun[1] + sun[2] * sun[2]);
	for (int i = 0; i < 3; ++i)
		sun[i] /= sun_length;
	lighting.directional_x = sun[0];
	lighting.directional_y = sun[1];
	lighting.directional_z = sun[2];
	lighting.directional_energy = 3.6f;
	lighting.directional_red = 1.0f;
	lighting.directional_green = 0.93f;
	lighting.directional_blue = 0.82f;
	set_environment(&lighting);
	for (int i = 0; i < 27; ++i)
		lighting.irradiance_sh[i] *= 0.25f;
	if (shadows)
	{
		btbh_gpu_window_scene_set_directional_shadow_size(window, 2048, 2048);  // (its box is square)
		lighting.directional_shadow_enabled = 1;
		lighting.directional_shadow_softness = 1.0f;
		destruct_shadow(sun, lighting.directional_shadow_view_projection);
	}
	// The explosions' light.
	for (int i = 0; i < tick->blast_count && lighting.point_light_count < BTBH_GPU_SCENE_POINT_LIGHTS; ++i)
	{
		const D3Blast *e = &tick->blasts[i];
		if (e->type == 2)  // (dirt thrown, no fire)
			continue;
		const float left = 1.0f - e->width / (float)SDL_max(e->max, 1);
		float *l = lighting.point_lights[lighting.point_light_count++];
		l[0] = (float)e->x;
		l[1] = 200.0f - e->y;
		l[2] = -D3_PLANE + 6;
		l[3] = 24.0f + e->max * 2.5f;
		l[4] = 1.0f;
		l[5] = 0.55f;
		l[6] = 0.22f;
		l[7] = 3.0f * left * SDL_min(e->max / 20.0f, 1.5f);
	}

	BTBHGPUScenePost post;
	Uint32 render_w, render_h;
	scene_post(&post, &frame, &render_w, &render_h);
	scene_ssao(&post, 1.0f);
	post.exposure = ui_screen_fade();

	// The panels' glass: the scene blurred, made again each frame.
	if (scene_blur_targets(w, h))
	{
		frost_texture = scene_blur[SCENE_BLUR_STEPS - 1];
		cover_map[0] = cover_map[1] = 0;
		cover_map[2] = w;
		cover_map[3] = h;
		blur_ready = true;
	}
	BTBHGPUSceneReport report;
	const bool drawn = btbh_gpu_window_scene_present_instances_with_visibility(window,
	        shader_paths[SH_MODEL_VERT], shader_paths[SH_ANIMATED_MODEL_VERT],
	        shader_paths[SH_SHADOW_FAST_VERT], shader_paths[SH_SHADOW_FAST_FRAG],
	        shader_paths[SH_SHADOW_VERT], shader_paths[SH_ANIMATED_SHADOW_VERT], shader_paths[SH_SHADOW_FRAG],
	        shader_paths[SH_MODEL_FRAG], shader_paths[SH_MODEL_UNSHADOWED_FRAG],
	        shader_paths[SH_POST_VERT], shader_paths[SH_POST_FRAG],
	        shader_format, render_w, render_h,
	        camera.view_projection, camera.right, camera.up, camera.position,
	        &lighting, &post, instances, (uint32_t)instance_count, (uint32_t)instance_count, batches, NULL, casts_shadow, (uint32_t)batch_count,
	        2, 2, 5, 255, &report) == BTBH_GPU_OK;
	if (!drawn)
		fprintf(stderr, "warning: destruct scene failed: %s\n", report.message);
	if (drawn && blur_ready)
	{
		BTBHGPUTextureReport capture_report;
		scene_capture = btbh_gpu_window_capture_pending_scene_texture(window, &capture_report);
		if (scene_capture == NULL)
			blur_ready = false;
	}
	else
		blur_ready = false;

	const UIView view = { .w = w, .h = h, .pixel = 1.0f / text_density, .picture = { 0, 0, w, h } };
	ui_build_screen(&view);
	present_canvas(NULL, 0, false, !drawn, &frame);
	blur_ready = false;
	// (TYR3D_PROFILE: frames a second, what a frame takes, of it the ridge's meshes.)
	static int profile = -1;
	if (profile < 0)
		profile = SDL_getenv("TYR3D_PROFILE") != NULL;
	if (profile)
	{
		static int frames = 0;
		static double spent = 0, meshing = 0;
		static Uint64 since = 0;
		const double k = 1000.0 / SDL_GetPerformanceFrequency();
		const Uint64 now = SDL_GetPerformanceCounter();
		spent += (now - started) * k;
		meshing += (meshes_made - started) * k;
		if (++frames == 120)
		{
			printf("destruct: %.1f frames a second, %.2f ms a frame, meshes %.2f ms\n", since != 0 ? 120 * 1000.0 / ((now - since) * k) : 0.0,
			       spent / frames, meshing / frames);
			frames = 0;
			spent = meshing = 0;
			since = now;
		}
	}
	return true;
}

void rgpu_present_ui_again(void)
{
	ahead = 1;
	rgpu_present_ui(NULL);
	ahead = 0;
}

/* --- The modern UI's screens (ui.h), and their 3D scene (the store's ship) ------------------ */

/*
 * The store's floor under its ship: a dark warm pad lit in its middle, with faint brass rings and a
 * grid, drawn for a box w x h screen pixels (the texture is stretched over it).
 */
#define PAD_TEXELS 256
static BTBHGPUTexture *pad_texture = NULL;

static void make_pad(float w, float h)
{
	static float made_w = 0, made_h = 0;
	if (pad_texture == NULL)
	{
		pad_texture = create_texture_filtered(PAD_TEXELS, PAD_TEXELS, BTBH_GPU_TEXTURE_COLOR_SPACE_SRGB, BTBH_GPU_TEXTURE_FILTER_LINEAR);
		made_w = made_h = 0;
	}
	if (SDL_fabsf(made_w - w) < 0.5f && SDL_fabsf(made_h - h) < 0.5f)
		return;
	made_w = w;
	made_h = h;
	static Uint32 rgba[PAD_TEXELS * PAD_TEXELS];
	for (int ty = 0; ty < PAD_TEXELS; ++ty)
		for (int tx = 0; tx < PAD_TEXELS; ++tx)
		{
			// The texel's place in the box: screen pixels from its middle.
			const float x = ((tx + 0.5f) / PAD_TEXELS - 0.5f) * w, y = ((ty + 0.5f) / PAD_TEXELS - 0.5f) * h;
			const float r = sqrtf(x * x + y * y) / (h * 0.5f);
			float light = 0.3f + 0.7f * expf(-r * r * 1.5f);
			const float ex = SDL_fabsf(x) / (w * 0.5f), ey = SDL_fabsf(y) / (h * 0.5f);
			light *= 1.0f - 0.5f * SDL_clamp((SDL_max(ex, ey) - 0.65f) / 0.35f, 0.0f, 1.0f);
			float c[3] = { 16 + 44 * light, 11 + 32 * light, 8 + 20 * light };
			// Rings round the middle, a grid every 10 screen pixels fading outwards.
			const float ring = 0.32f * SDL_clamp(1 - SDL_fabsf(r - 0.84f) / 0.014f, 0.0f, 1.0f) +
			                   0.16f * SDL_clamp(1 - SDL_fabsf(r - 0.9f) / 0.008f, 0.0f, 1.0f);
			const float gx = SDL_fabsf(fmodf(x + 1005.0f, 10.0f) - 5.0f), gy = SDL_fabsf(fmodf(y + 1005.0f, 10.0f) - 5.0f);
			const float grid = 0.08f * (SDL_clamp((gx - 4.45f) / 0.55f, 0.0f, 1.0f) + SDL_clamp((gy - 4.45f) / 0.55f, 0.0f, 1.0f)) *
			                   SDL_clamp(1.15f - r, 0.0f, 1.0f);
			const float brass[3] = { 196, 154, 94 };
			const float a = SDL_clamp(ring + grid, 0.0f, 1.0f);
			for (int k = 0; k < 3; ++k)
				c[k] += (brass[k] - c[k]) * a;
			rgba[ty * PAD_TEXELS + tx] = pack_rgba((Uint8)c[0], (Uint8)c[1], (Uint8)c[2]);
		}
	btbh_gpu_texture_update_rgba8(pad_texture, (const uint8_t *)rgba, 0, 0, PAD_TEXELS, PAD_TEXELS);
}

/*
 * A showcase's scene (its objects over a floor) in a rectangle of the window (points), seen from
 * straight above: box is the screen's box it is laid out on (screen pixels, as its objects are
 * placed), the floor a texture over the box (u, v: how much of it). True if it was drawn.
 */
static BTBHGPUTexture *sim_space;

static bool present_scene_pane(const RGPUShowcase *show, const float rect[4], const float box[4], BTBHGPUTexture *floor, float floor_u,
                               float floor_v, const BTBHGPUWindowReport *window_frame)
{
	const bool floor_is_space = floor != NULL && floor == sim_space;
	const float logical_w = (float)window_frame->logical_width, logical_h = (float)window_frame->logical_height;
	const float wx0 = rect[0], wy0 = rect[1], wx1 = rect[0] + rect[2], wy1 = rect[1] + rect[3];
	if (wx1 - wx0 < 1 || wy1 - wy0 < 1 || box[2] <= 0 || box[3] <= 0)
		return false;
	const float ndc_rect[4] = { wx0 / logical_w * 2 - 1, 1 - wy1 / logical_h * 2, wx1 / logical_w * 2 - 1, 1 - wy0 / logical_h * 2 };
	const float tilt = rgpu_camera.tilt_degrees;
	rgpu_camera.tilt_degrees = 0;
	const Camera3D camera = fit_camera(0.0f, (wx1 - wx0) / (wy1 - wy0), ndc_rect, false, false);
	rgpu_camera.tilt_degrees = tilt;
	shown_view.valid = false;

	// (The camera fits the playfield's width, as the last level had it.)
	const float fx = (float)l3d_field_x(), fw = (float)l3d_field_w();
	const float k = fw / box[2];  // world units per screen pixel
	const float top = L3D_PLAYFIELD_H - box[3] * k;
#define PANE_X(px) (fx + ((px) - box[0]) * k)
#define PANE_Z(py) (top + ((py) - box[1]) * k)

	Uint32 colors[256];
	memcpy(colors, rgb_palette, sizeof(colors));
	sync_model_cache();
	int instance_count = 0, batch_count = 0;
	{
		Mat4 transform = mat4_identity();
		transform.m[0] = fw;
		transform.m[10] = box[3] * k;
		transform.m[12] = fx;
		transform.m[14] = top;
		write_instance_world(instances + instance_count * 24, &transform, 1.0f);
		BTBHGPUSceneGeometryBatch *b = &batches[batch_count++];
		init_batch(b);
		b->kind = BTBH_GPU_SCENE_GEOMETRY_CUSTOM_MESH;
		b->custom_mesh = quad_mesh;
		b->first_instance = instance_count++;
		b->instance_count = 1;
		b->albedo_texture = floor;
		b->uv_scale_x = floor_u;
		b->uv_scale_y = floor_v;
		b->unlit_enabled = 1;
		b->ssao_mode = floor_is_space ? BTBH_GPU_SCENE_SSAO_NONE : BTBH_GPU_SCENE_SSAO_RECEIVE_ONLY;
	}
	const int first_model_batch = batch_count;
	enum { MAX_PANE_OBJECTS = 160 };
	static Mat4 placements[MAX_PANE_OBJECTS];
	for (int i = 0; i < show->object_count && i < MAX_PANE_OBJECTS; ++i)
	{
		const RGPUShowcaseObject *o = &show->objects[i];
		const Mat4 *parent = o->parent >= 0 && o->parent < i ? &placements[o->parent] : NULL;
		placements[i] = showcase_placement(o, parent, PANE_X(o->x), PANE_Z(o->y), k);
		const float scale = o->scale > 0 ? o->scale : 1.0f;
		if (o->model != M3D_VOLUME)
			add_showcase_model(o->model, &placements[i], o->size * k * scale, k * scale, colors, &instance_count, &batch_count);
	}
	add_showcase_volumes(show, placements, SDL_min(show->object_count, MAX_PANE_OBJECTS), k, colors, &instance_count,
	                     &batch_count);
	const float ox = PANE_X(0), oz = PANE_Z(0);
#undef PANE_X
#undef PANE_Z

	static Uint8 casts_shadow[MAX_BATCHES];
	const bool shadows = shadows_enabled();
	for (int i = 0; i < batch_count; ++i)
	{
		casts_shadow[i] = shadows && i >= first_model_batch;
		// (Space takes no shadow: the simulator's floor is deep space.)
		if (shadows && batches[i].unlit_enabled == 1 && !(i < first_model_batch && floor_is_space))
			batches[i].unlit_enabled = 2;
	}
	// The glows and particles last, as a level's: they neither cast nor take shadows.
	const int first_light_batch = batch_count;
	if (settings3d.effects)
	{
		if (show->particles)
			add_showcase_particles(ox, oz, k, &instance_count, &batch_count);
		add_showcase_glows(show, ox, oz, k, colors, &instance_count, &batch_count);
	}
	for (int i = first_light_batch; i < batch_count; ++i)
	{
		casts_shadow[i] = 0;
		batches[i].ssao_mode = BTBH_GPU_SCENE_SSAO_NONE;
	}
	BTBHGPUSceneLighting lighting;
	scene_lighting(&lighting, &camera, shadows, false);
	if (settings3d.effects)
		add_showcase_lights(&lighting, show, ox, oz, k, colors);
	BTBHGPUScenePost post;
	Uint32 render_w, render_h;
	scene_post(&post, window_frame, &render_w, &render_h);
	scene_ssao(&post, k);
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
	return drawn;
}

/*
 * The weapon simulator's space (make_sim_space): a dark navy deep, lighter in the middle, a faint nebula, and stars
 * in three layers drifting down past the ship at their own pace (the far ones small, dim and slow), drawn anew each
 * time it shows (by the time).
 */
#define SIM_SPACE_W 256
#define SIM_SPACE_H 320
static BTBHGPUTexture *sim_space = NULL;  // (declared above present_scene_pane)

static void make_sim_space(float aspect)
{
	static Uint32 pixels[SIM_SPACE_W * SIM_SPACE_H];
	static float base[SIM_SPACE_W * SIM_SPACE_H][3];
	static bool based = false;
	if (sim_space == NULL)
		sim_space = create_texture_filtered(SIM_SPACE_W, SIM_SPACE_H, BTBH_GPU_TEXTURE_COLOR_SPACE_SRGB, BTBH_GPU_TEXTURE_FILTER_LINEAR);
	if (!based)
	{
		based = true;
		for (int y = 0; y < SIM_SPACE_H; ++y)
			for (int x = 0; x < SIM_SPACE_W; ++x)
			{
				const float u = (x + 0.5f) / SIM_SPACE_W, v = (y + 0.5f) / SIM_SPACE_H;
				const float r = sqrtf((u - 0.5f) * (u - 0.5f) + (v - 0.45f) * (v - 0.45f) * 0.6f);
				const float glow = SDL_clamp(1 - r * 1.7f, 0.0f, 1.0f);
				const float gas = nebula_fbm(u * 3, v * 3, 3, 71u);
				const float neb = SDL_clamp((gas - 0.45f) / 0.3f, 0.0f, 1.0f);
				float *c = base[y * SIM_SPACE_W + x];
				c[0] = 6 + 10 * glow + 40 * neb * neb;
				c[1] = 8 + 14 * glow + 18 * neb * neb;
				c[2] = 16 + 26 * glow + 52 * neb * neb;
			}
	}
	static float scratch[SIM_SPACE_W * SIM_SPACE_H][3];
	memcpy(scratch, base, sizeof(scratch));
	const float t = SDL_GetTicks() / 1000.0f;
	// (The texture is stretched over the pane: the stars kept round by the pane's shape.)
	const float squash = SDL_clamp((float)SIM_SPACE_W / SIM_SPACE_H / SDL_max(aspect, 0.1f), 0.5f, 2.0f);
	static const struct { int count; float speed, size, light; } layers[3] = {
		{ 70, 14.0f, 0.7f, 0.45f }, { 40, 32.0f, 1.0f, 0.7f }, { 18, 70.0f, 1.5f, 1.0f },
	};
	for (int l = 0; l < 3; ++l)
		for (int i = 0; i < layers[l].count; ++i)
		{
			const Uint32 seed = hash32((Uint32)(l * 1000 + i) * 2654435761u);
			const float sx = hash_unit(seed) * SIM_SPACE_W;
			const float sy = fmodf(hash_unit(seed + 1) * SIM_SPACE_H + t * layers[l].speed, SIM_SPACE_H);
			const float size = layers[l].size * (0.7f + 0.6f * hash_unit(seed + 2));
			const float light = layers[l].light * (0.6f + 0.4f * hash_unit(seed + 3)) * 255;
			const bool blue = hash_unit(seed + 4) < 0.4f;
			const int rx = (int)ceilf(size * 2 * squash), ry = (int)ceilf(size * 2);
			for (int dy = -ry; dy <= ry; ++dy)
				for (int dx = -rx; dx <= rx; ++dx)
				{
					const int x = (int)sx + dx, y = (int)sy + dy;
					if (x < 0 || x >= SIM_SPACE_W || y < 0 || y >= SIM_SPACE_H)
						continue;
					const float ddx = (x + 0.5f - sx) / squash, ddy = y + 0.5f - sy;
					const float d2 = (ddx * ddx + ddy * ddy) / (size * size);
					const float a = expf(-d2 * 1.6f);
					if (a < 0.01f)
						continue;
					float *c = scratch[y * SIM_SPACE_W + x];
					c[0] += light * a * (blue ? 0.6f : 1.0f);
					c[1] += light * a * (blue ? 0.75f : 0.97f);
					c[2] += light * a;
				}
		}
	for (int i = 0; i < SIM_SPACE_W * SIM_SPACE_H; ++i)
	{
		const Uint8 rgba[4] = { (Uint8)SDL_min(scratch[i][0], 255.0f), (Uint8)SDL_min(scratch[i][1], 255.0f),
		                        (Uint8)SDL_min(scratch[i][2], 255.0f), 255 };
		memcpy(&pixels[i], rgba, 4);
	}
	btbh_gpu_texture_update_rgba8(sim_space, (const uint8_t *)pixels, 0, 0, SIM_SPACE_W, SIM_SPACE_H);
}

// What the screen draws over the weapon simulator's box beside its models (shots without one): the
// box's pixels that differ from its picture under the models, over the scene.
static BTBHGPUTexture *pane_overlay = NULL;

static void add_pane_overlay(const RGPUShowcase *show, const float rect[4], const float box[4])
{
	const int bx = (int)box[0], by = (int)box[1], bw = (int)box[2], bh = (int)box[3];
	if (show->backdrop == NULL || bw <= 0 || bh <= 0 || bw > SCREEN_W || bh > SCREEN_H || bx < 0 || by < 0 || bx + bw > SCREEN_W ||
	    by + bh > SCREEN_H)
		return;
	if (pane_overlay == NULL)
		pane_overlay = create_texture(SCREEN_W, SCREEN_H, BTBH_GPU_TEXTURE_COLOR_SPACE_LINEAR);
	static Uint32 rgba[SCREEN_W * SCREEN_H];
	const Uint8 *picture = show->transparent != NULL ? show->transparent : ui_screen_picture();
	bool any = false;
	for (int y = 0; y < bh; ++y)
		for (int x = 0; x < bw; ++x)
		{
			const int i = (by + y) * SCREEN_W + bx + x;
			const bool drawn = picture[i] != show->backdrop[i];
			rgba[y * bw + x] = drawn ? rgb_palette[picture[i]] : 0;
			any |= drawn;
		}
	if (!any)
		return;
	btbh_gpu_texture_update_rgba8(pane_overlay, (const uint8_t *)rgba, 0, 0, (uint32_t)bw, (uint32_t)bh);
	HudQuad *q = hud_quad_add();
	if (q == NULL)
		return;
	*q = (HudQuad){ rect[0], rect[1], rect[2], rect[3], 0, 0, (float)bw / SCREEN_W, (float)bh / SCREEN_H, { 1, 1, 1, 1 }, { 1, 1, 1, 1 },
	                .texture = pane_overlay };
}

static void present_ui(const RGPUShowcase *scene);

/*
 * TYR3D_PROFILE=gpu: as for the 3D frames (gpu_profiled_present_3d), the GPU's time for each frame of the screens the
 * modern UI draws (the store with its pad's or simulator's scene, Destruct, the jukebox, the menus), every 300 frames
 * ("ui gpu:").
 */
void rgpu_present_ui(const RGPUShowcase *scene)
{
	if (!gpu_profile())
	{
		present_ui(scene);
		return;
	}
	static double frame_ms[300];
	static int frame_count = 0;
	BTBHGPUFrameTelemetrySample samples[16];
	(void)btbh_gpu_window_finish_frame_telemetry(window, samples, 16);  // (the GPU idle before this frame)
	present_ui(scene);
	const Uint32 n = btbh_gpu_window_finish_frame_telemetry(window, samples, 16);
	Uint32 last = 0;
	for (Uint32 i = 1; i < n; ++i)
		if (samples[i].frame_serial > samples[last].frame_serial)
			last = i;
	if (n > 0)
		frame_ms[frame_count++] = samples[last].fence_completion_milliseconds;
	if (frame_count == (int)COUNTOF(frame_ms))
	{
		double sum = 0;
		for (int i = 0; i < frame_count; ++i)
			sum += frame_ms[i];
		qsort(frame_ms, (size_t)frame_count, sizeof(frame_ms[0]), compare_doubles);
		printf("ui gpu: median %.3f ms/frame, mean %.3f, at most %.3f (%d frames)\n", frame_ms[frame_count / 2],
		       sum / frame_count, frame_ms[frame_count - 1], frame_count);
		frame_count = 0;
	}
}

static void present_ui(const RGPUShowcase *scene)
{
	// Destruct in 3D (destruct3d.h): its field, its units and shots, its screens over them.
	if (ui_published_is(UI_SCREEN_DESTRUCT) && destruct3d_active() && present_destruct())
		return;
	BTBHGPUWindowReport frame;
	if (!begin_frame(&frame))
		return;
	hud_quad_count = 0;
	canvas_fade[3] = 0;
	convert_pixels(ui_screen_picture(), screen_rgba);
	const float w = (float)frame.logical_width, h = (float)frame.logical_height;
	SDL_Rect dst;
	ui_fill_rect(frame.logical_width, frame.logical_height, &dst);
	// The jukebox: its visuals under its panel, instead of the original's stars (jukebox3d.h).
	bool drawn = (ui_published_is(UI_SCREEN_JUKEBOX) || ui_published_is(UI_SCREEN_ENDING)) && present_jukebox_scene(&frame);
	const bool jukebox = drawn;
	if (!jukebox)
		make_blur(screen_rgba, w, h);
	// (A picture drawn anew: the screen then only what the game drew over it, after the blur.)
	hd_picture = jukebox ? 0 : match_hd_picture(ui_screen_picture(), screen_rgba);
	if (hd_picture != 0)
		find_hd_logos(ui_screen_picture(), screen_rgba);
	if (!jukebox)
		find_hd_face(ui_screen_picture(), screen_rgba);
	btbh_gpu_texture_update_rgba8(screen_texture, (const uint8_t *)screen_rgba, 0, 0, SCREEN_W, SCREEN_H);
	const UIView view = { .w = w, .h = h, .pixel = 1.0f / text_density,
	                      .picture = { (float)dst.x, (float)dst.y, (float)dst.w, (float)dst.h } };
	const bool whole = ui_screen_whole_picture() && !jukebox;
	float pane[4], box[4];
	const bool with_scene = scene != NULL && !jukebox && ui_scene_pane(&view, pane, box);
	if (whole)
	{
		add_surround(&dst, w, h);
		if (hd_picture != 0)
		{
			add_hd_picture(0, 0, SCREEN_W, SCREEN_H, (float)dst.x, (float)dst.y, (float)dst.w, (float)dst.h, 1);
			add_hd_logos(&dst);
			hud_under = hud_quad_count;  // (under the screen's quad)
		}
		add_hd_face(0, 0, SCREEN_W, SCREEN_H, (float)dst.x, (float)dst.y, (float)dst.w, (float)dst.h, 1);
	}
	else if (!jukebox)
		add_backdrop(w, h, with_scene ? pane : NULL);
	if (with_scene)
	{
		if (ui_screen_scene() == UI_SCENE_SIM && scene->backdrop != NULL)
		{
			// The simulator: its ship and shots over deep space (stars drifting by in layers, a faint nebula,
			// sim_space) rather than its flat picture of stars; the pane shows a little more than its box, most of
			// it below, so the ship's model is whole; what the screen drew over the box (shots without models) over
			// it, where the box is in the pane.
			const float grow = 1.22f;
			const float wide[4] = { box[0] - box[2] * (grow - 1) / 2, box[1] - box[3] * 0.04f, box[2] * grow, box[3] * grow };
			make_sim_space(wide[2] / wide[3]);
			drawn = present_scene_pane(scene, pane, wide, sim_space, 1, 1, &frame);
			if (drawn)
			{
				const float inner[4] = { pane[0] + (box[0] - wide[0]) / wide[2] * pane[2], pane[1] + (box[1] - wide[1]) / wide[3] * pane[3],
				                         box[2] / wide[2] * pane[2], box[3] / wide[3] * pane[3] };
				add_pane_overlay(scene, inner, box);
			}
		}
		else
		{
			make_pad(box[2], box[3]);
			drawn = present_scene_pane(scene, pane, box, pad_texture, 1, 1, &frame);
		}
		if (!drawn)
		{
			// (The pane dark, if the scene couldn't be drawn.)
			const float px[4] = { pane[0], pane[0] + pane[2], pane[0] + pane[2], pane[0] };
			const float py[4] = { pane[1], pane[1], pane[1] + pane[3], pane[1] + pane[3] };
			const float dark[4][4] = { { 0.06f, 0.04f, 0.03f, 1 }, { 0.06f, 0.04f, 0.03f, 1 }, { 0.03f, 0.02f, 0.02f, 1 }, { 0.03f, 0.02f, 0.02f, 1 } };
			colour_quad(px, py, dark);
		}
	}
	ui_build_screen(&view);
	// (TYR3D_SOFTWARE_POINTER: the pointer in the frame, where the system's would be.)
	static int software_pointer = -1;
	if (software_pointer < 0)
		software_pointer = SDL_getenv("TYR3D_SOFTWARE_POINTER") != NULL;
	float pointer_x, pointer_y;
	if (software_pointer && mouse_pointer_window(&pointer_x, &pointer_y))
		ui_build_pointer(&view, pointer_x, pointer_y, mouseCursor);
	CanvasQuad quad = whole_screen_quad(&dst);
	quad.sharp = true;
	present_canvas(whole ? &quad : NULL, whole ? 1 : 0, false, !drawn, &frame);
	blur_ready = false;
	hd_picture = 0;
	hd_face = -1;
	hd_frame_shown = false;
}

/* --- The items' icons rendered from their 3D models (rgpu_ui_model_icon, rgpu_render_icons) ------ */

/*
 * The modern UI draws an item that has a 3D model of its own (ui.c item_icon: the store's cards and rows, the rogue run's
 * cards; build_card: the title cards' ships) as a render of that model: assets/models/icons/<model>.png, made from the
 * models (in git) by TYR3D_RENDER_ICONS (rgpu_render_icons, below), straight alpha. Each is resized to the size it is
 * drawn at in the window's pixels on a thread of its own (model_icons.h: Mitchell-Netravali from the 512-pixel render),
 * so that it is sharp at every UI scale, and drawn on those pixels, its colours multiplied by its alpha; it fades in as
 * it is ready, a frame or two after it is first asked for (the sizes it was drawn at before stand in meanwhile).
 * TYR3D_MODEL_ICONS=0 draws the sprites' pictures instead, as before (to compare).
 */
#define MODEL_ICON_TEXTURES 128
#define MODEL_ICON_FILES 256
#define MODEL_ICON_FADE 140.0f  // milliseconds
static struct
{
	char name[32];            // the model's (models.cfg), "" a free slot
	int size;                 // the window's pixels a side
	BTBHGPUTexture *texture;
	Uint64 used;              // the frame it was last drawn in (text_frames)
	Uint64 ready;             // when it was made (SDL_GetTicks), 0 to show it at once
} model_icons[MODEL_ICON_TEXTURES];
// Which models have a render (looked for once each).
static struct
{
	char name[32];
	bool exists;
} model_icon_files[MODEL_ICON_FILES];
static int model_icon_file_count = 0;

static void forget_model_icons(void)
{
	memset(model_icons, 0, sizeof(model_icons));  // (the window's textures)
}

static bool model_icons_on(void)
{
	static int on = -1;
	if (on < 0)
	{
		const char *value = SDL_getenv("TYR3D_MODEL_ICONS");
		on = value == NULL || strcmp(value, "0") != 0;
	}
	return on;
}

// The model's render (its path), if it has one.
static bool model_icon_file(const char *name, char *path, size_t size)
{
	static char dir[1024] = "";
	if (dir[0] == '\0')
	{
		char models[1024];
		snprintf(dir, sizeof(dir), "%s/icons", tyr3d_resource_dir("TYR3D_MODEL_DIR", TYR3D_MODEL_DIR, "models", models, sizeof(models)));
	}
	snprintf(path, size, "%s/%s.png", dir, name);
	for (int i = 0; i < model_icon_file_count; ++i)
		if (strcmp(model_icon_files[i].name, name) == 0)
			return model_icon_files[i].exists;
	const bool exists = SDL_GetPathInfo(path, NULL);
	if (model_icon_file_count < MODEL_ICON_FILES)
	{
		SDL_strlcpy(model_icon_files[model_icon_file_count].name, name, sizeof(model_icon_files[0].name));
		model_icon_files[model_icon_file_count++].exists = exists;
	}
	return exists;
}

static void model_icon_missing(const char *name)
{
	for (int i = 0; i < model_icon_file_count; ++i)
		if (strcmp(model_icon_files[i].name, name) == 0)
			model_icon_files[i].exists = false;
}

// A slot for a new icon: a free one, else the one drawn longest ago (not in this frame), its texture released.
static int model_icon_slot(void)
{
	int oldest = -1;
	for (int i = 0; i < MODEL_ICON_TEXTURES; ++i)
	{
		if (model_icons[i].name[0] == '\0')
			return i;
		if (model_icons[i].used != text_frames && (oldest < 0 || model_icons[i].used < model_icons[oldest].used))
			oldest = i;
	}
	if (oldest >= 0)
	{
		btbh_gpu_texture_destroy(model_icons[oldest].texture);
		memset(&model_icons[oldest], 0, sizeof(model_icons[oldest]));
	}
	return oldest;
}

bool rgpu_ui_model_icon(int model, float x, float y, float w, float h, float alpha)
{
	if (!model_icons_on() || window == NULL || model < 0 || model >= m3d_model_count)
		return false;
	const char *name = m3d_models[model].name;
	char path[1200];
	if (name[0] == '\0' || !model_icon_file(name, path, sizeof(path)))
		return false;
	// The square in the middle of the box, on the window's pixels.
	const float side = SDL_min(w, h);
	const int size = SDL_clamp((int)lroundf(side * text_density), 4, 1024);
	const float points = size / text_density;
	const float qx = snap_to_pixel(x + (w - points) / 2), qy = snap_to_pixel(y + (h - points) / 2);
	int shown = -1, other = -1;
	for (int i = 0; i < MODEL_ICON_TEXTURES; ++i)
		if (model_icons[i].texture != NULL && strcmp(model_icons[i].name, name) == 0)
		{
			if (model_icons[i].size == size)
				shown = i;
			else if (other < 0 || abs(model_icons[i].size - size) < abs(model_icons[other].size - size))
				other = i;
		}
	Uint8 *pixels;
	const Uint64 asked = SDL_GetPerformanceCounter();
	if (shown < 0 && model_icon_take(path, size, &pixels))
	{
		if (pixels == NULL)
		{
			fprintf(stderr, "warning: model icon %s can't be read\n", path);
			model_icon_missing(name);
			return false;
		}
		const int slot = model_icon_slot();
		BTBHGPUTextureReport report;
		BTBHGPUTexture *texture = slot < 0 ? NULL
		                        : btbh_gpu_window_texture_create_rgba8_ex(window, pixels, (uint32_t)size, (uint32_t)size, 0,
		                                                                  BTBH_GPU_TEXTURE_FILTER_LINEAR, BTBH_GPU_TEXTURE_WRAP_CLAMP,
		                                                                  BTBH_GPU_TEXTURE_COLOR_SPACE_LINEAR, &report);
		SDL_free(pixels);
		if (texture != NULL)
		{
			SDL_strlcpy(model_icons[slot].name, name, sizeof(model_icons[slot].name));
			model_icons[slot].size = size;
			model_icons[slot].texture = texture;
			model_icons[slot].ready = other >= 0 ? 0 : SDL_GetTicks();
			shown = slot;
			static int profile = -1;  // (TYR3D_PROFILE: what making its texture took the main thread)
			if (profile < 0)
				profile = SDL_getenv("TYR3D_PROFILE") != NULL;
			if (profile)
				printf("model icon: %s at %d pixels, its texture made in %.3f ms\n", name, size,
				       (SDL_GetPerformanceCounter() - asked) * 1000.0 / SDL_GetPerformanceFrequency());
		}
	}
	const int i = shown >= 0 ? shown : other;
	if (i < 0)
		return true;  // (being made)
	model_icons[i].used = text_frames;
	float a = alpha;
	if (i == shown && model_icons[i].ready != 0)
		a *= SDL_clamp((SDL_GetTicks() - model_icons[i].ready) / MODEL_ICON_FADE, 0.0f, 1.0f);
	HudQuad *q = hud_quad_add();
	if (q != NULL)
		*q = (HudQuad){ qx, qy, points, points, 0, 0, 1, 1, { a, a, a, a }, { a, a, a, a }, .texture = model_icons[i].texture,
		                .premultiplied = true };
	return true;
}

/*
 * TYR3D_RENDER_ICONS=<dir>: the items' icons rendered from their models into <dir>/<model>.png. One three-quarter view for
 * every model: turned ICON_YAW clockwise and its front tilted ICON_TILT up towards a camera that looks straight down, as
 * the store's pad's does, so that it is lit as the pad's ship is (the sun from the upper left, the sky, its own shadows,
 * the bloom). Each is rendered twice into the window's left square, over black and over grey: the difference is its alpha
 * (glass shows through), over black its colours with the light round what glows; then it is framed by what shows of it,
 * its longer side ICON_SIZE less the margins in every icon, and resized from three to four times that (Mitchell-
 * Netravali). The picture: straight alpha, the colours as the canvas blends them (sRGB, rendered over black divided by
 * the alpha, which is at least the brightest colour: the glow round a lamp is light over the well).
 */
#define ICON_SIZE 512
#define ICON_MARGIN 0.06f   // round the model's longer side, of the icon's
#define ICON_YAW 30.0f      // degrees, clockwise
#define ICON_TILT 35.0f     // degrees: the camera 55 degrees above the model's horizon
#define ICON_FOV 20.0f      // degrees across the fitted square: a gentle perspective
#define ICON_RADIUS 50.0f   // the sphere round the model's bounds (world units), its middle that high + 4: in the shadows' reach
#define ICON_GREY 191       // the second background (0.75 in linear light: below the bloom's threshold)

static float icon_linear[256];

// The window's left square (its height) of one of an icon's renders, over a background of grey: RGBA, rows from the top.
static Uint8 *icon_render(const RGPUIcon *icon, const LoadedModel *loaded, Uint8 grey, int *side)
{
	BTBHGPUWindowReport frame;
	if (!begin_frame(&frame))
		return NULL;
	const float W = (float)frame.logical_width, H = (float)frame.logical_height;
	const float fx = (float)l3d_field_x(), fw = (float)l3d_field_w();
	// The square fitted round the sphere: the camera fits the field's width at the sphere's middle into a square that
	// many times larger than the window's left square, around it.
	const float zoom = 0.47f * fw / ICON_RADIUS;
	const float mid = -1 + H / W;
	const float ndc_rect[4] = { mid - zoom * H / W, -zoom, mid + zoom * H / W, zoom };
	const float height = ICON_RADIUS + 4;
	const float tilt = rgpu_camera.tilt_degrees, fov = rgpu_camera.fov_degrees;
	rgpu_camera.tilt_degrees = 0;
	rgpu_camera.fov_degrees = ICON_FOV;
	const Camera3D camera = fit_camera(height, 1.0f, ndc_rect, false, false);
	rgpu_camera.tilt_degrees = tilt;
	rgpu_camera.fov_degrees = fov;
	shown_view.valid = false;

	Uint32 palette[256];
	for (int i = 0; i < 256; ++i)
	{
		const int c = icon->ramp >= 0 ? (icon->ramp << 4 | (i & 0x0f)) & 0xff : i;
		palette[i] = pack_rgba(colors[c].r, colors[c].g, colors[c].b);
	}
	const float radius = sqrtf(loaded->half[0] * loaded->half[0] + loaded->half[1] * loaded->half[1] + loaded->half[2] * loaded->half[2]);
	const Mat4 chain[] = { mat4_translation(fx + fw / 2, height, L3D_PLAYFIELD_H - fw / 2), mat4_rotation(0, -ICON_TILT),
	                       mat4_rotation(1, -ICON_YAW) };
	const Mat4 placement = mat4_chain((int)COUNTOF(chain), chain);
	int instance_count = 0, batch_count = 0;
	add_showcase_model(icon->model, &placement, ICON_RADIUS / radius * loaded->footprint, 1.0f, palette, &instance_count, &batch_count);
	static Uint8 casts_shadow[MAX_BATCHES];
	const bool shadows = shadows_enabled();
	for (int i = 0; i < batch_count; ++i)
		casts_shadow[i] = shadows;
	BTBHGPUSceneLighting lighting;
	scene_lighting(&lighting, &camera, shadows, false);
	BTBHGPUScenePost post;
	Uint32 render_w, render_h;
	scene_post(&post, &frame, &render_w, &render_h);
	render_w = frame.drawable_width;  // (the window's own pixels: not scaled up)
	render_h = frame.drawable_height;
	post.upscale_mode = BTBH_GPU_SCENE_UPSCALE_LINEAR;
	post.anti_aliasing = 0;  // (made from three to four times its size; both renders alike)
	BTBHGPUSceneReport scene_report;
	if (batch_count == 0 ||
	    btbh_gpu_window_scene_present_instances_with_visibility(window,
	        shader_paths[SH_MODEL_VERT], shader_paths[SH_ANIMATED_MODEL_VERT],
	        shader_paths[SH_SHADOW_FAST_VERT], shader_paths[SH_SHADOW_FAST_FRAG],
	        shader_paths[SH_SHADOW_VERT], shader_paths[SH_ANIMATED_SHADOW_VERT], shader_paths[SH_SHADOW_FRAG],
	        shader_paths[SH_MODEL_FRAG], shader_paths[SH_MODEL_UNSHADOWED_FRAG],
	        shader_paths[SH_POST_VERT], shader_paths[SH_POST_FRAG],
	        shader_format, render_w, render_h,
	        camera.view_projection.m, camera.right, camera.up, camera.position,
	        &lighting, &post, instances, instance_count, instance_count, batches, NULL, casts_shadow, (uint32_t)batch_count,
	        grey, grey, grey, 255, &scene_report) != BTBH_GPU_OK)
	{
		fprintf(stderr, "warning: icons: %s: the scene failed: %s\n", m3d_models[icon->model].name, batch_count == 0 ? "no model" : scene_report.message);
		present_canvas(NULL, 0, false, true, &frame);
		return NULL;
	}
	btbh_gpu_window_request_presented_frame_readback(window);
	BTBHGPUCanvasPass pass;
	memset(&pass, 0, sizeof(pass));
	BTBHGPUCanvasReport report;
	if (btbh_gpu_window_canvas_present(window, shader_paths[SH_CANVAS_VERT], shader_paths[SH_CANVAS_FRAG],
	                                   shader_paths[SH_CANVAS_TEXTURED_FRAG], shader_format, NULL, 0, NULL, 0, &pass, 1, &report) != BTBH_GPU_OK)
	{
		fprintf(stderr, "warning: icons: canvas present failed: %s\n", report.message);
		return NULL;
	}
	const size_t needed = (size_t)frame.drawable_width * frame.drawable_height * 4;
	if (needed > readback_capacity)
	{
		free(readback_rgba);
		readback_rgba = malloc(needed);
		readback_capacity = readback_rgba != NULL ? needed : 0;
	}
	BTBHGPUCanvasReport readback;
	if (readback_rgba == NULL ||
	    btbh_gpu_window_readback_presented_frame(window, readback_rgba, (uint32_t)readback_capacity, &readback) != BTBH_GPU_OK)
	{
		fprintf(stderr, "warning: icons: no readback\n");
		return NULL;
	}
	const int s = (int)SDL_min(readback.drawable_width, readback.drawable_height);
	Uint8 *square = malloc((size_t)s * s * 4);
	if (square == NULL)
		return NULL;
	for (int y = 0; y < s; ++y)
		memcpy(square + (size_t)y * s * 4, readback_rgba + (size_t)y * readback.drawable_width * 4, (size_t)s * 4);
	*side = s;
	return square;
}

bool rgpu_render_icons(const char *dir, const RGPUIcon *icons, int count)
{
	if (window == NULL)
		return false;
	SDL_CreateDirectory(dir);
	for (int i = 0; i < 256; ++i)
	{
		const float c = i / 255.0f;  // (the post's sRGB, inverted)
		icon_linear[i] = powf((c + 0.055f) / 1.055f, 2.4f);
	}
	icon_linear[0] = 0;
	sync_model_cache();
	int written = 0;
	for (int n = 0; n < count; ++n)
	{
		const RGPUIcon *icon = &icons[n];
		const LoadedModel *loaded = icon->model >= 0 && icon->model < m3d_model_count ? get_model(icon->model) : NULL;
		if (loaded == NULL || loaded->footprint <= 0)
		{
			fprintf(stderr, "warning: icons: model %d isn't there\n", icon->model);
			continue;
		}
		const char *name = m3d_models[icon->model].name;
		int side = 0, side_grey = 0;
		Uint8 *black = icon_render(icon, loaded, 0, &side);
		Uint8 *grey = black != NULL ? icon_render(icon, loaded, ICON_GREY, &side_grey) : NULL;
		float *premultiplied = black != NULL && grey != NULL && side == side_grey ? malloc((size_t)side * side * 4 * sizeof(float)) : NULL;
		float *resized = malloc((size_t)ICON_SIZE * ICON_SIZE * 4 * sizeof(float));
		Uint8 *png = malloc((size_t)ICON_SIZE * ICON_SIZE * 4);
		bool ok = premultiplied != NULL && resized != NULL && png != NULL;
		int x0 = side, y0 = side, x1 = -1, y1 = -1;
		if (ok)
		{
			// The backgrounds: the square's corners.
			float under_black[3] = { 0, 0, 0 }, under_grey[3] = { 0, 0, 0 };
			const int corners[4] = { 0, side - 1, (side - 1) * side, side * side - 1 };
			for (int k = 0; k < 4; ++k)
				for (int c = 0; c < 3; ++c)
				{
					under_black[c] += icon_linear[black[corners[k] * 4 + c]] / 4;
					under_grey[c] += icon_linear[grey[corners[k] * 4 + c]] / 4;
				}
			const float range = (under_grey[0] - under_black[0]) + (under_grey[1] - under_black[1]) + (under_grey[2] - under_black[2]);
			ok = range > 0.5f;
			for (int p = 0; ok && p < side * side; ++p)
			{
				float difference = 0;
				for (int c = 0; c < 3; ++c)
				{
					const float b = icon_linear[black[p * 4 + c]];
					difference += icon_linear[grey[p * 4 + c]] - b;
					premultiplied[p * 4 + c] = SDL_max(b - under_black[c], 0.0f);
				}
				const float a = SDL_clamp(1 - difference / range, 0.0f, 1.0f);
				premultiplied[p * 4 + 3] = a;
				if (a > 0.04f)
				{
					const int x = p % side, y = p / side;
					x0 = SDL_min(x0, x);
					x1 = SDL_max(x1, x);
					y0 = SDL_min(y0, y);
					y1 = SDL_max(y1, y);
				}
			}
			if (!ok)
				fprintf(stderr, "warning: icons: %s: the backgrounds aren't apart (%.3f)\n", name, range);
		}
		if (ok && x1 < 0)
		{
			fprintf(stderr, "warning: icons: %s: nothing shows\n", name);
			ok = false;
		}
		if (ok)
		{
			if (x0 == 0 || y0 == 0 || x1 == side - 1 || y1 == side - 1)
				fprintf(stderr, "warning: icons: %s: cut at the render's edge\n", name);
			// Framed: its longer side ICON_SIZE less the margins, in the middle.
			const double longer = SDL_max(x1 + 1 - x0, y1 + 1 - y0), span = longer / (1 - 2 * ICON_MARGIN);
			const double mx = (x0 + x1 + 1) / 2.0, my = (y0 + y1 + 1) / 2.0;
			ok = model_icon_resample(premultiplied, side, side, mx - span / 2, my - span / 2, mx + span / 2, my + span / 2, resized, ICON_SIZE);
			for (int p = 0; ok && p < ICON_SIZE * ICON_SIZE; ++p)
			{
				float colour[3], brightest = 0;
				for (int c = 0; c < 3; ++c)
				{
					const float v = SDL_clamp(resized[p * 4 + c], 0.0f, 1.0f);
					colour[c] = SDL_max(1.055f * powf(v, 1 / 2.4f) - 0.055f, 0.0f);
					brightest = SDL_max(brightest, colour[c]);
				}
				const float a = SDL_max(SDL_clamp(resized[p * 4 + 3], 0.0f, 1.0f), brightest);
				for (int c = 0; c < 3; ++c)
					png[p * 4 + c] = a > 0 ? (Uint8)lroundf(SDL_min(colour[c] / a, 1.0f) * 255) : 0;
				png[p * 4 + 3] = (Uint8)lroundf(a * 255);
			}
			char path[1200];
			snprintf(path, sizeof(path), "%s/%s.png", dir, name);
			ok = ok && btbh_gpu_write_png_rgba8(path, ICON_SIZE, ICON_SIZE, png) == BTBH_GPU_OK;
			if (ok)
			{
				++written;
				printf("icons: %s: %dx%d of a %d square, written\n", name, x1 + 1 - x0, y1 + 1 - y0, side);
			}
			else
				fprintf(stderr, "warning: icons: %s: not written\n", path);
		}
		free(black);
		free(grey);
		free(premultiplied);
		free(resized);
		free(png);
	}
	printf("icons: %d of %d written into %s\n", written, count, dir);
	return written == count;
}
