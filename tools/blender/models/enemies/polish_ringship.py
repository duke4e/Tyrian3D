"""HARVEST's machine on a ring frame, drawn from two sprites of sheet 5 side by side (2x2 each): the pod, 39, at the
left of the ring, 41 (enemies 66 and 67 of episode 4, on the top layer, 41 always 24 pixels right of 39), and its
mirror image, the ring 43 left of the pod 45 (enemies 68 and 69): 43 and 45 are 41 and 39 mirrored pixel for pixel.
About 55 of each; the pairs slide across the screen together (models.cfg: model ringship_pod / ringship_ring /
ringship_ring_r / ringship_pod_r ... origin; sprite 5 39 ringship_pod yaw=0 and so on), polished (2026-10-19; it
replaces wave3_l_parts.py's ring ship).

The machine is built whole, lying along x, and cut along the sprites' edge (x = 0 here) into the two pieces, each
moved so that its sprite's centre is its origin (base on the layer): drawn at their own places they meet again, and
the cut pieces keep the whole's shading across the cut (polish_redjet.py's method). The mirror image is the whole
mirrored (its shading mirrored with it) and cut alike.

As the 4x upscales draw it (the whole 48 x 28 picture, columns 0-47, the machine's axis along row 13):
- a blue bullet pod pointing left (columns 2-11, 15 pixels across at its back), its upper flank lit, a grey rod
  lying along its crest from the nose to two thirds of the way back (rows 12-14);
- a bright steel collar round the pod's back (column 12);
- behind it a dark tail cone narrowing to the ring (columns 13-22), two small blue lights on either flank (rows 8-9
  and 17-18), and along its crest the grey shaft with a light blue window, a dark slot along its middle (columns
  16-22 of rows 12-14), ending in a bright flange where it meets the ring;
- the ring frame: a thick steel ring round an opening (columns 22-36, rows 5-21), the opening see-through where
  nothing fills it, a glossy blue sphere in its left half (columns 24-30, rows 10-16) on the shaft's end;
- four arms on the ring: the two on the left rising from it and turning towards the pod, each ending in a blue
  claw pointing left (rows 4 and 22, reaching column 21); the two on the right curving out and round a blue
  block on the ring's right side (columns 37-42, rows 10-16), a blue panel set in each (columns 37-39 of rows
  5-7 and 19-21); the block lit along its left side, a small light at its upper left.

The pod, its tail cone and the shaft are one body turned round the machine's axis (its sections a little flatter
than round, SQUASH); the rod, the rail and the window lie along its crest; the ring is a band lofted round the
opening (rounded-rectangle sections between two superellipses), the arms are plates in plan sunk into it, extruded
and bevelled (polish_machine_kit), the right ones with the blue panels set in pockets. Colours: the sprites' blues
(ramp 3) and greys (ramp 0); the window, the lights on the cone, the block's lamp and the sphere glow a little in
their own colours (the sphere is seen mostly from its unlit side).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera. The whole's
x = 0 is the edge between the sprites (column 24 of the picture), y = 0 its middle row's top edge (row 14), so a
point (column, row) of the picture's pixel grid is (c - 24, 14 - r) (px()). The machine's axis runs along y =
AXIS_Y at the height AXIS_Z; it rests on z = 0.

Replaces wave3_l_parts.py's ring ship (RING, RING_PIECES, ring_materials(), build_ringship(), ring_piece(), its
four PIECES entries and its w.whole("ringship", ...) line): remove them so that they don't overwrite these models.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes of the
whole and of each piece against enemy_5.png), --preview <prefix> (the whole's and each piece's views).
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
from polish_redjet import Curve  # noqa: E402

AXIS_Y, AXIS_Z = 0.5, 5.45
SQUASH = 0.72          # the round parts' height over their width

# The pieces: (model, sprite, the box it covers in the whole (x0, x1, y0, y1)); the mirrored whole's likewise.
PIECES = [("ringship_pod", 39, (-24.0, 0.0, -14.0, 14.0)), ("ringship_ring", 41, (0.0, 24.0, -14.0, 14.0))]
MIRRORED = [("ringship_ring_r", 43, (-24.0, 0.0, -14.0, 14.0)), ("ringship_pod_r", 45, (0.0, 24.0, -14.0, 14.0))]


def px(c, r):
    """A point of the whole picture's pixel grid (column, row) in the whole's coordinates."""
    return (c - 24.0, 14.0 - r)


# --- The body: pod, tail cone and shaft, one round body along x ---------------------------------------------
# Its radius in plan along x (half a pixel inside the sprites' outline): the pod's ogive from the nose (column 2)
# to the collar (column 12), the tail cone (columns 13-21) and the shaft (rows 11-15) to the sphere.
BODY = Curve([(-21.75, 0.0), (-21.45, 1.5), (-20.8, 2.75), (-20.0, 3.65), (-19.0, 4.5), (-18.0, 5.15), (-17.0, 5.7),
              (-16.0, 6.1), (-15.0, 6.45), (-14.0, 6.75), (-13.0, 6.95), (-12.2, 7.05), (-11.6, 6.75), (-11.0, 6.5),
              (-9.0, 6.4), (-7.0, 6.25), (-6.0, 5.95), (-5.0, 5.4), (-4.0, 4.65), (-3.2, 3.6), (-2.6, 2.85),
              (-2.0, 2.6), (1.5, 2.6)])
NOSE_TIP, BODY_END = -21.75, 1.5
POD_END, CONE_END = -12.2, -2.7     # the pod's blue ends at the collar, the cone's dark at the shaft
COLLAR = (-12.1, -11.15, 7.35)       # its x from, to and its radius in plan (column 12)
GROOVE_X = -12.35                   # a dark groove in front of the collar
FLANGE = (-1.6, -0.7, 3.35)         # the bright flange where the shaft meets the ring
# The grey rod on the pod's crest (columns 3-8 of rows 12-14): its x from, to, half-width, height above the crest.
POD_ROD = (-20.9, -14.7, 1.3, 0.55)
# The grey rail on the cone's crest (columns 13-22) and the window in it (columns 16-22 of rows 12-14).
RAIL = (-11.2, -1.2, 2.35, 0.45)
WINDOW = (-8.0, -1.9, 1.45, 0.6)    # x from, to, half-width, the frame's width
# The blue lights on the cone's flanks: (x from, to, y of their middle on the upper flank); the lower flank's
# mirror them about the axis.
TABS = [(-10.1, -7.0, 5.05, 0.8), (-6.0, -3.4, 4.45, 0.6)]

# --- The ring frame and its arms ------------------------------------------------------------------------------
RING_CENTRE = (5.5, AXIS_Y)
RING_OUTER, RING_INNER = (7.6, 9.1), (4.6, 5.95)     # half-widths and half-heights
RING_POWER = (2.8, 2.5)                              # superellipses (2: an ellipse), the outer edge squarer
RING_SECTION_POWER = 4.0                             # the band's section: a rounded rectangle
FRAME_Z = (AXIS_Z - 1.9, AXIS_Z + 1.9)
ARM_BEVEL = 0.7
# The arms in plan, upper ones (column, row); the lower ones mirror them about the axis.
ARM_LEFT = [(26.8, 6.6), (25.0, 5.6), (24.0, 4.2), (24.0, 2.6), (25.0, 1.5), (26.8, 1.3), (28.4, 2.0), (29.6, 3.6),
            (31.0, 5.8)]
CLAW = [(20.5, 4.5), (21.6, 3.65), (23.6, 3.45), (25.6, 3.6), (26.6, 4.3), (26.4, 5.2), (24.6, 5.6), (22.4, 5.45),
        (21.1, 5.1)]
ARM_RIGHT = [(33.4, 7.2), (33.5, 4.6), (34.2, 3.2), (35.8, 3.0), (38.6, 4.3), (41.6, 5.7), (43.4, 7.0), (43.7, 8.7),
             (43.0, 9.9), (40.0, 10.0), (37.0, 9.9), (35.4, 9.7), (34.6, 9.2)]
PANEL = [(36.4, 4.9), (38.6, 5.3), (40.6, 6.4), (40.9, 7.6), (39.4, 8.2), (36.8, 7.8), (35.9, 6.4)]
# The blue block on the ring's right (columns 37-42, rows 10-16): x from, to; half-width (y), half-height (z).
BLOCK = (12.4, 19.7, 3.75, 2.75)
BLOCK_LIGHT = (14.3, 2.55)          # the small light at its upper left
SPHERE = ((3.5, AXIS_Y, AXIS_Z), 4.0)


# --- Helpers --------------------------------------------------------------------------------------------------

def ring_x(x, r, segments=40, squash=SQUASH, cy=AXIS_Y, cz=AXIS_Z):
    return [Vector((x, cy + r * math.cos(2 * math.pi * j / segments), cz + squash * r * math.sin(2 * math.pi * j / segments)))
            for j in range(segments)]


def lathe_x(name, profile, mat, segments=40, squash=SQUASH):
    rings = [ring_x(x, max(r, 1e-3), segments, squash) for x, r in profile]
    return k.loft(name, rings, mat, start_point=(profile[0][0], AXIS_Y, AXIS_Z), end_point=(profile[-1][0], AXIS_Y, AXIS_Z))


def crest(x, dy=0.0):
    """The body's top at x, dy off its crest line in plan."""
    r = BODY(min(max(x, NOSE_TIP), BODY_END))
    return AXIS_Z + SQUASH * math.sqrt(max(r * r - dy * dy, 0.0))


