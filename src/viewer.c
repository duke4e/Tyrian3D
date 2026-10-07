/*
 * Tyrian3D dev tool: a model viewer (see viewer.h).
 */
#include "viewer.h"

#include "episodes.h"
#include "keyboard.h"
#include "layer3d.h"
#include "lvllib.h"
#include "lvlmast.h"
#include "models3d.h"
#include "opentyr.h"
#include "palette.h"
#include "pcxmast.h"
#include "sprite.h"
#include "video.h"
#include "volume3d.h"

#include <SDL3/SDL.h>

#include <stdio.h>
#include <string.h>

#define MAX_ENTRIES 48

typedef struct
{
	Sprite2_array *sheet;
	unsigned int sprite;  // as blit_sprite2x2 (large) or blit_sprite2 takes it
	bool large;
	M3DAppearance look;
	int frame_count;      // enemies: their animation (frames[0] is sprite)
	unsigned int frames[20];
} Entry;

static bool seen_before(const Entry *entries, int count, const Sprite2_array *sheet, unsigned int sprite)
{
	for (int i = 0; i < count; ++i)
		if (entries[i].sheet == sheet && entries[i].sprite == sprite)
			return true;
	return false;
}

// Each player ship sprite once, with the appearance of the first ship using it.
static int ship_entries(Entry *entries)
{
	JE_initEpisode(1);  // loads the ships

	int count = 0;
	for (unsigned int id = 1; id <= SHIP_NUM && count < MAX_ENTRIES; ++id)
	{
		const unsigned int graphic = ships[id].shipgraphic;
		if (graphic <= 1)  // the Nort Ship and the Dragonwing are drawn in parts
			continue;
		Sprite2_array *sheet = graphic > 500 ? &spriteSheetT2000 : &spriteSheet9;
		const unsigned int sprite = graphic > 500 ? graphic - 500 : graphic;
		if (!seen_before(entries, count, sheet, sprite))
			entries[count++] = (Entry){ sheet, sprite, true, m3d_ship_appearance(id) };
	}
	return count;
}

// The enemy types models.cfg gives a model of their own ("sprite" lines), each with its
// animation as the first episode using it defines it.
static int enemy_entries(Entry *entries)
{
	static Sprite2_array sheets[8];
	static char sheet_letters[8];
	int sheet_count = 0;

	int count = 0;
	for (int r = 0; r < m3d_sprite_rule_count() && count < MAX_ENTRIES; ++r)
	{
		char letter;
		unsigned int first;
		M3DAppearance look;
		m3d_sprite_rule(r, &letter, &first, &look);
		if (look.model < 0)
			continue;

		// The enemy type: its size and frames.
		bool found = false;
		Entry e = { .sprite = first, .look = look };
		for (int episode = 1; episode <= EPISODE_MAX && !found; ++episode)
		{
			if (!episodeAvail[episode - 1])
				continue;
			JE_initEpisode((JE_byte)episode);
			for (int id = 1; id <= ENEMY_NUM && !found; ++id)
			{
				const int bank = enemyDat[id].shapebank;
				const char bank_letter = bank == 21 ? M3D_SHEET_COINS : bank == 26 ? M3D_SHEET_POWERUPS :
				                         bank >= 1 && bank <= (int)COUNTOF(shapeFile) ? (char)SDL_tolower((unsigned char)shapeFile[bank - 1]) : 0;
				if (bank_letter != letter || enemyDat[id].egraphic[0] != first)
					continue;
				found = true;
				e.large = enemyDat[id].esize == 1;
				e.frame_count = SDL_max(1, SDL_min(enemyDat[id].ani, 20));
				for (int k = 0; k < e.frame_count; ++k)
					e.frames[k] = enemyDat[id].egraphic[k] != 0 ? enemyDat[id].egraphic[k] : first;
			}
		}
		if (!found)
			continue;

		// Its shape file, loaded once (the coins and power-ups sheets are always loaded).
		if (letter == M3D_SHEET_COINS || letter == M3D_SHEET_POWERUPS)
		{
			e.sheet = letter == M3D_SHEET_COINS ? &spriteSheet11 : &spriteSheet10;
			entries[count++] = e;
			continue;
		}
		int s = 0;
		while (s < sheet_count && sheet_letters[s] != letter)
			++s;
		if (s == sheet_count)
		{
			if (sheet_count == (int)COUNTOF(sheets))
				continue;
			JE_loadCompShapes(&sheets[s], letter);
			sheet_letters[s] = letter;
			++sheet_count;
		}
		e.sheet = &sheets[s];
		entries[count++] = e;
	}
	return count;
}

// Each sidekick's first frame once (sidekicks of styles 1 and 2 are drawn 2x2 from the power-ups
// sheet, the others 1x1 from the ships sheet, as player_drawSidekicks does).
static int sidekick_entries(Entry *entries)
{
	JE_initEpisode(1);  // loads the sidekicks

	int count = 0;
	for (unsigned int id = 1; id <= OPTION_NUM && count < MAX_ENTRIES; ++id)
	{
		const JE_OptionType *option = &options[id];
		if (option->option == 0 || option->gr[0] == 0)
			continue;
		const bool large = option->tr == 1 || option->tr == 2;
		Sprite2_array *sheet = large ? &spriteSheet10 : &spriteSheet9;
		if (!seen_before(entries, count, sheet, option->gr[0]))
			entries[count++] = (Entry){ sheet, option->gr[0], large, m3d_sidekick_appearance(id) };
	}
	return count;
}

static float env_float(const char *name, float fallback)
{
	const char *value = SDL_getenv(name);
	return value != NULL ? (float)SDL_atof(value) : fallback;
}

