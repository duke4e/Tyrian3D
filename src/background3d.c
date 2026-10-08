/*
 * Tyrian3D: background maps drawn directly in 3D. See background3d.h.
 */
#include "background3d.h"

#include "config.h"
#include "palette.h"
#include "paths3d.h"
#include "pcxmast.h"
#include "varz.h"
#include "wfc.h"

#include <btbh_gpu/btbh_gpu.h>

#include <math.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <zlib.h>

unsigned int b3d_map_generation = 0;

typedef struct
{
	Uint8 **map;              // first entry of the map
	int width, rows;
	const Uint8 *first_tile;  // shapes[0].sh
	ptrdiff_t tile_stride;    // distance between consecutive tiles
	int tile_count;
} MapSet;

static MapSet map_set(int set)
{
	switch (set)
	{
	case 1:
		return (MapSet){ &megaData1.mainmap[0][0], 14, 300, megaData1.shapes[0].sh,
		                 sizeof(megaData1.shapes[0]), COUNTOF(megaData1.shapes) };
	case 2:
		return (MapSet){ &megaData2.mainmap[0][0], 14, 600, megaData2.shapes[0].sh,
		                 sizeof(megaData2.shapes[0]), COUNTOF(megaData2.shapes) };
	default:
		return (MapSet){ &megaData3.mainmap[0][0], 15, 600, megaData3.shapes[0].sh,
		                 sizeof(megaData3.shapes[0]), COUNTOF(megaData3.shapes) };
	}
}

_Static_assert(COUNTOF(megaData1.shapes) <= B3D_TILES_PER_SET, "atlas cells per map");

void b3d_build_atlas(Uint8 *indices, Uint8 *opaque, Uint8 *ground)
{
	memset(indices, 0, B3D_ATLAS_W * B3D_ATLAS_H);
	memset(opaque, 0, B3D_ATLAS_W * B3D_ATLAS_H);
	memset(ground, 0, B3D_ATLAS_W * B3D_ATLAS_H);

	// The blank cell: colour 0 everywhere.
	int bx, by;
	b3d_cell_origin(B3D_BLANK_CELL, &bx, &by);
	for (int y = -1; y <= B3D_TILE_H; ++y)
		memset(ground + (by + y) * B3D_ATLAS_W + bx - 1, 1, B3D_CELL_W);

	for (int set = 1; set <= B3D_SETS; ++set)
	{
		const MapSet m = map_set(set);
		for (int k = 0; k < m.tile_count; ++k)
		{
			const Uint8 *tile = m.first_tile + k * m.tile_stride;
			int ox, oy;
			b3d_cell_origin((set - 1) * B3D_TILES_PER_SET + k, &ox, &oy);

			// The tile and a border that repeats its edge pixels.
			for (int y = -1; y <= B3D_TILE_H; ++y)
				for (int x = -1; x <= B3D_TILE_W; ++x)
				{
					const Uint8 index = tile[SDL_clamp(y, 0, B3D_TILE_H - 1) * B3D_TILE_W + SDL_clamp(x, 0, B3D_TILE_W - 1)];
					const int i = (oy + y) * B3D_ATLAS_W + ox + x;
					indices[i] = index;
					opaque[i] = index != 0;
					ground[i] = set == 1;
				}
		}
	}
}

// Average brightness (low nibble of the palette index) of background 1 over the level's map.
static int ground_brightness(void)
{
	static unsigned int generation = 0;
	static int brightness = 8;
	if (generation == b3d_map_generation)
		return brightness;
	generation = b3d_map_generation;

	const MapSet m = map_set(1);
	Uint32 tile_sum[B3D_TILES_PER_SET] = { 0 };
	for (int k = 0; k < m.tile_count; ++k)
		for (int p = 0; p < B3D_TILE_W * B3D_TILE_H; ++p)
			tile_sum[k] += m.first_tile[k * m.tile_stride + p] & 0x0f;

	Uint64 sum = 0, pixels = 0;
	for (int i = 0; i < m.width * m.rows; ++i)
	{
		const Uint8 *data = m.map[i];
		const ptrdiff_t offset = data != NULL ? data - m.first_tile : -1;
		if (offset < 0 || offset % m.tile_stride != 0 || offset / m.tile_stride >= m.tile_count)
			continue;
		sum += tile_sum[offset / m.tile_stride];
		pixels += B3D_TILE_W * B3D_TILE_H;
	}
	if (pixels > 0)
		brightness = (int)((sum + pixels / 2) / pixels);
	return brightness;
}

static void remap_colors(const L3DBackground *b, bool blend, Uint8 remap[256])
{
	const int below = blend ? ground_brightness() : 0;
	for (int i = 0; i < 256; ++i)
	{
		Uint8 index = (Uint8)i;
		if (blend)
			index = (index & 0xf0) | (((index & 0x0f) + below) / 2);
		for (int e = 0; e < b->effect_count; ++e)
		{
			switch (b->effects[e])
			{
			case L3D_EFFECT_LAVA:
				index = 0x70 | (index & 0x0f);
				break;
			case L3D_EFFECT_WATER:
				if ((index & 0x30) != 0)
					index = b->effect_params[e] | (index & 0x0f);
				break;
			case L3D_EFFECT_ICE:
				index = 0x80 | (index & 0x0f);
				break;
			}
		}
		remap[i] = index;
	}
}

void b3d_tile_remap(const L3DBackground *b, Uint8 remap[256])
{
	remap_colors(b, b->blend, remap);
}

void b3d_effect_remap(const L3DBackground *b, Uint8 remap[256])
{
	remap_colors(b, false, remap);
}

static int floor_div(int a, int b)
{
	return a / b - (a % b != 0 && (a < 0) != (b < 0));
}

// The scroll position one row further up the map, as the game will scroll to it: a looping map
// section continues at its wrap target (otherwise the map simply ends at its top).
static Uint8 **row_above(const L3DBackground *b, Uint8 **position, int width)
{
	position -= width;
	if (b->wrap_to > b->wrap && (intptr_t)position <= (intptr_t)b->wrap)
		position = b->wrap_to;
	return position;
}

