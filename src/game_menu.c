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
#include "game_menu.h"

#include "backgrnd.h"
#include "config.h"
#include "file.h"
#include "fonthand.h"
#include "joystick.h"
#include "keyboard.h"
#include "loudness.h"
#include "mainint.h"
#include "mouse.h"
#include "musmast.h"
#include "network.h"
#include "nortsong.h"
#include "nortvars.h"
#include "params.h"
#include "pcxmast.h"
#include "picload.h"
#include "player.h"
#include "shots.h"
#include "sprite.h"
#include "tyrian2.h"
#include "varz.h"
#include "vga256d.h"
#include "ui.h"
#include "video.h"
#include "voiceover.h"

#include <assert.h>

enum
{
	MENU_FULL_GAME       =  0,
	MENU_UPGRADES        =  1,
	MENU_OPTIONS         =  2,
	MENU_PLAY_NEXT_LEVEL =  3,
	MENU_UPGRADE_SUB     =  4,
	MENU_KEYBOARD_CONFIG =  5,
	MENU_LOAD_SAVE       =  6,
	MENU_DATA_CUBES      =  7,
	MENU_DATA_CUBE_SUB   =  8,
	MENU_2_PLAYER_ARCADE =  9,
	MENU_1_PLAYER_ARCADE = 10,  // Also networked games.
	MENU_LIMITED_OPTIONS = 11,  // Hides save/load menus.
	MENU_JOYSTICK_CONFIG = 12,
	MENU_SUPER_TYRIAN    = 13,
	MENU_MOUSE_CONFIG    = 14,  // T2000
};

/*** Structs ***/
struct cube_struct
{
	char title[81];
	char header[13];
	int face_sprite;
	char text[90][36];
	int last_line;
	Uint32 voice_hash;  // Tyrian3D: its text's, which its voice must match (voiceover.h)
};

/*** Globals ***/
static int joystick_config = 0; // which joystick is being configured in menu

static JE_word yLoc;
static JE_shortint yChg;
static int newPal, curPal, oldPal;
static JE_boolean quikSave;
static JE_byte oldMenu;
static JE_boolean backFromHelp;
static JE_integer lastDirection;
static JE_boolean firstMenu9, paletteChanged;
static JE_MenuChoiceType menuChoices;
static JE_integer col, colC;
static JE_byte lastCurSel;
static JE_integer curMenu;
static JE_byte curSel[MENU_MAX]; /* [1..maxmenu] */
static JE_byte curItemType, curItem, cursor;
static JE_boolean leftPower, rightPower, rightPowerAfford;
static JE_byte currentCube;
static JE_boolean keyboardUsed;
static JE_byte weaponSimTime;

static JE_byte planetAni, planetAniWait;
static JE_byte currentDotNum, currentDotWait;
static JE_real navX, navY, newNavX, newNavY;
static JE_integer tempNavX, tempNavY;
static JE_byte planetDots[5]; /* [1..5] */
static JE_integer planetDotX[5][10], planetDotY[5][10]; /* [1..5, 1..10] */
static PlayerItems old_items[2];  // TODO: should not be global if possible

static struct cube_struct cube[4];

static const JE_MenuChoiceType menuChoicesDefault = { 7, 9, 9, 0, 0, 11, (SAVE_FILES_NUM / 2) + 2, 0, 0, 6, 4, 6, 7, 5, 6 };
static const JE_byte menuEsc[MENU_MAX] = { 0, 1, 1, 1, 2, 3, 3, 1, 8, 0, 0, 11, 3, 0, 2 };
static const JE_byte itemAvailMap[7] = { 1, 2, 3, 9, 4, 6, 7 };
static const JE_word planetX[21] = { 200, 150, 240, 300, 270, 280, 320, 260, 220, 150, 160, 210, 80, 240, 220, 180, 310, 330, 150, 240, 200 };
static const JE_word planetY[21] = {  40,  90,  90,  80, 170,  30,  50, 130, 120, 150, 220, 200, 80,  50, 160,  10,  55,  55,  90,  90,  40 };
static const uint cube_line_chars = sizeof(*cube->text) - 1;
static const uint cube_line_width = 150;

/*** Functions ***/
static Uint8 *playeritem_map(PlayerItems *items, uint i)
{
	Uint8 *const map[] =
	{
		&items->ship,
		&items->weapon[FRONT_WEAPON].id,
		&items->weapon[REAR_WEAPON].id,
		&items->shield,
		&items->generator,
		&items->sidekick[LEFT_SIDEKICK],
		&items->sidekick[RIGHT_SIDEKICK],
	};
	assert(i < COUNTOF(map));
	return map[i];
}

JE_longint JE_cashLeft(void)
{
	JE_longint tempL = player[0].cash;
	JE_word itemNum = *playeritem_map(&player[0].items, curSel[MENU_UPGRADES] - 2);

	tempL -= JE_getCost(curSel[MENU_UPGRADES], itemNum);

	tempW = 0;

	switch (curSel[MENU_UPGRADES])
	{
	case 3:
	case 4:
		for (uint i = 1; i < player[0].items.weapon[curSel[MENU_UPGRADES]-3].power; ++i)
		{
			tempW += weaponPort[itemNum].cost * i;
			tempL -= tempW;
		}
		break;
	}

	return tempL;
}

/*
 * Tyrian3D: the store's screen as it shows, published for the modern UI (ui.h) before each time it
 * is shown: its menu's choices with where the original takes the mouse on them, the parts' choices
 * with their costs, icons and short stats, the weapon's power, the credits, the help line. The
 * original drawing goes on as ever (the classic UI and the 2D view show it).
 */
static void menu_header_text(char *out, size_t size);
static void main_menu_help_text(char *tempStr);
static void shop_ship_name(int ship, char *name, size_t name_size, char *class_name, size_t class_size);
static void shop_plain_text(char *out, const char *in, size_t size);

static bool shop_showing = false;      // JE_itemScreen runs (its questions are published over it)
static long shop_cash_before = -1;     // the credits as a part's choices were opened
static int shop_capturing = -1;        // the keyboard's setting waiting for a key (its choice), or -1

static const JE_byte shop_mouse_rows[MENU_MAX] = { 16, 16, 16, 16, 26, 12, 11, 28, 0, 16, 16, 16, 8, 16, 24 };

// Where the original's click takes each choice of the current menu (as its click handler reckons
// them, screen pixels), for choices 2 to last.
static void shop_hits(SDL_Rect *hits, int last)
{
	for (int s = 0; s <= last; ++s)
		hits[s] = (SDL_Rect){ 0, 0, 0, 0 };
	const int step = shop_mouse_rows[curMenu];
	if (step == 0)
		return;
	for (int y = 21; y < 38 + (last + 2) * step; ++y)
	{
		int selection = (y - 38) / step + 2;
		if (curMenu == MENU_2_PLAYER_ARCADE)
		{
			if (selection > 5)
				selection--;
			if (selection > 3)
				selection--;
		}
		if (curMenu == MENU_FULL_GAME && selection > 7)
			selection = 7;
		if (curMenu == MENU_PLAY_NEXT_LEVEL && selection == menuChoices[curMenu] + 1)
			selection = menuChoices[curMenu];
		if (selection < 2 || selection > last)
			continue;
		SDL_Rect *r = &hits[selection];
		if (r->h == 0)
			*r = (SDL_Rect){ 171, y, 137, 1 };
		else if (y < r->y + step)  // (one row's worth: a last choice takes all below it)
			r->h = y - r->y + 1;
	}
}

// An item's name and cost in a part (2 ship ... 8 right sidekick), as the store shows them.
static void shop_item_name(int part, int item, char *out, size_t size)
{
	switch (part)
	{
	case 2:
		if (item > 90)
			snprintf(out, size, "Custom Ship %d", item - 90);
		else
			SDL_strlcpy(out, ships[item].name, size);
		break;
	case 3:
	case 4:
		SDL_strlcpy(out, weaponPort[item].name, size);
		break;
	case 5:
		SDL_strlcpy(out, shields[item].name, size);
		break;
	case 6:
		SDL_strlcpy(out, powerSys[item].name, size);
		break;
	default:
		SDL_strlcpy(out, options[item].name, size);
		break;
	}
	for (int i = (int)strlen(out) - 1; i >= 0 && out[i] == ' '; --i)
		out[i] = '\0';
}

static long shop_item_cost(int part, int item)
{
	switch (part)
	{
	case 2: return item > 90 ? 100 : ships[item].cost;
	case 3:
	case 4: return weaponPort[item].cost;
	case 5: return shields[item].cost;
	case 6: return powerSys[item].cost;
	default: return options[item].cost;
	}
}

// A shot's damage as the game deals it (99 ices, 100-249 sets off another weapon's shots, 250 and
// more pierce), about.
static float shop_shot_damage(int attack, int depth)
{
	if (attack == 99)
		return 0;
	if (attack >= 250)
		return (attack - 250) * 2.0f;
	if (attack > 99)
	{
		const int chain = attack - 100;
		float sum = 1;
		if (depth == 0 && chain > 0 && chain <= WEAP_NUM)
			for (int i = 0; i < weapons[chain].multi && i < 8; ++i)
				sum += shop_shot_damage(weapons[chain].attack[i], depth + 1);
		return sum;
	}
	return (float)attack;
}

// A weapon's damage a second, about (its shots), for the cards' stats.
static float shop_weapon_damage(int w)
{
	if (w <= 0 || w > WEAP_NUM)
		return 0;
	float damage = 0;
	for (int i = 0; i < weapons[w].multi && i < 8; ++i)
		damage += shop_shot_damage(weapons[w].attack[i], 0);
	return damage * 35.0f / (weapons[w].shotrepeat + 1);
}

// A weapon port's at a power level.
static float shop_weapon_rate(int port, int power, int mode)
{
	if (port <= 0 || port > PORT_NUM || power < 1)
		return 0;
	return shop_weapon_damage(weaponPort[port].op[SDL_clamp(mode, 0, 1)][SDL_clamp(power, 1, 11) - 1]);
}

// The item's icon as JE_drawItem draws it.
static void shop_item_icon(UIItem *it, int part, int item)
{
	if (item <= 0)
		return;
	if (part == 2)
	{
		if (item > 90)
			return;
		it->icon_sheet = ships[item].shipgraphic > 500 ? &spriteSheetT2000 : &spriteSheet9;
		it->icon_sprite = ships[item].shipgraphic > 500 ? ships[item].shipgraphic - 500 : ships[item].shipgraphic;
		it->icon_large = true;
		return;
	}
	const int graphic = part == 3 || part == 4 ? weaponPort[item].itemgraphic : part == 5 ? shields[item].itemgraphic
	                  : part == 6 ? powerSys[item].itemgraphic : options[item].itemgraphic;
	if (graphic > 0)
	{
		it->icon_sheet = &shopSpriteSheet;
		it->icon_sprite = graphic;
		it->icon_large = true;
	}
}

// A part's choices as cards (ITEMS: the choices being picked from; else a preview), stats relative to
// the best of them.
static void shop_part_items(UIMenu *ui, int part, bool choosing)
{
	const int list = itemAvailMap[part - 2] - 1;
	const int count = itemAvailMax[list];
	const int owned = *playeritem_map(&old_items[0], part - 2), chosen = *playeritem_map(&player[0].items, part - 2);
	const int have = choosing ? owned : chosen;
	float best[2] = { 0, 0 };
	float stats[UI_MENU_ITEMS][2];
	int stat_count = 0;
	const char *labels[2] = { "", "" };
	for (int i = 0; i < count && i < UI_MENU_ITEMS - 1; ++i)
	{
		const int item = itemAvail[list][i];
		stats[i][0] = stats[i][1] = 0;
		switch (part)
		{
		case 2:
			stat_count = 2, labels[0] = "ARMOR", labels[1] = "SPEED";
			if (item > 0 && item <= 90)
				stats[i][0] = ships[item].dmg, stats[i][1] = ships[item].spd;
			break;
		case 3:
		case 4:
		{
			// (All at the power the ship's weapon has now.)
			stat_count = 1, labels[0] = "FIREPOWER";
			stats[i][0] = shop_weapon_rate(item, player[0].items.weapon[part - 3].power, 0);

			break;
		}
		case 5:
			stat_count = 2, labels[0] = "STRENGTH", labels[1] = "RECHARGE";
			stats[i][0] = shields[item].mpwr, stats[i][1] = shields[item].tpwr;
			break;
		case 6:
			stat_count = 1, labels[0] = "OUTPUT";
			stats[i][0] = powerSys[item].power;
			break;
		default:
			stat_count = 1, labels[0] = "FIREPOWER";
			if (item > 0 && options[item].wport > 0)
				stats[i][0] = shop_weapon_damage(options[item].wpnum);
			break;
		}
		for (int k = 0; k < 2; ++k)
			best[k] = SDL_max(best[k], stats[i][k]);
	}
	for (int i = 0; i < count && i < UI_MENU_ITEMS - 1; ++i)
	{
		const int item = itemAvail[list][i];
		char name[48];
		shop_item_name(part, item, name, sizeof(name));
		// (On the choosing page each where the original takes the mouse on it.)
		UIItem *it = ui_menu_add(ui, UI_ITEM_ACTION, name, 171, 38 + i * 26, 137, 26);
		if (!choosing)
			it->hit = (SDL_Rect){ 0, 0, 0, 0 };
		const long cost = shop_item_cost(part, item);
		shop_item_icon(it, part, item);
		it->owned = item == have && item != 0;
		it->chosen = item == chosen && item != 0;
		it->unaffordable = choosing && cost > (long)player[0].cash && !it->owned;
		if (!it->owned)
		{
			char value[24];
			snprintf(value, sizeof(value), "%ld", cost);
			SDL_strlcpy(it->value, value, sizeof(it->value));
		}
		if (item != 0)
		{
			it->stat_count = stat_count;
			for (int k = 0; k < stat_count; ++k)
			{
				it->stat[k] = best[k] > 0 ? SDL_clamp(stats[i][k] / best[k], 0.0f, 1.0f) : 0;
				SDL_strlcpy(it->stat_label[k], labels[k], sizeof(it->stat_label[k]));
			}
		}
	}
}

// The store's categories as tabs (their names' first words), the selected one.
static void shop_tabs(UIShop *s, int selected, bool live)
{
	SDL_Rect hits[16];
	if (live)
		shop_hits(hits, menuChoices[MENU_UPGRADES]);
	s->tab_count = 0;
	// (The parts the parts' list has, Done aside: of the seven the ship's items know. A part added later, as
	// episode 6's specials, needs its items here and in playeritem_map, then its tab comes with them.)
	const int parts_end = SDL_min((int)menuChoices[MENU_UPGRADES] - 1, 8);
	for (int part = 2; part <= parts_end && s->tab_count < UI_SHOP_TABS; ++part)
	{
		char word[24];
		SDL_strlcpy(word, menuInt[2][part - 1], sizeof(word));
		char *space = strchr(word, ' ');
		if (space != NULL)
			*space = '\0';
		SDL_strlcpy(s->tab[s->tab_count], word, sizeof(s->tab[0]));
		s->tab_hit[s->tab_count] = live ? hits[part] : (SDL_Rect){ 0, 0, 0, 0 };
		++s->tab_count;
	}
	s->tab_selected = selected;
}

