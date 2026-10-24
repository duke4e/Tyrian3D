/*
 * OpenTyrian: A modern cross-platform port of Tyrian
 * Copyright (C) 2007-2009  The OpenTyrian Development Team
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
 */
#ifndef VIDEO_H
#define VIDEO_H

#include "opentyr.h"

#include <SDL3/SDL.h>

#define vga_width 320
#define vga_height 200

typedef enum {
	SCALE_CENTER,
	SCALE_INTEGER,
	SCALE_ASPECT_8_5,
	SCALE_ASPECT_4_3,
	ScalingMode_MAX
} ScalingMode;

extern const char *const scaling_mode_names[ScalingMode_MAX];

extern int fullscreen_display; // -1 means windowed
extern ScalingMode scaling_mode;

extern SDL_Surface *VGAScreen, *VGAScreenSeg;
extern SDL_Surface *game_screen;
extern SDL_Surface *VGAScreen2;

// game_screen and VGAScreen2 have rows of memory above row 0. When the 3D view is active the
// game also draws into them (backgrounds and enemies above the top edge), since the tilted
// camera sees past the top of the original screen.
#define SCREEN_OVERSCAN_MAX 64
extern int screen_overscan_rows;

static inline bool surface_has_overscan(const SDL_Surface *surface)
{
	return surface == game_screen || surface == VGAScreen2;
}

// Topmost row that may be drawn to (0, or negative with overscan).
static inline int surface_top(const SDL_Surface *surface)
{
	return surface_has_overscan(surface) ? -screen_overscan_rows : 0;
}

// Lowest pixel address that may be drawn to.
static inline Uint8 *surface_pixels_ll(const SDL_Surface *surface)
{
	return (Uint8 *)surface->pixels + surface_top(surface) * surface->pitch;
}

extern SDL_Window *main_window;

void init_video(void);

void video_on_win_resize(void);
void reinit_fullscreen(int new_display);
void toggle_fullscreen(void);
bool init_scaler(unsigned int new_scaler);
bool set_scaling_mode_by_name(const char *name);

void deinit_video(void);

void JE_clr256(SDL_Surface *);
void JE_showVGA(void);
void JE_showVGA3D(void);
void video_backdrop_shade(const SDL_Surface *surface, int x1, int y1, int x2, int y2);  // JE_barShade darkened a box
// The store's illustration of the ship: begun before it is drawn, ended once it is; what goes on its
// box under the ship's model besides the box itself is drawn on video_showcase_backdrop (NULL if none).
void video_showcase_begin(void);
SDL_Surface *video_showcase_backdrop(void);
void video_showcase_end(void);
// The store's weapon simulator: begun each frame once its stars are drawn; the ship and the shots
// that have models are drawn as models instead of sprites (true: don't draw the sprite).
void video_sim_begin(void);
bool video_sim_shot(bool shots2, unsigned int sprite, int x, int y);
bool video_sim_ship(int x, int y);
// Tyrian3D: a level's start (on), as its panel fades in on black, until it plays (off). With the
// modern HUD the 3D view shows no panel, so the window stays black until the level's first frame.
void video_level_intro(bool on);
// Tyrian3D: waits for the game's next tick (the delay set with setDelay*), showing the last 3D
// frame again as often as the display refreshes, moved on in time (rgpu_present_3d_ahead).
void video_wait_tick_3d(void);
// Tyrian3D: whole window points per screen pixel, for the pointer's size.
int video_pointer_scale(void);

// Tyrian3D: switches between the 3D view and the original 2D screen.
void video_set_3d_enabled(bool enabled);

// Tyrian3D view controls (2D/3D toggle, camera). Returns true if the key was consumed.
bool video_handle_key(SDL_Scancode scancode);  // presents the captured 3D layers with the HUD from VGAScreenSeg

void mapScreenPointToWindow(Sint32 *inout_x, Sint32 *inout_y);
void mapWindowPointToScreen(Sint32 *inout_x, Sint32 *inout_y);
void scaleWindowDistanceToScreen(Sint32 *inout_x, Sint32 *inout_y);
// Window points per screen pixel as the screen is shown now (in the 3D view, the playfield's).
void video_window_points_per_pixel(float *x, float *y);
// A window point (points) as a game screen position as the screen is shown now (in the 3D view,
// on the player's plane), and back.
bool video_window_to_game(float wx, float wy, float *x, float *y);
bool video_game_to_window(float x, float y, float *wx, float *wy);

#endif /* VIDEO_H */
