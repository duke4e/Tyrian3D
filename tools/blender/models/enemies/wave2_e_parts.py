"""The batch E models that are pieces of larger objects (wave2_e.py): each object is built whole from its
pixel art (wave2_e_art.py) and cut along its sprites' edges into the pieces the game draws, each
moved to its sprite's centre (models.cfg: origin, so that they meet again). The levels place the
pieces as the sheets arrange them (checked in the level files' enemy events).

- EYESPY's robot (sheet 9): two armoured halves, which the level places far apart, each a shoulder
  housing under a roll, with a dark hollow where the arm joins, and an arm hooked down to a gun with
  a blue lens; sprites 1, 3 and 39 (left), 5, 7 and 45 (right).
- DREAD-NOT's anchors (sheet 9): two hooded bodies standing on the ground, each with a gun pointing
  at the other and four struts reaching out to the ground; each drawn from four overlapping sprites
  (235, 236, 254, 274 on the left, 238, 239, 258, 276 on the right).
- NOSE DRIP's nose (sheet 5): the bridge (154) above the tip with its nostrils (191, 193).

Volumes come from the sprites' outlines, inflated (wave1_d_shapes.py), and from turned and lofted
parts placed over them in the art's pixels.
"""
import math

from mathutils import Matrix, Vector

import tyrkit as k
import wave1_d_shapes as sh
import wave2_e_art as art


# --- Helpers ---------------------------------------------------------------------------------------

def select(rows, keep):
    """The art with only the pixels where keep(column, row, char) is true."""
    return ["".join(ch if ch != "." and keep(c, r, ch) else "." for c, ch in enumerate(line))
            for r, line in enumerate(rows)]


def paint(obj, mats, pick):
    """Gives each face the material mats[pick(x, y, z)] (x, y, z: the face's centre)."""
    for m in mats:
        if m.name not in obj.data.materials:
            obj.data.materials.append(m)
    names = [m.name for m in obj.data.materials]
    for poly in obj.data.polygons:
        c = poly.center
        poly.material_index = names.index(mats[pick(c.x, c.y, c.z)].name)
    return obj


def smoothmin(a, b, k_=1.0):
    h = max(k_ - abs(a - b), 0.0) / k_
    return min(a, b) - h * h * k_ * 0.25


def smoothmax(a, b, k_=1.0):
    return -smoothmin(-a, -b, k_)


def cut_pieces(build, pieces, name, origin):
    """Builds the whole object and keeps the piece `name` of `pieces` ({name: (left, top)} in the
    art's pixels; 24 x 28 pixels each), moved so that its sprite's centre is the origin."""
    objects = build()
    left, top = pieces[name]
    ox, oy = origin
    x0, x1 = left - ox, left + 24 - ox
    y0, y1 = oy - top - 28, oy - top
    kept = sh.cut_box(objects, x0, x1, y0, y1)
    sh.move(kept, -(x0 + 12), -(y0 + 14))
    for obj in kept:
        k.smooth(obj, 50)
    return kept


# --- EYESPY's robot (sheet 9, sprites 1, 3, 5, 7, 39, 45) --------------------------------------------

ROBOT_ORIGIN = (48, 28)
ROBOT_PIECES = {
    "eyespy_l_shoulder": (0, 0),    # sprite 1
    "eyespy_l_dome": (24, 0),       # sprite 3
    "eyespy_r_dome": (48, 0),       # sprite 5
    "eyespy_r_shoulder": (72, 0),   # sprite 7
    "eyespy_l_arm": (0, 28),        # sprite 39
    "eyespy_r_arm": (72, 28),       # sprite 45
}


def robot_materials():
    return {
        "hull": k.material("eyespy_hull", palette=8, metallic=0.4, roughness=0.35),
        "dark": k.material("eyespy_dark", palette=3, metallic=0.5, roughness=0.5),
        "steel": k.material("eyespy_steel", palette=10, metallic=0.6, roughness=0.25),
        "lens": k.material("eyespy_lens", palette=153, metallic=0.1, roughness=0.1, emission=(40, 90, 255),
                           emission_strength=0.8),
        "armour": k.material("eyespy_armour", palette=5, metallic=0.4, roughness=0.4),
        "fore": k.material("eyespy_forearm", palette=6, metallic=0.45, roughness=0.32),
    }


