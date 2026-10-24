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
// The window black (nothing of the screen).
void rgpu_present_blank(void);
// Whether the 3D view shows the modern HUD (gauges over the scene) rather than the game's panel.
bool rgpu_modern_hud(void);
// hud is the 8-bit screen holding the HUD; its playfield area is replaced by the 3D view.
void rgpu_present_3d(const SDL_Surface *hud, const L3DFrame *frame, const SDL_Rect *dst);
// The same frame again, `ticks` of the game's ticks later: what moves (the maps, objects with a
// velocity, particles) moved on at its speed. For the frames shown while the game waits for its
// next tick.
void rgpu_present_3d_ahead(const SDL_Surface *hud, const L3DFrame *frame, const SDL_Rect *dst, float ticks);

// Window points per game pixel in the 3D view's playfield (at the player's height).
// A menu or message the game shows over the playfield in a level (pause, the in-game options, the
// level's end), over the 3D view's last frame: what differs from the screen as it was when that
// frame showed (backdrop) is drawn over it, the boxes the menu darkened (x1, y1, x2, y2, as
// JE_barShade takes them) darken it, fade (RGBA 0-1) goes over the whole window. *screen_rect:
// where the screen's pixels show in the window (the playfield's part of them as laid out), for the mouse.
void rgpu_present_3d_menu(const SDL_Surface *screen, const Uint8 *backdrop, const int (*shades)[4], int shade_count,
                          const float fade[4], const L3DFrame *frame, const SDL_Rect *dst, SDL_Rect *screen_rect);

// A box of the store's screen as a scene (the illustration of the ship, the weapon simulator): its
// picture without the ship (and shots) on the ground seen from straight above, models over it, the
// screen over everything but where it still shows the picture.
typedef struct
{
	int model;
	float x, y;    // screen pixels (on a parent: from its centre, as it is drawn unturned)
	float height;  // above the picture (on a parent: above its origin), screen pixels
	float size;    // footprint, screen pixels, centred on its bounds (0: its own size in screen pixels, at its origin)
	float yaw, pitch, roll;  // degrees
	int parent;    // an earlier object it rides on (turns with it), or -1
} RGPUShowcaseObject;

typedef struct
{
	SDL_Rect pane;             // the box (screen pixels)
	const Uint8 *backdrop;     // the screen with the box's picture under the models (SCREEN_W x SCREEN_H)
	const Uint8 *transparent;  // where the screen is as this, the scene shows
	const RGPUShowcaseObject *objects;
	int object_count;
	float fade[4];             // a colour over everything (RGBA 0-1)
} RGPUShowcase;

void rgpu_present_showcase(const SDL_Surface *screen, const RGPUShowcase *show, const SDL_Rect *dst);

float rgpu_playfield_scale(void);
// A window point (points) as a position on the player's plane in the view shown last, in game
// screen coordinates, and back. False before a 3D frame was shown (or above the horizon).
bool rgpu_window_to_playfield(float wx, float wy, float *x, float *y);
bool rgpu_playfield_to_window(float x, float y, float *wx, float *wy);

#endif /* RENDER_GPU_H */
