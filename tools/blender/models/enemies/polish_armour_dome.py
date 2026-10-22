"""The armoured dome of the asteroid levels, polished (2026-10-22, round 32; it replaces wave3_ah_dome.py's shell and
wreck and wave3_at_m.py's gun port frames). One 72 x 56 picture that the game puts together from six 2x2 sprites of
sheet M: 45 47 49 above 83 85 87 (models armour_dome_tl, _tm, _tr, _bl, _bm, _br); the gun port's frames 7 9 11 of the
lower middle piece (armour_dome_7, _9, _11; armour_dome_85 the port shut, as armour_dome_bm); its wreck 39 41 43 above
77 79 81 (armour_dome_wreck_tl ... _br).

PLACEMENT AND WHAT IT IS (the level events, tools/content/tyrdata.py's enemy data)

Six enemies, 536-541 in episodes 1-3, 1082-1087 in episode 5 (the same data): armour 100 and worth 100 each, one frame
but the lower middle's; 539 (M 83) and 541 (M 87) fire (weapons 116, 115) and launch the darts D 171 every 60 ticks
(enemies 543, 544: polish_launched_darts.py), 540 (M 85) fires weapon 154 every 120 ticks and plays 85 7 9 11 9 9 7 7 85
when it does (animate 2): the doors of its gun band slide apart on a fire. Each piece's damaged look is its wreck (dgr
39 41 43 77 79 81, dlevel -1): one shot down, all six (one link) switch to their wrecks and stay. The levels place it by
event 6 (ground): 536 at (x, y - 28), 537 (x + 24, y - 28), 538 (x + 48, y - 28), 539 (x, y), 540 (x + 24, y), 541
(x + 48, y): the picture whole, on the woven stone floor (map tile 372; the sprites carry it, a shade darker round the
shell: its shadow; the floor is the map's, not modelled).
- ASTEROID1 t7552 (x 144, link 69): with event 79 (the boss bar on link 69): the level's last foe.
- AST ROCK (episode 5) t6292 (x 144, link 254, event 57: 6400, event 79 on 254): the level's boss: shot down, every
  enemy on the screen goes with it and the level jumps to its end (t6400).
- AST. CITY (episode 3) t1336 (x 138), t3548 (210), t5172 (66), t6712 (66): four domes, the top middle piece first on
  link 95, which event 33 gives enemy 476 to leave (coins 245, a gem worth 800, drifting down) before event 39 joins it
  to the others' link 5: shot down, the dome leaves that gem where its top middle piece was.
- TYRIAN X (episode 3) t3253: event 33 names 536 (the top left piece) as what the link-6 enemies (the U-ship of t3058)
  leave (TYRIAN has 534 there, an item); TYRIAN X never loads sheet M (its shape banks 2, 4, E), so the game would
  draw sprite 45 of the slot's last sheet: a quirk of the data (the catalogue's "drop"), never the dome.
- No episode 6 level places it. No other enemy shows these sprites (catalog.json, launched ones too) and none is
  another sprite's pixels mirrored, turned or in other ramps: the frame lines are its own, no twins. The asteroid
  levels' terrain is flat with holes (tools/terrain/levels.json) and ASTEROID1's background 2 is empty: height=-4 sets
  the dome on the floor, 13.5 high (16.7 at the capsule).

THE DOME (as the sprites and their 4x upscales draw it; columns and rows of the picture)

A low steel shell (ramp 6) on the floor, its outline an ellipse (columns 6-66, rows 2-51), lit from the upper left,
dark at its rim; on it a raised red housing (ramp 4), a U whose pillars run from the back rim (columns 24-28 and 45-48)
down to its bottom bar (rows 22-28), the left pillar's outer edge lit orange (ramp 7) and thin at rows 10-15 where the
recess between the pillars widens; in the recess a red capsule (columns 33-40, rows 4-16), its rounded tip up the
screen, an orange streak down its upper left, on a grey rounded mount narrowing to the bar; light ridges curving from
the housing down to the rim either side, a small dark port in a bezel above each (17, 14), (56, 13), a large bronze
lens in a grey bezel below each (16.6, 34.6), (56, 35); red armour on the lower flanks round the rim, short red bars
beside the front; at the front, between seams down columns 23 and 49, a plate, the recessed gun band (rows 34-45: its
doors meeting at the seam down column 36.5, the lower half darker) and the lower plate, lit along its top edge; four
rivets at the right of the housing (51-53, 21-27).

Built as the game's camera sees it (20 degrees from straight down): one surface over the picture (a grid GRID apart,
cut along every part's outline and its inset (polish_coral_manta.split_contour) so that the steps are sharp, its
heights heights(): the shell (HEIGHT, its rim an upright SKIRT), the housing (HOUSING_H, crowned), the recess, the mount,
the flanks and bars, the band (BAND_D deep), the lower plate, grooves along the seams, beads along the ridges, the
rivets, the ports' sockets and the bezels), its underside flat at FOOT; every point then moved TILT z down the screen
(to_world), so that the camera sees each where the sprite draws it. The capsule (a cylinder with a rounded tip) and the
lenses (glassy caps) are built the same way. Painted by its parts (regions()): the steel and the red in bands of the
sprite's shades there (blurred SHADE_BLUR; STEEL_BANDS 0x66 0x6a 0x6d, RED_BANDS 0x45 0x48 0x4c), the faces cut along
their contours; the recess, the band and the rim darker, the bezels and the lower plate's edge lit; the orange edge
0x78 glowing 0.22, the capsule 0x48 (glass, glowing 0.12) and its streak 0x7a (0.35), the lenses bronze 0xa6/0xaa, the
ports dark bronze 0xa3.

The gun port's frames (FIRE_ART): the doors drawn back to the frame's slot (SLOT_X: 6, 13 and 17 pixels wide), the
slot SLOT_D deep and dark (0x61), in it the fire: a heap over the frame's fire pixels, painted by their shades in
glowing FIRE_BANDS (0x74 to 0x7d, 0.3 to 0.6). Only the lower middle piece is cut from these wholes.

The wreck: the same surface dented (DENT deep where the wreck's steel is burnt darkest), painted from the wreck's
sprites: the burnt steel in WRECK_BANDS (0x63 to 0x6d; the flanks' armour burnt to steel too), the housing scorched tan
in TAN_BANDS (ramp 10: 0xa5 0xa8 0xab), the capsule scorched (0xa7) with a crack down its middle and an ember in it
(0x76 glowing 0.4), the lenses smashed (their sockets dark), the ports dark.

Each look is built whole and cut along the planes the camera sees as the sprites' edges (polish_stone_face.view_cut:
x = -12 and 12 upright, y = 0 leaning back up the screen; the caps the inside's grey, the uncut dome's shading), each
piece moved so that its sprite's centre is its origin, every mesh triangulated (polish_k_pod.triangulate).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the floor; the whole's origin
is the picture's centre (pixel corner 36, 28). The pieces' centres: tl (-24, 14), tm (0, 14), tr (24, 14), bl (-24,
-14), bm (0, -14), br (24, -14).

models.cfg: the model lines stay; the sprite lines of M 45 47 49 83 85 87 and 39 41 43 77 79 81 get height=-4; the frame
lines (m 85, 7, 9, 11) stay. Replaces wave3_ah_dome.py (all of it), wave3_at_m.py's gun port section and the pixels
only they read: wave3_ah_art.py's DOME and WRECK (and its DOME_FIRE, which nothing reads).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes as the game's
camera sees them, of the intact and the wreck's wholes and of each piece, against the sprites' own pixels in
enemy_M.png / .idx, the floor's ramp 0 left out), --preview <prefix> (each piece's top and 3/4 views, each look's whole),
--whole <prefix> (each look's uncut whole as <prefix>armour_dome_<look>_<frame>.glb), --only <model,...>.
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
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_coral_manta import split_contour  # noqa: E402
from polish_deli_boss import join, drop_unused  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_stone_face import view_cut, view_coverage  # noqa: E402

TILT = math.tan(math.radians(20.0))
W, H = 72, 56
FOOT = -0.5                    # the shell's foot, a little under the floor


def sstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


# --- The pictures (the shades of the sprites' ramps: 6 the steel, 4 the red; '.' elsewhere) -----------------------

DOME_STEEL = [
    "........................................................................",
    "........................................................................",
    "..............................6556666666533.............................",
    "..........................0.1a9998666668999833..........................",
    ".......................2.....db986.....689995...23......................",
    ".....................5b8.....d765.......46795....861....................",
    "...................6ace7.....8544........3565....a9743..................",
    ".................39bdcc8....65334........1354....a899632................",
    "................59b999a8...753264........3533....b6779853...............",
    "...............6989999b8...624465........3625....b55677842..............",
    "..............58999a8bc9...436565........3737....c4458a9963.............",
    ".............5779657bceb...547565........4747....d557a7.6963............",
    "............5679...5cefc...647565........4757....d668a....964...........",
    "...........46796...6cefc...647565........4757....e67896...6944..........",
    "..........3787a....cabfc...857575........5757....e67889...6a854.........",
    ".........46878a...cabceb....775765......5575.....e678989..8c8763........",
    ".........588789bcc9abcca.....86749adba88346......e678a879ab77874........",
    "........2897899999aaaaa8......975555554327.......8345676576678864.......",
    "........399789aaa9787778........757997433........ddcba75445567975.......",
    ".......27988aba878abccc7.........79ab8633........d79bccba84467a955......",
    ".......3999bb967bccbbab6.........79ac963.........c768999aba8458a76......",
    ".......5aaca66accbaabca66........689b862........5c7ada86457aa75a86......",
    "......37bd758bcbaaa99985ada996...678a764....9bccab89687744568a75966.....",
    "......39d857ba9aaabcdb86ebaaa7....6797556...89ab9b869d98445668a8566.....",
    "......39848a9999a989bb87daaaa8.....69756....89ab8b6a77a944566789845.....",
    "......4536988999abcea778caaaa9..............79ab7b669ada74567789965.....",
    "......435887889978abb898caaaa9..............8aba6b68a99864567789886.....",
    "......45877778887bfc78a8baaaa97.............8ac95a689bd985567789867.....",
    "......465667788789bc89a8baaaa965....4......6abb74a66aa8465677788433.....",
    "......355567778aaaa86aa8aaa99987766627666679bc964a6689aa99677887........",
    "......22246678b8...a7797a99999988888397778aad9754a669b735897787.........",
    "......2..2567a8....7a797a999988888873c789abe97544a67b74...8978..........",
    "..........3669.....4a6869888888887772b89abe975454a68a4.....a87..........",
    "..........3469......a686988888877777289abd9754555745a......a76..........",
    "..........3239......9..31334455555541444444323333...9......b5...........",
    "...........349......9..32445666666651444453233343...9......b............",
    "............498.....a..346777777789a3876644555554...9......b............",
    ".............79.....b..4567777899aaa4a65445556654...9.....c.............",
    "..............798..c8..467999abcba871944455667754....a...d..............",
    "................9bb....13566667777541944556677654.....abc...............",
    ".......................02344444444441855566666655.......................",
    ".......................13455555555552856666666655.......................",
    ".......................23566666666663866667777655.......................",
    ".......................14677777777763877777776555.......................",
    ".......................33466666666651445555555565.......................",
    ".......................6bbbbbbbbbcd74ebbbaaaa9986.......................",
    ".......................5a999999999b85b99999999986.......................",
    ".......................59889999999a73899999999876.......................",
    ".......................36888889999963799999988665.......................",
    ".......................02567777777752577777775443.......................",
    "..........................123444666402555555421.........................",
    "..............................0024320133321.............................",
    "........................................................................",
    "........................................................................",
    "........................................................................",
    "........................................................................",
]
DOME_RED = [
    "........................................................................",
    "........................................................................",
    "........................................................................",
    "...........................1..................2.........................",
    "........................44554.....56765......336........................",
    "........................75554....3698655.....4483.......................",
    "........................b5554....57.a5445....55a3.......................",
    "........................d666.....57.65335....55c2.......................",
    "........................e88......45.54334....45d2.......................",
    "........................e96......46.75334....37c2.......................",
    ".........................a5......47.85334....37a3.......................",
    ".........................a5......58.85334....3893.......................",
    "..........................5......58.75325....3894.......................",
    "..........................6......45655325....4784.......................",
    "..........................9......35553235....6765.......................",
    ".........................a89......354333....78675.......................",
    ".........................9889..............585686.......................",
    ".........................87789............6855585.......................",
    ".........................7667888.........56544685.......................",
    ".........................77777775........55455884.......................",
    "........................677777665.......255778963.......................",
    ".........................45543765.......25533433........................",
    "..............................765.......3554............................",
    "..............................9653.......563............................",
    "..............................a6653.....5463............................",
    "..............................a7765353455563............................",
    "...............................8776655666673............................",
    "...............................4444333333333............................",
    "................................3333.333333.............................",
    "................................................................322.....",
    "...............................................................3433.....",
    ".......22......................................................343......",
    ".......232....................................................3343......",
    ".......232....................................................3433......",
    "........33...........87..........................987.........3543.......",
    "........333..........77..........................856........45533.......",
    ".........333.........66..........................645........75431.......",
    ".........3333........56..........................535.......86532........",
    ".........13433.......44..........................5346.....a75431........",
    "..........144334...4.............................54447...a86432.........",
    "...........144433443333..........................5445567897533..........",
    "............04444333333..........................545556797532...........",
    ".............1444444333..........................55556797533............",
    "..............144554444..........................5556797433.............",
    "...............13455555..........................556785432..............",
    "................0245555..........................56765331...............",
    ".................023455..........................4554330................",
    "...................0234..........................3333...................",
    ".....................02..........................222....................",
    ".................................................0......................",
    "........................................................................",
    "........................................................................",
    "........................................................................",
    "........................................................................",
    "........................................................................",
    "........................................................................",
]
WRECK_STEEL = [
    "........................................................................",
    "........................................................................",
    "..............................6666666666655.............................",
    "..........................44399998666668999843..........................",
    ".......................4.....bb986.....689996...25......................",
    ".....................565.....b765.......46796...5865....................",
    "...................57884.....7544........3566...5a9855..................",
    ".................3678873....65334........1354...4bba9644................",
    "................45988844...753264........35337..47647a853...............",
    "...............5625a9557...624465........36377..4ba636a844..............",
    "..............67413656a9...436565.........7584..5c677578565.............",
    ".............576400268db...547565.........a324..5d56774347a5............",
    "............23350000bcec...647565.4.......3222...d66850000675...........",
    "...........32140011b9dfc...647565.........3154...e644300000755..........",
    "..........45202053099bfc...857575........3345....e3012300009865.........",
    ".........454002370359ceb....77576.......5335.....e424ab5004ba875........",
    ".........463003c7715acca.....86749....88346......e658ab534526765........",
    "........4562008966679aa8......975555554327.......83456963545ab865.......",
    "........3663016889677778........757997433........ddcba7544558c976.......",
    ".......34552235778abccc7.........79ab8633........d79bccba8446aa966......",
    ".......455534657bccbbab6.........79ac9633........c768999aba8458876......",
    ".......5532356accbaabca5578876...689b8624..5676..c7ada86457aa75666......",
    "......4663448bcbaaa999736ca996..9678a764...67accab89687744568a74544.....",
    "......566557ba9aaabcdb83859aa7..96679755...2147a8b869d98445668a7255.....",
    "......56648a8799a989bb84002698...866975....100344a6a77a943458789834.....",
    "......55369745799acea773000138....86857....3020009669ada5123a789965.....",
    "......43587554764babb894112014.dc..........434300968a9973023a889786.....",
    "......45864557620cfc78a745310127777666666665366008689bd63033aa86657.....",
    "......46543478a31dbc89aba840000255533544454467820866ad4000345744456.....",
    "......35421367ad6fa86aa84591202463330533445458830965c40004313334666.....",
    "......56410157a9327a6695356c885511452843576576621953840014310125865.....",
    "......46500168633236748555b8643111573b53536757322a32920210012359a64.....",
    ".......563022635323262757b74510134772a6556867423481160243002349b76......",
    ".......57851254424616278b6442002765505666667532444015045330228b965......",
    ".......467a30752485262630100000640000010003322021503715654141c9864......",
    "........56690653b622715321001215330000000222320224039145443849866.......",
    "........46670551530292633200031344320043002244112403901344b847665.......",
    ".........56713523006a2644310000032210671000124101503a1012ba76556........",
    ".........5663210103b625454710101130008230000462027257a3028886455........",
    "..........66420002a51131344000000001272021126500284458944598445.........",
    "...........6564103532350231000000001130105a8411049545741288634..........",
    "............45644233355133100101100311024a6421124976542167632...........",
    ".............343135b87623300011000000115a6643122498752169854............",
    "..............4324a7777133112332200002676441102249897358765.............",
    "...............55c988883223443214540034543000135599a973665..............",
    "................677788958aaa74248cd72daaa533689868aba6565...............",
    ".................57778834577522289b848653135999867987653................",
    "...................577721026776779a7241001499987656664..................",
    ".....................5732346889787850000039988665555....................",
    ".......................356677777554200004777765555......................",
    "..........................455666655300156666654.........................",
    "..............................4566541146654.............................",
    "........................................................................",
    "........................................................................",
    "........................................................................",
    "........................................................................",
]


WRECK_BRONZE = [
    "........................................................................",
    "........................................................................",
    "........................................................................",
    "..............................................3.........................",
    "........................76777.....78987......555........................",
    "........................77777.....8c9877.....777........................",
    "........................87777....78d87667....777........................",
    "........................8788.....68d.6557....777........................",
    "........................98.......36..55.5.....77........................",
    ".........................98......2...54.3.....87........................",
    "........................d.7......1...74.13....87........................",
    ".........................c7.......2.c75.1.....97........................",
    ".........................d7......2.b975.1.....876.......................",
    ".........................d7......558775.4......86.......................",
    ".........................d9......57775..7....8.87.......................",
    ".........................c.9......576555....9c887.......................",
    "..........................999.....8c98.....7c7888.......................",
    "........................d99889............8c77797.......................",
    "........................d9888899.........78766797.......................",
    "........................d99998897........77677896.......................",
    "........................9c...9887........77889975.......................",
    "..............................987........77....5........................",
    "..............................98.........77.............................",
    "...............................8........577.............................",
    "..............................c88......5767.............................",
    "..............................c887.....7778.............................",
    "..............................d..9887788889.............................",
    "........................................................................",
    "........................................................................",
    "........................................................................",
    "........................................................................",
    "........................................................................",
    "........................................................................",
    "........................................................................",
    "........................................................................",
    "........................................................................",
    "........................................................................",
    "........................................................................",
    "........................................................................",
    "........................................................................",
    "........................................................................",
    "........................................................................",
    "........................................................................",
    "........................................................................",
    "........................................................................",
    "........................................................................",
    "........................................................................",
    "........................................................................",
    "........................................................................",
    "........................................................................",
    "........................................................................",
    "........................................................................",
    "........................................................................",
    "........................................................................",
    "........................................................................",
    "........................................................................",
]

# The gun port's fire in frames 7, 9 and 11 (ramp 7's shades, '.' elsewhere): rows 34-44 of the picture, its
# columns 24-47 (the lower middle sprite's).
FIRE_ART = {
    7: [
        "........................",
        "........................",
        "............2...........",
        "...........551..........",
        "..........4662..........",
        "..........6893..........",
        "..........7983..........",
        "..........4440..........",
        "...........10...........",
        "........................",
        "........................",
    ],
    9: [
        "........................",
        "........................",
        "...........443..........",
        ".........665774.........",
        "........379ac962........",
        "........37deb863........",
        "........47bba883........",
        "........55779973........",
        ".........334553.........",
        "........................",
        "........................",
    ],
    11: [
        "........................",
        "...........0............",
        ".........321123.........",
        "........655765455.......",
        ".......667acea3354......",
        ".......579adec4286......",
        ".......37a779847b9......",
        "........5674568bb.......",
        ".........55657aa........",
        "...........4456.........",
        "........................",
    ],
}


def load_art(rows):
    a = np.full((len(rows), len(rows[0])), -1, int)
    for r, line in enumerate(rows):
        for c, ch in enumerate(line):
            if ch != ".":
                a[r, c] = int(ch, 16)
    return a


def blurred(art, sigma):
    """The art's shades blurred (a gaussian sigma pixels wide), only its own pixels counted (normalized convolution),
    sampled at arrays of picture positions (columns, rows of pixel corners); nan where it has no pixels near."""
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
        x, y = np.asarray(c, float) - 0.5, np.asarray(r, float) - 0.5
        x0, y0 = np.floor(x).astype(int), np.floor(y).astype(int)
        fx, fy = x - x0, y - y0
        acc_n = np.zeros(len(x))
        acc_d = np.zeros(len(x))
        for dy, wy in ((0, 1 - fy), (1, fy)):
            for dx, wx in ((0, 1 - fx), (1, fx)):
                yy, xx = np.clip(y0 + dy, 0, hgt - 1), np.clip(x0 + dx, 0, wid - 1)
                acc_n += wy * wx * num[yy, xx]
                acc_d += wy * wx * den[yy, xx]
        return np.where(acc_d > 0.05, acc_n / np.maximum(acc_d, 1e-9), np.nan)
    return sample


# --- Shapes in the picture ------------------------------------------------------------------------------------------

class Poly:
    """A polygon of the picture (pixel corners): signed distances (positive inside) for arrays of points."""

    def __init__(self, pts):
        self.p = np.array(pts, float)

    def signed(self, x, y):
        x, y = np.atleast_1d(np.asarray(x, float)), np.atleast_1d(np.asarray(y, float))
        a, b = self.p, np.roll(self.p, -1, axis=0)
        dx, dy = b[:, 0] - a[:, 0], b[:, 1] - a[:, 1]
        ll = np.maximum(dx * dx + dy * dy, 1e-12)
        out = np.empty(len(x))
        for s in range(0, len(x), 4096):
            px, py = x[s:s + 4096, None], y[s:s + 4096, None]
            t = np.clip(((px - a[:, 0]) * dx + (py - a[:, 1]) * dy) / ll, 0.0, 1.0)
            d = np.sqrt(((px - a[:, 0] - t * dx) ** 2 + (py - a[:, 1] - t * dy) ** 2).min(axis=1))
            cond = (a[:, 1] > py) != (b[:, 1] > py)
            den = np.where(b[:, 1] != a[:, 1], b[:, 1] - a[:, 1], 1e-12)
            xint = a[:, 0] + (py - a[:, 1]) * (b[:, 0] - a[:, 0]) / den
            inside = (cond & (px < xint)).sum(axis=1) % 2 == 1
            out[s:s + 4096] = np.where(inside, d, -d)
        return out


class Ellipse:
    def __init__(self, c, r, rx, ry):
        self.c, self.r, self.rx, self.ry = c, r, rx, ry

    def signed(self, x, y):
        """About the distance inside the ellipse (its radius times one less the normalised radius)."""
        x, y = np.asarray(x, float), np.asarray(y, float)
        u, v = (x - self.c) / self.rx, (y - self.r) / self.ry
        rho = np.sqrt(u * u + v * v)
        scale = np.sqrt((u * self.rx) ** 2 + (v * self.ry) ** 2) / np.maximum(rho, 1e-9)
        return (1.0 - rho) * np.where(rho > 1e-9, scale, min(self.rx, self.ry))


class Line:
    """A polyline: distances to it."""

    def __init__(self, pts):
        self.p = np.array(pts, float)

    def distance(self, x, y):
        x, y = np.atleast_1d(np.asarray(x, float)), np.atleast_1d(np.asarray(y, float))
        a, b = self.p[:-1], self.p[1:]
        dx, dy = b[:, 0] - a[:, 0], b[:, 1] - a[:, 1]
        ll = np.maximum(dx * dx + dy * dy, 1e-12)
        px, py = x[:, None], y[:, None]
        t = np.clip(((px - a[:, 0]) * dx + (py - a[:, 1]) * dy) / ll, 0.0, 1.0)
        return np.sqrt(((px - a[:, 0] - t * dx) ** 2 + (py - a[:, 1] - t * dy) ** 2).min(axis=1))


CX, CY, RX, RY = 36.5, 27.0, 30.5, 25.0      # the shell's outline (columns 6-66, rows 2-51)
SHELL = Ellipse(CX, CY, RX, RY)
HEIGHT = 13.5                                 # the shell's top over the floor
SKIRT = 0.9                                   # the rim's upright band

# The red housing: two pillars from the shell's back rim, the left one thin at rows 10-15 (where the recess the
# capsule lies in widens), joined below the capsule's mount by the U's bottom bar.
HOUSING = Poly([(24.0, 2.0), (29.0, 2.0), (29.0, 9.8), (27.0, 9.8), (27.0, 15.8), (29.0, 16.0), (30.6, 17.0),
                (32.0, 18.0), (33.0, 19.6), (33.0, 25.0), (40.0, 25.0), (40.0, 19.6), (41.0, 18.0), (42.0, 17.0),
                (43.2, 16.0), (45.0, 15.8), (45.0, 2.0), (49.0, 2.0), (49.0, 21.8), (44.0, 22.0), (44.0, 28.0),
                (43.0, 29.0), (32.0, 29.0), (31.0, 28.0), (30.0, 26.0), (30.0, 22.0), (24.0, 21.8)])
HOUSING_H = 2.6
CROWN = 0.7            # the housing's top rounded: this much higher in its middle
RECESS = Poly([(29.0, 2.0), (45.0, 2.0), (45.0, 15.8), (43.2, 16.0), (40.0, 19.6), (40.0, 25.0), (33.0, 25.0),
               (33.0, 19.6), (29.0, 16.0), (27.0, 15.8), (27.0, 9.8), (29.0, 9.8)])
RECESS_D = 0.7
MOUNT = Poly([(33.4, 15.6), (40.6, 15.6), (40.2, 18.0), (39.6, 20.0), (39.6, 25.0), (33.4, 25.0), (33.4, 20.0),
              (32.8, 18.0)])
MOUNT_H = 2.4
GLOW = Poly([(24.0, 9.4), (25.4, 9.4), (25.6, 20.2), (24.0, 20.4)])   # the left pillar's lit orange edge
# The front's plates between the flanks: the plate over the gun band, the band's two halves, the lower plate's lit
# top edge and the lower plate (for their paint).
FRONT_X = (23.4, 48.6)
PLATE_UP_R, BAND_SPLIT_R, PLATE_EDGE_R, PLATE_LOW_R = (29.0, 34.0), 39.8, (45.0, 46.1), (46.1, 50.4)

FLANK_L = Poly([(5.6, 28.6), (9.0, 29.4), (10.0, 32.0), (10.8, 35.0), (12.6, 37.0), (14.0, 38.0), (16.0, 39.0),
                (23.0, 39.8), (23.0, 49.4), (20.0, 49.6), (12.0, 45.0), (6.0, 36.0)])
FLANK_R = Poly([(67.4, 28.6), (64.0, 29.0), (63.0, 30.0), (62.0, 32.0), (61.0, 34.0), (60.0, 35.0), (59.0, 37.0),
                (58.0, 38.0), (57.0, 39.0), (49.0, 39.8), (49.0, 49.4), (52.0, 49.6), (61.0, 45.0), (67.0, 36.0)])
FLANK_H = 1.3
BARS = [Poly([(20.8, 33.8), (23.0, 33.8), (23.0, 39.8), (20.8, 39.8)]),
        Poly([(49.0, 33.8), (51.8, 33.8), (51.8, 39.8), (49.0, 39.8)])]
BAND = Poly([(23.0, 34.0), (49.0, 34.0), (49.0, 45.0), (23.0, 45.0)])
BAND_D = 0.9
PLATE_LOW = Poly([(23.0, 45.0), (49.0, 45.0), (49.0, 52.5), (23.0, 52.5)])
PLATE_H = 0.45
SEAMS = [Line([(23.2, 21.8), (23.2, 50.5)]), Line([(48.9, 21.8), (48.9, 50.5)]), Line([(36.5, 29.0), (36.5, 45.0)]),
         Line([(23.4, 39.8), (48.6, 39.8)])]
SEAM_D, SEAM_W = 0.45, 0.32
RIDGES = [Line([(23.8, 16.6), (19.0, 17.6), (14.0, 19.4), (10.0, 21.0), (6.6, 22.8)]),
          Line([(49.2, 16.6), (54.0, 17.6), (59.0, 19.4), (63.0, 21.0), (66.4, 22.8)])]
RIDGE_H, RIDGE_W = 0.9, 0.85
RIVETS = [(51.2, 21.4), (51.6, 23.1), (52.0, 24.8), (52.3, 26.5)]
RIVET_H, RIVET_R = 0.8, 0.85
PORTS = [Ellipse(17.3, 13.6, 2.5, 2.3), Ellipse(56.3, 13.2, 2.5, 2.3)]
PORT_BEZEL = 1.4           # the ports' bezels (times the port's size)
PORT_D = 0.8
LENSES = [Ellipse(16.6, 34.6, 2.9, 3.5), Ellipse(56.0, 35.0, 2.9, 3.5)]
BEZEL = 1.35, 0.8          # the bezels' outer size (times the lens's) and height


STATE = {"slot": None, "dents": None}   # the frame's open slot (a Poly), the wreck's dents (a sampler)
SLOT_D = 2.4                               # how deep the open gun port's slot is under the band


def slot_poly(sprite):
    """The gun port's slot as a frame draws it: the doors drawn back from the seam to the slot's ends (columns of
    the picture), over the band's rows."""
    x0, x1 = SLOT_X[sprite]
    return Poly([(x0, 34.2), (x1, 34.2), (x1, 44.8), (x0, 44.8)])


