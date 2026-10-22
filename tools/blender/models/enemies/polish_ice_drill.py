"""CAMANIS' ice drill (sheet 7: the red hood 169 above its arm 207, 2x2 each: one 24 x 56 picture; enemies 85 above 86
of episode 3, on the ground: 14 times in CAMANIS, t 384-3324, the arm's event 28 ticks before the hood's, one tile
row below it at the same x, both on one link), polished (2026-10-22; it replaces wave3_ac_ice.py's drill and
wave3_at_misc.py's drill_in(): a sphere carved into a hood and a stack of lathed parts). models.cfg: model
ice_drill_dome / ice_drill_arm enemies/ice_drill_dome.glb / ice_drill_arm.glb origin (unchanged), model
ice_drill_arm_205 / _203 (unchanged); sprite 7 169 ice_drill_dome yaw=0 height=-4 and sprite 7 207 ice_drill_arm
yaw=0 height=-4 (height=-4 is new: the hood and its arm on the ice, see below); frame 7 205 ice_drill_arm_205, frame 7
203 ice_drill_arm_203 (unchanged). No other enemy (launched ones included) shows these sprites or their frames; none of
them is another sprite's pixels mirrored, turned or in other ramps. Episode 6 does not use the drill.

Its frames: the arm (enemy 86: 207 205 203 205 207, animate 2) plays them when it launches its ice spike (enemy 463, D
191, every 40 ticks): its knuckle, the head with its band and bracket and the point slide 2 and 3 pixels up the screen
into the flange, the neck behind the knuckle hidden in it (frame models, cut as the arm is). The hood's frames (85: 169
167 165 167 169) would light the lamp on its back, but it has no gun and launches nothing, and no level event starts its
animation: the game only ever shows 169, the lamp dim, as the model does.

As the sprites and their 4x upscales draw it (columns and rows of the 24 x 56 picture; the drill is symmetric about the
middle of the picture's columns 10 and 11, x = -1): the red hood (columns 1-20 of rows 0-24): a glossy dome, lit on its
upper left (its glint orange-yellow), the dim orange lamp panel on its back (columns 8-14 of rows 1-5); open at its
front (rows 9-21) between two clawed cheeks, each two red fingers curling down (the outer one from row 8 to row 20, the
inner one from row 11 to row 17); in the dark opening the grey fork of the arm's piston (its prongs columns 8 and 13 of
rows 14-21, a pin across them, rows 16-17); under the hood the red collar the arm comes out of (columns 6-15 of rows
21-25). The arm lying on the ice down the screen (rows 25-52): a short grey rod, the flange (columns 6-15 of rows
28-33, a mushroom cap lit along its back), a thin neck, the red knuckle (rows 35-37), the grey head (columns 4-17 of
rows 38-52): a bulb lit on its upper left (rows 38-43) with a dark band round it at row 43, a cone under it tapering to
the point (rows 44-52), a bracket on its right side (column 16, rows 41-47). Round the hood CAMANIS' ice (ramp 3:
columns 0-4 and 17-23 beside it, rows 21-27 under the collar): the map's ground and the hood's shadow, left out (the
silhouette is checked against the drill's own pixels, the ice's left out).

Built as the ice levels' other machines are (polish_ice_bunker.py, polish_ice_globe.py): the hood a lathed dome (its
plan the sprite's outline, a superellipse, its top flattened a little) cut open at the front by an exact boolean, its
inside dark, the lamp panel a low glowing pad laid on its back; the fingers tapering tubes along curves; the fork two
bevelled prongs and a pin on a dark piston block; the collar, the rod, the flange, the neck, the knuckle and the head
lathed about the arm's axis (lying along the screen 5 pixels over the ice), the head's cross-section a flattened
ellipse (as wide as the sprite draws it, lower than that), its band a dark groove ring, the bracket a bevelled block.
Faces are painted by how they face the sun: the red 0x76 (its shaded side 0x74, underside 0x72, lit faces 0x78, the
glint on the hood's upper left 0x7b and 0x7c, a little emission so the glossy red does not read black from the game's
camera, 0.05-0.12), the greys as the bunker's (tops 0x0a, rims facing the sun 0x0c, sides 0x08, undersides 0x02), the
lamp 0x76 at 0.2 (dim, as 169 draws it). The whole is cut along the sprites' edge (y = 0; the coral manta's cut: the
pieces keep the whole's shading, their caps dark), each piece moved so its sprite's centre is its origin, its parts
joined into one mesh and triangulated (the same output with and without --check).

Where it stands: the drill stands on the ice at its hood, its arm lying on it (the whole on z = 0, the head's lowest
point just over it); models drawn at their origin stand at the ground enemies' layer, 4 pixels above the terrain, so
height=-4 on both sprite lines sets them on the ice, as the bunker and the globe stand (the game lifts the two pieces
onto the terrain at one height, the terrain's under their middle).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the ice; the whole's origin is
the middle of the picture (the edge between the two sprites): column c's left edge is x = c - 12, row r's top edge
y = 28 - r. The pieces' centres: 169 (0, 14), 207 (0, -14).

Replaces wave3_ac_ice.py (all that is left of it: the drill, build_drill() and its a.pieced("ice_drill", ...)
registration; the bunker, the globe and the vent are polished already): delete it, and wave3_at_misc.py's drill section
("# --- Sheet 7: the drill's arm pulling in": drill_in() and its loop over 205 / 203, the quiet_import of wave3_ac_ice,
and the drill paragraph of its docstring); wave3_ac_art.py's DRILL and DRILL_B (only the drill read them) and
wave3_ac_kit.py (only wave3_ac_ice.py imported it) go with it.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes of the whole
and of each piece against the drill's own pixels of enemy_7.png), --preview <prefix> (the whole's top and 3/4 views;
--pieces 1 also each piece's), --only <name,...> (models to export; "none": none), --whole <file.glb> (the uncut drill
as well, for looking at), --stats 1 (the whole's parts' triangles).
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_deli_boss import join, drop_unused  # noqa: E402
from polish_coral_manta import cut  # noqa: E402  (savara's cut, the caps' material set as they are made)
from polish_k_pod import triangulate  # noqa: E402
from polish_orb_red import band_split  # noqa: E402

AX = -1.0                       # the drill's axis (between the picture's columns 10 and 11)
LIGHT = Vector((-0.6, 0.6, 1.0)).normalized()   # towards the sun (from the upper left and above)
# The pieces: model, its look's sprite, the piece's box; the arm's frames (sprite: how far its head slides in).
PIECES = [("ice_drill_dome", 169, (-12.0, 12.0, 0.0, 28.0)), ("ice_drill_arm", 207, (-12.0, 12.0, -28.0, 0.0))]
ARM_FRAMES = {205: 2.0, 203: 3.0}


def XE(c):
    """The left edge of the picture's column c (fractions allowed)."""
    return c - 12.0


