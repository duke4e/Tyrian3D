"""Batch AD of wave 3 (sheet H: GYGES, TORM, BONUS), GYGES' bronze worm and its small flying things, modelled
as the sprites look (models.cfg: yaw=0). GYGES' creatures in their pieces of tube wall are in wave3_ad_wall.py,
TORM's beetle in polish_torm_beetle.py, the waterfall of TORM and BONUS in wave3_ad_fall.py; the kit is
wave3_ad_kit.py, the pixels wave3_ad_art.py.

- gyges_worm_head_tip, gyges_worm_head_base (H 17 above 55; enemies 422 at (x, y - 28) and 423 at (x, y),
  one link, on the top layer or in the sky): the pointed head of GYGES' bronze worm, whose body segments
  are the bronze_yuanbao model (H 93, enemy 424, five of them 10 pixels apart below the head, each a link of
  its own that follows the one before) and whose tail is gyges_worm_tail: a bronze cone in tiers, a bright
  ridge down its middle, its base round. Like the segments (bronze_yuanbao is drawn centred in height) it
  is built round z = 0, so that head, body and tail lie at one height (origin).
- gyges_worm_tail (H 131, enemy 425, 10 pixels below the last segment): the worm's tail, a ribbed bronze
  shell with a ridge down its middle, a small dome at its front, little hooks at its shoulders and a point
  at its end.
- gyges_orb_s, gyges_orb_m, gyges_orb_l (H 89, 127, 91; enemies 417, 418, 419): GYGES' glossy green balls,
  which swing round over the grey stalk (wave3_ad_wall.py) in ever wider circles.
- gyges_spike_top, gyges_spike_tip (H 77 above 115; enemies 420 above 421, one movement): the green spike
  that swings widest of them, a faceted green knob on a ridged neck over a long pale-ridged point down the
  screen (origin; built round z = 0 like the balls).
- gyges_bone_eye (H 39; enemy 153, frames 39, 1, 3, 3, 3, 1, 39: the eye lights up): a ring of knobbly bone
  in a square of GYGES' tube wall round a dark pit with a green eye, which glows.

usage: Blender -b --factory-startup -P wave3_ad.py -- [--only name,name] [--preview <prefix>]
       [--check 1] [--stats 1]
"""
import math
import os
import sys

from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_ad_kit as kit  # noqa: E402
from wave3_ad_kit import art, k, sh, w, pal, Frame, Painter  # noqa: E402

OUTLINE = {0x01, 0x00, 0x10}


def spans(f):
    """For each row of a frame with pixels: (y of the row's middle, left x, right x)."""
    out = []
    for r, row in enumerate(f.g):
        cols = [c for c, v in enumerate(row) if v is not None]
        if cols:
            out.append((f.Y(r), cols[0] - f.ox, cols[-1] + 1 - f.ox))
    return out


def lathe_spans(name, f, mat, squash=0.62, inset=0.35, segments=40, power=2.0, crest=0.0, z=0.0, rows=None,
                smooth=1):
    """A body round a line along y through the sprite's rows: each row's span (less `inset` for the outline)
    as an oval section `squash` times as high as wide, centred on z; the spans smoothed `smooth` times
    (no pixel steps in the outline)."""
    rows_ = [(y, (x0 + x1) / 2, max(0.3, (x1 - x0) / 2 - inset)) for y, x0, x1 in sorted(spans(f))
             if rows is None or rows[0] <= y <= rows[1]]
    for _ in range(smooth):
        rows_ = [(y, (rows_[max(0, i - 1)][1] + 2 * cx + rows_[min(len(rows_) - 1, i + 1)][1]) / 4,
                  (rows_[max(0, i - 1)][2] + 2 * hw + rows_[min(len(rows_) - 1, i + 1)][2]) / 4)
                 for i, (y, cx, hw) in enumerate(rows_)]
    rings = []
    for y, cx, hw in rows_:
        rings.append(k.ring(y, hw, hw * squash, segments, z=z, x=cx, power=power, crest=crest * hw / 6))
    first, last = rings[0], rings[-1]
    start = sum(first, Vector()) / len(first) - Vector((0, 0.5, 0))
    end = sum(last, Vector()) / len(last) + Vector((0, 0.5, 0))
    body = k.loft(name, rings, mat, start_point=start, end_point=end)
    return k.smooth(body, 50)


