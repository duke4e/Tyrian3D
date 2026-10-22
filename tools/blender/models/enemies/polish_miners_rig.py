"""MINERS's drilling rig, the level's boss (sheet M sprites 191 193 195 above 229 231 233, 2x2 each: one 72 x 52
picture, the lower row 24 pixels under the upper; enemies 1174-1179 of episode 5, ground layer, armour 0: they stay),
and what the level puts on it: its two guns (M 235, enemy 1180), its two hatches (M 197, enemy 1181; frames 199 and
237 open them), its drill (M 267, enemy 1184; frame 269 turns it), its torches (M 275 and 277, enemies 1182, 1183) and
the black egg in its pit (M 271, enemy 1185, the boss: link 254), polished (2026-10-22, round 35; it replaces
wave3_ah_rig.py's rig, a heightfield of pleated stone with lathed parts, wave3_at_m.py's hatch frames and wave2_f.py's
egg, a see-through ellipsoid round nested glowing ones). models.cfg: model drill_rig_tl / _tm / _tr / _bl / _bm / _br,
rig_gun_post, rig_hatch, rig_hatch_199, rig_hatch_237, rig_drill_bit, rig_torch_l, rig_torch_r ... origin and
obsidian_egg (unchanged), the new model rig_drill_bit_269 ... origin and frame m 269 rig_drill_bit_269; every rig
sprite line gets height=-4 (the egg's stays: drawn centred in height, the game rests it on the ground).

Where the level puts it (the level events, tools/content/tyrevents.py; the enemy data, tools/content/tyrdata.py):
MINERS builds it once, at t4472, at the top of the screen (191 at x 126, y -40): 191 193 195 at (x + 24 i, y - 40)
and 229 231 233 at (x + 24 i, y - 16) on the ground layer (link 8), the guns (235) at (x + 4, y - 34) and (x + 44,
y - 34), the hatches (197) at (x - 2, y - 12) and (x + 52, y - 12), the torches (275, 277) at (x - 16, y - 21) and
(x + 64, y - 21), the drill (267) at (x + 24, y - 12) and the egg (271) at (x + 24, y - 40), all on ground 2, each
part with a link of its own; from t4550 the whole moves up the screen as fast as the map scrolls down (global moves,
eyc -1): it stays at the top of the screen, riding up MINERS's two grey rails (the map's long pipes, which run under
its torches). The boss bar is the egg's (link 254): its guns, hatches and torches fire in turns (the hatches open for
it: 197 199 199 237 237 199 199 197, animate 2), the drill turns all the time (267 269 269 267, animate 1); shot, each
part dies alone (the game leaves its slumped wreck), the rig's own pieces cannot be shot; when the egg dies every enemy
on the screen dies with it. In the overlap of its two rows the game draws 231 over 193 and 233 over 195, 191 over 229
(the order the event makes them): the pieces are cut at the lower row's top (24 rows). No other enemy, launched ones
included, shows these sprites; M 277 is 275 mirrored (rig_torch_r is rig_torch_l mirrored); none is another sprite's
pixels turned or in other ramps. Episode 6's CRUSTGATE puts the egg alone on its sand as a mid-boss (t1852): the egg is
a model of its own, resting on the ground in both levels.

As the sprites and their 4x upscales draw it (columns and rows of the 72 x 52 picture; ramp 10's tans 0xa2-0xad, its
outline 0x10): two wings of pleated tan stone, each three broad pleats (8 columns: a lit ridge, a dark fall, a long
lit rise) standing higher towards the middle, their pointed tops stepping up from row 13 (the outer) to rows 4 and 1;
between them a tan block with a deep oval pit in its top (columns 29-42 of rows 4-23, dark, blue lines and a red light
deep in it: the egg lies in it) and in its front a round socket in a grey steel ring (columns 22-49 of rows 26-48,
ramp 0's greys 0x04-0x0a), dark inside, blue lines and orange lights in it (the drill comes out of it); in the wings'
fronts two dark recesses with a red light (columns 3-17 and 54-68 of rows 37-45: the hatches stand in them); under the
wings two grey clamps (columns 5-17 and 54-66 of rows 47-51). On it: the guns, tan barrels lying up the screen on the
wings (235: columns 7-16, an orange light round their middle, rows 9-10, 0x78-0x7e); the hatches, tan cabinets with
two doors (197: columns 5-18 of rows 9-17), which slide apart on a red light (199: a gap of 5 columns, 237: 9); the
drill, a grey cone with spiral flutes coming out of the socket and digging into the ground in front of the rig (267,
269: the flutes a sixth of a turn on); the torches, tan poles beside the rig with a lamp at their heads, its flame on
their outer side (275 / 277); the egg, black glass with a smoky light inside (271: 0x60 round greys 0x01-0x0d).

Built for the game's camera: everything is designed in the picture's plane (x, y as the picture draws them, z up, the
camera looking straight down) and then sheared along the game camera's line of sight (y - z tan 20:
polish_lava_grub.py's way, as polish_rock_column.py and polish_tan_dome.py are), so that the camera sees every part
where its sprite draws it. The rig's body is a signed distance field on a grid H pixels apart (polish_rock_arch.py's
surface nets): a heightfield over its outline (the pleats' tops PLEAT_H, the middle block TOP_H, the corrugation's
sawtooth across them as drawn, the wings' fronts falling to the ground over FRONT, the socket's slope over the middle),
its sides rounded; the pit, the socket's bore and the recesses carved out of it, deep and dark (0xa1), the blue lines
(0xd5, emission 0.25) and the lights (0x78, 0.4) on their floors where the picture has them. The steel ring round the
socket is a round tube on the slope (0x07, lit 0x0b); the clamps steel bars with prongs. Its colours are the picture's
own tans under each face (the broad shading kept in part round MID, the fine kept). The steel parts take
polish_asteroid_rig.py's way of painting by the light (its paint_light), as the two rigs' steel does. The guns are
lathed tan capsules lying on the wings, an orange ring glowing between their halves (0x7a, 0.45); the hatches tan
cabinets standing in the recesses, their doors sliding apart in the frames on a red light (0x46 0.38, 0x48 0.5); the
drill a cone turned about its axis, from a rounded back in the socket to its point in the ground, three spiral flutes
cut into it (steel 0x06 0x0a 0x0d, its grooves ramp 6's 0x67), the frame model the same cone turned a sixth of a turn;
the torches tan poles leaning back from their feet on the rails, a lamp head with its flame glowing on its outer side
(0x78 0.4, 0x7c 0.55); the egg a lathed lemon of glossy black glass (0x60) lying in the pit on the ground, its smoky
light in bands on its top where the picture draws it (greys 0x05 0x08 0x0a 0x0d glowing 0.12-0.35).

The body is cut along the planes the camera sees as the sprites' edges (x = -12 and 12; y + tan 20 z = 2: the lower
row's top) into its six pieces (polish_rock_column.cut_piece; its caps in the stone's inside colour), each piece's
triangles reduced to TARGET with its cuts' vertices kept and its normals those of the dense whole, the ring and the
clamps cut the same way (polish_stone_face.view_cut); each piece moved so that its sprite's centre is its origin. The
parts are built at their places on the rig and moved to their own sprites' centres.

Coordinates: 1 unit = 1 game pixel; +X right, +Y up the screen, +Z up from the ground (z = 0); the whole's origin is
the picture's middle (column 36, row 26): the pixel corner (c, r) is (c - 36, 26 - r). The pieces' centres: 191 (-24,
12), 193 (0, 12), 195 (24, 12), 229 (-24, -12), 231 (0, -12), 233 (24, -12); the parts': the guns (-20, 6) and (20,
6), the hatches (-26, -16) and (28, -16), the torches (-40, -7) and (40, -7), the drill (0, -16), the egg (0, 12). Drawn
at their origins (origin) on the ground layers: height=-4 sets the rig on the terrain (MINERS's ground is level under
the rails); the egg is drawn centred in height and rests on the ground, in the pit, whose floor is the ground.

Replaces wave3_ah_rig.py (all of it), wave3_at_m.py (all of it: the hatch's frames) and wave2_f.py (all of it: the
egg was all it built; its TWIN pixels were read by nothing); with wave3_ah.py and wave3_ah_rock.py gone too, nothing
imports wave3_ah_kit.py or wave3_ah_art.py (the rig's RIG, RIG_ALL, HATCH, HATCH_OPEN, GUN, DRILL, TORCH_L, TORCH_R):
both go. wave3_ap_kit.py's cut_plane() and split() (wave3_ah_kit's, for wave3_ap_miners.py only) go with them, and
so do the other helpers only round 35's removed MINERS scripts used: wave3_z_kit.py's model, move(), rotate_about(),
field(), field_sampler(), bands(), nearest_band(), paint_by(), jitter() and its assembly previews, wave3_at_kit.py's
fire_mats() and fireball(), wave2_f_kit.py's art(), its registry (model(), main()) and its output paths.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each piece's and part's
silhouette as the camera sees it against its sprite's pixels), --preview <prefix>, --whole <prefix> (the rig with all
its parts: views and GLB), --only <name,...>.
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
                              assign, decimate, shade_like, nearest)
from polish_k_pod import triangulate  # noqa: E402
from polish_deli_boss import join, drop_unused  # noqa: E402
from polish_stone_face import view_cut  # noqa: E402
from polish_rock_column import drop_islands, shear_to_camera, cut_piece, view_coverage, TILT  # noqa: E402
from polish_asteroid_rig import paint_light as rig_paint_light  # noqa: E402

LIGHT = Vector((-0.55, 0.45, 0.7)).normalized()

# The bare rig's picture (72 x 52, the six sprites as the game draws them), a character per pixel: a hex digit its
# shade (ramps 10, 11 and 1: the tans and browns), g-v ramp 0's greys (shade 0-15: the ring, the clamps), B the blue
# lines (ramp 13), R the red and orange lights (ramp 7); '.' none.
ART = """
................................00000000................................
.....................000.0000000667888760000000.000.....................
....................0abd055566666667777766778550abd0....................
..............00..0088abc556666655666668876775588abc00..00..............
.............0db0066988bb5666555552222798986655988bb5400ca0.............
............0abdd7549888a66655555211112799976559888a7549bdb0............
............09aab7659889966555552111111289a97559889976589bc0............
......00..00889b97658899a66555521111111128998658899a765889b900..00......
.....0db006698a9a7658999b65555211111111112898658999b76598a9a5400dd0.....
....0abdc7548aa9b7658899a66555211100011112788658899a7658aa9b7549bbd0....
....09aac7658899a7658889966552110BBBBBB11127865888997658899a76597bb0....
...09878b765888997658899b6555210000000B111267658899b765888997659877b0...
..069887b7658a99b7558888b6555210111110B001267658888b7558a99b7659887b80..
.0669b87b7658888b6558889b6652111111110B101127658889b6558888b7659b87b790.
07659cb9b76598a9b655889a95652110BBBB0BB10012765889a965598a9b7659cb9b7790
07659ba9c765889a975589aa95652110B1111001111276589aa9755889a97659ba9c6770
07659b89c76589ab9765899a95652110B01111100012755899a976589ab97659b89c6670
07659887b765899a9765888ab66521010B11BBBB1002755888ab765899a97659887b6780
07658777b76588a9b7658888b6562111101R000B11127558888b76588a9b7658777b7880
07658977b755988ab7658888b6542111101RR10B01127558888b765988ab7558977b6780
07559997b6559889b7658899b6542110B000001B01127558899b7659889b6559997b6670
06559a9796558899c76589aab6544210B1111001012765589aab7658899c6559a9796670
06559aa7975589aac7658aaac6544210BBBB1R1101276558aaac76589aac7559aa795670
07559aa797658aaac76589aab6554211000B0RR0112665589aab7658aaac7659aa795670
07659a97b76589aab765889ab66665545522226688665558998b7658998b765877897880
07658977b765889ab7658889b6666676656aba88aa866558989b7658998c765878897880
07658977b765888997658988b566677kmllmpmlkkbb865588aab7658989c7658789b6780
076587789765898897658998b5667kknpqqpnnppnklb8558aaab76588aab7659889b6670
07659988b7658aaab7659aaa9567mmnnnpppppqqpnnp9559aaa97658aaab7659988b6670
0765878ab7659aaa9775aabba55npnnn00000000qqpnl76aabba7759aaa9765878ab6670
0765898bb765aabba887abccb5mppn000000000000qpnk4abccb887aabba765898bb6670
07659bbbc8878bccb77589998kmn0000000000000000pnk988897758bccb8879bbbc6770
08879ccb8665698895559778knn000000111111000000pnk9889555698896659ccb87870
0665898895456877a554977knn00001111001111100000pnk9895546877a545898896660
05457778955469879654977kn0000111j0jjR1111100000nk97965469879554777895560
0554887796546889966485knm0001111i0j011R111h1000pnk7a66468899654887797550
06548997a7648abba84585kn00011111h0j111B111i11110nk8a6458abba7648997a8750
0764000000000000077685jm01111hijkjk11BB000j01110nm7a64400000000000007760
05500000ii0j0000007695jm0110R110h01BBB0kijj00110pm795500330ii00033000660
05500033RRii3320005695km0110R111i01B110i00011110pk7955000233RRB322000560
05400i233RR332200045a5jl0110RRRRj0BB100j01111110nk7954000222RRR220000450
05402i023RR32j022045a7jkl0111Rjjk0B00kjj1011110mnk795402000RRRR0ij220450
06401200RRR0Bi221045975jl011110001B00j011011110nk57a640120j0RR00i2210450
0650111i001111211056975jkl01111R11B01R00100110nmk58a650111ii111122110560
064011101111111100648855jml0111RR000011001110nmk578a6401111i001111110640
0643000000000000064588756jml0011111100100100nmk5777a64300000000000003450
.0645555566344454546877574jmll001111101100mmmk4777996645555566654454540.
..0005660000076600000997000jjmkl00000000nmmkk0009aa0000056600000655000..
.....000l0klk0000....000...00jjkkklllmmmmkk00...000....0000klk0l000.....
.......0r0prpp0r0............00jjjjkkkkkk00............0r0prpo0r0.......
.......0p000000p0..............0000000000..............0p000000p0.......
........0......0........................................0......0........
"""
# The egg's picture (rows 1-25 of M 271): 0 its black glass (0x60), a hex digit the smoky light's grey shade.
EGG_ART = """
..........0000..........
.........000000.........
........00010000........
.......0000110000.......
......000011111000......
......000011111100......
.....00000121111000.....
.....00001122211100.....
.....00001332222100.....
....0000134333221100....
....0001359754322100....
....000247ca97332100....
....000235adca432100....
....0001359cdc533100....
....0001247acd941000....
....00001359ad941000....
....000002479c530000....
.....00001245741000.....
.....00000134530000.....
.....00000023410000.....
......000000110000......
......000000010000......
.......0000000000.......
........00000000........
..........0000..........
"""

PIECES = [("drill_rig_tl", 191, (None, -12.0, 2.0, None), (-24.0, 12.0)),
          ("drill_rig_tm", 193, (-12.0, 12.0, 2.0, None), (0.0, 12.0)),
          ("drill_rig_tr", 195, (12.0, None, 2.0, None), (24.0, 12.0)),
          ("drill_rig_bl", 229, (None, -12.0, None, 2.0), (-24.0, -12.0)),
          ("drill_rig_bm", 231, (-12.0, 12.0, None, 2.0), (0.0, -12.0)),
          ("drill_rig_br", 233, (12.0, None, None, 2.0), (24.0, -12.0))]
GUN_AT = [(-20.0, 6.0), (20.0, 6.0)]
HATCH_AT = [(-26.0, -16.0), (28.0, -16.0)]
TORCH_AT = [(-40.0, -7.0), (40.0, -7.0)]
DRILL_AT = (0.0, -16.0)
EGG_AT = (0.0, 12.0)

# --- The body (in the picture's plane) ----------------------------------------------------------------------------------
PLEAT_H = [(28.0, 8.0), (20.0, 10.5), (0.0, 13.0)]   # (|x| from, the pleats' height): the outer, the middle, the inner
TOP_H = 13.0                                        # the middle block's top
SAW_LEFT, SAW_RIGHT, SAW_AMP = -27.5, 15.5, 2.3     # the corrugation's ridges (columns 8 and 51 and every 8), its depth
FRONT = (-20.6, -10.5)                              # the wings' fronts: from the ground (row 46.6) to their tops (row 36.5)
SOCKET_SLOPE = (-21.6, 1.2)                         # the middle's slope: the ground at row 47.6, the top at row 24.8
SOCKET = dict(x=-0.5, y=-11.5, rx=12.4, ry=10.4, ring=1.9, bore=(10.0, 8.6))
PIT = dict(x=-0.5, y=12.4, rx=8.6, ry=12.9)
RECESSES = [(-33.2, -18.2, -19.6, -11.0), (18.2, 33.2, -19.6, -11.0)]   # (x0, x1, y0, y1)
RECESS_DEPTH = 2.6
FLOOR = -0.3                                        # the hollows' floors (the pit's: the ground, where the egg rests)
SKIRT = 1.5
NOISE = ((0.12, 2.6), (0.05, 1.1))
RELIEF = 0.12
H = 0.35
X0, NX = -37.4, 215
Y0, NY = -24.8, 152
Z0, NZ = -2.4, 58
XS = X0 + H * np.arange(NX)
YS = Y0 + H * np.arange(NY)
ZS = Z0 + H * np.arange(NZ)
MID, KEEP, DETAIL, DITHER = 8.4, 0.6, 0.9, 0.3
CAP = 0xa4
HOLLOW, CIRCUIT, LIGHT_RED = 0xa1, 0xd5, 0x78
TARGET = 5200


def smoothstep(e0, e1, x):
    t = np.clip((np.asarray(x, dtype=np.float64) - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def art():
    """The rig's arrays (52 x 72): the tan shades (nan elsewhere), the outline mask, the blue lines and the lights."""
    shade = np.full((52, 72), np.nan)
    own = np.zeros((52, 72), bool)
    blue = np.zeros((52, 72), bool)
    red = np.zeros((52, 72), bool)
    for r, line in enumerate(ART.strip("\n").split("\n")):
        for c, ch in enumerate(line):
            if ch == ".":
                continue
            own[r, c] = True
            if ch in "0123456789abcdef":
                shade[r, c] = int(ch, 16)
            elif ch in "ghijklmnopqrstuv":
                shade[r, c] = 3.0
            elif ch == "B":
                shade[r, c], blue[r, c] = 1.0, True
            elif ch == "R":
                shade[r, c], red[r, c] = 2.0, True
    return shade, own, blue, red