/*
 * Beyond its sides the map continues with columns that wave function collapse (wfc.h) generates
 * from the map's own tiles: the tiles' neighbours in the map say which may stand next to which,
 * and the columns next to the map must fit its edge. They are made once per map, the same every
 * time (the seed comes from the map). Further out, and in bands of rows the solver could not
 * fill, the map continues mirrored.
 */
#define SIDE_COLUMNS 16
#define SIDE_BAND_ROWS 24
#define SIDE_MAX_ROWS 600
#define SIDE_MIRROR (-2)  // not generated: mirror the map

typedef struct
{
	unsigned int made_for;  // b3d_map_generation + 1, or 0
	Sint16 left[SIDE_MAX_ROWS][SIDE_COLUMNS];   // tile kind (see tile_kind); SIDE_MIRROR
	Sint16 right[SIDE_MAX_ROWS][SIDE_COLUMNS];
} MapSides;

static MapSides map_sides[B3D_SETS];

// A map entry as a tile kind for the solver: the tile's index, or tile_count for an empty entry.
static int tile_kind(const MapSet *m, const Uint8 *data)
{
	const ptrdiff_t offset = data != NULL ? data - m->first_tile : -1;
	if (offset >= 0 && offset % m->tile_stride == 0 && offset / m->tile_stride < m->tile_count)
		return (int)(offset / m->tile_stride);
	return m->tile_count;
}

// Solves one side in bands of rows, each bound to the map's edge and to the band above it.
// Returns how many bands the solver could not fill.
static int make_side(const WFCRules *rules, const int *edge, int rows, bool left_side, uint32_t seed,
                     Sint16 (*out)[SIDE_COLUMNS])
{
	int failed = 0;
	int band[SIDE_BAND_ROWS * SIDE_COLUMNS];
	int above[SIDE_COLUMNS];
	bool have_above = false;
	for (int r0 = 0; r0 < rows; r0 += SIDE_BAND_ROWS)
	{
		const int n = SDL_min(SIDE_BAND_ROWS, rows - r0);
		// A few seeds bound to the map's edge and the band above, then a few free of the band above,
		// then a few free of the edge (a seam is less visible than a mirrored band).
		bool solved = false;
		for (int attempt = 0; attempt < 24 && !solved; ++attempt)
		{
			const int *bound_edge = attempt < 16 ? edge + r0 : NULL;
			solved = wfc_solve(rules, n, SIDE_COLUMNS, left_side ? NULL : bound_edge, left_side ? bound_edge : NULL,
			                   have_above && (attempt < 8 || attempt >= 16) ? above : NULL,
			                   seed ^ (Uint32)(r0 * 2654435761u) ^ (Uint32)(attempt * 40503u), band);
		}
		for (int r = 0; r < n; ++r)
			for (int c = 0; c < SIDE_COLUMNS; ++c)
				out[r0 + r][c] = solved ? (Sint16)band[r * SIDE_COLUMNS + c] : SIDE_MIRROR;
		have_above = solved;
		if (solved)
			memcpy(above, band + (n - 1) * SIDE_COLUMNS, sizeof(above));
		else
			++failed;
	}
	return failed;
}

// Sides are kept in files named by a hash of the map and of what shapes the result: first in
// the game's assets (assets/sides, made ahead of time by tools/precompute_sides.sh), then in the
// user's directory, where sides made while playing go. TYR3D_SIDES_WRITE=<dir> writes new ones
// there instead (for precomputing). The files are zlib-compressed rows of Sint16 kinds, each row
// the left side's columns, then the right side's.
#define SIDE_CACHE_VERSION 5

static bool side_file_path(const char *dir, Uint64 hash, char *path, size_t size)
{
	if (dir == NULL)
		return false;
	snprintf(path, size, "%s/%016llx.bin", dir, (unsigned long long)hash);
	return true;
}

static const char *shipped_sides_dir(void)
{
	static char buffer[1024];
	return tyr3d_resource_dir("TYR3D_SIDES_DIR", TYR3D_SIDES_DIR, "sides", buffer, sizeof(buffer));
}

static const char *user_sides_dir(char *buffer, size_t size)
{
	const char *dir = SDL_getenv("TYR3D_SIDES_WRITE");
	if (dir != NULL)
		return dir;
	if (get_user_directory() == NULL)
		return NULL;
	snprintf(buffer, size, "%s/tyrian3d-sides", get_user_directory());
	return buffer;
}

static bool read_sides_file(const char *path, int rows, MapSides *sides)
{
	FILE *f = fopen(path, "rb");
	if (f == NULL)
		return false;
	static Uint8 packed[SIDE_MAX_ROWS * 2 * SIDE_COLUMNS * sizeof(Sint16) + 1024];
	static Sint16 data[SIDE_MAX_ROWS][2][SIDE_COLUMNS];
	const size_t packed_size = fread(packed, 1, sizeof(packed), f);
	fclose(f);
	uLongf size = (uLongf)(rows * sizeof(data[0]));
	if (uncompress((Bytef *)data, &size, packed, (uLong)packed_size) != Z_OK || size != rows * sizeof(data[0]))
		return false;
	for (int r = 0; r < rows; ++r)
	{
		memcpy(sides->left[r], data[r][0], sizeof(data[r][0]));
		memcpy(sides->right[r], data[r][1], sizeof(data[r][1]));
	}
	return true;
}

static bool load_sides(Uint64 hash, int rows, MapSides *sides)
{
	char path[1024], buffer[1024];
	return (side_file_path(shipped_sides_dir(), hash, path, sizeof(path)) && read_sides_file(path, rows, sides)) ||
	       (side_file_path(user_sides_dir(buffer, sizeof(buffer)), hash, path, sizeof(path)) &&
	        read_sides_file(path, rows, sides));
}

