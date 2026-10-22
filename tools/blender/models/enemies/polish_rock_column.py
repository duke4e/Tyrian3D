"""MINERS's banded rock column and its broken look (sheet M sprites 163 165 above 201 203 above 239 241, 2x2 each: one
48 x 84 picture; the broken look 167 169 above 205 207 in the upper four's places; enemies 1191-1196 of episode 5,
ground layers, armour 30, worth 10 each), polished (2026-10-22, round 35; it replaces wave3_ah_rock.py, an octagonal
pillar leaning up the screen built as a heightfield on its own frame, painted by the sprite's ramps, and its broken
look cut out of it). models.cfg: model rock_column_tl / _tr / _ml / _mr / _bl / _br and rock_column_wreck_tl / _tr /
_ml / _mr ... origin (unchanged); every sprite line gets height=-4.

Where the level puts it (the level events, tools/content/tyrevents.py; the enemy data, tools/content/tyrdata.py):
MINERS builds the column five times (t468 at column 3, t1140 at 10, t1196 at 9, t3632 at 6, t4276 at 7), each time
from six ground enemies with one link: 1195 (239) at (x, y) and 1196 (241) at x + 24 on the ground layer, 1193 (201)
and 1194 (203) 28 pixels up the screen and 1191 (163) and 1192 (165) 56 pixels up (d5 -29 and -57) on ground 2: the
sheet's picture whole. Always on the map's row above tiles of its own: the map paints the column's broken stump (the
lower drum shattered) in the tile row under 239 and 241. Shot, the six go together (one link): the upper four turn to
their broken looks (dgr 167 169 205 207, dlevel -1: they stay), the lower two die (the game leaves its slumped wrecks
of their models over the painted stump). No other enemy, launched ones included, shows these sprites; none is another
sprite's pixels mirrored, turned or in other ramps; no episode 6 level places the column.

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

Built as such a column, for the game's camera: designed in the picture's plane (x, y as the picture draws them, z up,
the camera looking straight down) and then sheared along the game camera's line of sight (y - z tan 20:
polish_lava_grub.py's and polish_red_mound.py's way), so that the camera sees every point where the picture draws it.
In the picture's plane the column leans back LEAN (72) degrees from upright about its foot, so that the camera sees its
drums nearly face on and their joints as the flat arcs the sprites draw (a ring of the column shows RN cos LEAN = 5.6
rows deeper at its front than at its sides); the joints lie where the sprites draw them at the column's sides (rows 69.5,
50, 31 and the head's rim at row 20: T_JOINTS, T_CAP along its axis); the head's dome reaches the picture's row 2
(DOME). The column's foot stands on the ground: under its lowest ring its sides go straight down to the ground in the
picture's plane (along the camera's line of sight once sheared: unseen), so that the camera sees the foot's edge where
the sprites draw it and nothing under it. After the shear the column leans back about 73 degrees from upright (from
the side a thick pillar lying back on the sand), its head 36 pixels over the ground. It is a signed distance field on a
grid H pixels apart (polish_rock_arch.py's surface nets, as polish_red_spire.py's and polish_red_mound.py's rocks): an
octagonal prism (RX across, RN deep, its front face W_FRONT wide) with rounded edges, the joints sunk GROOVE deep round
it, the head rounding from the octagon into an ellipsoid dome; the picture's fine shading as relief (lumps where it is
light, pits where it is dark: the drums' mottling), smooth noise, rougher on the head. Its colours are the picture's own
shades under each face (the faces' points taken back into the picture's plane): the broad shading kept in part round MID
(KEEP: the game's sun shades it), the fine shading kept, grained a little; the gold flecks 0x19 and the quartz 0xbf
where the picture has them; the undersides dark. The broken look is the same column with the hollows carved out of it
down the camera's line of sight (as deep as the picture's black is dark, up to HOLLOW_DEPTH under the surface) and the
head's top right broken away (everything the camera would see outside the broken outline removed, its edge sloping in
as a fracture face), painted from the broken pictures (the hollows 0x61 / 0x64 by the light, their lips dark).

The whole is cut along the planes the camera sees as the sprites' edges (x = 0; y + tan 20 z = 14 and -14, leaning
back up the screen: polish_stone_face.view_cut's planes), so that each piece holds what the camera sees in its sprite
(the upper pieces the head, which stands over the middle pieces once sheared), the cuts capped with the stone's inside
(CAP; they show only through gaps: the pieces stand together); each piece's triangles reduced to TARGET with its cut's
vertices kept (polish_rock_arch.decimate) and its normals those of the dense whole (shade_like), so the pieces meet
exactly and shade as one column; each moved so that its sprite's centre is its origin, triangulated
(polish_k_pod.triangulate). The broken pieces are cut the same way (only the upper four are exported).

Coordinates: 1 unit = 1 game pixel; +X right, +Y up the screen, +Z up from the ground (z = 0); the whole's origin is
the picture's middle (the corner where 201 and 203 meet, half way down): column c of the picture is x = c + 0.5 - 24,
row r is y = 41.5 - r. The pieces' centres: 163 (-12, 28), 165 (12, 28), 201 (-12, 0), 203 (12, 0), 239 (-12, -28),
241 (12, -28). Drawn at their origins (origin) on the ground layers: height=-4 sets the column on the terrain (the game
lifts pieces side by side moving alike together, to the terrain under their middle; MINERS's ground is level there).

Replaces wave3_ah_rock.py (all of it: the column and its broken look were all it built). With wave3_ah.py
(polish_miners_machines.py, polish_block_rubble.py) and wave3_ah_rig.py (polish_miners_rig.py) gone too, nothing
imports wave3_ah_kit.py or its pixels, wave3_ah_art.py (the column's ROCK and ROCK_WRECK among them): both go.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the whole's and each piece's
silhouette as the camera sees it against the sprites' own pixels, the ground they paint left out), --preview <prefix>,
--whole <prefix> (the uncut column and its broken look: views and GLBs), --only <name,...>.
"""
import math
import os
import sys
import time

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
from polish_rock_arch import (surface_nets, finish_whole, mesh_object, noise3, smax, fill_outside, face_data,  # noqa: E402
                              assign, decimate, shade_like)