SLOT_X = {7: (32.0, 38.0), 9: (29.0, 42.0), 11: (27.0, 44.0)}   # the frames' slots (the 'b' pixels round the fire)


def heights(c, r):
    """The dome's surface (heights over the floor) where the camera sees the picture's points (arrays)."""
    c, r = np.asarray(c, float), np.asarray(r, float)
    d = SHELL.signed(c, r)
    u, v = (c - CX) / RX, (r - CY) / RY
    rho2 = np.clip(u * u + v * v, 0.0, 1.0)
    z = FOOT + (SKIRT - FOOT) * sstep(0.0, 0.45, d) + (HEIGHT - SKIRT) * (1.0 - rho2) ** 0.55
    hd = HOUSING.signed(c, r)
    z += HOUSING_H * sstep(0.0, 0.5, hd) + CROWN * sstep(0.5, 2.2, hd)
    z -= RECESS_D * sstep(0.0, 0.6, RECESS.signed(c, r))
    # the mount: a rounded neck along the screen, broad under the capsule, narrowing down to the U's bottom bar
    half = np.interp(r, [15.6, 17.0, 19.5, 25.0], [3.4, 3.6, 3.1, 2.9])
    across = np.clip(1.0 - ((c - 36.5) / half) ** 2, 0.0, 1.0)
    along = sstep(15.4, 16.4, r) * (1.0 - sstep(24.6, 25.2, r))
    z += MOUNT_H * np.sqrt(across) * along
    for f in (FLANK_L, FLANK_R):
        fd = f.signed(c, r)
        z += FLANK_H * sstep(0.0, 0.5, fd) + 0.35 * CROWN * sstep(0.5, 2.0, fd)
    for b in BARS:
        z += FLANK_H * sstep(0.0, 0.4, b.signed(c, r))
    z -= BAND_D * sstep(0.0, 0.5, BAND.signed(c, r))
    z += PLATE_H * sstep(0.0, 0.45, PLATE_LOW.signed(c, r))
    for s in SEAMS:
        z -= SEAM_D * np.exp(-(s.distance(c, r) / SEAM_W) ** 2)
    for s in RIDGES:
        z += RIDGE_H * np.exp(-(s.distance(c, r) / RIDGE_W) ** 2)
    for rc, rr in RIVETS:
        z += RIVET_H * np.exp(-(((c - rc) ** 2 + (r - rr) ** 2) / RIVET_R ** 2))
    for p in PORTS:
        z -= PORT_D * sstep(0.0, 0.5, p.signed(c, r))
        ring = Ellipse(p.c, p.r, p.rx * PORT_BEZEL, p.ry * PORT_BEZEL)
        z += 0.5 * sstep(0.0, 0.4, ring.signed(c, r)) * (1.0 - sstep(-0.3, 0.2, p.signed(c, r)))
    for e in LENSES:
        ring = Ellipse(e.c, e.r, e.rx * BEZEL[0], e.ry * BEZEL[0])
        z += BEZEL[1] * sstep(0.0, 0.5, ring.signed(c, r)) * (1.0 - sstep(-0.4, 0.2, e.signed(c, r)))
    if STATE["slot"] is not None:
        z -= SLOT_D * sstep(0.0, 0.35, STATE["slot"].signed(c, r))
    if STATE["dents"] is not None:
        z -= STATE["dents"](c, r) * sstep(0.5, 2.5, d)
    return np.where(d > 0, z, FOOT)


