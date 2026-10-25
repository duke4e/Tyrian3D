"""Extracts the GBC Tyrian levels into data/gbc/levels (outside git: the ROM's content is the user's).

For each of the 24 levels: the full map (blocks of 16x16, 11 per row) as PNG and JSON, its tiles and
palettes, the sprite tiles with the palettes the game used for them, and a screenshot.
The game is run in the emulator (gbemu.c): boot, the menus, then each level is started through the
level dispatcher (bank 7:4fea reads the level from $d92f) and its init routine is read for the map.

    python tools/gbc/extract.py [--levels 1,2,...]
"""
import argparse
import ctypes
import json
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gb as G

OUT = os.path.join(G.ROOT, 'data', 'gbc')
CACHE = os.path.join(OUT, 'cache')
ROW = 11          # blocks per map row (176 px)
BLOCK_TILE0 = 26  # block b uses BG tiles 26+4b .. 26+4b+3 (TL, BL, TR, BR)


def rom_off(bank, addr):
    return addr if addr < 0x4000 else bank * 0x4000 + addr - 0x4000


def level_names(rom):
    o = rom.find(b'New Game')
    names = [rom[o + 8 * i:o + 8 * i + 8].decode('ascii').strip() for i in range(24)]
    return names + ['Level24']


def load_state(g, path):
    raw = open(path, 'rb').read()
    g.load(ctypes.create_string_buffer(raw, len(raw)))


def boot_to_level_menu():
    """Power on, skip the intro (A), New Game / 1 player / Full Game / Normal, the story, then
    Start > Level in the shop. Cached in data/gbc/cache/levelmenu.state."""
    path = os.path.join(CACHE, 'levelmenu.state')
    g = G.GB()
    if os.path.exists(path):
        load_state(g, path)
        return g
    g.run(200)
    for i in range(1, 2401):
        g.run(1, G.A if i % 120 < 6 else 0)
    for _ in range(10):
        g.run(4, G.A); g.run(56)
    for j, f in [(G.B, 4), (0, 20), (G.B, 4), (0, 20), (G.DOWN, 4), (0, 10), (G.DOWN, 4), (0, 10), (G.A, 4), (0, 40)]:
        g.run(f, j)
    os.makedirs(CACHE, exist_ok=True)
    open(path, 'wb').write(g.save().raw)
    return g


def start_level(level):
    """A machine just past the level's init (the dispatcher's level replaced by `level`)."""
    g = boot_to_level_menu()
    g.L.gb_set_joy(g.g, G.A)
    if not g.until(0x4fea, 7, 50_000_000):
        raise RuntimeError('level dispatcher not reached')
    g.write(0xd92f, level)
    g.ww_enable(0xc440, 0xc45f)
    g.run(4, G.A)
    bank, init = g.read(0xc45b), g.read(0xc45e) | (g.read(0xc45f) << 8)
    g.run(150)
    first = {}
    for w in g.ww_log():
        first.setdefault(int(w['addr']), int(w['val']))
    word = lambda lo: first.get(lo, 0) | (first.get(lo + 1, 0) << 8)
    consts = {'map': word(0xc449), 'block_pal': word(0xc44d), 'events_pos': word(0xc455),
              'events': word(0xc457), 'song': word(0xc445)}
    return g, bank, init, consts


def tile_px(vram, addr):
    t = np.frombuffer(bytes(vram[addr:addr + 16]), np.uint8).reshape(8, 2)
    lo = np.unpackbits(t[:, 0]).reshape(8, 8)
    hi = np.unpackbits(t[:, 1]).reshape(8, 8)
    return lo | (hi << 1)


def bg_tile_addr(index):
    """BG tiles use the $8800 addressing (LCDC bit 4 clear in the levels)."""
    return 0x1000 + (index - 256 if index > 127 else index) * 16


def render_map(rows, block_pal, vram, pal):
    h = len(rows)
    img = np.zeros((h * 16, ROW * 16, 3), np.uint8)
    cache = {}
    for y, row in enumerate(rows):
        for x, b in enumerate(row):
            if b not in cache:
                blk = np.zeros((16, 16, 3), np.uint8)
                p = pal[block_pal[b] & 7] if b < len(block_pal) else pal[0]
                t0 = BLOCK_TILE0 + 4 * b
                for k, (dx, dy) in enumerate([(0, 0), (0, 8), (8, 0), (8, 8)]):
                    blk[dy:dy + 8, dx:dx + 8] = p[tile_px(vram, bg_tile_addr((t0 + k) & 255))]
                cache[b] = blk
            img[y * 16:y * 16 + 16, x * 16:x * 16 + 16] = cache[b]
    return img


