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
#include "menus.h"

#include "config.h"
#include "episodes.h"
#include "font.h"
#include "fonthand.h"
#include "joystick.h"
#include "keyboard.h"
#include "mouse.h"
#include "network.h"
#include "nortsong.h"
#include "opentyr.h"
#include "palette.h"
#include "picload.h"
#include "rogue.h"
#include "sprite.h"
#include "ui.h"
#include "vga256d.h"
#include "video.h"

char episode_name[EPISODE_MAX + 1][31];  // Tyrian3D: + episodes 6 and 7
char difficulty_name[7][21];
char gameplay_name[GAMEPLAY_NAME_COUNT][26];
char timed_battle_name[4][23];

/*
 * Tyrian3D: each menu as it shows, for the modern UI (ui.h): its items where the original takes the
 * mouse on them, which can't be chosen, what each does; over the menu's picture (VGAScreen2).
 */
static void publish_choices(UIScreenKind kind, const char *title, const char *const *texts, const char *const *hints,
                            size_t count, size_t selected, const int *widths, const int *xs, int y_items, int dy_items,
                            int h_item, const bool *disabled, int pips)
{
	UIMenu *menu = ui_menu_begin(kind, title);
	for (size_t i = 0; i < count; ++i)
	{
		UIItem *item = ui_menu_add(menu, UI_ITEM_ACTION, texts[i], xs[i], y_items + dy_items * (int)i, widths[i], h_item);
		if (hints != NULL && hints[i] != NULL)
			SDL_strlcpy(item->hint, hints[i], sizeof(item->hint));
		item->disabled = disabled != NULL && disabled[i];
		if (pips > 0)
		{
			item->pips = pips;
			item->pips_on = (int)i + 1;
		}
	}
	menu->selected = (int)selected;
	ui_menu_publish(menu, VGAScreen, VGAScreen2);
}

