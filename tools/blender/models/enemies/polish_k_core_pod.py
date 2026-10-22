"""FLEET's pod with the red core and the blue eye (sheet K sprite 245, 2x2: 24 x 28 pixels, the pod in rows 1-26; enemy
703 of episode 3, the ground layer (ground 2); one frame, not animated), modelled (2026-10-22; until now it had no
model and was drawn as a flat volume).

What it is: one of FLEET's grey machines (enemies 702-708: k_pod, fin_chevron, k_lampgun, k_clawblock, k_turret, all
coming down the screen at 2 pixels a game frame). The walker's hatches (O 191 beside O 193: enemies 737 and 738,
FLEET's events at 5020, three pairs on ground 2, fleet_hatch_l / _r) roll their shutters up and launch one every 80
game frames from their bays, and it slides down the screen out of the walker ((0, 2) and the ground's scroll). Armour
20. Episode 6's DELI RUIN has FLEET's walker as its boss, so it shows there too. No other enemy shows the sprite
(catalog.json); it is no other sprite's pixels mirrored or turned (k_pod, K 276, has the same octagon but other
pixels).

As the sprite draws it: an octagon of grey armour plate (ramp 0), the full width (columns 0-23) over rows 8-19, its
corners cut on the diagonal (to columns 7-16 at rows 1 and 26), the sprite its own mirror image across the middle of
its height (rows 14-26 are rows 13-1 but for a few shades of the eye, the bars and the slots); a darker band of plate
round its edge (rows 2-3 and along the diagonals: the
crown sloping down to the edge); on each half a raised light frame, a U of 1-pixel rails (columns 8-15 of row 4, down
columns 8 and 15 to row 8) open towards the middle, round a dark gap (row 5, columns 9 and 14) and a grey plate with a
light ridge down its middle (column 12, rows 6-8); across the middle a window (its dark edges rows 9 and 18, columns
6-17) holding a red core shaped like a lozenge (rows 10-17, its pointed ends reaching columns 4 and 19 at rows 13-14),
dark red (0x72-0x74) with two glowing orange bars across it (columns 8 and 15: 0x76-0x7b), a blue eye in its middle
(columns 11-12 of rows 13-14: 0x93-0x99) in a dark ring, short orange bars above and below the eye (rows 10-11 and
16-17); either flank a dark slot (rows 13-14, columns 0-3 and 20-23) the core's ends point into, its lips lit (rows
12 and 15).

Built as a CAD modeller would (polish_machine_kit, polish_k_pod's way): the body a prism of the octagon, its crown cut
by a plane along each of its eight edges (sloping down 2.2 pixels over the last 2.2: the dark band round the edge),
bevelled; the window, the flank slots and the frames' gaps cut with exact booleans; the frames' rails, the plates and
their ridges laid on as bevelled boxes (the top half's built and mirrored across y = 0); the core a rounded lozenge
bar lofted along x (its section a superellipse, thinner towards its points), two raised bands round it for the
orange bars, cut into bands by its facets (polish_orb_red.band_split), glowing in its own reds and oranges, well under
1; the eye a blue dome in a dark bezel ring, the short bars glowing studs. The pod flies low: flat underneath, 8.5
pixels high, centred in height by the game. Meshes after booleans are rebuilt in a fixed order (canonical): the exact
boolean's output order changes from run to run.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; origin at the
sprite's centre (pixel 12, 14): column c's left edge is x = c - 12, row r's top edge y = 14 - r.

models.cfg (new): model k_core_pod enemies/k_core_pod.glb; sprite k 245 k_core_pod yaw=0 glow=14:0.18:121:0:0 (a faint
orange light round the core), with FLEET's grey machines (after sprite k 207 fin_chevron).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouette against
enemy_K.png), --preview <prefix>.
"""
import math
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_k_pod import mirror_y, plane_box, triangulate  # noqa: E402
from polish_orb_red import band_split  # noqa: E402
from polish_launched_flames import vertex_normals  # noqa: E402

