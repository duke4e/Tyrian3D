/*
 * Tyrian3D: background maps drawn directly in 3D.
 *
 * The original game draws only the background tiles that fit on its 320x200 screen. The tilted
 * 3D camera sees more of the world: further up the level, and beyond the screen's sides. So the
 * 3D view draws the background maps itself, as tiles, for whatever area the camera sees on each
 * background's plane. The game still draws its own backgrounds as well; inside the playfield the
 * captured layer is drawn on top of the tiles, which keeps effects such as water and blur exact.
 *
 * Every draw of a background is recorded with its scroll state (l3d_add_background), so the tiles
 * line up with the game's own drawing. Beside the map, columns generated from the map's own tiles
 * with wave function collapse continue it (cached in the user's directory), then the map
 * continues mirrored; it darkens away from the map. Past the map's top, the background's wrap
 * point (BKwrap) is followed.
 */
#ifndef BACKGROUND3D_H
#define BACKGROUND3D_H

#include "opentyr.h"

#include "layer3d.h"

#define B3D_TILE_W 24
#define B3D_TILE_H 28

// Tile atlas: the tiles of the three background maps, each in a cell with one pixel of padding
// (copies of its edge pixels) so that sampling at a tile's edge never reaches a neighbour.
#define B3D_SETS 3
#define B3D_TILES_PER_SET 72
#define B3D_CELL_W (B3D_TILE_W + 2)
#define B3D_CELL_H (B3D_TILE_H + 2)
#define B3D_ATLAS_COLUMNS 16
#define B3D_CELLS (B3D_SETS * B3D_TILES_PER_SET)
#define B3D_BLANK_CELL B3D_CELLS        // a tile of colour 0, for empty entries of background 1
#define B3D_ATLAS_CELLS (B3D_CELLS + 1)
#define B3D_ATLAS_W (B3D_ATLAS_COLUMNS * B3D_CELL_W)
#define B3D_ATLAS_H (((B3D_ATLAS_CELLS + B3D_ATLAS_COLUMNS - 1) / B3D_ATLAS_COLUMNS) * B3D_CELL_H)

// Increases whenever a level's background maps are loaded, so the atlas can be rebuilt.
extern unsigned int b3d_map_generation;

// Makes (or loads from the cache) the columns beside the maps just loaded, so that drawing them
// doesn't wait for it. Drawing would otherwise make them when first needed.
void b3d_prepare_sides(void);

// The tile set the maps just loaded use: the shapes file's letter, and for each background the
// shape number (1-based, in shapes<letter>.dat) of each of its tiles (JE_loadMap's mapSh).
void b3d_note_tileset(char letter, const Uint16 shape_numbers[3][128]);

// Dev tool (TYR3D_EXPORT_MAPS=<dir>): writes the maps just loaded as images in the levels'
// palette, in parts of at most 72 rows, with a JSON index naming every cell's tile; maps already
// written are skipped. For upscaling the tiles in context (tools/export_maps.sh).
void b3d_export_maps(const char *dir);

// Fills the atlas with palette indices and opacity (B3D_ATLAS_W x B3D_ATLAS_H). Colour 0 is
// transparent; under background 1 that shows the starfield or the black of the cleared screen,
// as in the game. `ground` marks the cells of background 1 and the blank cell: where a filter
// recolours colour 0 (b3d_tile_remap), their colour 0 is drawn as well.
void b3d_build_atlas(Uint8 *indices, Uint8 *opaque, Uint8 *ground);

// The HD tiles of the maps' tileset (tools/tiles_hd.py): how many times the original's size they
// are, 1 if there are none.
int b3d_hd_scale(void);
// The atlas at b3d_hd_scale() times the size: the same layout with every cell and border scaled,
// HD tiles where there are, the original's pixels enlarged where not.
void b3d_build_atlas_hd(Uint8 *indices, Uint8 *opaque, Uint8 *ground);

// Atlas cell position of a tile, in pixels (top-left of the tile itself, inside the padding).
static inline void b3d_cell_origin(int cell, int *x, int *y)
{
	*x = (cell % B3D_ATLAS_COLUMNS) * B3D_CELL_W + 1;
	*y = (cell / B3D_ATLAS_COLUMNS) * B3D_CELL_H + 1;
}

// Palette remap for a background's tiles that approximates how the game combines them with what
// is below (draw_background_2_blend) and recolours them afterwards (water, lava and ice filters):
// the hue and average brightness, without the detail, blur and waver those also add.
void b3d_tile_remap(const L3DBackground *background, Uint8 remap[256]);
// The same for the filters alone.
void b3d_effect_remap(const L3DBackground *background, Uint8 remap[256]);

// Beyond its sides the map continues mirrored, darkening by this factor per tile away from it.
#define B3D_BEYOND_FADE 0.88f

typedef struct
{
	Uint16 cell;        // atlas cell
	bool flipped;       // mirrored left to right (the map continuing beyond its sides)
	Sint8 fade;         // beyond the map: darkens across the tile, to the left (-1) or right (1)
	float x, z;         // top-left corner in game screen coordinates
	float brightness;   // at the tile's edge nearest the map (1 inside the map)
	int map_row, map_column;  // where in the map (columns beside it negative or past its width)
} B3DTile;

