"""Renders the GBC Tyrian music to data/gbc/music (outside git: the ROM's content is the user's).

The songs are found in the code: each level's init sets its song ($c445, decompressed with $1da8 and
started with $1a0a) and its boss song; five more go through the second buffer ($1d9e / $1a10). Each song
is played by the ROM's own driver in the emulator, ticked once a frame ($1a5f) with nothing else running,
and the sound register writes are synthesised (apu.py). Duplicates (the same tune in several banks)
are rendered once.

    python tools/gbc/songs.py [--seconds 150]
"""
import argparse
import ctypes
import hashlib
import json
import os
import re
import sys
import wave

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gb as G
import apu

OUT = os.path.join(G.ROOT, 'data', 'gbc', 'music')
FPS = 4194304 / 70224


def find_songs(rom):
    songs = []
    for m in re.finditer(rb'\x3e(.)\xea\x45\xc4\x3e(.)\xea\x46\xc4', rom, re.S):
        bank = m.start() // 0x4000
        songs.append({'bank': bank, 'ptr': m.group(1)[0] | (m.group(2)[0] << 8), 'buf': 0})
    for m in re.finditer(rb'\x11(..)\xd5\xcd\x9e\x1d', rom, re.S):
        bank = m.start() // 0x4000
        songs.append({'bank': bank, 'ptr': int.from_bytes(m.group(1), 'little'), 'buf': 1})
    seen, out = set(), []
    for s in songs:
        k = (s['bank'], s['ptr'])
        if k not in seen:
            seen.add(k)
            out.append(s)
    return out


def play(song, ticks):
    g = G.GB()
    raw = open(os.path.join(G.ROOT, 'data', 'gbc', 'cache', 'levelmenu.state'), 'rb').read()
    g.load(ctypes.create_string_buffer(raw, len(raw)))
    g.write(0xffff, 0)  # no interrupts: only the driver runs
    sp = g.reg(1) - 2
    g.write(sp, song['ptr'] & 255); g.write(sp + 1, song['ptr'] >> 8)
    g.set_reg(1, sp)
    g.call(0x1d9e if song['buf'] else 0x1da8, song['bank'])
    g.set_reg(1, sp + 2)
    io = g.io()
    # the registers as the menu left them (triggers cleared), then the song's start
    events = [(0.0, r, int(io[r]) & (0x7f if r in (0x14, 0x19, 0x1e, 0x23) else 0xff))
              for r in [0x26, 0x24, 0x25] + list(range(0x10, 0x24)) + list(range(0x30, 0x40))]
    g.snd_enable(True)
    g.call(0x1a10 if song['buf'] else 0x1a0a)
    events += [(0.0, int(e['reg']), int(e['val'])) for e in g.snd_log()]
    for t in range(ticks):
        g.snd_enable(True)
        g.call(0x1a5f)
        log = g.snd_log()
        events += [(t / FPS, int(e['reg']), int(e['val'])) for e in log]
    return events


def write_wav(path, samples, rate):
    pcm = (np.clip(samples, -1, 1) * 32767).astype('<i2')
    with wave.open(path, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(rate)
        w.writeframes(pcm.tobytes())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seconds', type=float, default=150)
    a = ap.parse_args()
    rom = open(G.ROM, 'rb').read()
    os.makedirs(OUT, exist_ok=True)
    levels = json.load(open(os.path.join(G.ROOT, 'data', 'gbc', 'levels.json')))
    where = {}
    for lv in levels.values():
        where.setdefault((lv['bank'], lv['song']), []).append(f"L{lv['level']:02d} {lv['name']}")
    songs = find_songs(rom)
    ticks = int(a.seconds * FPS)
    index, hashes = [], {}
    for s in songs:
        ev = play(s, ticks)
        h = hashlib.sha1(repr([(round(t * FPS), r, v) for t, r, v in ev[:4000]]).encode()).hexdigest()[:12]
        uses = where.get((s['bank'], s['ptr']), [])
        entry = {'bank': s['bank'], 'ptr': s['ptr'], 'buf': s['buf'], 'events': len(ev), 'hash': h, 'used_by': uses}
        if h in hashes:
            entry['same_as'] = hashes[h]
        else:
            name = f"song{len(hashes) + 1:02d}_{s['bank']:02x}_{s['ptr']:04x}"
            hashes[h] = name
            entry['file'] = name + '.wav'
            if ev:
                write_wav(os.path.join(OUT, name + '.wav'), apu.render(ev, a.seconds), 44100)
            json.dump(ev, open(os.path.join(OUT, name + '.json'), 'w'))
        index.append(entry)
        print(f"{s['bank']:02x}:{s['ptr']:04x} buf{s['buf']} events {len(ev):6d} {entry.get('file') or 'same as ' + entry['same_as']} {', '.join(uses)}")
    json.dump(index, open(os.path.join(OUT, 'songs.json'), 'w'), indent=1)
    print(len(songs), 'song pointers,', len(hashes), 'distinct')


if __name__ == '__main__':
    main()
