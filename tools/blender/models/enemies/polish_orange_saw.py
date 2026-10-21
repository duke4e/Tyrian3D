"""FRUIT's bladed orange (sheet ', written x27 in models.cfg; enemies 1229-1232 of episode 5, all sky enemies): a
dimpled orange on a steel saw plate whose eight curved blades sweep up towards their tips. Polished (2026-10-21; it
replaces wave3_ae.py's orange_saw and wave3_at_orange.py's frame models of it). The levels always put its four 2x2
sprites together as one 48 x 56 picture (FRUIT's sky events at 870-1660, type 15, 35 groups): 1229 (' 78) at (x,
y - 28), 1230 (' 80) at (x + 24, y - 28), 1231 (' 116) at (x, y), 1232 (' 118) at (x + 24, y); each is an enemy of
its own (the four move together and can be shot away one by one). Their animation (78 82, 80 84, 116 120, 118 122, a
frame each) turns the blades a sixteenth of a turn, so that the two frames make the saw spin: frame models
orange_saw_82, _84, _120, _122 (no other enemy, launched ones included, shows any of these eight sprites; none of
them is another sprite's pixels mirrored, turned or in other ramps, in any sheet).

As the sprites and their 4x upscales draw it (columns and rows of the 48 x 56 picture): an orange ball 20 pixels
across (columns 14-33 of rows 18-37, its middle the corner where the four sprites meet), its peel stippled in two
oranges (0x79, 0x7a: dimples), darker red round its lower left (0x74-0x77), lit at its upper right (0x7b); round it
eight curved steel blades (greys of ramps 0 and 6, a light ridge along each, 0x0e and 0x5e where the light catches
it), each leaving the peel about 5 pixels wide and tapering to a needle point 24-25 pixels out, curving the same way
round (counter-clockwise outwards: about 20 degrees further round at its tip than where it leaves the peel). The
sprites space the blades unevenly, alternately 42 and 48 degrees apart (four-fold symmetric: in the first frame the
blades leave the peel at about 21, 69, 111, 159 ... degrees, in the second at about -1, 47, 89, 137 ...), and the
second frame is the first turned 22.5 degrees clockwise: so the spin reads clockwise, the blades trailing their
curves as a pinwheel's (with even blades a sixteenth of a turn could be either way round). The orange is the same in
both frames. The sprites light the blades as if they rose towards their tips (the blades pointing down and left,
whose rising tops face the sprites' light at the upper right, are the lightest).

Built as such a saw: the orange an ellipsoid (10 x 10 x 9.4, a little flattened as oranges are) of even triangles,
finer where the game's camera sees it, its peel pitted with small dimples (DIMPLES points spread evenly over it, each
pressed in as a round dimple) and painted in bands of shade cut along smooth contours (polish_orb_red.band_split): the
oranges of the sprite, lighter towards the top, darker towards the rim as the slanted camera sees it, a glossy glare
at the upper left (where the game's sun lights it: the sprite lights it from the upper right), the dimples a band
darker where they cross a band's border (the sprite's stipple), every band glowing faintly in its own colour (0.1-0.3)
so that the ball doesn't read dark from the slanted camera; a small stem scar at its top. Round its middle, a little
under it, a steel collar hugging the peel, and the eight blades: each lofted along its curve (THETA: the sprites'
curve, CURVE times), its cross-section a flat diamond (a rounded ridge along the middle, thin edges, a shallow
underside), broad at the collar and tapering to its point, rising SWEEP pixels towards the tip; painted as the
sprite's blades (a light ridge, steel bevels, darker edges, a dark underside), metallic. The blades are spaced as the
sprites space them (FIRST_BLADE + 45 k, SPREAD degrees off either way); the second frame is the first with the blades
and the collar turned 22.5 degrees clockwise about the orange, the orange left as it is.

The whole is built (once for each frame) and cut along the sprites' edges (x = 0, y = 0: polish_arch.cut, the pieces
keep the whole's shading across the cuts; the orange's cuts closed with its flesh (0x7a), the steel's with dark steel:
they show only when a piece is shot away), each piece moved so that its sprite's centre is its origin, its parts
joined into one mesh, every mesh triangulated before the export (polish_k_pod.triangulate: the output is the same
with and without --check).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera. The whole's
origin is the picture's middle (column c is x = c + 0.5 - 24, row r is y = 27.5 - r), the orange's middle there at
z = 0 (a sky object, centred in height as the game centres its other sky models; origin models are drawn at their
origin). The pieces' centres: 78 and 82 (-12, 14), 80 and 84 (12, 14), 116 and 120 (-12, -14), 118 and 122 (12, -14).
models.cfg (model lines unchanged): model orange_saw_tl / _tr / _bl / _br enemies/orange_saw_*.glb origin, sprite x27
78 orange_saw_tl yaw=0 (80 _tr, 116 _bl, 118 _br); model orange_saw_82 / _84 / _120 / _122 enemies/orange_saw_*.glb
origin, frame x27 82 orange_saw_82 (84, 120, 122 the same).

Replaces wave3_ae.py's orange (its section "' 78 80 / 116 118: the bladed orange": SAW, ORANGE_C, ORANGE_R,
orange_saw_whole() and the kit.pieced("orange_saw", ...) registration, "orange" in its kit.PROTECT line, its docstring
paragraph), wave3_at_orange.py (all of it: the frame models were all it built) and wave3_ae_art.py's SUN and SUN_B
(read only by wave3_ae.py; SUN_B by nothing): remove them so that they don't overwrite these models.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes of the whole
of each frame and of each piece against enemy_x27.png), --preview <prefix> (each frame's whole: top and 3/4 views;
--pieces 1 also each piece's), --only <model,...>, --whole <prefix> (the uncut wholes as <prefix>1.glb, <prefix>2.glb,
for looking at).
"""
import math
import os
import sys

