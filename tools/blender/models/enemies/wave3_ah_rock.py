"""Batch AH of wave 3 (sheet M): MINERS' banded rock column and its broken look (models.cfg: yaw=0). The kit is
wave3_ah_kit.py, the pixels wave3_ah_art.py.

MINERS puts the column together from six ground enemies (1191-1196): 163, 165 at (x, y - 57), (x + 24, y - 57),
201, 203 at (x, y - 29), (x + 24, y - 29) and 239, 241 at (x, y - 1), (x + 24, y - 1): 48 x 84 pixels, its foot
on the red ground at the bottom. Each piece is an enemy of its own; the upper four leave their broken looks in
their place when destroyed (dgr 167, 169, 205, 207; dlevel -1), the lower two just go.

The sprites draw a thick octagonal pillar of rock standing on the ground in the game's oblique view (its side seen
from the front and above): its pale top (rows 2-33), two drums below it parted by dark grooves, its foot on the
red ground (row 79). The model stands upright (batch AV): its footprint (44 x 30 pixels) on the ground where the
sprites draw the foot (rows 49-79), its top 40 pixels above the ground. It is built in the sprites' oblique view
(each point z above the ground moved K z up the screen, so that the model lies over the sprites as they draw it),
painted there by the sprites' pixels and cut into the pieces along the sprites' edges, and each piece is then
stood upright (moved K z back down the screen): every piece is the part of the pillar its sprite draws (the upper
pieces the top and the back of the upper drum, the middle ones the upper drum, the lower ones the lower drum and
the foot), so the pieces' parts lie below their sprites' centres (up to 60 pixels for the top ones). The red ground
round the foot is the map's (the game draws it under the column): not modelled.

- rock_column_tl, _tr, _ml, _mr, _bl, _br (M 163, 165, 201, 203, 239, 241): the pillar, cut into its six pieces.
- rock_column_wreck_tl, _tr, _ml, _mr (M 167, 169, 205, 207): the top and the upper drum broken open, dark
  hollows gouged into them where the sprites show the rock's grey insides, the top's back right corner broken off.

usage: Blender -b --factory-startup -P wave3_ah_rock.py -- [--only name,name] [--preview <prefix>] [--check 1]
       [--stats 1] [--whole <prefix> (renders the whole column in the sprites' oblique view)]
       (names: the pieces, e.g. --only rock_column_tl,rock_column_bl; the whole: rock_column, rock_column_wreck)
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_ah_kit as kit  # noqa: E402
from wave3_ah_kit import k, sh, w, pal  # noqa: E402

ROCK = kit.frame("ROCK", 48, (24, 42))
BROKEN = kit.frame("ROCK_WRECK", 48, (24, 42))

A, D, POWER = 22.3, 15.0, 3.2   # the cross-section: half-width, half-depth, superellipse power (the drawn top)
BOTTOM_Y = -37.6                # the foot's front edge (row 79)
CY = BOTTOM_Y + D               # the pillar's axis: its footprint over rows 49-79, where the sprites draw the foot
HEIGHT = 40.0                   # the top's edge above the ground (its crown CROWN more)
CROWN = 1.4
TOP_FRONT_Y = 9.0               # where the sprites draw the top's front edge (row 33)
K = (TOP_FRONT_Y - BOTTOM_Y) / HEIGHT   # the oblique view: a point z above the ground is drawn K z up the screen


def z_of_row(row):
    """The height on the pillar's front whose point the sprites draw on a row (edge) of the art."""
    return (42.0 - row - BOTTOM_Y) / K


# The drums and grooves (rows of the art on the pillar's front: a groove 33-37 under the top, the upper drum 37-53,
# a groove 53-56, the lower drum 56-72 and its foot rounding into the ground over 72-79).
Z_DRUM1 = z_of_row(55.5)        # the lower drum's top
Z_DRUM2 = (z_of_row(54.0), z_of_row(36.5) - 0.8)   # the upper drum
Z_HEAD = z_of_row(36.5) - 1.6   # the top cap's foot, in the upper drum's rounded top (its edge dark: the groove)


def drawn(objects):
    """Into the sprites' oblique view: each point moved K z up the screen."""
    for obj in objects:
        sh.apply_modifiers(obj)
        obj.data.transform(Matrix.Shear("XY", 4, (0.0, K)))


