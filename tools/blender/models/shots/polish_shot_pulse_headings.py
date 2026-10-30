"""The pulse's other headings (shots sheet sprites 1 2 3 5 39 40 41 43 77 78 163 164 182 183 201 202 203 220-222 275-282
294-301, all 1x1: 12 x 14 cells), modelled (2026-10-29, round 2 of the energy shots' models): the Pulse-Cannon's bolts
(polish_shot_pulse.py: shot_pulse one bolt, _2 two, _3 three, _4 four narrow, _5 five) drawn flying other ways.

Who fires them (sprites as models.cfg writes them; ports by their number in the shop's lists, power levels 1-11):
  the Multi-Cannon front (port 2, the first shop): 201 202 (tilted 18 degrees out) at power 2-3, 5-6, 9-10, 163 164
    (45 degrees out) at 4-6, 279 280 (two bolts tilted out) at 11, with 58 or 59 up the middle (and the fireballs 121
    122 at 7-11, another family's);
  the Multi-Cannon rear (port 10, the first shop), mode 1: 39 1 (one bolt sideways, left and right) at power 1-2, 8;
    40 2 (two) at 3, 41 3 (three) at 5, 6, 9, 203 222 (four) at 10, 43 5 (five) at 11; 281 282 300 301 (one bolt 22.5
    degrees off sideways, up and down) and 77 (one down the screen) at 4; 77 at 6; 277 278 296 297 (two bolts 22.5 off
    sideways) at 7-11; mode 2: 281 at 1, 281 282 at 2-3 (300 301 at 3), 163 164 183 182 (45 degrees) and 77 at 4,
    277 278 with 183 182 at 5, 6 (and 77 at 6), with 295 294 (two bolts, 45 degrees back) and 77 at 7-9, 298 299 (two
    bolts 22.5 degrees off down) at 9-11, 39 1 at 8, 10, 40 2 at 11;
  the Hyper Pulse (port 27): 279 280 at power 9-11; the NortShip Spreader (port 37, the Nort Ship's own gun): 163 164,
    281 282, 39 1, 201 202 and 77; the second player's guns in two-player games: the linked turret (shots.c linkMultiGr,
    one bolt, and linkMult2Gr, two, 16 headings each: heading k flies k x 22.5 degrees from straight down,
    counter-clockwise on the screen) and the charge cannon (461: 279 280);
  enemies: weapons 81 (TYRIAN's boss and HOLES', TYRIAN X's, NOSE DRIP's turrets: a burst of 77 58 182 163 1 183 164
    flying every way, whatever heading the sprites show) and 78 (58 down with 201 202 down and out: TYRIAN, GYGES,
    TYRIAN X), once fire override events give the turrets a frequency. (The catalogue also gives weapons 254 and 255 to
    enemies of MINES, MINEMAZE, GAUNTLET, DELI, HARVEST and the asteroid levels, but an enemy's turret 251-255 is a
    special case in tyrian2.c, magnets and the like, that fires no shot: weapons 254 and 255 are only the rear
    Multi-Cannon's power 1 and 2.)
None is animated (weapani 0); every sprite shows its bolts at one heading. Models follow the sprite (the heading it
draws), not the way a weapon flies it.

As the sprites draw them: the same bolts of fire (ramp 7: dark red 0x71-0x75 tails, orange 0x77-0x78 bodies, yellow
0x7a-0x7c heads) redrawn by hand at each heading. One bolt: up (58), down (77, 58 turned upside down), sideways (1 39),
22.5 degrees off up or down (201 202 220 221: a bolt 4 pixels wide and 11 long in a cell's corner), 45 degrees (163 164
182 183: drawn longer, 14 pixels along the diagonal, with a pale yellow 0x7d head and a dark 0x12 pixel at its tip) and
67.5 degrees (281 282 300 301). Two bolts: up (59), down (78), sideways (2 40) 6 pixels apart as 59 draws them; at the
other headings the single bolt drawn twice, 4 pixels apart along the screen's x (279 280 298 299) or y (277 278 296
297), or 2 and 3 pixels apart (275 276 294 295): only 3.5-3.7 pixels apart across the heading (59: 6) and one of the two
0.7-1.5 pixels behind the other. Three, four and five bolts only sideways (3 41, 222 203, 5 43): 60, 165 and 62 turned a
quarter turn, as drawn.

The models: every heading takes the models of the bolts it draws turned with yaw= (the heading, clockwise from up:
(180 - 22.5 k) mod 360 for heading k of the turret's tables) and moved with at=<dx>:<dy> (game pixels, dy down the
screen) onto the sprite's pixels: the hand-drawn sprites don't put their bolts where the turned model would land (up to
3.05 pixels off). Each offset was measured by laying the reference sprite (58 for shot_pulse, 59, 60, 165, 62) turned by
the yaw onto the heading sprite's pixels, both blurred (0.6 pixels), scored by the overlap and by the heat (the palette
shade) together, at 0.05 pixels (HEADINGS below; the scratch tool register.py of round 2; the centroid method of round 1
gave the same within 0.07 pixels, but for the 45-degree bolts, which it put 0.75 pixels further back). Built here: the
two bolts the tilted twins draw, which no committed model has: shot_pulse_h2l and _h2r (the 22.5 and 67.5 degree twins:
a second bolt 3.70 pixels to the right of the first and 1.53 behind it, or to its left; the first where shot_pulse's
bolt is, so each line takes its single bolt's yaw= and at=) and shot_pulse_h2l_45 and _h2r_45 (the 45 degree twins, the
bolts 3.54 apart, one 0.71 behind the other, both moved off shot_pulse's place as the sprites draw them: 163's bolt +
(2, 0) and + (0, 3) for 275 ...). Each bolt is shot_pulse's own (polish_shot_pulse.py's builders, imported: the sheath
of fire in 8 bands of ramp 7 on the mesh's rings, the raised core 0x7e/0x7d, its hot line on the left as 58 draws it),
664 triangles, 10 materials a model. Every line's glow= is its model's (shot_pulse: 10 pixels at 0.5 in 0x7b on the
head, 2.5 pixels up its axis; _2: 13; _3: 15; _4: 15; _5: 16; the twins here: 12) turned and moved with it, onto the
heads.

Coordinates as in tyrkit (1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera, the origin at the
sprite's centre: pixel 6, 7 of the cell), authored flying up the screen (yaw 0).

models.cfg (the shots section, after the pulse block): `--cfg <file>` writes the block's lines (the model lines and
the 36 shot lines with their yaw=, at= and glow=, computed from HEADINGS and GLOWS).

Run: Blender -b --factory-startup -P tools/blender/models/shots/polish_shot_pulse_headings.py -- [--only <name,...>]
     [--outdir <dir>] (default assets/models/shots) [--check <sheets dir>] (every heading line's model, turned and moved
     as its line says, against its sprite in <dir>/shots.png, from TYR3D_EXTRACT; builds the committed pulse models for
     that without writing them) [--preview <prefix>] (top, three-quarter and game-camera views) [--cfg <file>]
"""
import math
import os
import sys

