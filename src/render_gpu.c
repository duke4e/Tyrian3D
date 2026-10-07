/*
 * Tyrian3D: GPU presentation through the BTBH renderer. See render_gpu.h.
 */
#include "render_gpu.h"

#include "background3d.h"
#include "backgrnd.h"
#include "config.h"
#include "devtools.h"
#include "fonthand.h"
#include "mainint.h"
#include "player.h"
#include "models3d.h"
#include "palette.h"
#include "particles3d.h"
#include "paths3d.h"
#include "settings3d.h"
#include "sprite.h"
#include "varz.h"
#include "volume3d.h"

#include <btbh_gpu/btbh_gpu.h>

#include "cgltf.h"

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
static BTBHGPUTexture *layer_atlas = NULL;     // 3D layers, 320 x ATLAS_H
static BTBHGPUTexture *tile_atlas = NULL;      // background map tiles (background3d.h)
static BTBHGPUTexture *white_texture = NULL;   // 1x1, for flat-coloured quads
static BTBHGPUTexture *particle_texture = NULL;  // a soft round dot
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
static Uint32 hash_colors(const Uint32 colors[256]);

static Uint32 screen_rgba[SCREEN_W * SCREEN_H];

// Darkness over the whole window on spotlight levels (see build_spotlight).
#define SPOT_W 320
#define SPOT_H 200
static BTBHGPUTexture *spot_texture = NULL;
static Uint32 spot_rgba[SPOT_W * SPOT_H];
static Uint32 atlas_rgba[L3D_WIDTH * ATLAS_H];

// Water glints (the renderer's GLINTS surface): masks of the water in the layers and the tiles,
// in the blue channel, laid out as layer_atlas and tile_atlas.
static BTBHGPUTexture *layer_water = NULL;
static BTBHGPUTexture *tile_water = NULL;
static BTBHGPUTexture *composed_water = NULL;
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

