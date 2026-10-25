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
#include "mainint.h"

#include "debugmode.h"

#include "backgrnd.h"
#include "config.h"
#include "devtools.h"
#include "editship.h"
#include "episodes.h"
#include "file.h"
#include "font.h"
#include "fonthand.h"
#include "game_menu.h"
#include "ui.h"
#include "helptext.h"
#include "helptext.h"
#include "joystick.h"
#include "keyboard.h"
#include "layer3d.h"
#include "lds_play.h"
#include "loudness.h"
#include "music_midi.h"
#include "models3d.h"
#include "rogue.h"
#include "volume3d.h"
#include "menus.h"
#include "mouse.h"
#include "mtrand.h"
#include "network.h"
#include "nortsong.h"
#include "nortvars.h"
#include "opentyr.h"
#include "palette.h"
#include "params.h"
#include "pcxmast.h"
#include "picload.h"
#include "player.h"
#include "shots.h"
#include "settings3d.h"
#include "sndmast.h"
#include "sprite.h"
#include "varz.h"
#include "vga256d.h"
#include "video.h"
#include "voiceover.h"

#include <assert.h>
#include <ctype.h>
#include <string.h>

bool button[4];

#define MAX_PAGE 8
#define TOPICS 6
const JE_byte topicStart[TOPICS] = { 0, 1, 2, 3, 7, 255 };

JE_shortint constantLastX;
JE_word textErase;
char text_window_message[128];  // Tyrian3D: the message JE_drawTextWindow last showed
JE_word upgradeCost;
JE_word downgradeCost;
JE_boolean performSave;
JE_boolean jumpSection;
JE_boolean useLastBank; /* See if I want to use the last 16 colors for DisplayText */

bool pause_pressed = false, ingamemenu_pressed = false;

/* Draws a message at the bottom text window on the playing screen */
void JE_drawTextWindow(const char *text)
{
	if (textErase > 0) // erase current text
		blit_sprite(VGAScreenSeg, 16, 189, OPTION_SHAPES, 36);  // in-game text area

	textErase = 100;
	SDL_strlcpy(text_window_message, text, sizeof(text_window_message));
	JE_outText(VGAScreenSeg, 20, 190, text, 0, 4);
}

static void plain_label(char *out, const char *in, size_t size);

/*
 * Tyrian3D: the story text being shown (JE_displayText), for the modern UI: its picture (the screen
 * before the text), which line the original reveals and how far, published before each frame shows.
 */
static struct
{
	bool on;
	int kind, score_lines;
	int line;              // the line being revealed (levelWarningLines: all, the prompt)
	int chars;             // and its characters revealed
	SDL_Surface *picture;  // the screen as it was before the text
} story;

static void story_publish(void)
{
	if (!ui_modern() || story.picture == NULL)
		return;
	UIMenu *ui = ui_menu_begin(UI_SCREEN_STORY, "");
	UIStory *s = &ui->story;
	s->kind = (UIStoryKind)story.kind;
	s->line_count = SDL_min((int)levelWarningLines, UI_STORY_LINES);
	for (int i = 0; i < s->line_count; ++i)
		SDL_strlcpy(s->lines[i], levelWarningText[i], sizeof(s->lines[i]));
	s->shown_line = SDL_min(story.line, s->line_count);
	s->shown_chars = story.chars;
	s->prompt = story.line >= levelWarningLines;
	s->top = warningRed;
	s->score_lines = story.score_lines;
	if (story.kind == UI_STORY_ENDING && episodeNum >= 1 && episodeNum <= EPISODE_MAX)
	{
		// The episode's name: "Episode 1: Escape" as its number and its name.
		const char *name = episode_name[episodeNum];
		const char *colon = strchr(name, ':');
		SDL_strlcpy(ui->title, colon != NULL ? colon + 1 : name, sizeof(ui->title));
		while (ui->title[0] == ' ')
			memmove(ui->title, ui->title + 1, strlen(ui->title));
		for (int i = (int)strlen(ui->title) - 1; i >= 0 && ui->title[i] == ' '; --i)
			ui->title[i] = '\0';
		snprintf(ui->crumb, sizeof(ui->crumb), "EPISODE %d COMPLETE", episodeNum);
	}
	ui->selected = -1;
	ui->wheel = UI_WHEEL_NONE;
	ui_menu_publish(ui, VGAScreen, story.picture);
}

void story_begin(int kind, int score_lines)
{
	// The text read aloud (voiceover.h): an ending's past its score lines and the blank line after them.
	voiceover_story(levelWarningText, kind == UI_STORY_ENDING ? score_lines + 1 : 0, levelWarningLines);

	story.on = ui_modern();
	if (!story.on)
		return;
	story.kind = kind;
	story.score_lines = score_lines;
	story.line = 0;
	story.chars = 0;
	if (story.picture == NULL)
		story.picture = SDL_CreateSurface(320, 200, SDL_PIXELFORMAT_INDEX8);
	if (story.picture != NULL)
		for (int y = 0; y < 200; ++y)
			memcpy((Uint8 *)story.picture->pixels + y * story.picture->pitch, (const Uint8 *)VGAScreen->pixels + y * VGAScreen->pitch, 320);
}

void story_line(int line)
{
	story.line = line;
	story.chars = 0;
}

void story_end(void)
{
	story.on = false;
	voiceover_stop();
}

void story_refresh(void)
{
	if (story.on)
		story_publish();
}

// The characters of the line being revealed so far, published as the frame shows.
static void story_shown(int chars)
{
	voiceover_update();
	if (!story.on)
		return;
	story.chars = chars;
	story_publish();
}

void card_publish(const char *crumb, const char *title, const char *const *lines, const char *code, const void *icon_sheet,
                  int icon_sprite, bool prompt, bool large)
{
	if (!ui_modern())
		return;
	UIMenu *ui = ui_menu_begin(UI_SCREEN_CARD, "");
	while (crumb != NULL && *crumb == ' ')
		++crumb;
	while (title != NULL && *title == ' ')
		++title;
	plain_label(ui->crumb, crumb != NULL ? crumb : "", sizeof(ui->crumb));
	for (char *k = ui->crumb; *k != '\0'; ++k)
		*k = (char)SDL_toupper(*k);
	plain_label(ui->title, title != NULL ? title : "", sizeof(ui->title));
	UICard *c = &ui->card;
	for (int i = 0; lines != NULL && lines[i] != NULL && c->line_count < UI_CARD_LINES; ++i)
		plain_label(c->lines[c->line_count++], lines[i], sizeof(c->lines[0]));
	if (code != NULL)
		plain_label(c->code, code, sizeof(c->code));
	c->icon_sheet = icon_sheet;
	c->icon_sprite = icon_sprite;
	c->prompt = prompt;
	c->large = large;
	ui->selected = -1;
	ui->wheel = UI_WHEEL_NONE;
	ui_menu_publish(ui, VGAScreen, VGAScreen);
}

void JE_outCharGlow(JE_word x, JE_word y, const char *s)
{
	JE_integer maxloc, loc, z;
	JE_shortint glowcol[60]; /* [1..60] */
	JE_shortint glowcolc[60]; /* [1..60] */
	JE_word textloc[60]; /* [1..60] */
	JE_byte bank;

	setDelay2(1);

	bank = (warningRed) ? 7 : ((useLastBank) ? 15 : 14);

	if (s[0] == '\0')
		return;

	if (frameCountMax == 0)
	{
		JE_textShade(VGAScreen, x, y, s, bank, 0, PART_SHADE);
		story_shown((int)strlen(s));  // Tyrian3D: the modern UI's (above)
		JE_showVGA();
	}
	else
	{
		maxloc = strlen(s);
		for (z = 0; z < 60; z++)
		{
			glowcol[z] = -8;
			glowcolc[z] = 1;
		}

		loc = x;
		for (z = 0; z < maxloc; z++)
		{
			textloc[z] = loc;

			int sprite_id = font_ascii[(unsigned char)s[z]];

			if (s[z] == ' ')
				loc += 6;
			else if (sprite_id != -1)
				loc += sprite(TINY_FONT, sprite_id)->width + 1;
		}

		for (loc = 0; (unsigned)loc < strlen(s) + 28; loc++)
		{
			if (!ESCPressed)
			{
				setDelay(frameCountMax);

				NETWORK_KEEP_ALIVE();

				int sprite_id = -1;

				for (z = loc - 28; z <= loc; z++)
				{
					if (z >= 0 && z < maxloc)
					{
						sprite_id = font_ascii[(unsigned char)s[z]];

						if (sprite_id != -1)
						{
							blit_sprite_hv(VGAScreen, textloc[z], y, TINY_FONT, sprite_id, bank, glowcol[z]);

							glowcol[z] += glowcolc[z];
							if (glowcol[z] > 9)
								glowcolc[z] = -1;
						}
					}
				}
				if (sprite_id != -1 && --z < maxloc)
					blit_sprite_dark(VGAScreen, textloc[z] + 1, y + 1, TINY_FONT, sprite_id, true);

				if (JE_anyButton())
					frameCountMax = 0;

				do
				{
					if (levelWarningDisplay)
						JE_updateWarning(VGAScreen);

					SDL_Delay(16);
				} while (!(getDelayTicks() == 0 || ESCPressed));

				story_shown(SDL_min(loc + 1, maxloc));  // Tyrian3D: the modern UI's (above)
				JE_showVGA();
			}
		}
	}
}

void JE_drawPortConfigButtons(void) // rear weapon pattern indicator
{
	if (twoPlayerMode)
		return;

	if (player[0].weapon_mode == 1)
	{
		blit_sprite(VGAScreenSeg, 285, 44, OPTION_SHAPES, 18);  // lit
		blit_sprite(VGAScreenSeg, 302, 44, OPTION_SHAPES, 19);  // unlit
	}
	else // == 2
	{
		blit_sprite(VGAScreenSeg, 285, 44, OPTION_SHAPES, 19);  // unlit
		blit_sprite(VGAScreenSeg, 302, 44, OPTION_SHAPES, 18);  // lit
	}
}

static bool helpSystemPage(Uint8 *topic, bool *restart);

void JE_helpSystem(JE_byte startTopic)
{
	if (shopSpriteSheet.data == NULL)
		JE_loadCompShapes(&shopSpriteSheet, '1');  // need mouse pointer sprites
	ui_take_press();  // (Tyrian3D: no click from before)

	Uint8 topic = startTopic;

	bool restart = true;

	const size_t menuItemsCount = COUNTOF(topicName) - 1;
	size_t selectedIndex = 0;

	const int xCenter = 320 / 2;
	const int yMenuHeader = 30;
	const int yMenuItems = 60;
	const int dyMenuItems = 20;
	const int hMenuItem = 13;
	int wMenuItem[COUNTOF(topicName) - 1] = { 0 };

	for (; ; )
	{
		if (restart)
		{
			play_song(SONG_MAPVIEW);

			JE_loadPic(VGAScreen2, 2, false);
		}

		if (topic > 1)
		{
			if (!helpSystemPage(&topic, &restart))
				return;

			selectedIndex = (size_t)topic - 1;
			topic = 1;
			continue;
		}

		// Restore background.
		memcpy(VGAScreen->pixels, VGAScreen2->pixels, (size_t)VGAScreen->pitch * VGAScreen->h);

		// Draw header.
		draw_font_hv_shadow(VGAScreen, xCenter, yMenuHeader, topicName[0], large_font, centered, 15, -3, false, 2);

		// Draw menu items.
		for (size_t i = 0; i < menuItemsCount; ++i)
		{
			const char *const text = topicName[i + 1];

			wMenuItem[i] = JE_textWidth(text, normal_font);
			const int y = yMenuItems + dyMenuItems * i;

			const bool selected = i == selectedIndex;

			draw_font_hv_shadow(VGAScreen, xCenter, y, text, normal_font, centered, 15, -3 + (selected ? 2 : 0), false, 2);
		}

		mouseCursor = MOUSE_POINTER_NORMAL;

		// Tyrian3D: the topics for the modern UI (ui.h), as setup's pages.
		if (ui_modern())
		{
			static const char *const hints[] = {
				"The store's menu in a game of one player.",
				"The menu between levels in a game of two players.",
				"Buying ships, weapons, shields, generators and sidekicks.",
				"Sound, the controls, loading and saving.",
				"Back to the title screen.",
			};
			UIMenu *ui = ui_menu_begin(UI_SCREEN_SETUP, "");
			plain_label(ui->title, topicName[0], sizeof(ui->title));
			plain_label(ui->crumb, menuText[3], sizeof(ui->crumb));
			for (char *c = ui->crumb; *c != '\0'; ++c)
				*c = (char)SDL_toupper(*c);
			for (size_t i = 0; i < menuItemsCount; ++i)
			{
				char label[48];
				plain_label(label, topicName[i + 1], sizeof(label));
				// ("EXIT HELP" as the others: only its first letter large.)
				if (label[0] != '\0' && SDL_isupper((unsigned char)label[1]))
					for (char *c = label + 1; *c != '\0'; ++c)
						*c = (char)SDL_tolower(*c);
				UIItem *it = ui_menu_add(ui, UI_ITEM_ACTION, label, xCenter - wMenuItem[i] / 2, yMenuItems + dyMenuItems * (int)i, wMenuItem[i],
				                         hMenuItem);
				if (i < COUNTOF(hints))
					SDL_strlcpy(it->hint, hints[i], sizeof(it->hint));
			}
			ui->selected = (int)selectedIndex;
			ui_menu_publish(ui, VGAScreen, VGAScreen2);
		}

		if (restart)
		{
			fade_palette(colors, 10, 0, 255);

			restart = false;
		}

		service_SDL_events(true);

		JE_mouseStart();
		JE_showVGA();
		JE_mouseReplace();

		bool mouseMoved = false;
		do
		{
			SDL_Delay(16);

			Uint16 oldMouseX = mouse_x;
			Uint16 oldMouseY = mouse_y;

			push_joysticks_as_keyboard();
			service_SDL_events(false);

			mouseMoved = mouse_x != oldMouseX || mouse_y != oldMouseY;
		} while (!(newkey || newmouse || mouseMoved));

		// Handle interaction.

		bool action = false;
		bool done = false;

		if (mouseMoved || newmouse)
		{
			// Find menu item that was hovered or clicked.
			for (size_t i = 0; i < menuItemsCount; ++i)
			{
				const int xMenuItem = xCenter - wMenuItem[i] / 2;
				if (mouse_x >= xMenuItem && mouse_x < xMenuItem + wMenuItem[i])
				{
					const int yMenuItem = yMenuItems + dyMenuItems * i;
					if (mouse_y >= yMenuItem && mouse_y < yMenuItem + hMenuItem)
					{
						if (selectedIndex != i)
						{
							JE_playSampleNum(S_CURSOR);

							selectedIndex = i;
						}

						if (newmouse && lastmouse_but == SDL_BUTTON_LEFT &&
						    lastmouse_x >= xMenuItem && lastmouse_x < xMenuItem + wMenuItem[i] &&
						    lastmouse_y >= yMenuItem && lastmouse_y < yMenuItem + hMenuItem)
						{
							action = true;
						}

						break;
					}
				}
			}
		}

		if (newmouse)
		{
			if (lastmouse_but == SDL_BUTTON_RIGHT)
			{
				JE_playSampleNum(S_SPRING);

				done = true;
			}
		}
		else if (newkey)
		{
			switch (lastkey_scan)
			{
			case SDL_SCANCODE_UP:
			{
				JE_playSampleNum(S_CURSOR);

				selectedIndex = selectedIndex == 0
					? menuItemsCount - 1
					: selectedIndex - 1;
				break;
			}
			case SDL_SCANCODE_DOWN:
			{
				JE_playSampleNum(S_CURSOR);

				selectedIndex = selectedIndex == menuItemsCount - 1
					? 0
					: selectedIndex + 1;
				break;
			}
			case SDL_SCANCODE_SPACE:
			case SDL_SCANCODE_RETURN:
			{
				action = true;
				break;
			}
			case SDL_SCANCODE_ESCAPE:
			{
				JE_playSampleNum(S_SPRING);

				done = true;
				break;
			}
			default:
				break;
			}
		}

		if (action)
		{
			JE_playSampleNum(S_SELECT);

			topic = selectedIndex + 2;

			if (selectedIndex == menuItemsCount - 1)
				done = true;
		}

		if (done)
		{
			fade_black(15);
			ui_screen_done();  // Tyrian3D

			return;
		}
	}
}

static bool helpSystemPage(Uint8 *topic, bool *restart)
{
	Uint8 page = topicStart[*topic - 1];

	const int xCenter = 320 / 2;

	for (; ; )
	{
		if (page == 0)
		{
			*topic = 1;
			return true;
		}
		else if (page > MAX_PAGE)
		{
			*topic = COUNTOF(topicName) - 1;
			return true;
		}

		for (Uint8 temp = 0; temp < COUNTOF(topicName); ++temp)
		{
			if (topicStart[temp] <= page)
				*topic = temp + 1;
			else
				break;
		}

		// Restore background.
		memcpy(VGAScreen->pixels, VGAScreen2->pixels, (size_t)VGAScreen->pitch * VGAScreen->h);

		fill_rectangle_wh(VGAScreen, 0, 192, 320, 8, 0);

		const char *const text = topicName[*topic - 1];

		// Draw header.
		draw_font_hv_shadow(VGAScreen, xCenter, 1, text, normal_font, centered, 15, -3, false, 2);

		// Draw footer.
		JE_char buffer[128];

		snprintf(buffer, sizeof buffer, "%s %d", miscText[24], page - topicStart[*topic - 1] + 1);
		draw_font_hv(VGAScreen, 10, 192, buffer, small_font, left_aligned, 13, 5);

		snprintf(buffer, sizeof buffer, "%s %d of %d", miscText[25], page, MAX_PAGE);
		draw_font_hv(VGAScreen, 320 - 10, 192, buffer, small_font, right_aligned, 13, 5);

		// Draw text.

		helpBoxBrightness = 3;
		verticalHeight = 8;

		switch (page)
		{
		case 1: /* One-Player Menu */
			JE_HBox(VGAScreen, 10,  20,  2, 60);
			JE_HBox(VGAScreen, 10,  50,  5, 60);
			JE_HBox(VGAScreen, 10,  80, 21, 60);
			JE_HBox(VGAScreen, 10, 110,  1, 60);
			JE_HBox(VGAScreen, 10, 140, 28, 60);
			break;
		case 2: /* Two-Player Menu */
			JE_HBox(VGAScreen, 10,  20,  1, 60);
			JE_HBox(VGAScreen, 10,  60,  2, 60);
			JE_HBox(VGAScreen, 10, 100, 21, 60);
			JE_HBox(VGAScreen, 10, 140, 28, 60);
			break;
		case 3: /* Upgrade Ship */
			JE_HBox(VGAScreen, 10,  20,  5, 60);
			JE_HBox(VGAScreen, 10,  70,  6, 60);
			JE_HBox(VGAScreen, 10, 110,  7, 60);
			break;
		case 4:
			JE_HBox(VGAScreen, 10,  20,  8, 60);
			JE_HBox(VGAScreen, 10,  55,  9, 60);
			JE_HBox(VGAScreen, 10,  87, 10, 60);
			JE_HBox(VGAScreen, 10, 120, 11, 60);
			JE_HBox(VGAScreen, 10, 170, 13, 60);
			break;
		case 5:
			JE_HBox(VGAScreen, 10,  20, 14, 60);
			JE_HBox(VGAScreen, 10,  80, 15, 60);
			JE_HBox(VGAScreen, 10, 120, 16, 60);
			break;
		case 6:
			JE_HBox(VGAScreen, 10,  20, 17, 60);
			JE_HBox(VGAScreen, 10,  40, 18, 60);
			JE_HBox(VGAScreen, 10, 130, 20, 60);
			break;
		case 7: /* Options */
			JE_HBox(VGAScreen, 10,  20, 21, 60);
			JE_HBox(VGAScreen, 10,  70, 22, 60);
			JE_HBox(VGAScreen, 10, 110, 23, 60);
			JE_HBox(VGAScreen, 10, 140, 24, 60);
			break;
		case 8:
			JE_HBox(VGAScreen, 10,  20, 25, 60);
			JE_HBox(VGAScreen, 10,  60, 26, 60);
			JE_HBox(VGAScreen, 10, 100, 27, 60);
			JE_HBox(VGAScreen, 10, 140, 28, 60);
			JE_HBox(VGAScreen, 10, 170, 29, 60);
			break;
		}

		helpBoxBrightness = 1;
		verticalHeight = 7;

		// Tyrian3D: the page for the modern UI (ui.h): its help texts (as the boxes above: their titles the
		// texts' highlighted words), its number; the original takes a click on either half of the screen.
		if (ui_modern())
		{
			static const Uint8 boxes[MAX_PAGE][5] = { { 2, 5, 21, 1, 28 }, { 1, 2, 21, 28 }, { 5, 6, 7 }, { 8, 9, 10, 11, 13 },
			                                          { 14, 15, 16 }, { 17, 18, 20 }, { 21, 22, 23, 24 }, { 25, 26, 27, 28, 29 } };
			UIMenu *ui = ui_menu_begin(UI_SCREEN_HELP, "");
			plain_label(ui->title, text, sizeof(ui->title));
			plain_label(ui->crumb, menuText[3], sizeof(ui->crumb));
			for (char *c = ui->crumb; *c != '\0'; ++c)
				*c = (char)SDL_toupper(*c);
			for (int b = 0; b < 5 && page >= 1 && page <= MAX_PAGE && boxes[page - 1][b] != 0 && ui->help.count < UI_HELP_PARTS; ++b)
			{
				const char *help = helpTxt[boxes[page - 1][b] - 1];
				char title[40] = "";
				const char *open = strchr(help, '~');
				const char *close = open != NULL ? strchr(open + 1, '~') : NULL;
				// (A title only where the text starts with its highlighted words.)
				if (open != NULL && close != NULL && open - help <= 1)
				{
					SDL_strlcpy(title, open + 1, SDL_min((size_t)(close - open), sizeof(title)));
					help = close + 1;
				}
				const int k = ui->help.count++;
				plain_label(ui->help.title[k], title, sizeof(ui->help.title[k]));
				while (*help != '\0' && (unsigned char)*help <= ' ')
					++help;
				plain_label(ui->help.text[k], help, sizeof(ui->help.text[k]));
			}
			UIPaging *pg = &ui->paging;
			pg->index = page - 1;
			pg->count = MAX_PAGE;
			pg->prev = pg->next = true;
			pg->hit_prev = (SDL_Rect){ 40, 90, 40, 20 };
			pg->hit_next = (SDL_Rect){ 240, 90, 40, 20 };
			snprintf(pg->label, sizeof(pg->label), "%s %d of %d", miscText[25], page, MAX_PAGE);
			ui->selected = -1;
			ui->wheel = UI_WHEEL_LEFT_RIGHT;
			ui_menu_publish(ui, VGAScreen, VGAScreen2);
		}

		if (*restart)
		{
			fade_palette(colors, 10, 0, 255);

			*restart = false;
		}

		do
		{
			mouseCursor = mouse_x < xCenter ? MOUSE_POINTER_LEFT : MOUSE_POINTER_RIGHT;

			service_SDL_events(true);

			JE_mouseStart();
			JE_showVGA();
			JE_mouseReplace();

			SDL_Delay(16);

			push_joysticks_as_keyboard();
			service_SDL_events(false);
		} while (!(newkey || newmouse));

		// Handle interaction.

		bool done = false;

		if (newmouse)
		{
			switch (lastmouse_but)
			{
			case SDL_BUTTON_LEFT:
			{
				JE_playSampleNum(S_CURSOR);

				if (mouse_x < xCenter)
					page -= 1;
				else
					page += 1;
				break;
			}
			case SDL_BUTTON_RIGHT:
			{
				JE_playSampleNum(S_SPRING);

				done = true;
				break;
			}
			default:
				break;
			}
		}
		else if (newkey)
		{
			switch (lastkey_scan)
			{
			case SDL_SCANCODE_LEFT:
			{
				JE_playSampleNum(S_CURSOR);

				page -= 1;
				break;
			}
			case SDL_SCANCODE_RIGHT:
			case SDL_SCANCODE_SPACE:
			case SDL_SCANCODE_RETURN:
			{
				JE_playSampleNum(S_CURSOR);

				page += 1;
				break;
			}
			case SDL_SCANCODE_ESCAPE:
			{
				JE_playSampleNum(S_SPRING);

				done = true;
				break;
			}
			default:
				break;
			}
		}

		if (done)
		{
			fade_black(15);
			ui_screen_done();  // Tyrian3D

			return false;
		}
	}
}

// cost to upgrade a weapon power from power-1 (where power == 0 indicates an unupgraded weapon)
long weapon_upgrade_cost(long base_cost, unsigned int power)
{
	assert(power <= 11);

	unsigned int temp = 0;

	// 0 1 3 6 10 15 21 29 ...
	for (; power > 0; power--)
		temp += power;

	return base_cost * temp;
}

ulong JE_getCost(JE_byte itemType, JE_word itemNum)
{
	long cost = 0;

	switch (itemType)
	{
	case 2:
		cost = (itemNum > 90) ? 100 : ships[itemNum].cost;
		break;
	case 3:
	case 4:
		cost = weaponPort[itemNum].cost;

		const uint port = itemType - 3,
		           item_power = player[0].items.weapon[port].power - 1;

		downgradeCost = weapon_upgrade_cost(cost, item_power);
		upgradeCost = weapon_upgrade_cost(cost, item_power + 1);
		break;
	case 5:
		cost = shields[itemNum].cost;
		break;
	case 6:
		cost = powerSys[itemNum].cost;
		break;
	case 7:
	case 8:
		cost = options[itemNum].cost;
		break;
	}

	return cost;
}

