"""The wrecks of the jawed guns in the leaves of TORM, BOTANY A, BOTANY B, BONUS and ROOST (sheet G 229 beside 231:
gun A; 267 beside 269: gun B), stage 4 of the clean ground (2026-10-25): what the maps paint under the guns, which
tools/terrain/make_cleanground.py erases and the game shows as stand-ins (models.cfg "wreck g 229 jaw_gun_a_left_wreck"
and so on, drawn with the live sprite lines' options: yaw=0 height=-4).

As the maps paint it (TORM's, BOTANY A's, ROOST's and BONUS' tiles under the guns, at 4x in the HD tiles; whole
coordinates as below): the same jaw, torn open. The deck's back edge (y 12-13) and the hinge's C round the left end
stay; the deck between them and the mouth is gone from x -16 to 1 (a jagged hole), its inside burnt black with red
embers in it (x -15..-10 y 7-10, x -6..0 y 9-12, x -12..-6 y 3-5, the brightest in the throat at x -2..2 y 1-3) and
twisted metal across it (a diagonal strut from (-13, 4) to (-9, 8), a pale bar along y 7-8, the divider bent upright
at x -3); the deck right of the hole, the flange, the rods, the bracket's post and its box (x 14-22) stand, the brace
still runs down to the jaw's corner; the gun and its red lens under the box are gone (dark there); the lower jaw is
burnt black and broken, its fangs splayed as charred bars down into the leaves (x -14, -8, -4, 0 from y 0 to -6).
Gun B's painting is gun A's mirrored (column c of B is column 46 - c of A, as the live sprites are).

Built on polish_jaw_gun.py: its parts in the cold state (the upper jaw, the hinge, the lower jaw, the flange and rods,
the bracket), then broken: the hole cut out of the upper jaw with an exact boolean (its floor soot, its torn walls
glowing dimly), the slot's parts inside it dropped, torn deck plates bent up at its rim, twisted bars across it,
embers (palette ramp 7, emission 0.22-0.42) in it and in the throat, the lower jaw cracked in two, its right part
dropped and turned, teeth knocked out or tilted, the fangs replaced by charred bent bars, a few charred shards on the
ground in front, the gun left out; everything scorched by a field strongest round the hole and over the mouth (faces
cut along its contours, their palette shades three darker or burnt brown-black 0x10; the hinge's C and the twisted
bars stay bright, as painted). Cut along x = 0 as the live gun (polish_arch.py's cut()), gun B mirrored about x = -0.5
first, as the live one.

Also here, for the other wreck scripts (polish_brick_crab_wreck.py, polish_cliff_bunker_wreck.py,
polish_deli_floor_eye_wreck.py): scorch(), darker(), ember(), shard(), rock(), bent_bar(), jagged(), inside(),
grid_cut(), reshade().

Coordinates as in polish_jaw_gun.py: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the ground (z = 0);
the whole's origin is the edge between the two sprites at their middle.

models.cfg: model jaw_gun_a_left_wreck enemies/jaw_gun_a_left_wreck.glb origin (and _a_right_, _b_left_, _b_right_);
wreck g 229 jaw_gun_a_left_wreck, wreck g 231 jaw_gun_a_right_wreck, wreck g 267 jaw_gun_b_left_wreck,
wreck g 269 jaw_gun_b_right_wreck.

Options after "--": --outdir <dir> (default assets/models/enemies), --preview <prefix>, --whole <prefix> (the uncut
wrecks too, <prefix>jaw_gun_a_wreck.glb ...), --only a|b.
"""
import math
import os
import random
import sys

import bmesh
import bpy
import mathutils.noise as noise
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_arch import cut  # noqa: E402
from polish_coral_manta import split_contour  # noqa: E402
import polish_jaw_gun as jg  # noqa: E402


# --- Shared wreck helpers ------------------------------------------------------------------------------------------

def palette_index(mat):
    """The palette index of a "<name>@<index>" material, or None."""
    if mat is None or "@" not in mat.name:
        return None
    try:
        return int(mat.name.rsplit("@", 1)[1])
    except ValueError:
        return None


