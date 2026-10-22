"""FLEET's crescents of fire (sheet K sprites 115 117 119, 2x2: 24 x 28 cells, the crescent in rows 12-24; enemy 709 of
episode 3, the ground layer; its animation 115 x4, 117 x4, 119 x4, 117 x4, cycling), modelled (2026-10-22; until now
they had no model and were drawn as flat volumes).

What they are: FLEET's invisible launchers (E 197, a blank sprite: enemy 698, armour 255; ten of them, events 664-4024
on ground 2 at x 18, 42, 258, 210, 90, 66, 210, -6, 90 and 66) each send one down the screen every 30 game frames,
fast ((0, 5) and the ground's scroll), on ground 2 as they are. Armour 30: the player can shoot them. No other enemy
shows these sprites (catalog.json); none is another sprite's pixels mirrored or turned. Not in episode 6 (THE CORE's
FLEET waves hold no launcher).

As the sprites draw it (the fire's ramp 7): a crescent flying belly first, its horns trailing up the screen: the band
round a circle of radius 12.6 about (0, 1.5) (its outer edge), its inner edge 5.6 from that centre at the bottom and
closing on the outer towards the horns' tips (up the screen at x -10.5 and 10.5), so it is 7 pixels thick at its belly
and tapers to the tips; a dark red rim (0x70-0x72), orange, yellow along its middle, hottest in the belly (rows 21-22).
The frames are the crescent pulsing: 115 is the dimmest (shades 0-11), its horns a pixel shorter and its belly's inner
edge narrower; 117 brighter (2-13), 119 the brightest (4-15, white-hot in the belly); 117 and 119 have the same
outline.

Built as a band of fire lofted along the crescent (sections across the band on rays from the centre, (0, 1.5), every
2 degrees, their ends closing to the horns' points): each section a rounded lens, fuller on top than underneath, its
crest swollen a little more along three flame tongues that run along the band from the belly up into each horn, fading
out towards the tips (ridges along the band's middle and half way to either edge, rippling across as they go: the
flames streaming back as it rushes down), the band's outline smoothed from each frame's pixels (OUTLINES: inner and
outer radius by angle).
Painted with each frame's own heat (the sprite's shades smoothed: polish_flame_drop.Heat) in bands of ramp 7's palette
indices (polish_orb_red.band_split: smooth borders), cooler where the surface turns away from the camera, hotter along
the tongues' crests, never darker than two shades over the frame's rim (115's 0x70, 117's 0x72, 119's 0x74), the
underside that dark red; every band glows in its own colour, more the hotter (0.08-0.62: the game's bloom and
models.cfg's glow add on top). The frame models: fire_crescent (115) on 115's outline,
fire_crescent_117 and fire_crescent_119 on 117's, the same section heights (their bounds in height are the same: the
game centres the model in height).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; origin at the
sprite's centre (pixel 12, 14: column c is x = c + 0.5 - 12, row r is y = 13.5 - r).

models.cfg (new): model fire_crescent enemies/fire_crescent.glb, model fire_crescent_117 enemies/fire_crescent_117.glb,
model fire_crescent_119 enemies/fire_crescent_119.glb; sprite k 115 fire_crescent yaw=0 glow=22:0.2:123:0:6, frame k
117 fire_crescent_117, frame k 119 fire_crescent_119 (the glow: the belly's light, in the fire's orange).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each frame's silhouette
against enemy_K.png), --preview <prefix>, --only <name,...>.
"""
import math
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
from polish_orb_red import band_split  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_flame_drop import Heat, monotone  # noqa: E402
from polish_launched_flames import grid, lit, shades, smoothstep, vertex_normals  # noqa: E402

CENTRE = (0.0, 1.5)  # the crescent's circle's centre