def bronze_painter(prefix):
    return Painter(prefix, shades={1: (1, 2, 3, 4, 5, 6, 7, 8, 9, 0xa, 0xb, 0xc, 0xd, 0xe, 0xf)}, metallic=0.75,
                   roughness=0.3, remap={0x01: 0x11, 0x00: 0x11})


# --- H 17 / 55: the worm's head ------------------------------------------------------------------------

HEAD = kit.frame("BRONZE_HEAD", 24, (12, 28))


def worm_head():
    paint = bronze_painter("worm")
    pf = kit.frame("BRONZE_HEAD", 24, (12, 28)).fill(OUTLINE)
    body = lathe_spans("worm_head", HEAD, paint(0x16), squash=0.66, power=1.7, crest=0.6)
    kit.paint_sprite(body, pf, paint, wall_steps=-2, blur=1, probe=-0.6, default=paint(0x15), shade_shift=0.3)
    # The ridge down its middle catches the light.
    ridge = pal("worm_ridge", 0x1c, metallic=0.75, roughness=0.22)
    pts = []
    for y, x0, x1 in sorted(spans(HEAD)):
        if y > -24:
            hw = (x1 - x0) / 2 - 0.35
            pts.append((0.5, y, hw * 0.66 + 0.6 * hw / 6 - 0.15))
    dense = w.catmull(pts[::3] + [pts[-1]], 0.6)
    kit.loft_path("worm_head_ridge", dense, [0.35] * len(dense), ridge, segments=8)


kit.pieced("gyges_worm_head", worm_head, (24, 56), kit.grid_pieces("gyges_worm_head_", HEAD, ["tip", "base"], 1, 2))


# --- H 131: the worm's tail -----------------------------------------------------------------------------

TAIL = kit.frame("BRONZE_TAIL", 24, (12, 14))


@kit.model("gyges_worm_tail", mask=lambda: TAIL.mask())
def worm_tail():
    paint = bronze_painter("tail")
    pf = kit.frame("BRONZE_TAIL", 24, (12, 14)).fill(OUTLINE)
    body = lathe_spans("tail_body", TAIL, paint(0x16), squash=0.6, power=1.8, crest=0.5, inset=0.5, z=6.0, smooth=2)
    kit.paint_sprite(body, pf, paint, wall_steps=-2, blur=1, probe=-0.6, default=paint(0x15), shade_shift=0.3)
    # The small dome at its front and the hooks at its shoulders.
    dome = pal("tail_dome", 0x1b, metallic=0.8, roughness=0.2)
    w.sphere("tail_dome", (0.5, 11.2, 8.4), (3.4, 2.4, 2.4), dome, 20, 10)
    hook = pal("tail_hook", 0x17, metallic=0.75, roughness=0.3)
    for side in (-1, 1):
        x = 0.5 + side * 8.6
        kit.cone(f"tail_hook{side}", (x, 6.0, 7.0), (x + side * 1.6, 9.2, 8.6), 1.1, hook, segments=8)


# --- H 89, 127, 91: the green balls ----------------------------------------------------------------------

def orb(name, art_name, centre, radii):
    f = kit.frame(art_name, 24, (12, 14))

    @kit.model(name, mask=lambda: f.mask())
    def build():
        paint = Painter(name, shades={0xc: (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0xa, 0xb, 0xc, 0xd, 0xe, 0xf)},
                        metallic=0.15, roughness=0.12, glow={0xcc: 0.2, 0xcd: 0.35, 0xce: 0.5, 0xcf: 0.6},
                        remap={0x01: 0xc0, 0x20: 0xc0, 0x21: 0xc1, 0x22: 0xc2, 0x2e: 0xcd, 0x2f: 0xce})
        pf = kit.frame(art_name, 24, (12, 14)).fill({0x01, 0x20, 0x21, 0x22})
        rx, ry, rz = radii
        ball = w.sphere(name + "_ball", (centre[0], centre[1], rz), radii, paint(0xc6), 48, 24)
        kit.paint_sprite(ball, pf, paint, wall_steps=-1, blur=1, probe=-0.8, default=paint(0xc4), shade_shift=0.4)
    return build


orb("gyges_orb_s", "BALL_S", (0.5, 1.0), (7.0, 6.6, 5.8))
orb("gyges_orb_m", "BALL_M", (0.0, 0.5), (8.6, 8.1, 7.0))
orb("gyges_orb_l", "BALL_L", (0.5, 0.5), (10.1, 9.2, 8.2))


# --- H 77 / 115: the green spike -----------------------------------------------------------------------

SPIKE = kit.frame("GREEN_SPIKE", 24, (12, 28))