def is_lit(mat):
    bsdf = mat.node_tree.nodes.get("Principled BSDF") if mat is not None and mat.use_nodes else None
    return bsdf is not None and bsdf.inputs["Emission Strength"].default_value > 0 and \
        tuple(bsdf.inputs["Emission Color"].default_value)[:3] != (0.0, 0.0, 0.0)


def darker(index, level):
    """A palette shade burnt `level` steps: level 1 three shades darker within its ramp of 16 (not below the ramp's
    first shade above black), level 2 or more the burnt brown-black 0x10 (the maps' soot)."""
    if level >= 2:
        return 0x10
    ramp, shade = divmod(index, 16)
    return 16 * ramp + max(min(shade, 1), shade - 3 * level)


def burnt_material(mat, level):
    """The material of mat scorched `level` steps: one material per burnt palette shade ("burnt@<index>", rough and
    dull; "soot@16" for the brown-black), shared by all the parts; lit materials (embers, lenses) stay."""
    index = palette_index(mat)
    if index is None or is_lit(mat) or level <= 0:
        return mat
    new = darker(index, level)
    if new == index:
        return mat
    name = "soot" if new == 0x10 else "burnt"
    found = bpy.data.materials.get("%s@%d" % (name, new))
    if found is None and new != 0x10:
        # A material of the model's own of that shade or one off it in the same ramp (fewer materials), darker first.
        for target in (new, new - 1, new + 1):
            if target // 16 != new // 16 or target == index:
                continue
            found = next((x for x in sorted(bpy.data.materials, key=lambda x: x.name)
                          if palette_index(x) == target and not is_lit(x) and x.users > 0), None)
            if found is not None:
                break
    return found or k.material(name, palette=new, metallic=0.3, roughness=0.72 if new == 0x10 else 0.6)