def sample(a, x, y, pad=0.0):
    rows, cols = a.shape
    u, v = x + 36.0 - 0.5, 25.5 - y
    c0, r0 = np.floor(u).astype(int), np.floor(v).astype(int)
    fu, fv = u - c0, v - r0

    def at(r, c):
        ok = (r >= 0) & (r < rows) & (c >= 0) & (c < cols)
        return np.where(ok, a[np.clip(r, 0, rows - 1), np.clip(c, 0, cols - 1)], pad)
    return ((1 - fu) * (1 - fv) * at(r0, c0) + fu * (1 - fv) * at(r0, c0 + 1) + (1 - fu) * fv * at(r0 + 1, c0) +
            fu * fv * at(r0 + 1, c0 + 1))


def blur(a, sigma):
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
    u = np.clip((x - X0) / H, 0.0, NX - 1.001)
    v = np.clip((y - Y0) / H, 0.0, NY - 1.001)
    i, j = np.floor(u).astype(int), np.floor(v).astype(int)
    fu, fv = u - i, v - j
    return (a[i, j] * (1 - fu) * (1 - fv) + a[i + 1, j] * fu * (1 - fv) + a[i, j + 1] * (1 - fu) * fv +
            a[i + 1, j + 1] * fu * fv)


def contour(f, level=0.5):
    pts = []
    a, b = f[:-1, :], f[1:, :]
    i, j = np.nonzero((a - level) * (b - level) < 0)
    t = (level - a[i, j]) / (b[i, j] - a[i, j])
    pts.append(np.stack([XS[i] + t * H, YS[j]], 1))
    a, b = f[:, :-1], f[:, 1:]
    i, j = np.nonzero((a - level) * (b - level) < 0)
    t = (level - a[i, j]) / (b[i, j] - a[i, j])
    pts.append(np.stack([XS[i], YS[j] + t * H], 1))
    return np.concatenate(pts)