def plan(points, mirror=False, smooth=2):
    """An outline given as (column, row) points, its corners rounded (smooth: Chaikin's passes), optionally
    mirrored about the axis."""
    pts = mk.chaikin([px(c, r) for c, r in points], smooth) if smooth else [px(c, r) for c, r in points]
    if mirror:
        pts = [(x, 2 * AXIS_Y - y) for x, y in reversed(pts)]
    return ccw(pts)


def ccw(points):
    area = sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(points, points[1:] + points[:1]))
    return points if area > 0 else list(reversed(points))


def rounded_bar(name, x0, x1, half, top, bottom, mat, steps=26, ends=0.9):
    """A bar along x lying on the body's crest: rounded-rectangle sections, half-width half, its top `top` above
    the crest (and its underside `bottom` below it), its ends rounded over `ends`."""
    rings = []
    for i in range(steps + 1):
        x = x0 + (x1 - x0) * i / steps
        f = min(1.0, (x - x0) / ends, (x1 - x) / ends)
        f = math.sqrt(max(0.0, 1 - (1 - max(f, 0.0)) ** 2))
        w = max(half * (0.35 + 0.65 * f), 0.05)
        zc = crest(x) + top * 0.5 - bottom * 0.5
        h = (top + bottom) * 0.5 * (0.45 + 0.55 * f)
        rings.append([Vector((x, AXIS_Y + p.x * w, zc + p.y * h)) for p in RECT])
    return k.smooth(k.loft(name, rings, mat), 50)


