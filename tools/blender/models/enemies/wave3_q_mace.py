"""Batch Q of wave 3 (sheet A: GAUNTLET and MACES), the mace and its chain and the skull chest; modelled as their
sprites look (models.cfg: yaw=0). (The mace's anchor, A 83, 85 above 121, 123: polish_mace_anchor.py.) The levels place them (custom enemies, events
49-52) as the sheet arranges them: the mace's six sprites in three columns and two rows, the anchor's four
in two by two (polish_mace_anchor.py), the chest's eight in four by two; the three chain rings run between the mace and its
anchor, larger towards the mace (and come out of the chest at first).

- mace_tl, mace_tc, mace_tr, mace_bl, mace_bc, mace_br (A 77, 79, 81 above 115, 117, 119): the mace head,
  a steel ball with four long spikes in bronze collars along the screen's axes and four shorter ones
  rising between them, a bronze eyelet with a steel bolt on its top where the chain is fixed. Built whole
  and cut into its six pieces (origin).
- chain_ring_s, chain_ring_m, chain_ring_l (A 87, 125, 127): the chain's steel rings, lying flat at the
  height of the mace's eyelet and the anchor's ball (origin: they keep that height).
- skull_chest_t1 ... skull_chest_t4, skull_chest_b1 ... skull_chest_b4 (A 153, 155, 157, 159 above 191,
  193, 195, 197): the wooden chest with two steel straps, a skull carved in a sunken panel between them
  and a steel handle folded back over its rear edge. Built whole and cut into its eight pieces (origin).

usage: Blender -b --factory-startup -P wave3_q_mace.py -- [--only name,name] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1] [--whole mace|chest --preview <prefix>]
"""
import math
import os
import sys

from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_q_kit as q  # noqa: E402
from wave3_q_kit import art, pal  # noqa: E402

CHAIN_Z = 14.0  # the chain's height: between the anchor's ball and the mace's eyelet


def steel(prefix, lo=2, hi=15, metallic=0.7, roughness=0.3):
    return {s: pal(f"{prefix}_steel{s}", s, metallic=metallic, roughness=roughness) for s in range(lo, hi + 1)}


def wood(prefix, lo=1, hi=14):
    return {s: pal(f"{prefix}_wood{s}", 0x10 | s, metallic=0.0, roughness=0.78) for s in range(lo, hi + 1)}


def shade_paint(obj, shade, mats, mid=8.0, squeeze=0.6, side=-1.5, under=None, override=None):
    """Paints faces in the sprite's shades (shade(x, y)), pulled towards `mid` by squeeze; steep sides
    `side` darker; faces facing down `under` (a shade); override(c, n) -> material or None first."""
    lo, hi = min(mats), max(mats)

    def pick(c, n):
        if override is not None:
            m = override(c, n)
            if m is not None:
                return m
        if n.z < -0.3 and under is not None:
            return mats[under]
        s = mid + (shade(c.x, c.y) - mid) * squeeze
        if n.z < 0.35:
            s += side
        return mats[int(min(hi, max(lo, round(s))))]
    q.paint_faces(obj, pick)


def place_pieces(prefix, whole_fn, pieces):
    """Registers the pieces of a whole object: (name, sprite, centre, box)."""
    for name, sprite, centre, box in pieces:
        def build(centre=centre, box=box):
            objects = whole_fn()
            q.cut(objects, box, centre)
            q.budget(4800)
        q.model(name, [(sprite, True)])(build)


# --- A 77 ... 119: the mace head ---------------------------------------------------------------------

MACE_ORIGIN = (36, 28)  # the art: 72 x 56
BALL = Vector((0.5, -0.5, 12.0))
BALL_R, BALL_RZ = 16.4, 12.6


