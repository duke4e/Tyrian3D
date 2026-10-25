/*
 * Tyrian3D: the music measured for the jukebox's visuals. See musicviz.h.
 */
#include "musicviz.h"

#include "lds_play.h"
#include "loudness.h"
#include "music_midi.h"
#include "opl.h"

#include <math.h>
#include <stdio.h>
#include <string.h>

#define RING 16384        // the output's samples kept (a power of two)
#define FFT_N 2048        // the spectrum's window (46 ms at 44.1 kHz)
#define FFT_BITS 11
#define HOP 512           // the spectrum is measured every so many samples (86 times a second)
#define SNAPSHOTS 128     // the chip's states kept (1.8 s of the player's updates)
#define UPDATE_RATE 69.5  // the player's updates a second (loudness.c)
#define SILENT_DB 54.0    // a note this far below full level has faded out (as music_midi.c's)

// How far behind the newest sample the output is heard: the device's buffer (1024 samples) and
// about as much queued before it.
#define LATENCY_SAMPLES 2048

static const Uint8 op_offset[9] = { 0x00, 0x01, 0x02, 0x08, 0x09, 0x0a, 0x10, 0x11, 0x12 };

/* --- The audio thread's side --------------------------------------------------------------- */

static Sint16 ring[RING];
static SDL_AtomicU32 written;    // samples fed so far (wrapping)
static SDL_SpinLock timing_lock;
static Uint32 timing_written;    // (under the lock) the samples fed by the last feed ...
static Uint64 timing_ns;         // ... and when

typedef struct
{
	Uint32 at;                         // the sample it belongs to (counted as written)
	Uint32 notes[MUSICVIZ_CHANNELS];   // notes started so far
	float level[MUSICVIZ_CHANNELS];    // amplitude, 0-1
	float pitch[MUSICVIZ_CHANNELS];    // a MIDI note number, 0 none
	Uint8 key[MUSICVIZ_CHANNELS];
	Uint8 midinst[MUSICVIZ_CHANNELS];  // the instrument's MIDI program (128 and up: a drum)
	bool midi;
} ChipSnapshot;

static ChipSnapshot snapshots[SNAPSHOTS];
static SDL_AtomicU32 snapshot_count;

// (The audio thread's own.)
static Uint32 chip_updates;
static Uint32 lds_notes_seen[MUSICVIZ_CHANNELS], notes[MUSICVIZ_CHANNELS];
static Uint32 started_at[MUSICVIZ_CHANNELS], off_at[MUSICVIZ_CHANNELS];
static double off_db[MUSICVIZ_CHANNELS];
static bool key_was[MUSICVIZ_CHANNELS];

// The chip's envelope rates as dB a second (0 to 96 dB in 39.28 s at the effective rate 4, twice as
// fast every 4).
static double rate_db_per_second(int rate, int rate_offset)
{
	return 96 / (39.28 * pow(2, -(SDL_min(rate * 4 + rate_offset, 60) - 4) / 4.0));
}

void musicviz_chip(int offset)
{
	const Bit8u *r = adlib_registers();
	const Uint32 n = SDL_GetAtomicU32(&snapshot_count);
	ChipSnapshot *s = &snapshots[n % SNAPSHOTS];
	s->at = SDL_GetAtomicU32(&written) + (Uint32)offset;
	s->midi = music_midi_active();
	for (int ch = 0; ch < MUSICVIZ_CHANNELS; ++ch)
	{
		const bool key = (r[0xb0 + ch] & 0x20) != 0;
		if (lds_channel_notes[ch] != lds_notes_seen[ch] || (key && !key_was[ch]))
		{
			notes[ch] += SDL_max(1u, SDL_min(lds_channel_notes[ch] - lds_notes_seen[ch], 4u));
			lds_notes_seen[ch] = lds_channel_notes[ch];
			started_at[ch] = chip_updates;
		}
		const int fnum = r[0xa0 + ch] | ((r[0xb0 + ch] & 3) << 8), block = (r[0xb0 + ch] >> 2) & 7;
		s->pitch[ch] = fnum > 0 ? (float)(69 + 12 * log2(fnum * 49716.0 / (double)(1 << (20 - block)) / 440)) : 0;
		// How loud: the chip's level and envelope while the key is held, then its release.
		double db;
		if (key)
		{
			db = midi_chip_channel_db(r, ch, (chip_updates - started_at[ch]) / UPDATE_RATE);
			off_db[ch] = db;
			off_at[ch] = chip_updates;
		}
		else
		{
			const int car = op_offset[ch] + 3, kcode = (block << 1) | ((fnum >> 9) & 1);
			const int rate_offset = (r[0x20 + car] & 0x10) ? kcode : kcode >> 2, rr = r[0x80 + car] & 15;
			db = off_db[ch] + (rr == 0 ? 0 : (chip_updates - off_at[ch]) / UPDATE_RATE * rate_db_per_second(rr, rate_offset));
		}
		key_was[ch] = key;
		s->key[ch] = key;
		s->level[ch] = db >= SILENT_DB ? 0.0f : (float)pow(10, -db / 20);
		s->notes[ch] = notes[ch];
		const SoundBank *sb = lds_sound(lds_channel_sound[ch]);
		s->midinst[ch] = sb != NULL ? sb->midinst : 0;
	}
	++chip_updates;
	SDL_SetAtomicU32(&snapshot_count, n + 1);
}

