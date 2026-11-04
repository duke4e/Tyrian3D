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
#include "tyrian2.h"
#include "opentyrian_version.h"

#include "debugmode.h"
#include "destruct.h"

#include "animlib.h"
#include "backgrnd.h"
#include "background3d.h"
#include "devtools.h"
#include "layer3d.h"
#include "settings3d.h"
#include "particles3d.h"
#include "models3d.h"
#include "rogue.h"
#include "secrets.h"
#include "volume3d.h"
#include "episodes.h"
#include "file.h"
#include "font.h"
#include "fonthand.h"
#include "game_menu.h"
#include "joystick.h"
#include "keyboard.h"
#include "lds_play.h"
#include "loudness.h"
#include "paths3d.h"
#include "lvllib.h"
#include "menus.h"
#include "mainint.h"
#include "mouse.h"
#include "mtrand.h"
#include "network.h"
#include "nortsong.h"
#include "nortvars.h"
#include "opentyr.h"
#include "params.h"
#include "pcxload.h"
#include "pcxmast.h"
#include "picload.h"
#include "render_gpu.h"
#include "shots.h"
#include "sprite.h"
#include "ui.h"
#include "vga256d.h"
#include "video.h"
#include "voiceover.h"

#include <assert.h>
#include <ctype.h>
#include <math.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

inline static void blit_enemy(SDL_Surface *surface, unsigned int i, signed int x_offset, signed int y_offset, signed int sprite_offset);

boss_bar_t boss_bar[2];

/* Level Event Data */
JE_boolean quit, loadLevelOk;

struct JE_EventRecType eventRec[EVENT_MAXIMUM]; /* [1..eventMaximum] */
JE_word levelEnemyMax;
JE_word levelEnemyFrequency;
JE_word levelEnemy[40]; /* [1..40] */

char tempStr[31];

/* Data used for ItemScreen procedure to indicate items available */
JE_byte itemAvail[10][10]; /* [1..10, 1..10] (Tyrian3D: the 10th the specials) */
JE_byte itemAvailMax[10]; /* [1..10] */

// Tyrian3D: the last frame was shown in 3D without waiting; the next tick waits first.
static bool wait_at_tick_start = false;

void JE_starShowVGA(void)
{
	JE_byte *src;
	Uint8 *s = NULL; /* screen pointer, 8-bit specific */

	int x, y, lightx, lighty, lightdist;

	if (!playerEndLevel && !skipStarShowVGA)
	{

		s = VGAScreenSeg->pixels;

		// Tyrian3D: on the wide playfield the 2D view shows the 264 pixels round the ship.
		l3d_view_x = l3d_field_wide ? SDL_clamp(player[0].x + 7 - L3D_PLAYFIELD_W / 2, 0, L3D_WIDTH - L3D_PLAYFIELD_W)
		                            : L3D_PLAYFIELD_X;
		src = game_screen->pixels;
		src += l3d_view_x;

		// Tyrian3D: a frame for the 3D view shows at once; the game waits for its next tick at the
		// start of the tick instead (video_wait_tick_3d), so input shows a tick sooner.
		const bool frame_3d = l3d_take_frame();
		if (smoothScroll != 0 /*&& thisPlayerNum != 2*/ && !frame_3d)
		{
			wait_delay();
			setTickDelay(frameCountMax);
		}

		if (starShowVGASpecialCode == 1)
		{
			src += game_screen->pitch * 183;
			for (y = 0; y < 184; y++)
			{
				memmove(s, src, 264);
				s += VGAScreenSeg->pitch;
				src -= game_screen->pitch;
			}
		}
		else if (starShowVGASpecialCode == 2 && processorType >= 2)
		{
			lighty = 172 - player[0].y;
			lightx = 257 + l3d_view_x - player[0].x;

			for (y = 184; y; y--)
			{
				if (lighty > y)
				{
					for (x = 320 - 56; x; x--)
					{
						*s = (*src & 0xf0) | ((*src >> 2) & 0x03);
						s++;
						src++;
					}
				}
				else
				{
					for (x = 320 - 56; x; x--)
					{
						lightdist = abs(lightx - x) + lighty;
						if (lightdist < y)
							*s = *src;
						else if (lightdist - y <= 5)
							*s = (*src & 0xf0) | (((*src & 0x0f) + (3 * (5 - (lightdist - y)))) / 4);
						else
							*s = (*src & 0xf0) | ((*src & 0x0f) >> 2);
						s++;
						src++;
					}
				}
				s += 56 + VGAScreenSeg->pitch - 320;
				src += 56 + VGAScreenSeg->pitch - 320;
			}
		}
		else
		{
			for (y = 0; y < 184; y++)
			{
				memmove(s, src, 264);
				s += VGAScreenSeg->pitch;
				src += game_screen->pitch;
			}
		}
		if (frame_3d)
		{
			dev_on_layers_captured();
			JE_showVGA3D();
			if (smoothScroll != 0)
				wait_at_tick_start = true;
		}
		else
		{
			JE_showVGA();
		}
	}

	quitRequested = false;
	skipStarShowVGA = false;
}

inline static void blit_enemy(SDL_Surface *surface, unsigned int i, signed int x_offset, signed int y_offset, signed int sprite_offset)
{
	if (enemy[i].sprite2s == NULL)
	{
		fprintf(stderr, "warning: enemy %d sprite missing\n", i);
		return;
	}
	
	const int x = enemy[i].ex + x_offset + tempMapXOfs,
	          y = enemy[i].ey + y_offset;
	const unsigned int index = enemy[i].egr[enemy[i].enemycycle - 1] + sprite_offset;

	if (enemy[i].filter != 0)
		blit_sprite2_filter(surface, x, y, *enemy[i].sprite2s, index, enemy[i].filter);
	else
		blit_sprite2(surface, x, y, *enemy[i].sprite2s, index);
}

static char enemy_sheet_letter(const Sprite2_array *sprite2s)
{
	if (sprite2s == &spriteSheet11)
		return M3D_SHEET_COINS;
	if (sprite2s == &spriteSheet10)
		return M3D_SHEET_POWERUPS;
	for (size_t k = 0; k < COUNTOF(enemySpriteSheetIds); ++k)
		if (sprite2s == &enemySpriteSheets[k] && enemySpriteSheetIds[k] > 0 && enemySpriteSheetIds[k] <= COUNTOF(shapeFile))
			return shapeFile[enemySpriteSheetIds[k] - 1];
	return 0;
}

// Keys for the motion of enemies' 3D objects (l3d_key_last_object), by slot.
#define ENEMY_MOTION_KEY(slot) (L3D_KEY_ENEMY + (Uint32)(slot))

// Tyrian3D: the object each enemy is a piece of, for the 3D view (L3DObject.group: the pieces of one
// object stand at one height on raised ground). The level's events make an object's pieces at one time
// (a large enemy's parts, an ore tug and its load: they need not share a link), or row by row as the map
// scrolls, with one link (CAMANIS's boss): an enemy an event makes is tagged with the event's time (+ 1)
// and the link it was made with; what takes an enemy's place (its damaged look, event 59) keeps its
// tags; the others (launched, random) have none (0). Only the 3D view reads them.
static Uint32 enemy_group[100];
static Uint8 enemy_group_link[100];

// Tyrian3D: episode 7's enemies, which GBC enemy each is a piece of (a composite's parts, the events right after
// an event 201 that names how many; an event 12's four): a GBC group is one link, and the PC kills a link's
// enemies together, but the GBC's die alone (gbc_takes_along). 0: none.
static Uint32 gbc_object[100];
static Uint32 gbc_objects = 0;
static int gbc_object_head = -1, gbc_object_event = -1;

// Tyrian3D: episode 7's bosses in the 3D view (tools/gbc/boss.py wholes): a group of a GBC boss's pieces draws the PC
// boss's whole body, each part by the piece nearest it, from the events 202 right before the piece's (its sprite,
// sheet letter and size, d2 d5 from the piece's centre; d4 the group's look). A piece of the group with none draws
// nothing while one of its others with parts is there, its own look once none is. Only the 3D view's.
#define GBC_LOOK_PARTS 8
#define GBC_LOOK_KEY(slot, part) (L3D_KEY_ENEMY + 0x100u * ((Uint32)(part) + 1) + (Uint32)(slot))
#define GBC_COMING_LOOK_KEY(event) (COMING_KEY + (Uint32)(event) * 16)  // (as draw_coming_enemies' keys: an event 202's)
typedef struct
{
	Uint16 sprite;
	char sheet;
	bool large;
	Sint16 dx, dy;
	Uint32 forecast;  // (the coming part it takes the place of, till first drawn)
} GbcLookPart;
static GbcLookPart gbc_look[100][GBC_LOOK_PARTS];
static Uint8 gbc_look_parts[100];
static Uint8 gbc_look_id[100];  // (0: none)

// The forecast (draw_coming_enemies' key) an event's enemy takes the place of, by slot, till it is
// first drawn: it fades in on from there (l3d_key_continue). Only the 3D view's.
static Uint32 enemy_forecast[100];

static int bit_count(Uint32 bits)
{
	int n = 0;
	for (; bits != 0; bits &= bits - 1)
		++n;
	return n;
}

// Tyrian3D: the sides (V3D_OPEN_*) on which another part of the same large enemy continues this
// one's sprite: an enemy of the same size right beside it, in the same group of slots (as the
// game makes the parts of large enemies and bosses), whose sprite meets this one's along most of
// the shared edge. The volumetric sprites then join there without a seam.
static Uint8 enemy_open_sides(unsigned int i)
{
	const bool large = enemy[i].size == 1;
	const int w = large ? 24 : 12, h = large ? 28 : 14;
	Uint32 mine[4];
	v3d_sprite_edges(enemy[i].sprite2s, enemy[i].egr[SDL_max(enemy[i].enemycycle, 1) - 1], large, mine);
	Uint8 open = 0;
	const unsigned int group = i / 25 * 25;
	for (unsigned int j = group; j < group + 25; ++j)
	{
		if (j == i || enemyAvail[j] == 1 || enemy[j].size != enemy[i].size || enemy[j].sprite2s == NULL)
			continue;
		// Parts not yet moved this frame may be a step behind.
		const int dx = enemy[j].ex - enemy[i].ex, dy = enemy[j].ey - enemy[i].ey, tolerance = 3;
		int side;  // where the other part is: 0 above, 1 right, 2 below, 3 left
		if (abs(dy) <= tolerance && abs(dx - w) <= tolerance)
			side = 1;
		else if (abs(dy) <= tolerance && abs(dx + w) <= tolerance)
			side = 3;
		else if (abs(dx) <= tolerance && abs(dy - h) <= tolerance)
			side = 2;
		else if (abs(dx) <= tolerance && abs(dy + h) <= tolerance)
			side = 0;
		else
			continue;
		Uint32 theirs[4];
		v3d_sprite_edges(enemy[j].sprite2s, enemy[j].egr[SDL_max(enemy[j].enemycycle, 1) - 1], large, theirs);
		const int edge = bit_count(mine[side]);
		const int shared = bit_count(mine[side] & theirs[(side + 2) % 4]);
		if (edge >= 3 && shared * 5 >= edge * 4)
			open |= (Uint8)(1u << side);
	}
	return open;
}

// Tyrian3D dev (TYR3D_LOG_GROUND): where ground enemies are on the backgrounds' maps, for keeping
// the terrain under them at the ground's height and solids clear of them
// (tools/terrain/make_terrain.py). Prints "ground: <map> <x> <y> <size> <slot> <sheet> <sprite> <screen
// x> <screen y> <frame> <group> <link>" in the exported map's pixels, when an enemy has moved (so an
// enemy standing on the map shows once, one moving over it every few pixels); sheet (its letter's code)
// and the first sprite of its animation name its look (the renderer's "groundmodel:" lines say what its
// model covers), the screen position where it is on the screen (game pixels: the 3D view's ground under
// it depends on it), the 3D frame when, and group and link which object it is a piece of
// (enemy_group, L3DObject.group). The top enemies (drawn after background 3, carried by it) as "riding:"
// lines with the same fields, on background 3's map only (tools/terrain/make_cleanground.py's upper maps).
static struct
{
	float x, y;
	int size;
	unsigned int slot;
	char sheet;
	unsigned int sprite;
	Uint32 group;
	Uint8 link;
	bool riding;
} ground_logged[COUNTOF(enemy) * 2];
static int ground_logged_count = 0;

static void log_ground_enemy(unsigned int i, char sheet, unsigned int first_sprite, int look_layer)
{
	// (on the ground as shown: a model put on another layer than the game's, models.cfg layer=, is there)
	const L3DLayerType layer = look_layer > 0 ? (L3DLayerType)(look_layer - 1) : l3d_current_layer();
	const bool riding = l3d_current_layer() == L3D_TOP_ENEMY;
	if ((layer != L3D_GROUND_ENEMY && !riding) || enemy[i].ey <= -26 || enemy[i].ey >= 190 ||
	    ground_logged_count == (int)COUNTOF(ground_logged))
		return;
	ground_logged[ground_logged_count++] = (typeof(ground_logged[0])){
		enemy[i].ex + tempMapXOfs + 6, enemy[i].ey + 7, enemy[i].size == 1 ? 24 : 12, i, sheet, first_sprite,
		enemy_group[i], enemy_group_link[i], riding };
}

// At the frame's end, when all its backgrounds are drawn: where the frame's ground enemies were on
// each background's map (backgrounds 2 and 3 solids keep clear of them too).
static void flush_ground_log(void)
{
	static int last_x[B3D_SETS][COUNTOF(enemy)], last_y[B3D_SETS][COUNTOF(enemy)];
	static Uint64 hashes[B3D_SETS];
	static unsigned int generation = 0;
	if (generation != b3d_map_generation + 1)
	{
		generation = b3d_map_generation + 1;
		for (int set = 1; set <= B3D_SETS; ++set)
			hashes[set - 1] = b3d_map_hash(set);
		SDL_memset(last_x, 0, sizeof(last_x));
	}
	for (int e = 0; e < ground_logged_count; ++e)
		for (int b = 0; b < l3d_frame.background_count; ++b)
		{
			const L3DBackground *background = &l3d_frame.backgrounds[b];
			const int set = background->set;
			const unsigned int i = ground_logged[e].slot;
			int map_x, map_y;
			if (set < 1 || set > B3D_SETS || (ground_logged[e].riding && set != 3) ||
			    !b3d_map_point(background, ground_logged[e].x, ground_logged[e].y, &map_x, &map_y))
				continue;
			if (abs(map_x - last_x[set - 1][i]) < 4 && abs(map_y - last_y[set - 1][i]) < 4)
				continue;
			last_x[set - 1][i] = map_x;
			last_y[set - 1][i] = map_y;
			printf("%s: %016llx %d %d %d %u %u %u %d %d %u %u %u\n", ground_logged[e].riding ? "riding" : "ground",
			       (unsigned long long)hashes[set - 1], map_x, map_y,
			       ground_logged[e].size, i, (unsigned int)(Uint8)ground_logged[e].sheet, ground_logged[e].sprite,
			       (int)ground_logged[e].x, (int)ground_logged[e].y, l3d_frame_number, (unsigned int)ground_logged[e].group,
			       (unsigned int)ground_logged[e].link);
		}
	ground_logged_count = 0;
}

// Tyrian3D: how far the enemy in slot i, just drawn, is shown as it fades in (l3d_key_shown): one
// the game makes in sight fades in rather than popping up; one taking the place of its forecast
// fades in on from where that got to (shown fully if it came into sight).
static float enemy_shown(unsigned int i)
{
	if (enemy_forecast[i] != 0)
	{
		l3d_key_continue(ENEMY_MOTION_KEY(i), enemy_forecast[i]);
		enemy_forecast[i] = 0;
	}
	const float shown = l3d_key_shown(ENEMY_MOTION_KEY(i));
	if (shown * (L3D_APPEAR_FRAMES + 1) < 1.5f && SDL_getenv("TYR3D_LOG_SPAWNS") != NULL)
		printf("appear: %s slot %u enemy %u sprite %u at %d,%d (3D frame %u)\n", levelName, i, enemy[i].enemytype, enemy[i].egr[0],
		       enemy[i].ex + tempMapXOfs, enemy[i].ey, l3d_frame_number);
	return shown;
}

// Tyrian3D: an enemy in its damaged look smokes, thick at first, thinning out over SMOULDER_FRAMES (it only
// shows; with Effects).
#define SMOULDER_FRAMES 420.0f

static void smoulder(unsigned int i, float x, float y, bool large)
{
	static bool was_damaged[100];
	static Uint32 damaged_at[100];
	const bool damaged = enemy[i].edamaged != (enemy[i].edani < 0) && !enemy[i].scoreitem;
	if (damaged && !was_damaged[i])
		damaged_at[i] = l3d_frame_number;
	was_damaged[i] = damaged;
	const float since = (float)(l3d_frame_number - damaged_at[i]);
	if (!damaged || !settings3d.effects || since > SMOULDER_FRAMES)
		return;
	const L3DLayerType layer = l3d_current_layer();
	const bool ground = layer == L3D_GROUND_ENEMY || layer == L3D_BG2_LOW || layer == L3D_GROUND;
	// (In the sky it flies on, its smoke a trail behind it: thinner, or damaged jets and saucers drew thick grey
	// worms across the screen.)
	const float scale = (large ? 1.6f : 1.0f) * (ground ? 1.0f : 0.65f), strength = (1 - since / SMOULDER_FRAMES) * (ground ? 1.0f : 0.6f);
	p3d_smoulder(x, y, ground ? 3.0f : l3d_layer_height(layer) - l3d_terrain_headroom, scale, strength);
}

// Tyrian3D: the GBC bosses' pieces (episode 7, tools/gbc/boss.py) are on links of their own: one shot down or rammed
// goes alone (and no other turns damaged with it), as the GBC's pieces do, each with its own hit points; their link
// still moves them all, and the level's end waits for it to be empty.
bool gbc_piece_link(int link)
{
	return episodeNum == EPISODE_GBC && link >= 101 && link <= 120;
}

// Tyrian3D: whether the enemy dying (its link) takes another of the link along: in episode 7 only the pieces of one
// GBC enemy (gbc_object), never a boss's pieces (gbc_piece_link) nor the others of its group.
bool gbc_takes_along(int link, unsigned int dying, unsigned int other)
{
	if (episodeNum != EPISODE_GBC)
		return true;
	return !gbc_piece_link(link) && gbc_object[dying] != 0 && gbc_object[other] == gbc_object[dying];
}

// Tyrian3D: a GBC boss's pieces (gbc_piece_link) are one body, as a PC boss is (the user, 2026-10-29: each piece had
// a whole PC boss's hit points, and every one had to go): the GBC hit points of those that can be shot go into one pool
// as they are made, the pool their sum over the root of their number (TYRIAN's nine of 50-100, 780: 260), every hit on
// a piece (shot or rammed) is taken off it, and when it is gone all the pieces die together, the unshootable ones too.
// They still move as the GBC moves them. The boss bar shows it. A piece made while none of the last body's lives
// starts a new one.
static struct { int sum, count, taken; } gbc_pool;
static bool gbc_pooled[100];  // pieces of the body (cleared as any enemy is made: gbc_pool_forget)

static void gbc_pool_forget(const struct JE_SingleEnemyType *e)
{
	gbc_pooled[e - enemy] = false;
}

static bool gbc_in_pool(unsigned int i)
{
	return episodeNum == EPISODE_GBC && gbc_pooled[i] && enemyAvail[i] != 1;
}

static int gbc_pool_full(void)
{
	return gbc_pool.count > 0 ? (int)(gbc_pool.sum / sqrtf((float)gbc_pool.count) + 0.5f) : 0;
}

// What the body has left (0: gone).
static int gbc_pool_left(void)
{
	return SDL_max(0, gbc_pool_full() - gbc_pool.taken);
}

static void gbc_pool_join(unsigned int i)
{
	if (!gbc_piece_link(enemy[i].linknum))
		return;
	bool live = false;
	for (unsigned int j = 0; j < COUNTOF(enemy); ++j)
		live = live || (j != i && gbc_in_pool(j));
	if (!live)
		gbc_pool.sum = gbc_pool.count = gbc_pool.taken = 0;
	gbc_pooled[i] = true;
	if (enemy[i].armorleft < 255 && enemyDat[enemy[i].enemytype].armor != 0)
	{
		gbc_pool.sum += enemy[i].armorleft;
		++gbc_pool.count;
		enemy[i].armorleft = 254;  // (its own never runs out: the body's does)
	}
	if (!live && boss_bar[0].link_num == 0 && boss_bar[1].link_num == 0)
		boss_bar[0].link_num = enemy[i].linknum;
}

// A hit of `damage` on enemy i (shot or rammed): -1 if it isn't a piece of a body, else what the body has left after it.
int gbc_pool_hit(unsigned int i, int damage)
{
	if (!gbc_in_pool(i) || enemy[i].armorleft >= 255)
		return -1;
	gbc_pool.taken += damage;
	return gbc_pool_left();
}

// Whether enemy other dies with dying: both pieces of a body that is gone.
bool gbc_pool_takes(unsigned int dying, unsigned int other)
{
	return episodeNum == EPISODE_GBC && gbc_pooled[dying] && gbc_pooled[other] && enemyAvail[other] != 1 &&
	       gbc_pool_left() == 0;
}

// Tyrian3D: episode 7's levels play the GBC's songs (tools/gbc/music.py; build.py writes music.txt: a line a level by
// its number in the level file, its song and the sample its loop starts at, its boss song and its loop's, - for none):
// its own from the start, its boss's from event 204. False where it has none (the PC song plays).
#define GBC_SONG 204
static bool gbc_song_plays = false;  // (one of them plays: it loops on its own; a boss without one keeps the level's)
static bool gbc_music(bool boss)
{
	if (!boss)
		gbc_song_plays = false;
	if (episodeNum != EPISODE_GBC)
		return false;
	char dir[1024], path[1200], song[2][64];
	tyr3d_resource_dir("TYR3D_CONTENT_DIR", TYR3D_CONTENT_DIR, "content", dir, sizeof(dir));
	snprintf(path, sizeof(path), "%s/episode7/music.txt", dir);
	FILE *f = fopen(path, "r");
	if (f == NULL)
		return false;
	int level;
	unsigned long loop[2];
	bool found = false;
	while (!found && fscanf(f, "%d %63s %lu %63s %lu", &level, song[0], &loop[0], song[1], &loop[1]) == 5)
		found = level == lvlFileNum;
	fclose(f);
	if (!found || strcmp(song[boss], "-") == 0)
		return false;
	snprintf(path, sizeof(path), "%s/episode7/music/%s", dir, song[boss]);
	printf("music: %s%s\n", song[boss], boss ? " (boss)" : "");
	const bool plays = play_recorded_song(path, loop[boss]);  // (one that can't be read: the one before plays on)
	gbc_song_plays |= plays;
	return plays;
}

// Tyrian3D: episode 7's ticks this many times as long as the others'. The GBC's own pace (8/3 of a GBC frame at 59.73
// a second, 44.65 ms, over the PC's Normal 28.75: JE_main) was 1.553, which played too slow beside the PC episodes
// (the user, 2026-10-29); 1.25 (35.9 ms) is about halfway, still calmer than the PC's.
#define GBC_PACE 1.25f

// Tyrian3D: the GBC game's enemy table holds 17 (at $c192), and an enemy launched with it full doesn't come: in
// episode 7 a launch waits for fewer than that alive (WARP's boss launches every few frames; on the GBC eight of its
// orbs fly at once, here they filled the screen).
#define GBC_ENEMY_MAX 17
static bool gbc_enemies_full(void)
{
	if (episodeNum != EPISODE_GBC)
		return false;
	int alive = 0;
	for (int i = 0; i < 100; i++)
		alive += enemyAvail[i] == 0;
	return alive >= GBC_ENEMY_MAX;
}

// Tyrian3D: and its enemy shots' table holds 10 (at $c37f): a GBC boss's piece fires only while fewer fly (OASIS's
// tank fires a shot a frame in its bursts, which the GBC's table holds to a few at once).
#define GBC_SHOT_MAX 10
static bool gbc_shots_full(void)
{
	int flying = 0;
	for (int i = 0; i < ENEMY_SHOT_MAX; i++)
		flying += enemyShotAvail[i] == 0;
	return flying >= GBC_SHOT_MAX;
}

// Tyrian3D dev: the enemy that fired each enemy shot (TYR3D_LOG_BALANCE's hits)
static JE_word shot_from[ENEMY_SHOT_MAX];

// Tyrian3D: episode 7's enemies as tough as the GBC's and firing as often (event 203, right before the event that
// makes one, its event 201 for an object of several, or its look's events 202 for a boss's piece; head: that event).
// The PC enemies they are drawn as are often far tougher (a big ship for a small GBC one, a wall that can't be shot
// for one that can) and fire far more (a stream a tick for one that never fires): the user found Easy hard. d1: the
// GBC enemy's hit points (Normal; 0 the PC enemy's own armour), on the GBC's difficulty scale (Easy half, Hard 1.5x:
// the ROM's), shared among an object's PC parts by their armour (parts that can't be shot keep theirs, unless none
// can); d3: how often its guns fire (ticks; 0 never, -1 the PC enemy's own).
#define GBC_FIGHT 203
static int gbc_shootable(int type)
{
	const int armor = type > 0 && type <= ENEMY_NUM ? enemyDat[type].armor : 0;
	return armor > 0 && armor < 254 ? armor : 0;
}

// (one gun, as a GBC enemy has, every pace ticks (0: none): the first of its PC guns that fires by itself, or its
// first; the magnets and launchers of 251 up as they are)
static void gbc_fire(struct JE_SingleEnemyType *en, int pace)
{
	int gun = -1;
	for (int j = 0; j < 3; ++j)
		if (en->tur[j] > 0 && en->tur[j] < 251 && (gun < 0 || (en->freq[gun] == 0 && en->freq[j] > 0)))
			gun = j;
	for (int j = 0; j < 3; ++j)
		if (en->tur[j] < 251)
			en->freq[j] = j == gun ? pace : 0;
}

static void gbc_fight(struct JE_SingleEnemyType *en, int head)
{
	int k = head - 1;
	while (k >= 0 && eventRec[k].eventtype == 202 && eventRec[k].eventtime == eventRec[head].eventtime)
		--k;
	if (k < 0 || eventRec[k].eventtype != GBC_FIGHT || eventRec[k].eventtime != eventRec[head].eventtime)
		return;
	const struct JE_EventRecType *f = &eventRec[k], *h = &eventRec[head];
	const int own = gbc_shootable(en->enemytype);
	int sum = 0;
	if (h->eventtype == 201)
		for (int j = head + 1; j <= head + h->eventdat && j < EVENT_MAXIMUM; ++j)
			sum += gbc_shootable(eventRec[j].eventdat);
	else if (h->eventtype == 12)
		for (int part = 0; part < 4; ++part)
			sum += gbc_shootable(h->eventdat + part);
	else
		sum = own;
	if (f->eventdat > 0 && (own > 0 || sum == 0) && enemyDat[en->enemytype].armor != 0)  // (0: an item)
	{
		int hp = sum > 0 ? (f->eventdat * own + sum / 2) / sum : f->eventdat;
		if (difficultyLevel <= DIFFICULTY_EASY)
			hp = (hp + 1) / 2;
		else if (difficultyLevel >= DIFFICULTY_HARD)  // (above Hard as the PC's armour grows, from Hard's 1.5x)
			hp = hp * SDL_max(150, own > 0 ? en->armorleft * 100 / own + 30 : 150) / 100;
		en->armorleft = SDL_clamp(hp, 1, 254);
	}
	if (f->eventdat3 >= 0)
		gbc_fire(en, f->eventdat3);
}

// Tyrian3D: episode 7's enemies fly the GBC game's paths, which go sideways and back up the screen too, while the
// GBC's sprites always face down it, as the PC models do: in the sky one that moves sideways leans that way, at
// most GBC_LEAN degrees, easing into it (gbc_lean_now), never turning round. Not the pieces of one object (models
// drawn at their origin, or other enemies' sprites made with it at its side; a boss's pieces even apart), turning
// items, nor what stands on the ground.
#define GBC_LEAN 40.0f
#define GBC_LEAN_EASE 0.08f  // (of the way there each frame drawn)
static float gbc_lean[100];  // (by slot; NAN: just made)

static bool gbc_faces_its_way(unsigned int i, const M3DAppearance *look)
{
	if (episodeNum != EPISODE_GBC || look->model < 0 || look->spin != 0 || m3d_models[look->model].keep_origin ||
	    l3d_current_layer() == L3D_GROUND_ENEMY || gbc_piece_link(enemy[i].linknum))
		return false;
	for (unsigned int j = 0; j < COUNTOF(enemy); ++j)
		if (j != i && enemyAvail[j] != 1 && enemy_group[i] != 0 && enemy_group[j] == enemy_group[i] &&
		    enemy_group_link[j] == enemy_group_link[i] && enemy[j].egr[0] != enemy[i].egr[0] &&
		    abs(enemy[j].ex - enemy[i].ex) < 40 && abs(enemy[j].ey - enemy[i].ey) < 40)
			return false;  // (a piece of an object of several sprites)
	return true;
}

static float gbc_lean_now(unsigned int i)
{
	const float down = fabsf((float)(enemy[i].eyc + enemy[i].fixedmovey)) + 2.0f;
	const float want = SDL_clamp(-atan2f((float)enemy[i].exc, down) * 180.0f / (float)M_PI, -GBC_LEAN, GBC_LEAN);
	gbc_lean[i] = isnan(gbc_lean[i]) ? want : gbc_lean[i] + (want - gbc_lean[i]) * GBC_LEAN_EASE;
	return gbc_lean[i];
}

// Tyrian3D: a part of an episode-7 boss's look (gbc_look) at x, y (game pixels, the sprite's centre), with its glow;
// key: its motion's, forecast: the coming part it takes the place of (0: none). False if it has no model.
static bool draw_gbc_look_part(const GbcLookPart *p, float x, float y, Uint32 key, Uint32 forecast, Uint8 filter, int vx,
                               int vy, Uint32 group, Uint8 link)
{
	const M3DAppearance look = m3d_enemy_appearance(p->sheet, p->sprite, p->large, l3d_current_layer());
	if (look.model < 0)
		return false;
	float yaw = look.yaw;
	if (look.yaw_mode == M3D_YAW_AIM)
		yaw = atan2f(player[0].x + 7 - x, -(player[0].y + 7 - y)) * 180.0f / (float)M_PI;
	else if (look.yaw_mode == M3D_YAW_VELOCITY && (vx != 0 || vy != 0))
		yaw = atan2f((float)vx, (float)-vy) * 180.0f / (float)M_PI;
	if (look.spin != 0)
		yaw += fmodf(look.spin * l3d_frame_number + (float)(key & 0xff) * 47.0f, 360.0f);
	if (!l3d_add_object(look.model, x, y, look.height, yaw, 0.0f, filter))
		return true;
	l3d_enemy_last_object(p->sheet, p->sprite);
	l3d_group_last_object(group, link);
	if (look.layer > 0)
		l3d_layer_last_object((L3DLayerType)(look.layer - 1));
	float mx, my;
	l3d_key_last_object(key, NULL, NULL);
	if (forecast != 0)
		l3d_key_continue(key, forecast);
	l3d_new_object_velocity(vx, vy, &mx, &my);
	const float shown = l3d_key_shown(key);
	l3d_appear_last_object(shown);
	if (look.glow_size != 0 && (look.glow_has_rgb || look.glow_color != 0))  // (not one of the sprite's colour)
	{
		const float size = look.glow_size < 0 ? -look.glow_size * (p->large ? 24 : 12) : look.glow_size;
		if (look.glow_has_rgb)
			l3d_add_rgb_glow(x + look.glow_dx, y + look.glow_dy, size, look.glow_strength * shown, look.glow_rgb, mx, my);
		else
			l3d_add_color_glow(x + look.glow_dx, y + look.glow_dy, size, look.glow_strength * shown, look.glow_color, mx,
			                   my);
	}
	return true;
}

// Tyrian3D: the top row above which the 3D view leaves an enemy's model out (in game y). The view sees further up
// than the screen, furthest on the ground (from the Steep camera, some 135 rows up there): one coming down is drawn
// as far up as it lives, so a big one made of rows (LAVA RUN's boss, the wide walls of turrets), and its shadow,
// come down whole rather than row by row where the line used to be; one standing or rising up there is one the
// game keeps out of sight (made above the playfield's top so as not to be seen), and stays left out.
static int enemy_model_top(unsigned int i)
{
	const int vy = enemy[i].eyc + enemy[i].fixedmovey + tempBackMove;
	return vy > 0 ? -112 - l3d_field_ahead : -26 - SDL_max(screen_overscan_rows, l3d_field_ahead);
}

// Tyrian3D: an episode-7 boss's piece in the 3D view by its look (gbc_look): its parts of the PC boss's body, or none
// (true) while another piece of its group draws some; false: as itself.
static bool draw_gbc_look(unsigned int i)
{
	if (gbc_look_id[i] == 0)
		return false;
	if (gbc_look_parts[i] == 0)
	{
		for (unsigned int j = 0; j < COUNTOF(enemy); ++j)
			if (j != i && enemyAvail[j] != 1 && gbc_look_id[j] == gbc_look_id[i] && gbc_look_parts[j] > 0)
				return true;
		return false;
	}
	const float x0 = enemy[i].ex + tempMapXOfs + 6, y0 = enemy[i].ey + 7;
	const int vx = enemy[i].exc, vy = enemy[i].eyc + enemy[i].fixedmovey + tempBackMove;
	for (unsigned int k = 0; k < gbc_look_parts[i]; ++k)
	{
		GbcLookPart *p = &gbc_look[i][k];
		if (enemy[i].ey + p->dy <= enemy_model_top(i) || enemy[i].ey + p->dy >= 200)
			continue;  // off screen
		draw_gbc_look_part(p, x0 + p->dx, y0 + p->dy, GBC_LOOK_KEY(i, k), p->forecast, enemy[i].filter, vx, vy,
		                   enemy_group[i], enemy_group_link[i]);
		p->forecast = 0;
	}
	smoulder(i, x0, y0, enemy[i].size == 1);
	return true;
}

