"""What is left of the asteroid cities' hangar once it is shot (stage 4 of the clean ground: the wreck models that stand
in for the maps' painting of its ruin; sheet S sprites 51, 53 above 89, 91, the hangar's lower four), built on
polish_roof_hangar.py (2026-10-25). models.cfg: model roof_hangar_ml_wreck / _mr_wreck / _bl_wreck / _br_wreck
enemies/roof_hangar_*_wreck.glb origin; wreck s 51 roof_hangar_ml_wreck, wreck s 53 roof_hangar_mr_wreck (and wreck s 89
roof_hangar_bl_wreck, wreck s 91 roof_hangar_br_wreck, for when the clean ground marks the lower pieces as the wreck's
too: today it stands their live models there). Drawn with the live sprite lines' options (yaw=0 height=-4), at the live
pieces' places; above them the far end's damaged look (S 17, 55: the game's own, polish_roof_hangar.py) stands as the
top pieces' stand-in, broken off along its lower edge where these begin.

The painting (the maps' tiles 421 422 above 431 432, the same in ASTCITY 6498eda0c182465c at 576, 5894 and AST. CITY
6ecacae4c50b7490 at 624, 4187; columns and rows of the 48 x 84 picture, the ruin's rows 28-66, where the sprites draw
the hangar's roof and its gable front): the hangar burnt out to its floor, black (0x01) between its walls (columns 6
and 41), the roof fallen in. A pale torn sheet of the left slope leaning on the left wall (columns 7-10 of rows 28-49,
0x09-0x0d), the left wall's top lit down to row 56; a grey sheet of the right slope on the right wall (columns 33-40 of
rows 28-44, 0x06-0x0a), its upper left edge curled up white; the ridge beam fallen along the middle (columns 21-23 of
rows 34-50, 0x09-0x0b) to the fascia lying bent across the near end (columns 18-27 of rows 49-51, 0x0a-0x0d);
red-hot purlins lying up the screen (ramp 7, 0x70-0x73: columns 12-14 of rows 29-44, a white-hot spot at its top end,
columns 18-19 of rows 30-48, 29-30 of rows 33-44), and on the gable front, fallen low (its wall panels left and right
standing dark grey in rows 60-65, 0x04-0x08; burnt black where the gate and the door were), the gate's bars red-hot
(columns 23, 25, 27 of rows 52-66, a bar across at row 60, another at column 31 of rows 51-61). The kerb, the apron, the
pale rim left of the hangar (columns 4-5) and the floor round it are the map's floor (left out, as the live model leaves
them out).

The model, in the picture's plane as the live hangar (polish_asteroid_kit; sheared to the camera afterwards, so the
camera sees each point where the painting draws it; its materials, with the palette's black 0x00 for the burnt floor
and two embers): the floor burnt black, the wall stubs with ragged tops (the left one's top lit), the two slopes' torn
sheets fallen by the walls still pitched as they were (thin buckled plates over jagged outlines: the left one facing
the sun, light; the right one away from it, its inner edge curled up and lit white), dark sheets between the purlins,
the ridge beam fallen in two onto the fascia's torn sheets across the near end, the gable front fallen to a low ragged
slab (the live wall panels on it, polish_roof_hangar.FRONT; black where the gate and the door were), the purlins and
the gate's bars lying red-hot (their tops 0x75 at 0.42, their sides 0x72 glowing at 0.3: under the bloom's white), a
few embers, grey scraps and dark rubble (polish_pyramid_wreck.chunk) on the floor. Cut along the sprites' edges as the
live hangar (x = 0, y = -14, 14; polish_coral_manta.cut, the caps charred), sheared, each piece moved so that its
sprite's middle is its origin. The highest point is a sheet's 4.8 (the live hangar's ridge 20): the ruin lies low.

Coordinates as polish_roof_hangar.py's: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera (z 0:
the floor); in the picture's plane column c's left edge is x = c - 24, row r's top edge y = 42 - r.

Options after "--": --outdir <dir> (default assets/models/enemies), --preview <prefix>, --only <model,...>, --whole
<prefix> (the uncut wreck too, sheared).
"""
import math
import os
import random
import sys

