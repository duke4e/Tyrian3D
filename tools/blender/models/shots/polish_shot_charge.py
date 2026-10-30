"""The second player's charge cannon's high charges (shots sheet sprites 218, 219, 239, 240, 258 and 259; shots2 sprites
78, 81, 100, 119, 183-190, 202-209, 221-228, 240-247, 267-270 and 286-289, all 1x1: 12 x 14 cells), modelled
(2026-10-30, round 4 of the energy shots' models; until then each was drawn as its sprite with volume and the
automatic glow). Built with the earlier rounds' kits, imported and never changed: polish_shot_pulse.py's bolts,
polish_shot_fireball.py's Dome, Loft, balls and drops, polish_shot_dflame.py's drop_spec, polish_shot_sonic.py's Wave,
polish_shot_zflame.py's open cuts.

Who fires them: the second player in two-player games (TYR3D_MODE=two or twin: player 2 a ship of its own or the turret
linked to player 1's ship). Besides its rear gun (or the linked turret) it has a charge cannon (mainint.c, "Super
Charge Weapons"): the charge grows a level every 28 - 2 x power frames of the game (5 at most; player 2's rear power is
1 unless a powerup raises it: 26 frames, 21 above Hard) and a press of fire shoots weapon
chargeGunWeapons[rear port - 1] + charge (varz.c; the charge back to 0), flying from the ship whatever way the turret
points (linked, it fires only from charge 1):
  rear port 15 (Vulcan Cannon: player 2's starting rear gun), weapons 470-475: charge 0 and 1 the Vulcan's needles (67,
       70), 2 219 (one, 20 pixels a frame, slowing), 3 218 218 (4 out), 4 B78 x 4 (two either side, 8 out, slowly
       accelerating up), 5 B78 x 8
  rear ports 10 (Multi-Cannon) and 27-38, weapons 458-463: the pulses (58 59 60, 59 279 280), then 4 the big drop
       (B100 at by -7 above B119 at +7: one shot in two sprites) and B81 either side (10 out, 9 behind), 5 two big drops
       (6 out) and B81 14 out
  rear port 14 (Wild Ball), weapons 488-493: the Wild Ball's balls (126, 214), then 4 the bubble (239 240 above 258 259,
       6 out and 7 up or down: one shot in four sprites, falling back and then rising faster and faster), 5 two bubbles
       drifting apart
  rear port 12 (Protron), weapons 482-487: Protron pearls (B101, B82), then 5 the twin fireballs (B183 at bx -6 by -7,
       B202 +6 -7, B221 -6 +7, B240 +6 +7, flying up at 2 pixels a frame, weapani 7: frames B183-B190 and so on)
  rear port 11 (Sonic Wave), weapons 464-469: the sonic waves (66 73 123 143+144, polish_shot_sonic.py), then 5 the
       great arch (B267 B268 B269 B270 at bx -18 -6 6 18 by -7, B286-B289 below them at by +7: one 48 x 28 shot in
       eight sprites, 7 pixels a frame up the screen)
The shots of several sprites fly on through whatever they hit (damage 250 and over: infinite shots), so their pieces
stay together until they leave the screen (and fly on in the 3D view).

As the sprites draw them (ramp 7 the fire 0x70-0x7f, 9 the blue 0x90-0x9f, 12 the green 0xc0-0xcf; 0x5f ramp 5's
white, 0x2f ramp 2's, 0x60 ramp 6's black):
- 219 four of the Pulse-Cannon's narrow bolts (shots 165's: 3 pixels wide, a hot spine down the middle, 0x7c at its
  head) packed 2 pixels apart, the inner pair 2 rows ahead; 218 three (the middle one ahead).
- B78 an arch of fire 12 wide (a filled chevron, rows 0-8): a white-yellow crest (0x7d) a pixel inside its outer edge,
  0x7b-0x79 behind it, dark red (0x73-0x71) at its back; its legs (columns 1 and 10) and two drips (3 and 8) trailing.
- B81 a white-hot drop: a head 7 wide with a white middle (0x7f), a tail tapering to a pixel at row 13.
- B100 + B119 one teardrop 11 wide and 23 long: a round head of white (0x5f) inside a thin rim (0x7d, 0x7a, 0x73),
  its tail (B119) narrowing with a white streak down its middle.
- 239 240 / 258 259 a bubble of blue glass 21 across: its top rim thin and dark (0x90-0x93, black specks 0x60), its
  lower half filled with dark blue (0x91, 0x92), a bright crescent of caustic light along its lower rim (0x95-0x9f,
  brightest at the lower left), two highlights in its upper middle (0x9f; a dimmer 0x99), the rest see-through.
- B183... two identical fireballs 12 across (lit spheres: white 0x7f at their upper left, yellow, orange 0x79 at the
  lower right, a dark red rim 0x75/0x72) 12 apart, turning round their middle 22.5 degrees clockwise a frame: frame 0
  one above the other, frame 4 side by side (eight frames: half a turn, the balls being alike).
- B267... a great arch 45 wide and 23 tall (columns 1-46, rows 3-25 of the 48 x 28): white (0x2f) between a green rim
  (0xc4-0xcc) and a green inner edge, flat across its top (rows 3-13), its legs reaching down at both ends to row 25,
  dark green drips (0xc0-0xc8) hanging from its inner edge, a notch of dark green under its middle.

The models (the energy shots' method: half-bodies, round on top and flat underneath; palette materials glowing in
their own colours by shade; the heat in bands whose borders are the mesh's own rings, so that no face is cut; raised
hot cores; at most 10 materials a model):
- shot_charge_219, shot_charge_218: the pulse's narrow bolts (polish_shot_pulse.sheath and core) where the sprites draw
  them, the heat from their own pixels, on a low web of fire under their tails (alone they read as a claw of fingers,
  as polish_shot_nort.py found for 134).
- shot_charge_b78: a Wave (polish_shot_sonic.py) between the arch's outer edge and its back, in fire: the crest near
  the front edge, a white-yellow core standing out along it; the legs and drips thin lofts trailing behind.
- shot_charge_b81: a drop fitted to the sprite (polish_shot_dflame.drop_spec, polish_shot_fireball.build_drop).
- shot_charge_b100, _b119: the big drop fitted the same way to the two sprites together (its bands up to pale yellow,
  0x7e, a raised core of white, 0x5f as the sprite, over most of the head), built whole and cut along the sprites' edge
  (open cuts: polish_shot_zflame.cut_open), each half moved onto its sprite's centre.
- the bubble, the twin fireballs and the great arch: see their sections below.
Pieces of a shot of several sprites: model lines "origin", shot lines height= half the whole's height down (the
whole centred on the player's layer as the other shots are), one glow a shot on one piece (glow=1:0 on the others).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; a 1x1 model's
origin at its sprite's centre (pixel 6, 7: column c is x = c + 0.5 - 6, row r is y = 6.5 - r); a whole of several
sprites built round its middle (its column c, row r: x = c + 0.5 - w / 2, y = h / 2 - 0.5 - r), each piece moved
onto its own sprite's centre; built on z = 0.

models.cfg: see the block's comment; --cfg <file> appends the model and shot lines (heights and glows as built).

Checking in the game: player 2's rear port can only change by a pickup, so a test run arms it with the ship editor's
extra ships: a newsh$.shp in the user directory (editship.c; graphics type 1-7 needs no shapes) whose ships carry the
wanted rear ports, then CapsLock + the ship's digit in a two-player run (mainint.c JE_mainKeyboardInput); the debug
flight's pause and single steps give the same game states before and after (round 4's report, shots4b).

Run: Blender -b --factory-startup -P tools/blender/models/shots/polish_shot_charge.py -- [--only <name,...>]
     [--outdir <dir>] (default assets/models/shots) [--check <sheets dir>] (silhouettes against <dir>/shots.png and
     shots2.png, from TYR3D_EXTRACT) [--preview <prefix>] (top, three-quarter and game-camera views) [--cfg <file>]
"""
import math
import os
import sys