import bpy
from mathutils import Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_shot_pulse as pp  # noqa: E402
from polish_shot_pulse import k, mk  # noqa: E402

OUTDIR = pp.OUTDIR

# --- The twins built here ---------------------------------------------------------------------------------------------
# name: (its bolts: offsets (x, y) of shot_pulse's bolt (sprite 58's, as built), what it is). The offsets are the
# sprites' pixel shifts turned back into the model's frame: 279 = 201 + 201 moved 4 pixels right (yaw 337.5: the second
# bolt 3.70 to the right of the first, 1.53 behind); 275 = 163 moved (2, 0) + 163 moved (0, 3) (yaw 315).
R45 = 2.0 * math.sqrt(0.5)   # (2, 0) on the screen at yaw 45 / 315 ...
D45 = 3.0 * math.sqrt(0.5)   # (0, 3)
TWINS = [
    ("shot_pulse_h2l", [(0.0, 0.0), (3.6955, -1.5307)],
     "two bolts, the right one 3.70 pixels out and 1.53 behind (the 22.5 and 67.5 degree twins)"),
    ("shot_pulse_h2r", [(0.0, 0.0), (-3.6955, -1.5307)],
     "two bolts, the left one 3.70 pixels out and 1.53 behind (their mirror images)"),
    ("shot_pulse_h2l_45", [(-R45, -R45), (D45, -D45)],
     "two bolts 3.54 pixels apart, the right one 0.71 behind (the 45 degree twins)"),
    ("shot_pulse_h2r_45", [(R45, -R45), (-D45, -D45)],
     "two bolts 3.54 pixels apart, the left one 0.71 behind (their mirror images)"),
]

