"""The grey boulders in the pit of TYRIAN, HOLES and TYRIAN X, and the pit with its glowing pool once they are blown
away, polished (2026-10-22, round 32; it replaces wave3_aa_rocks.py's convex hulls painted by the sprite and
wave3_ap_pit.py's pool and lumps). One 72 x 56 picture that the game puts together from six 2x2 sprites of sheet E:
E 1 3 5 above 39 41 43 (models holes_rocks_tl, _tm, _tr, _bl, _bm, _br) and the damaged look E 7 9 11 above 45 47 49
(holes_rocks_tl_damaged ... _br_damaged).

PLACEMENT (the level events, tools/content/tyrdata.py's enemy data; episodes 1-3 share it)

- TYRIAN (episode 1) t1308: enemies 516-521 (E 1 3 5 39 41 43; armour 20, no damaged look (dgr 0), 516 worth 50),
  event 6 (ground), link 29: 516 at (210, y - 28), 517 (234, y - 28), 518 (258, y - 28), 519 (210, y), 520 (234, y),
  521 (258, y): the picture whole. The ground map paints the pit under them (tiles 341 342 343 above 351 352 353 at
  map row 243, columns 10-12: a dark crater, rubble round its rim, grey teeth in its front half); TYRIAN's terrain is
  flat (0) there. Shot, the six die together (one link) and leave the game's slumped wrecks of these models.
- TYRIAN t1868: enemies 522-527, the same sprites with armour 40, dgr 7 9 11 45 47 49 and dlevel -1, worth 10015,
  link 30, at x 258, 282, 306 (map row 223, columns 12-14; the third column in the wide view's side columns): shot,
  the six switch together to the damaged look (they stay, enemyAvail 2), and flying over it warps the ship to
  section 15 of episode 1, the bonus stage BUBBLES (mainint.c: a value over 10000 on a piece left standing is the
  section to warp to). The pool is that way in.
- HOLES (episode 1) t790: 516-521 on the top layer (event 7, link 22, x 144-192, dat5 -29 / -1): HOLES' background 3
  (solid, its terrain 0 there) paints the same pit tiles (row 505, column 6).
- TYRIAN X (episode 3) t1308 and t1868: 516-521 both times (link 29 and 30): no damaged look, no warp.
- No episode 6 level places them (GRAVITRON's enemies 520 and 521 are episode 5's, sheet 5 sprites). No other enemy
  shows these sprites (catalog.json, launched ones too) and none is another sprite's pixels mirrored, turned or in
  other ramps: no frame models, no twins.

THE BOULDERS (E 1 3 5 above 39 41 43, as the sprites and their 4x upscales draw them; columns and rows of the picture)

Grey stone (ramp 0, 0x02-0x0b) in the pit: the big block (columns 27-66 of rows 0-31), a cube turned to the camera, its
top a broad low ridged roof (lit 0x07-0x08 on the left of the ridge from its back (46, 1) down to its front corner
(43, 16), darker 0x05-0x06 on the right), the lit diagonal along the roof's left edge (0x09-0x0b), a steep dark face
under it, the crease down its front corner and the broad right-front face; in front of its steep face a boulder in its
shadow (29-46, 18-31) with a lit edge down its front; left of it the middle boulder (12-32, 11-31), its top in shade
and a broad lit face down its front (16-25, 19-28), and the left boulder (0-16, 13-33), lit along its left and on a
face at its right; the boulders' dark lower faces (rows 28-36), dark stones at the big block's right foot (45-61,
21-34), a few low stones and pebbles lying on the pit's floor in front. The dirt round the pit and the pit's dark
floor (0x20) are the map's (the sprites carry a copy of them; the game's HD tiles paint the crater with its teeth):
not modelled.

Each boulder is the convex hull of points placed where the camera sees them (Boulder: columns, rows and heights of the
picture, each moved TILT z down the screen, so that the game's camera, 20 degrees from straight down, sees every
point where the sprite draws it; a roof plane through three points gives the big block's two flat roof planes), the
tops on the hidden back getting feet under them (upright walls, BACK_LEAN back), a few seeded chips off their corners,
its edges chamfered (CHAMFER), standing on FOOT a little under the ground; the boulders' fronts run down onto the
pit's floor (feet at rows 31-36), so the heap lies in the pit, and the stones in front are low rounded cobbles (COBBLES,
INTACT_PEBBLES: hulls of rings of points on a squashed dome, 0.8-2 high) lying on the floor, no upright slabs (an
in-game check of the first version, TYRIAN round frame 1520, found its front teeth reading as legs over the dark
crater). Each face painted one grey (boulder_value): the median of the sprite's shades where the camera sees that face
(rays along its line of sight through the pixels), up to LIFT lighter (none at the floor, the full lift from LIFT_FULL
up: the game's light reads palette greys darker), and ORIENT shades per unit lighter or darker as the face looks up
more or less than UP_REF (the game's light shades the faces evenly: lit tops, darker sides, fronts and lower faces, as
the sprite draws them); chamfers facing the sun a highlight. Then weathered (polish_asteroids.roughen: the faces the
camera sees retriangulated evenly and moved along their normals by smooth noise), darker where boulders meet (CREVICE:
the faces cut along contours of the distance to the other boulders) and at the foot (GROUNDED). The big block's top
12.8 high, the middle boulder 9, the left 7.4, the dark stones at its right foot 3-3.6, the cobbles 1-2.

THE PIT (E 7 9 11 above 45 47 49)

The boulders gone, in the pit (the map's) a pool of glowing blue water (ramp 9, its rim dark purple ramp 5), a whirl
of brighter crescents round a darker middle (the brightest at its upper left and down its right); in front of it the
teeth the boulders hid (lit at their tops, 0x05-0x06); rubble (grey, 0x02-0x09) and clods of dirt (dark brown, ramp 10)
round its back and sides; the pebbles as before. The pool: rings from its middle out to its outline (traced from the
sprite's blue and purple pixels, rays from its middle, no further down the screen than POOL_ELLIPSE), the water rising
from POOL_Z's middle to its rim (a shallow whirl), a wall down to the feet; painted by the sprite's blues (blurred)
along smooth contours (polish_orb_red.band_split) in POOL_BANDS (0x91 to 0x9e, glowing 0.1 to 0.6). The stones are
the boulders' machinery (PIT_STONES, painted from the damaged sprite's greys by rock_value: LIFT lighter, less so low
down, and lighter still by COMPENSATE shades per unit of the sun a face gets less than one looking up), the clods small
hulls (0xa3).

Each look is built whole and cut along the planes the camera sees as the sprites' edges (polish_stone_face.view_cut:
x = -12 and 12 upright, y = 0 leaning back up the screen; the caps 0x04, the uncut rock's shading), each piece moved so
that its sprite's centre is its origin, every mesh triangulated (polish_k_pod.triangulate).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the ground; the whole's origin
is the picture's centre (pixel corner 36, 28); P(c, r, z) is the world point the camera sees at the picture's pixel
corner (c, r) at height z. The pieces' centres: tl (-24, 14), tm (0, 14), tr (24, 14), bl (-24, -14), bm (0, -14),
br (24, -14).

models.cfg: the model lines stay (holes_rocks_<tl..br> and holes_rocks_<tl..br>_damaged, origin); the sprite lines of
E 1 3 5 39 41 43 and 7 9 11 45 47 49 get height=-4 (set on the terrain, as their polished neighbours). Replaces
wave3_aa_rocks.py (all of it) and wave3_ap_pit.py (all of it), and the pixels only they read: wave3_aa_art.py's ROCKS
and wave3_ap_art.py's ROCKS_DMG.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <any value> (the silhouettes as the game's
camera sees them, of each look's whole and of each piece, against the sprites' own pixels: the embedded pictures),
--preview <prefix> (each piece's top and 3/4 views, and each look's whole), --whole <prefix> (each look's uncut whole
as <prefix>holes_rocks[_damaged].glb), --only <model,...>, --looks intact,damaged (default both).
"""
import math
import os
import random
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
import polish_asteroids as pa  # noqa: E402
from polish_coral_manta import split_contour  # noqa: E402
from polish_deli_boss import join, drop_unused  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_orb_red import band_split  # noqa: E402
from polish_stone_face import view_cut, view_coverage  # noqa: E402

