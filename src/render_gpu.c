/*
 * Tyrian3D: GPU presentation through the BTBH renderer. See render_gpu.h.
 */
#include "render_gpu.h"

#include "background3d.h"
#include "devtools.h"
#include "models3d.h"
#include "palette.h"
#include "sprite.h"
#include "volume3d.h"

#include <btbh_gpu/btbh_gpu.h>

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

// Direction the sun's light travels: from the upper left, slightly from the bottom of the screen.
static const float sun_direction[3] = { 0.45f, -1.0f, -0.35f };

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
static BTBHGPUCustomMesh *quad_mesh = NULL;    // unit quad in the XZ plane
// The unit quad darkening by B3D_BEYOND_FADE towards its left or right edge.
static BTBHGPUCustomMesh *fade_meshes[2] = { NULL, NULL };

typedef struct
{
	BTBHGPUModel *gpu;
	bool load_attempted;
	uint32_t material_count;
	BTBHGPUModelMaterialInfo materials[16];
	float center[3];
	float footprint;  // larger of width and depth, model units
} LoadedModel;

static LoadedModel loaded_models[M3D_MAX_MODELS];

typedef struct VolumeSheet VolumeSheet;
static void forget_volume_sheets(void);
static Uint32 hash_colors(const Uint32 colors[256]);

static Uint32 screen_rgba[SCREEN_W * SCREEN_H];
static Uint32 atlas_rgba[L3D_WIDTH * ATLAS_H];