@q.whole("mace", (72, 56))
def mace_whole():
    g = q.grid(art.MACE, 72)
    st = steel("mace", metallic=0.5, roughness=0.3)
    bronze = pal("mace_bronze", 0xa8, metallic=0.65, roughness=0.32)
    bronze_light = pal("mace_bronze_light", 0xab, metallic=0.65, roughness=0.28)
    spike = pal("mace_spike", 0x0a, metallic=0.75, roughness=0.22)
    parts = []
    ball = q.sphere("ball", tuple(BALL), (BALL_R, BALL_R, BALL_RZ), st[9], 56, 28)
    shade = q.shades(g, MACE_ORIGIN, keep=lambda v: v >> 4 == 0 and (v & 15) > 1, blur=3)
    shade_paint(ball, shade, st, mid=10.0, squeeze=0.35, side=-1.0, under=5)
    parts.append(ball)

    # The long spikes along the screen's axes, in bronze collars.
    for i, (dx, dy, length) in enumerate(((0, 1, 27.2), (0, -1, 27.2), (-1, 0, 27.6), (1, 0, 27.0))):
        d = Vector((dx, dy, 0.0))
        parts.append(q.cone(f"spike{i}", BALL + d * 13.0, d, length - 13.0, 3.0, spike))
        parts.append(q.lathe_axis(f"collar{i}", [(0.0, 2.6), (0.2, 3.7), (1.5, 3.8), (1.75, 2.9)], bronze,
                                  tuple(BALL + d * 15.6), (dx, dy, 0.0), 24))
        parts.append(q.lathe_axis(f"collar_lip{i}", [(0.0, 3.0), (0.1, 3.95), (0.4, 3.95), (0.5, 3.0)], bronze_light,
                                  tuple(BALL + d * 17.0), (dx, dy, 0.0), 24))
    # The short spikes between them, rising towards the camera.
    for i in range(4):
        a = math.radians(45 + 90 * i)
        e = math.radians(16)
        d = Vector((math.cos(a) * math.cos(e), math.sin(a) * math.cos(e), math.sin(e)))
        parts.append(q.cone(f"spike_d{i}", BALL + d * 12.0, d, 11.5, 2.0, spike, segments=12))
    # The eyelet on the top: a bronze collar round a steel bolt.
    top = BALL.z + BALL_RZ
    parts.append(q.torus("eyelet", (BALL.x, BALL.y, top - 0.55), 3.7, 1.25, bronze_light, 36, 12, squash=0.85))
    parts.append(q.sphere("bolt", (BALL.x, BALL.y, top - 0.35), (2.4, 2.4, 1.7), st[11], 20, 10))
    parts.append(q.torus("bolt_eye", (BALL.x, BALL.y, top + 1.0), 1.1, 0.45, st[13], 20, 8))
    return parts


MACE_PIECES = []
for _row, (_cy, _y0, _y1) in enumerate(((14.0, 0.0, 32.0), (-14.0, -32.0, 0.0))):
    for _col, (_cx, _x0, _x1) in enumerate(((-24.0, -40.0, -12.0), (0.0, -12.0, 12.0), (24.0, 12.0, 40.0))):
        MACE_PIECES.append((f"mace_{'tb'[_row]}{'lcr'[_col]}", (77, 79, 81, 115, 117, 119)[_row * 3 + _col],
                            (_cx, _cy), (_x0, _x1, _y0, _y1)))
place_pieces("mace", mace_whole, MACE_PIECES)


# --- A 87, 125, 127: the chain rings -----------------------------------------------------------------

def chain_ring(prefix, centre, major, minor):
    light = pal(f"{prefix}_light", 0x0a, metallic=0.75, roughness=0.25)
    dark = pal(f"{prefix}_dark", 0x06, metallic=0.7, roughness=0.32)
    ring = q.torus(prefix, (centre[0], centre[1], CHAIN_Z), major, minor, light, 48, 14, squash=0.9)
    q.paint_faces(ring, lambda c, n: dark if n.z < 0.15 else None)


q.model("chain_ring_s", [(87, True)])(lambda: chain_ring("ring_s", (0.5, -0.5), 6.5, 1.85))
q.model("chain_ring_m", [(125, True)])(lambda: chain_ring("ring_m", (0.5, -0.5), 8.55, 2.0))
q.model("chain_ring_l", [(127, True)])(lambda: chain_ring("ring_l", (0.0, 0.0), 9.55, 2.4))


# --- A 153 ... 197: the skull chest ------------------------------------------------------------------

CHEST_ORIGIN = (48, 28)  # the art: 96 x 56
CHEST_H = 15.0
CHEST_PANEL = (-9.6, 10.6, -24.6, 2.2)   # the sunken panel with the skull: x0, x1, y0, y1
CHEST_STRAPS = ((-24.0, -13.0), (14.0, 25.0))
CHEST_HANDLE = (-0.5, 9.0, 11.5)          # the handle's middle x, its half width, its pivots' y


