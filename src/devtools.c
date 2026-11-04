/*
 * Tyrian3D developer tooling: environment-driven helpers for automated testing.
 */
#include "devtools.h"

#include "config.h"
#include "debugmode.h"
#include "episodes.h"
#include "joystick.h"
#include "layer3d.h"
#include "lvlmast.h"
#include "models3d.h"
#include "mtrand.h"
#include "palette.h"
#include "params.h"
#include "player.h"
#include "sprite.h"
#include "tyrian2.h"
#include "varz.h"
#include "video.h"
#include "volume3d.h"

#include <SDL3/SDL.h>

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static long env_long(const char *name, long fallback)
{
	const char *value = SDL_getenv(name);
	return (value != NULL && *value != '\0') ? strtol(value, NULL, 10) : fallback;
}

Uint32 dev_demo_idle_ms(void)
{
	return (Uint32)env_long("TYR3D_DEMO_IDLE_MS", 30000);
}

static long frame = 0;
static SDL_AtomicInt key_pressed;  // TYR3D_DUMP_KEYS: a test key since the last dump
static SDL_AtomicInt key_pending;  // a test key pushed, not yet taken by the game (dev_input_taken)

static bool dumping_this_frame(void)
{
	if (SDL_getenv("TYR3D_DUMP_KEYS") != NULL)
		return SDL_getenv("TYR3D_DUMP_DIR") != NULL && SDL_GetAtomicInt(&key_pressed) != 0;
	const long dump_every = env_long("TYR3D_DUMP_EVERY", 60);
	return SDL_getenv("TYR3D_DUMP_DIR") != NULL && dump_every > 0 && (frame + 1) % dump_every == 0 &&
	       frame + 1 >= env_long("TYR3D_DUMP_FROM", 0);
}

void dev_input_taken(void)
{
	if (SDL_GetAtomicInt(&key_pending) != 0)
	{
		SDL_SetAtomicInt(&key_pending, 0);
		SDL_SetAtomicInt(&key_pressed, 1);
	}
}

bool dev_capture_next_frame(void)
{
	return dumping_this_frame() || debug_flight_snapshot_wanted();
}

bool dev_dumping_frame(void)
{
	return dumping_this_frame();
}

void dev_on_layers_captured(void)
{
	if (SDL_getenv("TYR3D_DUMP_LAYERS") == NULL || !dumping_this_frame())
		return;

	static Uint32 rgba[L3D_WIDTH * L3D_ROWS];
	for (int l = 0; l < l3d_frame.layer_count; ++l)
	{
		const L3DLayer *layer = &l3d_frame.layers[l];
		for (int i = 0; i < L3D_WIDTH * L3D_ROWS; ++i)
			rgba[i] = layer->cover[i] ? rgb_palette[layer->index[i]] : pack_rgba(255, 0, 255);

		SDL_Surface *surface = SDL_CreateSurfaceFrom(L3D_WIDTH, L3D_ROWS, SDL_PIXELFORMAT_RGBA32, rgba, L3D_WIDTH * 4);
		if (surface != NULL)
		{
			char path[1024];
			snprintf(path, sizeof(path), "%s/frame_%06ld_layer%02d_%s.bmp", SDL_getenv("TYR3D_DUMP_DIR"), frame + 1, l, l3d_layer_name(layer->type));
			SDL_SaveBMP(surface, path);
			SDL_DestroySurface(surface);
		}
	}

	for (int i = 0; i < l3d_frame.background_count; ++i)
	{
		const L3DBackground *b = &l3d_frame.backgrounds[i];
		printf("frame %ld: background %d in layer %d (%s)%s at %d,%d, %d effects\n", frame + 1, b->set, b->layer,
		       l3d_layer_name(l3d_frame.layers[b->layer].type), b->blend ? " blended" : "", b->x, b->top_y, b->effect_count);
	}
}

bool dev_start_game(void)
{
	static bool started = false;
	const char *start = SDL_getenv("TYR3D_START");
	if (started || start == NULL)
		return false;
	started = true;

	int episode = 0, section = 0;
	// A custom episode by its folder's name: <name>:<section> (episodes.h).
	char name[32] = "";
	if (sscanf(start, "%31[^:]:%d", name, &section) == 2 && custom_episode_find(name) != 0 && section >= 1 && section <= 255)
	{
		custom_episode = custom_episode_find(name);
		return dev_setup_game(custom_episodes[custom_episode - 1].episode, section);
	}
	if (sscanf(start, "%d:%d", &episode, &section) != 2 || episode < 1 || episode > EPISODE_MAX ||
	    section < 1 || section > 255)
	{
		fprintf(stderr, "warning: TYR3D_START must be <episode>:<section> or <custom episode>:<section>, got '%s'\n", start);
		return false;
	}
	return dev_setup_game(episode, section);
}

