"""The glass hatch of DELI (sheet C sprite 1, 2x2: 24 x 28 pixels; enemy 142 and its episode 6 copies 1583, 1584;
DELI and VAULT on the ground, BONUS in the sky, HARVEST on the top layer, a few in episode 2's skies; its animation
1 3 5 9 11 13 11 9 7 5 3 1), polished (2026-10-19; it replaces wave3_x.py's glass_hatch(), a frame round a
see-through pane with the machine shown under it in every frame). models.cfg: sprite c 1 glass_hatch yaw=0,
frame c 3 glass_hatch_3, frame c 5 glass_hatch_5, frame c 7 glass_hatch_7, frame c 9 glass_hatch_9, frame c 11
glass_hatch_11, frame c 13 glass_hatch_13 (and a model line for each, see the report).

As the sprites and their 4x upscales draw it: a square of glass let into the floor, the pale frame round it
(columns 2-20 of rows 3-24) and the floor's blue-grey bricks round that; through the glass the bricks of a shallow
pit, and a broad glint running over the glass from its upper left to its lower right. The frames open it: in 3 the
glint breaks into a crack and something red pushes up through it (rows 7-10), in 5 the glass is gone and a machine
stands in the pit, dim: a head of three red pods side by side (columns 7-15 of rows 6-14; joined at the back,
apart at their front ends), and either side a grey claw reaching out and down the screen to the pit's floor
(columns 4-7 and 15-18 of rows 10-20); in 7 it is fully up, its pods dark red with orange slots down their middles;
in 9, 11 and 13 the slots glow, brighter each time, the middle one white-yellow in 13; then back down the same way.

The frame and the bricks round it are the map's: DELI, BONUS, HARVEST and VAULT lay a hatch tile there (shape 581:
the same frame and floor, its glass broken, a red speck in it; the enemies stand on it). So the model leaves them
out; it is what the sprite adds inside the frame (columns 3-19 of rows 4-23): the pit's floor (opaque, its bricks
in three shades: it covers the broken glass the map paints), the glass, and the machine.

The glass is two leaves meeting along the glint (its seam): see-through, a little blue, the glint a brighter, less
clear band along the seam where the leaves' bevelled edges catch the light. In 3 the leaves part along the seam and
tilt up at it, pushed open by the pods' crowns coming up between them; in 5 the leaves are gone (folded away) and
the machine is up to RISE_5 of its height (sunk into the pit: what would be below the floor is cut away). One model
per frame: glass_hatch (1), glass_hatch_3, _5, _7, _9, _11 and _13; the machine's colours and glow change with the
frames.

All the frames have the same bounds, z 0 to PIN_Z: each carries a speck at PIN_Z (a triangle a thousandth of a
pixel across, invisible) above the machine's top, so the closed frames, whose glass lies low, reach as high as the
open ones. The game centres a model in height on its layer and lifts it to 0.3 if it would reach lower; as half of
PIN_Z is more than the ground enemies' layer height (4) less 0.3, every frame is placed alike, on the ground.

The machine is symmetric about the sprite's column 11 (x = -0.5 here; it is built about x = 0 and moved there); so
are the pit and the glass (columns 3-19, built where they are).
Origin at the sprite's centre (pixel 12, 14); +Y up the sprite, +Z up from the ground (z = 0).

Replaces wave3_x.py's glass_hatch() (and its @x.model entry; wave3_x_art.py's HATCH, HATCH_OPEN and HATCH_HOT go
with it): remove it so that it doesn't overwrite these models.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each frame's silhouette
against the pit, columns 3-19 of rows 4-23), --preview <prefix>, --only <name,...>.
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402

AXIS_X = -0.5
PIT = (-9.0, 8.0, -10.0, 10.0)        # the frame's opening: columns 3-19, rows 4-23
FLOOR_TOP = 0.08
# The pit's bricks: the seams of its floor (as the sprite draws them through the glass: x of vertical seams per
# band of rows, y of the horizontal ones).
BRICK_ROWS = [(10.0, 5.5, (-1.5, 6.5)), (5.5, -0.5, (-6.0, 2.5)), (-0.5, -6.5, (-1.5, 6.5)), (-6.5, -10.0, (-6.0, 2.5))]
SEAM_W = 0.32
# The glass: its leaves' top and thickness, the seam between them through the glint's points (x, y), the glint's
# half-width along it (wider at its upper left, as the sprite's).
GLASS_Z, GLASS_T = 0.62, 0.32
SEAM = [(-9.6, 10.6), (-6.4, 8.4), (-3.4, 5.6), (-1.2, 2.6), (0.4, -0.8), (2.6, -3.6), (5.4, -6.4), (8.6, -10.6)]
GLINT_W = [(0.0, 0.65), (0.25, 1.15), (0.45, 0.95), (0.7, 0.6), (1.0, 0.5)]
LEAF_GAP_3 = 0.2                      # how far each leaf moves back from the seam in 3
LEAF_TILT_3 = math.radians(9.0)       # and tilts up at the seam
# The machine (built about x = 0, moved to AXIS_X): its pods (x, y of the back end, y of the front end, half-width,
# top height, half-height), egg-shaped, broadest towards the back, lying on a dark base.
PODS = [(-3.45, 7.0, -0.4, 1.55, 5.5, 1.55), (0.0, 7.6, -1.2, 1.95, 6.3, 1.9), (3.45, 7.0, -0.4, 1.55, 5.5, 1.55)]
POD_WIDEST = 0.62                     # where along a pod (0 front .. 1 back) it is broadest
SLOT_W = 0.4                          # the slot's half-width, a share of the pod's
BASE = (0.0, 3.4, 3.9, 3.3, 2.6)      # x, y, half-width, half-depth, height
# The left claw (mirrored for the right): an arm out of the base's side to its elbow (x, y, z, radius), then the
# blade down the screen to its tip: sections (x, y, z, half-width, half-height), broad at the elbow, pointed at the
# tip on the floor (the sprite's columns 4-5 of rows 11-13, then 4-7 of rows 14-18 and 6-7 of rows 19-20).
CLAW_ARM = [(-3.0, 3.4, 2.9, 0.62), (-4.8, 3.1, 3.55, 0.6), (-6.0, 2.5, 3.75, 0.62), (-6.55, 1.6, 3.65, 0.7)]
CLAW_BLADE = [(-6.6, 1.9, 3.6, 0.85, 0.75), (-6.75, 0.6, 3.5, 1.35, 0.7), (-6.6, -1.4, 3.05, 1.6, 0.62),
              (-6.2, -3.2, 2.2, 1.35, 0.55), (-5.75, -4.8, 1.25, 0.95, 0.45), (-5.4, -6.0, 0.5, 0.5, 0.32),
              (-5.2, -6.6, 0.15, 0.15, 0.15)]
RISE_5 = 0.62                         # how far up the machine is in 5
RISE_3 = 0.3                          # and in 3 (the pods' crowns between the leaves)
PIN_Z = 7.7

# The frames: (model, sprite, glass state, machine rise, the pods' body (palette index, glow), the three slots
# (left, middle, right): (palette index, glow)).
FRAMES = [
    ("glass_hatch", 1, "closed", None, None, None),
    ("glass_hatch_3", 3, "cracked", RISE_3, (0x43, 0.25), [(0x46, 0.3)] * 3),
    ("glass_hatch_5", 5, None, RISE_5, (0xa4, 0.0), [(0x46, 0.15), (0x47, 0.2), (0x46, 0.15)]),
    ("glass_hatch_7", 7, None, 1.0, (0x44, 0.0), [(0x7a, 0.9), (0x73, 0.5), (0x75, 0.6)]),
    ("glass_hatch_9", 9, None, 1.0, (0x71, 0.35), [(0x7b, 1.6), (0x75, 1.0), (0x78, 1.3)]),
    ("glass_hatch_11", 11, None, 1.0, (0x72, 0.45), [(0x7b, 1.7), (0x7c, 2.0), (0x78, 1.4)]),
    ("glass_hatch_13", 13, None, 1.0, (0x73, 0.55), [(0x7b, 1.9), (0x7f, 3.0), (0x7b, 1.9)]),
]


# --- The pit --------------------------------------------------------------------------------------------------

def pit_floor(m):
    """The pit's floor: a plate filling the opening, its bricks in three shades with dark seams between."""
    x0, x1, y0, y1 = PIT
    plate = mk.box("pit_floor", x0, x1, y0, y1, 0.0, FLOOR_TOP, m["floor"])
    bm = bmesh.new()
    bm.from_mesh(plate.data)
    cuts = []
    for ya, yb, xs in BRICK_ROWS:
        cuts += [((0, ya - SEAM_W / 2, 0), (0, 1, 0)), ((0, ya + SEAM_W / 2, 0), (0, 1, 0))]
        for x in xs:
            cuts += [((x - SEAM_W / 2, 0, 0), (1, 0, 0)), ((x + SEAM_W / 2, 0, 0), (1, 0, 0))]
    for co, no in cuts:
        top = [f for f in bm.faces if f.normal.z > 0.9]
        geom = list({v for f in top for v in f.verts}) + list({e for f in top for e in f.edges}) + top
        bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-5, plane_co=co, plane_no=no)
    bm.to_mesh(plate.data)
    bm.free()

    def pick(c, n):
        if n.z < 0.9:
            return None
        for ya, yb, xs in BRICK_ROWS:
            if abs(c.y - ya) < SEAM_W / 2 + 1e-3:
                return m["seam"]
            if yb < c.y < ya:
                if any(abs(c.x - x) < SEAM_W / 2 + 1e-3 for x in xs):
                    return m["seam"]
                bricks = [x0] + list(xs) + [x1]
                i = sum(c.x > x for x in xs)
                j = BRICK_ROWS.index((ya, yb, xs))
                return (m["floor"], m["floor_light"], m["floor_dark"])[(i + 2 * j) % 3]
        return None
    mk.paint(plate, pick)
    return plate


