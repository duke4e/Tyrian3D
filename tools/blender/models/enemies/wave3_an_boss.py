"""Batch AN of wave 3 (sheet n, written n in models.cfg): GYGES' boss, the great maw, and its damaged look, modelled as
the sprites look (models.cfg: yaw=0), built whole and cut into its sprites' pieces, drawn at their own origins
(origin) so they meet. The kit is wave3_an_kit.py, the pixels wave3_an_art.py (BOSS, BOSS_OPEN, BOSS_DMG).

The level events (GYGES) put the boss together from 24 sprites, all sky enemies (366-389), in rows spawned 14 ticks
apart (28 pixels), as the sheet lays them out: 193 195 197 at (102, 0) ... (150, 0) first, then 153 155 157 159 161
at (78, 0) ... (174, 0), 115-123, 77-85, 41 43 45 at (102, 0) ..., 3 5 7 last: 120 x 168 pixels (the bottom row
holds only the chin), origin (60, 84). The beast is symmetric about pixel column 63 (x = 3.5).

What it is: a huge beast seen from above, its maw down the screen. On its back a carapace of dark blue-grey plates:
two knobs at its top, big lobes either side of a purple spine that swells into three warty bulbs, two purple-rimmed
spiracles beside its neck; great shoulder lobes; a wrinkled face with three glowing red eyes either side; the maw:
a ring of fleshy pink lips, fangs (two long ones from the top lip) leaning into a deep red throat ridged in rings;
a purple horn either side of the jaw, glossy dark tendrils dripping from the face's sides, a drip under the chin.

- gyges_maw_<sprite> for the 24 sprites (3 5 7, 41 43 45, 77-85, 115-123, 153-161, 193 195 197). The four in the
  maw's middle (119 121 157 159) open it when the boss fires (frames 229-243, 267-281: the teeth fold back and a
  fireball swells in the throat); the models keep it as it is drawn the rest of the time (frame 0).
- The damaged looks (dgr: each piece switches to its own when hit hard, in place): gyges_maw_51 53 55 (of 41-45),
  87 89 91 93 18 (of 77-85), 127 129 131 (of 117-121), 165 167 169 (of 155-159): the spine torn open into raw red
  flesh, the right shoulder's plating torn away over bare ribs, the left back gouged, a gash down the face, the
  eyes put out but the lowest right one, the throat dark and bloody, the right fang snapped. The other pieces'
  damaged sprites are their own (3 5 7 115 123 153 161 193-197), so their models serve both. Same shapes as the
  intact pieces (so that they swap in place), painted by the damaged sprites.

usage: Blender -b --factory-startup -P wave3_an_boss.py -- [--only names] [--preview <prefix>] [--check 1]
       [--stats 1] [--whole <prefix>]
"""
import math
import os
import random
import sys

from mathutils import Vector, noise

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_an_kit as kit  # noqa: E402
from wave3_an_kit import k, sh, w, pal, Painter, smoothstep, blob, soft_union  # noqa: E402

ORIGIN = (60, 84)
AXC = 63.0         # the axis: pixel column 63 (column c mirrors 126 - c)
AX = AXC + 0.5 - ORIGIN[0]

BOSS = kit.frame("BOSS", 120, ORIGIN)
DMG = kit.frame("BOSS_DMG", 120, ORIGIN)


def X(c):
    return c + 0.5 - ORIGIN[0]


def Y(r):
    return ORIGIN[1] - (r + 0.5)


def col_of(x):
    return x + ORIGIN[0] - 0.5


def row_of(y):
    return ORIGIN[1] - y - 0.5


def mc(c):
    """A pixel column mirrored about the axis."""
    return 2 * AXC - c


# --- Regions --------------------------------------------------------------------------------------------------

def tendril_bound(r):
    """Left of this pixel column (right of its mirror) the rows 96-125 hold the tendrils dripping from the face."""
    for r0, r1, c in ((96, 100, 11), (101, 102, 14), (103, 109, 21), (110, 112, 22), (113, 125, 26)):
        if r0 <= r <= r1:
            return c
    return -1


