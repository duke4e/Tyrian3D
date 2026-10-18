"""The blue ring of EYESPY, NOSE DRIP, DELI RUIN, GLACIER and INVADERS (sheet 5 sprite 127, 2x2: 24 x 28
pixels; sky and top layers), polished (2026-10-18; it replaces later_episodes.py's plain torus lying
flat). models.cfg: sprite 5 127 donut yaw=0, frame 5 129 donut_129, frame 5 131 donut_131.

As the 4x upscale draws it: a thick ring of glossy blue flesh, tilted so that its upper side (as
the sprite shows it) is a big bulging dome, its highlight at the upper left, and the hole, low in
the sprite, opens into a dark throat. The throat's wall that faces the camera (below and right of
the hole) is wrinkled into rolls that wind round into the dark, and a fleshy knob sits on the
hole's upper left lip. The ring is lopsided: its upper side is nearly twice as thick as its lower
side, which puts the hole low (rows 14-16 in 127).

The animation (127, 129 x3, 131 x3, 129 x3, 127 x2) tumbles it back and forth: its outline goes
from wide (127: 23 x 19 pixels) through round (129: 21 x 21) to tall (131: 19 x 23) and back, the
same picture squeezed. So the ring's axis, tilted from the camera, swings from down the screen
(127) over the lower right (129) to the right (131), its thick side kept up the screen. One model
per frame: donut (127), donut_129 and donut_131. The hole is closed deep inside by a dark membrane,
so that it stays as dark as the sprite draws it over any background.

Origin at the sprite's centre (pixel 12, 14); +Y up the sprite, +Z towards the camera.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <enemy_5.png or the
directory of the exported sheets> (the silhouette of each frame), --preview <prefix>.
"""
import math
import os
import sys

import bpy
import mathutils.noise as noise
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
from polish_orb_red import band_split, smoothstep  # noqa: E402
from polish_pod import triangles  # noqa: E402

# The ring, built in its own frame (its axis +Z, its thick side +Y) and then tilted: the radius of
# its tube's middle line, the tube's mean radius and how much thicker it is on the upper side (and
# thinner on the lower), its thickness along the axis (relative), the middle of its outline.
RING_RADIUS = 7.25
TUBE = 4.25
LOPSIDE = 1.25
AXIAL = 0.92
CENTRE = Vector((0.5, 0.25, 0.0))

# The tube's cross-section: a little elliptic, its long axis turning round the tube along the ring
# (TWIST turns per loop, a whole or half number); lumps (relative to the tube's radius) and their
# size (1 / pixels).
ELLIPSE, TWIST = 0.05, 1.0
LUMP, LUMP_SCALE = 0.06, 0.22

# The smooth dome: the ring's outer side all round, and its top as far as the hole's lip over the
# upper left (DOME_MIDDLE, degrees round the ring; DOME_HALF: fully dome within this many degrees of
# it, none beyond DOME_FADE). Elsewhere the top and the throat are the wrinkled lip: its edge runs
# round the tube at LIP_EDGE (degrees; DOME_EDGE where the dome is), along a groove.
DOME_MIDDLE, DOME_HALF, DOME_FADE = 110.0, 40.0, 85.0
LIP_EDGE, DOME_EDGE = 62.0, 122.0
GROOVE_DEPTH, GROOVE_WIDTH, GROOVE_SHADE = 0.35, 7.0, 2.0

# The rolls of the lip: their number per turn of the tube's cross-section, how they wind round the
# ring (whole turns), their height (pixels), and how much darker the creases between them and
# lighter their tops are (shades).
ROLLS, ROLL_WIND, ROLL_HEIGHT = 9, 2, 0.6
CREASE_SHADE, ROLL_SHADE = 2.0, 1.6

# Fleshy knobs on the lip of the hole: (angle round the ring, angle round the tube (degrees), radius
# (pixels), height (pixels)).
KNOBS = [(140.0, 128.0, 1.7, 1.3)]

# The shades of ramp 3 (0-11: palette 0x30-0x3b): the dome's, and the lip's round the tube from its
# edge down the throat (angle past the lip's edge (degrees), shade).
DOME_SHADE = 11.0
LIP_SHADES = [(0, 7.2), (30, 7.0), (70, 6.2), (105, 4.8), (130, 3.2), (150, 1.8), (172, 0.3), (190, 0.0)]
SHADE_COUNT = 12

