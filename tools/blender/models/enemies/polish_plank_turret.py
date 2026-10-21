"""SURFACE's brown turret of planks with two guns (sheet 3 sprite 12, 2x2; enemy 205 of episode 4, a ground enemy: 21
of them in SURFACE, on its ground and ground2 layers, each alone; no other level, episode 6's included, places it),
polished (2026-10-21; it replaces wave3_n.py's plank_turret(), a tapered box with two lids, iron bands and two
lathed guns). models.cfg: model plank_turret enemies/plank_turret.glb (unchanged), sprite 3 12 plank_turret yaw=aim
(unchanged).

Its eight frames (12 14 16 50 54 88 90 92; animate 0, none plays by itself) are one turret drawn at eight headings,
lit from one side: 14 points it up the screen (its guns at rows 1-5), 16 up and right, 54 right, 92 down and right,
90 down, 88 down and left, 50 left, 12 up and left; 16, 54 and 92 are 12's, 50's and 88's mirror images in coverage
(IoU 0.99, 1.0, 0.995), 90 is 14 turned round (0.97, a pixel off) and 14 is symmetric about its axis. No other enemy,
launched ones included, shows any of them, and none is another sprite's pixels mirrored, turned or in other ramps. So
one model, authored pointing up the screen as 14 draws it; yaw=aim turns it to the player (SURFACE itself picks the
frames: its events 19 set each turret's frame, most of them 90, pointing down, and turn the first one through 92, 54,
16 and 14 as it slides; facing the player stands in for that). Its origin is where the eight headings balance: the
mean of the frames' centroids, x 0.13, y 0.42 of the cell (PIVOT; the silhouette check puts the model there, turned
to each frame's heading). The frames don't quite agree with each other: 14 and 90 draw the guns 8 pixels apart, the
others about 5; the model follows 14 and 90.

As the frames and their 4x upscales draw it (rows and columns of 14; browns of ramp 10, an outline of 0x02): a box of
planks 14 pixels square (columns 6-19 of rows 6-20), its back corners cut off (rows 19-20, and the back of every
frame); on its top two broad planks running front to back (columns 7-10 and 15-18), their grain along their length,
their front ends lit (0xab-0xae at row 7); between them a channel (columns 11-14) open at the front (a notch in the
box's front edge between the guns, columns 12-13 of row 6), in it a lit block (rows 8-11) whose back end is a V
(rows 12-14: two lit edges meeting at the channel's middle; the A of frame 90), the channel's back part dark (rows
15-19); two guns reaching forward from the box's front under the planks' middles (four pixels apart), each a sleeve
at the box, a barrel with a lit band (row 4) and a lit muzzle ring at its tip (row 2), as the upscales of 50, 54 and
88 show them (two light knobs on each dark barrel).

Built as such a crate: its body a prism of the plan (the back corners chamfered), the notch cut in its front, its
sides boards (dark seams at SEAMS, the boards in two shades), corner posts at the front; the planks wedges of their
plans with a crowned top, bevelled, their tops split into grain strips along their length in three shades (seeded
random widths: the same every run), their edges lit towards the game's sun (the upper left) and dark away from it,
iron nail heads at their ends; the block in the channel a bevelled wedge with the V at its back; the guns lathed
along Y (a bronze sleeve, the barrel, a lit band, the muzzle ring, a dark bore). Every mesh is triangulated before
the export (polish_k_pod.triangulate: the output is the same with and without --check) and joined into one.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen (forward, the guns' way), +Z up from the
ground (z = 0); origin at PIVOT. It stands from z 0 to the planks' tops (centred in height by the game, as its other
ground models without origin).

Replaces wave3_n.py's plank_turret() (its section "# --- 3 12: the plank turret": the @n.model("plank_turret",
mask=None) function, and the plank_turret paragraph of its docstring): remove them so that they don't overwrite this
model.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouette against each
of the eight frames of enemy_3.png, the model turned to the frame's heading), --preview <prefix> (top and 3/4 views),
--headings <prefix> (top views turned to the eight headings beside each other, for looking at).
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
from polish_k_pod import triangulate  # noqa: E402
from polish_deli_boss import join  # noqa: E402
from polish_orb_red import band_split  # noqa: E402
from polish_ring_machine import Region, round_edge  # noqa: E402

NAME = "plank_turret"
PIVOT = (0.13, 0.42)  # where the headings balance (the cell's coordinates): the model's origin
# The frames and the headings they draw (degrees counter-clockwise from up the screen).
FRAMES = [(14, 0.0), (12, 45.0), (50, 90.0), (88, 135.0), (90, 180.0), (92, -135.0), (54, -90.0), (16, -45.0)]

# The crate: half its width, its front and back, the back corners' chamfer, its top; the seams between its boards
# (heights) and their height.
HALF_W, FRONT, BACK, CHAMFER, CRATE_TOP = 6.75, 7.0, -7.35, 1.9, 4.0
SEAMS, SEAM_H = (1.33, 2.67), 0.2
POST = 0.85                          # the front corner posts' size (square)
# The notch in its front between the planks: half-width, depth back from the front, its floor.
SLOT_HW, SLOT_DEPTH, SLOT_FLOOR = 1.8, 1.45, 2.2
# The planks: |x| of their inner and outer edges, their front and back overhang, bottom, top, crown, bevel.
PLANK_IN, PLANK_OUT, PLANK_OVER = 1.8, 6.62, 0.18
PLANK_BOTTOM, PLANK_TOP, CROWN, PLANK_ROUND = 3.65, 5.6, 0.22, 0.7
# The grain: the streaks' spacing across a plank, the borders between its four shades (of grain_value: light,
# plank, darker, streak), how far the dark streaks sink.
GRAIN_STEP, GRAIN, GRAIN_RELIEF = 1.35, (-0.72, 0.5), 0.05
PLANK_COLUMN, PLANK_ROW = 0.24, 0.8  # the planks' grid: across and along them
# The block in the channel: half-width, its front, where its V starts and its tip, bottom, top at its front and at
# its tip (its top slopes down towards the V: a prow pointing back).
BLOCK_HW, BLOCK_FRONT, BLOCK_V, BLOCK_TIP = 1.42, FRONT - SLOT_DEPTH - 0.05, 1.3, -1.35
BLOCK_Z0, BLOCK_Z1, BLOCK_TIP_Z = 3.8, 5.0, 4.35
# The guns: their axes (|x|, z) and their profile along y (y, radius, the part from this ring to the next): the
# sleeve at the crate, the barrel, the lit band, the barrel, the muzzle ring, its face, into the bore.
GUN_X, GUN_Z = 4.22, 3.95
GUN = [(5.9, 1.62, "sleeve"), (7.7, 1.62, "sleeve"), (7.78, 1.2, "barrel"), (8.55, 1.2, "band"),
       (8.6, 1.44, "band"), (9.42, 1.44, "band"), (9.47, 1.17, "barrel"), (10.6, 1.17, "ring"),
       (10.65, 1.5, "ring"), (11.95, 1.5, "ring"), (12.0, 1.3, "ring"), (12.0, 0.72, "bore"), (11.35, 0.62, "bore")]
NAIL_R = 0.24

WOOD = dict(metallic=0.0, roughness=0.72)
BRONZE = dict(metallic=0.55, roughness=0.36)
MATS = {  # name: (palette index, options)
    "plank": (0xa9, WOOD), "plank2": (0xa8, WOOD), "plank3": (0xaa, WOOD), "lit": (0xab, WOOD),
    "edge": (0xa6, WOOD), "board": (0xa7, WOOD), "seam": (0xa3, WOOD),
    "channel": (0xa4, WOOD), "post": (0xa5, WOOD),
    "sleeve": (0xa6, BRONZE), "barrel": (0xa5, BRONZE), "band": (0xaa, BRONZE), "ring": (0xab, BRONZE),
    "nail": (0xa2, dict(metallic=0.5, roughness=0.45)),
    "bore": (0xa1, dict(metallic=0.2, roughness=0.8)),
}


SAME = {"streak": "board", "board2": "edge"}  # (the same shades: one material each)


def materials():
    m = {name: k.material(f"plankt_{name}", palette=index, **opts) for name, (index, opts) in MATS.items()}
    m.update({name: m[other] for name, other in SAME.items()})
    return m


def ccw(points):
    area = sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(points, points[1:] + points[:1]))
    return points if area > 0 else points[::-1]


def crate_plan():
    w, c = HALF_W, CHAMFER
    return ccw([(-w, FRONT), (-w, BACK + c), (-w + c, BACK), (w - c, BACK), (w, BACK + c), (w, FRONT)])


def plank_plan(side):
    """A plank's plan (its outer back corner cut as the crate's): side -1 left, 1 right."""
    back, front = BACK + 0.12, FRONT + PLANK_OVER
    x_in, x_out = PLANK_IN, PLANK_OUT
    # the crate's chamfer line: x - y = HALF_W - BACK - CHAMFER (right side)
    k_line = HALF_W - BACK - CHAMFER
    pts = [(x_in, back), (back + k_line, back), (x_out, x_out - k_line), (x_out, front), (x_in, front)]
    return ccw([(side * x, y) for x, y in pts])


# --- The parts ------------------------------------------------------------------------------------------------------

def crate(m):
    """The crate: a prism of the plan, the notch cut in its front, bevelled, its sides boards with dark seams."""
    body = mk.prism("crate", crate_plan(), 0.0, CRATE_TOP, m["board"])
    mk.boolean(body, mk.box("crate_slot", -SLOT_HW, SLOT_HW, FRONT - SLOT_DEPTH, FRONT + 2.0, SLOT_FLOOR,
                            CRATE_TOP + 2.0), "DIFFERENCE")
    mk.cleanup(body)
    mk.bevel(body, 0.28, 2, 30)
    bm = bmesh.new()
    bm.from_mesh(body.data)
    for z in sorted(set([z0 for z in SEAMS for z0 in (z - SEAM_H / 2, z + SEAM_H / 2)])):
        bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-5, plane_co=(0, 0, z),
                               plane_no=(0, 0, 1))
    bm.to_mesh(body.data)
    bm.free()
    mk.shade(body, 35)

    def pick(c, n):
        if c.z > CRATE_TOP - 0.05 and n.z > 0.7:
            return m["channel"]                    # the top: the channel's floor where the planks leave it bare
        if abs(c.x) < SLOT_HW + 0.05 and c.y > FRONT - SLOT_DEPTH - 0.05 and c.z > SLOT_FLOOR - 0.3:
            return m["seam"]                       # the notch
        if n.z > 0.7:
            return m["channel"]
        for z in SEAMS:
            if abs(c.z - z) < SEAM_H / 2:
                return m["seam"]
        board = sum(c.z > z for z in SEAMS)
        return m["board"] if board % 2 == 0 else m["board2"]
    mk.paint(body, pick)
    parts = [body]
    # The front corner posts.
    for side in (-1, 1):
        x0 = side * (HALF_W + 0.12)
        x1 = side * (HALF_W - POST + 0.12)
        post = mk.box(f"post{side:+d}", min(x0, x1), max(x0, x1), FRONT - POST + 0.12, FRONT + 0.12, 0.0,
                      CRATE_TOP + 0.05, m["post"])
        mk.bevel(post, 0.18, 2, 30)
        mk.shade(post, 35)
        parts.append(post)
    return parts


def grain_value(x, y, seed):
    """The wood's grain on a plank's top, -1 to 1: streaks along the plank (GRAIN_STEP apart across it), wavering
    along its length, bending round a knot (KNOT: where along the plank, seeded), its core the darkest."""
    kx, ky = seed["knot"]
    q = ((x - kx) / 0.95) ** 2 + ((y - ky) / 1.7) ** 2
    phase = (2 * math.pi * (x - seed["x0"]) / GRAIN_STEP + 0.55 * math.sin(y / 2.6 + seed["a"]) +
             0.9 * noise.noise(Vector((x * 0.45 + seed["b"], y * 0.09, seed["c"]))) + 2.0 * math.exp(-q))
    if ((x - kx) / 0.3) ** 2 + ((y - ky) / 0.5) ** 2 < 1.0:
        return 1.0
    return math.sin(phase)


def plank_rows():
    """The y of a plank's rows of vertices: close together at its ends (their rounded edges), PLANK_ROW apart along
    its middle."""
    back, front = BACK + 0.12, FRONT + PLANK_OVER
    ends = [0.0, 0.1, 0.25, 0.45, 0.7, 1.0]
    middle = []
    n = max(1, int(round((front - back - 2 * ends[-1]) / PLANK_ROW)))
    for i in range(1, n):
        middle.append(back + ends[-1] + (front - back - 2 * ends[-1]) * i / n)
    return [back + e for e in ends] + middle + [front - e for e in reversed(ends)]


def plank(side, m, rng):
    """A plank on the crate's top: a grid fine across it (PLANK_COLUMN) and coarser along it (its grain's way),
    squeezed into the crate's chamfered corner; its crowned top rounds off at the edges (PLANK_ROUND, by the distance
    to its outline), straight sides down into the crate. The grain (grain_value) is cut in along smooth contours in
    three shades (polish_orb_red.band_split), the dark streaks sunk a little (GRAIN_RELIEF); the rounded edges lit
    towards the game's sun (the upper left) and dark away from it."""
    plan = plank_plan(side)
    region = Region([plan])
    xs = [abs(x) for x, _ in plan]
    mid = side * (min(xs) + max(xs)) / 2
    half = (max(xs) - min(xs)) / 2
    lift, tilt = rng.uniform(-0.05, 0.05), rng.uniform(-0.008, 0.008)
    seed = {"x0": mid + rng.uniform(-0.5, 0.5), "a": rng.uniform(0, 6.28), "b": rng.uniform(0, 50),
            "c": rng.uniform(0, 50), "knot": (mid + rng.uniform(-0.9, 0.9), rng.uniform(-4.0, 3.0))}
    k_line = HALF_W - BACK - CHAMFER          # the chamfer: |x| = y + k_line
    rows = plank_rows()
    nx = int(round((PLANK_OUT - PLANK_IN) / PLANK_COLUMN))
    across = [0.0, 0.04, 0.1] + [0.1 + 0.8 * i / (nx - 6) for i in range(1, nx - 6)] + [0.9, 0.96, 1.0]
    top = []
    for y in rows:
        x_max = min(PLANK_OUT, y + k_line)
        top.append([(side * (PLANK_IN + (x_max - PLANK_IN) * f), y) for f in across])
    verts, values, faces = [], [], []
    index = {}
    for j, row in enumerate(top):
        dists = region.distance(row)
        for i, (x, y) in enumerate(row):
            g = grain_value(x, y, seed)
            u = (x - mid) / half
            z = PLANK_TOP + lift + tilt * y + CROWN * (1.0 - u * u) - GRAIN_RELIEF * max(0.0, g)
            edge = PLANK_TOP - PLANK_ROUND
            z = edge + (z - edge) * round_edge(float(dists[i]), PLANK_ROUND)
            index[(i, j)] = len(verts)
            verts.append((x, y, z))
            values.append(g)
    cols = len(across)
    for j in range(len(rows) - 1):
        for i in range(cols - 1):
            quad = [index[(i, j)], index[(i + 1, j)], index[(i + 1, j + 1)], index[(i, j + 1)]]
            faces.append(quad if side > 0 else quad[::-1])
    # The sides: the top's outline straight down into the crate.
    loop = ([index[(i, 0)] for i in range(cols)] + [index[(cols - 1, j)] for j in range(1, len(rows))] +
            [index[(i, len(rows) - 1)] for i in reversed(range(cols - 1))] +
            [index[(0, j)] for j in reversed(range(1, len(rows) - 1))])
    if side < 0:
        loop = loop[::-1]
    low = {}
    for a in loop:
        low[a] = len(verts)
        verts.append((verts[a][0], verts[a][1], PLANK_BOTTOM))
        values.append(values[a])
    for a, b in zip(loop, loop[1:] + loop[:1]):
        faces.append([b, a, low[a], low[b]])
    obj = k.mesh_object(f"plank{side:+d}", verts, faces)
    band_split(obj, values, [(-9.0, m["plank3"]), (GRAIN[0], m["plank"]), (GRAIN[1], m["plank2"])])
    if sum(p.normal.z * p.area for p in obj.data.polygons) < 0:
        obj.data.flip_normals()
    k.smooth(obj, 55)

    def pick(c, n):
        if n.z >= 0.55:
            return None
        if c.z < CRATE_TOP + 0.25:
            return m["seam"]                       # where it sits on the crate: a dark gap
        if n.z > 0.2:
            return m["lit"] if (n.y > 0.3 or n.x < -0.3) else m["edge"]
        return m["edge"]
    mk.paint(obj, pick)
    return obj


