"""TORM's grey armoured orb on the foliage (sheet J sprite 83, 2x2: 24 x 28 pixels; enemy 751 of episode 2, ground layer,
each one alone; its animation 83 121 85 123 87 125 125 125 87 87 87 123 123 123 85 85 85 121 121 83 plays as it fires,
and its damaged look, dgr 83 with dlevel -1, is the orb shut: the wreck it leaves), polished (2026-10-21; it replaces
wave3_m_ground.py's eye_orb(), an ellipsoid with a hoop round a lens and three tube brackets, and wave3_at_j.py's
eye_orb_83, the same with its eye taken out). models.cfg: model eye_orb / eye_orb_121 / eye_orb_85 / eye_orb_123 /
eye_orb_87 / eye_orb_125 enemies/eye_orb*.glb origin; sprite j 83 eye_orb yaw=0 height=-4; frame j 121 eye_orb_121,
frame j 85 eye_orb_85, frame j 123 eye_orb_123, frame j 87 eye_orb_87, frame j 125 eye_orb_125 (no other enemy shows
these sprites); eye_orb itself is 83, the orb shut, so the old frame line on 83 and eye_orb_83 go. No other sprite has
their pixels mirrored, turned or in other ramps (its frames are each other's shell with another eye).

As the sprites and their 4x upscales draw it (columns and rows of the 24 x 28 sprite): a grey ball wider than it is
deep (columns 1-21 of rows 4-19, its middle at column 11, row 11.5), lit from the upper left (0x09 over most of it,
0x0b-0x0f in a highlight at columns 6-8 of rows 7-9, 0x07-0x02 down its lower right), sitting in a collar whose rim
shows as a lighter crescent below it (rows 16-21: 0x08-0x0c on its right and front, dark on its left); the black round
its right side and under it (transparent pixels in the sprite, which the upscale paints black) is its outline and
shadow in the leaves, and the leaves (ramps 2 and 12) are the map's: the model leaves them out. 83 draws the ball shut
and smooth. 121, 85, 123, 87 and 125 draw it open: an opening at its top (columns 6-15 of rows 4-13) holds a round
glass eye (columns 7-14 of rows 5-12), and seams part the shell into petals: one down its front from the eye to the
collar (column 10), one from either side of the eye round to the ball's sides (rows 10-13), where a hinge boss holds
them. The eye brightens frame by frame: 121 dull brown glass (ramps 10 and 1, 0xa6-0xac, 0x19-0x1b), 85 pink (ramp 4,
0x45-0x4b, a bright spot 0x7c), 123 red (0x70-0x7a, its spot 0x7d-0x7f at the upper left, a glowing crescent at the
lower right and a dark band at the lower left, as a glass ball lit through), 87 orange-hot (0x74-0x7f), 125 yellow-white
(0x7a-0x7f over nearly all of it).

Built for the game's slanted camera: the shell is an ellipsoid (RADII) on the ground whose top view covers the ball's
pixels; its opening, the eye and the seams are laid out round an axis tilted from straight up, so that the camera (20
degrees off straight down, from the bottom of the screen) sees the eye as high on the ball as the sprite draws it
(EYE_VIEW; polish_dark_orb.py's VIEW_TILT). The shell is lofted ring by ring round that axis (its rings near the
opening drawn in towards a rounder oval, so the opening and the eye are as round as the sprite draws them, not as wide
as the ball), the opening's lip rolls into a dark socket, the eye is a glossy lens in it, cut along smooth contours into
bands of its brightness (polish_orb_red.band_split: a hot spot at its upper left, dark at its lower left, the light
through it at its lower right), glowing in their own colours (0-0.6: the game's bloom adds), and the seams are
grooves pressed into the shell along the petals' edges, painted dark. The shell's greys are bands of how squarely it
faces the light (LIGHT, the upper left, where the sprite and the game's sun light it: 0x0c, 0x0b, 0x09, 0x08, a
shade over the sprite's, which read as charcoal in the game). Under
it a round rim (lit on top, as the sprite's crescent) stands a little off the ball at its front, so that a dark gap
shows between them as in the sprite, on a dark foot and floor; the hinge bosses are short pins at the side seams'
ends. One model per frame: eye_orb (83) is the whole shell closed over the eye (no opening, no seams); the five others
are the same open shell, each with its eye's colours and glow.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the ground (z = 0); origin at
the sprite's centre (pixel 12, 14): column c is x = c + 0.5 - 12, row r is y = 13.5 - r.

Where it stands: drawn at its origin (models.cfg origin), height=-4 sets the collar's foot on the terrain (as the other
polished ground models of TORM do: the lens pad, the window block, the jaw guns); the ring's foot reaches SKIRT below z = 0
so no gap shows on uneven ground.

Replaces wave3_m_ground.py's eye_orb(): its section ("# --- J 83: the eye orb": the @model("eye_orb", [(J, 83, True)])
registration and eye_orb()) and eye_orb's paragraph in its docstring; and wave3_at_j.py's eye orb: its section
("# --- The eye orb, shut": eye_orb_shut() and the w.model("eye_orb_83", ...) registration), its docstring paragraph,
and then its import of wave3_m_ground (mg = kit.quiet_import("wave3_m_ground"): only the eye orb used it).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each frame's silhouette
against the orb's own pixels in enemy_J.png), --preview <prefix>, --only <name,...>.
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k, smoothstep  # noqa: E402
from polish_orb_red import band_split  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402

# The frames: (model, sprite, the eye's bands: (lowest brightness, palette index, glow)); None: the orb shut.
FRAMES = [
    ("eye_orb", 83, None),
    ("eye_orb_121", 121, [(0xa3, 0.0), (0xa5, 0.02), (0xa7, 0.03), (0xa9, 0.04), (0x1a, 0.05), (0x1c, 0.07)]),
    ("eye_orb_85", 85, [(0x43, 0.04), (0x45, 0.06), (0x47, 0.09), (0x49, 0.12), (0x4b, 0.16), (0x4d, 0.22)]),
    ("eye_orb_123", 123, [(0x70, 0.1), (0x72, 0.15), (0x75, 0.22), (0x78, 0.3), (0x7b, 0.38), (0x7e, 0.45)]),
    ("eye_orb_87", 87, [(0x74, 0.18), (0x77, 0.26), (0x79, 0.33), (0x7b, 0.4), (0x7d, 0.47), (0x7f, 0.54)]),
    ("eye_orb_125", 125, [(0x7b, 0.32), (0x7c, 0.38), (0x7d, 0.44), (0x7e, 0.5), (0x7f, 0.55), (0x7f, 0.6)]),
]
# The eye's bands: the lowest brightness of each (the frames' colours above go with them in order).
EYE_BANDS = (-9.0, 0.18, 0.32, 0.46, 0.6, 0.75)

SKIRT = 1.2                         # how far the collar reaches below the ground (z = 0)

# The shell: its middle and radii (x, y, z), standing on the ground.
CENTRE = Vector((-0.5, 2.0, 9.2))
RADII = (10.5, 7.9, 9.2)
# Where the camera should see the eye's middle on the ball's disc (the sprite's: column 10.6, row 8.5 on a disc round
# column 11, row 11.7 of 10.5 x 7.75 pixels): (across, up) as fractions of the disc's half-width and half-height.
EYE_VIEW = (-0.07, 0.5)
VIEW_TILT = 20.0
# The opening round the eye's axis: its half-depth (along the shell's y) and how much wider it is across (an oval, as
# the sprite's opening is: the rings round it are drawn in towards it from the ball's 1.36), and where the rings start
# going over from the ball's oval into the opening's (fraction of the way down from the axis, as sin of the angle).
HOLE = 5.1
HOLE_ASPECT = 1.12
BLEND_FROM = 0.92
# The lip rolling into the socket and the socket's wall and floor: (inward, up along the axis) from the opening's edge.
SOCKET = [(0.28, 0.2), (0.56, 0.16), (0.74, -0.25), (0.86, -0.95), (0.9, -2.1), (1.4, -2.5)]
LIP_RINGS = 2                       # the first rings of SOCKET are the lit lip, the rest dark
# The eye: its radii as inset from the socket's wall (across, deep) and its height (along the axis, from its middle),
# and how far its middle lies below the opening's edge.
EYE_INSET = 0.3
EYE_HEIGHT = 3.3
EYE_DROP = 0.75
# Its brightness (as the sprite's glass ball lit through): a base, the hot spot at its upper left, the light coming
# through at its lower right, the dark at its lower left and down its right edge: (middle (across, deep) as fractions
# of its radii, falloff, weight); and how much its rim darkens.
EYE_BASE = 0.36
EYE_SPOTS = [((-0.22, 0.32), 0.2, 0.55), ((-0.4, -0.65), 0.3, -0.22)]
EYE_GLOW = (0.86, 0.02, -45.0, 0.3)      # the light through it: radius, falloff, the angle it faces, weight
EYE_RIM = 0.15
# The seams: angles round the axis (degrees from the shell's +x, counter-clockwise: 0 the right side, 180 the left,
# 270 the front, down the screen), their half-width and depth (pixels).
SEAMS = (0.0, 180.0, 270.0)
SEAM_HALF, SEAM_DEPTH = 0.32, 0.32
# The shell's greys as the sprite shades it, lit from the upper left (the game's sun comes from there too): bands of
# how squarely a point faces LIGHT (the lowest of each band and its material), cut along smooth contours.
LIGHT = Vector((-0.55, 0.45, 0.7)).normalized()
SHADES = [(-9.0, "shell_dark"), (-0.15, "shell_low"), (0.3, "shell"), (0.88, "shell_light")]
# The hinge bosses at the side seams' ends: how far round from the axis (degrees), radius, how far they stand out.
BOSS_AT, BOSS_R, BOSS_OUT = 84.0, 1.05, 0.55
# The ring the ball sits in: a round rim (its tube's radius, the height of its middle) round the ball, a gap between them
# at the front that opens on the dark floor (the sprite's dark band between the ball and the crescent), none at the
# sides, the rim sunk into the ball at the back; under it a dark foot down into the ground, a dark floor inside.
RIM_TUBE, RIM_Z = 1.45, 3.0
RIM_GAP = 1.0                       # the gap at the front (straight down the screen), going to none at the sides
FOOT_IN, FLOOR_Z = 0.55, 0.35

SEGMENTS = 72                       # points round each ring (5 degrees: the seams fall on points)


def materials():
    def grey(name, index, metallic=0.4, roughness=0.32):
        return k.material(name, palette=index, metallic=metallic, roughness=roughness)
    # A shade lighter and less metallic than the sprite's greys: in the game's light (a dark sky to reflect) the
    # sprite's own shades read as charcoal.
    return {
        "shell_light": grey("orb_shell_light", 0x0c, 0.25, 0.24),
        "shell": grey("orb_shell", 0x0b, 0.25, 0.28),
        "shell_low": grey("orb_shell_low", 0x09, 0.3, 0.32),
        "shell_dark": grey("orb_shell_dark", 0x08, 0.3, 0.36),
        "seam": grey("orb_seam", 0x02, 0.4, 0.5),
        "lip": grey("orb_lip", 0x0c, 0.35, 0.24),
        "socket": grey("orb_socket", 0x01, 0.3, 0.55),
    }


def eye_materials(colours):
    pal = k.level_palette()
    return [(lowest, k.material(f"orb_eye_{index:x}", palette=index, metallic=0.1, roughness=0.06,
                                emission=pal[index], emission_strength=strength))
            for lowest, (index, strength) in zip(EYE_BANDS, colours)]


# --- The eye's axis -------------------------------------------------------------------------------------------------

T = math.radians(VIEW_TILT)


def view_of(p):
    """Where the point p of the shell shows on the ball's disc as the game camera sees it (fractions of the disc's
    half-width and half-height)."""
    rx, ry, rz = RADII
    rel = p - CENTRE
    view_h = math.hypot(ry * math.cos(T), rz * math.sin(T))
    return rel.x / rx, (rel.y * math.cos(T) + rel.z * math.sin(T)) / view_h


def eye_axis():
    """The direction from the shell's middle whose point on the shell the camera sees at EYE_VIEW (a search over a fine
    grid of directions near straight up; the same every run)."""
    rx, ry, rz = RADII
    best = None
    for i in range(-60, 61):
        for j in range(-60, 61):
            d = Vector((i * 0.004, j * 0.004, 1.0)).normalized()
            t = 1.0 / math.sqrt((d.x / rx) ** 2 + (d.y / ry) ** 2 + (d.z / rz) ** 2)
            u, v = view_of(CENTRE + d * t)
            err = (u - EYE_VIEW[0]) ** 2 + (v - EYE_VIEW[1]) ** 2
            if best is None or err < best[0]:
                best = (err, d)
    return best[1]


def axis_matrix():
    """The shell's own frame (its +z the eye's axis, its +x as near the world's +x as can be) placed at its middle."""
    d = eye_axis()
    x = (Vector((1.0, 0.0, 0.0)) - d * d.x).normalized()
    y = d.cross(x)
    m = Matrix((x.to_4d(), y.to_4d(), d.to_4d(), (0.0, 0.0, 0.0, 1.0))).transposed()
    m.translation = CENTRE
    return m