import bpy
from mathutils import Vector, noise

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
import polish_asteroid_kit as ak  # noqa: E402
import polish_roof_hangar as live  # noqa: E402
from polish_pyramid_wreck import chunk  # noqa: E402
from polish_jaw_gun_wreck import lump  # noqa: E402

SEED = 51
PIECES = [(name + "_wreck", sprite, box) for name, sprite, box in live.PIECES if sprite in (51, 53, 89, 91)]
WALL_X, FOOT = live.WALL_X, live.FOOT
FLOOR = 0.3                      # the burnt floor's top
TOP_Y = 14.0                     # where the ruin begins (the far end's damaged look ends there)


def Q(c, r):
    """The picture's point at column edge c, row edge r (fractions allowed)."""
    return (c - 24.0, 42.0 - r)


def n2(x, y, seed):
    """Smooth noise, -1 to 1 (mathutils' Perlin basis: the same every run)."""
    return noise.noise(Vector((x * 0.55 + seed, y * 0.55 - seed, 0.37 * seed)))


# --- The pieces of the ruin (columns, rows; heights) ------------------------------------------------------------------
# The wall stubs: (x0, x1) and their tops' heights (lowest, highest), their materials.
WALLS = [((-WALL_X - 0.4, -WALL_X + 0.6), (1.6, 3.4), "roof"), ((WALL_X - 0.6, WALL_X + 0.4), (1.3, 3.0), "trim")]
WALL_Y = (-17.6, TOP_Y)
# The torn sheets of the roof: columns (from, to), rows (from, to), heights at their left and right edges, the
# material, how much they buckle, a curl along the left edge (rows from, to; how high it rises) or None. The two slopes'
# big sheets fallen by the walls, still pitched as they were (low at the wall, so the left one faces the sun, the right
# one away from it); dark ones between the purlins; the fascia's sheets across the near end.
SHEETS = [((6.9, 10.8), (28.0, 49.4), 0.8, 3.0, "ridge", 0.12, None),
          ((32.4, 40.7), (28.0, 44.2), 3.2, 0.8, "roof", 0.14, ((31.0, 38.6), 1.6)),
          ((14.2, 17.4), (33.4, 47.2), 1.5, 0.9, "gable", 0.1, None),
          ((23.8, 28.4), (35.4, 46.6), 1.4, 0.7, "gable", 0.1, None),
          ((18.8, 24.8), (47.2, 51.6), 0.9, 1.9, "ridge", 0.15, None),
          ((25.0, 30.6), (49.2, 52.2), 1.4, 0.8, "roof_r", 0.1, None)]
# The ridge beam, fallen in two (from, to: column, row, height; its width and depth).
RIDGE = [((22.0, 32.2, 1.7), (22.5, 40.6, 1.4)), ((22.9, 41.0, 1.3), (22.2, 48.6, 1.9))]
RIDGE_SECTION = (2.1, 0.9)
# Grey wreckage on the floor: (column, row, size, heading (degrees), material).
SCRAPS = [(15.6, 48.6, 2.0, 80.0, "ridge"), (26.2, 29.4, 2.6, 10.0, "seam"), (9.2, 52.2, 1.4, 40.0, "side")]
# The red-hot purlins and the gate's bars: points (column, row) along each, lying on the floor or the fallen front.
BARS = [[(12.6, 29.0), (12.7, 36.0), (13.2, 41.5), (14.4, 44.6)],
        [(18.6, 30.2), (18.5, 39.0), (18.7, 48.4)],
        [(17.0, 37.6), (19.8, 37.9)],
        [(30.0, 33.0), (29.8, 39.0), (29.4, 44.8)],
        [(31.4, 51.0), (31.2, 56.0), (31.0, 61.6)],
        [(23.4, 54.0), (23.4, 60.0), (23.5, 65.6)],
        [(25.4, 52.4), (25.5, 59.0), (25.6, 65.6)],
        [(27.6, 55.0), (27.4, 62.6)],
        [(23.0, 60.4), (27.6, 60.2), (30.8, 59.8)]]
