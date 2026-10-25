"""What is left of CORAL's long tan spiral shell once it is destroyed, under its lower piece (stage 4 of the clean ground:
the wreck model that stands in for the map's painting of it; sheet T sprite 51, the shell's base), built on
polish_coral_sea.py's shell (2026-10-25). models.cfg: model coral_shell_base_wreck enemies/coral_shell_base_wreck.glb
origin; wreck t 51 coral_shell_base_wreck. The game draws it where CORAL paints the broken shell (three places: (396,
4102), (588, 4242), (492, 4466)), with 51's sprite line's options (yaw=0 height=-4), at 51's place. The map paints only
the lower piece's wreck: over the upper piece (T 13) it paints the sea floor (no stand-in there).

The painting (the same at the three places; columns and rows of the 24 x 28 sprite, the water round it the map's): the
shell's lower whorls as the live sprite draws them (tan, 0xa3-0xaa), broken open at their upper end: a narrow jagged
tip left at the sprite's top (columns 10-14 of rows 0-1), its sides torn back (the left edge from column 11 at row 0
to column 4 at row 6, the right from column 13 at row 0 to column 19 at row 8: the live shell fills columns 5-19
there), a black hollow (0x00, its rim brown-black 0x10 and 0xa2) through the broken end (columns 8-18 of rows 1-9), a
smaller hole in its left flank (columns 3-6 of rows 10-13), a crack (columns 10-12 of rows 10-11), the mouth at the
foot black (0x00, 0x10: the live one 0xb0, 0xb1), the shades round the breaks darker; in the HD tiles a pale chip
beside its right flank.

The model: polish_coral_sea.py's shell (whole, world: lying on the floor; its loft and mouth rebuilt here unpainted,
shell_body), broken without booleans: its upper end narrowed towards the painting's tip and sunk (TAPER, SINK: the
torn sides), dents pressed in along the normals where the painting is black (DENTS: the broken end's hollow and its
notch, the flank's hole, the crack), then painted as the live shell (by the light, the whorls), the dents' middles and
the mouth the brown-black 0x10, darker round the dents; the tan scorched round the breaks (polish_jaw_gun_wreck.scorch:
three shades darker, the soot 0x10 nearest), a pale chip of shell and two dark ones on the floor. Cut into the base
piece as the live one (polish_coral_sea.export_pieces: in the picture's frame), moved so that 51's middle is its origin.

Coordinates as polish_coral_sea.py's shell: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the sea floor;
the whole's origin is its picture's middle (24 x 56): the base sprite's pixel corner (c, r) is (c - 12, -r) in the
picture (y + z tan 20).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir>, --preview <prefix>, --whole
<prefix>.
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_jaw_gun_wreck import scorch, rock, shard  # noqa: E402
from polish_pyramid_wreck import Noise  # noqa: E402
import polish_coral_sea as live  # noqa: E402

TAN = live.TAN_T
SEED = 51
PIECES = [("coral_shell_base_wreck", 51, (-12.0, 12.0, -28.0, 0.0))]

# The broken end: the shell narrowed towards the sprite's top (rows of the base sprite, how much of its half width is
# left, where its middle is (column)), and sunk (its height scaled by SINK + (1 - SINK) * the width left).
TAPER = [(-2.0, 0.2, 12.4), (0.0, 0.24, 12.3), (3.0, 0.5, 11.8), (6.0, 0.84, 10.9), (8.6, 1.0, 12.0)]
SINK = 0.55
# Dents pressed into it, their middles black (picture middle (column, row), radii, depth): the broken end's hollow,
# the hole in its left flank, the crack, the dark notch on its right.
DENTS = [((13.2, 4.6), (3.9, 4.4), 3.8), ((15.8, 7.4), (2.4, 1.7), 2.0), ((4.8, 11.8), (1.8, 1.9), 1.5),
         ((11.2, 10.8), (1.6, 0.9), 0.8)]
DENT_BLACK = 0.72                       # (of the radius: black inside, darker round it)
# The scorch round the breaks: spots (column, row, radii, strength), its noise, its levels.
SPOTS = [(13.0, 4.0, 6.5, 6.0, 0.75), (5.0, 11.6, 3.0, 3.0, 0.6), (11.2, 10.9, 2.6, 1.8, 0.4),
         (17.0, 20.0, 4.0, 3.5, 0.45)]
LEVELS = (0.35, 0.8)
# Chips of shell on the floor: (column, row (where the camera sees them), size, heading, palette index).
CHIPS = [(19.6, 15.2, 0.7, 30.0, 0xaa), (20.4, 9.6, 0.6, -20.0, 0xa4), (6.6, 4.2, 0.55, 60.0, 0xa3)]


def P(c, r):
    return (c - 12.0, -r)


def taper_at(r):
    """The width left and the middle (column) at a row of the base sprite."""
    if r <= TAPER[0][0]:
        return TAPER[0][1:]
    for (r0, w0, c0), (r1, w1, c1) in zip(TAPER, TAPER[1:]):
        if r <= r1:
            t = (r - r0) / (r1 - r0)
            return w0 + (w1 - w0) * t, c0 + (c1 - c0) * t
    return 1.0, None


def dent_q(x, y, z, i):
    (c, r), (rc, rr), _ = DENTS[i]
    pc, pr = x + 12.0, -(y + z * TAN)
    return math.hypot((pc - c) / rc, (pr - r) / rr) + 0.14 * dent_q.noise(pc * 1.1 + 3.0 * i, pr * 1.1)


dent_q.noise = Noise(SEED + 5, 0.9)


def break_shell(body, frame):
    """The shell's upper end narrowed and sunk (TAPER), the dents pressed in along the normals (DENTS)."""
    tip, axis, d, side = frame
    mesh = body.data
    for v in mesh.vertices:
        r = -(v.co.y + v.co.z * TAN)
        w, c = taper_at(r)
        if c is None:
            continue
        t = max(0.0, min(1.0, (Vector((v.co.x, v.co.y, 0.0)) - tip).dot(d) / axis.length))
        ax = (tip + axis * t).x
        v.co.x = (c - 12.0) + (v.co.x - ax) * w
        v.co.z *= SINK + (1.0 - SINK) * w
    mesh.update()
    nn = [Vector(tuple(n)) for n in live.vertex_normals(mesh)]
    for v, n in zip(mesh.vertices, nn):
        if not (n.z > 0.1 or n.y < -0.3):
            continue
        for i, (_, _, depth) in enumerate(DENTS):
            q = dent_q(v.co.x, v.co.y, v.co.z, i)
            if q < 1.0:
                v.co -= n * depth * (1.0 - q * q)
    mesh.update()