bool dev_setup_game(int episode, int section)
{

	// The same random numbers every run (TYR3D_SEED picks others), so runs can be compared frame
	// by frame.
	const char *seed = SDL_getenv("TYR3D_SEED");
	mt_srand(seed != NULL ? strtoul(seed, NULL, 10) : 1);

	// As newGame() does for a one-player full game.
	onePlayerAction = false;
	twoPlayerMode = false;
	timedBattleMode = false;
	JE_initEpisode((JE_byte)episode);
	initial_episode_num = episodeNum;
	difficultyLevel = DIFFICULTY_NORMAL;
	// TYR3D_DIFFICULTY=<n> (config.h's: 1 easy, 2 normal, 3 hard ...): some levels differ from Hard on (TYRIAN's
	// and SAVARA's maps in episode 1).
	if (SDL_getenv("TYR3D_DIFFICULTY") != NULL)
		difficultyLevel = (JE_byte)SDL_clamp(SDL_atoi(SDL_getenv("TYR3D_DIFFICULTY")), DIFFICULTY_WIMP, DIFFICULTY_NORTANEOUS);
	initialDifficulty = difficultyLevel;
	player[0].cash = 10000;
	const char *ship = SDL_getenv("TYR3D_SHIP");  // ship id as in the shop (1-18)
	if (ship != NULL)
		player[0].items.ship = (JE_byte)SDL_atoi(ship);
	const char *sidekicks = SDL_getenv("TYR3D_SIDEKICKS");  // "<left>,<right>" ids as in the shop
	int left = 0, right = 0;
	if (sidekicks != NULL && sscanf(sidekicks, "%d,%d", &left, &right) >= 1)
	{
		player[0].items.sidekick[LEFT_SIDEKICK] = (JE_byte)SDL_clamp(left, 0, OPTION_NUM);
		player[0].items.sidekick[RIGHT_SIDEKICK] = (JE_byte)SDL_clamp(right, 0, OPTION_NUM);
	}

	const char *special_weapon = SDL_getenv("TYR3D_SPECIAL");  // a special weapon, its id (the item data's)
	if (special_weapon != NULL)
		player[0].items.special = (JE_byte)SDL_clamp(SDL_atoi(special_weapon), 0, SPECIAL_NUM);

	// "<front>,<rear>[,<power>]": the weapons, ids as in the shop's weapon ports, and their power (1-11).
	const char *weapons = SDL_getenv("TYR3D_WEAPONS");
	int front = 0, rear = 0, power = 1;
	if (weapons != NULL && sscanf(weapons, "%d,%d,%d", &front, &rear, &power) >= 1)
	{
		player[0].items.weapon[FRONT_WEAPON].id = (JE_byte)SDL_clamp(front, 0, PORT_NUM);
		player[0].items.weapon[REAR_WEAPON].id = (JE_byte)SDL_clamp(rear, 0, PORT_NUM);
		player[0].items.weapon[FRONT_WEAPON].power = player[0].items.weapon[REAR_WEAPON].power = (JE_byte)SDL_clamp(power, 1, WEAPON_POWER_OVERCLOCK);
	}

	// Other game modes, as newGame() and newSuperArcadeGame() set them up.
	const char *mode = SDL_getenv("TYR3D_MODE");
	int mode_number = 1;
	if (mode != NULL && strcmp(mode, "arcade") == 0)
	{
		onePlayerAction = true;
		player[0].cash = 0;
		player[0].items.ship = 8;  // Stalker
	}
	else if (mode != NULL && strcmp(mode, "two") == 0)
	{
		twoPlayerMode = true;
		for (uint i = 0; i < COUNTOF(player); ++i)
			player[i].cash = 0;
		player[0].items.ship = 11;  // Silver Ship
		difficultyLevel++;
		inputDevice[0] = 1;
		inputDevice[1] = 2;
	}
	else if (mode != NULL && strcmp(mode, "twin") == 0)
	{
		// Twin-stick (player.h), as newGame() sets it up.
		twoPlayerMode = true;
		twinStickMode = true;
		for (uint i = 0; i < COUNTOF(player); ++i)
			player[i].cash = 0;
		player[0].items.ship = 11;  // Silver Ship
		inputDevice[0] = inputDevice[1] = 0;
	}
	else if (mode != NULL && sscanf(mode, "timed:%d", &mode_number) == 1)
	{
		timedBattleMode = true;
		onePlayerAction = true;
		timeBattleSelection = (JE_byte)SDL_clamp(mode_number, 1, 2);
		player[0].cash = 0;
		player[0].items.ship = 8;
	}
	else if (mode != NULL && sscanf(mode, "super:%d", &mode_number) == 1)
	{
		const int i = SDL_clamp(mode_number, 1, SA_LASTSHIP) - 1;
		onePlayerAction = true;
		superArcadeMode = (JE_byte)(i + 1);
		player[0].cash = 0;
		player[0].items.ship = SAShip[i];
		player[0].items.weapon[FRONT_WEAPON].id = SAWeapon[i][0];
		player[0].items.special = SASpecialWeapon[i];
		if (superArcadeMode == SA_NORTSHIPZ)
			for (uint k = 0; k < COUNTOF(player[0].items.sidekick); ++k)
				player[0].items.sidekick[k] = 24;  // Companion Ship Quicksilver
		difficultyLevel++;
	}
	else if (mode != NULL && strcmp(mode, "galaga") == 0)
	{
		// The secret level's mode (the "]g" script command): the second ship joins with a Vulcan
		// Cannon, as the script sets it up, in a two-player game.
		onePlayerAction = true;
		twoPlayerMode = true;
		galagaMode = true;
		player[1].items = player[0].items;
		player[1].items.weapon[REAR_WEAPON].id = 15;  // Vulcan Cannon
		for (uint k = 0; k < COUNTOF(player[1].items.sidekick); ++k)
			player[1].items.sidekick[k] = 0;
	}
	else if (mode != NULL && strcmp(mode, "full") != 0)
		fprintf(stderr, "warning: TYR3D_MODE must be full, arcade, two, twin, galaga, timed:<1-2> or super:<1-%d>\n",
		        SA_LASTSHIP);
	initialDifficulty = difficultyLevel;

	// Skip shops (they jump straight to the next level), unless TYR3D_SHOP=1.
	constantPlay = SDL_getenv("TYR3D_SHOP") == NULL || SDL_atoi(SDL_getenv("TYR3D_SHOP")) == 0;
	mainLevel = (JE_byte)section;
	gameLoaded = true;

	printf("devtools: starting episode %d at section %d%s%s\n", episode, section, mode != NULL ? ", mode " : "",
	       mode != NULL ? mode : "");
	return true;
}

void dev_level_start_items(void)
{
	const char *bombs = SDL_getenv("TYR3D_BOMBS");  // super bombs at each level's start
	if (bombs != NULL && SDL_getenv("TYR3D_START") != NULL)
		player[0].superbombs = (uint)SDL_clamp(SDL_atoi(bombs), 0, 10);
	const char *armor = SDL_getenv("TYR3D_ARMOR");  // the ship's armor at each level's start (under 6: the warning)
	if (armor != NULL && SDL_getenv("TYR3D_START") != NULL)
		player[0].armor = (uint)SDL_clamp(SDL_atoi(armor), 1, 28);
}

bool dev_background_run(void)
{
	return SDL_getenv("TYR3D_WINDOWED") != NULL;
}

void dev_level_tick(void)
{
	static const char *limit = NULL;
	static bool looked = false;
	if (!looked)
		limit = SDL_getenv("TYR3D_LEVEL_TICKS"), looked = true;
	static int ticks = 0;
	const char *die = SDL_getenv("TYR3D_LEVEL_DIE");
	if (limit == NULL && die == NULL)
		return;
	++ticks;
	if (die != NULL && ticks == SDL_atoi(die) && player[0].is_alive)
	{
		printf("devtools: destroying the ship after %d ticks\n", ticks);
		JE_playerDamage(255, &player[0]);
		JE_playerDamage(255, &player[0]);
	}
	if (limit != NULL && ticks >= SDL_atoi(limit) && !reallyEndLevel)
	{
		printf("devtools: ending the level after %d ticks\n", ticks);
		reallyEndLevel = true;
		ticks = 0;
	}
	if (die != NULL && reallyEndLevel)
		ticks = 0;
}