def fields():
    shade, own, blue, red = art()
    body = own.copy()
    body[47:, :] = False                                 # (the clamps under the wings are parts of their own)
    gx, gy = np.meshgrid(XS, YS, indexing="ij")
    mf = blur(sample(body.astype(np.float64), gx, gy), 0.4)
    pts = contour(mf)
    (d,) = nearest(gx.ravel(), gy.ravel(), pts)
    d = d.reshape(gx.shape).astype(np.float64)
    side = np.where(mf >= 0.5, -d, d)
    filled = fill_outside(shade)
    s_px = sample(filled, gx, gy)
    fine, mid, broad = blur(s_px, 0.5), blur(s_px, 1.6), blur(s_px, 4.5)
    local = blur(s_px, 0.6)
    paint = MID + (broad - MID) * KEEP + DETAIL * (local - broad)
    return {"side": side, "paint": paint, "relief": fine - mid, "own": own, "body": body,
            "blue": blur(sample(blue.astype(np.float64), gx, gy), 0.35),
            "red": blur(sample(red.astype(np.float64), gx, gy), 0.35)}


def saw(x):
    """The corrugation (1 on a ridge): a steep fall to the right of each ridge, a long rise to the next, as drawn."""
    phase = np.where(x < 0, (x - SAW_LEFT) % 8.0, (x - SAW_RIGHT) % 8.0)
    fall = 1.0 - smoothstep(0.0, 2.6, phase)
    rise = smoothstep(2.6, 8.0, phase)
    return np.maximum(fall, rise)