def burn(co):
    c, r = co.x + 12.0, -(co.y + co.z * TAN)
    v = 0.12 * burn.noise.fbm(c, r, 2)
    for sc, sr, rc, rr, s in SPOTS:
        v += s * math.exp(-(((c - sc) / rc) ** 2 + ((r - sr) / rr) ** 2))
    return v


burn.noise = Noise(SEED + 2, 1.4)


def shell_body(m):
    """polish_coral_sea.shell_whole's shell before it is painted (its band_split leaves the mesh open along the bands'
    borders, which the exact booleans cannot cut): the loft from its point to its body whorl, the mouth pressed in."""
    tip = Vector((live.SHELL_TIP[0], live.SHELL_TIP[1], 0.0))
    foot = Vector((live.SHELL_FOOT[0], live.SHELL_FOOT[1], 0.0))
    axis = foot - tip
    d = axis.normalized()
    side = Vector((-d.y, d.x, 0.0))
    up = Vector((0, 0, 1))
    rings, segments = 112, 32
    stations = []
    for i in range(rings + 1):
        t = i / rings
        r = live.shell_radius(t)
        c = tip + axis * t
        c.z = r * live.SHELL_SQUASH + 0.25
        ring = []
        for j in range(segments):
            a = 2 * math.pi * j / segments
            dist = whorl(t, a)
            groove = live.SUTURE[0] * math.exp(-(dist / live.SUTURE[1]) ** 2)
            bulge = 0.025 * math.cos(dist - math.pi)
            rr = r * (1.0 - groove + bulge)
            ring.append(c + side * (math.cos(a) * rr) + up * (math.sin(a) * rr * live.SHELL_SQUASH))
        stations.append(ring)
    end = tip + axis + d * 0.4
    end.z = live.shell_radius(1.0) * live.SHELL_SQUASH + 0.25
    body = k.loft("shell_body", stations, m[0xa6], start_point=tuple(tip + Vector((0, 0, 0.25)) - d * 0.3),
                  end_point=tuple(end))
    k.smooth(body, 50)
    (px, py), (rx, ry, depth) = live.MOUTH
    mesh = body.data
    nn0 = [Vector(tuple(n)) for n in live.vertex_normals(mesh)]
    for v, n in zip(mesh.vertices, nn0):
        q = math.hypot((v.co.x - px) / rx, (v.co.y + v.co.z * TAN - py) / ry)
        if (n.z > 0.15 or n.y < -0.3) and q < 1.0:
            v.co -= n * depth * (1.0 - q * q)
    mesh.update()
    return body, (tip, axis, d, side)