# The contours the surface is cut along (sharp steps): (shape, its offsets inward).
CONTOURS = ([(SHELL, (0.0, 0.45)), (HOUSING, (0.0, 0.5)), (RECESS, (0.0, 0.6)),
             (FLANK_L, (0.0, 0.5)), (FLANK_R, (0.0, 0.5)), (BAND, (0.0, 0.5)), (PLATE_LOW, (0.0, 0.45)),
             (GLOW, (0.0,))] + [(b, (0.0, 0.4)) for b in BARS] + [(p, (0.0, 0.5)) for p in PORTS] +
            [(Ellipse(e.c, e.r, e.rx * BEZEL[0], e.ry * BEZEL[0]), (0.0, 0.5)) for e in LENSES] +
            [(Ellipse(p.c, p.r, p.rx * PORT_BEZEL, p.ry * PORT_BEZEL), (0.0, 0.4)) for p in PORTS] +
            [(e, (0.2, -0.4)) for e in LENSES] +
            [(Poly([(FRONT_X[0], r0), (FRONT_X[1], r0), (FRONT_X[1], r1), (FRONT_X[0], r1)]), (0.0,))
             for r0, r1 in (PLATE_UP_R, (BAND_SPLIT_R, 45.0), PLATE_EDGE_R, PLATE_LOW_R)])
