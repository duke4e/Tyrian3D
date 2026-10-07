/*
 * Tyrian3D: background maps drawn directly in 3D. See background3d.h.
 */
#include "background3d.h"

#include "varz.h"

#include <math.h>
#include <stddef.h>
#include <string.h>

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

void b3d_build_atlas(Uint8 *indices, Uint8 *opaque)
{
	memset(indices, 0, B3D_ATLAS_W * B3D_ATLAS_H);
	memset(opaque, 0, B3D_ATLAS_W * B3D_ATLAS_H);

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

void b3d_tile_remap(const L3DBackground *b, Uint8 remap[256])
{
	const int below = b->blend ? ground_brightness() : 0;
	for (int i = 0; i < 256; ++i)
	{
		Uint8 index = (Uint8)i;
		if (b->blend)
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

static int collect_row(const L3DBackground *b, const MapSet *m, Uint8 **row_entry, int row, int first_tile,
                       int last_tile, B3DTile *tiles, int count, int capacity)
{
	const intptr_t entry = ((intptr_t)row_entry - (intptr_t)m->map) / (intptr_t)sizeof(Uint8 *);
	if (entry < 0 || entry >= (intptr_t)m->width * m->rows)
		return count;  // past either end of the map

	Uint8 **const row_start = m->map + entry / m->width * m->width;
	const int first_column = (int)(entry % m->width);

	for (int t = first_tile; t <= last_tile && count < capacity; ++t)
	{
		// Beyond its sides the map continues mirrored.
		const int c = first_column + t;
		const int period = floor_div(c, m->width);
		const bool flipped = (period & 1) != 0;
		int column = c - period * m->width;
		if (flipped)
			column = m->width - 1 - column;

		const Uint8 *data = row_start[column];
		if (data == NULL)
			continue;
		const ptrdiff_t offset = data - m->first_tile;
		if (offset < 0 || offset % m->tile_stride != 0 || offset / m->tile_stride >= m->tile_count)
			continue;

		B3DTile *tile = &tiles[count++];
		tile->cell = (Uint16)((b->set - 1) * B3D_TILES_PER_SET + offset / m->tile_stride);
		tile->flipped = flipped;
		tile->x = (float)(b->x + t * B3D_TILE_W);
		tile->z = (float)(b->top_y + row * B3D_TILE_H);
		const int beyond = c < 0 ? -c : c >= m->width ? c - m->width + 1 : 0;
		tile->fade = c < 0 ? -1 : c >= m->width ? 1 : 0;
		tile->brightness = beyond > 1 ? powf(B3D_BEYOND_FADE, (float)(beyond - 1)) : 1.0f;
	}
	return count;
}

int b3d_collect_tiles(const L3DBackground *b, float x0, float z0, float x1, float z1,
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
		count = collect_row(b, &m, b->top_row + row * m.width, row, first_tile, last_tile, tiles, count, capacity);

	// Rows above are the ones the map will scroll to.
	const ptrdiff_t column_offset = b->top_row - b->position;
	Uint8 **position = b->position;
	for (int row = -1; row >= first_row; --row)
	{
		position = row_above(b, position, m.width);
		count = collect_row(b, &m, position + column_offset, row, first_tile, last_tile, tiles, count, capacity);
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
