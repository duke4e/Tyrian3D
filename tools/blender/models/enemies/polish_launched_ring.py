"""The red ring MARKERS' eye beetle launches (sheet V sprites 190 209 228, 1x1; episode 2's enemy 816 (the same in the
data of episodes 1-5), launched every 20 game frames by the eye beetle V 197 (enemy 815, polish_eye_beetle.py: its eye
flares, 199 201, each time it fires), 7 beetles in MARKERS' sky, and aimed at the player at launch, speed 4; armour
3). Polished (2026-10-22; nothing replaced: no generator made a model of V 190 and models.cfg had no line for it, so
the game drew it as its sprite with volume). No other enemy shows V 190, 209 or 228 (launched ones included).

The sprite (columns 2-9 of rows 3-10, an 8 x 8 picture round the cell's middle): a thin ring of ramp 4's dark reds,
one pixel wide (its corners cut as an octagon: a squircle in plan), brightest along its inner side at the upper right
(0x45) and darkest on its outer corners (0x41), and inside it two crescents of a smaller ring (about 1.6 pixels out):
the upper right one (from column 5 of row 5 round to column 7 of row 7) fat in its middle, a dark nub (column 6 of row
6) towards the ring's middle and its outer corner (column 7 of row 5) the sprite's brightest pixel (0x47), touching the
band there (a pixel corner to corner); the lower left one (columns 4-5 of rows 7-8) thin and dimmer (0x44 at its
corner), touching the band at the lower left. The hole shows the ground. Its frames 190 190 190 209 209 209 228 228
228 209 209 209 brighten it: 209 every shade one up (the bright corner two), 228 two or three up (the crescents three
to five) and the lower left crescent longer by a pixel at each end (column 4 of row 6, column 6 of row 8): then the
two crescents are each other turned half round, the upper right one lit, the other in shadow. A frame model each, the
same band, brighter materials and more emission; 228's lower crescent longer (the band sets the bounds, so they are
equal: the game, which centres them in height, keeps them in place). V 209 is, pixel for pixel, I 114, SAVARA's pulse
ring's damaged graphic (polish_launched_flames.py leaves I 114 to the base model on purpose: catalogue enemy 0 shows it
as a 2x2 sprite). Not a twin of anything with a model: the small sister of that pulse ring (I 19: the same ramp, a
band ring with a crescent ledge inside joining it at its upper right).

Built as such a ring in the pulse ring's manner: the band a rounded section (superellipse) turned about the ring's
axis (polish_launched_flames.revolve) round a squircle (PLAN_POWER: the sprite's octagon, a little wider on the
diagonals, BAND_CORNER, so that its corner pixels are covered); each crescent lofted along its arc of the inner squircle
(elliptical sections across it, their outer side tilted up like a ledge, widest at the arc's middle and running out to
points at its ends: the upper one fat, the lower one thin), a thin neck from its middle out to the band's inner side
(where the sprite's pixels touch corner to corner), and on the upper one's inner edge a dark tooth pointing in (the
nub). Painted as the sprite shades it, in seven classes (190's shades 0x41-0x47; each frame gives a class its own
palette index and emission): the band brightest at the upper right (value RING_BASE + RING_SWING * cos(angle -
RING_PEAK)), darker over its outer edge and underneath; each crescent brightest at its middle along its outer edge (a
peak falling off over CRESCENT_FALL degrees), its neck bright, the tooth dark, the lower crescent dimmer; the crescents
gain more in the brighter frames (as the sprite's do). Every class glows a little in its own colour (0-0.22 in 190 up
to 0.06-0.42 in 228; models.cfg's glow and the bloom add on top), satin rather than glossy (roughness 0.44-0.62: the
sky's reflection greys a glossy dark red). The parts are joined into one mesh and triangulated
(polish_k_pod.triangulate: the same output with and without --check).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; origin at the
sprite's centre (pixel 6, 7 of the cell: column c is x = c + 0.5 - 6, row r is y = 6.5 - r): the ring's middle. A
flying object (the sky): the game centres it in height.

models.cfg (new): model beetle_ring (and beetle_ring_209, _228) enemies/beetle_ring*.glb, sprite v 190 beetle_ring yaw=0
glow=10:0.15, frame v 209 beetle_ring_209, frame v 228 beetle_ring_228.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each frame's silhouette against
enemy_V.png), --preview <prefix>, --only <name,...>.
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
from polish_deli_boss import join  # noqa: E402
from polish_orb_red import band_split  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_launched_flames import (check_frames, lit, revolve, smoothstep, superellipse, turn,  # noqa: E402
                                    vertex_normals)

# The plan: a squircle (|x|^p + |y|^p = r^p), as the sprite's octagon.
PLAN_POWER = 2.5
# The band: the middle of its section (radius, z), half-width and half-height, superellipse power; how much wider it is
# on the diagonals (the octagon's corner pixels).
BAND = (3.5, 0.0, 0.56, 0.5, 2.4)
BAND_CORNER = 0.16
# The crescents: per crescent its arc (degrees from +x, counter-clockwise; per frame where they differ: the ends run out
# to points a little beyond the sprite's end pixels), its middle line's radius (on the inner squircle), its widest
# (across, at its middle), its thickness, its paint (the peak, values over 1, and the share its inner edge keeps) and
# the tooth on its inner edge at its middle (the upper one's, pointing in: the nub, column 6 of row 6; how far out its
# middle is, its radii along and across the radius and its half-thickness) or None.
CRESCENTS = {
    "upper": dict(arc={None: (-44.0, 134.0)}, radius=1.8, width=1.3, height=0.8, peak=6.0, keep=0.15,
                  tooth=(1.0, (0.72, 0.4, 0.3))),
    "lower": dict(arc={None: (176.0, 274.0), 228: (132.0, 318.0)}, radius=1.8, width=0.92, height=0.66, peak=3.0,
                  keep=0.25, tooth=None),
}
CRESCENT_Z, CRESCENT_TILT = 0.08, 0.22   # the crescents' middle height; their outer side higher (a ledge)
# The neck from each crescent's middle out to the band's inner side (the sprite's pixels touching corner to corner
# there): its radius at the crescent and at the band.
NECK = (0.2, 0.14)
CRESCENT_FALL = 24.0          # the crescents' paint falls off from their middles over this many degrees
RING_SEGMENTS, BAND_POINTS, CRESCENT_STEPS, CRESCENT_POINTS = 64, 12, 40, 12
# The paint: the band's value at its middle line, brightest towards RING_PEAK; its outer edge darker by RING_EDGE (over
# EDGE_RANGE of its half-width out from its middle line); undersides darker. The classes: 190's shades 0x41-0x47.
RING_BASE, RING_SWING, RING_PEAK = 3.2, 1.5, 40.0
RING_EDGE, EDGE_RANGE = 2.2, (0.2, 0.9)
CLASS_BORDERS = [-99.0, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5]
# Per frame: each class's (palette index, emission strength), and how much brighter the crescents are (values).
RING_FRAMES = {
    190: ([(0x41, 0.0), (0x42, 0.04), (0x43, 0.07), (0x44, 0.1), (0x45, 0.14), (0x46, 0.18), (0x47, 0.22)], 0.0),
    209: ([(0x42, 0.03), (0x43, 0.07), (0x44, 0.11), (0x45, 0.15), (0x46, 0.19), (0x48, 0.24), (0x49, 0.3)], 0.3),
    228: ([(0x43, 0.06), (0x45, 0.11), (0x46, 0.16), (0x47, 0.21), (0x48, 0.26), (0x4a, 0.33), (0x4b, 0.42)], 1.2),
}


def plan(phi):
    """The squircle's radius at angle phi (radians) for a unit radius."""
    c, s = abs(math.cos(phi)), abs(math.sin(phi))
    return (c ** PLAN_POWER + s ** PLAN_POWER) ** (-1.0 / PLAN_POWER)