TILT = math.tan(math.radians(20.0))
W, H = 72, 56
LIGHT = Vector((-0.6, 0.6, 1.0)).normalized()
CAMERA = Vector((0.0, -math.sin(math.radians(20.0)), math.cos(math.radians(20.0))))
FOOT = -0.6                 # the boulders' feet, a little under the ground
BACK_LEAN = 0.3             # how far back of upright their hidden back walls stand


def P(c, r, z=0.0):
    """The world point the game's camera sees at the picture's pixel corner (c, r), z above the ground."""
    return Vector((c - 36.0, 28.0 - r - TILT * z, z))


def picture(v):
    """Where the camera sees a world point: the picture's (column, row) of pixel corners."""
    return v.x + 36.0, 28.0 - (v.y + TILT * v.z)


# --- The art --------------------------------------------------------------------------------------------------------

def load_art(rows):
    a = np.full((len(rows), len(rows[0])), -1, int)
    for r, line in enumerate(rows):
        for c, ch in enumerate(line):
            if ch != ".":
                a[r, c] = int(ch, 16)
    return a


# The intact sprites' greys (ramp 0's shades as hex digits; '.' the dirt, the pit's floor and the transparent).
ROCKS_ART = [
    "........................................................................",
    "...........................................6675.........................",
    "......................................327666777624......................",
    "...................................66764877777773445....................",
    "............................2...5788776487777776556877665...............",
    "............................2889988777658777777647978888874.............",
    "............................5a99877777668777777688788888864442..........",
    "............................469b87777776777777888788888875555543........",
    "............................4459b87777766777788778888885555556653.......",
    "............................44479b9777776677777788887755555566664.......",
    "............................444559a987777766777888765555555666664.......",
    "............................4444559a9877777668887655555666666666........",
    "...............5666663.....244445556a987777768876555666666666665........",
    ".............4666555565...64244445555998777767555566666666666665........",
    "...........26677544445223557534445555589877657566666666666666665........",
    "..........467754334443345555763444555558866656455555556666666655........",
    "........567765334444455555555753445555555666598876666655666655542.......",
    ".......5767533445666644555555575345555555566586666666665565555443.......",
    "...2556754445455665555445555555744.345555566586666666666435543322.......",
    "..568775555665444557886445555543223344455556576666666665542433333.......",
    "..698666666678324798777754554432444334444444576666666655443233332.......",
    "..5a66666667783359877777753444234444334444445666666654444433.332........",
    "..5976666677883457977777773353234444435444566566655444444434.33..2......",
    ".45867666778883455987777854552334444436445655334444443..22442.2.........",
    ".4475667778846344579777784555233444453645655643444442.2334443....2......",
    ".327445667749824455877786455423344445365655643344442.23335443...22......",
    ".22644444539882345568787455542334444536655563334444.233345443...22......",
    ".2.63444437555.244556785455542334444537455642234444.23345443...22.......",
    "...33334364443.234556874555442334444534555622224442.23354433...2........",
    "...22222254443..2345666455443234555552555642..2432..23533332...2........",
    "......22.43332...334444455432345555543555622...4.23..433333....2........",
    ".........422......2444434442345555545334642.33..3542.33332.....2........",
    ".........322.......33443334234555546675364..33.25443.332.......2........",
    "...................2233333323455546555643..23..45433.3.........2........",
    "........22..........2223333.245554655555...22..44333....................",
    ".......22222..22.....222233.2345436555532..2...33333....................",
    ".........22..3222......2223.2344226555522..2...33332....................",
    ".............3...2.......22.2342..555542...2...3332..........22.........",
    "..................2.......2..322..54553....2...332...........222........",
    "..................................54542.......222.......................",
    "..................................54422.......22........................",
    "...................2.....232......4332..................................",
    "...................2....2332......2322.......2332.......................",
    "..................22.3...2222......22.......222.........................",
    ".................2...32...232..............2222..243....................",
    "...........................................222...232....................",
] + ["." * 72] * 10


