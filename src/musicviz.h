/*
 * Tyrian3D: the music measured where it is made, for the jukebox's visuals (jukebox3d.h).
 *
 * The audio thread hands over what it makes: the mixed output (music and sound effects, as heard)
 * after each buffer, and the chip's state after each update of the music's player (both kinds of
 * music, the emulated chip and MIDI through the SoundFont, are played from the same chip writes):
 * each channel's key, pitch, instrument, the notes it has started and how loud it sounds (the chip's
 * levels and envelopes). The main thread reads them where the output is being heard (the device's
 * latency, about) and makes a spectrum, levels, beats and the channels' notes from them. Nothing is
 * locked but a few numbers (a spinlock), the audio thread never waits.
 */
#ifndef MUSICVIZ_H
#define MUSICVIZ_H

#include "opentyr.h"

#include <SDL3/SDL.h>

#define MUSICVIZ_BANDS 48     // the spectrum's bands, 30 Hz to 16 kHz, a log scale
#define MUSICVIZ_CHANNELS 9   // the chip's channels

// The drums the songs play (their instruments' General MIDI drum notes).
enum { MUSICVIZ_KICK, MUSICVIZ_SNARE, MUSICVIZ_HAT, MUSICVIZ_CYMBAL, MUSICVIZ_TOM, MUSICVIZ_DRUM_KINDS };

typedef struct
{
	bool on;          // a note sounds (its key held and not faded out)
	float level;      // how loud, 0-1 (amplitude)
	float note;       // its pitch, a MIDI note number (the last note's while silent)
	float flash;      // 1 as a note starts, falling to 0 in about a third of a second
	Uint32 notes;     // notes started on it (its last frame's count + the new ones)
	int drum;         // its instrument is a drum: its General MIDI drum note (35-81); else 0
	int drum_kind;    // and which (MUSICVIZ_KICK...), or -1
	int program;      // its instrument's General MIDI program (0-127)
} MusicVizChannel;

typedef struct
{
	bool live;                       // the audio runs and has been measured
	float time;                      // seconds measured (the visuals' clock)
	float level;                     // loudness, 0-1 (against the music's own loudest of late)
	float peak;                      // the loudest sample of the window, 0-1
	float bands[MUSICVIZ_BANDS];     // the spectrum, 0-1, quick to rise, slower to fall
	float peaks[MUSICVIZ_BANDS];     // each band's peak: held a moment, then falling
	float bass, mid, high;           // the spectrum's lows (to 150 Hz), mids (to 2 kHz) and highs, 0-1
	float flux;                      // how much louder the spectrum got (onsets), 0-1
	float beat;                      // 1 on a beat, falling to 0 in about a quarter of a second
	Uint32 beats;                    // beats so far
	float drums[MUSICVIZ_DRUM_KINDS];       // 1 on a hit, falling
	Uint32 drum_hits[MUSICVIZ_DRUM_KINDS];  // hits so far
	MusicVizChannel channels[MUSICVIZ_CHANNELS];
	int notes_new;                   // notes started since the last update (all channels)
	bool midi;                       // the music plays through the SoundFont (else the chip)
} MusicViz;

// The audio thread (loudness.c): after each update of the music's player, at this sample of the
// buffer being made; and the buffer made (mono, at audioSampleRate).
void musicviz_chip(int offset);
void musicviz_feed(const Sint16 *samples, int count);

// The main thread: the music as heard now, dt seconds after the last update. TYR3D_LOG_MUSICVIZ=1
// prints it every half second.
void musicviz_update(MusicViz *viz, float dt);

#endif /* MUSICVIZ_H */
