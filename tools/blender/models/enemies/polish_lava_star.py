"""The spiked star of glowing lava of BRAINIAC and SQUADRON (sheet 5 sprite 278, 2x2: a 23 x 23 star in the 24 x 28
cell; ground layer; BRAINIAC's enemy 541 shows 278 alone, SQUADRON's 726 pulses 278 278 278 280 280 280 282 282 282
280 280 280), polished (2026-10-19; it replaces wave2_g.py's lava_star(), a crust inflated from the sprite's outline
and painted with its pixels). models.cfg: sprite 5 278 lava_star yaw=0 glow=24:0.25, frame 5 280 lava_star_280,
frame 5 282 lava_star_282 (no other enemy shows sheet 5's 280 or 282).

As the sprite and its 4x upscales draw it: a star of lava lying on the ground, a square (columns 5-19 of rows 5-19)
with a long point out of the middle of each side (to columns 1 and 23, rows 1 and 23), so eight points in all, the
square's corners the four short ones. On it a flower of glowing lobes: a white-hot knob in the middle (rows 10-12),
and round it eight petals, one along each point, raised, glowing orange to yellow along their middles (the sprite's
78-7f), the upper and left ones hottest (the north and west petals white-hot, 7f and 7e), the right one dull (78);
between them dark cracks and red crust (72-75), darker towards the star's edge (its outline 70) and on its lower
half. The frames shrink it: 280 is the same picture 19 pixels across, 282 17 (each about its middle, pixel 12, 12).

The star: a polar mesh round its middle (rings out to the outline, finer towards the edge; the outline's eight
points exact), raised as a low pyramid whose ridges run out to the points (its height a function of how far out
towards the outline a point is), the edge rounded down to the ground, the knob and the petals swelling out of it,
cracks sunk between the petals. The heat painted on it is cut into bands of the sprite's own palette indices (ramp
7), the hot bands glowing in their own colour (polish_orb_red.band_split, as polish_molten_rock.py). The frames are
the same star (the relief made on 278's outline) stretched to their own outlines, each direction from the middle by
its own share (280's square is a little fuller for its size than 278's), and lowered in proportion.

All the frames have the same bounds, z 0 to PIN_Z: each carries a speck at PIN_Z (a triangle a thousandth of a pixel
across, invisible), so that they are tall enough for the game to set them on the ground (it centres ground models
in height on the ground enemies' layer, 4, and lifts them to 0.3 when they would reach lower: half of PIN_Z is more
than 3.7) and every frame is placed alike.

Origin at the sprite's centre (pixel 12, 14); +X right, +Y up the sprite, +Z up from the ground (z = 0); column c is
x = c + 0.5 - 12, row r is y = 13.5 - r.

Replaces wave2_g.py's lava_star() (its @model("lava_star", "5", 278) registration; wave2_g_art.py's E5_278 goes with
it, nothing else uses it): remove it so that it doesn't overwrite these models.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each frame's silhouette
against enemy_5.png), --preview <prefix>, --only <name,...>.
"""
import math
import os
import sys

import bpy
import mathutils.noise as noise
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k, smoothstep  # noqa: E402
from polish_orb_red import band_split  # noqa: E402

CENTRE = Vector((0.5, 1.5))     # the star's middle: pixel 12, 12 (columns 1-23, rows 1-23)
# The outline of each frame round the middle (pixel edges): the long points' reach, the square's half-size, where a
# long point's edge meets the square's (from the point's axis); the square's edges between there and its corners
# curve in by SAG of its half-size.
SHAPE_278 = (11.5, 7.5, 4.0)    # columns 1-23 and rows 1-23, the square columns 5-19 and rows 5-19
SHAPE_280 = (9.5, 6.5, 3.0)     # columns 3-21, the square 6-18
SHAPE_282 = (8.5, 5.5, 3.0)     # columns 4-20, the square 7-17
SAG = 0.045

# The pyramid: its height at the middle (before the knob), at RIM_T of the way out (where the edge's rounding
# begins), the rounding down to the ground.
TOP_Z, RIM_Z, RIM_T = 2.7, 1.0, 0.9
# The knob in the middle: its centre (from the star's middle), radius of its swell, height, hot core's radius.
KNOB = (Vector((-0.1, 0.35)), 2.3, 1.6, 1.55)
# The petals: (direction in degrees, peak heat, swell), along the eight points; each from PETAL_FROM to PETAL_TO of
# its point's reach, PETAL_W wide (half-width at its broadest; the corner ones a little narrower).
PETALS = [(90, 1.22, 1.25), (45, 0.98, 1.05), (0, 0.7, 0.95), (-45, 0.98, 1.05),
          (-90, 0.84, 1.1), (-135, 0.72, 1.0), (180, 1.16, 1.25), (135, 0.92, 1.05)]
PETAL_FROM, PETAL_TO, PETAL_W = 0.22, 0.86, 1.7
CRACK_W, CRACK_DEPTH = 0.45, 0.55
CRUST_HEAT = 0.27               # the crust between the petals (73-74), cooler on the lower half and at the edge