bool JE_loadScreen(void)
{
	if (shopSpriteSheet.data == NULL)
		JE_loadCompShapes(&shopSpriteSheet, '1');  // need mouse pointer and arrow sprites
	ui_take_press();  // (Tyrian3D: no click from before)

	bool restart = true;

	size_t playersIndex = 0;
	const size_t menuItemsCount = 12;
	size_t selectedIndex = 0;

	const int xCenter = 320 / 2;
	const int yMenuHeader = 5;
	const int xMenuItem = 10;
	const int xMenuItemName = xMenuItem;
	const int xMenuItemLastLevel = 120;
	const int xMenuItemEpisode = 250;
	const int wMenuItem = 300;
	const int yMenuItems = 30;
	const int dyMenuItems = 13;
	const int hMenuItem = 8;
	const int xLeftControl = 83;
	const int xRightControl = 213;
	const int wControl = 24;
	const int yControls = 179;

	for (; ; )
	{
		if (restart)
		{
			JE_loadPic(VGAScreen2, 2, false);
			fill_rectangle_wh(VGAScreen2, 0, 192, 320, 8, 0);
		}

		// Restore background.
		memcpy(VGAScreen->pixels, VGAScreen2->pixels, (size_t)VGAScreen->pitch * VGAScreen->h);

		// Draw header.
		draw_font_hv_shadow(VGAScreen, xCenter, yMenuHeader, miscText[38 + playersIndex], large_font, centered, 15, -3, false, 2);

		// Draw menu items.

		for (size_t i = 0; i < menuItemsCount; ++i)
		{
			const int y = yMenuItems + dyMenuItems * i;

			const bool selected = i == selectedIndex;

			if (i == menuItemsCount - 1)
			{
				JE_textShade(VGAScreen, xMenuItemName, y, miscText[33], 13, selected ? 6 : 2, FULL_SHADE);
				continue;
			}

			const JE_SaveFileType *const saveFile = &saveFiles[playersIndex * 11 + i];

			const bool disabled = saveFile->level == 0;

			char buffer[22];

			if (disabled)
			{
				JE_textShade(VGAScreen, xMenuItemName, y, miscText[2], 13, selected ? 6 : 0, FULL_SHADE);

				snprintf(buffer, sizeof buffer, "%s -----", miscTextB[2]);
				JE_textShade(VGAScreen, xMenuItemLastLevel, y, buffer, 5, selected ? 6 : 0, FULL_SHADE);
			}
			else
			{
				JE_textShade(VGAScreen, xMenuItemName, y, saveFile->name, 13, selected ? 6 : 2, FULL_SHADE);

				snprintf(buffer, sizeof buffer, "%s %s", miscTextB[2], saveFile->levelName);
				JE_textShade(VGAScreen, xMenuItemLastLevel, y, buffer, 5, selected ? 6 : 2, FULL_SHADE);

				snprintf(buffer, sizeof buffer, "%s %u", miscTextB[1], saveFile->episode);
				JE_textShade(VGAScreen, xMenuItemEpisode, y, buffer, 5, selected ? 6 : 2, FULL_SHADE);
			}
		}

		// Draw paging controls.

		const bool leftControlVisible = playersIndex > 0;
		const bool rightControlVisible = playersIndex < 1;

		if (leftControlVisible)
			blit_sprite2x2(VGAScreen, xLeftControl, yControls, shopSpriteSheet, 279);

		if (rightControlVisible)
			blit_sprite2x2(VGAScreen, xRightControl, yControls, shopSpriteSheet, 281);

		helpBoxColor = 15;
		JE_helpBox(VGAScreen, 103, 182, miscText[55], 25);

		// Tyrian3D: the slots for the modern UI (ui.h): the players' pages as tabs, each slot where the
		// original takes the mouse on it.
		if (ui_modern())
		{
			UIMenu *ui = ui_menu_begin(UI_SCREEN_LOAD, "");
			plain_label(ui->title, miscText[38 + playersIndex], sizeof(ui->title));
			plain_label(ui->crumb, menuText[1], sizeof(ui->crumb));
			for (char *c = ui->crumb; *c != '\0'; ++c)
				*c = (char)SDL_toupper(*c);
			for (size_t i = 0; i < menuItemsCount; ++i)
			{
				const int y = yMenuItems + dyMenuItems * (int)i;
				UIItem *it = ui_menu_add(ui, UI_ITEM_ACTION, "", xMenuItem, y, wMenuItem, hMenuItem);
				if (i == menuItemsCount - 1)
				{
					plain_label(it->label, miscText[33], sizeof(it->label));
					continue;
				}
				const JE_SaveFileType *const saveFile = &saveFiles[playersIndex * 11 + i];
				if (saveFile->level == 0)
				{
					plain_label(it->label, miscText[2], sizeof(it->label));
					it->disabled = true;
					continue;
				}
				plain_label(it->label, saveFile->name, sizeof(it->label));
				plain_label(it->value, saveFile->levelName, sizeof(it->value));
				snprintf(it->value2, sizeof(it->value2), "%s%u", miscTextB[0], saveFile->episode);
			}
			ui->selected = (int)selectedIndex;
			UIPaging *pg = &ui->paging;
			pg->index = (int)playersIndex;
			pg->count = 2;
			plain_label(pg->tab[0], miscText[46], sizeof(pg->tab[0]));
			plain_label(pg->tab[1], miscText[47], sizeof(pg->tab[1]));
			pg->tabs_click = true;
			pg->prev = leftControlVisible;
			pg->next = rightControlVisible;
			pg->hit_prev = (SDL_Rect){ xLeftControl, yControls, wControl, 200 - yControls };
			pg->hit_next = (SDL_Rect){ xRightControl, yControls, wControl, 200 - yControls };
			plain_label(ui->hint, miscText[55], sizeof(ui->hint));
			ui_menu_publish(ui, VGAScreen, VGAScreen2);  // (the picture without the paging's arrows)
		}

		if (restart)
		{
			mouseCursor = MOUSE_POINTER_NORMAL;

			fade_palette(colors, 10, 0, 255);

			restart = false;
		}

		service_SDL_events(true);

		JE_mouseStart();
		JE_showVGA();
		JE_mouseReplace();

		bool mouseMoved = false;
		do
		{
			SDL_Delay(16);

			Uint16 oldMouseX = mouse_x;
			Uint16 oldMouseY = mouse_y;

			push_joysticks_as_keyboard();
			service_SDL_events(false);

			mouseMoved = mouse_x != oldMouseX || mouse_y != oldMouseY;
		} while (!(newkey || newmouse || mouseMoved));

		// Handle interaction.

		bool leftAction = false;
		bool rightAction = false;
		bool action = false;
		bool done = false;

		// Tyrian3D: the other players' tab clicked on the modern UI (its own: ui.h); the pages toggle.
		const int tab = ui_take_press() - UI_ACTION_PAGE;
		if (tab >= 0 && tab < 2 && (size_t)tab != playersIndex)
		{
			JE_playSampleNum(S_CURSOR);
			leftAction = true;
		}

		if (mouseMoved || newmouse)
		{
			if (leftControlVisible &&
			    mouse_y >= yControls &&
			    mouse_x >= xLeftControl &&
			    mouse_x < xLeftControl + wControl)
			{
				if (newmouse && lastmouse_but == SDL_BUTTON_LEFT)
				{
					JE_playSampleNum(S_CURSOR);

					leftAction = true;
				}
			}
			else if (rightControlVisible &&
			         mouse_y >= yControls &&
			         mouse_x >= xRightControl &&
			         mouse_x < xRightControl + wControl)
			{
				if (newmouse && lastmouse_but == SDL_BUTTON_LEFT)
				{
					JE_playSampleNum(S_CURSOR);

					rightAction = true;
				}
			}
			else
			{
				// Find menu item that was hovered or clicked.
				if (mouse_x >= xMenuItem && mouse_x < xMenuItem + wMenuItem)
				{
					for (size_t i = 0; i < menuItemsCount; ++i)
					{
						const int yMenuItem = yMenuItems + dyMenuItems * i;
						if (mouse_y >= yMenuItem && mouse_y < yMenuItem + hMenuItem)
						{
							if (selectedIndex != i)
							{
								JE_playSampleNum(S_CURSOR);

								selectedIndex = i;
							}

							if (newmouse && lastmouse_but == SDL_BUTTON_LEFT &&
							    lastmouse_x >= xMenuItem && lastmouse_x < xMenuItem + wMenuItem &&
							    lastmouse_y >= yMenuItem && lastmouse_y < yMenuItem + hMenuItem)
							{
								action = true;
							}

							break;
						}
					}
				}
			}
		}

		if (newmouse)
		{
			if (lastmouse_but == SDL_BUTTON_RIGHT)
			{
				JE_playSampleNum(S_SPRING);

				done = true;
			}
		}
		else if (newkey)
		{
			switch (lastkey_scan)
			{
			case SDL_SCANCODE_LEFT:
			{
				JE_playSampleNum(S_CURSOR);

				leftAction = true;
				break;
			}
			case SDL_SCANCODE_RIGHT:
			{
				JE_playSampleNum(S_CURSOR);

				rightAction = true;
				break;
			}
			case SDL_SCANCODE_UP:
			{
				JE_playSampleNum(S_CURSOR);

				selectedIndex = selectedIndex == 0
					? menuItemsCount - 1
					: selectedIndex - 1;
				break;
			}
			case SDL_SCANCODE_DOWN:
			{
				JE_playSampleNum(S_CURSOR);

				selectedIndex = selectedIndex == menuItemsCount - 1
					? 0
					: selectedIndex + 1;
				break;
			}
			case SDL_SCANCODE_SPACE:
			case SDL_SCANCODE_RETURN:
			{
				action = true;
				break;
			}
			case SDL_SCANCODE_ESCAPE:
			{
				JE_playSampleNum(S_SPRING);

				done = true;
				break;
			}
			default:
				break;
			}
		}

		if (leftAction)
		{
			playersIndex = playersIndex == 0 ? 1 : 0;
		}
		else if (rightAction)
		{
			playersIndex = playersIndex == 1 ? 0 : 1;
		}
		else if (action)
		{
			if (selectedIndex == menuItemsCount - 1)  // "Exit to Main Menu"
			{
				JE_playSampleNum(S_SELECT);

				done = true;
			}
			else
			{
				const size_t saveFileIndex = playersIndex * 11 + selectedIndex;

				if (saveFiles[saveFileIndex].level == 0)  // "EMPTY SLOT"
				{
					JE_playSampleNum(S_CLINK);
				}
				else
				{
					JE_playSampleNum(S_SELECT);

					performSave = false;
					JE_operation(saveFileIndex + 1);

					fade_black(15);
					ui_screen_done();  // Tyrian3D

					return gameLoaded;
				}
			}
		}

		if (done)
		{
			fade_black(15);
			ui_screen_done();  // Tyrian3D

			return false;
		}
	}
}

ulong JE_totalScore(const Player *this_player)
{
	ulong temp = this_player->cash;

	temp += JE_getValue(2, this_player->items.ship);
	temp += JE_getValue(3, this_player->items.weapon[FRONT_WEAPON].id);
	temp += JE_getValue(4, this_player->items.weapon[REAR_WEAPON].id);
	temp += JE_getValue(5, this_player->items.shield);
	temp += JE_getValue(6, this_player->items.generator);
	temp += JE_getValue(7, this_player->items.sidekick[LEFT_SIDEKICK]);
	temp += JE_getValue(8, this_player->items.sidekick[RIGHT_SIDEKICK]);

	return temp;
}

JE_longint JE_getValue(JE_byte itemType, JE_word itemNum)
{
	long value = 0;

	switch (itemType)
	{
	case 2:
		value = ships[itemNum].cost;
		break;
	case 3:
	case 4:;
		const long base_value = weaponPort[itemNum].cost;

		// if two-player, use first player's front and second player's rear weapon
		const uint port = itemType - 3;
		const uint item_power = player[twoPlayerMode ? port : 0].items.weapon[port].power - 1;

		value = base_value;
		for (unsigned int i = 1; i <= item_power; ++i)
			value += weapon_upgrade_cost(base_value, i);
		break;
	case 5:
		value = shields[itemNum].cost;
		break;
	case 6:
		value = powerSys[itemNum].cost;
		break;
	case 7:
	case 8:
		value = options[itemNum].cost;
		break;
	}

	return value;
}

void JE_nextEpisode(void)
{
	strcpy(lastLevelName, "Completed");

	// Tyrian3D: a custom episode ends at the title screen (episodes.h), without a high score: its
	// board would be the original episode's. (JE_loadMap goes back to the title, as when the
	// store is quit.)
	if (custom_episode != 0)
	{
		gameLoaded = true;
		mainLevel = 0;
		return;
	}

	// Tyrian3D: episode 7 (the GBC levels) ends at the title screen too, without a high score (the save
	// file's 22 tables are the timed battles' and episodes 1-6's)
	if (episodeNum == EPISODE_GBC)
	{
		gameLoaded = true;
		mainLevel = 0;
		return;
	}

	if (episodeNum == initial_episode_num && !gameHasRepeated && !isNetworkGame && !constantPlay)
	{
		JE_highScoreCheck();
	}

	unsigned int newEpisode = JE_findNextEpisode();

	if (jumpBackToEpisode1)
	{
		if (episodeNum > 2 &&
			!constantPlay)
		{
			JE_playCredits();
		}

		// randomly give player the SuperCarrot
		if ((mt_rand() % 6) == 0)
		{
			player[0].items.ship = 2;                      // SuperCarrot
			player[0].items.weapon[FRONT_WEAPON].id = 23;  // Banana Blast
			player[0].items.weapon[REAR_WEAPON].id = 24;   // Banana Blast Rear

			for (uint i = 0; i < COUNTOF(player[0].items.weapon); ++i)
				player[0].items.weapon[i].power = 1;

			player[1].items.weapon[REAR_WEAPON].id = 24;   // Banana Blast Rear

			player[0].last_items = player[0].items;
		}
	}

	if (newEpisode != episodeNum)
		JE_initEpisode(newEpisode);

	gameLoaded = true;
	mainLevel = FIRST_LEVEL;
	saveLevel = FIRST_LEVEL;

	play_song(26);

	JE_clr256(VGAScreen);
	memcpy(colors, palettes[6-1], sizeof(colors));

	JE_dString(VGAScreen, JE_fontCenter(episode_name[episodeNum], SMALL_FONT_SHAPES), 130, episode_name[episodeNum], SMALL_FONT_SHAPES);
	JE_dString(VGAScreen, JE_fontCenter(miscText[5-1], SMALL_FONT_SHAPES), 185, miscText[5-1], SMALL_FONT_SHAPES);

	// Tyrian3D: the modern UI's card: "Episode 2: Treachery" as its number over its name.
	{
		const char *name = episode_name[episodeNum];
		const char *colon = strchr(name, ':');
		char crumb[32] = "";
		if (colon != NULL)
			SDL_strlcpy(crumb, name, SDL_min((size_t)(colon - name) + 1, sizeof(crumb)));
		card_publish(crumb, colon != NULL ? colon + 1 : name, NULL, NULL, NULL, 0, !constantPlay, true);
	}
	JE_showVGA();
	fade_palette(colors, 15, 0, 255);

	JE_wipeKey();
	if (!constantPlay)
	{
		do
		{
			NETWORK_KEEP_ALIVE();

			SDL_Delay(16);
		} while (!JE_anyButton());
	}

	fade_black(15);
	ui_screen_done();
}

void JE_initPlayerData(void)
{
	/* JE: New Game Items/Data */

	player[0].items.ship = 1;                     // USP Talon
	player[0].items.weapon[FRONT_WEAPON].id = 1;  // Pulse Cannon
	player[0].items.weapon[REAR_WEAPON].id = 0;   // None
	player[0].items.shield = 4;                   // Gencore High Energy Shield
	player[0].items.generator = 2;                // Advanced MR-12
	for (uint i = 0; i < COUNTOF(player[0].items.sidekick); ++i)
		player[0].items.sidekick[i] = 0;          // None
	player[0].items.special = 0;                  // None

	player[0].last_items = player[0].items;

	player[1].items = player[0].items;
	player[1].items.weapon[REAR_WEAPON].id = 15;  // Vulcan Cannon
	player[1].items.sidekick_level = 101;         // 101, 102, 103
	player[1].items.sidekick_series = 0;          // None

	gameHasRepeated = false;
	onePlayerAction = false;
	superArcadeMode = SA_NONE;
	superTyrian = false;
	twoPlayerMode = false;
	timedBattleMode = false;

	secretHint = (mt_rand() % 3) + 1;

	for (uint p = 0; p < COUNTOF(player); ++p)
	{
		for (uint i = 0; i < COUNTOF(player->items.weapon); ++i)
		{
			player[p].items.weapon[i].power = 1;
		}

		player[p].weapon_mode = 1;
		player[p].armor = ships[player[p].items.ship].dmg;

		player[p].is_dragonwing = (p == 1);
		player[p].lives = &player[p].items.weapon[p].power;

	}

	mainLevel = FIRST_LEVEL;
	saveLevel = FIRST_LEVEL;

	strcpy(lastLevelName, miscText[19]);
}

void JE_sortHighScores(void)
{
	T2KHighScoreType tempHiScore;
	for (int table = 0; table < 20; ++table)
	{
		if (t2kHighScores[table][1].score > t2kHighScores[table][0].score)
		{
			memcpy(&tempHiScore,             &t2kHighScores[table][0], sizeof(T2KHighScoreType));
			memcpy(&t2kHighScores[table][0], &t2kHighScores[table][1], sizeof(T2KHighScoreType));
			memcpy(&t2kHighScores[table][1], &tempHiScore,             sizeof(T2KHighScoreType));
		}
		if (t2kHighScores[table][2].score > t2kHighScores[table][1].score)
		{
			memcpy(&tempHiScore,             &t2kHighScores[table][1], sizeof(T2KHighScoreType));
			memcpy(&t2kHighScores[table][1], &t2kHighScores[table][2], sizeof(T2KHighScoreType));
			memcpy(&t2kHighScores[table][2], &tempHiScore,             sizeof(T2KHighScoreType));
		}
		if (t2kHighScores[table][1].score > t2kHighScores[table][0].score)
		{
			memcpy(&tempHiScore,             &t2kHighScores[table][0], sizeof(T2KHighScoreType));
			memcpy(&t2kHighScores[table][0], &t2kHighScores[table][1], sizeof(T2KHighScoreType));
			memcpy(&t2kHighScores[table][1], &tempHiScore,             sizeof(T2KHighScoreType));
		}
	}
}

// Tyrian3D: a number with its thousands apart ("12 345").
static void group_digits(unsigned long value, char *out, size_t size)
{
	char digits[32];
	snprintf(digits, sizeof(digits), "%lu", value);
	const int n = (int)strlen(digits);
	size_t k = 0;
	for (int i = 0; i < n && k + 2 < size; ++i)
	{
		if (i > 0 && (n - i) % 3 == 0)
			out[k++] = ' ';
		out[k++] = digits[i];
	}
	out[k] = '\0';
}

// Tyrian3D: a table of the high scores for the modern UI (ui.h): its three entries of a board.
static void scores_table(UIScoreTable *t, const char *heading, int board)
{
	plain_label(t->heading, heading, sizeof(t->heading));
	for (char *c = t->heading; *c != '\0'; ++c)
		*c = (char)SDL_toupper(*c);
	t->count = UI_SCORE_ROWS;
	for (int i = 0; i < UI_SCORE_ROWS; ++i)
	{
		const T2KHighScoreType *h = &t2kHighScores[board][i];
		group_digits((unsigned long)SDL_max(h->score, 0), t->score[i], sizeof(t->score[i]));
		plain_label(t->name[i], h->playerName, sizeof(t->name[i]));
		const int rank = h->difficulty <= 10 ? h->difficulty : 0;
		plain_label(t->rank[i], difficultyNameB[rank], sizeof(t->rank[i]));
		t->tier[i] = rank;
	}
}

// Tyrian3D: the high scores' board as the modern UI shows it: its name, its tables, the boards as tabs
// (index of count; count 1: this one alone), the original's paging controls.
static UIMenu *scores_menu(const char *board, int index, int count, bool prev, bool next)
{
	UIMenu *ui = ui_menu_begin(UI_SCREEN_SCORES, "");
	plain_label(ui->title, board, sizeof(ui->title));
	plain_label(ui->crumb, miscText[50], sizeof(ui->crumb));
	for (char *c = ui->crumb; *c != '\0'; ++c)
		*c = (char)SDL_toupper(*c);
	UIPaging *pg = &ui->paging;
	pg->index = index;
	pg->count = count;
	if (count > 1)
	{
		// The episodes and the timed battles.
		for (int i = 0; i < count && i < UI_PAGES; ++i)
		{
			if (i < 5)
				snprintf(pg->tab[i], sizeof(pg->tab[i]), "%s %d", miscTextB[1], i + 1);
			else
				plain_label(pg->tab[i], timed_battle_name[i - 4], sizeof(pg->tab[i]));
		}
		pg->tabs_click = true;
	}
	pg->prev = prev;
	pg->next = next;
	pg->hit_prev = (SDL_Rect){ 83, 179, 24, 21 };
	pg->hit_next = (SDL_Rect){ 213, 179, 24, 21 };
	ui->scores.new_table = ui->scores.new_row = -1;
	ui->selected = -1;
	ui->wheel = UI_WHEEL_LEFT_RIGHT;
	return ui;
}

void JE_highScoreScreen(void)
{
	if (shopSpriteSheet.data == NULL)
		JE_loadCompShapes(&shopSpriteSheet, '1');  // need mouse pointer and arrow sprites
	ui_take_press();  // (Tyrian3D: no click from before)

	bool restart = true;

	size_t episodeIndex = 0;
	// Five episodes, three timed battles
	const size_t episodeCount = 8;

	const int xCenter = 320 / 2;
	const int yMenuHeader = 3;
	const int yEpisodeHeader = 30;
	const int xLeftControl = 83;
	const int xRightControl = 213;
	const int wControl = 24;
	const int yControls = 179;

	char buffer[64];
	int boardOnePlayer, boardTwoPlayer;

	for (; ; )
	{
		if (restart)
		{
			JE_loadPic(VGAScreen2, 2, false);
			fill_rectangle_wh(VGAScreen2, 0, 192, 320, 8, 0);

			// Draw header.
			draw_font_hv_shadow(VGAScreen2, xCenter, yMenuHeader, miscText[50], large_font, centered, 15, -3, false, 2);
		}

		// Restore background and header.
		memcpy(VGAScreen->pixels, VGAScreen2->pixels, (size_t)VGAScreen->pitch * VGAScreen->h);

		if (episodeIndex < 5)
		{
			snprintf(buffer, sizeof(buffer), "%s", episode_name[episodeIndex + 1]);

			// Regular episode boards
			boardOnePlayer = 10 + (episodeIndex * 2);
			boardTwoPlayer = 11 + (episodeIndex * 2);
		}
		else
		{
			snprintf(buffer, sizeof(buffer), "%s %s", timed_battle_name[0], timed_battle_name[episodeIndex - 4]);

			// Timed Battle boards
			boardOnePlayer = episodeIndex - 5;
			boardTwoPlayer = -1;
		}

		// Draw episode header.
		draw_font_hv_shadow(VGAScreen, xCenter, yEpisodeHeader, buffer, normal_font, centered, 15, -3, false, 2);

		// Draw 1-player scores.
		draw_font_hv_shadow(VGAScreen, xCenter, 55, miscText[46], normal_font, centered, 15, -3, false, 2);

		for (Uint8 i = 0; i < 3; ++i)
		{
			const int y = 75 + 10 * i;

			if (t2kHighScores[boardOnePlayer][i].difficulty > 9)
				t2kHighScores[boardOnePlayer][i].difficulty = 0;

			const int rank = t2kHighScores[boardOnePlayer][i].difficulty;
			const int score = t2kHighScores[boardOnePlayer][i].score;
			const char *playerName = t2kHighScores[boardOnePlayer][i].playerName;

			snprintf(buffer, sizeof buffer, "~#%d:~  %d", i + 1, score);
			JE_textShade(VGAScreen, 20, y, buffer, 15, 0, FULL_SHADE);
			JE_textShade(VGAScreen, 110, y, playerName, 15, 2, FULL_SHADE);
			JE_textShade(VGAScreen, 250, y, difficultyNameB[rank], 15, rank + (rank == 0 ? 0 : -1), FULL_SHADE);
		}

		// Draw 2-player scores.
		if (boardTwoPlayer >= 0)
		{
			draw_font_hv_shadow(VGAScreen, xCenter, 120, miscText[47], normal_font, centered, 15, -3, false, 2);

			for (Uint8 i = 0; i < 3; ++i)
			{
				const int y = 135 + 10 * i;

				if (t2kHighScores[boardTwoPlayer][i].difficulty > 9)
					t2kHighScores[boardTwoPlayer][i].difficulty = 0;

				const int rank = t2kHighScores[boardTwoPlayer][i].difficulty;
				const int score = t2kHighScores[boardTwoPlayer][i].score;
				const char *teamName = t2kHighScores[boardTwoPlayer][i].playerName;

				snprintf(buffer, sizeof buffer, "~#%d:~  %d", i + 1, score);
				JE_textShade(VGAScreen, 20, y, buffer, 15, 0, FULL_SHADE);
				JE_textShade(VGAScreen, 110, y, teamName, 15, 2, FULL_SHADE);
				JE_textShade(VGAScreen, 250, y, difficultyNameB[rank], 15, rank + (rank == 0 ? 0 : -1), FULL_SHADE);
			}			
		}

		// Draw paging controls.

		const bool leftControlVisible = episodeIndex > 0;
		const bool rightControlVisible = episodeIndex < episodeCount - 1;

		if (leftControlVisible)
			blit_sprite2x2(VGAScreen, xLeftControl, yControls, shopSpriteSheet, 279);

		if (rightControlVisible)
			blit_sprite2x2(VGAScreen, xRightControl, yControls, shopSpriteSheet, 281);

		helpBoxColor = 15;
		JE_helpBox(VGAScreen, 103, 182, miscText[56], 25);

		// Tyrian3D: the board for the modern UI (ui.h).
		if (ui_modern())
		{
			UIMenu *ui = scores_menu(buffer, (int)episodeIndex, (int)episodeCount, leftControlVisible, rightControlVisible);
			if (episodeIndex < 5)
				snprintf(ui->title, sizeof(ui->title), "%s", episode_name[episodeIndex + 1]);
			else
				snprintf(ui->title, sizeof(ui->title), "%s %s", timed_battle_name[0], timed_battle_name[episodeIndex - 4]);
			plain_label(ui->title, ui->title, sizeof(ui->title));
			scores_table(&ui->scores.table[ui->scores.table_count++], miscText[46], boardOnePlayer);
			if (boardTwoPlayer >= 0)
				scores_table(&ui->scores.table[ui->scores.table_count++], miscText[47], boardTwoPlayer);
			plain_label(ui->hint, miscText[56], sizeof(ui->hint));
			ui_menu_publish(ui, VGAScreen, VGAScreen2);  // (the picture without the paging's arrows)
		}

		if (restart)
		{
			mouseCursor = MOUSE_POINTER_NORMAL;

			fade_palette(colors, 10, 0, 255);

			restart = false;
		}

		do
		{
			service_SDL_events(true);

			JE_mouseStart();
			JE_showVGA();
			JE_mouseReplace();

			SDL_Delay(16);

			push_joysticks_as_keyboard();
			service_SDL_events(false);
		} while (!(newkey || newmouse));

		// Handle interaction.

		bool leftAction = false;
		bool rightAction = false;
		bool done = false;

		// Tyrian3D: a board's tab clicked on the modern UI (its own: ui.h).
		const int tab = ui_take_press() - UI_ACTION_PAGE;
		if (tab >= 0 && tab < (int)episodeCount)
		{
			JE_playSampleNum(S_CURSOR);
			episodeIndex = (size_t)tab;
			continue;
		}

		if (newmouse)
		{
			switch (lastmouse_but)
			{
			case SDL_BUTTON_LEFT:
			{
				if (leftControlVisible &&
				    mouse_y >= yControls &&
				    mouse_x >= xLeftControl &&
				    mouse_x < xLeftControl + wControl)
				{
					JE_playSampleNum(S_CURSOR);

					leftAction = true;
				}
				else if (rightControlVisible &&
				         mouse_y >= yControls &&
				         mouse_x >= xRightControl &&
				         mouse_x < xRightControl + wControl)
				{
					JE_playSampleNum(S_CURSOR);

					rightAction = true;
				}
				break;
			}
			case SDL_BUTTON_RIGHT:
			{
				JE_playSampleNum(S_SPRING);

				done = true;
				break;
			}
			default:
				break;
			}
		}
		else if (newkey)
		{
			switch (lastkey_scan)
			{
			case SDL_SCANCODE_LEFT:
			{
				JE_playSampleNum(S_CURSOR);

				leftAction = true;
				break;
			}
			case SDL_SCANCODE_RIGHT:
			{
				JE_playSampleNum(S_CURSOR);

				rightAction = true;
				break;
			}
			case SDL_SCANCODE_SPACE:
			case SDL_SCANCODE_RETURN:
			case SDL_SCANCODE_ESCAPE:
			{
				JE_playSampleNum(S_SPRING);

				done = true;
				break;
			}
			default:
				break;
			}
		}

		if (leftAction)
		{
			episodeIndex = episodeIndex == 0
				? episodeCount - 1
				: episodeIndex - 1;
		}
		else if (rightAction)
		{
			episodeIndex = episodeIndex == episodeCount - 1
				? 0
				: episodeIndex + 1;
		}

		if (done)
		{
			fade_black(15);
			ui_screen_done();  // Tyrian3D

			return;
		}
	}
}