# --- The shell ------------------------------------------------------------------------------------------------------

def ring_radii(s):
    """The ring's half-widths (across, deep) at sin(angle from the axis) s: the ball's oval, drawn in near the opening
    to the opening's rounder oval."""
    rx, ry, _ = RADII
    a, b = rx * s, ry * s
    w = 1.0 - smoothstep(HOLE / ry, BLEND_FROM, s)
    return b * HOLE_ASPECT * w + a * (1.0 - w), b


def angles():
    return [2 * math.pi * j / SEGMENTS for j in range(SEGMENTS)]


def shell_thetas(open_):
    """The rings' angles from the axis: from the opening's edge (or near the pole) down to near the bottom, closer near
    the top."""
    ry = RADII[1]
    top = math.asin(HOLE / ry) if open_ else 0.06
    n = 28
    return [top + (math.pi - 0.06 - top) * (0.55 * (i / n) + 0.45 * (i / n) ** 2) for i in range(n + 1)]


def seam_distance(phi, a, b):
    """How far (pixels along the ring) the point at angle phi of a ring with half-widths a, b is from the nearest seam."""
    best = 1e9
    for s in SEAMS:
        d = abs(((math.degrees(phi) - s) + 180.0) % 360.0 - 180.0)
        best = min(best, math.radians(d) * math.hypot(a * math.sin(phi), b * math.cos(phi)))
    return best