// Tyrian3D: shows the enemy as a 3D model instead of its sprite if one is mapped.
static bool draw_enemy_model(unsigned int i)
{
	if (!l3d_capturing || enemy[i].sprite2s == NULL)
		return false;
	if (episodeNum == EPISODE_GBC && m3d_enabled && draw_gbc_look(i))
		return true;

	// Keyed by the first animation frame, so the appearance stays the same while the sprite animates.
	const unsigned int first_sprite = enemy[i].egr[0];
	const char sheet = enemy_sheet_letter(enemy[i].sprite2s);
	M3DAppearance look = m3d_enemy_appearance(sheet, first_sprite, enemy[i].size == 1, l3d_current_layer());
	if (SDL_getenv("TYR3D_LOG_ENEMIES") != NULL)
	{
		static Uint32 logged[256];
		const Uint32 key = ((Uint32)(Uint8)sheet << 16) | first_sprite;
		bool seen = false;
		for (size_t k = 0; k < COUNTOF(logged) && logged[k] != 0; ++k)
			seen |= logged[k] == key + 1;
		for (size_t k = 0; !seen && k < COUNTOF(logged); ++k)
			if (logged[k] == 0)
			{
				logged[k] = key + 1;
				printf("enemy: sheet '%c' sprite %u %s layer %s -> %d (3D frame %u)\n", sheet ? sheet : '?', first_sprite,
				       enemy[i].size == 1 ? "2x2" : "1x1", l3d_layer_name(l3d_current_layer()), look.model, l3d_frame_number);
				break;
			}
	}
	if (SDL_getenv("TYR3D_LOG_GROUND") != NULL)
		log_ground_enemy(i, sheet, first_sprite, look.model >= 0 ? look.layer : 0);
	if (look.model == M3D_SPRITE)
		return false;

	if (enemy[i].ey <= enemy_model_top(i) || enemy[i].ey >= 200)
		return true;  // off screen

	// Both 1x1 and 2x2 sprites are centred on (ex + 6, ey + 7).
	const float x = enemy[i].ex + tempMapXOfs + 6, y = enemy[i].ey + 7;

	if (look.model == M3D_VOLUME)
	{
		// The current animation frame, as drawn: rotation frames are already in the sprite.
		// Ground enemies are drawn over the ground they include, so they sit flat on it.
		const bool ground = l3d_current_layer() == L3D_GROUND_ENEMY;
		const float height = ground ? 0.3f - l3d_layer_height(L3D_GROUND_ENEMY) : look.height;
		const bool added = l3d_add_volume(enemy[i].sprite2s, enemy[i].egr[enemy[i].enemycycle - 1], enemy[i].size == 1,
		                                  ground ? V3D_STYLE_FLAT : V3D_STYLE_RAISED, x, y, height, 0.0f, 0.0f,
		                                  enemy[i].filter);
		if (added && !ground)
			l3d_open_last_object(enemy_open_sides(i));
		l3d_key_last_object(ENEMY_MOTION_KEY(i), NULL, NULL);
		l3d_new_object_velocity(enemy[i].exc, enemy[i].eyc + enemy[i].fixedmovey + tempBackMove, NULL, NULL);
		if (added)
			l3d_appear_last_object(enemy_shown(i));
		return added;
	}

	const bool large = enemy[i].size == 1;
	const unsigned int sprite = enemy[i].egr[enemy[i].enemycycle - 1];
	if (look.model >= 0)
		look.model = m3d_frame_model(sheet, sprite, look.model);  // a frame that changes shape

	// Palette materials can take the colour of the current frame (items whose animation cycles
	// colours); a sprite filter (hit) wins.
	Uint8 filter = enemy[i].filter;
	if (filter == 0 && look.recolor)
		filter = (Uint8)(l3d_sprite_ramp(enemy[i].sprite2s, sprite, large) << 4);

	float yaw = look.yaw;
	switch (look.yaw_mode)
	{
	case M3D_YAW_FIXED:
		if (gbc_faces_its_way(i, &look))
			yaw += gbc_lean_now(i);
		break;
	case M3D_YAW_VELOCITY:
		if (enemy[i].exc != 0 || enemy[i].eyc != 0)
			yaw = atan2f((float)enemy[i].exc, (float)-enemy[i].eyc) * 180.0f / (float)M_PI;
		break;
	case M3D_YAW_AIM:
		yaw = atan2f(player[0].x + 7 - x, -(player[0].y + 7 - y)) * 180.0f / (float)M_PI;
		break;
	case M3D_YAW_FRAMES:
		yaw = look.yaw + (enemy[i].enemycycle - 1) * look.yaw_step;
		break;
	}

	// Turning items: each slot a little ahead of the previous one, so they don't turn in step.
	if (look.spin != 0)
		yaw += fmodf(look.spin * l3d_frame_number + i * 47.0f, 360.0f);

	const float roll = (enemy[i].enemycycle - 1) * look.roll_step;
	const bool added = l3d_add_object(look.model, x, y, look.height, yaw, roll, filter);
	if (added)
		smoulder(i, x, y, large);
	if (added)
	{
		l3d_enemy_last_object(sheet, first_sprite);
		l3d_group_last_object(enemy_group[i], enemy_group_link[i]);
	}
	if (added && look.layer > 0)
		l3d_layer_last_object((L3DLayerType)(look.layer - 1));  // a piece of an object on another layer
	float vx, vy;
	l3d_key_last_object(ENEMY_MOTION_KEY(i), NULL, NULL);
	// An enemy that has just appeared moves on as the game will move it.
	l3d_new_object_velocity(enemy[i].exc, enemy[i].eyc + enemy[i].fixedmovey + tempBackMove, &vx, &vy);
	// One made in sight fades in, its glow with it.
	const float shown = enemy_shown(i);
	if (added)
		l3d_appear_last_object(shown);
	look.glow_strength *= shown;
	// Jets (models.cfg "trail") leave contrails as they fly in the sky (with Effects).
	if (added && look.trail && settings3d.effects && shown >= 1 && l3d_current_layer() != L3D_GROUND_ENEMY)
		p3d_trail(x, y, vx, vy, l3d_layer_height(l3d_current_layer()) - l3d_terrain_headroom, P3D_TRAIL_VAPOUR,
		          large ? 20.0f : 10.0f);
	if (look.glow_size != 0)
	{
		const float size = look.glow_size < 0 ? -look.glow_size * (large ? 24 : 12) : look.glow_size;
		if (look.glow_has_rgb)
			l3d_add_rgb_glow(x + look.glow_dx, y + look.glow_dy, size, look.glow_strength, look.glow_rgb, vx, vy);
		else if (look.glow_color != 0)
			l3d_add_color_glow(x + look.glow_dx, y + look.glow_dy, size, look.glow_strength, look.glow_color, vx, vy);
		else
		{
			l3d_add_sprite_glow(enemy[i].sprite2s, sprite, large, x + look.glow_dx, y + look.glow_dy, size, look.glow_strength);
			l3d_last_glow_velocity(vx, vy);
		}
	}
	return added;
}

/*
 * Tyrian3D: enemies still to come. The 3D view sees further up than the screen, but the game
 * makes an enemy only when the map scrolls to its event, on a line just above the screen. So that
 * enemies don't pop up on that line, the events of the next stretch of map are shown ahead of
 * time: each enemy where it would be now had it existed, moving towards where it will appear
 * (carried by its layer's scroll and its own speed, as JE_drawEnemy moves it). Enemies the events
 * make below the screen, rising, are shown coming from below the same way. Only shown; it reads
 * the events and touches nothing (no random numbers either: enemies placed at random are left out).
 */
#define COMING_KEY 0x50000u
#define COMING_FAR (-260)    // game pixels: the furthest row worth showing above the screen
#define COMING_BELOW 330     // and below it

typedef struct
{
	int shapebank;
	unsigned int graphic;
	bool large;
} ComingLook;

static void draw_coming_enemy(Uint32 key, ComingLook what, float ex, float ey, float dx, float dy, float ticks, int map_x_ofs,
                              bool from_below, Uint32 group, Uint8 link)
{
	if (ticks < 0)
		return;
	const float x_now = ex - dx * ticks, y_now = ey - dy * ticks;
	if (from_below ? y_now > COMING_BELOW : y_now < COMING_FAR)
		return;

	Sprite2_array *sheet = NULL;
	if (what.shapebank == 21)
		sheet = &spriteSheet11;
	else if (what.shapebank == 26)
		sheet = &spriteSheet10;
	else
		for (size_t i = 0; i < COUNTOF(enemySpriteSheetIds); ++i)
			if (what.shapebank == enemySpriteSheetIds[i] && enemySpriteSheets[i].data != NULL)
				sheet = &enemySpriteSheets[i];
	if (sheet == NULL || what.graphic == 0 || what.graphic == 999)
		return;

	const float x = x_now + map_x_ofs + 6, y = y_now + 7;
	const char letter = enemy_sheet_letter(sheet);
	const M3DAppearance look = m3d_enemy_appearance(letter, what.graphic, what.large, l3d_current_layer());
	bool added;
	if (look.model >= 0)
		added = l3d_add_object(look.model, x, y, look.height, look.yaw, 0.0f, 0);
	else if (look.model == M3D_VOLUME)
	{
		const bool ground = l3d_current_layer() == L3D_GROUND_ENEMY;
		added = l3d_add_volume(sheet, what.graphic, what.large, ground ? V3D_STYLE_FLAT : V3D_STYLE_RAISED, x, y,
		                       ground ? 0.3f - l3d_layer_height(L3D_GROUND_ENEMY) : look.height, 0.0f, 0.0f, 0);
	}
	else
		return;
	// Tyrian3D dev: TYR3D_LOG_SPAWNS also says where an event's enemy is first shown coming.
	if (added && !l3d_key_seen(key) && SDL_getenv("TYR3D_LOG_SPAWNS") != NULL)
		printf("coming: event %u part %u first shown at %.0f,%.0f clock %u\n", (key - COMING_KEY) / 16, (key - COMING_KEY) / 4 % 4,
		       x_now, y_now, (unsigned)curLoc);
	if (added)
	{
		l3d_enemy_last_object(letter, what.graphic);
		l3d_group_last_object(group, link);  // (as the enemy will be: enemy_group)
		l3d_key_last_object(key, NULL, NULL);
		l3d_appear_last_object(l3d_key_shown(key));  // (one first shown in sight fades in)
	}
}

// Tyrian3D: a coming episode-7 boss piece's part of its look (the event 202 k: gbc_look), as draw_coming_enemy draws
// the piece (ex, ey: its place when made).
static void draw_coming_look_part(int k, float ex, float ey, float dx, float dy, float ticks, int map_x_ofs,
                                  bool from_below, Uint32 group, Uint8 link)
{
	const struct JE_EventRecType *ev = &eventRec[k];
	const float x_now = ex - dx * ticks, y_now = ey - dy * ticks + ev->eventdat5;
	if (ticks < 0 || (from_below ? y_now > COMING_BELOW : y_now < COMING_FAR))
		return;
	const GbcLookPart p = { .sprite = (Uint16)ev->eventdat, .sheet = (char)ev->eventdat3, .large = ev->eventdat6 != 0,
	                        .dx = ev->eventdat2, .dy = ev->eventdat5 };
	draw_gbc_look_part(&p, x_now + ev->eventdat2 + map_x_ofs + 6, y_now + 7, GBC_COMING_LOOK_KEY(k), 0, 0,
	                   (int)lroundf(dx), (int)lroundf(dy), group, link);
}

// The slots an event's enemies take (-1: it makes none at the screen's top; bottom: made at the
// screen's bottom), how many parts, and whether it is one of events 49-52 (enemy 0 with the
// event's sprite).
static int spawn_slots(const struct JE_EventRecType *ev, int *parts, int *bottom_y, bool *custom)
{
	*parts = 1;
	*bottom_y = 0;
	*custom = false;
	switch (ev->eventtype)
	{
	case 6:  return 25;
	case 7:  return 50;
	case 10: return 75;
	case 15: return 0;
	case 12:
		*parts = 4;
		return ev->eventdat6 <= 1 ? 25 : ev->eventdat6 == 2 ? 0 : ev->eventdat6 == 3 ? 50 : 75;
	case 17: *bottom_y = 190 + ev->eventdat5; return 25;
	case 18: *bottom_y = 190 + ev->eventdat5; return 0;
	case 23: *bottom_y = 180 + ev->eventdat5; return 50;
	case 32: *bottom_y = 190; return 50;
	case 56: *bottom_y = 190; return 75;
	case 49: case 50: case 51: case 52:
		*custom = true;
		return (const int[]){ 25, 0, 50, 75 }[ev->eventtype - 49];
	default:
		return -1;
	}
}

// How the map and the clock move on: event_step clock pixels an event step, ground_rate pixels a
// tick the ground layers move; false when the clock stands.
static bool clock_rates(bool *slow, int *event_step, float *ground_rate)
{
	*slow = map1YDelayMax > 1 && backMove < 2;
	if (*slow)
	{
		*event_step = 1;
		*ground_rate = 1.0f / map1YDelayMax;
	}
	else if (backMove > 0)
		*ground_rate = *event_step = backMove;
	else if (forceEvents)
	{
		*event_step = 1;
		*ground_rate = 0;
	}
	else
		return false;
	return true;
}

// Ticks until an event at that time happens (0: this tick).
static int ticks_until(JE_word eventtime, bool slow, int event_step)
{
	const int moves = ((int)eventtime - (int)curLoc + event_step - 1) / event_step;
	return moves <= 0 ? 0 : slow ? map1YDelay + (moves - 1) * map1YDelayMax : moves;
}

/*
 * Tyrian3D: on a playfield reaching above the screen (l3d_field_ahead: the wide playfield, the
 * side-scrolling levels), an enemy an event makes at the screen's top is made ahead of its time,
 * as far up as it flies down in that time, so it comes down through the playfield's top part and
 * is where the original makes it when the original makes it (and goes on as there). Enemies that
 * don't come down are made at their time: sky and top ones at the playfield's top, ground ones
 * where their map puts them. prespawned: the events already done that way (passed over when the
 * clock reaches them).
 */
static bool prespawned[EVENT_MAXIMUM];
#define WIDE_AHEAD 64  // the wide playfield reaches this far above the screen (the overscan rows the 3D view gets)
// Seen from the side (event 200), the playfield reaches at least this far ahead: a 16:9 window, seen from straight above
// with the playfield's width as tall as the window, shows 535 game pixels across from 6 % in, to 351 above the screen.
#define SIDE_AHEAD 340
static int prespawn_rise = 0;   // made by prespawn_events: this far above where the event puts it,
static int prespawn_ticks = 0;  // this many ticks ahead of its time

// The enemy sheet slot an enemy of that shape bank takes, as JE_makeEnemy picks it (-1: not
// loaded); 4 for the coins and two-player sheets, which are always loaded.
static int shape_bank_slot(int bank)
{
	if (bank == 21 || bank == 26)
		return 4;
	int slot = -1;
	for (int k = 0; k < (int)COUNTOF(enemySpriteSheetIds); ++k)
		if (bank == enemySpriteSheetIds[k] && enemySpriteSheets[k].data != NULL)
			slot = k;
	return slot;
}

// Events the look ahead may pass: they neither change the enemies there are or how the next ones
// are made, nor the course or speed of events (what the screen shows and plays, and the events
// that make enemies, spawn_slots).
static bool prespawn_passes(int type)
{
	switch (type)
	{
	case 0:  // (unknown: ignored)
	case 1: case 8: case 9: case 16: case 21: case 22: case 28: case 29: case 34: case 35: case 37: case 42:
	case 43: case 44: case 48: case 62: case 64: case 69: case 73: case 79: case 82: case 99: case 201: case 202: case 203: case 204:
		return true;
	default:
		return false;
	}
}

// The link of the enemies an event acting on enemies changes, when it changes only those (true):
// enemies of other links made ahead of time past it are as they would be. (Link 0 is the enemies
// without one, except where 0 means all.)
static bool event_link_target(const struct JE_EventRecType *ev, int *link)
{
	const bool picked = ev->eventdat3 > 79 && ev->eventdat3 < 90;  // (a link the game picks then)
	*link = ev->eventdat4;
	switch (ev->eventtype)
	{
	case 19:
		return ev->eventdat3 == 0;
	case 24: case 33:
		return true;
	case 20: case 27: case 55:
		return ev->eventdat4 != 0 && !picked;
	case 25: case 47: case 74:
		return ev->eventdat4 != 0;
	case 31:
		return ev->eventdat4 != 99;
	case 39:
		*link = ev->eventdat;
		return true;
	default:
		return false;
	}
}

// A boss whose death jumps (event 57) is there.
static bool boss_jump_armed(void)
{
	if (superEnemy254Jump == 0)
		return false;
	for (int i = 0; i < 100; ++i)
		if (enemyAvail[i] != 1 && enemy[i].linknum == 254)
			return true;
	return false;
}

// An event at x -99 makes its enemies where their data starts them (JE_makeEnemy: start x and y with
// a random spread). Those starting at the screen's top (their lowest start no lower than
// OWN_START_TOP) are made ahead of time too, as far up as needed to come down through all of the
// playfield's top part: the extra rise past the screen's top their lowest start needs (*extra), or
// false when they start lower down.
#define OWN_START_TOP 8
static bool own_start_rise(const struct JE_EventRecType *ev, int parts, bool custom, int *extra)
{
	*extra = 0;
	for (int part = 0; part < parts; ++part)
	{
		const int id = custom ? 0 : ev->eventdat + part;
		if (id < 0 || id > ENEMY_NUM)
			return false;
		const struct JE_SingleEnemyDat *d = &enemyDat[id];
		const int lowest = d->starty + (d->startyc != 0 ? d->startyc : 1) + SDL_max(ev->eventdat5, 0);
		if (lowest > OWN_START_TOP)
			return false;
		*extra = SDL_max(*extra, lowest + (d->esize == 1 ? 28 : 14));
	}
	return true;
}

static void prespawn_events(void)
{
	bool slow;
	int event_step;
	float ground_rate;
	if (l3d_field_ahead <= 0 || endLevel || !clock_rates(&slow, &event_step, &ground_rate))
		return;
	// Not while what comes next may never come: a jump when the screen is clear (a return, the
	// level's end) or when a boss dies.
	if (returnActive || readyToEndLevel || boss_jump_armed())
		return;
	// Links whose enemies an event before the one being looked at changes (made at their time).
	int changed_links[16], changed_count = 0;
	// Sheet slots whose sheet stays put until the event being looked at (event 5 loads others).
	bool sheet_stays[COUNTOF(enemySpriteSheetIds) + 1];
	for (size_t k = 0; k < COUNTOF(enemySpriteSheetIds) + 1; ++k)
		sheet_stays[k] = true;
	// The look ahead's clock: it follows unconditional jumps (event 54 and its returns) and the
	// maps' speed changes (event 2: the clock's rate, and the top and ground layers' enemies carried
	// at their new rates from then on). After a jump it makes ahead of time only events the clock
	// has passed this time round (the others' first time is still to come).
	bool rebased = false;        // (the clock restarted: at base_loc base_ticks ticks from now, event_step a tick)
	int base_ticks = 0;
	int base_loc = curLoc;
	int jumps = 0, pending_last = -1;  // (events from eventLoc - 1 to pending_last are still due before the jump)
	int return_loc = returnLoc;
	float rate_top = backMove3, rate_ground = ground_rate, carried_top = 0, carried_ground = 0;
	float slowest_top = rate_top, slowest_ground = rate_ground;  // (the slowest rates from now on)
	int change_ticks = 0;
	for (int e = eventLoc - 1; e >= 0 && e < maxEvent; ++e)
	{
		struct JE_EventRecType *ev = &eventRec[e];
		int ticks;
		if (!rebased)
			ticks = ticks_until(ev->eventtime, slow, event_step);
		else
		{
			const int moves = ((int)ev->eventtime - base_loc + event_step - 1) / event_step;
			ticks = base_ticks + SDL_max(moves, 0);
		}
		// The clock at the start of that tick (events come before the clock moves on).
		const int clock = (rebased ? base_loc : (int)curLoc) + (ticks - base_ticks) * event_step;
		if (ticks > l3d_field_ahead + 1 + OWN_START_TOP + 28)
			break;  // (at least a pixel a tick: none of the later ones is due)
		// Nor past the level's timer running out (it jumps).
		if (levelTimer && levelTimerCountdown > 0 && levelTimerCountdown <= ticks + 1)
			return;
		switch (ev->eventtype)
		{
		case 2:
		{
			// The maps' speeds: the clock goes on at its new rate (not when it stands; the slow
			// clock's phase isn't followed).
			const int step = ev->eventdat > 0 ? ev->eventdat : forceEvents ? 1 : 0;
			if (slow || step <= 0)
				return;
			carried_top += rate_top * (ticks - change_ticks);
			carried_ground += rate_ground * (ticks - change_ticks);
			change_ticks = ticks;
			rate_top = ev->eventdat3;
			rate_ground = ev->eventdat;
			slowest_top = SDL_min(slowest_top, rate_top);
			slowest_ground = SDL_min(slowest_ground, rate_ground);
			if (step != event_step)
			{
				base_loc = clock;
				base_ticks = ticks;
				event_step = step;
				rebased = true;
			}
			continue;
		}
		case 54:
		{
			// A jump (or a return, 65535): the clock goes on from there.
			if (slow || ++jumps > 4)
				return;
			if (pending_last < 0)
				pending_last = e;
			const JE_word jump = (JE_word)ev->eventdat;  // (as JE_eventJump takes it)
			const int target = jump == 65535 ? return_loc : jump;
			if (jump != 65535)
				return_loc = clock + 1;  // (JE_eventJump: where the clock is then, plus one)
			base_ticks = ticks;
			base_loc = target;
			rebased = true;
			int i = 0;
			while (i < maxEvent && (int)eventRec[i].eventtime < target)
				++i;
			e = i - 1;  // (the loop's ++e)
			continue;
		}
		case 5:
		{
			// The enemy sheets change: an enemy holds its slot's sheet, and one made before its
			// sheet is loaded has no sprite, so later ones are made ahead of time only from
			// sheets this keeps in their slots.
			const int tables[COUNTOF(enemySpriteSheetIds)] = {
				SDL_max(ev->eventdat, 0), SDL_max(ev->eventdat2, 0), SDL_max(ev->eventdat3, 0), ev->eventdat4,
			};
			for (size_t k = 0; k < COUNTOF(enemySpriteSheetIds); ++k)
				if (tables[k] != enemySpriteSheetIds[k])
					sheet_stays[k] = false;
			continue;
		}
		default:
			break;
		}
		int parts, bottom_y;
		bool custom;
		const int offset = spawn_slots(ev, &parts, &bottom_y, &custom);
		// Not past what may change the enemies there are, how the next are made, the course of
		// events (jumps, skips) or the speeds the times were reckoned at: what comes after it is
		// made at its own time. This runs before the tick's events, so that holds for one due this
		// tick too.
		int link;
		if (offset < 0 && event_link_target(ev, &link))
		{
			if (changed_count == (int)COUNTOF(changed_links))
				return;
			changed_links[changed_count++] = link;
			continue;
		}
		if (offset < 0 && !prespawn_passes(ev->eventtype))
			return;
		if (ticks == 0 || prespawned[e] || offset < 0 || bottom_y != 0)
			continue;
		if (jumps > 0 && e >= eventLoc - 1 && e <= pending_last)
			continue;  // (its first time is still to come)
		const bool own_start = ev->eventdat2 == -99;  // (at its data's start position)
		int extra = 0;
		if (own_start && !own_start_rise(ev, parts, custom, &extra))
			continue;
		bool changed = false;
		for (int k = 0; k < changed_count; ++k)
			changed = changed || changed_links[k] == ev->eventdat4;
		if (changed)
			continue;
		const Uint16 eDatI = custom ? 0 : (Uint16)ev->eventdat;
		if ((eDatI == 0 && !custom) || eDatI + (custom ? 0 : parts - 1) > ENEMY_NUM)
			continue;
		const struct JE_SingleEnemyDat *dat = &enemyDat[eDatI];
		// Carried by its layer at the rates the maps move at until then.
		const float carried = offset == 0 ? 0 : offset == 50 ? carried_top + rate_top * (ticks - change_ticks)
		                                                   : carried_ground + rate_ground * (ticks - change_ticks);
		const float slowest = offset == 0 ? 0 : offset == 50 ? slowest_top : slowest_ground;
		const int own_dy = custom ? dat->ymove : dat->ymove + ev->eventdat3 + ev->eventdat6 * (ev->eventtype != 12);
		const int rise = (int)lroundf(own_dy * ticks + carried);
		// (coming down all the way: not standing in sight while its layer stands)
		if (own_dy + slowest <= 0 || rise <= 0 || rise > l3d_field_ahead + extra)
			continue;
		// Only enemies on a steady course, the same for all its parts: back up it (and back along
		// it sideways) is where they come from. Those steering for the player or swinging up and
		// down are made at their time; a boss whose death jumps too (it could die before its time).
		bool steady = !(superEnemy254Jump > 0 && ev->eventdat4 == 254);
		for (int part = 0; part < parts && steady; ++part)
		{
			const struct JE_SingleEnemyDat *d = &enemyDat[custom ? 0 : eDatI + part];
			steady = d->xaccel == 0 && d->yaccel == 0 && d->ycaccel == 0 && d->ymove == dat->ymove;
			// (sideways, not so far back that the game takes it for gone: JE_drawEnemy)
			if (steady && d->xcaccel == 0 && d->xmove != 0 && own_start)
			{
				const int spread = d->startxc != 0 ? d->startxc : 1;
				const int left = d->startx - spread + 1 - d->xmove * ticks, right = d->startx + spread - d->xmove * ticks;
				steady = left > -76 && right < 336;
			}
			else if (steady && d->xcaccel == 0 && d->xmove != 0)
			{
				int ex = ev->eventdat2 - (mapX - 1) * 24 + (part & 1) * 24;
				if (offset == 25 || offset == 75 || (offset == 50 && background3x1))
					ex -= 12;
				else if (offset == 50)
					ex = ev->eventdat2 - mapX3 * 24 - 24 * 2 + 6 + (part & 1) * 24;
				if (offset == 50 && background3x1b)
					ex -= 6;
				const int start = ex - d->xmove * ticks;
				steady = start > -76 && start < 336;
			}
		}
		if (!steady)
			continue;
		// Only with its sheets loaded now and kept until its time (events 49-52 give the enemy
		// the event's shape bank).
		bool sheets_hold = true;
		for (int part = 0; part < parts && sheets_hold; ++part)
		{
			const int id = custom ? 0 : (int)ev->eventdat + part;
			const int bank = custom && ev->eventdat3 > 0 ? ev->eventdat3 : (id >= 0 && id <= ENEMY_NUM ? enemyDat[id].shapebank : -1);
			const int slot = shape_bank_slot(bank);
			sheets_hold = slot >= 0 && sheet_stays[slot];
		}
		if (!sheets_hold)
			continue;
		// With room for all its parts (an enemy that finds none is lost).
		int free_slots = 0;
		for (int i = offset; i < offset + 25; ++i)
			free_slots += enemyAvail[i] == 1;
		if (free_slots < parts)
			return;

		// Made now, as the event makes it, that far up (and back).
		const JE_word saved = eventLoc;
		eventLoc = (JE_word)(e + 1);
		prespawn_rise = rise;
		prespawn_ticks = ticks;
		JE_eventSystem();
		prespawn_rise = 0;
		prespawn_ticks = 0;
		eventLoc = saved;
		prespawned[e] = true;
	}
}

// enemy_offset: the slots of the layer being drawn (0 sky, 25 and 75 ground, 50 top).
static void draw_coming_enemies(int enemy_offset)
{
	if (!l3d_capturing || !m3d_enabled || endLevel)
		return;
	// How far the events move on a tick (on slowly scrolling maps the map moves a pixel every few
	// ticks: the next time in map1YDelay ticks), and how far the layer carries its enemies.
	bool slow;
	int event_step;
	float ground_rate;
	if (!clock_rates(&slow, &event_step, &ground_rate))
		return;
	const float carried = enemy_offset == 0 ? 0 : enemy_offset == 50 ? backMove3 : ground_rate;
	const int map_x_ofs = enemy_offset == 0 ? mapX2Ofs : enemy_offset == 50 ? (background3x1 == 0 ? oldMapX3Ofs : mapXOfs) : mapXOfs;

	bool adjust = smallEnemyAdjust;  // (as it will be at each event: event 26 sets it)
	for (int e = eventLoc - 1; e >= 0 && e < maxEvent; ++e)
	{
		const struct JE_EventRecType *ev = &eventRec[e];
		// The event happens `ticks` ticks from now: the map moves until it reaches the event, and
		// events come at the start of a tick, before the map moves. The enemy is first drawn in that
		// tick, a tick's movement from where it is made.
		const float ticks = 1 + ticks_until(ev->eventtime, slow, event_step);
		if (ticks > 400)
			break;
		if (ev->eventtype == 26)
		{
			adjust = ev->eventdat != 0;
			continue;
		}
		if (ev->eventtype == 66 && initialDifficulty <= ev->eventdat)
		{
			// (the events it skips on this difficulty never come: shown, episode 7's Normal and Hard enemies came
			// down on Easy and vanished where they'd have been made, the user's asteroids and planes "vanishing
			// halfway down the screen")
			e += ev->eventdat2;
			continue;
		}

		// The slots the event's enemies take, how many (a 2x2 group), and where they appear.
		int parts, bottom_y;
		bool custom;  // events 49-52: enemy 0 with the event's sprite
		const int offset = spawn_slots(ev, &parts, &bottom_y, &custom);
		if (offset != enemy_offset || ev->eventdat2 == -200 || ev->eventdat2 == -99 || prespawned[e])
			continue;

		for (int part = 0; part < parts; ++part)
		{
			const Uint16 eDatI = custom ? 0 : (Uint16)(ev->eventdat + part);
			if ((eDatI == 0 && !custom) || eDatI > ENEMY_NUM)
				continue;
			const struct JE_SingleEnemyDat *dat = &enemyDat[eDatI];
			ComingLook what = { dat->shapebank, dat->egraphic[0], dat->esize == 1 };
			if (custom)
			{
				what.graphic = (unsigned int)ev->eventdat;
				if (ev->eventdat3 > 0)
					what.shapebank = ev->eventdat3;
			}

			int ex = ev->eventdat2 - (mapX - 1) * 24;
			if (offset == 25 || offset == 75)
				ex -= 12;
			else if (offset == 50)
				ex = background3x1 ? ev->eventdat2 - (mapX - 1) * 24 - 12 : ev->eventdat2 - mapX3 * 24 - 24 * 2 + 6;
			int ey = -28;
			if (offset == 50 && background3x1b)
			{
				ex -= 6;
				ey += 4;
			}
			if (adjust && dat->esize == 0)
			{
				ex -= 10;
				ey -= 7;
			}
			if (part & 1)
				ex += 24;
			if (part & 2)
				ey -= 28;
			ey += ev->eventdat5;
			if (bottom_y != 0)
				ey = bottom_y;
			// Events 49-52 give the enemy no speed of their own (eventdat3 and 6 mean other things).
			const int own_dy = custom ? dat->ymove : dat->ymove + ev->eventdat3 + ev->eventdat6 * (ev->eventtype != 12);
			const float dy = own_dy + carried;
			const Uint32 key = COMING_KEY + (Uint32)(e * 4 + part) * 4 + (eDatI & 3);
			// (Tyrian3D: an episode-7 boss's piece with a look, the events 202 right before it: its parts instead)
			int look_from = e;
			while (episodeNum == EPISODE_GBC && parts == 1 && look_from > 0 && eventRec[look_from - 1].eventtype == 202 &&
			       eventRec[look_from - 1].eventtime == ev->eventtime)
				--look_from;
			if (look_from < e)
			{
				if (bottom_y != 0 ? dy < 0 : dy > 0)
					for (int k = look_from; k < e; ++k)
						if (eventRec[k].eventdat > 0)
							draw_coming_look_part(k, ex + dat->xmove, ey + dy, dat->xmove, dy, ticks, map_x_ofs, bottom_y != 0,
							                      (Uint32)ev->eventtime + 1, (Uint8)ev->eventdat4);
				continue;
			}
			if (bottom_y != 0 ? dy < 0 : dy > 0)
				draw_coming_enemy(key, what, ex + dat->xmove, ey + dy, dat->xmove, dy, ticks, map_x_ofs, bottom_y != 0,
				                  (Uint32)ev->eventtime + 1, (Uint8)ev->eventdat4);
		}
	}
}

/*
 * Tyrian3D: stand-ins. Where the 3D view's clean ground (tools/terrain/make_cleanground.py) erased what
 * the ground map paints of an object (what is left of it once destroyed, or the object itself), the
 * original shows that painting whenever the enemy's sprite doesn't cover it: before the enemy comes, once
 * it is destroyed, and where none ever stands. So the model of that painting (assets/terrain/<map>.std:
 * the look the game leaves standing when it is destroyed, the object's own model, or a placeholder) is
 * shown at its place on the map while no ground enemy of its looks (alive, dead, coming or what it turns
 * into) is drawn there. Only shown; it touches nothing of the game.
 */
#define STANDIN_KEY 0x70000u  // (after layer3d.c L3D_KEY_DEPARTED)
#define STANDIN_GROUP 0x40000000u
#define STANDIN_COVERED 6.5f   // game pixels: an enemy of its looks this near covers it
#define STANDIN_FAR (-420)     // game pixels: the furthest row worth showing above the screen
#define STANDIN_BELOW 330