static void shop_publish(void)
{
	if (!ui_modern())
		return;
	const JE_word saved_tempW = tempW;  // (JE_cashLeft reckons in the game's scratch variable)
	char title[48];
	menu_header_text(title, sizeof(title));
	UIMenu *ui = ui_menu_begin(UI_SCREEN_SHOP, title);
	UIShop *s = &ui->shop;
	SDL_strlcpy(ui->crumb, "SHOP", sizeof(ui->crumb));
	s->credits = s->credits_after = -1;
	s->generator = -1;
	ui->nowhere = (SDL_Point){ 100, 196 };
	char help[67];
	main_menu_help_text(help);
	SDL_strlcpy(ui->hint, help, sizeof(ui->hint));

	// The ship and its gauges, where the original shows them.
	const bool illustrated = (curMenu >= MENU_FULL_GAME && curMenu <= MENU_OPTIONS) || curMenu == MENU_KEYBOARD_CONFIG ||
	                         curMenu == MENU_LOAD_SAVE || curMenu >= MENU_2_PLAYER_ARCADE;
	// (Two players, Super Arcade, Super Tyrian: the original shows texts there; the first ship shows.)
	if (illustrated)
		s->scene = UI_SCENE_SHIP;
	// What the ship's scene shows: the ship, its sidekicks beside it (screen pixels, as the illustration);
	// two players' ships side by side.
	s->scene_w = twoPlayerMode ? 150.0f : player[0].items.sidekick[LEFT_SIDEKICK] > 0 || player[0].items.sidekick[RIGHT_SIDEKICK] > 0 ? 160.0f : 116.0f;
	shop_ship_name(player[0].items.ship, s->ship, sizeof(s->ship), s->ship_class, sizeof(s->ship_class));
	if (((curMenu <= MENU_OPTIONS || curMenu == MENU_KEYBOARD_CONFIG || curMenu == MENU_LOAD_SAVE || curMenu >= MENU_1_PLAYER_ARCADE) &&
	     !twoPlayerMode) || curMenu == MENU_UPGRADE_SUB)
	{
		s->credits = (long)player[0].cash;
		s->gauges = true;
		s->armor = SDL_clamp(player[0].armor / 28.0f, 0.0f, 1.0f);
		s->shield = SDL_clamp(shields[player[0].items.shield].mpwr / 14.0f, 0.0f, 1.0f);
	}
	if (twoPlayerMode)
	{
		char one[24], two[24];
		shop_plain_text(one, miscText[40], sizeof(one));
		shop_plain_text(two, miscText[41], sizeof(two));
		snprintf(s->caption, sizeof(s->caption), "%s %lu    %s %lu", one, player[0].cash, two, player[1].cash);
		// What each player has (their ships side by side over it): the ship, the score, the gun the player
		// fires (player 1 the front, player 2 the rear, as the game's panel) and its power, lives, bombs, input.
		s->player_count = 2;
		for (int k = 0; k < 2; ++k)
		{
			const Player *p = &player[k];
			shop_plain_text(s->players[k].name, miscText[48 + k], sizeof(s->players[k].name));
			if (k == 0)
				shop_ship_name(p->items.ship, s->players[k].ship, sizeof(s->players[k].ship), s->ship_class, 0);
			else
				SDL_strlcpy(s->players[k].ship, "Dragonwing", sizeof(s->players[k].ship));
			snprintf(s->players[k].score, sizeof(s->players[k].score), "%lu", p->cash);
			const int w = k == 0 ? FRONT_WEAPON : REAR_WEAPON;
			char weapon[48] = "-";
			if (p->items.weapon[w].id > 0)
				shop_item_name(w == FRONT_WEAPON ? 3 : 4, p->items.weapon[w].id, weapon, sizeof(weapon));
			SDL_strlcpy(s->players[k].weapon, weapon, sizeof(s->players[k].weapon));
			s->players[k].power = p->items.weapon[w].id > 0 ? p->items.weapon[w].power : 0;
			s->players[k].power_max = s->players[k].power > 11 ? 15 : 11;
			s->players[k].lives = p->lives != NULL ? (int)*p->lives - 1 : -1;
			s->players[k].bombs = (int)p->superbombs;
			if (joysticks > 1 && inputDevice[k] > 2)
				snprintf(s->players[k].input, sizeof(s->players[k].input), "%s %d", inputDevices[2], inputDevice[k] - 2);
			else if (inputDevice[k] >= 1 && inputDevice[k] <= 3)
				SDL_strlcpy(s->players[k].input, inputDevices[inputDevice[k] - 1], sizeof(s->players[k].input));
		}
		s->ship_class[0] = '\0';
	}
	// The Super Arcade's and Super Tyrian's ship info, as the original's help boxes show it there: the
	// ship's name, its main and special weapons.
	if (illustrated && !twoPlayerMode && (superArcadeMode != SA_NONE || superTyrian))
	{
		SDL_strlcpy(s->super_title, superTyrian ? "Super Tyrian" : superShips[0], sizeof(s->super_title));
		shop_plain_text(s->ship, superShips[superTyrian ? SA + 3 : superArcadeMode], sizeof(s->ship));
		s->ship_class[0] = '\0';
		shop_plain_text(s->super[0][0], superShips[SA + 1], sizeof(s->super[0][0]));
		shop_plain_text(s->super[0][1], weaponPort[player[0].items.weapon[FRONT_WEAPON].id].name, sizeof(s->super[0][1]));
		shop_plain_text(s->super[1][0], superShips[SA + 2], sizeof(s->super[1][0]));
		shop_plain_text(s->super[1][1], special[player[0].items.special].name, sizeof(s->super[1][1]));
		s->super_special = player[0].items.special;
		s->power = player[0].items.weapon[FRONT_WEAPON].power;
	}

	SDL_Rect hits[UI_MENU_ITEMS + 2];
	const int last = SDL_min((int)menuChoices[curMenu], UI_MENU_ITEMS + 1);
	shop_hits(hits, last);
	ui->selected = curSel[curMenu] - 2;

	switch (curMenu)
	{
	case MENU_UPGRADES:
	{
		s->page = UI_SHOP_UPGRADE;
		const int part = curSel[MENU_UPGRADES];
		shop_tabs(s, part <= 8 ? part - 2 : -1, true);
		SDL_strlcpy(s->done, menuInt[2][8], sizeof(s->done));
		s->hit_done = hits[9];
		if (part >= 2 && part <= 8)
			shop_part_items(ui, part, false);
		ui->selected = -1;
		break;
	}
	case MENU_UPGRADE_SUB:
	{
		s->page = UI_SHOP_ITEMS;
		const int part = curSel[MENU_UPGRADES];
		// (The weapon's costs as the store last reckoned them, before the cards' own costs are looked up.)
		const long down = downgradeCost, up = upgradeCost;
		shop_tabs(s, part - 2, false);
		shop_part_items(ui, part, true);
		ui_menu_add(ui, UI_ITEM_ACTION, miscText[13], 171, 38 + (menuChoices[MENU_UPGRADE_SUB] - 2) * 26, 137, 26);
		s->scene = part == 2 || part == 5 ? UI_SCENE_SHIP : UI_SCENE_SIM;
		s->credits = shop_cash_before >= 0 ? shop_cash_before : (long)player[0].cash;
		s->credits_after = JE_cashLeft();
		downgradeCost = (JE_word)down;
		upgradeCost = (JE_word)up;
		if (s->scene == UI_SCENE_SIM)
			s->generator = SDL_clamp(power / 900.0f, 0.0f, 1.0f);
		if ((part == 3 || part == 4) && (leftPower || rightPower))
		{
			s->power_on = true;
			s->power = player[0].items.weapon[part - 3].power;
			s->power_max = 11;
			s->power_down = leftPower;
			s->power_up = rightPower;
			s->power_afford = rightPowerAfford;
			s->cost_down = downgradeCost;
			s->cost_up = upgradeCost;
			s->hit_down = (SDL_Rect){ 23, 149, 14, 20 };
			s->hit_up = (SDL_Rect){ 119, 149, 13, 20 };
		}
		if (part == 4 && weaponPort[player[0].items.weapon[REAR_WEAPON].id].opnum == 2)
			snprintf(s->mode, sizeof(s->mode), "Firing mode %d of 2   [ / ]", player[0].weapon_mode);
		break;
	}
	case MENU_LOAD_SAVE:
	{
		s->page = UI_SHOP_FILES;
		const int min = twoPlayerMode ? 13 : 2, max = twoPlayerMode ? 24 : 13;
		for (int x = min; x <= max; ++x)
		{
			const int i = x - min + 2;
			char name[48], level[24] = "", episode[24] = "";
			if (x == max)
				SDL_strlcpy(name, miscText[6 - 1], sizeof(name));
			else if (saveFiles[x - 2].level == 0)
				SDL_strlcpy(name, miscText[3 - 1], sizeof(name));
			else
			{
				shop_plain_text(name, saveFiles[x - 2].name, sizeof(name));
				SDL_strlcpy(level, saveFiles[x - 2].levelName, sizeof(level));
				snprintf(episode, sizeof(episode), "%s%d", miscTextB[1 - 1], saveFiles[x - 2].episode);
			}
			UIItem *it = ui_menu_add(ui, UI_ITEM_ACTION, name, 0, 0, 0, 0);
			it->hit = i <= last ? hits[i] : (SDL_Rect){ 0, 0, 0, 0 };
			it->disabled = x < max && saveFiles[x - 2].level == 0 && !performSave;
			SDL_strlcpy(it->value, level, sizeof(it->value));
			SDL_strlcpy(it->value2, episode, sizeof(it->value2));
		}
		break;
	}
	case MENU_PLAY_NEXT_LEVEL:
	{
		s->page = UI_SHOP_MAP;
		s->scene = UI_SCENE_NONE;
		s->picture_part = (SDL_Rect){ 19, 16, 117, 154 };
		for (int x = 2; x <= menuChoices[curMenu]; ++x)
		{
			UIItem *it = ui_menu_add(ui, UI_ITEM_ACTION, menuInt[4][x - 1], 0, 0, 0, 0);
			it->hit = x <= last ? hits[x] : (SDL_Rect){ 0, 0, 0, 0 };
		}
		if (curSel[curMenu] < menuChoices[curMenu])
			SDL_strlcpy(s->caption, menuInt[4][curSel[curMenu] - 1], sizeof(s->caption));
		if (extraGame)
			SDL_strlcpy(s->note, miscText[68 - 1], sizeof(s->note));
		break;
	}
	case MENU_DATA_CUBES:
	case MENU_DATA_CUBE_SUB:
	{
		s->page = curMenu == MENU_DATA_CUBES ? UI_SHOP_CUBES : UI_SHOP_CUBE;
		s->scene = UI_SCENE_NONE;
		const int selected = curSel[MENU_DATA_CUBES] - 2;
		s->picture_part = (SDL_Rect){ 1, 1, 145, 170 };  // (the portrait's box, with the face if it has one)
		if (selected < cubeMax)
			SDL_strlcpy(s->caption, cube[selected].header, sizeof(s->caption));
		if (curMenu == MENU_DATA_CUBES)
		{
			if (cubeMax == 0)
				SDL_strlcpy(s->note, miscText[16 - 1], sizeof(s->note));
			for (int x = 1; x <= cubeMax + 1; ++x)
			{
				UIItem *it = ui_menu_add(ui, UI_ITEM_ACTION, x <= cubeMax ? cube[x - 1].title : miscText[6 - 1], 0, 0, 0, 0);
				it->hit = x + 1 <= last ? hits[x + 1] : (SDL_Rect){ 0, 0, 0, 0 };
				if (x <= cubeMax)
				{
					it->icon_table = OPTION_SHAPES;
					it->icon_sprite = 25;
				}
			}
		}
		else
		{
			SDL_strlcpy(ui->title, cube[currentCube].header, sizeof(ui->title));
			SDL_strlcpy(ui->crumb, cube[currentCube].title, sizeof(ui->crumb));
			s->line_count = SDL_min(cube[currentCube].last_line, UI_CUBE_LINES);
			for (int i = 0; i < s->line_count; ++i)
				SDL_strlcpy(s->lines[i], cube[currentCube].text[i], sizeof(s->lines[i]));
			s->line_first = yLoc / 12.0f;
			s->percent = cube[currentCube].last_line <= 9 ? 100 : (yLoc * 100) / ((cube[currentCube].last_line - 9) * 12);
			SDL_strlcpy(s->done, miscText[12], sizeof(s->done));
			s->hit_done = (SDL_Rect){ 259, 160, 31, 11 };
			ui->selected = -1;
			ui->hint[0] = '\0';
		}
		break;
	}
	case MENU_JOYSTICK_CONFIG:
	{
		s->page = UI_SHOP_MENU;
		const char *const names[] = { "JOYSTICK", "ANALOG AXES", " SENSITIVITY", " THRESHOLD", menuInt[6][1], menuInt[6][4], menuInt[6][2],
		                              menuInt[6][3], menuInt[6][5], menuInt[6][6], menuInt[6][7], menuInt[6][8], "MENU", "PAUSE",
		                              menuInt[6][9], menuInt[6][10] };
		for (int i = 0; i < (int)COUNTOF(names); ++i)
		{
			char value[30] = "";
			if (joysticks == 0 && i < 14)
				strcpy(value, "-");
			else if (i == 0)
				snprintf(value, sizeof(value), "%d", joystick_config + 1);
			else if (i == 1)
				snprintf(value, sizeof(value), "%s", joystick[joystick_config].analog ? "TRUE" : "FALSE");
			else if (i < 4)
				snprintf(value, sizeof(value), "%d", i == 2 ? joystick[joystick_config].sensitivity : joystick[joystick_config].threshold);
			else if (i < 14)
				joystick_assignments_to_string(value, sizeof(value), joystick[joystick_config].assignment[i - 4]);
			UIItem *it = ui_menu_add(ui, UI_ITEM_CHOICE, names[i][0] == ' ' ? names[i] + 1 : names[i], 0, 0, 0, 0);
			it->hit = i + 2 <= last ? hits[i + 2] : (SDL_Rect){ 0, 0, 0, 0 };
			SDL_strlcpy(it->value, value, sizeof(it->value));
			it->disabled = (joysticks == 0 && i < 14) || ((i == 2 || i == 3) && joysticks > 0 && !joystick[joystick_config].analog);
			if (i >= 14)
				it->kind = UI_ITEM_ACTION;
		}
		break;
	}
	case MENU_KEYBOARD_CONFIG:
	{
		s->page = UI_SHOP_MENU;
		for (int x = 2; x <= 11; ++x)
		{
			UIItem *it = ui_menu_add(ui, x < 10 ? UI_ITEM_CHOICE : UI_ITEM_ACTION, menuInt[curMenu + 1][x - 1], 0, 0, 0, 0);
			it->hit = x <= last ? hits[x] : (SDL_Rect){ 0, 0, 0, 0 };
			if (x < 10)
				SDL_strlcpy(it->value, SDL_GetScancodeName(keySettings[x - 2]), sizeof(it->value));
			it->capturing = x == shop_capturing;
			it->gap_before = x == 10;
		}
		break;
	}
	default:
	{
		// The game menu, the arcade's, the options, the mouse.
		s->page = UI_SHOP_MENU;
		for (int x = 2; x <= menuChoices[curMenu] && x - 2 < UI_MENU_ITEMS; ++x)
		{
			UIItem *it = ui_menu_add(ui, UI_ITEM_ACTION, menuInt[curMenu + 1][x - 1], 0, 0, 0, 0);
			it->hit = x <= last ? hits[x] : (SDL_Rect){ 0, 0, 0, 0 };
			if (curMenu == MENU_FULL_GAME && x == 2)
				it->cubes = cubeMax;
			if (curMenu == MENU_FULL_GAME && x == 7)
				it->gap_before = true;
			if ((curMenu == MENU_OPTIONS || curMenu == MENU_LIMITED_OPTIONS) && (x == 4 || x == 5))
			{
				const bool music = x == 4;
				it->kind = UI_ITEM_BAR;
				it->bar = (music ? tyrMusicVolume : fxVolume) / 255.0f;
				it->muted = music ? music_disabled : samples_disabled;
				it->hit = (SDL_Rect){ 171, music ? 70 : 86, 50, 16 };
				it->hit_value = (SDL_Rect){ 221, music ? 70 : 86, 86, 13 };
			}
			if (curMenu == MENU_MOUSE_CONFIG && x <= 4)
			{
				it->kind = UI_ITEM_CHOICE;
				SDL_strlcpy(it->value, joyButtonNames[mouseSettings[x - 2] - 1], sizeof(it->value));
			}
			if (curMenu == MENU_MOUSE_CONFIG && x == 5)
				it->gap_before = true;
			if (curMenu == MENU_2_PLAYER_ARCADE && (x == 3 || x == 4))
			{
				const int i = x - 3;
				it->kind = UI_ITEM_CHOICE;
				if (joysticks > 1 && inputDevice[i] > 2)
					snprintf(it->value, sizeof(it->value), "%s %d", inputDevices[2], inputDevice[i] - 2);
				else
					SDL_strlcpy(it->value, inputDevices[inputDevice[i] - 1], sizeof(it->value));
			}
			if (curMenu == MENU_2_PLAYER_ARCADE && (x == 4 || x == 5))
				it->gap_before = true;
		}
		break;
	}
	}
	ui_menu_publish(ui, VGAScreen, VGAScreen);
	tempW = saved_tempW;
}

// A ship's name as the store shows it: its name and its class (they're apart by spaces: "USP Talon
// Light Fighter").
static void shop_ship_name(int ship, char *name, size_t name_size, char *class_name, size_t class_size)
{
	name[0] = class_name[0] = '\0';
	if (ship < 0 || ship >= (int)COUNTOF(ships))
		return;
	char full[48];
	SDL_strlcpy(full, ships[ship].name, sizeof(full));
	for (int i = (int)strlen(full) - 1; i >= 0 && full[i] == ' '; --i)
		full[i] = '\0';
	const char *gap = strstr(full, "  ");
	if (gap == NULL)
	{
		SDL_strlcpy(name, full, name_size);
		return;
	}
	SDL_strlcpy(name, full, SDL_min((size_t)(gap - full) + 1, name_size));
	while (*gap == ' ')
		++gap;
	SDL_strlcpy(class_name, gap, class_size);
}

// A text of the game without its highlight marks ('~').
static void shop_plain_text(char *out, const char *in, size_t size)
{
	size_t n = 0;
	for (; *in != '\0' && n + 1 < size; ++in)
		if (*in != '~')
			out[n++] = *in;
	out[n] = '\0';
	while (n > 0 && out[n - 1] == ' ')
		out[--n] = '\0';
}

// Ship specs: the ship's texts, its numbers and what it carries, round the ship (shown while the
// original's picture zooms in and is looked at: released after).
static void shop_specs_publish(void)
{
	if (!ui_modern())
		return;
	UIMenu *ui = ui_menu_begin(UI_SCREEN_SHOP, "Ship Specs");
	UIShop *s = &ui->shop;
	s->page = UI_SHOP_SPECS;
	s->scene = UI_SCENE_SHIP;
	s->scene_w = player[0].items.sidekick[LEFT_SIDEKICK] > 0 || player[0].items.sidekick[RIGHT_SIDEKICK] > 0 ? 160.0f : 116.0f;
	s->credits = s->credits_after = -1;
	s->generator = -1;
	ui->hold = true;
	ui->selected = -1;
	const int ship = player[0].items.ship;
	shop_ship_name(ship, s->ship, sizeof(s->ship), s->ship_class, sizeof(s->ship_class));
	for (int k = 0; k < 2; ++k)
		if (ship >= 1 && ship - 1 < HELPTEXT_SHIPINFO_COUNT)
			shop_plain_text(s->specs[k], shipInfo[ship - 1][k], sizeof(s->specs[k]));
	// The ship's armor and speed (an offset of the ships' own) among the ships'.
	float best_armor = 1, slowest = 0, fastest = 0;
	for (int i = 1; i < (int)COUNTOF(ships); ++i)
	{
		best_armor = SDL_max(best_armor, ships[i].dmg);
		slowest = SDL_min(slowest, ships[i].spd);
		fastest = SDL_max(fastest, ships[i].spd);
	}
	UIItem *armor = ui_menu_add(ui, UI_ITEM_BAR, "ARMOR", 0, 0, 0, 0);
	armor->bar = ship < (int)COUNTOF(ships) ? ships[ship].dmg / best_armor : 0;
	UIItem *speed = ui_menu_add(ui, UI_ITEM_BAR, "SPEED", 0, 0, 0, 0);
	speed->bar = ship < (int)COUNTOF(ships) && fastest > slowest ? (ships[ship].spd - slowest + 1) / (fastest - slowest + 1) : 0.5f;
	static const char *const labels[] = { "FRONT", "REAR", "SHIELD", "GENERATOR", "LEFT", "RIGHT" };
	for (int k = 0; k < 6; ++k)
	{
		UIItem *it = ui_menu_add(ui, UI_ITEM_ACTION, labels[k], 0, 0, 0, 0);
		const int part = k + 3, item = *playeritem_map(&player[0].items, part - 2);
		char name[48];
		if (item == 0)
			SDL_strlcpy(name, "-", sizeof(name));
		else
			shop_item_name(part, item, name, sizeof(name));
		SDL_strlcpy(it->value, name, sizeof(it->value));
		if (k < 2 && item != 0)
		{
			it->pips = player[0].items.weapon[k].power > 11 ? 15 : 11;
			it->pips_on = player[0].items.weapon[k].power;
		}
	}
	ui_menu_publish(ui, VGAScreen, VGAScreen);
}

