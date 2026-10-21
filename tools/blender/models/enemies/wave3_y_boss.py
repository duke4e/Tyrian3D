"""Batch Y of wave 3 (sheet 8: IXMUCANE and SAWBLADES), the objects the game draws in pieces, modelled as
their sprites look (models.cfg: yaw=0), each built whole and cut into its sprites' pieces, drawn at their
own origins (origin) so they meet. The level events place the pieces as the sheet arranges them. The kit is
wave3_y_kit.py, the pixels wave3_y_art.py. (The red pod, 8 153 above 191: polish_ixm_pod.py; the
docked ship, 8 39-81: polish_ixm_dock.py.)

- ixm_spider_l, ixm_spider_r (8 229 beside 231; event 7, both on the top layer): the big tan spider:
  a red heart-shaped body with a red spike at its front and a dark head, two grey fangs under it and four
  tan legs a side, curving out and up the screen at their ends (its frames 233/235, 273/275 move the legs a
  little; the model keeps the first).

usage: Blender -b --factory-startup -P wave3_y_boss.py -- [--only names] [--preview <prefix>] [--check 1]
       [--whole <prefix>]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_y_kit as y  # noqa: E402
from wave3_y_kit import pal, sphere  # noqa: E402


# --- 8 229 beside 231: the big spider ------------------------------------------------------------------

SPIDER = y.frame("SPIDER", 48, (24, 14))


def build_spider():
    ax = -0.5
    tan = pal("spider_tan", 0x17, metallic=0.25, roughness=0.5)
    tan_dark = pal("spider_tan_dark", 0x13, metallic=0.2, roughness=0.55)
    red = pal("spider_red", 0x47, metallic=0.3, roughness=0.35)
    red_light = pal("spider_red_light", 0x4b, metallic=0.3, roughness=0.3)
    red_dark = pal("spider_red_dark", 0x43, metallic=0.25, roughness=0.45)
    dark = pal("spider_head", 0x03, metallic=0.4, roughness=0.4)
    fang = pal("spider_fang", 0x09, metallic=0.6, roughness=0.25)
    fang_dark = pal("spider_fang_dark", 0x05, metallic=0.55, roughness=0.3)

    # The body: two red lobes (a heart), the dark head before them, the red spike at the front.
    for side in (-1, 1):
        lobe = sphere(f"lobe{side}", (ax + side * 1.75, -2.4, 4.4), (2.5, 3.9, 3.2), red, 20, 10)
        y.paint_faces(lobe, lambda c, nrm: red_light if nrm.z > 0.85 else red if nrm.z > 0.2 else red_dark)
    sphere("head", (ax, 3.4, 4.4), (2.6, 2.8, 2.6), dark, 18, 9)
    y.cone("spike", (ax, 5.2, 5.4), (0, 1, 0.1), 6.0, 1.5, red, segments=14)
    for side in (-1, 1):
        # The fang under the body.
        path = [(ax + side * 3.0, -3.0, 3.6), (ax + side * 5.4, -5.6, 3.2), (ax + side * 5.8, -8.8, 2.4),
                (ax + side * 4.6, -11.4, 1.6)]
        pts = y.resample(path, 14)
        secs = [(max(0.3, 1.1 - 0.75 * i / 13), max(0.3, 0.9 - 0.6 * i / 13)) for i in range(14)]
        f = y.loft_path(f"fang{side}", pts, secs, fang, segments=10)
        y.paint_faces(f, lambda c, nrm: fang if nrm.z > 0.3 else fang_dark)
        # The legs.
        legs = [
            ([(3.0, 1.2, 4.8), (6.0, 4.2, 7.0), (8.6, 7.4, 6.6), (10.2, 10.4, 4.4), (10.6, 13.4, 2.0)], 2.5, 0.8),
            ([(3.6, 0.0, 4.8), (8.6, 1.0, 6.8), (12.4, 1.8, 5.8), (13.9, 3.6, 3.6), (14.6, 5.8, 1.8)], 2.4, 0.8),
            ([(4.0, -4.4, 4.4), (10.6, -5.0, 6.2), (16.4, -5.0, 4.8), (18.2, -2.4, 3.0), (18.6, 2.6, 1.4)], 2.2, 0.8),
            ([(5.0, -6.6, 4.0), (10.0, -9.4, 5.4), (16.8, -9.7, 4.6), (21.6, -9.3, 3.0), (22.9, -7.0, 2.0),
              (23.2, -3.8, 1.2)], 2.1, 0.75),
        ]
        for i, (path, w0, w1) in enumerate(legs):
            pts = y.resample([(ax + side * px, py, pz) for px, py, pz in path], 26)
            secs = []
            for j in range(len(pts)):
                t = j / (len(pts) - 1)
                hw = w0 + (w1 - w0) * t ** 2.2
                secs.append((hw, hw * 0.8))
            leg = y.loft_path(f"leg{side}_{i}", pts, secs, tan, segments=10)
            y.paint_faces(leg, lambda c, nrm: tan if nrm.z > -0.1 else tan_dark)


y.pieced("ixm_spider", build_spider, (48, 28),
         [("ixm_spider_l", (-24.0, 0.0, -14.0, 14.0), (-12.0, 0.0), lambda: y.frame_mask(SPIDER, (0, 24, 0, 28))),
          ("ixm_spider_r", (0.0, 24.0, -14.0, 14.0), (12.0, 0.0), lambda: y.frame_mask(SPIDER, (24, 48, 0, 28)))])


if __name__ == "__main__":
    y.run()