void JE_gammaCorrect_func(JE_byte *col, JE_real r)
{
	int temp = roundf(*col * r);
	if (temp > 255)
	{
		temp = 255;
	}
	*col = temp;
}

void JE_gammaCorrect(Palette *colorBuffer, JE_byte gamma)
{
	int x;
	JE_real r = 1 + (JE_real)gamma / 10;

	for (x = 0; x < 256; x++)
	{
		JE_gammaCorrect_func(&(*colorBuffer)[x].r, r);
		JE_gammaCorrect_func(&(*colorBuffer)[x].g, r);
		JE_gammaCorrect_func(&(*colorBuffer)[x].b, r);
	}
}

JE_boolean JE_gammaCheck(void)
{
	bool temp = keysactive[SDL_SCANCODE_F11] != 0;
	if (temp)
	{
		keysactive[SDL_SCANCODE_F11] = false;
		newkey = false;
		gammaCorrection = (gammaCorrection + 1) % 4;
		memcpy(colors, palettes[pcxpal[3-1]], sizeof(colors));
		JE_gammaCorrect(&colors, gammaCorrection);
		set_palette(colors, 0, 255);
	}
	return temp;
}

void JE_doInGameSetup(void)
{
	mouseSetRelative(false);

	haltGame = false;

#ifdef WITH_NETWORK
	if (isNetworkGame)
	{
		network_prepare(PACKET_GAME_MENU);
		network_send(4);  // PACKET_GAME_MENU

		while (true)
		{
			service_SDL_events(false);

			if (packet_in[0] && SDLNet_Read16(&packet_in[0]->data[0]) == PACKET_GAME_MENU)
			{
				network_update();
				break;
			}

			network_update();
			network_check();

			SDL_Delay(16);
		}
	}
#endif

	if (yourInGameMenuRequest)
	{
		if (JE_inGameSetup())
		{
			reallyEndLevel = true;
			playerEndLevel = true;
		}
		quitRequested = false;

		keysactive[SDL_SCANCODE_ESCAPE] = false;

#ifdef WITH_NETWORK
		if (isNetworkGame)
		{
			if (!playerEndLevel)
			{
				network_prepare(PACKET_WAITING);
				network_send(4);  // PACKET_WAITING
			}
			else
			{
				network_prepare(PACKET_GAME_QUIT);
				network_send(4);  // PACKET_GAMEQUIT
			}
		}
#endif
	}

#ifdef WITH_NETWORK
	if (isNetworkGame)
	{
		SDL_Surface *temp_surface = VGAScreen;
		VGAScreen = VGAScreenSeg; /* side-effect of game_screen */

		if (!yourInGameMenuRequest)
		{
			JE_barShade(VGAScreen, 3, 60, 257, 80); /*Help Box*/
			JE_barShade(VGAScreen, 5, 62, 255, 78);
			JE_dString(VGAScreen, 10, 65, "Other player in options menu.", SMALL_FONT_SHAPES);
			JE_showVGA();

			while (true)
			{
				service_SDL_events(false);
				JE_showVGA();

				if (packet_in[0])
				{
					if (SDLNet_Read16(&packet_in[0]->data[0]) == PACKET_WAITING)
					{
						network_check();
						break;
					}
					else if (SDLNet_Read16(&packet_in[0]->data[0]) == PACKET_GAME_QUIT)
					{
						reallyEndLevel = true;
						playerEndLevel = true;

						network_check();
						break;
					}
				}

				network_update();
				network_check();

				SDL_Delay(16);
			}
		}
		else
		{
			/*
			JE_barShade(3, 160, 257, 180); /-*Help Box*-/
			JE_barShade(5, 162, 255, 178);
			tempScreenSeg = VGAScreen;
			JE_dString(VGAScreen, 10, 165, "Waiting for other player.", SMALL_FONT_SHAPES);
			JE_showVGA();
			*/
		}

		while (!network_is_sync())
		{
			service_SDL_events(false);

			network_check();
			SDL_Delay(16);
		}

		VGAScreen = temp_surface; /* side-effect of game_screen */
	}
#endif

	yourInGameMenuRequest = false;

	//skipStarShowVGA = true;

	mouseSetRelative(true);
}

/*
 * Tyrian3D: the modern settings (settings3d.h, as the setup menu's "3D" and "Music") in a level. The
 * in-game options show the graphics on a page of their own ("Graphics", with the original's detail
 * level), the mouse and the music beside the volumes. The graphics page is drawn in that menu's box;
 * with the modern menus at the side of the playfield, the 3D view behind it bright, so what each
 * change does shows at once. Each value turns by Left/Right, Enter or a click; Escape, a right click
 * or "Done" go back. They take effect at once and are saved as from the setup menu.
 */
enum
{
	OPT_VIEW, OPT_OBJECTS, OPT_SHADOWS, OPT_EFFECTS, OPT_CAMERA, OPT_MOUSE, OPT_HUD, OPT_PLAYFIELD, OPT_MUSIC, OPT_MENUS,
	OPT_SCREENS, OPT_UI_SCALE, OPT_DETAIL, OPT_SOUNDFONT, OPT_DONE,
	OPT_COUNT
};

// The graphics page's rows.
static const int graphics_page[] = {
	OPT_VIEW, OPT_OBJECTS, OPT_SHADOWS, OPT_EFFECTS, OPT_CAMERA, OPT_HUD, OPT_PLAYFIELD, OPT_MENUS, OPT_SCREENS, OPT_UI_SCALE,
	OPT_DETAIL, OPT_DONE,
};

static const char *const option_names[OPT_COUNT] = {
	"View", "Objects", "Shadows", "Effects", "Camera", "Mouse", "HUD", "Playfield", "Music", "Menus", "Screens", "UI Scale",
	"Detail Level", "SoundFont", "Done",
};

static const char *const option_help[OPT_COUNT] = {
	"Play in 3D or on the original screen.",
	"Ships and enemies in 3D, or flat sprites.",
	"Shadows of ships and enemies.",
	"Explosion particles and glowing shots.",
	"How the 3D camera looks at the playfield.",
	"The ship moves as far as the mouse, or as in the original.",
	"A few gauges over the playfield, or the original panel.",
	"All the 3D view shows, or the original's screen (next level).",
	"The music through a SoundFont, or on the AdLib chip.",
	"Menus in the new style over the 3D view, or the original screens.",
	"The game's other screens fill the window's height, or in whole steps.",
	"The size of the new menus and the HUD.",
	"The original's detail: its water, blur and light effects.",
	"The instruments the music plays on: the SoundFonts in data/soundfonts.",
	"Return to the options.",
};

// Tyrian3D: a text of the game without its highlight marks ('~') and trailing spaces and colon.
static void plain_label(char *out, const char *in, size_t size)
{
	size_t n = 0;
	for (; *in != '\0' && n + 1 < size; ++in)
		if (*in != '~')
			out[n++] = *in;
	out[n] = '\0';
	while (n > 0 && (out[n - 1] == ' ' || out[n - 1] == ':'))
		out[--n] = '\0';
}

static const char *option_value(int option)
{
	switch (option)
	{
	case OPT_VIEW:    return settings3d.view_3d ? "3D" : "Original 2D";
	case OPT_OBJECTS: return settings3d.models ? "3D" : "Flat sprites";
	case OPT_SHADOWS: return settings3d.shadows ? "On" : "Off";
	case OPT_EFFECTS: return settings3d.effects ? "On" : "Off";
	case OPT_CAMERA:  return settings3d_camera_name(settings3d.camera);
	case OPT_MOUSE:   return settings3d.mouse_direct ? "Direct" : "Original";
	case OPT_HUD:     return settings3d.hud_modern ? "Modern" : "Classic";
	case OPT_PLAYFIELD: return settings3d.playfield_wide ? "Wide" : "Original";
	case OPT_MUSIC:   return settings3d.music_midi ? (music_midi_available() ? "SoundFont" : "SoundFont (none)") : "AdLib";
	case OPT_MENUS:   return settings3d.menus_modern ? "Modern" : "Classic";
	case OPT_SCREENS: return settings3d.screens_fill ? "Fill" : "Integer";
	case OPT_UI_SCALE:
	{
		static char percent[16];
		snprintf(percent, sizeof(percent), "%d%%", settings3d.ui_scale);
		return percent;
	}
	case OPT_SOUNDFONT:
		return music_midi_soundfont()[0] != '\0' ? music_midi_soundfont() : "None";
	case OPT_DETAIL:
	{
		static char detail[16];
		plain_label(detail, detailLevel[processorType - 1], sizeof(detail));
		return detail;
	}
	default:          return NULL;
	}
}

// Turns an option to its next (or previous) value.
static void option_turn(int option, int step)
{
	switch (option)
	{
	case OPT_VIEW:
		settings3d.view_3d = !settings3d.view_3d;
		settings3d_changed(S3D_VIEW);
		settings3d_apply();
		break;
	case OPT_OBJECTS:
		settings3d.models = !settings3d.models;
		settings3d_changed(S3D_MODELS);
		settings3d_apply();
		break;
	case OPT_SHADOWS:
		settings3d.shadows = !settings3d.shadows;
		settings3d_changed(S3D_SHADOWS);
		break;
	case OPT_EFFECTS:
		settings3d.effects = !settings3d.effects;
		settings3d_changed(S3D_EFFECTS);
		break;
	case OPT_CAMERA:
	{
		const int count = settings3d_camera_count();
		settings3d.camera = (settings3d.camera + step + count) % count;
		settings3d_changed(S3D_CAMERA);
		settings3d_apply();
		break;
	}
	case OPT_MOUSE:
		settings3d.mouse_direct = !settings3d.mouse_direct;
		settings3d_changed(S3D_MOUSE);
		break;
	case OPT_HUD:
		settings3d.hud_modern = !settings3d.hud_modern;
		settings3d_changed(S3D_HUD);
		break;
	case OPT_PLAYFIELD:
		settings3d.playfield_wide = !settings3d.playfield_wide;  // (from the next level)
		settings3d_changed(S3D_PLAYFIELD);
		break;
	case OPT_MUSIC:
		settings3d.music_midi = !settings3d.music_midi;
		settings3d_changed(S3D_MUSIC);
		settings3d_apply();
		break;
	case OPT_MENUS:
		settings3d.menus_modern = !settings3d.menus_modern;
		settings3d_changed(S3D_MENUS);
		break;
	case OPT_SCREENS:
		settings3d.screens_fill = !settings3d.screens_fill;
		settings3d_changed(S3D_SCREENS);
		break;
	case OPT_UI_SCALE:
	{
		const int count = settings3d_ui_scale_count();
		const int i = settings3d_ui_scale_index(settings3d.ui_scale);
		settings3d.ui_scale = settings3d_ui_scale_value((i + step + count) % count);
		settings3d_changed(S3D_UI_SCALE);
		break;
	}
	case OPT_SOUNDFONT:
	{
		const int count = music_midi_soundfont_count();
		int i = 0;
		while (i < count && SDL_strcasecmp(music_midi_soundfont_name(i), music_midi_soundfont()) != 0)
			++i;
		if (count == 0)
			break;
		const char *name = music_midi_soundfont_name(((i < count ? i : 0) + step + count) % count);
		if (music_midi_use(name))
		{
			SDL_strlcpy(settings3d.soundfont, name, sizeof(settings3d.soundfont));
			settings3d_changed(S3D_SOUNDFONT);
		}
		break;
	}
	case OPT_DETAIL:  // (as the original's in-game options turned it)
		if (step > 0)
			processorType = processorType < 4 ? processorType + 1 : 1;
		else
			processorType = processorType > 1 ? processorType - 1 : 4;
		JE_initProcessorType();
		JE_setNewGameSpeed();
		break;
	default:
		break;
	}
}

// The level's name as the modern UI's screens over it show it.
static void level_crumb(char *out, size_t size)
{
	plain_label(out, levelName, size);
	for (char *c = out; *c != '\0'; ++c)
		*c = (char)SDL_toupper(*c);
}

// background: the in-game options' screen with their boxes (VGAScreen2), drawn on each time.
static void ingame_options_3d(void)
{
	enum { ROWS = (int)COUNTOF(graphics_page) };
	const int yItems = 16, dyItems = 9, hItem = 9;  // (Tyrian3D: 12 rows in the box)
	const int xName = 10, wName = 80, xValue = xName + wName, wValue = 120;
	int selected = 0;

	for (bool done = false; !done; )
	{
		memcpy(VGAScreen->pixels, VGAScreen2->pixels, (size_t)VGAScreen->pitch * VGAScreen->h);
		for (int i = 0; i < ROWS; ++i)
		{
			const int y = yItems + dyItems * i;
			const int brightness = -4 + (i == selected ? 2 : 0);
			// (The shadow a pixel off, not two: the rows are close.)
			draw_font_hv_shadow(VGAScreen, xName, y, option_names[graphics_page[i]], normal_font, left_aligned, 15, brightness, false, 1);
			const char *value = option_value(graphics_page[i]);
			if (value != NULL)
				draw_font_hv_shadow(VGAScreen, xValue, y, value, normal_font, left_aligned, 15, brightness, false, 1);
		}
		JE_outTextAdjust(VGAScreen, 10, 147, option_help[graphics_page[selected]], 14, 6, TINY_FONT, true);

		// Tyrian3D: the page for the modern UI (ui.h): each row where the original takes the mouse on it.
		if (ui_modern())
		{
			UIMenu *ui = ui_menu_begin(UI_SCREEN_LEVEL_MENU, "Graphics");
			SDL_strlcpy(ui->crumb, "OPTIONS", sizeof(ui->crumb));
			ui->values_turn = true;
			ui->enter_turns = true;
			ui->preview = true;
			for (int i = 0; i < ROWS; ++i)
			{
				const int option = graphics_page[i];
				const char *value = option_value(option);
				UIItem *it = ui_menu_add(ui, value != NULL ? UI_ITEM_CHOICE : UI_ITEM_ACTION, option_names[option], xName,
				                         yItems + dyItems * i, wName + wValue, hItem);
				if (value != NULL)
					SDL_strlcpy(it->value, value, sizeof(it->value));
				SDL_strlcpy(it->hint, option_help[option], sizeof(it->hint));
			}
			ui->selected = selected;
			ui->nowhere = (SDL_Point){ 300, 190 };
			ui_menu_publish(ui, VGAScreen, VGAScreen2);
		}

		service_SDL_events(true);
		JE_mouseStart();
		JE_showVGA();
		JE_mouseReplace();

		bool mouseMoved = false;
		do
		{
			SDL_Delay(16);
			const Uint16 oldMouseX = mouse_x, oldMouseY = mouse_y;
			push_joysticks_as_keyboard();
			service_SDL_events(false);
			NETWORK_KEEP_ALIVE();
			mouseMoved = mouse_x != oldMouseX || mouse_y != oldMouseY;
		} while (!(newkey || newmouse || mouseMoved));

		int step = 0;  // turn the selected option by this, or act on "Done"
		if ((mouseMoved || newmouse) && mouse_x >= xName && mouse_x < xValue + wValue)
		{
			for (int i = 0; i < ROWS; ++i)
			{
				const int y = yItems + dyItems * i;
				if (mouse_y >= y && mouse_y < y + hItem)
				{
					if (selected != i)
						JE_playSampleNum(S_CURSOR);
					selected = i;
					if (newmouse && lastmouse_but == SDL_BUTTON_LEFT && lastmouse_y >= y && lastmouse_y < y + hItem)
						step = 1;
					break;
				}
			}
		}
		if (newmouse && lastmouse_but == SDL_BUTTON_RIGHT)
		{
			JE_playSampleNum(S_SPRING);
			done = true;
		}
		else if (newkey)
		{
			switch (lastkey_scan)
			{
			case SDL_SCANCODE_UP:
				JE_playSampleNum(S_CURSOR);
				selected = (selected + ROWS - 1) % ROWS;
				break;
			case SDL_SCANCODE_DOWN:
				JE_playSampleNum(S_CURSOR);
				selected = (selected + 1) % ROWS;
				break;
			case SDL_SCANCODE_LEFT:
				if (graphics_page[selected] != OPT_DONE)
					step = -1;
				break;
			case SDL_SCANCODE_RIGHT:
				if (graphics_page[selected] != OPT_DONE)
					step = 1;
				break;
			case SDL_SCANCODE_W:  // (the original's secret wild detail)
				if (graphics_page[selected] == OPT_DETAIL)
				{
					processorType = 6;
					JE_initProcessorType();
				}
				break;
			case SDL_SCANCODE_SPACE:
			case SDL_SCANCODE_RETURN:
				step = 1;
				break;
			case SDL_SCANCODE_ESCAPE:
				JE_playSampleNum(S_SPRING);
				done = true;
				break;
			default:
				break;
			}
		}

		if (step != 0)
		{
			if (graphics_page[selected] == OPT_DONE)
			{
				JE_playSampleNum(S_SELECT);
				done = true;
			}
			else
			{
				JE_playSampleNum(S_CLICK);
				option_turn(graphics_page[selected], step);
			}
		}
	}
	keysactive[SDL_SCANCODE_ESCAPE] = false;
	memcpy(VGAScreen->pixels, VGAScreen2->pixels, (size_t)VGAScreen->pitch * VGAScreen->h);
}

JE_boolean JE_inGameSetup(void)
{
	bool result = false;

	SDL_Surface *temp_surface = VGAScreen;
	VGAScreen = VGAScreenSeg; /* side-effect of game_screen */

	// Tyrian3D: the graphics on a page of their own (with the original's detail level), the mouse and the
	// music beside the volumes, back to the game first.
	enum MenuItemIndex
	{
		MENU_ITEM_RETURN_TO_GAME = 0,
		MENU_ITEM_GRAPHICS,  // Tyrian3D: the graphics page (ingame_options_3d)
		MENU_ITEM_MUSIC_VOLUME,
		MENU_ITEM_EFFECTS_VOLUME,
		MENU_ITEM_MUSIC,     // Tyrian3D: SoundFont or AdLib
		MENU_ITEM_SOUNDFONT, // Tyrian3D: which SoundFont
		MENU_ITEM_GAME_SPEED,
		MENU_ITEM_MOUSE,     // Tyrian3D
		MENU_ITEM_QUIT,
		MENU_ITEM_COUNT
	};

	// The original's texts (inGameText: music volume, effects volume, detail level, game speed, return to
	// game, quit) and help lines (mainMenuHelp), where it has them.
	static const int text_of[MENU_ITEM_COUNT] = { 4, -1, 0, 1, -1, -1, 3, -1, 5 };
	static const int help_of[MENU_ITEM_COUNT] = { 25, -1, 14, 14, -1, -1, 28, -1, 26 };
	static const int option_of[MENU_ITEM_COUNT] = { -1, -1, -1, -1, OPT_MUSIC, OPT_SOUNDFONT, -1, OPT_MOUSE, -1 };
	static const char *const graphics_help = "The 3D view: objects, shadows, effects, camera, HUD and menus, shown as they change.";

	if (shopSpriteSheet.data == NULL)
		JE_loadCompShapes(&shopSpriteSheet, '1');  // need mouse pointer sprites

	bool restart = true;

	const size_t menuItemsCount = MENU_ITEM_COUNT;
	size_t selectedIndex = MENU_ITEM_RETURN_TO_GAME;

	const int yMenuItems = 20;
	const int dyMenuItems = 13;  // (Tyrian3D: 9 rows in the box)
	const int xMenuItem = 10;
	const int xMenuItemName = xMenuItem;
	const int wMenuItemName = 110;
	const int xMenuItemValue = xMenuItemName + wMenuItemName;
	const int wMenuItemValue = 90;
	const int wMenuItem = wMenuItemName + wMenuItemValue;
	const int hMenuItem = 13;

	for (bool done = false; !done; )
	{
		if (restart)
		{
			// Main box
			JE_barShade(VGAScreen, 3, 13, 217, 137);
			JE_barShade(VGAScreen, 5, 15, 215, 135);

			// Help box
			JE_barShade(VGAScreen, 3, 143, 257, 157);
			JE_barShade(VGAScreen, 5, 145, 255, 155);

			memcpy(VGAScreen2->pixels, VGAScreen->pixels, VGAScreen2->pitch * VGAScreen2->h);

			mouseCursor = MOUSE_POINTER_NORMAL;

			restart = false;
		}

		// Restore background.
		memcpy(VGAScreen->pixels, VGAScreen2->pixels, (size_t)VGAScreen->pitch * VGAScreen->h);

		// Draw menu items.
		for (size_t i = 0; i < menuItemsCount; ++i)
		{
			const int y = yMenuItems + dyMenuItems * i;

			const char *const name = text_of[i] >= 0 ? inGameText[text_of[i]] : i == MENU_ITEM_GRAPHICS ? "Graphics..."
			                                                                                              : option_names[option_of[i]];

			const bool selected = i == selectedIndex;

			draw_font_hv_shadow(VGAScreen, xMenuItemName, y, name, normal_font, left_aligned, 15, -4 + (selected ? 2 : 0), false, 2);

			switch (i)
			{
			case MENU_ITEM_MUSIC_VOLUME:
			{
				JE_barDrawShadow(VGAScreen, xMenuItemValue, y, 1, music_disabled ? 12 : 16, (tyrMusicVolume + 6) / 12, 3, 13);
				break;
			}
			case MENU_ITEM_EFFECTS_VOLUME:
			{
				JE_barDrawShadow(VGAScreen, xMenuItemValue, y, 1, samples_disabled ? 12 : 16, (fxVolume + 6) / 12, 3, 13);
				break;
			}
			case MENU_ITEM_GAME_SPEED:
			{
				draw_font_hv_shadow(VGAScreen, xMenuItemValue, y, gameSpeedText[gameSpeed-1], normal_font, left_aligned, 15, -4 + (selected ? 2 : 0), false, 2);
				break;
			}
			case MENU_ITEM_MUSIC:
			case MENU_ITEM_SOUNDFONT:
			case MENU_ITEM_MOUSE:
			{
				draw_font_hv_shadow(VGAScreen, xMenuItemValue, y, option_value(option_of[i]), normal_font, left_aligned, 15, -4 + (selected ? 2 : 0), false, 2);
				break;
			}
			}
		}

		// Draw help text.
		const char *const help = selectedIndex == MENU_ITEM_GRAPHICS ? graphics_help
		                         : help_of[selectedIndex] >= 0       ? mainMenuHelp[help_of[selectedIndex]]
		                                                             : option_help[option_of[selectedIndex]];
		JE_outTextAdjust(VGAScreen, 10, 147, help, 14, 6, TINY_FONT, true);

		// Tyrian3D: the menu for the modern UI (ui.h): each item where the original takes the mouse on its
		// name and its value (the volumes' bars from their left end, as the click sets them).
		if (ui_modern())
		{
			UIMenu *ui = ui_menu_begin(UI_SCREEN_LEVEL_MENU, "Options");
			level_crumb(ui->crumb, sizeof(ui->crumb));
			ui->values_turn = true;
			ui->enter_turns = true;
			for (size_t i = 0; i < menuItemsCount; ++i)
			{
				const int y = yMenuItems + dyMenuItems * (int)i;
				char name[48];
				plain_label(name, text_of[i] >= 0 ? inGameText[text_of[i]] : i == MENU_ITEM_GRAPHICS ? "Graphics" : option_names[option_of[i]],
				            sizeof(name));
				const bool volume = i == MENU_ITEM_MUSIC_VOLUME || i == MENU_ITEM_EFFECTS_VOLUME;
				const bool value = i == MENU_ITEM_GAME_SPEED || option_of[i] >= 0;
				UIItem *it = ui_menu_add(ui, volume ? UI_ITEM_BAR : value ? UI_ITEM_CHOICE : UI_ITEM_ACTION, name, xMenuItemName, y,
				                         wMenuItemName, hMenuItem);
				SDL_strlcpy(it->hint, i == MENU_ITEM_GRAPHICS ? graphics_help : help_of[i] >= 0 ? mainMenuHelp[help_of[i]] : option_help[option_of[i]],
				            sizeof(it->hint));
				if (volume)
				{
					const bool music = i == MENU_ITEM_MUSIC_VOLUME;
					it->bar = (music ? tyrMusicVolume : fxVolume) / 255.0f;
					it->muted = music ? music_disabled : samples_disabled;
					it->hit_value = (SDL_Rect){ xMenuItemValue, y, ((255 + 6) / 12) * (3 + 1) - 1, hMenuItem };
				}
				else if (value)
				{
					plain_label(it->value, i == MENU_ITEM_GAME_SPEED ? gameSpeedText[gameSpeed - 1] : option_value(option_of[i]),
					            sizeof(it->value));
					it->hit_value = (SDL_Rect){ xMenuItemValue, y, wMenuItemValue, hMenuItem };
				}
			}
			ui->selected = (int)selectedIndex;
			ui->nowhere = (SDL_Point){ 300, 190 };
			ui_menu_publish(ui, VGAScreen, VGAScreen2);
		}

		service_SDL_events(true);

		JE_mouseStart();
		JE_showVGA();
		JE_mouseReplace();

		bool mouseMoved = false;
		do
		{
			SDL_Delay(16);

			Uint16 oldMouseX = mouse_x;
			Uint16 oldMouseY = mouse_y;

			push_joysticks_as_keyboard();
			service_SDL_events(false);

			NETWORK_KEEP_ALIVE();

			mouseMoved = mouse_x != oldMouseX || mouse_y != oldMouseY;
		} while (!(newkey || newmouse || mouseMoved));

		// Handle interaction.

		bool action = false;
		bool leftAction = false;
		bool rightAction = false;

		if (mouseMoved || newmouse)
		{
			// Find menu item that was hovered or clicked.
			if (mouse_x >= xMenuItem && mouse_x < xMenuItem + wMenuItem)
			{
				for (size_t i = 0; i < menuItemsCount; ++i)
				{
					const int yMenuItem = yMenuItems + dyMenuItems * i;
					if (mouse_y >= yMenuItem && mouse_y < yMenuItem + hMenuItem)
					{
						if (selectedIndex != i)
						{
							JE_playSampleNum(S_CURSOR);

							selectedIndex = i;
						}

						if (newmouse && lastmouse_but == SDL_BUTTON_LEFT &&
						    lastmouse_x >= xMenuItem && lastmouse_x < xMenuItem + wMenuItem &&
						    lastmouse_y >= yMenuItem && lastmouse_y < yMenuItem + hMenuItem)
						{
							// Act on menu item via name.
							if (lastmouse_x >= xMenuItemName && lastmouse_x < xMenuItemName + wMenuItemName)
							{
								action = true;
							}

							// Act on menu item via value.
							else if (lastmouse_x >= xMenuItemValue && lastmouse_x < xMenuItemValue + wMenuItemValue)
							{
								switch (i)
								{
								case MENU_ITEM_MUSIC_VOLUME:
								{
									JE_playSampleNum(S_CURSOR);

									const int w = ((255 + 6) / 12) * (3 + 1) - 1;

									int value = (lastmouse_x - xMenuItemValue) * 255 / (w - 1);
									tyrMusicVolume = MIN(MAX(0, value), 255);

									set_volume(tyrMusicVolume, fxVolume);
									break;
								}
								case MENU_ITEM_EFFECTS_VOLUME:
								{
									const int w = ((255 + 6) / 12) * (3 + 1) - 1;

									int value = (lastmouse_x - xMenuItemValue) * 255 / (w - 1);
									fxVolume = MIN(MAX(0, value), 255);

									set_volume(tyrMusicVolume, fxVolume);

									JE_playSampleNum(S_CURSOR);
									break;
								}
								case MENU_ITEM_GAME_SPEED:
								case MENU_ITEM_MUSIC:
								case MENU_ITEM_SOUNDFONT:
								case MENU_ITEM_MOUSE:
								{
									rightAction = true;
									break;
								}
								default:
									break;
								}
							}
						}

						break;
					}
				}
			}
		}

		if (newmouse)
		{
			if (lastmouse_but == SDL_BUTTON_RIGHT)
			{
				JE_playSampleNum(S_SPRING);

				done = true;
			}
		}
		else if (newkey)
		{
			switch (lastkey_scan)
			{
			case SDL_SCANCODE_UP:
			{
				JE_playSampleNum(S_CURSOR);

				selectedIndex = selectedIndex == 0
					? menuItemsCount - 1
					: selectedIndex - 1;
				break;
			}
			case SDL_SCANCODE_DOWN:
			{
				JE_playSampleNum(S_CURSOR);

				selectedIndex = selectedIndex == menuItemsCount - 1
					? 0
					: selectedIndex + 1;
				break;
			}
			case SDL_SCANCODE_LEFT:
			{
				leftAction = true;
				break;
			}
			case SDL_SCANCODE_RIGHT:
			{
				rightAction = true;
				break;
			}
			case SDL_SCANCODE_SPACE:
			case SDL_SCANCODE_RETURN:
			{
				action = true;
				break;
			}
			case SDL_SCANCODE_ESCAPE:
			{
				JE_playSampleNum(S_SPRING);

				done = true;
				break;
			}
			default:
				break;
			}
		}

		// (Enter turns the choices as Right does.)
		if (action && (selectedIndex == MENU_ITEM_GAME_SPEED || option_of[selectedIndex] >= 0))
		{
			action = false;
			rightAction = true;
		}

		if (action)
		{
			switch (selectedIndex)
			{
			case MENU_ITEM_MUSIC_VOLUME:
			{
				JE_playSampleNum(S_SELECT);

				music_disabled = !music_disabled;
				break;
			}
			case MENU_ITEM_EFFECTS_VOLUME:
			{
				samples_disabled = !samples_disabled;

				JE_playSampleNum(S_SELECT);
				break;
			}
			case MENU_ITEM_GRAPHICS:
			{
				JE_playSampleNum(S_SELECT);
				ingame_options_3d();
				break;
			}
			case MENU_ITEM_RETURN_TO_GAME:
			{
				JE_playSampleNum(S_SELECT);

				done = true;
				break;
			}
			case MENU_ITEM_QUIT:
			{
				JE_playSampleNum(S_SELECT);

				if (constantPlay)
					JE_tyrianHalt(0);

				if (isNetworkGame)
				{
					/*Tell other computer to exit*/
					haltGame = true;
					playerEndLevel = true;
				}

				result = true;
				done = true;
				break;
			}
			default:
				break;
			}
		}
		else if (leftAction || rightAction)
		{
			const int step = rightAction ? 1 : -1;
			switch (selectedIndex)
			{
			case MENU_ITEM_MUSIC_VOLUME:
			{
				JE_playSampleNum(S_CURSOR);

				JE_changeVolume(&tyrMusicVolume, 12 * step, &fxVolume, 0);
				break;
			}
			case MENU_ITEM_EFFECTS_VOLUME:
			{
				JE_changeVolume(&tyrMusicVolume, 0, &fxVolume, 12 * step);

				JE_playSampleNum(S_CURSOR);
				break;
			}
			case MENU_ITEM_GAME_SPEED:
			{
				JE_playSampleNum(S_CURSOR);

				if (step > 0)
					gameSpeed = gameSpeed < 5 ? gameSpeed + 1 : 1;
				else
					gameSpeed = gameSpeed > 1 ? gameSpeed - 1 : 5;
				JE_initProcessorType();
				JE_setNewGameSpeed();
				break;
			}
			case MENU_ITEM_MUSIC:
			case MENU_ITEM_SOUNDFONT:
			case MENU_ITEM_MOUSE:
			{
				JE_playSampleNum(S_CLICK);
				option_turn(option_of[selectedIndex], step);
				break;
			}
			default:
				break;
			}
		}
	}

	VGAScreen = temp_surface; /* side-effect of game_screen */

	return result;
}

