"""IXMUCANE's grey dome on two claws (sheet 8 sprite 115, 2x2: a 23 x 28 creature in the 24 x 28 cell; enemy 108 of
episode 3, IXMUCANE, in the sky: its animation 115 117 119 117, a frame a tick), polished (2026-10-22; it replaces
wave3_y.py's claw_dome(): a heightfield dome painted in bands, a tan plate for a jaw, two lofted claws).

The level brings ten of them up from below the screen (events 2030-2140, type 18: made at the bottom, ey 190, moving
up 6-7 pixels a tick, slowing, swaying sideways). No other enemy shows 115, 117 or 119 (catalog.json); none of them is
another sprite's pixels mirrored, turned or in other ramps. 117 and 119 are 115 with the claws' hooks drawn one and
three pixels further in and the light moved from the lamp on top to the eye: the lamp dims (its middle 7d 7f 7f, then
79 7b 7f, then 78 7e 7c), the eye brightens two shades a frame (its middle 7d, 7f, 7f; its rings 7a 77 74, 7c 79 76,
7e 7b 78): frame models claw_dome_117 and claw_dome_119, the claws closing and the light passing from the lamp to the
eye and back as the animation runs.

As the sprite and its 4x upscales draw it (columns and rows of the cell; symmetric about column 12, x 0.5): a grey
metal dome (rows 3-14, columns 2-22: round at the back, its sides straight) in three plates: a lit middle one (columns
10-14) from the lamp to the brow, seams either side of it (columns 9 and 15), the flanks coming down beside the eye to
row 13; the brow a dark band across its front (row 11); on its back a red lamp, glowing (rows 0-3, columns 8-16,
brightest along its front); under the brow the big red eye (columns 10-14 of rows 12-16, its middle hottest) in a dark
socket; and two tan claws (ramp 1) from under the dome's front corners, each like a 5 (the right one the left one
mirrored): a bar out to the side (rows 15-17, columns 3-9), a stem down from its inner end (columns 8-9 of rows 18-20)
and a broad hooked blade at its foot (rows 21-26, columns 2-10) curling out and up the screen into a hook (columns 1-2
of rows 20-22).

Built as a flying creature for the game's camera. The dome a solid (a signed distance on a grid STEP apart: its plan
the sprite's outline, notched round the eye, its top an ellipsoid crowned towards the back, the edges rounded, the
seams grooved along it, wider apart by the lamp; its surface by surface nets, reduced, shaded with the dense surface's
normals), painted by its plates as the sprite draws them (GREYS: the middle plate between the seams lit, a shade
darker where it slopes down to the brow, the flanks darker, their skirts darker still, the brow's front darker again;
every face turned down, and the walls of the socket, dark; metallic as the family's greys, polish_ixm_pod's head); the
lamp a squat dome of glass on the back in a grey ring, glowing hottest along its front (the side the camera sees: the
dome's back slope puts it a row or two lower than the sprite seen from straight above, where the tilted camera sees it
where the sprite draws it); the eye a ball in a dark socket under the brow, its hot middle on the side the camera sees
(VIEW_TILT); each claw a tan tube of oval section, broad across, along the 5 (the bar, the stem, the blade broadening
and tapering into the hook), painted in bands of the light its faces get (polish_tan_crab's way), the blade hinged at
the stem's foot. In each
frame the blades turn up and in about the hinge (HINGE: an axis along the stem's foot; 0, 30 and 52 degrees: their
hooks one and three pixels further in, seen from above, as the sprites draw them) and the lamp's and the eye's
materials change (emission 0.12-0.62, well under 1: the cfg's glow halo and the bloom add). All frames span the same
bounds (the game centres a sky enemy's model in height).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up; the creature is built about u = 0
(the sprite's column 12) and moved to x 0.5 (AXIS_X); column c is x = c + 0.5 - 12, row r is y = 13.5 - r.

models.cfg: the model line stays (model claw_dome enemies/claw_dome.glb), add model claw_dome_117
enemies/claw_dome_117.glb, model claw_dome_119 enemies/claw_dome_119.glb, frame 8 117 claw_dome_117, frame 8 119
claw_dome_119; sprite 8 115 claw_dome yaw=0 glow=12:0.3:119:0.5:1 (the halo on the eye, 1 down the screen from the
sprite's centre; it was at the centre).

Replaces wave3_y.py's claw_dome() (its section "# --- 8 115: the dome on two claws": DOME and the
@y.model("claw_dome", ...) function, and the claw_dome paragraph of its docstring) and wave3_y_art.py's DOME (nothing
else reads it).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each frame's silhouette
against its sprite, also leaving the sprite's black outline ring out), --preview <prefix>, --only <name,...>.
"""
import math
import os
import sys