// A question over the store (its quit and save), as it shows now.
void shop_dialog_publish(const char *title, const char *text, const char *field_label, const char *field, bool caret,
                                int selected)
{
	// (In the store; and over the rogue run's map, its quit request.)
	if ((!shop_showing && !ui_published_is(UI_SCREEN_ROGUE)) || !ui_modern())
		return;
	UIDialog *d = ui_dialog_begin();
	shop_plain_text(d->title, title, sizeof(d->title));
	shop_plain_text(d->text, text != NULL ? text : "", sizeof(d->text));
	if (field != NULL)
	{
		d->field_on = true;
		shop_plain_text(d->field_label, field_label, sizeof(d->field_label));
		SDL_strlcpy(d->field, field, sizeof(d->field));
		d->caret = caret;
	}
	shop_plain_text(d->yes, miscText[9], sizeof(d->yes));
	shop_plain_text(d->no, miscText[10], sizeof(d->no));
	d->selected = selected;
	d->hit_yes = (SDL_Rect){ 57, 124, 85, 25 };
	d->hit_no = (SDL_Rect){ 152, 124, 85, 25 };
	ui_dialog_publish(VGAScreen);
}

void JE_itemScreen(void)
{
	bool quit = false;
	shop_showing = true;

	if (shopSpriteSheet.data == NULL)
		JE_loadCompShapes(&shopSpriteSheet, '1');

	load_cubes();

	VGAScreen = VGAScreenSeg;

	memcpy(menuChoices, menuChoicesDefault, sizeof(menuChoices));

	play_song(songBuy);

	JE_loadPic(VGAScreen, 1, false);

	curPal = 1;
	newPal = 0;

	JE_showVGA();

	set_palette(colors, 0, 255);

	col = 1;
	gameLoaded = false;
	curItemType = 1;
	cursor = 1;
	curItem = 0;

	for (unsigned int i = 0; i < COUNTOF(curSel); ++i)
		curSel[i] = 2;

	curMenu = MENU_FULL_GAME;

	int temp_weapon_power[7]; // assumes there'll never be more than 6 weapons to choose from, 7th is "Done"

	/* JE: (* Check for where Pitems and Select match up - if no match then add to the itemavail list *) */
	for (int i = 0; i < 7; i++)
	{
		int item = *playeritem_map(&player[0].last_items, i);

		int slot = 0;

		for (; slot < itemAvailMax[itemAvailMap[i]-1]; ++slot)
		{
			if (itemAvail[itemAvailMap[i]-1][slot] == item)
				break;
		}

		if (slot == itemAvailMax[itemAvailMap[i]-1])
		{
			itemAvail[itemAvailMap[i]-1][slot] = item;
			itemAvailMax[itemAvailMap[i]-1]++;
		}
	}

	memcpy(VGAScreen2->pixels, VGAScreen->pixels, VGAScreen2->pitch * VGAScreen2->h);

	keyboardUsed = false;
	firstMenu9 = false;
	backFromHelp = false;

	/* JE: Sort items in merchant inventory */
	for (int x = 0; x < 9; x++)
	{
		if (itemAvailMax[x] > 1)
		{
			for (temp = 0; temp < itemAvailMax[x] - 1; temp++)
			{
				for (temp2 = temp; temp2 < itemAvailMax[x]; temp2++)
				{
					if (itemAvail[x][temp] == 0 || (itemAvail[x][temp] > itemAvail[x][temp2] && itemAvail[x][temp2] != 0))
					{
						temp3 = itemAvail[x][temp];
						itemAvail[x][temp] = itemAvail[x][temp2];
						itemAvail[x][temp2] = temp3;
					}
				}
			}
		}
	}

	do
	{
		quit = false;

		JE_getShipInfo();

		if (curMenu == MENU_FULL_GAME)
		{
			if (twoPlayerMode)
				curMenu = MENU_2_PLAYER_ARCADE;

			if (isNetworkGame || onePlayerAction)
				curMenu = MENU_1_PLAYER_ARCADE;

			if (superTyrian)
				curMenu = MENU_SUPER_TYRIAN;
		}

		paletteChanged = false;

		leftPower = false;
		rightPower = false;

		/* SYN: note reindexing... "firstMenu9" refers to Menu 8 here :( */
		if (curMenu != MENU_DATA_CUBE_SUB || firstMenu9)
		{
			memcpy(VGAScreen->pixels, VGAScreen2->pixels, VGAScreen->pitch * VGAScreen->h);
		}

		if (curMenu == MENU_UPGRADES &&
		    (curSel[curMenu] == 3 || curSel[curMenu] == 4))
		{
			// reset temp_weapon_power[] every time we select upgrading front or back
			const uint item       = player[0].items.weapon[curSel[MENU_UPGRADES] - 3].id,
			           item_power = player[0].items.weapon[curSel[MENU_UPGRADES] - 3].power,
			           i = curSel[MENU_UPGRADES] - 2;  // 1 or 2 (front or rear)

			// set power level of owned weapon
			for (int slot = 0; slot < itemAvailMax[itemAvailMap[i]-1]; ++slot)
			{
				if (itemAvail[itemAvailMap[i]-1][slot] == item)
					temp_weapon_power[slot] = item_power;
				else
					temp_weapon_power[slot] = 1;
			}

			// set power level for "Done"
			temp_weapon_power[itemAvailMax[itemAvailMap[i]-1]] = item_power;
		}

		if (curMenu == MENU_PLAY_NEXT_LEVEL)
		{
			planetAni = 0;
			keyboardUsed = false;
			currentDotNum = 0;
			currentDotWait = 8;
			planetAniWait = 3;
			JE_updateNavScreen();
		}

		/* Draw menu title for everything but upgrade ship submenus */
		if (curMenu != MENU_UPGRADE_SUB)
		{
			JE_drawMenuHeader();
		}

		/* Draw menu choices for simple menus */
		if ((curMenu >= MENU_FULL_GAME && curMenu <= MENU_PLAY_NEXT_LEVEL) ||
		    (curMenu >= MENU_2_PLAYER_ARCADE && curMenu <= MENU_LIMITED_OPTIONS) ||
		    curMenu >= MENU_SUPER_TYRIAN)
		{
			JE_drawMenuChoices();
		}

		if (curMenu == MENU_MOUSE_CONFIG)
		{
			for (int i = 0; i < 3; ++i)
			{
				int tempY = 51 + i * 24;
				JE_textShade(VGAScreen, 215, tempY, joyButtonNames[mouseSettings[i] - 1], 15, 2, PART_SHADE);
			}
		}

		/* Data cube icons */
		if (curMenu == MENU_FULL_GAME)
		{
			for (int i = 1; i <= cubeMax; i++)
			{
				blit_sprite_dark(VGAScreen, 190 + i * 18 + 2, 37 + 1, OPTION_SHAPES, 34, false);
				blit_sprite(VGAScreen, 190 + i * 18, 37, OPTION_SHAPES, 34);  // data cube
			}
		}

		/* load/save menu */
		if (curMenu == MENU_LOAD_SAVE)
		{
			int min, max;

			if (twoPlayerMode)
			{
				min = 13;
				max = 24;
			}
			else
			{
				min = 2;
				max = 13;
			}

			for (int x = min; x <= max; x++)
			{
				/* Highlight if current selection */
				temp2 = (x - min + 2 == curSel[curMenu]) ? 15 : 28;

				/* Write save game slot */
				if (x == max)
					strcpy(tempStr, miscText[6-1]);
				else if (saveFiles[x-2].level == 0)
					strcpy(tempStr, miscText[3-1]);
				else
					strcpy(tempStr, saveFiles[x-2].name);

				int tempY = 38 + (x - min)*11;

				JE_textShade(VGAScreen, 163, tempY, tempStr, temp2 / 16, temp2 % 16 - 8, DARKEN);

				if (x < max) /* x == max isn't a save slot */
				{
					/* Highlight if current selection */
					temp2 = (x - min + 2 == curSel[curMenu]) ? 252 : 250;

					if (saveFiles[x-2].level == 0)
					{
						strcpy(tempStr, "-----"); /* Empty save slot */
					}
					else
					{
						char buf[20];

						strcpy(tempStr, saveFiles[x-2].levelName);

						snprintf(buf, sizeof buf, "%s%d", miscTextB[1-1], saveFiles[x-2].episode);
						JE_textShade(VGAScreen, 297, tempY, buf, temp2 / 16, temp2 % 16 - 8, DARKEN);
					}

					JE_textShade(VGAScreen, 245, tempY, tempStr, temp2 / 16, temp2 % 16 - 8, DARKEN);
				}

				JE_drawMenuHeader();
			}
		}

		if (curMenu == MENU_KEYBOARD_CONFIG)
		{
			for (int x = 2; x <= 11; x++)
			{
				if (x == curSel[curMenu])
				{
					temp2 = 15;
				}
				else
				{
					temp2 = 28;
				}

				JE_textShade(VGAScreen, 166, 38 + (x - 2)*12, menuInt[curMenu + 1][x-1], temp2 / 16, temp2 % 16 - 8, DARKEN);

				if (x < 10) /* 10 = reset to defaults, 11 = done */
				{
					temp2 = (x == curSel[curMenu]) ? 252 : 250;
					JE_textShade(VGAScreen, 236, 38 + (x - 2)*12, SDL_GetScancodeName(keySettings[x-2]), temp2 / 16, temp2 % 16 - 8, DARKEN);
				}
			}

			menuChoices[MENU_KEYBOARD_CONFIG] = 11;
		}

		if (curMenu == MENU_JOYSTICK_CONFIG)
		{
			const char *const menu_item[] =
			{
				"JOYSTICK",
				"ANALOG AXES",
				" SENSITIVITY",
				" THRESHOLD",
				menuInt[6][1],
				menuInt[6][4],
				menuInt[6][2],
				menuInt[6][3],
				menuInt[6][5],
				menuInt[6][6],
				menuInt[6][7],
				menuInt[6][8],
				"MENU",
				"PAUSE",
				menuInt[6][9],
				menuInt[6][10]
			};

			for (uint i = 0; i < COUNTOF(menu_item); i++)
			{
				int temp = (i == curSel[curMenu] - 2u) ? 15 : 28;

				JE_textShade(VGAScreen, 166, 38 + i * 8, menu_item[i], temp / 16, temp % 16 - 8, DARKEN);

				temp = (i == curSel[curMenu] - 2u) ? 252 : 250;

				char value[30] = "";
				if (joysticks == 0 && i < 14) // no joysticks, everything disabled
				{
					sprintf(value, "-");
				}
				else if (i == 0) // joystick number
				{
					sprintf(value, "%d", joystick_config + 1);
				}
				else if (i == 1) // joystick is analog
				{
					sprintf(value, "%s", joystick[joystick_config].analog ? "TRUE" : "FALSE");
				}
				else if (i < 4)  // joystick analog settings
				{
					if (!joystick[joystick_config].analog)
						temp -= 3;
					sprintf(value, "%d", i == 2 ? joystick[joystick_config].sensitivity : joystick[joystick_config].threshold);
				}
				else if (i < 14) // assignments
				{
					joystick_assignments_to_string(value, sizeof(value), joystick[joystick_config].assignment[i - 4]);
				}

				JE_textShade(VGAScreen, 236, 38 + i * 8, value, temp / 16, temp % 16 - 8, DARKEN);
			}

			menuChoices[curMenu] = COUNTOF(menu_item) + 1;
		}

		if (curMenu == MENU_UPGRADE_SUB)
		{
			/* Move cursor until we hit either "Done" or a weapon the player can afford */
			while (curSel[MENU_UPGRADE_SUB] < menuChoices[MENU_UPGRADE_SUB] &&
			       JE_getCost(curSel[MENU_UPGRADES], itemAvail[itemAvailMap[curSel[MENU_UPGRADES]-2]-1][curSel[MENU_UPGRADE_SUB]-2]) > player[0].cash)
			{
				curSel[MENU_UPGRADE_SUB] += lastDirection;
				if (curSel[MENU_UPGRADE_SUB] < 2)
					curSel[MENU_UPGRADE_SUB] = menuChoices[MENU_UPGRADE_SUB];
				else if (curSel[MENU_UPGRADE_SUB] > menuChoices[MENU_UPGRADE_SUB])
					curSel[MENU_UPGRADE_SUB] = 2;
			}

			if (curSel[MENU_UPGRADE_SUB] == menuChoices[MENU_UPGRADE_SUB])
			{
				/* If cursor on "Done", use previous weapon */
				*playeritem_map(&player[0].items, curSel[MENU_UPGRADES] - 2) = *playeritem_map(&old_items[0], curSel[MENU_UPGRADES] - 2);
			}
			else
			{
				/* Otherwise display the selected weapon */
				*playeritem_map(&player[0].items, curSel[MENU_UPGRADES] - 2) = itemAvail[itemAvailMap[curSel[MENU_UPGRADES]-2]-1][curSel[MENU_UPGRADE_SUB]-2];
			}

			/* Get power level info for front and rear weapons */
			if ((curSel[MENU_UPGRADES] == 3 || curSel[MENU_UPGRADES] == 4) && curSel[MENU_UPGRADE_SUB] < menuChoices[MENU_UPGRADE_SUB])
			{
				if (curSel[MENU_UPGRADES] == 4 && itemAvail[itemAvailMap[curSel[MENU_UPGRADES]-2]-1][curSel[MENU_UPGRADE_SUB]-2] == 0)
				{
					// "None" on rear weapon menu cannot be upgraded
					// ("None" on front weapon menu can -- this is accurate to the original game)
					leftPower = false;
					rightPower = false;
				}
				else
				{
					const uint port = curSel[MENU_UPGRADES] - 3,  // 0 or 1 (front or back)
					           item_level = player[0].items.weapon[port].power;

					// calculate upgradeCost
					JE_getCost(curSel[MENU_UPGRADES], itemAvail[itemAvailMap[curSel[MENU_UPGRADES]-2]-1][curSel[MENU_UPGRADE_SUB]-2]);

					leftPower  = item_level > 1;  // can downgrade
					rightPower = item_level < 11; // can upgrade

					if (rightPower)
						rightPowerAfford = JE_cashLeft() >= upgradeCost; // can afford upgrade
				}
			}
			else
			{
				// Nothing else can be upgraded or downgraded
				leftPower = false;
				rightPower = false;
			}

			/* submenu title  e.g., "Left Sidekick" */
			JE_dString(VGAScreen, 74 + JE_fontCenter(menuInt[2][curSel[MENU_UPGRADES]-1], FONT_SHAPES), 10, menuInt[2][curSel[MENU_UPGRADES]-1], FONT_SHAPES);

			/* Iterate through all submenu options */
			for (tempW = 1; tempW < menuChoices[curMenu]; tempW++)
			{
				int tempY = 40 + (tempW-1) * 26; /* Calculate y position */
				uint temp_cost;

				/* Is this a item or None/DONE? */
				if (tempW < menuChoices[MENU_UPGRADE_SUB] - 1)
				{
					/* Get base cost for choice */
					temp_cost = JE_getCost(curSel[MENU_UPGRADES], itemAvail[itemAvailMap[curSel[MENU_UPGRADES]-2]-1][tempW-1]);
				}
				else
				{
					/* "None" is free :) */
					temp_cost = 0;
				}

				int afford_shade = (temp_cost > player[0].cash) ? 4 : 0;  // can player afford current weapon at all

				temp = itemAvail[itemAvailMap[curSel[MENU_UPGRADES]-2]-1][tempW-1]; /* Item ID */
				switch (curSel[MENU_UPGRADES]-1)
				{
					case 1: /* ship */
						if (temp > 90)
							snprintf(tempStr, sizeof(tempStr), "Custom Ship %d", temp - 90);
						else
							strcpy(tempStr, ships[temp].name);
						break;
					case 2: /* front and rear weapon */
					case 3:
						strcpy(tempStr, weaponPort[temp].name);
						break;
					case 4: /* shields */
						strcpy(tempStr, shields[temp].name);
						break;
					case 5: /* generator */
						strcpy(tempStr, powerSys[temp].name);
						break;
					case 6: /* sidekicks */
					case 7:
						strcpy(tempStr, options[temp].name);
						break;
				}
				if (tempW == curSel[curMenu]-1)
					temp2 = 15;
				else
					temp2 = 28;

				JE_getShipInfo();

				/* item-owned marker */
				if (temp == *playeritem_map(&old_items[0], curSel[MENU_UPGRADES] - 2) && temp != 0 && tempW != menuChoices[curMenu]-1)
				{
					fill_rectangle_xy(VGAScreen, 160, tempY+7, 300, tempY+11, 227);
					blit_sprite2(VGAScreen, 298, tempY+2, shopSpriteSheet, 247);
				}

				/* Draw DONE */
				if (tempW == menuChoices[curMenu]-1)
				{
					strcpy(tempStr, miscText[13]);
				}
				JE_textShade(VGAScreen, 185, tempY, tempStr, temp2 / 16, temp2 % 16 - 8 - afford_shade, DARKEN);

				/* Draw icon if not DONE. NOTE: None is a normal item with a blank icon. */
				if (tempW < menuChoices[curMenu]-1)
				{
					JE_drawItem(curSel[MENU_UPGRADES]-1, temp, 160, tempY-4);
				}

				/* Make selected text brighter */
				temp2 = (tempW == curSel[curMenu]-1) ? 15 : 28;

				/* Draw Cost: if it's not the DONE option */
				if (tempW != menuChoices[curMenu]-1)
				{
					char buf[20];

					snprintf(buf, sizeof buf, "Cost: %d", temp_cost);
					JE_textShade(VGAScreen, 187, tempY+10, buf, temp2 / 16, temp2 % 16 - 8 - afford_shade, DARKEN);
				}
			}
		}

		/* Draw current money and shield/armor bars, when appropriate */
		if (((curMenu <= MENU_OPTIONS ||
		      curMenu == MENU_KEYBOARD_CONFIG ||
		      curMenu == MENU_LOAD_SAVE ||
		      curMenu >= MENU_1_PLAYER_ARCADE) &&
		     !twoPlayerMode) ||
		    (curMenu == MENU_UPGRADE_SUB &&
		     (curSel[MENU_UPGRADES] >= 1 && curSel[MENU_UPGRADES] <= 6)))
		{
			if (curMenu != MENU_UPGRADE_SUB)
			{
				char buf[20];

				snprintf(buf, sizeof buf, "%lu", player[0].cash);
				JE_textShade(VGAScreen, 65, 173, buf, 1, 6, DARKEN);
			}
			JE_barDrawShadow(VGAScreen, 42, 152, 3, 14, player[0].armor, 2, 13);
			JE_barDrawShadow(VGAScreen, 104, 152, 2, 14, shields[player[0].items.shield].mpwr * 2, 2, 13);
		}

		/* Draw crap on the left side of the screen, i.e. two player scores, ship graphic, etc. */
		if ((curMenu >= MENU_FULL_GAME && curMenu <= MENU_OPTIONS) ||
		    curMenu == MENU_KEYBOARD_CONFIG ||
		    curMenu == MENU_LOAD_SAVE ||
		    curMenu >= MENU_2_PLAYER_ARCADE ||
		    (curMenu == MENU_UPGRADE_SUB &&
		     (curSel[MENU_UPGRADES] == 2 || curSel[MENU_UPGRADES] == 5)))
		{
			if (twoPlayerMode)
			{
				char buf[50];

				for (uint i = 0; i < 2; ++i)
				{
					snprintf(buf, sizeof(buf), "%s %lu", miscText[40 + i], player[i].cash);
					JE_textShade(VGAScreen, 25, 50 + 10 * i, buf, 15, 0, FULL_SHADE);
				}
			}
			else if (superArcadeMode != SA_NONE || superTyrian)
			{
				helpBoxColor = 15;
				helpBoxBrightness = 4;
				if (!superTyrian)
					JE_helpBox(VGAScreen, 35, 25, superShips[superArcadeMode], 18);
				else
					JE_helpBox(VGAScreen, 35, 25, superShips[SA+3], 18);
				helpBoxBrightness = 1;

				JE_textShade(VGAScreen, 25, 50, superShips[SA+1], 15, 0, FULL_SHADE);
				JE_helpBox(VGAScreen,   25, 60, weaponPort[player[0].items.weapon[FRONT_WEAPON].id].name, 22);
				JE_textShade(VGAScreen, 25, 120, superShips[SA+2], 15, 0, FULL_SHADE);
				JE_helpBox(VGAScreen,   25, 130, special[player[0].items.special].name, 22);
			}
			else
			{
				draw_ship_illustration();
			}
		}

		/* Changing the volume? */
		if (curMenu == MENU_OPTIONS ||
		    curMenu == MENU_LIMITED_OPTIONS)
		{
			JE_barDrawShadow(VGAScreen, 225, 70, 1, music_disabled ? 12 : 16, tyrMusicVolume / 12, 3, 13);
			JE_barDrawShadow(VGAScreen, 225, 86, 1, samples_disabled ? 12 : 16, fxVolume / 12, 3, 13);
		}

		/* "firstmenu9" refers to menu 8 because of reindexing */
		if (curMenu == MENU_DATA_CUBES ||
		    (curMenu == MENU_DATA_CUBE_SUB && (firstMenu9 || backFromHelp)))
		{
			firstMenu9 = false;
			menuChoices[MENU_DATA_CUBES] = cubeMax + 2;
			fill_rectangle_xy(VGAScreen, 1, 1, 145, 170, 0);

			blit_sprite(VGAScreenSeg, 1, 1, OPTION_SHAPES, 20); /* Portrait area background */

			if (curMenu == MENU_DATA_CUBES)
			{
				if (cubeMax == 0)
				{
					JE_helpBox(VGAScreen, 166, 80, miscText[16 - 1], 30);
					tempW = 160;
					temp2 = 252;
				}
				else
				{
					for (int x = 1; x <= cubeMax; x++)
					{
						JE_drawCube(VGAScreenSeg, 166, 38 + (x - 1) * 28, 13, 0);
						if (x + 1 == curSel[curMenu])
						{
							temp2 = 252;
						}
						else
						{
							temp2 = 250;
						}

						helpBoxColor = temp2 / 16;
						helpBoxBrightness = (temp2 % 16) - 8;
						helpBoxShadeType = DARKEN;
						JE_helpBox(VGAScreen, 192, 44 + (x - 1) * 28, cube[x - 1].title, 24);
					}
					int x = cubeMax + 1;
					if (x + 1 == curSel[curMenu])
					{
						temp2 = 252;
					}
					else
					{
						temp2 = 250;
					}
					tempW = 44 + (x - 1) * 28;
				}

				JE_textShade(VGAScreen, 172, tempW, miscText[6 - 1], temp2 / 16, (temp2 % 16) - 8, DARKEN);
			}

			if (curSel[MENU_DATA_CUBES] < menuChoices[MENU_DATA_CUBES])
			{
				const int face_sprite = cube[curSel[MENU_DATA_CUBES] - 2].face_sprite;

				if (face_sprite != -1)
				{
					const int face_x = 77 - (sprite(FACE_SHAPES, face_sprite)->width / 2),
					          face_y = 92 - (sprite(FACE_SHAPES, face_sprite)->height / 2);

					blit_sprite(VGAScreenSeg, face_x, face_y, FACE_SHAPES, face_sprite);  // datacube face

					// modify palette for face
					paletteChanged = true;
					temp2 = (face_sprite < 12) ? facepal[face_sprite] : 0;
					newPal = 0;

					for (temp = 1; temp <= 255 - (3 * 16); temp++)
						colors[temp] = palettes[temp2][temp];
				}
			}
		}

		/* 2 player input devices */
		if (curMenu == MENU_2_PLAYER_ARCADE)
		{
			for (uint i = 0; i < COUNTOF(inputDevice); i++)
			{
				if (inputDevice[i] > 2 + joysticks)
					inputDevice[i] = inputDevice[i == 0 ? 1 : 0] == 1 ? 2 : 1;

				char temp[64];
				if (joysticks > 1 && inputDevice[i] > 2)
					sprintf(temp, "%s %d", inputDevices[2], inputDevice[i] - 2);
				else
					sprintf(temp, "%s", inputDevices[inputDevice[i] - 1]);
				JE_dString(VGAScreen, 186, 38 + 2 * (i + 1) * 16, temp, SMALL_FONT_SHAPES);
			}
		}

		/* JE: { - Step VI - Help text for current cursor location } */

		flash = false;

		/* JE: {Reset player weapons} */
		memset(shotMultiPos, 0, sizeof(shotMultiPos));

		JE_drawScore();

		JE_drawMainMenuHelpText();

		if (newPal > 0) /* can't reindex this :( */
		{
			curPal = newPal;
			memcpy(colors, palettes[newPal - 1], sizeof(colors));
			set_palette(palettes[newPal - 1], 0, 255);
			newPal = 0;
		}

		/* datacube title under face */
		if ((curMenu == MENU_DATA_CUBES || curMenu == MENU_DATA_CUBE_SUB) &&
			curSel[MENU_DATA_CUBES] < menuChoices[MENU_DATA_CUBES])
		{
			JE_textShade(VGAScreen, 75 - JE_textWidth(cube[curSel[MENU_DATA_CUBES] - 2].header, TINY_FONT) / 2, 173, cube[curSel[MENU_DATA_CUBES] - 2].header, 14, 3, DARKEN);
		}

		/* SYN: Everything above was just drawing the screen. In the rest of it, we process
		   any user input (and do a few other things) */

		/* SYN: Let's start by getting fresh events from SDL */
		service_SDL_events(true);

		if (constantPlay)
		{
			mainLevel = mapSection[mapPNum-1];
			jumpSection = true;
		}
		else
		{
			do
			{
			/* Inner loop -- this handles animations on menus that need them and handles
			   some keyboard events. Events it can't handle end the loop and fall through
			   to the main keyboard handler below.

			   Also, I think all timing is handled in here. Somehow. */

				NETWORK_KEEP_ALIVE();

				// Tyrian3D: the data cube being read, read aloud (voiceover.h).
				voiceover_cube(episodeNum, curMenu == MENU_DATA_CUBE_SUB ? cubeList[currentCube] : 0, cube[currentCube].voice_hash);

				mouseCursor = MOUSE_POINTER_NORMAL;

				col += colC;
				if (col < -2 || col > 6)
				{
					colC = (-1 * colC);
				}

				// data cube reading
				if (curMenu == MENU_DATA_CUBE_SUB)
				{
					if (mouseX > 164 && mouseX < 299 && mouseY > 47 && mouseY < 153)
					{
						if (mouseY > 100)
							mouseCursor = MOUSE_POINTER_DOWN;
						else
							mouseCursor = MOUSE_POINTER_UP;
					}

					fill_rectangle_xy(VGAScreen, 160, 49, 310, 158, 228);
					if (yLoc + yChg < 0)
					{
						yChg = 0;
						yLoc = 0;
					}

					yLoc += yChg;
					temp = yLoc / 12;
					temp2 = yLoc % 12;
					tempW = 38 + 12 - temp2;
					temp3 = cube[curSel[MENU_DATA_CUBES] - 2].last_line;

					for (int x = temp + 1; x <= temp + 10; x++)
					{
						if (x <= temp3)
						{
							JE_outTextAndDarken(VGAScreen, 161, tempW, cube[curSel[MENU_DATA_CUBES] - 2].text[x-1], 14, 3, TINY_FONT);
							tempW += 12;
						}
					}

					fill_rectangle_xy(VGAScreen, 160, 39, 310, 48, 228);
					fill_rectangle_xy(VGAScreen, 160, 157, 310, 166, 228);

					int percent_read = (cube[currentCube].last_line <= 9)
					                   ? 100
					                   : (yLoc * 100) / ((cube[currentCube].last_line - 9) * 12);

					char buf[55];
					snprintf(buf, sizeof(buf), "%s %d%%", miscText[11], percent_read);
					JE_outTextAndDarken(VGAScreen, 176, 160, buf, 14, 1, TINY_FONT);

					JE_dString(VGAScreen, 260, 160, miscText[12], SMALL_FONT_SHAPES);

					if (temp2 == 0)
						yChg = 0;

					shop_publish();  // Tyrian3D: for the modern UI
					JE_mouseStart();

					JE_showVGA();

					if (backFromHelp)
					{
						fade_palette(colors, 10, 0, 255);
						backFromHelp = false;
					}
					JE_mouseReplace();

					setDelay(1);
				}
				else
				{
					/* current menu is not 8 (read data cube) */

					if (curMenu == MENU_PLAY_NEXT_LEVEL)
					{
						JE_updateNavScreen();
						JE_drawMainMenuHelpText();
						JE_drawMenuHeader();
						JE_drawMenuChoices();
						if (extraGame)
							JE_dString(VGAScreen, 170, 140, miscText[68 - 1], FONT_SHAPES);
					}

					if (curMenu == MENU_DATA_CUBES &&
					    curSel[MENU_DATA_CUBES] < menuChoices[MENU_DATA_CUBES])
					{
						/* Draw flashy cube */
						blit_sprite_hv_blend(VGAScreenSeg, 166, 38 + (curSel[MENU_DATA_CUBES] - 2) * 28, OPTION_SHAPES, 25, 13, col);
					}

					/* IF (curmenu = 5) AND (cursel [2] IN [3, 4, 6, 7, 8]) */
					if (curMenu == MENU_UPGRADE_SUB &&
					    (curSel[MENU_UPGRADES] == 3 ||
					     curSel[MENU_UPGRADES] == 4 ||
					     (curSel[MENU_UPGRADES] >= 6 &&
					      curSel[MENU_UPGRADES] <= 8)))
					{
						setDelay(3);
						JE_weaponSimUpdate();
						JE_drawScore();
						service_SDL_events(false);

						if (newPal > 0)
						{
							curPal = newPal;
							set_palette(palettes[newPal - 1], 0, 255);
							newPal = 0;
						}

						shop_publish();  // Tyrian3D: for the modern UI
						JE_mouseStart();

						if (paletteChanged)
						{
							set_palette(colors, 0, 255);
							paletteChanged = false;
						}

						JE_showVGA(); /* SYN: This is where it updates the screen for the weapon sim */

						if (backFromHelp)
						{
							fade_palette(colors, 10, 0, 255);
							backFromHelp = false;
						}

						JE_mouseReplace();

					}
					else  /* current menu is anything but weapon sim or datacube */
					{
						setDelay(2);

						JE_drawScore();

						if (newPal > 0)
						{
							curPal = newPal;
							set_palette(palettes[newPal - 1], 0, 255);
							newPal = 0;
						}

						shop_publish();  // Tyrian3D: for the modern UI
						JE_mouseStart();

						if (paletteChanged)
						{
							set_palette(colors, 0, 255);
							paletteChanged = false;
						}

						JE_showVGA(); /* SYN: This is the where the screen updates for most menus */

						JE_mouseReplace();

						if (backFromHelp)
						{
							fade_palette(colors, 10, 0, 255);
							backFromHelp = false;
						}

					}
				}

				wait_delay();

				push_joysticks_as_keyboard();
				service_SDL_events(false);
				mouseButton = JE_mousePosition(&mouseX, &mouseY);
				inputDetected = newkey || mouseButton > 0;

				if (curMenu != MENU_LOAD_SAVE)
				{
					if (keysactive[SDL_SCANCODE_S] && (keysactive[SDL_SCANCODE_LALT] || keysactive[SDL_SCANCODE_RALT]))
					{
						if (curMenu == MENU_DATA_CUBE_SUB ||
						    curMenu == MENU_DATA_CUBES)
						{
							curMenu = MENU_FULL_GAME;
						}
						quikSave = true;
						oldMenu = curMenu;
						curMenu = MENU_LOAD_SAVE;
						performSave = true;
						newPal = 1;
						oldPal = curPal;
					}
					if (keysactive[SDL_SCANCODE_L] && (keysactive[SDL_SCANCODE_LALT] || keysactive[SDL_SCANCODE_RALT]))
					{
						if (curMenu == MENU_DATA_CUBE_SUB ||
						    curMenu == MENU_DATA_CUBES)
						{
							curMenu = MENU_FULL_GAME;
						}
						quikSave = true;
						oldMenu = curMenu;
						curMenu = MENU_LOAD_SAVE;
						performSave = false;
						newPal = 1;
						oldPal = curPal;
					}
				}

				if (curMenu == MENU_DATA_CUBE_SUB)
				{
					if (mouseButton > 0 && mouseCursor != MOUSE_POINTER_NORMAL)
					{
						inputDetected = false;
						if (mouseCursor == MOUSE_POINTER_UP)
							yChg = -1;
						else
							yChg = 1;
					}

					if (keysactive[SDL_SCANCODE_PAGEUP])
					{
						yChg = -2;
						inputDetected = false;
					}
					if (keysactive[SDL_SCANCODE_PAGEDOWN])
					{
						yChg = 2;
						inputDetected = false;
					}

					bool joystick_up = false, joystick_down = false;
					for (int j = 0; j < joysticks; j++)
					{
						joystick_up |= joystick[j].direction[0];
						joystick_down |= joystick[j].direction[2];
					}

					if (keysactive[SDL_SCANCODE_UP] || joystick_up)
					{
						yChg = -1;
						inputDetected = false;
					}

					if (keysactive[SDL_SCANCODE_DOWN] || joystick_down)
					{
						yChg = 1;
						inputDetected = false;
					}

					// Tyrian3D: the mouse wheel scrolls the text, three lines a notch (a trackpad's parts
					// of a notch add up).
					const int wheel_lines = (int)(mouse_wheel_pending * 3);
					if (wheel_lines != 0)
					{
						const int most = SDL_max(((int)cube[currentCube].last_line - 10) * 12, 0);
						const int to = (int)yLoc - wheel_lines * 12;
						yLoc = (JE_word)SDL_clamp(to - to % 12, 0, most);
						yChg = 0;
						mouse_wheel_pending -= wheel_lines / 3.0f;
					}

					if (yChg < 0 && yLoc == 0)
					{
						yChg = 0;
					}
					if (yChg  > 0 && (yLoc / 12) > cube[currentCube].last_line - 10)
					{
						yChg = 0;
					}
				}

			} while (!inputDetected);
		}

		keyboardUsed = false;

		/* The rest of this just grabs input events, handles them, then proceeds on. */

		if (mouseButton > 0)
		{
			lastDirection = 1;

			mouseButton = JE_mousePosition(&mouseX, &mouseY);

			if (curMenu == MENU_DATA_CUBES && cubeMax == 0)
			{
				curMenu = MENU_FULL_GAME;
				JE_playSampleNum(S_SPRING);
				newPal = 1;
				JE_wipeKey();
			}

			if (curMenu == MENU_DATA_CUBE_SUB)
			{
				if ((mouseX > 258) && (mouseX < 290) && (mouseY > 159) && (mouseY < 171))
				{
					curMenu = MENU_DATA_CUBES;
					JE_playSampleNum(S_SPRING);
				}
			}

			if (curMenu == MENU_OPTIONS ||
			    curMenu == MENU_LIMITED_OPTIONS)
			{
				if ((mouseX >= (225 - 4)) && (mouseY >= 70) && (mouseY <= 82))
				{
					if (music_disabled)
					{
						music_disabled = false;
						restart_song();
					}

					curSel[MENU_OPTIONS] = 4;

					tyrMusicVolume = (mouseX - (225 - 4)) / 4 * 12;
					if (tyrMusicVolume > 255)
						tyrMusicVolume = 255;
				}

				if ((mouseX >= (225 - 4)) && (mouseY >= 86) && (mouseY <= 98))
				{
					samples_disabled = false;

					curSel[MENU_OPTIONS] = 5;

					fxVolume = (mouseX - (225 - 4)) / 4 * 12;
					if (fxVolume > 255)
						fxVolume = 255;
				}

				set_volume(tyrMusicVolume, fxVolume);

				JE_playSampleNum(S_CURSOR);
			}

			if (mouseY > 20 &&
			    mouseX > 170 &&
			    mouseX < 308 &&
			    curMenu != MENU_DATA_CUBE_SUB)
			{
				const JE_byte mouseSelectionY[MENU_MAX] = { 16, 16, 16, 16, 26, 12, 11, 28, 0, 16, 16, 16, 8, 16, 24 };

				int selection = (mouseY - 38) / mouseSelectionY[curMenu]+2;

				if (curMenu == MENU_2_PLAYER_ARCADE)
				{
					if (selection > 5)
						selection--;
					if (selection > 3)
						selection--;
				}

				if (curMenu == MENU_FULL_GAME)
				{
					if (selection > 7)
						selection = 7;
				}

				// is play next level screen?
				if (curMenu == MENU_PLAY_NEXT_LEVEL)
				{
					if (selection == menuChoices[curMenu] + 1)
						selection = menuChoices[curMenu];
				}

				if (selection <= menuChoices[curMenu])
				{
					if (curMenu == MENU_UPGRADE_SUB &&
					    selection == menuChoices[MENU_UPGRADE_SUB])
					{
						player[0].cash = JE_cashLeft();
						curMenu = MENU_UPGRADES;
						JE_playSampleNum(S_ITEM);
					}
					else
					{
						JE_playSampleNum(S_CLICK);
						if (curSel[curMenu] == selection)
						{
							JE_menuFunction(curSel[curMenu]);
						}
						else
						{
							if (curMenu == MENU_UPGRADE_SUB &&
							    JE_getCost(curSel[MENU_UPGRADES], itemAvail[itemAvailMap[curSel[MENU_UPGRADES]-2]-1][selection-2]) > player[0].cash)
							{
								JE_playSampleNum(S_CLINK);
							}
							else
							{
								if (curSel[MENU_UPGRADES] == 4)
									player[0].weapon_mode = 1;

								curSel[curMenu] = selection;
							}

							// in front or rear weapon upgrade screen?
							if (curMenu == MENU_UPGRADE_SUB &&
							    (curSel[MENU_UPGRADES] == 3 || curSel[MENU_UPGRADES] == 4))
							{
								player[0].items.weapon[curSel[MENU_UPGRADES]-3].power = temp_weapon_power[curSel[MENU_UPGRADE_SUB]-2];
							}
						}
					}
				}

				wait_noinput(false, true, false);
			}

			if (curMenu == MENU_UPGRADE_SUB &&
			    (curSel[MENU_UPGRADES] == 3 || curSel[MENU_UPGRADES] == 4))
			{
				if ((mouseX >= 23) && (mouseX <= 36) && (mouseY >= 149) && (mouseY <= 168))
				{
					JE_playSampleNum(S_CURSOR);
					switch (curSel[MENU_UPGRADES])
					{
					case 3:
					case 4:
						if (leftPower)
							player[0].items.weapon[curSel[MENU_UPGRADES]-3].power = --temp_weapon_power[curSel[MENU_UPGRADE_SUB]-2];
						else
							JE_playSampleNum(S_CLINK);

						break;
					}
					wait_noinput(false, true, false);
				}

				if ((mouseX >= 119) && (mouseX <= 131) && (mouseY >= 149) && (mouseY <= 168))
				{
					JE_playSampleNum(S_CURSOR);
					switch (curSel[MENU_UPGRADES])
					{
					case 3:
					case 4:
						if (rightPower && rightPowerAfford)
							player[0].items.weapon[curSel[MENU_UPGRADES]-3].power = ++temp_weapon_power[curSel[MENU_UPGRADE_SUB]-2];
						else
							JE_playSampleNum(S_CLINK);

						break;
					}
					wait_noinput(false, true, false);
				}
			}
		}
		else if (newkey)
		{
			switch (lastkey_scan)
			{
			case SDL_SCANCODE_SLASH:
				// if in rear weapon upgrade screen
				if (curMenu == MENU_UPGRADE_SUB && curSel[MENU_UPGRADES] == 4)
				{
					// cycle weapon modes
					if (++player[0].weapon_mode > weaponPort[player[0].items.weapon[REAR_WEAPON].id].opnum)
						player[0].weapon_mode = 1;
				}
				break;

			case SDL_SCANCODE_SPACE:
			case SDL_SCANCODE_RETURN:
				keyboardUsed = true;

				// if front or rear weapon, update "Done" power level
				if (curMenu == MENU_UPGRADE_SUB && (curSel[MENU_UPGRADES] == 3 || curSel[MENU_UPGRADES] == 4))
					temp_weapon_power[itemAvailMax[itemAvailMap[curSel[MENU_UPGRADES]-2]-1]] = player[0].items.weapon[curSel[MENU_UPGRADES]-3].power;

				JE_menuFunction(curSel[curMenu]);
				break;

			case SDL_SCANCODE_ESCAPE:
				keyboardUsed = true;

				JE_playSampleNum(S_SPRING);
				if (curMenu == MENU_LOAD_SAVE && quikSave)
				{
					curMenu = oldMenu;
					newPal = oldPal;
				}
				else if (menuEsc[curMenu] == 0)
				{
					if (JE_quitRequest())
					{
						gameLoaded = true;
						mainLevel = 0;
					}
				}
				else
				{
					if (curMenu == MENU_UPGRADE_SUB)  // leaving upgrade menu without buying
					{
						player[0].items = old_items[0];
						curSel[MENU_UPGRADE_SUB] = lastCurSel;
						player[0].cash = JE_cashLeft();
					}

					if (curMenu != MENU_DATA_CUBE_SUB)
						newPal = 1;

					curMenu = menuEsc[curMenu] - 1;
				}
				break;

			case SDL_SCANCODE_F1:
				if (!isNetworkGame)
				{
					fade_black(10);
					JE_helpSystem(2);

					play_song(songBuy);

					JE_loadPic(VGAScreen, 1, false);
					newPal = 1;

					switch (curMenu)
					{
					case 3:
						newPal = 18;
						break;
					case 7:
					case 8:
						break;
					}

					memcpy(VGAScreen2->pixels, VGAScreen->pixels, VGAScreen2->pitch * VGAScreen2->h);

					curPal = newPal;
					memcpy(colors, palettes[newPal-1], sizeof(colors));
					JE_showVGA();
					newPal = 0;
					backFromHelp = true;
				}
				break;

			case SDL_SCANCODE_UP:
				keyboardUsed = true;
				lastDirection = -1;

				if (curMenu != MENU_DATA_CUBE_SUB)
					JE_playSampleNum(S_CURSOR);

				curSel[curMenu]--;
				if (curSel[curMenu] < 2)
					curSel[curMenu] = menuChoices[curMenu];

				// if in front or rear weapon upgrade screen
				if (curMenu == MENU_UPGRADE_SUB &&
				    (curSel[MENU_UPGRADES] == 3 || curSel[MENU_UPGRADES] == 4))
				{
					player[0].items.weapon[curSel[MENU_UPGRADES]-3].power = temp_weapon_power[curSel[MENU_UPGRADE_SUB]-2];
					if (curSel[MENU_UPGRADES] == 4)
						player[0].weapon_mode = 1;
				}

				// if joystick config, skip disabled items when digital
				if (curMenu == MENU_JOYSTICK_CONFIG &&
				    joysticks > 0 &&
				    !joystick[joystick_config].analog &&
				    curSel[curMenu] == 5)
				{
					curSel[curMenu] = 3;
				}

				break;

			case SDL_SCANCODE_DOWN:
				keyboardUsed = true;
				lastDirection = 1;

				if (curMenu != MENU_DATA_CUBE_SUB)
					JE_playSampleNum(S_CURSOR);

				curSel[curMenu]++;
				if (curSel[curMenu] > menuChoices[curMenu])
					curSel[curMenu] = 2;

				// if in front or rear weapon upgrade screen
				if (curMenu == MENU_UPGRADE_SUB &&
				    (curSel[MENU_UPGRADES] == 3 || curSel[MENU_UPGRADES] == 4))
				{
					player[0].items.weapon[curSel[MENU_UPGRADES]-3].power = temp_weapon_power[curSel[MENU_UPGRADE_SUB]-2];
					if (curSel[MENU_UPGRADES] == 4)
						player[0].weapon_mode = 1;
				}

				// if in joystick config, skip disabled items when digital
				if (curMenu == MENU_JOYSTICK_CONFIG &&
				    joysticks > 0 &&
				    !joystick[joystick_config].analog &&
				    curSel[curMenu] == 4)
				{
					curSel[curMenu] = 6;
				}

				break;

			case SDL_SCANCODE_HOME:
				if (curMenu == MENU_DATA_CUBE_SUB)
					yLoc = 0;
				break;

			case SDL_SCANCODE_END:
				if (curMenu == MENU_DATA_CUBE_SUB)
					yLoc = (cube[currentCube].last_line - 9) * 12;
				break;

			case SDL_SCANCODE_LEFT:
				if (curMenu == MENU_JOYSTICK_CONFIG)
				{
					if (joysticks > 0)
					{
						switch (curSel[curMenu])
						{
							case 2:
								if (joystick_config == 0)
									joystick_config = joysticks;
								joystick_config--;
								break;
							case 3:
								joystick[joystick_config].analog = !joystick[joystick_config].analog;
								break;
							case 4:
								if (joystick[joystick_config].sensitivity == 0)
									joystick[joystick_config].sensitivity = 10;
								else
									joystick[joystick_config].sensitivity--;
								break;
							case 5:
								if (joystick[joystick_config].threshold == 0)
									joystick[joystick_config].threshold = 10;
								else
									joystick[joystick_config].threshold--;
								break;
							default:
								break;
						}
					}
				}

				if (curMenu == MENU_2_PLAYER_ARCADE)
				{
					switch (curSel[curMenu])
					{
					case 3:
					case 4:
						JE_playSampleNum(S_CURSOR);

						int temp = curSel[curMenu] - 3;
						do
						{
							if (joysticks == 0)
								inputDevice[temp == 0 ? 1 : 0] = inputDevice[temp]; // swap controllers
							if (inputDevice[temp] <= 1)
								inputDevice[temp] = 2 + joysticks;
							else
								inputDevice[temp]--;
						} while (inputDevice[temp] == inputDevice[temp == 0 ? 1 : 0]);
						break;
					}
				}

				if (curMenu == MENU_OPTIONS ||
				    curMenu == MENU_UPGRADE_SUB ||
				    curMenu == MENU_LIMITED_OPTIONS)
				{
					JE_playSampleNum(S_CURSOR);
				}

				switch (curMenu)
				{
				case 2:
				case 11:
					switch (curSel[curMenu])
					{
					case 4:
						JE_changeVolume(&tyrMusicVolume, -12, &fxVolume, 0);
						if (music_disabled)
						{
							music_disabled = false;
							restart_song();
						}
						break;
					case 5:
						JE_changeVolume(&tyrMusicVolume, 0, &fxVolume, -12);
						samples_disabled = false;
						break;
					}
					break;
				case 4:
					switch (curSel[MENU_UPGRADES])
					{
					case 3:
					case 4:
						if (leftPower)
							player[0].items.weapon[curSel[MENU_UPGRADES]-3].power = --temp_weapon_power[curSel[MENU_UPGRADE_SUB]-2];
						else
							JE_playSampleNum(S_CLINK);

						break;
					}
					break;
				}
				break;

			case SDL_SCANCODE_RIGHT:
				if (curMenu == MENU_JOYSTICK_CONFIG)
				{
					if (joysticks > 0)
					{
						switch (curSel[curMenu])
						{
							case 2:
								joystick_config++;
								joystick_config %= joysticks;
								break;
							case 3:
								joystick[joystick_config].analog = !joystick[joystick_config].analog;
								break;
							case 4:
								joystick[joystick_config].sensitivity++;
								joystick[joystick_config].sensitivity %= 11;
								break;
							case 5:
								joystick[joystick_config].threshold++;
								joystick[joystick_config].threshold %= 11;
								break;
							default:
								break;
						}
					}
				}

				if (curMenu == MENU_2_PLAYER_ARCADE)
				{
					switch (curSel[curMenu])
					{
					case 3:
					case 4:
						JE_playSampleNum(S_CURSOR);

						int temp = curSel[curMenu] - 3;
						do
						{
							if (joysticks == 0)
								inputDevice[temp == 0 ? 1 : 0] = inputDevice[temp]; // swap controllers
							if (inputDevice[temp] >= 2 + joysticks)
								inputDevice[temp] = 1;
							else
								inputDevice[temp]++;
						} while (inputDevice[temp] == inputDevice[temp == 0 ? 1 : 0]);
						break;
					}
				}

				if (curMenu == MENU_OPTIONS ||
				    curMenu == MENU_UPGRADE_SUB ||
				    curMenu == MENU_LIMITED_OPTIONS)
				{
					JE_playSampleNum(S_CURSOR);
				}

				switch (curMenu)
				{
				case 2:
				case 11:
					switch (curSel[curMenu])
					{
					case 4:
						JE_changeVolume(&tyrMusicVolume, 12, &fxVolume, 0);
						if (music_disabled)
						{
							music_disabled = false;
							restart_song();
						}
						break;
					case 5:
						JE_changeVolume(&tyrMusicVolume, 0, &fxVolume, 12);
						samples_disabled = false;
						break;
					}
					break;
				case 4:
					switch (curSel[MENU_UPGRADES])
					{
					case 3:
					case 4:
						if (rightPower && rightPowerAfford)
							player[0].items.weapon[curSel[MENU_UPGRADES]-3].power = ++temp_weapon_power[curSel[MENU_UPGRADE_SUB]-2];
						else
							JE_playSampleNum(S_CLINK);

						break;
					}
					break;
				}
				break;

			default:
				break;
			}
		}

	} while (!(quit || gameLoaded || jumpSection));

	voiceover_stop();  // Tyrian3D

#ifdef WITH_NETWORK
	if (!quit && isNetworkGame)
	{
		JE_barShade(VGAScreen, 3, 3, 316, 196);
		JE_barShade(VGAScreen, 1, 1, 318, 198);
		JE_dString(VGAScreen, 10, 160, "Waiting for other player.", SMALL_FONT_SHAPES);

		network_prepare(PACKET_WAITING);
		network_send(4);  // PACKET_WAITING

		while (true)
		{
			service_SDL_events(false);
			JE_showVGA();

			if (packet_in[0] && SDLNet_Read16(&packet_in[0]->data[0]) == PACKET_WAITING)
			{
				network_update();
				break;
			}

			network_update();
			network_check();

			SDL_Delay(16);
		}

		network_state_reset();
	}

	if (isNetworkGame)
	{
		while (!network_is_sync())
		{
			service_SDL_events(false);
			JE_showVGA();

			network_check();
			SDL_Delay(16);
		}
	}
#endif

	if (gameLoaded)
		fade_black(10);
	shop_showing = false;
}

