"""Episode 7's GBC songs as MIDI, for the SoundFont the PC's music plays through (tools/gbc/music.py writes them beside
the songs' loops; src/music_midi.c music_midi_song_* plays them while the music plays as MIDI).

The ROM's driver writes a note's frequency only as it starts it (every NRx4 write a trigger, no vibrato, the sweep's
shift 0), so its sound register writes (songs.py's <song>.json) are its notes: a trigger is a note on, its frequency
the pitch, and it ends at the channel's next trigger, its length running out, its envelope falling to 0 or its DAC
turned off. The envelope's volume is the velocity, and where it swells or fades slowly the expression follows it.

Each of a channel's instruments (a pulse's envelope and duty, the wave's pattern) gets a part of its own, a MIDI
channel with a General MIDI program by its role (ROLES: the programs the PC songs' instruments use most); the noise
channel's hits are drums by their pitch and length. CC 111 marks the loop's start (as RPG Maker's MIDI do), and the
file's last events, all notes off, its end.
"""
import math
import statistics

TRIGGERS = {0x14: 0, 0x19: 1, 0x1e: 2, 0x23: 3}
DRUMS = 9                      # the MIDI drum channel
DIVISION = 480                 # MIDI ticks a quarter note, at 120 a minute: 960 a second
LOOP_CC = 111

# Role: (General MIDI program, channel volume). The PC songs' instruments mostly play synth basses (38, 39), saw and
# square leads (81, 80), synth brass (62), strings (48, 50) and polysynth (90).
ROLES = {
    'bass': (38, 112),         # the wave channel low (its usual part)
    'bass2': (39, 100),        # a pulse low
    'lead': (81, 96),          # held or slowly fading, loud
    'lead50': (80, 96),        # the same at 50 % duty (hollow, square)
    'pluck': (62, 92),         # short: an envelope gone within 0.35 s or notes of 0.12 s
    'pad': (50, 84),           # swelling
    'soft': (90, 84),          # held quietly (volume 6 or less: chords, arpeggios behind the lead)
}
KICK, SNARE, SNARE2, HAT, OPEN_HAT, CRASH = 36, 38, 40, 42, 46, 49
# A song's own choices, by its file and (GB channel 1-4, the instrument's signature) or GB channel: a role or a program.
SONG_PROGRAMS = {}


def note_of(freq):
    return 69 + 12 * math.log2(freq / 440)


def envelope(byte):
    """(starting volume, rising, seconds a step; 0 for none)."""
    return byte >> 4, bool(byte & 8), (byte & 7) / 64


def level_at(byte, seconds):
    v, up, step = envelope(byte)
    if not step:
        return v
    n = int(seconds / step)
    return min(15, v + n) if up else max(0, v - n)


def env_end(byte):
    """Seconds until a falling envelope reaches 0 (None if it doesn't)."""
    v, up, step = envelope(byte)
    return v * step if step and not up else (0.0 if v == 0 and not up else None)


def read_notes(events, until):
    """[(GB channel 0-3, start, end, pitch or noise byte, envelope or wave level, signature)] up to `until` s."""
    reg = [0] * 0x40
    on = [None] * 4    # each channel's sounding note: [start, end limit, pitch, env, sig]
    out = []

    def close(c, t):
        n = on[c]
        if n is not None:
            out.append((c, n[0], min(t, n[1]), n[2], n[3], n[4]))
            on[c] = None

    for t, r, v in events:
        if t >= until:
            break
        reg[r] = v
        if r in (0x12, 0x17, 0x21) and v & 0xf8 == 0:       # DAC off
            close({0x12: 0, 0x17: 1, 0x21: 3}[r], t)
        elif r == 0x1a and not v & 0x80:
            close(2, t)
        elif r in TRIGGERS and v & 0x80 and t > 0:
            c = TRIGGERS[r]
            close(c, t)
            limit = math.inf
            if c < 2:
                b = 0x10 + 5 * c
                freq = 131072 / (2048 - (reg[b + 3] | (v & 7) << 8))
                env, duty = reg[b + 2], reg[b + 1] >> 6
                if v & 0x40:
                    limit = (64 - (reg[b + 1] & 63)) / 256
                end = env_end(env)
                if end is not None:
                    limit = min(limit, end)
                on[c] = [t, t + limit, note_of(freq), env, ('p', env, duty)]
            elif c == 2:
                freq = 65536 / (2048 - (reg[0x1d] | (v & 7) << 8))
                if v & 0x40:
                    limit = (256 - reg[0x1b]) / 256
                level = (0, 1.0, 0.5, 0.25)[reg[0x1c] >> 5 & 3]
                if level and reg[0x1a] & 0x80:
                    on[c] = [t, t + limit, note_of(freq), level, ('w', bytes(reg[0x30:0x40]).hex())]
            else:
                env = reg[0x21]
                if v & 0x40:
                    limit = (64 - (reg[0x20] & 63)) / 256
                end = env_end(env)
                if end is not None:
                    limit = min(limit, end)
                on[c] = [t, t + limit, reg[0x22], env, ('n', reg[0x22])]
    for c in range(4):
        close(c, until)
    return [n for n in out if n[2] > n[1]]


def noise_hz(byte):
    shift, div = byte >> 4, byte & 7
    return 524288 / (div or 0.5) / 2 ** (shift + 1)


def drum_of(byte, seconds):
    hz = noise_hz(byte)
    if hz >= 7000:
        return OPEN_HAT if seconds >= 0.3 else HAT
    if hz >= 3500:
        return SNARE
    if hz >= 1500:
        return CRASH if seconds >= 0.4 else SNARE2
    return KICK