def oam_clusters(g, vram, obpal):
    """The sprites on screen grouped into touching clusters, each rendered as an RGBA image."""
    oam = g.oam().reshape(40, 4)
    spr = [(int(x) - 8, int(y) - 16, int(t) & 0xfe, int(a)) for y, x, t, a in oam if 0 < y < 160 and 0 < x < 168]
    n = len(spr)
    parent = list(range(n))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    for i in range(n):
        for j in range(i + 1, n):
            if abs(spr[i][0] - spr[j][0]) <= 8 and abs(spr[i][1] - spr[j][1]) <= 16:
                parent[find(i)] = find(j)
    groups = {}
    for i in range(n):
        groups.setdefault(find(i), []).append(spr[i])
    out = []
    for grp in groups.values():
        x0 = min(s[0] for s in grp); y0 = min(s[1] for s in grp)
        w = max(s[0] for s in grp) + 8 - x0; h = max(s[1] for s in grp) + 16 - y0
        img = np.zeros((h, w, 4), np.uint8)
        for x, y, t, a in reversed(grp):
            for half in range(2):
                px = tile_px(vram, ((t + half) * 16) + (0x2000 if a & 8 else 0))
                if a & 0x20: px = px[:, ::-1]
                rgb = obpal[a & 7][px]
                blk = np.dstack([rgb, np.where(px > 0, 255, 0).astype(np.uint8)])
                yy = y - y0 + ((1 - half) * 8 if a & 0x40 else half * 8)
                if a & 0x40: blk = blk[::-1]
                sub = img[yy:yy + 8, x - x0:x - x0 + 8]
                m = blk[:, :, 3] > 0
                sub[m] = blk[m]
        out.append(img)
    return out


def gallery(found, limit=48):
    items = sorted((v for v in found.values() if v[1] >= 3 and v[0].shape[0] * v[0].shape[1] >= 256),
                   key=lambda v: -v[0].shape[0] * v[0].shape[1])[:limit]
    if not items:
        return None
    W = 480
    x = y = rowh = 0
    pos = []
    for img, n in items:
        h, w = img.shape[:2]
        if x + w + 4 > W:
            x, y, rowh = 0, y + rowh + 4, 0
        pos.append((x, y)); x += w + 4; rowh = max(rowh, h)
    canvas = np.zeros((y + rowh, W, 3), np.uint8) + 24
    for (img, n), (px, py) in zip(items, pos):
        h, w = img.shape[:2]
        sub = canvas[py:py + h, px:px + w]
        m = img[:, :, 3] > 0
        sub[m] = img[:, :, :3][m]
    return np.kron(canvas, np.ones((2, 2, 1), np.uint8))


def run_level(g, frames, map_lo):
    """Plays the level unattended (firing) and records the map rows reached and the sprites shown."""
    lo = g.read(0xc449) | (g.read(0xc44a) << 8)
    still = 0
    oam_use = {}
    shots = []
    found = {}
    for i in range(frames):
        g.run(1, G.A if i % 16 < 8 else 0)
        p = g.read(0xc449) | (g.read(0xc44a) << 8)
        if map_lo <= p < lo:
            lo, still = p, 0
        else:
            still += 1
        if i % 4 == 0:
            oam = g.oam().reshape(40, 4)
            for y, x, t, a in oam:
                if 0 < y < 160 and 0 < x < 168:
                    key = (int(t) & 0xfe, int(a) & 0x0f)
                    oam_use[key] = oam_use.get(key, 0) + 1
        if i % 6 == 0:
            vram, obpal = g.vram(), G.cgb_rgb(g.obpal())
            for img in oam_clusters(g, vram, obpal):
                k = img.tobytes() + bytes(img.shape[:2])
                if k in found:
                    found[k][1] += 1
                else:
                    found[k] = [img, 1]
        if i % 1500 == 0:
            shots.append(g.frame())
        if still > 2400:
            break
    return lo, oam_use, shots, i + 1, found