NAME = "k_core_pod"
MID = 0.5                       # the details' middle (column 12's)

# The octagon (through the middles of the sprite's steps), its underside and crown, the band round its edge where the
# crown slopes down (how far in, how far down), the bevel.
PLAN = [(-4.5, 13.0), (4.5, 13.0), (12.0, 5.5), (12.0, -5.5), (4.5, -13.0), (-4.5, -13.0), (-12.0, -5.5), (-12.0, 5.5)]
BOTTOM, CROWN = -3.0, 5.0
EDGE_BAND, EDGE_DROP = 2.2, 2.2
BEVEL = 0.35
# The window across the middle (its plan, a hexagon round the core's lozenge) and its floor.
WINDOW = [(-6.3, 5.0), (6.3, 5.0), (7.7, 2.6), (9.0, 0.85), (9.0, -0.85), (7.7, -2.6), (6.3, -5.0), (-6.3, -5.0),
          (-7.7, -2.6), (-9.0, -0.85), (-9.0, 0.85), (-7.7, 2.6)]
WINDOW_FLOOR = -0.6
# The flanks' slots (x from the window out past the edge, half-height up the screen, their floor), their lit lips
# (from y to y either side).
SLOT = (8.2, 12.8, 0.95, 1.5)
LIPS = (0.95, 2.05)
# Each half's frame (the top half's; mirrored): the rails (x0, x1, y0, y1), how proud of the crown and how deep they
# reach; the gap inside the U (x0, x1, y0, y1, depth); the plate in it (x0, x1, y0, y1, its top under the crown) and
# its ridge (half-width about MID, y0, y1, how proud of the plate).
RAILS = [(-4.05, 4.05, 9.0, 10.05), (-4.05, -3.0, 5.0, 10.05), (3.0, 4.05, 5.0, 10.05)]
RAIL_UP, RAIL_DOWN = 0.55, 0.6
GAP = (-3.0, 3.0, 4.9, 9.0, 1.0)
PLATE = (-2.45, 2.45, 4.9, 8.35, 0.2)
RIDGE = (0.42, 5.1, 8.15, 0.3)
# The core: the lozenge bar along x, its half-width up the screen where it is full (out to CORE_FULL) and its points
# (x of the tips; the taper's power), its height (half-height at the middle, thinner towards the points: times
# (half-width / full) ^ CORE_THIN), its axis's height, the section's squareness (superellipse power); the orange bars
# round it (x ranges, how much proud); the rings along it.
CORE_W, CORE_FULL, CORE_TIP, CORE_TAPER = 4.25, 5.6, 8.75, 1.6
CORE_H, CORE_THIN, CORE_Z, CORE_POWER = 2.25, 0.55, 2.05, 2.6
BARS = [(-4.0, -3.0), (3.0, 4.0)]
BAR_UP = 0.2
CORE_STEP, CORE_SEGMENTS = 0.35, 24
# The eye: the bezel (inner and outer radius, its height over the core's top, its depth into it), the dome (radius,
# height); the studs above and below it (x0, x1, y0, y1: the upper one; their top over the core's top).
BEZEL = (1.25, 2.05, 0.3, 0.6)
EYE = (1.3, 0.95)
STUD = (-0.55, 1.05, 2.35, 3.95, 0.35)

# Palette indices: the plate's greys (a shade lighter than polish_k_pod's, as the sprite's plate is: its crown 0x09-0x0a
# with the frames' 0x0c-0x0e; greys read darker in the game: metallic 0.3), the core's reds and oranges and the eye's
# blues (index, emission strength).
GREYS = {"slot": 0x02, "wall": 0x05, "edge": 0x08, "plate": 0x0a, "crown": 0x0b, "rail": 0x0d, "bright": 0x0e}
GLOWS = {"bezel": (0x70, 0.05), "core_low": (0x72, 0.12), "core": (0x73, 0.16), "core_top": (0x75, 0.22),
         "bar": (0x79, 0.38), "bar_top": (0x7b, 0.48), "eye": (0x95, 0.25), "glint": (0x99, 0.35)}


