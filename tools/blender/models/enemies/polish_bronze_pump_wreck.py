"""What is left of the bronze pump on its block house once it is destroyed (sheet P sprites 229 and 231 above 267 and
269: their stand-ins, what the asteroid maps paint where the pump stands, before it comes, once it is shot and where
none comes; 17 of them in ASTEROID1, ASTEROID?, ASTCITY, AST. CITY and ASTEROID2), stage 4 of the clean ground
(2026-10-25), built on polish_bronze_pump.py. models.cfg: model bronze_pump_tl_wreck / _tr_wreck / _bl_wreck /
_br_wreck enemies/bronze_pump_*_wreck.glb origin; wreck p 229 bronze_pump_tl_wreck, wreck p 231 bronze_pump_tr_wreck,
wreck p 267 bronze_pump_bl_wreck, wreck p 269 bronze_pump_br_wreck (drawn with the live sprite lines' options, yaw=0
height=-4). The dome's own wreck (P 121, pump_dome_wreck) stands on the shaft as before.

As the maps paint it at 4x (the same on every map; ASTEROID1 14a0d01cd2b01f4c at 576, 5013; columns and rows of the 48 x
84 picture, the house's rows 28-80): the house's front right blown away into a black void (0x00, 0x01: columns 20-47 of
rows 58-80, and its right side, columns 40-47 of rows 35-64), its left part and the roof's back standing grey; the
pump on it scorched, its bronze dark (0xa1-0xa7 where it was 0xa3-0xae, the gold gone brown), the shaft charred nearly
black (0x01, 0x40, 0xa1-0xa6); red-hot gashes (ramp 7, 0x70-0x75) in the tower's front (columns 28-33 of rows 41-45),
the arm's middle (columns 20-25 of rows 56-59), the arm's end block (columns 33-37 of rows 54-58) and down the leg
(columns 12-16 of rows 61-72).

The model: polish_bronze_pump.py's house and cross and shaft (its build_whole(); the dome is its own model), then
broken: the house's front right cut away (an exact boolean with a jagged L-shaped prism from FLOOR up, the house's
parts and the arm's end block and lobe that reach into it cut, those wholly in it gone; the hole's floor and walls
charred, 0x02 and 0x03), broken concrete and torn slabs lying in it (polish_pyramid_wreck.chunk,
polish_block_house_wreck.curled_plate), a few embers at its rim; the pump's gold repainted in its bronze and every
bronze part scorched by noise fields along their contours (polish_jaw_gun_wreck.scorch: three shades darker, the
brown-black 0x10 in patches; the shaft nearly all), the house sooted round the hole; the gashes glowing strips laid
into the surfaces where the camera sees them (ramp 7: 0x74 at 0.42, 0x76 at 0.3; under the bloom's white). Cut along
the sprites' edges as the live pump (polish_savara_boss.cut, the caps in each part's inside colour).

Coordinates as polish_bronze_pump.py's: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the floor; the
whole's origin is the corner where the four pump sprites meet; E(c, r) is the picture's pixel corner, at(c, r, z) the
point at height z the camera shows there.

Options after "--": --outdir <dir> (default assets/models/enemies), --preview <prefix>, --only <name,...>.
"""
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
import polish_bronze_pump as live  # noqa: E402
from polish_panel_pills_wreck import fbm  # noqa: E402
from polish_jaw_gun_wreck import ccw, grid_cut, inside, jagged  # noqa: E402
from polish_coral_manta import split_contour  # noqa: E402
from polish_pyramid_wreck import break_with, chunk, emissive  # noqa: E402
from polish_block_house_wreck import curled_plate  # noqa: E402

E, at, H, TILT = live.E, live.at, live.H, live.TILT
SEED = 229
PIECES = [(name + "_wreck", box) for name, _, box in live.PIECES]
FLOOR = 0.6                    # the hole's floor
# The hole (the picture's corners, before roughening): the house's front right and its right side, out past its walls.
HOLE = [(40.2, 34.6), (44.0, 34.0), (48.6, 33.4), (48.6, 82.0), (20.4, 82.0), (20.4, 64.0), (21.2, 60.2),
        (24.6, 58.6), (28.6, 59.4), (32.4, 58.2), (36.4, 59.0), (39.0, 57.2), (39.6, 52.0), (40.8, 47.0),
        (39.8, 41.0), (40.6, 37.6)]
