"""Batch AH of wave 3 (sheet M): MINERS' banded rock column and its broken look, modelled as the sprites look
(models.cfg: yaw=0). The kit is wave3_ah_kit.py, the pixels wave3_ah_art.py.

MINERS puts the column together from six ground enemies (1191-1196): 163, 165 at (x, y - 57), (x + 24, y - 57),
201, 203 at (x, y - 29), (x + 24, y - 29) and 239, 241 at (x, y - 1), (x + 24, y - 1): 48 x 84 pixels, its foot
on the red ground at the bottom. Each piece is an enemy of its own; the upper four leave their broken looks in
their place when destroyed (dgr 167, 169, 205, 207; dlevel -1), the lower two just go.

The sprites draw a thick octagonal pillar of rock standing on the ground, seen from the side and above: its pale
top, two drums below it parted by dark grooves, its foot on the red ground. The model leans the pillar up the
screen from its foot (as the tall towers of wave3_x_tower.py and the spire of wave3_z_rock.py do), so that from
above it covers the sprites and its pale head rises highest (about 38 pixels over the ground).

- rock_column_tl, _tr, _ml, _mr, _bl, _br (M 163, 165, 201, 203, 239, 241): the pillar, cut into its six pieces;
  the lower two with the red ground round the foot.
- rock_column_wreck_tl, _tr, _ml, _mr (M 167, 169, 205, 207): the head and the upper drum broken open, dark
  hollows gouged into them where the sprites show the rock's grey insides.

usage: Blender -b --factory-startup -P wave3_ah_rock.py -- [--only name,name] [--preview <prefix>] [--check 1]
       [--stats 1] [--whole <prefix>]
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_ah_kit as kit  # noqa: E402
from wave3_ah_kit import k, sh, w, pal  # noqa: E402

ROCK = kit.frame("ROCK", 48, (24, 42))
BROKEN = kit.frame("ROCK_WRECK", 48, (24, 42))

THETA = math.radians(18.0)      # the pillar's lean up the screen
SIN, COS = math.sin(THETA), math.cos(THETA)
A, B, POWER = 22.3, 12.5, 3.2   # the cross-section: half-width, half-thickness, superellipse power
BOTTOM_Y = -37.6                # the foot's front edge (row 79)
TOP_Y = 40.0                    # the head's far edge (row 2)
FOOT_Y = BOTTOM_Y + B * SIN     # the axis at the foot
FOOT_Z = 2.4
LENGTH = (TOP_Y - B * SIN - FOOT_Y) / COS
UP = Vector((0.0, -SIN, COS))   # the cross-sections' "up", square to the axis
AXIS = Vector((0.0, COS, SIN))


def t_of_row(row):
    """The distance along the axis whose section's top lies over a row of the art."""
    y = 42.0 - row - 0.5
    return (y + B * SIN - FOOT_Y) / COS


def axis(t):
    return Vector((0.0, FOOT_Y, FOOT_Z)) + AXIS * t


def _outline(segments):
    """The cross-section's superellipse (A x B, unit scale) as (s, h) points spaced evenly along it."""
    fine = []
    for i in range(720):
        a = 2 * math.pi * i / 720
        ca, sa = math.cos(a), math.sin(a)
        fine.append((math.copysign(abs(ca) ** (2 / POWER), ca) * A, math.copysign(abs(sa) ** (2 / POWER), sa) * B))
    lengths = [0.0]
    for i in range(720):
        (x0, y0), (x1, y1) = fine[i], fine[(i + 1) % 720]
        lengths.append(lengths[-1] + math.hypot(x1 - x0, y1 - y0))
    total = lengths[-1]
    out, j = [], 0
    for i in range(segments):
        target = total * i / segments
        while lengths[j + 1] < target:
            j += 1
        f = (target - lengths[j]) / max(1e-9, lengths[j + 1] - lengths[j])
        (x0, y0), (x1, y1) = fine[j], fine[(j + 1) % 720]
        out.append((x0 + (x1 - x0) * f, y0 + (y1 - y0) * f))
    return out


_OUTLINES = {}


def section(t, scale=1.0, segments=72, lift=0.0, xscale=1.0):
    """A cross-section of the pillar at t: the superellipse A x B scaled by `scale` (and its width by `xscale`),
    its points spaced evenly."""
    if segments not in _OUTLINES:
        _OUTLINES[segments] = _outline(segments)
    c = axis(t)
    return [c + Vector((s_ * scale * xscale, 0.0, 0.0)) + UP * (h * scale + lift) for s_, h in _OUTLINES[segments]]


