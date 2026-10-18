"""GRYPHON's blue tower with the glowing orb (sheet G sprite 201, 2x2: 24 x 28 pixels; custom events 51 put
144 of them on the top layer; not animated), polished (2026-10-18; it replaces wave3_r_beasts.py's
orb_tower). models.cfg: sprite g 201 orb_tower yaw=0 glow=20:0.3:62:-0.3:-9.3 (the orb's light).

As the sprite draws it (no 4x upscale of G 201 exists; columns are the sprite's, rows from its top),
symmetric about column 11: a pale blue orb glowing almost white on its upper left (columns 7-15 of rows
0-7) on a collar (row 8), at the back of a blue steel body (columns 5-18 of rows 9-24). Through the
body's upper part goes a square port (the transparent columns 11-12 of rows 11-12 in a dark frame);
two light ribs run down the body beside it (columns 6-7 above, 8 and 14 below), a grille of light
slats between them (rows 14-18); shoulder blocks stand out either side (columns 0-4 and 18-22 of rows
13-19, dark seams between them and the body); below them the body narrows to a blunt point (rows
19-26) and two brown claws (the sprite's ramp 10, columns 3-6 and 16-19 of rows 20-24) curl out and
down from under the shoulders. Nothing round it is ground: every pixel outside its dark outline is
transparent (it is placed by custom events anywhere on the top layer).

The sprite draws the tower from above and in front, its orb at the top of the picture: modelled as
the sprite lays it out, the orb high on a neck at the back, the body falling from there to its point
at the front, so that the game's slanted camera sees it as the sprite does and the silhouette seen
from straight above matches.

Origin at the sprite's centre (pixel 12, 14); +Y up the sprite, +Z towards the camera (z = 0 its
underside; the game centres top-layer objects in height).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the
silhouette against G 201's pixels, written below), --preview <prefix>.
"""
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402

# G 201's pixels ('#'); the port's hole is transparent.
SPRITE = """
.........#####..........
........#######.........
.......#########........
......###########.......
......###########.......
......###########.......
......###########.......
......###########.......
......############......
.....##############.....
.....##############.....
.....######..######.....
.....######..######.....
.#####################..
#######################.
#######################.
#######################.
#######################.
#######################.
.#####################..
..###################...
..###################...
..###################...
...#################....
...#################....
....###############.....
.........#####..........
........................
"""

AXIS = -0.3                 # the tower's middle (column 11; its upper part is centred half a pixel right)
# The body in sections from its back (under the collar) to its point: y, half-width, height.
BODY = [(5.75, 5.6, 6.4), (5.2, 6.85, 6.9), (3.0, 6.95, 6.8), (1.0, 6.85, 6.4), (-1.5, 6.5, 5.8), (-4.0, 6.3, 5.0),
        (-6.5, 6.0, 4.1), (-8.5, 5.0, 3.2), (-10.0, 4.0, 2.4), (-11.0, 2.9, 1.85), (-11.6, 1.5, 1.5)]
BODY_POWER = 3.2            # its sections: superellipses, squarer than ellipses
PORT = (0.0, 1.3, 0.7, 3.3)  # the square port through it: middle x, half-width, y0, y1 (columns 11-12, rows 11-12)
GRILLE = (2.35, -5.3, 0.3, 0.45, (-0.55, -2.55, -4.55))  # half-width, y0, y1, depth, its slats' y (rows 14-18)
RIBS = (3.55, 5.0, -7.2)    # the light ribs beside the port and the grille: offset from the middle, from y, to y
# The shoulder blocks (columns 0-4 and 18-22 of rows 13-19): from the middle out, y range, heights.
SHOULDER = (5.8, 11.25, -5.65, 0.7, 4.6, 3.7)  # inner, outer, y0, y1, top at the back, top at the front
# The claws: points along each from under the shoulder to its tip.
CLAW = [(6.3, -4.9, 2.2, 1.75), (7.25, -6.9, 2.05, 1.9), (7.35, -8.9, 1.7, 1.6), (6.6, -10.5, 1.15, 1.05),
        (5.6, -11.2, 0.65, 0.55)]  # out, y, z, radius
ORB = (9.3, 10.3, (4.95, 4.3, 4.5))  # the orb's middle (y, z) and radii (columns 6-16 of rows 0-8)
HOT = ((-0.55, 0.45, 0.75), 4.05)    # its hot core (the sprite's white): offset from the orb's middle, radius
# The collar under the orb (row 8): its middle (y), its profile (radius, z) from its foot up, its plan squashed in y.
COLLAR = (5.6, [(2.6, 5.6), (3.5, 5.75), (4.05, 6.3), (4.1, 6.9), (3.7, 7.35), (2.8, 7.55)], 0.62)


