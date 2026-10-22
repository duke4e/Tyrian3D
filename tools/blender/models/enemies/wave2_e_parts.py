"""The batch E models that are pieces of larger objects (wave2_e.py): each object is built whole from its
pixel art (wave2_e_art.py) and cut along its sprites' edges into the pieces the game draws, each
moved to its sprite's centre (models.cfg: origin, so that they meet again). The levels place the
pieces as the sheets arrange them (checked in the level files' enemy events).

- NOSE DRIP's nose (sheet 5): the bridge (154) above the tip with its nostrils (191, 193).

Volumes come from the sprites' outlines, inflated (wave1_d_shapes.py). (EYESPY's robot and DREAD-NOT's
anchors are polish_eyespy_boss.py's and polish_dread_parts.py's.)
"""
import math

from mathutils import Matrix

import tyrkit as k
import wave1_d_shapes as sh
import wave2_e_art as art


# --- Helpers ---------------------------------------------------------------------------------------

def smoothmin(a, b, k_=1.0):
    h = max(k_ - abs(a - b), 0.0) / k_
    return min(a, b) - h * h * k_ * 0.25


def smoothmax(a, b, k_=1.0):
    return -smoothmin(-a, -b, k_)


def cut_pieces(build, pieces, name, origin):
    """Builds the whole object and keeps the piece `name` of `pieces` ({name: (left, top)} in the
    art's pixels; 24 x 28 pixels each), moved so that its sprite's centre is the origin."""
    objects = build()
    left, top = pieces[name]
    ox, oy = origin
    x0, x1 = left - ox, left + 24 - ox
    y0, y1 = oy - top - 28, oy - top
    kept = sh.cut_box(objects, x0, x1, y0, y1)
    sh.move(kept, -(x0 + 12), -(y0 + 14))
    for obj in kept:
        k.smooth(obj, 50)
    return kept


# --- NOSE DRIP's nose (sheet 5, sprites 154 above 191 and 193) -------------------------------------------

NOSE_ORIGIN = (24, 28)
NOSE_PIECES = {
    "nose_bridge": (12, 0),      # sprite 154
    "nose_tip_left": (0, 28),    # sprite 191
    "nose_tip_right": (24, 28),  # sprite 193
}


def build_nose():
    """The face's nose rising from the face (z = 0) towards the camera: the bridge narrow at the
    top (rows 2-9) and widening, the round tip (rows 28-42), the wings beside it and the black
    nostrils under them (the art's n), the columella between them reaching down to row 51."""
    rows = sh.art(art.NOSE)
    o = NOSE_ORIGIN
    skin = k.material("nose_skin", palette=24, metallic=0.25, roughness=0.36)
    dark = k.material("nose_nostril", palette=16, metallic=0.0, roughness=0.6)

    def p(c, r):
        return c - o[0], o[1] - r

    def bump(x, y, c, r, rx, ry, h):
        cx, cy = p(c, r)
        q = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
        return h * math.sqrt(max(0.0, 1.0 - q)) if q < 1.0 else -2.0 * (math.sqrt(q) - 1.0)

    # The bridge fills the outline of its rows (2-27) across, rounded; further down it keeps row 27's.
    spans = {}
    for r in range(2, 28):
        cols = [c for c, ch in enumerate(rows[r]) if ch != "."]
        spans[r] = ((cols[0] + cols[-1] + 1) / 2.0 - o[0], (cols[-1] + 1 - cols[0]) / 2.0)
    # Smoothed along the rows (the outline's pixel steps would show as ridges).
    weights = (1, 2, 3, 4, 3, 2, 1)
    smooth_spans = {}
    for r in spans:
        acc, total = [0.0, 0.0], 0.0
        for j, w in enumerate(weights):
            rr = min(max(r + j - 3, 2), 27)
            acc[0] += spans[rr][0] * w
            acc[1] += spans[rr][1] * w
            total += w
        smooth_spans[r] = (acc[0] / total, acc[1] / total)
    spans = smooth_spans

    def span(r):
        r = min(max(r - 0.5, 2.0), 27.0)
        r0 = int(math.floor(r))
        r1 = min(r0 + 1, 27)
        f = r - r0
        return tuple(spans[r0][i] * (1 - f) + spans[r1][i] * f for i in range(2))

    def bridge(x, y):
        r = o[1] - y
        cx, width = span(r)
        width = width + 0.3
        height = 3.4 + 7.2 * sh.smoothstep(0.0, 34.0, r)
        q = ((x - cx) / width) ** 2
        top = 1.0 - sh.smoothstep(-1.0, 3.0, 1.5 - r)
        return height * math.sqrt(max(0.0, 1.0 - q)) * top if q < 1.0 else -2.0 * (math.sqrt(q) - 1.0)

    nostrils = [(15.4, 42.8, 4.0, 2.5, -20.0), (32.9, 43.3, 4.7, 2.9, 25.0)]  # column, row, radii, slant

    def nostril_depth(x, y):
        depth = 0.0
        for c, r, rx, ry, slant in nostrils:
            cx, cy = p(c, r)
            ca, sa = math.cos(math.radians(slant)), math.sin(math.radians(slant))
            u, v = (x - cx) * ca + (y - cy) * sa, -(x - cx) * sa + (y - cy) * ca
            q = (u / rx) ** 2 + (v / ry) ** 2
            depth = max(depth, 1.0 - sh.smoothstep(0.35, 1.2, q))
        return depth

    def height(x, y):
        h = bridge(x, y)
        h = smoothmax(h, bump(x, y, 24.2, 35.5, 8.6, 8.2, 12.8), 2.5)       # the tip
        h = smoothmax(h, bump(x, y, 12.8, 40.0, 7.4, 7.6, 7.6), 2.0)        # the left wing
        h = smoothmax(h, bump(x, y, 36.4, 40.0, 7.4, 7.6, 7.6), 2.0)        # the right wing
        h = smoothmax(h, bump(x, y, 24.4, 45.5, 4.6, 6.5, 6.5), 2.0)        # the columella
        h = max(h, 1.2)
        return h - 2.6 * nostril_depth(x, y)

    outline = sh.outlines(rows, "0123456789abcdefn", o, smooth=2, epsilon=0.45)
    nose = sh.inflate("nose", outline, skin, sh.pillow_profile(1.0, 2.4), bottom=0.0, rim=0.05, spacing=0.4,
                      z_fn=lambda x, y, z: 0.05 + max(0.0, min(1.0, z - 0.05)) * max(0.6, height(x, y)))
    objs = [k.smooth(nose, 60)]
    # The nostrils: black hollows in the pits under the wings.
    for i, (c, r, rx, ry, slant) in enumerate(nostrils):
        cx, cy = p(c, r)
        floor = sh.surface_z(nose, cx, cy, 2.0)
        hole = k.ellipsoid(f"nostril{i}", (0, 0, 0), (rx * 0.98, ry * 0.98, 1.2), dark, 32, 12)
        hole.data.transform(Matrix.Translation((cx, cy, floor + 0.95)) @ Matrix.Rotation(math.radians(slant), 4, "Z"))
        objs.append(k.smooth(hole, 60))
    return objs


# --- Registry -----------------------------------------------------------------------------------------

PIECES = []    # (name, sheet, sprite, builder)
ASSEMBLED = []  # (name, builder, size)

for _name, _sprite in (("nose_bridge", 154), ("nose_tip_left", 191), ("nose_tip_right", 193)):
    PIECES.append((_name, "5", _sprite, lambda name=_name: cut_pieces(build_nose, NOSE_PIECES, name, NOSE_ORIGIN)))
ASSEMBLED.append(("nose", build_nose, (48, 56)))
