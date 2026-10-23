"""MINERS's banded rock column and its broken look (sheet M sprites 163 165 above 201 203 above 239 241, 2x2 each: one
48 x 84 picture; the broken look 167 169 above 205 207 in the upper four's places; enemies 1191-1196 of episode 5,
ground layers, armour 30, worth 10 each), polished (2026-10-23, round 38, the quality redo: rebuilt from faceted
stones; round 35's version, one signed distance field with the picture's shading as relief and its shades painted on
face by face, read as a lumpy blob with blotchy white highlights; that one replaced wave3_ah_rock.py, an octagonal
pillar built as a heightfield on its own frame). models.cfg: model rock_column_tl / _tr / _ml / _mr / _bl / _br and
rock_column_wreck_tl / _tr / _ml / _mr ... origin (unchanged); every sprite line has height=-4 (unchanged).

Where the level puts it (the level events, tools/content/tyrevents.py; the enemy data, tools/content/tyrdata.py):
MINERS builds the column five times (t468 at column 3, t1140 at 10, t1196 at 9, t3632 at 6, t4276 at 7), each time
from six ground enemies with one link: 1195 (239) at (x, y) and 1196 (241) at x + 24 on the ground layer, 1193 (201)
and 1194 (203) 28 pixels up the screen and 1191 (163) and 1192 (165) 56 pixels up (d5 -29 and -57) on ground 2: the
sheet's picture whole. Always on the map's row above tiles of its own: the map paints the column's broken stump (the
lower drum shattered) in the tile row under 239 and 241 (background 1, e.g. map row 274 under the column whose top left
is at row 272, column 3). Shot, the six go together (one link): the upper four turn to their broken looks (dgr 167
169 205 207, dlevel -1: they stay), the lower two die (the game leaves its slumped wrecks of their models over the
painted stump). No other enemy, launched ones included, shows these sprites; none is another sprite's pixels
mirrored, turned or in other ramps; no episode 6 level places the column.

As the sprites and their 4x upscales draw it (columns and rows of the 48 x 84 picture; ramp 10's tans 0xa1-0xae): an
octagonal column of stone seen from the front and above, standing up the screen from its foot (the bottom edge, rows
68-78) to its head (row 2): two drums (rows 39-52 and 57-71 at the front) parted by dark joints (rows 34-38 and 53-56,
near-black greys and browns, 0x01-0x04, 0xb0), their sides at columns 2 and 46, their front faces between darker
corner lines (columns 12-13 and 35-36), mottled, flecked with gold (0x18-0x1c); the head a pale rough stone (rows 2-33,
0xab-0xae) bulging up into a dome (its outline highest, row 2, over the middle), sparkling with white quartz (the
brightest shade of several ramps: 0x4f 0x5f 0x7f 0xbf 0xff) and a few cracks. The red ground round it (ramp 4, rows
56-83) is the map's, painted in: left out. The broken look: the head gouged into a deep black hollow (columns 8-22 of
rows 7-22, ramp 6's 0x60-0x66), its top right broken away (the outline running from column 25 of row 3 to column 46 of
row 28) over a smaller hollow (columns 33-39 of rows 21-27); hollows in the upper drum (columns 33-41 of rows 31-38,
11-18 of rows 46-55, 34-38 of rows 40-50).

Built as such a column of separate stones, for the game's camera: designed in the picture's plane (x, y as the
picture draws them, z up) and then sheared along the game camera's line of sight (y - z tan 20: polish_lava_grub.py's
and polish_red_mound.py's way), so that the camera sees every point where the picture draws it. In the picture's
plane the column leans back LEAN (72) degrees from upright about its foot, so that the camera sees its stones nearly
face on and their joints as the flat arcs the sprites draw (a ring of the column shows RN cos LEAN = 5.6 rows deeper
at its front than at its sides); the joints lie where the sprites draw them at the column's sides (rows 50 and 31: J1,
J2 along its axis), the head's rim at row 20 (T_CAP), its dome's tip at row 2 (T_END). Each stone is a convex solid
with clean flat facets (the convex hull of its rings: no noise, no painting): the two drums octagons (RX across, RN
deep, the front face W_FRONT wide, the corners chamfered CORNER) with chamfered ends, a little fuller in their middles
(each face a few facets); the foot a plinth flaring forward to the sprites' lowest row (78) and under its ring straight
down to the ground (in the picture's plane: along the camera's line of sight once sheared, unseen), a few of its edges
chipped off by flat cuts; the head the octagon narrowing into a dome whose points are jittered (ROUGH), so that its
hull is a rough cap of flat chiselled facets, CHIPS of its edges chipped. In each joint a dark core shows between the stones' chamfers. Details are their own small solids:
gold nuggets set into the stones where the picture's gold flecks cluster, white quartz crystals standing out of the
head where its sparkles cluster (found by a ray straight down in the picture's plane: what the camera sees there).
The broken look is the same column shattered, cut into with exact booleans (one joined cutter a part,
self-intersection on; the meshes rebuilt in a fixed order after them, canonical(), so that the output is the same
every run): cavities where the broken pictures are dark (hollow_mask(): ramp 6's black or shades 0-2 that are not dark
in the intact picture, closed over a pixel), each a jagged funnel over the region's outline grown by HOLLOW_GROW, its
floor sloping in from the surface to HOLLOW_DEPTH with its points jittered (broken faces the camera sees); V-shaped
cracks along CRACKS; chips broken off the upper drum's rims and corners and the head's lower rim (chip_cutters); the
head's top right broken away beyond the broken outline by three faceted wedges. The broken faces keep each stone's own
colour; only faces deeper than DEEP under the original surface, the holes' insides, are dark (0x61). Broken chunks
(RUBBLE) lie in the head's crater, in the joints and on the drum, faceted, in the colour of the stone they lie on.
Heights: the foot's front 17 over the ground, the head 34.6 at its top (round 35's 34.3).
Materials by part (palette, the shading the geometry's): the drums 0xa7, the head 0xad, the joints 0x02, gold 0x1b
(metallic, emission 0.12), quartz 0xbf (emission 0.18), the holes' dark insides 0x61. The facets flat-shaded, the
holes' dark insides smooth.

The whole is cut along the sprites' edges in the picture's plane (x = 0, y = 14 and -14: the camera's lines of sight
once sheared, polish_stone_face.view_cut's planes), so that each piece holds what the camera sees in its sprite (the
upper pieces the head, which stands over the middle pieces once sheared), the cuts closed in each part's own material
(they show only through gaps: the pieces stand together); each piece sheared, moved so that its sprite's centre is its
origin, triangulated (polish_k_pod.triangulate) and joined. The broken pieces are cut the same way (only the upper
four are exported).

Coordinates: 1 unit = 1 game pixel; +X right, +Y up the screen, +Z up from the ground (z = 0); the whole's origin is
the picture's middle (the corner where 201 and 203 meet, half way down): column c of the picture is x = c + 0.5 - 24,
row r is y = 41.5 - r. The pieces' centres: 163 (-12, 28), 165 (12, 28), 201 (-12, 0), 203 (12, 0), 239 (-12, -28),
241 (12, -28). Drawn at their origins (origin) on the ground layers: height=-4 sets the column on the terrain (the game
lifts pieces side by side moving alike together, to the terrain under their middle; MINERS's ground is level there).

shear_to_camera, view_coverage, cut_piece, drop_islands and TILT stay as round 35 wrote them: polish_lander.py,
polish_tan_dome.py and polish_miners_rig.py import them. The old code (wave3_ah_rock.py and its kit and art) went with
round 35.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the whole's and each piece's
silhouette as the camera sees it against the sprites' own pixels, the ground they paint left out), --preview <prefix>,
--whole <prefix> (the uncut column and its broken look: views), --only <name,...>.
"""
import math
import os
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_deli_boss import join, drop_unused  # noqa: E402
from polish_ring_machine import relief, round_edge, resample  # noqa: E402
from polish_fleet_walker import mask_loops, area  # noqa: E402