static bool standin_covered(const B3DStandin *s, float x, float y, L3DLayerType layer)
{
	for (int o = 0; o < l3d_frame.object_count; ++o)
	{
		const L3DObject *object = &l3d_frame.objects[o];
		if (object->layer != layer || object->enemy_sheet == 0 || object->standin != 0 ||
		    fabsf(object->x - x) > STANDIN_COVERED || fabsf(object->y - y) > STANDIN_COVERED)
			continue;
		for (int k = 0; k < s->cover_count; ++k)
			if (s->cover_sheet[k] == object->enemy_sheet && s->cover_sprite[k] == object->enemy_sprite)
				return true;
	}
	return false;
}

// set: the background whose map's stand-ins these are (1 the ground's, among the ground enemies; 3 background
// 3's, among the top enemies riding it).
static void draw_standins(int set)
{
	if (!l3d_capturing || !m3d_enabled || endLevel)
		return;
	const B3DStandins *standins = b3d_standins(set);
	if (standins == NULL)
		return;
	const L3DLayerType layer = set == 3 ? L3D_TOP_ENEMY : L3D_GROUND_ENEMY;
	const L3DBackground *ground = NULL;
	for (int b = 0; b < l3d_frame.background_count; ++b)
		if (l3d_frame.backgrounds[b].set == set)
			ground = &l3d_frame.backgrounds[b];
	float ox, oy;  // where the map's corner is on the screen (the map moves as a whole)
	if (ground == NULL || !b3d_screen_point(ground, 0.0f, 0.0f, &ox, &oy))
		return;
	static int log_on = -1;  // TYR3D_LOG_STANDINS=1: every 30th frame, the stand-ins shown on the screen
	if (log_on < 0)
		log_on = SDL_getenv("TYR3D_LOG_STANDINS") != NULL;
	const bool log_now = log_on && l3d_frame_number % 30 == 0;
	int shown = 0, covered = 0;
	for (int i = 0; i < standins->count; ++i)
	{
		const B3DStandin *s = &standins->standins[i];
		const float x = ox + s->x, y = oy + s->y;
		if (y < STANDIN_FAR || y > STANDIN_BELOW)
			continue;
		if (standin_covered(s, x, y, layer))
		{
			covered += y >= 0;
			continue;
		}
		M3DAppearance look = m3d_enemy_appearance(s->sheet, s->sprite, s->large, L3D_GROUND_ENEMY);
		// A placeholder gives way to the look's wreck model where there is one (models.cfg "wreck").
		Uint8 mode = s->mode;
		const int wreck = mode == L3D_STANDIN_PLACEHOLDER ? m3d_wreck_model(s->sheet, s->sprite) : -1;
		if (wreck == M3D_WRECK_NONE)
			continue;
		if (wreck >= 0)
		{
			look.model = wreck;
			mode = L3D_STANDIN_OWN;
		}
		else if (mode == L3D_STANDIN_OWN && m3d_standin_model(s->sheet, s->sprite) >= 0)
			look.model = m3d_standin_model(s->sheet, s->sprite);
		if (look.model < 0 || !l3d_add_object(look.model, x, y, look.height, look.yaw, 0.0f, 0))
			continue;
		if (log_now && y >= 0 && y < 200)
		{
			// (and the nearest ground enemy, to see why it doesn't cover it)
			const L3DObject *near = NULL;
			float best = 1e9f;
			for (int o = 0; o < l3d_frame.object_count; ++o)
			{
				const L3DObject *object = &l3d_frame.objects[o];
				const float d = fabsf(object->x - x) + fabsf(object->y - y);
				if (object->enemy_sheet != 0 && object->standin == 0 && d < best)
				{
					best = d;
					near = object;
				}
			}
			printf("standin: frame %u look %c%d %s at %.0f,%.0f (map %.0f,%.0f)", l3d_frame_number, s->sheet, s->sprite,
			       mode == L3D_STANDIN_PLACEHOLDER ? "placeholder" : wreck >= 0 ? "wreck" : "own", x, y, s->x, s->y);
			if (near != NULL)
				printf(" nearest %c%u (layer %d) at %+.1f,%+.1f", near->enemy_sheet, near->enemy_sprite, (int)near->layer,
				       near->x - x, near->y - y);
			printf("\n");
			++shown;
		}
		l3d_enemy_last_object(s->sheet, s->sprite);
		l3d_group_last_object(STANDIN_GROUP + s->group, 0);
		l3d_key_last_object(STANDIN_KEY + (Uint32)i, NULL, NULL);
		l3d_standin_last_object(mode);
		if (look.layer > 0)
			l3d_layer_last_object((L3DLayerType)(look.layer - 1));
	}
	if (log_now)
		printf("standins: frame %u shown %d covered %d (on the screen)\n", l3d_frame_number, shown, covered);
}

// Tyrian3D: an enemy's force field as it acts (particles3d.h), a ring every so often.
static void show_field(int enemy_index, int x, int y, P3DField field, float reach)
{
	if (!l3d_enabled || enemy_index < 0 || enemy_index >= 100)
		return;
	static Uint32 last_pulse[100];
	const bool pulse = l3d_frame_number - last_pulse[enemy_index] >= 24;
	if (pulse)
		last_pulse[enemy_index] = l3d_frame_number;
	p3d_field((float)x + 6, (float)y + 7, enemy[enemy_index].enemyground ? 4.0f : 30.0f, field, reach, pulse);
}

/*
 * Tyrian3D: on the wide playfield the ship shoots further than in the original (up to l3d_field_ahead above the
 * screen, and at its sides), so it can bring a boss down before the level's events take it over: HARVEST's ship (link
 * 10), shot down before its fight, left the one piece the fight then makes (enemy 66, stopped high above the playfield,
 * to go with the ship) alone and out of reach, and the map, stopped until the ground's enemies are gone, never moved
 * on. An enemy like that (above where the shots reach, not coming down, and so all that is left of its link) doesn't
 * hold the map stopped (enemyOnScreen); once the map moves on it comes down with the ground and can be fought.
 */
static bool out_of_reach(int i)
{
	// (The layer that carries it, by its slot as JE_drawEnemy's groups take them: ground 25-49 and 75-99, sky 0-24,
	// top 50-74.)
	const int carried = i < 25 ? 0 : i < 50 || i >= 75 ? backMove : backMove3;
	return enemy[i].ey + (enemy[i].size == 1 ? 28 : 14) <= -15 - l3d_field_ahead &&  // (shots: shots.c)
	       enemy[i].eyc + enemy[i].fixedmovey + carried <= 0;
}

static bool stranded_enemy(int i)
{
	// (All that is left of its link, not only the last one: a boss's pieces made after its core was shot down,
	// stopped above the playfield with the map.)
	if (!l3d_field_wide || enemy[i].linknum == 0 || !out_of_reach(i))
		return false;
	for (int j = 0; j < 100; ++j)
		if (j != i && enemyAvail[j] != 1 && enemy[j].linknum == enemy[i].linknum && !out_of_reach(j))
			return false;
	return true;
}

void JE_drawEnemy(int enemyOffset) // actually does a whole lot more than just drawing
{
	player[0].x -= 25;

	for (int i = enemyOffset - 25; i < enemyOffset; i++)
	{
		if (enemyAvail[i] != 1)
		{
			enemy[i].mapoffset = tempMapXOfs;

			if (enemy[i].xaccel && enemy[i].xaccel - 89u > mt_rand() % 11)
			{
				if (player[0].x > enemy[i].ex)
				{
					if (enemy[i].exc < enemy[i].xaccel - 89)
						enemy[i].exc++;
				}
				else
				{
					if (enemy[i].exc >= 0 || -enemy[i].exc < enemy[i].xaccel - 89)
						enemy[i].exc--;
				}
			}

			if (enemy[i].yaccel && enemy[i].yaccel - 89u > mt_rand() % 11)
			{
				if (player[0].y > enemy[i].ey)
				{
					if (enemy[i].eyc < enemy[i].yaccel - 89)
						enemy[i].eyc++;
				}
				else
				{
					if (enemy[i].eyc >= 0 || -enemy[i].eyc < enemy[i].yaccel - 89)
						enemy[i].eyc--;
				}
			}

 			if (enemy[i].ex + tempMapXOfs > -29 && enemy[i].ex + tempMapXOfs < 300 + l3d_field_right())
			{
				if (enemy[i].aniactive == 1)
				{
					enemy[i].enemycycle++;

					if (enemy[i].enemycycle == enemy[i].animax)
						enemy[i].aniactive = enemy[i].aniwhenfire;
					else if (enemy[i].enemycycle > enemy[i].ani)
						enemy[i].enemycycle = enemy[i].animin;
				}

				if (enemy[i].egr[enemy[i].enemycycle - 1] == 999)
					goto enemy_gone;

				if (draw_enemy_model(i))
				{
					// drawn as a 3D model
				}
				else if (enemy[i].size == 1) // 2x2 enemy
				{
					if (enemy[i].ey > -13 - screen_overscan_rows)
					{
						blit_enemy(VGAScreen, i, -6, -7, 0);
						blit_enemy(VGAScreen, i,  6, -7, 1);
					}
					if (enemy[i].ey > -26 - screen_overscan_rows && enemy[i].ey < 182)
					{
						blit_enemy(VGAScreen, i, -6,  7, 19);
						blit_enemy(VGAScreen, i,  6,  7, 20);
					}
				}
				else
				{
					if (enemy[i].ey > -13 - screen_overscan_rows)
						blit_enemy(VGAScreen, i, 0, 0, 0);
				}

				enemy[i].filter = 0;
			}
			// Tyrian3D: the wide 3D view sees beyond those sides near its top, as far as enemies live: their models
			// there too (the game goes on as ever: no animation step, no sprite), so they don't pop in at the edges.
			else if (l3d_field_wide && l3d_capturing && enemy[i].ex + tempMapXOfs > -80 && enemy[i].ex + tempMapXOfs < 340 &&
			         enemy[i].egr[enemy[i].enemycycle - 1] != 999)
				draw_enemy_model(i);

			if (enemy[i].excc)
			{
				if (--enemy[i].exccw <= 0)
				{
					if (enemy[i].exc == enemy[i].exrev)
					{
						enemy[i].excc = -enemy[i].excc;
						enemy[i].exrev = -enemy[i].exrev;
						enemy[i].exccadd = -enemy[i].exccadd;
					}
					else
					{
						enemy[i].exc += enemy[i].exccadd;
						enemy[i].exccw = enemy[i].exccwmax;
						if (enemy[i].exc == enemy[i].exrev)
						{
							enemy[i].excc = -enemy[i].excc;
							enemy[i].exrev = -enemy[i].exrev;
							enemy[i].exccadd = -enemy[i].exccadd;
						}
					}
				}
			}

			if (enemy[i].eycc)
			{
				if (--enemy[i].eyccw <= 0)
				{
					if (enemy[i].eyc == enemy[i].eyrev)
					{
						enemy[i].eycc = -enemy[i].eycc;
						enemy[i].eyrev = -enemy[i].eyrev;
						enemy[i].eyccadd = -enemy[i].eyccadd;
					}
					else
					{
						enemy[i].eyc += enemy[i].eyccadd;
						enemy[i].eyccw = enemy[i].eyccwmax;
						if (enemy[i].eyc == enemy[i].eyrev)
						{
							enemy[i].eycc = -enemy[i].eycc;
							enemy[i].eyrev = -enemy[i].eyrev;
							enemy[i].eyccadd = -enemy[i].eyccadd;
						}
					}
				}
			}

			enemy[i].ey += enemy[i].fixedmovey;

			enemy[i].ex += enemy[i].exc;
			if (enemy[i].ex < -80 || enemy[i].ex > 340)
				goto enemy_gone;

			enemy[i].ey += enemy[i].eyc;
			if (enemy[i].ey < -112 - l3d_field_ahead || enemy[i].ey > 190)
				goto enemy_gone;

			goto enemy_still_exists;

enemy_gone:
			/* enemy[i].egr[10] &= 0x00ff; <MXD> madness? */
			enemyAvail[i] = 1;
			goto draw_enemy_end;

enemy_still_exists:

			/*X bounce*/
			if (enemy[i].ex <= enemy[i].xminbounce || enemy[i].ex >= enemy[i].xmaxbounce)
				enemy[i].exc = -enemy[i].exc;

			/*Y bounce*/
			if (enemy[i].ey <= enemy[i].yminbounce || enemy[i].ey >= enemy[i].ymaxbounce)
				enemy[i].eyc = -enemy[i].eyc;

			/* Evalue != 0 - score item at boundary */
			if (enemy[i].scoreitem)
			{
				// (Tyrian3D: on the wide playfield, where the ship can pick it up: within 8 of where the ship goes
				// (x 16-288, a pickup within 12: mainint.c), its layer's offset held still; at 1-307, the edges of
				// what shows, it was out of reach.)
				const int left = l3d_field_wide ? 40 - l3d_field_left() - 8 - tempMapXOfs : -5;
				const int right = l3d_field_wide ? 256 + l3d_field_right() + 8 - tempMapXOfs : 245;
				if (enemy[i].ex < left)
					enemy[i].ex++;
				if (enemy[i].ex > right)
					enemy[i].ex--;
				// (Tyrian3D: above where the ship goes, not coming down: down into reach, as gently; and once the
				// level only waits for the screen to clear (36), down past the ship and away, since one standing
				// still held the level's end (REEF's cube from a courier: until its closing event, 40 s on).)
				if (!isNetworkGame && !play_demo && !record_demo && enemy[i].eyc + enemy[i].fixedmovey + tempBackMove <= 0 &&
				    ((l3d_field_wide && enemy[i].ey < 10 - l3d_field_ahead - 8) || readyToEndLevel))
					enemy[i].ey++;
			}

			enemy[i].ey += tempBackMove;

			// (Tyrian3D: on the wide playfield, where it shows on 0-319, as far out as the original
			// allows round 24-287.)
			if (l3d_field_wide ? enemy[i].ex + tempMapXOfs <= -33 || enemy[i].ex + tempMapXOfs >= 343
			                   : enemy[i].ex <= -24 || enemy[i].ex >= 296)
				goto draw_enemy_end;

			JE_integer tempX = enemy[i].ex;
			JE_integer tempY = enemy[i].ey;

			temp = enemy[i].enemytype;

			/* Enemy Shots */
			if (enemy[i].edamaged == 1)
				goto draw_enemy_end;

			if (!stranded_enemy(i))
				enemyOnScreen++;

			if (enemy[i].iced)
			{
				enemy[i].iced--;
				if (enemy[i].enemyground != 0)
				{
					enemy[i].filter = 0x09;
				}
				goto draw_enemy_end;
			}

			for (int j = 3; j > 0; j--)
			{
				if (enemy[i].freq[j-1])
				{
					temp3 = enemy[i].tur[j-1];

					if (--enemy[i].eshotwait[j-1] == 0 && temp3)
					{
						enemy[i].eshotwait[j-1] = enemy[i].freq[j-1];
						if (difficultyLevel > DIFFICULTY_NORMAL)
						{
							enemy[i].eshotwait[j-1] = (enemy[i].eshotwait[j-1] / 2) + 1;
							if (difficultyLevel > DIFFICULTY_MANIACAL)
								enemy[i].eshotwait[j-1] = (enemy[i].eshotwait[j-1] / 2) + 1;
						}

						if (galagaMode && (enemy[i].eyc == 0 || (mt_rand() % 400) >= galagaShotFreq))
							goto draw_enemy_end;

						switch (temp3)
						{
						case 252: /* Savara Boss DualMissile */
							if (enemy[i].ey > 20)
							{
								JE_setupExplosion(tempX - 8 + tempMapXOfs, tempY - 20 - backMove * 8, -2, 6, false, false);
								JE_setupExplosion(tempX + 4 + tempMapXOfs, tempY - 20 - backMove * 8, -2, 6, false, false);
							}
							break;
						case 251:; /* Suck-O-Magnet */
							const JE_integer attraction = 4 - (abs(player[0].x - tempX) + abs(player[0].y - tempY)) / 100;
							if (attraction > 0)
								player[0].x_velocity += (player[0].x > tempX) ? -attraction : attraction;
							show_field(i, tempX + tempMapXOfs, tempY, P3D_FIELD_ATTRACT, 90);  // Tyrian3D
							break;
						case 253: /* Left ShortRange Magnet */
							show_field(i, tempX + tempMapXOfs, tempY, P3D_FIELD_RIGHT, 24);  // Tyrian3D
							if (abs(player[0].x + 25 - 14 - tempX) < 24 && abs(player[0].y - tempY) < 28)
							{
								player[0].x_velocity += 2;
							}
							if (twoPlayerMode &&
							   (abs(player[1].x - 14 - tempX) < 24 && abs(player[1].y - tempY) < 28))
							{
								player[1].x_velocity += 2;
							}
							break;
						case 254: /* Left ShortRange Magnet */
							show_field(i, tempX + tempMapXOfs, tempY, P3D_FIELD_LEFT, 24);  // Tyrian3D
							if (abs(player[0].x + 25 - 14 - tempX) < 24 && abs(player[0].y - tempY) < 28)
							{
								player[0].x_velocity -= 2;
							}
							if (twoPlayerMode &&
							   (abs(player[1].x - 14 - tempX) < 24 && abs(player[1].y - tempY) < 28))
							{
								player[1].x_velocity -= 2;
							}
							break;
						case 255: /* Magneto RePulse!! */
							if (difficultyLevel != DIFFICULTY_EASY) /*DIF*/
							{
								if (j == 3)
								{
									enemy[i].filter = 0x70;
								}
								else
								{
									const JE_integer repulsion = 4 - (abs(player[0].x - tempX) + abs(player[0].y - tempY)) / 20;
									if (repulsion > 0)
										player[0].x_velocity += (player[0].x > tempX) ? repulsion : -repulsion;
									show_field(i, tempX + tempMapXOfs, tempY, P3D_FIELD_REPULSE, 80);  // Tyrian3D
								}
							}
							break;
						default:
						/*Rot*/
							for (int tempCount = weapons[temp3].multi; tempCount > 0; tempCount--)
							{
								for (b = 0; b < ENEMY_SHOT_MAX; b++)
								{
									if (enemyShotAvail[b] == 1)
										break;
								}
								if (b == ENEMY_SHOT_MAX || (gbc_piece_link(enemy[i].linknum) && gbc_shots_full()))
									goto draw_enemy_end;

								enemyShotAvail[b] = !enemyShotAvail[b];
								dev_balance("shot", enemy[i].enemytype);  // Tyrian3D dev
								shot_from[b] = enemy[i].enemytype;

								if (weapons[temp3].sound > 0)
								{
									do
									{
										temp = mt_rand() % 8;
									} while (temp == 3);
									soundQueue[temp] = weapons[temp3].sound;
								}

								if (enemy[i].aniactive == 2)
									enemy[i].aniactive = 1;

								if (++enemy[i].eshotmultipos[j-1] > weapons[temp3].max)
									enemy[i].eshotmultipos[j-1] = 1;

								int tempPos = enemy[i].eshotmultipos[j-1] - 1;

								if (j == 1)
									temp2 = 4;

								enemyShot[b].sx = tempX + weapons[temp3].bx[tempPos] + tempMapXOfs;
								enemyShot[b].sy = tempY + weapons[temp3].by[tempPos];
								enemyShot[b].sdmg = weapons[temp3].attack[tempPos];
								// Tyrian3D: episode 7's shots hurt as the GBC's do on its difficulty, a point less on Easy and one
								// more on Hard (a gun's damage + the difficulty - 1, $054d), but at least one
								if (episodeNum == EPISODE_GBC && enemyShot[b].sdmg > 0 && enemyShot[b].sdmg < 100)
									enemyShot[b].sdmg = SDL_max(1, enemyShot[b].sdmg + difficultyLevel - DIFFICULTY_NORMAL);
								enemyShot[b].tx = weapons[temp3].tx;
								enemyShot[b].ty = weapons[temp3].ty;
								enemyShot[b].duration = weapons[temp3].del[tempPos];
								enemyShot[b].animate = 0;
								enemyShot[b].animax = weapons[temp3].weapani;

								enemyShot[b].sgr = weapons[temp3].sg[tempPos];
								switch (j)
								{
								case 1:
									enemyShot[b].syc = weapons[temp3].acceleration;
									enemyShot[b].sxc = weapons[temp3].accelerationx;

									enemyShot[b].sxm = weapons[temp3].sx[tempPos];
									enemyShot[b].sym = weapons[temp3].sy[tempPos];
									break;
								case 3:
									enemyShot[b].sxc = -weapons[temp3].acceleration;
									enemyShot[b].syc = weapons[temp3].accelerationx;

									enemyShot[b].sxm = -weapons[temp3].sy[tempPos];
									enemyShot[b].sym = -weapons[temp3].sx[tempPos];
									break;
								case 2:
									enemyShot[b].sxc = weapons[temp3].acceleration;
									enemyShot[b].syc = -weapons[temp3].acceleration;

									enemyShot[b].sxm = weapons[temp3].sy[tempPos];
									enemyShot[b].sym = -weapons[temp3].sx[tempPos];
									break;
								}

								if (weapons[temp3].aim > 0)
								{
									JE_byte aim = weapons[temp3].aim;

									/*DIF*/
									if (difficultyLevel > DIFFICULTY_NORMAL)
										aim += difficultyLevel - 2;

									JE_word targetX = player[0].x;
									JE_word targetY = player[0].y;

									if (twoPlayerMode)
									{
										// fire at live player(s)
										if (player[0].is_alive && !player[1].is_alive)
											temp = 0;
										else if (player[1].is_alive && !player[0].is_alive)
											temp = 1;
										else
											temp = mt_rand() % 2;

										if (temp == 1)
										{
											targetX = player[1].x - 25;
											targetY = player[1].y;
										}
									}

									JE_integer aimX = (targetX + 25) - tempX - tempMapXOfs - 4;
									if (aimX == 0)
										aimX = 1;
									JE_integer aimY = targetY - tempY;
									if (aimY == 0)
										aimY = 1;
									const JE_integer maxMagAim = MAX(abs(aimX), abs(aimY));
									enemyShot[b].sxm = roundf((float)aimX / maxMagAim * aim);
									enemyShot[b].sym = roundf((float)aimY / maxMagAim * aim);
								}
							}
							break;
						}
					}
				}
			}

			/* Enemy Launch Routine */
			if (enemy[i].launchfreq)
			{
				if (--enemy[i].launchwait == 0)
				{
					enemy[i].launchwait = enemy[i].launchfreq;

					if (enemy[i].launchspecial != 0)
					{
						/*Type  1 : Must be inline with player*/
						if (abs(enemy[i].ey - player[0].y) > 5)
							goto draw_enemy_end;
					}

					if (enemy[i].aniactive == 2)
					{
						enemy[i].aniactive = 1;
					}

					if (enemy[i].launchtype == 0 || gbc_enemies_full())
						goto draw_enemy_end;

					tempW = enemy[i].launchtype;
					b = JE_newEnemy(enemyOffset == 50 ? 75 : enemyOffset - 25, tempW, 0);

					/*Launch Enemy Placement*/
					if (b > 0)
					{
						struct JE_SingleEnemyType* e = &enemy[b-1];

						e->ex = tempX;
						e->ey = tempY + enemyDat[e->enemytype].startyc;
						if (e->size == 0)
							e->ey -= 7;

						if (e->launchtype > 0 && e->launchfreq == 0)
						{
							if (e->launchtype > 90)
							{
								e->ex += mt_rand() % ((e->launchtype - 90) * 4) - (e->launchtype - 90) * 2;
							}
							else
							{
								JE_integer aimX = (player[0].x + 25) - tempX - tempMapXOfs - 4;
								if (aimX == 0)
									aimX = 1;
								JE_integer aimY = player[0].y - tempY;
								if (aimY == 0)
									aimY = 1;
								const JE_integer maxMagAim = MAX(abs(aimX), abs(aimY));
								e->exc = roundf((float)aimX / maxMagAim * e->launchtype);
								e->eyc = roundf((float)aimY / maxMagAim * e->launchtype);
							}
						}

						do
						{
							temp = mt_rand() % 8;
						} while (temp == 3);
						soundQueue[temp] = randomEnemyLaunchSounds[(mt_rand() % 3)];

						if (enemy[i].launchspecial == 1 &&
						    enemy[i].linknum < 100)
						{
							e->linknum = enemy[i].linknum;
						}
					}
				}
			}
		}
draw_enemy_end:
		;
	}

	player[0].x += 25;
}

// Tyrian3D: a mini-game's own weapons (script ]k[, episode 6's INVADERS, the user, 2026-11-04: "bonus level ... nebi
// trebao koristiti igračeva oružja"): the next level is flown with what the original's mini-games give (ENGAGE's: the
// Atomic RailGun and nothing else; the ship, its shield and generator its own), and the ship gets its own back before
// the next shop or level (kit_restore; a game loaded or begun forgets it).
static PlayerItems kit_backup;
static bool kit_saved = false, kit_this_level = false;