def is_tendril(c, r):
    b = tendril_bound(r)
    return c < b or c > mc(b)


def back_clip(c, r):
    """The back (rows 14-55), cut by the sprites' edges at columns 24 and 95, with its outer corners rounded."""
    if not 12 <= r <= 56:
        return True
    dy = abs(r - 37.0) / 26.0
    half = 36.6 * max(0.0, 1.0 - dy ** 4) ** 0.25
    return 59.5 - half <= c + 0.5 <= 60.5 + half - 1.0


def stray(c, r):
    """The clipped tips of something beyond the sprites at the shoulders' top (rows 56-57, far out)."""
    return 56 <= r <= 57 and (c < 13 or c > 113)


POCKETS = [(36, 50, 16, 28), (76, 91, 16, 28), (44, 83, 40, 58), (54, 73, 7, 11), (40, 87, 93, 141),
           (12, 30, 98, 112), (96, 115, 98, 112)]


def closed(f):
    """The frame with its slits and holes closed (the spiracles, the gaps round the spine's bulbs, the cap's
    slits, the maw's gaps between the teeth) and its strays left out."""
    def inside(c, r):
        return any(c0 <= c <= c1 and r0 <= r <= r1 for c0, c1, r0, r1 in POCKETS)
    out = kit.filled(f, inside)
    for r in range(out.height):
        for c in range(out.width):
            if stray(c, r) or not back_clip(c, r):
                out.g[r][c] = None
    # A stray dark pixel or two at the tendrils' tips, as the sprite has none of them beyond the bulbs.
    return out


# --- Heights -------------------------------------------------------------------------------------------------------

# Blobs of the body (pixel column, row, radii, height); those off the axis come in mirrored pairs.
BLOBS = [
    (58.5, 6.5, 6.5, 5.0, 16.0), (63.0, 11.0, 24.0, 4.5, 14.5),          # the cap: two knobs on a ridge
    (49.0, 19.5, 10.5, 9.0, 20.5), (36.0, 42.0, 13.0, 17.0, 20.0),      # the back's lobes
    (30.0, 24.0, 7.5, 9.0, 14.0), (63.0, 22.0, 7.0, 10.0, 18.0),
    (63.0, 40.0, 19.0, 15.0, 19.0), (63.0, 66.0, 14.0, 13.0, 22.0),     # under the spine
    (34.0, 66.5, 21.0, 13.5, 25.0), (19.0, 73.0, 9.0, 11.0, 15.0),      # the shoulders
    (63.0, 90.0, 42.0, 16.0, 28.0), (28.0, 93.0, 18.0, 15.0, 22.0),     # the face
    (36.0, 119.0, 14.0, 18.0, 17.0), (63.0, 127.0, 30.0, 21.0, 21.0),   # the cheeks, the jaw
    (63.0, 143.5, 24.0, 6.5, 11.0), (14.0, 101.0, 7.0, 12.0, 9.0),      # the chin, the face's outer edge
]

# The maw: the lips' outer edge, its half-width (pixels from the axis) by row.
MOUTH_W = {91: 10, 92: 11, 93: 12, 94: 12, 95: 16, 96: 17, 97: 18.5, 98: 20, 99: 20.5, 100: 21, 101: 22, 102: 26,
           103: 27, 104: 28, 105: 28, 106: 28, 107: 28, 108: 28, 109: 28, 110: 27, 111: 26, 112: 26, 113: 25, 114: 24,
           115: 23.5, 116: 24, 117: 24, 118: 24, 119: 23, 120: 22, 121: 21, 122: 19.5, 123: 19, 124: 19, 125: 19,
           126: 18, 127: 18, 128: 18, 129: 18, 130: 18, 131: 17, 132: 17, 133: 17, 134: 17, 135: 17, 136: 17, 137: 17,
           138: 14, 139: 12, 140: 12, 141: 7}
