"""SAVARA's grey airship (SAVARA, SAVARA V, SAVARA Y; episodes 1, 3 and 5), polished (2026-10-20; it replaces
wave3_k.py's zeppelin_whole(), a plain egg with lat-long lines, and wave3_ar_beasts.py's zeppelin_fan()). Sheet I,
seventeen 2x2 sprites, each an enemy of its own (349-365; 1089-1105 in episode 5), which the levels always place
as one 96 x 140 picture and move together (SAVARA's events 2000-2014 and 2500-2514: 39 41 43 45 at x, x + 24, x + 48,
x + 72, the rows 77-83 and 115-121 28 and 56 pixels below them, 154 156 158 at x + 12, x + 36, x + 60 below those,
and 14 frames later 3 and 5 at x + 24 and x + 48 above the first row): the stern I 3, 5 (columns 24-71 of rows 0-27
of the picture), the rows I 39-45, 77-83 and 115-121 (columns 0-95 of rows 28-111) and the nose I 154, 156, 158
(columns 12-83 of rows 112-139). All are ground enemies: the airship floats a little above the ground layer, its
nose down the screen. models.cfg: model zeppelin_<sprite> enemies/zeppelin_<sprite>.glb origin; sprite i <sprite>
zeppelin_<sprite> yaw=0 (as before). I 3, 5, 41 and 43 alternate with 17, 55, 93 and 131, the fan turning: frame
models zeppelin_17, 55, 93, 131 (frame i 17 zeppelin_17 ...), the same pieces with the fan turned by half a blade.
Its damaged look (the dgr sprites 8 further on) is polish_airship_damaged.py's, built from this one.

As the sprites and the whole sheet's 4x upscale draw it, built as an airship in the round:
- The envelope: a long egg of grey fabric, widest (69 pixels) over its middle, rounder at the stern than at the
  nose, its cross-section a flattened ellipse (it floats from 1 to 35 pixels up; the duct's bridge reaches 38). It
  is sewn from eight gores that bulge a little between their seams, and a net of lighter ropes lies over its top
  and flanks: a diamond mesh (fourteen meshes round) whose ropes press into the fabric, which bulges softly in each
  mesh, knotted where they cross. The net ends in a hoop near the nose, from which eight ropes run down the gores'
  seams to a cap on the nose (the sprite's lines meeting at the nose), at a load rope along each flank and under
  the stern's cowl.
- The stern: a grey metal cowl over the envelope's tail with two rounded shoulders either side of a long hub
  fairing (the sprite's grey dome between the red brackets), seams round the shoulders, its front edge swept back
  in a chevron (the sprite's diagonal bands from the brackets to the flanks) with a broad rim. Behind it the fan: a
  red duct round eight broad pale blades on a hub, its axis tilted 30 degrees towards the nose (its back raised),
  so that seen from above its back is the sprite's arch and its sides the arch's legs, which run into the cowl's
  flanks (fairings there); the game's camera looks almost down its axis and sees its broad inlet face (the
  sprite's red band, light along its outer edge). Its front passes under the envelope's belly, where nothing sees
  it, and is left out. The grey bridge rises from the hub fairing's end over the blades to a clamp on the duct's
  back, a dark channel along it with five lamps glowing red to orange (a little).
- On its back: red brackets either side of the hub fairing, the red gate in front of it (a crossbar on a stem,
  four legs, feet on the outer ones) and the red sensor pod on the envelope's crown with its dark visor.
- The gun pods at its sides (the left one built, the right one its mirror image): a red mount (lit along its top)
  on a grey strut from the envelope's flank, a red rod under the strut and a grey coupling across it into which a
  red hose curves down from the cowl's flank; the grey pod hanging along the envelope, red bands, a red pipe along
  its top and one down its inner side, a thin red barrel from its outer side and a grey muzzle whose bore and lip
  glow orange (a little: the game's bloom burns strong emission white).

The envelope's mesh is finer over its top than underneath and coarser on its smaller rings (rings stitched
together), and left out under the cowl. The airship is built whole and cut along the sprites' edges into the
seventeen pieces (polish_arch.cut: the pieces keep the whole's shading across the cuts, their cuts capped), each
moved so that its sprite's centre is its origin (its base on the layer: z = 0 is the ground layer): drawn at their
own places they meet again. The fan's frames are the same cut with the blades turned by 22.5 degrees (eight blades:
the sprites' frames show them at 45 and 135 degrees round the duct, then at 22.5, 67.5, 112.5 and 157.5).

Coordinates: 1 unit = 1 game pixel; x = the picture's column edge - 48 (it is symmetric about the middle of column
48: the parts are built about X = x - 0.5 = 0 and moved there, AXIS_X), y = 70 - the row edge, +Z up from the
ground layer. Colours are the sprites' palette indices (palette materials).

Replaces wave3_k.py's airship (zeppelin_whole and its helpers that the red fighter doesn't use, ZEPPELIN_PIECES,
OBJECTS["zeppelin"]), wave3_ar_beasts.py's zeppelin_fan, and with polish_airship_damaged.py wave3_ao_zeppelin.py and
wave3_ao_art.py's ZEP and ZEP_DMG.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes of the
whole and of each piece against enemy_I.png), --preview <prefix> (the whole's and each piece's top and 3/4 views),
--only <model,...> (pieces to export, frames by their own names; "none": none), --whole <file.glb> (the uncut
airship as well, for looking at), --frames 0 (no fan frames).
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
from polish_arch import cut  # noqa: E402  (polish_machine_kit.cut without its material indices shifted twice)

AXIS_X = 0.5
# name, sprite, the box it covers in the whole's coordinates (x0, x1, y0, y1)
PIECES = [(f"zeppelin_{s}", s, box) for s, box in (
    (3, (-24, 0, 42, 70)), (5, (0, 24, 42, 70)),
    (39, (-48, -24, 14, 42)), (41, (-24, 0, 14, 42)), (43, (0, 24, 14, 42)), (45, (24, 48, 14, 42)),
    (77, (-48, -24, -14, 14)), (79, (-24, 0, -14, 14)), (81, (0, 24, -14, 14)), (83, (24, 48, -14, 14)),
    (115, (-48, -24, -42, -14)), (117, (-24, 0, -42, -14)), (119, (0, 24, -42, -14)), (121, (24, 48, -42, -14)),
    (154, (-36, -12, -70, -42)), (156, (-12, 12, -70, -42)), (158, (12, 36, -70, -42)))]
# The fan's frames: the pieces they replace while the fan turns.
FAN_FRAMES = {3: 17, 5: 55, 41: 93, 43: 131}


def cell_of(box):
    """A piece's top left corner in the 96 x 140 picture."""
    return (int(box[0] + 48), int(70 - box[3]))


# --- Numbers ---------------------------------------------------------------------------------------------------