def tube(name, points, radii, mat, squash=1.0, segments=20, round_ends=True):
    """A round part along a path of (x, y, z) points, its radius varying (radii: one per point),
    its cross-sections squashed in height; the ends rounded (or flat)."""
    pts = [Vector(p) for p in points]
    frames = []
    for i, p in enumerate(pts):
        a, b = pts[max(i - 1, 0)], pts[min(i + 1, len(pts) - 1)]
        tangent = (b - a).normalized()
        side = tangent.cross(Vector((0, 0, 1)))
        if side.length < 1e-6:
            side = Vector((1, 0, 0))
        side.normalize()
        frames.append((tangent, side, side.cross(tangent).normalized()))

    def ring_at(c, frame, r):
        _t, side, up = frame
        return [c + side * math.cos(2 * math.pi * j / segments) * r + up * math.sin(2 * math.pi * j / segments) * r *
                squash for j in range(segments)]

    rings = [ring_at(p, f, r) for p, f, r in zip(pts, frames, radii)]
    if round_ends:
        for a in (0.5, 0.82):
            s_, c_ = math.sin(a * math.pi / 2), math.cos(a * math.pi / 2)
            rings.insert(0, ring_at(pts[0] - frames[0][0] * radii[0] * s_ * 0.8, frames[0], radii[0] * c_))
            rings.append(ring_at(pts[-1] + frames[-1][0] * radii[-1] * s_ * 0.8, frames[-1], radii[-1] * c_))
    reach = 0.8 if round_ends else 0.0
    obj = k.loft(name, rings, mat, start_point=pts[0] - frames[0][0] * radii[0] * reach,
                 end_point=pts[-1] + frames[-1][0] * radii[-1] * reach)
    return k.smooth(obj, 60)


def plate(name, outline, height, mat, base=0.0, radius=1.2, crown=0.0, spacing=0.4, z_fn=None):
    """A part over an outline [(x, y)] standing on `base`: a flat top `height` above it, its edges
    rounded over `radius` (an inflated pillow)."""
    obj = sh.inflate(name, [outline], mat, sh.pillow_profile(height, radius, crown), bottom=0.0, base=base,
                     rim=0.05, spacing=spacing, z_fn=z_fn)
    return k.smooth(obj, 50)


