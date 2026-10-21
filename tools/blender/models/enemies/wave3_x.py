"""Batch X of wave 3 (sheet C: DELI, New Deli, BONUS and others), modelled as their sprites look (models.cfg:
yaw=0). DELI's tall tower is in wave3_x_tower.py, its long cannons in
polish_deli_cannon.py; the kit is wave3_x_kit.py, the pixels wave3_x_art.py. (The glass hatch, C 1, is built by polish_glass_hatch.py,
the blue helm, C 49, by polish_blue_eye_helm.py, the gun on the mast over the ball by polish_ball_mast.py.)

- slit_bunker (C 39): the grey bunker with a rounded back, a raised spine down its middle with two slits in it
  (the frames 41, 43 light them red; the slits glow), a band across it and four ribs at its front reaching
  down to the floor tiles it stands on.

usage: Blender -b --factory-startup -P wave3_x.py -- [--only name,name] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1]
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_x_kit as x  # noqa: E402
from wave3_x_kit import art, k, w, pal, px, py  # noqa: E402


# --- C 39: the bunker with the slits ---------------------------------------------------------------------

@x.model("slit_bunker", [(39, True)])
def slit_bunker():
    """A grey block with a rounded back and chamfered back corners: a raised spine down its middle (cols 8-16)
    with two slits in it, a pale band across the spine between them, the sides falling away in tiers, and at
    its front four ribs reaching down to the floor tiles round it."""
    g = x.grid(art.BUNKER, 24)
    origin = (12, 14)
    m = {s_: pal(f"sb_grey{s_}", s_, metallic=0.3, roughness=0.45) for s_ in range(2, 13)}
    slit_dark = pal("sb_slit", 0x02, metallic=0.2, roughness=0.6)
    glow = pal("sb_glow", 0x77, metallic=0.0, roughness=0.3, glow=1.6)
    core = pal("sb_core", 0x79, metallic=0.0, roughness=0.3, glow=2.2)

    is_body = lambda v, c, r: v >> 4 == 0 and r <= 24 and 1 <= c <= 22
    shadow = lambda v, c, r: ((c >= 20 and 4 <= r <= 26) or (r >= 24 and c >= 2)) and v & 15 <= 3
    fg = x.floor_grid(g, lambda v, c, r: True, lambda v, c, r: shadow(v, c, r) or is_body(v, c, r), seed=9)
    x.floor_bed("tiles", fg, origin, top=0.35, prefix="sb_floor")

    xc = px(12)           # the spine's middle
    top = 9.4
    slits = [(py(7.0), py(4.0)), (py(13.2), py(11.0))]   # (y0, y1) of each slit, cols 9-14

    def z_of(xx, yy, e):
        z = top
        # The back: rounded over its last 3 pixels.
        if yy > 9.0:
            t = min(1.0, (yy - 9.0) / 4.2)
            z -= 3.2 * (1 - math.sqrt(max(0.0, 1 - t * t)))
        # The front: falling to the floor from row 17.
        if yy < -3.0:
            t = min(1.0, (-3.0 - yy) / 8.2)
            z -= 6.6 * t ** 1.4
        # The sides: falling away beside the spine, in tiers.
        dx = abs(xx - xc)
        if dx > 4.6:
            z -= 1.0 + 0.55 * (dx - 4.6)
        # The slits: sunk into the spine.
        for y0, y1 in slits:
            if abs(xx - xc) < 3.1 and y0 < yy < y1:
                z -= 2.2
        return 0.4 + (z - 0.4) * math.sqrt(e * (2 - e))

    polys = x.pixel_polys(g, is_body, origin, smooth=2, epsilon=0.35)
    body = x.q.heightfield("body", polys, z_of, m[7], spacing=0.45, edge=1.1)
    w.simplify_bottom(body)
    x.decimate(body, 2300)
    k.smooth(body, 35)
    shade = x.shades(g, origin, lambda v: v >> 4 == 0, blur=1)

    def paint(c, n):
        if c.z < 1.0:
            return m[3]
        for y0, y1 in slits:
            if abs(c.x - xc) < 3.0 and y0 + 0.2 < c.y < y1 - 0.2 and c.z < top - 0.6:
                return slit_dark
        s_ = shade(c.x, c.y) + 1.0
        if n.z < 0.45:
            s_ -= 1.5
        if abs(c.x - xc) < 4.6 and n.z > 0.8:
            s_ += 0.8
        return m[int(min(12, max(2, round(s_))))]
    w.paint_faces(body, paint)

    # The glow in the slits: a red bar along each slit's floor, brightest in the middle.
    for i, (y0, y1) in enumerate(slits):
        zz = top - 2.2 + 0.1
        w.rounded_box(f"slit_glow{i}", (xc, (y0 + y1) / 2 - 0.3, zz), (5.8, (y1 - y0) * 0.55, 0.6), glow, bevel=0.25)
        w.sphere(f"slit_core{i}", (xc, (y0 + y1) / 2 - 0.3, zz + 0.3), (2.0, (y1 - y0) * 0.22, 0.25), core, 12, 6)
    # The pale band across the spine between the slits.
    w.rounded_box("band", (xc, py(9.2), top + 0.15), (7.4, 2.4, 0.8), m[9], bevel=0.3)

    # The ribs at the front: four rounded toes from the spine's foot down to the floor.
    for i, col in enumerate((6.3, 10.2, 13.8, 17.6)):
        xx = px(col)
        path = [(xx, py(15.5), z_of(xx, py(15.5), 1.0) - 0.4), (xx, py(19.0), z_of(xx, py(19.0), 1.0) + 0.3),
                (xx, py(22.0), z_of(xx, py(22.0), 1.0) + 0.5), (xx, py(23.6), 0.9)]
        rib = w.tube(f"toe{i}", x.catmull(path, 0.8), 1.15, m[7], 8, squash=0.6)
        w.paint_faces(rib, lambda c, n: m[9] if n.z > 0.75 else m[5] if n.z < 0.2 else None)
    # The tiers on the sides: shallow grooves running down and out from the spine.
    for side in (-1, 1):
        for i, row in enumerate((4.5, 9.5, 14.5)):
            a = (xc + side * 4.9, py(row))
            b = (xc + side * 10.2, py(row + 2.4))
            x.q.groove(f"tier{side}{i}", [a, b], lambda xx, yy: z_of(xx, yy, 1.0), m[3], radius=0.38, sink=0.12,
                       step=1.4)
    x.report()


if __name__ == "__main__":
    x.run()