# The frames: (model name, sprite, the direction the ring's axis leans to (degrees, 0 = right,
# -90 = down the screen), how far it leans from the camera (degrees), and a shift (pixels) that
# keeps the outline where the sprite draws it).
FRAMES = [
    ("donut", 127, -90.0, 43.6, (0.0, 0.0)),
    ("donut_129", 129, -45.0, 38.0, (-0.4, 0.1)),
    ("donut_131", 131, 0.0, 43.6, (0.0, 0.0)),
]


def tube_radius(phi):
    return TUBE + LOPSIDE * math.sin(phi)


def thetas():
    """The tube's angles: closer together on the throat's wall (the rolls)."""
    out, a = [], -80.0
    for step, end in ((12.0, 100.0), (6.0, 226.0), (9.0, 280.0)):
        while a < end - 1e-6:
            out.append(math.radians(a))
            a += step
    return out


def interp(points, x):
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        if x0 <= x <= x1:
            t = (x - x0) / (x1 - x0)
            return y0 + (y1 - y0) * (t * t * (3 - 2 * t))
    return points[-1][1]


def dome(phi):
    """How much of the dome reaches down to the hole here (0-1), phi round the ring (radians)."""
    off = abs((math.degrees(phi) - DOME_MIDDLE + 180.0) % 360.0 - 180.0)
    return smoothstep(DOME_FADE, DOME_HALF, off)


def lip(phi, deg):
    """The wrinkled lip at phi round the ring, deg round the tube: how far past its edge the point is
    (degrees), how much it is wrinkled (0-1) and where on a roll it is (0 in a crease, 1 on top)."""
    past = deg - (LIP_EDGE + (DOME_EDGE - LIP_EDGE) * dome(phi))
    weight = smoothstep(2.0, 14.0, past) * smoothstep(255.0, 225.0, deg)
    theta = math.radians(deg)
    wobble = noise.noise(Vector((math.cos(phi) * 1.3, math.sin(phi) * 1.3, theta * 0.8)))
    phase = ROLLS * theta + ROLL_WIND * phi + 1.4 * wobble
    return past, weight, abs(math.sin(phase / 2)) ** 0.5


def knob_height(phi, theta):
    h = 0.0
    for kp, kt, radius, height in KNOBS:
        dp = (math.degrees(phi) - kp + 180.0) % 360.0 - 180.0
        dt = (math.degrees(theta) - kt + 180.0) % 360.0 - 180.0
        # Distances in pixels: along the ring (at the knob's distance from the axis) and round the tube.
        along = RING_RADIUS + tube_radius(phi) * math.cos(math.radians(kt))
        d = math.hypot(math.radians(dp) * along, math.radians(dt) * tube_radius(phi))
        h += height * math.exp(-(d / radius) ** 2)
    return h


def ring_point(phi, theta):
    """The ring's surface at angle phi round the ring and theta round the tube (in its own frame),
    and its shade (0-11: palette 0x30-0x3b)."""
    er = Vector((math.cos(phi), math.sin(phi), 0.0))
    ez = Vector((0.0, 0.0, 1.0))
    r = tube_radius(phi) * (1 + ELLIPSE * math.cos(2 * (theta - TWIST * phi)))
    direction = er * math.cos(theta) + ez * (AXIAL * math.sin(theta))
    base = er * RING_RADIUS + direction * r
    r *= 1 + LUMP * noise.noise(base * LUMP_SCALE + Vector((3.0, 1.0, 5.0)))
    deg = (math.degrees(theta) + 90.0) % 360.0 - 90.0  # -90 to 270
    past, weight, roll = lip(phi, deg)
    groove = math.exp(-(past / GROOVE_WIDTH) ** 2)
    knob = knob_height(phi, theta)
    r += ROLL_HEIGHT * weight * (roll - 0.6) - GROOVE_DEPTH * groove + knob
    shade = DOME_SHADE if past < 0 else interp(LIP_SHADES, past)
    shade -= GROOVE_SHADE * groove
    shade -= weight * (CREASE_SHADE * smoothstep(0.75, 0.35, roll) - ROLL_SHADE * smoothstep(0.8, 0.98, roll))
    shade += 3.0 * knob
    return er * RING_RADIUS + direction * r, shade


def ring_mesh(name, segments=56):
    ts = thetas()
    verts, shades = [], []
    for i in range(segments):
        phi = 2 * math.pi * i / segments
        for theta in ts:
            p, s = ring_point(phi, theta)
            verts.append(p)
            shades.append(s)
    n = len(ts)
    faces = [(i * n + j, ((i + 1) % segments) * n + j, ((i + 1) % segments) * n + (j + 1) % n, i * n + (j + 1) % n)
             for i in range(segments) for j in range(n)]
    obj = k.mesh_object(name, verts, faces)
    k.recalc_normals(obj)
    return obj, shades


