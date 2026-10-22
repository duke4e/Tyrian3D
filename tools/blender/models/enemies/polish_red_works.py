"""TYRIAN's and TYRIAN X's red works in the rocks (sheet 2: 15, 17 above 53, 55, 2x2 each: one 48 x 56 picture; the top
layer; one frame each), polished (2026-10-22, round 37; it replaces wave3_p_ground.py's works_whole(), a steel slab with
red rounded boxes, pipes and spheres on grey boulders).

Where the levels put them: TYRIAN (both of its level files) and TYRIAN X at t3200, event 7 (top enemies 42-45 of
episodes 1 and 3, armour 12, link 31): 42 (2 15) at (48, y - 27), 43 (2 17) at (72, y - 27), 44 (2 53) at (48, y + 1),
45 (2 55) at (72, y + 1): the sheet's layout, on background 3's tile grid (columns 2 and 3). They lie exactly over
background 3's tiles 161 162 above 171 172 (map rows 354-355, columns 2-3), which draw the same works wrecked
(blackened, broken, rubble at the lower right) on a cobbled outcrop: the cobbles round the works in the sprites are the
map's own pixels (identical to the tiles' outside the works), so the models leave them out and stand on background 3's
plane (height=-6, as TYRIAN's purple pads and hooded turret do: the top layer is drawn 6 pixels above background 3), and
shooting a piece away leaves the wreck the map draws. (The sprites' darker cobbles at the lower right, columns 38-47 of
rows 28-50, differ from the map's rubble there; they are ground too: left to the map.) None of the four is another
sprite's pixels mirrored, turned or in other ramps; no other enemy, launched ones included, shows them; no episode 6
level brings them (its levels take no TYRIAN waves with the top enemies 42-45).

As the sprites and their 4x upscale draw it (columns and rows of the 48 x 56 picture; lit from the upper left): a dark
steel deck (0x01-0x03) over columns 3-38 of rows 3-50, crowded with machinery: at the top a grey drum lying across
(columns 5-13 of rows 1-6, red caps at its ends) and a dark panel striped with tan rails (columns 14-30 of rows 3-6), a
grey knob at the top right (columns 30-34 of rows 1-6); a big red block bent down at its left (columns 3-16 of rows
7-16, its top lit pink), a grey block beside it, a red block at the upper right (columns 22-28 of rows 7-15) and a tan
rod right of it (columns 31-32 of rows 6-15); between them a dark housing (columns 13-19 of rows 11-21) with two glowing
grilles, yellow to orange and red round a white-hot pixel (columns 14-18 of rows 12-14 and 18-20); a red pipe from the
housing along row 16-17 to column 34, down the right side to row 33 and back along row 28 to column 21, framing a dark
box (columns 20-34 of rows 18-28) with a grey lid, a dark tan panel sunk in it and grey slats at its right; at the left
a tan box (columns 0-10 of rows 15-29) with a red button in a dark socket and a tan rail along its foot; under the
housing a grey block and a red block (columns 11-18 of rows 21-29); lower down a small red block (columns 3-6 of rows
29-34), a tall tan block (columns 6-12 of rows 33-47) beside a grey block and a red wedge (columns 12-19 of rows 33-47),
a red bar at the lower right (columns 29-33 of rows 33-48) with the pipe running into its top, a tan rod at the deck's
right edge (columns 36-37 of rows 22-34).

Built for the game's camera with polish_sheet9_kit (as GYGES' maw and the round 36 machines are): one heightfield of
the whole in the picture's plane (gw.Plate, its grid STEP 0.5 apart with the sprites' edges on its lines, so each piece
is the cells of its sprite's box: no mesh cutting; walls where cut, dark), its outline the works' own pixels (OUTLINE,
smoothed a little), sheared along the camera's line of sight (y - z tan 20) so the camera sees every point where the
sprites draw it. Its heights: the deck 1.3 (rounding over 0.8 at its edge), the blocks rounded boxes (BOXES, 2.6-5.4),
the drum, the pipes and the rods lying tubes (TUBES, 3.0-4.4), the grilles domes glowing out of the housing (6.0), the
button a dome in a sunk socket (5.6), the knob a dome (3.6), the box's tan panel sunk 0.7; the sprite's fine shading a
little relief on the parts (DETAIL). Painted by the sprite under each face (polish_sheet9_kit.Painter: the shades of
each ramp's pixels filled outwards and blurred, LIFT lighter, lighter where the game's sun lights a face less (COMP)):
the reds ramp 4 (0x43-0x4d), the tans ramp 10 (0xa2-0xac) and the rail's ramp 1 (0x10-0x1c), the steel and the deck
ramp 0, the grilles ramp 7 glowing in their own colours (0.3-0.6); the walls dark. Heights 0-6.0 over background 3's
plane (the player's plane is 12 above it).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera (z 0: background 3's
plane, with height=-6). The whole's origin is its picture's middle (column c is x = c + 0.5 - 24, row r is y = 27.5 -
r); each piece moved so its sprite's middle is its origin (models.cfg origin): 15 (-12, 14), 17 (12, 14), 53 (-12, -14),
55 (12, -14).

models.cfg: the four model lines stay (model red_works_tl ... origin); the sprite lines get height=-6: sprite 2 15
red_works_tl yaw=0 height=-6, sprite 2 17 red_works_tr yaw=0 height=-6, sprite 2 53 red_works_bl yaw=0 height=-6,
sprite 2 55 red_works_br yaw=0 height=-6; the grilles glow: glow=9:0.25:123:4.5:2.5 on 15 (the grilles' middle, 4.5
right of 15's centre and 2.5 down: columns 14-18 of rows 12-20).

Replaces wave3_p_ground.py's red works (WORKS_OUTLINE, works_whole() and the quarters("red_works", ...) line; with them
inside_outline() and quarters(), which only they use, and so the whole file: delete it) and wave3_p_art.py's WORKS (read
only by wave3_p_ground.py).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each piece's outline against
its sprite's own pixels, the works' (the cobbles left out)), --preview <prefix>, --only <name,...>.
"""
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
from polish_sheet9_kit import Pic, parse, blur, smax, Region, Zone, Painter, round_rise  # noqa: E402