BAR_SECTION = (1.4, 0.8)         # width, height
# Embers: (column, row, radius); the first the white-hot spot at the first purlin's top end.
EMBERS = [(12.6, 30.6, 0.8), (18.6, 37.8, 0.6), (29.9, 35.6, 0.6), (25.5, 60.2, 0.7), (14.0, 43.6, 0.5)]
# The gable front fallen low: its top edge (row) and height there; its burnt middle (x from, to); the live wall panels
# kept on it (polish_roof_hangar.FRONT names).
FRONT_TOP, FRONT_H = 59.8, 2.4
FRONT_BURNT = (-5.6, 10.5)
FRONT_KEEP = ("panel_l1", "panel_l2", "panel_l3", "panel_r1", "panel_r2")
RUBBLE = 14                      # dark lumps on the floor


def materials():
    m = live.materials(damaged=True)
    m["ember"] = ak.pal("hangarwreck_ember", 0x72, 0.0, 0.8, 0.3, 0x74)
    m["hot"] = ak.pal("hangarwreck_hot", 0x75, 0.0, 0.7, 0.42)
    m["black"] = ak.pal("hangarwreck_black", 0x00, 0.0, 1.0)      # (the burnt floor: the painting's black)
    return m


def paint_faces(obj, top, side, under, up=0.5):
    """Faces turned up (n.z > up) top, down under, the rest side."""
    mk.paint(obj, lambda c, n: top if n.z > up else under if n.z < -0.5 else side)
    return obj


# --- Builders ---------------------------------------------------------------------------------------------------------

def thin_grid(name, top, thick, mat):
    """A thin plate whose top is the grid top[j][i] = (x, y, z) and whose underside lies thick under it, closed round
    its border."""
    rows, cols = len(top), len(top[0])
    verts = [tuple(p) for row in top for p in row] + [(x, y, z - thick) for row in top for x, y, z in row]
    n = rows * cols
    faces = []

    def v(i, j):
        return j * cols + i
    for j in range(rows - 1):
        for i in range(cols - 1):
            a, b, c, d = v(i, j), v(i + 1, j), v(i + 1, j + 1), v(i, j + 1)
            faces += [(a, b, c, d), (n + d, n + c, n + b, n + a)]
    border = [v(i, 0) for i in range(cols)] + [v(cols - 1, j) for j in range(1, rows)] + \
        [v(i, rows - 1) for i in range(cols - 2, -1, -1)] + [v(0, j) for j in range(rows - 2, 0, -1)]
    for q in range(len(border)):
        a, b = border[q], border[(q + 1) % len(border)]
        faces.append((a, n + a, n + b, b))
    obj = ak.link(name, verts, faces, mat)
    k.recalc_normals(obj)
    return obj


def sheet(name, cols, rows, z_left, z_right, mat, buckle, curl, seed, m):
    """A torn sheet of the roof lying tilted in the ruin: a buckled thin plate over a jagged outline (its edges torn
    by noise), z_left high at its left edge and z_right at its right; its curl (a lip rising along its left edge) if
    any, turned to the sun: white."""
    (c0, c1), (r0, r1) = cols, rows
    x0, x1 = c0 - 24.0, c1 - 24.0
    y0, y1 = 42.0 - r1, 42.0 - r0
    nx, ny = max(3, int((x1 - x0) / 0.9)), max(4, int((y1 - y0) / 1.0))
    top = []
    for j in range(ny + 1):
        y = y0 + (y1 - y0) * j / ny
        jl, jr = 0.55 * n2(3.1, y, seed), 0.55 * n2(7.3, y, seed + 1.0)
        row = []
        for i in range(nx + 1):
            u = i / nx
            x = x0 + jl + (x1 + jr - x0 - jl) * u
            yy = y + (0.7 * n2(x, 1.7, seed + 2.0) if j == 0 else 0.0)
            z = z_left + (z_right - z_left) * u + buckle * n2(x * 0.7, y * 0.5, seed + 3.0)
            if curl is not None:
                (cr0, cr1), rise = curl
                r = 42.0 - yy
                if cr0 <= r <= cr1 and u < 0.34:
                    z += rise * math.sin(math.pi * (r - cr0) / (cr1 - cr0)) * (1.0 - u / 0.34) ** 2
            row.append((x, yy, z))
        top.append(row)
    obj = thin_grid(name, top, 0.22, m[mat])
    x_curl = x0 + 0.34 * (x1 - x0)

    def pick(c, n):
        if n.z < -0.5:
            return m["inside"]
        if n.z < 0.45:
            return m["seam"]
        if curl is not None and c.x < x_curl and n.x < -0.2:
            return m["number"]
        return None
    mk.paint(obj, pick)
    return k.smooth(obj, 70)