// The store's illustration of the ship: where its pieces are drawn (see ship_illustration_piece).
static const int illustration_weapon_sprites[60] =
{
	-1,  0,  1,  2,  3,  4,  5,  6,  7,  8,
	 9, 10, 11, 21,  5, 13, -1, 14, 15,  0,
	14,  9,  8,  2, 15,  0, 13,  0,  8,  8,
	11,  1,  0,  0,  0,  0,  0,  0,  0,  0,
	 0,  2,  1,  0,  0,  1,  1,  1
};

static const int illustration_front_xy_list[60] =
{
	 -1,  4,  9,  3,  8,  2,  5, 10,  1, -1,
	 -1, -1, -1,  7,  8, -1, -1,  0, -1,  4,
	  0, -1, -1,  3, -1,  4, -1,  4, -1, -1,
	 -1,  9,  0,  0,  0,  0,  0,  0,  0,  0,
	  0,  3,  9,  4,  4,  9,  9,  9
};
static const int illustration_front_x[12] = { 59, 66, 66, 54, 61, 51, 58, 51, 61, 52, 53, 58 };
static const int illustration_front_y[12] = { 38, 53, 41, 36, 48, 35, 41, 35, 53, 41, 39, 31 };

static const int illustration_rear_xy_list[60] =
{
	-1, -1, -1, -1, -1, -1, -1, -1, -1,  0,
	 1,  2,  3, -1,  4,  5, -1, -1,  6, -1,
	-1,  1,  0, -1,  6, -1,  5, -1,  0,  0,
	 3,  0,  0,  0,  0,  0,  0,  0,  0,  0,
	 0, -1, -1, -1, -1, -1, -1, -1
};
static const int illustration_rear_x[7] = { 41, 27,  49,  43, 51, 39, 41 };
static const int illustration_rear_y[7] = { 92, 92, 113, 102, 97, 96, 76 };