# 2 15 17 / 53 55: the 48 x 56 picture (rows top to bottom; each pixel its palette index in hex, '..' none).
WORKS_ART = """
09aaaaaaababab050401060305060606060504040607070609aaaaaa0904030306030304660606060605040406070706
a9aaaaaaababab0404020504010101070606050507090909a9aaaaaa6a05040308030302040506070606050507090909
a9a9aaaaaaaa070809050a08024301090908050507080808a9a9aaaa090a070309050301040507090908050507080808
08a8a9a9a905430c0b070f0a044a010102010b0a09080b0a0a0508010b0d0b060d070401030508090907050405060708
040406a70345490807030905034802a4a40118a5a5a218a5a5a217a50a08060409050301030407090806040303050506
05050405024a4d0306010504024301010101010101010101010101010606040105040301010203050402020508090a09
070705020346480104010404011001010101010405090908070705030304010102010201010101010101010509090908
0808050102074d4b4b4a4a4949494903010101010101010101010101020302a5a202030101020201010104080a090908
08070604044b4b484847474747474646450505040201494746464645010602a5a202050101020303010105080b0a0908
070808064a494a464645464646464646430303050402484646464645010401a5a3010401010304040303060a0b0a0808
0809084949484a4646a2434343434343a20301030403474646464644010201a5a3010101010304040303060909090807
0908084847484544444206060603070b0d0905030803444444444442010101a5a30101010203040403a3a50708080608
0807054747454b48474507050502787c7d7b780105034a4948484743010201a5a3010101020304040302a50708070808
08060447444a4846464506050501760b7a787401050347464646464401010116a301010202030304030203a505060607
0705044449484846464305050503787c7d7b780204024546464645a201010116a3010102020303030101010203040504
070303484747464546a20345454545450505040201010243434310010101010101010101020202010101010103060705
0f0b0909090807040301a24b494847430405044b494847474449474747474747474747010202010101010206080a0a09
4ea4a4a4a3a3a3a3a3a3034a484747a20405044a48474747454947474747474747474701a010a0a0010306080b0c0b0a
1ca5a5a4a4a4a4a4a4a403040302787c7d7b78010303030303020102010101020101470101015001020406080a0b0c0a
1ca5a5a4a4a4a4a4a4a402050401750e7a7875010404040404030106a4a404040403470101020101020407080a0a0b0a
1ba5a403030202a2a4a401060502787c7d7b7802050501010101010101a20505050447010102020102040708080a0b0a
1ba503484a4846a202a403040504040504030103040401a2a2a2a2a2a2a2040304044301010101010204066a0a0c0b0a
1ba5034a4d4a47a201a2a24c4a4a474c4847a209070601a2a3a3a3a3a3a3090706044a010101a001020406070a0b0b0a
1aa503474a47431001a2a34b464644494646a203020201a2a3a4a4a4a4a4040304044701a41601010204060709090909
1aa5a2a243a2a20101a2a34a464644484646a205070601a2a3a4a4a4a4a4090605044801a2a401010103040508080807
1aa5a4010101010101a2a34b484844494746a202020301a2a3a4a4a4a4a4040304044901a2a401010101030507070706
19a5a5a40101a2a2a2a3a347a2a24144a2a21004050501a2a3a4a4a4a4a4060505044901a2a401010101010406060504
18181716161616161616a446a2a24144a2a2100406494949494949494949494949494a01a2a401010101010103050404
0317a4a4a4a4a4a4a4a40244a2a24143a2a2100404040404040404040201010101014801a2a401010101010102050506
04160102a2a20202a3a30143a2a24142a2a2100303030303030303030106030102014701a2a401010102010103070709
021601464543430202010102101010101010010202020202020202020107050205044701a2a401010203010103060608
011601454343a20101010101010101010101010101020202020202020107050205044701a2a501010202010101040508
01a502454343100101010101010101010102010101020202020202020104040304044701a31601020202500101030306
01a20143434301a3a2a2020201030202010402020101020202020202014b494847474701a41701010101010203076a09
0203040404030216a3a3a3a3020503030205030401010102020202020148474701010201a51701010150020305070708
0205050403030718a5a4a4a4020503030205030501010101020202020148474702030301a20201010101030506070708
030303030303091b16a4a4a4020404040305040601010101010202020147454502040501010201010102040507060708
0302010101010c1b18a5a5a502030404030404060101010101010101014c4b490104050101a201010203040507060608
0604010101010b1b1916a5a501030202020203060101010101010102014b49480103050101a201a00103040505060607
08050302010108a51c19a5a502484746454547010101010101020203014b4a4a03050601010101a10102030404060408
08060503010106a3a41b1816024846464648100101010101020203030148454502040401010101a10102a30404050608
08080604020107a3a3a51c1802494848491001010101010102030303014743430101010101010101010202a303040407
07070503020107a3a3a4a2a201a2a2a24610010101010101020203030147434343434301010101a10101a00202030304
05050403020207a316a3a3a301434343434510010101010101010202014743a505044301010101020101010101040505
0909090906040b16a3a3a3a3014343434343430101450101020202020146431617014301a3a3a30101010104050a6a09
0a09090909060a16a3a3a30201a24343434343a2014502a5a5a5a5a4a34643a5a3014301010101010103686a6a0b0a0a
0a090909080707a5a3a3a3010110434343a210a201a2010101010101014543a4a30143010201015003686a68680a0b0a
0a090908060504a4a3a30201010101a2a21010010101010101010101014543a2a301430103020101046a0a6a686a0a0a
0a09080605050101010101010101010101010101010101010101010110434343a2a24301020201010305680a6a6a0a0a
0a090606070505020101010101010101010102020303030303030301a001010101010101010101010405076a0b0b0a0a
0a090607070806040202010101010101010203040404040404030102010101010101010102020201030507070a0b0b0a
080706070808080706020101010101010102030406060504040302020202020202010102030302020204070709090909
070606070707070606030202010101010102040404040403030202030304040404030252020304040203060608080807
060606a70606060404040202020201010101030303030302020202a50404050505040202020406070402050507070706
040506a9aaaaaaa9a9a80603030504020101030404040302020304a8a9aaaaa9a8a70503030507070602030406060504
0607aaaaabacacaba9a8a8050507070503030304050504040607aaaaabacacaba9a8a805030505050504030305050404
"""
# The works' own pixels: inside this outline (pixel corners: column, row); the cobbles round it are background 3's.
OUTLINE = [(4.5, 1.0), (14.0, 1.0), (14.0, 2.5), (30.0, 2.5), (30.0, 0.5), (35.0, 0.5), (35.0, 3.5), (38.5, 3.5),
           (38.5, 50.0), (5.0, 50.0), (5.0, 35.0), (0.5, 35.0), (0.5, 29.5), (0.0, 29.5), (0.0, 15.5), (3.0, 15.5),
           (3.0, 7.0), (4.5, 7.0)]
