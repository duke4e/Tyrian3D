"""The NortShip's weapons' own shots (shots sheet sprites 134, 241, 255, 111 and 246, all 1x1: 12 x 14 cells),
modelled (2026-10-30, round 3 of the energy shots' models; until then each was drawn as its sprite with volume and
the automatic glow). Built with polish_shot_pulse.py's bolts, polish_shot_fireball.py's kit (Dome, dome_core) and
polish_shot_sidekick.py's Tube.

Who fires them: the Nort Ship's guns (not sold: ports 36-38, its own; their pulses and comets are the pulse's and the
fireballs' models):
  134  the NortShip Super Pulse (front port 36) at power 7 (weapon 679): in the middle of its volley, 4 ahead of the
       gun, flying up at 8 pixels a game frame between two pulses (58)
  241  the NortShip Super Pulse at power 9-11 (weapons 681-683: one in the middle, two at 10) and the NortShip Spreader
       (rear port 37) at power 10-11 (weapons 693 694: two flying out up and sideways, one down at 11); a chain shot
       (damage 173): where it hits, a burst of the Starburst's stars (weapon 73) flies out
  255  the NortShip Spreader B (port 38) and the Spreader's second mode at every power (weapons 695-705: two flying out
       up and sideways, four from power 9), and the Pearl Wind special (2 and 44: weapon 620); a chain shot too (174,
       175): where it hits it splits (weapons 74, 75) into a 255 flying on and a spark (246)
  111  the Spreader B / the Spreader's second mode from power 3 (weapons 697-705: one to four flying down and out)
  246  the spark of 255's split (weapons 74 75), and the Nort Ship's engine sparks (weapon 671, while it banks)
None picks its sprite by heading: each is drawn as its sprite (yaw 0).

As the sprites draw them:
- 134 the Pulse-Cannon's five-bolt arrowhead (62) with the dark seams between its bolts filled with fire: one crown of
  flame, five hot heads (0x7c) along its leading edge, orange (0x7a) between them, its tails dark red.
- 241 a ring of dark red fire (columns 2-9, rows 2-11: 0x70-0x75) round a dark eye, hot spots on it (0x79, 0x7a: right,
  bottom; 0x77: top, left) and a swirl of fire inside its upper left (0x7a, 0x74).
- 255 a ball of white-blue light 11 across (columns 0-10, rows 2-12; its middle x -0.5, y -0.5): white (0x8f) over most
  of it, pale blue (0x8b-0x8e) in a crescent at its lower right, a dark slate rim (0x34, 0x3b).
- 111 a small bead of fire, 5 across (columns 3-7, rows 4-8): a dark red rim, orange, a white-yellow middle (0x7d).
- 246 a small blue spark, a four-pointed star 5 across (column 6, row 7 its middle): pale blue middle (0x89), blue
  arms (0x99), dark blue tips (0x93).

The models:
- 134: the five bolts of the Pulse-Cannon's arrowhead (polish_shot_pulse.sheath and core, the pulse's bands and cores,
  the heat from 134's own pixels) on a web of fire filling the valleys between their tails (a low Tube along a chevron
  through them, orange towards the heads, dark red behind), so that it reads as one crown (the pulse's shot_pulse_5
  alone read as a claw of five bolts where the sprite's volume had been one crown; fire along the seams between the
  bolts' bodies was tried first: hidden under the bolts).
- 241: a Tube (polish_shot_sidekick) round the ring (a closed curve, thicker below as the sprite's ring is, its bands
  across it: dark red edges, red, a hotter crest), raised beads of fire on its hot spots (polish_shot_fireball.
  dome_core) and a short swirl of fire inside its upper left.
- 255: a dome (polish_shot_fireball.Dome) of white-blue light round a hot spot up and left of its middle, falling
  through pale blue to a dark slate rim, faster towards its lower right; a white core raised on the hot spot.
- 111: a small dome of fire (the same), a white-yellow core.
- 246: a small four-pointed star (polish_shot_starburst's Star and polar mesh), a pale middle.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; the origin at the
cell's centre (pixel 6, 7: column c is x = c + 0.5 - 6, row r is y = 6.5 - r); built on z = 0.

models.cfg: see the block's comment.

Run: Blender -b --factory-startup -P tools/blender/models/shots/polish_shot_nort.py -- [--only <name,...>]
     [--outdir <dir>] (default assets/models/shots) [--check <sheets dir>] [--preview <prefix>]
"""
import math
import os
import sys