# The damaged look's pixels: its greys (the stones), the dark browns (clods of dirt) and the pool (ramp 9; its rim's
# dark purples, ramp 5, as 0).
PIT_ART = [
    "........................................................................",
    "........................................................................",
    "........................................................................",
    "........................................................................",
    "........................................................................",
    "........................................................................",
    "........................................................................",
    "........................................................................",
    "........................................................................",
    "..................................................43....................",
    ".................................................4532...................",
    "...............23.................................2322..................",
    "...............34.............................232.......................",
    "................2............................6843..22...22..............",
    "....................33..................3453..4552.392...24.............",
    "...................322..................3664...2...453...274............",
    ".................5..2..............................243....653...........",
    "............54.2..........................................444...........",
    ".......54..332.............................................22...........",
    "......594...............................................................",
    "......342...............................................................",
    "........................................................................",
    ".............................................................2..........",
    "....2.63.....................................................24.........",
    "......53.....................................................3432.......",
    ".............................................................2333.......",
    ".......54...............................................................",
    ".......32.....................................................2.........",
    "...33.2....22........553................................................",
    "...222.4..3442......35643......................................2........",
    "......22.34332...3..244452.............................32......2........",
    ".........422........244363...352.................53...3332.....2........",
    ".........322.........44353...3552..364.........2543..332.......2........",
    ".....................33353...3554.35552........4542..2.........2........",
    "........22...........22343...3555365555........4433.....................",
    ".......22222..22.....222232..34543655552.......33332....................",
    ".........22..3222......2222..24422655552.......33332....................",
    ".............3...2.......22..342..555542...2...3332..........22.........",
    "..................2.......2..322..54553....2...332...........222........",
    "..................................54542.......222.......................",
    "..................................54422.......22........................",
    "...................2.....232......4332..................................",
    "...................2....2332......2322.......2332.......................",
    "..................22.3...2222......22.......222.........................",
    ".................2...32...232..............2222..243....................",
    "...........................................222...232....................",
] + ["." * 72] * 10
CLOD_ART = [
    "........................................................................",
    "........................................................................",
    "........................................................................",
    "..............................3.........................................",
    ".............................1...22.....................................",
    "..................................0.....................................",
    ".....................................2....0.............................",
    "..................................0........02...........................",
    "...........................1......1122.0....000.........................",
    "..................................2..2..................................",
    ".................................1122..0................................",
    "........................................................................",
    "........................................................................",
    "........................................................................",
    ".............................22.....00..................................",
    "..................................32....................................",
    "........................................................................",
    "........................................................1...............",
    ".......................................................00...............",
    ".........2.................................................0............",
    "...........................................................0............",
    "..............................................................0.........",
    "...............................................................1........",
    "...............................................................31.......",
    "........................................................................",
    "........................................................................",
    "...............................................................13.......",
    "................................................................3..2....",
    "...............................................................1..100...",
] + ["." * 72] * 27
POOL_ART = ["." * 72] * 16 + [
    "......................00000111111111111111111...........................",
    "................000003333223444455544443346777643..00...................",
    "..............00046799985556789aaaa9875432245577872000..................",
    ".............00379abdddc9668accccccb98765322355778a85200..0.............",
    "............003778bdfffeb879abcbbba98756654455566369a862000.............",
    "...........0058359ceffffc9657888988754456655544454146ba6100.............",
    "..........01473348ceffedb86545789885433457755323331016dc50000...........",
    "..........017412379ccdcb8543348abb974223577542111100139ee3000...........",
    "..........016511235899985432249cdca83213565431000001258bf6000...........",
    "..........1255101123454432111279ba85211345421000001249adf3100...........",
    "..........0125520000000000000124443211134431000011358abeb2100...........",
    "...........000264100000000000011111001223431111123588ba65220............",
    ".............00001000...00..0000000012223321222223476430201..0..........",
    "..............000000.........0.......1111110111110111100......0.........",
    "...............................0......00000000000.00000.................",
    "......................................00000000..........................",
    "........................................00000.0.........................",
    ".........................................000............................",
] + ["." * 72] * 22


# --- Boulders -------------------------------------------------------------------------------------------------------

class Boulder:
    """A boulder: the convex hull of points given as the camera sees them ((column, row, height) of the picture; a
    height given as the name of one of its roofs takes that roof's height there: a roof is a plane through three
    such points), its tops marked "b" getting a foot under them on the hidden back (an upright wall, BACK_LEAN back),
    a few chips off its corners (random planes, seed)."""

    def __init__(self, name, points, chips=3, seed=0, roofs=None):
        self.name = name
        self.chips = chips
        self.seed = seed
        planes = {}
        for key, ((c1, r1, z1), (c2, r2, z2), (c3, r3, z3)) in (roofs or {}).items():
            u, v = Vector((c2 - c1, r2 - r1, z2 - z1)), Vector((c3 - c1, r3 - r1, z3 - z1))
            n = u.cross(v)
            planes[key] = (n, n.dot(Vector((c1, r1, z1))))
        self.points = []
        for p in points:
            c, r, z = p[0], p[1], p[2]
            if isinstance(z, str):
                n, d = planes[z]
                z = (d - n.x * c - n.y * r) / n.z
            self.points.append((c, r, z) + tuple(p[3:]))


BOULDERS = [
    # The big block, a cube turned to the camera: its top a low ridged roof (the ridge from the back down to the front
    # corner; the left plane's edge the lit diagonal), a steep face under the lit diagonal, the crease down its front
    # corner, the broad right-front face, the right wall; its lower faces running down onto the pit's floor.
    Boulder("big", [
        (28.6, 5.2, "L", "b"), (36.0, 2.2, "L", "b"), (46.0, 0.7, 12.6, "b"), (56.0, 3.4, "R", "b"),
        (64.6, 7.2, "R", "b"), (43.4, 16.2, 12.8), (40.4, 15.8, "L"), (63.8, 13.4, "R"), (65.9, 11.0, 2.0, "b"),
        (65.8, 17.0, 0.0), (62.6, 25.8, 0.0), (55.0, 30.4, 0.0), (47.6, 31.6, 0.0), (43.6, 24.0, 0.0),
        (27.5, 13.0, 0.0)],
        roofs={"L": ((46.0, 0.7, 12.6), (43.4, 16.2, 12.8), (28.6, 5.2, 11.2)),
               "R": ((46.0, 0.7, 12.6), (43.4, 16.2, 12.8), (64.6, 7.2, 9.8))}, chips=0, seed=1),
    # In front of the big block's steep face: a boulder in its shadow, a lit edge down its front, its front face running
    # down to the floor.
    Boulder("under", [
        (30.6, 18.4, 5.6, "b"), (43.0, 22.2, 6.2, "b"), (37.0, 24.4, 6.6),
        (29.4, 22.4, 0.0), (29.0, 31.6, 0.0), (36.6, 34.6, 0.0), (44.0, 33.6, 0.0), (46.2, 28.6, 0.0)],
        chips=1, seed=2),
    # The middle boulder: its top, a broad face down its front, its right face in shade.
    Boulder("mid", [
        (13.6, 13.2, 7.0, "b"), (19.0, 11.6, 8.0, "b"), (27.4, 13.6, 7.6, "b"), (30.4, 17.6, 5.8, "b"),
        (15.6, 19.4, 8.8), (25.2, 19.8, 9.0),
        (12.4, 15.6, 0.0), (12.6, 21.4, 0.0), (14.8, 32.4, 0.0), (24.6, 34.2, 0.0), (29.8, 33.6, 0.0),
        (31.8, 23.6, 0.0)], chips=1, seed=3),
    # The left boulder: lit along its left and on a face at its right, dark below.
    Boulder("left", [
        (10.6, 14.2, 6.2, "b"), (15.6, 13.4, 6.4, "b"), (3.2, 17.8, 5.4, "b"), (9.2, 20.6, 7.4), (14.2, 21.2, 7.2),
        (0.6, 21.6, 0.0), (0.8, 30.6, 0.0), (4.0, 34.4, 0.0), (10.0, 35.4, 0.0), (14.6, 33.4, 0.0),
        (16.0, 24.4, 0.0), (16.2, 17.6, 0.0)], chips=1, seed=4),
    # Dark stones at the big block's right foot, lying on the floor.
    Boulder("rs_a", [
        (46.6, 23.4, 3.2, "b"), (51.6, 22.8, 3.4, "b"), (49.0, 27.0, 3.6),
        (45.4, 27.0, 0.0), (46.4, 33.6, 0.0), (50.0, 36.4, 0.0), (53.8, 33.2, 0.0), (53.6, 25.0, 0.0)],
        chips=1, seed=7),
    Boulder("rs_b", [
        (53.6, 22.0, 2.8, "b"), (58.6, 21.4, 3.0, "b"), (56.0, 26.0, 3.4),
        (52.6, 26.0, 0.0), (53.2, 33.0, 0.0), (56.6, 35.4, 0.0), (60.6, 32.4, 0.0), (61.4, 25.0, 0.0)],
        chips=1, seed=8),
]


