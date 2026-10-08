"""Enemies of wave 3, batch AN (sheet n, written n in models.cfg): GYGES' pincers and blue bubbles, modelled as their
sprites look (models.cfg: yaw=0). The kit is wave3_an_kit.py, the pixels wave3_an_art.py; GYGES' maw boss is in
wave3_an_boss.py.

GYGES puts the pincers at the screen's sides while the boss comes in: enemy 180 above 181 (n 163 above 201) at
(18, -50) and (18, -22), enemy 182 above 183 (n 11 above 49) at (290, -50) and (290, -22), ground enemies, swaying
from side to side. Their frames (163 203 207, 201 205 245; 11 9 1, 49 47 39) open and close the pincer; the models
show it as most frames do (163, 11): nearly closed.

- gyges_pincer_163, gyges_pincer_201 (n 163 above 201): the left pincer, a crab's claw hanging down the screen: a
  thick armoured hand (its top cut off by the sprite), lit down its left, the big fixed finger curving down from
  its left, the small movable finger on its right, hinged on a glossy blue ball joint; rounded like tubes where
  thin, the fingers sinking towards their tips. Built whole (24 x 56), cut in two (origin); the lower piece keeps
  the fingers' tips.
- gyges_pincer_11, gyges_pincer_49 (n 11 above 49): the right pincer, the left one's mirror image.
- gyges_bubble_l, gyges_bubble_m, gyges_bubble_s (n 13, 15, 125; enemies 176/179, 175/178, 174/177): glossy blue
  bubbles (eggs?) rolling in from the sides, a light swirl inside: a sphere painted by the sprite's pixels, the
  swirl's bright crescent a little raised. Three sizes (the levels spawn the small ones first).

usage: Blender -b --factory-startup -P wave3_an.py -- [--only name,name] [--preview <prefix>] [--check 1]
       [--stats 1] [--whole <prefix>]
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_an_kit as kit  # noqa: E402
from wave3_an_kit import k, pal, Painter, smoothstep  # noqa: E402


# --- The bubbles ---------------------------------------------------------------------------------------------

def bubble(name, art_name):
    f = kit.frame(art_name, 24, (12, 14))
    cells = [(c, r) for r in range(f.height) for c in range(24) if f.get(c, r) is not None]
    cx = sum(c + 0.5 for c, _ in cells) / len(cells) - 12.0
    cy = 14.0 - sum(r + 0.5 for _, r in cells) / len(cells)
    radius = math.sqrt(len(cells) / math.pi)
    paint_f = f.fill({0x01, 0x30})

    @kit.model(name, mask=lambda: f.mask((0, 24, 0, 28)))
    def build():
        p = Painter(name, shades={3: (1, 2, 3, 4, 5, 6, 7, 8, 9, 0xa, 0xb, 0xc, 0xd, 0xe)}, metallic=0.25,
                    roughness=0.14, remap={0x01: 0x31, 0x30: 0x31})
        rz = radius * 0.9
        ball = kit.ico_ellipsoid(name, (cx, cy, rz), (radius, radius, rz), p(0x36), 5)
        kit.delete_faces(ball, lambda c, nrm: nrm.z < -0.3)
        # The swirl's light crescent raised a little, its dark band sunk: a glassy spiral inside the shell.
        field = kit.brightness(paint_f, blur=1)
        mid = sum(field(x - 12 + 0.5, 14 - r - 0.5) for x, r in cells) / len(cells)
        kit.emboss(ball, lambda x, y: (field(x, y) - mid) * 2.2, 0.6, min_nz=0.25)
        k.smooth(ball, 70)

        def pick(c, nrm):
            x, y = c.x, c.y
            if nrm.z < 0.35:   # the flanks: the pixel a little inside the outline
                x, y = cx + (x - cx) * 0.85, cy + (y - cy) * 0.85
            val = paint_f.at(x, y)
            if val is None:
                return p(0x32)
            return p(val) if nrm.z > 0.0 else p(0x31)
        kit.paint_faces(ball, pick)
        return ball
    return build


bubble("gyges_bubble_l", "ORB_13")
bubble("gyges_bubble_m", "ORB_15")
bubble("gyges_bubble_s", "ORB_125")


# --- The pincers -----------------------------------------------------------------------------------------------

CLAW_L = kit.frame("CLAW_L", 24, (12, 28))
CLAW_R = kit.frame("CLAW_R", 24, (12, 28))
MIRROR_X = -0.5          # the right pincer's art is the left one's mirror image about pixel column 11


def claw_painter():
    return Painter("pincer", shades={6: (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0xa, 0xb, 0xc), 0: (1, 2),
                                     3: (0, 4, 5, 0xc), 8: (8,)},
                   metallic=0.5, roughness=0.3, finish={3: (0.2, 0.12), 8: (0.2, 0.12)},
                   remap={0x01: 0x60, 0x02: 0x61})


def claw_height(x, y, z):
    """The fingers sink towards their tips; the hand's top (cut off by the sprite) stays high."""
    r = 28.0 - y
    return z * (1.0 - 0.38 * smoothstep(16.0, 33.5, r)) + 0.8 * (1.0 - smoothstep(14.0, 30.0, r))


def claw(right):
    f = CLAW_R if right else CLAW_L
    paint_f = f.fill({0x01, 0x02})
    p = claw_painter()
    # Built as the left pincer, mirrored for the right one.
    polys = kit.region(CLAW_L, lambda val, c, r: True, smooth=2, min_area=2.0)
    shell = kit.inflated("pincer", polys, p(0x66), 8.4, aspect=0.95, spacing=0.5, z_fn=claw_height)
    joint = kit.w.sphere("pincer_joint", (0.8, 13.4, 6.6), (2.3, 2.1, 1.9), pal("pincer_joint", 0x35, metallic=0.2,
                                                                                    roughness=0.1), 16, 8)
    parts = [shell, joint]
    if right:
        for obj in parts:
            obj.data.transform(kit.Matrix.Translation((MIRROR_X, 0, 0)) @ kit.Matrix.Scale(-1, 4, (1, 0, 0)) @
                               kit.Matrix.Translation((-MIRROR_X, 0, 0)))
            obj.data.flip_normals()
    kit.paint(shell, paint_f, p, walls=-2, probe=-0.4, grid=True)
    blues = [pal("pincer_joint_32", 0x32, metallic=0.2, roughness=0.12),
             pal("pincer_joint_35", 0x35, metallic=0.2, roughness=0.1),
             pal("pincer_joint_3c", 0x3c, metallic=0.1, roughness=0.08, glow=0.4)]
    hl = -1.0 if not right else 1.0
    kit.paint_faces(joint, lambda c, nrm: blues[2] if nrm.z > 0.6 and nrm.x * hl > 0.25 and nrm.y > 0.0 else
                    blues[1] if nrm.z > 0.2 else blues[0])
    for obj in parts:
        k.smooth(obj, 50)


kit.PROTECT += ["pincer"]
kit.pieced("gyges_pincer_left", lambda: claw(False), (24, 56),
           [kit.piece("gyges_pincer_163", CLAW_L, 0, 0), kit.piece("gyges_pincer_201", CLAW_L, 0, 28)])
kit.pieced("gyges_pincer_right", lambda: claw(True), (24, 56),
           [kit.piece("gyges_pincer_11", CLAW_R, 0, 0), kit.piece("gyges_pincer_49", CLAW_R, 0, 28)])


if __name__ == "__main__":
    kit.run()
