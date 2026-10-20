"""The tan rock arch of SURFACE and DESERTRUN (and episode 6's ROOST and COLLECTOR), polished (2026-10-20; it replaces
wave3_n_rocks.py's ridge of tan rock and wave2_h.py's desert_rock_tip). Sheet 3, ramp 1's tans. The levels put it
together from 2x2 sprites, each an enemy of its own (213-222 and 228-233 in episodes 4 and 6; the nub is 212):

- rock_arch_198 (the left foot), 162 above 200 and 164 above 202 (the left leg and the start of the span), then
  either the right leg at once (the short version, 132 x 56: SURFACE's events at 1196 and 1308, DESERTRUN's at 48
  and on) or three more columns of span first, 166/204, 168/206, 170/208 (the long version, 204 x 56: SURFACE's
  1644). The right leg is 241 above 279, 262 a column on and 14 rows lower, 281 below 262 and 282 12 pixels right
  of 281; it joins whichever column comes last, 72 or 144 pixels from 198's left edge. Its sprites overlap (their
  pixels are the same where they do): 262 keeps its top half, 281 its left half, 282 all of it.
- desert_rock_tip (3 180, 1x1): the nub in the notch of the left leg. DESERTRUN puts it there (6 pixels right of
  198's x and 22 above its y: drawn one row above the notch); SURFACE, ROOST and COLLECTOR put it at 162's x and
  116 pixels down (194 below the notch), where it is a stray rock.
The levels mostly put the feet (198, 281, 282) and the nub on the ground layers and the rest on the top one;
models.cfg's layer=ground draws all of them on the ground enemies' layer, where they meet.

As the sprites and their 4x upscales draw it: a natural arch of golden sandstone seen from above and a little from
the south. Its span runs along the top of the picture, lit on its north side (shades c-f) and smooth there, darker
on its south side (over the opening between the legs), which dark cracks break into blocks; its legs come down to
the bottom of the picture, the left one sinewy (light ribs and dark grooves running down it), the right one
fractured; a light boulder lies at each foot.

Built as such an arch in the round. The legs stand on the sand, flaring into it, and rise to the span, which is
lifted over the opening (its underside HS pixels up, its crest HC): the span's north face steep, its south face a
long rounded slope down to a lip over the opening (the game's sun casts the span's shadow under it); the legs'
inner feet are the spring lines of the opening's vault, its underside rising from them to the soffit SPRING pixels
in. Seen from above the rock covers the sprites' pixels (the outline a little smoothed). On it: the sprite's shading
as relief (lumps where it is light, creases and cracks where it is dark: the left leg's ribs, the span's lobes and
blocks), sandstone's bedding (the slopes stepped a little into layers, grooves round the steep walls, the layers'
colour banded), smooth noise. Its colours are the sprite's own shades under each face: the broad shading with which
the sprite paints the light lifted towards the middle (the game's light adds it again), its fine shading kept,
grained a little; the undersides dark.

The arch is built whole (the long version) as a signed distance field on a grid H pixels apart, its surface
extracted (surface nets) and smoothed a little, then cut along the sprites' edges into the pieces (the cuts capped),
each piece's triangles reduced to about TARGET with the vertices on its cuts kept where they are and its normals
those of the dense whole: pieces meet exactly and shade as one rock. The span is the same round both joints (x 72
and 144, so that the right leg meets either: the short version puts 241/279 after 164/202): the field there is the
mean of both neighbourhoods, its noise the same, its triangles split alike. Each piece is moved so that its sprite's
centre is its origin. The nub is a small boulder of its own (not cut from the whole: the game draws it a row above
the notch), lying in the notch against the leg's edge.

Coordinates: 1 unit = 1 game pixel; the whole's x is the picture's column edge (0-204), y = 28 - row, z up from the
sand (z = 0). The rock reaches SKIRT under the sand: the pieces and the nub stand on the terrain with height=-4.
models.cfg (the model lines stay as they are): sprite 3 198 rock_arch_198 yaw=0 layer=ground height=-4, the same for
162, 200, 164, 202, 166, 204, 168, 206, 170, 208, 241, 262, 279, 281 and 282, and sprite 3 180 desert_rock_tip yaw=0
layer=ground height=-4 (on the ground where the levels put the nub on the top layer).

Replaces wave3_n_rocks.py (the arch was all it still built), wave3_n_art.py's ROCK_A and ROCK_B, and wave2_h.py's
desert_rock_tip() and ROCK_TIP.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes of the whole
and of each piece against enemy_3.png), --preview <prefix> (each piece's top and 3/4 views), --whole <prefix> (the
whole's), --only <model,...>.
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

# The arch's pixels as the levels put its sprites together (the long version, 204 x 56): each pixel its shade in
# ramp 1 (palette index 0x10 + digit), '.' none. Columns 0-23 rows 28-55 are 3 198, then two rows of 24 x 28 columns
# (162 above 200, 164/202, 166/204, 168/206, 170/208, 241/279), 3 262 at columns 168-191 rows 14-41, 281 at
# 168-191 rows 28-55, 282 at 180-203 rows 28-55 (where they overlap their pixels are the same).
ARCH = """
.
.
....................................................................11130001111.............................................................0110055
..............................................................11110368abbaa8776631011...................................................000039bcbaa4
........................................................11121479aabcccccccccccccaa772111...................................1101123110100178acccccbb972
.......................................................116abbccccccccccccccccccccbbaa87401110........3332221011111111021..1.2589bcb887689bcccccccbba8735
.....................................................107bcabbbbbbbbbbcccccccccccbbbbbbbb87733210101357777667765546899ba998777acdddbaaaaaaabccccccbba97635
....................................................15adddbbcccddefdbbcccccccccbbbbbbbbbbbbb66654788aaaaaaaaaaaaaabccccccccddeedbbbbaaaaaaabcccccbbb975510
.............................................11111027bddddddddddeeeedbbcbbbbbbbbbbbbbbbbbbbbbb978abbbbbbbbbbbbbbbbbbccccddeeedcbccbbbbbaaaaaabbbbbba87572233
...........................................10257698acdddddddeedeeeddcbaabbbbbbbbbbbbbbbbbbbbbbba7abbbbbbcccccccccdddeeeeeeecbabccbbbbbbbbaaaaaabbaa975468675223
.........................................1148dcbdcdddddddddefeeeedcbaabaabbbbbbbbbbbbbbbbbbbbbbb9bbbbbbbbbbccccdddeedddddbbaaabca978777778888999aaa9777aa99998613
.......................................1158cdddddcccdddcdefeffeedbabaaa999999aaaabbbbbbbbbbbbbbaabbbbbbbbbbbbbaaaaaaaaaaaaaabcca8667888999aaaaaa99968aaaaaaaaa97433
....................................1059adddddcccccccccefecbaabbbaaaaaaaaaaa98aaa9aabbbbbbbbbbaaabaaaaaaaaaaaaabbbbbbbbbcccdddca778899aaaaaaaaaaaaa69aaaaaaaaaaaa764422
.................................1128addddddccccccccccefbaaaaaaaaaaaaaaaaaaa88aaaa99aa9abbbbbaaaabbbbbbbbbbbbbbbbbbbbbbccdddddb868889aaaaaaaaaaaaa77aaaaaaaaaaaaaa887541
................................108bcddddddacccccccccffaaaaaaaaaaaaaaaaaaa9abccdcc979899889999aaabbbbbbbbbbbbbbbbbbbbccccdddeda88999aa9aaaaaaaaaa97aaaa999999aaaaaa888661112
................................16bcbbcbbddddcccccdeeeaaaaaaaaaaaaaaaaaabaacbcccbba6889999888889abbbbbbbbbbbbbbcccccccccddddecba999999aaaaaaaaaab88aaaaa999999aaaaaa988764411
................................18ccccccdddddeddddeeeaaaaaaaaaabbbbcccdcbcccccbbaa768aaaa9999999bccccccccccccccbbbbbcdcddddedbba999abbbbbaaaaaaab9abbaaaaa99999aaaaaaa99824511
...............................106bccccccdeeeeeddfde999999999aabbccbbbbcccbaaaaaa8668999aaa9999acbabbbbbbbbbbbbbbbcccccdddefdbbbaa9bbbbbbbbaabbcaaccbbbbaaa99999aaaaaaaa963311..1
...............................15bccbcccccccdddfed98999999aaaabbbbbbbbbbbaaaaaa9766667789ab99999aaaaaabbbbbbbbbbbcccddccfffcbba9a9bbbbbbbbbbcccc9ccccbaaaaa99999999aaa9976aa420111
...........................11149ccbbbcbbccbbcdeec86899999aaaaaaaabbbbbbaaa98876666667787789abaa9aaaaaaaaabbbcccccdddccdeffecbaa9abbbbbbbbbcccccb9deddcaaaaa99999888888883899b43221
..........................02689998addccccddcdbbb93588899999999988777766666666666666778876789899bbcdccbbbbbbcccccccccddffedbbbbbbbbbbbbbbbbba876757bbcccaaa999998887777653688aa44321
.........................258ba88ab99cdddddbdb966358777777777788778887777777777777777877765666898aabeeddbaa9aabccccdddca99999999bbaa9988888876667765799cca99999987776577876788b644321
.........................18ba79aacfa9cdccbca87543687777777777777777777777777777777777777524444334779cfeabbcdcccccc9a88898877777776554445566667777777678b9998887545546899966889b545341
........................06a96578abbfa9dbbc987656866877777777777777777777777777777777777743334555555547c88888888866666676666667665455665245777777777777579988862456679999986788aa445321
........................6abaded76abcc8cdc8677788785777777777777777777777777777777777777732222566666665a988888866666544332333435444577775257877777777876578765034589999999977889a5455301
........................aaaccdde77bbc7bca667789aba7577777777777777777777777777777777777445564344666654a97777776544332233445545455566677754687777777787765884124368999999997778898555542
........................aacbbbbbf89bb7bb666788999b74777777777777777777777777777777777753566665543111178977777762223344455555656666666667644487777778788746423555443367899997788885555542
........................acbaaaaadeaba6a96668888889607777777777777777777777777777777654366666666666414677777777423445554555555666666666666654687777777764200466677765543569987888885555532
....................19a6cbaaaaabbfac96a866788888895167777777777777777777777766555543466666666666423466665556653245555423455555556666666665654577777554333211458a97666665434677888855555521
....................3b6cbaaaaabcdc6b86a66678887779515775566677777777777777655424434455556666665324455544555553124555640133335555566666665555536675554444443256bba76666666654225888666555501
..................205accaaaabbcbaa48746667788877785401455566666666666465555633345455555556666432222222224544300344454334320124555555555555555255554455555444246a9876666666665514887666654311
..................06accabbbccb9888359666677886666664431455666655555555435533435555555555555543354334443233222033344412366532333455555555555332555566655556543214a9986666666666503776555553112
.................048bcbbbbb99888853677667788666665554223333333222333343210113555555555555554333544555541222212223303344666654322344555554421114416666655555555535898776665555555535666555412201
................0479aaa88888888874677668787665554222222233333333333322222101455555555554442222455555553012211222110..024456665311001222332111013256666666555455522597666655555555544576554212111
...............127998888888888866667756775555422233333333344444444444302112355555555553321211455555552001..1122211......32111131121111122010110112333456665555555224866666555555555544755532321122
...............15977888888888877666767755553221223333333344444566533112100234444444442333223355555542201................................11011224033234325666656668746876666555555555547655422433311
...............18777888a88887786665665555432222234444344334555664432101110222201211211032342555554334....................................1111234131201232155666655765687666665555555555755533244421
...............187777788a778777665765554332222334444444443445564332011224444410121..3221032355533334......................................1113554443344442244666744646676666665555555556655422244401
...............1577678888987776656865533332223335444444443356644333333355544310.......4211234432233........................................013455444322344234667667543534666666555555555755530134421
..............115676888898777765687654344322233554444444433564423344445443222..........3000111111...........................................00143244444434542266786455563245666655555555765420134440
............1110565677777777765687654344432223554444444443223424344454300...............41111110...............................................013233323023452247899999983777766655555555642112444511
...........023146556666777777557765434443223355444444444422332243444441....................213....................................................22222..123342247778888a7466666655555555653234445530
..........11432665666667777755785543444432335654444444444223224455432.....................................................................................2223343366778887366666665555555664524444532
..........1465356666666777775577552344434455654444455544313535455442.......................................................................................1332344447888886266666655555555564214444421
..........166545666666777787556652344434467774433455554412444455565..........................................................................................32323344788888456666665555555555113444431
.........1366525666667777897566523344345677954434555554334444555..............................................................................................03434334788887266666654355555452124445213
.........146772656677777788566542334435577954424455555324453445.................................................................................................033333378888556666642145555543123334411
........1246784257777777789655422334346669654224555654234532345..................................................................................................0023343778863666663223555554412243330
........144778916677677778855532333435779654324555665334553035.....................................................................................................021332467714466611033555553201442311
.......1153889b3356867778a655422333335786553335556663334430..........................................................................................................22340345131351122234455531224413101
......00553989a8157667779a65532233333686553435556666324433.............................................................................................................3469998842111233324555411033231211
......0565388a9c63746778b855522233324665553335566664234321..............................................................................................................4a999a986113333323455512123311411
.....146654779aba7566778b755422223335755534345666663334223..............................................................................................................3bccb778862333444335552221212254
....1566542889aae913678a965532222325655533345566664234432...............................................................................................................38ac97778743344454345521103223531
...10456430777ada632278b86553222233555533335566666322321................................................................................................................257b977777634445555344422221345422
...05776333797dc767526aa6555532234555532334556666421221.................................................................................................................1659a777777434555553444434211554233
"""


# --- Layout ---------------------------------------------------------------------------------------------------------
# The pieces: model, sprite, its sprite's top left pixel in the picture (column, row) and, where the right leg's
# sprites overlap, the part of it the piece keeps (columns c0-c1, rows r0-r1, ends exclusive).
PIECES = [
    ("rock_arch_198", 198, (0, 28), None),
    ("rock_arch_162", 162, (24, 0), None), ("rock_arch_200", 200, (24, 28), None),
    ("rock_arch_164", 164, (48, 0), None), ("rock_arch_202", 202, (48, 28), None),
    ("rock_arch_166", 166, (72, 0), None), ("rock_arch_204", 204, (72, 28), None),
    ("rock_arch_168", 168, (96, 0), None), ("rock_arch_206", 206, (96, 28), None),
    ("rock_arch_170", 170, (120, 0), None), ("rock_arch_208", 208, (120, 28), None),
    ("rock_arch_241", 241, (144, 0), None), ("rock_arch_279", 279, (144, 28), None),
    ("rock_arch_262", 262, (168, 14), (168, 192, 14, 28)),
    ("rock_arch_281", 281, (168, 28), (168, 180, 28, 56)),
    ("rock_arch_282", 282, (180, 28), (180, 204, 28, 56)),
]
# The nub: its 12 x 14 cell's top left pixel in the picture, where DESERTRUN puts it (6 right of 198's x and 22 above
# its y: a 1x1 sprite is drawn at (x, y), a 2x2 one at (x - 6, y - 7)).
TIP = ("desert_rock_tip", 180, (12, 13))
JOINTS = (72.0, 144.0)      # where the right leg joins the span: after 164/202 (short) or after 170/208 (long)


def kept(piece):
    """A piece's box in the whole's coordinates (x0, x1, y0, y1) and its origin (its sprite's centre)."""
    _, _, (c, r), keep = piece
    c0, c1, r0, r1 = keep or (c, c + 24, r, r + 28)
    return (float(c0), float(c1), 28.0 - r1, 28.0 - r0), (c + 12.0, 14.0 - r)


# --- The form ---------------------------------------------------------------------------------------------------------
HC = 22.0                   # the crest of the span over the sand
HS = 11.0                   # the opening under the span (the soffit's height)
LIP = 2.6                   # how thick the lifted rock's edges are (the lips over the opening)
SKIRT = 1.5                 # how far the grounded rock reaches under the sand
FOOT = 0.6                  # how high the grounded rock's edges stand over the sand
RHO_C = 0.3                 # where the crest lies across the band: 0 its outer edge, 1 its inner edge
K_SIDE, K_BOT = 1.3, 0.8    # rounding of the edges where the sides meet the top and the underside
FLARE = 0.6                 # the legs' rise from their feet (smoothstep ** FLARE: the feet flare into the sand)
# The arch's crest line, from the left foot (under the sand below the sprites' bottom edge) up the left leg, along the
# span and down the right leg: its height is the arch's height at the points nearest it. The legs reach the span's
# height at SPAN's vertices, outside the joints' neighbourhoods (the span is the same at both joints).
SPINE = [(28.5, -30.0), (32.5, -22.0), (37.5, -14.0), (43.0, -6.0), (49.5, 2.0), (56.0, 8.5), (63.0, 12.5),
         (72.0, 13.5), (144.0, 13.5), (152.0, 12.5), (159.0, 8.5), (166.0, 1.5), (172.5, -6.5), (178.5, -14.5),
         (183.0, -22.0), (185.5, -30.0)]
SPAN = (6, 9)
# The opening under the arch, seen from above: inside it the rock's underside rises from the spring lines (along the
# legs' inner feet, then straight on under the span, 12 pixels short of either joint) to the soffit, SPRING pixels in,
# so that the soffit is level round both joints.
VOID = [(56.5, -40.0), (58.5, -24.0), (61.5, -20.0), (61.0, -15.0), (60.0, -12.0), (60.0, 40.0), (156.0, 40.0),
        (156.0, -12.0), (156.5, -13.0), (158.0, -16.0), (164.0, -21.0), (167.0, -24.0), (167.5, -40.0)]
SPRING = 6.0
# Weathering: smooth noise (amplitude, scale in pixels), sandstone's bedding as grooves round the walls (depth,
# spacing), the sprite's shading as relief (lumps where it is light, creases where it is dark: per shade step,
# fine and broad).
NOISE = ((0.18, 3.2), (0.07, 1.25))
LUMPS = (0.35, 8.0)
STRATA = (0.32, 2.3)
TERRACE = 0.25              # how much the slopes step into the bedding's layers
RELIEF = (0.32, 0.4)
CRACKS = (1.1, 0.8)         # the sprite's dark lines cut in as cracks: depth, and how much darker than round them
DARK_KEEP = 0.5             # the share of the sprite's darkening (below shade 9.5) the colours keep (the light adds)
DETAIL = 1.1                # the sprite's fine shading (cracks, lumps, highlights) on the colours
DITHER = 0.3                # noise on the shades before they are rounded to the palette's
BANDS = 0.5                 # the bedding's colour: the layers a shade lighter between the grooves

# --- The grid the solid is sampled on -------------------------------------------------------------------------------
H = 0.4
X0, NX = -3.2, 528          # 72 and 144 are grid points (i = 188 and 368)
Y0, NY = -32.0, 156
Z0, NZ = -2.0, 76
XS = X0 + H * np.arange(NX)
YS = Y0 + H * np.arange(NY)
ZS = Z0 + H * np.arange(NZ)
I72 = int(round((JOINTS[0] - X0) / H))
SHIFT = int(round((JOINTS[1] - JOINTS[0]) / H))
LOCK = (4.8, 10.0)          # the joints' neighbourhoods made the same: wholly within the first, blended to the second


# --- Numbers ----------------------------------------------------------------------------------------------------------

def smoothstep(e0, e1, x):
    t = np.clip((np.asarray(x, dtype=np.float64) - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def smax(a, b, k):
    """A smooth maximum (rounds the edge where two surfaces of a solid meet, k pixels wide)."""
    h = np.clip(0.5 + 0.5 * (a - b) / k, 0.0, 1.0)
    return b + (a - b) * h + k * h * (1.0 - h)


def art(text, width):
    rows = text.strip("\n").split("\n")
    out = np.full((len(rows), width), np.nan)
    for r, line in enumerate(rows):
        for c, ch in enumerate(line):
            if ch != ".":
                out[r, c] = int(ch, 16)
    return out


def fill_outside(a, steps=16):
    """The pixels without a value take their neighbours' (step by step outwards): shades to sample near edges."""
    a = a.copy()
    for _ in range(steps):
        known = ~np.isnan(a)
        if known.all():
            break
        v = np.pad(np.where(known, a, 0.0), 1)
        kn = np.pad(known.astype(np.float64), 1)
        acc = v[:-2, 1:-1] + v[2:, 1:-1] + v[1:-1, :-2] + v[1:-1, 2:]
        cnt = kn[:-2, 1:-1] + kn[2:, 1:-1] + kn[1:-1, :-2] + kn[1:-1, 2:]
        new = ~known & (cnt > 0)
        a[new] = acc[new] / cnt[new]
    a[np.isnan(a)] = 8.0
    return a


def sample(a, x, y, pad=0.0):
    """Bilinear sample of a pixel array a[row, column] (values at the pixels' centres) at whole coordinates."""
    rows, cols = a.shape
    u, v = x - 0.5, 27.5 - y
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


def contour(f, level=0.5):
    """Where a field on the grid's x, y crosses level: points (x, y) and, for each, the grid point beside it on the
    side below level (i, j)."""
    pts, outside = [], []
    a, b = f[:-1, :], f[1:, :]
    i, j = np.nonzero((a - level) * (b - level) < 0)
    t = (level - a[i, j]) / (b[i, j] - a[i, j])
    pts.append(np.stack([XS[i] + t * H, YS[j]], 1))
    outside.append(np.stack([np.where(a[i, j] < level, i, i + 1), j], 1))
    a, b = f[:, :-1], f[:, 1:]
    i, j = np.nonzero((a - level) * (b - level) < 0)
    t = (level - a[i, j]) / (b[i, j] - a[i, j])
    pts.append(np.stack([XS[i], YS[j] + t * H], 1))
    outside.append(np.stack([i, np.where(a[i, j] < level, j, j + 1)], 1))
    return np.concatenate(pts), np.concatenate(outside)


def nearest(px, py, pts, subsets=(), chunk=1024):
    """The distance from each point (px, py) to the nearest of pts, then to the nearest of each subset (masks)."""
    p = np.stack([px, py], 1).astype(np.float32)
    q = pts.astype(np.float32)
    out = [np.empty(len(p), np.float32) for _ in range(1 + len(subsets))]
    for s in range(0, len(p), chunk):
        d2 = ((p[s:s + chunk, None, :] - q[None, :, :]) ** 2).sum(-1)
        out[0][s:s + chunk] = d2.min(1)
        for o, m in zip(out[1:], subsets):
            o[s:s + chunk] = d2[:, m].min(1) if m.any() else 1e12
    return [np.sqrt(o) for o in out]


def flood(mask, seed):
    """The pixels not in mask reachable from seed (row, column) without crossing it."""
    rows, cols = mask.shape
    seen = np.zeros_like(mask)
    stack = [seed]
    while stack:
        r, c = stack.pop()
        if 0 <= r < rows and 0 <= c < cols and not seen[r, c] and not mask[r, c]:
            seen[r, c] = True
            stack.extend(((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)))
    return seen


def polygon_sdf(px, py, poly):
    """Signed distance to a closed polygon (negative inside)."""
    d = np.full(px.shape, np.inf)
    inside = np.zeros(px.shape, bool)
    n = len(poly)
    for i in range(n):
        (x0, y0), (x1, y1) = poly[i], poly[(i + 1) % n]
        dx, dy = x1 - x0, y1 - y0
        t = np.clip(((px - x0) * dx + (py - y0) * dy) / (dx * dx + dy * dy), 0.0, 1.0)
        d = np.minimum(d, np.hypot(px - x0 - t * dx, py - y0 - t * dy))
        if y0 != y1:
            inside ^= ((y0 > py) != (y1 > py)) & (px < x0 + (x1 - x0) * (py - y0) / (y1 - y0))
    return np.where(inside, -d, d)


def spine_height(px, py):
    """The arch's height at the points of its crest line nearest (px, py): the span's crest, falling down the legs."""
    pts = np.array(SPINE, float)
    seg = pts[1:] - pts[:-1]
    lengths = np.hypot(seg[:, 0], seg[:, 1])
    arc = np.concatenate([[0.0], np.cumsum(lengths)])
    best = np.full(px.shape, np.inf)
    along = np.zeros(px.shape)
    for i in range(len(seg)):
        t = np.clip(((px - pts[i, 0]) * seg[i, 0] + (py - pts[i, 1]) * seg[i, 1]) / lengths[i] ** 2, 0.0, 1.0)
        dist = np.hypot(px - pts[i, 0] - t * seg[i, 0], py - pts[i, 1] - t * seg[i, 1])
        better = dist < best
        best = np.where(better, dist, best)
        along = np.where(better, arc[i] + t * lengths[i], along)
    rise = np.minimum(along / arc[SPAN[0]], (arc[-1] - along) / (arc[-1] - arc[SPAN[1]]))
    return HC * smoothstep(0.0, 1.0, rise) ** FLARE


# Smooth gradient noise (Perlin's), vectorized.
_GRAD = np.array([[1, 1, 0], [-1, 1, 0], [1, -1, 0], [-1, -1, 0], [1, 0, 1], [-1, 0, 1], [1, 0, -1], [-1, 0, -1],
                  [0, 1, 1], [0, -1, 1], [0, 1, -1], [0, -1, -1]], np.float64)


def _hash(ix, iy, iz, seed):
    h = (ix * 73856093) ^ (iy * 19349663) ^ (iz * 83492791) ^ (seed * 2654435761)
    h &= 0xFFFFFFFF
    h = ((h >> 16) ^ h) * 0x45D9F3B & 0xFFFFFFFF
    h = ((h >> 16) ^ h) * 0x45D9F3B & 0xFFFFFFFF
    return (h >> 16) ^ h


def noise3(x, y, z, seed=0):
    x0, y0, z0 = np.floor(x), np.floor(y), np.floor(z)
    fx, fy, fz = x - x0, y - y0, z - z0
    ix, iy, iz = x0.astype(np.int64), y0.astype(np.int64), z0.astype(np.int64)
    u, v, w = (f * f * f * (f * (f * 6 - 15) + 10) for f in (fx, fy, fz))
    total = np.zeros(x.shape)
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                g = _GRAD[_hash(ix + dx, iy + dy, iz + dz, seed) % 12]
                dot = g[:, 0] * (fx - dx) + g[:, 1] * (fy - dy) + g[:, 2] * (fz - dz)
                total += (u if dx else 1 - u) * (v if dy else 1 - v) * (w if dz else 1 - w) * dot
    return total


def locked(fn, x, *args):
    """fn(x, ...) made the same round both joints: past the middle of the span (x > 108) it is fn(x - 72, ...),
    blended over 16 pixels (keeping the noise's strength)."""
    w = smoothstep(100.0, 116.0, x)
    out = np.zeros(x.shape)
    a = w < 1.0
    b = w > 0.0
    out[a] += fn(x[a], *[v[a] for v in args]) * (1.0 - w[a])
    out[b] += fn(x[b] - (JOINTS[1] - JOINTS[0]), *[v[b] for v in args]) * w[b]
    return out / np.sqrt((1.0 - w) ** 2 + w ** 2)


def lock(a):
    """The array (along x on the grid) made the same round both joints: the mean of both neighbourhoods, wholly
    within LOCK[0] of them, blended to each's own by LOCK[1]."""
    n1, n2 = int(round(LOCK[0] / H)), int(round(LOCK[1] / H))
    for kk in range(-n2, n2 + 1):
        w = 1.0 if abs(kk) <= n1 else float(smoothstep(n2, n1, abs(kk)))
        p, q = a[I72 + kk].copy(), a[I72 + SHIFT + kk].copy()
        m = 0.5 * (p + q)
        a[I72 + kk] = p + (m - p) * w
        a[I72 + SHIFT + kk] = q + (m - q) * w
    return a


# --- The solid ----------------------------------------------------------------------------------------------------------

def fields():
    """The arch's plan fields on the grid's x, y: the sides' distance, the top's and the underside's heights, the
    sprite's shades for the colours."""
    t0 = time.time()
    shade = art(ARCH, 204)
    mask = ~np.isnan(shade)
    ext = np.vstack([mask, np.repeat(mask[-1:], 8, axis=0)])        # the legs go on under the sand
    ext_shade = np.vstack([shade, np.repeat(shade[-1:], 8, axis=0)])
    gx, gy = np.meshgrid(XS, YS, indexing="ij")
    mf = blur(sample(ext.astype(np.float64), gx, gy), 0.45)
    # The outline: its inner part faces the opening between the legs, the rest is its outer part.
    pts, outside = contour(mf)
    opening = flood(ext, (50, 110))
    col = np.floor(XS[outside[:, 0]]).astype(int)
    row = np.floor(28.0 - YS[outside[:, 1]]).astype(int)
    ok = (row >= 0) & (row < ext.shape[0]) & (col >= 0) & (col < 204)
    inner = np.zeros(len(pts), bool)
    inner[ok] = opening[row[ok], col[ok]]
    d_all, d_in, d_out = nearest(gx.ravel(), gy.ravel(), pts, (inner, ~inner))
    d_all, d_in, d_out = (a.reshape(gx.shape).astype(np.float64) for a in (d_all, d_in, d_out))
    side = np.where(mf >= 0.5, -d_all, d_all)
    # The rock stays inside the pieces' boxes (none would keep what is outside them); the bottom row's boxes run on
    # under the sand, where the pieces' cuts end the legs.
    union = np.zeros_like(mf)
    for piece in PIECES:
        (x0, x1, y0, y1), _ = kept(piece)
        union[(gx >= x0) & (gx <= x1) & (gy >= (y0 if y0 > -27.9 else -31.0)) & (gy <= y1)] = 1.0
    union = blur(union, 0.3)
    upts, _ = contour(union)
    (du,) = nearest(gx.ravel(), gy.ravel(), upts)
    du = du.reshape(gx.shape).astype(np.float64)
    side = smax(side, np.where(union >= 0.5, -du, du), 0.8)
    # The underside: on the sand (under it) round the opening, rising inside it to the soffit.
    s = np.clip(-polygon_sdf(gx, gy, VOID) / SPRING, 0.0, 1.0)
    z_void = HS * np.sqrt(1.0 - (1.0 - s) ** 2)
    bot = z_void - SKIRT * np.clip(1.0 - z_void, 0.0, 1.0)
    # The top: across the band from its outer edge up to the crest (RHO_C of the way) and down to its inner edge.
    # Its edges flare into the sand round the legs; over the opening they are lips (the span's north face steep,
    # its south face a long rounded slope down to the lip); between, one blends into the other.
    lifted = blur(np.clip(z_void / 2.0, 0.0, 1.0), 5.0)
    rho = d_out / np.maximum(d_out + d_in, 1e-3)
    outer = rho <= RHO_C
    u = np.clip(np.where(outer, rho / RHO_C, (1.0 - rho) / (1.0 - RHO_C)), 0.0, 1.0)
    f_ground = u * u * (3.0 - 2.0 * u)
    f_lifted = 1.0 - (1.0 - u) ** np.where(outer, 2.6, 1.8)
    f = f_ground + (f_lifted - f_ground) * lifted
    crest = blur(spine_height(gx, gy), 1.5)
    edge = FOOT + (HS + LIP - FOOT) * lifted
    filled = fill_outside(ext_shade)
    s_px = sample(filled, gx, gy)
    fine, mid, broad = blur(s_px, 0.5), blur(s_px, 1.6), blur(s_px, 4.5)
    relief = RELIEF[0] * (fine - mid) + RELIEF[1] * (mid - broad)
    relief -= CRACKS[0] * np.clip((mid - fine - CRACKS[1]) / 2.0, 0.0, 1.0)  # the sprite's dark lines: cracks
    lumps = LUMPS[0] * locked(lambda a, b, c: noise3(a / LUMPS[1], b / LUMPS[1], c, 21), gx.ravel(), gy.ravel(),
                              np.full(gx.size, 0.5)).reshape(gx.shape)
    top = edge + (crest - edge) * f + lumps * np.clip(3.0 * f, 0.0, 1.0)
    # The bedding: the slopes stepped a little into layers (treads and risers, STRATA[1] apart, wavering), then the
    # sprite's relief on them.
    warp = strata_warp(gx.ravel(), gy.ravel()).reshape(gx.shape)
    u = (top + warp) / STRATA[1]
    steps = (np.floor(u) + smoothstep(0.3, 0.7, u - np.floor(u))) * STRATA[1] - warp
    top = top + TERRACE * (steps - top) * np.clip(top - 0.6, 0.0, 1.0)
    top = top + relief * np.clip(3.0 * f, 0.0, 1.0)
    # Never thinner than a lip over the opening, nor lower than a little over the sand.
    top = smax(top, np.where(z_void > 0.0, z_void + LIP, 0.35), 1.0)
    print("fields: %.1f s" % (time.time() - t0))
    # The colours: the sprite's broad shading (the light it paints in) lifted towards the middle, as the game's light
    # adds it again, its fine shading (cracks, lumps, highlights) kept.
    lifted_broad = np.where(broad < 9.5, 9.5 + (broad - 9.5) * DARK_KEEP, broad)
    paint = lifted_broad + DETAIL * (blur(s_px, 0.35) - broad)
    return {"side": side, "top": top, "bot": bot, "paint": lock(paint), "mask": mask, "shade": shade}


def strata_warp(x, y):
    """How far the bedding's layers waver up and down (pixels) at x, y."""
    return 0.8 * locked(lambda a, b, c: noise3(a / 11.0, b / 11.0, c, 5), x, y, np.full(np.shape(x), 0.37))


def solid(fl):
    """The arch's signed distance on the grid (negative inside), weathered, the same round both joints."""
    t0 = time.time()
    z = ZS.astype(np.float32)[None, None, :]
    d = smax(fl["side"].astype(np.float32)[:, :, None], z - fl["top"].astype(np.float32)[:, :, None], K_SIDE)
    d = smax(d, fl["bot"].astype(np.float32)[:, :, None] - z, K_BOT).astype(np.float32)
    gz = np.gradient(d, H, axis=2)
    i, j, kz = np.nonzero(np.abs(d) < 2.0)
    x, y, zz = XS[i], YS[j], ZS[kz]
    detail = np.zeros(len(i))
    for n, (amp, scale) in enumerate(NOISE):
        detail += amp * locked(lambda a, b, c, n=n, scale=scale: noise3(a / scale, b / scale, c / scale, 11 + n),
                               x, y, zz)
    # The bedding: grooves at heights wavering a little, round the steep walls (not on the tops, not underground).
    wall = np.clip(1.0 - 1.3 * np.abs(gz[i, j, kz]), 0.0, 1.0) * np.clip(zz / 0.8, 0.0, 1.0)
    detail *= np.clip((zz - 0.1) / 0.8, 0.0, 1.0)  # (none under the sand)
    phase = (zz + strata_warp(x, y)) / STRATA[1] - 0.32   # under each layer's lip
    depth = STRATA[0] * (0.6 + 0.8 * np.clip(locked(lambda a, b, c: noise3(a / 6.0, b / 6.0, c / 6.0, 9), x, y, zz)
                                             + 0.5, 0.0, 1.0))
    detail += depth * wall * np.exp(-((phase - np.round(phase)) / 0.2) ** 2)
    d[i, j, kz] += detail.astype(np.float32)
    # Smoothed a little (no features finer than the grid, which the surface would pinch at).
    for axis in range(3):
        p = np.pad(d, [(1, 1) if ax == axis else (0, 0) for ax in range(3)], mode="edge")
        d = 0.25 * np.take(p, range(0, d.shape[axis]), axis=axis) + 0.5 * d + \
            0.25 * np.take(p, range(2, d.shape[axis] + 2), axis=axis)
    d = d.astype(np.float32)
    lock(d)
    print("solid: %.1f s, %d points weathered" % (time.time() - t0, len(i)))
    return d


def surface_nets(f, origin, h):
    """The surface where f (on a grid h apart from origin) crosses 0, as quads: a vertex in each cell the surface
    passes (the mean of where it crosses the cell's edges), a quad round each grid edge it crosses. Faces outward."""
    inside = f < 0
    nx, ny, nz = f.shape
    count = np.zeros((nx - 1, ny - 1, nz - 1), np.float32)
    acc = np.zeros((nx - 1, ny - 1, nz - 1, 3), np.float32)
    crossings = []
    for axis in range(3):
        a = np.take(f, range(f.shape[axis] - 1), axis=axis)
        b = np.take(f, range(1, f.shape[axis]), axis=axis)
        cross = np.take(inside, range(f.shape[axis] - 1), axis=axis) != np.take(inside, range(1, f.shape[axis]), axis=axis)
        t = np.where(cross, a / np.where(cross, a - b, 1.0), 0.0).astype(np.float32)
        c = cross.astype(np.float32)
        others = [ax for ax in range(3) if ax != axis]
        for d1 in (0, 1):
            for d2 in (0, 1):
                sl = [slice(None)] * 3
                sl[others[0]] = slice(d1, d1 + (nx, ny, nz)[others[0]] - 1)
                sl[others[1]] = slice(d2, d2 + (nx, ny, nz)[others[1]] - 1)
                sl = tuple(sl)
                count += c[sl]
                acc[..., axis] += t[sl]
                acc[..., others[0]] += c[sl] * d1
                acc[..., others[1]] += c[sl] * d2
        crossings.append(cross)
    active = count > 0
    cells = np.argwhere(active)
    verts = (cells + acc[active] / count[active][:, None]) * h + np.asarray(origin)
    vid = np.full(count.shape, -1, np.int64)
    vid[active] = np.arange(len(cells))
    quads = []
    for axis, cross in enumerate(crossings):
        sl = [slice(None)] * 3
        others = [ax for ax in range(3) if ax != axis]
        for ax in others:
            sl[ax] = slice(1, (nx, ny, nz)[ax] - 1)
        idx = np.argwhere(cross[tuple(sl)])
        for ax in others:
            idx[:, ax] += 1
        i, j, kk = idx[:, 0], idx[:, 1], idx[:, 2]
        if axis == 0:
            q = np.stack([vid[i, j - 1, kk - 1], vid[i, j, kk - 1], vid[i, j, kk], vid[i, j - 1, kk]], 1)
            flip = ~inside[i, j, kk]
        elif axis == 1:
            q = np.stack([vid[i - 1, j, kk - 1], vid[i, j, kk - 1], vid[i, j, kk], vid[i - 1, j, kk]], 1)
            flip = inside[i, j, kk]
        else:
            q = np.stack([vid[i - 1, j - 1, kk], vid[i, j - 1, kk], vid[i, j, kk], vid[i - 1, j, kk]], 1)
            flip = ~inside[i, j, kk]
        q[flip] = q[flip][:, ::-1]
        quads.append(q)
    return verts, np.concatenate(quads)


def mesh_object(name, verts, faces):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts.tolist(), [], faces.tolist())
    mesh.validate()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def finish_whole(obj, smooth=1):
    """Triangulates the surface nets' quads, smooths away their steps, shades smooth."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    # (split the same way everywhere, not by their shape: the two joints' neighbourhoods, the same but 72 pixels apart,
    # must be triangulated alike to the last bit)
    bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method="FIXED")
    for _ in range(smooth):
        bmesh.ops.smooth_vert(bm, verts=bm.verts[:], factor=0.35, use_axis_x=True, use_axis_y=True, use_axis_z=True)
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.polygons.foreach_set("use_smooth", [True] * len(obj.data.polygons))
    obj.data.update()
    return obj


# --- Colours ----------------------------------------------------------------------------------------------------------

def materials():
    return {i: k.material("arch_rock", palette=i, metallic=0.0, roughness=0.86) for i in range(0x10, 0x20)}


CAP = 0x16                  # the cuts between the pieces (inside the rock where the pieces meet; the feet's ends)


def sample_grid(a, x, y):
    """Bilinear sample of a field on the grid's x, y."""
    u = np.clip((x - X0) / H, 0.0, NX - 1.001)
    v = np.clip((y - Y0) / H, 0.0, NY - 1.001)
    i, j = np.floor(u).astype(int), np.floor(v).astype(int)
    fu, fv = u - i, v - j
    return (a[i, j] * (1 - fu) * (1 - fv) + a[i + 1, j] * fu * (1 - fv) + a[i, j + 1] * (1 - fu) * fv +
            a[i + 1, j + 1] * fu * fv)


def face_data(obj):
    mesh = obj.data
    n = len(mesh.polygons)
    centres = np.empty(3 * n)
    normals = np.empty(3 * n)
    mesh.polygons.foreach_get("center", centres)
    mesh.polygons.foreach_get("normal", normals)
    return centres.reshape(n, 3), normals.reshape(n, 3)


def shades(centres, normals, field, s=None):
    """Each face's palette index: the colours' shade under it (from field, or s), the undersides dark, grained a
    little and banded with the bedding's layers."""
    if s is None:
        s = sample_grid(field, centres[:, 0], centres[:, 1])
    s = np.where(normals[:, 2] < -0.3, np.minimum(s, 4.2), s)
    # The shades' borders broken up a little (the grain of the stone), the same round both joints.
    x, y, z = centres[:, 0], centres[:, 1], centres[:, 2]
    s = s + DITHER * locked(lambda a, b, c: noise3(a / 1.3, b / 1.3, c / 1.3, 41), x, y, z)
    s = s - BANDS * np.cos(2.0 * math.pi * (z + strata_warp(x, y)) / STRATA[1]) * (z > 0.3)
    return 0x10 + np.clip(np.round(s), 2, 14).astype(int)


def assign(obj, indices, mats):
    """Gives the faces the palette materials of their indices (only the materials used)."""
    mesh = obj.data
    used = sorted(set(indices.tolist()))
    mesh.materials.clear()
    for u in used:
        mesh.materials.append(mats[u])
    slot = {u: s for s, u in enumerate(used)}
    mesh.polygons.foreach_set("material_index", [slot[u] for u in indices.tolist()])
    mesh.update()


# --- Pieces -----------------------------------------------------------------------------------------------------------

def cut_piece(whole, box, name):
    """The part of the whole inside box (x0, x1, y0, y1), its cuts closed (caps: material slot 1). Returns the object
    and the indices of its vertices on the cuts."""
    x0, x1, y0, y1 = box
    obj = whole.copy()
    obj.data = whole.data.copy()
    obj.name = obj.data.name = name
    bpy.context.scene.collection.objects.link(obj)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    for co, no in (((x0, 0, 0), (-1, 0, 0)), ((x1, 0, 0), (1, 0, 0)), ((0, y0, 0), (0, -1, 0)), ((0, y1, 0), (0, 1, 0))):
        if not bm.faces:
            break
        res = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-6, plane_co=co,
                                     plane_no=no, clear_outer=True)
        edges = [e for e in res["geom_cut"] if isinstance(e, bmesh.types.BMEdge) and e.is_valid]
        open_edges = [e for e in edges if len(e.link_faces) == 1]
        if open_edges:
            filled = bmesh.ops.holes_fill(bm, edges=open_edges, sides=0)
            if filled["faces"]:
                for f in bmesh.ops.triangulate(bm, faces=filled["faces"])["faces"]:  # facing out of the piece
                    f.normal_update()
                    if f.normal.dot(Vector(no)) < 0:
                        f.normal_flip()
    if not bm.faces:
        bm.free()
        bpy.data.objects.remove(obj)
        return None, set()
    # The caps and their rims, found on the box's planes (a later cut splits an earlier cap into new faces).
    def on_plane(co):
        return min(abs(co.x - x0), abs(co.x - x1), abs(co.y - y0), abs(co.y - y1)) < 1e-4
    bm.normal_update()
    bm.verts.index_update()
    rim = {v.index for v in bm.verts if on_plane(v.co)}
    for f in bm.faces:
        cap = all(v.index in rim for v in f.verts) and (abs(f.normal.x) > 0.999 or abs(f.normal.y) > 0.999)
        f.material_index = 1 if cap else 0
        if cap:
            f.smooth = False
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.materials.clear()
    obj.data.materials.append(bpy.data.materials.get("arch_rock@%d" % 0x18))
    obj.data.materials.append(bpy.data.materials.get("arch_rock@%d" % CAP))
    return obj, rim


def decimate(obj, rim, target):
    """Collapses the rock's triangles to about target, the vertices on the cuts kept where they are (so pieces cut
    from the same rock meet exactly)."""
    n = len(obj.data.polygons)
    if n <= target:
        return obj
    group = obj.vertex_groups.new(name="free")
    free = [i for i in range(len(obj.data.vertices)) if i not in rim]
    group.add(free, 1.0, "REPLACE")
    if rim:
        group.add(sorted(rim), 0.0, "REPLACE")
    mod = obj.modifiers.new("decimate", "DECIMATE")
    mod.decimate_type = "COLLAPSE"
    mod.ratio = target / n
    mod.use_collapse_triangulate = True
    mod.vertex_group = "free"
    mod.vertex_group_factor = 1000.0
    mk.apply(obj)
    obj.vertex_groups.clear()
    return obj


def shade_like(obj, shading):
    """The rock's normals those of the dense whole at the same points (the pieces shade as the whole does, across
    the cuts), the caps flat."""
    mesh = obj.data
    normals = []
    for poly in mesh.polygons:
        flat = poly.material_index == 1
        for li in poly.loop_indices:
            n = None if flat else shading.normal(mesh.vertices[mesh.loops[li].vertex_index].co, poly.center)
            normals.append(tuple(n if n is not None else poly.normal))
    mesh.normals_split_custom_set(normals)


def piece_mask(sheet, piece):
    """The pixels of a piece's sprite it keeps (rows of bools, 24 x 28)."""
    name, sprite, (c, r), keep = piece
    full = k.sprite_mask(sheet, sprite)
    if keep is None:
        return full
    c0, c1, r0, r1 = keep
    return [[full[y][x] and c0 <= c + x < c1 and r0 <= r + y < r1 for x in range(24)] for y in range(28)]


def whole_mask(fl):
    return fl["mask"].tolist()


# --- The nub (3 180) ----------------------------------------------------------------------------------------------------

TIP_SHAPE = ((24.0, 2.0), 62.0, (3.6, 1.8, 1.6))    # its middle (x, y), long axis (degrees), radii (along, across, up)


def tip(mats, field):
    """A small boulder of the same rock: it fills the notch of the left leg where DESERTRUN puts it, and stands as a
    rock of its own where SURFACE puts it (far from the arch). Origin at its cell's centre."""
    hh = 0.15
    xs, ys, zs = np.arange(17.0, 31.0, hh), np.arange(-4.0, 9.0, hh), np.arange(-2.2, 5.0, hh)
    gx, gy, gz = np.meshgrid(xs, ys, zs, indexing="ij")
    (cx, cy), angle, (ra, rc, rz) = TIP_SHAPE
    ux, uy = math.cos(math.radians(angle)), math.sin(math.radians(angle))
    px, py = gx - cx, gy - cy
    along, across = px * ux + py * uy, -px * uy + py * ux
    # higher towards the leg (the sprite's lit top at its lower right), flat underneath under the sand
    rise = 1.0 + 0.15 * along / ra - 0.25 * across / rc
    d = (np.sqrt((along / ra) ** 2 + (across / rc) ** 2 + (gz / (rz * rise)) ** 2) - 1.0) * 1.4
    d = smax(d, -(gz + SKIRT), 0.4)
    flat = d.ravel()
    near = np.abs(flat) < 1.2
    x, y, z = gx.ravel()[near], gy.ravel()[near], gz.ravel()[near]
    flat[near] += 0.22 * noise3(x / 1.6, y / 1.6, z / 1.6, 31) + 0.07 * noise3(x / 0.7, y / 0.7, z / 0.7, 37)
    d = flat.reshape(d.shape)
    verts, quads = surface_nets(d, (xs[0], ys[0], zs[0]), hh)
    obj = finish_whole(mesh_object("desert_rock_tip", verts, quads), smooth=1)
    decimate(obj, set(), 900)
    k.smooth(obj, 180)
    centres, normals = face_data(obj)
    # The leg's lit edge's shades (the sprite's 1a, 19 on its top), darker low round its foot.
    own = np.clip(sample_grid(field, centres[:, 0], centres[:, 1]), 8.5, 11.5)
    own = own - 3.0 * (1.0 - np.clip(normals[:, 2], 0.0, 1.0)) * (centres[:, 2] < 0.6)
    assign(obj, shades(centres, normals, field, own), mats)
    ox, oy = TIP[2][0] + 6.0, 28.0 - TIP[2][1] - 7.0
    obj.data.transform(Matrix.Translation((-ox, -oy, 0.0)))
    obj.data.validate()
    bpy.context.view_layer.update()
    return obj


# --- Build --------------------------------------------------------------------------------------------------------------

TARGET = 5200               # triangles per full piece (fewer for pieces with less rock)


def build():
    options = k.args()
    out = mk.outdir(options)
    only = set(options["only"].split(",")) if "only" in options else None
    sheet = os.path.join(options["check"], "enemy_3.png") if "check" in options else None
    k.reset()
    bpy.context.scene.view_settings.view_transform = "Standard"
    mats = materials()
    fl = fields()
    d = solid(fl)
    t0 = time.time()
    verts, quads = surface_nets(d, (X0, Y0, Z0), H)
    del d
    whole = finish_whole(mesh_object("arch_whole", verts, quads))
    print("whole: %d vertices, %d triangles (%.1f s)" % (len(whole.data.vertices), len(whole.data.polygons),
                                                        time.time() - t0))
    shading = mk.NormalSource(whole)
    dense = len(whole.data.polygons)
    if "whole" in options or sheet:
        preview = whole.copy()
        preview.data = whole.data.copy()
        bpy.context.scene.collection.objects.link(preview)
        centres, normals = face_data(preview)
        assign(preview, shades(centres, normals, fl["paint"]), mats)
        whole.hide_render = True
        if sheet:
            mk.compare("whole (long)", mk.coverage([preview], 204, 56, centre=(102.0, 0.0)), whole_mask(fl))
        if "whole" in options:
            mk.preview(options["whole"] + "rock_arch_whole", [preview], size=(204, 56), scale=6, distance=4.2,
                       centre=(102.0, 0.0))
        bpy.data.objects.remove(preview)
        whole.hide_render = False
    for piece in PIECES:
        name = piece[0]
        if only and name not in only:
            continue
        box, (ox, oy) = kept(piece)
        obj, rim = cut_piece(whole, box, name)
        if obj is None:
            print("== %s: nothing" % name)
            continue
        whole.hide_render = True
        share = len(obj.data.polygons) / max(1.0, dense * 672.0 / (204 * 56))  # of an average piece's
        decimate(obj, rim, int(TARGET * min(1.0, share)))
        shade_like(obj, shading)
        centres, normals = face_data(obj)
        indices = shades(centres, normals, fl["paint"])
        flags = np.empty(len(obj.data.polygons), np.int64)
        obj.data.polygons.foreach_get("material_index", flags)
        indices[flags == 1] = CAP
        assign(obj, indices, mats)
        obj.data.transform(Matrix.Translation((-ox, -oy, 0.0)))
        obj.data.validate()
        bpy.context.view_layer.update()
        if sheet:
            mk.compare("%s (3 %d)" % (name, piece[1]), mk.coverage([obj], 24, 28), piece_mask(sheet, piece))
        mk.report(name, [obj], os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, [obj])
        bpy.data.objects.remove(obj)
        whole.hide_render = False
    if not only or TIP[0] in only:
        for obj in list(bpy.context.scene.objects):
            if obj.type == "MESH":
                obj.hide_render = True
        stone = tip(mats, fl["paint"])
        if sheet:
            mk.compare("%s (3 %d)" % (TIP[0], TIP[1]), mk.coverage([stone], 12, 14), k.sprite_mask(sheet, TIP[1], False))
        mk.report(TIP[0], [stone], os.path.join(out, TIP[0] + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + TIP[0], [stone], size=(12, 14), scale=24)


if __name__ == "__main__":
    build()
