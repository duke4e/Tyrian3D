"""What is left of the drilling rig's block house once the rig is destroyed (sheet P sprites 1 and 3 above 39 and 41:
their stand-ins, what ASTEROID1 and AST ROCK paint under the house once the rig is shot, before it comes and where none
comes; 7 of them), stage 4 of the clean ground (2026-10-25), built on polish_asteroid_rig.py. The crane's own wreck (P
47 49: asteroid_rig_wreck_crane_l / _r, the game's dead look) stands over it as before; these are the house's four
pieces. models.cfg: model asteroid_rig_tl_wreck / _tr_wreck / _bl_wreck / _br_wreck enemies/asteroid_rig_*_wreck.glb
origin; wreck p 1 asteroid_rig_tl_wreck, wreck p 3 asteroid_rig_tr_wreck, wreck p 39 asteroid_rig_bl_wreck, wreck p 41
asteroid_rig_br_wreck (drawn with the live sprite lines' options, yaw=0 height=-4).

As the maps paint it at 4x (ASTEROID1's tiles 429 430 above 439 440; ASTEROID1 6996cad08e04cb84 at 552, 3025; columns
and rows of the 48 x 84 picture, the house's rows 28-80): the house burnt: its roof's left part grey still (columns
0-14 of rows 28-52), its right half and the middle of its front black (0x01, 0x02), its front's ribs dark grey; red-hot
fissures (ramp 7, 0x70-0x75) down its right side (columns 38-44 of rows 34-68) and down the front under the collar
(columns 19-24 of rows 52-68), short ones at the left (columns 4-7 of rows 36-37 and 54-58); the gold collar round the
bore and the four anchors standing, still lit; the stays black, the left ones standing, the inner right one (broken
off under the hub in the crane's wreck) lying on the roof from its anchor up towards the hub.

The model: polish_asteroid_rig.py's rig in its first frame, with the crane's damage (its wreck(): the inner right stay
broken off under the hub, the outer right one broken through, so these pieces meet the crane's wreck), then broken
further: the inner right stay's lower part fallen onto the roof (a charred pipe from its anchor up the roof); the house
scorched by a field (strong over its right half and the middle of its front, torn by noise) into its own darker greys
and black (polish_bronze_pump_wreck.scorch_map: no new materials), the anchors, the clamps, the collar and the drill
string a shade darker; the fissures glowing strips laid into the surfaces where the camera sees them (0x74 at 0.42,
0x76 at 0.3 at their middles: under the bloom's white), a few embers in them. Cut along the planes the camera sees as
the sprites' edges as the live rig (polish_stone_face.view_cut), only the house's four pieces exported.

Coordinates as polish_asteroid_rig.py's: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the floor (the
roof at 10); the whole's origin is the corner where the four house sprites meet; E(c, r) the picture's pixel corner,
at(c, r, z) the point at height z the camera shows there.

Options after "--": --outdir <dir> (default assets/models/enemies), --preview <prefix>, --only <name,...>.
"""
import math
import os
import random
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
import polish_asteroid_rig as live  # noqa: E402
from polish_panel_pills_wreck import fbm  # noqa: E402
from polish_pyramid_wreck import chunk, emissive  # noqa: E402
from polish_bronze_pump_wreck import scorch_map  # noqa: E402

E, at, H, TILT = live.E, live.at, live.H, live.TILT
SEED = 39
SPECS = [(name + "_wreck", sprite, box, centre) for name, sprite, box, centre in live.PIECES[2:]]
# The fissures as the camera sees them: (column, row) along each, its half-width.
FISSURES = [([(38.6, 34.2), (38.4, 37.0), (38.8, 40.2)], 0.65), ([(39.4, 47.6), (39.8, 50.0), (39.4, 52.4)], 0.6),
            ([(40.4, 52.6), (40.6, 55.2), (40.2, 58.4)], 0.7), ([(43.0, 53.0), (43.4, 55.6), (43.2, 58.2)], 0.65),
            ([(38.6, 62.0), (38.8, 65.0), (38.6, 68.4)], 0.6),
            ([(20.6, 52.4), (21.2, 55.6), (20.4, 59.0), (20.8, 62.6), (20.2, 66.4)], 0.7),
            ([(22.6, 56.6), (23.4, 59.2), (23.0, 61.4)], 0.5), ([(24.6, 57.0), (24.8, 60.6)], 0.5),
            ([(27.8, 52.4), (28.2, 55.4), (27.8, 58.0)], 0.5), ([(4.6, 36.2), (6.2, 37.0)], 0.45),
            ([(6.8, 54.2), (7.2, 56.4), (6.8, 58.2)], 0.5)]
EMBERS = [(20.8, 57.4), (39.6, 56.0), (42.8, 55.0), (38.6, 38.0), (21.0, 64.0)]
# The fallen stay: from its anchor (br) up the roof to its broken end (as drawn: column, row), its height over the roof.
FALLEN = [(33.0, 58.6), (31.6, 52.0), (30.0, 45.0), (28.8, 38.6), (27.6, 33.4)]


def materials():
    m = live.materials()
    # (the wells' black dull, so the charred roof reads black from the camera, not the sky's grey)
    bsdf = m["well"].node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Metallic"].default_value = 0.1
    bsdf.inputs["Roughness"].default_value = 0.9
    m["fissure"] = emissive("rigwreck_fissure", 0x74, 0.42)
    m["ember"] = emissive("rigwreck_ember", 0x76, 0.3)
    return m