import bpy
import numpy as np
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_shot_fireball as kit  # noqa: E402
from polish_shot_fireball import k, mk, triangulate, view  # noqa: E402
import polish_shot_pulse as pulse  # noqa: E402
import polish_shot_dflame as dflame  # noqa: E402
import polish_shot_sonic as sonic  # noqa: E402
from polish_shot_zflame import cut_open, prune  # noqa: E402
from polish_launched_flames import lit, grid, shades  # noqa: E402
from polish_flame_drop import Heat  # noqa: E402

OUTDIR = kit.OUTDIR
TOP = 7.0

# === The sprites (palette indices, '..' transparent) ==================================================================

SPRITES = {
    ("shots", 218): """
.. .. .. .. .. .. 75 .. .. .. .. ..
.. .. .. .. .. 75 7c 76 .. .. .. ..
.. .. .. .. 75 76 7b 77 75 .. .. ..
.. .. .. 76 7c 78 7a 78 7c 76 .. ..
.. .. .. 77 7b 76 79 76 7b 77 .. ..
.. .. .. 78 7a 74 78 75 7a 78 .. ..
.. .. .. 76 79 74 77 74 79 76 .. ..
.. .. .. 75 78 73 75 73 78 75 .. ..
.. .. .. 74 77 72 73 72 77 74 .. ..
.. .. .. 73 75 73 72 73 75 73 .. ..
.. .. .. 72 73 72 71 72 73 72 .. ..
.. .. .. .. 72 .. .. .. 72 .. .. ..
.. .. .. .. 71 .. .. .. 71 .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
""",
    ("shots", 219): """
.. .. .. .. .. 75 .. 75 .. .. .. ..
.. .. .. .. 75 7c 76 7c 75 .. .. ..
.. .. .. 75 76 7b 77 7b 76 75 .. ..
.. .. 75 7c 78 7a 78 7a 78 7c 75 ..
.. .. 76 7b 76 79 76 79 76 7b 76 ..
.. .. 78 7a 74 78 75 78 74 7a 78 ..
.. .. 76 79 74 77 74 77 74 79 76 ..
.. .. 74 78 73 75 73 75 73 78 74 ..
.. .. 74 77 72 73 72 73 72 77 74 ..
.. .. 73 75 73 72 .. 72 73 75 73 ..
.. .. 72 73 72 71 .. 71 72 73 72 ..
.. .. .. 72 .. .. .. .. .. 72 .. ..
.. .. .. 71 .. .. .. .. .. 71 .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
""",
    ("shots2", 78): """
.. .. .. .. 73 76 76 73 .. .. .. ..
.. .. .. 73 79 7d 7d 79 73 .. .. ..
.. .. 73 76 7b 7d 7d 7b 76 73 .. ..
.. 73 76 7d 78 7b 7b 78 7d 76 73 ..
73 76 79 7d 76 79 79 76 7d 79 76 73
76 7d 7a 79 73 75 75 73 79 7a 7d 76
76 7d 79 76 71 73 73 71 76 79 7d 76
73 79 73 73 71 72 72 71 73 73 79 73
71 76 71 72 .. 71 71 .. 72 71 76 71
.. 73 .. 71 .. .. .. .. 71 .. 73 ..
.. 72 .. .. .. .. .. .. .. .. 72 ..
.. 71 .. .. .. .. .. .. .. .. 71 ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
""",
    ("shots2", 81): """
.. .. .. 72 76 7a 77 73 .. .. .. ..
.. .. 72 77 7b 7e 7b 78 73 .. .. ..
.. .. 74 7a 7f 7f 7f 7a 74 .. .. ..
.. .. 76 7c 7f 7f 7f 7d 76 .. .. ..
.. .. 75 7b 7f 7f 7f 7b 75 .. .. ..
.. .. 73 7a 7f 7f 7f 7a 73 .. .. ..
.. .. 71 75 7b 7e 7b 75 71 .. .. ..
.. .. .. 73 79 7c 79 73 .. .. .. ..
.. .. .. 71 75 7b 75 71 .. .. .. ..
.. .. .. .. 73 79 73 .. .. .. .. ..
.. .. .. .. 71 76 71 .. .. .. .. ..
.. .. .. .. .. 74 .. .. .. .. .. ..
.. .. .. .. .. 72 .. .. .. .. .. ..
.. .. .. .. .. 71 .. .. .. .. .. ..
""",
    # B100 above B119: one drop (the whole 12 x 28)
    ("shots2", 100): """
.. .. .. 72 74 76 74 72 .. .. .. ..
.. .. 72 77 7a 7c 7a 77 72 .. .. ..
.. 73 78 7d 5f 5f 5f 7d 78 73 .. ..
73 78 7d 5f 5f 5f 5f 5f 7d 78 73 ..
77 7d 5f 5f 5f 5f 5f 5f 5f 7d 77 ..
79 7d 5f 5f 5f 5f 5f 5f 5f 7d 7a ..
7a 7d 5f 5f 5f 5f 5f 5f 5f 7d 7b ..
7b 7d 5f 5f 5f 5f 5f 5f 5f 7d 7c ..
7a 7d 5f 5f 5f 5f 5f 5f 5f 7d 7a ..
77 7b 7e 5f 5f 5f 5f 5f 7e 7b 77 ..
73 79 7d 5f 5f 5f 5f 5f 7d 79 73 ..
.. 75 7b 7e 5f 5f 5f 7e 7b 75 .. ..
.. 73 79 7d 5f 5f 5f 7d 79 73 .. ..
.. .. 75 7b 5f 5f 5f 7b 75 .. .. ..
""",
    ("shots2", 119): """
.. .. 73 79 7e 5f 7e 79 73 .. .. ..
.. .. .. 75 7d 5f 7d 75 .. .. .. ..
.. .. .. 73 7b 7e 7b 73 .. .. .. ..
.. .. .. .. 79 7d 79 .. .. .. .. ..
.. .. .. .. 75 7c 75 .. .. .. .. ..
.. .. .. .. 73 7a 73 .. .. .. .. ..
.. .. .. .. .. 78 .. .. .. .. .. ..
.. .. .. .. .. 75 .. .. .. .. .. ..
.. .. .. .. .. 73 .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
""",
}