def smoothstep(e0, e1, x):
    t = min(1.0, max(0.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


def monotone(xs, ys):
    """A smooth curve through (xs, ys) that never overshoots them (monotone cubic)."""
    n = len(xs)
    d = [(ys[i + 1] - ys[i]) / (xs[i + 1] - xs[i]) for i in range(n - 1)]
    m = [d[0]] + [(d[i - 1] + d[i]) / 2 if d[i - 1] * d[i] > 0 else 0.0 for i in range(1, n - 1)] + [d[-1]]
    for i in range(n - 1):
        if d[i] == 0:
            m[i] = m[i + 1] = 0.0
            continue
        a, b = m[i] / d[i], m[i + 1] / d[i]
        if a * a + b * b > 9:
            t = 3 / math.sqrt(a * a + b * b)
            m[i], m[i + 1] = t * a * d[i], t * b * d[i]

    def f(x):
        x = min(max(x, xs[0]), xs[-1])
        i = max(0, min(n - 2, next((j for j in range(n - 1) if x <= xs[j + 1]), n - 2)))
        h = xs[i + 1] - xs[i]
        t = (x - xs[i]) / h
        return ((2 * t ** 3 - 3 * t ** 2 + 1) * ys[i] + (t ** 3 - 2 * t ** 2 + t) * h * m[i] +
                (-2 * t ** 3 + 3 * t ** 2) * ys[i + 1] + (t ** 3 - t ** 2) * h * m[i + 1])
    return f


def frame_of(t):
    """Two unit vectors perpendicular to t and to each other."""
    ref = Vector((0, 0, 1)) if abs(t.z) < 0.9 else Vector((1, 0, 0))
    a = t.cross(ref).normalized()
    return a, t.cross(a).normalized()


# --- Materials -------------------------------------------------------------------------------------------------

def materials():
    pal = k.level_palette()

    def mat(name, index, metallic=0.0, roughness=0.5, **kw):
        return k.material("zep_" + name, palette=index, metallic=metallic, roughness=roughness, **kw)
    return {
        "fabric": mat("fabric", 0x0a, 0.0, 0.72),
        "rope": mat("rope", 0x0c, 0.0, 0.8),
        "steel": mat("steel", 0x08, 0.55, 0.36),
        "steel_light": mat("steel_light", 0x0a, 0.55, 0.3),
        "dark": mat("dark", 0x03, 0.4, 0.5),
        "red": mat("red", 0x46, 0.35, 0.34),
        "red_dark": mat("red_dark", 0x43, 0.35, 0.4),
        "red_light": mat("red_light", 0x49, 0.3, 0.28),
        "blade": mat("blade", 0x0f, 0.1, 0.5),
        "cowl": mat("cowl", 0x0a, 0.35, 0.4),
        "lamp": mat("lamp", 0x74, 0.0, 0.3, emission=pal[0x75], emission_strength=0.5),
        "lamp_hot": mat("lamp_hot", 0x77, 0.0, 0.3, emission=pal[0x78], emission_strength=0.5),
        "fire": mat("fire", 0x78, 0.0, 0.4, emission=pal[0x78], emission_strength=0.6),
        "glass": mat("glass", 0x01, 0.6, 0.08),
    }


# --- The envelope ------------------------------------------------------------------------------------------------
# Its half-width along y (the outline's runs of pixels: the middle of each run, a fifth of a pixel inside), from
# the nose (y -70.35) to the stern's end under the cowl (42.6).
PROFILE = [(-70.35, 0.0), (-70.1, 2.9), (-69.6, 5.1), (-69.0, 7.0), (-68.3, 8.6), (-67.5, 10.2), (-66.5, 11.95),
           (-65.5, 13.5), (-64.5, 14.95), (-63.5, 16.2), (-62.5, 17.35), (-61.5, 18.35), (-60.5, 19.35),
           (-59.5, 20.3), (-58.5, 21.25), (-57.5, 22.2), (-56.0, 23.3), (-54.5, 24.35), (-53.5, 25.15),
           (-52.5, 25.95), (-51.0, 27.05), (-49.0, 28.2), (-46.5, 29.3), (-43.5, 30.35), (-41.0, 31.3), (-38.5, 32.25),
           (-35.0, 33.2), (-31.0, 34.0), (-26.0, 34.28), (-14.0, 34.3), (1.0, 34.28), (4.5, 34.0), (7.0, 33.45),
           (12.0, 32.4), (19.5, 30.3), (25.0, 27.9), (30.0, 24.6), (34.0, 20.9), (37.0, 17.2), (39.5, 13.0),
           (41.2, 8.8), (42.15, 5.0), (42.6, 0.0)]
NOSE_Y, STERN_Y = PROFILE[0][0], PROFILE[-1][0]
R_MAX = 34.3
ZC = 17.0                     # the envelope's axis height
SQ_TOP, SQ_BOT = 0.5, 0.46    # its cross-section: the upper and lower halves' heights over its half-width
_radius = monotone([p[0] for p in PROFILE], [p[1] for p in PROFILE])


def radius(y):
    return max(0.0, _radius(y)) if NOSE_Y < y < STERN_Y else 0.0


def radius_slope(y, h=0.02):
    return (radius(min(y + h, STERN_Y)) - radius(max(y - h, NOSE_Y))) / (min(y + h, STERN_Y) - max(y - h, NOSE_Y))


# The cross-section by arc length: psi runs from -pi to pi round it in equal lengths (0 at the top, +-pi/2 about
# its widest, positive towards +x).
_TH = np.linspace(-math.pi, math.pi, 4001)
_SQ = np.where(np.cos(_TH) >= 0, SQ_TOP, SQ_BOT)
_SX, _SZ = np.sin(_TH), _SQ * np.cos(_TH)
_S = np.concatenate([[0.0], np.cumsum(np.hypot(np.diff(_SX), np.diff(_SZ)))])
PERIMETER = _S[-1]            # the unit section's perimeter
_PSI = -math.pi + 2 * math.pi * _S / PERIMETER


def section(psi):
    """The unit section at psi (arrays): x, z and its outward normal (nx, nz) in the XZ plane."""
    th = np.interp(psi, _PSI, _TH)
    c, s = np.cos(th), np.sin(th)
    sq = np.where(c >= 0, SQ_TOP, SQ_BOT)
    nx, nz = sq * s, c
    length = np.hypot(nx, nz)
    return s, sq * c, nx / length, nz / length


def surface(y, psi):
    """The plain envelope (no gores, no net) at y and the angles psi (an array): points and normals (n x 3)."""
    r, dr = radius(y), radius_slope(y)
    sx, sz, nx, nz = section(np.asarray(psi, dtype=float))
    pts = np.stack([r * sx, np.full_like(sx, y), ZC + r * sz], axis=1)
    ny = -dr * (nx * sx + nz * sz)
    nrm = np.stack([nx, ny, nz], axis=1)
    nrm /= np.linalg.norm(nrm, axis=1)[:, None]
    return pts, nrm


# The gores: eight, seams at psi = k * 45 degrees (one along the crown), bulging GORE pixels at their middles (less
# towards the ends, where they narrow).
GORES = 8
GORE = 0.55


def gore_bulge(y, psi):
    f = np.mod(np.asarray(psi) / (2 * math.pi / GORES), 1.0)
    return GORE * (radius(y) / R_MAX) * (1.0 - (2 * f - 1) ** 2) ** 0.75


# The net: a diamond mesh, MESHES round the envelope, its ropes at 45 degrees on the surface. In the coordinates
# (psi, w), w = the integral of 2 pi sqrt(1 + (SQ_TOP r')^2) / (PERIMETER r) dy (a length along the envelope in
# the units of psi there, so that the meshes are square on its crown), the ropes are the lines u1 = (psi + w) / D
# and u2 = (psi - w) / D whole numbers (D = 2 pi / MESHES). It covers |psi| <= NET_PSI (the load ropes along the
# flanks) from the nose hoop (y NET_NOSE) to under the cowl; eight ropes run on down the gores' seams to the nose.
MESHES = 14
D = 2 * math.pi / MESHES
NET_PSI = math.radians(108.0)
NET_NOSE = -57.0
NET_STERN = 33.0
NET_PILLOW = 0.6              # how far the fabric bulges in a mesh (at the envelope's widest)
ROPE_R, LOAD_R = 0.34, 0.42   # the ropes' and the load ropes' radii
_WY = np.linspace(NOSE_Y + 0.6, STERN_Y - 0.6, 2400)
_WI = np.array([2 * math.pi * math.sqrt(1 + (SQ_TOP * radius_slope(y)) ** 2) / (PERIMETER * max(radius(y), 0.5))
                for y in _WY])
_W = np.concatenate([[0.0], np.cumsum((_WI[1:] + _WI[:-1]) / 2 * np.diff(_WY))])
_W -= np.interp(0.0, _WY, _W)      # w = 0 at y = 0


def w_of_y(y):
    return np.interp(y, _WY, _W)


def y_of_w(w):
    return np.interp(w, _W, _WY)


def net_weight(y, psi):
    """1 inside the net, falling to 0 at its edges (the hoops and load ropes there, the cowl's rim)."""
    pts, _ = surface(y, np.asarray(psi, dtype=float))
    edge_y = np.array([cowl_edge(x) for x in pts[:, 0]])
    d = np.minimum.reduce([np.full(len(pts), (y - NET_NOSE) * 1.0), (NET_PSI - np.abs(psi)) * radius(y),
                           edge_y - 1.0 - y])
    return np.clip(d / 1.6, 0.0, 1.0) ** 2 * (3 - 2 * np.clip(d / 1.6, 0.0, 1.0))


def pillow(y, psi):
    """How far the fabric bulges between the ropes at y, psi (array)."""
    w = w_of_y(y)
    u1, u2 = (psi + w) / D, (psi - w) / D
    f1, f2 = np.abs(np.sin(math.pi * u1)), np.abs(np.sin(math.pi * u2))
    return NET_PILLOW * (radius(y) / R_MAX) * (f1 * f2) ** 0.8 * net_weight(y, psi)


def envelope_point(y, psi, lift=0.0, with_pillow=True):
    """Points of the envelope as built (gores, the net's pillows), lifted off it along its normal."""
    psi = np.atleast_1d(np.asarray(psi, dtype=float))
    pts, nrm = surface(y, psi)
    out = gore_bulge(y, psi) + lift
    if with_pillow:
        out = out + pillow(y, psi)
    return pts + nrm * out[:, None], nrm


def envelope_stations(y_end, step_at=None):
    """The envelope's rings from its nose to y_end: about ENV_STEP (or step_at(y)) pixels apart along its
    outline."""
    ys = []
    y = NOSE_Y
    while True:
        base = step_at(y) if step_at else ENV_STEP
        step = base / math.sqrt(1 + radius_slope(min(max(y, NOSE_Y + 0.05), STERN_Y - 0.05)) ** 2)
        y += max(step, 0.1)
        if y >= y_end:
            break
        ys.append(y)
    return ys


ENV_STEP = 0.85               # the envelope's mesh: about this many pixels apart over its top and flanks
ENV_TOP = math.radians(118.0)  # (|psi| up to this), three times coarser underneath


def ring_angles(y):
    """The angles round the ring at y, fewer on the smaller rings; always starting at -pi, with -ENV_TOP and
    ENV_TOP among them, so that the rings' regions line up."""
    arc = PERIMETER * max(radius(y), 0.3) / (2 * math.pi)       # pixels per unit of psi
    n_top = max(8, int(round(2 * ENV_TOP * arc / ENV_STEP)))
    half = max(2, int(round((math.pi - ENV_TOP) * arc / (ENV_STEP * 3.0))))
    out = [-math.pi + (math.pi - ENV_TOP) * i / half for i in range(half)]
    out += [-ENV_TOP + 2 * ENV_TOP * i / n_top for i in range(n_top)]
    out += [ENV_TOP + (math.pi - ENV_TOP) * i / half for i in range(half)]
    return out


def stitch(faces, a, b, ta, tb):
    """Triangles between two closed rings of vertex indices a and b at the angles ta, tb (both from -pi up)."""
    na, nb = len(a), len(b)
    ta = list(ta) + [ta[0] + 2 * math.pi]
    tb = list(tb) + [tb[0] + 2 * math.pi]
    i = j = 0
    while i < na or j < nb:
        if j >= nb or (i < na and ta[i + 1] <= tb[j + 1]):
            faces.append((a[i], a[(i + 1) % na], b[j % nb]))
            i += 1
        else:
            faces.append((a[i % na], b[(j + 1) % nb], b[j]))
            j += 1


_COWL_PSI = np.linspace(-math.pi, math.pi, 361)
_COWL_FRONT = None


def cowl_front_at(psi):
    """cowl_front, interpolated."""
    global _COWL_FRONT
    if _COWL_FRONT is None:
        _COWL_FRONT = np.array([cowl_front(a) for a in _COWL_PSI])
    return np.interp(psi, _COWL_PSI, _COWL_FRONT)


def envelope(m, step_at=None, angles_at=None):
    """The fabric: rings stitched together, fewer points on the smaller rings; under the cowl it is left out.
    step_at(y) and angles_at(y) may make it finer in places (the damaged look's wounds)."""
    y_end = COWL_TIP + 3.0
    verts, faces, rings, hidden = [Vector((0.0, NOSE_Y, ZC))], [], [], []
    for y in envelope_stations(y_end, step_at):
        ta = angles_at(y) if angles_at else ring_angles(y)
        pts, _ = envelope_point(y, ta)
        start = len(verts)
        verts += [Vector(p) for p in pts]
        rings.append((list(range(start, start + len(ta))), ta))
        hidden += [y > f + 2.2 for f in cowl_front_at(np.array(ta))]
    hidden = [False] + hidden
    first, ta = rings[0]
    for i in range(len(first)):
        faces.append((0, first[(i + 1) % len(first)], first[i]))
    for (a, ta), (b, tb) in zip(rings, rings[1:]):
        stitch(faces, a, b, ta, tb)
    faces = [f for f in faces if not all(hidden[v] for v in f)]
    body = k.mesh_object("envelope", verts, faces, m["fabric"])
    k.recalc_normals(body)
    return k.smooth(body, 80)


# --- The net's ropes -------------------------------------------------------------------------------------------

def rope_mesh(name, paths, radius_, mat, lift=0.06):
    """Half-round ropes lying on the envelope along paths of (y, psi): one object."""
    verts, faces = [], []
    for path in paths:
        if len(path) < 2:
            continue
        pts, nrms = [], []
        for y, psi in path:
            p, n = envelope_point(y, [psi], lift=lift)
            pts.append(Vector(p[0]))
            nrms.append(Vector(n[0]))
        ring_start = len(verts)
        for i, (p, n) in enumerate(zip(pts, nrms)):
            t = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)])
            t = (t - n * t.dot(n)).normalized()
            b = t.cross(n).normalized()
            for a in (0.0, 62.0, 118.0, 180.0):   # half round, its feet a little in the fabric
                ar = math.radians(a)
                sink = 0.08 if a in (0.0, 180.0) else 0.0
                verts.append(p + b * math.cos(ar) * radius_ + n * (math.sin(ar) * radius_ * 1.05 - sink))
        n_ring = 4
        count = len(pts)
        for i in range(count - 1):
            for j in range(n_ring - 1):
                a = ring_start + i * n_ring + j
                faces.append((a, a + 1, a + 1 + n_ring, a + n_ring))
        # the ends rounded off: a point beyond each end
        for end, step in ((0, 1), (count - 1, -1)):
            p, n = pts[end], nrms[end]
            t = (pts[end] - pts[end + step]).normalized()
            verts.append(p + t * radius_ * 0.8 + n * radius_ * 0.3)
            c = len(verts) - 1
            base = ring_start + end * n_ring
            for j in range(n_ring - 1):
                faces.append((base + j, c, base + j + 1) if step == 1 else (base + j + 1, c, base + j))
    obj = k.mesh_object(name, verts, faces, mat)
    k.recalc_normals(obj)
    return k.smooth(obj, 70)


