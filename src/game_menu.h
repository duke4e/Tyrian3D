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
#ifndef GAME_MENU_H
#define GAME_MENU_H

#include "helptext.h"
#include "opentyr.h"
#include "player.h"

typedef JE_byte JE_MenuChoiceType[MENU_MAX];

JE_longint JE_cashLeft(void);
void JE_itemScreen(void);

void load_cubes(void);
bool load_cube(int cube_slot, int cube_index);

void JE_drawItem(JE_byte itemType, JE_word itemNum, JE_word x, JE_word y);
void JE_drawMenuHeader(void);
void JE_drawMenuChoices(void);
void JE_updateNavScreen(void);
void JE_drawNavLines(JE_boolean dark);
void JE_drawLines(SDL_Surface *surface, JE_boolean dark);
void JE_drawDots(void);
void JE_drawPlanet(JE_byte planetNum);
void draw_ship_illustration(void);

// The pieces of the store's illustration of the ship (draw_ship_illustration) for these items: the
// sprite (table and index, as blit_sprite takes them) and its top left on the screen, or false.
typedef enum { ILLUSTRATION_SHIP, ILLUSTRATION_GENERATOR, ILLUSTRATION_FRONT, ILLUSTRATION_REAR } IllustrationPart;
bool ship_illustration_piece(IllustrationPart part, const PlayerItems *items, unsigned int *table, int *sprite_id,
                             int *x, int *y);
// Tyrian3D: the store shows the shields' choices (the 3D view shows the shield round the ship's model), and the strength
// of the shield on the ship now (0-1, as the store's gauge shows it).
bool shop_shield_page(void);
float shop_shield_strength(void);
// Tyrian3D: an item's own 3D model (models.cfg index), as the store's ship pad and the levels show it, or -1: part as
// the store's upgrade menu numbers them (2 the ship, 3 and 4 the guns: their mounts on the illustration, 5 the shield:
// none, 6 the generator: its mount, 7 and 8 the sidekicks); a special weapon's: its power-up's. The modern UI draws
// its render as the item's icon (ui.h icon_model).
int shop_item_model(int part, int item);
int special_item_model(int id);
// TYR3D_RENDER_ICONS: the models every item's icon is rendered from, once each, and the palette ramp each takes (-1:
// its own colours); how many.
int shop_icon_models(int *models, int *ramps, int max);
void JE_scaleBitmap(SDL_Surface *dst, const SDL_Surface *src, int x1, int y1, int x2, int y2);
void JE_initWeaponView(void);
void JE_computeDots(void);
JE_integer JE_partWay(JE_integer start, JE_integer finish, JE_byte dots, JE_byte dist);
void JE_doShipSpecs(void);
void JE_drawMainMenuHelpText(void);
JE_boolean JE_saveRequest(JE_byte slot, const char *savename);
JE_boolean JE_quitRequest(void);
void JE_genItemMenu(JE_byte itemnum);
void JE_scaleInPicture(SDL_Surface *dst, const SDL_Surface *src);
void JE_drawScore(void);
void JE_menuFunction(JE_byte select);
void JE_drawShipSpecs(SDL_Surface *, SDL_Surface *);
void JE_weaponSimUpdate(void);
void JE_weaponViewFrame(void);

// Tyrian3D: a question over the store for the modern UI (ui.h), as it shows now: its title and text,
// a field being typed (NULL: none) with its caret, which answer is selected (0 yes, 1 no, -1 neither).
void shop_dialog_publish(const char *title, const char *text, const char *field_label, const char *field, bool caret,
                         int selected);

#endif // GAME_MENU_H
