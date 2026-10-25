/*
 * Tyrian3D: the game's music as MIDI. See music_midi.h.
 */
#include "music_midi.h"

#include "file.h"
#include "lds_play.h"
#include "opl.h"
#include "paths3d.h"
#include "loudness.h"
#include "settings3d.h"

#include <math.h>
#include <stdio.h>
#include <string.h>

#define TSF_IMPLEMENTATION
#if defined(__clang__)
#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Wnull-pointer-subtraction"
#pragma clang diagnostic ignored "-Wunused-function"
#pragma clang diagnostic ignored "-Wsign-compare"
#pragma clang diagnostic ignored "-Wimplicit-fallthrough"
#endif
#include "tsf.h"
#if defined(__clang__)
#pragma clang diagnostic pop
#endif

#define BEND_RANGE 2.0  // semitones (the General MIDI default)

static const Uint8 op_offset[9] = { 0x00, 0x01, 0x02, 0x08, 0x09, 0x0a, 0x10, 0x11, 0x12 };

// --- The chip, as the player writes to it --------------------------------------------------

static Uint8 reg[256];
static bool keyoff_written[9];  // a key went off since the last update (a retriggered note)
static Uint8 drum_hits;         // rhythm bits that went on since the last update

void midi_opl_write(unsigned int r, unsigned int value)
{
	if (r >= 0xb0 && r <= 0xb8 && (reg[r] & 0x20) && !(value & 0x20))
		keyoff_written[r - 0xb0] = true;
	if (r == 0xbd)
		drum_hits |= (Uint8)(value & ~reg[0xbd] & 0x1f);
	reg[r & 0xff] = (Uint8)value;
}

void midi_opl_clear(void)
{
	memset(reg, 0, sizeof(reg));
	memset(keyoff_written, 0, sizeof(keyoff_written));
	drum_hits = 0;
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

// --- Translator -----------------------------------------------------------------------------

void midi_translator_reset(MidiTranslator *t)
{
	for (int ch = 0; ch < 9; ++ch)
		t->voices[ch] = (MidiVoice){ .program = -1, .bend = 8192, .expression = -1 };
	memset(t->drum_on, 0, sizeof(t->drum_on));
	memset(keyoff_written, 0, sizeof(keyoff_written));
	drum_hits = 0;
}

static void emit(MidiTranslator *t, Uint32 update, Uint8 status, int data1, int data2)
{
	t->event(t->user, update, status, data1, data2);
}

void midi_translator_update(MidiTranslator *t, Uint32 update)
{
	static const int drum_note[5] = { 42, 49, 45, 38, 36 };  // bits 0-4: hi-hat, cymbal, tom, snare, bass drum
	const bool rhythm = (reg[0xbd] & 0x20) != 0;

	for (int ch = 0; ch < 9; ++ch)
	{
		MidiVoice *v = &t->voices[ch];
		const bool melodic = !(rhythm && ch >= 6);
		const bool key = melodic && (reg[0xb0 + ch] & 0x20) != 0;
		const double pitch = channel_pitch(ch);
		const int level = channel_level(ch);

		const bool restart = key && (!v->on || keyoff_written[ch] || fabs(pitch - v->note_pitch) > BEND_RANGE);
		if (v->on && (!key || restart))
		{
			emit(t, update, 0x80 | ch, v->note, 0);
			MidiInstrumentUse *u = &t->use[v->inst & 0xff];
			u->seconds += (update - v->started) / 69.5;
			v->on = false;
		}
		if (restart && pitch > 0)
		{
			const int inst = lds_channel_sound[ch];
			const int program = instrument_program(inst);
			if (program != v->program)
			{
				emit(t, update, 0xc0 | ch, program, -1);
				v->program = program;
			}
			if (v->bend != 8192)
			{
				emit(t, update, 0xe0 | ch, 0, 64);
				v->bend = 8192;
			}
			if (v->expression != 127)
			{
				emit(t, update, 0xb0 | ch, 11, 127);
				v->expression = 127;
			}
			const int transpose = instrument_transpose(inst);
			v->note = SDL_clamp((int)lround(pitch) + transpose, 0, 127);
			v->note_pitch = v->note - transpose;
			v->inst = inst;
			v->started = update;
			v->start_level = level;
			v->on = true;
			emit(t, update, 0x90 | ch, v->note, SDL_max(1, level_to_midi(level, 0) * instrument_velocity(inst) / 127));

			MidiInstrumentUse *u = &t->use[inst & 0xff];
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
				emit(t, update, 0xe0 | ch, bend & 0x7f, bend >> 7);
				v->bend = bend;
			}
			const int expression = level_to_midi(level, v->start_level);
			if (expression != v->expression)
			{
				emit(t, update, 0xb0 | ch, 11, expression);
				v->expression = expression;
			}
		}
	}

	// The rhythm section's drums.
	for (int d = 0; d < 5; ++d)
	{
		const bool hit = rhythm && (drum_hits & (1 << d));
		const bool held = rhythm && (reg[0xbd] & (1 << d));
		if (t->drum_on[d] && (hit || !held))
		{
			emit(t, update, 0x80 | MIDI_DRUM_CHANNEL, drum_note[d], 0);
			t->drum_on[d] = false;
		}
		if (hit)
		{
			const int ch = d == 4 ? 6 : (d == 0 || d == 3) ? 7 : 8;  // the channels the drums use
			emit(t, update, 0x90 | MIDI_DRUM_CHANNEL, drum_note[d], level_to_midi(channel_level(ch), 0));
			t->drum_on[d] = true;
		}
	}

	memset(keyoff_written, 0, sizeof(keyoff_written));
	drum_hits = 0;
}

