"""The eye sphere of LAVA RUN (in the sky) and EYESPY (on the top layer): sheet 9 sprites 153 155 157 / 191 193 195 /
210 212 214 (2x2 each), one 72 x 70 picture; polished (2026-10-22, round 36). It replaces wave3_aj_eye.py (a
heightfield ball painted pixel by pixel, 32.4 pixels tall, its eye a pixelated shell over it).

Where the levels put it (the enemy events): nine pieces as the sheet lays them out, 153 155 157 at (x, y - 56), (x + 24,
y - 56), (x + 48, y - 56), 191 193 195 28 pixels lower, 210 212 214 14 pixels lower still (their boxes overlap 191-195's
lower half): episode 4's enemies 327-335, LAVA RUN t2800 (event 15, the sky) and EYESPY t4400 (event 7, the top
layer). One frame each, no damaged look, nothing launched; 333 and 335 (210, 214) have armour 0 (shots pass through),
the rest 255; 334 (212) fires. The overlapping rows 42-55 are kept by 210-214 (191-195 keep rows 28-41). No other
sprite of any sheet is these pixels mirrored, turned or in other ramps (the ball is round, 97.5 % its own mirror image
in outline, but its plates and lighting are not); no other enemy shows them.

As the sprites and their 4x upscales draw it (the picture's columns and rows; lit from the upper left): a big steel ball
(columns 0-71, rows 0-68) of grey armour plates (ramp 0) with dark seams; on its upper left a raised silver plate
(bright greys, columns 14-37 of rows 8-30), on its upper right a curved strip of light blue glass set into it (ramp 8,
columns 36-49 of rows 10-25); a piston lying on each side above the eye (columns 5-15 of rows 29-37 and 57-67 of rows
29-41: dark sleeves, light rods); on its lower front a great glass eye bulging from the ball (columns 15-56 of rows
36-64): a light blue iris (ramps 8 and 9) shading to deep blue at its rim (ramp 3), a black pupil (columns 29-38 of rows
46-57) and black crosshairs through it, in a dark steel rim.

Built for the game's camera, with polish_sheet9_kit: the ball a flattened sphere (BALL) rolling over at its outline,
the silver plate a plate of its bright pixels raised over it, the strip a glass inlay a little proud of it, the eye a
cap bulging from the ball (EYE) in a raised rim; the sprite's dark seams creased, its fine shading a little relief.
Solids: the pistons (a dark sleeve and a light rod each, lying on the ball). The eye is glass: glossy, glowing a
little in its own blues (0.12-0.35; the ball's round shape reads dark from the slanted camera otherwise). Heights: z 0
to 13.6 (the eye's crown; the old ball rose 32 pixels, through the player's plane on the top layer).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera (z 0: the base, its
layer's plane). The whole's origin is the picture's middle (column 36, row 35): column c is x = c + 0.5 - 36, row r is
y = 34.5 - r; a piece whose sprite's top left pixel is (c0, r0) has its origin at (c0 - 24, 21 - r0) (models.cfg
origin).

models.cfg: the nine model and sprite lines stay as they are (eye_sphere_<sprite> ... origin; yaw=0).

Replaces wave3_aj_eye.py (all of it: delete it).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each piece's outline as the
camera sees it against its sprite's pixels), --preview <prefix>, --only <name,...>.
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
from polish_sheet9_kit import Pic, parse, blur, smoothstep, smax, Region, Zone, Painter, round_rise  # noqa: E402

LEFT, TOP = -36.0, 35.0
W, H = 72, 70

BALL = ((36.0, 34.4), (36.1, 34.7), 11.4)      # the ball: middle (column, row), radii, height
EDGE_ROLL = 2.0
EYE = ((35.6, 50.4), (21.2, 14.6), 2.2)       # the eye: middle, radii, how far its crown bulges over the ball
EYE_RIM = (1.1, 0.55)                         # its rim: width, height over the ball
PLATE_T = 1.1                                 # the silver plate stands this high over the ball
STRIP_T = 0.45                                # the glass strip
CREASE = 0.8
DETAIL = (0.1, 0.3)
PISTONS = [((7.6, 29.6), (15.6, 39.4), 1.9, 1.15), ((64.4, 30.0), (57.0, 40.2), 1.9, 1.15)]  # from, to, radii

PIECES = {153: ((0, 0), None), 155: ((24, 0), None), 157: ((48, 0), None),
          191: ((0, 28), (0, 24, 28, 42)), 193: ((24, 28), (24, 48, 28, 42)), 195: ((48, 28), (48, 72, 28, 42)),
          210: ((0, 42), None), 212: ((24, 42), None), 214: ((48, 42), None)}

GREY = [0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e]
CYAN = [0x81, 0x82, 0x83, 0x85, 0x87, 0x89, 0x8b, 0x8d]
BLUE = [0x9b, 0x9d, 0x9f]
DEEP = [0x33, 0x35, 0x36, 0x38]
FINISH = {"grey": (0.32, 0.34), "plate": (0.4, 0.26), "cyan": (0.1, 0.08), "blue": (0.1, 0.08), "deep": (0.1, 0.1),
          "dark": (0.2, 0.45), "pupil": (0.1, 0.06), "rod": (0.6, 0.18)}
GLOW_CYAN = {0x81: 0.12, 0x82: 0.14, 0x83: 0.16, 0x85: 0.2, 0x87: 0.24, 0x89: 0.28, 0x8b: 0.32, 0x8d: 0.35}
GLOW_BLUE = {0x9b: 0.25, 0x9d: 0.3, 0x9f: 0.35}

EYE_ART = """
    ............................................................010101010101010101010101............................................................
    ....................................................01010101030304030405050504020101............................................................
    ..............................................0101010304040505050606060605030202030301010101....................................................
    ........................................010101010406070707070707070606060204040404030303030301010101............................................
    ....................................01010406060604070808080808080808080405050506060605050505030303030101........................................
    ................................0101040507070708080509080808080808080604060607070606060605050505050404030101....................................
    ..............................0104050707080808080807040909080808080804040607070707070606060605050505040404030101................................
    ..........................0101050707070808080808080806050a09090909070405060707070807070706060605050505040404030301..............................
    ........................01050607070708080808080808080806080a09090805030606070708080807070706060605050505040404030301............................
    ......................010506070708080909080706060505050606090b0a090501020102040505070807070706060605050505040404030301..........................
    ....................010506070708090a0a0907080b0d0e0e0e0c090a0a0c0a090706058080808005050707070706060605050504040403030301........................
    ..................0104060707090a0a0a0a060c0d0e0d0c0c0c0c090a0a0b0d0b090782828383838381060607070706060605050504040403030301......................
    ................010406060708090a0a0a070c0e0c0c0c0c0b0b0b090a0a0b0b0e0a090782828484848382070507070606060505050504040303030201....................
    ..............0104050607070809080908080f0d0c0c0b0b0b0b0907090a0b0b0c0e0b080782838484848383070407060606060505050403020101020101010101............
    ............0103050607070808090909060e0d0c0b0b0b0a09080705090a0b0b0d080808090507828484848383800506060606050503020203030303020202010101..........
    ..........010304060607080808080807070d0c0b0b0b0a08080b0b0708090b0e06070a0b0a050506838585848383800406060605030305040404030303020201010101........
    ..........010405060707080808080806090d0b0b0a0a09080d0e0e0b07070a0d06090a0b09050807078485858383828104060504040605040404030303020202010101........
    ........010304050607070808080808060b0c0a0a0a0a080b0e0f0f0e0705090a040404060507080806828585848383800405040607070504040403030302020201010101......
    ......01030304050607070808080807060b0c0a0a0a0a090c0e0e0e0c0906090708070608080908080805848684848381040406080605050404040303030202020101010101....
    ......01020304050607070708080707060b0b0a0a0a0a0a0c0d0d0c0c0a08080c0e0d0b0b0b0b09080804838786848583800407070505050404040303030302020101010101....
    ....0101020304050606070707070707060b0a0a0a0a0a0a0b0c0c0b0908070c0f0f0e0a090a0b09070805828987858584040908060505050404040303030302020101010101....
    ....0103050204050506060707070706060b090a0a0a0a0a0b0b0b0909080a0f0f0e0a0a080a0b09070807058b86868586030a07060505050404040303030302020101010101....
    ..010204050303040506060606060606050b09090a0a0a0a0b0b0b0b0908080c0e0b0c0b0b0b0b09070808048c87868687040a0606050505040404030303030202010101010101..
    ..010304050505030404050606060605050c080909090a0a0a0a0a0909090807080c0f0b0b0b0a07070908018c8786868704090606050505040404030303030202010101010101..
    ..0104040505060607060505050505050c0a0809090909090909090909090906080f0c0b0b0a0807070909038d8c8d8a8805070708080807050404030303030202010101010101..
    ..020404050506060607070808090a0b090808080909090909090909090908090d0a0a0a09080707090a0a03868485838304050403020202020304030303030202010101010101..
    0102040405050606060707070808080808080808080808080808080808080a0b0907070707070709090a0b01050302020504090a0a070705030101010303030202010101010101..
    01030404050506060607070708080808080808090909090909090a0a0a0a0a0807060606070809090a0a0b0306050706060409070806070605040301010103020201010101010101
    01030404050505060506060707080808070707070706060706050505050606060706060809090a0a0a0b0b0507070707060408060505050504050503020101010201010101010101
    020304040505050503020305070706050505050505060706060606060707070709090909090a0a0b0b0c0a0507070706060307050505050504040404040302010101010101010101
    02030404050504020403040102040405060606070707070707070708080808080b0a0a0a0a0b0b0b0c0a040607070606060307050505050404040401030404010101010101010101
    0203040404040203060b050402060606070707070707070708080808080808080e0b0b0b0b0c0c0c0a05060707060606060306050505050404040201040505030101010101010101
    02030404040401030501070503050707070707070707070808080808080808080e0d0d0c0c0b0b070506070706060606050105060505040404040102040702020201010101010101
    0203030403020103050e0a07050305060606060607070708080808080808090a0b0a0a0a0a0a09050808070606060606030205060505040404030104060702010101010101010101
    020303020203010304090a070604050606060606070707080808090b0b0b0b0a0a0a0a0a090909050909080808070605020205050504040403010207070302010101010101010101
    020301010303020104050a0b0605030506060606060707090c0c0c0b0b0807070706040404060706080808080808070504020304040403020203040b030301010101010101010101
    02010102030403020304050c090604030606060606070a0b0b0a09080706839d9e9e9e89819e9d9d9d09080808070707070605020203020206080c07030101020101010101010101
    0102020303040302030405050c07070403040606080a0a09090707829e9e898989898989829f9e9d9e9d9d9c09070707070706050302010104060a04020102020101010101010101
    010102030304030405030405080d0a05030307090908080982839e8b8a89899d81818389829f9c39849c849d9d9c9c08070606060505030304050605010202020101010101010101
    010102030303040507010405070b030204060908080882819c8e8b8b9e9d828382829c89839f9e829c83849c9d9d9d9c820505060605050803020303020202010101010101010101
    ..010203030306070501010306030307070608080883389d8e8b9e83839c82839b9d9f8e839f9c839c839c84849c9d9c9b8104050504060703010102020202010101010101010101
    ..01010203040604030102010402050b0705070783389d8c8a9c9d9e9d9f9d829b9e8b8f818e828381829c82839c9c9c839c82040306070301010102020201010101010101010102
    ....01020406040204040301010202080a060682389c9f9d9c9e8b8b8b9f9f839b9d8c8f829f83823883813882848383838282810503040202030101020101010101010101010101
    ....0101020502020304040301020405070881379c9c9c849c8b8d8f8c8b9f9e9c9d9f9f348e9c383838368282818283838182838104030404030201010101010101010101020201
    ....01010504020303030404040506050481349c9c849c839d8b8b8f8e8b9f9e9c9d9b9f349f823536363881818182828182828383810503040403010101010101010101010202..
    ....01010402010303030304040506068138839c838283839c9f8b8d8c8b8b9f9f9e9f8b618b813536388138388238818282828383848203030402010101010101010101020202..
    ....010303010102030303030406060681368482818283839c9d9f8b8b8b9f9d9c9f8382019d333338813881383638828282828382828005030302020101010101010102020202..
    ....0102010102020203030304050681368184818182839c9e9e9e9e9f9f9e83833835350182010101353836363838388181813882828281010303020101010101010102020201..
    ....01020101020202020203040505383581823881829c9d9e9f9f9e9e9f9c810101010101380101013335363836363682828181828282380103030201010101010102020302....
    ....01010101020202020202040505383581388181829d9e3e3e9f9e9e9f9e360101010101356161616133819c9d9d9c83828181828281800103030201010101010102030301....
    ......0101010101020202020304053661388181389c9e9f3e3e3e9f9e9c82010101010101010161610101613533333536353535363533910103030201010101010204040101....
    ........0101010101010202030404360133353336363535353535353501010101010101619e84849d9f9c9e9d9d9d9d9c838586888a893a01030302010101020203040201......
    ..........010101010101020304043661368383839c9d9e9f9f9e9d8385010101010101619c803836350161363637373881388181818335020303020101020203040301........
    ..........01010101010101030304366135828283839c9e9e9f9e9c83840101010101010181360134336133363636373738818181829d35020303010202020405040101........
    ............01010101010101030404016181813838388182828282828335010101010101363534346101363636373738388181839d39030304030202030405050201..........
    ..............0101010101010202036133818281383838818383823838386101010101013635336133333636353781828382818483350303040101030405060201............
    ................0101010101020203023535388181818282813838388282386101010101366101016135383838373881839c9e9e360304040301030505060201..............
    ..................0101010101020203033535388138383838383835388138813301010136610133383681388181828281819e820305040302040506060301................
    ....................010101010102020303333636813838363638828138818238363501823636353538358138819c9d9d9f840405050603040507060301..................
    ......................010101010202020303333336363881828281388182823836380182363638368181819c8282859f3a0405050508020406050101....................
    ........................010101010202020304333536818181813881828281818181018238358181389c82819d9f8b3b05050606060a0106040101......................
    ..........................0101010102020202043333363838353881838282818281618283819c9c819c9d869f8b820506060606080d02010101........................
    ..............................0101010102020204033335333881819c828281833861819c81839c9d839f86820506060706060708080101............................
    ................................0101010102020202040302333636818183819d3835829e839c9d9f8306050606070507070707040201..............................
    ....................................010101010303030404040404353581819d82389c9e9c9c0605060607060606060604010101..................................
    ........................................010101010202020204040405050506060404050505070607070707060504010101......................................
    ..............................................010101020202020304040505050606060606060505040101010101............................................
    ....................................................010101010202010202020202020202010101010101..................................................
    ............................................................01010101010101010101010101..........................................................