DEEP = (63.0, 103.5)                    # the throat's deepest point, under the top lip
EYES = [(37.5, 81.2, 2.2, 2.0), (32.4, 88.5, 2.2, 2.0), (29.9, 96.8, 1.9, 2.1)]   # the left eyes; mirrored
SPIRACLES = [(42.6, 23.6, 4.8, 2.6)]   # the left one; mirrored


def in_mouth(c, r):
    return r in MOUTH_W and abs(c - AXC) <= MOUTH_W[r] + 0.01


def mouth_depth_field():
    """A function (x, y) -> how far a point lies inside the maw's outline (pixels; negative outside)."""
    box = [(c, r) for r in range(84, 149) for c in range(26, 101)]
    inside = {(c, r) for c, r in box if in_mouth(c, r)}
    steps = ((1, 0), (-1, 0), (0, 1), (0, -1))
    edge = [(c, r) for c, r in inside if any((c + dc, r + dr) not in inside for dc, dr in steps)]
    outside_edge = [(c, r) for c, r in box if (c, r) not in inside and
                    any((c + dc, r + dr) in inside for dc, dr in steps)]
    g = [[None] * 120 for _ in range(168)]
    for c, r in box:
        if (c, r) in inside:
            d = min(math.hypot(c - a, r - b) for a, b in outside_edge) - 0.5
        else:
            d = -(min(math.hypot(c - a, r - b) for a, b in edge) - 0.5)
        g[r][c] = d
    return w.sampler(g, ORIGIN, value=lambda val: val, blur=1, keep=lambda val: val is not None)


_MOUTH_D = None


def mouth_d(c, r):
    global _MOUTH_D
    if _MOUTH_D is None:
        _MOUTH_D = mouth_depth_field()
    if not (84 <= r <= 148 and 26 <= c <= 100):
        return -10.0
    return _MOUTH_D(X(c), Y(r))


def body_height(c, r):
    u = abs(c - AXC)
    cm = AXC - u                       # the left half's column
    hs = []
    for bc, br, rx, ry, top in BLOBS:
        hs.append(blob(cm, r, bc, br, rx, ry, top))
    h = soft_union(hs, 4.0)
    return max(h, 4.0)


def throat_floor(c, r):
    """The throat's floor: rings descending to its deepest point under the top lip."""
    dc = (c - DEEP[0]) / 24.0
    dr = (r - DEEP[1]) / (30.0 if r > DEEP[1] else 9.0)
    s = min(1.0, math.hypot(dc, dr))
    return 2.0 + 17.0 * s ** 1.3


def height(c, r):
    h = body_height(c, r)
    d = mouth_d(c, r)
    if d > 2.0:
        t = smoothstep(2.5, 8.5, d)
        h = h - (h - throat_floor(c, r)) * t
    u = abs(c - AXC)
    cm = AXC - u
    for ec, er, rx, ry in EYES:        # the eyes' sockets
        d2 = ((cm - ec) / (rx + 1.6)) ** 2 + ((r - er) / (ry + 1.6)) ** 2
        h -= 2.6 * math.exp(-2.0 * d2)
    for sc, sr, rx, ry in SPIRACLES:   # the spiracles: deep holes
        d2 = ((cm - sc) / rx) ** 2 + ((r - sr) / ry) ** 2
        if d2 < 1.0:
            h -= 9.0 * (1.0 - d2) ** 0.5
    return max(h, 1.0)


# --- Painting ------------------------------------------------------------------------------------------------------

def painter(prefix, raw=False):
    """The beast's materials by palette index; raw: its red the raw flesh of wounds (wet, faintly lit)."""
    glow = {0x78: 0.5, 0x79: 0.7, 0x7a: 0.9, 0x7c: 1.2, 0xff: 0.6}
    if raw:
        glow.update({0x73: 0.15, 0x74: 0.2, 0x75: 0.25, 0x76: 0.3, 0x77: 0.4})
    return Painter(prefix, shades={0: (1, 2, 3, 5, 7, 9, 0xb), 6: tuple(range(0, 16)), 5: tuple(range(0, 14)),
                                   4: tuple(range(0, 16)), 7: (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0xa, 0xc),
                                   10: tuple(range(0, 15)), 1: (0, 1, 3), 15: (15,)},
                   metallic=0.12, roughness=0.48,
                   glow=glow,
                   finish={4: (0.05, 0.32), 7: (0.05, 0.22 if raw else 0.34), 10: (0.05, 0.4), 5: (0.1, 0.4),
                           15: (0.0, 0.1)},
                   remap={0x01: 0x60, 0x02: 0x61, 0x03: 0x61})


