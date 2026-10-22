"""The two spiked hands of SURFACE's boss (and of COLLECTOR): grey gauntlets each with a blue eye set in it and four long
spikes, one reaching up and to the left (sheet ^, x5e in models.cfg: 11 beside 13 at the top, the 1x1 49 and 50 beside
52 below), its twin up and to the right (92 beside 94, 129 beside 131 and the 1x1 133); one 60 x 56 picture each;
polished (2026-10-22, round 37). It replaces wave3_i.py's hand_whole() (a palm raised from the pixels, lathed cones for
spikes, an ellipsoid eye in a tube rim).

Where the levels put them: SURFACE (episode 4's enemies 260-264 at t5900, link 99: 260 (11) at x 220, 261 (13) at
244, both y -56; 262 (49) at 214, y -35; 263 (50) at 232, 264 (52) at 256, y -28; and 265-269 at t5930, link 198:
265 (92) at x -6, 266 (94) at 16, y -56; 267 (129) at -20, 268 (131) at 4, y -28; 269 (133) at 22, y -35), sky
enemies coming down a pixel a frame until t6040 / t6070, when they stop and bob (eycc 5, eyrev 3) either side of the
last rock machine (polish_rock_machine.py), SURFACE's boss; COLLECTOR (episode 6) puts both hands together the same
way (t936 the right one, 266 and 268 as its own 1656 and 1657; t2434 the left one, 260 and 263 as 1658 and 1659),
with the same bobbing. Each piece has armour 150 (260, 263, 266 and 268 fire, tur 116); a hand's pieces share a link,
so shooting one down destroys the hand; one frame each, no damaged look, nothing launched. A 2x2 sprite is drawn at
(ex - 6, ey - 7), a 1x1 at (ex, ey) (no event 26 in either level): the left hand's sprites meet edge to edge (11 at
columns 0-23 and 13 at 24-47 of rows 0-27; 49 at columns 0-11 of rows 28-41; 50 at 12-35 and 52 at 36-59 of rows
28-55), but the right hand's 92 lies two columns further right than its pixels were drawn for (columns 14-37, over
94's first two; 94 at 36-59, 129 at 0-23 and 131 at 24-47 of rows 28-55, 133 at 48-59 of rows 28-41): the game shows
its knuckles and its upright spike two pixels to the right of the rest, and so do these models (they are built in
the game's layout, 94 drawn over 92). FRUIT's launched enemies listed in the catalogue's launched list as "^ 13, 49,
50, 52" are episode 5's 1261-1264 (polish_launched_fruit.py, polish_launched_last.py), not these. No other enemy shows
these sprites; the right hand is the left one's pixels mirrored (column c to 59 - c) and redrawn without the dark
outline, so its shapes are the left one's mirrored, on its own pixels.

As the sprites and their 4x upscales draw the left hand (columns and rows of its 60 x 56 picture; grey ramp 0 lit from
the upper left, blue ramp 3): the gauntlet (columns 18-60 of rows 22-55), its top face (with the eye) to the upper
right of a lit ridge from the knuckles (column 36, row 31) down to its right edge (column 53, row 44), its left side
face below that in shade; the eye (columns 34-46 of rows 36-43), a blue lens glowing at its upper middle (0x3d,
0x3e); the knuckles where the spikes join the gauntlet's upper edge (rows 18-34), small bright joints between dark
gaps; four long spikes: A up the screen from (34.5, 21) to its point at (35.5, 0), B from (29.5, 24) to (18.5, 1.5),
C from (23, 27) to (5.5, 7.5), D from (20, 34.5) to (0.5, 17.5), each a lit ridge down its middle. The right hand the
same mirrored (no outline: a pixel thinner all round), painted a little lighter.

Built for the game's camera with polish_sheet9_kit: one heightfield a hand in the picture's plane on the sprites' grid
(the gauntlet a block, its top face level and its left side face falling to its lower left edge, the eye's socket
sunk in it; the knuckles domes; the spikes round in section, as high as they are half wide, on a lift falling from
their roots to their points; joined by smooth maxima, the dark lines creased, the fine shading a little relief). The
outline is the pixels', but along each spike (short of its root) it is smoothed along the spike's midline (SPIKE_BLUR:
the pixels' steps would show along the thin straight spikes, most of all on the right hand, which has no dark outline)
and the spike's section is fitted to it; the midlines and half widths of SPIKES were fitted to the pixels across each
spike. The eye a glossy blue lens (a solid ellipsoid, cut along the pieces' edges) glowing in its own blues
(0.2-0.45); everything painted by its own pixels (polish_sheet9_kit.Painter) and sheared along the camera's line of
sight. The right hand's shapes are the left one's mirrored about column 30 (u to 60 - u), its spikes a pixel narrower
(SPIKE_THIN), moved two pixels right over 92's box (blended over three pixels at its lower and right edges, so the
pieces meet without a step). Heights: z 0 to 8.0 (the eye's lens), the gauntlet 7.4, the spikes 1.0-5.9. Sky enemies
(22 pixels up, plus the terrain's headroom): under the player's plane.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera (z 0: the sky
enemies' plane). Each hand's origin is its picture's middle (column 30, row 28): column c is x = c + 0.5 - 30, row r is
y = 27.5 - r; the pieces' origins (their sprites' middles): 11 (-18, 14), 13 (6, 14), 49 (-24, -7), 50 (-6, -14), 52
(18, -14); 92 (-4, 14), 94 (18, 14), 129 (-18, -14), 131 (6, -14), 133 (24, -7) (models.cfg origin).

models.cfg: the ten model and sprite lines stay as they are (spike_hand_tl ... origin; yaw=0).

Replaces wave3_i.py's hands: HAND, HAND_R, SPIKES, SPIKES_R, hand_whole(), its two w.WHOLES entries ("hand",
"hand_r") and the two loops registering spike_hand_* and spike_hand_r_*, the spike_hand paragraph of its docstring
("hand,hand_r" in its --whole usage line), and wave3_i_art.py's HAND and HAND_R (only hand_whole() reads them).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each piece's outline as the
camera sees it against its sprite's pixels), --preview <prefix>, --only <name,...>.
"""
import math
import os
import sys