bool gameplaySelect(void)
{
	enum MenuItemIndex
	{
		MENU_ITEM_1_PLAYER_FULL_GAME = 0,
		MENU_ITEM_1_PLAYER_ARCADE,
		MENU_ITEM_1_PLAYER_TIMED_BATTLE,
		MENU_ITEM_2_PLAYER_ARCADE,
		MENU_ITEM_NETWORK,
		MENU_ITEM_ROGUE,  // Tyrian3D (rogue.h)
		MENU_ITEM_TWIN_STICK,  // Tyrian3D (player.h twin_stick)
	};

	if (shopSpriteSheet.data == NULL)
		JE_loadCompShapes(&shopSpriteSheet, '1');  // need mouse pointer sprites

	bool restart = true;

	// Tyrian3D: the items shown, without network play (the user: take the modem play option away).
	int shown[COUNTOF(gameplay_name)];
	size_t menuItemsCount = 0;
	for (int id = 0; id <= MENU_ITEM_ROGUE; ++id)
	{
		if (id == MENU_ITEM_2_PLAYER_ARCADE)
			shown[menuItemsCount++] = MENU_ITEM_TWIN_STICK;  // (the one-player modes first)
		if (id != MENU_ITEM_NETWORK)
			shown[menuItemsCount++] = id;
	}
	size_t selectedIndex = 0;

	const int xCenter = 320 / 2;
	const int yMenuHeader = 20;
	const int yMenuItems = 54;
	const int dyMenuItems = 24;
	const int hMenuItem = 13;
	int wMenuItem[COUNTOF(gameplay_name) - 1 + 1] = { 0 };

	for (; ; )
	{
		if (restart)
		{
			JE_loadPic(VGAScreen2, 2, false);

			// Draw header.
			draw_font_hv_shadow(VGAScreen2, xCenter, yMenuHeader, gameplay_name[0], large_font, centered, 15, -3, false, 2);
		}

		// Restore background and header.
		memcpy(VGAScreen->pixels, VGAScreen2->pixels, (size_t)VGAScreen->pitch * VGAScreen->h);

		// Draw menu items.
		for (size_t i = 0; i < menuItemsCount; ++i)
		{
			const char *const text = shown[i] == MENU_ITEM_ROGUE ? "Rogue Run" : shown[i] == MENU_ITEM_TWIN_STICK ? "1 Player Twin-Stick"
			                       : gameplay_name[shown[i] + 1];

			wMenuItem[i] = JE_textWidth(text, normal_font);
			const int y = yMenuItems + dyMenuItems * i;

			const bool selected = i == selectedIndex;
			const bool disabled = false;

			// Tyrian3D: drawn centred (as it was at xCenter - wMenuItem[i] / 2), so the 3D view's text is.
			draw_font_hv_shadow(VGAScreen, xCenter, y, text, normal_font, centered, 15, -4 + (selected ? 2 : 0) + (disabled ? -4 : 0), false, 2);
		}
		{
			static const char *const hints[] = {
				"The story: the shop between levels, your ship and savings kept.",
				"Straight into the levels, power-ups instead of the shop.",
				"Score as much as you can before the time runs out.",
				"Two ships side by side, power-ups instead of the shop.",
				"Not available in this version.",
				"Three acts, one life: a new route and new cards every run.",
				"The linked ship alone: keys or left stick fly, mouse or right stick aim the turret.",
			};
			const char *texts[COUNTOF(gameplay_name)];
			const char *shown_hints[COUNTOF(gameplay_name)];
			int xs[COUNTOF(gameplay_name)];
			bool disabled[COUNTOF(gameplay_name)];
			for (size_t i = 0; i < menuItemsCount; ++i)
			{
				texts[i] = shown[i] == MENU_ITEM_ROGUE ? "Rogue Run" : shown[i] == MENU_ITEM_TWIN_STICK ? "1 Player Twin-Stick"
				         : gameplay_name[shown[i] + 1];
				shown_hints[i] = hints[shown[i]];
				xs[i] = xCenter - wMenuItem[i] / 2;
				disabled[i] = false;
			}
			publish_choices(UI_SCREEN_PLAYERS, gameplay_name[0], texts, shown_hints, menuItemsCount, selectedIndex, wMenuItem, xs,
			                yMenuItems, dyMenuItems, hMenuItem, disabled, 0);
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

		bool action = false;
		bool cancel = false;

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

				cancel = true;
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

				cancel = true;
				break;
			}
			default:
				break;
			}
		}

		if (action)
		{
			const int chosen = shown[selectedIndex];
			switch (chosen)
			{
			case MENU_ITEM_1_PLAYER_FULL_GAME:
			case MENU_ITEM_1_PLAYER_ARCADE:
			case MENU_ITEM_1_PLAYER_TIMED_BATTLE:
			case MENU_ITEM_2_PLAYER_ARCADE:
			case MENU_ITEM_TWIN_STICK:
			{
				JE_playSampleNum(S_SELECT);

				fade_black(10);

				onePlayerAction = chosen == MENU_ITEM_1_PLAYER_ARCADE;
				timedBattleMode = chosen == MENU_ITEM_1_PLAYER_TIMED_BATTLE;
				twoPlayerMode = chosen == MENU_ITEM_2_PLAYER_ARCADE || chosen == MENU_ITEM_TWIN_STICK;
				twinStickMode = chosen == MENU_ITEM_TWIN_STICK;  // (a two-player game, one player: player.h)
				return true;
			}
			case MENU_ITEM_NETWORK:
			{
				JE_playSampleNum(S_SPRING);
				break;
			}
			case MENU_ITEM_ROGUE:
			{
				JE_playSampleNum(S_SELECT);

				fade_black(10);

				if (rogue_menu())
					return true;

				restart = true;
				break;
			}
			default:
				break;
			}
		}

		if (cancel)
		{
			fade_black(15);

			return false;
		}
	}
}

