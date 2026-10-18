"""The small green machine of TORM and BONUS (sheet J sprite 131, 2x2: 24 x 28 pixels; custom events put
175 of them on the ground and top layers; not animated), polished (2026-10-18; it replaces wave3_m.py's
green_scarab). models.cfg: sprite j 131 green_scarab yaw=0.

As the sprite draws it (no 4x upscale of J 131 exists; columns are the sprite's, rows from its top),
symmetric about column 12: a beetle of green armour (the sprite's ramp 2) in a dark outline. Its
domed shell (rows 8-15, columns 2-22 at its widest) is cut by seams into lobes (dark columns 6, 9, 15
and 18), a light green core glowing along its crest (columns 10-14 of rows 8-13, lightest at rows
10-12), a light stud on each side lobe (columns 5 and 19 of row 9). In front a small head plate
(columns 9-15 of rows 5-7) with two light eyes (columns 11 and 13 of row 6), and at the front corners
two red lamps (columns 5-7 and 17-19 of rows 6-7). Behind the shell two red pods (columns 4-8 and
16-20 of rows 16-21), a yellow light glowing on each (column 6 and 18, rows 18-19), their ends
curling in towards each other (rows 22-23) round a green tail with a dark groove down it (columns
9-15 of rows 16-22). Nothing round it is ground: every pixel outside its outline is transparent.

Origin at the sprite's centre (pixel 12, 14); +Y up the sprite, +Z up from its underside (z = 0).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the
silhouette against J 131's pixels, written below), --preview <prefix>.
"""
import math
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402

# J 131's pixels ('#').
SPRITE = """
........................
........................
........................
........................
........#########.......
.....###############....
....#################...
....#################...
....#################...
...###################..
..#####################.
..#####################.
..#####################.
..#####################.
..#####################.
...###################..
....#################...
....#################...
....#################...
....#################...
....#################...
....#################...
.....###############....
......#############.....
........#########.......
........................
........................
........................
"""

AXIS = 0.5                  # the middle (column 12)
# The shell: its middle along y, half-length; its half-width and height at its middle; the power of
# its sections (squarer than ellipses); how far its sides come down.
SHELL = (1.95, 4.75, 10.2, 5.9, 2.6, 0.6)
SEAMS = (2.95, 6.0)         # the seams between its lobes (columns 9, 15 and 6, 18): out from the middle
CORE = ((0.0, 2.4), (2.35, 3.0, 1.25))  # its glowing crest: middle (x out, y) and radii
CORE_HOT = ((0.45, 1.6), (1.05, 1.15, 1.2))  # its lightest spot (columns 12-13 of rows 10-12)
STUDS = (6.95, 4.7, 0.75)   # the light studs on the side lobes: out, y, radius (columns 5, 19 of row 9)
HEAD = ((0.0, 7.4), (3.75, 2.45, 3.6))  # the head plate: middle and radii (columns 8-16 of rows 4-7)
EYES = (1.0, 7.95, 0.62)    # its eyes: out, y, radius (columns 11 and 13 of row 6)
FRONT_LAMPS = (5.55, 7.05, (1.65, 1.25, 1.35))  # out, y, radii (columns 5-7 and 17-19 of rows 6-7)
# A rear pod: points along it (out, y, z) and radii, from under the shell back and curling in.
POD = [(6.2, -1.2, 2.2, 1.9), (6.3, -3.2, 2.35, 2.25), (6.15, -5.6, 2.3, 2.2), (5.6, -7.6, 2.0, 1.9),
       (4.4, -9.0, 1.6, 1.45), (2.9, -9.75, 1.25, 1.0), (1.9, -10.0, 1.0, 0.65)]  # out, y, z, radius
POD_LIGHT = (6.15, -5.1, (0.95, 1.25, 0.75))  # the yellow light on each: out, y, radii (rows 18-19)
# The tail: half-width and height from under the shell to its tip (columns 9-15 of rows 16-22).
TAIL = [(-1.0, 3.3, 3.4), (-3.0, 3.25, 3.0), (-5.0, 3.05, 2.7), (-7.0, 2.7, 2.35), (-8.6, 2.05, 2.0),
        (-9.7, 1.25, 1.6), (-10.3, 0.5, 1.2)]


def materials():
    glow = k.level_palette()

    def lit(name, index, strength, **kw):
        return k.material(name, palette=index, emission=glow[index], emission_strength=strength, **kw)
    return {
        "shell": k.material("scarab_shell", palette=0x29, metallic=0.35, roughness=0.3),
        "lobe": k.material("scarab_lobe", palette=0x2a, metallic=0.35, roughness=0.28),
        "seam": k.material("scarab_seam", palette=0x23, metallic=0.2, roughness=0.6),
        "core": lit("scarab_core", 0x2d, 0.3, metallic=0.1, roughness=0.12),
        "core_rim": k.material("scarab_core_rim", palette=0x2c, metallic=0.2, roughness=0.2),
        "stud": lit("scarab_stud", 0x2f, 0.4, metallic=0.2, roughness=0.2),
        "tail": k.material("scarab_tail", palette=0x27, metallic=0.35, roughness=0.32),
        "red": k.material("scarab_red", palette=0x74, metallic=0.3, roughness=0.26),
        "red_dark": k.material("scarab_red_dark", palette=0x72, metallic=0.3, roughness=0.35),
        "lamp": lit("scarab_lamp", 0x77, 1.0, roughness=0.15),
        "light": lit("scarab_light", 0x7b, 1.6, roughness=0.15),
        "dark": k.material("scarab_dark", palette=0x02, metallic=0.3, roughness=0.6),
    }