RECT = [Vector(mk.superellipse_point(2 * math.pi * j / 16, 3.2)) for j in range(16)]


# --- The parts ------------------------------------------------------------------------------------------------

def body(m):
    """The pod, the tail cone and the shaft: one round body along x, stations at the colours' borders."""
    xs = sorted(set([NOSE_TIP + 0.02, NOSE_TIP + 0.12, NOSE_TIP + 0.35, NOSE_TIP + 0.7, NOSE_TIP + 1.15] +
                    [x / 2 for x in range(-40, int(BODY_END * 2) + 1)] + [POD_END, CONE_END]))
    profile = [(x, BODY(x)) for x in xs if NOSE_TIP < x <= BODY_END]
    obj = lathe_x("body", profile, m["pod"], 40)
    for key in ("cone", "steel"):
        obj.data.materials.append(m[key])
    for poly in obj.data.polygons:
        x = poly.center.x
        poly.material_index = 0 if x < POD_END else 1 if x < CONE_END else 2
    k.smooth(obj, 50)
    # The collar, the groove in front of it and the flange at the shaft's end.
    x0, x1, r = COLLAR
    prof = [(x0 - 0.02, BODY(x0) - 0.2), (x0, r - 0.25), (x0 + 0.15, r), (x1 - 0.15, r), (x1, r - 0.25),
            (x1 + 0.02, BODY(x1) - 0.2)]
    k.smooth(lathe_x("collar", prof, m["collar"], 48), 50)
    g = GROOVE_X
    k.smooth(lathe_x("groove", [(g - 0.18, BODY(g) - 0.1), (g, BODY(g) + 0.06), (g + 0.18, BODY(g) - 0.1)], m["seam"], 48), 40)
    f0, f1, r = FLANGE
    prof = [(f0 - 0.02, 2.4), (f0, r - 0.3), (f0 + 0.2, r), (f1 - 0.2, r), (f1, r - 0.3), (f1 + 0.02, 2.4)]
    k.smooth(lathe_x("flange", prof, m["collar"], 40), 50)


