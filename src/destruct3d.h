/*
 * Tyrian3D: Destruct's battles in 3D. destruct.c hands over what it shows each tick; render_gpu.c
 * draws it (rgpu_present_ui, while Destruct's screen is published).
 *
 * The field is the game's own: its 320x200 picture of dirt (destructTempScreen), which every shot digs
 * into, stays the truth. It is seen as the cut face of a ridge: the game's plane, where the units
 * stand and the shots fly, just behind the face; the ground goes back behind it and falls away to the
 * land far behind. Where the game has dug the dirt away the face is dug back into the ground, in a
 * bowl as deep as the hole is wide (its distance to the dirt left); the field's pixels on fire glow in
 * the game's plane.
 *
 * World: x as the game's, y up (200 - the game's y), z towards the camera; game pixels. The face is
 * near z 0, the game's plane at z -D3_PLANE.
 */
#ifndef DESTRUCT3D_H
#define DESTRUCT3D_H

#include "opentyr.h"

#include <SDL3/SDL.h>

#define D3_W 320
#define D3_H 200
#define D3_TOP 12          // the field's first row (above it, the original's panel)
#define D3_PLANE 4.0f      // how far behind the face the game's plane is
#define D3_SLICE 2.0f      // the ridge's slices from the face back, game pixels apart
#define D3_SLICES 14
#define D3_PAD 96          // columns of land beside the field each side
#define D3_CHUNK 16        // columns of the ridge in a mesh
#define D3_CHUNKS ((D3_W + 2 * D3_PAD) / D3_CHUNK)

#define D3_MAX_UNITS 32
#define D3_MAX_SHOTS 64
#define D3_MAX_WALLS 32
#define D3_MAX_BLASTS 64

typedef struct
{
	int type;           // destruct.c's de_unit_t
	int side;           // 0 left, 1 right
	float x, y;         // the game's unitX (its sprite's left) and unitY (its bottom row)
	float angle;        // radians above the horizon, towards the other side
	int sprite;         // the sprite the game draws for it (1-based, the destruct sheet)
	bool selected;      // its side's unit chosen
	int frame;          // its animation's frame (0-3: a helicopter's rotor, a magnet pulsing)
	int last_move;      // a helicopter's way and speed (-5 left .. 5 right)
	float health;       // its armor left, 0-1
} D3Unit;

typedef struct
{
	float x, y, xmov, ymov;
	int type;           // de_shot_t
} D3Shot;

typedef struct
{
	int x, y;           // its sprite's top left
} D3Wall;

typedef struct
{
	int x, y, width, max, type;  // an explosion as the game spreads it (de_expl_t)
} D3Blast;

typedef struct
{
	const Uint8 *field;  // the field's pixels (palette indices), pitch D3_W... or as given
	int pitch;
	int unit_count, shot_count, wall_count, blast_count;
	D3Unit units[D3_MAX_UNITS];
	D3Shot shots[D3_MAX_SHOTS];
	D3Wall walls[D3_MAX_WALLS];
	D3Blast blasts[D3_MAX_BLASTS];
	bool aim[2];         // a side's crosshair, where the game draws it
	float aim_x[2], aim_y[2];
} D3Tick;

// Destruct starts and ends (its screens show the 3D view while it runs).
void destruct3d_enter(void);
void destruct3d_leave(void);
bool destruct3d_active(void);
// A new field, as the game has made it (before the battle on it).
void destruct3d_new_field(const Uint8 *pixels, int pitch);
// What a tick shows (field: as the game's temp screen holds it now).
void destruct3d_tick(const D3Tick *tick);

/* --- For drawing (render_gpu.c) --- */

// A mesh in the renderer's vertex layout: 24 floats a vertex (position, normal, uv, tangent, colour,
// joints, weights).
typedef struct
{
	const float *vertices;
	int vertex_count;
	const Uint32 *indices;
	int index_count;
} D3Mesh;

// The ridge's chunk c, made again when the field has changed there; returns its generation (it
// changes with the mesh).
unsigned int destruct3d_chunk(int c, D3Mesh *mesh);
// The land behind the ridge, and the far planet; their generation.
unsigned int destruct3d_back(D3Mesh *land);
// The field's pixels on fire as RGBA (D3_W x D3_H, clear elsewhere) and whether any is; its generation.
unsigned int destruct3d_glow(const Uint32 **rgba, bool *any);
// The sky's picture (RGBA) and the planet's.
const Uint32 *destruct3d_sky(int *w, int *h);
const Uint32 *destruct3d_planet_texture(int *w, int *h);

typedef struct
{
	float view_projection[16];  // column-major
	float position[3], right[3], up[3], forward[3];
	float sky[4][3];            // the sky's corners far away: top left, top right, bottom right, bottom left
	float tan_half[2];          // the view's half width and height at a distance of 1
} D3Camera;

// The view for a window of that aspect: the field fills it (wide windows show the land beside it).
void destruct3d_camera(float aspect, D3Camera *camera);
// The far planet (a sphere of radius 1) where the view shows it, how large.
void destruct3d_planet(const D3Camera *camera, D3Mesh *sphere, float centre[3], float *radius);
// The tick shown last.
const D3Tick *destruct3d_state(void);

// The battle's effects: fire, sparks, smoke and dirt thrown by the explosions, the shots' trails and
// their muzzles' flashes, smoke from what is destroyed. World coordinates (game pixels).
typedef enum
{
	D3P_SMOKE,   // blended, billowing
	D3P_DEBRIS,  // blended: clods of dirt, falling
	D3P_FIRE,    // additive, billowing
	D3P_GLOW,    // additive: flashes, sparks, the trails
	D3P_RING,    // additive: a big explosion's shock wave
	D3P_KINDS
} D3ParticleKind;

typedef struct
{
	float x, y, z, vx, vy, vz;  // per tick
	float size, grow;           // across, and its change a tick
	float age, life;            // ticks
	float gravity, drag;        // y speed lost a tick; the speed kept a tick
	float colour[4], end_colour[4];  // linear RGB (may be over 1 for light) and opacity
	Uint8 kind;
} D3Particle;

#define D3_MAX_PARTICLES 3072

int destruct3d_particles(const D3Particle **particles);

#endif /* DESTRUCT3D_H */