import bpy
from mathutils import Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_shot_sidekick as kit3  # noqa: E402
from polish_shot_sidekick import (kit, k, mk, triangulate, view, Path, Tube, band_material, top_of,  # noqa: E402
                                  facing, px)
from polish_shot_starburst import Star, polar_mesh, spoke_angles  # noqa: E402
from polish_launched_flames import lit, grid, shades  # noqa: E402
from polish_flame_drop import Heat  # noqa: E402
import polish_shot_pulse as pulse  # noqa: E402

OUTDIR = kit.OUTDIR
TOP = 7.0

# === 134: the crown of flame ==========================================================================================

SPRITE_134 = """
.. .. .. .. .. 75 76 .. .. .. .. ..
.. .. .. 75 79 7c 7b 7a 75 .. .. ..
.. .. 76 7c 7a 7b 7a 7a 7c 76 .. ..
.. 75 7a 7b 7a 7a 79 7a 7b 7a 75 ..
76 7c 7b 7a 7a 77 78 7a 7a 7b 7c 76
77 7b 7a 79 77 76 77 77 79 7a 7b 77
78 7a 78 78 75 77 77 75 78 79 7a 78
76 79 76 77 75 76 75 75 77 76 79 76
75 78 73 75 74 73 72 73 75 74 78 75
74 77 72 73 73 72 71 72 73 73 77 74
73 75 73 72 .. 71 .. .. 72 73 75 73
72 73 72 71 .. .. .. .. 71 72 73 72
.. 72 .. .. .. .. .. .. .. .. 72 ..
.. 71 .. .. .. .. .. .. .. .. 71 ..
"""
# The arrowhead's bolts (polish_shot_pulse's shot_pulse_5: a 4-pixel bolt in the middle, 3-pixel ones a row and three
# rows behind it either side), the heat from 134's own pixels.
CROWN_BOLTS = [pulse.Bolt(0.0, TOP, TOP - 11, 1.75, "wedge"), pulse.narrow(-2.5, 1, 11), pulse.narrow(2.5, 1, 11),
               pulse.narrow(-4.5, 3, 13), pulse.narrow(4.5, 3, 13)]
# The web of fire under them, filling the valleys between their tails (the sprite's seams): a low body along a chevron
# through the tails, its front edge (towards the heads) orange, its back edge dark red.
WEB_PATH = ((-5.4, -5.6), (-3.6, -3.6), (-1.6, -2.4), (0.0, -2.1), (1.6, -2.4), (3.6, -3.6), (5.4, -5.6))
WEB_HALF, WEB_DEPTH = 2.7, 0.36
WEB_ACROSS = ((-1.0, 2.2), (-0.4, 4.6), (0.2, 6.6), (0.7, 8.2), (1.0, 8.6))  # (u: -1 its back edge, 1 its front)


def crown(name):
    heat = Heat(shades(grid(SPRITE_134), 7), TOP, sigma=(0.55, 0.7))
    fire = [lit(f"pulse_fire_{index:02x}", index, glow, roughness=pulse.FIRE_ROUGHNESS)
            for _, index, glow in pulse.FIRE_BANDS]
    parts = []
    for i, bolt in enumerate(CROWN_BOLTS):
        parts.append(pulse.sheath(f"{name}_bolt{i}", bolt, heat, fire))
        bands = pulse.WEDGE_BANDS if bolt.core == "wedge" else pulse.SPINE_BANDS
        core_mats = [lit(f"pulse_core_{index:02x}", index, glow, roughness=pulse.CORE_ROUGHNESS)
                     for _, index, glow in bands]
        parts.append(pulse.core(f"{name}_core{i}", bolt, heat, core_mats))
    path = Path(WEB_PATH, smooth=2)
    across = kit.curve(WEB_ACROSS)

    def width(t):
        return WEB_HALF * min(1.0, 4.0 * min(t, 1.0 - t) + 0.25)

    def web_heat(t, u):
        return across(u) - 1.6 * abs(2.0 * t - 1.0)
    bands = [(b[0], b[1]) for b in pulse.FIRE_BANDS]
    web = Tube(path, width, web_heat, bands, depth=WEB_DEPTH, angle_gap=math.radians(30.0), caps=(True, True),
               fixed=[i / 10 for i in range(11)])
    parts.append(k.smooth(web.build(name + "_web", fire), 50))
    return parts


# === 241: the ring of fire ============================================================================================