bool ship_illustration_piece(IllustrationPart part, const PlayerItems *items, unsigned int *table, int *sprite_id,
                             int *x, int *y)
{
	switch (part)
	{
	case ILLUSTRATION_SHIP:
	{
		if (items->ship == 0)
			return false;
		// full of evil hardcoding
		*sprite_id = (items->ship < COUNTOF(ships))  // shipedit ships get a default
		             ? ships[items->ship].bigshipgraphic - 1
		             : 31;

		static const int ship_x[] = { 31, 0, 0, 0, 35, 31, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 36, 30 },
		                 ship_y[] = { 36, 0, 0, 0, 33, 35, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 33, 30 };
		*x = ship_x[*sprite_id - 27];
		*y = ship_y[*sprite_id - 27];
		*table = OPTION_SHAPES;
		return true;
	}
	case ILLUSTRATION_GENERATOR:
	{
		if (items->generator <= 0 || items->generator >= 7)
			return false;
		*sprite_id = (items->generator == 1)  // generator 1 and generator 2 have the same sprite
		             ? items->generator + 15
		             : items->generator + 14;

		static const int generator_x[5] = { 62, 64, 67, 66, 63 },
		                 generator_y[5] = { 84, 85, 86, 84, 97 };
		*x = generator_x[*sprite_id - 16];
		*y = generator_y[*sprite_id - 16];
		*table = WEAPON_SHAPES;
		return true;
	}
	case ILLUSTRATION_FRONT:
	case ILLUSTRATION_REAR:
	{
		const bool front = part == ILLUSTRATION_FRONT;
		const unsigned int id = items->weapon[front ? FRONT_WEAPON : REAR_WEAPON].id;
		if (id == 0 || id >= COUNTOF(illustration_weapon_sprites))
			return false;
		const int place = front ? illustration_front_xy_list[id] : illustration_rear_xy_list[id];
		if (place < 0 || illustration_weapon_sprites[id] < 0)
			return false;
		*sprite_id = illustration_weapon_sprites[id];
		*x = front ? illustration_front_x[place] : illustration_rear_x[place];
		*y = front ? illustration_front_y[place] : illustration_rear_y[place];
		*table = WEAPON_SHAPES;
		return true;
	}
	}
	return false;
}