// The tile atlas has pages coloured with different palettes: the frame's colours, and those
// colours as recoloured by a level's filters (water, lava, ice).
#define TILE_PAGES 4
static Uint8 tile_indices[B3D_ATLAS_W * B3D_ATLAS_H];
static Uint8 tile_opaque[B3D_ATLAS_W * B3D_ATLAS_H];
static Uint32 tile_rgba[B3D_ATLAS_W * B3D_ATLAS_H];
static bool tile_indices_valid = false;
static unsigned int tile_indices_generation;  // b3d_map_generation of tile_indices
static struct
{
	bool valid;
	unsigned int generation;  // b3d_map_generation it was coloured for
	Uint32 colors_hash;
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

static BTBHGPUTexture *create_texture(int width, int height, BTBHGPUTextureColorSpace color_space)
{
	static Uint32 zeroes[L3D_WIDTH * ATLAS_H];
	BTBHGPUTextureReport report;
	BTBHGPUTexture *texture = btbh_gpu_window_texture_create_rgba8_ex(
		window, (const uint8_t *)zeroes, width, height, 0,
		BTBH_GPU_TEXTURE_FILTER_NEAREST, BTBH_GPU_TEXTURE_WRAP_CLAMP, color_space, &report);
	if (texture == NULL)
		die("failed to create GPU texture", report.message);
	return texture;
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

static void init_shader_paths(BTBHGPUBackendRequest backend)
{
	const char *dir = SDL_getenv("TYR3D_SHADER_DIR");
	SDL_strlcpy(shader_dir, dir != NULL ? dir : TYR3D_SHADER_DIR, sizeof(shader_dir));

	const char *ext = backend == BTBH_GPU_BACKEND_METAL ? "metallib" : "spv";
	for (int i = 0; i < SH_COUNT; ++i)
		snprintf(shader_paths[i], sizeof(shader_paths[i]), "%s/%s.%s", shader_dir, shader_names[i], ext);
}

static void init_camera_from_env(void)
{
	const char *value;
	if ((value = SDL_getenv("TYR3D_TILT")) != NULL)
		rgpu_camera.tilt_degrees = (float)SDL_atof(value);
	if ((value = SDL_getenv("TYR3D_FOV")) != NULL)
		rgpu_camera.fov_degrees = (float)SDL_atof(value);
	if ((value = SDL_getenv("TYR3D_HEIGHT_SCALE")) != NULL)
		rgpu_camera.height_scale = (float)SDL_atof(value);
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
	init_camera_from_env();

	screen_texture = create_texture(SCREEN_W, SCREEN_H, BTBH_GPU_TEXTURE_COLOR_SPACE_LINEAR);
	layer_atlas = create_texture(L3D_WIDTH, ATLAS_H, BTBH_GPU_TEXTURE_COLOR_SPACE_SRGB);
	tile_atlas = create_texture(B3D_ATLAS_W, B3D_ATLAS_H * TILE_PAGES, BTBH_GPU_TEXTURE_COLOR_SPACE_SRGB);
	white_texture = create_texture(1, 1, BTBH_GPU_TEXTURE_COLOR_SPACE_SRGB);
	const Uint32 white = 0xffffffff;
	btbh_gpu_texture_update_rgba8(white_texture, (const uint8_t *)&white, 0, 0, 1, 1);
	quad_mesh = create_quad_mesh(1, 1);
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
	tile_atlas = NULL;
	white_texture = NULL;
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

static void push_quad(BTBHGPUCanvasVertex *v, float x, float y, float w, float h)
{
	const BTBHGPUCanvasVertex corners[4] = {
		{ x,     y,     0, 0, 1, 1, 1, 1 },
		{ x + w, y,     1, 0, 1, 1, 1, 1 },
		{ x + w, y + h, 1, 1, 1, 1, 1, 1 },
		{ x,     y + h, 0, 1, 1, 1, 1, 1 },
	};
	v[0] = corners[0];
	v[1] = corners[1];
	v[2] = corners[2];
	v[3] = corners[0];
	v[4] = corners[2];
	v[5] = corners[3];
}

// Draws the screen texture over the window and presents. Composites a pending 3D scene first.
static void present_canvas(const SDL_Rect *dst, bool clear, const BTBHGPUWindowReport *frame)
{
	BTBHGPUCanvasVertex vertices[6];
	push_quad(vertices, (float)dst->x, (float)dst->y, (float)dst->w, (float)dst->h);

	BTBHGPUCanvasBatch batch = { 0 };
	batch.first_vertex = 0;
	batch.vertex_count = 6;
	batch.texture = screen_texture;
	batch.blend_mode = BTBH_GPU_CANVAS_BLEND_ALPHA;

	BTBHGPUCanvasPass pass = { 0 };
	pass.first_batch = 0;
	pass.batch_count = 1;
	pass.target = NULL;
	pass.clear_enabled = clear;
	pass.clear_alpha = 255;

	const bool capture = dev_capture_next_frame();
	if (capture)
		btbh_gpu_window_request_presented_frame_readback(window);

	BTBHGPUCanvasReport report;
	if (btbh_gpu_window_canvas_present(window,
	        shader_paths[SH_CANVAS_VERT], shader_paths[SH_CANVAS_FRAG], shader_paths[SH_CANVAS_TEXTURED_FRAG],
	        shader_format, vertices, 6, &batch, 1, &pass, 1, &report) != BTBH_GPU_OK)
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

	present_canvas(dst, true, &frame);
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
static Camera3D fit_camera(float reference_height, float viewport_aspect, const float ndc_rect[4])
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
	post.m[5] = sy;
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
                              int *slot_of_layer, int *slot_count)
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

	int slots = 0;
	for (int l = 0; l < frame->layer_count; ++l)
	{
		const L3DLayer *layer = &frame->layers[l];
		if (layer->type == L3D_OVERLAY)
		{
			slot_of_layer[l] = -1;
			continue;
		}
		slot_of_layer[l] = slots;
		Uint32 *dst = atlas_rgba + slots * ATLAS_SLOT_H * L3D_WIDTH;
		if (native[l])
		{
			memset(dst, 0, L3D_WIDTH * L3D_ROWS * sizeof(Uint32));
			for (int y = L3D_OVERSCAN; y < L3D_OVERSCAN + L3D_PLAYFIELD_H; ++y)
				for (int x = L3D_PLAYFIELD_X; x < L3D_PLAYFIELD_X + L3D_PLAYFIELD_W; ++x)
				{
					const int i = y * L3D_WIDTH + x;
					if (layer->cover[i])
						dst[i] = colors[layer->index[i]];
				}
			++slots;
			continue;
		}
		const Uint8 *fade = &edge_fade[0][0];
		for (int i = 0; i < L3D_WIDTH * L3D_ROWS; ++i)
		{
			if (!layer->cover[i])
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
		++slots;
	}
	*slot_count = slots;
}

// HUD with a transparent playfield, plus the overlay layers drawn into the playfield.
static void build_hud(const SDL_Surface *hud, const L3DFrame *frame)
{
	convert_screen(hud, screen_rgba);
	for (int y = 0; y < L3D_PLAYFIELD_H; ++y)
		memset(screen_rgba + y * SCREEN_W, 0, L3D_PLAYFIELD_W * sizeof(Uint32));

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
		loaded->footprint = SDL_max(report.maximum_x - report.minimum_x, report.maximum_z - report.minimum_z);
		loaded->material_count = SDL_min(report.material_count, (uint32_t)COUNTOF(loaded->materials));
		for (uint32_t m = 0; m < loaded->material_count; ++m)
			btbh_gpu_model_material_info(loaded->gpu, m, &loaded->materials[m]);
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

#define MAX_INSTANCES (L3D_MAX_LAYERS + L3D_MAX_OBJECTS + MAX_TILES + MAX_STARS)
// Background tiles: per background, a batch for each of its cells mirrored or not and fading
// either way or not at all (B3D_CELLS covers the cells of all three backgrounds).
#define MAX_BATCHES (L3D_MAX_LAYERS + M3D_MAX_MODELS * 4 + L3D_MAX_OBJECTS + B3D_CELLS * 6 + 1)

static float instances[MAX_INSTANCES * 24];
static BTBHGPUSceneGeometryBatch batches[MAX_BATCHES];

// Appends instances and batches for the frame's model objects, grouped by model.
static void add_object_batches(const L3DFrame *frame, int *instance_count, int *batch_count)
{
	sync_model_cache();

	for (int model_index = 0; model_index < m3d_model_count; ++model_index)
	{
		const int first_instance = *instance_count;
		const LoadedModel *loaded = NULL;

		for (int o = 0; o < frame->object_count; ++o)
		{
			const L3DObject *object = &frame->objects[o];
			if (object->model != model_index)
				continue;
			if (loaded == NULL && (loaded = get_model(model_index)) == NULL)
				break;

			const M3DModel *model = &m3d_models[model_index];
			const float scale = model->size > 0 && loaded->footprint > 0 ? model->size / loaded->footprint : 1.0f;
			const float height = l3d_layer_height(object->layer) * rgpu_camera.height_scale + object->height;
			const Mat4 chain[] = {
				mat4_translation(object->x, height, object->y),
				mat4_rotation(1, -object->yaw),
				mat4_rotation(2, -object->roll),
				mat4_rotation(1, model->yaw),
				mat4_rotation(0, model->pitch),
				mat4_rotation(2, model->roll),
				mat4_scaling(scale),
				mat4_translation(-loaded->center[0], -loaded->center[1], -loaded->center[2]),
			};
			const Mat4 transform = mat4_chain((int)COUNTOF(chain), chain);
			write_instance(instances + *instance_count * 24, &transform, object->filter != 0 ? 2.5f : 1.0f);
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
	memset(entry, 0, sizeof(*entry));
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

		// All objects showing the same sprite share one batch.
		const int first_instance = *instance_count;
		for (int p = o; p < frame->object_count; ++p)
		{
			const L3DObject *object = &frame->objects[p];
			if (done[p] || object->model != L3D_VOLUME || object->sheet != first->sheet ||
			    object->sprite != first->sprite || object->large != first->large || object->style != first->style)
				continue;
			done[p] = true;
			if (mesh == NULL || *instance_count >= MAX_INSTANCES)
				continue;

			const float height = l3d_layer_height(object->layer) * rgpu_camera.height_scale + object->height;
			const Mat4 chain[] = {
				mat4_translation(object->x, height, object->y),
				mat4_rotation(1, -object->yaw),
				mat4_rotation(2, -object->roll),
			};
			const Mat4 transform = mat4_chain((int)COUNTOF(chain), chain);
			write_instance(instances + *instance_count * 24, &transform, object->filter != 0 ? 2.5f : 1.0f);
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
		b->albedo_texture = entry->texture;
		b->unlit_enabled = 1;  // shaded by the mesh's vertex colours (v3d_build_mesh)
		b->alpha_cutoff = 0.5f;
	}
}

/* --- Background maps ----------------------------------------------------------------------- */

// Background tiles sit this far below their layer, so that the captured layer, which is exact
// inside the playfield (filters and all), is drawn over them.
#define TILE_BELOW_LAYER 0.05f

// Atlas page coloured with the given colours, reusing one that already is. Returns its index.
static int tile_page(const Uint32 colors[256])
{
	if (!tile_indices_valid || tile_indices_generation != b3d_map_generation)
	{
		b3d_build_atlas(tile_indices, tile_opaque);
		tile_indices_valid = true;
		tile_indices_generation = b3d_map_generation;
	}

	const Uint32 hash = hash_colors(colors);
	int page = 0;
	for (int p = 0; p < TILE_PAGES; ++p)
	{
		if (tile_pages[p].valid && tile_pages[p].generation == b3d_map_generation && tile_pages[p].colors_hash == hash)
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
		tile_rgba[i] = tile_opaque[i] ? colors[tile_indices[i]] : 0;
	btbh_gpu_texture_update_rgba8(tile_atlas, (const uint8_t *)tile_rgba, 0, page * B3D_ATLAS_H, B3D_ATLAS_W, B3D_ATLAS_H);
	tile_pages[page].valid = true;
	tile_pages[page].generation = b3d_map_generation;
	tile_pages[page].colors_hash = hash;
	tile_pages[page].used = tile_frame;
	return page;
}

// Appends instances and batches for the background maps: every tile the camera sees on each
// background's plane, grouped into one batch per atlas cell.
static void add_background_batches(const L3DFrame *frame, const Camera3D *camera, const float *heights,
                                   const Uint32 colors[256], int *instance_count, int *batch_count)
{
	if (frame->background_count == 0)
		return;
	++tile_frame;

	static B3DTile tiles[MAX_TILES];
	static float tile_height[MAX_TILES];
	static int tile_key[MAX_TILES];
	const int capacity = SDL_min(MAX_TILES, MAX_INSTANCES - *instance_count);
	int tile_count = 0;
	for (int i = 0; i < frame->background_count; ++i)
	{
		const L3DBackground *background = &frame->backgrounds[i];
		const float height = heights[background->layer] - TILE_BELOW_LAYER;
		float rect[4];
		plane_footprint(camera, height, rect);
		if (rect[0] > rect[2])
			continue;

		// Tiles take the colours the game gives them through blending and the level's filters.
		Uint8 remap[256];
		Uint32 page_colors[256];
		b3d_tile_remap(background, remap);
		for (int c = 0; c < 256; ++c)
			page_colors[c] = colors[remap[c]];
		const int page = tile_page(page_colors);

		const int first = tile_count;
		tile_count += b3d_collect_tiles(background, rect[0], rect[1], rect[2], rect[3],
		                                tiles + tile_count, capacity - tile_count);
		for (int t = first; t < tile_count; ++t)
		{
			tile_height[t] = height;
			// Batch key: atlas page and cell, mirrored, fading.
			tile_key[t] = ((page * B3D_CELLS + tiles[t].cell) * 2 + tiles[t].flipped) * 3 + tiles[t].fade + 1;
		}
	}

	enum { KEYS = TILE_PAGES * B3D_CELLS * 6 };
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
		const int cell = key / 6 % B3D_CELLS, page = key / 6 / B3D_CELLS;
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

// Appends the starfield outside the playfield (inside it, the captured layer has the stars).
static void add_star_batch(const L3DFrame *frame, const Camera3D *camera, const float *heights,
                           const Uint32 colors[256], int *instance_count, int *batch_count)
{
	if (frame->star_count == 0 || *batch_count >= MAX_BATCHES)
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

static void present_3d(const SDL_Surface *hud, const L3DFrame *frame, const SDL_Rect *dst)
{
	BTBHGPUWindowReport window_frame;
	if (!begin_frame(&window_frame))
		return;

	Uint32 colors[256];
	frame_colors(frame, colors);

	// Layers that background maps were drawn into get the map's tiles beneath them.
	bool native[L3D_MAX_LAYERS] = { false };
	for (int i = 0; i < frame->background_count; ++i)
		native[frame->backgrounds[i].layer] = true;

	int slot_of_layer[L3D_MAX_LAYERS];
	int slot_count = 0;
	build_layer_atlas(frame, colors, native, slot_of_layer, &slot_count);
	if (slot_count > 0)
		btbh_gpu_texture_update_rgba8(layer_atlas, (const uint8_t *)atlas_rgba, 0, 0, L3D_WIDTH, slot_count * ATLAS_SLOT_H);

	build_hud(hud, frame);
	btbh_gpu_texture_update_rgba8(screen_texture, (const uint8_t *)screen_rgba, 0, 0, SCREEN_W, SCREEN_H);

	if (slot_count == 0)
	{
		present_canvas(dst, true, &window_frame);
		return;
	}

	// Playfield rectangle in NDC (y up) of the whole window.
	const float logical_w = (float)window_frame.logical_width, logical_h = (float)window_frame.logical_height;
	const float px0 = dst->x, px1 = dst->x + dst->w * (float)L3D_PLAYFIELD_W / SCREEN_W;
	const float py0 = dst->y, py1 = dst->y + dst->h * (float)L3D_PLAYFIELD_H / SCREEN_H;
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

	const Camera3D camera = fit_camera(reference_height, viewport_aspect, ndc_rect);

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
		transform.m[14] = -L3D_OVERSCAN;
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
	}

	add_background_batches(frame, &camera, heights, colors, &instance_count, &batch_count);
	add_star_batch(frame, &camera, heights, colors, &instance_count, &batch_count);
	add_object_batches(frame, &instance_count, &batch_count);
	add_volume_batches(frame, &instance_count, &batch_count);

	// Models are lit by a sun and a cool ambient term; layers and volumetric sprites are unlit.
	BTBHGPUSceneLighting lighting = { 0 };
	lighting.spot_falloff = 1.0f;
	lighting.spot_inner_cutoff = 0.92388f;
	lighting.spot_outer_cutoff = 0.70711f;
	lighting.spot_range = 50.0f;
	lighting.ambient_red = 0.55f;
	lighting.ambient_green = 0.58f;
	lighting.ambient_blue = 0.68f;
	lighting.ambient_energy = 0.9f;
	const float *sun = sun_direction;
	const float sun_length = sqrtf(sun[0] * sun[0] + sun[1] * sun[1] + sun[2] * sun[2]);
	lighting.directional_x = sun[0] / sun_length;
	lighting.directional_y = sun[1] / sun_length;
	lighting.directional_z = sun[2] / sun_length;
	lighting.directional_energy = 2.6f;
	lighting.directional_red = 1.0f;
	lighting.directional_green = 0.96f;
	lighting.directional_blue = 0.88f;

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

	BTBHGPUSceneReport scene_report;
	if (btbh_gpu_window_scene_present_instances(window,
	        shader_paths[SH_MODEL_VERT], shader_paths[SH_ANIMATED_MODEL_VERT],
	        shader_paths[SH_SHADOW_FAST_VERT], shader_paths[SH_SHADOW_FAST_FRAG],
	        shader_paths[SH_SHADOW_VERT], shader_paths[SH_ANIMATED_SHADOW_VERT], shader_paths[SH_SHADOW_FRAG],
	        shader_paths[SH_MODEL_FRAG], shader_paths[SH_MODEL_UNSHADOWED_FRAG],
	        shader_paths[SH_POST_VERT], shader_paths[SH_POST_FRAG],
	        shader_format, window_frame.drawable_width, window_frame.drawable_height,
	        camera.view_projection.m, camera.right, camera.up, camera.position,
	        &lighting, &post, instances, instance_count, instance_count, batches, batch_count,
	        0, 0, 0, 255, &scene_report) != BTBH_GPU_OK)
	{
		fprintf(stderr, "warning: scene present failed: %s\n", scene_report.message);
		present_canvas(dst, true, &window_frame);
		return;
	}

	present_canvas(dst, false, &window_frame);
}
