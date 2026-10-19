"""CORE's glossy bubble of lava on the ground (sheet 3 sprite 128, 2x2: 24 x 28 pixels; ground layer; enemy 253
wobbles 128 128 128 128 130 130 130 130 132 132 132 132 130 130 130 130, enemy 256 swells 128 130 132 and bursts),
polished (2026-10-19; it replaces wave3_n.py's lava_bubble(), a dark ellipsoid with a lip and a drop per pixel round
its foot, and wave3_ar_beasts.py's lava_bubble_130 and _132, the same with the frames' drops). models.cfg: sprite 3
128 lava_bubble yaw=0 glow=22:0.2:118, frame 3 130 lava_bubble_130, frame 3 132 lava_bubble_132 (no other enemy
shows sheet 3's 130 or 132).

As the sprites and their 4x upscales draw it: a dome of dark red lava (the sprite's ramp 7, 70-74), glossy, a white
glare on its upper left (7f, rows 7-10 of 128 round columns 7-10, a yellow and orange halo round it), its right side
in shadow (70-71) with a lighter rim along its right edge (73, columns 20-21), its foot warm where it meets the
ground in front (73-77), and lava splashed round its foot: lumps and drops at its sides and in front of it (rows
17-26), some still glowing (74-78). Round at the top (a circle of 11 pixels round pixel 11.5, 13.5), fuller below.
The frames swell it: in 130 it is a pixel higher up the screen and a pixel narrower, in 132 another (rows 1-19,
columns 2-21), the splashes round its foot thrown about: in 130 drops flung further out in front (rows 24-27), in 132
lava running down its front into a glowing drip (columns 6-15 of rows 21-26).

The bubble: a dome lofted round its axis, its plan a superellipse (rounder at the back, fuller in front), its
widest a little above the ground and its foot flaring out to the ground in a meniscus, a little lumpy. The light the
sprite paints on it is cut into bands of its palette indices (polish_orb_red.band_split): the glare (glowing, hot
lava under a thin skin, where the game's sun puts a highlight too), the rim along its right edge, the warm foot in
front, darker at its base behind; it is glossy and glows a little in its own colour all over, so that the game's
slanted camera, which sees it mostly from above, shows it red rather than black. The splashes are flattened lumps
of lava on the ground, each placed and sized as the frame draws them (its pixels outside the dome, grouped), those
against the foot drawn out to it; a dark crust (rougher) round a glowing top where the sprite draws them hot. One
model per frame, its dome taller each time (8, 9.2 and 10.4 pixels) and further up the screen, its splashes the
frame's own.

All the frames have the same bounds, z 0 to PIN_Z: each carries a speck at PIN_Z (a triangle a thousandth of a pixel
across, invisible) above the tallest dome, so that the game sets every frame on the ground alike (it centres ground
models in height on the ground enemies' layer, 4, and lifts them to 0.3 when they would reach lower).

Origin at the sprite's centre (pixel 12, 14); +X right, +Y up the sprite, +Z up from the ground (z = 0); column c is
x = c + 0.5 - 12, row r is y = 13.5 - r.

Replaces wave3_n.py's lava_bubble() (its @n.model("lava_bubble", ...) registration; wave3_n_art.py's DOME goes with
it if nothing else uses it) and wave3_ar_beasts.py's lava_bubble() with its n.model(f"lava_bubble_{sprite}", ...)
loop (wave3_ar_art.py's LAVA_130 and LAVA_132 go with them): remove them so that they don't overwrite these models.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each frame's silhouette
against enemy_3.png), --preview <prefix>, --only <name,...>.
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

# The dome: where its widest ring is (above the ground), how far its foot flares out to the ground (a share of its
# radius, behind and in front), its plan's power (2: an ellipse) behind and in front.
WIDEST_Z = 0.9
FLARE_BACK, FLARE_FRONT = 0.035, 0.09
POWER_BACK, POWER_FRONT = 2.0, 2.6
SEGMENTS, CAP_STEPS, FOOT_STEPS = 64, 14, 5
# The glare (a share of the dome's radii from its middle, its half-sizes), the rim light along the right edge (the
# directions it covers round from +X, degrees, and the normals' z it lies at).
GLARE, GLARE_SIZE = Vector((-0.33, 0.2)), Vector((0.17, 0.15))
RIM_SPREAD, RIM_Z = 62.0, (0.12, 0.62)

# The tone painted on the dome and the splashes: (lowest tone, palette index, emission strength in its colour).
BANDS = [
    (-9.0, 0x70, 0.1),
    (0.1, 0x71, 0.2),
    (0.2, 0x72, 0.3),
    (0.36, 0x73, 0.42),
    (0.46, 0x74, 0.55),
    (0.56, 0x76, 0.8),
    (0.66, 0x77, 1.0),
    (0.78, 0x79, 1.3),
    (0.9, 0x7a, 1.55),
    (1.0, 0x7d, 2.0),
    (1.1, 0x7f, 2.6),
]
BODY = 0.29                     # the dome's tone (72)

# The frames: the dome's middle (x, y), its foot's reach in plan (to the sides, behind, in front), its height; the
# splashes round its foot, as the frame draws them (its pixels outside the dome, grouped): (x, y, half-length out
# from the dome, half-width, how many pixels, the hottest shade in them).
FRAMES = [
    ("lava_bubble", 128, (0.0, 0.5), (11.0, 10.5, 9.3), 8.0, [
        (-10.8, -4.5, 1.4, 1.2, 3, 0x74),      # the lumps at the left (columns 0-2, rows 17-20)
        (-10.0, -6.0, 1.2, 1.2, 4, 0x75),
        (10.5, -4.7, 1.2, 1.6, 5, 0x72),       # at the right (columns 21-23, rows 17-19)
        (9.7, -8.3, 1.9, 1.6, 6, 0x73),        # at the lower right (columns 20-22, rows 20-23)
        (-5.5, -8.5, 1.0, 1.4, 3, 0x73),       # on the foot in front (row 22)
        (5.5, -8.8, 1.2, 1.4, 4, 0x74),
        (-7.8, -9.9, 1.7, 1.9, 8, 0x76),       # and below it (rows 22-26)
        (-3.9, -10.3, 1.4, 1.3, 5, 0x76),
        (0.2, -10.5, 1.5, 1.5, 7, 0x72),
        (5.0, -11.0, 1.2, 1.2, 4, 0x76),
        (-1.9, -11.3, 1.5, 1.2, 5, 0x73),
        (-0.5, -7.5, 0.9, 0.8, 2, 0x77),       # the hot spot on the foot (column 11, row 21)
    ]),
    ("lava_bubble_130", 130, (-0.4, 1.0), (10.6, 11.0, 9.6), 9.2, [
        (-10.2, -4.8, 1.0, 1.6, 4, 0x75),      # at the left (columns 1-2, rows 16-19)
        (10.0, -4.5, 0.9, 1.6, 4, 0x75),       # at the right (columns 20-22, rows 17-19)
        (7.5, -7.7, 1.2, 1.9, 6, 0x76),        # at the lower right (columns 18-20, rows 20-22)
        (-7.3, -7.7, 1.0, 2.3, 5, 0x78),       # at the lower left (columns 3-6, rows 20-22)
        (-3.5, -8.5, 0.6, 0.6, 1, 0x70),       # on the foot in front (row 22)
        (3.0, -8.5, 0.7, 1.0, 2, 0x71),
        (-0.5, -10.5, 0.6, 0.6, 1, 0x74),      # flung out in front (rows 24-27)
        (4.7, -11.1, 1.2, 1.6, 5, 0x74),
        (-8.0, -12.0, 1.2, 1.2, 4, 0x73),
        (5.0, -12.5, 0.7, 1.0, 2, 0x71),
        (0.3, -12.9, 1.0, 1.5, 5, 0x73),
    ]),
    ("lava_bubble_132", 132, (0.0, 1.6), (10.1, 11.4, 9.8), 10.4, [
        (-10.7, -2.1, 1.3, 1.9, 5, 0x75),      # at the left (columns 0-1, rows 14-17)
        (-9.0, -5.5, 0.9, 0.8, 2, 0x76),       # (columns 2-3, row 19)
        (-10.8, -7.8, 0.9, 1.2, 3, 0x74),      # thrown out at the left (columns 0-1, rows 21-22)
        (-7.5, -11.5, 0.6, 0.6, 1, 0x73),      # (column 4, row 25)
        (9.3, -5.1, 1.4, 1.7, 5, 0x76),        # at the right (columns 20-21, rows 17-20)
        (6.0, -7.5, 0.8, 0.9, 2, 0x77),        # at the lower right (columns 17-18, row 21)
        (-5.0, -8.5, 1.2, 1.4, 4, 0x77),       # the drip running down its front (columns 6-15, rows 21-26)
        (-2.7, -9.2, 1.6, 1.5, 6, 0x75),
        (0.5, -9.0, 1.0, 1.5, 6, 0x7a),
        (3.0, -9.0, 1.1, 1.1, 4, 0x74),
        (2.2, -11.2, 1.5, 1.7, 6, 0x75),
        (0.1, -11.3, 1.5, 1.0, 5, 0x72),
        (5.5, -10.5, 0.6, 0.6, 1, 0x74),       # a drop (column 17, row 24)
    ]),
]
# The tone of a splash by the hottest shade the sprite draws in it.
SPLASH_TONE = {0x70: 0.15, 0x71: 0.2, 0x72: 0.28, 0x73: 0.4, 0x74: 0.5, 0x75: 0.56, 0x76: 0.62, 0x77: 0.7,
               0x78: 0.76, 0x7a: 0.92}
PIN_Z = 10.9


# --- The dome ------------------------------------------------------------------------------------------------------

def plan_point(angle, power):
    c, s = math.cos(angle), math.sin(angle)
    return (math.copysign(abs(c) ** (2 / power), c), math.copysign(abs(s) ** (2 / power), s))


def profile(height):
    """The dome's profile from its top down: (share of its plan radius out, z, share of the foot's flare out): the cap
    down to its widest ring, then the foot curving out to the ground."""
    out = []
    for i in range(CAP_STEPS + 1):
        a = (math.pi / 2) * i / CAP_STEPS
        out.append((math.sin(a), WIDEST_Z + (height - WIDEST_Z) * math.cos(a), 0.0))
    for i in range(1, FOOT_STEPS + 1):
        u = (math.pi / 2) * i / FOOT_STEPS
        out.append((1.0, WIDEST_Z * (1 - math.sin(u)), 1 - math.cos(u)))
    return out


def dome(centre, radii, height):
    """The dome's surface (its bottom closed on the ground) and the tone painted on it; radii: (x, back, front), the
    foot's reach in plan."""
    cx, cy = centre
    rows = profile(height)
    vertices, faces = [(cx, cy, height)], []
    for i, (rho, z, flare) in enumerate(rows[1:], 1):
        for j in range(SEGMENTS):
            a = 2 * math.pi * j / SEGMENTS
            front = smoothstep(0.0, 0.5, -math.sin(a))
            u, v = plan_point(a, POWER_BACK + (POWER_FRONT - POWER_BACK) * front)
            reach = 1 + FLARE_BACK + (FLARE_FRONT - FLARE_BACK) * front
            out = rho * (1 + (reach - 1) * flare) / reach
            ry = radii[2] if v < 0 else radii[1]
            # A little lumpy, more so at the foot.
            wobble = 1.0 + (0.012 + 0.03 * (1 - z / height)) * noise.noise(Vector((u * 2.2, v * 2.2, z * 0.35)))
            vertices.append((cx + radii[0] * out * u * wobble, cy + ry * out * v * wobble, z))
    n = SEGMENTS
    faces += [(0, 1 + j, 1 + (j + 1) % n) for j in range(n)]
    for i in range(len(rows) - 2):
        a0, a1 = 1 + i * n, 1 + (i + 1) * n
        faces += [(a0 + j, a1 + j, a1 + (j + 1) % n, a0 + (j + 1) % n) for j in range(n)]
    last = 1 + (len(rows) - 2) * n
    faces.append(tuple(last + j for j in reversed(range(n))))   # the bottom, on the ground
    obj = k.mesh_object("dome", vertices, faces)
    k.recalc_normals(obj)
    obj.data.update()
    tones = []
    for vert in obj.data.vertices:
        tones.append(dome_tone(vert.co, vert.normal, centre, radii, height))
    return obj, tones


