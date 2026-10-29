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

#include "debugmode.h"
#include "devtools.h"
#include "episodes.h"
#include "game_menu.h"
#include "keyboard.h"
#include "mainint.h"
#include "opentyr.h"
#include "layer3d.h"
#include "models3d.h"
#include "mouse.h"
#include "nortsong.h"
#include "palette.h"
#include "particles3d.h"
#include "player.h"
#include "render_gpu.h"
#include "settings3d.h"
#include "sprite.h"
#include "ui.h"
#include "video_scale.h"
#include "volume3d.h"

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

	// Tyrian3D dev runs in the background: on macOS the game doesn't become the active application.
	if (dev_background_run())
		SDL_SetHint(SDL_HINT_MAC_BACKGROUND_APP, "1");

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

	// Tyrian3D dev runs (tools/capture_run.sh): TYR3D_WINDOWED keeps them in a window in the corner
	// of the screen, whatever the configuration says, without taking the focus. (A hidden window
	// gets no frames to render to.)
	const bool windowed = dev_background_run();
	const int configured_display = fullscreen_display;
	reinit_fullscreen(windowed ? -1 : fullscreen_display);
	if (windowed)
	{
		fullscreen_display = configured_display;  // so the configuration is saved unchanged
		SDL_SetHint(SDL_HINT_WINDOW_ACTIVATE_WHEN_SHOWN, "0");
		int w = scalers[scaler].width, h = scalers[scaler].height;
		const char *size = SDL_getenv("TYR3D_WINDOW_SIZE");  // "<w>x<h>", e.g. 1280x720
		if (size != NULL && sscanf(size, "%dx%d", &w, &h) == 2)
			SDL_SetWindowSize(main_window, w, h);
		SDL_Rect usable;
		if (SDL_GetDisplayUsableBounds(SDL_GetPrimaryDisplay(), &usable))
			SDL_SetWindowPosition(main_window, usable.x + usable.w - w - 16, usable.y + usable.h - h - 16);
	}

	SDL_ShowWindow(main_window);

	// Tyrian3D: what is typed (the title's codes, the names of saves and high scores) comes as text input,
	// which SDL3 sends only once asked (SDL2 had it on).
	SDL_StartTextInput(main_window);

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
	if (debug_flight_replaying())
		return;
	present_screen(VGAScreen);
}

