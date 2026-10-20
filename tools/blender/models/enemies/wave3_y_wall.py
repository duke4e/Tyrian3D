"""Batch Y of wave 3 (sheet 8): the rock wall of IXMUCANE and SAWBLADES, modelled as its sprites look
(models.cfg: yaw=0). The kit is wave3_y_kit.py, the pixels wave3_y_art.py (WALL).

The levels build the wall from 2x2 sprites, one column of three (top, middle, bottom) every 24 pixels:
a left end (8 169 / 207 / 245), a slot (277 / 203 / 241), one or three rock columns (167 / 205 / 243),
a slot again and a right end (161 / 199 / 237), all on one layer (events 6, 7, 10 or 15).

- ixm_wall_slot_top, _mid, _low (8 277, 203, 241): a red machine set into the wall between rocks: a
  housing with a lip at the back and a glowing window on top (277's frames brighten it: it glows), a
  smaller lit panel, two bars at the top's front edge and, down the cliff, a grille of red bars over a
  dark well, ending in a red foot.
- ixm_wall_end_l_top, _mid, _low (8 169, 207, 245) and ixm_wall_end_r_top, _mid, _low (8 161, 199, 237):
  the wall's ends, the rock rounding off.

Each column's left and right edges have the same section (the ridge, its boulders faded out at the edges),
so the columns meet whatever their neighbours; every piece is cut from its column and drawn at its own
origin (origin). ixm_wall_end_l_low replaces rock_tip (8 245, wave2_g.py), a low tip made alone.
The rock column (8 167, 205, 243) stays in the whole, so that its neighbours keep their overlap with it, but its
pieces, ixm_wall_rock_top, _mid and _low, are polish_ixm_wall_rock.py's.

The wall stands upright. The sprites draw it in the game's oblique view: its top of boulders (rows 0-44) and,
below it, its face of rock ribs (rows 44-69) seen from the front. Modelled as drawn, the face was a long ramp
falling down the screen; now the wall is built as drawn and then stood up (upright()): the face turned into a
vertical cliff, HEIGHT (20) pixels high, its ribs standing out of it and a dark cliff behind them where the
sprites show gaps between them, and the top moved SHIFT (14) pixels down the screen onto the cliff. The cliff
stands at y -16.5, between the drawn foot (-28.5) and the drawn edge of the top (-2.5), so that every piece keeps
a part of the wall (its footprint y -16.5 .. 27.5; from the game's tilted camera the top shows about where the
sprites draw it); the slot's window lies in the middle piece.

usage: Blender -b --factory-startup -P wave3_y_wall.py -- [--only names] [--preview <prefix>] [--check 1]
       [--whole <prefix>]
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_y_kit as y  # noqa: E402
from wave3_y_kit import k, sh, pal, tube, smoothstep  # noqa: E402

WALL = y.frame("WALL", 96, (48, 42))  # whole coordinates: x -48..48, y -42..42
SLOT_HOT = y.frame("SLOT_HOT", 24, (12, 14))
CREST = 15.0        # the height of the ridge's top
FRONT = 6.0         # where the ridge starts falling (y)
FOOT = -28.5        # where it reaches the ground (y)
EDGE = -2.5         # where the top ends and the face begins, as drawn (y; row 44)
FACE = EDGE - FOOT  # the face's height as drawn (down the screen)
HEIGHT = 20.0       # the wall's height, stood up
SHIFT = 14.0        # how far the top moves down the screen when the wall stands up (the cliff at EDGE - SHIFT)
COLUMNS = [("end_l", -36.0, (169, 207, 245)), ("slot", -12.0, (277, 203, 241)), ("rock", 12.0, (167, 205, 243)),
           ("end_r", 36.0, (161, 199, 237))]


def ridge(yy):
    """The ridge's height without its boulders."""
    if yy >= FRONT:
        return CREST
    t = max(0.0, (yy - FOOT) / (FRONT - FOOT))
    return 0.6 + (CREST - 0.6) * (1.0 - (1.0 - t) ** 1.6)


def rock_mats():
    shades = {}
    for s_ in range(0, 15):
        shades[s_] = pal(f"wall_rock{s_}", 0x10 + s_, metallic=0.05, roughness=0.8)
    return shades


def is_slot(c, r):
    """The slot's machine: columns 5-16 of the slot column (whole columns 29-40), rows 4-61."""
    return 29 <= c <= 40 and 4 <= r <= 61


def column_mask(c0):
    """The column's rock pixels (columns c0 .. c0 + 23 of the wall art), its edge columns repeated 6 pixels
    outwards (so that the heightfield runs on level through the cuts)."""
    g = WALL.g
    rows = []
    for r in range(len(g)):
        line = []
        for c in range(len(g[0])):
            if c < c0 - 6 or c > c0 + 29:
                line.append(".")
                continue
            cc = min(max(c, c0), c0 + 23)
            # The ends: only their outer edge column is not repeated (they round off outwards).
            v = g[r][cc]
            line.append("#" if v is not None and not is_slot(cc, r) else ".")
        rows.append("".join(line))
    return rows