def YE(r):
    """The top edge of the picture's row r."""
    return 28.0 - r


# --- The measures --------------------------------------------------------------------------------------------------
# The hood: its plan (a superellipse: middle row, half-width, half-length, power), its height and how its top is
# flattened, the opening at its front (half-width, from row, down to row), the cavity's floor.
HOOD = (12.3, 10.0, 12.4, 3.0)
HOOD_H, HOOD_FLAT = 8.6, 0.82
OPENING = (7.9, 8.6, 26.0)
CAVITY_FLOOR = 0.6
# The lamp on its back (middle column and row, half-axes, how far it stands out).
LAMP = (11.0, 3.2, 3.3, 2.0, 0.35)
# The fingers of the cheeks (the left side's; mirrored): [(column, row, height, radius)] along each.
FINGERS = [[(3.0, 7.0, 6.2, 1.7), (2.9, 10.0, 5.6, 1.75), (3.1, 13.0, 4.8, 1.65), (3.7, 16.0, 3.8, 1.45),
            (4.6, 18.6, 2.8, 1.15), (5.6, 20.4, 2.0, 0.8), (6.4, 21.3, 1.5, 0.4)],
           [(6.4, 9.6, 6.8, 1.3), (6.2, 12.0, 6.0, 1.35), (6.0, 14.2, 5.0, 1.2), (6.3, 16.0, 4.0, 0.95),
            (6.9, 17.4, 3.2, 0.5)]]