import bpy
import numpy as np
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
import polish_ixm_wall_rock as rw  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_rock_arch import (face_data, finish_whole, mesh_object, polygon_sdf, smax, smoothstep,  # noqa: E402
                              surface_nets)
from polish_tan_crab import band, chaikin_open, light, paint_bands, resample  # noqa: E402

AXIS_X = 0.5
VIEW_TILT = 20.0

# The dome: its plan (u, y; the left half from the back round to the front middle, mirrored), its top (an ellipsoid
# crowned at CROWN: its middle, its base's height, its height over the base, radii across and towards the front and
# the back, the superellipse powers across and along), the rounding of its edges, its underside's height, the seams
# (the right one's line (u, y) from the back, wider apart by the lamp, to the brow; their grooves' depth and
# half-width).
PLAN = [(0.0, 11.1), (-2.8, 11.0), (-4.6, 10.6), (-6.0, 9.7), (-7.2, 8.6), (-8.3, 7.5), (-9.2, 6.3), (-9.9, 5.0),
        (-10.3, 3.6), (-10.4, 2.0), (-10.2, 0.6), (-9.4, -0.2), (-7.0, -0.35), (-4.7, -0.25), (-3.7, 0.5),
        (-3.1, 1.4), (-1.8, 1.85), (0.0, 1.95)]
CROWN = (6.2, 2.7, 6.8, 11.0, 6.8, 5.4, 2.6, 2.0)   # y, base z, height, radius across, front, back, powers
EDGE_ROUND, BOTTOM_ROUND = 0.9, 0.5
UNDER = 1.6
SEAM_LINE = [(5.1, 9.7), (4.4, 7.7), (3.35, 6.3), (3.05, 2.6)]
SEAM_GROOVE = (0.3, 0.3)
# The lamp on the back: its middle (y, how far it stands out of the dome), radii (across, along, up), its ring.
LAMP = (10.1, 0.15, (3.3, 1.75, 1.45), 0.42)
# The eye: its middle and radius; where its middle and its ring end (how far the faces turn from the camera); the
# dark socket round it (a squat ellipsoid in the dome's notch).
EYE = (Vector((0.0, -1.25, 3.7)), 2.55)
EYE_RINGS = (0.1, 0.32)
SOCKET = (Vector((0.0, -0.7, 2.85)), Vector((3.7, 2.4, 1.45)))
# The claws (the left one; the right one mirrored): the path (u, y, z) along the 5 from the bar's outer end to the
# hook's tip, its sections' half-widths (across, up) at each key point, and the hinge (the key point at the stem's foot,
# the u and z of the axis along y about which the blade turns up and in).
CLAW = [((-9.35, -1.95, 2.3), (1.35, 0.95)), ((-7.4, -2.0, 2.55), (1.65, 1.05)), ((-5.2, -2.1, 2.75), (1.65, 1.1)),
        ((-3.55, -2.7, 2.8), (1.45, 1.05)), ((-3.2, -4.3, 2.6), (1.2, 0.9)), ((-3.35, -6.0, 2.3), (1.2, 0.88)),
        ((-3.6, -7.6, 2.0), (1.6, 0.9)), ((-4.7, -9.7, 1.75), (2.75, 0.95)), ((-6.7, -10.7, 1.65), (2.75, 0.92)),
        ((-8.6, -10.2, 1.75), (2.2, 0.86)), ((-9.75, -8.8, 2.05), (1.35, 0.72)), ((-10.1, -7.3, 2.4), (0.72, 0.52))]