void midi_translator_end(MidiTranslator *t, Uint32 update)
{
	static const int drum_note[5] = { 42, 49, 45, 38, 36 };
	for (int ch = 0; ch < 9; ++ch)
		if (t->voices[ch].on)
		{
			emit(t, update, 0x80 | ch, t->voices[ch].note, 0);
			t->voices[ch].on = false;
		}
	for (int d = 0; d < 5; ++d)
		if (t->drum_on[d])
		{
			emit(t, update, 0x80 | MIDI_DRUM_CHANNEL, drum_note[d], 0);
			t->drum_on[d] = false;
		}
}

// --- Live synth -----------------------------------------------------------------------------

static tsf *synth = NULL;
static bool enabled = true;
static MidiTranslator live;
static Uint32 live_update = 0;

static void live_event(void *user, Uint32 update, Uint8 status, int data1, int data2)
{
	(void)user;
	(void)update;
	const int ch = status & 0x0f;
	switch (status & 0xf0)
	{
	case 0x80:
		tsf_channel_note_off(synth, ch, data1);
		break;
	case 0x90:
		tsf_channel_note_on(synth, ch, data1, data2 / 127.0f);
		break;
	case 0xb0:
		tsf_channel_midi_control(synth, ch, data1, data2);
		break;
	case 0xc0:
		tsf_channel_set_presetnumber(synth, ch, data1, ch == MIDI_DRUM_CHANNEL);
		break;
	case 0xe0:
		tsf_channel_set_pitchwheel(synth, ch, data1 | (data2 << 7));
		break;
	}
}

static void prepare_channels(void)
{
	for (int ch = 0; ch < 16; ++ch)
		tsf_channel_set_presetnumber(synth, ch, 0, ch == MIDI_DRUM_CHANNEL);
	for (int ch = 0; ch < 16; ++ch)
		tsf_channel_set_pitchrange(synth, ch, (float)BEND_RANGE);
}

#define DEFAULT_SOUNDFONT "GeneralUser-GS"

static int output_rate = 0;
static char soundfont_now[64] = "";  // the one the music plays through

// The soundfonts folder: beside the game's data (with the default SoundFont in it), else with the
// program's resources.
static const char *soundfont_dir(void)
{
	static char dir[1024] = "";
	if (dir[0] == '\0')
	{
		char path[1100];
		snprintf(dir, sizeof(dir), "%s/../soundfonts", data_dir());
		snprintf(path, sizeof(path), "%s/" DEFAULT_SOUNDFONT ".sf2", dir);
		if (!SDL_GetPathInfo(path, NULL))
		{
			char resources[1024];
			SDL_strlcpy(dir, tyr3d_resource_dir("TYR3D_SOUNDFONT_DIR", TYR3D_SOUNDFONT_DIR, "soundfonts", resources, sizeof(resources)),
			            sizeof(dir));
		}
	}
	return dir;
}

enum { MAX_SOUNDFONTS = 32 };
static char soundfont_names[MAX_SOUNDFONTS][64];
static int soundfont_count = -1;

static int compare_names(const void *a, const void *b)
{
	return SDL_strcasecmp((const char *)a, (const char *)b);
}