# The piston's fork in the opening: the prongs (column, rows), their half-width; the pin (rows); the block they stand
# on (columns, rows, top).
PRONGS = [(8.5, 13.8, 21.4), (13.5, 13.8, 21.4)]
PRONG_W = 0.75
PIN = (15.9, 17.6)
PISTON = (7.4, 14.6, 12.6, 22.0, 3.6)
# The arm: its axis' height, the lathed profile [(row, radius)] of its parts from the collar down (the collar red, the
# rod, the flange, the neck, the knuckle red, the head and its point), how flat the head is.
ARM_Z = 5.4
COLLAR = [(20.6, 3.8), (21.3, 4.8), (23.4, 5.1), (25.4, 4.8), (26.4, 3.8), (26.9, 2.2)]
ROD = [(26.4, 1.6), (28.6, 1.6)]
FLANGE = [(28.0, 2.4), (28.6, 3.9), (29.4, 4.8), (32.4, 5.0), (33.2, 4.4), (33.7, 2.6), (34.0, 1.3)]
NECK = [(33.6, 1.2), (35.4, 1.2)]
KNUCKLE = (36.4, 2.8, 1.6)       # middle row, radius across, radius along
# The head: a bulb, its front rounded down to its muzzle (from row, the hole's radius, the lip's).
HEAD = [(37.6, 2.0), (38.2, 4.0), (39.2, 5.6), (40.4, 6.5), (42.0, 7.0), (44.5, 7.0), (46.5, 6.6), (48.2, 5.8),
        (49.6, 4.6), (50.8, 3.4), (51.8, 2.2), (52.6, 0.4)]
HEAD_FLAT = 0.74
MUZZLE = (50.4, 1.5, 2.4)
BAND = (43.0, 0.45)             # the dark band round the head: row, half-width
BRACKET = (15.6, 17.6, 40.8, 47.6, 1.8)   # columns, rows, half-height


def materials():
    pal = k.level_palette()

    def mat(name, index, metallic, roughness, glow=None):
        if glow:
            return k.material("idrill_" + name, palette=index, metallic=metallic, roughness=roughness,
                              emission=pal[index], emission_strength=glow)
        return k.material("idrill_" + name, palette=index, metallic=metallic, roughness=roughness)
    return {
        "red_under": mat("red_under", 0x72, 0.3, 0.4, 0.05),
        "red_side": mat("red_side", 0x74, 0.35, 0.32, 0.06),
        "red": mat("red", 0x76, 0.35, 0.28, 0.08),
        "red_lit": mat("red_lit", 0x78, 0.35, 0.24, 0.1),
        "glint": mat("glint", 0x7b, 0.3, 0.2, 0.12),
        "lamp": mat("lamp", 0x76, 0.05, 0.3, 0.2),
        "steel": mat("steel", 0x08, 0.4, 0.4),
        "lit": mat("lit", 0x0a, 0.4, 0.36),
        "hi": mat("hi", 0x0c, 0.4, 0.32),
        "dark": mat("dark", 0x02, 0.3, 0.55),
        "black": mat("black", 0x01, 0.2, 0.5),
    }


# --- Helpers ------------------------------------------------------------------------------------------------------

def superellipse(cx, cy, a, b, p, n=64):
    pts = []
    for j in range(n):
        t = 2 * math.pi * j / n
        c, s = math.cos(t), math.sin(t)
        pts.append((cx + a * math.copysign(abs(c) ** (2 / p), c), cy + b * math.copysign(abs(s) ** (2 / p), s)))
    return pts


def paint_light(obj, m, bands, under=None):
    """Faces by how much they face the sun, along smooth borders (band_split): bands [(lowest n . LIGHT, name)];
    faces turned down (n.z < -0.3) under."""
    mesh = obj.data
    mesh.update()
    values = [0.0] * len(mesh.vertices)
    count = [0] * len(mesh.vertices)
    for poly in mesh.polygons:
        for vi in poly.vertices:
            values[vi] += poly.normal.dot(LIGHT)
            count[vi] += 1
    values = [v / max(c, 1) for v, c in zip(values, count)]
    band_split(obj, values, [(lo, m[name]) for lo, name in bands])
    if under:
        mk.paint(obj, lambda c, n: m[under] if n.z < -0.3 else None)
    return obj


def paint_faces(obj, m, top, side, lit=None, under="dark", top_min=0.9, lit_min=0.5):
    def pick(c, n):
        if n.z > top_min:
            return m[top]
        if n.z < -0.3:
            return m[under]
        if lit and n.dot(LIGHT) > lit_min:
            return m[lit]
        return m[side]
    return mk.paint(obj, pick)