def edge_radii():
    return ring_radii(math.sin(math.asin(HOLE / RADII[1])))


def shell(m, open_, light):
    """The shell, in its own frame (the eye's axis +z): rings round the axis from the socket's floor up over the
    opening's lip (open) or from the pole, down to the bottom; open, the seams are grooved and painted dark; its greys
    in bands of how it faces the light (light: LIGHT in the shell's frame)."""
    rz = RADII[2]
    phis = angles()
    rings, values = [], []
    thetas = shell_thetas(open_)
    for th in thetas:
        a, b = ring_radii(math.sin(th))
        rings.append([Vector((a * math.cos(p), b * math.sin(p), rz * math.cos(th))) for p in phis])
        values.append([seam_distance(p, a, b) if open_ else 9.0 for p in phis])
    edge_z = rz * math.cos(thetas[0])
    if open_:
        a, b = edge_radii()
        socket = [[Vector(((a - inward) * math.cos(p), (b - inward) * math.sin(p), edge_z + up)) for p in phis]
                  for inward, up in SOCKET]
        rings = list(reversed(socket)) + rings
        values = [[9.0] * SEGMENTS for _ in socket] + values
        start = Vector((0.0, 0.0, edge_z + SOCKET[-1][1] - 0.1))
    else:
        start = Vector((0.0, 0.0, rz))
    obj = k.loft("shell", rings, m["shell"], start_point=start, end_point=Vector((0.0, 0.0, -rz)))
    slot = {key: mk.slot_of(obj, m[key]) for key in m}
    n, n_socket, bands = SEGMENTS, (len(SOCKET) if open_ else 0), len(rings) - 1
    for poly in obj.data.polygons:
        row = poly.index // n
        if row >= bands:    # the end fans: the socket's floor (open) or the pole, and the bottom
            poly.material_index = slot["socket"] if (open_ and poly.center.z > 0) else slot["shell"]
        elif row < n_socket:
            # The socket's bands from its floor up to the lip; the last LIP_RINGS join the lip to the shell's edge.
            poly.material_index = slot["lip"] if n_socket - row <= LIP_RINGS else slot["socket"]
        else:
            poly.material_index = slot["shell"]
    if open_:
        vals = [v for ring in values for v in ring] + [9.0, 9.0]
        vals = split_bands(obj, vals, [(-9.0, slot["seam"]), (SEAM_HALF, None)])
        press_seams(obj, vals)
    rx, ry, _ = RADII
    shade = [Vector((v.co.x / rx ** 2, v.co.y / ry ** 2, v.co.z / rz ** 2)).normalized().dot(light)
             for v in obj.data.vertices]
    split_bands(obj, shade, [(lowest, slot[name]) for lowest, name in SHADES], only={slot["shell"]})
    k.recalc_normals(obj)
    return k.smooth(obj, 50)