def top_height(x, y):
    ax = np.abs(x + 0.5)
    base = np.full(x.shape, PLEAT_H[-1][1])
    for edge, h in PLEAT_H[:-1][::-1]:
        base = np.where(ax >= edge, h, base)
    wing = smoothstep(7.0, 9.0, ax)
    base = base + SAW_AMP * (saw(x) - 0.6) * wing
    wing_front = 1.0 + (base - 1.0) * smoothstep(FRONT[0], FRONT[1], y)
    mid_front = 1.0 + (TOP_H - 1.0) * np.clip((y - SOCKET_SLOPE[0]) / (SOCKET_SLOPE[1] - SOCKET_SLOPE[0]), 0.0, 1.0)
    blend = smoothstep(13.5, 16.0, ax)
    return wing_front * blend + mid_front * (1.0 - blend)


def hollows(gx, gy, gz, tops):
    """The pit, the socket's bore and the recesses: their solids' distances (negative inside), to carve."""
    p = PIT
    pit = (np.sqrt(((gx - p["x"]) / p["rx"]) ** 2 + ((gy - p["y"]) / p["ry"]) ** 2) - 1.0) * min(p["rx"], p["ry"])
    s = SOCKET
    bx, by = s["bore"]
    bore = (np.sqrt(((gx - s["x"]) / bx) ** 2 + ((gy - s["y"]) / by) ** 2) - 1.0) * min(bx, by)
    holes = np.maximum(np.minimum(pit, bore), FLOOR - gz)
    for x0, x1, y0, y1 in RECESSES:
        box = np.maximum(np.maximum(x0 - gx, gx - x1), np.maximum(y0 - gy, gy - y1))
        holes = np.minimum(holes, np.maximum(box, (tops - RECESS_DEPTH) - gz))
    return holes


def solid(fl):
    t0 = time.time()
    gx, gy = np.meshgrid(XS, YS, indexing="ij")
    tops2 = top_height(gx, gy) + RELIEF * fl["relief"]
    tops = tops2[:, :, None]
    gz = ZS[None, None, :]
    d = smax(fl["side"][:, :, None], gz - tops, 1.0)
    d = np.maximum(d, -SKIRT - gz)
    d = np.maximum(d, -hollows(gx[:, :, None], gy[:, :, None], gz, tops)).astype(np.float32)
    i, j, kz = np.nonzero(np.abs(d) < 2.0)
    x, y, zz = XS[i], YS[j], ZS[kz]
    detail = np.zeros(len(i))
    for n, (amp, scale) in enumerate(NOISE):
        detail += amp * noise3(x / scale, y / scale, zz / scale, 31 + n)
    d[i, j, kz] += detail.astype(np.float32)
    for axis in range(3):
        p = np.pad(d, [(1, 1) if ax == axis else (0, 0) for ax in range(3)], mode="edge")
        d = 0.25 * np.take(p, range(0, d.shape[axis]), axis=axis) + 0.5 * d + \
            0.25 * np.take(p, range(2, d.shape[axis] + 2), axis=axis)
    print("solid: %.1f s" % (time.time() - t0))
    return d.astype(np.float32), tops2