# The sprites' rows 12-24 (palette indices; 115's stray dark pixel of ramp 4, row 15 column 12, is left out).
K_115 = """
.. 70 .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. 70 ..
71 75 70 .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. 70 75 71
71 79 73 .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. 73 79 71
.. 77 76 70 .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. 70 75 77 ..
.. 72 79 75 70 .. .. .. .. .. .. .. .. .. .. .. .. .. .. 70 75 79 72 ..
.. 70 72 79 75 70 .. .. .. .. 70 70 70 70 .. .. .. .. 70 75 79 77 70 ..
.. .. 72 77 79 75 75 70 71 72 73 75 75 73 72 71 70 75 75 79 77 72 .. ..
.. .. 70 72 77 79 79 75 75 76 77 77 77 77 76 75 75 79 79 77 72 70 .. ..
.. .. .. 70 72 77 77 79 79 7a 7b 7a 7a 7b 79 79 79 77 77 72 70 .. .. ..
.. .. .. .. 70 72 72 77 77 78 7a 7a 7a 78 78 77 77 72 72 70 .. .. .. ..
.. .. .. .. .. .. 70 72 74 75 76 77 77 76 74 73 72 70 .. .. .. .. .. ..
.. .. .. .. .. .. .. .. 70 70 72 73 72 72 71 70 .. .. .. .. .. .. .. ..
"""
K_117 = """
.. 70 .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. 70 ..
71 72 70 .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. 70 72 71
73 77 72 .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. 72 77 73
73 7b 75 70 .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. 70 75 7b 73
71 79 78 72 70 .. .. .. .. .. .. .. .. .. .. .. .. .. .. 70 72 77 79 71
.. 74 7b 77 72 70 .. .. .. .. .. .. .. .. .. .. .. .. 70 72 77 7b 74 ..
.. 72 74 7b 77 72 70 .. 70 71 72 72 72 72 71 70 .. 70 72 77 7b 79 72 ..
.. .. 74 79 7b 77 77 72 73 74 75 77 77 75 74 73 72 77 77 7b 79 74 .. ..
.. .. 72 74 79 7b 7b 77 77 78 79 79 79 79 78 77 77 7b 7b 79 74 72 .. ..
.. .. .. 72 74 79 79 7b 7b 7c 7d 7c 7c 7d 7b 7b 7b 79 79 74 72 .. .. ..
.. .. .. .. 72 74 74 79 79 7a 7c 7c 7c 7a 7a 79 79 74 74 72 .. .. .. ..
.. .. .. .. .. .. 72 74 76 77 78 79 79 78 76 75 74 72 .. .. .. .. .. ..
.. .. .. .. .. .. .. .. 72 72 74 75 74 74 73 72 .. .. .. .. .. .. .. ..
"""
K_119 = """
.. 72 .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. 72 ..
73 74 72 .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. 72 74 73
75 79 74 .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. 74 79 75
75 7d 77 72 .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. 72 77 7d 75
73 7b 7a 74 72 .. .. .. .. .. .. .. .. .. .. .. .. .. .. 72 74 79 7b 73
.. 76 7d 79 74 72 .. .. .. .. .. .. .. .. .. .. .. .. 72 74 79 7d 76 ..
.. 74 76 7d 79 74 72 .. 72 73 74 74 74 74 73 72 .. 72 74 79 7d 7b 74 ..
.. .. 76 7b 7d 79 79 74 75 76 77 79 79 77 76 75 74 79 79 7d 7b 76 .. ..
.. .. 74 76 7b 7d 7d 79 79 7a 7b 7b 7b 7b 7a 79 79 7d 7d 7b 76 74 .. ..
.. .. .. 74 76 7b 7b 7d 7d 7e 7f 7e 7e 7f 7d 7d 7d 7b 7b 76 74 .. .. ..
.. .. .. .. 74 76 76 7b 7b 7c 7e 7e 7e 7c 7c 7b 7b 76 76 74 .. .. .. ..
.. .. .. .. .. .. 74 76 78 79 7a 7b 7b 7a 78 77 76 74 .. .. .. .. .. ..
.. .. .. .. .. .. .. .. 74 74 76 77 76 76 75 74 .. .. .. .. .. .. .. ..
"""
ART_TOP = 2.0        # the art's first row (row 12) has its top edge at y 2

