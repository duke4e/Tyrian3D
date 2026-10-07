/*
 * Tyrian3D: the game's music as MIDI (plan M10).
 *
 * The songs are Loudness (LDS) modules for the AdLib's OPL2 FM chip. The translator watches the
 * chip register writes the game's LDS player makes and turns them into MIDI events: a key going on
 * or off on one of the nine FM channels is a note, its frequency the pitch (bends follow vibrato
 * and slides), the carrier's level the velocity and expression; in rhythm mode the chip's five
 * drums go to the MIDI drum channel. Programs, velocities and transpositions come from the
 * General MIDI settings LDS instruments carry for MIDI devices (midinst, midvelo, midtrans).
 *
 * The export tool (music_export.c) writes the events to MIDI files; the live synth plays them
 * through a SoundFont (TinySoundFont) instead of the emulated chip, as the music plays.
 */
#ifndef MUSIC_MIDI_H
#define MUSIC_MIDI_H

#include "opentyr.h"

#include <SDL3/SDL.h>

#define MIDI_DRUM_CHANNEL 9

typedef struct
{
	unsigned int notes;
	double lowest, highest, seconds;
} MidiInstrumentUse;

typedef struct
{
	bool on;
	int note;            // sounding MIDI note
	double note_pitch;   // its pitch when it started (bends are relative to the note)
	int bend;            // last pitch bend sent (0..16383)
	int expression;      // last expression sent
	int start_level;     // the chip's level when the note started (its velocity)
	int program;         // last program sent, or -1
	int inst;            // LDS instrument of the sounding note
	Uint32 started;      // update it started
} MidiVoice;

typedef struct
{
	// Where events go: update is the player update (69.5 a second) they belong to.
	void (*event)(void *user, Uint32 update, Uint8 status, int data1, int data2);
	void *user;

	MidiVoice voices[9];
	bool drum_on[5];
	MidiInstrumentUse use[256];  // what each LDS instrument played (for the export's notes)
} MidiTranslator;

// Starts translating from a silent chip.
void midi_translator_reset(MidiTranslator *t);
// After each lds_update: the events for what the player changed on the chip.
void midi_translator_update(MidiTranslator *t, Uint32 update);
// Ends every sounding note.
void midi_translator_end(MidiTranslator *t, Uint32 update);

// The chip register writes the translator watches (opl_write_hook while translating).
void midi_opl_write(unsigned int reg, unsigned int value);
// Clears the watched chip state (a new song).
void midi_opl_clear(void);

// --- Live synth ---------------------------------------------------------------------------

// Loads the SoundFont (soundfonts/GeneralUser-GS.sf2 beside the game's data or the program, or
// TYR3D_SOUNDFONT=<file>) for output at the given rate. False if there is none.
bool music_midi_init(int sample_rate);
bool music_midi_available(void);
// The live synth plays the music (instead of the OPL emulator) while enabled and available.
void music_midi_enable(bool enabled);
bool music_midi_active(void);

// Called from the audio callback: after each lds_update, and to render samples.
void music_midi_update(void);
void music_midi_render(Sint16 *samples, int count);
// A new song, a rewind or a stop: all notes off, translation from a silent chip.
void music_midi_reset(void);

#endif /* MUSIC_MIDI_H */