// Fills a screen surface including its overscan rows, which the 3D view shows too.
static void fill_with_overscan(SDL_Surface *surface, Uint8 color)
{
	Uint8 *first = (Uint8 *)surface->pixels - SCREEN_OVERSCAN_MAX * surface->pitch;
	memset(first, color, (size_t)surface->pitch * (surface->h + SCREEN_OVERSCAN_MAX));
}

void dev_model_viewer(const char *what)
{
	Entry entries[MAX_ENTRIES];
	int count = 0;
	if (strcmp(what, "ships") == 0)
		count = ship_entries(entries);
	else if (strcmp(what, "sidekicks") == 0)
		count = sidekick_entries(entries);
	else if (strcmp(what, "enemies") == 0)
		count = enemy_entries(entries);
	if (count == 0)
	{
		fprintf(stderr, "warning: TYR3D_VIEWER: nothing to show for '%s' (try 'ships', 'sidekicks' or 'enemies')\n", what);
		return;
	}

	// The palette levels are played in (that of the in-game panel picture).
	memcpy(colors, palettes[pcxpal[3 - 1]], sizeof(colors));
	set_palette(colors, 0, 255);

	const float yaw = env_float("TYR3D_VIEWER_YAW", 0);
	const float roll = env_float("TYR3D_VIEWER_ROLL", 0);
	const float spin = env_float("TYR3D_VIEWER_SPIN", 0);
	const Uint8 ground = (Uint8)env_float("TYR3D_VIEWER_GROUND", 0);

	// Pairs of 3D appearance (left) and sprite (right), in rows centred in the playfield.
	bool any_large = false;
	for (int i = 0; i < count; ++i)
		any_large |= entries[i].large;
	const int cell_w = any_large ? 24 : 12, cell_h = any_large ? 28 : 14;
	const int pair_w = 2 * cell_w + 14;
	const int columns = L3D_PLAYFIELD_W / pair_w;
	const int rows = (count + columns - 1) / columns;
	const int row_h = SDL_min(cell_h + 12, (L3D_PLAYFIELD_H + 20) / rows);  // tighter when there are many
	const int left = L3D_PLAYFIELD_X + (L3D_PLAYFIELD_W - columns * pair_w) / 2;
	const int top = (L3D_PLAYFIELD_H - rows * row_h) / 2;

	JE_clr256(VGAScreenSeg);  // no panel around the playfield
	for (unsigned int frame = 0; ; ++frame)
	{
		VGAScreen = game_screen;
		l3d_frame_begin(L3D_GROUND);
		fill_with_overscan(game_screen, ground);
		l3d_phase(L3D_PLAYER);

		for (int i = 0; i < count; ++i)
		{
			const Entry *e = &entries[i];
			// Centre of the left cell; sprites are drawn from their top left corner, half a
			// sprite from their centre.
			const int half_w = e->large ? 12 : 6, half_h = e->large ? 14 : 7;
			const int x = left + (i % columns) * pair_w + cell_w / 2 + 5;
			const int y = top + (i / columns) * row_h + cell_h / 2 + 6;
			// Enemies animate as in the game, a frame every few ticks; models turn or roll with it.
			const int k = e->frame_count > 1 ? (int)(frame / 4) % e->frame_count : 0;
			const unsigned int sprite = e->frame_count > 1 ? e->frames[k] : e->sprite;
			float turn = e->look.yaw + yaw + (spin + e->look.spin) * frame;
			if (e->look.yaw_mode == M3D_YAW_FRAMES)
				turn += k * e->look.yaw_step;
			const float model_roll = roll + k * e->look.roll_step;
			const Uint8 filter = e->look.recolor ? (Uint8)(l3d_sprite_ramp(e->sheet, sprite, e->large) << 4) : 0;
			if (e->look.model >= 0 && e->look.glow_size != 0)
				l3d_add_sprite_glow(e->sheet, sprite, e->large, x, y,
				                    e->look.glow_size < 0 ? -e->look.glow_size * (e->large ? 24 : 12) : e->look.glow_size,
				                    e->look.glow_strength);

			if (e->look.model >= 0)
				l3d_add_object(e->look.model, x, y, e->look.height, turn, model_roll, filter);
			else if (e->look.model != M3D_VOLUME ||
			         !l3d_add_volume(e->sheet, sprite, e->large, V3D_STYLE_RAISED, x, y, e->look.height, turn, roll, 0))
				(e->large ? blit_sprite2x2 : blit_sprite2)(VGAScreen, x - half_w, y - half_h, *e->sheet, sprite);

			(e->large ? blit_sprite2x2 : blit_sprite2)(VGAScreen, x + cell_w + 4 - half_w, y - half_h, *e->sheet, sprite);
		}

		l3d_frame_end();

		// The 2D view (F3) shows the playfield as drawn, on the left of the screen (as
		// JE_starShowVGA copies it).
		for (int row = 0; row < L3D_PLAYFIELD_H; ++row)
			memcpy((Uint8 *)VGAScreenSeg->pixels + row * VGAScreenSeg->pitch,
			       (const Uint8 *)game_screen->pixels + row * game_screen->pitch + L3D_PLAYFIELD_X, L3D_PLAYFIELD_W);
		VGAScreen = VGAScreenSeg;
		if (l3d_take_frame())
			JE_showVGA3D();
		else
			JE_showVGA();

		service_SDL_events(true);
		if (newkey && lastkey_scan == SDL_SCANCODE_ESCAPE)
			break;
		SDL_Delay(16);
	}
}