static void find_soundfonts(void)
{
	soundfont_count = 0;
	int count = 0;
	char **files = SDL_GlobDirectory(soundfont_dir(), "*.sf2", SDL_GLOB_CASEINSENSITIVE, &count);
	for (int i = 0; files != NULL && i < count && soundfont_count < MAX_SOUNDFONTS; ++i)
	{
		const char *name = SDL_strrchr(files[i], '/') != NULL ? SDL_strrchr(files[i], '/') + 1 : files[i];
		const size_t n = strlen(name);
		if (n <= 4 || n - 4 >= sizeof(soundfont_names[0]))
			continue;
		memcpy(soundfont_names[soundfont_count], name, n - 4);
		soundfont_names[soundfont_count++][n - 4] = '\0';
	}
	SDL_free(files);
	qsort(soundfont_names, (size_t)soundfont_count, sizeof(soundfont_names[0]), compare_names);
}

int music_midi_soundfont_count(void)
{
	if (soundfont_count < 0)
		find_soundfonts();
	return soundfont_count;
}

const char *music_midi_soundfont_name(int i)
{
	return i >= 0 && i < music_midi_soundfont_count() ? soundfont_names[i] : "";
}

const char *music_midi_soundfont(void)
{
	return soundfont_now;
}

// A SoundFont loaded for output, ready to play (NULL if it can't be read).
static tsf *load_soundfont(const char *file)
{
	tsf *font = tsf_load_filename(file);
	if (font == NULL)
		return NULL;
	tsf_set_output(font, TSF_MONO, output_rate, -8.0f);  // about as loud as the emulated chip
	tsf_set_max_voices(font, 96);
	return font;
}

bool music_midi_init(int sample_rate)
{
	if (synth != NULL)
		return true;
	output_rate = sample_rate;

	char path[1024];
	const char *file = SDL_getenv("TYR3D_SOUNDFONT");
	if (file != NULL)
		synth = load_soundfont(file);
	else
	{
		// The one chosen, else the default, else any there is.
		const char *names[3] = { settings3d.soundfont, DEFAULT_SOUNDFONT, music_midi_soundfont_name(0) };
		for (int i = 0; i < 3 && synth == NULL; ++i)
		{
			if (names[i][0] == '\0')
				continue;
			snprintf(path, sizeof(path), "%s/%s.sf2", soundfont_dir(), names[i]);
			if ((synth = load_soundfont(path)) != NULL)
				SDL_strlcpy(soundfont_now, names[i], sizeof(soundfont_now));
		}
		file = path;
	}
	if (synth == NULL)
	{
		printf("music: no SoundFont (%s); the music plays on the emulated OPL chip\n", file);
		return false;
	}
	prepare_channels();
	midi_translator_reset(&live);
	live.event = live_event;
	printf("music: MIDI through %s\n", file);
	return true;
}

bool music_midi_use(const char *name)
{
	const char *want = name != NULL && name[0] != '\0' ? name : DEFAULT_SOUNDFONT;
	if (output_rate == 0 || SDL_getenv("TYR3D_SOUNDFONT") != NULL)
		return false;  // (no sound yet, or a run's own)
	if (synth != NULL && SDL_strcasecmp(want, soundfont_now) == 0)
		return true;
	char path[1100];
	snprintf(path, sizeof(path), "%s/%s.sf2", soundfont_dir(), want);
	tsf *next = load_soundfont(path);
	if (next == NULL)
	{
		printf("music: can't load the SoundFont %s\n", path);
		return false;
	}
	loudness_lock();
	tsf *old = synth;
	synth = next;
	prepare_channels();
	midi_translator_reset(&live);  // (the notes sounding now start again on it)
	live.event = live_event;
	opl_write_hook = midi_opl_write;
	loudness_unlock();
	if (old != NULL)
		tsf_close(old);
	SDL_strlcpy(soundfont_now, want, sizeof(soundfont_now));
	printf("music: MIDI through %s\n", path);
	return true;
}

bool music_midi_available(void)
{
	return synth != NULL;
}

static SDL_AtomicInt pending_reset;

void music_midi_enable(bool on)
{
	if (on != enabled)
		SDL_SetAtomicInt(&pending_reset, 1);  // the notes sounding now start again on the synth
	enabled = on;
}

bool music_midi_active(void)
{
	return synth != NULL && enabled;
}

void music_midi_update(void)
{
	if (SDL_GetAtomicInt(&pending_reset))
	{
		SDL_SetAtomicInt(&pending_reset, 0);
		tsf_note_off_all(synth);
		midi_translator_reset(&live);
	}
	midi_translator_update(&live, live_update++);
}

void music_midi_render(Sint16 *samples, int count)
{
	tsf_render_short(synth, samples, count, 0);
}

void music_midi_reset(void)
{
	if (synth == NULL)
		return;
	tsf_note_off_all(synth);
	midi_translator_reset(&live);
	midi_opl_clear();
}
