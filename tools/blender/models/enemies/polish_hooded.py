"""CORE's hooded figure (sheet 3 sprites 237 above 275, 2x2 each: one 24 x 56 picture) and its wreck (239 above 277),
polished (2026-10-23, round 38, the quality redo: rebuilt from separate parts; round 36's version, one heightfield of
the whole picture with the sprite's shading laid on and painted face by face, read as a pixel-stepped red-and-black
relief; that one replaced wave3_n.py's hooded_whole() and wave3_ap_core.py's hooded_damaged()).

Where it appears: CORE (episode 4) puts six on the ground at its start (t48-524: enemies 251 above 252 at the same x,
event 6: 237 28 pixels above 275, links 20-25); armour 20 each, value 25, one frame; shot down, each piece shows its
damaged sprite (dgr 239, 277) and stays (dlevel -1: a wreck). No other enemy shows these sprites, and none is another
sprite's pixels mirrored, turned or in other ramps.

As the sprites and their 4x upscales draw it (the picture's columns and rows; lit from the upper left): a figure in a
red hooded cloak seen from the front and above: the hood's red rim (70-75) round a smooth grey stone face (07-0c,
columns 7-20 of rows 6-17, lit at its upper left, a white glint at column 11 of row 17), a grey stone body under it
(columns 10-20 of rows 18-37, 03-07, darker to the right), a grey hand at the left (columns 5-10 of rows 29-35) and a
smaller one at the right (columns 19-21 of rows 26-29); the cloak hanging from the shoulders down to its ragged hem
(rows 50-53), its folds red (70-77) down both sides, its front open and black (01: columns 8-20 of rows 33-52). The
wreck: the face and the hood gone, two clusters of jagged grey stone shards left at the neck (columns 6-21 of rows
20-31), the shoulders broken, the cloak as it was.

Built as such a figure from separate parts, for the game's camera, in the picture's plane (x, y as the picture draws
them, z up; then sheared along the camera's line of sight, y - z tan 20, the normals with it, so that the camera sees
every point where the picture draws it):
- the cloak: a draped mass (polish_ring_machine.relief) over the figure's outline (the sprites' own outline through
  its boundary edges' midpoints, smoothed: polish_fleet_walker.mask_loops), its height an analytic profile along the
  figure (CLOAK: 2.4 at the hem, 6.8 over the shoulders and the hood) rounding over RIM at its edges, its folds crisp
  ridges and troughs along hand-placed curves down both sides (FOLDS, FOLD_SHARP, swelling towards the hem), the arms
  swelling under it from the shoulders to the hands (ARMS), its hem rolled (HEM), the hood's rim rolled round the face
  and its brim standing over the face's top edge (HOOD, BRIM); its opening (the chest from the neck down and the open
  front, merged) a hole whose edges roll down into it (OPEN_ROLL);
- the stone face under the hood: a dome over the face's outline (to 11.3) with a brow ridge (BROW), two eye sockets
  (SOCKETS) each with a faint red glow deep in it (EYE_GLOW: the sprites' reds; tiny, so it reads as a glint), a nose
  (NOSE), the mouth's line (MOUTH), hollow cheeks (CHEEKS) and the chin over the jaw (CHIN: the sprites' white glint);
- the chest in a grey inner robe: rounded sections lofted down the opening (TORSO), vertical folds over it
  (CHEST_FOLDS), a domed clasp at the throat (CLASP), a belt across the waist (BELT) with its buckle (BUCKLE); under the
  belt the black inner robe fills the open front, its folds vertical;
- the hands clutching the cloak's edges (FISTS): a palm, curled fingers (capsules: knuckle, joint, tip) and a thumb
  of stone, each coming out of the sleeve's red cuff.
The wreck: the same cloak torn raggedly above row 27 (TORN, TORN_EDGE: no hood; its opening the intact one's below the
chest's broken top), the robe, the hands, the chest below row 29.5 with its belt (the clasp gone with the face), and
the shards: faceted spikes (convex hulls, flat-shaded, SHARDS) round two broken stumps (0x07).
Materials by part (palette, the shading the geometry's): the cloak and the cuffs 0x76, glowing a little in a lighter
red of its ramp (0x77, 0.07: CORE is dark, and the sprites' reds glow against the black), the black robe 0x01, the
stone (face, hands, shards) 0x09, the stumps' broken stone 0x07, the inner robe 0x08, the clasp and buckle 0x0b, the
belt 0x04, the eyes' glow 0x74 (0x77, 0.26). No face coloured from the sprite's pixels.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; the whole's origin
is the picture's middle (12, 28) (the corner between the two sprites): column c is x = c + 0.5 - 12, row r is y =
27.5 - r; the whole is cut along y = 0 (polish_coral_manta.cut, the caps in each part's own material) into the top
piece, moved so its origin is its sprite's centre (0, 14), and the bottom piece (0, -14) (models.cfg origin). On the
ground: height=-4 sets them on the terrain (all four lines, unchanged).

models.cfg: unchanged (the model lines; the sprite lines of hooded_top, hooded_bottom, hooded_top_damaged and
hooded_bottom_damaged with height=-4). The old code (wave3_n.py, wave3_ap_core.py, wave3_n_art.py's HOOD and
wave3_ap_art.py's HOOD_DMG) went with round 36.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each piece's silhouette
against enemy_3.png as the camera sees it), --only <model,...>, --preview <prefix> (each piece's top and 3/4 views).
"""
import math
import os
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_deli_boss import join, drop_unused  # noqa: E402
from polish_coral_manta import cut  # noqa: E402
from polish_fleet_walker import shear_to_camera, mask_loops, area  # noqa: E402
from polish_ring_machine import relief, Region, round_edge  # noqa: E402
from polish_gyges_wall import parse  # noqa: E402