def split_bands(obj, values, bands, only=None):
    """polish_orb_red.band_split keeping other materials: the faces whose material slot is in only (all if None) are
    cut along the smooth contours where the value per vertex crosses the bands' borders and get their band's slot (a
    band of None keeps the face's own); the other faces stay as they are. Returns the new mesh's vertices' values."""
    mesh = obj.data
    co = [v.co.copy() for v in mesh.vertices]
    vals = list(values)
    thresholds = [b[0] for b in bands]
    cuts = {}

    def cut(a, b, t):
        key = (min(a, b), max(a, b), t)
        if key not in cuts:
            f = (t - vals[a]) / (vals[b] - vals[a])
            co.append(co[a].lerp(co[b], f))
            vals.append(t)
            cuts[key] = len(co) - 1
        return cuts[key]

    def clip(poly, t, above):
        out = []
        for i in range(len(poly)):
            a, b = poly[i], poly[(i + 1) % len(poly)]
            ina, inb = (vals[a] >= t) == above, (vals[b] >= t) == above
            if ina:
                out.append(a)
            if ina != inb:
                out.append(cut(a, b, t))
        return out

    faces, mats = [], []
    for poly in mesh.polygons:
        idx = list(poly.vertices)
        if only is not None and poly.material_index not in only:
            faces.append(idx)
            mats.append(poly.material_index)
            continue
        low, high = min(vals[i] for i in idx), max(vals[i] for i in idx)
        for b in range(len(bands)):
            lo = thresholds[b] if b > 0 else -1e9
            hi = thresholds[b + 1] if b + 1 < len(bands) else 1e9
            if high < lo or low >= hi:
                continue
            piece = idx
            if b > 0 and low < lo:
                piece = clip(piece, lo, True)
            if b + 1 < len(bands) and high >= hi:
                piece = clip(piece, hi, False)
            if len(piece) >= 3:
                faces.append(piece)
                mats.append(poly.material_index if bands[b][1] is None else bands[b][1])
    new = bpy.data.meshes.new(mesh.name)
    new.from_pydata([tuple(c) for c in co], [], faces)
    for mat in mesh.materials:
        new.materials.append(mat)
    for poly, mat in zip(new.polygons, mats):
        poly.material_index = mat
    new.validate()
    obj.data = new
    return vals


