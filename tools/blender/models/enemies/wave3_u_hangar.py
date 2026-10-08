"""Batch U of wave 3 (sheet S), the hangar of ASTEROID2, ASTCITY and AST. CITY; modelled as its sprites look
(models.cfg: yaw=0).

- roof_hangar_tl, roof_hangar_tr, roof_hangar_ml, roof_hangar_mr, roof_hangar_bl, roof_hangar_br (S 13, 15
  above 51, 53 above 89, 91): the levels place it as six sprites (enemies 326, 327 at the top and the four of
  event 12, 330, 331 above 328, 329). A grey hangar with a pitched roof, its ridge up the screen and its far
  end pointed like a prow, the numbers 92 and 26 painted on its slopes, its front sloping down to the ground
  with a barred door in it, a pale kerb before it and a ribbed apron, a pipe along its left side, in grey
  rubble. Built whole, 48 x 84, and cut into its six pieces (origin).

usage: Blender -b --factory-startup -P wave3_u_hangar.py -- [--only name,name] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1] [--whole hangar --preview <prefix>]
"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_u_kit as u  # noqa: E402
from wave3_u_kit import art, k, sh, w, pal  # noqa: E402

ORIGIN = (24, 42)   # the art: S 13, 15 above 51, 53 above 89, 91, 48 x 84
XR = -1.0           # the ridge (between columns 22 and 23)
X0, X1 = -18.0, 18.5  # the side walls (columns 6 and 42)
EAVES, RIDGE = 11.0, 17.0
FAR_APEX, FAR_LEFT, FAR_RIGHT = 31.0, 25.0, 25.5      # the far end's outline: the ridge's end and the corners
NEAR_APEX, NEAR_LEFT, NEAR_RIGHT = -9.5, -15.0, -14.0  # the near end (the roof's lower edge)
GROUND = -24.0      # where the sloping front meets the ground (row 66)


def px(col):
    return col + 0.5 - ORIGIN[0]


def py(row):
    return ORIGIN[1] - (row + 0.5)


def side_t(x):
    """0 at the ridge, 1 at the eaves."""
    return min(1.0, abs(x - XR) / ((XR - X0) if x < XR else (X1 - XR)))


def y_near(x):
    t = side_t(x)
    return NEAR_APEX + ((NEAR_LEFT if x < XR else NEAR_RIGHT) - NEAR_APEX) * t


def y_far(x):
    t = side_t(x)
    return FAR_APEX + ((FAR_LEFT if x < XR else FAR_RIGHT) - FAR_APEX) * t


def roof_z(x):
    return RIDGE - (RIDGE - EAVES) * side_t(x)


def building_z(x, y):
    """The hangar's top: the roof, and below its lower edge the front sloping to the ground."""
    if y >= y_near(x):
        return roof_z(x)
    f = (y - GROUND) / (y_near(x) - GROUND)
    return roof_z(x) * max(0.0, f) ** 0.9