W, H = 24, 56
LEFT, TOP = -12.0, 28.0

# Sheet 3 237 above 275: the hooded figure, 24 x 56 (rows top to bottom; each pixel its palette index in hex,
# '..' none).
HOODED = """
..
..
..
..
..
..
........................72727001707070
......................700708080707070701
....................0107080908070707050470
....................7208090807070706060471
..................710808080707070608070472
................70080808070707060706080373
..............7008080807070705060607070271
..............0107080908070706070509050301
..............010609090908070605070a020201
................0108090a080706070707020101
................0106070a090808080704010101
................010407070a0c09060502010101
................70720707070704050502010201
................70727407070607030101010201
................01737307070602010102030201
................01737273060502020403040301
..............0172757373060503030403040501
..............0174757473060503030403040701
............01737575740406050203040304070201
............70747575750606050203040205070402
..........017375750775750505020304037206050170
..........017474070606740506010304037206070401
........01737575070505720505010104037204070470
........01747575070607730706050201017172077301
......70727406090b0a7574080606050401017275740101
....70727404050709077374070705050471017175757101
....70727405040607057374040606050372017172757301
..0101727303040504727474040303037173017071747471
..7071737473040503727473040302717171017071727473
..0172737473730471747473030202717171017070727374
..0172737273737072747372020202717170017071717274
..0173737272717173747302020271717101017070717375
..0172727270017373737201017070707001017070717276
..0171727101727373727101707070700101017070717274
..0101717070747774737170017001010101017070707274
..0101017173767273727001700101010101017070717372
..7271727373737071710101010101010170700170717201
..7372737272707101710101010101010101700170700101
....71727273710171010101010101017001010101010101
....72710173747172010101010101010170700101010101
....73737176737201010101017001017070010101010101
......737370737301010101010101010101010170017001
......717373717272717070010101010170707070700170
....71737374710170727001010101010101010101017072
....73757574710170700101010170717070707070707273
........7271737101010170707272727101010101717172
..........7172747271707071737271010170707070
..............727171717171717101
..
..
"""

# Sheet 3 239 above 277: its wreck (the damaged sprites), 24 x 56, the same way.
HOODED_DAMAGED = """
..
..
..
..
..
..
..
..
..
..
..
..
..
..
..
..
..
..
..
..
..............................0101
..............................010401
................010101........01050801
..............0104020401....010306060801
..............0106020301....01040606070701
............010507020303010103030206070b0601
............010606020303010308060104070a0501
..........010506070301030205050602020306070401
........01730506080401030502020505050104070470
........01747576080301040506040105040172077301
......7070710609..0302040505070701010172757401
....70727401010609050403050709080371017175757101
....70727405010304040503040707050472017172757301
..0101727303040503720305040403047273017071747471
..7071737473040503017173030304727471017071727473
..0172737472720401737473030405757371017070727374
..0172737273710101747373020505757170017071717274
..0173737272010171747302020571717101017070717375
..0172727270017301717201010101017001017070717276
..0171727101727372010101700101010101017070717274
..0101717070747774727170017001010101017070707274
..0101017173767273727001700101010101017070717372
..7271727373737071710101010101010170700170717201
..7372737272707101710101010101010101700170700101
....71727273710171010101010101017001010101010101
....72710173747172010101010101010170700101010101
....73737176737201010101017001017070010101010101
......737370737301010101010101010101010170017001
......717373717272717070010101010170707070700170
....71737374710170727001010101010101010101017072
....73757574710170700101010170717070707070707273
........7271737101010170707272727101010101717172
..........7172747271707071737271010170707070
..............727171717171717101
..
..
"""

PIECES = {"intact": [("hooded_top", 237, (-40.0, 40.0, 0.0, 60.0), (0.0, 14.0)),
                     ("hooded_bottom", 275, (-40.0, 40.0, -60.0, 0.0), (0.0, -14.0))],
          "damaged": [("hooded_top_damaged", 239, (-40.0, 40.0, 0.0, 60.0), (0.0, 14.0)),
                      ("hooded_bottom_damaged", 277, (-40.0, 40.0, -60.0, 0.0), (0.0, -14.0))]}