@q.whole("chest", (96, 56))
def chest_whole():
    g = q.grid(art.CHEST, 96)
    wd = wood("chest")
    strap = pal("chest_strap", 0x0b, metallic=0.65, roughness=0.3)
    strap_dark = pal("chest_strap_dark", 0x08, metallic=0.6, roughness=0.35)
    strap_light = pal("chest_strap_light", 0x0d, metallic=0.65, roughness=0.25)
    handle = pal("chest_handle", 0x0a, metallic=0.7, roughness=0.25)
    grain = q.shades(g, CHEST_ORIGIN, keep=lambda v: v >> 4 == 1, blur=0)
    px0, px1, py0, py1 = CHEST_PANEL

    def in_panel(x, y, soft=0.5):
        return (q.smoothstep(px0 - soft, px0 + soft, x) * q.smoothstep(px1 + soft, px1 - soft, x) *
                q.smoothstep(py0 - soft, py0 + soft, y) * q.smoothstep(py1 + soft, py1 - soft, y))

    def z_of(x, y, e):
        p = in_panel(x, y)
        z = CHEST_H - 1.2 * p
        # The skull is carved: the sprite's dark lines are grooves in the panel, the wood elsewhere grained.
        z += (0.22 * p + 0.06 * (1 - p)) * (grain(x, y) - 7.0)
        return z - 1.4 * (1.0 - e)

    body_polys = q.pixel_polys(g, lambda v, c, r: r >= 18 and 12 <= c <= 85, CHEST_ORIGIN, smooth=1, epsilon=0.3)
    body = q.heightfield("body", body_polys, z_of, wd[9], spacing=0.5, edge=1.4)
    q.w.simplify_bottom(body)
    shade = q.shades(g, CHEST_ORIGIN, keep=lambda v: v >> 4 == 1, blur=0)
    shade_paint(body, shade, wd, mid=8.5, squeeze=0.9, side=-3.0, under=2)
    q.decimate(body, 14000)
    parts = [body]

    # The straps: steel bands over the lid and down the front and back, a ridge and rivets near each end.
    for i, (x0, x1) in enumerate(CHEST_STRAPS):
        cx, hw = (x0 + x1) / 2, (x1 - x0) / 2
        band = q.block(f"strap{i}", (cx, -8.5), hw, 19.5, CHEST_H + 0.9, strap, taper=0.0, rounding=0.9, power=6.0,
                       dome=0.5)
        q.paint_faces(band, lambda c, n, cx=cx: strap_dark if (n.z > 0.5 and c.x > cx + 2.5) else None)
        parts.append(band)
        for j, y in enumerate((5.0, -18.5)):
            parts.append(q.rounded_box(f"strap{i}_ridge{j}", (cx, y, CHEST_H + 1.25), (2 * hw - 0.6, 1.2, 0.9),
                                       strap_light, bevel=0.35))
            for k_, dx in enumerate((-hw + 2.0, hw - 2.0)):
                parts.append(q.sphere(f"strap{i}_rivet{j}{k_}", (cx + dx, y + (2.0 if j == 0 else -2.0), CHEST_H + 1.2),
                                      (0.7, 0.7, 0.55), strap_light, 10, 6))

    # The handle: two brackets on the lid's rear edge, a U-shaped bar folded back over it.
    hx, half, pivot_y = CHEST_HANDLE
    pivot_z = CHEST_H + 1.6
    for side in (-1, 1):
        parts.append(q.block(f"bracket{side}", (hx + side * half, pivot_y + 0.8), 2.4, 2.0, 2.6, strap, rounding=0.7,
                             power=4.0, z0=CHEST_H - 0.6, dome=0.3))
    tilt = math.radians(36)
    pts = []
    leg = 7.0
    for i in range(8):  # up the left leg
        pts.append((-half, leg * i / 7))
    for i in range(1, 24):  # round the top
        a = math.pi * i / 24
        pts.append((-half * math.cos(a), leg + half * math.sin(a)))
    for i in range(8):  # down the right leg
        pts.append((half, leg * (7 - i) / 7))
    path = [(hx + u, pivot_y + v * math.cos(tilt), pivot_z + v * math.sin(tilt)) for u, v in pts]
    parts.append(q.tube("handle", path, 1.3, handle, 14))
    for side in (-1, 1):
        parts.append(q.lathe_axis(f"pin{side}", [(-1.6, 0.7), (-1.4, 0.95), (1.4, 0.95), (1.6, 0.7)], strap_light,
                                  (hx + side * half, pivot_y, pivot_z), (1, 0, 0), 14))
    return parts


CHEST_PIECES = []
for _row, (_cy, _y0, _y1) in enumerate(((14.0, 0.0, 32.0), (-14.0, -32.0, 0.0))):
    for _col in range(4):
        _cx = -36.0 + 24.0 * _col
        _x0 = -52.0 if _col == 0 else _cx - 12.0
        _x1 = 52.0 if _col == 3 else _cx + 12.0
        CHEST_PIECES.append((f"skull_chest_{'tb'[_row]}{_col + 1}", ((153, 155, 157, 159), (191, 193, 195, 197))[_row][_col],
                             (_cx, _cy), (_x0, _x1, _y0, _y1)))
place_pieces("chest", chest_whole, CHEST_PIECES)


if __name__ == "__main__":
    q.run()
