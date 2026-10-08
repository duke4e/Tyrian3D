"""Batch AI of wave 3 (sheet 0): GRYPHON's boss, a blue gryphon with bat's wings, modelled as its sprites look
(models.cfg: yaw=0) and drawn at their own origins (origin) so that the pieces meet. The kit is wave3_ai_kit.py,
the pixels wave3_ai_art.py.

GRYPHON's events put the boss together at the level's end (t7100) from custom enemies of sheet 0 (bank 29, on the
top layer) and the head, enemy 835:
- gryphon_1 ... gryphon_89: its body and wings, 186 x 84 pixels, twenty 2x2 sprites of link 61, which stay
  still: rows at y = -84, -56, -28 (28 apart), the sprites 24 apart from x = 40 (1 3 . 7 9 . 13 15 / 39 ... 53 /
  . 79 ... 89 .); 15 and 53 are put at x = 202, 6 pixels left of the grid, over 13 and 51 (the right wing is 6
  pixels shorter than the left in the game). Built whole and cut along the sprites' edges (between 13 and 15,
  51 and 53, in the middle of their overlap). A body down the middle with two long horns up the screen, grey
  claws fanned at its shoulders, the wings spread out and up to grey claws at their tips, their fingers ridged;
  under the neck a low saddle where the neck lies.
- gryphon_neck_91, gryphon_neck_93: the neck with its grey claws, 48 x 28, of link 62 at (112, -20), (136, -20):
  8 pixels lower than the body's last row, over it; GRYPHON's events thrust the neck and the head down the
  screen and back while the body stays. Higher than the body's saddle so it lies on it.
- gryphon_head (0 123, enemy 835 at (125, 8), right under the neck): the head, its frames (121, 119, 129) opening
  the jaw; modelled half open (119) with fangs in the dark maw and glowing red eyes.

The body's, neck's and head's axes are all at x = 124.5 in the game's coordinates. The plates are reliefs over
the sprites' outlines whose heights follow a map of the parts, the sprites' shading embossed on them and their
colours painted on; the horns are round.

usage: Blender -b --factory-startup -P wave3_ai_gryphon.py -- [--only names] [--preview <prefix>] [--check 1]
       [--whole <prefix>] [--stats 1]
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_ai_kit as kit  # noqa: E402
import wave3_aa_kit as aa  # noqa: E402
import wave3_ab_kit as ab  # noqa: E402
from wave3_ai_kit import k, sh, w, pal, Painter  # noqa: E402

# The body's art: pixel (c, r) at game (28 + c, -98 + r); the whole's origin at game (124, -56) (column 96, row 42).
BODY = kit.frame("GRYPHON_BODY", 186, (96, 42))
BODY_PAINT = kit.frame("GRYPHON_BODY", 186, (96, 42)).fill({0x01, 0xfe})
NECK = kit.frame("GRYPHON_NECK", 48, (24, 14))
NECK_PAINT = kit.frame("GRYPHON_NECK", 48, (24, 14)).fill({0x01, 0xfe})
HEAD = kit.frame("GRYPHON_HEAD_119", 24, (12, 14))
HEAD_PAINT = kit.frame("GRYPHON_HEAD_119", 24, (12, 14)).fill({0x01, 0xfe})
AXIS = 96  # the body's axis: pixel column 96's centre (x = 0.5)


def clamp01(v):
    return max(0.0, min(1.0, v))


def painter():
    return Painter("gryph", shades={0: (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14),
                                    3: (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14),
                                    7: (2, 4, 6, 8)},
                   metallic=0.35, roughness=0.35, remap={0xfe: 0x01, 0x00: 0x01},
                   finish={0: (0.55, 0.3), 3: (0.3, 0.35)})


def grey(v):
    return v is not None and v >> 4 == 0 and (v & 15) >= 3


# --- The body ---------------------------------------------------------------------------------------------------

def body_zone(v, c, r):
    """Which part a pixel of the body belongs to: H a horn (round, left out of the relief), G the grey claws at the
    shoulders, K the grey claws at the wings' tips, T the body, L the saddle under the neck, W the wings."""
    if v is None:
        return None
    dc = abs(c - AXIS)
    if r <= 41 and dc <= 16:
        return "H"
    if 40 <= r <= 59 and 12 <= dc <= 38 and (grey(v) or (v >> 4 == 0 and r <= 57)):
        return "G"
    if dc >= 78 and grey(v):
        return "K"
    if r >= 63 and dc <= 26:
        return "L"
    if dc <= 14 and r >= 30:
        return "T"
    return "W"