# Each outline: the horns' tips (degrees from straight down, either way) and the inner and outer radius by angle
# (degrees, radius), smoothed from the frame's pixels (they are the same either side).
OUTLINES = {
    "115": dict(tip=86.5,
                inner=[(0, 5.66), (12, 5.72), (20, 5.98), (27, 6.9), (34, 7.6), (42, 8.15), (52, 8.45), (62, 8.75),
                       (72, 9.25), (80, 9.65), (86.5, 10.45)],
                outer=[(0, 12.42), (30, 12.62), (60, 12.55), (72, 12.3), (78, 12.05), (83, 11.55), (86.5, 10.6)]),
    "117": dict(tip=93.0,
                inner=[(0, 5.66), (12, 5.72), (20, 5.98), (28, 6.35), (36, 6.95), (45, 7.6), (55, 7.9), (65, 8.2),
                       (75, 8.75), (84, 9.35), (89, 9.85), (93.0, 10.45)],
                outer=[(0, 12.42), (30, 12.62), (60, 12.55), (75, 12.4), (82, 12.1), (88, 11.6), (93.0, 10.6)]),
}
# The sections: the angle step (degrees; finer towards the tips), the points round each (on top, underneath), the
# heights over the band's half-width (on top, underneath), and how much the crest is fuller (a superellipse power).
STEP, TIP_STEPS = 2.0, 6
SEGMENTS = (20, 8)
RISE = (0.82, 0.42)
FULL = 2.3
# The tongues: ridges across the section (at these shares of the half-width from the middle, -1 inner .. 1 outer),
# their height (pixels, at the belly; fading out between TONGUE_FADE degrees from straight down, the same for every
# frame, so that their bounds in height are the same), width (share), and their ripple along the band (waves over the
# half-crescent, how far they swing across (share)).
TONGUES = [(-0.5, 0.58), (0.0, 0.78), (0.48, 0.58)]
TONGUE_W = 0.21
TONGUE_FADE = (46.0, 88.0)
TONGUE_WAVES, TONGUE_SWING = 3.0, 0.12
TONGUE_HEAT = 2.0     # how much hotter the tongues' crests are (shades)
# The heat: the sprite's shades scaled (the smoothed peak lies under the pixels'), the sides turning from the camera
# cooler (times SIDE_COOL[0] + SIDE_COOL[1] * smoothstep(SIDE_COOL[2], SIDE_COOL[3], normal z)), the underside the
# rim's dark red.
GAIN = 1.1
FLOOR = 2.0           # the heat nowhere drops under the frame's darkest shade (its rim's) plus this
SIDE_COOL = (0.6, 0.4, -0.35, 0.6)
# The bands: (lowest heat, palette index, emission strength in the palette colour), ramp 7 from the rim's dark red to
# white.
BANDS = [(-99.0, 0x70, 0.08), (1.3, 0x72, 0.12), (2.6, 0x73, 0.14), (4.0, 0x75, 0.17), (5.8, 0x77, 0.22),
         (7.6, 0x79, 0.28), (9.3, 0x7b, 0.36), (10.9, 0x7c, 0.43), (12.1, 0x7d, 0.5), (13.3, 0x7e, 0.56),
         (14.4, 0x7f, 0.62)]

MODELS = [("fire_crescent", 115, K_115, "115"), ("fire_crescent_117", 117, K_117, "117"),
          ("fire_crescent_119", 119, K_119, "117")]


class Band:
    """A frame's crescent: inner and outer radius at any angle (smooth), the horns' tips."""

    def __init__(self, outline):
        self.tip = outline["tip"]
        self.inner = monotone([a for a, _ in outline["inner"]], [r for _, r in outline["inner"]])
        self.outer = monotone([a for a, _ in outline["outer"]], [r for _, r in outline["outer"]])

    def radii(self, phi):
        a = min(abs(phi), self.tip)
        return self.inner(a), self.outer(a)


def at(phi, r, z):
    """The point at angle phi (degrees from straight down, positive to the right), r from the centre, height z."""
    a = math.radians(phi)
    return Vector((CENTRE[0] + r * math.sin(a), CENTRE[1] - r * math.cos(a), z))


def angles(tip):
    """The sections' angles from -tip to tip: every STEP, finer over the last few degrees before each tip."""
    count = int(math.ceil((2 * tip - 8.0) / STEP))
    mid = [-tip + 4.0 + (2 * tip - 8.0) * i / count for i in range(count + 1)]
    ends = [tip - 4.0 * (1 - (i / TIP_STEPS)) ** 0.7 for i in range(1, TIP_STEPS)]
    ends = [a for a in ends if a > mid[-1] + 0.05]
    return sorted([-a for a in ends] + mid + ends)