def rods(m):
    """The grey rod on the pod's crest and the rail on the cone's with its window."""
    x0, x1, half, top = POD_ROD
    rod = rounded_bar("pod_rod", x0, x1, half, top, 0.6, m["steel"])
    mk.paint(rod, lambda c, n: m["steel_light"] if n.z > 0.55 and n.y > -0.2 else None)
    x0, x1, half, top = RAIL
    rail = rounded_bar("rail", x0, x1, half, top, 1.2, m["steel"], steps=30, ends=0.6)
    mk.paint(rail, lambda c, n: m["steel_light"] if n.z > 0.6 and n.y > 0.35 else None)
    # The window: a light blue frame raised on the rail, a dark slot inside it.
    w0, w1, hw, frame = WINDOW
    rail_top = lambda x: crest(x) + top  # noqa: E731
    outer = mk.rounded_rect_ring((0, 0), (w1 - w0) / 2, hw, 0.55, 0.0, 64)
    inner = mk.rounded_rect_ring((0, 0), (w1 - w0) / 2 - frame * 0.8, hw - frame, 0.3, 0.0, 64)
    cx = (w0 + w1) / 2
    verts, faces = [], []
    rings = [(outer, -0.25), (outer, 0.12), ([p * 0.985 for p in outer], 0.2), (inner, 0.2), (inner, 0.02), (inner, -0.25)]
    for pts, dz in rings:
        for p in pts:
            verts.append(Vector((cx + p.x, AXIS_Y + p.y, rail_top(cx + p.x) + dz)))
    n = len(outer)
    for r_ in range(len(rings) - 1):
        for j in range(n):
            a, b = r_ * n + j, r_ * n + (j + 1) % n
            faces.append((a, b, b + n, a + n))
    win = k.mesh_object("window", verts, faces, m["window"])
    k.recalc_normals(win)
    k.smooth(win, 50)
    # The slot: a dark floor inside the frame, strips across it following the rail's slope.
    hx, hy, rc = (w1 - w0) / 2 - frame * 0.8, hw - frame, 0.3
    verts, faces = [], []
    steps, across = 24, 4
    for i in range(steps + 1):
        u = -hx + 2 * hx * i / steps
        d = max(0.0, abs(u) - (hx - rc))
        half = max((hy - rc) + math.sqrt(max(rc * rc - d * d, 0.0)), 0.02)
        for j in range(across + 1):
            y = -half + 2 * half * j / across
            verts.append(Vector((cx + u, AXIS_Y + y, rail_top(cx + u) + 0.04)))
    for i in range(steps):
        for j in range(across):
            a = i * (across + 1) + j
            faces.append((a, a + across + 1, a + across + 2, a + 1))
    slot = k.mesh_object("slot", verts, faces, m["seam"])
    k.recalc_normals(slot)
    if slot.data.polygons[0].normal.z < 0:
        slot.data.flip_normals()
    k.smooth(slot, 80)