void draw_ship_illustration(void)
{
	video_showcase_begin();  // Tyrian3D: the 3D view shows the ship as a model over the box

	unsigned int table;
	int sprite_id, x, y;

	// ship
	assert(player[0].items.ship > 0);
	if (ship_illustration_piece(ILLUSTRATION_SHIP, &player[0].items, &table, &sprite_id, &x, &y))
		blit_sprite(VGAScreenSeg, x, y, table, sprite_id);

	// generator
	assert(player[0].items.generator > 0 && player[0].items.generator < 7);
	if (ship_illustration_piece(ILLUSTRATION_GENERATOR, &player[0].items, &table, &sprite_id, &x, &y))
		blit_sprite(VGAScreenSeg, x, y, table, sprite_id);

	// front weapon
	if (ship_illustration_piece(ILLUSTRATION_FRONT, &player[0].items, &table, &sprite_id, &x, &y))
		blit_sprite(VGAScreenSeg, x, y, table, sprite_id);  // ship illustration: front weapon

	// rear weapon
	if (ship_illustration_piece(ILLUSTRATION_REAR, &player[0].items, &table, &sprite_id, &x, &y))
		blit_sprite(VGAScreenSeg, x, y, table, sprite_id);

	// sidekicks
	JE_drawItem(6, player[0].items.sidekick[LEFT_SIDEKICK], 3, 84);
	JE_drawItem(7, player[0].items.sidekick[RIGHT_SIDEKICK], 129, 84);

	// shield
	blit_sprite_hv(VGAScreenSeg, 28, 23, OPTION_SHAPES, 26, 15, shields[player[0].items.shield].mpwr - 10);

	// Tyrian3D: the shield's arc stays on the box under the ship's model.
	SDL_Surface *backdrop = video_showcase_backdrop();
	if (backdrop != NULL)
		blit_sprite_hv(backdrop, 28, 23, OPTION_SHAPES, 26, 15, shields[player[0].items.shield].mpwr - 10);
	video_showcase_end();
}

void load_cubes(void)
{
	for (int cube_slot = 0; cube_slot < cubeMax; ++cube_slot)
	{
		memset(cube[cube_slot].text, 0, sizeof(cube->text));

		load_cube(cube_slot, cubeList[cube_slot]);
	}
}

bool load_cube(int cube_slot, int cube_index)
{
	FILE *f = dir_fopen_die(data_dir(), cube_file, "rb");

	char buf[256];

	// seek to the cube
	while (cube_index > 0)
	{
		read_encrypted_pascal_string(buf, sizeof(buf), f);
		if (buf[0] == '*')
			--cube_index;
	}

	str_pop_int(&buf[4], &cube[cube_slot].face_sprite);
	--cube[cube_slot].face_sprite;

	read_encrypted_pascal_string(cube[cube_slot].title, sizeof(cube[cube_slot].title), f);
	read_encrypted_pascal_string(cube[cube_slot].header, sizeof(cube[cube_slot].header), f);

	uint line = 0, line_chars = 0, line_width = 0;
	cube[cube_slot].voice_hash = VOICEOVER_HASH_START;

	// for each line of decrypted text, split the line into words
	// and add them individually to the lines of wrapped text
	for (; ; )
	{
		read_encrypted_pascal_string(buf, sizeof(buf), f);

		// end of data
		if (buf[0] == '*')
			break;

		cube[cube_slot].voice_hash = voiceover_hash(cube[cube_slot].voice_hash, buf);  // Tyrian3D

		// new paragraph
		if (strlen(buf) == 0)
		{
			if (line_chars == 0)
				line += 4;  // subsequent new paragaphs indicate 4-line break
			else
				++line;
			line_chars = 0;
			line_width = 0;

			continue;
		}

		uint word_start = 0;
		for (uint i = 0; ; ++i)
		{
			bool end_of_line = (buf[i] == '\0'),
			     end_of_word = end_of_line || (buf[i] == ' ');

			if (end_of_word)
			{
				buf[i] = '\0';

				char *word = &buf[word_start];
				word_start = i + 1;

				uint word_chars = strlen(word),
				     word_width = JE_textWidth(word, TINY_FONT);

				// word won't fit; no can do
				if (word_chars > cube_line_chars || word_width > cube_line_width)
					break;

				bool prepend_space = true;

				line_chars += word_chars + (prepend_space ? 1 : 0);
				line_width += word_width + (prepend_space ? 6 : 0);

				// word won't fit on current line; use next
				if (line_chars > cube_line_chars || line_width > cube_line_width)
				{
					++line;
					line_chars = word_chars;
					line_width = word_width;

					prepend_space = false;
				}

				// append word
				if (line < COUNTOF(cube->text))
				{
					if (prepend_space)
						strcat(cube[cube_slot].text[line], " ");
					strcat(cube[cube_slot].text[line], word);

					// track last line with text
					cube[cube_slot].last_line = line + 1;
				}
			}

			if (end_of_line)
				break;
		}
	}

	fclose(f);

	return true;
}

void JE_drawItem(JE_byte itemType, JE_word itemNum, JE_word x, JE_word y)
{
	JE_word tempW = 0;

	if (itemNum > 0)
	{
		switch (itemType)
		{
			case 2:
			case 3:
				tempW = weaponPort[itemNum].itemgraphic;
				break;
			case 5:
				tempW = powerSys[itemNum].itemgraphic;
				break;
			case 6:
			case 7:
				tempW = options[itemNum].itemgraphic;
				break;
			case 4:
				tempW = shields[itemNum].itemgraphic;
				break;
		}

		if (itemType == 1)
		{
			if (itemNum > 90)
			{
				shipGrPtr = &spriteSheet9;
				shipGr = JE_SGr(itemNum - 90, &shipGrPtr);
				blit_sprite2x2(VGAScreen, x, y, *shipGrPtr, shipGr);
			}
			else if (ships[itemNum].shipgraphic > 500)
			{
				blit_sprite2x2(VGAScreen, x, y, spriteSheetT2000, ships[itemNum].shipgraphic - 500);
			}
			else
			{
				blit_sprite2x2(VGAScreen, x, y, spriteSheet9, ships[itemNum].shipgraphic);
			}
		}
		else if (tempW > 0)
		{
			blit_sprite2x2(VGAScreen, x, y, shopSpriteSheet, tempW);
		}
	}
}

// Tyrian3D: the current menu's title for the modern UI, as JE_drawMenuHeader's (a part's choices: their part's).
static void menu_header_text(char *out, size_t size)
{
	switch (curMenu)
	{
		case MENU_DATA_CUBE_SUB:
			SDL_strlcpy(out, cube[curSel[MENU_DATA_CUBES]-2].header, size);
			break;
		case MENU_DATA_CUBES:
			SDL_strlcpy(out, menuInt[1][1], size);
			break;
		case MENU_LOAD_SAVE:
			SDL_strlcpy(out, menuInt[3][performSave + 1], size);
			break;
		case MENU_UPGRADE_SUB:
			SDL_strlcpy(out, menuInt[2][curSel[MENU_UPGRADES]-1], SDL_min(size, sizeof(menuInt[2][0])));
			break;
		default:
			SDL_strlcpy(out, menuInt[curMenu + 1][0], SDL_min(size, sizeof(menuInt[0][0])));
			break;
	}
}

void JE_drawMenuHeader(void)
{
	switch (curMenu)
	{
		case MENU_DATA_CUBE_SUB:
			strcpy(tempStr, cube[curSel[MENU_DATA_CUBES]-2].header);
			break;
		case MENU_DATA_CUBES:
			strcpy(tempStr, menuInt[1][1]);
			break;
		case MENU_LOAD_SAVE:
			strcpy(tempStr, menuInt[3][performSave + 1]);
			break;
		default:
			strcpy(tempStr, menuInt[curMenu + 1][0]);
			break;
	}
	JE_dString(VGAScreen, 74 + JE_fontCenter(tempStr, FONT_SHAPES), 10, tempStr, FONT_SHAPES);
}

void JE_drawMenuChoices(void)
{
	JE_byte x;
	char *str;

	for (x = 2; x <= menuChoices[curMenu]; x++)
	{
		int tempY = 38 + (x-1) * 16;

		if (curMenu == MENU_FULL_GAME)
		{
			if (x == 7)
			{
				tempY += 16;
			}
		}

		if (curMenu == MENU_2_PLAYER_ARCADE)
		{
			if (x > 3)
			{
				tempY += 16;
			}
			if (x > 4)
			{
				tempY += 16;
			}
		}

		if (!(curMenu == MENU_PLAY_NEXT_LEVEL &&
		      x == menuChoices[curMenu]))
		{
			tempY -= 16;
		}

		if (curMenu == MENU_MOUSE_CONFIG)
		{
			tempY += (x-2) * 8;
		}

		str = malloc(strlen(menuInt[curMenu + 1][x-1])+2);
		if (curSel[curMenu] == x)
		{
			str[0] = '~';
			strcpy(str+1, menuInt[curMenu + 1][x-1]);
		}
		else
		{
			strcpy(str, menuInt[curMenu + 1][x-1]);
		}
		JE_dString(VGAScreen, 166, tempY, str, SMALL_FONT_SHAPES);
		free(str);
	}
}

void JE_updateNavScreen(void)
{
	JE_byte x;

	/* minor issues: */
	/* TODO: The scroll to the new planet is too fast, I think */
	/* TODO: The starting coordinates for the scrolling effect may be wrong, the
	   yellowish planet below Tyrian isn't visible for as many frames as in the
	   original. */

	tempNavX = roundf(navX);
	tempNavY = roundf(navY);
	fill_rectangle_xy(VGAScreen, 19, 16, 135, 169, 2);
	JE_drawNavLines(true);
	JE_drawNavLines(false);
	JE_drawDots();

	for (x = 0; x < 11; x++)
		JE_drawPlanet(x);

	for (x = 0; x < menuChoices[MENU_PLAY_NEXT_LEVEL]-1; x++)
	{
		if (mapPlanet[x] > 11)
			JE_drawPlanet(mapPlanet[x] - 1);
	}

	if (mapOrigin > 11)
		JE_drawPlanet(mapOrigin - 1);

	blit_sprite(VGAScreenSeg, 0, 0, OPTION_SHAPES, 28);  // navigation screen interface

	if (curSel[MENU_PLAY_NEXT_LEVEL] < menuChoices[MENU_PLAY_NEXT_LEVEL])
	{
		const unsigned int origin_x_offset = sprite(PLANET_SHAPES, PGR[mapOrigin-1]-1)->width / 2,
		                   origin_y_offset = sprite(PLANET_SHAPES, PGR[mapOrigin-1]-1)->height / 2,
		                   dest_x_offset = sprite(PLANET_SHAPES, PGR[mapPlanet[curSel[MENU_PLAY_NEXT_LEVEL]-2] - 1]-1)->width / 2,
		                   dest_y_offset = sprite(PLANET_SHAPES, PGR[mapPlanet[curSel[MENU_PLAY_NEXT_LEVEL]-2] - 1]-1)->height / 2;

		newNavX = (planetX[mapOrigin-1] - origin_x_offset
		          + planetX[mapPlanet[curSel[MENU_PLAY_NEXT_LEVEL]-2] - 1] - dest_x_offset) / 2.0f;
		newNavY = (planetY[mapOrigin-1] - origin_y_offset
		          + planetY[mapPlanet[curSel[MENU_PLAY_NEXT_LEVEL]-2] - 1] - dest_y_offset) / 2.0f;
	}

	navX = navX + (newNavX - navX) / 2.0f;
	navY = navY + (newNavY - navY) / 2.0f;

	if (fabsf(newNavX - navX) < 1)
		navX = newNavX;
	if (fabsf(newNavY - navY) < 1)
		navY = newNavY;

	fill_rectangle_xy(VGAScreen, 314, 0, 319, 199, 230);

	if (planetAniWait > 0)
	{
		planetAniWait--;
	}
	else
	{
		planetAni++;
		if (planetAni > 14)
			planetAni = 0;
		planetAniWait = 3;
	}

	if (currentDotWait > 0)
	{
		currentDotWait--;
	}
	else
	{
		if (currentDotNum < planetDots[curSel[MENU_PLAY_NEXT_LEVEL]-2])
			currentDotNum++;
		currentDotWait = 5;
	}
}

void JE_drawLines(SDL_Surface *surface, JE_boolean dark)
{
	JE_byte x, y;
	JE_integer tempX, tempY;
	JE_integer tempX2, tempY2;
	JE_word tempW, tempW2;

	tempX2 = -10;
	tempY2 = 0;

	tempW = 0;
	for (x = 0; x < 20; x++)
	{
		tempW += 15;
		tempX = tempW - tempX2;

		if (tempX > 18 && tempX < 135)
		{
			if (dark)
				JE_rectangle(surface, tempX + 1, 0, tempX + 1, 199, 32+3);
			else
				JE_rectangle(surface, tempX, 0, tempX, 199, 32+5);
		}
	}

	tempW = 0;
	for (y = 0; y < 20; y++)
	{
		tempW += 15;
		tempY = tempW - tempY2;

		if (tempY > 15 && tempY < 169)
		{
			if (dark)
				JE_rectangle(surface, 0, tempY + 1, 319, tempY + 1, 32+3);
			else
				JE_rectangle(surface, 0, tempY, 319, tempY, 32+5);

			tempW2 = 0;

			for (x = 0; x < 20; x++)
			{
				tempW2 += 15;
				tempX = tempW2 - tempX2;
				if (tempX > 18 && tempX < 135)
				{
					JE_pix3(surface, tempX, tempY, 32+6);
				}
			}
		}
	}
}

/* SYN: This was originally PROC drawlines... yes, there were two different procs called
   drawlines in different scopes in the same file. Dammit, Jason, why do you do this to me? */

void JE_drawNavLines(JE_boolean dark)
{
	JE_byte x, y;
	JE_integer tempX, tempY;
	JE_integer tempX2, tempY2;
	JE_word tempW, tempW2;

	tempX2 = tempNavX >> 1;
	tempY2 = tempNavY >> 1;

	tempW = 0;
	for (x = 1; x <= 20; x++)
	{
		tempW += 15;
		tempX = tempW - tempX2;

		if (tempX > 18 && tempX < 135)
		{
			if (dark)
				JE_rectangle(VGAScreen, tempX + 1, 16, tempX + 1, 169, 1);
			else
				JE_rectangle(VGAScreen, tempX, 16, tempX, 169, 5);
		}
	}

	tempW = 0;
	for (y = 1; y <= 20; y++)
	{
		tempW += 15;
		tempY = tempW - tempY2;

		if (tempY > 15 && tempY < 169)
		{
			if (dark)
				JE_rectangle(VGAScreen, 19, tempY + 1, 135, tempY + 1, 1);
			else
				JE_rectangle(VGAScreen, 8, tempY, 160, tempY, 5);

			tempW2 = 0;

			for (x = 0; x < 20; x++)
			{
				tempW2 += 15;
				tempX = tempW2 - tempX2;
				if (tempX > 18 && tempX < 135)
					JE_pix3(VGAScreen, tempX, tempY, 7);
			}
		}
	}
}

void JE_drawDots(void)
{
	JE_byte x, y;
	JE_integer tempX, tempY;

	for (x = 0; x < mapPNum; x++)
	{
		for (y = 0; y < planetDots[x]; y++)
		{
			tempX = planetDotX[x][y] - tempNavX + 66 - 2;
			tempY = planetDotY[x][y] - tempNavY + 85 - 2;
			if (tempX > 0 && tempX < 140 && tempY > 0 && tempY < 168)
				blit_sprite(VGAScreenSeg, tempX, tempY, OPTION_SHAPES, (x == curSel[MENU_PLAY_NEXT_LEVEL]-2 && y < currentDotNum) ? 30 : 29);  // navigation dots
		}
	}
}

void JE_drawPlanet(JE_byte planetNum)
{
	JE_integer tempZ = PGR[planetNum]-1,
	           tempX = planetX[planetNum] + 66 - tempNavX - sprite(PLANET_SHAPES, tempZ)->width / 2,
	           tempY = planetY[planetNum] + 85 - tempNavY - sprite(PLANET_SHAPES, tempZ)->height / 2;

	if (tempX > -7 && tempX + sprite(PLANET_SHAPES, tempZ)->width < 170 && tempY > 0 && tempY < 160)
	{
		if (PAni[planetNum])
			tempZ += planetAni;

		blit_sprite_dark(VGAScreenSeg, tempX + 3, tempY + 3, PLANET_SHAPES, tempZ, false);
		blit_sprite(VGAScreenSeg, tempX, tempY, PLANET_SHAPES, tempZ);  // planets
	}
}

void JE_scaleBitmap(SDL_Surface *dst_bitmap, const SDL_Surface *src_bitmap,  int x1, int y1, int x2, int y2)
{
	/* This function scales one screen and writes the result to another.
	 *  The only code that calls it is the code run when you select 'ship
	 * specs' from the main menu.
	 *
	 * Originally this used fixed point math.  I haven't seen that in ages :).
	 * But we're well past the point of needing that.*/

	assert(src_bitmap != NULL && dst_bitmap != NULL);
	assert(x1 >= 0 && y1 >= 0 && x2 < src_bitmap->pitch && y2 < src_bitmap->h);

	int w = x2 - x1 + 1,
	    h = y2 - y1 + 1;
	float base_skip_w = src_bitmap->pitch / (float)w,
	      base_skip_h = src_bitmap->h / (float)h;
	float cumulative_skip_w, cumulative_skip_h;

	//Okay, it's time to loop through and add bits of A to a rectangle in B
	Uint8 *dst = dst_bitmap->pixels;  /* 8-bit specific */
	const Uint8 *src, *src_w;  /* 8-bit specific */

	dst += y1 * dst_bitmap->pitch + x1;
	cumulative_skip_h = 0;

	for (int i = 0; i < h; i++)
	{
		//this sets src to the beginning of our desired line
		src = src_w = (Uint8 *)(src_bitmap->pixels) + (src_bitmap->w * ((unsigned int)cumulative_skip_h));
		cumulative_skip_h += base_skip_h;
		cumulative_skip_w = 0;

		for (int j = 0; j < w; j++)
		{
			//copy and move pointers
			*dst = *src;
			dst++;

			cumulative_skip_w += base_skip_w;
			src = src_w + ((unsigned int)cumulative_skip_w); //value is floored
		}

		dst += dst_bitmap->pitch - w;
	}
}