void JE_main(void)
{
	char buffer[256];

	int lastEnemyOnScreen;

	kit_saved = kit_this_level = false;
	custom_then_gbc = false;  // (a game begun or loaded: not Camanis 2 on its way to episode 7)

	/* NOTE: BEGIN MAIN PROGRAM HERE AFTER LOADING A GAME OR STARTING A NEW ONE */

	/* ----------- GAME ROUTINES ------------------------------------- */
	/* We need to jump to the beginning to make space for the routines */
	/* --------------------------------------------------------------- */
	goto start_level_first;

	/*------------------------------GAME LOOP-----------------------------------*/

	/* Startlevel is called after a previous level is over.  If the first level
	   is started for a gaming session, startlevelfirst is called instead and
	   this code is skipped.  The code here finishes the level and prepares for
	   the loadmap function. */

start_level:

	mouseSetRelative(false);

	if (galagaMode)
		twoPlayerMode = false;

	JE_clearKeyboard();

	free_sprite2s(&enemySpriteSheets[0]);
	free_sprite2s(&enemySpriteSheets[1]);
	free_sprite2s(&enemySpriteSheets[2]);
	free_sprite2s(&enemySpriteSheets[3]);

	/* Normal speed */
	if (fastPlay != 0)
	{
		smoothScroll = true;
		Uint16 speed = 0x4300;
		setDelaySpeed(speed);
	}

	if (play_demo || record_demo)
	{
		if (demo_file)
		{
			fclose(demo_file);
			demo_file = NULL;
		}

		if (play_demo)
		{
			moveTyrianLogoUp = true;
			stop_song();
			fade_black(10);

			wait_noinput(true, true, true);
		}
	}

	difficultyLevel = oldDifficultyLevel;   /*Return difficulty to normal*/

	printf("level over: %s, cash %lu\n", levelName, player[0].cash);  // Tyrian3D: for logs and sweeps

	// Tyrian3D: the debug flight rewinds by restarting the level (debugmode.h).
	if (debug_flight_restarting())
		goto start_level_first;

	// Tyrian3D: a rogue run picks the next level itself, or ends (rogue.h).
	if (rogue_run && !play_demo)
	{
		if (!rogue_level_over())
			return;
		goto start_level_first;
	}

	if (!play_demo)
	{
		if ((!all_players_dead() || normalBonusLevelCurrent || bonusLevelCurrent) && !playerEndLevel)
		{
			mainLevel = nextLevel;
			JE_endLevelAni();

			fade_song();
		}
		else
		{
			fade_song();
			fade_black(10);

			if (timedBattleMode)
			{
				mainLevel = 0;
				return;
			}

			JE_loadGame(twoPlayerMode ? 22 : 11);
			if (doNotSaveBackup)
			{
				superTyrian = false;
				onePlayerAction = false;
				player[0].items.super_arcade_mode = SA_NONE;
			}
			if (bonusLevelCurrent && !playerEndLevel)
			{
				mainLevel = nextLevel;
			}
		}
	}
	doNotSaveBackup = false;

	if (play_demo)
		return;

start_level_first:

	set_volume(tyrMusicVolume, fxVolume);

	endLevel = false;
	reallyEndLevel = false;
	playerEndLevel = false;
	extraGame = false;

	doNotSaveBackup = false;
	debug_flight_level_start();
	JE_loadMap();

	if (mainLevel == 0)  // if quit itemscreen
		return;          // back to titlescreen

	if (!play_demo)
		mouseSetRelative(true);

	fade_song();

	for (uint i = 0; i < COUNTOF(player); ++i)
		player[i].is_alive = true;

	oldDifficultyLevel = difficultyLevel;
	if (episodeNum == EPISODE_AVAILABLE)  // episode 5 (Tyrian3D: not episode 6, though it is the last)
		difficultyLevel--;
	if (difficultyLevel < DIFFICULTY_EASY)
		difficultyLevel = DIFFICULTY_EASY;

	player[0].x = 100;
	player[0].y = 180;

	player[1].x = 190;
	player[1].y = 180;

	assert(COUNTOF(player->old_x) == COUNTOF(player->old_y));

	for (uint i = 0; i < COUNTOF(player); ++i)
	{
		for (uint j = 0; j < COUNTOF(player->old_x); ++j)
		{
			player[i].old_x[j] = player[i].x - (19 - j);
			player[i].old_y[j] = player[i].y - 18;
		}
		
		player[i].last_x_shot_move = player[i].x;
		player[i].last_y_shot_move = player[i].y;
	}
	
	JE_loadPic(VGAScreen, twoPlayerMode ? 6 : 3, false);

	JE_drawOptions();

	JE_outText(VGAScreen, 268, twoPlayerMode ? 76 : 118, levelName, 12, 4);
	printf("level: %s (episode %d)\n", levelName, episodeNum);  // Tyrian3D: for logs and sweeps
	video_level_intro(true);  // Tyrian3D: no panel fading in with the modern HUD (video.h)
	JE_showVGA();
	JE_gammaCorrect(&colors, gammaCorrection);
	fade_palette(colors, 50, 0, 255);
	video_level_intro(false);

	if (explosionSpriteSheet.data == NULL)
		JE_loadCompShapes(&explosionSpriteSheet, '6');

	/* MAPX will already be set correctly */
	mapY = 300 - 8;
	mapY2 = 600 - 8;
	mapY3 = 600 - 8;
	mapYPos = &megaData1.mainmap[mapY][0] - 1;
	mapY2Pos = &megaData2.mainmap[mapY2][0] - 1;
	mapY3Pos = &megaData3.mainmap[mapY3][0] - 1;
	mapXPos = 0;
	mapXOfs = 0;
	mapX2Pos = 0;
	mapX3Pos = 0;
	mapX3Ofs = 0;
	mapXbpPos = 0;
	mapX2bpPos = 0;
	mapX3bpPos = 0;

	map1YDelay = 1;
	map1YDelayMax = 1;
	map2YDelay = 1;
	map2YDelayMax = 1;

	musicFade = false;

	backPos = 0;
	backPos2 = 0;
	backPos3 = 0;
	power = 0;
	starfield_speed = 1;

	/* Setup player ship graphics */
	JE_getShipInfo();

	for (uint i = 0; i < COUNTOF(player); ++i)
	{
		player[i].x_velocity = 0;
		player[i].y_velocity = 0;

		player[i].invulnerable_ticks = 100;
	}

	newkey = newmouse = false;

	/* Initialize Level Data and Debug Mode */
	levelEnd = 255;
	levelEndWarp = -4;
	levelEndFxWait = 0;
	warningCol = 120;
	warningColChange = 1;
	warningSoundDelay = 0;
	armorShipDelay = 50;

	bonusLevel = false;
	readyToEndLevel = false;
	firstGameOver = true;
	eventLoc = 1;
	curLoc = 0;
	backMove = 1;
	backMove2 = 2;
	backMove3 = 3;
	explodeMove = 2;
	enemiesActive = true;
	for (temp = 0; temp < 3; temp++)
	{
		button[temp] = false;
	}
	stopBackgrounds = false;
	stopBackgroundNum = 0;
	background3x1   = false;
	background3x1b  = false;
	background3over = 0;
	background2over = 1;
	topEnemyOver = false;
	skyEnemyOverAll = false;
	smallEnemyAdjust = false;
	starActive = true;
	enemyContinualDamage = false;
	levelEnemyFrequency = 96;
	quitRequested = false;

	for (unsigned int i = 0; i < COUNTOF(boss_bar); i++)
		boss_bar[i].link_num = 0;

	forceEvents = false;  /*Force events to continue if background movement = 0*/

	superEnemy254Jump = 0;   /*When Enemy with PL 254 dies*/

	/* Filter Status */
	filterActive = true;
	filterFade = true;
	filterFadeStart = false;
	levelFilter = -99;
	levelBrightness = -14;
	levelBrightnessChg = 1;

	background2notTransparent = false;

	uint old_weapon_bar[2] = { 0, 0 };  // only redrawn when they change

	/* Initially erase power bars */
	lastPower = power / 10;

	/* Initial Text */
	JE_drawTextWindow(miscText[20]);

	/* Setup Armor/Shield Data */
	shieldWait = 1;
	shieldT    = shields[player[0].items.shield].tpwr * 20;

	for (uint i = 0; i < COUNTOF(player); ++i)
	{
		player[i].shield     = shields[player[i].items.shield].mpwr;
		player[i].shield_max = player[i].shield * 2;
	}

	JE_drawShield();
	JE_drawArmor();

	for (uint i = 0; i < COUNTOF(player); ++i)
		player[i].superbombs = 0;
	dev_level_start_items();  // (Tyrian3D dev: TYR3D_BOMBS)

	/* Set cubes to 0 */
	cubeMax = 0;

	/* Secret Level Display */
	flash = 0;
	flashChange = 1;
	displayTime = 0;

	if (!gbc_music(false))  // (Tyrian3D: episode 7's GBC song)
		play_song(levelSong - 1);

	JE_drawPortConfigButtons();

	/* --- MAIN LOOP --- */

	newkey = false;

#ifdef WITH_NETWORK
	if (isNetworkGame)
	{
		JE_clearSpecialRequests();
		mt_srand(32402394);
	}
#endif

	initialize_starfield();

	JE_setNewGameSpeed();
	// Tyrian3D: episode 7's levels at the GBC's pace: its translation (tools/gbc/script.py) makes a GBC frame 0.375
	// ticks (its map's pixel every 4 frames the PC's pixel a tick), and the GBC shows 59.73 frames a second, so a
	// tick lasts 8/3 of its frames, 44.6 ms (the PC's Normal: 28.75): its map, enemies, shots and script as fast as
	// the GBC's (at 28.75 they went 1.55 times as fast).
	nortsong_tick_pace = episodeNum == EPISODE_GBC ? GBC_PACE : 1.0f;

	set_volume(tyrMusicVolume, fxVolume);

	/*Save backup game*/
	if (!play_demo && !doNotSaveBackup && !timedBattleMode)
	{
		temp = twoPlayerMode ? 22 : 11;
		JE_saveGame(temp, "LAST LEVEL    ");
	}

	if (!play_demo && record_demo)
	{
		Uint8 new_demo_num = 0;

		do
		{
			sprintf(tempStr, "demorec.%d", new_demo_num++);
		} while (dir_file_exists(get_user_directory(), tempStr)); // until file doesn't exist

		demo_file = dir_fopen_warn(get_user_directory(), tempStr, "wb");
		if (!demo_file)
			exit(1);

		fwrite_u8_die(&episodeNum, 1, demo_file);

		// Pad string buffer with NULs.
		for (size_t i = 1; i < 10; ++i)
			if (levelName[i - 1] == '\0')
				levelName[i] = '\0';
		fwrite_u8_die((Uint8 *)levelName, 10, demo_file);

		fwrite_u8_die(&lvlFileNum, 1, demo_file);

		fwrite_u8_die(&player[0].items.weapon[FRONT_WEAPON].id,  1, demo_file);
		fwrite_u8_die(&player[0].items.weapon[REAR_WEAPON].id,   1, demo_file);
		fwrite_u8_die(&player[0].items.super_arcade_mode,        1, demo_file);
		fwrite_u8_die(&player[0].items.sidekick[LEFT_SIDEKICK],  1, demo_file);
		fwrite_u8_die(&player[0].items.sidekick[RIGHT_SIDEKICK], 1, demo_file);
		fwrite_u8_die(&player[0].items.generator,                1, demo_file);

		fwrite_u8_die(&player[0].items.sidekick_level,           1, demo_file);
		fwrite_u8_die(&player[0].items.sidekick_series,          1, demo_file);

		fwrite_u8_die(&initial_episode_num,                      1, demo_file);

		fwrite_u8_die(&player[0].items.shield,                   1, demo_file);
		fwrite_u8_die(&player[0].items.special,                  1, demo_file);
		fwrite_u8_die(&player[0].items.ship,                     1, demo_file);

		for (uint i = 0; i < 2; ++i)
			fwrite_u8_die(&player[0].items.weapon[i].power,      1, demo_file);

		Uint8 unused[3] = { 0, 0, 0 };
		fwrite_u8_die(unused, 3, demo_file);

		fwrite_u8_die(&levelSong, 1, demo_file);

		demo_keys = 0;
		demo_keys_wait = 0;
	}

	twoPlayerLinked = false;
	linkGunDirec = M_PI;

	for (uint i = 0; i < COUNTOF(player); ++i)
		calc_purple_balls_needed(&player[i]);

	damageRate = 2;  /*Normal Rate for Collision Damage*/

	chargeWait   = 5;
	chargeLevel  = 0;
	chargeMax    = 5;
	chargeGr     = 0;
	chargeGrWait = 3;

	portConfigChange = false;

	/*Destruction Ratio*/
	totalEnemy = 0;
	enemyKilled = 0;

	astralDuration = 0;

	superArcadePowerUp = 1;

	yourInGameMenuRequest = false;

	constantLastX = -1;

	for (uint i = 0; i < COUNTOF(player); ++i)
		player[i].exploding_ticks = 0;

	if (isNetworkGame)
	{
		JE_loadItemDat();
	}

	memset(enemyAvail,       1, sizeof(enemyAvail));
	for (uint i = 0; i < COUNTOF(enemyShotAvail); i++)
		enemyShotAvail[i] = 1;

	/*Initialize Shots*/
	memset(playerShotData,   0, sizeof(playerShotData));
	memset(shotAvail,        0, sizeof(shotAvail));
	memset(shotMultiPos,     0, sizeof(shotMultiPos));
	memset(shotRepeat,       1, sizeof(shotRepeat));

	memset(button,           0, sizeof(button));

	memset(globalFlags,      0, sizeof(globalFlags));

	memset(explosions,       0, sizeof(explosions));
	memset(rep_explosions,   0, sizeof(rep_explosions));

	/* --- Clear Sound Queue --- */
	memset(soundQueue,       0, sizeof(soundQueue));
	soundQueue[3] = V_GOOD_LUCK;

	memset(enemySpriteSheetIds, 0, sizeof(enemySpriteSheetIds));
	memset(enemy,               0, sizeof(enemy));

	memset(SFCurrentCode,    0, sizeof(SFCurrentCode));
	memset(SFExecuted,       0, sizeof(SFExecuted));

	zinglonDuration = 0;
	specialWait = 0;
	nextSpecialWait = 0;
	optionAttachmentMove  = 0;    /*Launch the Attachments!*/
	optionAttachmentLinked = true;

	editShip1 = false;
	editShip2 = false;

	memset(smoothies, 0, sizeof(smoothies));
	l3d_level_frame = l3d_frame_number;
	l3d_sideways = SDL_getenv("TYR3D_SIDEWAYS") != NULL;  // (dev: any level from the side)
	l3d_side_decor = l3d_sideways ? SDL_atoi(SDL_getenv("TYR3D_SIDEWAYS")) - 1 : 0;
	l3d_chase = SDL_getenv("TYR3D_CHASE") != NULL;  // (dev: any level from behind the ship)
	// (not for the demos: they replay inputs on the original playfield)
	l3d_field_wide = debug_flight_field_wide(settings3d.view_3d && settings3d.playfield_wide && !isNetworkGame &&
	                                         !play_demo && !record_demo);
	l3d_field_ahead = l3d_field_wide ? WIDE_AHEAD : 0;
	memset(prespawned, 0, sizeof(prespawned));

	levelTimer = false;
	randomExplosions = false;

	last_superpixel = 0;
	memset(superpixels, 0, sizeof(superpixels));

	returnActive = false;

	galagaShotFreq = 0;

	if (galagaMode)
	{
		difficultyLevel = DIFFICULTY_NORMAL;
	}
	galagaLife = 10000;

	JE_drawOptionLevel();

	// keeps map from scrolling past the top
	BKwrap1 = BKwrap1to = &megaData1.mainmap[1][0];
	BKwrap2 = BKwrap2to = &megaData2.mainmap[1][0];
	BKwrap3 = BKwrap3to = &megaData3.mainmap[1][0];

level_loop:
		debug_flight_tick();
		dev_level_tick();

	// Tyrian3D: the wait the 3D view moved here from JE_starShowVGA, before input is read.
	if (wait_at_tick_start)
	{
		wait_at_tick_start = false;
		video_wait_tick_3d();
		setTickDelayContinued(frameCountMax);
	}

	//tempScreenSeg = game_screen; /* side-effect of game_screen */

	if (isNetworkGame)
	{
		smoothies[9-1] = false;
		smoothies[6-1] = false;
	}
	else
	{
		starShowVGASpecialCode = smoothies[9-1] + (smoothies[6-1] << 1);
	}

	/*Background Wrapping*/
	if (mapYPos <= BKwrap1)
		mapYPos = BKwrap1to;
	if (mapY2Pos <= BKwrap2)
		mapY2Pos = BKwrap2to;
	if (mapY3Pos <= BKwrap3)
		mapY3Pos = BKwrap3to;

	allPlayersGone = all_players_dead() &&
	                 ((*player[0].lives == 1 && player[0].exploding_ticks == 0) || (!onePlayerAction && !twoPlayerMode)) &&
	                 ((*player[1].lives == 1 && player[1].exploding_ticks == 0) || !twoPlayerMode ||
	                  twin_stick());  // (Tyrian3D: the twin-stick turret goes with the ship's last life)

	/*-----MUSIC FADE------*/
	if (musicFade)
	{
		if (tempVolume > 10)
		{
			tempVolume--;
			set_volume(tempVolume, fxVolume);
		}
		else
		{
			musicFade = false;
		}
	}

	if (!allPlayersGone && levelEnd > 0 && endLevel)
	{
		play_song(9);
		musicFade = false;
	}
	else if (!playing && firstGameOver && !gbc_song_plays)  // (Tyrian3D: not over episode 7's, which never stop)
	{
		play_song(levelSong - 1);
	}
	else if (gbc_song_plays)
	{
		follow_recorded_song();  // (Tyrian3D: the music gone between MIDI and the chip in the options)
	}

	if (!endLevel) // draw HUD
	{
		VGAScreen = VGAScreenSeg; /* side-effect of game_screen */

		/*-----------------------Message Bar------------------------*/
		if (textErase > 0 && --textErase == 0)
			blit_sprite(VGAScreenSeg, 16, 189, OPTION_SHAPES, 36);  // in-game message area

		/*------------------------Shield Gen-------------------------*/
		if (galagaMode)
		{
			for (uint i = 0; i < COUNTOF(player); ++i)
				player[i].shield = 0;

			// spawned dragonwing died :(
			if (*player[1].lives == 0 || player[1].armor == 0)
				twoPlayerMode = false;

			if (player[0].cash >= (unsigned)galagaLife)
			{
				soundQueue[6] = S_EXPLOSION_11;
				soundQueue[7] = S_SOUL_OF_ZINGLON;

				if (*player[0].lives < 11)
					++(*player[0].lives);
				else
					player[0].cash += 1000;

				if (galagaLife == 10000)
					galagaLife = 20000;
				else
					galagaLife += 25000;
			}
		}
		else // not galagaMode
		{
			if (twoPlayerMode)
			{
				if (--shieldWait == 0)
				{
					shieldWait = 15;

					for (uint i = 0; i < COUNTOF(player); ++i)
					{
						if (player[i].shield < player[i].shield_max && player[i].is_alive)
							++player[i].shield;
					}

					JE_drawShield();
				}
			}
			else if (player[0].is_alive && player[0].shield < player[0].shield_max && power > shieldT)
			{
				if (--shieldWait == 0)
				{
					shieldWait = 15;

					power -= shieldT;

					++player[0].shield;
					if (player[1].shield < player[0].shield_max)
						++player[1].shield;

					JE_drawShield();
				}
			}
		}

		/*---------------------Weapon Display-------------------------*/
		for (uint i = 0; i < 2; ++i)
		{
			uint item_power = player[twoPlayerMode ? i : 0].items.weapon[i].power;

			if (old_weapon_bar[i] != item_power)
			{
				old_weapon_bar[i] = item_power;

				int x = twoPlayerMode ? 286 : 289,
				    y = (i == 0) ? (twoPlayerMode ? 6 : 17) : (twoPlayerMode ? 100 : 38);

				fill_rectangle_xy(VGAScreenSeg, x, y, x + 1 + (WEAPON_POWER_OVERCLOCK - 1) * 2, y + 2, 0);  // (Tyrian3D: to 15)

				for (uint j = 1; j <= item_power; ++j)
				{
					JE_rectangle(VGAScreen, x, y, x + 1, y + 2, 115 + j); /* SEGa000 */
					x += 2;
				}
			}
		}

		/*------------------------Power Bar-------------------------*/
		if (twoPlayerMode || onePlayerAction)
		{
			power = 900;
		}
		else
		{
			power += powerAdd;
			if (power > 900)
				power = 900;

			temp = power / 10;

			if (temp != lastPower)
			{
				if (temp > lastPower)
					fill_rectangle_xy(VGAScreenSeg, 269, 113 - 11 - temp, 276, 114 - 11 - lastPower, 113 + temp / 7);
				else
					fill_rectangle_xy(VGAScreenSeg, 269, 113 - 11 - lastPower, 276, 114 - 11 - temp, 0);
				
				lastPower = temp;
			}
		}

		oldMapX3Ofs = mapX3Ofs;

		enemyOnScreen = 0;
	}

	/* use game_screen for all the generic drawing functions */
	VGAScreen = game_screen;

	/*---------------------------EVENTS-------------------------*/
	prespawn_events();
	voiceover_update();  // (Tyrian3D: a data cube picked up, read aloud: voiceover_cube_found)
	while (eventRec[eventLoc-1].eventtime <= curLoc && eventLoc <= maxEvent)
	{
		if (prespawned[eventLoc-1])
		{
			prespawned[eventLoc-1] = false;  // (done ahead of time; again if a jump brings it round)
			eventLoc++;
			continue;
		}
		JE_eventSystem();
	}

	// Tyrian3D dev: TYR3D_LOG_MOVES prints every enemy each tick as the events leave it (where, how fast, carried
	// how far, its link): to set its paths against another's (tools/gbc: the GBC's).
	if (SDL_getenv("TYR3D_LOG_MOVES") != NULL)
		for (int i = 0; i < 100; i++)
			if (enemyAvail[i] != 1)
				printf("move: clock %u slot %d enemy %u at %d,%d moving %d,%d+%d steer %d,%d link %d\n", (unsigned)curLoc, i,
				       enemy[i].enemytype, enemy[i].ex, enemy[i].ey, enemy[i].exc, enemy[i].eyc, enemy[i].fixedmovey,
				       enemy[i].xaccel, enemy[i].yaccel, enemy[i].linknum);

	if (isNetworkGame && reallyEndLevel)
		goto start_level;

	/* SMOOTHIES! */
	JE_checkSmoothies();
	if (anySmoothies)
		VGAScreen = VGAScreen2;  // this makes things complicated, but we do it anyway :(

	/* --- BACKGROUNDS --- */
	/* --- BACKGROUND 1 --- */

	if (forceEvents && !backMove)
		curLoc++;

	if (map1YDelayMax > 1 && backMove < 2)
		backMove = (map1YDelay == 1) ? 1 : 0;

	/*Draw background*/
	l3d_frame_begin(L3D_GROUND);
	if (astralDuration == 0)
		draw_background_1(VGAScreen);
	else
	{
		JE_clr256(VGAScreen);
		// (Tyrian3D: the rows above the screen too, which the 3D view shows: else the Astral Zone's space had a band
		// of the last ground drawn there across its top, flat and at the screen's size)
		memset(surface_pixels_ll(VGAScreen), 0, (size_t)(-surface_top(VGAScreen)) * VGAScreen->pitch);
	}

	/*Set Movement of background 1*/
	if (--map1YDelay == 0)
	{
		map1YDelay = map1YDelayMax;

		curLoc += backMove;

		backPos += backMove;

		if (backPos > 27)
		{
			backPos -= 28;
			mapY--;
			mapYPos -= 14;  /*Map Width*/
		}
	}

	if (starActive || astralDuration > 0)
		update_and_draw_starfield(VGAScreen, starfield_speed);

	if (processorType > 1 && smoothies[5-1])
	{
		l3d_modify();
		iced_blur_filter(game_screen, VGAScreen);
		VGAScreen = game_screen;
	}

	/*-----------------------BACKGROUNDS------------------------*/
	/*-----------------------BACKGROUND 2------------------------*/
	l3d_phase(L3D_BG2_LOW);
	if (background2over == 3)
	{
		draw_background_2(VGAScreen);
		background2 = true;
	}

	if (background2over == 0)
	{
		if (!(smoothies[2-1] && processorType < 4) && !(smoothies[1-1] && processorType == 3))
		{
			if (wild && !background2notTransparent)
				draw_background_2_blend(VGAScreen);
			else
				draw_background_2(VGAScreen);
		}
	}

	if (smoothies[0] && processorType > 2 && smoothie_data[0] == 0)
	{
		l3d_modify();
		lava_filter(game_screen, VGAScreen);
		VGAScreen = game_screen;
	}
	if (smoothies[2-1] && processorType > 2)
	{
		l3d_modify();
		water_filter(game_screen, VGAScreen);
		VGAScreen = game_screen;
	}

	/*-----------------------Ground Enemy------------------------*/
	l3d_phase(L3D_GROUND_ENEMY);
	lastEnemyOnScreen = enemyOnScreen;

	tempMapXOfs = mapXOfs;
	tempBackMove = backMove;
	JE_drawEnemy(50);
	JE_drawEnemy(100);
	draw_coming_enemies(25);
	draw_coming_enemies(75);
	draw_standins(1);

	if (enemyOnScreen == 0 || enemyOnScreen == lastEnemyOnScreen)
	{
		if (stopBackgroundNum == 1)
			stopBackgroundNum = 9;
	}

	if (smoothies[0] && processorType > 2 && smoothie_data[0] > 0)
	{
		l3d_modify();
		lava_filter(game_screen, VGAScreen);
		VGAScreen = game_screen;
	}

	if (superWild)
	{
		neat += 3;
		l3d_modify();
		JE_darkenBackground(neat);
	}

	/*-----------------------BACKGROUNDS------------------------*/
	/*-----------------------BACKGROUND 2------------------------*/
	l3d_phase(L3D_BG2);
	if (!(smoothies[2-1] && processorType < 4) &&
	    !(smoothies[1-1] && processorType == 3))
	{
		if (background2over == 1)
		{
			if (wild && !background2notTransparent)
				draw_background_2_blend(VGAScreen);
			else
				draw_background_2(VGAScreen);
		}
	}

	if (superWild)
	{
		neat++;
		l3d_modify();
		JE_darkenBackground(neat);
	}

	l3d_phase(L3D_BG3_LOW);  // (Tyrian3D: drawn here, under the sky enemies, it stands below them in 3D)
	if (background3over == 2)
		draw_background_3(VGAScreen);

	/* New Enemy */
	if (enemiesActive && mt_rand() % 100 > levelEnemyFrequency)
	{
		tempW = levelEnemy[mt_rand() % levelEnemyMax];
		if (tempW == 2)
			soundQueue[3] = S_WEAPON_7;
		b = JE_newEnemy(0, tempW, 0);
		// (Tyrian3D: on a playfield reaching above the screen, one coming down from the screen's
		// top comes from the playfield's, rather than appearing in it)
		if (b > 0 && l3d_field_ahead > 0 && enemy[b-1].ey < 0 && enemy[b-1].eyc > 0)
			enemy[b-1].ey -= l3d_field_ahead;
	}

	if (processorType > 1 && smoothies[3-1])
	{
		l3d_modify();
		iced_blur_filter(game_screen, VGAScreen);
		VGAScreen = game_screen;
	}
	if (processorType > 1 && smoothies[4-1])
	{
		l3d_modify_blur();
		blur_filter(game_screen, VGAScreen);
		VGAScreen = game_screen;
	}

	/* Draw Sky Enemy */
	l3d_phase(L3D_SKY_ENEMY);
	if (!skyEnemyOverAll)
	{
		lastEnemyOnScreen = enemyOnScreen;

		tempMapXOfs = mapX2Ofs;
		tempBackMove = 0;
		JE_drawEnemy(25);
		draw_coming_enemies(0);

		if (enemyOnScreen == lastEnemyOnScreen)
		{
			if (stopBackgroundNum == 2)
				stopBackgroundNum = 9;
		}
	}

	l3d_phase(L3D_BG3);
	if (background3over == 0)
		draw_background_3(VGAScreen);

	/* Draw Top Enemy */
	l3d_phase(L3D_TOP_ENEMY);
	if (!topEnemyOver)
	{
		tempMapXOfs = (background3x1 == 0) ? oldMapX3Ofs : mapXOfs;
		tempBackMove = backMove3;
		JE_drawEnemy(75);
		draw_standins(3);  // Tyrian3D: what stands in for background 3's painted objects
		draw_coming_enemies(50);
	}

	l3d_phase(L3D_PLAYER);
	l3d_draw_departed_shots();  // Tyrian3D

	/* Player Shot Images */
	for (int z = 0; z < MAX_PWEAPON; z++)
	{
		if (shotAvail[z] != 0)
		{
			bool is_special = false;
			int tempShotX = 0, tempShotY = 0;
			JE_byte chain;
			JE_byte playerNum;
			JE_word tempX2, tempY2;
			JE_integer damage;
			
			if (!player_shot_move_and_draw(z, &is_special, &tempShotX, &tempShotY, &damage, &temp2, &chain, &playerNum, &tempX2, &tempY2))
			{
				goto draw_player_shot_loop_end;
			}

			for (b = 0; b < 100; b++)
			{
				if (enemyAvail[b] == 0)
				{
					bool collided;

					if (z == MAX_PWEAPON - 1)
					{
						temp = 25 - abs(zinglonDuration - 25);
						collided = abs(enemy[b].ex + enemy[b].mapoffset - (player[0].x + 7)) < temp;
						temp2 = 9;
						chain = 0;
						damage = 10;
					}
					else if (is_special)
					{
						collided = ((enemy[b].enemycycle == 0) &&
						            (abs(enemy[b].ex + enemy[b].mapoffset - tempShotX - tempX2) < (25 + tempX2)) &&
						            (abs(enemy[b].ey - tempShotY - 12 - tempY2)                 < (29 + tempY2))) ||
						           ((enemy[b].enemycycle > 0) &&
						            (abs(enemy[b].ex + enemy[b].mapoffset - tempShotX - tempX2) < (13 + tempX2)) &&
						            (abs(enemy[b].ey - tempShotY - 6 - tempY2)                  < (15 + tempY2)));
					}
					else
					{
						collided = ((enemy[b].enemycycle == 0) &&
						            (abs(enemy[b].ex + enemy[b].mapoffset - tempShotX) < 25) && (abs(enemy[b].ey - tempShotY - 12) < 29)) ||
						           ((enemy[b].enemycycle > 0) &&
						            (abs(enemy[b].ex + enemy[b].mapoffset - tempShotX) < 13) && (abs(enemy[b].ey - tempShotY - 6) < 15));
					}

					if (collided)
					{
						if (chain > 0)
						{
							shotMultiPos[SHOT_MISC] = 0;
							b = player_shot_create(0, SHOT_MISC, tempShotX, tempShotY, mouseX, mouseY, chain, playerNum);
							shotAvail[z] = 0;
							goto draw_player_shot_loop_end;
						}

						infiniteShot = false;

						if (damage == 99)
						{
							damage = 0;
							doIced = 40;
							enemy[b].iced = 40;
						}
						else
						{
							doIced = 0;
							if (damage >= 250)
							{
								damage = damage - 250;
								infiniteShot = true;
							}
						}

						int armorleft = enemy[b].armorleft;
						// (Tyrian3D: a GBC boss's piece: its body's, gbc_pool_hit)
						const bool pooled = gbc_in_pool(b) && armorleft < 255;
						if (pooled)
							armorleft = gbc_pool_left();

						temp = enemy[b].linknum;
						if (temp == 0)
							temp = 255;

						if (enemy[b].armorleft < 255)
						{
							for (unsigned int i = 0; i < COUNTOF(boss_bar); i++)
								if (temp == boss_bar[i].link_num || (pooled && gbc_piece_link(boss_bar[i].link_num)))
									boss_bar[i].color = 6;

							if (enemy[b].enemyground)
								enemy[b].filter = temp2;

							for (unsigned int e = 0; e < COUNTOF(enemy); e++)
							{
								if (enemy[e].linknum == temp &&
								    enemyAvail[e] != 1 &&
								    enemy[e].enemyground != 0)
								{
									if (doIced)
										enemy[e].iced = doIced;
									enemy[e].filter = temp2;
								}
							}
						}

						if (armorleft > damage)
						{
							if (z != MAX_PWEAPON - 1)
							{
								if (enemy[b].armorleft != 255)
								{
									if (pooled)
										gbc_pool_hit(b, damage);
									else
										enemy[b].armorleft -= damage;
									JE_setupExplosion(tempShotX, tempShotY, 0, 0, false, false);
								}
								else
								{
									JE_doSP(tempShotX + 6, tempShotY + 6, damage / 2 + 3, damage / 4 + 2, temp2);
								}
							}

							soundQueue[5] = S_ENEMY_HIT;

							if (!pooled && (armorleft - damage <= enemy[b].edlevel) &&  // (a body's pieces go whole)
							    ((!enemy[b].edamaged) ^ (enemy[b].edani < 0)))
							{

								for (temp3 = 0; temp3 < 100; temp3++)
								{
									if (enemyAvail[temp3] != 1)
									{
										int linknum = enemy[temp3].linknum;
										if (
										     (temp3 == b) ||
										     (
										       (temp != 255) && gbc_takes_along(temp, b, temp3) &&
										       (
										         ((enemy[temp3].edlevel > 0) && (linknum == temp)) ||
										         (
										           (enemyContinualDamage && (temp - 100 == linknum)) ||
										           ((linknum > 40) && (linknum / 20 == temp / 20) && (linknum <= temp))
										         )
										       )
										     )
										   )
										{
											enemy[temp3].enemycycle = 1;

											enemy[temp3].edamaged = !enemy[temp3].edamaged;

											if (enemy[temp3].edani != 0)
											{
												enemy[temp3].ani = abs(enemy[temp3].edani);
												enemy[temp3].aniactive = 1;
												enemy[temp3].animax = 0;
												enemy[temp3].animin = enemy[temp3].edgr;
												enemy[temp3].enemycycle = enemy[temp3].animin - 1;

											}
											else if (enemy[temp3].edgr > 0)
											{
												enemy[temp3].egr[1-1] = enemy[temp3].edgr;
												enemy[temp3].ani = 1;
												enemy[temp3].aniactive = 0;
												enemy[temp3].animax = 0;
												enemy[temp3].animin = 1;
											}
											else
											{
												enemyAvail[temp3] = 1;
												enemyKilled++;
												dev_balance("kill", temp3);  // Tyrian3D dev
											}

											enemy[temp3].aniwhenfire = 0;

											if (enemy[temp3].armorleft > (unsigned char)enemy[temp3].edlevel)
												enemy[temp3].armorleft = enemy[temp3].edlevel;

											JE_integer tempX = enemy[temp3].ex + enemy[temp3].mapoffset;
											JE_integer tempY = enemy[temp3].ey;

											if (enemyDat[enemy[temp3].enemytype].esize != 1)
												JE_setupExplosion(tempX, tempY - 6, 0, 1, false, false);
											else
												JE_setupExplosionLarge(enemy[temp3].enemyground, enemy[temp3].explonum / 2, tempX, tempY);
										}
									}
								}
							}
						}
						else
						{
							if (pooled)
								gbc_pool_hit(b, damage);  // (the body gone: all its pieces go, gbc_pool_takes)

							if ((temp == 254) && (superEnemy254Jump > 0))
								JE_eventJump(superEnemy254Jump);

							for (temp2 = 0; temp2 < 100; temp2++)
							{
								if (enemyAvail[temp2] != 1)
								{
									temp3 = enemy[temp2].linknum;
									if ((temp2 == b) || (temp == 254) || gbc_pool_takes(b, temp2) ||
									    ((temp != 255) && gbc_takes_along(temp, b, temp2) && ((temp == temp3) || (temp - 100 == temp3) ||
									                       ((temp3 > 40) && (temp3 / 20 == temp / 20) && (temp3 <= temp)))))
									{

										int enemy_screen_x = enemy[temp2].ex + enemy[temp2].mapoffset;

										if (enemy[temp2].special)
										{
											assert((unsigned int) enemy[temp2].flagnum-1 < COUNTOF(globalFlags));
											globalFlags[enemy[temp2].flagnum-1] = enemy[temp2].setto;
										}

										if ((enemy[temp2].enemydie > 0) &&
										    !((superArcadeMode != SA_NONE) &&
										      (enemyDat[enemy[temp2].enemydie].value == 30000)))
										{
											int temp_b = b;
											tempW = enemy[temp2].enemydie;
											int enemy_offset = temp2 - (temp2 % 25);
											if (enemyDat[tempW].value > 30000)
											{
												enemy_offset = 0;
											}
											b = JE_newEnemy(enemy_offset, tempW, 0);
											dev_balance(b != 0 ? "drop" : "droplost", enemyDat[tempW].value);  // Tyrian3D dev
											if (b != 0)
											{
												enemy_group[b-1] = enemy_group[temp2];  // (Tyrian3D: in its place)
												enemy_group_link[b-1] = enemy_group_link[temp2];
												if ((superArcadeMode != SA_NONE) && (enemy[b-1].evalue > 30000))
												{
													superArcadePowerUp++;
													if (superArcadePowerUp > 5)
														superArcadePowerUp = 1;
													enemy[b-1].egr[1-1] = 5 + superArcadePowerUp * 2;
													enemy[b-1].evalue = 30000 + superArcadePowerUp;
												}

												if (enemy[b-1].evalue != 0)
													enemy[b-1].scoreitem = true;
												else
													enemy[b-1].scoreitem = false;

												enemy[b-1].ex = enemy[temp2].ex;
												enemy[b-1].ey = enemy[temp2].ey;
											}
											b = temp_b;
										}

										if ((enemy[temp2].evalue > 0) && (enemy[temp2].evalue < 10000))
										{
											if (enemy[temp2].evalue == 1)
											{
												cubeMax++;
												cube_picked_up();  // (Tyrian3D: read aloud)
											}
											else
											{
												// in galaga mode player 2 is sidekick, so give cash to player 1
												player[galagaMode ? 0 : playerNum - 1].cash += enemy[temp2].evalue;
											}
										}

										if ((enemy[temp2].edlevel == -1) && (temp == temp3))
										{
											enemy[temp2].edlevel = 0;
											enemyAvail[temp2] = 2;
											enemy[temp2].egr[1-1] = enemy[temp2].edgr;
											enemy[temp2].ani = 1;
											enemy[temp2].aniactive = 0;
											enemy[temp2].animax = 0;
											enemy[temp2].animin = 1;
											enemy[temp2].edamaged = true;
											enemy[temp2].enemycycle = 1;
										}
										else
										{
											enemyAvail[temp2] = 1;
											enemyKilled++;
											dev_balance("kill", temp2);  // Tyrian3D dev
										}

										if (enemyDat[enemy[temp2].enemytype].esize == 1)
										{
											JE_setupExplosionLarge(enemy[temp2].enemyground, enemy[temp2].explonum, enemy_screen_x, enemy[temp2].ey);
											soundQueue[6] = S_EXPLOSION_9;
										}
										else
										{
											JE_setupExplosion(enemy_screen_x, enemy[temp2].ey, 0, 1, false, false);
											soundQueue[6] = S_EXPLOSION_8;
										}
									}
								}
							}
						}

						if (infiniteShot)
						{
							damage += 250;
						}
						else if (z != MAX_PWEAPON - 1)
						{
							if (damage <= armorleft)
							{
								shotAvail[z] = 0;
								goto draw_player_shot_loop_end;
							}
							else
							{
								playerShotData[z].shotDmg -= armorleft;
							}
						}
					}
				}
			}

draw_player_shot_loop_end:
			;
		}
	}

	/* Player movement indicators for shots that track your ship */
	for (uint i = 0; i < COUNTOF(player); ++i)
	{
		player[i].last_x_shot_move = player[i].x;
		player[i].last_y_shot_move = player[i].y;
	}
	
	/*=================================*/
	/*=======Collisions Detection======*/
	/*=================================*/
	
	for (uint i = 0; i < (twoPlayerMode ? 2 : 1); ++i)
		if (player[i].is_alive && !endLevel)
			JE_playerCollide(&player[i], i + 1);
	
	if (firstGameOver)
		JE_mainGamePlayerFunctions();      /*--------PLAYER DRAW+MOVEMENT---------*/

	if (!endLevel)
	{    /*MAIN DRAWING IS STOPPED STARTING HERE*/

		/* Draw Enemy Shots */
		for (int z = 0; z < ENEMY_SHOT_MAX; z++)
		{
			if (enemyShotAvail[z] == 0)
			{
				enemyShot[z].sxm += enemyShot[z].sxc;
				enemyShot[z].sx += enemyShot[z].sxm;

				if (enemyShot[z].tx != 0)
				{
					if (enemyShot[z].sx > player[0].x)
					{
						if (enemyShot[z].sxm > -enemyShot[z].tx)
							enemyShot[z].sxm--;
					}
					else
					{
						if (enemyShot[z].sxm < enemyShot[z].tx)
							enemyShot[z].sxm++;
					}
				}

				enemyShot[z].sym += enemyShot[z].syc;
				enemyShot[z].sy += enemyShot[z].sym;

				if (enemyShot[z].ty != 0)
				{
					if (enemyShot[z].sy > player[0].y)
					{
						if (enemyShot[z].sym > -enemyShot[z].ty)
							enemyShot[z].sym--;
					}
					else
					{
						if (enemyShot[z].sym < enemyShot[z].ty)
							enemyShot[z].sym++;
					}
				}

				if (enemyShot[z].duration-- == 0 || enemyShot[z].sy > 190 || enemyShot[z].sy <= -14 - l3d_field_ahead || enemyShot[z].sx > 275 + l3d_field_right() || enemyShot[z].sx <= -l3d_field_left())
				{
					enemyShotAvail[z] = true;
				}
				else  // check if shot collided with player
				{
					for (uint i = 0; i < (twoPlayerMode ? 2 : 1); ++i)
					{
						if (player[i].is_alive && !(i == 1 && twin_stick()) &&  // (Tyrian3D: the twin-stick turret isn't hit)
						    enemyShot[z].sx > player[i].x - (signed)player[i].shot_hit_area_x &&
						    enemyShot[z].sx < player[i].x + (signed)player[i].shot_hit_area_x &&
						    enemyShot[z].sy > player[i].y - (signed)player[i].shot_hit_area_y &&
						    enemyShot[z].sy < player[i].y + (signed)player[i].shot_hit_area_y)
						{
							JE_integer tempX = enemyShot[z].sx;
							JE_integer tempY = enemyShot[z].sy;
							temp = enemyShot[z].sdmg;

							enemyShotAvail[z] = true;

							JE_setupExplosion(tempX, tempY, 0, 0, false, false);

							if (player[i].invulnerable_ticks == 0)
							{
								dev_balance("hit", shot_from[z]);  // Tyrian3D dev
								if ((temp = JE_playerDamage(temp, &player[i])) > 0)
								{
									player[i].x_velocity += (enemyShot[z].sxm * temp) / 2;
									player[i].y_velocity += (enemyShot[z].sym * temp) / 2;
								}
							}

							break;
						}
					}

					if (enemyShotAvail[z] == false)
					{
						if (enemyShot[z].animax != 0)
						{
							if (++enemyShot[z].animate >= enemyShot[z].animax)
								enemyShot[z].animate = 0;
						}

						// Tyrian3D: in 3D a flat volume with its glow, moving on between ticks.
						if (enemyShot[z].sgr >= 500)
						{
							const unsigned int sprite = enemyShot[z].sgr + enemyShot[z].animate - 500;
							if (!l3d_add_shot(&spriteSheet12, sprite, enemyShot[z].sx, enemyShot[z].sy, enemyShot[z].sxm,
							                  enemyShot[z].sym, true, L3D_KEY_ENEMY_SHOT + z))
							{
								blit_sprite2(VGAScreen, enemyShot[z].sx, enemyShot[z].sy, spriteSheet12, sprite);
								l3d_add_glow(&spriteSheet12, sprite, enemyShot[z].sx, enemyShot[z].sy);
							}
						}
						else
						{
							const unsigned int sprite = enemyShot[z].sgr + enemyShot[z].animate;
							if (!l3d_add_shot(&spriteSheet8, sprite, enemyShot[z].sx, enemyShot[z].sy, enemyShot[z].sxm,
							                  enemyShot[z].sym, true, L3D_KEY_ENEMY_SHOT + z))
							{
								blit_sprite2(VGAScreen, enemyShot[z].sx, enemyShot[z].sy, spriteSheet8, sprite);
								l3d_add_glow(&spriteSheet8, sprite, enemyShot[z].sx, enemyShot[z].sy);
							}
						}
					}
				}

			}
		}
	}

	l3d_phase(L3D_BG3_OVER);
	if (background3over == 1)
		draw_background_3(VGAScreen);

	/* Draw Top Enemy */
	l3d_phase(L3D_TOP_ENEMY);
	if (topEnemyOver)
	{
		tempMapXOfs = (background3x1 == 0) ? oldMapX3Ofs : oldMapXOfs;
		tempBackMove = backMove3;
		JE_drawEnemy(75);
		draw_standins(3);
		draw_coming_enemies(50);
	}

	/* Draw Sky Enemy */
	l3d_phase(L3D_SKY_ENEMY);
	if (skyEnemyOverAll)
	{
		lastEnemyOnScreen = enemyOnScreen;

		tempMapXOfs = mapX2Ofs;
		tempBackMove = 0;
		JE_drawEnemy(25);
		draw_coming_enemies(0);

		if (enemyOnScreen == lastEnemyOnScreen)
		{
			if (stopBackgroundNum == 2)
				stopBackgroundNum = 9;
		}
	}

	/*-------------------------- Sequenced Explosions -------------------------*/
	enemyStillExploding = false;
	for (int i = 0; i < MAX_REPEATING_EXPLOSIONS; i++)
	{
		if (rep_explosions[i].ttl != 0)
		{
			enemyStillExploding = true;

			if (rep_explosions[i].delay > 0)
			{
				rep_explosions[i].delay--;
				continue;
			}

			rep_explosions[i].y += backMove2 + 1;
			JE_integer tempX = rep_explosions[i].x + (mt_rand() % 24) - 12;
			JE_integer tempY = rep_explosions[i].y + (mt_rand() % 27) - 24;

			if (rep_explosions[i].big)
			{
				JE_setupExplosionLarge(false, 2, tempX, tempY);

				if (rep_explosions[i].ttl == 1 || mt_rand() % 5 == 1)
					soundQueue[7] = S_EXPLOSION_11;
				else
					soundQueue[6] = S_EXPLOSION_9;

				rep_explosions[i].delay = 4 + (mt_rand() % 3);
			}
			else
			{
				JE_setupExplosion(tempX, tempY, 0, 1, false, false);

				soundQueue[5] = S_EXPLOSION_4;

				rep_explosions[i].delay = 3;
			}

			rep_explosions[i].ttl--;
		}
	}

	// Tyrian3D dev: TYR3D_TEST_EXPLOSION=<x>,<y>,<every n frames>: large explosions there, on
	// the ground and in the air in turn (for looking at the explosions).
	{
		const char *test = SDL_getenv("TYR3D_TEST_EXPLOSION");
		static unsigned int test_frame = 0;
		int tx, ty, every;
		if (test != NULL && sscanf(test, "%d,%d,%d", &tx, &ty, &every) == 3 && every > 0 && ++test_frame % every == 0)
			JE_setupExplosionLarge((test_frame / every) & 1, 0, tx, ty);
		// TYR3D_TEST_PICKUP=<every n frames>: an item's pickup flash at the ship and a coin's value over it (250 and 1000
		// in turn; for looking at them).
		const char *pickup = SDL_getenv("TYR3D_TEST_PICKUP");
		static unsigned int pickup_frame = 0;
		if (pickup != NULL && SDL_atoi(pickup) > 0 && ++pickup_frame % SDL_atoi(pickup) == 0 && l3d_capturing)
		{
			p3d_pickup(player[0].x + 7.0f, player[0].y + 7.0f, l3d_layer_height(L3D_PLAYER) - l3d_terrain_headroom);
			const int e = JE_setupExplosion(player[0].x, player[0].y - 24, 0, 36, true, false);
			if (e >= 0)
				explosions[e].value = (pickup_frame / SDL_atoi(pickup)) & 1 ? 1000 : 250;
		}
		// TYR3D_TEST_WARP=<frame>: the level ends there as its last event ends it (the ship warping away).
		const char *warp = SDL_getenv("TYR3D_TEST_WARP");
		static unsigned int warp_frame = 0;
		if (warp != NULL && ++warp_frame == (unsigned int)SDL_atoi(warp) && !endLevel)
		{
			endLevel = true;
			levelEnd = 40;
		}
		// TYR3D_TEST_WRECK=<every n frames>: a ship's wreck flung apart in the middle of the screen.
		const char *wreck = SDL_getenv("TYR3D_TEST_WRECK");
		static unsigned int wreck_frame = 0;
		if (wreck != NULL && SDL_atoi(wreck) > 0 && ++wreck_frame % SDL_atoi(wreck) == 0 && l3d_capturing)
		{
			JE_setupExplosionLarge(false, 0, 160, 100);
			p3d_ship_destroyed(160.0f, 93.0f, l3d_layer_height(L3D_PLAYER) - l3d_terrain_headroom);
		}
	}

	/*---------------------------- Draw Explosions ----------------------------*/
	l3d_phase(L3D_EXPLOSION);
	if (l3d_capturing)
		p3d_update(explodeMove);  // Tyrian3D: the explosions' particles
	for (int j = 0; j < MAX_EXPLOSIONS; j++)
	{
		if (explosions[j].ttl != 0)
		{
			if (!explosions[j].fixedPosition)
			{
				explosions[j].sprite++;
				explosions[j].y += explodeMove;
			}
			else if (explosions[j].followPlayer)
			{
				explosions[j].x += explosionFollowAmountX;
				explosions[j].y += explosionFollowAmountY;
			}
			explosions[j].y += explosions[j].deltaY;

			if (explosions[j].y > 200 - 14)
			{
				explosions[j].ttl = 0;
			}
			else
			{
				// Tyrian3D: explosions the particles show aren't drawn as sprites in the 3D view, nor items' values,
				// which it writes.
				if (explosions[j].value != 0 && l3d_capturing && rgpu_values_written())
					l3d_add_value(explosions[j].x, explosions[j].y, explosions[j].value,
					              1 - explosions[j].ttl / (float)SDL_max(explosions[j].life, 1), 1.0f / SDL_max(explosions[j].life, 1));
				else if (explosions[j].particles && l3d_capturing && m3d_enabled)
					;
				else if (explosionTransparent)
					blit_sprite2_blend(VGAScreen, explosions[j].x, explosions[j].y, explosionSpriteSheet, explosions[j].sprite + 1);
				else
					blit_sprite2(VGAScreen, explosions[j].x, explosions[j].y, explosionSpriteSheet, explosions[j].sprite + 1);

				explosions[j].ttl--;
			}
		}
	}

	if (!portConfigChange)
		portConfigDone = true;

	/*-----------------------BACKGROUNDS------------------------*/
	/*-----------------------BACKGROUND 2------------------------*/
	if (!(smoothies[2-1] && processorType < 4) &&
	    !(smoothies[1-1] && processorType == 3))
	{
		l3d_phase(L3D_BG2_OVER);
		if (background2over == 2)
		{
			if (wild && !background2notTransparent)
				draw_background_2_blend(VGAScreen);
			else
				draw_background_2(VGAScreen);
		}
	}

	/*-------------------------Warning---------------------------*/
	l3d_phase(L3D_OVERLAY);
	armor_warning = -1;
	if ((player[0].is_alive && player[0].armor < 6) ||
	    (twoPlayerMode && !galagaMode && player[1].is_alive && player[1].armor < 6))
	{
		int armor_amount = (player[0].is_alive && player[0].armor < 6) ? player[0].armor : player[1].armor;

		if (armorShipDelay > 0)
		{
			armorShipDelay--;
		}
		else
		{
			tempW = 560;
			b = JE_newEnemy(50, tempW, 0);
			if (b > 0)
			{
				enemy[b-1].enemydie = 560 + (mt_rand() % 3) + 1;
				enemy[b-1].eyc -= backMove3;
				enemy[b-1].armorleft = 4;
			}
			armorShipDelay = 500;
		}

		if ((player[0].is_alive && player[0].armor < 6 && (!isNetworkGame || thisPlayerNum == 1)) ||
		    (twoPlayerMode && player[1].is_alive && player[1].armor < 6 && (!isNetworkGame || thisPlayerNum == 2)))
		{

			tempW = armor_amount * 4 + 8;
			if (warningSoundDelay > tempW)
				warningSoundDelay = tempW;

			if (warningSoundDelay > 1)
			{
				warningSoundDelay--;
			}
			else
			{
				soundQueue[7] = S_WARNING;
				warningSoundDelay = tempW;
			}

			warningCol += warningColChange;
			if (warningCol > 113 + (14 - (armor_amount * 2)))
			{
				warningColChange = -warningColChange;
				warningCol = 113 + (14 - (armor_amount * 2));
			}
			else if (warningCol < 113)
			{
				warningColChange = -warningColChange;
			}
			// (Tyrian3D: one of the game's displays, which the modern HUD shows its own way: armor_warning)
			armor_warning = armor_amount;
			l3d_phase(L3D_HUD);
			fill_rectangle_xy(VGAScreen, 24, 181, 138, 183, warningCol);
			fill_rectangle_xy(VGAScreen, 175, 181, 287, 183, warningCol);
			fill_rectangle_xy(VGAScreen, 24, 0, 287, 3, warningCol);

			JE_outText(VGAScreen, 140, 178, "WARNING", 7, (warningCol % 16) / 2);
			l3d_phase(L3D_OVERLAY);

		}
	}

	/*------- Random Explosions --------*/
	if (randomExplosions && mt_rand() % 10 == 1)
		JE_setupExplosionLarge(false, 20, mt_rand() % 280, mt_rand() % 180);

	/*=================================*/
	/*=======The Sound Routine=========*/
	/*=================================*/
	if (firstGameOver)
	{
		temp = 0;
		for (temp2 = 0; temp2 < COUNTOF(soundQueue); temp2++)
		{
			if (soundQueue[temp2] != S_NONE)
			{
				temp = soundQueue[temp2];
				if (temp2 == 3)
					temp3 = fxPlayVol;
				else if (temp == 15)
					temp3 = fxPlayVol / 4;
				else   /*Lightning*/
					temp3 = fxPlayVol / 2;

				multiSamplePlay(soundSamples[temp-1], soundSampleCount[temp-1], temp2, temp3);

				soundQueue[temp2] = S_NONE;
			}
		}
	}

	if (returnActive && enemyOnScreen == 0)
	{
		JE_eventJump(65535);
		returnActive = false;
	}

	/*-------      DEbug      ---------*/
	debugTime = SDL_GetTicks();
	tempW = lastmouse_but;

	if (debug)
	{
		for (size_t i = 0; i < 9; i++)
		{
			tempStr[i] = '0' + smoothies[i];
		}
		tempStr[9] = '\0';
		sprintf(buffer, "SM = %s", tempStr);
		JE_outText(VGAScreen, 30, 70, buffer, 4, 0);

		sprintf(buffer, "Memory left = %d", -1);
		JE_outText(VGAScreen, 30, 80, buffer, 4, 0);
		sprintf(buffer, "Enemies onscreen = %d", enemyOnScreen);
		JE_outText(VGAScreen, 30, 90, buffer, 6, 0);

		debugHist = debugHist + abs((JE_longint)debugTime - (JE_longint)lastDebugTime);
		debugHistCount++;
		sprintf(tempStr, "%2.3f", 1000.0f / roundf(debugHist / debugHistCount));
		sprintf(buffer, "X:%d Y:%-5d  %s FPS  %d %d %d %d", (mapX - 1) * 12 + player[0].x, curLoc, tempStr, player[0].x_velocity, player[0].y_velocity, player[0].x, player[0].y);
		JE_outText(VGAScreen, 45, 175, buffer, 15, 3);
		lastDebugTime = debugTime;
	}

	if (displayTime > 0)
	{
		displayTime--;
		l3d_phase(L3D_HUD);  // (Tyrian3D: one of the game's displays, which the modern HUD shows its own way)
		JE_outTextAndDarken(VGAScreen, 90, 10, miscText[59], 15, (JE_byte)flash - 8, FONT_SHAPES);
		l3d_phase(L3D_OVERLAY);
		flash += flashChange;
		if (flash > 4 || flash == 0)
			flashChange = -flashChange;
	}

	/*Pentium Speed Mode?*/
	if (pentiumMode)
	{
		frameCountMax = (frameCountMax == 2) ? 3 : 2;
	}

	/*--------  Level Timer    ---------*/
	if (levelTimer && levelTimerCountdown > 0)
	{
		levelTimerCountdown--;
		if (levelTimerCountdown == 0)
			JE_eventJump(levelTimerJumpTo);

		if (timedBattleMode)
		{
			// No-op; play no sound effects
		}
		else if (levelTimerCountdown > 200)
		{
			if (levelTimerCountdown % 100 == 0)
				soundQueue[7] = S_WARNING;

			if (levelTimerCountdown % 10 == 0)
				soundQueue[6] = S_CLICK;
		}
		else if (levelTimerCountdown % 20 == 0)
		{
			soundQueue[7] = S_WARNING;
		}

		l3d_phase(L3D_HUD);  // (Tyrian3D: the modern HUD shows the timer its own way)
		JE_textShade (VGAScreen, 140, 6, miscText[66], 7, (levelTimerCountdown % 20) / 3, FULL_SHADE);
		// Don't use floats due to rounding.
		sprintf(buffer, "%d.%d", levelTimerCountdown / 100, (levelTimerCountdown / 10) % 10);
		JE_dString (VGAScreen, 100, 2, buffer, SMALL_FONT_SHAPES);
		l3d_phase(L3D_OVERLAY);
	}

	/*GAME OVER*/
	if (!constantPlay && !constantDie)
	{
		if (allPlayersGone)
		{
			if (player[0].exploding_ticks > 0 || player[1].exploding_ticks > 0)
			{
				if (galagaMode)
					player[1].exploding_ticks = 0;

				musicFade = true;
			}
			else
			{
				if (play_demo || normalBonusLevelCurrent || bonusLevelCurrent)
					reallyEndLevel = true;
				else
				{
					// (Tyrian3D: the modern HUD shows it its own way.)
					const L3DLayerType layer = l3d_current_layer();
					l3d_phase(L3D_HUD);
					JE_dString(VGAScreen, 120, 60, miscText[21], FONT_SHAPES); // game over
					l3d_phase(layer);
					ui_note_game_over(miscText[21]);
				}

				if (firstGameOver)
				{
					if (!play_demo)
					{
						play_song(SONG_GAMEOVER);
						set_volume(tyrMusicVolume, fxVolume);
					}
					firstGameOver = false;
				}

				if (!play_demo)
				{
					push_joysticks_as_keyboard();
					service_SDL_events(true);
					if ((newkey || button[0] || button[1] || button[2]) || newmouse)
					{
						reallyEndLevel = true;
					}
				}

				if (isNetworkGame)
					reallyEndLevel = true;
			}
		}
	}

	if (play_demo) // input kills demo
	{
		push_joysticks_as_keyboard();
		service_SDL_events(false);

		if (newkey || newmouse)
		{
			reallyEndLevel = true;

			stopped_demo = true;
		}
	}
	else // input handling for pausing, menu, cheats
	{
		service_SDL_events(false);

		if (newkey)
		{
			skipStarShowVGA = false;
			JE_mainKeyboardInput();
			newkey = false;
			if (skipStarShowVGA)
				goto level_loop;
		}

		if (pause_pressed || (!windowHasFocus && !dev_background_run()))
		{
			pause_pressed = false;

			if (isNetworkGame)
				pauseRequest = true;
			else
				JE_pauseGame();
		}

		if (ingamemenu_pressed)
		{
			ingamemenu_pressed = false;

			if (isNetworkGame)
			{
				inGameMenuRequest = true;
			}
			else
			{
				yourInGameMenuRequest = true;
				JE_doInGameSetup();
				skipStarShowVGA = true;
			}
		}
	}

	/*Network Update*/
#ifdef WITH_NETWORK
	if (isNetworkGame)
	{
		if (!reallyEndLevel)
		{
			Uint16 requests = (pauseRequest == true) |
			                  (inGameMenuRequest == true) << 1 |
			                  (skipLevelRequest == true) << 2 |
			                  (nortShipRequest == true) << 3;
			SDLNet_Write16(requests,        &packet_state_out[0]->data[14]);

			SDLNet_Write16(difficultyLevel, &packet_state_out[0]->data[16]);
			SDLNet_Write16(player[0].x,     &packet_state_out[0]->data[18]);
			SDLNet_Write16(player[1].x,     &packet_state_out[0]->data[20]);
			SDLNet_Write16(player[0].y,     &packet_state_out[0]->data[22]);
			SDLNet_Write16(player[1].y,     &packet_state_out[0]->data[24]);
			SDLNet_Write16(curLoc,          &packet_state_out[0]->data[26]);

			network_state_send();

			if (network_state_update())
			{
				assert(SDLNet_Read16(&packet_state_in[0]->data[26]) == SDLNet_Read16(&packet_state_out[network_delay]->data[26]));

				requests = SDLNet_Read16(&packet_state_in[0]->data[14]) ^ SDLNet_Read16(&packet_state_out[network_delay]->data[14]);
				if (requests & 1)
				{
					JE_pauseGame();
				}
				if (requests & 2)
				{
					yourInGameMenuRequest = SDLNet_Read16(&packet_state_out[network_delay]->data[14]) & 2;
					JE_doInGameSetup();
					yourInGameMenuRequest = false;
					if (haltGame)
						reallyEndLevel = true;
				}
				if (requests & 4)
				{
					levelTimer = true;
					levelTimerCountdown = 0;
					endLevel = true;
					levelEnd = 40;
				}
				if (requests & 8) // nortship
				{
					player[0].items.ship = 12;                     // Nort Ship
					player[0].items.special = 13;                  // Astral Zone
					player[0].items.weapon[FRONT_WEAPON].id = 36;  // NortShip Super Pulse
					player[0].items.weapon[REAR_WEAPON].id = 37;   // NortShip Spreader
					shipGr = 1;
				}

				for (int i = 0; i < 2; i++)
				{
					if (SDLNet_Read16(&packet_state_in[0]->data[18 + i * 2]) != SDLNet_Read16(&packet_state_out[network_delay]->data[18 + i * 2]) || SDLNet_Read16(&packet_state_in[0]->data[20 + i * 2]) != SDLNet_Read16(&packet_state_out[network_delay]->data[20 + i * 2]))
					{
						char temp[64];
						sprintf(temp, "Player %d is unsynchronized!", i + 1);

						JE_textShade(game_screen, 40, 110 + i * 10, temp, 9, 2, FULL_SHADE);
					}
				}
			}
		}

		JE_clearSpecialRequests();
	}
#endif

	/** Test **/
	l3d_phase(L3D_EXPLOSION);
	JE_drawSP();
	l3d_phase(L3D_OVERLAY);

	/*Filtration*/
	if (filterActive)
	{
		JE_filterScreen(levelFilter, levelBrightness);
	}

	l3d_phase(L3D_HUD);  // (Tyrian3D: the game's displays, which the modern HUD shows its own way)
	draw_boss_bar();

	JE_inGameDisplays();

	if (SDL_getenv("TYR3D_LOG_GROUND") != NULL)
		flush_ground_log();
	l3d_frame_end();

	VGAScreen = VGAScreenSeg; /* side-effect of game_screen */

	JE_starShowVGA();

	/*Start backgrounds if no enemies on screen
	  End level if number of enemies left to kill equals 0.*/
	if (stopBackgroundNum == 9 && backMove == 0 && !enemyStillExploding)
	{
		backMove = 1;
		backMove2 = 2;
		backMove3 = 3;
		explodeMove = 2;
		stopBackgroundNum = 0;
		stopBackgrounds = false;
		if (waitToEndLevel)
		{
			endLevel = true;
			levelEnd = 40;
		}
		if (allPlayersGone)
		{
			reallyEndLevel = true;
		}
	}

	if (!endLevel && enemyOnScreen == 0)
	{
		if (readyToEndLevel && !enemyStillExploding)
		{
			if (levelTimerCountdown > 0)
			{
				levelTimer = false;
			}
			readyToEndLevel = false;
			endLevel = true;
			levelEnd = 40;
			if (allPlayersGone)
			{
				reallyEndLevel = true;
			}
		}
		if (stopBackgrounds)
		{
			stopBackgrounds = false;
			backMove = 1;
			backMove2 = 2;
			backMove3 = 3;
			explodeMove = 2;
		}
	}

	/*Other Network Functions*/
	JE_handleChat();

	if (reallyEndLevel)
	{
		goto start_level;
	}
	goto level_loop;
}