def body_height(z, c, r):
    dc = abs(c - AXIS)
    if z == "T":
        return 5.0 + 4.6 * math.sqrt(clamp01(1.0 - (dc / 15.0) ** 2)) * clamp01((64 - r) / 10.0)
    if z == "G":
        return 6.6 - 1.6 * clamp01((dc - 14) / 22.0)
    if z == "K":
        return 4.2
    if z == "L":
        return 2.6
    # The wings: thick at the shoulders, thinning out to their tips.
    return 2.0 + 2.8 * clamp01((62.0 - dc) / 44.0)


def build_body():
    p = painter()
    blue = p(0x36)

    def height_of(v, c, r):
        z = body_zone(v, c, r)
        return None if z in (None, "H") else body_height(z, c, r)
    height = ab.field(BODY, height_of, blur=2)
    plates = kit.relief_map("gbody", BODY, lambda v, c, r: body_zone(v, c, r) not in (None, "H"), height, blue,
                            edge=1.4, bevel=1.0, emboss=2.6, fine_blur=1, coarse_blur=3, spacing=0.7, sigma=0.9)
    ab.simplify_bottom(plates)
    ab.sharpen_walls(plates)
    # The horns: long, round, tapering up the screen to sharp tips, leaning down towards them; as wide as the
    # sprite's (its black outline half in), bowing out a little in their middles.
    horns = []
    keys = [(0.0, -7.6, 4.9, 8.8), (4.0, -8.3, 4.6, 8.6), (8.0, -9.3, 4.3, 8.2), (12.0, -10.0, 3.7, 7.8),
            (16.0, -10.6, 3.2, 7.3), (20.0, -10.9, 2.9, 6.8), (24.0, -10.7, 2.3, 6.3), (28.0, -10.4, 2.0, 5.8),
            (32.0, -10.0, 1.6, 5.3), (36.0, -9.6, 1.2, 4.9), (39.5, -9.3, 0.9, 4.6), (41.6, -8.6, 0.25, 4.4)]
    for side in (-1, 1):
        path = [(0.5 + side * (0.5 - x), y, z) for y, x, _, z in keys]
        sections = [(hw, hw * 0.92) for _, _, hw, _ in keys]
        horns.append(ab.loft_path(f"ghorn{side:+d}", path, sections, blue, segments=14))
    for obj in [plates] + horns:
        ab.paint(obj, BODY_PAINT, p, wall_steps=2, under=p(0x31), wall_z=0.3 if obj is plates else 0.45, top_blur=1)
    ab.s.merge_flat(plates, 1.0)


def body_piece(sprite, gx, gy, x0=None, x1=None):
    """A piece of the body: the sprite the events put at (gx, gy); x0, x1 narrow its box where 15 and 53 overlap
    13 and 51."""
    cx, cy = gx - 124.0, -(gy + 56.0)
    bx0 = cx - 12.0 if x0 is None else x0
    bx1 = cx + 12.0 if x1 is None else x1
    c0, r0 = gx - 12 - 28, gy - 14 + 98
    e = 0.01
    return (f"gryphon_{sprite}", (bx0 + e, bx1 - e, cy - 14.0 + e, cy + 14.0 - e), (cx, cy),
            lambda: BODY.mask((c0, c0 + 24, r0, r0 + 28)))


CUT = 69.0  # between 13 (x 48 .. 72) and 15 (x 66 .. 90): the middle of their overlap
BODY_PIECES = [body_piece(1, 40, -84), body_piece(3, 64, -84), body_piece(7, 112, -84), body_piece(9, 136, -84),
               body_piece(13, 184, -84, x1=CUT), body_piece(15, 202, -84, x0=CUT),
               body_piece(39, 40, -56), body_piece(41, 64, -56), body_piece(43, 88, -56), body_piece(45, 112, -56),
               body_piece(47, 136, -56), body_piece(49, 160, -56), body_piece(51, 184, -56, x1=CUT),
               body_piece(53, 202, -56, x0=CUT),
               body_piece(79, 64, -28), body_piece(81, 88, -28), body_piece(83, 112, -28), body_piece(85, 136, -28),
               body_piece(87, 160, -28), body_piece(89, 184, -28)]