// Appends the tiles of a recorded background that overlap the rectangle [x0, x1] x [z0, z1]
// (game screen coordinates). With fill_empty, empty map entries get the blank cell (for
// background 1 under a filter that recolours colour 0). Returns the number of tiles written
// (at most capacity).
int b3d_collect_tiles(const L3DBackground *background, bool fill_empty, float x0, float z0, float x1, float z1,
                      B3DTile *tiles, int capacity);

typedef struct
{
	float x, z;   // a pixel, in game screen coordinates
	Uint8 color;  // palette index
} B3DStar;

// Appends the pixels of the frame's starfield that lie outside the playfield (inside it the game
// draws the stars itself) and inside the rectangle [x0, x1] x [z0, z1]. The game's stars cycle
// through a ring of 65536 pixels, 320 wide; the ring continues further up the screen, where the
// stars will come from, and repeats every 320 pixels beside it.
int b3d_collect_stars(const L3DFrame *frame, float x0, float z0, float x1, float z1,
                      B3DStar *stars, int capacity);

/*
 * Filtered backgrounds. Where the game filters the screen (lava, water, ice), the tiles cannot
 * reproduce the result: the filters blur and waver across tile edges. Those backgrounds are
 * composed on the CPU instead, for the area the camera sees, exactly as the game draws them, and
 * the game's filters are applied to the composite with their waver aligned to the game's screen.
 * Each pixel stays with the background that drew it, like the captured layers.
 */

// Marks the backgrounds that must be composed: those drawn before a filter, blended ones (they
// average each pixel with what is below, which tiles can't), and those drawn before them.
void b3d_composed_backgrounds(const L3DFrame *frame, bool composed[L3D_MAX_BACKGROUNDS]);

// Composes the marked backgrounds over the rectangle (x0, z0, w x h) in game screen coordinates:
// the screen's palette indices after the filters, and the background owning each pixel (0xff for
// none). Each composed background also keeps its whole drawing, unfiltered (images[i]; 0 where it
// drew nothing, except background 1, which draws everywhere), as the captured layers do: drawn at
// its own height, a background covered by a higher one must not have holes. shades[i] holds the
// darkening of the map's continuation beyond its sides (255 inside the map).
void b3d_compose(const L3DFrame *frame, const bool composed[L3D_MAX_BACKGROUNDS], int x0, int z0, int w, int h,
                 Uint8 *index, Uint8 *owner, Uint8 *const images[L3D_MAX_BACKGROUNDS],
                 Uint8 *const shades[L3D_MAX_BACKGROUNDS]);

// Clouds: whether a tile of background 2 or 3 (index within its set) is a cloud, shown as a soft
// cloud above the ground.
bool b3d_tile_is_cloud(int set, int tile);

// A blended background whose map is opaque all over (** ALE **'s blue grid over its trees): over a
// ground of terrain it tints the ground as the game's blend does (its hue; the brightness halfway
// between its own and the ground's) instead of being drawn. Its commonest hue (high nibble) and its
// average brightness (low nibble), or false when it isn't one.
bool b3d_tint_overlay(int set, Uint8 *hue, int *brightness);
// Whether a background's map is opaque all over (the same scan).
bool b3d_map_opaque(int set);
// A tile's pixels (24 x 28 palette indices, 0 transparent), and whether a set has cloud tiles.
const Uint8 *b3d_tile_pixels(int set, int tile);
bool b3d_set_has_clouds(int set);
// Clouds are shown as clouds (set by the renderer): blended backgrounds of clouds aren't composed.
extern bool b3d_clouds;
// The ground is terrain this frame (render_gpu.c): no background is composed then.
extern bool b3d_terrain_ground;
// Backgrounds 2 and 3 may be solids this frame (render_gpu.c: when there are models), and whether a
// background is one: it has terrain and is drawn over the ground's enemies, unfiltered.
extern bool b3d_solids;
bool b3d_solid_background(const L3DFrame *frame, const L3DBackground *b);
// Marks (1) the layer pixels (L3D_WIDTH x L3D_ROWS) that a background's cloud tiles cover.
void b3d_cloud_mask(const L3DBackground *b, Uint8 *mask);

// Water (polish): whether a tile is water (drawn almost only in saturated blues), the layer
// pixels (L3D_WIDTH x L3D_ROWS) that a background's water tiles cover, and the average colour of a
// set's water (false if it has none).
bool b3d_tile_is_water(int set, int tile);
bool b3d_tile_has_water(int set, int tile);  // water in good part, or a shore
// Whether a pixel (palette index) of a tile is water: in a water tile, the water's colours.
bool b3d_water_pixel(int set, int tile, Uint8 index);
void b3d_water_mask(const L3DBackground *b, Uint8 *mask);
bool b3d_water_color(int set, Uint8 rgb[3]);

// A map's name (the hash in TYR3D_EXPORT_MAPS's files and terrain assets).
Uint64 b3d_map_hash(int set);