TILT = math.tan(math.radians(20.0))     # the camera shows a point this much further up the screen per pixel up

# The pieces: model, sprite, (its broken look's model, sprite), its box in the picture's plane (x0, x1, y0, y1; None:
# no neighbour that side), its sprite's centre.
PIECES = [("rock_column_tl", 163, ("rock_column_wreck_tl", 167), (None, 0.0, 14.0, None), (-12.0, 28.0)),
          ("rock_column_tr", 165, ("rock_column_wreck_tr", 169), (0.0, None, 14.0, None), (12.0, 28.0)),
          ("rock_column_ml", 201, ("rock_column_wreck_ml", 205), (None, 0.0, -14.0, 14.0), (-12.0, 0.0)),
          ("rock_column_mr", 203, ("rock_column_wreck_mr", 207), (0.0, None, -14.0, 14.0), (12.0, 0.0)),
          ("rock_column_bl", 239, None, (None, 0.0, None, -14.0), (-12.0, -28.0)),
          ("rock_column_br", 241, None, (0.0, None, None, -14.0), (12.0, -28.0))]
LAYOUT = [[163, 165], [201, 203], [239, 241]]
LAYOUT_DMG = [[167, 169], [205, 207], [239, 241]]

# The column's picture (rows 2-79 of the 48 x 84: 163 165 above 201 203 above 239 241, as MINERS places them) and the
# broken look's (rows 2-55: 167 169 above 205 207), a character per pixel: a hex digit its shade (ramps 10, 11, 1 and
# 0: the tans, browns and greys), G a gold fleck (ramp 1, shades 7-12), Q quartz (the brightest shade of any ramp), K the
# broken look's black (ramp 6); '.' none, or the red ground the lower sprites paint round the column (ramp 4: the
# map's, left out).
ART = """
......................ccbbG.....................
.................bc9aeceQdcdb8aa................
.............ccccQQQdQceedbdbcacab99............
.........9eQedeeQQeQeQdeQddbcddcccbaaa87........
........a8QQQQQQQQdeQdbeeddbedcdaabeaaa86.......
.......eccdQQQQQQQQQQdbceecbccQQcdcdcba977......
.......QQdbdddQQQQQQQdccdeaceQQQdcccbd9b87......
.......QQedcQQQQQQQQQQQccbbbdcdddbc9cb9bG8......
.......ecQeceQdQQQeddcebbbdeededbdecb99a8G6.....
......ccQQeQeaadQQebcbbb9abcbcccee9caba9877.....
......deQQQQebcbca87Gbb99bba6778abcaaba9877.....
......eQQeQQcccb7becbbbbabb989878ccbaaaaa78.....
.....deQQQedbdQb7dedcGbbbba988869cab8abaa886....
.....dQQQQdbcQec7babcb9bbaa99887acc9aaba9886....
.....eQQQedbQdecGbabdebab9999G78bdecdbbaG8G7....
....beQQddbdecebGabbcebcb9888GG8bdececc998GG7...
....bQedcbdeQbebG9bdbcbca8888G89aeQeedb988G77...
...7cededeeQQceGG8bdcbbaa8887G9abQeeedbd897773..
..67cdQQdQQQdcc979acbba9977779aacQeecdce9776732.
..26dQQcQQQQcca8779aab99977G8Gb9cQQdcbccc777730.
..07cQdQQQQQcdb88779aa9897G9aaa9acQQebdcc977730.
..17adeQQQQQcc887bb9989GG788aabd9aQQQbceca77730.
..17c9QQQeQQdb86ccbb9797G7888bcQQ9dQQbcecb8G630.
..17aaQQQdQedc76ddcae79766778aceQQcQQdcQcb9G530.
..078aeQddQecb7ddbaacdccbdQdacbeQQbQQecQdda9630.
..278beQdeeda9acbaaceeedcdedbccceQQeQecdddaa530.
..6679cdeQddaaca98addceebeccabedcdQeQQceec96332.
..46269cecb9bdccdabeQcQebdcaaaQdQQdeQebedb63121.
..25216acbaacddcdbadeeQebdcdccccQQQQQd9dc730002.
...23216a889aQedddacddecdcccdQbedeQQec9b730001..
....13206b757cdcdd98ceddedcddcdddQQedbc840011...
....61322799aacbbcbbeeacdaceebdedcc8767511204...
....761447873357899b9ba8a768a9877532355532055...
....66526796222222345898898753211111135530355...
....65552333345642222247773011112332221002334...
....75657222111112235656775543210000012322334...
...7656678212221000111245321100001345662223543..
..575486796786652222201222000244433433232345430.
..265589787897755546663323354332334543222344430.
..0765888767876533557887567553222243432223G4430.
..17558d77787677777565GG56754444444332222454430.
..17656a777986665578758756535543244423212454330.
..176669667755689998755657654567554433212343430.
..076768666665789755785757645665GG4433212334440.
..377666576666789cdc7877663256689G4432222224431.
..7767555666665797GG755655545665432432212235332.
..362475556766675898487655543355652332222252022.
..133048676676785888466655545535542222222620012.
...1320487667775455645555554553322343222520001..
....12205976777664445655555553333334322731101...
....61222778988a43555G66556653323377765511015...
....76136786302458899666555587765321245532155...
....66515688422222223579896421111111254321345...
....65552232223355322247773001233221110022344...
....65757322111011123467786432100000123522434...
..676567787622222000112333210000235552222335432.
..375487886887654322221121013442333443232345330.
..266588787887655556666333554333334343222354430.
..17558a876566765334788G577553223343432223G5430.
..17558d776976677776757G56755554454222222444330.
..176568777876677646757G55445433455433222453430.
..1767695667546899988755576556665325332.2343430.
..076758676666789aa748675754566G984422222334430.
..577665576765789b.c78775634566G9G34322.2234432.
..7647555665665496785635555456745534322.2234222.
..262275566776775898577655543446652332222241022.
..123127676677775888466555445535442332222510112.
...0231277667775345653555555553322343222510202..
....01313886676554555665555555433333327521201...
....201337787888a355577655655332876655552201....
....2.0266762022356889b565b8776321112344301.....
.....2.02356643222222267875211111123332201......
......2.1111111223432036663123322100000110......
........221000000011123465311000000012341.......
..............22100000011100000133322110........
...................3320000022212222200..........
......................211..011.22..22...........
.....................222...2....................
"""
ART_DMG = """
......................82........................
.................bc9aeaG5.......................
.............ccccQQQdQcc61......................
.........7dQedeeQQeQeQdda22.....................
........41Kdddeeddbdec9cc630....................
.......c2K0GGaGK879GdaGGdG521...................
.......e6KKK2354002167G8Gd8766..................
.......eGKKKK011KKKK19d9aaba9432................
.......dG0KKKKKKK1KKK3G99aded99402..............
......cbc50KKKKKKKKK157868bcbb9G7402............
......ddd721KKKKKKKK056569G9688775300...........
......eee720KKK00KK1212678988aa88G952...........
.....deec721KK00KKKKKKK37GG789a8acaa43..........
.....dQd84220000KKKKKKK454447899Gdd9942.........
.....eQb51KK1010KKKKKKK340124679bcecd8323.......
....bee93KKK1011KKKKKKK2310025G8bdedeb724.......
....bQc511K01010KKKKKKK00K0024689dQedc8444......
...7ce82KK110K00KKKKKK0KKKK00257GeeecaGG563.....
..67ca50KKKKKK10KKKKKK0KKKK002347cccGGGb743.....
..26cG1KK01KK110KKKK000KKKK024204bbG535GG543....
..07950K03311242KKKK1KKKK000442025.752469G43....
..1652003999551121KK00KK021156K6226320168G43....
..1780116GbeG400G5K00KKKKKK2698981010KK47a64....
..177225bGddbG01c8225KKKKKK27aba75K00KK27a74....
..07636bcdQe961Gc956510KKK379cbb72KKKKK27bG64...
..2778cedeec635GG99a9210K0589cca61KKKKK07b984...
..6679cdeQdc65G998abG21113599bea511110K18GG5332.
..46279cedb8GG9bdbbdc3222578aGQG931020K2Ga63121.
..252069cbaaGcc9cbGdc842268bccc9810K01K1G630002.
...232K59G899edbGcacc963579bdQab710KKKK0220001..
....14206bKK7bGGGcG8cdGG9abddddb852KKKK00K011...
....61323899G9GG9GaGee89G9ceecdda6KKKK11KK204...
....7614K8871212478a9b979768a98784KKKKKKK0055...
....6552679610KKK1235998GG87530111KKKKKKKK255...
....64552334332201002157761010KK1521KK0KK0234...
....74557223201K100157677645431K01201K1K10234...
...765667821222KK1111115532000KKK122220K012543..
..5754867967G663KK01201233000355420011200235430.
..26658G6878G675301335332335323143100K001344430.
..07668G7556G6553000467756754113332KKK1013G443K.
..17558c544676777630225G677533345530KK10035443K.
..176459544G887765652045675355432542KK10025433K.
..17656G5456578aba97302258754567564201011143430.
..0767685533347ab975442448745676GG4200022234440.
..3776663420K0369dec443346315679aG3100K23324431.
..776755432KKKK157cc50133553467653010KK03335332.
..3624765551KKKK058945444553335563K000003352022.
..13304878730KKKK25965445653663541K102212720012.
...1320488841KKK0K0677555553553320KK0331400001..
....12205a962KKKKKK288655544433331KK03372K101...
....6122078850KKKKK17G8765655432320K366601015...
....761367971KK00KK399876654887642KK145642155...
....665067993KKKKKKKK9a98963201K11KK265321345...
....655534442KKKKKK14GK867300010200K022121344...
"""
ART_TOP = 2