kit.pieced("gryphon_body", build_body, (186, 84), BODY_PIECES)


# --- The neck ---------------------------------------------------------------------------------------------------

def neck_zone(v, c, r):
    if v is None:
        return None
    dc = abs(c - 24)
    if grey(v) and dc >= 4:
        return "G"
    if dc <= 4:
        return "S"
    return "N"


def neck_height(z, c, r):
    dc = abs(c - 24)
    drop = clamp01((r - 18) / 9.0)
    if z == "S":
        return 9.2 - 1.2 * dc / 4.0 - 2.0 * drop
    if z == "G":
        return 7.6 - 1.4 * clamp01((dc - 4) / 14.0) - 1.0 * drop
    return 6.6 - 1.4 * drop


def build_neck():
    p = painter()

    def height_of(v, c, r):
        z = neck_zone(v, c, r)
        return None if z is None else neck_height(z, c, r)
    height = ab.field(NECK, height_of, blur=1)
    plates = kit.relief_map("gneck", NECK, lambda v, c, r: v is not None, height, p(0x36), edge=1.2, bevel=1.0,
                            emboss=2.2, fine_blur=1, coarse_blur=3, spacing=0.5, sigma=0.8)
    ab.simplify_bottom(plates)
    ab.sharpen_walls(plates)
    ab.paint(plates, NECK_PAINT, p, wall_steps=2, under=p(0x31), wall_z=0.3, top_blur=1)
    ab.s.merge_flat(plates, 1.0)


kit.pieced("gryphon_neck", build_neck, (48, 28), kit.grid_pieces("gryphon_neck_", NECK, ["91", "93"], 2, 1))


# --- The head ---------------------------------------------------------------------------------------------------

def head_zone(v, c, r):
    if v is None:
        return None
    dc = abs(c - 11)
    if v >> 4 == 7:
        return "E"
    if 9 <= r <= 18 and dc <= 3 and (v >> 4 == 0 and (v & 15) <= 1 or v == 0x30):
        return "M"
    if r >= 12:
        return "J"
    return "S"


def head_height(z, c, r):
    dc = abs(c - 11)
    if z == "S":
        return 6.8 - 0.9 * clamp01(r / 11.0) - 1.6 * clamp01((dc - 6) / 6.0)
    if z == "E":
        return 5.0
    if z == "M":
        return 2.2
    return 4.6 - 1.4 * clamp01((r - 12) / 10.0)


@kit.model("gryphon_head", mask=lambda: HEAD.mask())
def gryphon_head():
    p = painter()

    def height_of(v, c, r):
        z = head_zone(v, c, r)
        return None if z is None else head_height(z, c, r)
    height = ab.field(HEAD, height_of, blur=1)
    skull = kit.relief_map("ghead", HEAD, lambda v, c, r: v is not None, height, p(0x36), edge=1.2, bevel=1.1,
                           emboss=2.0, fine_blur=1, coarse_blur=3, spacing=0.4, sigma=0.8)
    ab.simplify_bottom(skull)
    ab.sharpen_walls(skull)
    ab.paint(skull, HEAD_PAINT, p, wall_steps=2, under=p(0x31), wall_z=0.3, top_blur=1)
    # The eyes: red lenses glowing in their sockets.
    eye = pal("ghead_eye", 0x76, metallic=0.1, roughness=0.15, glow=1.4)
    for x, y in ((-7.5, 9.2), (6.5, 9.2)):
        kit.lens(f"ghead_eye{x:+.0f}", (x, y, 5.0), (0.0, 0.0, 1.0), (1.6, 1.0, 0.6), eye, sink=0.1, segments=14)
    # Fangs: two hanging from the upper jaw, three standing in the lower one, pale steel.
    fang = pal("ghead_fang", 0x3c, metallic=0.4, roughness=0.25)
    for x in (-2.5, 1.5):
        aa.cone(f"ghead_fang{x:+.0f}", (x, 4.6, 4.2), (x * 0.9, 1.4, 3.0), 0.75, fang, segments=8)
    for x in (-2.5, -0.5, 1.5):
        aa.cone(f"ghead_tooth{x:+.0f}", (x, -4.2, 3.6), (x * 0.95, -1.8, 3.2), 0.55, fang, segments=8)


if __name__ == "__main__":
    kit.run()