GRID = 0.85


def contours():
    extra = [(STATE["slot"], (0.0, 0.35))] if STATE["slot"] is not None else []
    return CONTOURS + extra


def surface_mesh():
    """The dome's surface as a closed bmesh in the camera's view (z the heights; moved down the screen after): a grid
    over the outline, cut along every contour, its underside flat at FOOT."""
    x0, x1, y0, y1 = CX - RX - 1.0, CX + RX + 1.0, CY - RY - 1.0, CY + RY + 1.0
    nx, ny = int(math.ceil((x1 - x0) / GRID)), int(math.ceil((y1 - y0) / GRID))
    xs = [x0 + i * GRID for i in range(nx + 1)]
    ys = [y0 + j * GRID for j in range(ny + 1)]
    X, Y = np.meshgrid(np.array(xs), np.array(ys))
    sd = SHELL.signed(X.ravel(), Y.ravel()).reshape(X.shape)
    bm = bmesh.new()
    verts = {}
    for j in range(len(ys)):
        for i in range(len(xs)):
            if sd[j, i] > -2.0 * GRID:
                verts[i, j] = bm.verts.new((xs[i], ys[j], 0.0))
    for j in range(len(ys) - 1):
        for i in range(len(xs) - 1):
            corner = [(i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)]
            if not all(q in verts for q in corner) or max(sd[q[1], q[0]] for q in corner) <= 0:
                continue
            a, b, c, e = (verts[q] for q in corner)
            if (xs[i] + GRID / 2 < CX) == ((i + j) % 2 == 0):  # diagonals mirrored about the middle
                bm.faces.new((a, b, c))
                bm.faces.new((a, c, e))
            else:
                bm.faces.new((a, b, e))
                bm.faces.new((b, c, e))
    for shape, offsets in contours():
        for off in offsets:
            vals = {}
            pts = list(bm.verts)
            s = shape.signed(np.array([v.co.x for v in pts]), np.array([v.co.y for v in pts]))
            for v, val in zip(pts, s):
                vals[v] = float(val) - off
            split_contour(bm, {"f": vals}, "f", 0.0)
            if shape is SHELL and off == 0.0:
                gone = [f for f in bm.faces if sum(vals[v] for v in f.verts) / len(f.verts) < 0]
                bmesh.ops.delete(bm, geom=gone, context="FACES")
                bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    pts = list(bm.verts)
    z = heights(np.array([v.co.x for v in pts]), np.array([v.co.y for v in pts]))
    rim = set()
    for v, zz in zip(pts, z):
        v.co.z = float(zz)
        if v.is_boundary:
            v.co.z = FOOT
            rim.add(v)
    top = list(bm.faces)
    under = {v: (v if v in rim else bm.verts.new((v.co.x, v.co.y, FOOT))) for v in pts}
    bottom = [bm.faces.new([under[v] for v in reversed(f.verts)]) for f in top if not all(v in rim for v in f.verts)]
    bottom_set = set(bottom)
    bm.edges.index_update()
    inner = sorted((e for e in {e for f in bottom for e in f.edges}
                    if all(fc in bottom_set for fc in e.link_faces) and not all(v in rim for v in e.verts)),
                   key=lambda e: e.index)
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(2.0), verts=[], edges=inner, delimit={"NORMAL"})
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    return bm


