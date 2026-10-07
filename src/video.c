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
#include "video.h"

#include "devtools.h"
#include "keyboard.h"
#include "opentyr.h"
#include "layer3d.h"
#include "models3d.h"
#include "palette.h"
#include "render_gpu.h"
#include "video_scale.h"

#include <assert.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

const char *const scaling_mode_names[ScalingMode_MAX] = {
	"Center",
	"Integer",
	"Fit 8:5",
	"Fit 4:3",
};

int fullscreen_display;
ScalingMode scaling_mode = SCALE_INTEGER;
static SDL_Rect last_output_rect = { 0, 0, vga_width, vga_height };

SDL_Surface *VGAScreen, *VGAScreenSeg;
SDL_Surface *VGAScreen2;
SDL_Surface *game_screen;

int screen_overscan_rows = 0;

static bool last_frame_was_3d = false;

SDL_Window *main_window = NULL;

static SDL_DisplayID display_id_from_index(int display_index);
static void window_center_in_display(SDL_DisplayID display);
static void calc_dst_render_rect(SDL_Rect *dst_rect);
static void present_screen(SDL_Surface *);

// A screen surface whose pixels are preceded by SCREEN_OVERSCAN_MAX rows of memory.
static SDL_Surface *create_overscan_screen_surface(void)
{
	Uint8 *buffer = calloc((size_t)vga_width * (vga_height + SCREEN_OVERSCAN_MAX), 1);
	SDL_Surface *surface = buffer != NULL
		? SDL_CreateSurfaceFrom(vga_width, vga_height, SDL_PIXELFORMAT_INDEX8, buffer + SCREEN_OVERSCAN_MAX * vga_width, vga_width)
		: NULL;
	if (surface == NULL)
	{
		fprintf(stderr, "error: failed to create screen surface: %s\n", SDL_GetError());
		exit(EXIT_FAILURE);
	}
	return surface;
}

static void destroy_overscan_screen_surface(SDL_Surface *surface)
{
	Uint8 *buffer = (Uint8 *)surface->pixels - SCREEN_OVERSCAN_MAX * surface->pitch;
	SDL_DestroySurface(surface);
	free(buffer);
}

static SDL_Surface *create_screen_surface(void)
{
	SDL_Surface *surface = SDL_CreateSurface(vga_width, vga_height, SDL_PIXELFORMAT_INDEX8);
	if (surface == NULL)
	{
		fprintf(stderr, "error: failed to create screen surface: %s\n", SDL_GetError());
		exit(EXIT_FAILURE);
	}
	return surface;
}

void init_video(void)
{
	if (SDL_WasInit(SDL_INIT_VIDEO))
		return;

	if (!SDL_InitSubSystem(SDL_INIT_VIDEO))
	{
		fprintf(stderr, "error: failed to initialize SDL video: %s\n", SDL_GetError());
		exit(1);
	}

	// Create the software surfaces that the game renders to. These are all 320x200x8 regardless
	// of the window size or monitor resolution.
	VGAScreen = VGAScreenSeg = create_screen_surface();
	VGAScreen2 = create_overscan_screen_surface();
	game_screen = create_overscan_screen_surface();
	screen_overscan_rows = l3d_enabled ? SCREEN_OVERSCAN_MAX : 0;

	// The game code writes to surface->pixels directly without locking, so make sure that we
	// indeed created software surfaces that support this.
	assert(!SDL_MUSTLOCK(VGAScreen));
	assert(!SDL_MUSTLOCK(VGAScreen2));
	assert(!SDL_MUSTLOCK(game_screen));

	JE_clr256(VGAScreen);

	main_window = rgpu_init(opentyrian_str, scalers[scaler].width, scalers[scaler].height);

	reinit_fullscreen(fullscreen_display);

	SDL_ShowWindow(main_window);

	JE_showVGA();
}

void deinit_video(void)
{
	rgpu_shutdown();  // destroys the window
	main_window = NULL;

	SDL_DestroySurface(VGAScreenSeg);
	destroy_overscan_screen_surface(VGAScreen2);
	destroy_overscan_screen_surface(game_screen);

	SDL_QuitSubSystem(SDL_INIT_VIDEO);
}

static SDL_DisplayID display_id_from_index(int display_index)
{
	int count = 0;
	SDL_DisplayID *displays = SDL_GetDisplays(&count);
	SDL_DisplayID id = 0;
	if (displays != NULL && count > 0)
		id = displays[(display_index >= 0 && display_index < count) ? display_index : 0];
	SDL_free(displays);
	return id;
}

