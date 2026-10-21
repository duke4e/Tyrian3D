"""Batch Q of wave 3 (sheet A: APPROACH, MISTAKES, SOH JIN, GAUNTLET), SOH JIN's sign; modelled as its
sprites look (models.cfg: yaw=0). (The fire gates' housings: polish_fire_gate.py.) The skull chest
is in wave3_q_mace.py; the mace, its chain and anchor and SOH JIN's bronze pieces in polish_*.py.

- missile_sign_left, missile_sign_right (A 49 beside 51): SOH JIN's red "WARNING / MISSILE SHIPS!!"
  sign, glowing red letter strokes, built whole and cut in two (origin).

usage: Blender -b --factory-startup -P wave3_q.py -- [--only name,name] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1] [--whole sign --preview <prefix>]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_q_kit as q  # noqa: E402
from wave3_q_kit import art, sh, pal  # noqa: E402


# --- A 49 / 51: the MISSILE SHIPS sign -------------------------------------------------------------

@q.whole("sign", (48, 28))
def sign_whole():
    """Glowing red strokes, the letters' left sides (shade 6) a darker red, as the sprite draws them."""
    g = q.grid(art.SIGN, 48)
    origin = (24, 14)
    rows = q.regions(g, lambda v, c, r: "R")
    strokes = q.part("letters", rows, "R", None, sh.round_profile(3.0, max_height=1.5, min_height=1.2),
                     origin=origin, base=0.0, bottom=0.35, smooth=0, epsilon=0.12, spacing=0.3, rim=0.1, sigma=0.6)
    q.decimate(strokes, 6000)
    shade = q.shades(g, origin, keep=lambda v: True, blur=0)
    bands = [(0.0, pal("sign_red5", 0x75, metallic=0.1, roughness=0.35, glow=0.5)),
             (6.5, pal("sign_red6", 0x76, metallic=0.1, roughness=0.32, glow=0.65)),
             (7.5, pal("sign_red8", 0x78, metallic=0.1, roughness=0.3, glow=0.85))]
    q.paint_bands(strokes, lambda c, n: shade(c.x, c.y) - (2.0 if n.z < 0.3 else 0.0), bands)
    return [strokes]


def sign_piece(cx, box):
    objects = sign_whole()
    q.cut(objects, (box[0], box[1], -14.0, 14.0), (cx, 0.0))


for _name, _sprite, _cx, _box in (("missile_sign_left", 49, -12.0, (-24.0, 0.0)),
                                  ("missile_sign_right", 51, 12.0, (0.0, 24.0))):
    q.model(_name, [(_sprite, True)])(lambda cx=_cx, box=_box: sign_piece(cx, box))


if __name__ == "__main__":
    q.run()
