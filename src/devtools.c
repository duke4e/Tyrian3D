/*
 * Tyrian3D developer tooling: environment-driven helpers for automated testing.
 */
#include "devtools.h"

#include "layer3d.h"
#include "palette.h"

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