static void save_sides(Uint64 hash, int rows, const MapSides *sides)
{
	char path[1024], buffer[1024];
	const char *dir = user_sides_dir(buffer, sizeof(buffer));
	if (!side_file_path(dir, hash, path, sizeof(path)))
		return;
	SDL_CreateDirectory(dir);

	static Sint16 data[SIDE_MAX_ROWS][2][SIDE_COLUMNS];
	static Uint8 packed[SIDE_MAX_ROWS * 2 * SIDE_COLUMNS * sizeof(Sint16) + 1024];
	for (int r = 0; r < rows; ++r)
	{
		memcpy(data[r][0], sides->left[r], sizeof(data[r][0]));
		memcpy(data[r][1], sides->right[r], sizeof(data[r][1]));
	}
	uLongf packed_size = sizeof(packed);
	if (compress2(packed, &packed_size, (const Bytef *)data, (uLong)(rows * sizeof(data[0])), 9) != Z_OK)
		return;
	FILE *f = fopen(path, "wb");
	if (f == NULL)
		return;
	const bool ok = fwrite(packed, 1, packed_size, f) == packed_size;
	if (fclose(f) != 0 || !ok)
		remove(path);
}

static void mirror_sides(MapSides *sides)
{
	for (int r = 0; r < SIDE_MAX_ROWS; ++r)
		for (int c = 0; c < SIDE_COLUMNS; ++c)
			sides->left[r][c] = sides->right[r][c] = SIDE_MIRROR;
}

static void make_sides(int set, const MapSet *m, MapSides *sides)
{
	mirror_sides(sides);
	const char *mode = SDL_getenv("TYR3D_SIDES");  // "mirror": the old way, for comparison
	if (mode != NULL && SDL_strcmp(mode, "mirror") == 0)
		return;

	const int rows = SDL_min(m->rows, SIDE_MAX_ROWS);
	int *grid = malloc(sizeof(int) * rows * m->width);
	int *left_edge = malloc(sizeof(int) * rows), *right_edge = malloc(sizeof(int) * rows);
	WFCRules *rules = malloc(sizeof(WFCRules));
	if (grid != NULL && left_edge != NULL && right_edge != NULL && rules != NULL)
	{
		// FNV-1a of the map and of the settings, for the seed and the cache.
		Uint64 hash = 14695981039346656037ull;
		const int settings[] = { SIDE_CACHE_VERSION, SIDE_COLUMNS, SIDE_BAND_ROWS, m->tile_count, m->width, rows };
		for (size_t i = 0; i < COUNTOF(settings); ++i)
			hash = (hash ^ (Uint64)settings[i]) * 1099511628211ull;
		for (int r = 0; r < rows; ++r)
			for (int c = 0; c < m->width; ++c)
			{
				const int kind = tile_kind(m, m->map[r * m->width + c]);
				grid[r * m->width + c] = kind;
				hash = (hash ^ (Uint64)kind) * 1099511628211ull;
			}

		if (!load_sides(hash, rows, sides))
		{
			const Uint64 start = SDL_GetTicksNS();
			wfc_learn(rules, m->tile_count + 1, grid, rows, m->width);

			// The map's edge binds the columns beside it, unless a tile there never has a
			// neighbour on that side in the map (it is only ever at the edge): nothing could fit.
			for (int r = 0; r < rows; ++r)
			{
				const int left = grid[r * m->width], right = grid[r * m->width + m->width - 1];
				left_edge[r] = wfc_has_any(&rules->left[left]) ? left : -1;
				right_edge[r] = wfc_has_any(&rules->right[right]) ? right : -1;
			}
			const Uint32 seed = (Uint32)(hash ^ (hash >> 32));
			const int failed = make_side(rules, left_edge, rows, true, seed, sides->left) +
			                   make_side(rules, right_edge, rows, false, seed ^ 0x9e3779b9u, sides->right);
			printf("background %d: sides generated in %.0f ms (%d of %d bands mirrored)\n", set,
			       (SDL_GetTicksNS() - start) / 1e6, failed, 2 * ((rows + SIDE_BAND_ROWS - 1) / SIDE_BAND_ROWS));
			save_sides(hash, rows, sides);
		}
	}
	free(grid);
	free(left_edge);
	free(right_edge);
	free(rules);
}

static const MapSides *sides_for(int set, const MapSet *m)
{
	MapSides *sides = &map_sides[set - 1];
	if (sides->made_for != b3d_map_generation + 1)
	{
		sides->made_for = b3d_map_generation + 1;
		make_sides(set, m, sides);
	}
	return sides;
}

void b3d_prepare_sides(void)
{
	for (int set = 1; set <= B3D_SETS; ++set)
	{
		const MapSet m = map_set(set);
		sides_for(set, &m);
	}
}

static int collect_row(const L3DBackground *b, const MapSet *m, bool fill_empty, Uint8 **row_entry, int row,
                       int first_tile, int last_tile, B3DTile *tiles, int count, int capacity)
{
	const intptr_t entry = ((intptr_t)row_entry - (intptr_t)m->map) / (intptr_t)sizeof(Uint8 *);
	if (entry < 0 || entry >= (intptr_t)m->width * m->rows)
		return count;  // past either end of the map

	const int map_row = (int)(entry / m->width);
	Uint8 **const row_start = m->map + map_row * m->width;
	const int first_column = (int)(entry % m->width);
	const MapSides *sides = sides_for(b->set, m);

	for (int t = first_tile; t <= last_tile && count < capacity; ++t)
	{
		const int c = first_column + t;

		// Beside the map: the generated columns.
		int kind = SIDE_MIRROR;
		if (map_row < SIDE_MAX_ROWS && c < 0 && c >= -SIDE_COLUMNS)
			kind = sides->left[map_row][SIDE_COLUMNS + c];
		else if (map_row < SIDE_MAX_ROWS && c >= m->width && c < m->width + SIDE_COLUMNS)
			kind = sides->right[map_row][c - m->width];

		// Otherwise the map, continuing mirrored beyond its sides.
		bool flipped = false;
		if (kind == SIDE_MIRROR)
		{
			const int period = floor_div(c, m->width);
			flipped = (period & 1) != 0;
			int column = c - period * m->width;
			if (flipped)
				column = m->width - 1 - column;
			kind = tile_kind(m, row_start[column]);
		}

		int cell;
		if (kind < m->tile_count)
			cell = (b->set - 1) * B3D_TILES_PER_SET + kind;
		else if (fill_empty)
			cell = B3D_BLANK_CELL;
		else
			continue;

		B3DTile *tile = &tiles[count++];
		tile->cell = (Uint16)cell;
		tile->flipped = flipped;
		tile->x = (float)(b->x + t * B3D_TILE_W);
		tile->z = (float)(b->top_y + row * B3D_TILE_H);
		const int beyond = c < 0 ? -c : c >= m->width ? c - m->width + 1 : 0;
		tile->fade = c < 0 ? -1 : c >= m->width ? 1 : 0;
		tile->brightness = beyond > 1 ? powf(B3D_BEYOND_FADE, (float)(beyond - 1)) : 1.0f;
	}
	return count;
}