RING = dict(centre=(0.0, 0.3), radii=(3.3, 4.0), half=0.7, bottom=0.62, depth=1.05)  # (bottom: thicker below)
RING_BANDS = [(-99.0, 0x71), (2.6, 0x73), (4.4, 0x75)]
# the hot spots: (angle round the ring, degrees counter-clockwise from +x; the bead's half-axes along and across the
# ring, its bands from its middle out)
RING_BEADS = [(10.0, 1.25, 0.72, ((0.0, 0x7a), (0.55, 0x78))), (-90.0, 1.3, 0.8, ((0.0, 0x7a), (0.55, 0x78))),
              (-40.0, 0.9, 0.6, ((0.0, 0x79), (0.55, 0x77))), (60.0, 0.95, 0.55, ((0.0, 0x78), (0.55, 0x77))),
              (175.0, 1.0, 0.6, ((0.0, 0x78), (0.55, 0x77)))]
# the swirl inside the ring's upper left (pixel centres, its hot end first)
SWIRL = ((5.9, 3.9), (4.9, 4.4), (4.25, 5.3), (4.1, 6.3))
SWIRL_BANDS = [(-99.0, 0x74), (2.0, 0x77), (3.4, 0x7a)]


def ring_of_fire(name):
    cx, cy = RING["centre"]
    rx, ry = RING["radii"]
    n = 32
    path = Path([(cx + rx * math.cos(2 * math.pi * i / n), cy + ry * math.sin(2 * math.pi * i / n)) for i in range(n)],
                closed=True, smooth=0)

    def heat(t, u):
        return 5.2 - 4.4 * u * u
    mats = [band_material("ring", i) for _, i in RING_BANDS]
    def width(t):
        return RING["half"] + RING["bottom"] * max(0.0, -math.sin(2 * math.pi * t))
    tube = Tube(path, width, heat, RING_BANDS, depth=RING["depth"], angle_gap=math.radians(40.0),
                caps=(False, False), fixed=[i / 28 for i in range(29)])
    body = kit3.weld(tube.build(name + "_ring", mats))
    parts = [k.smooth(body, 60)]
    for i, (angle, along_r, across_r, bands) in enumerate(RING_BEADS):
        a = math.radians(angle)
        bx, by = cx + rx * math.cos(a), cy + ry * math.sin(a)
        bead_bands = [(f, idx, 0.0) for f, idx in bands]
        bead_mats = [band_material("ring", idx) for _, idx in bands]
        # (an oval along the ring: dome_core's oval is axis-aligned, so turn it to lie along the ring)
        bead = kit.dome_core(f"{name}_bead{i}", (0.0, 0.0), across_r, along_r, 0.32,
                             lambda x, y, a=a, bx=bx, by=by: tube.top(bx + x * math.cos(a) - y * math.sin(a),
                                                                       by + x * math.sin(a) + y * math.cos(a)),
                             bead_bands, bead_mats, segments=12, tongues=(3, 0.0, 1.0))
        bead.data.transform(Matrix.Translation((bx, by, 0)) @ Matrix.Rotation(a, 4, "Z"))
        parts.append(bead)
    swirl_path = Path([px(c, r) for c, r in SWIRL], smooth=2)

    def swirl_width(t):
        return 0.62 * (math.sin(math.pi * min(max(t, 0.0), 1.0)) ** 0.5)

    def swirl_heat(t, u):
        return 4.2 - 3.4 * t - 0.6 * u * u
    swirl = Tube(swirl_path, swirl_width, swirl_heat, SWIRL_BANDS, depth=0.9, gap=0.7, angle_gap=math.radians(40.0))
    parts.append(k.smooth(swirl.build(name + "_swirl", [band_material("ring", i) for _, i in SWIRL_BANDS]), 60))
    return parts


# === 255: the pearl of light, 111: the bead of fire ===================================================================

def pearl_heat(u, phi):
    """The pearl's light: a white plateau, a pale blue crescent of shade towards its lower right, a dark rim."""
    shade = 1.0 + math.cos(phi - math.radians(315.0))  # (0 up and left .. 2 down and right)
    return (22.5 - (1.2 + 2.7 * shade) * mk.smoothstep(0.25, 0.86, u) - 10.0 * mk.smoothstep(0.77, 0.97, u))


PEARL = dict(centre=(-0.5, -0.5), radius=5.5, depth=0.78, hot=(-1.7, 0.9), heat_fn=pearl_heat,
             bands=[(-99.0, 0x3b, 0.0), (13.0, 0x8a, 0.5), (16.4, 0x8c, 0.54), (19.0, 0x8e, 0.58)],
             core=(2.6, 2.6, 0.42, ((0.0, 0x8f, 0.6), (0.6, 0x8e, 0.58))))
