/*
 * Tyrian3D: the data cubes and the story texts read aloud. See voiceover.h.
 */
#include "voiceover.h"

#include "loudness.h"
#include "paths3d.h"
#include "settings3d.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifndef TYR3D_VOICES_DIR
#define TYR3D_VOICES_DIR NULL
#endif

// A voice of the manifest: a cube's (episode, cube) or a story text's (episode 0, cube 0), by hash.
typedef struct
{
	int episode, cube;
	Uint32 hash;
	int duration_ms;
	char file[48];
} Voice;

static struct
{
	bool loaded;     // the manifest was looked for
	char dir[1024];
	Voice *voices;
	int count;
	bool debug;

	// What plays: the cube (episode, cube) or the story (by hash) whose voice was asked for last.
	bool on;
	int episode, cube;
	Uint32 hash;
	bool playing;    // a voice was started and has not ended
	char name[32];   // "cube 1:19", "story 1a2b3c4d" (the log's)
} vo;

Uint32 voiceover_hash(Uint32 hash, const char *line)
{
	for (const unsigned char *c = (const unsigned char *)line; *c != '\0'; ++c)
		hash = (hash ^ *c) * 16777619u;
	return (hash ^ '\n') * 16777619u;
}

// The manifest (manifest.txt, written by tools/voices/generate.py):
//   cube <episode> <cube> <hash> <duration_ms> <file> [line times...]
//   story <hash> <duration_ms> <file>
static void load_manifest(void)
{
	if (vo.loaded)
		return;
	vo.loaded = true;
	vo.debug = SDL_getenv("TYR3D_DEBUG_VOICES") != NULL;

	char buffer[1024];
	SDL_strlcpy(vo.dir, tyr3d_resource_dir("TYR3D_VOICES_DIR", TYR3D_VOICES_DIR, "voices", buffer, sizeof(buffer)), sizeof(vo.dir));
	char path[1100];
	snprintf(path, sizeof(path), "%s/manifest.txt", vo.dir);
	FILE *f = fopen(path, "r");
	if (f == NULL)
	{
		if (vo.debug)
			printf("voices: no manifest (%s): no voices\n", path);
		return;
	}

	int capacity = 0, cubes = 0, stories = 0;
	char line[4096];
	while (fgets(line, sizeof(line), f) != NULL)
	{
		Voice v = { 0 };
		unsigned int hash = 0;
		if (SDL_strncmp(line, "cube ", 5) == 0)
		{
			if (sscanf(line + 5, "%d %d %x %d %47s", &v.episode, &v.cube, &hash, &v.duration_ms, v.file) != 5 || v.cube <= 0)
				continue;
			++cubes;
		}
		else if (SDL_strncmp(line, "story ", 6) == 0)
		{
			if (sscanf(line + 6, "%x %d %47s", &hash, &v.duration_ms, v.file) != 3)
				continue;
			++stories;
		}
		else
		{
			continue;
		}
		v.hash = hash;
		if (vo.count == capacity)
		{
			capacity = capacity == 0 ? 256 : capacity * 2;
			Voice *grown = SDL_realloc(vo.voices, (size_t)capacity * sizeof(*grown));
			if (grown == NULL)
				break;
			vo.voices = grown;
		}
		vo.voices[vo.count++] = v;
	}
	fclose(f);

	if (vo.debug)
		printf("voices: %d cubes and %d story texts in %s\n", cubes, stories, path);
}

bool voiceover_installed(void)
{
	load_manifest();
	return vo.count > 0;
}

static const Voice *find_cube(int episode, int cube)
{
	for (int i = 0; i < vo.count; ++i)
		if (vo.voices[i].cube == cube && vo.voices[i].episode == episode)
			return &vo.voices[i];
	return NULL;
}

static const Voice *find_story(Uint32 hash)
{
	for (int i = 0; i < vo.count; ++i)
		if (vo.voices[i].cube == 0 && vo.voices[i].hash == hash)
			return &vo.voices[i];
	return NULL;
}

static void free_done(Sint16 *done[2], int n)
{
	for (int i = 0; i < n; ++i)
		SDL_free(done[i]);
}