# The cloak's height along the figure (row, height): low at the hem, highest over the shoulders and the hood; how far
# in from its outline it rounds over (RIM); its front edges rolling down into the opening (to OPEN_ROLL of it, over
# OPEN_RIM); the hood's rolled rim round the face (HOOD: its height, how far out of the face's outline, how wide).
CLOAK = [(5.0, 6.2), (12.0, 6.8), (20.0, 6.8), (27.0, 6.3), (34.0, 5.6), (42.0, 4.6), (49.0, 3.5), (55.0, 2.4)]
RIM, OPEN_ROLL, OPEN_RIM = 3.0, 0.5, 1.6
HOOD = (1.3, 1.0, 0.9)
# The folds: ridges along curves of the picture (columns, rows), (height, half width); positive ridges, negative
# troughs; they swell down the figure (FOLD_FADE: from this row on, full at the next).
FOLDS = [([(8.6, 22.0), (6.2, 29.0), (4.0, 37.0), (2.9, 45.0), (2.8, 50.0)], (1.7, 1.45)),
         ([(10.2, 27.5), (8.2, 34.0), (6.6, 42.0), (5.8, 51.5)], (1.8, 1.5)),
         ([(10.8, 34.5), (9.8, 41.0), (9.0, 47.5), (8.8, 52.5)], (1.3, 1.15)),
         ([(7.2, 25.5), (5.0, 32.5), (3.4, 40.5), (2.4, 47.0)], (-1.3, 1.05)),
         ([(9.4, 30.5), (7.2, 38.5), (5.0, 46.5), (4.4, 52.0)], (-1.4, 1.05)),
         ([(10.0, 38.0), (8.0, 45.0), (7.0, 51.5)], (-0.9, 0.8)),
         ([(20.6, 25.0), (21.6, 33.0), (22.3, 41.0), (22.6, 50.0)], (1.8, 1.45)),
         ([(18.9, 30.5), (19.3, 38.5), (19.8, 45.5), (20.3, 51.5)], (1.4, 1.15)),
         ([(19.9, 27.5), (20.5, 35.5), (21.1, 43.5), (21.5, 51.0)], (-1.2, 0.95)),
         ([(22.6, 30.0), (23.2, 38.0), (23.4, 46.0)], (-0.8, 0.8)),
         ([(12.8, 49.5), (13.4, 53.2)], (1.0, 1.1)), ([(16.4, 48.5), (17.0, 52.8)], (0.9, 1.0)),
         ([(4.5, 47.5), (6.0, 52.0)], (0.9, 1.0))]
FOLD_FADE = (19.0, 30.0)
FOLD_SHARP = 1.35                # the folds' crests: (1 - distance / half width) to this power (crisp, not round)
CREST_SOFT = 0.22                # (their very crest rounded over this, so the mesh resolves it)
# The open front: the inner robe's height (its base, its rise over its rim) and its folds.
ROBE = (1.6, 1.5, 2.2)
# The stone face: its dome (its base, its height, how far in it rises) and its features (columns, rows of the picture):
# the brow ridge, the eye sockets (middle, radii, depth) with a faint glow deep in each, the nose ridge and its tip,
# the mouth's line, the cheeks' hollows, the chin (the sprites' white glint) over the jaw; the hood's brim standing
# over the face's top edge (height, how far out of the face's outline, how wide, down to this row).
FACE = (4.4, 6.0, 4.4)
BROW = ([(9.3, 10.9), (12.0, 10.3), (14.2, 10.4), (16.6, 9.9), (18.8, 9.6)], (0.8, 0.75))
SOCKETS = [((11.9, 12.2), (1.55, 1.05), 1.35), ((16.4, 11.7), (1.5, 1.05), 1.35)]
EYE_GLOW = (0x74, 0x77, 0.26, 0.42)       # the glow deep in the sockets: colour, emission colour, strength, radius
NOSE = ([(14.3, 11.2), (14.0, 13.2), (13.8, 14.6)], (0.75, 0.6), ((13.8, 14.6), 0.8, 0.35))
MOUTH = ([(11.9, 15.7), (13.6, 15.85), (15.6, 15.4)], (-0.45, 0.4))
CHEEKS = [((10.3, 14.6), 1.3, -0.35), ((17.6, 14.0), 1.3, -0.35)]
CHIN = ((12.9, 16.8), 1.4, 0.55)
BRIM = (1.7, -0.2, 0.75, 12.5)
# The body: rings down the figure (row, its middle's column, half its width, its top), lofted, its foot at z 1.5.
TORSO = [(16.7, 14.1, 2.0, 6.6), (18.5, 14.6, 2.9, 6.8), (22.0, 15.2, 3.7, 6.9), (26.0, 15.4, 4.0, 6.7),
         (29.5, 15.1, 3.5, 6.2), (32.4, 14.8, 2.9, 5.6), (33.5, 14.7, 2.0, 4.9), (34.1, 14.6, 1.0, 4.3)]