def angle_off(a, b):
    return (a - b + 180.0) % 360.0 - 180.0


def arc_of(crescent, frame):
    return crescent["arc"].get(frame, crescent["arc"][None])


def crescent_shape(crescent, phi, arc):
    """The crescent at angle phi (radians) of its arc: its middle line's radius, its half-width and half-thickness."""
    a0, a1 = arc
    t = (math.degrees(phi) - a0) / (a1 - a0)
    sw = math.sin(math.pi * min(max(t, 0.0), 1.0))
    return crescent["radius"] * plan(phi), crescent["width"] / 2 * sw ** 0.45, crescent["height"] / 2 * sw ** 0.4


def band_mesh(name):
    phis = [2 * math.pi * i / RING_SEGMENTS for i in range(RING_SEGMENTS)]
    cx, cz, hw, hh, power = BAND

    def section(phi):
        f = plan(phi)
        w = hw * (1 + BAND_CORNER * math.sin(2 * phi) ** 2)
        return [(r * f, z) for r, z in superellipse(cx + (w - hw) * 0.5, cz, w, hh, BAND_POINTS, power)]
    return revolve(name, section, phis)


def crescent_mesh(name, crescent, frame):
    """A crescent: an arc of rings across it (ellipses in the radial-z plane, the outer side tilted up), running out to
    points at its ends; and the neck from its middle out to the band."""
    arc = arc_of(crescent, frame)
    a0, a1 = arc
    rings = []
    for i in range(1, CRESCENT_STEPS):
        phi = math.radians(a0 + (a1 - a0) * i / CRESCENT_STEPS)
        rc, w, h = crescent_shape(crescent, phi, arc)
        ux, uy = math.cos(phi), math.sin(phi)
        ring = []
        for j in range(CRESCENT_POINTS):
            a = 2 * math.pi * j / CRESCENT_POINTS
            r = rc + w * math.cos(a)
            ring.append(Vector((r * ux, r * uy, CRESCENT_Z + h * math.sin(a) + CRESCENT_TILT * w * math.cos(a))))
        rings.append(ring)
    tips = []
    for deg in (a0, a1):
        phi = math.radians(deg)
        rc = crescent["radius"] * plan(phi)
        tips.append((rc * math.cos(phi), rc * math.sin(phi), CRESCENT_Z))
    body = k.loft(name, rings, None, start_point=tips[0], end_point=tips[1])
    middle = math.radians((a0 + a1) / 2)
    rc, w, _ = crescent_shape(crescent, middle, arc)
    ux, uy = math.cos(middle), math.sin(middle)
    band_in = (BAND[0] - BAND[2] * 0.6) * plan(middle)
    count = 6
    path, radii = [], []
    for i in range(count):
        u = i / (count - 1)
        r = rc + w * 0.6 + (band_in - rc - w * 0.6) * u
        path.append((r * ux, r * uy, CRESCENT_Z + CRESCENT_TILT * w * 0.6 * (1 - u)))
        radii.append(NECK[0] + (NECK[1] - NECK[0]) * u)
    neck = mk.tube(name + "_neck", path, NECK[0], None, segments=10, radii=radii)
    parts = [body, neck]
    if crescent["tooth"] is not None:
        r, (along, across, thick) = crescent["tooth"]
        # an ellipsoid along y, turned to point along the crescent's middle
        tooth = k.ellipsoid(name + "_tooth", (0.0, 0.0, 0.0), (across, along, thick), None, 16, 10)
        mk.transform([tooth], Matrix.Translation((r * ux, r * uy, CRESCENT_Z - 0.05)) @
                     Matrix.Rotation(middle - math.pi / 2, 4, "Z"))
        parts.append(tooth)
    return parts