HINGE = (6, -3.6, 1.95)
CLAW_FLOOR = 1.05
# The frames: (model, sprite, the blades' turn (degrees), the lamp's (palette index, emission) for its hot front and
# its rest, the eye's for its middle, its ring and its rim).
FRAMES = [("claw_dome", 115, 0.0, ((0x7c, 0.5), (0x78, 0.3)), ((0x7b, 0.42), (0x78, 0.3), (0x75, 0.18))),
          ("claw_dome_117", 117, 30.0, ((0x79, 0.36), (0x76, 0.22)), ((0x7d, 0.52), (0x7a, 0.38), (0x77, 0.24))),
          ("claw_dome_119", 119, 52.0, ((0x77, 0.26), (0x74, 0.14)), ((0x7e, 0.6), (0x7c, 0.46), (0x79, 0.3)))]

# The grid the dome's solid is sampled on.
STEP = 0.15
X0, NX = -11.4, 153
Y0, NY = -0.9, 87
Z0, NZ = 1.1, 64
DOME_TARGET = 2300
GREYS = (0x05, 0x08, 0x0a, 0x0c)    # the brow's front, the skirts, the flanks, the middle plate
BROW_Y, SKIRT_Z = 3.3, 3.9   # where the middle plate slopes down to the brow, below what the flanks are skirts
METAL = (0.45, 0.28)          # the greys' metallic and roughness (polish_ixm_pod's head: 0.55, 0.25-0.3)
DARK = 0x02
TAN = ((0.3, 0.5, 0.74), (0x15, 0x17, 0x1a, 0x1c))


def materials():
    pal = k.level_palette()
    m = {g: k.material(f"cdome_grey_{g:x}", palette=g, metallic=METAL[0], roughness=METAL[1]) for g in GREYS}
    m["dark"] = k.material("cdome_dark", palette=DARK, metallic=0.3, roughness=0.5)
    for index in TAN[1]:
        m[index] = k.material(f"cdome_tan_{index:x}", palette=index, metallic=0.15, roughness=0.45)
    for _, _, _, lamp, eye in FRAMES:
        for kind, levels in (("lamp", lamp), ("eye", eye)):
            for index, strength in levels:
                key = (kind, index, strength)
                if key not in m:
                    m[key] = k.material(f"cdome_{kind}_{index:x}_{int(strength * 100)}", palette=index, metallic=0.0,
                                        roughness=0.22, emission=pal[index], emission_strength=strength)
    return m


# --- The dome -------------------------------------------------------------------------------------------------------

def plan():
    left = PLAN
    right = [(-u, y) for u, y in reversed(PLAN[1:-1])]
    loop = left + right
    pts = [Vector((u, y, 0.0)) for u, y in loop]
    for _ in range(2):   # (Chaikin, closed)
        out = []
        for a, b in zip(pts, pts[1:] + pts[:1]):
            out += [a.lerp(b, 0.25), a.lerp(b, 0.75)]
        pts = out
    return [(p.x, p.y) for p in pts]


def crown_height(u, y):
    cy, base, height, ru, rf, rb, pu, py = CROWN
    ry = np.where(y < cy, rf, rb)
    q = 1.0 - np.abs(u / ru) ** pu - np.abs((y - cy) / ry) ** py
    return base + height * np.clip(q, 0.0, 1.0) ** (1.0 / py)


def seam_u(y):
    """The seams' |u| at y (between their ends)."""
    line = SEAM_LINE[::-1]
    return np.interp(y, [p[1] for p in line], [p[0] for p in line])


def seam_distance(u, y):
    """How far (u, y) lies from the nearer seam (in the plan)."""
    p = np.stack([np.abs(u), y], -1)
    d = np.full(np.shape(u), 9.0)
    for (u0, y0), (u1, y1) in zip(SEAM_LINE, SEAM_LINE[1:]):
        a, b = np.array([u0, y0]), np.array([u1, y1])
        t = np.clip(((p - a) @ (b - a)) / ((b - a) @ (b - a)), 0.0, 1.0)
        d = np.minimum(d, np.linalg.norm(p - (a + t[..., None] * (b - a)), axis=-1))
    return d