import bpy
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
import polish_sheet9_kit as nk  # noqa: E402
from polish_sheet9_kit import Pic, parse, blur, smoothstep, smax, Region, Zone, Painter, round_rise  # noqa: E402

MIRROR = 60.0                     # the right hand's shapes: the left one's at u' = MIRROR - u
SHIFT = (2.0, (26.5, 29.5), (34.5, 38.0))  # over 92's box: this far right; blended over these rows and columns
# The spikes of the left hand, from their roots to their points: (column, row, half width, lift off the plane), their
# midlines and half widths fitted to the pixels across them (the dark outline included; the right hand's are a pixel
# narrower, SPIKE_THIN).
SPIKES = [
    [(34.6, 22.0, 3.5, 2.6), (34.5, 18.1, 3.3, 2.3), (34.0, 15.4, 3.0, 2.0), (34.0, 12.2, 2.9, 1.7), (34.5, 8.9, 2.5, 1.3),
     (35.0, 5.6, 2.1, 1.0), (35.0, 2.4, 1.9, 0.7), (35.5, 0.0, 0.7, 0.4)],
    [(29.6, 24.2, 3.3, 2.6), (27.5, 20.1, 3.0, 2.3), (26.0, 17.5, 3.0, 2.1), (24.2, 14.1, 2.5, 1.7), (22.2, 11.0, 2.3, 1.4),
     (21.0, 7.2, 2.2, 1.0), (19.5, 3.7, 1.6, 0.7), (18.4, 1.1, 0.7, 0.4)],
    [(23.2, 27.4, 3.2, 2.6), (19.8, 24.0, 2.9, 2.2), (17.7, 21.5, 2.5, 1.9), (14.9, 18.7, 2.5, 1.6), (12.3, 15.6, 2.2, 1.3),
     (9.6, 12.7, 1.9, 1.0), (7.0, 9.6, 1.4, 0.7), (5.3, 7.2, 0.7, 0.4)],
    [(20.2, 34.6, 3.2, 2.6), (16.9, 31.2, 2.9, 2.2), (14.7, 29.0, 2.7, 1.9), (11.2, 27.0, 2.5, 1.6), (8.2, 24.5, 2.0, 1.3),
     (5.0, 22.2, 1.7, 1.0), (2.0, 19.6, 1.4, 0.7), (0.2, 17.3, 0.7, 0.4)],
]
SPIKE_THIN = 0.9                  # the right hand's spikes this much narrower each side (no dark outline)
SPIKE_ZONE = (0.8, 1.8)           # along a spike short of this share of it from its point (its root is the knuckles'),
                                  # within this of its edge: its outline smoothed along it (SPIKE_BLUR, so that the
                                  # pixels' steps don't show along it) and its section round to that outline
