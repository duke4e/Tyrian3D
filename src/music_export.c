/*
 * Tyrian3D dev tool: exports the game's music as MIDI files (see music_export.h).
 *
 * The songs are Loudness (LDS) modules for the AdLib's OPL2 FM chip. Each song is played through
 * the game's own LDS player without sound, and the chip register writes it makes are turned
 * into MIDI: a key going on or off on one of the nine FM channels is a note, its frequency the
 * pitch (bends follow vibrato and slides), the carrier's level the velocity and expression. In
 * rhythm mode the chip's five drums go to the MIDI drum channel. Each song plays until it loops.
 *
 * Instruments: LDS instruments carry the General MIDI program, velocity and transposition the
 * Loudness system used on MIDI devices (midinst, midvelo, midtrans); the exporter uses them, and
 * lists every instrument with its FM settings and use in instruments.json, so the choice can be
 * checked and changed by ear.
 */
#include "music_export.h"

#include "lds_play.h"
#include "loudness.h"
#include "musmast.h"
#include "opl.h"
#include "opentyr.h"

#include <SDL3/SDL.h>

#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define TICKS_PER_SECOND 69.5           // the game updates the player at 69.5 Hz (loudness.c)
#define MIDI_DIVISION 1390               // MIDI ticks per quarter note
#define MIDI_TEMPO 1000000               // microseconds per quarter note: 20 MIDI ticks per update
#define MIDI_TICKS_PER_UPDATE 20
#define MAX_UPDATES (int)(TICKS_PER_SECOND * 600)  // 10 minutes
#define DRUM_CHANNEL 9
#define BEND_RANGE 2.0                   // semitones (the General MIDI default)

static const Uint8 op_offset[9] = { 0x00, 0x01, 0x02, 0x08, 0x09, 0x0a, 0x10, 0x11, 0x12 };

// --- MIDI tracks ---------------------------------------------------------------------------

typedef struct
{
	Uint8 *data;
	size_t size, capacity;
	Uint32 last_time;  // MIDI ticks of the last event
} Track;

static void track_byte(Track *t, Uint8 b)
{
	if (t->size == t->capacity)
	{
		t->capacity = t->capacity ? t->capacity * 2 : 4096;
		t->data = realloc(t->data, t->capacity);
	}
	t->data[t->size++] = b;
}

static void track_varlen(Track *t, Uint32 value)
{
	Uint8 bytes[5];
	int n = 0;
	do
	{
		bytes[n++] = value & 0x7f;
		value >>= 7;
	} while (value != 0);
	while (n > 0)
	{
		--n;
		track_byte(t, bytes[n] | (n > 0 ? 0x80 : 0));
	}
}

static void track_event(Track *t, Uint32 time, Uint8 status, int data1, int data2)
{
	track_varlen(t, time - t->last_time);
	t->last_time = time;
	track_byte(t, status);
	track_byte(t, (Uint8)data1);
	if (data2 >= 0)
		track_byte(t, (Uint8)data2);
}

static void track_meta(Track *t, Uint32 time, Uint8 type, const Uint8 *payload, Uint32 length)
{
	track_varlen(t, time - t->last_time);
	t->last_time = time;
	track_byte(t, 0xff);
	track_byte(t, type);
	track_varlen(t, length);
	for (Uint32 i = 0; i < length; ++i)
		track_byte(t, payload[i]);
}

static void write_u32(FILE *f, Uint32 v)
{
	const Uint8 b[4] = { v >> 24, v >> 16, v >> 8, v };
	fwrite(b, 1, 4, f);
}

static void write_u16(FILE *f, Uint16 v)
{
	const Uint8 b[2] = { v >> 8, v };
	fwrite(b, 1, 2, f);
}

// --- The chip, as the player writes to it --------------------------------------------------

static Uint8 reg[256];
static bool keyoff_written[9];  // a key went off during this update (a retriggered note)
static Uint8 drum_hits;         // rhythm bits that went on during this update

static void on_write(unsigned int r, unsigned int value)
{
	if (r >= 0xb0 && r <= 0xb8 && (reg[r] & 0x20) && !(value & 0x20))
		keyoff_written[r - 0xb0] = true;
	if (r == 0xbd)
		drum_hits |= (Uint8)(value & ~reg[0xbd] & 0x1f);
	reg[r & 0xff] = (Uint8)value;
}

static double channel_pitch(int ch)
{
	const int fnum = reg[0xa0 + ch] | ((reg[0xb0 + ch] & 3) << 8);
	const int block = (reg[0xb0 + ch] >> 2) & 7;
	if (fnum == 0)
		return 0;
	const double hz = fnum * 49716.0 / (double)(1 << (20 - block));
	return 69 + 12 * log2(hz / 440);
}

// A level of 0..63 (0.75 dB steps, 0 loudest) as a MIDI value, loudness rather than amplitude;
// relative to a reference level (expression while a note sounds), or to full volume.
static int level_to_midi(int level, int reference)
{
	const double amplitude = pow(10, -0.75 * (level - reference) / 20);
	const int value = (int)lround(127 * sqrt(amplitude));
	return SDL_clamp(value, 1, 127);
}