def rows_of(*keys):
    """The sprites' palette indices (rows of ints or None), stacked top to bottom."""
    out = []
    for key in keys:
        out += grid(SPRITES[key])
    return out


class Art(dflame.Art):
    """polish_shot_dflame.Art (a sprite as shades, nan transparent, with its pixels' model coordinates) from rows of
    palette indices: the shade is the index's low digit (0x5f, 0x2f: white)."""

    def __init__(self, rows):
        self.S = np.array([[np.nan if i is None else float(i & 15) for i in row] for row in rows])
        self.h, self.w = self.S.shape


def materials(prefix, bands, roughness=kit.FIRE_ROUGHNESS):
    """kit.materials, one material a palette index (bands repeating an index share it)."""
    out, made = [], {}
    for _, index, glow in bands:
        if index not in made:
            made[index] = lit(f"{prefix}_{index:02x}", index, glow, roughness=roughness)
        out.append(made[index])
    return out


# === 218, 219: the pulse's narrow bolts, packed =======================================================================

CROWNS = {
    "shot_charge_219": (("shots", 219), [pulse.narrow(-2.5, 2, 12), pulse.narrow(-0.5, 0, 10), pulse.narrow(1.5, 0, 10),
                                         pulse.narrow(3.5, 2, 12)], "four narrow bolts packed (port 15's charge 2)"),
    "shot_charge_218": (("shots", 218), [pulse.narrow(-1.5, 2, 12), pulse.narrow(0.5, 0, 10), pulse.narrow(2.5, 2, 12)],
                        "three narrow bolts packed (port 15's charge 3)"),
}


# The web of fire under the bolts' tails (the sprites' dark red between the spines, so that the bolts read as one
# body, as polish_shot_nort.py's crown): a low loft round the crown's middle line (x), from its nose to its tail (y),
# its half-width, its height over its half-width; its heat along it (front to tail) and how much less at its sides.
WEBS = {219: dict(x=0.5, nose=2.6, tail=-4.4, half=4.1, depth=0.3),
        218: dict(x=0.5, nose=2.6, tail=-4.4, half=3.2, depth=0.36)}
WEB_ALONG = ((0.0, 6.6), (0.3, 5.6), (0.6, 4.2), (0.85, 3.0), (1.0, 2.0))
WEB_ACROSS = ((0.0, 1.0), (1.0, 1.4))


def build_crown(name, key, bolts):
    heat = Heat(shades(grid(SPRITES[key]), 7), TOP, sigma=(0.55, 0.7))
    fire = [lit(f"pulse_fire_{index:02x}", index, glow, roughness=pulse.FIRE_ROUGHNESS)
            for _, index, glow in pulse.FIRE_BANDS]
    core_mats = [lit(f"pulse_core_{index:02x}", index, glow, roughness=pulse.CORE_ROUGHNESS)
                 for _, index, glow in pulse.SPINE_BANDS]
    parts = []
    for i, bolt in enumerate(bolts):
        parts.append(pulse.sheath(f"{name}_bolt{i}", bolt, heat, fire))
        parts.append(pulse.core(f"{name}_core{i}", bolt, heat, core_mats))
    web = WEBS[key[1]]
    half = web["half"]
    width = kit.curve(((0.0, 0.0), (0.04, 0.6 * half), (0.14, 0.95 * half), (0.3, half), (0.7, 0.96 * half),
                       (0.88, 0.75 * half), (1.0, 0.0)))
    loft = kit.Loft(web["x"], web["nose"], web["tail"], width, kit.loft_heat(WEB_ALONG, WEB_ACROSS),
                    pulse.FIRE_BANDS, depth=web["depth"], segments=8, tongues=(2.5, 0.02, 1.9), gap=0.2,
                    width_gap=0.6)
    parts.append(prune(loft.build(name + "_web", fire)))
    return parts


# === B78: the arch of fire ============================================================================================

# The arch's outer (front) and inner (back) edges' right halves, apex first, both ending at the same tip (the bottom
# corner); the crest's height along it (|u|: 0 the apex, 1 the end), where it lies across (s) and how the back falls;
# the heat along its crest (|u|), how much it falls to the front edge and to the back, where it peaks across; the
# core along the crest (from |u| = -c to c, its half-width, lift).
ARCH = dict(
    outer=[(0.0, 7.0), (1.4, 6.95), (2.5, 6.45), (3.5, 5.5), (4.5, 4.5), (5.4, 3.5), (5.9, 2.4), (6.0, 1.0),
           (6.0, -0.6), (5.9, -1.6), (5.65, -2.05)],
    inner=[(0.0, -1.85), (1.1, -1.5), (2.2, -1.45), (3.2, -1.65), (4.3, -1.85), (5.2, -2.0), (5.65, -2.05)],
    samples=31, height=((0.0, 1.85), (0.35, 1.75), (0.65, 1.45), (0.85, 1.05), (0.95, 0.6), (1.0, 0.0)),
    crest=0.2, back=1.15,
    along=((0.0, 13.8), (0.3, 13.7), (0.55, 13.3), (0.75, 12.6), (0.88, 10.6), (0.95, 7.8), (1.0, 5.0)),
    front=0.62, back_drop=0.92, peak=0.17, back_power=1.45,
    core=(0.86, 0.62, 0.36))
ARCH_BANDS = [(-99.0, 0x71, 0.2), (2.6, 0x73, 0.24), (4.6, 0x75, 0.31), (6.6, 0x77, 0.38), (8.4, 0x79, 0.46),
              (10.2, 0x7a, 0.5), (11.8, 0x7b, 0.52)]