def robot_half(side, mats):
    """One half of the robot (side -1: the left, art columns 0-47; 1: the right, mirrored). Parts, in
    the left half's pixels: the roll on top of the shoulder (columns 24-46, rows 2-12), the shoulder's
    housing below it (columns 30-46, rows 11-28) with a dark hollow at its left where the arm joins,
    the upper arm (a broad plate down to the left), the elbow, the forearm curving down to the gun
    and its blue lens (columns 3-9, rows 46-51). Under them all, a low armour plate over the half's
    whole outline (its own pixels: the halves differ by a pixel here and there)."""
    rows = sh.art(art.ROBOT)
    o = ROBOT_ORIGIN
    mine = select(rows, lambda c, r, ch: (c < 48) == (side < 0))
    objs = []

    def p(c, r):
        # A point in the left half's pixels, as a model point of this half.
        x, y = c - o[0], o[1] - r
        return (x if side < 0 else 1.0 - x, y)  # the right half is the mirror image a pixel to the right

    def poly(points):
        pts = [p(c, r) for c, r in points]
        return pts if side < 0 else pts[::-1]

    def p3(c, r, z):
        return (*p(c, r), z)

    # The armour under everything, over the whole outline.
    base = sh.outlines(mine, "0123456789abcdefB", o, smooth=2, epsilon=0.5)
    hollow_c, hollow_r = p(29.0, 20.5), (4.2, 6.5)

    def base_z(x, y, z):
        q = ((x - hollow_c[0]) / hollow_r[0]) ** 2 + ((y - hollow_c[1]) / hollow_r[1]) ** 2
        return z - 1.6 * math.exp(-q * 2.0) * min(1.0, z / 2.0)

    armour = sh.inflate(f"armour{side}", base, mats["armour"], sh.pillow_profile(3.4, 1.6), bottom=0.35,
                        spacing=0.45, z_fn=base_z)
    objs.append(k.smooth(armour, 50))
    floor = sh.surface_z(armour, hollow_c[0], hollow_c[1], 2.0)
    objs.append(k.smooth(k.ellipsoid(f"armour_hollow{side}", (hollow_c[0], hollow_c[1], floor + 0.2),
                                     (hollow_r[0] * 0.7, hollow_r[1] * 0.7, 0.8), mats["dark"], 24, 12), 60))
    # The shoulder's housing: a block narrowing at its bottom, its top sloping down to the front.
    housing = poly([(31.0, 11.5), (44.6, 11.5), (44.8, 22.5), (41.6, 27.6), (32.4, 27.6), (30.0, 24.0),
                    (30.4, 15.0)])
    # Its hollow at the left, where the arm joins (columns 27-35, rows 13-27), dark inside, and its
    # lower end bending down (rows 22-27).
    hc, hr = p(31.6, 20.0), (3.6, 7.6)
    low_y = o[1] - 21.5

    def housing_depth(x, y):
        q = ((x - hc[0]) / hr[0]) ** 2 + ((y - hc[1]) / hr[1]) ** 2
        return 3.2 * math.exp(-q * q * 1.5) + 2.2 * sh.smoothstep(0.0, 4.0, low_y - y)

    obj = plate(f"housing{side}", housing, 4.4, mats["hull"], base=2.0, radius=1.6,
                z_fn=lambda x, y, z: z - housing_depth(x, y) * min(1.0, z / 3.0)
                - 0.8 * max(0.0, min(1.0, (o[1] - 13.0 - y) / 8.0)))
    objs.append(obj)
    # The hollow's dark inside: a dark lens in the pit, whose rim the pit's walls cut smoothly.
    floor = sh.surface_z(obj, hc[0], hc[1], 3.0)
    inside = k.ellipsoid(f"hollow{side}", (hc[0], hc[1], floor + 0.4), (hr[0] * 0.78, hr[1] * 0.8, 1.2), mats["dark"],
                         32, 16)
    objs.append(k.smooth(inside, 60))
    # The roll on top: thicker at its outer (right) end.
    roll = [p3(25.6, 8.2, 7.2), p3(30.0, 7.2, 7.8), p3(35.0, 7.0, 8.2), p3(39.5, 7.0, 8.3), p3(42.3, 7.2, 8.2)]
    objs.append(tube(f"roll{side}", roll, [3.6, 4.3, 4.6, 4.6, 4.3], mats["hull"], squash=0.9))
    # Two bands round the roll's outer end (the sprite's bright spots).
    for i, (c, r, z, rad) in enumerate(((36.6, 7.0, 8.25, 4.45), (40.4, 7.05, 8.3, 4.45))):
        band = k.lathe(f"band{side}{i}", [(-0.75, rad - 0.3), (-0.6, rad + 0.35), (0.6, rad + 0.35),
                                           (0.75, rad - 0.3)], mats["steel"], 28, squash=0.9)
        band.data.transform(Matrix.Translation((*p(c, r), z)) @ Matrix.Rotation(math.radians(-90 if side < 0 else 90),
                                                                                 4, "Z"))
        objs.append(k.smooth(band, 50))
    # The upper arm: a broad plate from the shoulder down to the elbow, with a raised rib along its
    # lit edge.
    upper = poly([(9.0, 22.5), (14.5, 14.0), (20.0, 8.6), (27.0, 8.6), (30.5, 12.0), (29.5, 17.0),
                  (25.0, 25.5), (22.5, 30.0), (14.0, 30.5), (9.0, 28.5)])
    objs.append(plate(f"upper_arm{side}", upper, 3.6, mats["hull"], base=2.0, radius=1.8, crown=0.0,
                      z_fn=lambda x, y, z: z + 0.9 * max(0.0, min(1.0, (y - (o[1] - 30.0)) / 20.0))))
    rib = [p3(22.0, 10.5, 5.6), p3(22.6, 16.0, 5.7), p3(22.0, 22.0, 5.6), p3(20.6, 27.5, 5.4)]
    objs.append(tube(f"rib{side}", rib, [1.0, 1.15, 1.15, 1.0], mats["steel"], squash=0.8))
    # The upper arm's lower end: a round post going down to the elbow (columns 15-21, rows 28-39).
    post = [p3(18.4, 27.5, 4.8), p3(18.3, 32.5, 4.6), p3(18.0, 36.6, 4.2)]
    objs.append(tube(f"post{side}", post, [3.5, 3.5, 3.1], mats["hull"], squash=0.95))
    # The forearm: a pipe hooked over at its top, curving down to the gun.
    fore = [p3(14.4, 33.6, 5.0), p3(12.2, 31.4, 5.6), p3(9.2, 32.0, 5.4), p3(7.7, 35.4, 4.9), p3(7.7, 40.4, 4.2),
            p3(7.1, 45.6, 3.4)]
    objs.append(tube(f"forearm{side}", fore, [2.2, 2.9, 3.2, 3.3, 3.2, 3.0], mats["fore"], squash=0.9))
    # The gun: a collar and the lens, pointing down and out.
    lens_c = p(6.3, 48.8)
    d = Vector((p(5.0, 51.0)[0] - p(8.2, 45.5)[0], p(5.0, 51.0)[1] - p(8.2, 45.5)[1], -0.25)).normalized()
    angle = math.atan2(d.x, d.y)
    collar = k.lathe(f"gun_collar{side}", [(-3.6, 2.9), (-3.4, 3.35), (-1.7, 3.35), (-1.5, 2.9), (-0.7, 2.9),
                                            (-0.5, 2.5), (0.0, 2.5)], mats["steel"], 24)
    lens = k.ellipsoid(f"lens{side}", (0, 0.05, 0), (2.45, 1.3, 2.45), mats["lens"], 24, 12)
    for obj in (collar, lens):
        obj.data.transform(Matrix.Translation((lens_c[0], lens_c[1], 2.9)) @ Matrix.Rotation(-angle, 4, "Z") @
                           Matrix.Rotation(math.radians(38), 4, "X"))
        objs.append(k.smooth(obj, 50))
    for obj in objs:
        k.recalc_normals(obj)
    return objs