def rock_height(fade_x0, fade_x1):
    """z(x, y, e) of a column's rock: the ridge plus boulders from the sprite's shades (lighter higher),
    the boulders faded out within 2 pixels of the column's edges, the outline rounded."""
    shade = WALL.shade(1, 1)
    dark = y.sampler(WALL.g, (48, 42), value=lambda v: 1.0 if v == 0x01 else 0.0, blur=1,
                     keep=lambda v: v is not None)

    def z(x, yy, e):
        base = ridge(yy)
        s_ = shade(x, yy) - 6.0 * dark(x, yy)
        bump = 2.4 * max(-1.0, min(1.0, (s_ - 7.0) / 5.5))
        fade = smoothstep(0.0, 2.0, x - fade_x0) * smoothstep(0.0, 2.0, fade_x1 - x)
        h = base + bump * fade * (0.55 + 0.45 * min(1.0, base / 6.0))
        return max(0.3, h * (0.25 + 0.75 * e))
    return z


def paint_rock(obj, mats):
    """Paints the rock by the sprite's shades, smoothed (fewer pixel speckles): the crevices it draws
    black darkest, steep faces darker, in every other shade."""
    shade = WALL.shade(1, 1)
    dark = y.sampler(WALL.g, (48, 42), value=lambda v: 1.0 if v == 0x01 else 0.0, blur=0,
                     keep=lambda v: v is not None)

    def pick(c, nrm):
        if nrm.z < -0.3:
            return mats[1]
        s_ = shade(c.x, c.y) - 5.0 * dark(c.x, c.y)
        if nrm.z < 0.45:
            s_ -= 2.5
        s_ = 2 * round((s_ + 1.0) / 2) - 1  # odd shades only
        return mats[int(max(1, min(13, s_)))]
    return y.paint_faces(obj, pick)


def build_backing(name, c0, mat):
    """The cliff behind the face's ribs, which shows between them once the wall stands: the column's face rows
    (from just above EDGE down) filled across between their outermost rock pixels, 1.2 pixels under the ridge's
    surface (behind the ribs)."""
    rows = column_mask(c0)
    filled = []
    for r, line in enumerate(rows):
        cols = [c for c, ch in enumerate(line) if ch == "#"]
        if 42 - (r + 0.5) > EDGE + 1.5 or not cols:
            filled.append("." * len(line))
            continue
        filled.append("." * cols[0] + "#" * (cols[-1] - cols[0] + 1) + "." * (len(line) - cols[-1] - 1))
    polys = sh.outlines(filled, "#", (48, 42), smooth=2, epsilon=0.35, min_area=1.0)
    obj = y.heightfield(name, polys, lambda x, yy: max(0.3, ridge(yy) - 1.2), mat, spacing=0.6)
    y.simplify_bottom(obj)
    return obj


def upright(objects):
    """Stands the wall up: every vertex of the parts built as drawn (the top above EDGE, the face below it,
    its surface at ridge(y)) moved to the upright wall: the top's down the screen by SHIFT, raised so that the
    ridge's surface lies at HEIGHT (what stands out of it, the boulders, as high as drawn); the face's turned into
    a vertical cliff at y EDGE - SHIFT (the drawn foot at the ground, EDGE at HEIGHT), what stood out of the
    ridge's surface standing out of the cliff towards the viewer (down the screen), what lay under it (the
    part's underside, its rounded rims) at most a pixel behind the cliff, a thin shell over the cliff."""
    for obj in objects:
        mesh = obj.data
        for v in mesh.vertices:
            x, yd, zd = v.co
            base = ridge(yd)
            if yd >= EDGE:
                v.co = (x, yd - SHIFT, min(zd, base) * HEIGHT / base + max(0.0, zd - base))
            else:
                v.co = (x, EDGE - SHIFT - max(zd - base, -1.0), HEIGHT * max(0.0, (yd - FOOT) / FACE))
        mesh.update()
    return objects


def build_column(name, c0, mats, ends=None):
    """The rock of one column (art columns c0 .. c0 + 23): a heightfield over its pixels."""
    x0 = c0 - 48.0
    rows = column_mask(c0)
    polys = sh.outlines(rows, "#", (48, 42), smooth=2, epsilon=0.35, min_area=1.0)
    fade0, fade1 = (x0, x0 + 24.0)
    obj = y.heightfield(name, polys, rock_height(fade0, fade1), mats[8], spacing=0.6, edge=3.2)
    y.simplify_bottom(obj)
    y.decimate(obj, 9000)
    paint_rock(obj, mats)
    return obj


# --- The slot's machine ------------------------------------------------------------------------------

