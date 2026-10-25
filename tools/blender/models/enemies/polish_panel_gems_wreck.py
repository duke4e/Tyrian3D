"""The panel with gems' wreck (sheet D sprite 127's stand-in: what the asteroid maps paint where panel_gems stands once
it is destroyed, before it comes and where none comes; 169 of them in ASTEROID1, ASTEROID2, ASTEROID?, ASTCITY,
AST. CITY, AST ROCK and GREY MOON), built on polish_panel_gems.py (2026-10-25, the clean ground's stage 4).

As the maps paint it at 4x (the asteroid tiles' 358, the most common of its paintings; ASTEROID? 3ea5fc307b8e3f67 at
564, 3738): the round stone disc in its place with its dark crevice round it, but blasted: the block on the upright's
top end still bright (0x0d-0x0f), the cross's left arm and the lower right cushion still lit (0x09-0x0e), the rest
burnt dark (0x01-0x04): the upper left cushion gone, the right arm smashed, the upright broken between the gems; the
two gems dimmed to dark red (0x70-0x72) and cracked; soot over the disc's lower part (rows 19-23 0x01-0x03).

The model: the live panel (polish_panel_gems.build, run without its export) without its slab of stones (that is the
map's ground, which the 3D terrain shows); the disc on a dark plinth down to the ground where the slab carried it (so
the disc stands where the live one does); broken with exact booleans by lumpy blasts (their faces burnt, 0x03): one
through the right arm, one through the upright between the gems and the crossing; the upper left cushion blown away;
soot laid over the disc, the cushions and the cross in smooth patches (0x04, 0x02), heaviest over the lower part and
round the blasts; the top gem knocked askew in its bezel and dark (0x72), the bottom one dim with an ember's faint
glow (0x74 at 0.25) and still at the live gems' height (6.61), so the wreck's bounds in height are the live model's
and the game, which centres these models in height on the ground enemies' layer, places the two alike; rubble of the
disc's stone where the blasts were, and a little at its foot.

The same frame as panel_gems: origin at the sprite's centre (pixel 12, 14), +Y up the sprite, +Z up from the ground
(z = 0); drawn as the live model (models.cfg: model panel_gems_wreck enemies/panel_gems_wreck.glb; wreck d 127
panel_gems_wreck, so the game draws it with sprite d 127's options, yaw=0; its glow is the live enemy's only).

Options after "--": --outdir <dir> (default assets/models/enemies), --preview <prefix>.
"""
import math
import os
import sys
import types

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k, smoothstep  # noqa: E402
import polish_panel_pills_wreck as wk  # noqa: E402


def load_live():
    """polish_panel_gems.py as a module: it builds and exports when it is run, so its source without that last call,
    its export turned off (its build() then leaves the panel in the scene)."""
    path = os.path.join(HERE, "polish_panel_gems.py")
    source = open(path).read()
    head, tail = source.rsplit("\nbuild()", 1)
    assert not tail.strip(), "polish_panel_gems.py no longer ends with its build() call"
    module = types.ModuleType("polish_panel_gems")
    module.__file__ = path
    exec(compile(head, path, "exec"), module.__dict__)

    class NoExport:
        def __getattr__(self, name):
            return getattr(k, name)

        def finish(self, *args, **kwargs):
            pass
    module.k = NoExport()
    return module


live = load_live()
LIVE_TOP = live.UPRIGHT_TOP + 0.3 + 0.72 * live.GEM_RADIUS   # 6.61: the gems' tables
# The cracks (a plane through a point, its normal), each splitting a part in two: (part, point, normal, the piece
# in front's name).
CRACKS = [("cushion11", (6.0, 3.6, 0), (-0.55, 1.0, 0), "cushion11_b"),
          ("cushion1-1", (6.2, -4.6, 0), (1.0, 0.8, 0), "cushion1-1_b"),
          ("cushion-1-1", (-5.6, -5.4, 0), (1.0, -0.35, 0), "cushion-1-1_b"),
          ("arm", (-live.UPRIGHT - 0.15, 0, 0), (1, 0.12, 0), "arm_mid"),
          ("arm_mid", (live.UPRIGHT + 0.25, 0, 0), (1, -0.18, 0), "arm_right"),
          ("upright", (0, 0.05, 0), (0.15, 1, 0), "upright_top"),
          ("cushion11_b", (6.2, 6.6, 0), (1.0, 0.2, 0), "cushion11_c"),
          ("cushion-1-1", (-8.2, -2.6, 0), (0.6, -1.0, 0), "cushion-1-1_c"),
          ("cushion1-1", (5.6, -7.0, 0), (1.0, -0.3, 0), "cushion1-1_c")]
