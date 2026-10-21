"""The grey frame flying in CAMANIS and DIG SITE (sheet 7 sprite 13, 2x2: 21 x 24 pixels in the 24 x 28 cell; sky layer;
enemy 133 of episode 3, 12 in CAMANIS, and enemy 1507 of episode 6, 12 in DIG SITE, which takes CAMANIS' waves; its
animation 13 15 17 15 flashes its two beacons), polished (2026-10-21; it replaces wave3_ac.py's cross_beacon(), boxes
and tubes laid on a block). models.cfg: model cross_beacon enemies/cross_beacon.glb (unchanged) and model
cross_beacon_15 / cross_beacon_17 (new); sprite 7 13 cross_beacon yaw=0 (unchanged); frame 7 15 cross_beacon_15;
frame 7 17 cross_beacon_17. No other enemy (launched ones included) shows 7 13, 15 or 17; none of them is another
sprite's pixels mirrored, turned or in other ramps.

The sprite is its own mirror image across the middle of its height (rows 14-25 are rows 13-2, index for index), and
its coverage is symmetric about column 11 (the shading is not: it is lit from the upper left). As the sprite and its
4x upscales draw the upper half (the lower half is its mirror image):
- a crossbar (columns 6-16 of rows 3-7): a dark round bar lying across the screen, five grey ribs round it (columns
  7, 9, 11, 13 and 15; the outer two the biggest and brightest, rising to row 3, the middle one under the beacon, the
  other two faint), its underside black (row 7);
- the beacon on its outer side (columns 9-13 of rows 2-4): a red lamp, its middle orange (0x7a); in frame 15 it swells
  a pixel outwards (row 1) with a yellow core (0x7d), in frame 17 two pixels (row 0, seven pixels wide at its foot)
  round a white-hot core (0x7f), a pointed flare;
- a bow from each end of the crossbar: grey (one pixel between black outlines), out along the crossbar's line (row
  4), round the corner (rows 5-6) and down the side (columns 1-3 of rows 6-9), then bending in to the middle
  (columns 3-6 of rows 13-14), blue where it bends (rows 10-17: dark blue at its edges, 0x3e where its outer curve
  catches the light at rows 11 and 16), a little thicker there;
- a grey stub from each bow's inner point to the crystal (columns 7-8 of rows 13-14, black round it);
- the crystal between them (columns 8-14 of rows 8-19): a faceted blue gem, two diamonds pinched together at its
  waist (rows 13-14, three pixels wide; seven at rows 10-11 and 16-17), a light streak down its ridge (column 11,
  0x3e where it is widest), its ends against the crossbars' undersides.
Between the bows and the crystal the frame is open (the sky shows through).

Built as a frame of turned and lofted steel: each crossbar a dark bar turned about its own axis across the screen,
rounded at its ends, black underneath, the ribs rings turned round it (proud, rounded; the outer two lit grey, the
middle one grey, the inner two the bar's dark steel); the bows tubes lofted along their paths (their cross-section a
little flatter than round), coloured band by band round them (lit grey on top, grey, then the bar's dark steel down
their sides and black underneath, the sprite's outlines), blue where they bend in (the colours meet along a ring); the
stubs short dark pegs with a grey knob on each; the crystal a gem lofted along its length, a diamond in section (a
flat underside, two facets either side rising to a ridge), its plan the sprite's (its outline included), its left
facets lighter, its right ones darker, its ridge a light streak (a thin glowing bar); the beacons red glass lenses on
the crossbars' outer faces, tilted out, cut into bands of heat (polish_orb_red.band_split) that glow in their own
colours, well under 1 (0.22-0.42 in 13, to 0.32-0.65 in 17; the game's bloom adds to them); each frame's lens swells
as its sprite draws it (frame 17's drawn out to a point). The blues glow a little in their own colours (0.14-0.38),
so the shaded crystal does not read black. The left half is built and mirrored about column 11 (x = -0.5), the upper
half and mirrored across y = 0. All three frames reach from z -0.32 (the outer ribs' undersides) to 6.2 (a speck,
pin(), as polish_glass_hatch.py's: the bigger lenses reach higher than the ribs), so the game, which centres sky
objects in height, keeps them in place.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; origin at the
sprite's centre (pixel 12, 14): column c's middle is x = c + 0.5 - 12, row r's y = 13.5 - r.

Replaces wave3_ac.py's cross_beacon(), which is all wave3_ac.py still builds (its vent went to polish_ice_vent.py):
delete wave3_ac.py (nothing imports it; wave3_ac_ice.py, the bunker and the drill, uses wave3_ac_kit.py, which stays),
and wave3_ac_art.py's XFRAME (read only by wave3_ac.py) and XFRAME_HOT (read by nothing).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each frame's silhouette
against its sprite in enemy_7.png), --preview <prefix>, --only <name,...>, --stats 1 (each part's triangles).
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
from polish_k_pod import triangulate  # noqa: E402
from polish_orb_red import band_split  # noqa: E402

AX = -0.5                       # the sprite's axis (column 11's middle)

# The crossbar (upper one): its axis' y and z, its radii across (y) and up (z), its half-length from the axis (to the
# ends' tips) and the rounding of its ends.
BAR_Y, BAR_Z = 8.6, 2.6
BAR_R = (2.4, 2.3)
BAR_HALF, BAR_END = 5.55, 1.45
# The ribs round it: x from the axis, how far proud, half-width, colour (the outer two the biggest and lit, rising to
# row 3; the middle one under the beacon; the other two faint).
RIB_SEGMENTS = 24
RIBS = [(-4.0, 0.62, 0.55, "grey_lit"), (4.0, 0.62, 0.55, "grey_lit"), (0.0, 0.3, 0.45, "grey"),
        (-2.0, 0.2, 0.36, "bar"), (2.0, 0.2, 0.36, "bar")]
# The left bow's middle line (x from the axis, y; z = BOW_Z) from inside the crossbar's end to its inner point at
# y = 0, and its radius (across; up it is BOW_SQUASH of it) along it, the sprite's outlines included.
BOW = [(-4.8, 9.6), (-6.0, 9.6), (-7.3, 9.4), (-8.4, 8.6), (-8.95, 7.4), (-9.05, 6.0), (-8.9, 4.8), (-8.6, 3.6),
       (-8.1, 2.5), (-7.5, 1.5), (-6.85, 0.6), (-6.55, 0.0)]
BOW_R = [1.35, 1.4, 1.45, 1.5, 1.5, 1.5, 1.55, 1.65, 1.75, 1.8, 1.85, 1.85]
BOW_Z, BOW_SQUASH = 2.45, 0.8
BOW_BLUE = 3.75                 # blue below this |y| (rows 10-17)
BOW_STEP, BOW_SEGMENTS = 0.7, 10
# The stubs from the bows' inner points to the crystal's waist: x from the axis (outer, inner end), radius across
# (y; the sprite's black round the grey peg included), how much lower than wide, z; the grey knob on it (x from the
# axis, radii).
STUB = (-6.5, -1.6, 1.75, 0.6, 2.45)
KNOB = (-3.6, (1.3, 1.15, 0.95))
# The crystal: half-width in plan along y (from its middle, y >= 0; mirrored below; its outline included), its
# underside and its ridge's height over it (at each y: RIDGE[0] + RIDGE[1] * half-width).
CRYSTAL = [(0.0, 2.05), (0.5, 2.15), (1.5, 3.2), (2.5, 4.15), (3.5, 4.0), (4.5, 2.75), (5.5, 2.25), (6.25, 1.6)]
CRYSTAL_Z = 1.05
RIDGE = (1.0, 0.55)
# The beacons: where the lens sits on the crossbar (degrees round it from its top towards its outer side), how far it
# is tilted out (degrees), how deep it is sunk; per frame its radii (across, along the bar's face, out of it), how far
# it is moved outwards along the bar's face, how pointed its outer half is (0 round, 1 a point), where its hottest point lies along it (a
# fraction of its radius outwards), and its bands of heat (lowest heat, palette index, glow).
LENS_AT, LENS_TILT, LENS_SINK = 52.0, 48.0, 0.25
LENS_INNER = 0.65               # the lens' inner half is this much shorter than its outer half
FRAMES = [
    ("cross_beacon", 13, dict(radii=(2.4, 1.65, 1.25), out=0.3, point=0.0, hot=0.0,
                              bands=[(-9.0, 0x74, 0.22), (0.3, 0x76, 0.28), (0.52, 0x78, 0.34), (0.72, 0x7a, 0.42)])),
    ("cross_beacon_15", 15, dict(radii=(2.55, 2.15, 1.45), out=0.9, point=0.15, hot=0.15,
                                 bands=[(-9.0, 0x75, 0.26), (0.26, 0x77, 0.33), (0.46, 0x79, 0.4),
                                        (0.64, 0x7b, 0.48), (0.8, 0x7d, 0.56)])),
    ("cross_beacon_17", 17, dict(radii=(3.4, 2.6, 1.6), out=1.15, point=0.85, hot=0.3,
                                 bands=[(-9.0, 0x76, 0.32), (0.25, 0x78, 0.42), (0.45, 0x7a, 0.5),
                                        (0.65, 0x7d, 0.58), (0.83, 0x7f, 0.65)])),
]
PIN_Z = 6.2                     # every frame's top (pin())


def materials(bands):
    pal = k.level_palette()

    def steel(name, index, metallic=0.6, roughness=0.32):
        return k.material(name, palette=index, metallic=metallic, roughness=roughness)

    def glow(name, index, strength, roughness=0.18, metallic=0.2):
        return k.material(name, palette=index, metallic=metallic, roughness=roughness, emission=pal[index],
                          emission_strength=strength)
    m = {
        "bar": steel("xbeacon_bar", 0x03, 0.55, 0.36),        # the crossbars, the bows' and stubs' dark sides
        "under": steel("xbeacon_under", 0x01, 0.4, 0.5),      # undersides (the sprite's outlines)
        "grey_lit": steel("xbeacon_grey_lit", 0x0a, 0.3, 0.34),
        "grey": steel("xbeacon_grey", 0x07, 0.45, 0.34),
        "blue_lit": glow("xbeacon_blue_lit", 0x3c, 0.14, 0.2, 0.4),
        "blue": glow("xbeacon_blue", 0x39, 0.22, 0.14, 0.35),  # the bows' blue and the crystal
        "blue_dark": glow("xbeacon_blue_dark", 0x36, 0.15, 0.2, 0.35),
        "streak": glow("xbeacon_streak", 0x3e, 0.38, 0.15, 0.1),
    }
    for _, index, strength in bands:
        m[("lens", index)] = glow("xbeacon_lens_%x" % index, index, strength, 0.2, 0.0)
    return m


# --- Helpers --------------------------------------------------------------------------------------------------

def smoothstep(e0, e1, x):
    t = min(1.0, max(0.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


def interp(table, v):
    """Linear interpolation in a table of (key, value) pairs sorted by key (clamped at its ends)."""
    if v <= table[0][0]:
        return table[0][1]
    for (a, fa), (b, fb) in zip(table, table[1:]):
        if v <= b:
            return fa + (fb - fa) * (v - a) / (b - a)
    return table[-1][1]


def catmull(points, step):
    """A Catmull-Rom curve through 2D or 3D points, sampled about every step along it (the points kept)."""
    pts = [Vector(p) for p in points]
    out = []
    for i in range(len(pts) - 1):
        p0, p1, p2, p3 = pts[max(i - 1, 0)], pts[i], pts[i + 1], pts[min(i + 2, len(pts) - 1)]
        n = max(1, int(math.ceil((p2 - p1).length / step)))
        for j in range(n):
            t = j / n
            t2, t3 = t * t, t * t * t
            out.append(0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 +
                              (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(pts[-1])
    return out


def paint_faces(obj, pick):
    mk.paint(obj, pick)
    return obj


def mirror_objects(objects, matrix, suffix):
    """Mirrored copies of objects (matrix: a reflection), their faces turned the right way out."""
    copies = []
    for obj in objects:
        copy = obj.copy()
        copy.data = obj.data.copy()
        copy.name = obj.name + suffix
        copy.data.name = copy.name
        bpy.context.scene.collection.objects.link(copy)
        copy.data.transform(matrix)
        copy.data.flip_normals()
        copy.data.update()
        copies.append(copy)
    return copies


def mirror_x_about_axis():
    return Matrix.Translation((AX, 0, 0)) @ Matrix.Scale(-1, 4, (1, 0, 0)) @ Matrix.Translation((-AX, 0, 0))


# --- Parts ----------------------------------------------------------------------------------------------------

def crossbar(m):
    """The upper crossbar: a bar turned about its axis across the screen, rounded at its ends, its upper side the
    bar's dark steel, its underside black; the ribs round it."""
    ry, rz = BAR_R
    half, end = BAR_HALF, BAR_END
    # Its profile along x: the radius scale at each x from the axis (a quarter ellipse at each end).
    profile = [(-half, 0.0)] + [(-half + end * (1 - math.cos(math.pi / 2 * i / 6)), math.sin(math.pi / 2 * i / 6))
                                for i in range(1, 7)]
    profile += [(-p[0], p[1]) for p in reversed(profile)]
    segments = 28
    rings = []
    for x, s in profile[1:-1]:
        ring = []
        for j in range(segments):
            a = 2 * math.pi * j / segments
            ring.append(Vector((AX + x, BAR_Y + ry * s * math.cos(a), BAR_Z + rz * s * math.sin(a))))
        rings.append(ring)
    # (The loft runs along +x: its rings are ordered along x.)
    bar = k.loft("crossbar", rings, m["bar"], start_point=(AX - half, BAR_Y, BAR_Z), end_point=(AX + half, BAR_Y, BAR_Z))
    k.smooth(bar, 60)
    paint_faces(bar, lambda c, n: m["under"] if n.z < -0.35 or (n.z < 0.25 and n.y < -0.5) else None)
    parts = [bar]
    for i, (dx, proud, hw, key) in enumerate(RIBS):
        # A ring: its profile across (x from its middle, how far out from the bar's surface), turned about the axis.
        prof = [(-hw, -0.05), (-hw * 0.72, proud * 0.82), (0.0, proud), (hw * 0.72, proud * 0.82), (hw, -0.05)]
        rib_rings = []
        for px, out in prof:
            x = AX + dx + px
            ring = []
            for j in range(RIB_SEGMENTS):
                a = 2 * math.pi * j / RIB_SEGMENTS
                ring.append(Vector((x, BAR_Y + (ry + out) * math.cos(a), BAR_Z + (rz + out) * math.sin(a))))
            rib_rings.append(ring)
        rib = k.loft("rib%d" % i, rib_rings, m[key], cap_start=True, cap_end=True)
        k.smooth(rib, 50)
        paint_faces(rib, lambda c, n: m["under"] if n.z < -0.35 else None)
        parts.append(rib)
    return parts


