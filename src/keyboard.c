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
#include "keyboard.h"

#include "devtools.h"

#include "config.h"
#include "joystick.h"
#include "mouse.h"
#include "network.h"
#include "opentyr.h"
#include "player.h"
#include "settings3d.h"
#include "ui.h"
#include "video.h"
#include "video_scale.h"

#include <SDL3/SDL.h>

#include <stdio.h>

JE_boolean ESCPressed;

JE_boolean newkey, newmouse, keydown, mousedown;
SDL_Scancode lastkey_scan;
SDL_Keymod lastkey_mod;
Uint8 lastmouse_but;
Sint32 lastmouse_x, lastmouse_y;
JE_boolean mouse_pressed[4] = {false, false, false, false};
Sint32 mouse_x, mouse_y;
float mouse_wheel_pending = 0;

bool windowHasFocus;

Uint8 keysactive[SDL_SCANCODE_COUNT];

bool new_text;
char last_text[32];

static bool mouseRelativeEnabled;

// Relative mouse position in window coordinates (SDL reports fractions of a point).
static float mouseWindowXRelative;
static float mouseWindowYRelative;

// Tyrian3D: the pointer's position in the window (points), and whether it moved since the game
// last looked (mouse_take_pointer_moved).
static float pointerWindowX, pointerWindowY;
static bool pointerMoved;

void flush_events_buffer(void)
{
	SDL_Event ev;

	while (SDL_PollEvent(&ev));
}

void wait_input(JE_boolean keyboard, JE_boolean mouse, JE_boolean joystick)
{
	service_SDL_events(false);
	while (!((keyboard && keydown) || (mouse && mousedown) || (joystick && joydown)))
	{
		SDL_Delay(SDL_POLL_INTERVAL);
		push_joysticks_as_keyboard();
		service_SDL_events(false);

#ifdef WITH_NETWORK
		if (isNetworkGame)
			network_check();
#endif
	}
}

void wait_noinput(JE_boolean keyboard, JE_boolean mouse, JE_boolean joystick)
{
	service_SDL_events(false);
	while ((keyboard && keydown) || (mouse && mousedown) || (joystick && joydown))
	{
		SDL_Delay(SDL_POLL_INTERVAL);
		poll_joysticks();
		service_SDL_events(false);

#ifdef WITH_NETWORK
		if (isNetworkGame)
			network_check();
#endif
	}
}

void init_keyboard(void)
{
	//SDL_EnableKeyRepeat(500, 60); TODO Find if SDL2 has an equivalent.

	newkey = newmouse = false;
	keydown = mousedown = false;

	SDL_HideCursor();

	SDL_SetHint(SDL_HINT_MOUSE_RELATIVE_SYSTEM_SCALE, "1");
}

void mouseSetRelative(bool enable)
{
	// Tyrian3D: with the direct mouse the ship goes where the (hidden) pointer is, so the pointer
	// keeps moving as on the desktop; it is only kept in the window. So too where it aims twin-stick's
	// turret (player.h).
	if (settings3d.mouse_direct || twin_stick())
	{
		SDL_SetWindowRelativeMouseMode(main_window, false);
		SDL_SetWindowMouseGrab(main_window, enable && windowHasFocus);
	}
	else
	{
		SDL_SetWindowMouseGrab(main_window, false);
		SDL_SetWindowRelativeMouseMode(main_window, enable && windowHasFocus);
	}

	mouseRelativeEnabled = enable;

	mouseWindowXRelative = 0;
	mouseWindowYRelative = 0;
}

JE_word JE_mousePosition(JE_word *mouseX, JE_word *mouseY)
{
	service_SDL_events(false);
	*mouseX = mouse_x;
	*mouseY = mouse_y;
	return mousedown ? lastmouse_but : 0;
}