bool dev_godmode(void)
{
	// (TYR3D_GODMODE_UNTIL=<clock>: only until the level's clock reaches that, as for a checkpoint's test)
	const char *until = SDL_getenv("TYR3D_GODMODE_UNTIL");
	return debug_flight || SDL_getenv("TYR3D_GODMODE") != NULL || (until != NULL && curLoc < SDL_atoi(until));
}

void dev_balance(const char *what, int value)
{
	static int on = -1;
	if (on < 0)
		on = SDL_getenv("TYR3D_LOG_BALANCE") != NULL;
	if (on)
		printf("balance: %s %d clock %u\n", what, value, (unsigned)curLoc);
}

/*
 * TYR3D_LOG_SPRITES: what the 3D view draws from a sprite (an HD volume from the 4x sheets, the sprite's own volume,
 * flat for shots, or the flat sprite) rather than as a model, with a model of the same thing where models.cfg has one.
 * Each look once, as it is first drawn so ("sprites: look ..."); a summary for each level as it ends and for the run
 * ("sprites: level ...", "sprites: run ..."). The objects are told apart by their keys (layer3d.h L3D_KEY_*, tyrian2.c's
 * coming enemies and stand-ins).
 */
enum { SPRITES_ENEMY, SPRITES_ITEM, SPRITES_COMING, SPRITES_SHOT, SPRITES_ENEMY_SHOT, SPRITES_DEPARTED, SPRITES_PLAYER,
       SPRITES_SIDEKICK, SPRITES_STORE, SPRITES_OTHER, SPRITES_KINDS };
static const char *const sprites_kind_names[SPRITES_KINDS] = { "enemy", "item", "coming", "shot", "enemyshot", "departed",
                                                               "player", "sidekick", "store", "other" };

typedef struct
{
	Uint32 frames;
	Uint32 models[SPRITES_KINDS], sprites[SPRITES_KINDS];  // objects drawn, over the frames
	Uint32 looks[SPRITES_KINDS], related[SPRITES_KINDS];   // looks first drawn as sprites, and of those with a model near
	Uint32 overlay_frames;                                  // frames with the game's drawing over the playfield
} SpritesCount;

static SpritesCount sprites_level, sprites_run;
static char sprites_level_name[24] = "";

bool dev_log_sprites_on(void)
{
	static int on = -1;
	if (on < 0)
		on = SDL_getenv("TYR3D_LOG_SPRITES") != NULL;
	return on != 0;
}

// The sheet's name as models.cfg writes it (a shape file's letter small, its symbols as x<hex>), and its letter for
// m3d_enemy_appearance (0: not an enemy sheet).
static const char *sprites_sheet_name(const void *sheet, char *letter, char name[8])
{
	*letter = 0;
	if (sheet == &spriteSheet8)
		return "shots";
	if (sheet == &spriteSheet12)
		return "shots2";
	if (sheet == &spriteSheet9)
		return "ships";
	if (sheet == &spriteSheetT2000)
		return "ships_t2000";
	if (sheet == &explosionSpriteSheet)
		return "explosions";
	if (sheet == &spriteSheet11)
	{
		*letter = M3D_SHEET_COINS;
		return "coins";
	}
	if (sheet == &spriteSheet10)
	{
		*letter = M3D_SHEET_POWERUPS;
		return "powerups";
	}
	for (size_t k = 0; k < COUNTOF(enemySpriteSheetIds); ++k)
		if (sheet == &enemySpriteSheets[k] && enemySpriteSheetIds[k] > 0 && enemySpriteSheetIds[k] <= COUNTOF(shapeFile))
		{
			*letter = shapeFile[enemySpriteSheetIds[k] - 1];
			const char c = (char)SDL_tolower((unsigned char)*letter);
			if (SDL_isalnum((unsigned char)c))
				snprintf(name, 8, "%c", c);
			else
				snprintf(name, 8, "x%02x", (unsigned char)c);
			return name;
		}
	return "?";
}

// The model of models.cfg's "sprite" line for exactly this sheet and first sprite, or -1.
static int sprites_rule_model(char letter, unsigned int sprite)
{
	letter = (char)SDL_tolower((unsigned char)letter);
	for (int i = 0; i < m3d_sprite_rule_count(); ++i)
	{
		char sheet;
		unsigned int first;
		M3DAppearance look;
		m3d_sprite_rule(i, &sheet, &first, &look);
		if (sheet == letter && first == sprite)
			return look.model;
	}
	return -1;
}

// A model of the same thing (hint: what it is), or -1: its own sprite or shot line, which the path that drew it went
// without; for an enemy or item, a sprite line for another frame of its animation, or a frame line of one. (Sprites next
// to it on its sheet are often other things: left to a look at the log.)
static int sprites_related(int kind, char letter, const void *sheet, unsigned int first, const JE_word *frames, int frame_count,
                           char *hint, size_t hint_size)
{
	if (kind == SPRITES_SHOT || kind == SPRITES_ENEMY_SHOT || kind == SPRITES_DEPARTED || kind == SPRITES_STORE)
	{
		if (sheet != &spriteSheet8 && sheet != &spriteSheet12)
			return -1;
		const bool shots2 = sheet == &spriteSheet12;
		M3DAppearance look;
		if (m3d_shot_appearance(shots2, first, &look))
		{
			snprintf(hint, hint_size, "its own shot line (%s), not drawn", m3d_models[look.model].name);
			return look.model;
		}
		return -1;
	}
	if (letter == 0)
		return -1;
	const M3DAppearance own = m3d_enemy_appearance(letter, first, false, L3D_SKY_ENEMY);
	if (own.model >= 0)
	{
		snprintf(hint, hint_size, "its own sprite line (%s), not drawn", m3d_models[own.model].name);
		return own.model;
	}
	for (int f = 0; f < frame_count; ++f)
	{
		if (frames[f] == first || frames[f] == 0 || frames[f] == 999)
			continue;
		int model = sprites_rule_model(letter, frames[f]);
		if (model >= 0)
		{
			snprintf(hint, hint_size, "its frame %u's sprite line (%s)", frames[f], m3d_models[model].name);
			return model;
		}
		model = m3d_frame_model(letter, frames[f], -1);
		if (model >= 0)
		{
			snprintf(hint, hint_size, "its frame %u's frame line (%s)", frames[f], m3d_models[model].name);
			return model;
		}
	}
	return -1;
}