def materials():
    pal = k.level_palette()
    m = {key: k.material(f"kcore_{key}", palette=index, metallic=0.3 if key not in ("slot", "wall") else 0.35,
                         roughness=0.34 if key not in ("slot", "wall") else 0.45)
         for key, index in GREYS.items()}
    for key, (index, strength) in GLOWS.items():
        m[key] = k.material(f"kcore_{key}", palette=index, metallic=0.0,
                            roughness=0.4 if key == "bezel" else 0.3 if key.startswith("core") else 0.25,
                            emission=pal[index], emission_strength=strength)
    return m


def canonical(obj):
    """Rebuilds the object's mesh in a fixed order (its vertices by position, each face starting at its smallest
    corner, the faces by their corners), as polish_powerups_specials.py's: the exact boolean returns its result in an
    order that changes from run to run, and the bevel, the shading and the export follow that order."""
    me = obj.data

    def key(co):
        return (round(co.x, 5), round(co.y, 5), round(co.z, 5))
    faces = []
    for poly in me.polygons:
        corners = [key(me.vertices[i].co) for i in poly.vertices]
        start = corners.index(min(corners))
        faces.append((corners[start:] + corners[:start], poly.material_index))
    faces.sort()
    verts = sorted({c for corners, _ in faces for c in corners})
    index = {c: i for i, c in enumerate(verts)}
    mesh = bpy.data.meshes.new(me.name)
    mesh.from_pydata(verts, [], [[index[c] for c in corners] for corners, _ in faces])
    for mat in me.materials:
        mesh.materials.append(mat)
    for poly, (_, material) in zip(mesh.polygons, faces):
        poly.material_index = material
    obj.data = mesh
    bpy.data.meshes.remove(me)
    return obj


# --- The body ------------------------------------------------------------------------------------------------------

def edge_planes():
    """For each edge of the octagon, the crown's plane sloping down to it: z = CROWN where it is EDGE_BAND in, falling
    EDGE_DROP to the edge."""
    planes = []
    n = len(PLAN)
    area = sum(PLAN[i][0] * PLAN[(i + 1) % n][1] - PLAN[(i + 1) % n][0] * PLAN[i][1] for i in range(n))
    for i in range(n):
        (x0, y0), (x1, y1) = PLAN[i], PLAN[(i + 1) % n]
        ex, ey = x1 - x0, y1 - y0
        length = math.hypot(ex, ey)
        # inward normal (the plan runs clockwise when its area is negative)
        nx, ny = (-ey / length, ex / length) if area > 0 else (ey / length, -ex / length)
        slope = EDGE_DROP / EDGE_BAND
        planes.append(lambda x, y, x0=x0, y0=y0, nx=nx, ny=ny, slope=slope:
                      CROWN + slope * ((x - x0) * nx + (y - y0) * ny - EDGE_BAND))
    return planes


def in_window(c):
    """Whether a point lies inside the window's plan."""
    inside = False
    n = len(WINDOW)
    for i in range(n):
        (x0, y0), (x1, y1) = WINDOW[i], WINDOW[(i + 1) % n]
        if (y0 > c.y) != (y1 > c.y):
            x = x0 + (c.y - y0) * (x1 - x0) / (y1 - y0)
            if c.x < x:
                inside = not inside
    return inside


