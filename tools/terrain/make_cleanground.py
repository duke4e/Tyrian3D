#!/usr/bin/env python3
"""Clean ground for the 3D view: the art the maps paint under and round their ground objects erased and
filled with the ground round it, where something 3D takes its place; and what the 3D view shows there once
the enemy is gone (stand-ins). Replaces make_erasures.py.

The original paints under many ground enemies what is left of them once destroyed (a crater, a burnt
housing, a broken pyramid, rubble) or the object itself, and the sprite covers it while the enemy lives;
the 3D view draws the enemy as a model, so the painting showed under and round the model. Here:
- The objects: where ground enemies stand (export/terrain/ground.txt), their pieces joined by event and
  link, each piece's sprite placed on the map where its pixels match best.
- The art: in the tiles under an object, the pixels the ground there doesn't explain. A tile drawn over a
  plain ground tile (sharing at least half its pixels, or a fifth in large pieces where the object covers
  most of it, and the same ground under the object as round it) has its art where it differs from that
  tile; an object's own tile (mostly under objects where the maps use it) with no such plain tile is art
  whole; other tiles by colour: palette indices rare in the plain ground the object lies on are art, surely
  so when they are rare in the landscape round it too (a wreck's reds). In the object's own tiles all of it
  goes, in the tiles round them what its sprite covers or what joins that; art that goes on out of the
  object's tiles is landscape (cliffs, rock outcrops, waterfalls, shores) and stays; the object's painted
  shadow goes with it. Green found by colour is plants', black space on maps over space the map's holes.
- Palms (maps with "palms": true in levels.json): every painted palm, its fronds, trunk and soft shadow
  (the 3D palms stand where they were: make_vegetation.py).
- Copies: the objects' tiles painted where no enemy stands get the same treatment, as if the object that
  stands on that tile elsewhere stood there; in the generated side columns they are replaced by the plain
  tile that fits their neighbours best (no objects out there).
- The fill: a tile's plain ground where it was drawn over one (an offset to that tile's nearest place in the
  map, so the HD tiles fill it too); otherwise the ground of the same map copied from within five tiles, one
  offset per part (any offset), the one whose surroundings match the ground round the part (as filled so
  far) best (FFT correlation), from ground free of any art, of the plain tiles round the object where it
  can, without colours the ground round the part doesn't have where it can (else in smaller parts).
- A piece is erased only where something 3D takes its place: its stand-in, a 3D palm, or nothing at all in
  the side columns. Looks without a model, and the models in cleanground.json's "keep" (and "keep_maps"
  for one map), keep their painting.
- Stand-ins (assets/terrain/<map>.std, src/tyrian2.c draw_standins): for every erased piece, the model of
  what the map painted there, drawn while no ground enemy of its looks (alive, dead, coming or what it turns
  into) covers its place: its own model where the map paints the object as it is; the look the game leaves
  standing when it is destroyed (dgr with dlevel -1), or the one cleanground.json names; else its own model
  slumped and darkened as a placeholder.

usage: <python with numpy, scipy and PIL> tools/terrain/make_cleanground.py all | <map hash>...

Writes assets/terrain/<map>.era (as make_erasures.py did: "TYER", version 1, count, then zlib-compressed,
in order of y: x, y (uint16, the map's pixels, the generated columns included), w, h (uint8, at most a tile:
the loader's limit), the source's offset dx, dy (int16), w x h mask bytes), assets/terrain/<map>.std (text,
a stand-in a line, see write_standins) and export/terrain/<map>_clean.png (the level's start, the map | the
clean ground with the stand-ins ringed).
"""
import glob
import json
import math
import os
import struct
import sys
import zlib
from collections import Counter, defaultdict

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
from scipy.signal import correlate

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "content"))
sys.path.insert(0, os.path.join(HERE, ".."))
import footprints as fpr  # noqa: E402
import make_terrain as mt  # noqa: E402

ROOT = mt.ROOT
DATA = os.path.join(ROOT, "data", "tyrian2000")
OVERRIDES = os.path.join(HERE, "cleanground.json")
TILE_W, TILE_H = 24, 28
SHAPE_FILE = "2478ABCDEFGHIJKLMNOPQRSTU5#V0@3^59'%"   # lvlmast.c shapeFile[]: shapebank -> newsh<letter>.shp
E6_LEVELS = {"DIG SITE", "REEF", "GREY MOON", "VAULT", "DELI RUIN", "ROOST", "MIGRATION", "DEEP ICE", "GLACIER",
             "COLLECTOR", "CRUSTGATE", "GRAVITRON", "THE CORE", "INVADERS"}


def custom_episodes():
    """{folder name: (episode number, its folder)} of the custom episodes (src/episodes.h), as tools/levels.py finds them."""
    import levels
    out = {}
    for name, script in levels.custom_episodes(ROOT, DATA).items():
        number = int(os.path.basename(script).lower()[len("levels"):-len(".dat")])
        out[name] = (number, os.path.dirname(script))
    return out


def custom_levels():
    """The custom episodes' level names that no episode of the game has: their maps, like episode 6's, don't
    teach the tilesets (what is plain ground, what objects look like), so the originals' assets stay as they are."""
    import levels
    names = lambda path: {name.strip() for _, name in levels.level_sections(path)}
    game = set().union(*(names(os.path.join(DATA, f"levels{ep}.dat")) for ep in range(1, 6)
                         if os.path.exists(os.path.join(DATA, f"levels{ep}.dat"))))
    custom = set().union(set(), *(names(os.path.join(folder, f)) for number, folder in custom_episodes().values()
                                  for f in os.listdir(folder) if f.lower() == f"levels{number}.dat"))
    return custom - game


DERIVED_LEVELS = E6_LEVELS | custom_levels()   # maps that aren't the game's own


def derived(info):
    """A map that isn't the game's own: episode 6's and the custom episodes' levels by name, episode 7's (the GBC
    levels, several named as originals are) by the episode tools/content/gbc/terrain.py writes into its export."""
    return info.get("episode") == 7 or info["level"].strip() in DERIVED_LEVELS

PLAIN_MIN, PLAIN_UNDER = 20, 0.15   # a tile this common and seldom under an object is plain ground,
PLAIN_COMMON = 60                   # or one this common not mostly under objects (a floor many stand on)
BASE_EXACT = 0.5     # a tile drawn over a plain tile shares at least this many of its pixels,
BASE_PART = 0.2      # or, where the object covers most of it, this many
BASE_PIECE = 0.75    # nearly all of them in large pieces (the plain tile round the object, not chance),
BASE_LARGE = 24      # (pixels)
BASE_FOREIGN = 0.05  # and the plain tile under the object at most this much of colours not round it
BASE_FOREIGN_EXACT = 0.2   # (sharing BASE_EXACT: this much; more is another surface there, a shore, a machine)
RING = 1             # tiles round the object whose plain ground it lies on
DOMINANT = 0.25      # a plain tile making up this share of that ring is the ground
GROUND_SHARE = 0.25  # (and the fills copy from the plain tiles making up this much of it, where they can)
RARE = 0.004         # an index rarer than this in the ground is art,
RARE_ALL = 0.002     # rarer than this counting the landscape round it surely
SPECK = 4            # art smaller than this (pixels) is noise
CONTINUE = 6         # edge pixels whose shape goes on out of the object's tiles: landscape
SHADOW = 5           # pixels round the art where its painted shadow is looked for
WHOLE = -1           # (a cell's tile all art: cell_base)
SEARCH = 5           # tiles: how far a fill's source may be
FOREIGN = 0.15       # a fill's source with more of colours not in the ground round the part is the last resort
SPLIT = 10           # pixels: a part larger than this with only such sources, or none, is filled in quarters
COVERED = 6.5        # game pixels: a stand-in is covered by a ground enemy of its looks this near

_pal = None


def palette():
    global _pal
    if _pal is None:
        rows = [[int(v) for v in line.split()] for line in open(os.path.join(ROOT, "tools", "blender", "palette_levels.txt"))
                if line.strip()]
        _pal = np.array(rows, np.uint8)
    return _pal


def to_indices(rgb):
    pal = palette()
    keys = (pal[:, 0].astype(np.int64) << 16) | (pal[:, 1].astype(np.int64) << 8) | pal[:, 2]
    lut = {}
    for i in range(255, -1, -1):
        lut[int(keys[i])] = i
    ks = np.array(sorted(lut), np.int64)
    vs = np.array([lut[int(x)] for x in ks], np.uint8)
    key = (rgb[..., 0].astype(np.int64) << 16) | (rgb[..., 1].astype(np.int64) << 8) | rgb[..., 2]
    pos = np.clip(np.searchsorted(ks, key), 0, len(ks) - 1)
    return vs[pos]


_maps = {}


def load(name):
    """(info, indices, rgb uint8, opaque, shapes) of an exported map."""
    if name not in _maps:
        info, rgb, opaque = mt.load_map(name)
        rgb8 = (rgb * 255 + 0.5).astype(np.uint8)
        _maps[name] = (info, to_indices(rgb8), rgb8, opaque, np.array(info["shapes"], np.int32))
    return _maps[name]


_tiles = {}