static void sprites_print_count(const char *what, const char *name, const SpritesCount *c)
{
	Uint32 models = 0, sprites = 0, looks = 0, related = 0;
	for (int k = 0; k < SPRITES_KINDS; ++k)
	{
		models += c->models[k];
		sprites += c->sprites[k];
		looks += c->looks[k];
		related += c->related[k];
	}
	printf("sprites: %s %s: %u frames; objects drawn as models %u, from sprites %u (%.1f %%); looks from sprites %u, "
	       "%u of them with a model near; overlay in %u frames;", what, name, c->frames, models, sprites,
	       models + sprites > 0 ? 100.0 * sprites / (models + sprites) : 0.0, looks, related, c->overlay_frames);
	for (int k = 0; k < SPRITES_KINDS; ++k)
		if (c->sprites[k] > 0 || c->looks[k] > 0)
			printf(" %s %u/%u looks %u near %u;", sprites_kind_names[k], c->sprites[k], c->models[k] + c->sprites[k], c->looks[k],
			       c->related[k]);
	printf("\n");
}

static void sprites_level_over(void)
{
	if (sprites_level.frames > 0)
		sprites_print_count("level", sprites_level_name, &sprites_level);
	memset(&sprites_level, 0, sizeof(sprites_level));
}

static void sprites_at_exit(void)
{
	sprites_level_over();
	sprites_print_count("run", "total", &sprites_run);
	fflush(stdout);
}

// Whether a look was seen before (and now is): its kind, sheet (by name: the enemies' sheets' slots take other sheets
// from level to level) and first sprite.
static bool sprites_seen(int kind, const char *sheet_name, unsigned int first, bool large)
{
	enum { LOOKS = 4096 };
	typedef struct { char sheet[12]; Uint16 first; Uint8 kind, large; } Seen;
	static Seen seen[LOOKS];
	static int count = 0;
	for (int i = 0; i < count; ++i)
		if (seen[i].first == first && seen[i].kind == kind && seen[i].large == large && strcmp(seen[i].sheet, sheet_name) == 0)
			return true;
	if (count < LOOKS)
	{
		seen[count] = (Seen){ "", (Uint16)first, (Uint8)kind, (Uint8)large };
		SDL_strlcpy(seen[count++].sheet, sheet_name, sizeof(seen[0].sheet));
	}
	return false;
}

// One look drawn from a sprite (first drawn now): what, where, and a model near it.
static void sprites_note(int kind, const void *sheet, unsigned int sprite, unsigned int first, const JE_word *frames,
                         int frame_count, bool large, int style, const char *layer, float x, float y)
{
	char letter, name[8], hint[96] = "";
	const char *sheet_name = sprites_sheet_name(sheet, &letter, name);
	if (sprites_seen(kind, sheet_name, first, large))
		return;
	const int related = sprites_related(kind, letter, sheet, first, frames, frame_count, hint, sizeof(hint));
	++sprites_level.looks[kind];
	++sprites_run.looks[kind];
	if (related >= 0)
	{
		++sprites_level.related[kind];
		++sprites_run.related[kind];
	}
	printf("sprites: look %s sheet %s sprite %u first %u %s %s layer %s at %.0f,%.0f episode %d level %s clock %u -> %s\n",
	       sprites_kind_names[kind], sheet_name, sprite, first, large ? "2x2" : "1x1",
	       style < 0 ? "sprite" : style == V3D_STYLE_FLAT ? "flat" : "volume",
	       layer, x, y, episodeNum, sprites_level_name, (unsigned)curLoc, related >= 0 ? hint : "no model");
}