def sprite_sheet(vram, obpal, oam_use):
    """The OBJ tiles ($8000-$8fff, 8x16 pairs) coloured with the palette each was used with most."""
    best = {}
    for (t, a), n in oam_use.items():
        k = (t, a & 8)
        if n > best.get(k, (0, 0))[0]:
            best[k] = (n, a & 7)
    cols = 16
    img = np.zeros((8 * 16 * 2, cols * 8 * 2, 3), np.uint8) + 40
    used = np.zeros(128, bool)
    for t in range(0, 256, 2):
        n, p = best.get((t, 0), (0, 0))
        idx = t // 2
        cx, cy = (idx % cols) * 8, (idx // cols) * 16
        for half in range(2):
            px = tile_px(vram, (t + half) * 16)
            rgb = obpal[p][px]
            rgb[px == 0] = (40, 40, 40) if n else (20, 20, 20)
            img[cy + half * 8:cy + half * 8 + 8, cx:cx + 8] = rgb
        used[idx] = n > 0
    return np.kron(img[:16 * 8, :cols * 8], np.ones((2, 2, 1), np.uint8)), int(used.sum())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--levels', default=','.join(str(i) for i in range(1, 25)))
    ap.add_argument('--frames', type=int, default=30000)
    a = ap.parse_args()
    rom = open(G.ROM, 'rb').read()
    names = level_names(rom)
    summary_path = os.path.join(OUT, 'levels.json')
    summary = json.load(open(summary_path)) if os.path.exists(summary_path) else {}
    for level in [int(x) for x in a.levels.split(',')]:
        g, bank, init, c = start_level(level)
        name = names[level]
        d = os.path.join(OUT, 'levels', f'L{level:02d}_{name}')
        os.makedirs(d, exist_ok=True)
        pal = G.cgb_rgb(g.bgpal()); obpal = G.cgb_rgb(g.obpal())
        vram = g.vram()
        # block palette table: up to the first byte with high bits set (the compressed tiles follow)
        bp = []
        o = rom_off(bank, c['block_pal'])
        while len(bp) < 64 and rom[o + len(bp)] < 8:
            bp.append(rom[o + len(bp)])
        bottom = c['map']
        Image.fromarray(g.frame()).resize((320, 288), Image.NEAREST).save(os.path.join(d, 'start.png'))
        top, oam_use, shots, frames, found = run_level(g, a.frames, 0x4000)
        # rows from the bottom up while every block has a palette entry (above lies other data)
        rows = []
        p = bottom
        while p >= max(top, 0x4000):
            r = list(rom[rom_off(bank, p):rom_off(bank, p) + ROW])
            if max(r) >= len(bp):
                break
            rows.insert(0, r)
            p -= ROW
        top = p + ROW
        nblocks = max(max(r) for r in rows) + 1
        Image.fromarray(render_map(rows, bp, vram, pal)).save(os.path.join(d, 'map.png'))
        sheet, nspr = sprite_sheet(g.vram(), obpal, oam_use)
        Image.fromarray(sheet).save(os.path.join(d, 'sprites.png'))
        gal = gallery(found)
        if gal is not None:
            Image.fromarray(gal).save(os.path.join(d, 'gallery.png'))
        if shots:
            s = Image.new('RGB', (160 * len(shots), 144))
            for i, im in enumerate(shots):
                s.paste(Image.fromarray(im), (160 * i, 0))
            s.save(os.path.join(d, 'run.png'))
        info = {'level': level, 'name': name, 'bank': bank, 'init': init, 'map_top': top, 'map_bottom': bottom,
                'rows': len(rows), 'blocks': nblocks, 'block_pal': bp, 'events_pos': c['events_pos'],
                'events': c['events'], 'song': c['song'], 'frames': frames, 'sprite_tiles': nspr,
                'bg_palettes': pal.tolist(), 'obj_palettes': obpal.tolist()}
        json.dump(dict(info, map=rows), open(os.path.join(d, 'map.json'), 'w'))
        summary[str(level)] = info
        print(f'L{level:02d} {name:9s} bank {bank:02x} rows {len(rows):4d} blocks {nblocks:3d} sprites {nspr:3d} frames {frames}')
    json.dump(summary, open(summary_path, 'w'), indent=1)


if __name__ == '__main__':
    main()