# Low rounded stones lying on the pit's floor in front of the boulders (where the sprite draws dark stones):
# (column, row, half-width, half-depth, height), each a hull of points on a squashed dome.
COBBLES = [(19.4, 34.8, 5.6, 2.6, 1.6), (31.4, 36.2, 4.8, 2.8, 2.0), (38.8, 38.6, 3.8, 3.4, 1.9),
           (47.2, 37.4, 3.4, 2.4, 1.4), (56.8, 36.2, 3.0, 1.8, 1.1)]


def cobble(name, c, r, rx, ry, h, seed):
    """A low rounded stone: rings of points on a squashed dome (jittered, seeded), its top a little to the upper left
    (towards the light)."""
    rng = random.Random(seed)
    pts = []
    for z_f, rad_f, count in ((0.0, 1.0, 12), (0.6, 0.88, 9), (0.9, 0.6, 6)):
        for j in range(count):
            a = 2 * math.pi * (j + rng.uniform(-0.2, 0.2) + 0.5 * (z_f > 0)) / count
            f = rad_f * rng.uniform(0.9, 1.06)
            pts.append((c + math.cos(a) * rx * f, r - math.sin(a) * ry * f, h * z_f * rng.uniform(0.92, 1.05)))
    pts.append((c - 0.15 * rx, r - 0.15 * ry, h))
    return Boulder(name, pts, chips=0, seed=seed)


INTACT_PEBBLES = [(9.6, 36.8, 1.8, 0.8), (26.2, 42.4, 1.9, 0.9), (46.4, 43.0, 1.7, 0.8)]


def intact_stones():
    """The boulders and, in front of them, the cobbles and pebbles lying on the floor."""
    out = list(BOULDERS)
    for i, (c, r, rx, ry, h) in enumerate(COBBLES):
        out.append(cobble("cobble%d" % i, c, r, rx, ry, h, 60 + i))
    for i, (c, r, rad, h) in enumerate(INTACT_PEBBLES):
        out.append(cobble("stone%d" % i, c, r, rad, rad * 0.75, h, 80 + i))
    return out


# Pebbles in the pit: (column, row, radius, height), each a little boulder.
PEBBLES = [(9.6, 35.4, 1.9, 1.1), (15.0, 36.2, 1.5, 1.0), (25.8, 42.6, 1.9, 1.2), (20.0, 42.0, 1.0, 0.8),
           (46.2, 42.9, 1.8, 1.1), (50.4, 44.6, 1.4, 0.9), (62.2, 37.8, 1.4, 0.9)]


def pebbles():
    """The pebbles as boulders: hulls of a few points round each (seeded)."""
    out = []
    for i, (c, r, rad, hgt) in enumerate(PEBBLES):
        rng = random.Random(100 + i)
        pts = []
        for j in range(6):
            a = 2 * math.pi * (j + rng.uniform(-0.25, 0.25)) / 6
            f = rng.uniform(0.8, 1.1)
            pts.append((c + math.cos(a) * rad * f, r - math.sin(a) * rad * f * 0.75, 0.0))
        pts.append((c + rng.uniform(-0.3, 0.3) * rad, r - 0.2 * rad, hgt, "b"))
        pts.append((c + rng.uniform(-0.3, 0.3) * rad, r + 0.3 * rad, hgt * 0.8))
        out.append(Boulder("pebble%d" % i, pts, chips=0, seed=200 + i))
    return out