void musicviz_feed(const Sint16 *samples, int count)
{
	Uint32 w = SDL_GetAtomicU32(&written);
	for (int i = 0; i < count; ++i)
		ring[(w + (Uint32)i) & (RING - 1)] = samples[i];
	w += (Uint32)count;
	SDL_SetAtomicU32(&written, w);
	SDL_LockSpinlock(&timing_lock);
	timing_written = w;
	timing_ns = SDL_GetTicksNS();
	SDL_UnlockSpinlock(&timing_lock);
}

/* --- The main thread's side ---------------------------------------------------------------- */

static float window[FFT_N], cos_table[FFT_N / 2], sin_table[FFT_N / 2];
static Uint16 bit_reversed[FFT_N];
static float band_from[MUSICVIZ_BANDS], band_to[MUSICVIZ_BANDS];  // bins (fractional)
static float band_tilt[MUSICVIZ_BANDS];                           // dB added (the highs' lesser loudness)
static float window_power;
static int band_low_end, band_mid_end;  // the first band above 150 Hz, above 2 kHz

static void prepare(void)
{
	for (int i = 0; i < FFT_N; ++i)
	{
		window[i] = 0.5f - 0.5f * cosf(2 * (float)M_PI * i / FFT_N);  // Hann
		window_power += window[i];
		int r = 0;
		for (int b = 0; b < FFT_BITS; ++b)
			r |= ((i >> b) & 1) << (FFT_BITS - 1 - b);
		bit_reversed[i] = (Uint16)r;
	}
	window_power = window_power * window_power / 4;  // a full sine's peak bin: 0 dB
	for (int i = 0; i < FFT_N / 2; ++i)
	{
		cos_table[i] = cosf(2 * (float)M_PI * i / FFT_N);
		sin_table[i] = -sinf(2 * (float)M_PI * i / FFT_N);
	}
	const float rate = audioSampleRate > 0 ? (float)audioSampleRate : 44100.0f, bin_hz = rate / FFT_N;
	const float low = 30, high = 16000;
	band_low_end = band_mid_end = MUSICVIZ_BANDS;
	for (int k = 0; k < MUSICVIZ_BANDS; ++k)
	{
		const float f0 = low * powf(high / low, (float)k / MUSICVIZ_BANDS), f1 = low * powf(high / low, (float)(k + 1) / MUSICVIZ_BANDS);
		band_from[k] = f0 / bin_hz;
		band_to[k] = f1 / bin_hz;
		// +4.5 dB an octave above 1 kHz and below it: music's highs are much quieter than its lows.
		band_tilt[k] = 4.5f * log2f(sqrtf(f0 * f1) / 1000.0f);
		if (f0 >= 150 && band_low_end == MUSICVIZ_BANDS)
			band_low_end = k;
		if (f0 >= 2000 && band_mid_end == MUSICVIZ_BANDS)
			band_mid_end = k;
	}
}

static void fft(float *re, float *im)
{
	for (int i = 0; i < FFT_N; ++i)
	{
		const int j = bit_reversed[i];
		if (j > i)
		{
			float t = re[i];
			re[i] = re[j];
			re[j] = t;
			t = im[i];
			im[i] = im[j];
			im[j] = t;
		}
	}
	for (int size = 2; size <= FFT_N; size *= 2)
	{
		const int half = size / 2, step = FFT_N / size;
		for (int start = 0; start < FFT_N; start += size)
			for (int k = 0; k < half; ++k)
			{
				const float wr = cos_table[k * step], wi = sin_table[k * step];
				const int a = start + k, b = a + half;
				const float tr = re[b] * wr - im[b] * wi, ti = re[b] * wi + im[b] * wr;
				re[b] = re[a] - tr;
				im[b] = im[a] - ti;
				re[a] += tr;
				im[a] += ti;
			}
	}
}