def grid_cut(obj, step=1.0, axes=("x", "y")):
    """Cuts an object's faces along planes x = n * step (and y), so fields painted on it follow smooth contours."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    if not bm.verts:
        bm.free()
        return obj
    for axis in axes:
        i = 0 if axis == "x" else 1 if axis == "y" else 2
        lo = min(v.co[i] for v in bm.verts)
        hi = max(v.co[i] for v in bm.verts)
        n = math.floor(lo / step) + 1
        while n * step < hi:
            co = [0.0, 0.0, 0.0]
            co[i] = n * step
            no = [0.0, 0.0, 0.0]
            no[i] = 1.0
            bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-5, plane_co=co,
                                   plane_no=no)
            n += 1
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    return obj


def scorch(obj, field, levels=(0.25, 0.62), step=None):
    """Scorches an object: its faces cut along a grid (step) and along the field's contours at the levels, each face
    then given its material burnt by the number of levels the field passes over it (burnt_material)."""
    if step:
        grid_cut(obj, step)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    vals = {"f": {v: field(v.co) for v in bm.verts}}
    for t in levels:
        split_contour(bm, vals, "f", t)
    mats = list(obj.data.materials)
    slots = {}
    for f in bm.faces:
        value = sum(vals["f"][v] for v in f.verts) / len(f.verts)
        level = sum(1 for t in levels if value > t + 1e-6)
        if level == 0:
            continue
        src = mats[f.material_index] if f.material_index < len(mats) else None
        new = burnt_material(src, level)
        if new is src or new is None:
            continue
        if new.name not in slots:
            slots[new.name] = mk.slot_of(obj, new)
        f.material_index = slots[new.name]
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    return obj


def reshade(obj, angle=35.0, round_part=False):
    """Shading again after cuts: smooth by angle (round parts) or weighted normals (hard-surface parts)."""
    if round_part:
        return k.smooth(obj, angle)
    return mk.shade(obj, angle)


def jagged(points, seed, amount=0.45, step=0.7):
    """A polygon's outline roughened: each edge divided about every `step` and its points pushed in and out by noise
    (deterministic: mathutils' Perlin noise)."""
    out = []
    n = len(points)
    for i in range(n):
        a, b = Vector(points[i]), Vector(points[(i + 1) % n])
        d = b - a
        count = max(1, int(round(d.length / step)))
        normal = Vector((d.y, -d.x)).normalized() if d.length > 1e-9 else Vector((0, 0))
        for j in range(count):
            p = a + d * (j / count)
            off = amount * noise.noise(Vector((p.x * 0.9 + seed, p.y * 0.9 - seed, seed * 0.37)))
            if j == 0:
                off *= 0.5
            out.append(tuple(p + normal * off))
    return out


def inside(point, polygon):
    """Whether a point (x, y) lies inside a polygon [(x, y), ...] (even-odd rule)."""
    x, y = point[0], point[1]
    result = False
    n = len(polygon)
    for i in range(n):
        x0, y0 = polygon[i]
        x1, y1 = polygon[(i + 1) % n]
        if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
            result = not result
    return result


def ccw(points):
    area = sum(points[i][0] * points[(i + 1) % len(points)][1] - points[(i + 1) % len(points)][0] * points[i][1]
               for i in range(len(points)))
    return list(points) if area > 0 else list(points)[::-1]


def ember_material(index, strength):
    """An ember glowing faintly in its own palette colour (emission well under 0.5: the game's bloom burns strong
    emission white)."""
    glow = k.level_palette()
    return k.material("ember_%x_%d" % (index, int(round(strength * 100))), palette=index, metallic=0.0, roughness=0.9,
                      emission=glow[index], emission_strength=strength)


def lump(name, centre, radii, mat, seed, wobble=0.22, subdivisions=2, flat=None):
    """An irregular lump (rubble, a charred chunk, an ember): an icosphere scaled to radii, its surface pushed by
    noise; flat cuts it off below z = flat."""
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subdivisions, radius=1.0)
    for v in bm.verts:
        d = v.co.normalized()
        r = 1.0 + wobble * noise.noise(d * 1.7 + Vector((seed, -seed * 0.6, seed * 0.3)))
        v.co = Vector(centre) + Vector((d.x * radii[0], d.y * radii[1], d.z * radii[2])) * r
    if flat is not None:
        res = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-5,
                                     plane_co=(0, 0, flat), plane_no=(0, 0, -1), clear_outer=True)
        edges = [e for e in res["geom_cut"] if isinstance(e, bmesh.types.BMEdge) and e.is_valid and e.is_boundary]
        if edges:
            bmesh.ops.holes_fill(bm, edges=edges, sides=0)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.data.materials.append(mat)
    return obj


def ember(name, centre, radii, mats, seed):
    """An ember: a flattened lump of the darkest material, a smaller hotter one rising out of its middle (mats: the
    rim's and the core's materials)."""
    outer = lump(name, centre, radii, mats[0], seed, 0.32, 2)
    k.smooth(outer, 70)
    core_c = Vector(centre) + Vector((0.0, -0.1 * radii[1], 0.45 * radii[2]))
    core = lump(name + "_core", tuple(core_c), (radii[0] * 0.55, radii[1] * 0.55, radii[2] * 0.7), mats[1],
                seed + 3.1, 0.2, 1)
    k.smooth(core, 70)
    return [outer, core]


def rock(name, centre, radii, mat, seed, flat=0.0, angle=30.0):
    """A broken stone or chunk: a coarse lump (faceted: flat shading kept over sharp edges), cut flat at its foot."""
    obj = lump(name, centre, radii, mat, seed, 0.3, 1, flat=flat)
    mk.shade(obj, angle)
    return obj


