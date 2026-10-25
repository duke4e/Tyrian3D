"""The bronze eye tub's wreck (sheet D sprite 193's stand-in: what the asteroid maps paint where eye_tub stands once it
is destroyed, before it comes and where none comes; 26 of them in ASTEROID2, ASTCITY and the other asteroid maps),
built on polish_eye_tub.py (2026-10-25, the clean ground's stage 4).

As the maps paint it at 4x (ASTEROID2 14a0d01cd2b01f4c at 516, 3543; ASTCITY 6498eda0c182465c the same): the tub
whole in its place, its rim and staves still bronze (a little darker, sooted at the mouth's edge), but the iris smashed
open: the mouth a black pit with the dark grey housing's quarters and the black X between them showing (the eye gone
from where they cross), the petals' broken edges pale grey round the opening's upper left and right; the front wall
split by dark vertical gashes (columns 5-18 of rows 15-22, the longest down the middle), the lit band and the shutter
gone with the lamp.

The model: the live tub (polish_eye_tub.tub(), its staves, rim and seams, its materials) with the band, the shutter, its
lip and the lamp left out (the window at its foot a dark hole), the front wall split by gashes (exact booleans of thin
jagged prisms across the wall, their walls the inside's black 0x01); the four petals shut, then broken open by a
jagged hole (only their edges under the rim left, wider at the upper left and right, as painted), two broken petals
fallen tilted into the pit; the housing's faces darker (0x03) and the eye gone: a charred lump where the X's arms
cross, a dull ember in it (0x72 at 0.2); the rim's inner edge sooted in patches. Then leaned into place as the live
tub (TUB_FRAME), so the wreck's bounds are the live model's (the game, which centres these models in height, places
the two alike).

The same frame as eye_tub: origin at the sprite's centre (pixel 12, 14), +Y up the sprite, +Z up from the ground
(z = 0); no origin flag (as the live model's line). models.cfg: model eye_tub_wreck enemies/eye_tub_wreck.glb;
wreck d 193 eye_tub_wreck (drawn with sprite d 193's options, yaw=0).

Options after "--": --outdir <dir> (default assets/models/enemies), --preview <prefix>.
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
import polish_eye_tub as live  # noqa: E402
import polish_panel_pills_wreck as wk  # noqa: E402
from polish_jaw_gun_wreck import ember_material, jagged, rock, scorch, shard  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_pyramid_wreck import Hole  # noqa: E402

LIVE_TOP = 11.98                 # the live tub's highest point (its rim's back)
# The gashes down the front wall (in the tub's frame: u across, w up its axis): (u, from w, to w, half-width).
# (the front wall runs from w -4.0 at its foot, where the tub leans forward onto the floor, up to the rim at 7.6)
GASHES = [(-6.5, -2.2, 4.4, 0.8), (-3.4, -3.0, 5.6, 1.0), (-0.3, -0.2, 6.5, 1.05), (2.9, -2.8, 5.2, 0.95),
          (5.9, -1.6, 4.0, 0.75)]
GASH_DEPTH = 1.1                # how far into the wall
# The hole broken through the shut iris: its middle (u, v), radii, power, jag; the petals' edges are what is left.
IRIS_HOLE = ((0.7, -1.3), (6.5, 7.5), 2.8, 0.8)
# The broken petals fallen into the pit: (outline in u, v, w, thickness, tilt about u and v, degrees).
FALLEN = [([(-4.2, 2.6), (-1.2, 3.4), (-1.8, 0.8), (-4.0, 0.2)], live.HOUSING_TOP - 0.9, 0.45, (16.0, -22.0)),
          ([(1.4, -2.8), (4.4, -2.0), (4.0, -4.6), (1.8, -4.8)], live.HOUSING_TOP - 1.2, 0.45, (-20.0, 14.0))]
# The charred lump where the eye was, the ember in it (centre u, v, w and radii).
LUMP = ((0.0, -0.3, live.HOUSING_TOP - 0.55), (1.6, 1.8, 0.8))
EMBER = ((0.35, -0.6, live.HOUSING_TOP - 0.2), (0.55, 0.5, 0.3))


def soot_field(co):
    """The rim's inner edge sooted in patches (in the tub's frame)."""
    q = ((abs(co.x) / live.INNER[0]) ** live.POWER + (abs(co.y) / live.INNER[1]) ** live.POWER) ** (1 / live.POWER)
    near = math.exp(-((q - 1.0) * 6.0) ** 2) if co.z > live.MOUTH - 0.6 else 0.0
    return near * (0.55 + 0.35 * wk.perlin(co.x * 0.45 + 2.0, co.y * 0.45 - 1.0, 0.7))


def gash(name, u, w0, w1, half, mat):
    """A thin jagged prism across the front wall at u, from w0 to w1 up the axis, GASH_DEPTH into it."""
    pts = [(u - half * 0.25, w0), (u + half * 0.3, w0 + 0.1), (u + half, (w0 + w1) * 0.5), (u + half * 0.2, w1),
           (u - half * 0.3, w1 - 0.15), (u - half, (w0 + w1) * 0.45)]
    outline = jagged(pts, 3.0 + u, 0.18, 0.45)
    v_wall = live.wall_point(u, 0.0, 0.0).y
    # (mk.prism along y: the outline in (x, z) = (u, w); extruded from outside the wall into it)
    area = sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(outline, outline[1:] + outline[:1]))
    return mk.prism(name, outline if area > 0 else outline[::-1], v_wall - 1.5, v_wall + GASH_DEPTH, mat, axis="y")


def build():
    options = k.args()
    k.reset()
    frame = live.FRAMES[0]   # (the shut iris, the eye dark)
    m = live.materials(frame)
    m["housing_burnt"] = k.material("tubwreck_housing", palette=0x03, metallic=0.4, roughness=0.5)
    char = k.material("tubwreck_char", palette=0x01, metallic=0.1, roughness=0.9)
    body = live.tub(m)
    mk.apply(body)
    # The front wall split by gashes.
    for i, (u, w0, w1, half) in enumerate(GASHES):
        mk.boolean(body, gash(f"gash{i}", u, w0, w1, half, m["inside"]), "DIFFERENCE")
    mk.cleanup(body, dissolve=0.0)
    scorch(body, soot_field, levels=(0.45, 0.85))
    k.smooth(body, 40)
    # The window at its foot a dark hole (the lamp's place, dark).
    deep = -live.WINDOW_DEPTH - 0.3
    live.wall_slab("window_back", -live.WINDOW_HALF - 0.2, live.WINDOW_HALF + 0.2, live.floor_w(-live.OUTER[1]),
                   live.WINDOW_TOP + 0.2, deep, -live.WINDOW_DEPTH + 0.05, m["inside"],
                   bottom=lambda u: live.floor_w(live.wall_point(u, 0.0, deep).y) + 0.06)
    # The iris broken open: its petals' edges left under the rim.
    (hu, hv), radii, power, jag = IRIS_HOLE
    hole = Hole((hu, hv), radii, power, 77.0, jag, 1.0)
    for petal in live.petals(m, 0.0):
        mk.apply(petal)
        mk.boolean(petal, hole.cutter(petal.name + "_cut", [(live.FLOOR - 1.0, 1.0), (live.MOUTH + 4.0, 1.0)],
                                      m["petal_side"], step=0.4), "DIFFERENCE")
        mk.cleanup(petal, dissolve=0.0)
        if not petal.data.polygons:
            bpy.data.objects.remove(petal)
            continue
        k.smooth(petal, 35)
    # Two broken petals fallen into the pit.
    for i, (outline, w, thick, tilt) in enumerate(FALLEN):
        shard(f"fallen{i}", outline, w, thick, m["petal_side"], tilt)
    # The housing darker, the eye gone: a charred lump where the arms cross, a dull ember in it.
    for face in live.housing(m):
        for i, mt in enumerate(face.data.materials):
            if mt == m["housing"]:
                face.data.materials[i] = m["housing_burnt"]
    rock("eye_lump", LUMP[0], LUMP[1], char, 5.0)
    rock("ember", EMBER[0], EMBER[1], ember_material(0x72, 0.2), 9.0)
    parts = mk.meshes()
    for obj in parts:
        mk.apply(obj)
        obj.data.transform(live.TUB_FRAME)
        obj.data.update()
    wk.clip_below(parts)
    parts = triangulate(mk.meshes())
    bpy.context.view_layer.update()
    wk.finish("eye_tub_wreck", options, LIVE_TOP)


if __name__ == "__main__":
    build()