DECK = (1.3, 0.8)                 # the deck: its height and how far in from the outline it rounds over
# Rounded boxes (pixel corners column0, row0, column1, row1; height; how far in they round over).
BOXES = [
    (14.0, 3.0, 30.0, 6.5, 2.6, 0.6),      # the dark panel with the tan rails
    (5.0, 7.0, 16.5, 12.0, 5.4, 1.2),      # the big red block, its top arm
    (3.5, 9.0, 9.5, 16.0, 5.2, 1.2),       # and the part bent down at its left
    (10.0, 11.0, 14.0, 15.0, 3.8, 0.6),    # the grey block beside it
    (13.0, 11.0, 19.5, 21.5, 5.0, 0.7),    # the grilles' housing
    (22.0, 7.5, 29.0, 15.5, 5.2, 1.1),     # the red block at the upper right
    (20.0, 18.0, 34.0, 28.0, 2.4, 0.5),    # the dark box in the pipe's frame
    (23.0, 18.0, 29.0, 20.5, 3.0, 0.5),    # its grey lid
    (29.5, 20.5, 33.5, 26.5, 3.0, 0.4),    # its grey slats
    (0.0, 15.5, 10.3, 29.5, 4.0, 0.9),     # the tan box
    (10.0, 17.0, 14.0, 21.0, 3.8, 0.5),    # the grey block under the housing's left
    (11.0, 21.0, 18.5, 29.0, 4.8, 1.0),    # the red block under the housing
    (3.0, 29.5, 6.5, 34.0, 3.0, 0.7),      # the small red block
    (6.0, 33.0, 12.5, 47.5, 4.6, 0.9),     # the tall tan block
    (12.0, 33.0, 18.5, 39.5, 3.2, 0.6),    # the grey block beside it
    (12.0, 39.5, 19.5, 47.5, 4.4, 1.0),    # the red wedge
    (28.8, 33.0, 33.2, 48.5, 4.2, 0.9),    # the red bar at the lower right
]
CORNER = 0.6                      # the boxes' corners rounded in plan
# Lying tubes: points (column, row) with their half-width and height.
TUBES = [
    [(5.4, 3.6, 2.1, 4.4), (13.6, 3.6, 2.1, 4.4)],                         # the grey drum (red caps at its ends)
    [(32.0, 6.5, 0.9, 3.4), (32.0, 15.8, 0.9, 3.4)],                       # the tan rod at the upper right
    [(11.0, 16.9, 1.05, 3.9), (34.5, 16.9, 1.05, 3.9), (34.5, 33.6, 1.05, 3.9)],   # the red pipe along and down
    [(21.0, 28.4, 1.0, 3.6), (34.5, 28.4, 1.0, 3.6)],                      # and back along the box's foot
    [(0.8, 27.6, 0.8, 4.6), (10.0, 27.6, 0.8, 4.6)],                       # the tan rail along the box's foot
    [(36.6, 22.5, 0.8, 3.0), (36.6, 34.5, 0.8, 3.0)],                      # the tan rod at the right edge
]
GRILLES = [((16.5, 13.5), (2.7, 1.8), 6.0), ((16.5, 19.5), (2.7, 1.8), 6.0)]   # middle, radii, top height
BUTTON = ((5.2, 22.8), (2.3, 2.2), 5.6, (3.2, 3.4))   # middle, radii, top; its socket's radius and floor height
KNOB = ((32.4, 3.6), (2.6, 2.8), 3.6)
PANEL = ((23.0, 20.5, 30.0, 27.5), 0.7)   # the tan panel sunk into the dark box (its box, how deep)
DETAIL = (0.12, 0.3)              # the sprite's fine shading as relief on the parts: per shade, its limit (pixels)
GLOW = {0x76: 0.36, 0x7a: 0.48, 0x7d: 0.6}
RED_LIFT = 1.5                    # the reds a little lighter than the other parts (they read dark in the game)
# Each zone's palette indices (a piece holds at most 15 materials: 4 + 4 + 2 + 1 + 3 + 1, so no shade is merged).
SHADES = {"red": [0x44, 0x47, 0x4a, 0x4c], "steel": [0x02, 0x04, 0x06, 0x09], "tan": [0xa3, 0xa5], "rail": [0x18],
          "glow": [0x76, 0x7a, 0x7d]}