BEAD = dict(centre=(-0.5, 0.5), radius=2.55, depth=0.85, hot=(-0.5, 0.6),
            heat=13.5, rim=kit.fourier_rim(3.0), fall=1.2,
            bands=[(-99.0, 0x72, 0.24), (4.6, 0x75, 0.31), (7.6, 0x78, 0.42), (10.0, 0x7a, 0.5)],
            core=(0.75, 0.75, 0.26, ((0.0, 0x7d, 0.58), (0.55, 0x7b, 0.52))))


def dome(name, spec, prefix, segments, tongues):
    cx, cy = spec["centre"]
    r = spec["radius"]
    top, radius_from = kit.ellipse_dome(cx, cy, r, r, r * spec["depth"])
    hot = spec["hot"]
    heat = spec["heat_fn"] if "heat_fn" in spec else kit.ball_heat(spec["heat"], spec["rim"], spec["fall"])
    body = kit.Dome(hot, radius_from(*hot), top, heat, spec["bands"], segments=segments, tongues=tongues)
    mats = kit.materials(prefix, spec["bands"], roughness=0.45)
    parts = [body.build(name + "_body", mats)]
    rx, ry, lift, cbands = spec["core"]
    cmats = kit.materials(prefix, cbands, 0.35)  # (a palette index the body has too shares its material: one draw)
    parts.append(kit.dome_core(name + "_core", hot, rx, ry, lift, top, cbands, cmats, segments=segments))
    return parts


# === 246: the spark ===================================================================================================

SPARK = Star(tip=2.75, w0=1.3, taper=0.8, depth=0.9, section=1.8)
SPARK_CENTRE = (0.5, -0.5)
SPARK_RINGS = ((0.35, 1), (0.7, 2), (1.0, 2))  # (fraction of the way out, band of the faces outside it)
SPARK_BANDS = (0x89, 0x99, 0x93)


def spark(name):
    phis = spoke_angles((0.0, 6.0, 20.0, 45.0))
    edges = [SPARK.outline(p) for p in phis]
    rings = [([f * e for e in edges], b) for f, b in SPARK_RINGS]
    mats = [band_material("spark", i) for i in SPARK_BANDS]

    def top(x, y):
        return SPARK.height(x, y) + (0.25 if abs(x) < 1e-9 and abs(y) < 1e-9 else 0.0)
    obj = polar_mesh(name, phis, rings, 0, top, mats, under=2)
    obj.data.transform(Matrix.Translation((SPARK_CENTRE[0], SPARK_CENTRE[1], 0)))
    return [k.smooth(obj, 70)]


# === The models =======================================================================================================

MODELS = {  # name: (sprites, what it is, its hot point (model coordinates))
    "shot_nort_crown": ((134,), "a crown of flame: the pulse's five-bolt arrowhead on a web of fire", (0.0, 4.0)),
    "shot_nort_ring": ((241,), "a ring of dark red fire, hot beads on it, a swirl inside", (0.0, 0.0)),
    "shot_nort_pearl": ((255,), "a pearl of white-blue light, a dark slate rim", (-1.7, 0.9)),
    "shot_nort_bead": ((111,), "a small bead of fire, a white-yellow middle", (-0.5, 0.6)),
    "shot_nort_spark": ((246,), "a small blue spark, four-pointed", (0.5, -0.5)),
}


def build_model(name):
    if name == "shot_nort_crown":
        return crown(name)
    if name == "shot_nort_ring":
        return ring_of_fire(name)
    if name == "shot_nort_pearl":
        return dome(name, PEARL, "pearl", 28, (6, 0.02, 1.3))
    if name == "shot_nort_bead":
        return dome(name, BEAD, "bead", 10, (4, 0.03, 1.3))
    return spark(name)


def build():
    options = k.args()
    only = set(options["only"].split(",")) if "only" in options else None
    outdir = options.get("outdir", OUTDIR)
    for name, (sprites, what, hot) in MODELS.items():
        if only is not None and name not in only:
            continue
        k.reset()
        parts = triangulate(build_model(name))
        bpy.context.view_layer.update()
        print(f"== {name} (shots {' '.join(str(s) for s in sprites)}): {what}; top {top_of(parts):.3f}; "
              f"faces up/down/sideways {facing(parts)}")
        if "check" in options:
            kit.check_lines(name, parts, os.path.join(options["check"], "shots.png"), [(s, 0, 0, 0) for s in sprites],
                            hot)
        bpy.context.scene.view_settings.view_transform = "Standard"
        mk.report(name, parts, os.path.join(outdir, name + ".glb"))
        if "preview" in options:
            view(options["preview"] + name, parts)


if __name__ == "__main__":
    build()
