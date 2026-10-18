"""The steel missile of ASTEROID1, HOLES and AST ROCK (sheet D sprite 77, 2x2: a 13 x 25 missile in the
24 x 28 cell; ground, top and sky layers, 116 of them; not animated), polished (2026-10-18; it
replaces rounds.py's missile(), a grey lump with pink fins). models.cfg: sprite d 77 missile yaw=0.

As the 4x upscale draws it: a polished steel missile lying along the screen, its nose down the
screen. At the top of the sprite its rear, a rounded cap (rows 3-8, columns 6-18), then a dark
groove round it (rows 8-9), a lip (row 10) and a narrower polished neck (rows 11-12, columns
7-17); below them the body (rows 13-18, columns 6-18), whose lower end rounds in (rows 19-22)
round a red warhead (ramp 4): an ogive coming out of the steel at rows 20-22, a dark seam round it,
and drawn to a point at row 27, column 12. The sprite has no fins; nor has the model.

The sprite draws the steel as chrome: a bright stripe left of the middle (column 10), a dark one
right of it (column 15) and a lighter rim beyond that, along the whole missile, and the same dark
stripe (ramp 10) down the glossy warhead. A straight cylinder along the screen catches no
highlight from the game's sun (from above and the top left) and the game's sky reflections are
dim, so the model carries these reflections painted on, in bands round its axis (the angle from
straight up, as REFLECTIONS lists them).

Origin at the sprite's centre (pixel 12, 14); +Y up the sprite, +Z towards the camera. The axis
runs along Y at x = 0.5 (the sprite's middle, column 12) and z = 6.55 (its widest radius): the
missile lies on z = 0.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the
silhouette against enemy_D.png), --preview <prefix>.
"""
import math
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
import tyrkit as k  # noqa: E402

AXIS_X, AXIS_Z = 0.5, 6.55
MAX_STEP = 9.0  # degrees between the points round the axis (more where bands meet)

# The steel's profile, (y, radius), from the lip round the warhead (y -7.8) to the rear cap's top
# (y 11): each sprite row r spans y 13 - r to 14 - r, and the radius is the row's half-width.
STEEL = [
    (-7.8, 3.85), (-7.75, 4.2), (-7.6, 4.5), (-7.3, 4.78),                    # the lip round the warhead
    (-6.8, 5.1), (-6.2, 5.45), (-5.6, 5.8), (-5.0, 6.1),                      # the lower end, rounding in
    (-4.6, 6.33), (-4.3, 6.5),
    (-2.5, 6.55), (-0.6, 6.55), (0.45, 6.5),                                  # the body (rows 13-18)
    (0.7, 6.42), (0.9, 6.15), (1.1, 5.72), (1.3, 5.52),                       # the shoulder down to the neck
    (2.0, 5.5), (2.7, 5.52),                                                  # the neck (rows 11-12)
    (2.9, 5.72), (3.1, 6.2), (3.3, 6.45), (3.5, 6.52),                        # up to the lip (row 10)
    (3.85, 6.52), (4.05, 6.32), (4.25, 6.08), (4.6, 6.04), (5.0, 6.04),       # the groove (rows 8-9)
    (5.25, 6.1), (5.5, 6.33), (5.75, 6.5),
    (6.4, 6.55), (7.2, 6.52), (7.8, 6.38), (8.4, 6.05), (9.0, 5.55),          # the cap (rows 3-8)
    (9.5, 4.95), (9.95, 4.25), (10.35, 3.45), (10.65, 2.6), (10.85, 1.75),
    (10.97, 0.9), (11.02, 0.0),
]
SEAM, GROOVE = (-8.0, -7.45), (4.0, 5.55)  # the dark seam round the warhead, the groove (y from, to)
SEAM_INDEX = 0x02

# The warhead's ogive, (y, radius), from its point (row 27) to inside the steel (it shows from row 20).
WARHEAD = [
    (-13.95, 0.0), (-13.75, 0.32), (-13.4, 0.72), (-12.9, 1.28), (-12.3, 1.88), (-11.6, 2.5), (-10.8, 3.1),
    (-10.0, 3.62), (-9.2, 4.0), (-8.4, 4.3), (-7.6, 4.42), (-6.9, 4.3), (-6.4, 3.9), (-6.4, 0.0),
]