# --- Colours ------------------------------------------------------------------------------------------------------------

def mat(name, index, metallic=0.3, roughness=0.45, glow=None):
    if glow is not None:
        return k.material(name, palette=index, metallic=0.0, roughness=0.4, emission=k.level_palette()[index],
                          emission_strength=glow)
    return k.material(name, palette=index, metallic=metallic, roughness=roughness)


def materials():
    m = {i: mat("rig_stone", i, 0.1, 0.62) for i in range(0xa3, 0xad)}
    m.update({HOLLOW: mat("rig_hollow", HOLLOW, 0.1, 0.8), CIRCUIT: mat("rig_circuit", CIRCUIT, glow=0.25),
              LIGHT_RED: mat("rig_light", LIGHT_RED, glow=0.4),
              "steel": mat("rig_steel", 0x07, 0.45, 0.32), "steel_lit": mat("rig_steel_lit", 0x0b, 0.45, 0.3),
              "tan": mat("rig_tan", 0xa8, 0.25, 0.45), "tan_lit": mat("rig_tan_lit", 0xab, 0.25, 0.42),
              "tan_dark": mat("rig_tan_dark", 0xa5, 0.25, 0.48), "outline": mat("rig_outline", 0xa2, 0.2, 0.6),
              "egg": mat("rig_egg", 0x60, 0.35, 0.1), "egg_smoke": mat("rig_egg_smoke", 0x05, glow=0.12),
              "egg_glow": mat("rig_egg_glow", 0x08, glow=0.2), "egg_bright": mat("rig_egg_bright", 0x0a, glow=0.28),
              "egg_core": mat("rig_egg_core", 0x0d, glow=0.35)})
    return m


def shades(centres, normals, fl, tops):
    x, y, z = centres[:, 0], centres[:, 1], centres[:, 2]
    py = y + TILT * z
    s = sample_grid(fl["paint"], x, py)
    s = s + DITHER * noise3(x / 1.1, py / 1.1, z / 1.1, 37)
    s = np.where(normals[:, 2] < -0.35, np.minimum(s, 4.0), s)
    idx = 0xa0 + np.clip(np.round(s), 3, 12).astype(int)
    deep = z < sample_grid(tops, x, py) - 1.4                       # inside the pit, the bore, the recesses
    idx = np.where(deep, HOLLOW, idx)
    up = normals[:, 2] > 0.5
    idx = np.where(deep & up & (sample_grid(fl["blue"], x, py) > 0.4), CIRCUIT, idx)
    idx = np.where(deep & up & (sample_grid(fl["red"], x, py) > 0.4), LIGHT_RED, idx)
    return idx


# --- The ring and the clamps ---------------------------------------------------------------------------------------------

def sheared(p):
    return Vector((p.x, p.y - TILT * p.z, p.z))


def slope_z(y):
    return 1.0 + (TOP_H - 1.0) * min(1.0, max(0.0, (y - SOCKET_SLOPE[0]) / (SOCKET_SLOPE[1] - SOCKET_SLOPE[0])))


def ring(m):
    """The steel ring round the socket: a round tube along an ellipse on the slope, its top lit."""
    s = SOCKET
    pts = []
    n = 72
    for i in range(n):
        a = 2 * math.pi * i / n
        x, y = s["x"] + s["rx"] * math.cos(a), s["y"] + s["ry"] * math.sin(a)
        pts.append(sheared(Vector((x, y, slope_z(y) + 0.5))))
    rings = []
    seg = 14
    for i, p in enumerate(pts):
        t = (pts[(i + 1) % n] - pts[i - 1]).normalized()
        out = Vector((math.cos(2 * math.pi * i / n), math.sin(2 * math.pi * i / n), 0.0))
        a = t.cross(out).normalized()
        if a.z < 0:
            a = -a
        b = t.cross(a).normalized()
        rings.append([p + (a * math.cos(2 * math.pi * j / seg) + b * math.sin(2 * math.pi * j / seg)) * s["ring"]
                      for j in range(seg)])
    verts = [v for r in rings for v in r]
    faces = []
    for i in range(n):
        for j in range(seg):
            a0, a1 = i * seg + j, i * seg + (j + 1) % seg
            b0, b1 = ((i + 1) % n) * seg + j, ((i + 1) % n) * seg + (j + 1) % seg
            faces.append((a0, a1, b1, b0))
    obj = k.mesh_object("socket_ring", verts, faces, m["steel"])
    k.recalc_normals(obj)
    k.smooth(obj, 60)
    rig_paint_light(obj, m, "steel", "steel_lit", "steel", lit_at=0.5)
    return obj


def clamps(m):
    """The grey clamps under the wings (columns 5-17 and 54-66 of rows 47-51): a bar along the wing's foot, two prongs
    down into the ground."""
    out = []
    for i, (c0, c1) in enumerate(((7.0, 16.0), (56.0, 65.0))):
        x0, x1 = c0 - 36.0, c1 - 36.0
        y = 26.0 - 48.6
        bar = mk.box(f"clamp{i}", x0 - 0.2, x1 + 0.2, y - 0.9, y + 0.9, 0.6, 2.6, m["steel"])
        mk.bevel(bar, 0.35, 2, 35)
        mk.shade(bar, 35)
        out.append(bar)
        for j, x in enumerate((x0 + 0.6, x1 - 0.6)):
            prong = mk.tube(f"prong{i}{j}", [Vector((x, y, 1.6)), Vector((x, y - 2.2, 0.8)), Vector((x, y - 3.0, -0.6))],
                            0.7, m["steel"], 10, radii=[0.8, 0.65, 0.35])
            out.append(prong)
        for o in out[-3:]:
            rig_paint_light(o, m, "steel", "steel_lit", "steel", lit_at=0.45)
    return out


# --- The parts ------------------------------------------------------------------------------------------------------------

