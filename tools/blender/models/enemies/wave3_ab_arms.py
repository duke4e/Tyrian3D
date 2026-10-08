"""Batch AB of wave 3 (sheet 4): the two long arms of TYRIAN and TYRIAN X, which the level events sweep across the
screen before the tusked boss comes (wave3_ab_boss.py), modelled as their sprites look (models.cfg: yaw=0), each
built whole and cut into its seven sprites' pieces, drawn at their own origins (origin) so they meet. The kit is
wave3_ab_kit.py, the pixels wave3_ab_art.py.

- tusk_arm_a_153, _155, _157, _159, _191, _193, _195 (enemies 66-72 side by side, 24 pixels apart, on the top
  layer): 168 x 28 pixels, a thick brown pipe on the left narrowing through a ball joint into a thinner pipe
  with steel clamps, which runs on into a long tusk curving down to its point on the right.
- tusk_arm_b_231, _233, _235, _267, _269, _271, _273 (enemies 73-79): the other arm, its mirror image (the tusk
  on the left). Its piece 269 replaces pipe_arm_2 of wave 2 (wave2_g.py), which was cut from the pipe alone
  and does not meet these pieces.

The arm is one round hull along the middle of the sprite's pixels, as wide as their columns (across the
curve, where the tusk bends down) and 0.8 times as high, sitting on its layer; the clamps are rings a
little proud of it, and everything takes the colour of the pixel under it.

usage: Blender -b --factory-startup -P wave3_ab_arms.py -- [--only names] [--preview <prefix>] [--check 1]
       [--whole <prefix>]
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_ab_kit as ab  # noqa: E402
from wave3_ab_kit import s  # noqa: E402

SQUASH = 0.8


def arm_painter():
    return s.Painter("tarm", shades={0: (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14),
                                     1: (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14),
                                     6: (5, 7, 9, 10, 11, 12, 14),
                                     10: (3, 4, 5, 6, 7, 8, 10)},
                     metallic=0.45, roughness=0.36,
                     finish={0: (0.5, 0.35), 1: (0.4, 0.36), 6: (0.6, 0.3), 10: (0.15, 0.5)})


def columns(fr):
    """For each pixel column: (x of its centre, y of the middle of its pixels, half their height), smoothed
    along the arm (the ends kept); columns without pixels left out."""
    raw = []
    for c in range(fr.width):
        rows = [r for r in range(len(fr.g)) if fr.g[r][c] is not None]
        if rows:
            raw.append((fr.X(c), fr.Y((rows[0] + rows[-1]) / 2.0), (rows[-1] - rows[0] + 1) / 2.0))
    out = []
    for i, (x, _, _) in enumerate(raw):
        reach = min(3, i, len(raw) - 1 - i) if 0 < i < len(raw) - 1 else 0
        near = raw[i - reach:i + reach + 1]
        out.append((x, sum(p[1] for p in near) / len(near), sum(p[2] for p in near) / len(near)))
    return out


def steel_runs(fr, minimum=2):
    """Runs of columns where at least 40% of the pixels are steel (grey, blue-grey or pale): the clamps."""
    runs, start = [], None
    for c in range(fr.width + 1):
        rows = [fr.g[r][c] for r in range(len(fr.g)) if c < fr.width and fr.g[r][c] is not None]
        steel = rows and sum(1 for v in rows if v >> 4 in (0, 6, 10)) >= 0.4 * len(rows)
        if steel and start is None:
            start = c
        if not steel and start is not None:
            if c - start >= minimum:
                runs.append((start, c - 1))
            start = None
    return runs


def build_arm(name):
    fr = ab.frame(name, 168, (84, 14))
    paint_frame = ab.frame(name, 168, (84, 14)).fill({0x10, 0x11, 0x01, 0x02})
    p = arm_painter()
    brown = p(0x16)
    cols = columns(fr)
    # The middle line and the sections across it: the half-height of the columns, narrowed where the arm
    # slopes (the tusk) to its width across the curve.
    path, secs = [], []
    for i, (x, yc, half) in enumerate(cols):
        a, b = cols[max(0, i - 2)], cols[min(len(cols) - 1, i + 2)]
        slope = (b[1] - a[1]) / max(1e-6, b[0] - a[0])
        hw = max(0.3, half * math.cos(math.atan(slope)))
        path.append((x, yc, SQUASH * hw + 0.15))
        secs.append((hw, SQUASH * hw))
    # The thick end is cut square at the sprite's edge; the tusk ends in a point.
    thick_first = cols[0][2] > cols[-1][2]
    if thick_first:
        path[0] = (fr.left(0), path[0][1], path[0][2])
    else:
        path[-1] = (fr.right(fr.width - 1), path[-1][1], path[-1][2])
    hull = ab.loft_path("arm", path, secs, brown, segments=28)
    parts = [hull]
    # The clamps: rings a little proud of the hull.
    for c0, c1 in steel_runs(fr):
        idx = [i for i, (x, _, _) in enumerate(cols) if fr.X(c0) - 0.01 <= x <= fr.X(c1) + 0.01]
        if len(idx) < 2:
            continue
        ring_path = [path[i] for i in idx]
        ring_secs = [(secs[i][0] + 0.35, secs[i][1] + 0.3) for i in idx]
        parts.append(ab.loft_path(f"clamp{c0}", ring_path, ring_secs, p(0x08), segments=28))
    for obj in parts:
        ab.paint(obj, paint_frame, p, wall_steps=1, under=p(0x11), top_blur=1 if obj is hull else 0)


def arm_pieces(prefix, sprites, frame_name):
    fr = ab.frame(frame_name, 168, (84, 14))
    out = []
    for i, sprite in enumerate(sprites):
        x0 = -84.0 + 24.0 * i
        out.append((f"{prefix}_{sprite}", (x0, x0 + 24.0, -14.0, 14.0), (x0 + 12.0, 0.0),
                    (lambda c0=24 * i: ab.frame_mask(fr, (c0, c0 + 24, 0, 28)))))
    return out


ab.pieced("tusk_arm_a", lambda: build_arm("ARM_A"), (168, 28),
          arm_pieces("tusk_arm_a", (153, 155, 157, 159, 191, 193, 195), "ARM_A"))
ab.pieced("tusk_arm_b", lambda: build_arm("ARM_B"), (168, 28),
          arm_pieces("tusk_arm_b", (231, 233, 235, 267, 269, 271, 273), "ARM_B"))


ab.run()