SPIKE_BLUR = 1.5                  # how far along a spike its outline is smoothed (sigma, pixels)
SPIKE_POWER = 0.5
KNUCKLES = [((34.6, 24.0), (3.6, 3.0), 6.6), ((29.4, 27.0), (3.5, 3.0), 6.4), ((24.0, 30.4), (3.4, 3.0), 6.2),
            ((20.6, 35.0), (3.2, 2.8), 5.6)]   # domes over the spikes' roots: middle, radii, height
# The gauntlet: its outline (columns, rows) as a polygon, its top face's height, the ridge (two points) along which
# its left side face starts to fall, how far it falls a pixel, its least height.
PALM = [(18.6, 33.0), (24.0, 29.0), (31.0, 24.6), (38.0, 22.4), (44.0, 23.0), (49.0, 26.0), (54.0, 32.0), (58.5, 39.0),
        (60.5, 44.0), (60.5, 52.0), (57.0, 55.6), (46.0, 56.4), (36.0, 56.4), (31.5, 50.0), (25.0, 42.0), (19.0, 36.0)]
PALM_H = (7.4, ((36.0, 30.5), (53.5, 44.5)), 0.42, 2.2, 2.4)   # height, ridge, fall a pixel, least height, rounding
EYE = ((39.8, 39.6), (5.3, 3.8, 2.2), 5.8, (6.4, 4.7), 1.7)    # middle, lens radii, lens middle's height, socket radii,
                                                               # socket depth
CREASE = 0.8
DETAIL = (0.1, 0.25)
GREY = list(range(0x01, 0x0e))
BLUE = [0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x3a, 0x3b, 0x3c, 0x3d, 0x3e]
BLUE_GLOW = {0x31: 0.2, 0x32: 0.21, 0x33: 0.22, 0x34: 0.24, 0x35: 0.25, 0x36: 0.27, 0x37: 0.29, 0x38: 0.31,
             0x39: 0.33, 0x3a: 0.35, 0x3b: 0.38, 0x3c: 0.4, 0x3d: 0.43, 0x3e: 0.45}
FINISH = {"grey": (0.32, 0.34), "blue": (0.1, 0.08), "dark": (0.2, 0.5)}
HANDS = {
    "l": ("LEFT_ART", False, [("spike_hand_tl", (0, 0), True), ("spike_hand_tr", (24, 0), True),
                              ("spike_hand_tip", (0, 28), False), ("spike_hand_bl", (12, 28), True),
                              ("spike_hand_br", (36, 28), True)]),
    "r": ("RIGHT_ART", True, [("spike_hand_r_tl", (14, 0), True), ("spike_hand_r_tr", (36, 0), True),
                              ("spike_hand_r_bl", (0, 28), True), ("spike_hand_r_bc", (24, 28), True),
                              ("spike_hand_r_tip", (48, 28), False)]),
}
# 92's box (the right hand's top left piece) holds only the columns 94 does not draw over (14-35).
KEEP = {"spike_hand_r_tl": (14, 36, 0, 28)}