static int channel_level(int ch)
{
	const int car = reg[0x40 + op_offset[ch] + 3] & 0x3f;
	const int mod = reg[0x40 + op_offset[ch]] & 0x3f;
	return (reg[0xc0 + ch] & 1) ? SDL_min(car, mod) : car;  // additive: both operators sound
}

// --- Instruments ----------------------------------------------------------------------------

typedef struct
{
	unsigned int notes;
	double lowest, highest, seconds;
} InstrumentUse;

static InstrumentUse use[256];

static int instrument_program(int inst)
{
	const SoundBank *s = lds_sound(inst);
	return s != NULL ? s->midinst & 0x7f : 0;
}

// The instrument's transposition for MIDI (signed semitones), as Loudness played it on MIDI
// devices, where the FM patch sounds in another octave than its notes.
static int instrument_transpose(int inst)
{
	const SoundBank *s = lds_sound(inst);
	return s != NULL ? (Sint8)s->midtrans : 0;
}

// The instrument's MIDI velocity (1..127), which scales the chip's level.
static int instrument_velocity(int inst)
{
	const SoundBank *s = lds_sound(inst);
	return s != NULL && s->midvelo > 0 ? SDL_min(s->midvelo, 127) : 127;
}

// --- Export ---------------------------------------------------------------------------------

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
} Voice;

static void export_song(unsigned int song, const char *dir)
{
	music_load_song(song);
	memset(reg, 0, sizeof(reg));
	memset(lds_channel_sound, 0, sizeof(lds_channel_sound));
	opl_write_hook = on_write;
	lds_rewind();

	Track tracks[16] = { { 0 } };
	Voice voices[9];
	for (int ch = 0; ch < 9; ++ch)
		voices[ch] = (Voice){ .program = -1, .bend = 8192, .expression = -1 };
	bool drum_on[5] = { false };
	static const int drum_note[5] = { 42, 49, 45, 38, 36 };  // bits 0-4: hi-hat, cymbal, tom, snare, bass drum

	Uint32 update = 0;
	for (; update < MAX_UPDATES; ++update)
	{
		memset(keyoff_written, 0, sizeof(keyoff_written));
		drum_hits = 0;
		const bool more = lds_update();
		const Uint32 time = update * MIDI_TICKS_PER_UPDATE;
		const bool rhythm = (reg[0xbd] & 0x20) != 0;

		for (int ch = 0; ch < 9; ++ch)
		{
			Voice *v = &voices[ch];
			Track *t = &tracks[ch];
			const bool melodic = !(rhythm && ch >= 6);
			const bool key = melodic && (reg[0xb0 + ch] & 0x20) != 0;
			const double pitch = channel_pitch(ch);
			const int level = channel_level(ch);

			const bool restart = key && (!v->on || keyoff_written[ch] || fabs(pitch - v->note_pitch) > BEND_RANGE);
			if (v->on && (!key || restart))
			{
				track_event(t, time, 0x80 | ch, v->note, 0);
				InstrumentUse *u = &use[v->inst & 0xff];
				u->seconds += (update - v->started) / TICKS_PER_SECOND;
				v->on = false;
			}
			if (restart && pitch > 0)
			{
				const int inst = lds_channel_sound[ch];
				const int program = instrument_program(inst);
				if (program != v->program)
				{
					track_event(t, time, 0xc0 | ch, program, -1);
					v->program = program;
				}
				if (v->bend != 8192)
				{
					track_event(t, time, 0xe0 | ch, 0, 64);
					v->bend = 8192;
				}
				if (v->expression != 127)
				{
					track_event(t, time, 0xb0 | ch, 11, 127);
					v->expression = 127;
				}
				const int transpose = instrument_transpose(inst);
				v->note = SDL_clamp((int)lround(pitch) + transpose, 0, 127);
				v->note_pitch = v->note - transpose;
				v->inst = inst;
				v->started = update;
				v->start_level = level;
				v->on = true;
				track_event(t, time, 0x90 | ch, v->note, SDL_max(1, level_to_midi(level, 0) * instrument_velocity(inst) / 127));

				InstrumentUse *u = &use[inst & 0xff];
				if (u->notes == 0 || pitch < u->lowest)
					u->lowest = pitch;
				if (u->notes == 0 || pitch > u->highest)
					u->highest = pitch;
				++u->notes;
			}
			else if (v->on)
			{
				// Vibrato and slides as pitch bends, the level's changes (fades, tremolo) as expression.
				const int bend = SDL_clamp((int)lround(8192 + (pitch - v->note_pitch) / BEND_RANGE * 8192), 0, 16383);
				if (abs(bend - v->bend) > 16)
				{
					track_event(t, time, 0xe0 | ch, bend & 0x7f, bend >> 7);
					v->bend = bend;
				}
				const int expression = level_to_midi(level, v->start_level);
				if (expression != v->expression)
				{
					track_event(t, time, 0xb0 | ch, 11, expression);
					v->expression = expression;
				}
			}
		}

		// The rhythm section's drums.
		Track *drums = &tracks[DRUM_CHANNEL];
		for (int d = 0; d < 5; ++d)
		{
			const bool hit = rhythm && (drum_hits & (1 << d));
			const bool held = rhythm && (reg[0xbd] & (1 << d));
			if (drum_on[d] && (hit || !held))
			{
				track_event(drums, time, 0x80 | DRUM_CHANNEL, drum_note[d], 0);
				drum_on[d] = false;
			}
			if (hit)
			{
				const int ch = d == 4 ? 6 : (d == 0 || d == 3) ? 7 : 8;  // the channels the drums use
				track_event(drums, time, 0x90 | DRUM_CHANNEL, drum_note[d], level_to_midi(channel_level(ch), 0));
				drum_on[d] = true;
			}
		}

		if (!more)
			break;
	}
	opl_write_hook = NULL;

	// End every note, then write the file: a tempo track and a track per channel used.
	const Uint32 end = (update + 1) * MIDI_TICKS_PER_UPDATE;
	for (int ch = 0; ch < 9; ++ch)
		if (voices[ch].on)
			track_event(&tracks[ch], end, 0x80 | ch, voices[ch].note, 0);
	for (int d = 0; d < 5; ++d)
		if (drum_on[d])
			track_event(&tracks[DRUM_CHANNEL], end, 0x80 | DRUM_CHANNEL, drum_note[d], 0);

	char name[64], path[1024];
	SDL_strlcpy(name, song < MUSIC_NUM ? musicTitle[song] : "song", sizeof(name));
	for (char *c = name; *c != '\0'; ++c)
		if (!SDL_isalnum((unsigned char)*c) && *c != ' ' && *c != '-')
			*c = '_';
	snprintf(path, sizeof(path), "%s/%02u %s.mid", dir, song + 1, name);
	FILE *f = fopen(path, "wb");
	if (f == NULL)
	{
		fprintf(stderr, "warning: can't write %s\n", path);
		return;
	}

	Track tempo = { 0 };
	const Uint8 tempo_bytes[3] = { MIDI_TEMPO >> 16, (MIDI_TEMPO >> 8) & 0xff, MIDI_TEMPO & 0xff };
	track_meta(&tempo, 0, 0x51, tempo_bytes, 3);
	track_meta(&tempo, 0, 0x03, (const Uint8 *)name, (Uint32)strlen(name));
	track_meta(&tempo, end, 0x2f, NULL, 0);

	int used = 0;
	for (int c = 0; c < 16; ++c)
		used += tracks[c].size > 0;
	fwrite("MThd", 1, 4, f);
	write_u32(f, 6);
	write_u16(f, 1);
	write_u16(f, (Uint16)(used + 1));
	write_u16(f, MIDI_DIVISION);
	Track *all[17] = { &tempo };
	int count = 1;
	for (int c = 0; c < 16; ++c)
		if (tracks[c].size > 0)
		{
			track_meta(&tracks[c], end, 0x2f, NULL, 0);
			all[count++] = &tracks[c];
		}
	for (int i = 0; i < count; ++i)
	{
		fwrite("MTrk", 1, 4, f);
		write_u32(f, (Uint32)all[i]->size);
		fwrite(all[i]->data, 1, all[i]->size, f);
		free(all[i]->data);
	}
	fclose(f);
	printf("music: %s (%.0f s)\n", path, update / TICKS_PER_SECOND);
}

