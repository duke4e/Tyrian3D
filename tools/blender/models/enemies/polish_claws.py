"""SAVARA's twin red claws (sheet F sprite 169, 2x2: two claws side by side, each 10 x 23 pixels in the
24 x 28 cell; static; ground (SAVARA, SAVARA IV, V and Y: enemy 500, drifting down the water) and sky
(MINEMAZE, MINES, TYRIAN, WINDY, GAUNTLET, TYRIAN X, MACES)), polished (2026-10-18; it replaces
misc.py's claws(), two lathed dumbbells with spikes). models.cfg: sprite f 169 claws yaw=0.

As the 4x upscale draws them: two identical crab claws (the right one the left one moved 12 pixels,
not mirrored), pointing up the screen, glossy salmon-red shells (the sprite's ramp 4). Each claw:
two fingers at the top (columns 3-5 and 6-9 of rows 4-8 for the left claw), their tips apart, the
outer one lit, the inner darker; the palm below (columns 1-11 of rows 8-15), its two halves bulging
either side of a dark groove that runs down from between the fingers, the outer edge catching the
light; a narrower wrist (columns 3-9 of rows 15-22) with a grey-violet band round it (rows 17-18,
the sprite's ramp 5); and a rounded knuckle at the bottom (columns 2-10 of rows 22-26) with two
light knobs (columns 3-4 and 8-9 of rows 23-24).

Each claw is a loft along the screen through cross-sections that are unions of lobes (tyrkit's
lobed_ring: the palm's two halves and their outer ridges, the wrist's and the knuckle's round
middle, the knuckle's two knobs), so that the creases between them show; the groove where the
palm's halves meet is painted dark along the crease (cut in along smooth borders). Two tapered
fingers (lofts along their axes) grow out of the palm's halves, and a band rings the wrist. The
claw is built once about its own middle line (column 6 of the sprite for the left claw) and placed
at x -6 and x +6. The shell is glossy, its colour the sprite's lit salmon-red; the game's light
darkens its sides as the sprite's outline does.

Origin at the sprite's centre (pixel 12, 14); +Y up the sprite, +Z towards the camera.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <dir with enemy_F.png,
or the sheet itself> (the silhouette), --preview <prefix>.
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
from polish_sphere_nozzle import split_along  # noqa: E402

CLAW_X = (-6.0, 6.0)  # the claws' middle lines (columns 6 and 18 of the sprite)
SEGMENTS = 36


def y_of(row):
    return 14.0 - row


# The body's cross-sections from the knuckle's end (row 26.45) up to the palm's top (row 8.3):
# (row, {lobe: (x, z, half-width, height above, depth below)}) about the claw's middle line: the
# knuckle's and wrist's round middle "C", the knuckle's knobs "KL" and "KR", the palm's halves "L"
# (outer, the thumb side) and "R" (the inner finger's side) and their outer ridges "OL" and "OR".
# A lobe missing from a section has no size there (lobes grow from and shrink to nothing inside the
# others, where the size is given as 0).
SECTIONS = [
    (26.45, {"C": (0.0, 0.0, 1.5, 1.2, 1.0)}),
    (26.0, {"C": (0.0, 0.0, 2.45, 1.75, 1.4), "KL": (-1.2, 0.1, 0.0, 0.0, 0.0), "KR": (1.2, 0.1, 0.0, 0.0, 0.0)}),
    (25.3, {"C": (0.0, 0.0, 3.3, 2.1, 1.75), "KL": (-2.0, 0.2, 1.1, 1.7, 1.2), "KR": (2.0, 0.2, 1.05, 1.6, 1.2)}),
    (24.4, {"C": (0.0, 0.0, 3.75, 2.2, 2.0), "KL": (-2.3, 0.3, 1.5, 2.35, 1.4), "KR": (2.25, 0.3, 1.45, 2.25, 1.4)}),
    (23.5, {"C": (0.0, 0.0, 3.6, 2.2, 1.95), "KL": (-2.3, 0.3, 1.45, 2.3, 1.4), "KR": (2.25, 0.3, 1.4, 2.2, 1.4)}),
    (22.7, {"C": (0.0, 0.0, 3.05, 2.05, 1.75), "KL": (-1.9, 0.2, 0.9, 1.6, 1.1), "KR": (1.9, 0.2, 0.85, 1.5, 1.1)}),
    (22.0, {"C": (0.0, 0.0, 2.7, 1.95, 1.65), "KL": (-1.2, 0.1, 0.0, 0.0, 0.0), "KR": (1.2, 0.1, 0.0, 0.0, 0.0)}),
    (20.0, {"C": (0.0, 0.0, 2.75, 2.0, 1.65)}),
    (18.2, {"C": (0.0, 0.0, 2.85, 2.1, 1.7)}),
    (16.7, {"C": (0.0, 0.0, 3.0, 2.25, 1.8), "L": (-1.1, 0.1, 1.9, 1.9, 1.5), "R": (1.15, 0.1, 1.85, 1.8, 1.5),
            "OL": (-2.3, 0.1, 0.0, 0.0, 0.0), "OR": (2.3, 0.1, 0.0, 0.0, 0.0)}),
    (15.6, {"C": (0.0, 0.0, 3.1, 2.35, 1.9), "L": (-1.6, 0.2, 2.6, 2.45, 1.9), "R": (1.65, 0.2, 2.5, 2.3, 1.9),
            "OL": (-3.4, 0.2, 1.0, 1.5, 1.3), "OR": (3.45, 0.2, 0.95, 1.4, 1.3)}),
    (14.6, {"C": (0.0, 0.0, 2.6, 2.2, 1.9), "L": (-1.75, 0.3, 2.35, 2.8, 2.1), "R": (1.85, 0.3, 2.3, 2.6, 2.1),
            "OL": (-3.75, 0.3, 1.3, 2.05, 1.6), "OR": (3.8, 0.3, 1.25, 1.9, 1.6)}),
    (12.2, {"C": (0.0, 0.0, 2.0, 2.0, 1.9), "L": (-1.75, 0.3, 2.15, 2.95, 2.2), "R": (1.85, 0.3, 2.1, 2.7, 2.15),
            "OL": (-3.85, 0.3, 1.3, 2.25, 1.7), "OR": (3.85, 0.3, 1.25, 2.05, 1.7)}),
    (9.7, {"L": (-1.8, 0.3, 2.1, 2.8, 2.1), "R": (1.85, 0.3, 2.05, 2.55, 2.05),
           "OL": (-3.75, 0.3, 1.3, 2.0, 1.6), "OR": (3.75, 0.3, 1.25, 1.85, 1.6)}),
    (8.9, {"L": (-1.85, 0.3, 2.05, 2.5, 1.9), "R": (1.9, 0.3, 1.95, 2.3, 1.85),
           "OL": (-3.2, 0.3, 0.9, 1.5, 1.2), "OR": (3.2, 0.3, 0.85, 1.4, 1.2)}),
    (8.3, {"L": (-1.85, 0.3, 1.9, 2.2, 1.75), "R": (1.85, 0.3, 1.85, 2.0, 1.7),
           "OL": (-2.6, 0.3, 0.0, 0.0, 0.0), "OR": (2.6, 0.3, 0.0, 0.0, 0.0)}),
]
LOBES = ("C", "L", "R", "OL", "OR", "KL", "KR")
# The dark groove down the palm, painted along the crease on top between its halves (L, R; the
# sprite's dark column 6): (lobe pair, half-width). Only creases above GROOVE_MIN_Z count (the top,
# not the underside). (The creases between the halves and the outer ridges are left to the light:
# painted, they broke up where the loft's points straddle them.)
GROOVES = [((1, 2), 0.34)]
GROOVE_MIN_Z = 1.0
BODY_END = (26.7, 8.05)  # the knuckle's end and the palm's top (rows)
# The fingers: (axis points (x, row) from inside the palm up to the tip, radius at each), growing
# out of the palm's halves.
FINGERS = [
    ([(-1.85, 10.0), (-1.85, 8.2), (-1.6, 6.8), (-1.6, 5.5), (-1.75, 4.6), (-1.75, 3.95)],
     [2.0, 1.85, 1.45, 1.0, 0.55, 0.12], "outer"),
    ([(1.85, 10.0), (1.85, 8.2), (1.6, 6.8), (1.65, 5.5), (1.7, 4.7), (1.55, 4.15)],
     [1.9, 1.75, 1.45, 1.0, 0.55, 0.12], "inner"),
]
FINGER_Z, FINGER_SQUASH = 0.45, 0.8
BAND = (17.85, 0.62, 0.32)  # the band round the wrist: its middle row, half its length, how far it stands out


def lerp_lobe(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(5))


def section_at(row):
    """The lobes at a row, interpolated between SECTIONS (smoothly: a cosine ease)."""
    for (r0, l0), (r1, l1) in zip(SECTIONS, SECTIONS[1:]):
        if r1 <= row <= r0:
            t = (r0 - row) / (r0 - r1)
            t = 0.5 - 0.5 * math.cos(math.pi * t)
            lobes = []
            for key in LOBES:  # all of them, in this order, so that each keeps its index
                a = l0.get(key)
                b = l1.get(key)
                if a is None and b is None:
                    a = b = (0.0, 0.0, 0.0, 0.0, 0.0)
                if a is None:
                    a = (b[0], b[1], 0.0, 0.0, 0.0)
                if b is None:
                    b = (a[0], a[1], 0.0, 0.0, 0.0)
                lobes.append(lerp_lobe(a, b, t))
            return lobes
    raise ValueError(row)


def body(mats):
    """The claw's body: lobed cross-sections from the knuckle up to the palm's top, the groove
    painted along the crease between the palm's halves."""
    rows = []
    r = SECTIONS[0][0]
    while r > SECTIONS[-1][0] + 1e-6:
        rows.append(r)
        r -= 0.45
    rows.append(SECTIONS[-1][0])
    rings, creases = [], {pair: [] for pair, _ in GROOVES}
    for row in rows:
        c = []
        rings.append(k.lobed_ring(y_of(row), section_at(row), SEGMENTS, origin_z=0.2, creases=c))
        for pair in creases:
            top = [p for q, p in c if q == pair and p.z > GROOVE_MIN_Z]
            creases[pair].append(max(top, key=lambda p: p.z) if top else None)
    obj = k.loft("claw_body", rings, mats["shell"], start_point=(0.0, y_of(BODY_END[0]), 0.0),
                 end_point=(0.0, y_of(BODY_END[1]), 0.5))
    paint_grooves(obj, [(longest_run(creases[pair]), width) for pair, width in GROOVES], mats)
    return [k.smooth(obj, 50)]