int b3d_collect_tiles(const L3DBackground *b, bool fill_empty, float x0, float z0, float x1, float z1,
                      B3DTile *tiles, int capacity)
{
	if (b->set < 1 || b->set > B3D_SETS)
		return 0;
	const MapSet m = map_set(b->set);

	// Rows and tiles relative to the topmost drawn row and its first tile.
	const int first_row = (int)floorf((z0 - b->top_y) / B3D_TILE_H);
	const int last_row = (int)floorf((z1 - b->top_y) / B3D_TILE_H);
	const int first_tile = (int)floorf((x0 - b->x) / B3D_TILE_W);
	const int last_tile = (int)floorf((x1 - b->x) / B3D_TILE_W);

	int count = 0;

	// The drawn rows and those below them follow each other in the map.
	for (int row = SDL_max(first_row, 0); row <= last_row; ++row)
		count = collect_row(b, &m, fill_empty, b->top_row + row * m.width, row, first_tile, last_tile, tiles, count, capacity);

	// Rows above are the ones the map will scroll to.
	const ptrdiff_t column_offset = b->top_row - b->position;
	Uint8 **position = b->position;
	for (int row = -1; row >= first_row; --row)
	{
		position = row_above(b, position, m.width);
		count = collect_row(b, &m, fill_empty, position + column_offset, row, first_tile, last_tile, tiles, count, capacity);
	}
	return count;
}

// Stars are drawn on rows above this one only.
#define STAR_ROWS 177
#define STAR_RING 65536

static int add_star_pixel(float x, float z, Uint8 color, B3DStar *stars, int count, int capacity)
{
	const bool in_playfield = x >= L3D_PLAYFIELD_X && x < L3D_PLAYFIELD_X + L3D_PLAYFIELD_W &&
	                          z >= 0 && z < L3D_PLAYFIELD_H;
	if (in_playfield || count == capacity)
		return count;
	stars[count].x = x;
	stars[count].z = z;
	stars[count].color = color;
	return count + 1;
}

int b3d_collect_stars(const L3DFrame *frame, float x0, float z0, float x1, float z1,
                      B3DStar *stars, int capacity)
{
	int count = 0;
	const int first_copy = (int)floorf((x0 - 1) / L3D_WIDTH), last_copy = (int)floorf((x1 + 1) / L3D_WIDTH);

	for (int s = 0; s < frame->star_count; ++s)
	{
		const L3DStar *star = &frame->stars[s];
		// The star, and where it was a whole ring ago and before: further up the screen.
		Sint32 position = star->position;
		for (int lap = 0; lap < 16; ++lap, position -= STAR_RING)
		{
			const int row = floor_div(position, L3D_WIDTH), column = position - row * L3D_WIDTH;
			if (row + 1 < z0)
				break;
			if (row >= STAR_ROWS || row - 1 > z1)
				continue;

			for (int copy = first_copy; copy <= last_copy; ++copy)
			{
				const float x = (float)(column + copy * L3D_WIDTH), z = (float)row;
				if (x + 1 < x0 || x - 1 > x1)
					continue;
				count = add_star_pixel(x, z, star->color, stars, count, capacity);
				if (star->bright)
				{
					const Uint8 dim = star->color - 4;
					count = add_star_pixel(x - 1, z, dim, stars, count, capacity);
					count = add_star_pixel(x + 1, z, dim, stars, count, capacity);
					count = add_star_pixel(x, z - 1, dim, stars, count, capacity);
					count = add_star_pixel(x, z + 1, dim, stars, count, capacity);
				}
			}
		}
	}
	return count;
}

/* --- Filtered backgrounds ------------------------------------------------------------------- */

bool b3d_clouds = false;

void b3d_composed_backgrounds(const L3DFrame *frame, bool composed[L3D_MAX_BACKGROUNDS])
{
	int last = -1;
	for (int i = 0; i < frame->background_count; ++i)
	{
		const L3DBackground *b = &frame->backgrounds[i];
		// A blended background of clouds isn't blended in the 3D view (its clouds are the canvas).
		const bool blended = b->blend && !(b3d_clouds && b3d_set_has_clouds(b->set));
		if (b->effect_count > 0 || blended)
			last = i;
	}
	for (int i = 0; i < frame->background_count; ++i)
		composed[i] = i <= last;
}

// Pixels of a tile in the game's tile data (NULL for the blank cell).
static const Uint8 *cell_pixels(int cell)
{
	if (cell < 0 || cell >= B3D_CELLS)
		return NULL;
	const MapSet m = map_set(cell / B3D_TILES_PER_SET + 1);
	const int k = cell % B3D_TILES_PER_SET;
	return k < m.tile_count ? m.first_tile + k * m.tile_stride : NULL;
}