def relief_of(val):
    """The sprite's shading as relief: dark creases sunk, lit crowns raised."""
    ramp, shade = val >> 4, val & 15
    if ramp == 0 and shade <= 2:
        return -1.0
    if ramp in (6, 5) and shade <= 1:
        return -0.8
    return max(-0.6, min(1.0, (shade - 5.0) / 6.0))


def relief_field(f):
    return w.sampler(f.g, ORIGIN, value=relief_of, blur=1, keep=lambda val: val is not None)


# --- The parts -------------------------------------------------------------------------------------------------------

def body(f, p, wound=None):
    """The body's mass: f paints it; wound (a field 0-1) tears it open, sunk that much."""
    shape = closed(BOSS)
    polys = kit.region(shape, lambda val, c, r: not is_tendril(c, r), smooth=2, min_area=4.0)

    def z_of(x, y, e):
        t = 1.0 - math.sqrt(max(0.0, 1.0 - e * e))      # 0 on the outline, 1 twelve pixels in
        return height(col_of(x), row_of(y)) * (0.1 + 0.9 * t ** 1.1)
    obj = kit.heightfield("body", polys, z_of, p(0x64), spacing=1.0, edge=12.0)
    kit.emboss_z(obj, relief_field(shape), 2.4, min_nz=0.5)
    if wound is not None:
        kit.displace_z(obj, lambda x, y, z: -min(z - 1.5, 5.0 * wound(x, y)) if z > 2.0 else 0.0)
    kit.paint(obj, f, p, walls=-2, probe=-0.6, grid=True)
    return [obj]


def masked(f, pred):
    """A copy of frame f keeping only the pixels pred(column, row) accepts (filled where f has none)."""
    out = kit.Frame.__new__(kit.Frame)
    out.__dict__.update(f.__dict__)
    out._shades = {}
    out.g = [[(f.g[r][c] if f.g[r][c] is not None else 0x60) if pred(c, r) else None for c in range(f.width)]
             for r in range(f.height)]
    return out


SPINE = [  # rows, columns, the lump's height over its base, its base
    ((10, 26), (56, 72), 8.0, 13.0),
    ((27, 42), (43, 84), 13.0, 16.0),
    ((43, 55), (45, 81), 12.0, 16.0),
    ((56, 78), (47, 80), 12.0, 18.0),
]


def spine_span(r, c0, c1):
    """A row's purple span on the spine (columns c0..c1), made symmetric about the axis (the wider side kept)."""
    cols = [c for c in range(c0, c1 + 1) if BOSS.get(c, r) is not None and BOSS.get(c, r) >> 4 == 5]
    if not cols:
        return None
    a = min(min(cols), mc(max(cols)))
    return a, mc(a)


def spine(f, p, wound=None):
    shape = closed(BOSS)
    parts = []
    for i, ((r0, r1), (c0, c1), lift_h, base) in enumerate(SPINE):
        spans = {r: spine_span(r, c0, c1) for r in range(r0, r1 + 1)}
        m = masked(shape, lambda c, r, spans=spans: r in spans and spans[r] is not None and
                   spans[r][0] <= c <= spans[r][1])
        polys = kit.region(m, lambda val, c, r: True, smooth=2, min_area=2.0)
        obj = kit.inflated(f"spine{i}", polys, p(0x55), lift_h, aspect=0.75, spacing=1.0, base=base,
                           min_height=0.5)
        warts = kit.brightness(shape, blur=1, keep=lambda val: val >> 4 == 5)
        kit.emboss_z(obj, lambda x, y: (warts(x, y) - 0.3) * 3.0, 1.0, min_nz=0.4)
        kit.wobble(obj, 0.35, 1.3, seed=i + 1.0, min_z=base + 1.0)
        if wound is not None:   # torn open: a crater down into the body
            def crater(x, y, z, base=base, i=i):
                ragged = 0.75 + 0.35 * noise.noise(Vector((x / 2.2, y / 2.2, i + 0.5)))
                return -min(z - base - 0.3, 5.0 * wound(x, y) * ragged) if z > base + 0.3 else 0.0
            kit.displace_z(obj, crater)
        kit.paint(obj, f, p, walls=-2, probe=-0.4, grid=True)
        parts.append(obj)
    return parts