# The red-hot gashes as the camera sees them: (columns, rows) along each, its half-width, its glow (rim, core).
GASHES = [([(28.4, 41.2), (30.0, 42.4), (31.4, 43.4), (32.8, 44.8)], 1.15),
          ([(29.4, 44.6), (31.2, 45.0)], 0.8),
          ([(20.6, 56.6), (22.4, 57.2), (24.6, 58.0)], 0.95),
          ([(33.6, 54.8), (35.2, 55.8), (36.8, 56.4)], 1.0),
          ([(13.2, 61.4), (14.0, 63.6), (13.6, 66.0)], 1.0), ([(14.2, 67.8), (14.6, 69.6), (14.0, 71.4)], 0.95),
          ([(15.6, 64.2), (16.2, 65.8)], 0.6), ([(13.4, 40.2), (14.2, 41.2)], 0.55)]
# Broken concrete in the hole: how many lumps; torn slabs lying in it ((column, row), heading, length, width).
CONCRETE = 16
PLATES = [((26.0, 66.0), 20.0, 5.0, 3.0), ((44.0, 48.0), 100.0, 5.0, 3.0)]
EMBERS = [(22.4, 61.0), (30.6, 61.4), (41.6, 40.0), (37.6, 60.6), (25.6, 70.4), (43.2, 56.0)]


def hole_outline():
    return ccw(jagged([E(c, r) for c, r in HOLE], 2.9, 0.55, 1.1))


def in_hole(x, y, outline):
    return inside((x, y), outline)


def hole_distance(x, y, outline):
    """How far (x, y) lies from the hole's outline (in plan), negative inside it."""
    p = Vector((x, y))
    best = 1e9
    for a, b in zip(outline, outline[1:] + outline[:1]):
        a, b = Vector(a), Vector(b)
        ab = b - a
        t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-9)))
        best = min(best, (p - (a + ab * t)).length)
    return -best if inside((x, y), outline) else best


# How the scorch darkens each material, one step and two (no new materials: the house's greys, the pump's bronze, the
# hole's black): (material key, its burnt key, its charred key).
BURNT = {"roof": ("shade", "seam"), "lit": ("roof", "shade"), "shade": ("groove", "well"), "groove": ("seam", "well"),
         "wall": ("seam", "well"), "glacis": ("well", "well"), "seam": ("well", "well"), "well": ("well", "well"),
         "conduit": ("shade", "seam"), "bz_lit": ("bz", "char"), "bz": ("bz_dark", "char"),
         "bz_dark": ("bz_deep", "char"), "bz_deep": ("bz_deep", "char")}


def materials():
    m = live.materials()
    m["char"] = k.material("soot", palette=0x10, metallic=0.2, roughness=0.8)
    m["fissure"] = emissive("pumpwreck_fissure", 0x74, 0.42)
    m["ember"] = emissive("pumpwreck_ember", 0x76, 0.3)
    return m


PUMP_PARTS = ("arm", "lobe", "tower", "cabinet", "leg", "shaft")
GOLD_TO_BRONZE = {"gold": "bz", "gold_lit": "bz", "gold_dark": "bz_dark", "lamp": "bz_deep"}


def regild(obj, m):
    """The pump's gold (and the shaft's lamp) repainted in its bronze, the hatches' hinges in the house's shade: the
    painting shows them all brown (and fewer materials)."""
    names = {m[g].name: m[b] for g, b in GOLD_TO_BRONZE.items()}
    names[m["conduit"].name] = m["shade"]
    for i, mat in enumerate(obj.data.materials):
        if mat is not None and mat.name in names:
            obj.data.materials[i] = names[mat.name]


def scorch_map(obj, field, remap, levels=(0.25, 0.62), step=None, split=True):
    """polish_jaw_gun_wreck.scorch() with fixed steps (no new materials): faces cut along a grid (step) and the field's
    contours at the levels, each face's material burnt one step per level the field passes over it (remap: material
    name -> (burnt material, charred material); materials not in it stay; split False: whole faces, uncut). Also for
    the other wreck scripts of this batch (polish_ice_globe_wreck.py, polish_asteroid_rig_wreck.py)."""
    if step:
        grid_cut(obj, step)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    vals = {"f": {v: field(v.co) for v in bm.verts}}
    if split:
        for t in levels:
            split_contour(bm, vals, "f", t)
    mats = list(obj.data.materials)
    slots = {}
    for f in bm.faces:
        value = sum(vals["f"][v] for v in f.verts) / len(f.verts)
        level = sum(1 for t in levels if value > t + 1e-6)
        src = mats[f.material_index] if f.material_index < len(mats) else None
        steps = remap.get(src.name) if src is not None else None
        if level == 0 or steps is None:
            continue
        new = steps[min(level, len(steps)) - 1]
        if new.name not in slots:
            slots[new.name] = mk.slot_of(obj, new)
        f.material_index = slots[new.name]
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    return obj


