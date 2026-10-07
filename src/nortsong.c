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
#include "nortsong.h"

#include "file.h"
#include "joystick.h"
#include "keyboard.h"
#include "loudness.h"
#include "musmast.h"
#include "opentyr.h"
#include "params.h"
#include "sndmast.h"
#include "vga256d.h"

#include <SDL3/SDL.h>

JE_word frameCountMax;

Sint16 *soundSamples[SOUND_COUNT] = { NULL }; /* [1..soundnum + 9] */  // FKA digiFx
size_t soundSampleCount[SOUND_COUNT] = { 0 }; /* [1..soundnum + 9] */  // FKA fxSize

JE_word tyrMusicVolume, fxVolume;
const JE_word fxPlayVol = 4;
JE_word tempVolume;

// The period of the x86 programmable interval timer in milliseconds.
static const float pitPeriod = (12.0f / 14318180.0f) * 1000.0f;

static Uint16 delaySpeed = 0x4300;
static float delayPeriod = 0x4300 * ((12.0f / 14318180.0f) * 1000.0f);

static Uint32 target = 0;
static Uint32 target2 = 0;

void setDelay(int delay)  // FKA NortSong.frameCount
{
	target = SDL_GetTicks() + delay * delayPeriod;
}

void setDelay2(int delay)  // FKA NortSong.frameCount2
{
	target2 = SDL_GetTicks() + delay * delayPeriod;
}

Uint32 getDelayTicks(void)  // FKA NortSong.frameCount
{
	Sint32 delay = target - SDL_GetTicks();
	return MAX(0, delay);
}

Uint32 getDelayTicks2(void)  // FKA NortSong.frameCount2
{
	Sint32 delay = target2 - SDL_GetTicks();
	return MAX(0, delay);
}

void wait_delay(void)
{
	Sint32 delay = target - SDL_GetTicks();
	if (delay > 0)
		SDL_Delay(delay);
}

void service_wait_delay(void)
{
	for (; ; )
	{
		service_SDL_events(false);

		Sint32 delay = target - SDL_GetTicks();
		if (delay <= 0)
			return;

		SDL_Delay(MIN(delay, SDL_POLL_INTERVAL));
	}
}

void wait_delayorinput(void)
{
	for (; ; )
	{
		service_SDL_events(false);
		poll_joysticks();

		if (newkey || mousedown || joydown)
		{
			newkey = false;
			return;
		}

		Sint32 delay = target - SDL_GetTicks();
		if (delay <= 0)
			return;

		SDL_Delay(MIN(delay, SDL_POLL_INTERVAL));
	}
}

// Tyrian3D: sound effects as WAV files, named "<number>_<title>.wav". TYR3D_EXPORT_SFX=<dir> writes
// the samples as the game's files have them (8-bit, 11025 Hz, as 16-bit WAV); WAV files of the same
// names in a "sfx" directory beside the game's data (upscaled ones, plan M10) replace them, unless
// TYR3D_ORIGINAL_SFX is set.
static void sfx_file_name(size_t i, char *out, size_t size)
{
	char title[sizeof(soundTitle[0]) + 1];
	size_t n = 0;
	for (size_t k = 0; k < sizeof(soundTitle[0]) && soundTitle[i][k] != '\0'; ++k)
		if (SDL_isalnum((unsigned char)soundTitle[i][k]))
			title[n++] = (char)SDL_tolower((unsigned char)soundTitle[i][k]);
	title[n] = '\0';
	snprintf(out, size, "%02u_%s.wav", (unsigned int)(i + 1), title);
}