// A line of the episode's script, or false at its end: read_encrypted_pascal_string stops the game there, and feof()
// only says so once a read has failed (a cube picked up in an episode's last level, whose next section is its ending:
// no "]?" nor "]L" before the end).
static bool script_line(char *s, size_t size, FILE *f, long end)
{
	const long at = ftell(f);
	const int len = fgetc(f);
	if (len == EOF || at + 1 + len > end)
		return false;
	fseek(f, at, SEEK_SET);
	read_encrypted_pascal_string(s, size, f);
	return true;
}

int upcoming_cube(int n)
{
	if (n <= 0)
		return 0;
	FILE *f = dir_fopen(data_dir(), episode_file, "rb");
	if (f == NULL)
		return 0;
	fseek(f, 0, SEEK_END);
	const long end = ftell(f);
	fseek(f, 0, SEEK_SET);
	char s[256];
	int section = 0, cube = 0;
	while (section < nextLevel && script_line(s, sizeof(s), f, end))
	{
		if (s[0] == '*')
			++section;
	}
	// (as JE_loadMap reads "]?": the count at 4, the cubes at 7, 11, ...)
	for (int lines = 0; lines < 2000; ++lines)
	{
		strcpy(s, " ");
		if (!script_line(s, sizeof(s), f, end))
			break;
		if (s[0] != ']')
			continue;
		if (s[1] == 'L')
			break;
		if (s[1] == '?')
		{
			const int count = atoi(s + 4);
			if (n <= count && (size_t)(3 + n * 4) < strlen(s))
				cube = atoi(s + 3 + n * 4);
			break;
		}
	}
	fclose(f);
	return cube;
}

// (The mini-game's weapons, kit_restore.)
static void kit_restore(void)
{
	if (!kit_saved)
		return;
	player[0].items = kit_backup;
	player[0].last_items = kit_backup;  // (the store lists what the ship came with)
	kit_saved = false;
}