// The waver of lava_filter and water_filter for a pixel of the game's screen: both step through
// the screen in groups of 8 pixels with a counter w = 320 * row + last column of the group.
static int filter_counter(int x, int z)
{
	return 320 * z + (x | 7);
}

// lava_filter: brightness averaged with the pixels above and below (the one below already
// filtered), all shifted right by a waver, in the lava's hue. The game reads the pixel above from
// the previous frame's screen; the unfiltered pixel stands in for it.
static void filter_lava(Uint8 *dst, const Uint8 *src, int x0, int z0, int w, int h)
{
	for (int y = h - 1; y >= 0; --y)
		for (int x = 0; x < w; ++x)
		{
			const int waver = abs(((filter_counter(x0 + x, z0 + y) >> 9) & 0x0f) - 8) - 1;
			const int xw = SDL_clamp(x + waver, 0, w - 1);
			const Uint8 here = src[y * w + xw] & 0x0f;
			const Uint8 below = y + 1 < h ? dst[(y + 1) * w + xw] & 0x0f : here;
			const Uint8 above = y > 0 ? src[(y - 1) * w + xw] & 0x0f : here;
			dst[y * w + x] = (Uint8)(((here * 2 + below + above) / 4) | 0x70);
		}
}

// water_filter: pixels of the water's hues take its hue, with their brightness averaged with the
// (filtered, wavered) pixel below.
static void filter_water(Uint8 *dst, const Uint8 *src, int x0, int z0, int w, int h, Uint8 hue)
{
	for (int y = h - 1; y >= 0; --y)
		for (int x = 0; x < w; ++x)
		{
			const Uint8 s = src[y * w + x];
			if ((s & 0x30) == 0)
			{
				dst[y * w + x] = s;
				continue;
			}
			const int waver = abs(((filter_counter(x0 + x, z0 + y) >> 10) & 0x07) - 4) - 1;
			const int xw = SDL_clamp(x + waver, 0, w - 1);
			const Uint8 below = y + 1 < h ? dst[(y + 1) * w + xw] : s;
			dst[y * w + x] = (Uint8)((((s & 0x0f) + (below & 0x0f)) / 2) | hue);
		}
}

void b3d_compose(const L3DFrame *frame, const bool composed[L3D_MAX_BACKGROUNDS], int x0, int z0, int w, int h,
                 Uint8 *index, Uint8 *owner, Uint8 *const images[L3D_MAX_BACKGROUNDS],
                 Uint8 *const shades[L3D_MAX_BACKGROUNDS])
{
	const size_t pixels = (size_t)w * h;
	memset(index, 0, pixels);
	memset(owner, 0xff, pixels);

	static B3DTile tiles[4096];
	static B3DStar stars[4096];
	static Uint8 *before = NULL;  // the composite before a filter
	static size_t before_size = 0;
	if (before_size < pixels)
	{
		free(before);
		before = malloc(pixels);
		before_size = before != NULL ? pixels : 0;
		if (before == NULL)
			return;
	}

	for (int i = 0; i < frame->background_count; ++i)
	{
		const L3DBackground *b = &frame->backgrounds[i];
		if (composed[i])
		{
			Uint8 *image = images[i], *shade = shades[i];
			memset(image, 0, pixels);
			memset(shade, 255, pixels);

			// Background 1 clears the screen first: every pixel is its.
			if (b->set == 1)
				memset(owner, i, pixels);

			const int count = b3d_collect_tiles(b, false, (float)x0, (float)z0, (float)(x0 + w - 1),
			                                    (float)(z0 + h - 1), tiles, (int)COUNTOF(tiles));
			for (int t = 0; t < count; ++t)
			{
				const B3DTile *tile = &tiles[t];
				const Uint8 *data = cell_pixels(tile->cell);
				if (data == NULL)
					continue;
				const int tx0 = (int)tile->x - x0, ty0 = (int)tile->z - z0;
				for (int ty = SDL_max(0, -ty0); ty < B3D_TILE_H && ty0 + ty < h; ++ty)
					for (int tx = SDL_max(0, -tx0); tx < B3D_TILE_W && tx0 + tx < w; ++tx)
					{
						const Uint8 value = data[ty * B3D_TILE_W + (tile->flipped ? B3D_TILE_W - 1 - tx : tx)];
						if (value == 0)
							continue;
						const size_t p = (size_t)(ty0 + ty) * w + tx0 + tx;
						index[p] = b->blend ? (Uint8)((value & 0xf0) | (((index[p] & 0x0f) + (value & 0x0f)) / 2)) : value;
						image[p] = index[p];
						owner[p] = (Uint8)i;
						// Darkening beyond the map, across the tile towards the side away from it.
						float s = tile->brightness;
						if (tile->fade != 0)
						{
							const float across = ((tile->fade > 0 ? tx : B3D_TILE_W - 1 - tx) + 0.5f) / B3D_TILE_W;
							s *= 1.0f + (B3D_BEYOND_FADE - 1.0f) * across;
						}
						shade[p] = (Uint8)(255.0f * s);
					}
			}

			// The starfield is drawn into background 1's black.
			if (b->set == 1 && frame->star_count > 0 && frame->star_layer == b->layer)
			{
				const int star_count = b3d_collect_stars(frame, (float)x0, (float)z0, (float)(x0 + w - 1),
				                                         (float)(z0 + h - 1), stars, (int)COUNTOF(stars));
				for (int s = 0; s < star_count; ++s)
				{
					const int x = (int)stars[s].x - x0, y = (int)stars[s].z - z0;
					if (x >= 0 && x < w && y >= 0 && y < h && index[(size_t)y * w + x] == 0)
						index[(size_t)y * w + x] = image[(size_t)y * w + x] = stars[s].color;
				}
			}
		}

		// Filters applied between this background and the next: the first entries of this
		// background's list that the next one doesn't have.
		const int later = i + 1 < frame->background_count ? frame->backgrounds[i + 1].effect_count : 0;
		for (int e = 0; e < b->effect_count - later; ++e)
		{
			memcpy(before, index, pixels);
			switch (b->effects[e])
			{
			case L3D_EFFECT_LAVA:
				filter_lava(index, before, x0, z0, w, h);
				break;
			case L3D_EFFECT_WATER:
				filter_water(index, before, x0, z0, w, h, b->effect_params[e]);
				break;
			case L3D_EFFECT_ICE:
				// iced_blur_filter also averages with the previous frame; that blur is left out.
				for (size_t p = 0; p < pixels; ++p)
					index[p] = 0x80 | (index[p] & 0x0f);
				break;
			}
		}
	}
}