def dome_solid():
    xs = X0 + STEP * np.arange(NX)
    ys = Y0 + STEP * np.arange(NY)
    zs = Z0 + STEP * np.arange(NZ)
    gu, gy = np.meshgrid(xs, ys, indexing="ij")
    d_plan = polygon_sdf(gu, gy, plan()).astype(np.float32)
    top = crown_height(gu, gy) - SEAM_GROOVE[0] * np.exp(-(seam_distance(gu, gy) / SEAM_GROOVE[1]) ** 2)
    z = zs[None, None, :].astype(np.float32)
    d = smax(d_plan[:, :, None], (z - top[:, :, None]).astype(np.float32), EDGE_ROUND)
    d = smax(d, UNDER - z, BOTTOM_ROUND)
    verts, quads = surface_nets(d.astype(np.float32), (X0, Y0, Z0), STEP)
    whole = finish_whole(mesh_object("dome_dense", verts, quads), smooth=2)
    return whole


def dome_greys(centres, normals):
    """Each face's palette index, by the plates the sprite draws: the middle plate between the seams lit (its front,
    where it slopes down to the brow, a shade darker), the flanks a shade darker, their skirts darker still, the brow's
    front darker again; every face turned down, and the walls of the socket round the eye, dark."""
    u, y, z = centres[:, 0], centres[:, 1], centres[:, 2]
    middle = (np.abs(u) < seam_u(y)) & (y > SEAM_LINE[-1][1] - 0.4) & (y < SEAM_LINE[0][1] + 1.6)
    brow, skirt, flank, plate = GREYS
    idx = np.where(middle, np.where(y < BROW_Y, flank, plate), np.where(z < SKIRT_Z, skirt, flank))
    idx = np.where(middle & (normals[:, 1] < -0.55), brow, idx)
    socket = (np.abs(u) < 3.7) & (y < 2.3) & (normals[:, 2] < 0.25)
    dark = (normals[:, 2] < -0.35) | socket
    return np.where(dark, DARK, idx)


def dome(m):
    whole = dome_solid()
    shading = mk.NormalSource(whole)
    obj = whole.copy()
    obj.data = whole.data.copy()
    obj.name = obj.data.name = "dome"
    bpy.context.scene.collection.objects.link(obj)
    rw.decimate(obj, set(), DOME_TARGET)
    rw.shade_like(obj, shading)
    centres, normals = face_data(obj)
    idx = dome_greys(centres, normals)
    used = sorted(set(idx.tolist()))
    obj.data.materials.clear()
    for u in used:
        obj.data.materials.append(m["dark"] if u == DARK else m[u])
    slot = {u: i for i, u in enumerate(used)}
    obj.data.polygons.foreach_set("material_index", [slot[u] for u in idx.tolist()])
    bpy.data.objects.remove(whole)
    return obj


def dome_top(u, y):
    """The dome's top at (u, y) (its seams left out)."""
    return float(crown_height(np.array([u]), np.array([y]))[0])


# --- Round parts ----------------------------------------------------------------------------------------------------

def ball(name, centre, radii, mat, around=28, rings=14, z_min=None):
    """An ellipsoid lofted from explicit rings (the same mesh every run), its poles on z; flattened below z_min."""
    verts = [(centre.x, centre.y, centre.z - radii.z)]
    for i in range(1, rings):
        a = -math.pi / 2 + math.pi * i / rings
        for j in range(around):
            b = 2 * math.pi * j / around
            verts.append((centre.x + radii.x * math.cos(a) * math.cos(b),
                          centre.y + radii.y * math.cos(a) * math.sin(b), centre.z + radii.z * math.sin(a)))
    verts.append((centre.x, centre.y, centre.z + radii.z))
    if z_min is not None:
        verts = [(x, y, max(z, z_min)) for x, y, z in verts]
    faces = [(0, 1 + (j + 1) % around, 1 + j) for j in range(around)]
    for i in range(rings - 2):
        for j in range(around):
            a, b = 1 + i * around + j, 1 + i * around + (j + 1) % around
            faces.append((a, b, b + around, a + around))
    top = len(verts) - 1
    base = 1 + (rings - 2) * around
    faces += [(base + j, base + (j + 1) % around, top) for j in range(around)]
    obj = k.mesh_object(name, verts, faces, mat)
    k.recalc_normals(obj)
    return k.smooth(obj, 60)


