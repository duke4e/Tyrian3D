"""The Needle Laser's needles (shots sheet sprites 185, 186, 189 and 190, all 1x1: 12 x 14 cells), modelled (2026-10-30,
round 3 of the energy shots' models; until then each was drawn as its sprite with volume, flat, from the 4x sheets, with
the automatic glow: two blue capsules in a white-blue haze).

Who fires them: the Needle Laser (front weapon port 43, first sold in episode 5's shop 2; weapons 781-791 for power
levels 1-11), straight up the screen at 12-16 pixels a game frame, every 7-9 frames (shotrepeat 6-8): each needle is two
shots fired together one above the other 14 pixels apart (by -7 and 7), the head over the tail, so that they make one
needle 28 pixels long: 185 over 186 at power 1 and 3-10 (one needle at power 1-3, two side by side 10-18 pixels apart at
4-6, three at 7-9 (the middle one 4 pixels ahead), four at 10), 189 over 190 at power 2 and 11 (and two of the three at
8 and 9: 189 190 in the middle at 8, the outer pair at 9; four at 11). None is animated (weapani 0) and none turns.

As the sprites draw them: a needle of ramp 9's blues, 185 and 186 three pixels wide (column 5-7: its edges 0x95 and a
light middle column, 0x9a at the head's point rising to 0x9e four rows down, then 0x9b all the way down to the tail's
point), its head a single pixel (0x94, row 0 of 185) and its tail too (row 13 of 186); 189 and 190 four pixels wide
(columns 4-7: the edges 0x95, column 5 0x9b, column 6 the light core, 0x9a at the point rising to 0x9f five rows down
and flickering 0x9c-0x9e all the way down), its point and tail two pixels wide.

The models: one needle built whole, 28 pixels long, and cut in two where its cells meet (each half then moved onto its
own cell's centre): a rod round on top and flat underneath (a half-body: the game's camera only sees shots from above),
2.6 pixels wide (189's 3.4: a little slimmer than the sprites' 3 and 4, so that it reads as a needle), pointed at both
ends (round points 1.5 pixels long), its section in bands along it: dark blue at its edges (0x95), blue (0x98), and a
raised core ridge along its top in the core's colour by an idealized heat along it as the sprite's middle column goes:
light blue (0x9c), lighter (0x9e) and, where the sprite's core is brightest (four rows behind the point; 189's flashes
down its length), the pale cyan white of ramp 8 (0x8e): a shade hotter than the sprite's, so that the needle reads as a
laser (the mesh has a ring wherever the core's band changes, so no face is cut). The two halves have the same height
bounds (the rod's), so the game sets them on one level and they meet; each half's cut end is closed (a half flies on
alone when the other hits something). Each band glows in its own colour by its shade (CONVENTIONS 4: 0.31-0.62); 107-197
triangles a half, 3-5 materials. Each line's glow= (in place of the automatic glow, 13 pixels at 0.7 in the sprite's
brightest colour) puts a small light blue halo on the head and a fainter one on the tail.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; the origin at the
sprite's centre (pixel 6, 7 of the cell: column c is x = c + 0.5 - 6, row r is y = 6.5 - r, its top edge y = 7 - r);
185/186's needle half a pixel right of the cell's centre (column 6), 189/190's on it; the needles stand on z = 0 (the
game centres shot models in height on the player's layer).

models.cfg (the shots section):
    model shot_needle     shots/shot_needle.glb
    model shot_needle_186 shots/shot_needle_186.glb
    model shot_needle_189 shots/shot_needle_189.glb
    model shot_needle_190 shots/shot_needle_190.glb
    shot shots 185 shot_needle     glow=...

Run: Blender -b --factory-startup -P tools/blender/models/shots/polish_shot_needle.py -- [--only <name,...>]
     [--outdir <dir>] (default assets/models/shots) [--check <sheets dir>] (each half's top view against its sprite in
     <dir>/shots.png, from TYR3D_EXTRACT) [--preview <prefix>] (top, three-quarter and game-camera views, and
     <prefix>needles_game.png: the halves joined as the game fires them)
"""
import math
import os
import sys

