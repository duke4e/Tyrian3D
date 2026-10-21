"""Enemies of wave 3, batch AE (sheet ', written x27 in models.cfg): CORAL's red sea worm and blue egg, on the sea
floor (the ground layer), modelled as their sprites look (models.cfg: yaw=0); the rest of the sheet
is in wave3_ae.py, wave3_ae_lemon.py and wave3_ae_boss.py, the kit in wave3_ae_kit.py, the pixels in
wave3_ae_art.py. Each is 24 x 56, drawn from two sprites one above the other, so each is built whole and cut in
two (origin), lying on the floor (z = 0). (The electric eel, ' 3 above 41: polish_coral_eel.py.)

- coral_worm_t, coral_worm_b (' 1 above 39; enemies 1216 at (x, y) and 1217 at (x, y + 28)): a red sea worm,
  a fat tube in ringed segments, a knotted bulb at its head (up the screen), its tail tapering to a point.
- coral_egg_t, coral_egg_b (' 14 above 52; enemies 1224 above 1225): a glossy blue egg half sunk in the floor,
  a pale glow inside it.

usage: Blender -b --factory-startup -P wave3_ae_coral.py -- [--only name,name] [--preview <prefix>]
       [--check 1] [--stats 1] [--whole <prefix>]
"""
import os
import sys


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_ae_kit as kit  # noqa: E402
from wave3_ae_kit import sh, w, Painter  # noqa: E402


def halves(prefix, f):
    """The two 24 x 28 sprites of a 24 x 56 object: top and bottom."""
    return [kit.piece(prefix + "_t", f, 0, 0), kit.piece(prefix + "_b", f, 0, 28)]


# --- ' 1 / 39: the red sea worm --------------------------------------------------------------------------

WORM = kit.frame("WORM", 24, (12, 28))
WORM_Z = 3.4


def worm_whole():
    f = WORM
    red = Painter("worm", shades={4: (4, 5, 6, 7, 8, 9, 0xa, 0xb, 0xc)}, metallic=0.1, roughness=0.35)
    # The radius row by row: the sprite's half-width, rounded between the rings.
    half = {}
    for r, row in enumerate(f.g):
        cols = [c for c, val in enumerate(row) if val is not None]
        if cols:
            half[r] = (max(cols) - min(cols) + 1) / 2
    profile = []
    for r in range(55, 3, -1):  # from the tail (low y) up to the neck under the bulb
        hw = half.get(r, 0.5)
        # Rings are one row narrower: keep the pinch, round the segments' sides.
        profile.append((f.oy - (r + 0.5), hw * 0.98))
    profile.insert(0, (f.oy - 56.0, 0.15))
    body = kit.lathe_axis("worm_body", [(y - profile[0][0], rad) for y, rad in profile], red(0x47),
                          (0.0, profile[0][0], WORM_Z), (0, 1, 0), 28, squash=0.85)
    # The rings: soft bulges between the pinches.
    kit.paint_sprite(body, f, red, wall_steps=-1, default=red(0x46), blur=1, probe=-0.8)
    # The knotted bulb at the head: two lobes side by side over a small one.
    for name, (x, y, rx, ry, rz) in (("worm_knot_l", (-2.3, 26.2, 3.0, 2.4, 3.0)),
                                     ("worm_knot_r", (2.3, 26.2, 3.0, 2.4, 3.0)),
                                     ("worm_knot_m", (0.0, 25.0, 2.6, 2.0, 3.2))):
        lobe = w.sphere(name, (x, y, WORM_Z), (rx, ry, rz), red(0x47), 20, 10)
        kit.paint_sprite(lobe, f, red, wall_steps=-1, default=red(0x46), blur=1, probe=-0.6)
    sh.flat_bottom(kit.meshes(), 0.0)


kit.pieced("coral_worm", worm_whole, (24, 56), halves("coral_worm", WORM))


# --- ' 14 / 52: the blue egg ---------------------------------------------------------------------------

EGG = kit.frame("EGG", 24, (12, 28))


def egg_whole():
    f = EGG
    blue = Painter("cegg", shades={3: (5, 6, 7, 8, 9, 0xa, 0xb, 0xc, 0xd, 0xe), 6: (0xf,)}, metallic=0.2,
                   roughness=0.12, glow={0x6f: 1.2, 0x3e: 0.6, 0x3d: 0.35, 0x3c: 0.15})
    shell = w.sphere("egg_shell", (0.0, 1.0, 0.0), (12.0, 24.0, 10.0), blue(0x38), 32, 20)
    sh.flat_bottom([shell], 0.0)
    kit.pixelate(shell, f)
    kit.paint_sprite(shell, f, blue, wall_steps=-1, default=blue(0x37), probe=-0.6)


kit.PROTECT += ["egg_shell"]
kit.pieced("coral_egg", egg_whole, (24, 56), halves("coral_egg", EGG))


if __name__ == "__main__":
    kit.run()