void JE_inGameHelp(void)
{
	SDL_Surface *temp_surface = VGAScreen;
	VGAScreen = VGAScreenSeg; /* side-effect of game_screen */

	//tempScreenSeg = VGAScreenSeg;

	JE_clearKeyboard();
	JE_wipeKey();

	// Tyrian3D: the screen as it was, put back once the help goes (the key that closes it may open the
	// in-game options at once, before the game draws its next frame: they showed over the help's text).
	static Uint8 saved[320 * 200];
	for (int y = 0; y < 200; ++y)
		memcpy(saved + y * 320, (const Uint8 *)VGAScreenSeg->pixels + y * VGAScreenSeg->pitch, 320);
	const int shades = video_backdrop_shade_mark();  // (and the boxes it darkens, which the 3D view counts)

	JE_barShade(VGAScreen, 1, 1, 262, 182); /*Main Box*/
	JE_barShade(VGAScreen, 3, 3, 260, 180);
	JE_barShade(VGAScreen, 5, 5, 258, 178);
	JE_barShade(VGAScreen, 7, 7, 256, 176);
	fill_rectangle_xy(VGAScreen, 9, 9, 254, 174, 0);

	if (twoPlayerMode)  // Two-Player Help
	{
		helpBoxColor = 3;
		helpBoxBrightness = 3;
		JE_HBox(VGAScreen, 20,  4, 36, 50);

		// weapon help
		blit_sprite(VGAScreenSeg, 2, 21, OPTION_SHAPES, 43);
		helpBoxColor = 5;
		helpBoxBrightness = 3;
		JE_HBox(VGAScreen, 55, 20, 37, 40);

		// sidekick help
		blit_sprite(VGAScreenSeg, 5, 36, OPTION_SHAPES, 41);
		helpBoxColor = 5;
		helpBoxBrightness = 3;
		JE_HBox(VGAScreen, 40, 43, 34, 44);

		// shield/armor help
		blit_sprite(VGAScreenSeg, 2, 79, OPTION_SHAPES, 42);
		helpBoxColor = 5;
		helpBoxBrightness = 3;
		JE_HBox(VGAScreen, 54, 84, 35, 40);

		helpBoxColor = 5;
		helpBoxBrightness = 3;
		JE_HBox(VGAScreen, 5, 126, 38, 55);
		helpBoxColor = 5;
		helpBoxBrightness = 3;
		JE_HBox(VGAScreen, 5, 160, 39, 55);
	}
	else
	{
		// power bar help
		blit_sprite(VGAScreenSeg, 15, 5, OPTION_SHAPES, 40);
		helpBoxColor = 5;
		helpBoxBrightness = 3;
		JE_HBox(VGAScreen, 40, 10, 31, 45);

		// weapon help
		blit_sprite(VGAScreenSeg, 5, 37, OPTION_SHAPES, 39);
		helpBoxColor = 5;
		helpBoxBrightness = 3;
		JE_HBox(VGAScreen, 40, 40, 32, 44);
		helpBoxColor = 5;
		helpBoxBrightness = 3;
		JE_HBox(VGAScreen, 40, 60, 33, 44);

		// sidekick help
		blit_sprite(VGAScreenSeg, 5, 98, OPTION_SHAPES, 41);
		helpBoxColor = 5;
		helpBoxBrightness = 3;
		JE_HBox(VGAScreen, 40, 103, 34, 44);

		// shield/armor help
		blit_sprite(VGAScreenSeg, 2, 138, OPTION_SHAPES, 42);
		helpBoxColor = 5;
		helpBoxBrightness = 3;
		JE_HBox(VGAScreen, 54, 143, 35, 40);
	}

	// "press a key"
	blit_sprite(VGAScreenSeg, 16, 189, OPTION_SHAPES, 36);  // in-game text area
	JE_outText(VGAScreenSeg, 120 - JE_textWidth(miscText[5-1], TINY_FONT) / 2 + 20, 190, miscText[5-1], 0, 4);

	// Tyrian3D: the help for the modern UI (ui.h): each part's title (its highlighted words) and text.
	if (ui_modern())
	{
		static const int single[] = { 31, 32, 33, 34, 35 }, two[] = { 36, 37, 34, 35, 38, 39 };
		const int *parts = twoPlayerMode ? two : single;
		const int count = twoPlayerMode ? (int)COUNTOF(two) : (int)COUNTOF(single);
		UIMenu *ui = ui_menu_begin(UI_SCREEN_LEVEL_HELP, "");
		level_crumb(ui->crumb, sizeof(ui->crumb));
		for (int i = 0; i < count && i < UI_HELP_PARTS; ++i)
		{
			const char *text = helpTxt[parts[i] - 1];
			char title[40] = "";
			const char *open = strchr(text, '~');
			const char *close = open != NULL ? strchr(open + 1, '~') : NULL;
			if (open != NULL && close != NULL)
			{
				SDL_strlcpy(title, open + 1, SDL_min((size_t)(close - open), sizeof(title)));
				text = close + 1;
			}
			plain_label(ui->help.title[i], title, sizeof(ui->help.title[i]));
			while (*text != '\0' && (unsigned char)*text <= ' ')
				++text;
			plain_label(ui->help.text[i], text, sizeof(ui->help.text[i]));
			// (Without what's left of a mark at its start.)
			char *t = ui->help.text[i];
			while (*t != '\0' && !SDL_isalnum((unsigned char)*t) && *t != '"' && *t != '(')
				memmove(t, t + 1, strlen(t));
			ui->help.count = i + 1;
		}
		ui->selected = -1;
		ui_menu_publish(ui, VGAScreenSeg, VGAScreenSeg);
	}

	do
	{
		service_SDL_events(true);

		JE_mouseStart();
		JE_showVGA();
		JE_mouseReplace();

		SDL_Delay(16);

		push_joysticks_as_keyboard();
		service_SDL_events(false);

		NETWORK_KEEP_ALIVE();
	} while (!(newkey || newmouse));

	textErase = 1;

	for (int y = 0; y < 200; ++y)
		memcpy((Uint8 *)VGAScreenSeg->pixels + y * VGAScreenSeg->pitch, saved + y * 320, 320);
	video_backdrop_shade_reset(shades);

	VGAScreen = temp_surface;
}

void JE_highScoreCheck(void)
{
	if (shopSpriteSheet.data == NULL)
		JE_loadCompShapes(&shopSpriteSheet, '1');  // need mouse pointer sprite

	Sint32 temp_score;

	for (int temp_p = 0; temp_p < (twoPlayerMode ? 2 : 1); ++temp_p)
	{
		JE_sortHighScores();

		int p = temp_p;
		int table = 10 + (initial_episode_num - 1) * 2;

		if (timedBattleMode)
		{
			// timed battle score is just money
			temp_score = player[0].cash;
			table = timeBattleSelection - 1;
		}
		else if (twoPlayerMode)
		{
			// ask for the highest scorer first
			if (player[0].cash < player[1].cash)
				p = (temp_p == 0) ? 1 : 0;

			temp_score = (p == 0) ? player[0].cash : player[1].cash;
			++table;
		}
		else
		{
			// single player highscore includes cost of upgrades
			temp_score = JE_totalScore(&player[0]);
		}

		int slot;
		for (slot = 0; slot < 3; ++slot)
		{
			if (temp_score > t2kHighScores[table][slot].score)
				break;
		}

		// did you get a high score?
		if (slot < 3)
		{
			// shift down old scores
			for (int i = 2; i > slot; --i)
				memcpy(&t2kHighScores[table][i], &t2kHighScores[table][i - 1], sizeof(T2KHighScoreType));

			wait_noinput(false, true, false);

			JE_clr256(VGAScreen);
			JE_showVGA();
			memcpy(colors, palettes[0], sizeof(colors));

			if (!timedBattleMode) // Doesn't play this music
				play_song(33);

			// Not part of the above condition
			{
				/* Enter Thy name */

				JE_byte flash = 8 * 16 + 10;
				JE_boolean fadein = true;
				JE_boolean quit = false, cancel = false;
				char stemp[30], tempstr[30];
				char buffer[256];

				strcpy(stemp, "                             ");
				temp = 0;

				// As astoundingly ugly as this makes the shade below look, this is in fact what Tyrian 2000 does.
				if (timedBattleMode)
					JE_loadPic(VGAScreen, 13, false);

				// Tyrian3D: the screen before the question's box, as the modern UI's picture under it.
				static SDL_Surface *name_picture = NULL;
				if (ui_modern() && (name_picture != NULL || (name_picture = SDL_CreateSurface(320, 200, SDL_PIXELFORMAT_INDEX8)) != NULL))
					for (int y = 0; y < 200; ++y)
						memcpy((Uint8 *)name_picture->pixels + y * name_picture->pitch, (const Uint8 *)VGAScreen->pixels + y * VGAScreen->pitch, 320);

				JE_barShade(VGAScreen, 65, 55, 255, 155);

				do
				{
					service_SDL_events(true);

					JE_dString(VGAScreen, JE_fontCenter(miscText[51], FONT_SHAPES), 3, miscText[51], FONT_SHAPES);

					temp3 = twoPlayerMode ? 58 + p : 53;

					JE_dString(VGAScreen, JE_fontCenter(miscText[temp3-1], SMALL_FONT_SHAPES), 30, miscText[temp3-1], SMALL_FONT_SHAPES);

					blit_sprite(VGAScreenSeg, 50, 50, OPTION_SHAPES, 35);  // message box

					if (twoPlayerMode)
					{
						sprintf(buffer, "%s %s", miscText[48 + p], miscText[53]);
						JE_textShade(VGAScreen, 60, 55, buffer, 11, 4, FULL_SHADE);
					}
					else
					{
						JE_textShade(VGAScreen, 60, 55, miscText[53], 11, 4, FULL_SHADE);
					}

					sprintf(buffer, "%s %d", miscText[37], temp_score);
					JE_textShade(VGAScreen, 70, 70, buffer, 11, 4, FULL_SHADE);

					do
					{
						flash = (flash == 8 * 16 + 10) ? 8 * 16 + 2 : 8 * 16 + 10;
						temp3 = (temp3 == 6) ? 2 : 6;

						strncpy(tempstr, stemp, temp);
						tempstr[temp] = '\0';
						JE_outText(VGAScreen, 65, 89, tempstr, 8, 3);
						tempW = 65 + JE_textWidth(tempstr, TINY_FONT);
						JE_barShade(VGAScreen, tempW + 2, 90, tempW + 6, 95);
						fill_rectangle_xy(VGAScreen, tempW + 1, 89, tempW + 5, 94, flash);

						// Tyrian3D: the question for the modern UI (ui.h): the score large, the name typed,
						// its buttons the UI's own (the original's mouse check reads a position never set).
						if (ui_modern())
						{
							UIMenu *ui = ui_menu_begin(UI_SCREEN_SCORE_NAME, "");
							UIDialog *d = &ui->dialog;
							d->on = true;
							d->actions = true;
							d->selected = -1;
							plain_label(d->title, miscText[51], sizeof(d->title));
							char said[96];
							if (twoPlayerMode)
								snprintf(said, sizeof(said), "%s %s %s", miscText[57 + p], miscText[48 + p], miscText[53]);
							else
								snprintf(said, sizeof(said), "%s %s", miscText[52], miscText[53]);
							plain_label(d->text, said, sizeof(d->text));
							plain_label(d->note_label, miscText[37], sizeof(d->note_label));
							for (char *c = d->note_label; *c != '\0'; ++c)
								*c = (char)SDL_toupper(*c);
							group_digits((unsigned long)SDL_max(temp_score, 0), d->note, sizeof(d->note));
							d->field_on = true;
							SDL_strlcpy(d->field, tempstr, sizeof(d->field));
							d->caret = flash == 8 * 16 + 10;
							plain_label(d->yes, miscText[9], sizeof(d->yes));
							plain_label(d->no, miscText[10], sizeof(d->no));
							ui->selected = -1;
							ui->wheel = UI_WHEEL_NONE;
							ui_menu_publish(ui, VGAScreen, name_picture != NULL ? name_picture : VGAScreen);
						}

						for (int i = 0; i < 14; i++)
						{
							setDelay(1);

							JE_mouseStart();
							JE_showVGA();
							if (fadein)
							{
								fade_palette(colors, 15, 0, 255);
								fadein = false;
							}
							JE_mouseReplace();

							push_joysticks_as_keyboard();
							service_wait_delay();

							if (newkey || newmouse)
								break;
						}

					} while (!newkey && !newmouse && !new_text);

					if (!playing)
						play_song(31);

					// Tyrian3D: the modern UI's buttons (above).
					const int pressed = ui_take_press();
					if (pressed == UI_ACTION_YES)
						quit = true;
					else if (pressed == UI_ACTION_NO)
						quit = cancel = true;

					if (mouseButton > 0)
					{
						if (mouseX > 56 && mouseX < 142 && mouseY > 123 && mouseY < 149)
						{
							quit = true;
						}
						else if (mouseX > 151 && mouseX < 237 && mouseY > 123 && mouseY < 149)
						{
							quit = true;
							cancel = true;
						}
					}
					else if (new_text)
					{
						for (size_t ti = 0U; last_text[ti] != '\0'; ++ti)
						{
							const char c = (unsigned char)last_text[ti] <= 127U ? toupper(last_text[ti]) : 0;
							if ((c == ' ' || font_ascii[(unsigned char)c] != -1) &&
							    temp < 28)
							{
								stemp[temp] = c;
								temp += 1;
							}
						}
					}
					else if (newkey)
					{
						switch (lastkey_scan)
						{
							case SDL_SCANCODE_BACKSPACE:
							case SDL_SCANCODE_DELETE:
								if (temp)
								{
									temp--;
									stemp[temp] = ' ';
								}
								break;
							case SDL_SCANCODE_ESCAPE:
								quit = true;
								cancel = true;
								break;
							case SDL_SCANCODE_RETURN:
								quit = true;
								break;
							default:
								break;
						}
					}
				} while (!quit);

				// Timed Battle mode doesn't allow cancelling, so we ignore it
				if (!cancel || timedBattleMode)
				{
					t2kHighScores[table][slot].score = temp_score;
					strcpy(t2kHighScores[table][slot].playerName, stemp);
					t2kHighScores[table][slot].difficulty = difficultyLevel;
				}

				fade_black(15);
				JE_loadPic(VGAScreen, 2, false);

				JE_dString(VGAScreen, JE_fontCenter(miscText[50], FONT_SHAPES), 10, miscText[50], FONT_SHAPES);

				if (timedBattleMode)
					JE_dString(VGAScreen, JE_fontCenter(timed_battle_name[timeBattleSelection], SMALL_FONT_SHAPES), 35, timed_battle_name[timeBattleSelection], SMALL_FONT_SHAPES);
				else
					JE_dString(VGAScreen, JE_fontCenter(episode_name[episodeNum], SMALL_FONT_SHAPES), 35, episode_name[episodeNum], SMALL_FONT_SHAPES);

				for (int i = 0; i < 3; ++i)
				{
					if (i != slot)
					{
						sprintf(buffer, "~#%d:~  %d", i+1, t2kHighScores[table][i].score);
						JE_textShade(VGAScreen,  20, (i * 12) + 65, buffer, 15, 0, FULL_SHADE);
						JE_textShade(VGAScreen, 150, (i * 12) + 65, t2kHighScores[table][i].playerName, 15, 2, FULL_SHADE);
					}
				}

				// Tyrian3D: the board with the new entry for the modern UI (ui.h), shown while its texts
				// glow in (hold), then waiting for a key.
				UIMenu *board_ui = NULL;
				if (ui_modern())
				{
					board_ui = scores_menu(timedBattleMode ? timed_battle_name[timeBattleSelection] : episode_name[episodeNum], 0, 1, false, false);
					scores_table(&board_ui->scores.table[board_ui->scores.table_count++], twoPlayerMode ? miscText[47] : miscText[46], table);
					board_ui->scores.new_table = 0;
					board_ui->scores.new_row = slot;
					board_ui->hold = true;
					ui_menu_publish(board_ui, VGAScreen, VGAScreen);
				}

				JE_showVGA();

				fade_palette(colors, 15, 0, 255);

				sprintf(buffer, "~#%d:~  %d", slot+1, t2kHighScores[table][slot].score);

				frameCountMax = 6;
				textGlowFont = TINY_FONT;

				textGlowBrightness = 10;
				JE_outTextGlow(VGAScreenSeg,  20, (slot * 12) + 65, buffer);
				textGlowBrightness = 10;
				JE_outTextGlow(VGAScreenSeg, 150, (slot * 12) + 65, t2kHighScores[table][slot].playerName);
				textGlowBrightness = 10;
				JE_outTextGlow(VGAScreenSeg, JE_fontCenter(miscText[4], TINY_FONT), 180, miscText[4]);

				if (board_ui != NULL && ui_modern())
				{
					board_ui = scores_menu(timedBattleMode ? timed_battle_name[timeBattleSelection] : episode_name[episodeNum], 0, 1, false, false);
					scores_table(&board_ui->scores.table[board_ui->scores.table_count++], twoPlayerMode ? miscText[47] : miscText[46], table);
					board_ui->scores.new_table = 0;
					board_ui->scores.new_row = slot;
					board_ui->scores.prompt = true;
					board_ui->hold = true;
					ui_menu_publish(board_ui, VGAScreen, VGAScreen);
				}
				JE_showVGA();

				if (frameCountMax != 0)
					wait_input(true, true, true);

				fade_black(15);
				ui_screen_done();  // Tyrian3D
			}

		}
	}
}

// increases game difficulty based on player's total score / total of players' scores
void adjust_difficulty(void)
{
	const float score_multiplier[10] =
	{
		0,     // Wimp  (doesn't exist)
		0.4f,  // Easy
		0.8f,  // Normal
		1.3f,  // Hard
		1.6f,  // Impossible
		2,     // Insanity
		2,     // Suicide
		3,     // Maniacal
		3,     // Zinglon
		3,     // Nortaneous
	};

	assert(initialDifficulty > 0 && initialDifficulty < 10);

	const ulong score = twoPlayerMode ? (player[0].cash + player[1].cash) : JE_totalScore(&player[0]),
	            adjusted_score = roundf(score * score_multiplier[initialDifficulty]);

	uint new_difficulty = 0;

	if (twoPlayerMode)
	{
		if (adjusted_score < 10000)
			new_difficulty = DIFFICULTY_EASY;
		else if (adjusted_score < 20000)
			new_difficulty = DIFFICULTY_NORMAL;
		else if (adjusted_score < 50000)
			new_difficulty = DIFFICULTY_HARD;
		else if (adjusted_score < 80000)
			new_difficulty = DIFFICULTY_IMPOSSIBLE;
		else if (adjusted_score < 125000)
			new_difficulty = DIFFICULTY_INSANITY;
		else if (adjusted_score < 200000)
			new_difficulty = DIFFICULTY_SUICIDE;
		else if (adjusted_score < 400000)
			new_difficulty = DIFFICULTY_MANIACAL;
		else if (adjusted_score < 600000)
			new_difficulty = DIFFICULTY_ZINGLON;
		else
			new_difficulty = DIFFICULTY_NORTANEOUS;
	}
	else
	{
		if (adjusted_score < 40000)
			new_difficulty = DIFFICULTY_EASY;
		else if (adjusted_score < 70000)
			new_difficulty = DIFFICULTY_NORMAL;
		else if (adjusted_score < 150000)
			new_difficulty = DIFFICULTY_HARD;
		else if (adjusted_score < 300000)
			new_difficulty = DIFFICULTY_IMPOSSIBLE;
		else if (adjusted_score < 600000)
			new_difficulty = DIFFICULTY_INSANITY;
		else if (adjusted_score < 1000000)
			new_difficulty = DIFFICULTY_SUICIDE;
		else if (adjusted_score < 2000000)
			new_difficulty = DIFFICULTY_MANIACAL;
		else if (adjusted_score < 3000000)
			new_difficulty = DIFFICULTY_ZINGLON;
		else
			new_difficulty = DIFFICULTY_NORTANEOUS;
	}

	difficultyLevel = MAX((unsigned)difficultyLevel, new_difficulty);
}

bool load_next_demo(void)
{
	if (++demo_num > 5)
		demo_num = 1;

	char demo_filename[9];
	snprintf(demo_filename, sizeof(demo_filename), "demo.%d", demo_num);
	demo_file = dir_fopen_die(data_dir(), demo_filename, "rb"); // TODO: only play demos from existing file (instead of dying)

	difficultyLevel = DIFFICULTY_NORMAL;
	bonusLevelCurrent = false;

	Uint8 temp;
	fread_u8_die(&temp, 1, demo_file);
	JE_initEpisode(temp);

	fread_die(levelName, 1, 10, demo_file);
	levelName[10] = '\0';

	fread_u8_die(&lvlFileNum, 1, demo_file);

	fread_u8_die(&player[0].items.weapon[FRONT_WEAPON].id,  1, demo_file);
	fread_u8_die(&player[0].items.weapon[REAR_WEAPON].id,   1, demo_file);
	fread_u8_die(&player[0].items.super_arcade_mode,        1, demo_file);
	fread_u8_die(&player[0].items.sidekick[LEFT_SIDEKICK],  1, demo_file);
	fread_u8_die(&player[0].items.sidekick[RIGHT_SIDEKICK], 1, demo_file);
	fread_u8_die(&player[0].items.generator,                1, demo_file);

	fread_u8_die(&player[0].items.sidekick_level,           1, demo_file); // could probably ignore
	fread_u8_die(&player[0].items.sidekick_series,          1, demo_file); // could probably ignore

	fread_u8_die(&initial_episode_num,                      1, demo_file); // could probably ignore

	fread_u8_die(&player[0].items.shield,                   1, demo_file);
	fread_u8_die(&player[0].items.special,                  1, demo_file);
	fread_u8_die(&player[0].items.ship,                     1, demo_file);

	for (uint i = 0; i < 2; ++i)
		fread_u8_die(&player[0].items.weapon[i].power,      1, demo_file);

	Uint8 unused[3];
	fread_u8_die(unused, 3, demo_file);

	fread_u8_die(&levelSong, 1, demo_file);

	demo_keys = 0;

	Uint8 temp2[2] = { 0, 0 };
	fread_u8(temp2, 2, demo_file);
	demo_keys_wait = (temp2[0] << 8) | temp2[1];

	printf("loaded demo '%s'\n", demo_filename);

	return true;
}