import bpy
from mathutils import Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
ENEMIES = os.path.join(HERE, "..", "enemies")
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, ENEMIES)
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_launched_flames import lit, check_frames, turn  # noqa: E402
from polish_shot_starburst import glow_of, game_camera  # noqa: E402

OUTDIR = os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "shots")
TOP, CUT, BOTTOM = 7.0, -7.0, -21.0  # (the needle's point, where its cells meet, its tail's point: the head cell's y)


def linear_curve(xs, ys):
    """A curve through the points, straight between them (the heat along a needle has its ups and downs)."""
    def f(x):
        if x <= xs[0]:
            return ys[0]
        for i in range(len(xs) - 1):
            if x <= xs[i + 1]:
                t = (x - xs[i]) / (xs[i + 1] - xs[i])
                return ys[i] + (ys[i + 1] - ys[i]) * t
        return ys[-1]
    return f


class Needle:
    """A needle: its two sprites (head, tail), its middle's x, its half-width and its heat along it by row."""

    def __init__(self, name, sprites, x, half, heat):
        self.name, self.sprites, self.x, self.half = name, sprites, x, half
        self.heat_rows = linear_curve([p[0] for p in heat], [p[1] for p in heat])


# The heat along each needle by row of its two cells (0 the point, 27 the tail's point), in ramp 9's shades, smoothed
# from the sprites' middle columns.
HEAT_185 = ((0.0, 9.0), (1.0, 10.0), (2.0, 11.0), (3.0, 12.5), (4.0, 14.2), (5.0, 13.4), (6.5, 12.2), (8.0, 11.2),
            (13.0, 11.0), (20.0, 10.8), (26.0, 10.4), (27.5, 9.0))
HEAT_189 = ((0.0, 9.0), (1.0, 10.0), (2.0, 11.2), (3.0, 12.4), (4.0, 13.4), (5.0, 15.0), (6.0, 13.4), (7.5, 12.6),
            (9.5, 13.6), (10.5, 13.8), (12.5, 12.4), (15.0, 12.4), (17.0, 14.0), (18.5, 13.2), (20.5, 13.0),
            (22.5, 11.6), (24.0, 12.0), (26.0, 10.6), (27.5, 9.0))
NEEDLES = [
    Needle("shot_needle", (185, 186), 0.5, 1.3, HEAT_185),
    Needle("shot_needle_189", (189, 190), 0.0, 1.7, HEAT_189),
]
# The section: a half-ellipse DEPTH times the half-width high, a core ridge CORE_U of the half-width either side of the
# middle standing CORE_LIFT (times the half-width over 1.3) out of it; bands out from the middle (from u, palette index;
# the core's by the heat, CORE_BANDS: (lowest heat, index), coolest first).
DEPTH = 0.66
CORE_U, CORE_LIFT = 0.38, 0.3
BANDS = ((0.0, None), (0.38, 0x98), (0.66, 0x95))
SECTION_US = (0.0, 0.38, 0.66, 0.84, 1.0)
CORE_BANDS = ((-99.0, 0x9c), (11.6, 0x9e), (13.6, 0x8e))
# The points: rings this far from each point (pixels), the width there (the point's roundness).
POINT_LENGTH = 1.5
POINT_RINGS = (0.12, 0.35, 0.7, 1.05, 1.5)


def core_index(heat):
    index = CORE_BANDS[0][1]
    for lowest, i in CORE_BANDS:
        if heat >= lowest - 1e-9:
            index = i
    return index


def width_at(y):
    """The needle's width at y against its full width: round points 1.5 pixels long at both ends."""
    d = min(TOP - y, y - BOTTOM)
    if d >= POINT_LENGTH:
        return 1.0
    f = max(d, 0.0) / POINT_LENGTH
    return math.sqrt(max(0.0, 1.0 - (1.0 - f) ** 2))


def z_of(u, w):
    u = min(abs(u), 1.0)
    body = DEPTH * w * math.sqrt(max(0.0, 1.0 - u * u))
    if u < CORE_U - 1e-9:
        body += CORE_LIFT * (w / 1.3) * math.sqrt(max(0.0, 1.0 - (u / CORE_U) ** 2))
    return body