def ridge_lift(phi, t):
    """How far the tongues raise the crest at angle phi and share t across the band (-1 inner .. 1 outer), and how
    near a tongue's crest the point is (0-1)."""
    fade = 1.0 - smoothstep(TONGUE_FADE[0], TONGUE_FADE[1], abs(phi))
    lift, near = 0.0, 0.0
    for i, (t0, height) in enumerate(TONGUES):
        swing = TONGUE_SWING * math.sin(math.radians(abs(phi)) * TONGUE_WAVES * 2 + i * 2.1)
        d = (t - t0 - swing) / TONGUE_W
        g = math.exp(-d * d)
        lift += height * g * fade
        near = max(near, g * fade)
    return lift, near


def crescent(name, band):
    """The band of fire: sections across it at every angle, lofted, the ends closed to the horns' points; with each
    vertex its share across the band and its tongues' nearness (for the paint)."""
    up, down = SEGMENTS
    thetas = [math.pi * j / up for j in range(up)] + [math.pi + math.pi * j / down for j in range(down)]
    rings, info = [], []
    for phi in angles(band.tip):
        r_in, r_out = band.radii(phi)
        mid, half = (r_in + r_out) / 2, max((r_out - r_in) / 2, 0.02)
        ring = []
        for theta in thetas:
            c, s = math.cos(theta), math.sin(theta)
            t = c                                         # -1 at the inner edge (theta pi), 1 at the outer
            r = mid + half * math.copysign(abs(c) ** (2 / FULL), c) if s >= 0 else mid + half * c
            if s >= 0:
                z = RISE[0] * half * abs(s) ** (2 / FULL)
                lift, near = ridge_lift(phi, t)
                z += lift * min(1.0, half / 1.4) * smoothstep(0.0, 0.35, s)
            else:
                z = RISE[1] * half * s
                near = 0.0
            ring.append(at(phi, r, z))
            info.append((t, near))
        rings.append(ring)
    a_tip = band.tip
    r_tip = sum(band.radii(a_tip)) / 2
    obj = k.loft(name, rings, None, start_point=at(-a_tip, r_tip, 0.0), end_point=at(a_tip, r_tip, 0.0))
    info += [(0.0, 0.0), (0.0, 0.0)]
    return obj, info


def paint(obj, info, heat, darkest):
    mats = [(lowest, lit(f"crescent_{index:02x}", index, glow, roughness=0.4 if index < 0x75 else 0.32 if index < 0x79
                         else 0.25)) for lowest, index, glow in BANDS]
    floor = darkest + FLOOR
    values = []
    for v, n, (t, near) in zip(obj.data.vertices, vertex_normals(obj), info):
        h = heat(v.co.x, v.co.y) * GAIN
        if n.z < -0.25:
            h = floor                                     # the underside: the rim's dark red
        else:
            h *= SIDE_COOL[0] + SIDE_COOL[1] * smoothstep(SIDE_COOL[2], SIDE_COOL[3], n.z)
            h += TONGUE_HEAT * near * smoothstep(0.0, 0.5, n.z) * smoothstep(2.0, 6.0, h)
            h = max(h, floor)
        values.append(h)
    band_split(obj, values, mats)
    return k.smooth(obj, 70)


def build():
    options = k.args()
    only = set(options["only"].split(",")) if "only" in options else None
    sheet = os.path.join(options["check"], "enemy_K.png") if "check" in options else None
    for name, sprite, art, outline in MODELS:
        if only is not None and name not in only:
            continue
        k.reset()
        band = Band(OUTLINES[outline])
        obj, info = crescent(name, band)
        rows = shades(grid(art), 7)
        heat = Heat(rows, ART_TOP, sigma=(0.6, 0.6))
        paint(obj, info, heat, min(v for row in rows for v in row if v is not None))
        parts = triangulate([obj])
        bpy.context.view_layer.update()
        if sheet is not None:
            mk.compare("%s (K %d)" % (name, sprite), mk.coverage(parts, 24, 28), k.sprite_mask(sheet, sprite))
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        mk.report(name, parts, os.path.join(mk.outdir(options), name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, parts, distance=0.6)


if __name__ == "__main__":
    build()