def canonical(obj):
    """The object's mesh rebuilt in a fixed order (its vertices by position, each face starting at its smallest corner,
    the faces by their corners; polish_cargo_pod.canonical's, the faces' materials kept), so that the shading, the cut
    and the export see the same mesh every run (some of the bmesh steps above fill and dissolve in an order that can
    change from run to run)."""
    me = obj.data

    def key(co):
        return (round(co.x, 5), round(co.y, 5), round(co.z, 5))
    faces = []
    for poly in me.polygons:
        corners = [key(me.vertices[i].co) for i in poly.vertices]
        # corners the rounding merges (slivers the cuts left) go; faces left with fewer than three go too
        corners = [c for i, c in enumerate(corners) if c != corners[i - 1]]
        if len(set(corners)) < 3 or len(set(corners)) != len(corners):
            continue
        start = corners.index(min(corners))
        faces.append((tuple(corners[start:] + corners[:start]), poly.material_index))
    faces = sorted(set(faces))
    verts = sorted({c for corners, _ in faces for c in corners})
    index = {c: i for i, c in enumerate(verts)}
    mesh = bpy.data.meshes.new(me.name)
    mesh.from_pydata(verts, [], [[index[c] for c in corners] for corners, _ in faces])
    for mat in me.materials:
        mesh.materials.append(mat)
    for poly, (_, material) in zip(mesh.polygons, faces):
        poly.material_index = material
    mesh.validate()
    obj.data = mesh
    bpy.data.meshes.remove(me)
    return obj


def to_world(bm):
    """From the picture's coordinates (column, row, height) to the world's: each point TILT z down the screen from
    where the camera sees it; the faces turned outward again (the rows run down the screen)."""
    for v in bm.verts:
        v.co.x, v.co.y = v.co.x - 36.0, 28.0 - v.co.y - TILT * max(v.co.z, 0.0)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)


# --- Painting -------------------------------------------------------------------------------------------------------