static void set_glints(BTBHGPUSceneGeometryBatch *b, BTBHGPUTexture *mask)
{
	if (!settings3d.effects)
		return;
	b->surface_variant = BTBH_GPU_SCENE_SURFACE_GLINTS;
	b->orm_texture = mask;
	b->surface_time = glint_time;
	memcpy(b->surface_parameters0, glint_parameters, sizeof(glint_parameters));
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
	spot_texture = create_texture_filtered(SPOT_W, SPOT_H, BTBH_GPU_TEXTURE_COLOR_SPACE_LINEAR, BTBH_GPU_TEXTURE_FILTER_LINEAR);
	layer_atlas = create_texture(L3D_WIDTH, ATLAS_H, BTBH_GPU_TEXTURE_COLOR_SPACE_SRGB);
	layer_water = create_texture(L3D_WIDTH, ATLAS_H, BTBH_GPU_TEXTURE_COLOR_SPACE_LINEAR);
	tile_atlas = create_texture(B3D_ATLAS_W, B3D_ATLAS_H * TILE_PAGES, BTBH_GPU_TEXTURE_COLOR_SPACE_SRGB);
	tile_water = create_texture(B3D_ATLAS_W, B3D_ATLAS_H * TILE_PAGES, BTBH_GPU_TEXTURE_COLOR_SPACE_LINEAR);
	white_texture = create_texture(1, 1, BTBH_GPU_TEXTURE_COLOR_SPACE_SRGB);
	composed_texture = create_texture(COMPOSED_SIZE, COMPOSED_SIZE * L3D_MAX_BACKGROUNDS, BTBH_GPU_TEXTURE_COLOR_SPACE_SRGB);
	composed_water = create_texture(COMPOSED_SIZE, COMPOSED_SIZE * L3D_MAX_BACKGROUNDS, BTBH_GPU_TEXTURE_COLOR_SPACE_LINEAR);
	const Uint32 white = 0xffffffff;
	btbh_gpu_texture_update_rgba8(white_texture, (const uint8_t *)&white, 0, 0, 1, 1);
	quad_mesh = create_quad_mesh(1, 1);
	billboard_mesh = create_billboard_mesh();
	particle_texture = create_particle_texture();
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

	if (window != NULL)
		btbh_gpu_window_destroy(window);  // releases every resource the window owns
	window = NULL;
	screen_texture = NULL;
	layer_atlas = NULL;
	layer_water = NULL;
	tile_water = NULL;
	composed_water = NULL;
	tile_atlas = NULL;
	white_texture = NULL;
	particle_texture = NULL;
	billboard_mesh = NULL;
	composed_texture = NULL;
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

// A rectangle of the screen texture (in screen pixels) drawn to a rectangle of the window.
typedef struct
{
	float x, y, w, h;
	float source_x, source_y, source_w, source_h;
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
	BTBHGPUCanvasVertex vertices[6 * (MAX_CANVAS_QUADS + 1)];
	BTBHGPUCanvasBatch batches_2d[2] = { { 0 } };
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
		push_quad(vertices + vertex_count + 6 * i, &quads[i], SCREEN_W, SCREEN_H);
	BTBHGPUCanvasBatch *batch = &batches_2d[batch_count_2d++];
	batch->first_vertex = vertex_count;
	batch->vertex_count = 6 * (uint32_t)quad_count;
	batch->texture = screen_texture;
	batch->blend_mode = BTBH_GPU_CANVAS_BLEND_ALPHA;
	vertex_count += batch->vertex_count;

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

// The part of the horizontal plane at the given height that the window shows (the playfield
// and everything around it), as a rectangle {x0, z0, x1, z1} in game screen coordinates.
static void plane_footprint(const Camera3D *camera, float height, float rect[4])
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
			s = (-BACKGROUND_AHEAD - camera->position[2]) / ray[2];
		else
			continue;
		const float x = camera->position[0] + ray[0] * s;
		const float z = SDL_max(camera->position[2] + ray[2] * s, -BACKGROUND_AHEAD);
		rect[0] = SDL_min(rect[0], x);
		rect[1] = SDL_min(rect[1], z);
		rect[2] = SDL_max(rect[2], x);
		rect[3] = SDL_max(rect[3], z);
	}
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
			for (int y = L3D_OVERSCAN; y < L3D_OVERSCAN + L3D_PLAYFIELD_H; ++y)
				for (int x = L3D_PLAYFIELD_X; x < L3D_PLAYFIELD_X + L3D_PLAYFIELD_W; ++x)
				{
					const int i = y * L3D_WIDTH + x;
					if (!layer->cover[i] || (empty_zero && layer->index[i] == 0))
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
			Uint32 *water = layer_water_rgba + (slots) * ATLAS_SLOT_H * L3D_WIDTH;
			for (int i = 0; i < L3D_WIDTH * L3D_ROWS; ++i)
				water[i] = background_layer(layer->type) && dst[i] != 0 ? water_mask(dst[i]) : 0;
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

static Layout3D layout_3d(float window_w, float window_h, const SDL_Rect *dst)
{
	Layout3D layout = { .split = true };
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
	quads[0] = (CanvasQuad){ p[0], p[1], p[2], p[3], PANEL_X, 0, SCREEN_W - PANEL_X, SCREEN_H };
	quads[1] = (CanvasQuad){ f[0], f[1], f[2], f[3], 0, 0, L3D_PLAYFIELD_W, L3D_PLAYFIELD_H };
	return 2;
}

// In-game messages (JE_drawTextWindow) are written over the bar below the playfield, which the
// split layout leaves out. While one shows, it is drawn again, as the game draws it, near the
// bottom of the playfield, with a shadow.
#define MESSAGE_Y 189
#define MESSAGE_H 10
#define MESSAGE_AT (L3D_PLAYFIELD_H - 22)

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
}

static void present_3d(const SDL_Surface *hud, const L3DFrame *frame, const SDL_Rect *dst);

void rgpu_present_3d_ahead(const SDL_Surface *hud, const L3DFrame *frame, const SDL_Rect *dst, float ticks)
{
	ahead = ticks;
	present_3d(hud, frame, dst);
	ahead = 0;
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

static void write_instance(float *instance, const Mat4 *transform, float brightness)
{
	memcpy(instance, transform->m, 16 * sizeof(float));
	instance[16] = instance[17] = instance[18] = brightness;
	instance[19] = 1;
	instance[20] = instance[21] = instance[22] = instance[23] = 0;
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
                       L3D_MAX_GLOWS + DEEP_STARS)
// Background tiles: per background, a batch for each of its cells mirrored or not and fading
// either way or not at all (B3D_ATLAS_CELLS covers the cells of all three backgrounds).
#define MAX_BATCHES (L3D_MAX_LAYERS + M3D_MAX_MODELS * 4 + L3D_MAX_OBJECTS + B3D_ATLAS_CELLS * 6 + 1 + L3D_MAX_BACKGROUNDS + P3D_KIND_COUNT + 1 + 1)

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
				const float height = l3d_layer_height(object->layer) * rgpu_camera.height_scale + object->height;
				Mat4 mirror_x = mat4_identity();
				if (mirror)
					mirror_x.m[0] = -1;
				const Mat4 chain[] = {
					mat4_translation(object->x + object->vx * ahead, height, object->y + object->vy * ahead),
					mirror_x,
					mat4_rotation(1, -object->yaw),
					mat4_rotation(2, -object->roll),
					mat4_rotation(1, model->yaw),
					mat4_rotation(0, model->pitch),
					mat4_rotation(2, model->roll),
					mat4_scaling(scale),
					mat4_translation(-loaded->center[0], -loaded->center[1], -loaded->center[2]),
				};
				Mat4 transform = mat4_chain((int)COUNTOF(chain), chain);
				// Nothing sinks into the ground: models centred on their layer's height (items on
				// the ground enemies' layer) are lifted by what their turned bounds reach below it.
				const float reach = fabsf(transform.m[1]) * loaded->half[0] + fabsf(transform.m[5]) * loaded->half[1] +
				                    fabsf(transform.m[9]) * loaded->half[2];
				if (height - reach < 0.3f)
					transform.m[13] += 0.3f - (height - reach);
				write_instance(instances + *instance_count * 24, &transform, 1.0f);
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
	BTBHGPUCustomMesh *meshes[V3D_STYLE_COUNT][2][SHEET_SPRITES + 1];  // [style][large][sprite index]
	bool mesh_built[V3D_STYLE_COUNT][2][SHEET_SPRITES + 1];
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
			for (int i = 0; i <= SHEET_SPRITES; ++i)
				if (entry->meshes[s][l][i] != NULL)
					btbh_gpu_custom_mesh_destroy(entry->meshes[s][l][i]);
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

static BTBHGPUCustomMesh *get_volume_mesh(VolumeSheet *entry, unsigned int sprite, bool large, int style)
{
	if (sprite == 0 || sprite > SHEET_SPRITES || style < 0 || style >= V3D_STYLE_COUNT)
		return NULL;
	BTBHGPUCustomMesh **mesh = &entry->meshes[style][large][sprite];
	if (!entry->mesh_built[style][large][sprite])
	{
		entry->mesh_built[style][large][sprite] = true;
		static V3DVertex vertices[V3D_MAX_VERTICES];
		static Uint32 indices[V3D_MAX_INDICES];
		int vertex_count = 0;
		const float length = sqrtf(sun_direction[0] * sun_direction[0] + sun_direction[1] * sun_direction[1] +
		                           sun_direction[2] * sun_direction[2]);
		const float light[3] = { -sun_direction[0] / length, -sun_direction[1] / length, -sun_direction[2] / length };
		const int index_count = v3d_build_mesh(entry->indices, entry->cover, sprite, large, (V3DStyle)style, light,
		                                       vertices, &vertex_count, indices);
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

static void add_volume_batches(const L3DFrame *frame, int *instance_count, int *batch_count)
{
	Uint32 colors[256];
	frame_colors(frame, colors);
	const Uint32 colors_hash = hash_colors(colors);

	bool done[L3D_MAX_OBJECTS] = { false };
	for (int o = 0; o < frame->object_count; ++o)
	{
		const L3DObject *first = &frame->objects[o];
		if (done[o] || first->model != L3D_VOLUME)
			continue;

		VolumeSheet *entry = get_volume_sheet(first->sheet, colors, colors_hash);
		BTBHGPUCustomMesh *mesh = entry != NULL ? get_volume_mesh(entry, first->sprite, first->large, first->style) : NULL;

		// All objects showing the same sprite in the same state share one batch.
		const int first_instance = *instance_count;
		for (int p = o; p < frame->object_count; ++p)
		{
			const L3DObject *object = &frame->objects[p];
			if (done[p] || object->model != L3D_VOLUME || object->sheet != first->sheet ||
			    object->sprite != first->sprite || object->large != first->large || object->style != first->style ||
			    object->filter != first->filter || object->ghost != first->ghost)
				continue;
			done[p] = true;
			if (mesh == NULL || *instance_count >= MAX_INSTANCES)
				continue;

			const float height = l3d_layer_height(object->layer) * rgpu_camera.height_scale + object->height;
			const Mat4 chain[] = {
				mat4_translation(object->x + object->vx * ahead, height, object->y + object->vy * ahead),
				mat4_rotation(1, -object->yaw),
				mat4_rotation(2, -object->roll),
			};
			const Mat4 transform = mat4_chain((int)COUNTOF(chain), chain);
			write_instance(instances + *instance_count * 24, &transform, 1.0f);
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
		b->albedo_texture = filtered_volume_texture(entry, colors, colors_hash, first->filter);
		b->unlit_enabled = 1;  // shaded by the mesh's vertex colours (v3d_build_mesh)
		b->alpha_cutoff = 0.5f;
		if (first->ghost)
		{
			b->transparency_enabled = 1;
			b->albedo_alpha = 128;
			b->alpha_cutoff = 0.2f;
		}
	}
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
	btbh_gpu_texture_update_rgba8(tile_atlas, (const uint8_t *)tile_rgba, 0, page * B3D_ATLAS_H, B3D_ATLAS_W, B3D_ATLAS_H);
	for (int i = 0; i < B3D_ATLAS_W * B3D_ATLAS_H; ++i)
		tile_rgba[i] = tile_rgba[i] != 0 ? water_mask(tile_rgba[i]) : 0;
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
static void add_background_batches(const L3DFrame *frame, const bool *composed, const Camera3D *camera,
                                   const float *heights, const Uint32 colors[256], int *instance_count, int *batch_count)
{
	if (frame->background_count == 0)
		return;
	++tile_frame;

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
		// A composed (filtered) background covers only so much; its tiles, in the filters' colours,
		// go on beyond it, a little below so that the composed image wins where it is.
		const float height = heights[background->layer] - TILE_BELOW_LAYER - (composed[i] ? 0.1f : 0.0f);
		const float shift = background_speed[background->set & 3] * ahead;
		float rect[4];
		plane_footprint(camera, height, rect);
		if (rect[0] > rect[2])
			continue;
		rect[1] -= shift;  // what has scrolled into view
		rect[3] -= shift;

		// Tiles take the colours the game gives them through blending and the level's filters.
		Uint8 remap[256];
		Uint32 page_colors[256];
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
		for (int t = first; t < tile_count; ++t)
		{
			tiles[t].z += shift;
			tile_height[t] = height;
			// Batch key: atlas page and cell, mirrored, fading.
			tile_key[t] = ((page * B3D_ATLAS_CELLS + tiles[t].cell) * 2 + tiles[t].flipped) * 3 + tiles[t].fade + 1;
		}
	}

	enum { KEYS = TILE_PAGES * B3D_ATLAS_CELLS * 6 };
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
		const int fade = key % 3 - 1;
		const bool flipped = (key / 3 & 1) != 0;
		const int cell = key / 6 % B3D_ATLAS_CELLS, page = key / 6 / B3D_ATLAS_CELLS;
		int ox, oy;
		b3d_cell_origin(cell, &ox, &oy);
		oy += page * B3D_ATLAS_H;

		BTBHGPUSceneGeometryBatch *b = &batches[(*batch_count)++];
		init_batch(b);
		b->kind = BTBH_GPU_SCENE_GEOMETRY_CUSTOM_MESH;
		b->custom_mesh = fade == 0 ? quad_mesh : fade_meshes[fade > 0];
		b->first_instance = key_next[key] - key_count[key];
		b->instance_count = key_count[key];
		b->albedo_texture = tile_atlas;
		b->uv_scale_x = (flipped ? -1.0f : 1.0f) * B3D_TILE_W / B3D_ATLAS_W;
		b->uv_scale_y = B3D_TILE_H / atlas_h;
		b->uv_offset_x = (float)(ox + (flipped ? B3D_TILE_W : 0)) / B3D_ATLAS_W;
		b->uv_offset_y = oy / atlas_h;
		b->unlit_enabled = 1;
		b->alpha_cutoff = 0.5f;
		set_glints(b, tile_water);
	}
	*instance_count = next;
}

// The starfield sits below background 1, whose colour 0 lets it through as in the game.
#define STARS_BELOW_LAYER 0.3f

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
	const float ground = heights[frame->star_layer] - STARS_BELOW_LAYER;
	for (int k = 0; k < DEEP_STAR_LAYERS; ++k)
	{
		const float height = ground - deep_star_layers[k].depth * rgpu_camera.height_scale;
		float rect[4];
		plane_footprint(camera, height, rect);
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
			write_instance(instance, &transform, 1.0f);

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

	const float height = heights[frame->star_layer] - STARS_BELOW_LAYER;
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
			const float t = SDL_clamp(p->age / p->life, 0.0f, 1.0f);
			Mat4 transform = mat4_identity();
			transform.m[0] = transform.m[5] = transform.m[10] = p->size;
			const float age = SDL_max(0.0f, SDL_min(ahead, p->age + ahead));  // not before it appears
			transform.m[12] = p->x + p->vx * age;
			transform.m[13] = SDL_max(0.0f, p->height + p->vheight * age) * rgpu_camera.height_scale;
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
		b->albedo_texture = particle_texture;
		b->billboard_mode = BTBH_GPU_SCENE_BILLBOARD_FRONT;
		b->unlit_enabled = 1;
		b->transparency_enabled = 1;
		b->blend_mode = kind == P3D_GLOW ? BTBH_GPU_SCENE_BLEND_ADDITIVE : BTBH_GPU_SCENE_BLEND_ALPHA;
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
	plane_footprint(camera, 0.0f, rect);
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
	const bool new_frame = presented_frame != l3d_frame_number || ahead == 0;
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

	if (new_frame)
	{
		build_hud(hud, frame, layout.split);
		btbh_gpu_texture_update_rgba8(screen_texture, (const uint8_t *)screen_rgba, 0, 0, SCREEN_W, SCREEN_H);
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

	int instance_count = 0;
	int batch_count = 0;
	for (int l = 0; l < frame->layer_count; ++l)
	{
		const int slot = slot_of_layer[l];
		if (slot < 0)
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
	const int first_object_batch = batch_count;
	add_object_batches(frame, colors, upside_down, &instance_count, &batch_count);
	add_volume_batches(frame, &instance_count, &batch_count);

	// Shadows: objects (models and volumetric sprites) cast the sun's shadow; the unlit surfaces
	// (layers, background tiles, volumetric sprites) darken in it, lit models are shaded by it.
	static Uint8 casts_shadow[MAX_BATCHES];
	const bool shadows = shadows_enabled();
	for (int i = 0; i < batch_count; ++i)
	{
		casts_shadow[i] = shadows && i >= first_object_batch;
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

	// Models are lit by the sun and the sky; layers and volumetric sprites are unlit. The sun is
	// strong against the sky, as in the sprites' own shading: lit from the upper left, with
	// clear highlights and shadows.
	BTBHGPUSceneLighting lighting = { 0 };
	lighting.spot_falloff = 1.0f;
	lighting.spot_inner_cutoff = 0.92388f;
	lighting.spot_outer_cutoff = 0.70711f;
	lighting.spot_range = 50.0f;
	lighting.ambient_red = 0.55f;
	lighting.ambient_green = 0.58f;
	lighting.ambient_blue = 0.68f;
	lighting.ambient_energy = 0.6f;
	const float *sun = sun_direction;
	const float sun_length = sqrtf(sun[0] * sun[0] + sun[1] * sun[1] + sun[2] * sun[2]);
	lighting.directional_x = sun[0] / sun_length;
	lighting.directional_y = sun[1] / sun_length;
	lighting.directional_z = sun[2] / sun_length;
	lighting.directional_energy = SUN_ENERGY;
	lighting.directional_red = 1.0f;
	lighting.directional_green = 0.98f;
	lighting.directional_blue = 0.94f;
	set_environment(&lighting);
	const char *energies = SDL_getenv("TYR3D_LIGHTING");
	float sky_fill = SKY_FILL;
	if (energies != NULL)
		sscanf(energies, "%f,%f", &lighting.directional_energy, &sky_fill);
	for (int i = 0; i < 27; ++i)
		lighting.irradiance_sh[i] *= sky_fill;
	if (shadows)
	{
		lighting.directional_shadow_enabled = 1;
		lighting.directional_shadow_softness = 1.0f;
		shadow_view_projection(&camera, lighting.directional_shadow_view_projection);
	}

	BTBHGPUScenePost post = { 0 };
	post.tonemap_mode = BTBH_GPU_SCENE_TONEMAP_REINHARD;
	post.tonemap_white = 1.0f;
	post.exposure = 1.0f;
	post.contrast = 1.0f;
	post.saturation = 1.0f;
	post.blur_curve = 1.0f;
	post.focus_half_width = 0.05f;
	post.focus_point_x = 0.5f;
	post.focus_point_y = 0.55f;
	post.focus_direction_x = 1.0f;
	post.highlight_threshold = 0.7f;
	if (settings3d.effects)
	{
		post.bloom_intensity = bloom_parameters[0];
		post.bloom_threshold = bloom_parameters[1];
		post.bloom_knee = bloom_parameters[2];
		post.bloom_radius = bloom_parameters[3];
	}

	BTBHGPUSceneReport scene_report;
	if (btbh_gpu_window_scene_present_instances_with_visibility(window,
	        shader_paths[SH_MODEL_VERT], shader_paths[SH_ANIMATED_MODEL_VERT],
	        shader_paths[SH_SHADOW_FAST_VERT], shader_paths[SH_SHADOW_FAST_FRAG],
	        shader_paths[SH_SHADOW_VERT], shader_paths[SH_ANIMATED_SHADOW_VERT], shader_paths[SH_SHADOW_FRAG],
	        shader_paths[SH_MODEL_FRAG], shader_paths[SH_MODEL_UNSHADOWED_FRAG],
	        shader_paths[SH_POST_VERT], shader_paths[SH_POST_FRAG],
	        shader_format, window_frame.drawable_width, window_frame.drawable_height,
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