# --- The headings -----------------------------------------------------------------------------------------------------
# sprite: (model, yaw, at dx, at dy (game pixels, dy down the screen), what it is). Yaws are the headings the sprites
# draw (nominal: k x 22.5; the fitted yaws were within 2 degrees of them); offsets measured (see the docstring).
HEADINGS = {
    # one bolt (shot_pulse = 58)
    77: ("shot_pulse", 180.0, 0.0, 0.0, "one bolt, down (Multi-Cannon rear, enemies' bursts)"),
    221: ("shot_pulse", 157.5, 2.0, 0.4, "one bolt, down and right (the second player's turret)"),
    183: ("shot_pulse", 135.0, 0.5, 1.55, "one bolt, 45 degrees down and right (Multi-Cannon rear)"),
    301: ("shot_pulse", 112.5, -0.65, 3.05, "one bolt, right and down (Multi-Cannon rear)"),
    1: ("shot_pulse", 90.0, -1.0, -1.0, "one bolt, right (Multi-Cannon rear, enemies)"),
    282: ("shot_pulse", 67.5, -0.6, -3.0, "one bolt, right and up (Multi-Cannon rear)"),
    164: ("shot_pulse", 45.0, 0.55, -1.5, "one bolt, 45 degrees up and right (Multi-Cannon)"),
    202: ("shot_pulse", 22.5, 2.05, -0.35, "one bolt, up and right (Multi-Cannon front)"),
    201: ("shot_pulse", 337.5, -2.0, -0.4, "one bolt, up and left (Multi-Cannon front)"),
    163: ("shot_pulse", 315.0, -0.5, -1.55, "one bolt, 45 degrees up and left (Multi-Cannon)"),
    281: ("shot_pulse", 292.5, 0.65, -3.05, "one bolt, left and up (Multi-Cannon rear)"),
    39: ("shot_pulse", 270.0, 1.0, -1.0, "one bolt, left (Multi-Cannon rear, enemies)"),
    300: ("shot_pulse", 247.5, 0.6, 3.0, "one bolt, left and down (Multi-Cannon rear)"),
    182: ("shot_pulse", 225.0, -0.55, 1.5, "one bolt, 45 degrees down and left (Multi-Cannon rear)"),
    220: ("shot_pulse", 202.5, -2.05, 0.35, "one bolt, down and left (the second player's turret)"),
    # two bolts: as 59 (6 pixels apart) down and sideways; the tilted twins here, on their single bolt's yaw and at
    78: ("shot_pulse_2", 180.0, 0.0, 0.0, "two bolts, down (the second player's turret)"),
    2: ("shot_pulse_2", 90.0, -1.0, 0.0, "two bolts, right (Multi-Cannon rear)"),
    40: ("shot_pulse_2", 270.0, 1.0, 0.0, "two bolts, left (Multi-Cannon rear)"),
    299: ("shot_pulse_h2l", 157.5, 2.0, 0.4, "two bolts, down and right (Multi-Cannon rear)"),
    279: ("shot_pulse_h2l", 337.5, -2.0, -0.4, "two bolts, up and left (Multi-Cannon front, Hyper Pulse)"),
    278: ("shot_pulse_h2l", 67.5, -0.6, -3.0, "two bolts, right and up (Multi-Cannon rear)"),
    296: ("shot_pulse_h2l", 247.5, 0.6, 3.0, "two bolts, left and down (Multi-Cannon rear)"),
    280: ("shot_pulse_h2r", 22.5, 2.05, -0.35, "two bolts, up and right (Multi-Cannon front, Hyper Pulse)"),
    298: ("shot_pulse_h2r", 202.5, -2.05, 0.35, "two bolts, down and left (Multi-Cannon rear)"),
    297: ("shot_pulse_h2r", 112.5, -0.65, 3.05, "two bolts, right and down (Multi-Cannon rear)"),
    277: ("shot_pulse_h2r", 292.5, 0.65, -3.05, "two bolts, left and up (Multi-Cannon rear)"),
    276: ("shot_pulse_h2l_45", 45.0, 0.55, -1.5, "two bolts, 45 degrees up and right (the second player's turret)"),
    294: ("shot_pulse_h2l_45", 225.0, -0.55, 1.5, "two bolts, 45 degrees down and left (Multi-Cannon rear)"),
    295: ("shot_pulse_h2r_45", 135.0, 0.5, 1.55, "two bolts, 45 degrees down and right (Multi-Cannon rear)"),
    275: ("shot_pulse_h2r_45", 315.0, -0.5, -1.55, "two bolts, 45 degrees up and left (the second player's turret)"),
    # three, four and five bolts: 60, 165 and 62 a quarter turn round, as drawn
    3: ("shot_pulse_3", 90.0, -1.0, 0.0, "three bolts, right (Multi-Cannon rear)"),
    41: ("shot_pulse_3", 270.0, 1.0, 0.0, "three bolts, left (Multi-Cannon rear)"),
    222: ("shot_pulse_4", 90.0, -1.0, 0.0, "four narrow bolts, right (Multi-Cannon rear)"),
    203: ("shot_pulse_4", 270.0, 1.0, 0.0, "four narrow bolts, left (Multi-Cannon rear)"),
    5: ("shot_pulse_5", 90.0, -1.0, 0.0, "five bolts in an arrowhead, right (Multi-Cannon rear)"),
    43: ("shot_pulse_5", 270.0, 1.0, 0.0, "five bolts in an arrowhead, left (Multi-Cannon rear)"),
}