def materials():
    def mat(name, i, metallic=0.3, roughness=0.38, glow=None, emission=None):
        pal = k.level_palette()
        if glow is None:
            return k.material(name, palette=i, metallic=metallic, roughness=roughness)
        return k.material(name, palette=i, metallic=metallic, roughness=roughness,
                          emission=pal[emission if emission is not None else i], emission_strength=glow)
    return {
        "steel": mat("dome_steel", 0x6a), "steel_lit": mat("dome_steel", 0x6d), "steel_dark": mat("dome_steel", 0x66),
        "steel_deep": mat("dome_steel", 0x63, roughness=0.5),
        "red": mat("dome_red", 0x48, 0.25, 0.42), "red_lit": mat("dome_red", 0x4c, 0.25, 0.4),
        "red_dark": mat("dome_red", 0x45, 0.25, 0.45),
        "glow": mat("dome_glow", 0x78, 0.0, 0.4, glow=0.22, emission=0x79),
        "capsule": mat("dome_capsule", 0x48, 0.1, 0.18, glow=0.12),
        "streak": mat("dome_streak", 0x7a, 0.0, 0.25, glow=0.35),
        "bronze": mat("dome_lens", 0xa6, 0.45, 0.22), "bronze_hi": mat("dome_lens", 0xaa, 0.45, 0.2),
        "port": mat("dome_port", 0xa3, 0.2, 0.25),
        "cap": mat("dome_inside", 0x64, 0.2, 0.6),
        "slot": mat("dome_slot", 0x61, 0.1, 0.7),
        "fire": [mat("dome_fire", i, 0.0, 0.5, glow=g) for _, i, g in FIRE_BANDS],
    }


def wreck_materials():
    """The burnt wreck's paints, under the intact's names where the parts are the same."""
    def mat(name, i, metallic=0.25, roughness=0.6, glow=None, emission=None):
        pal = k.level_palette()
        if glow is None:
            return k.material(name, palette=i, metallic=metallic, roughness=roughness)
        return k.material(name, palette=i, metallic=metallic, roughness=roughness,
                          emission=pal[emission if emission is not None else i], emission_strength=glow)
    return {
        "steel": mat("wreck_steel", 0x68), "steel_lit": mat("wreck_steel", 0x6b), "steel_dark": mat("wreck_steel", 0x65),
        "steel_hi": mat("wreck_steel", 0x6d),
        "steel_deep": mat("wreck_steel", 0x63, roughness=0.75),
        "red": mat("wreck_tan", 0xa8, 0.3, 0.55), "red_lit": mat("wreck_tan", 0xab, 0.3, 0.5),
        "red_dark": mat("wreck_tan", 0xa5, 0.3, 0.6),
        "glow": mat("wreck_tan", 0xa5, 0.3, 0.6),
        "capsule": mat("wreck_capsule", 0xa7, 0.2, 0.55), "streak": mat("wreck_crack", 0x01, 0.0, 0.9),
        "bronze": mat("wreck_lens", 0x62, 0.3, 0.4), "bronze_hi": mat("wreck_lens", 0x64, 0.3, 0.4),
        "port": mat("wreck_lens", 0x62, 0.3, 0.4),
        "cap": mat("wreck_inside", 0x62, 0.2, 0.7),
        "ember": mat("wreck_ember", 0x76, 0.0, 0.5, glow=0.4, emission=0x77),
    }


def regions(c, r):
    """What the points of the surface are part of (where the camera sees them; arrays), for their paint."""
    out = np.full(len(c), "steel", dtype=object)
    order = [("band", [BAND]), ("red", [FLANK_L, FLANK_R] + BARS), ("recess", [RECESS]), ("mount", [MOUNT]),
             ("red", [HOUSING]), ("glow", [GLOW]),
             ("bezel", [Ellipse(e.c, e.r, e.rx * BEZEL[0], e.ry * BEZEL[0]) for e in LENSES] +
              [Ellipse(p.c, p.r, p.rx * PORT_BEZEL, p.ry * PORT_BEZEL) for p in PORTS]), ("port", PORTS)]
    for key, shapes in order:   # later ones over earlier ones
        hit = np.zeros(len(c), bool)
        for sh in shapes:
            hit |= sh.signed(c, r) > 0
        out[hit] = key
    if STATE["slot"] is not None:
        out[STATE["slot"].signed(c, r) > 0] = "slot"
    rim = SHELL.signed(c, r) < RIM_DARK
    out[rim & (out != "red")] = "rim"
    front = (c > FRONT_X[0]) & (c < FRONT_X[1])
    out[front & (out == "band") & (r < BAND_SPLIT_R)] = "band_up"
    out[front & (out == "band") & (r >= BAND_SPLIT_R)] = "band_low"
    out[front & (out == "steel") & (r > PLATE_EDGE_R[0]) & (r < PLATE_EDGE_R[1])] = "plate_edge"
    out[front & (out == "steel") & (r >= PLATE_LOW_R[0]) & (r < PLATE_LOW_R[1])] = "plate_low"
    out[front & (out == "steel") & (r > PLATE_UP_R[0]) & (r < PLATE_UP_R[1])] = "plate_up"
    return out


RIM_DARK = 0.8          # the shell's last this many pixels darker (the sprites' dark rim)
# Shade bands from the sprites' pixels: (region group, the picture, [(lowest shade, material)]).
STEEL_BANDS = [(-99.0, "steel_dark"), (6.0, "steel"), (11.0, "steel_lit")]
SHADE_BLUR = 1.1
RED_BANDS = [(-99.0, "red_dark"), (4.6, "red"), (9.6, "red_lit")]
FIXED = {"bezel": "steel_lit", "mount": "steel", "recess": "steel_dark", "rim": "steel_deep", "glow": "glow",
         "port": "port", "band_up": "steel_dark", "band_low": "steel_deep", "plate_edge": "steel_lit", "plate_low": "steel",
         "plate_up": "steel", "band": "steel_dark", "slot": "slot"}


def paint_surface(bm, m, steel_art, red_art, slots):
    """Each face of the surface (still in the picture's coordinates: a face's centre is where the camera sees it) its
    part's paint: the steel and the red in bands of the sprite's shades there (the faces cut along their contours),
    the rest fixed; the underside the inside's."""
    steel = blurred(load_art(steel_art), SHADE_BLUR)
    red = blurred(load_art(red_art), SHADE_BLUR)
    for name, sample, bands in (("steel", steel, STEEL_BANDS), ("red", red, RED_BANDS)):
        faces = list(bm.faces)
        cen = np.array([f.calc_center_median() for f in faces])
        keys = regions(cen[:, 0], cen[:, 1])
        group = [f for f, kk in zip(faces, keys) if (kk == "steel" if name == "steel" else kk == "red")]
        verts = list({v for f in group for v in f.verts})
        vals = sample(np.array([v.co.x for v in verts]), np.array([v.co.y for v in verts]))
        field = {v: (float(x) if not np.isnan(x) else 8.0) for v, x in zip(verts, vals)}
        for other in bm.verts:
            field.setdefault(other, 8.0)
        for t, _ in bands[1:]:
            group = list(split_contour(bm, {"f": field}, "f", t, faces=group))
    faces = list(bm.faces)
    cen = np.array([f.calc_center_median() for f in faces])
    keys = regions(cen[:, 0], cen[:, 1])
    sv, rv = steel(cen[:, 0], cen[:, 1]), red(cen[:, 0], cen[:, 1])
    for f, key, s_, r_ in zip(faces, keys, sv, rv):
        if f.calc_center_median().z < FOOT + 1e-3 and abs(f.normal.z) > 0.5 and all(v.co.z < FOOT + 1e-3 for v in f.verts):
            mat = "cap"
        elif key == "steel":
            shade = 8.0 if np.isnan(s_) else s_
            mat = [b for lo, b in STEEL_BANDS if shade >= lo][-1]
        elif key == "red":
            shade = 7.0 if np.isnan(r_) else r_
            mat = [b for lo, b in RED_BANDS if shade >= lo][-1]
        else:
            mat = FIXED[key]
        f.material_index = slots.setdefault(m[mat].name, (len(slots), m[mat]))[0]


# --- Parts laid on it -----------------------------------------------------------------------------------------------