def bow(m):
    """The left bow: a tube along BOW (its upper half; the lower half is its mirror image across y = 0, built with
    it so the tube runs on through y = 0), coloured in bands round it: lit grey on top, grey and dark grey down its
    sides, black underneath, the blue ones where it bends in."""
    half = [Vector((AX + x, y, BOW_Z)) for x, y in BOW]
    radii_half = list(BOW_R)
    path = half + [Vector((p.x, -p.y, p.z)) for p in reversed(half[:-1])]
    radii = radii_half + list(reversed(radii_half[:-1]))
    pts = catmull(path, BOW_STEP)
    # Radii along the smoothed path: by the nearest control point's y (the path is monotonic in y past its top).
    def radius_at(p):
        best = min(range(len(path)), key=lambda i: (path[i] - p).length)
        return radii[best]
    rs = [radius_at(p) for p in pts]
    # Smooth the radii a little.
    rs = [sum(rs[max(0, i - 2):i + 3]) / len(rs[max(0, i - 2):i + 3]) for i in range(len(rs))]
    segments = BOW_SEGMENTS
    rings = []
    for i, p in enumerate(pts):
        t = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        side = t.cross(Vector((0, 0, 1))).normalized()
        up = side.cross(t).normalized()
        ring = []
        for j in range(segments):
            a = 2 * math.pi * (j + 0.5) / segments
            ring.append(p + (up * math.cos(a) * BOW_SQUASH + side * math.sin(a)) * rs[i])
        rings.append(ring)
    obj = k.loft("bow", rings, m["grey"], start_point=pts[0] - (pts[1] - pts[0]).normalized() * 0.3,
                 end_point=pts[-1] + (pts[-1] - pts[-2]).normalized() * 0.3)
    k.smooth(obj, 70)

    # Blue or grey by the band of faces between two rings (the loft makes them band by band, the end caps last),
    # so the colours meet along a ring.
    blue_band = [abs((pts[i].y + pts[i + 1].y) / 2) < BOW_BLUE for i in range(len(pts) - 1)]
    slots = {}
    for poly in obj.data.polygons:
        band = poly.index // segments
        blue = blue_band[band] if band < len(blue_band) else False
        n = poly.normal
        if n.z > 0.72:
            key = "blue_lit" if blue else "grey_lit"
        elif n.z > 0.38:
            key = "blue" if blue else "grey"
        elif n.z > -0.1:
            key = "blue_dark" if blue else "bar"
        else:
            key = "under"
        if key not in slots:
            slots[key] = mk.slot_of(obj, m[key])
        poly.material_index = slots[key]
    return [obj]