void dev_log_sprites_frame(void)
{
	if (!dev_log_sprites_on())
		return;
	static bool registered = false;
	if (!registered)
	{
		registered = true;
		atexit(sprites_at_exit);
	}
	char name[24];
	snprintf(name, sizeof(name), "%d:%.10s", episodeNum, levelName);
	for (char *c = name + strlen(name); c > name && c[-1] == ' '; --c)
		c[-1] = '\0';
	if (strcmp(name, sprites_level_name) != 0)
	{
		sprites_level_over();
		SDL_strlcpy(sprites_level_name, name, sizeof(sprites_level_name));
	}
	++sprites_level.frames;
	++sprites_run.frames;

	// The game's own drawing over the playfield (the overlay layer: pixels the 3D view shows flat, at the screen's
	// size, as text, bars or brightened bands): where and how much, at most once a second while it shows.
	{
		static Uint32 last_told = 0;
		int count = 0, x0 = L3D_WIDTH, y0 = L3D_ROWS, x1 = -1, y1 = -1;
		for (int l = 0; l < l3d_frame.layer_count; ++l)
		{
			const L3DLayer *layer = &l3d_frame.layers[l];
			if (layer->type != L3D_OVERLAY)
				continue;
			for (int y = SDL_max(layer->min_y, L3D_OVERSCAN); y < SDL_min(layer->max_y, L3D_OVERSCAN + L3D_PLAYFIELD_H); ++y)
				for (int x = l3d_field_x(); x < l3d_field_x() + l3d_field_w(); ++x)
					if (layer->cover[y * L3D_WIDTH + x])
					{
						++count;
						x0 = SDL_min(x0, x), x1 = SDL_max(x1, x), y0 = SDL_min(y0, y), y1 = SDL_max(y1, y);
					}
		}
		if (count > 0)
		{
			++sprites_level.overlay_frames;
			++sprites_run.overlay_frames;
			if (l3d_frame_number - last_told >= 60 || last_told == 0)
			{
				last_told = l3d_frame_number;
				printf("sprites: overlay %d px at %d,%d-%d,%d episode %d level %s clock %u frame %ld\n", count, x0, y0 - L3D_OVERSCAN, x1,
				       y1 - L3D_OVERSCAN, episodeNum, sprites_level_name, (unsigned)curLoc, frame);
			}
		}
	}

	for (int o = 0; o < l3d_frame.object_count; ++o)
	{
		const L3DObject *object = &l3d_frame.objects[o];
		const Uint32 key = object->key;
		int kind = key >= 0x70000u ? SPRITES_OTHER          // (tyrian2.c's stand-ins: models)
		         : key >= 0x60000u ? SPRITES_DEPARTED       // (layer3d.c L3D_KEY_DEPARTED)
		         : key >= 0x50000u ? SPRITES_COMING         // (tyrian2.c COMING_KEY)
		         : key >= L3D_KEY_ENEMY_SHOT ? SPRITES_ENEMY_SHOT
		         : key >= L3D_KEY_SHOT ? SPRITES_SHOT
		         : key >= L3D_KEY_SIDEKICK ? SPRITES_SIDEKICK
		         : key >= L3D_KEY_PLAYER ? SPRITES_PLAYER
		         : key >= L3D_KEY_ENEMY ? SPRITES_ENEMY
		         : SPRITES_OTHER;
		if ((kind == SPRITES_ENEMY || kind == SPRITES_COMING) &&
		    (object->model == L3D_VOLUME ? object->sheet == &spriteSheet10 || object->sheet == &spriteSheet11
		                                 : object->enemy_sheet == M3D_SHEET_COINS || object->enemy_sheet == M3D_SHEET_POWERUPS))
			kind = kind == SPRITES_ENEMY ? SPRITES_ITEM : kind;
		if (object->model != L3D_VOLUME)
		{
			++sprites_level.models[kind];
			++sprites_run.models[kind];
			continue;
		}
		if (l3d_sprite_glow_color(object->sheet, object->sprite, object->large) == 0)
			continue;  // (a blank sprite: nothing shows, as the TYRIAN boss's parts once destroyed)
		++sprites_level.sprites[kind];
		++sprites_run.sprites[kind];

		// The enemy's animation (its slot by its key), to name it by its first sprite as models.cfg does.
		unsigned int first = object->sprite;
		const JE_word *frames = NULL;
		int frame_count = 0;
		if (kind == SPRITES_ENEMY || kind == SPRITES_ITEM)
		{
			const unsigned int slot = (key - L3D_KEY_ENEMY) & 0xff;
			if (slot < COUNTOF(enemy) && (const void *)enemy[slot].sprite2s == object->sheet)
			{
				first = enemy[slot].egr[0];
				frames = enemy[slot].egr;
				frame_count = SDL_clamp((int)enemy[slot].ani, 1, (int)COUNTOF(enemy[slot].egr));
			}
		}
		sprites_note(kind, object->sheet, object->sprite, first, frames, frame_count, object->large, object->style,
		             l3d_layer_name(object->layer), object->x, object->y);
	}

	// Enemies in sight that left no object (keyed by their slot) three frames running, as the same enemy: drawn as their
	// flat sprites (models.cfg "sprite", a sheet with no letter). (One made after the enemies are drawn, a drop, leaves
	// none in its first frame.) Not episode 7's bosses' pieces, whose groups' other pieces draw their parts.
	if (episodeNum == EPISODE_GBC)
		return;
	static bool keyed[COUNTOF(enemy)];
	static Uint8 unkeyed[COUNTOF(enemy)];  // frames running
	static const void *was_sheet[COUNTOF(enemy)];
	static JE_word was_first[COUNTOF(enemy)];
	memset(keyed, 0, sizeof(keyed));
	for (int o = 0; o < l3d_frame.object_count; ++o)
	{
		const Uint32 key = l3d_frame.objects[o].key;
		if (key >= L3D_KEY_ENEMY && key < L3D_KEY_PLAYER && (key & 0xff) < COUNTOF(enemy))
			keyed[key & 0xff] = true;
	}
	for (unsigned int i = 0; i < COUNTOF(enemy); ++i)
	{
		const struct JE_SingleEnemyType *e = &enemy[i];
		const bool same = enemyAvail[i] != 1 && was_sheet[i] == (const void *)e->sprite2s && was_first[i] == e->egr[0];
		was_sheet[i] = enemyAvail[i] != 1 ? (const void *)e->sprite2s : NULL;
		was_first[i] = e->egr[0];
		unkeyed[i] = !keyed[i] && same ? (Uint8)SDL_min(unkeyed[i] + 1, 250) : !keyed[i] && enemyAvail[i] != 1;
		// (Where the game draws it: by its layer's offset as it was drawn, mapoffset.)
		if (enemyAvail[i] == 1 || unkeyed[i] < 3 || e->sprite2s == NULL || e->enemycycle == 0 || e->egr[e->enemycycle - 1] == 999 ||
		    e->egr[e->enemycycle - 1] == 0 || e->ey < -12 || e->ey > 180 || e->ex + (int)e->mapoffset < -16 ||
		    e->ex + (int)e->mapoffset > 300)
			continue;
		const int kind = e->sprite2s == &spriteSheet10 || e->sprite2s == &spriteSheet11 ? SPRITES_ITEM : SPRITES_ENEMY;
		if (l3d_sprite_glow_color(e->sprite2s, e->egr[e->enemycycle - 1], e->size == 1) == 0)
			continue;  // (blank)
		++sprites_level.sprites[kind];
		++sprites_run.sprites[kind];
		sprites_note(kind, e->sprite2s, e->egr[e->enemycycle - 1], e->egr[0], e->egr, SDL_clamp((int)e->ani, 1, 20), e->size == 1,
		             -1, "?", e->ex + (int)e->mapoffset + 6.0f, e->ey + 7.0f);
	}
}

// The store's weapon simulator: a shot drawn from its sprite (shots2: the second sheet) or as a model.
void dev_log_sprites_store(bool shots2, unsigned int sprite, bool model)
{
	if (!dev_log_sprites_on())
		return;
	SDL_strlcpy(sprites_level_name, "store", sizeof(sprites_level_name));
	if (model)
	{
		++sprites_level.models[SPRITES_STORE];
		++sprites_run.models[SPRITES_STORE];
		return;
	}
	++sprites_level.sprites[SPRITES_STORE];
	++sprites_run.sprites[SPRITES_STORE];
	sprites_note(SPRITES_STORE, shots2 ? (const void *)&spriteSheet12 : (const void *)&spriteSheet8, sprite, sprite, NULL, 0,
	             false, V3D_STYLE_FLAT, "store", 0, 0);
}

bool dev_autopilot(void)
{
	return SDL_getenv("TYR3D_AUTOPILOT") != NULL;
}