# --- The column (in the picture's plane) ------------------------------------------------------------------------------
LEAN = math.radians(72.0)
SA, CA = math.sin(LEAN), math.cos(LEAN)
Y_FOOT, Z_FOOT = -28.0, 0.0             # its axis meets its foot ring here (the foot's sides drawn at row 69.5)
X_AXIS = 0.5                            # (the sprites draw it from column 2 to 46: its middle half a pixel right)
RX, RN = 22.5, 18.0                     # the octagon: half its width, half its depth (front to back)
W_FRONT, H_SIDE = 10.8, 7.2             # half the front face's width, half the side faces' depth
J1, J2 = 19.5 / SA, 38.5 / SA           # the joints' middles along the axis (the sprites' rows 50 and 31 at its sides)
GAP = 1.45                              # half the joints' gap between the stones
END = (1.6, 0.895)                      # the stones' chamfered ends: how long along the axis, how far in (a share)
BULGE = 1.022                           # the drums a little fuller in their middles
CORNER = 0.55                           # the octagon's corners chamfered this far along its faces (catching light)
PLINTH = [(0.0, 1.0, 26.0), (2.6, 1.0, 21.0), (6.2, 1.0, 18.2)]   # the foot: (axis, share of the width, depth)
# The head: from the upper joint up, the octagon (shares of it along the axis) narrowing into a rough dome whose tip
# is drawn at row 2 (T_END along the axis); its facets: the points jittered in by up to ROUGH, every DOME_STEP.
T_CAP = 49.5 / SA
T_END = (70.0 - 2.4) / SA
HEAD = [(J2 + GAP, END[1]), (J2 + GAP + END[0], 1.0), (T_CAP - 3.0, 0.985), (T_CAP, 0.955)]
DOME_POWER, DOME_STEP, ROUGH = 2.3, 1.3, 1.15
SKIRT = 1.5                             # how far the column reaches under the ground
CHIPS = 6                               # chipped edges on the head
# The broken look: cavities where the broken pictures are dark (hollow_mask(); regions of HOLLOW_MIN pixels or more):
# each a jagged funnel over the region's outline grown by HOLLOW_GROW (its points jittered JAG), its floor sloping in
# at HOLLOW_SLOPE from the surface to HOLLOW_DEPTH (the big regions deepest), the floor's points jittered JAG_FLOOR:
# broken faces. Cracks: V grooves along CRACKS (half width, depth: CRACK). Faces deeper than DEEP under the stone's
# surface are the holes' dark insides; the shallower broken faces keep the stone's own colour. WRECK_CHIPS edges of
# the head and of the upper drum chipped off; RUBBLE: broken chunks (column, row, size) lying where they fell.
HOLLOW_DEPTH, HOLLOW_GROW, HOLLOW_SLOPE, HOLLOW_MIN = (2.4, 5.6), 1.35, 1.3, 3
JAG, JAG_FLOOR, DEEP = 0.7, 0.8, 1.6
CRACKS = [[(16.0, 23.0), (17.6, 27.4), (16.6, 31.6), (18.3, 35.6)],
          [(14.4, 35.2), (17.0, 39.0), (19.6, 42.4), (22.2, 45.6)],
          [(35.0, 45.8), (35.3, 50.0), (34.5, 54.2)],
          [(30.2, 23.2), (28.2, 27.8), (29.6, 32.6)],
          [(9.2, 32.8), (7.6, 37.8), (8.6, 43.2)],
          [(26.2, 8.8), (23.4, 14.2), (24.6, 18.0)]]
CRACK = (0.6, 2.2)
WRECK_CHIPS = (14, 8)            # chips broken off the upper drum's rims and corners, the head's lower rim
RUBBLE = [(15.5, 19.5, 1.5), (20.0, 22.0, 1.15), (11.2, 16.5, 0.95), (19.6, 36.4, 1.25), (28.6, 36.0, 1.05),
          (23.2, 55.0, 1.15), (39.2, 31.4, 1.0), (13.4, 52.0, 0.9)]
BREAK = [(24.0, 2.0), (47.5, 28.5)]
MATS = {"drum": 0xa7, "head": 0xad, "joint": 0x02, "gold": 0x1b, "quartz": 0xbf, "hollow": 0x61}


def art(text, base=None):
    """A picture's arrays (84 x 48): its shades (nan: none), its gold flecks, quartz and black (bools); rows the text
    leaves out are base's."""
    shade = np.full((84, 48), np.nan) if base is None else base[0].copy()
    flags = [np.zeros((84, 48), bool) for _ in range(3)] if base is None else [f.copy() for f in base[1:]]
    for i, line in enumerate(text.strip("\n").split("\n")):
        r = ART_TOP + i
        shade[r, :] = np.nan
        for f in flags:
            f[r, :] = False
        for c, ch in enumerate(line):
            if ch == ".":
                continue
            if ch == "Q":
                shade[r, c], flags[1][r, c] = 15.0, True
            elif ch == "G":
                shade[r, c], flags[0][r, c] = 9.0, True
            elif ch == "K":
                shade[r, c], flags[2][r, c] = 1.5, True
            else:
                shade[r, c] = int(ch, 16)
    return (shade, *flags)