def shard(name, outline, z, thickness, mat, tilt=(0.0, 0.0), pivot=None):
    """A thin plate (a torn sheet, a charred shard): an outline in plan extruded by thickness from z, tilted about
    x and y (degrees) round pivot (default: its centre)."""
    obj = mk.prism(name, ccw(outline), z, z + thickness, mat)
    mk.bevel(obj, min(0.12, thickness * 0.4), 1, 35)
    if pivot is None:
        cx = sum(p[0] for p in outline) / len(outline)
        cy = sum(p[1] for p in outline) / len(outline)
        pivot = (cx, cy, z)
    turn = (Matrix.Translation(pivot) @ Matrix.Rotation(math.radians(tilt[0]), 4, "X") @
            Matrix.Rotation(math.radians(tilt[1]), 4, "Y") @ Matrix.Translation(-Vector(pivot)))
    obj.data.transform(turn)
    mk.shade(obj, 35)
    return obj


def bent_bar(name, points, radius, mat, segments=8):
    """A twisted bar along points (x, y, z) or (x, y, z, radius)."""
    pts = [tuple(p) if len(p) == 4 else tuple(p) + (radius,) for p in points]
    obj = mk.smooth_tube(name, pts, mat, segments, iterations=2)
    return k.smooth(obj, 55)


def clip_below(obj, z):
    return jg.clip_below(obj, z)


def delete(objects):
    for obj in objects:
        data = obj.data
        bpy.data.objects.remove(obj)
        if data is not None and data.users == 0:
            bpy.data.meshes.remove(data)


# --- The gun's wreck (gun A; whole coordinates) --------------------------------------------------------------------

# The hole torn into the upper jaw (plan, before roughening): from the hinge's C to the deck's right end, from the
# deck's back edge down through the mouth.
HOLE = [(-16.2, 9.4), (-14.6, 11.1), (-12.0, 10.7), (-10.2, 11.6), (-7.6, 11.1), (-5.4, 12.0), (-3.2, 11.5),
        (-1.0, 11.9), (0.9, 10.7), (0.3, 9.0), (1.6, 7.4), (0.6, 5.8), (1.5, 3.6), (-1.0, 2.2), (-15.4, 2.2),
        (-14.9, 5.2), (-16.6, 7.4)]
HOLE_FLOOR = 2.3                # the hole's floor (in the back of the head, where the jaw reaches the ground)
# The torn plates bent up at the hole's rim: outline, z, tilt about x and y (degrees), pivot.
PETALS = [([(-16.4, 9.0), (-14.4, 9.3), (-14.0, 11.0), (-15.4, 10.9)], 7.9, (-28.0, 14.0), (-15.0, 10.9, 8.3)),
          ([(-6.2, 11.2), (-3.6, 11.0), (-3.0, 12.1), (-5.6, 12.4)], 8.0, (-34.0, 0.0), (-4.5, 12.0, 8.4)),
          ([(0.0, 9.4), (1.4, 8.6), (1.8, 10.6), (0.6, 10.9)], 7.9, (0.0, 30.0), (1.4, 9.8, 8.3)),
          ([(-11.0, 10.6), (-8.6, 10.4), (-8.2, 11.6), (-10.6, 11.8)], 8.0, (-22.0, -8.0), (-9.6, 11.5, 8.4))]
# The twisted bars across the hole: points (x, y, z), radius, material.
BARS = [([(-13.6, 3.6, 3.2), (-12.2, 5.4, 5.6), (-10.6, 6.9, 7.0), (-8.8, 8.3, 7.7)], 0.42, "edge"),
        ([(-11.6, 7.6, 6.7), (-9.4, 7.0, 6.4), (-7.2, 7.5, 6.9), (-5.2, 7.9, 6.2)], 0.36, "edge"),
        ([(-3.0, 2.8, 2.6), (-3.3, 5.0, 5.4), (-2.6, 7.2, 6.8), (-3.2, 9.2, 7.6)], 0.44, "light"),
        ([(-15.0, 8.2, 6.6), (-13.4, 8.8, 5.2), (-12.4, 9.6, 3.6)], 0.3, "steel")]