def dome_tone(co, normal, centre, radii, height):
    """The tone painted at a point of the dome (its normal pointing out)."""
    cx, cy = centre
    px = (co.x - cx) / radii[0]
    py = (co.y - cy) / (radii[1] if co.y > cy else radii[2])
    tone = BODY + 0.025 * noise.noise(Vector((px * 3.0, py * 3.0, 0.7)))
    # Darker on the side away from the light (the sprite's lower right, 70-71).
    if normal.length > 0.5:
        tone -= 0.15 * smoothstep(0.1, 0.65, 0.7 * normal.x - 0.7 * normal.y)
    # The glare on its upper left: white-hot in the middle, a yellow and orange halo round it.
    if co.z > 0.45 * height:
        g = math.exp(-((px - GLARE.x) / GLARE_SIZE.x) ** 2 - ((py - GLARE.y) / GLARE_SIZE.y) ** 2)
        tone = max(tone, tone + (1.2 - tone) * g ** 1.3)
    # The rim light along its right edge.
    if normal.length > 0.5:
        across = math.degrees(math.atan2(normal.y, normal.x))
        side = smoothstep(RIM_SPREAD, RIM_SPREAD * 0.55, abs(across))
        band = smoothstep(RIM_Z[0], RIM_Z[0] + 0.12, normal.z) * smoothstep(RIM_Z[1], RIM_Z[1] - 0.15, normal.z)
        tone = max(tone, 0.4 * side * band + tone * (1 - side * band))
    # The foot: warm in front where it meets the ground (hot spots in it), dark behind and at the sides.
    foot = smoothstep(2.2, 0.3, co.z)
    if foot > 0:
        front = smoothstep(-0.2, -0.75, py)
        heat = 0.38 + 0.2 * noise.noise(Vector((px * 5.0, py * 5.0, 2.0))) + 0.12 * front
        tone = tone * (1 - foot) + (heat * front + 0.12 * (1 - front)) * foot
    return tone