/*
 * Terrain (polish): heights for a whole map, computed offline from its surfaces
 * (tools/terrain/make_terrain.py) and loaded with the map from assets/terrain/<map>.ter. Samples
 * every `sample` game pixels at the samples' corners, from the map's left generated column
 * (-side_columns) on; heights in game pixels above the background's plane (for the ground, where
 * its enemies stand). B3D_TERRAIN_HOLE marks samples with nothing there (black space, or what
 * backgrounds 2 and 3 leave clear): the surface ends at them in walls down to below the plane.
 */
#define B3D_TERRAIN_HOLE (-128)

typedef struct
{
	int width, height;   // samples
	int sample;          // game pixels between samples
	int side_columns;    // tile columns beside the map that the samples cover on each side
	bool holes;          // samples may be B3D_TERRAIN_HOLE (version 2: the stars show only through them)
	int hole_count;      // samples that are B3D_TERRAIN_HOLE
	int lowest, highest; // the lowest and highest heights of samples with ground there (0 or beyond)
	const Sint8 *heights;
} B3DTerrain;

// The terrain of a background's current map (1 = the ground), or NULL if it has none (or
// TYR3D_TERRAIN=0).
const B3DTerrain *b3d_terrain(int set);
/*
 * Vegetation (polish): palms, trees and grass of the ground map, found offline by their colour
 * (tools/terrain/make_vegetation.py, assets/terrain/<map>.veg), drawn as models on the terrain.
 * Positions in the exported map's pixels (the generated columns included), plants in order of y.
 */
enum { B3D_PALM, B3D_TREE, B3D_GRASS, B3D_PLANT_KINDS };

typedef struct
{
	Uint16 x, y;
	Uint8 kind;
	Uint8 size;   // eighths of a pixel
	Uint8 turn;   // 1/256 of a full turn
	Uint8 shade;  // 128 = as is
} B3DPlant;

typedef struct
{
	int count;
	int side_columns;
	Uint8 colors[B3D_PLANT_KINDS * 2][3];  // palm leaves, trunk; tree leaves, highlights; grass base, tips
	const B3DPlant *plants;
	const int *row_start;  // by map row (tile row), the first plant at or below it; rows + 1 entries
	int rows;
} B3DVegetation;

// The current ground map's vegetation, or NULL if it has none (or TYR3D_VEGETATION=0).
const B3DVegetation *b3d_vegetation(void);

/*
 * Erasures (tools/terrain/make_cleanground.py, assets/terrain/<map>.era): where a map has a ground
 * enemy's object or what is left of it painted into its tiles, its painted palms, and the objects'
 * tiles in the generated columns, the pixels to replace with the map's own pixels at an offset (the
 * ground round them). Positions in the exported map's pixels (the generated columns included), in
 * order of y; each at most a tile.
 */
typedef struct
{
	Uint16 x, y;
	Uint8 w, h;
	Sint16 dx, dy;
	const Uint8 *mask;  // w x h, 1: replace
} B3DErasure;

typedef struct
{
	int count;
	const B3DErasure *erasures;
} B3DErasures;

// The erasures of a background's current map, or NULL (none, or TYR3D_ERASE=0).
const B3DErasures *b3d_erasures(int set);

/*
 * Stand-ins (tools/terrain/make_cleanground.py, assets/terrain/<map>.std): where the clean-up erased
 * what the ground map painted of an object (what is left of it once destroyed, or the object itself), the
 * model of that painting, which the 3D view shows while no ground enemy of its looks covers its place
 * (tyrian2.c draw_standins). Positions in the exported map's pixels (the generated columns included).
 */
#define B3D_STANDIN_COVERS 8

typedef struct
{
	float x, y;
	char sheet;          // the look whose model stands in: its sheet's letter (as L3DObject.enemy_sheet)
	Uint16 sprite;       // and first sprite
	bool large;
	Uint8 mode;          // L3D_STANDIN_OWN or L3D_STANDIN_PLACEHOLDER
	Uint16 group;        // the stand-ins of one object (they stand and lean together)
	int cover_count;     // the looks that cover it: the enemy's own, its damaged and dead looks, what it
	char cover_sheet[B3D_STANDIN_COVERS];  // turns into when destroyed
	Uint16 cover_sprite[B3D_STANDIN_COVERS];
} B3DStandin;

typedef struct
{
	int count;
	const B3DStandin *standins;
} B3DStandins;

// The current ground map's stand-ins, or NULL (none, or TYR3D_ERASE=0).
const B3DStandins *b3d_standins(void);

// The atlas cell of a map's tile at a row and column (sides and mirroring as the tiles are
// collected), or -1 for an empty entry.
int b3d_map_cell(int set, int map_row, int map_column, bool *flipped);
// Where a screen point over a background lies in its exported map (TYR3D_EXPORT_MAPS's images:
// game pixels from the map's top left, the generated columns included); false off the map.
bool b3d_map_point(const L3DBackground *b, float x, float y, int *map_x, int *map_y);
// The other way: where a point of a background's exported map is on the screen now.
bool b3d_screen_point(const L3DBackground *b, float map_x, float map_y, float *x, float *y);

#endif /* BACKGROUND3D_H */
