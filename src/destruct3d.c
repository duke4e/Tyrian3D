/*
 * Tyrian3D: Destruct's battles in 3D (destruct3d.h).
 *
 * The ridge is a density field over the field's columns (and the land beside it), its rows and its
 * slices from the face back, made into meshes by surface nets, a chunk of columns at a time; a chunk
 * is made again when the field has changed under it. The density at a slice: the field's dirt there
 * now (smoothed a pixel), or, where the game has dug dirt away, the dirt as it was behind the bowl the
 * hole digs into the ridge (as deep as the distance from the hole's pixel to the dirt left).
 */
#include "destruct3d.h"

#include <math.h>
#include <stdlib.h>
#include <string.h>

#define PIXEL_DIRT 25           // destruct.c's dirt; 17-24 the original's softened edges of it
#define GRID_W (D3_W + 2 * D3_PAD)
#define Y0 8                    // the grid's rows (above: air; below: dirt)
#define Y1 236
#define GRID_H (Y1 - Y0 + 1)
#define S_LAST (D3_SLICES - 1)  // the last slice (beyond it the ridge goes on as it is)
#define CARVE_MAX ((D3_SLICES - 2) * D3_SLICE)

static bool active = false;
static D3Tick shown;
static Uint8 field[D3_H * D3_W];      // the field as shown (its pixels)

// The density's parts per grid point (row-major, GRID_W a row).
static float occ[GRID_H * GRID_W];    // the dirt now, smoothed
static float orig[GRID_H * GRID_W];   // the dirt as the field was made, smoothed
static float carve[GRID_H * GRID_W];  // how deep the dug bowl goes back (game pixels)
static float raw_now[GRID_H * GRID_W], raw_orig[GRID_H * GRID_W];
static float decor_top[GRID_W];       // the land beside the field: its first row of dirt
static float top_orig[GRID_W];        // each column's top as made (world y), for the land behind
static unsigned int field_generation = 0;

static inline int at(int gx, int y)
{
	return (y - Y0) * GRID_W + gx;
}

static Uint32 hash32(Uint32 x)
{
	x ^= x >> 16;
	x *= 0x7feb352dU;
	x ^= x >> 15;
	x *= 0x846ca68bU;
	x ^= x >> 16;
	return x;
}

static float hash_unit(Uint32 x)
{
	return (hash32(x) & 0xffffff) / (float)0x1000000;
}

static float srgb_linear(float c)
{
	c /= 255.0f;
	return c <= 0.04045f ? c / 12.92f : powf((c + 0.055f) / 1.055f, 2.4f);
}

/* --- The field ---------------------------------------------------------------------------- */

// How much of a pixel is dirt: the dirt, the original's softened edges a little.
static float pixel_dirt(Uint8 p)
{
	if (p == PIXEL_DIRT)
		return 1.0f;
	if (p >= 17 && p <= 24)
		return 0.3f;
	return 0.0f;
}

// The grid's raw dirt from the field's pixels: the field's columns (its edge columns, empty in the
// game, as their neighbours), the land beside it, dirt below the field.
static void raw_from_field(const Uint8 *pixels, float *raw)
{
	for (int y = Y0; y <= Y1; ++y)
		for (int gx = 0; gx < GRID_W; ++gx)
		{
			const int x = gx - D3_PAD;
			float v;
			if (y >= D3_H)
				v = 1.0f;
			else if (x < 0 || x >= D3_W)
				v = y >= decor_top[gx] ? 1.0f : 0.0f;
			else if (y < D3_TOP)
				v = 0.0f;
			else
				v = pixel_dirt(pixels[y * D3_W + SDL_clamp(x, 1, D3_W - 2)]);
			raw[at(gx, y)] = v;
		}
}

// A 3x3 blur (the field's stair-steps smoothed).
static void smooth(const float *raw, float *out)
{
	for (int y = Y0; y <= Y1; ++y)
		for (int gx = 0; gx < GRID_W; ++gx)
		{
			float sum = 0, weight = 0;
			for (int dy = -1; dy <= 1; ++dy)
				for (int dx = -1; dx <= 1; ++dx)
				{
					const int yy = y + dy, xx = gx + dx;
					if (xx < 0 || xx >= GRID_W)
						continue;
					const float w = (dx == 0 ? 2.0f : 1.0f) * (dy == 0 ? 2.0f : 1.0f);
					const float v = yy < Y0 ? 0.0f : yy > Y1 ? 1.0f : raw[at(xx, yy)];
					sum += w * v;
					weight += w;
				}
			out[at(gx, y)] = sum / weight;
		}
}