def press_seams(obj, vals):
    """The seams' middles pressed in along the shell's normal (deepest on the seam, nothing at its border)."""
    rx, ry, rz = RADII
    for v in obj.data.vertices:
        f = vals[v.index] if v.index < len(vals) else 9.0
        if f >= SEAM_HALF:
            continue
        p = v.co
        n = Vector((p.x / rx ** 2, p.y / ry ** 2, p.z / rz ** 2)).normalized()
        v.co = p - n * SEAM_DEPTH * (1.0 - f / SEAM_HALF)


def bosses(m):
    """The hinge bosses at the side seams' ends (in the shell's frame): short pins standing out of the shell."""
    out = []
    th = math.radians(BOSS_AT)
    a, b = ring_radii(math.sin(th))
    for side, phi in ((1, 0.0), (-1, math.pi)):
        p = Vector((a * math.cos(phi), b * math.sin(phi), RADII[2] * math.cos(th)))
        nrm = Vector((p.x / RADII[0] ** 2, p.y / RADII[1] ** 2, p.z / RADII[2] ** 2)).normalized()
        prof = [(-0.4, BOSS_R), (BOSS_OUT - 0.25, BOSS_R), (BOSS_OUT - 0.05, BOSS_R * 0.82), (BOSS_OUT, 0.01)]
        out.append(turned(f"boss{side}", prof, p, nrm, m["lip"], 20))
    return out