# --- The glass ------------------------------------------------------------------------------------------------

def seam_point(t):
    """The point at t (0 at the upper left, 1 at the lower right) along the seam (a smooth curve through SEAM)."""
    pts = [Vector((x, y, 0)) for x, y in SEAM]
    n = len(pts) - 1
    f = min(n - 1e-6, max(0.0, t * n))
    i = int(f)
    u = f - i
    p0, p1 = pts[max(i - 1, 0)], pts[i]
    p2, p3 = pts[i + 1], pts[min(i + 2, n)]
    u2, u3 = u * u, u * u * u
    return 0.5 * (2 * p1 + (-p0 + p2) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u2 + (-p0 + 3 * p1 - 3 * p2 + p3) * u3)


def seam_polyline(count=40):
    return [seam_point(i / count) for i in range(count + 1)]


def seam_distance(x, y, line):
    """Signed distance from the seam: positive on the upper right leaf's side; and where along it (0..1)."""
    p = Vector((x, y, 0))
    best = (1e9, 0.0, 1.0)
    for i in range(len(line) - 1):
        a, b = line[i], line[i + 1]
        ab = b - a
        t = max(0.0, min(1.0, (p - a).dot(ab) / ab.length_squared))
        q = a + ab * t
        d = (p - q).length
        if d < best[0]:
            side = 1.0 if ab.x * (p.y - a.y) - ab.y * (p.x - a.x) < 0 else -1.0
            best = (d, (i + t) / (len(line) - 1), side)
    return best[0] * best[2], best[1]


