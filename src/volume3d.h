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
int v3d_build_mesh(const Uint8 *sheet_indices, const Uint8 *sheet_cover, unsigned int index, bool large,
                   V3DStyle style, const float light[3], V3DVertex *vertices, int *vertex_count, Uint32 *indices);

#endif /* VOLUME3D_H */