void JE_initWeaponView(void)
{
	fill_rectangle_xy(VGAScreen, 8, 8, 144, 177, 0);

	player[0].sidekick[LEFT_SIDEKICK].x = 72 - 15;
	player[0].sidekick[LEFT_SIDEKICK].y = 120;
	player[0].sidekick[RIGHT_SIDEKICK].x = 72 + 15;
	player[0].sidekick[RIGHT_SIDEKICK].y = 120;

	player[0].x = 72;
	player[0].y = 110;
	player[0].delta_x_shot_move = 0;
	player[0].delta_y_shot_move = 0;
	player[0].last_x_explosion_follow = 72;
	player[0].last_y_explosion_follow = 110;
	power = 500;
	lastPower = 500;

	memset(shotAvail, 0, sizeof(shotAvail));

	memset(shotRepeat, 1, sizeof(shotRepeat));
	memset(shotMultiPos, 0, sizeof(shotMultiPos));

	initialize_starfield();
}

void JE_computeDots(void)
{
	JE_integer tempX, tempY;
	JE_longint distX, distY;
	JE_byte x, y;

	for (x = 0; x < mapPNum; x++)
	{
		distX = (int)(planetX[mapPlanet[x]-1]) - (int)(planetX[mapOrigin-1]);
		distY = (int)(planetY[mapPlanet[x]-1]) - (int)(planetY[mapOrigin-1]);
		tempX = abs(distX) + abs(distY);

		if (tempX != 0)
			planetDots[x] = roundf(sqrtf(sqrtf((distX * distX) + (distY * distY)))) - 1;
		else
			planetDots[x] = 0;

		if (planetDots[x] > 10)
			planetDots[x] = 10;

		for (y = 0; y < planetDots[x]; y++)
		{
			tempX = JE_partWay(planetX[mapOrigin-1], planetX[mapPlanet[x]-1], planetDots[x], y);
			tempY = JE_partWay(planetY[mapOrigin-1], planetY[mapPlanet[x]-1], planetDots[x], y);
			/* ??? Why does it use temp? =P */
			planetDotX[x][y] = tempX;
			planetDotY[x][y] = tempY;
		}
	}
}

JE_integer JE_partWay(JE_integer start, JE_integer finish, JE_byte dots, JE_byte dist)
{
	return (finish - start) / (dots + 2) * (dist + 1) + start;
}

void JE_doShipSpecs(void)
{
	/* This function is called whenever you select 'ship specs' in the
	 * game menu.  It draws the nice green tech screen and scales it onto
	 * the main window.  To do this we need two temp buffers, so we're going
	 * to use VGAScreen and game_screen for the purpose (making things more
	 * complex than they would be if we just malloc'd, but faster)
	 *
	 * Originally the whole system was pretty oddly designed.  So I changed it.
	 * Currently drawFunkyScreen creates the image, scaleInPicture draws it,
	 * and doFunkyScreen ties everything together.  Before it was more like
	 * an oddly designed, unreusable, global sharing hierarchy. */

	//create the image we want
	wait_noinput(true, true, true);
	JE_drawShipSpecs(game_screen, VGAScreen2);

	//reset VGAScreen2, which we clobbered
	JE_loadPic(VGAScreen2, 1, false);

	//draw it
	JE_playSampleNum(S_SPRING);
	shop_specs_publish();  // Tyrian3D: the modern UI shows its own while the picture zooms in and after
	JE_scaleInPicture(VGAScreen, game_screen);
	if (ui_modern())
	{
		// (The same wait, shown on meanwhile: its 3D ship turns.)
		service_SDL_events(false);
		Uint64 shown = SDL_GetTicks();
		while (!(keydown || mousedown || joydown))
		{
			SDL_Delay(SDL_POLL_INTERVAL);
			push_joysticks_as_keyboard();
			service_SDL_events(false);
#ifdef WITH_NETWORK
			if (isNetworkGame)
				network_check();
#endif
			if (SDL_GetTicks() - shown >= 30)
			{
				JE_showVGA();
				shown = SDL_GetTicks();
			}
		}
	}
	else
		wait_input(true, true, true);
	ui_menu_release();
}

// The help line at the screen's foot for the current menu and choice (Tyrian3D: also for the modern UI).
static void main_menu_help_text(char *tempStr)
{
	JE_byte temp;

	temp = curSel[curMenu] - 2;
	if (curMenu == MENU_JOYSTICK_CONFIG) // joystick settings menu help
	{
		const int help[16] = { 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 24, 11 };
		memcpy(tempStr, mainMenuHelp[help[curSel[curMenu] - 2]], 67);
	}
	else if (curMenu < MENU_PLAY_NEXT_LEVEL || curMenu >= MENU_2_PLAYER_ARCADE)
	{
		memcpy(tempStr, mainMenuHelp[(menuHelp[curMenu][temp])-1], 67);
	}
	else if (curMenu == MENU_KEYBOARD_CONFIG &&
	         curSel[MENU_KEYBOARD_CONFIG] == 10)
	{
		memcpy(tempStr, mainMenuHelp[25-1], 67);
	}
	else if (leftPower || rightPower)
	{
		memcpy(tempStr, mainMenuHelp[24-1], 67);
	}
	else if (temp == menuChoices[curMenu] - 2 ||
	         (curMenu == MENU_DATA_CUBES && cubeMax == 0))
	{
		memcpy(tempStr, mainMenuHelp[12-1], 67);
	}
	else
	{
		memcpy(tempStr, mainMenuHelp[17 + curMenu - 3], 67);
	}
}

void JE_drawMainMenuHelpText(void)
{
	char tempStr[67];
	main_menu_help_text(tempStr);
	JE_textShade(VGAScreen, 10, 187, tempStr, 14, 1, DARKEN);
}

JE_boolean JE_saveRequest(JE_byte slot, const char *savename)
{
	bool save_selected = true, done = false;

	JE_clearKeyboard();
	JE_wipeKey();
	wait_noinput(true, true, true);

	JE_barShade(VGAScreen, 65, 55, 255, 155);

	while (!done)
	{
		Uint8 col = 8;
		int colC = 1;

		do
		{
			service_SDL_events(true);
			setDelay(4);

			blit_sprite(VGAScreen, 50, 50, OPTION_SHAPES, 35);  // message box
			JE_textShade(VGAScreen, 70, 66, miscText[68], 0, 5, FULL_SHADE); // Are you sure you want to save?
			JE_textShade(VGAScreen, 74, 90, miscText[1], 12, 1, FULL_SHADE); // Save name:
			JE_textShade(VGAScreen, 135, 90, savename, 12, 1, FULL_SHADE);
			JE_textShade(VGAScreen, 74, 100, miscText[69], 12, 1, FULL_SHADE); // Original save:
			JE_textShade(VGAScreen, 140, 100, saveFiles[slot-1].name, 12, 1, FULL_SHADE);
			{
				// Tyrian3D: the question for the modern UI.
				char text[160];
				snprintf(text, sizeof(text), "%s %s     %s %s", miscText[1], savename, miscText[69], saveFiles[slot - 1].name);
				shop_dialog_publish(miscText[68], text, NULL, NULL, false, save_selected ? 0 : 1);
			}

			col += colC;
			if (col > 8 || col < 2)
				colC = -colC;

			int temp_x, temp_c;

			temp_x = 54 + 45 - (JE_textWidth(miscText[9], FONT_SHAPES) / 2);
			temp_c = save_selected ? col - 12 : -5;

			JE_outTextAdjust(VGAScreen, temp_x, 128, miscText[9], 15, temp_c, FONT_SHAPES, true);

			temp_x = 149 + 45 - (JE_textWidth(miscText[10], FONT_SHAPES) / 2);
			temp_c = !save_selected ? col - 12 : -5;

			JE_outTextAdjust(VGAScreen, temp_x, 128, miscText[10], 15, temp_c, FONT_SHAPES, true);

			if (has_mouse)
			{
				JE_mouseStart();
				JE_showVGA();
				JE_mouseReplace();
			}
			else
			{
				JE_showVGA();
			}

			wait_delay();

			push_joysticks_as_keyboard();
			service_SDL_events(false);

		} while (!newkey && !mousedown);

		if (mousedown)
		{
			if (lastmouse_y > 123 && lastmouse_y < 149)
			{
				if (lastmouse_x > 56 && lastmouse_x < 142)
				{
					save_selected = true;
					done = true;
				}
				else if (lastmouse_x > 151 && lastmouse_x < 237)
				{
					save_selected = false;
					done = true;
				}
			}
			mousedown = false;
		}
		else if (newkey)
		{
			switch (lastkey_scan)
			{
				case SDL_SCANCODE_LEFT:
				case SDL_SCANCODE_RIGHT:
				case SDL_SCANCODE_TAB:
					save_selected = !save_selected;
					JE_playSampleNum(S_CURSOR);
					break;
				case SDL_SCANCODE_RETURN:
				case SDL_SCANCODE_SPACE:
					done = true;
					break;
				case SDL_SCANCODE_ESCAPE:
					save_selected = false;
					done = true;
					break;
				default:
					break;
			}
		}
	}

	JE_playSampleNum(save_selected ? S_SELECT : S_CLICK);
	return save_selected;
}

JE_boolean JE_quitRequest(void)
{
	bool quit_selected = true, done = false;

	JE_clearKeyboard();
	JE_wipeKey();
	wait_noinput(true, true, true);

	JE_barShade(VGAScreen, 65, 55, 255, 155);

	while (!done)
	{
		Uint8 col = 8;
		int colC = 1;

		do
		{
			service_SDL_events(true);
			setDelay(4);

			blit_sprite(VGAScreen, 50, 50, OPTION_SHAPES, 35);  // message box
			JE_textShade(VGAScreen, 70, 60, miscText[28], 0, 5, FULL_SHADE);
			JE_helpBox(VGAScreen, 70, 90, miscText[30], 30);

			col += colC;
			if (col > 8 || col < 2)
				colC = -colC;

			int temp_x, temp_c;

			temp_x = 54 + 45 - (JE_textWidth(miscText[9], FONT_SHAPES) / 2);
			temp_c = quit_selected ? col - 12 : -5;

			JE_outTextAdjust(VGAScreen, temp_x, 128, miscText[9], 15, temp_c, FONT_SHAPES, true);

			temp_x = 149 + 45 - (JE_textWidth(miscText[10], FONT_SHAPES) / 2);
			temp_c = !quit_selected ? col - 12 : -5;

			JE_outTextAdjust(VGAScreen, temp_x, 128, miscText[10], 15, temp_c, FONT_SHAPES, true);

			shop_dialog_publish(miscText[28], miscText[30], NULL, NULL, false, quit_selected ? 0 : 1);  // Tyrian3D

			if (has_mouse)
			{
				JE_mouseStart();
				JE_showVGA();
				JE_mouseReplace();
			}
			else
			{
				JE_showVGA();
			}

			wait_delay();

			push_joysticks_as_keyboard();
			service_SDL_events(false);

		} while (!newkey && !mousedown);

		if (mousedown)
		{
			if (lastmouse_y > 123 && lastmouse_y < 149)
			{
				if (lastmouse_x > 56 && lastmouse_x < 142)
				{
					quit_selected = true;
					done = true;
				}
				else if (lastmouse_x > 151 && lastmouse_x < 237)
				{
					quit_selected = false;
					done = true;
				}
			}
			mousedown = false;
		}
		else if (newkey)
		{
			switch (lastkey_scan)
			{
				case SDL_SCANCODE_LEFT:
				case SDL_SCANCODE_RIGHT:
				case SDL_SCANCODE_TAB:
					quit_selected = !quit_selected;
					JE_playSampleNum(S_CURSOR);
					break;
				case SDL_SCANCODE_RETURN:
				case SDL_SCANCODE_SPACE:
					done = true;
					break;
				case SDL_SCANCODE_ESCAPE:
					quit_selected = false;
					done = true;
					break;
				default:
					break;
			}
		}
	}

	JE_playSampleNum(quit_selected ? S_SPRING : S_CLICK);

#ifdef WITH_NETWORK
	if (isNetworkGame && quit_selected)
	{
		network_prepare(PACKET_QUIT);
		network_send(4);  // PACKET QUIT

		network_tyrian_halt(0, true);
	}
#endif

	return quit_selected;
}

void JE_genItemMenu(JE_byte itemNum)
{
	menuChoices[MENU_UPGRADE_SUB] = itemAvailMax[itemAvailMap[itemNum - 2] - 1] + 2;

	temp3 = 2;
	temp2 = *playeritem_map(&player[0].items, itemNum - 2);

	strcpy(menuInt[5][0], menuInt[2][itemNum - 1]);

	for (tempW = 0; tempW < itemAvailMax[itemAvailMap[itemNum - 2] - 1]; tempW++)
	{
		temp = itemAvail[itemAvailMap[itemNum - 2] - 1][tempW];
		switch (itemNum)
		{
		case 2:
			strcpy(tempStr, ships[temp].name);
			break;
		case 3:
		case 4:
			strcpy(tempStr, weaponPort[temp].name);
			break;
		case 5:
			strcpy(tempStr, shields[temp].name);
			break;
		case 6:
			strcpy(tempStr, powerSys[temp].name);
			break;
		case 7:
		case 8:
			strcpy(tempStr, options[temp].name);
			break;
		}
		if (temp == temp2)
		{
			temp3 = tempW + 2;
		}
		strcpy(menuInt[5][tempW], tempStr);
	}

	strcpy(menuInt[5][tempW], miscText[13]);

	curSel[MENU_UPGRADE_SUB] = temp3;
}

void JE_scaleInPicture(SDL_Surface *dst, const SDL_Surface *src)
{
	for (int i = 2; i <= 160; i += 2)
	{
		if (JE_anyButton())
			break;

		JE_scaleBitmap(dst, src, 160 - i, 0, 160 + i - 1, 100 + roundf(i * 0.625f) - 1);
		JE_showVGA();

		SDL_Delay(1);
	}
}

void JE_drawScore(void)
{
	char cl[24];
	if (curMenu == MENU_UPGRADE_SUB)
	{
		sprintf(cl, "%d", JE_cashLeft());
		JE_textShade(VGAScreen, 65, 173, cl, 1, 6, DARKEN);
	}
}