# How each piece lies now: (piece, pivot, axis, degrees, sink): turned about an axis through the pivot, then lowered.
TILTS = [("cushion11", (9.0, 2.4, 3.7), (0.45, 1, 0), 14.0, 0.0),
         ("cushion11_b", (4.2, 8.4, 3.7), (1, -0.2, 0), -12.0, 0.2),
         ("cushion1-1", (8.6, -6.2, 3.7), (0.8, -1, 0), -16.0, 0.0),
         ("cushion1-1_b", (4.2, -8.0, 3.7), (1, 0.2, 0), 10.0, 0.3),
         ("cushion-1-1", (-9.4, -3.0, 3.7), (0.35, 1, 0), -11.0, 0.1),
         ("cushion-1-1_b", (-4.0, -8.8, 3.7), (1, -0.3, 0), 13.0, 0.0),
         ("arm", (-10.0, 0.0, 3.7), (0, 1, 0), 9.0, 0.0),
         ("arm_right", (10.0, 0.0, 3.7), (0.1, 1, 0), 24.0, 1.1),
         ("cushion11_c", (9.6, 5.2, 3.7), (0.6, 1, 0), 18.0, 0.4),
         ("cushion-1-1_c", (-10.2, -0.6, 3.7), (0.2, 1, 0), 16.0, 0.0),
         ("cushion1-1_c", (8.2, -9.6, 3.7), (1, 0.3, 0), 16.0, 0.4)]
# The upright's top half (with its cap, the top gem and its bezel) knocked back: pivot, axis, degrees, sink.
TOP_HALF = ((0.0, 9.8, 3.7), (1, 0.1, 0), 4.0, 0.45)
# Each plate pushed out from the disc's middle (opening the cracks between them), and its shade: "lit" keeps its
# stone, "soot" is sooted (0x05), "burnt" burnt dark (0x03), as the painting shows them.
PUSH = 0.55
SHADES = {"cushion11": "soot", "cushion11_b": "lit", "cushion1-1": "lit", "cushion1-1_b": "soot",
          "cushion-1-1": "lit", "cushion-1-1_b": "soot", "arm": "lit", "arm_mid": "soot", "arm_right": "burnt",
          "upright": "soot", "upright_top": "soot", "cap": "lit", "cushion11_c": "burnt", "cushion-1-1_c": "soot",
          "cushion1-1_c": "burnt"}
# Rubble: (x, y, z, radius, seed, grey).
RUBBLE = [(-5.2, 4.6, 3.75, 0.95, 1.0, False), (-3.6, 6.8, 3.7, 0.6, 2.0, True), (-7.6, 2.8, 3.65, 0.55, 3.0, True),
          (-6.4, 6.6, 3.5, 0.5, 4.0, False), (5.0, -0.6, 3.9, 0.55, 5.0, True), (0.8, 0.2, 4.2, 0.5, 6.0, False),
          (10.8, -3.2, 0.35, 0.6, 7.0, True), (9.4, -7.0, 0.3, 0.45, 8.0, False), (-9.2, -7.4, 0.3, 0.5, 9.0, True),
          (2.4, -10.4, 0.3, 0.45, 10.0, False), (-11.0, 3.0, 0.3, 0.5, 11.0, True)]


def soot_field(c):
    """How sooted a point of the disc's top is: rays burnt out from the blast at its middle, heavier over the disc's
    lower part and where the upper left cushion was."""
    a = math.atan2(c.y - live.DISC_CENTRE[1], c.x - live.DISC_CENTRE[0])
    rays = wk.perlin(math.cos(a) * 2.2 + 1.0, math.sin(a) * 2.2, 0.7)
    low = 1.0 - smoothstep(-9.0, -3.0, c.y)
    hole = 1.0 - smoothstep(2.0, 5.0, math.hypot(c.x + 5.2, c.y - 4.5))
    return 0.55 * rays + 0.7 * low + 0.8 * hole