# The heat bands: (lowest heat, palette index, emission strength in the palette colour).
BANDS = [
    (-9.0, 0x70, 0.0),
    (0.1, 0x71, 0.0),
    (0.17, 0x72, 0.1),
    (0.24, 0x73, 0.22),
    (0.32, 0x74, 0.34),
    (0.41, 0x75, 0.46),
    (0.5, 0x76, 0.58),
    (0.58, 0x77, 0.72),
    (0.66, 0x78, 0.86),
    (0.74, 0x79, 1.0),
    (0.82, 0x7a, 1.2),
    (0.92, 0x7b, 1.45),
    (1.02, 0x7c, 1.7),
    (1.12, 0x7f, 2.4),
]
# The rings of the mesh: (share of the way out to the outline, vertices round it).
RINGS = [(0.06, 12), (0.12, 24), (0.19, 24), (0.26, 48), (0.33, 48), (0.4, 48), (0.47, 96), (0.54, 96),
         (0.61, 96), (0.68, 96), (0.75, 96), (0.81, 96), (0.86, 96), (0.9, 96), (0.94, 96), (0.97, 96), (0.99, 96),
         (1.0, 96)]
PIN_Z = 7.6

# The frames: (model, sprite, outline).
FRAMES = [("lava_star", 278, SHAPE_278), ("lava_star_280", 280, SHAPE_280), ("lava_star_282", 282, SHAPE_282)]


# --- The outline -----------------------------------------------------------------------------------------------

def outline(shape):
    """A frame's outline round the middle, counter-clockwise from the right point: each quarter the long point,
    the notch where its edge meets the square, the square's edge (curving in a little) to its corner and on to the
    next notch."""
    tip, square, notch = shape
    sag = SAG * square
    quarter = [(tip, 0.0), (square, notch), (square - sag, (notch + square) / 2), (square, square),
               ((notch + square) / 2, square - sag), (notch, square)]
    points = []
    for q in range(4):
        c, s = math.cos(q * math.pi / 2), math.sin(q * math.pi / 2)
        points += [Vector((x * c - y * s, x * s + y * c)) for x, y in quarter]
    return points


OUTLINE = outline(SHAPE_278)    # the relief is made on the first frame's outline


def outline_radius(theta, polygon=OUTLINE):
    """How far the outline is from the middle in the direction theta."""
    d = Vector((math.cos(theta), math.sin(theta)))
    best = 0.0
    for a, b in zip(polygon, polygon[1:] + polygon[:1]):
        e = b - a
        den = d.x * e.y - d.y * e.x
        if abs(den) < 1e-12:
            continue
        t = (a.x * e.y - a.y * e.x) / den       # along the ray
        u = (a.x * d.y - a.y * d.x) / den       # along the edge
        if -1e-9 <= u <= 1 + 1e-9 and t > best:
            best = t
    return best


def notch_angles():
    """The directions of the notches between the points (where the cracks run)."""
    return [math.atan2(p.y, p.x) for i, p in enumerate(OUTLINE) if i % 6 in (1, 5)]


NOTCHES = notch_angles()


# --- The relief and its heat -----------------------------------------------------------------------------------

def angle_between(a, b):
    return (a - b + math.pi) % (2 * math.pi) - math.pi


def relief(p):
    """The star's height and heat (0: its dark edge, about 0.27 its red crust, 1 and more white-hot) at p (from its
    middle, on the first frame's outline)."""
    tip = SHAPE_278[0]
    r = p.length
    theta = math.atan2(p.y, p.x)
    t = r / outline_radius(theta)
    # The pyramid, its ridges out to the points; the edge rounded down to the ground.
    if t <= RIM_T:
        z = RIM_Z + (TOP_Z - RIM_Z) * ((RIM_T - t) / RIM_T) ** 1.25
    else:
        z = RIM_Z * math.sqrt(max(0.0, 1 - ((t - RIM_T) / (1 - RIM_T)) ** 2))
    q = Vector((p.x * 0.8, p.y * 0.8, 0.5))
    z += (0.16 * noise.noise(q) + 0.07 * noise.noise(q * 2.7 + Vector((5.0, 1.0, 2.0)))) * smoothstep(1.0, 0.85, t)
    heat = CRUST_HEAT + 0.08 * noise.noise(q * 1.6 + Vector((3.0, 7.0, 1.0))) + 0.06 * p.y / tip
    # The cracks from the knob out towards the notches.
    for a in NOTCHES:
        da = angle_between(theta, a)
        if abs(da) < math.pi / 2:
            w = r * math.sin(abs(da))
            along = smoothstep(1.6, 3.0, r) * smoothstep(0.92, 0.7, t)
            crack = math.exp(-(w / CRACK_W) ** 2) * along
            z -= CRACK_DEPTH * crack
            heat -= 0.22 * crack
    # The petals: lobes along the points, broadest a little inside their middles, narrowing to the tips.
    for degrees, peak, swell in PETALS:
        a = math.radians(degrees)
        da = angle_between(theta, a)
        if abs(da) >= math.pi / 2:
            continue
        reach = outline_radius(a)
        along = r * math.cos(da) / reach
        w = r * math.sin(abs(da))
        corner = degrees % 90 != 0
        mid, half = (PETAL_FROM + PETAL_TO) / 2, (PETAL_TO - PETAL_FROM) / 2
        u = (along - mid) / half
        width = PETAL_W * (0.85 if corner else 1.0) * (1.0 - 0.35 * max(0.0, u))
        lobe = math.exp(-u * u * (1.4 if u < 0 else 1.0) - (w / width) ** 2)
        z += swell * lobe ** 1.2
        heat = max(heat, heat + (peak - heat) * lobe ** 1.25)
    # The knob in the middle, white-hot at its core.
    centre, radius, height, core = KNOB
    d = (p - centre).length
    z += height * math.exp(-(d / radius) ** 2)
    heat = max(heat, heat + (1.24 - heat) * math.exp(-(d / core) ** 2))
    # The edge: darker crust towards the outline (the sprite's outline 70).
    heat -= (heat + 0.05) * smoothstep(0.8, 1.0, t) * 0.95
    return max(0.0, z), heat