def own_pixels(pic):
    return ~np.isnan(pic[0])


def morph(mask, size, grow):
    """A binary dilation (grow) or erosion of a picture's mask by a size x size square (numpy only)."""
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


def hollow_mask(pic, pic_dmg):
    """Where the broken look's hollows are: dark in the broken picture (ramp 6's black or shades 0-2) but not in the
    intact one (not its joints and edges), closed over a pixel, specks opened away; ramp 6's black always."""
    dark_b = (pic_dmg[3] | (pic_dmg[0] <= 2)) & ~np.isnan(pic_dmg[0])
    dark_a = (pic[0] <= 2) & ~np.isnan(pic[0])
    m = dark_b & ~dark_a
    m = morph(morph(m, 3, True), 3, False)
    m = morph(morph(m, 2, False), 2, True)
    return m | pic_dmg[3]


def components(mask):
    """The connected groups of a boolean picture's pixels (4-neighbours): lists of (row, column), largest first."""
    seen = np.zeros(mask.shape, bool)
    groups = []
    for r0, c0 in zip(*np.nonzero(mask)):
        if seen[r0, c0]:
            continue
        stack, group = [(r0, c0)], []
        seen[r0, c0] = True
        while stack:
            r, c = stack.pop()
            group.append((int(r), int(c)))
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                rr, cc = r + dr, c + dc
                if 0 <= rr < mask.shape[0] and 0 <= cc < mask.shape[1] and mask[rr, cc] and not seen[rr, cc]:
                    seen[rr, cc] = True
                    stack.append((rr, cc))
        groups.append(sorted(group))
    groups.sort(key=lambda g: (-len(g), g[0]))
    return groups


def pic_xy(c, r):
    """A point of the picture (column c, row r; pixel corners) in the model's plane."""
    return (c - 24.0, 42.0 - r)


# --- Solids ------------------------------------------------------------------------------------------------------------

def at(t, u, v):
    """The point of the column's frame: t along its axis from the foot ring, u across, v towards its front."""
    return Vector((X_AXIS + u, Y_FOOT + t * SA - v * CA, Z_FOOT + t * CA + v * SA))


def octagon(share=1.0, depth=RN, corner=CORNER):
    """The octagon's corners (u, v), counter-clockwise from the front face's right corner, each chamfered (two points
    `corner` along its faces)."""
    w, h = W_FRONT * share, H_SIDE * share * depth / RN
    rx, rn = RX * share, depth * share
    pts = [(w, rn), (-w, rn), (-rx, h), (-rx, -h), (-w, -rn), (w, -rn), (rx, -h), (rx, h)]
    if corner <= 0:
        return pts
    out = []
    for i, (u, v) in enumerate(pts):
        (pu, pv), (nu, nv) = pts[i - 1], pts[(i + 1) % len(pts)]
        for (au, av) in ((pu, pv), (nu, nv)):
            d = math.hypot(au - u, av - v)
            f = min(corner * share, d * 0.3) / d
            out.append((u + (au - u) * f, v + (av - v) * f))
    return out


def ring(t, share=1.0, depth=RN):
    return [at(t, u, v) for u, v in octagon(share, depth)]


class Rand:
    """A small deterministic random source (a linear congruential generator): the same numbers every run."""

    def __init__(self, seed):
        self.state = seed & 0x7FFFFFFF or 1

    def random(self):
        self.state = (1103515245 * self.state + 12345) & 0x7FFFFFFF
        return self.state / 0x7FFFFFFF

    def uniform(self, a, b):
        return a + (b - a) * self.random()


def hull(name, points, mat):
    """The convex hull of the points as a closed solid, its coplanar triangles merged into flat faces."""
    bm = bmesh.new()
    verts = [bm.verts.new(tuple(p)) for p in points]
    res = bmesh.ops.convex_hull(bm, input=verts, use_existing_faces=False)
    drop = list(dict.fromkeys(g for g in res["geom_interior"] + res["geom_unused"] if isinstance(g, bmesh.types.BMVert)))
    if drop:
        bmesh.ops.delete(bm, geom=drop, context="VERTS")
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(0.5), use_dissolve_boundaries=False, verts=bm.verts[:],
                             edges=bm.edges[:])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.data.materials.append(mat)
    return obj


def slice_off(obj, planes, mat_index=0):
    """Cuts away what lies beyond each plane (point, outward normal), the cuts closed flat (material slot mat_index)."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    for co, no in planes:
        if not bm.faces:
            break
        res = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-6, plane_co=co,
                                     plane_no=no, clear_outer=True)
        edges = [e for e in res["geom_cut"] if isinstance(e, bmesh.types.BMEdge) and e.is_valid]
        open_edges = [e for e in edges if len(e.link_faces) == 1]
        if open_edges:
            filled = bmesh.ops.holes_fill(bm, edges=open_edges, sides=0)
            for f in filled["faces"]:
                f.material_index = mat_index
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def chip(obj, rand, count, mat_index=0, depth=(0.45, 1.1)):
    """Chipped edges: flat cuts across `count` of the solid's sharper edges facing the camera (deterministic)."""
    mesh = obj.data
    edges = []
    for e in mesh.edges:
        a, b = mesh.vertices[e.vertices[0]].co, mesh.vertices[e.vertices[1]].co
        if (a - b).length < 1.2:
            continue
        mid = (a + b) / 2
        if mid.z < 2.0:
            continue
        edges.append((round(mid.x, 3), round(mid.y, 3), round(mid.z, 3), tuple(a), tuple(b)))
    edges.sort()
    if not edges:
        return obj
    centre = sum((v.co for v in mesh.vertices), Vector()) / len(mesh.vertices)
    planes = []
    for _ in range(count):
        mx, my, mz, a, b = edges[int(rand.random() * len(edges)) % len(edges)]
        a, b = Vector(a), Vector(b)
        p = a + (b - a) * rand.uniform(0.2, 0.8)
        out = (p - centre)
        out.x *= 0.6
        n = (out.normalized() + Vector((rand.uniform(-0.3, 0.3), rand.uniform(-0.3, 0.3), 0.35))).normalized()
        planes.append((p - n * rand.uniform(*depth), n))
    return slice_off(obj, planes, mat_index)


def drum(name, t0, t1, mat, rand):
    """A stone of the column: the octagon between two joints, its ends and corners chamfered, a little fuller in its
    middle (each face a few facets)."""
    length = t1 - t0
    pts = ring(t0, END[1]) + ring(t0 + END[0], 1.0) + ring(t1 - END[0], 1.0) + ring(t1, END[1])
    for f, share in ((0.3, (1.0 + BULGE) / 2), (0.5, BULGE), (0.7, (1.0 + BULGE) / 2)):
        pts += ring(t0 + length * f, share)
    return hull(name, pts, mat)


def plinth(mat, rand):
    """The foot: the lowest stone's base flaring forward (the sprites' foot ring reaching row 78 in the middle), and
    under its ring straight down to the ground (in the picture's plane: along the camera's line of sight once
    sheared, unseen)."""
    pts = []
    for t, share, depth in PLINTH:
        pts += ring(t, share, depth)
    foot = ring(0.0, 1.0, PLINTH[0][2])
    pts += [Vector((p.x, p.y, -SKIRT)) for p in foot if p.z > -SKIRT]
    obj = hull("plinth", pts, mat)
    return chip(obj, rand, 3)