bool replay_demo_keys(void)
{
	while (demo_keys_wait == 0)
	{
		demo_keys = 0;
		fread_u8(&demo_keys, 1, demo_file);

		Uint8 temp2[2] = { 0, 0 };
		fread_u8(temp2, 2, demo_file);
		demo_keys_wait = (temp2[0] << 8) | temp2[1];

		if (feof(demo_file))
		{
			// no more keys
			return false;
		}
	}

	demo_keys_wait--;

	if (demo_keys & (1 << 0))
		player[0].y -= CURRENT_KEY_SPEED;
	if (demo_keys & (1 << 1))
		player[0].y += CURRENT_KEY_SPEED;

	if (demo_keys & (1 << 2))
		player[0].x -= CURRENT_KEY_SPEED;
	if (demo_keys & (1 << 3))
		player[0].x += CURRENT_KEY_SPEED;

	button[0] = (bool)(demo_keys & (1 << 4));
	button[3] = (bool)(demo_keys & (1 << 5));
	button[1] = (bool)(demo_keys & (1 << 6));
	button[2] = (bool)(demo_keys & (1 << 7));

	return true;
}

/*Street Fighter codes*/
void JE_SFCodes(JE_byte playerNum_, JE_integer PX_, JE_integer PY_, JE_integer mouseX_, JE_integer mouseY_)
{
	JE_byte temp, temp2, temp3, temp4, temp5;

	uint ship = player[playerNum_-1].items.ship;

	/*Get direction*/
	if (playerNum_ == 2 && ship < 15)
	{
		ship = 0;
	}

	if (ship < 15)
	{

		temp2 = (mouseY_ > PY_) +    /*UP*/
		        (mouseY_ < PY_) +    /*DOWN*/
		        (PX_ < mouseX_) +    /*LEFT*/
		        (PX_ > mouseX_);     /*RIGHT*/
		temp = (mouseY_ > PY_) * 1 + /*UP*/
		       (mouseY_ < PY_) * 2 + /*DOWN*/
		       (PX_ < mouseX_) * 3 + /*LEFT*/
		       (PX_ > mouseX_) * 4;  /*RIGHT*/

		if (temp == 0) // no direction being pressed
		{
			if (!button[0]) // if fire button is released
			{
				temp = 9;
				temp2 = 1;
			}
			else
			{
				temp2 = 0;
				temp = 99;
			}
		}

		if (temp2 == 1) // if exactly one direction pressed or fire button is released
		{
			temp += button[0] * 4;

			temp3 = superTyrian ? 21 : 3;
			for (temp2 = 0; temp2 < temp3; temp2++)
			{

				/*Use SuperTyrian ShipCombos or not?*/
				temp5 = superTyrian ? shipCombosB[temp2] : shipCombos[ship][temp2];

				// temp5 == selected combo in ship
				if (temp5 == 0) /* combo doesn't exists */
				{
					// mark twiddles as cancelled/finished
					SFCurrentCode[playerNum_-1][temp2] = 0;
				}
				else
				{
					// get next combo key
					temp4 = keyboardCombos[temp5-1][SFCurrentCode[playerNum_-1][temp2]];

					// correct key
					if (temp4 == temp)
					{
						SFCurrentCode[playerNum_-1][temp2]++;

						temp4 = keyboardCombos[temp5-1][SFCurrentCode[playerNum_-1][temp2]];
						if (temp4 > 100 && temp4 <= 100 + SPECIAL_NUM)
						{
							SFCurrentCode[playerNum_-1][temp2] = 0;
							SFExecuted[playerNum_-1] = temp4 - 100;
						}
					}
					else
					{
						if ((temp != 9) &&
						    (temp4 - 1) % 4 != (temp - 1) % 4 &&
						    (SFCurrentCode[playerNum_-1][temp2] == 0 ||
						     keyboardCombos[temp5-1][SFCurrentCode[playerNum_-1][temp2]-1] != temp))
						{
							SFCurrentCode[playerNum_-1][temp2] = 0;
						}
					}
				}
			}
		}

	}
}

void JE_playCredits(void)
{
	enum { lines_max = 126 };
	enum { line_max_length = 65 };

	char credstr[lines_max][line_max_length + 1];

	int lines = 0;

	JE_byte currentpic = 0, fade = 0;
	JE_shortint fadechg = 1;
	JE_byte currentship = 0;
	JE_integer shipx = 0, shipxwait = 0;
	JE_shortint shipxc = 0, shipxca = 0;

	load_sprites_file(EXTRA_SHAPES, "estsc.shp");

	setDelay2(1000);

	play_song(8);

	// load credits text
	FILE *f = dir_fopen_die(data_dir(), "tyrian.cdt", "rb");
	for (lines = 0; lines < lines_max; ++lines)
	{
		read_encrypted_pascal_string(credstr[lines], sizeof(credstr[lines]), f);
	}
	fclose(f);

	memcpy(colors, palettes[6-1], sizeof(colors));
	JE_clr256(VGAScreen);
	JE_showVGA();
	fade_palette(colors, 2, 0, 255);

	//tempScreenSeg = VGAScreenSeg;

	const int ticks_max = lines * 20 * 3;
	for (int ticks = 0; ticks < ticks_max; ++ticks)
	{
		setDelay(1);
		JE_clr256(VGAScreen);

		blit_sprite_hv(VGAScreenSeg, 319 - sprite(EXTRA_SHAPES, currentpic)->width, 100 - (sprite(EXTRA_SHAPES, currentpic)->height / 2), EXTRA_SHAPES, currentpic, 0x0, fade - 15);

		fade += fadechg;
		if (fade == 0 && fadechg == -1)
		{
			fadechg = 1;
			++currentpic;
			if (currentpic >= sprite_table[EXTRA_SHAPES].count)
				currentpic = 0;
		}
		if (fade == 15)
			fadechg = 0;

		if (getDelayTicks2() == 0)
		{
			fadechg = -1;
			setDelay2(900);
		}

		if (ticks % 200 == 0)
		{
			currentship = (mt_rand() % 11) + 1;
			shipxwait = (mt_rand() % 80) + 10;
			if ((mt_rand() % 2) == 1)
			{
				shipx = 1;
				shipxc = 0;
				shipxca = 1;
			}
			else
			{
				shipx = 900;
				shipxc = 0;
				shipxca = -1;
			}
		}

		shipxwait--;
		if (shipxwait == 0)
		{
			if (shipx == 1 || shipx == 900)
				shipxc = 0;
			shipxca = -shipxca;
			shipxwait = (mt_rand() % 40) + 15;
		}
		shipxc += shipxca;
		shipx += shipxc;
		if (shipx < 1)
		{
			shipx = 1;
			shipxwait = 1;
		}
		if (shipx > 900)
		{
			shipx = 900;
			shipxwait = 1;
		}
		int tmp_unknown = shipxc * shipxc;
		if (450 + tmp_unknown < 0 || 450 + tmp_unknown > 900)
		{
			if (shipxca < 0 && shipxc < 0)
				shipxwait = 1;
			if (shipxca > 0 && shipxc > 0)
				shipxwait = 1;
		}

		uint ship_sprite = ships[currentship].shipgraphic;
		if (shipxc < -10)
			ship_sprite -= (shipxc < -20) ? 4 : 2;
		else if (shipxc > 10)
			ship_sprite += (shipxc > 20) ? 4 : 2;

		blit_sprite2x2(VGAScreen, shipx / 40, 184 - (ticks % 200), spriteSheet9, ship_sprite);

		// Tyrian3D: the screen before its texts (with the bars the original puts over them), the modern UI's
		// picture under its own lines (below).
		static SDL_Surface *credits_picture = NULL;
		if (ui_modern() && (credits_picture != NULL || (credits_picture = SDL_CreateSurface(320, 200, SDL_PIXELFORMAT_INDEX8)) != NULL))
			for (int row = 0; row < 200; ++row)
			{
				Uint8 *to = (Uint8 *)credits_picture->pixels + row * credits_picture->pitch;
				if (row <= 10 || row >= 190)
					memset(to, 0, 320);
				else
					memcpy(to, (const Uint8 *)VGAScreen->pixels + row * VGAScreen->pitch, 320);
			}

		const int bottom_line = (ticks / 3) / 20;
		int y = 20 - ((ticks / 3) % 20);

		for (int line = bottom_line - 10; line < bottom_line; ++line)
		{
			if (line >= 0 && line < lines_max)
			{
				if (strcmp(&credstr[line][0], ".") != 0 && strlen(credstr[line]))
				{
					const Uint8 color = credstr[line][0] - 65;
					const char *text = &credstr[line][1];

					const int x = 110 - JE_textWidth(text, SMALL_FONT_SHAPES) / 2;

					JE_outTextAdjust(VGAScreen, x + abs((y / 18) % 4 - 2) - 1, y - 1, text, color, -8, SMALL_FONT_SHAPES, false);
					JE_outTextAdjust(VGAScreen, x,                             y,     text, color, -2, SMALL_FONT_SHAPES, false);
				}
			}

			y += 20;
		}

		fill_rectangle_xy(VGAScreen, 0,  0, 319, 10, 0);
		fill_rectangle_xy(VGAScreen, 0, 190, 319, 199, 0);

		if (currentpic == sprite_table[EXTRA_SHAPES].count - 1)
			JE_outTextAdjust(VGAScreen, 5, 180, miscText[54], 2, -2, SMALL_FONT_SHAPES, false);  // levels-in-episode

		// Tyrian3D: the lines on the screen for the modern UI (ui.h), where they are (smoothly between the
		// original's steps); a block's first line is its name.
		if (ui_modern())
		{
			UIMenu *ui = ui_menu_begin(UI_SCREEN_CREDITS, "");
			UICredits *c = &ui->credits;
			const float top = 20.0f - (ticks % 60) / 3.0f;
			for (int line = bottom_line - 10, k = 0; line < bottom_line; ++line, ++k)
			{
				if (line < 0 || line >= lines_max || strcmp(credstr[line], ".") == 0 || strlen(credstr[line]) == 0 || c->count >= UI_CREDIT_LINES)
					continue;
				const int i = c->count++;
				plain_label(c->text[i], &credstr[line][1], sizeof(c->text[i]));
				c->x[i] = 110;
				c->y[i] = top + 20 * k;
				const bool first = line == 0 || strcmp(credstr[line - 1], ".") == 0 || credstr[line - 1][0] == '\0';
				c->colour[i] = first ? -1 : credstr[line][0] - 65;
			}
			if (currentpic == sprite_table[EXTRA_SHAPES].count - 1)
				plain_label(c->note, miscText[54], sizeof(c->note));
			ui->selected = -1;
			ui->wheel = UI_WHEEL_NONE;
			ui_menu_publish(ui, VGAScreen, credits_picture != NULL ? credits_picture : VGAScreen);
		}

		if (bottom_line == lines_max - 8)
			fade_song();

		if (ticks == ticks_max - 1)
		{
			--ticks;
			play_song(9);
		}

		NETWORK_KEEP_ALIVE();

		JE_showVGA();

		wait_delay();

		if (JE_anyButton())
			break;
	}

	fade_black(10);
	ui_screen_done();  // Tyrian3D

	free_sprites(EXTRA_SHAPES);
}

// Tyrian3D: a level's results for the modern UI (ui.h), row by row as the level's end shows them;
// shown whatever the screen shows (its texts glow in) until the end is over.
static UIResults level_results;

static void level_results_publish(void)
{
	if (!ui_modern())
		return;
	UIMenu *ui = ui_menu_begin(UI_SCREEN_LEVEL_END, "");
	level_crumb(ui->crumb, sizeof(ui->crumb));
	ui->results = level_results;
	ui->hold = true;
	ui->selected = -1;
	ui_menu_publish(ui, VGAScreenSeg, VGAScreenSeg);
}

static void level_results_row(const char *label, const char *value)
{
	if (level_results.row_count >= UI_RESULT_ROWS)
		return;
	plain_label(level_results.label[level_results.row_count], label, sizeof(level_results.label[0]));
	SDL_strlcpy(level_results.value[level_results.row_count], value, sizeof(level_results.value[0]));
	++level_results.row_count;
	level_results_publish();
}

static void level_results_money(const char *label, unsigned long value)
{
	char digits[32], grouped[40];
	snprintf(digits, sizeof(digits), "%lu", value);
	const int n = (int)strlen(digits);
	size_t k = 0;
	for (int i = 0; i < n && k + 2 < sizeof(grouped); ++i)
	{
		if (i > 0 && (n - i) % 3 == 0)
			grouped[k++] = ' ';
		grouped[k++] = digits[i];
	}
	grouped[k] = '\0';
	level_results_row(label, grouped);
}

void JE_endLevelAni(void)
{
	JE_word x, y;
	JE_byte temp;
	char tempStr[256];

	Sint8 i;

	memset(&level_results, 0, sizeof(level_results));
	level_results.percent = -1;
	level_results.cubes = -1;

	if (!constantPlay && !rogue_run)  // Tyrian3D: not for a rogue run's items
	{
		// grant shipedit privileges

		// special
		if (player[0].items.special < 21)
			saveTemp[SAVE_FILES_SIZE + 81 + player[0].items.special] = 1;

		for (uint p = 0; p < COUNTOF(player); ++p)
		{
			// front, rear
			for (uint i = 0; i < COUNTOF(player[p].items.weapon); ++i)
				saveTemp[SAVE_FILES_SIZE + player[p].items.weapon[i].id] = 1;

			// options
			for (uint i = 0; i < COUNTOF(player[p].items.sidekick); ++i)
				saveTemp[SAVE_FILES_SIZE + 51 + player[p].items.sidekick[i]] = 1;
		}
	}

	adjust_difficulty();

	player[0].last_items = player[0].items;
	strcpy(lastLevelName, levelName);

	JE_wipeKey();
	frameCountMax = 4;
	textGlowFont = SMALL_FONT_SHAPES;

	SDL_Color white = { 255, 255, 255 };
	set_colors(white, 254, 254);

	if (!levelTimer || levelTimerCountdown > 0 || !(episodeNum == 4))
		JE_playSampleNum(V_LEVEL_END);
	else
		play_song(21);

	// (Tyrian3D: the modern UI's results title, and the rows as each shows.)
	plain_label(level_results.title, bonusLevel ? miscText[17-1] : all_players_alive() ? miscText[27-1] : miscText[62-1],
	            sizeof(level_results.title));
	level_results_publish();

	if (bonusLevel)
	{
		JE_outTextGlow(VGAScreenSeg, 20, 20, miscText[17-1]);
	}
	else if (all_players_alive())
	{
		sprintf(tempStr, "%s %s", miscText[27-1], levelName); // "Completed"
		JE_outTextGlow(VGAScreenSeg, 20, 20, tempStr);
	}
	else
	{
		sprintf(tempStr, "%s %s", miscText[62-1], levelName); // "Exiting"
		JE_outTextGlow(VGAScreenSeg, 20, 20, tempStr);
	}

	if (twoPlayerMode)
	{
		for (uint i = 0; i < 2; ++i)
		{
			level_results_money(miscText[40 + i], player[i].cash);
			snprintf(tempStr, sizeof(tempStr), "%s %lu", miscText[40 + i], player[i].cash);
			JE_outTextGlow(VGAScreenSeg, 30, 50 + 20 * i, tempStr);
		}
	}
	else
	{
		level_results_money(miscText[28-1], player[0].cash);
		sprintf(tempStr, "%s %lu", miscText[28-1], player[0].cash);
		JE_outTextGlow(VGAScreenSeg, 30, 50, tempStr);
	}

	if (timedBattleMode)
	{
		x = (levelTimerCountdown / 10) * 100;
		level_results_money(miscTextB[6], x);
		sprintf(tempStr, "%s %d", miscTextB[6], x);
		JE_outTextGlow(VGAScreenSeg, 40, 75, tempStr);
		player[0].cash += x;
	}

	temp = (totalEnemy == 0) ? 0 : roundf(enemyKilled * 100 / totalEnemy);
	{
		char percent[16];
		snprintf(percent, sizeof(percent), "%d%%", temp);
		level_results.percent = temp;
		level_results_row(miscText[63-1], percent);
	}
	sprintf(tempStr, "%s %d%%", miscText[63-1], temp);
	JE_outTextGlow(VGAScreenSeg, 40, 90, tempStr);

	if (!constantPlay)
		editorLevel += temp / 5;

	if (timedBattleMode)
	{
		for (temp = 1; temp <= *player[0].lives; temp++)
		{
			JE_playSampleNum(S_ITEM);
			x = 20 + 15 * temp;
			y = 115;

			for (i = -15; i <= 10; i++)
			{
				setDelay(frameCountMax);

				blit_sprite_hv(VGAScreenSeg, x, y, OPTION_SHAPES, 46, 0x9, i);

				if (JE_anyButton())
					frameCountMax = 0;

				JE_showVGA();

				wait_delay();
			}
			for (i = 10; i >= 0; i--)
			{
				setDelay(frameCountMax);

				blit_sprite_hv(VGAScreenSeg, x, y, OPTION_SHAPES, 46, 0x9, i);

				if (JE_anyButton())
					frameCountMax = 0;

				JE_showVGA();

				wait_delay();
			}
		}
		x = *player[0].lives * 1000;
		level_results_money(miscTextB[7], x);
		sprintf(tempStr, "%s %d", miscTextB[7], x);
		JE_outTextGlow(VGAScreenSeg, 120, 120, tempStr);
		player[0].cash += x;
	}
	else if (!onePlayerAction && !twoPlayerMode)
	{
		level_results.cubes = 0;
		level_results_publish();
		JE_outTextGlow(VGAScreenSeg, 30, 120, miscText[4-1]);   /*Cubes*/

		if (cubeMax > 0)
		{
			if (cubeMax > 4)
				cubeMax = 4;

			if (frameCountMax != 0)
				frameCountMax = 1;

			for (temp = 1; temp <= cubeMax; temp++)
			{
				NETWORK_KEEP_ALIVE();

				level_results.cubes = temp;
				level_results_publish();
				JE_playSampleNum(S_ITEM);
				x = 20 + 30 * temp;
				y = 135;
				JE_drawCube(VGAScreenSeg, x, y, 9, 0);
				JE_showVGA();

				for (i = -15; i <= 10; i++)
				{
					setDelay(frameCountMax);

					blit_sprite_hv(VGAScreenSeg, x, y, OPTION_SHAPES, 25, 0x9, i);

					if (JE_anyButton())
						frameCountMax = 0;

					JE_showVGA();

					wait_delay();
				}
				for (i = 10; i >= 0; i--)
				{
					setDelay(frameCountMax);

					blit_sprite_hv(VGAScreenSeg, x, y, OPTION_SHAPES, 25, 0x9, i);

					if (JE_anyButton())
						frameCountMax = 0;

					JE_showVGA();

					wait_delay();
				}
			}
		}
		else
		{
			JE_outTextGlow(VGAScreenSeg, 50, 135, miscText[15-1]);
		}

	}

	if (frameCountMax != 0)
	{
		frameCountMax = 6;
		temp = 1;
	}
	else
	{
		temp = 0;
	}
	temp2 = twoPlayerMode ? 150 : 160;
	JE_outTextGlow(VGAScreenSeg, 90, temp2, miscText[5-1]);
	level_results.prompt = true;
	level_results_publish();

	if (!constantPlay && !rogue_automatic())  // Tyrian3D: whole rogue runs for tests
	{
		do
		{
			setDelay(1);

			NETWORK_KEEP_ALIVE();

			wait_delay();
		} while (!(JE_anyButton() || (frameCountMax == 0 && temp == 1)));
	}

	wait_noinput(false, false, true); // TODO: should up the joystick repeat temporarily instead

	fade_black(15);
	JE_clr256(VGAScreen);
	ui_menu_release();  // Tyrian3D
}

void JE_drawCube(SDL_Surface * screen, JE_word x, JE_word y, JE_byte filter, JE_byte brightness)
{
	blit_sprite_dark(screen, x + 4, y + 4, OPTION_SHAPES, 25, false);
	blit_sprite_dark(screen, x + 3, y + 3, OPTION_SHAPES, 25, false);
	blit_sprite_hv(screen, x, y, OPTION_SHAPES, 25, filter, brightness);
}

void JE_handleChat(void)
{
	// STUB(); Annoying piece of crap =P
}

bool str_pop_int(char *str, int *val)
{
	bool success = false;

	char buf[256];
	assert(strlen(str) < sizeof(buf));

	// grab the value from str
	char *end;
	*val = strtol(str, &end, 10);

	if (end != str)
	{
		success = true;

		// shift the rest to the beginning
		strcpy(buf, end);
		strcpy(str, buf);
	}

	return success;
}

void JE_operation(JE_byte slot)
{
	JE_byte flash;
	char stemp[21];
	char tempStr[51];

	if (!performSave)
	{
		if (saveFiles[slot-1].level > 0)
		{
			gameJustLoaded = true;
			JE_loadGame(slot);
			gameLoaded = true;
		}
	}
	else if (slot % 11 != 0)
	{
		strcpy(stemp, "              ");
		memcpy(stemp, saveFiles[slot-1].name, strlen(saveFiles[slot-1].name));
		temp = strlen(stemp);
		while (stemp[temp-1] == ' ' && --temp);

		flash = 8 * 16 + 10;

		wait_noinput(false, true, false);

		JE_barShade(VGAScreen, 65, 55, 255, 155);

		bool quit = false;
		while (!quit)
		{
			service_SDL_events(true);

			blit_sprite(VGAScreen, 50, 50, OPTION_SHAPES, 35);  // message box

			JE_textShade(VGAScreen, 60, 55, miscText[1-1], 11, 4, DARKEN);
			JE_textShade(VGAScreen, 70, 70, levelName, 11, 4, DARKEN);

			do
			{
				flash = (flash == 8 * 16 + 10) ? 8 * 16 + 2 : 8 * 16 + 10;
				temp3 = (temp3 == 6) ? 2 : 6;

				strcpy(tempStr, miscText[2-1]);
				strncat(tempStr, stemp, temp);
				JE_outText(VGAScreen, 65, 89, tempStr, 8, 3);
				tempW = 65 + JE_textWidth(tempStr, TINY_FONT);
				JE_barShade(VGAScreen, tempW + 2, 90, tempW + 6, 95);
				fill_rectangle_xy(VGAScreen, tempW + 1, 89, tempW + 5, 94, flash);

				int text_x = 54 + 45 - (JE_textWidth(miscText[9], FONT_SHAPES) / 2);
				JE_outTextAdjust(VGAScreen, text_x, 128, miscText[9], 15, -5, FONT_SHAPES, true);

				text_x = 149 + 45 - (JE_textWidth(miscText[10], FONT_SHAPES) / 2);
				JE_outTextAdjust(VGAScreen, text_x, 128, miscText[10], 15, -5, FONT_SHAPES, true);

				// Tyrian3D: the question for the modern UI: the name typed so far, its caret flashing.
				{
					char name[21];
					SDL_strlcpy(name, stemp, SDL_min((size_t)temp + 1, sizeof(name)));
					shop_dialog_publish(miscText[1 - 1], levelName, miscText[2 - 1], name, flash == 8 * 16 + 10, -1);
				}

				for (int i = 0; i < 14; i++)
				{
					setDelay(1);

					push_joysticks_as_keyboard();
					service_wait_delay();

					JE_mouseStart();
					JE_showVGA();
					JE_mouseReplace();

					if (newkey || newmouse || new_text)
						break;
				}
			} while (!newkey && !newmouse && !new_text);

			if (mouseButton > 0)
			{
				if (lastmouse_x > 56 && lastmouse_x < 142 && lastmouse_y > 123 && lastmouse_y < 149)
				{
					quit = true;
					if (JE_saveRequest(slot, stemp))
						JE_saveGame(slot, stemp);
				}
				else if (lastmouse_x > 151 && lastmouse_x < 237 && lastmouse_y > 123 && lastmouse_y < 149)
				{
					quit = true;
					JE_playSampleNum(S_SPRING);
				}
			}
			else if (new_text)
			{
				for (size_t ti = 0U; last_text[ti] != '\0'; ++ti)
				{
					const char c = (unsigned char)last_text[ti] <= 127U ? toupper(last_text[ti]) : 0;
					if ((c == ' ' || font_ascii[(unsigned char)c] != -1) &&
					    temp < 14)
					{
						JE_playSampleNum(S_CURSOR);
						stemp[temp] = c;
						temp += 1;
					}
				}
			}
			else if (newkey)
			{
				switch (lastkey_scan)
				{
					case SDL_SCANCODE_BACKSPACE:
					case SDL_SCANCODE_DELETE:
						if (temp)
						{
							temp--;
							stemp[temp] = ' ';
							JE_playSampleNum(S_CLICK);
						}
						break;
					case SDL_SCANCODE_ESCAPE:
						quit = true;
						JE_playSampleNum(S_SPRING);
						break;
					case SDL_SCANCODE_RETURN:
						quit = true;
						if (JE_saveRequest(slot, stemp))
							JE_saveGame(slot, stemp);
						break;
					default:
						break;
				}
			}
		}
	}

	wait_noinput(false, true, false);
}

void JE_inGameDisplays(void)
{
	char stemp[21];
	char tempstr[256];

	for (uint i = 0; i < ((twoPlayerMode && !galagaMode) ? 2 : 1); ++i)
	{
		snprintf(tempstr, sizeof(tempstr), "%lu", player[i].cash);

		if (smoothies[6-1])
			JE_textShade(VGAScreen, 30 + 200 * i, 175, tempstr, 8, 8, FULL_SHADE);
		else
			JE_textShade(VGAScreen, 30 + 200 * i, 175, tempstr, 2, 4, FULL_SHADE);
	}

	// Tyrian3D: the displays the game draws while drawing the playfield (the special weapon's ready light,
	// player two's charge), in a frame the 3D view captures held back to here (l3d_hud_sprite; under what
	// follows, as the game draws them before it).
	l3d_hud_sprites_draw(VGAScreen);

	/*Special Weapon?*/
	if (player[0].items.special > 0)
		blit_sprite2x2(VGAScreen, 25, 1, spriteSheet10, special[player[0].items.special].itemgraphic);

	/*Lives Left*/
	if (onePlayerAction || twoPlayerMode)
	{
		for (int temp = 0; temp < (onePlayerAction ? 1 : 2); temp++)
		{
			const uint extra_lives = *player[temp].lives - 1;

			int y = (temp == 0 && player[0].items.special > 0) ? 35 : 15;
			tempW = (temp == 0) ? 30: 270;

			if (extra_lives >= 5)
			{
				blit_sprite2(VGAScreen, tempW, y, spriteSheet9, 285);
				tempW = (temp == 0) ? 45 : 250;
				sprintf(tempstr, "%d", extra_lives);
				JE_textShade(VGAScreen, tempW, y + 3, tempstr, 15, 1, FULL_SHADE);
			}
			else if (extra_lives >= 1)
			{
				for (uint i = 0; i < extra_lives; ++i)
				{
					blit_sprite2(VGAScreen, tempW, y, spriteSheet9, 285);

					tempW += (temp == 0) ? 12 : -12;
				}
			}

			strcpy(stemp, (temp == 0) ? miscText[49-1] : miscText[50-1]);
			if (isNetworkGame)
			{
				strcpy(stemp, JE_getName(temp+1));
			}

			tempW = (temp == 0) ? 28 : (285 - JE_textWidth(stemp, TINY_FONT));
			JE_textShade(VGAScreen, tempW, y - 7, stemp, 2, 6, FULL_SHADE);
		}
	}

	/*Super Bombs!!*/
	for (uint i = 0; i < COUNTOF(player); ++i)
	{
		int x = (i == 0) ? 30 : 270;

		for (uint j = player[i].superbombs; j > 0; --j)
		{
			blit_sprite2(VGAScreen, x, 160, spriteSheet9, 304);
			x += (i == 0) ? 12 : -12;
		}
	}

	if (youAreCheating)
	{
		JE_outText(VGAScreen, 90, 170, "Cheaters always prosper.", 3, 4);
	}
}