void dev_autopilot_steer(int x, int y, int speed, int *dx, int *dy, bool *fire)
{
	// Weave across the playfield with a slow vertical drift; always fire (TYR3D_AUTOPILOT=nofire: never,
	// so that enemies live to be looked at). Timed by frames, so runs started with TYR3D_START repeat
	// exactly (see dev_start_game).
	const double t = frame / 35.0;
	// (Across the wide playfield's 16-288 when it is on. TYR3D_AUTOPILOT=park: held in the bottom left corner,
	// never firing, as tools/gbc/boss_rom.py flies the GBC's bosses: out of their way, so they live their loops.)
	const bool park = SDL_strcmp(SDL_getenv("TYR3D_AUTOPILOT"), "park") == 0;
	int target_x = park ? 0 : l3d_field_wide ? 152 + (int)(128 * SDL_sin(t * 0.9)) : 140 + (int)(100 * SDL_sin(t * 0.9));
	// (TYR3D_AUTOPILOT=aim: under the boss bars' enemy while there is one, weaving a little: episode 6's HOARD fights
	// run through in a test.)
	int boss_x;
	if (SDL_strcmp(SDL_getenv("TYR3D_AUTOPILOT"), "aim") == 0 && boss_bar_enemy_x(&boss_x))
		target_x = boss_x + (int)(36 * SDL_sin(t * 1.7));
	const int target_y = park ? 999 : 140 + (int)(25 * SDL_sin(t * 0.37));

	if (x < target_x - speed)
		*dx += speed;
	else if (x > target_x + speed)
		*dx -= speed;
	if (y < target_y - speed)
		*dy += speed;
	else if (y > target_y + speed)
		*dy -= speed;

	*fire = SDL_strcmp(SDL_getenv("TYR3D_AUTOPILOT"), "nofire") != 0 && !park;
}

/*
 * TYR3D_TEST_KEYS=<frame>:<key>[,<ms>:<key>...]: presses a key (an SDL scancode name: P, Escape,
 * Return, Down...; MouseLeft, MouseRight, MouseMiddle; <key>*<ms> holds it that long; MouseTo<x>x<y>
 * moves the pointer to that window point, where the mouse buttons then click; WheelUp, WheelDown turn
 * the mouse wheel a notch; Joy<key> presses the key as a joystick's: joystick.h; Type<text> types the text;
 * with TYR3D_TEST_PAD=1 a virtual gamepad: PadLX<v>, PadLY<v>, PadRX<v>, PadRY<v> put a stick's axis at
 * v (-1..1, right and down positive) and leave it there, PadLT<v>, PadRT<v> a trigger (0..1), PadA, PadB,
 * PadX, PadY, PadBack, PadStart, PadLB, PadRB press a button)
 * when that frame is
 * presented, then each next one so many milliseconds after the one before (menus wait for keys
 * without presenting frames). The list may be any length.
 */
static SDL_Joystick *test_pad = NULL;  // TYR3D_TEST_PAD's virtual gamepad

void dev_attach_test_pad(void)
{
	if (SDL_getenv("TYR3D_TEST_PAD") == NULL || test_pad != NULL)
		return;
	// (A test window runs without the focus, where SDL would drop the pad's presses.)
	SDL_SetHint(SDL_HINT_JOYSTICK_ALLOW_BACKGROUND_EVENTS, "1");
	SDL_VirtualJoystickDesc desc;
	SDL_INIT_INTERFACE(&desc);
	desc.type = SDL_JOYSTICK_TYPE_GAMEPAD;
	desc.naxes = SDL_GAMEPAD_AXIS_COUNT;  // (in the gamepad's order: left x, y, right x, y, the triggers)
	desc.nbuttons = SDL_GAMEPAD_BUTTON_COUNT;
	desc.name = "Tyrian3D test pad";
	const SDL_JoystickID id = SDL_AttachVirtualJoystick(&desc);
	if (id == 0 || (test_pad = SDL_OpenJoystick(id)) == NULL)
	{
		fprintf(stderr, "devtools: no test pad: %s\n", SDL_GetError());
		return;
	}
	printf("devtools: test pad attached\n");
}

// A Pad key (TYR3D_TEST_PAD); false if the name isn't one.
static bool press_pad_key(const char *name, Uint32 hold);

static Uint32 SDLCALL release_pad_button(void *userdata, SDL_TimerID timer, Uint32 interval)
{
	(void)timer, (void)interval;
	if (test_pad != NULL)
		SDL_SetJoystickVirtualButton(test_pad, (int)(intptr_t)userdata, false);
	return 0;
}

static bool press_pad_key(const char *name, Uint32 hold)
{
	if (strncmp(name, "Pad", 3) != 0 || name[3] == '\0')
		return false;
	name += 3;
	if (test_pad == NULL)
	{
		fprintf(stderr, "devtools: Pad%s without TYR3D_TEST_PAD\n", name);
		return true;
	}
	static const struct { const char *name; int axis; bool trigger; } axes[] = {
		{ "LX", SDL_GAMEPAD_AXIS_LEFTX, false }, { "LY", SDL_GAMEPAD_AXIS_LEFTY, false },
		{ "RX", SDL_GAMEPAD_AXIS_RIGHTX, false }, { "RY", SDL_GAMEPAD_AXIS_RIGHTY, false },
		{ "LT", SDL_GAMEPAD_AXIS_LEFT_TRIGGER, true }, { "RT", SDL_GAMEPAD_AXIS_RIGHT_TRIGGER, true },
	};
	for (size_t i = 0; i < SDL_arraysize(axes); ++i)
		if (strncmp(name, axes[i].name, 2) == 0 && name[2] != '\0')
		{
			// (a trigger's axis runs from its minimum at rest to its maximum)
			const float v = SDL_clamp(strtof(name + 2, NULL), axes[i].trigger ? 0.0f : -1.0f, 1.0f);
			const Sint16 value = (Sint16)SDL_clamp(axes[i].trigger ? -32768.0f + v * 65535.0f : v * 32767.0f, -32768.0f, 32767.0f);
			printf("devtools: pad %s at %.2f\n", axes[i].name, v);
			if (!SDL_SetJoystickVirtualAxis(test_pad, axes[i].axis, value))
				fprintf(stderr, "devtools: pad %s: %s\n", axes[i].name, SDL_GetError());
			return true;
		}
	static const struct { const char *name; int button; } buttons[] = {
		{ "A", SDL_GAMEPAD_BUTTON_SOUTH }, { "B", SDL_GAMEPAD_BUTTON_EAST }, { "X", SDL_GAMEPAD_BUTTON_WEST },
		{ "Y", SDL_GAMEPAD_BUTTON_NORTH }, { "Back", SDL_GAMEPAD_BUTTON_BACK }, { "Start", SDL_GAMEPAD_BUTTON_START },
		{ "LB", SDL_GAMEPAD_BUTTON_LEFT_SHOULDER }, { "RB", SDL_GAMEPAD_BUTTON_RIGHT_SHOULDER },
	};
	for (size_t i = 0; i < SDL_arraysize(buttons); ++i)
		if (strcmp(name, buttons[i].name) == 0)
		{
			printf("devtools: pressing pad %s for %u ms\n", name, hold);
			if (!SDL_SetJoystickVirtualButton(test_pad, buttons[i].button, true))
				fprintf(stderr, "devtools: pad %s: %s\n", name, SDL_GetError());
			SDL_AddTimer(hold, release_pad_button, (void *)(intptr_t)buttons[i].button);
			return true;
		}
	fprintf(stderr, "devtools: no pad key Pad%s\n", name);
	return true;
}