void dev_export_music(const char *dir)
{
	SDL_CreateDirectory(dir);
	memset(use, 0, sizeof(use));
	const unsigned int songs = music_song_count();
	char path[1024];
	snprintf(path, sizeof(path), "%s/instruments.json", dir);
	FILE *json = fopen(path, "w");
	if (json != NULL)
		fprintf(json, "[");

	for (unsigned int song = 0; song < songs; ++song)
	{
		memset(use, 0, sizeof(use));
		export_song(song, dir);

		// The song's instruments, with their FM settings and how the song used them.
		for (int inst = 0; json != NULL && inst < 256; ++inst)
		{
			const SoundBank *s = lds_sound(inst);
			if (s == NULL || use[inst].notes == 0)
				continue;
			fprintf(json, "%s\n  {\"song\": %u, \"instrument\": %d, \"program\": %d, \"midi\": [%d, %d, %d], "
			        "\"modulator\": [%d, %d, %d, %d, %d], \"carrier\": [%d, %d, %d, %d, %d], \"feedback\": %d, "
			        "\"notes\": %u, \"lowest\": %.1f, \"highest\": %.1f, \"seconds\": %.1f}",
			        ftell(json) > 1 ? "," : "", song + 1, inst, s->midinst & 0x7f, s->midvelo, s->midkey, s->midtrans,
			        s->mod_misc, s->mod_vol, s->mod_ad, s->mod_sr, s->mod_wave,
			        s->car_misc, s->car_vol, s->car_ad, s->car_sr, s->car_wave, s->feedback,
			        use[inst].notes, use[inst].lowest, use[inst].highest, use[inst].seconds);
		}
	}
	if (json != NULL)
	{
		fprintf(json, "\n]\n");
		fclose(json);
	}
}
