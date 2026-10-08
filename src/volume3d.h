/*
 * Tyrian3D: volumetric sprites.
 *
 * Turns a sprite into a mesh with real volume while keeping its exact pixels: the sprite's
 * silhouette is "inflated" into a rounded relief (height grows with the distance from the edge,
 * plus a little relief from brightness), and the top surface is textured with the sprite itself.
 * This gives every enemy and ship a 3D shape that takes light and shadow, before (or instead of)
 * a hand-made model.
 *
 * Meshes use the sprite sheet's layout as texture space: a sheet is decoded into one atlas of
 * 19x16 cells of 12x14 pixels, matching the sprite indices.
 */
#ifndef VOLUME3D_H
#define VOLUME3D_H

#include "opentyr.h"

#include "sprite.h"

#define V3D_CELL_W 12
#define V3D_CELL_H 14
#define V3D_COLUMNS 19
#define V3D_ROWS 16
#define V3D_ATLAS_W (V3D_COLUMNS * V3D_CELL_W)
#define V3D_ATLAS_H (V3D_ROWS * V3D_CELL_H)

// Vertex layout expected by the BTBH renderer (96 bytes).
typedef struct
{
	float position[3];
	float normal[3];
	float uv[2];
	float tangent[4];
	float color[4];
	float joints[4];
	float weights[4];
} V3DVertex;

// Worst case for a 2x2 sprite: a vertex per pixel corner and two triangles per pixel on top,
// plus a wall quad on each of a pixel's four edges.
#define V3D_PIXELS (2 * V3D_CELL_W * 2 * V3D_CELL_H)
#define V3D_MAX_VERTICES ((2 * V3D_CELL_W + 1) * (2 * V3D_CELL_H + 1) + V3D_PIXELS * 16)
#define V3D_MAX_INDICES (V3D_PIXELS * 6 + V3D_PIXELS * 24)

typedef enum
{
	V3D_STYLE_RAISED,  // ships and flying enemies: a rounded body
	V3D_STYLE_FLAT,    // ground objects, whose sprites include the ground around them
	V3D_STYLE_COUNT
} V3DStyle;

// Decodes every cell of a sheet into palette indices and coverage (V3D_ATLAS_W x V3D_ATLAS_H).
void v3d_decode_sheet(const Sprite2_array *sheet, Uint8 *indices, Uint8 *cover);

// Builds the mesh of sprite `index` (1-based; a 2x2 sprite also uses index+1, +19 and +20)
// from a decoded sheet. The mesh is centred on the sprite, in game pixels: X right, Z down the
// screen, Y up. Returns the number of indices (0 if the sprite is empty).
//
// The shading is baked into the vertex colours, for drawing unlit: diffuse light from the
// direction `light` (a unit vector towards the light) plus fill light, scaled so that faces
// pointing straight up keep exactly the sprite's colours. (Lit, the scene's ambient and specular
// terms would lift dark colours towards grey.)
// open_sides (V3D_OPEN_*): sides where another part of the same enemy continues the sprite.
int v3d_build_mesh(const Uint8 *sheet_indices, const Uint8 *sheet_cover, unsigned int index, bool large,
                   V3DStyle style, Uint8 open_sides, const float light[3], V3DVertex *vertices, int *vertex_count,
                   Uint32 *indices);

/*
 * HD volumes (polish): the same, from a sprite sheet upscaled 4x (tools/hd_sheets.py: RGBA, the
 * sheet's layout at 4x). The outline follows the upscale's alpha (vertices snapped to where it
 * crosses one half), the body is rounded and higher, and the top takes the upscale's detail.
 * Vertices every V3D_HD_STEP upscaled pixels.
 */
#define V3D_HD_SCALE 4
#define V3D_HD_STEP 2
#define V3D_HD_GRID_W (2 * V3D_CELL_W * V3D_HD_SCALE / V3D_HD_STEP)
#define V3D_HD_GRID_H (2 * V3D_CELL_H * V3D_HD_SCALE / V3D_HD_STEP)
#define V3D_HD_MAX_VERTICES ((V3D_HD_GRID_W + 1) * (V3D_HD_GRID_H + 1) + V3D_HD_GRID_W * V3D_HD_GRID_H * 8)
#define V3D_HD_MAX_INDICES (V3D_HD_GRID_W * V3D_HD_GRID_H * 6 + V3D_HD_GRID_W * V3D_HD_GRID_H * 12)

int v3d_build_hd_mesh(const Uint8 *rgba, int sheet_w, int sheet_h, unsigned int index, bool large, V3DStyle style,
                      Uint8 open_sides, const float light[3], V3DVertex *vertices, int *vertex_count, Uint32 *indices);

// Whether a sprite has pixels in an HD sheet (any alpha in its cells).
bool v3d_hd_has_sprite(const Uint8 *rgba, int sheet_w, int sheet_h, unsigned int index, bool large);

// A sprite sheet's name as TYR3D_EXTRACT and tools/hd_sheets.py give it (enemy_<letter>, coins,
// powerups, ships, shots...), or NULL.
const char *v3d_sheet_name(const Sprite2_array *sheet);

#define V3D_OPEN_TOP    1u
#define V3D_OPEN_RIGHT  2u
#define V3D_OPEN_BOTTOM 4u
#define V3D_OPEN_LEFT   8u

// Which pixels along a sprite's edges are covered: edges[0] top and [2] bottom (bit x), [1] right
// and [3] left (bit y). For joining the parts of an enemy made of several sprites.
void v3d_sprite_edges(const Sprite2_array *sheet, unsigned int index, bool large, Uint32 edges[4]);

#endif /* VOLUME3D_H */
