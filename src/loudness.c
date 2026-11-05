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
#include "loudness.h"

#include "file.h"
#include "lds_play.h"
#include "music_midi.h"
#include "musicviz.h"
#include "opl.h"
#include "nortsong.h"
#include "opentyr.h"
#include "params.h"

#include <assert.h>
#include <stdlib.h>
#include <string.h>

#define OUTPUT_QUALITY 4  // 44.1 kHz

int audioSampleRate = 0;

bool music_stopped = true;
unsigned int song_playing = 0;

bool audio_disabled = false, music_disabled = false, samples_disabled = false;

static SDL_AudioStream *audioStream = NULL;

static Uint8 musicVolume = 255;
static Uint8 sampleVolume = 255;

// Tyrian3D: audio_hold's: held, and the song asked for meanwhile (-1: none).
static bool held = false;
static int held_song = -1;

static const float volumeRange = 30.0f;  // dB

// Fixed point Q20.12; needs to be able to store (10 * INT16_MIN/MAX)
static Sint32 volumeFactorTable[256];
#define TO_FIXED(x) ((Sint32)((x) * (1 << 12)))
#define FIXED_TO_INT(x) ((Sint32)((x) >> 12))

// Twice the Loudness update rate (in updates/second).  In Tyrian, Loudness
// updates were performed at the same rate as the game timer, which varied
// depending on the game speed (~69.57 Hz at most game speeds).  We don't have
// the same limitations, so we'll keep the update rate constant, but we do want
// to stick to integer math, so we'll update at 69.5 Hz.
static const int ldsUpdate2Rate = 139;  // 69.5 * 2

static int samplesPerLdsUpdate;
static int samplesPerLdsUpdateFrac;

static int samplesUntilLdsUpdate = 0;
static int samplesUntilLdsUpdateFrac = 0;

static FILE *music_file = NULL;
static Uint32 *song_offset;
static Uint16 song_count = 0;

#define CHANNEL_COUNT 8
static const Sint16 *channelSamples[CHANNEL_COUNT];
static size_t channelSampleCount[CHANNEL_COUNT] = { 0 };
static Uint8 channelVolume[CHANNEL_COUNT];
#define CHANNEL_VOLUME_LEVELS 8

// Tyrian3D: the voice channel (voiceover.h): the voice playing and the one fading out after it was
// replaced or stopped (~30 ms), mixed over the rest; the music and the sounds ducked (~6 dB, ~200 ms ramps)
// while a voice speaks. The buffers belong to voiceover.c, which frees them once the mixer is done.
typedef struct
{
	Sint16 *samples;
	size_t count, pos;
	int fade_left;  // the fading voice's samples to go
} VoiceSlot;
static VoiceSlot voiceCurrent, voiceFading;
static bool voicePaused = false;  // the current voice held where it is (the store's cube player)
static Uint8 voiceVolume = 255;
static int voiceFadeSamples = 1323;
#define VOICE_DUCK_ONE (1 << 16)  // Q16 gain on the music
static Sint32 voiceDuck = VOICE_DUCK_ONE, voiceDuckLow = 32845, voiceDuckStep = 4;  // (-6 dB)

// Tyrian3D: a recorded song (play_recorded_song: episode 7's GBC songs, tools/gbc/music.py) in place of the Loudness
// music: mono samples at the output's rate, from its loop's start again at its end, or, while the music plays as MIDI,
// its MIDI file through the SoundFont (music_midi_song_*); faded out by fade_song.
static Sint16 *recordedSamples = NULL;
static size_t recordedCount = 0, recordedPos = 0, recordedLoop = 0;
static bool recordedMidi = false;    // its MIDI file plays
static bool recordedHasMidi = false; // it has one (follow_recorded_song)
static size_t recordedLoopStart = 0; // (as play_recorded_song had it)
static bool recordedSilent = false;  // faded out: silent until another song
static int recordedFade = 0, recordedFadeLength = 1;  // samples of the fade-out to go (0: none)
static char recordedPath[1024];
static Sint16 *endedSamples = NULL;  // the song ended, to free once the stream is unlocked
static MidiSong *endedMidi = NULL;

static void audioCallback(void *userdata, Uint8 *stream, int size);
static void audioStreamCallback(void *userdata, SDL_AudioStream *stream, int additional_amount, int total_amount);

static void load_song(unsigned int song_num);