FINISH = {"red": (0.35, 0.32), "tan": (0.3, 0.42), "rail": (0.3, 0.4), "steel": (0.45, 0.35), "glow": (0.0, 0.2),
          "dark": (0.3, 0.55)}
PIECES = [("red_works_tl", 15, (0, 0)), ("red_works_tr", 17, (24, 0)), ("red_works_bl", 53, (0, 28)),
          ("red_works_br", 55, (24, 28))]


class Works:
    def __init__(self):
        self.pic = pic = Pic(parse(WORKS_ART), -24.0, 28.0)
        a = pic.a
        inside = nk.polygon_mask(pic, OUTLINE)
        self.own = (a >= 0) & inside
        self.region = Region(pic, self.own, sigma=0.5)
        shade = np.where(self.own, a & 15, 0).astype(float)
        self.soft = blur(nk.fill(shade, self.own), 0.6)
        self.broad = blur(nk.fill(shade, self.own), 2.0)

    @staticmethod
    def cr(X, Y):
        """Picture columns and rows (pixel corners) of plane points."""
        return np.asarray(X, float) + 24.0, 28.0 - np.asarray(Y, float)

    def heights(self, X, Y):
        X, Y = np.asarray(X, float), np.asarray(Y, float)
        c, r = self.cr(X, Y)
        d = self.region.depth(X, Y)
        deck = DECK[0] * round_rise(d, DECK[1])
        z = deck.copy()
        for c0, r0, c1, r1, h, roll in BOXES:
            hw, hh = (c1 - c0) / 2, (r1 - r0) / 2
            qx, qy = np.abs(c - (c0 + c1) / 2) - (hw - CORNER), np.abs(r - (r0 + r1) / 2) - (hh - CORNER)
            sdf = np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - CORNER
            z = smax(z, h * round_rise(-sdf, roll) * (sdf < 0), 0.35)
        for pts in TUBES:
            z = smax(z, nk.tube(c, -r, [(pc, -pr, hw, hh) for pc, pr, hw, hh in pts]), 0.35)
        for (gc, gr), (rx, ry), top in GRILLES:
            z = smax(z, nk.dome(c, -r, (gc, -gr), (rx, ry), top), 0.3)
        (bc, br), (bx, by), btop, (sock, floor) = BUTTON
        dist = np.hypot((c - bc) / sock, (r - br) / sock)
        z = np.where(dist < 1.0, np.minimum(z, floor + (z - floor) * nk.smoothstep(0.8, 1.0, dist)), z)
        z = smax(z, nk.dome(c, -r, (bc, -br), (bx, by), btop), 0.2)
        (kc, kr), (kx, ky), ktop = KNOB
        z = smax(z, nk.dome(c, -r, (kc, -kr), (kx, ky), ktop), 0.3)
        (p0, q0, p1, q1), depth = PANEL
        inner = np.minimum(np.minimum(c - p0, p1 - c), np.minimum(r - q0, q1 - r))
        z = z - depth * nk.smoothstep(0.0, 0.5, inner)
        pic = self.pic
        fine = pic.sample(self.soft, X, Y) - pic.sample(self.broad, X, Y)
        z = z + np.clip(DETAIL[0] * fine, -DETAIL[1], DETAIL[1]) * nk.smoothstep(DECK[0] + 0.3, DECK[0] + 1.2, z)
        z = z * round_rise(d, 0.7)
        return np.where(d > 0, np.maximum(z, 0.0), 0.0)


