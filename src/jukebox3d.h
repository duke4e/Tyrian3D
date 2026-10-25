/*
 * Tyrian3D: the jukebox's visuals. With the modern UI the jukebox (jukebox.c) shows a 3D scene that
 * plays with the music, as measured where it is made (musicviz.h), under its panel (ui.c
 * build_jukebox), instead of the original's starfield. Each frame jukebox3d_frame makes the scene of a
 * few shapes (boxes, bars, spheres, glows, rings, the ships' models) and render_gpu.c draws it
 * (present_jukebox_scene), the panel's glass showing it blurred.
 *
 * Its looks (jukebox3d_look, V in the jukebox; TYR3D_JUKEBOX_LOOK=<n> for a run):
 *   0 Orrery: the spectrum as a crown of bars on a ring round a planet, the chip's nine channels as
 *     moons that light up with their notes, the drums as shock waves and sparks.
 *   1 Warp: the ship flies on, drawing the spectrum as rings of a tunnel and the channels' notes as
 *     lanes of light along it (a piano roll), the drums flashing its rings.
 */
#ifndef JUKEBOX3D_H
#define JUKEBOX3D_H

#include "opentyr.h"

#include <SDL3/SDL.h>

#define J3D_LOOKS 2
#define J3D_MAX_ITEMS 8192
#define J3D_MAX_LIGHTS 24

typedef enum
{
	J3D_BOX,     // a unit cube about its middle
	J3D_BAR,     // the same, dark at its foot, full at its top (vertex colours)
	J3D_SPHERE,  // a unit sphere, textured (J3D_TEXTURE_PLANET) or not
	J3D_GLOW,    // a soft dot facing the camera (a unit quad)
	J3D_RING,    // a soft ring lying in the shape's XZ plane (a unit quad)
	J3D_DOT,     // a soft dot lying in the shape's XZ plane (a unit quad)
	J3D_MODEL,   // a model of models3d.h, its footprint 1
	J3D_SHAPES
} J3DShape;

typedef enum
{
	J3D_LIT,       // lit by the sun and the lights
	J3D_UNLIT,     // its colour as it is (brighter than 1: it glows)
	J3D_ADDITIVE,  // light added to what is behind it
} J3DLook;

typedef struct
{
	Uint8 shape, look;
	Uint8 textured;  // J3D_SPHERE: the planet's texture
	Sint16 model;    // J3D_MODEL: the model's index
	float m[16];     // where (column-major: the shape's unit size to the world)
	float color[4];  // linear RGB and alpha
} J3DItem;

typedef struct
{
	float view_projection[16], position[3], right[3], up[3];
	int item_count;
	const J3DItem *items;
	int light_count;
	float lights[J3D_MAX_LIGHTS][8];   // x, y, z, radius, red, green, blue, energy
	float sun[3], sun_color[3], sun_energy;
	float ambient[3], ambient_energy;
	float bloom, bloom_threshold;
	float exposure;
	float metalness, roughness;        // the lit shapes'
} J3DScene;

// The frame's scene, for a window w x h (points); the panel shown or hidden (the scene's middle then
// higher, or in the window's middle).
const J3DScene *jukebox3d_frame(float w, float h, bool panel_shown);

// The look shown, and the next one (V).
int jukebox3d_look(void);
void jukebox3d_next_look(void);
const char *jukebox3d_look_name(int look);

// The shapes' meshes as the renderer takes them (vertices of 24 floats: position, normal, uv,
// tangent, colour, joints, weights), and the planet's texture (RGBA, sRGB), for J3D_BOX, J3D_BAR,
// J3D_SPHERE (the quads are the renderer's own).
void jukebox3d_mesh(J3DShape shape, const float **vertices, int *vertex_count, const Uint32 **indices, int *index_count);
const Uint32 *jukebox3d_planet_texture(int *w, int *h);

#endif /* JUKEBOX3D_H */
