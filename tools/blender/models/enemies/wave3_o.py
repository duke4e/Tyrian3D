"""Batch O of wave 3 (sheet K, FLEET and LAVA RUN), the fire; modelled as its sprites look
(models.cfg: yaw=0). (The WARNING sign: polish_warning.py.) The grey machines of sheet K are in wave3_o_machines.py.

- fire_tail_l, fire_tail_c, fire_tail_r, fire_mid_l, fire_mid_c, fire_mid_r, fire_head_l, fire_head_c,
  fire_head_r (K 13, 15, 17, 51, 53, 55, 89, 91, 93): the wall of fire that sweeps down FLEET and LAVA
  RUN, 72 pixels wide. The game builds it from a row of three head sprites, rows of the three middle
  sprites every 24 pixels (as many as it likes) and a row of the three tail sprites, all moving down
  together. Built whole as a billowing, glowing column (white-hot along its crest, red at its edges)
  whose middle repeats every 24 pixels, and cut into the nine pieces (origin), each as high as its
  sprite: the middle pieces join each other, the head and the tail without a seam (where the rows
  overlap, the pieces' surfaces coincide).
- spark_dot (K 124), spark_glint (K 125): CAMANIS' two tiny white sparks (1x1): a glowing bead and a
  four-pointed glint.

usage: Blender -b --factory-startup -P wave3_o.py -- [--only name,name] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1] [--whole fire --preview <prefix>]
"""
import math
import os
import sys

from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_o_kit as o  # noqa: E402
from wave3_o_kit import art, k, pal  # noqa: E402


# --- K 13 ... 93: the wall of fire -----------------------------------------------------------------

FIRE_PITCH = 24.0  # the game repeats the middle row every 24 pixels (the sprites are 28 high)
# Each row of the column: (sprites left to right, the row's centre y, the y range it keeps). Every piece
# keeps its sprite's whole height, 28 pixels, 2 more at each end than the 24 the rows are apart: what
# lies there is the middle's repeating pattern, the same as its neighbour's there, so the pieces also
# meet where a level puts rows farther apart (LAVA RUN, where the ground's scroll carries them).
FIRE_ROWS = [
    ("tail", (13, 15, 17), 24.0, (10.0, 38.0)),
    ("mid", (51, 53, 55), 0.0, (-14.0, 14.0)),
    ("head", (89, 91, 93), -24.0, (-38.0, -10.0)),
]
FIRE_COLUMNS = [("l", -24.0, (-36.0, -12.0)), ("c", 0.0, (-12.0, 12.0)), ("r", 24.0, (12.0, 36.0))]


def fire_edges():
    """The column's left and right edges and its shade, as functions of y (and x): the middle rows of
    the sprite (30-53, one 24-pixel period) repeat; the tail's rows (from the top of K 13) and the
    head's (from the bottom of K 89) take over beyond y = +-14, blended in over 5 pixels."""
    g = o.grid(art.FIRE, 72)
    ext = {}
    for r, row in enumerate(g):
        cols = [c for c, v in enumerate(row) if v is not None]
        if cols:
            ext[r] = (min(cols) - 36.0, max(cols) + 1 - 36.0)

    def row_mid(y):
        return 30.0 + ((41.5 - y - 30.0) % FIRE_PITCH)

    def row_tail(y):
        return min(max(37.5 - y, 4.0), 27.0)

    def row_head(y):
        return min(max(45.5 - y, 56.0), 78.0)

    def edge_at(f, side, wrap):
        r0 = int(math.floor(f))
        t = f - r0
        r1 = r0 + 1
        if wrap and r1 > 53:
            r1 = 30
        e0, e1 = ext.get(r0, ext[min(ext, key=lambda r: abs(r - r0))]), ext.get(r1, ext[min(ext, key=lambda r: abs(r - r1))])
        return e0[side] * (1 - t) + e1[side] * t

    weights = ((-1.0, 1), (-0.5, 2), (0.0, 3), (0.5, 2), (1.0, 1))

    def smoothed(fn, y, side):
        return sum(wt * fn(y + d, side) for d, wt in weights) / 9.0

    mid = lambda y, side: edge_at(row_mid(y), side, True)
    tail = lambda y, side: edge_at(row_tail(y), side, False)
    head = lambda y, side: edge_at(row_head(y), side, False)

    def blend(y):
        """(weight of the cap, the cap's function)."""
        if y > 14.0:
            return o.smoothstep(14.0, 19.0, y), tail
        if y < -14.0:
            return o.smoothstep(-14.0, -19.0, y), head
        return 0.0, None

    def edge(y, side):
        m = smoothed(mid, y, side)
        wt, cap = blend(y)
        if wt <= 0.0:
            return m
        return m * (1 - wt) + smoothed(cap, y, side) * wt

    sample = o.shades(g, (36, 0), keep=lambda v: True, blur=1)

    def shade(x, y):
        m = sample(x, -(row_mid(y) + 0.5))
        wt, _ = blend(y)
        if wt <= 0.0:
            return m
        f = row_tail(y) if y > 0 else row_head(y)
        return m * (1 - wt) + sample(x, -(f + 0.5)) * wt

    return edge, shade