RED_BANDS = [(-9.0, "red_side"), (0.35, "red"), (0.72, "red_lit"), (0.9, "glint")]
GREY_BANDS = [(-9.0, "steel"), (0.55, "lit"), (0.88, "hi")]


def arm_lathe(name, rows, mat, flat=1.0, shift=0.0, segments=24):
    """A part turned about the arm's axis: [(row, radius)] down the screen; flat squashes its height."""
    rings = []
    for r, rad in rows:
        y = YE(r) + shift
        rings.append(k.ring(y, max(rad, 0.02), max(rad, 0.02) * flat, segments, z=ARM_Z, x=AX))
    obj = k.loft(name, rings[::-1], mat)
    return k.smooth(obj, 50)


# --- The hood ------------------------------------------------------------------------------------------------------

def hood_height(x, y):
    """The hood's top over (x, y): a dome over its superellipse plan, its top flattened a little."""
    r, a, b, p = HOOD
    u = (abs(x - AX) / a) ** p + (abs(y - YE(r)) / b) ** p
    if u >= 1.0:
        return 0.0
    rho = u ** (1.0 / p)
    return HOOD_H * min(1.0, (1.0 - rho ** 2.2) ** 0.5 / HOOD_FLAT)


def hood(m):
    """The red hood: a dome over the sprite's outline, open at its front between the cheeks, its inside dark."""
    r, a, b, p = HOOD
    rings = []
    steps = 16
    plan_pts = superellipse(AX, YE(r), a, b, p, 52)
    for i in range(steps + 1):
        f = i / steps                       # from the rim (0) to the top (1)
        rho = 1.0 - f ** 1.6 * 0.995
        z = HOOD_H * min(1.0, (1.0 - rho ** 2.2) ** 0.5 / HOOD_FLAT)
        rings.append([Vector((AX + (px - AX) * rho, YE(r) + (py - YE(r)) * rho, z)) for px, py in plan_pts])
    shell = k.loft("hood", rings, m["red"], cap_start=True, cap_end=True,
                   start_point=(AX, YE(r), 0.0), end_point=(AX, YE(r), HOOD_H))
    k.smooth(shell, 60)
    half, r0, r1 = OPENING
    opening = mk.wedge("hood_opening", [(AX - half, YE(r1)), (AX + half, YE(r1)), (AX + half, YE(r0)),
                                        (AX - half, YE(r0))], -1.0, lambda x, y: 20.0, m["black"])
    mk.boolean(shell, opening, "DIFFERENCE")
    mk.cleanup(shell, dissolve=0.0)
    paint_light(shell, m, RED_BANDS, under="red_under")
    # The opening's walls and the hood's inside dark (the cut's own faces are black already).
    mk.paint(shell, lambda c, n: m["black"] if c.z < HOOD_H - 0.2 and abs(c.x - AX) < half + 0.05 and
             c.y < YE(r0) + 0.05 and n.z < 0.95 else None)
    k.smooth(shell, 60)
    # The cavity's floor in the opening, dark.
    cavity = mk.box("hood_cavity", AX - half - 0.2, AX + half + 0.2, YE(r1 - 4.0), YE(r0) + 0.6, 0.0, CAVITY_FLOOR,
                    m["black"])
    # The lamp on its back: a low glowing pad following the dome.
    c, rr, ax, ay, lift = LAMP
    cx, cy = XE(c) + 0.5, YE(rr)
    lamp = mk.ball("hood_lamp", (cx, cy, hood_height(cx, cy) - 0.25), (ax, ay, lift + 0.25), m["lamp"], 20, 8)
    return [shell, cavity, k.smooth(lamp, 70)]


def fingers(m):
    """The cheeks' fingers curling down beside the opening (the left side's; mirrored), red, tapering."""
    parts = []
    for i, finger in enumerate(FINGERS):
        pts = [(XE(c) + 0.5, YE(r), z, rad) for c, r, z, rad in finger]
        tube = mk.smooth_tube(f"finger{i}", pts, m["red"], 10, 2)
        k.smooth(tube, 60)
        paint_light(tube, m, RED_BANDS, under="red_under")
        parts.append(tube)
    return parts