def longest_run(points):
    """The longest unbroken run of rings that have a crease point."""
    runs, run = [], []
    for p in points:
        if p is None:
            if run:
                runs.append(run)
            run = []
        else:
            run.append(p)
    if run:
        runs.append(run)
    return max(runs, key=len)


def paint_grooves(obj, lines, mats):
    """Paints the grooves: the faces on top within each line's half-width of it (in plan), cut
    along smooth borders first; the lines' ends taper."""
    def distance(v, line, width):
        if v.co.z < GROOVE_MIN_Z - 0.3:
            return 9.0
        best = 9.0
        for i, (a, b) in enumerate(zip(line, line[1:])):
            ab = (b - a).to_2d()
            t = max(0.0, min(1.0, (v.co.to_2d() - a.to_2d()).dot(ab) / max(ab.length_squared, 1e-9)))
            d = (v.co.to_2d() - (a.to_2d() + ab * t)).length
            # Narrower towards the ends (over the last 3 rings).
            along = min(i + t, len(line) - 1 - i - t)
            best = min(best, d / (width * min(1.0, 0.25 + along / 3.0)))
        return best

    bm = bmesh.new()
    bm.from_mesh(obj.data)
    fields = []
    for line, width in lines:
        field = {v: distance(v, line, width) for v in bm.verts}
        split_along(bm, field, 1.0)
        for v in bm.verts:  # the vertices the split made
            if v not in field:
                field[v] = distance(v, line, width)
        fields.append(field)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    for f in bm.faces:
        dark = any(sum(field.get(v, 9.0) for v in f.verts) / len(f.verts) < 1.0 for field in fields)
        f.material_index = 1 if dark else 0
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.materials.append(mats["groove"])