def resample_path(points, spacing):
    """A path of (y, psi) resampled about `spacing` pixels apart on the envelope."""
    xyz = []
    for y, psi in points:
        p, _ = surface(y, np.array([psi]))
        xyz.append(Vector(p[0]))
    lengths = [0.0]
    for a, b in zip(xyz, xyz[1:]):
        lengths.append(lengths[-1] + (b - a).length)
    total = lengths[-1]
    if total < 1e-6:
        return []
    count = max(1, int(math.ceil(total / spacing)))
    out, j = [], 0
    for i in range(count + 1):
        s = total * i / count
        while j < len(lengths) - 2 and lengths[j + 1] < s:
            j += 1
        seg = lengths[j + 1] - lengths[j]
        t = (s - lengths[j]) / seg if seg > 1e-9 else 0.0
        (y0, p0), (y1, p1) = points[j], points[j + 1]
        out.append((y0 + (y1 - y0) * t, p0 + (p1 - p0) * t))
    return out


def inside_net(y, psi, margin=0.0):
    if y < NET_NOSE + margin or abs(psi) > NET_PSI - margin / max(radius(y), 1.0):
        return False
    x = surface(y, np.array([psi]))[0][0][0]
    return y < cowl_edge(x) - 0.4 - margin


def net(m):
    """The diamond mesh's ropes and knots, the nose hoop with the eight ropes to the nose cap, the load ropes."""
    paths = []
    w0, w1 = w_of_y(NET_NOSE - 1.0), w_of_y(NET_STERN + 1.0)
    for family in (1, -1):
        # ropes psi + family * w = c D for whole c
        lo = math.floor((-NET_PSI + min(family * w0, family * w1)) / D) - 1
        hi = math.ceil((NET_PSI + max(family * w0, family * w1)) / D) + 1
        for c in range(lo, hi + 1):
            run = []
            for i in range(1201):
                w = w0 + (w1 - w0) * i / 1200
                psi = c * D - family * w
                y = float(y_of_w(w))
                if inside_net(y, psi):
                    run.append((y, psi))
                elif run:
                    paths.append(run)
                    run = []
            if run:
                paths.append(run)
    paths = [resample_path(p, 1.4) for p in paths if len(p) > 3]
    rope_mesh("net_ropes", paths, ROPE_R, m["rope"])
    # The knots: where whole u1 and u2 meet inside the net.
    knots = []
    for a in range(-80, 81):
        for b in range(-80, 81):
            if (a + b) % 2:
                continue
            psi, w = D * (a + b) / 2, D * (a - b) / 2
            if not (w0 <= w <= w1):
                continue
            y = float(y_of_w(w))
            if inside_net(y, psi, margin=0.3):
                knots.append((y, psi))
    knot_mesh("net_knots", knots, m["rope"])
    # The nose hoop, all the way round, and the load ropes along the flanks.
    hoop = [(NET_NOSE, -math.pi + 2 * math.pi * i / 200) for i in range(201)]
    rope_mesh("net_hoop", [resample_path(hoop, 1.1)], LOAD_R, m["rope"])
    loads = []
    for side in (-1, 1):
        ys = [NET_NOSE + (cowl_edge(-side * 30.0) - NET_NOSE) * i / 160 for i in range(161)]
        loads.append(resample_path([(y, side * NET_PSI) for y in ys], 1.1))
    rope_mesh("net_load", loads, LOAD_R, m["rope"])
    # The eight ropes down the gores' seams from the hoop to the nose cap.
    seams = []
    for g in range(GORES):
        psi = -math.pi + 2 * math.pi * g / GORES
        ys = [NET_NOSE - (NET_NOSE - (NOSE_Y + 1.3)) * i / 60 for i in range(61)]
        seams.append(resample_path([(y, psi) for y in ys], 0.9))
    rope_mesh("net_seams", seams, ROPE_R, m["rope"])
    k.smooth(k.lathe("nose_cap", [(NOSE_Y - 0.25, 0.0), (NOSE_Y - 0.2, 0.9), (NOSE_Y + 0.15, 1.7), (NOSE_Y + 0.8, 2.2),
                                  (NOSE_Y + 1.25, 2.1), (NOSE_Y + 1.5, 0.0)], m["steel"], segments=16, axis_z=ZC), 60)