# The embers in the hole and the throat: centre, radii, the rim's and the core's glow ("dim", "mid", "hot").
EMBERS = [((-12.8, 8.4, 2.8), (3.0, 2.0, 0.9), "mid", "hot"),
          ((-3.4, 10.3, 2.8), (3.2, 1.6, 0.9), "mid", "hot"),
          ((-9.0, 4.2, 1.3), (3.0, 1.3, 0.7), "mid", "hot"),
          ((-0.2, 2.2, 1.9), (2.2, 1.5, 1.2), "mid", "hot"),
          ((5.8, 4.0, 1.2), (1.1, 0.9, 0.5), "dim", "mid")]
GLOWS = {"dim": (0x74, 0.22), "mid": (0x76, 0.3), "hot": (0x77, 0.42)}
# Charred chunks lying in the hole (centre, radii).
CHUNKS = [((-14.2, 6.6, 2.4), (1.3, 1.1, 0.8)), ((-6.4, 9.2, 2.6), (1.4, 1.0, 0.8)),
          ((-7.6, 5.6, 1.4), (1.1, 0.9, 0.6)), ((-1.6, 6.0, 2.0), (1.0, 1.2, 0.7))]
# The charred bars splayed from the lower jaw's front into the leaves (the painting's fangs): points, radius.
FANG_BARS = [([(-14.2, 0.6, 1.8), (-14.6, -1.6, 1.0), (-13.6, -3.8, 0.1)], 0.55),
             ([(-8.4, 0.8, 2.0), (-8.0, -1.4, 1.2), (-7.0, -3.9, 0.15)], 0.6),
             ([(-4.6, -0.4, 1.6), (-4.0, -2.4, 0.9), (-3.2, -4.6, 0.1)], 0.5),
             ([(-0.6, -0.8, 1.4), (0.2, -3.0, 0.8), (1.0, -5.6, 0.05)], 0.45)]
# Charred shards on the ground in front and under the bracket (outline, z, thickness, tilt).
SHARDS = [([(-18.4, -1.4), (-16.2, -1.8), (-16.8, -3.4), (-18.8, -2.8)], 0.0, 0.35, (6.0, -8.0)),
          ([(-11.6, -3.4), (-9.8, -3.0), (-10.0, -4.8)], 0.0, 0.3, (-5.0, 6.0)),
          ([(2.6, -1.6), (4.6, -1.2), (4.2, -3.2), (2.8, -3.0)], 0.0, 0.35, (4.0, 10.0)),
          ([(14.6, 0.8), (17.8, 1.6), (18.6, 0.0), (15.4, -0.8)], 0.0, 0.45, (-6.0, 4.0)),
          ([(19.0, 3.4), (20.6, 3.8), (20.2, 2.2)], 0.0, 0.3, (8.0, 0.0))]
# The scorch: strongest round the hole's middle, torn by noise.
BURN_CENTRE, BURN_RADII = Vector((-7.5, 6.5, 4.0)), Vector((11.0, 7.5, 8.0))


def burn(co):
    d = Vector(((co.x - BURN_CENTRE.x) / BURN_RADII.x, (co.y - BURN_CENTRE.y) / BURN_RADII.y,
                (co.z - BURN_CENTRE.z) / BURN_RADII.z))
    mouth = 0.55 * smooth01((5.0 - co.y) / 2.0) * smooth01((3.0 - co.x) / 3.0)   # the mouth and the lower jaw
    return (1.05 * math.exp(-1.3 * d.length_squared) + mouth +
            0.18 * noise.noise(co * 0.45 + Vector((3.1, 7.2, 1.3))))


# How each part takes the scorch: (prefix, base, factor): the hinge's C keeps its light grey, as painted; the jaw and
# the bracket burnt all over.
BURN_PARTS = [("hinge", 0.0, 0.45), ("petal", 0.0, 0.5), ("upper_jaw", 0.22, 1.0), ("lower_jaw", 0.25, 1.0),
              ("flange", 0.12, 1.0),
              ("rod", 0.12, 1.0), ("bracket", 0.12, 0.8), ("base", 0.12, 1.0), ("pod", 0.1, 0.8)]


