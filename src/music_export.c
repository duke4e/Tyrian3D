/*
 * Tyrian3D dev tool: exports the game's music as MIDI files (see music_export.h).
 *
 * Each song is played through the game's own LDS player without sound, and the translator of
 * music_midi.h turns the chip register writes it makes into MIDI. Each song plays until it loops.
 *
 * Instruments: LDS instruments carry the General MIDI program, velocity and transposition the
 * Loudness system used on MIDI devices (midinst, midvelo, midtrans); the exporter uses them, and
 * lists every instrument with its FM settings and use in instruments.json, so the choice can be
 * checked and changed by ear.
 */
#include "music_export.h"

#include "music_midi.h"

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

// --- Export ---------------------------------------------------------------------------------

typedef struct
{
	Track tracks[16];
} ExportTracks;

static void track_midi_event(void *user, Uint32 update, Uint8 status, int data1, int data2)
{
	ExportTracks *e = user;
	track_event(&e->tracks[status & 0x0f], update * MIDI_TICKS_PER_UPDATE, status, data1, data2);
}

static MidiInstrumentUse use[256];

static void export_song(unsigned int song, const char *dir)
{
	music_load_song(song);
	midi_opl_clear();
	memset(lds_channel_sound, 0, sizeof(lds_channel_sound));
	void (*live_hook)(unsigned int, unsigned int) = opl_write_hook;
	opl_write_hook = midi_opl_write;
	lds_rewind();

	static ExportTracks export_tracks;
	memset(&export_tracks, 0, sizeof(export_tracks));
	Track *tracks = export_tracks.tracks;
	static MidiTranslator translator;
	memset(&translator, 0, sizeof(translator));
	midi_translator_reset(&translator);
	translator.event = track_midi_event;
	translator.user = &export_tracks;

	Uint32 update = 0;
	for (; update < MAX_UPDATES; ++update)
	{
		const bool more = lds_update();
		midi_translator_update(&translator, update);
		if (!more)
			break;
	}
	opl_write_hook = live_hook;
	midi_opl_clear();

	// End every note, then write the file: a tempo track and a track per channel used.
	const Uint32 end = (update + 1) * MIDI_TICKS_PER_UPDATE;
	midi_translator_end(&translator, update + 1);
	memcpy(use, translator.use, sizeof(use));

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
			        "\"notes\": %u, \"lowest\": %.1f, \"highest\": %.1f, \"seconds\": %.1f, \"raw\": [%d, %d, %d]}",
			        ftell(json) > 1 ? "," : "", song + 1, inst, s->midinst & 0x7f, s->midvelo, s->midkey, s->midtrans,
			        s->mod_misc, s->mod_vol, s->mod_ad, s->mod_sr, s->mod_wave,
			        s->car_misc, s->car_vol, s->car_ad, s->car_sr, s->car_wave, s->feedback,
			        use[inst].notes, use[inst].lowest, use[inst].highest, use[inst].seconds, s->midinst, s->middum1, s->middum2);
		}
	}
	if (json != NULL)
	{
		fprintf(json, "\n]\n");
		fclose(json);
	}
}