def turned(name, profile, origin, axis, mat, segments=24):
    """A round part along an axis: profile [(along, radius), ...] from origin; closed at both ends."""
    d = Vector(axis).normalized()
    ref = Vector((0, 0, 1)) if abs(d.z) < 0.9 else Vector((1, 0, 0))
    a = d.cross(ref).normalized()
    b = d.cross(a).normalized()
    o = Vector(origin)
    rings = []
    for t, r in profile:
        rings.append([o + d * t + (a * math.cos(2 * math.pi * j / segments) + b * math.sin(2 * math.pi * j / segments)) * r
                      for j in range(segments)])
    obj = k.loft(name, rings, mat, start_point=o + d * profile[0][0], end_point=o + d * profile[-1][0])
    return k.smooth(obj, 50)


def eye(bands):
    """The glass eye in the socket (in the shell's frame): an ellipsoid of even triangles, cut into bands of its
    brightness."""
    from polish_orb_red import icosphere
    a, b = edge_radii()
    wall = SOCKET[4][0]
    ra, rb = a - wall - EYE_INSET, b - wall - EYE_INSET
    edge_z = RADII[2] * math.cos(math.asin(HOLE / RADII[1]))
    cz = edge_z - EYE_DROP
    obj = icosphere("eye", (0.0, 0.0, cz), (ra, rb, EYE_HEIGHT), subdivisions=3)

    def value(p):
        u, v = p.x / ra, p.y / rb
        rho = math.hypot(u, v)
        b = EYE_BASE - EYE_RIM * smoothstep(0.75, 1.0, rho)
        for (sx, sy), falloff, weight in EYE_SPOTS:
            b += weight * math.exp(-((u - sx) ** 2 + (v - sy) ** 2) / falloff)
        radius, falloff, facing, weight = EYE_GLOW
        towards = max(0.0, math.cos(math.atan2(v, u) - math.radians(facing))) if rho > 1e-6 else 0.0
        return b + weight * math.exp(-(rho - radius) ** 2 / falloff) * towards ** 2
    band_split(obj, [value(v.co) for v in obj.data.vertices], eye_materials(bands))
    k.recalc_normals(obj)
    return k.smooth(obj, 80)


def rim_path(n=72):
    """The rim's middle line: round the ball's outline at RIM_Z, out by the tube and the gap (most at the front)."""
    rx, ry, rz = RADII
    f = math.sqrt(max(0.0, 1.0 - ((RIM_Z - CENTRE.z) / rz) ** 2))
    a, b = rx * f, ry * f
    pts = []
    for j in range(n):
        p = 2 * math.pi * j / n
        s = math.sin(p)
        gap = RIM_GAP * smoothstep(-0.2, -1.0, s) - (RIM_TUBE + 0.4) * smoothstep(0.2, 1.0, s)
        nx, ny = math.cos(p) / a, s / b
        norm = math.hypot(nx, ny)
        out = RIM_TUBE + gap
        pts.append(Vector((CENTRE.x + a * math.cos(p) + out * nx / norm, CENTRE.y + b * s + out * ny / norm, RIM_Z)))
    return pts


def loop_tube(name, path, radius, mat, segments=16):
    """A round tube along a closed path (a ring), its cross-sections upright."""
    n = len(path)
    verts, faces = [], []
    for i, p in enumerate(path):
        t = (path[(i + 1) % n] - path[i - 1]).normalized()
        out = t.cross(Vector((0, 0, 1))).normalized()
        if out.dot(p - Vector((CENTRE.x, CENTRE.y, p.z))) < 0:
            out = -out
        for j in range(segments):
            a = 2 * math.pi * j / segments
            verts.append(p + (out * math.cos(a) + Vector((0, 0, 1)) * math.sin(a)) * radius)
    for i in range(n):
        for j in range(segments):
            a, b = i * segments + j, i * segments + (j + 1) % segments
            c, d = ((i + 1) % n) * segments + (j + 1) % segments, ((i + 1) % n) * segments + j
            faces.append((a, b, c, d))
    obj = k.mesh_object(name, verts, faces, mat)
    k.recalc_normals(obj)
    return obj


