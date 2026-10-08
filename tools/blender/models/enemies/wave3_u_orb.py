"""Batch U of wave 3 (sheet S), the black orb of the asteroid levels (ASTEROID1, ASTEROID2, ASTEROID?, ASTCITY,
AST. CITY, AST ROCK); modelled as its sprites look (models.cfg: yaw=0).

- claw_orb_tl, claw_orb_tr, claw_orb_bl, claw_orb_br (S 39, 41 above 77, 79): the levels place it as four
  sprites (event 12: enemies 311, 312 above 309, 310). A big glossy black orb standing on the ground, held by
  bronze shoulders at its sides and a studded bronze band across its front, two dark curved claws hanging
  from the band round a small ball below it. The stone floor the sprites draw round it is the map's ground
  (the 3D ground shows it): left out. The frames (43, 47 and their neighbours) heat the
  small ball red and let it cool: the model shows it as a dark ember that glows. Built whole, 48 x 56, and
  cut into its four pieces (origin).

usage: Blender -b --factory-startup -P wave3_u_orb.py -- [--only name,name] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1] [--whole orb --preview <prefix>]
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_u_kit as u  # noqa: E402
from wave3_u_kit import art, k, sh, w, pal  # noqa: E402

ORIGIN = (24, 28)   # the art: S 39, 41 above 77, 79, 48 x 56
AX = -1.8           # the machine's axis (the sprites draw it a little left of their middle)
ORB = (AX, 8.6, 4.6)
ORB_R = (16.4, 15.9, 12.8)


def px(col):
    return col + 0.5 - ORIGIN[0]


def py(row):
    return ORIGIN[1] - (row + 0.5)


@u.whole("orb", (48, 56))
def orb_whole():
    black = pal("co_black", 0x01, metallic=0.35, roughness=0.1)
    glint = pal("co_glint", 0x0e, metallic=0.1, roughness=0.1, glow=0.5)
    pit = pal("co_pit", 0x01, metallic=0.2, roughness=0.6)
    bronze = {s: pal(f"co_bronze{s}", 0x10 | s, metallic=0.65, roughness=0.32) for s in range(2, 10)}
    tan = {s: pal(f"co_tan{s}", 0xa0 | s, metallic=0.55, roughness=0.38) for s in range(1, 8)}
    stud = pal("co_stud", 0x17, metallic=0.7, roughness=0.25)
    ember = pal("co_ember", 0x42, metallic=0.25, roughness=0.12, glow=0.6)
    parts = []

    # (The stone floor round it is the map's: not modelled.)
    # The orb: a glossy black ellipsoid sunk in the ground, a soft glint on its upper left, a dark collar
    # where it meets the ground.
    orb = w.sphere("orb", ORB, ORB_R, black, 48, 24)
    parts.append(orb)
    gx, gy = px(12.0), py(13.0)
    gz = ORB[2] + ORB_R[2] * math.sqrt(max(0.0, 1 - ((gx - ORB[0]) / ORB_R[0]) ** 2 - ((gy - ORB[1]) / ORB_R[1]) ** 2))
    parts.append(w.sphere("glint", (gx, gy, gz - 0.6), (2.3, 2.0, 0.85), glint, 16, 8))
    parts.append(u.torus("orb_socket", (ORB[0], ORB[1], 1.0), ORB_R[0] - 0.6, 1.2, pit, 56, 8, squash=0.6,
                         scale_y=ORB_R[1] / ORB_R[0]))

    # The bronze shoulders at its sides (rows 23-37): plates hugging the orb's flanks.
    for side in (-1, 1):
        cx = AX + side * 17.4
        shoulder = w.sphere(f"shoulder{side}", (cx, py(30.0), 2.2), (4.3, 8.2, 5.4), bronze[6], 24, 12)
        w.paint_faces(shoulder, lambda c, n, s=side: bronze[8] if n.z > 0.75 else bronze[7] if n.z > 0.4 and n.x * s < 0.3
                      else bronze[4] if n.z < 0.1 else bronze[6])
        parts.append(shoulder)
        # A rim along its outer edge.
        parts.append(w.tube(f"shoulder_rim{side}", u.catmull([(cx + side * 2.6, py(23.5), 2.6), (cx + side * 3.7, py(29.5), 3.2),
                                                             (cx + side * 3.0, py(36.0), 2.2)], 0.6), 0.7, bronze[3], 10))

    # The band across its front (rows 35-39), bowing towards the viewer, studs along it.
    band_pts = [(px(9.0), py(34.8), 4.6), (px(15.0), py(36.8), 5.4), (AX, py(37.6), 5.8), (px(29.0), py(36.8), 5.4),
                (px(34.5), py(34.8), 4.6)]
    band = w.tube("band", u.catmull(band_pts, 0.6), 2.3, bronze[5], 16, squash=0.75)
    w.paint_faces(band, lambda c, n: bronze[7] if n.z > 0.7 else bronze[5] if n.z > 0.2 else bronze[3])
    parts.append(band)
    path = u.catmull(band_pts, 0.3)
    for i, t in enumerate((0.3, 0.37, 0.44, 0.51, 0.58, 0.65, 0.72)):
        p0 = path[int(t * (len(path) - 1))]
        parts.append(w.sphere(f"stud{i}", (p0.x, p0.y - 0.3, p0.z + 1.55), (0.75, 0.75, 0.5), stud, 10, 6))

    # The claws: dark curved horns from the band's ends down round the pit.
    for side, pts in ((-1, [(px(12.5), py(29.5), 5.2), (px(8.5), py(32.5), 4.8), (px(5.6), py(37.0), 3.8),
                            (px(5.2), py(41.0), 2.6), (px(6.6), py(44.5), 1.6)]),
                      (1, [(px(31.0), py(29.5), 5.2), (px(35.0), py(32.5), 4.8), (px(37.6), py(37.0), 3.8),
                           (px(37.6), py(41.0), 2.6), (px(36.0), py(43.8), 1.6)])):
        path = u.catmull(pts, 0.5)
        radii = [2.4 * (1 - i / len(path)) ** 0.8 + 0.35 for i in range(len(path))]
        claw = w.tube(f"claw{side}", path, radii, tan[5], 14, squash=0.8)
        w.paint_faces(claw, lambda c, n: tan[7] if n.z > 0.7 else tan[5] if n.z > 0.2 else tan[2])
        parts.append(claw)

    # The small ball below the band: a dark ember, glowing.
    parts.append(w.sphere("ball", (px(22.5), py(45.0), 3.4), (6.6, 6.2, 4.6), ember, 28, 14))
    parts.append(w.sphere("ball_glint", (px(20.6), py(43.0), 7.25), (1.3, 1.1, 0.5), glint, 12, 6))

    sh.flat_bottom(parts, 0.0)
    return u.meshes()


def orb_piece(cx, cy):
    objects = orb_whole()
    u.cut(objects, (cx - 12.0, cx + 12.0, cy - 14.0, cy + 14.0), (cx, cy))
    u.budget(4800)


for _name, _sprite, _cx, _cy in (("claw_orb_tl", 39, -12.0, 14.0), ("claw_orb_tr", 41, 12.0, 14.0),
                                 ("claw_orb_bl", 77, -12.0, -14.0), ("claw_orb_br", 79, 12.0, -14.0)):
    u.model(_name, [(_sprite, True)])(lambda cx=_cx, cy=_cy: orb_piece(cx, cy))


if __name__ == "__main__":
    u.run()