ARCH_CORE_BANDS = ((0.0, 0x7d, 0.58),)
# The legs (columns 1 and 10, to row 11) and the drips (columns 3 and 8, to row 9): x, the y of their root (inside the
# arch's back) and tip, half-width; their heat along them.
ARCH_TRAILS = [(-4.5, 0.6, -5.0, 0.42, ((0.0, 6.8), (0.35, 5.0), (0.7, 3.0), (1.0, 1.2))),
               (4.5, 0.6, -5.0, 0.42, ((0.0, 6.8), (0.35, 5.0), (0.7, 3.0), (1.0, 1.2))),
               (-2.5, -0.6, -3.0, 0.36, ((0.0, 3.6), (0.5, 2.4), (1.0, 1.0))),
               (2.5, -0.6, -3.0, 0.36, ((0.0, 3.6), (0.5, 2.4), (1.0, 1.0)))]
TRAIL_ACROSS = ((0.0, 1.2), (1.0, 1.4))


def build_arch(name):
    mats = materials("charge_arch", ARCH_BANDS)
    cmats = materials("charge_arch_core", ARCH_CORE_BANDS, kit.CORE_ROUGHNESS)
    spec = ARCH
    outer, us = sonic.arch_path(spec["outer"], spec["samples"])
    inner, _ = sonic.arch_path(spec["inner"], spec["samples"])
    wave = sonic.Wave(outer, inner, us, sonic.height_curve(spec["height"]),
                      sonic.heat_field(spec["along"], spec["front"], spec["back_drop"], spec["peak"],
                                       spec["back_power"]), ARCH_BANDS, crest=spec["crest"], back=spec["back"],
                      waves=(3.0, 0.02, 1.9), gap=0.3)
    parts = [prune(wave.build(name + "_wave", mats))]
    c, w, lift = spec["core"]
    n = len(us) - 1
    parts.append(sonic.crest_core(name + "_core", wave, spec["peak"], n * (1 - c) / 2, n * (1 + c) / 2, w, lift,
                                  ARCH_CORE_BANDS, cmats, rings=24))
    for i, (x, root, tip, half, along) in enumerate(ARCH_TRAILS):
        loft = kit.Loft(x, root, tip, sonic.streak_width(half), kit.loft_heat(along, TRAIL_ACROSS), ARCH_BANDS,
                        depth=0.5, segments=5, tongues=(2.0, 0.02, 1.2), gap=0.25, width_gap=0.5,
                        head_fractions=(0.2,), tail_fractions=(0.5,))
        parts.append(prune(loft.build(name + "_trail%d" % i, mats)))
    return parts


# === B81 and B100 + B119: drops of white fire =========================================================================

DROP_CORE = {15: ((0.0, 0x7f, 0.62), (0.5, 0x7e, 0.6)), 14: ((0.0, 0x7e, 0.6), (0.5, 0x7d, 0.58))}
# The big drop's bands: a thin rim of red, orange and yellow round a head of pale yellow (0x7e), on which a raised
# core of white (ramp 5's 0x5f, as the sprite) covers most of the head: its half-axes (times the head's) and lift.
BIG_DROP_BANDS = [(-99.0, 0x73, 0.24), (3.6, 0x75, 0.31), (5.6, 0x77, 0.38), (7.6, 0x79, 0.46), (9.4, 0x7b, 0.52),
                  (11.4, 0x7d, 0.58), (13.0, 0x7e, 0.6)]
BIG_DROP_CORE = ((0.0, 0x5f, 0.62), (0.78, 0x7e, 0.6))
BIG_DROP_CORE_SIZE = (0.8, 0.76, 0.5)
BIG_DROP_PIECES = [(("shots2", 100), (-6.0, 6.0, 0.0, 14.0)), (("shots2", 119), (-6.0, 6.0, -14.0, 0.0))]


# B81's core: as large as the sprite's white block (half-axes times the head's half-width and height), lift.
SMALL_DROP_CORE_SIZE = (0.5, 0.42, 0.42)


def build_small_drop(name):
    spec, peak = dflame.drop_spec(Art(rows_of(("shots2", 81))))
    cx, cy, _, _, _ = spec["core"]
    head_rx = max(w for _, w in spec["width"])
    fx, fy, lift = SMALL_DROP_CORE_SIZE
    spec["core"] = (cx, cy, fx * head_rx, fy * (spec["nose"] - spec["tail"]) * 0.5, lift)
    parts = kit.build_drop(name, spec, "charge_drop", dflame.BANDS, DROP_CORE[min(max(peak, 14), 15)])
    return [prune(p) for p in parts], spec


def build_big_drop(name):
    """The big drop whole (12 x 28: B100 above B119): (parts, spec)."""
    art = Art(rows_of(("shots2", 100), ("shots2", 119)))
    spec, peak = dflame.drop_spec(art)
    fire = materials("charge_bigdrop", BIG_DROP_BANDS)
    body = kit.Loft(spec["x"], spec["nose"], spec["tail"], kit.curve(spec["width"]), None, BIG_DROP_BANDS,
                    depth=spec["depth"], segments=spec["segments"], tongues=spec["waves"], gap=0.12, width_gap=0.6,
                    heat_xy=spec["heat"])
    parts = [prune(body.build(name + "_fire", fire))]
    cx, cy, _, _, _ = spec["core"]
    head_rx = max(w for _, w in spec["width"])
    head_ry = 0.5 * (spec["nose"] - cy) + 0.5 * head_rx
    fx, fy, lift = BIG_DROP_CORE_SIZE
    cmats = materials("charge_bigdrop_core", BIG_DROP_CORE, kit.CORE_ROUGHNESS)
    parts.append(prune(kit.dome_core(name + "_core", (cx, cy), fx * head_rx, fy * head_ry, lift, body.top,
                                     BIG_DROP_CORE, cmats, segments=24, tongues=(3, 0.0, 1.0))))
    print("big drop: head half-width %.2f, core %.2f x %.2f at %.2f %.2f" % (head_rx, fx * head_rx, fy * head_ry,
                                                                               cx, cy))
    return parts, spec


# === B183-B190, B202-B209, B221-B228, B240-B247: the twin fireballs (port 12's charge 5) ==============================

# One fireball (the sixteen balls of the eight frames are the same pixels): a dome over a circle of BALL_RADIUS round
# its middle, BALL_DEPTH times as high; its heat from the hot spot (BALL_HOT from its middle: the sprite's white, up and
# left) out to its outline: towards the near side (up and left) white and yellow in a plateau up to a thin dark rim
# (BALL_NEAR), towards the far side (BALL_FAR, seen from the hot spot) falling to orange, which holds most of the way
# to the rim (BALL_FAR_HEAT), between them by the angle; its bands' borders waving and swirling a little; a raised
# white core on the hot spot (BALL_CORE: its half-width, length, lift, bands from its middle out).
BALL_RADIUS, BALL_DEPTH, BALL_HOT, BALL_FAR = 6.0, 0.84, (-1.0, 1.9), -62.0
BALL_NEAR = ((0.0, 15.6), (0.35, 15.2), (0.6, 13.6), (0.8, 11.4), (0.92, 8.0), (1.0, 4.4))
BALL_FAR_HEAT = ((0.0, 15.6), (0.22, 13.9), (0.45, 11.6), (0.65, 10.4), (0.84, 9.5), (0.93, 7.4), (1.0, 4.4))
BALL_BANDS = [(-99.0, 0x72, 0.22), (4.6, 0x75, 0.31), (7.0, 0x77, 0.38), (8.6, 0x79, 0.46), (10.0, 0x7a, 0.5),
              (11.2, 0x7b, 0.52), (12.4, 0x7c, 0.56), (13.4, 0x7d, 0.58)]
