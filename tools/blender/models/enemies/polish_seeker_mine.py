"""ASTEROID?'s seeker mine (sheet P sprite 171 and its frames 190 209 228 247 266 285, 1x1: 12 x 14 pixels; enemy 199,
armour 2), new (2026-10-22, round 37: it had no model; the game drew its pixelated stand-in). models.cfg: model
seeker_mine enemies/seeker_mine.glb and model seeker_mine_190 / _209 / _228 / _247 / _266 / _285; sprite p 171
seeker_mine yaw=0 glow=6:0.15:116; frame p 190 seeker_mine_190 ... frame p 285 seeker_mine_285.

Where it comes from (the enemy data, tools/content/tyrdata.py; ASTEROID?'s events, tools/content/tyrevents.py): the
small blocks with lids (P 279, enemy 198: polish_block_parts.py) launch it (their launch type, 199) once the events have
opened their lids and given them a launch frequency (t200-220 and t1096: event 24 opens the lids, event 31 sets
launchfreq 40, then 1 and 10): it rises from the block's well (the block's frames 237 and 239 show its cross glowing in
the well) onto ground 2 (slots 75-99, drawn on the ground layer) and homes on the player (xaccel and yaccel 94, xrev and
yrev 5). It animates always (171 190 209 228 247 266 285 266 ... 190: the cross heats from dark red to white and back);
no other enemy shows these sprites (catalog.json and launched.txt miss it: its launcher's frequency comes from the
events); no twin (no other sprite is these pixels moved, mirrored or recoloured).

As the sprite draws it (columns and rows of the 12 x 14 sprite): a grey ball (columns 2-10, rows 3-11, ramp 0's 0x04-0x0a,
lit at its upper right, darker below and at its left) in a dark outline (0x20), two little studs on its top (row 3:
columns 4-5 and 8), a small plus-shaped lamp in its middle (column 6, row 7: arms a pixel wide, three long) dark red in
171 (0x70 round a 0x71 heart) heating through 190 (0x73 0x75), 209 (0x75 0x77), 228 (0x77 0x79), 247 (0x79 0x7b), 266
(0x7b 0x7d) to 285 (0x7d 0x7f), the ball round it lit more and more (0x0b-0x0e in 285).

Built as such a mine for the game's camera: a ball lofted from explicit rings (BALL: centre and radius), grey steel in
three shades by how the game's sun lights it, a little emission in its lighter grey (balls read near black from the
slanted camera); the lamp a plus-shaped inset glass standing a little out of the ball where the camera sees the
sprite's lamp (the ball's point along the camera's line of sight from its middle: VIEW_TILT), in a dark bezel; two studs
on its far rim. The frames are the same mesh with the lamp's glass and heart in their colours and glows (0.12 to 0.65:
FRAMES) and, in the hotter ones, the ball round the lamp painted lighter (WARM). Centred in height: the game draws it
at ground 2's height (the ground enemies' layer).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; the origin is the
sprite's middle (column c's left edge x = c - 6, row r's top edge y = 7 - r).

Replaces nothing (new). Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (its
outline as the camera sees it against its sprite), --preview <prefix>, --only <model,...>.
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
import polish_asteroid_kit as ak  # noqa: E402

BALL = ((0.5, -0.5, 0.0), 4.45)          # its middle (x, y, z) and radius (columns 2-10, rows 3-11)
VIEW = Vector((0.0, -math.sin(math.radians(20.0)), math.cos(math.radians(20.0))))
LAMP_ARM, LAMP_W = 1.55, 0.5             # the lamp's arms: from its middle to their ends, half their width
STUDS = [(-1.0, 0.55), (2.5, 0.45)]      # the studs on its far rim (x, radius)
# The frames: sprite, the lamp's glass and heart (palette index, emission), how far the ball round it is lit.
FRAMES = [(171, (0x70, 0.12), (0x71, 0.18), 0.0), (190, (0x73, 0.22), (0x75, 0.3), 0.0),
          (209, (0x75, 0.3), (0x77, 0.38), 0.0), (228, (0x77, 0.36), (0x79, 0.45), 0.6),
          (247, (0x79, 0.42), (0x7b, 0.52), 1.2), (266, (0x7b, 0.5), (0x7d, 0.58), 1.8),
          (285, (0x7d, 0.56), (0x7f, 0.65), 2.4)]
WARM = 2.6                               # the lit ring round the lamp's radius (on the ball, as the camera sees it)


def model_name(sprite):
    return "seeker_mine" if sprite == 171 else "seeker_mine_%d" % sprite


def materials(frame):
    sprite, glass, heart, warm = frame
    m = {"steel_d": ak.pal("mine_steel_d", 0x07, 0.35, 0.35, 0.14, 0x08),
         "steel": ak.pal("mine_steel", 0x09, 0.35, 0.33, 0.16, 0x09),
         "steel_l": ak.pal("mine_steel_l", 0x0b, 0.35, 0.3, 0.18, 0x0a),
         "bezel": ak.pal("mine_bezel", 0x03, 0.4, 0.45),
         "stud": ak.pal("mine_stud", 0x04, 0.5, 0.35),
         "glass": ak.pal("mine_glass_%x" % glass[0], glass[0], 0.0, 0.25, glass[1]),
         "heart": ak.pal("mine_heart_%x" % heart[0], heart[0], 0.0, 0.2, heart[1])}
    if warm:
        m["warm"] = ak.pal("mine_warm_%d" % sprite, 0x0c if warm < 1.5 else 0x0d, 0.3, 0.3, 0.16 + 0.06 * warm, 0x0d)
    return m


def ball_mesh(name, m, frame):
    """The ball, lofted from explicit rings about the camera's line of sight (so that its rings sit round the lamp),
    painted by the game's sun (and the warm ring round the lamp in the hot frames)."""
    (cx, cy, cz), r = BALL
    axis = VIEW
    side = Vector((1.0, 0.0, 0.0))
    up = axis.cross(side).normalized()
    centre = Vector((cx, cy, cz))
    rings = []
    count, around = 18, 48
    for i in range(1, count):
        p = math.pi * i / count                         # from the lamp (0) to the far side (pi)
        rr, h = r * math.sin(p), r * math.cos(p)
        rings.append([centre + axis * h + (side * math.cos(2 * math.pi * j / around) +
                                           up * math.sin(2 * math.pi * j / around)) * rr for j in range(around)])
    obj = k.loft(name, rings[::-1], m["steel"], start_point=centre - axis * r, end_point=centre + axis * r)
    k.smooth(obj, 80)
    warm = frame[3]

    def pick(c, n):
        p = c - centre
        if warm and p.dot(axis) > 0 and (p - axis * p.dot(axis)).length < WARM + 0.25 * warm:
            return m["warm"]
        lit = n.dot(ak.SUN)
        return m["steel_l"] if lit > 0.7 else m["steel"] if lit > 0.2 else m["steel_d"]
    mk.paint(obj, pick)
    return obj