static void calc_dst_render_rect(SDL_Rect *const dst_rect)
{
	// Decides how the logical 320x200 output will fit in the window (in window coordinates).

	int win_w, win_h;
	SDL_GetWindowSize(main_window, &win_w, &win_h);

	// Tyrian3D: the modern UI's screens fill the window's height (ui_fill_screens).
	if (ui_fill_screens())
	{
		ui_fill_rect(win_w, win_h, dst_rect);
		return;
	}

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

/*
 * Tyrian3D: in a level, the menus and messages the game draws over the playfield (the pause, the
 * in-game options, the level's end) show over the 3D view's last frame (rgpu_present_3d_menu): the
 * screen as it was when that frame showed (the backdrop), the boxes JE_barShade has darkened on it
 * since, and the palette then, for its fades. Until the screen is something else: its panel no
 * longer the level's.
 */
#define BACKDROP_SHADES 16

static Uint8 backdrop[320 * 200];
static bool backdrop_valid = false;
static bool backdrop_menu = false;       // a menu over the level has shown over it
static Uint32 backdrop_menu_frames = 0;  // l3d_frames_begun then
static int backdrop_shades[BACKDROP_SHADES][4];
static int backdrop_shade_count = 0;
static Uint32 backdrop_palette[256];

static void take_backdrop(void)
{
	for (int y = 0; y < 200 && y < VGAScreenSeg->h; ++y)
		memcpy(backdrop + y * 320, (const Uint8 *)VGAScreenSeg->pixels + y * VGAScreenSeg->pitch, 320);
	memcpy(backdrop_palette, rgb_palette, sizeof(backdrop_palette));
	backdrop_shade_count = 0;
	backdrop_valid = true;
	backdrop_menu = false;
}

static int shades_ignored = 0;  // see video_backdrop_ignore_shades

void video_backdrop_ignore_shades(bool ignore)
{
	shades_ignored += ignore ? 1 : -1;
}

int video_backdrop_shade_mark(void)
{
	return backdrop_shade_count;
}

void video_backdrop_shade_reset(int mark)
{
	backdrop_shade_count = SDL_clamp(mark, 0, backdrop_shade_count);
}

void video_backdrop_shade(const SDL_Surface *surface, int x1, int y1, int x2, int y2)
{
	if (backdrop_valid && shades_ignored <= 0 && surface->pixels == VGAScreenSeg->pixels && backdrop_shade_count < BACKDROP_SHADES)
	{
		int *r = backdrop_shades[backdrop_shade_count++];
		r[0] = x1;
		r[1] = y1;
		r[2] = x2;
		r[3] = y2;
	}
}

// The screen still shows the level: its panel (the right column) much as it was.
static bool backdrop_holds(const SDL_Surface *screen)
{
	if (!backdrop_valid || !l3d_enabled || screen->pixels != VGAScreenSeg->pixels)
		return false;
	int changed = 0;
	for (int y = 0; y < 200; ++y)
		for (int x = L3D_PLAYFIELD_W; x < 320; ++x)
			changed += ((const Uint8 *)screen->pixels)[y * screen->pitch + x] != backdrop[y * 320 + x];
	return changed < (320 - L3D_PLAYFIELD_W) * 200 / 4;
}

// The palette's fade since the backdrop: towards black or white, how far.
static void backdrop_fade(float fade[4])
{
	float was = 0, now = 0;
	for (int i = 0; i < 256; ++i)
	{
		const Uint8 *a = (const Uint8 *)&backdrop_palette[i], *b = (const Uint8 *)&rgb_palette[i];
		was += a[0] + a[1] + a[2];
		now += b[0] + b[1] + b[2];
	}
	const float white = now > was;
	fade[0] = fade[1] = fade[2] = white;
	if (white)
		fade[3] = (now - was) / SDL_max(256 * 3 * 255 - was, 1.0f);
	else
		fade[3] = was > 0 ? 1 - now / was : 0;
	fade[3] = SDL_clamp(fade[3], 0.0f, 1.0f);
}

/*
 * Tyrian3D: the store's illustration of the ship (draw_ship_illustration) shows as models over its
 * box (rgpu_present_showcase), while the screen still shows it: the box before the ship was drawn
 * on it (with the shield's arc, see video_showcase_backdrop) and the screen once it was.
 */
static const SDL_Rect showcase_pane = { 3, 8, 151, 141 };
static SDL_Surface *showcase_surface = NULL;  // the box without the ship
static Uint8 showcase_illustrated[320 * 200];
static bool showcase_valid = false;

void video_showcase_begin(void)
{
	showcase_valid = false;
	if (!l3d_enabled)
		return;
	if (showcase_surface == NULL &&
	    (showcase_surface = SDL_CreateSurface(VGAScreenSeg->w, VGAScreenSeg->h, SDL_PIXELFORMAT_INDEX8)) == NULL)
		return;
	for (int y = 0; y < VGAScreenSeg->h; ++y)
		memcpy((Uint8 *)showcase_surface->pixels + y * showcase_surface->pitch,
		       (const Uint8 *)VGAScreenSeg->pixels + y * VGAScreenSeg->pitch, VGAScreenSeg->w);
}

SDL_Surface *video_showcase_backdrop(void)
{
	return l3d_enabled ? showcase_surface : NULL;
}

void video_showcase_end(void)
{
	if (!l3d_enabled || showcase_surface == NULL)
		return;
	for (int y = 0; y < 200; ++y)
		memcpy(showcase_illustrated + y * 320, (const Uint8 *)VGAScreenSeg->pixels + y * VGAScreenSeg->pitch, 320);
	showcase_valid = true;
}

// The screen still shows the illustration: most of its box as it was drawn.
static bool showcase_holds(const SDL_Surface *screen)
{
	if (!showcase_valid || !l3d_enabled || !m3d_enabled || screen->pixels != VGAScreenSeg->pixels)
		return false;
	const SDL_Rect *p = &showcase_pane;
	int same = 0;
	for (int y = p->y; y < p->y + p->h; ++y)
		for (int x = p->x; x < p->x + p->w; ++x)
			same += ((const Uint8 *)screen->pixels)[y * screen->pitch + x] == showcase_illustrated[y * 320 + x];
	return same > p->w * p->h * 6 / 10;
}

// How dark the palette is against the store's.
static float store_fade(void)
{
	float now = 0, full = 0;
	for (int i = 0; i < 256; ++i)
	{
		const Uint8 *c = (const Uint8 *)&rgb_palette[i];
		now += c[0] + c[1] + c[2];
		full += colors[i].r + colors[i].g + colors[i].b;
	}
	return full > 0 ? SDL_clamp(1 - now / full, 0.0f, 1.0f) : 0;
}

static int player_ship_model(void)
{
	const PlayerItems *items = &player[0].items;
	const bool dragonwing = items->ship < COUNTOF(ships) && ships[items->ship].shipgraphic == 0;
	return m3d_ship_appearance(dragonwing ? M3D_SHIP_DRAGONWING : items->ship).model;
}

#define SHOWCASE_DECK 12.0f  // where the illustration's guns and generator sit on its big ship (models.cfg)

// The illustration: the ship hovering over its box, turning a little and banking as if flying,
// its sidekicks in their places (screen pixels, as the store's screen has them); returns how many.
static int showcase_objects(RGPUShowcaseObject *objects)
{
	const float t = SDL_GetTicks() / 1000.0f;
	const float yaw = 16.0f * sinf(t * 0.55f), roll = 14.0f * sinf(t * 0.8f + 1.0f), bob = sinf(t * 1.3f);
	int count = 0;

	// Two players (the modern UI's store): their ships side by side, player 1's at the left, player 2's
	// Dragonwing at the right.
	if (twoPlayerMode && ui_modern())
	{
		objects[count++] = (RGPUShowcaseObject){ player_ship_model(), 46, 88, 24.0f + 1.7f * bob, 50.0f, yaw, 0, roll, -1 };
		objects[count++] = (RGPUShowcaseObject){ m3d_ship_appearance(M3D_SHIP_DRAGONWING).model, 112, 88,
		                                         24.0f + 1.7f * sinf(t * 1.3f + 1.4f), 50.0f, -yaw, 0, -roll, -1 };
		return count;
	}

	// The big ship of the illustration with its generator and guns on its deck, if it has a
	// model; else the ship's own model.
	unsigned int table;
	int sprite_id, x, y;
	const PlayerItems *items = &player[0].items;
	const int big = ship_illustration_piece(ILLUSTRATION_SHIP, items, &table, &sprite_id, &x, &y)
	                ? m3d_illustration_model(sprite_id) : -1;
	if (big >= 0)
	{
		const float cx = x + get_sprite_width(table, sprite_id) / 2.0f, cy = y + get_sprite_height(table, sprite_id) / 2.0f;
		objects[count++] = (RGPUShowcaseObject){ big, cx, cy, 10.0f + 1.7f * bob, 0, yaw, 0, roll, -1 };
		static const IllustrationPart parts[] = { ILLUSTRATION_GENERATOR, ILLUSTRATION_FRONT, ILLUSTRATION_REAR };
		for (size_t i = 0; i < COUNTOF(parts); ++i)
		{
			if (!ship_illustration_piece(parts[i], items, &table, &sprite_id, &x, &y))
				continue;
			const int model = m3d_mount_model(sprite_id);
			if (model >= 0)
				objects[count++] = (RGPUShowcaseObject){ model, x + get_sprite_width(table, sprite_id) / 2.0f - cx,
				                                         y + get_sprite_height(table, sprite_id) / 2.0f - cy, SHOWCASE_DECK,
				                                         0, 0, 0, 0, 0 };
		}
	}
	else
		objects[count++] = (RGPUShowcaseObject){ player_ship_model(), 80, 86, 24.0f + 1.7f * bob, 70.0f, yaw, 0, roll, -1 };
	for (int i = 0; i < 2; ++i)
	{
		const JE_byte sidekick = items->sidekick[i];
		if (sidekick > 0)
			objects[count++] = (RGPUShowcaseObject){ m3d_sidekick_appearance(sidekick).model, i == 0 ? 15 : 141, 97,
			                                         16.0f + 1.2f * sinf(t * 1.1f + i * 2.0f), 22.0f, yaw * 0.5f, 0, roll * 0.5f, -1 };
	}
	return count;
}

static void sim_engine(float x, float y, float height, float scale, float yaw, RGPUShowcaseGlow *glows, int *count, int max);

// What glows round the illustration's models (showcase_objects, as it places them), as a level shows the same (with the
// Effects setting): the ship's engines and their flame behind its own model (not the illustration's big ship), the
// sidekicks' glows, and (shield: the modern store) on the shields' page the shield round the ship, as a level shows it
// when it takes a hit, as strong as the shield is (the original's arc over the illustration, which the modern store's
// pad hasn't; the classic store keeps the arc).
static int showcase_glows(RGPUShowcaseGlow *glows, int max, bool shield)
{
	if (!settings3d.effects || (twoPlayerMode && ui_modern()))
		return 0;
	const float t = SDL_GetTicks() / 1000.0f;
	const float yaw = 16.0f * sinf(t * 0.55f), bob = sinf(t * 1.3f);
	int count = 0;
	unsigned int table;
	int sprite_id, x, y;
	const PlayerItems *items = &player[0].items;
	float cx = 80, cy = 86, height = 24.0f + 1.7f * bob, reach = 70.0f;  // (the ship's model, 70 screen pixels)
	const bool big = ship_illustration_piece(ILLUSTRATION_SHIP, items, &table, &sprite_id, &x, &y) &&
	                 m3d_illustration_model(sprite_id) >= 0;
	if (big)
	{
		cx = x + get_sprite_width(table, sprite_id) / 2.0f;
		cy = y + get_sprite_height(table, sprite_id) / 2.0f;
		height = 10.0f + 1.7f * bob;
		reach = SDL_max(get_sprite_width(table, sprite_id), get_sprite_height(table, sprite_id));
	}
	else
		sim_engine(cx, cy, height, 70.0f / 24.0f, yaw, glows, &count, max);
	if (shield && shop_shield_page() && count + 2 <= max)
	{
		// (A level's: 34 and 20 pixels round a 24 pixel ship; slowly breathing.)
		static const Uint8 shield[3] = { 110, 180, 255 }, rim[3] = { 190, 225, 255 };
		const float k = reach / 24.0f, g = (0.45f + 0.55f * shop_shield_strength()) * (0.85f + 0.15f * sinf(t * 2.2f));
		glows[count] = (RGPUShowcaseGlow){ cx, cy + 2 * k, height, 34.0f * k, 0.32f * g, 0, { 0, 0, 0 } };
		memcpy(glows[count++].rgb, shield, 3);
		glows[count] = (RGPUShowcaseGlow){ cx, cy + 2 * k, height, 20.0f * k, 0.28f * g * g, 0, { 0, 0, 0 } };
		memcpy(glows[count++].rgb, rim, 3);
	}
	for (int i = 0; i < 2 && count < max; ++i)
	{
		const JE_byte id = items->sidekick[i];
		if (id == 0)
			continue;
		const M3DAppearance look = m3d_sidekick_appearance(id);
		if (look.model < 0 || look.glow_size == 0)
			continue;
		const bool large = options[id].tr == 1 || options[id].tr == 2;
		const float k = 22.0f / (large ? 24 : 12);  // (the model 22 screen pixels across)
		const float size = (look.glow_size < 0 ? -look.glow_size * (large ? 24 : 12) : look.glow_size) * k;
		const Uint8 color = look.glow_has_rgb ? 0 : look.glow_color != 0 ? look.glow_color
		                  : (Uint8)(l3d_sprite_ramp(large ? (const void *)&spriteSheet10 : (const void *)&spriteSheet9,
		                                            options[id].gr[0], large) << 4 | 11);
		glows[count] = (RGPUShowcaseGlow){ (i == 0 ? 15 : 141) + look.glow_dx * k, 97 + look.glow_dy * k,
		                                   16.0f + 1.2f * sinf(t * 1.1f + i * 2.0f), size, look.glow_strength, color, { 0, 0, 0 } };
		memcpy(glows[count++].rgb, look.glow_rgb, 3);
	}
	return count;
}

static void present_showcase(SDL_Surface *screen, const SDL_Rect *dst_rect)
{
	static Uint8 backdrop_pixels[320 * 200];
	for (int y = 0; y < 200; ++y)
		memcpy(backdrop_pixels + y * 320, (const Uint8 *)showcase_surface->pixels + y * showcase_surface->pitch, 320);
	RGPUShowcaseObject objects[6];
	const int count = showcase_objects(objects);
	RGPUShowcaseGlow glows[16];
	RGPUShowcase show = { .pane = showcase_pane, .backdrop = backdrop_pixels, .transparent = showcase_illustrated,
	                      .objects = objects, .object_count = count, .glows = glows,
	                      .glow_count = showcase_glows(glows, (int)COUNTOF(glows), false) };
	show.fade[3] = store_fade();
	rgpu_present_showcase(screen, &show, dst_rect);
}

/*
 * The store's weapon simulator (JE_weaponViewFrame) in the 3D view, as a level's 3D view shows the same things: its box
 * as it is once the stars are drawn each frame; the ship, its sidekicks (where the simulator fires their shots from,
 * which the original doesn't draw) and the shots as models, the shots without one as their sprites with volume (flat,
 * HD), instead of their sprites (video_sim_ship, video_sim_shot); the shots' glows, the ship's engines' glow and flame,
 * the sidekicks' glows; the missiles' smoke (the particles, particles3d.h, are the simulator's while it shows: cleared as
 * it opens, a level clears them as it loads). The simulator's logic and what it fires are the original's.
 */
#define SIM_OBJECTS 128
#define SIM_GLOWS 192

static const SDL_Rect sim_pane = { 8, 8, 136, 175 };
static Uint8 sim_backdrop[320 * 200];
static bool sim_valid = false;
static RGPUShowcaseObject sim_objects[SIM_OBJECTS];
static int sim_object_count = 0;
static RGPUShowcaseGlow sim_glows[SIM_GLOWS];
static int sim_glow_count = 0;
static Uint32 sim_frame = 0;

// A glow in the simulator (screen pixels; color a palette index, or 0 and rgb).
static void sim_glow(float x, float y, float height, float size, float strength, Uint8 color, const Uint8 *rgb)
{
	if (sim_glow_count == SIM_GLOWS || (color == 0 && rgb == NULL) || strength <= 0)
		return;
	RGPUShowcaseGlow *g = &sim_glows[sim_glow_count++];
	*g = (RGPUShowcaseGlow){ x, y, height, size, strength, color, { 0, 0, 0 } };
	if (color == 0)
		memcpy(g->rgb, rgb, 3);
}

void video_sim_begin(void)
{
	sim_valid = l3d_enabled && m3d_enabled;
	sim_object_count = 0;
	sim_glow_count = 0;
	++sim_frame;
	if (!sim_valid)
		return;
	for (int y = 0; y < 200; ++y)
		memcpy(sim_backdrop + y * 320, (const Uint8 *)VGAScreen->pixels + y * VGAScreen->pitch, 320);
	// (A simulator opened anew starts with no particles: what a level left, or an earlier simulator's.)
	static Uint32 last_ticks = 0;
	const Uint32 now = (Uint32)SDL_GetTicks();
	if (now - last_ticks > 500)
		p3d_clear();
	last_ticks = now;
	p3d_update(0);
}

bool video_sim_shot(bool shots2, unsigned int sprite, int x, int y, int dx, int dy)
{
	if (!sim_valid || sim_object_count == SIM_OBJECTS)
		return false;
	const void *sheet = shots2 ? (const void *)&spriteSheet12 : (const void *)&spriteSheet8;
	const float height = l3d_layer_height(L3D_PLAYER);
	M3DAppearance look;
	const bool model = m3d_shot_appearance(shots2, sprite, &look);
	dev_log_sprites_store(shots2, sprite, model);  // (TYR3D_LOG_SPRITES)
	if (model)
	{
		const float yaw = look.yaw + (look.spin != 0 ? fmodf(look.spin * sim_frame + (float)(x * 7 + y * 13 & 63) * 47.0f, 360.0f) : 0.0f);
		sim_objects[sim_object_count++] = (RGPUShowcaseObject){ look.model, x + 6.0f, y + 7.0f, height + look.height, 0, yaw, 0, 0, -1 };
		// Missiles leave smoke (with Effects), as in a level.
		if (look.trail && settings3d.effects)
			p3d_trail(x + 6.0f, y + 7.0f, (float)dx, (float)dy, height, P3D_TRAIL_SMOKE, 0);
	}
	else  // (its sprite with volume, flat, as a level's shots without a model: layer3d.c l3d_add_shot)
		sim_objects[sim_object_count++] = (RGPUShowcaseObject){ M3D_VOLUME, x + 6.0f, y + 7.0f, height, 0, 0, 0, 0, -1,
		                                                       sheet, (Uint16)sprite, false, V3D_STYLE_FLAT };
	// Its glow in the sprite's brightest colour (l3d_add_glow).
	sim_glow(x + 6.0f, y + 7.0f, height, 13.0f, 0.7f, l3d_sprite_glow_color(sheet, sprite, false), NULL);
	return true;
}

// The box once the shots are drawn (before the simulator's frame goes over it): what the modern UI
// draws over the scene of the simulator (shots without models).
static Uint8 sim_shots[320 * 200];

void video_sim_shots_drawn(void)
{
	if (!sim_valid)
		return;
	for (int y = 0; y < 200; ++y)
		memcpy(sim_shots + y * 320, (const Uint8 *)VGAScreen->pixels + y * VGAScreen->pitch, 320);
}

// The engines' glow behind a ship and the flame trailing from them, as a level shows them (mainint.c): at x, y the
// ship's middle, scale times a ship's size in a level, turned yaw degrees (screen pixels).
static void sim_engine(float x, float y, float height, float scale, float yaw, RGPUShowcaseGlow *glows, int *count, int max)
{
	static const Uint8 engine[3] = { 255, 150, 64 };
	static const Uint8 flame[5][3] = { { 255, 226, 168 }, { 255, 176, 84 }, { 255, 120, 40 }, { 226, 70, 22 }, { 170, 40, 16 } };
	static const float flame_size[5] = { 8.0f, 7.0f, 6.0f, 5.0f, 4.0f };
	static const float flame_strength[5] = { 0.56f, 0.46f, 0.36f, 0.26f, 0.16f };
	static Uint32 flicker = 0x2545f491u;
	const float s = sinf(yaw * (float)M_PI / 180.0f), c = cosf(yaw * (float)M_PI / 180.0f);
	for (int i = -1; i < 5 && *count < max; ++i)
	{
		flicker = flicker * 1664525u + 1013904223u;
		const float wobble = i < 0 ? 1.0f : 0.85f + 0.3f * (float)(flicker >> 8) / 16777216.0f;
		const float back = (12.0f + (i < 0 ? 0.0f : (2.5f + 2.2f * i) * wobble)) * scale;  // (behind the middle)
		RGPUShowcaseGlow *g = &glows[(*count)++];
		*g = (RGPUShowcaseGlow){ x - s * back, y + c * back, height, (i < 0 ? 10.0f : flame_size[i]) * scale,
		                         i < 0 ? 0.45f : flame_strength[i] * wobble, 0, { 0, 0, 0 } };
		memcpy(g->rgb, i < 0 ? engine : flame[i], 3);
	}
}

bool video_sim_ship(int x, int y)
{
	if (!sim_valid)
		return false;
	const float height = l3d_layer_height(L3D_PLAYER);

	// The sidekicks where the simulator fires their shots from (JE_weaponViewFrame), as a level shows them: their models,
	// centred where their sprites would be, turning as they do, with their glows.
	for (int i = 0; i < 2 && sim_object_count < SIM_OBJECTS; ++i)
	{
		const JE_byte id = player[0].items.sidekick[i];
		const JE_OptionType *option = &options[id];
		if (id == 0 || option->option == 0)
			continue;
		const M3DAppearance look = m3d_sidekick_appearance(id);
		const bool large = option->tr == 1 || option->tr == 2;
		const float sx = player[0].sidekick[i].x + 6.0f, sy = player[0].sidekick[i].y + (large ? 14.0f : 7.0f);
		float yaw = look.yaw;
		if (look.spin != 0)
			yaw += fmodf(look.spin * sim_frame + i * 90.0f, 360.0f);
		if (look.model >= 0)
			sim_objects[sim_object_count++] = (RGPUShowcaseObject){ look.model, sx, sy, height + look.height, 0, yaw, 0, 0, -1 };
		else if (look.model == M3D_VOLUME)
			sim_objects[sim_object_count++] = (RGPUShowcaseObject){ M3D_VOLUME, sx, sy, height + look.height, 0, 0, 0, 0, -1,
			                                                       large ? (const void *)&spriteSheet10 : (const void *)&spriteSheet9,
			                                                       option->gr[0], large, V3D_STYLE_RAISED };
		if (look.model >= 0 && look.glow_size != 0)
		{
			const float size = look.glow_size < 0 ? -look.glow_size * (large ? 24 : 12) : look.glow_size;
			const Uint8 color = look.glow_has_rgb ? 0 : look.glow_color != 0 ? look.glow_color
			                  : (Uint8)(l3d_sprite_ramp(large ? (const void *)&spriteSheet10 : (const void *)&spriteSheet9,
			                                            option->gr[0], large) << 4 | 11);
			sim_glow(sx + look.glow_dx, sy + look.glow_dy, height + look.height, size, look.glow_strength, color, look.glow_rgb);
		}
	}

	const int model = player_ship_model();
	if (model < 0 || sim_object_count == SIM_OBJECTS)
		return false;
	sim_objects[sim_object_count++] = (RGPUShowcaseObject){ model, (float)x, (float)y, height, 0, 0, 0, 0, -1 };
	if (settings3d.effects)
		sim_engine((float)x, (float)y, height, 1.0f, 0.0f, sim_glows, &sim_glow_count, SIM_GLOWS);
	return true;
}

// The screen still shows the simulator: most of its box as the frame began.
static bool sim_holds(const SDL_Surface *screen)
{
	if (!sim_valid || !l3d_enabled || !m3d_enabled || screen->pixels != VGAScreenSeg->pixels)
		return false;
	const SDL_Rect *p = &sim_pane;
	int same = 0;
	for (int y = p->y; y < p->y + p->h; ++y)
		for (int x = p->x; x < p->x + p->w; ++x)
			same += ((const Uint8 *)screen->pixels)[y * screen->pitch + x] == sim_backdrop[y * 320 + x];
	return same > p->w * p->h / 2;
}

static void present_sim(SDL_Surface *screen, const SDL_Rect *dst_rect)
{
	RGPUShowcase show = { .pane = sim_pane, .backdrop = sim_backdrop, .transparent = sim_backdrop,
	                      .objects = sim_objects, .object_count = sim_object_count,
	                      .glows = sim_glows, .glow_count = sim_glow_count, .particles = true };
	show.fade[3] = store_fade();
	rgpu_present_showcase(screen, &show, dst_rect);
}

static bool level_intro = false;  // see video_level_intro

void video_level_intro(bool on)
{
	level_intro = on;
}

static void present_screen_timed(SDL_Surface *src_surface);

// (TYR3D_PROFILE: what presenting the game's screens costs, averaged over 120 of them.)
static void present_screen(SDL_Surface *src_surface)
{
	static int profile = -1;
	if (profile < 0)
		profile = SDL_getenv("TYR3D_PROFILE") != NULL;
	if (!profile)
	{
		present_screen_timed(src_surface);
		return;
	}
	static Uint64 spent = 0, most = 0;
	static int count = 0;
	const Uint64 start = SDL_GetPerformanceCounter();
	present_screen_timed(src_surface);
	const Uint64 took = SDL_GetPerformanceCounter() - start;
	spent += took;
	most = SDL_max(most, took);
	if (++count == 120)
	{
		const double k = 1000.0 / SDL_GetPerformanceFrequency();
		printf("screen present: %.2f ms a screen, at most %.2f\n", spent * k / count, most * k);
		spent = most = 0;
		count = 0;
	}
}

// TYR3D_RENDER_ICONS=<dir>: the items' icons rendered from their models into <dir> (render_gpu.c rgpu_render_icons), once
// the modern store shows its ship (so in the store's palette).
static void render_icons_once(void)
{
	static bool done = false;
	const char *dir = SDL_getenv("TYR3D_RENDER_ICONS");
	if (done || dir == NULL || dir[0] == '\0' || ui_screen_scene() != UI_SCENE_SHIP)
		return;
	done = true;
	static int models[256], ramps[256];
	static RGPUIcon icons[256];
	const int count = shop_icon_models(models, ramps, (int)COUNTOF(models));
	for (int i = 0; i < count; ++i)
		icons[i] = (RGPUIcon){ models[i], ramps[i] };
	rgpu_render_icons(dir, icons, count);
}

static void present_screen_timed(SDL_Surface *src_surface)
{
	assert(SDL_BITSPERPIXEL(src_surface->format) == 8);

	SDL_Rect dst_rect;
	calc_dst_render_rect(&dst_rect);
	ui_screen_shown(false);

	// A level's start with the modern HUD: not the panel the game fades in (the HUD's gauges show over
	// the level once it plays), the window black.
	if (level_intro && l3d_enabled && rgpu_modern_hud())
	{
		rgpu_present_blank();
		last_output_rect = dst_rect;
		last_frame_was_3d = false;
		mouse_frame_shown();
		return;
	}

	// A menu in the modern UI's style (ui.h): while the screen shows what the menu published (those
	// over a level: over its 3D view, below).
	const bool modern = ui_screen_holds(src_surface);
	if (modern && !ui_screen_over_level())
	{
		render_icons_once();
		backdrop_valid = false;
		// The store's ship or its weapon simulator, as models where the screen's layout shows them.
		RGPUShowcase show = { .backdrop = sim_backdrop };
		static RGPUShowcaseObject objects[8];
		const RGPUShowcase *scene = NULL;
		switch (ui_screen_scene())
		{
		case UI_SCENE_SHIP:
			if (m3d_enabled)
			{
				static RGPUShowcaseGlow glows[16];
				show.objects = objects;
				show.object_count = showcase_objects(objects);
				show.glows = glows;
				show.glow_count = showcase_glows(glows, (int)COUNTOF(glows), true);
				show.backdrop = NULL;
				scene = &show;
			}
			break;
		case UI_SCENE_SIM:
			if (sim_valid)
			{
				show.objects = sim_objects;
				show.object_count = sim_object_count;
				show.glows = sim_glows;
				show.glow_count = sim_glow_count;
				show.particles = true;
				show.transparent = sim_shots;
				scene = &show;
			}
			break;
		default:
			break;
		}
		sim_valid = false;
		showcase_valid = false;
		rgpu_present_ui(scene);
		int win_w, win_h;
		SDL_GetWindowSize(main_window, &win_w, &win_h);
		ui_fill_rect(win_w, win_h, &last_output_rect);  // (as the picture shows)
		last_frame_was_3d = false;
		ui_screen_shown(true);
		mouse_frame_shown();
		return;
	}

	if (backdrop_holds(src_surface))
	{
		// (Shown mid-tick, the frame being captured ends here: what's drawn of the tick after the
		// menu shows in it only in 2D.)
		if (l3d_capturing)
			l3d_frame_end_early();
		float fade[4];
		backdrop_fade(fade);
		SDL_Rect screen_rect;
		const bool modern_level = modern && ui_screen_over_level();
		rgpu_present_3d_menu(src_surface, backdrop, (const int (*)[4])backdrop_shades, backdrop_shade_count, fade,
		                     &l3d_frame, &dst_rect, &screen_rect, modern_level);
		last_output_rect = screen_rect;
		last_frame_was_3d = false;
		backdrop_menu = true;
		backdrop_menu_frames = l3d_frames_begun;
		ui_screen_shown(modern_level);
		mouse_frame_shown();
		return;
	}
	// (The view turned to 2D in a menu over the level (the in-game options) and back: the backdrop
	// holds again while the game hasn't gone on since.)
	if (l3d_enabled || !backdrop_menu || backdrop_menu_frames != l3d_frames_begun)
		backdrop_valid = false;

	const bool sim = sim_holds(src_surface);
	if (!sim)
		sim_valid = false;
	if (sim || showcase_holds(src_surface))
	{
		if (sim)
			present_sim(src_surface, &dst_rect);
		else
			present_showcase(src_surface, &dst_rect);
		last_output_rect = dst_rect;
		last_frame_was_3d = false;
		mouse_frame_shown();
		return;
	}

	rgpu_present_2d(src_surface, &dst_rect);

	// Save output rect to be used by mouse functions
	last_output_rect = dst_rect;
	last_frame_was_3d = false;
	mouse_frame_shown();
}

int video_pointer_scale(void)
{
	// Window points per screen pixel, whole.
	const int scale = (last_output_rect.w + vga_width / 2) / vga_width;
	return scale < 1 ? 1 : scale;
}

void JE_showVGA3D(void)
{
	if (debug_flight_replaying())
		return;
	// Fast debug flights show every so many ticks, as the display allows.
	static int fast_skipped = 0;
	if (nortsong_time_scale < 0.4f && ++fast_skipped < (int)(0.5f / nortsong_time_scale))
		return;
	fast_skipped = 0;
	take_backdrop();
	showcase_valid = sim_valid = false;
	ui_screen_shown(false);

	// TYR3D_TURBO (dev): only every so many ticks shows, so the game isn't held up by the display.
	static int turbo = -1, skipped = 0;
	if (turbo < 0)
		turbo = SDL_getenv("TYR3D_TURBO") != NULL ? SDL_max(SDL_atoi(SDL_getenv("TYR3D_TURBO")), 1) : 1;
	if (++skipped < turbo)
		return;
	skipped = 0;

	SDL_Rect dst_rect;
	calc_dst_render_rect(&dst_rect);

	rgpu_present_3d(VGAScreenSeg, &l3d_frame, &dst_rect);

	last_output_rect = dst_rect;
	last_frame_was_3d = true;
	mouse_frame_shown();
}

// The display's refresh period, for pacing the frames shown between ticks.
static Uint64 refresh_period_ns(void)
{
	const SDL_DisplayMode *mode = SDL_GetCurrentDisplayMode(SDL_GetDisplayForWindow(main_window));
	const float rate = mode != NULL && mode->refresh_rate > 1.0f ? mode->refresh_rate : 60.0f;
	return (Uint64)(1e9f / rate);
}

void video_wait_tick_3d(void)
{
	if (nortsong_skip_waits)
		return;
	// TYR3D_SMOOTH=0: wait as the game always has, showing nothing more.
	static int smooth = -1;
	if (smooth < 0)
		smooth = SDL_getenv("TYR3D_SMOOTH") == NULL || SDL_atoi(SDL_getenv("TYR3D_SMOOTH")) != 0;

	const Uint64 period = refresh_period_ns();
	static Uint64 cost = 0;  // what showing a frame takes, about
	static unsigned int ticks = 0, extra_frames = 0;
	static double left_sum = 0;
	left_sum += getDelayLeftNS() / 1e6;
	Uint64 next = SDL_GetTicksNS() + period;
	for (;;)
	{
		const Sint64 left = getDelayLeftNS();
		if (!smooth || left <= (Sint64)(cost + 500000))
			break;
		const Uint64 now = SDL_GetTicksNS();
		if (now < next)
		{
			const Uint64 sleep = SDL_min(next - now, (Uint64)left - cost - 500000);
			SDL_DelayPrecise(sleep);
			continue;
		}

		SDL_Rect dst_rect;
		calc_dst_render_rect(&dst_rect);
		const Uint64 start = SDL_GetTicksNS();
		service_SDL_events(false);  // the mouse's motion so far, for the ship it moves
		player_pointer_lead(l3d_pointer_lead);
		rgpu_present_3d_ahead(VGAScreenSeg, &l3d_frame, &dst_rect, getDelayProgress());
		const Uint64 end = SDL_GetTicksNS();
		// A typical frame's cost: an occasional slow one (the GPU catching up) doesn't count fully,
		// or it would cut the frames short after it.
		cost = (cost * 7 + SDL_min(end - start, cost * 2 + 500000)) / 8;
		next = start + period;
		++extra_frames;
	}
	l3d_pointer_lead[0] = l3d_pointer_lead[1] = 0;
	wait_delay_precise();

	++ticks;
	if (SDL_getenv("TYR3D_PROFILE") != NULL && ticks % 175 == 0)
		printf("smooth: %.1f frames shown per tick (display %.0f Hz; %.1f ms left after a tick, a frame costs %.1f ms)\n",
		       1.0 + extra_frames / 175.0, 1e9 / period, left_sum / 175, cost / 1e6);
	if (ticks % 175 == 0)
	{
		extra_frames = 0;
		left_sum = 0;
	}
}

void video_wait_tick_ui(void)
{
	if (nortsong_skip_waits)
		return;
	static int smooth = -1;
	if (smooth < 0)
		smooth = SDL_getenv("TYR3D_SMOOTH") == NULL || SDL_atoi(SDL_getenv("TYR3D_SMOOTH")) != 0;
	if (!smooth || !l3d_enabled || !ui_screen_holds(VGAScreen))
	{
		wait_delay();
		return;
	}
	const Uint64 period = refresh_period_ns();
	static Uint64 cost = 0;  // what showing a frame takes, about
	Uint64 next = SDL_GetTicksNS() + period;
	for (;;)
	{
		const Sint64 left = getDelayLeftNS();
		if (left <= (Sint64)(cost + 500000))
			break;
		const Uint64 now = SDL_GetTicksNS();
		if (now < next)
		{
			SDL_DelayPrecise(SDL_min(next - now, (Uint64)left - cost - 500000));
			continue;
		}
		const Uint64 start = SDL_GetTicksNS();
		service_SDL_events(false);  // (the pointer over the panel)
		rgpu_present_ui_again();
		const Uint64 end = SDL_GetTicksNS();
		cost = (cost * 7 + SDL_min(end - start, cost * 2 + 500000)) / 8;
		next = start + period;
	}
	wait_delay_precise();
}

void video_set_3d_enabled(bool enabled)
{
	if (l3d_enabled != enabled)
		printf("view: %s\n", enabled ? "3D" : "2D");
	l3d_enabled = enabled;
	screen_overscan_rows = enabled ? SCREEN_OVERSCAN_MAX : 0;
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
		settings3d.view_3d = !l3d_enabled;
		settings3d_changed(S3D_VIEW);
		video_set_3d_enabled(settings3d.view_3d);
		return true;
	}
	if (scancode == SDL_SCANCODE_F4)
	{
		settings3d.models = m3d_enabled = !m3d_enabled;
		settings3d_changed(S3D_MODELS);
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
	// Tyrian3D: on a modern UI's screen, the point of the original's item the pointer is on (ui.h).
	if (ui_map_pointer((float)*inout_x, (float)*inout_y, inout_x, inout_y))
		return;
	*inout_x = (2 * (*inout_x - last_output_rect.x) + 1) * VGAScreen->w / (2 * last_output_rect.w);
	*inout_y = (2 * (*inout_y - last_output_rect.y) + 1) * VGAScreen->h / (2 * last_output_rect.h);
}

bool video_window_to_game(float wx, float wy, float *x, float *y)
{
	if (last_frame_was_3d)
		return rgpu_window_to_playfield(wx, wy, x, y);
	if (last_output_rect.w <= 0 || last_output_rect.h <= 0)
		return false;
	*x = (wx - last_output_rect.x) * VGAScreen->w / last_output_rect.w;
	*y = (wy - last_output_rect.y) * VGAScreen->h / last_output_rect.h;
	return true;
}

bool video_game_to_window(float x, float y, float *wx, float *wy)
{
	if (last_frame_was_3d)
		return rgpu_playfield_to_window(x, y, wx, wy);
	*wx = last_output_rect.x + x * last_output_rect.w / VGAScreen->w;
	*wy = last_output_rect.y + y * last_output_rect.h / VGAScreen->h;
	return true;
}

void video_window_points_per_pixel(float *x, float *y)
{
	if (last_frame_was_3d)
	{
		*x = *y = rgpu_playfield_scale();
		return;
	}
	*x = (float)last_output_rect.w / VGAScreen->w;
	*y = (float)last_output_rect.h / VGAScreen->h;
}

/** Scales a distance in window coordinates to game screen coordinates. */
void scaleWindowDistanceToScreen(Sint32 *const inout_x, Sint32 *const inout_y)
{
	*inout_x = (2 * *inout_x + 1) * VGAScreen->w / (2 * last_output_rect.w);
	*inout_y = (2 * *inout_y + 1) * VGAScreen->h / (2 * last_output_rect.h);
}