def upright(objects):
    """Back out of the oblique view: each point moved K z down the screen."""
    for obj in objects:
        sh.apply_modifiers(obj)
        obj.data.transform(Matrix.Shear("XY", 4, (0.0, -K)))


def _outline(segments):
    """The cross-section's superellipse (A x D) as (x, y) points spaced evenly along it, round (0, 0)."""
    fine = []
    for i in range(720):
        a = 2 * math.pi * i / 720
        ca, sa = math.cos(a), math.sin(a)
        fine.append((math.copysign(abs(ca) ** (2 / POWER), ca) * A, math.copysign(abs(sa) ** (2 / POWER), sa) * D))
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


def section(z, scale=1.0, segments=72):
    """A horizontal cross-section of the pillar at height z, scaled by `scale` about its axis."""
    if segments not in _OUTLINES:
        _OUTLINES[segments] = _outline(segments)
    return [Vector((x * scale, CY + y * scale, z)) for x, y in _OUTLINES[segments]]


def axis(z):
    return Vector((0.0, CY, z))


def drum(name, z0, z1, mat, round0=1.6, round1=1.6, step=1.0):
    """A drum of the pillar from z0 to z1, its ends rounded over round0 / round1."""
    zs = []
    count = max(2, int(math.ceil((z1 - z0) / step)))
    for i in range(count + 1):
        zs.append(z0 + (z1 - z0) * i / count)
    zs += [z0 + round0 * f for f in (0.15, 0.4, 0.7)] + [z1 - round1 * f for f in (0.05, 0.15, 0.3, 0.5, 0.7)]
    zs = sorted(set(round(z, 4) for z in zs if z0 <= z <= z1))
    rings = []
    for z in zs:
        d0, d1 = z - z0, z1 - z
        scale = 1.0
        if d0 < round0:
            u = 1.0 - d0 / round0
            scale = min(scale, 0.9 + 0.1 * math.sqrt(max(0.0, 1.0 - u * u)))
        if d1 < round1:
            u = 1.0 - d1 / round1
            scale = min(scale, 0.9 + 0.1 * math.sqrt(max(0.0, 1.0 - u * u)))
        rings.append(section(z, scale))
    obj = k.loft(name, rings, mat, start_point=axis(zs[0]), end_point=axis(zs[-1]))
    return k.smooth(obj, 55)


def head(name, mat, edge=2.2):
    """The pillar's top: a cap from Z_HEAD up to HEIGHT, its edge rounded over `edge`, its top rising a little to
    a low crown in its middle (a fine grid on top, for the sprites' pixels to paint)."""
    outline = [(x, CY + y) for x, y in _outline(96)]

    def z_of(x, y, e):
        rr = min(1.0, (abs(x) / A) ** POWER + (abs(y - CY) / D) ** POWER)
        return HEIGHT - edge * (1.0 - e) + CROWN * (1.0 - rr)
    obj = kit.heightfield(name, [outline], z_of, mat, spacing=1.1, smooth_angle=55, edge=edge)
    sh.cut_planes([obj], [((0, 0, Z_HEAD), (0, 0, -1))])
    return obj


def rock_noise(obj, amount, seed, scale=2.2):
    """Roughens a drum: each vertex moves out from the axis by smooth noise (and the top's up and down)."""
    rng = __import__("random").Random(seed)
    waves = [(Vector([rng.uniform(-1, 1) for _ in range(3)]).normalized() / scale, rng.uniform(0, 6.3))
             for _ in range(9)]
    sh.apply_modifiers(obj)
    for v in obj.data.vertices:
        co = v.co
        out = co - axis(co.z)
        d = sum(math.sin(wv.dot(co) + ph) for wv, ph in waves) / math.sqrt(len(waves))
        on_top = min(1.0, max(0.0, (co.z - HEIGHT + 1.0) / 1.0))
        if out.length > 1e-6:
            co = co + out.normalized() * d * amount * (1.0 - on_top)
        v.co = co + Vector((0.0, 0.0, d * amount * 0.9 * on_top))
    return obj