# --- The mesh ------------------------------------------------------------------------------------------------------

def stitch(inner, outer, faces):
    """Faces between two rings of vertex indices (counter-clockwise, the outer one as many or twice as many)."""
    n, m = len(inner), len(outer)
    if m == n:
        for j in range(n):
            faces.append((inner[j], outer[j], outer[(j + 1) % m], inner[(j + 1) % n]))
    else:
        assert m == 2 * n
        for j in range(n):
            a, b = inner[j], inner[(j + 1) % n]
            o0, o1, o2 = outer[2 * j], outer[2 * j + 1], outer[(2 * j + 2) % m]
            faces += [(a, o0, o1), (a, o1, b), (b, o1, o2)]


def star(mats, shape):
    """The star: the polar mesh raised as its relief, its faces cut into heat bands, the bottom flat on the ground;
    for another frame the relief made on the first frame's outline is stretched to the frame's (each direction from
    the middle by its own share) and lowered in proportion."""
    polygon = outline(shape)
    height = shape[0] / SHAPE_278[0]
    vertices, faces, values = [], [], []

    def add(p):
        z, heat = relief(p)
        theta = math.atan2(p.y, p.x)
        stretch = outline_radius(theta, polygon) / outline_radius(theta) if p.length > 0 else 1.0
        vertices.append((CENTRE.x + p.x * stretch, CENTRE.y + p.y * stretch, z * height))
        values.append(heat)
        return len(vertices) - 1
    middle = add(Vector((0.0, 0.0)))
    rings = []
    for t, count in RINGS:
        ring = []
        for j in range(count):
            theta = 2 * math.pi * j / count
            d = Vector((math.cos(theta), math.sin(theta)))
            ring.append(add(d * outline_radius(theta) * t))
        rings.append(ring)
    first = rings[0]
    faces += [(middle, first[j], first[(j + 1) % len(first)]) for j in range(len(first))]
    for inner, outer in zip(rings, rings[1:]):
        stitch(inner, outer, faces)
    edge = rings[-1]
    faces.append(tuple(reversed(edge)))  # the bottom, on the ground
    obj = k.mesh_object("lava_star", vertices, faces)
    k.recalc_normals(obj)
    band_split(obj, values, [(lowest, mats[index]) for lowest, index, _ in BANDS])
    return k.smooth(obj, 50)


def materials():
    glow = k.level_palette()
    return {index: k.material(f"lava_star_{index:x}", palette=index, metallic=0.05, roughness=0.36,
                              emission=glow[index] if strength > 0 else None, emission_strength=strength)
            for _, index, strength in BANDS}


def pin(mat):
    """A speck at PIN_Z (a triangle a thousandth of a pixel across, over the middle): every frame reaches as high,
    so all have the same bounds and the game sets them on the ground."""
    e = 0.001
    x, y = CENTRE
    return k.mesh_object("pin", [(x, y, PIN_Z), (x + e, y, PIN_Z), (x, y + e, PIN_Z)], [(0, 1, 2)], mat)


def build():
    options = k.args()
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    for name, sprite, shape in FRAMES:
        if only and name not in only:
            continue
        k.reset()
        mats = materials()
        parts = [star(mats, shape), pin(mats[0x70])]
        bpy.context.view_layer.update()
        if "check" in options:
            mk.compare("%s (5 %d)" % (name, sprite), mk.coverage(parts, 24, 28),
                       k.sprite_mask(os.path.join(options["check"], "enemy_5.png"), sprite))
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        mk.report(name, parts, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, parts)


if __name__ == "__main__":
    build()
