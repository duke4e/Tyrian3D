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
#ifndef MAININT_H
#define MAININT_H

#include "config.h"
#include "opentyr.h"
#include "palette.h"
#include "player.h"
#include "sprite.h"

extern bool button[4]; // fire, left fire, right fire, mode swap

extern JE_shortint constantLastX;
extern JE_word textErase;
extern char text_window_message[128];
extern JE_word upgradeCost;
extern JE_word downgradeCost;
extern JE_boolean performSave;
extern JE_boolean jumpSection;
extern JE_boolean useLastBank;

extern bool pause_pressed, ingamemenu_pressed;

/*void JE_textMenuWait(JE_word waittime, JE_boolean dogamma);*/

void JE_drawTextWindow(const char *text);
void JE_initPlayerData(void);
void JE_highScoreScreen(void);
void JE_gammaCorrect_func(JE_byte *col, JE_real r);
void JE_gammaCorrect(Palette *colorBuffer, JE_byte gamma);
JE_boolean JE_gammaCheck(void);
/* void JE_textMenuWait(JE_word *waitTime, JE_boolean doGamma); /!\ In setup.h */
void JE_nextEpisode(void);
void JE_helpSystem(JE_byte startTopic);
void JE_doInGameSetup(void);
JE_boolean JE_inGameSetup(void);
void JE_inGameHelp(void);
void JE_sortHighScores(void);
void JE_highScoreCheck(void);
void adjust_difficulty(void);

bool load_next_demo(void);
bool replay_demo_keys(void);

void JE_SFCodes(JE_byte playerNum_, JE_integer PX_, JE_integer PY_, JE_integer mouseX_, JE_integer mouseY_);
void JE_sort(void);

long weapon_upgrade_cost(long base_cost, unsigned int power);
ulong JE_getCost(JE_byte itemType, JE_word itemNum);
JE_longint JE_getValue(JE_byte itemType, JE_word itemNum);
ulong JE_totalScore(const Player *);

void JE_drawPortConfigButtons(void);
void JE_outCharGlow(JE_word x, JE_word y, const char *s);

// Tyrian3D: a story text between levels (JE_displayText's levelWarningText) for the modern UI (ui.h):
// story_begin before it is drawn (its picture is the screen as it is then: kind UIStoryKind, the
// ending's first lines its scores), story_line as each line (all: levelWarningLines) is revealed,
// story_end once it waits no more (it shows until the screen changes or the next screen).
void story_begin(int kind, int score_lines);
void story_line(int line);
void story_end(void);
// The screen changed under the story (the warning's bars): published again as it shows now.
void story_refresh(void);
// A title card (ui.h UICard) for the modern UI, over the screen as it is now: crumb, title, lines
// (NULL-ended), a code word, a sprite of the game (2x2) or NULL, whether it waits for a key.
void card_publish(const char *crumb, const char *title, const char *const *lines, const char *code, const void *icon_sheet,
                  int icon_sprite, bool prompt, bool large);

void JE_playCredits(void);
void JE_endLevelAni(void);
void JE_drawCube(SDL_Surface * screen, JE_word x, JE_word y, JE_byte filter, JE_byte brightness);
void JE_handleChat(void);
bool str_pop_int(char *str, int *val);
bool JE_loadScreen(void);
void JE_operation(JE_byte slot);
void JE_inGameDisplays(void);
void JE_mainKeyboardInput(void);
void JE_pauseGame(void);

void JE_playerMovement(Player *this_player, JE_byte inputDevice, JE_byte playerNum, JE_word shipGr, Sprite2_array *shipGrPtr_, JE_word *mouseX, JE_word *mouseY);
// Tyrian3D: how far the mouse has moved the ship it moves directly since the last tick (game
// pixels, within the ship's bounds), for the frames shown between ticks.
void player_pointer_lead(float lead[2]);
// Tyrian3D: twin-stick (player.h): the pointer aims the turret now, so the 3D view draws its aim lines
// through it (render_gpu.c).
bool twin_stick_aim_lines(void);
void JE_mainGamePlayerFunctions(void);
const char *JE_getName(JE_byte pnum);

void JE_playerCollide(Player *this_player, JE_byte playerNum);

#endif /* MAININT_H */