// The power between two fractional bins, per bin (a band narrower than a bin: where it lies).
static float band_power(const float *power, float from, float to)
{
	if (to - from < 1.0f)
	{
		const float at = SDL_clamp((from + to) / 2, 1.0f, FFT_N / 2 - 2.0f);
		const int i = (int)at;
		return power[i] + (power[i + 1] - power[i]) * (at - i);
	}
	const int i0 = SDL_max(1, (int)ceilf(from)), i1 = SDL_min(FFT_N / 2 - 1, (int)floorf(to));
	float sum = 0;
	for (int i = i0; i <= i1; ++i)
		sum += power[i];
	return i1 >= i0 ? sum / (i1 - i0 + 1) : 0;
}

// A loudness's reference: rising quickly to the loudest of late, falling slowly, never under a floor.
typedef struct
{
	float db;
} Reference;

static void follow(Reference *r, float db, float dt, float floor_db)
{
	const float tau = db > r->db ? 0.35f : 14.0f;
	r->db += (db - r->db) * (1 - expf(-dt / tau));
	r->db = SDL_max(r->db, floor_db);
}

static float smooth_to(float shown, float target, float dt, float rise, float fall)
{
	return shown + (target - shown) * (1 - expf(-dt / (target > shown ? rise : fall)));
}

static int drum_kind(int note)
{
	switch (note)
	{
	case 35: case 36:
		return MUSICVIZ_KICK;
	case 37: case 38: case 39: case 40:
		return MUSICVIZ_SNARE;
	case 49: case 51: case 52: case 53: case 55: case 57: case 59:
		return MUSICVIZ_CYMBAL;
	case 41: case 43: case 45: case 47: case 48: case 50: case 60: case 61: case 62: case 63: case 64: case 65: case 66:
		return MUSICVIZ_TOM;
	default:
		return MUSICVIZ_HAT;
	}
}

static struct
{
	bool prepared;
	Uint32 next_hop;     // the sample the next window ends at
	bool hop_valid;
	float raw[MUSICVIZ_BANDS];  // the last window's bands, 0-1, unsmoothed
	Reference band_ref, level_ref;
	float flux_mean, flux_dev;
	float since_beat;
	float since_drum_beat;  // since a kick or a snare started (the song's own beats)
	Uint32 notes_seen[MUSICVIZ_CHANNELS];
	bool notes_valid;
	float peak_hold[MUSICVIZ_BANDS];
	float log_in;
} state;

#define BAND_RANGE_DB 46.0f   // the bands show this far below the reference
#define LEVEL_RANGE_DB 36.0f

