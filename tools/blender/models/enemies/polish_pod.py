"""The bronze pod of episode 1 (sheet 2 sprite 159, 2x2: a 16 x 17 pod in the 24 x 28 cell; MINEMAZE,
MINES, TYRIAN, BONUS, WINDY, ASSASSIN, ALE, GAUNTLET, TYRIAN X, MACES, ICESECRET; sky, ground and top
layers), polished (2026-10-18; it replaces pod.py's brown disc with a bar). models.cfg: sprite 2 159
pod, frame 2 161 pod_161, frame 2 163 pod_163, frame 2 165 pod_165, frame 2 167 pod_167.

As the 4x upscale draws it: a round pod (columns 4-19 of rows 7-23), its upper half a dark shell
with bronze knobs (a crest at the top, columns 10-13 of rows 8-10, and a knob on either shoulder,
columns 6-8 and 14-17 of rows 10-11), its lower half a bronze horseshoe (rows 16-22). A grey bar
runs across its middle (rows 12-15), and over it runs a shiny grey visor (columns 9-13 from row 12)
whose lower end holds a dark glass lens (rows 16-19), the horseshoe's arms either side of it.

The animation (159 161 163 165 167 and back) opens the pod: the bar's ends slide out, 9, 10, 11 and
12 pixels from the middle (rows 13-14 reach columns 3-20, 2-21, 1-22, 0-23), bending down a little
as they leave the shell, and from 163 on a red glowing vane rides out under each end, showing above
and below it (the sprite's ramp 7 at the pod's sides, columns 2-4 and 19-21 of rows 11-18 in 167).
One model per frame: pod (159, closed), pod_161 (the bar out a pixel), pod_163, pod_165 and
pod_167. 159 draws the pod a pixel higher up the screen than the others (rows 6-22); so does its
model.

Origin at the sprite's centre (pixel 12, 14); +Y up the sprite, +Z towards the camera. Every frame
reaches the same height (the visor's top) and depth (the shell's bottom), so the game, which centres
sky objects in height, centres them all alike.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <enemy_2.png> (the
silhouette of each frame), --preview <prefix>.
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
import tyrkit as k  # noqa: E402

# The shell: its middle and half-axes in plan (columns 4-19, rows 7-23 in 161-167), the power of its
# plan (a little squarer than an ellipse), its equator's height, its dome above (a superellipse of
# power DOME_POWER, fuller than a sphere) and its bowl below.
CENTRE = (0.0, -1.5)
RADII = (8.0, 8.5)
PLAN_POWER = 2.3
EQUATOR, DOME, BOWL = 4.0, 4.6, 4.0
DOME_POWER = 2.5
SEGMENTS = 56
# The horseshoe on the shell's lower half (rows 16-22): its arms run down from under the bar at
# x = +-U_ARM to U_TURN, then round an elliptic bend U_BEND deep; its half-width and half-height.
U_ARM, U_TOP, U_TURN, U_BEND = 5.0, -1.3, -4.3, 3.2
U_HALF, U_THICK = 1.9, 0.85
# The bar (rows 12-15): half its height in plan, half its thickness, its axis' height in the middle
# and how it bends down towards its ends (z = BAR_Z - BAR_SAG x^2), the length of its rounded ends.
BAR_HALF, BAR_THICK, BAR_Z, BAR_SAG, BAR_CAP = 1.9, 1.25, 8.0, 0.028, 1.6
# The visor (columns 9-13, rows 12-19): in plan a stadium round the segment from VISOR_ENDS[0] down
# to VISOR_ENDS[1] (x VISOR_X), VISOR_RADIUS wide either side; its half-height, and the height of
# its middle line along it (y, z), from its top end down, rising over the bar.
VISOR_X, VISOR_ENDS, VISOR_RADIUS, VISOR_THICK = -0.4, (0.4, -4.0), 2.6, 0.95
VISOR_LINE = [(-6.8, 7.9), (-5.9, 8.5), (-4.8, 8.85), (-3.6, 9.0), (-2.4, 9.15), (-1.2, 9.4), (0.0, 9.5),
              (1.2, 9.4), (2.2, 8.95), (2.9, 8.45)]
LENS = (-4.0, (2.3, 2.15, 0.8))    # the lens: its middle on the visor (y), radii
# The knobs on the dark shell (rows 8-11): middle (x, y), radii (x, y, height above the shell).
KNOBS = [((0.0, 4.8), (1.7, 1.9, 0.8)), ((-4.8, 3.0), (1.5, 1.15, 0.7)), ((4.3, 3.0), (1.5, 1.15, 0.7))]
# The red vane under each end of the bar, a kite in plan (offsets from the bar's tip, inwards and up
# the screen, when fully out): its tip, upper, inner and lower corners; its thickness, the rounding of
# its corners and top edge, its top's height above the bar's underside. Part way out (163, 165) it
# is smaller (VANE_SHRINK: its size along and across the bar just out, fractions of the full size)
# and lower (by VANE_SINK just out).
VANE = [(0.6, -0.3), (3.6, 4.0), (7.0, -0.8), (4.3, -5.7)]
VANE_THICK, VANE_CORNER, VANE_ROUND, VANE_ABOVE = 1.9, 1.0, 0.6, 1.75
VANE_SHRINK, VANE_SINK = (0.6, 0.5), 1.0

# The frames: (model, sprite, the shift up the screen, how far the bar reaches, how far the vanes are
# out (0-1) or None).
FRAMES = [
    ("pod", 159, 1.0, 7.6, None),
    ("pod_161", 161, 0.0, 9.0, None),
    ("pod_163", 163, 0.0, 10.0, 0.3),
    ("pod_165", 165, 0.0, 11.0, 0.7),
    ("pod_167", 167, 0.0, 12.0, 1.0),
]


def plan_point(theta, scale):
    c, s = math.cos(theta), math.sin(theta)
    return (CENTRE[0] + scale * RADII[0] * math.copysign(abs(c) ** (2 / PLAN_POWER), c),
            CENTRE[1] + scale * RADII[1] * math.copysign(abs(s) ** (2 / PLAN_POWER), s))


def plan_radius(x, y):
    """0 at the shell's middle, 1 on its outline."""
    return ((abs(x - CENTRE[0]) / RADII[0]) ** PLAN_POWER +
            (abs(y - CENTRE[1]) / RADII[1]) ** PLAN_POWER) ** (1 / PLAN_POWER)