def glint_width(t):
    for (t0, w0), (t1, w1) in zip(GLINT_W, GLINT_W[1:]):
        if t0 <= t <= t1:
            return w0 + (w1 - w0) * (t - t0) / (t1 - t0)
    return GLINT_W[-1][1]


def leaves(m, state):
    """The glass's two leaves: the opening split along the seam, each a thin plate whose edges are bevelled, the
    glint a band along the seam; in the cracked state each moved back from the seam and tilted up at it."""
    inner = 0.12 if state == "closed" else 0.4  # the leaves stop a little inside the frame's opening
    x0, x1, y0, y1 = PIT[0] + inner, PIT[1] - inner, PIT[2] + inner, PIT[3] - inner
    line = seam_polyline()

    def inside(q):
        return x0 <= q.x <= x1 and y0 <= q.y <= y1

    def clip_end(a, b):
        """Where the segment from a (inside) to b (outside) leaves the opening's rectangle."""
        lo, hi = 0.0, 1.0
        for _ in range(50):
            mid = (lo + hi) / 2
            if inside(a.lerp(b, mid)):
                lo = mid
            else:
                hi = mid
        return a.lerp(b, lo)
    pts = [p for p in line if inside(p)]
    seam = [clip_end(pts[0], line[0])] + pts + [clip_end(pts[-1], line[-1])]

    def perimeter(q):
        """Where q (on the rectangle's edge) lies round it: 0 at the lower left corner, counter-clockwise, 4 round."""
        e = 1e-4
        if abs(q.y - y0) < e:
            return (q.x - x0) / (x1 - x0)
        if abs(q.x - x1) < e:
            return 1 + (q.y - y0) / (y1 - y0)
        if abs(q.y - y1) < e:
            return 2 + (x1 - q.x) / (x1 - x0)
        return 3 + (y1 - q.y) / (y1 - y0)
    corners = [(0.0, (x0, y0)), (1.0, (x1, y0)), (2.0, (x1, y1)), (3.0, (x0, y1))]
    s_start, s_end = perimeter(seam[0]), perimeter(seam[-1])
    # Round from the seam's end back to its start, one way and the other: the corners passed.
    ccw = sorted(((c - s_end) % 4, xy) for c, xy in corners if 0 < (c - s_end) % 4 < (s_start - s_end) % 4)
    cw = sorted(((s_end - c) % 4, xy) for c, xy in corners if 0 < (s_end - c) % 4 < (s_end - s_start) % 4)
    seam2 = [(q.x, q.y) for q in seam]
    outlines = [seam2 + [xy for _, xy in ccw], seam2 + [xy for _, xy in cw]]
    made = []
    for i, outline in enumerate(outlines):
        leaf = mk.prism(f"leaf{i}", outline, GLASS_Z - GLASS_T, GLASS_Z, m["glass"])
        mk.bevel(leaf, 0.14, 2, 30)
        # The glint: the top's faces near the seam, split along the band's edge so it runs smoothly.
        bm = bmesh.new()
        bm.from_mesh(leaf.data)
        top = [f for f in bm.faces if f.normal.z > 0.7]
        tri = bmesh.ops.triangulate(bm, faces=top)["faces"]
        edges = list({e for f in tri for e in f.edges})
        bmesh.ops.subdivide_edges(bm, edges=edges, cuts=2, use_grid_fill=False)
        bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3])
        values = {}
        for v in bm.verts:
            d, t = seam_distance(v.co.x, v.co.y, line)
            values[v] = abs(d) - glint_width(t)
        mk.split_along(bm, values, 0.0)
        bm.to_mesh(leaf.data)
        bm.free()

        def pick(c, n):
            if n.z < 0.7:
                return m["glass_edge"]
            d, t = seam_distance(c.x, c.y, line)
            return m["glint"] if abs(d) < glint_width(t) else None
        mk.paint(leaf, pick)
        k.smooth(leaf, 35)
        if state == "cracked":
            # Back from the seam and tilted up at it: turned about a line along the seam through the leaf's far side.
            centre = sum((Vector((x, y, 0)) for x, y in outline), Vector()) / len(outline)
            direction = (seam[-1] - seam[0]).normalized()
            normal = Vector((-direction.y, direction.x, 0))
            if (centre - seam[0]).dot(normal) < 0:
                normal = -normal  # towards the leaf, away from the seam
            far = max((Vector((x, y, 0)) for x, y in outline), key=lambda q: (q - seam[0]).dot(normal))
            pivot = Vector((far.x, far.y, GLASS_Z - GLASS_T))
            mid = seam[len(seam) // 2]
            for sign in (1.0, -1.0):
                rot = Matrix.Translation(pivot) @ Matrix.Rotation(LEAF_TILT_3 * sign, 4, direction) @ \
                    Matrix.Translation(-pivot)
                if (rot @ Vector((mid.x, mid.y, GLASS_Z))).z > GLASS_Z:
                    break
            leaf.data.transform(Matrix.Translation(normal * LEAF_GAP_3) @ rot)
        made.append(leaf)
    return made


# --- The machine ------------------------------------------------------------------------------------------------

def pod(name, x, y_back, y_front, half_w, top, half_h, mat_body, mat_slot):
    """An egg-shaped pod lying along y, broadest towards its back, its top at `top`, its slot (a band down its
    middle) painted."""
    rings = []
    steps = 16
    for i in range(steps + 1):
        s = i / steps                     # 0 at the front tip .. 1 at the back
        y = y_front + (y_back - y_front) * s
        # The egg's profile: rises fast at the back, tapers long to the front.
        if s <= POD_WIDEST:
            f = math.sin((math.pi / 2) * (s / POD_WIDEST)) ** 0.85
        else:
            f = math.cos((math.pi / 2) * ((s - POD_WIDEST) / (1 - POD_WIDEST))) ** 0.6
        f = max(f, 0.02)
        rings.append(k.ring(y, half_w * f, half_h * f, 20, z=top - half_h, x=x))
    obj = k.loft(name, rings[1:-1], mat_body, start_point=(x, y_front, top - half_h * 1.1),
                 end_point=(x, y_back, top - half_h))
    width = half_w * SLOT_W
    floor = top - half_h * 0.45          # the slot runs over the pod's upper part only
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    mk.split_along(bm, {v: abs(v.co.x - x) - width for v in bm.verts}, 0.0)
    mk.split_along(bm, {v: floor - v.co.z for v in bm.verts}, 0.0)
    bm.to_mesh(obj.data)
    bm.free()
    k.smooth(obj, 70)
    if mat_slot is not None:
        mk.paint(obj, lambda c, n: mat_slot if abs(c.x - x) < width and c.z > floor else None)
    return obj


def machine(m, rise):
    """The pods, the base under them, the claws; moved down by (1 - rise) of its height and cut at the floor."""
    parts = []
    for i, (x, yb, yf, hw, top, hh) in enumerate(PODS):
        parts.append(pod(f"pod{i}", x, yb, yf, hw, top, hh, m["pod"], m[("slot", i)]))
    bx, by, bw, bd, bh = BASE
    base = mk.lathe("base", [(0.01, 0.0), (1.0, 0.0), (1.0, bh * 0.7), (0.85, bh), (0.01, bh)], (bx, by), m["base"],
                    32, squash=(bw, bd))
    k.smooth(base, 40)
    parts.append(base)
    arm = mk.smooth_tube("claw", CLAW_ARM, m["claw"], 12)
    k.smooth(arm, 60)
    parts.append(arm)
    # The blade: rounded-box sections along its path, turned to face along it, lit along its top.
    pts = mk.chaikin([tuple(p) for p in CLAW_BLADE], 2, closed=False)
    rings = []
    for i, (x, y, z, hw, hh) in enumerate(pts):
        a, b = Vector(pts[max(i - 1, 0)][:3]), Vector(pts[min(i + 1, len(pts) - 1)][:3])
        t = (b - a).normalized()
        side = Vector((-t.y, t.x, 0)).normalized()
        up = side.cross(t).normalized()
        if up.z < 0:
            up = -up
        ring = []
        for j in range(16):
            u, v = mk.superellipse_point(2 * math.pi * j / 16, 2.6)
            ring.append(Vector((x, y, z)) + side * (u * hw) + up * (v * hh))
        rings.append(ring)
    blade = k.loft("blade", rings, m["claw"], end_point=tuple(pts[-1][:3]))
    k.smooth(blade, 50)
    mk.paint(blade, lambda c, n: m["claw_dark"] if n.z < -0.3 else None)
    parts.append(blade)
    for obj in list(parts):
        if obj.name in ("claw", "blade"):
            parts.append(k.mirror_x(obj, obj.name + "_r"))
    height = max(p[4] for p in PODS)
    drop = (1.0 - rise) * height
    for obj in parts:
        mk.apply(obj)
        obj.data.transform(Matrix.Translation((AXIS_X, 0, -drop)))
        if min(v.co.z for v in obj.data.vertices) < FLOOR_TOP * 0.5:  # what is below the pit's floor is cut away
            bm = bmesh.new()
            bm.from_mesh(obj.data)
            bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-5,
                                   plane_co=(0, 0, FLOOR_TOP * 0.5), plane_no=(0, 0, -1), clear_outer=True)
            bm.to_mesh(obj.data)
            bm.free()
    return [o for o in parts if len(o.data.polygons) > 0]


