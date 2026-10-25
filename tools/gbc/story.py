"""The GBC Tyrian story in the order the Full Game tells it, into data/gbc/story.json (episode 7).

The texts are plain ASCII in the ROM ('/' a new line, '|' a new page, 0 the end), each with a speaker
whose name the story screen reads from a table of 8-character names. The game is flown through its
Full Game in the emulator (each level ended at once, the ship kept alive) and the texts and names it
reads are logged: the opening (Transon's greeting at the title, the escape before the first shop),
the text after each level, and the ending.

    python tools/gbc/story.py
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gb as G  # noqa: E402
import extract as X  # noqa: E402

NAMES = 0x23f78  # NEWS, VYKROMOD, TRANSON, DOUGAN, SAVARA, JAVI, CAPTAIN, REID, TECH, STATIC, MONDUS
OUT = os.path.join(G.ROOT, 'data', 'gbc', 'story.json')


def main():
    rom = open(G.ROM, 'rb').read()
    texts = [(m.start(), m.group()[:-1].decode('ascii')) for m in re.finditer(rb'[\x20-\x7e]{40,}\x00', rom)
             if b'/' in m.group()]
    names = [rom[NAMES + 8 * k:NAMES + 8 * k + 8].decode('ascii').strip('.') for k in range(11)]

    def read(g):
        f = g.romflags()
        hit = [(a, t) for a, t in texts if (f[a:a + len(t)] & 1).sum() > len(t) // 2]
        who = [names[k] for k in range(11) if (f[NAMES + 8 * k:NAMES + 8 * k + 8] & 1).any()]
        f[:] = 0
        return hit, who
    # the opening, as boot_to_level_menu goes: the title's greeting, then the escape before the shop
    g = G.GB()
    opening = []
    g.run(200)
    for i in range(1, 2401):
        g.run(1, G.A if i % 120 < 6 else 0)
        if i == 1500:
            hit, who = read(g)
            opening += [(a, t, who[0] if who else None) for a, t in hit]
    for _ in range(10):
        g.run(4, G.A)
        g.run(56)
    hit, who = read(g)
    opening += [(a, t, who[0] if who else None) for a, t in hit]
    for j, f in [(G.B, 4), (0, 20), (G.B, 4), (0, 20), (G.DOWN, 4), (0, 10), (G.DOWN, 4), (0, 10), (G.A, 4), (0, 40)]:
        g.run(f, j)
    seen, ordered = set(), []
    for a, t, who in opening:
        if a not in seen:
            seen.add(a)
            # (the escape's screen shows the Hazudra; it is Trent's own account)
            ordered.append(dict(text=t, speaker=who if who in ('TRANSON',) else None))
    story = dict(opening=ordered, after={}, ending=[])
    level_names = X.level_names(rom)

    def start():
        g.L.gb_set_joy(g.g, G.A)
        return g.until(0x4fea, 7, 400_000_000), g.read(0xd92f)
    ok, level = start()
    while ok:
        g.run(4, 0)
        for _ in range(300):
            g.write(0xd8da, 8)
            g.run(1, 0)
        read(g)
        g.write(0xc42d, 1)  # the level ends
        for i in range(40):
            g.write(0xd8da, 8)
            g.run(30, G.A if i % 2 == 0 else 0)
        hit, who = read(g)
        speaker = who[0] if who else None
        story['after'][str(level)] = [dict(text=t, speaker=speaker) for a, t in hit]
        print(f'after {level_names[level] if level < 24 else level}: {speaker}, {len(hit)} text(s)')
        for j, f in [(G.B, 4), (0, 20), (G.B, 4), (0, 20), (G.B, 4), (0, 20), (G.DOWN, 4), (0, 10), (G.DOWN, 4),
                     (0, 10), (G.A, 4), (0, 40)]:
            g.run(f, j)
        ok, level = start()
        hit, who = read(g)
        if hit:
            story['ending'] = [dict(text=t, speaker=None) for a, t in hit]
    json.dump(story, open(OUT, 'w'), indent=1)
    print(OUT)


if __name__ == '__main__':
    main()