import bmesh
import bpy
import mathutils.noise as noise
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_arch import cut  # noqa: E402  (polish_machine_kit.cut without its material indices shifted twice)
from polish_deli_boss import join  # noqa: E402
from polish_orb_red import band_split, smoothstep  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402

# The pieces: model, sprite, its box in the whole (x0, x1, y0, y1); the first frame's and the second's.
BOXES = {"tl": (-24.0, 0.0, 0.0, 28.0), "tr": (0.0, 24.0, 0.0, 28.0), "bl": (-24.0, 0.0, -28.0, 0.0),
         "br": (0.0, 24.0, -28.0, 0.0)}
FRAMES = [
    # (frame, the blades' turn (degrees, counter-clockwise: the second frame's is clockwise), [(model, sprite, box)])
    (1, 0.0, [("orange_saw_tl", 78, BOXES["tl"]), ("orange_saw_tr", 80, BOXES["tr"]),
              ("orange_saw_bl", 116, BOXES["bl"]), ("orange_saw_br", 118, BOXES["br"])]),
    (2, -22.5, [("orange_saw_82", 82, BOXES["tl"]), ("orange_saw_84", 84, BOXES["tr"]),
               ("orange_saw_120", 120, BOXES["bl"]), ("orange_saw_122", 122, BOXES["br"])]),
]
LAYOUTS = {1: (78, 80, 116, 118), 2: (82, 84, 120, 122)}

