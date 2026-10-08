"""The eye sphere of LAVA RUN and EYESPY (wave 3, batch AJ; sheet 9), modelled as its sprites look (models.cfg:
yaw=0); the rest of the sheet is in wave3_aj.py, wave3_aj_head.py, wave3_aj_dread.py and wave3_aj_capsule.py, the
kit in wave3_aj_kit.py, the pixels in wave3_aj_art.py.

The levels draw it from nine sprites as the sheet lays them out, 72 x 70 pixels (enemies 327-329 at (x, y - 56),
(x + 24, y - 56), (x + 48, y - 56); 330-332 at (x, y - 28) ..; 333-335 at (x, y - 14) ..), in the sky in LAVA RUN,
on the top layer in EYESPY. The middle row's sprites (191, 193, 195) overlap the bottom row's (210, 212, 214) by
a tile, so they keep only their upper half (eye_sphere_<sprite>, origin): 153, 155, 157 rows 0-27, 191, 193, 195
rows 28-41, 210, 212, 214 rows 42-69.

A big steel ball of armour plates: on its upper left a raised silver plate, on its upper right a curved strip of
blue glass set into it, a piston lying on each side above the eye; on its lower front a great glass eye bulging
from the ball, blue, its black pupil and crosshairs drawn in it, in a dark steel rim. It stands on z = 0 and
rises 30 pixels.

usage: Blender -b --factory-startup -P wave3_aj_eye.py -- [--only name,name] [--preview <prefix>] [--check 1]
       [--stats 1] [--whole <prefix>]
"""
import math
import os
import sys

from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_aj_kit as kit  # noqa: E402
from wave3_aj_kit import k, sh, pal, Painter, smoothstep  # noqa: E402

EYE = kit.frame("EYE", 72, (36, 35))
F = EYE
BALL_C = (35.8, 34.2)       # pixel column, row
BALL_R = (36.3, 34.7, 30.0)
IRIS_C = (35.5, 50.3)
IRIS_R = (21.6, 14.6)


def P(c, r, z=0.0):
    return (c - F.ox, F.oy - r, z)


def cr(x, y):
    return x + F.ox, F.oy - y


def ball_h(c, r):
    q = 1.0 - ((c - BALL_C[0]) / BALL_R[0]) ** 2 - ((r - BALL_C[1]) / BALL_R[1]) ** 2
    return BALL_R[2] * math.sqrt(max(q, 0.0))


def ball_normal(c, r):
    z = ball_h(c, r)
    return Vector(((c - BALL_C[0]) / BALL_R[0] ** 2, -(r - BALL_C[1]) / BALL_R[1] ** 2, z / BALL_R[2] ** 2)).normalized()


def iris_q(c, r):
    return ((c - IRIS_C[0]) / IRIS_R[0]) ** 2 + ((r - IRIS_C[1]) / IRIS_R[1]) ** 2


# The raised silver plate on the upper left (pixel columns, rows), from the sprite's lit plate.
PLATE = [(12.0, 10.6), (14.5, 9.4), (18.0, 8.8), (22.0, 8.6), (25.5, 9.3), (28.0, 11.0), (29.4, 13.6), (30.6, 16.2),
         (33.4, 17.6), (36.6, 18.8), (39.4, 22.0), (41.2, 26.4), (40.8, 30.8), (38.6, 34.2), (34.2, 35.6),
         (29.4, 34.4), (26.6, 31.0), (25.8, 27.8), (20.0, 27.9), (14.0, 26.8), (11.0, 24.2), (10.2, 17.4)]
PISTONS = [((8.4, 30.2), (15.2, 39.8)), ((63.6, 30.4), (57.2, 39.6))]


def plate_lift(c, r):
    """How far the silver plate stands out of the ball (0 off it), its edges bevelled."""
    x, y, _ = P(c, r)
    poly = [P(a, b)[:2] for a, b in PLATE]
    inside = _inside(poly, x, y)
    d = min(kit.seg_dist(x, y, poly[i], poly[(i + 1) % len(poly)])[0] for i in range(len(poly)))
    return 2.4 * smoothstep(0.0, 1.1, d) if inside else 0.0


def _inside(poly, x, y):
    hit = False
    for i in range(len(poly)):
        (ax, ay), (bx, by) = poly[i], poly[i - 1]
        if (ay > y) != (by > y) and x < ax + (y - ay) * (bx - ax) / (by - ay):
            hit = not hit
    return hit


def glass_strip_mask(val, c, r):
    return val >> 4 == 8 and r < 30


def shell_h(c, r):
    z = ball_h(c, r) + plate_lift(c, r)
    # The blue glass strip lies in a shallow groove.
    return z


def ball():
    grey = Painter("eball", shades={0: (1, 2, 3, 4, 5, 6, 7, 8, 9, 0xa, 0xb, 0xc, 0xd, 0xe)}, metallic=0.45,
                   roughness=0.33)
    polys = kit.outlines_of(F, lambda val, c, r: True, smooth=2, epsilon=0.35)

    def z_of(x, y, e):
        c, r = cr(x, y)
        return 0.6 + (shell_h(c, r) - 0.6) * e
    body = kit.heightfield("eball", polys, z_of, grey(0x06), spacing=1.0, edge=1.2)
    k.smooth(body, 40)
    kit.pixelate(body, F)
    kit.paint_sprite(body, F, grey, wall_steps=-1, keep=lambda val: val >> 4 == 0, default=grey(0x04),
                     under=grey(0x02))
    kit.merge_bottom(body)