// How deep each dug pixel's bowl goes: its distance to the dirt left (chamfer 3-4), as deep.
static void carve_depths(const float *raw)
{
	static int dist[GRID_H * GRID_W];
	const int far = 1 << 20;
	for (int i = 0; i < GRID_H * GRID_W; ++i)
		dist[i] = raw[i] >= 0.5f ? 0 : far;
	for (int y = Y0; y <= Y1; ++y)
		for (int gx = 0; gx < GRID_W; ++gx)
		{
			int d = dist[at(gx, y)];
			if (gx > 0)
				d = SDL_min(d, dist[at(gx - 1, y)] + 3);
			if (y > Y0)
			{
				d = SDL_min(d, dist[at(gx, y - 1)] + 3);
				if (gx > 0)
					d = SDL_min(d, dist[at(gx - 1, y - 1)] + 4);
				if (gx < GRID_W - 1)
					d = SDL_min(d, dist[at(gx + 1, y - 1)] + 4);
			}
			dist[at(gx, y)] = d;
		}
	for (int y = Y1; y >= Y0; --y)
		for (int gx = GRID_W - 1; gx >= 0; --gx)
		{
			int d = dist[at(gx, y)];
			if (gx < GRID_W - 1)
				d = SDL_min(d, dist[at(gx + 1, y)] + 3);
			if (y < Y1)
			{
				d = SDL_min(d, dist[at(gx, y + 1)] + 3);
				if (gx > 0)
					d = SDL_min(d, dist[at(gx - 1, y + 1)] + 4);
				if (gx < GRID_W - 1)
					d = SDL_min(d, dist[at(gx + 1, y + 1)] + 4);
			}
			dist[at(gx, y)] = d;
		}
	// (Smoothed, so the bowls are round where the flares have eaten the dirt pixel by pixel.)
	static float depth[GRID_H * GRID_W];
	for (int i = 0; i < GRID_H * GRID_W; ++i)
		depth[i] = SDL_min(dist[i] / 3.0f + 0.5f, CARVE_MAX);
	for (int y = Y0; y <= Y1; ++y)
		for (int gx = 0; gx < GRID_W; ++gx)
		{
			float sum = 0;
			int n = 0;
			for (int dy = -2; dy <= 2; ++dy)
				for (int dx = -2; dx <= 2; ++dx)
				{
					const int yy = y + dy, xx = gx + dx;
					if (yy < Y0 || yy > Y1 || xx < 0 || xx >= GRID_W)
						continue;
					sum += depth[at(xx, yy)];
					++n;
				}
			carve[at(gx, y)] = sum / n;
		}
}

static float density(int gx, int y, int s)
{
	if (y < Y0 || s < 0)
		return 0.0f;
	if (y > Y1)
		return 1.0f;
	gx = SDL_clamp(gx, 0, GRID_W - 1);
	s = SDL_min(s, S_LAST);
	const int i = at(gx, y);
	const float z = s * D3_SLICE;
	const float behind = orig[i] * SDL_clamp((z - carve[i]) * 0.5f + 0.5f, 0.0f, 1.0f);
	return SDL_max(occ[i], behind);
}

/* --- The ridge's meshes (surface nets) --------------------------------------------------------- */

typedef struct
{
	float *vertices;
	Uint32 *indices;
	int vertex_count, index_count, vertex_room, index_room;
	unsigned int generation;
	bool stale;
} Chunk;

static Chunk chunks[D3_CHUNKS];

static void room_for(Chunk *c, int vertices, int indices)
{
	if (c->vertex_count + vertices > c->vertex_room)
	{
		c->vertex_room = SDL_max(c->vertex_room * 2, c->vertex_count + vertices + 4096);
		c->vertices = realloc(c->vertices, sizeof(float) * 24 * (size_t)c->vertex_room);
	}
	if (c->index_count + indices > c->index_room)
	{
		c->index_room = SDL_max(c->index_room * 2, c->index_count + indices + 8192);
		c->indices = realloc(c->indices, sizeof(Uint32) * (size_t)c->index_room);
	}
}

// The earth's colour (linear) at a point of the ridge, by its facing: layers in the cut face, darker
// down it and back in a bowl; dry topsoil on what faces up.
static void earth_colour(float x, float y, float z, const float n[3], float out[3])
{
	static const float layers[][3] = {
		{ 112, 74, 44 }, { 128, 86, 50 }, { 146, 100, 58 }, { 120, 80, 46 }, { 150, 106, 62 },
		{ 132, 90, 52 }, { 116, 76, 44 }, { 140, 98, 58 },
	};
	const int n_layers = (int)(sizeof(layers) / sizeof(layers[0]));
	const float wobble = 3.0f * sinf(x * 0.031f) + 2.0f * sinf(x * 0.077f + 1.3f) + 1.2f * sinf(x * 0.19f);
	const float t = (y + wobble) * 0.11f;
	const int k = (int)floorf(t);
	const float f = t - k;
	const float *a = layers[((k % n_layers) + n_layers) % n_layers], *b = layers[(((k + 1) % n_layers) + n_layers) % n_layers];
	const float blend = f < 0.75f ? 0.0f : (f - 0.75f) / 0.25f;  // (bands with soft edges)
	float face[3];
	for (int c = 0; c < 3; ++c)
		face[c] = a[c] + (b[c] - a[c]) * blend;
	static const float soil[3] = { 178, 138, 88 };
	const float up = SDL_clamp(n[1] * 1.6f - 0.5f, 0.0f, 1.0f);
	const float grain = 0.9f + 0.2f * hash_unit((Uint32)((int)floorf(x * 2) * 7919 + (int)floorf(y * 2) * 104729 + (int)floorf(z) * 15485863));
	// Down the face darker; back in a bowl darker still.
	const float down = 0.5f + 0.5f * SDL_clamp((y + 30.0f) / 190.0f, 0.0f, 1.0f);
	const float back = 1.0f - 0.55f * SDL_clamp(-z / CARVE_MAX, 0.0f, 1.0f) * (1.0f - up);
	for (int c = 0; c < 3; ++c)
	{
		const float srgb = (face[c] * down * (1 - up) + soil[c] * up) * grain * back;
		out[c] = srgb_linear(SDL_clamp(srgb, 0.0f, 255.0f));
	}
}