def lamp(m, hot, rest):
    """The lamp: a squat glass dome on the dome's back, tilted with it, in a grey ring; hottest along its front (the
    side the camera sees), the rest of it glowing less."""
    y, out, (rx, ry, rz), ring = LAMP
    base = dome_top(0.0, y) - 0.35
    centre = Vector((0.0, y, base + out))
    glass = ball("lamp", centre, Vector((rx, ry, rz)), m[("lamp",) + rest], around=24, rings=10, z_min=base - 0.3)

    def front(co, n):
        return (y + 0.35 - co.y) / ry          # 0 across its middle, 1 at its front

    paint_bands(glass, [(lambda co, n: front(co, n) - 0.05, 0.0)],
                lambda c, n: m[("lamp",) + (hot if front(c, n) > 0.05 else rest)])
    k.smooth(glass, 60)
    count = 24
    rim = [(rx * 1.08 * math.cos(2 * math.pi * j / count), y + ry * 1.12 * math.sin(2 * math.pi * j / count))
           for j in range(count)]
    verts = [(x * (1 + ring / rx), yy + (yy - y) * ring / ry, dome_top(x, yy) - 0.3) for x, yy in rim]
    verts += [(x, yy, dome_top(x, yy) + 0.35) for x, yy in rim]
    verts += [(x * 0.92, y + (yy - y) * 0.92, dome_top(x, yy) + 0.15) for x, yy in rim]
    faces = []
    for a, b in ((0, count), (count, 2 * count)):
        for j in range(count):
            faces.append((a + j, a + (j + 1) % count, b + (j + 1) % count, b + j))
    ring_obj = k.mesh_object("lamp_ring", verts, faces, m[GREYS[2]])
    k.recalc_normals(ring_obj)
    k.smooth(ring_obj, 50)
    return [glass, ring_obj]


def eye(m, levels):
    """The eye: a ball in the socket, its rings of heat round the point the camera sees straight on."""
    centre, radius = EYE
    obj = ball("eye", centre, Vector((radius, radius, radius)), m[("eye",) + levels[2]], around=24, rings=12)
    view = Vector((0.0, -math.sin(math.radians(VIEW_TILT)), math.cos(math.radians(VIEW_TILT))))

    def heat(co, n):
        return 1.0 - n.dot(view)

    def paint(c, n):
        h = 1.0 - n.dot(view)
        return m[("eye",) + (levels[0] if h < EYE_RINGS[0] else levels[1] if h < EYE_RINGS[1] else levels[2])]
    paint_bands(obj, [(lambda co, n, r=r: heat(co, n) - r, 0.0) for r in EYE_RINGS], paint)
    return k.smooth(obj, 60)


def socket(m):
    """The dark socket round the eye: under the brow, between the flaps and the eye, under the eye."""
    c, r = SOCKET
    return ball("socket", c, r, m["dark"], around=24, rings=10)


# --- The claws ------------------------------------------------------------------------------------------------------

