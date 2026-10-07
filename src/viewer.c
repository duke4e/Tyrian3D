/*
 * Tyrian3D dev tool: a model viewer (see viewer.h).
 */
#include "viewer.h"

#include "episodes.h"
#include "keyboard.h"
#include "layer3d.h"
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

#define MAX_ENTRIES 16

typedef struct
{
	Sprite2_array *sheet;
	unsigned int sprite;    // 2x2 sprite, as blit_sprite2x2 takes it
	M3DAppearance look;
} Entry;

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

		bool seen = false;
		for (int i = 0; i < count; ++i)
			seen |= entries[i].sheet == sheet && entries[i].sprite == sprite;
		if (seen)
			continue;

		entries[count++] = (Entry){ sheet, sprite, m3d_ship_appearance(id) };
	}
	return count;
}

static float env_float(const char *name, float fallback)
{
	const char *value = SDL_getenv(name);
	return value != NULL ? (float)SDL_atof(value) : fallback;
}

// Clears a screen surface including its overscan rows, which the 3D view shows too.
static void clear_with_overscan(SDL_Surface *surface)
{
	Uint8 *first = (Uint8 *)surface->pixels - SCREEN_OVERSCAN_MAX * surface->pitch;
	memset(first, 0, (size_t)surface->pitch * (surface->h + SCREEN_OVERSCAN_MAX));
}

void dev_model_viewer(const char *what)
{
	Entry entries[MAX_ENTRIES];
	int count = 0;
	if (strcmp(what, "ships") == 0)
		count = ship_entries(entries);
	if (count == 0)
	{
		fprintf(stderr, "warning: TYR3D_VIEWER: nothing to show for '%s' (try 'ships')\n", what);
		return;
	}

	// The palette levels are played in (that of the in-game panel picture).
	memcpy(colors, palettes[pcxpal[3 - 1]], sizeof(colors));
	set_palette(colors, 0, 255);

	const float yaw = env_float("TYR3D_VIEWER_YAW", 0);
	const float roll = env_float("TYR3D_VIEWER_ROLL", 0);
	const float spin = env_float("TYR3D_VIEWER_SPIN", 0);

	// Pairs of 3D appearance (left) and sprite (right), four to a row, centred in the playfield.
	const int columns = 4, pair_w = 62, row_h = 40;
	const int rows = (count + columns - 1) / columns;
	const int left = L3D_PLAYFIELD_X + (L3D_PLAYFIELD_W - columns * pair_w) / 2;
	const int top = (L3D_PLAYFIELD_H - rows * row_h) / 2;

	JE_clr256(VGAScreenSeg);  // no panel around the playfield
	for (unsigned int frame = 0; ; ++frame)
	{
		VGAScreen = game_screen;
		l3d_frame_begin(L3D_GROUND);
		clear_with_overscan(game_screen);
		l3d_phase(L3D_PLAYER);

		for (int i = 0; i < count; ++i)
		{
			const Entry *e = &entries[i];
			// Centre of the left cell; sprites are drawn from their top left corner, 12 and 14
			// pixels from their centre, as the game draws the player's ship.
			const int x = left + (i % columns) * pair_w + 12 + 5;
			const int y = top + (i / columns) * row_h + 14 + 6;
			const float turn = e->look.yaw + yaw + spin * frame;

			if (e->look.model >= 0)
				l3d_add_object(e->look.model, x, y, e->look.height, turn, roll, 0);
			else if (e->look.model == M3D_VOLUME)
				l3d_add_volume(e->sheet, e->sprite, true, V3D_STYLE_RAISED, x, y, e->look.height, turn, roll, 0);
			else
				blit_sprite2x2(VGAScreen, x - 12, y - 14, *e->sheet, e->sprite);

			blit_sprite2x2(VGAScreen, x + 28 - 12, y - 14, *e->sheet, e->sprite);
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
