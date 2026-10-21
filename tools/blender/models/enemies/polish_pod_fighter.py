"""MINERS's grey fighter with the yellow-lit pods (sheet L sprite 267, 2x2: 24 x 28 pixels; enemy 1150 of episode 5, sky
layer, about 18 of them; one frame), polished (2026-10-21; it replaces wave3_z_small.py's yellow_pod_fighter(), three
pixel-painted inflated blobs with a tube of light on each pod). models.cfg: model yellow_pod_fighter
enemies/yellow_pod_fighter.glb; sprite l 267 yellow_pod_fighter yaw=0 (both unchanged: the model faces the way the sprite
does, nose down the screen; the game centres sky objects in height). No other sprite has its pixels mirrored, turned or
in other ramps, and no other enemy shows it.

As the sprite and its 4x upscale draw it (rows 7-24; armour ramp 6's blue-greys, a navy outline, ramp 3): a slim
fuselage down the middle (columns 9-14): at its back (up the screen, rows 8-10) the engine, a pale cream rim
(0xed-0xef) round a dark mouth (0x03-0x04), the exhaust opening up and back; the body a rounded bulb (rows 11-16, lit
down its middle, 0x6a-0x6d), a narrow waist (row 17, two pixels), and the snout (rows 18-24) with the gun lying in a dark
slot along its top (columns 11-12 of rows 19-21, 0x03-0x06, the barrel's glint 0x0b), its tip a point (row 24). Either
side a pod like a long leaf (columns 0-7 and 16-23 of rows 7-22): pointed at both ends, its inner side straight along
the fuselage, its outer side bowed out, joined to the fuselage by short struts (rows 13-15); in each pod's top a
crescent window of yellow light bowed outwards (the left one's columns 2-4 of rows 11-18, 0x7a-0x7c; the right one's
columns 19-21, 0x7c-0x7e), a dark rim round it.

Built as a small aircraft would be: the fuselage and the pods lofted from round sections through smooth tables of the
sprite's widths and their heights; the crescents cut into the pods' tops (exact booleans), their floors glowing yellow
(emission 0.3-0.45, well under 1: the game's bloom adds), their walls dark; the engine a short nozzle turned up and
back at the fuselage's end, its lip dark, inside it the far (back) wall cream, lit by the exhaust (a faint glow, 0.3),
its throat dark; the gun a barrel lying in a slot cut along the snout; the struts round bars. The pods sit a little lower than the fuselage. The right pod is the left one mirrored
(the sprite draws the right one lighter: the game's sun, from the upper left, shades them itself).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; origin at the
sprite's centre (pixel 12, 14): column c is x = c + 0.5 - 12, row r is y = 13.5 - r. Symmetric about x = 0 (the edge
between columns 11 and 12).

Replaces wave3_z_small.py's yellow_pod_fighter(): remove its section ("# --- L 267: the fighter", the
@kit.model("yellow_pod_fighter", mask=lambda: SHIP.mask()) registration and yellow_pod_fighter()), the line SHIP =
kit.frame("SHIP", 24, (12, 14)) and the fighter's paragraph in its docstring; and wave3_z_art.py's SHIP (only that
function reads it). red_mouth_lander() and MECH stay. Nothing imports wave3_z_small.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouette against
enemy_L.png), --preview <prefix>, --stats 1 (triangles per part).
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
from polish_jets import Curve, spaced  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402

NAME = "yellow_pod_fighter"

# The fuselage: (y, half-width, its middle's height, half-height above, below), from the gun's tip up to the engine.
FUSELAGE = [(-10.55, 0.25, 0.3, 0.3, 0.25), (-10.0, 0.95, 0.45, 0.75, 0.6), (-9.3, 1.5, 0.55, 1.2, 0.9),
            (-8.4, 2.05, 0.6, 1.65, 1.15), (-7.3, 2.55, 0.65, 1.95, 1.3), (-6.0, 2.6, 0.65, 2.05, 1.35),
            (-4.9, 2.05, 0.6, 1.8, 1.2), (-4.0, 1.65, 0.55, 1.5, 1.0), (-3.4, 1.7, 0.6, 1.65, 1.1),
            (-2.6, 2.4, 0.75, 2.45, 1.6), (-1.4, 2.95, 0.85, 2.95, 1.9), (0.2, 3.05, 0.9, 3.1, 2.0),
            (1.6, 2.9, 0.9, 3.0, 1.95), (2.8, 2.7, 0.9, 2.75, 1.8), (3.9, 2.55, 0.85, 2.45, 1.65),
            (4.8, 2.25, 0.8, 2.05, 1.45), (5.5, 1.5, 0.7, 1.3, 1.0), (5.95, 0.4, 0.6, 0.4, 0.3)]
# The left pod (the right one mirrored): (y, its inner edge's x, its outer edge's x, half-height), from its front tip to
# its back tip (the sprite's columns 0-7 of rows 7-22, about two thirds into the navy outline).
POD = [(-8.85, -6.0, -6.6, 0.15), (-8.3, -5.55, -7.75, 0.75), (-7.3, -5.15, -8.85, 1.35), (-6.3, -4.85, -9.85, 1.85),
       (-5.0, -4.55, -10.75, 2.35), (-3.5, -4.4, -11.45, 2.65), (-1.5, -4.35, -11.65, 2.8), (0.5, -4.35, -11.55, 2.8),
       (2.0, -4.45, -11.0, 2.6), (3.4, -4.6, -10.4, 2.3), (4.6, -4.95, -9.55, 1.9), (5.5, -5.4, -8.6, 1.4),
       (6.3, -6.0, -7.7, 0.85), (6.85, -6.6, -7.05, 0.2)]
POD_Z = -0.35                       # the pods' middle, a little under the fuselage's
POD_POWER = 2.2
# The crescent window in the left pod's top: its outline (inner side, then the outer bow back), how deep it is cut and
# where its floor lies under the cut's rim.
CRESCENT = [(-7.0, 2.95), (-7.45, 1.4), (-7.65, -0.4), (-7.5, -2.3), (-7.05, -4.2), (-6.8, -5.0), (-7.6, -4.4),
            (-8.75, -3.1), (-9.6, -1.4), (-9.85, -0.2), (-9.5, 1.2), (-8.6, 2.5), (-7.6, 3.2)]
CRESCENT_DEPTH = 0.95
# The struts (rows 13-15): their middle (y), radius, how far in and out they reach (x, left side).
STRUT = (-0.45, 1.35, -2.4, -5.2)
# The engine: where its axis leaves the fuselage, its direction (up the screen and up), its radius, its length; the
# share of its rim at the back that is cream.
ENGINE = ((0.0, 4.3, 1.75), (0.0, 0.42, 0.91), 1.7, 1.35)
# The gun's slot along the snout's top (x half-width, y from, y to, depth) and the barrel in it (radius, its ends).
SLOT = (0.95, -8.15, -4.9, 1.05)
BARREL = (0.48, -8.9, -5.1)


def materials():
    pal = k.level_palette()

    def mat(name, index, metallic=0.4, roughness=0.34):
        return k.material(name, palette=index, metallic=metallic, roughness=roughness)

    def lit(name, index, strength, roughness=0.25):
        return k.material(name, palette=index, metallic=0.0, roughness=roughness, emission=pal[index],
                          emission_strength=strength)
    return {
        "hull": mat("pfighter_hull", 0x6a),
        "light": mat("pfighter_light", 0x6c, 0.4, 0.3),
        "dark": mat("pfighter_dark", 0x67, 0.4, 0.4),
        "under": mat("pfighter_under", 0x64, 0.35, 0.45),
        "rim": mat("pfighter_rim", 0x31, 0.3, 0.5),
        "window": lit("pfighter_window", 0x7a, 0.3),
        "window_core": lit("pfighter_window_core", 0x7c, 0.45),
        "cream": lit("pfighter_cream", 0xee, 0.3, 0.3),
        "mouth": mat("pfighter_mouth", 0x03, 0.3, 0.6),
        "slot": mat("pfighter_slot", 0x04, 0.3, 0.55),
        "barrel": mat("pfighter_barrel", 0x0b, 0.7, 0.25),
    }


# --- Hulls ------------------------------------------------------------------------------------------------------------

def hull_rings(table, step=0.35, segments=32, power=2.0):
    """Rings through a smooth curve of the table (y, x of the middle, half-width, z of the middle, above, below),
    closer together at the ends."""
    curve = Curve(table)
    y0, y1 = table[0][0], table[-1][0]
    stations = spaced(y0, y1, max(2, int(round((y1 - y0) / step))) + 1, dense_a=0.35, dense_b=0.35)
    rings = []
    for y in stations:
        xc, hw, zc, top, bottom = curve(y)
        rings.append(k.ring(y, max(hw, 0.03), 1.0, segments, z=zc, x=xc, top=max(top, 0.03), bottom=max(bottom, 0.03),
                            power=power))
    return rings, curve


def fuselage(m):
    table = [(y, 0.0, hw, zc, top, bottom) for y, hw, zc, top, bottom in FUSELAGE]
    rings, curve = hull_rings(table, step=0.42, segments=28)
    y0, y1 = table[0][0], table[-1][0]
    obj = k.loft("fuselage", rings, m["hull"], start_point=(0.0, y0 - 0.05, curve(y0)[2]),
                 end_point=(0.0, y1 + 0.05, curve(y1)[2]))
    k.smooth(obj, 50)
    # The gun's slot along the snout's top.
    hw, s0, s1, depth = SLOT
    top = max(curve(y)[2] + curve(y)[3] for y in (s0, (s0 + s1) / 2, s1))
    cutter = mk.box("slot", -hw, hw, s0, s1, top - depth - 1.2, top + 3.0, m["slot"])
    # its floor follows the snout's top down to the tip
    for v in cutter.data.vertices:
        if v.co.z < top:
            v.co.z = curve(v.co.y)[2] + curve(v.co.y)[3] - depth
    cutter.data.update()
    mk.boolean(obj, cutter, "DIFFERENCE")
    mk.cleanup(obj, dissolve=0.0)
    k.smooth(obj, 50)

    def pick(c, n):
        if abs(c.x) < hw + 0.05 and s0 - 0.05 < c.y < s1 + 0.05 and c.z < curve(c.y)[2] + curve(c.y)[3] - 0.08:
            return m["slot"]
        if n.z < -0.2:
            return m["under"]
        if n.z < 0.35:
            return m["dark"]
        if abs(c.x) < 1.2 and -3.0 < c.y < 3.6:
            return m["light"]                   # the bulb's lit middle (0x6a-0x6d)
        return None
    mk.paint(obj, pick)
    return obj, curve


def pod(m, side):
    """The pod on one side (side -1 left, 1 right): a leaf-shaped hull with the crescent cut into its top."""
    table = []
    for y, x_in, x_out, h in POD:
        xc, hw = (x_in + x_out) / 2, abs(x_in - x_out) / 2
        table.append((y, xc, hw, POD_Z, h, h * 0.8))
    rings, curve = hull_rings(table, step=0.45, segments=28, power=POD_POWER)
    y0, y1 = table[0][0], table[-1][0]
    obj = k.loft("pod_l", rings, m["hull"], start_point=(curve(y0)[0], y0 - 0.05, POD_Z),
                 end_point=(curve(y1)[0], y1 + 0.05, POD_Z))
    k.smooth(obj, 50)
    # The crescent: a prism of its outline, cut down from above to CRESCENT_DEPTH under the pod's top there.
    cutter = mk.prism("crescent", CRESCENT, -5.0, 8.0, m["window"])
    surf = mk.surface([obj])
    for v in cutter.data.vertices:
        if v.co.z < 0:
            hit = surf(v.co.x, v.co.y)
            v.co.z = (hit[0].z if hit else POD_Z + 2.0) - CRESCENT_DEPTH
    cutter.data.update()
    mk.boolean(obj, cutter, "DIFFERENCE")
    mk.cleanup(obj, dissolve=0.0)
    k.smooth(obj, 40)
    inside = [Vector((x, y)) for x, y in CRESCENT]

    def in_crescent(x, y):
        hit = False
        for i in range(len(inside)):
            a, b = inside[i], inside[i - 1]
            if (a.y > y) != (b.y > y) and x < a.x + (y - a.y) * (b.x - a.x) / (b.y - a.y):
                hit = not hit
        return hit

    def pick(c, n):
        if in_crescent(c.x, c.y) and c.z < POD_Z + curve(c.y)[3] - 0.2:
            if n.z > 0.75:
                return m["window_core"] if -2.6 < c.y < 1.4 else m["window"]
            return m["rim"]
        if n.z < -0.2:
            return m["under"]
        if n.z < 0.35:
            return m["dark"]
        return None
    mk.paint(obj, pick)
    if side > 0:
        mirror(obj)
        obj.name = "pod_r"
    return obj


def mirror(obj):
    """Mirrors an object across x = 0 in place, keeping its shading (corner normals) and materials (polish_k_pod.py's
    mirror_y, across x)."""
    mk.apply(obj)
    mesh = obj.data
    corner = {}
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            n = mesh.corner_normals[li].vector
            corner[(poly.index, mesh.loops[li].vertex_index)] = (-n.x, n.y, n.z)
    mesh.transform(Matrix.Scale(-1, 4, (1, 0, 0)))
    mesh.flip_normals()
    normals = [None] * len(mesh.loops)
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            normals[li] = corner[(poly.index, mesh.loops[li].vertex_index)]
    mesh.normals_split_custom_set(normals)
    mesh.update()
    return obj


def struts(m):
    y, r, x0, x1 = STRUT
    out = []
    for i, s in enumerate((-1, 1)):
        bar = mk.tube(f"strut{i}", [(s * x0, y, 0.1), (s * x1, y, POD_Z + 0.1)], r, m["hull"], 16)
        k.smooth(bar, 50)
        mk.paint(bar, lambda c, n: m["dark"] if n.z < 0.1 else None)
        out.append(bar)
    return out


def engine(m, curve):
    """The nozzle at the fuselage's end, turned up and back: a short can, its rim's far half cream, its mouth dark."""
    base, direction, radius, length = ENGINE
    base, d = Vector(base), Vector(direction).normalized()
    up = Vector((0, 0, 1))
    frame_rot = up.rotation_difference(d).to_matrix().to_4x4()   # local +y: towards the back
    lip = 0.32
    profile = [(radius * 0.92, -0.6), (radius, 0.2), (radius * 1.03, length - 0.35), (radius * 0.98, length),
               (radius - lip, length - 0.05), (radius - lip - 0.05, length - 0.7), (0.01, length - 0.75)]
    can = mk.lathe("engine", profile, (0.0, 0.0), m["dark"], 32)
    can.data.transform(Matrix.Translation(base) @ frame_rot)
    k.smooth(can, 45)
    tip = base + d * length

    def pick(c, n):
        # the mouth: inside the rim, its far (back) wall lit cream by the exhaust, the rest of it dark
        local = frame_rot.inverted() @ (c - base)
        r = math.hypot(local.x, local.y)
        if r < radius - lip + 0.02 and local.z > length - 0.8:
            return m["cream"] if local.y > 0.35 * (radius - lip) else m["mouth"]
        if local.z > length - 0.4:
            return m["rim"]                     # the lip, dark (the sprite's navy outline round the engine)
        return None
    mk.paint(can, pick)
    return can


def gun(m, curve):
    r, y0, y1 = BARREL
    _, s0, s1, depth = SLOT
    pts = []
    for i in range(9):
        y = y0 + (y1 - y0) * i / 8
        top = curve(min(max(y, s0), s1))[2] + curve(min(max(y, s0), s1))[3] - depth
        pts.append((0.0, y, top + r * 0.95))
    obj = mk.tube("barrel", pts, r, m["barrel"], 14)
    return k.smooth(obj, 50)


def build():
    options = k.args()
    out = mk.outdir(options)
    k.reset()
    m = materials()
    body, curve = fuselage(m)
    parts = [body, pod(m, -1), pod(m, 1)] + struts(m) + [engine(m, curve), gun(m, curve)]
    parts = triangulate(parts)
    if "stats" in options:
        for obj in parts:
            print("   %-10s %6d triangles" % (obj.name, len(obj.data.polygons)))
    bpy.context.view_layer.update()
    if "check" in options:
        sheet = os.path.join(options["check"], "enemy_L.png")
        mk.compare("yellow_pod_fighter (L 267)", mk.coverage(parts, 24, 28), k.sprite_mask(sheet, 267))
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    mk.report(NAME, parts, os.path.join(out, NAME + ".glb"))
    if "preview" in options:
        mk.preview(options["preview"] + NAME, parts, distance=0.6)


if __name__ == "__main__":
    build()