static char *test_keys = NULL;  // a copy of the variable's value, for the program's life
static const char *next_test_key = NULL;
static float test_pointer_x = 0, test_pointer_y = 0;  // where MouseTo put the pointer (window points)

static Uint32 SDLCALL release_mouse(void *userdata, SDL_TimerID timer, Uint32 interval)
{
	(void)timer, (void)interval;
	SDL_Event event = { 0 };
	event.type = SDL_EVENT_MOUSE_BUTTON_UP;
	event.button.windowID = SDL_GetWindowID(main_window);
	event.button.button = (Uint8)(intptr_t)userdata;
	event.button.x = test_pointer_x;
	event.button.y = test_pointer_y;
	SDL_PushEvent(&event);
	return 0;
}

// A modifier key's flag (Shift, Ctrl, Alt, GUI), or none: a pressed one is held in SDL's modifier state too, as
// a real key would be (the game asks SDL_GetModState: the difficulty menu's Shift+G).
static SDL_Keymod modifier_of(SDL_Scancode scancode)
{
	switch (scancode)
	{
	case SDL_SCANCODE_LSHIFT: return SDL_KMOD_LSHIFT;
	case SDL_SCANCODE_RSHIFT: return SDL_KMOD_RSHIFT;
	case SDL_SCANCODE_LCTRL: return SDL_KMOD_LCTRL;
	case SDL_SCANCODE_RCTRL: return SDL_KMOD_RCTRL;
	case SDL_SCANCODE_LALT: return SDL_KMOD_LALT;
	case SDL_SCANCODE_RALT: return SDL_KMOD_RALT;
	case SDL_SCANCODE_LGUI: return SDL_KMOD_LGUI;
	case SDL_SCANCODE_RGUI: return SDL_KMOD_RGUI;
	default: return SDL_KMOD_NONE;
	}
}

static Uint32 SDLCALL release_key(void *userdata, SDL_TimerID timer, Uint32 interval)
{
	(void)timer, (void)interval;
	SDL_Event event = { 0 };
	event.type = SDL_EVENT_KEY_UP;
	event.key.scancode = (SDL_Scancode)(intptr_t)userdata;
	event.key.key = SDL_GetKeyFromScancode(event.key.scancode, SDL_KMOD_NONE, false);
	const SDL_Keymod mod = modifier_of(event.key.scancode);
	if (mod != SDL_KMOD_NONE)
		SDL_SetModState(SDL_GetModState() & ~mod);
	event.key.mod = SDL_GetModState();
	SDL_PushEvent(&event);
	return 0;
}

static void press_key(const char *name)
{
	// "<key>*<ms>": held that long (default 100 ms). MouseLeft, MouseRight, MouseMiddle: mouse buttons.
	char key[32];
	snprintf(key, sizeof(key), "%s", name);
	Uint32 hold = 100;
	char *star = strchr(key, '*');
	if (star != NULL)
	{
		hold = (Uint32)SDL_max(strtol(star + 1, NULL, 10), 1);
		*star = '\0';
	}
	name = key;
	if (press_pad_key(name, hold))
		return;
	const int mouse_button = strcmp(name, "MouseLeft") == 0 ? SDL_BUTTON_LEFT : strcmp(name, "MouseRight") == 0 ? SDL_BUTTON_RIGHT
	                       : strcmp(name, "MouseMiddle") == 0 ? SDL_BUTTON_MIDDLE : 0;
	if (mouse_button != 0)
	{
		printf("devtools: pressing %s for %u ms\n", name, hold);
		SDL_Event event = { 0 };
		event.type = SDL_EVENT_MOUSE_BUTTON_DOWN;
		event.button.windowID = SDL_GetWindowID(main_window);
		event.button.button = (Uint8)mouse_button;
		event.button.down = true;
		event.button.x = test_pointer_x;
		event.button.y = test_pointer_y;
		SDL_PushEvent(&event);
		SDL_AddTimer(hold, release_mouse, (void *)(intptr_t)mouse_button);
		return;
	}
	// WheelUp, WheelDown: a notch of the mouse wheel, where the pointer is.
	if (strcmp(name, "WheelUp") == 0 || strcmp(name, "WheelDown") == 0)
	{
		printf("devtools: turning the wheel %s\n", name + 5);
		SDL_Event event = { 0 };
		event.type = SDL_EVENT_MOUSE_WHEEL;
		event.wheel.windowID = SDL_GetWindowID(main_window);
		event.wheel.y = name[5] == 'U' ? 1.0f : -1.0f;
		event.wheel.integer_y = name[5] == 'U' ? 1 : -1;
		event.wheel.direction = SDL_MOUSEWHEEL_NORMAL;
		event.wheel.mouse_x = test_pointer_x;
		event.wheel.mouse_y = test_pointer_y;
		SDL_SetAtomicInt(&key_pending, 1);
		SDL_PushEvent(&event);
		return;
	}
	// (A pointer event of its own: the system pointer stays where it is.)
	int to_x = 0, to_y = 0;
	if (sscanf(name, "MouseTo%dx%d", &to_x, &to_y) == 2)
	{
		printf("devtools: moving the pointer to %d,%d\n", to_x, to_y);
		SDL_Event event = { 0 };
		event.type = SDL_EVENT_MOUSE_MOTION;
		event.motion.windowID = SDL_GetWindowID(main_window);
		event.motion.x = (float)to_x;
		event.motion.y = (float)to_y;
		const float dx = to_x - test_pointer_x, dy = to_y - test_pointer_y;
		event.motion.xrel = dx != 0 || dy != 0 ? dx : 1;  // (it moved: the game shows the pointer)
		event.motion.yrel = dy;
		test_pointer_x = (float)to_x;
		test_pointer_y = (float)to_y;
		SDL_SetAtomicInt(&key_pending, 1);
		SDL_PushEvent(&event);
		return;
	}
	// Type<text>: the text typed (a text input event: names, the title's codes).
	if (strncmp(name, "Type", 4) == 0 && name[4] != '\0')
	{
		printf("devtools: typing %s\n", name + 4);
		SDL_Event event = { 0 };
		event.type = SDL_EVENT_TEXT_INPUT;
		event.text.windowID = SDL_GetWindowID(main_window);
		event.text.text = SDL_strdup(name + 4);  // (kept: the event is taken later)
		SDL_SetAtomicInt(&key_pending, 1);
		SDL_PushEvent(&event);
		return;
	}
	// Joy<key>: the key as a joystick's (push_joysticks_as_keyboard's: the modern UI shows its buttons).
	const bool from_joystick = strncmp(name, "Joy", 3) == 0 && name[3] != '\0';
	if (from_joystick)
		name += 3;
	const SDL_Scancode scancode = SDL_GetScancodeFromName(name);
	if (scancode == SDL_SCANCODE_UNKNOWN)
	{
		fprintf(stderr, "devtools: no key %s\n", name);
		return;
	}
	printf("devtools: pressing %s%s\n", name, from_joystick ? " (as a joystick's)" : "");
	if (from_joystick)
		++joystick_keys_pushed;
	SDL_SetAtomicInt(&key_pending, 1);
	SDL_Event event = { 0 };
	event.type = SDL_EVENT_KEY_DOWN;
	event.key.scancode = scancode;
	event.key.key = SDL_GetKeyFromScancode(scancode, SDL_KMOD_NONE, false);
	event.key.down = true;
	if (modifier_of(scancode) != SDL_KMOD_NONE)
		SDL_SetModState(SDL_GetModState() | modifier_of(scancode));
	event.key.mod = SDL_GetModState();
	SDL_PushEvent(&event);
	// Released a little later, so the game sees it held.
	SDL_AddTimer(hold, release_key, (void *)(intptr_t)scancode);
}

