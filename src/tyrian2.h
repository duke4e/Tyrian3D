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
#ifndef TYRIAN2_H
#define TYRIAN2_H

#include "opentyr.h"

#include "varz.h"
#include "helptext.h"

void intro_logos(void);

typedef struct
{
	Uint8 link_num;
	Uint8 armor;
	Uint8 color;
}
boss_bar_t;

extern boss_bar_t boss_bar[2];

extern char tempStr[31];
extern JE_byte itemAvail[10][10], itemAvailMax[10];  // (the 10th list, Tyrian3D: the specials, ITEM_LIST_SPECIAL)

void JE_createNewEventEnemy(JE_byte enemytypeofs, JE_word enemyoffset, Sint16 uniqueShapeTableI);

void JE_doNetwork(void);

uint JE_makeEnemy(struct JE_SingleEnemyType *enemy, Uint16 eDatI, Sint16 uniqueShapeTableI);

void JE_eventJump(JE_word jump);

void JE_whoa(void);

Sint16 JE_newEnemy(int enemyOffset, Uint16 eDatI, Sint16 uniqueShapeTableI);
void JE_drawEnemy(int enemyOffset);
void JE_starShowVGA(void);

void JE_main(void);
void JE_loadMap(void);
// Tyrian3D: the data cube the store after this level shows as its n-th (1-based: the n-th found since the last store),
// by its list (the "]?" command) in the episode's sections from the next level's (nextLevel) on, up to the next level
// they load; 0 if there is none.
int upcoming_cube(int n);
#ifdef WITH_NETWORK
void networkStartScreen(void);
#endif
bool titleScreen(void);
bool newGame(void);
bool newSuperArcadeGame(unsigned int i);
bool newSuperTyrianGame(void);
void JE_readTextSync(void);
void JE_displayText(void);

bool JE_searchFor(JE_byte PLType, JE_byte* out_index);
bool gbc_piece_link(int link);
bool gbc_takes_along(int link, unsigned int dying, unsigned int other);
int gbc_pool_hit(unsigned int i, int damage);
bool gbc_pool_takes(unsigned int dying, unsigned int other);
void JE_eventSystem(void);

void draw_boss_bar(void);

#endif /* TYRIAN2_H */