def bar_beam(name, points, z_of, m, section=BAR_SECTION):
    """A red-hot bar lying along points (columns, rows), a straight beam between each two, its top hot, its sides
    glowing duller."""
    w, h = section
    parts = []
    for i, ((ca, ra), (cb, rb)) in enumerate(zip(points, points[1:])):
        a, b = Vector((*Q(ca, ra), 0.0)), Vector((*Q(cb, rb), 0.0))
        d = (b - a).normalized()
        a, b = a - d * 0.3, b + d * 0.3         # (overlapping at the bends)
        a.z, b.z = z_of(a.x, a.y), z_of(b.x, b.y)
        beam = ak.beam(f"{name}_{i}", a, b, ak.rect_profile(w, h, 0.18, below=0.2), (0, 0, 1), m["ember"])
        paint_faces(beam, m["hot"], m["ember"], m["ember"], 0.6)
        parts.append(k.smooth(beam, 30))
    return parts


def front_top(x):
    """The fallen gable front's ragged top edge (y in the plane)."""
    return 42.0 - FRONT_TOP + 0.7 * n2(x * 0.8, 2.3, 11.0)


def front_z(x, y):
    """The fallen front's surface: from the foot up to its top edge."""
    t = max(0.0, min(1.0, (y - FOOT) / (front_top(x) - FOOT)))
    return FRONT_H * t * (0.85 + 0.15 * n2(x, y, 12.0))


def floor_z(x, y):
    """What a bar or a lump lies on: the fallen front, else the floor."""
    if y < front_top(x) and abs(x) < WALL_X:
        return max(FLOOR, front_z(x, y))
    return FLOOR


# --- The ruin ---------------------------------------------------------------------------------------------------------