static void build_chunk(int c)
{
	Chunk *ch = &chunks[c];
	ch->vertex_count = ch->index_count = 0;
	const int gx0 = c * D3_CHUNK, gx1 = gx0 + D3_CHUNK;  // the points it owns
	const int cx0 = gx0 - 1;                             // its cells, and the one before (shared)
	const int ncx = gx1 - cx0, ncy = Y1 - Y0 + 2, ncs = D3_SLICES + 1;
	static int *cell_vertex = NULL;
	static int cell_room = 0;
	if (ncx * ncy * ncs > cell_room)
	{
		cell_room = ncx * ncy * ncs;
		cell_vertex = realloc(cell_vertex, sizeof(int) * (size_t)cell_room);
	}
#define CELL(cx, cy, cs) cell_vertex[(((cs) + 1) * ncy + ((cy) - (Y0 - 1))) * ncx + ((cx) - cx0)]

	// The cells the surface crosses: a vertex each, where it crosses their edges on average.
	static const int corner[8][3] = { { 0, 0, 0 }, { 1, 0, 0 }, { 0, 1, 0 }, { 1, 1, 0 }, { 0, 0, 1 }, { 1, 0, 1 }, { 0, 1, 1 }, { 1, 1, 1 } };
	static const int edge[12][2] = { { 0, 1 }, { 2, 3 }, { 4, 5 }, { 6, 7 }, { 0, 2 }, { 1, 3 }, { 4, 6 }, { 5, 7 }, { 0, 4 }, { 1, 5 }, { 2, 6 }, { 3, 7 } };
	for (int cs = -1; cs < D3_SLICES; ++cs)
		for (int cy = Y0 - 1; cy <= Y1; ++cy)
			for (int cx = cx0; cx < gx1; ++cx)
			{
				float d[8];
				int inside = 0;
				for (int k = 0; k < 8; ++k)
				{
					d[k] = density(cx + corner[k][0], cy + corner[k][1], cs + corner[k][2]);
					inside += d[k] >= 0.5f;
				}
				if (inside == 0 || inside == 8)
				{
					CELL(cx, cy, cs) = -1;
					continue;
				}
				float p[3] = { 0, 0, 0 };
				int crossings = 0;
				for (int e = 0; e < 12; ++e)
				{
					const int a = edge[e][0], b = edge[e][1];
					if ((d[a] >= 0.5f) == (d[b] >= 0.5f))
						continue;
					const float t = (0.5f - d[a]) / (d[b] - d[a]);
					for (int i = 0; i < 3; ++i)
						p[i] += corner[a][i] + (corner[b][i] - corner[a][i]) * t;
					++crossings;
				}
				for (int i = 0; i < 3; ++i)
					p[i] /= crossings;
				// The density's gradient in the cell, in the world's axes (y up, z towards the camera).
				const float gx = (d[1] + d[3] + d[5] + d[7] - d[0] - d[2] - d[4] - d[6]) / 4;
				const float gy = (d[2] + d[3] + d[6] + d[7] - d[0] - d[1] - d[4] - d[5]) / 4;
				const float gs = (d[4] + d[5] + d[6] + d[7] - d[0] - d[1] - d[2] - d[3]) / 4 / D3_SLICE;
				float n[3] = { -gx, gy, gs };  // (out of the dirt)
				const float length = sqrtf(n[0] * n[0] + n[1] * n[1] + n[2] * n[2]);
				for (int i = 0; i < 3; ++i)
					n[i] = length > 1e-6f ? n[i] / length : (i == 2 ? 1.0f : 0.0f);
				const float wx = cx - D3_PAD + 0.5f + p[0];
				const float wy = 199.5f - (cy + p[1]);
				const float wz = -(cs + p[2]) * D3_SLICE;
				room_for(ch, 1, 0);
				float *v = ch->vertices + ch->vertex_count * 24;
				v[0] = wx;
				v[1] = wy;
				v[2] = wz;
				v[3] = n[0];
				v[4] = n[1];
				v[5] = n[2];
				v[6] = wx / D3_W;
				v[7] = (199.5f - wy) / D3_H;
				v[8] = 1;
				v[9] = v[10] = 0;
				v[11] = 1;
				earth_colour(wx, wy, wz, n, v + 12);
				v[15] = 1;
				memset(v + 16, 0, 8 * sizeof(float));
				CELL(cx, cy, cs) = ch->vertex_count++;
			}

	// A quad for each edge the surface crosses, of the four cells round it.
	for (int s = -1; s <= S_LAST; ++s)
		for (int y = Y0; y <= Y1; ++y)
			for (int x = gx0; x < gx1; ++x)
			{
				const bool in = density(x, y, s) >= 0.5f;
				int quad[3][4];
				bool flip[3];
				int count = 0;
				if (s >= 0 && (density(x + 1, y, s) >= 0.5f) != in)
				{
					const int q[4] = { CELL(x, y - 1, s - 1), CELL(x, y, s - 1), CELL(x, y, s), CELL(x, y - 1, s) };
					memcpy(quad[count], q, sizeof(q));
					flip[count++] = in;
				}
				if (s >= 0 && (density(x, y + 1, s) >= 0.5f) != in)
				{
					const int q[4] = { CELL(x - 1, y, s - 1), CELL(x - 1, y, s), CELL(x, y, s), CELL(x, y, s - 1) };
					memcpy(quad[count], q, sizeof(q));
					flip[count++] = in;
				}
				if (s < S_LAST && (density(x, y, s + 1) >= 0.5f) != in)
				{
					const int q[4] = { CELL(x - 1, y - 1, s), CELL(x, y - 1, s), CELL(x, y, s), CELL(x - 1, y, s) };
					memcpy(quad[count], q, sizeof(q));
					flip[count++] = in;
				}
				for (int k = 0; k < count; ++k)
				{
					const int *q = quad[k];
					if (q[0] < 0 || q[1] < 0 || q[2] < 0 || q[3] < 0)
						continue;
					room_for(ch, 0, 6);
					Uint32 *o = ch->indices + ch->index_count;
					if (flip[k])
					{
						o[0] = q[0]; o[1] = q[2]; o[2] = q[1];
						o[3] = q[0]; o[4] = q[3]; o[5] = q[2];
					}
					else
					{
						o[0] = q[0]; o[1] = q[1]; o[2] = q[2];
						o[3] = q[0]; o[4] = q[2]; o[5] = q[3];
					}
					ch->index_count += 6;
				}
			}
#undef CELL
	ch->stale = false;
	++ch->generation;
}

