"""Three grey asteroids of the asteroid levels (sheet D sprites 43, 85 and 123, 2x2: 24 x 28 pixels; sky layer, D 43 the
ground layer too; ASTEROID1, ASTEROID2, ASTEROID?, ASTCITY and AST. CITY, enemies 260-262 (D 43), 263-265 (D 85) and
266-268 (D 123) of episodes 1-3, mostly sent by the levels' random enemies; one frame each, not animated), polished
(2026-10-21; they replace wave3_j_rocks.py's sky_rock() rocks rock_a, rock_b and rock_c, noisy faceted hulls over the
sprites' outlines). models.cfg: model rock_a / rock_b / rock_c enemies/rock_?.glb and sprite d 43 rock_a yaw=0, sprite
d 85 rock_b yaw=0, sprite d 123 rock_c yaw=0 (the lines as they are).

They are the lumpy asteroid's family (D 5, polish_asteroid_lumpy.py: grey ramp 0, a near-black outline, lit from the
upper left, broken into lumps by dark creases), built the same way with its machinery and constants (polish_asteroids:
each lump a convex block over its part of the outline, its walls rising steeply from the ground, roof planes leaning
towards the light where the sprite lights it, a rounded cap of large facets on the knobs, a few chips; the creases cut
in as V-shaped grooves (0x04), the hairlines finer (0x06), carved rings and knobs laid on as low welts; the faces the
camera sees retriangulated evenly and weathered by smooth noise; matte stone, roughness 0.58). None is another sprite's
pixels mirrored, turned or in other ramps (twins3.py), but D 123 is D 229's rock (rock_blue_eye, frames 231-235: 0.94):
ROCK_C below is its spec, for building that one from this (its blue light where ROCK_C's knob is), as D 93 (rock_beacon)
is polish_asteroid_lumpy's ROCK with a lamp.

As the sprites and their 4x upscales draw them (columns and rows of the 24 x 28 sprite):
- rock_a (D 43; columns 0-20 of rows 1-23): a clenched fist of five lumps: along its top a long lump lying from the
  top down to the right (rows 1-11), its upper left face brightly lit (columns 9-14 of rows 6-9); under it, parted
  from it by a crease from the left edge (row 8) to a notch in the right edge (row 11), the left lobe (columns 0-8 of
  rows 8-16), a bright knuckle in the middle (columns 8-13 of rows 11-16), a darker block at the right (columns 13-20
  of rows 11-18) and the bottom lobe (rows 16-23).
- rock_b (D 85; columns 0-23 of rows 1-25): a crown at the top carved with a ring round a knob (columns 8-16 of rows
  3-11), the left lobe under it, a block at the right carved with a smaller ring round a boss (columns 17-23 of rows
  12-19), the bottom left lobe and the dark lower right foot (rows 19-25), parted by creases from below the crown: to the
  left edge, down to the bottom and to the right.
- rock_c (D 123; columns 1-23 of rows 2-24): a broad flat block at the upper left (columns 2-12 of rows 5-14), the top
  right block standing higher (columns 12-23 of rows 2-12, streaked by hairlines), an egg of a knob in the middle (the
  brightest, columns 12-16 of rows 10-15: where rock_blue_eye has its light), the lower left block (rows 14-24) and the
  darker lower right one (columns 14-23 of rows 13-23).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; origin at the
sprite's centre (pixel 12, 14). The specs give pixel corners (column, row) of the 24 x 28 sprite (polish_asteroid_lumpy
.P() moves them into polish_asteroids' picture). Flat underneath (the camera never sees their bellies), 9-10.5 pixels
high; the game centres them in height on their layer (and lifts D 43 on the ground layer clear of the terrain).

Replaces wave3_j_rocks.py's rock_a(), rock_b() and rock_c() (their three @model registrations and their docstring
bullet "rock_a, rock_b, rock_c (D 43, 85, 123)"; sky_rock() stays: rock_beacon() and rock_blue_eye() use it) and
wave3_j_art.py's D43, D85 and D123 (read only by those three).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each rock's silhouette against
enemy_D.png), --preview <prefix> (top and 3/4 views), --only <name,...>.
"""
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
import polish_asteroids as pa  # noqa: E402
import polish_asteroid_lumpy as lumpy  # noqa: E402
from polish_asteroid_lumpy import P, crack  # noqa: E402