def membrane(name, mat, segments=48):
    """The dark membrane closing the hole inside the ring, sagging a little towards the back; its rim
    is buried in the tube's wall."""
    rim = []
    for i in range(segments):
        phi = 2 * math.pi * i / segments
        r = tube_radius(phi)
        rim.append(Vector((math.cos(phi), math.sin(phi), 0.0)) * (RING_RADIUS - 0.62 * r) +
                   Vector((0.0, 0.0, -0.5 * AXIAL * r)))
    middle = Vector((0.0, -0.5 * LOPSIDE, -0.5 * AXIAL * TUBE - 0.8))
    rings = [rim] + [[p.lerp(middle, f) + Vector((0.0, 0.0, -0.5 * f * (1 - f))) for p in rim] for f in (0.35, 0.7)]
    verts = [p for r in rings for p in r] + [middle]
    faces = []
    for a in range(len(rings) - 1):
        for i in range(segments):
            j = (i + 1) % segments
            faces.append((a * segments + i, a * segments + j, (a + 1) * segments + j, (a + 1) * segments + i))
    c = len(verts) - 1
    last = (len(rings) - 1) * segments
    faces += [(last + i, last + (i + 1) % segments, c) for i in range(segments)]
    obj = k.mesh_object(name, verts, faces, mat)
    k.recalc_normals(obj)
    return k.smooth(obj, 60)


def orientation(lean, tilt, shift=(0.0, 0.0)):
    """The ring's frame turned so that its axis leans tilt degrees from the camera towards the
    direction lean (degrees in the screen's plane), its thick side kept up the screen."""
    t, l = math.radians(tilt), math.radians(lean)
    a = Vector((math.sin(t) * math.cos(l), math.sin(t) * math.sin(l), math.cos(t)))
    up = Vector((0.0, 1.0, 0.0))
    y = (up - a * up.dot(a)).normalized()
    x = y.cross(a)
    m = Matrix((x, y, a)).transposed()
    return Matrix.Translation(CENTRE + Vector((shift[0], shift[1], 0.0))) @ m.to_4x4()


def materials():
    mats = {}
    for shade in range(SHADE_COUNT):
        index = 0x30 + shade
        # The dome glossy, the lip less, the throat dull.
        gloss = 2 if shade >= 11 else 1 if shade >= 5 else 0
        mats[shade] = k.material(f"donut_{index:x}", palette=index, metallic=(0.1, 0.2, 0.25)[gloss],
                                 roughness=(0.45, 0.3, 0.22)[gloss])
    return mats


def donut(name, lean, tilt, shift=(0.0, 0.0)):
    mats = materials()
    ring, shades = ring_mesh(name)
    band_split(ring, shades, [(-9.0 if s == 0 else s - 0.5, mats[s]) for s in range(SHADE_COUNT)])
    k.smooth(ring, 55)
    membrane(name + "_membrane", mats[0])
    turn = orientation(lean, tilt, shift)
    for obj in bpy.context.scene.objects:
        if obj.type == "MESH":
            obj.data.transform(turn)


def bounds():
    vs = [obj.matrix_world @ v.co for obj in bpy.context.scene.objects if obj.type == "MESH" for v in obj.data.vertices]
    return [(min(v[i] for v in vs), max(v[i] for v in vs)) for i in range(3)]


def build():
    options = k.args()
    outdir = options.get("outdir", os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "enemies"))
    for name, sprite, lean, tilt, shift in FRAMES:
        k.reset()
        donut(name, lean, tilt, shift)
        used = {m.name for obj in bpy.context.scene.objects if obj.type == "MESH" for m in obj.data.materials}
        (x0, x1), (y0, y1), (z0, z1) = bounds()
        print("== %s (5 %d): %d triangles, %d materials, x %.2f to %.2f, y %.2f to %.2f, z %.2f to %.2f" % (
            name, sprite, triangles(), len(used), x0, x1, y0, y1, z0, z1))
        if "check" in options:  # the sheet, or the directory of the exported sheets
            sheet = options["check"]
            k.check_silhouette(os.path.join(sheet, "enemy_5.png") if os.path.isdir(sheet) else sheet, sprite)
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        path = os.path.join(outdir, name + ".glb")
        k.export(path)
        print("%s: %d bytes" % (path, os.path.getsize(path)))
        if "preview" in options:
            k.preview(options["preview"] + name)


if __name__ == "__main__":
    build()