// One window ending at the sample `end`: its spectrum and level, hop seconds after the last.
static void analyse(MusicViz *v, Uint32 end, float hop)
{
	static float re[FFT_N], im[FFT_N], power[FFT_N / 2];
	float sum = 0, peak = 0;
	for (int i = 0; i < FFT_N; ++i)
	{
		const float x = ring[(end - FFT_N + (Uint32)i) & (RING - 1)] / 32768.0f;
		sum += x * x;
		peak = SDL_max(peak, SDL_fabsf(x));
		re[i] = x * window[i];
		im[i] = 0;
	}
	fft(re, im);
	for (int i = 0; i < FFT_N / 2; ++i)
		power[i] = (re[i] * re[i] + im[i] * im[i]) / window_power;

	float db[MUSICVIZ_BANDS], loudest = -200;
	for (int k = 0; k < MUSICVIZ_BANDS; ++k)
	{
		db[k] = 10 * log10f(band_power(power, band_from[k], band_to[k]) + 1e-12f) + band_tilt[k];
		loudest = SDL_max(loudest, db[k]);
	}
	follow(&state.band_ref, loudest, hop, -62.0f);
	const float rms_db = 10 * log10f(sum / FFT_N + 1e-12f);
	follow(&state.level_ref, rms_db, hop, -52.0f);

	// The bands against the reference; how much they rose since the last window (onsets, the lows
	// counting twice).
	float flux = 0, weights = 0;
	for (int k = 0; k < MUSICVIZ_BANDS; ++k)
	{
		const float x = SDL_clamp((db[k] - (state.band_ref.db - BAND_RANGE_DB)) / BAND_RANGE_DB, 0.0f, 1.0f);
		const float value = powf(x, 1.45f);  // (the loud standing out)
		const float w = k < band_low_end ? 2.0f : 1.0f;
		if (state.hop_valid)
			flux += SDL_max(0.0f, value - state.raw[k]) * w;
		weights += w;
		state.raw[k] = value;
		v->bands[k] = smooth_to(v->bands[k], value, hop, 0.018f, 0.14f);
		if (v->bands[k] >= v->peaks[k])
		{
			v->peaks[k] = v->bands[k];
			state.peak_hold[k] = 0.45f;
		}
		else if ((state.peak_hold[k] -= hop) < 0)
			v->peaks[k] = SDL_max(v->bands[k], v->peaks[k] - hop * 0.9f);
	}
	flux /= weights;
	state.hop_valid = true;

	const float level = SDL_clamp((rms_db - (state.level_ref.db - LEVEL_RANGE_DB)) / LEVEL_RANGE_DB, 0.0f, 1.0f);
	v->level = smooth_to(v->level, level, hop, 0.02f, 0.2f);
	v->peak = peak;
	float lows = 0, mids = 0, highs = 0;
	for (int k = 0; k < MUSICVIZ_BANDS; ++k)
		*(k < band_low_end ? &lows : k < band_mid_end ? &mids : &highs) += v->bands[k];
	v->bass = lows / SDL_max(band_low_end, 1);
	v->mid = mids / SDL_max(band_mid_end - band_low_end, 1);
	v->high = highs / SDL_max(MUSICVIZ_BANDS - band_mid_end, 1);

	// Beats: a rise well above the usual (when the song plays no drums of its own).
	v->flux = SDL_clamp(flux * 6, 0.0f, 1.0f);
	const bool onset = flux > state.flux_mean + 2.2f * state.flux_dev + 0.012f;
	state.flux_mean += (flux - state.flux_mean) * (1 - expf(-hop / 0.6f));
	state.flux_dev += (SDL_fabsf(flux - state.flux_mean) - state.flux_dev) * (1 - expf(-hop / 0.6f));
	state.since_beat += hop;
	if (onset && state.since_beat > 0.22f && state.since_drum_beat > 3.0f)
	{
		v->beat = 1;
		++v->beats;
		state.since_beat = 0;
	}
}

static void read_channels(MusicViz *v, Uint32 heard, float dt)
{
	const Uint32 count = SDL_GetAtomicU32(&snapshot_count);
	const ChipSnapshot *found = NULL;
	for (Uint32 back = 1; back <= SDL_min(count, (Uint32)SNAPSHOTS - 8); ++back)
	{
		const ChipSnapshot *s = &snapshots[(count - back) % SNAPSHOTS];
		if ((Sint32)(heard - s->at) >= 0)
		{
			found = s;
			break;
		}
	}
	ChipSnapshot snap;
	if (found != NULL)
		snap = *found;
	const bool fresh = found != NULL && audioSampleRate > 0 && (Sint32)(heard - snap.at) < audioSampleRate / 4;
	v->notes_new = 0;
	v->midi = fresh && snap.midi;
	for (int d = 0; d < MUSICVIZ_DRUM_KINDS; ++d)
		v->drums[d] = SDL_max(0.0f, v->drums[d] - dt / 0.3f);
	state.since_drum_beat += dt;
	for (int ch = 0; ch < MUSICVIZ_CHANNELS; ++ch)
	{
		MusicVizChannel *c = &v->channels[ch];
		c->flash = SDL_max(0.0f, c->flash - dt / 0.35f);
		if (!fresh)
		{
			c->on = false;
			c->level = smooth_to(c->level, 0, dt, 0.01f, 0.08f);
			continue;
		}
		const Uint32 started = state.notes_valid ? SDL_min(snap.notes[ch] - state.notes_seen[ch], 8u) : 0;
		state.notes_seen[ch] = snap.notes[ch];
		c->notes += started;
		c->drum = (snap.midinst[ch] & 0x80) ? snap.midinst[ch] & 0x7f : 0;
		c->drum_kind = c->drum != 0 ? drum_kind(c->drum) : -1;
		c->program = snap.midinst[ch] & 0x7f;
		if (snap.pitch[ch] > 0)
			c->note = snap.pitch[ch];
		c->on = snap.key[ch] && snap.level[ch] > 0;
		c->level = smooth_to(c->level, snap.level[ch], dt, 0.008f, 0.06f);
		if (started == 0)
			continue;
		c->flash = 1;
		v->notes_new += (int)started;
		if (c->drum_kind >= 0)
		{
			v->drums[c->drum_kind] = 1;
			v->drum_hits[c->drum_kind] += started;
			if ((c->drum_kind == MUSICVIZ_KICK || c->drum_kind == MUSICVIZ_SNARE) && state.since_beat > 0.12f)
			{
				// The song's own drums are its beats.
				v->beat = 1;
				++v->beats;
				state.since_beat = 0;
				state.since_drum_beat = 0;
			}
		}
	}
	state.notes_valid = fresh;
}