# The inner robe over the chest: vertical folds (height, spacing, phase), a clasp at the throat (column, row, radius),
# a belt across the waist (from row, to row) with its buckle (column, half width, half height).
CHEST_FOLDS = (0.4, 2.3, 0.6)
CLASP = (14.4, 19.5, 1.15)
BELT = (30.7, 31.9)
BUCKLE = (14.9, 0.8, 0.65)
# The arms under the cloak: broad swellings from the shoulders down to the hands (curve, (height, half width)).
ARMS = [([(9.6, 21.5), (9.0, 25.5), (8.4, 28.6)], (1.6, 1.9)), ([(19.6, 21.5), (20.1, 24.5), (20.1, 26.0)], (1.1, 1.5))]
# The hands clutching the cloak's edges: the palm (middle, radii, height), the fingers (knuckle, middle joint and tip:
# column, row, height; radius), the thumb, the sleeve's cuff round the wrist (middle, radius, its tube's radius).
FISTS = [{"palm": ((8.1, 30.2), (1.9, 1.7, 1.2), 5.9),
          "fingers": [([(6.6, 31.4, 6.5), (6.4, 32.5, 6.3), (6.6, 33.2, 5.3)], 0.5),
                      ([(7.6, 31.6, 6.7), (7.5, 32.7, 6.5), (7.6, 33.4, 5.5)], 0.52),
                      ([(8.6, 31.6, 6.7), (8.6, 32.7, 6.5), (8.6, 33.4, 5.5)], 0.5),
                      ([(9.5, 31.4, 6.5), (9.6, 32.4, 6.3), (9.4, 33.0, 5.4)], 0.44)],
          "thumb": ([(9.9, 29.9, 6.1), (10.3, 31.0, 6.5), (9.9, 31.8, 6.6)], 0.5),
          "cuff": ((8.7, 28.5, 5.7), 1.9, 0.62)},
         {"palm": ((20.1, 27.0), (1.25, 1.2, 0.9), 5.6),
          "fingers": [([(19.3, 27.8, 6.0), (19.2, 28.6, 5.9), (19.3, 29.1, 5.1)], 0.38),
                      ([(20.1, 27.9, 6.1), (20.1, 28.7, 6.0), (20.1, 29.2, 5.2)], 0.4),
                      ([(20.9, 27.8, 6.0), (21.0, 28.5, 5.9), (20.9, 29.0, 5.1)], 0.36)],
          "thumb": None,
          "cuff": ((20.1, 26.0, 5.4), 1.35, 0.5)}]
HEM = (0.75, 1.0, 0.65, 46.0)    # the hem's rolled edge: its height, how far in from the outline, how wide, from row
# The wreck: the stone shards left at the neck: tips (column, row, height) round each cluster's base (column, row,
# radius, height).
SHARDS = [((9.4, 28.2, 4.2, 6.6), [(8.4, 22.2, 9.4), (10.8, 23.0, 8.8), (6.6, 25.0, 7.8), (11.9, 25.8, 8.2),
                                   (7.4, 28.4, 7.2)]),
          ((16.8, 27.0, 5.0, 6.9), [(15.6, 20.0, 10.2), (17.3, 21.2, 9.8), (19.2, 23.4, 9.2), (20.8, 25.6, 8.4),
                                    (13.6, 22.8, 8.8), (18.6, 27.2, 8.4), (14.6, 26.4, 8.0)])]
TORN = 27.4                      # the wreck's cloak torn off above this row (its hood gone)
MATS = {"cloak": 0x76, "robe": 0x01, "stone": 0x09, "broken": 0x07, "cloth": 0x08, "metal": 0x0b, "belt": 0x04}
CLOAK_GLOW = (0x77, 0.07)        # the cloak's glow: in a lighter red of its own ramp
TORN_EDGE = [(1.7, 1.7, 0.0), (1.0, 0.85, 1.3)]   # the wreck's cloak torn raggedly: (amplitude, frequency, phase)


def px(c, r):
    return (c - 12.0, 28.0 - r)


def lerp_table(table, r):
    if r <= table[0][0]:
        return table[0][1]
    for (r0, v0), (r1, v1) in zip(table, table[1:]):
        if r <= r1:
            t = (r - r0) / (r1 - r0)
            return v0 + (v1 - v0) * (t * t * (3 - 2 * t))
    return table[-1][1]