# The glows (models.cfg's glow=, in place of the automatic one): model: (size, strength, palette index, where on the
# model (x, y up), flying up): the pulse block's (polish_shot_pulse.py), and the twins' between their two heads.
HEAD = 2.5  # shot_pulse's glow: 2.5 pixels up its axis from the cell's centre


def twin_head(bolts):
    return (sum(b[0] for b in bolts) / len(bolts), sum(b[1] for b in bolts) / len(bolts) + HEAD)


GLOWS = {
    "shot_pulse": (10, 0.5, 0x7b, (0.0, HEAD)),
    "shot_pulse_2": (13, 0.5, 0x7b, (0.0, 2.5)),
    "shot_pulse_3": (15, 0.5, 0x7b, (0.0, 1.5)),
    "shot_pulse_4": (15, 0.5, 0x7b, (0.0, 1.0)),
    "shot_pulse_5": (16, 0.5, 0x7b, (0.0, 1.5)),
}
for _name, _bolts, _ in TWINS:
    GLOWS[_name] = (12, 0.5, 0x7b, twin_head(_bolts))


def turned(x, y, yaw):
    """A model point turned by yaw (clockwise on the screen, as the game turns shots), model coordinates."""
    t = math.radians(yaw)
    return x * math.cos(t) + y * math.sin(t), -x * math.sin(t) + y * math.cos(t)


def fmt(v):
    s = ("%.2f" % v).rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def shot_line(sprite):
    """The models.cfg line of a heading: its model turned and moved, its glow on the turned heads."""
    model, yaw, dx, dy, what = HEADINGS[sprite]
    size, strength, colour, (hx, hy) = GLOWS[model]
    gx, gy = turned(hx, hy, yaw)
    glow = "glow=%d:%s:%d:%s:%s" % (size, fmt(strength), colour, fmt(gx + dx), fmt(-gy + dy))
    at = " at=%s:%s" % (fmt(dx), fmt(dy)) if dx or dy else ""
    return "shot shots %-3d %-17s yaw=%-5s%s" % (sprite, model, fmt(yaw), at), glow, what