# The left hand's pixels (palette indices).
LEFT_ART = """
    ....................................................................010b01..............................................
    ....................................01............................010a0b01..............................................
    ..................................010a01..........................010b0a01..............................................
    ..................................01080b01........................010b0a01..............................................
    ....................................010b0901......................010b0901..............................................
    ....................................01090b01......................010b0901..............................................
    ....................................01050b0901..................01050b0901..............................................
    ..........0101........................01090b01..................01040b0901..............................................
    ..........010901......................01060b0901................01060a0901..............................................
    ..........01090c01......................010a0b01................01070a0901..............................................
    ............01090b01....................01070b0901..............01070a0901..............................................
    ..............010a0a01..................0105080b0701..........010408090901..............................................
    ..............01060a0b01..................01070a0901..........010508090801..............................................
    ................01080a0901................0106070a0801........010608090801..............................................
    ..................01080b0901..............010406090a01........010607090801..............................................
    ..................0102080a0901..............010608090601......010506090801..............................................
    ....................0104080a0801............01040708090501....010605090801..............................................
    01....................0106090a0901............010606080701....010705080701..............................................
    0c0101..................0107090a0901..........01050507080401..01050308070801............................................
    010a0b01................010307090a0901..........010505070601010105020607060801..........................................
    ..01080a0101..............010407090a0901........01050406070301040301050405060201........................................
    ....01090a0901..............010307090a0801........010404050501020101020306070401........................................
    ......01070a0a0101............010408090a0601......01040405020705030305070907050301......................................
    ........0107090a0801............0104070a090601..01050402030808060306070909070304040101..................................
    ..........0107090a080101..........0104080a0706010205050506090c07020607070a0603030304030101..............................
    ............0105080a08060101......0105050809070404030606060705060205060608010305050606050501............................
    ..............0106070a09050401......0106060808020207030504040406010203020404050707080808050501..........................
    ................010506080907060101....010606060501080b060102020204020505070507080808080908050401........................
    ..................010505070908060401....01050602020809080401030807070504060608080808080a09070501........................
    ....................0104050607080704010105020203060706070403050a05060a09080707070808080a0b090601........................
    ......................01010406060808050302040405060405040306080504070a0c0a0907070709080a0b0806010101....................
    ..........................01040405060604020204030402030104070505070808090c0a090707070a0a0b070606050401..................
    ............................01040505030101050402010101040906040708080808090c0a090807070a0706070908060501................
    ..............................01010203010609080704030105040509060808080808090b0b090807070508080a0b09070301..............
    ................................0103050609090807070303030507080a06080808090b0a0b09080704070a08090a0a070401..............
    ................................010404050607070606030304060708080b070809090908040404040404080a080808080601..............
    ..................................01050606060605050103040607070a0607080908040404343333350404080b0808080701..............
    ....................................0104040505060303030406070905060809080404323338393834340405080b0808080601............
    ......................................0103030301010303040608050608080904043131373b3d3b3832040407090b08080601............
    ........................................01030303030303050804040707080404343236383d3e3b373104030707090b08080601..........
    ..........................................01030303030307040305050607043634353537393a3a34040402070707090b08080601........
    ............................................0103030303060303030405050436383432333331333304030407070707090c08080601......
    ..............................................01030303060303030303050434373b38343534360403020507070707080e0a08070601....
    ................................................010303050403030303030404343639383804040302050707070707080b090808070501..
    ..................................................0103040403030303010304040404040404020205070707070707070a08080705050501
    ....................................................01030404030303030303030303030303030507070707070707090707070505050501
    ......................................................010304040303030303040404050505060707070707070709070505050505050501
    ........................................................0103030303030304040405050506060707070707070907050505050505050501
    ..........................................................01030303030404040405050506070707070707090705050505050505050401
    ............................................................010303030404040505050606070707070708070505050505050505050301
    ..............................................................0103030404050505050606070707070707050505050505050504030101
    ................................................................010303040505050506060707070707050505050505040304010101..
    ..................................................................0103030405050506060607070705050505040403010101........
    ....................................................................01020304050505060607070605050404010101..06..........
    ......................................................................010203040505050505050302010101....................
    ........................................................................0101020303030404010101..........................
"""
# The right hand's, as the game puts its sprites together (92 two columns right of where it was drawn for, 94 over it).
RIGHT_ART = """
    ....................................................0b..................................................................
    ....................................................0b0a................................................................
    ....................................................0a0b..........................0a....................................
    ....................................................0a0b........................0b08....................................
    ....................................................090b......................090b......................................
    ....................................................090b......................0b09......................................
    ....................................................090b05..................090b05......................................
    ....................................................090b04..................0b09........................................
    ....................................................090a06................090b06..........................09............
    ....................................................090a07................0b0a..........................0c09............
    ....................................................090a07..............090b07........................0b09..............
    ....................................................09090804............0b0805......................0a0a................
    ....................................................08090805............0a07......................0b0a06................
    ....................................................08090806............0706....................090a08..................
    ....................................................08090706............0604..................090b08....................
    ....................................................08090605..........060608................090a0802....................
    ....................................................08090506........05090407..............080a0804......................
    ....................................................07080507........07080606............090a0906........................
    ..................................................0807080305......0408070505..........090a0907........................0c
    ................................................080607060205......06070505..........090a090703....................0b0a..
    ..............................................0206050405010304010307060405........090a090704....................0a08....
    ..............................................04070603020101020105050404........080a090703..................090a09......
    ............................................0305070907050303050702050404......060a090804..................0a0a07........
    ..........................................04040307090907060306080803020405..06090a0704................080a0907..........
    ......................................0304030303060a07070602070c090605050506070a0804................080a0907............
    ..................................05050606050503010806060502060507060606040709080505............06080a0805..............
    ................................05050808080707050404020302010604040405030208080606..........0405090a0706................
    ..............................04050809080808080705070505020402020201060b05060606..........060709080605..................
    ..........................0507090a08080808080606040507070803010408090802020605........04060809070505....................
    ..........................06090b0a08080807070708090a06050a0503040706070603020205....04070807060504......................
    ..........................06080b0a0809070707090a0c0a070405080603040504060504040203050808060604..........................
    ....................04050606070b0a0a070707090a0c09080807050507040103020403040202040606050404............................
    ..................050608090706070a070708090a0c09080808080704060904010101020405010103050504..............................
    ................0307090b0a080805070708090b0b090808080808060905040501030407080906010302..................................
    ................04070a0a09080a07040708090b0a0b09080808060a0807050303030707080909060503..................................
    ................06080808080a080404040404040809090908070b080807060403030606070706050404..................................
    ................070808080b0804043533333404040408090807060a07070604030105050606060605....................................
    ..............060808080b0805043434383938333204040809080605090706040303030605050404......................................
    ..............0608080b0907040432383b3d3b3731310404090808060508060403030101030303........................................
    ............0608080b090707030431373b3e3d38363234040408070704040805030303030303..........................................
    ..........0608080b09070707020404343a3a39373535343604070605050304070303030303............................................
    ........0608080c0907070707040304333331333332343836040505040303030603030303..............................................
    ......0607080a0e08070707070502030436343534383b37340405030303030306030303................................................
    ....05070808090b080707070707050203040438383936340404030303030304050303..................................................
    ..0505050708080a0707070707070705020204040404040404030103030303040403....................................................
    ..0505050507070709070707070707070503030303030303030303030303040403......................................................
    ..05050505050505070907070707070707060505050404040303030303040403........................................................
    ..050505050505050507090707070707070606050505040404030303030303..........................................................
    ..0405050505050505050709070707070707060505050404040403030303............................................................
    ..03050505050505050505070807070707070606050505040404030303..............................................................
    ..010304050505050505050507070707070706060505050504040303................................................................
    ........0403040505050505050707070707060605050505040303..................................................................
    ..............03040405050505070707060606050505040303....................................................................
    ..........06........040405050607070606050505040302......................................................................
    ..........................0203050505050505040302........................................................................
    ................................040403030302............................................................................
"""