# --- The splashes --------------------------------------------------------------------------------------------------

def splash(name, x, y, length, width, height, tone, towards, attached, seed):
    """A flattened lump of lava on the ground, stretched away from the dome (towards: the dome's middle), lumpy, its
    inner end drawn out to the dome's foot when it lies against it (attached); a crust round a hot top when it is
    hot. Returns the object and its vertices' tones."""
    away = (Vector((x, y)) - Vector(towards)).normalized()
    side = Vector((-away.y, away.x))
    offset = Vector((seed * 3.1, seed * 1.7, 0.5))
    segments, rings = 14, 5
    vertices, values = [], []

    def add(d):
        plan = 1.0 + 0.22 * noise.noise(Vector((d.x, d.y, 0.0)) * 1.3 + offset)
        lump = 1.0 + 0.18 * noise.noise(d * 2.1 + offset)
        along = d.x * length * plan * (1.9 if attached and d.x < 0 else 1.0)
        p = Vector((x, y)) + away * along + side * (d.y * width * plan)
        vertices.append((p.x, p.y, d.z ** 0.8 * height * lump))
        if tone > 0.45:  # a dark crust round a glowing top
            values.append(0.14 + (tone + 0.08 - 0.14) * smoothstep(0.45, 0.95, d.z) ** 1.5)
        else:
            values.append(0.06 + (tone - 0.06) * smoothstep(0.2, 1.0, d.z))
    for i in range(rings):
        e = (math.pi / 2) * i / rings
        for j in range(segments):
            a = 2 * math.pi * j / segments
            add(Vector((math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e))))
    add(Vector((0.0, 0.0, 1.0)))
    top = len(vertices) - 1
    faces = []
    for i in range(rings - 1):
        for j in range(segments):
            a, b = i * segments + j, i * segments + (j + 1) % segments
            faces.append((a, b, b + segments, a + segments))
    last = (rings - 1) * segments
    faces += [(last + j, last + (j + 1) % segments, top) for j in range(segments)]
    faces.append(tuple(reversed(range(segments))))  # the bottom, on the ground
    obj = k.mesh_object(name, vertices, faces)
    k.recalc_normals(obj)
    return obj, values