# The damaged look: the boulders blown away, in the pit (the map's) a pool of glowing blue water, a whirl (POOL_ART),
# the stones that were under the boulders in front of it (the pit's teeth, lit where the boulders shaded them), rubble
# and clods of dirt round its back.
PIT_STONES = [
    # the teeth in front of the pool
    Boulder("tooth1", [(20.4, 28.6, 3.0, "b"), (24.2, 28.2, 3.2, "b"), (22.6, 29.6, 3.4),
                       (19.8, 31.0, 0.0), (20.4, 35.6, 0.0), (23.0, 37.4, 0.0), (26.4, 36.4, 0.0), (26.6, 30.6, 0.0)],
            chips=1, seed=31),
    Boulder("tooth2", [(30.0, 31.2, 2.8, "b"), (32.6, 31.2, 3.0, "b"), (31.4, 32.4, 3.2),
                       (29.6, 33.0, 0.0), (29.8, 37.6, 0.0), (31.4, 39.0, 0.0), (33.6, 37.0, 0.0), (34.6, 33.4, 0.0)],
            chips=1, seed=32),
    Boulder("tooth3", [(35.4, 32.2, 3.6, "b"), (38.6, 32.0, 3.8, "b"), (36.4, 33.6, 4.2),
                       (34.0, 35.0, 0.0), (34.4, 40.6, 0.0), (36.2, 43.2, 0.0), (38.8, 41.0, 0.0), (40.8, 36.0, 0.0)],
            chips=1, seed=33),
    Boulder("tooth4", [(48.4, 31.6, 2.6, "b"), (51.4, 31.2, 2.6, "b"), (49.8, 32.6, 3.0),
                       (47.6, 34.0, 0.0), (48.0, 38.6, 0.0), (50.0, 39.2, 0.0), (52.6, 36.0, 0.0), (52.4, 32.6, 0.0)],
            chips=1, seed=34),
    Boulder("tooth5", [(55.2, 30.4, 1.8, "b"), (57.8, 30.2, 1.8, "b"),
                       (54.2, 32.0, 0.0), (54.6, 33.6, 0.0), (57.0, 32.8, 0.0), (58.6, 31.6, 0.0)], chips=0, seed=35),
    # rubble round the pool's back and sides
    Boulder("rub1", [(49.6, 9.4, 1.4, "b"), (52.4, 9.6, 1.2, "b"), (51.0, 10.6, 1.6),
                     (49.0, 10.6, 0.0), (49.8, 12.0, 0.0), (52.6, 12.0, 0.0), (53.6, 11.0, 0.0)], chips=0, seed=41),
    Boulder("rub2", [(15.4, 11.2, 1.0, "b"), (16.8, 11.4, 1.0, "b"),
                     (15.0, 12.4, 0.0), (16.0, 13.6, 0.0), (17.2, 12.6, 0.0)], chips=0, seed=42),
    Boulder("rub3", [(46.4, 12.6, 1.8, "b"), (49.2, 12.4, 1.6, "b"), (47.6, 13.6, 2.0),
                     (45.8, 14.0, 0.0), (46.6, 15.2, 0.0), (49.0, 15.0, 0.0), (49.8, 13.6, 0.0)], chips=0, seed=43),
    Boulder("rub4", [(40.4, 14.2, 1.6, "b"), (43.4, 14.2, 1.6, "b"), (41.8, 15.0, 2.0),
                     (40.0, 15.4, 0.0), (40.8, 16.4, 0.0), (43.2, 16.2, 0.0), (44.0, 15.0, 0.0)], chips=0, seed=44),
    Boulder("rub5", [(51.2, 13.4, 1.4, "b"), (54.4, 14.0, 1.4, "b"), (52.8, 14.8, 1.8),
                     (51.0, 15.0, 0.0), (52.0, 17.2, 0.0), (54.4, 17.0, 0.0), (55.0, 15.0, 0.0)], chips=0, seed=45),
    Boulder("rub6", [(56.8, 13.4, 1.4, "b"), (58.8, 13.6, 1.6, "b"), (59.6, 15.6, 2.0),
                     (56.6, 15.0, 0.0), (57.8, 18.6, 0.0), (60.6, 18.6, 0.0), (61.0, 16.0, 0.0)], chips=0, seed=46),
    Boulder("rub7", [(19.6, 14.2, 1.2, "b"), (21.6, 14.2, 1.2, "b"),
                     (19.0, 15.4, 0.0), (20.4, 16.8, 0.0), (22.0, 15.6, 0.0)], chips=0, seed=47),
    Boulder("rub8", [(11.8, 17.2, 1.2, "b"), (13.8, 17.2, 1.2, "b"),
                     (11.0, 18.6, 0.0), (12.4, 19.2, 0.0), (14.2, 18.6, 0.0), (15.6, 17.8, 0.0)], chips=0, seed=48),
    Boulder("rub9", [(6.4, 18.4, 1.6, "b"), (8.8, 18.2, 1.6, "b"), (7.2, 19.4, 2.0),
                     (5.8, 19.6, 0.0), (6.4, 21.2, 0.0), (8.6, 21.0, 0.0), (9.4, 19.4, 0.0)], chips=0, seed=49),
    Boulder("rub10", [(5.4, 23.2, 1.2, "b"), (7.8, 23.0, 1.2, "b"),
                      (5.0, 24.2, 0.0), (6.0, 25.2, 0.0), (8.2, 24.6, 0.0)], chips=0, seed=50),
    Boulder("rub11", [(7.2, 26.2, 1.0, "b"), (8.8, 26.2, 1.0, "b"),
                      (7.0, 27.4, 0.0), (8.0, 28.2, 0.0), (9.2, 27.4, 0.0)], chips=0, seed=51),
    Boulder("rub12", [(61.4, 22.6, 1.2, "b"), (64.4, 23.6, 1.2, "b"), (62.6, 24.2, 1.6),
                      (61.0, 24.0, 0.0), (61.6, 26.2, 0.0), (64.4, 26.0, 0.0), (65.0, 24.6, 0.0)], chips=0, seed=52),
    Boulder("rub13", [(10.6, 29.0, 1.8, "b"), (14.4, 28.6, 1.8, "b"), (12.4, 30.0, 2.2),
                      (9.4, 30.6, 0.0), (9.6, 33.0, 0.0), (12.0, 32.8, 0.0), (15.0, 30.4, 0.0)], chips=0, seed=53),
    Boulder("rub14", [(3.2, 28.2, 1.0, "b"), (6.6, 28.4, 1.0, "b"),
                      (3.0, 29.6, 0.0), (4.4, 30.4, 0.0), (7.4, 30.8, 0.0), (7.8, 29.4, 0.0)], chips=0, seed=54),
]

# Clods of dirt thrown up round the pit's back rim and right side: (column, row, radius).
CLODS = [(30.0, 3.6, 1.0), (34.6, 4.4, 1.1), (37.6, 6.4, 0.9), (43.6, 7.4, 1.0), (28.0, 8.2, 0.9), (36.2, 8.6, 1.3),
         (45.6, 8.4, 1.2), (35.0, 10.2, 1.2), (39.8, 10.4, 0.9), (29.6, 14.4, 1.0), (35.2, 15.2, 1.0),
         (37.0, 14.4, 0.9), (56.4, 17.8, 1.1), (59.8, 19.8, 0.9), (62.6, 21.4, 0.8), (63.8, 23.2, 1.0),
         (63.8, 26.6, 1.0), (67.0, 27.4, 0.8), (65.6, 28.4, 1.0), (9.8, 19.2, 0.8)]


def clods():
    out = []
    for i, (c, r, rad) in enumerate(CLODS):
        rng = random.Random(300 + i)
        pts = []
        for j in range(5):
            a = 2 * math.pi * (j + rng.uniform(-0.25, 0.25)) / 5
            f = rng.uniform(0.8, 1.15)
            pts.append((c + math.cos(a) * rad * f, r - math.sin(a) * rad * f * 0.8, 0.0))
        pts.append((c + rng.uniform(-0.3, 0.3) * rad, r, rad * rng.uniform(0.7, 1.0), "b"))
        out.append(Boulder("clod%d" % i, pts, chips=0, seed=300 + i))
    return out


def hull_points(b):
    """The boulder's points in the world (each moved TILT z down the screen from where the camera sees it); the feet
    at FOOT; under each top marked "b" a foot on the hidden back (an upright wall, leaning BACK_LEAN back)."""
    pts = []
    for p in b.points:
        c, r, z = p[0], p[1], p[2]
        top = P(c, r, z)
        pts.append(top if z > 0 else Vector((top.x, top.y, FOOT)))
        if len(p) > 3 and "b" in p[3]:
            pts.append(Vector((top.x, top.y + BACK_LEAN, FOOT)))
    return pts