unsigned int destruct3d_chunk(int c, D3Mesh *mesh)
{
	if (c < 0 || c >= D3_CHUNKS)
		return 0;
	Chunk *ch = &chunks[c];
	if (ch->stale)
		build_chunk(c);
	mesh->vertices = ch->vertices;
	mesh->vertex_count = ch->vertex_count;
	mesh->indices = ch->indices;
	mesh->index_count = ch->index_count;
	return ch->generation;
}

/* --- The land behind, the planet ------------------------------------------------------------- */

static float *land_vertices = NULL;
static Uint32 *land_indices = NULL;
static int land_vertex_count = 0, land_index_count = 0;
static unsigned int land_generation = 0;
static bool land_stale = true;

#define LAND_COLUMNS (GRID_W / 2 + 1)
static const float land_rows[] = { 0, 3, 7, 12, 18, 26, 36, 48, 62, 80, 102, 128, 160, 200, 250, 310, 380, 460, 560, 680, 820 };
#define LAND_ROWS ((int)(sizeof(land_rows) / sizeof(land_rows[0])))

static float land_height(int column, int row)
{
	const float x = column * 2.0f - D3_PAD;
	const float back = land_rows[row];
	const int gx = SDL_clamp(column * 2, 0, GRID_W - 1);
	// From the ridge's top at its end down to the hills behind, which roll and fall away.
	// (Always below the ridge: the battle stands out against the sky.)
	const float top = top_orig[gx];
	const float base = SDL_min(top - 26.0f, 26.0f + 12.0f * sinf(x * 0.013f + 0.4f) + 8.0f * sinf(x * 0.037f + 1.9f));
	// (Falling the faster the higher the ridge stands: cliffs behind its spires.)
	const float k = SDL_clamp(back / SDL_clamp((top - base) * 0.5f, 24.0f, 110.0f), 0.0f, 1.0f), ease = k * k * (3 - 2 * k);
	const float roll = (6.0f + back * 0.03f) * (sinf(x * 0.017f + back * 0.011f) * 0.6f + sinf(x * 0.041f - back * 0.023f) * 0.4f) * ease;
	const float noise = (hash_unit((Uint32)(column * 92821 + row * 68917)) - 0.5f) * 2.0f * SDL_clamp(back / 20.0f, 0.0f, 1.0f);
	return top - 0.6f + (base - top) * ease - back * 0.1f + roll + noise;
}