static int display_index_from_id(SDL_DisplayID id)
{
	int count = 0;
	SDL_DisplayID *displays = SDL_GetDisplays(&count);
	int index = 0;
	for (int i = 0; displays != NULL && i < count; ++i)
		if (displays[i] == id)
			index = i;
	SDL_free(displays);
	return index;
}

static void window_center_in_display(SDL_DisplayID display)
{
	SDL_SetWindowPosition(main_window, SDL_WINDOWPOS_CENTERED_DISPLAY(display), SDL_WINDOWPOS_CENTERED_DISPLAY(display));
}

void reinit_fullscreen(int new_display)
{
	int count = 0;
	SDL_free(SDL_GetDisplays(&count));

	fullscreen_display = new_display;

	if (fullscreen_display >= count)
	{
		fullscreen_display = 0;
	}

	SDL_SetWindowFullscreen(main_window, false);
	SDL_SetWindowSize(main_window, scalers[scaler].width, scalers[scaler].height);

	if (fullscreen_display == -1)
	{
		window_center_in_display(SDL_GetDisplayForWindow(main_window));
	}
	else
	{
		window_center_in_display(display_id_from_index(fullscreen_display));

		SDL_SetWindowFullscreenMode(main_window, NULL); // borderless desktop fullscreen
		if (!SDL_SetWindowFullscreen(main_window, true))
		{
			reinit_fullscreen(-1);
			return;
		}
	}
}

void video_on_win_resize(void)
{
	int w, h;
	int scaler_w, scaler_h;

	// Enforce a minimum size on the window.

	SDL_GetWindowSize(main_window, &w, &h);
	scaler_w = vga_width;
	scaler_h = vga_height;

	if (w < scaler_w || h < scaler_h)
	{
		w = w < scaler_w ? scaler_w : w;
		h = h < scaler_h ? scaler_h : h;

		SDL_SetWindowSize(main_window, w, h);
	}
}

void toggle_fullscreen(void)
{
	if (fullscreen_display != -1)
		reinit_fullscreen(-1);
	else
		reinit_fullscreen(display_index_from_id(SDL_GetDisplayForWindow(main_window)));
}

bool init_scaler(unsigned int new_scaler)
{
	if (new_scaler >= scalers_count)
		return false;

	scaler = new_scaler;

	if (fullscreen_display == -1)
	{
		// Changing scalers, when not in fullscreen mode, forces the window
		// to resize to exactly match the scaler's output dimensions.
		SDL_SetWindowSize(main_window, scalers[scaler].width, scalers[scaler].height);
		window_center_in_display(SDL_GetDisplayForWindow(main_window));
	}

	return true;
}

bool set_scaling_mode_by_name(const char *name)
{
	for (int i = 0; i < ScalingMode_MAX; ++i)
	{
		 if (strcmp(name, scaling_mode_names[i]) == 0)
		 {
			 scaling_mode = i;
			 return true;
		 }
	}
	return false;
}

void JE_clr256(SDL_Surface *screen)
{
	SDL_FillSurfaceRect(screen, NULL, 0);
}

void JE_showVGA(void)
{
	present_screen(VGAScreen);
}

static void calc_dst_render_rect(SDL_Rect *const dst_rect)
{
	// Decides how the logical 320x200 output will fit in the window (in window coordinates).

	int win_w, win_h;
	SDL_GetWindowSize(main_window, &win_w, &win_h);

	int maxh_width, maxw_height;

	switch (scaling_mode)
	{
	case SCALE_CENTER:
		dst_rect->w = scalers[scaler].width;
		dst_rect->h = scalers[scaler].height;
		break;
	case SCALE_INTEGER:
		dst_rect->w = vga_width;
		dst_rect->h = vga_height;
		while (dst_rect->w + vga_width <= win_w && dst_rect->h + vga_height <= win_h)
		{
			dst_rect->w += vga_width;
			dst_rect->h += vga_height;
		}
		break;
	case SCALE_ASPECT_8_5:
		maxh_width = win_h * (8.f / 5.f);
		maxw_height = win_w * (5.f / 8.f);

		if (maxh_width > win_w)
		{
			dst_rect->w = win_w;
			dst_rect->h = maxw_height;
		}
		else
		{
			dst_rect->w = maxh_width;
			dst_rect->h = win_h;
		}
		break;
	case SCALE_ASPECT_4_3:
		maxh_width = win_h * (4.f / 3.f);
		maxw_height = win_w * (3.f / 4.f);

		if (maxh_width > win_w)
		{
			dst_rect->w = win_w;
			dst_rect->h = maxw_height;
		}
		else
		{
			dst_rect->w = maxh_width;
			dst_rect->h = win_h;
		}
		break;
	case ScalingMode_MAX:
		assert(false);
		break;
	}

	dst_rect->x = (win_w - dst_rect->w) / 2;
	dst_rect->y = (win_h - dst_rect->h) / 2;
}

