/*
 * Tyrian3D: GPU presentation through the BTBH renderer (SDL_GPU: Metal / Vulkan).
 *
 * Two ways to present a frame:
 *  - 2D: the 8-bit 320x200 screen, palette-converted and scaled into the window (menus etc.).
 *  - 3D: the captured depth layers of the playfield as planes under a tilted perspective camera,
 *        with the HUD and in-playfield text drawn flat on top.
 */
#ifndef RENDER_GPU_H
#define RENDER_GPU_H

#include "opentyr.h"

#include "layer3d.h"

#include <SDL3/SDL.h>

typedef struct
{
	float tilt_degrees;   // camera tilt away from straight down
	float fov_degrees;    // vertical field of view
	float height_scale;   // multiplier for layer heights
} RGPUCamera;

extern RGPUCamera rgpu_camera;

// Applies the camera settings given in the environment (TYR3D_TILT, TYR3D_FOV,
// TYR3D_HEIGHT_SCALE, TYR3D_SUN) over the current ones.
void rgpu_apply_camera_overrides(void);

// Creates the GPU device and a hidden window. Exits on failure.
SDL_Window *rgpu_init(const char *title, int width, int height);
void rgpu_shutdown(void);

// dst is the 320x200 screen's rectangle in window coordinates.
void rgpu_present_2d(const SDL_Surface *screen, const SDL_Rect *dst);
// hud is the 8-bit screen holding the HUD; its playfield area is replaced by the 3D view.
void rgpu_present_3d(const SDL_Surface *hud, const L3DFrame *frame, const SDL_Rect *dst);
// The same frame again, `ticks` of the game's ticks later: what moves (the maps, objects with a
// velocity, particles) moved on at its speed. For the frames shown while the game waits for its
// next tick.
void rgpu_present_3d_ahead(const SDL_Surface *hud, const L3DFrame *frame, const SDL_Rect *dst, float ticks);

#endif /* RENDER_GPU_H */