def hull_planes(pts):
    """The planes (n, d: n . p <= d inside) of the faces of the points' convex hull."""
    bm = bmesh.new()
    for p in pts:
        bm.verts.new(p)
    bmesh.ops.convex_hull(bm, input=bm.verts[:])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    planes = []
    for f in sorted(bm.faces, key=lambda f: tuple(round(c, 5) for c in f.calc_center_median())):
        n = f.normal.copy()
        planes.append((n, n.dot(f.verts[0].co)))
    bm.free()
    return planes


def chip_planes(b, pts):
    """Chips off the boulder's upper corners: planes a little in from a top point, leaning outward (seeded)."""
    rng = random.Random(b.seed * 7919 + 17)
    tops = [p for p in pts if p.z > 1.0]
    centre = sum(pts, Vector()) / len(pts)
    out = []
    order = sorted(range(len(tops)), key=lambda i: rng.random())
    for i in order[:b.chips]:
        t = tops[i]
        outward = t - centre
        outward.z = 0.0
        if outward.length < 1e-6:
            continue
        outward.normalize()
        depth = rng.uniform(0.5, 1.0)
        n = (outward * rng.uniform(0.7, 1.3) + Vector((rng.uniform(-0.3, 0.3), rng.uniform(-0.3, 0.3), 1.0))).normalized()
        out.append((n, n.dot(t - n * depth)))
    return out


def solid(name, planes, mat, bottom=FOOT):
    """The convex polyhedron of the half-spaces (n, d: n . p <= d) above z = bottom (polish_asteroids.solid's)."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(160.0, 160.0, 80.0), verts=bm.verts)
    bmesh.ops.translate(bm, vec=(0.0, 0.0, 30.0), verts=bm.verts)
    for n, d in [(Vector((0.0, 0.0, -1.0)), -bottom)] + planes:
        length = n.length
        n, d = n / length, d / length
        if not bm.faces:
            break
        bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-6, plane_co=n * d,
                               plane_no=n, clear_outer=True)
        open_edges = [e for e in bm.edges if e.is_boundary]
        if open_edges:
            bmesh.ops.holes_fill(bm, edges=open_edges, sides=0)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(0.2), verts=bm.verts, edges=bm.edges)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    mesh.materials.append(mat)
    return obj


def chamfer(obj, width):
    """The boulder's edges chamfered (its feet's edges kept), so that they catch the light."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    edges = [e for e in bm.edges if min(v.co.z for v in e.verts) > FOOT + 0.05 and e.calc_face_angle(0.0) > math.radians(20)]
    tag = bm.faces.layers.int.new("chamfer")
    if edges:
        result = bmesh.ops.bevel(bm, geom=edges, offset=width, offset_type="OFFSET", segments=1, profile=0.5,
                                 affect="EDGES", clamp_overlap=True)
        for f in result["faces"]:
            f[tag] = 1
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(obj.data)
    bm.free()


def boulder_object(b, mat):
    pts = hull_points(b)
    planes = hull_planes(pts) + chip_planes(b, pts)
    obj = solid("rock_" + b.name, planes, mat)
    chamfer(obj, CHAMFER)
    return obj


CHAMFER = 0.35


# --- Painting from the picture ---------------------------------------------------------------------------------------

def visible_faces(objects, art):
    """For each of the picture's pixels the art has: the object and face the camera sees there (rays along its line of
    sight through the pixel's middle); returns {(object index, face index): [shades]}."""
    depsgraph = bpy.context.evaluated_depsgraph_get()
    trees = [BVHTree.FromObject(o, depsgraph) for o in objects]
    d = Vector((0.0, TILT, -1.0)).normalized()
    seen = {}
    for r in range(art.shape[0]):
        for c in range(art.shape[1]):
            if art[r, c] < 0:
                continue
            origin = P(c + 0.5, r + 0.5, 60.0)
            best = None
            for i, t in enumerate(trees):
                hit = t.ray_cast(origin, d)
                if hit[0] is not None and (best is None or hit[3] < best[2]):
                    best = (i, hit[2], hit[3])
            if best is not None:
                seen.setdefault((best[0], best[1]), []).append(int(art[r, c]))
    return seen


def paint_faces(objects, art, m, value_of, greys=(0x02, 0x0b)):
    """Each face one grey: value_of(the median shade of the pixels where the camera sees it (None for faces it sees
    nowhere: then their neighbours'), the face's normal, whether it is a chamfer), the hidden ones dark."""
    seen = visible_faces(objects, art)
    for i, obj in enumerate(objects):
        mesh = obj.data
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bm.faces.ensure_lookup_table()
        tag = bm.faces.layers.int.get("chamfer")
        shade = {}
        for f in bm.faces:
            s_ = seen.get((i, f.index))
            if s_ and len(s_) >= (1 if tag is None or not f[tag] else 2):
                shade[f.index] = float(np.median(s_))
        values = {}
        for f in bm.faces:
            sh = shade.get(f.index)
            if sh is None:
                near = [shade[g.index] for e in f.edges for g in e.link_faces if g.index in shade]
                sh = sum(near) / len(near) if near else None
            hidden = f.normal.dot(CAMERA) < 0.0 or f.calc_center_median().z < FOOT + 0.1
            values[f.index] = 3.0 if hidden else value_of(sh, f.normal, bool(tag is not None and f[tag]),
                                                          f.calc_center_median().z)
        bm.free()
        slots = {}
        for poly in mesh.polygons:
            index = int(max(greys[0], min(greys[1], round(values[poly.index]))))
            mat = m[index]
            if mat.name not in slots:
                slots[mat.name] = mk.slot_of(obj, mat)
            poly.material_index = slots[mat.name]
        drop_unused([obj])


def rock_value(shade, normal, chamfer, z):
    """A rock face's grey from the picture's shade where the camera sees it: LIFT lighter (the game's light reads
    palette greys darker than the sprite; less so low down, where the sprite's pit is dark: full from LIFT_FULL up),
    lighter still by COMPENSATE shades per unit of the sun it gets less than a face looking straight up (the sprite
    lights faces the game's sun turns from); chamfers facing the sun a highlight."""
    lit = max(0.0, normal.dot(LIGHT))
    lift = LIFT * (0.35 + 0.65 * mk.smoothstep(0.0, LIFT_FULL, z))
    value = (4.5 if shade is None else shade) + lift + COMPENSATE * (LIGHT.z - lit)
    if chamfer and lit > 0.6:
        value += 1.8
    return value


LIFT = 2.1
LIFT_FULL = 6.0
COMPENSATE = 1.1