def head_width(t):
    """The head narrows towards its end as the sprites draw it: its half-width 22.3 up to row 20, 17.5 at row 7."""
    t20, t7 = t_of_row(20.0), t_of_row(7.0)
    if t <= t20:
        return 1.0
    f = min(1.0, (t - t20) / (t7 - t20))
    return (22.3 - 4.8 * f) / 22.3


# Where the drums and grooves lie along the axis (rows of the art: the head 2-33, a groove 33-37, the upper drum
# 37-53, a groove 53-56, the lower drum 56-72 and its foot rounding into the ground over 72-79).
T_HEAD = t_of_row(34.5)
T_GROOVE1 = t_of_row(36.5)
T_DRUM2 = t_of_row(54.0)
T_GROOVE2 = t_of_row(55.5)


def drum(name, t0, t1, mat, round0=1.6, round1=1.6, step=1.0, end_cap=None, xprofile=None):
    """A drum of the pillar from t0 to t1, its ends rounded over round0 / round1 (end_cap: the head's long
    rounded end instead, over that length)."""
    ts = []
    count = max(2, int(math.ceil((t1 - t0) / step)))
    for i in range(count + 1):
        ts.append(t0 + (t1 - t0) * i / count)
    # Finer at the rounded ends.
    extra = [t0 + round0 * f for f in (0.15, 0.4, 0.7)] + [t1 - (end_cap or round1) * f for f in (0.05, 0.15, 0.3, 0.5, 0.7)]
    ts = sorted(set(round(t, 4) for t in ts + extra if t0 <= t <= t1))
    rings = []
    for t in ts:
        d0, d1 = t - t0, t1 - t
        scale = 1.0
        if d0 < round0:
            u = 1.0 - d0 / round0
            scale = min(scale, 0.9 + 0.1 * math.sqrt(max(0.0, 1.0 - u * u)))
        r1 = end_cap or round1
        if d1 < r1:
            u = 1.0 - d1 / r1
            floor_ = 0.25 if end_cap else 0.9
            scale = min(scale, floor_ + (1.0 - floor_) * math.sqrt(max(0.0, 1.0 - u * u)))
        rings.append(section(t, scale, xscale=xprofile(t) if xprofile else 1.0))
    obj = k.loft(name, rings, mat, start_point=axis(ts[0]), end_point=axis(ts[-1]))
    return k.smooth(obj, 55)


def rock_noise(obj, amount, seed, scale=2.2, keep_ends=None):
    """Roughens a drum: each vertex moves along its direction from the axis by smooth noise."""
    rng = __import__("random").Random(seed)
    waves = [(Vector([rng.uniform(-1, 1) for _ in range(3)]).normalized() / scale, rng.uniform(0, 6.3))
             for _ in range(9)]
    sh.apply_modifiers(obj)
    for v in obj.data.vertices:
        co = v.co
        t = (co - Vector((0.0, FOOT_Y, FOOT_Z))).dot(AXIS)
        out = co - axis(t)
        if out.length < 1e-6:
            continue
        d = sum(math.sin(wv.dot(co) + ph) for wv, ph in waves) / math.sqrt(len(waves))
        v.co = co + out.normalized() * d * amount
    return obj


def gouge(obj, depth_at, max_depth):
    """Pushes the vertices in towards the axis by depth_at(x, y) * max_depth (hollows)."""
    sh.apply_modifiers(obj)
    for v in obj.data.vertices:
        d = depth_at(v.co.x, v.co.y)
        if d <= 0:
            continue
        t = (v.co - Vector((0.0, FOOT_Y, FOOT_Z))).dot(AXIS)
        inward = axis(t) - v.co
        if inward.length < 1e-6:
            continue
        v.co += inward.normalized() * min(inward.length * 0.7, d * max_depth)
    return obj


