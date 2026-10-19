"""CORAL's brown seahorses in profile (sheet T sprites 203 and 241, 2x2: 24 x 27 pixels; enemy 1221 swims in from the
right facing left, 203, and enemy 1205 from the left facing right, 241; ground layer, about 65 of them; their
animations sway them, eight game frames each: 203 205 and 241 243), polished (2026-10-19; they replace wave3_v_sea.py's
seahorse(), a relief of the sprite's outline). models.cfg: model coral_seahorse_left / coral_seahorse_right /
coral_seahorse_left_205 / coral_seahorse_right_243; sprite t 203 coral_seahorse_left yaw=0, sprite t 241
coral_seahorse_right yaw=0, frame t 205 coral_seahorse_left_205, frame t 243 coral_seahorse_right_243.

T 241 is T 203 mirrored left for right, pixel for pixel, and T 243 is T 205 mirrored: the right-facing models are the
left-facing ones mirrored (x -> -x), not modelled again. No other enemy shows these four sprites.

As the sprites and their 4x upscales draw it (203): a glossy brown seahorse (ramp 1) lying in profile, its head at
the top facing left: a horse-like head (columns 5-16 of rows 0-8) with a long thin snout (row 5) ending in a small
flared mouth (column 1 of rows 3-7, light above, dark in its middle), a pale blue eye (columns 7-8 of rows 2-3), a
small knob of a crown on the back of its head (column 13 of rows 0-1, cut off by the cell's top edge), a curved gill
crease behind the eye (columns 12-13 of rows 1-7, dark) and behind it the pectoral fin, a frill of three pale blue
rays fanning back (columns 13-15 of rows 1-7); under the back of the head a short spine pointing down (columns 12-13
of rows 8-10). The ringed body arches down from the head (the neck at row 8, the belly bulging forward to columns 4-11
at rows 12-15), its rings drawn as lighter pixels every two rows along its middle, sweeps down to the right and runs
into the tail, which curls up into a spiral at the lower right (columns 16-23 of rows 16-26: along the bottom, up the
right side, over the top and in to its tip at column 18 of row 20). 205, the sway: the head two pixels back and one
down, the trunk a pixel down, the curl a pixel up (the tail tighter), the crown a pixel taller (no longer cut off).

Built as a creature lying on its side, its profile in the screen's plane and its midplane (the sagittal plane) at
height ZM, so the game's camera sees one flank: the body a tube lofted along a smooth path through the sprite's
middle from inside the head to the tail's tip, round in section (the flank deep as the sprite draws it, the
thickness towards the camera less), its bony rings (RING_PERIOD apart) swelling between pinched joints so that the
light picks them out; the head lofted along the snout's line, a bony brow over the eye, the snout a thin tube flaring
into the mouth, its dark opening facing forward; the eye a pale ball in a bony ring, the crown a stalk with three
points, the gill crease painted in, the fin a thin dark web fanning back over the flank with three pale pointed rays
standing off it, the spine a flattened tapering horn. The brown is painted in the sprite's shades by how far each
point faces the camera (the flank's middle lighter, its edges darker; the cheek lighter), cut into bands along smooth
contours (polish_orb_red.band_split); nothing is painted by direction, so the mirrored models are as right as the
mirrored sprites.

Frame 205's model is the same creature posed as 205 draws it (BODY's offsets, the head's HEAD_SHIFT, the crown's
CROWN_GROW); both frames span the same height, so the game, which centres them in height on their layer, keeps them
in place.

Origin at the sprite's centre (pixel 12, 14); +Y up the screen, +Z towards the camera.

Replaces wave3_v_sea.py's seahorse(): its SEAHORSE frame, seahorse() and the two v.model("coral_seahorse_left"/
"coral_seahorse_right", ...) registrations, the seahorse lines of its docstring; wave3_v_art.py's SEAHORSE,
SEAHORSE_FIN and SEAHORSE_R (nothing else reads them): remove them so that they don't overwrite these models.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each model's silhouette
against its sprite in enemy_T.png), --preview <prefix>, --only <name,...>.
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
from polish_orb_red import band_split  # noqa: E402
from polish_sphere_nozzle import smoothstep  # noqa: E402

ZM = 2.85            # the midplane's height
SEGMENTS = 14        # round the body and the head, TOP of them on the side the camera sees
TOP = 0.66

# The body's path (203; pixel coordinates, column and row of the cell, fractions between pixel centres): (column,
# row, 205's offset in columns and rows, the half-width across the path in the screen's plane, the outline included,
# the half-thickness towards the camera).
BODY = [
    (8.9, 6.6, 2.0, 1.0, 2.55, 1.84),      # inside the head's lower back
    (8.4, 8.0, 2.0, 1.0, 2.7, 1.89),       # the neck
    (7.7, 9.5, 1.6, 1.0, 2.9, 1.98),
    (7.3, 11.0, 1.0, 1.0, 3.45, 2.21),
    (7.45, 12.6, 0.4, 1.0, 3.9, 2.35),     # the belly
    (7.75, 14.1, 0.0, 1.0, 4.05, 2.39),
    (8.25, 15.4, 0.0, 1.0, 4.0, 2.39),
    (8.8, 16.7, 0.0, 1.0, 3.6, 2.25),
    (9.45, 18.0, 0.0, 1.0, 3.3, 2.12),
    (10.2, 19.3, 0.0, 1.0, 3.0, 1.93),
    (11.3, 20.5, 0.0, 1.0, 2.7, 1.75),
    (12.75, 21.6, 0.3, 0.9, 2.35, 1.56),
    (14.1, 22.6, 0.3, 0.4, 2.1, 1.38),
    (15.5, 23.35, 0.3, -0.1, 1.95, 1.27),  # the tail along the bottom
    (17.0, 24.25, 0.2, -0.7, 1.75, 1.15),
    (18.4, 24.9, 0.1, -0.9, 1.55, 1.09),
    (19.6, 24.85, 0.0, -1.0, 1.55, 1.06),
    (20.6, 24.2, 0.0, -1.0, 1.65, 1.03),   # up the curl's right side
    (21.3, 23.1, 0.0, -1.0, 1.7, 1.01),
    (21.75, 21.7, 0.0, -1.0, 1.7, 0.98),
    (21.6, 20.2, 0.0, -1.0, 1.65, 0.94),
    (21.0, 18.9, 0.0, -1.0, 1.6, 0.9),
    (20.15, 17.85, 0.0, -1.0, 1.55, 0.86),  # over its top
    (19.15, 17.3, 0.0, -1.0, 1.48, 0.83),
    (18.15, 17.55, 0.0, -1.0, 1.4, 0.78),
    (17.45, 18.35, -0.1, -1.0, 1.3, 0.72),  # down its left side and in to the tip
    (17.35, 19.35, -0.3, -1.0, 1.1, 0.63),
    (17.95, 20.15, -0.6, -1.1, 0.85, 0.52),
    (18.95, 20.45, -0.8, -1.2, 0.6, 0.41),
]
RING_PERIOD, RING_RISE = 1.9, 0.09   # the body's bony rings: how far apart along the path, how much they swell it
RINGS_PER = 4                        # the body's sections per ring
RING_FROM = 1.6                      # the first ring's distance along the path (from the head)

# The head along the snout's line, from its blunt face (x -7.2) to the back of the skull (x 5.05): (x, the middle's y,
# the half-height in the screen's plane, the half-thickness towards the camera). Model coordinates of 203.
HEAD = [(-7.2, 8.9, 1.0, 0.9), (-6.6, 9.0, 2.35, 1.55), (-5.6, 9.25, 3.4, 2.1), (-4.5, 9.45, 4.05, 2.4),
        (-3.0, 9.55, 4.28, 2.5), (-1.5, 9.5, 4.25, 2.45), (-0.5, 9.3, 4.0, 2.38), (0.5, 9.2, 3.9, 2.3),
        (1.5, 9.25, 3.85, 2.2), (2.5, 9.35, 3.8, 2.0), (3.5, 9.5, 3.45, 1.7), (4.3, 9.5, 2.35, 1.25),
        (4.8, 9.5, 1.3, 0.75), (5.1, 9.5, 0.2, 0.15)]
HEAD_POWER = 2.25
# The snout from inside the face to the mouth: (x, y, half-height, half-thickness).
SNOUT = [(-5.3, 8.8, 2.3, 1.75), (-6.3, 8.62, 1.62, 1.33), (-7.3, 8.53, 1.32, 1.1), (-8.5, 8.5, 1.22, 1.03),
         (-9.6, 8.5, 1.25, 1.05), (-10.3, 8.5, 1.6, 1.18), (-10.75, 8.5, 2.15, 1.34), (-11.2, 8.5, 2.35, 1.4),
         (-11.55, 8.5, 2.1, 1.22), (-11.8, 8.5, 1.4, 0.8)]
MOUTH_X = -11.4       # the mouth's dark opening: the snout's end beyond this, facing forward
EYE = (Vector((-3.85, 10.85)), 0.98, 0.42)  # its middle, radius, how far it bulges from the head
GILL = [(0.5, 12.6), (1.45, 10.2), (1.05, 8.1), (0.1, 6.2)]  # the gill crease, from the top down
GILL_WIDTH = 0.32
CHEEK = (-2.0, 8.6, 2.4, 1.6)   # the lit cheek under and behind the eye: its middle and half-sizes
BROW = [(-6.3, 9.9), (-5.2, 11.6), (-3.9, 12.15), (-2.6, 11.7), (-2.0, 10.9)]  # the ridge over the eye
CROWN = [(1.1, 11.7), (1.25, 12.9), (1.35, 13.65)]           # the crown's stalk, from the head up to its tip
CROWN_GROW = 0.9      # 205's crown: this much taller
# The fin: its root along the gill crease's back, from the top down; its three rays' tips (the top one up past
# the head's back, the middle one back, the bottom one down); how far the web between them dips in; how high its
# edge stands off the flank.
FIN_ROOT = [(1.85, 11.95), (2.25, 9.7), (1.8, 7.3)]
FIN_TIPS = [(3.35, 13.45), (4.95, 9.75), (3.45, 5.85)]
FIN_DIP, FIN_LIFT = 0.3, 0.75
SPINE = ((1.15, 6.4), (1.6, 3.0), 1.2)   # the spine under the back of the head: root, tip, root's radius
HEAD_SHIFT = (2.0, -1.0)  # 205: the head and all on it, in pixels (x, y)

SHADES = range(3, 12)     # the brown's shades (ramp 1), dark to light


def P(c, r):
    """A pixel's centre (column c, row r of the 24 x 28 cell)."""
    return c + 0.5 - 12.0, 13.5 - r