# --- The orange ----------------------------------------------------------------------------------------------------
RX, RY, RZ = 10.0, 10.0, 9.4          # its radii (the sprite's 20 x 20; a little flattened)
CENTRE = Vector((0.0, 0.0, 0.0))
VIEW_TILT = 20.0                      # the game's camera: degrees off straight down, from the bottom of the screen
T = math.radians(VIEW_TILT)
TOWARDS_VIEW = Vector((0.0, -math.sin(T), math.cos(T)))
VIEW_H = math.hypot(RY * math.cos(T), RZ * math.sin(T))
# The dimples: DIMPLES points spread evenly over the peel (a golden-angle spiral, jittered), each a round dimple
# DIMPLE_R pixels across (give or take DIMPLE_VARY) pressed in up to DIMPLE_DEPTH; a gentle lumpiness.
DIMPLES, DIMPLE_JITTER, DIMPLE_R, DIMPLE_VARY, DIMPLE_DEPTH = 1100, 0.35, 0.42, 0.25, 0.26
LUMPS, LUMP_SCALE = 0.12, 0.22
# The shades (ramp 7, 0-15): the body from the bottom of the view to its top; the glare (its middle in the view's
# (u, v), radius, peak over the body); the rim (where it starts darkening, as a fraction of the view's radius, the
# shade at the edge at the upper left and at the lower right); the side the camera doesn't see.
BODY = (8.75, 9.85)
GLARE, GLARE_R, GLARE_PEAK = (-0.36, 0.44), 0.3, 2.4
RIM_FROM, RIM_EDGE = 0.72, (7.3, 6.2)
BACK = 8.0
# (lowest shade, palette index, emission strength in its own colour)
BANDS = [(-99.0, 0x76, 0.1), (6.5, 0x77, 0.1), (7.5, 0x78, 0.12), (8.5, 0x79, 0.14), (9.5, 0x7a, 0.17),
         (10.5, 0x7b, 0.24), (11.5, 0x7c, 0.3)]
PEEL = dict(metallic=0.0, roughness=0.42)
# The dimples stipple the peel as the sprite's two oranges do: the shade lighter or darker by
# MOTTLE * (MOTTLE_MID - how deep a dimple a point lies in), fading out towards the rim (from MOTTLE_RIM[0] to
# MOTTLE_RIM[1] of the view's radius).
MOTTLE, MOTTLE_MID, MOTTLE_RIM = 1.0, 0.3, (0.7, 0.92)
FLESH = 0x7a                          # the cuts through the orange (the band material of that index)
# The stem scar at its top: a small knob in a dimple, the dark red of the sprite's rim.
STEM = (Vector((-0.6, 0.8)), 0.75, 0x75)

# --- The saw: the collar and the blades -----------------------------------------------------------------------------
FIRST_BLADE = 22.5                    # degrees: the first frame's blades leave the peel at 22.5 + 45 k, the even
SPREAD = 1.5                          # ones SPREAD degrees clockwise of that, the odd ones counter-clockwise
CURVE = 1.1                           # the curve measured from the sprites' blades, a little stronger (the fit)
Z_PLATE = -0.9                        # the blades' and the collar's middle plane at the orange
COLLAR = (9.55, 0.72, 0.5)            # the collar: radius round the orange, its half-width (out) and half-height
R_ROOT, R_TIP = 7.0, 24.7             # each blade from inside the orange to its point (distance from the middle)
SWEEP = 3.4                           # how far the tips rise (pixels)
# Along the blade (distance from the orange's middle): the half-width in plan, the ridge's height over the blade's
# middle plane and the underside's depth under it.
HALF_WIDTH = [(7.0, 3.0), (10.0, 2.95), (11.5, 2.85), (13.0, 2.6), (15.0, 2.15), (17.0, 1.65), (19.0, 1.2),
              (21.0, 0.8), (23.0, 0.42), (24.0, 0.2), (24.7, 0.0)]
RIDGE = [(7.0, 1.7), (11.0, 1.5), (15.0, 1.15), (19.0, 0.8), (23.0, 0.42), (24.7, 0.08)]
UNDER = [(7.0, 0.6), (11.0, 0.55), (15.0, 0.42), (19.0, 0.3), (23.0, 0.16), (24.7, 0.03)]
SECTION = 12                          # points round a blade's cross-section
STATIONS = 44                         # cross-sections along a blade (closer together towards the tip)
STEEL = dict(metallic=0.55, roughness=0.28)
# The steel's materials: (name, palette index)
STEEL_MATS = [("ridge", 0x0d), ("bevel", 0x6b), ("edge", 0x69), ("under", 0x66), ("collar", 0x0b),
              ("collar_dark", 0x08)]


def theta(r):
    """How far round (radians) a blade's middle line is at distance r from the orange's middle, from where it
    leaves the peel (r 10): measured from the sprites' blades, 19-20 degrees at the tip."""
    d = r - 10.0
    return math.radians(CURVE * (0.7044 * d + (0.04325 * d * d if d > 0 else 0.0)))