def row_of(y):
    return TOP - y - 0.5


def ring_ys(needle, y0, y1):
    """The rings of the half from y0 down to y1: its ends, the point's rings near a point, and every core band border
    where the heat along the needle crosses it."""
    ys = {y0, y1}
    for d in POINT_RINGS:
        for y in (TOP - d, BOTTOM + d):
            if y1 < y < y0:
                ys.add(round(y, 6))
    heat = needle.heat_rows
    steps = 400
    for border, _ in CORE_BANDS[1:]:
        lowest = border - 1e-6  # (a crossing exactly on a sample still counts)
        for i in range(steps):
            a = y0 + (y1 - y0) * i / steps
            b = y0 + (y1 - y0) * (i + 1) / steps
            ha, hb = heat(row_of(a)), heat(row_of(b))
            if (ha - lowest) * (hb - lowest) < 0:
                lo, hi = a, b
                for _ in range(40):
                    mid = (lo + hi) / 2
                    if (heat(row_of(mid)) - lowest) * (ha - lowest) > 0:
                        lo = mid
                    else:
                        hi = mid
                ys.add(round((lo + hi) / 2, 6))
    return sorted(ys, reverse=True)


def material(index):
    return lit(f"needle_{index:02x}", index, glow_of(index & 15), roughness=0.4 if index & 15 >= 12 else 0.5)


def half_mesh(needle, name, y0, y1, materials):
    """The needle between y0 and y1 (the head cell's coordinates): rings along it, each a section from the right edge
    over the top to the left edge; the flat underside; a point (a fan to z = 0) where it reaches TOP or BOTTOM, else a
    flat cap (the cut)."""
    us = list(SECTION_US)
    order = [u for u in reversed(us[1:])] + [-u for u in us]
    ys = ring_ys(needle, y0, y1)
    verts, faces, bands = [], [], []
    starts = []
    for y in ys:
        w = needle.half * width_at(y)
        starts.append(len(verts))
        for u in order:
            verts.append((needle.x + u * w, y, z_of(u, w)))
    count = len(order)

    def strip_band(j, heat):
        mid = (abs(order[j]) + abs(order[j + 1])) / 2
        band = max(i for i, b in enumerate(BANDS) if mid >= b[0] - 1e-9)
        return core_index(heat) if BANDS[band][1] is None else BANDS[band][1]
    for i in range(len(ys) - 1):
        heat = needle.heat_rows(row_of((ys[i] + ys[i + 1]) / 2))
        a, b = starts[i], starts[i + 1]
        for j in range(count - 1):
            faces.append((a + j, a + j + 1, b + j + 1, b + j))
            bands.append(strip_band(j, heat))
        faces.append((a + count - 1, a, b, b + count - 1))
        bands.append(BANDS[-1][1])
    # The ends: a point (to a vertex on the axis at z = 0) or the flat cut (a fan to its middle).
    for end, y in ((0, ys[0]), (len(ys) - 1, ys[-1])):
        heat = needle.heat_rows(row_of(y))
        first = starts[end]
        point = abs(y - TOP) < 1e-6 or abs(y - BOTTOM) < 1e-6
        centre = len(verts)
        verts.append((needle.x, y, 0.0 if point else z_of(0.0, needle.half * width_at(y)) * 0.5))
        for j in range(count - 1):
            faces.append((first + j + 1, first + j, centre) if end == 0 else (first + j, first + j + 1, centre))
            bands.append(strip_band(j, heat))
    obj = k.mesh_object(name, verts, faces)
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.dissolve_degenerate(bm, dist=1e-6, edges=bm.edges)
    bm.to_mesh(obj.data)
    bm.free()
    slots = []
    for index in bands:
        if index not in slots:
            slots.append(index)
    for index in slots:
        obj.data.materials.append(materials[index])
    # (after the welding, each face's band again from its place: its middle's u and heat)
    for poly in obj.data.polygons:
        cx, cy, _ = poly.center
        if poly.normal.z < -0.5:
            index = BANDS[-1][1]
        else:
            w = needle.half * max(width_at(cy), 1e-3)
            u = abs(cx - needle.x) / w
            band = max(i for i, b in enumerate(BANDS) if u >= b[0] - 1e-9)
            index = core_index(needle.heat_rows(row_of(cy))) if BANDS[band][1] is None else BANDS[band][1]
        poly.material_index = slots.index(index) if index in slots else 0
    k.recalc_normals(obj)
    return k.smooth(obj, 60)