def part_burn(name):
    for prefix, base, factor in BURN_PARTS:
        if name.startswith(prefix):
            return lambda co, b=base, f=factor: b + f * burn(co)
    return burn


def smooth01(t):
    t = min(1.0, max(0.0, t))
    return t * t * (3 - 2 * t)


def wreck_materials():
    m = jg.materials("cold")
    m["soot"] = k.material("soot", palette=0x10, metallic=0.2, roughness=0.8)
    m["char"] = k.material("jaw_char", palette=0x02, metallic=0.25, roughness=0.75)
    for key, (index, strength) in GLOWS.items():
        m[key] = ember_material(index, strength)
    return m


def build_wreck():
    """Gun A's wreck, whole (every part's modifiers applied)."""
    m = wreck_materials()
    hole = jagged(HOLE, 1.3, 0.5, 0.8)
    # The upper jaw, the hole torn out of it (its walls and floor soot, from the cutter).
    upper = jg.upper_jaw(m)
    cutter = mk.prism("hole_cut", ccw(hole), HOLE_FLOOR, 14.0, m["soot"])
    mk.boolean(upper, cutter, "DIFFERENCE")
    mk.cleanup(upper, dissolve=0.0)
    # Its torn walls glow dull red (the painting's red inside the hole), its floor soot.
    soot_slot = mk.slot_of(upper, m["soot"])
    dim_slot = mk.slot_of(upper, m["dim"])
    for poly in upper.data.polygons:
        if poly.material_index == soot_slot and abs(poly.normal.z) < 0.6:
            poly.material_index = dim_slot
    # The slot's parts: what lay in the hole is gone; the rivets outside it stay.
    jg.slot_parts(m, "cold")
    for obj in [o for o in mk.meshes() if o.name.startswith(("bezel", "divider", "lens", "slat", "rivet"))]:
        corners = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
        centre = sum(corners, Vector()) / 8
        if not obj.name.startswith("rivet") or inside((centre.x, centre.y), hole):
            delete([obj])
    jg.hinge(m)
    # The lower jaw, cracked at x = -11: its right part dropped and turned down at its front; teeth knocked out.
    jg.lower_jaw(m)
    low = bpy.data.objects["lower_jaw"]
    right = low.copy()
    right.data = low.data.copy()
    right.name = "lower_jaw_r"
    bpy.context.scene.collection.objects.link(right)
    mk.boolean(low, mk.prism("crack_l", ccw([(-11.2, -4.0), (-3.0, -4.0), (-3.0, 5.0), (-11.2, 5.0)]), -3, 5),
               "DIFFERENCE")
    mk.boolean(right, mk.prism("crack_r", ccw([(-30.0, -4.0), (-10.6, -4.0), (-10.6, 5.0), (-30.0, 5.0)]), -3, 5),
               "DIFFERENCE")
    turn = (Matrix.Translation((-10.6, 2.4, 0.0)) @ Matrix.Rotation(math.radians(14.0), 4, "X") @
            Matrix.Rotation(math.radians(6.0), 4, "Y") @ Matrix.Translation((10.6, -2.4, -0.6)))
    right.data.transform(turn)
    for name in ("upper_tooth1", "upper_tooth3", "lower_tooth2", "lower_tooth4", "fang0", "fang1", "fang2"):
        delete([bpy.data.objects[name]])
    for name, tilt in (("upper_tooth0", (18.0, 10.0)), ("upper_tooth2", (-24.0, -6.0)), ("upper_tooth4", (30.0, 0.0)),
                       ("lower_tooth3", (0.0, 28.0))):
        obj = bpy.data.objects[name]
        corners = [Vector(c) for c in obj.bound_box]
        c = sum(corners, Vector()) / 8
        obj.data.transform(Matrix.Translation(c) @ Matrix.Rotation(math.radians(tilt[0]), 4, "X") @
                           Matrix.Rotation(math.radians(tilt[1]), 4, "Y") @ Matrix.Translation(-c))
    # The flange, the rods, the bracket and its box stand; the gun under the box is gone.
    jg.right_end(m)
    jg.bracket(m)
    # Torn plates at the hole's rim, twisted bars across it.
    for i, (outline, z, tilt, pivot) in enumerate(PETALS):
        shard(f"petal{i}", outline, z, 0.4, m["grey"], tilt, pivot)
    for i, (points, radius, mat) in enumerate(BARS):
        bent_bar(f"twisted{i}", points, radius, m[mat])
    for i, (points, radius) in enumerate(FANG_BARS):
        bent_bar(f"charred_fang{i}", [p + (radius * (1.0 - 0.55 * j / (len(points) - 1)),)
                                      for j, p in enumerate(points)], radius, m["char"], 10)
    for i, (outline, z, thick, tilt) in enumerate(SHARDS):
        shard(f"shard{i}", outline, z, thick, m["char"], tilt)
    for i, (centre, radii) in enumerate(CHUNKS):
        rock(f"chunk{i}", centre, radii, m["soot"], 5.0 + i, flat=0.0)
    parts = mk.meshes()
    for obj in parts:
        mk.apply(obj)
    # Scorched: everything but the embers (made after), the darker the nearer the hole.
    round_parts = ("hinge", "twisted", "charred_fang", "rod", "bracket")
    gridded = ("upper_jaw", "lower_jaw", "mouth_floor", "cheek", "flange", "bracket_foot", "base", "pod")
    for obj in parts:
        if obj.name.startswith(("chunk", "shard", "charred_fang", "twisted")):
            continue  # (the twisted bars stay bright, as painted)
        scorch(obj, part_burn(obj.name), step=1.5 if obj.name.startswith(gridded) else None)
        reshade(obj, 50 if obj.name.startswith(round_parts) else 35, obj.name.startswith(round_parts))
    for i, (centre, radii, rim, core) in enumerate(EMBERS):
        ember(f"ember{i}", centre, radii, (m[rim], m[core]), 11.0 + 2.3 * i)
    whole = mk.meshes()
    for obj in whole:
        mk.apply(obj)
        if min(v.co.z for v in obj.data.vertices) < -jg.SKIRT - 1e-4:
            clip_below(obj, -jg.SKIRT)
    bpy.context.view_layer.update()
    return [o for o in whole if len(o.data.polygons) > 0], m