static void build_land(void)
{
	free(land_vertices);
	free(land_indices);
	land_vertex_count = LAND_COLUMNS * LAND_ROWS;
	land_vertices = calloc((size_t)land_vertex_count * 24, sizeof(float));
	land_index_count = (LAND_COLUMNS - 1) * (LAND_ROWS - 1) * 6;
	land_indices = malloc(sizeof(Uint32) * (size_t)land_index_count);
	const float z0 = (S_LAST - 1.5f) * D3_SLICE;  // (under the ridge's last slices)
	for (int r = 0; r < LAND_ROWS; ++r)
		for (int c = 0; c < LAND_COLUMNS; ++c)
		{
			float *v = land_vertices + (r * LAND_COLUMNS + c) * 24;
			const float x = c * 2.0f - D3_PAD + 0.5f, y = land_height(c, r), z = -(z0 + land_rows[r]);
			const float hx = land_height(SDL_min(c + 1, LAND_COLUMNS - 1), r) - land_height(SDL_max(c - 1, 0), r);
			const float hz = land_height(c, SDL_min(r + 1, LAND_ROWS - 1)) - land_height(c, SDL_max(r - 1, 0));
			const float dz = land_rows[SDL_min(r + 1, LAND_ROWS - 1)] - land_rows[SDL_max(r - 1, 0)];
			float n[3] = { -hx / 4.0f, 1.0f, dz > 0 ? hz / dz : 0.0f };  // (z goes back: -z)
			const float length = sqrtf(n[0] * n[0] + n[1] * n[1] + n[2] * n[2]);
			v[0] = x;
			v[1] = y;
			v[2] = z;
			v[3] = n[0] / length;
			v[4] = n[1] / length;
			v[5] = n[2] / length;
			v[6] = x / D3_W;
			v[7] = r / (float)LAND_ROWS;
			v[8] = 1;
			v[11] = 1;
			float colour[3];
			earth_colour(x, y, 0.0f, v + 3, colour);
			// Into the dark with the distance.
			const float k = 1.0f - 0.85f * SDL_clamp(land_rows[r] / 700.0f, 0.0f, 1.0f);
			for (int i = 0; i < 3; ++i)
				v[12 + i] = colour[i] * k;
			v[15] = 1;
		}
	int n = 0;
	for (int r = 0; r + 1 < LAND_ROWS; ++r)
		for (int c = 0; c + 1 < LAND_COLUMNS; ++c)
		{
			const Uint32 a = (Uint32)(r * LAND_COLUMNS + c), b = a + 1, d = a + LAND_COLUMNS, e = d + 1;
			land_indices[n++] = a;
			land_indices[n++] = d;
			land_indices[n++] = b;
			land_indices[n++] = b;
			land_indices[n++] = d;
			land_indices[n++] = e;
		}
	land_stale = false;
	++land_generation;
}

unsigned int destruct3d_back(D3Mesh *land)
{
	if (land_stale)
		build_land();
	land->vertices = land_vertices;
	land->vertex_count = land_vertex_count;
	land->indices = land_indices;
	land->index_count = land_index_count;
	return land_generation;
}

#define SPHERE_RINGS 32
#define SPHERE_SEGMENTS 64

void destruct3d_planet(const D3Camera *camera, D3Mesh *sphere, float centre[3], float *radius)
{
	static float vertices[(SPHERE_RINGS + 1) * (SPHERE_SEGMENTS + 1) * 24];
	static Uint32 indices[SPHERE_RINGS * SPHERE_SEGMENTS * 6];
	static bool made = false;
	if (!made)
	{
		for (int r = 0; r <= SPHERE_RINGS; ++r)
			for (int s = 0; s <= SPHERE_SEGMENTS; ++s)
			{
				const float theta = (float)M_PI * r / SPHERE_RINGS, phi = 2 * (float)M_PI * s / SPHERE_SEGMENTS;
				const float n[3] = { sinf(theta) * cosf(phi), cosf(theta), sinf(theta) * sinf(phi) };
				float *v = vertices + (r * (SPHERE_SEGMENTS + 1) + s) * 24;
				memcpy(v, n, sizeof(n));
				memcpy(v + 3, n, sizeof(n));
				v[6] = s / (float)SPHERE_SEGMENTS;
				v[7] = r / (float)SPHERE_RINGS;
				v[8] = -sinf(phi);
				v[10] = cosf(phi);
				v[11] = 1;
				v[12] = v[13] = v[14] = v[15] = 1;
			}
		int n = 0;
		for (int r = 0; r < SPHERE_RINGS; ++r)
			for (int s = 0; s < SPHERE_SEGMENTS; ++s)
			{
				const Uint32 a = (Uint32)(r * (SPHERE_SEGMENTS + 1) + s), b = a + 1, c = a + SPHERE_SEGMENTS + 1, d = c + 1;
				indices[n++] = a;
				indices[n++] = b;
				indices[n++] = c;
				indices[n++] = b;
				indices[n++] = d;
				indices[n++] = c;
			}
		made = true;
	}
	sphere->vertices = vertices;
	sphere->vertex_count = (SPHERE_RINGS + 1) * (SPHERE_SEGMENTS + 1);
	sphere->indices = indices;
	sphere->index_count = SPHERE_RINGS * SPHERE_SEGMENTS * 6;
	// Far away at the view's upper right, under the HUD.
	const float distance = 3000.0f, ndc[2] = { 0.56f, 0.42f };
	for (int i = 0; i < 3; ++i)
		centre[i] = camera->position[i] + camera->forward[i] * distance + camera->right[i] * ndc[0] * camera->tan_half[0] * distance +
		            camera->up[i] * ndc[1] * camera->tan_half[1] * distance;
	*radius = 0.2f * camera->tan_half[1] * distance;
}

/* --- Pictures: the sky, the planet, the field's fire ----------------------------------------- */