def eyes(f, p, surf, lit=None):
    """The six eyes: glowing red-orange lenses set in the sockets. lit(i, side) -> False puts an eye out (a dark
    hollow)."""
    parts = []
    reds = [pal("maw_eye_73", 0x73, metallic=0.0, roughness=0.15, glow=0.6),
            pal("maw_eye_75", 0x75, metallic=0.0, roughness=0.12, glow=0.9),
            pal("maw_eye_78", 0x78, metallic=0.0, roughness=0.1, glow=1.3),
            pal("maw_eye_7b", 0x7b, metallic=0.0, roughness=0.1, glow=1.8)]
    for i, (ec, er, rx, ry) in enumerate(EYES):
        for side, c in ((0, ec), (1, mc(ec))):
            if lit is not None and not lit(i, side):
                continue
            x, y = X(c), Y(er)
            z = surf(x, y) + 0.4
            eye = kit.lens(f"eye{i}_{side}", (x, y, z), (0.0, -0.15, 1.0), (rx, ry, 1.5), reds[1], sink=0.5,
                           segments=20)
            hx = -0.35 if side == 0 else 0.35

            def pick(cc, nrm, x=x, y=y, hx=hx):
                d = math.hypot(cc.x - x - hx, cc.y - y - 0.3)
                return reds[3] if d < 0.6 else reds[2] if d < 1.2 else reds[1] if nrm.z > 0.3 else reds[0]
            kit.paint_faces(eye, pick)
            parts.append(eye)
    return parts


def lips(f, p, surf):
    def keep(val, c, r):
        return val >> 4 == 4 and mouth_d(c, r) < 9.0 and not (95 <= r <= 102 and 59 <= c <= 67)
    shape = closed(BOSS)
    polys = kit.region(shape, keep, smooth=2, min_area=2.0)
    obj = kit.draped("lips", polys, p(0x47), 3.6, surf, sink=1.0, aspect=0.9, spacing=1.0)
    lit = kit.brightness(shape, blur=1, keep=lambda val: val >> 4 == 4)
    kit.emboss_z(obj, lambda x, y: (lit(x, y) - 0.35) * 2.5, 0.8, min_nz=0.4)
    kit.paint(obj, f, p, walls=-2, probe=-0.4, grid=True)
    # The uvula hanging from the top lip into the throat.
    uv = kit.region(shape, lambda val, c, r: val >> 4 == 4 and 95 <= r <= 102 and 59 <= c <= 67, smooth=2)
    uvula = kit.inflated("lips_uvula", uv, p(0x47), 3.0, aspect=0.9, spacing=0.4, base=0.0,
                         z_fn=lambda x, y, z: throat_floor(col_of(x), row_of(y)) + 8.0 + 4.0 *
                         smoothstep(102.0, 95.0, row_of(y)) + z)
    kit.paint(uvula, f, p, walls=-2, probe=-0.3, grid=True)
    return [obj, uvula]


# Teeth of the left half (base column, row; tip column, row; radius); mirrored, but the one on the axis.
TEETH = [((56.4, 96.8), (58.7, 108.6), 2.5), ((47.0, 102.4), (51.9, 107.1), 1.8), ((40.6, 110.2), (48.3, 112.6), 1.75),
         ((41.4, 115.4), (47.6, 116.2), 1.2), ((44.4, 120.4), (49.9, 118.0), 1.75), ((46.8, 127.7), (53.9, 125.3), 1.5),
         ((52.6, 136.2), (55.1, 130.8), 1.8), ((60.2, 137.6), (60.3, 130.9), 1.45)]