def build_robot():
    mats = robot_materials()
    objs = []
    for side in (-1, 1):
        objs += robot_half(side, mats)
    return objs


# --- DREAD-NOT's anchors (sheet 9, sprites 235, 236, 254, 274 and 238, 239, 258, 276) --------------------

ANCHOR_ORIGIN = (36, 28)
ANCHOR_PIECES = {
    "anchor_l_side": (0, 0),     # sprite 235
    "anchor_l_gun": (12, 0),     # sprite 236
    "anchor_l_hip": (0, 14),     # sprite 254
    "anchor_l_legs": (12, 28),   # sprite 274
    "anchor_r_gun": (36, 0),     # sprite 238
    "anchor_r_side": (48, 0),    # sprite 239
    "anchor_r_hip": (48, 14),    # sprite 258
    "anchor_r_legs": (36, 28),   # sprite 276
}


def anchor_materials():
    return {
        "body": k.material("anchor_body", palette=6, metallic=0.45, roughness=0.38),
        "base": k.material("anchor_base", palette=4, metallic=0.4, roughness=0.45),
        "gun": k.material("anchor_gun", palette=8, metallic=0.55, roughness=0.28),
        "rim": k.material("anchor_rim", palette=11, metallic=0.6, roughness=0.22),
        "leg": k.material("anchor_leg", palette=7, metallic=0.5, roughness=0.32),
        "dark": k.material("anchor_dark", palette=2, metallic=0.4, roughness=0.5),
    }


