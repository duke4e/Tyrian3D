"""Enemies of wave 3, batch N (sheet 3: SURFACE, DESERTRUN and CORE), the machines and ships; modelled
as their sprites look (models.cfg: yaw=0 unless noted). The rock arch is in polish_rock_arch.py, the stepped
pyramid in polish_pyramid.py, CORE's fire in wave3_n_fire.py, SURFACE's horned pod (3 1) in polish_horned_pod.py,
DESERTRUN's hatch bunker (3 18) in polish_hatch_bunker.py, CORE's lava bubble (3 128) in
polish_lava_bubble.py, SURFACE's plank turret (3 12) in polish_plank_turret.py, SURFACE's lamp blocks (3 84/86,
122/124) in polish_lamp_block.py.

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