def knot_mesh(name, knots, mat):
    """Small domes on the ropes' crossings."""
    verts, faces = [], []
    seg = 6
    profile = ((0.72, -0.05), (0.6, 0.38), (0.32, 0.62))
    for y, psi in knots:
        p, n = envelope_point(y, [psi], lift=0.0)
        p, n = Vector(p[0]), Vector(n[0])
        a, b = frame_of(n)
        base = len(verts)
        for rad, h in profile:
            for j in range(seg):
                ang = 2 * math.pi * j / seg
                verts.append(p + (a * math.cos(ang) + b * math.sin(ang)) * rad + n * h)
        verts.append(p + n * 0.7)
        top = len(verts) - 1
        for ring in range(len(profile) - 1):
            for j in range(seg):
                r0, r1 = base + ring * seg, base + (ring + 1) * seg
                faces.append((r0 + j, r0 + (j + 1) % seg, r1 + (j + 1) % seg, r1 + j))
        last = base + (len(profile) - 1) * seg
        for j in range(seg):
            faces.append((last + j, last + (j + 1) % seg, top))
    obj = k.mesh_object(name, verts, faces, mat)
    k.recalc_normals(obj)
    return k.smooth(obj, 80)


# --- The stern: the cowl and the hub fairing --------------------------------------------------------------------
# The cowl: a metal shell COWL_OFF off the envelope over its tail, its front edge level at y COWL_TIP out to |X|
# COWL_FLAT and swept forward beyond (a chevron: the sprite's diagonal bands from the brackets to the flanks), with a
# rolled rim; two shoulders on it either side of the middle (centre (|X|, y), half-width, half-length, height).
COWL_TIP, COWL_FLAT, COWL_SWEEP = 30.5, 6.0, 0.29
COWL_OFF = 1.15
SHOULDER = ((10.5, 35.2), 8.2, 6.6, 2.4)
# The hub fairing along the middle (the sprite's grey dome between the brackets): from y HUB_Y[0] to HUB_Y[1].
HUB_Y = (25.4, 40.2)