void JE_mainKeyboardInput(void)
{
	JE_gammaCheck();

	/* { Network Request Commands } */

	if (!isNetworkGame)
	{
		/* { Edited Ships } for Player 1 */
		if (extraAvail && keysactive[SDL_SCANCODE_TAB] && !isNetworkGame && !superTyrian)
		{
			for (x = SDL_SCANCODE_1; x <= SDL_SCANCODE_0; x++)
			{
				if (keysactive[x])
				{
					int z = x - SDL_SCANCODE_1 + 1;
					player[0].items.ship = 90 + z;                     /*Ships*/
					z = (z - 1) * 15;
					player[0].items.weapon[FRONT_WEAPON].id = extraShips[z + 1];
					player[0].items.weapon[REAR_WEAPON].id = extraShips[z + 2];
					player[0].items.special = extraShips[z + 3];
					player[0].items.sidekick[LEFT_SIDEKICK] = extraShips[z + 4];
					player[0].items.sidekick[RIGHT_SIDEKICK] = extraShips[z + 5];
					player[0].items.generator = extraShips[z + 6];
					/*Armor*/
					player[0].items.shield = extraShips[z + 8];
					memset(shotMultiPos, 0, sizeof(shotMultiPos));

					if (player[0].weapon_mode > JE_portConfigs())
						player[0].weapon_mode = 1;

					tempW = player[0].armor;
					JE_getShipInfo();
					if (player[0].armor > tempW && editShip1)
						player[0].armor = tempW;
					else
						editShip1 = true;

					SDL_Surface *temp_surface = VGAScreen;
					VGAScreen = VGAScreenSeg;
					JE_wipeShieldArmorBars();
					JE_drawArmor();
					JE_drawShield();
					VGAScreen = temp_surface;
					JE_drawOptions();

					keysactive[x] = false;
				}
			}
		}

		/* for Player 2 */
		if (extraAvail && keysactive[SDL_SCANCODE_CAPSLOCK] && !isNetworkGame && !superTyrian)
		{
			for (x = SDL_SCANCODE_1; x <= SDL_SCANCODE_0; x++)
			{
				if (keysactive[x])
				{
					int z = x - SDL_SCANCODE_1 + 1;
					player[1].items.ship = 90 + z;
					z = (z - 1) * 15;
					player[1].items.weapon[FRONT_WEAPON].id = extraShips[z + 1];
					player[1].items.weapon[REAR_WEAPON].id = extraShips[z + 2];
					player[1].items.special = extraShips[z + 3];
					player[1].items.sidekick[LEFT_SIDEKICK] = extraShips[z + 4];
					player[1].items.sidekick[RIGHT_SIDEKICK] = extraShips[z + 5];
					player[1].items.generator = extraShips[z + 6];
					/*Armor*/
					player[1].items.shield = extraShips[z + 8];
					memset(shotMultiPos, 0, sizeof(shotMultiPos));

					if (player[1].weapon_mode > JE_portConfigs())
						player[1].weapon_mode = 1;

					tempW = player[1].armor;
					JE_getShipInfo();
					if (player[1].armor > tempW && editShip2)
						player[1].armor = tempW;
					else
						editShip2 = true;

					SDL_Surface *temp_surface = VGAScreen;
					VGAScreen = VGAScreenSeg;
					JE_wipeShieldArmorBars();
					JE_drawArmor();
					JE_drawShield();
					VGAScreen = temp_surface;
					JE_drawOptions();

					keysactive[x] = false;
				}
			}
		}
	}

	/* { In-Game Help } */
	if (keysactive[SDL_SCANCODE_F1])
	{
		if (isNetworkGame)
		{
			helpRequest = true;
		}
		else
		{
			JE_inGameHelp();
			skipStarShowVGA = true;
		}
	}

	/* {!Activate Nort Ship!} */
	if (keysactive[SDL_SCANCODE_F2] && keysactive[SDL_SCANCODE_F4] && keysactive[SDL_SCANCODE_F6] && keysactive[SDL_SCANCODE_F7] &&
	    keysactive[SDL_SCANCODE_F9] && keysactive[SDL_SCANCODE_BACKSLASH] && keysactive[SDL_SCANCODE_SLASH])
	{
		if (isNetworkGame)
		{
			nortShipRequest = true;
		}
		else
		{
			player[0].items.ship = 12;                     // Nort Ship
			player[0].items.special = 13;                  // Astral Zone
			player[0].items.weapon[FRONT_WEAPON].id = 36;  // NortShip Super Pulse
			player[0].items.weapon[REAR_WEAPON].id = 37;   // NortShip Spreader
			shipGr = 1;
		}
	}

	/* {Cheating} */
	if (!isNetworkGame && !twoPlayerMode && !superTyrian && superArcadeMode == SA_NONE)
	{
		if (keysactive[SDL_SCANCODE_F2] && keysactive[SDL_SCANCODE_F3] && keysactive[SDL_SCANCODE_F6])
		{
			youAreCheating = !youAreCheating;
			keysactive[SDL_SCANCODE_F2] = false;
		}

		if (keysactive[SDL_SCANCODE_F2] && keysactive[SDL_SCANCODE_F3] && (keysactive[SDL_SCANCODE_F4] || keysactive[SDL_SCANCODE_F5]))
		{
			for (uint i = 0; i < COUNTOF(player); ++i)
				player[i].armor = 0;

			youAreCheating = !youAreCheating;
			JE_drawTextWindow(miscText[63-1]);
		}

		if (constantPlay && keysactive[SDL_SCANCODE_C])
		{
			youAreCheating = !youAreCheating;
			keysactive[SDL_SCANCODE_C] = false;
		}
	}

	if (superTyrian)
	{
		youAreCheating = false;
	}

	/* {Personal Commands} */

	/* {DEBUG} */
	if (keysactive[SDL_SCANCODE_F10] && keysactive[SDL_SCANCODE_BACKSPACE])
	{
		keysactive[SDL_SCANCODE_F10] = false;
		debug = !debug;

		debugHist = 1;
		debugHistCount = 1;

		/* YKS: clock ticks since midnight replaced by SDL_GetTicks */
		lastDebugTime = SDL_GetTicks();
	}

	/* {CHEAT-SKIP LEVEL} */
	if (keysactive[SDL_SCANCODE_F2] && keysactive[SDL_SCANCODE_F6] && (keysactive[SDL_SCANCODE_F7] || keysactive[SDL_SCANCODE_F8]) && !keysactive[SDL_SCANCODE_F9] &&
	    !superTyrian && superArcadeMode == SA_NONE)
	{
		if (isNetworkGame)
		{
			skipLevelRequest = true;
		}
		else
		{
			levelTimer = true;
			levelTimerCountdown = 0;
			endLevel = true;
			levelEnd = 40;
		}
	}

	/* pause game */
	pause_pressed = pause_pressed || keysactive[SDL_SCANCODE_P];

	/* in-game setup */
	ingamemenu_pressed = ingamemenu_pressed || keysactive[SDL_SCANCODE_ESCAPE];

	if (keysactive[SDL_SCANCODE_BACKSPACE])
	{
		/* toggle screenshot pause */
		if (keysactive[SDL_SCANCODE_NUMLOCKCLEAR])
			superPause = !superPause;

		/* {SMOOTHIES} */
		if (keysactive[SDL_SCANCODE_F12] && keysactive[SDL_SCANCODE_SCROLLLOCK])
		{
			for (temp = SDL_SCANCODE_2; temp <= SDL_SCANCODE_9; temp++)
				if (keysactive[temp])
					smoothies[temp-SDL_SCANCODE_2] = !smoothies[temp-SDL_SCANCODE_2];
			if (keysactive[SDL_SCANCODE_0])
				smoothies[8] = !smoothies[8];
		}
		else

		/* {CYCLE THROUGH FILTER COLORS} */
		if (keysactive[SDL_SCANCODE_MINUS])
		{
			if (levelFilter == -99)
			{
				levelFilter = 0;
			}
			else
			{
				levelFilter++;
				if (levelFilter == 16)
					levelFilter = -99;
			}
		}
		else

		/* {HYPER-SPEED} */
		if (keysactive[SDL_SCANCODE_1])
		{
			fastPlay++;
			if (fastPlay > 2)
				fastPlay = 0;
			keysactive[SDL_SCANCODE_1] = false;
			JE_setNewGameSpeed();
		}

		/* {IN-GAME RANDOM MUSIC SELECTION} */
		if (keysactive[SDL_SCANCODE_SCROLLLOCK])
			play_song(mt_rand() % MUSIC_NUM);
	}
}

void JE_pauseGame(void)
{
	mouseSetRelative(false);

	JE_boolean done = false;
	JE_word mouseX, mouseY;

	SDL_Surface *temp_surface = VGAScreen;
	VGAScreen = VGAScreenSeg; /* side-effect of game_screen */

	//tempScreenSeg = VGAScreenSeg; // sega000
	if (!superPause)
	{
		JE_dString(VGAScreenSeg, 120, 90, miscText[22], FONT_SHAPES);

		// Tyrian3D: for the modern UI (ui.h).
		if (ui_modern())
		{
			char title[48];
			plain_label(title, miscText[22], sizeof(title));
			UIMenu *ui = ui_menu_begin(UI_SCREEN_LEVEL_PAUSE, title);
			ui->selected = -1;
			ui_menu_publish(ui, VGAScreenSeg, VGAScreenSeg);
		}

		VGAScreen = VGAScreenSeg;
		JE_showVGA();
	}

	set_volume(tyrMusicVolume / 2, fxVolume);

#ifdef WITH_NETWORK
	if (isNetworkGame)
	{
		network_prepare(PACKET_GAME_PAUSE);
		network_send(4);  // PACKET_GAME_PAUSE

		while (true)
		{
			service_SDL_events(false);

			if (packet_in[0] && SDLNet_Read16(&packet_in[0]->data[0]) == PACKET_GAME_PAUSE)
			{
				network_update();
				break;
			}

			network_update();
			network_check();

			SDL_Delay(16);
		}
	}
#endif

	wait_noinput(false, false, true); // TODO: should up the joystick repeat temporarily instead

	int shown_again = 0;  // (Tyrian3D: the modern UI's plate shown on now and then: it pulses)
	do
	{
		setDelay(2);

		push_joysticks_as_keyboard();
		service_SDL_events(true);

		if ((newkey && lastkey_scan != SDL_SCANCODE_LCTRL && lastkey_scan != SDL_SCANCODE_RCTRL && lastkey_scan != SDL_SCANCODE_LALT && lastkey_scan != SDL_SCANCODE_RALT) ||
		    JE_mousePosition(&mouseX, &mouseY) > 0)
		{
#ifdef WITH_NETWORK
			if (isNetworkGame)
			{
				network_prepare(PACKET_WAITING);
				network_send(4);  // PACKET_WAITING
			}
#endif
			done = true;
		}

#ifdef WITH_NETWORK
		if (isNetworkGame)
		{
			network_check();

			if (packet_in[0] && SDLNet_Read16(&packet_in[0]->data[0]) == PACKET_WAITING)
			{
				network_check();

				done = true;
			}
		}
#endif

		// (After the input is looked at, as ever: the time the loop takes stays the same.)
		if (!done && !superPause && ui_modern() && ++shown_again % 3 == 0)
		{
			VGAScreen = VGAScreenSeg;
			JE_showVGA();
		}

		wait_delay();
	} while (!done);

#ifdef WITH_NETWORK
	if (isNetworkGame)
	{
		while (!network_is_sync())
		{
			service_SDL_events(false);

			network_check();
			SDL_Delay(16);
		}
	}
#endif

	set_volume(tyrMusicVolume, fxVolume);

	//skipStarShowVGA = true;

	VGAScreen = temp_surface; /* side-effect of game_screen */

	mouseSetRelative(true);
}

// Tyrian3D: the ship the mouse moves directly (settings3d.mouse_direct), or NULL, and where the
// pointer last put it (or was put at it).
static Player *mouse_ship = NULL;
static JE_integer pointer_placed_x = -1000, pointer_placed_y = -1000;

// The ship's bounds, as JE_playerMovement keeps it in them.
static int ship_max_y(int playerNum_)
{
	return isNetworkGame && playerNum_ == 1 ? 154 : 160;
}

// Where the pointer puts the ship (its top left, as the game keeps it, within its bounds).
static bool pointer_ship_position(int playerNum_, float *x, float *y)
{
	float px, py;
	if (!mouse_pointer_game(&px, &py))
		return false;
	// (the ship's centre is 7 pixels in; the bounds as JE_playerMovement's, the wide playfield's)
	*x = SDL_clamp(px - 7, 40.0f - l3d_field_left(), 256.0f + l3d_field_right());
	*y = SDL_clamp(py - 7, 10.0f - l3d_field_ahead, (float)ship_max_y(playerNum_));
	return true;
}

void player_pointer_lead(float lead[2])
{
	lead[0] = lead[1] = 0;
	float x, y;
	if (mouse_ship == NULL || !settings3d.mouse_direct || endLevel || !mouse_pointer_moved() ||
	    !pointer_ship_position(mouse_ship == &player[0] ? 1 : 2, &x, &y))
		return;
	lead[0] = x - mouse_ship->x;
	lead[1] = y - mouse_ship->y;
}

// The ship moved by the controls (keys, a digital pad): seen from the side (the 3D view turned
// clockwise, the level scrolling to the right), right is up the level and down is right on it.
// What moves the ship otherwise (the autopilot, constant play) goes in the level's terms.
static void controls_move(Player *this_player, int dx, int dy)
{
	if (l3d_sideways && l3d_enabled)
	{
		this_player->x += dy;
		this_player->y -= dx;
	}
	else
	{
		this_player->x += dx;
		this_player->y += dy;
	}
}

// The maps' offsets on the wide playfield (l3d_field_wide), held still: layer 1's 14 columns at
// x 24c - 48 + ofs cover 0-319 for ofs 32-48 (32: to the map's right edge, as far right as the
// original shows it), layer 2 (the sky enemies' too) the middle of the original's 7-54, layer 3's
// 15 columns at 24c - 72 + ofs for 32-72.
#define WIDE_OFS1 32
#define WIDE_OFS2 34
#define WIDE_OFS3 48