TOOTH_AXIS = ((63.0, 100.6), (63.0, 106.2), 1.3)


def tooth_materials():
    return [pal("maw_tooth_a5", 0xa5, metallic=0.0, roughness=0.4), pal("maw_tooth_a8", 0xa8, metallic=0.0,
                                                                         roughness=0.35),
            pal("maw_tooth_ab", 0xab, metallic=0.0, roughness=0.3), pal("maw_tooth_ad", 0xad, metallic=0.0,
                                                                        roughness=0.25)]


def teeth(f, p, surf, broken=None):
    mats = tooth_materials()
    parts = []
    specs = []
    for i, ((bc, br), (tc, tr), rad) in enumerate(TEETH):
        specs.append((f"tooth{i}", (bc, br), (tc, tr), rad))
        specs.append((f"tooth{i}_m", (mc(bc), br), (mc(tc), tr), rad))
    specs.append(("tooth_axis",) + TOOTH_AXIS)
    for name, (bc, br), (tc, tr), rad in specs:
        zb = surf(X(bc), Y(br)) + 0.6
        zt = max(surf(X(tc), Y(tr)) + 3.5, zb - 8.0)
        base = Vector((X(bc), Y(br), zb))
        tip = Vector((X(tc), Y(tr), zt))
        if broken is not None and name in broken:
            tip = base + (tip - base) * broken[name]
        obj = kit.cone(name, base, tip, rad, mats[1], segments=12, squash=0.85, bulge=0.2,
                       tip_radius=0.12 if broken is None or name not in broken else rad * 0.45)
        kit.paint_faces(obj, lambda cc, nrm: mats[3] if nrm.z > 0.75 and nrm.x < 0.1 else mats[2] if nrm.z > 0.35
                        else mats[1] if nrm.z > -0.2 else mats[0])
        parts.append(obj)
    return parts


def tendrils(f, p):
    """The glossy dark tendrils dripping from the face's sides, each ending in a bulb."""
    def keep(val, c, r):
        return is_tendril(c, r)
    polys = kit.region(closed(BOSS), keep, smooth=2, min_area=1.0)
    parts = []
    for i, poly in enumerate(polys):
        top = max(pt[1] for pt in poly)
        obj = sh.inflate(f"tendril{i}", [poly], p(0x64), sh.round_profile(0.95, 2.4, 0.5), bottom=1.0, base=0.0,
                         rim=0.0, spacing=0.5, sigma=1.0)
        kit.displace_z(obj, lambda x, y, z, top=top: 1.2 + 4.2 * (1.0 - smoothstep(0.0, 11.0, top - y)))
        k.smooth(obj, 60)
        kit.paint(obj, f, p, walls=-1, probe=-0.3, grid=True, merge=False)
        parts.append(obj)
    return parts


def horns(f, p, surf):
    """The purple horns either side of the jaw, pointing down and out."""
    def keep(val, c, r):
        u = abs(c - AXC)
        return 117 <= r <= 134 and 24 <= u <= 38 and val >> 4 == 5
    polys = kit.region(closed(BOSS), keep, smooth=2, min_area=2.0)
    parts = []
    for i, poly in enumerate(polys):
        obj = kit.draped(f"horn{i}", [poly], p(0x55), 3.0, surf, sink=0.9, aspect=0.9, spacing=0.5)
        kit.paint(obj, f, p, walls=-2, probe=-0.3, grid=True)
        parts.append(obj)
    return parts


# --- Damage -----------------------------------------------------------------------------------------------------------

def is_eye(c, r):
    cm = AXC - abs(c - AXC)
    return any(((cm - ec) / (rx + 2.0)) ** 2 + ((r - er) / (ry + 2.0)) ** 2 < 1.0 for ec, er, rx, ry in EYES)