BALL_CORE = (2.5, 4.8, 0.45, ((0.0, 0x7f, 0.62), (0.5, 0x7e, 0.6)))
# The balls' places frame by frame (found on the sprites: two alike, turning half a turn in eight frames).
TWIN_PLACES = [((0, 6), (0, -6)), ((2, 5), (-2, -5)), ((4, 4), (-4, -4)), ((5, 2), (-5, -2)), ((6, 0), (-6, 0)),
               ((5, -2), (-5, 2)), ((4, -4), (-4, 4)), ((2, -5), (-2, 5))]
TWIN_FIRST = (183, 202, 221, 240)  # (the pieces' first frames: top left, top right, bottom left, bottom right)
TWIN_BOXES = ((-12.0, 0.0, 0.0, 14.0), (0.0, 12.0, 0.0, 14.0), (-12.0, 0.0, -14.0, 0.0), (0.0, 12.0, -14.0, 0.0))
# Each ball's glow (size, strength, index): the first ball's on the top left piece, the second's on the bottom right.
TWIN_GLOW = (17, 0.35, 0x7c)


def twin_pieces(f):
    return [(("shots2", first + f), box) for first, box in zip(TWIN_FIRST, TWIN_BOXES)]


def build_ball(name, centre, mats, cmats):
    cx, cy = centre
    top, radius_from = kit.ellipse_dome(cx, cy, BALL_RADIUS, BALL_RADIUS, BALL_RADIUS * BALL_DEPTH)
    hot = (cx + BALL_HOT[0], cy + BALL_HOT[1])
    far = math.radians(BALL_FAR)
    near_heat, far_heat = kit.curve(BALL_NEAR), kit.curve(BALL_FAR_HEAT)

    def heat(u, phi):
        u = min(max(u, 0.0), 1.0)
        w = 0.5 + 0.5 * math.cos(phi - far)  # (1 towards the far side, 0 towards the near one)
        swirl = 0.25 * math.sin(2 * phi + 2.4 * u + 0.4) * math.sin(math.pi * u) ** 2
        return near_heat(u) * (1.0 - w) + far_heat(u) * w + swirl - 0.01 * u
    dome = kit.Dome(hot, radius_from(*hot), top, heat, BALL_BANDS, segments=24, tongues=(6, 0.03, 1.3))
    parts = [prune(dome.build(name + "_fire", mats))]
    w, length, lift, cbands = BALL_CORE
    parts.append(prune(kit.dome_core(name + "_core", hot, w, length / 2, lift, top, cbands, cmats)))
    return parts


def build_twins(f):
    mats = materials("charge_ball", BALL_BANDS)
    cmats = materials("charge_ball_core", BALL_CORE[3], kit.CORE_ROUGHNESS)
    a, b = TWIN_PLACES[f]
    return build_ball("charge_twin%d_a" % f, a, mats, cmats) + build_ball("charge_twin%d_b" % f, b, mats, cmats)


# === 239 240 / 258 259: the bubble (port 14's charges 4-5) ============================================================

# A bubble of blue glass. Its body a ring (a closed Wave, polish_shot_sonic.py) between its outline (BUBBLE_OUTER: a
# circle) and its see-through middle (BUBBLE_INNER: an ellipse higher up, so that the ring is thin and dark at the top
# and thick at the bottom, where the sprite fills it with dark blue); its heat a crescent of caustic light a little in
# from the outline (BUBBLE_PEAK_IN pixels), brightest at the lower left (BUBBLE_CREST: (degrees counter-clockwise from
# right, heat)), the outline itself BUBBLE_EDGE of that, falling inwards to BUBBLE_BACK; its height by angle; a core of
# light blue standing out along the crescent's brightest part (BUBBLE_CORE: from, to (degrees), half-width, lift). Over
# the middle a cap of dark blue glass (see-through, drawn blended as polish_purpleball.py's), BUBBLE_CAP high, with
# the sprite's highlight in it (the cap's bands round it: light blue, then glass) and a dimmer second highlight (a small
# lens on the cap).
BUBBLE_OUTER = ((-0.5, -0.5), 10.5, 10.5)
BUBBLE_INNER = ((0.0, 2.0), 7.0, 6.5)
BUBBLE_SAMPLES = 56
BUBBLE_CREST = ((-160.0, 9.5), (-135.0, 15.0), (-110.0, 11.0), (-90.0, 8.5), (-60.0, 8.2), (-30.0, 7.0), (0.0, 5.0),
                (40.0, 3.0), (90.0, 1.4), (140.0, 2.6), (180.0, 4.6))
BUBBLE_PEAK_IN, BUBBLE_EDGE, BUBBLE_BACK, BUBBLE_FALL = 1.1, 0.5, 0.6, 0.55
BUBBLE_HEIGHT = ((-90.0, 2.6), (-30.0, 2.2), (0.0, 1.6), (90.0, 0.8), (180.0, 1.6), (-150.0, 2.2))
BUBBLE_BANDS = [(-99.0, 0x90, 0.12), (1.3, 0x92, 0.2), (3.4, 0x94, 0.28), (5.4, 0x96, 0.34), (7.4, 0x98, 0.4),
                (9.6, 0x9a, 0.48), (12.0, 0x9c, 0.54)]
BUBBLE_CORE = (-165.0, -105.0, 0.55, 0.3)
BUBBLE_CORE_BANDS = ((0.0, 0x9f, 0.6),)
BUBBLE_CAP = 3.2
BUBBLE_GLASS = (0x93, 0.3, 0.15)  # (palette index, alpha, emission)
# The highlights: the big one the cap's bands round its middle (its heat there and its fall a pixel out), the small one
# a lens (its middle, half-axes, lift, bands from its middle out).
BUBBLE_HI = ((2.6, 3.0), (16.0, 4.5))
BUBBLE_CAP_BANDS = [(-99.0, None, 0.0), (5.5, 0x9a, 0.48), (10.5, 0x9f, 0.6)]
BUBBLE_LENS = ((-2.5, 3.5), 1.7, 1.6, 0.35, ((0.0, 0x99, 0.46), (0.55, 0x94, 0.28)))
BUBBLE_PIECES = [(("shots", 239), (-12.0, 0.0, 0.0, 14.0)), (("shots", 240), (0.0, 12.0, 0.0, 14.0)),
                 (("shots", 258), (-12.0, 0.0, -14.0, 0.0)), (("shots", 259), (0.0, 12.0, -14.0, 0.0))]