def joint(name, t, mat):
    """The dark core showing in a joint between two stones."""
    return hull(name, ring(t - GAP - END[0] - 0.4, 0.9) + ring(t + GAP + END[0] + 0.4, 0.9), mat)


def head(mat, rand):
    """The pale head: the octagon over the upper joint narrowing into a rough dome, its facets the points of the
    dome jittered in (a convex hull: clean flat facets)."""
    pts = []
    for t, share in HEAD:
        pts += ring(t, share)
    t = T_CAP + DOME_STEP
    n = 0
    while t < T_END - 0.3:
        f = (t - T_CAP) / (T_END - T_CAP)
        share = HEAD[-1][1] * (1.0 - f ** DOME_POWER) ** (1.0 / DOME_POWER)
        for j in range(20):
            a = 2 * math.pi * (j + 0.5 * (n % 2)) / 20
            # the octagon rounding into a superellipse towards the top
            u, v = math.cos(a), math.sin(a)
            box = max(abs(u) / RX, abs(v) / RN)
            ru, rv = u / box, v / box
            blend = min(1.0, f * 1.6)
            q = (abs(u) ** 2.6 / RX ** 2.6 + abs(v) ** 2.6 / RN ** 2.6) ** (-1 / 2.6)
            ru, rv = (1 - blend) * ru + blend * u * q, (1 - blend) * rv + blend * v * q
            jit = 1.0 + rand.uniform(-ROUGH, 0.3) / (RN * max(share, 0.3))
            pts.append(at(t + rand.uniform(-0.45, 0.45), ru * share * jit, rv * share * jit))
        t += DOME_STEP
        n += 1
    pts.append(at(T_END, 0.0, 1.5))
    obj = hull("head", pts, mat)
    return chip(obj, rand, CHIPS)


def ray_down(objects):
    """hit(x, y): the topmost point of the objects over (x, y) of the picture's plane and its normal (pointing up),
    or None: what the camera sees there once sheared."""
    depsgraph = bpy.context.evaluated_depsgraph_get()
    trees = [BVHTree.FromObject(o, depsgraph) for o in objects]

    def hit(x, y):
        best = None
        for tree in trees:
            loc, nor, _, _ = tree.ray_cast(Vector((x, y, 200.0)), Vector((0, 0, -1)))
            if loc is not None and (best is None or loc.z > best[0].z):
                best = (loc, nor if nor.z > 0 else -nor)
        return best
    return hit


def gem(name, centre, normal, radius, height, mat, rand, sides=6, tip=0.0):
    """A small faceted stone set into the surface at centre (half sunk), standing along normal: gold nuggets (tip 0),
    quartz crystals (a pointed tip)."""
    n = Vector(normal).normalized()
    ref = Vector((1, 0, 0)) if abs(n.x) < 0.8 else Vector((0, 1, 0))
    a = n.cross(ref).normalized()
    b = n.cross(a).normalized()
    pts = []
    for level, scale in ((-0.6 * height, 0.9), (0.0, 1.0), (height * (0.6 if tip else 1.0), 0.75 if not tip else 0.9)):
        for j in range(sides):
            ang = 2 * math.pi * (j + rand.uniform(-0.2, 0.2)) / sides
            r = radius * scale * rand.uniform(0.8, 1.1)
            pts.append(Vector(centre) + n * level + (a * math.cos(ang) + b * math.sin(ang)) * r)
    if tip:
        pts.append(Vector(centre) + n * (height * (1.0 + tip)))
    return hull(name, pts, mat)


def details(look, stones, m, rand, hollows=None):
    """The gold flecks on the stones (nuggets where the picture's gold clusters are) and the quartz on the head
    (crystals where its white sparkles cluster)."""
    shade, gold, quartz, black = look
    hit = ray_down(stones)
    out = []
    for kind, mask, limit, min_px in (("gold", gold, 22, 1), ("quartz", quartz, 26, 2)):
        groups = [g for g in components(mask) if len(g) >= min_px][:limit]
        for i, g in enumerate(groups):
            r = sum(p[0] for p in g) / len(g) + 0.5
            c = sum(p[1] for p in g) / len(g) + 0.5
            if hollows is not None and hollows[max(0, int(r) - 1):int(r) + 2, max(0, int(c) - 1):int(c) + 2].any():
                continue
            x, y = pic_xy(c, r)
            h = hit(x, y)
            if h is None:
                continue
            loc, nor = h
            if kind == "gold":
                size = 0.55 + 0.12 * min(len(g), 4)
                out.append(gem("gold_%d" % i, loc, nor, size, 0.45, m["gold"], rand, 5))
            else:
                for j in range(1 + (len(g) > 4)):
                    tilt = Vector((rand.uniform(-0.45, 0.45), rand.uniform(-0.45, 0.45), 0.0))
                    off = Vector((rand.uniform(-0.6, 0.6), rand.uniform(-0.6, 0.6), 0.0)) * j
                    h2 = hit(x + off.x, y + off.y) or h
                    out.append(gem("quartz_%d_%d" % (i, j), h2[0], (h2[1] + tilt).normalized(), 0.48, 0.42,
                                   m["quartz"], rand, 6, tip=0.45))
    return out


def canonical(obj):
    """Rebuilds the object's mesh in a fixed order (its vertices by position, each face starting at its smallest
    corner, the faces by their corners; polish_powerups_specials.canonical): the exact boolean returns its result in
    an order that changes from run to run."""
    me = obj.data

    def key(co):
        return (round(co.x, 5), round(co.y, 5), round(co.z, 5))
    faces = []
    for poly in me.polygons:
        corners = [key(me.vertices[i].co) for i in poly.vertices]
        start = corners.index(min(corners))
        faces.append((corners[start:] + corners[:start], poly.material_index))
    faces.sort()
    verts = sorted({c for corners, _ in faces for c in corners})
    index = {c: i for i, c in enumerate(verts)}
    mesh = bpy.data.meshes.new(me.name)
    mesh.from_pydata(verts, [], [[index[c] for c in corners] for corners, _ in faces])
    mesh.validate()
    for mat in me.materials:
        mesh.materials.append(mat)
    for poly, (_, material) in zip(mesh.polygons, faces):
        poly.material_index = material
    obj.data = mesh
    bpy.data.meshes.remove(me)
    return obj


def jitter(x, y, seed):
    """A deterministic number in [0, 1) for a point (a hash of its coordinates)."""
    v = math.sin(x * 12.9898 + y * 78.233 + seed * 37.719) * 43758.5453
    return v - math.floor(v)


def grow_loop(loop, amount, jag=0.0, seed=0):
    """A loop moved out along its normals (it runs counter-clockwise round its inside), each point by amount plus up to
    jag either way."""
    n = len(loop)
    out = []
    for i in range(n):
        (x0, y0), (x1, y1), (x2, y2) = loop[i - 1], loop[i], loop[(i + 1) % n]
        tx, ty = x2 - x0, y2 - y0
        length = math.hypot(tx, ty) or 1.0
        a = amount + (jitter(x1, y1, seed) - 0.5) * 2.0 * jag
        out.append((x1 + ty / length * a, y1 - tx / length * a))
    return out