def materials():
    glow = k.level_palette()
    return {
        "body": k.material("orbtower_body", palette=0x39, metallic=0.5, roughness=0.3),
        "shoulder": k.material("orbtower_shoulder", palette=0x3a, metallic=0.5, roughness=0.3),
        "rib": k.material("orbtower_rib", palette=0x3c, metallic=0.55, roughness=0.24),
        "dark": k.material("orbtower_dark", palette=0x32, metallic=0.3, roughness=0.6),
        "slat": k.material("orbtower_slat", palette=0x38, metallic=0.5, roughness=0.3),
        "collar": k.material("orbtower_collar", palette=0x3b, metallic=0.6, roughness=0.22),
        "orb": k.material("orbtower_orb", palette=0x3d, roughness=0.1, emission=glow[0x3d], emission_strength=0.9),
        "orb_hot": k.material("orbtower_orb_hot", palette=0x3f, roughness=0.1, emission=glow[0x3f],
                              emission_strength=1.4),
        "claw": k.material("orbtower_claw", palette=0xa8, metallic=0.35, roughness=0.32),
        "claw_dark": k.material("orbtower_claw_dark", palette=0xa4, metallic=0.3, roughness=0.4),
    }


def body(m):
    rings = []
    for y, hw, h in BODY:
        rings.append(k.ring(y, hw, h, 48, z=0.0, x=AXIS, top=1.0, bottom=0.001, power=BODY_POWER))
    obj = k.loft("body", list(reversed(rings)), m["body"])
    # The port through it, the grille's recess in its front.
    px, hw, y0, y1 = PORT
    mk.boolean(obj, mk.box("port", px - hw, px + hw, y0, y1, -1.0, 20.0, m["dark"]), "DIFFERENCE")
    gw, gy0, gy1, depth, slats = GRILLE
    top = mk.surface([obj])
    floor = min(top(AXIS, y)[0].z for y in (gy0, gy1)) - depth
    mk.boolean(obj, mk.box("grille", AXIS - gw, AXIS + gw, gy0, gy1, floor, 20.0, m["dark"]), "DIFFERENCE")
    mk.cleanup(obj, dissolve=0.0)
    mk.paint(obj, lambda c, n: m["dark"] if (abs(c.x - px) < hw + 0.05 and y0 - 0.05 < c.y < y1 + 0.05) or
             (abs(c.x - AXIS) < gw + 0.05 and gy0 - 0.05 < c.y < gy1 + 0.05 and c.z < floor + 1.5) else None)
    k.smooth(obj, 40)
    for i, y in enumerate(slats):
        z = floor + 0.25
        bar = mk.box(f"slat{i}", AXIS - gw + 0.05, AXIS + gw - 0.05, y - 0.42, y + 0.42, z - 0.4, z + 0.45, m["slat"])
        mk.bevel(bar, 0.2, 2, 35)
        mk.shade(bar, 40)
    # The ribs beside the port and the grille.
    hit = mk.surface([obj])
    off, ya, yb = RIBS
    for side in (-1, 1):
        points, ups = [], []
        for j in range(20):
            h = hit(AXIS + side * off, ya + (yb - ya) * j / 19)
            if h is not None:
                points.append(h[0])
                ups.append(h[1])
        k.smooth(mk.bar(f"rib{side}", points, ups, 0.5, 0.4, 0.5, m["rib"], 12, 3.0), 40)
    return obj


def shoulders(m):
    inner, outer, y0, y1, zb, zf = SHOULDER
    top = mk.plane((0, y1, zb), (1, y1, zb), (0, y0, zf))
    for side in (-1, 1):
        xa, xb = sorted((AXIS + side * inner, AXIS + side * outer))
        block = mk.wedge(f"shoulder{side}", [(xa, y0), (xb, y0), (xb, y1), (xa, y1)], 0.0, top, m["shoulder"])
        mk.soften(block, 0.2, 9, 0.6, 0.12)


def claws(m):
    for side in (-1, 1):
        claw = mk.smooth_tube(f"claw{side}", [(AXIS + side * u, y, z, r) for u, y, z, r in CLAW], m["claw"], 16)
        mk.paint(claw, lambda c, n: m["claw_dark"] if n.z < -0.1 or (n.x * side > 0.5 and n.z < 0.4) else None)
        k.smooth(claw, 50)


def orb(m):
    y, z, radii = ORB
    collar_y, profile, squash = COLLAR
    k.smooth(mk.lathe("collar", profile, (AXIS, collar_y), m["collar"], segments=40, squash=(1.0, squash)), 45)
    # A neck from the body up to the orb.
    k.smooth(mk.lathe("neck", [(2.2, 5.0), (2.2, z - radii[2] + 1.0)], (AXIS, (collar_y + y) / 2), m["collar"],
                      segments=24, squash=(1.0, 1.3)), 45)
    mk.ball("orb", (AXIS, y, z), radii, m["orb"], 40, 20)
    # Its hot core showing through on its upper left, where the sprite's white lies.
    (dx, dy, dz), r = HOT
    mk.ball("orb_core", (AXIS + dx, y + dy, z + dz), (r * radii[0] / radii[2], r * radii[1] / radii[2], r),
            m["orb_hot"], 40, 20)


def build():
    options = k.args()
    k.reset()
    m = materials()
    body(m)
    shoulders(m)
    claws(m)
    orb(m)
    parts = mk.meshes()
    if "check" in options:
        mk.compare("orb_tower (G 201)", mk.coverage(parts, 24, 28),
                   [[c == "#" for c in line] for line in SPRITE.strip().splitlines()])
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    mk.report("orb_tower", parts, os.path.join(mk.outdir(options), "orb_tower.glb"))
    if "preview" in options:
        mk.preview(options["preview"] + "orb_tower", parts)


if __name__ == "__main__":
    build()