def claw(m, side, turn):
    """One claw: an oval tube along the 5 (CLAW), broad across (square to its path, horizontally) and thinner up, its
    blade turned up and in about the hinge (an axis along y at the stem's foot) by turn degrees, the turn growing over
    the stem's foot; painted in bands of the light its faces get."""
    keys = [Vector(p) for p, _ in CLAW]
    sections = [s for _, s in CLAW]
    hinge_i, hu, hz = HINGE
    path = resample(chaikin_open(keys, 3), 40)
    # Each point's share of the turn (0 up to the key before the hinge, 1 from the key after it), and its section:
    # interpolated along the keys by the nearest key positions.
    key_s = [0.0]
    for a, b in zip(keys, keys[1:]):
        key_s.append(key_s[-1] + (b - a).length)
    lengths = [0.0]
    for a, b in zip(path, path[1:]):
        lengths.append(lengths[-1] + (b - a).length)
    scale = key_s[-1] / lengths[-1]
    rings = []
    around = 16
    tangents = [(path[min(i + 1, len(path) - 1)] - path[max(i - 1, 0)]).normalized() for i in range(len(path))]
    previous = None
    for i, p in enumerate(path):
        s = lengths[i] * scale
        j = max(0, min(len(key_s) - 2, sum(1 for v in key_s[1:-1] if v <= s)))
        f = (s - key_s[j]) / max(1e-9, key_s[j + 1] - key_s[j])
        a = sections[j][0] + (sections[j + 1][0] - sections[j][0]) * f
        b = sections[j][1] + (sections[j + 1][1] - sections[j][1]) * f
        w = smoothstep(key_s[hinge_i - 1], key_s[hinge_i + 1], s)
        t = tangents[i]
        across = Vector((-t.y, t.x, 0.0)).normalized()
        up = t.cross(across).normalized()
        if (previous is None and up.z < 0) or (previous is not None and up.dot(previous) < 0):
            up = -up
        previous = up
        ring = [p + across * (a * math.cos(2 * math.pi * q / around)) + up * (b * math.sin(2 * math.pi * q / around))
                for q in range(around)]
        angle = math.radians(turn) * w
        if angle:
            # the turn: about the axis along y through (hu, hz), the outer (lower u) side going up
            ca, sa = math.cos(angle), math.sin(angle)
            ring = [Vector((hu + (v.x - hu) * ca + (v.z - hz) * sa, v.y, hz - (v.x - hu) * sa + (v.z - hz) * ca))
                    for v in ring]
        rings.append(ring)
    start = rings[0]
    end = rings[-1]
    c0 = sum(start, Vector()) / len(start) - tangents[0] * 0.3
    end_mid = sum(end, Vector()) / len(end)
    c1 = end_mid + (end_mid - sum(rings[-2], Vector()) / len(rings[-2])) * 0.8
    obj = k.loft(f"claw_{'l' if side < 0 else 'r'}", rings, m[TAN[1][2]], start_point=c0, end_point=c1)
    for v in obj.data.vertices:      # (a flat underside where a blade turns below it: every frame the same bounds)
        v.co.z = max(v.co.z, CLAW_FLOOR)
    if side > 0:
        obj.data.transform(Matrix.Scale(-1.0, 4, (1.0, 0.0, 0.0)))
        obj.data.flip_normals()
    k.recalc_normals(obj)
    k.smooth(obj, 70)
    paint_bands(obj, [(lambda co, n, b=b: light(n) - b, 0.0) for b in TAN[0]], lambda cc, n: m[band(TAN, light(n))])
    return k.smooth(obj, 70)


# --- The model ------------------------------------------------------------------------------------------------------

def build_model(m, turn, lamp_levels, eye_levels):
    parts = [dome(m)] + lamp(m, *lamp_levels) + [eye(m, eye_levels), socket(m)]
    parts += [claw(m, side, turn) for side in (-1.0, 1.0)]
    mk.transform(parts, Matrix.Translation((AXIS_X, 0.0, 0.0)))
    return triangulate(parts)


def outline_ring(sheet, sprite):
    """The sprite's outline: its near-black pixels (0x01) next to a transparent one."""
    from sprite_profile import sprite_indices
    idx = sprite_indices(sheet, sprite)
    h, w = len(idx), len(idx[0])

    def empty(r, c):
        return not (0 <= r < h and 0 <= c < w) or idx[r][c] is None
    return [[idx[r][c] == 0x01 and any(empty(r + dr, c + dc) for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)))
             for c in range(w)] for r in range(h)]


def compare_core(label, covered, mask, ring):
    """The overlap leaving the sprite's outline ring out (neither counted for nor against)."""
    h, w = len(mask), len(mask[0])
    both = sum(covered[y][x] and mask[y][x] and not ring[y][x] for y in range(h) for x in range(w))
    either = sum((covered[y][x] or mask[y][x]) and not ring[y][x] for y in range(h) for x in range(w))
    print("silhouette overlap %s without the sprite's outline: %.3f" % (label, both / max(either, 1)))
    return both / max(either, 1)


def build():
    options = k.args()
    out = mk.outdir(options)
    only = set(options["only"].split(",")) if "only" in options else None
    for name, sprite, turn, lamp_levels, eye_levels in FRAMES:
        if only is not None and name not in only:
            continue
        k.reset()
        bpy.context.scene.view_settings.view_transform = "Standard"
        m = materials()
        parts = build_model(m, turn, lamp_levels, eye_levels)
        bpy.context.view_layer.update()
        if "check" in options:
            sheet = os.path.join(options["check"], "enemy_8.png")
            covered, mask = mk.coverage(parts, 24, 28), k.sprite_mask(sheet, sprite)
            mk.compare("%s (8 %d)" % (name, sprite), covered, mask)
            compare_core("%s (8 %d)" % (name, sprite), covered, mask, outline_ring(sheet, sprite))
        mk.report(name, parts, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, parts)


if __name__ == "__main__":
    build()