def remap(m):
    """The scorch's steps: the house's greys into its darker ones and its wells' black; the gold and steel a shade."""
    steps = {"roof": ("groove", "well"), "lit": ("shade", "seam"), "shade": ("seam", "well"),
             "groove": ("well", "well"), "wall": ("seam", "well"), "glacis": ("well", "well"), "seam": ("well", "well"),
             "conduit": ("seam", "well"), "gold_lit": ("gold", "gold_dark"), "gold": ("gold_dark", "gold_dark"),
             "steel_lit": ("steel", "well"), "steel": ("well", "well")}
    return {m[key].name: tuple(m[x] for x in s) for key, s in steps.items()}


def burn(co):
    """Strong over the house's right half and the middle of its front, torn by noise; the roof's left part clean."""
    right = max(0.0, min(1.0, (co.x + 12.0) / 10.0))
    front = max(0.0, min(1.0, (E(0, 50.0)[1] - co.y) / 6.0)) * math.exp(-((co.x + 1.5) / 11.0) ** 2)
    left_front = 0.6 * max(0.0, min(1.0, (E(0, 54.0)[1] - co.y) / 8.0))
    return 0.95 * max(right, front, left_front) + 0.3 * fbm(co.x * 0.3 + 2.0, co.y * 0.3 - 4.0, co.z * 0.2, 3)


def metal_burn(co):
    return 0.3 + 0.3 * fbm(co.x * 0.4, co.y * 0.4 + 3.0, co.z * 0.4, 2)


def view_hit(trees, c, r):
    """The surface point the camera sees at the picture's point (c, r) (a ray along its line of sight)."""
    x, yv = E(c, r)
    z0 = 140.0
    origin = Vector((x, yv - (z0 - H) * TILT, z0))
    d = Vector((0.0, TILT, -1.0)).normalized()
    best = None
    for tree in trees:
        hit = tree.ray_cast(origin, d)
        if hit[0] is not None and (best is None or hit[3] < best[1]):
            best = (hit[0], hit[3])
    return best[0] if best else None


def fissures(parts, m):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    trees = [BVHTree.FromObject(o, depsgraph) for o in parts]
    for i, (line, w) in enumerate(FISSURES):
        dense = []
        for (c0, r0), (c1, r1) in zip(line, line[1:]):
            n = max(2, int(math.hypot(c1 - c0, r1 - r0) / 0.5))
            dense += [(c0 + (c1 - c0) * j / n, r0 + (r1 - r0) * j / n) for j in range(n)]
        dense.append(line[-1])
        pts, radii = [], []
        w *= 1.4
        for j, (c, r) in enumerate(dense):
            p = view_hit(trees, c, r)
            if p is None:
                continue
            t = j / max(1, len(dense) - 1)
            pts.append(p + Vector((0.0, 0.0, -0.5 * w)))
            radii.append(w * (0.5 + 0.5 * math.sin(math.pi * t)))
        if len(pts) >= 2:
            k.smooth(mk.tube(f"fissure{i}", pts, w, m["fissure"], 6, radii=radii), 50)
    rng = random.Random(SEED)
    for i, (c, r) in enumerate(EMBERS):
        p = view_hit(trees, c, r)
        if p is not None:
            chunk(f"ember{i}", (p.x, p.y, p.z - 0.2), rng.uniform(0.8, 1.2), rng, m["ember"], 0.55, 9)


def fallen_stay(m):
    """The inner right stay's lower part, fallen onto the roof from its anchor (a charred pipe)."""
    top = live.SLAB_TOP + live.STAY_R - 0.25
    sock = live.socket("br")
    pts = [sock + Vector((0.0, 0.0, 0.2))]
    for c, r in FALLEN[1:]:
        p = at(c, r, top)
        pts.append(Vector((p.x, p.y, top)))
    dense = mk.chaikin([tuple(p) for p in pts], 2, closed=False)
    pipe = mk.tube("stay_fallen", dense, live.STAY_R, m["steel"], 10)
    k.smooth(pipe, 60)
    mk.paint(pipe, lambda c, n: m["well"] if n.dot(live.LIGHT) < 0.4 else None)
    return pipe


def build_whole():
    m = materials()
    whole = live.wreck(live.build_whole(m, live.FRAMES[0][2]), m)
    by_name = {o.name: o for o in whole}
    for name in ("stay_mr", "clamp_mr", "clamp_mr_arm", "clamp_mr_ear"):    # (gone with its upper part)
        obj = by_name.get(name)
        if obj is not None:
            bpy.data.objects.remove(obj)
    fallen_stay(m)
    steps = remap(m)
    for obj in [o for o in mk.meshes() if len(o.data.polygons) > 0]:
        mk.apply(obj)
        if obj.name.startswith(("house", "slab", "hatch", "rib", "bolt", "hinge", "conduit", "clamp")):
            step = 3.6 if obj.name.startswith("house") else 2.6 if obj.name.startswith(("slab", "hatch")) else None
            scorch_map(obj, burn, steps, levels=(0.35, 0.72), step=step)
        elif obj.name.startswith(("anchor", "collar", "stay", "drill")):
            scorch_map(obj, metal_burn, steps, levels=(0.3, 0.9), split=False)
    bpy.context.view_layer.update()
    fissures([o for o in mk.meshes() if len(o.data.polygons) > 0], m)
    whole = [o for o in mk.meshes() if len(o.data.polygons) > 0]
    for obj in whole:
        mk.apply(obj)
    live.triangulate(whole)
    bpy.context.view_layer.update()
    return whole, m


def build():
    options = k.args()
    k.reset()
    whole, m = build_whole()
    print("whole rig wreck: %d triangles" % mk.triangles(whole))
    if "preview" in options:
        mk.preview(options["preview"] + "asteroid_rig_house_wreck_whole", whole, size=(48, 84), scale=8, distance=2.4,
                   centre=(0.0, 14.0))
    live.pieces(whole, SPECS, m, options, None)


if __name__ == "__main__":
    build()