"""


def picture():
    return Pic(parse(EYE_ART), LEFT, TOP)


def CR(X, Y):
    return np.asarray(X, float) - LEFT, TOP - np.asarray(Y, float)


def XY(c, r):
    return c + LEFT, TOP - r


class Sphere:
    def __init__(self, pic):
        self.pic = pic
        a = pic.a
        own = a >= 0
        rows = np.arange(pic.h)[:, None] * np.ones((1, pic.w))
        cols = np.ones((pic.h, 1)) * np.arange(pic.w)[None, :]
        self.own = own
        self.region = Region(pic, own, sigma=0.5)
        grey = own & (a >> 4 == 0)
        shade = np.where(own, a & 15, 0)
        self.plate_mask = grey & (shade >= 10) & (rows >= 8) & (rows <= 31) & (cols >= 13) & (cols <= 38)
        self.plate_mask = nk.erode(nk.dilate(self.plate_mask, 2), 1) & own
        self.plate_region = Region(pic, self.plate_mask, sigma=0.7)
        self.strip = own & (a >> 4 == 8) & (rows < 30)
        self.strip_region = Region(pic, self.strip, sigma=0.5)
        dark = own & (a >> 4 == 0) & (shade <= 1)
        h, w = a.shape
        p = np.pad(own, 1)
        surrounded = np.ones_like(own)
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            surrounded &= p[1 + dr:1 + dr + h, 1 + dc:1 + dc + w]
        self.crease = blur((dark & surrounded & ~self.eye_mask_px(rows, cols)).astype(float), 0.45)
        self.soft = blur(nk.fill(shade.astype(float), grey), 0.6)
        self.broad = blur(nk.fill(shade.astype(float), grey), 2.0)

    def eye_mask_px(self, rows, cols):
        (ec, er), (rx, ry), _ = EYE
        return ((cols + 0.5 - ec) / (rx + 1.6)) ** 2 + ((rows + 0.5 - er) / (ry + 1.6)) ** 2 < 1.0

    def ball(self, X, Y):
        C, R = CR(X, Y)
        (bc, br), (rx, ry), hh = BALL
        q = np.clip(1.0 - ((C - bc) / rx) ** 2 - ((R - br) / ry) ** 2, 0.0, 1.0)
        return hh * np.sqrt(q)

    def eye_q(self, X, Y):
        C, R = CR(X, Y)
        (ec, er), (rx, ry), _ = EYE
        return ((C - ec) / rx) ** 2 + ((R - er) / ry) ** 2

    def heights(self, X, Y):
        X, Y = np.asarray(X, float), np.asarray(Y, float)
        pic = self.pic
        d = self.region.depth(X, Y)
        z = self.ball(X, Y)
        z = z - CREASE * pic.sample(self.crease, X, Y) * np.clip(z / 4.0, 0.0, 1.0)
        fine = pic.sample(self.soft, X, Y) - pic.sample(self.broad, X, Y)
        q = self.eye_q(X, Y)
        z = z + np.clip(DETAIL[0] * fine, -DETAIL[1], DETAIL[1]) * (q > 1.15)
        pd = self.plate_region.depth(X, Y)
        z = z + PLATE_T * round_rise(np.maximum(pd, 0.0), 1.0) * (pd > 0)
        sd = self.strip_region.depth(X, Y)
        z = z + STRIP_T * round_rise(np.maximum(sd, 0.0), 0.8) * (sd > 0)
        # The eye: a cap bulging over the ball, in a rim.
        rimw, rimh = EYE_RIM
        r = np.sqrt(q)
        (ec, er), (rx, ry), bulge = EYE
        cap = bulge * np.sqrt(np.clip(1.0 - q, 0.0, 1.0)) + 0.35
        rim = rimh * np.clip(1.0 - np.abs(r - 1.0) * min(rx, ry) / rimw, 0.0, 1.0) ** 0.6
        z = z + np.where(q < 1.0, cap, 0.0) + rim
        z = z * round_rise(d, EDGE_ROLL)
        return np.where(d > 0, np.maximum(z, 0.0), 0.0)

    def cells(self, X, Y):
        return self.region.inside(X, Y)


def zones(pic, sph):
    a = pic.a
    own = a >= 0
    grey = own & (a >> 4 == 0)
    return [Zone("grey", grey, GREY, FINISH["grey"]),
            Zone("plate", grey, GREY, FINISH["plate"], lift=1.6, pick=False),
            Zone("cyan", own & (a >> 4 == 8), CYAN, FINISH["cyan"], glow=GLOW_CYAN, sigma=0.6, lift=0.8, comp=1.2),
            Zone("blue", own & (a >> 4 == 9), BLUE, FINISH["blue"], glow=GLOW_BLUE, sigma=0.5, lift=0.4, comp=0.8),
            Zone("deep", own & np.isin(a >> 4, [3, 6]), DEEP, FINISH["deep"], sigma=0.5, lift=0.6, comp=1.0),
            Zone("pupil", own & ((a & 15) <= 1), [0x01, 0x02], FINISH["pupil"], lift=0.0, comp=0.0, pick=False),
            Zone("dark", grey, [0x01, 0x02], FINISH["dark"], lift=0.0, comp=0.0, pick=False)]


def plate_keys(sph, painter):
    def keys(obj, kinds, wall_z):
        centres, normals = nk.face_data(obj)
        X, Y = centres[:, 0], centres[:, 1]
        q = sph.eye_q(X, Y)
        pic = sph.pic
        px = pic.pixel(X, Y)
        inside_eye = q < 1.0
        rim = (q >= 1.0) & (q < 1.16)
        pd = sph.plate_region.depth(X, Y)
        names = []
        near = painter.zone_at(X, Y)
        for i in range(len(X)):
            if kinds[i] != 0:
                names.append("dark")
            elif inside_eye[i]:
                v = px[i]
                if v >= 0 and (v & 15) <= 1 and v >> 4 in (0, 6):
                    names.append("pupil")
                elif near[i] in ("cyan", "blue", "deep"):
                    names.append(near[i])
                else:
                    names.append("deep")
            elif rim[i]:
                names.append("dark")
            elif near[i] == "cyan":
                names.append("cyan")
            elif pd[i] > 0.3:
                names.append("plate")
            else:
                names.append("grey")
        out = painter.keys(obj, zones=names)
        return [("dark", 0x02) if (kinds[i] != 0 or (rim[i] and kinds[i] == 0)) else key for i, key in enumerate(out)]
    return keys


def solids(sph, painter):
    out = []
    for i, ((c0, r0), (c1, r1), rs, rr) in enumerate(PISTONS):
        x0, y0 = XY(c0, r0)
        x1, y1 = XY(c1, r1)
        z0 = float(sph.ball(np.array([x0]), np.array([y0]))[0]) + rs * 0.35
        z1 = float(sph.ball(np.array([x1]), np.array([y1]))[0]) + rs * 0.35
        n = 6
        pts = [(x0 + (x1 - x0) * j / n, y0 + (y1 - y0) * j / n, z0 + (z1 - z0) * j / n) for j in range(n + 1)]
        m = 4
        sleeve = nk.loft_path("piston_sleeve%d" % i, pts[:m + 1], [rs] * (m + 1), around=16, squash=0.9)
        nk.assign(sleeve, painter.keys(sleeve, zone="grey", offset=-1.5), painter)
        rod = nk.loft_path("piston_rod%d" % i, pts[m - 1:], [rr] * (len(pts) - m + 1), around=14, squash=0.9)
        nk.assign(rod, painter.keys(rod, zone="plate", offset=1.5), painter)
        out += [sleeve, rod]
    return out


def build():
    options = k.args()
    out = mk.outdir(options)
    only = set(options["only"].split(",")) if "only" in options else None
    k.reset()
    pic = picture()
    sph = Sphere(pic)
    plate = nk.gw.Plate((LEFT, LEFT + W, TOP - H, TOP), sph.heights, cells=sph.cells)
    painter = Painter(pic, zones(pic, sph), "eye_sphere")
    parts = solids(sph, painter)
    for p in parts:
        p.hide_render = True
    keys = plate_keys(sph, painter)
    for sprite, ((c0, r0), keep) in PIECES.items():
        name = "eye_sphere_%d" % sprite
        if only is not None and name not in only:
            continue
        box = nk.own_box(pic, c0, r0, keep)
        pieces = nk.piece_parts(plate, keys, parts, box, nk.box_owner(box), name, painter, ("dark", 0x02))
        for p in pieces:
            p.hide_render = False
        mask = None
        if "check" in options:
            m = np.array(nk.sprite_mask(pic, c0, r0))
            if keep is not None:
                kc0, kc1, kr0, kr1 = keep
                sub = np.zeros_like(m)
                sub[max(0, kr0 - r0):kr1 - r0, max(0, kc0 - c0):kc1 - c0] = True
                m = m & sub
            mask = m.tolist()
        piece = nk.finish(name, pieces, box, out, options, painter, mask=mask, origin=(LEFT + c0 + 12, TOP - r0 - 14))
        bpy.data.objects.remove(piece)


if __name__ == "__main__":
    build()