def spike_fields(u, v, thin):
    """Over all spikes, for each point: the nearest spike's half width and lift there, the direction of its midline
    (columns, rows), how much the point lies in that spike's zone (SPIKE_ZONE: 1 well inside it, falling to 0 over a
    pixel at its edge) and its distance from the midline."""
    best = np.full(u.shape, 1e9)
    hw = np.zeros(u.shape)
    lift = np.zeros(u.shape)
    du_ = np.zeros(u.shape)
    dv_ = np.zeros(u.shape)
    zone = np.zeros(u.shape)
    for spike in SPIKES:
        length = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(spike, spike[1:]))
        s = 0.0
        for (pu, pv, pw, pl), (qu, qv, qw, ql) in zip(spike, spike[1:]):
            du, dv = qu - pu, qv - pv
            ln = math.hypot(du, dv)
            t = np.clip(((u - pu) * du + (v - pv) * dv) / max(1e-9, ln * ln), 0.0, 1.0)
            d = np.hypot(u - (pu + t * du), v - (pv + t * dv))
            w = np.maximum(pw + t * (qw - pw) - thin, 0.6)
            from_point = 1.0 - (s + t * ln) / length        # 0 at the root, 1 at the point
            inz = smoothstep(w + SPIKE_ZONE[1], w + SPIKE_ZONE[1] - 1.0, d) * \
                smoothstep(1.0 - SPIKE_ZONE[0] - 0.08, 1.0 - SPIKE_ZONE[0] + 0.08, from_point)
            closer = d < best
            best = np.where(closer, d, best)
            hw = np.where(closer, w, hw)
            lift = np.where(closer, pl + t * (ql - pl), lift)
            du_ = np.where(closer, du / ln, du_)
            dv_ = np.where(closer, dv / ln, dv_)
            zone = np.maximum(zone, inz)
            s += ln
    return hw, lift, du_, dv_, zone, best


