"""Batch AG of wave 3 (sheet u, written u in models.cfg: DELI, New Deli, BONUS and HARVEST), modelled as the
sprites look (models.cfg: yaw=0). DELI's two towers and their damaged looks are in wave3_ag_tower.py; the kit is
wave3_ag_kit.py, the pixels wave3_ag_art.py. Objects the levels put together from several sprites (the level
files' enemy events say how) are built whole and cut into their pieces, drawn at their own origins (origin).

- glass_globe_tl, glass_globe_tr, glass_globe_bl, glass_globe_br (u 153, 155 above 191, 193; enemies 243, 244
  at (x, y), (x + 24, y) and 241, 242 under them, all four in the sky or all four on top): the big glass globe
  of DELI, New Deli, BONUS and HARVEST, 48 x 56: green glass round a core of bulging green lobes, three of
  them glowing, curved bands sweeping round its lower half. Its 19 frames fade the green out to grey-blue
  glass and on to a pale shut shell (246 170 / 284 208) and back; the model keeps the green look, its glow
  option follows the frames' colour. Built whole and cut in four (origin), standing on its layer (z = 0).

usage: Blender -b --factory-startup -P wave3_ag.py -- [--only name,name] [--preview <prefix>]
       [--check 1] [--stats 1] [--whole <prefix>]
"""
import os
import sys

from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_ag_kit as kit  # noqa: E402
from wave3_ag_kit import k, w, pal  # noqa: E402


# --- u 153 155 / 191 193: the glass globe ----------------------------------------------------------------

GLOBE = kit.frame("SPHERE", 48, (24, 28))
GLOBE_C = Vector((-0.5, 0.5, 14.0))
GLOBE_R = (22.4, 23.3, 14.0)


def globe_whole():
    f = GLOBE
    cx, cy, cz = GLOBE_C
    rx, ry, rz = GLOBE_R
    green = w.sampler(f.g, (f.ox, f.oy), value=lambda val: 1.0 if val >> 4 == 0xc else 0.0, blur=2)
    green1 = w.sampler(f.g, (f.ox, f.oy), value=lambda val: 1.0 if val >> 4 == 0xc else 0.0, blur=1)
    light = kit.brightness(f, blur=2)
    sharp = kit.brightness(f, blur=1)
    dark = [pal(f"globe_{i:02x}", i, metallic=0.2, roughness=0.3) for i in (0x22, 0x24, 0x26)]
    lobe = [pal(f"globe_{i:02x}", i, metallic=0.1, roughness=0.22) for i in (0xc4, 0xc6, 0xc7)]
    lit = [pal(f"globe_{i:02x}", i, metallic=0.0, roughness=0.2, glow=g) for i, g in ((0xc9, 0.5), (0xcb, 0.9),
                                                                                         (0xce, 1.4))]

    def colour(x, y):
        g, lum = green1(x, y), 0.25 * light(x, y) + 0.75 * sharp(x, y)
        if g < 0.4:
            return dark[0] if lum < 0.09 else dark[1] if lum < 0.15 else dark[2]
        for limit, mat in ((0.2, lobe[0]), (0.26, lobe[1]), (0.36, lobe[2]), (0.45, lit[0]), (0.54, lit[1])):
            if lum < limit:
                return mat
        return lit[2]
    # The core: an oblate ball of lobes, the green ones bulging, the dark creases between them sunk, the
    # brightest parts swelling most. Its underside (never seen) is left out.
    core = kit.ico_ellipsoid("globe_core", tuple(GLOBE_C), (rx - 0.6, ry - 0.6, rz - 0.6), dark[1], 6)
    kit.delete_faces(core, lambda c, nrm: c.z < cz - 0.25 * rz)
    kit.emboss(core, lambda x, y: 1.2 * (green(x, y) - 0.5) + 1.8 * max(0.0, light(x, y) - 0.3)
               - 0.9 * max(0.0, 0.09 - sharp(x, y)) / 0.09, 1.0, centre=GLOBE_C, min_nz=0.1)

    def pick(c, nrm):
        q = Vector((c.x, c.y, 0.0))
        if abs(nrm.z) < 0.5:  # the sides take the colour a little inside the outline, darker
            q -= Vector((nrm.x, nrm.y, 0.0)).normalized() * 1.2
        mat = colour(q.x, q.y)
        if nrm.z < 0.3 and mat in lobe[1:]:
            return lobe[0]
        return mat
    kit.paint_faces(core, pick)
    # The glowing lobes: lenses swelling out of the core where the sprite has its brightest blobs.
    hot = pal("globe_lobe_hot", 0xcf, metallic=0.0, roughness=0.15, glow=1.8)
    warm = pal("globe_lobe", 0xcb, metallic=0.0, roughness=0.18, glow=1.0)
    for name, (x, y), (ax, ay), lift in (("lobe_a", (-7.4, 9.6), (4.2, 3.6), 1.2), ("lobe_b", (-0.6, 15.6), (2.6, 2.4), 1.0),
                                         ("lobe_c", (12.6, -8.6), (2.4, 2.4), 0.9)):
        at, nrm = kit.ellipsoid_point(tuple(GLOBE_C), (rx - 0.6, ry - 0.6, rz - 0.6), x, y)
        kit.lens(f"globe_{name}", at, nrm, (ax, ay, 0.9 + lift), warm, sink=0.3)
        kit.lens(f"globe_{name}_core", at + nrm * 0.25, nrm, (ax * 0.55, ay * 0.55, 1.1 + lift), hot, sink=0.2)
    # The glass round it: clear, glossy, a little green.
    glass = k.material("globe_glass", palette=0x28, metallic=0.1, roughness=0.04, alpha=0.16)
    kit.ico_ellipsoid("globe_glass", tuple(GLOBE_C), (rx, ry, rz), glass, 4, 80)


kit.PROTECT += ["globe_core", "globe_lobe"]
kit.pieced("glass_globe", globe_whole, (48, 56), kit.grid_pieces("glass_globe_", GLOBE, ["tl", "tr", "bl", "br"], 2, 2))


if __name__ == "__main__":
    kit.run()