def lathe_y(name, profile, centre, mat_, segments=32):
    """A body turned about an axis along y through centre (x, z): profile [(y, radius), ...]."""
    cx, cz = centre
    rings = []
    for y, r in profile:
        rings.append([Vector((cx + r * math.cos(2 * math.pi * j / segments), y, cz + r * math.sin(2 * math.pi * j / segments)))
                      for j in range(segments)])
    return k.loft(name, rings, mat_, start_point=(cx, profile[0][0], cz), end_point=(cx, profile[-1][0], cz))


def sheared_parts(parts):
    for o in parts:
        shear_to_camera(o)
    return parts


def gun(m, at):
    """A gun on a wing (M 235): a tan capsule lying up the screen, its two halves parted by an orange ring."""
    ax, ay = at
    x = ax + 0.1
    z = 15.6
    y_top, y_light, y_bot = ay + 13.5, ay + 4.0, ay - 12.6
    back = lathe_y("gun_back", [(y_top, 0.2), (y_top - 0.6, 2.6), (y_top - 1.6, 4.0), (y_top - 3.0, 4.6),
                                (y_light + 1.6, 4.6), (y_light + 1.0, 3.8)], (x, z), m["tan"])
    front = lathe_y("gun_front", [(y_light - 1.0, 3.8), (y_light - 1.6, 4.6), (y_bot + 4.0, 4.6), (y_bot + 2.4, 4.1),
                                  (y_bot + 1.0, 2.8), (y_bot + 0.2, 1.2)], (x, z), m["tan"])
    glow = lathe_y("gun_light", [(y_light + 1.2, 3.4), (y_light + 0.6, 3.6), (y_light - 0.6, 3.6),
                                 (y_light - 1.2, 3.4)], (x, z), mat("rig_gun_glow", 0x7a, glow=0.45))
    muzzle = lathe_y("gun_muzzle", [(y_bot + 1.4, 1.9), (y_bot + 0.1, 1.7), (y_bot - 0.3, 0.6)], (x, z), m["outline"])
    parts = [back, front, glow, muzzle]
    for p in (back, front):
        k.smooth(p, 50)
        rig_paint_light(p, m, "tan", "tan_lit", "tan_dark", lit_at=0.6, dark_at=0.15)
    mount = mk.box("gun_mount", x - 2.6, x + 2.6, y_bot + 2.0, y_top - 2.0, 10.0, z - 2.0, m["tan_dark"])
    mk.bevel(mount, 0.6, 2, 35)
    parts.append(mount)
    return sheared_parts(parts)


def hatch(m, at, gap=0.0, glow=0.0):
    """A hatch (M 197): a tan cabinet standing in its recess, two doors in its front sliding apart by gap on a red
    light glowing glow."""
    ax, ay = at
    x0, x1 = ax - 7.5 + 0.4, ax + 7.5 - 0.6
    y0, y1 = ay - 3.7, ay + 4.6
    zb, zt = 1.0, 9.0
    box = mk.box("hatch_box", x0, x1, y0, y1, zb, zt, m["tan"])
    mk.bevel(box, 0.7, 3, 35)
    mk.shade(box, 35)
    rig_paint_light(box, m, "tan", "tan_lit", "tan_dark", lit_at=0.62, dark_at=0.2)
    parts = [box]
    xm = ax - 0.3
    inner = mk.box("hatch_inside", xm - 4.6, xm + 4.6, y0 + 0.5, y1 - 1.2, zt - 0.6, zt + 0.25, m["outline"])
    parts.append(inner)
    if gap > 0:
        light = mk.ball("hatch_light", (xm, (y0 + y1) / 2 - 0.4, zt + 0.1), (gap / 2, 1.8 + 0.1 * gap, 0.6),
                        mat("rig_hatch_light_%d" % int(glow * 100), 0x46 if glow < 0.45 else 0x48, glow=glow), 16, 8)
        parts.append(light)
    for i, side in enumerate((-1, 1)):
        a = xm + side * (0.2 + gap / 2)
        b = xm + side * 4.4
        lo, hi = min(a, b), max(a, b)
        if hi - lo < 0.5:
            continue
        door = mk.box(f"hatch_door{i}", lo, hi, y0 + 0.5, y1 - 1.5, zt - 0.2, zt + 0.55, m["tan_lit"])
        mk.bevel(door, 0.25, 2, 35)
        mk.paint(door, lambda c, n: m["tan_dark"] if n.z < 0.6 and n.dot(LIGHT) < 0.3 else None)
        parts.append(door)
    return sheared_parts(parts)


DRILL_ROWS = [(0.0, 0.3), (0.8, 3.6), (2.0, 6.2), (3.2, 8.2), (4.6, 9.6), (6.5, 10.4), (9.0, 10.6), (11.5, 10.3),
              (13.5, 9.3), (16.0, 7.8), (19.0, 5.6), (22.0, 3.4), (24.5, 1.8), (26.2, 0.4)]


def drill(m, at, turn=0.0):
    """The drill (M 267): a cone turned about an axis from the socket, through the bore, down the screen and into the
    ground in front of the rig; three spiral flutes; turn: how far it is turned (turns)."""
    ax, ay = at
    base = Vector((ax - 0.5, ay + 12.7, 8.2))           # its rounded back, in the socket (drawn at row 29.3)
    tip = Vector((ax - 0.5, ay - 13.4, -0.4))           # its point, in the ground (row 55.4)
    axis = tip - base
    length = axis.length
    d = axis.normalized()
    side = Vector((1.0, 0.0, 0.0))
    up = d.cross(side).normalized()
    if up.z < 0:
        up = -up
    rows = DRILL_ROWS
    span = rows[-1][0]
    seg, n = 48, 60
    starts, pitch = 3, 9.0
    verts, faces = [], []
    for i in range(n + 1):
        t = i / n * span
        r = float(np.interp(t, [p[0] for p in rows], [p[1] for p in rows]))
        c = base + d * (t / span * length)
        for j in range(seg):
            a = 2 * math.pi * j / seg
            phase = (a / (2 * math.pi) * starts + t / pitch + turn * starts) % 1.0
            groove = 0.16 * max(0.0, math.cos(2 * math.pi * phase)) ** 6
            rr = max(0.05, r * (1.0 - groove))
            verts.append(c + (side * math.cos(a) + up * math.sin(a)) * rr)
    for i in range(n):
        for j in range(seg):
            a0, a1 = i * seg + j, i * seg + (j + 1) % seg
            faces.append((a0, a1, a1 + seg, a0 + seg))
    verts.append(base - d * 0.05)
    verts.append(tip + d * 0.05)
    cb, ct = len(verts) - 2, len(verts) - 1
    faces += [((j + 1) % seg, j, cb) for j in range(seg)]
    faces += [(n * seg + j, n * seg + (j + 1) % seg, ct) for j in range(seg)]
    obj = k.mesh_object("drill", verts, faces, m["steel_lit"])
    k.recalc_normals(obj)
    k.smooth(obj, 50)
    groove_m, land_lit = mat("rig_drill_groove", 0x67, 0.35, 0.4), mat("rig_drill_lit", 0x0d, 0.35, 0.28)
    dark = mat("rig_drill_dark", 0x06, 0.35, 0.4)
    land = mat("rig_drill_land", 0x0a, 0.35, 0.32)

    def pick(cc, nn):
        rel = cc - base
        t = rel.dot(d) / length * span
        a = math.atan2(rel.dot(up), rel.dot(side))
        phase = (a / (2 * math.pi) * starts + t / pitch + turn * starts) % 1.0
        if phase < 0.18 or phase > 0.82:
            return groove_m
        dl = nn.dot(LIGHT)
        return land_lit if dl > 0.7 else dark if dl < 0.15 else land
    mk.paint(obj, pick)
    return sheared_parts([obj])