FIRE_BANDS = [(-99.0, 0x74, 0.3), (3.0, 0x77, 0.38), (6.0, 0x79, 0.45), (9.0, 0x7b, 0.52), (12.0, 0x7d, 0.6)]
FIRE_H = 1.6          # how high the fire swells over the slot's floor


def fire(m, sprite):
    """The fire in the open gun port: a heap over the frame's fire pixels (the blurred mask), its top painted by their
    shades (blurred) in glowing bands, on the slot's floor."""
    rows = ["." * 72] * 34 + ["." * 24 + line + "." * 24 for line in FIRE_ART[sprite]] + ["." * 72] * 11
    art = load_art(rows)
    shade = blurred(art, 0.7)
    have = np.argwhere(art >= 0)
    r0, r1 = have[:, 0].min() - 1.0, have[:, 0].max() + 2.0
    c0, c1 = have[:, 1].min() - 1.0, have[:, 1].max() + 2.0
    step = 0.35
    cs = np.arange(c0, c1 + 1e-6, step)
    rs = np.arange(r0, r1 + 1e-6, step)
    C, R = np.meshgrid(cs, rs)
    floor = heights(C.ravel(), R.ravel()).reshape(C.shape)
    verts, faces, values = [], [], []
    index = {}
    dens = np.zeros(C.shape)
    for j in range(C.shape[0]):
        for i in range(C.shape[1]):
            cc, rr = C[j, i], R[j, i]
            near = ((have[:, 1] + 0.5 - cc) ** 2 + (have[:, 0] + 0.5 - rr) ** 2).min()
            dens[j, i] = math.exp(-near / 1.1)
    for j in range(C.shape[0]):
        for i in range(C.shape[1]):
            h = FIRE_H * dens[j, i] ** 0.6
            index[i, j] = len(verts)
            verts.append((C[j, i], R[j, i], float(floor[j, i]) + 0.05 + h))
            sv = shade(np.array([C[j, i]]), np.array([R[j, i]]))[0]
            values.append(-99.0 if dens[j, i] < 0.35 else (0.0 if np.isnan(sv) else float(sv)))
    for j in range(C.shape[0] - 1):
        for i in range(C.shape[1] - 1):
            q = [index[i, j], index[i + 1, j], index[i + 1, j + 1], index[i, j + 1]]
            if min(dens[j, i], dens[j, i + 1], dens[j + 1, i + 1], dens[j + 1, i]) < 0.2:
                continue
            faces.append(tuple(q))
    obj = k.mesh_object("fire", verts, faces, m["fire"][0])
    from polish_orb_red import band_split
    band_split(obj, values, [(lo, mat) for (lo, _, _), mat in zip(FIRE_BANDS, m["fire"])])
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    # close it: a flat underside under its rim, a little into the slot's floor
    boundary = [e for e in bm.edges if e.is_boundary]
    if boundary:
        ext = bmesh.ops.extrude_edge_only(bm, edges=boundary)
        for v in [g for g in ext["geom"] if isinstance(g, bmesh.types.BMVert)]:
            v.co.z -= 0.6
        bmesh.ops.holes_fill(bm, edges=[e for e in bm.edges if e.is_boundary], sides=0)
    to_world(bm)
    bm.to_mesh(obj.data)
    bm.free()
    canonical(obj)
    k.smooth(obj, 60.0)
    return obj


def capsule(m, wreck=False):
    """The red glass capsule lying in the housing's recess on its mount, pointing up the screen (columns 33-40, rows
    3.6-16): a cylinder with a rounded tip, built where the camera sees it and moved down the screen as the rest."""
    c0, r_tip, r_base, rad = 37.0, 4.0, 16.4, 3.75
    if wreck:
        rad *= 0.94
    z_axis = float(heights(np.array([37.0]), np.array([11.0]))[0]) + 1.2
    seg, rings = 28, []
    profile = []
    for i in range(7):  # the tip: a quarter circle, from its point out to the full radius
        a = math.radians(90.0 * i / 6)
        profile.append((r_tip + rad * (1 - math.cos(a)), rad * math.sin(a)))
    for r in (r_tip + rad + 2.0, r_base - 2.0, r_base - 0.6):
        profile.append((r, rad))
    profile.append((r_base, rad * 0.9))
    profile.append((r_base + 0.2, 0.0))
    verts, faces = [], []
    for r, radius in profile:
        ring = []
        for j in range(seg):
            a = 2 * math.pi * j / seg
            x, z = c0 + radius * math.cos(a), z_axis + radius * math.sin(a) * 0.95
            ring.append(len(verts))
            verts.append((x, r, z))
        rings.append(ring)
    for a_, b_ in zip(rings, rings[1:]):
        for j in range(seg):
            faces.append((a_[j], a_[(j + 1) % seg], b_[(j + 1) % seg], b_[j]))
    obj = k.mesh_object("capsule", verts, faces, m["capsule"])
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    # the lit streak along its upper left (columns 35-36 of rows 5.5-14); the wreck's: a crack down its middle, an
    # ember in it
    slot = mk.slot_of(obj, m["streak"])
    ember = mk.slot_of(obj, m["ember"]) if wreck else None
    for f in bm.faces:
        cc = f.calc_center_median()
        if wreck:
            if abs(cc.x - 36.3) < 0.55 and 6.0 < cc.y < 12.6 and f.normal.z > 0.3:
                f.material_index = ember if 8.2 < cc.y < 10.8 else slot
        elif 34.3 < cc.x < 36.1 and 5.4 < cc.y < 14.6 and f.normal.z > 0.3:
            f.material_index = slot
    to_world(bm)
    bm.to_mesh(obj.data)
    bm.free()
    canonical(obj)
    k.smooth(obj, 60.0)
    return obj


def lens(m, e, name):
    """A lens in its bezel: a low glassy cap over the lens's ellipse."""
    seg, rings = 32, 6
    z0 = float(heights(np.array([e.c]), np.array([e.r]))[0])
    verts, faces = [], []
    for i in range(rings + 1):
        t = i / rings
        f = math.cos(t * math.pi / 2)
        for j in range(seg):
            a = 2 * math.pi * j / seg
            verts.append((e.c + e.rx * f * math.cos(a), e.r - e.ry * f * math.sin(a), z0 - 0.4 + 1.1 * math.sin(t * math.pi / 2)))
    for i in range(rings):
        for j in range(seg):
            a, b = i * seg + j, i * seg + (j + 1) % seg
            faces.append((a, b, b + seg, a + seg))
    faces.append(tuple(range(seg))[::-1])
    obj = k.mesh_object(name, verts, faces, m["bronze"])
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    slot = mk.slot_of(obj, m["bronze_hi"])
    for f in bm.faces:
        cc = f.calc_center_median()
        if (cc.x - e.c) < -0.6 and (cc.y - e.r) < -0.6:
            f.material_index = slot
    to_world(bm)
    bm.to_mesh(obj.data)
    bm.free()
    canonical(obj)
    k.smooth(obj, 60.0)
    return obj


def dome_whole(m, look="intact", sprite=85):
    STATE["slot"] = slot_poly(sprite) if look == "intact" and sprite in SLOT_X else None
    STATE["dents"] = dent_field() if look == "wreck" else None
    bm = surface_mesh()
    slots = {}
    if look == "wreck":
        paint_wreck(bm, m, slots)
    else:
        paint_surface(bm, m, DOME_STEEL, DOME_RED, slots)
    # the paint's cuts on the sloping surface: their new points onto the surface (split_contour interpolates linearly)
    pts = [v for v in bm.verts if v.co.z > FOOT + 1e-4]
    z = heights(np.array([v.co.x for v in pts]), np.array([v.co.y for v in pts]))
    for v, zz in zip(pts, z):
        v.co.z = max(float(zz), FOOT + 2e-4)
    to_world(bm)
    mesh = bpy.data.meshes.new("dome")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("dome", mesh)
    bpy.context.scene.collection.objects.link(obj)
    for name, (i, mat) in sorted(slots.items(), key=lambda kv: kv[1][0]):
        obj.data.materials.append(mat)
    canonical(obj)
    k.smooth(obj, 35.0)
    parts = [obj, capsule(m, look == "wreck")]
    if look != "wreck":  # the wreck's lenses are smashed: their sockets dark
        parts += [lens(m, e, "lens%d" % i) for i, e in enumerate(LENSES)]
    if STATE["slot"] is not None:
        parts.append(fire(m, sprite))
    return parts