// Smooth value noise, 0-1.
static float value_noise(float x, float y, Uint32 seed)
{
	const int xi = (int)floorf(x), yi = (int)floorf(y);
	const float fx = x - xi, fy = y - yi;
	const float sx = fx * fx * (3 - 2 * fx), sy = fy * fy * (3 - 2 * fy);
#define V(i, j) hash_unit((Uint32)((xi + (i)) * 73856093) ^ (Uint32)((yi + (j)) * 19349663) ^ seed)
	const float a = V(0, 0) + (V(1, 0) - V(0, 0)) * sx;
	const float b = V(0, 1) + (V(1, 1) - V(0, 1)) * sx;
#undef V
	return a + (b - a) * sy;
}

static float fbm(float x, float y, Uint32 seed)
{
	float sum = 0, amplitude = 0.5f;
	for (int o = 0; o < 5; ++o)
	{
		sum += value_noise(x, y, seed + (Uint32)o * 1013) * amplitude;
		x *= 2.03f;
		y *= 2.03f;
		amplitude *= 0.5f;
	}
	return sum;
}

static Uint32 rgba(float r, float g, float b, float a)
{
	const Uint8 bytes[4] = { (Uint8)SDL_clamp(r, 0.0f, 255.0f), (Uint8)SDL_clamp(g, 0.0f, 255.0f), (Uint8)SDL_clamp(b, 0.0f, 255.0f),
	                         (Uint8)SDL_clamp(a, 0.0f, 255.0f) };
	Uint32 v;
	memcpy(&v, bytes, 4);
	return v;
}

#define SKY_W 1024
#define SKY_H 512

const Uint32 *destruct3d_sky(int *w, int *h)
{
	static Uint32 *sky = NULL;
	if (sky == NULL)
	{
		sky = malloc(sizeof(Uint32) * SKY_W * SKY_H);
		static float rgb[SKY_W * SKY_H * 3];
		for (int y = 0; y < SKY_H; ++y)
			for (int x = 0; x < SKY_W; ++x)
			{
				const float t = y / (float)(SKY_H - 1);  // 0 top, 1 the horizon
				float *c = rgb + (y * SKY_W + x) * 3;
				c[0] = 4 + 30 * t * t;
				c[1] = 4 + 10 * t * t;
				c[2] = 14 + 22 * t * t;
				// Faint nebulae.
				const float neb = fbm(x / 170.0f, y / 120.0f, 77);
				const float k = SDL_clamp((neb - 0.48f) * 2.6f, 0.0f, 1.0f);
				c[0] += 34 * k * k;
				c[1] += 14 * k * k;
				c[2] += 40 * k * k;
			}
		// Stars, a few bright with a soft glow.
		for (int i = 0; i < 1600; ++i)
		{
			const int x = (int)(hash_unit((Uint32)i * 3 + 1) * SKY_W), y = (int)(hash_unit((Uint32)i * 3 + 2) * SKY_H * 0.92f);
			const float b = powf(hash_unit((Uint32)i * 3 + 3), 3.0f);
			const float tint = hash_unit((Uint32)i * 7 + 5);
			const float col[3] = { 200 + 55 * tint, 210 + 30 * tint, 255 - 40 * tint };
			const int r = b > 0.6f ? 2 : 0;
			for (int dy = -r; dy <= r; ++dy)
				for (int dx = -r; dx <= r; ++dx)
				{
					const int xx = x + dx, yy = y + dy;
					if (xx < 0 || yy < 0 || xx >= SKY_W || yy >= SKY_H)
						continue;
					const float fall = (dx == 0 && dy == 0) ? 1.0f : 0.18f / (dx * dx + dy * dy);
					float *c = rgb + (yy * SKY_W + xx) * 3;
					for (int k = 0; k < 3; ++k)
						c[k] += col[k] * (0.15f + 0.85f * b) * fall;
				}
		}
		for (int i = 0; i < SKY_W * SKY_H; ++i)
			sky[i] = rgba(rgb[i * 3], rgb[i * 3 + 1], rgb[i * 3 + 2], 255);
	}
	*w = SKY_W;
	*h = SKY_H;
	return sky;
}

#define PLANET_W 512
#define PLANET_H 256

const Uint32 *destruct3d_planet_texture(int *w, int *h)
{
	static Uint32 *planet = NULL;
	if (planet == NULL)
	{
		planet = malloc(sizeof(Uint32) * PLANET_W * PLANET_H);
		for (int y = 0; y < PLANET_H; ++y)
			for (int x = 0; x < PLANET_W; ++x)
			{
				// (Wrapping in x: the noise over a circle.)
				const float a = x / (float)PLANET_W * 2 * (float)M_PI;
				const float u = 3.0f + cosf(a) * 2.2f, v = 3.0f + sinf(a) * 2.2f;
				const float bands = 0.5f + 0.5f * sinf(y * 0.09f + fbm(u, v + y * 0.02f, 9) * 6.0f);
				const float n = fbm(u * 1.8f + y * 0.01f, v * 1.8f, 31);
				const float t = SDL_clamp(0.55f * bands + 0.6f * n - 0.15f, 0.0f, 1.0f);
				planet[y * PLANET_W + x] = rgba(70 + 150 * t, 26 + 70 * t * t, 22 + 40 * t * t, 255);
			}
	}
	*w = PLANET_W;
	*h = PLANET_H;
	return planet;
}