bool episodeSelect(void)
{
	if (shopSpriteSheet.data == NULL)
		JE_loadCompShapes(&shopSpriteSheet, '1');  // need mouse pointer sprites

	bool restart = true;

	// Tyrian3D: episodes 6 and 7 too, when their files are there, then the custom episodes (episodes.h;
	// not over the network: the other player's game may not have them).
	int episodeNumbers[EPISODE_MAX];
	size_t episodeCount = 0;
	for (int e = 1; e <= EPISODE_MAX; ++e)
		if (e <= EPISODE_AVAILABLE || episodeAvail[e - 1])
			episodeNumbers[episodeCount++] = e;
	const size_t customCount = isNetworkGame ? 0 : (size_t)custom_episode_count;
	const size_t menuItemsCount = episodeCount + customCount;
	size_t selectedIndex = 0;
	// (The extras, episode 7 and the custom episodes, the modern UI shows beside the others: Left and Right
	// go between them.)
	size_t firstExtra = episodeCount;
	for (size_t i = 0; i < episodeCount; ++i)
		if (episodeNumbers[i] >= 7)
		{
			firstExtra = i;
			break;
		}
	size_t lastMain = 0;

	char customNames[CUSTOM_EPISODE_MAX][48];
	const char *itemNames[EPISODE_MAX + CUSTOM_EPISODE_MAX];
	bool itemDisabled[EPISODE_MAX + CUSTOM_EPISODE_MAX];
	for (size_t i = 0; i < menuItemsCount; ++i)
	{
		if (i < episodeCount)
		{
			itemNames[i] = episode_name[episodeNumbers[i]];
			itemDisabled[i] = !episodeAvail[episodeNumbers[i] - 1];
		}
		else
		{
			snprintf(customNames[i - episodeCount], sizeof(*customNames), "Custom: %s", custom_episodes[i - episodeCount].title);
			itemNames[i] = customNames[i - episodeCount];
			itemDisabled[i] = false;
		}
	}

	const int xCenter = 320 / 2;
	const int yMenuHeader = 20;
	const int xMenuItem = 20;
	const int yMenuItems = 50;
	const int hMenuItem = 13;
	const int dyMenuItems = SDL_min(menuItemsCount > EPISODE_AVAILABLE ? 25 : 30, (195 - hMenuItem - yMenuItems) / (int)SDL_max(menuItemsCount - 1, 1));
	int wMenuItem[EPISODE_MAX + CUSTOM_EPISODE_MAX] = { 0 };

	for (; ; )
	{
		if (restart)
		{
			JE_loadPic(VGAScreen2, 2, false);

			// Draw header.
			draw_font_hv_shadow(VGAScreen2, xCenter, yMenuHeader, episode_name[0], large_font, centered, 15, -3, false, 2);
		}

		// Restore background and header.
		memcpy(VGAScreen->pixels, VGAScreen2->pixels, (size_t)VGAScreen->pitch * VGAScreen->h);

		// Draw menu items.
		for (size_t i = 0; i < menuItemsCount; ++i)
		{
			const char *const text = itemNames[i];

			wMenuItem[i] = JE_textWidth(text, normal_font);
			const int y = yMenuItems + dyMenuItems * i;

			const bool selected = i == selectedIndex;
			const bool disabled = itemDisabled[i];

			draw_font_hv_shadow(VGAScreen, xMenuItem, y, text, normal_font, left_aligned, 15, -4 + (selected ? 2 : 0) + (disabled ? -4 : 0), false, 2);
		}
		{
			int xs[EPISODE_MAX + CUSTOM_EPISODE_MAX];
			for (size_t i = 0; i < menuItemsCount; ++i)
				xs[i] = xMenuItem;
			publish_choices(UI_SCREEN_EPISODES, episode_name[0], itemNames, NULL, menuItemsCount, selectedIndex, wMenuItem, xs, yMenuItems,
			                dyMenuItems, hMenuItem, itemDisabled, 0);
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

			NETWORK_KEEP_ALIVE();

			mouseMoved = mouse_x != oldMouseX || mouse_y != oldMouseY;
		} while (!(newkey || newmouse || mouseMoved));

		// Handle interaction.

		bool action = false;
		bool cancel = false;

		if (mouseMoved || newmouse)
		{
			// Find menu item that was hovered or clicked.
			for (size_t i = 0; i < menuItemsCount; ++i)
			{
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

				cancel = true;
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
			case SDL_SCANCODE_RIGHT:
			{
				if (selectedIndex < firstExtra && firstExtra < menuItemsCount)
				{
					JE_playSampleNum(S_CURSOR);
					lastMain = selectedIndex;
					selectedIndex = firstExtra;
				}
				break;
			}
			case SDL_SCANCODE_LEFT:
			{
				if (selectedIndex >= firstExtra && firstExtra > 0)
				{
					JE_playSampleNum(S_CURSOR);
					selectedIndex = SDL_min(lastMain, firstExtra - 1);
				}
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

				cancel = true;
				break;
			}
			default:
				break;
			}
		}

		if (action)
		{
			if (!itemDisabled[selectedIndex])
			{
				JE_playSampleNum(S_SELECT);

				fade_black(10);

				if (selectedIndex >= episodeCount)
				{
					custom_episode_start((int)(selectedIndex - episodeCount) + 1);
				}
				else
				{
					custom_episode = 0;
					JE_initEpisode(episodeNumbers[selectedIndex]);
				}
				initial_episode_num = episodeNum;
				return true;
			}
			else
			{
				JE_playSampleNum(S_SPRING);
			}
		}

		if (cancel)
		{
			fade_black(15);

			return false;
		}
	}
}