@o.whole("fire", (72, 84))
def fire_whole():
    """The column of fire: a loft along y of cross-sections that bulge like a pillow, white-hot crest up,
    over the sprite's outline row by row, with billows (soft bumps) that repeat every 24 pixels, painted
    in the fire ramp from the sprite's shades (the edges dark red, the crest white)."""
    edge, shade = fire_edges()
    puffs = o.PeriodicPuffs(22, -27.0, 27.0, FIRE_PITCH, radius=(2.2, 4.2), amplitude=(0.8, 2.4), stretch=(1.6, 2.6),
                            seed=7)
    swirl = o.PeriodicWaves(7, FIRE_PITCH, kx=(0.2, 0.7), harmonics=(1, 5), seed=3)
    y_top, y_bottom = 34.0, -33.0
    hw_mid = 29.5
    n_top, n_bottom = 60, 12

    def section(y, close=1.0):
        xl, xr = edge(y, 0), edge(y, 1)
        xm, hw = (xl + xr) / 2, (xr - xl) / 2 * close
        height = 11.0 * min(1.1, max(0.15, hw / hw_mid)) ** 0.6
        pts = []
        for i in range(n_top):
            s = -1.0 + 2.0 * i / (n_top - 1)
            u = 0.45 * s + 0.55 * math.sin(s * math.pi / 2)
            x = xm + u * hw
            fall = max(0.0, 1.0 - u * u)
            z = height * fall ** 0.55 + (puffs(x, y) + 0.6 * swirl(x, y)) * fall * close
            pts.append(Vector((x, y, max(z, 0.0))))
        for i in range(1, n_bottom):
            s = 1.0 - 2.0 * i / n_bottom
            x = xm + s * hw
            pts.append(Vector((x, y, -0.4 * height * max(0.0, 1.0 - s * s) ** 0.6)))
        return pts

    rings = []
    count = int(round((y_top - y_bottom) / 0.5))
    # Rounded ends just inside the sprite's first and last rows.
    for t in (0.35, 0.7):
        rings.append(section(y_bottom - 0.6 * (1 - t), close=math.sqrt(1 - (1 - t) ** 2)))
    for i in range(count + 1):
        rings.append(section(y_bottom + 0.5 * i))
    for t in (0.7, 0.35):
        rings.append(section(y_top + 0.6 * (1 - t), close=math.sqrt(1 - (1 - t) ** 2)))
    obj = k.loft("fire", rings, None, start_point=(rings[0][n_top // 2].x, y_bottom - 0.6, 0.0),
                 end_point=(rings[-1][n_top // 2].x, y_top + 0.6, 0.0))
    k.smooth(obj, 70)

    levels = [(0.0, 5), (6.0, 7), (8.0, 8), (9.5, 9), (11.0, 10), (12.2, 11), (13.2, 12), (14.0, 13), (14.6, 14),
              (15.1, 15)]
    bands = [(lowest, pal(f"fire{s}", 0x70 | s, metallic=0.0, roughness=0.45, glow=0.45 + s / 22.0))
             for lowest, s in levels]

    def value(c, n):
        if n.z < -0.2:
            return 0.0
        s = shade(c.x, c.y)
        heart = o.smoothstep(12.0, 15.0, s)
        # The edges flicker in the swirl; in the white heart only the creases between billows cool to
        # yellow; steep flanks show the fire's red skin.
        v = s + 0.9 * swirl(c.x * 1.3, c.y) * (1 - heart)
        v -= heart * 1.4 * max(0.0, 1.0 - puffs(c.x, c.y) / 0.7) ** 2
        v -= 2.2 * max(0.0, 0.45 - n.z)
        return v
    o.paint_bands(obj, value, bands)
    return [obj]


def fire_piece(row, column):
    _, _, cy, (y0, y1) = row
    _, cx, (x0, x1) = column
    objects = fire_whole()
    o.cut(objects, (x0, x1, y0, y1), (cx, cy))


for _row in FIRE_ROWS:
    for _i, _column in enumerate(FIRE_COLUMNS):
        o.model(f"fire_{_row[0]}_{_column[0]}", [(_row[1][_i], True)])(
            lambda row=_row, column=_column: fire_piece(row, column))


# --- K 124, 125: CAMANIS' sparks (1x1) -------------------------------------------------------------

@o.model("spark_dot", [(124, False)], size=(12, 14))
def spark_dot():
    """A white bead, glowing, with a brighter core showing through its top."""
    shell = pal("spark_shell", 0x0b, metallic=0.2, roughness=0.25, glow=0.6)
    core = pal("spark_core", 0x0f, metallic=0.0, roughness=0.2, glow=1.2)
    o.sphere("bead", (0.0, 0.0, 0.0), (2.1, 2.1, 1.9), shell, 20, 10)
    o.sphere("core", (-0.2, 0.2, 0.75), (1.35, 1.35, 1.3), core, 16, 8)


@o.model("spark_glint", [(125, False)], size=(12, 14))
def spark_glint():
    """A four-pointed glint: a glowing white bead with four tapering rays along the axes."""
    ray = pal("glint_ray", 0x0a, metallic=0.2, roughness=0.3, glow=0.6)
    core = pal("glint_core", 0x0f, metallic=0.0, roughness=0.2, glow=1.2)
    cx, cy = 0.5, 0.5
    o.sphere("bead", (cx, cy, 0.0), (1.7, 1.7, 1.5), core, 16, 8)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        o.lathe_axis(f"ray{dx}{dy}", [(0.0, 1.2), (1.2, 0.9), (2.2, 0.45), (2.7, 0.01)], ray, (cx, cy, 0.0),
                     (dx, dy, 0), 10, squash=0.8)


if __name__ == "__main__":
    o.run()
