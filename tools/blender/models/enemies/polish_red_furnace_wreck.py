"""The red furnace's wreck (sheet D sprite 267's stand-in: what the asteroid maps paint where red_furnace stands once
it is destroyed, before it comes and where none comes; 54 of them in ASTEROID1, ASTEROID2, ASTCITY, AST. CITY and
AST ROCK), built on polish_red_furnace.py (2026-10-25, the clean ground's stage 4).

As the maps paint it at 4x (the asteroid tiles' 357, the most common of its paintings; ASTEROID2 14a0d01cd2b01f4c at
468, 3486): the red housing whole in its place, its rails along its sides, but cracked over its lower part (darker
reds, 0x41-0x42, in lines) and its rim broken at its upper end (0x41-0x45 where the sprite's rim is 0x47-0x4c, the
well running on up through it, 0x70); the pins across the slots gone (the slots dark, 0x01-0x05); the well no longer
dark round a copper rod but burning: its walls red and orange (0x72-0x79, the left wall brighter), two hot spots on it
near white (0x7b, 0x7c; rows 9 and 15), the rod down its middle burnt out black (0x70).

The model: the live furnace (polish_red_furnace: housing, rim, element, rails) with the pins taken out (one lies
fallen in the left slot) and broken: a lumpy exact boolean through the rim's upper end and the housing's edge under it
(its faces burnt, the slots' dark red 0x42), crack grooves cut along jagged lines over the housing's lower part and
its upper left (their walls 0x42); the well's walls and floor glowing faintly with the last of the heat (0x75 at 0.3,
0x73 at 0.25), embers heaped in it (0x73, 0x75, 0x78 at 0.25-0.4), two hot spots on its left wall (0x7b at 0.45), the
heating element burnt out (0x70) and snapped in two, its halves sagging into the well. The rim's lower end keeps the
live height (7.6: more than 7.4, so the game sets the wreck on the ground as it does the live furnace).

The same frame as red_furnace: origin at the sprite's centre (pixel 12, 14), +Y up the sprite, +Z up from the ground
(z = 0); drawn as the live model (models.cfg: model red_furnace_wreck enemies/red_furnace_wreck.glb; wreck d 267
red_furnace_wreck, so the game draws it with sprite d 267's options, yaw=0).

Options after "--": --outdir <dir> (default assets/models/enemies), --preview <prefix>.
"""
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
import polish_red_furnace as live  # noqa: E402
import polish_panel_pills_wreck as wk  # noqa: E402

AX = live.AXIS_X
# The wreck's colours as a frame of the live furnace: the element burnt out, the well's walls and floor glowing
# faintly with the last of the heat.
FRAME = ("red_furnace_wreck", 267, (0x70, 0.0), (0x70, 0.0), (0x75, 0.3), (0x73, 0.25))
# The blast through the rim's upper end: centre, radii, seed.
BLAST = ((AX + 0.6, 11.4, 8.2), (3.3, 2.1, 2.5), 4.0)
# The cracks: jagged lines over the housing's top (x, y), their width and depth.
CRACKS = [([(-10.4, -5.2), (-8.6, -6.4), (-7.0, -8.6), (-5.6, -9.4), (-4.6, -11.6), (-3.8, -13.4)], 0.42, 1.3),
          ([(7.6, -8.4), (5.6, -8.0), (4.4, -9.6), (2.8, -10.2), (2.0, -12.0), (1.2, -13.4)], 0.36, 1.1),
          ([(-10.4, 6.6), (-8.8, 8.0), (-7.8, 10.2), (-6.2, 11.4), (-5.4, 13.6)], 0.32, 1.0),
          ([(-2.6, -12.6), (-1.6, -10.4), (-2.4, -8.6)], 0.26, 0.8)]
# The element snapped at y SNAP; each half turned (degrees) about its far post, sagging into the well.
SNAP, SAG = 1.6, (-9.0, 11.0)
# The hot spots on the well's left wall: (y, z, radius).
HOT = [(4.8, 3.4, 0.85), (-1.6, 3.0, 0.8)]
# Embers heaped in the well either side of the rod: (dx from the well's middle, y, z, radius, shade).
EMBERS = [(-1.45, -4.4, 2.1, 1.0, 0x75), (-1.5, -2.6, 2.3, 1.05, 0x78), (-1.4, -0.4, 2.2, 1.0, 0x75),
          (-1.5, 1.6, 2.4, 1.1, 0x78), (-1.45, 3.4, 2.2, 1.0, 0x75), (-1.5, 6.2, 2.3, 1.0, 0x78),
          (-1.3, 8.2, 2.0, 0.9, 0x73), (1.45, -4.0, 1.9, 0.95, 0x73), (1.5, -1.8, 2.0, 1.0, 0x75),
          (1.45, 0.6, 1.9, 0.95, 0x73), (1.5, 2.8, 2.1, 1.0, 0x75), (1.45, 5.0, 1.9, 0.95, 0x73),
          (1.4, 7.4, 2.0, 0.9, 0x75), (0.1, -5.2, 1.8, 0.8, 0x73), (0.0, 8.8, 1.8, 0.8, 0x75)]