def cfg_lines():
    lines = ["model %-17s shots/%s.glb" % (name, name) for name, _, _ in TWINS]
    order = [77, 221, 183, 301, 1, 282, 164, 202, 201, 163, 281, 39, 300, 182, 220,
             78, 2, 40, 299, 279, 278, 296, 280, 298, 297, 277, 276, 294, 295, 275, 3, 41, 222, 203, 5, 43]
    rows = [shot_line(s) for s in order]
    w0 = max(len(r[0]) for r in rows)
    w1 = max(len(r[1]) for r in rows)
    for head, glow, what in rows:
        lines.append("%s %s  # %s" % (head.ljust(w0), glow.ljust(w1), what))
    return lines


# --- Building ---------------------------------------------------------------------------------------------------------

def build_bolts(name, offsets):
    """shot_pulse's bolt (polish_shot_pulse.py: wide(0, 0, 10), its heat sprite 58's) at each offset: the sheath of
    fire and its raised core, the heat moved with it (its hot line where 58 draws it)."""
    heat = pp.Heat(pp.shades(pp.grid(pp.SPRITES[58]), 7), pp.TOP, sigma=(0.55, 0.7))
    fire = [pp.lit(f"pulse_fire_{index:02x}", index, glow, roughness=pp.FIRE_ROUGHNESS)
            for _, index, glow in pp.FIRE_BANDS]
    parts = []
    for i, (dx, dy) in enumerate(offsets):
        base = pp.wide(0.0, 0, 10)
        bolt = pp.Bolt(base.x + dx, base.nose + dy, base.tail + dy, base.w, base.core)

        def moved(x, y, dx=dx, dy=dy):
            return heat(x - dx, y - dy)
        parts.append(pp.sheath(f"{name}_bolt{i}", bolt, moved, fire))
        core_mats = [pp.lit(f"pulse_core_{index:02x}", index, glow, roughness=pp.CORE_ROUGHNESS)
                     for _, index, glow in pp.WEDGE_BANDS]
        parts.append(pp.core(f"{name}_core{i}", bolt, moved, core_mats))
    return pp.triangulate(parts)


def build_any(name):
    """A model by name: a twin of this script, or a committed pulse model (for --check only)."""
    for twin, offsets, _ in TWINS:
        if twin == name:
            return build_bolts(name, offsets)
    for pulse, sprite, bolts, _ in pp.MODELS:
        if pulse == name:
            return pp.build_model(name, sprite, bolts)
    raise KeyError(name)


def check(parts, name, sheets):
    """Every heading line of the model: the model turned by its yaw and moved by its at= against the sprite."""
    frames = []
    for sprite, (model, yaw, dx, dy, what) in sorted(HEADINGS.items()):
        if model == name:
            frames.append((sprite, Matrix.Translation((dx, -dy, 0.0)) @ pp.turn(yaw),
                           f"shots {sprite} ({name} yaw {fmt(yaw)} at {fmt(dx)}:{fmt(dy)})"))
    if frames:
        pp.check_frames(parts, os.path.join(sheets, "shots.png"), frames, move_to_frame=False)


def build():
    options = k.args()
    only = set(options["only"].split(",")) if "only" in options else None
    outdir = options.get("outdir", OUTDIR)
    for name, offsets, what in TWINS:
        if only is not None and name not in only:
            continue
        k.reset()
        parts = build_bolts(name, offsets)
        bpy.context.view_layer.update()
        print(f"== {name}: {what}")
        if "check" in options:
            check(parts, name, options["check"])
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        mk.report(name, parts, os.path.join(outdir, name + ".glb"))
        if "preview" in options:
            pp.game_view(options["preview"] + name, parts)
    # The committed models' headings (checked only: nothing written).
    if "check" in options:
        for name in ("shot_pulse", "shot_pulse_2", "shot_pulse_3", "shot_pulse_4", "shot_pulse_5"):
            if only is not None and name not in only:
                continue
            k.reset()
            parts = build_any(name)
            bpy.context.view_layer.update()
            print(f"== {name} (committed; its headings checked, not written)")
            check(parts, name, options["check"])
    if "cfg" in options:
        with open(options["cfg"], "w") as f:
            f.write("\n".join(cfg_lines()) + "\n")
        print("wrote", options["cfg"])


if __name__ == "__main__":
    build()