def stub(m):
    """The left stub: a short dark rounded peg along x from the bow's inner point to the crystal's waist (the
    sprite's black round the grey), a grey knob on it (columns 7-8 of rows 13-14), lit on top."""
    x0, x1, r, squash, z = STUB
    length = x1 - x0
    prof = [(0.0, 0.55), (0.3, 0.85), (0.7, 1.0), (length - 0.7, 1.0), (length - 0.3, 0.85), (length, 0.55)]
    segments = 16
    rings = []
    for d, s in prof:
        ring = []
        for j in range(segments):
            a = 2 * math.pi * j / segments
            ring.append(Vector((AX + x0 + d, r * s * math.cos(a), z + r * squash * s * math.sin(a))))
        rings.append(ring)
    obj = k.loft("stub", rings, m["bar"], start_point=(AX + x0 - 0.1, 0, z), end_point=(AX + x1 + 0.1, 0, z))
    k.smooth(obj, 60)
    paint_faces(obj, lambda c, n: m["under"] if n.z < 0.15 else None)
    kx, radii = KNOB
    knob = k.ellipsoid("knob", (AX + kx, 0.0, z + r * squash * 0.55), radii, m["grey"], 20, 10)
    k.smooth(knob, 70)
    paint_faces(knob, lambda c, n: m["grey_lit"] if n.z > 0.25 else m["bar"] if n.z < -0.3 else None)
    return [obj, knob]