def column_whole(broken=False):
    f = BROKEN if broken else ROCK
    tag = "rcw" if broken else "rc"
    finish = {10: (0.05, 0.75), 11: (0.05, 0.75), 0: (0.05, 0.85), 1: (0.05, 0.8), 4: (0.05, 0.7), 5: (0.05, 0.7),
              7: (0.1, 0.6), 15: (0.05, 0.8), 6: (0.1, 0.8)}
    shades = {10: (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14), 11: (8, 10, 12, 13, 15), 0: (1, 2, 3, 4),
              1: (2, 4, 6, 8), 4: (6, 8, 10, 12, 15), 5: (8, 12, 15), 7: (10, 13, 15), 15: (1, 2, 3, 4), 6: (1, 2, 3, 4, 5, 6)}

    def on_rock(x, y):
        v = ROCK.at(x, y)
        return not (v is not None and v >> 4 == 4 and y < -14.0)  # the red ground round the foot

    # The rock's tans, its dark cracks and (broken) grey insides; its coloured specks (reds, pinks, oranges) left
    # to the tan around them, which keeps the stone calm in 3D.
    paint = kit.RampPainter(tag, f, ramps={10, 11, 1, 0, 6}, fallback=10, shades=shades, blur=1, wall=0.8, under=3.0,
                            finish=finish, where=on_rock)
    rock = pal(f"{tag}_rock", 0xa7, metallic=0.05, roughness=0.75)
    dark = pal(f"{tag}_groove", 0x01, metallic=0.05, roughness=0.9)

    parts = []
    parts.append(drum("drum1", -4.0, T_GROOVE2, rock, round0=0.1, round1=1.8))
    parts.append(drum("drum2", T_DRUM2, T_GROOVE1, rock, round0=1.8, round1=1.8))
    parts.append(drum("head", T_HEAD, LENGTH, rock, round0=1.8, end_cap=6.0, xprofile=head_width))
    for i, obj in enumerate(parts):
        rock_noise(obj, 0.55 if obj.name == "head" else 0.35, seed=5 + i)
    # The grooves: the core between the drums, dark.
    for name, t0, t1 in (("core1", T_GROOVE2 - 1.0, T_DRUM2 + 1.0), ("core2", T_GROOVE1 - 1.0, T_HEAD + 1.0)):
        rings = [section(t, 0.86, 40) for t in (t0, (t0 + t1) / 2, t1)]
        k.smooth(k.loft(name, rings, dark, start_point=axis(t0), end_point=axis(t1)), 50)

    if broken:
        # Hollows where the broken sprites show the dark grey insides (ramp 6), deepest in their middles.
        hollow = kit.field(f, lambda v: 1.0 if v >> 4 in (6,) else (0.5 if v >> 4 == 0 and (v & 15) <= 2 else 0.0),
                           lambda v: True, blur=2)
        depth = kit.field_sampler(f, hollow)
        for obj in parts:
            if obj.name in ("head", "drum2"):
                gouge(obj, lambda x, y: max(0.0, depth(x, y) - 0.2) * 1.4 if y > -14.0 else 0.0, 9.0)
            if obj.name == "head":
                # Its upper right broken away along the diagonal from (col 23, row 2) to (col 46, row 26).
                kit.cut_plane(obj, (11.0, 27.5, 0.0), (24.0, 23.0, 0.0))
            if obj.name in ("head", "drum2"):
                rock_noise(obj, 0.45, seed=11)
    for obj in parts:
        kit.clip_below(obj, 0.0)
        paint(obj)

    # The red ground round the foot (the lower pieces, rows 56-83): a thin bed in its shades.
    ground = [[None] * 48 for _ in range(84)]
    for r in range(56, 84):
        for c in range(48):
            v = ROCK.g[r][c] if r < len(ROCK.g) else None
            ground[r][c] = v if v is not None and v >> 4 == 4 else 0x46
    kit.xk.floor_bed("ground", ground, (24, 42), top=0.35, prefix=f"{tag}_ground", shades_=(3, 4, 5, 6, 7, 8), ramp=4)


def broken_whole():
    column_whole(broken=True)


kit.pieced("rock_column", column_whole, (48, 84),
           [kit.quarter(f"rock_column_{n_}", ROCK, 24 * (i % 2), 28 * (i // 2)) for i, n_ in
            enumerate(("tl", "tr", "ml", "mr", "bl", "br"))])
kit.pieced("rock_column_wreck", broken_whole, (48, 84),
           [kit.quarter(f"rock_column_wreck_{n_}", BROKEN, 24 * (i % 2), 28 * (i // 2)) for i, n_ in
            enumerate(("tl", "tr", "ml", "mr"))])


if __name__ == "__main__":
    kit.run()