def finger(name, points, radii, mats):
    path = [Vector((x, y_of(r), FINGER_Z)) for x, r in points]
    # A smooth axis through the points, and the radius along it.
    dense, dradii = [], []
    for i in range(len(path) - 1):
        for s in range(6):
            t = s / 6
            dense.append(path[i].lerp(path[i + 1], t))
            dradii.append(radii[i] + (radii[i + 1] - radii[i]) * t)
    dense.append(path[-1])
    dradii.append(radii[-1])
    rings = []
    for i, p in enumerate(dense):
        a, b = dense[max(i - 1, 0)], dense[min(i + 1, len(dense) - 1)]
        tangent = (b - a).normalized()
        side = tangent.cross(Vector((0, 0, 1))).normalized()
        up = side.cross(tangent).normalized()
        rad = dradii[i]
        rings.append([p + side * math.cos(2 * math.pi * j / 16) * rad +
                      up * math.sin(2 * math.pi * j / 16) * rad * FINGER_SQUASH for j in range(16)])
    tip = dense[-1] + (dense[-1] - dense[-2]).normalized() * 0.35
    obj = k.loft(name, rings, mats["shell"], start_point=dense[0], end_point=tip)
    return k.smooth(obj, 55)


def band(mats):
    """The grey-violet band round the wrist: the wrist's cross-section a little larger."""
    row, half, out = BAND
    rings = []
    for t in (-1.0, -0.7, 0.0, 0.7, 1.0):
        lobes = section_at(row + t * half)
        grow = out * math.sqrt(max(0.0, 1 - t * t)) + 0.04
        lobes = [(x, z, w + grow, top + grow, bottom + grow) for x, z, w, top, bottom in lobes]
        rings.append(k.lobed_ring(y_of(row + t * half), lobes, SEGMENTS, origin_z=0.2))
    obj = k.loft("claw_band", rings, mats["band"], cap_start=False, cap_end=False)
    k.recalc_normals(obj)
    return k.smooth(obj, 60)