def role_of(c, sig, notes):
    pitches = [n[3] for n in notes]
    lengths = [n[2] - n[1] for n in notes]
    med, length = statistics.median(pitches), statistics.median(lengths)
    if len({round(p) for p in pitches}) <= 1 and length <= 0.15 and len(notes) >= 16:
        return 'kick'
    if c == 2:
        return 'bass' if med < 52 else 'lead'
    if med < 48:
        return 'bass2'
    v, up, step = envelope(sig[1])
    if up and step:
        return 'pad'
    end = env_end(sig[1])
    if (end is not None and end <= 0.35) or length <= 0.12:
        return 'pluck'
    if v <= 6:
        return 'soft'
    return 'lead50' if sig[2] == 2 else 'lead'


def transcribe(song, events, loop_start, loop_end):
    """A standard MIDI file (bytes) of the song from its start to `loop_end` s, CC 111 at `loop_start`, and its parts
    [(GB channel 1-4, role, notes)]."""
    notes = read_notes(events, loop_end)
    parts = {}
    for n in notes:
        if n[0] != 3:
            parts.setdefault((n[0], n[5]), []).append(n)
    own = SONG_PROGRAMS.get(song, {})
    channel_of, programs, free = {}, [], [ch for ch in range(16) if ch != DRUMS]
    summary = []
    for (c, sig), ns in sorted(parts.items(), key=lambda kv: (kv[0][0], -len(kv[1]))):
        role = own.get((c + 1, sig), own.get(c + 1)) or role_of(c, sig, ns)
        summary.append((c + 1, role, len(ns)))
        if role == 'kick':
            channel_of[c, sig] = None
            continue
        program, volume = ROLES[role] if isinstance(role, str) else (role, 96)
        ch = free.pop(0) if free else programs[-1][0]  # (more than 15 parts: the last shares)
        channel_of[c, sig] = (ch, role)
        programs.append((ch, program, volume))

    out = []  # (seconds, order, status, data1, data2): order puts note offs before ons at one time
    for ch, program, volume in programs:
        out += [(0, 0, 0xc0 | ch, program, None), (0, 0, 0xb0 | ch, 7, volume), (0, 0, 0xb0 | ch, 11, 127)]
    out += [(0, 0, 0xb0 | DRUMS, 7, 112)]
    for c, start, end, pitch, env, sig in notes:
        if c == 3:
            key = drum_of(pitch, end - start)
            vel = max(1, round(127 * envelope(env)[0] / 15)) if env else 64
            out += [(start, 2, 0x90 | DRUMS, key, vel), (min(end, start + 0.1), 1, 0x80 | DRUMS, key, 0)]
            continue
        part = channel_of[c, sig]
        if part is None:  # a pulse played as a drum
            vel = max(1, round(127 * envelope(env)[0] / 15))
            out += [(start, 2, 0x90 | DRUMS, KICK, vel), (min(end, start + 0.1), 1, 0x80 | DRUMS, KICK, 0)]
            continue
        ch, role = part
        key = max(0, min(127, round(pitch)))
        if c == 2:
            vel = round(112 * env)
            out += [(start, 2, 0x90 | ch, key, vel), (end, 1, 0x80 | ch, key, 0)]
            continue
        v, up, step = envelope(env)
        follow = step and role not in ('pluck', 'bass', 'bass2') and (up or (v * step) > 0.35)
        if follow:
            levels = [level_at(env, k * step) for k in range(int((end - start) / step) + 1)]
            peak = max(levels) or 1
            out.append((start, 2, 0xb0 | ch, 11, round(127 * levels[0] / peak)))
            out.append((start, 3, 0x90 | ch, key, max(1, round(127 * peak / 15))))
            for k in range(1, len(levels)):
                if levels[k] != levels[k - 1]:
                    out.append((start + k * step, 4, 0xb0 | ch, 11, round(127 * levels[k] / peak)))
        else:
            out.append((start, 3, 0x90 | ch, key, max(1, round(127 * max(v, 1) / 15))))
        out.append((end, 1, 0x80 | ch, key, 0))
    out.append((loop_start, 0, 0xb0, LOOP_CC, 0))
    used = sorted({ch for ch, _, _ in programs} | {DRUMS})
    out += [(loop_end, 5, 0xb0 | ch, 123, 0) for ch in used]
    out.sort(key=lambda e: (e[0], e[1]))
    hits = sum(1 for n in notes if n[0] == 3)
    return smf(out), summary + ([(4, 'drums', hits)] if hits else [])


def smf(events):
    """Format 0, 120 a minute, DIVISION a quarter: (seconds, _, status, d1, d2 or None for a 2-byte message)."""
    def vlq(n):
        b = [n & 0x7f]
        while n > 0x7f:
            n >>= 7
            b.insert(0, 0x80 | (n & 0x7f))
        return bytes(b)
    track, last = bytearray(), 0
    track += b'\x00\xff\x51\x03\x07\xa1\x20'   # 500000 us a quarter
    for t, _, status, d1, d2 in events:
        tick = round(t * DIVISION * 2)
        track += vlq(max(0, tick - last)) + bytes([status, d1] + ([] if d2 is None else [d2]))
        last = max(last, tick)
    track += b'\x00\xff\x2f\x00'
    return (b'MThd' + (6).to_bytes(4, 'big') + (0).to_bytes(2, 'big') + (1).to_bytes(2, 'big')
            + DIVISION.to_bytes(2, 'big') + b'MTrk' + len(track).to_bytes(4, 'big') + bytes(track))