/* --- Load Level/Map Data --- */
void JE_loadMap(void)
{
	JE_DanCShape shape;

	JE_word x, y;
	JE_integer yy;
	JE_word mapSh[3][128]; /* [1..3, 0..127] */
	JE_byte *ref[3][128]; /* [1..3, 0..127] */
	char s[256];

	JE_byte mapBuf[15 * 600]; /* [1..15 * 600] */
	JE_word bufLoc;

	char buffer[256];
	int i;
	Uint8 pic_buffer[320*200]; /* screen buffer, 8-bit specific */
	Uint8 *vga, *pic, *vga2; /* screen pointer, 8-bit specific */

	lastCubeMax = cubeMax;

	/*Defaults*/
	songBuy = DEFAULT_SONG_BUY;  /*Item Screen default song*/

	/* Load LEVELS.DAT - Section = MAINLEVEL */
	saveLevel = mainLevel;

new_game:
	galagaMode  = false;
	useLastBank = false;
	extraGame   = false;
	haltGame = false;

	gameLoaded = false;

	if (!play_demo)
	{
		do
		{
			FILE *ep_f = dir_fopen_die(data_dir(), episode_file, "rb");

			jumpSection = false;
			loadLevelOk = false;

			/* Seek Section # Mainlevel */
			int x = 0;
			while (x < mainLevel)
			{
				read_encrypted_pascal_string(s, sizeof(s), ep_f);
				if (s[0] == '*')
				{
					x++;
					s[0] = ' ';
				}
			}

			ESCPressed = false;

			do
			{
				if (gameLoaded)
				{
					fclose(ep_f);

					if (mainLevel == 0)  // if quit itemscreen
						return;          // back to title screen
					else
						goto new_game;
				}

				strcpy(s, " ");
				read_encrypted_pascal_string(s, sizeof(s), ep_f);

				if (s[0] == ']')
				{
					switch (s[1])
					{
					case 'A':
						JE_playAnim("tyrend.anm", 0, 7);
						break;

					case 'G':
						mapOrigin = atoi(s + 4);
						mapPNum   = atoi(s + 7);
						for (i = 0; i < mapPNum; i++)
						{
							mapPlanet[i] = atoi(s + 1 + (i + 1) * 8);
							mapSection[i] = atoi(s + 4 + (i + 1) * 8);
						}
						break;

					case '?':
						temp = atoi(s + 4);
						for (i = 0; i < temp; i++)
						{
							cubeList[i] = atoi(s + 3 + (i + 1) * 4);
						}
						if (cubeMax > temp)
							cubeMax = temp;
						if (SDL_getenv("TYR3D_CUBES") != NULL)  // Tyrian3D dev: the store holds every cube it lists
							cubeMax = temp;
						break;

					case '!':
						cubeMax = atoi(s + 4);    /*Auto set CubeMax*/
						break;

					case '+':
						temp = atoi(s + 4);
						cubeMax += temp;
						if (cubeMax > 4)
							cubeMax = 4;
						break;

					case 'g':
						galagaMode = true;   /*GALAGA mode*/

						player[1].items = player[0].items;
						player[1].items.weapon[REAR_WEAPON].id = 15;  // Vulcan Cannon
						for (uint i = 0; i < COUNTOF(player[1].items.sidekick); ++i)
							player[1].items.sidekick[i] = 0;          // None
						break;

					case 'x':
						extraGame = true;
						break;

					case 'e': // ENGAGE mode, used for mini-games
						doNotSaveBackup = true;
						constantDie = false;
						onePlayerAction = true;
						superTyrian = true;
						twoPlayerMode = false;

						player[0].cash = 0;

						player[0].items.ship = 13;                     // The Stalker 21.126
						player[0].items.weapon[FRONT_WEAPON].id = 39;  // Atomic RailGun
						player[0].items.weapon[REAR_WEAPON].id = 0;    // None
						for (uint i = 0; i < COUNTOF(player[0].items.sidekick); ++i)
							player[0].items.sidekick[i] = 0;           // None
						player[0].items.generator = 2;                 // Advanced MR-12
						player[0].items.shield = 4;                    // Advanced Integrity Field
						player[0].items.special = 0;                   // None

						player[0].items.weapon[FRONT_WEAPON].power = 3;
						player[0].items.weapon[REAR_WEAPON].power = 1;
						break;

					case 'J':  // section jump
						temp = atoi(s + 3);
						mainLevel = temp;
						jumpSection = true;
						break;

					case '2':  // two-player section jump
						temp = atoi(s + 3);
						if (twoPlayerMode || onePlayerAction)
						{
							mainLevel = temp;
							jumpSection = true;
						}
						break;

					case 'w':  // Stalker 21.126 section jump
						temp = atoi(s + 3);   /*Allowed to go to Time War?*/
						if (player[0].items.ship == 13)
						{
							mainLevel = temp;
							jumpSection = true;
						}
						break;

					case 't':
						temp = atoi(s + 3);
						if (levelTimer && levelTimerCountdown == 0)
						{
							mainLevel = temp;
							jumpSection = true;
						}
						break;

					case 'l':
						temp = atoi(s + 3);
						if (!all_players_alive())
						{
							mainLevel = temp;
							jumpSection = true;
						}
						break;

					case 's':
						saveLevel = mainLevel;
						break; /*store savepoint*/

					case 'b':
						if (twoPlayerMode)
							temp = 22;
						else
							temp = 11;
						// Tyrian3D: not over the player's save for a rogue run or a debug flight.
						if (!rogue_run && !debug_flight)
							JE_saveGame(11, "LAST LEVEL    ");
						break;

					case 'i':
						temp = atoi(s + 3);
						songBuy = temp - 1;
						break;

					case 'k':  // Tyrian3D: the mini-game's weapons for the next level (kit_restore)
						if (!kit_saved)
							kit_backup = player[0].items;
						kit_saved = true;
						kit_this_level = true;
						player[0].items.weapon[FRONT_WEAPON].id = 39;  // Atomic RailGun
						player[0].items.weapon[FRONT_WEAPON].power = 3;
						player[0].items.weapon[REAR_WEAPON].id = 0;    // None
						player[0].items.weapon[REAR_WEAPON].power = 1;
						for (uint i = 0; i < COUNTOF(player[0].items.sidekick); ++i)
							player[0].items.sidekick[i] = 0;           // None
						player[0].items.special = 0;                   // None
						break;

					case 'I': /*Load Items Available Information*/
						kit_restore();
						memset(&itemAvail, 0, sizeof(itemAvail));

						for (int i = 0; i < 9; ++i)
						{
							read_encrypted_pascal_string(s, sizeof(s), ep_f);

							char buf[256];
							strncpy(buf, (strlen(s) > 8) ? s + 8 : "", sizeof(buf));

							int j = 0, temp;
							while (str_pop_int(buf, &temp))
								itemAvail[i][j++] = temp;
							itemAvailMax[i] = j;
						}
						// Tyrian3D: a 10th line " Spec   <specials>" (episode 6's shops: the specials sold, game_menu.c),
						// else the line is the script's next.
						{
							const long at = ftell(ep_f);
							read_encrypted_pascal_string(s, sizeof(s), ep_f);
							if (strncmp(s, " Spec", 5) == 0)
							{
								char buf[256];
								strncpy(buf, (strlen(s) > 8) ? s + 8 : "", sizeof(buf));
								int j = 0, temp;
								while (j < 10 && str_pop_int(buf, &temp))
									itemAvail[9][j++] = temp;
								itemAvailMax[9] = j;
							}
							else
								fseek(ep_f, at, SEEK_SET);
						}

						secrets_shop(episodeNum, mainLevel);  // (Tyrian3D: secrets.h)
						if (!rogue_run)  // Tyrian3D: a rogue run has its own merchants
							JE_itemScreen();
						break;

					case 'L':
						if (!kit_this_level)
							kit_restore();
						kit_this_level = false;
						secrets_level(episodeNum, mainLevel);  // (Tyrian3D: a secret level's, secrets.h)
						nextLevel = atoi(s + 9);
						SDL_strlcpy(levelName, s + 13, 10);
						levelSong = atoi(s + 22);
						if (nextLevel == 0)
						{
							nextLevel = mainLevel + 1;
						}
						lvlFileNum = atoi(s + 25);
						loadLevelOk = true;
						bonusLevelCurrent = (strlen(s) > 28) & (s[28] == '$');
						normalBonusLevelCurrent = (strlen(s) > 27) & (s[27] == '$');
						gameJustLoaded = false;
						break;

					case '@':
						useLastBank = !useLastBank;
						break;

					case 'Q':
						ESCPressed = false;
						temp = secretHint + (mt_rand() % 3) * 3;

						if (twoPlayerMode)
						{
							for (uint i = 0; i < 2; ++i)
								snprintf(levelWarningText[i], sizeof(*levelWarningText), "%s %lu", miscText[40 + i], player[i].cash);
							strcpy(levelWarningText[2], "");
							levelWarningLines = 3;
						}
						else
						{
							sprintf(levelWarningText[0], "%s %lu", miscText[37], JE_totalScore(&player[0]));
							strcpy(levelWarningText[1], "");
							levelWarningLines = 2;
						}

						for (x = 0; x < temp - 1; x++)
						{
							do
							{
								read_encrypted_pascal_string(s, sizeof(s), ep_f);
							} while (s[0] != '#');
						}

						do
						{
							read_encrypted_pascal_string(s, sizeof(s), ep_f);
							strcpy(levelWarningText[levelWarningLines], s);
							levelWarningLines++;
						} while (s[0] != '#');
						levelWarningLines--;

						JE_wipeKey();
						frameCountMax = 4;
						if (!constantPlay)
						{
							story_begin(UI_STORY_ENDING, twoPlayerMode ? 2 : 1);  // Tyrian3D: the modern UI's (mainint.h)
							JE_displayText();
						}

						fade_black(15);

						JE_nextEpisode();

						if (jumpBackToEpisode1 && !twoPlayerMode)
						{
							JE_loadPic(VGAScreen, 1, false); // huh?
							JE_clr256(VGAScreen);

							if (superTyrian)
							{
								// if completed Zinglon's Revenge, show SuperTyrian and Destruct codes
								// if completed SuperTyrian, show Nort-Ship Z code
								superArcadeMode = (initialDifficulty == DIFFICULTY_ZINGLON) ? 8 : 1;
							}

							if (superArcadeMode < SA_ENGAGE)
							{
								if (SANextShip[superArcadeMode] == SA_ENGAGE)
								{
									sprintf(buffer, "%s %s", miscTextB[4], pName[0]);
									JE_dString(VGAScreen, JE_fontCenter(buffer, FONT_SHAPES), 100, buffer, FONT_SHAPES);

									sprintf(buffer, "Or play... %s", specialName[SA_DESTRUCT - 1]);
									JE_dString(VGAScreen, 80, 180, buffer, SMALL_FONT_SHAPES);
								}
								else
								{
									JE_dString(VGAScreen, JE_fontCenter(superShips[0], FONT_SHAPES), 30, superShips[0], FONT_SHAPES);
									JE_dString(VGAScreen, JE_fontCenter(superShips[SANextShip[superArcadeMode]], SMALL_FONT_SHAPES), 100, superShips[SANextShip[superArcadeMode]], SMALL_FONT_SHAPES);
								}

								if (SANextShip[superArcadeMode] < SA_NORTSHIPZ)
									blit_sprite2x2(VGAScreen, 148, 70, spriteSheet9, ships[SAShip[SANextShip[superArcadeMode]-1]].shipgraphic);
								else if (SANextShip[superArcadeMode] == SA_NORTSHIPZ)
									trentWin = true;

								sprintf(buffer, "Type %s at Title", specialName[SANextShip[superArcadeMode]-1]);
								JE_dString(VGAScreen, JE_fontCenter(buffer, SMALL_FONT_SHAPES), 160, buffer, SMALL_FONT_SHAPES);

								// Tyrian3D: the modern UI's card (mainint.h): the next ship or the codes, the word to type.
								{
									char title[64], line[64];
									const char *lines[3] = { line, NULL, NULL };
									if (SANextShip[superArcadeMode] == SA_ENGAGE)
									{
										snprintf(title, sizeof(title), "%s %s", miscTextB[4], pName[0]);
										snprintf(line, sizeof(line), "Or play... %s", specialName[SA_DESTRUCT - 1]);
										card_publish("", title, lines, NULL, NULL, 0, !constantPlay, true);
									}
									else
									{
										SDL_strlcpy(title, superShips[SANextShip[superArcadeMode]], sizeof(title));
										snprintf(line, sizeof(line), "Type it at the title screen:");
										const bool drawn = SANextShip[superArcadeMode] < SA_NORTSHIPZ;
										card_publish(superShips[0], title, lines, specialName[SANextShip[superArcadeMode] - 1], drawn ? &spriteSheet9 : NULL,
										             drawn ? ships[SAShip[SANextShip[superArcadeMode] - 1]].shipgraphic : 0, !constantPlay, false);
									}
								}
								JE_showVGA();

								fade_palette(colors, 50, 0, 255);

								if (!constantPlay)
									wait_input(true, true, true);
							}

							jumpSection = true;

							if (isNetworkGame)
								JE_readTextSync();

							if (superTyrian)
							{
								fade_black(10);

								// back to titlescreen
								mainLevel = 0;
								return;
							}
						}
						break;

					case 'P':
						ui_screen_done();  // Tyrian3D: a new picture (the modern UI's story text before it goes)
						if (!constantPlay && !rogue_run)
						{
							JE_word tempX = atoi(s + 3);
							if (tempX > 900)
							{
								memcpy(colors, palettes[pcxpal[tempX-1 - 900]], sizeof(colors));
								JE_clr256(VGAScreen);
								JE_showVGA();
								fade_palette(colors, 1, 0, 255);
							}
							else
							{
								if (tempX == 0)
									JE_loadPCX("tshp2.pcx");
								else
									JE_loadPic(VGAScreen, tempX, false);

								JE_showVGA();
								fade_palette(colors, 10, 0, 255);
							}
						}
						break;

					case 'U':
						ui_screen_done();  // Tyrian3D (as ]P)
						if (!constantPlay && !rogue_run)
						{
							memcpy(VGAScreen2->pixels, VGAScreen->pixels, VGAScreen2->pitch * VGAScreen2->h);

							JE_word tempX = atoi(s + 3);
							JE_loadPic(VGAScreen, tempX, false);
							memcpy(pic_buffer, VGAScreen->pixels, sizeof(pic_buffer));

							service_SDL_events(true);

							for (int z = 0; z <= 199; z++)
							{
								if (!newkey)
								{
									vga = VGAScreen->pixels;
									vga2 = VGAScreen2->pixels;
									pic = pic_buffer + (199 - z) * 320;

									setDelay(1);

									for (y = 0; y <= 199; y++)
									{
										if (y <= z)
										{
											memcpy(vga, pic, 320);
											pic += 320;
										}
										else
										{
											memcpy(vga, vga2, VGAScreen->pitch);
											vga2 += VGAScreen->pitch;
										}
										vga += VGAScreen->pitch;
									}

									rgpu_picture_slide(tempX, 0, z - 199, 0, z + 1);  // Tyrian3D (drawn anew; the earlier one pushed down)
									JE_showVGA();

									if (isNetworkGame)
									{
										/* TODO: NETWORK */
									}

									service_wait_delay();
								}
							}

							memcpy(VGAScreen->pixels, pic_buffer, sizeof(pic_buffer));
							rgpu_picture_slide(0, 0, 0, 0, 0);  // Tyrian3D
						}
						break;

					case 'V':
						ui_screen_done();  // Tyrian3D (as ]P)
						if (!constantPlay && !rogue_run)
						{
							/* TODO: NETWORK */
							memcpy(VGAScreen2->pixels, VGAScreen->pixels, VGAScreen2->pitch * VGAScreen2->h);

							JE_word tempX = atoi(s + 3);
							JE_loadPic(VGAScreen, tempX, false);
							memcpy(pic_buffer, VGAScreen->pixels, sizeof(pic_buffer));

							service_SDL_events(true);
							for (int z = 0; z <= 199; z++)
							{
								if (!newkey)
								{
									vga = VGAScreen->pixels;
									vga2 = VGAScreen2->pixels;
									pic = pic_buffer;

									setDelay(1);

									for (y = 0; y < 199; y++)
									{
										if (y <= 199 - z)
										{
											memcpy(vga, vga2, VGAScreen->pitch);
											vga2 += VGAScreen->pitch;
										}
										else
										{
											memcpy(vga, pic, 320);
											pic += 320;
										}
										vga += VGAScreen->pitch;
									}

									rgpu_picture_slide(tempX, 0, 200 - z, 0, 0);  // Tyrian3D (drawn anew)
									JE_showVGA();

									if (isNetworkGame)
									{
										/* TODO: NETWORK */
									}

									service_wait_delay();
								}
							}

							memcpy(VGAScreen->pixels, pic_buffer, sizeof(pic_buffer));
							rgpu_picture_slide(0, 0, 0, 0, 0);  // Tyrian3D
						}
						break;

					case 'R':
						ui_screen_done();  // Tyrian3D (as ]P)
						if (!constantPlay && !rogue_run)
						{
							/* TODO: NETWORK */
							memcpy(VGAScreen2->pixels, VGAScreen->pixels, VGAScreen2->pitch * VGAScreen2->h);

							JE_word tempX = atoi(s + 3);
							JE_loadPic(VGAScreen, tempX, false);
							memcpy(pic_buffer, VGAScreen->pixels, sizeof(pic_buffer));

							service_SDL_events(true);

							for (int z = 0; z <= 318; z++)
							{
								if (!newkey)
								{
									vga = VGAScreen->pixels;
									vga2 = VGAScreen2->pixels;
									pic = pic_buffer;

									setDelay(1);

									for (y = 0; y < 200; y++)
									{
										memcpy(vga, vga2 + z, 319 - z);
										vga += 320 - z;
										vga2 += VGAScreen2->pitch;
										memcpy(vga, pic, z + 1);
										vga += z;
										pic += 320;
									}

									rgpu_picture_slide(tempX, 320 - z, 0, -z, 0);  // Tyrian3D (drawn anew; the earlier one pushed left)
									JE_showVGA();

									if (isNetworkGame)
									{
										/* TODO: NETWORK */
									}

									service_wait_delay();
								}
							}

							memcpy(VGAScreen->pixels, pic_buffer, sizeof(pic_buffer));
							rgpu_picture_slide(0, 0, 0, 0, 0);  // Tyrian3D
						}
						break;

					case 'C':
						if (!isNetworkGame)
						{
							fade_black(10);
						}
						ui_screen_done();  // Tyrian3D (as ]P)
						JE_clr256(VGAScreen);
						JE_showVGA();
						memcpy(colors, palettes[7], sizeof(colors));
						set_palette(colors, 0, 255);
						break;

					case 'B':
						if (!isNetworkGame)
						{
							fade_black(10);
						}
						break;
					case 'F':
						if (!isNetworkGame)
						{
							fade_white(100);
							fade_black(30);
						}
						ui_screen_done();  // Tyrian3D (as ]P)
						JE_clr256(VGAScreen);
						JE_showVGA();
						break;

					case 'W':
						if (!constantPlay && !rogue_run)
						{
							if (!ESCPressed)
							{
								JE_wipeKey();
								warningCol = 14 * 16 + 5;
								warningColChange = 1;
								warningSoundDelay = 0;
								levelWarningDisplay = (s[2] == 'y');
								levelWarningLines = 0;
								frameCountMax = atoi(s + 4);
								setDelay2(6);
								warningRed = frameCountMax / 10;
								frameCountMax = frameCountMax % 10;

								do
								{
									read_encrypted_pascal_string(s, sizeof(s), ep_f);

									if (s[0] != '#')
									{
										strcpy(levelWarningText[levelWarningLines], s);
										levelWarningLines++;
									}
								} while (!(s[0] == '#'));

								story_begin(levelWarningDisplay ? UI_STORY_WARNING : UI_STORY_TEXT, 0);  // Tyrian3D (mainint.h)
								JE_displayText();
								newkey = false;
							}
						}
						break;

					case 'H':
						if (initialDifficulty < DIFFICULTY_HARD)
						{
							mainLevel = atoi(s + 4);
							jumpSection = true;
						}
						break;

					case 'h':
						if (initialDifficulty > DIFFICULTY_NORMAL)
						{
							read_encrypted_pascal_string(s, sizeof(s), ep_f);
						}
						break;

					case 'S':
						if (isNetworkGame)
						{
							JE_readTextSync();
						}
						break;

					case 'n':
						ESCPressed = false;
						break;

					case 'M':
						temp = atoi(s + 3);
						play_song(temp - 1);
						break;

					case 'T':
						if (timedBattleMode)
						{
							// ]T[ 43 44 45 46 47 -- Episode 1
							// ]T[ 03 03 04 05 06 -- Episode 5
							mainLevel = atoi(s + (timeBattleSelection * 3));
							jumpSection = true;
						}
						break;

					case 'q':
						if (timedBattleMode)
						{
							JE_highScoreCheck();
							mainLevel = 0;
							return;
						}
						break;
					}
				}

			} while (!(loadLevelOk || jumpSection));

			fclose(ep_f);

		} while (!loadLevelOk);
	}

	if (play_demo)
		load_next_demo();
	else
		fade_black(50);

	FILE *level_f = dir_fopen_die(data_dir(), levelFile, "rb");
	fseek(level_f, lvlPos[(lvlFileNum-1) * 2], SEEK_SET);

	JE_char char_mapFile;
	JE_char char_shapeFile;
	fread_die(&char_mapFile,   1, 1, level_f);
	fread_die(&char_shapeFile, 1, 1, level_f);
	fread_u16_die(&mapX,  1, level_f);
	fread_u16_die(&mapX2, 1, level_f);
	fread_u16_die(&mapX3, 1, level_f);

	fread_u16_die(&levelEnemyMax, 1, level_f);
	fread_u16_die(levelEnemy, levelEnemyMax, level_f);

	fread_u16_die(&maxEvent, 1, level_f);
	for (x = 0; x < maxEvent; x++)
	{
		fread_u16_die(&eventRec[x].eventtime, 1, level_f);
		fread_u8_die( &eventRec[x].eventtype, 1, level_f);
		fread_s16_die(&eventRec[x].eventdat,  1, level_f);
		fread_s16_die(&eventRec[x].eventdat2, 1, level_f);
		fread_s8_die( &eventRec[x].eventdat3, 1, level_f);
		fread_s8_die( &eventRec[x].eventdat5, 1, level_f);
		fread_s8_die( &eventRec[x].eventdat6, 1, level_f);
		fread_u8_die( &eventRec[x].eventdat4, 1, level_f);
	}
	eventRec[x].eventtime = 65500;  /*Not needed but just in case*/

	/*debuginfo('Level loaded.');*/

	/*debuginfo('Loading Map');*/

	/* MAP SHAPE LOOKUP TABLE - Each map is directly after level */
	for (temp = 0; temp < 3; temp++)
	{
		fread_u16_die(mapSh[temp], sizeof(*mapSh) / sizeof(JE_word), level_f);
		for (temp2 = 0; temp2 < 128; temp2++)
		{
			mapSh[temp][temp2] = SDL_Swap16(mapSh[temp][temp2]);
		}
	}

	/* Read Shapes.DAT */
	sprintf(tempStr, "shapes%c.dat", tolower((unsigned char)char_shapeFile));
	FILE *shpFile = dir_fopen_die(data_dir(), tempStr, "rb");

	for (int z = 0; z < 600; z++)
	{
		JE_boolean shapeBlank;
		fread_bool_die(&shapeBlank, shpFile);

		if (shapeBlank)
			memset(shape, 0, sizeof(shape));
		else
			fread_u8_die(shape, sizeof(shape), shpFile);

		/* Match 1 */
		for (int x = 0; x <= 71; ++x)
		{
			if (mapSh[0][x] == z+1)
			{
				memcpy(megaData1.shapes[x].sh, shape, sizeof(JE_DanCShape));

				ref[0][x] = megaData1.shapes[x].sh;
			}
		}

		/* Match 2 */
		for (int x = 0; x <= 71; ++x)
		{
			if (mapSh[1][x] == z+1)
			{
				if (x != 71 && !shapeBlank)
				{
					memcpy(megaData2.shapes[x].sh, shape, sizeof(JE_DanCShape));

					y = 1;
					for (yy = 0; yy < (24 * 28) >> 1; yy++)
						if (shape[yy] == 0)
							y = 0;

					megaData2.shapes[x].fill = y;
					ref[1][x] = megaData2.shapes[x].sh;
				}
				else
				{
					ref[1][x] = NULL;
				}
			}
		}

		/*Match 3*/
		for (int x = 0; x <= 71; ++x)
		{
			if (mapSh[2][x] == z+1)
			{
				if (x < 70 && !shapeBlank)
				{
					memcpy(megaData3.shapes[x].sh, shape, sizeof(JE_DanCShape));

					y = 1;
					for (yy = 0; yy < (24 * 28) >> 1; yy++)
						if (shape[yy] == 0)
							y = 0;

					megaData3.shapes[x].fill = y;
					ref[2][x] = megaData3.shapes[x].sh;
				}
				else
				{
					ref[2][x] = NULL;
				}
			}
		}
	}

	fclose(shpFile);

	fread_u8_die(mapBuf, 14 * 300, level_f);
	bufLoc = 0;              /* MAP NUMBER 1 */
	for (y = 0; y < 300; y++)
	{
		for (x = 0; x < 14; x++)
		{
			megaData1.mainmap[y][x] = ref[0][mapBuf[bufLoc]];
			bufLoc++;
		}
	}

	fread_u8_die(mapBuf, 14 * 600, level_f);
	bufLoc = 0;              /* MAP NUMBER 2 */
	for (y = 0; y < 600; y++)
	{
		for (x = 0; x < 14; x++)
		{
			megaData2.mainmap[y][x] = ref[1][mapBuf[bufLoc]];
			bufLoc++;
		}
	}

	fread_u8_die(mapBuf, 15 * 600, level_f);
	bufLoc = 0;              /* MAP NUMBER 3 */
	for (y = 0; y < 600; y++)
	{
		for (x = 0; x < 15; x++)
		{
			megaData3.mainmap[y][x] = ref[2][mapBuf[bufLoc]];
			bufLoc++;
		}
	}

	fclose(level_f);

	++b3d_map_generation;
	p3d_clear();
	l3d_clear_departed_shots();
	b3d_note_tileset(char_shapeFile, (const Uint16 (*)[128])mapSh);
	if (l3d_enabled)
		b3d_prepare_sides();
	if (SDL_getenv("TYR3D_EXPORT_MAPS") != NULL)
		b3d_export_maps(SDL_getenv("TYR3D_EXPORT_MAPS"));

	/* Note: The map data is automatically calculated with the correct mapsh
	value and then the pointer is calculated using the formula (MAPSH-1)*168.
	Then, we'll automatically add S2Ofs to get the exact offset location into
	the shape table! This makes it VERY FAST! */

	/*debuginfo('Map file done.');*/
	/* End of find loop for LEVEL??.DAT */
}

#ifdef WITH_NETWORK
void networkStartScreen(void)
{
	JE_loadPic(VGAScreen, 2, false);
	memcpy(VGAScreen2->pixels, VGAScreen->pixels, VGAScreen2->pitch * VGAScreen2->h);
	JE_dString(VGAScreen, JE_fontCenter("Waiting for other player.", SMALL_FONT_SHAPES), 140, "Waiting for other player.", SMALL_FONT_SHAPES);
	JE_showVGA();
	fade_palette(colors, 10, 0, 255);

	network_connect();

	twoPlayerMode = true;
	if (thisPlayerNum == 1)
	{
		fade_black(10);

		if (episodeSelect() && difficultySelect())
		{
			initialDifficulty = difficultyLevel;

			difficultyLevel++;  /*Make it one step harder for 2-player mode!*/

			network_prepare(PACKET_DETAILS);
			SDLNet_Write16(episodeNum, &packet_out_temp->data[4]);
			SDLNet_Write16(difficultyLevel, &packet_out_temp->data[6]);
			network_send(8);  // PACKET_DETAILS
		}
		else
		{
			network_prepare(PACKET_QUIT);
			network_send(4);  // PACKET QUIT

			network_tyrian_halt(0, true);
		}
	}
	else
	{
		memcpy(VGAScreen->pixels, VGAScreen2->pixels, VGAScreen->pitch * VGAScreen->h);
		JE_dString(VGAScreen, JE_fontCenter(networkText[4 - 1], SMALL_FONT_SHAPES), 140, networkText[4 - 1], SMALL_FONT_SHAPES);
		JE_showVGA();

		// until opponent sends details packet
		while (true)
		{
			service_SDL_events(false);
			JE_showVGA();

			if (packet_in[0] && SDLNet_Read16(&packet_in[0]->data[0]) == PACKET_DETAILS)
				break;

			network_update();
			network_check();

			SDL_Delay(16);
		}

		JE_initEpisode(SDLNet_Read16(&packet_in[0]->data[4]));
		difficultyLevel = SDLNet_Read16(&packet_in[0]->data[6]);
		initialDifficulty = difficultyLevel - 1;
		fade_black(10);

		network_update();
	}

	for (uint i = 0; i < COUNTOF(player); ++i)
		player[i].cash = 0;

	player[0].items.ship = 11;  // Silver Ship

	while (!network_is_sync())
	{
		service_SDL_events(false);
		JE_showVGA();

		network_check();
		SDL_Delay(16);
	}
}
#endif /* WITH_NETWORK */

// Tyrian3D: the title's menu as it shows, for the modern UI (ui.h): the items where the original takes
// the mouse on them, what each does (ids: titleScreen's MenuItemIndex).
static void title_publish(size_t selected, const char *const *texts, const int *ids, size_t count, const int *widths, int x_centre,
                          int y_items, int h_item)
{
	static const char *const hints[] = {
		"A new game: the players, an episode and how hard.",
		"Go on with a game you saved.",
		"The best pilots of each episode.",
		"How to play: the controls, the ship, the shop.",
		"Graphics, 3D, sound and the jukebox.",
		"Watch a game play by itself.",
		"Leave Tyrian.",
		"The secret artillery duel: two armies, one battlefield.",
		"The secrets you have found, and what is still locked.",
	};
	UIMenu *menu = ui_menu_begin(UI_SCREEN_TITLE, "");
	for (size_t i = 0; i < count; ++i)
	{
		UIItem *item = ui_menu_add(menu, UI_ITEM_ACTION, texts[i], x_centre - widths[i] / 2, y_items + h_item * (int)i, widths[i],
		                           h_item);
		if (ids[i] >= 0 && ids[i] < (int)COUNTOF(hints))
			SDL_strlcpy(item->hint, hints[ids[i]], sizeof(item->hint));
	}
	menu->selected = (int)selected;
	SDL_strlcpy(menu->footer, TYRIAN3D_VERSION, sizeof(menu->footer));
	ui_menu_publish(menu, VGAScreen, VGAScreen2);
}

bool titleScreen(void)
{
	enum MenuItemIndex
	{
		MENU_ITEM_NEW_GAME = 0,
		MENU_ITEM_LOAD_GAME,
		MENU_ITEM_HIGH_SCORES,
		MENU_ITEM_INSTRUCTIONS,
		MENU_ITEM_SETUP,
		MENU_ITEM_DEMO,
		MENU_ITEM_QUIT,
		MENU_ITEM_DESTRUCT,  // Tyrian3D: once it has been found (destruct.h)
		MENU_ITEM_SECRETS,   // Tyrian3D: the secrets found and locked (secrets.h), where the instructions were
	};

	if (shopSpriteSheet.data == NULL)
		JE_loadCompShapes(&shopSpriteSheet, '1');  // need mouse pointer sprites

	bool restart = true;

	size_t selectedIndex = MENU_ITEM_NEW_GAME;
	size_t specialNameProgress[SA_ENGAGE] = { 0 };

	// Tyrian3D: the items shown, the original's and, once Destruct has been found, it before Demo (the
	// items a little closer to fit).
	const char *itemText[COUNTOF(menuText) + 1];
	int itemId[COUNTOF(menuText) + 1];
	size_t itemCount = 0;

	const int xCenter = VGAScreen->w / 2;
	int yMenuItems = 104;
	int hMenuItem = 13;
	int wMenuItem[COUNTOF(menuText) + 1] = { 0 };

	for (; ; )
	{
		if (restart)
		{
			itemCount = 0;
			for (int i = 0; i < (int)COUNTOF(menuText); ++i)
			{
				if (i == MENU_ITEM_INSTRUCTIONS)
				{
					// (The user: take the instructions away; the secrets in their place.)
					itemText[itemCount] = "Secrets";
					itemId[itemCount++] = MENU_ITEM_SECRETS;
					continue;
				}
				if (i == MENU_ITEM_DEMO && destruct_discovered())
				{
					itemText[itemCount] = "Destruct";
					itemId[itemCount++] = MENU_ITEM_DESTRUCT;
				}
				itemText[itemCount] = i == MENU_ITEM_SETUP ? "Settings" : menuText[i];
				itemId[itemCount++] = i;
			}
			hMenuItem = itemCount > COUNTOF(menuText) ? 12 : 13;
			yMenuItems = itemCount > COUNTOF(menuText) ? 98 : 104;
			selectedIndex = SDL_min(selectedIndex, itemCount - 1);

			play_song(SONG_TITLE);

			JE_loadPic(VGAScreen, 4, false);

			draw_font_hv_shadow(VGAScreen, 2, 192, TYRIAN3D_VERSION, small_font, left_aligned, 15, 0, false, 1);

			if (moveTyrianLogoUp)
			{
				memcpy(VGAScreen2->pixels, VGAScreen->pixels, VGAScreen2->pitch * VGAScreen2->h);

				blit_sprite(VGAScreenSeg, 11, 62, PLANET_SHAPES, 146); // tyrian logo
				blit_sprite(VGAScreenSeg, 155, 41, PLANET_SHAPES, 151); // 2000(tm)
				fade_palette(colors, 10, 0, 255 - 16);

				for (int yLogo = 60, y2K = 45; yLogo >= 4; yLogo -= 2, ++y2K)
				{
					setDelay(2);

					memcpy(VGAScreen->pixels, VGAScreen2->pixels, VGAScreen->pitch * VGAScreen->h);
					blit_sprite(VGAScreenSeg, 11, yLogo, PLANET_SHAPES, 146); // tyrian logo
					blit_sprite(VGAScreenSeg, 155, y2K, PLANET_SHAPES, 151); // 2000(tm)
					JE_showVGA();

					service_wait_delay();
				}
				moveTyrianLogoUp = false;
			}
			else
			{
				blit_sprite(VGAScreenSeg, 11, 4, PLANET_SHAPES, 146); // tyrian logo
				blit_sprite(VGAScreenSeg, 155, 73, PLANET_SHAPES, 151); // 2000(tm)
				fade_palette(colors, 10, 0, 255 - 16);
			}

			// Draw menu items.
			for (size_t i = 0; i < itemCount; ++i)
			{
				const char *const text = itemText[i];

				wMenuItem[i] = JE_textWidth(text, normal_font);
				const int y = yMenuItems + hMenuItem * i;

				// Tyrian3D: drawn centred (as they were at xCenter - wMenuItem[i] / 2), so the 3D view's texts are.
				const int x = xCenter;
				draw_font_hv(VGAScreen, x - 1, y - 1, itemText[i], normal_font, centered, 15, -10);
				draw_font_hv(VGAScreen, x + 1, y + 1, itemText[i], normal_font, centered, 15, -10);
				draw_font_hv(VGAScreen, x + 1, y - 1, itemText[i], normal_font, centered, 15, -10);
				draw_font_hv(VGAScreen, x - 1, y + 1, itemText[i], normal_font, centered, 15, -10);
				draw_font_hv(VGAScreen, x,     y,     itemText[i], normal_font, centered, 15, -3);
			}

			memcpy(VGAScreen2->pixels, VGAScreen->pixels, VGAScreen2->pitch * VGAScreen2->h);
			title_publish(selectedIndex, itemText, itemId, itemCount, wMenuItem, xCenter, yMenuItems, hMenuItem);

			mouseCursor = MOUSE_POINTER_NORMAL;

			// Fade in menu items.
			fade_palette(colors, 20, 255 - 16 + 1, 255);

			restart = false;
		}

		memcpy(VGAScreen->pixels, VGAScreen2->pixels, VGAScreen->pitch * VGAScreen->h);

		// Highlight selected menu item.
		draw_font_hv(VGAScreen, VGAScreen->w / 2, yMenuItems + hMenuItem * selectedIndex, itemText[selectedIndex], normal_font, centered, 15, -1);
		title_publish(selectedIndex, itemText, itemId, itemCount, wMenuItem, xCenter, yMenuItems, hMenuItem);

		service_SDL_events(true);

		JE_mouseStartFilter(0xF0);
		JE_showVGA();
		JE_mouseReplace();

		const Uint32 idleStartTick = SDL_GetTicks();

		bool mouseMoved = false;
		do
		{
			// Play demo after idle for 30 seconds.
			if (SDL_GetTicks() - idleStartTick > dev_demo_idle_ms())
			{
				fade_black(15);

				play_demo = true;
				return true;
			}

			SDL_Delay(16);

			Uint16 oldMouseX = mouse_x;
			Uint16 oldMouseY = mouse_y;

			push_joysticks_as_keyboard();
			service_SDL_events(false);

			mouseMoved = mouse_x != oldMouseX || mouse_y != oldMouseY;
		} while (!(newkey || new_text || newmouse || mouseMoved));

		// Handle interaction.

		bool action = false;
		bool done = false;

		if (mouseMoved || newmouse)
		{
			// Find menu item that was hovered or clicked.
			for (size_t i = 0; i < itemCount; ++i)
			{
				const int xMenuItem = xCenter - wMenuItem[i] / 2;
				if (mouse_x >= xMenuItem && mouse_x < xMenuItem + wMenuItem[i])
				{
					const int yMenuItem = yMenuItems + hMenuItem * i;
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
					? itemCount - 1
					: selectedIndex - 1;
				break;
			}
			case SDL_SCANCODE_DOWN:
			{
				JE_playSampleNum(S_CURSOR);

				selectedIndex = selectedIndex == itemCount - 1
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
			}
			default:
				break;
			}
		}

		if (new_text)
		{
			for (size_t ti = 0U; last_text[ti] != '\0'; ++ti)
			{
				const char c = toupper(last_text[ti]);

				for (size_t i = 0; i < SA_ENGAGE; i++)
				{
					if (specialNameProgress[i] >= COUNTOF(specialName[i]) - 1 ||
						c != specialName[i][specialNameProgress[i]])
					{
						specialNameProgress[i] = 0;
						continue;
					}

					specialNameProgress[i]++;

					if (specialName[i][specialNameProgress[i]] == '\0')
					{
						secrets_code((int)i);  // (Tyrian3D: secrets.h)
						if (i + 1 == SA_DESTRUCT)
						{
							fade_black(10);

							loadDestruct = true;
							return true;
						}
						else if (i + 1 == SA_ENGAGE)
						{
							JE_playSampleNum(V_DANGER);

							JE_whoa();
							set_colors((SDL_Color) { 0, 0, 0 }, 0, 255);

							if (newSuperTyrianGame())
								return true;

							restart = true;
						}
						else
						{
							fade_black(10);

							if (newSuperArcadeGame(i))
								return true;

							restart = true;
						}
					}
				}
			}
		}

		if (action)
		{
			JE_playSampleNum(S_SELECT);

			switch (itemId[selectedIndex])
			{
			case MENU_ITEM_NEW_GAME:
			{
				fade_black(15);

				if (newGame())
					return true;

				restart = true;
				break;
			}
			case MENU_ITEM_LOAD_GAME:
			{
				fade_black(15);

				if (JE_loadScreen())
					return true;

				restart = true;
				break;
			}
			case MENU_ITEM_HIGH_SCORES:
			{
				fade_black(15);

				JE_highScoreScreen();

				restart = true;
				break;
			}
			case MENU_ITEM_INSTRUCTIONS:
			{
				fade_black(15);

				JE_helpSystem(1);

				restart = true;
				break;
			}
			case MENU_ITEM_SETUP:
			{
				fade_black(15);

				setupMenu();
				if (debug_flight)
					return true;  // Tyrian3D: a debug flight was picked

				restart = true;
				break;
			}
			case MENU_ITEM_DEMO:
			{
				fade_black(15);

				play_demo = true;
				return true;
			}
			case MENU_ITEM_QUIT:
			{
				fade_black(15);

				return false;
			}
			case MENU_ITEM_SECRETS:
			{
				fade_black(15);

				secrets_screen();

				restart = true;
				break;
			}
			case MENU_ITEM_DESTRUCT:
			{
				// (As when its code is typed.)
				fade_black(10);

				loadDestruct = true;
				return true;
			}
			default:
				break;
			}
		}

		if (done)
		{
			fade_black(15);

			return false;
		}
	}
}

bool newGame(void)
{
	if (gameplaySelect())
	{
		if (rogue_run)
			return true;  // Tyrian3D: a rogue run, set up (rogue.h)

		if (timedBattleMode)
		{
			onePlayerAction = true;
			if (timedBattleSelect() && difficultySelect())
				gameLoaded = true;
		}
		else if (episodeSelect() && difficultySelect())
			gameLoaded = true;

		initialDifficulty = difficultyLevel;

		if (onePlayerAction)
		{
			player[0].cash = 0;

			player[0].items.ship = 8;  // Stalker
		}
		else if (twoPlayerMode)
		{
			for (uint i = 0; i < COUNTOF(player); ++i)
				player[i].cash = 0;

			player[0].items.ship = 11;  // Silver Ship

			// Tyrian3D: twin-stick (player.h), one player alone: both inputs "any" (as its saves keep
			// it), the difficulty as chosen (two players' is a step harder).
			if (twinStickMode)
			{
				inputDevice[0] = inputDevice[1] = 0;
			}
			else
			{
				difficultyLevel++;

				inputDevice[0] = 1;
				inputDevice[1] = 2;
			}
		}
		else if (richMode)
		{
			player[0].cash = 1000000;
		}
		else if (gameLoaded)
		{
			// allows player to smuggle arcade/super-arcade ships into full game

			const ulong initial_cash[] = { 10000, 15000, 20000, 30000, 20000, 30000, 10000 };  // Tyrian3D: + episodes 6, 7

			assert(episodeNum >= 1 && episodeNum <= EPISODE_MAX);
			player[0].cash = initial_cash[episodeNum - 1];
		}
	}

	return gameLoaded;
}

bool newSuperArcadeGame(unsigned int i)
{
	player[0].items.ship = SAShip[i];

	if (episodeSelect() && difficultySelect())
	{
		/* Start special mode! */
		JE_loadPic(VGAScreen, 1, false);
		JE_clr256(VGAScreen);
		JE_dString(VGAScreen, JE_fontCenter(superShips[0], FONT_SHAPES), 30, superShips[0], FONT_SHAPES);
		JE_dString(VGAScreen, JE_fontCenter(superShips[i + 1], SMALL_FONT_SHAPES), 100, superShips[i + 1], SMALL_FONT_SHAPES);
		tempW = ships[player[0].items.ship].shipgraphic;
		if (tempW > 500)
			blit_sprite2x2(VGAScreen, 148, 70, spriteSheetT2000, tempW - 500);
		else if (tempW != 1)
			blit_sprite2x2(VGAScreen, 148, 70, spriteSheet9, tempW);

		// Tyrian3D: the modern UI's card (mainint.h): the mode and its ship.
		card_publish(superShips[0], superShips[i + 1], NULL, NULL,
		             tempW > 500 ? (const void *)&spriteSheetT2000 : tempW != 1 ? (const void *)&spriteSheet9 : NULL,
		             tempW > 500 ? tempW - 500 : tempW, true, false);
		JE_showVGA();
		fade_palette(colors, 50, 0, 255);

		wait_input(true, true, true);

		twoPlayerMode = false;
		onePlayerAction = true;
		superArcadeMode = i + 1;
		timedBattleMode = false;
		gameLoaded = true;
		initialDifficulty = ++difficultyLevel;

		player[0].cash = 0;

		player[0].items.weapon[FRONT_WEAPON].id = SAWeapon[i][0];
		player[0].items.special = SASpecialWeapon[i];
		if (superArcadeMode == SA_NORTSHIPZ)
		{
			for (uint i = 0; i < COUNTOF(player[0].items.sidekick); ++i)
				player[0].items.sidekick[i] = 24;  // Companion Ship Quicksilver
		}

		fade_black(10);
	}

	return gameLoaded;
}