@u.whole("hangar", (48, 84))
def hangar_whole():
    g = u.grid(art.HANGAR, 48)
    h, wd = len(g), 48
    parts = []

    # The hangar: a heightfield over its pixels (a pixel wider than its outline), each pixel painted in its
    # sprite's grey (the right slope a shade lighter: the light falls on the left), cut to its outline.
    indices = {}
    mats = [pal("rh_wall", 0x03, metallic=0.3, roughness=0.55)]

    def slot(v, metallic=0.3, roughness=0.5):
        if v not in indices:
            indices[v] = len(mats)
            mats.append(pal(f"rh_grey{v}", v, metallic=metallic, roughness=roughness))
        return indices[v]

    def paint(v, c, r, x, y):
        """The roof in three greys (its slope, the painted numbers, the seams between its panels); the front in a
        dark grey with the barred door (columns 19-27, rows 58-65) and a lip under the roof's edge."""
        v = 0x05 if v is None or v >> 4 != 0 else v
        if y >= y_near(x):
            if x < XR:
                return 0x0d if v >= 0x0c else 0x06 if v <= 0x07 else 0x09
            return 0x0c if v >= 0x0a else 0x06 if v <= 0x05 else 0x08
        if y >= y_near(x) - 1.3:
            return 0x06
        if 19 <= c <= 27 and 58 <= r <= 65:
            return 0x01 if v <= 0x02 else 0x05
        return 0x03

    heights = np.zeros((h, wd))
    mat_index = np.zeros((h, wd), dtype=int)
    keep = np.zeros((h, wd), dtype=bool)
    for r in range(h):
        for c in range(wd):
            x, y = px(c), py(r)
            if not (X0 - 1.0 <= x <= X1 + 1.0 and GROUND - 0.5 <= y <= y_far(x) + 1.2):
                continue
            keep[r, c] = True
            heights[r, c] = building_z(x, y)
            v = g[r][c] if r < len(g) and c < len(g[r]) else None
            mat_index[r, c] = slot(paint(v, c, r, x, y))
    body = u.p.bed("hangar", heights.tolist(), mat_index.tolist(), mats, ORIGIN, z0=0.0, keep=keep.tolist())
    planes = [((X0, 0, 0), (-1, 0, 0)), ((X1, 0, 0), (1, 0, 0)), ((0, GROUND, 0), (0, -1, 0))]
    for (ax, ay), (bx, by) in (((X0, FAR_LEFT), (XR, FAR_APEX)), ((XR, FAR_APEX), (X1, FAR_RIGHT))):
        nx, ny = -(by - ay), (bx - ax)  # the outward normal of the far edges (pointing up the screen)
        if ny < 0:
            nx, ny = -nx, -ny
        planes.append(((ax, ay, 0), (nx, ny, 0)))
    body = sh.cut_planes([body], planes)[0]
    k.smooth(body, 30)
    parts.append(body)

    # The ridge cap and the eaves' edges.
    parts.append(w.tube("ridge", [(XR, y_far(XR) - 0.3, RIDGE + 0.15), (XR, NEAR_APEX + 0.3, RIDGE + 0.15)], 0.7,
                        pal("rh_ridge", 0x0b, metallic=0.4, roughness=0.4), 10))
    eave = pal("rh_eave", 0x05, metallic=0.4, roughness=0.45)
    for x in (X0 + 0.35, X1 - 0.35):
        parts.append(w.tube(f"eave{x}", [(x, y_far(x) - 0.3, EAVES + 0.1), (x, y_near(x) + 0.3, EAVES + 0.1)], 0.45, eave, 8))

    # The kerb before the front (rows 66-69) and the ribbed apron (rows 70-79).
    kerb = pal("rh_kerb", 0x08, metallic=0.1, roughness=0.7)
    kerb_dark = pal("rh_kerb_dark", 0x05, metallic=0.1, roughness=0.7)
    k_obj = w.rounded_box("kerb", ((X0 - 2.0 + X1 + 1.0) / 2, (py(65.6) + py(69.4)) / 2, 0.75),
                          (X1 - X0 + 3.0, py(65.6) - py(69.4), 1.5), kerb, bevel=0.4)
    sh.apply_modifiers(k_obj)
    w.paint_faces(k_obj, lambda c, n: kerb if n.z > 0.7 else kerb_dark)
    parts.append(k_obj)
    apron = pal("rh_apron", 0x02, metallic=0.2, roughness=0.7)
    rib = pal("rh_rib", 0x06, metallic=0.4, roughness=0.5)
    y0, y1 = py(79.5), py(69.5)
    parts.append(w.rounded_box("apron", ((X0 - 3.0 + X1 + 1.5) / 2, (y0 + y1) / 2, 0.35), (X1 - X0 + 4.5, y1 - y0, 0.7),
                               apron, bevel=0.2))
    for i in range(10):
        x = X0 - 1.5 + i * 4.0
        parts.append(w.rounded_box(f"apron_rib{i}", (x, (y0 + y1) / 2, 0.8), (1.3, y1 - y0 - 0.6, 0.9), rib, bevel=0.3))

    # The pipe along its left side (columns 4-5, rows 28-65), on brackets.
    pipe = pal("rh_pipe", 0x0c, metallic=0.6, roughness=0.3)
    bracket = pal("rh_bracket", 0x05, metallic=0.4, roughness=0.5)
    x = px(4.5)
    parts.append(w.tube("pipe", [(x, py(27.6), 1.6), (x, py(65.0), 1.6)], 0.95, pipe, 12))
    for i, y in enumerate((py(31.0), py(43.0), py(55.0))):
        parts.append(w.rounded_box(f"bracket{i}", (x + 0.6, y, 0.8), (2.6, 1.2, 1.6), bracket, bevel=0.3))

    # The rubble at its sides and at the bottom (and under the pipe).
    in_rubble = lambda v, c, r: r >= 28 and (r >= 80 or c <= 5 or c >= 43)  # noqa: E731
    g2 = u.refill(g, lambda v, c, r: in_rubble(v, c, r) and c in (4, 5) and r <= 66,
                  lambda v, c, r: in_rubble(v, c, r) and c <= 3, seed=11)
    parts += u.rubble("rubble", g2, in_rubble, "rh", ORIGIN, rmin=1.6, rmax=2.6, height=0.6, segments=7, rings=4)
    return u.meshes()


PIECES = [("roof_hangar_tl", 13, -12.0, 28.0), ("roof_hangar_tr", 15, 12.0, 28.0),
          ("roof_hangar_ml", 51, -12.0, 0.0), ("roof_hangar_mr", 53, 12.0, 0.0),
          ("roof_hangar_bl", 89, -12.0, -28.0), ("roof_hangar_br", 91, 12.0, -28.0)]


def hangar_piece(cx, cy):
    objects = hangar_whole()
    u.cut(objects, (cx - 12.0, cx + 12.0, cy - 14.0, cy + 14.0), (cx, cy))
    u.budget(4800)


for _name, _sprite, _cx, _cy in PIECES:
    u.model(_name, [(_sprite, True)])(lambda cx=_cx, cy=_cy: hangar_piece(cx, cy))


if __name__ == "__main__":
    u.run()