BUBBLE_GLOW = (24, 0.3, 0x99, (-0.5, -2.0))  # (size, strength, index, its point in the whole)


def drop_downward(obj, limit=-0.3):
    """Deletes the faces turned down (a cap's or a lens's flat underside: under glass it would show)."""
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.normal_update()
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.normal.z < limit], context="FACES")
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def ellipse_point(spec, theta):
    (cx, cy), a, b = spec
    return cx + a * math.cos(theta), cy + b * math.sin(theta)


def build_bubble(name):
    mats = materials("charge_bubble", BUBBLE_BANDS)
    n = BUBBLE_SAMPLES
    thetas = [-math.pi + 2 * math.pi * j / n for j in range(n)]
    outer = [ellipse_point(BUBBLE_OUTER, t) for t in thetas]
    inner = [ellipse_point(BUBBLE_INNER, t) for t in thetas]
    us = [t / math.pi for t in thetas]
    crest_heat = kit.rim_curve(BUBBLE_CREST)
    crest_height = kit.rim_curve(BUBBLE_HEIGHT)

    def width_at(theta):
        (ox, oy), (ix, iy) = ellipse_point(BUBBLE_OUTER, theta), ellipse_point(BUBBLE_INNER, theta)
        return math.hypot(ox - ix, oy - iy)

    def heat(s, u):
        theta = u * math.pi
        top = crest_heat(theta)
        peak = min(max(BUBBLE_PEAK_IN / max(width_at(theta), 1e-3), 0.05), 0.5)
        if s < peak:
            return top * (1.0 - (1.0 - BUBBLE_EDGE) * ((peak - s) / peak) ** 2)
        return top - (top - BUBBLE_BACK) * ((s - peak) / (1.0 - peak)) ** BUBBLE_FALL
    ring = sonic.Wave(outer, inner, us, lambda u: crest_height(u * math.pi), heat, BUBBLE_BANDS, crest=0.38, back=1.25,
                      closed=True, waves=(4.0, 0.02, 1.9), gap=0.3)
    parts = [prune(ring.build(name + "_ring", mats))]
    # (the core along the crescent's brightest part)
    a0, a1, w, lift = BUBBLE_CORE
    j0 = (math.radians(a0) + math.pi) / (2 * math.pi) * n
    j1 = (math.radians(a1) + math.pi) / (2 * math.pi) * n
    mid = math.radians(0.5 * (a0 + a1))
    s_line = min(max(BUBBLE_PEAK_IN / width_at(mid), 0.05), 0.5)
    cmats = materials("charge_bubble_core", BUBBLE_CORE_BANDS, kit.CORE_ROUGHNESS)
    parts.append(sonic.crest_core(name + "_core", ring, s_line, j0, j1, w, lift, BUBBLE_CORE_BANDS, cmats, rings=16))
    # The glass cap over the middle, the big highlight in it.
    (hx, hy), a, b = BUBBLE_INNER

    def cap_top(x, y):
        rho2 = ((x - hx) / a) ** 2 + ((y - hy) / b) ** 2
        return BUBBLE_CAP * max(0.0, 1.0 - rho2) ** 0.5
    _, radius_from = kit.ellipse_dome(hx, hy, a, b, BUBBLE_CAP)
    hi, (hot, fall) = BUBBLE_HI
    hi_radius = radius_from(*hi)

    def cap_heat(u, phi):
        return hot - fall * u * hi_radius(phi)  # (by the distance from the highlight's middle)
    index, alpha, glow = BUBBLE_GLASS
    pal = k.level_palette()
    glass = k.material("charge_bubble_glass", palette=index, roughness=0.1, metallic=0.0, emission=pal[index],
                       emission_strength=glow, alpha=alpha)
    cap_mats = [glass] + [lit("charge_bubble_hi_%02x" % i, i, g, roughness=kit.CORE_ROUGHNESS)
                          for _, i, g in BUBBLE_CAP_BANDS[1:]]
    cap = kit.Dome(hi, radius_from(*hi), cap_top, cap_heat, BUBBLE_CAP_BANDS, segments=28, tongues=(5, 0.0, 1.0),
                   gap=0.2, middle_fractions=(0.5,), rim_fractions=(0.5, 0.8, 1.0))
    parts.append(drop_downward(cap.build(name + "_cap", cap_mats)))
    (lx, ly), rx, ry, lift, lbands = BUBBLE_LENS
    lmats = materials("charge_bubble_lens", lbands, kit.CORE_ROUGHNESS)
    parts.append(drop_downward(kit.dome_core(name + "_lens", (lx, ly), rx, ry, lift, lambda x, y: cap_top(x, y) + 0.04,
                                             lbands, lmats, segments=14, tongues=(3, 0.0, 1.0))))
    return parts


# === B267-B270 / B286-B289: the great arch (port 11's charge 5) =======================================================

# A Wave (polish_shot_sonic.py) between the arch's outer edge and its inner edge (right halves, apex first, both ending
# at the leg's tip; the whole's coordinates: x = c + 0.5 - 24, y = 13.5 - r), white over most of it between a green rim
# outside and a green inner edge (the heat: GREAT's along |u| and across), its crest high; dark green drips hanging from
# its inner edge (thin lofts rooted in its back: x, root y, tip y, half-width).
GREAT = dict(
    outer=[(0.0, 11.0), (4.0, 11.0), (6.0, 10.6), (8.0, 10.05), (10.0, 9.6), (12.0, 9.05), (14.0, 8.5), (15.5, 8.0),
           (17.0, 7.3), (18.5, 6.5), (20.0, 5.6), (21.0, 4.5), (21.6, 3.0), (22.3, 1.5), (22.8, 0.0), (23.0, -3.0),
           (23.0, -7.0), (23.0, -10.5), (22.75, -12.0)],
    inner=[(0.0, 0.4), (3.0, 0.5), (5.0, 0.3), (7.0, -0.2), (9.0, -0.6), (11.0, -1.4), (12.5, -2.2), (14.0, -3.0),
           (15.3, -4.0), (16.6, -5.2), (18.0, -6.2), (19.5, -7.0), (20.8, -8.0), (21.6, -9.3), (22.2, -10.8),
           (22.75, -12.0)],
    samples=73, height=((0.0, 3.4), (0.5, 3.1), (0.75, 2.4), (0.88, 1.6), (0.95, 0.9), (1.0, 0.0)),
    crest=0.42, back=0.9,
    along=((0.0, 17.0), (0.6, 16.9), (0.78, 16.4), (0.86, 13.4), (0.93, 9.6), (1.0, 6.0)),
    front=0.74, back_drop=0.74, peak=0.2, back_power=5.0)