def gouge(obj, depth_at, max_depth):
    """Hollows: pushes the vertices in by depth_at(x, y) * max_depth (depth_at in the sprites' oblique view, where
    each point is drawn): the sides in towards the axis, the top down."""
    sh.apply_modifiers(obj)
    for v in obj.data.vertices:
        co = v.co
        d = depth_at(co.x, co.y + K * co.z)
        if d <= 0:
            continue
        inward = axis(co.z) - co
        on_top = min(1.0, max(0.0, (co.z - HEIGHT + 3.0) / 2.0))
        side = inward.normalized() * min(inward.length * 0.7, d * max_depth) if inward.length > 1e-6 else Vector()
        down = Vector((0.0, 0.0, -min(6.5, d * max_depth * 0.7)))
        v.co = co + side * (1.0 - on_top) + down * on_top
    return obj


def column_whole(broken=False):
    """The column in the sprites' oblique view, painted (see the module's doc)."""
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
    parts.append(drum("drum1", -0.6, Z_DRUM1, rock, round0=0.8, round1=1.8))
    parts.append(drum("drum2", Z_DRUM2[0], Z_DRUM2[1], rock, round0=1.8, round1=1.8))
    parts.append(head("head", rock))
    for i, obj in enumerate(parts):
        rock_noise(obj, 0.55 if obj.name == "head" else 0.35, seed=5 + i)
    # The grooves: the core between the drums, dark.
    cores = []
    for name, z0, z1 in (("core1", Z_DRUM1 - 1.0, Z_DRUM2[0] + 1.0), ("core2", Z_DRUM2[1] - 1.0, Z_HEAD + 1.0)):
        rings = [section(z, 0.86, 40) for z in (z0, (z0 + z1) / 2, z1)]
        cores.append(k.smooth(k.loft(name, rings, dark, start_point=axis(z0), end_point=axis(z1)), 50))

    if broken:
        # Hollows where the broken sprites show the dark grey insides (ramp 6), deepest in their middles.
        hollow = kit.field(f, lambda v: 1.0 if v >> 4 in (6,) else (0.5 if v >> 4 == 0 and (v & 15) <= 2 else 0.0),
                           lambda v: True, blur=2)
        depth = kit.field_sampler(f, hollow)
        for obj in parts:
            if obj.name in ("head", "drum2"):
                gouge(obj, lambda x, y: max(0.0, depth(x, y) - 0.2) * 1.4 if y > -14.0 else 0.0, 9.0)
                rock_noise(obj, 0.45, seed=11)
    drawn(parts + cores)
    if broken:
        # The top's back right corner broken away, along the diagonal the sprites draw from (col 23, row 2) to
        # (col 46, row 26).
        for obj in parts:
            if obj.name == "head":
                kit.cut_plane(obj, (11.0, 27.5, 0.0), (24.0, 23.0, 0.0))
    for obj in parts:
        kit.clip_below(obj, 0.0)
        paint(obj)

    # The top's rounded edge and foot (steep once upright) in one dark tan: the sprites' pixels streak them.
    edge_mat = paint.material(10, 4)

    def steep(n):
        u = Vector((n.x, n.y, n.z + K * n.y))  # the face's normal once upright
        return u.length > 1e-6 and u.z / u.length < 0.75
    kit.paint_faces(parts[2], lambda c, n: edge_mat if steep(n) else None)


def broken_whole():
    column_whole(broken=True)


def column_piece(builder, box, centre):
    """A piece of the column: the part its sprite draws (the whole in the oblique view cut along the sprite's
    edges), stood upright, round its sprite's centre."""
    builder()
    w.bake()
    kept = sh.cut_box(w.meshes(), *box)
    upright(kept)
    sh.move(kept, -centre[0], -centre[1])
    for obj in kept:
        k.smooth(obj, 40)


for whole_fn, f, names in ((column_whole, ROCK, ("tl", "tr", "ml", "mr", "bl", "br")),
                           (broken_whole, BROKEN, ("tl", "tr", "ml", "mr"))):
    prefix = "rock_column_wreck" if whole_fn is broken_whole else "rock_column"
    for i, n_ in enumerate(names):
        piece_name, box, centre, mask = kit.quarter(f"{prefix}_{n_}", f, 24 * (i % 2), 28 * (i // 2))
        kit.model(piece_name, mask=mask)(lambda fn=whole_fn, box=box, centre=centre: column_piece(fn, box, centre))
    # The whole, for --whole (its views in the oblique view, as the sprites draw it).
    kit.pieced(prefix, whole_fn, (48, 84), [])


if __name__ == "__main__":
    kit.run()