def slot_machine(cx):
    """The red machine of the slot column whose centre is at x = cx (its axis 1 pixel left of it)."""
    ax = cx - 1.0
    red = pal("slot_red", 0x73, metallic=0.5, roughness=0.3)
    red_light = pal("slot_red_light", 0x76, metallic=0.5, roughness=0.25)
    red_dark = pal("slot_red_dark", 0x70, metallic=0.45, roughness=0.4)
    well = pal("slot_well", 0x01, metallic=0.2, roughness=0.7)
    lip = pal("slot_lip", 0x7b, metallic=0.2, roughness=0.25, glow=0.7)
    window = pal("slot_window", 0x7a, metallic=0.0, roughness=0.2, glow=2.4)
    window_core = pal("slot_window_core", 0x7e, metallic=0.0, roughness=0.2, glow=3.0)
    panel_light = pal("slot_panel_light", 0x77, metallic=0.0, roughness=0.3, glow=1.2)

    def surf(yy):
        return ridge(yy)

    # The housing: a block level with the ridge's top from the back edge to y 9.5.
    top = CREST + 0.4
    house = y.slab("house", [(ax - 6.0, 9.5), (ax + 6.0, 9.5), (ax + 6.0, 37.6), (ax - 6.0, 37.6)], 0.0, top, red,
                   bevel=0.7, segments=2)
    y.paint_faces(house, lambda c, nrm: red_dark if nrm.z < 0.5 else None)
    # The lip at its back edge, catching the light.
    tube("lip", [(ax - 5.6, 35.6, top + 0.1), (ax + 5.6, 35.6, top + 0.1)], 1.1, lip, 12)
    # The window's frame and the glowing pane in it.
    y.rounded_box("window_frame", (ax, 23.4, top), (7.6, 12.0, 1.0), red_dark, bevel=0.4)
    y.rounded_box("window", (ax + 0.1, 23.4, top + 0.25), (5.2, 9.6, 0.9), window, bevel=0.35)
    y.rounded_box("window_core", (ax + 0.1, 23.2, top + 0.55), (3.4, 6.6, 0.6), window_core, bevel=0.25)
    # A band across under it and the small lit panel.
    y.rounded_box("band", (ax, 16.8, top + 0.05), (11.0, 1.6, 0.8), red_dark, bevel=0.3)
    y.rounded_box("panel", (ax + 0.5, 12.2, top + 0.1), (6.0, 2.8, 0.7), panel_light, bevel=0.3)
    y.rounded_box("panel_frame", (ax + 0.5, 12.2, top - 0.15), (8.2, 4.2, 0.8), red_light, bevel=0.35)

    # Down the front slope: two bars, then a grille over a dark well, then a red foot.
    def slope_block(name, x0, x1, ya, yb, lift, mat, depth=2.0, bevel=0.35):
        pts = []
        steps = max(2, int(abs(ya - yb) / 0.8))
        for i in range(steps + 1):
            yy = ya + (yb - ya) * i / steps
            pts.append((yy, surf(yy) + lift))
        outline = [(yy, z) for yy, z in pts] + [(yy, z - depth) for yy, z in reversed(pts)]
        return y.prism_x(name, outline, x0, x1, mat, bevel=bevel, segments=1)
    slope_block("bar_l", ax - 3.8, ax - 1.1, 10.0, -1.5, 0.5, red_light, depth=3.0)
    slope_block("bar_r", ax + 0.0, ax + 3.6, 10.0, -1.5, 0.5, red, depth=3.0)
    slope_block("well", ax - 5.0, ax + 4.5, -1.0, -18.8, -0.4, well, depth=3.0)
    for i, yy in enumerate((-3.5, -5.5, -7.5, -9.5)):
        half = 4.6 - 0.2 * i
        z = surf(yy) + 0.2
        tube(f"grille{i}", [(ax - half, yy, z), (ax + half, yy, z)], 0.6, red_light if i % 2 == 0 else red, 10)
    slope_block("foot", ax - 4.2, ax + 4.0, -11.2, -18.0, 0.5, red, depth=3.0)
    slope_block("foot_rim", ax - 4.7, ax + 4.5, -17.6, -19.6, 0.1, red_dark, depth=2.0)


# --- The whole and its pieces ----------------------------------------------------------------------------

def build_wall(stand=True):
    """The whole wall, upright (stand=False: as drawn, for painting by the sprites' pixels; then upright())."""
    mats = rock_mats()
    for name, cx, _ in COLUMNS:
        c0 = int(cx - 12 + 48)
        build_column(f"rock_{name}", c0, mats)
        build_backing(f"rock_back_{name}", c0, mats[3])
    slot_machine(-12.0)
    if stand:
        y.bake()
        upright(y.meshes())


PIECES = []
for _name, _cx, _sprites in COLUMNS:
    if _name == "rock":  # (its pieces: polish_ixm_wall_rock.py)
        continue
    for _row, (_suffix, _y0) in enumerate((("top", 14.0), ("mid", -14.0), ("low", -42.0))):
        _sprite = _sprites[_row]
        _box = (_cx - 12.0, _cx + 12.0, _y0, _y0 + 28.0)
        _c0 = int(_cx - 12 + 48)
        _r0 = int(42 - (_y0 + 28.0))
        PIECES.append((f"ixm_wall_{_name}_{_suffix}", _box, (_cx, _y0 + 14.0),
                       (lambda c0=_c0, r0=_r0: y.frame_mask(WALL, (c0, c0 + 24, r0, r0 + 28)))))

y.pieced("ixm_wall", build_wall, (96, 84), PIECES)


if __name__ == "__main__":
    y.run()