def boulder_value(shade, normal, chamfer, z):
    """The intact boulders' greys: the picture's shade where the camera sees the face, up to LIFT lighter (none at the
    floor, the full lift from LIFT_FULL up: the stones lying on the floor stay as dark as the sprite's), and by ORIENT shades per unit how much more or less the face looks up than UP_REF (the game's
    light shades its faces evenly: the tops lit, the sides and fronts and the lower faces darker, as the sprite draws
    them); chamfers facing the sun a highlight."""
    lit = max(0.0, normal.dot(LIGHT))
    lift = LIFT * mk.smoothstep(0.0, LIFT_FULL, z) ** 0.8
    value = (4.5 if shade is None else shade) + lift + ORIENT * (normal.z - UP_REF)
    if chamfer and lit > 0.6:
        value += 1.8
    return value


ORIENT, UP_REF = 3.2, 0.72


def darken(objects, m, rules, lowest=0x02):
    """Darker greys where a field is low: rules [(field(obj, bmesh) -> {vertex: value}, [(threshold, shades darker)
    ...])]: the faces cut along the field's contours at the thresholds (polish_coral_manta.split_contour) and taken
    that many shades darker where the field's mean over their corners is under a threshold (the most that applies)."""
    index_of = {mat.name: i for i, mat in m.items() if isinstance(i, int)}
    for obj in objects:
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        for field, steps in rules:
            vals = field(obj, bm)
            fields = {"f": vals}
            for t, _ in sorted(steps):
                split_contour(bm, fields, "f", t)
            for f in bm.faces:
                mean = sum(vals[v] for v in f.verts) / len(f.verts)
                shift = max([n for t, n in steps if mean < t] or [0])
                if shift:
                    name = obj.data.materials[f.material_index].name
                    if name in index_of:
                        f.material_index = mk.slot_of(obj, m[max(lowest, index_of[name] - shift)])
        bm.to_mesh(obj.data)
        bm.free()
        drop_unused([obj])


def crevice_field(objects):
    """How far each point lies from the other boulders' surfaces (where boulders meet: their crevices)."""
    depsgraph = bpy.context.evaluated_depsgraph_get()
    trees = [BVHTree.FromObject(o, depsgraph) for o in objects]

    def field(obj, bm):
        others = [t for o, t in zip(objects, trees) if o is not obj]
        out = {}
        for v in bm.verts:
            best = 9.0
            for t in others:
                hit = t.find_nearest(v.co, 9.0)
                if hit[0] is not None:
                    best = min(best, hit[3])
            out[v] = best
        return out
    return field


def height_field(obj, bm):
    return {v: v.co.z for v in bm.verts}


CREVICE = [(0.6, 3), (1.3, 1)]       # within this far of another boulder: this many shades darker
GROUNDED = [(0.6, 1)]                # this low over the ground: darker (the pit's shadow)


# --- The pool ---------------------------------------------------------------------------------------------------

POOL_CENTRE = (35.6, 23.4)     # where the camera sees the pool's middle (picture)
POOL_Z = (0.25, 1.05)          # its water's height at the middle and at the rim: a shallow whirl
POOL_ELLIPSE = (25.6, 6.6)     # how far it reaches down the screen at most: an ellipse's half-axes
POOL_RINGS, POOL_SEGMENTS = 16, 144
POOL_BANDS = [(-99.0, 0x91, 0.1), (1.5, 0x93, 0.16), (4.0, 0x96, 0.24), (7.0, 0x99, 0.34), (10.0, 0x9c, 0.46),
              (12.5, 0x9e, 0.6)]    # (lowest shade of POOL_ART, palette index, emission strength)


def pool_outline():
    """How far the pool's pixels reach from its middle in each of POOL_SEGMENTS directions (picture pixels, rays in
    steps of a quarter pixel, the last pixel's far edge), smoothed round the outline."""
    mask = load_art(POOL_ART) >= 0
    cx, cy = POOL_CENTRE
    reach = []
    for j in range(POOL_SEGMENTS):
        a = 2 * math.pi * j / POOL_SEGMENTS
        dx, dy = math.cos(a), -math.sin(a)
        t, last = 0.0, 0.0
        while t < 40.0:
            c, r = cx + dx * t, cy + dy * t
            if 0 <= int(r) < mask.shape[0] and 0 <= int(c) < mask.shape[1] and mask[int(r), int(c)]:
                last = t
            t += 0.25
        if dy > 0:  # down the screen: no further than the ellipse (the dark pixels under its middle are the teeth's)
            ex, ey = POOL_ELLIPSE
            last = min(last, 1.0 / math.sqrt((dx / ex) ** 2 + (dy / ey) ** 2))
        reach.append(last + 0.35)
    smooth = []
    for j in range(POOL_SEGMENTS):
        smooth.append(sum(reach[(j + d) % POOL_SEGMENTS] for d in range(-3, 4)) / 7.0)
    return smooth


def pool_object(m):
    """The pool: rings from its middle out to its outline, the water's height rising from POOL_Z's middle to its rim
    (where the camera sees each point: moved TILT z down the screen), a wall down to the feet and a flat underside;
    painted by POOL_ART's shades (blurred), banded into glowing blues."""
    reach = pool_outline()
    cx, cy = POOL_CENTRE
    zc, zr = POOL_Z
    verts, faces = [P(cx, cy, zc)], []
    rings = []
    for kk in range(1, POOL_RINGS + 1):
        f = kk / POOL_RINGS
        z = zc + (zr - zc) * f ** 2
        ring = []
        for j in range(POOL_SEGMENTS):
            a = 2 * math.pi * j / POOL_SEGMENTS
            c, r = cx + math.cos(a) * reach[j] * f, cy - math.sin(a) * reach[j] * f
            ring.append(len(verts))
            verts.append(P(c, r, z))
        rings.append(ring)
    n = POOL_SEGMENTS
    for j in range(n):
        faces.append((0, rings[0][j], rings[0][(j + 1) % n]))
    for a_, b_ in zip(rings, rings[1:]):
        for j in range(n):
            faces.append((a_[j], b_[j], b_[(j + 1) % n], a_[(j + 1) % n]))
    foot = []
    for j in range(n):
        v = verts[rings[-1][j]]
        foot.append(len(verts))
        verts.append(Vector((v.x, v.y + TILT * zr, FOOT)))
    for j in range(n):
        faces.append((rings[-1][j], foot[j], foot[(j + 1) % n], rings[-1][(j + 1) % n]))
    faces.append(tuple(reversed(foot)))
    obj = k.mesh_object("pool", verts, faces, m["pool"][0])
    k.recalc_normals(obj)
    sample = blurred(load_art(POOL_ART), 0.7)
    values = []
    for v in obj.data.vertices:
        if v.co.z < zc - 0.05:
            values.append(-99.0)
            continue
        c, r = picture(v.co)
        sh = sample(c, r)
        values.append(0.0 if sh is None else sh)
    band_split(obj, values, [(lo, mat) for (lo, _, _), mat in zip(POOL_BANDS, m["pool"])])
    return obj


