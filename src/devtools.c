/*
 * Tyrian3D developer tooling: environment-driven helpers for automated testing.
 */
#include "devtools.h"

#include "config.h"
#include "episodes.h"
#include "layer3d.h"
#include "mtrand.h"
#include "palette.h"
#include "params.h"
#include "player.h"
#include "varz.h"

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

static bool dumping_this_frame(void)
{
	const long dump_every = env_long("TYR3D_DUMP_EVERY", 60);
	return SDL_getenv("TYR3D_DUMP_DIR") != NULL && dump_every > 0 && (frame + 1) % dump_every == 0 &&
	       frame + 1 >= env_long("TYR3D_DUMP_FROM", 0);
}

bool dev_capture_next_frame(void)
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
	if (sscanf(start, "%d:%d", &episode, &section) != 2 || episode < 1 || episode > EPISODE_MAX ||
	    section < 1 || section > 255)
	{
		fprintf(stderr, "warning: TYR3D_START must be <episode>:<section>, got '%s'\n", start);
		return false;
	}

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

	// "<front>,<rear>[,<power>]": the weapons, ids as in the shop's weapon ports, and their power (1-11).
	const char *weapons = SDL_getenv("TYR3D_WEAPONS");
	int front = 0, rear = 0, power = 1;
	if (weapons != NULL && sscanf(weapons, "%d,%d,%d", &front, &rear, &power) >= 1)
	{
		player[0].items.weapon[FRONT_WEAPON].id = (JE_byte)SDL_clamp(front, 0, PORT_NUM);
		player[0].items.weapon[REAR_WEAPON].id = (JE_byte)SDL_clamp(rear, 0, PORT_NUM);
		player[0].items.weapon[FRONT_WEAPON].power = player[0].items.weapon[REAR_WEAPON].power = (JE_byte)SDL_clamp(power, 1, 11);
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
		fprintf(stderr, "warning: TYR3D_MODE must be full, arcade, two, galaga, timed:<1-2> or super:<1-%d>\n",
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

bool dev_background_run(void)
{
	return SDL_getenv("TYR3D_WINDOWED") != NULL;
}

bool dev_godmode(void)
{
	return SDL_getenv("TYR3D_GODMODE") != NULL;
}

bool dev_autopilot(void)
{
	return SDL_getenv("TYR3D_AUTOPILOT") != NULL;
}

void dev_autopilot_steer(int x, int y, int speed, int *dx, int *dy, bool *fire)
{
	// Weave across the playfield with a slow vertical drift; always fire. Timed by frames, so runs
	// started with TYR3D_START repeat exactly (see dev_start_game).
	const double t = frame / 35.0;
	const int target_x = 140 + (int)(100 * SDL_sin(t * 0.9));
	const int target_y = 140 + (int)(25 * SDL_sin(t * 0.37));

	if (x < target_x - speed)
		*dx += speed;
	else if (x > target_x + speed)
		*dx -= speed;
	if (y < target_y - speed)
		*dy += speed;
	else if (y > target_y + speed)
		*dy -= speed;

	*fire = true;
}

/*
 * TYR3D_TEST_KEYS=<frame>:<key>[,<ms>:<key>...]: presses a key (an SDL scancode name: P, Escape,
 * Return, Down...) when that frame is presented, then each next one so many milliseconds after the
 * one before (menus wait for keys without presenting frames).
 */
static char test_keys[256];
static const char *next_test_key = NULL;

static Uint32 SDLCALL release_key(void *userdata, SDL_TimerID timer, Uint32 interval)
{
	(void)timer, (void)interval;
	SDL_Event event = { 0 };
	event.type = SDL_EVENT_KEY_UP;
	event.key.scancode = (SDL_Scancode)(intptr_t)userdata;
	event.key.key = SDL_GetKeyFromScancode(event.key.scancode, SDL_KMOD_NONE, false);
	SDL_PushEvent(&event);
	return 0;
}

static void press_key(const char *name)
{
	const SDL_Scancode scancode = SDL_GetScancodeFromName(name);
	if (scancode == SDL_SCANCODE_UNKNOWN)
	{
		fprintf(stderr, "devtools: no key %s\n", name);
		return;
	}
	printf("devtools: pressing %s\n", name);
	SDL_Event event = { 0 };
	event.type = SDL_EVENT_KEY_DOWN;
	event.key.scancode = scancode;
	event.key.key = SDL_GetKeyFromScancode(scancode, SDL_KMOD_NONE, false);
	event.key.down = true;
	SDL_PushEvent(&event);
	// Released a little later, so the game sees it held.
	SDL_AddTimer(100, release_key, (void *)(intptr_t)scancode);
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
		if (value == NULL)
			return;
		snprintf(test_keys, sizeof(test_keys), "%s", value);
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
	++frame;
	test_keys_on_frame();

	const char *dump_dir = SDL_getenv("TYR3D_DUMP_DIR");
	if (dump_dir != NULL && rgba != NULL)
	{
		SDL_Surface *surface = SDL_CreateSurfaceFrom(width, height, SDL_PIXELFORMAT_RGBA32, (void *)rgba, pitch);
		if (surface != NULL)
		{
			char path[1024];
			snprintf(path, sizeof(path), "%s/frame_%06ld.bmp", dump_dir, frame);
			SDL_SaveBMP(surface, path);
			SDL_DestroySurface(surface);
			// To find what TYR3D_LOG_ENEMIES reports by 3D frame.
			if (SDL_getenv("TYR3D_LOG_ENEMIES") != NULL)
				printf("dump: frame %ld is 3D frame %u\n", frame, l3d_frame_number);
		}
	}

	const long exit_after = env_long("TYR3D_EXIT_AFTER", 0);
	if (exit_after > 0 && frame >= exit_after)
	{
		printf("devtools: exiting after %ld frames\n", frame);
		exit(0);
	}
}