def spline(points, step):
    """A Catmull-Rom curve through points (tuples of equal length; their first two values x, y), about `step` apart
    in x, y; the other values are carried along."""
    pts = [tuple(p) for p in points]
    out = []
    n = len(pts)
    for s in range(n - 1):
        p0, p1, p2, p3 = pts[max(s - 1, 0)], pts[s], pts[s + 1], pts[min(s + 2, n - 1)]
        count = max(1, int(round(math.hypot(p2[0] - p1[0], p2[1] - p1[1]) / step)))
        for j in range(count):
            t = j / count
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * (2 * b + (-a + c) * t + (2 * a - 5 * b + 4 * c - d) * t2 +
                                    (-a + 3 * b - 3 * c + d) * t3) for a, b, c, d in zip(p0, p1, p2, p3)))
    out.append(pts[-1])
    return out


def ring_angles(count=SEGMENTS):
    """Angles round a section, TOP of them on its upper half (the side the camera sees)."""
    top = int(round(count * TOP))
    return [math.pi * j / top for j in range(top)] + [math.pi + math.pi * j / (count - top) for j in range(count - top)]


def materials():
    m = {}
    for s in SHADES:
        m[s] = k.material(f"seahorse_{s:x}", palette=0x10 + s, metallic=0.15,
                          roughness=0.45 if s < 5 else 0.3 if s < 8 else 0.22)
    m["mouth"] = k.material("seahorse_mouth", palette=0x11, metallic=0.1, roughness=0.6)
    m["eye"] = k.material("seahorse_eye", palette=0x3d, metallic=0.0, roughness=0.1)
    m["pupil"] = k.material("seahorse_pupil", palette=0x33, metallic=0.0, roughness=0.06)
    m["web"] = k.material("seahorse_fin_web", palette=0x39, metallic=0.0, roughness=0.3)
    m["fin"] = k.material("seahorse_fin", palette=0x3c, metallic=0.0, roughness=0.25)
    m["ray"] = k.material("seahorse_fin_ray", palette=0x3e, metallic=0.0, roughness=0.2)
    return m