bool init_audio(void)
{
	if (audio_disabled)
		return false;

	if (!SDL_InitSubSystem(SDL_INIT_AUDIO))
	{
		fprintf(stderr, "error: failed to initialize SDL audio: %s\n", SDL_GetError());
		audio_disabled = true;
		return false;
	}

	const SDL_AudioSpec spec = {
		.format = SDL_AUDIO_S16,
		.channels = 1,
		.freq = 11025 * OUTPUT_QUALITY,
	};

	SDL_SetHint(SDL_HINT_AUDIO_DEVICE_SAMPLE_FRAMES, "1024"); // ~23 ms

	audioStream = SDL_OpenAudioDeviceStream(SDL_AUDIO_DEVICE_DEFAULT_PLAYBACK, &spec, audioStreamCallback, NULL);

	if (audioStream == NULL)
	{
		fprintf(stderr, "error: SDL failed to open audio device: %s\n", SDL_GetError());
		audio_disabled = true;
		return false;
	}

	audioSampleRate = spec.freq;

	samplesPerLdsUpdate = 2 * (audioSampleRate / ldsUpdate2Rate);
	samplesPerLdsUpdateFrac = 2 * (audioSampleRate % ldsUpdate2Rate);

	volumeFactorTable[0] = 0;
	for (size_t i = 1; i < 256; ++i)
		volumeFactorTable[i] = TO_FIXED(powf(10, (255 - i) * (-volumeRange / (20.0f * 255))));

	voiceFadeSamples = audioSampleRate * 30 / 1000;
	voiceDuckStep = SDL_max(1, (VOICE_DUCK_ONE - voiceDuckLow) / (audioSampleRate / 5));

	opl_init();

	// Tyrian3D: the music as MIDI through a SoundFont when there is one (music_midi.h).
	if (music_midi_init(audioSampleRate))
		opl_write_hook = midi_opl_write;

	SDL_ResumeAudioStreamDevice(audioStream);

	return true;
}

void loudness_lock(void)
{
	if (audioStream != NULL)
		SDL_LockAudioStream(audioStream);
}

void loudness_unlock(void)
{
	if (audioStream != NULL)
		SDL_UnlockAudioStream(audioStream);
}

static void audioStreamCallback(void *userdata, SDL_AudioStream *stream, int additional_amount, int total_amount)
{
	(void)total_amount;

	Sint16 buffer[1024];
	while (additional_amount > 0)
	{
		const int size = MIN(additional_amount, (int)sizeof(buffer)) & ~1;
		if (size <= 0)
			break;

		audioCallback(userdata, (Uint8 *)buffer, size);
		SDL_PutAudioStreamData(stream, buffer, size);

		// Tyrian3D dev tool: TYR3D_RECORD_AUDIO=<file> writes the output as raw 16-bit mono samples.
		static FILE *record = NULL;
		static bool record_checked = false;
		if (!record_checked)
		{
			record_checked = true;
			const char *path = SDL_getenv("TYR3D_RECORD_AUDIO");
			if (path != NULL)
			{
				record = fopen(path, "wb");
				printf("audio: recording from %u ms\n", (unsigned)SDL_GetTicks());
			}
		}
		if (record != NULL)
		{
			fwrite(buffer, 1, size, record);
			fflush(record);
		}
		additional_amount -= size;
	}
}

