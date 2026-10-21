"""Batch AC of wave 3 (sheet 7: CAMANIS and ICESECRET; the globe on its legs: polish_ice_globe.py; the bunker:
polish_ice_bunker.py), the ground object the game draws in pieces, modelled as its sprites look (models.cfg:
yaw=0), built whole and cut into its sprites' pieces, drawn at their own origins (origin) so they meet. The level
events place the pieces as the sheet arranges them (the red dome is placed as two events, the dome 28 rows above its
arm), on the ground layer. The sprites draw the ice plateau round them and their shadows on it: the models leave both
out (the 3D ground shows the ice, the game casts the shadows). The kit is wave3_ac_kit.py, the pixels wave3_ac_art.py.

- ice_drill_dome, ice_drill_arm (7 169 above 207; events 85, 86): CAMANIS' red hood with its arm, 24 x 56: a
  red dome with an orange lamp on its back, open at its front between clawed cheeks over a grey piston; out of
  its red collar the arm runs down the screen, a flange, a red knuckle and the grey head with its point. 169's
  frames would light the lamp (the enemy never fires: it stays dim); 207's frames (205, 203) pull the arm in
  when it launches, the model keeps it out.

usage: Blender -b --factory-startup -P wave3_ac_ice.py -- [--only names] [--preview <prefix>] [--check 1]
       [--whole <prefix>]
"""
import math
import os
import sys


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_ac_kit as a  # noqa: E402
from wave3_ac_kit import pal, sphere  # noqa: E402


# --- 7 169 / 207: the red dome with its arm ---------------------------------------------------------

DRILL = a.frame("DRILL", 24, (12, 28))
DX = -1.0      # the object's axis (between the sprite's columns 10 and 11)
ARM_Z = 4.8    # the arm's axis above the ground