def anchor(side, mats):
    """One anchor standing on the ground (side -1: the left, art columns 0-35; 1: the right, its
    mirror image four pixels further left than the art's middle, from its own pixels). Its hooded
    body (columns 9-24, rows 0-30, a crest on top) holds a gun pointing at the other anchor (rows
    4-14) and four struts reaching out to the ground: outwards (rows 10-14), down and out, down and
    in, and straight down (columns 20-26, to row 44)."""
    rows = sh.art(art.ANCHOR)
    o = ANCHOR_ORIGIN
    mine = select(rows, lambda c, r, ch: (c < 36) == (side < 0))

    def p(c, r):
        x, y = c - o[0], o[1] - r
        return (x if side < 0 else -4.0 - x, y)

    def p3(c, r, z):
        return (*p(c, r), z)

    objs = []
    body_c = p(16.5, 19.0)

    def low(x, y, z):
        # The struts' part of the outline stays low: the struts are round parts of their own.
        d = math.hypot((x - body_c[0]) / 1.0, (y - body_c[1]) / 1.45)
        f = 1.0 - 0.72 * sh.smoothstep(7.5, 11.0, d)
        return z * f

    base = sh.outlines(mine, "0123456789abcdef", o, smooth=2, epsilon=0.45)
    hull = sh.inflate(f"anchor_hull{side}", base, mats["body"], sh.round_profile(0.95, max_height=8.2),
                      bottom=0.0, spacing=0.4, sigma=1.6, z_fn=low)
    objs.append(k.smooth(hull, 50))
    # The gun, along X, its muzzle ringed, a dark bore.
    def gun_profile(c0, c1):
        a, b = p(c0, 0)[0], p(c1, 0)[0]
        lo, hi = min(a, b), max(a, b)
        return lo, hi

    lo, hi = gun_profile(17.0, 29.9)
    gy, gz, gr = p(0, 9.3)[1], 5.6, 4.85
    if side < 0:
        prof = [(lo, 4.2), (lo + 0.6, gr - 0.2), (hi - 2.2, gr - 0.2), (hi - 2.0, gr), (hi - 0.35, gr),
                (hi, gr - 0.6), (hi + 0.01, 0.01)]
        bore = [(hi - 1.2, 2.6), (hi + 0.05, 2.6), (hi + 0.06, 0.01)]
    else:
        prof = [(lo - 0.01, 0.01), (lo, gr - 0.6), (lo + 0.35, gr), (lo + 2.0, gr), (lo + 2.2, gr - 0.2),
                (hi - 0.6, gr - 0.2), (hi, 4.2)]
        bore = [(lo - 0.06, 0.01), (lo - 0.05, 2.6), (lo + 1.2, 2.6)]
    gun = _lathe_x(f"gun{side}", prof, mats["gun"], y=gy, z=gz, squash=0.82)
    objs.append(paint(gun, [mats["gun"], mats["rim"]],
                      lambda x, y, z: 1 if (x > hi - 2.1 if side < 0 else x < lo + 2.1) else 0))
    objs.append(_lathe_x(f"bore{side}", bore, mats["dark"], y=gy, z=gz, squash=0.82, segments=20))
    # The struts: a joint at the body, a round leg narrowing to a foot on the ground.
    struts = [
        [p3(11.5, 12.2, 4.4), p3(6.0, 12.3, 3.4), p3(0.9, 12.4, 2.5)],            # outwards
        [p3(12.6, 27.6, 4.2), p3(8.4, 30.2, 3.2), p3(4.6, 32.6, 2.2)],           # down and out
        [p3(22.4, 29.6, 4.4), p3(26.4, 31.6, 3.3), p3(30.1, 33.3, 2.3)],         # down and in
        [p3(23.6, 31.0, 4.8), p3(23.3, 37.0, 3.6), p3(23.0, 43.4, 2.4)],         # down
    ]
    radii = [[2.4, 2.3, 2.15], [2.45, 2.3, 2.0], [2.4, 2.25, 2.0], [3.6, 3.0, 2.3]]
    for i, (path, rr) in enumerate(zip(struts, radii)):
        objs.append(tube(f"strut{side}{i}", path, rr, mats["leg"], squash=0.95))
        # A collar where the strut leaves the body.
        a, b = Vector(path[0]), Vector(path[1])
        d = (b - a).normalized()
        collar = k.lathe(f"collar{side}{i}", [(-0.55, rr[0]), (-0.4, rr[0] + 0.35), (0.4, rr[0] + 0.35),
                                              (0.55, rr[0])], mats["gun"], 20)
        collar.data.transform(Matrix.Translation(a + d * 1.4) @
                              Vector((0, 1, 0)).rotation_difference(d).to_matrix().to_4x4())
        objs.append(k.smooth(collar, 50))
    # The crest on the hood's top: a blade along its ridge.
    crest = [p3(16.0, 6.5, 8.6), p3(18.0, 3.0, 7.0), p3(19.6, 0.9, 4.6)]
    objs.append(tube(f"crest{side}", crest, [1.6, 1.3, 0.9], mats["body"], squash=1.2))
    for obj in objs:
        k.recalc_normals(obj)
    return sh.flat_bottom(objs)


