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
#include "jukebox.h"

#include "font.h"
#include "joystick.h"
#include "jukebox3d.h"
#include "keyboard.h"
#include "layer3d.h"
#include "lds_play.h"
#include "loudness.h"
#include "mtrand.h"
#include "nortsong.h"
#include "opentyr.h"
#include "palette.h"
#include "sprite.h"
#include "starlib.h"
#include "ui.h"
#include "vga_palette.h"
#include "video.h"

#include <stdio.h>

void jukebox(void)  // FKA Setup.jukeboxGo
{
	bool trigger_quit = false,  // true when user wants to quit
	     quitting = false;
	
	bool hide_text = false;

	bool fade_looped_songs = true, fading_song = false;
	bool stopped = false;

	bool fx = false;
	int fx_num = 0;

	int palette_fade_steps = 15;

	int diff[256][3];
	init_step_fade_palette(diff, vga_palette, 0, 255);

	JE_starlib_init();

	int fade_volume = tyrMusicVolume;

	ui_take_press();  // (Tyrian3D: no click from before)

	// Tyrian3D: TYR3D_JUKEBOX=<song> (1-based) plays that song first.
	const int first_song = SDL_getenv("TYR3D_JUKEBOX") != NULL ? SDL_atoi(SDL_getenv("TYR3D_JUKEBOX")) : 0;
	if (first_song >= 1 && first_song <= MUSIC_NUM && !audio_disabled)
		play_song(first_song - 1);
	
	for (; ; )
	{
		if (!stopped && !audio_disabled)
		{
			if (songlooped && fade_looped_songs)
				fading_song = true;

			if (fading_song)
			{
				if (fade_volume > 5)
				{
					fade_volume -= 2;
				}
				else
				{
					fade_volume = tyrMusicVolume;

					fading_song = false;
				}

				set_volume(fade_volume, fxVolume);
			}

			if (!playing || (songlooped && fade_looped_songs && !fading_song))
				play_song(mt_rand() % MUSIC_NUM);
		}

		setDelay(1);

		SDL_FillSurfaceRect(VGAScreenSeg, NULL, 0);

		// starlib input needs to be rewritten
		JE_starlib_main();

		push_joysticks_as_keyboard();
		service_SDL_events(true);

		if (!hide_text)
		{
			char buffer[60];
			
			if (fx)
				snprintf(buffer, sizeof(buffer), "%d %s", fx_num + 1, soundTitle[fx_num]);
			else
				snprintf(buffer, sizeof(buffer), "%d %s", song_playing + 1, musicTitle[song_playing]);
			
			const int x = VGAScreen->w / 2;
			
			draw_font_hv(VGAScreen, x, 170, "Press ESC to quit the jukebox.",           small_font, centered, 1, 0);
			draw_font_hv(VGAScreen, x, 180, "Arrow keys change the song being played.", small_font, centered, 1, 0);
			draw_font_hv(VGAScreen, x, 190, buffer,                                     small_font, centered, 1, 4);
		}

		if (palette_fade_steps > 0)
			step_fade_palette(diff, palette_fade_steps--, 0, 255);

		// Tyrian3D: the jukebox for the modern UI (ui.h) over its stars.
		if (ui_modern())
		{
			UIMenu *ui = ui_menu_begin(UI_SCREEN_JUKEBOX, "");
			UIJukebox *j = &ui->jukebox;
			j->song = song_playing;
			j->song_count = MUSIC_NUM;
			j->sfx = fx;
			j->sfx_number = fx_num;
			j->sfx_count = SOUND_COUNT;
			SDL_strlcpy(j->sfx_title, soundTitle[fx_num], sizeof(j->sfx_title));
			j->hidden = hide_text;
			j->stopped = stopped;
			j->fading = fading_song;
			j->fade_looped = fade_looped_songs;
			if (l3d_enabled)
				SDL_strlcpy(j->look, jukebox3d_look_name(jukebox3d_look()), sizeof(j->look));
			ui->palette = vga_palette;  // (it fades in and out to its own palette)
			ui->selected = -1;
			ui_menu_publish(ui, VGAScreen, VGAScreen);
		}
		
		JE_showVGA();

		// (Tyrian3D: its visuals shown at the display's rate between the ticks.)
		if (ui_modern())
			video_wait_tick_ui();
		else
			wait_delay();

		// quit on mouse click
		Uint16 x, y;
		const JE_word button = JE_mousePosition(&x, &y);
		if (!ui_modern())
		{
			if (button > 0)
				trigger_quit = true;
		}
		else
		{
			// Tyrian3D: the modern UI's buttons and songs (its own: ui.h); the right button leaves.
			if (button == SDL_BUTTON_RIGHT)
				trigger_quit = true;
			const int action = ui_take_press();
			if (action >= UI_ACTION_ITEM && action < UI_ACTION_ITEM + MUSIC_NUM)
			{
				play_song(action - UI_ACTION_ITEM);
				stopped = false;
			}
			switch (action)
			{
			case UI_ACTION_BACK:
				trigger_quit = true;
				break;
			case UI_ACTION_PREV:
				play_song((song_playing > 0 ? song_playing : MUSIC_NUM) - 1);
				stopped = false;
				break;
			case UI_ACTION_NEXT:
				play_song((song_playing + 1) % MUSIC_NUM);
				stopped = false;
				break;
			case UI_ACTION_STOP:
				stop_song();
				stopped = true;
				break;
			case UI_ACTION_RESTART:
				restart_song();
				stopped = false;
				break;
			case UI_ACTION_FADE:
				fading_song = !fading_song;
				break;
			case UI_ACTION_FADE_LOOPED:
				fade_looped_songs = !fade_looped_songs;
				break;
			case UI_ACTION_SFX:
				fx = !fx;
				break;
			case UI_ACTION_PLAY_SFX:
				JE_playSampleNum(fx_num + 1);
				break;
			case UI_ACTION_LOOK:
				jukebox3d_next_look();
				break;
			default:
				break;
			}
		}

		if (newkey)
		{
			switch (lastkey_scan)
			{
			case SDL_SCANCODE_ESCAPE: // quit jukebox
			case SDL_SCANCODE_Q:
				trigger_quit = true;
				break;

			case SDL_SCANCODE_SPACE:
				hide_text = !hide_text;
				break;
			case SDL_SCANCODE_V:  // (Tyrian3D: the visuals' next look)
				if (ui_modern())
					jukebox3d_next_look();
				break;

			case SDL_SCANCODE_F:
				fading_song = !fading_song;
				break;
			case SDL_SCANCODE_N:
				fade_looped_songs = !fade_looped_songs;
				break;

			case SDL_SCANCODE_SLASH: // switch to sfx mode
				fx = !fx;
				break;
			case SDL_SCANCODE_COMMA:
				if (fx && --fx_num < 0)
					fx_num = SOUND_COUNT - 1;
				break;
			case SDL_SCANCODE_PERIOD:
				if (fx && ++fx_num >= SOUND_COUNT)
					fx_num = 0;
				break;
			case SDL_SCANCODE_SEMICOLON:
				if (fx)
					JE_playSampleNum(fx_num + 1);
				break;

			case SDL_SCANCODE_LEFT:
			case SDL_SCANCODE_UP:
				play_song((song_playing > 0 ? song_playing : MUSIC_NUM) - 1);
				stopped = false;
				break;
			case SDL_SCANCODE_RETURN:
			case SDL_SCANCODE_RIGHT:
			case SDL_SCANCODE_DOWN:
				play_song((song_playing + 1) % MUSIC_NUM);
				stopped = false;
				break;
			case SDL_SCANCODE_S: // stop song
				stop_song();
				stopped = true;
				break;
			case SDL_SCANCODE_R: // restart song
				restart_song();
				stopped = false;
				break;

			default:
				break;
			}
		}
		
		// user wants to quit, start fade-out
		if (trigger_quit && !quitting)
		{
			palette_fade_steps = 15;
			
			SDL_Color black = { 0, 0, 0 };
			init_step_fade_solid(diff, black, 0, 255);
			
			quitting = true;
		}
		
		// if fade-out finished, we can finally quit
		if (quitting && palette_fade_steps == 0)
			break;
	}

	set_volume(tyrMusicVolume, fxVolume);
	ui_screen_done();  // Tyrian3D
}