static void present_screen(SDL_Surface *src_surface)
{
	assert(SDL_BITSPERPIXEL(src_surface->format) == 8);

	SDL_Rect dst_rect;
	calc_dst_render_rect(&dst_rect);

	rgpu_present_2d(src_surface, &dst_rect);

	// Save output rect to be used by mouse functions
	last_output_rect = dst_rect;
	last_frame_was_3d = false;
}

void JE_showVGA3D(void)
{
	SDL_Rect dst_rect;
	calc_dst_render_rect(&dst_rect);

	rgpu_present_3d(VGAScreenSeg, &l3d_frame, &dst_rect);

	last_output_rect = dst_rect;
	last_frame_was_3d = true;
}

static void set_3d_enabled(bool enabled)
{
	l3d_enabled = enabled;
	screen_overscan_rows = enabled ? SCREEN_OVERSCAN_MAX : 0;
	printf("view: %s\n", enabled ? "3D" : "2D");
}

static void print_camera(void)
{
	printf("camera: tilt %.1f deg, fov %.1f deg, height scale %.2f\n",
	       rgpu_camera.tilt_degrees, rgpu_camera.fov_degrees, rgpu_camera.height_scale);
}

bool video_handle_key(SDL_Scancode scancode)
{
	if (scancode == SDL_SCANCODE_F3)
	{
		set_3d_enabled(!l3d_enabled);
		return true;
	}
	if (scancode == SDL_SCANCODE_F4)
	{
		m3d_enabled = !m3d_enabled;
		printf("models: %s\n", m3d_enabled ? "on" : "off");
		return true;
	}
	if (scancode == SDL_SCANCODE_F5)
	{
		m3d_reload();
		return true;
	}

	// Camera keys only while the 3D view is on screen; menus use some of them.
	if (!l3d_enabled || !last_frame_was_3d)
		return false;

	switch (scancode)
	{
	case SDL_SCANCODE_PAGEUP:
		rgpu_camera.tilt_degrees = SDL_min(rgpu_camera.tilt_degrees + 2.5f, 60.0f);
		break;
	case SDL_SCANCODE_PAGEDOWN:
		rgpu_camera.tilt_degrees = SDL_max(rgpu_camera.tilt_degrees - 2.5f, 0.0f);
		break;
	case SDL_SCANCODE_HOME:
		rgpu_camera.fov_degrees = SDL_min(rgpu_camera.fov_degrees + 2.5f, 90.0f);
		break;
	case SDL_SCANCODE_END:
		rgpu_camera.fov_degrees = SDL_max(rgpu_camera.fov_degrees - 2.5f, 5.0f);
		break;
	case SDL_SCANCODE_INSERT:
		rgpu_camera.height_scale = SDL_min(rgpu_camera.height_scale + 0.25f, 4.0f);
		break;
	case SDL_SCANCODE_DELETE:
		rgpu_camera.height_scale = SDL_max(rgpu_camera.height_scale - 0.25f, 0.0f);
		break;
	default:
		return false;
	}
	print_camera();
	return true;
}

/** Maps a specified point in game screen coordinates to window coordinates. */
void mapScreenPointToWindow(Sint32 *const inout_x, Sint32 *const inout_y)
{
	*inout_x = (2 * *inout_x + 1) * last_output_rect.w / (2 * VGAScreen->w) + last_output_rect.x;
	*inout_y = (2 * *inout_y + 1) * last_output_rect.h / (2 * VGAScreen->h) + last_output_rect.y;
}

/** Maps a specified point in window coordinates to game screen coordinates. */
void mapWindowPointToScreen(Sint32 *const inout_x, Sint32 *const inout_y)
{
	*inout_x = (2 * (*inout_x - last_output_rect.x) + 1) * VGAScreen->w / (2 * last_output_rect.w);
	*inout_y = (2 * (*inout_y - last_output_rect.y) + 1) * VGAScreen->h / (2 * last_output_rect.h);
}

/** Scales a distance in window coordinates to game screen coordinates. */
void scaleWindowDistanceToScreen(Sint32 *const inout_x, Sint32 *const inout_y)
{
	*inout_x = (2 * *inout_x + 1) * VGAScreen->w / (2 * last_output_rect.w);
	*inout_y = (2 * *inout_y + 1) * VGAScreen->h / (2 * last_output_rect.h);
}