static void export_sfx(const char *dir, size_t i, const Sint8 *samples, size_t count)
{
	char name[64], path[1024];
	sfx_file_name(i, name, sizeof(name));
	snprintf(path, sizeof(path), "%s/%s", dir, name);
	FILE *f = fopen(path, "wb");
	if (f == NULL)
		return;
	const Uint32 rate = 11025, bytes = (Uint32)count * 2;
	const Uint8 header[44] = {
		'R', 'I', 'F', 'F', (Uint8)(36 + bytes), (Uint8)((36 + bytes) >> 8), (Uint8)((36 + bytes) >> 16), (Uint8)((36 + bytes) >> 24),
		'W', 'A', 'V', 'E', 'f', 'm', 't', ' ', 16, 0, 0, 0, 1, 0, 1, 0,
		(Uint8)rate, (Uint8)(rate >> 8), 0, 0, (Uint8)(rate * 2), (Uint8)((rate * 2) >> 8), 0, 0, 2, 0, 16, 0,
		'd', 'a', 't', 'a', (Uint8)bytes, (Uint8)(bytes >> 8), (Uint8)(bytes >> 16), (Uint8)(bytes >> 24),
	};
	fwrite(header, 1, sizeof(header), f);
	for (size_t k = 0; k < count; ++k)
	{
		const Sint16 v = (Sint16)(samples[k] * 256);
		const Uint8 le[2] = { (Uint8)v, (Uint8)((Uint16)v >> 8) };
		fwrite(le, 1, 2, f);
	}
	fclose(f);
}

// A replacement for sound i from the "sfx" directory, converted to dstSpec; NULL if there is none.
static Uint8 *load_sfx_replacement(size_t i, const SDL_AudioSpec *dstSpec, int *size)
{
	if (SDL_getenv("TYR3D_ORIGINAL_SFX") != NULL)
		return NULL;
	char name[64], path[1024];
	sfx_file_name(i, name, sizeof(name));
	snprintf(path, sizeof(path), "%s/sfx/%s", data_dir(), name);
	SDL_AudioSpec spec;
	Uint8 *wav = NULL;
	Uint32 length = 0;
	if (!SDL_LoadWAV(path, &spec, &wav, &length))
		return NULL;
	Uint8 *converted = NULL;
	if (!SDL_ConvertAudioSamples(&spec, wav, (int)length, dstSpec, &converted, size))
		converted = NULL;
	SDL_free(wav);
	return converted;
}

