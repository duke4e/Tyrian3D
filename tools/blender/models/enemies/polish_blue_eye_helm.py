"""The blue armoured helm with the red eye (sheet C sprite 49, 2x2: 24 x 28 pixels; enemies 559 of DELI and New Deli
(sky layer) and HARVEST (top layer), 1587 and 1625 of VAULT and DEEP ICE (sky layer); its animation 49 51 53 53 53 51 51
51 49 only brightens the eye), polished (2026-10-21; it replaces wave3_x.py's blue_eye_helm(), a heightfield of the
sprite's plan with the eye, a crest tube and box ribs on it). models.cfg: model blue_eye_helm enemies/blue_eye_helm.glb;
sprite c 49 blue_eye_helm yaw=0 glow=10:0.3:119 (as before).

C 51 and 53 are C 49's pixels but for the eye's, five and eight shades brighter (ramp 7): the frames change only light,
so there are no frame models (the cfg's glow halo pulses nothing either; the eye is given the middle frame's colours).
No other sprite of any sheet is C 49 mirrored, turned or in other ramps.

As the sprite draws it (columns and rows of C 49): a thick blue hood curving over the upper left (its outer edge the
sprite's diagonal from column 11 of row 0 to column 0 of row 12 and down the left side; its inner lip from row 3 round
to column 8, lit along its crest, columns 5-7 on the left); inside it a dark face (ramp 3 shade 4) with the eye in its
middle (columns 9-15 of rows 10-16: a red lens, hottest a little above its middle) in a dark socket; an L-shaped
bracket stepping up from the face at its upper right (a bar across rows 4-6 from column 13, down columns 16-18 to row
14), a dark groove (column 19) and a tall plate on the right (columns 20-22 of rows 4-15, the notch above it empty);
under the plate a vent block (columns 15-22 of rows 15-18: a lit top, three dark slots between ribs) and a ledge under
the eye (columns 9-14 of row 17); across the bottom a base (rows 19-24) of two lit slats (rows 20 and 22-23) with a
dark vent and a light divider at its left end (columns 2-5), and under it a chin (rows 25-27) with teeth in its front
(columns 9-15 of row 27) and a lighter block at its right.

Built as a CAD modeller would: a core block (the face on its top) under everything; the hood lofted along its inner
lip, each section a steep inner wall up to the lip, a rounded crest near it and a long dome falling away to the outer
edge, sinking into the base at its foot; the bracket, the plate, the vent block (its slots cut by exact booleans), the
ledge, the base with its slats and the vent cut into its left end, the chin with its lip and teeth: prisms of their
plans with bevelled edges. The socket is a bowl cut into the core; in it a dark rim and the eye, a lens turned about an
axis tilted towards the game's camera, its colours cut along smooth contours (rim, ring, core: polish_orb_red's
band_split), glowing well under 1 (the cfg's glow halo adds a red light round it).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera (the helm's floor
z = 0; the game centres sky objects in height); origin at the sprite's centre (pixel 12, 14): column c's left edge is
x = c - 12, row r's top edge y = 14 - r.

Replaces wave3_x.py's blue_eye_helm(): remove it with its @x.model("blue_eye_helm", [(49, True)]) registration, its
section header and the blue_eye_helm bullet of the docstring (and `sh` from its kit import, which only it used); and
wave3_x_art.py's DOME (only blue_eye_helm() reads it) and DOME_HOT (read by nothing).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouette against
enemy_C.png's sprite 49), --preview <prefix>.
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_orb_red import band_split  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402

NAME, SPRITE = "blue_eye_helm", 49

# The sprite's outline (its black edge's outer side; the diagonal through the middles of its steps), anticlockwise.
OUTLINE = [(-10.0, -14.0), (9.0, -14.0), (9.0, -11.0), (12.0, -11.0), (12.0, 10.0), (8.0, 10.0), (8.0, 14.0),
           (-0.6, 14.0), (-2.0, 13.0), (-3.5, 12.0), (-4.5, 11.0), (-5.5, 10.0), (-6.5, 9.0), (-7.5, 8.0), (-8.5, 7.0),
           (-9.5, 6.0), (-10.1, 5.0), (-10.6, 4.0), (-11.1, 3.0), (-11.6, 2.0), (-12.0, 1.0), (-12.0, -12.0),
           (-10.0, -12.0)]
FACE_Z = 5.0                     # the core's top: the face
# The hood: its inner lip from the top right round to the left side (the sections are made square to it), the part of
# the outline it reaches out to, its heights (the lip's top, the crest, the outer edge), where the crest lies (share of
# the way from the lip to the outer edge), how far the inner wall stands inside the lip.
LIP = [(7.95, 11.0), (1.7, 11.0), (0.6, 10.7), (0.1, 9.8), (0.0, 8.2), (-0.4, 6.7), (-1.5, 5.6), (-2.9, 4.8),
       (-3.8, 3.6), (-4.1, 2.0), (-4.2, 0.0), (-4.2, -3.0), (-4.2, -6.2)]
HOOD_Z = (8.9, 11.0, 3.2)
CREST_U = 0.34
WALL_IN = 0.3
HOOD_FOOT = (-1.0, -6.2, 5.6)    # the hood sinks from this y on to that y, where its crest is this high (in the base)
# The bracket (an L: a bar across, a bar down), the plate, the vent block and its slots (x, half-width), the ledge.
BRACKET = [(1.0, 7.0), (4.0, 7.0), (4.0, -1.0), (7.0, -1.0), (7.0, 10.0), (1.0, 10.0)]
BRACKET_Z = 7.0
PLATE = (8.0, 11.95, -1.3, 9.85, 8.2)          # x0, x1, y0, y1, top
PLATE_GROOVE = 9.05                             # a fine groove down the plate
VENT = (3.0, 11.95, -5.05, -1.3, 6.5)
VENT_SLOTS = [(5.5, 0.48), (7.5, 0.48), (10.0, 0.95)]
VENT_SLOT_TOP = -2.0                            # the slots run from here down through the block's front
LEDGE = (-4.4, 3.4, -4.15, -2.75, 6.3)
# The base, its slats (x0, x1, y0, y1, top), the vent in its left end and its divider.
BASE = (-11.95, 11.95, -11.05, -4.9, 6.0)
SLATS = [(-3.3, 11.65, -7.05, -5.85, 6.65), (-5.3, 11.65, -10.1, -7.9, 6.65)]
BASE_VENT = (-10.25, -7.05, -10.75, -5.85, 4.55)
DIVIDER = (-6.95, -6.0, -10.6, -5.6, 6.45)
# The chin, its lip along the front with the teeth cut into it (slot x, half-width), the lighter block at its right.
CHIN = (-9.95, 8.95, -13.95, -11.0, 3.5)
CHIN_LIP = (-9.8, 4.1, -13.95, -12.95, 4.4)
TEETH_SLOTS = [(-2.5, 0.42), (-0.5, 0.42), (1.5, 0.42), (3.5, 0.42)]
CHIN_BLOCK = (4.0, 8.95, -13.95, -11.0, 4.7)
# The socket and the eye: its centre, the socket's radius, the eye's radius and how far it bulges, its axis (tilted
# towards the game's camera), where its core is (from the axis towards its upper left), the bands' cosines.
EYE_C = Vector((0.5, 0.55, FACE_Z - 0.1))
SOCKET_R = 3.95
EYE_R, EYE_BULGE = 3.2, 2.5
EYE_AXIS = Vector((0.0, -0.3, 0.95)).normalized()
HOT_DIR = Vector((-0.18, 0.12, 1.0)).normalized()
EYE_BANDS = (0.72, 0.93)


def materials():
    glow = k.level_palette()

    def mat(name, index, metallic=0.5, roughness=0.32):
        return k.material(name, palette=index, metallic=metallic, roughness=roughness)

    def lit(name, index, strength, roughness=0.15):
        return k.material(name, palette=index, metallic=0.0, roughness=roughness, emission=glow[index],
                          emission_strength=strength)
    m = {
        "socket": mat("helm_socket", 0x31, 0.3, 0.5),
        "rim": mat("helm_rim", 0x33, 0.45, 0.35),
        "face": mat("helm_face", 0x35, 0.45, 0.38),
        "dark": mat("helm_dark", 0x34, 0.45, 0.4),
        "side": mat("helm_side", 0x36, 0.5, 0.35),
        "body": mat("helm_body", 0x37, 0.5, 0.32),
        "hood": mat("helm_hood", 0x38, 0.55, 0.3),
        "hood_mid": mat("helm_hood_mid", 0x39, 0.55, 0.28),
        "lit": mat("helm_lit", 0x3a, 0.55, 0.28),
        "crest": mat("helm_crest", 0x3b, 0.55, 0.26),
        "glint": mat("helm_glint", 0x3c, 0.55, 0.24),
        "eye_rim": lit("helm_eye_rim", 0x74, 0.3),
        "eye_ring": lit("helm_eye_ring", 0x77, 0.42),
        "eye_core": lit("helm_eye_core", 0x7b, 0.55, 0.1),
    }
    m["slot"] = m["socket"]
    return m


# --- Helpers ----------------------------------------------------------------------------------------------------

def inset(poly, d):
    """An anticlockwise polygon moved in by d (mitred corners)."""
    out = []
    n = len(poly)
    for i in range(n):
        p0, p1, p2 = Vector(poly[i - 1]), Vector(poly[i]), Vector(poly[(i + 1) % n])
        e0, e1 = (p1 - p0).normalized(), (p2 - p1).normalized()
        n0, n1 = Vector((-e0.y, e0.x)), Vector((-e1.y, e1.x))
        bis = n0 + n1
        if bis.length < 1e-6:
            bis = n0
        bis.normalize()
        out.append(tuple(p1 + bis * (d / max(0.3, bis.dot(n0)))))
    return out


def rect(x0, x1, y0, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def block(name, x0, x1, y0, y1, top, mat, bevel, z0=0.0, angle=30.0):
    obj = mk.prism(name, rect(x0, x1, y0, y1), z0, top, mat)
    mk.bevel(obj, bevel, 2, angle)
    mk.shade(obj, 35)
    return obj


def ray_hit(origin, direction, poly):
    """The nearest point where the ray from origin along direction leaves the polygon (2D)."""
    best = None
    o, d = Vector(origin), Vector(direction)
    n = len(poly)
    for i in range(n):
        a, b = Vector(poly[i]), Vector(poly[(i + 1) % n])
        e = b - a
        den = d.x * e.y - d.y * e.x
        if abs(den) < 1e-9:
            continue
        w = a - o
        t = (w.x * e.y - w.y * e.x) / den
        s = (w.x * d.y - w.y * d.x) / den
        if t > 1e-4 and -1e-6 <= s <= 1 + 1e-6 and (best is None or t < best):
            best = t
    return o + d * best if best is not None else None


def resample(points, step):
    """A polyline resampled about step apart (its corners kept), rounded a little (Chaikin)."""
    pts = mk.chaikin(points, 2, closed=False)
    out = [Vector(pts[0])]
    for p, q in zip(pts, pts[1:]):
        p, q = Vector(p), Vector(q)
        n = max(1, round((q - p).length / step))
        out += [p.lerp(q, i / n) for i in range(1, n + 1)]
    return out


# --- The parts ----------------------------------------------------------------------------------------------------

def core(m):
    """The core block under everything: the sprite's plan a little in, the face on its top; the socket's bowl cut
    into it."""
    body = mk.prism("core", inset(OUTLINE, 0.22), 0.0, FACE_Z, m["face"])
    mk.bevel(body, 0.35, 2, 30)
    bowl = k.ellipsoid("bowl", (EYE_C.x, EYE_C.y, FACE_Z + 0.9), (SOCKET_R + 0.12,) * 3, m["socket"], 32, 16)
    mk.boolean(body, bowl, "DIFFERENCE")
    mk.cleanup(body)
    mk.shade(body, 35)
    mk.paint(body, lambda c, n: m["socket"] if (Vector(c) - EYE_C).length < SOCKET_R + 0.6 and c.z < FACE_Z - 0.05
             else m["side"] if n.z < 0.4 else None)
    return body


def hood_profile(u, lip, crest, side):
    """The hood's height at u (0 the lip, 1 the outer edge): rising from the lip to the crest, then a dome falling to
    the outer edge (its tangent upright there)."""
    if u <= CREST_U:
        return lip + (crest - lip) * mk.smoothstep(0.0, CREST_U, u)
    t = (u - CREST_U) / (1 - CREST_U)
    p = 2.3
    return side + (crest - side) * max(0.0, 1 - t ** p) ** (1 / p)


def hood(m):
    """The hood: lofted along its inner lip, each section square to it from the inner wall's foot (in the core) up to
    the lip, over the crest and down its dome to the outer edge and down that to the floor; sinking into the base at
    its foot."""
    lip = resample(LIP, 0.55)
    us = [i / 18 for i in range(19)]
    rings, owners = [], []
    for i, p in enumerate(lip):
        a, b = lip[max(i - 1, 0)], lip[min(i + 1, len(lip) - 1)]
        t = (b - a).normalized()
        out = Vector((t.y, -t.x))      # the outward normal (the lip runs clockwise round the face)
        far = ray_hit(p, out, OUTLINE)
        length = (far - p).length - 0.05 if far is not None else 3.0
        f = 1.0 - mk.smoothstep(HOOD_FOOT[1], HOOD_FOOT[0], p.y)
        z_lip, z_crest, z_side = HOOD_Z
        z_lip += (HOOD_FOOT[2] - 1.0 - z_lip) * f
        z_crest += (HOOD_FOOT[2] - z_crest) * f
        z_side += (min(z_side, HOOD_FOOT[2] - 1.5) - z_side) * f
        section = [(-WALL_IN, 0.0), (-WALL_IN, FACE_Z - 0.4), (-WALL_IN * 0.9, z_lip - 0.9),
                   (-WALL_IN * 0.55, z_lip - 0.3)]
        section += [(u * length, hood_profile(u, z_lip, z_crest, z_side)) for u in us]
        section += [(length, z_side * 0.5), (length, 0.0)]
        rings.append([Vector((p.x + out.x * s, p.y + out.y * s, z)) for s, z in section])
        owners.append([("wall" if j < 4 else "top", us[j - 4] if 4 <= j < 4 + len(us) else None) for j in
                       range(len(section))])
    body = k.loft("hood", rings, m["hood"])
    k.smooth(body, 40)
    # Paint by where a face lies across the hood (its share of the way from the lip), and how it faces.
    ring_n = len(rings[0])

    def u_of(c):
        best = None
        for i, p in enumerate(lip):
            d = (Vector((c.x, c.y)) - p).length
            if best is None or d < best[0]:
                best = (d, i)
        p = lip[best[1]]
        far = rings[best[1]][ring_n - 1]
        length = (Vector((far.x, far.y)) - p).length
        return best[0] / max(length, 0.1) if (Vector((c.x, c.y)) - p).dot(Vector((far.x, far.y)) - p) > 0 else -0.1

    def pick(c, n):
        u = u_of(c)
        if u < 0.02 and n.z < 0.6:
            return m["dark"]
        if n.z < 0.15:
            return m["side"]
        if u < 0.07:
            return m["glint"]
        if u < 0.2:
            return m["hood_mid"]
        if u < 0.5:
            return m["crest"]
        if u < 0.74:
            return m["hood_mid"]
        return m["hood"]
    mk.paint(body, pick)
    return body


def bracket(m):
    """The L-shaped bracket stepping up from the face at its upper right, its edges bevelled, lit along the face."""
    obj = mk.prism("bracket", BRACKET, 0.0, BRACKET_Z, m["body"])
    mk.bevel(obj, 0.45, 2, 30)
    mk.shade(obj, 35)
    mk.paint(obj, lambda c, n: m["lit"] if 0.2 < n.z < 0.95 and (n.x < -0.25 or n.y < -0.25) else
             m["side"] if n.z <= 0.2 else None)
    return obj


def plate(m):
    """The tall plate on the right, a fine groove down it; its top edge lit."""
    x0, x1, y0, y1, top = PLATE
    obj = block("plate", x0, x1, y0, y1, top, m["body"], 0.55)
    groove = mk.box("plate_groove", PLATE_GROOVE - 0.16, PLATE_GROOVE + 0.16, y0 + 0.7, y1 - 0.7, top - 0.3, top + 2.0,
                    m["dark"])
    mk.boolean(obj, groove, "DIFFERENCE")
    mk.cleanup(obj)
    mk.shade(obj, 35)
    mk.paint(obj, lambda c, n: m["lit"] if 0.25 < n.z < 0.95 and n.y > 0.3 else m["dark"] if c.z < top - 0.2 and
             abs(c.x - PLATE_GROOVE) < 0.2 and n.z > 0.5 else m["side"] if n.z < 0.25 else None)
    return obj


def vent(m):
    """The vent block under the plate: its top lit, three slots cut down through its front between ribs."""
    x0, x1, y0, y1, top = VENT
    obj = block("vent", x0, x1, y0, y1, top, m["body"], 0.4)
    for i, (x, hw) in enumerate(VENT_SLOTS):
        cutter = mk.box(f"vent_slot{i}", x - hw, x + hw, y0 - 1.0, VENT_SLOT_TOP, FACE_Z - 0.6, top + 2.0, m["slot"])
        mk.boolean(obj, cutter, "DIFFERENCE")
    mk.cleanup(obj)
    mk.shade(obj, 35)

    def pick(c, n):
        if any(abs(c.x - x) < hw + 0.02 for x, hw in VENT_SLOTS) and c.y < VENT_SLOT_TOP + 0.05 and c.z < top - 0.1:
            return m["slot"]
        if n.z > 0.6 and c.y > VENT_SLOT_TOP:
            return m["lit"]
        return m["side"] if n.z < 0.25 else None
    mk.paint(obj, pick)
    return obj


def ledge(m):
    x0, x1, y0, y1, top = LEDGE
    obj = block("ledge", x0, x1, y0, y1, top, m["lit"], 0.45)
    mk.paint(obj, lambda c, n: m["side"] if n.z < 0.3 else None)
    return obj


def base(m):
    """The base across the bottom: a block with two lit slats along it, the dark lines between them its top; the vent
    cut into its left end with the divider beside it."""
    x0, x1, y0, y1, top = BASE
    obj = block("base", x0, x1, y0, y1, top, m["dark"], 0.5)
    vx0, vx1, vy0, vy1, vz = BASE_VENT
    cutter = mk.prism("base_vent_cut", mk.chaikin(rect(vx0, vx1, vy0, vy1), 1), vz, top + 2.0, m["slot"])
    mk.boolean(obj, cutter, "DIFFERENCE")
    mk.cleanup(obj)
    mk.shade(obj, 35)
    mk.paint(obj, lambda c, n: m["slot"] if vx0 - 0.05 < c.x < vx1 + 0.05 and vy0 - 0.05 < c.y < vy1 + 0.05 and
             c.z < top - 0.1 else m["side"] if n.z < 0.3 and n.y < -0.5 else m["body"] if n.z < 0.3 else None)
    for i, (sx0, sx1, sy0, sy1, stop) in enumerate(SLATS):
        slat = block(f"slat{i}", sx0, sx1, sy0, sy1, stop, m["hood_mid"], 0.42)
        mk.paint(slat, lambda c, n: m["lit"] if n.z > 0.8 else m["body"] if n.z < 0.3 else None)
    dx0, dx1, dy0, dy1, dz = DIVIDER
    divider = block("divider", dx0, dx1, dy0, dy1, dz, m["lit"], 0.3)
    mk.paint(divider, lambda c, n: m["body"] if n.z < 0.3 else None)
    return obj


def chin(m):
    """The chin under the base: a low block, its lip along the front with the teeth cut into it, the lighter block at
    its right."""
    x0, x1, y0, y1, top = CHIN
    obj = block("chin", x0, x1, y0, y1, top, m["socket"], 0.35)
    mk.paint(obj, lambda c, n: m["dark"] if n.z < 0.3 else None)
    lx0, lx1, ly0, ly1, ltop = CHIN_LIP
    lip = block("chin_lip", lx0, lx1, ly0, ly1, ltop, m["side"], 0.35)
    for i, (x, hw) in enumerate(TEETH_SLOTS):
        cutter = mk.box(f"tooth_slot{i}", x - hw, x + hw, ly0 - 1.0, ly1 + 1.0, top - 0.9, ltop + 2.0, m["slot"])
        mk.boolean(lip, cutter, "DIFFERENCE")
    mk.cleanup(lip)
    mk.shade(lip, 35)
    mk.paint(lip, lambda c, n: m["slot"] if any(abs(c.x - x) < hw + 0.02 for x, hw in TEETH_SLOTS) and
             c.z < ltop - 0.1 else m["hood_mid"] if n.z > 0.75 and -3.2 < c.x < 4.2 else
             m["body"] if n.z > 0.75 else None)
    bx0, bx1, by0, by1, btop = CHIN_BLOCK
    right = block("chin_block", bx0, bx1, by0, by1, btop, m["body"], 0.4)
    mk.paint(right, lambda c, n: m["hood"] if n.z > 0.8 else m["side"] if n.z < 0.3 else None)
    return obj


def eye(m):
    """The socket's dark rim and the eye: a lens turned about its axis, its colours cut along smooth contours (a core
    at its upper left, a ring round it, the rim)."""
    rim_pts = []
    for i in range(48):
        a = 2 * math.pi * i / 48
        rim_pts.append(Vector((EYE_C.x + SOCKET_R * math.cos(a), EYE_C.y + SOCKET_R * math.sin(a), FACE_Z + 0.02)))
    rings = []
    for j in range(10):
        b = 2 * math.pi * j / 10
        rings.append([p + (Vector((p.x - EYE_C.x, p.y - EYE_C.y, 0)).normalized() * math.cos(b) * 0.42 +
                           Vector((0, 0, 1)) * math.sin(b) * 0.3) for p in rim_pts])
    # A torus: rings round the tube (each a ring of the rim's points), closed both ways.
    verts = [v for ring in rings for v in ring]
    n = len(rim_pts)
    faces = []
    for j in range(10):
        for i in range(n):
            a, b = j * n + i, j * n + (i + 1) % n
            c, d = ((j + 1) % 10) * n + (i + 1) % n, ((j + 1) % 10) * n + i
            faces.append((a, b, c, d))
    torus = k.mesh_object("socket_rim", verts, faces, m["rim"])
    k.recalc_normals(torus)
    k.smooth(torus, 60)
    seg, steps = 40, 12
    profile = []
    for i in range(steps + 1):
        t = (math.pi / 2) * i / steps
        profile.append((max(0.01, EYE_R * math.cos(t)), EYE_BULGE * math.sin(t)))
    lens = mk.lathe("eye", [(r, z - 0.4) for r, z in profile], (0.0, 0.0), m["eye_rim"], seg)
    turn = EYE_AXIS.to_track_quat("Z", "Y").to_matrix().to_4x4()
    lens.data.transform(Matrix.Translation(EYE_C) @ turn)
    values = [(v.co - EYE_C).normalized().dot(HOT_DIR) for v in lens.data.vertices]
    band_split(lens, values, [(-9.0, m["eye_rim"]), (EYE_BANDS[0], m["eye_ring"]), (EYE_BANDS[1], m["eye_core"])])
    k.smooth(lens, 70)
    return lens


def build_parts(m):
    core(m)
    hood(m)
    bracket(m)
    plate(m)
    vent(m)
    ledge(m)
    base(m)
    chin(m)
    eye(m)
    parts = mk.meshes()
    for obj in parts:
        mk.apply(obj)
    bpy.context.view_layer.update()
    return parts


def build():
    options = k.args()
    out = mk.outdir(options)
    k.reset()
    m = materials()
    parts = build_parts(m)
    triangulate(parts)
    bpy.context.view_layer.update()
    if "check" in options:
        sheet = os.path.join(options["check"], "enemy_C.png")
        mk.compare("%s (C %d)" % (NAME, SPRITE), mk.coverage(parts, 24, 28), k.sprite_mask(sheet, SPRITE))
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    mk.report(NAME, parts, os.path.join(out, NAME + ".glb"))
    if "preview" in options:
        mk.preview(options["preview"] + NAME, parts)


if __name__ == "__main__":
    build()