def foot_distance(x, y, centre, radii):
    """Roughly how far (x, y) lies outside the dome's foot."""
    cx, cy = centre
    a = math.atan2(y - cy, x - cx)
    front = smoothstep(0.0, 0.5, -math.sin(a))
    u, v = plan_point(a, POWER_BACK + (POWER_FRONT - POWER_BACK) * front)
    ry = radii[2] if v < 0 else radii[1]
    reach = math.hypot(radii[0] * u, ry * v)
    return math.hypot(x - cx, y - cy) - reach


# --- Build ---------------------------------------------------------------------------------------------------------

def materials():
    glow = k.level_palette()
    return {index: k.material(f"lava_bubble_{index:x}", palette=index, metallic=0.0, roughness=0.3,
                              emission=glow[index], emission_strength=strength)
            for _, index, strength in BANDS}


def bands(mats, crust=None):
    """The bands' materials; crust: rougher materials for the two darkest bands (the splashes' skin)."""
    out = [(lowest, mats[index]) for lowest, index, _ in BANDS]
    if crust:
        out[0] = (out[0][0], crust[0x70])
        out[1] = (out[1][0], crust[0x71])
    return out


def crust_materials():
    glow = k.level_palette()
    return {index: k.material(f"lava_bubble_crust_{index:x}", palette=index, metallic=0.0, roughness=0.55,
                              emission=glow[index], emission_strength=strength)
            for _, index, strength in BANDS[:2]}