def whorl(t, a):
    """polish_coral_sea.shell_whole's whorl: how far round from the spiral suture (radians)."""
    a = a % (2 * math.pi)
    g = 2.0 * a if a <= math.pi else 0.0
    phase = (live.SHELL_TURNS * t * 2 * math.pi + g) % (2 * math.pi)
    return min(phase, 2 * math.pi - phase)


def paint_shell(body, frame, m, inside):
    """polish_coral_sea.shell_whole's painting (by the light, the whorls' crests lighter, the suture darker, the body
    whorl light), the mouth black: on the broken shell's own faces only (the breaks' faces, inside, kept apart)."""
    import numpy as np
    from polish_orb_red import band_split
    from polish_coral_citadel import light
    tip, axis, d, side = frame
    mesh = body.data
    k.smooth(body, 50)
    nn = live.vertex_normals(mesh)
    lv = light(nn) + live.TIE
    (px, py), (rx, ry, depth) = live.MOUTH
    extra = []
    for v in mesh.vertices:
        rel = Vector((v.co.x, v.co.y, 0.0)) - tip
        t = max(0.0, min(1.0, rel.dot(d) / axis.length))
        c = tip + axis * t
        c.z = live.shell_radius(t) * live.SHELL_SQUASH + 0.25
        off = v.co - c
        a = math.atan2(off.z / live.SHELL_SQUASH, off.dot(side))
        dist = whorl(t, a)
        e = 1.4 + 0.5 * math.cos(dist - math.pi) * 0.5 - 2.0 * math.exp(-(dist / 0.26) ** 2)
        e += 1.6 * float(live.sstep(0.8, 0.97, t))
        q = math.hypot((v.co.x - px) / rx, (v.co.y + v.co.z * TAN - py) / ry)
        e += 2.0 * math.exp(-((q - 1.12) / 0.14) ** 2)
        if q < 1.0:
            e = -60.0
        for i in range(len(DENTS)):
            qd = dent_q(v.co.x, v.co.y, v.co.z, i)
            if qd < DENT_BLACK:
                e = -60.0
            elif qd < 1.4:
                e -= 3.2 * (1.4 - qd) / (1.4 - DENT_BLACK)
        extra.append(e)
    lv = lv + np.array(extra)
    band_split(body, lv, [(-99.0, inside)] + [(lo if lo > -99 else -40.0, m[i]) for lo, i in live.TAN])
    k.smooth(body, 50)


def build_whole(m):
    inside = k.material("coral_shell_inside", palette=0x10, metallic=0.0, roughness=0.95)
    body, frame = shell_body(m)
    break_shell(body, frame)
    paint_shell(body, frame, m, inside)
    parts = [body]
    # the tan scorched round the breaks
    scorch(body, burn, LEVELS)
    k.smooth(body, 50)
    for i, (c, r, size, heading, index) in enumerate(CHIPS):
        x, yp = P(c, r)
        z = size * 0.2
        mat = k.material("coral_shell", palette=index, **live.SHELL_FINISH)
        if i == 0:
            y = yp - z * TAN
            chip = shard("shell_chip%d" % i, [(x - size, y - size * 0.6), (x + size, y - size * 0.4),
                                              (x + size * 0.6, y + size * 0.7), (x - size * 0.7, y + size * 0.5)],
                         0.0, 0.35, mat, (14.0, -10.0))
        else:
            chip = rock("shell_chip%d" % i, (x, yp - z * TAN, 0.0), (size, size * 0.7, size * 0.45), mat, 4.0 + 1.9 * i)
            chip.data.transform(Matrix.Translation((x, yp, 0)) @ Matrix.Rotation(math.radians(heading), 4, "Z") @
                                Matrix.Translation((-x, -yp, 0)))
        parts.append(chip)
    for obj in parts:
        mk.apply(obj)
    return parts


def build():
    options = k.args()
    out = mk.outdir(options)
    k.reset()
    bpy.context.scene.view_settings.view_transform = "Standard"
    m = live.materials()
    parts = build_whole(m)
    live.export_pieces("coral_shell", parts, PIECES, m[0xa4], (24, 56), options, out, None)


if __name__ == "__main__":
    build()