void JE_playerMovement(Player *this_player,
                       JE_byte inputDevice,
                       JE_byte playerNum_,
                       JE_word shipGr_,
                       Sprite2_array *shipGrPtr_,
                       JE_word *mouseX_, JE_word *mouseY_)
{
	JE_integer mouseXC, mouseYC;
	JE_integer accelXC, accelYC;
	bool pointer_moved = false;  // Tyrian3D: the direct mouse's pointer moved this tick

	if (playerNum_ == 2 || !twoPlayerMode)
	{
		tempW = weaponPort[this_player->items.weapon[REAR_WEAPON].id].opnum;

		if (this_player->weapon_mode > tempW)
			this_player->weapon_mode = 1;
	}

#ifdef WITH_NETWORK
	if (isNetworkGame && thisPlayerNum == playerNum_)
	{
		network_state_prepare();
		memset(&packet_state_out[0]->data[4], 0, 10);
	}
#endif

redo:

	if (isNetworkGame)
	{
		inputDevice = 0;
	}

	mouseXC = 0;
	mouseYC = 0;
	accelXC = 0;
	accelYC = 0;

	bool link_gun_analog = false;
	float link_gun_angle = 0;

	/* Draw Player */
	if (!this_player->is_alive)
	{
		if (this_player->exploding_ticks > 0)
		{
			--this_player->exploding_ticks;

			if (levelEndFxWait > 0)
			{
				levelEndFxWait--;
			}
			else
			{
				levelEndFxWait = (mt_rand() % 6) + 3;
				if ((mt_rand() % 3) == 1)
					soundQueue[6] = S_EXPLOSION_9;
				else
					soundQueue[5] = S_EXPLOSION_11;
			}

			int explosion_x = this_player->x + (mt_rand() % 32) - 16;
			int explosion_y = this_player->y + (mt_rand() % 32) - 16;
			JE_setupExplosionLarge(false, 0, explosion_x, explosion_y + 7);
			JE_setupExplosionLarge(false, 0, this_player->x, this_player->y + 7);

			if (levelEnd > 0)
				levelEnd--;
		}
		else
		{
			if (twoPlayerMode || onePlayerAction)  // if arcade mode
			{
				if (*this_player->lives > 1)  // respawn if any extra lives
				{
					--(*this_player->lives);

					reallyEndLevel = false;
					shotMultiPos[playerNum_-1] = 0;
					calc_purple_balls_needed(this_player);
					twoPlayerLinked = false;
					if (galagaMode)
						twoPlayerMode = false;
					this_player->y = 160;
					this_player->invulnerable_ticks = 100;
					this_player->is_alive = true;
					endLevel = false;

					if (galagaMode || episodeNum == 4)
						this_player->armor = this_player->initial_armor;
					else
						this_player->armor = this_player->initial_armor / 2;

					if (galagaMode)
						this_player->shield = 0;
					else
						this_player->shield = this_player->shield_max / 2;

					VGAScreen = VGAScreenSeg; /* side-effect of game_screen */
					JE_drawArmor();
					JE_drawShield();
					VGAScreen = game_screen; /* side-effect of game_screen */
					goto redo;
				}
				else
				{
					if (galagaMode)
						twoPlayerMode = false;
					if (allPlayersGone && isNetworkGame)
						reallyEndLevel = true;
				}

			}
		}
	}
	else if (constantDie)
	{
		// finished exploding?  start dying again
		if (this_player->exploding_ticks == 0)
		{
			this_player->shield = 0;

			if (this_player->armor > 0)
			{
				--this_player->armor;
			}
			else
			{
				this_player->is_alive = false;
				this_player->exploding_ticks = 60;
				levelEnd = 40;
			}

			JE_wipeShieldArmorBars();
			VGAScreen = VGAScreenSeg; /* side-effect of game_screen */
			JE_drawArmor();
			VGAScreen = game_screen; /* side-effect of game_screen */

			// as if instant death weren't enough, player also gets infinite lives in order to enjoy an infinite number of deaths -_-
			if (*player[0].lives < 11)
				++(*player[0].lives);
		}
	}

	if (!this_player->is_alive)
	{
		explosionFollowAmountX = explosionFollowAmountY = 0;
		return;
	}

	if (!endLevel)
	{
		*mouseX_ = this_player->x;
		*mouseY_ = this_player->y;
		button[1-1] = false;
		button[2-1] = false;
		button[3-1] = false;
		button[4-1] = false;

		/* --- Movement Routine Beginning --- */

		if (!isNetworkGame || playerNum_ == thisPlayerNum)
		{
			if (endLevel)
			{
				this_player->y -= 2;
			}
			else
			{
				if (record_demo || play_demo)
					inputDevice = 1;  // keyboard is required device for demo recording

				// demo playback input
				if (play_demo)
				{
					if (!replay_demo_keys())
					{
						endLevel = true;
						levelEnd = 40;
					}
				}

				/* joystick input */
				if ((inputDevice == 0 || inputDevice >= 3) && joysticks > 0)
				{
					int j = inputDevice  == 0 ? 0 : inputDevice - 3;
					int j_max = inputDevice == 0 ? joysticks : inputDevice - 3 + 1;
					for (; j < j_max; j++)
					{
						poll_joystick(j);

						if (joystick[j].analog)
						{
							mouseXC += joystick_axis_reduce(j, joystick[j].x);
							mouseYC += joystick_axis_reduce(j, joystick[j].y);

							link_gun_analog = joystick_analog_angle(j, &link_gun_angle);
						}
						else
						{
							controls_move(this_player,
							              (joystick[j].direction[3] ? -CURRENT_KEY_SPEED : 0) + (joystick[j].direction[1] ? CURRENT_KEY_SPEED : 0),
							              (joystick[j].direction[0] ? -CURRENT_KEY_SPEED : 0) + (joystick[j].direction[2] ? CURRENT_KEY_SPEED : 0));
						}

						button[0] |= joystick[j].action[0];
						button[1] |= joystick[j].action[2];
						button[2] |= joystick[j].action[3];
						button[3] |= joystick[j].action_pressed[1];

						ingamemenu_pressed |= joystick[j].action_pressed[4];
						pause_pressed |= joystick[j].action_pressed[5];
					}
				}

				service_SDL_events(false);

				/* mouse input */
				if ((inputDevice == 0 || inputDevice == 2) && has_mouse)
				{
					button[0] |= mouse_pressed[0];
					button[1] |= mouse_pressed[1];
					button[2] |= mouse_pressed[2];
					button[3] |= mouse_pressed[3];

					Sint32 mouseXR;
					Sint32 mouseYR;
					mouseGetRelativePosition(&mouseXR, &mouseYR);
					if (settings3d.mouse_direct && !isNetworkGame)
					{
						pointer_moved = mouse_take_pointer_moved();
						mouse_ship = this_player;
					}
					else
					{
						mouseXC += mouseXR;
						mouseYC += mouseYR;
						if (mouse_ship == this_player)
							mouse_ship = NULL;
					}
				}

				/* keyboard input */
				if ((inputDevice == 0 || inputDevice == 1) && !play_demo)
				{
					controls_move(this_player,
					              (keysactive[keySettings[KEY_SETTING_LEFT]] ? -CURRENT_KEY_SPEED : 0) +
					              (keysactive[keySettings[KEY_SETTING_RIGHT]] ? CURRENT_KEY_SPEED : 0),
					              (keysactive[keySettings[KEY_SETTING_UP]] ? -CURRENT_KEY_SPEED : 0) +
					              (keysactive[keySettings[KEY_SETTING_DOWN]] ? CURRENT_KEY_SPEED : 0));

					button[0] = button[0] || keysactive[keySettings[KEY_SETTING_FIRE]];
					button[3] = button[3] || keysactive[keySettings[KEY_SETTING_CHANGE_FIRE]];
					button[1] = button[1] || keysactive[keySettings[KEY_SETTING_LEFT_SIDEKICK]];
					button[2] = button[2] || keysactive[keySettings[KEY_SETTING_RIGHT_SIDEKICK]];

					bool autopilot_fire = true;
					if (dev_autopilot())
					{
						int dx = 0, dy = 0;
						bool fire = false;
						dev_autopilot_steer(this_player->x, this_player->y, CURRENT_KEY_SPEED, &dx, &dy, &fire);
						this_player->x += dx;
						this_player->y += dy;
						button[0] = button[0] || fire;
						autopilot_fire = fire;
					}

					if (constantPlay)
					{
						// Tyrian3D: the autopilot steers by itself (constant play's drift held it at the left
						// edge) and holds fire with TYR3D_AUTOPILOT=nofire
						if (autopilot_fire)
							for (unsigned int i = 0; i < 4; i++)
								button[i] = true;

						if (!dev_autopilot())
						{
							++this_player->y;
							this_player->x += constantLastX;
						}
					}

					// TODO: check if demo recording still works
					if (record_demo)
					{
						bool new_input = false;

						for (unsigned int i = 0; i < 8; i++)
						{
							bool temp = demo_keys & (1 << i);
							if (temp != keysactive[keySettings[i]])
								new_input = true;
						}

						demo_keys_wait++;

						if (new_input)
						{
							Uint8 temp2[2] = { demo_keys_wait >> 8, demo_keys_wait };
							fwrite_u8(temp2, 2, demo_file);

							demo_keys = 0;
							for (unsigned int i = 0; i < 8; i++)
								demo_keys |= keysactive[keySettings[i]] ? (1 << i) : 0;

							fwrite_u8(&demo_keys, 1, demo_file);

							demo_keys_wait = 0;
						}
					}
				}

				if (l3d_sideways && l3d_enabled)
				{
					// Tyrian3D: seen from the side, the analog stick and the mouse turned too (see
					// controls_move).
					const JE_integer cx = mouseXC;
					mouseXC = mouseYC;
					mouseYC = -cx;
				}

				if (smoothies[9-1])
				{
					*mouseY_ = this_player->y - (*mouseY_ - this_player->y);
					mouseYC = -mouseYC;
				}

				accelXC += this_player->x - *mouseX_;
				accelYC += this_player->y - *mouseY_;

				if (mouseXC > 30)
					mouseXC = 30;
				else if (mouseXC < -30)
					mouseXC = -30;
				if (mouseYC > 30)
					mouseYC = 30;
				else if (mouseYC < -30)
					mouseYC = -30;

				if (mouseXC > 0)
					this_player->x += (mouseXC + 3) / 4;
				else if (mouseXC < 0)
					this_player->x += (mouseXC - 3) / 4;
				if (mouseYC > 0)
					this_player->y += (mouseYC + 3) / 4;
				else if (mouseYC < 0)
					this_player->y += (mouseYC - 3) / 4;

				// Tyrian3D: the ship goes where the pointer is, which moves as on the desktop (it is
				// hidden and kept in the window), without the original's speed limit and momentum
				// (settings3d.mouse_direct).
				float pointer_x, pointer_y;
				if (pointer_moved && pointer_ship_position(playerNum_, &pointer_x, &pointer_y))
				{
					this_player->x = (JE_integer)lroundf(pointer_x);
					this_player->y = (JE_integer)lroundf(pointer_y);
					this_player->x_velocity = this_player->y_velocity = 0;
					accelXC = accelYC = 0;
					pointer_placed_x = this_player->x;
					pointer_placed_y = this_player->y;
				}

				if (mouseXC > 3)
					accelXC++;
				else if (mouseXC < -2)
					accelXC--;
				if (mouseYC > 2)
					accelYC++;
				else if (mouseYC < -2)
					accelYC--;

			}   /*endLevel*/

#ifdef WITH_NETWORK
			if (isNetworkGame && playerNum_ == thisPlayerNum)
			{
				Uint16 buttons = 0;
				for (int i = 4 - 1; i >= 0; i--)
				{
					buttons <<= 1;
					buttons |= button[i];
				}

				SDLNet_Write16(this_player->x - *mouseX_, &packet_state_out[0]->data[4]);
				SDLNet_Write16(this_player->y - *mouseY_, &packet_state_out[0]->data[6]);
				SDLNet_Write16(accelXC,                   &packet_state_out[0]->data[8]);
				SDLNet_Write16(accelYC,                   &packet_state_out[0]->data[10]);
				SDLNet_Write16(buttons,                   &packet_state_out[0]->data[12]);

				this_player->x = *mouseX_;
				this_player->y = *mouseY_;

				button[0] = false;
				button[1] = false;
				button[2] = false;
				button[3] = false;

				accelXC = 0;
				accelYC = 0;
			}
#endif
		}  /*isNetworkGame*/

		/* --- Movement Routine Ending --- */

		moveOk = true;

#ifdef WITH_NETWORK
		if (isNetworkGame && !network_state_is_reset())
		{
			if (playerNum_ != thisPlayerNum)
			{
				if (thisPlayerNum == 2)
					difficultyLevel = SDLNet_Read16(&packet_state_in[0]->data[16]);

				Uint16 buttons = SDLNet_Read16(&packet_state_in[0]->data[12]);
				for (int i = 0; i < 4; i++)
				{
					button[i] = buttons & 1;
					buttons >>= 1;
				}

				this_player->x += (Sint16)SDLNet_Read16(&packet_state_in[0]->data[4]);
				this_player->y += (Sint16)SDLNet_Read16(&packet_state_in[0]->data[6]);
				accelXC = (Sint16)SDLNet_Read16(&packet_state_in[0]->data[8]);
				accelYC = (Sint16)SDLNet_Read16(&packet_state_in[0]->data[10]);
			}
			else
			{
				Uint16 buttons = SDLNet_Read16(&packet_state_out[network_delay]->data[12]);
				for (int i = 0; i < 4; i++)
				{
					button[i] = buttons & 1;
					buttons >>= 1;
				}

				this_player->x += (Sint16)SDLNet_Read16(&packet_state_out[network_delay]->data[4]);
				this_player->y += (Sint16)SDLNet_Read16(&packet_state_out[network_delay]->data[6]);
				accelXC = (Sint16)SDLNet_Read16(&packet_state_out[network_delay]->data[8]);
				accelYC = (Sint16)SDLNet_Read16(&packet_state_out[network_delay]->data[10]);
			}
		}
#endif

		/*Street-Fighter codes*/
		JE_SFCodes(playerNum_, this_player->x, this_player->y, *mouseX_, *mouseY_);

		if (moveOk)
		{
			/* END OF MOVEMENT ROUTINES */

			/*Linking Routines*/

			if (twoPlayerMode && !twoPlayerLinked && this_player->x == *mouseX_ && this_player->y == *mouseY_ &&
			    abs(player[0].x - player[1].x) < 8 && abs(player[0].y - player[1].y) < 8 &&
			    player[0].is_alive && player[1].is_alive && !galagaMode)
			{
				twoPlayerLinked = true;
			}

			if (playerNum_ == 1 && (button[3-1] || button[2-1]) && !galagaMode)
				twoPlayerLinked = false;

			if (twoPlayerMode && twoPlayerLinked && playerNum_ == 2 &&
			    (this_player->x != *mouseX_ || this_player->y != *mouseY_))
			{
				if (button[0])
				{
					if (link_gun_analog)
					{
						linkGunDirec = link_gun_angle;
					}
					else
					{
						JE_real tempR;

						if (abs(this_player->x - *mouseX_) > abs(this_player->y - *mouseY_))
							tempR = (this_player->x - *mouseX_ > 0) ? M_PI_2 : (M_PI + M_PI_2);
						else
							tempR = (this_player->y - *mouseY_ > 0) ? 0 : M_PI;

						if (fabsf(linkGunDirec - tempR) < 0.3f)
							linkGunDirec = tempR;
						else if (linkGunDirec < tempR && linkGunDirec - tempR > -3.24f)
							linkGunDirec += 0.2f;
						else if (linkGunDirec - tempR < M_PI)
							linkGunDirec -= 0.2f;
						else
							linkGunDirec += 0.2f;
					}

					if (linkGunDirec >= (2 * M_PI))
						linkGunDirec -= (2 * M_PI);
					else if (linkGunDirec < 0)
						linkGunDirec += (2 * M_PI);
				}
				else if (!galagaMode)
				{
					twoPlayerLinked = false;
				}
			}
		}
	}

	if (levelEnd > 0 && all_players_dead())
		reallyEndLevel = true;

	/* End Level Fade-Out */
	if (this_player->is_alive && endLevel)
	{
		if (levelEnd == 0)
		{
			reallyEndLevel = true;
		}
		else
		{
			this_player->y -= levelEndWarp;
			if (this_player->y < -200 - l3d_field_ahead)
				reallyEndLevel = true;

			int trail_spacing = 1;
			int trail_y = this_player->y;
			int num_trails = abs(41 - levelEnd);
			if (num_trails > 20)
				num_trails = 20;

			for (int i = 0; i < num_trails; i++)
			{
				trail_y += trail_spacing;
				trail_spacing++;
			}

			for (int i = 1; i < num_trails; i++)
			{
				trail_y -= trail_spacing;
				trail_spacing--;

				if (trail_y > 0 && trail_y < 170)
				{
					if (shipGr_ == 0)
					{
						blit_sprite2x2(VGAScreen, this_player->x - 17, trail_y - 7, *shipGrPtr_, 13);
						blit_sprite2x2(VGAScreen, this_player->x + 7 , trail_y - 7, *shipGrPtr_, 51);
					}
					else if (shipGr_ == 1)
					{
						blit_sprite2x2(VGAScreen, this_player->x - 17, trail_y - 7, *shipGrPtr_, 220);
						blit_sprite2x2(VGAScreen, this_player->x + 7 , trail_y - 7, *shipGrPtr_, 222);
					}
					else
					{
						blit_sprite2x2(VGAScreen, this_player->x - 5, trail_y - 7, *shipGrPtr_, shipGr_);
					}
				}
			}
		}
	}

	// Tyrian3D: the debug flight records the input, or plays it back when it rewinds.
	if (!endLevel && (!isNetworkGame || playerNum_ == thisPlayerNum))
		debug_flight_input(playerNum_, this_player, &accelXC, &accelYC);

	if (play_demo)
	{
		// (Tyrian3D: the modern HUD shows it its own way.)
		const L3DLayerType layer = l3d_current_layer();
		l3d_phase(L3D_HUD);
		JE_dString(VGAScreen, 115, 10, miscText[7], SMALL_FONT_SHAPES); // insert coin
		l3d_phase(layer);
		ui_note_insert_coin(miscText[7]);
	}

	if (this_player->is_alive && !endLevel)
	{
		if (!twoPlayerLinked || playerNum_ < 2)
		{
			if (!twoPlayerMode || shipGr2 != 0)  // if not dragonwing
			{
				if (this_player->sidekick[LEFT_SIDEKICK].style == 0)
				{
					this_player->sidekick[LEFT_SIDEKICK].x = *mouseX_ - 14;
					this_player->sidekick[LEFT_SIDEKICK].y = *mouseY_;
				}

				if (this_player->sidekick[RIGHT_SIDEKICK].style == 0)
				{
					this_player->sidekick[RIGHT_SIDEKICK].x = *mouseX_ + 16;
					this_player->sidekick[RIGHT_SIDEKICK].y = *mouseY_;
				}
			}

			if (this_player->x_friction_ticks > 0)
			{
				--this_player->x_friction_ticks;
			}
			else
			{
				this_player->x_friction_ticks = 1;

				if (this_player->x_velocity < 0)
					++this_player->x_velocity;
				else if (this_player->x_velocity > 0)
					--this_player->x_velocity;
			}

			if (this_player->y_friction_ticks > 0)
			{
				--this_player->y_friction_ticks;
			}
			else
			{
				this_player->y_friction_ticks = 2;

				if (this_player->y_velocity < 0)
					++this_player->y_velocity;
				else if (this_player->y_velocity > 0)
					--this_player->y_velocity;
			}

			this_player->x_velocity += accelXC;
			this_player->y_velocity += accelYC;

			this_player->x_velocity = MIN(MAX(-4, this_player->x_velocity), 4);
			this_player->y_velocity = MIN(MAX(-4, this_player->y_velocity), 4);

			this_player->x += this_player->x_velocity;
			this_player->y += this_player->y_velocity;

			// if player moved, add new ship x, y history entry
			if (this_player->x - *mouseX_ != 0 || this_player->y - *mouseY_ != 0)
			{
				for (uint i = 1; i < COUNTOF(player->old_x); ++i)
				{
					this_player->old_x[i - 1] = this_player->old_x[i];
					this_player->old_y[i - 1] = this_player->old_y[i];
				}
				this_player->old_x[COUNTOF(player->old_x) - 1] = this_player->x;
				this_player->old_y[COUNTOF(player->old_x) - 1] = this_player->y;
			}
		}
		else  /*twoPlayerLinked*/
		{
			if (shipGr_ == 0)
				this_player->x = player[0].x - 1;
			else
				this_player->x = player[0].x;
			this_player->y = player[0].y + 8;

			this_player->x_velocity = player[0].x_velocity;
			this_player->y_velocity = 4;

			// turret direction marker/shield
			shotMultiPos[SHOT_MISC] = 0;
			b = player_shot_create(0, SHOT_MISC, this_player->x + 1 + roundf(sinf(linkGunDirec + 0.2f) * 26), this_player->y + roundf(cosf(linkGunDirec + 0.2f) * 26), *mouseX_, *mouseY_, 148, playerNum_);
			shotMultiPos[SHOT_MISC] = 0;
			b = player_shot_create(0, SHOT_MISC, this_player->x + 1 + roundf(sinf(linkGunDirec - 0.2f) * 26), this_player->y + roundf(cosf(linkGunDirec - 0.2f) * 26), *mouseX_, *mouseY_, 148, playerNum_);
			shotMultiPos[SHOT_MISC] = 0;
			b = player_shot_create(0, SHOT_MISC, this_player->x + 1 + roundf(sinf(linkGunDirec) * 26), this_player->y + roundf(cosf(linkGunDirec) * 26), *mouseX_, *mouseY_, 147, playerNum_);

			if (shotRepeat[SHOT_REAR] > 0)
			{
				--shotRepeat[SHOT_REAR];
			}
			else if (button[1-1])
			{
				shotMultiPos[SHOT_REAR] = 0;
				b = player_shot_create(0, SHOT_REAR, this_player->x + 1 + roundf(sinf(linkGunDirec) * 20), this_player->y + roundf(cosf(linkGunDirec) * 20), *mouseX_, *mouseY_, linkGunWeapons[this_player->items.weapon[REAR_WEAPON].id-1], playerNum_);
				player_shot_set_direction(b, this_player->items.weapon[REAR_WEAPON].id, linkGunDirec);
			}
		}
	}

	if (!endLevel)
	{
		if (this_player->x > 256 + l3d_field_right())
		{
			this_player->x = 256 + l3d_field_right();
			constantLastX = -constantLastX;
		}
		if (this_player->x < 40 - l3d_field_left())
		{
			this_player->x = 40 - l3d_field_left();
			constantLastX = -constantLastX;
		}

		if (isNetworkGame && playerNum_ == 1)
		{
			if (this_player->y > 154)
				this_player->y = 154;
		}
		else
		{
			if (this_player->y > 160)
				this_player->y = 160;
		}

		if (this_player->y < 10 - l3d_field_ahead)
			this_player->y = 10 - l3d_field_ahead;

		// Tyrian3D: a ship the keyboard (or anything but the direct mouse) moved takes the pointer
		// along, so the ship doesn't jump when the mouse moves again.
		if (mouse_ship == this_player && settings3d.mouse_direct && !pointer_moved &&
		    (this_player->x != pointer_placed_x || this_player->y != pointer_placed_y))
		{
			mouse_place_pointer(this_player->x + 7, this_player->y + 7);
			pointer_placed_x = this_player->x;
			pointer_placed_y = this_player->y;
		}

		// Determines the ship banking sprite to display, depending on horizontal velocity and acceleration
		int ship_banking = this_player->x_velocity / 2 + (this_player->x - *mouseX_) / 6;
		ship_banking = MAX(-2, MIN(ship_banking, 2));

		int ship_sprite = ship_banking * 2 + shipGr_;

		// Tyrian3D: ships can be shown as a 3D model, which replaces the sprite and its shadow. Ships
		// drawn in two halves (the Dragonwing, shipGr_ 0, and the Nort Ship, 1) are centred on the
		// pair, as the others; without a model they get volume half by half.
		const bool two_part = shipGr_ <= 1;
		const M3DAppearance ship_look = m3d_ship_appearance(shipGr_ == 0 ? M3D_SHIP_DRAGONWING : this_player->items.ship);
		const bool ship_ghost = this_player->invulnerable_ticks > 0;  // drawn half transparent
		const bool ship_model = ship_look.model >= 0
			? l3d_add_object(ship_look.model, this_player->x + 7, this_player->y + 7, ship_look.height,
			                 ship_look.yaw, ship_look.banking ? ship_banking * 12.0f : 0.0f, 0)
			: !two_part && ship_look.model == M3D_VOLUME &&
			  l3d_add_volume(shipGrPtr_, ship_sprite, true, V3D_STYLE_RAISED, this_player->x + 7, this_player->y + 7,
			                 ship_look.height, 0.0f, 0.0f, 0);
		if (ship_model && ship_ghost)
			l3d_ghost_last_object();
		const bool follows_mouse = mouse_ship == this_player && settings3d.mouse_direct;
		float ship_vx = 0, ship_vy = 0;
		if (ship_model)
			l3d_key_last_object(L3D_KEY_PLAYER + playerNum_ * 4, &ship_vx, &ship_vy);
		if (ship_model && follows_mouse)
			l3d_pointer_last_object();
		// Tyrian3D: the engines' glow behind the ship, which lights the ground under it.
		static const Uint8 engine_glow[3] = { 255, 150, 64 };
		if (ship_model && !ship_ghost && settings3d.effects &&
		    l3d_add_rgb_glow(this_player->x + 7, this_player->y + 19, 10.0f, 0.45f, engine_glow, ship_vx, ship_vy) &&
		    follows_mouse)
			l3d_pointer_last_glow();
		bool two_part_volume = false;
		if (two_part && ship_look.model == M3D_VOLUME)
		{
			two_part_volume = l3d_add_volume(shipGrPtr_, shipGr_ == 0 ? ship_sprite + 13 : 220, true, V3D_STYLE_RAISED,
			                                 this_player->x - 5, this_player->y + 7, ship_look.height, 0.0f, 0.0f, 0);
			if (two_part_volume)
				l3d_key_last_object(L3D_KEY_PLAYER + playerNum_ * 4 + 1, NULL, NULL);
			if (two_part_volume && follows_mouse)
				l3d_pointer_last_object();
			if (two_part_volume && ship_ghost)
				l3d_ghost_last_object();
			if (two_part_volume && l3d_add_volume(shipGrPtr_, shipGr_ == 0 ? ship_sprite + 51 : 222, true, V3D_STYLE_RAISED,
			                                      this_player->x + 19, this_player->y + 7, ship_look.height, 0.0f, 0.0f, 0))
			{
				l3d_key_last_object(L3D_KEY_PLAYER + playerNum_ * 4 + 2, NULL, NULL);
				if (ship_ghost)
					l3d_ghost_last_object();
				if (follows_mouse)
					l3d_pointer_last_object();
			}
		}

		explosionFollowAmountX = this_player->x - this_player->last_x_explosion_follow;
		explosionFollowAmountY = this_player->y - this_player->last_y_explosion_follow;

		if (explosionFollowAmountY < 0)
			explosionFollowAmountY = 0;

		this_player->last_x_explosion_follow = this_player->x;
		this_player->last_y_explosion_follow = this_player->y;

		if (two_part_volume || (two_part && ship_model))
			;  // the volumes and models have real shadows
		else if (shipGr_ == 0)
		{
			if (background2)
			{
				blit_sprite2x2_darken(VGAScreen, this_player->x - 17 - mapX2Ofs + 30, this_player->y - 7 + shadowYDist, *shipGrPtr_, ship_sprite + 13);
				blit_sprite2x2_darken(VGAScreen, this_player->x + 7 - mapX2Ofs + 30, this_player->y - 7 + shadowYDist, *shipGrPtr_, ship_sprite + 51);
				if (superWild)
				{
					blit_sprite2x2_darken(VGAScreen, this_player->x - 16 - mapX2Ofs + 30, this_player->y - 7 + shadowYDist, *shipGrPtr_, ship_sprite + 13);
					blit_sprite2x2_darken(VGAScreen, this_player->x + 6 - mapX2Ofs + 30, this_player->y - 7 + shadowYDist, *shipGrPtr_, ship_sprite + 51);
				}
			}
		}
		else if (shipGr_ == 1)
		{
			if (background2)
			{
				blit_sprite2x2_darken(VGAScreen, this_player->x - 17 - mapX2Ofs + 30, this_player->y - 7 + shadowYDist, *shipGrPtr_, 220);
				blit_sprite2x2_darken(VGAScreen, this_player->x + 7 - mapX2Ofs + 30, this_player->y - 7 + shadowYDist, *shipGrPtr_, 222);
			}
		}
		else if (!ship_model)
		{
			if (background2)
			{
				blit_sprite2x2_darken(VGAScreen, this_player->x - 5 - mapX2Ofs + 30, this_player->y - 7 + shadowYDist, *shipGrPtr_, ship_sprite);
				if (superWild)
				{
					blit_sprite2x2_darken(VGAScreen, this_player->x - 4 - mapX2Ofs + 30, this_player->y - 7 + shadowYDist, *shipGrPtr_, ship_sprite);
				}
			}
		}

		if (this_player->invulnerable_ticks > 0)
		{
			--this_player->invulnerable_ticks;

			if (two_part_volume || (two_part && ship_model))
				;
			else if (shipGr_ == 0)
			{
				blit_sprite2x2_blend(VGAScreen, this_player->x - 17, this_player->y - 7, *shipGrPtr_, ship_sprite + 13);
				blit_sprite2x2_blend(VGAScreen, this_player->x + 7 , this_player->y - 7, *shipGrPtr_, ship_sprite + 51);
			}
			else if (shipGr_ == 1)
			{
				blit_sprite2x2_blend(VGAScreen, this_player->x - 17, this_player->y - 7, *shipGrPtr_, 220);
				blit_sprite2x2_blend(VGAScreen, this_player->x + 7 , this_player->y - 7, *shipGrPtr_, 222);
			}
			else if (!ship_model)
				blit_sprite2x2_blend(VGAScreen, this_player->x - 5, this_player->y - 7, *shipGrPtr_, ship_sprite);
		}
		else
		{
			if (shipGr_ == 0)
			{
				if (!two_part_volume && !ship_model)
				{
					blit_sprite2x2(VGAScreen, this_player->x - 17, this_player->y - 7, *shipGrPtr_, ship_sprite + 13);
					blit_sprite2x2(VGAScreen, this_player->x + 7, this_player->y - 7, *shipGrPtr_, ship_sprite + 51);
				}
			}
			else if (shipGr_ == 1)
			{
				if (!two_part_volume && !ship_model)
				{
					blit_sprite2x2(VGAScreen, this_player->x - 17, this_player->y - 7, *shipGrPtr_, 220);
					blit_sprite2x2(VGAScreen, this_player->x + 7, this_player->y - 7, *shipGrPtr_, 222);
				}

				int ship_banking = 0;
				switch (ship_sprite)
				{
				case 5:
					blit_sprite2(VGAScreen, this_player->x - 17, this_player->y + 7, *shipGrPtr_, 40);
					tempW = this_player->x - 7;
					ship_banking = -2;
					break;
				case 3:
					blit_sprite2(VGAScreen, this_player->x - 17, this_player->y + 7, *shipGrPtr_, 39);
					tempW = this_player->x - 7;
					ship_banking = -1;
					break;
				case 1:
					ship_banking = 0;
					break;
				case -1:
					blit_sprite2(VGAScreen, this_player->x + 19, this_player->y + 7, *shipGrPtr_, 58);
					tempW = this_player->x + 9;
					ship_banking = 1;
					break;
				case -3:
					blit_sprite2(VGAScreen, this_player->x + 19, this_player->y + 7, *shipGrPtr_, 59);
					tempW = this_player->x + 9;
					ship_banking = 2;
					break;
				}
				if (ship_banking != 0)  // NortSparks
				{
					if (shotRepeat[SHOT_NORTSPARKS] > 0)
					{
						--shotRepeat[SHOT_NORTSPARKS];
					}
					else
					{
						b = player_shot_create(0, SHOT_NORTSPARKS, tempW + (mt_rand() % 8) - 4, this_player->y + (mt_rand() % 8) - 4, *mouseX_, *mouseY_, 671, 1);
						shotRepeat[SHOT_NORTSPARKS] = abs(ship_banking) - 1;
					}
				}
			}
			else if (!ship_model)
			{
				blit_sprite2x2(VGAScreen, this_player->x - 5, this_player->y - 7, *shipGrPtr_, ship_sprite);
			}
		}

		/*Options Location*/
		if (playerNum_ == 2 && shipGr_ == 0)  // if dragonwing
		{
			if (this_player->sidekick[LEFT_SIDEKICK].style == 0)
			{
				this_player->sidekick[LEFT_SIDEKICK].x = this_player->x - 14 + ship_banking * 2;
				this_player->sidekick[LEFT_SIDEKICK].y = this_player->y;
			}

			if (this_player->sidekick[RIGHT_SIDEKICK].style == 0)
			{
				this_player->sidekick[RIGHT_SIDEKICK].x = this_player->x + 17 + ship_banking * 2;
				this_player->sidekick[RIGHT_SIDEKICK].y = this_player->y;
			}
		}
	}  // !endLevel

	if (moveOk)
	{
		if (this_player->is_alive)
		{
			if (!endLevel)
			{
				this_player->delta_x_shot_move = this_player->x - this_player->last_x_shot_move;
				this_player->delta_y_shot_move = this_player->y - this_player->last_y_shot_move;

				/* PLAYER SHOT Change */
				if (button[4-1])
				{
					portConfigChange = true;
					if (portConfigDone)
					{
						shotMultiPos[SHOT_REAR] = 0;

						if (superArcadeMode != SA_NONE && superArcadeMode <= SA_LASTSHIP)
						{
							shotMultiPos[SHOT_SPECIAL] = 0;
							shotMultiPos[SHOT_SPECIAL2] = 0;
							if (player[0].items.special == SASpecialWeapon[superArcadeMode-1])
							{
								player[0].items.special = SASpecialWeaponB[superArcadeMode-1];
								this_player->weapon_mode = 2;
							}
							else
							{
								player[0].items.special = SASpecialWeapon[superArcadeMode-1];
								this_player->weapon_mode = 1;
							}
						}
						else if (++this_player->weapon_mode > JE_portConfigs())
							this_player->weapon_mode = 1;

						JE_drawPortConfigButtons();
						portConfigDone = false;
					}
				}

				/* PLAYER SHOT Creation */

				/*SpecialShot*/
				if (!galagaMode)
					JE_doSpecialShot(playerNum_, &this_player->armor, &this_player->shield);

				/*Normal Main Weapons*/
				if (!(twoPlayerLinked && playerNum_ == 2))
				{
					int min, max;

					if (!twoPlayerMode)
						min = 1, max = 2;
					else
						min = max = playerNum_;

					for (temp = min - 1; temp < max; temp++)
					{
						const uint item = this_player->items.weapon[temp].id;

						if (item > 0)
						{
							if (shotRepeat[temp] > 0)
							{
								--shotRepeat[temp];
							}
							else if (button[1-1])
							{
								const uint item_power = galagaMode ? 0 : this_player->items.weapon[temp].power - 1,
								           item_mode = (temp == REAR_WEAPON) ? this_player->weapon_mode - 1 : 0;

								b = player_shot_create(item, temp, this_player->x, this_player->y, *mouseX_, *mouseY_, weaponPort[item].op[item_mode][item_power], playerNum_);
							}
						}
					}
				}

				/*Super Charge Weapons*/
				if (playerNum_ == 2)
				{

					if (!twoPlayerLinked)  // (Tyrian3D: one of the game's displays, drawn with them in the 3D view)
						l3d_hud_sprite(VGAScreen, this_player->x + (shipGr_ == 0) + 1, this_player->y - 13, &spriteSheet10,
						               77 + chargeLevel + chargeGr * 19, false);

					if (chargeGrWait > 0)
					{
						chargeGrWait--;
					}
					else
					{
						chargeGr++;
						if (chargeGr == 4)
							chargeGr = 0;
						chargeGrWait = 3;
					}

					if (chargeLevel > 0)
					{
						fill_rectangle_xy(VGAScreenSeg, 269, 107 + (chargeLevel - 1) * 3, 275, 108 + (chargeLevel - 1) * 3, 193);
					}

					if (chargeWait > 0)
					{
						chargeWait--;
					}
					else
					{
						if (chargeLevel < chargeMax)
							chargeLevel++;

						chargeWait = 28 - this_player->items.weapon[REAR_WEAPON].power * 2;
						if (difficultyLevel > DIFFICULTY_HARD)
							chargeWait -= 5;
					}

					if (chargeLevel > 0)
						fill_rectangle_xy(VGAScreenSeg, 269, 107 + (chargeLevel - 1) * 3, 275, 108 + (chargeLevel - 1) * 3, 204);

					if (shotRepeat[SHOT_P2_CHARGE] > 0)
					{
						--shotRepeat[SHOT_P2_CHARGE];
					}
					else if (button[1-1] && (!twoPlayerLinked || chargeLevel > 0))
					{
						shotMultiPos[SHOT_P2_CHARGE] = 0;
						b = player_shot_create(16, SHOT_P2_CHARGE, this_player->x, this_player->y, *mouseX_, *mouseY_, chargeGunWeapons[player[1].items.weapon[REAR_WEAPON].id-1] + chargeLevel, playerNum_);

						if (chargeLevel > 0)
							fill_rectangle_xy(VGAScreenSeg, 269, 107 + (chargeLevel - 1) * 3, 275, 108 + (chargeLevel - 1) * 3, 193);

						chargeLevel = 0;
						chargeWait = 30 - this_player->items.weapon[REAR_WEAPON].power * 2;
					}
				}

				/*SUPER BOMB*/
				temp = playerNum_;
				if (temp == 0)
					temp = 1;  /*Get whether player 1 or 2*/

				if (player[temp-1].superbombs > 0)
				{
					if (shotRepeat[SHOT_P1_SUPERBOMB + temp-1] > 0)
					{
						--shotRepeat[SHOT_P1_SUPERBOMB + temp-1];
					}
					else if (button[3-1] || button[2-1])
					{
						--player[temp-1].superbombs;
						shotMultiPos[SHOT_P1_SUPERBOMB + temp-1] = 0;
						b = player_shot_create(16, SHOT_P1_SUPERBOMB + temp-1, this_player->x, this_player->y, *mouseX_, *mouseY_, 535, playerNum_);
					}
				}

				// sidekicks

				if (this_player->sidekick[LEFT_SIDEKICK].style == 4 && this_player->sidekick[RIGHT_SIDEKICK].style == 4)
					optionSatelliteRotate += 0.2f;
				else if (this_player->sidekick[LEFT_SIDEKICK].style == 4 || this_player->sidekick[RIGHT_SIDEKICK].style == 4)
					optionSatelliteRotate += 0.15f;

				switch (this_player->sidekick[LEFT_SIDEKICK].style)
				{
				case 1:  // trailing
				case 3:
					this_player->sidekick[LEFT_SIDEKICK].x = this_player->old_x[COUNTOF(player->old_x) / 2 - 1];
					this_player->sidekick[LEFT_SIDEKICK].y = this_player->old_y[COUNTOF(player->old_x) / 2 - 1];
					break;
				case 2:  // front-mounted
					this_player->sidekick[LEFT_SIDEKICK].x = this_player->x;
					this_player->sidekick[LEFT_SIDEKICK].y = MAX(10, this_player->y - 20);
					break;
				case 4:  // orbiting
					this_player->sidekick[LEFT_SIDEKICK].x = this_player->x + roundf(sinf(optionSatelliteRotate) * 20);
					this_player->sidekick[LEFT_SIDEKICK].y = this_player->y + roundf(cosf(optionSatelliteRotate) * 20);
					break;
				}

				switch (this_player->sidekick[RIGHT_SIDEKICK].style)
				{
				case 4:  // orbiting
					this_player->sidekick[RIGHT_SIDEKICK].x = this_player->x - roundf(sinf(optionSatelliteRotate) * 20);
					this_player->sidekick[RIGHT_SIDEKICK].y = this_player->y - roundf(cosf(optionSatelliteRotate) * 20);
					break;
				case 1:  // trailing
				case 3:
					this_player->sidekick[RIGHT_SIDEKICK].x = this_player->old_x[0];
					this_player->sidekick[RIGHT_SIDEKICK].y = this_player->old_y[0];
					break;
				case 2:  // front-mounted
					if (!optionAttachmentLinked)
					{
						this_player->sidekick[RIGHT_SIDEKICK].y += optionAttachmentMove / 2;
						if (optionAttachmentMove >= -2)
						{
							if (optionAttachmentReturn)
								temp = 2;
							else
								temp = 0;

							if (this_player->sidekick[RIGHT_SIDEKICK].y > (this_player->y - 20) + 5)
							{
								temp = 2;
								optionAttachmentMove -= 1 + optionAttachmentReturn;
							}
							else if (this_player->sidekick[RIGHT_SIDEKICK].y > (this_player->y - 20) - 0)
							{
								temp = 3;
								if (optionAttachmentMove > 0)
									optionAttachmentMove--;
								else
									optionAttachmentMove++;
							}
							else if (this_player->sidekick[RIGHT_SIDEKICK].y > (this_player->y - 20) - 5)
							{
								temp = 2;
								optionAttachmentMove++;
							}
							else if (optionAttachmentMove < 2 + optionAttachmentReturn * 4)
							{
								optionAttachmentMove += 1 + optionAttachmentReturn;
							}

							if (optionAttachmentReturn)
								temp = temp * 2;
							if (abs(this_player->sidekick[RIGHT_SIDEKICK].x - this_player->x) < temp)
								temp = 1;

							if (this_player->sidekick[RIGHT_SIDEKICK].x > this_player->x)
								this_player->sidekick[RIGHT_SIDEKICK].x -= temp;
							else if (this_player->sidekick[RIGHT_SIDEKICK].x < this_player->x)
								this_player->sidekick[RIGHT_SIDEKICK].x += temp;

							if (abs(this_player->sidekick[RIGHT_SIDEKICK].y - (this_player->y - 20)) + abs(this_player->sidekick[RIGHT_SIDEKICK].x - this_player->x) < 8)
							{
								optionAttachmentLinked = true;
								soundQueue[2] = S_CLINK;
							}

							if (button[3-1])
								optionAttachmentReturn = true;
						}
						else  // sidekick needs to catch up to player
						{
							optionAttachmentMove += 1 + optionAttachmentReturn;
							JE_setupExplosion(this_player->sidekick[RIGHT_SIDEKICK].x + 1, this_player->sidekick[RIGHT_SIDEKICK].y + 10, 0, 0, false, false);
						}
					}
					else
					{
						this_player->sidekick[RIGHT_SIDEKICK].x = this_player->x;
						this_player->sidekick[RIGHT_SIDEKICK].y = this_player->y - 20;
						if (button[3-1])
						{
							optionAttachmentLinked = false;
							optionAttachmentReturn = false;
							optionAttachmentMove = -20;
							soundQueue[3] = S_WEAPON_26;
						}
					}

					if (this_player->sidekick[RIGHT_SIDEKICK].y < 10)
						this_player->sidekick[RIGHT_SIDEKICK].y = 10;
					break;
				}

				if (playerNum_ == 2 || !twoPlayerMode)  // if player has sidekicks
				{
					for (uint i = 0; i < COUNTOF(player->items.sidekick); ++i)
					{
						uint shot_i = (i == 0) ? SHOT_LEFT_SIDEKICK : SHOT_RIGHT_SIDEKICK;

						JE_OptionType *this_option = &options[this_player->items.sidekick[i]];

						// fire/refill sidekick
						if (this_option->wport > 0)
						{
							if (shotRepeat[shot_i] > 0)
							{
								--shotRepeat[shot_i];
							}
							else
							{
								const int ammo_max = this_player->sidekick[i].ammo_max;

								if (ammo_max > 0)  // sidekick has limited ammo
								{
									if (this_player->sidekick[i].ammo_refill_ticks > 0)
									{
										--this_player->sidekick[i].ammo_refill_ticks;
									}
									else  // refill one ammo
									{
										this_player->sidekick[i].ammo_refill_ticks = this_player->sidekick[i].ammo_refill_ticks_max;

										if (this_player->sidekick[i].ammo < ammo_max)
											++this_player->sidekick[i].ammo;

										// draw sidekick refill ammo gauge
										const int y = hud_sidekick_y[twoPlayerMode ? 1 : 0][i] + 13;
										draw_segmented_gauge(VGAScreenSeg, 284, y, 112, 2, 2, MAX(1, ammo_max / 10), this_player->sidekick[i].ammo);
									}

									if (button[1 + i] && this_player->sidekick[i].ammo > 0)
									{
										b = player_shot_create(this_option->wport, shot_i, this_player->sidekick[i].x, this_player->sidekick[i].y, *mouseX_, *mouseY_, this_option->wpnum + this_player->sidekick[i].charge, playerNum_);

										--this_player->sidekick[i].ammo;
										if (this_player->sidekick[i].charge > 0)
										{
											shotMultiPos[shot_i] = 0;
											this_player->sidekick[i].charge = 0;
										}
										this_player->sidekick[i].charge_ticks = 20;
										this_player->sidekick[i].animation_enabled = true;

										// draw sidekick discharge ammo gauge
										const int y = hud_sidekick_y[twoPlayerMode ? 1 : 0][i] + 13;
										fill_rectangle_xy(VGAScreenSeg, 284, y, 312, y + 2, 0);
										draw_segmented_gauge(VGAScreenSeg, 284, y, 112, 2, 2, MAX(1, ammo_max / 10), this_player->sidekick[i].ammo);
									}
								}
								else  // has infinite ammo
								{
									// Tyrian 2000: weapons with charge stages do not auto-fire
									if ((button[0] && !this_option->pwr) || button[1 + i])
									{
										b = player_shot_create(this_option->wport, shot_i, this_player->sidekick[i].x, this_player->sidekick[i].y, *mouseX_, *mouseY_, this_option->wpnum + this_player->sidekick[i].charge, playerNum_);

										if (this_player->sidekick[i].charge > 0)
										{
											shotMultiPos[shot_i] = 0;
											this_player->sidekick[i].charge = 0;
										}
										this_player->sidekick[i].charge_ticks = 20;
										this_player->sidekick[i].animation_enabled = true;
									}
								}
							}
						}
					}
				}  // end of if player has sidekicks
			}  // !endLevel
		} // this_player->is_alive
	} // moveOK

	// draw sidekicks
	if ((playerNum_ == 2 || !twoPlayerMode) && !endLevel)
	{
		for (uint i = 0; i < COUNTOF(this_player->sidekick); ++i)
		{
			JE_OptionType *this_option = &options[this_player->items.sidekick[i]];

			if (this_option->option > 0)
			{
				if (this_player->sidekick[i].animation_enabled)
				{
					if (++this_player->sidekick[i].animation_frame >= this_option->ani)
					{
						this_player->sidekick[i].animation_frame = 0;
						this_player->sidekick[i].animation_enabled = (this_option->option == 1);
					}
				}

				const int x = this_player->sidekick[i].x,
				          y = this_player->sidekick[i].y;
				const uint sprite = this_option->gr[this_player->sidekick[i].animation_frame] + this_player->sidekick[i].charge;

				// Tyrian3D: the sidekick's 3D appearance, centred where its sprite would be.
				const bool large = this_player->sidekick[i].style == 1 || this_player->sidekick[i].style == 2;
				const M3DAppearance look = m3d_sidekick_appearance(this_player->items.sidekick[i]);
				const float centre_y = large ? y + 14 : y + 7;
				// Models: turning as the animation does or spinning, recoloured, with their glow.
				float yaw = look.yaw;
				if (look.yaw_mode == M3D_YAW_FRAMES)
					yaw += this_player->sidekick[i].animation_frame * look.yaw_step;
				if (look.spin != 0)
					yaw += fmodf(look.spin * l3d_frame_number + i * 90.0f, 360.0f);
				Uint8 filter = 0;
				if (look.recolor)
					filter = (Uint8)(l3d_sprite_ramp(large ? &spriteSheet10 : &spriteSheet9, sprite, large) << 4);
				const bool sidekick_3d = look.model >= 0
					? l3d_add_object(look.model, x + 6, centre_y, look.height, yaw,
					                 this_player->sidekick[i].animation_frame * look.roll_step, filter)
					: look.model == M3D_VOLUME &&
					  l3d_add_volume(large ? &spriteSheet10 : &spriteSheet9, sprite, large, V3D_STYLE_RAISED, x + 6, centre_y,
					                 look.height, 0.0f, 0.0f, 0);

				if (sidekick_3d)
				{
					float vx, vy;
					l3d_key_last_object(L3D_KEY_SIDEKICK + playerNum_ * 4 + i, &vx, &vy);
					if (look.model >= 0 && look.glow_size != 0)
					{
						const float size = look.glow_size < 0 ? -look.glow_size * (large ? 24 : 12) : look.glow_size;
						if (look.glow_has_rgb)
							l3d_add_rgb_glow(x + 6 + look.glow_dx, centre_y + look.glow_dy, size, look.glow_strength,
							                 look.glow_rgb, vx, vy);
						else if (look.glow_color != 0)
							l3d_add_color_glow(x + 6 + look.glow_dx, centre_y + look.glow_dy, size, look.glow_strength,
							                   look.glow_color, vx, vy);
						else
						{
							l3d_add_sprite_glow(large ? &spriteSheet10 : &spriteSheet9, sprite, large, x + 6 + look.glow_dx,
							                    centre_y + look.glow_dy, size, look.glow_strength);
							l3d_last_glow_velocity(vx, vy);
						}
					}
				}
				else if (large)
					blit_sprite2x2(VGAScreen, x - 6, y, spriteSheet10, sprite);
				else
					blit_sprite2(VGAScreen, x, y, spriteSheet9, sprite);
			}

			if (--this_player->sidekick[i].charge_ticks == 0)
			{
				if (this_player->sidekick[i].charge < this_option->pwr)
					++this_player->sidekick[i].charge;
				this_player->sidekick[i].charge_ticks = 20;
			}
		}
	}
}