bool difficultySelect(void)
{
	if (shopSpriteSheet.data == NULL)
		JE_loadCompShapes(&shopSpriteSheet, '1');  // need mouse pointer sprites

	bool restart = true;

	const size_t menuItemsCount = COUNTOF(difficulty_name) - 1;
	size_t menuItemsVisibleCount = menuItemsCount - 3;
	size_t selectedIndex = 1;
	size_t lordProgress = 0;

	const int xCenter = 320 / 2;
	const int yMenuHeader = 20;
	const int yMenuItems = 54;
	const int dyMenuItems = 24;
	const int hMenuItem = 13;
	int wMenuItem[COUNTOF(difficulty_name) - 1] = { 0 };

	for (; ; )
	{
		if (restart)
		{
			JE_loadPic(VGAScreen2, 2, false);

			// Draw header.
			draw_font_hv_shadow(VGAScreen2, xCenter, yMenuHeader, difficulty_name[0], large_font, centered, 15, -3, false, 2);
		}

		// Restore background and header.
		memcpy(VGAScreen->pixels, VGAScreen2->pixels, (size_t)VGAScreen->pitch * VGAScreen->h);

		// Draw menu items.
		for (size_t i = 0; i < menuItemsVisibleCount; ++i)
		{
			const char *const text = difficulty_name[i + 1];

			wMenuItem[i] = JE_textWidth(text, normal_font);
			const int y = yMenuItems + dyMenuItems * i;

			const bool selected = i == selectedIndex;

			// Tyrian3D: drawn centred (as it was at xCenter - wMenuItem[i] / 2), so the 3D view's text is.
			draw_font_hv_shadow(VGAScreen, xCenter, y, text, normal_font, centered, 15, -4 + (selected ? 2 : 0), false, 2);
		}
		{
			static const char *const hints[] = {
				"A gentler start, for learning the levels.",
				"The challenge as it was meant.",
				"For seasoned pilots.",
				"Only for the best.",
				"You asked for it.",
				"The hidden last word in difficulty.",
			};
			const char *texts[COUNTOF(difficulty_name)];
			int xs[COUNTOF(difficulty_name)];
			for (size_t i = 0; i < menuItemsVisibleCount; ++i)
			{
				texts[i] = difficulty_name[i + 1];
				xs[i] = xCenter - wMenuItem[i] / 2;
			}
			publish_choices(UI_SCREEN_DIFFICULTY, difficulty_name[0], texts, hints, menuItemsVisibleCount, selectedIndex, wMenuItem, xs,
			                yMenuItems, dyMenuItems, hMenuItem, NULL, 6);
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

			NETWORK_KEEP_ALIVE();

			mouseMoved = mouse_x != oldMouseX || mouse_y != oldMouseY;
		} while (!(newkey || newmouse || mouseMoved));

		// Handle interaction.

		if (menuItemsVisibleCount == 5)
		{
			const SDL_Scancode lordKeys[] = { SDL_SCANCODE_L, SDL_SCANCODE_O, SDL_SCANCODE_R, SDL_SCANCODE_D };

			for (size_t i = 0; ; ++i)
			{
				if (i == COUNTOF(lordKeys))
				{
					menuItemsVisibleCount = 6;
					break;
				}

				if (!keysactive[lordKeys[i]])
					break;
			}

			if (newkey)
			{
				// Due to key jamming, holding down 4 keys simultaneous may not be possible, so an
				// alternate input method is also provided.
				if (lordProgress < COUNTOF(lordKeys) &&
					lastkey_scan == lordKeys[lordProgress])
				{
					lordProgress += 1;

					if (lordProgress == COUNTOF(lordKeys))
						menuItemsVisibleCount = 6;
				}
				else
				{
					lordProgress = 0;
				}
			}
		}
		if (SDL_GetModState() & SDL_KMOD_SHIFT)
		{
			if (menuItemsVisibleCount == 4 && keysactive[SDL_SCANCODE_RIGHTBRACKET])
				menuItemsVisibleCount = 5;
			if (menuItemsVisibleCount == 3 && keysactive[SDL_SCANCODE_G])
				menuItemsVisibleCount = 4;
		}

		bool action = false;
		bool cancel = false;

		if (mouseMoved || newmouse)
		{
			// Find menu item that was hovered or clicked.
			for (size_t i = 0; i < menuItemsVisibleCount; ++i)
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

				cancel = true;
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
					? menuItemsVisibleCount - 1
					: selectedIndex - 1;
				break;
			}
			case SDL_SCANCODE_DOWN:
			{
				JE_playSampleNum(S_CURSOR);

				selectedIndex = selectedIndex == menuItemsVisibleCount - 1
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

				cancel = true;
				break;
			}
			default:
				break;
			}
		}

		if (action)
		{
			JE_playSampleNum(S_SELECT);

			switch (selectedIndex)
			{
			case 0:
				difficultyLevel = DIFFICULTY_EASY;
				break;
			case 1:
				difficultyLevel = DIFFICULTY_NORMAL;
				break;
			case 2:
				difficultyLevel = DIFFICULTY_HARD;
				break;
			case 3:
				difficultyLevel = DIFFICULTY_IMPOSSIBLE;
				break;
			case 4:
				difficultyLevel = DIFFICULTY_SUICIDE;
				break;
			case 5:
				difficultyLevel = DIFFICULTY_ZINGLON;
				break;
			}

			fade_black(10);

			return true;
		}

		if (cancel)
		{
			fade_black(15);

			return false;
		}
	}
}