def shade_bands(m):
    return [(-99.0 if i == 0 else s - 0.5, m[s]) for i, s in enumerate(SHADES)]


def flank(n):
    """The brown's shade by how far a point faces the camera (n: its normal): the flank's middle lighter."""
    if n.z < -0.15:
        return 3.0  # underneath, which the camera never sees: one shade
    return 4.9 + 2.6 * max(0.0, n.z) ** 0.8


def paint(obj, value, m):
    """Bands of the brown by value(index, co, normal) per vertex, smooth along their borders."""
    mesh = obj.data
    mesh.update()
    values = [value(v.index, v.co, v.normal) for v in mesh.vertices]
    band_split(obj, values, shade_bands(m))
    return k.smooth(obj, 50)


# --- The body ---------------------------------------------------------------------------------------------------------

def resample(path, positions):
    """Points of a polyline of tuples at the given distances along it (its first two values x, y), interpolated."""
    s = [0.0]
    for a, b in zip(path, path[1:]):
        s.append(s[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    out, j = [], 0
    for target in positions:
        while j < len(s) - 2 and s[j + 1] < target:
            j += 1
        t = min(1.0, max(0.0, (target - s[j]) / max(s[j + 1] - s[j], 1e-9)))
        out.append(tuple(a + (b - a) * t for a, b in zip(path[j], path[j + 1])))
    return out


def body(m, pose):
    """The body along its path, its sections RING_PERIOD / RINGS_PER apart so that one falls on every joint between
    the bony rings: pinched there, swelling between."""
    rows = []
    for c, r, dc, dr, hw, ht in BODY:
        x, y = P(c + dc * pose, r + dr * pose)
        rows.append((x, y, hw, ht))
    fine = spline(rows, 0.08)
    total = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(fine, fine[1:]))
    spacing = RING_PERIOD / RINGS_PER
    first = RING_FROM % spacing
    positions = [0.0] + [first + j * spacing for j in range(int((total - first) / spacing) + 1)
                         if 0.1 < first + j * spacing < total - 0.2] + [total]
    path = resample(fine, positions)
    rings = []
    for i, ((x, y, hw, ht), s) in enumerate(zip(path, positions)):
        a, b = path[max(i - 1, 0)], path[min(i + 1, len(path) - 1)]
        tx, ty = b[0] - a[0], b[1] - a[1]
        length = math.hypot(tx, ty)
        nx, ny = -ty / length, tx / length
        fade = smoothstep(RING_FROM - 0.6, RING_FROM + 0.6, s) * (1 - smoothstep(total - 3.0, total - 0.8, s))
        phase = ((s - RING_FROM) / RING_PERIOD) % 1.0
        plate = math.sin(math.pi * phase) ** 0.6           # 0 at the joints between the rings, 1 midway
        swell = 1.0 + RING_RISE * fade * (plate - 0.6)
        rings.append([Vector((x + nx * hw * swell * math.cos(f), y + ny * hw * swell * math.cos(f),
                              ZM + ht * swell * math.sin(f))) for f in ring_angles()])
    x1, y1, hw1, ht1 = path[-1]
    x0, y0 = path[-2][:2]
    d = Vector((x1 - x0, y1 - y0, 0.0)).normalized()
    tip = Vector((x1, y1, ZM)) + d * hw1 * 0.9
    obj = k.loft("body", rings, m[6], start_point=(path[0][0], path[0][1], ZM), end_point=tuple(tip))
    return paint(obj, lambda i, co, n: flank(n), m)


# --- The head ---------------------------------------------------------------------------------------------------------

def x_loft(name, table, mat, power=2.0, step=0.42, segments=SEGMENTS):
    """A loft along x through table rows (x, the middle's y, half-height, half-thickness), from its first row to
    its last, closed at both ends."""
    path = spline(table, step)
    rings = []
    for x, yc, hy, hz in path[1:-1]:
        ring = []
        for a in ring_angles(segments):
            u, v = mk.superellipse_point(a, power)
            ring.append(Vector((x, yc + max(hy, 0.03) * u, ZM + max(hz, 0.03) * v)))
        rings.append(ring)
    first, last = path[0], path[-1]
    if first[0] > last[0]:
        rings.reverse()
        first, last = last, first
    return k.loft(name, rings, mat, start_point=(first[0], first[1], ZM), end_point=(last[0], last[1], ZM))


def gill_distance(x, y):
    path = mk.chaikin(GILL, 2, closed=False)
    best = 9.0
    for (ax, ay), (bx, by) in zip(path, path[1:]):
        ex, ey = bx - ax, by - ay
        t = max(0.0, min(1.0, ((x - ax) * ex + (y - ay) * ey) / (ex * ex + ey * ey)))
        best = min(best, math.hypot(x - ax - t * ex, y - ay - t * ey))
    return best


def head_surface(x, y):
    """The head's height above its midplane at (x, y) (0 outside)."""
    table = sorted(HEAD)
    if x <= table[0][0] or x >= table[-1][0]:
        return 0.0
    for (x0, y0, hy0, hz0), (x1, y1, hy1, hz1) in zip(table, table[1:]):
        if x0 <= x <= x1:
            t = (x - x0) / (x1 - x0)
            yc, hy, hz = y0 + (y1 - y0) * t, hy0 + (hy1 - hy0) * t, hz0 + (hz1 - hz0) * t
            q = abs(y - yc) / hy
            return hz * max(0.0, 1 - q ** HEAD_POWER) ** (1 / HEAD_POWER) if q < 1 else 0.0
    return 0.0


def head(m):
    skull = x_loft("head", HEAD, m[6], power=HEAD_POWER)

    def value(i, co, n):
        v = flank(n)
        if n.z > 0.15:
            top = smoothstep(0.15, 0.5, n.z)
            v += 1.1 * math.exp(-((co.x - CHEEK[0]) / CHEEK[2]) ** 2 - ((co.y - CHEEK[1]) / CHEEK[3]) ** 2) * top
            v -= 3.6 * math.exp(-(gill_distance(co.x, co.y) / GILL_WIDTH) ** 2) * top
        return v
    paint(skull, value, m)
    # The brow: a bony ridge arching over the eye from the snout's root.
    pts = []
    for x, y in mk.chaikin(BROW, 2, closed=False):
        pts.append((x, y, ZM + head_surface(x, y) - 0.12))
    count = len(pts)
    mk.tube("brow", pts, 0.3, m[8], 6, radii=[0.12 + 0.24 * math.sin(math.pi * j / (count - 1)) for j in range(count)])
    k.smooth(bpy.data.objects["brow"], 60)
    snout = x_loft("snout", SNOUT, m[6], step=0.34, segments=12)
    # The snout lit along its top, its mouth's upper lip lightest (the sprite's 1b).
    paint(snout, lambda i, co, n: flank(n) + 0.8 * smoothstep(0.2, 0.7, n.y) + (1.0 if co.x < -10.2 and n.y > 0.3
                                                                                 else 0.0), m)
    mk.paint(snout, lambda c, n: m["mouth"] if c.x < MOUTH_X and n.x < -0.55 else None)
    # The eye: a pale ball bulging from the flank in a bony ring, its pupil looking forward and up.
    centre, radius, bulge = EYE
    z = ZM + head_surface(centre.x, centre.y) + bulge - radius * 0.75
    mk.ball("eye", (centre.x, centre.y, z), (radius, radius, radius * 0.75), m["eye"], 18, 9)
    mk.ball("pupil", (centre.x - 0.25, centre.y - 0.1, z + radius * 0.66), (0.36, 0.42, 0.14), m["pupil"], 12, 6)
    ring = []
    for j in range(21):
        a = 2 * math.pi * j / 20
        x, y = centre.x + 1.18 * radius * math.cos(a), centre.y + 1.18 * radius * math.sin(a)
        ring.append((x, y, ZM + head_surface(x, y) - 0.08))
    mk.tube("eye_ring", ring, 0.26, m[7], 6)
    k.smooth(bpy.data.objects["eye_ring"], 60)
    # The crown: a stalk up from the back of the head, three points at its top.
    stalk = [Vector((x, y, ZM + 0.25 * head_surface(x, y))) for x, y in CROWN]
    stalk[0].z = ZM + head_surface(*CROWN[0]) * 0.6
    pts = mk.chaikin([tuple(p) for p in stalk], 2, closed=False)
    n = len(pts)
    mk.tube("crown", pts, 0.8, m[8], 10, radii=[0.86 - 0.22 * j / (n - 1) for j in range(n)])
    k.smooth(bpy.data.objects["crown"], 60)
    top = Vector(pts[-1])
    for i, (dx, dy, dz) in enumerate(((-0.5, 0.42, 0.25), (0.5, 0.42, 0.25), (0.0, 0.5, 0.6))):
        tip = top + Vector((dx, dy, dz))
        mk.tube(f"crown_point{i}", [tuple(top - Vector((dx, dy, dz)) * 0.4), tuple(tip)], 0.3, m[9], 8,
                radii=[0.4, 0.07])
        k.smooth(bpy.data.objects[f"crown_point{i}"], 60)
    # The spine under the back of the head: a flattened horn pointing down.
    (rx, ry), (tx, ty), r0 = SPINE
    pts = [(rx + (tx - rx) * t, ry + (ty - ry) * t - 0.25 * math.sin(math.pi * t), ZM) for t in
           (i / 8 for i in range(9))]
    radii = [r0 * (1 - 0.92 * (i / 8) ** 1.1) for i in range(9)]
    horn = mk.tube("spine", pts, r0, m[6], 8, radii=radii)
    for v in horn.data.vertices:
        v.co.z = ZM + (v.co.z - ZM) * 0.7
    paint(horn, lambda i, co, n: flank(n), m)


def fin(m):
    """The pectoral fin: a thin dark web fanning back over the flank from behind the gill crease, its edge scalloped
    between three pale pointed rays that stand off the flank."""
    root_path = mk.chaikin(FIN_ROOT, 3, closed=False)
    edge_path = spline(FIN_TIPS, 0.1)
    nv, nu = 25, 6

    def along(path, v):
        f = v * (len(path) - 1)
        i = min(int(f), len(path) - 2)
        return Vector(path[i]).lerp(Vector(path[i + 1]), f - i)

    def mid(u, v, dip=FIN_DIP):
        """The fin's middle surface at u (0 the root, 1 the edge) and v (0 the top ray, 1 the bottom one)."""
        root = along(root_path, v)
        edge = along(edge_path, v)
        edge = root + (edge - root) * (1 - dip * math.sin(2 * math.pi * v) ** 2)
        p = root.lerp(edge, u)
        z = ZM + head_surface(root.x, root.y) * (1 - 0.45 * u) + 0.1 + FIN_LIFT * u ** 1.4
        return Vector((p.x, p.y, z))

    rings = []
    for j in range(nv + 1):
        v = j / nv
        top = [mid(0.82 * i / nu, v) + Vector((0, 0, 0.1)) for i in range(nu + 1)]
        bottom = [mid(0.82 * i / nu, v) - Vector((0, 0, 0.1)) for i in range(nu + 1)]
        rings.append(top + bottom[::-1])
    web = k.loft("fin_web", rings, m["web"])
    k.smooth(web, 70)
    # The rays: pale pointed blades on the web, from its root out past its edge.
    for i, v in enumerate((0.03, 0.5, 0.97)):
        root, tip = mid(0.0, v), mid(1.0, v, 0.0)
        axis = tip - root
        side = Vector((-axis.y, axis.x, 0.0)).normalized()
        rings = []
        for q in range(1, 12):
            t = q / 12
            w = 0.62 * math.sin(math.pi * t ** 0.55) ** 0.8 * (1 - t) ** 0.25
            c = mid(t, v, 0.0) + Vector((0, 0, 0.16))
            rings.append([c + side * (w * math.cos(2 * math.pi * a / 10)) +
                          Vector((0, 0, 0.11 * math.sin(2 * math.pi * a / 10))) for a in range(10)])
        blade = k.loft(f"fin_ray{i}", rings, m["fin"], start_point=tuple(root + Vector((0, 0, 0.16))),
                       end_point=tuple(tip + axis.normalized() * 0.25 + Vector((0, 0, 0.16))))
        k.smooth(blade, 70)
        mk.paint(blade, lambda c, n, root=root, axis=axis, side=side:
                 m["ray"] if abs((c - root).dot(side)) < 0.2 or (c - root).dot(axis) > 0.72 * axis.length_squared
                 else None)


def build_model(pose, mirror):
    k.reset()
    m = materials()
    body(m, pose)
    before = set(bpy.context.scene.objects)
    head(m)
    fin(m)
    shift = Matrix.Translation((HEAD_SHIFT[0] * pose, HEAD_SHIFT[1] * pose, 0.0))
    for obj in set(bpy.context.scene.objects) - before:
        if obj.type != "MESH":
            continue
        if obj.name.startswith("crown") and pose:  # 205's crown, no longer cut off: taller
            for v in obj.data.vertices:
                v.co.y += CROWN_GROW * smoothstep(CROWN[0][1], CROWN[-1][1], v.co.y)
        obj.data.transform(shift)
    if mirror:
        for obj in mk.meshes():
            obj.data.transform(Matrix.Scale(-1, 4, (1, 0, 0)))
            obj.data.flip_normals()
    return mk.meshes()


# The models: (name, sprite, the pose (0: 203, 1: 205), mirrored).
MODELS = [("coral_seahorse_left", 203, 0, False), ("coral_seahorse_left_205", 205, 1, False),
          ("coral_seahorse_right", 241, 0, True), ("coral_seahorse_right_243", 243, 1, True)]


def build():
    options = k.args()
    out = mk.outdir(options)
    only = set(options["only"].split(",")) if "only" in options else None
    for name, sprite, pose, mirror in MODELS:
        if only is not None and name not in only:
            continue
        parts = build_model(pose, mirror)
        if "check" in options:
            mk.compare("%s (T %d)" % (name, sprite), mk.coverage(parts, 24, 28),
                       k.sprite_mask(os.path.join(options["check"], "enemy_T.png"), sprite))
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        bpy.context.view_layer.update()
        mk.report(name, parts, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, parts)


if __name__ == "__main__":
    build()