class RockBlock(pa.Block):
    """polish_asteroids.Block whose random chips are cut against the block's tops only: Block.chipped() finds a
    point's height under every plane leaning up, and a cap's near-upright facets (normals' z near 0) sent it to -100
    where a chip lay outside the cap, which cut the whole block away."""

    def chipped(self, poly, planes):
        return super().chipped(poly, [(n, d) for n, d in planes if n.z > 0.3])

    def planes(self, cracks, outer, inner):
        """Block.planes(), the cap's ellipse first widened (its proportions kept) to cover the whole footprint: its
        upright facets would cut away what lies outside it."""
        if self.cap is not None:
            c, r, rx, ry, rz, z0, count = self.cap
            centre = pa.px(c, r)
            reach = max(((p[0] - centre.x) / rx) ** 2 + ((p[1] - centre.y) / ry) ** 2
                        for p in self.footprint(cracks)) ** 0.5
            if reach > 0.9:
                self.cap = (c, r, rx * reach / 0.9, ry * reach / 0.9, rz, z0, count)
        return super().planes(cracks, outer, inner)


def block(name, rim, cracks, roofs, shade, cap=None, chips=3, seed=0):
    """polish_asteroid_lumpy.block() (pixel corners of the 24 x 28 sprite), as a RockBlock."""
    return RockBlock(name, lumpy.corners(rim), list(cracks), [(*P(c, r), z, nx, ny) for c, r, z, nx, ny in roofs],
                     shade, random_chips=chips, seed=seed, cap=None if cap is None else (*P(cap[0], cap[1]), *cap[2:]))


def ring(c, r, radius, start=200.0, sweep=320.0, steps=14, squash=1.0):
    """Pixel corners round a carved ring (from the angle start, degrees, counter-clockwise on the screen)."""
    import math
    pts = []
    for i in range(steps + 1):
        a = math.radians(start + sweep * i / steps)
        pts.append((c + radius * math.cos(a), r - radius * math.sin(a) * squash))
    return pts