def build():
    options = k.args()
    out = mk.outdir(options)
    only = options.get("only")
    for gun, left, right in (("a", "jaw_gun_a_left_wreck", "jaw_gun_a_right_wreck"),
                             ("b", "jaw_gun_b_left_wreck", "jaw_gun_b_right_wreck")):
        if only and only != gun:
            continue
        k.reset()
        whole, m = build_wreck()
        if gun == "b":
            jg.mirrored(whole, jg.MIRROR_X)
        bpy.context.scene.view_settings.view_transform = "Standard"
        print("whole wreck %s: %d triangles, %d objects" % (gun, mk.triangles(whole), len(whole)))
        if "whole" in options:
            mk.export(whole, options["whole"] + "jaw_gun_%s_wreck.glb" % gun)
        if "preview" in options:
            mk.preview(options["preview"] + "jaw_gun_%s_wreck_whole" % gun, whole, size=(48, 28), scale=8,
                       distance=1.7)
        for name, box in ((left, (-24.0, 0.0, -14.0, 14.0)), (right, (0.0, 24.0, -14.0, 14.0))):
            pieces = [p for p in (cut(src, box, m["soot"]) for src in whole) if p is not None]
            mk.transform(pieces, Matrix.Translation((-(box[0] + box[1]) / 2, 0, 0)))
            bpy.context.view_layer.update()
            for src in whole:
                src.hide_render = True
            mk.report(name, pieces, os.path.join(out, name + ".glb"))
            if "preview" in options:
                mk.preview(options["preview"] + name, pieces)
            for obj in pieces:
                bpy.data.objects.remove(obj)
            for src in whole:
                src.hide_render = False


if __name__ == "__main__":
    build()