def tabs(m):
    """The blue lights on the cone's flanks: low lenses lying on its surface."""
    for side in (1, -1):
        for i, (x0, x1, y, half) in enumerate(TABS):
            yy = AXIS_Y + side * (y - AXIS_Y)
            cx = (x0 + x1) / 2
            rx = (x1 - x0) / 2
            # On the body's surface at that offset: its normal there.
            dy = yy - AXIS_Y
            r = BODY(cx)
            zs = crest(cx, dy)
            nrm = Vector((0.0, dy / (r * r), (zs - AXIS_Z) / (SQUASH * SQUASH * r * r))).normalized()
            lens = mk.ball("tab%d_%d" % (i, side), (0, 0, 0), (rx, half, 0.38), m["tab"], 16, 8)
            rot = Vector((0, 0, 1)).rotation_difference(nrm).to_matrix().to_4x4()
            lens.data.transform(Matrix.Translation((cx, yy, zs - 0.12)) @ rot)
            k.smooth(lens, 70)


def superellipse_reach(theta, radii, power):
    """How far from its centre a superellipse (half-widths radii) lies along the direction theta."""
    c, sn = abs(math.cos(theta)), abs(math.sin(theta))
    return 1.0 / max(((c / radii[0]) ** power + (sn / radii[1]) ** power) ** (1.0 / power), 1e-9)


def ring_solid(m, sections=96, profile=16):
    """The ring: a closed band round the opening, its section a rounded rectangle from the opening's edge to
    the outer edge (along rays from the centre), its inner upper edge catching the light."""
    cx, cy = RING_CENTRE
    z0, z1 = FRAME_Z
    zc, hz = (z0 + z1) / 2, (z1 - z0) / 2
    shape = [mk.superellipse_point(2 * math.pi * j / profile, RING_SECTION_POWER) for j in range(profile)]
    verts, faces, keys = [], [], []
    for i in range(sections):
        theta = 2 * math.pi * i / sections
        r_in = superellipse_reach(theta, RING_INNER, RING_POWER[1])
        r_out = superellipse_reach(theta, RING_OUTER, RING_POWER[0])
        mid, half = (r_in + r_out) / 2, (r_out - r_in) / 2
        u = Vector((math.cos(theta), math.sin(theta), 0.0))
        for su, sz in shape:
            p = Vector((cx, cy, zc)) + u * (mid + su * half) + Vector((0, 0, sz * hz))
            verts.append(p)
    for i in range(sections):
        for j in range(profile):
            a, b = i * profile + j, i * profile + (j + 1) % profile
            c, d = ((i + 1) % sections) * profile + (j + 1) % profile, ((i + 1) % sections) * profile + j
            faces.append((a, b, c, d))
            phi = math.degrees(2 * math.pi * (j + 0.5) / profile)
            keys.append("frame_light" if 95.0 < phi < 175.0 else "frame")
    obj = k.mesh_object("ring", verts, faces, m["frame"])
    obj.data.materials.append(m["frame_light"])
    for poly, key in zip(obj.data.polygons, keys):
        poly.material_index = 1 if key == "frame_light" else 0
    k.recalc_normals(obj)
    return k.smooth(obj, 60)