# --- D 43: the fist -------------------------------------------------------------------------------------------------
A_J1, A_J2, A_J3, A_J4 = (10.0, 10.0), (7.2, 16.2), (13.4, 16.2), (13.6, 11.4)
ROCK_A = {
    "prefix": "rock_a", "sprite": 43, "outer": lumpy.OUTER, "inner": lumpy.INNER,
    "crack_shade": 0x04, "hairline_shade": 0x06,
    "cracks": {
        "a1": crack([(2.8, 7.7), (6.0, 8.1), (8.4, 8.8), A_J1], 1.0, 1.9, ("out", "in")),
        "a2": crack([A_J1, (12.0, 11.0), A_J4], 0.95, 1.8),
        "a3": crack([A_J4, (15.6, 11.9), (17.0, 11.7), (18.6, 11.0)], 0.9, 1.7, ("in", "out")),
        "lm": crack([A_J1, (8.8, 12.2), (7.6, 14.0), A_J2], 0.85, 1.5),
        "lb": crack([(0.8, 16.6), (4.0, 16.9), A_J2], 0.85, 1.5, ("out", "in")),
        "mb": crack([A_J2, (10.2, 17.0), A_J3], 0.8, 1.4),
        "mr": crack([A_J4, (13.9, 13.8), A_J3], 0.8, 1.4),
        "rb": crack([A_J3, (16.4, 17.5), (18.6, 18.3), (20.6, 18.4)], 0.85, 1.5, ("in", "out")),
    },
    "hairlines": [
        crack([(15.0, 19.4), (16.2, 20.8), (16.6, 22.4)], 0.38, 0.45),
        crack([(15.8, 4.4), (17.2, 6.2)], 0.36, 0.42),
    ],
    "blocks": [
        block("top", [(2.8, 7.7), (2.5, 7.5), (4.0, 6.6), (6.0, 5.6), (7.5, 4.6), (8.5, 3.6), (9.5, 2.6), (10.5, 1.6),
                      (11.0, 1.0), (16.0, 1.0), (17.5, 2.0), (19.0, 3.2), (20.0, 4.5), (20.0, 8.5), (18.6, 9.6),
                      (18.6, 11.0)], ["a1", "a2", "a3"],
              [(12.4, 6.0, 9.4, -0.32, 0.3), (17.6, 6.8, 8.6, 0.42, 0.12), (9.4, 8.6, 8.6, -0.15, -0.3),
               (14.0, 9.8, 8.8, 0.05, -0.4), (6.0, 7.4, 7.8, -0.5, 0.2), (15.0, 2.6, 8.2, 0.05, 0.55)], 0x0a,
              seed=3),
        block("left", [(0.8, 16.6), (0.0, 15.5), (0.0, 9.5), (1.0, 8.4), (2.8, 7.7)], ["a1", "lm", "lb"],
              [(4.4, 11.6, 8.6, -0.48, 0.1), (6.2, 14.4, 8.0, -0.1, -0.35)], 0x09,
              cap=(4.4, 12.0, 5.2, 5.2, 10.8, -2.4, 20), seed=5),
        block("mid", [], ["a2", "lm", "mb", "mr"], [(10.8, 13.6, 9.8, -0.12, 0.08)], 0x0b,
              cap=(10.8, 13.8, 4.4, 4.0, 11.6, -1.8, 20), chips=2, seed=7),
        block("right", [(18.6, 11.0), (18.0, 11.6), (19.0, 12.4), (20.0, 13.4), (21.0, 14.4), (21.0, 17.4),
                        (20.6, 18.4)], ["a3", "mr", "rb"],
              [(16.6, 14.6, 8.2, 0.38, 0.0), (19.4, 16.4, 7.2, 0.55, -0.15)], 0x08, seed=11),
        block("bottom", [(20.6, 18.4), (19.0, 19.5), (19.0, 20.6), (18.0, 21.4), (18.0, 22.6), (17.0, 23.5),
                         (16.0, 24.0), (11.0, 24.0), (9.5, 23.2), (8.0, 22.4), (7.0, 21.4), (6.0, 20.4), (5.0, 19.4),
                         (4.0, 18.4), (2.5, 17.5), (0.8, 16.6)], ["lb", "mb", "rb"],
              [(11.0, 19.0, 8.6, -0.08, 0.2), (15.2, 18.8, 8.2, 0.3, 0.05), (10.4, 21.8, 7.2, 0.0, -0.5)], 0x08,
              cap=(11.6, 19.4, 7.4, 4.8, 10.6, -2.4, 22), seed=13),
    ],
    "bowls": [],
    "ridges": [],
    "knobs": [],
}