void JE_menuFunction(JE_byte select)
{
	JE_byte x;
	JE_word curSelect;

	col = 0;
	colC = -1;
	JE_playSampleNum(S_CLICK);

	curSelect = curSel[curMenu];

	switch (curMenu)
	{
	case MENU_FULL_GAME:
		switch (select)
		{
		case 2: //cubes
			curMenu = MENU_DATA_CUBES;
			curSel[MENU_DATA_CUBES] = 2;
			break;
		case 3: //shipspecs
			JE_doShipSpecs();
			break;
		case 4://upgradeship
			curMenu = MENU_UPGRADES;
			break;
		case 5: //options
			curMenu = MENU_OPTIONS;
			break;
		case 6: //nextlevel
			curMenu = MENU_PLAY_NEXT_LEVEL;
			newPal = 18;
			JE_computeDots();
			navX = planetX[mapOrigin - 1];
			navY = planetY[mapOrigin - 1];
			newNavX = navX;
			newNavY = navY;
			menuChoices[MENU_PLAY_NEXT_LEVEL] = mapPNum + 2;
			curSel[MENU_PLAY_NEXT_LEVEL] = 2;
			strcpy(menuInt[4][0], "Next Level");
			for (x = 0; x < mapPNum; x++)
			{
				temp = mapPlanet[x];
				strcpy(menuInt[4][x + 1], pName[temp - 1]);
			}
			strcpy(menuInt[4][x + 1], miscText[5]);
			break;
		case 7: //quit
			if (JE_quitRequest())
			{
				gameLoaded = true;
				mainLevel = 0;
			}
			break;
		}
		break;

	case MENU_UPGRADES:
		if (select == 9) //done
		{
			curMenu = MENU_FULL_GAME;
		}
		else // selected item to upgrade
		{
			old_items[0] = player[0].items;
			shop_cash_before = (long)player[0].cash;  // Tyrian3D: for the modern UI's credits

			weaponSimTime = 0;
			lastDirection = 1;
			JE_genItemMenu(select);
			JE_initWeaponView();
			curMenu = MENU_UPGRADE_SUB;
			lastCurSel = curSel[MENU_UPGRADE_SUB];
			player[0].cash = player[0].cash * 2 - JE_cashLeft();
		}
		break;

	case MENU_OPTIONS:
		switch (select)
		{
		case 2:
			curMenu = MENU_LOAD_SAVE;
			performSave = false;
			quikSave = false;
			break;
		case 3:
			curMenu = MENU_LOAD_SAVE;
			performSave = true;
			quikSave = false;
			break;
		case 6:
			curMenu = MENU_JOYSTICK_CONFIG;
			break;
		case 7:
			curMenu = MENU_KEYBOARD_CONFIG;
			break;
		case 8:
			curMenu = MENU_MOUSE_CONFIG;
			break;
		case 9:
			curMenu = MENU_FULL_GAME;
			break;
		}
		break;

	case MENU_PLAY_NEXT_LEVEL:
		if (select == menuChoices[MENU_PLAY_NEXT_LEVEL]) //exit
		{
			curMenu = MENU_FULL_GAME;
			newPal = 1;
		}
		else
		{
			mainLevel = mapSection[curSelect - 2];
			jumpSection = true;
		}
		break;

	case MENU_UPGRADE_SUB:
		if (curSel[MENU_UPGRADE_SUB] < menuChoices[MENU_UPGRADE_SUB])
		{
			// select done
			curSel[MENU_UPGRADE_SUB] = menuChoices[MENU_UPGRADE_SUB];
		}
		else // if done is selected
		{
			JE_playSampleNum(S_ITEM);

			player[0].cash = JE_cashLeft();
			curMenu = MENU_UPGRADES;
		}
		break;

	case MENU_KEYBOARD_CONFIG:
		if (curSelect == 10) /* reset to defaults */
		{
			memcpy(keySettings, defaultKeySettings, sizeof(keySettings));
		}
		else if (curSelect == 11) /* done */
		{
			curMenu = isNetworkGame
				? MENU_LIMITED_OPTIONS
				: MENU_OPTIONS;
		}
		else /* change key */
		{
			temp2 = 254;
			int tempY = 38 + (curSelect - 2) * 12;
			JE_textShade(VGAScreen, 236, tempY, SDL_GetScancodeName(keySettings[curSelect-2]), (temp2 / 16), (temp2 % 16) - 8, DARKEN);
			JE_showVGA();

			wait_noinput(true, true, true);

			col = 248;
			colC = 1;
			shop_capturing = curSelect;  // Tyrian3D: the modern UI shows the setting waiting

			do
			{
				setDelay(1);

				col += colC;
				if (col < 243 || col > 248)
				{
					colC *= -1;
				}
				JE_rectangle(VGAScreen, 230, tempY - 2, 300, tempY + 7, col);

				poll_joysticks();
				service_SDL_events(true);

				shop_publish();
				JE_showVGA();

				wait_delay();
			} while (!newkey && !mousedown && !joydown);
			shop_capturing = -1;
			
			if (newkey)
			{
				// already used? then swap
				for (uint i = 0; i < COUNTOF(keySettings); ++i)
				{
					if (keySettings[i] == lastkey_scan)
					{
						keySettings[i] = keySettings[curSelect-2];
						break;
					}
				}
				
				if (lastkey_scan != SDL_SCANCODE_ESCAPE && // reserved for menu
				    lastkey_scan != SDL_SCANCODE_F11 &&    // reserved for gamma
				    lastkey_scan != SDL_SCANCODE_P)        // reserved for pause
				{
					JE_playSampleNum(S_CLICK);
					keySettings[curSelect-2] = lastkey_scan;
					++curSelect;
				}
				
				JE_wipeKey();
			}
		}
		break;

	case MENU_LOAD_SAVE:
		if (curSelect == 13)
		{
			if (quikSave)
			{
				curMenu = oldMenu;
				newPal = oldPal;
			}
			else
			{
				curMenu = MENU_OPTIONS;
			}
		}
		else
		{
			if (twoPlayerMode)
				temp = 11;
			else
				temp = 0;
			JE_operation(curSelect - 1 + temp);
			if (quikSave)
			{
				curMenu = oldMenu;
				newPal = oldPal;
			}
		}
		break;

	case MENU_DATA_CUBES:
		if (curSelect == menuChoices[curMenu])
		{
			curMenu = MENU_FULL_GAME;
			newPal = 1;
		}
		else
		{
			if (cubeMax > 0)
			{
				firstMenu9 = true;
				curMenu = MENU_DATA_CUBE_SUB;
				yLoc = 0;
				yChg = 0;
				currentCube = curSel[MENU_DATA_CUBES] - 2;
			}
			else
			{
				curMenu = MENU_FULL_GAME;
				newPal = 1;
			}
		}
		break;

	case MENU_DATA_CUBE_SUB:
		curMenu = MENU_DATA_CUBES;
		break;

	case MENU_2_PLAYER_ARCADE:
		switch (curSel[curMenu])
		{
		case 2:
			mainLevel = mapSection[mapPNum-1];
			jumpSection = true;
			break;
		case 3:
		case 4:
			JE_playSampleNum(S_CURSOR);

			int temp = curSel[curMenu] - 3;
			do
			{
				if (joysticks == 0)
					inputDevice[temp == 0 ? 1 : 0] = inputDevice[temp]; // swap controllers
				if (inputDevice[temp] >= 2 + joysticks)
					inputDevice[temp] = 1;
				else
					inputDevice[temp]++;
			} while (inputDevice[temp] == inputDevice[temp == 0 ? 1 : 0]);
			break;
		case 5:
			curMenu = MENU_OPTIONS;
			break;
		case 6:
			if (JE_quitRequest())
			{
				gameLoaded = true;
				mainLevel = 0;
			}
			break;
		}
		break;

	case MENU_1_PLAYER_ARCADE:
		switch (curSel[curMenu])
		{
		case 2:
			mainLevel = mapSection[mapPNum-1];
			jumpSection = true;
			break;
		case 3:
			curMenu = isNetworkGame
				? MENU_LIMITED_OPTIONS
				: MENU_OPTIONS;
			break;
		case 4:
			if (JE_quitRequest())
			{
				gameLoaded = true;
				mainLevel = 0;
			}
			break;
		}
		break;

	case MENU_LIMITED_OPTIONS:
		switch (select)
		{
		case 2:
			curMenu = MENU_JOYSTICK_CONFIG;
			break;
		case 3:
			curMenu = MENU_KEYBOARD_CONFIG;
			break;
		case 6:
			curMenu = MENU_1_PLAYER_ARCADE;
			break;
		}
		break;

	case MENU_JOYSTICK_CONFIG:
		if (joysticks == 0 && select != 17)
			break;

		switch (select)
		{
		case 2:
			joystick_config++;
			joystick_config %= joysticks;
			break;
		case 3:
			joystick[joystick_config].analog = !joystick[joystick_config].analog;
			break;
		case 4:
			if (joystick[joystick_config].analog)
			{
				joystick[joystick_config].sensitivity++;
				joystick[joystick_config].sensitivity %= 11;
			}
			break;
		case 5:
			if (joystick[joystick_config].analog)
			{
				joystick[joystick_config].threshold++;
				joystick[joystick_config].threshold %= 11;
			}
			break;
		case 16:
			reset_joystick_assignments(joystick_config);
			break;
		case 17:
			curMenu = isNetworkGame
				? MENU_LIMITED_OPTIONS
				: MENU_OPTIONS;
			break;
		default:
			if (joysticks == 0)
				break;

			// int temp = 254;
			// JE_textShade(VGAScreen, 236, 38 + i * 8, value, temp / 16, temp % 16 - 8, DARKEN);

			JE_rectangle(VGAScreen, 235, 21 + select * 8, 310, 30 + select * 8, 248);

			Joystick_assignment temp;
			if (detect_joystick_assignment(joystick_config, &temp))
			{
				// if the detected assignment was already set, unset it
				for (uint i = 0; i < COUNTOF(*joystick->assignment); i++)
				{
					if (joystick_assignment_cmp(&temp, &joystick[joystick_config].assignment[select - 6][i]))
					{
						joystick[joystick_config].assignment[select - 6][i].type = NONE;
						goto joystick_assign_done;
					}
				}

				// if there is an empty assignment, set it
				for (uint i = 0; i < COUNTOF(*joystick->assignment); i++)
				{
					if (joystick[joystick_config].assignment[select - 6][i].type == NONE)
					{
						joystick[joystick_config].assignment[select - 6][i] = temp;
						goto joystick_assign_done;
					}
				}

				// if no assignments are empty, shift them all forward and set the last one
				for (uint i = 0; i < COUNTOF(*joystick->assignment); i++)
				{
					if (i == COUNTOF(*joystick->assignment) - 1)
						joystick[joystick_config].assignment[select - 6][i] = temp;
					else
						joystick[joystick_config].assignment[select - 6][i] = joystick[joystick_config].assignment[select - 6][i + 1];
				}

joystick_assign_done:
				curSelect++;

				poll_joysticks();
			}
		}
		break;

	case MENU_SUPER_TYRIAN:
		switch (curSel[curMenu])
		{
		case 2:
			mainLevel = mapSection[mapPNum-1];
			jumpSection = true;
			break;
		case 3:
			JE_doShipSpecs();
			break;
		case 4:
			curMenu = MENU_OPTIONS;
			break;
		case 5:
			if (JE_quitRequest())
			{
				if (isNetworkGame)
				{
					JE_tyrianHalt(0);
				}
				gameLoaded = true;
				mainLevel = 0;
			}
		}
		break;

	case MENU_MOUSE_CONFIG:
		switch(curSel[curMenu])
		{
			case 2:
			case 3:
			case 4:
				temp = curSel[curMenu] - 2;
				if (++mouseSettings[temp] > 5)
					mouseSettings[temp] = 1;
				break;
			case 5:
				memcpy(mouseSettings, defaultMouseSettings, sizeof(mouseSettings));
				break;
			case 6:
				curMenu = MENU_OPTIONS;
				break;
		}
	}

	old_items[0] = player[0].items;
}

void JE_drawShipSpecs(SDL_Surface * screen, SDL_Surface * temp_screen)
{
	/* In this function we create our ship description image.
	 *
	 * We use a temp screen for convenience.  Bad design maybe (Jason!),
	 * but it'll be okay (and the alternative is malloc/a large stack) */

	int temp_x = 0, temp_y = 0, temp_index;
	Uint8 *src, *dst;

	//first, draw the text and other assorted flavoring.
	JE_clr256(screen);
	JE_drawLines(screen, true);
	JE_drawLines(screen, false);
	JE_rectangle(screen, 0, 0, 319, 199, 37);
	JE_rectangle(screen, 1, 1, 318, 198, 35);

	verticalHeight = 9;
	JE_outText(screen, 10, 2, ships[player[0].items.ship].name, 12, 3);
	JE_helpBox(screen, 100, 20, shipInfo[player[0].items.ship-1][0], 40);
	JE_helpBox(screen, 100, 100, shipInfo[player[0].items.ship-1][1], 40);
	verticalHeight = 7;

	JE_outText(screen, JE_fontCenter(miscText[4], TINY_FONT), 190, miscText[4], 12, 2);

	//now draw the green ship over that.
	//This hardcoded stuff is for positioning our little ship graphic
	if (player[0].items.ship > 90)
	{
		temp_index = 32;
	}
	else if (player[0].items.ship > 0)
	{
		temp_index = ships[player[0].items.ship].bigshipgraphic;
	}
	else
	{
		temp_index = ships[old_items[0].ship].bigshipgraphic;
	}

	switch (temp_index)
	{
		case 32:
			temp_x = 35;
			temp_y = 33;
			break;
		case 28:
			temp_x = 31;
			temp_y = 36;
			break;
		case 33:
			temp_x = 31;
			temp_y = 35;
			break;
		case 45:
			temp_x = 36;
			temp_y = 33;
			break;
		case 46:
			temp_x = 30;
			temp_y = 30;
			break;
		default:
			assert(0);
	}
	temp_x -= 30;

	//draw the ship into our temp buffer.
	JE_clr256(temp_screen);
	blit_sprite(temp_screen, temp_x, temp_y, OPTION_SHAPES, temp_index - 1);  // ship illustration

	/* But wait!  Our ship is fully colored, not green!
	 * With a little work we could get the sprite dimensions and greenify
	 * the area it resides in.  For now, let's just greenify the (almost
	 * entirely) black screen.

	 * We can't work in place.  In fact we'll need to overlay the result
	 * To avoid our temp screen dependence this has been rewritten to
	 * only write one line at a time.*/
	dst = screen->pixels;
	src = temp_screen->pixels;
	for (int y = 0; y < screen->h; y++)
	{
		for (int x = 0; x < screen->pitch; x++)
		{
			int avg = 0;
			if (y > 0)
				avg += *(src - screen->pitch) & 0x0f;
			if (y < screen->h - 1)
				avg += *(src + screen->pitch) & 0x0f;
			if (x > 0)
				avg += *(src - 1) & 0x0f;
			if (x < screen->pitch - 1)
				avg += *(src + 1) & 0x0f;
			avg /= 4;

			if ((*src & 0x0f) > avg)
				*dst = (*src & 0x0f) | 0xc0;
			//else
			//	*dst = 0;

			src++;
			dst++;
		}
	}
}

void JE_weaponSimUpdate(void)
{
	char buf[32];

	JE_weaponViewFrame();

	++weaponSimTime;
	weaponSimTime %= 150;

	if (leftPower || rightPower)
	{
		if (!leftPower)
			blit_sprite(VGAScreenSeg, 24, 149, OPTION_SHAPES, 13);  // downgrade disabled
		if (!rightPower || !rightPowerAfford)
			blit_sprite(VGAScreenSeg, 119, 149, OPTION_SHAPES, 14);  // upgrade disabled

		temp = player[0].items.weapon[curSel[MENU_UPGRADES]-3].power;

		if ((curMenu == MENU_UPGRADE_SUB) && (curSel[MENU_UPGRADES] == 4)
			&& weaponPort[player[0].items.weapon[REAR_WEAPON].id].opnum == 2
			&& (weaponSimTime >= 75))
		{
			// [/] Rear Weapon Mode
			JE_outText(VGAScreen, 28, 137, miscText[70], 1, 4);
		}
		else
		{
			if (leftPower)
			{
				sprintf(buf, "%d", downgradeCost);
				JE_outText(VGAScreen, 26, 137, buf, 1, 4);
			}
			if (rightPower)
			{
				sprintf(buf, "%d", upgradeCost);
				JE_outText(VGAScreen, 108, 137, buf, (rightPowerAfford) ? 1 : 7, 4);
			}

			sprintf(buf, "%s %d", miscTextB[5], temp);
			JE_outText(VGAScreen, 58, 137, buf, 15, 4);
		}

		for (int x = 1; x <= temp; x++)
		{
			fill_rectangle_xy(VGAScreen, 39 + x * 6, 151, 39 + x * 6 + 4, 151, 251);
			JE_pix(VGAScreen, 39 + x * 6, 151, 252);
			fill_rectangle_xy(VGAScreen, 39 + x * 6, 152, 39 + x * 6 + 4, 164, 250);
			fill_rectangle_xy(VGAScreen, 39 + x * 6, 165, 39 + x * 6 + 4, 165, 249);
		}
	}
	else
		blit_sprite(VGAScreenSeg, 20, 146, OPTION_SHAPES, 17);  // hide power level interface

	if (!video_sim_ship(player[0].x + 7, player[0].y + 7))
		JE_drawItem(1, player[0].items.ship, player[0].x - 5, player[0].y - 7);
}

void JE_weaponViewFrame(void)
{
	fill_rectangle_xy(VGAScreen, 8, 8, 143, 182, 0);

	/* JE: (* Port Configuration Display *)
	(*    drawportconfigbuttons;*/

	update_and_draw_starfield(VGAScreen, 1);
	video_sim_begin();  // Tyrian3D: the 3D view draws the ship and shots as models

	mouseX = player[0].x;
	mouseY = player[0].y;

	// create shots in weapon simulator
	for (uint i = 0; i < 2; ++i)
	{
		if (shotRepeat[i] > 0)
		{
			--shotRepeat[i];
		}
		else
		{
			const uint item       = player[0].items.weapon[i].id,
			           item_power = player[0].items.weapon[i].power - 1,
			           item_mode = (i == REAR_WEAPON) ? player[0].weapon_mode - 1 : 0;

			b = player_shot_create(item, i, player[0].x, player[0].y, mouseX, mouseY, weaponPort[item].op[item_mode][item_power], 1);
		}
	}

	if (options[player[0].items.sidekick[LEFT_SIDEKICK]].wport > 0)
	{
		if (shotRepeat[SHOT_LEFT_SIDEKICK] > 0)
		{
			--shotRepeat[SHOT_LEFT_SIDEKICK];
		}
		else
		{
			const uint item = player[0].items.sidekick[LEFT_SIDEKICK];
			const int x = player[0].sidekick[LEFT_SIDEKICK].x,
			          y = player[0].sidekick[LEFT_SIDEKICK].y;

			b = player_shot_create(options[item].wport, SHOT_LEFT_SIDEKICK, x, y, mouseX, mouseY, options[item].wpnum, 1);
		}
	}

	if (options[player[0].items.sidekick[RIGHT_SIDEKICK]].tr == 2)
	{
		player[0].sidekick[RIGHT_SIDEKICK].x = player[0].x;
		player[0].sidekick[RIGHT_SIDEKICK].y = MAX(10, player[0].y - 20);
	}
	else
	{
		player[0].sidekick[RIGHT_SIDEKICK].x = 72 + 15;
		player[0].sidekick[RIGHT_SIDEKICK].y = 120;
	}

	if (options[player[0].items.sidekick[RIGHT_SIDEKICK]].wport > 0)
	{
		if (shotRepeat[SHOT_RIGHT_SIDEKICK] > 0)
		{
			--shotRepeat[SHOT_RIGHT_SIDEKICK];
		}
		else
		{
			const uint item = player[0].items.sidekick[RIGHT_SIDEKICK];
			const int x = player[0].sidekick[RIGHT_SIDEKICK].x,
			          y = player[0].sidekick[RIGHT_SIDEKICK].y;

			b = player_shot_create(options[item].wport, SHOT_RIGHT_SIDEKICK, x, y, mouseX, mouseY, options[item].wpnum, 1);
		}
	}

	simulate_player_shots();
	video_sim_shots_drawn();  // Tyrian3D

	blit_sprite(VGAScreenSeg, 0, 0, OPTION_SHAPES, 12); // upgrade interface

	// weapon mode indicator
	if (player[0].weapon_mode == 1)
	{
		blit_sprite(VGAScreenSeg, 3, 56, OPTION_SHAPES, 18);  // lit
		blit_sprite(VGAScreenSeg, 3, 64, OPTION_SHAPES, 19);  // unlit
	}
	else // == 2
	{
		blit_sprite(VGAScreenSeg, 3, 56, OPTION_SHAPES, 19);  // unlit
		blit_sprite(VGAScreenSeg, 3, 64, OPTION_SHAPES, 18);  // lit
	}

	/*========================Power Bar=========================*/

	power += powerAdd;
	if (power > 900)
		power = 900;

	temp = power / 10;

	for (temp = 147 - temp; temp <= 146; temp++)
	{
		temp2 = 113 + (146 - temp) / 9 + 2;
		temp3 = (temp + 1) % 6;
		if (temp3 == 1)
			temp2 += 3;
		else if (temp3 != 0)
			temp2 += 2;

		JE_pix(VGAScreen, 141, temp, temp2 - 3);
		JE_pix(VGAScreen, 142, temp, temp2 - 3);
		JE_pix(VGAScreen, 143, temp, temp2 - 2);
		JE_pix(VGAScreen, 144, temp, temp2 - 1);
		fill_rectangle_xy(VGAScreen, 145, temp, 149, temp, temp2);

		if (temp2 - 3 < 112)
			temp2++;
	}

	temp = 147 - (power / 10);
	temp2 = 113 + (146 - temp) / 9 + 4;

	JE_pix(VGAScreen, 141, temp - 1, temp2 - 1);
	JE_pix(VGAScreen, 142, temp - 1, temp2 - 1);
	JE_pix(VGAScreen, 143, temp - 1, temp2 - 1);
	JE_pix(VGAScreen, 144, temp - 1, temp2 - 1);

	fill_rectangle_xy(VGAScreen, 145, temp-1, 149, temp-1, temp2);

	lastPower = temp;

	//JE_waitFrameCount();  TODO: didn't do anything?
}
