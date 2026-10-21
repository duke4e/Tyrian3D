"""Enemies of wave 3, batch N (sheet 3: SURFACE, DESERTRUN and CORE), the machines and ships; modelled
as their sprites look (models.cfg: yaw=0 unless noted). The rock arch is in polish_rock_arch.py, the stepped
pyramid in polish_pyramid.py, CORE's fire in wave3_n_fire.py, SURFACE's horned pod (3 1) in polish_horned_pod.py,
DESERTRUN's hatch bunker (3 18) in polish_hatch_bunker.py, CORE's lava bubble (3 128) in
polish_lava_bubble.py, SURFACE's plank turret (3 12) in polish_plank_turret.py.

- lamp_block_84, lamp_block_86 (3 84, 86) and lamp_block_122, lamp_block_124 (3 122, 124): SURFACE's
  two stone blocks, each drawn in two pieces side by side (origin), with a square relief on top and
  red lamps in slots at one end (glowing).
- hooded_top, hooded_bottom (3 237 above 275): CORE's hooded figure, a grey stone face in a red hood
  and cloak, in two pieces (origin).

usage: Blender -b --factory-startup -P wave3_n.py -- [--only name,name] [--preview <prefix>]
       [--check 1] [--stats 1] [--whole <prefix>]
"""
import math
import os
import sys

from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_n_kit as n  # noqa: E402
from wave3_n_kit import art, k, sh, w, pal, px, py  # noqa: E402


# --- 3 84/86 and 3 122/124: the lamp blocks ------------------------------------------------------

BLOCK_ORIGIN = (24, 14)


def lamp_block(art_text, lamps, square, ribs, prefix):
    """A stone block (one of SURFACE's two, each drawn from two sprites side by side): its top face a
    little domed, its sides and its wide south face leaning as the sprite draws them, a notch under its
    south edge; on its top a square relief (a raised frame round a raised panel) between two ribs, and
    at one end two red lamps glowing in dark slots. lamps: [(column, first row, last row)], square:
    (c0, c1, r0, r1) of its frame, ribs: [(column, first row, last row)] (pixels of the art)."""
    g = w.grid(art_text, 48)
    stone = pal(f"{prefix}_stone", 0xa8, metallic=0.05, roughness=0.7)
    stone_light = pal(f"{prefix}_stone_light", 0xaa, metallic=0.05, roughness=0.65)
    stone_side = pal(f"{prefix}_stone_side", 0xa5, metallic=0.05, roughness=0.75)
    stone_front = pal(f"{prefix}_stone_front", 0xa4, metallic=0.05, roughness=0.8)
    groove = pal(f"{prefix}_groove", 0xa2, metallic=0.05, roughness=0.85)
    slot = pal(f"{prefix}_slot", 0xa1, metallic=0.1, roughness=0.7)
    lamp = pal(f"{prefix}_lamp", 0x75, metallic=0.0, roughness=0.2, glow=1.2)
    lamp_hot = pal(f"{prefix}_lamp_hot", 0x78, metallic=0.0, roughness=0.2, glow=1.8)
    ox, oy = BLOCK_ORIGIN
    height, front_row, bottom_row = 8.0, 16.5, 23.5
    rows = w.regions(g, lambda v, c, r: "#")
    polys = sh.outlines(rows, "#", BLOCK_ORIGIN, smooth=2, epsilon=0.35, min_area=1.0)

    def front(x, y, z):
        row = oy - y
        if row > front_row:  # the south face leans out down to the foot
            t = (row - front_row) / (bottom_row - front_row)
            z = min(z, height - (height - 0.6) * t ** 1.2)
        return z
    body = sh.inflate("body", polys, stone, sh.pillow_profile(height - 0.3, 2.6, crown=0.5), bottom=0.0, spacing=0.45,
                      rim=0.3, z_fn=front)
    w.simplify_bottom(body)
    k.smooth(body, 35)
    w.paint_faces(body, lambda c, nrm: stone_front if nrm.y < -0.45 and nrm.z < 0.85 else
                  stone_side if abs(nrm.x) > 0.4 and nrm.z < 0.85 else
                  stone_light if nrm.z > 0.97 and c.z > height else None)

    def on_top(x, y, lift=0.0):
        return sh.surface_z(body, x, y, height) + lift
    # The square relief: a groove round a raised frame round a raised panel.
    c0, c1, r0, r1 = square
    x0, x1, y0, y1 = c0 - ox, c1 + 1 - ox, oy - r1 - 1, oy - r0
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    z = on_top(cx, cy)
    w.rounded_box("square_groove", (cx, cy, z - 0.25), (x1 - x0 + 0.6, y1 - y0 + 0.6, 0.6), groove, bevel=0.2)
    for name, (bx, by, sx, sy) in {"n": (cx, y1 - 0.9, x1 - x0, 1.6), "s": (cx, y0 + 0.9, x1 - x0, 1.6),
                                   "w": (x0 + 0.9, cy, 1.6, y1 - y0), "e": (x1 - 0.9, cy, 1.6, y1 - y0)}.items():
        w.rounded_box(f"square_{name}", (bx, by, z + 0.3), (sx, sy, 1.4), stone_light, bevel=0.4)
    w.rounded_box("panel", (cx, cy, z + 0.2), (x1 - x0 - 5.0, y1 - y0 - 5.0, 1.6), stone, bevel=0.5)
    # The ribs.
    for c, ra, rb in ribs:
        x = c + 0.5 - ox
        pts = [(x, oy - r - 0.5, on_top(x, oy - r - 0.5, 0.15)) for r in (ra, (ra + rb) / 2, rb)]
        w.tube(f"rib{c}", pts, 0.55, stone_light, 8, squash=0.8)
    # The lamps in their slots.
    for i, (c, ra, rb) in enumerate(lamps):
        x = c + 1.0 - ox
        ya, yb = oy - ra - 0.2, oy - rb - 0.8
        za, zb = on_top(x, ya), on_top(x, yb)
        w.tube(f"slot{i}", [(x, ya, za - 0.2), (x, yb, zb - 0.2)], 1.25, slot, 12, squash=0.6)
        w.tube(f"lamp{i}", [(x, ya - 0.5, za + 0.25), (x, yb + 0.5, zb + 0.25)], 0.8, lamp, 12)
        w.sphere(f"lamp_hot{i}", (x - 0.2, ya - 1.2, za + 0.8), (0.45, 0.8, 0.3), lamp_hot, 8, 4)