def torch(m, at, side):
    """A torch beside the rig (M 275, side -1; 277 is its mirror image): a tan pole leaning back from its foot on the
    rail, a lamp head at its top, its flame glowing on its outer side."""
    ax, ay = at
    x = ax - side * 1.0
    foot = Vector((x, ay - 12.6, 0.0))
    neck = Vector((x, ay + 3.6, 10.0))
    head_c = Vector((x - side * 0.2, ay + 8.7, 12.4))
    pole = mk.tube("torch_pole", [foot, foot.lerp(neck, 0.5), neck], 1.9, m["tan"], 14, radii=[1.7, 1.9, 2.1])
    k.smooth(pole, 50)
    rig_paint_light(pole, m, "tan", "tan_lit", "tan_dark", lit_at=0.5)
    collar = mk.ball("torch_collar", tuple(neck + Vector((0.0, 0.6, 0.4))), (2.6, 1.8, 2.0), m["tan_dark"], 16, 8)
    head = mk.ball("torch_head", tuple(head_c), (3.3, 4.8, 3.0), m["tan"], 20, 10)
    rig_paint_light(head, m, "tan", "tan_lit", "tan_dark", lit_at=0.55)
    flame = mk.ball("torch_flame", tuple(head_c + Vector((side * 2.6, 0.0, 0.3))), (1.7, 3.8, 2.2),
                    mat("rig_flame", 0x78, glow=0.4), 16, 8)
    core = mk.ball("torch_core", tuple(head_c + Vector((side * 3.4, 0.2, 0.4))), (0.9, 2.4, 1.4),
                   mat("rig_flame_core", 0x7c, glow=0.55), 12, 6)
    return sheared_parts([pole, collar, head, flame, core])


def egg(m):
    """The black egg (M 271) lying in the pit: a lemon of glossy black glass, its smoky light painted on its top
    where the picture draws it (the picture's greys interpolated: smooth bands), glowing a little."""
    ex, ey = EGG_AT
    cx, cy = ex - 0.5, ey + 0.5                     # its outline's middle (column 11.5, row 13 of its sprite)
    rx, ry, rz = 8.1, 12.5, 6.4
    # a lemon of an egg: its outline pointed at both ends, as drawn (its radius falling as (1 - t^2) ** 0.72)
    profile = [(cy + ry * t, max(0.01, rx * (1.0 - t * t) ** 0.72)) for t in np.linspace(-1.0, 1.0, 37)]
    obj = lathe_y("egg", profile, (cx, rz), m["egg"], 72)
    for v in obj.data.vertices:
        v.co.z = rz + (v.co.z - rz) * rz / rx
    obj.data.update()
    k.smooth(obj, 80)
    grid = np.zeros((28, 24))
    for line_i, line in enumerate(EGG_ART.strip("\n").split("\n")):
        for c, ch in enumerate(line):
            if ch not in ".0":
                grid[line_i + 1, c] = int(ch, 16)
    levels = [(10.5, "egg_core"), (7.5, "egg_bright"), (5.0, "egg_glow"), (2.6, "egg_smoke")]

    def value(px, py):
        u, v = px - ex + 12.0 - 0.5, 14.0 - (py - ey) - 0.5
        c0, r0 = int(math.floor(u)), int(math.floor(v))
        fu, fv = u - c0, v - r0

        def at(r, c):
            return grid[r, c] if 0 <= r < 28 and 0 <= c < 24 else 0.0
        return ((1 - fu) * (1 - fv) * at(r0, c0) + fu * (1 - fv) * at(r0, c0 + 1) + (1 - fu) * fv * at(r0 + 1, c0) +
                fu * fv * at(r0 + 1, c0 + 1))

    # The bands' edges follow the field's smooth contours (the faces split along them: polish_machine_kit.split_along),
    # on the egg's upper half (built in the picture's plane: x, y are where the picture draws them).
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    vals = {v: (value(v.co.x, v.co.y) if v.co.z > rz * 0.6 else 0.0) for v in bm.verts}
    for level, _ in levels:
        mk.split_along(bm, vals, level)
    slots = {name: mk.slot_of(obj, m[name]) for _, name in levels}
    bm.normal_update()
    for f in bm.faces:
        if f.normal.z < 0.25:
            continue
        v = sum(vals[q] for q in f.verts) / len(f.verts)
        for level, name in levels:
            if v >= level - 1e-6:
                f.material_index = slots[name]
                break
    bm.to_mesh(obj.data)
    bm.free()
    k.smooth(obj, 80)
    return sheared_parts([obj])


# --- Build --------------------------------------------------------------------------------------------------------------

def body(fl):
    d, tops = solid(fl)
    verts, quads = surface_nets(d, (X0, Y0, Z0), H)
    quads = drop_islands(verts, quads)
    whole = finish_whole(mesh_object("drill_rig", verts, quads))
    bm = bmesh.new()
    bm.from_mesh(whole.data)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    bm.to_mesh(whole.data)
    bm.free()
    shear_to_camera(whole)
    whole.data.update()
    return whole, tops