def collar(m):
    """The ring the ball sits in (in the world's frame): the rim, lit on top, darker below; its foot and the floor."""
    path = rim_path()
    rim = loop_tube("rim", path, RIM_TUBE, m["lip"])
    mk.paint(rim, lambda c, nrm: m["shell_low"] if nrm.z < -0.15 else None)
    k.smooth(rim, 60)
    # The foot: a band from inside the rim's underside down into the ground, and the floor inside it.
    centre = Vector((CENTRE.x, CENTRE.y, 0.0))
    inner = []
    for p in path:
        flat = Vector((p.x, p.y, 0.0))
        d = (flat - centre)
        inner.append(flat - d.normalized() * FOOT_IN)
    rings = [[Vector((q.x, q.y, -SKIRT)) for q in inner], [Vector((q.x, q.y, RIM_Z - 0.3)) for q in inner]]
    foot = k.loft("foot", [r for r in rings], m["seam"], start_point=(CENTRE.x, CENTRE.y, -SKIRT),
                  end_point=(CENTRE.x, CENTRE.y, RIM_Z - 0.3))
    # its top (inside the ring, under the ball) is the floor: lowered to FLOOR_Z
    for v in foot.data.vertices:
        if v.co.z > RIM_Z - 0.5 and math.hypot(v.co.x - CENTRE.x, v.co.y - CENTRE.y) < 0.01:
            v.co.z = FLOOR_Z
    k.recalc_normals(foot)
    return [rim, k.smooth(foot, 30)]


def build_frame(name, bands):
    k.reset()
    m = materials()
    open_ = bands is not None
    frame = axis_matrix()
    light = (frame.to_3x3().inverted() @ LIGHT).normalized()
    parts = [shell(m, open_, light)] + bosses(m)
    if open_:
        parts.append(eye(bands))
    mk.transform(parts, frame)
    parts += collar(m)
    return triangulate(parts)


def mask_of(sheet, sprite):
    """The orb's own pixels: the greys and the eye's colours joined to the ball (the leaves, ramps 2 and 12, left out)."""
    from sprite_profile import sprite_indices
    idx = sprite_indices(sheet, sprite)
    h, w = len(idx), len(idx[0])
    own = [[idx[r][c] is not None and idx[r][c] >> 4 not in (2, 12) for c in range(w)] for r in range(h)]
    # The largest 4-connected group (the ball, its collar and its eye).
    seen = [[False] * w for _ in range(h)]
    best = []
    for r0 in range(h):
        for c0 in range(w):
            if own[r0][c0] and not seen[r0][c0]:
                group, stack = [], [(r0, c0)]
                seen[r0][c0] = True
                while stack:
                    r, c = stack.pop()
                    group.append((r, c))
                    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        rr, cc = r + dr, c + dc
                        if 0 <= rr < h and 0 <= cc < w and own[rr][cc] and not seen[rr][cc]:
                            seen[rr][cc] = True
                            stack.append((rr, cc))
                if len(group) > len(best):
                    best = group
    mask = [[False] * w for _ in range(h)]
    for r, c in best:
        mask[r][c] = True
    return mask


def build():
    options = k.args()
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    for name, sprite, bands in FRAMES:
        if only and name not in only:
            continue
        parts = build_frame(name, bands)
        bpy.context.view_layer.update()
        if "check" in options:
            sheet = os.path.join(options["check"], "enemy_J.png")
            sys.path.insert(0, os.path.join(HERE, "..", ".."))
            mk.compare("%s (J %d, the orb's own pixels)" % (name, sprite), mk.coverage(parts, 24, 28),
                       mask_of(sheet, sprite))
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        mk.report(name, parts, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, parts, distance=0.6)


if __name__ == "__main__":
    build()
