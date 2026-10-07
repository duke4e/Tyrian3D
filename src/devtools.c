/*
 * Tyrian3D developer tooling: environment-driven helpers for automated testing.
 */
#include "devtools.h"

#include "config.h"
#include "episodes.h"
#include "layer3d.h"
#include "palette.h"
#include "params.h"
#include "player.h"
#include "varz.h"

#include <SDL3/SDL.h>

#include <stdio.h>
#include <stdlib.h>

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
	return SDL_getenv("TYR3D_DUMP_DIR") != NULL && dump_every > 0 && (frame + 1) % dump_every == 0;
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

	// As newGame() does for a one-player full game.
	onePlayerAction = false;
	twoPlayerMode = false;
	timedBattleMode = false;
	JE_initEpisode((JE_byte)episode);
	initial_episode_num = episodeNum;
	difficultyLevel = DIFFICULTY_NORMAL;
	initialDifficulty = difficultyLevel;
	player[0].cash = 10000;

	constantPlay = true;  // skip shops: they jump straight to the next level
	mainLevel = (JE_byte)section;
	gameLoaded = true;

	printf("devtools: starting episode %d at section %d\n", episode, section);
	return true;
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
	// Weave across the playfield with a slow vertical drift; always fire.
	const double t = SDL_GetTicks() / 1000.0;
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

void dev_on_frame_presented(const Uint8 *rgba, int width, int height, int pitch)
{
	++frame;

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
		}
	}

	const long exit_after = env_long("TYR3D_EXIT_AFTER", 0);
	if (exit_after > 0 && frame >= exit_after)
	{
		printf("devtools: exiting after %ld frames\n", frame);
		exit(0);
	}
}