def frame(m):
    """The ring and its four arms (rounded plates sunk into it, the right ones with a blue panel set in a
    pocket), and the blue claws at the left arms' ends."""
    ring_solid(m)
    for mirror in (False, True):
        for points, key in ((ARM_LEFT, "l"), (ARM_RIGHT, "r")):
            arm = mk.prism("arm_" + key, plan(points, mirror), FRAME_Z[0] + 0.2, FRAME_Z[1] - 0.05, m["arm"])
            if key == "r":
                bed = mk.prism("bed", plan(PANEL, mirror), FRAME_Z[1] - 0.6, FRAME_Z[1] + 1, m["arm"])
                mk.boolean(arm, bed, "DIFFERENCE")
                mk.cleanup(arm)
            mk.bevel(arm, ARM_BEVEL, 3, 35.0)
            mk.shade(arm, 40.0)
        panel = mk.prism("panel", plan(PANEL, mirror), FRAME_Z[1] - 1.0, FRAME_Z[1] - 0.35, m["blue_light"])
        mk.bevel(panel, 0.3, 2, 35.0)
        mk.shade(panel, 40.0)
        claw = mk.prism("claw", plan(CLAW, mirror), AXIS_Z - 0.9, AXIS_Z + 0.9, m["blue"])
        mk.bevel(claw, 0.5, 3, 35.0)
        mk.shade(claw, 40.0)
        tip_x = px(22.6, 0)[0]
        mk.paint(claw, lambda c, n: m["blue_light"] if c.x < tip_x and n.z > 0.3 else None)


def block(m):
    """The blue block on the ring's right: a rounded box, a light band along its left side and a small light."""
    x0, x1, hy, hz = BLOCK
    rings = []
    count = 22
    for i in range(count + 1):
        t = i / count
        x = x0 + (x1 - x0) * t
        f = min(1.0, t / 0.08, (1 - t) / 0.22)
        f = math.sqrt(max(0.0, 1 - (1 - f) ** 2))
        ring = []
        for p in RECT:
            ring.append(Vector((x, AXIS_Y + p.x * hy * (0.55 + 0.45 * f), AXIS_Z + p.y * hz * (0.6 + 0.4 * f))))
        rings.append(ring)
    obj = k.loft("block", rings, m["blue"])
    k.smooth(obj, 50)
    band = (x0 + 1.3, x0 + 2.6)
    mk.paint(obj, lambda c, n: m["blue_light"] if band[0] < c.x < band[1] and n.z > 0.5 else None)
    bx, by = BLOCK_LIGHT
    mk.ball("block_light", (bx, by, AXIS_Z + hz - 0.05), (0.55, 0.55, 0.3), m["lamp"], 16, 8)


def sphere(m):
    centre, r = SPHERE
    ball = mk.ball("sphere", centre, (r, r, r * 0.95), m["sphere"], 40, 20)
    return ball


def materials():
    pal = k.level_palette()
    return {
        "pod": k.material("ringship_pod", palette=0x37, metallic=0.45, roughness=0.3),
        "cone": k.material("ringship_cone", palette=0x33, metallic=0.45, roughness=0.35),
        "steel": k.material("ringship_steel", palette=0x08, metallic=0.6, roughness=0.3),
        "steel_light": k.material("ringship_steel_light", palette=0x0b, metallic=0.6, roughness=0.25),
        "collar": k.material("ringship_collar", palette=0x0c, metallic=0.65, roughness=0.22),
        "seam": k.material("ringship_seam", palette=0x02, metallic=0.3, roughness=0.6),
        "window": k.material("ringship_window", palette=0x3c, metallic=0.2, roughness=0.15, emission=pal[0x3b],
                             emission_strength=0.8),
        "tab": k.material("ringship_tab", palette=0x38, metallic=0.3, roughness=0.15, emission=pal[0x37],
                          emission_strength=0.5),
        "frame": k.material("ringship_frame", palette=0x09, metallic=0.6, roughness=0.28),
        "arm": k.material("ringship_arm", palette=0x07, metallic=0.6, roughness=0.32),
        "frame_light": k.material("ringship_frame_light", palette=0x0b, metallic=0.6, roughness=0.25),
        "blue": k.material("ringship_blue", palette=0x38, metallic=0.45, roughness=0.28),
        "blue_light": k.material("ringship_blue_light", palette=0x3b, metallic=0.4, roughness=0.25),
        "lamp": k.material("ringship_lamp", palette=0x3e, metallic=0.1, roughness=0.2, emission=pal[0x3d],
                           emission_strength=1.2),
        "sphere": k.material("ringship_sphere", palette=0x37, metallic=0.3, roughness=0.12, emission=pal[0x36],
                             emission_strength=0.3),
    }