class SmoothRegion(Region):
    """polish_gyges_wall.Region of a field already smooth (its outline the field's 0.5 contour)."""

    def __init__(self, pic, soft, step=0.25):
        self.pic = pic
        self.soft = soft
        xs = np.arange(pic.left + step / 2, pic.left + pic.w, step)
        ys = np.arange(pic.top - pic.h + step / 2, pic.top, step)
        X, Y = np.meshgrid(xs, ys)
        inside = pic.sample(self.soft, X, Y) > 0.5
        p = np.pad(inside, 1, mode="edge")
        h, w = inside.shape
        edge = np.zeros_like(inside)
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            edge |= p[1 + dr:1 + dr + h, 1 + dc:1 + dc + w] != inside
        self.pts = np.stack([X[edge], Y[edge]], 1)


def inside_polygon(u, v, poly):
    inside = np.zeros(u.shape, bool)
    n = len(poly)
    for i in range(n):
        (c0, r0), (c1, r1) = poly[i], poly[(i + 1) % n]
        cond = (r0 > v) != (r1 > v)
        with np.errstate(divide="ignore", invalid="ignore"):
            xi = c0 + (v - r0) * (c1 - c0) / np.where(r1 == r0, 1e-9, r1 - r0)
        inside ^= cond & (u < xi)
    return inside


