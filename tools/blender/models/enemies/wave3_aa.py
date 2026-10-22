"""Enemies of wave 3, batch AA (sheet E), modelled as their sprites look (models.cfg: yaw=0 unless noted). The
boulders in the pit of TYRIAN and HOLES are in wave3_aa_rocks.py, the lava grubs in polish_lava_grub.py;
the kit is wave3_aa_kit.py, the pixels wave3_aa_art.py. Objects the levels put together from several sprites
(the level files' enemy events say how) are built whole and cut into their pieces, drawn at their own
origins (origin). (The big dark orb, E 191 193 above 229 231: polish_dark_orb.py.)

(The tan spiked mine of MINES, ** ALE ** and ASTEROIDS, E 201, is polish_spike_mine.py's chrome mine in the sprite's
colours: models.cfg color=sprite.)
(BUBBLES' boiling bubbles, E 155: polish_bubbles_hot.py.)
- dome_magma (E 203): ASTEROIDS' red glass dome on a grey pedestal, molten swirls inside it (its frames
  brighten them: they glow).
- tan_crater_tl, tan_crater_tr, tan_crater_bl, tan_crater_br (E 51, 53 above 55, 93; events 1138-1141 at
  (x, y), (x + 24, y), (x, y + 28), (x + 24, y + 28)): ASTEROIDS' tan crater, a ring of rock round a dark
  shaft, its far rim thin, its near slope broad, cracked. Built whole and cut in four (origin).
- crater_dome (E 243; event 1143 at (x + 12, y - 6) of the crater's): the blue glass dome on a grey pedestal
  over the crater's far rim (its frames move the reflections); the pedestal stands on the ground behind the
  rim, tall enough to hold the dome over it (origin, with the crater's pieces).

usage: Blender -b --factory-startup -P wave3_aa.py -- [--only name,name] [--preview <prefix>]
       [--check 1] [--stats 1] [--whole <prefix>]
"""
import math
import os
import sys


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_aa_kit as kit  # noqa: E402
from wave3_aa_kit import art, k, w, pal, Frame, Painter  # noqa: E402


# --- E 203 and E 243: the glass domes ---------------------------------------------------------------

RED_DOME = Frame(art.RED_DOME, 24, (12, 14))
BLUE_DOME = Frame(art.BLUE_DOME, 24, (12, 14))
DOME_BASE = ((-0.5, -0.6), (11.5, 10.4))
DOME_GLASS = ((-0.5, 1.4), (10.4, 9.4))


def steel(prefix):
    return (pal(f"{prefix}_steel9", 0x09, metallic=0.55, roughness=0.35),
            pal(f"{prefix}_steel6", 0x06, metallic=0.55, roughness=0.4),
            pal(f"{prefix}_steel3", 0x03, metallic=0.4, roughness=0.5))


@kit.model("dome_magma", mask=lambda: RED_DOME.mask())
def dome_magma():
    painter = Painter("magma", shades={7: (1, 3, 5, 7, 9, 0xb, 0xd, 0xe)}, metallic=0.15, roughness=0.12,
                      glow={0x73: 0.3, 0x75: 0.55, 0x77: 0.8, 0x79: 1.2, 0x7b: 1.6, 0x7d: 2.0, 0x7e: 2.4})
    kit.dome_parts("magma", RED_DOME, painter, steel("magma"), DOME_GLASS[0], DOME_GLASS[1], DOME_BASE[0],
                   DOME_BASE[1], 3.2, 6.6, default=painter(0x75))


# --- E 51 53 / 55 93: the tan crater, and E 243, the blue dome on its rim ----------------------------------

CRATER = Frame(art.CRATER, 48, (24, 28))
HOLE_CENTRE = (-0.5, 7.2)
HOLE_RADII = (8.4, 6.2)
CRATER_CENTRE = (0.0, 0.5)
CRATER_RADII = (23.0, 18.6)
CRATER_HEIGHT = 9.0
# The blue dome's sprite centre in the crater's coordinates (event 1143 at (x + 12, y - 6) of 1138's).
CRATER_DOME_AT = (0.0, 20.0)