def shell_top(x, y):
    """The dome's height at (x, y) (the equator's outside it)."""
    r = min(1.0, plan_radius(x, y))
    return EQUATOR + DOME * (1 - r ** DOME_POWER) ** (1 / DOME_POWER)


def visor_z(y):
    """The height of the visor's middle line at y."""
    for (y0, z0), (y1, z1) in zip(VISOR_LINE, VISOR_LINE[1:]):
        if y0 <= y <= y1:
            return z0 + (z1 - z0) * (y - y0) / (y1 - y0)
    return VISOR_LINE[0][1] if y < VISOR_LINE[0][0] else VISOR_LINE[-1][1]


def bar_z(x):
    return BAR_Z - BAR_SAG * x * x


def shell(mats):
    """The shell: rings in plan from the bowl's bottom over the equator to the dome's top; dark, its
    upper half nearly black, its lower half (under the horseshoe and the lens) a dark bronze."""
    rings = []
    for i in range(1, 6):  # the bowl, from its bottom up (a quarter ellipse)
        a = (math.pi / 2) * i / 6
        rings.append((math.sin(a), EQUATOR - BOWL * math.cos(a)))
    for i in range(0, 14):  # the dome, from the equator up
        a = (math.pi / 2) * i / 14
        rings.append((math.cos(a) ** (2 / DOME_POWER), EQUATOR + DOME * math.sin(a) ** (2 / DOME_POWER)))
    verts = [[Vector((*plan_point(2 * math.pi * j / SEGMENTS, scale), z)) for j in range(SEGMENTS)]
             for scale, z in rings]
    obj = k.loft("shell", verts, None, start_point=(CENTRE[0], CENTRE[1], 0.0),
                 end_point=(CENTRE[0], CENTRE[1], EQUATOR + DOME))
    obj.data.materials.append(mats["dark"])
    obj.data.materials.append(mats["under"])
    for poly in obj.data.polygons:
        c = poly.center
        poly.material_index = 1 if c.z < EQUATOR - 0.05 or c.y < 0.0 else 0
    return k.smooth(obj, 50)


def horseshoe(mats):
    """The bronze horseshoe lying on the shell's lower half: rounded cross-sections along a U."""
    path = [Vector((-U_ARM, U_TOP + (U_TURN - U_TOP) * i / 5)) for i in range(6)]
    path += [Vector((U_ARM * math.cos(a), U_TURN + U_BEND * math.sin(a)))
             for a in (math.pi + math.pi * i / 20 for i in range(1, 20))]
    path += [Vector((U_ARM, U_TURN + (U_TOP - U_TURN) * i / 5)) for i in range(6)]
    rings = []
    for i, p in enumerate(path):
        t = (path[min(i + 1, len(path) - 1)] - path[max(i - 1, 0)]).normalized()
        across = Vector((-t.y, t.x, 0.0))
        z = shell_top(p.x, p.y) + 0.1
        ring = []
        for j in range(16):
            a = 2 * math.pi * j / 16
            c, sn = math.cos(a), math.sin(a)
            ring.append(Vector((p.x, p.y, z)) + across * U_HALF * math.copysign(abs(c) ** (2 / 2.4), c) +
                        Vector((0.0, 0.0, U_THICK * math.copysign(abs(sn) ** (2 / 2.4), sn))))
        rings.append(ring)
    obj = k.loft("horseshoe", rings, mats["bronze"])
    return k.smooth(obj, 50)


