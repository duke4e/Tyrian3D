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
	double start_level;  // how far below full level the chip sounded it as it started (dB; its velocity)
	bool faded;          // the chip's note has faded out (its envelope) while its key is held: note off sent
	bool drum;           // a drum's (its instrument's MIDI program 128 and up): on the drum channel
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
// How far below full level a chip channel sounds (dB), seconds after its key went on, by the chip's
// registers (its operators' levels, key scaling and envelopes; the jukebox's visuals read it too).
double midi_chip_channel_db(const Uint8 *reg, int ch, double seconds);

// --- Live synth ---------------------------------------------------------------------------

// Loads the SoundFont (the one settings3d.soundfont names, else GeneralUser-GS, from soundfonts/ beside
// the game's data or the program; TYR3D_SOUNDFONT=<file> for a run) for output at the given rate. False
// if there is none.
bool music_midi_init(int sample_rate);
bool music_midi_available(void);
// The SoundFonts to choose from (the soundfonts folder's *.sf2, by name: the file's without ".sf2"),
// and the one the music plays through ("" with none).
int music_midi_soundfont_count(void);
const char *music_midi_soundfont_name(int i);
const char *music_midi_soundfont(void);
// The music through that SoundFont from now on ("": the default one); false if it can't be loaded (the
// one before stays). Loading a large one takes a moment.
bool music_midi_use(const char *name);
// The live synth plays the music (instead of the OPL emulator) while enabled and available.
void music_midi_enable(bool enabled);
bool music_midi_active(void);

// Called from the audio callback: after each lds_update, and to render samples.
void music_midi_update(void);
void music_midi_render(Sint16 *samples, int count);
// A new song, a rewind or a stop: all notes off, translation from a silent chip.
void music_midi_reset(void);

#endif /* MUSIC_MIDI_H */
