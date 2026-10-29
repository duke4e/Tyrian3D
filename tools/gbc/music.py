"""The GBC songs as episode 7 plays them: each song's loop found and cut, into data/gbc/music/loops (outside git: the
ROM's content is the user's), and which songs each level plays (tools/content/gbc/build.py copies them into the
episode's content with its music.txt; src/loudness.c play_recorded_song).

The songs as songs.py renders them (data/gbc/music: 150 s of each, played by the ROM's own driver, its sound register
writes kept as <song>.json) run on: the driver plays a song once and then goes round its loop for ever. The loop is
found in the writes: the shortest period P (in driver ticks, one a frame) after which every frame's writes repeat to
the end of the log, from the earliest frame S they do. The song is cut at S + P, mono at the game's 44.1 kHz, its last
10 ms blended into the 10 ms before S, so that going back to S runs on without a click; one that never repeats within
the log is played whole and starts over. A level plays its own song; its boss song (the one its init starts after it,
the bank's other: songs.json's order) once the boss comes (event 204).

    python tools/gbc/music.py
"""
import json
import os
import sys
import wave

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gb as G  # noqa: E402

MUSIC = os.path.join(G.ROOT, 'data', 'gbc', 'music')
OUT = os.path.join(MUSIC, 'loops')
FPS = 4194304 / 70224   # driver ticks (frames) a second
RATE = 44100
BLEND = RATE // 100     # the samples blended at the loop's end
MIN_PERIOD = 4 * 60     # frames: no song loops sooner


def frames(events, total):
    """Each frame's writes as one number (a hash of the frame's (register, value) writes in order)."""
    out = [[] for _ in range(total)]
    for t, r, v in events:
        f = int(round(t * FPS))
        if f < total:
            out[f].append((r, v))
    return np.array([hash(tuple(w)) for w in out], np.int64)


def find_loop(events):
    """(S, P) in frames: the frames from S on repeat every P frames to the end of the log; None if none do."""
    total = int(round(max(t for t, _, _ in events) * FPS))
    sig = frames(events, total)
    for p in range(MIN_PERIOD, total // 2):
        same = sig[:-p] == sig[p:]
        bad = np.nonzero(~same)[0]
        s = int(bad[-1]) + 1 if len(bad) else 0
        if total - p - s >= p:  # (the period seen whole at least once after S)
            return s, p
    return None


def read_wav(path):
    with wave.open(path, 'rb') as w:
        n, ch = w.getnframes(), w.getnchannels()
        data = np.frombuffer(w.readframes(n), '<i2').astype(np.float32).reshape(-1, ch)
    return data.mean(1)


def write_wav(path, samples):
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(RATE)
        w.writeframes(np.clip(samples, -32768, 32767).astype('<i2').tobytes())


def level_songs():
    """{GBC level: (its song's file, its boss song's file or None)} from songs.json (each level's init starts its
    song, then its boss song, the next one of its bank there)."""
    index = json.load(open(os.path.join(MUSIC, 'songs.json')))
    file_of = [e.get('file') or e['same_as'] + '.wav' for e in index]
    out = {}
    for k, e in enumerate(index):
        for use in e['used_by']:
            level = int(use[1:3])
            nxt = index[k + 1] if k + 1 < len(index) else None
            boss = file_of[k + 1] if nxt and nxt['bank'] == e['bank'] and not nxt['used_by'] and not nxt['buf'] else None
            out[level] = (file_of[k], boss)
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    loops = {}
    songs = sorted({f for pair in level_songs().values() for f in pair if f})
    for f in songs:
        base = f[:-4]
        events = json.load(open(os.path.join(MUSIC, base + '.json')))
        audio = read_wav(os.path.join(MUSIC, f))
        found = find_loop(events)
        if found:
            s, p = found
            start, end = int(round(s / FPS * RATE)), int(round((s + p) / FPS * RATE))
            cut = audio[:end].copy()
            if start >= BLEND:
                ramp = np.linspace(0, 1, BLEND, dtype=np.float32)
                cut[-BLEND:] = cut[-BLEND:] * (1 - ramp) + audio[start - BLEND:start] * ramp
        else:
            start, cut = 0, audio
        write_wav(os.path.join(OUT, f), cut)
        loops[f] = start
        print(f"{f}: {'loop at %.1f s, %.1f s long' % (start / RATE, (len(cut) - start) / RATE) if found else 'no loop: whole'}"
              f" ({len(cut) / RATE:.1f} s)")
    json.dump(dict(loops=loops, levels={str(k): v for k, v in sorted(level_songs().items())}),
              open(os.path.join(OUT, 'loops.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