def pin(m):
    """A speck at PIN_Z (a triangle a thousandth of a pixel across, in the pit's middle): every frame reaches as
    high, so all have the same bounds."""
    e = 0.001
    x = AXIS_X
    return k.mesh_object("pin", [(x, 0, PIN_Z), (x + e, 0, PIN_Z), (x, e, PIN_Z)], [(0, 1, 2)], m["floor"])


# --- Build --------------------------------------------------------------------------------------------------------

def materials(body, slots):
    glow = k.level_palette()

    def mat(name, index, strength=0.0, metallic=0.1, roughness=0.3):
        if strength > 0:
            return k.material(name, palette=index, metallic=metallic, roughness=roughness, emission=glow[index],
                              emission_strength=strength)
        return k.material(name, palette=index, metallic=metallic, roughness=roughness)
    m = {
        "floor": mat("hatch_floor", 0x65, metallic=0.3, roughness=0.55),
        "floor_light": mat("hatch_floor_light", 0x66, metallic=0.3, roughness=0.55),
        "floor_dark": mat("hatch_floor_dark", 0x64, metallic=0.3, roughness=0.55),
        "seam": mat("hatch_floor_seam", 0x62, metallic=0.2, roughness=0.7),
        "glass": k.material("hatch_glass", palette=0x68, metallic=0.0, roughness=0.12, alpha=0.28),
        "glint": k.material("hatch_glint", palette=0x6c, metallic=0.0, roughness=0.08, alpha=0.8),
        "glass_edge": k.material("hatch_glass_edge", palette=0x6a, metallic=0.0, roughness=0.1, alpha=0.6),
        "claw": mat("hatch_claw", 0x08, metallic=0.55, roughness=0.3),
        "claw_dark": mat("hatch_claw_dark", 0x03, metallic=0.5, roughness=0.4),
        "base": mat("hatch_base", 0x02, metallic=0.4, roughness=0.5),
    }
    if body is not None:
        m["pod"] = mat(f"hatch_pod_{body[0]:x}", body[0], body[1], roughness=0.25)
        for i, (index, strength) in enumerate(slots):
            m[("slot", i)] = mat(f"hatch_slot_{index:x}", index, strength, roughness=0.2)
    return m


def pit_mask():
    mask = [[False] * 24 for _ in range(28)]
    for r in range(4, 24):
        for c in range(3, 20):
            mask[r][c] = True
    return mask


def build():
    options = k.args()
    out = mk.outdir(options)
    only = options.get("only", "").split(",") if "only" in options else None
    for name, sprite, glass, rise, body, slots in FRAMES:
        if only and name not in only:
            continue
        k.reset()
        m = materials(body, slots)
        made = [pit_floor(m)]
        if glass is not None:
            made += leaves(m, glass)
        if rise is not None:
            made += machine(m, rise)
        made.append(pin(m))
        parts = mk.meshes()
        for obj in parts:
            mk.apply(obj)
        bpy.context.view_layer.update()
        if "check" in options:
            mk.compare("%s (C %d, the pit)" % (name, sprite), mk.coverage(parts, 24, 28), pit_mask())
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        mk.report(name, parts, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, parts)


if __name__ == "__main__":
    build()
