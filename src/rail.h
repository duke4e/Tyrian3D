/*
 * Tyrian3D: a level flown as Star Fox 64 flies (docs/plans/2026-11-04-starfox.md). The ship goes on a rail into the
 * window, low over the level's own ground seen from behind it, and moves across the window and up and down; enemies
 * come at it out of the haze, fly past it or come up from behind; its lasers fire into the depth. It is a game of its
 * own (rail.c), not the level's 2D logic, and has no 2D view: the script's ]r[ before a level's ]L line has the level
 * loaded (its maps, their terrain, their plants) and then flown so, ending as the level would (rail_play).
 *
 * World: x across (0 the middle of the maps), y up (0 the ground's plane), z along the ground towards the camera (the
 * flight goes towards -z; z is the maps' pixel row, the level starting at their bottom); game pixels. Past the maps'
 * top they go on mirrored, end to end, as far as the flight goes; beside them, mirrored too.
 */
#ifndef RAIL_H
#define RAIL_H

#include "opentyr.h"

#include "destruct3d.h"

// The script's ]r[: the next level loaded is flown on the rail.
extern bool rail_next_level;

// Flies the level just loaded (JE_loadMap); whether the ship came through. The cash it earned is the player's, and
// the level's enemies killed and total (totalEnemy, enemyKilled) are the flight's.
bool rail_play(void);
// The flight is on (render_gpu.c draws it while the rail's screen is published).
bool rail_active(void);

/* --- For drawing (render_gpu.c present_rail) --- */

#define RAIL_CHUNK 1120   // the ground's chunks along z (40 map rows), chunk k from z = k * RAIL_CHUNK
#define RAIL_GROUND_X 2104.0f  // the ground's mesh goes this far to either side (the maps and their mirrors): its
                               // sides first in view where the haze has nearly hidden all (render_gpu.c present_rail)

// The ground of chunk k: its mesh (heights, normals, the texture's uv) and its texture (RGBA, w x h), made as the
// flight nears it; the generation it was made in (0: not made). Valid until the next call for another chunk.
unsigned int rail_ground_chunk(int k, D3Mesh *mesh, const Uint32 **rgba, int *w, int *h);

#define RAIL_MAX_OBJECTS 192
typedef struct
{
	int model;              // models.cfg's index
	float x, y, z;
	float yaw, pitch, roll; // degrees: yaw 0 its nose towards +z (as the enemies' models face down the screen)
	float scale;
	float flash;            // hit: drawn brighter (0-1)
	bool shadow;            // casts a shadow
} RailObject;

#define RAIL_MAX_GLOWS 640
typedef struct
{
	float x, y, z, size;
	float colour[3];        // linear, may be over 1
	Uint8 kind;             // RAIL_GLOW_*
} RailGlow;
enum { RAIL_GLOW_DOT, RAIL_GLOW_RING, RAIL_GLOW_KINDS };

#define RAIL_MAX_LIGHTS 8

#define RAIL_MAX_PLANTS 9000
typedef struct
{
	float x, y, z, size, turn, shade;
	Uint8 kind;             // B3D_PALM, B3D_TREE, B3D_GRASS
} RailPlant;

#define RAIL_MAX_SHADOWS 64
typedef struct
{
	float x, y, z, size, alpha;  // a soft dark patch on the ground under what flies (the ground is drawn unlit)
} RailShadow;

typedef struct
{
	float position[3], forward[3], up[3];  // the camera (up: rolled)
	float fov_degrees;
	float sun[3];                         // the way the sunlight goes
	float sky_top[3], sky_horizon[3];     // sRGB 0-1
	float haze[3];                        // sRGB 0-1: the far ground's
	float haze_near, haze_far;            // where the haze starts and where it hides all (thickening with the distance)
	int chunk_first, chunk_last;          // the ground's chunks in view
	int object_count;
	RailObject objects[RAIL_MAX_OBJECTS];
	int glow_count;
	RailGlow glows[RAIL_MAX_GLOWS];
	int light_count;
	float lights[RAIL_MAX_LIGHTS][8];     // x, y, z, radius, red, green, blue, energy (an explosion's flash)
	int plant_count;
	RailPlant plants[RAIL_MAX_PLANTS];
	int shadow_count;
	RailShadow shadows[RAIL_MAX_SHADOWS];
	float fade;                           // 0 black .. 1 shown
	float shadow_centre[3];               // the shadow's box: about the ship
} RailView;

const RailView *rail_view(void);
// The flight's effects (destruct3d's kinds of particles), world coordinates.
int rail_particles(const D3Particle **particles);

#endif /* RAIL_H */
