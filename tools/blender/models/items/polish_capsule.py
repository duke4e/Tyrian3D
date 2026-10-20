"""Power-up capsule (the coins sheet's sprites 165 and 203: the front and rear weapon power-ups, values -1 and -2;
2x2, 24 x 28 pixels; about 75 of them in the levels, and the random replacements of 533/534), polished (2026-10-20;
it replaces capsule.py's smooth grey egg with a band and red lights). models.cfg: sprite coins 165/203 capsule
spin=2, and the frames that light it as frame models (below). Not color=sprite: it keeps its own colours.

165 and 203 are the same grey pod (its grey pixels the same, shade for shade): 165 has its red light strips on its
upper half and a red lamp above its middle, a green lamp below it; 203 has them the other way round (the red
strips and lamp below, the green lamp above). The capsule turns (spin), so one model serves both. Their animations
(165 165 165 167 167 167 169 169 169 167 167 167; 203-207 likewise) brighten the lights: the strips and the red
lamp from a dull dark red (0x70-0x75) to orange (167) and yellow-white (169), the green lamp from dark green
(0xc0-0xc3) to bright green (0xce). The grey stays. No other enemy shows these sprites, so the lit frames are frame
models: capsule_167 (for 167 and 205) and capsule_169 (169 and 207), the same pod with its lights brighter. All
three span the same bounds.

As the sprite and its 4x upscales draw it: a ribbed metal pod lying across the screen, 23 x 17 pixels (columns 1-23,
rows 7-23), glossy grey, lit at its upper left; dark grooves round it divide it into ribs, four of them (columns 3, 7,
16, 21) glowing red along their upper half, brightest towards the pod's middle; a narrower middle part (the outline
dips a pixel at its top and bottom, columns 10-13) carries the two lamps.

Built as the pod: a lofted body along X with rounded ends, its cross-sections rounded rectangles (POWER), dipping in
narrow grooves round it (GROOVES) and slimmer round its middle (WAIST); light strips lie in the four grooves on the
upper half, each in three lengths, brighter towards the pod's top; the two lamps are domed lenses in sockets on the
middle part. The grey is palette ramp 0 (glossy, half metallic); the lights glow in their own palette colours
(emission), more in the lit frames.

The pod is centred on the origin (the sprite's centre; the sprite draws it 1.5 pixels lower and half a pixel to
the right), so that it turns in place.

Options after "--": --outdir <dir> (default assets/models/items), --check <sheets dir> (the silhouette against
coins.png), --preview <prefix>, --only <name,...>.
"""
import math
import os
import sys

import bmesh
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_item_kit as kit  # noqa: E402
from polish_item_kit import k  # noqa: E402

# The body: half its length, width (Y) and height (Z); the cross-sections' superellipse power; the ends rounded
# over END (the last END pixels at each end); the grooves (x, half width, depth) and the slimmer middle (|x| below
# WAIST[0], WAIST[1] of the full section).
HALF_X, HALF_Y, HALF_Z = 11.4, 8.3, 6.6
POWER = 2.3
END = 4.6
GROOVES = [(-8.7, 0.45, 0.65), (-4.5, 0.45, 0.65), (4.5, 0.45, 0.65), (8.7, 0.45, 0.65), (-2.2, 0.3, 0.35),
           (2.2, 0.3, 0.35)]
WAIST = (2.2, 0.88)
RING = 40        # points round a cross-section
STEP = 0.9       # pixels between cross-sections (closer in the grooves, the waist and the ends)
# The light strips: in the grooves at these x, round the section from STRIP_FROM to STRIP_TO degrees (0: the
# pod's upper side (+Y) seen from above, 90: its top), in three lengths whose light grows towards the top.
STRIPS_X = (-8.7, -4.5, 4.5, 8.7)
STRIP_FROM, STRIP_TO, STRIP_W = 6.0, 84.0, 0.62
# The lamps: (colour, the angle round the middle section, as the strips'); their lenses' radii across, along the
# section and out (LENS).
LAMPS = [("red", 54.0), ("green", 126.0)]
LENS = (1.15, 1.45, 0.75)