DENT = 1.8            # how deep the wreck's shell is dented where its pixels are burnt darkest


def dent_field():
    """The wreck's dents: deepest where its steel's shades are darkest (blurred), none where they are lit."""
    shade = blurred(load_art(WRECK_STEEL), 0.9)

    def dents(c, r):
        v = shade(c, r)
        v = np.where(np.isnan(v), 8.0, v)
        return DENT * np.clip((5.0 - v) / 4.0, 0.0, 1.0) ** 1.2
    return dents


WRECK_BANDS = [(-99.0, "steel_deep"), (2.2, "steel_dark"), (4.6, "steel"), (7.0, "steel_lit"), (9.8, "steel_hi")]
TAN_BANDS = [(-99.0, "red_dark"), (7.5, "red"), (11.0, "red_lit")]


def paint_wreck(bm, m, slots):
    """The wreck painted from its sprites: the burnt steel (its flanks' armour too) in bands of their shades, the
    housing scorched tan in bands of its bronzes', the bezels and ports dark (its faces cut along their contours)."""
    steel = blurred(load_art(WRECK_STEEL), SHADE_BLUR)
    tan = blurred(load_art(WRECK_BRONZE), SHADE_BLUR)

    def keys_of(faces):
        cen = np.array([f.calc_center_median() for f in faces])
        keys = regions(cen[:, 0], cen[:, 1])
        housing = HOUSING.signed(cen[:, 0], cen[:, 1]) > 0
        keys = np.where(housing, "tan", keys)
        keys = np.where(np.isin(keys, ["red", "steel", "band", "band_up", "band_low", "plate_edge", "plate_low",
                                        "plate_up", "recess", "mount", "bezel"]), "burnt", keys)
        return cen, keys
    for name, sample, bands in (("burnt", steel, WRECK_BANDS), ("tan", tan, TAN_BANDS)):
        faces = list(bm.faces)
        _, keys = keys_of(faces)
        group = [f for f, kk in zip(faces, keys) if kk == name]
        verts = list({v for f in group for v in f.verts})
        vals = sample(np.array([v.co.x for v in verts]), np.array([v.co.y for v in verts]))
        field = {v: (float(x) if not np.isnan(x) else 6.0) for v, x in zip(verts, vals)}
        for other in bm.verts:
            field.setdefault(other, 6.0)
        for t, _ in bands[1:]:
            group = list(split_contour(bm, {"f": field}, "f", t, faces=group))
    faces = list(bm.faces)
    cen, keys = keys_of(faces)
    sv, tv = steel(cen[:, 0], cen[:, 1]), tan(cen[:, 0], cen[:, 1])
    for f, key, s_, t_ in zip(faces, keys, sv, tv):
        if f.calc_center_median().z < FOOT + 1e-3 and abs(f.normal.z) > 0.5 and all(v.co.z < FOOT + 1e-3 for v in f.verts):
            mat = "cap"
        elif key == "burnt":
            mat = [b for lo, b in WRECK_BANDS if (6.0 if np.isnan(s_) else s_) >= lo][-1]
        elif key == "tan":
            mat = [b for lo, b in TAN_BANDS if (8.0 if np.isnan(t_) else t_) >= lo][-1]
        else:
            mat = {"rim": "steel_deep", "glow": "red_dark", "port": "port"}.get(key, "steel_deep")
        f.material_index = slots.setdefault(m[mat].name, (len(slots), m[mat]))[0]


NAMES = ["tl", "tm", "tr", "bl", "bm", "br"]
BOXES = [(-36.0, -12.0, 0.0, 28.0), (-12.0, 12.0, 0.0, 28.0), (12.0, 36.0, 0.0, 28.0),
         (-36.0, -12.0, -28.0, 0.0), (-12.0, 12.0, -28.0, 0.0), (12.0, 36.0, -28.0, 0.0)]
# (look, gun port frame, [(model, sprite, piece)])
LOOKS = [("intact", 85, [("armour_dome_" + n, s_, i) for i, (n, s_) in enumerate(zip(NAMES, [45, 47, 49, 83, 85, 87]))]
          + [("armour_dome_85", 85, 4)]),
         ("intact", 7, [("armour_dome_7", 7, 4)]), ("intact", 9, [("armour_dome_9", 9, 4)]),
         ("intact", 11, [("armour_dome_11", 11, 4)]),
         ("wreck", 85, [("armour_dome_wreck_" + n, s_, i) for i, (n, s_) in enumerate(zip(NAMES, [39, 41, 43, 77, 79, 81]))])]


def own_mask(sheets, sprites):
    """The picture's pixels of the sprites (3 x 2) that are not the floor (palette ramp 0 is the map's floor), from
    the extracted sheet's index file."""
    wid = 19 * 12
    raw = open(os.path.join(sheets, "enemy_M.idx"), "rb").read()
    out = [[False] * 72 for _ in range(56)]
    for i, s_ in enumerate(sprites):
        x0, y0 = (s_ - 1) % 19 * 12, (s_ - 1) // 19 * 14
        mask = k.sprite_mask(os.path.join(sheets, "enemy_M.png"), s_)
        for yy in range(28):
            for xx in range(24):
                v = raw[(y0 + yy) * wid + x0 + xx]
                if mask[yy][xx] and (v >> 4) != 0:
                    out[(i // 3) * 28 + yy][(i % 3) * 24 + xx] = True
    return out


def build():
    options = k.args()
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    sheets = options.get("check")
    for look, sprite, pieces in LOOKS:
        if only and not any(n in only for n, _, _ in pieces):
            continue
        k.reset()
        bpy.context.scene.view_settings.view_transform = "Standard"
        m = wreck_materials() if look == "wreck" else materials()
        parts = dome_whole(m, look, sprite)
        triangulate(parts)
        label = "%s %d" % (look, sprite)
        print("armour dome %s whole: %d triangles" % (label, mk.triangles(parts)))
        sprites = [39, 41, 43, 77, 79, 81] if look == "wreck" else [45, 47, 49, 83, sprite, 87]
        if sheets and sprite == 85:
            mk.compare("whole (%s) as the camera sees it" % label, view_coverage(parts, W, H), own_mask(sheets, sprites))
        if "whole" in options:
            mk.export(parts, options["whole"] + "armour_dome_%s_%d.glb" % (look, sprite))
        if "preview" in options:
            mk.preview(options["preview"] + "armour_dome_%s_%d" % (look, sprite), parts, size=(W, H), scale=8)
        for name, spr, i in pieces:
            if only and name not in only:
                continue
            box = BOXES[i]
            open_box = tuple(None if abs(v) > 30.0 else v for v in box)
            cut = [p for p in (view_cut(o, open_box, m["cap"]) for o in parts) if p is not None]
            centre = Vector(((box[0] + box[1]) / 2, (box[2] + box[3]) / 2, 0.0))
            mk.transform(cut, Matrix.Translation(-centre))
            bpy.context.view_layer.update()
            drop_unused(cut)
            triangulate(cut)
            piece = join(cut, name)
            piece.data.name = name
            for o in parts:
                o.hide_render = True
            if sheets:
                whole = own_mask(sheets, sprites)
                c0, r0 = int(box[0] + 36), int(28 - box[3])
                mk.compare("%s (M %d) as the camera sees it" % (name, spr), view_coverage([piece], 24, 28),
                           [row[c0:c0 + 24] for row in whole[r0:r0 + 28]])
            mk.report(name, [piece], os.path.join(out, name + ".glb"))
            if "preview" in options:
                mk.preview(options["preview"] + name, [piece])
            data = piece.data
            bpy.data.objects.remove(piece)
            if data.users == 0:
                bpy.data.meshes.remove(data)
            for o in parts:
                o.hide_render = False


if __name__ == "__main__":
    build()