void JE_mainGamePlayerFunctions(void)
{
	/*PLAYER MOVEMENT/MOUSE ROUTINES*/

	if (endLevel && levelEnd > 0)
	{
		levelEnd--;
		levelEndWarp++;
	}

	/*Reset Street-Fighter commands*/
	memset(SFExecuted, 0, sizeof(SFExecuted));

	portConfigChange = false;

	if (twoPlayerMode)
	{
		JE_playerMovement(&player[0],
		                  !galagaMode ? inputDevice[0] : 0, 1, shipGr, shipGrPtr,
		                  &mouseX, &mouseY);
		JE_playerMovement(&player[1],
		                  !galagaMode ? inputDevice[1] : 0, 2, shipGr2, shipGr2ptr,
		                  &mouseXB, &mouseYB);
	}
	else
	{
		JE_playerMovement(&player[0],
		                  0, 1, shipGr, shipGrPtr,
		                  &mouseX, &mouseY);
	}

	/* == Parallax Map Scrolling == */
	JE_word tempX;
	if (twoPlayerMode)
		tempX = (player[0].x + player[1].x) / 2;
	else
		tempX = player[0].x;

	tempW = floorf((float)(260 - (tempX - 36)) / (260 - 36) * (24 * 3) - 1);
	if (l3d_field_wide)
	{
		// Tyrian3D: the wide playfield holds the maps still, each where its tiles cover the
		// whole game x 0-319 (layer 1 to its right edge; the sky between where the original's
		// parallax takes it; layer 3 inside its 15 columns).
		tempW = WIDE_OFS3;
	}
	mapX3Ofs   = tempW;
	mapX3Pos   = mapX3Ofs % 24;
	mapX3bpPos = 1 - (mapX3Ofs / 24);

	mapX2Ofs   = (tempW * 2) / 3;
	mapX2Pos   = mapX2Ofs % 24;
	mapX2bpPos = 1 - (mapX2Ofs / 24);

	if (l3d_field_wide)
	{
		mapX2Ofs   = WIDE_OFS2;
		mapX2Pos   = mapX2Ofs % 24;
		mapX2bpPos = 1 - (mapX2Ofs / 24);
	}
	oldMapXOfs = mapXOfs;
	mapXOfs    = l3d_field_wide ? WIDE_OFS1 : mapX2Ofs / 2;
	mapXPos    = mapXOfs % 24;
	mapXbpPos  = 1 - (mapXOfs / 24);

	if (background3x1)
	{
		mapX3Ofs = mapXOfs;
		mapX3Pos = mapXPos;
		mapX3bpPos = mapXbpPos - 1;
	}
}

const char *JE_getName(JE_byte pnum)
{
	if (pnum == thisPlayerNum && network_player_name[0] != '\0')
		return network_player_name;
	else if (network_opponent_name[0] != '\0')
		return network_opponent_name;

	return miscText[47 + pnum];
}

void JE_playerCollide(Player *this_player, JE_byte playerNum_)
{
	char tempStr[256];

	for (int z = 0; z < 100; z++)
	{
		if (enemyAvail[z] != 1)
		{
			int enemy_screen_x = enemy[z].ex + enemy[z].mapoffset;

			if (abs(this_player->x - enemy_screen_x) < 12 && abs(this_player->y - enemy[z].ey) < 14)
			{   /*Collide*/
				int evalue = enemy[z].evalue;
				if (evalue > 29999)
				{
					if (evalue == 30000)  // spawn dragonwing in galaga mode, otherwise just a purple ball
					{
						this_player->cash += 100;

						if (!galagaMode)
						{
							if (!rogue_purple_ball())  // Tyrian3D: experience in a rogue run
								handle_got_purple_ball(this_player);
						}
						else
						{
							// spawn the dragonwing?
							if (twoPlayerMode)
								this_player->cash += 2400;
							twoPlayerMode = true;
							twoPlayerLinked = true;
							player[1].items.weapon[REAR_WEAPON].power = 1;
							player[1].armor = 10;
							player[1].is_alive = true;
						}
						enemyAvail[z] = 1;
						soundQueue[7] = S_POWERUP;
					}
					else if (superArcadeMode != SA_NONE && evalue > 30000)
					{
						shotMultiPos[SHOT_FRONT] = 0;
						shotRepeat[SHOT_FRONT] = 10;

						tempW = SAWeapon[superArcadeMode-1][evalue - 30000-1];

						// if picked up already-owned weapon, power weapon up
						if (tempW == player[0].items.weapon[FRONT_WEAPON].id)
						{
							this_player->cash += 1000;
							power_up_weapon(this_player, FRONT_WEAPON);
						}
						// else weapon also gives purple ball
						else
						{
							handle_got_purple_ball(this_player);
						}

						player[0].items.weapon[FRONT_WEAPON].id = tempW;
						this_player->cash += 200;
						soundQueue[7] = S_POWERUP;
						enemyAvail[z] = 1;
					}
					else if (evalue > 32100)
					{
						if (playerNum_ == 1)
						{
							this_player->cash += 250;
							player[0].items.special = evalue - 32100;
							shotMultiPos[SHOT_SPECIAL] = 0;
							shotRepeat[SHOT_SPECIAL] = 10;
							shotMultiPos[SHOT_SPECIAL2] = 0;
							shotRepeat[SHOT_SPECIAL2] = 0;

							if (isNetworkGame)
								snprintf(tempStr, sizeof(tempStr), "%s %s %s", JE_getName(1), miscTextB[4-1], special[evalue - 32100].name);
							else if (twoPlayerMode)
								snprintf(tempStr, sizeof(tempStr), "%s %s", miscText[43-1], special[evalue - 32100].name);
							else
								snprintf(tempStr, sizeof(tempStr), "%s %s", miscText[64-1], special[evalue - 32100].name);
							JE_drawTextWindow(tempStr);
							soundQueue[7] = S_POWERUP;
							enemyAvail[z] = 1;
						}
					}
					else if (evalue > 32000)
					{
						if (playerNum_ == 2)
						{
							enemyAvail[z] = 1;
							if (isNetworkGame)
								snprintf(tempStr, sizeof(tempStr), "%s %s %s", JE_getName(2), miscTextB[4-1], options[evalue - 32000].name);
							else
								snprintf(tempStr, sizeof(tempStr), "%s %s", miscText[44-1], options[evalue - 32000].name);
							JE_drawTextWindow(tempStr);

							// if picked up a different sidekick than player already has, then reset sidekicks to least powerful, else power them up
							if (evalue - 32000u != player[1].items.sidekick_series)
							{
								player[1].items.sidekick_series = evalue - 32000;
								player[1].items.sidekick_level = 101;
							}
							else if (player[1].items.sidekick_level < 103)
							{
								++player[1].items.sidekick_level;
							}

							uint temp = player[1].items.sidekick_level - 100 - 1;
							for (uint i = 0; i < COUNTOF(player[1].items.sidekick); ++i)
								player[1].items.sidekick[i] = optionSelect[player[1].items.sidekick_series][temp][i];

							shotMultiPos[SHOT_LEFT_SIDEKICK] = 0;
							shotMultiPos[SHOT_RIGHT_SIDEKICK] = 0;
							JE_drawOptions();
							soundQueue[7] = S_POWERUP;
						}
						else if (onePlayerAction)
						{
							enemyAvail[z] = 1;
							snprintf(tempStr, sizeof(tempStr), "%s %s", miscText[64-1], options[evalue - 32000].name);
							JE_drawTextWindow(tempStr);

							for (uint i = 0; i < COUNTOF(player[0].items.sidekick); ++i)
								player[0].items.sidekick[i] = evalue - 32000;
							shotMultiPos[SHOT_LEFT_SIDEKICK] = 0;
							shotMultiPos[SHOT_RIGHT_SIDEKICK] = 0;

							JE_drawOptions();
							soundQueue[7] = S_POWERUP;
						}
						if (enemyAvail[z] == 1)
							this_player->cash += 250;
					}
					else if (evalue > 31000)
					{
						this_player->cash += 250;
						if (playerNum_ == 2)
						{
							if (isNetworkGame)
								snprintf(tempStr, sizeof(tempStr), "%s %s %s", JE_getName(2), miscTextB[4-1], weaponPort[evalue - 31000].name);
							else
								snprintf(tempStr, sizeof(tempStr), "%s %s", miscText[44-1], weaponPort[evalue - 31000].name);
							JE_drawTextWindow(tempStr);
							player[1].items.weapon[REAR_WEAPON].id = evalue - 31000;
							shotMultiPos[SHOT_REAR] = 0;
							enemyAvail[z] = 1;
							soundQueue[7] = S_POWERUP;
						}
						else if (onePlayerAction)
						{
							snprintf(tempStr, sizeof(tempStr), "%s %s", miscText[64-1], weaponPort[evalue - 31000].name);
							JE_drawTextWindow(tempStr);
							player[0].items.weapon[REAR_WEAPON].id = evalue - 31000;
							shotMultiPos[SHOT_REAR] = 0;
							enemyAvail[z] = 1;
							soundQueue[7] = S_POWERUP;

							if (player[0].items.weapon[REAR_WEAPON].power == 0)  // does this ever happen?
								player[0].items.weapon[REAR_WEAPON].power = 1;
						}
					}
					else if (evalue > 30000)
					{
						if (playerNum_ == 1 && twoPlayerMode)
						{
							if (isNetworkGame)
								snprintf(tempStr, sizeof(tempStr), "%s %s %s", JE_getName(1), miscTextB[4-1], weaponPort[evalue - 30000].name);
							else
								snprintf(tempStr, sizeof(tempStr), "%s %s", miscText[43-1], weaponPort[evalue - 30000].name);
							JE_drawTextWindow(tempStr);
							player[0].items.weapon[FRONT_WEAPON].id = evalue - 30000;
							shotMultiPos[SHOT_FRONT] = 0;
							enemyAvail[z] = 1;
							soundQueue[7] = S_POWERUP;
						}
						else if (onePlayerAction)
						{
							snprintf(tempStr, sizeof(tempStr), "%s %s", miscText[64-1], weaponPort[evalue - 30000].name);
							JE_drawTextWindow(tempStr);
							player[0].items.weapon[FRONT_WEAPON].id = evalue - 30000;
							shotMultiPos[SHOT_FRONT] = 0;
							enemyAvail[z] = 1;
							soundQueue[7] = S_POWERUP;
						}

						if (enemyAvail[z] == 1)
						{
							player[0].items.special = specialArcadeWeapon[evalue - 30000-1];
							if (player[0].items.special > 0)
							{
								shotMultiPos[SHOT_SPECIAL] = 0;
								shotRepeat[SHOT_SPECIAL] = 0;
								shotMultiPos[SHOT_SPECIAL2] = 0;
								shotRepeat[SHOT_SPECIAL2] = 0;
							}
							this_player->cash += 250;
						}

					}
				}
				else if (evalue > 20000)
				{
					if (twoPlayerLinked)
					{
						// share the armor evenly between linked players
						for (uint i = 0; i < COUNTOF(player); ++i)
						{
							player[i].armor += (evalue - 20000) / COUNTOF(player);
							if (player[i].armor > 28)
								player[i].armor = 28;
						}
					}
					else
					{
						this_player->armor += evalue - 20000;
						if (this_player->armor > 28)
							this_player->armor = 28;
					}
					enemyAvail[z] = 1;
					VGAScreen = VGAScreenSeg; /* side-effect of game_screen */
					JE_drawArmor();
					VGAScreen = game_screen; /* side-effect of game_screen */
					soundQueue[7] = S_POWERUP;
				}
				else if (evalue > 10000 && enemyAvail[z] == 2)
				{
					if (!bonusLevel)
					{
						if (SDL_getenv("TYR3D_LOG_JUMPS") != NULL)  // Tyrian3D dev
							printf("warp: to section %d\n", evalue - 10000);
						play_song(30);  /*Zanac*/
						bonusLevel = true;
						nextLevel = evalue - 10000;
						enemyAvail[z] = 1;
						displayTime = 150;
					}
				}
				else if (enemy[z].scoreitem)
				{
					enemyAvail[z] = 1;
					soundQueue[7] = S_ITEM;
					if (evalue == 1)
					{
						if (SDL_getenv("TYR3D_LOG_JUMPS") != NULL)  // Tyrian3D dev
							printf("data cube picked up\n");
						cubeMax++;
						soundQueue[3] = V_DATA_CUBE;
					}
					else if (evalue == -1)  // got front weapon powerup
					{
						if (isNetworkGame)
							snprintf(tempStr, sizeof(tempStr), "%s %s %s", JE_getName(1), miscTextB[4-1], miscText[45-1]);
						else if (twoPlayerMode)
							snprintf(tempStr, sizeof(tempStr), "%s %s", miscText[43-1], miscText[45-1]);
						else
							strcpy(tempStr, miscText[45-1]);
						JE_drawTextWindow(tempStr);

						power_up_weapon(&player[0], FRONT_WEAPON);
						soundQueue[7] = S_POWERUP;
					}
					else if (evalue == -2)  // got rear weapon powerup
					{
						if (isNetworkGame)
							snprintf(tempStr, sizeof(tempStr), "%s %s %s", JE_getName(2), miscTextB[4-1], miscText[46-1]);
						else if (twoPlayerMode)
							snprintf(tempStr, sizeof(tempStr), "%s %s", miscText[44-1], miscText[46-1]);
						else
							strcpy(tempStr, miscText[46-1]);
						JE_drawTextWindow(tempStr);

						power_up_weapon(twoPlayerMode ? &player[1] : &player[0], REAR_WEAPON);
						soundQueue[7] = S_POWERUP;
					}
					else if (evalue == -3)
					{
						// picked up orbiting asteroid killer
						shotMultiPos[SHOT_MISC] = 0;
						b = player_shot_create(0, SHOT_MISC, this_player->x, this_player->y, mouseX, mouseY, 104, playerNum_);
						shotAvail[z] = 0;
					}
					else if (evalue == -4)
					{
						if (player[playerNum_-1].superbombs < 10)
							++player[playerNum_-1].superbombs;
					}
					else if (evalue == -5)
					{
						player[0].items.weapon[FRONT_WEAPON].id = 25;  // HOT DOG!
						player[0].items.weapon[REAR_WEAPON].id = 26;
						player[1].items.weapon[REAR_WEAPON].id = 26;

						player[0].last_items = player[0].items;

						for (uint i = 0; i < COUNTOF(player); ++i)
							player[i].weapon_mode = 1;

						memset(shotMultiPos, 0, sizeof(shotMultiPos));
					}
					else if (twoPlayerLinked)
					{
						// players get equal share of pick-up cash when linked
						for (uint i = 0; i < COUNTOF(player); ++i)
							player[i].cash += evalue / COUNTOF(player);
					}
					else
					{
						this_player->cash += evalue;
					}
					JE_setupExplosion(enemy_screen_x, enemy[z].ey, 0, enemyDat[enemy[z].enemytype].explosiontype, true, false);
				}
				else if (this_player->invulnerable_ticks == 0 && enemyAvail[z] == 0 &&
				         (enemyDat[enemy[z].enemytype].explosiontype & 1) == 0) // explosiontype & 1 == 0: not ground enemy
				{
					int armorleft = enemy[z].armorleft;
					if (armorleft > damageRate)
						armorleft = damageRate;

					JE_playerDamage(armorleft, this_player);

					// player ship gets push-back from collision
					if (enemy[z].armorleft > 0)
					{
						this_player->x_velocity += (enemy[z].exc * enemy[z].armorleft) / 2;
						this_player->y_velocity += (enemy[z].eyc * enemy[z].armorleft) / 2;
					}

					int armorleft2 = enemy[z].armorleft;
					if (armorleft2 == 255)
						armorleft2 = 30000;

					temp = enemy[z].linknum;
					if (temp == 0)
						temp = 255;

					b = z;

					if (armorleft2 > armorleft)
					{
						// damage enemy
						if (enemy[z].armorleft != 255)
							enemy[z].armorleft -= armorleft;
						soundQueue[5] = S_ENEMY_HIT;
					}
					else
					{
						// kill enemy
						for (temp2 = 0; temp2 < 100; temp2++)
						{
							if (enemyAvail[temp2] != 1)
							{
								temp3 = enemy[temp2].linknum;
								if (temp2 == b ||
									(temp != 255 &&
									 (temp == temp3 || temp - 100 == temp3 ||
									  (temp3 > 40 && temp3 / 20 == temp / 20 && temp3 <= temp))))
								{
									int enemy_screen_x = enemy[temp2].ex + enemy[temp2].mapoffset;

									enemy[temp2].linknum = 0;

									enemyAvail[temp2] = 1;

									if (enemyDat[enemy[temp2].enemytype].esize == 1)
									{
										JE_setupExplosionLarge(enemy[temp2].enemyground, enemy[temp2].explonum, enemy_screen_x, enemy[temp2].ey);
										soundQueue[6] = S_EXPLOSION_9;
									}
									else
									{
										JE_setupExplosion(enemy_screen_x, enemy[temp2].ey, 0, 1, false, false);
										soundQueue[5] = S_EXPLOSION_4;
									}
								}
							}
						}
						enemyAvail[z] = 1;
					}
				}
			}

		}
	}
}