def tiles(letter):
    """shapes<letter>.dat: shape number -> 28 x 24 palette indices (None for blank ones)."""
    if letter not in _tiles:
        data = open(os.path.join(DATA, f"shapes{letter}.dat"), "rb").read()
        o, out = 0, {}
        for z in range(600):
            if o >= len(data):
                break
            blank = data[o]
            o += 1
            if blank:
                out[z + 1] = None
            else:
                out[z + 1] = np.frombuffer(data[o:o + TILE_W * TILE_H], np.uint8).reshape(TILE_H, TILE_W)
                o += TILE_W * TILE_H
        _tiles[letter] = out
    return _tiles[letter]


_grids = {}


def full_grid(name):
    """The map's shapes with the generated side columns (their tiles found by their pixels, flips too)."""
    if name in _grids:
        return _grids[name]
    info, idx, rgb, opaque, shapes = load(name)
    T = tiles(info["tileset"])
    side = info["side_columns"]
    rows, cols = shapes.shape
    grid = np.full((rows, cols + 2 * side), -1, np.int32)
    grid[:, side:side + cols] = shapes
    lut = {}
    for s, t in T.items():
        if t is not None:
            lut.setdefault(t.tobytes(), s)
            lut.setdefault(np.ascontiguousarray(t[:, ::-1]).tobytes(), s)
    for r in range(rows):
        for c in list(range(side)) + list(range(side + cols, cols + 2 * side)):
            hit = lut.get(np.ascontiguousarray(idx[r * TILE_H:(r + 1) * TILE_H, c * TILE_W:(c + 1) * TILE_W]).tobytes())
            if hit is not None:
                grid[r, c] = hit
    _grids[name] = grid
    return grid


# --- the enemies' looks and what the game shows of them damaged or dead ------------------------------------
_sheets = {}


def sheet(letter):
    """newsh<letter>.shp decoded as blit_sprite2 draws it: sprite -> (14 x 12 indices, mask)."""
    letter = letter.lower()
    if letter in _sheets:
        return _sheets[letter]
    path = os.path.join(DATA, f"newsh{letter}.shp")
    out = {}
    if os.path.exists(path):
        data = open(path, "rb").read()
        count = struct.unpack_from("<H", data, 0)[0] // 2
        for index in range(1, count + 1):
            off = struct.unpack_from("<H", data, (index - 1) * 2)[0]
            pix, mask = np.zeros((40, 12), np.uint8), np.zeros((40, 12), bool)
            pos, o = 0, off
            while o < len(data) and data[o] != 0x0F:
                b = data[o]
                pos += b & 0x0F
                for _ in range((b & 0xF0) >> 4):
                    o += 1
                    if o >= len(data):
                        break
                    y, x = divmod(pos, 12)
                    if y < 40:
                        pix[y, x], mask[y, x] = data[o], True
                    pos += 1
                o += 1
            out[index] = (pix[:14], mask[:14])
    _sheets[letter] = out
    return out


def picture(letter, first, large):
    s = sheet(letter)
    if not large:
        return s.get(first, (np.zeros((14, 12), np.uint8), np.zeros((14, 12), bool)))
    pix, mask = np.zeros((28, 24), np.uint8), np.zeros((28, 24), bool)
    for k, (dy, dx) in zip((first, first + 1, first + 19, first + 20), ((0, 0), (0, 12), (14, 0), (14, 12))):
        p, m = s.get(k, (np.zeros((14, 12), np.uint8), np.zeros((14, 12), bool)))
        pix[dy:dy + 14, dx:dx + 12][m] = p[m]
        mask[dy:dy + 14, dx:dx + 12] |= m
    return pix, mask


_enemies = None


def enemy_looks():
    """(sheet letter, first sprite) -> the enemy records with that look, in every episode's item data:
    dgr, dlevel, the death enemy's look, the animation's sprites."""
    global _enemies
    if _enemies is not None:
        return _enemies
    import tyrdata
    out = defaultdict(list)
    sets = [(1, DATA), (4, DATA), (5, DATA)]
    for ep in (6, 7):  # (episode 7: the GBC levels, tools/content/gbc)
        folder = os.path.join(ROOT, "assets", "content", f"episode{ep}")
        if os.path.exists(os.path.join(folder, f"tyrian{ep}.lvl")):
            sets.append((ep, folder))
    sets += [(number, folder) for number, folder in custom_episodes().values() if number >= 4]  # (1-3: tyrian.hdt's)
    for ep, d in sets:
        en = tyrdata.load_items(ep, data_dir=d)["enemies"]
        def look(e):
            b = e["shapebank"]
            return SHAPE_FILE[b - 1].lower() if 1 <= b <= len(SHAPE_FILE) else None
        for i, e in en.items():
            letter = look(e)
            if letter is None or not e["egraphic"][0]:
                continue
            die = en.get(e["eenemydie"]) if e["eenemydie"] else None
            rec = dict(dgr=e["dgr"], dlevel=e["dlevel"], frames=[g for g in e["egraphic"][:max(1, min(e["ani"], 20))] if g],
                       die=(look(die), die["egraphic"][0], die["dgr"]) if die is not None and look(die) else None)
            if rec not in out[(letter, e["egraphic"][0])]:
                out[(letter, e["egraphic"][0])].append(rec)
    _enemies = out
    return out


def code_letter(code):
    return chr(code).lower()


def letter_code(letter):
    return ord(letter.upper()) if letter.isalpha() else ord(letter)


# --- standing objects ------------------------------------------------------------------------------------------
class Piece:
    pass