def smoothstep(e0, e1, x):
    t = min(1.0, max(0.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


def seg_dist(p, a, b):
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    t = max(0.0, min(1.0, ((p[0] - ax) * dx + (p[1] - ay) * dy) / max(dx * dx + dy * dy, 1e-9)))
    return math.hypot(p[0] - ax - t * dx, p[1] - ay - t * dy)


def curve_dist(p, pts):
    return min(seg_dist(p, a, b) for a, b in zip(pts, pts[1:]))


# --- The picture -------------------------------------------------------------------------------------------------------

class Picture:
    """A 24 x 56 picture's palette indices (-1: none) and the masks the parts are built over."""

    def __init__(self, text):
        rows = parse(text)
        a = np.full((H, W), -1, int)
        for r, row in enumerate(rows):
            for c, v in enumerate(row):
                if v is not None:
                    a[r, c] = v
        self.a = a
        has = a >= 0
        ramp = np.where(has, a >> 4, -1)
        shade = np.where(has, a & 15, 0)
        self.has = has
        self.red = has & (ramp == 7)
        self.grey = has & (ramp == 0) & (shade >= 3)
        self.dark = has & (ramp == 0) & (shade <= 2)

    def loops(self, mask, sigma=1.3, min_area=3.0):
        return [l for l in mask_loops(mask, LEFT, TOP, chaikin=1, sigma=sigma) if area(l) >= min_area]


def morph(mask, size, grow):
    out = mask.copy() if grow else np.ones_like(mask)
    lo = -(size // 2)
    for dr in range(lo, lo + size):
        for dc in range(lo, lo + size):
            shifted = np.zeros_like(mask)
            r0, r1 = max(0, dr), mask.shape[0] + min(0, dr)
            c0, c1 = max(0, dc), mask.shape[1] + min(0, dc)
            shifted[r0:r1, c0:c1] = mask[r0 - dr:r1 - dr, c0 - dc:c1 - dc]
            out = (out | shifted) if grow else (out & shifted)
    return out


def largest(loops):
    return max(loops, key=area)


def masks(pic, damaged):
    """The parts' masks: the whole outline, the open front, the face, the stone body; the wreck's cloak torn."""
    rr = np.arange(H)[:, None] * np.ones((1, W), int)
    cc = np.arange(W)[None, :] * np.ones((H, 1), int)
    whole = morph(morph(pic.has, 3, True), 3, False) | pic.has
    front = pic.dark & (rr >= 33) & (rr <= 52) & (cc >= 7) & (cc <= 20)
    front = morph(morph(front, 3, True), 3, False)
    front = morph(morph(front, 2, False), 2, True)
    black_front = front
    face = pic.grey & (rr >= 5) & (rr <= 17)
    face = morph(morph(face, 3, True), 3, False)
    body = pic.grey & (rr >= 17) & (rr <= 37) & (cc >= 10) & (cc <= 20)
    body = morph(morph(body, 3, True), 3, False)
    body = morph(morph(body, 2, False), 2, True)
    if damaged:
        torn = TORN + sum(a * np.sin(cc * f + ph) for a, f, ph in TORN_EDGE)
        whole = whole & ((rr >= torn) | pic.red)
    # The cloak's opening: the open front and the stone body in it (from the neck down), merged.
    opening = morph(morph(black_front | (body & (rr >= 19)), 3, True), 3, False)
    return {"whole": whole, "front": black_front, "face": face, "body": body, "opening": opening}


# --- The parts ---------------------------------------------------------------------------------------------------------

def materials():
    pal = k.level_palette()

    def m(name, idx, metallic, roughness, glow=0.0):
        extra = dict(emission=pal[idx], emission_strength=glow) if glow else {}
        return k.material("hooded_" + name, palette=idx, metallic=metallic, roughness=roughness, **extra)
    cloak_mat = k.material("hooded_cloak", palette=MATS["cloak"], metallic=0.0, roughness=0.74,
                           emission=pal[CLOAK_GLOW[0]], emission_strength=CLOAK_GLOW[1])
    eye = k.material("hooded_eye", palette=EYE_GLOW[0], metallic=0.0, roughness=0.4, emission=pal[EYE_GLOW[1]],
                     emission_strength=EYE_GLOW[2])
    return {"cloak": cloak_mat, "robe": m("robe", MATS["robe"], 0.0, 0.9),
            "stone": m("stone", MATS["stone"], 0.1, 0.5), "broken": m("broken", MATS["broken"], 0.1, 0.6),
            "cloth": m("cloth", MATS["cloth"], 0.0, 0.75), "metal": m("metal", MATS["metal"], 0.6, 0.3),
            "belt": m("belt", MATS["belt"], 0.2, 0.6), "eye": eye}


def cloak(m, outline, front_loop, face_loop):
    """The cloak: a draped mass over the figure's outline, its opening (the stone body and the open front) a hole in
    it whose edges roll down into it, its folds ridges and troughs swelling down the figure, the arms swelling under
    it, its hem rolled, the hood's rim rolled round the face."""
    outer = Region([outline])
    opening = Region([front_loop])
    face = Region([face_loop]) if face_loop else None
    rims = {}

    def height(x, y, d):
        r = 28.0 - y
        do = float(outer.distance([(x, y)])[0])
        dh = float(opening.distance([(x, y)])[0])
        z = lerp_table(CLOAK, r) * round_edge(do, RIM)
        z *= OPEN_ROLL + (1.0 - OPEN_ROLL) * round_edge(dh, OPEN_RIM)
        c = x + 12.0
        for pts, (amp, half) in FOLDS:
            dist = curve_dist((c, r), pts)
            w = half * 1.5
            if dist < w:
                fade = smoothstep(FOLD_FADE[0], FOLD_FADE[1], r)
                t = min(1.0, math.hypot(dist, CREST_SOFT) / w)
                z += amp * fade * (1.0 - t) ** FOLD_SHARP * round_edge(do, 1.2)
        for pts, (amp, half) in ARMS:
            dist = curve_dist((c, r), pts)
            if dist < 3 * half:
                z += amp * math.exp(-(dist / half) ** 2) * round_edge(do, 1.5)
        hh, hin, hw, hrow = HEM
        if r > hrow:
            z += hh * math.exp(-((do - hin) / hw) ** 2) * smoothstep(hrow, hrow + 3.0, r)
        if face is not None and r < 23.0:
            inside_face = bool(face.inside([(x, y)])[0])
            df = float(face.distance([(x, y)])[0]) * (-1.0 if inside_face else 1.0)
            h, off, wid = HOOD
            z += h * math.exp(-((df - off) / wid) ** 2) * (1.0 - smoothstep(19.0, 23.0, r))
            bh, boff, bw, brow = BRIM
            z += bh * math.exp(-((df - boff) / bw) ** 2) * (1.0 - smoothstep(brow - 3.0, brow, r))
        return max(z, 0.05)
    polys = [outline, front_loop]
    return relief("cloak", polys, height, m, paint=lambda x, y, d: "cloak", side="cloak", bottom=0.0, spacing=0.44,
                  smooth_angle=70.0)


def robe(m, front_loop):
    """The black inner robe in the open front, its edges tucked under the cloak's."""
    grown = grow_loop(front_loop, 0.9)
    reg = Region([front_loop])

    def height(x, y, d):
        r = 28.0 - y
        z = ROBE[0] + ROBE[1] * round_edge(d, ROBE[2])
        z += 0.5 * math.cos((x + 12.0) * 2.0 * math.pi / 2.4 + 0.7 + r * 0.05) * smoothstep(35.0, 43.0, r) * \
            round_edge(d, 1.0)
        return z
    return relief("robe", [grown], height, m, paint=lambda x, y, d: "robe", side="robe", bottom=0.0, spacing=0.55,
                  smooth_angle=70.0, band=1.2)


def grow_loop(loop, amount):
    """A loop moved out along its normals (it is counter-clockwise round its inside)."""
    n = len(loop)
    out = []
    for i in range(n):
        (x0, y0), (x1, y1), (x2, y2) = loop[i - 1], loop[i], loop[(i + 1) % n]
        tx, ty = x2 - x0, y2 - y0
        length = math.hypot(tx, ty) or 1.0
        out.append((x1 + ty / length * amount, y1 - tx / length * amount))
    return out


def bump(c, r, centre, radius, amp):
    q = ((c - centre[0]) ** 2 + (r - centre[1]) ** 2) / radius ** 2
    return amp * max(0.0, 1.0 - q) ** 2


def face_height(face_loop):
    """The stone face's height over the picture's plane: a dome over its outline, its brow ridge, eye sockets, nose,
    mouth, cheeks and chin."""
    reg = Region([face_loop])

    def height(x, y, d=None):
        if d is None:
            d = float(reg.distance([(x, y)])[0])
        c, r = x + 12.0, 28.0 - y
        z = FACE[0] + FACE[1] * round_edge(d, FACE[2])
        inner = round_edge(d, 1.4)
        pts, (amp, half) = BROW
        dist = curve_dist((c, r), pts)
        if dist < 1.5 * half:
            z += amp * (1.0 - dist / (1.5 * half)) ** 1.5 * inner
        for (sc, sr), (rx, ry), depth in SOCKETS:
            q = ((c - sc) / rx) ** 2 + ((r - sr) / ry) ** 2
            if q < 1.0:
                z -= depth * (1.0 - q) ** 1.5 * inner
        pts, (amp, half), (tip, trad, tamp) = NOSE
        dist = curve_dist((c, r), pts)
        if dist < 1.5 * half:
            z += amp * (1.0 - dist / (1.5 * half)) ** 1.4 * inner
        z += bump(c, r, tip, trad, tamp) * inner
        pts, (amp, half) = MOUTH
        dist = curve_dist((c, r), pts)
        if dist < 1.5 * half:
            z += amp * (1.0 - dist / (1.5 * half)) ** 1.4 * inner
        for centre, rad, amp in CHEEKS:
            z += bump(c, r, centre, rad, amp) * inner
        (cc, cr), rad, amp = CHIN
        z += bump(c, r, (cc, cr), rad, amp) * round_edge(d, 0.8)
        return z
    return height


def face(m, face_loop):
    """The stone face under the hood (face_height), a faint glow deep in each eye socket."""
    height = face_height(face_loop)
    obj = relief("face", [face_loop], lambda x, y, d: height(x, y, d), m, paint=lambda x, y, d: "stone", side="stone",
                 bottom=2.0, spacing=0.26, smooth_angle=60.0)
    eyes = []
    for i, ((sc, sr), _, _) in enumerate(SOCKETS):
        x, y = px(sc, sr)
        z = height(x, y)
        rad = EYE_GLOW[3]
        eyes.append(ellipsoid("eye_%d" % i, (x, y, z + 0.05), (rad * 1.25, rad, rad * 0.8), m["eye"], 12, 6))
    return [obj] + eyes


def torso_at(r):
    """The chest's section at a row: (its middle's column, half its width, its top), between the TORSO rings."""
    for (r0, c0, h0, t0), (r1, c1, h1, t1) in zip(TORSO, TORSO[1:]):
        if r0 <= r <= r1:
            f = (r - r0) / (r1 - r0)
            f = f * f * (3 - 2 * f)
            return c0 + (c1 - c0) * f, h0 + (h1 - h0) * f, t0 + (t1 - t0) * f
    return TORSO[-1][1:] if r > TORSO[-1][0] else TORSO[0][1:]


def torso(m):
    """The chest under the face, in the inner robe: rounded sections down the figure (TORSO) lofted, vertical folds
    over its top (CHEST_FOLDS, fading up to the neck); the clasp at the throat, the belt across the waist with its
    buckle."""
    amp, spacing, phase = CHEST_FOLDS
    rings = []
    r = TORSO[0][0]
    while r <= TORSO[-1][0] + 1e-6:
        c, half, top = torso_at(r)
        x, y = px(c, r)
        hz = (top - 1.5) / 2.0
        ring = k.ring(y, half, hz, 28, z=1.5 + hz, x=x, power=2.6)
        fade = smoothstep(18.0, 23.0, r)
        for p in ring:
            up = max(0.0, (p.z - (1.5 + hz)) / hz)
            p.z += amp * fade * up ** 2 * math.cos((p.x - x) * 2.0 * math.pi / spacing + phase)
        rings.append(ring)
        r += 0.75
    rings.reverse()                     # ordered along +y
    chest = k.smooth(k.loft("torso", rings, m["cloth"]), 70)
    out = [chest]
    # the clasp: a domed disc at the throat
    cc, cr, rad = CLASP
    x, y = px(cc, cr)
    z0 = torso_at(cr)[2] - 0.15
    clasp = mk.lathe("clasp", [(rad, z0), (rad, z0 + 0.3), (rad * 0.75, z0 + 0.55), (rad * 0.4, z0 + 0.68),
                               (0.01, z0 + 0.7)], (x, y), m["metal"], 20)
    k.recalc_normals(clasp)
    out.append(k.smooth(clasp, 50))
    # the belt: a band round the chest's section, a little out of it, its edges rounded
    r0, r1 = BELT
    brings = []
    for f, grow in ((0.0, 0.05), (0.15, 0.3), (0.85, 0.3), (1.0, 0.05)):
        r = r0 + (r1 - r0) * f
        c, half, top = torso_at(r)
        x, y = px(c, r)
        hz = (top - 1.5) / 2.0
        brings.append(k.ring(y, half + grow, hz + grow, 28, z=1.5 + hz, x=x, power=2.6))
    brings.reverse()
    out.append(k.smooth(k.loft("belt", brings, m["belt"]), 50))
    bc, bw, bh = BUCKLE
    br = (r0 + r1) / 2
    x, y = px(bc, br)
    ztop = torso_at(br)[2] + 0.3
    buckle = mk.box("buckle", x - bw, x + bw, y - bh, y + bh, ztop - 0.6, ztop + 0.35, m["metal"])
    mk.bevel(buckle, 0.18, 2, 30)
    out.append(mk.shade(buckle, 40, True))
    return out


def ellipsoid(name, centre, radii, mat, segments=24, rings=12):
    """An ellipsoid lofted from explicit rings (the same faces every run)."""
    cx, cy, cz = centre
    rx, ry, rz = radii
    rs = []
    for i in range(1, rings):
        t = math.pi * i / rings
        rs.append([Vector((cx + rx * math.sin(t) * math.cos(2 * math.pi * j / segments),
                           cy + ry * math.sin(t) * math.sin(2 * math.pi * j / segments), cz - rz * math.cos(t)))
                   for j in range(segments)])
    obj = k.loft(name, rs, mat, start_point=(cx, cy, cz - rz), end_point=(cx, cy, cz + rz))
    return k.smooth(obj, 70)


def capsule(name, pts, radius, mat, segments=8):
    """A rounded bar through points (column, row, height): a tube with a ball at its knuckle and its tip."""
    world = [Vector((c - 12.0, 28.0 - r, z)) for c, r, z in pts]
    parts = []
    tube = mk.tube(name, [tuple(p) for p in world], radius, mat, segments)
    k.recalc_normals(tube)
    parts.append(k.smooth(tube, 70))
    for i in (0, len(world) - 1):
        parts.append(ellipsoid("%s_j%d" % (name, i), tuple(world[i]), (radius, radius, radius), mat, 8, 5))
    return parts


def hands(m):
    """The hands clutching the cloak's edges (FISTS): a palm, curled fingers and a thumb of stone, coming out of the
    sleeve's red cuff."""
    out = []
    for i, fist in enumerate(FISTS):
        (c, r), radii, z = fist["palm"]
        x, y = px(c, r)
        out.append(ellipsoid("palm_%d" % i, (x, y, z), radii, m["stone"], 16, 8))
        for j, (pts, rad) in enumerate(fist["fingers"]):
            out += capsule("finger_%d_%d" % (i, j), pts, rad, m["stone"])
        if fist["thumb"]:
            pts, rad = fist["thumb"]
            out += capsule("thumb_%d" % i, pts, rad, m["stone"])
        (cc, cr, cz), big, small = fist["cuff"]
        cx, cy = px(cc, cr)
        circle = [(cx + big * math.cos(2 * math.pi * a / 20), cy, cz + 0.8 * big * math.sin(2 * math.pi * a / 20))
                  for a in range(21)]
        cuff = mk.tube("cuff_%d" % i, circle, small, m["cloak"], 10, cap=False)
        k.recalc_normals(cuff)
        out.append(k.smooth(cuff, 70))
    return out


class Rand:
    def __init__(self, seed):
        self.state = seed & 0x7FFFFFFF or 1

    def random(self):
        self.state = (1103515245 * self.state + 12345) & 0x7FFFFFFF
        return self.state / 0x7FFFFFFF

    def uniform(self, a, b):
        return a + (b - a) * self.random()


def hull(name, points, mat):
    bm = bmesh.new()
    verts = [bm.verts.new(tuple(p)) for p in points]
    res = bmesh.ops.convex_hull(bm, input=verts, use_existing_faces=False)
    drop = list(dict.fromkeys(g for g in res["geom_interior"] + res["geom_unused"] if isinstance(g, bmesh.types.BMVert)))
    if drop:
        bmesh.ops.delete(bm, geom=drop, context="VERTS")
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.data.materials.append(mat)
    return obj


def shards(m):
    """The wreck's stone shards: faceted spikes round each cluster's broken stump (convex hulls, flat-shaded)."""
    rand = Rand(17)
    out = []
    for n, ((bc, br, rad, bz), tips) in enumerate(SHARDS):
        bx, by = px(bc, br)
        stump = []
        for j in range(9):
            a = 2 * math.pi * (j + rand.uniform(-0.2, 0.2)) / 9
            rr = rad * rand.uniform(0.75, 1.05)
            stump.append(Vector((bx + rr * math.cos(a), by + rr * 1.15 * math.sin(a), bz * rand.uniform(0.75, 1.0))))
            stump.append(Vector((bx + rr * 1.05 * math.cos(a), by + rr * 1.2 * math.sin(a), 1.5)))
        out.append(hull("stump_%d" % n, stump, m["broken"]))
        for i, (tc, tr, tz) in enumerate(tips):
            tx, ty = px(tc, tr)
            base = []
            for j in range(5):
                a = 2 * math.pi * (j + rand.uniform(-0.25, 0.25)) / 5
                rr = rand.uniform(1.9, 2.8)
                # the spike's foot on the stump, part way from the stump's middle towards its tip
                fx, fy = bx + (tx - bx) * 0.4, by + (ty - by) * 0.4
                base.append(Vector((fx + rr * math.cos(a), fy + rr * math.sin(a), bz * rand.uniform(0.6, 0.9))))
            tip = Vector((tx + rand.uniform(-0.2, 0.2), ty + rand.uniform(-0.2, 0.2), tz))
            mid = (sum(base, Vector()) / len(base) + tip) / 2 + Vector((rand.uniform(-0.4, 0.4), rand.uniform(-0.4, 0.4),
                                                                         0.0))
            out.append(hull("shard_%d_%d" % (n, i), base + [tip, mid], m["stone"]))
    for obj in out:
        obj.data.polygons.foreach_set("use_smooth", [False] * len(obj.data.polygons))
    return out


def build_figure(m, pic, damaged):
    ms = masks(pic, damaged)
    outline = largest(pic.loops(ms["whole"], sigma=1.4))
    front = largest(pic.loops(ms["front"], sigma=1.3))
    if damaged:
        # the wreck's opening: the intact one's below the torso's broken top (above it the cloak is torn away)
        intact = Picture(HOODED)
        im = masks(intact, False)
        rows = np.arange(H)[:, None] * np.ones((1, W), int)
        opening = largest(intact.loops(im["opening"] & (rows >= 30), sigma=1.3))
    else:
        opening = largest(pic.loops(ms["opening"], sigma=1.3))
    face_loop = None if damaged else largest(pic.loops(ms["face"], sigma=1.2))
    parts = [cloak(m, outline, opening, face_loop), robe(m, front)]
    if damaged:
        parts += [keep_below(obj, 29.5) for obj in torso(m) if obj.name not in ("clasp",)]
        parts += shards(m)
    else:
        parts += face(m, face_loop)
        parts += torso(m)
    parts += hands(m)
    bpy.context.view_layer.update()
    return parts


def keep_below(obj, row):
    """What of an object lies below a row of the picture (the wreck keeps only the body's lower part), its cut
    closed."""
    y = 28.0 - row
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    res = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-6,
                                 plane_co=(0, y, 0), plane_no=(0, 1, 0), clear_outer=True)
    edges = [e for e in res["geom_cut"] if isinstance(e, bmesh.types.BMEdge) and e.is_valid and len(e.link_faces) == 1]
    if edges:
        bmesh.ops.holes_fill(bm, edges=edges, sides=0)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(obj.data)
    bm.free()
    return obj


# --- Pieces ------------------------------------------------------------------------------------------------------------

def own_mask(sheet, sprite):
    return k.sprite_mask(sheet, sprite)


def build():
    options = k.args()
    out = mk.outdir(options)
    only = set(options["only"].split(",")) if "only" in options else None
    k.reset()
    bpy.context.scene.view_settings.view_transform = "Standard"
    m = materials()
    sheet = os.path.join(options["check"], "enemy_3.png") if "check" in options else None
    for kind, text in (("intact", HOODED), ("damaged", HOODED_DAMAGED)):
        pieces = [p for p in PIECES[kind] if only is None or p[0] in only]
        if not pieces:
            continue
        pic = Picture(text)
        whole = build_figure(m, pic, kind == "damaged")
        print("%s: %d parts, %d triangles" % (kind, len(whole), mk.triangles(whole)))
        for name, sprite, box, origin in pieces:
            parts = []
            for src in whole:
                cap = src.data.materials[0]
                piece = cut(src, box, cap)
                if piece is not None:
                    piece.name = src.name + "_" + name
                    parts.append(piece)
            drop_unused(parts)
            for src in whole:
                src.hide_render = True
            if sheet:
                mk.compare("%s (3 %d, as the camera sees it)" % (name, sprite),
                           mk.coverage(parts, 24, 28, centre=origin), own_mask(sheet, sprite))
            shear_to_camera(parts)
            mk.transform(parts, Matrix.Translation((-origin[0], -origin[1], 0.0)))
            bpy.context.view_layer.update()
            triangulate(parts)
            obj = join(parts, name)
            obj.data.name = name
            mk.report(name, [obj], os.path.join(out, name + ".glb"))
            if "preview" in options:
                mk.preview(options["preview"] + name, [obj])
            bpy.data.objects.remove(obj)
            for src in whole:
                src.hide_render = False
        for src in whole:
            bpy.data.objects.remove(src)


if __name__ == "__main__":
    build()