def block(m):
    """The block in the channel, its back end a V (the A of frame 90)."""
    plan = ccw([(-BLOCK_HW, BLOCK_FRONT), (-BLOCK_HW, BLOCK_V), (0.0, BLOCK_TIP), (BLOCK_HW, BLOCK_V),
                (BLOCK_HW, BLOCK_FRONT)])
    obj = mk.wedge("block", plan, BLOCK_Z0, lambda x, y: BLOCK_TIP_Z + (BLOCK_Z1 - BLOCK_TIP_Z) *
                   (y - BLOCK_TIP) / (BLOCK_FRONT - BLOCK_TIP), m["plank3"])
    mk.bevel(obj, 0.3, 2, 30)
    mk.shade(obj, 35)
    mk.paint(obj, lambda c, n: None if n.z >= 0.9 else (m["lit"] if (n.y > 0.3 or n.x < -0.3) and n.z > 0.2
                                                         else m["edge"]))
    return obj


def nails(m):
    """Iron nail heads at the planks' ends: two at each end of each plank."""
    out = []
    for side in (-1, 1):
        for y in (FRONT - 1.0, BACK + 1.45):
            for f in (0.3, 0.72):
                x = side * (PLANK_IN + (PLANK_OUT - PLANK_IN) * f)
                if y < 0 and f > 0.5:
                    continue                       # (the chamfered corner)
                z = PLANK_TOP + CROWN * (1.0 - ((f - 0.5) / 0.5) ** 2) - 0.12
                out.append(mk.dome(f"nail{len(out)}", (x, y), (NAIL_R, NAIL_R, 0.2), z, m["nail"], segments=10,
                                   steps=3))
    return out


