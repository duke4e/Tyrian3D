"""What the GBC Tyrian shop offers before each level of the Full Game, into data/gbc/shop.json (episode 7).

The shop's Items menu has six lists (Ship, Weapon, Engine, Shield, SideA, SideB); each shows the items unlocked so
far, by name, from the ROM's tables of 8-character names (one per kind). The game is flown through its Full Game in
the emulator as story.py flies it (each level ended at once, the ship kept alive); at every shop each list is opened
and the names the menu reads (the ROM's read flags) are its offer.

    python tools/gbc/shop.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gb as G  # noqa: E402
import extract as X  # noqa: E402

OUT = os.path.join(G.ROOT, 'data', 'gbc', 'shop.json')
# The name tables (ROM offsets of their first names) and their lengths; the menus in the Items list's order
TABLES = {'side': (b'None    Single  Dual', 10), 'shield': (b'Low     Hard', 7), 'engine': (b'Std     Light', 6),
          'weapon': (b'Pulse   Multi', 25), 'ship': (b'Talon   Micros', 7)}
MENUS = ['ship', 'weapon', 'engine', 'shield', 'side', 'side']   # SideA, SideB: the same names


def names(rom):
    out = {}
    for kind, (key, n) in TABLES.items():
        o = rom.find(key)
        out[kind] = (o, [rom[o + 8 * k:o + 8 * k + 8].decode('ascii').strip() for k in range(n)])
    return out


def offer(g, tables):
    """From the shop's Level menu: each Items list's names. Returns {menu: [names]}; leaves it at the Level menu."""
    def go(seq):
        for j, f in seq:
            g.run(f, j)
    go([(0, 20), (G.B, 4), (0, 30), (G.UP, 4), (0, 20), (G.UP, 4), (0, 20), (G.A, 4), (0, 40)])  # Main > Items
    out = {}
    for k, menu in enumerate(['ship', 'weapon', 'engine', 'shield', 'sideA', 'sideB']):
        kind = MENUS[k]
        o, ns = tables[kind]
        f = g.romflags()
        f[:] = 0
        go([(G.A, 4), (0, 60)] + [(G.DOWN, 4), (0, 12)] * 28)  # (down the list: a long one scrolls)
        read = [ns[i] for i in range(len(ns)) if (f[o + 8 * i:o + 8 * i + 8] & 1).sum() >= 4]
        out[menu] = read
        go([(G.B, 4), (0, 30), (G.DOWN, 4), (0, 20)])
    # back: Items > Main > Start (Level)
    go([(G.B, 4), (0, 30), (G.DOWN, 4), (0, 20), (G.DOWN, 4), (0, 20), (G.A, 4), (0, 40)])
    return out


def main():
    rom = open(G.ROM, 'rb').read()
    tables = names(rom)
    level_names = X.level_names(rom)
    g = X.boot_to_level_menu()
    shops = []

    def start():
        g.L.gb_set_joy(g.g, G.A)
        return g.until(0x4fea, 7, 400_000_000), g.read(0xd92f)
    # the first shop, then after each level the next
    first = offer(g, tables)
    ok, level = start()
    shops.append(dict(before=level, offer=first))
    print(f'before {level_names[level]}: {first}')
    while ok:
        g.run(4, 0)
        for _ in range(300):
            g.write(0xd8da, 8)
            g.run(1, 0)
        g.write(0xc42d, 1)  # the level ends
        for i in range(40):
            g.write(0xd8da, 8)
            g.run(30, G.A if i % 2 == 0 else 0)
        # (story.py's way to the Level menu)
        for j, f in [(G.B, 4), (0, 20), (G.B, 4), (0, 20), (G.B, 4), (0, 20), (G.DOWN, 4), (0, 10), (G.DOWN, 4),
                     (0, 10), (G.A, 4), (0, 40)]:
            g.run(f, j)
        got = offer(g, tables)
        ok, nxt = start()
        if not ok:
            break
        shops.append(dict(after=level, before=nxt, offer=got))
        print(f'before {level_names[nxt] if nxt < 24 else nxt}: {got}', flush=True)
        level = nxt
    json.dump(dict(names={k: v[1] for k, v in tables.items()}, shops=shops), open(OUT, 'w'), indent=1)
    print(OUT)


if __name__ == '__main__':
    main()