def _ellipse_ray(cx, cy, ex, ey, rx, ry, dx, dy):
    """The distance along a ray from (cx, cy) in direction (dx, dy) to the ellipse centred at (ex, ey)."""
    ox, oy = (cx - ex) / rx, (cy - ey) / ry
    ddx, ddy = dx / rx, dy / ry
    a = ddx * ddx + ddy * ddy
    b = 2 * (ox * ddx + oy * ddy)
    c = ox * ox + oy * oy - 1
    return (-b + math.sqrt(max(0.0, b * b - 4 * a * c))) / (2 * a)


def crater_height(u):
    """The crater's height across its ring: u = -1 at the shaft's floor, 0 at its lip, 1 at the outer foot."""
    h = CRATER_HEIGHT
    if u <= -0.35:
        return 0.6
    if u < 0.0:  # the shaft's wall, steep
        t = (u + 0.35) / 0.35
        return 0.6 + (0.78 * h - 0.6) * t ** 1.6
    if u < 0.22:  # the lip rounding over to the crest
        t = u / 0.22
        return h * (0.78 + 0.22 * math.sin(t * math.pi / 2))
    t = (u - 0.22) / 0.78  # the outer slope, a rounded shoulder down to the ground
    return h * math.sqrt(max(0.0, 1.0 - t ** 2.2)) * (1 - 0.12 * t)


def crater_whole():
    f = CRATER
    painter = Painter("crater", shades={1: (1, 2, 3, 5, 6, 7, 8, 9, 0xa, 0xb, 0xc, 0xd)}, metallic=0.05,
                      roughness=0.6)
    hx, hy = HOLE_CENTRE
    segs = 144
    us = [-1.0, -0.6, -0.35, -0.25, -0.15, -0.07, 0.0, 0.05, 0.11, 0.17, 0.22, 0.3, 0.38, 0.46, 0.54, 0.62, 0.7,
          0.77, 0.84, 0.9, 0.95, 1.0]
    verts, faces = [], []
    for u in us:
        for i in range(segs):
            a = 2 * math.pi * i / segs
            dx, dy = math.cos(a), math.sin(a)
            r_hole = _ellipse_ray(hx, hy, hx, hy, *HOLE_RADII, dx, dy)
            r_out = _ellipse_ray(hx, hy, *CRATER_CENTRE, *CRATER_RADII, dx, dy)
            r = r_hole * (1 + u) if u < 0 else r_hole + (r_out - r_hole) * u
            # The far rim, where the blue dome stands, lower than the near one.
            back = 1.0 - 0.3 * max(0.0, dy) ** 1.5 if u > -0.35 else 1.0
            verts.append((hx + dx * r, hy + dy * r, crater_height(u) * back))
    for j in range(len(us) - 1):
        for i in range(segs):
            a, b = j * segs + i, j * segs + (i + 1) % segs
            faces.append((a, b, b + segs, a + segs))
    verts.append((hx, hy, crater_height(-1.0)))
    faces += [((i + 1) % segs, i, len(verts) - 1) for i in range(segs)]
    body = k.mesh_object("crater_body", verts, faces, painter(0x18))
    k.recalc_normals(body)
    k.smooth(body, 50)
    kit.paint_sprite(body, f, painter, wall_steps=-1, default=painter(0x15), blur=1, probe=-0.8)
    # The shaft's floor in the dark.
    w.sphere("crater_floor", (hx, hy, 0.4), (HOLE_RADII[0] * 0.75, HOLE_RADII[1] * 0.75, 0.5),
             pal("crater_dark", 0x11, metallic=0.0, roughness=0.9), 32, 8)


kit.pieced("tan_crater", crater_whole, (48, 56), kit.grid_pieces("tan_crater_", CRATER, ["tl", "tr", "bl", "br"], 2, 2))


@kit.model("crater_dome", mask=lambda: BLUE_DOME.mask())
def crater_dome():
    painter = Painter("bluedome", shades={3: (2, 3, 4, 5, 6, 7, 8, 9, 0xa, 0xb, 0xc, 0xd, 0xe)}, metallic=0.25,
                      roughness=0.08)
    # Its pedestal stands on the ground behind the crater, tall enough to hold the dome over the far rim.
    kit.dome_parts("bluedome", BLUE_DOME, painter, steel("bluedome"), DOME_GLASS[0], DOME_GLASS[1], DOME_BASE[0],
                   DOME_BASE[1], 8.0, 6.6, default=painter(0x36))


if __name__ == "__main__":
    kit.run()