def crosses(poly):
    """Whether a closed polygon's edges cross each other (segments that do not share a corner)."""
    n = len(poly)

    def ccw_(a, b, c):
        return (c[1] - a[1]) * (b[0] - a[0]) - (b[1] - a[1]) * (c[0] - a[0])
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        for j in range(i + 2, n):
            if i == 0 and j == n - 1:
                continue
            c, d = poly[j], poly[(j + 1) % n]
            if (ccw_(a, b, c) > 0) != (ccw_(a, b, d) > 0) and (ccw_(c, d, a) > 0) != (ccw_(c, d, b) > 0):
                return True
    return False


def safe_grow(loop, amount, jag, seed):
    """The loop resampled evenly and grown (grow_loop), with less jitter and growth until its edges do not cross."""
    pts = resample(loop, 1.05)
    if area(pts) < 0:
        pts.reverse()
    for f in (1.0, 0.5, 0.25, 0.0):
        poly = grow_loop(pts, amount * (0.5 + 0.5 * f), jag * f, seed)
        if not crosses(poly):
            return poly
    return pts


def funnel(name, poly, depth, slope, hit, z_miss, mat, seed, spacing=0.5, jag_floor=JAG_FLOOR):
    """A cutter over a polygon of the picture's plane: from far above down to a floor that starts just over the
    stone's surface at the polygon's edge and slopes in under it (slope per pixel in from the edge) to depth, its points
    jittered (broken faces). Built as a relief standing on its head (polish_ring_machine.relief), then turned over."""
    def height(x, y, d):
        h = hit(x, y)
        zs = h[0].z if h is not None else z_miss
        sink = min(depth, slope * d) + (jitter(x, y, seed) - 0.5) * jag_floor * min(1.0, d)
        return -(zs + 0.3 - sink)
    obj = relief(name, [poly], height, {"hollow": mat}, paint=lambda x, y, d: "hollow", side="hollow",
                 bottom=-60.0 - 0.37 * (seed % 17), spacing=spacing, smooth_angle=0.0)
    obj.data.transform(Matrix.Scale(-1.0, 4, (0.0, 0.0, 1.0)))
    k.recalc_normals(obj)
    return obj


def hollow_cutters(black, hit, mat):
    """The broken picture's dark regions as jagged cavities (funnels over their outlines grown by HOLLOW_GROW)."""
    out = []
    for n, g in enumerate(components(black)):
        if len(g) < HOLLOW_MIN:
            continue
        mask = np.zeros(black.shape, bool)
        for r, c in g:
            mask[r, c] = True
        depth = HOLLOW_DEPTH[0] + (HOLLOW_DEPTH[1] - HOLLOW_DEPTH[0]) * min(1.0, len(g) / 60.0)
        rs = [p_[0] for p_ in g]
        cs = [p_[1] for p_ in g]
        fallback = hit(*pic_xy(sum(cs) / len(cs) + 0.5, sum(rs) / len(rs) + 0.5))
        z_miss = fallback[0].z if fallback is not None else 0.0
        for i, loop in enumerate(mask_loops(mask, -24.0, 42.0, chaikin=1, sigma=0.7)):
            if area(loop) < 1.5:
                continue
            poly = safe_grow(loop, HOLLOW_GROW, JAG, 7 * n + i)
            spacing = 0.72 if len(g) < 80 else 0.78
            out.append(funnel("hollow_%d_%d" % (n, i), poly, depth, HOLLOW_SLOPE, hit, z_miss, mat, 11 + n, spacing))
    return out