def build():
    options = k.args()
    out = mk.outdir(options)
    only = set(options["only"].split(",")) if "only" in options else None
    k.reset()
    works = Works()
    pic, own = works.pic, works.own
    a = pic.a
    # The grilles: ramp 7's pixels and the white-hot grey pixel in each (0x0b, 0x0e: the hottest shade).
    core = own & (a >= 0) & (a >> 4 == 0) & nk.gw.dilate(own & (a >> 4 == 7), 1, diagonal=False) & (a & 15 >= 10)
    lamp = own & ((a >> 4 == 7) | core)
    lamp_values = np.where(core, 14.5, pic.shade())
    zones = [Zone("red", own & (a >> 4 == 4), SHADES["red"], FINISH["red"], lift=RED_LIFT),
             Zone("tan", own & (a >> 4 == 10), SHADES["tan"], FINISH["tan"]),
             Zone("rail", own & (a >> 4 == 1), SHADES["rail"], FINISH["rail"]),
             Zone("steel", own & (a >> 4 == 0) & ~core, SHADES["steel"], FINISH["steel"]),
             Zone("glow", lamp, SHADES["glow"], FINISH["glow"], glow=GLOW, sigma=0.6, lift=0.0, comp=0.3,
                  values=lamp_values),
             Zone("dark", own, [0x01], FINISH["dark"], lift=0.0, comp=0.0, pick=False)]
    painter = Painter(pic, zones, "works")
    plate = nk.gw.Plate((-24.0, 24.0, -28.0, 28.0), works.heights, cells=works.region.inside)

    def keys(obj, kinds, wall_z):
        centres, normals = nk.face_data(obj)
        near = painter.zone_at(centres[:, 0], centres[:, 1])
        out_ = painter.keys(obj, zones=["dark" if kinds[i] != 0 else near[i] for i in range(len(kinds))])
        return [("dark", 0x01) if kinds[i] != 0 else key for i, key in enumerate(out_)]
    for name, sprite, (c0, r0) in PIECES:
        if only is not None and name not in only:
            continue
        box = nk.sprite_box(pic, c0, r0)
        parts = nk.piece_parts(plate, keys, [], box, nk.box_owner(box), name, painter, ("dark", 0x01))
        mask = None
        if "check" in options:
            sub = own[r0:r0 + 28, c0:c0 + 24]
            mask = sub.tolist()
        piece = nk.finish(name, parts, box, out, options, painter, mask=mask,
                          origin=(pic.left + c0 + 12, pic.top - r0 - 14))
        bpy.data.objects.remove(piece)


if __name__ == "__main__":
    build()