def _lathe_x(name, profile, mat, segments=28, y=0.0, z=0.0, squash=1.0):
    """A round part along X: profile is (x, radius) pairs in increasing x."""
    obj = k.lathe(name, profile, mat, segments=segments, squash=squash)
    obj.data.transform(Matrix.Rotation(math.radians(-90), 4, "Z"))
    obj.data.transform(Matrix.Translation((0.0, y, z)))
    return k.smooth(obj, 50)


def build_anchors():
    mats = anchor_materials()
    objs = []
    for side in (-1, 1):
        objs += anchor(side, mats)
    return objs


# --- NOSE DRIP's nose (sheet 5, sprites 154 above 191 and 193) -------------------------------------------

NOSE_ORIGIN = (24, 28)
NOSE_PIECES = {
    "nose_bridge": (12, 0),      # sprite 154
    "nose_tip_left": (0, 28),    # sprite 191
    "nose_tip_right": (24, 28),  # sprite 193
}


def build_nose():
    """The face's nose rising from the face (z = 0) towards the camera: the bridge narrow at the
    top (rows 2-9) and widening, the round tip (rows 28-42), the wings beside it and the black
    nostrils under them (the art's n), the columella between them reaching down to row 51."""
    rows = sh.art(art.NOSE)
    o = NOSE_ORIGIN
    skin = k.material("nose_skin", palette=24, metallic=0.25, roughness=0.36)
    dark = k.material("nose_nostril", palette=16, metallic=0.0, roughness=0.6)

    def p(c, r):
        return c - o[0], o[1] - r

    def bump(x, y, c, r, rx, ry, h):
        cx, cy = p(c, r)
        q = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
        return h * math.sqrt(max(0.0, 1.0 - q)) if q < 1.0 else -2.0 * (math.sqrt(q) - 1.0)

    # The bridge fills the outline of its rows (2-27) across, rounded; further down it keeps row 27's.
    spans = {}
    for r in range(2, 28):
        cols = [c for c, ch in enumerate(rows[r]) if ch != "."]
        spans[r] = ((cols[0] + cols[-1] + 1) / 2.0 - o[0], (cols[-1] + 1 - cols[0]) / 2.0)
    # Smoothed along the rows (the outline's pixel steps would show as ridges).
    weights = (1, 2, 3, 4, 3, 2, 1)
    smooth_spans = {}
    for r in spans:
        acc, total = [0.0, 0.0], 0.0
        for j, w in enumerate(weights):
            rr = min(max(r + j - 3, 2), 27)
            acc[0] += spans[rr][0] * w
            acc[1] += spans[rr][1] * w
            total += w
        smooth_spans[r] = (acc[0] / total, acc[1] / total)
    spans = smooth_spans

    def span(r):
        r = min(max(r - 0.5, 2.0), 27.0)
        r0 = int(math.floor(r))
        r1 = min(r0 + 1, 27)
        f = r - r0
        return tuple(spans[r0][i] * (1 - f) + spans[r1][i] * f for i in range(2))

    def bridge(x, y):
        r = o[1] - y
        cx, width = span(r)
        width = width + 0.3
        height = 3.4 + 7.2 * sh.smoothstep(0.0, 34.0, r)
        q = ((x - cx) / width) ** 2
        top = 1.0 - sh.smoothstep(-1.0, 3.0, 1.5 - r)
        return height * math.sqrt(max(0.0, 1.0 - q)) * top if q < 1.0 else -2.0 * (math.sqrt(q) - 1.0)

    nostrils = [(15.4, 42.8, 4.0, 2.5, -20.0), (32.9, 43.3, 4.7, 2.9, 25.0)]  # column, row, radii, slant

    def nostril_depth(x, y):
        depth = 0.0
        for c, r, rx, ry, slant in nostrils:
            cx, cy = p(c, r)
            ca, sa = math.cos(math.radians(slant)), math.sin(math.radians(slant))
            u, v = (x - cx) * ca + (y - cy) * sa, -(x - cx) * sa + (y - cy) * ca
            q = (u / rx) ** 2 + (v / ry) ** 2
            depth = max(depth, 1.0 - sh.smoothstep(0.35, 1.2, q))
        return depth

    def height(x, y):
        h = bridge(x, y)
        h = smoothmax(h, bump(x, y, 24.2, 35.5, 8.6, 8.2, 12.8), 2.5)       # the tip
        h = smoothmax(h, bump(x, y, 12.8, 40.0, 7.4, 7.6, 7.6), 2.0)        # the left wing
        h = smoothmax(h, bump(x, y, 36.4, 40.0, 7.4, 7.6, 7.6), 2.0)        # the right wing
        h = smoothmax(h, bump(x, y, 24.4, 45.5, 4.6, 6.5, 6.5), 2.0)        # the columella
        h = max(h, 1.2)
        return h - 2.6 * nostril_depth(x, y)

    outline = sh.outlines(rows, "0123456789abcdefn", o, smooth=2, epsilon=0.45)
    nose = sh.inflate("nose", outline, skin, sh.pillow_profile(1.0, 2.4), bottom=0.0, rim=0.05, spacing=0.4,
                      z_fn=lambda x, y, z: 0.05 + max(0.0, min(1.0, z - 0.05)) * max(0.6, height(x, y)))
    objs = [k.smooth(nose, 60)]
    # The nostrils: black hollows in the pits under the wings.
    for i, (c, r, rx, ry, slant) in enumerate(nostrils):
        cx, cy = p(c, r)
        floor = sh.surface_z(nose, cx, cy, 2.0)
        hole = k.ellipsoid(f"nostril{i}", (0, 0, 0), (rx * 0.98, ry * 0.98, 1.2), dark, 32, 12)
        hole.data.transform(Matrix.Translation((cx, cy, floor + 0.95)) @ Matrix.Rotation(math.radians(slant), 4, "Z"))
        objs.append(k.smooth(hole, 60))
    return objs