def wound_map():
    """1 where the damaged sprite tore the beast open (it differs from the intact one there and shows raw flesh,
    bone or a dark hole), outside the maw and the eyes; 0 elsewhere on the beast."""
    g = [[None] * 120 for _ in range(168)]
    for r in range(168):
        for c in range(120):
            i, d = BOSS.get(c, r), DMG.get(c, r)
            if i is None:
                continue
            if mouth_d(c, r) > -1.5 or is_eye(c, r) or is_tendril(c, r):
                g[r][c] = 0
                continue
            torn = d != i and (d is None or d >> 4 in (7, 10) or (d >> 4 == 0 and (d & 15) <= 2) or
                               (d >> 4 == 6 and (d & 15) <= 1))
            g[r][c] = 1 if torn else 0
    return g


def wound_field():
    return w.sampler(wound_map(), ORIGIN, value=lambda val: float(val), blur=2, keep=lambda val: val is not None)


def components(keep):
    """Connected groups of pixels (4-neighbours) keep(column, row) accepts: lists of (column, row)."""
    seen, out = set(), []
    for r in range(168):
        for c in range(120):
            if (c, r) in seen or not keep(c, r):
                continue
            stack, group = [(c, r)], []
            seen.add((c, r))
            while stack:
                a, b = stack.pop()
                group.append((a, b))
                for nc, nr in ((a + 1, b), (a - 1, b), (a, b + 1), (a, b - 1)):
                    if (nc, nr) not in seen and 0 <= nc < 120 and 0 <= nr < 168 and keep(nc, nr):
                        seen.add((nc, nr))
                        stack.append((nc, nr))
            out.append(group)
    return out


def gore(f, p, surf, wmap):
    """Raw flesh in the wounds: soft red lumps strewn over the pixels where the damaged sprite shows red."""
    def keep(c, r):
        d = DMG.get(c, r)
        return wmap[r][c] == 1 and d is not None and d >> 4 == 7
    rnd = random.Random(5)
    spots = []
    for group in components(keep):
        if len(group) < 3:
            continue
        cells = group[:]
        rnd.shuffle(cells)
        # Brightest first: the lumps' crowns where the sprite's flesh is lit.
        cells.sort(key=lambda cr: -(DMG.get(*cr) & 15))
        for c, r in cells:
            if all(math.hypot(c - a, r - b) > 3.0 for a, b, _ in spots):
                near = sum(1 for a, b in group if abs(a - c) <= 2 and abs(b - r) <= 2)
                spots.append((c, r, near))
    parts = []
    for i, (c, r, near) in enumerate(spots):
        x, y = X(c) + rnd.uniform(-0.3, 0.3), Y(r) + rnd.uniform(-0.3, 0.3)
        size = 1.0 + 0.14 * near
        rad = (size * rnd.uniform(0.9, 1.25), size * rnd.uniform(0.9, 1.25), 0.8 + 0.09 * near)
        lump = w.lumpy(f"gore{i}", (x, y, surf(x, y) + 0.1), rad, p(0x74), seed=i + 3, amount=0.25, segments=9,
                       rings=5)
        kit.paint(lump, f, p, walls=-1, probe=0.0, merge=False, default=p(0x73))
        parts.append(lump)
    return parts


