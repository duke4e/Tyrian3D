"""The cage turret's wreck (sheet D sprite 275's stand-in: what the asteroid maps paint where cage_turret stands once
it is destroyed, before it comes and where none comes; 54 of them in ASTEROID1, ASTEROID2, ASTEROID?, ASTCITY,
AST. CITY and AST ROCK), built on polish_cage_turret.py (2026-10-25, the clean ground's stage 4).

As the maps paint it at 4x (the asteroid tiles' 359 over 417, the most common of its paintings; ASTEROID2
14a0d01cd2b01f4c at 468, 3235): the turret whole in its place, but scorched: its tan darker all over (0xa1-0xa6 where
the sprite has 0xa7-0xa9), soot nearly black (0x40) in blotches over the cage; the cage's left inner bar and the cross
bar beside it broken through (rows 7-11, columns 8-10: soot), the back block cracked in its middle (row 2, columns
10-12), the slat across the upper window gone (rows 4-5), the gun's barrel burst on its right (rows 20-22, columns
11-13: a black hole); the lens, the pipes and the two red lamps still there (the lamps' glass red, 0x72-0x76, but its
light out); the bore dark red (0x71-0x73).

The model: the live turret (polish_cage_turret: body, lens, pipes and lamps, chin, collar and gun), frame 275's
colours with the lamps' and the bore's light all but out (0.1-0.2), broken with lumpy exact booleans (their faces
soot, 0x40): through the left inner bar and the cross bar, a crack through the back block's middle, a hole burst in
the gun's right side; the slat gone; the tan scorched all over, a shade or three darker (the sides 0xa5, the tops
0xa7, the windows' walls 0xa3), soot round the blasts; rubble of the broken bars in the windows and at its foot. The
body keeps its top at the live height (7.6: more than 7.4, so the game sets the wreck on the ground as it does the
live turret).

The same frame as cage_turret: origin at the sprite's centre (pixel 12, 14), +Y up the sprite, +Z up from the ground
(z = 0); drawn as the live model (models.cfg: model cage_turret_wreck enemies/cage_turret_wreck.glb; wreck d 275
cage_turret_wreck, so the game draws it with sprite d 275's options, yaw=0).

Options after "--": --outdir <dir> (default assets/models/enemies), --preview <prefix>.
"""
import math
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
import polish_cage_turret as live  # noqa: E402
import polish_panel_pills_wreck as wk  # noqa: E402

# The wreck's colours as a frame of the live turret: frame 275's, the lamps' and the bore's light all but out.
FRAME = ("cage_turret_wreck", 275, [(0x72, 0.1), (0x74, 0.14), (0x76, 0.2)], (0x71, 0.15), None, None)
# The blasts: (part, centre, radii, seed).
BLASTS = [("body", (-4.4, 3.2, 7.8), (2.5, 3.8, 3.0), 1.0),
          ("body", (-1.0, 10.6, 8.2), (1.7, 1.9, 2.6), 2.0),
          ("back", (-1.0, 11.4, 6.2), (1.5, 1.7, 2.0), 2.0),
          ("gun", (2.4, -8.4, 4.0), (1.9, 2.1, 1.8), 3.0)]
# Rubble of the broken bars: (x, y, z, radius, seed).
RUBBLE = [(-6.4, 4.2, 4.2, 0.6, 1.0), (-3.6, 6.6, 4.1, 0.5, 2.0), (-6.8, 0.4, 4.1, 0.45, 3.0),
          (-1.6, 7.2, 4.0, 0.4, 4.0),
          (-11.4, 2.6, 0.3, 0.5, 5.0), (3.6, -9.6, 0.3, 0.45, 6.0), (-4.0, -8.6, 0.3, 0.5, 7.0)]


def soot_near(c):
    """How near a point is to a blast (1 at its middle, 0 at twice its radii out), the edge wandering."""
    best = 0.0
    for _, (bx, by, bz), (rx, ry, rz), _ in BLASTS:
        d = math.sqrt(((c.x - bx) / rx) ** 2 + ((c.y - by) / ry) ** 2 + ((c.z - bz) / rz) ** 2) / 2.0
        best = max(best, 1.0 - d)
    return best + 0.18 * wk.perlin(c.x * 0.6 + 2.0, c.y * 0.6, c.z * 0.6)


def build():
    options = k.args()
    k.reset()
    m = live.materials(FRAME)
    soot = wk.mat("cagewreck_soot", 0x40, 0.1, 0.85)
    scorched = wk.mat("cagewreck_scorched", 0xa5, 0.2, 0.5)
    deep = wk.mat("cagewreck_deep", 0xa3, 0.2, 0.55)
    live.body(m)
    live.lens(m)
    live.pipes_and_lamps(m)
    live.front(m)
    objects = {o.name: o for o in mk.meshes()}
    bpy.data.objects.remove(objects.pop("slat"))
    for obj in objects.values():
        mk.apply(obj)
    for name, centre, radii, seed in BLASTS:
        before = len(objects[name].data.polygons)
        wk.break_away(objects[name], wk.rock("blast", centre, radii, soot, seed, subdivisions=2, rough=0.3))
        assert len(objects[name].data.polygons) > before * 0.5, "the blast emptied " + name
    # The tan scorched all over, a shade or three darker (the sides 0xa5, the tops 0xa7, the windows' walls 0xa3), soot
    # round the blasts (each face by how near its middle is to one, the edge of the soot wandering).
    recolour = {m["tan"].name: scorched, m["tan_top"].name: m["tan_dark"], m["tan_dark"].name: deep}
    for name in ("body", "back", "stub", "chin", "gun") + tuple(n for n in objects if n.startswith("knob")):
        obj = objects[name]
        if name == "body":   # (its top's faces divided round the blasts, so the soot's edge can wander)
            wk.grid_cut(obj, 0.6, 0.98, (-8.6, 1.6, -1.6, 13.4), live.TOP - 0.2)
        k.smooth(obj, 35 if name in ("body", "back", "chin") else 50)
        slots = {key: mk.slot_of(obj, mat_) for key, mat_ in recolour.items()}
        o_slot = mk.slot_of(obj, soot)
        names = [mm.name for mm in obj.data.materials]
        for poly in obj.data.polygons:
            key = names[poly.material_index]
            if key not in recolour:
                continue
            poly.material_index = o_slot if soot_near(poly.center) > 0.22 else slots[key]
    for j, (x, y, z, r, seed) in enumerate(RUBBLE):
        mk.apply(wk.rock(f"rubble{j}", (x, y, z), (r, r * 0.85, r * 0.6), scorched if j % 2 else soot, seed + 40.0,
                         1, 0.3))
    wk.clip_below(mk.meshes())
    wk.finish("cage_turret_wreck", options, live.TOP)


if __name__ == "__main__":
    build()