static void audioCallback(void *userdata, Uint8 *stream, int size)
{
	(void)userdata;

	Sint16 *const samples = (Sint16 *)stream;
	const int samplesCount = size / sizeof (Sint16);

	if (!music_disabled && !music_stopped && (recordedSamples != NULL || recordedMidi))
	{
		// Tyrian3D: the recorded song
		if (recordedMidi && music_midi_active() && !recordedSilent)
			music_midi_song_render(samples, samplesCount);
		for (int i = 0; i < samplesCount; ++i)
		{
			Sint32 sample = 0;
			if (recordedSilent || (recordedMidi && !music_midi_active()))
				sample = 0;
			else if (recordedMidi)
				sample = samples[i];
			else
			{
				if (recordedPos >= recordedCount)
					recordedPos = recordedLoop < recordedCount ? recordedLoop : recordedCount;
				sample = recordedPos < recordedCount ? recordedSamples[recordedPos++] : 0;
			}
			if (recordedFade > 0)
			{
				sample = sample * recordedFade / recordedFadeLength;
				if (--recordedFade == 0)
					recordedSilent = true;
			}
			samples[i] = (Sint16)sample;
		}
	}
	else if (!music_disabled && !music_stopped)
	{
		Sint16 *remaining = samples;
		int remainingCount = samplesCount;
		while (remainingCount > 0)
		{
			if (samplesUntilLdsUpdate == 0)
			{
				lds_update();
				if (music_midi_active())
					music_midi_update();
				musicviz_chip(samplesCount - remainingCount);  // Tyrian3D: the jukebox's visuals

				// The number of samples that should be produced per Loudness
				// update is not an integer, but we can only produce an integer
				// number of samples, so we accumulate the fractional samples
				// until it amounts to a whole sample.
				samplesUntilLdsUpdate += samplesPerLdsUpdate;
				samplesUntilLdsUpdateFrac += samplesPerLdsUpdateFrac;
				if (samplesUntilLdsUpdateFrac >= ldsUpdate2Rate)
				{
					samplesUntilLdsUpdate += 1;
					samplesUntilLdsUpdateFrac -= ldsUpdate2Rate;
				}
			}

			int count = MIN(samplesUntilLdsUpdate, remainingCount);

			if (music_midi_active())
				music_midi_render(remaining, count);
			else
				opl_update(remaining, count);

			remaining += count;
			remainingCount -= count;

			samplesUntilLdsUpdate -= count;
		}
	}
	else
	{
		for (int i = 0; i < samplesCount; ++i)
			samples[i] = 0;
	}

	// Tyrian3D: the music ducked while a voice speaks.
	const Sint32 duckTarget = voiceCurrent.pos < voiceCurrent.count && !voicePaused ? voiceDuckLow : VOICE_DUCK_ONE;
	if (voiceDuck != VOICE_DUCK_ONE || duckTarget != VOICE_DUCK_ONE)
	{
		for (int i = 0; i < samplesCount; ++i)
		{
			if (voiceDuck > duckTarget)
				voiceDuck = SDL_max(duckTarget, voiceDuck - voiceDuckStep);
			else if (voiceDuck < duckTarget)
				voiceDuck = SDL_min(duckTarget, voiceDuck + voiceDuckStep);
			samples[i] = (Sint16)((samples[i] * voiceDuck) >> 16);
		}
	}

	Sint32 musicVolumeFactor = volumeFactorTable[musicVolume];
	if (!music_midi_active() && recordedSamples == NULL && !recordedMidi)
		musicVolumeFactor *= 2;  // OPL emulator is too quiet

	if (samples_disabled && !music_disabled)
	{
		// Mix music
		Sint16 *remaining = samples;
		int remainingCount = samplesCount;
		while (remainingCount > 0)
		{
			Sint32 sample = *remaining * musicVolumeFactor;

			sample = FIXED_TO_INT(sample);
			*remaining = MIN(MAX(INT16_MIN, sample), INT16_MAX);

			remaining += 1;
			remainingCount -= 1;
		}
	}
	else if (!samples_disabled)
	{
		Sint32 sampleVolumeFactor = volumeFactorTable[sampleVolume];
		// (Tyrian3D: ducked as the music is while a voice speaks, by where its ramp is at the buffer's end)
		sampleVolumeFactor = (Sint32)(((Sint64)sampleVolumeFactor * voiceDuck) >> 16);
		Sint32 sampleVolumeFactors[CHANNEL_VOLUME_LEVELS];
		for (int i = 0; i < CHANNEL_VOLUME_LEVELS; ++i)
			sampleVolumeFactors[i] = sampleVolumeFactor * (i + 1) / CHANNEL_VOLUME_LEVELS;

		// Mix music and channels
		Sint16 *remaining = samples;
		int remainingCount = samplesCount;
		while (remainingCount > 0)
		{
			Sint32 sample = *remaining * musicVolumeFactor;

			for (size_t i = 0; i < CHANNEL_COUNT; ++i)
			{
				if (channelSampleCount[i] > 0)
				{
					sample += *channelSamples[i] * sampleVolumeFactors[channelVolume[i]];

					channelSamples[i] += 1;
					channelSampleCount[i] -= 1;
				}
			}

			sample = FIXED_TO_INT(sample);
			*remaining = MIN(MAX(INT16_MIN, sample), INT16_MAX);

			remaining += 1;
			remainingCount -= 1;
		}
	}

	// Tyrian3D: the voice over it all (even with the music and the samples off).
	if ((voiceCurrent.pos < voiceCurrent.count && !voicePaused) || voiceFading.fade_left > 0)
	{
		const Sint32 voiceFactor = volumeFactorTable[voiceVolume];
		for (int i = 0; i < samplesCount; ++i)
		{
			Sint32 voice = 0;
			if (voiceCurrent.pos < voiceCurrent.count && !voicePaused)
				voice += voiceCurrent.samples[voiceCurrent.pos++] * voiceFactor;
			if (voiceFading.fade_left > 0 && voiceFading.pos < voiceFading.count)
			{
				const Sint32 gain = voiceFactor * voiceFading.fade_left / voiceFadeSamples;
				voice += voiceFading.samples[voiceFading.pos++] * gain;
				voiceFading.fade_left -= 1;
			}
			const Sint32 sample = samples[i] + FIXED_TO_INT(voice);
			samples[i] = MIN(MAX(INT16_MIN, sample), INT16_MAX);
		}
	}

	// Tyrian3D: the output as heard, for the jukebox's visuals.
	musicviz_feed(samples, samplesCount);
}

