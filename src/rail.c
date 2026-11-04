/*
 * Tyrian3D: a level flown on the rail, as Star Fox 64 flies (rail.h, docs/plans/2026-11-04-starfox.md).
 *
 * The ground is the level's own: background 1's map and, over it where it has tiles, background 3's (HARVEST's
 * meadows and woods over its machinery), standing PLATEAU higher, each with its terrain's relief and the plants found
 * on it, its HD tiles at TEXELS texels a pixel, in chunks along the flight made a few rows at a time as it nears them.
 * What moves lives in the rail's frame: across (x from the rail's middle), up (y over the ground's plane) and ahead of
 * the ship (d, along the flight), the rail curving gently across the maps (rail_x). The level is a list of waves
 * (WAVES) by the flight's tick (70 a second), then its boss: SAVARA's big red jet, its seven pieces as the game draws
 * them, flown at the ship.
 */
#include "rail.h"

#include "background3d.h"
#include "config.h"
#include "devtools.h"
#include "episodes.h"
#include "joystick.h"
#include "keyboard.h"
#include "loudness.h"
#include "mainint.h"
#include "models3d.h"
#include "mouse.h"
#include "nortsong.h"
#include "palette.h"
#include "pcxmast.h"
#include "player.h"
#include "settings3d.h"
#include "sndmast.h"
#include "ui.h"
#include "varz.h"
#include "video.h"

#include <math.h>
#include <stdlib.h>
#include <string.h>

bool rail_next_level = false;

static bool active = false;
static RailView view;
static Uint32 fx_seed = 0x6c078965;  // (the flight's own random numbers)

static float frand(void)
{
	fx_seed = fx_seed * 1664525u + 1013904223u;
	return (fx_seed >> 8) / 16777216.0f;
}

static float frange(float a, float b)
{
	return a + (b - a) * frand();
}

static float clampf(float v, float lo, float hi)
{
	return v < lo ? lo : v > hi ? hi : v;
}

static float approach(float v, float to, float step)
{
	return v < to ? SDL_min(v + step, to) : SDL_max(v - step, to);
}

// v folded into [0, period): up to the period, then back down it, and so on (the maps mirrored end to end).
static float mirror(float v, float period)
{
	float f = fmodf(v, 2 * period);
	if (f < 0)
		f += 2 * period;
	return f < period ? f : SDL_min(2 * period - f, period - 0.001f);
}

/* --- The ground ------------------------------------------------------------------------------------------- */

#define TILE_W B3D_TILE_W
#define TILE_H B3D_TILE_H
#define SIDES 16               // the generated columns beside background 1's map (background3d.c SIDE_COLUMNS)
#define TEXELS 2               // the ground's texture: texels a game pixel
#define MESH_STEP 8            // game pixels between the ground mesh's vertices
#define PLATEAU 26.0f          // background 3's ground over background 1's
#define CHUNKS_CACHED 5
#define CELL_TW (TILE_W * TEXELS)
#define CELL_TH (TILE_H * TEXELS)

typedef struct
{
	int set, columns, rows;
	int sides;                  // the generated columns beside it it takes (0: it goes on mirrored at once)
	float width, length;        // its exported map's pixels (the generated columns included), and its rows'
	float centre;               // the exported x of the maps' middle (x 0)
	const B3DTerrain *terrain;
	// For each column of the texture: where it lies in this map (after the mirroring), the tile's column and the
	// pixel in it.
	Sint16 *column_of;
	Uint8 *pixel_of;
	// Each row's tiles (their atlas cells, -1 for none; mirrored or not), the generated columns included.
	Sint16 *cell_of;
	bool *flipped;
} Layer;

static Layer layers[2];         // background 1's, then background 3's over it (if it has a map)
static int layer_count = 0;
static Uint32 *cells = NULL;    // the atlas's cells at TEXELS a pixel, RGBA (alpha 0 where the tile has nothing)
static int tex_w = 0;           // the ground texture's width: the widest map's
static float tex_half = 0;      // half its width in game pixels

typedef struct
{
	int k;                      // the chunk (INT32_MIN: free)
	unsigned int generation;
	int rows_done;              // texture rows made so far (TEX_H when whole)
	bool meshed;
	Uint32 *rgba;
	float *vertices;
	Uint32 *indices;
	int vertex_count, index_count;
	Uint32 used;
} Chunk;

#define TEX_H (RAIL_CHUNK * TEXELS)
static Chunk chunks[CHUNKS_CACHED];
static unsigned int chunk_generation = 0;
static Uint32 chunk_clock = 0;

static Uint8 cell_rgb[256][3];

static void make_cells(void)
{
	const int s = b3d_hd_scale();
	const int aw = B3D_ATLAS_W * s, ah = B3D_ATLAS_H * s;
	Uint8 *indices = malloc((size_t)aw * ah), *opaque = malloc((size_t)aw * ah), *ground = malloc((size_t)aw * ah);
	free(cells);
	cells = malloc(sizeof(Uint32) * (size_t)B3D_ATLAS_CELLS * CELL_TW * CELL_TH);
	if (indices == NULL || opaque == NULL || ground == NULL || cells == NULL)
	{
		free(indices);
		free(opaque);
		free(ground);
		free(cells);
		cells = NULL;
		return;
	}
	if (s > 1)
		b3d_build_atlas_hd(indices, opaque, ground);
	else
		b3d_build_atlas(indices, opaque, ground);
	for (int i = 0; i < 256; ++i)
	{
		cell_rgb[i][0] = colors[i].r;
		cell_rgb[i][1] = colors[i].g;
		cell_rgb[i][2] = colors[i].b;
	}
	// Each texel the mean of the HD pixels it covers (those with something there), opaque if most have.
	const int span = SDL_max(s / TEXELS, 1);
	for (int c = 0; c < B3D_ATLAS_CELLS; ++c)
	{
		int ox, oy;
		b3d_cell_origin(c, &ox, &oy);
		ox *= s;
		oy *= s;
		Uint32 *out = cells + (size_t)c * CELL_TW * CELL_TH;
		for (int ty = 0; ty < CELL_TH; ++ty)
			for (int tx = 0; tx < CELL_TW; ++tx)
			{
				const int hx = ox + tx * s / TEXELS, hy = oy + ty * s / TEXELS;
				int r = 0, g = 0, b = 0, n = 0;
				for (int y = 0; y < span; ++y)
					for (int x = 0; x < span; ++x)
					{
						const size_t at = (size_t)(hy + y) * aw + hx + x;
						const bool there = opaque[at] || ground[at];
						if (!there || (indices[at] == 0 && !ground[at]))
							continue;
						r += cell_rgb[indices[at]][0];
						g += cell_rgb[indices[at]][1];
						b += cell_rgb[indices[at]][2];
						++n;
					}
				out[ty * CELL_TW + tx] = n * 2 < span * span ? 0
				                       : (Uint32)(r / n) | (Uint32)(g / n) << 8 | (Uint32)(b / n) << 16 | 0xff000000u;
			}
	}
	free(indices);
	free(opaque);
	free(ground);
}

static void layer_begin(Layer *l, int set, int columns, int rows, int sides)
{
	l->set = set;
	l->sides = sides;
	l->columns = columns;
	l->rows = rows;
	l->width = (float)((columns + 2 * sides) * TILE_W);
	l->length = (float)(rows * TILE_H);
	l->centre = l->width / 2;
	l->terrain = b3d_terrain(set);
}

// Where the texture's columns lie in each map: the texture spans the widest map (x -tex_half to tex_half); a narrower
// one goes on mirrored at its sides.
static void layer_columns(Layer *l)
{
	free(l->column_of);
	free(l->pixel_of);
	l->column_of = malloc(sizeof(Sint16) * (size_t)tex_w);
	l->pixel_of = malloc((size_t)tex_w);
	if (l->column_of == NULL || l->pixel_of == NULL)
		return;
	const int width = l->columns + 2 * l->sides;
	free(l->cell_of);
	free(l->flipped);
	l->cell_of = malloc(sizeof(Sint16) * (size_t)l->rows * width);
	l->flipped = malloc(sizeof(bool) * (size_t)l->rows * width);
	if (l->cell_of == NULL || l->flipped == NULL)
		return;
	for (int row = 0; row < l->rows; ++row)
		for (int c = 0; c < width; ++c)
			l->cell_of[row * width + c] = (Sint16)b3d_map_cell(l->set, row, c - l->sides, &l->flipped[row * width + c]);
	for (int tx = 0; tx < tex_w; ++tx)
	{
		const float x = -tex_half + (tx + 0.5f) / TEXELS;
		const float ex = mirror(x + l->centre, l->width);
		const int column = (int)(ex / TILE_W);
		l->column_of[tx] = (Sint16)(column - l->sides);
		l->pixel_of[tx] = (Uint8)SDL_clamp((int)((ex - column * TILE_W) * TEXELS), 0, CELL_TW - 1);
	}
}

// A map's texel at a texture column and a game row (its exported map's, mirrored end to end): 0 where it has nothing.
static Uint32 layer_texel(const Layer *l, int tx, float z)
{
	const float ez = mirror(z, l->length);
	const int row = SDL_min((int)(ez / TILE_H), l->rows - 1);
	const int c = l->column_of[tx] + l->sides, width = l->columns + 2 * l->sides;
	if (c < 0 || c >= width)
		return 0;
	const int cell = l->cell_of[row * width + c];
	if (cell < 0)
		return 0;
	const int py = SDL_clamp((int)((ez - row * TILE_H) * TEXELS), 0, CELL_TH - 1);
	const int px = l->flipped[row * width + c] ? CELL_TW - 1 - l->pixel_of[tx] : l->pixel_of[tx];
	return cells[(size_t)cell * CELL_TW * CELL_TH + (size_t)py * CELL_TW + px];
}

// The texture's x for a world x: the widest map's, mirrored beyond it.
static float texture_x(float x)
{
	return mirror(x + tex_half, 2 * tex_half) - tex_half;
}