def pin(mat):
    """A speck at PIN_Z (a triangle a thousandth of a pixel across): every frame reaches as high, so all have the
    same bounds and the game sets them on the ground alike."""
    e = 0.001
    return k.mesh_object("pin", [(0, 0, PIN_Z), (e, 0, PIN_Z), (0, e, PIN_Z)], [(0, 1, 2)], mat)


def build():
    options = k.args()
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    for name, sprite, centre, radii, height, splashes in FRAMES:
        if only and name not in only:
            continue
        k.reset()
        mats = materials()
        crust = crust_materials()
        body, tones = dome(centre, radii, height)
        band_split(body, tones, bands(mats))
        k.smooth(body, 60)
        parts = [body]
        for i, (x, y, length, width, pixels, hottest) in enumerate(splashes):
            attached = foot_distance(x, y, centre, radii) < 2.0
            lump, values = splash(f"splash{i}", x, y, length + 0.1, width + 0.1, 0.28 + 0.2 * math.sqrt(pixels),
                                  SPLASH_TONE[hottest], centre, attached, i + sprite)
            band_split(lump, values, bands(mats, crust))
            k.smooth(lump, 70)
            parts.append(lump)
        parts.append(pin(mats[0x72]))
        bpy.context.view_layer.update()
        if "check" in options:
            mk.compare("%s (3 %d)" % (name, sprite), mk.coverage(parts, 24, 28),
                       k.sprite_mask(os.path.join(options["check"], "enemy_3.png"), sprite))
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        mk.report(name, parts, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, parts)


if __name__ == "__main__":
    build()