def bones(f, p, surf, wmap):
    """Bare bones in the wounds (the right shoulder's ribs): a rod along each streak of bone the sprite draws."""
    def keep(c, r):
        d = DMG.get(c, r)
        return wmap[r][c] == 1 and d is not None and d >> 4 == 10
    mats = tooth_materials()
    parts = []
    for i, group in enumerate(components(keep)):
        if len(group) < 4:
            continue
        cx = sum(c for c, _ in group) / len(group)
        cy = sum(r for _, r in group) / len(group)
        sxx = sum((c - cx) ** 2 for c, _ in group) / len(group)
        syy = sum((r - cy) ** 2 for _, r in group) / len(group)
        sxy = sum((c - cx) * (r - cy) for c, r in group) / len(group)
        ang = 0.5 * math.atan2(2 * sxy, sxx - syy)
        dx, dy = math.cos(ang), math.sin(ang)
        ts = [(c - cx) * dx + (r - cy) * dy for c, r in group]
        t0, t1 = min(ts) + 0.3, max(ts) - 0.3
        width = len(group) / max(1.0, t1 - t0 + 1.0)
        rad = max(0.6, min(1.3, width * 0.5))
        pts = []
        for k_ in range(5):
            t = t0 + (t1 - t0) * k_ / 4
            c, r = cx + dx * t, cy + dy * t
            x, y = X(c), Y(r)
            pts.append((x, y, surf(x, y) + rad * 0.6 + 0.6 * math.sin(math.pi * k_ / 4)))
        rib = w.tube(f"bone{i}", pts, rad, mats[2], 8)
        kit.paint_faces(rib, lambda cc, nrm: mats[3] if nrm.z > 0.75 else mats[2] if nrm.z > 0.3 else mats[1]
                        if nrm.z > -0.2 else mats[0])
        parts.append(rib)
    return parts


def surface_of(objects):
    """A function (x, y) -> the height of the body's surface there (a ray cast down)."""
    return lambda x, y: kit.ae.surface_z(objects, x, y, 2.0)


# --- The whole boss ------------------------------------------------------------------------------------------------

def boss():
    p = painter("maw")
    f = closed(BOSS)
    hull = body(f, p)
    surf = surface_of(hull)
    spine(f, p)
    eyes(f, p, surf)
    lips(f, p, surf)
    teeth(f, p, surf)
    tendrils(f, p)
    horns(f, p, surf)
    for obj in kit.meshes():
        k.smooth(obj, 45)


def boss_damaged():
    p = painter("maw_dmg", raw=True)
    f = closed(DMG)
    wmap = wound_map()
    field = w.sampler(wmap, ORIGIN, value=lambda val: float(val), blur=2, keep=lambda val: val is not None)
    hull = body(f, p, wound=field)
    surf = surface_of(hull)
    spine(f, p, wound=field)
    # Only the lowest right eye still burns; the others are dark hollows.
    eyes(f, p, surf, lit=lambda i, side: i == 2 and side == 1)
    lips(f, p, surf)
    teeth(f, p, surf, broken={"tooth0_m": 0.3, "tooth7": 0.25, "tooth7_m": 0.45, "tooth6": 0.7})
    tendrils(f, p)
    horns(f, p, surf)
    gore(f, p, surf, wmap)
    bones(f, p, surf, wmap)
    for obj in kit.meshes():
        k.smooth(obj, 45)


# The pieces: sprite -> its top left pixel in the whole; the damaged sprites (dgr) of those that have their own.
CELLS = {3: (24, 0), 5: (48, 0), 7: (72, 0), 41: (24, 28), 43: (48, 28), 45: (72, 28),
         77: (0, 56), 79: (24, 56), 81: (48, 56), 83: (72, 56), 85: (96, 56),
         115: (0, 84), 117: (24, 84), 119: (48, 84), 121: (72, 84), 123: (96, 84),
         153: (0, 112), 155: (24, 112), 157: (48, 112), 159: (72, 112), 161: (96, 112),
         193: (24, 140), 195: (48, 140), 197: (72, 140)}
DAMAGED = {41: 51, 43: 53, 45: 55, 77: 87, 79: 89, 81: 91, 83: 93, 85: 18, 117: 127, 119: 129, 121: 131,
           155: 165, 157: 167, 159: 169}

kit.PROTECT += ["body", "spine", "lips", "horn", "tendril"]
kit.pieced("gyges_maw", boss, (120, 168),
           [kit.piece(f"gyges_maw_{s}", BOSS, c0, r0, 24, 28) for s, (c0, r0) in CELLS.items()])
kit.pieced("gyges_maw_damaged", boss_damaged, (120, 168),
           [kit.piece(f"gyges_maw_{DAMAGED[s]}", DMG, c0, r0, 24, 28) for s, (c0, r0) in CELLS.items() if s in DAMAGED])


if __name__ == "__main__":
    kit.run()