def body(m):
    obj = mk.prism("body", PLAN, BOTTOM, CROWN, m["crown"])
    for i, top in enumerate(edge_planes()):
        mk.boolean(obj, plane_box(f"edge{i}", top), "INTERSECT")
    mk.cleanup(obj)
    canonical(obj)
    cutters = [mk.prism("window", WINDOW, WINDOW_FLOOR, CROWN + 3.0, m["slot"])]
    x0, x1, hy, floor = SLOT
    for side in (-1, 1):
        a, b = sorted((side * x0, side * x1))
        cutters.append(mk.box(f"slot{side}", a, b, -hy, hy, floor, CROWN + 3.0, m["wall"]))
    gx0, gx1, gy0, gy1, gd = GAP
    for sign in (1, -1):
        a, b = sorted((sign * gy0, sign * gy1))
        cutters.append(mk.box(f"gap{sign}", gx0, gx1, a, b, CROWN - gd, CROWN + 3.0, m["slot"]))
    mk.boolean(obj, cutters, "DIFFERENCE")
    mk.cleanup(obj)
    canonical(obj)
    mk.bevel(obj, BEVEL, 2, 30)
    mk.shade(obj, 35)

    def pick(c, n):
        if n.z < -0.5:
            return m["wall"]                                          # underneath
        if in_window(c) and c.z < CROWN - 0.05:
            return m["slot"]                                          # the window's walls and floor
        if abs(c.y) < hy + 0.03 and abs(c.x) > x0 - 0.05 and c.z < CROWN - 0.3:
            return m["slot"] if n.z > 0.5 else m["wall"]              # the flanks' slots
        if gx0 - 0.03 < c.x < gx1 + 0.03 and gy0 - 0.03 < abs(c.y) < gy1 + 0.03 and c.z < CROWN - 0.05:
            return m["slot"]                                          # the frames' gaps
        if n.z < 0.3:
            return m["wall"]                                          # the outer walls
        if LIPS[0] < abs(c.y) < LIPS[1] and abs(c.x) > x0 - 0.3:
            return m["bright"]                                        # the slots' lit lips
        if n.z < 0.95:
            return m["edge"]                                          # the band sloping to the edge
        return None
    mk.paint(obj, pick)
    return obj


def frame(m, prefix):
    """The top half's frame: the U of rails, the plate in its gap and the plate's ridge."""
    parts = []
    for i, (x0, x1, y0, y1) in enumerate(RAILS):
        rail = mk.box(f"{prefix}_rail{i}", x0, x1, y0, y1, CROWN - RAIL_DOWN, CROWN + RAIL_UP, m["rail"])
        mk.bevel(rail, 0.22, 2, 30)
        mk.shade(rail, 35)
        mk.paint(rail, lambda c, n: m["edge"] if n.z < 0.3 else None)
        parts.append(rail)
    x0, x1, y0, y1, below = PLATE
    plate = mk.box(f"{prefix}_plate", x0, x1, y0, y1, CROWN - GAP[4] - 0.2, CROWN - below, m["plate"])
    mk.bevel(plate, 0.3, 2, 30)
    mk.shade(plate, 35)
    mk.paint(plate, lambda c, n: m["wall"] if n.z < 0.3 else None)
    parts.append(plate)
    half, ry0, ry1, up = RIDGE
    ridge = mk.box(f"{prefix}_ridge", MID - half, MID + half, ry0, ry1, CROWN - below - 0.3, CROWN - below + up,
                   m["bright"])
    mk.bevel(ridge, 0.15, 2, 30)
    mk.shade(ridge, 35)
    parts.append(ridge)
    return parts


# --- The core and the eye ------------------------------------------------------------------------------------------

def core_width(x):
    a = abs(x)
    if a <= CORE_FULL:
        return CORE_W
    t = min(1.0, (a - CORE_FULL) / (CORE_TIP - CORE_FULL))
    return CORE_W * max(0.0, 1 - t ** CORE_TAPER) ** 0.5


def on_bar(x):
    return any(x0 <= x <= x1 for x0, x1 in BARS)