GREAT_BANDS = [(-99.0, 0xc1, 0.16), (2.4, 0xc3, 0.22), (4.6, 0xc5, 0.3), (7.0, 0xc8, 0.4), (9.6, 0xca, 0.48),
               (11.8, 0xcc, 0.54), (14.0, 0xcf, 0.56), (15.6, 0x2f, 0.45)]
GREAT_DRIPS = [(0.0, 1.8, -2.1, 1.25), (-7.2, 0.6, -5.0, 1.5), (7.2, 0.6, -5.0, 1.5), (-15.5, -3.6, -8.0, 1.1),
               (15.5, -3.6, -8.0, 1.1), (-19.5, -6.4, -9.0, 0.8), (19.5, -6.4, -9.0, 0.8)]
# (the drips taper as teeth, bright green where they leave the arch, dark at their tips: the sprite's toothed fringe)
GREAT_DRIP_WIDTH = ((0.0, 0.0), (0.05, 0.85), (0.22, 1.0), (0.6, 0.55), (0.9, 0.18), (1.0, 0.0))
GREAT_DRIP_ALONG = ((0.0, 12.6), (0.3, 10.2), (0.6, 6.6), (1.0, 2.0))
GREAT_DRIP_ACROSS = ((0.0, 1.2), (1.0, 1.4))
GREAT_PIECES = [(("shots2", 267), (-24.0, -12.0, 0.0, 14.0)), (("shots2", 268), (-12.0, 0.0, 0.0, 14.0)),
                (("shots2", 269), (0.0, 12.0, 0.0, 14.0)), (("shots2", 270), (12.0, 24.0, 0.0, 14.0)),
                (("shots2", 286), (-24.0, -12.0, -14.0, 0.0)), (("shots2", 287), (-12.0, 0.0, -14.0, 0.0)),
                (("shots2", 288), (0.0, 12.0, -14.0, 0.0)), (("shots2", 289), (12.0, 24.0, -14.0, 0.0))]
GREAT_GLOW = (30, 0.38, 0xcc)  # (on 268 and 269, over the arch's shoulders: GREAT_GLOW_AT and its mirror)
GREAT_GLOW_AT = (-11.0, 6.0)


def build_great(name):
    mats = materials("charge_great", GREAT_BANDS)
    spec = GREAT
    outer, us = sonic.arch_path(spec["outer"], spec["samples"])
    inner, _ = sonic.arch_path(spec["inner"], spec["samples"])
    wave = sonic.Wave(outer, inner, us, sonic.height_curve(spec["height"]),
                      sonic.heat_field(spec["along"], spec["front"], spec["back_drop"], spec["peak"],
                                       spec["back_power"]), GREAT_BANDS, crest=spec["crest"], back=spec["back"],
                      waves=(8.0, 0.012, 1.9), gap=0.22)
    parts = [prune(wave.build(name + "_wave", mats))]
    for i, (x, root, tip, half) in enumerate(GREAT_DRIPS):
        width = kit.curve([(t, half * f) for t, f in GREAT_DRIP_WIDTH])
        loft = kit.Loft(x, root, tip, width, kit.loft_heat(GREAT_DRIP_ALONG, GREAT_DRIP_ACROSS),
                        GREAT_BANDS, depth=0.62, segments=5, tongues=(2.0, 0.02, 1.2), gap=0.25, width_gap=0.5,
                        head_fractions=(0.2,), tail_fractions=(0.5,))
        parts.append(prune(loft.build(name + "_drip%d" % i, mats)))
    return parts


# === The pieces of shots of several sprites ===========================================================================

def piece_name(key):
    sheet, sprite = key
    return "shot_charge_%s%d" % ("b" if sheet == "shots2" else "", sprite)


def cut_pieces(whole, pieces):
    """The whole cut into its sprites' pieces (open cuts: the pieces always fly together), each moved onto its sprite's
    centre: {key: [objects]}."""
    out = {}
    for key, box in pieces:
        cx, cy = (box[0] + box[1]) / 2, (box[2] + box[3]) / 2
        parts = []
        for obj in whole:
            piece = cut_open(obj, box)
            if piece is None:
                continue
            piece.data.transform(Matrix.Translation((-cx, -cy, 0.0)))
            piece.name = "%s_%s" % (obj.name, piece_name(key))
            parts.append(piece)
        out[key] = parts
    return out


def whole_mask(sheets, pieces, w, h):
    """The sprites' masks put together as the whole (w x h) is."""
    m = [[False] * w for _ in range(h)]
    for (sheet, sprite), (x0, x1, y0, y1) in pieces:
        sm = k.sprite_mask(os.path.join(sheets, sheet + ".png"), sprite, large=False)
        c0, r0 = int(round(x0 + w / 2)), int(round(h / 2 - y1))
        for r, row in enumerate(sm):
            for c, v in enumerate(row):
                if v:
                    m[r0 + r][c0 + c] = True
    return m


# === The models and their lines =======================================================================================

GLOW = {  # 1x1 models: (size, strength, palette index), at the hot point
    "shot_charge_219": (15, 0.5, 0x7b), "shot_charge_218": (14, 0.5, 0x7b), "shot_charge_b78": (15, 0.48, 0x7b),
    "shot_charge_b81": (12, 0.45, 0x7c)}


class Model:
    """A model of one sprite: name, its sprite (sheet, n), builder (name -> (parts, its hot point: the glow's)), what it
    is."""

    def __init__(self, name, key, builder, what):
        self.name, self.key, self.builder, self.what = name, key, builder, what


def single_models():
    out = []
    for name, (key, bolts, what) in CROWNS.items():
        hot = (0.5 if key[1] == 218 else 0.5, 4.2)
        out.append(Model(name, key, lambda name, key=key, bolts=bolts, hot=hot: (build_crown(name, key, bolts), hot),
                         what))
    out.append(Model("shot_charge_b78", ("shots2", 78), lambda name: (build_arch(name), (0.0, 3.4)),
                     "an arch of fire (port 15's charges 4-5)"))

    def drop(name):
        parts, spec = build_small_drop(name)
        return parts, spec["core"][:2]
    out.append(Model("shot_charge_b81", ("shots2", 81), drop,
                     "a white-hot drop (ports 10, 27-38: charges 4-5, the side shots)"))
    return out


def write_cfg(path, models, shots):
    with open(path, "a") as out:
        out.write("\n".join(models + shots) + "\n")