def eye():
    """The glass eye: a shell over the ball, bulging in its middle, painted pixel by pixel (its pupil and
    crosshairs), in a dark rim."""
    glass = Painter("eiris", shades={8: tuple(range(0, 16)), 9: (0xb, 0xc, 0xd, 0xe, 0xf), 3: (3, 4, 5, 6, 7, 8, 9, 0xa, 0xb, 0xe),
                                    0: (1, 2, 3, 4, 5), 6: (1,)},
                    metallic=0.15, roughness=0.08,
                    glow={**{0x80 + s: 0.12 + 0.03 * s for s in range(16)}, **{0x90 + s: 0.45 for s in range(16)}})
    outline = [P(IRIS_C[0] + IRIS_R[0] * math.cos(2 * math.pi * j / 96),
                 IRIS_C[1] + IRIS_R[1] * math.sin(2 * math.pi * j / 96))[:2] for j in range(96)]

    def z_of(x, y):
        c, r = cr(x, y)
        return ball_h(c, r) + 0.9 + 1.9 * max(0.0, 1.0 - iris_q(c, r)) ** 0.8
    shell = kit.heightfield("eiris", [outline], z_of, glass(0x84), spacing=1.0)
    k.smooth(shell, 70)
    kit.pixelate(shell, F)
    kit.paint_sprite(shell, F, glass, wall_steps=0, default=glass(0x82), blur=1)
    kit.merge_bottom(shell)
    # The rim: a dark steel ring round the eye, lying on the ball.
    rim = pal("eiris_rim", 0x03, metallic=0.55, roughness=0.3)
    pts = []
    for j in range(72):
        t = 2 * math.pi * j / 72
        c, r = IRIS_C[0] + IRIS_R[0] * 1.0 * math.cos(t), IRIS_C[1] + IRIS_R[1] * 1.0 * math.sin(t)
        pts.append(P(c, r)[:2])
    kit.ring_on("eiris_rim", pts, lambda x, y: ball_h(*cr(x, y)), 0.5, 1.15, rim, 10)


def details():
    """The blue glass strip, the pistons."""
    blue = Painter("estrip", shades={8: tuple(range(0, 16)), 0: (1, 2, 3)}, metallic=0.15, roughness=0.08,
                   glow={0x80 + s: 0.15 + 0.03 * s for s in range(16)})
    polys = kit.outlines_of(F, glass_strip_mask, smooth=2, epsilon=0.3, grow=0.3)

    def z_fn(x, y, z):
        return ball_h(*cr(x, y)) - 0.5 + z
    strip = kit.relief("estrip", polys, blue(0x84), sh.pillow_profile(0.9, 0.8, crown=0.3), bottom=0.0, base=0.0,
                       rim=0.2, spacing=0.7, z_fn=z_fn, angle=50)
    kit.paint_sprite(strip, F, blue, wall_steps=-2, keep=lambda val: val >> 4 == 8, default=blue(0x82), blur=1)
    # The pistons: a dark sleeve and a bright rod, lying on the ball.
    sleeve = pal("episton_sleeve", 0x04, metallic=0.55, roughness=0.3)
    rod = pal("episton_rod", 0x0c, metallic=0.75, roughness=0.15)
    for i, ((c0, r0), (c1, r1)) in enumerate(PISTONS):
        a = Vector(P(c0, r0, ball_h(c0, r0) + 1.0))
        b = Vector(P(c1, r1, ball_h(c1, r1) + 1.0))
        m = a.lerp(b, 0.55)
        kit.pipe(f"episton_sleeve{i}", [tuple(a), tuple(m)], 2.0, sleeve, segments=14)
        kit.pipe(f"episton_rod{i}", [tuple(a.lerp(b, 0.45)), tuple(b)], 1.2, rod, segments=12)
        # A dark slot in the ball under it.
        slot = pal("episton_slot", 0x01, metallic=0.3, roughness=0.5)
        kit.pipe(f"episton_slot{i}", [tuple(a - Vector((0, 0, 1.2))), tuple(b - Vector((0, 0, 1.2)))], 2.4, slot,
                 segments=12, squash=0.5)


def eye_whole():
    ball()
    eye()
    details()
    kit.flatten_under(kit.meshes(), 0.0)


PIECES = [
    (153, 0, 0, None), (155, 24, 0, None), (157, 48, 0, None),
    (191, 0, 28, (0, 24, 28, 42)), (193, 24, 28, (24, 48, 28, 42)), (195, 48, 28, (48, 72, 28, 42)),
    (210, 0, 42, None), (212, 24, 42, None), (214, 48, 42, None),
]

kit.PROTECT += ["eball", "eiris", "estrip"]
kit.pieced("eye_sphere", eye_whole, (72, 70), [kit.piece(f"eye_sphere_{s}", F, c0, r0, keep)
                                               for s, c0, r0, keep in PIECES])


if __name__ == "__main__":
    kit.run()