# Where the sprite draws the pod's middle (for the silhouette check).
SPRITE_CENTRE = (0.5, -1.5)
# The frames: (model, sprite, the strips' three lengths' palette indices from the side up, the red lamp's, the
# green lamp's, and how strongly each glows).
FRAMES = [
    ("capsule", 165, (0x71, 0x73, 0x75), 0x74, 0xc3, 0.45),
    ("capsule_167", 167, (0x74, 0x77, 0x7a), 0x79, 0xc8, 0.9),
    ("capsule_169", 169, (0x77, 0x7b, 0x7e), 0x7e, 0xcd, 1.5),
]
BODY = dict(metallic=0.45, roughness=0.22)


def section_scale(x):
    """The cross-section's size at x, as a part of the full section (the rounded ends, the grooves, the waist)."""
    s = 1.0
    end = abs(x) - (HALF_X - END)
    if end > 0:
        s *= math.sqrt(max(0.0, 1.0 - (end / END) ** 2))
    if abs(x) < WAIST[0] - 0.3:
        s *= WAIST[1]
    elif abs(x) < WAIST[0] + 0.3:
        t = (abs(x) - (WAIST[0] - 0.3)) / 0.6
        s *= WAIST[1] + (1 - WAIST[1]) * t
    return s


def groove_depth(x):
    d = 0.0
    for gx, half, depth in GROOVES:
        u = abs(x - gx) / half
        if u < 1:
            d = max(d, depth * (1 - u * u) ** 0.5)
    return d


def section_point(x, a, inset=0.0):
    """The point at angle a (degrees; 0 towards +Y, 90 towards +Z) of the cross-section at x, inset inwards."""
    s = section_scale(x)
    c, sn = math.cos(math.radians(a)), math.sin(math.radians(a))
    y = math.copysign(abs(c) ** (2 / POWER), c) * (HALF_Y * s - groove_depth(x) - inset)
    z = math.copysign(abs(sn) ** (2 / POWER), sn) * (HALF_Z * s - groove_depth(x) - inset)
    return Vector((x, y, z))


def body(mats):
    """The pod: cross-sections along X, closed at the ends; the grooves' faces and the waist's painted."""
    xs = []
    x = -HALF_X + 0.02
    while x < HALF_X - 0.02:
        xs.append(x)
        x += STEP
    xs.append(HALF_X - 0.02)
    for gx, half, _ in GROOVES:  # the grooves' profiles
        xs += [gx + half * u for u in (-1.0, -0.5, 0.0, 0.5, 1.0)]
    xs += [s * (WAIST[0] + d) for s in (-1, 1) for d in (-0.3, 0.3)]
    for s in (-1, 1):  # the rounded ends
        xs += [s * (HALF_X - END * (1 - math.sin(math.radians(a)))) for a in range(0, 90, 15)]
    xs = sorted(set(round(v, 4) for v in xs if abs(v) < HALF_X))
    bm = bmesh.new()
    rings = [[bm.verts.new(section_point(x, 360.0 * j / RING)) for j in range(RING)] for x in xs]
    groove_mat = list(mats).index("groove")
    band_mat = list(mats).index("band")
    for i in range(len(rings) - 1):
        xm = (xs[i] + xs[i + 1]) / 2
        in_groove = any(abs(xm - gx) < half for gx, half, _ in GROOVES)
        for j in range(RING):
            f = bm.faces.new((rings[i][j], rings[i][(j + 1) % RING], rings[i + 1][(j + 1) % RING],
                              rings[i + 1][j]))
            f.material_index = groove_mat if in_groove else band_mat if abs(xm) < WAIST[0] else 0
    for ring, x in ((rings[0], xs[0] - 0.02), (rings[-1], xs[-1] + 0.02)):
        centre = bm.verts.new((x, 0.0, 0.0))
        for j in range(RING):
            bm.faces.new((ring[j], ring[(j + 1) % RING], centre))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    obj = kit.from_bmesh("capsule", bm)
    for m in mats.values():
        obj.data.materials.append(m)
    return k.smooth(obj, 50)