def scorch(obj, field, m, levels=(0.25, 0.62), step=None):
    """scorch_map() with the house's and the pump's steps (BURNT)."""
    remap = {m[key].name: (m[a], m[b]) for key, (a, b) in BURNT.items()}
    return scorch_map(obj, field, remap, levels, step)


def burn_pump(name):
    if name.startswith("shaft"):
        return lambda co: 0.6 + 0.3 * fbm(co.x * 0.4 + 3.0, co.y * 0.4, co.z * 0.4, 2)
    return lambda co: 0.34 + 0.32 * fbm(co.x * 0.3 + 11.0, co.y * 0.3 - 2.0, co.z * 0.3, 3)


def break_house(whole, m, outline):
    """The house's parts (and the pump's that reach into the hole) cut by the hole; those wholly in it gone."""
    cutter_outline = outline
    xs, ys = [p[0] for p in outline], [p[1] for p in outline]
    hx0, hx1, hy0, hy1 = min(xs), max(xs), min(ys), max(ys)
    kept, straddling = [], []
    for obj in whole:
        corners = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
        inner = [in_hole(c.x, c.y, outline) for c in corners]
        outside = (max(c.x for c in corners) < hx0 or min(c.x for c in corners) > hx1 or
                   max(c.y for c in corners) < hy0 or min(c.y for c in corners) > hy1)
        if all(inner) and min(c.z for c in corners) > FLOOR and not obj.name.startswith(("house", "shaft")):
            bpy.data.objects.remove(obj)
        elif outside:
            kept.append(obj)
        else:
            straddling.append(obj)
    cutter = mk.prism("hole", cutter_outline, FLOOR, 60.0, m["well"])
    broken = break_with(straddling, cutter)
    for obj in broken:
        well = mk.slot_of(obj, m["well"])
        char = mk.slot_of(obj, m["char"])
        for poly in obj.data.polygons:
            if poly.material_index == well and poly.normal.z > 0.7 and poly.center.z < FLOOR + 0.05:
                poly.material_index = char     # (the hole's floor: burnt black)
        mk.shade(obj, 35)
    return kept + broken


def view_hit(trees, c, r):
    """The surface point the camera sees at the picture's point (c, r) (a ray along its line of sight), or None."""
    x, yv = c - 24.0, 56.0 - r
    z0 = 140.0
    origin = Vector((x, yv - (z0 - H) * TILT, z0))
    d = Vector((0.0, TILT, -1.0)).normalized()
    best = None
    for tree in trees:
        hit = tree.ray_cast(origin, d)
        if hit[0] is not None and (best is None or hit[3] < best[1]):
            best = (hit[0], hit[3])
    return best[0] if best else None


def gashes(parts, m):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    trees = [BVHTree.FromObject(o, depsgraph) for o in parts]
    made = []
    for i, (line, w) in enumerate(GASHES):
        dense = []
        for (c0, r0), (c1, r1) in zip(line, line[1:]):
            n = max(2, int(math.hypot(c1 - c0, r1 - r0) / 0.5))
            dense += [(c0 + (c1 - c0) * j / n, r0 + (r1 - r0) * j / n) for j in range(n)]
        dense.append(line[-1])
        pts, radii = [], []
        for j, (c, r) in enumerate(dense):
            p = view_hit(trees, c, r)
            if p is None:
                continue
            t = j / max(1, len(dense) - 1)
            pts.append(p + Vector((0.0, 0.0, -0.12)))
            radii.append(w * (0.55 + 0.45 * math.sin(math.pi * t)))
        if len(pts) < 2:
            continue
        rim = mk.tube(f"gash{i}", pts, w, m["fissure"], 8, radii=radii)
        k.smooth(rim, 50)
        made.append(rim)
    return made