def block_piece(name, art_name, sprite, side):
    """One sprite of a lamp block: side -1 is the left (its sprite centre at x = -12), 1 the right."""
    x0, x1 = (-24.0, 0.0) if side < 0 else (0.0, 24.0)

    def mask():
        c0 = 0 if side < 0 else 24
        return n.art_mask(w.grid(getattr(art, art_name), 48), (c0, c0 + 24, 0, 28))
    return (f"{name}_{sprite}", (x0, x1, -14.0, 14.0), (side * 12.0, 0.0), mask)


n.pieced("lamp_block_a", lambda: lamp_block(art.BLOCK_A, [(8, 10, 16), (12, 6, 15)], (22, 33, 5, 15),
                                            [(18, 4, 15), (35, 5, 15)], "block_a"), (48, 28),
         [block_piece("lamp_block", "BLOCK_A", 84, -1), block_piece("lamp_block", "BLOCK_A", 86, 1)])
n.pieced("lamp_block_b", lambda: lamp_block(art.BLOCK_B, [(35, 6, 15), (39, 9, 16)], (15, 26, 5, 15),
                                            [(13, 4, 15), (29, 5, 15)], "block_b"), (48, 28),
         [block_piece("lamp_block", "BLOCK_B", 122, -1), block_piece("lamp_block", "BLOCK_B", 124, 1)])


# --- 3 237 above 275: the hooded figure ----------------------------------------------------------

HOOD_ORIGIN = (12, 28)


