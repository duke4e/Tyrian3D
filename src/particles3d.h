/*
 * Tyrian3D: particle effects for the 3D view (plan M7).
 *
 * The game's explosions keep their sprites; in the 3D view each also throws out particles: a
 * flash, sparks, smoke and, on the ground, debris that flies up and falls back. The particles
 * live in game screen coordinates with a height above the ground, drift with the explosions
 * (explodeMove) and are drawn as camera-facing quads by the renderer. They only show; they use
 * their own random numbers, so the game plays exactly the same.
 */
#ifndef PARTICLES3D_H
#define PARTICLES3D_H

#include "opentyr.h"

typedef enum
{
	P3D_GLOW,   // drawn additively: flashes, fire, sparks
	P3D_SMOKE,  // drawn blended
	P3D_KIND_COUNT
} P3DKind;

typedef struct
{
	float x, y, height;      // game screen coordinates; height above the ground
	float vx, vy, vheight;   // per frame
	float size, grow;        // diameter in game pixels, and its change per frame
	float age, life;         // frames
	float gravity, drag;     // height speed lost per frame; fraction of speed kept per frame
	Uint8 color[4];          // at birth (RGBA)
	Uint8 end_color[4];      // at death
	Uint8 kind;              // P3DKind
} P3DParticle;

#define P3D_MAX_PARTICLES 4096

extern P3DParticle p3d_particles[P3D_MAX_PARTICLES];
extern int p3d_particle_count;

// Called by JE_setupExplosion: x, y are the explosion sprite's top left corner, type its
// explosion type (see explosion_data).
void p3d_explosion(int x, int y, int type);

// Advances the particles by one game frame; drift is how far explosions move down the screen in
// it (explodeMove).
void p3d_update(int drift);

// Removes all particles (a new level, the 2D view).
void p3d_clear(void);

#endif /* PARTICLES3D_H */