def cowl_edge(x):
    """The cowl's front edge (y) over x."""
    return COWL_TIP - COWL_SWEEP * max(0.0, abs(x) - COWL_FLAT)


def shoulder(x, y):
    (cx, cy), a, b, h = SHOULDER
    d2 = ((abs(x) - cx) / a) ** 2 + ((y - cy) / b) ** 2
    return h * (1 - d2) ** 2 if d2 < 1 else 0.0


def cowl_point(y, psi, lift=0.0):
    p, n = surface(y, np.array([psi]))
    p, n = Vector(p[0]), Vector(n[0])
    return p + n * (COWL_OFF + shoulder(p.x, p.y) + lift), n


def cowl_front(psi):
    """The y where the cowl begins at psi."""
    y = COWL_TIP
    for _ in range(40):
        x = surface(y, np.array([psi]))[0][0][0]
        y = 0.5 * y + 0.5 * cowl_edge(x)
    return y


def cowl(m):
    top = math.radians(100.0)
    angles = [-top + 2 * top * i / 66 for i in range(66)]
    angles += [top + (2 * math.pi - 2 * top) * i / 12 for i in range(12)]
    angles = [a if a <= math.pi else a - 2 * math.pi for a in angles]
    angles.sort()
    fronts = [cowl_front(a) for a in angles]
    rows = 21
    rings = []
    for i in range(rows):
        t = i / rows
        s = t ** 1.15
        ring = []
        for a, y0 in zip(angles, fronts):
            y = y0 + (STERN_Y - 0.05 - y0) * s
            ring.append(cowl_point(y, a)[0])
        rings.append(ring)
    shell = k.loft("cowl", rings, m["cowl"], cap_start=False, end_point=(0, STERN_Y + COWL_OFF, ZC))
    k.smooth(shell, 60)
    # The rim along its front edge, over the top and flanks.
    path, ups = [], []
    for i in range(91):
        a = -top + 2 * top * i / 90
        p, n = cowl_point(cowl_front(a), a, lift=-0.15)
        path.append(p)
        ups.append(n)
    k.smooth(mk.bar("cowl_rim", path, ups, 1.3, 0.85, 0.7, m["steel"], segments=8, power=3.0), 70)
    # Seams round the shoulders.
    (cx, cy), a_, b_, _ = SHOULDER
    for side in (-1, 1):
        pts = []
        for j in range(37):
            ang = 2 * math.pi * j / 36
            x, y = side * (cx + 0.93 * a_ * math.cos(ang)), cy + 0.93 * b_ * math.sin(ang)
            pts.append(cowl_point(y, psi_at(x, y), lift=-0.05)[0])
        k.smooth(mk.tube("cowl_seam_%s" % ("l" if side < 0 else "r"), pts, 0.24, m["dark"], segments=4), 100)
    hub_fairing(m)
    return shell


def psi_at(x, y):
    """The angle psi of the envelope's top at (x, y) (|x| below its half-width there)."""
    r = max(radius(y), 1e-3)
    lo, hi = -math.pi / 2, math.pi / 2
    for _ in range(40):
        mid = (lo + hi) / 2
        if r * section(np.array([mid]))[0][0] < x:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def hub_fairing(m):
    """A long rounded fairing on the cowl's middle from the gate's stem to the bridge's foot."""
    y0, y1 = HUB_Y
    rings = []
    count = 22
    for i in range(1, count):
        y = y0 + (y1 - y0) * i / count
        f = math.sqrt(max(0.0, 1 - ((y - (y0 + 5.0)) / 5.0) ** 2)) if y < y0 + 5.0 else 1.0
        w = 3.5 * f * (1 - 0.12 * smoothstep(y0 + 5, y1, y))
        h = 2.9 * f * (1 - 0.1 * smoothstep(y0 + 5, y1, y))
        z = cowl_point(y, 0.0)[0].z
        rings.append(k.ring(y, max(w, 0.08), 1.0, 16, z=z - 0.4, top=max(h + 0.4, 0.1), bottom=1.6, power=2.2))
    z0 = cowl_point(y0, 0.0)[0].z
    z1 = cowl_point(y1, 0.0)[0].z
    body = k.loft("hub_fairing", rings, m["steel_light"], start_point=(0, y0, z0 - 0.2), end_point=(0, y1 + 0.3, z1))
    return k.smooth(body, 60)


# --- The fan -------------------------------------------------------------------------------------------------------
# The duct: a ring of airfoil section round FAN_C, its axis tilted FAN_TILT from the vertical towards the nose (its
# back raised): in the ring's frame a point is FAN_C + X rho cos(phi) + B rho sin(phi) + A h (phi 0 at +X, 90 at the
# back; h along the axis, its inlet lip up).
FAN_C = Vector((0.0, 37.4, 20.4))
FAN_TILT = math.radians(30.0)
FX = Vector((1.0, 0.0, 0.0))
FB = Vector((0.0, math.cos(FAN_TILT), math.sin(FAN_TILT)))
FA = Vector((0.0, -math.sin(FAN_TILT), math.cos(FAN_TILT)))
# Its section (rho, h), closed: from the exit's trailing edge up the inner wall, over the broad inlet face (which
# the game's camera sees almost face on: the sprite's band), down the outside. Its edges up to DUCT_INNER are the
# inner wall (dark red), then the inlet face (red), the outer edge (light red) up to DUCT_RIM, the rest red.
DUCT = [(20.2, -5.0), (19.75, -3.6), (19.5, -1.8), (19.4, 0.2), (19.45, 2.2), (19.6, 3.6), (19.9, 4.45), (20.4, 4.9),
        (21.2, 5.08), (22.2, 5.15), (23.2, 5.08), (23.95, 4.85), (24.45, 4.35), (24.68, 3.6), (24.72, 2.2),
        (24.6, 0.4), (24.3, -1.4), (23.75, -3.0), (22.95, -4.3), (21.9, -5.1)]
DUCT_INNER, DUCT_RIM = 6, 14
DUCT_SEGMENTS = 96
DUCT_HIDDEN = (math.radians(215.0), math.radians(325.0))   # its front under the envelope's belly: left out
BLADES = 8
BLADE_ROOT, BLADE_TIP = 3.0, 18.9


def fan_point(rho, phi, h):
    return FAN_C + FX * (rho * math.cos(phi)) + FB * (rho * math.sin(phi)) + FA * h


def duct(m):
    n = len(DUCT)
    verts, faces, mats = [], [], []
    for j in range(DUCT_SEGMENTS):
        phi = 2 * math.pi * j / DUCT_SEGMENTS
        verts += [fan_point(rho, phi, h) for rho, h in DUCT]
    for j in range(DUCT_SEGMENTS):
        phi = 2 * math.pi * (j + 0.5) / DUCT_SEGMENTS
        if DUCT_HIDDEN[0] < phi < DUCT_HIDDEN[1]:
            continue
        for i in range(n):
            a, b = j * n + i, j * n + (i + 1) % n
            c, d = ((j + 1) % DUCT_SEGMENTS) * n + (i + 1) % n, ((j + 1) % DUCT_SEGMENTS) * n + i
            faces.append((a, b, c, d))
            mats.append(2 if i < DUCT_INNER else 1 if 12 <= i < DUCT_RIM else 0)
    # the open ends closed
    for phi0 in DUCT_HIDDEN:
        j = int(round(phi0 / (2 * math.pi) * DUCT_SEGMENTS))
        faces.append(tuple(j * n + i for i in range(n)))
        mats.append(2)
    obj = k.mesh_object("duct", verts, faces, m["red"])
    obj.data.materials.append(m["red_light"])
    obj.data.materials.append(m["red_dark"])
    for poly, mi in zip(obj.data.polygons, mats):
        poly.material_index = mi
    k.recalc_normals(obj)
    return k.smooth(obj, 50)


