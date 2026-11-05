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
#ifndef LOUDNESS_H
#define LOUDNESS_H

#include "opentyr.h"
#include "opl.h"

#include <SDL3/SDL.h>

extern int audioSampleRate;

extern unsigned int song_playing;

extern bool audio_disabled, music_disabled, samples_disabled;

bool init_audio(void);
void deinit_audio(void);
// Tyrian3D: holds the audio thread off (the music's synth changing under it), and lets it go on.
void loudness_lock(void);
void loudness_unlock(void);

void load_music(void);

// Tyrian3D, for the music exporter: the number of songs, and loading one into the player without
// playing it.
unsigned int music_song_count(void);
void music_load_song(unsigned int song_num);
void play_song(unsigned int song_num);
void restart_song(void);
void stop_song(void);
void fade_song(void);
// Tyrian3D: a recorded song (a WAV file) in place of the Loudness music, from loop_start (a sample of the file) again
// at its end, or the MIDI file beside it (its name's .mid) through the SoundFont while the music plays as MIDI;
// play_song, stop_song and fade_song end it. False if it can't be read.
bool play_recorded_song(const char *path, size_t loop_start);
// Tyrian3D: the recorded song in the form the music plays in now, from its start, where the music went between
// MIDI and the chip since it began (its MIDI file through the SoundFont, or its samples).
void follow_recorded_song(void);

void set_volume(Uint8 musicVolume, Uint8 sampleVolume);

void multiSamplePlay(const Sint16 *samples, size_t sampleCount, Uint8 chan, Uint8 vol);

// Tyrian3D: the sound held back while the game plays on unseen (a checkpoint's or a rewind's replay, debugmode.c): the
// samples it plays are dropped (unheld, they came all at once as a burst), the song playing goes on, and a song asked
// for meanwhile starts as it is let go.
void audio_hold(bool hold);

// Tyrian3D: the voice channel (voiceover.h), over the music (ducked meanwhile) and the samples.
// voice_channel_play starts samples (mono, 16-bit, at audioSampleRate, SDL_malloc'd; NULL: none) and
// fades out the voice playing. Both calls put in done[] the buffers the mixer no longer reads (0-2,
// returned), for the caller to SDL_free; collect also tells whether a voice is still playing.
int voice_channel_play(Sint16 *samples, size_t count, Sint16 *done[2]);
int voice_channel_collect(Sint16 *done[2], bool *playing);
void voice_channel_volume(Uint8 volume);
// The voice playing held where it is (or going on), and how far it has played (0-1).
void voice_channel_pause(bool paused);
float voice_channel_progress(void);

#endif /* LOUDNESS_H */