from polish_k_pod import triangulate  # noqa: E402

TILT = math.tan(math.radians(20.0))     # the camera shows a point this much further up the screen per pixel up
LIGHT = Vector((-0.55, 0.45, 0.7)).normalized()

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
FLARE, FLARE_T = 8.0, 7.0               # the foot flares forward (deeper by FLARE at the foot ring, over FLARE_T)
# Along its axis (pixels from the foot ring): the joints' middles (the sprites' rows 69.5, 50 and 31 at its sides) and
# the head's rim (row 20); the head's boss over it, narrowing from the rim to its top (S_RIM, S_TOP of the octagon),
# its top face's middle drawn at row 7.4 (T_TOP), bulging BULGE, its edge rounded over ROUND.
T_JOINTS = [0.0, 19.5 / SA, 38.5 / SA]
T_CAP = 49.5 / SA
T_TOP = (69.5 - 7.4) / SA
S_RIM, S_TOP, BULGE, ROUND = 0.935, 0.78, 1.6, 2.6
GROOVE, GROOVE_W, GROOVE_EDGE = 2.0, 1.3, 1.4       # the joints: depth, half width, the drums' rounded edges
FOOT_W = 0.6                            # the foot ring's joint is narrower (the drum's lower edge)
SKIRT = 1.5                             # how far the column reaches under the ground
# The relief from the picture's fine shading, the noise ((amplitude, scale)), on the drums and on the head.
RELIEF_DRUM, RELIEF_HEAD = 0.1, 0.45
NOISE_DRUM = ((0.08, 2.4), (0.03, 1.0))
NOISE_HEAD = ((0.3, 3.0), (0.12, 1.2))
# The broken look: how deep the hollows go under the surface (where the picture is black), how far in the broken top
# right's fracture face reaches over its height.
HOLLOW_DEPTH = 4.2
FRACTURE_DEPTH = 4.5