def blade(name, phi0, mat):
    """One broad blade at angle phi0: sections across the radius, pitched, twisted and cambered."""
    stations = [BLADE_ROOT, 4.5, 7.0, 10.0, 12.8, 15.4, 17.3, 18.4, BLADE_TIP]
    rings = []
    for rho in stations:
        f = (rho - BLADE_ROOT) / (BLADE_TIP - BLADE_ROOT)
        chord = 4.2 + 3.0 * f ** 0.8
        if rho > 17.3:
            chord *= 0.8 + 0.2 * math.sqrt(max(0.0, (BLADE_TIP - rho) / (BLADE_TIP - 17.3)))
        pitch = math.radians(30.0 - 12.0 * f)
        thick = 0.75 - 0.38 * f
        camber = 0.3 * chord / 6.0
        er = FX * math.cos(phi0) + FB * math.sin(phi0)
        et = -FX * math.sin(phi0) + FB * math.cos(phi0)
        along = et * math.cos(pitch) + FA * math.sin(pitch)
        normal = -et * math.sin(pitch) + FA * math.cos(pitch)
        centre = FAN_C + er * rho
        ring = []
        for j in range(12):
            a = 2 * math.pi * j / 12
            u = math.cos(a)                       # along the chord, -1..1
            v = math.sin(a)
            shape = math.sqrt(max(0.0, 1 - u * u))
            d = camber * (1 - u * u) + v * thick / 2 * (0.35 + 0.65 * shape)
            ring.append(centre + along * (u * chord / 2) + normal * d)
        rings.append(ring)
    tip = FAN_C + (FX * math.cos(phi0) + FB * math.sin(phi0)) * (BLADE_TIP + 0.12)
    obj = k.loft(name, rings, mat, end_point=tip)
    return k.smooth(obj, 50)


def fan_blades(m, phase=0):
    """The eight blades; phase 1: turned half a blade (the sprites' second frame)."""
    blades = []
    for i in range(BLADES):
        phi = 2 * math.pi * i / BLADES + (math.pi / BLADES if phase else 0.0)
        blades.append(blade("blade_%d" % i, phi, m["blade"]))
    return blades


def fan_hub(m):
    """The fan's hub (inside the cowl's tail)."""
    hub = k.lathe("fan_hub", [(-2.4, 0.0), (-2.4, 3.2), (-1.8, 3.6), (1.2, 3.6), (1.8, 3.1), (2.6, 1.8), (3.0, 0.0)],
                  m["steel"], segments=24)
    # the lathe runs along Y: its Y becomes the fan's axis (X stays, Z goes to -B)
    hub.data.transform(Matrix(((FX.x, FA.x, -FB.x, FAN_C.x), (FX.y, FA.y, -FB.y, FAN_C.y), (FX.z, FA.z, -FB.z, FAN_C.z),
                               (0, 0, 0, 1))))
    return k.smooth(hub, 50)


def frame_matrix(origin, along, up):
    """Local (x across, y along, z up) to world."""
    along = along.normalized()
    up = (up - along * up.dot(along)).normalized()
    across = along.cross(up).normalized()
    return Matrix(((across.x, along.x, up.x, origin.x), (across.y, along.y, up.y, origin.y),
                   (across.z, along.z, up.z, origin.z), (0, 0, 0, 1)))


# The bridge from the hub fairing's back (BRIDGE[0]) up over the blades to the duct's back rim (BRIDGE[1]), and the
# lamps in its channel (y of their middles, lengths along it; the lowest two the hottest).
BRIDGE = (Vector((0.0, 39.4, 28.4)), Vector((0.0, 51.7, 36.5)))
LAMPS = [(50.2, 1.4, "lamp"), (48.2, 1.4, "lamp"), (46.2, 1.4, "lamp"), (44.2, 1.4, "lamp_hot"),
         (42.2, 1.4, "lamp_hot")]


def bridge(m):
    p0, p1 = BRIDGE
    d = (p1 - p0)
    length = d.length
    up = Vector((0.0, -d.normalized().z, d.normalized().y))
    to_world = frame_matrix(p0, d, up)
    parts = []

    def box(name, x0, x1, y0, y1, z0, z1, mat, bevel=0.0):
        obj = mk.box(name, x0, x1, y0, y1, z0, z1, mat)
        if bevel:
            mk.bevel(obj, bevel, segments=2)
        parts.append(obj)
        return obj
    box("bridge_base", -4.2, 4.2, -1.0, length + 0.6, -1.8, -0.2, m["steel"], 0.45)
    box("bridge_rail_l", -4.2, -2.0, -0.6, length + 0.4, -0.5, 1.35, m["steel_light"], 0.5)
    box("bridge_rail_r", 2.0, 4.2, -0.6, length + 0.4, -0.5, 1.35, m["steel_light"], 0.5)
    box("bridge_channel", -2.05, 2.05, 0.4, length - 0.4, -0.5, 0.25, m["dark"])
    for i, (y, h, mat) in enumerate(LAMPS):
        t = (y - p0.y) / d.normalized().y
        box("lamp_%d" % i, -1.65, 1.65, t - h / 2, t + h / 2, 0.1, 0.62, m[mat], 0.12)
    box("bridge_foot", -4.5, 4.5, -2.0, 2.2, -2.6, 0.9, m["steel"], 0.5)
    for obj in parts:
        obj.data.transform(to_world)
    # The clamp over the duct's back rim: a block in the duct's own frame, wrapping its lip.
    c = mk.box("bridge_clamp", -4.4, 4.4, 20.4, 25.5, -3.4, 6.3, m["steel"])
    mk.bevel(c, 0.7, segments=2)
    c.data.transform(Matrix(((1, 0, 0, FAN_C.x), (0, FB.y, FA.y, FAN_C.y), (0, FB.z, FA.z, FAN_C.z), (0, 0, 0, 1))))
    parts.append(c)
    return parts


def duct_boots(m):
    """Fairings where the duct's sides run into the cowl's flanks."""
    for side in (-1, 1):
        # walk the duct's middle line forward from its side until it is inside the cowl
        phi = 0.0
        while phi > -math.radians(70):
            q = fan_point(22.8, (math.pi - phi) if side < 0 else phi, 0.0)
            if inside_cowl(q):
                break
            phi -= math.radians(1.0)
        j = fan_point(22.8, (math.pi - phi) if side < 0 else phi, 0.0)
        tangent = (fan_point(22.8, (math.pi - phi + 0.01) if side < 0 else phi - 0.01, 0.0) - j).normalized()
        radial = (j - FAN_C - FA * (j - FAN_C).dot(FA)).normalized()
        boot = k.ellipsoid("duct_boot_%s" % ("l" if side < 0 else "r"), (0, 0, 0), (2.4, 3.6, 5.6), m["cowl"], 14, 8)
        mat_ = Matrix(((radial.x, tangent.x, FA.x, j.x), (radial.y, tangent.y, FA.y, j.y),
                       (radial.z, tangent.z, FA.z, j.z), (0, 0, 0, 1)))
        boot.data.transform(mat_)
        k.smooth(boot, 60)