static char tileset_letter;
static Uint16 tile_shapes[B3D_SETS][128];

void b3d_note_tileset(char letter, const Uint16 shape_numbers[3][128])
{
	tileset_letter = letter;
	memcpy(tile_shapes, shape_numbers, sizeof(tile_shapes));
}

#define EXPORT_PART_ROWS 72

void b3d_export_maps(const char *dir)
{
	SDL_CreateDirectory(dir);
	const SDL_Color *palette = palettes[pcxpal[3 - 1]];  // the levels' palette
	for (int set = 1; set <= B3D_SETS; ++set)
	{
		const MapSet m = map_set(set);

		// Name the map by its tiles' shape numbers.
		Uint64 hash = 14695981039346656037ull;
		hash = (hash ^ (Uint64)(unsigned char)tileset_letter) * 1099511628211ull;
		for (int i = 0; i < m.rows * m.width; ++i)
		{
			const int kind = tile_kind(&m, m.map[i]);
			const int shape = kind < m.tile_count ? tile_shapes[set - 1][kind] : 0;
			hash = (hash ^ (Uint64)shape) * 1099511628211ull;
		}
		char path[1024];
		snprintf(path, sizeof(path), "%s/map_%016llx.json", dir, (unsigned long long)hash);
		FILE *probe = fopen(path, "r");
		if (probe != NULL)
		{
			fclose(probe);
			continue;
		}

		const int width = m.width * B3D_TILE_W;
		static Uint8 rgba[EXPORT_PART_ROWS * B3D_TILE_H * 15 * B3D_TILE_W * 4];
		const int parts = (m.rows + EXPORT_PART_ROWS - 1) / EXPORT_PART_ROWS;
		for (int part = 0; part < parts; ++part)
		{
			const int first = part * EXPORT_PART_ROWS, rows = SDL_min(EXPORT_PART_ROWS, m.rows - first);
			memset(rgba, 0, sizeof(rgba));
			for (int r = 0; r < rows; ++r)
				for (int c = 0; c < m.width; ++c)
				{
					const Uint8 *data = m.map[(first + r) * m.width + c];
					if (tile_kind(&m, data) >= m.tile_count)
						continue;
					for (int y = 0; y < B3D_TILE_H; ++y)
						for (int x = 0; x < B3D_TILE_W; ++x)
						{
							const Uint8 index = data[y * B3D_TILE_W + x];
							Uint8 *out = &rgba[((r * B3D_TILE_H + y) * width + c * B3D_TILE_W + x) * 4];
							out[0] = palette[index].r;
							out[1] = palette[index].g;
							out[2] = palette[index].b;
							out[3] = index != 0 || set == 1 ? 255 : 0;  // colour 0 of backgrounds 2 and 3 is clear
						}
				}
			char image[1024];
			snprintf(image, sizeof(image), "%s/map_%016llx_%d.png", dir, (unsigned long long)hash, part + 1);
			btbh_gpu_write_png_rgba8(image, width, rows * B3D_TILE_H, rgba);
		}

		FILE *json = fopen(path, "w");
		if (json == NULL)
			continue;
		fprintf(json, "{\"background\": %d, \"tileset\": \"%c\", \"columns\": %d, \"rows\": %d, \"tile\": [%d, %d],\n",
		        set, SDL_tolower((unsigned char)tileset_letter), m.width, m.rows, B3D_TILE_W, B3D_TILE_H);
		fprintf(json, " \"parts\": [");
		for (int part = 0; part < parts; ++part)
			fprintf(json, "%s{\"file\": \"map_%016llx_%d.png\", \"first_row\": %d}", part ? ", " : "",
			        (unsigned long long)hash, part + 1, part * EXPORT_PART_ROWS);
		fprintf(json, "],\n \"shapes\": [");
		for (int r = 0; r < m.rows; ++r)
		{
			fprintf(json, "%s\n  [", r ? "," : "");
			for (int c = 0; c < m.width; ++c)
			{
				const int kind = tile_kind(&m, m.map[r * m.width + c]);
				fprintf(json, "%s%d", c ? "," : "", kind < m.tile_count ? tile_shapes[set - 1][kind] : 0);
			}
			fprintf(json, "]");
		}
		fprintf(json, "\n]}\n");
		fclose(json);
		printf("background %d: map written to %s\n", set, path);
	}
}

/*
 * Clouds. Tiles of backgrounds 2 and 3 that are light, soft colours with no dark outline (clouds,
 * mist) are shown as soft clouds above the ground instead of flat tiles (the renderer's cloud
 * canvas); the game blends background 2's clouds with what is below, the 3D view doesn't.
 */
static struct
{
	unsigned int made_for;  // b3d_map_generation + 1, or 0
	bool cloud[B3D_TILES_PER_SET];
} clouds[B3D_SETS];

static float saturation(const Uint8 c[3])
{
	const int hi = SDL_max(c[0], SDL_max(c[1], c[2])), lo = SDL_min(c[0], SDL_min(c[1], c[2]));
	return hi > 0 ? (float)(hi - lo) / hi : 0.0f;
}