def crystal(m):
    """The crystal: a gem lofted along y, a diamond in section (a flat underside, a facet either side rising to the
    ridge), pinched at its waist; its facets lit by the game's sun; the light streak along its ridge."""
    table = CRYSTAL + []
    y_end = table[-1][0]
    ys = [-y_end + 2 * y_end * i / 36 for i in range(1, 36)]
    rings = []
    for y in ys:
        hw = interp(table, abs(y))
        ridge = RIDGE[0] + RIDGE[1] * hw
        z0 = CRYSTAL_Z
        pts = [(hw, z0 + 0.35), (hw * 0.93, z0 + 0.85), (hw * 0.5, z0 + 0.62 * ridge + 0.3), (0.0, z0 + ridge),
               (-hw * 0.5, z0 + 0.62 * ridge + 0.3), (-hw * 0.93, z0 + 0.85), (-hw, z0 + 0.35), (-hw * 0.6, z0),
               (hw * 0.6, z0)]
        rings.append([Vector((AX + x, y, z)) for x, z in pts])
    obj = k.loft("crystal", rings, m["blue"], start_point=(AX, -y_end - 0.2, CRYSTAL_Z + 0.9),
                 end_point=(AX, y_end + 0.2, CRYSTAL_Z + 0.9))
    k.smooth(obj, 24)
    paint_faces(obj, lambda c, n: m["blue_lit"] if n.x < -0.35 and n.z > 0.2 else
                m["blue_dark"] if (n.x > 0.3 and n.z < 0.92) or n.z < 0.0 else None)
    # The light streak along the ridge, thickest where the crystal is widest.
    line = []
    for i in range(25):
        y = -(y_end - 0.9) + 2 * (y_end - 0.9) * i / 24
        hw = interp(table, abs(y))
        line.append((y, hw))
    pts = [Vector((AX, y, CRYSTAL_Z + RIDGE[0] + RIDGE[1] * hw + 0.02)) for y, hw in line]
    radii = [0.16 + 0.12 * smoothstep(1.8, 3.6, hw) for _, hw in line]
    streak = mk.tube("streak", pts, 0.2, m["streak"], 6, radii=radii)
    k.smooth(streak, 60)
    return [obj, streak]