def lamp(m):
    """The plus-shaped lamp, standing a little out of the ball facing the camera where the sprite draws it, in its bezel;
    its heart a smaller plus over it."""
    (cx, cy, cz), r = BALL
    centre = Vector((cx, cy, cz)) + VIEW * (r - 0.35)
    side = Vector((1.0, 0.0, 0.0))
    up = VIEW.cross(side).normalized()
    parts = []
    for name, arm, w, depth, out, mat in (("lamp_bezel", LAMP_ARM + 0.3, LAMP_W + 0.28, 0.6, 0.12, m["bezel"]),
                                          ("lamp_glass", LAMP_ARM, LAMP_W, 0.6, 0.3, m["glass"]),
                                          ("lamp_heart", LAMP_W * 1.1, LAMP_W * 0.9, 0.6, 0.38, m["heart"])):
        plus = [(w, w), (w, arm), (-w, arm), (-w, w), (-arm, w), (-arm, -w), (-w, -w), (-w, -arm), (w, -arm),
                (w, -w), (arm, -w), (arm, w)]
        base = [centre + side * u + up * v + VIEW * (out - depth) for u, v in plus]
        top = [centre + side * u + up * v + VIEW * out for u, v in plus]
        obj = ak.section_loft(name, [base, top], mat)
        parts.append(obj)
    return parts


def studs(m):
    (cx, cy, cz), r = BALL
    out = []
    for i, (x, s) in enumerate(STUDS):
        dx = x - cx
        y = cy + math.sqrt(max(0.0, r * r - dx * dx)) * 0.92
        out.append(mk.ball("stud%d" % i, (x, y, cz + 0.6), (s, s, s), m["stud"], 12, 6))
    return out


def build_mine(frame, prefix="mine"):
    """The mine's parts for a frame (used by polish_block_parts.py for the mine rising in the block's well too)."""
    m = materials(frame)
    return [ball_mesh(prefix + "_ball", m, frame)] + lamp(m) + studs(m)


def build():
    options = k.args()
    out = mk.outdir(options)
    only = set(options["only"].split(",")) if "only" in options else None
    for frame in FRAMES:
        name = model_name(frame[0])
        if only and name not in only:
            continue
        k.reset()
        bpy.context.scene.view_settings.view_transform = "Standard"
        parts = build_mine(frame)
        mask = None
        if "check" in options:
            mask = k.sprite_mask(os.path.join(options["check"], "enemy_P.png"), frame[0], large=False)
        ak.finish(name, parts, (0.0, 0.0), out, options, mask, size=(12, 14), world=True, ground=False,
                  label="%s (P %d) as the camera sees it" % (name, frame[0]))


if __name__ == "__main__":
    build()