void loadSndFile(bool xmas)
{
	FILE *f;

	f = dir_fopen_die(data_dir(), "tyrian.snd", "rb");

	Uint16 sfxCount;
	Uint32 sfxPositions[SFX_COUNT + 1];

	// Read number of sounds.
	fread_u16_die(&sfxCount, 1, f);
	if (sfxCount != SFX_COUNT)
		goto die;

	// Read positions of sounds.
	fread_u32_die(sfxPositions, sfxCount, f);

	// Determine end of last sound.
	fseek(f, 0, SEEK_END);
	sfxPositions[sfxCount] = ftell(f);

	// Read samples.
	for (size_t i = 0; i < sfxCount; ++i)
	{
		soundSampleCount[i] = sfxPositions[i + 1] - sfxPositions[i];

		// Sound size cannot exceed 64 KiB.
		if (soundSampleCount[i] > UINT16_MAX)
			goto die;

		free(soundSamples[i]);
		soundSamples[i] = malloc(soundSampleCount[i]);

		fseek(f, sfxPositions[i], SEEK_SET);
		fread_u8_die((Uint8 *)soundSamples[i], soundSampleCount[i], f);
	}

	fclose(f);

	f = dir_fopen_die(data_dir(), xmas ? "voicesc.snd" : "voices.snd", "rb");

	Uint16 voiceCount;
	Uint32 voicePositions[VOICE_COUNT + 1];

	// Read number of sounds.
	fread_u16_die(&voiceCount, 1, f);
	if (voiceCount != VOICE_COUNT)
		goto die;

	// Read positions of sounds.
	fread_u32_die(voicePositions, voiceCount, f);

	// Determine end of last sound.
	fseek(f, 0, SEEK_END);
	voicePositions[voiceCount] = ftell(f);

	for (size_t vi = 0; vi < voiceCount; ++vi)
	{
		size_t i = SFX_COUNT + vi;

		soundSampleCount[i] = voicePositions[vi + 1] - voicePositions[vi];

		// Voice sounds have some bad data at the end.
		soundSampleCount[i] = soundSampleCount[i] >= 100
			? soundSampleCount[i] - 100
			: 0;

		// Sound size cannot exceed 64 KiB.
		if (soundSampleCount[i] > UINT16_MAX)
			goto die;

		free(soundSamples[i]);
		soundSamples[i] = malloc(soundSampleCount[i]);

		fseek(f, voicePositions[vi], SEEK_SET);
		fread_u8_die((Uint8 *)soundSamples[i], soundSampleCount[i], f);
	}

	fclose(f);

	// Convert samples to output sample format and rate.

	const SDL_AudioSpec srcSpec = { .format = SDL_AUDIO_S8, .channels = 1, .freq = 11025 };
	const SDL_AudioSpec dstSpec = { .format = SDL_AUDIO_S16, .channels = 1, .freq = audioSampleRate };

	const char *export_dir = SDL_getenv("TYR3D_EXPORT_SFX");
	int replaced = 0;

	for (size_t i = 0; i < SOUND_COUNT; ++i)
	{
		Uint8 *converted = NULL;
		int convertedSize = 0;

		if (export_dir != NULL)
			export_sfx(export_dir, i, (const Sint8 *)soundSamples[i], soundSampleCount[i]);

		if ((converted = load_sfx_replacement(i, &dstSpec, &convertedSize)) != NULL)
			++replaced;
		else if (!SDL_ConvertAudioSamples(&srcSpec, (const Uint8 *)soundSamples[i], (int)soundSampleCount[i], &dstSpec, &converted, &convertedSize))
		{
			fprintf(stderr, "error: Failed to convert audio: %s\n", SDL_GetError());

			soundSampleCount[i] = 0;

			continue;
		}

		free(soundSamples[i]);
		soundSamples[i] = malloc(convertedSize);

		memcpy(soundSamples[i], converted, convertedSize);
		soundSampleCount[i] = convertedSize / sizeof (Sint16);

		SDL_free(converted);
	}
	if (export_dir != NULL)
		printf("sfx: wrote %d sounds to %s\n", SOUND_COUNT, export_dir);
	if (replaced > 0)
		printf("sfx: %d of %d sounds from %s/sfx\n", replaced, SOUND_COUNT, data_dir());

	return;

die:
	fprintf(stderr, "error: Unexpected data was read from a file.\n");
	SDL_Quit();
	exit(EXIT_FAILURE);
}

void JE_playSampleNum(JE_byte samplenum)
{
	multiSamplePlay(soundSamples[samplenum-1], soundSampleCount[samplenum-1], 0, fxPlayVol);
}

void setDelaySpeed(Uint16 speed)  // FKA NortSong.speed and NortSong.setTimerInt
{
	delaySpeed = speed;
	delayPeriod = speed * pitPeriod;
}

void JE_changeVolume(JE_word *music, int music_delta, JE_word *sample, int sample_delta)
{
	int music_temp = *music + music_delta,
	    sample_temp = *sample + sample_delta;
	
	if (music_delta)
	{
		if (music_temp > 255)
		{
			music_temp = 255;
			JE_playSampleNum(S_CLINK);
		}
		else if (music_temp < 0)
		{
			music_temp = 0;
			JE_playSampleNum(S_CLINK);
		}
	}
	
	if (sample_delta)
	{
		if (sample_temp > 255)
		{
			sample_temp = 255;
			JE_playSampleNum(S_CLINK);
		}
		else if (sample_temp < 0)
		{
			sample_temp = 0;
			JE_playSampleNum(S_CLINK);
		}
	}
	
	*music = music_temp;
	*sample = sample_temp;
	
	set_volume(*music, *sample);
}