class Hand:
    def __init__(self, text, right):
        self.pic = Pic(parse(text), -30.0, 28.0)
        self.right = right
        a = self.pic.a
        own = a >= 0
        self.thin = SPIKE_THIN if right else 0.0
        # The outline: the pixels' (blurred a little), along the spikes smoothed along their midlines.
        pic = self.pic
        cols, rows = np.meshgrid(np.arange(pic.w) + 0.5, np.arange(pic.h) + 0.5)
        X, Y = cols - 30.0, 28.0 - rows
        u, v = self.uv(X, Y)
        _, _, du, dv, zone, _ = spike_fields(u, v, self.thin)
        if right:
            du = -du                    # the shapes are mirrored
        mask = own.astype(float)
        along = np.zeros_like(mask)
        total = 0.0
        for i in range(-8, 9):
            w = math.exp(-0.5 * (i * 0.5 / SPIKE_BLUR) ** 2)
            along += w * pic.sample(mask, X + i * 0.5 * du, Y - i * 0.5 * dv)
            total += w
        soft = blur(mask, 0.5) * (1.0 - zone) + (along / total) * zone
        self.region = SmoothRegion(pic, soft)
        shade = np.where(own, a & 15, 0).astype(float)
        grey = own & (a >> 4 == 0)
        h, w = a.shape
        p = np.pad(own, 1)
        surrounded = np.ones_like(own)
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            surrounded &= p[1 + dr:1 + dr + h, 1 + dc:1 + dc + w]
        dark = grey & (shade <= (2 if right else 1))
        self.crease = blur((dark & surrounded).astype(float), 0.45)
        self.soft = blur(nk.fill(shade, own), 0.6)
        self.broad = blur(nk.fill(shade, own), 2.0)

    def uv(self, X, Y):
        """The left hand's columns and rows at which the shapes of this point lie."""
        u, v = np.asarray(X, float) + 30.0, 28.0 - np.asarray(Y, float)
        if self.right:
            far, (r0, r1), (c0, c1) = SHIFT
            u = u - far * smoothstep(r1, r0, v) * smoothstep(c1, c0, u)
            u = MIRROR - u
        return u, v

    def heights(self, X, Y):
        X, Y = np.asarray(X, float), np.asarray(Y, float)
        u, v = self.uv(X, Y)
        d = self.region.depth(X, Y)
        hw, lift, _, _, zone, axis = spike_fields(u, v, self.thin)
        # A spike's section: round, as high as it is half wide, on its lift; in its zone round to its own outline,
        # towards its root round to its midline.
        sec = np.clip(1.0 - (axis / hw) ** 2, 0.0, None) ** SPIKE_POWER
        fitted = np.where(d > 0, lift + hw * round_rise(d, hw), 0.0)
        z = zone * fitted + (1.0 - zone) * np.where(sec > 0, lift + hw * sec, 0.0)
        top, ((a0, b0), (a1, b1)), fall, least, rnd = PALM_H
        palm = polygon_weight(u, v, PALM)
        # signed distance to the ridge's line: positive on its lower left (the side face)
        nx, ny = b1 - b0, -(a1 - a0)
        ln = math.hypot(nx, ny)
        side = ((u - a0) * nx + (v - b0) * ny) / ln
        level = np.maximum(least, top - fall * np.maximum(side, 0.0))
        pz = level * round_rise(d, rnd) * palm
        z = smax(z, pz, 0.8)
        for (kc, kr), (kx, ky), kh in KNUCKLES:
            z = smax(z, nk.gw.dome(u, v, (kc, kr), (kx, ky), kh), 0.6)
        (ec, er), _, _, (sx, sy), sd = EYE
        q = ((u - ec) / sx) ** 2 + ((v - er) / sy) ** 2
        z = z - sd * (1.0 - smoothstep(0.55, 1.0, q))
        pic = self.pic
        z = z - CREASE * pic.sample(self.crease, X, Y) * np.clip(z / 4.0, 0.0, 1.0)
        fine = pic.sample(self.soft, X, Y) - pic.sample(self.broad, X, Y)
        z = z + np.clip(DETAIL[0] * fine, -DETAIL[1], DETAIL[1]) * smoothstep(1.0, 3.0, z)
        z = z * round_rise(d, 0.8)
        return np.where(d > 0, np.maximum(z, 0.0), 0.0)