def build():
    options = k.args()
    live.build()   # the live panel (k.reset() first), not exported
    objects = {o.name: o for o in mk.meshes()}
    # The slab of stones is the map's ground: gone (the terrain shows the ground).
    for name in list(objects):
        if name == "bed" or name.startswith("stone"):
            bpy.data.objects.remove(objects.pop(name))
    joint = bpy.data.materials["gems_joint@2"]
    disc_mat = bpy.data.materials["gems_disc@6"]
    cushion_mat = bpy.data.materials["gems_cushion@9"]
    cross_mat = bpy.data.materials["gems_cross@11"]
    burnt = wk.mat("gemswreck_burnt", 0x03, 0.05, 0.85)
    soot = wk.mat("gemswreck_soot", 0x04, 0.05, 0.8)
    sooted = wk.mat("gemswreck_sooted", 0x05, 0.05, 0.75)
    gem_dark = wk.mat("gemswreck_gem", 0x72, 0.1, 0.1)
    gem_ember = wk.mat("gemswreck_gem_ember", 0x74, 0.1, 0.1, 0.25)
    stone = wk.mat("gemswreck_stone", 0x07, 0.0, 0.85)

    # The plinth: the disc's foot carried down to the ground where the slab held it, dark as its crevice.
    scale_z = [(1.06, live.SLAB_HEIGHT - 0.1), (1.075, 0.6), (1.09, 0.0)]
    rings = [[Vector((*live.ellipse_point(2 * math.pi * i / 64, s), z)) for i in range(64)] for s, z in scale_z]
    k.smooth(k.loft("plinth", rings, joint, cap_start=False, cap_end=False), 40)

    # The upper left cushion blown away, the groove between the gems with it.
    for name in ("cushion-11", "groove"):
        bpy.data.objects.remove(objects.pop(name))
    # The cross and the cushions cracked into plates, the plates heaved and sunk.
    for name, co, no, piece in CRACKS:
        new = wk.split_piece(objects[name], co, no, burnt, piece)
        assert new is not None and objects[name].data.polygons, "crack %s misses %s" % (piece, name)
        objects[piece] = new
    for name, pivot, axis, degrees, sink in TILTS:
        wk.turn([objects[name]], pivot, axis, degrees)
        objects[name].data.transform(Matrix.Translation((0, 0, -sink)))
    for name, shade in SHADES.items():
        obj = objects[name]
        if name not in ("upright", "upright_top", "cap", "arm_mid"):
            middle = sum((v.co for v in obj.data.vertices), Vector()) / len(obj.data.vertices)
            out = Vector((middle.x - live.DISC_CENTRE[0], middle.y - live.DISC_CENTRE[1], 0.0)).normalized()
            obj.data.transform(Matrix.Translation(out * PUSH))
        if shade != "lit":
            for i, m in enumerate(obj.data.materials):
                if m.name != burnt.name:
                    obj.data.materials[i] = sooted if shade == "soot" else burnt
    pivot, axis, degrees, sink = TOP_HALF
    top_half = [objects["upright_top"], objects["cap"], objects["bezel0"], objects["gem0"]]
    wk.turn(top_half, pivot, axis, degrees)
    for obj in top_half:   # (lowered, and pushed up the screen: a dark crack opens between the gems)
        obj.data.transform(Matrix.Translation((0.15, 0.6, -sink)))
    # The gems: the top one dark, the bottom one dim, its light nearly out (still at the live gems' height).
    objects["gem0"].data.materials[0] = gem_dark
    objects["gem1"].data.materials[0] = gem_ember
    for obj in objects.values():
        k.smooth(obj, 40)
    # Soot burnt in rays over the disc's top, and over the plates' broken faces' edges.
    disc = objects["disc"]
    wk.paint_field(disc, soot_field, [(-9.0, disc_mat), (0.05, soot), (0.55, joint)], only=lambda p: p.normal.z > 0.9)
    # Rubble where the blasts were and at the disc's foot.
    for j, (x, y, z, r, seed, grey) in enumerate(RUBBLE):
        lump = wk.rock(f"rubble{j}", (x, y, z), (r, r * 0.85, r * 0.6), stone if grey else burnt, seed, 1, 0.3)
        mk.apply(lump)
    wk.clip_below(mk.meshes())
    wk.finish("panel_gems_wreck", options, LIVE_TOP)


if __name__ == "__main__":
    build()