# The grid (the picture's plane).
H = 0.35
X0, NX = -25.2, 146
Y0, NY = -37.0, 230
Z0, NZ = -2.8, 124
XS = X0 + H * np.arange(NX)
YS = Y0 + H * np.arange(NY)
ZS = Z0 + H * np.arange(NZ)

# The colours: the share of the picture's broad shading kept (round MID), the fine shading's weight, the grain.
MID, KEEP, DETAIL, DITHER = 8.6, 0.65, 1.3, 0.35
CAP = 0xa5
GOLD, QUARTZ = 0x19, 0xbf
JOINT = 0x01
HOLLOW_DARK, HOLLOW_LIT = JOINT, 0x62
TARGET = 5600


def smoothstep(e0, e1, x):
    t = np.clip((np.asarray(x, dtype=np.float64) - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


# --- The picture ------------------------------------------------------------------------------------------------------

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


def sample(a, x, y, pad=0.0):
    """Bilinear sample of a pixel array a[row, column] of the picture (values at the pixels' centres)."""
    rows, cols = a.shape
    u, v = x + 24.0 - 0.5, 41.5 - y
    c0, r0 = np.floor(u).astype(int), np.floor(v).astype(int)
    fu, fv = u - c0, v - r0

    def at(r, c):
        ok = (r >= 0) & (r < rows) & (c >= 0) & (c < cols)
        return np.where(ok, a[np.clip(r, 0, rows - 1), np.clip(c, 0, cols - 1)], pad)
    return ((1 - fu) * (1 - fv) * at(r0, c0) + fu * (1 - fv) * at(r0, c0 + 1) + (1 - fu) * fv * at(r0 + 1, c0) +
            fu * fv * at(r0 + 1, c0 + 1))


def blur(a, sigma):
    """A Gaussian blur (sigma in pixels) of a field on the grid's x, y."""
    s = sigma / H
    r = int(math.ceil(3 * s))
    kernel = np.exp(-0.5 * (np.arange(-r, r + 1) / s) ** 2)
    kernel /= kernel.sum()
    out = a
    for axis in (0, 1):
        pad = [(0, 0), (0, 0)]
        pad[axis] = (r, r)
        p = np.pad(out, pad, mode="edge")
        acc = np.zeros_like(out)
        for i, w in enumerate(kernel):
            acc += w * (p[i:i + out.shape[0], :] if axis == 0 else p[:, i:i + out.shape[1]])
        out = acc
    return out


def sample_grid(a, x, y):
    """Bilinear sample of a field on the grid's x, y."""
    u = np.clip((x - X0) / H, 0.0, NX - 1.001)
    v = np.clip((y - Y0) / H, 0.0, NY - 1.001)
    i, j = np.floor(u).astype(int), np.floor(v).astype(int)
    fu, fv = u - i, v - j
    return (a[i, j] * (1 - fu) * (1 - fv) + a[i + 1, j] * fu * (1 - fv) + a[i, j + 1] * (1 - fu) * fv +
            a[i + 1, j + 1] * fu * fv)


def paint_fields(pic):
    """The picture's colours on the grid's x, y: the shade to paint (broad shading kept in part, the fine kept), the
    gold flecks', the quartz's and the black hollows' masks, the fine relief, the column's own pixels."""
    shade, gold, quartz, black = pic
    own = own_pixels(pic)
    filled = fill_outside(shade)
    gx, gy = np.meshgrid(XS, YS, indexing="ij")
    s_px = sample(filled, gx, gy)
    fine, mid, broad = blur(s_px, 0.5), blur(s_px, 1.6), blur(s_px, 4.5)
    local = blur(s_px, 0.6)
    paint = MID + (broad - MID) * KEEP + DETAIL * (local - broad)
    masks = {name: blur(sample(m.astype(np.float64), gx, gy), 0.35) for name, m in
             (("gold", gold), ("quartz", quartz), ("black", black))}
    mask = blur(sample(own.astype(np.float64), gx, gy), 0.4)
    return {"paint": paint, "relief": fine - mid, "mask": mask, **masks}


# --- The solid ------------------------------------------------------------------------------------------------------------

def octagon(u, v, rx=RX, rn=RN):
    """The octagon's distance (exact inside, a little short outside), u across, v front to back; rn may vary."""
    au, av = np.abs(u), np.abs(v)
    cx, cy = W_FRONT * rx / RX, rn                                   # the front face's corner
    ex, ey = rx, H_SIDE * rn / RN                                    # the side face's corner
    nx, ny = cy - ey, ex - cx                                        # the corner face's normal (before normalising)
    length = np.hypot(nx, ny)
    d = (nx * cx + ny * cy) / length
    return np.maximum(np.maximum(au - rx, av - rn), (nx * au + ny * av) / length - d)


def ellipse(u, v, rx=RX, rn=RN):
    return (np.sqrt((u / rx) ** 2 + (v / rn) ** 2) - 1.0) * np.minimum(rx, rn)


def joints(t):
    """How deep the joints sink the surface at axis position t."""
    g = np.zeros_like(t)
    for i, tj in enumerate(T_JOINTS):
        w = FOOT_W if i == 0 else GROOVE_W
        g = np.maximum(g, GROOVE * (1.0 - smoothstep(w, w + GROOVE_EDGE, np.abs(t - tj))))
    return g


def depth_at(t):
    """The octagon's half depth at axis position t (the foot flaring forward)."""
    return RN + FLARE * (1.0 - smoothstep(0.0, FLARE_T, t))


def boss_scale(t):
    """The head's boss: its size (a share of the drums') at axis position t."""
    s = S_RIM + (S_TOP - S_RIM) * np.clip((t - T_CAP - 1.5) / (T_TOP - T_CAP - 1.5), 0.0, 1.0)
    return np.where(t < T_CAP + 1.5, 1.0 + (S_RIM - 1.0) * smoothstep(T_CAP, T_CAP + 1.5, t), s)


def column_sdf(gx, gy, gz):
    """The column's signed distance on points of the picture's plane (before the relief and the noise)."""
    dy, dz = gy - Y_FOOT, gz - Z_FOOT
    t = dy * SA + dz * CA
    v = -dy * CA + dz * SA
    u = gx - X_AXIS
    rn = depth_at(np.maximum(t, 0.0))
    drums = smax(octagon(u, v, RX, rn) + joints(t), t - T_CAP - 0.6, 1.0)
    # The head's boss: the octagon rounding into an ellipse, narrowing to its top, its top face bulging, its edge round.
    s = boss_scale(t)
    w = 0.35 * smoothstep(T_CAP + 0.5, T_CAP + 7.0, t)
    radial = ((1.0 - w) * octagon(u / s, v / s) + w * ellipse(u / s, v / s)) * s
    q = np.minimum(1.0, (u / (RX * s)) ** 2 + (v / (RN * s)) ** 2)
    top = t - T_TOP - BULGE * (1.0 - q)
    boss = smax(np.maximum(radial, T_CAP - 1.0 - t), top, ROUND)
    upper = np.maximum(-smax(-drums, -boss, 1.0), -t)               # (a smooth union: the rim rounds into the boss)
    # The foot: under the foot ring, straight down to the ground (in the picture's plane: unseen by the camera).
    z_ring = Z_FOOT - dy * SA / CA                                  # the foot ring's plane over (x, y)
    v_ring = -dy * CA + (z_ring - Z_FOOT) * SA
    foot = np.maximum(octagon(u, v_ring, RX, depth_at(np.zeros_like(t))) + joints(np.zeros_like(t)), gz - z_ring)
    return np.minimum(upper, foot), t


def solid(fl, carve=None):
    t0 = time.time()
    gx = XS[:, None, None]
    gy = YS[None, :, None]
    gz = ZS[None, None, :].astype(np.float64)
    d, t = column_sdf(gx, gy, gz)
    d = d.astype(np.float32)
    t = np.broadcast_to(t, d.shape)
    # The relief from the picture's fine shading (lumps where it is light, pits where it is dark).
    relief = fl["relief"][:, :, None]
    head = smoothstep(T_JOINTS[2] + 1.5, T_JOINTS[2] + 3.5, t)
    d -= (relief * (RELIEF_DRUM + (RELIEF_HEAD - RELIEF_DRUM) * head)).astype(np.float32)
    # Noise near the surface: rougher on the head.
    i, j, kz = np.nonzero(np.abs(d) < 2.0)
    x, y, zz = XS[i], YS[j], ZS[kz]
    hw = head[i, j, kz]
    detail = np.zeros(len(i))
    for n, ((ad, sd), (ah, sh)) in enumerate(zip(NOISE_DRUM, NOISE_HEAD)):
        detail += (1.0 - hw) * ad * noise3(x / sd, y / sd, zz / sd, 71 + n)
        detail += hw * ah * noise3(x / sh, y / sh, zz / sh, 81 + n)
    d[i, j, kz] += detail.astype(np.float32)
    if carve is not None:
        d = np.maximum(d, carve(d).astype(np.float32))
    d = np.maximum(d, np.float32(-SKIRT) - ZS[None, None, :].astype(np.float32))
    for axis in range(3):                                            # smoothed a little: nothing finer than the grid
        p = np.pad(d, [(1, 1) if ax == axis else (0, 0) for ax in range(3)], mode="edge")
        d = 0.25 * np.take(p, range(0, d.shape[axis]), axis=axis) + 0.5 * d + \
            0.25 * np.take(p, range(2, d.shape[axis] + 2), axis=axis)
    print("solid: %.1f s" % (time.time() - t0))
    return d.astype(np.float32)


def top_surface(d):
    """The height of the highest surface over each grid point x, y (where the field first turns negative from above),
    nan where there is none."""
    inside = d < 0
    any_in = inside.any(axis=2)
    top_k = NZ - 1 - np.argmax(inside[:, :, ::-1], axis=2)
    k0 = np.clip(top_k, 0, NZ - 2)
    a = np.take_along_axis(d, k0[:, :, None], 2)[:, :, 0]
    b = np.take_along_axis(d, np.clip(k0 + 1, 0, NZ - 1)[:, :, None], 2)[:, :, 0]
    frac = np.where(np.abs(a - b) > 1e-6, a / (a - b), 0.0)
    z = ZS[k0] + np.clip(frac, 0.0, 1.0) * H
    return np.where(any_in, z, np.nan)


def broken_carve(fl_dmg, z_top):
    """The broken look's carving (a field to take the max with): the hollows down the camera's line of sight (in the
    picture's plane: straight down) as deep as the picture is black; everything the camera would see outside the broken
    outline, and inside it, near the break, the top lowered into a fracture face (up to FRACTURE_DEPTH at the edge)."""
    depth = blur(HOLLOW_DEPTH * smoothstep(0.12, 0.75, fl_dmg["black"]), 0.5)
    gone = np.clip(fl_dmg["gone"], 0.0, 1.0)
    lower = FRACTURE_DEPTH * smoothstep(0.06, 0.5, np.clip(fl_dmg["gone_soft"], 0.0, 1.0))
    zt = np.nan_to_num(z_top, nan=-10.0)

    def carve(d):
        gz = ZS[None, None, :]
        under = zt[:, :, None] - gz                                 # how far under the intact top surface
        cut = np.maximum(depth, lower)[:, :, None] - under          # > 0: inside a hollow or the fracture
        return np.maximum(cut, (gone[:, :, None] - 0.5) * 8.0)
    return carve


def hollow_test(fl_dmg, z_top):
    """Which faces (their points in the picture's plane x, py and height z) lie in a hollow: under the intact top where
    the broken picture is black."""
    depth = blur(HOLLOW_DEPTH * smoothstep(0.12, 0.75, fl_dmg["black"]), 0.5)
    zt = np.nan_to_num(z_top, nan=-10.0)

    def test(x, py, z):
        return (sample_grid(depth, x, py) > 0.6) & (z < sample_grid(zt, x, py) - 0.35)
    return test


# --- Colours -----------------------------------------------------------------------------------------------------------

def materials():
    m = {i: k.material("column_stone", palette=i, metallic=0.0, roughness=0.82) for i in range(0xa3, 0xae)}
    m[JOINT] = k.material("column_joint", palette=JOINT, metallic=0.3, roughness=0.6)
    m[GOLD] = k.material("column_gold", palette=GOLD, metallic=0.35, roughness=0.45)
    m[QUARTZ] = k.material("column_quartz", palette=QUARTZ, metallic=0.1, roughness=0.5)
    m[HOLLOW_LIT] = k.material("column_hollow_lit", palette=HOLLOW_LIT, metallic=0.0, roughness=0.9)
    return m


def axis_position(x, py, z):
    """Where along the column's axis a point (x, the picture's py, z) lies."""
    return (py - Y_FOOT) * SA + (z - Z_FOOT) * CA


def shades(centres, normals, fl, hollow=None):
    """Each face's palette index: the picture's colours under it (its point taken back into the picture's plane); the
    joints dark, the undersides in shade; the gold flecks and the quartz where the picture has them."""
    x, y, z = centres[:, 0], centres[:, 1], centres[:, 2]
    py = y + TILT * z
    s = sample_grid(fl["paint"], x, py)
    s = s + DITHER * noise3(x / 1.1, py / 1.1, z / 1.1, 91)
    s = np.where(normals[:, 2] < -0.35, np.minimum(s, 4.0), s)      # the undersides in shade
    t = axis_position(x, py, z)
    in_joint = np.zeros(len(x), bool)
    for tj in T_JOINTS[1:]:
        in_joint |= np.abs(t - tj) < GROOVE_W + 0.25
    idx = 0xa0 + np.clip(np.round(s), 3, 13).astype(int)
    idx = np.where(in_joint, JOINT, idx)
    seen = (normals[:, 2] - normals[:, 1] * TILT) > 0.15              # faces the camera sees
    idx = np.where(seen & ~in_joint & (sample_grid(fl["gold"], x, py) > 0.42), GOLD, idx)
    idx = np.where(seen & (normals[:, 2] > 0.25) & (sample_grid(fl["quartz"], x, py) > 0.62), QUARTZ, idx)
    if hollow is not None:
        inside = hollow(x, py, z)
        lit = (normals @ np.array(LIGHT)) > 0.55
        idx = np.where(inside, np.where(lit, HOLLOW_LIT, HOLLOW_DARK), idx)
    return idx


# --- Pieces ------------------------------------------------------------------------------------------------------------

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


def build_whole(name, fl, carve=None):
    d = solid(fl, carve)
    verts, quads = surface_nets(d, (X0, Y0, Z0), H)
    quads = drop_islands(verts, quads)
    whole = finish_whole(mesh_object(name, verts, quads))
    bm = bmesh.new()
    bm.from_mesh(whole.data)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    bm.to_mesh(whole.data)
    bm.free()
    return whole, d


def export_piece(obj, label, name, sprite_mask, centre, options, out):
    if sprite_mask is not None:
        mk.compare("%s as the camera sees it, its sprite's own pixels" % label,
                   view_coverage([obj], 24, 28, centre), sprite_mask)
    obj.data.transform(Matrix.Translation((-centre[0], -centre[1], 0.0)))
    obj.data.validate()
    mk.apply(obj)
    triangulate([obj])
    bpy.context.view_layer.update()
    mk.report(name, [obj], os.path.join(out, name + ".glb"))
    if "preview" in options:
        mk.preview(options["preview"] + name, [obj], size=(24, 56), scale=12, centre=(0.0, -10.0))


def build():
    options = k.args()
    out = mk.outdir(options)
    only = set(options["only"].split(",")) if "only" in options else None
    check = "check" in options
    k.reset()
    bpy.context.scene.view_settings.view_transform = "Standard"
    mats = materials()
    pic = art(ART)
    pic_dmg = art(ART_DMG, base=pic)
    fl = paint_fields(pic)
    fl_dmg = paint_fields(pic_dmg)
    gx, gy = np.meshgrid(XS, YS, indexing="ij")
    gone = (own_pixels(pic) & ~own_pixels(pic_dmg)).astype(np.float64)
    fl_dmg["gone"] = blur(sample(gone, gx, gy), 0.45)
    fl_dmg["gone_soft"] = blur(sample(gone, gx, gy), 1.7)
    wanted = [p for p in PIECES if not only or p[0] in only]
    wanted_dmg = [p for p in PIECES if p[2] and (not only or p[2][0] in only)]
    jobs = []
    if wanted or "whole" in options:
        jobs.append(("rock_column", pic, fl, False,
                     [(name, sprite, box, centre) for name, sprite, _, box, centre in wanted]))
    if wanted_dmg or "whole" in options:
        jobs.append(("rock_column_wreck", pic_dmg, fl_dmg, True,
                     [(dmg[0], dmg[1], box, centre) for _, _, dmg, box, centre in wanted_dmg]))
    for label, look, paint, broken, pieces in jobs:
        carve = hollow = None
        if broken:
            z_top = top_surface(solid(fl))
            carve = broken_carve(fl_dmg, z_top)
            hollow = hollow_test(fl_dmg, z_top)
        whole, _ = build_whole(label, paint, carve)
        shear_to_camera(whole)
        whole.data.update()
        print("%s: %d vertices, %d triangles" % (label, len(whole.data.vertices), len(whole.data.polygons)))
        source = mk.NormalSource(whole)
        own = own_pixels(look)
        if "whole" in options or check:
            view = whole.copy()
            view.data = whole.data.copy()
            bpy.context.scene.collection.objects.link(view)
            centres, normals = face_data(view)
            assign(view, shades(centres, normals, paint, hollow), mats)
            whole.hide_render = True
            if check:
                mk.compare("whole %s as the camera sees it (the ground left out)" % label,
                           view_coverage([view], 48, 84, (0.0, 0.0)), own.tolist())
            if "whole" in options:
                mk.preview(options["whole"] + label, [view], size=(48, 84), scale=8, distance=1.4)
                triangulate([view])
                mk.export([view], options["whole"] + label + ".glb")
            bpy.data.objects.remove(view)
            whole.hide_render = False
        for name, sprite, box, centre in pieces:
            obj, rim = cut_piece(whole, box, name, mats[CAP])
            if obj is None:
                continue
            whole.hide_render = True
            decimate(obj, rim, TARGET)
            shade_like(obj, source)
            centres, normals = face_data(obj)
            idx = shades(centres, normals, paint, hollow)
            flags = np.empty(len(obj.data.polygons), np.int64)
            obj.data.polygons.foreach_get("material_index", flags)
            idx[flags == 1] = CAP
            assign(obj, idx, mats)
            mask = None
            if check:
                c0, r0 = int(centre[0] - 12 + 24), int(42 - centre[1] - 14)
                mask = own[r0:r0 + 28, c0:c0 + 24].tolist()
            export_piece(obj, "%s (M %d)" % (name, sprite), name, mask, centre, options, out)
            bpy.data.objects.remove(obj)
            whole.hide_render = False
        bpy.data.objects.remove(whole)


if __name__ == "__main__":
    build()