def mirror_x(objs):
    for o in objs:
        bm = bmesh.new()
        bm.from_mesh(o.data)
        for v in bm.verts:
            v.co.x = -v.co.x
        bmesh.ops.reverse_faces(bm, faces=bm.faces[:])
        bm.to_mesh(o.data)
        bm.free()
    return objs


def export(parts, name, centre, options, mask=None, label=None):
    out = mk.outdir(options)
    if mask is not None:
        mk.compare("%s as the camera sees it, its sprite's pixels" % (label or name),
                   view_coverage(parts, 24, 28, centre), mask)
    mk.transform(parts, Matrix.Translation((-centre[0], -centre[1], 0.0)))
    drop_unused(parts)
    triangulate(parts)
    obj = join(parts, name)
    obj.data.name = name
    bpy.context.view_layer.update()
    mk.report(name, [obj], os.path.join(out, name + ".glb"))
    if "preview" in options:
        mk.preview(options["preview"] + name, [obj])
    bpy.data.objects.remove(obj)


def part_models(m):
    """The parts: (model, sprite, builder, its sprite's centre)."""
    return [("rig_gun_post", 235, lambda: gun(m, GUN_AT[0]), GUN_AT[0]),
            ("rig_hatch", 197, lambda: hatch(m, HATCH_AT[0]), HATCH_AT[0]),
            ("rig_hatch_199", 199, lambda: hatch(m, HATCH_AT[0], 4.8, 0.38), HATCH_AT[0]),
            ("rig_hatch_237", 237, lambda: hatch(m, HATCH_AT[0], 8.4, 0.5), HATCH_AT[0]),
            ("rig_drill_bit", 267, lambda: drill(m, DRILL_AT), DRILL_AT),
            ("rig_drill_bit_269", 269, lambda: drill(m, DRILL_AT, 1.0 / 6.0), DRILL_AT),
            ("rig_torch_l", 275, lambda: torch(m, TORCH_AT[0], -1), TORCH_AT[0]),
            ("rig_torch_r", 277, lambda: mirror_x(torch(m, (-TORCH_AT[1][0], TORCH_AT[1][1]), -1)), TORCH_AT[1]),
            ("obsidian_egg", 271, lambda: egg(m), EGG_AT)]


def assembly(m):
    """Every part where the level puts it (for --whole)."""
    parts = []
    for at in GUN_AT:
        parts += gun(m, at)
    for at in HATCH_AT:
        parts += hatch(m, at)
    parts += drill(m, DRILL_AT)
    parts += torch(m, TORCH_AT[0], -1)
    parts += mirror_x(torch(m, (-TORCH_AT[1][0], TORCH_AT[1][1]), -1))
    parts += egg(m)
    return parts


def build():
    options = k.args()
    only = set(options["only"].split(",")) if "only" in options else None
    sheets = options.get("check")
    k.reset()
    bpy.context.scene.view_settings.view_transform = "Standard"
    m = materials()
    fl = fields()
    wanted = [p for p in PIECES if not only or p[0] in only]
    if wanted or "whole" in options:
        whole, tops = body(fl)
        centres, normals = face_data(whole)
        assign(whole, shades(centres, normals, fl, tops), m)
        extras = [ring(m)] + clamps(m)
        for o in extras:
            mk.apply(o)
        print("body: %d triangles" % len(whole.data.polygons))
        if "whole" in options:
            parts = assembly(m)
            allp = [o.copy() for o in [whole] + extras + parts]
            for o, src_ in zip(allp, [whole] + extras + parts):
                o.data = src_.data.copy()
                bpy.context.scene.collection.objects.link(o)
            for o in [whole] + extras + parts:
                o.hide_render = True
            for o in allp:
                mk.apply(o)
            triangulate(allp)
            mk.export(allp, options["whole"] + "drill_rig.glb")
            mk.preview(options["whole"] + "drill_rig", allp, size=(104, 64), scale=8, distance=1.3)
            if sheets:
                own = fl["own"]
                mk.compare("the whole rig as the camera sees it (body only)", view_coverage([whole] + extras, 72, 52,
                                                                                            (0.0, 0.0)), own.tolist())
            for o in allp + parts:
                bpy.data.objects.remove(o)
            for o in [whole] + extras:
                o.hide_render = False
        source = mk.NormalSource(whole)
        for name, sprite, box, centre in wanted:
            obj, rim = cut_piece(whole, box, name, m[CAP])
            pieces = []
            if obj is not None:
                whole.hide_render = True
                decimate(obj, rim, TARGET)
                shade_like(obj, source)
                c2, n2 = face_data(obj)
                idx = shades(c2, n2, fl, tops)
                flags = np.empty(len(obj.data.polygons), np.int64)
                obj.data.polygons.foreach_get("material_index", flags)
                idx[flags == 1] = CAP
                assign(obj, idx, m)
                pieces.append(obj)
            for e in extras:
                p = view_cut(e, box, e.data.materials[0])
                if p is not None:
                    pieces.append(p)
            for o in [whole] + extras:
                o.hide_render = True
            mask = None
            if sheets:
                c0, r0 = int(centre[0] - 12 + 36), int(26 - centre[1] - 14)
                own = np.zeros((28, 24), bool)
                rows = fl["own"][r0:r0 + 28, c0:c0 + 24]
                own[:rows.shape[0], :] = rows
                if centre[1] > 0:                     # (the upper pieces: what the lower row leaves of them)
                    own[24:, :] = False
                mask = own.tolist()
            export(pieces, name, centre, options, mask, "%s (M %d)" % (name, sprite))
            for o in [whole] + extras:
                o.hide_render = False
        bpy.data.objects.remove(whole)
        for o in extras:
            bpy.data.objects.remove(o)
    for name, sprite, builder, centre in part_models(m):
        if only and name not in only:
            continue
        parts = builder()
        for o in parts:
            mk.apply(o)
        mask = k.sprite_mask(os.path.join(sheets, "enemy_M.png"), sprite) if sheets else None
        export(parts, name, centre, options, mask, "%s (M %d)" % (name, sprite))


if __name__ == "__main__":
    build()