static float terrain_at(const Layer *l, float x, float z)
{
	const B3DTerrain *t = l->terrain;
	if (t == NULL)
		return 0;
	const float ex = mirror(texture_x(x) + l->centre, l->width) + (t->side_columns - l->sides) * TILE_W;
	const float ez = mirror(z, l->length);
	const float fx = ex / t->sample, fy = ez / t->sample;
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

// Whether the top map has ground at a point (its texel opaque).
static bool top_there(float x, float z)
{
	if (layer_count < 2)
		return false;
	const Layer *l = &layers[1];
	const float tx = (texture_x(x) + tex_half) * TEXELS;
	return layer_texel(l, SDL_clamp((int)tx, 0, tex_w - 1), z) != 0;
}

// How high the ground is at a point: background 1's relief, rising to background 3's where it has ground (its edge
// eased over a few pixels).
static float ground_height(float x, float z)
{
	float h = terrain_at(&layers[0], x, z);
	if (layer_count < 2)
		return h;
	static const float dx[5] = { 0, -5, 5, 0, 0 }, dz[5] = { 0, 0, 0, -5, 5 };
	int there = 0;
	for (int k = 0; k < 5; ++k)
		there += top_there(x + dx[k], z + dz[k]);
	const float share = there / 5.0f;
	return h * (1 - share) + (PLATEAU + terrain_at(&layers[1], x, z)) * share;
}

static Chunk *chunk_slot(int k, bool make)
{
	Chunk *free_slot = NULL;
	for (int i = 0; i < CHUNKS_CACHED; ++i)
	{
		if (chunks[i].k == k && chunks[i].rgba != NULL)
		{
			chunks[i].used = ++chunk_clock;
			return &chunks[i];
		}
		if (free_slot == NULL || chunks[i].rgba == NULL || (free_slot->rgba != NULL && chunks[i].used < free_slot->used))
			free_slot = &chunks[i];
	}
	if (!make || free_slot == NULL)
		return NULL;
	if (free_slot->rgba == NULL)
		free_slot->rgba = malloc(sizeof(Uint32) * (size_t)tex_w * TEX_H);
	if (free_slot->rgba == NULL)
		return NULL;
	free_slot->k = k;
	free_slot->generation = 0;
	free_slot->rows_done = 0;
	free_slot->meshed = false;
	free_slot->used = ++chunk_clock;
	return free_slot;
}

// Some more rows of a chunk's texture (background 1's texels, background 3's over them where it has some).
static void chunk_rows(Chunk *c, int rows)
{
	const int last = SDL_min(c->rows_done + rows, TEX_H);
	for (int ty = c->rows_done; ty < last; ++ty)
	{
		const float z = c->k * (float)RAIL_CHUNK + (ty + 0.5f) / TEXELS;
		Uint32 *out = c->rgba + (size_t)ty * tex_w;
		for (int tx = 0; tx < tex_w; ++tx)
		{
			Uint32 texel = layer_count > 1 ? layer_texel(&layers[1], tx, z) : 0;
			if (texel == 0)
				texel = layer_texel(&layers[0], tx, z);
			out[tx] = texel != 0 ? texel : 0xff000000u;
		}
	}
	c->rows_done = last;
}

// The chunk's mesh: a vertex every MESH_STEP pixels, out to RAIL_GROUND_X either side (the texture mirrored beyond
// the maps), the renderer's 24 floats each.
static void chunk_mesh(Chunk *c)
{
	const int columns = (int)(2 * RAIL_GROUND_X / MESH_STEP) + 1, rows = RAIL_CHUNK / MESH_STEP + 1;
	const int vertex_count = columns * rows, index_count = (columns - 1) * (rows - 1) * 6;
	if (c->vertices == NULL)
	{
		c->vertices = malloc(sizeof(float) * 24 * (size_t)vertex_count);
		c->indices = malloc(sizeof(Uint32) * (size_t)index_count);
	}
	if (c->vertices == NULL || c->indices == NULL)
		return;
	static float *heights = NULL;
	static int height_count = 0;
	if (height_count < vertex_count)
	{
		free(heights);
		heights = malloc(sizeof(float) * (size_t)vertex_count);
		height_count = heights != NULL ? vertex_count : 0;
		if (heights == NULL)
			return;
	}
	const float z0 = c->k * (float)RAIL_CHUNK;
	const float sl = sqrtf(view.sun[0] * view.sun[0] + view.sun[1] * view.sun[1] + view.sun[2] * view.sun[2]);
	const float light[3] = { -view.sun[0] / sl, -view.sun[1] / sl, -view.sun[2] / sl };
	for (int j = 0; j < rows; ++j)
		for (int i = 0; i < columns; ++i)
			heights[j * columns + i] = ground_height(-RAIL_GROUND_X + i * MESH_STEP, z0 + j * MESH_STEP);
	float *v = c->vertices;
	for (int j = 0; j < rows; ++j)
		for (int i = 0; i < columns; ++i, v += 24)
		{
			const float x = -RAIL_GROUND_X + i * MESH_STEP, z = z0 + j * MESH_STEP;
			const float hl = heights[j * columns + SDL_max(i - 1, 0)], hr = heights[j * columns + SDL_min(i + 1, columns - 1)];
			const float hu = heights[SDL_max(j - 1, 0) * columns + i], hd = heights[SDL_min(j + 1, rows - 1) * columns + i];
			float n[3] = { -(hr - hl) / (2.0f * MESH_STEP), 1.0f, -(hd - hu) / (2.0f * MESH_STEP) };
			const float nl = sqrtf(n[0] * n[0] + n[1] * n[1] + n[2] * n[2]);
			// Shaded as the 3D view's terrain is (render_gpu.c build_terrain_row): flat ground as the tiles are, slopes
			// to the sun lighter, away from it darker (it is drawn unlit).
			const float lambert = (n[0] * light[0] + n[1] * light[1] + n[2] * light[2]) / nl;
			const float shade = (0.42f + 0.58f * SDL_max(lambert, 0.0f)) / (0.42f + 0.58f * SDL_max(light[1], 0.0f));
			memset(v, 0, sizeof(float) * 24);
			v[0] = x;
			v[1] = heights[j * columns + i];
			v[2] = z;
			v[3] = n[0] / nl;
			v[4] = n[1] / nl;
			v[5] = n[2] / nl;
			v[6] = (x + tex_half) / (2 * tex_half);  // (the texture mirrors beyond 0 and 1)
			v[7] = (float)j * MESH_STEP / RAIL_CHUNK;
			v[8] = 1;   // tangent
			v[11] = 1;
			v[12] = v[13] = v[14] = shade;  // colour
			v[15] = 1;
			v[20] = 1;  // weights
		}
	Uint32 *ix = c->indices;
	for (int j = 0; j + 1 < rows; ++j)
		for (int i = 0; i + 1 < columns; ++i)
		{
			const Uint32 a = (Uint32)(j * columns + i), b = a + 1, d = a + (Uint32)columns, e = d + 1;
			*ix++ = a;
			*ix++ = d;
			*ix++ = e;
			*ix++ = a;
			*ix++ = e;
			*ix++ = b;
		}
	c->vertex_count = vertex_count;
	c->index_count = index_count;
	c->meshed = true;
	c->generation = ++chunk_generation;
	// (TYR3D_RAIL_DUMP=<dir>, dev: the chunks' textures as BMPs, to see what the ground is made of.)
	const char *dump = SDL_getenv("TYR3D_RAIL_DUMP");
	if (dump != NULL)
	{
		SDL_Surface *surface = SDL_CreateSurfaceFrom(tex_w, TEX_H, SDL_PIXELFORMAT_RGBA32, c->rgba, tex_w * 4);
		if (surface != NULL)
		{
			char path[1024];
			snprintf(path, sizeof(path), "%s/chunk_%d.bmp", dump, c->k);
			SDL_SaveBMP(surface, path);
			SDL_DestroySurface(surface);
		}
	}
}

// The chunks the flight nears: made a part a tick (the nearest first), so the frame never waits long.
static void ground_tick(float z_near, float z_far)
{
	if (cells == NULL)
		return;
	const int k_near = (int)floorf(z_near / RAIL_CHUNK), k_far = (int)floorf(z_far / RAIL_CHUNK);
	for (int k = k_near; k >= k_far; --k)
	{
		Chunk *c = chunk_slot(k, true);
		if (c == NULL || c->meshed)
			continue;
		if (c->rows_done < TEX_H)
			chunk_rows(c, k == k_near ? TEX_H : 160);
		if (c->rows_done == TEX_H)
			chunk_mesh(c);
		if (k != k_near)
			break;  // (one chunk further on a tick)
	}
}

unsigned int rail_ground_chunk(int k, D3Mesh *mesh, const Uint32 **rgba, int *w, int *h)
{
	for (int i = 0; i < CHUNKS_CACHED; ++i)
		if (chunks[i].k == k && chunks[i].meshed && chunks[i].rgba != NULL)
		{
			mesh->vertices = chunks[i].vertices;
			mesh->vertex_count = chunks[i].vertex_count;
			mesh->indices = chunks[i].indices;
			mesh->index_count = chunks[i].index_count;
			*rgba = chunks[i].rgba;
			*w = tex_w;
			*h = TEX_H;
			return chunks[i].generation;
		}
	return 0;
}

static bool ground_begin(void)
{
	layer_count = 0;
	layer_begin(&layers[layer_count++], 1, 14, 300, SIDES);
	// (Background 3, HARVEST's meadows, mirrored from its own columns: its generated ones end it in straight edges.)
	if (!b3d_map_empty(3))
		layer_begin(&layers[layer_count++], 3, 15, 600, 0);
	tex_half = 0;
	for (int i = 0; i < layer_count; ++i)
		tex_half = SDL_max(tex_half, layers[i].width / 2);
	tex_w = (int)(2 * tex_half * TEXELS);
	for (int i = 0; i < layer_count; ++i)
		layer_columns(&layers[i]);
	for (int i = 0; i < CHUNKS_CACHED; ++i)
		chunks[i].k = INT32_MIN;
	make_cells();
	return cells != NULL;
}

static void ground_end(void)
{
	for (int i = 0; i < CHUNKS_CACHED; ++i)
	{
		free(chunks[i].rgba);
		free(chunks[i].vertices);
		free(chunks[i].indices);
		memset(&chunks[i], 0, sizeof(chunks[i]));
		chunks[i].k = INT32_MIN;
	}
	for (int i = 0; i < 2; ++i)
	{
		free(layers[i].column_of);
		free(layers[i].pixel_of);
		free(layers[i].cell_of);
		free(layers[i].flipped);
		layers[i].column_of = NULL;
		layers[i].pixel_of = NULL;
		layers[i].cell_of = NULL;
		layers[i].flipped = NULL;
	}
	free(cells);
	cells = NULL;
}

/* --- The flight ------------------------------------------------------------------------------------------- */

#define HZ 70
#define SPEED 3.0f             // the rail's pace, pixels a tick
#define SPEED_BOOST 5.2f
#define SPEED_BRAKE 1.7f
#define SHIP_X 118.0f          // how far the ship goes across the rail, either way
#define SHIP_LOW 36.0f         // and how low and high it flies (over the ground's plane)
#define SHIP_HIGH 150.0f
#define SHIP_SCALE 1.35f
#define SHIP_RADIUS 9.0f
#define CAMERA_BEHIND 98.0f
#define CAMERA_ABOVE 34.0f
#define FAR 2600.0f            // what is further ahead isn't made yet or shown
#define LASER_SPEED 15.0f
#define LASER_LIFE 72
#define ROLL_TICKS 34          // a barrel roll
#define BOOST_MAX 100.0f
#define CHARGE_TICKS 40        // fire held this long: a charged shot when it is let go
#define BLAST 66.0f            // a charged shot's burst: what is this near is hurt
#define BLAST_DAMAGE 12

enum { K_JET, K_DELTA, K_GREEN, K_BROWN, K_PURPLE, K_TAN, K_POD, K_TURRET, K_DOME, K_MINE, K_BOSS, K_COUNT };

typedef struct
{
	const char *model;
	float scale, radius;
	int armor, value;
	int fire;                  // ticks between its shots (0: it doesn't fire)
	Uint8 shot;                // 0 a red ball, 1 an orange one, heavier
	bool ground;
} Kind;

static const Kind kinds[K_COUNT] = {
	[K_JET]    = { "jet_cross",          2.9f, 20, 2,   100,   0, 0, false },
	[K_DELTA]  = { "jet_delta",          2.9f, 20, 3,   150, 170, 0, false },
	[K_GREEN]  = { "jet_green",          2.9f, 20, 4,   200, 140, 0, false },
	[K_BROWN]  = { "jet_brown",          3.1f, 22, 6,   300, 110, 1, false },
	[K_PURPLE] = { "purple_fighter",     2.9f, 20, 5,   250, 120, 0, false },
	[K_TAN]    = { "tan_fighter",        3.2f, 23, 9,   400,  95, 1, false },
	[K_POD]    = { "yellow_pod_fighter", 2.9f, 20, 4,   200, 150, 0, false },
	[K_TURRET] = { "pod_turret",         3.2f, 23, 6,   300, 105, 0, true },
	[K_DOME]   = { "dome_red",           3.4f, 24, 9,   350,  85, 1, true },
	[K_MINE]   = { "spike_mine",         2.7f, 18, 3,   120,   0, 0, false },
	[K_BOSS]   = { NULL,                 3.4f, 60, 450, 10000, 0, 0, false },
};

// How an enemy flies (in the rail's frame).
enum
{
	P_HEAD,     // at the ship from ahead, weaving a little
	P_CROSS,    // across ahead of the ship, from one side to the other (x: where it starts)
	P_BEHIND,   // up from behind the ship, past it, then round at it
	P_HOVER,    // to a stand ahead, matching the ship's pace, strafing, then away
	P_GROUND,   // standing on the ground
	P_DIVE,     // from high ahead, down past the ship
	P_ITEM,     // (a ring or a capsule hanging in the air: kind is the item)
};

enum { D_NONE, D_SHIELD, D_ARMOR, D_POWER, D_BOMB, D_CASH, D_ITEMS };

typedef struct
{
	int tick;
	Uint8 kind, path, count;
	float x, y;                // the formation's middle: across, height
	float spread, gap;         // its members this far apart across, and ahead (a V when gap > 0)
	Uint8 drop;                // what its last member leaves
} Wave;

#define T(seconds) ((int)((seconds) * HZ))
static const Wave WAVES[] = {
	// The fields: fighters in Vs coming at the ship, turrets in the meadows.
	{ T(3.0),  K_JET,    P_HEAD,   5,    0,  80, 34, 40, D_NONE },
	{ T(6.0),  K_JET,    P_HEAD,   5,  -40, 100, 34, 40, D_POWER },
	{ T(8.5),  K_TURRET, P_GROUND, 2,    0,   0, 150, 0, D_NONE },
	{ T(10.0), K_DELTA,  P_CROSS,  4, -320,  90,  0, 70, D_NONE },
	{ T(12.5), K_DELTA,  P_CROSS,  4,  320,  70,  0, 70, D_SHIELD },
	{ T(15.0), K_GREEN,  P_BEHIND, 3,    0, 120, 50, 30, D_NONE },
	{ T(17.5), K_TURRET, P_GROUND, 3,    0,   0, 100, 260, D_NONE },
	{ T(19.0), D_SHIELD, P_ITEM,   1,  -60,  80,  0, 0, D_NONE },
	{ T(20.0), K_JET,    P_HEAD,   7,    0,  90, 30, 36, D_NONE },
	{ T(23.0), K_POD,    P_HOVER,  3,    0,  95, 70, 0, D_CASH },
	{ T(27.0), K_DELTA,  P_DIVE,   4,  -50, 170, 36, 60, D_NONE },
	{ T(29.0), K_DELTA,  P_DIVE,   4,   50, 170, 36, 60, D_POWER },
	{ T(31.5), K_DOME,   P_GROUND, 2,    0,   0, 180, 0, D_NONE },
	{ T(33.0), K_GREEN,  P_HEAD,   5,    0, 120, 40, 50, D_NONE },
	{ T(35.0), D_ARMOR,  P_ITEM,   1,   50, 110,  0, 0, D_NONE },
	{ T(36.0), K_PURPLE, P_CROSS,  5,  340, 110,  0, 60, D_NONE },
	{ T(38.5), K_PURPLE, P_CROSS,  5, -340,  60,  0, 60, D_BOMB },
	// The Collector's escorts: they come up from behind and stand ahead.
	{ T(42.0), K_BROWN,  P_BEHIND, 2,    0, 110, 90, 0, D_NONE },
	{ T(45.0), K_TURRET, P_GROUND, 4,    0,   0, 90, 220, D_NONE },
	{ T(47.0), K_POD,    P_HOVER,  4,    0,  80, 60, 0, D_SHIELD },
	{ T(52.0), K_JET,    P_HEAD,   9,    0, 100, 26, 30, D_NONE },
	{ T(54.0), K_MINE,   P_HEAD,   6,    0,  70, 45, 120, D_NONE },
	{ T(57.0), K_TAN,    P_HOVER,  2,    0, 110, 120, 0, D_POWER },
	{ T(61.0), K_DELTA,  P_CROSS,  5, -330, 130,  0, 55, D_NONE },
	{ T(62.0), K_DELTA,  P_CROSS,  5,  330,  60,  0, 55, D_NONE },
	{ T(64.5), K_DOME,   P_GROUND, 3,    0,   0, 120, 240, D_ARMOR },
	{ T(67.0), K_GREEN,  P_BEHIND, 4,    0, 100, 45, 30, D_NONE },
	{ T(70.0), D_POWER,  P_ITEM,   1,    0,  90,  0, 0, D_NONE },
	// The storm of the Collector's fleet.
	{ T(72.0), K_BROWN,  P_HEAD,   3,    0, 100, 70, 80, D_NONE },
	{ T(74.0), K_PURPLE, P_DIVE,   6,    0, 180, 40, 40, D_NONE },
	{ T(77.0), K_TAN,    P_BEHIND, 2,    0, 120, 110, 0, D_SHIELD },
	{ T(81.0), K_JET,    P_HEAD,   9,    0,  70, 26, 30, D_NONE },
	{ T(82.5), K_JET,    P_HEAD,   9,    0, 130, 26, 30, D_NONE },
	{ T(85.0), K_TURRET, P_GROUND, 5,    0,   0, 80, 200, D_NONE },
	{ T(88.0), K_POD,    P_HOVER,  5,    0, 100, 55, 0, D_BOMB },
	{ T(93.0), K_MINE,   P_HEAD,   8,    0,  95, 38, 90, D_NONE },
	{ T(96.0), K_BROWN,  P_CROSS,  3,  330, 100,  0, 90, D_NONE },
	{ T(97.0), K_BROWN,  P_CROSS,  3, -330, 100,  0, 90, D_ARMOR },
	{ T(100.0), K_TAN,   P_HOVER,  3,    0, 100, 90, 0, D_POWER },
	{ T(105.0), K_GREEN, P_HEAD,   7,    0, 110, 32, 40, D_NONE },
	{ T(108.0), D_SHIELD, P_ITEM,  1,    0,  90,  0, 0, D_NONE },
	{ T(109.0), D_ARMOR, P_ITEM,   1,    0, 130,  0, 0, D_NONE },
};
#define BOSS_TICK T(114.0)
#define CHECKPOINT_TICK T(56.0)  // a ship lost after it flies on from there (as the long levels' checkpoints)

// Stone arches across the rail to fly through: sets of them one after another (from the haze ahead at their tick, gap
// apart), each a little to one side (swing); through every one of a set, a bonus. An arch's opening is ARCH_INNER
// either side of its middle, springing at ARCH_SPRING over its foot, its outer edge ARCH_OUTER
// (tools/modelkit/make_rail_arch.py).
#define ARCH_INNER 60.0f
#define ARCH_OUTER 86.0f
#define ARCH_SPRING 64.0f
typedef struct
{
	int tick;
	Uint8 count;
	float gap, swing;
} ArchSet;
static const ArchSet ARCH_SETS[] = {
	{ T(14.0), 6, 430, 64 },
	{ T(58.0), 5, 400, 80 },
};
#define MAX_ARCHES 12

typedef struct
{
	bool alive;
	Uint8 kind, path, drop;
	float x, y, d;             // across the rail, over the ground's plane, ahead of the ship
	float vx, vy, vd;          // a tick
	float ground_z;            // P_GROUND: where it stands (world z)
	float start_x, start_y;
	int age, armor, fire;
	float flash;
	float yaw, roll, pitch;
	int wave;                  // the wave it came in (for the formation's bonus)
} Enemy;

#define MAX_ENEMIES 96
static Enemy enemies[MAX_ENEMIES];

typedef struct
{
	bool alive;
	float x, y, d, vx, vy, vd;
	int life;
	Uint8 kind;                // a laser of the ship's (0), a homing missile (1), a charged shot (2); or the enemy's shot kind
	int target;                // what it homes at: an enemy, -2 the boss, -1 nothing
} Shot;

#define MAX_SHOTS 96
#define MAX_ENEMY_SHOTS 128
static Shot shots[MAX_SHOTS], enemy_shots[MAX_ENEMY_SHOTS];

typedef struct
{
	bool alive;
	Uint8 kind;                // D_*
	float x, y, z;             // world: it hangs still while the ship flies past
	int age;
} Item;

#define MAX_ITEMS 24
static Item items[MAX_ITEMS];

typedef struct
{
	bool alive, passed;
	float x, z, foot;          // world: its middle's x and z, its foot's height
	int set;
} Arch;

static Arch arches[MAX_ARCHES];
static int next_arch_set = 0, arches_through[COUNTOF(ARCH_SETS)];
static int arch_model = -1;

static D3Particle particles[D3_MAX_PARTICLES];
static int particle_count = 0;

static struct
{
	float x, y, vx, vy;        // across the rail, height; a tick
	float z;                   // the rail's z (world) at the ship
	float speed;
	float yaw, pitch, roll;    // degrees, how it leans as it moves
	int rolling;               // ticks of a barrel roll left
	int roll_way;
	float boost;
	int fire_wait, missile_wait;
	int charge;                // ticks the fire has been held
	int lock;                  // what the reticle locked on, held charged: an enemy + 1, -1 the boss, 0 nothing
	int hit_ticks;             // since the last hit
	int power;                 // the lasers' power (1-11)
	int bombs;
	int hits;                  // enemies shot down
	int dead_ticks;            // exploding
	int safe_ticks;            // back at the checkpoint: not hurt for a while
	float shake;
	int last_left, last_right; // the ticks the directions were last pressed (a double tap rolls)
	bool held_left, held_right;
} ship;

static struct
{
	float x, y, z;             // the camera, following the ship
	float roll;
} camera;

static struct
{
	bool on, entered, dying;
	int age, armor, armor_max, fire, launch, charge;
	float x, y, d, yaw, roll, pitch, flash;
	int dying_ticks;
} boss;

static int tick = 0, next_wave = 0, kills = 0, total = 0;
static int wave_left[COUNTOF(WAVES)], wave_spawned[COUNTOF(WAVES)];
static char message[64];
static int message_ticks = 0;
static int ended = 0;          // 1 through, -1 lost
static int end_ticks = 0;
static bool paused = false, leave_asked = false;
static int fade_from = 0;      // the tick the view faded in from (the start, a checkpoint)
static bool danger_said = false;
static struct
{
	bool reached;
	float z;
	ulong cash;
	int power, bombs, hits, kills, total, next_wave;
} checkpoint;

static float rail_x(float z)
{
	// The rail weaves across the maps, gently.
	return 70.0f * sinf(z / 1900.0f) + 34.0f * sinf(z / 730.0f + 1.3f);
}

static float rail_heading(float z)
{
	// Its way across (pixels across a pixel along), the flight's turning.
	return -(70.0f / 1900.0f * cosf(z / 1900.0f) + 34.0f / 730.0f * cosf(z / 730.0f + 1.3f));
}

// The world's point for a point of the rail's frame.
static void world_of(float x, float y, float d, float out[3])
{
	const float z = ship.z - d;
	out[0] = rail_x(z) + x;
	out[1] = y;
	out[2] = z;
}

static void say(const char *text, int ticks)
{
	SDL_strlcpy(message, text, sizeof(message));
	message_ticks = ticks;
}

static int sound_queue[8];

static void sound(int channel, int sample)
{
	if (channel >= 0 && channel < 8 && sample > 0)
		sound_queue[channel] = sample;
}

static void play_sounds(void)
{
	for (int i = 0; i < 8; ++i)
		if (sound_queue[i] != 0)
		{
			multiSamplePlay(soundSamples[sound_queue[i] - 1], soundSampleCount[sound_queue[i] - 1], (unsigned int)i,
			                i == 7 ? fxPlayVol : fxPlayVol / 2);
			sound_queue[i] = 0;
		}
}

static void rail_hurt(int damage);

/* --- Effects --- */

static D3Particle *spawn(D3ParticleKind kind, const float at[3], float life)
{
	if (particle_count >= D3_MAX_PARTICLES)
		return NULL;
	D3Particle *p = &particles[particle_count++];
	memset(p, 0, sizeof(*p));
	p->kind = (Uint8)kind;
	p->x = at[0];
	p->y = at[1];
	p->z = at[2];
	p->drag = 1;
	p->life = life;
	return p;
}

static void paint(D3Particle *p, float r, float g, float b, float a, float r1, float g1, float b1, float a1)
{
	const float c[8] = { r, g, b, a, r1, g1, b1, a1 };
	memcpy(p->colour, c, sizeof(p->colour));
	memcpy(p->end_colour, c + 4, sizeof(p->end_colour));
}

static void fling(D3Particle *p, float speed)
{
	const float a = frange(0, 2 * (float)M_PI), b = frange(-1, 1);
	const float r = sqrtf(1 - b * b);
	p->vx = cosf(a) * r * speed;
	p->vy = b * speed;
	p->vz = sinf(a) * r * speed;
}

static float flash_light[RAIL_MAX_LIGHTS][8];
static int flash_light_count = 0;
static int flash_light_age[RAIL_MAX_LIGHTS];

// An explosion of size s at a world point: a flash, fire, sparks, smoke, a shock wave if large; its light.
static void explode(const float at[3], float s)
{
	D3Particle *p;
	if ((p = spawn(D3P_GLOW, at, 7)) != NULL)
	{
		p->size = s * 2.4f;
		paint(p, 6, 3.8f, 1.6f, 1, 0, 0, 0, 0);
	}
	for (int i = 0; i < 5 + (int)(s / 3); ++i)
	{
		const float c[3] = { at[0] + frange(-0.2f, 0.2f) * s, at[1] + frange(-0.2f, 0.2f) * s, at[2] + frange(-0.2f, 0.2f) * s };
		if ((p = spawn(D3P_FIRE, c, frange(18, 34))) != NULL)
		{
			fling(p, frange(0.15f, 0.5f) * s / 16.0f);
			p->vz -= SPEED * 0.4f;
			p->drag = 0.92f;
			p->size = frange(0.5f, 0.95f) * s;
			p->grow = s * 0.02f;
			paint(p, 3.2f, 1.7f, 0.55f, 1, 0.7f, 0.14f, 0.02f, 0);
		}
	}
	for (int i = 0; i < (int)(s * 1.2f); ++i)
		if ((p = spawn(D3P_GLOW, at, frange(16, 36))) != NULL)
		{
			fling(p, frange(1.2f, 3.8f) * (s / 26.0f + 0.5f));
			p->gravity = 0.06f;
			p->drag = 0.965f;
			p->size = frange(1.2f, 2.6f);
			paint(p, 4.5f, 2.6f, 0.9f, 1, 1.4f, 0.3f, 0.05f, 0);
		}
	for (int i = 0; i < 2 + (int)(s / 6); ++i)
	{
		const float c[3] = { at[0] + frange(-0.2f, 0.2f) * s, at[1] + frange(0, 0.2f) * s, at[2] };
		if ((p = spawn(D3P_SMOKE, c, frange(70, 120))) != NULL)
		{
			p->vy = frange(0.12f, 0.35f);
			p->vx = frange(-0.1f, 0.1f);
			p->size = s * frange(0.5f, 0.8f);
			p->grow = 0.24f;
			p->drag = 0.985f;
			paint(p, 0.06f, 0.055f, 0.05f, 0.55f, 0.1f, 0.095f, 0.09f, 0.0f);
		}
	}
	if (s >= 22 && (p = spawn(D3P_RING, at, 13)) != NULL)
	{
		p->size = s * 0.6f;
		p->grow = s * 0.15f;
		paint(p, 2.2f, 1.3f, 0.5f, 1, 0, 0, 0, 0);
	}
	// Its light, a few ticks.
	int slot = flash_light_count < RAIL_MAX_LIGHTS ? flash_light_count++ : 0;
	for (int i = 0; i < flash_light_count; ++i)
		if (flash_light_age[i] > flash_light_age[slot])
			slot = i;
	const float light[8] = { at[0], at[1] + 6, at[2], 40 + s * 4, 1.0f, 0.55f, 0.22f, 3.5f * SDL_min(s / 20.0f, 2.0f) };
	memcpy(flash_light[slot], light, sizeof(light));
	flash_light_age[slot] = 0;
	const float dz = at[2] - ship.z;
	if (settings3d.shake && fabsf(dz) < 500)
		ship.shake = SDL_min(ship.shake + s / 40.0f, 3.0f);
}

static void step_particles(void)
{
	for (int i = 0; i < particle_count; ++i)
	{
		D3Particle *p = &particles[i];
		if (++p->age >= p->life)
		{
			particles[i--] = particles[--particle_count];
			continue;
		}
		p->x += p->vx;
		p->y += p->vy;
		p->z += p->vz;
		p->vy -= p->gravity;
		p->vx *= p->drag;
		p->vy *= p->drag;
		p->vz *= p->drag;
		p->size = SDL_max(p->size + p->grow, 0.0f);
	}
	for (int i = 0; i < flash_light_count; ++i)
		if (++flash_light_age[i] > 8)
		{
			flash_light_age[i] = flash_light_age[flash_light_count - 1];
			memcpy(flash_light[i], flash_light[flash_light_count - 1], sizeof(flash_light[0]));
			--flash_light_count;
			--i;
		}
}

/* --- Enemies --- */

static Enemy *new_enemy(int kind, int path, int wave)
{
	for (int i = 0; i < MAX_ENEMIES; ++i)
		if (!enemies[i].alive)
		{
			Enemy *e = &enemies[i];
			memset(e, 0, sizeof(*e));
			e->alive = true;
			e->kind = (Uint8)kind;
			e->path = (Uint8)path;
			e->armor = kinds[kind].armor;
			e->fire = kinds[kind].fire > 0 ? (int)frange(30, (float)kinds[kind].fire) : 0;
			e->wave = wave;
			return e;
		}
	return NULL;
}

static void new_item(int kind, const float at[3])
{
	for (int i = 0; i < MAX_ITEMS; ++i)
		if (!items[i].alive)
		{
			items[i] = (Item){ true, (Uint8)kind, at[0], at[1], at[2], 0 };
			return;
		}
}

static void spawn_wave(int w)
{
	const Wave *wave = &WAVES[w];
	if (wave->path == P_ITEM)
	{
		float at[3];
		world_of(wave->x, wave->y, FAR - 200, at);
		new_item(wave->kind, at);
		return;
	}
	wave_left[w] = wave->count;
	wave_spawned[w] = 0;
	const float mid = (wave->count - 1) / 2.0f;
	for (int i = 0; i < wave->count; ++i)
	{
		Enemy *e = new_enemy(wave->kind, wave->path, w);
		if (e == NULL)
			break;
		++wave_spawned[w];
		++total;
		const float side = i - mid;
		e->drop = i == wave->count - 1 ? wave->drop : D_NONE;
		switch (wave->path)
		{
		case P_HEAD:
			e->x = wave->x + side * wave->spread;
			e->y = wave->y + (i & 1 ? 10 : 0);
			e->d = FAR - 100 + fabsf(side) * wave->gap;
			e->vd = -frange(3.2f, 3.8f);
			break;
		case P_CROSS:
			e->x = wave->x;
			e->y = wave->y;
			e->d = 900 + i * wave->gap;
			e->start_x = wave->x;
			e->vx = (wave->x < 0 ? 1 : -1) * 3.4f;
			e->vd = -0.6f;
			e->age = -i * 10;
			break;
		case P_BEHIND:
			e->x = wave->x + side * wave->spread;
			e->y = wave->y + fabsf(side) * 8;
			e->d = -220 - fabsf(side) * wave->gap;
			e->vd = 6.0f;
			e->yaw = 180;
			break;
		case P_HOVER:
			e->x = wave->x + side * wave->spread;
			e->y = wave->y + (i & 1 ? 18 : 0);
			e->d = FAR - 200;
			e->vd = -9.0f;
			e->start_x = e->x;
			break;
		case P_GROUND:
		{
			// Turrets a gap apart along the rail, at alternating sides.
			const float dd = FAR - 300 + i * wave->gap;
			e->x = (i & 1 ? 1 : -1) * (40 + frange(0, wave->spread)) + wave->x;
			e->ground_z = ship.z - dd;
			e->d = dd;
			e->y = ground_height(rail_x(e->ground_z) + e->x, e->ground_z) + 2;
			break;
		}
		case P_DIVE:
			e->x = wave->x + side * wave->spread;
			e->y = wave->y + fabsf(side) * 12;
			e->d = 1300 + fabsf(side) * wave->gap;
			e->vd = -4.0f;
			e->vy = 0;
			break;
		}
		e->start_y = e->y;
	}
}

static void enemy_fire(Enemy *e, float x, float y, float d, Uint8 kind)
{
	for (int i = 0; i < MAX_ENEMY_SHOTS; ++i)
		if (!enemy_shots[i].alive)
		{
			Shot *s = &enemy_shots[i];
			const float speed = kind == 1 ? 3.6f : 4.6f;
			// At where the ship will be, roughly.
			const float t = SDL_max(d, 1.0f) / (speed + ship.speed);
			const float tx = ship.x + ship.vx * t * 0.5f, ty = ship.y + ship.vy * t * 0.5f;
			float dx = tx - x, dy = ty - y, dd = -d;
			const float l = sqrtf(dx * dx + dy * dy + dd * dd);
			*s = (Shot){ true, x, y, d, dx / l * speed, dy / l * speed, dd / l * speed, 400, kind, -1 };
			(void)e;
			sound(4, S_WEAPON_10);
			return;
		}
}

static void enemy_down(Enemy *e, bool shot)
{
	float at[3];
	world_of(e->x, e->y, e->d, at);
	explode(at, kinds[e->kind].radius * 1.4f);
	sound(5, e->kind == K_TAN || e->kind == K_BROWN || e->kind == K_DOME ? S_EXPLOSION_9 : S_EXPLOSION_4);
	e->alive = false;
	if (!shot)
		return;
	++kills;
	++ship.hits;
	player[0].cash += (ulong)kinds[e->kind].value;
	if (e->drop != D_NONE)
		new_item(e->drop, at);
	// A whole formation shot down: a bonus.
	if (e->wave >= 0 && --wave_left[e->wave] == 0 && wave_spawned[e->wave] >= 3)
	{
		ship.hits += 2;
		player[0].cash += 500;
		say("Formation down  +500", HZ * 2);
	}
}

static void move_enemy(Enemy *e)
{
	++e->age;
	const Kind *k = &kinds[e->kind];
	switch (e->path)
	{
	case P_HEAD:
		e->d += e->vd - (ship.speed - SPEED);
		e->x += sinf(e->age * 0.035f + e->start_y) * 0.6f;
		e->yaw = 0;
		e->roll = sinf(e->age * 0.035f + e->start_y) * 22;
		break;
	case P_CROSS:
		if (e->age > 0)
		{
			e->x += e->vx;
			e->y += sinf(e->age * 0.05f) * 0.4f;
		}
		e->d += e->vd - (ship.speed - SPEED);
		e->yaw = e->vx > 0 ? -60.0f : 60.0f;
		e->roll = e->vx > 0 ? 35.0f : -35.0f;
		break;
	case P_BEHIND:
		if (e->vd > -4.0f)
		{
			// Overtaking, then slowing ahead and turning round.
			if (e->d > 480)
				e->vd -= 0.12f;
			e->yaw = e->vd > 0 ? 180 : 180 - 180 * clampf(-e->vd / 4.0f, 0, 1);
		}
		else
			e->yaw = 0;
		e->d += e->vd - (ship.speed - SPEED);
		e->x += (e->start_x - e->x) * 0.02f + sinf(e->age * 0.03f) * 0.5f;
		e->roll = sinf(e->age * 0.03f) * 20;
		break;
	case P_HOVER:
		if (e->age < 140)
		{
			e->vd = approach(e->vd, 0, 0.08f);
			e->d += e->vd;
			e->yaw = 0;
		}
		else if (e->age < 140 + 520)
		{
			e->x = e->start_x + sinf((e->age - 140) * 0.022f) * 60;
			e->y = e->start_y + sinf((e->age - 140) * 0.031f) * 18;
			e->roll = cosf((e->age - 140) * 0.022f) * 30;
			e->d += (ship.speed < SPEED ? 0.6f : ship.speed > SPEED ? -1.2f : 0);
		}
		else
		{
			// Away up and ahead.
			e->vy += 0.05f;
			e->y += e->vy;
			e->d += 2.5f;
			e->yaw = 180;
			if (e->y > 400)
				e->alive = false;
		}
		break;
	case P_GROUND:
		e->d = ship.z - e->ground_z;
		e->x = e->x;  // (it stands: the rail's x under it changes, not its own)
		e->yaw = 0;
		break;
	case P_DIVE:
		e->d += e->vd - (ship.speed - SPEED);
		if (e->d < 900)
		{
			e->vy = approach(e->vy, -1.6f, 0.05f);
			e->y = SDL_max(e->y + e->vy, ground_height(rail_x(ship.z - e->d) + e->x, ship.z - e->d) + 18);
		}
		e->pitch = -e->vy * 12;
		e->yaw = 0;
		break;
	}
	if (e->d < -260 || e->d > FAR + 600 || fabsf(e->x) > 900)
	{
		e->alive = false;
		return;
	}
	e->flash *= 0.8f;
	// Its fire, while ahead and near enough.
	if (k->fire > 0 && e->d > 160 && e->d < 1500 && ended == 0 && --e->fire <= 0)
	{
		e->fire = k->fire + (int)frange(-20, 20);
		enemy_fire(e, e->x, e->y + (k->ground ? 10 : 0), e->d, k->shot);
	}
	// Into the ship.
	if (ship.dead_ticks == 0 && fabsf(e->d) < k->radius && ended == 0)
	{
		const float dx = e->x - ship.x, dy = e->y - ship.y;
		if (dx * dx + dy * dy < (k->radius + SHIP_RADIUS) * (k->radius + SHIP_RADIUS))
		{
			rail_hurt(8);
			enemy_down(e, false);
		}
	}
}

/* --- The boss: SAVARA's big red jet (SAVARA's events place its pieces so: tools/content/episode6 waves) --- */

static const struct { const char *model; float dx, dz; } BOSS_PIECES[] = {
	{ "redwing_201", -12, -28 }, { "redwing_203", 12, -28 }, { "redwing_237", -36, 0 }, { "redwing_239", -12, 0 },
	{ "redwing_241", 12, 0 }, { "redwing_243", 36, 0 }, { "redwing_278", 0, 28 },
};
static int boss_models[COUNTOF(BOSS_PIECES)];

static void boss_begin(void)
{
	memset(&boss, 0, sizeof(boss));
	boss.on = true;
	boss.armor = boss.armor_max = kinds[K_BOSS].armor;
	boss.x = 0;
	boss.y = 170;
	boss.d = -420;
	boss.yaw = 180;
	boss.fire = 120;
	boss.launch = 400;
	++total;
	printf("rail: the boss at tick %d, %d plants in view\n", tick, view.plant_count);
	say("Warning: the Collector's flagship", HZ * 3);
	JE_playSampleNum(V_BOSS);
}

static bool boss_hit_test(float x, float y, float d, float r)
{
	if (!boss.on || boss.dying)
		return false;
	const float s = kinds[K_BOSS].scale;
	static const float spheres[3][2] = { { 0, 0 }, { -30, 4 }, { 30, 4 } };
	for (int i = 0; i < 3; ++i)
	{
		const float c = cosf(boss.yaw * (float)M_PI / 180.0f);
		const float bx = boss.x + spheres[i][0] * s, bd = boss.d - spheres[i][1] * s * c;
		const float dx = x - bx, dy = y - boss.y, dd = d - bd, rr = 20 * s + r;
		if (dx * dx + dy * dy + dd * dd < rr * rr)
			return true;
	}
	return false;
}

static void boss_hurt(int damage)
{
	boss.armor -= damage;
	boss.flash = 1;
	if (boss.armor <= 0 && !boss.dying)
	{
		boss.dying = true;
		boss.dying_ticks = 0;
		for (int j = 0; j < MAX_ENEMY_SHOTS; ++j)
			enemy_shots[j].alive = false;
	}
}

static void boss_fire_fan(int n, float spread)
{
	for (int i = 0; i < n; ++i)
	{
		const float a = (i - (n - 1) / 2.0f) * spread;
		for (int j = 0; j < MAX_ENEMY_SHOTS; ++j)
			if (!enemy_shots[j].alive)
			{
				const float speed = 4.2f;
				float dx = ship.x - boss.x, dy = ship.y - boss.y, dd = -boss.d;
				const float l = sqrtf(dx * dx + dy * dy + dd * dd);
				dx /= l;
				dy /= l;
				dd /= l;
				const float c = cosf(a), sn = sinf(a);
				enemy_shots[j] = (Shot){ true, boss.x, boss.y - 6, boss.d - 20, (dx * c + dd * sn) * speed, dy * speed,
				                         (dd * c - dx * sn) * speed, 400, (Uint8)(i == (n - 1) / 2 ? 1 : 0), -1 };
				break;
			}
	}
	sound(4, S_WEAPON_13);
}

static void boss_tick(void)
{
	if (!boss.on)
		return;
	++boss.age;
	boss.flash *= 0.8f;
	if (boss.dying)
	{
		// Falling, burning, breaking up.
		++boss.dying_ticks;
		boss.y -= 0.5f + boss.dying_ticks * 0.012f;
		boss.roll += 1.6f;
		boss.d += 0.4f;
		if (boss.dying_ticks % 9 == 0)
		{
			float at[3];
			world_of(boss.x + frange(-60, 60), boss.y + frange(-10, 10), boss.d + frange(-40, 40), at);
			explode(at, frange(18, 34));
			sound(5 + (boss.dying_ticks / 9) % 2, S_EXPLOSION_11);
		}
		const float ground = ground_height(rail_x(ship.z - boss.d) + boss.x, ship.z - boss.d);
		if (boss.dying_ticks > 200 || boss.y < ground + 10)
		{
			float at[3];
			world_of(boss.x, boss.y, boss.d, at);
			for (int i = 0; i < 4; ++i)
			{
				const float c[3] = { at[0] + frange(-60, 60), at[1] + frange(0, 30), at[2] + frange(-60, 60) };
				explode(c, 46);
			}
			sound(7, S_EXPLOSION_22);
			boss.on = false;
			++kills;
			++ship.hits;
			player[0].cash += (ulong)kinds[K_BOSS].value;
			if (ended == 0)
			{
				ended = 1;
				end_ticks = 0;
				say("Mission complete", HZ * 5);
				JE_playSampleNum(V_LEVEL_END);
			}
		}
		return;
	}
	if (!boss.entered)
	{
		// Up from behind, over the ship, then round at it.
		boss.d += 6.5f - (ship.speed - SPEED);
		boss.y = approach(boss.y, 110, 0.4f);
		if (boss.d > 460)
		{
			boss.entered = true;
			boss.age = 0;
		}
		return;
	}
	const bool angry = boss.armor * 2 < boss.armor_max;
	boss.yaw = approach(boss.yaw, 0, 2.4f);
	boss.pitch = approach(boss.pitch, boss.yaw < 30 ? 16.0f : 0.0f, 0.4f);  // (its top towards the camera)
	const float t = (float)boss.age;
	const float pace = angry ? 1.5f : 1.0f;
	float aim_d = 440 + 50 * sinf(t * 0.011f);
	if (angry && boss.charge > 0)
	{
		// A charge at the ship, then back.
		--boss.charge;
		aim_d = boss.charge > 60 ? 190.0f : 440.0f;
	}
	else if (angry && boss.age % 520 == 260)
		boss.charge = 120;
	boss.d = approach(boss.d, aim_d, angry && boss.charge > 60 ? 6.0f : 3.0f) - (ship.speed - SPEED);
	const float to_x = 90 * sinf(t * 0.013f * pace), to_y = 100 + 28 * sinf(t * 0.017f * pace);
	const float old_x = boss.x;
	boss.x += (to_x - boss.x) * 0.04f;
	boss.y += (to_y - boss.y) * 0.04f;
	boss.roll = clampf((boss.x - old_x) * -14, -30, 30);
	if (ended == 0 && ship.dead_ticks == 0 && --boss.fire <= 0)
	{
		boss.fire = angry ? 38 : 58;
		boss_fire_fan(angry ? 7 : 5, 0.12f);
	}
	if (ended == 0 && --boss.launch <= 0)
	{
		// Fighters from under its wings.
		boss.launch = angry ? 330 : 450;
		for (int i = 0; i < 4; ++i)
		{
			Enemy *e = new_enemy(K_DELTA, P_HEAD, -1);
			if (e == NULL)
				break;
			++total;
			e->x = boss.x + (i - 1.5f) * 40;
			e->y = boss.y - 10;
			e->d = boss.d - 30;
			e->vd = -4.0f;
			e->start_y = e->y;
		}
	}
	if (angry && boss.age % 4 == 0)
	{
		// Smoke from its burning wing.
		float at[3];
		world_of(boss.x + 30 * kinds[K_BOSS].scale, boss.y + 4, boss.d, at);
		D3Particle *p = spawn(D3P_SMOKE, at, frange(50, 80));
		if (p != NULL)
		{
			p->vy = 0.3f;
			p->vz = SPEED * 0.6f;
			p->size = 14;
			p->grow = 0.3f;
			p->drag = 0.99f;
			paint(p, 0.07f, 0.06f, 0.06f, 0.6f, 0.1f, 0.1f, 0.1f, 0);
		}
	}
	// Into the ship.
	if (ship.dead_ticks == 0 && boss_hit_test(ship.x, ship.y, 0, SHIP_RADIUS))
	{
		rail_hurt(4);
	}
}

/* --- The ship --- */

static void rail_hurt(int damage)
{
	if (ship.dead_ticks > 0 || (ship.rolling > 0 && damage < 8) || ended != 0)
		return;
	if (dev_godmode() || ship.safe_ticks > 0)
		damage = 0;
	ship.hit_ticks = 0;
	ship.shake = SDL_min(ship.shake + 1.2f, 3.0f);
	if ((int)player[0].shield >= damage)
	{
		player[0].shield -= (uint)damage;
		sound(6, S_SHIELD_HIT);
		return;
	}
	damage -= (int)player[0].shield;
	player[0].shield = 0;
	sound(6, S_HULL_HIT);
	if ((int)player[0].armor > damage)
	{
		player[0].armor -= (uint)damage;
		return;
	}
	player[0].armor = 0;
	ship.dead_ticks = 1;
	float at[3];
	world_of(ship.x, ship.y, 0, at);
	explode(at, 40);
	sound(7, S_EXPLOSION_22);
}

typedef struct
{
	float dx, dy;      // -1..1
	bool fire, bomb, boost, brake;
	bool left, right;  // the directions held (for a double tap)
} Input;

static Input read_input(void)
{
	Input in = { 0 };
	service_SDL_events(false);
	// Keys.
	in.left = keysactive[keySettings[KEY_SETTING_LEFT]];
	in.right = keysactive[keySettings[KEY_SETTING_RIGHT]];
	in.dx = (in.right ? 1.0f : 0.0f) - (in.left ? 1.0f : 0.0f);
	in.dy = (keysactive[keySettings[KEY_SETTING_UP]] ? 1.0f : 0.0f) - (keysactive[keySettings[KEY_SETTING_DOWN]] ? 1.0f : 0.0f);
	in.fire = keysactive[keySettings[KEY_SETTING_FIRE]];
	in.bomb = keysactive[keySettings[KEY_SETTING_CHANGE_FIRE]];
	in.brake = keysactive[keySettings[KEY_SETTING_LEFT_SIDEKICK]];
	in.boost = keysactive[keySettings[KEY_SETTING_RIGHT_SIDEKICK]];
	// Joysticks.
	for (int j = 0; j < joysticks; ++j)
	{
		poll_joystick(j);
		if (joystick[j].analog)
		{
			in.dx += clampf(joystick[j].x / 24000.0f, -1, 1);
			in.dy -= clampf(joystick[j].y / 24000.0f, -1, 1);
		}
		else
		{
			in.dx += (joystick[j].direction[1] ? 1.0f : 0.0f) - (joystick[j].direction[3] ? 1.0f : 0.0f);
			in.dy += (joystick[j].direction[0] ? 1.0f : 0.0f) - (joystick[j].direction[2] ? 1.0f : 0.0f);
		}
		in.left |= joystick[j].direction[3];
		in.right |= joystick[j].direction[1];
		in.fire |= joystick[j].action[0];
		in.bomb |= joystick[j].action_pressed[1];
		in.brake |= joystick[j].action[2];
		in.boost |= joystick[j].action[3];
		if (joystick[j].action_pressed[5])
			paused = true;
	}
	// The mouse: moving it moves the ship; its buttons fire, boost and bomb.
	if (has_mouse)
	{
		Sint32 mx, my;
		mouseGetRelativePosition(&mx, &my);
		in.dx += clampf(mx / 6.0f, -1.5f, 1.5f);
		in.dy -= clampf(my / 6.0f, -1.5f, 1.5f);
		in.fire |= mouse_pressed[0];
		in.boost |= mouse_pressed[1];
		in.bomb |= mouse_pressed[2];
	}
	in.dx = clampf(in.dx, -1.5f, 1.5f);
	in.dy = clampf(in.dy, -1.5f, 1.5f);
	// The autopilot (dev): at the nearest enemy ahead, firing.
	if (dev_autopilot())
	{
		const Enemy *best = NULL;
		for (int i = 0; i < MAX_ENEMIES; ++i)
			if (enemies[i].alive && enemies[i].d > 120 && enemies[i].d < 1200 && (best == NULL || enemies[i].d < best->d))
				best = &enemies[i];
		float tx = 0, ty = 80;
		if (boss.on && boss.entered)
			tx = boss.x, ty = boss.y;
		else if (best != NULL)
			tx = best->x, ty = best->y;
		for (int i = 0; i < MAX_ARCHES; ++i)
			if (arches[i].alive && !arches[i].passed && ship.z - arches[i].z > 0 && ship.z - arches[i].z < 600)
				tx = arches[i].x - rail_x(arches[i].z), ty = arches[i].foot + 50;  // (through the arch ahead)
		in.dx = clampf((tx - ship.x) / 30.0f, -1, 1);
		in.dy = clampf((ty - ship.y) / 30.0f, -1, 1);
		in.fire = tick % 150 < 130;  // (let go now and then: a charged shot)
	}
	return in;
}

static void ship_fire(void)
{
	// Twin lasers from the wings (one at low power), along the ship's nose.
	const float yaw = -ship.yaw * (float)M_PI / 180.0f, pitch = ship.pitch * (float)M_PI / 180.0f;
	const float fx = sinf(yaw) * cosf(pitch), fy = sinf(pitch), fd = cosf(yaw) * cosf(pitch);
	const int guns = ship.power >= 3 ? 2 : 1;
	for (int g = 0; g < guns; ++g)
	{
		for (int i = 0; i < MAX_SHOTS; ++i)
			if (!shots[i].alive)
			{
				const float side = guns == 1 ? 0 : (g == 0 ? -7.0f : 7.0f);
				shots[i] = (Shot){ true, ship.x + side, ship.y - 1, 10, fx * LASER_SPEED, fy * LASER_SPEED, fd * LASER_SPEED,
				                   LASER_LIFE, 0, -1 };
				break;
			}
	}
	sound(0, ship.power >= 7 ? S_WEAPON_2 : S_WEAPON_1);
}

static void ship_missile(void)
{
	// A homing missile (the ship's rear gun, if it has one) at the nearest enemy ahead.
	int best = -1;
	for (int i = 0; i < MAX_ENEMIES; ++i)
		if (enemies[i].alive && enemies[i].d > 80 && enemies[i].d < 1200 && (best < 0 || enemies[i].d < enemies[best].d))
			best = i;
	if (best < 0 && !(boss.on && boss.entered && !boss.dying))
		return;
	for (int i = 0; i < MAX_SHOTS; ++i)
		if (!shots[i].alive)
		{
			shots[i] = (Shot){ true, ship.x, ship.y - 4, 6, 0, 1.0f, 6.0f, 160, 1, best };
			sound(1, S_WEAPON_6);
			return;
		}
}

static void bomb(void)
{
	if (ship.bombs <= 0)
		return;
	--ship.bombs;
	// Everything near ahead (the boss hurt) goes in a blinding flash.
	float at[3];
	world_of(ship.x, ship.y, 380, at);
	explode(at, 60);
	D3Particle *p = spawn(D3P_RING, at, 26);
	if (p != NULL)
	{
		p->size = 40;
		p->grow = 26;
		paint(p, 3, 3, 4, 1, 0, 0, 0, 0);
	}
	for (int i = 0; i < MAX_ENEMIES; ++i)
		if (enemies[i].alive && enemies[i].d > -40 && enemies[i].d < 1100)
			enemy_down(&enemies[i], true);
	for (int i = 0; i < MAX_ENEMY_SHOTS; ++i)
		enemy_shots[i].alive = false;
	if (boss.on && boss.entered && !boss.dying && boss.d < 1100)
		boss_hurt(60);
	sound(7, S_EXPLOSION_22);
}

// While the charge is held the reticle locks on what it passes over: the enemy nearest the line along the nose (or the
// boss), kept till it is gone.
static void lock_on(void)
{
	if ((ship.lock > 0 && enemies[ship.lock - 1].alive) || (ship.lock < 0 && boss.on && !boss.dying))
		return;
	ship.lock = 0;
	const float yaw = -ship.yaw * (float)M_PI / 180.0f, pitch = ship.pitch * (float)M_PI / 180.0f;
	const float f[3] = { sinf(yaw) * cosf(pitch), sinf(pitch), cosf(yaw) * cosf(pitch) };
	float best = 1;
	for (int i = -1; i < MAX_ENEMIES; ++i)
	{
		float x, y, d, radius;
		if (i < 0)
		{
			if (!boss.on || !boss.entered || boss.dying)
				continue;
			x = boss.x, y = boss.y, d = boss.d, radius = kinds[K_BOSS].radius;
		}
		else
		{
			const Enemy *e = &enemies[i];
			if (!e->alive)
				continue;
			x = e->x, y = e->y, d = e->d, radius = kinds[e->kind].radius;
		}
		const float r[3] = { x - ship.x, y - ship.y, d };
		const float along = r[0] * f[0] + r[1] * f[1] + r[2] * f[2];
		if (d < 60 || d > 1500 || along < 60)
			continue;
		const float off[3] = { r[0] - f[0] * along, r[1] - f[1] * along, r[2] - f[2] * along };
		const float miss = sqrtf(off[0] * off[0] + off[1] * off[1] + off[2] * off[2]) / (radius + 14 + along * 0.05f);
		if (miss < best)
		{
			best = miss;
			ship.lock = i < 0 ? -1 : i + 1;
		}
	}
	if (ship.lock != 0)
		sound(6, S_CLICK);
}

// Let go charged: a ball of light along the nose, homing at what the reticle locked on, bursting on what it meets.
static void ship_charged(void)
{
	const float yaw = -ship.yaw * (float)M_PI / 180.0f, pitch = ship.pitch * (float)M_PI / 180.0f;
	const float speed = 9.5f;
	for (int i = 0; i < MAX_SHOTS; ++i)
		if (!shots[i].alive)
		{
			shots[i] = (Shot){ true, ship.x, ship.y - 1, 12, sinf(yaw) * cosf(pitch) * speed, sinf(pitch) * speed,
			                   cosf(yaw) * cosf(pitch) * speed, 170, 2, ship.lock > 0 ? ship.lock - 1 : ship.lock < 0 ? -2 : -1 };
			sound(1, S_WEAPON_7);
			return;
		}
}

// A charged shot bursts: all near it hurt, a bonus for several shot down at once.
static void burst(const Shot *s)
{
	float at[3];
	world_of(s->x, s->y, s->d, at);
	explode(at, 34);
	D3Particle *p = spawn(D3P_RING, at, 16);
	if (p != NULL)
	{
		p->size = 10;
		p->grow = BLAST / 8;
		paint(p, 1.6f, 4.2f, 1.4f, 1, 0, 0, 0, 0);
	}
	int down = 0;
	for (int e = 0; e < MAX_ENEMIES; ++e)
	{
		Enemy *en = &enemies[e];
		if (!en->alive)
			continue;
		const float dx = s->x - en->x, dy = s->y - en->y, dd = s->d - en->d, r = BLAST + kinds[en->kind].radius;
		if (dx * dx + dy * dy + dd * dd < r * r)
		{
			en->flash = 1;
			en->armor -= BLAST_DAMAGE;
			if (en->armor <= 0)
			{
				enemy_down(en, true);
				++down;
			}
		}
	}
	if (boss_hit_test(s->x, s->y, s->d, BLAST))
		boss_hurt(BLAST_DAMAGE);
	printf("rail: a charged shot burst at tick %d, %d down\n", tick, down);
	if (down >= 2)
	{
		// (Each one past the first: a hit more, as Star Fox counts them.)
		ship.hits += down - 1;
		char text[32];
		snprintf(text, sizeof(text), "Hit +%d", down - 1);
		say(text, HZ * 2);
	}
	sound(7, S_EXPLOSION_11);
}

static void ship_tick(const Input *in)
{
	if (ship.dead_ticks > 0)
	{
		++ship.dead_ticks;
		ship.y -= 0.6f;
		ship.roll += 9;
		if (ship.dead_ticks % 8 == 0 && ship.dead_ticks < 70)
		{
			float at[3];
			world_of(ship.x + frange(-8, 8), ship.y, frange(-8, 8), at);
			explode(at, 16);
		}
		return;
	}
	// A double tap of a direction rolls the ship.
	if (in->left && !ship.held_left)
	{
		if (tick - ship.last_left < 14 && ship.rolling == 0)
			ship.rolling = ROLL_TICKS, ship.roll_way = -1;
		ship.last_left = tick;
	}
	if (in->right && !ship.held_right)
	{
		if (tick - ship.last_right < 14 && ship.rolling == 0)
			ship.rolling = ROLL_TICKS, ship.roll_way = 1;
		ship.last_right = tick;
	}
	ship.held_left = in->left;
	ship.held_right = in->right;
	const float accel = 0.5f, top = 3.4f;
	ship.vx = clampf(ship.vx * 0.84f + in->dx * accel, -top, top);
	ship.vy = clampf(ship.vy * 0.84f + in->dy * accel * 0.85f, -top, top);
	if (ship.rolling > 0)
		ship.vx += ship.roll_way * 0.9f;
	ship.x = clampf(ship.x + ship.vx, -SHIP_X, SHIP_X);
	const float ground = ground_height(rail_x(ship.z) + ship.x, ship.z);
	ship.y = clampf(ship.y + ship.vy, SDL_max(SHIP_LOW, ground + 14), SHIP_HIGH);
	if (ship.y < ground + 15 && tick % 20 == 0)
		rail_hurt(2);  // scraping the ground
	// Boost and brake.
	float speed = SPEED;
	if (in->boost && ship.boost > 1)
	{
		speed = SPEED_BOOST;
		ship.boost -= 0.9f;
	}
	else if (in->brake && ship.boost > 1)
	{
		speed = SPEED_BRAKE;
		ship.boost -= 0.6f;
	}
	else
		ship.boost = SDL_min(ship.boost + 0.35f, BOOST_MAX);
	if (boss.on && boss.entered)
		speed = SPEED + (speed - SPEED) * 0.5f;  // (the boss keeps its distance)
	ship.speed += (speed - ship.speed) * 0.08f;
	// How it leans.
	ship.yaw = -ship.vx * 6;
	ship.pitch = ship.vy * 5;
	if (ship.rolling > 0)
	{
		--ship.rolling;
		ship.roll = ship.roll_way * 360.0f * (1.0f - ship.rolling / (float)ROLL_TICKS) - ship.vx * 8;
	}
	else
		ship.roll = -ship.vx * 9;
	// Firing: a press fires the lasers, and they go on while it is held; held long enough, a charge glows at the nose
	// and the reticle locks on; let go, the charge goes.
	if (ship.fire_wait > 0)
		--ship.fire_wait;
	if (in->fire && ship.fire_wait == 0)
	{
		ship_fire();
		ship.fire_wait = ship.power >= 9 ? 5 : 7;
	}
	if (in->fire)
	{
		if (++ship.charge == CHARGE_TICKS)
			sound(6, S_POWERUP);
		if (ship.charge >= CHARGE_TICKS)
			lock_on();
	}
	else
	{
		if (ship.charge >= CHARGE_TICKS)
			ship_charged();
		ship.charge = ship.lock = 0;
	}
	if (ship.missile_wait > 0)
		--ship.missile_wait;
	if (in->fire && ship.missile_wait == 0 && player[0].items.weapon[REAR_WEAPON].id != 0)
	{
		ship_missile();
		ship.missile_wait = 110;
	}
	static bool bomb_held = false;
	if (in->bomb && !bomb_held)
		bomb();
	bomb_held = in->bomb;
	// The shield comes back, a while after the last hit.
	++ship.hit_ticks;
	if (ship.hit_ticks > 140 && tick % 26 == 0 && player[0].shield < player[0].shield_max)
		++player[0].shield;
	ship.shake *= 0.88f;
}

/* --- Shots and items --- */

static void shots_tick(void)
{
	for (int i = 0; i < MAX_SHOTS; ++i)
	{
		Shot *s = &shots[i];
		if (!s->alive)
			continue;
		if (s->kind == 1)
		{
			// A missile turns at its target.
			float tx = 0, ty = 0, td = 0;
			bool there = false;
			if (s->target >= 0 && enemies[s->target].alive)
				tx = enemies[s->target].x, ty = enemies[s->target].y, td = enemies[s->target].d, there = true;
			else if (boss.on && boss.entered && !boss.dying)
				tx = boss.x, ty = boss.y, td = boss.d, there = true;
			if (there)
			{
				float dx = tx - s->x, dy = ty - s->y, dd = td - s->d;
				const float l = sqrtf(dx * dx + dy * dy + dd * dd) + 0.01f;
				s->vx += dx / l * 0.9f;
				s->vy += dy / l * 0.9f;
				s->vd += dd / l * 0.9f;
				const float v = sqrtf(s->vx * s->vx + s->vy * s->vy + s->vd * s->vd);
				if (v > 9)
					s->vx *= 9 / v, s->vy *= 9 / v, s->vd *= 9 / v;
			}
			if (tick % 2 == 0)
			{
				float at[3];
				world_of(s->x, s->y, s->d, at);
				D3Particle *p = spawn(D3P_SMOKE, at, 30);
				if (p != NULL)
				{
					p->size = 4;
					p->grow = 0.25f;
					paint(p, 0.5f, 0.5f, 0.5f, 0.5f, 0.6f, 0.6f, 0.6f, 0);
				}
			}
		}
		else if (s->kind == 2)
		{
			// A charged shot turns hard at what it locked on, and bursts on the first thing it meets (or the ground, or
			// at the end of its way).
			float tx = 0, ty = 0, td = 0;
			bool there = false;
			if (s->target >= 0 && enemies[s->target].alive)
				tx = enemies[s->target].x, ty = enemies[s->target].y, td = enemies[s->target].d, there = true;
			else if (s->target == -2 && boss.on && !boss.dying)
				tx = boss.x, ty = boss.y, td = boss.d, there = true;
			if (there)
			{
				float dx = tx - s->x, dy = ty - s->y, dd = td - s->d;
				const float l = sqrtf(dx * dx + dy * dy + dd * dd) + 0.01f;
				s->vx += dx / l * 1.5f;
				s->vy += dy / l * 1.5f;
				s->vd += dd / l * 1.5f;
				const float v = sqrtf(s->vx * s->vx + s->vy * s->vy + s->vd * s->vd);
				if (v > 11)
					s->vx *= 11 / v, s->vy *= 11 / v, s->vd *= 11 / v;
			}
			s->x += s->vx;
			s->y += s->vy;
			s->d += s->vd;
			float at[3];
			world_of(s->x, s->y, s->d, at);
			D3Particle *p = spawn(D3P_GLOW, at, 14);
			if (p != NULL)
			{
				p->size = 7;
				p->drag = 0.9f;
				fling(p, 0.4f);
				paint(p, 1.2f, 3.6f, 1.2f, 1, 0.1f, 0.6f, 0.1f, 0);
			}
			bool meets = --s->life <= 0 || s->d > FAR || s->y < ground_height(at[0], at[2]) + 2 ||
			             boss_hit_test(s->x, s->y, s->d, 6);
			for (int e = 0; e < MAX_ENEMIES && !meets; ++e)
			{
				const Enemy *en = &enemies[e];
				const float r = kinds[en->kind].radius + 6, dx = s->x - en->x, dy = s->y - en->y, dd = s->d - en->d;
				meets = en->alive && dx * dx + dy * dy + dd * dd < r * r;
			}
			if (meets)
			{
				s->alive = false;
				burst(s);
			}
			continue;
		}
		const float ox = s->x, oy = s->y, od = s->d;
		s->x += s->vx;
		s->y += s->vy;
		s->d += s->vd - (ship.speed - SPEED) * 0;
		if (--s->life <= 0 || s->d > FAR)
		{
			s->alive = false;
			continue;
		}
		const int damage = s->kind == 1 ? 6 : ship.power >= 8 ? 3 : ship.power >= 5 ? 2 : 1;
		// What it hits on its way this tick.
		for (int k = 0; k <= 3 && s->alive; ++k)
		{
			const float f = k / 3.0f;
			const float x = ox + (s->x - ox) * f, y = oy + (s->y - oy) * f, d = od + (s->d - od) * f;
			for (int e = 0; e < MAX_ENEMIES && s->alive; ++e)
			{
				Enemy *en = &enemies[e];
				if (!en->alive)
					continue;
				const float r = kinds[en->kind].radius + 3;
				const float dx = x - en->x, dy = y - en->y, dd = d - en->d;
				if (dx * dx + dy * dy + dd * dd < r * r)
				{
					s->alive = false;
					en->flash = 1;
					en->armor -= damage;
					float at[3];
					world_of(x, y, d, at);
					D3Particle *p = spawn(D3P_GLOW, at, 6);
					if (p != NULL)
					{
						p->size = 10;
						paint(p, 3, 4, 2, 1, 0, 0, 0, 0);
					}
					if (en->armor <= 0)
						enemy_down(en, true);
					else
						sound(3, S_ENEMY_HIT);
				}
			}
			if (s->alive && boss_hit_test(x, y, d, 3))
			{
				s->alive = false;
				boss_hurt(damage);
				sound(3, S_ENEMY_HIT);
				float at[3];
				world_of(x, y, d, at);
				D3Particle *p = spawn(D3P_GLOW, at, 6);
				if (p != NULL)
				{
					p->size = 12;
					paint(p, 4, 3, 1.5f, 1, 0, 0, 0, 0);
				}
			}
		}
	}
	for (int i = 0; i < MAX_ENEMY_SHOTS; ++i)
	{
		Shot *s = &enemy_shots[i];
		if (!s->alive)
			continue;
		s->x += s->vx;
		s->y += s->vy;
		s->d += s->vd - (ship.speed - SPEED);
		if (--s->life <= 0 || s->d < -120 || s->d > FAR)
		{
			s->alive = false;
			continue;
		}
		if (ship.dead_ticks == 0 && fabsf(s->d) < 8)
		{
			const float dx = s->x - ship.x, dy = s->y - ship.y;
			const float r = ship.rolling > 0 ? 20.0f : SHIP_RADIUS + (s->kind == 1 ? 4 : 2);
			if (dx * dx + dy * dy < r * r)
			{
				s->alive = false;
				if (ship.rolling > 0)
				{
					float at[3];
					world_of(s->x, s->y, s->d, at);
					D3Particle *p = spawn(D3P_GLOW, at, 8);
					if (p != NULL)
					{
						p->size = 12;
						paint(p, 2, 3, 5, 1, 0, 0, 0, 0);
					}
					sound(2, S_CLINK);
				}
				else
					rail_hurt(s->kind == 1 ? 6 : 3);
			}
		}
	}
}

static void items_tick(void)
{
	for (int i = 0; i < MAX_ITEMS; ++i)
	{
		Item *it = &items[i];
		if (!it->alive)
			continue;
		++it->age;
		const float d = ship.z - it->z;
		if (d < -150)
		{
			it->alive = false;
			continue;
		}
		const float dx = it->x - (rail_x(ship.z) + ship.x), dy = it->y - ship.y;
		if (ship.dead_ticks == 0 && fabsf(d) < 14 && dx * dx + dy * dy < 24 * 24)
		{
			it->alive = false;
			switch (it->kind)
			{
			case D_SHIELD:
				player[0].shield = player[0].shield_max;
				say("Shield restored", HZ * 2);
				break;
			case D_ARMOR:
				player[0].armor = SDL_min(player[0].armor + SDL_max(player[0].initial_armor / 3, 4u), player[0].initial_armor);
				say("Armor repaired", HZ * 2);
				break;
			case D_POWER:
				ship.power = SDL_min(ship.power + 2, 11);
				say("Lasers up", HZ * 2);
				break;
			case D_BOMB:
				ship.bombs = SDL_min(ship.bombs + 1, 9);
				say("Bomb", HZ * 2);
				break;
			case D_CASH:
				player[0].cash += 1000;
				say("+1000", HZ * 2);
				break;
			}
			ship.hits += 1;
			sound(7, it->kind == D_CASH ? S_ITEM : S_POWERUP);
		}
	}
}

/* --- The view --- */

static void add_object(int model, const float at[3], float yaw, float pitch, float roll, float scale, float flash, bool shadow)
{
	if (model < 0 || view.object_count >= RAIL_MAX_OBJECTS)
		return;
	view.objects[view.object_count++] = (RailObject){ model, at[0], at[1], at[2], yaw, pitch, roll, scale, flash, shadow };
}

static void add_glow(const float at[3], float size, float r, float g, float b, int kind)
{
	if (view.glow_count >= RAIL_MAX_GLOWS)
		return;
	view.glows[view.glow_count++] = (RailGlow){ at[0], at[1], at[2], size, { r, g, b }, (Uint8)kind };
}

// A soft shadow on the ground under something at a world point (radius: its size), darker the lower it flies.
static void add_shadow(const float at[3], float radius)
{
	if (view.shadow_count >= RAIL_MAX_SHADOWS)
		return;
	const float ground = ground_height(at[0], at[2]), h = at[1] - ground;
	if (h < 0 || h > 170)
		return;
	view.shadows[view.shadow_count++] = (RailShadow){ at[0] + h * 0.35f, ground + 0.8f, at[2] - h * 0.3f, radius * 2.4f * (1 + h / 220),
	                                                  0.5f * (1 - h / 170) };
}

static int kind_models[K_COUNT];
static int ship_model = -1;

// The plants of the ground's maps in view, the nearest first (grass only near: far off its blades are too small to see).
static void plants_in(float z_far, float z_near)
{
	const B3DVegetation *veg = b3d_vegetation();
	view.plant_count = 0;
	if (veg == NULL)
		return;
	const Layer *l = NULL;
	for (int i = 0; i < layer_count; ++i)
		if (layers[i].set == veg->set)
			l = &layers[i];
	if (l == NULL)
		return;
	const float length = l->length;
	// Each stretch of the map end to end (mirrored every other) the view's z range crosses, the nearest first.
	for (int n = (int)floorf(z_near / length); n >= (int)floorf(z_far / length); --n)
	{
		const bool flipped = (n & 1) != 0;
		const float base = n * length;
		// The rows of the map in view in this stretch.
		float m0 = SDL_max(z_far - base, 0.0f), m1 = SDL_min(z_near - base, length);
		if (m0 >= m1)
			continue;
		if (flipped)
		{
			const float t = length - m1;
			m1 = length - m0;
			m0 = t;
		}
		const int r0 = SDL_clamp((int)(m0 / TILE_H), 0, veg->rows - 1), r1 = SDL_clamp((int)(m1 / TILE_H), 0, veg->rows - 1);
		const int first = veg->row_start[r0], last = veg->row_start[r1 + 1] - 1;
		for (int k = 0; k <= last - first && view.plant_count < RAIL_MAX_PLANTS; ++k)
		{
			// (Near first: down the map's rows where it runs as made, up them where mirrored.)
			const B3DPlant *p = &veg->plants[flipped ? first + k : last - k];
			const float z = base + (flipped ? length - p->y : p->y);
			if (z > z_near || z < z_far || (p->kind == B3D_GRASS && z_near - z > 760))
				continue;
			// Where it stands in the map's own columns, and so in each of its mirror images beside it.
			const float u = p->x - (float)((veg->side_columns - l->sides) * TILE_W);
			if (u < 0 || u >= l->width)
				continue;
			// (Inside the ground's texture a narrower map's images side by side; beyond it, the texture's mirror images
			// of those, as ground_height and the texture take them.)
			const float middle = rail_x(z);
			for (int m = -3; m <= 3; ++m)
			{
				const float inside = m * l->width + ((m & 1) ? l->width - u : u) - l->centre;
				if (inside < -tex_half || inside >= tex_half)
					continue;
				const float images[3] = { inside, 2 * tex_half - inside, -2 * tex_half - inside };
				for (int k = 0; k < 3 && view.plant_count < RAIL_MAX_PLANTS; ++k)
					if (fabsf(images[k] - middle) < 900)
						view.plants[view.plant_count++] = (RailPlant){ images[k], ground_height(images[k], z), z, p->size / 8.0f,
						                                               p->turn / 256.0f * 360.0f + (m + k) * 90.0f, p->shade / 128.0f,
						                                               p->kind };
			}
		}
	}
}

/* --- The arches --- */

static void arch_set_begin(int set)
{
	const ArchSet *a = &ARCH_SETS[set];
	arches_through[set] = 0;
	for (int k = 0; k < a->count; ++k)
		for (int i = 0; i < MAX_ARCHES; ++i)
			if (!arches[i].alive)
			{
				Arch *arch = &arches[i];
				arch->alive = true;
				arch->passed = false;
				arch->set = set;
				arch->z = ship.z - (FAR - 60) - k * a->gap;
				arch->x = rail_x(arch->z) + a->swing * sinf(k * 1.1f + set * 2.0f);
				// (Its foot at the lower of its pillars' ground: they go into it.)
				arch->foot = SDL_min(ground_height(arch->x - (ARCH_INNER + ARCH_OUTER) / 2, arch->z),
				                     ground_height(arch->x + (ARCH_INNER + ARCH_OUTER) / 2, arch->z)) - 2;
				break;
			}
}

// The ship through an arch's plane this tick (from z_before): through its opening, a hit on it, or past it beside.
static void arches_tick(float z_before)
{
	for (int i = 0; i < MAX_ARCHES; ++i)
	{
		Arch *a = &arches[i];
		if (!a->alive)
			continue;
		if (ship.z - a->z < -200)
		{
			a->alive = false;
			continue;
		}
		if (a->passed || ship.dead_ticks > 0 || ended != 0 || !(z_before > a->z && ship.z <= a->z))
			continue;
		a->passed = true;
		const float u = rail_x(ship.z) + ship.x - a->x, v = ship.y - a->foot - ARCH_SPRING;
		const float inner = ARCH_INNER - SHIP_RADIUS * 0.7f, outer = ARCH_OUTER + SHIP_RADIUS * 0.7f;
		const bool through = v < 0 ? fabsf(u) < inner : u * u + v * v < inner * inner;
		const bool on = v < 0 ? fabsf(u) < outer : u * u + v * v < outer * outer;
		const ArchSet *set = &ARCH_SETS[a->set];
		char text[48];
		printf("rail: %s an arch of set %d at tick %d (%.0f across its middle, %.0f over its spring)\n",
		       through ? "through" : on ? "into" : "past", a->set + 1, tick, u, v);
		if (through)
		{
			player[0].cash += 100;
			if (++arches_through[a->set] == set->count)
			{
				player[0].cash += 1000;
				ship.hits += 2;
				ship.bombs = SDL_min(ship.bombs + 1, 9);
				say("All arches  +1000  +bomb", HZ * 3);
				sound(7, S_POWERUP);
			}
			else
			{
				snprintf(text, sizeof(text), "Arch %d of %d", arches_through[a->set], set->count);
				say(text, HZ * 3 / 2);
				sound(7, S_ITEM);
			}
		}
		else if (on)
		{
			// Into its stone: hurt, thrown off.
			rail_hurt(8);
			ship.vx = (u < 0 ? -1 : 1) * (fabsf(u) < (ARCH_INNER + ARCH_OUTER) / 2 ? -3.0f : 3.0f);  // (in, or out)
			ship.vy = v > 0 ? -2.5f : 0;
			float at[3];
			world_of(ship.x, ship.y, -4, at);
			for (int k = 0; k < 14; ++k)
			{
				D3Particle *p = spawn(D3P_GLOW, at, frange(10, 22));
				if (p != NULL)
				{
					fling(p, frange(1, 3));
					p->gravity = 0.08f;
					p->size = frange(1.2f, 2.2f);
					paint(p, 4, 3, 1.5f, 1, 1, 0.3f, 0.05f, 0);
				}
			}
		}
	}
}

static void build_view(void)
{
	view.object_count = view.glow_count = view.shadow_count = 0;
	// The camera: behind the ship and over it, following it softly, leaning into its turns.
	const float shake_x = ship.shake > 0.05f ? frange(-ship.shake, ship.shake) : 0, shake_y = ship.shake > 0.05f ? frange(-1, 1) * ship.shake : 0;
	camera.x += (ship.x * 0.72f - camera.x) * 0.12f;
	camera.y += (ship.y * 0.72f + 28 - camera.y) * 0.12f;
	camera.roll += ((-ship.vx * 1.1f + rail_heading(ship.z) * -70.0f) - camera.roll) * 0.06f;
	const float cz = ship.z + CAMERA_BEHIND;
	view.position[0] = rail_x(cz) + camera.x + shake_x;
	view.position[1] = camera.y + CAMERA_ABOVE + shake_y;
	view.position[2] = cz;
	// It looks at a point ahead of the ship.
	float target[3];
	world_of(ship.x * 0.5f, ship.y * 0.6f + 14, 420, target);
	float f[3] = { target[0] - view.position[0], target[1] - view.position[1], target[2] - view.position[2] };
	const float fl = sqrtf(f[0] * f[0] + f[1] * f[1] + f[2] * f[2]);
	for (int i = 0; i < 3; ++i)
		view.forward[i] = f[i] / fl;
	const float r = camera.roll * (float)M_PI / 180.0f;
	// Up, rolled about forward: world up made square to forward, then turned.
	float up[3] = { 0, 1, 0 };
	const float dot = up[1] * view.forward[1];
	for (int i = 0; i < 3; ++i)
		up[i] -= view.forward[i] * dot;
	const float ul = sqrtf(up[0] * up[0] + up[1] * up[1] + up[2] * up[2]);
	for (int i = 0; i < 3; ++i)
		up[i] /= ul;
	const float right[3] = { view.forward[1] * up[2] - view.forward[2] * up[1], view.forward[2] * up[0] - view.forward[0] * up[2],
	                         view.forward[0] * up[1] - view.forward[1] * up[0] };
	for (int i = 0; i < 3; ++i)
		view.up[i] = up[i] * cosf(r) + right[i] * sinf(r);
	view.fov_degrees = 58.0f + (ship.speed - SPEED) * 2.5f;  // (wider at speed)
	view.chunk_last = (int)floorf((cz + 200) / RAIL_CHUNK);
	view.chunk_first = (int)floorf((cz - FAR - 300) / RAIL_CHUNK);
	view.shadow_centre[0] = rail_x(ship.z) + ship.x;
	view.shadow_centre[1] = 40;
	view.shadow_centre[2] = ship.z - 220;

	// The ship, its engines' glow.
	float at[3];
	world_of(ship.x, ship.y, 0, at);
	if (ship.dead_ticks == 0 || ship.dead_ticks < 40)
	{
		add_object(ship_model, at, ship.yaw, ship.pitch, ship.roll, SHIP_SCALE, ship.hit_ticks < 6 ? 0.8f : 0, true);
		add_shadow(at, 14);
		if (ship.dead_ticks == 0)
		{
			const float glow = ship.speed > SPEED + 0.5f ? 1.6f : ship.speed < SPEED - 0.5f ? 0.5f : 1.0f;
			const float tail[3] = { at[0] - sinf(-ship.yaw * (float)M_PI / 180.0f) * 14, at[1] + 2, at[2] + 15 };
			add_glow(tail, 4.5f * glow, 1.0f * glow, 1.5f * glow, 4.0f * glow, RAIL_GLOW_DOT);
		}
	}
	// The reticles, ahead along the nose.
	if (ship.dead_ticks == 0 && ended == 0)
	{
		const float yaw = -ship.yaw * (float)M_PI / 180.0f, pitch = ship.pitch * (float)M_PI / 180.0f;
		const bool locked = ship.lock != 0;
		for (int k = 1; k <= 2; ++k)
		{
			const float dist = 160.0f * k;
			float p[3];
			world_of(ship.x + sinf(yaw) * dist, ship.y + sinf(pitch) * dist, cosf(yaw) * dist, p);
			if (locked)
				add_glow(p, k == 1 ? 13.0f : 18.0f, 1.4f, 0.3f, 0.2f, RAIL_GLOW_RING);
			else
				add_glow(p, k == 1 ? 13.0f : 18.0f, 0.25f, 1.1f, 0.35f, RAIL_GLOW_RING);
		}
		// The charge at the nose, growing; full, pulsing.
		if (ship.charge > 8)
		{
			const float full = ship.charge >= CHARGE_TICKS ? 1.0f + 0.25f * sinf(tick * 0.5f) : 0.0f;
			const float grow = SDL_min(ship.charge - 8, CHARGE_TICKS - 8) / (float)(CHARGE_TICKS - 8);
			float p[3];
			world_of(ship.x + sinf(yaw) * 16, ship.y - 1 + sinf(pitch) * 16, cosf(yaw) * 16, p);
			add_glow(p, 3 + 5 * grow + 2 * full, 0.8f + full, 2.4f + full * 1.5f, 0.8f + full, RAIL_GLOW_DOT);
		}
		// What it locked on, ringed red.
		if (ship.lock > 0 || (ship.lock < 0 && boss.on))
		{
			float p[3];
			float size;
			if (ship.lock > 0)
			{
				const Enemy *e = &enemies[ship.lock - 1];
				world_of(e->x, e->y, e->d, p);
				if (e->path == P_GROUND)
					p[0] = rail_x(e->ground_z) + e->x, p[2] = e->ground_z;
				size = kinds[e->kind].radius * 1.9f;
			}
			else
			{
				world_of(boss.x, boss.y, boss.d, p);
				size = kinds[K_BOSS].radius * 1.6f;
			}
			const float pulse = 1.0f + 0.12f * sinf(tick * 0.4f);
			add_glow(p, size * pulse, 3.4f, 0.5f, 0.3f, RAIL_GLOW_RING);
			add_glow(p, size * 0.7f * pulse, 2.0f, 0.3f, 0.2f, RAIL_GLOW_RING);
		}
	}
	// The enemies.
	for (int i = 0; i < MAX_ENEMIES; ++i)
	{
		const Enemy *e = &enemies[i];
		if (!e->alive || e->d > FAR)
			continue;
		world_of(e->x, e->y, e->d, at);
		if (e->path == P_GROUND)
		{
			at[0] = rail_x(e->ground_z) + e->x;
			at[2] = e->ground_z;
		}
		float yaw = e->yaw, pitch = e->pitch;
		if (!kinds[e->kind].ground && fabsf(e->yaw) < 1 && e->d > 0)
		{
			// Coming at the ship: its nose at it, its top a little towards the camera (flat models read edge on).
			yaw = atan2f(ship.x - e->x, e->d) * 180.0f / (float)M_PI;
			pitch += atan2f(e->y - ship.y, e->d) * 180.0f / (float)M_PI + 10.0f;
		}
		add_object(kind_models[e->kind], at, yaw, pitch, e->roll, kinds[e->kind].scale, e->flash, true);
		if (!kinds[e->kind].ground)
			add_shadow(at, kinds[e->kind].radius);
	}
	// The arches, square to the rail.
	for (int i = 0; i < MAX_ARCHES; ++i)
	{
		const Arch *a = &arches[i];
		if (!a->alive || ship.z - a->z > FAR + 100)
			continue;
		const float pos[3] = { a->x, a->foot, a->z };
		add_object(arch_model, pos, -atanf(rail_heading(a->z)) * 180.0f / (float)M_PI, 0, 0, 1, 0, true);
	}
	// The boss's pieces.
	if (boss.on)
	{
		world_of(boss.x, boss.y, boss.d, at);
		add_shadow(at, 70);
		const float s = kinds[K_BOSS].scale, y = boss.yaw * (float)M_PI / 180.0f, rl = boss.roll * (float)M_PI / 180.0f;
		for (size_t p = 0; p < COUNTOF(BOSS_PIECES); ++p)
		{
			// (A piece's place turned by the jet's yaw and roll.)
			const float lx = BOSS_PIECES[p].dx * s, lz0 = BOSS_PIECES[p].dz * s, pt = boss.pitch * (float)M_PI / 180.0f;
			const float rx = lx * cosf(rl), ry0 = lx * sinf(rl);
			const float ry = ry0 * cosf(pt) - lz0 * sinf(pt), lz = ry0 * sinf(pt) + lz0 * cosf(pt);
			const float pos[3] = { at[0] + rx * cosf(y) + lz * sinf(y), at[1] + ry, at[2] - rx * sinf(y) + lz * cosf(y) };
			add_object(boss_models[p], pos, boss.yaw, boss.pitch, boss.roll, s, boss.flash, true);
		}
		if (!boss.dying)
			for (int k = -1; k <= 1; k += 2)
			{
				// Its engines.
				const float lx = k * 24 * s, lz = -40 * s;
				const float pos[3] = { at[0] + lx * cosf(y) + lz * sinf(y), at[1] + 2, at[2] - lx * sinf(y) + lz * cosf(y) };
				add_glow(pos, 16, 4, 1.6f, 0.6f, RAIL_GLOW_DOT);
			}
	}
	// The shots: lasers as streaks, the enemies' as glowing balls.
	for (int i = 0; i < MAX_SHOTS; ++i)
	{
		const Shot *s = &shots[i];
		if (!s->alive)
			continue;
		if (s->kind == 2)
		{
			// A charged shot: a ball of green light.
			world_of(s->x, s->y, s->d, at);
			const float pulse = 1.0f + 0.2f * sinf(s->life * 0.9f);
			add_glow(at, 15 * pulse, 1.0f, 3.2f, 1.0f, RAIL_GLOW_DOT);
			add_glow(at, 7, 4.0f, 5.0f, 4.0f, RAIL_GLOW_DOT);
			add_glow(at, 22 * pulse, 0.5f, 1.8f, 0.5f, RAIL_GLOW_RING);
			continue;
		}
		const bool blue = ship.power >= 6;
		for (int k = 0; k < 5; ++k)
		{
			const float f = 1.0f - k * 0.2f;
			world_of(s->x - s->vx * k * 0.35f, s->y - s->vy * k * 0.35f, s->d - s->vd * k * 0.35f, at);
			if (s->kind == 1)
				add_glow(at, 6 * f, 4 * f, 2.4f * f, 1 * f, RAIL_GLOW_DOT);
			else
				add_glow(at, (k == 0 ? 6.5f : 5.0f) * f, (blue ? 0.6f : 0.8f) * f, (blue ? 1.8f : 4.0f) * f, (blue ? 5.0f : 0.9f) * f,
				         RAIL_GLOW_DOT);
		}
	}
	for (int i = 0; i < MAX_ENEMY_SHOTS; ++i)
	{
		const Shot *s = &enemy_shots[i];
		if (!s->alive)
			continue;
		world_of(s->x, s->y, s->d, at);
		const float k = s->kind == 1 ? 1.4f : 1.0f;
		add_glow(at, 9 * k, 4.5f, s->kind == 1 ? 1.8f : 0.8f, 0.4f, RAIL_GLOW_DOT);
		add_glow(at, 4 * k, 5, 4, 3, RAIL_GLOW_DOT);
	}
	// The items: rings and capsules turning.
	for (int i = 0; i < MAX_ITEMS; ++i)
	{
		const Item *it = &items[i];
		if (!it->alive)
			continue;
		at[0] = it->x;
		at[1] = it->y + sinf(it->age * 0.08f) * 2;
		at[2] = it->z;
		const float pulse = 1.0f + 0.15f * sinf(it->age * 0.2f);
		switch (it->kind)
		{
		case D_SHIELD:
			add_glow(at, 26 * pulse, 1.6f, 2.0f, 2.6f, RAIL_GLOW_RING);
			break;
		case D_ARMOR:
			add_glow(at, 26 * pulse, 3.0f, 2.2f, 0.6f, RAIL_GLOW_RING);
			break;
		case D_POWER:
			add_glow(at, 12 * pulse, 0.8f, 1.6f, 5.0f, RAIL_GLOW_DOT);
			add_glow(at, 20 * pulse, 0.4f, 0.8f, 2.4f, RAIL_GLOW_RING);
			break;
		case D_BOMB:
			add_glow(at, 12 * pulse, 4.0f, 1.0f, 0.8f, RAIL_GLOW_DOT);
			add_glow(at, 20 * pulse, 2.4f, 0.6f, 0.4f, RAIL_GLOW_RING);
			break;
		default:
			add_glow(at, 10 * pulse, 4.0f, 3.2f, 0.8f, RAIL_GLOW_DOT);
			break;
		}
	}
	view.light_count = flash_light_count;
	memcpy(view.lights, flash_light, sizeof(flash_light[0]) * (size_t)flash_light_count);
	plants_in(cz - FAR, cz + 80);
	// The fade: in at the start, out at the end.
	view.fade = ended != 0 ? clampf(1.0f - (end_ticks - HZ * 4) / (float)HZ, 0, 1) : clampf((tick - fade_from) / 40.0f, 0, 1);
}

static void publish_hud(void)
{
	UIMenu *ui = ui_menu_begin(UI_SCREEN_RAIL, levelName);
	ui->text_color = 255;
	ui->selected = -1;
	ui->wheel = UI_WHEEL_NONE;
	UIRail *r = &ui->rail;
	r->shield = player[0].shield_max > 0 ? player[0].shield / (float)player[0].shield_max : 0;
	r->armor = player[0].initial_armor > 0 ? player[0].armor / (float)player[0].initial_armor : 0;
	r->boost = ship.boost / BOOST_MAX;
	r->score = (long)player[0].cash;
	r->hits = ship.hits;
	r->bombs = ship.bombs;
	r->power = ship.power;
	r->boss = boss.on && boss.entered ? SDL_max(boss.armor, 0) / (float)boss.armor_max : -1;
	SDL_strlcpy(r->boss_name, "COLLECTOR FLAGSHIP", sizeof(r->boss_name));
	if (message_ticks > 0)
		SDL_strlcpy(r->message, message, sizeof(r->message));
	r->message_alpha = clampf(message_ticks / 30.0f, 0, 1);
	r->paused = paused;
	r->leave_asked = leave_asked;
	SDL_strlcpy(r->level, levelName, sizeof(r->level));
	r->title_alpha = clampf(1.0f - (tick - HZ * 3) / (float)HZ, 0, 1);
	ui_menu_publish(ui, VGAScreen, VGAScreen);
}

static void begin_level(void)
{
	memset(enemies, 0, sizeof(enemies));
	memset(shots, 0, sizeof(shots));
	memset(enemy_shots, 0, sizeof(enemy_shots));
	memset(items, 0, sizeof(items));
	memset(arches, 0, sizeof(arches));
	memset(&boss, 0, sizeof(boss));
	particle_count = flash_light_count = 0;
	memset(&ship, 0, sizeof(ship));
	ship.z = (float)(layers[0].length - 140);  // (the maps' bottom, where the level starts)
	ship.y = 80;
	ship.speed = SPEED;
	ship.boost = BOOST_MAX;
	ship.power = SDL_clamp(player[0].items.weapon[FRONT_WEAPON].power, 1, 11);
	ship.bombs = 2 + (player[0].items.special != 0);
	ship.last_left = ship.last_right = -100;
	camera.x = 0;
	camera.y = ship.y + 28;
	camera.roll = 0;
	tick = next_wave = next_arch_set = kills = total = fade_from = 0;
	danger_said = false;
	memset(&checkpoint, 0, sizeof(checkpoint));
	ended = end_ticks = 0;
	message_ticks = 0;
	paused = leave_asked = false;
	for (int k = 0; k < K_COUNT; ++k)
		kind_models[k] = kinds[k].model != NULL ? m3d_find_model(kinds[k].model) : -1;
	for (size_t p = 0; p < COUNTOF(BOSS_PIECES); ++p)
		boss_models[p] = m3d_find_model(BOSS_PIECES[p].model);
	arch_model = m3d_find_model("rail_arch");
	// (TYR3D_RAIL_FROM=<tick>, dev: the flight from there, its waves before skipped.)
	const char *from = SDL_getenv("TYR3D_RAIL_FROM");
	if (from != NULL && SDL_atoi(from) > 0)
	{
		tick = fade_from = SDL_atoi(from);
		ship.z -= SPEED * tick;
		while (next_wave < (int)COUNTOF(WAVES) && WAVES[next_wave].tick <= tick)
			++next_wave;
		while (next_arch_set < (int)COUNTOF(ARCH_SETS) && ARCH_SETS[next_arch_set].tick <= tick)
			++next_arch_set;
	}
	const M3DAppearance look = m3d_ship_appearance(player[0].items.ship);
	ship_model = look.model >= 0 ? look.model : m3d_find_model("talon");
	// The ship as the level would have it.
	JE_getShipInfo();
	player[0].shield = shields[player[0].items.shield].mpwr;
	player[0].shield_max = player[0].shield * 2;
	player[0].is_alive = true;
	// (From behind the camera, high on the left: what comes at the ship is lit.)
	view.sun[0] = 0.42f;
	view.sun[1] = -0.78f;
	view.sun[2] = -0.46f;
	const float sky_top[3] = { 0.22f, 0.4f, 0.72f }, horizon[3] = { 0.7f, 0.78f, 0.86f }, haze[3] = { 0.62f, 0.7f, 0.78f };
	memcpy(view.sky_top, sky_top, sizeof(sky_top));
	memcpy(view.sky_horizon, horizon, sizeof(horizon));
	memcpy(view.haze, haze, sizeof(haze));
	view.haze_near = 500;
	view.haze_far = FAR;
}

// A ship lost past the checkpoint flies on from there: the enemies gone, the ship whole, the cash and the rest as they
// were there.
static void back_to_checkpoint(void)
{
	memset(enemies, 0, sizeof(enemies));
	memset(shots, 0, sizeof(shots));
	memset(enemy_shots, 0, sizeof(enemy_shots));
	memset(items, 0, sizeof(items));
	memset(arches, 0, sizeof(arches));
	memset(&boss, 0, sizeof(boss));
	particle_count = flash_light_count = 0;
	const float boost = BOOST_MAX;
	memset(&ship, 0, sizeof(ship));
	ship.z = checkpoint.z;
	ship.y = 80;
	ship.speed = SPEED;
	ship.boost = boost;
	ship.power = checkpoint.power;
	ship.bombs = checkpoint.bombs;
	ship.hits = checkpoint.hits;
	ship.last_left = ship.last_right = -100;
	ship.safe_ticks = HZ * 2;
	player[0].cash = checkpoint.cash;
	player[0].armor = player[0].initial_armor;
	player[0].shield = player[0].shield_max;
	kills = checkpoint.kills;
	total = checkpoint.total;
	next_wave = checkpoint.next_wave;
	tick = fade_from = CHECKPOINT_TICK;
	next_arch_set = 0;
	while (next_arch_set < (int)COUNTOF(ARCH_SETS) && ARCH_SETS[next_arch_set].tick <= tick)
		++next_arch_set;
	danger_said = false;
	camera.x = 0;
	camera.y = ship.y + 28;
	say("Back at the checkpoint", HZ * 3);
	printf("rail: back at the checkpoint (tick %d)\n", tick);
}

static void level_tick(const Input *in)
{
	++tick;
	const float z_before = ship.z;
	ship.z -= ship.speed;
	while (next_wave < (int)COUNTOF(WAVES) && WAVES[next_wave].tick <= tick)
		spawn_wave(next_wave++);
	while (next_arch_set < (int)COUNTOF(ARCH_SETS) && ARCH_SETS[next_arch_set].tick <= tick)
		arch_set_begin(next_arch_set++);
	if (tick == BOSS_TICK)
		boss_begin();
	if (tick == CHECKPOINT_TICK && ship.dead_ticks == 0)
	{
		checkpoint = (typeof(checkpoint)){ true, ship.z, player[0].cash, ship.power, ship.bombs, ship.hits, kills, total, next_wave };
		say("Checkpoint", HZ * 2);
		sound(7, S_ITEM);
	}
	ship_tick(in);
	if (ship.safe_ticks > 0)
		--ship.safe_ticks;
	// Low on armor: a warning, once, and smoke from the ship.
	if (ship.dead_ticks == 0 && player[0].armor * 10 < player[0].initial_armor * 3)
	{
		if (!danger_said)
		{
			danger_said = true;
			JE_playSampleNum(V_DANGER);
			say("Armor low", HZ * 2);
		}
		if (tick % 3 == 0)
		{
			float at[3];
			world_of(ship.x, ship.y + 2, -10, at);
			D3Particle *p = spawn(D3P_SMOKE, at, frange(30, 50));
			if (p != NULL)
			{
				p->vy = 0.2f;
				p->vz = ship.speed * 0.8f;
				p->size = 5;
				p->grow = 0.25f;
				p->drag = 0.98f;
				paint(p, 0.12f, 0.11f, 0.1f, 0.55f, 0.15f, 0.15f, 0.15f, 0);
			}
		}
	}
	for (int i = 0; i < MAX_ENEMIES; ++i)
		if (enemies[i].alive)
			move_enemy(&enemies[i]);
	boss_tick();
	shots_tick();
	items_tick();
	arches_tick(z_before);
	step_particles();
	ground_tick(ship.z + CAMERA_BEHIND + 200, ship.z - FAR - 300);
	if (message_ticks > 0)
		--message_ticks;
	if (ship.dead_ticks > 0 && ended == 0 && ship.dead_ticks > 90)
	{
		if (checkpoint.reached)
			back_to_checkpoint();
		else
		{
			ended = -1;
			end_ticks = 0;
		}
	}
	if (ended != 0)
		++end_ticks;
}

bool rail_active(void)
{
	return active;
}

const RailView *rail_view(void)
{
	return &view;
}

int rail_particles(const D3Particle **out)
{
	*out = particles;
	return particle_count;
}

bool rail_play(void)
{
	rail_next_level = false;
	// The level's palette (as its HUD's picture brings it), at once.
	memcpy(colors, palettes[pcxpal[3 - 1]], sizeof(colors));
	JE_gammaCorrect(&colors, gammaCorrection);
	set_palette(colors, 0, 255);
	if (!ground_begin())
		return true;  // (no ground to fly over: the level counts as flown)
	begin_level();
	// The ground near the start, whole, before the first frame.
	for (int i = 0; i < 8; ++i)
		ground_tick(ship.z + CAMERA_BEHIND + 200, ship.z - FAR - 300);
	active = true;
	printf("rail: %s, %d waves, ground %d x %d texels a chunk\n", levelName, (int)COUNTOF(WAVES), tex_w, TEX_H);
	play_song(levelSong - 1);
	JE_playSampleNum(V_GOOD_LUCK);
	mouseSetRelative(true);
	JE_clearKeyboard();
	totalEnemy = enemyKilled = 0;
	const Uint64 started = SDL_GetTicks();
	const double tick_seconds = 1.0 / HZ;
	Uint64 last = SDL_GetPerformanceCounter();
	double behind = tick_seconds;
	for (;;)
	{
		const Input in = read_input();
		// P pauses and goes on; Esc pauses, and Esc again while paused leaves the level; any other key goes on.
		const bool escape = keysactive[SDL_SCANCODE_ESCAPE], pause_key = keysactive[SDL_SCANCODE_P];
		keysactive[SDL_SCANCODE_ESCAPE] = keysactive[SDL_SCANCODE_P] = false;
		if (paused)
		{
			if (escape && leave_asked)
			{
				ended = -1;
				break;
			}
			if (escape)
				leave_asked = true;
			else if (pause_key || newkey)
				paused = leave_asked = false;
			newkey = false;
		}
		else if (escape || pause_key)
		{
			paused = true;
			leave_asked = escape;
			newkey = false;
		}
		// The game goes on at HZ ticks a second whatever the display's pace (a few ticks a frame at most).
		const Uint64 now = SDL_GetPerformanceCounter();
		behind = SDL_min(behind + (now - last) / (double)SDL_GetPerformanceFrequency(), 4 * tick_seconds);
		last = now;
		if (paused)
			behind = 0;
		else if (behind < tick_seconds)
		{
			SDL_Delay(1);
			continue;
		}
		while (behind >= tick_seconds)
		{
			level_tick(&in);
			behind -= tick_seconds;
		}
		build_view();
		publish_hud();
		JE_showVGA();
		play_sounds();
		if (paused)
			SDL_Delay(10);
		if (ended != 0 && end_ticks > HZ * 5)
			break;
	}
	active = false;
	ui_screen_done();
	ground_end();
	mouseSetRelative(false);
	totalEnemy = (JE_word)SDL_min(total, 65535);
	enemyKilled = (JE_word)SDL_min(kills, 65535);
	const bool through = ended > 0;
	player[0].is_alive = through;
	if (through)
		player[0].cash += (ulong)ship.hits * 25;
	printf("rail: %s, %s, %d of %d shot down, %d hits, %d ticks in %.1f s\n", levelName, through ? "through" : "lost", kills, total,
	       ship.hits, tick, (SDL_GetTicks() - started) / 1000.0);
	fade_black(10);
	return through;
}