def claw(mats):
    parts = body(mats)
    for points, radii, kind in FINGERS:
        parts.append(finger(f"claw_finger_{kind}", points, radii, mats))
    parts.append(band(mats))
    return parts


def materials():
    return {
        "shell": k.material("claws_shell", palette=0x46, metallic=0.25, roughness=0.2),
        "groove": k.material("claws_groove", palette=0x43, metallic=0.2, roughness=0.4),
        "band": k.material("claws_band", palette=0x58, metallic=0.45, roughness=0.25),
    }


def build_claws(mats):
    parts = claw(mats)
    for obj in parts:
        obj.data.transform(Matrix.Translation((CLAW_X[0], 0.0, 0.0)))
    for obj in parts:  # the right claw: the same, 12 pixels to the right
        copy = obj.copy()
        copy.data = obj.data.copy()
        copy.name = obj.name + "_r"
        bpy.context.scene.collection.objects.link(copy)
        copy.data.transform(Matrix.Translation((CLAW_X[1] - CLAW_X[0], 0.0, 0.0)))


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
    build_claws(materials())
    used = {m.name for o in bpy.context.scene.objects if o.type == "MESH" for m in o.data.materials}
    print("== claws (F 169): %d triangles, %d materials" % (triangles(), len(used)))
    if "check" in options:
        sheet = options["check"]
        k.check_silhouette(os.path.join(sheet, "enemy_F.png") if os.path.isdir(sheet) else sheet, 169)
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    path = os.path.join(outdir, "claws.glb")
    k.export(path)
    print("%s: %d bytes" % (path, os.path.getsize(path)))
    if "preview" in options:
        k.preview(options["preview"] + "claws")


if __name__ == "__main__":
    build()