def shell(m):
    yc, half, hw, h, power, side = SHELL
    rings = []
    count = 17
    for i in range(count):
        t = -1 + 2 * i / (count - 1)
        f = math.sqrt(max(0.0, 1 - t * t))
        rings.append(k.ring(yc + half * t, max(0.25, hw * f ** 0.55), max(0.2, h * f ** 0.8), 64, z=side, x=AXIS,
                            top=1.0, bottom=side / max(0.2, h * f ** 0.8), power=power))
    obj = k.loft("shell", rings, m["shell"], start_point=(AXIS, yc - half, side), end_point=(AXIS, yc + half, side))
    # The lobes: the outer ones a shade lighter.
    mk.paint(obj, lambda c, n: m["lobe"] if abs(c.x - AXIS) > SEAMS[1] and n.z > 0.2 else None)
    k.smooth(obj, 50)
    hit = mk.surface([obj])
    # The seams, dark lines along it.
    for off in SEAMS:
        for s in (-1, 1):
            points, ups = [], []
            for j in range(16):
                y = yc - half * 0.86 + 2 * half * 0.86 * j / 15
                h_ = hit(AXIS + s * off, y)
                if h_ is not None:
                    points.append(h_[0])
                    ups.append(h_[1])
            k.smooth(mk.bar(f"seam{s}_{off}", points, ups, 0.24, 0.07, 0.3, m["seam"], 8, 2.5), 40)
    # The glowing core along its crest, in a rim.
    (cx, cy), (rx, ry, rz) = CORE
    top = hit(AXIS + cx, cy)[0].z
    mk.ball("core_rim", (AXIS + cx, cy, top - 0.55), (rx + 0.45, ry + 0.45, rz * 0.75), m["core_rim"], 32, 12)
    mk.ball("core", (AXIS + cx, cy, top - 0.4), (rx, ry, rz), m["core"], 32, 14)
    (hx, hy), (hrx, hry, hrz) = CORE_HOT
    mk.ball("core_hot", (AXIS + hx, hy, top + rz - 0.4 - hrz * 0.75), (hrx, hry, hrz), m["stud"], 20, 10)
    # The studs on the side lobes.
    sx, sy, sr = STUDS
    for s in (-1, 1):
        p, n = hit(AXIS + s * sx, sy)
        mk.ball(f"stud{s}", tuple(p - n * 0.15), (sr, sr, sr * 0.8), m["stud"], 14, 7)
    return obj


def head(m):
    (hx, hy), radii = HEAD
    obj = mk.dome("head", (AXIS + hx, hy), radii, 0.0, m["shell"], 36, 10)
    hit = mk.surface([obj])
    ex, ey, er = EYES
    for s in (-1, 1):
        p, n = hit(AXIS + s * ex, ey)
        mk.ball(f"eye{s}", tuple(p - n * 0.2), (er, er, er * 0.8), m["stud"], 12, 6)
    lx, ly, (rx, ry, rz) = FRONT_LAMPS
    for s in (-1, 1):
        mk.dome(f"lamp_bezel{s}", (AXIS + s * lx, ly), (rx + 0.35, ry + 0.35, rz * 1.05), 0.0, m["dark"], 18, 6)
        mk.dome(f"lamp{s}", (AXIS + s * lx, ly), (rx, ry, rz * 1.6), 0.0, m["lamp"], 18, 8)


def pods(m):
    for s in (-1, 1):
        pod = mk.smooth_tube(f"pod{s}", [(AXIS + s * u, y, z, r) for u, y, z, r in POD], m["red"], 20)
        mk.paint(pod, lambda c, n: m["red_dark"] if n.z < 0.2 else None)
        k.smooth(pod, 50)
        hit = mk.surface([pod])
        lx, ly, radii = POD_LIGHT
        p, n = hit(AXIS + s * lx, ly)
        mk.ball(f"pod_light{s}", tuple(p - n * 0.3), radii, m["light"], 16, 8)


def tail(m):
    rings = []
    for y, hw, h in TAIL:
        rings.append(k.ring(y, hw, h, 24, z=0.0, x=AXIS, top=1.0, bottom=0.001, power=2.4))
    obj = k.loft("tail", list(reversed(rings)), m["tail"])
    k.smooth(obj, 50)
    hit = mk.surface([obj])
    points, ups = [], []
    for j in range(12):
        h = hit(AXIS, -1.5 - 8.2 * j / 11)
        if h is not None:
            points.append(h[0])
            ups.append(h[1])
    k.smooth(mk.bar("tail_groove", points, ups, 0.35, 0.05, 0.35, m["seam"], 8, 2.5), 40)


def build():
    options = k.args()
    k.reset()
    m = materials()
    shell(m)
    head(m)
    pods(m)
    tail(m)
    parts = mk.meshes()
    if "check" in options:
        mk.compare("green_scarab (J 131)", mk.coverage(parts, 24, 28),
                   [[c == "#" for c in line] for line in SPRITE.strip().splitlines()])
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    mk.report("green_scarab", parts, os.path.join(mk.outdir(options), "green_scarab.glb"))
    if "preview" in options:
        mk.preview(options["preview"] + "green_scarab", parts)


if __name__ == "__main__":
    build()
