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
	bool paused;
	char name[32];   // "cube 1:19", "story 1a2b3c4d" (the log's)

	// The store's cubes (voiceover_player_cubes) and the one the player plays (-1: none).
	int player_episode, player_count, player_index;
	int player_cubes[VOICEOVER_PLAYER_CUBES];
	Uint32 player_hashes[VOICEOVER_PLAYER_CUBES];
	char player_titles[VOICEOVER_PLAYER_CUBES][48];
	bool autoplay;   // the store's cubes were started one after another for this visit (settings3d.cube_autoplay)

	// Cubes picked up in a level (voiceover_cube_found) and read there, which the store's autoplay passes over, and the
	// one waiting for the game's "Data acquired" to be said (pending_at: SDL_GetTicks, 0: none).
	int heard_episode[VOICEOVER_PLAYER_CUBES], heard_cube[VOICEOVER_PLAYER_CUBES], heard_count;
	int pending_episode, pending_cube;
	Uint32 pending_hash;
	Uint64 pending_at;
} vo = { .player_index = -1 };

#define CUBE_FOUND_DELAY_MS 1300  // the game's "Data acquired." (V_DATA_CUBE) said first

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
	vo.paused = false;
}

static void autoplay_next(void);
static void cube_start(int episode, int cube, Uint32 text_hash);

void voiceover_update(void)
{
	if (vo.pending_at != 0 && SDL_GetTicks() >= vo.pending_at)
	{
		vo.pending_at = 0;
		cube_start(vo.pending_episode, vo.pending_cube, vo.pending_hash);
		return;
	}
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
		autoplay_next();
	}
}

void voiceover_stop(void)
{
	if (vo.on && vo.debug && vo.playing)
		printf("voices: stop %s\n", vo.name);
	vo.on = false;
	vo.episode = vo.cube = 0;
	vo.hash = 0;
	vo.player_index = -1;
	vo.pending_at = 0;
	vo.paused = false;
	if (vo.playing)
		start(NULL);
	// (what has faded out is freed by the next voice or update)
	Sint16 *done[2];
	bool playing;
	free_done(done, voice_channel_collect(done, &playing));
}

// The cube the store's reader asked for last (asked again each frame while it is open).
static int reader_episode, reader_cube;
static Uint32 reader_hash;

void voiceover_cube_found(int episode, int cube, Uint32 text_hash)
{
	if (cube <= 0 || !settings3d.voices || !voiceover_installed())
		return;
	if (vo.heard_count < VOICEOVER_PLAYER_CUBES)
	{
		vo.heard_episode[vo.heard_count] = episode;
		vo.heard_cube[vo.heard_count] = cube;
		++vo.heard_count;
	}
	vo.pending_episode = episode;
	vo.pending_cube = cube;
	vo.pending_hash = text_hash;
	vo.pending_at = SDL_GetTicks() + CUBE_FOUND_DELAY_MS;
	if (vo.debug)
		printf("voices: cube %d:%d picked up\n", episode, cube);
}

static bool heard(int episode, int cube)
{
	for (int i = 0; i < vo.heard_count; ++i)
		if (vo.heard_episode[i] == episode && vo.heard_cube[i] == cube)
			return true;
	return false;
}

void voiceover_cube(int episode, int cube, Uint32 text_hash)
{
	if (cube <= 0)  // (no reader open: a cube read goes on playing, the player's)
	{
		reader_cube = 0;
		voiceover_update();
		return;
	}
	if (cube == reader_cube && episode == reader_episode && text_hash == reader_hash)
	{
		voiceover_update();  // (what the player has chosen since plays on)
		return;
	}
	reader_episode = episode;
	reader_cube = cube;
	reader_hash = text_hash;
	cube_start(episode, cube, text_hash);
}

static void cube_start(int episode, int cube, Uint32 text_hash)
{
	if (vo.on && vo.cube == cube && vo.episode == episode && vo.hash == text_hash && vo.playing)
	{
		voiceover_update();
		return;
	}

	voiceover_stop();
	vo.on = true;
	vo.episode = episode;
	vo.cube = cube;
	vo.hash = text_hash;
	for (int i = 0; i < vo.player_count; ++i)
		if (vo.player_cubes[i] == cube && vo.player_episode == episode)
			vo.player_index = i;
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

static void autoplay_from(int i);

void voiceover_player_cubes(int episode, int count, const int *cubes, const Uint32 *hashes, const char *const *titles)
{
	vo.player_episode = episode;
	vo.player_count = SDL_clamp(count, 0, VOICEOVER_PLAYER_CUBES);
	for (int i = 0; i < vo.player_count; ++i)
	{
		vo.player_cubes[i] = cubes[i];
		vo.player_hashes[i] = hashes[i];
		SDL_strlcpy(vo.player_titles[i], titles[i], sizeof(vo.player_titles[i]));
	}
	if (vo.player_index >= vo.player_count)
		vo.player_index = -1;

	// Autoplay: as the store opens, its cubes are read one after another (settings3d.cube_autoplay).
	if (!vo.autoplay && vo.player_count > 0 && settings3d.cube_autoplay && settings3d.voices && voiceover_installed() &&
	    !vo.playing && reader_cube == 0)
	{
		vo.autoplay = true;
		if (vo.debug)
			printf("voices: autoplay the store's %d cubes\n", vo.player_count);
		autoplay_from(0);
	}
}

void voiceover_store_closed(void)
{
	voiceover_stop();
	vo.autoplay = false;
	vo.heard_count = 0;
}

// Plays the store's cube i (as its reader would).
static void player_play(int i)
{
	if (i < 0 || i >= vo.player_count)
		return;
	cube_start(vo.player_episode, vo.player_cubes[i], vo.player_hashes[i]);
	vo.player_index = i;
}

// Autoplay: the store's cubes from i on, the first one that has a voice (and wasn't read as it was picked up).
static void autoplay_from(int i)
{
	for (; i < vo.player_count; ++i)
	{
		if (heard(vo.player_episode, vo.player_cubes[i]))
			continue;
		player_play(i);
		if (vo.playing)
			return;
	}
}

// Autoplay: the store's next cube once one ends, unless the player is reading a cube (its reader open) or
// autoplay is off.
static void autoplay_next(void)
{
	if (vo.autoplay && settings3d.cube_autoplay && settings3d.voices && reader_cube == 0 && vo.player_index >= 0)
		autoplay_from(vo.player_index + 1);
}

void voiceover_player_toggle(void)
{
	if (vo.playing && vo.player_index >= 0)
	{
		vo.paused = !vo.paused;
		voice_channel_pause(vo.paused);
		if (vo.debug)
			printf("voices: %s %s\n", vo.paused ? "pause" : "resume", vo.name);
		return;
	}
	player_play(vo.player_index >= 0 ? vo.player_index : 0);
}

void voiceover_player_step(int step)
{
	if (vo.player_count == 0)
		return;
	const int from = vo.player_index >= 0 ? vo.player_index : (step > 0 ? -1 : 0);
	player_play(((from + step) % vo.player_count + vo.player_count) % vo.player_count);
}

bool voiceover_player_state(int *index, int *count, bool *paused, float *progress, const char **title)
{
	*count = vo.player_count;
	*index = vo.playing ? vo.player_index : -1;
	*paused = vo.paused;
	*progress = vo.playing ? voice_channel_progress() : 0.0f;
	*title = *index >= 0 ? vo.player_titles[*index] : "";
	return vo.player_count > 0 && settings3d.voices && voiceover_installed();
}