def crack_cutters(hit, mat):
    """The cracks: V grooves along CRACKS, their edges jagged, deepest along the middle."""
    half, depth = CRACK
    out = []
    for n, pts in enumerate(CRACKS):
        line = [pic_xy(c, r) for c, r in pts]
        dense = []
        for (x0, y0), (x1, y1) in zip(line, line[1:]):
            steps = max(1, int(math.hypot(x1 - x0, y1 - y0) / 0.7))
            dense += [(x0 + (x1 - x0) * t / steps, y0 + (y1 - y0) * t / steps) for t in range(steps)]
        dense.append(line[-1])
        left, right = [], []
        for i, (x, y) in enumerate(dense):
            (xa, ya), (xb, yb) = dense[max(0, i - 1)], dense[min(len(dense) - 1, i + 1)]
            tx, ty = xb - xa, yb - ya
            length = math.hypot(tx, ty) or 1.0
            nx, ny = -ty / length, tx / length
            taper = min(1.0, i / 2.0, (len(dense) - 1 - i) / 2.0) * 0.7 + 0.3
            w = half * taper * (0.75 + 0.5 * jitter(x, y, 90 + n))
            left.append((x + nx * w, y + ny * w))
            right.append((x - nx * w, y - ny * w))
        poly = left + right[::-1]
        if area(poly) < 0:
            poly.reverse()
        if crosses(poly):
            continue
        h = hit(*dense[len(dense) // 2])
        z_miss = h[0].z if h is not None else 0.0
        out.append(funnel("crack_%d" % n, poly, depth, depth / half * 1.1, hit, z_miss, mat, 120 + n, spacing=0.42,
                          jag_floor=0.4))
    return out


def chip_cutters(mat, rand):
    """Chips broken off the edges: small faceted lumps cut out where the upper drum's front rims meet its chamfers,
    down its octagon's corners, and along the head's lower rim (their faces the stone's own: a marker material)."""
    spots = []
    t_lo, t_hi = J1 + GAP + END[0], J2 - GAP - END[0]
    for _ in range(WRECK_CHIPS[0]):
        side = rand.random()
        if side < 0.35:
            spots.append((t_lo, rand.uniform(-RX * 0.95, RX * 0.95)))
        elif side < 0.7:
            spots.append((t_hi, rand.uniform(-RX * 0.95, RX * 0.95)))
        else:
            spots.append((rand.uniform(t_lo, t_hi), W_FRONT * (1 if rand.random() < 0.5 else -1)))
    for _ in range(WRECK_CHIPS[1]):
        spots.append((J2 + GAP + END[0], rand.uniform(-RX * 0.9, RX * 0.9)))
    out = []
    for i, (t, u) in enumerate(spots):
        # the octagon's surface point over u (the front face, or the corner faces beyond W_FRONT)
        au = abs(u)
        if au <= W_FRONT:
            v = RN
        else:
            v = RN - (RN - H_SIDE) * (au - W_FRONT) / (RX - W_FRONT)
        centre = at(t, u, v)
        size = rand.uniform(0.9, 1.7)
        pts = []
        for j in range(9):
            a = 2 * math.pi * (j + rand.uniform(-0.3, 0.3)) / 9
            el = rand.uniform(-1.2, 1.2)
            rr = size * rand.uniform(0.7, 1.15)
            pts.append(centre + Vector((rr * math.cos(a) * math.cos(el), rr * math.sin(a) * math.cos(el),
                                        rr * math.sin(el))))
        out.append(hull("chip_%d" % i, pts, mat))
    return out


def rubble(stones, m, rand):
    """Broken chunks lying on the broken column where they fell (RUBBLE), each the stone under it, faceted."""
    depsgraph = bpy.context.evaluated_depsgraph_get()
    trees = [(BVHTree.FromObject(o, depsgraph), o) for o in stones]
    out = []
    for i, (c, r, size) in enumerate(RUBBLE):
        x, y = pic_xy(c, r)
        best = None
        for tree, o in trees:
            loc, nor, _, _ = tree.ray_cast(Vector((x, y, 200.0)), Vector((0, 0, -1)))
            if loc is not None and (best is None or loc.z > best[0].z):
                best = (loc, nor if nor.z > 0 else -nor, o)
        if best is None:
            continue
        loc, nor, o = best
        centre = loc + nor * size * 0.45
        pts = []
        for j in range(11):
            a = 2 * math.pi * (j + rand.uniform(-0.3, 0.3)) / 11
            el = rand.uniform(-0.9, 0.9)
            rr = size * rand.uniform(0.65, 1.1)
            pts.append(centre + Vector((rr * math.cos(a) * math.cos(el), rr * math.sin(a) * math.cos(el),
                                        rr * 0.7 * math.sin(el))))
        mat = m["drum"] if o.name.startswith("joint") or not o.data.materials else o.data.materials[0]
        chunk = hull("rubble_%d" % i, pts, mat)
        out.append(chunk)
    return out


def cutter_break(name, z_top, mat, rand):
    """The head's top right broken away: three faceted wedges beyond the broken outline (column 25 of row 3 to column
    46 of row 28), their faces (the fracture) the stone's own (a marker material, replaced by each part's)."""
    (c0, r0), (c1, r1) = BREAK
    out = []
    for i in range(3):
        f0, f1 = i / 3 - (0.35 if i == 0 else 0.04), (i + 1) / 3 + (0.35 if i == 2 else 0.04)
        a = Vector(pic_xy(c0 + (c1 - c0) * f0, r0 + (r1 - r0) * f0) + (0.0,))
        b = Vector(pic_xy(c0 + (c1 - c0) * f1, r0 + (r1 - r0) * f1) + (0.0,))
        side = Vector((-(b.y - a.y), b.x - a.x, 0.0)).normalized()     # towards the upper right
        jag = rand.uniform(-1.0, 1.0)
        pts = []
        for p in (a, b):
            for dz, inset in ((z_top + 4.0, 1.6 + jag), (z_top * 0.6, -0.3), (-SKIRT - 1.0, -1.2)):
                q = p - side * inset
                pts.append(Vector((q.x, q.y, dz)))
                q2 = p + side * 24.0
                pts.append(Vector((q2.x, q2.y, dz)))
        out.append(hull("%s_%d" % (name, i), pts, mat))
    return out


def materials():
    pal = k.level_palette()

    def m(name, idx, metallic, roughness, glow=0.0):
        extra = dict(emission=pal[idx], emission_strength=glow) if glow else {}
        return k.material("column_" + name, palette=idx, metallic=metallic, roughness=roughness, **extra)
    return {"drum": m("drum", MATS["drum"], 0.0, 0.85), "head": m("head", MATS["head"], 0.0, 0.8),
            "joint": m("joint", MATS["joint"], 0.1, 0.9), "gold": m("gold", MATS["gold"], 0.6, 0.32, 0.12),
            "quartz": m("quartz", MATS["quartz"], 0.1, 0.22, 0.18), "hollow": m("hollow", MATS["hollow"], 0.0, 1.0),
            "marker": m("marker", MATS["drum"], 0.0, 0.85)}


def build_column(m, look, broken, hollows=None):
    """The column (or its broken look: hollows its mask) as its parts, in the picture's plane: [object, ...]."""
    rand = Rand(7)
    lower = drum("drum_low", PLINTH[-1][0] - 1.5, J1 - GAP, m["drum"], rand)
    foot = plinth(m["drum"], rand)
    upper = drum("drum_up", J1 + GAP, J2 - GAP, m["drum"], rand)
    top = head(m["head"], rand)
    cores = [joint("joint_1", J1, m["joint"]), joint("joint_2", J2, m["joint"])]
    stones = [lower, foot, upper, top]
    for obj in stones + cores:
        slice_off(obj, [(Vector((0, 0, -SKIRT)), Vector((0, 0, -1)))])
    bpy.context.view_layer.update()
    rand_d = Rand(11)
    if broken:
        hit = ray_down([upper, top] + cores)
        z_top = max(v.co.z for v in top.data.vertices)
        cutters = (hollow_cutters(hollows, hit, m["hollow"]) + crack_cutters(hit, m["hollow"]) +
                   cutter_break("break", z_top, m["marker"], Rand(53)) + chip_cutters(m["marker"], Rand(61)))
        cutter = join(cutters, "cutter")
        mesh = cutter.data
        names = [mt.name for mt in mesh.materials]
        deep = []
        for poly in mesh.polygons:
            c = poly.center
            h = hit(c.x, c.y)
            zs = h[0].z if h is not None else c.z
            deep.append(names[poly.material_index] == m["hollow"].name and zs - c.z > DEEP)
        for obj in [top, upper] + cores:
            tool = cutter.copy()
            tool.data = cutter.data.copy()
            bpy.context.scene.collection.objects.link(tool)
            tool.hide_render = True
            # the broken faces the part's own stone, the holes' deep insides dark
            tool.data.materials.clear()
            tool.data.materials.append(obj.data.materials[0])
            tool.data.materials.append(m["hollow"])
            tool.data.polygons.foreach_set("material_index", [1 if d else 0 for d in deep])
            mod = obj.modifiers.new("boolean", "BOOLEAN")
            mod.operation = "DIFFERENCE"
            mod.solver = "EXACT"
            mod.material_mode = "TRANSFER"
            mod.use_self = True
            mod.object = tool
            mk.apply(obj)
            data = tool.data
            bpy.data.objects.remove(tool)
            bpy.data.meshes.remove(data)
            canonical(obj)
            bm = bmesh.new()
            bm.from_mesh(obj.data)
            bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method="FIXED", ngon_method="EAR_CLIP")
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
            bad = sum(1 for e in bm.edges if not e.is_manifold)
            bm.to_mesh(obj.data)
            bm.free()
            if bad:
                print("  %s: %d non-manifold edges after the cuts" % (obj.name, bad))
        data = cutter.data
        bpy.data.objects.remove(cutter)
        bpy.data.meshes.remove(data)
        bpy.context.view_layer.update()
        stones = stones + rubble([top, upper] + cores, m, Rand(71))
    extra = details(look, [lower, upper, top], m, rand_d, hollows)
    return stones + cores + extra


# --- Shared with polish_lander.py, polish_tan_dome.py and polish_miners_rig.py (round 35's, unchanged) ---------

def shear_to_camera(obj, sign=-1.0):
    """Moves every point along the camera's line of sight: y - z tan 20 (sign -1; +1 undoes it)."""
    mesh = obj.data
    co = np.empty(3 * len(mesh.vertices))
    mesh.vertices.foreach_get("co", co)
    co = co.reshape(-1, 3)
    co[:, 1] += sign * TILT * co[:, 2]
    mesh.vertices.foreach_set("co", co.ravel())
    mesh.update()


def cut_piece(whole, box, name, cap_mat):
    """The part of the (sheared) whole the camera sees in a sprite's box (x0, x1, y0, y1 in the picture's plane; None:
    open): cut by x = x0, x1 and the planes y + tan 20 z = y0, y1, the cuts closed (caps: material slot 1, facing out
    of the piece). Returns the object and its vertices on the cuts."""
    x0, x1, y0, y1 = box
    obj = whole.copy()
    obj.data = whole.data.copy()
    obj.name = obj.data.name = name
    bpy.context.scene.collection.objects.link(obj)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    lean = Vector((0.0, 1.0, TILT)).normalized()
    planes = []
    if x0 is not None:
        planes.append((Vector((x0, 0, 0)), Vector((-1, 0, 0))))
    if x1 is not None:
        planes.append((Vector((x1, 0, 0)), Vector((1, 0, 0))))
    if y0 is not None:
        planes.append((Vector((0, y0, 0)), -lean))
    if y1 is not None:
        planes.append((Vector((0, y1, 0)), lean))
    for co, no in planes:
        if not bm.faces:
            break
        res = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-6, plane_co=co,
                                     plane_no=no, clear_outer=True)
        edges = [e for e in res["geom_cut"] if isinstance(e, bmesh.types.BMEdge) and e.is_valid]
        open_edges = [e for e in edges if len(e.link_faces) == 1]
        if open_edges:
            filled = bmesh.ops.holes_fill(bm, edges=open_edges, sides=0)
            if filled["faces"]:
                for f in bmesh.ops.triangulate(bm, faces=filled["faces"])["faces"]:
                    f.normal_update()
                    if f.normal.dot(no) < 0:
                        f.normal_flip()
    if not bm.faces:
        bm.free()
        bpy.data.objects.remove(obj)
        return None, set()

    def on_plane(co):
        dist = [abs(co.x - x0) if x0 is not None else 9.0, abs(co.x - x1) if x1 is not None else 9.0]
        yv = co.y + TILT * co.z
        dist += [abs(yv - y0) if y0 is not None else 9.0, abs(yv - y1) if y1 is not None else 9.0]
        return min(dist) < 1e-4
    bm.normal_update()
    bm.verts.index_update()
    rim = {v.index for v in bm.verts if on_plane(v.co)}
    for f in bm.faces:
        cap = all(v.index in rim for v in f.verts) and (abs(f.normal.x) > 0.999 or abs(f.normal.dot(lean)) > 0.999)
        f.material_index = 1 if cap else 0
        if cap:
            f.smooth = False
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.materials.clear()
    obj.data.materials.append(cap_mat)
    obj.data.materials.append(cap_mat)
    return obj, rim