void audio_hold(bool hold)
{
	if (hold == held)
		return;
	held = hold;
	if (audio_disabled)
		return;
	// (Nothing of the samples started before goes on: neither those as it began nor its last ones as it ends.)
	SDL_LockAudioStream(audioStream);
	for (size_t i = 0; i < CHANNEL_COUNT; ++i)
		channelSampleCount[i] = 0;
	SDL_UnlockAudioStream(audioStream);
	if (!hold && held_song >= 0)
	{
		const unsigned int song = (unsigned int)held_song;
		held_song = -1;
		play_song(song);
	}
}

int voice_channel_play(Sint16 *samples, size_t count, Sint16 *done[2])
{
	int n = 0;
	if (audioStream == NULL)
	{
		if (samples != NULL)
			done[n++] = samples;
		return n;
	}

	SDL_LockAudioStream(audioStream);

	if (voiceFading.samples != NULL)  // (still fading: cut short)
		done[n++] = voiceFading.samples;
	voiceFading = (VoiceSlot){ 0 };
	if (voiceCurrent.samples != NULL)
	{
		if (voiceCurrent.pos < voiceCurrent.count)
		{
			voiceFading = voiceCurrent;
			voiceFading.fade_left = voiceFadeSamples;
		}
		else
		{
			done[n++] = voiceCurrent.samples;
		}
	}
	voiceCurrent = (VoiceSlot){ .samples = samples, .count = samples != NULL ? count : 0 };
	voicePaused = false;

	SDL_UnlockAudioStream(audioStream);
	return n;
}

void voice_channel_pause(bool paused)
{
	if (audioStream == NULL)
		return;
	SDL_LockAudioStream(audioStream);
	voicePaused = paused;
	SDL_UnlockAudioStream(audioStream);
}

float voice_channel_progress(void)
{
	if (audioStream == NULL)
		return 0;
	SDL_LockAudioStream(audioStream);
	const float progress = voiceCurrent.count > 0 ? voiceCurrent.pos / (float)voiceCurrent.count : 0;
	SDL_UnlockAudioStream(audioStream);
	return progress;
}

int voice_channel_collect(Sint16 *done[2], bool *playing)
{
	int n = 0;
	*playing = false;
	if (audioStream == NULL)
		return n;

	SDL_LockAudioStream(audioStream);

	if (voiceCurrent.samples != NULL && voiceCurrent.pos >= voiceCurrent.count)
	{
		done[n++] = voiceCurrent.samples;
		voiceCurrent = (VoiceSlot){ 0 };
	}
	if (voiceFading.samples != NULL && (voiceFading.fade_left <= 0 || voiceFading.pos >= voiceFading.count))
	{
		done[n++] = voiceFading.samples;
		voiceFading = (VoiceSlot){ 0 };
	}
	*playing = voiceCurrent.samples != NULL;

	SDL_UnlockAudioStream(audioStream);
	return n;
}

void voice_channel_volume(Uint8 volume)
{
	if (audioStream == NULL)
		return;

	SDL_LockAudioStream(audioStream);
	voiceVolume = volume;
	SDL_UnlockAudioStream(audioStream);
}