def blurred(art, sigma):
    """The art's shades blurred (a gaussian sigma pixels wide), only its own pixels counted (normalized convolution):
    a function of picture positions (column, row of pixel corners) -> shade (None where it has no pixels near)."""
    radius = int(math.ceil(2.5 * sigma))
    xs = np.arange(-radius, radius + 1)
    g = np.exp(-0.5 * (xs / sigma) ** 2)
    g /= g.sum()
    have = (art >= 0).astype(float)
    vals = np.where(art >= 0, art, 0).astype(float)

    def conv(a):
        a = np.pad(a, radius)
        a = np.apply_along_axis(lambda row: np.convolve(row, g, mode="valid"), 0, a)
        return np.apply_along_axis(lambda row: np.convolve(row, g, mode="valid"), 1, a)
    num, den = conv(vals * have), conv(have)
    hgt, wid = art.shape

    def sample(c, r):
        x, y = c - 0.5, r - 0.5
        x0, y0 = int(math.floor(x)), int(math.floor(y))
        fx, fy = x - x0, y - y0
        acc_n = acc_d = 0.0
        for dy, wy in ((0, 1 - fy), (1, fy)):
            for dx, wx in ((0, 1 - fx), (1, fx)):
                yy, xx = min(max(y0 + dy, 0), hgt - 1), min(max(x0 + dx, 0), wid - 1)
                acc_n += wy * wx * num[yy, xx]
                acc_d += wy * wx * den[yy, xx]
        return acc_n / acc_d if acc_d > 0.05 else None
    return sample


# --- Whole -------------------------------------------------------------------------------------------------------

def materials():
    def grey(i):
        return k.material("pit_rock", palette=i, metallic=0.0, roughness=0.62)
    m = {i: grey(i) for i in range(0x02, 0x0c)}
    m["cap"] = k.material("pit_rock_inside", palette=0x04, metallic=0.0, roughness=0.7)
    m["clod"] = k.material("pit_clod", palette=0xa3, metallic=0.0, roughness=0.8)
    pal = k.level_palette()
    m["pool"] = [k.material("pit_pool", palette=i, metallic=0.0, roughness=0.12, emission=pal[i], emission_strength=e)
                 for _, i, e in POOL_BANDS]
    return m


def build_look(m, damaged):
    """The whole of a look: its stones (painted from its picture), and when damaged the pool and the clods."""
    if not damaged:
        specs, art, greys, value = intact_stones(), load_art(ROCKS_ART), (0x02, 0x0b), boulder_value
    else:
        specs, art, greys, value = PIT_STONES + pebbles(), load_art(PIT_ART), (0x03, 0x09), rock_value
    objs = [boulder_object(b, m[0x06]) for b in specs]
    paint_faces(objs, art, m, value, greys)
    for i, obj in enumerate(objs):
        pa.roughen(obj, spacing=1.0, amount=0.08, seed=i + 1)
    darken(objs, m, [(crevice_field(objs), CREVICE), (height_field, GROUNDED)], greys[0])
    if damaged:
        for b in clods():
            obj = boulder_object(b, m["clod"])
            pa.roughen(obj, spacing=1.0, amount=0.06, seed=7)
            objs.append(obj)
        objs.append(pool_object(m))
    for obj in objs:
        k.smooth(obj, 25.0)
    return objs


LOOKS = [("intact", ["holes_rocks_tl", "holes_rocks_tm", "holes_rocks_tr", "holes_rocks_bl", "holes_rocks_bm",
                     "holes_rocks_br"], [1, 3, 5, 39, 41, 43]),
         ("damaged", ["holes_rocks_tl_damaged", "holes_rocks_tm_damaged", "holes_rocks_tr_damaged",
                      "holes_rocks_bl_damaged", "holes_rocks_bm_damaged", "holes_rocks_br_damaged"],
          [7, 9, 11, 45, 47, 49])]
BOXES = [(-36.0, -12.0, 0.0, 28.0), (-12.0, 12.0, 0.0, 28.0), (12.0, 36.0, 0.0, 28.0),
         (-36.0, -12.0, -28.0, 0.0), (-12.0, 12.0, -28.0, 0.0), (12.0, 36.0, -28.0, 0.0)]


def art_mask(*arts):
    return [[any(bool(a[r, c] >= 0) for a in arts) for c in range(W)] for r in range(H)]


def build():
    options = k.args()
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    looks = options.get("looks", "intact,damaged").split(",")
    for label, names, sprites in LOOKS:
        if label not in looks or (only and not any(n in only for n in names) and "whole" not in options):
            continue
        k.reset()
        bpy.context.scene.view_settings.view_transform = "Standard"
        m = materials()
        damaged = label == "damaged"
        objs = build_look(m, damaged)
        triangulate(objs)
        arts = (load_art(PIT_ART), load_art(POOL_ART), load_art(CLOD_ART)) if damaged else (load_art(ROCKS_ART),)
        print("pit rocks %s whole: %d triangles" % (label, mk.triangles(objs)))
        if "check" in options:
            mk.compare("whole (%s) as the camera sees it" % label, view_coverage(objs, W, H), art_mask(*arts))
        if "whole" in options:
            mk.export(objs, options["whole"] + ("holes_rocks_damaged.glb" if damaged else "holes_rocks.glb"))
        if "preview" in options:
            mk.preview(options["preview"] + ("holes_rocks_damaged" if damaged else "holes_rocks"), objs, size=(W, H),
                       scale=8)
        for name, sprite, box in zip(names, sprites, BOXES):
            if only and name not in only:
                continue
            open_box = tuple(None if abs(v) > 30.0 else v for v in box)
            parts = [p for p in (view_cut(o, open_box, m["cap"]) for o in objs) if p is not None]
            centre = Vector(((box[0] + box[1]) / 2, (box[2] + box[3]) / 2, 0.0))
            mk.transform(parts, Matrix.Translation(-centre))
            bpy.context.view_layer.update()
            drop_unused(parts)
            triangulate(parts)
            piece = join(parts, name)
            piece.data.name = name
            for o in objs:
                o.hide_render = True
            if "check" in options:
                c0, r0 = int(box[0] + 36), int(28 - box[3])
                sub = [row[c0:c0 + 24] for row in art_mask(*arts)[r0:r0 + 28]]
                mk.compare("%s (E %d) as the camera sees it" % (name, sprite), view_coverage([piece], 24, 28), sub)
            mk.report(name, [piece], os.path.join(out, name + ".glb"))
            if "preview" in options:
                mk.preview(options["preview"] + name, [piece])
            data = piece.data
            bpy.data.objects.remove(piece)
            if data.users == 0:
                bpy.data.meshes.remove(data)
            for o in objs:
                o.hide_render = False


if __name__ == "__main__":
    build()