def band_values(obj):
    cx, _, hw, _, _ = BAND
    values = []
    for v, n in zip(obj.data.vertices, vertex_normals(obj)):
        phi = math.atan2(v.co.y, v.co.x)
        rp = math.hypot(v.co.x, v.co.y) / plan(phi)
        value = RING_BASE + RING_SWING * math.cos(phi - math.radians(RING_PEAK))
        value -= RING_EDGE * smoothstep(EDGE_RANGE[0], EDGE_RANGE[1], (rp - cx) / hw)
        if n.z < 0.0:
            value -= 2.5 * smoothstep(0.0, -0.6, n.z)
        values.append(value)
    return values


def crescent_values(obj, crescent, frame, boost, neck=False, tooth=False):
    arc = arc_of(crescent, frame)
    middle = (arc[0] + arc[1]) / 2
    values = []
    for v, n in zip(obj.data.vertices, vertex_normals(obj)):
        phi = math.atan2(v.co.y, v.co.x)
        deg = middle + angle_off(math.degrees(phi), middle)
        fall = math.exp(-(angle_off(deg, middle) / CRESCENT_FALL) ** 2)
        if neck or tooth:
            out = 1.0 if neck else 0.0
        else:
            rc, w, _ = crescent_shape(crescent, math.radians(deg), arc)
            out = max(0.0, min(1.0, (math.hypot(v.co.x, v.co.y) - (rc - w)) / max(2 * w, 1e-3)))
        value = 1.0 + crescent["peak"] * fall * (crescent["keep"] + (1 - crescent["keep"]) * out) + boost * fall
        if n.z < 0.0:
            value -= 2.5 * smoothstep(0.0, -0.6, n.z)
        values.append(value)
    return values


def beetle_ring(name, frame):
    classes, boost = RING_FRAMES[frame]
    mats = [(lowest, lit(f"bring{frame}_{i}", index, glow, roughness=0.62 if i == 0 else 0.52 if i < 4 else 0.44))
            for i, (lowest, (index, glow)) in enumerate(zip(CLASS_BORDERS, classes))]
    band = band_mesh(f"{name}_band")
    band_split(band, band_values(band), mats)
    k.smooth(band, 70)
    objects = [band]
    for key, crescent in CRESCENTS.items():
        parts = crescent_mesh(f"{name}_{key}", crescent, frame)
        for i, obj in enumerate(parts):
            band_split(obj, crescent_values(obj, crescent, frame, boost, neck=i == 1, tooth=i == 2), mats)
            k.smooth(obj, 70)
        objects += parts
    return [join(objects, name)]


# --- Build ------------------------------------------------------------------------------------------------------------

MODELS = [("beetle_ring", 190), ("beetle_ring_209", 209), ("beetle_ring_228", 228)]


def build():
    options = k.args()
    only = set(options["only"].split(",")) if "only" in options else None
    for name, frame in MODELS:
        if only is not None and name not in only:
            continue
        k.reset()
        objects = beetle_ring(name, frame)
        triangulate(objects)
        bpy.context.view_layer.update()
        if "check" in options:
            check_frames(objects, os.path.join(options["check"], "enemy_V.png"), [(frame, turn(0), f"V {frame}")],
                         move_to_frame=False)
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        mk.report(name, objects, os.path.join(mk.outdir(options), name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, objects, size=(12, 14), scale=32, distance=0.42)


if __name__ == "__main__":
    build()