void deinit_audio(void)
{
	if (audio_disabled)
		return;

	if (audioStream != NULL)
	{
		SDL_DestroyAudioStream(audioStream);
		audioStream = NULL;
	}

	SDL_QuitSubSystem(SDL_INIT_AUDIO);

	memset(channelSampleCount, 0, sizeof channelSampleCount);

	SDL_free(voiceCurrent.samples);
	SDL_free(voiceFading.samples);
	voiceCurrent = voiceFading = (VoiceSlot){ 0 };

	lds_free();
}

// Tyrian3D: the recorded song ended (the stream locked); free_ended_song frees it once unlocked.
static void end_recorded_song(void)
{
	SDL_free(endedSamples);
	endedSamples = recordedSamples;
	recordedSamples = NULL;
	if (recordedMidi)
		endedMidi = music_midi_song_play(NULL);
	recordedMidi = recordedSilent = false;
	recordedCount = recordedPos = recordedLoop = 0;
	recordedFade = 0;
	recordedPath[0] = '\0';
}

static void free_ended_song(void)
{
	SDL_free(endedSamples);
	endedSamples = NULL;
	music_midi_song_free(endedMidi);
	endedMidi = NULL;
}

// The MIDI file beside a recorded song (its name's .wav as .mid), if there is one.
static bool midi_beside(const char *path, char *midi, size_t size)
{
	const size_t n = strlen(path);
	if (n < 4 || n >= size || SDL_strcasecmp(path + n - 4, ".wav") != 0)
		return false;
	memcpy(midi, path, n - 4);
	SDL_strlcpy(midi + n - 4, ".mid", size - (n - 4));
	return SDL_GetPathInfo(midi, NULL);
}

bool play_recorded_song(const char *path, size_t loop_start)
{
	if (audio_disabled)
		return false;
	char midi_path[1024];
	bool has_midi = midi_beside(path, midi_path, sizeof(midi_path));
	MidiSong *midi = NULL;
	if ((recordedSamples != NULL || recordedMidi) && !recordedSilent && strcmp(path, recordedPath) == 0 &&
	    recordedMidi == (has_midi && music_midi_active()))
	{
		SDL_LockAudioStream(audioStream);  // (playing already: on as it is)
		music_stopped = false;
		SDL_UnlockAudioStream(audioStream);
		return true;
	}
	if (has_midi && music_midi_active())
	{
		midi = music_midi_song_load(midi_path);
		has_midi = midi != NULL;
	}
	if (midi != NULL)
	{
		SDL_LockAudioStream(audioStream);
		end_recorded_song();
		recordedMidi = recordedHasMidi = true;
		recordedLoopStart = loop_start;
		music_midi_song_play(midi);
		SDL_strlcpy(recordedPath, path, sizeof(recordedPath));
		music_stopped = false;
		song_playing = 0;
		SDL_UnlockAudioStream(audioStream);
		free_ended_song();
		return true;
	}
	SDL_AudioSpec spec;
	Uint8 *wav = NULL, *pcm = NULL;
	Uint32 length = 0;
	int pcm_length = 0;
	if (!SDL_LoadWAV(path, &spec, &wav, &length))
		return false;
	const SDL_AudioSpec out = { .format = SDL_AUDIO_S16, .channels = 1, .freq = audioSampleRate };
	const bool ok = SDL_ConvertAudioSamples(&spec, wav, (int)length, &out, &pcm, &pcm_length);
	const double scale = (double)audioSampleRate / spec.freq;
	SDL_free(wav);
	if (!ok)
		return false;
	SDL_LockAudioStream(audioStream);
	end_recorded_song();
	recordedSamples = (Sint16 *)pcm;
	recordedCount = (size_t)pcm_length / sizeof(Sint16);
	recordedLoop = (size_t)(loop_start * scale);
	recordedHasMidi = has_midi;
	recordedLoopStart = loop_start;
	SDL_strlcpy(recordedPath, path, sizeof(recordedPath));
	music_stopped = false;
	song_playing = 0;
	SDL_UnlockAudioStream(audioStream);
	free_ended_song();
	return true;
}

void follow_recorded_song(void)
{
	if (recordedPath[0] == '\0' || recordedSilent || !recordedHasMidi || recordedMidi == music_midi_active())
		return;
	char path[sizeof(recordedPath)];
	SDL_strlcpy(path, recordedPath, sizeof(path));
	play_recorded_song(path, recordedLoopStart);
}