def fork(m):
    """The piston's fork in the opening: two grey prongs on a dark block, a pin across them."""
    c0, c1, r0, r1, top = PISTON
    block = mk.box("piston", XE(c0), XE(c1), YE(r1), YE(r0), 0.0, top, m["dark"])
    mk.bevel(block, 0.3, 2, 30.0)
    paint_faces(block, m, "steel", "dark", top_min=0.9)
    parts = [mk.shade(block, 35.0)]
    for i, (c, r0, r1) in enumerate(PRONGS):
        x = XE(c)
        prong = mk.box(f"prong{i}", x - PRONG_W, x + PRONG_W, YE(r1), YE(r0), 0.0, top + 1.6, m["lit"])
        mk.bevel(prong, 0.3, 2, 30.0)
        paint_faces(prong, m, "hi", "steel", lit="hi", top_min=0.9, lit_min=0.55)
        parts.append(mk.shade(prong, 35.0))
    pr0, pr1 = PIN
    pin = mk.tube("pin", [(XE(PRONGS[0][0]) - 0.4, (YE(pr0) + YE(pr1)) / 2, top + 0.9),
                          (XE(PRONGS[1][0]) + 0.4, (YE(pr0) + YE(pr1)) / 2, top + 0.9)], 0.75, m["steel"], 12)
    paint_light(k.smooth(pin, 50), m, GREY_BANDS, under="dark")
    parts.append(pin)
    return parts


# --- The arm ----------------------------------------------------------------------------------------------------------

def arm(m, slide=0.0):
    """The collar, the rod, the flange (fixed), and the neck, the knuckle, the head with its band and bracket and the
    point, slid `slide` up the screen (the frames' arm pulled in)."""
    collar = arm_lathe("collar", COLLAR, m["red"], 0.9)
    paint_light(collar, m, RED_BANDS, under="red_under")
    rod = arm_lathe("rod", ROD, m["steel"], segments=16)
    paint_light(rod, m, GREY_BANDS, under="dark")
    flange = arm_lathe("flange", FLANGE, m["steel"], 0.92)
    paint_light(flange, m, GREY_BANDS, under="dark")
    neck = arm_lathe("neck", NECK, m["steel"], shift=slide, segments=14)
    paint_light(neck, m, GREY_BANDS, under="dark")
    r, rx, ry = KNUCKLE
    knuckle = mk.ball("knuckle", (AX, YE(r) + slide, ARM_Z), (rx, ry, rx * 0.95), m["red"], 24, 12)
    paint_light(k.smooth(knuckle, 70), m, RED_BANDS, under="red_under")
    head = arm_lathe("head", HEAD, m["steel"], HEAD_FLAT, shift=slide, segments=32)
    paint_light(head, m, GREY_BANDS, under="dark")
    # The band round the head: dark faces over its rows.
    br, bw = BAND
    mk.paint(head, lambda c, n: m["dark"] if abs(c.y - (YE(br) + slide)) < bw and n.z > -0.3 else None)
    # The muzzle at its front: the hole dark, its lip lit.
    mr, hole, lip = MUZZLE
    ym = YE(mr) + slide

    def muzzle(c, n):
        if c.y > ym:
            return None
        d = math.hypot(c.x - AX, (c.z - ARM_Z) / HEAD_FLAT)
        return m["black"] if d < hole else m["hi"] if d < lip else None
    mk.paint(head, muzzle)
    c0, c1, r0, r1, hh = BRACKET
    bracket = mk.box("bracket", XE(c0), XE(c1), YE(r1) + slide, YE(r0) + slide, ARM_Z - hh, ARM_Z + hh, m["steel"])
    mk.bevel(bracket, 0.3, 2, 30.0)
    paint_faces(bracket, m, "lit", "steel", lit="hi", top_min=0.9, lit_min=0.55)
    return [collar, rod, flange, neck, knuckle, head, mk.shade(bracket, 35.0)]


# --- The whole, checks, export ---------------------------------------------------------------------------------------

def build_whole(slide=0.0):
    m = materials()
    parts = hood(m)
    left = fingers(m)
    parts += left + mirror(left) + fork(m) + arm(m, slide)
    whole = [o for o in mk.meshes() if len(o.data.polygons) > 0]
    for obj in whole:
        mk.apply(obj)
    triangulate(whole)
    bpy.context.view_layer.update()
    return whole, m