def glow_text(size, strength, index, dx, dy):
    return "glow=%d:%.2f:%d:%.2f:%.2f" % (size, strength, index, round(dx, 2) + 0.0, round(dy, 2) + 0.0)


def export_whole(label, whole, pieces, options, size, glows):
    """Exports a whole's pieces: {key: name}; glows: {key: (size, strength, index, x, y)} (the glow's point in the
    whole's coordinates), the other pieces glow=1:0. Returns (model lines, shot lines)."""
    outdir = options.get("outdir", OUTDIR)
    only = set(options["only"].split(",")) if "only" in options else None
    sheets = options.get("check")
    height = max(v.co.z for o in whole for v in o.data.vertices)
    print("%s: whole %d triangles, height %.2f" % (label, mk.triangles(whole), height))
    if sheets:
        mk.compare(label, mk.coverage(whole, size[0], size[1]), whole_mask(sheets, pieces, *size))
    if "preview" in options:
        bpy.context.scene.view_settings.view_transform = "Standard"
        view(options["preview"] + label.replace(" ", "_"), whole, size=size)
    cut = cut_pieces(whole, pieces)
    for o in whole + [o for parts in cut.values() for o in parts]:
        o.hide_render = True
    models, shots = [], []
    for key, box in pieces:
        name, parts = piece_name(key), cut[key]
        cx, cy = (box[0] + box[1]) / 2, (box[2] + box[3]) / 2
        models.append("model %-18s shots/%s.glb origin" % (name, name))
        if key in glows:
            gs, strength, index, gx, gy = glows[key]
            g = glow_text(gs, strength, index, gx - cx, cy - gy)
        else:
            g = "glow=1:0"
        shots.append("shot %-6s %-3d %-18s height=%.2f %s" % (key[0], key[1], name, -height / 2, g))
        if only is not None and name not in only:
            continue
        for o in parts:
            o.hide_render = False
        bpy.context.view_layer.update()
        if sheets:
            mk.compare("%s (%s %d)" % (name, key[0], key[1]), mk.coverage(parts, 12, 14),
                       k.sprite_mask(os.path.join(sheets, key[0] + ".png"), key[1], large=False))
        bpy.context.scene.view_settings.view_transform = "Standard"
        mk.report(name, parts, os.path.join(outdir, name + ".glb"))
        if "preview" in options and "pieces" in options:
            view(options["preview"] + name, parts)
        for o in parts:
            o.hide_render = True
    return models, shots


def wanted(options, names):
    only = set(options["only"].split(",")) if "only" in options else None
    return only is None or any(n in only for n in names)


def build():
    options = k.args()
    outdir = options.get("outdir", OUTDIR)
    sheets = options.get("check")
    for m in single_models():
        if not wanted(options, [m.name]):
            continue
        k.reset()
        parts, hot = m.builder(m.name)
        parts = triangulate(parts)
        bpy.context.view_layer.update()
        print("== %s (%s %d): %s; hot point %.2f %.2f" % (m.name, m.key[0], m.key[1], m.what, hot[0], hot[1]))
        if sheets:
            kit.check_lines(m.name, parts, os.path.join(sheets, m.key[0] + ".png"), [(m.key[1], 0, 0, 0)], hot)
        bpy.context.scene.view_settings.view_transform = "Standard"
        mk.report(m.name, parts, os.path.join(outdir, m.name + ".glb"))
        if "cfg" in options:
            size, strength, index = GLOW[m.name]
            write_cfg(options["cfg"], ["model %-18s shots/%s.glb" % (m.name, m.name)],
                      ["shot %-6s %-3d %-18s %s" % (m.key[0], m.key[1], m.name,
                                                   glow_text(size, strength, index, hot[0], -hot[1]))])
        if "preview" in options:
            view(options["preview"] + m.name, parts)
    # The big drop: B100 above B119.
    names = [piece_name(key) for key, _ in BIG_DROP_PIECES]
    if wanted(options, names):
        k.reset()
        parts, spec = build_big_drop("charge_bigdrop")
        whole = triangulate(parts)
        bpy.context.view_layer.update()
        print("== big drop: axis x %.2f, nose %.1f, tail %.1f, core %s" % (
            spec["x"], spec["nose"], spec["tail"], " ".join("%.2f" % v for v in spec["core"])))
        models, shots = export_whole("big drop", whole, BIG_DROP_PIECES, options, (12, 28),
                                     {("shots2", 100): (17, 0.45, 0x7c, spec["core"][0], spec["core"][1])})
        if "cfg" in options:
            write_cfg(options["cfg"], models, shots)
    # The bubble: 239 240 above 258 259.
    if wanted(options, [piece_name(key) for key, _ in BUBBLE_PIECES]):
        k.reset()
        whole = triangulate(build_bubble("charge_bubble"))
        bpy.context.view_layer.update()
        size, strength, index, (gx, gy) = BUBBLE_GLOW
        models, shots = export_whole("bubble", whole, BUBBLE_PIECES, options, (24, 28),
                                     {("shots", 239): (size, strength, index, gx, gy)})
        if "cfg" in options:
            write_cfg(options["cfg"], models, shots)
    # The twin fireballs, frame by frame.
    for f in range(len(TWIN_PLACES)):
        pieces = twin_pieces(f)
        if not wanted(options, [piece_name(key) for key, _ in pieces]):
            continue
        k.reset()
        whole = triangulate(build_twins(f))
        bpy.context.view_layer.update()
        if sheets and f == 0:
            print("twin fireballs: ball centres frame by frame %s" % (TWIN_PLACES,))
        size, strength, index = TWIN_GLOW
        (ax, ay), (bx, by) = TWIN_PLACES[f]
        glows = {pieces[0][0]: (size, strength, index, ax + BALL_HOT[0] * 0.5, ay + BALL_HOT[1] * 0.5),
                 pieces[3][0]: (size, strength, index, bx + BALL_HOT[0] * 0.5, by + BALL_HOT[1] * 0.5)}
        models, shots = export_whole("twin fireballs frame %d" % f, whole, pieces, options, (24, 28), glows)
        if "cfg" in options:
            write_cfg(options["cfg"], models, shots)
    # The great arch: 267-270 above 286-289.
    if wanted(options, [piece_name(key) for key, _ in GREAT_PIECES]):
        k.reset()
        whole = triangulate(build_great("charge_great"))
        bpy.context.view_layer.update()
        size, strength, index = GREAT_GLOW
        gx, gy = GREAT_GLOW_AT
        models, shots = export_whole("great arch", whole, GREAT_PIECES, options, (48, 28),
                                     {("shots2", 268): (size, strength, index, gx, gy),
                                      ("shots2", 269): (size, strength, index, -gx, gy)})
        if "cfg" in options:
            write_cfg(options["cfg"], models, shots)


if __name__ == "__main__":
    build()