def view_coverage(objects, w, h, centre):
    """What the game's camera sees of the objects, in the picture's pixels (a w x h window round centre): their top
    view with the shear undone (on copies, so the output does not depend on --check)."""
    copies = []
    for obj in objects:
        c = obj.copy()
        c.data = obj.data.copy()
        bpy.context.scene.collection.objects.link(c)
        shear_to_camera(c, +1.0)
        copies.append(c)
    covered = mk.coverage(copies, w, h, centre=centre)
    for c in copies:
        data = c.data
        bpy.data.objects.remove(c)
        bpy.data.meshes.remove(data)
    return covered


def drop_islands(verts, quads, keep_share=0.05):
    """The surface nets' quads without the small pieces lying apart from the column (crumbs the broken look leaves)."""
    parent = np.arange(len(verts))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    for q in quads:
        roots = [find(int(v)) for v in q]
        r0 = min(roots)
        for r in roots:
            parent[r] = r0
    roots = np.array([find(int(q[0])) for q in quads])
    labels, counts = np.unique(roots, return_counts=True)
    keep = set(labels[counts >= keep_share * counts.max()].tolist())
    return quads[np.isin(roots, list(keep))]


def column_cut(obj, box, name):
    """The part of an object the camera sees in a sprite's box (x0, x1, y0, y1 in the picture's plane; None: open),
    cut there in the picture's plane (before the shear: the planes are the camera's lines of sight once sheared), the
    cuts closed in the part's own material."""
    x0, x1, y0, y1 = box
    planes = []
    if x0 is not None:
        planes.append((Vector((x0, 0, 0)), Vector((-1, 0, 0))))
    if x1 is not None:
        planes.append((Vector((x1, 0, 0)), Vector((1, 0, 0))))
    if y0 is not None:
        planes.append((Vector((0, y0, 0)), Vector((0, -1, 0))))
    if y1 is not None:
        planes.append((Vector((0, y1, 0)), Vector((0, 1, 0))))
    lo, hi = mk.bounds([obj])
    if ((x0 is not None and hi.x <= x0) or (x1 is not None and lo.x >= x1) or (y0 is not None and hi.y <= y0) or
            (y1 is not None and lo.y >= y1)):
        return None
    piece = obj.copy()
    piece.data = obj.data.copy()
    piece.name = name
    bpy.context.scene.collection.objects.link(piece)
    slice_off(piece, planes, 0)
    if not piece.data.polygons:
        bpy.data.objects.remove(piece)
        return None
    return piece


def export_pieces(parts, pieces, look, options, out, label):
    own = own_pixels(look)
    for name, sprite, box, centre in pieces:
        cuts = []
        for obj in parts:
            c = column_cut(obj, box, obj.name + "_" + name)
            if c is not None:
                cuts.append(c)
        for obj in parts:
            obj.hide_render = True
        if "check" in options:
            c0, r0 = int(centre[0] - 12 + 24), int(42 - centre[1] - 14)
            mask = own[r0:r0 + 28, c0:c0 + 24].tolist()
            mk.compare("%s (M %d) as the camera sees it, its sprite's own pixels" % (name, sprite),
                       mk.coverage(cuts, 24, 28, centre=centre), mask)
        for c in cuts:
            shear_to_camera(c)
        mk.transform(cuts, Matrix.Translation((-centre[0], -centre[1], 0.0)))
        bpy.context.view_layer.update()
        triangulate(cuts)
        obj = join(cuts, name)
        obj.data.name = name
        # Flat facets, the hollows' floors smooth (bowls).
        hollow = {i for i, mt in enumerate(obj.data.materials) if mt is not None and mt.name.startswith("column_hollow")}
        obj.data.polygons.foreach_set("use_smooth", [p_.material_index in hollow for p_ in obj.data.polygons])
        obj.data.update()
        mk.report(name, [obj], os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, [obj], size=(24, 56), scale=12, centre=(0.0, -10.0))
        bpy.data.objects.remove(obj)
        for p in parts:
            p.hide_render = False


def build():
    options = k.args()
    out = mk.outdir(options)
    only = set(options["only"].split(",")) if "only" in options else None
    k.reset()
    bpy.context.scene.view_settings.view_transform = "Standard"
    m = materials()
    pic = art(ART)
    pic_dmg = art(ART_DMG, base=pic)
    jobs = [("rock_column", pic, False, [(name, sprite, box, centre) for name, sprite, _, box, centre in PIECES
                                         if not only or name in only]),
            ("rock_column_wreck", pic_dmg, True, [(dmg[0], dmg[1], box, centre) for _, _, dmg, box, centre in PIECES
                                                  if dmg and (not only or dmg[0] in only)])]
    for label, look, broken, pieces in jobs:
        if not pieces and "whole" not in options:
            continue
        parts = build_column(m, look, broken, hollow_mask(pic, pic_dmg) if broken else None)
        print("%s: %d parts, %d triangles" % (label, len(parts), mk.triangles(parts)))
        if "check" in options:
            mk.compare("whole %s as the camera sees it (the ground left out)" % label,
                       mk.coverage(parts, 48, 84, (0.0, 0.0)), own_pixels(look).tolist())
        if "whole" in options:
            view = []
            for p in parts:
                c = p.copy()
                c.data = p.data.copy()
                bpy.context.scene.collection.objects.link(c)
                shear_to_camera(c)
                view.append(c)
            for p in parts:
                p.hide_render = True
            mk.preview(options["whole"] + label, view, size=(48, 84), scale=8, distance=1.4)
            for c in view:
                bpy.data.objects.remove(c)
            for p in parts:
                p.hide_render = False
        export_pieces(parts, pieces, look, options, out, label)
        for p in parts:
            bpy.data.objects.remove(p)


if __name__ == "__main__":
    build()