// The recorded song ended, if one plays (before a Loudness song, or none).
static void stop_recorded_song(void)
{
	if (recordedSamples == NULL && !recordedMidi)
		return;
	SDL_LockAudioStream(audioStream);
	end_recorded_song();
	SDL_UnlockAudioStream(audioStream);
	free_ended_song();
}

void load_music(void)  // FKA NortSong.loadSong
{
	if (music_file == NULL)
	{
		music_file = dir_fopen_die(data_dir(), "music.mus", "rb");

		fread_u16_die(&song_count, 1, music_file);

		song_offset = malloc((song_count + 1) * sizeof(*song_offset));

		fread_u32_die(song_offset, song_count, music_file);

		song_offset[song_count] = ftell_eof(music_file);
	}
}

static void load_song(unsigned int song_num)  // FKA NortSong.loadSong
{
	if (song_num < song_count)
	{
		unsigned int song_size = song_offset[song_num + 1] - song_offset[song_num];
		lds_load(music_file, song_offset[song_num], song_size);
		if (audioStream != NULL)
		{
			SDL_LockAudioStream(audioStream);
			music_midi_reset();
			SDL_UnlockAudioStream(audioStream);
		}
	}
	else
	{
		fprintf(stderr, "warning: failed to load song %d\n", song_num + 1);
	}
}

unsigned int music_song_count(void)
{
	load_music();
	return song_count;
}

void music_load_song(unsigned int song_num)
{
	load_music();
	load_song(song_num);
}

void play_song(unsigned int song_num)  // FKA NortSong.playSong
{
	if (audio_disabled)
		return;
	if (held)  // (Tyrian3D: once let go)
	{
		held_song = (int)song_num;
		return;
	}

	const bool recorded = recordedSamples != NULL || recordedMidi;  // (Tyrian3D: one played in place of the song loaded)
	stop_recorded_song();

	if (song_num != song_playing || recorded)
	{
		SDL_LockAudioStream(audioStream);

		music_stopped = true;

		SDL_UnlockAudioStream(audioStream);

		load_song(song_num);

		song_playing = song_num;
	}

	SDL_LockAudioStream(audioStream);

	music_stopped = false;

	SDL_UnlockAudioStream(audioStream);
}

void restart_song(void)  // FKA Player.selectSong(1)
{
	if (audio_disabled)
		return;

	SDL_LockAudioStream(audioStream);

	lds_rewind();
	music_midi_reset();
	recordedPos = 0;  // (Tyrian3D: a recorded song from its start)
	recordedFade = 0;
	recordedSilent = false;
	if (recordedMidi)
		music_midi_song_rewind();

	music_stopped = false;

	SDL_UnlockAudioStream(audioStream);
}

void stop_song(void)  // FKA Player.selectSong(0)
{
	if (audio_disabled)
		return;

	SDL_LockAudioStream(audioStream);

	music_stopped = true;
	music_midi_reset();
	end_recorded_song();  // (Tyrian3D)

	SDL_UnlockAudioStream(audioStream);
	free_ended_song();
}

void fade_song(void)  // FKA Player.selectSong($C001)
{
	if (audio_disabled)
		return;

	SDL_LockAudioStream(audioStream);

	lds_fade(1);
	if ((recordedSamples != NULL || recordedMidi) && recordedFade == 0 && !recordedSilent)  // (Tyrian3D: a recorded song over a second)
		recordedFade = recordedFadeLength = audioSampleRate;

	SDL_UnlockAudioStream(audioStream);
}

void set_volume(Uint8 musicVolume_, Uint8 sampleVolume_)  // FKA NortSong.setVol and Player.setVol
{
	if (audio_disabled)
		return;

	SDL_LockAudioStream(audioStream);

	musicVolume = musicVolume_;
	sampleVolume = sampleVolume_;

	SDL_UnlockAudioStream(audioStream);
}

void multiSamplePlay(const Sint16 *samples, size_t sampleCount, Uint8 chan, Uint8 vol)  // FKA Player.multiSamplePlay
{
	assert(chan < CHANNEL_COUNT);
	assert(vol < CHANNEL_VOLUME_LEVELS);

	if (audio_disabled || samples_disabled || held)
		return;

	SDL_LockAudioStream(audioStream);

	channelSamples[chan] = samples;
	channelSampleCount[chan] = sampleCount;
	channelVolume[chan] = vol;

	SDL_UnlockAudioStream(audioStream);
}