# --- D 85: the carved one -------------------------------------------------------------------------------------------
B_J1, B_J2 = (11.2, 11.8), (13.6, 19.2)
ROCK_B = {
    "prefix": "rock_b", "sprite": 85, "outer": lumpy.OUTER, "inner": lumpy.INNER,
    "crack_shade": 0x04, "hairline_shade": 0x06,
    "cracks": {
        "cl": crack([(0.2, 10.2), (3.6, 10.9), (7.6, 11.7), B_J1], 0.95, 1.8, ("out", "in")),
        "cr": crack([B_J1, (14.8, 11.2), (18.0, 10.6), (21.2, 10.8)], 0.95, 1.8, ("in", "out")),
        "lr": crack([B_J1, (9.2, 14.2), (6.4, 16.4), (2.8, 18.4)], 0.9, 1.7, ("in", "out")),
        "mid": crack([B_J1, (12.8, 15.2), B_J2], 0.9, 1.7),
        "rr": crack([B_J2, (17.0, 19.8), (20.4, 20.2), (24.2, 20.6)], 0.85, 1.6, ("in", "out")),
        "bb": crack([B_J2, (13.2, 22.4), (12.6, 25.6)], 0.85, 1.6, ("in", "out")),
    },
    "hairlines": [
        crack([(5.6, 19.8), (7.2, 21.6), (8.0, 23.6)], 0.38, 0.45),
        crack([(17.4, 22.0), (19.0, 23.4)], 0.36, 0.42),
    ],
    "blocks": [
        block("crown", [(0.2, 10.2), (0.0, 9.4), (1.2, 8.2), (2.6, 7.2), (4.2, 6.2), (5.4, 5.0), (6.4, 4.0), (7.4, 3.0),
                        (8.4, 2.0), (9.0, 1.0), (16.0, 1.0), (17.5, 2.2), (19.0, 3.6), (20.0, 6.0), (20.0, 9.6),
                        (21.2, 10.8)], ["cl", "cr"],
              [(12.0, 6.6, 9.6, -0.1, 0.08), (7.0, 6.0, 8.6, -0.42, 0.35), (17.0, 6.0, 8.6, 0.42, 0.3),
               (12.0, 10.0, 8.8, 0.0, -0.4), (12.0, 2.6, 8.6, 0.0, 0.55), (3.0, 9.0, 7.4, -0.55, 0.15),
               (19.6, 9.0, 7.6, 0.5, -0.1)], 0x0a, seed=3),
        block("left", [(2.8, 18.4), (2.0, 17.6), (1.0, 16.4), (0.0, 15.4), (0.2, 10.2)], ["cl", "lr"],
              [(4.0, 13.6, 8.6, -0.45, 0.12), (5.6, 16.0, 7.8, -0.1, -0.4)], 0x09,
              cap=(4.2, 13.8, 4.8, 4.6, 10.4, -2.2, 18), seed=5),
        block("right", [(21.2, 10.8), (23.2, 11.4), (24.0, 12.4), (24.0, 20.6)], ["cr", "mid", "rr"],
              [(19.4, 15.6, 9.0, 0.08, 0.05), (22.6, 14.0, 7.8, 0.55, 0.2)], 0x09,
              cap=(19.6, 15.6, 5.8, 5.4, 10.8, -2.0, 22), seed=7),
        block("low", [(12.6, 25.6), (8.0, 25.2), (6.0, 24.6), (4.6, 23.4), (3.0, 22.4), (3.0, 19.0), (2.8, 18.4)],
              ["lr", "mid", "bb"], [(8.6, 19.6, 8.8, -0.28, -0.05), (9.0, 23.2, 7.4, 0.0, -0.5),
                                    (11.0, 15.6, 8.8, 0.1, 0.25)], 0x09,
              cap=(8.6, 18.8, 5.6, 6.2, 10.6, -2.0, 22), seed=11),
        block("foot", [(24.2, 20.6), (24.0, 26.0), (18.0, 26.0), (17.0, 25.2), (12.6, 25.6)], ["rr", "bb"],
              [(18.0, 22.8, 7.6, 0.3, -0.3), (22.0, 23.6, 6.8, 0.5, -0.35)], 0x08, seed=13),
    ],
    "bowls": [(*P(12.2, 7.2), 1.1, 0.4, 0x08)],
    # The ring round the crown's knob and the smaller one round the right block's boss (pixel corners, half width,
    # height, grey); the knob and the boss.
    "ridges": [
        ([P(c, r) for c, r in ring(12.2, 7.2, 3.3, start=230.0, sweep=330.0, steps=16)], 0.85, 0.6, 0x0c),
        ([P(c, r) for c, r in ring(19.8, 15.6, 2.3, start=120.0, sweep=320.0, steps=12)], 0.7, 0.5, 0x0b),
    ],
    "knobs": [(*P(12.2, 4.2), 0.9, 0.7, 0x0b), (*P(19.8, 15.6), 1.0, 0.8, 0x0c), (*P(4.4, 9.8), 0.9, 0.6, 0x0b)],
}