void mouseGetRelativePosition(Sint32 *const out_x, Sint32 *const out_y)
{
	service_SDL_events(false);

	// Tyrian3D: in screen pixels at the size the screen is shown at (the 3D view's playfield is
	// larger than the 2D screen); what is left below a whole pixel is kept for the next call, so
	// slow motion moves the ship too (it used to be dropped below a pixel per frame).
	float points_x, points_y;
	video_window_points_per_pixel(&points_x, &points_y);
	*out_x = (Sint32)(mouseWindowXRelative / points_x);
	*out_y = (Sint32)(mouseWindowYRelative / points_y);
	mouseWindowXRelative -= *out_x * points_x;
	mouseWindowYRelative -= *out_y * points_y;
}

bool mouse_pointer_game(float *const out_x, float *const out_y)
{
	return video_window_to_game(pointerWindowX, pointerWindowY, out_x, out_y);
}

bool mouse_pointer_window(float *const out_x, float *const out_y)
{
	*out_x = pointerWindowX;
	*out_y = pointerWindowY;
	return !mouseInactive;
}

bool mouse_pointer_moved(void)
{
	return pointerMoved;
}

bool mouse_take_pointer_moved(void)
{
	const bool moved = pointerMoved;
	pointerMoved = false;
	return moved;
}

void mouse_place_pointer(float x, float y)
{
	float wx, wy;
	if (windowHasFocus && video_game_to_window(x, y, &wx, &wy))
	{
		SDL_WarpMouseInWindow(main_window, wx, wy);
		pointerWindowX = wx;
		pointerWindowY = wy;
	}
}