static void log_viz(const MusicViz *v)
{
	printf("musicviz: song %u t %.1f live %d midi %d level %.2f peak %.2f bass %.2f mid %.2f high %.2f flux %.2f beats %u ref %.1f dB | ch",
	       song_playing + 1, v->time, v->live, v->midi, v->level, v->peak, v->bass, v->mid, v->high, v->flux, v->beats, state.band_ref.db);
	for (int ch = 0; ch < MUSICVIZ_CHANNELS; ++ch)
	{
		const MusicVizChannel *c = &v->channels[ch];
		printf(" %d:%s%.2f/%.0f/%u%s", ch, c->on ? "+" : "-", c->level, c->note, c->notes, c->drum ? "d" : "");
	}
	printf(" | drums k%u s%u h%u c%u t%u | bands", v->drum_hits[MUSICVIZ_KICK], v->drum_hits[MUSICVIZ_SNARE], v->drum_hits[MUSICVIZ_HAT],
	       v->drum_hits[MUSICVIZ_CYMBAL], v->drum_hits[MUSICVIZ_TOM]);
	for (int k = 0; k < MUSICVIZ_BANDS; k += 4)
		printf(" %.2f", v->bands[k]);
	printf("\n");
}

void musicviz_update(MusicViz *v, float dt)
{
	if (!state.prepared)
	{
		prepare();
		state.prepared = true;
	}
	dt = SDL_clamp(dt, 0.0f, 0.25f);
	v->time += dt;
	v->beat = SDL_max(0.0f, v->beat - dt / 0.25f);

	// Where the output is heard now: the last feed, behind by the latency, on since by the clock.
	Uint32 fed;
	Uint64 fed_ns;
	SDL_LockSpinlock(&timing_lock);
	fed = timing_written;
	fed_ns = timing_ns;
	SDL_UnlockSpinlock(&timing_lock);
	const Uint64 now = SDL_GetTicksNS();
	v->live = !audio_disabled && fed_ns != 0 && now - fed_ns < 500000000ull && audioSampleRate > 0;
	if (!v->live)
	{
		for (int k = 0; k < MUSICVIZ_BANDS; ++k)
		{
			v->bands[k] = smooth_to(v->bands[k], 0, dt, 0.02f, 0.3f);
			v->peaks[k] = SDL_max(v->bands[k], v->peaks[k] - dt);
		}
		v->level = smooth_to(v->level, 0, dt, 0.02f, 0.3f);
		v->bass = v->mid = v->high = v->flux = 0;
		read_channels(v, 0, dt);
		state.hop_valid = false;
		return;
	}
	const Uint32 since = (Uint32)SDL_min((now - fed_ns) * (Uint64)audioSampleRate / 1000000000ull, (Uint64)LATENCY_SAMPLES);
	const Uint32 heard = fed - LATENCY_SAMPLES + since;

	// Every window up to it (some of them, a long frame).
	if (!state.hop_valid || (Sint32)(heard - state.next_hop) > 8 * HOP || (Sint32)(heard - state.next_hop) < -4 * HOP)
		state.next_hop = heard - HOP;
	const float hop = (float)HOP / audioSampleRate;
	while ((Sint32)(heard - state.next_hop) >= 0)
	{
		analyse(v, state.next_hop, hop);
		state.next_hop += HOP;
	}
	read_channels(v, heard, dt);

	static int log_on = -1;
	if (log_on < 0)
		log_on = SDL_getenv("TYR3D_LOG_MUSICVIZ") != NULL;
	if (log_on && (state.log_in -= dt) <= 0)
	{
		state.log_in = 0.5f;
		log_viz(v);
	}
}