bool newSuperTyrianGame(void)
{
	/* SuperTyrian */

	initialDifficulty = keysactive[SDL_SCANCODE_SCROLLLOCK] ? DIFFICULTY_SUICIDE : DIFFICULTY_ZINGLON;

	JE_clr256(VGAScreen);
	JE_outText(VGAScreen, 10, 10, superTyrianText[0], 15, 4);
	if (initialDifficulty == DIFFICULTY_ZINGLON)
		JE_outText(VGAScreen, 10, 20, superTyrianText[1], 15, 4);
	else
		JE_outText(VGAScreen, 10, 20, superTyrianText[2], 15, 4);
	JE_outText(VGAScreen, 10, 30, superTyrianText[3], 15, 4);
	if (initialDifficulty == DIFFICULTY_ZINGLON)
		JE_outText(VGAScreen, 10, 40, superTyrianText[4], 15, 4);
	JE_outText(VGAScreen, 10, 60, superTyrianText[5], 15, 4);

	char buf[10 + 1 + 15 + 1];
	snprintf(buf, sizeof(buf), "%s %s", miscTextB[4], pName[0]);
	JE_dString(VGAScreen, JE_fontCenter(buf, FONT_SHAPES), 110, buf, FONT_SHAPES);

	play_song(16);
	JE_playSampleNum(V_GOOD_LUCK);

	JE_showVGA();
	fade_palette(colors, 10, 0, 255);

	wait_noinput(true, true, true);
	wait_input(true, true, true);

	fade_black(1);
	if (episodeSelect()) // T2000 let you choose the starting episode
	{
		constantDie = false;
		superTyrian = true;
		onePlayerAction = true;
		timedBattleMode = false;
		gameLoaded = true;
		difficultyLevel = initialDifficulty;

		player[0].cash = 0;

		player[0].items.ship = 13;                     // The Stalker 21.126
		player[0].items.weapon[FRONT_WEAPON].id = 39;  // Atomic RailGun

		fade_black(10);
		return true;
	}
	else
	{
		play_song(SONG_TITLE);
		return false;
	}

}

void intro_logos(void)
{
	moveTyrianLogoUp = true;

	SDL_FillSurfaceRect(VGAScreen, NULL, 0);

	// Tyrian3D: the first logo comes in from black (the original flashed the screen to white first).
	fade_black(1);

	JE_loadPic(VGAScreen, 10, false);
	JE_showVGA();

	fade_palette(colors, 25, 0, 255);

	setDelay(200);
	wait_delayorinput();

	fade_black(10);

	// (Tyrian3D: the Eclipse logo shows whole, its name at its bottom: ui_fit_screen.)
	ui_fit_screen = true;
	JE_loadPic(VGAScreen, 12, false);
	JE_showVGA();

	fade_palette(colors, 10, 0, 255);

	setDelay(200);
	wait_delayorinput();

	fade_black(10);
	ui_fit_screen = false;
}

void JE_readTextSync(void)
{
#if 0  // this function seems to be unnecessary
	JE_clr256(VGAScreen);
	JE_showVGA();
	JE_loadPic(VGAScreen, 1, true);

	JE_barShade(VGAScreen, 3, 3, 316, 196);
	JE_barShade(VGAScreen, 1, 1, 318, 198);
	JE_dString(VGAScreen, 10, 160, "Waiting for other player.", SMALL_FONT_SHAPES);
	JE_showVGA();

	/* TODO: NETWORK */

	do
	{
		setjasondelay(2);

		/* TODO: NETWORK */

		wait_delay();

	} while (0 /* TODO: NETWORK */);
#endif
}