def gun(side, m):
    """A gun: lathed along Y through GUN's profile (sleeve, barrel, band, barrel, muzzle ring, into the bore)."""
    x = side * GUN_X
    rings = [k.ring(y, r, r, 20, z=GUN_Z, x=x) for y, r, _ in GUN]
    obj = k.loft(f"gun{side:+d}", rings, m["sleeve"], start_point=(x, GUN[0][0], GUN_Z),
                 end_point=(x, GUN[-1][0] - 0.2, GUN_Z))
    # Each face takes the part of the ring it starts from (the caps: the first ring's and the last ring's).
    for poly in obj.data.polygons:
        i = min(min(v // 20 for v in poly.vertices), len(GUN) - 1)
        poly.material_index = mk.slot_of(obj, m[GUN[i][2]])
    k.smooth(obj, 50)
    return obj


def build_turret(m):
    rng = random.Random(205)
    parts = crate(m)
    parts += [plank(-1, m, rng), plank(1, m, rng), block(m)]
    parts += nails(m)
    parts += [gun(-1, m), gun(1, m)]
    for obj in parts:
        mk.apply(obj)
    bpy.context.view_layer.update()
    return parts


# --- Checks, previews, export ---------------------------------------------------------------------------------------

def turned(objects, degrees):
    for obj in objects:
        obj.rotation_euler = (0.0, 0.0, math.radians(degrees))
    bpy.context.view_layer.update()


def shifted_overlap(covered, mask):
    """The best overlap with the mask moved a pixel at most either way (the frames don't all turn about one point:
    14's box lies a pixel right of 90's)."""
    h, w = len(mask), len(mask[0])
    best = 0.0
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            both = either = 0
            for y in range(h):
                for x in range(w):
                    ys, xs = y - dy, x - dx
                    m = 0 <= ys < h and 0 <= xs < w and mask[ys][xs]
                    both += covered[y][x] and m
                    either += covered[y][x] or m
            best = max(best, both / max(either, 1))
    return best


def check(objects, sheet):
    """The silhouette against each frame: the model at PIVOT, turned to the frame's heading (and the best overlap with
    the frame moved a pixel at most)."""
    scores, best = [], []
    for sprite, heading in FRAMES:
        turned(objects, heading)
        covered = mk.coverage(objects, 24, 28, centre=(-PIVOT[0], -PIVOT[1]))
        mask = k.sprite_mask(sheet, sprite)
        scores.append(mk.compare("3 %d (heading %+.0f)" % (sprite, heading), covered, mask))
        best.append(shifted_overlap(covered, mask))
        print("  moved a pixel at most: %.3f" % best[-1])
    turned(objects, 0.0)
    print("silhouette overlap, mean of the eight frames: %.3f (moved a pixel at most: %.3f)" % (
        sum(scores) / len(scores), sum(best) / len(best)))


def headings_preview(prefix, objects):
    """Top views turned to the eight headings, side by side (as the frames: 14 12 50 88 90 92 54 16)."""
    copies = []
    for i, (_, heading) in enumerate(FRAMES):
        for obj in objects:
            copy = obj.copy()
            copy.data = obj.data.copy()
            bpy.context.scene.collection.objects.link(copy)
            copy.data.transform(Matrix.Rotation(math.radians(heading), 4, "Z"))
            copy.location = (28.0 * (i - 3.5), 0.0, 0.0)
            copies.append(copy)
    for obj in objects:
        obj.hide_render = True
    mk.preview(prefix, copies, size=(224, 28), scale=6)
    for obj in copies:
        bpy.data.objects.remove(obj)
    for obj in objects:
        obj.hide_render = False


def build():
    options = k.args()
    out = mk.outdir(options)
    k.reset()
    m = materials()
    parts = build_turret(m)
    triangulate(parts)
    turret = join(parts, NAME)
    turret.data.name = NAME
    if "check" in options:
        sheets = options["check"]
        check([turret], os.path.join(sheets, "enemy_3.png") if os.path.isdir(sheets) else sheets)
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    mk.report(NAME, [turret], os.path.join(out, NAME + ".glb"))
    if "preview" in options:
        mk.preview(options["preview"] + NAME, [turret], centre=(-PIVOT[0], -PIVOT[1]))
    if "headings" in options:
        headings_preview(options["headings"], [turret])


if __name__ == "__main__":
    build()