def strip(name, x, a0, a1, mat):
    """A light strip lying in a groove, round the section at x from angle a0 to a1."""
    bm = bmesh.new()
    rows = []
    steps = max(2, int(abs(a1 - a0) / 3))
    for i in range(steps + 1):
        a = a0 + (a1 - a0) * i / steps
        row = [bm.verts.new(section_point(x + dx, a, inset=-0.12)) for dx in (-STRIP_W / 2, 0.0, STRIP_W / 2)]
        # Raised in the middle so the strip is a rounded bar, not a flat ribbon.
        mid = row[1]
        out = Vector((0.0, mid.co.y, mid.co.z)).normalized()
        mid.co += out * 0.12
        rows.append(row)
    for i in range(steps):
        for j in range(2):
            bm.faces.new((rows[i][j], rows[i][j + 1], rows[i + 1][j + 1], rows[i + 1][j]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    obj = kit.from_bmesh(name, bm, mat)
    return k.smooth(obj, 70)


def lamp(name, a, lens_mat, socket_mat):
    """A domed lens in a socket on the middle section at angle a."""
    p = section_point(0.0, a)
    # The surface's normal there: across the section's outline.
    q0, q1 = section_point(0.0, a - 1.0), section_point(0.0, a + 1.0)
    tangent = (q1 - q0).normalized()
    normal = tangent.cross(Vector((1.0, 0.0, 0.0))).normalized()
    if normal.dot(Vector((0.0, p.y, p.z))) < 0:
        normal = -normal
    frame = Matrix((Vector((1.0, 0.0, 0.0)), tangent, normal)).transposed().to_4x4()
    parts = []
    socket = k.ellipsoid(name + "_socket", (0, 0, 0), (LENS[0] + 0.45, LENS[1] + 0.45, LENS[2] + 0.2), socket_mat,
                         20, 8)
    lens = k.ellipsoid(name, (0, 0, 0), (LENS[0], LENS[1], LENS[2] + 0.35), lens_mat, 20, 10)
    for obj, lift in ((socket, -0.35), (lens, 0.05)):
        # Its semi-axes along X, the section's outline and the surface's normal.
        obj.data.transform(Matrix.Translation(p + normal * lift) @ frame)
        k.smooth(obj, 70)
        parts.append(obj)
    return parts


def build():
    opts = kit.options()
    for name, sprite, strips, red, green, glow in FRAMES:
        if not kit.wanted(opts, name):
            continue
        k.reset()
        pal = k.level_palette()
        mats = {"body": k.material("capsule_body", palette=0x0c, **BODY),
                "groove": k.material("capsule_groove", palette=0x03, metallic=0.4, roughness=0.5),
                "band": k.material("capsule_band", palette=0x09, **BODY)}
        light = lambda index, strength: k.material(  # noqa: E731
            f"{name}_light_{index:x}", palette=index, roughness=0.25, emission=pal[index], emission_strength=strength)
        socket = k.material("capsule_socket", palette=0x03, metallic=0.5, roughness=0.4)
        parts = [body(mats)]
        for x in STRIPS_X:
            span = (STRIP_TO - STRIP_FROM) / 3
            for i, index in enumerate(strips):
                parts.append(strip(f"strip_{x}_{i}", x, STRIP_FROM + span * i, STRIP_FROM + span * (i + 1),
                                   light(index, glow * (0.7 + 0.15 * i))))
        for colour, a in LAMPS:
            index = red if colour == "red" else green
            parts += lamp(f"lamp_{colour}", a, light(index, glow * 1.3), socket)
        for obj in parts:
            kit.drop_unused_materials(obj)
        kit.finish(opts, name, parts, sprite, large=True, distance=0.8, shift=SPRITE_CENTRE)


if __name__ == "__main__":
    build()