def spike():
    paint = Painter("spike", shades={2: (1, 2, 3, 4, 5, 6, 7, 8, 9, 0xa, 0xb, 0xc, 0xd),
                                     0xc: (1, 2, 3, 4, 5, 6, 7, 9, 0xb)},
                    metallic=0.3, roughness=0.25, remap={0x01: 0x21, 0x00: 0x21})
    pf = kit.frame("GREEN_SPIKE", 24, (12, 28)).fill(OUTLINE)
    body = lathe_spans("spike_body", SPIKE, paint(0x25), squash=0.8, power=1.6, crest=0.4, smooth=2)
    kit.paint_sprite(body, pf, paint, wall_steps=-2, blur=1, probe=-0.6, default=paint(0x24), shade_shift=0.3)
    # The point's pale ridge.
    ridge = pal("spike_ridge", 0x2b, metallic=0.3, roughness=0.2)
    pts = []
    for y, x0, x1 in sorted(spans(SPIKE)):
        if -24 < y < -1:
            hw = (x1 - x0) / 2 - 0.35
            pts.append((0.5, y, hw * 0.8 + 0.4 * hw / 6 - 0.2))
    dense = w.catmull(pts[::2] + [pts[-1]], 0.6)
    kit.loft_path("spike_ridge", dense, [0.4] * len(dense), ridge, segments=8)


kit.pieced("gyges_spike", spike, (24, 56), kit.grid_pieces("gyges_spike_", SPIKE, ["top", "tip"], 1, 2))


# --- H 39: the bone ring with its eye -------------------------------------------------------------------

RING = kit.frame("RING", 24, (12, 14))
RING_LIT = kit.frame("RING_3", 24, (12, 14))


@kit.model("gyges_bone_eye", mask=lambda: RING.mask())
def bone_eye():
    f = RING_LIT
    kit.tube_wall("eye_wall", f, (-12.0, 12.0, -14.0, 14.0), height=2.4, relief=2.0, prefix="eye_wall", step=0.75)
    # The ring of bone: a thick knobbly hoop round the pit, its knobs where the sprite's bone is light.
    bone = Painter("bone", shades={0xa: (2, 3, 5, 7, 9, 0xb, 0xd, 0xe), 1: (3, 5, 7, 9, 0xb, 0xd)}, metallic=0.05,
                   roughness=0.55, remap={0x01: 0xa2, 0x00: 0xa2})
    light = w.sampler(f.g, (f.ox, f.oy), value=kit.luminance, blur=1,
                      keep=lambda v: v is not None and v >> 4 in (0xa, 1))
    cx, cy, major = 0.4, 1.0, 6.4
    section = [(major + 2.4 * math.cos(a), 2.3 * math.sin(a)) for a in [2 * math.pi * i / 14 for i in range(14)]]
    ring = kit.hoop("eye_bone", (cx, cy, 2.6), section, bone(0xa9), segments=56, scale_y=1.05)
    for vt in ring.data.vertices:
        d = Vector((vt.co.x - cx, vt.co.y - cy, 0.0))
        bump = max(-0.6, min(1.0, (light(vt.co.x, vt.co.y) - 0.42) * 4.0))
        vt.co.z += bump * max(0.0, (vt.co.z - 2.0) / 2.5)
        if d.length > 1e-3:
            vt.co += d.normalized() * 0.4 * bump * max(0.0, (d.length - major) / 2.4)
    k.smooth(ring, 50)
    kit.paint_sprite(ring, f, bone, wall_steps=-2, blur=1, probe=-0.5, default=bone(0xa7),
                     ramp_of=lambda v: 0xa, shade_shift=-0.5)
    # The pit and the eye in it: a dark hollow, a green glowing ball with a bright pupil.
    pit = pal("eye_pit", 0x01, metallic=0.1, roughness=0.6)
    w.sphere("eye_pit", (0.5, 0.5, 2.2), (4.6, 4.4, 0.8), pit, 28, 8)
    green = pal("eye_green", 0xc5, metallic=0.1, roughness=0.15, glow=1.0)
    hot = pal("eye_green_hot", 0xcc, metallic=0.0, roughness=0.15, glow=1.8)
    w.sphere("eye_ball", (0.5, 0.5, 2.4), (3.4, 3.2, 2.2), green, 28, 12)
    w.sphere("eye_pupil", (0.9, 1.0, 4.3), (1.2, 1.0, 0.5), hot, 16, 6)


if __name__ == "__main__":
    kit.run()