void service_SDL_events(JE_boolean clear_new)
{
	SDL_Event ev;

	if (clear_new)
	{
		newkey = false;
		newmouse = false;
		new_text = false;
	}

	while (SDL_PollEvent(&ev))
	{
		switch (ev.type)
		{
			case SDL_EVENT_WINDOW_FOCUS_LOST:
				windowHasFocus = false;

				mouseSetRelative(mouseRelativeEnabled);
				break;

			case SDL_EVENT_WINDOW_FOCUS_GAINED:
				windowHasFocus = true;

				mouseSetRelative(mouseRelativeEnabled);
				break;

			case SDL_EVENT_WINDOW_RESIZED:
				video_on_win_resize();
				break;

			case SDL_EVENT_KEY_DOWN:
				dev_input_taken();  // (TYR3D_DUMP_KEYS)
				// Tyrian3D: a joystick's (push_key) or the keyboard's (joystick.h).
				joystick_last_input = joystick_keys_pushed > 0;
				if (joystick_keys_pushed > 0)
					--joystick_keys_pushed;
				/* <alt><enter> toggle fullscreen */
				if (ev.key.mod & SDL_KMOD_ALT && ev.key.scancode == SDL_SCANCODE_RETURN)
				{
					toggle_fullscreen();
					break;
				}

				if (!ev.key.repeat && video_handle_key(ev.key.scancode))
					break;

				keysactive[ev.key.scancode] = 1;

				newkey = true;
				lastkey_scan = ev.key.scancode;
				lastkey_mod = ev.key.mod;
				keydown = true;

				mouseInactive = true;
				return;

			case SDL_EVENT_KEY_UP:
				keysactive[ev.key.scancode] = 0;
				keydown = false;
				return;

			case SDL_EVENT_MOUSE_MOTION:
				dev_input_taken();  // (TYR3D_DUMP_KEYS)
				pointerWindowX = ev.motion.x;
				pointerWindowY = ev.motion.y;
				if (ev.motion.xrel != 0 || ev.motion.yrel != 0)
					pointerMoved = true;
				mouse_x = (Sint32)ev.motion.x;
				mouse_y = (Sint32)ev.motion.y;
				mapWindowPointToScreen(&mouse_x, &mouse_y);

				// (and in a test run's window, which hasn't the focus, its MouseTo moves: TYR3D_TEST_KEYS)
				if (mouseRelativeEnabled && (windowHasFocus || SDL_getenv("TYR3D_TEST_KEYS") != NULL))
				{
					mouseWindowXRelative += ev.motion.xrel;
					mouseWindowYRelative += ev.motion.yrel;
				}

				// Show system mouse pointer if outside screen (with the game's own pointer the system
				// pointer is shown as the screens want it, mouse_frame_shown).
				if (SDL_getenv("TYR3D_SOFTWARE_POINTER") != NULL)
				{
					if (mouse_x < 0 || mouse_x >= vga_width || mouse_y < 0 || mouse_y >= vga_height)
						SDL_ShowCursor();
					else
						SDL_HideCursor();
				}

				if (ev.motion.xrel != 0 || ev.motion.yrel != 0)
					mouseInactive = false;
				break;

			case SDL_EVENT_MOUSE_BUTTON_DOWN:
				dev_input_taken();  // (TYR3D_DUMP_KEYS)
				mouseInactive = false;

				// fall through
			case SDL_EVENT_MOUSE_BUTTON_UP:
				{
					Sint32 button_x = (Sint32)ev.button.x;
					Sint32 button_y = (Sint32)ev.button.y;
					mapWindowPointToScreen(&button_x, &button_y);
					if (ev.type == SDL_EVENT_MOUSE_BUTTON_DOWN)
					{
						lastmouse_x = button_x;
						lastmouse_y = button_y;
						ui_note_press(ev.button.button);  // Tyrian3D: on a modern UI's own widget (ui.h)
					}
				}
				if (ev.type == SDL_EVENT_MOUSE_BUTTON_DOWN)
				{
					newmouse = true;
					lastmouse_but = ev.button.button;
					mousedown = true;
				}
				else
				{
					mousedown = false;
				}

				int whichMB = -1;
				switch (ev.button.button)
				{
					case SDL_BUTTON_LEFT:   whichMB = 0; break;
					case SDL_BUTTON_RIGHT:  whichMB = 1; break;
					case SDL_BUTTON_MIDDLE: whichMB = 2; break;
				}
				if (whichMB < 0)
					break;

				switch (mouseSettings[whichMB])
				{
					case 1: // Fire Main Weapons
						mouse_pressed[0] = mousedown;
						break;
					case 2: // Fire Left Sidekick
						mouse_pressed[1] = mousedown;
						break;
					case 3: // Fire Right Sidekick
						mouse_pressed[2] = mousedown;
						break;
					case 4: // Fire BOTH Sidekicks
						mouse_pressed[1] = mousedown;
						mouse_pressed[2] = mousedown;
						break;
					case 5: // Change Rear Mode
						mouse_pressed[3] = mousedown;
						break;
				}
				break;

			case SDL_EVENT_MOUSE_WHEEL:
			{
				dev_input_taken();  // (TYR3D_DUMP_KEYS)
				// Tyrian3D: over a modern UI's menu (ui.h) the wheel moves through its items, as the
				// up and down keys do.
				const float y = ev.wheel.direction == SDL_MOUSEWHEEL_FLIPPED ? -ev.wheel.y : ev.wheel.y;
				SDL_Scancode wheel_key;
				if (ui_wheel_moves(y, &wheel_key))
				{
					newkey = true;
					lastkey_scan = wheel_key;
					lastkey_mod = SDL_KMOD_NONE;
					return;
				}
				// (Over a data cube's text, it scrolls it: game_menu.c takes it.)
				if (ui_wheel_scrolls_text())
					mouse_wheel_pending += y;
				break;
			}

			case SDL_EVENT_TEXT_INPUT:
				dev_input_taken();  // (TYR3D_DUMP_KEYS)
				SDL_strlcpy(last_text, ev.text.text, COUNTOF(last_text));
				new_text = true;
				break;

			case SDL_EVENT_TEXT_EDITING:
				break;

			case SDL_EVENT_QUIT:
				/* TODO: Call the cleanup code here. */
				exit(0);
				break;
		}
	}
}

void JE_clearKeyboard(void)
{
	// /!\ Doesn't seems important. I think. D:
}