static bool classify_cloud(const Uint8 *data)
{
	int opaque = 0, light = 0, dark = 0;
	float sat = 0;
	for (int p = 0; p < B3D_TILE_W * B3D_TILE_H; ++p)
	{
		if (data[p] == 0)
			continue;
		const Uint8 *c = (const Uint8 *)&rgb_palette[data[p]];
		const float lum = (0.299f * c[0] + 0.587f * c[1] + 0.114f * c[2]) / 255.0f;
		++opaque;
		light += lum > 0.5f;
		dark += lum < 0.12f;
		sat += saturation(c);
	}
	// Enough of the tile, mostly light, hardly any outline, soft colours.
	return opaque >= 40 && light * 10 >= opaque * 7 && dark * 25 <= opaque && sat / opaque < 0.45f;
}

bool b3d_tile_is_cloud(int set, int tile)
{
	if (set < 2 || set > B3D_SETS || tile < 0 || tile >= B3D_TILES_PER_SET)
		return false;
	if (clouds[set - 1].made_for != b3d_map_generation + 1)
	{
		// Tiles that clearly are clouds give the clouds' main colour ramp; tiles drawn in good part in
		// it are cloud too (the clouds' shaded parts, their edges).
		const MapSet m = map_set(set);
		int ramp_use[16] = { 0 }, ramp_total = 0;
		for (int t = 0; t < B3D_TILES_PER_SET; ++t)
		{
			const Uint8 *data = m.first_tile + t * m.tile_stride;
			clouds[set - 1].cloud[t] = t < m.tile_count && classify_cloud(data);
			if (!clouds[set - 1].cloud[t])
				continue;
			for (int p = 0; p < B3D_TILE_W * B3D_TILE_H; ++p)
				if (data[p] != 0)
				{
					++ramp_use[data[p] >> 4];
					++ramp_total;
				}
		}
		bool cloud_ramp[16];
		int main_ramp = 0;
		for (int r = 0; r < 16; ++r)
		{
			cloud_ramp[r] = ramp_total > 0 && ramp_use[r] * 33 >= ramp_total;  // 3 % of the clouds' pixels
			if (ramp_use[r] > ramp_use[main_ramp])
				main_ramp = r;
		}
		for (int t = 0; t < m.tile_count && t < B3D_TILES_PER_SET && ramp_total > 0; ++t)
		{
			if (clouds[set - 1].cloud[t])
				continue;
			const Uint8 *data = m.first_tile + t * m.tile_stride;
			int opaque = 0, in_ramps = 0, in_main = 0;
			for (int p = 0; p < B3D_TILE_W * B3D_TILE_H; ++p)
				if (data[p] != 0)
				{
					++opaque;
					in_ramps += cloud_ramp[data[p] >> 4];
					in_main += data[p] >> 4 == main_ramp;
				}
			// The clouds' shaded parts and edges mix in darker ramps (water, shadow): enough of the
			// clouds' main ramp makes a cloud.
			(void)in_ramps;
			clouds[set - 1].cloud[t] = opaque > 0 && in_main * 20 >= opaque * 7;
		}
		clouds[set - 1].made_for = b3d_map_generation + 1;
		if (SDL_getenv("TYR3D_LOG_CLOUDS") != NULL)
		{
			printf("clouds: set %d tiles", set);
			for (int t = 0; t < B3D_TILES_PER_SET; ++t)
				if (clouds[set - 1].cloud[t])
					printf(" %d", t);
			printf("\n");
		}
	}
	return clouds[set - 1].cloud[tile];
}

const Uint8 *b3d_tile_pixels(int set, int tile)
{
	return set >= 1 && set <= B3D_SETS && tile >= 0 && tile < B3D_TILES_PER_SET
		? cell_pixels((set - 1) * B3D_TILES_PER_SET + tile) : NULL;
}

bool b3d_set_has_clouds(int set)
{
	for (int t = 0; t < B3D_TILES_PER_SET; ++t)
		if (b3d_tile_is_cloud(set, t))
			return true;
	return false;
}

void b3d_cloud_mask(const L3DBackground *b, Uint8 *mask)
{
	static B3DTile tiles[512];
	const int count = b3d_collect_tiles(b, false, 0.0f, (float)-L3D_OVERSCAN, (float)(L3D_WIDTH - 1),
	                                    (float)(L3D_ROWS - L3D_OVERSCAN - 1), tiles, (int)COUNTOF(tiles));
	for (int t = 0; t < count; ++t)
	{
		const B3DTile *tile = &tiles[t];
		if (tile->cell / B3D_TILES_PER_SET + 1 != b->set || !b3d_tile_is_cloud(b->set, tile->cell % B3D_TILES_PER_SET))
			continue;
		const Uint8 *data = cell_pixels(tile->cell);
		for (int y = 0; y < B3D_TILE_H; ++y)
		{
			const int row = (int)tile->z + y + L3D_OVERSCAN;
			if (row < 0 || row >= L3D_ROWS)
				continue;
			for (int x = 0; x < B3D_TILE_W; ++x)
			{
				const int column = (int)tile->x + x;
				if (column >= 0 && column < L3D_WIDTH && data[y * B3D_TILE_W + (tile->flipped ? B3D_TILE_W - 1 - x : x)] != 0)
					mask[row * L3D_WIDTH + column] = 1;
			}
		}
	}
}

/*
 * Water (polish): tiles drawn almost only in saturated blue to cyan are water, which the renderer
 * shows as procedural water (the fork's PIXEL_WATER surface).
 */
static struct
{
	unsigned int made_for;  // b3d_map_generation + 1, or 0
	bool water[B3D_TILES_PER_SET];
} waters[B3D_SETS];

static bool water_pixel(Uint8 index)
{
	const Uint8 *c = (const Uint8 *)&rgb_palette[index];
	const int r = c[0], g = c[1], b = c[2];
	const int max = SDL_max(r, SDL_max(g, b)), min = SDL_min(r, SDL_min(g, b));
	if (max < 24 || b < r || (max - min) * 100 < max * 35)
		return false;
	const float hue = max == b ? 240.0f - 60.0f * (g - r) / (float)(max - min) : 180.0f - 60.0f * (b - r) / (float)(max - min);
	return hue >= 170.0f && hue <= 250.0f;
}