void JE_displayText(void)
{
	/* Display Warning Text */
	JE_word tempY = 55;
	if (warningRed)
	{
		tempY = 2;
	}
	for (temp = 0; temp < levelWarningLines; temp++)
	{
		if (!ESCPressed)
		{
			story_line(temp);  // Tyrian3D: the modern UI's (mainint.h)
			JE_outCharGlow(10, tempY, levelWarningText[temp]);

			if (haltGame)
			{
				JE_tyrianHalt(5);
			}

			tempY += 10;
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
	textGlowFont = TINY_FONT;
	tempW = 184;
	if (warningRed)
		tempW = 7 * 16 + 6;

	story_line(levelWarningLines);  // (all shown: "press a key")
	JE_outCharGlow(JE_fontCenter(miscText[4], TINY_FONT), tempW, miscText[4]);
	story_refresh();

	bool released = false;  // (Tyrian3D: see below)
	for (;;)
	{
		if (levelWarningDisplay)
			JE_updateWarning(VGAScreen);

		setDelay(1);

		NETWORK_KEEP_ALIVE();

		wait_delay();

		// (Tyrian3D: a mouse or pad button already held as the text comes, firing as the level ended or as the warp orb
		// was picked up, counts only once let go: it skipped the text at once, VAULT's arrival among them.)
		const bool any = JE_anyButton();
		if (any && (newkey || released))
			break;
		if ((frameCountMax == 0 && temp == 1) || ESCPressed)
			break;
		released = released || !(mousedown || joydown);
	}
	levelWarningDisplay = false;
	story_end();
}

Sint16 JE_newEnemy(int enemyOffset, Uint16 eDatI, Sint16 uniqueShapeTableI)
{
	for (int i = enemyOffset; i < enemyOffset + 25; ++i)
	{
		if (enemyAvail[i] == 1)
		{
			enemyAvail[i] = JE_makeEnemy(&enemy[i], eDatI, uniqueShapeTableI);
			enemy_group[i] = 0;  // (Tyrian3D: a piece of no object, unless the caller says)
			enemy_group_link[i] = 0;
			gbc_object[i] = 0;
			gbc_look_id[i] = 0;
			gbc_look_parts[i] = 0;
			gbc_lean[i] = NAN;
			return i + 1;
		}
	}
	
	return 0;
}

uint JE_makeEnemy(struct JE_SingleEnemyType *enemy, Uint16 eDatI, Sint16 uniqueShapeTableI)
{
	uint avail;

	JE_byte shapeTableI;

	if (superArcadeMode != SA_NONE && eDatI == 534)
		eDatI = 533;

	if (uniqueShapeTableI > 0)
	{
		shapeTableI = uniqueShapeTableI;
	}
	else
	{
		shapeTableI = enemyDat[eDatI].shapebank;
	}

	Sprite2_array *sprite2s = NULL;
	if (shapeTableI == 21)
	{
		sprite2s = &spriteSheet11;  // Coins&Gems
	}
	else if (shapeTableI == 26)
	{
		sprite2s = &spriteSheet10;  // Two-Player Stuff
	}
	else
	{
		for (size_t i = 0; i < COUNTOF(enemySpriteSheetIds); ++i)
			if (shapeTableI == enemySpriteSheetIds[i])
				sprite2s = &enemySpriteSheets[i];
	}
	
	if (sprite2s != NULL)
		enemy->sprite2s = sprite2s;
	else
		// Use shape table value from previous enemy that occupied the enemy slot. (Ex. APPROACH.)
		fprintf(stderr, "warning: ignoring sprite from unloaded shape table %d (enemy %u)\n", shapeTableI, (unsigned)eDatI);

	enemy->enemydatofs = &enemyDat[eDatI];

	enemy->mapoffset = 0;

	for (uint i = 0; i < 3; ++i)
	{
		enemy->eshotmultipos[i] = 0;
	}

	enemy->enemyground = (enemyDat[eDatI].explosiontype & 1) == 0;
	enemy->explonum = enemyDat[eDatI].explosiontype >> 1;

	enemy->launchfreq = enemyDat[eDatI].elaunchfreq;
	enemy->launchwait = enemyDat[eDatI].elaunchfreq;

	// T2000 ... Account for the second enemy bank only if we're creating something from it
	if (eDatI > 1000)
	{
		enemy->launchtype = enemyDat[eDatI].elaunchtype;
		enemy->launchspecial = 0;
	}
	else
	{
		enemy->launchtype = enemyDat[eDatI].elaunchtype % 1000;
		enemy->launchspecial = enemyDat[eDatI].elaunchtype / 1000;
	}

	enemy->xaccel = enemyDat[eDatI].xaccel;
	enemy->yaccel = enemyDat[eDatI].yaccel;

	enemy->xminbounce = -10000;
	enemy->xmaxbounce = 10000;
	enemy->yminbounce = -10000;
	enemy->ymaxbounce = 10000;
	/*Far enough away to be impossible to reach*/

	for (uint i = 0; i < 3; ++i)
	{
		enemy->tur[i] = enemyDat[eDatI].tur[i];
	}

	enemy->ani = enemyDat[eDatI].ani;
	enemy->animin = 1;

	switch (enemyDat[eDatI].animate)
	{
	case 0:
		enemy->enemycycle = 1;
		enemy->aniactive = 0;
		enemy->animax = 0;
		enemy->aniwhenfire = 0;
		break;
	case 1:
		enemy->enemycycle = 0;
		enemy->aniactive = 1;
		enemy->animax = 0;
		enemy->aniwhenfire = 0;
		break;
	case 2:
		enemy->enemycycle = 1;
		enemy->aniactive = 2;
		enemy->animax = enemy->ani;
		enemy->aniwhenfire = 2;
		break;
	}

	if (enemyDat[eDatI].startxc != 0)
		enemy->ex = enemyDat[eDatI].startx + (mt_rand() % (enemyDat[eDatI].startxc * 2)) - enemyDat[eDatI].startxc + 1;
	else
		enemy->ex = enemyDat[eDatI].startx + 1;

	if (enemyDat[eDatI].startyc != 0)
		enemy->ey = enemyDat[eDatI].starty + (mt_rand() % (enemyDat[eDatI].startyc * 2)) - enemyDat[eDatI].startyc + 1;
	else
		enemy->ey = enemyDat[eDatI].starty + 1;

	enemy->exc = enemyDat[eDatI].xmove;
	enemy->eyc = enemyDat[eDatI].ymove;
	enemy->excc = enemyDat[eDatI].xcaccel;
	enemy->eycc = enemyDat[eDatI].ycaccel;
	enemy->exccw = abs(enemy->excc);
	enemy->exccwmax = enemy->exccw;
	enemy->eyccw = abs(enemy->eycc);
	enemy->eyccwmax = enemy->eyccw;
	enemy->exccadd = (enemy->excc > 0) ? 1 : -1;
	enemy->eyccadd = (enemy->eycc > 0) ? 1 : -1;
	enemy->special = false;
	enemy->iced = 0;

	if (enemyDat[eDatI].xrev == 0)
		enemy->exrev = 100;
	else if (enemyDat[eDatI].xrev == -99)
		enemy->exrev = 0;
	else
		enemy->exrev = enemyDat[eDatI].xrev;

	if (enemyDat[eDatI].yrev == 0)
		enemy->eyrev = 100;
	else if (enemyDat[eDatI].yrev == -99)
		enemy->eyrev = 0;
	else
		enemy->eyrev = enemyDat[eDatI].yrev;

	enemy->exca = (enemy->xaccel > 0) ? 1 : -1;
	enemy->eyca = (enemy->yaccel > 0) ? 1 : -1;

	enemy->enemytype = eDatI;

	for (uint i = 0; i < 3; ++i)
	{
		if (enemy->tur[i] == 252)
			enemy->eshotwait[i] = 1;
		else if (enemy->tur[i] > 0)
			enemy->eshotwait[i] = 20;
		else
			enemy->eshotwait[i] = 255;
	}
	for (uint i = 0; i < 20; ++i)
		enemy->egr[i] = enemyDat[eDatI].egraphic[i];
	enemy->size = enemyDat[eDatI].esize;
	enemy->linknum = 0;
	gbc_pool_forget(enemy);  // (Tyrian3D)
	enemy->edamaged = enemyDat[eDatI].dani < 0;
	enemy->enemydie = enemyDat[eDatI].eenemydie;

	enemy->freq[1-1] = enemyDat[eDatI].freq[1-1];
	enemy->freq[2-1] = enemyDat[eDatI].freq[2-1];
	enemy->freq[3-1] = enemyDat[eDatI].freq[3-1];

	enemy->edani   = enemyDat[eDatI].dani;
	enemy->edgr    = enemyDat[eDatI].dgr;
	enemy->edlevel = enemyDat[eDatI].dlevel;

	enemy->fixedmovey = 0;

	enemy->filter = 0x00;

	int tempValue = 0;
	if (enemyDat[eDatI].value > 1 && enemyDat[eDatI].value < 10000)
	{
		switch (difficultyLevel)
		{
		case -1:
		case DIFFICULTY_WIMP:
			tempValue = enemyDat[eDatI].value * 0.75f;
			break;
		case DIFFICULTY_EASY:
		case DIFFICULTY_NORMAL:
			tempValue = enemyDat[eDatI].value;
			break;
		case DIFFICULTY_HARD:
			tempValue = enemyDat[eDatI].value * 1.125f;
			break;
		case DIFFICULTY_IMPOSSIBLE:
			tempValue = enemyDat[eDatI].value * 1.5f;
			break;
		case DIFFICULTY_INSANITY:
			tempValue = enemyDat[eDatI].value * 2;
			break;
		case DIFFICULTY_SUICIDE:
			tempValue = enemyDat[eDatI].value * 2.5f;
			break;
		case DIFFICULTY_MANIACAL:
		case DIFFICULTY_ZINGLON:
			tempValue = enemyDat[eDatI].value * 4;
			break;
		case DIFFICULTY_NORTANEOUS:
		case DIFFICULTY_10:
			tempValue = enemyDat[eDatI].value * 8;
			break;
		}
		if (tempValue > 10000)
			tempValue = 10000;
		enemy->evalue = tempValue;
	}
	else
	{
		enemy->evalue = enemyDat[eDatI].value;
	}

	int tempArmor = 1;
	if (enemyDat[eDatI].armor > 0)
	{
		if (enemyDat[eDatI].armor != 255)
		{
			switch (difficultyLevel)
			{
			case -1:
			case DIFFICULTY_WIMP:
				tempArmor = enemyDat[eDatI].armor * 0.5f + 1;
				break;
			case DIFFICULTY_EASY:
				tempArmor = enemyDat[eDatI].armor * 0.75f + 1;
				break;
			case DIFFICULTY_NORMAL:
				tempArmor = enemyDat[eDatI].armor;
				break;
			case DIFFICULTY_HARD:
				tempArmor = enemyDat[eDatI].armor * 1.2f;
				break;
			case DIFFICULTY_IMPOSSIBLE:
				tempArmor = enemyDat[eDatI].armor * 1.5f;
				break;
			case DIFFICULTY_INSANITY:
				tempArmor = enemyDat[eDatI].armor * 1.8f;
				break;
			case DIFFICULTY_SUICIDE:
				tempArmor = enemyDat[eDatI].armor * 2;
				break;
			case DIFFICULTY_MANIACAL:
				tempArmor = enemyDat[eDatI].armor * 3;
				break;
			case DIFFICULTY_ZINGLON:
				tempArmor = enemyDat[eDatI].armor * 4;
				break;
			case DIFFICULTY_NORTANEOUS:
			case DIFFICULTY_10:
				tempArmor = enemyDat[eDatI].armor * 8;
				break;
			}

			if (tempArmor > 254)
			{
				tempArmor = 254;
			}
		}
		else
		{
			tempArmor = 255;
		}

		enemy->armorleft = tempArmor;

		avail = 0;
		enemy->scoreitem = false;
	}
	else
	{
		avail = 2;
		enemy->armorleft = 255;
		if (enemy->evalue != 0)
			enemy->scoreitem = true;
	}

	if (!enemy->scoreitem)
	{
		totalEnemy++;  /*Destruction ratio*/
		dev_balance("spawn", enemy->enemytype);  // Tyrian3D dev
	}

	/* indicates what to set ENEMYAVAIL to */
	return avail;
}

void JE_createNewEventEnemy(JE_byte enemyTypeOfs, JE_word enemyOffset, Sint16 uniqueShapeTableI)
{
	int i;

	b = 0;

	for (i = enemyOffset; i < enemyOffset + 25; i++)
	{
		if (enemyAvail[i] == 1)
		{
			b = i + 1;
			break;
		}
	}

	if (b == 0)
		return;

	tempW = eventRec[eventLoc-1].eventdat + enemyTypeOfs;

	enemyAvail[b-1] = JE_makeEnemy(&enemy[b-1], tempW, uniqueShapeTableI);
	enemy_group[b-1] = (Uint32)eventRec[eventLoc-1].eventtime + 1;  // (Tyrian3D)
	enemy_group_link[b-1] = (Uint8)eventRec[eventLoc-1].eventdat4;
	if (episodeNum == EPISODE_GBC)
	{
		// (Tyrian3D: the GBC enemy it is a piece of: the event 201 just before that names it among its next ones, or
		// its own event; a new one at each event's first, at an event again (a loop) or another 201's)
		const int e = eventLoc - 1;
		int head = e;
		for (int k = e - 1; k >= 0 && k >= e - 32; --k)
			if (eventRec[k].eventtype == 201)
			{
				if (k + eventRec[k].eventdat >= e && eventRec[k].eventtime == eventRec[e].eventtime)
					head = k;
				break;
			}
		if (enemyTypeOfs == 0 && (head == e || head != gbc_object_head || e <= gbc_object_event))
			++gbc_objects;
		gbc_object_head = head;
		gbc_object_event = e;
		gbc_object[b-1] = gbc_objects;
		gbc_fight(&enemy[b-1], head);
	}
	else
		gbc_object[b-1] = 0;
	gbc_lean[b-1] = NAN;
	gbc_look_id[b-1] = 0;
	gbc_look_parts[b-1] = 0;
	if (episodeNum == EPISODE_GBC && enemyTypeOfs == 0)
	{
		// (Tyrian3D: its parts of its boss's look, the events 202 right before its own)
		const int e = eventLoc - 1;
		for (int k = e - 1; k >= 0 && eventRec[k].eventtype == 202 && eventRec[k].eventtime == eventRec[e].eventtime; --k)
		{
			gbc_look_id[b-1] = eventRec[k].eventdat4;
			if (eventRec[k].eventdat > 0 && gbc_look_parts[b-1] < GBC_LOOK_PARTS)
			{
				const Uint32 key = GBC_COMING_LOOK_KEY(k);
				gbc_look[b-1][gbc_look_parts[b-1]++] = (GbcLookPart){
					.sprite = (Uint16)eventRec[k].eventdat, .sheet = (char)eventRec[k].eventdat3,
					.large = eventRec[k].eventdat6 != 0, .dx = eventRec[k].eventdat2, .dy = eventRec[k].eventdat5,
					.forecast = l3d_key_seen(key) ? key : 0 };
			}
		}
	}

	// When T2000 gives an X position of -200, what it actually wants is a random X position...
	if (eventRec[eventLoc-1].eventdat2 == -200)
	{
		// Ranged 24 - 231
		eventRec[eventLoc-1].eventdat2 = (mt_rand() % 208) + 24;
	}

	if (eventRec[eventLoc-1].eventdat2 != -99)
	{
		switch (enemyOffset)
		{
		case 0:
			enemy[b-1].ex = eventRec[eventLoc-1].eventdat2 - (mapX - 1) * 24;
			enemy[b-1].ey -= backMove2;
			break;
		case 25:
		case 75:
			enemy[b-1].ex = eventRec[eventLoc-1].eventdat2 - (mapX - 1) * 24 - 12;
			enemy[b-1].ey -= backMove;
			break;
		case 50:
			if (background3x1)
				enemy[b-1].ex = eventRec[eventLoc-1].eventdat2 - (mapX - 1) * 24 - 12;
			else
				enemy[b-1].ex = eventRec[eventLoc-1].eventdat2 - mapX3 * 24 - 24 * 2 + 6;
			enemy[b-1].ey -= backMove3;

			if (background3x1b)
				enemy[b-1].ex -= 6;
			break;
		}
		enemy[b-1].ey = -28;
		if (background3x1b && enemyOffset == 50)
			enemy[b-1].ey += 4;
		// Tyrian3D: on a playfield reaching above the screen, made ahead of time that far up
		// (prespawn_events), and as far back along a steady sideways course; or, not coming down
		// (not even carried, steadily) nor placed lower, sky and top ones at the playfield's top.
		if (prespawn_rise > 0)
		{
			enemy[b-1].ey -= prespawn_rise;
			if (enemy[b-1].excc == 0)
				enemy[b-1].ex -= enemy[b-1].exc * prespawn_ticks;
		}
		else if (l3d_field_ahead > 0 && enemyOffset != 25 && enemyOffset != 75 && eventRec[eventLoc-1].eventdat5 <= 0 &&
		         enemy[b-1].eycc == 0 && enemy[b-1].yaccel == 0 &&
		         enemy[b-1].eyc + eventRec[eventLoc-1].eventdat3 + eventRec[eventLoc-1].eventdat6 +
		         (enemyOffset == 50 ? backMove3 : 0) <= 0)
			enemy[b-1].ey -= l3d_field_ahead;
		// Ground ones driving up the screen faster than the ground scrolls (never seen in the
		// original) out of sight too.
		else if (l3d_field_ahead > 0 && (enemyOffset == 25 || enemyOffset == 75) && eventRec[eventLoc-1].eventdat5 <= 0 &&
		         enemy[b-1].eycc == 0 && enemy[b-1].yaccel == 0 &&
		         enemy[b-1].eyc + eventRec[eventLoc-1].eventdat3 + eventRec[eventLoc-1].eventdat6 + backMove < 0)
			enemy[b-1].ey -= l3d_field_ahead;
	}
	else if (prespawn_rise > 0)
	{
		// Tyrian3D: at its data's start position above the screen, made ahead of time that far up
		// (prespawn_events: own_start_rise), and as far back along a steady sideways course.
		enemy[b-1].ey -= prespawn_rise;
		if (enemy[b-1].excc == 0)
			enemy[b-1].ex -= enemy[b-1].exc * prespawn_ticks;
	}
	else if (l3d_field_ahead > 0 && enemyOffset != 25 && enemyOffset != 75 && eventRec[eventLoc-1].eventdat5 <= 0 &&
	         enemy[b-1].ey + (enemy[b-1].size == 1 ? 28 : 14) <= 0 && enemy[b-1].eycc == 0 && enemy[b-1].yaccel == 0 &&
	         enemy[b-1].eyc + eventRec[eventLoc-1].eventdat3 + eventRec[eventLoc-1].eventdat6 +
	         (enemyOffset == 50 ? backMove3 : 0) <= 0)
	{
		// Tyrian3D: above the screen and not coming down: above the playfield's top too.
		enemy[b-1].ey -= l3d_field_ahead;
	}

	if (smallEnemyAdjust && enemy[b-1].size == 0)
	{
		enemy[b-1].ex -= 10;
		enemy[b-1].ey -= 7;
	}

	enemy[b-1].ey += eventRec[eventLoc-1].eventdat5;
	enemy[b-1].eyc += eventRec[eventLoc-1].eventdat3;
	enemy[b-1].linknum = eventRec[eventLoc-1].eventdat4;
	enemy[b-1].fixedmovey = eventRec[eventLoc-1].eventdat6;
	gbc_pool_join(b - 1);  // (Tyrian3D: a GBC boss's piece joins its body)

	// Tyrian3D: the forecast it takes the place of, if the 3D view showed it coming (enemy_shown).
	{
		const Uint32 key = COMING_KEY + (Uint32)((eventLoc - 1) * 4 + enemyTypeOfs) * 4 + (tempW & 3);
		enemy_forecast[b-1] = l3d_key_seen(key) ? key : 0;
	}

	// Tyrian3D dev: whether the 3D view showed the enemy coming (draw_coming_enemies).
	if (SDL_getenv("TYR3D_LOG_SPAWNS") != NULL)
	{
		const int e = eventLoc - 1;
		const Uint32 key = COMING_KEY + (Uint32)(e * 4 + enemyTypeOfs) * 4 + (tempW & 3);
		float px = 0, py = 0;
		const bool seen = l3d_key_seen(key) && l3d_key_position(key, &px, &py);
		printf("spawn: %s event %d type %d slot %d/%d enemy %u at %d,%d moving %d,%d+%d swing %d,%d steer %d,%d %s (shown at %.1f,%.1f); backMove %d/%d/%d delay %d armor %u link %u (3D frame %u)\n",
		       levelName, e, eventRec[e].eventtype, enemyOffset, b - 1, tempW, enemy[b-1].ex, enemy[b-1].ey, enemy[b-1].exc, enemy[b-1].eyc,
		       enemy[b-1].fixedmovey, enemy[b-1].excc, enemy[b-1].eycc, enemy[b-1].xaccel, enemy[b-1].yaccel,
		       seen ? "predicted" : "POPS", px - 6, py - 7, backMove, backMove2, backMove3, map1YDelayMax,
		       enemy[b-1].armorleft, enemy[b-1].linknum, l3d_frame_number);
	}
}

void JE_eventJump(JE_word jump)
{
	JE_word tempW;

	// Tyrian3D dev: TYR3D_LOG_JUMPS prints the level's clock jumps (loops, timers, mid-level bosses).
	if (SDL_getenv("TYR3D_LOG_JUMPS") != NULL)
		printf("jump: clock %u -> %u\n", (unsigned)curLoc, jump == 65535 ? (unsigned)returnLoc : (unsigned)jump);

	if (jump == 65535)
	{
		curLoc = returnLoc;
	}
	else
	{
		returnLoc = curLoc + 1;
		curLoc = jump;
	}
	tempW = 0;
	do
	{
		tempW++;
	} while (!(eventRec[tempW-1].eventtime >= curLoc));
	eventLoc = tempW - 1;
}

bool JE_searchFor/*enemy*/(JE_byte PLType, JE_byte* out_index)
{
	int found_id = -1;

	for (int i = 0; i < 100; i++)
	{
		if (enemyAvail[i] == 0 && enemy[i].linknum == PLType)
		{
			found_id = i;
			if (galagaMode)
				enemy[i].evalue += enemy[i].evalue;
		}
	}

	if (found_id != -1)
	{
		if (out_index)
			*out_index = found_id;
		return true;
	}
	else
	{
		return false;
	}
}

void JE_eventSystem(void)
{
	// Tyrian3D dev: TYR3D_LOG_EVENTS prints each event as the clock reaches it.
	static int log_events = -1;
	if (log_events < 0)
		log_events = SDL_getenv("TYR3D_LOG_EVENTS") != NULL;
	if (log_events)
	{
		const struct JE_EventRecType *ev = &eventRec[eventLoc-1];
		printf("event %d at %u (clock %u): type %u dat %d %d %d %u %d %d (3D frame %u)\n", eventLoc - 1, ev->eventtime,
		       (unsigned)curLoc, ev->eventtype, ev->eventdat, ev->eventdat2, ev->eventdat3, ev->eventdat4, ev->eventdat5,
		       ev->eventdat6, l3d_frame_number);
	}

	switch (eventRec[eventLoc-1].eventtype)
	{
	case 1:
		starfield_speed = eventRec[eventLoc-1].eventdat;
		break;

	case 2:
		if (SDL_getenv("TYR3D_LOG_JUMPS") != NULL)
			printf("speeds: clock %u: %d %d %d\n", (unsigned)curLoc, eventRec[eventLoc-1].eventdat,
			       eventRec[eventLoc-1].eventdat2, eventRec[eventLoc-1].eventdat3);
		map1YDelay = 1;
		map1YDelayMax = 1;
		map2YDelay = 1;
		map2YDelayMax = 1;

		backMove = eventRec[eventLoc-1].eventdat;
		backMove2 = eventRec[eventLoc-1].eventdat2;

		if (backMove2 > 0 && episodeNum != EPISODE_GBC)
			explodeMove = backMove2;
		else
			explodeMove = backMove;  // (Tyrian3D: episode 7's with the ground, its background 2 the faster clouds)

		backMove3 = eventRec[eventLoc-1].eventdat3;

		if (backMove > 0)
			stopBackgroundNum = 0;
		break;

	case 3:
		backMove = 1;
		map1YDelay = 3;
		map1YDelayMax = 3;
		backMove2 = 1;
		map2YDelay = 2;
		map2YDelayMax = 2;
		backMove3 = 1;
		break;

	case 4: // Map stop
	case 83: // T2000: Also a map stop 
		stopBackgrounds = true;
		switch (eventRec[eventLoc-1].eventdat)
		{
		case 0:
		case 1:
			stopBackgroundNum = 1;
			break;
		case 2:
			stopBackgroundNum = 2;
			break;
		case 3:
			stopBackgroundNum = 3;
			break;
		}
		break;

	case 5:  // load enemy shape banks
		{
			const Uint8 newEnemyShapeTables[] =
			{
				eventRec[eventLoc-1].eventdat > 0 ? eventRec[eventLoc-1].eventdat : 0,
				eventRec[eventLoc-1].eventdat2 > 0 ? eventRec[eventLoc-1].eventdat2 : 0,
				eventRec[eventLoc-1].eventdat3 > 0 ? eventRec[eventLoc-1].eventdat3 : 0,
				eventRec[eventLoc-1].eventdat4 > 0 ? eventRec[eventLoc-1].eventdat4 : 0,
			};
			
			for (unsigned int i = 0; i < COUNTOF(newEnemyShapeTables); ++i)
			{
				if (enemySpriteSheetIds[i] != newEnemyShapeTables[i])
				{
					if (newEnemyShapeTables[i] > 0)
					{
						assert(newEnemyShapeTables[i] <= COUNTOF(shapeFile));
						JE_loadCompShapes(&enemySpriteSheets[i], shapeFile[newEnemyShapeTables[i] - 1]);
					}
					else
						free_sprite2s(&enemySpriteSheets[i]);

					enemySpriteSheetIds[i] = newEnemyShapeTables[i];
				}
			}
		}
		break;

	case 6: /* Ground Enemy */
		JE_createNewEventEnemy(0, 25, 0);
		break;

	case 7: /* Top Enemy */
		JE_createNewEventEnemy(0, 50, 0);
		break;

	case 8:
		starActive = false;
		break;

	case 9:
		starActive = true;
		break;

	case 10: /* Ground Enemy 2 */
		JE_createNewEventEnemy(0, 75, 0);
		break;

	case 11:
		if (allPlayersGone || eventRec[eventLoc-1].eventdat == 1)
		{
			reallyEndLevel = true;
		}
		else if (!endLevel)
		{
			readyToEndLevel = false;
			endLevel = true;
			levelEnd = 40;
		}
		break;

	case 12: /* Custom 4x4 Ground Enemy */
		{
			uint temp = 0;
			switch (eventRec[eventLoc-1].eventdat6)
			{
			case 0:
			case 1:
				temp = 25;
				break;
			case 2:
				temp = 0;
				break;
			case 3:
				temp = 50;
				break;
			case 4:
				temp = 75;
				break;
			}
			eventRec[eventLoc-1].eventdat6 = 0;   /* We use EVENTDAT6 for the background */
			JE_createNewEventEnemy(0, temp, 0);
			JE_createNewEventEnemy(1, temp, 0);
			if (b > 0)
				enemy[b-1].ex += 24;
			JE_createNewEventEnemy(2, temp, 0);
			if (b > 0)
				enemy[b-1].ey -= 28;
			JE_createNewEventEnemy(3, temp, 0);
			if (b > 0)
			{
				enemy[b-1].ex += 24;
				enemy[b-1].ey -= 28;
			}
			break;
		}
	case 13:
		enemiesActive = false;
		break;

	case 14:
		enemiesActive = true;
		break;

	case 15: /* Sky Enemy */
		JE_createNewEventEnemy(0, 0, 0);
		break;

	case 16:
		if (eventRec[eventLoc-1].eventdat > 9)
		{
			fprintf(stderr, "warning: event 16: bad event data\n");
		}
		else
		{
			JE_drawTextWindow(outputs[eventRec[eventLoc-1].eventdat-1]);
			soundQueue[3] = windowTextSamples[eventRec[eventLoc-1].eventdat-1];
		}
		break;

	case 17: /* Ground Bottom */
		JE_createNewEventEnemy(0, 25, 0);
		if (b > 0)
			enemy[b-1].ey = 190 + eventRec[eventLoc-1].eventdat5;
		break;

	case 18: /* Sky Enemy on Bottom */
		JE_createNewEventEnemy(0, 0, 0);
		if (b > 0)
			enemy[b-1].ey = 190 + eventRec[eventLoc-1].eventdat5;
		break;

	case 19: /* Enemy Global Move */
	{
		int initial_i = 0, max_i = 0;
		bool all_enemies = false;

		if (eventRec[eventLoc-1].eventdat3 > 79 && eventRec[eventLoc-1].eventdat3 < 90)
		{
			initial_i = 0;
			max_i = 100;
			all_enemies = false;
			eventRec[eventLoc-1].eventdat4 = newPL[eventRec[eventLoc-1].eventdat3 - 80];
		}
		else
		{
			switch (eventRec[eventLoc-1].eventdat3)
			{
			case 0:
				initial_i = 0;
				max_i = 100;
				all_enemies = false;
				break;
			case 2:
				initial_i = 0;
				max_i = 25;
				all_enemies = true;
				break;
			case 1:
				initial_i = 25;
				max_i = 50;
				all_enemies = true;
				break;
			case 3:
				initial_i = 50;
				max_i = 75;
				all_enemies = true;
				break;
			case 99:
				initial_i = 0;
				max_i = 100;
				all_enemies = true;
				break;
			}
		}

		for (int i = initial_i; i < max_i; i++)
		{
			if (all_enemies || enemy[i].linknum == eventRec[eventLoc-1].eventdat4)
			{
				if (eventRec[eventLoc-1].eventdat != -99)
					enemy[i].exc = eventRec[eventLoc-1].eventdat;

				if (eventRec[eventLoc-1].eventdat2 != -99)
					enemy[i].eyc = eventRec[eventLoc-1].eventdat2;

				if (eventRec[eventLoc-1].eventdat6 != 0)
					enemy[i].fixedmovey = eventRec[eventLoc-1].eventdat6;

				if (eventRec[eventLoc-1].eventdat6 == -99)
					enemy[i].fixedmovey = 0;

				if (eventRec[eventLoc-1].eventdat5 > 0)
					enemy[i].enemycycle = eventRec[eventLoc-1].eventdat5;
			}
		}
		break;
	}

	case 20: /* Enemy Global Accel */
		if (eventRec[eventLoc-1].eventdat3 > 79 && eventRec[eventLoc-1].eventdat3 < 90)
			eventRec[eventLoc-1].eventdat4 = newPL[eventRec[eventLoc-1].eventdat3 - 80];

		for (temp = 0; temp < 100; temp++)
		{
			if (enemyAvail[temp] != 1 &&
			    (enemy[temp].linknum == eventRec[eventLoc-1].eventdat4 || eventRec[eventLoc-1].eventdat4 == 0))
			{
				if (eventRec[eventLoc-1].eventdat != -99)
				{
					enemy[temp].excc = eventRec[eventLoc-1].eventdat;
					enemy[temp].exccw = abs(eventRec[eventLoc-1].eventdat);
					enemy[temp].exccwmax = abs(eventRec[eventLoc-1].eventdat);
					if (eventRec[eventLoc-1].eventdat > 0)
						enemy[temp].exccadd = 1;
					else
						enemy[temp].exccadd = -1;
				}

				if (eventRec[eventLoc-1].eventdat2 != -99)
				{
					enemy[temp].eycc = eventRec[eventLoc-1].eventdat2;
					enemy[temp].eyccw = abs(eventRec[eventLoc-1].eventdat2);
					enemy[temp].eyccwmax = abs(eventRec[eventLoc-1].eventdat2);
					if (eventRec[eventLoc-1].eventdat2 > 0)
						enemy[temp].eyccadd = 1;
					else
						enemy[temp].eyccadd = -1;
				}

				if (eventRec[eventLoc-1].eventdat5 > 0)
				{
					enemy[temp].enemycycle = eventRec[eventLoc-1].eventdat5;
				}
				if (eventRec[eventLoc-1].eventdat6 > 0)
				{
					enemy[temp].ani = eventRec[eventLoc-1].eventdat6;
					enemy[temp].animin = eventRec[eventLoc-1].eventdat5;
					enemy[temp].animax = 0;
					enemy[temp].aniactive = 1;
				}
			}
		}
		break;

	case 21:
		background3over = 1;
		break;

	case 22:
		background3over = 0;
		break;

	case 23: /* Sky Enemy on Bottom */
		JE_createNewEventEnemy(0, 50, 0);
		if (b > 0)
			enemy[b-1].ey = 180 + eventRec[eventLoc-1].eventdat5;
		break;

	case 24: /* Enemy Global Animate */
		for (temp = 0; temp < 100; temp++)
		{
			if (enemy[temp].linknum == eventRec[eventLoc-1].eventdat4)
			{
				enemy[temp].aniactive = 1;
				enemy[temp].aniwhenfire = 0;
				if (eventRec[eventLoc-1].eventdat2 > 0)
				{
					enemy[temp].enemycycle = eventRec[eventLoc-1].eventdat2;
					enemy[temp].animin = enemy[temp].enemycycle;
				}
				else
				{
					enemy[temp].enemycycle = 0;
				}

				if (eventRec[eventLoc-1].eventdat > 0)
					enemy[temp].ani = eventRec[eventLoc-1].eventdat;

				if (eventRec[eventLoc-1].eventdat3 == 1)
				{
					enemy[temp].animax = enemy[temp].ani;
				}
				else if (eventRec[eventLoc-1].eventdat3 == 2)
				{
					enemy[temp].aniactive = 2;
					enemy[temp].animax = enemy[temp].ani;
					enemy[temp].aniwhenfire = 2;
				}
			}
		}
		break;

	case 25: /* Enemy Global Damage change */
		for (temp = 0; temp < 100; temp++)
		{
			if (eventRec[eventLoc-1].eventdat4 == 0 || enemy[temp].linknum == eventRec[eventLoc-1].eventdat4)
			{
				if (galagaMode)
					enemy[temp].armorleft = roundf(eventRec[eventLoc-1].eventdat * (difficultyLevel / 2));
				else
					enemy[temp].armorleft = eventRec[eventLoc-1].eventdat;
			}
		}
		break;

	case 26:
		smallEnemyAdjust = eventRec[eventLoc-1].eventdat;
		break;

	case 27: /* Enemy Global AccelRev */
		if (eventRec[eventLoc-1].eventdat3 > 79 && eventRec[eventLoc-1].eventdat3 < 90)
			eventRec[eventLoc-1].eventdat4 = newPL[eventRec[eventLoc-1].eventdat3 - 80];

		for (temp = 0; temp < 100; temp++)
		{
			if (eventRec[eventLoc-1].eventdat4 == 0 || enemy[temp].linknum == eventRec[eventLoc-1].eventdat4)
			{
				if (eventRec[eventLoc-1].eventdat != -99)
					enemy[temp].exrev = eventRec[eventLoc-1].eventdat;
				if (eventRec[eventLoc-1].eventdat2 != -99)
					enemy[temp].eyrev = eventRec[eventLoc-1].eventdat2;
				if (eventRec[eventLoc-1].eventdat3 != 0 && eventRec[eventLoc-1].eventdat3 < 17)
					enemy[temp].filter = eventRec[eventLoc-1].eventdat3;
			}
		}
		break;

	case 28:
		topEnemyOver = false;
		break;

	case 29:
		topEnemyOver = true;
		break;

	case 30:
		map1YDelay = 1;
		map1YDelayMax = 1;
		map2YDelay = 1;
		map2YDelayMax = 1;

		backMove = eventRec[eventLoc-1].eventdat;
		backMove2 = eventRec[eventLoc-1].eventdat2;
		explodeMove = episodeNum == EPISODE_GBC ? backMove : backMove2;  // (Tyrian3D: as event 2)
		backMove3 = eventRec[eventLoc-1].eventdat3;
		break;

	case 31: /* Enemy Fire Override */
		for (temp = 0; temp < 100; temp++)
		{
			if (eventRec[eventLoc-1].eventdat4 == 99 || enemy[temp].linknum == eventRec[eventLoc-1].eventdat4)
			{
				// (Tyrian3D: in episode 7 with d6 1 a GBC group's gun: one of its PC guns, at d1's pace, gbc_fire)
				if (episodeNum == EPISODE_GBC && eventRec[eventLoc-1].eventdat6 == 1)
				{
					gbc_fire(&enemy[temp], eventRec[eventLoc-1].eventdat);
					for (temp2 = 0; temp2 < 3; temp2++)
						enemy[temp].eshotwait[temp2] = 1;
					continue;
				}
				enemy[temp].freq[1-1] = eventRec[eventLoc-1].eventdat ;
				enemy[temp].freq[2-1] = eventRec[eventLoc-1].eventdat2;
				enemy[temp].freq[3-1] = eventRec[eventLoc-1].eventdat3;
				for (temp2 = 0; temp2 < 3; temp2++)
				{
					enemy[temp].eshotwait[temp2] = 1;
				}
				if (enemy[temp].launchtype > 0)
				{
					enemy[temp].launchfreq = eventRec[eventLoc-1].eventdat5;
					enemy[temp].launchwait = 1;
				}
			}
		}
		break;

	case 32:  // create enemy
		JE_createNewEventEnemy(0, 50, 0);
		if (b > 0)
			enemy[b-1].ey = 190;
		break;

	case 33: /* Enemy From other Enemies */
		if (!((eventRec[eventLoc-1].eventdat == 512 || eventRec[eventLoc-1].eventdat == 513) && (twoPlayerMode || onePlayerAction || superTyrian)))
		{
			if (superArcadeMode != SA_NONE)
			{
				if (eventRec[eventLoc-1].eventdat == 534)
					eventRec[eventLoc-1].eventdat = 827;
			}
			else if (!superTyrian)
			{
				const Uint8 lives = *player[0].lives;

				if (eventRec[eventLoc-1].eventdat == 533 && (lives == 11 || (mt_rand() % 15) < lives))
				{
					// enemy will drop random special weapon
					eventRec[eventLoc-1].eventdat = 829 + (mt_rand() % 6);
				}
			}
			if (eventRec[eventLoc-1].eventdat == 534 && superTyrian)
				eventRec[eventLoc-1].eventdat = 828 + superTyrianSpecials[mt_rand() % 4];

			for (temp = 0; temp < 100; temp++)
			{
				if (enemy[temp].linknum == eventRec[eventLoc-1].eventdat4)
					enemy[temp].enemydie = eventRec[eventLoc-1].eventdat;
			}
		}
		break;

	case 34: /* Start Music Fade */
		if (firstGameOver)
		{
			musicFade = true;
			tempVolume = tyrMusicVolume;
		}
		break;

	case 35: /* Play new song */
		if (firstGameOver)
		{
			play_song(eventRec[eventLoc-1].eventdat - 1);
			set_volume(tyrMusicVolume, fxVolume);
		}
		musicFade = false;
		break;

	case 36:
		readyToEndLevel = true;
		break;

	case 37:
		levelEnemyFrequency = eventRec[eventLoc-1].eventdat;
		break;

	case 38:
		curLoc = eventRec[eventLoc-1].eventdat;
		int new_event_loc = 1;
		for (tempW = 0; tempW < maxEvent; tempW++)
		{
			if (eventRec[tempW].eventtime <= curLoc)
				new_event_loc = tempW+1 - 1;
		}
		eventLoc = new_event_loc;
		break;

	case 39: /* Enemy Global Linknum Change */
		for (temp = 0; temp < 100; temp++)
		{
			if (enemy[temp].linknum == eventRec[eventLoc-1].eventdat)
				enemy[temp].linknum = eventRec[eventLoc-1].eventdat2;
		}
		break;

	case 40: /* Enemy Continual Damage */
		enemyContinualDamage = true;
		break;

	case 41:
		if (eventRec[eventLoc-1].eventdat == 0)
		{
			memset(enemyAvail, 1, sizeof(enemyAvail));
		}
		else
		{
			for (x = 0; x <= 24; x++)
				enemyAvail[x] = 1;
		}
		break;

	case 42:
		background3over = 2;
		break;

	case 43:
		background2over = eventRec[eventLoc-1].eventdat;
		break;

	case 44:
		filterActive       = (eventRec[eventLoc-1].eventdat > 0);
		filterFade         = (eventRec[eventLoc-1].eventdat == 2);
		levelFilter        = eventRec[eventLoc-1].eventdat2;
		levelBrightness    = eventRec[eventLoc-1].eventdat3;
		levelFilterNew     = eventRec[eventLoc-1].eventdat4;
		levelBrightnessChg = eventRec[eventLoc-1].eventdat5;
		filterFadeStart    = (eventRec[eventLoc-1].eventdat6 == 0);
		break;

	case 45: /* arcade-only enemy from other enemies */
		if (rogue_run)
		{
			// Tyrian3D: a rogue run gets the arcade's drops as purple orbs (its experience, rogue.h);
			// the arcade's weapons and items are the run's cards.
			for (temp = 0; temp < 100; temp++)
			{
				if (enemy[temp].linknum == eventRec[eventLoc-1].eventdat4)
					enemy[temp].enemydie = ROGUE_ORB_ENEMY;
			}
		}
		else if (!superTyrian)
		{
			const Uint8 lives = *player[0].lives;

			if (eventRec[eventLoc-1].eventdat == 533 && (lives == 11 || (mt_rand() % 15) < lives))
			{
				eventRec[eventLoc-1].eventdat = 829 + (mt_rand() % 6);
			}
			if (twoPlayerMode || onePlayerAction)
			{
				for (temp = 0; temp < 100; temp++)
				{
					if (enemy[temp].linknum == eventRec[eventLoc-1].eventdat4)
						enemy[temp].enemydie = eventRec[eventLoc-1].eventdat;
				}
			}
		}
		break;

	case 46:  // change difficulty
		if (eventRec[eventLoc-1].eventdat3 != 0)
			damageRate = eventRec[eventLoc-1].eventdat3;

		if (eventRec[eventLoc-1].eventdat2 == 0 || twoPlayerMode || onePlayerAction)
		{
			difficultyLevel += eventRec[eventLoc-1].eventdat;
			if (difficultyLevel < DIFFICULTY_EASY)
				difficultyLevel = DIFFICULTY_EASY;
			if (difficultyLevel > DIFFICULTY_10)
				difficultyLevel = DIFFICULTY_10;
		}
		break;

	case 47: /* Enemy Global AccelRev */
		for (temp = 0; temp < 100; temp++)
		{
			if (eventRec[eventLoc-1].eventdat4 == 0 || enemy[temp].linknum == eventRec[eventLoc-1].eventdat4)
				enemy[temp].armorleft = eventRec[eventLoc-1].eventdat;
		}
		break;

	case 48: /* Background 2 Cannot be Transparent */
		background2notTransparent = true;
		break;

	case 49:
	case 50:
	case 51:
	case 52:
		tempDat2 = eventRec[eventLoc-1].eventdat;
		eventRec[eventLoc-1].eventdat = 0;
		tempDat = eventRec[eventLoc-1].eventdat3;
		eventRec[eventLoc-1].eventdat3 = 0;
		tempDat3 = eventRec[eventLoc-1].eventdat6;
		eventRec[eventLoc-1].eventdat6 = 0;
		enemyDat[0].armor = tempDat3;
		enemyDat[0].egraphic[1-1] = tempDat2;
		switch (eventRec[eventLoc-1].eventtype - 48)
		{
		case 1:
			temp = 25;
			break;
		case 2:
			temp = 0;
			break;
		case 3:
			temp = 50;
			break;
		case 4:
			temp = 75;
			break;
		}
		JE_createNewEventEnemy(0, temp, tempDat);
		eventRec[eventLoc-1].eventdat = tempDat2;
		eventRec[eventLoc-1].eventdat3 = tempDat;
		eventRec[eventLoc-1].eventdat6 = tempDat3;
		break;

	case 53:
		forceEvents = (eventRec[eventLoc-1].eventdat != 99);
		break;

	case 54:
		JE_eventJump(eventRec[eventLoc-1].eventdat);
		break;

	case 55: /* Enemy Global AccelRev */
		if (eventRec[eventLoc-1].eventdat3 > 79 && eventRec[eventLoc-1].eventdat3 < 90)
			eventRec[eventLoc-1].eventdat4 = newPL[eventRec[eventLoc-1].eventdat3 - 80];

		for (temp = 0; temp < 100; temp++)
		{
			if (eventRec[eventLoc-1].eventdat4 == 0 || enemy[temp].linknum == eventRec[eventLoc-1].eventdat4)
			{
				if (eventRec[eventLoc-1].eventdat != -99)
					enemy[temp].xaccel = eventRec[eventLoc-1].eventdat;
				if (eventRec[eventLoc-1].eventdat2 != -99)
					enemy[temp].yaccel = eventRec[eventLoc-1].eventdat2;
			}
		}
		break;

	case 56: /* Ground2 Bottom */
		JE_createNewEventEnemy(0, 75, 0);
		if (b > 0)
			enemy[b-1].ey = 190;
		break;

	case 57:
		superEnemy254Jump = eventRec[eventLoc-1].eventdat;
		break;

	case 58: // Set enemy launch
		// This implementation comes from ArcTyr, and may not be 100% accurate to Tyrian 2000
		for (temp = 0; temp < 100; temp++)
		{
			if (eventRec[eventLoc-1].eventdat4 == 99 || enemy[temp].linknum == eventRec[eventLoc-1].eventdat4)
				enemy[temp].launchtype = eventRec[eventLoc-1].eventdat;
		}
		break;

	case 59: // Replace enemy
	case 68: // Note: random explosions got moved to event 99 in T2000
		// This implementation comes from ArcTyr, and may not be 100% accurate to Tyrian 2000
		{
			Uint16 eDatI = eventRec[eventLoc-1].eventdat;

			for (temp = 0; temp < 100; temp++)
			{
				if (!(eventRec[eventLoc-1].eventdat4 == 0 || enemy[temp].linknum == eventRec[eventLoc-1].eventdat4))
					continue;

				const int enemy_offset = temp - (temp % 25);
				b = JE_newEnemy(enemy_offset, eDatI, 0);
				if (b != 0)
				{
					enemy[b-1].ex = enemy[temp].ex;
					enemy[b-1].ey = enemy[temp].ey;
					enemy_group[b-1] = enemy_group[temp];  // (Tyrian3D: in its place)
					enemy_group_link[b-1] = enemy_group_link[temp];
					gbc_object[b-1] = gbc_object[temp];
					gbc_look_id[b-1] = gbc_look_id[temp];
					gbc_look_parts[b-1] = gbc_look_parts[temp];
					memcpy(gbc_look[b-1], gbc_look[temp], sizeof(gbc_look[temp]));
				}

				enemyAvail[temp] = 1;
			}			
		}
		break;
		break;

	case 60: /*Assign Special Enemy*/
		for (temp = 0; temp < 100; temp++)
		{
			if (enemy[temp].linknum == eventRec[eventLoc-1].eventdat4)
			{
				enemy[temp].special = true;
				enemy[temp].flagnum = eventRec[eventLoc-1].eventdat;
				enemy[temp].setto  = (eventRec[eventLoc-1].eventdat2 == 1);
			}
		}
		break;

	case 61:  // if specific flag set to specific value, skip events
		if (globalFlags[eventRec[eventLoc-1].eventdat-1] == eventRec[eventLoc-1].eventdat2)
			eventLoc += eventRec[eventLoc-1].eventdat3;
		break;

	case 62: /*Play sound effect*/
		soundQueue[3] = eventRec[eventLoc-1].eventdat;
		break;

	case 63:  // skip events if not in 2-player mode
		if (!twoPlayerMode && !onePlayerAction)
			eventLoc += eventRec[eventLoc-1].eventdat;
		break;

	case 64:
		if (!(eventRec[eventLoc-1].eventdat == 6 && twoPlayerMode && difficultyLevel > DIFFICULTY_NORMAL))
		{
			smoothies[eventRec[eventLoc-1].eventdat-1] = eventRec[eventLoc-1].eventdat2;
			temp = eventRec[eventLoc-1].eventdat;
			if (temp == 5)
				temp = 3;
			smoothie_data[temp-1] = eventRec[eventLoc-1].eventdat3;
		}
		break;

	case 65:
		background3x1 = (eventRec[eventLoc-1].eventdat == 0);
		break;

	case 66: /*If not on this difficulty level or higher then...*/
		if (initialDifficulty <= eventRec[eventLoc-1].eventdat)
			eventLoc += eventRec[eventLoc-1].eventdat2;
		break;

	case 67:
		levelTimer = (eventRec[eventLoc-1].eventdat == 1);
		levelTimerCountdown = eventRec[eventLoc-1].eventdat3 * 100;
		levelTimerJumpTo   = eventRec[eventLoc-1].eventdat2;
		break;

	case 69:
		for (uint i = 0; i < COUNTOF(player); ++i)
			player[i].invulnerable_ticks = eventRec[eventLoc-1].eventdat;
		break;

	case 70:
		if (eventRec[eventLoc-1].eventdat2 == 0)
		{  /*1-10*/
			bool found = false;

			for (temp = 1; temp <= 19; temp++)
				found = found || JE_searchFor(temp, NULL);

			if (!found)
				JE_eventJump(eventRec[eventLoc-1].eventdat);
		}
		else if (!JE_searchFor(eventRec[eventLoc-1].eventdat2, NULL) &&
		         (eventRec[eventLoc-1].eventdat3 == 0 || !JE_searchFor(eventRec[eventLoc-1].eventdat3, NULL)) &&
		         (eventRec[eventLoc-1].eventdat4 == 0 || !JE_searchFor(eventRec[eventLoc-1].eventdat4, NULL)))
		{
			JE_eventJump(eventRec[eventLoc-1].eventdat);
		}
		break;

	case 71:
		if (((((intptr_t)mapYPos - (intptr_t)&megaData1.mainmap) / sizeof(JE_byte *)) * 2) <= (unsigned)eventRec[eventLoc-1].eventdat2)
			JE_eventJump(eventRec[eventLoc-1].eventdat);
		break;

	case 72:
		background3x1b = (eventRec[eventLoc-1].eventdat == 1);
		break;

	case 73:
		skyEnemyOverAll = (eventRec[eventLoc-1].eventdat == 1);
		break;

	case 74: /* Enemy Global BounceParams */
		for (temp = 0; temp < 100; temp++)
		{
			if (eventRec[eventLoc-1].eventdat4 == 0 || enemy[temp].linknum == eventRec[eventLoc-1].eventdat4)
			{
				if (eventRec[eventLoc-1].eventdat5 != -99)
					enemy[temp].xminbounce = eventRec[eventLoc-1].eventdat5;

				if (eventRec[eventLoc-1].eventdat6 != -99)
					enemy[temp].yminbounce = eventRec[eventLoc-1].eventdat6;

				if (eventRec[eventLoc-1].eventdat != -99)
					enemy[temp].xmaxbounce = eventRec[eventLoc-1].eventdat;

				if (eventRec[eventLoc-1].eventdat2 != -99)
					enemy[temp].ymaxbounce = eventRec[eventLoc-1].eventdat2;
			}
		}
		break;

	case 75:;
		bool temp_no_clue = false; // TODO: figure out what this is doing

		for (temp = 0; temp < 100; temp++)
		{
			if (enemyAvail[temp] == 0 &&
			    enemy[temp].eyc == 0 &&
			    enemy[temp].linknum >= eventRec[eventLoc-1].eventdat &&
			    enemy[temp].linknum <= eventRec[eventLoc-1].eventdat2)
			{
				temp_no_clue = true;
			}
		}

		if (temp_no_clue)
		{
			JE_byte enemy_i;
			do
			{
				temp = (mt_rand() % (eventRec[eventLoc-1].eventdat2 + 1 - eventRec[eventLoc-1].eventdat)) + eventRec[eventLoc-1].eventdat;
			} while (!(JE_searchFor(temp, &enemy_i) && enemy[enemy_i].eyc == 0));

			newPL[eventRec[eventLoc-1].eventdat3 - 80] = temp;
		}
		else
		{
			newPL[eventRec[eventLoc-1].eventdat3 - 80] = 255;
			if (eventRec[eventLoc-1].eventdat4 > 0)
			{ /*Skip*/
				curLoc = eventRec[eventLoc-1 + eventRec[eventLoc-1].eventdat4].eventtime - 1;
				eventLoc += eventRec[eventLoc-1].eventdat4 - 1;
			}
		}

		break;

	case 76:
		returnActive = true;
		break;

	case 77:
		mapYPos = &megaData1.mainmap[0][0];
		mapYPos += eventRec[eventLoc-1].eventdat / 2;
		if (eventRec[eventLoc-1].eventdat2 > 0)
		{
			mapY2Pos = &megaData2.mainmap[0][0];
			mapY2Pos += eventRec[eventLoc-1].eventdat2 / 2;
		}
		else
		{
			mapY2Pos = &megaData2.mainmap[0][0];
			mapY2Pos += eventRec[eventLoc-1].eventdat / 2;
		}
		break;

	case 78:
		if (galagaShotFreq < 10)
			galagaShotFreq++;
		break;

	case 79:
		boss_bar[0].link_num = eventRec[eventLoc-1].eventdat;
		boss_bar[1].link_num = eventRec[eventLoc-1].eventdat2;
		break;

	case 80:  // skip events if in 2-player mode
		if (twoPlayerMode)
			eventLoc += eventRec[eventLoc-1].eventdat;
		break;

	case 81: /*WRAP2*/
		BKwrap2   = &megaData2.mainmap[0][0];
		BKwrap2   += eventRec[eventLoc-1].eventdat / 2;
		BKwrap2to = &megaData2.mainmap[0][0];
		BKwrap2to += eventRec[eventLoc-1].eventdat2 / 2;
		break;

	case 82: /*Give SPECIAL WEAPON*/
		player[0].items.special = eventRec[eventLoc-1].eventdat;
		shotMultiPos[SHOT_SPECIAL] = 0;
		shotRepeat[SHOT_SPECIAL] = 0;
		shotMultiPos[SHOT_SPECIAL2] = 0;
		shotRepeat[SHOT_SPECIAL2] = 0;
		break;

	case 84: // timed battle level timer
		if (!timedBattleMode)
			break;

		// note: a copy of event 67
		levelTimer = (eventRec[eventLoc-1].eventdat == 1);
		levelTimerCountdown = eventRec[eventLoc-1].eventdat3 * 100;
		levelTimerJumpTo   = eventRec[eventLoc-1].eventdat2;
		break;

	case 85: // timed battle enemy from other enemies
		if (timedBattleMode)
		{
			for (temp = 0; temp < 100; temp++)
			{
				if (enemy[temp].linknum == eventRec[eventLoc-1].eventdat4)
					enemy[temp].enemydie = eventRec[eventLoc-1].eventdat;
			}
		}
		break;


	case 99:
		randomExplosions = (eventRec[eventLoc-1].eventdat == 1);
		break;

	case 201:  // Tyrian3D: the next d1 events make one enemy (episode 7: its pieces; JE_createNewEventEnemy)
		break;

	case 202:  // Tyrian3D: a part of the next enemy's look (episode 7's bosses: gbc_look; JE_createNewEventEnemy)
		break;

	case GBC_SONG:  // Tyrian3D: episode 7's boss song (gbc_music)
		gbc_music(eventRec[eventLoc-1].eventdat == 1);
		break;

	case GBC_FIGHT:  // Tyrian3D: the next enemy's toughness and fire as the GBC's (episode 7: gbc_fight)
		break;

	case 200:  // Tyrian3D: the level seen from the side (d1 1) or from above again (0)
		l3d_sideways = eventRec[eventLoc-1].eventdat != 0;
		l3d_side_decor = eventRec[eventLoc-1].eventdat2;
		// (At least SIDE_AHEAD: enemies are made past the window's right edge rather than in the middle of it.)
		l3d_field_ahead = eventRec[eventLoc-1].eventdat != 0 && eventRec[eventLoc-1].eventdat3 > 0
		                  ? SDL_max(eventRec[eventLoc-1].eventdat3 * 10, SIDE_AHEAD) : l3d_field_wide ? WIDE_AHEAD : 0;
		break;

	case 205:  // Tyrian3D: the level seen from behind the ship (d1 1) or from above again (0)
		l3d_chase = eventRec[eventLoc-1].eventdat != 0;
		break;

	default:
		fprintf(stderr, "warning: ignoring unknown event %d\n", eventRec[eventLoc-1].eventtype);
		break;
	}

	eventLoc++;
}

void JE_whoa(void)
{
	unsigned int i, j, color, offset, timer;
	unsigned int screenSize, topBorder, bottomBorder;
	Uint8 * TempScreen1, * TempScreen2, * TempScreenSwap;

	/* 'whoa' gets us that nifty screen fade used when you type in
	 * 'engage'.  We need two temporary screen buffers (char arrays can
	 * work too, but these screens already exist) for our effect.
	 * This could probably be a lot more efficient (there's probably a
	 * way to get vgascreen as one of the temp buffers), but it's only called
	 * once so don't worry about it. */

	TempScreen1  = game_screen->pixels;
	TempScreen2  = VGAScreen2->pixels;

	screenSize   = VGAScreenSeg->h * VGAScreenSeg->pitch;
	topBorder    = VGAScreenSeg->pitch * 4; /* Seems an arbitrary number of lines */
	bottomBorder = VGAScreenSeg->pitch * 7;

	/* Okay, one disadvantage to using other screens as temp buffers: they
	 * need to be the right size.  I doubt they'll ever be anything but 320x200,
	 * but just in case, these asserts will clue in whoever stumbles across
	 * the problem.  You can fix it with the stack or malloc. */
	assert((unsigned)VGAScreen2->h  * VGAScreen2->pitch >= screenSize &&
	       (unsigned)game_screen->h * game_screen->pitch >= screenSize);

	/* Clear the top and bottom borders.  We don't want to process
	 * them and we don't want to draw them. */
	memset((Uint8 *)VGAScreenSeg->pixels, 0, topBorder);
	memset((Uint8 *)VGAScreenSeg->pixels + screenSize - bottomBorder, 0, bottomBorder);

	/* Copy our test subject to one of the temporary buffers.  Blank the other */
	memset(TempScreen1, 0, screenSize);
	memcpy(TempScreen2, VGAScreenSeg->pixels, VGAScreenSeg->h * VGAScreenSeg->pitch);

	service_SDL_events(true);
	timer = 300; /* About 300 rounds is enough to make the screen mostly black */

	do
	{
		setDelay(1);

		/* This gets us our 'whoa' effect with pixel bleeding magic.
		 * I'm willing to bet the guy who originally wrote the asm was goofing
		 * around on acid and thought this looked good enough to use. */
		for (i = screenSize - bottomBorder, j = topBorder / 2; i > 0; i--, j++)
		{
			offset = j + i/8192 - 4;
			color = (TempScreen2[offset                    ] * 12 +
			         TempScreen1[offset-VGAScreenSeg->pitch]      +
			         TempScreen1[offset-1                  ]      +
			         TempScreen1[offset+1                  ]      +
			         TempScreen1[offset+VGAScreenSeg->pitch]) / 16;

			TempScreen1[j] = color;
		}

		/* Now copy that mess to the buffer. */
		memcpy((Uint8 *)VGAScreenSeg->pixels + topBorder, TempScreen1 + topBorder, screenSize - bottomBorder);

		JE_showVGA();

		timer--;
		wait_delay();

		/* Flip the buffer. */
		TempScreenSwap = TempScreen1;
		TempScreen1    = TempScreen2;
		TempScreen2    = TempScreenSwap;

	} while (!(timer == 0 || JE_anyButton()));

	levelWarningLines = 4;
}

static void JE_barX(JE_word x1, JE_word y1, JE_word x2, JE_word y2, JE_byte col)
{
	fill_rectangle_xy(VGAScreen, x1, y1,     x2, y1,     col + 1);
	fill_rectangle_xy(VGAScreen, x1, y1 + 1, x2, y2 - 1, col    );
	fill_rectangle_xy(VGAScreen, x1, y2,     x2, y2,     col - 1);
}

void draw_boss_bar(void)
{
	for (unsigned int b = 0; b < COUNTOF(boss_bar); b++)
	{
		if (boss_bar[b].link_num == 0)
			continue;

		unsigned int armor = 256;  // higher than armor max

		for (unsigned int e = 0; e < COUNTOF(enemy); e++)  // find most damaged
		{
			// (Tyrian3D: not its wrecks, enemyAvail 2: a boss gone to wrecks kept its bar up at its last hit's armour,
			// REEF's GYGES in the middle of the level until the next boss's bar)
			if (enemyAvail[e] == 0 && enemy[e].linknum == boss_bar[b].link_num)
				if (enemy[e].armorleft < armor)
					armor = enemy[e].armorleft;
		}
		// (Tyrian3D: a GBC boss's body, gbc_pool_hit: what it has left of its full pool, while any piece of it lives)
		if (gbc_piece_link(boss_bar[b].link_num))
		{
			bool live = false;
			for (unsigned int e = 0; e < COUNTOF(enemy); e++)
				live = live || gbc_in_pool(e);
			const int full = gbc_pool_full();
			armor = live && full > 0 && gbc_pool_left() > 0 ? (unsigned int)SDL_max(1, gbc_pool_left() * 254 / full) : 0;
		}

		if (armor > 255 || armor == 0)  // boss dead?
			boss_bar[b].link_num = 0;
		else
			boss_bar[b].armor = (armor == 255) ? 254 : armor;  // 255 would make the bar too long

		// Tyrian3D dev: TYR3D_LOG_BOSS prints the boss's armour as it changes.
		static unsigned int logged[2] = { 999, 999 };
		if (SDL_getenv("TYR3D_LOG_BOSS") != NULL && armor != logged[b])
		{
			logged[b] = armor;
			printf("boss: bar %u link %d armor %u\n", b, boss_bar[b].link_num, armor);		}
	}

	unsigned int bars = (boss_bar[0].link_num != 0 ? 1 : 0)
	                  + (boss_bar[1].link_num != 0 ? 1 : 0);

	// if only one bar left, make it the first one
	if (bars == 1 && boss_bar[0].link_num == 0)
	{
		memcpy(&boss_bar[0], &boss_bar[1], sizeof(boss_bar_t));
		boss_bar[1].link_num = 0;
	}

	for (unsigned int b = 0; b < bars; b++)
	{
		unsigned int x = (bars == 2)
		               ? ((b == 0) ? 125 : 185)
		               : ((levelTimer) ? 250 : 155);  // level timer and boss bar would overlap
		unsigned int y = (levelTimer) ? 15 : 7;

		JE_barX(x - 25, y, x + 25, y + 5, 115);
		JE_barX(x - (boss_bar[b].armor / 10), y, x + (boss_bar[b].armor + 5) / 10, y + 5, 118 + boss_bar[b].color);

		if (boss_bar[b].color > 0)
			boss_bar[b].color--;
	}
}