static Uint32 glow[D3_W * D3_H];
static bool glow_any = false;
static unsigned int glow_generation = 0;

unsigned int destruct3d_glow(const Uint32 **out, bool *any)
{
	*out = glow;
	*any = glow_any;
	return glow_generation;
}

// The field's pixels on fire (the explosions' 241-255: dark red to bright yellow, fading) as light.
static void make_glow(void)
{
	static const Uint8 heat[15][3] = {
		{ 70, 6, 2 }, { 100, 10, 2 }, { 130, 16, 4 }, { 160, 24, 4 }, { 190, 34, 6 }, { 214, 48, 8 }, { 236, 66, 10 }, { 255, 88, 12 },
		{ 255, 112, 18 }, { 255, 140, 28 }, { 255, 168, 44 }, { 255, 196, 70 }, { 255, 220, 110 }, { 255, 236, 160 }, { 255, 248, 210 },
	};
	bool any = false;
	for (int i = 0; i < D3_W * D3_H; ++i)
	{
		const Uint8 p = field[i];
		if (p >= 241 && i >= D3_TOP * D3_W)
		{
			const Uint8 *c = heat[p - 241];
			glow[i] = rgba(c[0], c[1], c[2], 255);
			any = true;
		}
		else
			glow[i] = 0;
	}
	if (any || glow_any)
		++glow_generation;
	glow_any = any;
}

/* --- The state ---------------------------------------------------------------------------- */

// The land beside the field: from the field's edge columns' tops, rolling.
static void make_decor(const Uint8 *pixels)
{
	int left = D3_H - 1, right = D3_H - 1;
	for (int y = D3_TOP; y < D3_H; ++y)
		if (pixels[y * D3_W + 1] == PIXEL_DIRT)
		{
			left = y;
			break;
		}
	for (int y = D3_TOP; y < D3_H; ++y)
		if (pixels[y * D3_W + D3_W - 2] == PIXEL_DIRT)
		{
			right = y;
			break;
		}
	for (int gx = 0; gx < GRID_W; ++gx)
	{
		const int x = gx - D3_PAD;
		if (x >= 0 && x < D3_W)
		{
			decor_top[gx] = 0;
			continue;
		}
		const float d = x < 0 ? (float)-x : (float)(x - D3_W + 1);
		const float edge = x < 0 ? left : right;
		const float wave = 14.0f * sinf(x * 0.043f + 0.7f) + 8.0f * sinf(x * 0.11f + 2.1f);
		const float k = SDL_clamp(d / 40.0f, 0.0f, 1.0f);
		decor_top[gx] = SDL_clamp(edge * (1 - k) + (150.0f + wave) * k, 60.0f, 196.0f);
	}
}

static void mark_stale_all(void)
{
	for (int c = 0; c < D3_CHUNKS; ++c)
		chunks[c].stale = true;
	land_stale = true;
}

void destruct3d_new_field(const Uint8 *pixels, int pitch)
{
	for (int y = 0; y < D3_H; ++y)
		memcpy(field + y * D3_W, pixels + y * pitch, D3_W);
	make_decor(field);
	raw_from_field(field, raw_orig);
	memcpy(raw_now, raw_orig, sizeof(raw_now));
	smooth(raw_orig, orig);
	memcpy(occ, orig, sizeof(occ));
	carve_depths(raw_now);
	// Each column's top as made, for the land behind (smoothed along the ridge).
	static float tops[GRID_W];
	for (int gx = 0; gx < GRID_W; ++gx)
	{
		int y = Y0;
		while (y < Y1 && orig[at(gx, y)] < 0.5f)
			++y;
		tops[gx] = 200.0f - y;
	}
	for (int gx = 0; gx < GRID_W; ++gx)
	{
		float sum = 0;
		int n = 0;
		for (int k = -3; k <= 3; ++k)
			if (gx + k >= 0 && gx + k < GRID_W)
			{
				sum += tops[gx + k];
				++n;
			}
		top_orig[gx] = sum / n;
	}
	make_glow();
	++field_generation;
	mark_stale_all();
	shown.unit_count = shown.shot_count = shown.wall_count = shown.blast_count = 0;
	shown.aim[0] = shown.aim[1] = false;
}