def interp(table, r):
    """Linear in a table [(r, value)] (clamped)."""
    if r <= table[0][0]:
        return table[0][1]
    for (r0, a), (r1, b) in zip(table, table[1:]):
        if r <= r1:
            t = (r - r0) / (r1 - r0)
            return a + (b - a) * t
    return table[-1][1]


def smooth_interp(table, r):
    """A Catmull-Rom curve through a table [(r, value)]."""
    pts = table
    if r <= pts[0][0]:
        return pts[0][1]
    for i in range(len(pts) - 1):
        r0, r1 = pts[i][0], pts[i + 1][0]
        if r <= r1:
            t = (r - r0) / (r1 - r0)
            p0 = pts[max(i - 1, 0)][1]
            p1, p2 = pts[i][1], pts[i + 1][1]
            p3 = pts[min(i + 2, len(pts) - 1)][1]
            t2, t3 = t * t, t * t * t
            return max(0.0, 0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 +
                                   (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    return pts[-1][1]


# --- Materials -------------------------------------------------------------------------------------------------------

def materials():
    pal = k.level_palette()
    m = {}
    for _, index, glow in BANDS:
        m[index] = k.material(f"orange_peel_{index:02x}", palette=index, emission=pal[index], emission_strength=glow,
                              **PEEL)
    m["stem"] = k.material("orange_stem", palette=STEM[2], metallic=0.0, roughness=0.55, emission=pal[STEM[2]],
                           emission_strength=0.08)
    for name, index in STEEL_MATS:
        m[name] = k.material(f"saw_{name}", palette=index, **STEEL)
    return m


# --- The orange ----------------------------------------------------------------------------------------------------

def view(p):
    """Where the point p of the orange shows in the slanted camera's view: (u, v) (-1..1 across its outline), its
    distance out (a fraction of the outline's radius) and whether the camera sees it."""
    rel = p - CENTRE
    u = rel.x / RX
    v = (rel.y * math.cos(T) + rel.z * math.sin(T)) / VIEW_H
    seen = outward(p).dot(TOWARDS_VIEW) > 0.0
    return u, v, math.hypot(u, v), seen


def outward(p):
    rel = p - CENTRE
    return Vector((rel.x / RX ** 2, rel.y / RY ** 2, rel.z / RZ ** 2)).normalized()


def shade(p):
    u, v, rho, seen = view(p)
    if not seen:
        return BACK
    s = BODY[0] + (BODY[1] - BODY[0]) * smoothstep(-1.0, 1.0, v)
    s += GLARE_PEAK * math.exp(-((u - GLARE[0]) ** 2 + (v - GLARE[1]) ** 2) / GLARE_R ** 2)
    # The rim: towards the shade at the edge, darker at the lower right (the side away from the game's sun).
    away = 0.5 - 0.5 * (-u * 0.70710678 + v * 0.70710678) / max(rho, 1e-6)
    edge = RIM_EDGE[0] + (RIM_EDGE[1] - RIM_EDGE[0]) * away
    return s + (edge - s) * smoothstep(RIM_FROM, 1.0, rho)


_dimples = None


def dimples():
    """The dimples' middles on the peel and their radii, in a KD-tree (the same every run: no random numbers)."""
    global _dimples
    if _dimples is None:
        from mathutils.kdtree import KDTree
        golden = math.pi * (3.0 - math.sqrt(5.0))
        spacing = math.sqrt(4.0 * math.pi / DIMPLES)   # between neighbours, on the unit sphere
        points, radii = [], []
        for i in range(DIMPLES):
            z = 1.0 - 2.0 * (i + 0.5) / DIMPLES
            ring = math.sqrt(max(0.0, 1.0 - z * z))
            a = golden * i
            d = Vector((math.cos(a) * ring, math.sin(a) * ring, z))
            # jittered along the surface by smooth noise, a fraction of the spacing
            jitter = Vector([noise.noise(d * 7.3 + offset) for offset in
                             (Vector((1.7, 0.0, 0.0)), Vector((0.0, 4.1, 0.0)), Vector((0.0, 0.0, 8.9)))])
            d = (d + jitter * spacing * DIMPLE_JITTER).normalized()
            points.append(CENTRE + Vector((d.x * RX, d.y * RY, d.z * RZ)))
            radii.append(DIMPLE_R * (1.0 + DIMPLE_VARY * noise.noise(d * 11.0 + Vector((5.5, 2.2, 9.9)))))
        tree = KDTree(len(points))
        for i, q in enumerate(points):
            tree.insert(q, i)
        tree.balance()
        _dimples = (tree, radii)
    return _dimples


def dimple(p):
    """0-1: how deep a dimple the peel has at p (1 at a dimple's middle)."""
    tree, radii = dimples()
    best = 0.0
    for q, i, d in tree.find_range(p, DIMPLE_R * (1.0 + DIMPLE_VARY) + 0.05):
        t = max(0.0, 1.0 - (d / radii[i]) ** 2)
        best = max(best, t * t)
    return best


def orange_mesh(name):
    """An ellipsoid of even triangles (an icosphere), finer where the camera sees it, dimpled."""
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=4, radius=1.0)

    def point(v):
        d = v.co.normalized()
        return CENTRE + Vector((d.x * RX, d.y * RY, d.z * RZ))

    def seen(v):
        return outward(point(v)).dot(TOWARDS_VIEW) > -0.15

    edges = [e for e in bm.edges if all(seen(v) for v in e.verts)]
    bmesh.ops.subdivide_edges(bm, edges=edges, cuts=1, use_grid_fill=True)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    for v in bm.verts:
        p = point(v)
        n = outward(p)
        lump = LUMPS * noise.noise(p * LUMP_SCALE + Vector((3.1, 7.7, 1.3)))
        depth = DIMPLE_DEPTH * dimple(p) if n.dot(TOWARDS_VIEW) > -0.3 else 0.0
        v.co = p + n * (lump - depth)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def stem(m):
    """The stem scar at the orange's top: a small knob, a ring of five tiny lobes round it."""
    (sx, sy), r, _ = STEM
    top = CENTRE.z + RZ * math.sqrt(max(0.0, 1.0 - (sx / RX) ** 2 - (sy / RY) ** 2))
    parts = [mk.ball("orange_stem_knob", (sx, sy, top + 0.05), (r * 0.55, r * 0.55, 0.32), m["stem"], 12, 6)]
    for i in range(5):
        a = math.radians(90 + 72 * i)
        cx, cy = sx + math.cos(a) * r * 0.75, sy + math.sin(a) * r * 0.75
        parts.append(mk.ball(f"orange_stem_lobe{i}", (cx, cy, top - 0.08), (r * 0.42, r * 0.42, 0.18), m["stem"], 8,
                             4))
    return parts


def surface_point(p):
    """The point of the undimpled ellipsoid in the direction of p from its middle."""
    rel = p - CENTRE
    d = Vector((rel.x / RX, rel.y / RY, rel.z / RZ))
    if d.length < 1e-9:
        return CENTRE + Vector((0.0, 0.0, RZ))
    d.normalize()
    return CENTRE + Vector((d.x * RX, d.y * RY, d.z * RZ))


def stippled_shade(p):
    """The shade with the dimples' stipple: lighter between them, darker in them, as the sprite's two oranges; less
    towards the rim, none on the side the camera doesn't see."""
    q = surface_point(p)
    u, v, rho, seen = view(q)
    value = shade(q)
    if seen:
        fade = 1.0 - smoothstep(MOTTLE_RIM[0], MOTTLE_RIM[1], rho)
        if fade > 0.0:
            value += MOTTLE * fade * (MOTTLE_MID - dimple(q))
    return value


def orange(m):
    peel = orange_mesh("orange_peel")
    values = [stippled_shade(v.co.copy()) for v in peel.data.vertices]
    band_split(peel, values, [(lowest, m[index]) for lowest, index, _ in BANDS])
    k.smooth(peel, 75)
    return [peel] + stem(m)


# --- The saw ---------------------------------------------------------------------------------------------------------

def blade_frame(r, angle0):
    """The blade's middle line at distance r: its point, the direction along it, across it (the counter-clockwise
    side) and up from it."""
    def at(rr):
        a = angle0 + theta(rr)
        rise = SWEEP * max(0.0, (rr - 9.0) / (R_TIP - 9.0)) ** 1.6
        return Vector((rr * math.cos(a), rr * math.sin(a), Z_PLATE + rise))
    p = at(r)
    along = (at(min(r + 0.05, R_TIP)) - at(max(r - 0.05, R_ROOT - 0.5))).normalized()
    across = Vector((-along.y, along.x, 0.0)).normalized()
    up = along.cross(across).normalized()
    return p, along, across, up


def section(j):
    """The cross-section's point j: (across, up) as fractions of the half-width, ridge height and underside depth.
    j 0 is the counter-clockwise edge, SECTION / 4 the ridge, SECTION / 2 the clockwise edge."""
    phi = 2 * math.pi * j / SECTION
    c, s = math.cos(phi), math.sin(phi)
    if s >= -1e-9:     # the top: a flat diamond, its ridge rounded
        return c, (1.0 - abs(c) ** 1.25) ** 1.1
    return c, -(1.0 - abs(c) ** 2.0) ** 0.75


def blade(name, angle0, m):
    """One blade, its root at angle0 (radians) round the orange; painted by where its faces lie on the cross-section."""
    rs = []
    for i in range(STATIONS):
        t = i / (STATIONS - 1)
        rs.append(R_ROOT + (R_TIP - R_ROOT) * (1.0 - (1.0 - t) ** 1.35))
    rings = []
    for r in rs[:-1]:
        p, along, across, up = blade_frame(r, angle0)
        w, top, under = smooth_interp(HALF_WIDTH, r), interp(RIDGE, r), interp(UNDER, r)
        ring = []
        for j in range(SECTION):
            a, h = section(j)
            ring.append(p + across * (a * w) + up * (h * (top if h >= 0 else under)))
        rings.append(ring)
    tip = blade_frame(R_TIP, angle0)[0]
    root, along0, _, _ = blade_frame(R_ROOT, angle0)
    obj = k.loft(name, rings, m["bevel"], start_point=root - along0 * 0.3, end_point=tip)
    # Faces by their place round the cross-section (the loft's quads come first, SECTION a ring).
    quarter = SECTION // 4
    names = {}
    for j in range(SECTION):
        if j in (quarter - 1, quarter):
            names[j] = "ridge"
        elif j in (0, 2 * quarter - 1):
            names[j] = "edge"
        elif j < 2 * quarter:
            names[j] = "bevel"
        else:
            names[j] = "under"
    slots = {}
    count = (len(rings) - 1) * SECTION
    for poly in obj.data.polygons:
        if poly.index < count:
            key = names[poly.index % SECTION]
        elif poly.index < count + SECTION:   # the root's cap, inside the orange
            key = "under"
        else:                                # the point: its faces as the cross-section's
            key = names[(poly.index - count - SECTION) % SECTION]
        mat = m[key]
        if mat.name not in slots:
            slots[mat.name] = mk.slot_of(obj, mat)
        poly.material_index = slots[mat.name]
    return k.smooth(obj, 80)


def collar(m):
    """The steel collar hugging the peel where the blades leave it: a ring of a flattened round section."""
    rc, a, c = COLLAR
    seg, sides = 72, 10
    verts, faces = [], []
    for i in range(seg):
        ang = 2 * math.pi * i / seg
        for j in range(sides):
            phi = 2 * math.pi * j / sides
            rr = rc + a * math.cos(phi)
            verts.append((rr * math.cos(ang), rr * math.sin(ang), Z_PLATE + c * math.sin(phi)))
    for i in range(seg):
        for j in range(sides):
            a0, a1 = i * sides + j, i * sides + (j + 1) % sides
            b0, b1 = ((i + 1) % seg) * sides + j, ((i + 1) % seg) * sides + (j + 1) % sides
            faces.append((a0, b0, b1, a1))
    obj = k.mesh_object("saw_collar", verts, faces, m["collar"])
    k.recalc_normals(obj)
    mk.paint(obj, lambda ctr, n: m["collar_dark"] if n.z < 0.15 else None)
    return k.smooth(obj, 60)


def saw(m, turn):
    """The collar and the eight blades, turned `turn` degrees (counter-clockwise) from the first frame."""
    parts = [collar(m)]
    for i in range(8):
        a = math.radians(FIRST_BLADE + 45.0 * i + (SPREAD if i % 2 else -SPREAD) + turn)
        parts.append(blade(f"saw_blade{i}", a, m))
    if turn:
        rot = Matrix.Rotation(math.radians(turn), 4, "Z")
        parts[0].data.transform(rot)
    return parts


def build_whole(m, turn):
    """The orange and the saw (turned), each a part of its own; returns (orange parts, steel parts)."""
    fruit = orange(m)
    steel = saw(m, turn)
    for obj in fruit + steel:
        mk.apply(obj)
    bpy.context.view_layer.update()
    return fruit, steel


# --- Checks and export ----------------------------------------------------------------------------------------------

def whole_mask(sheet, sprites):
    """The four sprites' silhouettes as the levels put them together: 48 x 56."""
    mask = [[False] * 48 for _ in range(56)]
    for sprite, (c0, r0) in zip(sprites, ((0, 0), (24, 0), (0, 28), (24, 28))):
        for r, row in enumerate(k.sprite_mask(sheet, sprite)):
            for c, v in enumerate(row):
                mask[r0 + r][c0 + c] = v
    return mask


def export_frame(frame, turn, pieces, options, sheet, out):
    only = options["only"].split(",") if "only" in options else None
    wanted = [p for p in pieces if not only or p[0] in only]
    if not wanted and "whole" not in options and "preview" not in options:
        return
    k.reset()
    m = materials()
    fruit, steel = build_whole(m, turn)
    whole = fruit + steel
    triangulate(whole)  # the cuts are the same every run (with and without --check)
    low, high = mk.bounds(whole)
    print("== whole, frame %d: %d triangles, %d materials, x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f" % (
        frame, mk.triangles(whole), len(mk.materials_of(whole)), low.x, high.x, low.y, high.y, low.z, high.z))
    mask = None
    if sheet:
        mask = whole_mask(sheet, LAYOUTS[frame])
        mk.compare("whole, frame %d (x27 %d %d / %d %d)" % ((frame,) + LAYOUTS[frame]), mk.coverage(whole, 48, 56),
                   mask)
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    if "preview" in options:
        mk.preview(options["preview"] + "orange_saw_whole%d" % frame, whole, size=(48, 56), scale=10, distance=1.7)
    if "whole" in options:
        mk.export(whole, options["whole"] + "%d.glb" % frame)
    for name, sprite, box in wanted:
        parts = [cut(src, box, m[FLESH]) for src in fruit] + [cut(src, box, m["under"]) for src in steel]
        parts = [p for p in parts if p is not None]
        mk.transform(parts, Matrix.Translation((-(box[0] + box[1]) / 2, -(box[2] + box[3]) / 2, 0)))
        bpy.context.view_layer.update()
        triangulate(parts)
        parts = [join(parts, name)]
        for src in whole:
            src.hide_render = True
        if mask is not None:
            c0, r0 = int(box[0] + 24), int(28 - box[3])
            mk.compare("%s (x27 %d)" % (name, sprite), mk.coverage(parts, 24, 28),
                       [row[c0:c0 + 24] for row in mask[r0:r0 + 28]])
        mk.report(name, parts, os.path.join(out, name + ".glb"))
        if "preview" in options and options.get("pieces") == "1":
            mk.preview(options["preview"] + name, parts)
        for obj in parts:
            bpy.data.objects.remove(obj)
        for src in whole:
            src.hide_render = False


def build():
    options = k.args()
    out = mk.outdir(options)
    sheet = None
    if "check" in options:
        sheets = options["check"]
        sheet = os.path.join(sheets, "enemy_x27.png") if os.path.isdir(sheets) else sheets
    for frame, turn, pieces in FRAMES:
        export_frame(frame, turn, pieces, options, sheet, out)


if __name__ == "__main__":
    build()