def lens(m, spec):
    """The upper beacon: a glass lens on the crossbar's outer face, tilted up the screen (LENS_TILT): an ellipsoid
    (radii across, along the face and out of it), its outer half drawn out to a point as spec["point"] says; banded
    by heat, hottest at its crown (a little outwards on the pointed one); its inner half sunk into the bar."""
    rx, ry, rz = spec["radii"]
    point = spec["point"]
    obj = k.ellipsoid("lens", (0.0, 0.0, 0.0), (rx, ry, rz), m[("lens", spec["bands"][0][1])], 24, 12)
    for v in obj.data.vertices:
        t = max(0.0, v.co.y / ry)
        v.co.x *= 1.0 - point * 0.62 * t ** 1.4
        v.co.y *= 1.0 + point * 0.35 * t ** 2 if v.co.y > 0 else LENS_INNER
    obj.data.update()
    hot_y = ry * spec["hot"]

    def heat(co):
        d = math.hypot(co.x / rx, (co.y - hot_y) / ry)
        return 0.55 * (1.0 - d) + 0.45 * max(0.0, co.z / rz)
    band_split(obj, [heat(v.co) for v in obj.data.vertices], [(lo, m[("lens", index)]) for lo, index, _ in spec["bands"]])
    # Tilted up the screen and set on the bar's face at LENS_AT (an angle round the bar from its top towards +y).
    a = math.radians(LENS_AT)
    y0 = BAR_Y + BAR_R[0] * math.sin(a)
    z0 = BAR_Z + BAR_R[1] * math.cos(a)
    obj.data.transform(Matrix.Translation((AX, y0 + spec["out"], z0 - LENS_SINK)) @
                       Matrix.Rotation(math.radians(-LENS_TILT), 4, "X"))
    obj.data.update()
    k.smooth(obj, 80)
    return [obj]