// Starts v's file (NULL: stops what plays).
static void start(const Voice *v)
{
	Sint16 *samples = NULL;
	size_t count = 0;
	if (v != NULL && !audio_disabled && audioSampleRate > 0)
	{
		const Uint64 t0 = SDL_GetTicksNS();
		char path[1100];
		snprintf(path, sizeof(path), "%s/%s", vo.dir, v->file);
		SDL_AudioSpec spec;
		Uint8 *wav = NULL;
		Uint32 length = 0;
		if (SDL_LoadWAV(path, &spec, &wav, &length))
		{
			const SDL_AudioSpec dst = { .format = SDL_AUDIO_S16, .channels = 1, .freq = audioSampleRate };
			Uint8 *converted = NULL;
			int size = 0;
			if (SDL_ConvertAudioSamples(&spec, wav, (int)length, &dst, &converted, &size))
			{
				samples = (Sint16 *)converted;
				count = (size_t)size / sizeof(Sint16);
			}
			SDL_free(wav);
		}
		if (vo.debug)
		{
			if (samples != NULL)
				printf("voices: play %s (%s, %.1f s, loaded in %.0f ms)\n", vo.name, v->file, count / (double)audioSampleRate,
				       (SDL_GetTicksNS() - t0) / 1e6);
			else
				printf("voices: %s: cannot play %s: %s\n", vo.name, path, SDL_GetError());
		}
	}

	Sint16 *done[2];
	free_done(done, voice_channel_play(samples, count, done));
	if (samples != NULL)
		voice_channel_volume((Uint8)SDL_clamp(settings3d.voice_volume, 0, 255));
	vo.playing = samples != NULL;
}

void voiceover_update(void)
{
	if (!vo.playing)
		return;
	Sint16 *done[2];
	bool playing;
	free_done(done, voice_channel_collect(done, &playing));
	if (!playing)
	{
		vo.playing = false;
		if (vo.debug)
			printf("voices: %s ended\n", vo.name);
	}
}

void voiceover_stop(void)
{
	if (vo.on && vo.debug && vo.playing)
		printf("voices: stop %s\n", vo.name);
	vo.on = false;
	vo.episode = vo.cube = 0;
	vo.hash = 0;
	if (vo.playing)
		start(NULL);
	// (what has faded out is freed by the next voice or update)
	Sint16 *done[2];
	bool playing;
	free_done(done, voice_channel_collect(done, &playing));
}

void voiceover_cube(int episode, int cube, Uint32 text_hash)
{
	if (cube <= 0)
	{
		if (vo.on)
			voiceover_stop();
		voiceover_update();
		return;
	}
	if (vo.on && vo.cube == cube && vo.episode == episode && vo.hash == text_hash)
	{
		voiceover_update();
		return;
	}

	voiceover_stop();
	vo.on = true;
	vo.episode = episode;
	vo.cube = cube;
	vo.hash = text_hash;
	snprintf(vo.name, sizeof(vo.name), "cube %d:%d", episode, cube);
	if (!settings3d.voices || !voiceover_installed())
		return;
	const Voice *v = find_cube(episode, cube);
	if (v == NULL || v->hash != text_hash)
	{
		if (vo.debug)
			printf("voices: %s: %s\n", vo.name, v == NULL ? "no voice" : "its text differs from the voice's (not played)");
		return;
	}
	start(v);
}

void voiceover_story(char (*lines)[61], int first, int count)
{
	// (Each row as far as its 61 bytes: a longer line, copied whole, runs on into the next row.)
	Uint32 hash = VOICEOVER_HASH_START;
	for (int i = first; i < count; ++i)
	{
		char row[62];
		memcpy(row, lines[i], 61);
		row[61] = '\0';
		hash = voiceover_hash(hash, row);
	}

	voiceover_stop();
	vo.on = true;
	vo.hash = hash;
	snprintf(vo.name, sizeof(vo.name), "story %08x", (unsigned int)hash);
	if (!settings3d.voices || !voiceover_installed())
		return;
	const Voice *v = find_story(hash);
	if (v == NULL)
	{
		if (vo.debug)
			printf("voices: %s: no voice (\"%.40s\")\n", vo.name, first < count ? lines[first] : "");
		return;
	}
	start(v);
}

void voiceover_settings_changed(void)
{
	if (!settings3d.voices)
	{
		if (vo.playing)
		{
			if (vo.debug)
				printf("voices: off: stop %s\n", vo.name);
			start(NULL);
		}
		return;
	}
	voice_channel_volume((Uint8)SDL_clamp(settings3d.voice_volume, 0, 255));
}