def standing_pieces(name):
    """The map's standing ground enemies, one per place, their sprites placed where they match the map best."""
    info, idx, rgb, opaque, shapes = load(name)
    side = info["side_columns"]
    out, seen = [], {}
    for t in mt.ground_tracks(name, riding=info["background"] == 3):
        if not t.standing or t.look is None:
            continue
        x, y = float(np.median(t.x)), float(np.median(t.y))
        key = (t.look, int(x) // 3, int(y) // 3)
        if key in seen:
            continue
        letter = code_letter(t.look[0])
        large = t.size >= 24
        pic, mask = picture(letter, t.look[1], large)
        if not mask.any():
            continue
        h, w = pic.shape
        best = (-1.0, 0, 0, None)
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                x0, y0 = int(round(x)) - w // 2 + dx, int(round(y)) - h // 2 + dy
                if x0 < 0 or y0 < 0 or x0 + w > idx.shape[1] or y0 + h > idx.shape[0]:
                    continue
                eq = (idx[y0:y0 + h, x0:x0 + w] == pic) & mask
                f = eq.sum() / mask.sum()
                if f > best[0] + 1e-9:
                    best = (f, x0, y0, eq)
        if best[3] is None:
            continue
        p = Piece()
        p.letter, p.sprite, p.large, p.x, p.y = letter, t.look[1], large, x, y
        p.group, p.link = t.group or 0, t.link or 0
        p.x0, p.y0, p.pic, p.mask, p.eq = best[1], best[2], pic, mask, best[3]
        p.cells = sorted({(r, c) for r in range(max(p.y0, 0) // TILE_H, (p.y0 + h - 1) // TILE_H + 1)
                          for c in range(p.x0 // TILE_W - side, (p.x0 + w - 1) // TILE_W - side + 1)
                          if 0 <= r < shapes.shape[0] and 0 <= c < shapes.shape[1]})
        seen[key] = p
        out.append(p)
    return out


def objects(pieces):
    """Pieces joined into objects: made by one event with one link, their sprites touching."""
    parent = list(range(len(pieces)))

    def root(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    by = defaultdict(list)
    for i, p in enumerate(pieces):
        if p.group:
            by[(p.group, p.link)].append(i)
    for idxs in by.values():
        for a in idxs:
            for b in idxs:
                if a < b:
                    A, B = pieces[a], pieces[b]
                    if (A.x0 <= B.x0 + B.pic.shape[1] + 2 and B.x0 <= A.x0 + A.pic.shape[1] + 2 and
                            A.y0 <= B.y0 + B.pic.shape[0] + 2 and B.y0 <= A.y0 + A.pic.shape[0] + 2):
                        parent[root(a)] = root(b)
    groups = defaultdict(list)
    for i in range(len(pieces)):
        groups[root(i)].append(pieces[i])
    return sorted(groups.values(), key=lambda g: (min(p.y0 for p in g), min(p.x0 for p in g)))


# --- the tilesets: plain ground, object tiles, bases ----------------------------------------------------------
def tileset_maps(tileset, originals=True):
    out = []
    for f in sorted(glob.glob(os.path.join(mt.MAPS, "map_*.json"))):
        d = json.load(open(f))
        if d["tileset"] == tileset and d["background"] == 1 and not (originals and derived(d)):
            out.append(os.path.basename(f)[4:-5])
    return out


_stats = {}


def stats(tileset):
    """(count of each shape in the tileset's original ground maps, of those cells under standing pieces)."""
    if tileset not in _stats:
        total, under = Counter(), Counter()
        for name in tileset_maps(tileset):
            info, idx, rgb, opaque, shapes = load(name)
            total.update(shapes.ravel().tolist())
            under.update(s for s in {(r, c, int(shapes[r, c])) for p in standing_pieces(name) for r, c in p.cells})
        under = Counter(s for _, _, s in under)
        _stats[tileset] = (total, under)
    return _stats[tileset]


def plain(tileset, s):
    total, under = stats(tileset)
    n, u = total.get(s, 0), under.get(s, 0)
    return (n >= PLAIN_COMMON and u <= 0.5 * n) or (n >= PLAIN_MIN and u <= PLAIN_UNDER * n)


def own_tile(tileset, s):
    """Whether a tile is an object's own (not plain, and mostly under objects where the maps use it)."""
    total, under = stats(tileset)
    return not plain(tileset, s) and under.get(s, 0) >= 0.5 * total.get(s, 0) > 0


_bases = {}


def base_of(tileset, s):
    """(base, share, art mask) of a tile: itself for plain ground; the plain tile it was drawn over (sharing
    at least BASE_EXACT of its pixels, or BASE_PART of them nearly all in large pieces: the plain ground round
    an object that covers most of the tile; and with the same ground under the object as round it) and where
    it differs from it; or (None, share, None)."""
    key = (tileset, s)
    if key in _bases:
        return _bases[key]
    T = tiles(tileset)
    t = T.get(s)
    if t is None:
        _bases[key] = (None, 0.0, None)
    elif plain(tileset, s):
        _bases[key] = (s, 1.0, np.zeros((TILE_H, TILE_W), bool))
    else:
        total, _ = stats(tileset)

        def foreign(g, eq):
            # how much of the plain tile under the object has colours it doesn't have round the object
            seen = np.bincount(T[g][eq], minlength=256) > 0
            return float((~seen[T[g][~eq]]).mean()) if (~eq).any() else 0.0

        def piece(g, eq):
            # how many of the shared pixels are in large pieces, when nearly all of them are and under the
            # object the plain tile is the same ground as round it (not another surface: a shore, a cliff's
            # edge); else 0
            lab, n = ndimage.label(eq)
            sizes = ndimage.sum(eq, lab, range(1, n + 1)) if n else np.zeros(0)
            big = sizes[sizes >= BASE_LARGE].sum()
            return int(big) if big >= BASE_PIECE * eq.sum() and foreign(g, eq) <= BASE_FOREIGN else 0
        exact, part = [], []
        for g in total:
            if g > 0 and g != s and T.get(g) is not None and plain(tileset, g):
                eq = T[g] == t
                share = float(eq.mean())
                if share >= BASE_EXACT and foreign(g, eq) <= BASE_FOREIGN_EXACT:
                    exact.append((share, g))
                elif share >= BASE_PART:
                    big = piece(g, eq)
                    if big:   # (the plain tile round the object: the most in large pieces)
                        part.append((big, share, g))
        # the choices, best first: those sharing at least BASE_EXACT, then the others
        _choices[key] = [(g, share) for share, g in sorted(exact, reverse=True)] or \
                        [(g, share) for big, share, g in sorted(part, reverse=True)]
        g, share = _choices[key][0] if _choices[key] else (None, 0.0)
        _bases[key] = (None, share, None) if g is None else (g, share, differs(t, T[g]))
    return _bases[key]


_choices = {}


def base_choices(tileset, s):
    """The plain tiles a tile may have been drawn over, best first (base_of's choice the first): [(tile, share)]."""
    g, share, _ = base_of(tileset, s)
    return _choices.get((tileset, s), [(g, share)] if g is not None else [])


def differs(t, base):
    """Where a tile differs from the plain tile it was drawn over (specks left out, gaps closed)."""
    diff = base != t
    lab, n = ndimage.label(diff, np.ones((3, 3), bool))
    if n:
        sizes = ndimage.sum(diff, lab, range(1, n + 1))
        diff = np.isin(lab, 1 + np.nonzero(sizes >= 3)[0])
    return ndimage.binary_closing(diff, np.ones((3, 3), bool)) | diff


_adjacency = {}


def adjacency(tileset):
    if tileset not in _adjacency:
        right, down = Counter(), Counter()
        for name in tileset_maps(tileset):
            s = load(name)[4]
            right.update(zip(s[:, :-1].ravel().tolist(), s[:, 1:].ravel().tolist()))
            down.update(zip(s[:-1, :].ravel().tolist(), s[1:, :].ravel().tolist()))
        _adjacency[tileset] = (right, down)
    return _adjacency[tileset]


def fitting_plain(tileset, grid, r, c, avoid):
    """The plain tile that best continues the neighbours of (r, c), by how often the maps put it beside them."""
    right, down = adjacency(tileset)
    total, _ = stats(tileset)
    nb = []
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        rr, cc = r + dr, c + dc
        if 0 <= rr < grid.shape[0] and 0 <= cc < grid.shape[1] and grid[rr, cc] > 0 and (rr, cc) not in avoid:
            nb.append((dr, dc, int(grid[rr, cc])))
    best = (-1e9, None)
    for g in total:
        if g <= 0 or not plain(tileset, g):
            continue
        score = 0.05 * math.log1p(total[g])
        for dr, dc, n in nb:
            k = down.get((n, g), 0) if dr == -1 else down.get((g, n), 0) if dr == 1 else \
                right.get((n, g), 0) if dc == -1 else right.get((g, n), 0)
            score += math.log1p(k) if k else -3.0
        if score > best[0]:
            best = (score, g)
    return best[1]


# --- the art and the fill --------------------------------------------------------------------------------------
class Cleaner:
    def __init__(self, name):
        self.name = name
        self.info, self.idx, self.rgb, self.opaque, self.shapes = load(name)
        self.tileset = self.info["tileset"]
        self.side = self.info["side_columns"]
        self.rgbf = self.rgb.astype(np.float32)
        self.blocked = np.zeros(self.idx.shape, bool)  # art and objects: no fill is taken from there
        self.erased = np.zeros(self.idx.shape, bool)
        self.pieces = []                               # (x0, y0, mask, dx, dy)
        self.now = self.rgbf.copy()                    # the map with the pieces so far applied
        self.todo = np.zeros(self.idx.shape, bool)     # art still to be erased (the palms)
        self.now_idx = self.idx.copy()
        self.palms = False                             # a map with palms: their green is left to them
        self.ground = set()                            # the plain tiles round the last object (ground_hist)
        self._tile_px = None
        self.cell_bases = {}                           # (row, column) -> (plain tile, art mask) or None
        self.present = set(self.shapes.ravel().tolist())
        # black space on maps over space ("void" in levels.json) is never art, nor a fill's source: it is the
        # map's holes
        self.void = mt.void_mask(self.rgbf / 255) if "void" in mt.settings(name) else np.zeros(self.idx.shape, bool)

    def cell_box(self, r, c):
        return (c + self.side) * TILE_W, r * TILE_H

    def cell_base(self, r, c, avoid):
        """The plain tile a cell's tile was drawn over and the art against it (base_of); for an object's own
        tile without one WHOLE: all of it is art, filled from the ground round it; or None."""
        if (r, c) not in self.cell_bases:
            s = int(self.shapes[r, c])
            g, share, bm = base_of(self.tileset, s)
            T = tiles(self.tileset)
            if g is not None and g != s:
                # one this map has (the fill copies it from its nearest place)
                present = [h for h, _ in base_choices(self.tileset, s) if h in self.present]
                if present and present[0] != g:
                    g = present[0]
                    bm = differs(T[s], T[g])
            if g is None and own_tile(self.tileset, s) and T.get(s) is not None:
                g, bm = WHOLE, np.ones((TILE_H, TILE_W), bool)
            self.cell_bases[(r, c)] = (g, bm) if g is not None else None
        return self.cell_bases[(r, c)]

    def ground_hist(self, cells, occupied):
        rows, cols = self.shapes.shape
        count = Counter()
        for r, c in cells:
            for rr in range(r - RING, r + RING + 1):
                for cc in range(c - RING, c + RING + 1):
                    if 0 <= rr < rows and 0 <= cc < cols and (rr, cc) not in occupied:
                        s = int(self.shapes[rr, cc])
                        if plain(self.tileset, s):
                            count[s] += 1
        if not count:
            for r, c in cells:
                for rr in range(r - 2, r + 3):
                    for cc in range(c - 2, c + 3):
                        if 0 <= rr < rows and 0 <= cc < cols and (rr, cc) not in occupied:
                            count[int(self.shapes[rr, cc])] += 1
        self.ground = set()
        if not count:
            return np.full(256, 1.0 / 256)
        n = sum(count.values())
        top = [s for s, k in count.most_common(2) if k >= DOMINANT * n] or [count.most_common(1)[0][0]]
        self.ground = {s for s, k in count.items() if k >= GROUND_SHARE * n and plain(self.tileset, s)}
        T = tiles(self.tileset)
        hist = np.zeros(256)
        for s in top:
            if T.get(s) is not None:
                hist += count[s] * np.bincount(T[s].ravel(), minlength=256)
        return hist / max(hist.sum(), 1)

    def landscape_hist(self, cells, occupied, ring=2):
        rows, cols = self.shapes.shape
        hist = np.zeros(256)
        for r, c in cells:
            for rr in range(r - ring, r + ring + 1):
                for cc in range(c - ring, c + ring + 1):
                    if 0 <= rr < rows and 0 <= cc < cols and (rr, cc) not in occupied:
                        x, y = self.cell_box(rr, cc)
                        hist += np.bincount(self.idx[y:y + TILE_H, x:x + TILE_W].ravel(), minlength=256)
        return hist / max(hist.sum(), 1)

    def object_mask(self, pieces, cells, occupied, touch_extra=None):
        """The art to erase for an object (a mask over its cells' box) and the box."""
        r0, r1 = min(r for r, _ in cells), max(r for r, _ in cells) + 1
        c0, c1 = min(c for _, c in cells), max(c for _, c in cells) + 1
        X0, Y0 = self.cell_box(r0, c0)
        H, W = (r1 - r0) * TILE_H, (c1 - c0) * TILE_W
        strong, weak, inside = np.zeros((H, W), bool), np.zeros((H, W), bool), np.zeros((H, W), bool)
        exact = np.zeros((H, W), bool)   # (art against a cell's plain tile)
        own = np.zeros((H, W), bool)     # (the cells of the object's own tiles)
        hist = self.ground_hist(cells, occupied)
        land = self.landscape_hist(cells, occupied)
        for r, c in cells:
            y, x = (r - r0) * TILE_H, (c - c0) * TILE_W
            inside[y:y + TILE_H, x:x + TILE_W] = True
            s = int(self.shapes[r, c])
            own[y:y + TILE_H, x:x + TILE_W] = own_tile(self.tileset, s)
            g, bm = self.cell_base(r, c, occupied) or (None, None)
            if g == s:
                continue
            t = self.idx[Y0 + y:Y0 + y + TILE_H, X0 + x:X0 + x + TILE_W]
            if g is not None:
                strong[y:y + TILE_H, x:x + TILE_W] = bm
                exact[y:y + TILE_H, x:x + TILE_W] = True
                continue
            strong[y:y + TILE_H, x:x + TILE_W] = land[t] < RARE_ALL
            weak[y:y + TILE_H, x:x + TILE_W] = hist[t] < RARE
        # Green found by colour is left alone (plants); against a plain tile it is the object's (a window,
        # leaves), unless the map has palms (theirs).
        rgb = self.rgb[Y0:Y0 + H, X0:X0 + W].astype(np.int32)
        green = (rgb[..., 1] > rgb[..., 0] * 1.12) & (rgb[..., 1] > rgb[..., 2] * 1.05) & (rgb[..., 1] > 30)
        if not self.palms:
            green &= ~exact
        strong &= ~green & ~self.void[Y0:Y0 + H, X0:X0 + W]
        weak &= ~green & ~self.void[Y0:Y0 + H, X0:X0 + W]

        def tidy(m):
            m = ndimage.binary_closing(m, np.ones((3, 3), bool), border_value=0) | m
            lab, n = ndimage.label(m, np.ones((3, 3), bool))
            keep = []
            for k, sl in enumerate(ndimage.find_objects(lab), 1):
                if sl is not None:
                    area = int((lab[sl] == k).sum())
                    if area >= SPECK and area / max(sl[0].stop - sl[0].start, sl[1].stop - sl[1].start) >= 2.5:
                        keep.append(k)  # (not a line a pixel or two thick: the tiles' pattern)
            return np.isin(lab, keep) & inside

        strong = tidy(strong)
        weak = tidy(weak | strong) & ~strong
        touch = np.zeros((H, W), bool)     # what the sprites or the models' low parts cover
        covered = np.zeros((H, W), bool)   # what the sprites cover (hide while the enemy lives)
        for p in pieces:
            h, w = p.pic.shape
            ys, xs = p.y0 - Y0, p.x0 - X0
            a0, b0, a1, b1 = max(ys, 0), max(xs, 0), min(ys + h, H), min(xs + w, W)
            if a1 > a0 and b1 > b0:
                covered[a0:a1, b0:b1] |= p.mask[a0 - ys:a1 - ys, b0 - xs:b1 - xs]
            fp = fpr.footprint(p.letter, p.sprite, frames_of(p.letter, p.sprite))
            if fp is not None:
                fpr.stamp(touch, fp, p.x - X0, p.y - Y0, "low", 1)
        if touch_extra is not None:
            covered |= touch_extra
        touch |= covered
        def parts(m):
            # the art in the object's own tiles apart from the art in the tiles round it (a gun's apart
            # from the cliff it stands by), each in pieces
            a, n = ndimage.label(m & own, np.ones((3, 3), bool))
            b, k = ndimage.label(m & ~own, np.ones((3, 3), bool))
            return np.where(b > 0, b + n, a), n + k

        out = np.zeros((H, W), bool)
        lab, n = parts(strong)
        for k in range(1, n + 1):   # (in the object's own tiles all its art, in the tiles round it what it hides)
            comp = lab == k
            mine = (comp & own).any() or (comp & covered).sum() >= 0.5 * comp.sum()
            if mine and self.goes_on(comp, inside, X0, Y0, hist, occupied) < CONTINUE:
                out |= comp
        lab, n = parts(weak)
        grown = ndimage.binary_dilation(out, iterations=1)
        for k in range(1, n + 1):
            comp = lab == k
            if ((comp & grown).any() or (comp & touch).sum() >= 0.5 * comp.sum() or not (comp & ~own).any()) and \
                    self.goes_on(comp, inside, X0, Y0, hist, occupied) < CONTINUE:
                out |= comp
        out = ndimage.binary_fill_holes(ndimage.binary_closing(out, np.ones((3, 3), bool)) | out)
        if out.any():
            # its painted shadow: ground next to the art darker than the ground away from it (in its cells and
            # the tile round them, where no other object stands)
            ey0, ex0 = max(Y0 - TILE_H, 0), max(X0 - TILE_W, 0)
            ey1, ex1 = min(Y0 + H + TILE_H, self.idx.shape[0]), min(X0 + W + TILE_W, self.idx.shape[1])
            lum = self.rgbf[ey0:ey1, ex0:ex1] @ np.array([0.299, 0.587, 0.114], np.float32)
            smooth = ndimage.uniform_filter(lum, 5)
            art = np.zeros(lum.shape, bool)
            art[Y0 - ey0:Y0 - ey0 + H, X0 - ex0:X0 - ex0 + W] = out
            free = self.opaque[ey0:ey1, ex0:ex1].copy()
            for r, c in occupied - set(cells):
                x, y = self.cell_box(r, c)
                free[max(y - ey0, 0):max(y + TILE_H - ey0, 0), max(x - ex0, 0):max(x + TILE_W - ex0, 0)] = False
            away = free & ~ndimage.binary_dilation(art, iterations=SHADOW + 3)
            near = ndimage.binary_dilation(out, iterations=SHADOW)
            if away.sum() > 50:
                dark = np.percentile(smooth[away], 8)
                shade = near & ~out & (smooth[Y0 - ey0:Y0 - ey0 + H, X0 - ex0:X0 - ex0 + W] < dark) & inside
                lab, n = ndimage.label(shade | out, np.ones((3, 3), bool))
                keep = np.unique(lab[out])
                out |= np.isin(lab, keep[keep > 0]) & shade
        out = ndimage.binary_dilation(out, iterations=1) & inside
        return out, (X0, Y0, W, H)

    def goes_on(self, comp, inside, X0, Y0, hist, occupied=()):
        """How many of a part's pixels at the edge of the object's cells go on out of them: of a colour rare
        in the ground, next to another one outside, not in the cells of another object standing there (domes
        side by side, made by one event: IXMUCANE's three small ones and its two big ones, whose paintings
        touch, were each landscape to the others and kept)."""
        H, W = comp.shape
        edge = comp & ~ndimage.binary_erosion(inside, np.ones((3, 3), bool), border_value=0)
        edge &= hist[self.idx[Y0:Y0 + H, X0:X0 + W]] < RARE
        n = 0
        for y, x in zip(*np.nonzero(edge)):
            for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                yy, xx = y + dy, x + dx
                if 0 <= yy < H and 0 <= xx < W and inside[yy, xx]:
                    continue
                Y, X = Y0 + yy, X0 + xx
                if (Y // TILE_H, X // TILE_W - self.side) in occupied:
                    continue
                if 0 <= Y < self.idx.shape[0] and 0 <= X < self.idx.shape[1] and hist[self.idx[Y, X]] < RARE:
                    n += 1
                    break
        return n

    def nearest_tile(self, g, r, c):
        """The nearest place in the map's own columns that holds plain tile g whole, free of art."""
        rows, cols = self.shapes.shape
        best = None
        for rr, cc in zip(*np.nonzero(self.shapes == g)):
            x, y = self.cell_box(rr, cc)
            if self.blocked[y:y + TILE_H, x:x + TILE_W].any():
                continue
            d = abs(rr - r) * 2 + abs(cc - c)
            if best is None or d < best[0]:
                best = (d, int(rr), int(cc))
        return best

    def tile_px(self):
        """The tile at each of the map's pixels (the generated columns' as found, -1 where not known)."""
        if self._tile_px is None:
            self._tile_px = np.repeat(np.repeat(full_grid(self.name), TILE_H, 0), TILE_W, 1)
        return self._tile_px

    def add_piece(self, x0, y0, m, dx, dy):
        self.pieces.append((x0, y0, m, dx, dy))
        ys, xs = np.nonzero(m)
        self.now[y0 + ys, x0 + xs] = self.rgbf[y0 + ys + dy, x0 + xs + dx]
        self.now_idx[y0 + ys, x0 + xs] = self.idx[y0 + ys + dy, x0 + xs + dx]

    def offset_fill(self, mask, X0, Y0, pending=None, ground=None):
        """One offset for a part: the ground within SEARCH tiles whose ring matches the part's ring best (the
        ground round it as filled so far, without the art still to be erased: the palms', and pending, over the
        same box), from the plain tiles of the ground round the object (ground) where there are any: (dx, dy,
        whether the ground there has only the ring's colours), or None."""
        Hm, Wm = self.idx.shape
        # the part's box and the ring's two pixels round it
        h, w = mask.shape
        py0, px0 = min(2, Y0), min(2, X0)
        py1, px1 = max(min(2, Hm - Y0 - h), 0), max(min(2, Wm - X0 - w), 0)
        mask = np.pad(mask, ((py0, py1), (px0, px1)))
        if pending is not None:
            pending = np.pad(pending, ((py0, py1), (px0, px1)))
        X0, Y0 = X0 - px0, Y0 - py0
        H, W = mask.shape
        ring = ndimage.binary_dilation(mask, iterations=2) & ~mask
        later = self.todo[Y0:Y0 + H, X0:X0 + W] | (pending if pending is not None else False)
        if (ring & ~later).sum() >= 8:
            ring &= ~later
        if not ring.any():
            return None
        need = ndimage.binary_dilation(mask, iterations=2)
        here = self.now[Y0:Y0 + H, X0:X0 + W]
        ring_px = here[ring]
        ring_mean, ring_std = ring_px.mean(0), ring_px.std(0)
        keys = np.unique(self.now_idx[Y0:Y0 + H, X0:X0 + W][ring])
        sy0, sx0 = max(Y0 - SEARCH * TILE_H, 0), max(X0 - SEARCH * TILE_W, 0)
        sy1, sx1 = min(Y0 + H + SEARCH * TILE_H, Hm), min(X0 + W + SEARCH * TILE_W, Wm)
        S = self.rgbf[sy0:sy1, sx0:sx1]
        if S.shape[0] < H or S.shape[1] < W:
            return None
        rk, mk, nk = ring.astype(np.float32), mask.astype(np.float32), need.astype(np.float32)
        bad = self.blocked[sy0:sy1, sx0:sx1] | ~self.opaque[sy0:sy1, sx0:sx1] | self.void[sy0:sy1, sx0:sx1]
        blocked = correlate(bad.astype(np.float32), nk, mode="valid", method="fft")
        if ground:
            other = bad | ~np.isin(self.tile_px()[sy0:sy1, sx0:sx1], list(ground))
            elsewhere = correlate(other.astype(np.float32), nk, mode="valid", method="fft")
            if (elsewhere <= 0.5).any():
                blocked = elsewhere
        nin = mk.sum()
        ssd = np.zeros_like(blocked)
        mean_in = np.zeros(blocked.shape + (3,), np.float32)
        sq_in = np.zeros(blocked.shape + (3,), np.float32)
        for ch in range(3):
            s = S[..., ch]
            t = here[..., ch] * rk
            ssd += correlate(s * s, rk, mode="valid", method="fft") - 2 * correlate(s, t, mode="valid", method="fft") + (t * t).sum()
            mean_in[..., ch] = correlate(s, mk, mode="valid", method="fft") / nin
            sq_in[..., ch] = correlate(s * s, mk, mode="valid", method="fft") / nin
        std_in = np.sqrt(np.maximum(sq_in - mean_in ** 2, 0))
        like = np.abs(mean_in - ring_mean).sum(2) + np.abs(std_in - ring_std).sum(2)
        foreign = (~np.isin(self.idx[sy0:sy1, sx0:sx1], keys)).astype(np.float32)
        far = correlate(foreign, mk, mode="valid", method="fft") / nin
        oy = np.arange(blocked.shape[0])[:, None] + sy0 - Y0
        ox = np.arange(blocked.shape[1])[None, :] + sx0 - X0
        score = np.sqrt(np.maximum(ssd, 0) / max(rk.sum(), 1) / 3) + 0.5 * like + 300 * far + 0.02 * (np.abs(ox) + np.abs(oy))
        score[far > FOREIGN] += 1e6   # (ground with colours the ring doesn't have only as a last resort)
        score[blocked > 0.5] = np.inf
        score[(np.abs(ox) < W) & (np.abs(oy) < H)] = np.inf
        k = int(np.argmin(score))
        if not np.isfinite(score.ravel()[k]):
            return None
        a, b = np.unravel_index(k, score.shape)
        return int(ox[0, b]), int(oy[a, 0]), bool(score.ravel()[k] < 1e6)

    def fill(self, mask, X0, Y0, cells=None, ground=None):
        """Fills an erase mask (over a box at X0, Y0): cells drawn over a plain tile from that tile's nearest
        place, the rest by an offset per part. Returns the pixels it could fill."""
        H, W = mask.shape
        done = np.zeros_like(mask)
        r0, c0 = Y0 // TILE_H, X0 // TILE_W - self.side
        for (r, c) in (cells or []):
            g, bm = self.cell_bases.get((r, c)) or (None, None)
            if g is None or g == WHOLE or g == int(self.shapes[r, c]):
                continue
            y, x = (r - r0) * TILE_H, (c - c0) * TILE_W
            part = mask[y:y + TILE_H, x:x + TILE_W] & ~done[y:y + TILE_H, x:x + TILE_W]
            if not part.any():
                continue
            near = self.nearest_tile(g, r, c)
            if near is None:
                continue
            _, rr, cc = near
            self.add_piece(X0 + x, Y0 + y, part.copy(), (cc - c) * TILE_W, (rr - r) * TILE_H)
            done[y:y + TILE_H, x:x + TILE_W] |= part
        rest = mask & ~done
        lab, n = ndimage.label(rest, np.ones((3, 3), bool))
        parts = [(sl[0].start, sl[1].start, lab[sl] == k) for k, sl in enumerate(ndimage.find_objects(lab), 1)
                 if sl is not None]
        def known(part):
            # the share of a part's ring that is ground already (not art still to be filled)
            y, x, sub = part
            h, w = sub.shape
            a0, b0 = max(y - 2, 0), max(x - 2, 0)
            grown = ndimage.binary_dilation(np.pad(sub, 2), iterations=2)[2 - (y - a0):, 2 - (x - b0):]
            grown = grown[:H - a0, :W - b0]
            ring = grown & ~np.pad(sub, 2)[2 - (y - a0):, 2 - (x - b0):][:H - a0, :W - b0]
            todo = (mask & ~done)[a0:a0 + ring.shape[0], b0:b0 + ring.shape[1]]
            return float((ring & ~todo).sum()) / max(ring.sum(), 1)
        while parts:
            # the part with the most of its ring known first, so that the next see the ground filled
            parts.sort(key=known)
            y, x, sub = parts.pop()
            h, w = sub.shape
            off = self.offset_fill(sub, X0 + x, Y0 + y, (mask & ~done)[y:y + h, x:x + w], ground)
            if off is None and max(h, w) <= SPLIT:
                continue
            if (off is None or not off[2]) and max(h, w) > SPLIT:
                # no ground (like the ring's) free and far enough away for the whole part: its quarters,
                # each nearer and smaller
                for a0, a1 in ((0, h // 2), (h // 2, h)) if h > SPLIT else ((0, h),):
                    for b0, b1 in ((0, w // 2), (w // 2, w)) if w > SPLIT else ((0, w),):
                        q = sub[a0:a1, b0:b1]
                        if q.any():
                            ys, xs = np.nonzero(q)
                            parts.append((y + a0 + ys.min(), x + b0 + xs.min(),
                                          q[ys.min():ys.max() + 1, xs.min():xs.max() + 1]))
                continue
            self.add_piece(X0 + x, Y0 + y, sub.copy(), off[0], off[1])
            done[y:y + h, x:x + w] |= sub
        self.erased[Y0:Y0 + H, X0:X0 + W] |= done
        return int(done.sum())

    def whole_cell(self, r, c, g):
        """A generated side column's cell replaced whole by plain tile g (from its nearest place)."""
        x, y = c * TILE_W, r * TILE_H   # (c counts the side columns)
        near = self.nearest_tile(g, r, c - self.side)
        if near is None:
            return False
        _, rr, cc = near
        sx, sy = (cc + self.side) * TILE_W, rr * TILE_H
        self.add_piece(x, y, np.ones((TILE_H, TILE_W), bool), sx - x, sy - y)
        self.erased[y:y + TILE_H, x:x + TILE_W] = True
        return True

    def palm_masks(self, palms):
        """Each painted palm's art: what the bare ground there doesn't explain (fronds, trunk, the soft shadow),
        joined to the green next to the palm, within 1.6 times its size (the shadow 2.7): (x0, y0, mask)."""
        T = tiles(self.tileset)

        def leafy(t):
            c = palette()[t].astype(np.int32)
            return ((c[..., 1] > c[..., 0] * 1.08) & (c[..., 1] > c[..., 2] * 1.02)).sum() >= 6
        bare = [s for s, _ in Counter(self.shapes.ravel().tolist()).most_common(12)
                if plain(self.tileset, s) and T.get(s) is not None and not leafy(T[s])]
        if not bare:
            return []
        hist = np.bincount(T[bare[0]].ravel(), minlength=256) / float(TILE_W * TILE_H)
        rgb = self.rgb.astype(np.int32)
        out = []
        for x, y, size in palms:
            R = int(size * 1.6) + 2
            RS = int(R * 1.7) + 2
            x, y = int(x), int(y)
            y0, x0 = max(y - RS, 0), max(x - RS, 0)
            win = rgb[y0:y + RS + 1, x0:x + RS + 1]
            ix = self.idx[y0:y + RS + 1, x0:x + RS + 1]
            green = (win[..., 1] > win[..., 0] * 1.08) & (win[..., 1] > win[..., 2] * 1.02)
            foreign = hist[ix] < 0.004
            yy, xx = np.mgrid[y0:y0 + win.shape[0], x0:x0 + win.shape[1]]
            d2 = (xx - x) ** 2 + (yy - y) ** 2
            m = (green & (d2 <= R * R)) | (foreign & (d2 <= RS * RS))
            lab, n = ndimage.label(m, np.ones((3, 3), bool))
            near = green & (d2 <= (R * 0.6) ** 2)
            keep = np.unique(lab[near])
            keep = keep[keep > 0]
            if not n or keep.size == 0:
                continue
            m = np.isin(lab, keep)
            m = ndimage.binary_fill_holes(ndimage.binary_closing(m, np.ones((3, 3), bool)) | m)
            out.append((x0, y0, ndimage.binary_dilation(m, iterations=1) & (d2 <= (RS + 1) ** 2)))
        return out


_frames = {}


def frames_of(letter, sprite):
    if (letter, sprite) not in _frames:
        recs = enemy_looks().get((letter, sprite), [])
        _frames[(letter, sprite)] = tuple(sorted({f for r in recs for f in r["frames"]}))
    return _frames[(letter, sprite)]


# --- stand-ins -------------------------------------------------------------------------------------------------
_becomes = None


def becomes_from():
    """look -> the looks of the enemies that turn into it (damaged, dead, or the enemy made when they die): a
    piece logged in such a look (a lens pad already broken) is covered by them too."""
    global _becomes
    if _becomes is None:
        _becomes = defaultdict(set)
        for (letter, sprite), recs in enemy_looks().items():
            for r in recs:
                if r["dgr"]:
                    _becomes[(letter, r["dgr"])].add((letter, sprite))
                if r["die"]:
                    _becomes[(r["die"][0], r["die"][1])].add((letter, sprite))
    return _becomes


def standin_spec(letter, sprite, painted_as_is, overrides):
    """What stands in for a piece's painting: (look letter, sprite, mode, covers), or None (keep the painting).
    mode: "own" (the look's model as it is) or "placeholder" (slumped and darkened)."""
    model, _ = fpr.model_of(letter, sprite)
    if model is None or any(model.startswith(k) for k in overrides.get("keep", [])):
        return None
    covers = {(letter, sprite)} | becomes_from().get((letter, sprite), set())
    dead = None
    for r in enemy_looks().get((letter, sprite), []):
        if r["dgr"]:
            covers.add((letter, r["dgr"]))
            if r["dlevel"] == -1:
                dead = r["dgr"]
        if r["die"]:
            covers.add((r["die"][0], r["die"][1]))
            if r["die"][2]:
                covers.add((r["die"][0], r["die"][2]))
    named = overrides.get("standin", {}).get(f"{fpr_name(letter)}{sprite}")
    if painted_as_is:
        return letter, sprite, "own", covers
    if named:
        nl, ns = parse_look(named)
        if fpr.model_of(nl, ns)[0] is not None:
            covers.add((nl, ns))
            return nl, ns, "own", covers
    if dead and fpr.model_of(letter, dead)[0] is not None:
        return letter, dead, "own", covers
    return letter, sprite, "placeholder", covers


def for_map(overrides, name):
    """The overrides for one map: its own "keep_maps" entry added to "keep"."""
    out = dict(overrides)
    out["keep"] = list(overrides.get("keep", [])) + list(overrides.get("keep_maps", {}).get(name, []))
    return out


def fpr_name(letter):
    return letter if letter.isalnum() else "x%02x" % ord(letter)


def parse_look(text):
    """A look as cleanground.json writes it: a sheet letter (or x<hex> for a symbol) and the first sprite."""
    if text[0] == "x" and len(text) >= 4:
        return chr(int(text[1:3], 16)), int(text[3:])
    return text[0].lower(), int(text[1:])


# --- the two passes --------------------------------------------------------------------------------------------
def analyse(name, overrides):
    """Pass 1 for a map: its objects, what of their art is erased, each piece's stand-in, and the object tiles
    (tile -> (look, large, centre offset in the cell, spec)) the tileset learns from it."""
    cl = Cleaner(name)
    cl.palms = bool(mt.settings(name).get("palms")) and name not in overrides.get("no_palms", [])
    pieces = standing_pieces(name) if os.path.exists(mt.GROUND) else []
    objs = objects(pieces)
    occupied = {rc for p in pieces for rc in p.cells}
    for p in pieces:
        for r, c in p.cells:
            x, y = cl.cell_box(r, c)
            cl.blocked[y:y + TILE_H, x:x + TILE_W] = True
    return cl, objs, occupied


def piece_painted_as_is(p, mask, box):
    """Whether the map paints this piece as its sprite shows it (the art under it the sprite's own pixels)."""
    X0, Y0, W, H = box
    h, w = p.pic.shape
    ys, xs = p.y0 - Y0, p.x0 - X0
    a0, b0, a1, b1 = max(ys, 0), max(xs, 0), min(ys + h, H), min(xs + w, W)
    if a1 <= a0 or b1 <= b0:
        return False
    under = mask[a0:a1, b0:b1] & p.mask[a0 - ys:a1 - ys, b0 - xs:b1 - xs]
    if under.sum() < 30:
        return False
    eq = p.eq[a0 - ys:a1 - ys, b0 - xs:b1 - xs]
    return (under & ~eq).sum() / under.sum() < 0.2


def piece_erased_share(p, mask, box, others=None):
    """How much of the piece's place is erased art: the share of its sprite's pixels, or 1 when its sprite's
    box holds at least 30 erased pixels (a stump or a pad under a small sprite), not counting those under the
    object's other pieces (others: their sprites, in the box; a bunker's base erased under its top's box)."""
    X0, Y0, W, H = box
    h, w = p.pic.shape
    ys, xs = p.y0 - Y0, p.x0 - X0
    a0, b0, a1, b1 = max(ys, 0), max(xs, 0), min(ys + h, H), min(xs + w, W)
    if a1 <= a0 or b1 <= b0:
        return 0.0
    erased = mask[a0:a1, b0:b1]
    if others is not None:
        erased = erased & ~(others[a0:a1, b0:b1] & ~p.mask[a0 - ys:a1 - ys, b0 - xs:b1 - xs])
    if erased.sum() >= 30:
        return 1.0
    return float((mask[a0:a1, b0:b1] & p.mask[a0 - ys:a1 - ys, b0 - xs:b1 - xs]).sum() / max(p.mask.sum(), 1))


_wreck_looks = None


def wreck_looks():
    """The looks models.cfg gives a wreck model ("wreck <sheet> <sprite> <model>")."""
    global _wreck_looks
    if _wreck_looks is None:
        _wreck_looks = set()
        for line in open(os.path.join(ROOT, "assets", "models", "models.cfg")):
            t = line.split()
            if len(t) >= 4 and t[0] == "wreck" and t[3] != "none":
                _wreck_looks.add(parse_look(t[1] + t[2]))
    return _wreck_looks


def sprites_mask(pieces, box):
    """The pieces' sprites in an object's box."""
    X0, Y0, W, H = box
    out = np.zeros((H, W), bool)
    for p in pieces:
        h, w = p.pic.shape
        ys, xs = p.y0 - Y0, p.x0 - X0
        a0, b0, a1, b1 = max(ys, 0), max(xs, 0), min(ys + h, H), min(xs + w, W)
        if a1 > a0 and b1 > b0:
            out[a0:a1, b0:b1] |= p.mask[a0 - ys:a1 - ys, b0 - xs:b1 - xs]
    return out


def build(name, overrides, object_tiles, report):
    """Pass 2 for a map: erase, fill, stand-ins; writes the assets."""
    info = load(name)[0]
    overrides = for_map(overrides, name)
    cl, objs, occupied = analyse(name, overrides)
    s = mt.settings(name)
    standins = []
    stats_out = Counter()
    # palms first: their art is blocked for the objects' fills and left out of the objects' art
    pmasks = []
    if cl.palms:
        palms = painted_palms(name, s)
        pmasks = cl.palm_masks(palms)
        for x0, y0, m in pmasks:
            cl.blocked[y0:y0 + m.shape[0], x0:x0 + m.shape[1]] |= m
            cl.todo[y0:y0 + m.shape[0], x0:x0 + m.shape[1]] |= m
    # the objects (logged), then the copies of their tiles where none stands
    jobs = []
    for g in objs:
        jobs.append((g, sorted({rc for p in g for rc in p.cells}), None))
    if info["background"] == 1:  # (an upper map: only where its riders stand; its tiles' copies elsewhere are landscape)
        jobs += decor_jobs(cl, object_tiles, occupied)
    plans = []
    # (Where the logged objects' stand-ins stand, and the extra ones given so far: one stand-in a tile.)
    standing_cells = {(int(p.y) // TILE_H, int(p.x) // TILE_W - cl.side) for g in objs for p in g}
    for g, cells, touch in jobs:
        if not cells:
            continue
        specs = []
        mask, box = cl.object_mask(g, cells, occupied | set(cells), touch)
        if not mask.any():
            continue
        keep = np.zeros_like(mask)
        sprites = sprites_mask(g, box) if touch is None else None
        for p in g:
            share = piece_erased_share(p, mask, box, sprites) if touch is None else 1.0
            spec = standin_spec(p.letter, p.sprite, piece_painted_as_is(p, mask, box), overrides)
            if spec is None:
                # its painting stays: the art under its sprite is not erased
                X0, Y0, W, H = box
                h, w = p.pic.shape
                ys, xs = p.y0 - Y0, p.x0 - X0
                a0, b0, a1, b1 = max(ys, 0), max(xs, 0), min(ys + h, H), min(xs + w, W)
                if a1 > a0 and b1 > b0:
                    keep[a0:a1, b0:b1] |= ndimage.binary_dilation(p.mask, iterations=3)[a0 - ys:a1 - ys, b0 - xs:b1 - xs]
                stats_out["kept"] += 1
                report.setdefault((fpr.model_of(p.letter, p.sprite)[0] or "-", f"{fpr_name(p.letter)}{p.sprite}"),
                                  Counter())[("-", "kept", "-")] += 1
                continue
            if share >= 0.15:
                specs.append((p, spec))
        # A piece painted as it is beside its object's wrecked pieces is part of the wreck's painting (a
        # pyramid's foot under its broken top): where its look has a wreck model, that stands in for it too.
        if any(sp[2] == "placeholder" for _, sp in specs):
            specs = [(p, (sl, ss, "placeholder", cov) if mode == "own" and (sl, ss) == (p.letter, p.sprite) and
                      (p.letter, p.sprite) in wreck_looks() else (sl, ss, mode, cov)) for p, (sl, ss, mode, cov) in specs]
        if keep.any():
            lab, n = ndimage.label(mask, np.ones((3, 3), bool))
            hit = np.unique(lab[keep & mask])
            mask &= ~np.isin(lab, hit[hit > 0])  # (art joined to a kept piece stays whole)
        if touch is None and specs:
            # An object not set on the tiles' grid (a pod in GBC DELIANI's field of sockets) covers parts of
            # the object tiles round its own, and their art goes too: each such tile erased for the most part
            # gets the stand-in of what stands on it elsewhere, as a copy where none stands does (decor_jobs).
            table = object_tiles.get(cl.tileset, {})
            X0, Y0, W, H = box
            own = {(int(p.y) // TILE_H, int(p.x) // TILE_W - cl.side) for p, _ in specs}
            for r, c in cells:
                if (r, c) in own or (r, c) in standing_cells or not (0 <= r < cl.shapes.shape[0] and 0 <= c < cl.shapes.shape[1]):
                    continue
                if int(cl.shapes[r, c]) not in table:
                    continue
                x, y = cl.cell_box(r, c)
                part = mask[y - Y0:y - Y0 + TILE_H, x - X0:x - X0 + TILE_W]
                if part.size == 0 or part.mean() < 0.3:
                    continue
                p = table_piece(cl, table, r, c)
                # (Not where one of the object's own stands: a tile of the same object's painting, a building over
                # several tiles, puts its piece where the piece already is.)
                if any(abs(p.x - q.x) < TILE_W * 0.75 and abs(p.y - q.y) < TILE_H * 0.75 for q, _ in specs):
                    continue
                spec = standin_spec(p.letter, p.sprite, False, overrides)
                if spec is not None:
                    specs.append((p, spec))
                    own.add((r, c))
                    standing_cells.add((r, c))
        if not mask.any() or not specs:
            continue
        plans.append((cells, touch, mask, box, specs, keep.any(), cl.ground))
    # what the fills may copy: the ground in the objects' cells too, none of the art that goes
    for cells, touch, mask, box, specs, kept, ground in plans:
        for r, c in ([] if kept else cells):
            x, y = cl.cell_box(r, c)
            cl.blocked[y:y + TILE_H, x:x + TILE_W] = False
    for cells, touch, mask, box, specs, kept, ground in plans:
        X0, Y0, W, H = box
        cl.blocked[Y0:Y0 + H, X0:X0 + W] |= ndimage.binary_dilation(mask, iterations=2)
    for cells, touch, mask, box, specs, kept, ground in plans:
        X0, Y0, W, H = box
        n = cl.fill(mask, X0, Y0, cells, ground)
        if n == 0:
            continue
        stats_out["decor" if touch is not None else "objects"] += 1
        stats_out["px"] += n
        group = len(standins) + 1
        for p, (sl, ss, mode, covers) in specs:
            standins.append((p.x, p.y, sl, ss, p.large, mode, group, sorted(covers)))
            stats_out[mode] += 1
            report.setdefault((fpr.model_of(p.letter, p.sprite)[0] or "?", f"{fpr_name(p.letter)}{p.sprite}"),
                              Counter())[(f"{fpr_name(sl)}{ss}", mode, fpr.model_of(sl, ss)[0])] += 1
    # palms
    for x0, y0, m in pmasks:
        ys, xs = np.nonzero(m)
        a0, a1, b0, b1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        sub = m[a0:a1, b0:b1]
        cl.blocked[y0 + a0:y0 + a1, x0 + b0:x0 + b1] &= ~sub
        cl.todo[y0 + a0:y0 + a1, x0 + b0:x0 + b1] &= ~sub
        off = cl.offset_fill(sub, x0 + b0, y0 + a0)
        cl.blocked[y0 + a0:y0 + a1, x0 + b0:x0 + b1] |= sub
        if off is not None:
            cl.add_piece(x0 + b0, y0 + a0, sub.copy(), off[0], off[1])
            cl.erased[y0 + a0:y0 + a1, x0 + b0:x0 + b1] |= sub
            stats_out["palms"] += 1
    # the generated side columns: object tiles replaced whole by fitting plain ones
    grid = full_grid(name)
    tile_set = object_tiles.get(info["tileset"], {})
    for (r, c), shape in np.ndenumerate(grid):
        if (c < cl.side or c >= cl.side + cl.shapes.shape[1]) and int(shape) in tile_set:
            g = fitting_plain(info["tileset"], grid, r, c, set())
            if g is not None and cl.whole_cell(r, c, g):
                grid[r, c] = g
                stats_out["side cells"] += 1
    write_era(name, cl.pieces)
    write_standins(name, standins)
    review(name, cl, standins)
    print(f"{name} ({info['level'].strip()}): " + ", ".join(f"{k} {v}" for k, v in sorted(stats_out.items())), flush=True)
    return stats_out


def learn(object_tiles, cl, p, mask, box):
    """The tileset's object tiles: the tile under a piece's centre, when most of it is the art erased there,
    with the piece that stands on it and its offset from the cell's corner."""
    X0, Y0, W, H = box
    r, c = int(p.y) // TILE_H, int(p.x) // TILE_W - cl.side
    if not (0 <= r < cl.shapes.shape[0] and 0 <= c < cl.shapes.shape[1]):
        return
    y, x = r * TILE_H - Y0, (c + cl.side) * TILE_W - X0
    if not (0 <= y and y + TILE_H <= H and 0 <= x and x + TILE_W <= W):
        return
    share = float(mask[y:y + TILE_H, x:x + TILE_W].mean())
    shape = int(cl.shapes[r, c])
    entry = object_tiles.setdefault(cl.tileset, {}).setdefault(shape, [Counter(), []])
    entry[1].append(share)
    entry[0][(p.letter, p.sprite, p.large, int(round(p.x - (c + cl.side) * TILE_W)), int(round(p.y - r * TILE_H)))] += 1


def table_piece(cl, table, r, c):
    """The piece that stands on an object tile (table: the tileset's object tiles) at its usual offset in cell r, c."""
    (letter, sprite, large, cx, cy), _ = table[int(cl.shapes[r, c])].most_common(1)[0]
    x, y = cl.cell_box(r, c)
    p = Piece()
    p.letter, p.sprite, p.large, p.x, p.y = letter, sprite, large, x + cx, y + cy
    p.pic, p.mask = picture(letter, sprite, large)
    h, w = p.pic.shape
    p.x0, p.y0 = int(round(p.x)) - w // 2, int(round(p.y)) - h // 2
    win = cl.idx[max(p.y0, 0):p.y0 + h, max(p.x0, 0):p.x0 + w]
    p.eq = np.zeros_like(p.mask)
    if win.shape == p.pic.shape:
        p.eq = (win == p.pic) & p.mask
    p.cells = [(r, c)]
    p.group = p.link = 0
    return p


def decor_jobs(cl, object_tiles, occupied):
    """The copies: clusters of object tiles where no logged enemy stands, as objects of the pieces that stand on
    those tiles elsewhere (each at its usual offset)."""
    table = object_tiles.get(cl.tileset, {})
    if not table:
        return []
    m = np.isin(cl.shapes, list(table))
    for r, c in occupied:
        m[r, c] = False
    lab, n = ndimage.label(m, np.ones((3, 3), bool))
    jobs = []
    for k, sl in enumerate(ndimage.find_objects(lab), 1):
        cells = [(r, c) for r in range(sl[0].start, sl[0].stop) for c in range(sl[1].start, sl[1].stop) if lab[r, c] == k]
        pieces = [table_piece(cl, table, r, c) for r, c in cells]
        r0, c0 = min(r for r, _ in cells), min(c for _, c in cells)
        r1, c1 = max(r for r, _ in cells) + 1, max(c for _, c in cells) + 1
        touch = np.zeros(((r1 - r0) * TILE_H, (c1 - c0) * TILE_W), bool)
        for r, c in cells:
            touch[(r - r0) * TILE_H:(r - r0 + 1) * TILE_H, (c - c0) * TILE_W:(c - c0 + 1) * TILE_W] = True
        jobs.append((pieces, cells, touch))
    return jobs


def painted_palms(name, s):
    """The painted palms where make_vegetation.py puts its 3D palms (the same detection): (x, y, size)."""
    import make_vegetation as mv
    info, rgb, _ = mt.load_map(name)
    plants, _, _ = mv.detect(name, rgb, s, rgb)
    return [(x, y, size) for x, y, kind, size, turn, shade in plants if kind == mv.PALM]


# --- writing ---------------------------------------------------------------------------------------------------
def split(pieces):
    """The pieces cut along the tile grid, so that no erasure is larger than a tile (the loader's limit)."""
    out = []
    for x0, y0, m, dx, dy in pieces:
        h, w = m.shape
        for ty in range(y0 // TILE_H * TILE_H, y0 + h, TILE_H):
            for tx in range(x0 // TILE_W * TILE_W, x0 + w, TILE_W):
                a0, a1 = max(ty, y0), min(ty + TILE_H, y0 + h)
                b0, b1 = max(tx, x0), min(tx + TILE_W, x0 + w)
                sub = m[a0 - y0:a1 - y0, b0 - x0:b1 - x0]
                if not sub.any():
                    continue
                ys, xs = np.nonzero(sub)
                sub = sub[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
                out.append((b0 + int(xs.min()), a0 + int(ys.min()), sub, dx, dy))
    return out


def write_era(name, pieces):
    path = os.path.join(mt.OUT, f"{name}.era")
    parts = split(pieces)
    if not parts:
        if os.path.exists(path):
            os.remove(path)
        return
    parts.sort(key=lambda p: (p[1], p[0]))
    blob = b"".join(struct.pack("<HHBBhh", x, y, m.shape[1], m.shape[0], dx, dy) + m.astype(np.uint8).tobytes()
                    for x, y, m, dx, dy in parts)
    with open(path, "wb") as f:
        f.write(struct.pack("<4sII", b"TYER", 1, len(parts)) + zlib.compress(blob, 9))


def write_standins(name, standins):
    """assets/terrain/<map>.std: a stand-in a line, "x y look large mode group covers...", in order of y:
    x, y the map's pixels (the generated columns included) of the piece's centre; look as <sheet code>:<sprite>
    (the sheet's letter's character code, as the ground log has it); large 1 for a 2x2 sprite; mode own or
    placeholder; group: the stand-ins of one object (they lean together); covers: the looks that hide it."""
    path = os.path.join(mt.OUT, f"{name}.std")
    if not standins:
        if os.path.exists(path):
            os.remove(path)
        return
    lines = ["# Tyrian3D stand-ins (tools/terrain/make_cleanground.py): x y look large mode group covers..."]
    for x, y, letter, sprite, large, mode, group, covers in sorted(standins, key=lambda s: (s[1], s[0])):
        cov = " ".join(f"{letter_code(l)}:{s}" for l, s in covers)
        lines.append(f"{x:.1f} {y:.1f} {letter_code(letter)}:{sprite} {int(large)} {mode} {group} {cov}")
    open(path, "w", newline="\n").write("\n".join(lines) + "\n")  # (LF on Windows too)


def review(name, cl, standins):
    """The level's start (its last REVIEW rows), the map | the clean ground, the stand-ins ringed."""
    rows = 2100
    top = max(cl.idx.shape[0] - rows, 0)
    after = cl.idx.copy()
    for x0, y0, m, dx, dy in cl.pieces:
        ys, xs = np.nonzero(m)
        after[y0 + ys, x0 + xs] = cl.idx[y0 + ys + dy, x0 + xs + dx]
    pal = palette()
    a = Image.fromarray(pal[cl.idx[top:]])
    b = Image.fromarray(pal[after[top:]])
    d = ImageDraw.Draw(b)
    for x, y, letter, sprite, large, mode, group, covers in standins:
        if y >= top:
            colour = (0, 255, 255) if mode == "own" else (255, 0, 255)
            d.ellipse((x - 7, y - top - 7, x + 7, y - top + 7), outline=colour)
    out = Image.new("RGB", (a.width * 2 + 8, a.height), (255, 255, 255))
    out.paste(a, (0, 0))
    out.paste(b, (a.width + 8, 0))
    out.resize((out.width // 2, out.height // 2), Image.LANCZOS).save(os.path.join(mt.REVIEW, f"{name}_clean.png"))


def learn_object_tiles(learn_from, overrides):
    """Pass 1: the object tiles each tileset learns from its original maps' logged objects (what stands on which
    tile): {tileset: {shape: Counter of (letter, sprite, large, dx, dy)}}. (tools/gbc/episode.py keeps them out
    of the GBC maps' ground: each copy there would be erased, a stand-in on it.)"""
    object_tiles = {}
    for n in learn_from:
        if derived(load(n)[0]):
            continue
        cl, objs, occupied = analyse(n, overrides)
        here = for_map(overrides, n)
        for g in objs:
            cells = sorted({rc for p in g for rc in p.cells})
            if not cells:
                continue
            mask, box = cl.object_mask(g, cells, occupied | set(cells))
            if not mask.any():
                continue
            for p in g:
                if standin_spec(p.letter, p.sprite, False, here) is None or piece_erased_share(p, mask, box) < 0.15:
                    continue
                learn(object_tiles, cl, p, mask, box)
    # object tiles: not plain ground, and mostly art where the objects stand on them; a tile the maps use
    # mostly elsewhere (landscape an object stood on: a shore under a manta) only when seen so more than once
    for ts, table in object_tiles.items():
        for shape in list(table):
            art = float(np.median(table[shape][1]))
            if plain(ts, shape) or art < 0.3 or (not own_tile(ts, shape) and (art < 0.5 or len(table[shape][1]) < 2)):
                del table[shape]
            else:
                table[shape] = table[shape][0]
    return object_tiles


def tileset_object_tiles(tileset):
    """The object tiles of one tileset (learn_object_tiles over its original maps): a set of shapes."""
    overrides = json.load(open(OVERRIDES)) if os.path.exists(OVERRIDES) else {}
    maps = tileset_maps(tileset)
    mt.read_ground_log(maps)
    return set(learn_object_tiles(maps, overrides).get(tileset, {}))


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    overrides = json.load(open(OVERRIDES)) if os.path.exists(OVERRIDES) else {}
    every = sorted(os.path.basename(f)[4:-5] for f in glob.glob(os.path.join(mt.MAPS, "map_*.json"))
                   if json.load(open(f))["background"] == 1)
    every += sorted(overrides.get("upper_maps", {}))  # background 3's maps, for the top enemies riding them
    names = every if sys.argv[1:] == ["all"] else sys.argv[1:]
    skipped = [n for n in names if n in overrides.get("skip_maps", {})]
    for n in skipped:
        print(f"{n}: skipped ({overrides['skip_maps'][n]}), its assets stay as they are")
    names = [n for n in names if n not in skipped]
    tilesets = sorted({load(n)[0]["tileset"] for n in names})
    learn_from = [n for n in every if load(n)[0]["tileset"] in tilesets]
    mt.read_ground_log(learn_from)
    object_tiles = learn_object_tiles(learn_from, overrides)
    print("object tiles:", {ts: len(t) for ts, t in object_tiles.items()}, flush=True)
    report = {}
    totals = Counter()
    for n in names:
        totals.update(build(n, overrides, object_tiles, report))
    print("total:", dict(totals))
    lines = ["# the stand-ins per look: <model> <look> -> <stand-in look> <mode> <its model> x<count>",
             "# (kept: the painting stays, the look has no model or is in cleanground.json's keep)"]
    for (model, look), c in sorted(report.items()):
        for (sl, mode, smodel), k in c.most_common():
            lines.append(f"{model} {look} -> {sl} {mode} {smodel} x{k}")
    open(os.path.join(mt.REVIEW, "standins.txt"), "w").write("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