def polygon_weight(u, v, poly, soft=1.4):
    """1 inside a polygon, 0 outside, rising over `soft` either side of its edges."""
    d = np.full(u.shape, 1e9)
    for (c0, r0), (c1, r1) in zip(poly, poly[1:] + poly[:1]):
        dc, dr = c1 - c0, r1 - r0
        t = np.clip(((u - c0) * dc + (v - r0) * dr) / max(1e-9, dc * dc + dr * dr), 0.0, 1.0)
        d = np.minimum(d, np.hypot(u - (c0 + t * dc), v - (r0 + t * dr)))
    signed = np.where(inside_polygon(u, v, poly), d, -d)
    return smoothstep(-soft, soft, signed)


def build():
    options = k.args()
    out = mk.outdir(options)
    only = set(options["only"].split(",")) if "only" in options else None
    for side, (var, right, pieces) in HANDS.items():
        if only is not None and not any(n in only for n, _, _ in pieces):
            continue
        k.reset()
        hand = Hand(globals()[var], right)
        pic = hand.pic
        a = pic.a
        own = a >= 0
        lift = 1.6 if right else 1.2
        painter = Painter(pic, [Zone("grey", own & (a >> 4 == 0), GREY, FINISH["grey"], lift=lift),
                                Zone("blue", own & (a >> 4 == 3), BLUE, FINISH["blue"], glow=BLUE_GLOW, sigma=0.5,
                                     lift=1.0, comp=0.8),
                                Zone("dark", own, [0x01, 0x02], FINISH["dark"], lift=0.0, comp=0.0, pick=False)],
                          "hand_" + side)
        plate = nk.gw.Plate((-30.0, 30.0, -28.0, 28.0), hand.heights, cells=hand.region.inside)
        (ec, er), radii, ez, _, _ = EYE
        eu = MIRROR - ec if right else ec
        lens = nk.ellipsoid("spike_hand_eye_%s" % side, (eu - 30.0, 28.0 - er, ez), radii, count=10, around=28,
                            cut_below=0.3)
        nk.assign(lens, painter.keys(lens, zone="blue", offset=1.0), painter)
        lens.hide_render = True

        def keys(obj, kinds, wall_z):
            centres, normals = nk.face_data(obj)
            near = painter.zone_at(centres[:, 0], centres[:, 1])
            out_ = painter.keys(obj, zones=["dark" if kinds[i] != 0 else near[i] for i in range(len(kinds))])
            return [("dark", 0x01) if kinds[i] != 0 else key for i, key in enumerate(out_)]
        for name, (c0, r0), large in pieces:
            if only is not None and name not in only:
                continue
            w, h = (24, 28) if large else (12, 14)
            box = nk.own_box(pic, c0, r0, keep=KEEP.get(name), w=w, h=h)
            parts = nk.piece_parts(plate, keys, [lens], box, nk.box_owner(box), name, painter, ("dark", 0x01))
            for p in parts:
                p.hide_render = False
            mask = None
            if "check" in options:
                mask = nk.sprite_mask(pic, c0, r0, w, h)
                if name in KEEP:        # 92: the columns 94 draws over are 94's
                    k0, k1, _, _ = KEEP[name]
                    mask = [[mask[r][c] and k0 <= c0 + c < k1 for c in range(w)] for r in range(h)]
            piece = nk.finish(name, parts, box, out, options, painter, mask=mask,
                              origin=(pic.left + c0 + w / 2, pic.top - r0 - h / 2))
            bpy.data.objects.remove(piece)


if __name__ == "__main__":
    build()