def core(m):
    """The lozenge bar along x: superellipse sections, raised over the orange bars, cut into bands by its facets."""
    count = int(round(2 * CORE_TIP / CORE_STEP))
    xs = sorted({-CORE_TIP + 2 * CORE_TIP * i / count for i in range(1, count)} |
                {x + d for x0, x1 in BARS for x in (x0, x1) for d in (-0.06, 0.06)} |
                {s * (CORE_TIP - d) for s in (-1, 1) for d in (0.04, 0.12)})
    rings = []
    for x in xs:
        w = max(core_width(x), 0.02)
        h = CORE_H * (w / CORE_W) ** CORE_THIN
        if on_bar(x):
            w, h = w + BAR_UP, h + BAR_UP
        ring = []
        for j in range(CORE_SEGMENTS):
            a = 2 * math.pi * j / CORE_SEGMENTS
            c, s = math.cos(a), math.sin(a)
            ring.append(Vector((x, math.copysign(abs(c) ** (2 / CORE_POWER), c) * w,
                                CORE_Z + math.copysign(abs(s) ** (2 / CORE_POWER), s) * h)))
        rings.append(ring)
    obj = k.loft("core", rings, None, start_point=(-CORE_TIP, 0.0, CORE_Z), end_point=(CORE_TIP, 0.0, CORE_Z))
    values = []
    for v, n in zip(obj.data.vertices, vertex_normals(obj)):
        lit = n.z - 0.15 * n.x
        if on_bar(v.co.x) or any(abs(v.co.x - x) < 0.065 for x0, x1 in BARS for x in (x0, x1)):
            values.append(10.0 + (1.0 if lit > 0.5 else 0.0))
        else:
            values.append(lit)
    band_split(obj, values, [(-99.0, m["bezel"]), (-0.45, m["core_low"]), (0.15, m["core"]), (0.75, m["core_top"]),
                             (9.5, m["bar"]), (10.5, m["bar_top"])])
    return k.smooth(obj, 50)


def eye(m):
    """The dark bezel ring on the core's top, the blue dome in it, the glowing studs above and below it."""
    top = CORE_Z + CORE_H
    r0, r1, up, down = BEZEL
    bezel = mk.lathe("bezel", [(r0, top - down), (r1, top - down), (r1, top + up - 0.1), (r1 - 0.1, top + up),
                               (r0 + 0.1, top + up), (r0, top + up - 0.1)], (0.0, 0.0), m["bezel"], segments=32)
    k.recalc_normals(bezel)
    mk.shade(bezel, 40, weighted=False)
    radius, height = EYE
    dome = mk.dome("eye", (0.0, 0.0), (radius, radius, height), top - 0.15, m["eye"], 32, 10)
    values = [n.z - 0.3 * n.x + 0.2 * n.y for n in vertex_normals(dome)]
    band_split(dome, values, [(-99.0, m["eye"]), (0.8, m["glint"])])
    k.smooth(dome, 70)
    parts = [bezel, dome]
    x0, x1, y0, y1, up = STUD
    for sign in (1, -1):
        a, b = sorted((sign * y0, sign * y1))
        stud = mk.box(f"stud{sign}", x0, x1, a, b, top - 0.9, top + up, m["bar"])
        mk.bevel(stud, 0.2, 2, 30)
        mk.shade(stud, 35)
        mk.paint(stud, lambda c, n: m["bar_top"] if n.z > 0.8 else None)
        parts.append(stud)
    return parts


def build():
    options = k.args()
    out = mk.outdir(options)
    k.reset()
    m = materials()
    top = frame(m, "top")
    bottom = mirror_y(frame(m, "bottom"))
    parts = triangulate([body(m)] + top + bottom + [core(m)] + eye(m))
    bpy.context.view_layer.update()
    if "check" in options:
        sheet = os.path.join(options["check"], "enemy_K.png")
        mk.compare("k_core_pod (K 245)", mk.coverage(parts, 24, 28), k.sprite_mask(sheet, 245))
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    mk.report(NAME, parts, os.path.join(out, NAME + ".glb"))
    if "preview" in options:
        mk.preview(options["preview"] + NAME, parts, distance=0.6)


if __name__ == "__main__":
    build()