# --- Mirroring, checks, build -------------------------------------------------------------------------------------

def mirrored_copy(obj):
    """The object mirrored across x = 0, its faces turned to keep facing out and its corner normals mirrored."""
    mesh = obj.data
    normals = [Vector(c.vector) for c in mesh.corner_normals]
    verts = [(-v.co.x, v.co.y, v.co.z) for v in mesh.vertices]
    faces, loop_normals, mats = [], [], []
    for poly in mesh.polygons:
        loops = list(range(poly.loop_start, poly.loop_start + poly.loop_total))[::-1]
        faces.append([mesh.loops[li].vertex_index for li in loops])
        loop_normals += [(-normals[li].x, normals[li].y, normals[li].z) for li in loops]
        mats.append(poly.material_index)
    new = bpy.data.meshes.new(obj.name + "_m")
    new.from_pydata(verts, [], faces)
    for mat in mesh.materials:
        new.materials.append(mat)
    for poly, index in zip(new.polygons, mats):
        poly.material_index = index
        poly.use_smooth = True
    new.normals_split_custom_set(loop_normals)
    copy = bpy.data.objects.new(obj.name + "_m", new)
    bpy.context.scene.collection.objects.link(copy)
    return copy


def whole_mask(sheet, sprites):
    left, right = k.sprite_mask(sheet, sprites[0]), k.sprite_mask(sheet, sprites[1])
    return [a + b for a, b in zip(left, right)]


def build_whole():
    k.reset()
    m = materials()
    body(m)
    rods(m)
    tabs(m)
    frame(m)
    block(m)
    sphere(m)
    whole = mk.meshes()
    for obj in whole:
        mk.apply(obj)
    return whole, m


def build():
    options = k.args()
    outdir = mk.outdir(options)
    sheets = options.get("check")
    sheet = (os.path.join(sheets, "enemy_5.png") if os.path.isdir(sheets) else sheets) if sheets else None
    whole, m = build_whole()
    mirror = [mirrored_copy(o) for o in whole]
    for objects, pieces, label in ((whole, PIECES, "whole (5 39 | 41)"), (mirror, MIRRORED, "mirrored (5 43 | 45)")):
        for o in mirror if objects is whole else whole:
            o.hide_render = True
        for o in objects:
            o.hide_render = False
        low, high = mk.bounds(objects)
        print("== %s: %d triangles, %d objects, %d materials, x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f" % (
            label, mk.triangles(objects), len(objects), len(mk.materials_of(objects)), low.x, high.x, low.y, high.y,
            low.z, high.z))
        sprites = [p[1] for p in pieces]
        if sheet:
            mk.compare(label, mk.coverage(objects, 48, 28), whole_mask(sheet, sprites))
        if "preview" in options:
            mk.preview(options["preview"] + ("ringship_whole" if objects is whole else "ringship_whole_r"), objects,
                       size=(48, 28), scale=10, distance=1.6)
        for name, sprite, box in pieces:
            cut = [p for p in (mk.cut(src, box, m["seam"]) for src in objects) if p is not None]
            mk.transform(cut, Matrix.Translation((-(box[0] + box[1]) / 2, -(box[2] + box[3]) / 2, 0)))
            for o in objects:
                o.hide_render = True
            if sheet:
                mk.compare("%s (5 %d)" % (name, sprite), mk.coverage(cut, 24, 28), k.sprite_mask(sheet, sprite))
            bpy.context.view_layer.update()
            mk.report(name, cut, os.path.join(outdir, name + ".glb"))
            if "preview" in options:
                mk.preview(options["preview"] + name, cut)
            for o in cut:
                bpy.data.objects.remove(o)
            for o in objects:
                o.hide_render = False


if __name__ == "__main__":
    build()
