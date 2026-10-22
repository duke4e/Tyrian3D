"""Batch AD of wave 3 (sheet H: GYGES, TORM, BONUS), GYGES' small flying things, modelled as the sprites look
(models.cfg: yaw=0). GYGES' creatures in their pieces of tube wall are in polish_gyges_wall.py, its bronze worm's head
and tail in polish_gyges_worm.py, its bone ring with the eye in polish_gyges_bone_eye.py, TORM's beetle in
polish_torm_beetle.py, the waterfall of TORM and BONUS in polish_waterfall.py; the kit is wave3_ad_kit.py, the pixels
wave3_ad_art.py.

- gyges_orb_s, gyges_orb_m, gyges_orb_l (H 89, 127, 91; enemies 417, 418, 419): GYGES' glossy green balls,
  which swing round over the grey stalk (polish_gyges_wall.py) in ever wider circles.
- gyges_spike_top, gyges_spike_tip (H 77 above 115; enemies 420 above 421, one movement): the green spike
  that swings widest of them, a faceted green knob on a ridged neck over a long pale-ridged point down the
  screen (origin; built round z = 0 like the balls).
usage: Blender -b --factory-startup -P wave3_ad.py -- [--only name,name] [--preview <prefix>]
       [--check 1] [--stats 1]
"""
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


if __name__ == "__main__":
    kit.run()