# The pin lying fallen in the left slot: from, to, radius.
FALLEN_PIN = ((AX - 6.8, 4.8, 1.9), (AX - 5.2, -0.6, 1.6), 0.8)


def crack_cutter(name, points, width, depth, mat_):
    """A thin prism along a jagged line (points in plan), from depth under the housing's top up through it."""
    left, right = [], []
    for i, p in enumerate(points):
        a = Vector(points[max(i - 1, 0)])
        b = Vector(points[min(i + 1, len(points) - 1)])
        d = (b - a).normalized()
        n = Vector((-d.y, d.x))
        w = width * (0.5 if 0 < i < len(points) - 1 else 0.15)   # (tapering to its ends)
        left.append(Vector(p) + n * w)
        right.append(Vector(p) - n * w)
    outline = [(v.x, v.y) for v in right + list(reversed(left))]
    return mk.prism(name, outline, live.HOUSING_Z - depth, live.HOUSING_Z + 3.0, mat_)


def build():
    options = k.args()
    k.reset()
    m = live.materials(FRAME)
    m["element_end"] = m["element"]   # (one material for the burnt-out rod)
    # (at most 15 materials a model: the game colours no more from the palette; the slots' dark red walls serve the
    # broken faces, the well's glowing walls and floor some of the embers)
    burnt = m["slot_wall"]
    hot = wk.mat("furnacewreck_hot", 0x7b, 0.0, 0.4, 0.45)
    flame = wk.mat("furnacewreck_ember", 0x78, 0.0, 0.4, 0.4)
    ember_mats = {0x75: m["well"], 0x73: m["floor"], 0x78: flame}
    housing = live.housing(m)
    rim = live.rim(m)
    live.element(m)
    live.rails(m)
    # One pin fallen into the left slot (the others are gone).
    (a, b, r) = FALLEN_PIN
    live.rod("pin_fallen", a, b, r, m["post"], 14)
    # The blast through the rim's upper end and the housing's edge under it.
    (cx, cy, cz), radii, seed = BLAST
    for obj in (rim, housing):
        mk.apply(obj)
        wk.break_away(obj, wk.rock("blast", (cx, cy, cz), radii, burnt, seed, subdivisions=2, rough=0.3))
    # The cracks.
    for i, (points, width, depth) in enumerate(CRACKS):
        wk.break_away(housing, crack_cutter(f"crack{i}", points, width, depth, burnt))
    for obj in (rim, housing):
        k.smooth(obj, 35)
    # The element snapped, its halves sagging into the well (each turned about its far post).
    rod = bpy.data.objects["element"]
    upper = wk.split_piece(rod, (0, SNAP, 0), (0, 1, 0), m["element"], "element_b")
    x, y0, y1, z, _ = live.ELEMENT
    wk.turn([rod], (x, y0 + 0.6, z), (1, 0, 0), SAG[0])
    wk.turn([upper], (x, y1 - 0.6, z), (1, 0, 0), SAG[1])
    for obj in (rod, upper):
        k.smooth(obj, 50)
    # The hot spots on the well's left wall.
    (wcx, wcy), whw, _, _ = live.WELL
    for i, (y, z, r) in enumerate(HOT):
        mk.ball(f"hot{i}", (wcx - whw + 0.15, y, z), (r * 0.6, r, r), hot, 14, 8)
    for i, (dx, y, z, r, shade) in enumerate(EMBERS):
        jx, jy, js = (wk.perlin(i * 0.71, 0.3, 0.5), wk.perlin(i * 0.71, 2.3, 0.5), wk.perlin(i * 0.71, 4.3, 0.5))
        r *= 1.0 + 0.35 * js
        mk.apply(wk.rock(f"ember{i}", (wcx + dx + 0.35 * jx, y + 0.6 * jy, z), (r * 0.75, r * 1.1, r * 0.65),
                         ember_mats[shade], 30.0 + i, 1, 0.35))
    wk.clip_below(mk.meshes())
    wk.finish("red_furnace_wreck", options, live.RIM_TOP)


if __name__ == "__main__":
    build()