def pin(m):
    """A speck at PIN_Z (a triangle a thousandth of a pixel across, over the crystal): every frame reaches as high,
    so all have the same bounds and the game centres them alike."""
    e = 0.001
    return [k.mesh_object("pin", [(AX, 0, PIN_Z), (AX + e, 0, PIN_Z), (AX, e, PIN_Z)], [(0, 1, 2)], m["blue"])]


# --- Build ----------------------------------------------------------------------------------------------------

def build_model(spec):
    k.reset()
    m = materials(spec["bands"])
    upper = crossbar(m) + lens(m, spec)
    lower = mirror_objects(upper, Matrix.Scale(-1, 4, (0, 1, 0)), "_low")
    left = bow(m) + stub(m)
    right = mirror_objects(left, mirror_x_about_axis(), "_r")
    gem = crystal(m) + pin(m)
    for obj in lower + right:
        k.smooth(obj, 60 if "crystal" not in obj.name else 24)
    parts = upper + lower + left + right + gem
    for obj in parts:
        mk.apply(obj)
    triangulate(parts)
    bpy.context.view_layer.update()
    return parts


def build():
    options = k.args()
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    for name, sprite, spec in FRAMES:
        if only and name not in only:
            continue
        parts = build_model(spec)
        if "stats" in options:
            for obj in sorted(parts, key=lambda o: -mk.triangles([o])):
                print("    %-16s %6d" % (obj.name, mk.triangles([obj])))
        if "check" in options:
            sheet = os.path.join(options["check"], "enemy_7.png")
            mk.compare("%s (7 %d)" % (name, sprite), mk.coverage(parts, 24, 28), k.sprite_mask(sheet, sprite))
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        mk.report(name, parts, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, parts)


if __name__ == "__main__":
    build()
