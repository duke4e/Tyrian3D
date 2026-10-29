/*
 * Tyrian3D: the item icons rendered from the items' models, read and resized off the main thread. See model_icons.h.
 */
#include "model_icons.h"

#include <stdio.h>
#include <string.h>

// stb_image and stb_image_resize2 (public domain, in the renderer's raylib), this file's own copies.
#if defined(__clang__)
#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Wunused-function"
#pragma clang diagnostic ignored "-Wunused-parameter"
#pragma clang diagnostic ignored "-Wsign-compare"
#pragma clang diagnostic ignored "-Wimplicit-fallthrough"
#pragma clang diagnostic ignored "-Wunused-but-set-variable"
#elif defined(__GNUC__)
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wunused-function"
#pragma GCC diagnostic ignored "-Wunused-parameter"
#pragma GCC diagnostic ignored "-Wsign-compare"
#pragma GCC diagnostic ignored "-Wimplicit-fallthrough"
#pragma GCC diagnostic ignored "-Wunused-but-set-variable"
#pragma GCC diagnostic ignored "-Wmaybe-uninitialized"
#endif
#define STB_IMAGE_STATIC
#define STB_IMAGE_IMPLEMENTATION
#define STBI_ONLY_PNG
#define STBI_NO_LINEAR
#define STBI_NO_HDR
#include "stb_image.h"
#define STB_IMAGE_RESIZE_STATIC
#define STB_IMAGE_RESIZE_IMPLEMENTATION
#include "stb_image_resize2.h"
#if defined(__clang__)
#pragma clang diagnostic pop
#elif defined(__GNUC__)
#pragma GCC diagnostic pop
#endif

// The pictures asked for: queued, being made by the thread, made (taken by model_icon_take, which frees the slot).
#define JOBS 64
typedef enum { JOB_FREE, JOB_QUEUED, JOB_WORKING, JOB_DONE } JobState;
static struct
{
	JobState state;
	char path[1024];
	int size;
	Uint8 *pixels;  // (JOB_DONE: NULL if it couldn't be read)
} jobs[JOBS];
static SDL_Mutex *lock = NULL;
static SDL_Condition *wake = NULL;
static bool started = false, threaded = false;

// The picture as size x size pixels, premultiplied in its own (sRGB) values, as the canvas blends; or NULL.
static Uint8 *make_icon(const char *path, int size)
{
	int w, h, channels;
	stbi_uc *picture = stbi_load(path, &w, &h, &channels, 4);
	if (picture == NULL)
		return NULL;
	for (int i = 0; i < w * h; ++i)
	{
		stbi_uc *p = picture + i * 4;
		for (int c = 0; c < 3; ++c)
			p[c] = (stbi_uc)((p[c] * p[3] + 127) / 255);
	}
	Uint8 *out = SDL_malloc((size_t)size * size * 4);
	if (out != NULL && stbir_resize_uint8_linear(picture, w, h, 0, out, size, size, 0, STBIR_RGBA_PM) == NULL)
	{
		SDL_free(out);
		out = NULL;
	}
	stbi_image_free(picture);
	return out;
}

static int SDLCALL icon_thread(void *unused)
{
	(void)unused;
	SDL_LockMutex(lock);
	for (;;)
	{
		int job = -1;
		for (int i = 0; i < JOBS && job < 0; ++i)
			if (jobs[i].state == JOB_QUEUED)
				job = i;
		if (job < 0)
		{
			SDL_WaitCondition(wake, lock);
			continue;
		}
		jobs[job].state = JOB_WORKING;
		char path[sizeof(jobs[0].path)];
		SDL_strlcpy(path, jobs[job].path, sizeof(path));
		const int size = jobs[job].size;
		SDL_UnlockMutex(lock);
		Uint8 *pixels = make_icon(path, size);
		SDL_LockMutex(lock);
		jobs[job].pixels = pixels;
		jobs[job].state = JOB_DONE;
	}
	return 0;
}

static void start(void)
{
	started = true;
	lock = SDL_CreateMutex();
	wake = SDL_CreateCondition();
	SDL_Thread *thread = lock != NULL && wake != NULL ? SDL_CreateThread(icon_thread, "model icons", NULL) : NULL;
	threaded = thread != NULL;
	if (threaded)
		SDL_DetachThread(thread);
	else
		fprintf(stderr, "warning: model icons: no thread (%s), made as they are asked for\n", SDL_GetError());
}

bool model_icon_take(const char *path, int size, Uint8 **pixels)
{
	*pixels = NULL;
	if (path == NULL || size <= 0)
		return true;
	if (!started)
		start();
	if (!threaded)
	{
		*pixels = make_icon(path, size);
		return true;
	}
	SDL_LockMutex(lock);
	int free_job = -1;
	for (int i = 0; i < JOBS; ++i)
	{
		if (jobs[i].state == JOB_FREE)
		{
			if (free_job < 0)
				free_job = i;
			continue;
		}
		if (jobs[i].size != size || strcmp(jobs[i].path, path) != 0)
			continue;
		const bool done = jobs[i].state == JOB_DONE;
		if (done)
		{
			*pixels = jobs[i].pixels;
			jobs[i].pixels = NULL;
			jobs[i].state = JOB_FREE;
		}
		SDL_UnlockMutex(lock);
		return done;
	}
	if (free_job >= 0)
	{
		jobs[free_job].state = JOB_QUEUED;
		SDL_strlcpy(jobs[free_job].path, path, sizeof(jobs[free_job].path));
		jobs[free_job].size = size;
		jobs[free_job].pixels = NULL;
		SDL_SignalCondition(wake);
	}
	SDL_UnlockMutex(lock);
	return false;
}

bool model_icon_resample(const float *rgba, int w, int h, double x0, double y0, double x1, double y1, float *out, int size)
{
	STBIR_RESIZE resize;
	stbir_resize_init(&resize, rgba, w, h, 0, out, size, size, 0, STBIR_RGBA_PM, STBIR_TYPE_FLOAT);
	stbir_set_edgemodes(&resize, STBIR_EDGE_ZERO, STBIR_EDGE_ZERO);
	if (!stbir_set_input_subrect(&resize, x0 / w, y0 / h, x1 / w, y1 / h))
		return false;
	return stbir_resize_extended(&resize) != 0;
}