def debris(parts, m, outline):
    rng = random.Random(SEED)
    hit = mk.surface(parts)

    def rest_on(x, y):
        h = hit(x, y)
        return h[0].z if h else FLOOR
    made = []
    xs, ys = [p[0] for p in outline], [p[1] for p in outline]
    n = 0
    tries = 0
    while n < CONCRETE and tries < 400:
        tries += 1
        x, y = rng.uniform(min(xs), max(xs)), rng.uniform(min(ys), max(ys))
        if hole_distance(x, y, outline) > -0.8 or x > live.bh.X1 - 0.5 or y < live.bh.Y_FOOT + 0.5:
            continue
        mat = (m["seam"], m["well"], m["glacis"], m["seam"], m["char"], m["well"])[n % 6]
        made.append(chunk(f"concrete{n}", (x, y, rest_on(x, y) - 0.2), rng.uniform(1.0, 2.4), rng, mat,
                          rng.uniform(0.45, 0.8)))
        n += 1
    for i, ((c, r), heading, length, width) in enumerate(PLATES):
        made.append(curled_plate(f"torn{i}", E(c, r), heading, rng.uniform(-20, 20), length, width, 0.5,
                                 length * 0.5, rng.uniform(2.2, 3.4), rng.uniform(30, 70),
                                 (m["groove"], m["seam"])[i % 2], m["well"], rest_on, 0.3))
    for i, (c, r) in enumerate(EMBERS):
        x, y = E(c, r)
        made.append(chunk(f"ember{i}", (x, y, rest_on(x, y) - 0.15), rng.uniform(0.6, 1.0), rng, m["ember"], 0.6,
                          9))
    return made


def build_whole():
    m = materials()
    whole, dome, raw, _ = live.build_whole(0)
    for obj in dome + raw:
        data = obj.data
        bpy.data.objects.remove(obj)
        if data.users == 0:
            bpy.data.meshes.remove(data)
    # (build_whole made its own materials: the same names, so the same materials as m's)
    outline = hole_outline()
    parts = break_house(whole, m, outline)
    for obj in parts:
        if obj.name.startswith(PUMP_PARTS):
            regild(obj, m)
            scorch(obj, burn_pump(obj.name), m, levels=(0.25, 0.62), step=1.8)
            mk.shade(obj, 35)
        else:
            def soot(co, outline=outline):
                d = hole_distance(co.x, co.y, outline)
                return 0.9 * math.exp(-max(d, 0.0) / 2.2) + 0.25 * fbm(co.x * 0.4, co.y * 0.4 + 5.0, 0.3, 2) - 0.2
            regild(obj, m)
            scorch(obj, soot, m, levels=(0.35, 0.8), step=2.2 if obj.name.startswith("house") else None)
            mk.shade(obj, 35)
    bpy.context.view_layer.update()
    gashes(parts, m)
    debris(parts, m, outline)
    whole = [o for o in mk.meshes() if len(o.data.polygons) > 0]
    for obj in whole:
        mk.apply(obj)
    bpy.context.view_layer.update()
    return whole, m


def cap_of(obj, m):
    """The cuts' caps: the debris in their own colours, the rest as the live pump's."""
    if obj.name.startswith(("concrete", "torn")):
        return m["seam"]
    if obj.name.startswith(("gash", "ember")):
        return m["fissure"]
    return live.cap_of(obj, m)


def build():
    options = k.args()
    only = options["only"].split(",") if "only" in options else None
    k.reset()
    whole, m = build_whole()
    live.triangulate(whole)
    print("whole bronze pump wreck: %d triangles" % mk.triangles(whole))
    if "preview" in options:
        mk.preview(options["preview"] + "bronze_pump_wreck_whole", whole, size=(48, 84), scale=8, distance=2.4,
                   centre=(0.0, 14.0))
    for name, box in PIECES:
        if only and name not in only:
            continue
        parts = [p for p in (live.cut(src, box, cap_of(src, m)) for src in whole) if p is not None]
        mk.transform(parts, Matrix.Translation((-(box[0] + box[1]) / 2, -(box[2] + box[3]) / 2, 0)))
        bpy.context.view_layer.update()
        for src in whole:
            src.hide_render = True
        live.export(parts, name, options)
        for src in whole:
            src.hide_render = False


if __name__ == "__main__":
    build()