def build_half(needle, which, name):
    """The head half (which 0: the needle's first cell) or the tail half (1, moved up onto its own cell's centre)."""
    mats = {index: material(index) for index in [b[1] for b in BANDS[1:]] + [c[1] for c in CORE_BANDS]}
    if which == 0:
        part = half_mesh(needle, name, TOP, CUT, mats)
    else:
        part = half_mesh(needle, name, CUT, BOTTOM, mats)
        mk.transform([part], Matrix.Translation((0.0, 14.0, 0.0)))
    return triangulate([part])


MODELS = [  # (name, sprite, needle, half, what)
    ("shot_needle", 185, 0, 0, "the needle's head half (3 pixels wide)"),
    ("shot_needle_186", 186, 0, 1, "its tail half"),
    ("shot_needle_189", 189, 1, 0, "the wider needle's head half (4 pixels wide)"),
    ("shot_needle_190", 190, 1, 1, "its tail half"),
]
GLOW = {185: "9:0.45:157:0.5:-2", 186: "7:0.25:156:0.5:0", 189: "10:0.5:158:0:-2", 190: "8:0.3:157:0:0"}


def zbounds(parts):
    zs = [(p.matrix_world @ v.co).z for p in parts for v in p.data.vertices]
    return min(zs), max(zs)


def game_view(prefix, objects):
    mk.preview(prefix, objects, size=(12, 14), scale=32, distance=0.42)
    scene = bpy.context.scene
    cam, sun = game_camera(scene, 16.0, (512, 512))
    scene.render.filepath = prefix + "_game.png"
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam)
    bpy.data.objects.remove(sun)


def needles_view(prefix):
    """The halves joined as the game fires them (each centred in height on its bounds, as the game does)."""
    k.reset()
    scene = bpy.context.scene
    scene.view_settings.view_transform = "Standard"
    for n, (x, model_pair) in enumerate(((-8.0, (0, 1)), (8.0, (2, 3)))):
        for half, m in enumerate(model_pair):
            name, sprite, needle, which, _ = MODELS[m]
            parts = build_half(NEEDLES[needle], which, f"{name}_v{n}")
            low, high = zbounds(parts)
            mk.transform(parts, Matrix.Translation((x, 7.0 - 14.0 * half, -(low + high) / 2)))
    bpy.context.view_layer.update()
    cam, sun = game_camera(scene, 40.0, (800, 800))
    scene.render.filepath = prefix + "needles_game.png"
    bpy.ops.render.render(write_still=True)


def build():
    options = k.args()
    only = set(options["only"].split(",")) if "only" in options else None
    outdir = options.get("outdir", OUTDIR)
    for name, sprite, needle, which, what in MODELS:
        if only is not None and name not in only:
            continue
        k.reset()
        parts = build_half(NEEDLES[needle], which, name)
        bpy.context.view_layer.update()
        low, high = zbounds(parts)
        print(f"== {name} (shots {sprite}): {what}; z {low:.3f}..{high:.3f}")
        if "check" in options:
            check_frames(parts, os.path.join(options["check"], "shots.png"), [(sprite, turn(0), f"shots {sprite}")],
                         move_to_frame=False)
        bpy.context.scene.view_settings.view_transform = "Standard"
        mk.report(name, parts, os.path.join(outdir, name + ".glb"))
        if "preview" in options:
            game_view(options["preview"] + name, parts)
    if "preview" in options and only is None:
        needles_view(options["preview"])
    print("CFG:")
    for name, sprite, _, _, _ in MODELS:
        print(f"model {name:<15} shots/{name}.glb")
    for name, sprite, _, _, _ in MODELS:
        print(f"shot shots {sprite} {name:<15} glow={GLOW[sprite]}")


if __name__ == "__main__":
    build()