def inside_cowl(p):
    """Whether p is inside the cowl's shell (or the envelope)."""
    r = radius(p.y)
    if r <= 0:
        return False
    x, z = p.x, p.z - ZC
    sq = SQ_TOP if z >= 0 else SQ_BOT
    rr = r + COWL_OFF
    return (x / rr) ** 2 + (z / (sq * r + COWL_OFF)) ** 2 < 1.0


# --- On its back: the brackets, the gate, the sensor pod ----------------------------------------------------------

def top_point(x, y, lift=0.0, pillows=True):
    """The envelope's top as built at (x, y) (or without the net's pillows), lifted along its normal: point and
    normal."""
    p, n = envelope_point(y, [psi_at(x, y)], lift=lift + (0.0 if pillows else NET_PILLOW * 0.7),
                          with_pillow=pillows)
    return Vector(p[0]), Vector(n[0])


def bar_on(name, a, b, half_width, top, bottom, mat, on_cowl=False, step=1.2, power=3.0):
    """A red bar along the straight line a-b (x, y) standing on the envelope (or the cowl)."""
    length = math.dist(a, b)
    count = max(2, int(math.ceil(length / step)))
    path, ups = [], []
    for i in range(count + 1):
        x = a[0] + (b[0] - a[0]) * i / count
        y = a[1] + (b[1] - a[1]) * i / count
        if on_cowl and y > cowl_edge(x) - 0.2:
            p, n = cowl_point(y, psi_at(x, y), lift=0.7)
        else:
            p, n = top_point(x, y, lift=0.75, pillows=False)
        path.append(p)
        ups.append(n)
    obj = mk.bar(name, path, ups, half_width, top, bottom, mat, segments=10, power=power)
    return k.smooth(obj, 50)


def frames(m):
    red, dark_red = m["red"], m["red_dark"]
    for side, tag in ((-1, "l"), (1, "r")):
        bar_on("bracket_%s" % tag, (side * 10.2, 26.7), (side * 10.2, 33.6), 1.05, 1.5, 1.4, red, on_cowl=True)
        bar_on("bracket_prong_%s" % tag, (side * 10.2, 31.0), (side * 5.8, 31.0), 1.2, 1.25, 1.4, red, on_cowl=True)
    bar_on("gate_bar", (-7.6, 23.0), (7.6, 23.0), 1.75, 1.6, 0.9, red)
    bar_on("gate_stem", (0.0, 23.5), (0.0, 27.8), 1.5, 1.35, 0.9, red, on_cowl=True)
    for side in (-1, 1):
        tag = "l" if side < 0 else "r"
        bar_on("gate_leg_in_%s" % tag, (side * 3.6, 22.6), (side * 3.6, 9.0), 1.2, 1.25, 0.9, red)
        bar_on("gate_leg_out_%s" % tag, (side * 8.4, 22.6), (side * 8.4, 11.6), 1.15, 1.2, 0.9, red)
        bar_on("gate_foot_%s" % tag, (side * 5.6, 10.9), (side * 10.5, 10.9), 1.15, 0.95, 0.9, dark_red)
    # The sensor pod on the crown with its dark visor, on a darker collar.
    base = top_point(0.0, 0.2)[0].z
    mk.dome("pod", (0.0, 0.0), (2.9, 6.0, 2.9), base - 0.5, red, segments=28, steps=9, power=2.3)
    mk.dome("pod_collar", (0.0, 0.0), (3.6, 6.8, 1.25), base - 0.6, dark_red, segments=28, steps=5, power=2.6)
    visor = k.ellipsoid("pod_visor", (0.0, -1.9, base + 1.95), (1.2, 1.6, 0.85), m["glass"], 16, 8)
    k.smooth(visor, 60)


# --- The gun pods ----------------------------------------------------------------------------------------------------
GUN_X, GUN_Z = -42.7, 12.6      # the left pod's axis
BARREL_X, BARREL_Z = -45.0, 11.7


def gun(m):
    """The left gun pod (the right one is its mirror image)."""
    parts = []
    lathe = lambda name, prof, mat, x, z, seg=28: parts.append(k.smooth(k.lathe(name, prof, mat, segments=seg,
                                                                                 axis_x=x, axis_z=z), 50))
    lathe("gun_body", [(-17.1, 0.0), (-16.9, 2.4), (-16.3, 3.7), (-15.3, 4.2), (6.0, 4.2), (7.0, 3.8), (7.8, 2.6),
                       (8.15, 0.0)], m["steel"], GUN_X, GUN_Z)
    lathe("gun_band", [(-7.7, 4.05), (-7.5, 4.6), (-5.0, 4.6), (-4.8, 4.05)], m["red"], GUN_X, GUN_Z)
    lathe("gun_band2", [(-15.8, 4.05), (-15.6, 4.45), (-14.2, 4.45), (-14.0, 4.05)], m["red_dark"], GUN_X, GUN_Z)
    lathe("gun_band3", [(3.3, 4.05), (3.5, 4.4), (4.7, 4.4), (4.9, 4.05)], m["red_dark"], GUN_X, GUN_Z)
    lathe("gun_barrel", [(-30.0, 0.0), (-30.0, 1.1), (-17.0, 1.1), (-16.0, 1.6), (-15.6, 0.0)], m["red"],
          BARREL_X, BARREL_Z, 16)
    lathe("gun_barrel_ring", [(-23.6, 1.0), (-23.4, 1.45), (-22.2, 1.45), (-22.0, 1.0)], m["red_dark"],
          BARREL_X, BARREL_Z, 16)
    lathe("gun_muzzle", [(-34.2, 1.5), (-35.3, 1.62), (-35.6, 2.05), (-35.45, 2.55), (-35.0, 2.78), (-30.4, 2.78),
                         (-29.6, 2.2), (-29.4, 0.0)], m["steel_light"], BARREL_X, BARREL_Z, 24)
    lathe("gun_bore", [(-34.3, 0.0), (-34.3, 1.52), (-35.25, 1.6)], m["dark"], BARREL_X, BARREL_Z, 24)
    lathe("gun_fire", [(-34.85, 0.0), (-34.75, 1.05), (-34.35, 1.45), (-34.2, 0.0)], m["fire"], BARREL_X, BARREL_Z, 16)
    lathe("gun_fire_ring", [(-35.66, 1.62), (-35.72, 1.85), (-35.66, 2.15), (-35.5, 2.0)], m["fire"],
          BARREL_X, BARREL_Z, 24)
    # The red pipe along the pod's top and the one down its inner side.
    parts.append(k.smooth(mk.tube("gun_pipe_top", [(-43.4, 8.6, GUN_Z + 3.9), (-43.4, 6.5, GUN_Z + 4.55),
                                                   (-43.4, -2.5, GUN_Z + 4.55), (-43.4, -4.4, GUN_Z + 4.2)],
                                  0.75, m["red"], segments=10), 50))
    side_pipe = [(GUN_X + 4.0, -0.6, GUN_Z + 1.4), (GUN_X + 4.6, -1.8, GUN_Z + 0.6), (GUN_X + 4.6, -9.5, GUN_Z + 0.6),
                 (GUN_X + 4.0, -10.6, GUN_Z + 1.2)]
    parts.append(k.smooth(mk.tube("gun_pipe_side", side_pipe, 0.6, m["red"], segments=10), 50))
    # The mount at the pod's upper end, its cap, the strut to the envelope's flank with a red rod under it.
    mount = mk.box("gun_mount", -47.3, -39.7, 8.4, 15.6, 9.2, 17.4, m["red"])
    mk.bevel(mount, 1.5, segments=3)
    parts.append(mount)
    mk.paint(mount, lambda c, n: m["red_light"] if n.z > 0.8 else None)
    cap = k.lathe("gun_cap", [(-41.4, 0.0), (-41.3, 1.5), (-40.9, 2.0), (-33.4, 2.0), (-33.0, 1.5), (-32.9, 0.0)],
                  m["steel"], segments=16)
    cap.data.transform(Matrix(((0, 1, 0, 0), (1, 0, 0, 17.3), (0, 0, -1, 15.9), (0, 0, 0, 1))))   # along X at (y, z)
    k.recalc_normals(cap)
    parts.append(k.smooth(cap, 50))
    strut = mk.box("gun_strut", -40.2, -30.4, 11.2, 15.6, 12.2, 15.4, m["steel"])
    mk.bevel(strut, 0.6, segments=2)
    parts.append(strut)
    rod = mk.box("gun_rod", -46.9, -33.0, 9.9, 11.1, 10.6, 12.0, m["red"])
    mk.bevel(rod, 0.35, segments=1)
    parts.append(rod)
    # The hose from the cowl's flank down to the cap.
    x0, y0 = -25.6, 24.6
    start = cowl_point(y0, psi_at(x0, y0))[0]
    hose = [(start.x, start.y, start.z - 0.4, 1.15), (-29.8, 24.0, start.z + 0.5, 1.15),
            (-33.6, 23.0, start.z - 0.6, 1.15), (-36.0, 21.2, 20.6, 1.15), (-36.6, 19.2, 18.5, 1.15),
            (-36.7, 17.8, 17.2, 1.15)]
    parts.append(k.smooth(mk.smooth_tube("gun_hose", hose, m["red"], segments=10, iterations=2), 60))
    collar = k.ellipsoid("gun_hose_collar", (start.x, start.y, start.z - 0.2), (1.9, 1.9, 0.9), m["red_dark"], 16, 6)
    parts.append(k.smooth(collar, 60))
    return parts