def bar(reach, mats):
    """The bar across the pod: superellipse cross-sections square to its bending axis, its ends
    rounded."""
    straight = reach - BAR_CAP
    xs = [-straight + 2 * straight * i / 16 for i in range(17)]
    caps = [straight + BAR_CAP * math.sin((math.pi / 2) * i / 6) for i in range(1, 6)]
    xs = sorted(set([-c for c in caps] + xs + caps))
    rings = []
    for x in xs:
        t = max(0.0, (abs(x) - straight) / BAR_CAP)
        s = max(0.0, 1 - t * t) ** 0.8
        slope = -2 * BAR_SAG * x
        normal = Vector((-slope, 0.0, 1.0)).normalized()
        centre = Vector((x, 0.0, bar_z(x)))
        ring = []
        for j in range(16):
            a = 2 * math.pi * j / 16
            c, sn = math.cos(a), math.sin(a)
            across = BAR_HALF * s * math.copysign(abs(c) ** (2 / 2.6), c)
            up = BAR_THICK * (0.3 + 0.7 * s) * math.copysign(abs(sn) ** (2 / 2.6), sn)
            ring.append(centre + Vector((0.0, across, 0.0)) + normal * up)
        rings.append(ring)
    obj = k.loft("bar", rings, None, start_point=(-reach, 0.0, bar_z(reach)), end_point=(reach, 0.0, bar_z(reach)))
    obj.data.materials.append(mats["bar"])
    obj.data.materials.append(mats["bar_end"])
    for poly in obj.data.polygons:  # its tips light grey once they are out of the shell
        poly.material_index = 1 if reach > 8.5 and abs(poly.center.x) > straight - 0.5 else 0
    return k.smooth(obj, 50)


def visor(mats):
    """The visor: elliptic cross-sections along its middle line, its ends rounded."""
    y0, y1 = VISOR_ENDS[1] - VISOR_RADIUS, VISOR_ENDS[0] + VISOR_RADIUS
    ys = [y0 + (y1 - y0) * (1 - math.cos(math.pi * i / 22)) / 2 for i in range(1, 22)]
    rings = []
    for y in ys:
        sy = min(VISOR_ENDS[0], max(VISOR_ENDS[1], y))
        w = math.sqrt(max(0.0, VISOR_RADIUS ** 2 - (y - sy) ** 2))
        rings.append(k.ring(y, w, VISOR_THICK * (w / VISOR_RADIUS) ** 0.5, 18, z=visor_z(y), x=VISOR_X))
    obj = k.loft("visor", rings, mats["visor"], start_point=(VISOR_X, y0, visor_z(y0)),
                 end_point=(VISOR_X, y1, visor_z(y1)))
    return k.smooth(obj, 60)


def vane(name, tip_x, side, out, mats):
    """A red vane under the bar's end at tip_x (side -1 left, 1 right), out (0-1) of the shell: a kite
    in plan with a rounded top, glowing hottest on top."""
    sx = VANE_SHRINK[0] + (1 - VANE_SHRINK[0]) * out
    sy = VANE_SHRINK[1] + (1 - VANE_SHRINK[1]) * out
    corners = [Vector((side * (tip_x - dx * sx), dy * sy)) for dx, dy in VANE]
    if side < 0:
        corners.reverse()  # counter-clockwise seen from above
    centre = sum(corners, Vector((0.0, 0.0))) / 4
    x_mid = side * (tip_x - 3.6 * sx)
    z1 = bar_z(x_mid) - BAR_THICK + VANE_ABOVE - VANE_SINK * (1 - out)
    z0 = z1 - VANE_THICK
    outline = []
    for i in range(4):  # the kite's corners rounded
        p0, p1, p2 = corners[i - 1], corners[i], corners[(i + 1) % 4]
        r = VANE_CORNER * min(sx, sy)
        a, b = p1 + (p0 - p1).normalized() * r, p1 + (p2 - p1).normalized() * r
        outline += [a * (1 - u) ** 2 + p1 * 2 * (1 - u) * u + b * u * u for u in (0.0, 0.25, 0.5, 0.75, 1.0)]
    rings = [[Vector((p.x, p.y, z0)) for p in outline], [Vector((p.x, p.y, z1 - VANE_ROUND)) for p in outline]]
    for i in range(1, 4):  # the rounded top edge
        a = (math.pi / 2) * i / 3
        inset = VANE_ROUND * (1 - math.cos(a))
        rings.append([Vector((*(p + (centre - p).normalized() * inset), z1 - VANE_ROUND + VANE_ROUND * math.sin(a)))
                      for p in outline])
    edge = rings[-1]
    for f in (0.65, 0.3):  # the top, a little domed
        rings.append([Vector((*centre.lerp(p.to_2d(), f), z1 + 0.25 * (1 - f * f))) for p in edge])
    obj = k.loft(name, rings, None, start_point=(centre.x, centre.y, z0), end_point=(centre.x, centre.y, z1 + 0.25))
    for m in (mats["vane_side"], mats["vane"], mats["vane_hot"]):
        obj.data.materials.append(m)
    for poly in obj.data.polygons:
        z = poly.center.z
        poly.material_index = 2 if z > z1 - 0.05 else 1 if z > z1 - VANE_ROUND - 0.1 else 0
    return k.smooth(obj, 50)