def mirror(objects):
    """Copies of objects mirrored about the axis, their shading and materials kept."""
    flip = Matrix.Translation((AX, 0, 0)) @ Matrix.Scale(-1, 4, (1, 0, 0)) @ Matrix.Translation((-AX, 0, 0))
    out = []
    for obj in objects:
        mk.apply(obj)
        copy = obj.copy()
        copy.data = obj.data.copy()
        copy.name = obj.name + "_r"
        bpy.context.scene.collection.objects.link(copy)
        mesh = copy.data
        corner = {}
        for poly in mesh.polygons:
            for li in poly.loop_indices:
                n = mesh.corner_normals[li].vector
                corner[(poly.index, mesh.loops[li].vertex_index)] = (-n.x, n.y, n.z)
        mesh.transform(flip)
        mesh.flip_normals()
        normals = [None] * len(mesh.loops)
        for poly in mesh.polygons:
            for li in poly.loop_indices:
                normals[li] = corner[(poly.index, mesh.loops[li].vertex_index)]
        mesh.normals_split_custom_set(normals)
        out.append(copy)
    return out


def own_mask(sheets, sprite):
    """The drill's own pixels of a sprite: its pixels without the ice painted round it (ramp 3)."""
    import numpy as np
    mask = k.sprite_mask(os.path.join(sheets, "enemy_7.png"), sprite)
    path = os.path.join(sheets, "enemy_7.idx")
    if not os.path.exists(path):
        return mask
    idx = np.fromfile(path, np.uint8).reshape(224, 228)
    x0, y0 = (sprite - 1) % 19 * 12, (sprite - 1) // 19 * 14
    return [[mask[r][c] and idx[y0 + r, x0 + c] >> 4 != 3 for c in range(24)] for r in range(28)]


def export_piece(whole, m, name, sprite, box, options, sheets):
    parts = [p for p in (cut(src, box, m["dark"]) for src in whole) if p is not None]
    drop_unused(parts)
    mk.transform(parts, Matrix.Translation((-(box[0] + box[1]) / 2, -(box[2] + box[3]) / 2, 0)))
    bpy.context.view_layer.update()
    triangulate(parts)
    parts = [join(parts, name)]
    parts[0].data.name = name
    for src in whole:
        src.hide_render = True
    if sheets:
        mk.compare("%s (7 %d, its own pixels)" % (name, sprite), mk.coverage(parts, 24, 28), own_mask(sheets, sprite))
    mk.report(name, parts, os.path.join(mk.outdir(options), name + ".glb"))
    if "preview" in options and options.get("pieces") == "1":
        mk.preview(options["preview"] + name, parts)
    for obj in parts:
        data = obj.data
        bpy.data.objects.remove(obj)
        if data.users == 0:
            bpy.data.meshes.remove(data)
    for src in whole:
        src.hide_render = False


def build():
    options = k.args()
    only = options["only"].split(",") if "only" in options else None
    sheets = options.get("check")
    jobs = [(0.0, [(name, sprite, box) for name, sprite, box in PIECES])]
    jobs += [(slide, [(f"ice_drill_arm_{s}", s, PIECES[1][2])]) for s, slide in ARM_FRAMES.items()]
    for slide, pieces in jobs:
        if only is not None:
            pieces = [p for p in pieces if p[0] in only]
            if not pieces and not (slide == 0.0 and ("whole" in options or "preview" in options)):
                continue
        k.reset()
        whole, m = build_whole(slide)
        low, high = mk.bounds(whole)
        print("== whole drill (slide %.0f): %d triangles, %d objects, %d materials, x %.2f..%.2f y %.2f..%.2f "
              "z %.2f..%.2f" % (slide, mk.triangles(whole), len(whole), len(mk.materials_of(whole)), low.x, high.x,
                                low.y, high.y, low.z, high.z))
        if options.get("stats") == "1":
            for obj in sorted(whole, key=lambda o: -mk.triangles([o]))[:12]:
                print("   %-22s %6d" % (obj.name, mk.triangles([obj])))
        bpy.context.scene.view_settings.view_transform = "Standard"
        if slide == 0.0:
            if sheets:
                mask = own_mask(sheets, 169) + own_mask(sheets, 207)
                mk.compare("whole (7 169 above 207, the drill's own pixels)", mk.coverage(whole, 24, 56), mask)
            if "preview" in options:
                mk.preview(options["preview"] + "ice_drill_whole", whole, size=(24, 56), scale=12, distance=1.6)
            if "whole" in options:
                mk.export(whole, options["whole"])
        for name, sprite, box in pieces:
            export_piece(whole, m, name, sprite, box, options, sheets)


if __name__ == "__main__":
    build()