# --- Registry -----------------------------------------------------------------------------------------

PIECES = []    # (name, sheet, sprite, builder)
ASSEMBLED = []  # (name, builder, size)

for _name, _sprite in (("eyespy_l_dome", 3), ("eyespy_l_arm", 39), ("eyespy_r_dome", 5), ("eyespy_r_arm", 45),
                       ("eyespy_l_shoulder", 1), ("eyespy_r_shoulder", 7)):
    PIECES.append((_name, "9", _sprite,
                   lambda name=_name: cut_pieces(build_robot, ROBOT_PIECES, name, ROBOT_ORIGIN)))
ASSEMBLED.append(("eyespy", build_robot, (96, 56)))
for _name, _sprite in (("anchor_l_legs", 274), ("anchor_r_legs", 276), ("anchor_l_side", 235), ("anchor_l_gun", 236),
                       ("anchor_l_hip", 254), ("anchor_r_gun", 238), ("anchor_r_side", 239), ("anchor_r_hip", 258)):
    PIECES.append((_name, "9", _sprite,
                   lambda name=_name: cut_pieces(build_anchors, ANCHOR_PIECES, name, ANCHOR_ORIGIN)))
ASSEMBLED.append(("anchors", build_anchors, (72, 56)))
for _name, _sprite in (("nose_bridge", 154), ("nose_tip_left", 191), ("nose_tip_right", 193)):
    PIECES.append((_name, "5", _sprite, lambda name=_name: cut_pieces(build_nose, NOSE_PIECES, name, NOSE_ORIGIN)))
ASSEMBLED.append(("nose", build_nose, (48, 56)))