def build_pod(dy, reach, vanes, mats):
    shell(mats)
    horseshoe(mats)
    bar(reach, mats)
    visor(mats)
    ly, radii = LENS
    k.smooth(k.ellipsoid("lens", (VISOR_X, ly, visor_z(ly) + VISOR_THICK * 0.55), radii, mats["lens"], 20, 10), 60)
    for i, ((x, y), (rx, ry, h)) in enumerate(KNOBS):
        z = shell_top(x, y)
        k.smooth(k.ellipsoid(f"knob{i}", (x, y, z - 0.3), (rx, ry, h + 0.3), mats["knob"], 16, 8), 60)
    if vanes is not None:
        for side in (-1, 1):
            vane(f"vane{side}", reach, side, vanes, mats)
    if dy:
        for obj in bpy.context.scene.objects:
            if obj.type == "MESH":
                obj.data.transform(Matrix.Translation((0.0, dy, 0.0)))


def materials():
    glow = k.level_palette()
    return {
        "dark": k.material("pod_shell", palette=0x02, metallic=0.5, roughness=0.3),
        "bronze": k.material("pod_bronze", palette=0x16, metallic=0.45, roughness=0.3),
        "under": k.material("pod_under", palette=0x11, metallic=0.4, roughness=0.4),
        "bar": k.material("pod_bar", palette=0x07, metallic=0.6, roughness=0.3),
        "bar_end": k.material("pod_bar_end", palette=0x08, metallic=0.6, roughness=0.25),
        "visor": k.material("pod_visor", palette=0x08, metallic=0.75, roughness=0.14),
        "lens": k.material("pod_lens", palette=0x12, metallic=0.0, roughness=0.06),
        "knob": k.material("pod_knob", palette=0x18, metallic=0.55, roughness=0.3),
        "vane_side": k.material("pod_vane_side", palette=0x72, roughness=0.45, emission=glow[0x72],
                                emission_strength=0.3),
        "vane": k.material("pod_vane", palette=0x74, roughness=0.35, emission=glow[0x74], emission_strength=0.7),
        "vane_hot": k.material("pod_vane_hot", palette=0x76, roughness=0.3, emission=glow[0x76],
                               emission_strength=1.1),
    }


def triangles():
    depsgraph = bpy.context.evaluated_depsgraph_get()
    total = 0
    for obj in bpy.context.scene.objects:
        if obj.type == "MESH":
            evaluated = obj.evaluated_get(depsgraph)
            mesh = evaluated.to_mesh()
            mesh.calc_loop_triangles()
            total += len(mesh.loop_triangles)
            evaluated.to_mesh_clear()
    return total


def bounds():
    zs = [(obj.matrix_world @ v.co).z for obj in bpy.context.scene.objects if obj.type == "MESH"
          for v in obj.data.vertices]
    return min(zs), max(zs)


def build():
    options = k.args()
    outdir = options.get("outdir", os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "enemies"))
    for name, sprite, dy, reach, vanes in FRAMES:
        k.reset()
        build_pod(dy, reach, vanes, materials())
        used = {m.name for obj in bpy.context.scene.objects if obj.type == "MESH" for m in obj.data.materials}
        print("== %s (2 %d): %d triangles, %d materials, z %.2f to %.2f" % (name, sprite, triangles(), len(used),
                                                                           *bounds()))
        if "check" in options:
            k.check_silhouette(options["check"], sprite)
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        path = os.path.join(outdir, name + ".glb")
        k.export(path)
        print("%s: %d bytes" % (path, os.path.getsize(path)))
        if "preview" in options:
            k.preview(options["preview"] + name)


if __name__ == "__main__":
    build()