void destruct3d_tick(const D3Tick *tick)
{
	shown = *tick;
	shown.field = field;
	shown.pitch = D3_W;
	// The field's dirt changed: its smoothed dirt and bowls again, the chunks where they changed made again.
	bool changed = false;
	static Uint8 dirt_was[D3_H * D3_W];
	for (int y = D3_TOP; y < D3_H; ++y)
	{
		const Uint8 *row = tick->field + y * tick->pitch;
		for (int x = 0; x < D3_W; ++x)
		{
			const Uint8 now = (Uint8)(pixel_dirt(row[x]) * 10);
			if (now != dirt_was[y * D3_W + x])
			{
				dirt_was[y * D3_W + x] = now;
				changed = true;
			}
		}
	}
	for (int y = 0; y < D3_H; ++y)
		memcpy(field + y * D3_W, tick->field + y * tick->pitch, D3_W);
	make_glow();
	if (!changed)
		return;
	static float occ_was[GRID_H * GRID_W], carve_was[GRID_H * GRID_W];
	memcpy(occ_was, occ, sizeof(occ));
	memcpy(carve_was, carve, sizeof(carve));
	raw_from_field(field, raw_now);
	smooth(raw_now, occ);
	carve_depths(raw_now);
	for (int c = 0; c < D3_CHUNKS; ++c)
	{
		// (A chunk's mesh reads the columns from the one before it to the one after it.)
		const int gx0 = SDL_max(c * D3_CHUNK - 2, 0), gx1 = SDL_min((c + 1) * D3_CHUNK + 2, GRID_W);
		for (int y = Y0; y <= Y1 && !chunks[c].stale; ++y)
			for (int gx = gx0; gx < gx1; ++gx)
			{
				const int i = at(gx, y);
				if (occ[i] != occ_was[i] || (orig[i] > 0 && carve[i] != carve_was[i]))
				{
					chunks[c].stale = true;
					break;
				}
			}
	}
}

void destruct3d_enter(void)
{
	active = true;
	// A field to show before the first battle's: rolling hills.
	static Uint8 pixels[D3_H * D3_W];
	memset(pixels, 0, sizeof(pixels));
	for (int x = 1; x < D3_W - 1; ++x)
	{
		const int top = (int)(150 + 18 * sinf(x * 0.028f) + 10 * sinf(x * 0.071f + 1.0f) + 6 * cosf(x * 0.13f));
		for (int y = top; y < D3_H; ++y)
			pixels[y * D3_W + x] = PIXEL_DIRT;
	}
	destruct3d_new_field(pixels, D3_W);
}

void destruct3d_leave(void)
{
	active = false;
}

bool destruct3d_active(void)
{
	return active;
}

const D3Tick *destruct3d_state(void)
{
	return &shown;
}

/* --- The camera ---------------------------------------------------------------------------- */

#define CAMERA_TILT 13.0f  // degrees down
#define CAMERA_FOV 30.0f   // vertical, degrees

void destruct3d_camera(float aspect, D3Camera *camera)
{
	const float theta = CAMERA_TILT * (float)M_PI / 180.0f, t = tanf(CAMERA_FOV * (float)M_PI / 360.0f);
	const float c = cosf(theta), s = sinf(theta);
	const float forward[3] = { 0, -s, -c };
	const float up[3] = { 0, c, -s };
	const float right[3] = { 1, 0, 0 };
	// What it frames on the game's plane: the field's width, from a little below its floor to a band
	// above its top for the HUD.
	const float want_w = D3_W + 12.0f, bottom = -22.0f, top = 200.0f - D3_TOP + 40.0f;
	const float want_h = top - bottom;
	const float distance = SDL_max(want_w / 2 / (t * aspect), want_h * c / 2 / t);
	const float target[3] = { D3_W / 2.0f, (top + bottom) / 2, -D3_PLANE };
	for (int i = 0; i < 3; ++i)
	{
		camera->position[i] = target[i] - forward[i] * distance;
		camera->right[i] = right[i];
		camera->up[i] = up[i];
		camera->forward[i] = forward[i];
	}
	float view[16] = { 0 };
	for (int i = 0; i < 3; ++i)
	{
		view[i * 4 + 0] = right[i];
		view[i * 4 + 1] = up[i];
		view[i * 4 + 2] = forward[i];
	}
	float dot_r = 0, dot_u = 0, dot_f = 0;
	for (int i = 0; i < 3; ++i)
	{
		dot_r += right[i] * camera->position[i];
		dot_u += up[i] * camera->position[i];
		dot_f += forward[i] * camera->position[i];
	}
	view[12] = -dot_r;
	view[13] = -dot_u;
	view[14] = -dot_f;
	view[15] = 1;
	const float near_plane = 4.0f, far_plane = 8000.0f;
	float projection[16] = { 0 };
	projection[0] = 1.0f / (t * aspect);
	projection[5] = 1.0f / t;
	projection[10] = far_plane / (far_plane - near_plane);
	projection[11] = 1.0f;
	projection[14] = -near_plane * far_plane / (far_plane - near_plane);
	for (int col = 0; col < 4; ++col)
		for (int row = 0; row < 4; ++row)
		{
			float sum = 0;
			for (int k = 0; k < 4; ++k)
				sum += projection[k * 4 + row] * view[col * 4 + k];
			camera->view_projection[col * 4 + row] = sum;
		}
	camera->tan_half[0] = t * aspect;
	camera->tan_half[1] = t;
	// The sky far away, a little larger than the view.
	const float far_away = 6000.0f, hw = t * aspect * far_away * 1.08f, hh = t * far_away * 1.08f;
	const float corner[4][2] = { { -1, 1 }, { 1, 1 }, { 1, -1 }, { -1, -1 } };
	for (int k = 0; k < 4; ++k)
		for (int i = 0; i < 3; ++i)
			camera->sky[k][i] = camera->position[i] + forward[i] * far_away + right[i] * corner[k][0] * hw + up[i] * corner[k][1] * hh;
}