def build_whole(m):
    solids = []
    # The floor, burnt black.
    floor = mk.box("floor", -WALL_X - 0.4, WALL_X + 0.4, FOOT, TOP_Y, -1.0, FLOOR, m["black"])
    solids.append(floor)
    # The wall stubs, their tops ragged.
    for i, ((x0, x1), (lo, hi), mat) in enumerate(WALLS):
        top = []
        for j in range(41):
            y = WALL_Y[0] + (WALL_Y[1] - WALL_Y[0]) * j / 40
            z = lo + (hi - lo) * (0.5 + 0.5 * n2(y * 1.1, 4.0 * i, 5.0 + i))
            top.append([(x0, y, z), (x1, y, z)])
        wall = ak.grid_solid(f"wall{i}", top, -1.0, m[mat])
        paint_faces(wall, m[mat], m["inside"], m["inside"], 0.5)
        solids.append(mk.shade(wall, 40))
    # The torn roof sheets.
    for i, (cols, rows, zl, zr, mat, buckle, curl) in enumerate(SHEETS):
        solids.append(sheet(f"sheet{i}", cols, rows, zl, zr, mat, buckle, curl, 20.0 + 7.0 * i, m))
    # The ridge beam, fallen in two.
    w, h = RIDGE_SECTION
    for i, ((ca, ra, za), (cb, rb, zb)) in enumerate(RIDGE):
        ridge = ak.beam(f"ridge_beam{i}", (*Q(ca, ra), za), (*Q(cb, rb), zb), ak.rect_profile(w, h, 0.3, below=0.6),
                        (0, 0, 1), m["ridge"])
        paint_faces(ridge, m["ridge"], m["seam"], m["inside"])
        solids.append(k.smooth(ridge, 30))
    # The gable front, fallen low: a ragged slab from the foot, its middle charred, the wall panels on it.
    xs = [-WALL_X + 2 * WALL_X * i / 34 for i in range(35)]
    rows = 8
    top = []
    for j in range(rows + 1):
        line = []
        for x in xs:
            y = FOOT + (front_top(x) - FOOT) * j / rows
            line.append((x, y, front_z(x, y)))
        top.append(line)
    front = ak.grid_solid("front", top, -1.0, m["gable"])
    f0, f1 = FRONT_BURNT
    mk.paint(front, lambda c, n: m["inside"] if n.z < -0.5 else
             (m["black"] if f0 + 0.6 * n2(c.y, 1.0, 13.0) < c.x < f1 + 0.6 * n2(c.y, 2.0, 14.0) else
              m["gable"] if n.z > 0.3 else m["side"]))
    solids.append(mk.shade(front, 40))
    for name, (x0, x1, y0, y1), (z0, z1), mat in live.FRONT:
        if name not in FRONT_KEEP:
            continue
        outline = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        panel = ak.prism_on("front_" + name, outline, front_z, z0 - 0.2, z1 - 0.1, m["gable"])
        paint_faces(panel, m["side"], m["trim"], m["inside"])
        solids.append(mk.shade(panel, 35))
    # Grey wreckage on the floor.
    rng = random.Random(SEED)
    for i, (c, r, size, heading, mat) in enumerate(SCRAPS):
        x, y = Q(c, r)
        scrap = chunk(f"scrap{i}", (x, y, floor_z(x, y) - 0.1), size, rng, m[mat], 0.35)
        paint_faces(scrap, m[mat], m["seam"], m["inside"])
        solids.append(mk.shade(scrap, 30))
    # The red-hot purlins and bars, the embers.
    for i, pts in enumerate(BARS):
        solids += bar_beam(f"bar{i}", pts, lambda x, y: floor_z(x, y) + 0.25, m)
    for i, (c, r, rad) in enumerate(EMBERS):
        x, y = Q(c, r)
        e = lump(f"ember{i}", (x, y, floor_z(x, y) + 0.9), (rad, rad * 0.9, rad * 0.5), m["hot"], 3.3 + 1.1 * i, 0.3, 1)
        solids.append(k.smooth(e, 70))
    # Dark rubble on the floor (not on the bars).

    def near_bar(x, y):
        for pts in BARS:
            for (ca, ra), (cb, rb) in zip(pts, pts[1:]):
                a, b = Vector(Q(ca, ra)), Vector(Q(cb, rb))
                ab = b - a
                t = max(0.0, min(1.0, (Vector((x, y)) - a).dot(ab) / max(ab.length_squared, 1e-9)))
                if (Vector((x, y)) - (a + ab * t)).length < 1.6:
                    return True
        return False
    n = tries = 0
    while n < RUBBLE and tries < 600:
        tries += 1
        x, y = rng.uniform(-WALL_X + 1.5, WALL_X - 1.5), rng.uniform(FOOT + 1.0, TOP_Y - 1.5)
        if near_bar(x, y):
            continue
        size = rng.uniform(0.9, 2.0)
        mat = (m["inside"], m["trim"], m["char"], m["side"])[n % 4]
        lump_ = chunk(f"rubble{n}", (x, y, floor_z(x, y) - 0.15), size, rng, mat, rng.uniform(0.35, 0.6))
        solids.append(mk.shade(lump_, 30))
        n += 1
    for o in solids:
        mk.apply(o)
    bpy.context.view_layer.update()
    return solids


def build():
    options = k.args()
    out = mk.outdir(options)
    only = set(options["only"].split(",")) if "only" in options else None
    k.reset()
    bpy.context.scene.view_settings.view_transform = "Standard"
    m = materials()
    solids = build_whole(m)
    print("== whole hangar wreck: %d triangles, %d parts, %d materials" % (
        mk.triangles(solids), len(solids), len(mk.materials_of(solids))))
    if "whole" in options:
        view = ak.copy_all(solids, "_w")
        ak.shear_to_camera(view)
        ak.triangulate(view)
        mk.export(view, options["whole"] + "hangar_wreck.glb")
        ak.remove(view)
    for name, sprite, box in PIECES:
        if only and name not in only:
            continue
        parts = ak.piece(solids, box, m["char"])
        ak.hide(solids)
        centre = ((box[0] + box[1]) / 2, (box[2] + box[3]) / 2)
        obj, _ = ak.finish(name, parts, centre, out, options, None, label="%s (S %d)" % (name, sprite))
        ak.remove([obj])
        ak.hide(solids, False)


if __name__ == "__main__":
    build()
