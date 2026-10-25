"""TYRIAN's golden domes machine's wreck (sheet 2 sprites 77 79 above 115 117's stand-ins: what TYRIAN's map paints
where gold_domes stands once it is destroyed, before it comes and where none comes; 6 of each piece), built on
polish_gold_machines.py (2026-10-25, the clean ground's stage 4).

As the map paints it at 4x (TYRIAN 9d895f5c53c668ad at 492 and 516, 7211 and 7239): the machine in its place, its dark
steel housing whole but sooted black over its keel and round the domes, the domes burst: the big dome's top blown out,
its gold left as a thick broken rim round a black hollow (columns 6-31 of rows 1-22), dark steel ribs standing in the
hollow (columns 15-24 of rows 6-15) and a bent gold bar of the arch plate lying in it at its left (a "Γ", columns
11-16 of rows 9-17); the side domes torn into gold claws opening towards the keel, their clamps still on them (the
blue-grey bars, columns 6-10 and 28-32 of rows 30-36); the bottom dome burst into a gold hook (an "S" at columns 13-25
of rows 35-45) round a black hole, its port gone.

Built as the live machine (polish_gold_machines' housing, shoulders, keel, blocks, the three kinds of domes with their
gold bands, the arch plate, the slots, the pipes and the clamps, its materials), broken: each dome cut by a lumpy exact
boolean (wreck kit rocks: the big dome's top and inside down to a black bowl, the side domes' parts towards the keel,
the bottom dome's right and middle), the cuts' faces the hole's black-brown 0x10; the arch plate, the port's rim and
the pipes gone, a bent gold bar lying in the big dome's hollow, four dark steel ribs standing in it, the side domes'
gold torn up into claws where the pipes ran into them; the gold scorched three
shades darker along the breaks, the steel blackened (three shades darker all over, the hole's black-brown 0x10 in
patches round the domes and down the keel). Cut along
the sprites' edges as the live machine (polish_savara_boss.cut, the cuts capped dark steel), each piece moved to its
sprite's centre and joined.

Coordinates as polish_gold_machines.py's (the whole's origin the picture's centre; P(c, r) a pixel edge). models.cfg:
model gold_domes_tl_wreck enemies/gold_domes_tl_wreck.glb origin (and _tr_, _bl_, _br_); wreck 2 77 gold_domes_tl_wreck,
wreck 2 79 gold_domes_tr_wreck, wreck 2 115 gold_domes_bl_wreck, wreck 2 117 gold_domes_br_wreck (drawn with the live
sprite lines' options, yaw=0 height=-4, at the live pieces' places).

Options after "--": --outdir <dir> (default assets/models/enemies), --preview <prefix>, --only <model,...>.
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
import polish_gold_machines as live  # noqa: E402
import polish_panel_pills_wreck as wk  # noqa: E402
from polish_deli_boss import join  # noqa: E402
from polish_jaw_gun_wreck import bent_bar, scorch, shard  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_savara_boss import cut  # noqa: E402

P, X, Y = live.P, live.X, live.Y
# The breaks: (the dome, the cutter's middle (pixel edges and height), its radii, seed). The big dome's takes its top
# and its inside down to a bowl (its floor at about 3.4, over the housing); the side domes' their parts towards the
# keel; the bottom dome's its right and its middle.
BREAKS = [("big_dome", (19.2, 11.2, 9.6), (11.4, 9.4, 6.2), 3.0),
          ("side_dome0", (12.8, 29.4, 6.2), (5.4, 4.6, 3.8), 5.0),
          ("side_dome1", (26.2, 29.4, 6.2), (5.4, 4.6, 3.8), 6.0),
          ("bottom_dome", (22.0, 39.4, 5.4), (4.6, 3.8, 3.4), 7.0)]
# The ribs standing in the big dome's hollow: (column, from row, to row), their half width, their top.
RIBS = [(15.5, 7.2, 15.6), (18.0, 6.4, 16.4), (20.5, 6.4, 16.4), (23.0, 7.2, 15.6)]
RIB_HALF, RIB_TOP = 0.45, 6.4
RIB_FOOT = 3.2
# The bent gold bar of the arch plate lying in the hollow: (column, row, height) along it, its radius.
BAR = [(14.4, 16.4, 4.4), (14.6, 13.0, 5.4), (14.9, 9.8, 6.0), (16.8, 9.2, 5.8), (18.8, 9.6, 5.2)]
BAR_R = 0.8
# The side domes' gold torn up into claws where the pipes ran into them (the pipes gone): the left dome's (outline in
# the whole's plan, z, tilt about x and y); the right dome's are their mirror images about x = AXIS_X.
CLAWS = [([(-20.2, -3.4), (-17.6, -3.0), (-19.6, 3.6)], 4.2, (40.0, -14.0)),
         ([(-17.4, -2.4), (-14.6, -2.4), (-15.8, 5.2)], 4.8, (46.0, 0.0)),
         ([(-14.0, -3.0), (-11.4, -3.6), (-10.8, 2.6)], 4.6, (34.0, 18.0)),
         ([(-21.4, -6.6), (-19.6, -4.8), (-23.4, -2.8)], 3.6, (20.0, -30.0))]
AXIS_X = -4.5
# The scorch: the gold along its breaks; the steel round the domes and down the keel.
SOOT = [(Vector((X(19.0), Y(14.0), 3.0)), 9.0), (Vector((X(19.5), Y(32.0), 3.0)), 6.0),
        (Vector((X(19.5), Y(40.0), 3.0)), 5.0)]


def gold_burn(co):
    v = 0.25 + 0.3 * wk.perlin(co.x * 0.5 + 2.0, co.y * 0.5, co.z * 0.5)
    for name, (c, r, z), radii, _ in BREAKS:
        x, y = P(c, r)
        d = math.sqrt(((co.x - x) / radii[0]) ** 2 + ((co.y - y) / radii[1]) ** 2 + ((co.z - z) / radii[2]) ** 2)
        v += 0.75 * math.exp(-((d - 1.0) / 0.25) ** 2)
    return v


def steel_burn(co):
    v = 0.62 + 0.3 * wk.perlin(co.x * 0.4 - 1.0, co.y * 0.4 + 3.0, 0.7)
    for centre, reach in SOOT:
        v += 0.7 * math.exp(-((co - centre).length / reach) ** 2)
    return v


def wreck_whole(m):
    parts = live.domes_housing(m) + live.big_dome(m) + live.side_domes(m) + live.bottom_dome(m)
    for obj in parts:
        mk.apply(obj)
    objects = {o.name: o for o in parts}
    # The arch plate and the port's rim go with the breaks.
    for name in ("arch_bar", "arch_leg0", "arch_leg1", "port_rim", "pipe-1", "pipe1"):
        obj = objects.pop(name)
        data = obj.data
        bpy.data.objects.remove(obj)
        bpy.data.meshes.remove(data)
    # The domes burst.
    for name, (c, r, z), radii, seed in BREAKS:
        x, y = P(c, r)
        wk.break_away(objects[name], wk.rock(name + "_break", (x, y, z), radii, m["hole"], seed, subdivisions=3,
                                             rough=0.22))
        k.smooth(objects[name], 50)
    # The ribs in the big dome's hollow and the bent bar lying in it.
    for i, (c, r0, r1) in enumerate(RIBS):
        rib = mk.box(f"rib{i}", X(c) - RIB_HALF, X(c) + RIB_HALF, Y(r1), Y(r0), RIB_FOOT, RIB_TOP, m["steel_shade"])
        mk.bevel(rib, 0.15, 1, 35)
        mk.paint(rib, lambda cc, n: m["steel_lit"] if n.z > 0.7 else m["steel_edge"] if n.dot(live.LIGHT) > 0.6
                 else None)
        mk.shade(rib, 35)
    for side in (-1, 1):
        for i, (outline, z, (tx, ty)) in enumerate(CLAWS):
            pts = outline if side < 0 else [(2 * AXIS_X - x, y) for x, y in outline]
            claw = shard(f"claw{side}_{i}", pts, z, 0.45, m["gold"], (tx, ty * side))
            mk.paint(claw, live.gold_pick(m))
    pts = [(X(c), Y(r), z) for c, r, z in BAR]
    bar = bent_bar("arch_fallen", pts, BAR_R, m["gold_lit"])
    live.gold_bands(bar, m)
    whole = mk.meshes()
    for obj in whole:
        mk.apply(obj)
        if obj.name.startswith(("rib", "clamp")):
            continue
        gold = any(mt.name.startswith("goldm_gold") for mt in obj.data.materials)
        scorch(obj, gold_burn if gold else steel_burn, levels=(0.62, 1.0) if gold else (0.55, 0.95))
        k.smooth(obj, 50 if gold else 35)
        # (at most 15 materials a model: the soot is the hole's black-brown)
        for i, mt in enumerate(obj.data.materials):
            if mt.name == "soot@16":
                obj.data.materials[i] = m["hole"]
    bpy.context.view_layer.update()
    return whole


def build():
    options = k.args()
    out = mk.outdir(options)
    only = set(options["only"].split(",")) if "only" in options else None
    k.reset()
    bpy.context.scene.view_settings.view_transform = "Standard"
    m = live.materials()
    whole = wreck_whole(m)
    triangulate(whole)
    print("whole gold domes wreck: %d triangles, %d objects" % (mk.triangles(whole), len(whole)))
    if "preview" in options:
        mk.preview(options["preview"] + "gold_domes_wreck_whole", whole, size=(48, 56), scale=8, distance=1.8)
    for suffix, box, _ in live.QUARTERS:
        model = f"gold_domes_{suffix}_wreck"
        if only and model not in only:
            continue
        parts = [p for p in (cut(src, box, m["steel_dark"]) for src in whole) if p is not None]
        mk.transform(parts, Matrix.Translation((-(box[0] + box[1]) / 2, -(box[2] + box[3]) / 2, 0.0)))
        triangulate(parts)
        piece = join(parts, model)
        wk.drop_unused([piece])
        bpy.context.view_layer.update()
        for src in whole:
            src.hide_render = True
        mk.report(model, [piece], os.path.join(out, model + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + model, [piece])
        bpy.data.objects.remove(piece)
        for src in whole:
            src.hide_render = False


if __name__ == "__main__":
    build()