# --- D 123: the blocky one (rock_blue_eye's rock) ---------------------------------------------------------------------
C_J1, C_J2, C_J3, C_J4 = (12.6, 9.4), (11.4, 14.4), (16.6, 13.8), (14.4, 16.4)
ROCK_C = {
    "prefix": "rock_c", "sprite": 123, "outer": lumpy.OUTER, "inner": lumpy.INNER,
    "crack_shade": 0x04, "hairline_shade": 0x06,
    "cracks": {
        "a": crack([(12.2, 4.7), (12.4, 7.0), C_J1], 0.95, 1.8, ("out", "in")),
        "b": crack([C_J1, (15.0, 10.0), C_J3], 0.85, 1.5),
        "c": crack([C_J1, (11.6, 11.8), C_J2], 0.85, 1.5),
        "d": crack([(2.2, 14.2), (6.0, 14.7), (9.0, 14.5), C_J2], 0.95, 1.8, ("out", "in")),
        "e": crack([C_J2, (12.8, 16.0), C_J4], 0.8, 1.4),
        "f": crack([C_J3, (16.2, 15.6), C_J4], 0.8, 1.4),
        "g": crack([C_J4, (15.0, 19.6), (15.8, 22.4), (16.4, 24.8)], 0.9, 1.7, ("in", "out")),
        "h": crack([C_J3, (19.6, 13.1), (24.2, 12.4)], 0.9, 1.7, ("in", "out")),
    },
    "hairlines": [
        crack([(15.4, 3.8), (17.4, 6.6), (19.6, 9.0)], 0.4, 0.5),
        crack([(19.4, 3.4), (20.8, 5.8)], 0.36, 0.42),
        crack([(5.0, 16.8), (7.6, 19.4)], 0.38, 0.45),
    ],
    "blocks": [
        block("ul", [(2.2, 14.2), (2.0, 8.0), (3.0, 7.0), (4.4, 6.0), (5.0, 5.0), (12.0, 5.0), (12.2, 4.7)],
              ["a", "c", "d"], [(7.0, 9.6, 9.2, -0.22, 0.15), (4.8, 12.4, 8.4, -0.45, -0.05),
                                (9.6, 12.6, 8.8, 0.1, -0.3)], 0x0a, seed=3),
        block("tr", [(12.2, 4.7), (12.4, 4.2), (13.2, 3.2), (14.0, 2.0), (19.0, 2.0), (20.4, 3.0), (22.0, 4.0),
                     (23.2, 5.0), (24.0, 6.0), (24.2, 12.4)], ["a", "b", "h"],
              [(17.6, 7.0, 9.8, 0.0, 0.3), (21.6, 9.0, 8.8, 0.45, 0.05), (15.8, 10.4, 9.0, -0.1, -0.35)], 0x09,
              seed=5),
        block("knob", [], ["b", "c", "e", "f"], [(14.0, 12.6, 10.4, -0.1, 0.05)], 0x0b,
              cap=(14.0, 12.6, 3.2, 3.6, 10.0, 0.4, 18), chips=1, seed=7),
        block("ll", [(16.4, 24.8), (15.0, 25.0), (5.0, 25.0), (3.6, 23.8), (2.2, 22.6), (1.0, 21.4), (1.0, 18.0),
                     (2.0, 17.2), (2.2, 14.2)], ["d", "e", "g"],
              [(7.0, 19.0, 9.2, -0.3, 0.0), (8.6, 23.0, 7.6, 0.0, -0.55), (12.4, 18.6, 8.8, 0.2, 0.1)], 0x09,
              cap=(7.6, 19.4, 7.2, 6.0, 11.4, -2.4, 22), seed=11),
        block("lr", [(24.2, 12.4), (24.0, 18.6), (23.0, 19.4), (22.0, 20.4), (21.0, 21.4), (20.0, 22.4), (18.6, 23.4),
                     (16.4, 24.8)], ["f", "g", "h"],
              [(19.6, 17.4, 8.8, 0.25, -0.08), (22.4, 16.0, 7.8, 0.55, 0.0)], 0x08, seed=13),
    ],
    "bowls": [],
    "ridges": [],
    "knobs": [],
}

ROCKS = [ROCK_A, ROCK_B, ROCK_C]


def build():
    options = k.args()
    only = options["only"].split(",") if "only" in options else None
    for spec in ROCKS:
        name = spec["prefix"]
        if only and name not in only:
            continue
        k.reset()
        rock, _ = lumpy.build_rock(spec)
        parts = [rock]
        if "check" in options:
            sheet = os.path.join(options["check"], "enemy_D.png")
            mk.compare("%s (D %d)" % (name, spec["sprite"]), mk.coverage(parts, 24, 28),
                       k.sprite_mask(sheet, spec["sprite"]))
        bpy.context.scene.view_settings.view_transform = "Standard"   # previews in the game's colours
        mk.report(name, parts, os.path.join(mk.outdir(options), name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, parts, size=(24, 28), scale=16, distance=0.7)


if __name__ == "__main__":
    build()