bool timedBattleSelect(void)
{
	if (shopSpriteSheet.data == NULL)
		JE_loadCompShapes(&shopSpriteSheet, '1');  // need mouse pointer sprites

	bool restart = true;

	const size_t menuItemsCount = COUNTOF(timed_battle_name) - 1;
	size_t selectedIndex = 0;

	const int xCenter = 320 / 2;
	const int yMenuHeader = 20;
	const int yMenuItems = 54;
	const int dyMenuItems = 24;
	const int hMenuItem = 13;
	int wMenuItem[COUNTOF(timed_battle_name) - 1] = { 0 };

	for (; ; )
	{
		if (restart)
		{
			JE_loadPic(VGAScreen2, 2, false);

			// Draw header.
			draw_font_hv_shadow(VGAScreen2, xCenter, yMenuHeader, timed_battle_name[0], large_font, centered, 15, -3, false, 2);
		}

		// Restore background and header.
		memcpy(VGAScreen->pixels, VGAScreen2->pixels, (size_t)VGAScreen->pitch * VGAScreen->h);

		// Draw menu items.
		for (size_t i = 0; i < menuItemsCount; ++i)
		{
			const char *const text = timed_battle_name[i + 1];

			wMenuItem[i] = JE_textWidth(text, normal_font);
			const int y = yMenuItems + dyMenuItems * i;

			const bool selected = i == selectedIndex;

			// Tyrian3D: drawn centred (as it was at xCenter - wMenuItem[i] / 2), so the 3D view's text is.
			draw_font_hv_shadow(VGAScreen, xCenter, y, text, normal_font, centered, 15, -4 + (selected ? 2 : 0), false, 2);
		}
		{
			const char *texts[COUNTOF(timed_battle_name)];
			int xs[COUNTOF(timed_battle_name)];
			for (size_t i = 0; i < menuItemsCount; ++i)
			{
				texts[i] = timed_battle_name[i + 1];
				xs[i] = xCenter - wMenuItem[i] / 2;
			}
			publish_choices(UI_SCREEN_TIMED, timed_battle_name[0], texts, NULL, menuItemsCount, selectedIndex, wMenuItem, xs,
			                yMenuItems, dyMenuItems, hMenuItem, NULL, 0);
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

			NETWORK_KEEP_ALIVE();

			mouseMoved = mouse_x != oldMouseX || mouse_y != oldMouseY;
		} while (!(newkey || newmouse || mouseMoved));

		// Handle interaction.

		bool action = false;
		bool cancel = false;

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

				cancel = true;
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

				cancel = true;
				break;
			}
			default:
				break;
			}
		}

		if (action)
		{
			JE_playSampleNum(S_SELECT);

			fade_black(10);

			// I don't know how T2K determines episode from this,
			// I'm assuming it's hardcoded
			JE_initEpisode(selectedIndex == 0 ? 1 : 5);
			timeBattleSelection = selectedIndex + 1;
			return true;
		}

		if (cancel)
		{
			fade_black(15);

			return false;
		}
	}
}