// Presses the key at next_test_key ("<n>:<key>"), returns the delay to the next one, or 0.
static Uint32 SDLCALL press_test_key(void *userdata, SDL_TimerID timer, Uint32 interval)
{
	(void)userdata, (void)timer, (void)interval;
	const char *colon = strchr(next_test_key, ':');
	if (colon == NULL)
		return 0;
	char name[32];
	const size_t length = strcspn(colon + 1, ",");
	snprintf(name, sizeof(name), "%.*s", (int)SDL_min(length, sizeof(name) - 1), colon + 1);
	press_key(name);
	const char *comma = strchr(colon, ',');
	if (comma == NULL)
		return 0;
	next_test_key = comma + 1;
	return (Uint32)SDL_max(strtol(next_test_key, NULL, 10), 1);
}

static void test_keys_on_frame(void)
{
	if (next_test_key == NULL)
	{
		const char *value = SDL_getenv("TYR3D_TEST_KEYS");
		if (value == NULL || (test_keys = SDL_strdup(value)) == NULL)
			return;
		next_test_key = test_keys;
	}
	if (next_test_key == test_keys && strtol(test_keys, NULL, 10) == frame)
	{
		const Uint32 delay = press_test_key(NULL, 0, 0);
		if (delay > 0)
			SDL_AddTimer(delay, press_test_key, NULL);
		else
			next_test_key = "";
	}
}

void dev_on_frame_presented(const Uint8 *rgba, int width, int height, int pitch)
{
	if (rgba != NULL && debug_flight_snapshot_wanted())
		debug_flight_snapshot(rgba, width, height, pitch);
	++frame;
	test_keys_on_frame();

	const char *dump_dir = SDL_getenv("TYR3D_DUMP_DIR");
	if (dump_dir != NULL && rgba != NULL)
	{
		SDL_SetAtomicInt(&key_pressed, 0);
		SDL_Surface *surface = SDL_CreateSurfaceFrom(width, height, SDL_PIXELFORMAT_RGBA32, (void *)rgba, pitch);
		if (surface != NULL)
		{
			char path[1024];
			snprintf(path, sizeof(path), "%s/frame_%06ld.bmp", dump_dir, frame);
			SDL_SaveBMP(surface, path);
			SDL_DestroySurface(surface);
			// To find what TYR3D_LOG_ENEMIES, TYR3D_LOG_CLIP, TYR3D_LOG_STANDINS and TYR3D_LOG_EVENTS report by 3D frame
			// (and where the ship is in the game).
			if (SDL_getenv("TYR3D_LOG_ENEMIES") != NULL || SDL_getenv("TYR3D_LOG_CLIP") != NULL ||
			    SDL_getenv("TYR3D_LOG_STANDINS") != NULL || SDL_getenv("TYR3D_LOG_EVENTS") != NULL)
				printf("dump: frame %ld is 3D frame %u, the ship at %d %d\n", frame, l3d_frame_number, player[0].x,
				       player[0].y);
			// TYR3D_LOG_OBJECTS: the objects of each dumped frame, to tell what a model on the screen is.
			if (SDL_getenv("TYR3D_LOG_OBJECTS") != NULL)
				for (int o = 0; o < l3d_frame.object_count; ++o)
				{
					const L3DObject *object = &l3d_frame.objects[o];
					printf("object: frame %ld %s look %c%u at %.0f,%.0f layer %d group %u:%u standin %u\n", frame,
					       object->model >= 0 && object->model < m3d_model_count ? m3d_models[object->model].name : "-",
					       object->enemy_sheet ? object->enemy_sheet : '-', object->enemy_sprite, object->x, object->y,
					       (int)object->layer, (unsigned)object->group, (unsigned)object->group_link, (unsigned)object->standin);
				}
		}
	}

	const long exit_after = env_long("TYR3D_EXIT_AFTER", 0);
	if (exit_after > 0 && frame >= exit_after)
	{
		printf("devtools: exiting after %ld frames\n", frame);
		exit(0);
	}
}