def hooded_whole():
    """CORE's hooded figure lying on the ground as the sprites draw it, 24 x 56: a cloak of red cloth
    over the whole, its folds raised where the sprite's red is light and sunk where it is dark, and
    out of it a smooth grey stone head in the hood and a grey face strip below it, the highest part."""
    g = w.grid(art.HOOD, 24)
    ox, oy = HOOD_ORIGIN
    red_px = lambda v: v is not None and v >> 4 == 7  # noqa: E731
    grey_px = lambda v: v is not None and v >> 4 == 0  # noqa: E731
    any_px = lambda v: v is not None  # noqa: E731
    red_fine = w.sampler(g, HOOD_ORIGIN, value=lambda v: v & 15, blur=1, keep=red_px)
    grey_fine = w.sampler(g, HOOD_ORIGIN, value=lambda v: v & 15, blur=1, keep=grey_px)
    fine = w.sampler(g, HOOD_ORIGIN, value=lambda v: v & 15, blur=1, keep=any_px)
    coarse = w.sampler(g, HOOD_ORIGIN, value=lambda v: v & 15, blur=4, keep=any_px)

    redness = w.sampler(g, HOOD_ORIGIN, value=lambda v: 1.0 if v >> 4 == 7 else 0.0, blur=1, keep=any_px)
    darkness = w.sampler(g, HOOD_ORIGIN, value=lambda v: 1.0 if v >> 4 == 0 and (v & 15) <= 2 else 0.0, blur=1,
                         keep=any_px)

    def ramp_at(x, y):
        return 7 if redness(x, y) >= 0.5 else 0

    def cloak_z(x, y, z):
        return z + 0.5 * (fine(x, y) - coarse(x, y))
    rows = w.regions(g, lambda v, c, r: "#")
    cloak = w.part("cloak", rows, "#", pal("hood_red", 0x74, metallic=0.0, roughness=0.6),
                   sh.pillow_profile(5.0, 3.0, crown=1.2), origin=HOOD_ORIGIN, bottom=0.0, z_fn=cloak_z, spacing=0.4,
                   smooth_angle=50)
    reds = [(s - 1.5 if s > 1 else 0, pal(f"hood_red{s:x}", 0x70 + s, metallic=0.0, roughness=0.55,
                                          glow=0.12 if s >= 7 else None)) for s in range(1, 11)]
    shadow = pal("hood_shadow", 0x01, metallic=0.0, roughness=0.9)
    greys = [(s - 0.5 if s > 0 else 0, pal(f"hood_grey{s:x}", s, metallic=0.1, roughness=0.5)) for s in range(1, 11)]

    def paint(c, nrm):
        if nrm.z < -0.5:
            return reds[0][1]
        if ramp_at(c.x, c.y) == 0:
            shade = grey_fine(c.x, c.y)
            if darkness(c.x, c.y) > 0.55 and c.y < -1.0:  # the black of the cloak's folds
                return shadow
            return greys[n.band_index(shade - (1.5 if nrm.z < 0.4 else 0), greys)][1]
        return reds[n.band_index(red_fine(c.x, c.y) - (1.5 if nrm.z < 0.4 else 0), reds)][1]
    w.paint_faces(cloak, paint)
    # The head in the hood and the face strip: the grey pixels of the upper part, raised on the cloak.
    head_rows = w.regions(g, lambda v, c, r: "h" if v >> 4 == 0 and (v & 15) >= 3 and r <= 29 else ".")

    def head_z(x, y, z):
        return z + 0.35 * (grey_fine(x, y) - 6.0)
    head = w.part("head", head_rows, "h", greys[6][1], sh.round_profile(0.8, max_height=6.0), origin=HOOD_ORIGIN,
                  bottom=0.0, base=4.2, z_fn=head_z, spacing=0.35, smooth_angle=55, min_area=6.0)
    w.paint_faces(head, lambda c, nrm: greys[n.band_index(grey_fine(c.x, c.y) + (1.0 if nrm.z > 0.6 else -1.0),
                                                          greys)][1])


def hooded_piece(name, sprite, top):
    y0, y1 = (0.0, 28.0) if top else (-28.0, 0.0)

    def mask():
        return n.art_mask(w.grid(art.HOOD, 24), (0, 24, 0, 28) if top else (0, 24, 28, 56))
    return (name, (-12.0, 12.0, y0, y1), (0.0, 14.0 if top else -14.0), mask)


n.pieced("hooded", hooded_whole, (24, 56), [hooded_piece("hooded_top", 237, True),
                                           hooded_piece("hooded_bottom", 275, False)])


n.run()