def build_drill():
    red = pal("drill_red", 0x76, metallic=0.35, roughness=0.3)
    red_dark = pal("drill_red_dark", 0x72, metallic=0.3, roughness=0.4)
    cavity = pal("drill_cavity", 0x70, metallic=0.1, roughness=0.7)
    lamp = pal("drill_lamp", 0x77, metallic=0.0, roughness=0.25, glow=1.2)
    grey = pal("drill_grey", 0x09, metallic=0.65, roughness=0.25)
    grey_light = pal("drill_grey_light", 0x0c, metallic=0.65, roughness=0.2)
    grey_dark = pal("drill_grey_dark", 0x05, metallic=0.55, roughness=0.35)

    def red_paint(obj):
        a.paint_faces(obj, lambda c, nrm: red if nrm.z > -0.2 else red_dark)

    def grey_paint(obj):
        a.paint_faces(obj, lambda c, nrm: grey if nrm.z > -0.25 else grey_dark)

    # The dome: a red hood over the arm's piston, open at its front between two cheeks.
    dome = sphere("dome", (DX, 16.6, 0.0), (10.3, 11.4, 10.4), red, 36, 18)
    a.carve(dome, (DX, 3.0, 0.0), (8.6, 20.0, 15.6))
    a.carve(dome, (DX, 16.6, -6.0), (30.0, 30.0, 12.0))
    red_paint(dome)
    # The fingers of the hood's cheeks, curling down over the piston's sides, tapering to blunt points.
    for side in (-1, 1):
        for v, y0, y1 in ((8.0, 13.0, 6.4), (5.6, 12.0, 6.0)):
            x = DX + side * v
            u = ((x - DX) / 10.3) ** 2 + ((y0 - 16.6) / 11.4) ** 2
            z0 = 10.4 * math.sqrt(max(0.0, 1 - u)) - 1.0
            path = a.catmull([(x, y0, z0), (x + side * 0.4, y0 - 3.0, z0 * 0.8), (x + side * 0.5, y1 + 0.8, 2.6),
                              (x + side * 0.3, y1, 1.0)], 0.6)
            radii = [1.35 - 0.8 * i / (len(path) - 1) for i in range(len(path))]
            red_paint(a.tube(f"finger{side}_{v}", path, radii, red, 10))
    # The cavity behind the opening, and the seam along the top.
    a.rounded_box("cavity", (DX, 9.6, 3.8), (8.4, 6.0, 7.6), cavity, bevel=0.4, segments=1)
    seam = []
    for i in range(7):
        yy = 22.5 - 1.5 * i
        seam.append((DX, yy, 10.4 * math.sqrt(max(0.0, 1 - ((yy - 16.6) / 11.4) ** 2)) - 0.1))
    a.tube("seam", seam, 0.4, red_dark, 6)
    # The lamp on its back: an orange panel (its frames light it up; this frame has it dim).
    sphere("lamp", (DX + 0.2, 24.2, 7.3), (4.1, 2.6, 1.3), lamp, 20, 8)

    # The arm, along the axis down the screen: the piston in the dome, the red collar, a rod, the flange, the
    # red knuckle, the grey head with its point.
    piston = a.lathe_axis("piston", [(0.0, 0.01), (0.2, 3.4), (8.6, 3.6), (9.2, 3.0), (9.4, 0.01)], grey,
                          (DX, 14.4, ARM_Z), (0, -1, 0), segments=24)
    grey_paint(piston)
    collar = a.lathe_axis("collar", [(0.0, 0.01), (0.2, 4.6), (1.4, 5.2), (3.6, 4.9), (5.0, 4.2), (5.4, 3.6),
                                     (5.6, 0.01)], red, (DX, 6.2, ARM_Z), (0, -1, 0), segments=24)
    red_paint(collar)
    rod = a.lathe_axis("rod", [(0.0, 0.01), (0.1, 2.0), (2.0, 2.0), (2.1, 0.01)], grey_dark, (DX, 0.9, ARM_Z),
                       (0, -1, 0), segments=16)
    flange = a.lathe_axis("flange", [(0.0, 0.01), (0.2, 3.6), (0.9, 4.6), (3.0, 4.6), (3.8, 3.4), (4.0, 0.01)],
                          grey, (DX, -0.5, ARM_Z), (0, -1, 0), segments=24)
    grey_paint(flange)
    a.lathe_axis("rod2", [(0.0, 0.01), (0.1, 1.6), (3.4, 1.6), (3.5, 0.01)], grey_dark, (DX, -4.2, ARM_Z), (0, -1, 0),
                 segments=14)
    knuckle = sphere("knuckle", (DX, -8.6, ARM_Z), (2.8, 2.0, 2.6), red, 18, 10)
    red_paint(knuckle)
    head = sphere("head", (DX, -15.7, ARM_Z), (6.9, 6.0, 4.8), grey, 32, 16)
    grey_paint(head)
    # The dark band round the head's middle.
    a.lathe_axis("head_band", [(0.0, 6.5), (0.2, 7.05), (0.9, 7.05), (1.1, 6.5)], grey_dark, (DX, -15.0, ARM_Z),
                 (0, -1, 0), segments=28, squash=0.72)
    tip = a.cone("tip", (DX, -19.6, ARM_Z), (0, -1, 0), 5.0, 4.0, grey_light, segments=16)
    a.paint_faces(tip, lambda c, nrm: grey_light if nrm.z > -0.25 else grey_dark)
    a.rounded_box("bracket", (DX + 6.2, -16.0, ARM_Z), (1.6, 7.0, 3.0), grey_dark, bevel=0.5, segments=1)


a.pieced("ice_drill", build_drill, (24, 56),
         [("ice_drill_dome", (-12.0, 12.0, 0.0, 28.0), (0.0, 14.0), lambda: a.object_mask(DRILL, (0, 24, 0, 28))),
          ("ice_drill_arm", (-12.0, 12.0, -28.0, 0.0), (0.0, -14.0), lambda: a.object_mask(DRILL, (0, 24, 28, 56)))])


if __name__ == "__main__":
    a.run()