def mirror_x(objects):
    out = []
    for obj in objects:
        name = obj.name[:-2] + "_r" if obj.name.endswith("_l") else obj.name + "_r"
        copy = k.mirror_x(obj, name)
        copy.data.name = name
        out.append(copy)
    return out


# --- Build -------------------------------------------------------------------------------------------------------

def shift(objects):
    for obj in objects:
        mk.apply(obj)
        obj.data.transform(Matrix.Translation((AXIS_X, 0, 0)))


def build_whole(fan_phase=0):
    """The whole airship, its parts as objects (moved onto the picture's axis); returns them and the materials."""
    m = materials()
    envelope(m)
    net(m)
    cowl(m)
    duct(m)
    fan_hub(m)
    fan_blades(m, fan_phase)
    bridge(m)
    duct_boots(m)
    frames(m)
    mirror_x(gun(m))
    whole = mk.meshes()
    shift(whole)
    bpy.context.view_layer.update()
    return whole, m


def turn_fan(whole, m, phase):
    """The whole with its blades replaced by the fan turned to `phase`."""
    kept = []
    for obj in whole:
        if obj.name.startswith("blade_"):
            bpy.data.objects.remove(obj)
        else:
            kept.append(obj)
    blades = fan_blades(m, phase)
    shift(blades)
    bpy.context.view_layer.update()
    return kept + blades


def whole_mask(sheet):
    """The seventeen sprites' silhouettes placed as the levels place them: 96 x 140."""
    mask = [[False] * 96 for _ in range(140)]
    for _, sprite, box in PIECES:
        c0, r0 = cell_of(box)
        part = k.sprite_mask(sheet, sprite)
        for y in range(28):
            for x in range(24):
                if part[y][x]:
                    mask[r0 + y][c0 + x] = True
    return mask


def export_pieces(whole, m, pieces, out, sheet=None, preview=None, names=None):
    """Cuts the whole into the given pieces (name, sprite, box) and exports them; names: the models' names (by
    sprite) if not the pieces' own."""
    for name, sprite, box in pieces:
        model = names.get(sprite, name) if names else name
        parts = [p for p in (cut(src, box, m["dark"]) for src in whole) if p is not None]
        mk.transform(parts, Matrix.Translation((-(box[0] + box[1]) / 2, -(box[2] + box[3]) / 2, 0)))
        bpy.context.view_layer.update()
        for src in whole:
            src.hide_render = True
        if sheet:
            mk.compare("%s (I %d)" % (model, sprite), mk.coverage(parts, 24, 28), k.sprite_mask(sheet, sprite))
        mk.report(model, parts, os.path.join(out, model + ".glb"))
        if STATS:
            for obj in sorted(parts, key=lambda o: -mk.triangles([o]))[:10]:
                print("    %-20s %6d" % (obj.name, mk.triangles([obj])))
        if preview:
            mk.preview(preview + model, parts)
        for obj in parts:
            bpy.data.objects.remove(obj)
        for src in whole:
            src.hide_render = False


STATS = False


def build():
    global STATS
    k.reset()
    options = k.args()
    STATS = "stats" in options
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    whole, m = build_whole()
    print("whole airship: %d triangles, %d objects" % (mk.triangles(whole), len(whole)))
    for obj in sorted(whole, key=lambda o: -mk.triangles([o]))[:12]:
        print("   %-18s %6d" % (obj.name, mk.triangles([obj])))
    sheet = os.path.join(options["check"], "enemy_I.png") if "check" in options else None
    if sheet:
        mk.compare("whole (I 3 5 / 39-45 / 77-83 / 115-121 / 154-158)", mk.coverage(whole, 96, 140), whole_mask(sheet))
    bpy.context.scene.view_settings.view_transform = "Standard"
    if "preview" in options:
        mk.preview(options["preview"] + "zeppelin_whole", whole, size=(96, 140), scale=6, distance=4.0)
    if "whole" in options:
        mk.export(whole, options["whole"])
    pieces = [p for p in PIECES if not only or p[0] in only]
    export_pieces(whole, m, pieces, out, sheet, options.get("preview"))
    if options.get("frames", "1") != "0":
        names = {s: "zeppelin_%d" % f for s, f in FAN_FRAMES.items()}
        frames_ = [p for p in PIECES if p[1] in FAN_FRAMES and (not only or names[p[1]] in only)]
        if frames_:
            whole = turn_fan(whole, m, 1)
            if "whole" in options:
                mk.export(whole, options["whole"].replace(".glb", "_fan.glb"))
            export_pieces(whole, m, frames_, out, None, options.get("preview"), names)


if __name__ == "__main__":
    build()