// In a water tile: whether a pixel is the water's (blues, the crests' and the sun's glare's pale
// colours, the darkest troughs) rather than land, sand or rock.
static bool water_like(Uint8 index)
{
	if (water_pixel(index))
		return true;
	// Cool colours (the crests', the glare's pale blue-greys) and the darkest troughs.
	const Uint8 *c = (const Uint8 *)&rgb_palette[index];
	const int brightest = SDL_max(c[0], SDL_max(c[1], c[2]));
	return (c[2] >= c[0] && c[2] + 8 >= c[1]) || brightest < 40;
}

bool b3d_water_pixel(int set, int tile, Uint8 index)
{
	return index != 0 && b3d_tile_is_water(set, tile) && water_like(index);
}

/*
 * Which levels have water, and in which background (assets/models/terrain.cfg: "water <set> <level
 * name or its beginning>"): colours alone can't tell water from blue metal or blue rock.
 */
static struct
{
	char name[16];
	int set;
} water_sets[64];
static int water_set_count = -1;

static void load_terrain_config(void)
{
	water_set_count = 0;
	char dir[1024], path[1200];
	snprintf(path, sizeof(path), "%s/terrain.cfg",
	         tyr3d_resource_dir("TYR3D_MODEL_DIR", TYR3D_MODEL_DIR, "models", dir, sizeof(dir)));
	FILE *f = fopen(path, "r");
	if (f == NULL)
		return;
	char line[256];
	while (fgets(line, sizeof(line), f) != NULL)
	{
		char name[16];
		int set;
		if (sscanf(line, " water %d %15[^\r\n]", &set, name) == 2 && water_set_count < (int)COUNTOF(water_sets))
		{
			SDL_strlcpy(water_sets[water_set_count].name, name, sizeof(water_sets[0].name));
			water_sets[water_set_count].set = set;
			++water_set_count;
		}
	}
	fclose(f);
}

static bool set_has_water(int set)
{
	if (water_set_count < 0)
		load_terrain_config();
	for (int i = 0; i < water_set_count; ++i)
		if (water_sets[i].set == set &&
		    SDL_strncasecmp(levelName, water_sets[i].name, SDL_strlen(water_sets[i].name)) == 0)
			return true;
	return false;
}

bool b3d_tile_is_water(int set, int tile)
{
	if (set < 1 || set > B3D_SETS || tile < 0 || tile >= B3D_TILES_PER_SET)
		return false;
	if (waters[set - 1].made_for != b3d_map_generation + 1)
	{
		const MapSet m = map_set(set);
		const bool water_set = set_has_water(set);
		for (int t = 0; t < B3D_TILES_PER_SET; ++t)
		{
			waters[set - 1].water[t] = false;
			if (!water_set || t >= m.tile_count)
				continue;
			const Uint8 *data = m.first_tile + t * m.tile_stride;
			int opaque = 0, water = 0, cool = 0;
			for (int p = 0; p < B3D_TILE_W * B3D_TILE_H; ++p)
				if (data[p] != 0)
				{
					++opaque;
					water += water_pixel(data[p]);
					cool += water_like(data[p]);
				}
			// Tiles with water in good part (shores too), or drawn all in the water's cool colours
			// (the sun's glare); their water pixels are water (b3d_water_pixel). Clouds are not water.
			waters[set - 1].water[t] = opaque > 0 && !b3d_tile_is_cloud(set, t) &&
			                           (water * 100 >= opaque * 40 || cool * 100 >= opaque * 90);
		}
		waters[set - 1].made_for = b3d_map_generation + 1;
	}
	return waters[set - 1].water[tile];
}

void b3d_water_mask(const L3DBackground *b, Uint8 *mask)
{
	static B3DTile tiles[512];
	const int count = b3d_collect_tiles(b, false, 0.0f, (float)-L3D_OVERSCAN, (float)(L3D_WIDTH - 1),
	                                    (float)(L3D_ROWS - L3D_OVERSCAN - 1), tiles, (int)COUNTOF(tiles));
	for (int t = 0; t < count; ++t)
	{
		const B3DTile *tile = &tiles[t];
		if (tile->cell / B3D_TILES_PER_SET + 1 != b->set || !b3d_tile_is_water(b->set, tile->cell % B3D_TILES_PER_SET))
			continue;
		const Uint8 *data = cell_pixels(tile->cell);
		for (int y = 0; y < B3D_TILE_H; ++y)
		{
			const int row = (int)tile->z + y + L3D_OVERSCAN;
			if (row < 0 || row >= L3D_ROWS)
				continue;
			for (int x = 0; x < B3D_TILE_W; ++x)
			{
				const int column = (int)tile->x + x;
				if (column >= 0 && column < L3D_WIDTH &&
				    water_like(data[y * B3D_TILE_W + (tile->flipped ? B3D_TILE_W - 1 - x : x)]) &&
				    data[y * B3D_TILE_W + (tile->flipped ? B3D_TILE_W - 1 - x : x)] != 0)
					mask[row * L3D_WIDTH + column] = 1;
			}
		}
	}
}

bool b3d_water_color(int set, Uint8 rgb[3])
{
	const MapSet m = map_set(set);
	double sum[3] = { 0, 0, 0 };
	long count = 0;
	for (int t = 0; t < m.tile_count && t < B3D_TILES_PER_SET; ++t)
	{
		if (!b3d_tile_is_water(set, t))
			continue;
		const Uint8 *data = m.first_tile + t * m.tile_stride;
		for (int p = 0; p < B3D_TILE_W * B3D_TILE_H; ++p)
			if (data[p] != 0 && water_pixel(data[p]))
			{
				const Uint8 *c = (const Uint8 *)&rgb_palette[data[p]];
				for (int k = 0; k < 3; ++k)
					sum[k] += c[k];
				++count;
			}
	}
	if (count == 0)
		return false;
	for (int k = 0; k < 3; ++k)
		rgb[k] = (Uint8)(sum[k] / count);
	return true;
}