# The painted reflections: (the angle round the axis where the band ends, degrees from straight up,
# negative to the left; the steel's, the groove's and the warhead's palette indices), from the left.
# Read from the sprite's columns 6-18 (column c at asin((c - 12) / 6.5) on the body's rows 13-18):
# the bright stripe in column 10, the dark one in column 15 and the light rim in columns 16-17. The
# game's sun shades the rest (the left side lit, the right darker).
REFLECTIONS = [
    (-40, 0x08, 0x04, 0x46),
    (-30, 0x09, 0x06, 0x48),
    (-22, 0x0b, 0x06, 0x4a),
    (-12, 0x0d, 0x06, 0x4a),
    (-3, 0x0b, 0x06, 0x48),
    (6, 0x08, 0x04, 0x48),
    (14, 0x06, 0x04, 0x46),
    (32, 0x04, 0x02, 0xa4),
    (40, 0x07, 0x04, 0x46),
    (57, 0x0b, 0x04, 0x46),
    (180, 0x06, 0x04, 0x45),
]


def materials():
    """The palette materials by index: steel, the warhead's paint and the dark seam."""
    mats = {}
    for _, steel, groove, paint in REFLECTIONS:
        for index in (steel, groove, SEAM_INDEX):
            if index not in mats:
                mats[index] = k.material(f"missile_steel_{index:x}", palette=index, metallic=0.25, roughness=0.24)
        if paint not in mats:
            mats[paint] = k.material(f"missile_paint_{paint:x}", palette=paint, metallic=0.1, roughness=0.26)
    return mats


def angles():
    """The points round the axis: angles from straight up (degrees, positive towards +X, the right of
    the screen), every band's border among them."""
    borders = sorted({-180.0} | {float(end) for end, *_ in REFLECTIONS if end < 180})
    out = []
    for a, b in zip(borders, borders[1:] + [180.0]):
        steps = max(1, math.ceil((b - a) / MAX_STEP))
        out += [a + (b - a) * i / steps for i in range(steps)]
    return out


def band(angle):
    for i, (end, *_) in enumerate(REFLECTIONS):
        if angle < end:
            return i
    return len(REFLECTIONS) - 1


def lathe(name, profile, pick):
    """A part turned round the missile's axis from (y, radius) points in increasing y (no smoothing
    between them; an end of radius 0 is closed by a fan to the axis, another left open). Each face
    gets the material pick(y, angle) for the middle of its band and its angle round the axis."""
    around = angles()
    n = len(around)
    start = profile[0][1] <= 0
    end = profile[-1][1] <= 0
    inner = profile[1 if start else 0:len(profile) - 1 if end else len(profile)]
    rings = [[Vector((AXIS_X + r * math.sin(math.radians(a)), y, AXIS_Z + r * math.cos(math.radians(a))))
              for a in around] for y, r in inner]
    obj = k.loft(name, rings, None, cap_start=start, cap_end=end,
                 start_point=(AXIS_X, profile[0][0], AXIS_Z), end_point=(AXIS_X, profile[-1][0], AXIS_Z))
    # The loft's faces come band by band (n faces between rings i and i + 1), then the fans.
    bands = len(inner) - 1
    names = []
    for poly in obj.data.polygons:
        row, j = divmod(poly.index, n)
        if row < bands:
            y = (inner[row][0] + inner[row + 1][0]) / 2
        elif start and row == bands:
            y = (profile[0][0] + inner[0][0]) / 2
        else:
            y = (inner[-1][0] + profile[-1][0]) / 2
        a0, a1 = around[j], around[(j + 1) % n] + (360.0 if j + 1 == n else 0.0)
        mat = pick(y, (a0 + a1) / 2)
        if mat.name not in names:
            names.append(mat.name)
            obj.data.materials.append(mat)
        poly.material_index = names.index(mat.name)
    k.recalc_normals(obj)
    return obj


def build_missile(mats):
    def steel(y, angle):
        _, metal, groove, _ = REFLECTIONS[band(angle)]
        if SEAM[0] < y < SEAM[1]:
            return mats[SEAM_INDEX]
        return mats[groove if GROOVE[0] < y < GROOVE[1] else metal]

    body = lathe("steel", STEEL, steel)
    k.smooth(body, 38)
    head = lathe("warhead", WARHEAD, lambda y, angle: mats[REFLECTIONS[band(angle)][3]])
    k.smooth(head, 50)
    return body, head


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


def build():
    options = k.args()
    outdir = options.get("outdir", os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "enemies"))
    k.reset()
    build_missile(materials())
    used = {m.name for obj in bpy.context.scene.objects if obj.type == "MESH" for m in obj.data.materials}
    print("== missile (D 77): %d triangles, %d materials" % (triangles(), len(used)))
    if "check" in options:
        sheet = options["check"]
        k.check_silhouette(os.path.join(sheet, "enemy_D.png") if os.path.isdir(sheet) else sheet, 77)
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    path = os.path.join(outdir, "missile.glb")
    k.export(path)
    print("%s: %d bytes" % (path, os.path.getsize(path)))
    if "preview" in options:
        k.preview(options["preview"] + "missile")


if __name__ == "__main__":
    build()
