"""The armoured head of UNDERDELI, DREAD-NOT, GRAVITRON (on the ground) and LAVA RUN (in the sky): sheet 9 sprites
10 12 / 28 32 / 47 49 51 / 85 87 89 (2x2 each), one 72 x 84 picture; polished (2026-10-22, round 36). It replaces
wave3_aj_head.py (a heightfield painted pixel by pixel, 22.6 pixels tall, its knob, pipes and bulbs on it).

Where the levels put it (the enemy events): ten armoured pieces (armour 255, never destroyed) as the sheet lays them
out, 85 87 89 at (x, y), (x + 24, y), (x + 48, y), 47 49 51 28 pixels above them, 28 and 32 at (x, y - 42) and
(x + 48, y - 42), 10 and 12 at (x + 12, y - 56) and (x + 36, y - 56): episode 4's enemies 309-318 (336, 87 again, for
310 in LAVA RUN), UNDERDELI t4600 and t9600 and DREAD-NOT t100 on the ground (event 6), LAVA RUN t2880 in the sky
(event 15), GRAVITRON (episode 6) t6000 on the ground (its enemies 1665-1669 are 49 51 85 87 47 again). One frame each,
no damaged look (dgr 0), nothing launched (313's launch, enemy 337, needs a launch frequency no event gives it). The
sprites overlap: 10 and 28, 12 and 32 share a tile; 28 and 32 reach into 47 and 51's rows; each region is kept by one
piece: 10 and 12 the dome's top (columns 12-59, rows 0-27), 28 and 32 only its sides (columns 0-11 and 60-71 of rows
14-27), the others their whole boxes. No other sprite of any sheet is these pixels mirrored, turned or in other ramps
(the head is symmetric about the middle of column 35 in outline, 99.5 %, but lit from the upper left: each side is
painted by its own pixels); no other enemy shows them.
What stands on it: UNDERDELI puts its lilac capsule (9 123, polish_deli_capsule.py) on the jaw's middle (columns 23-46,
rows 57-84) and, a tick before the head, the pulsing blob (5 121, blob_big, 10.9 pixels tall) that fires its shots
under the dome's middle (columns 25-47, rows 17-39): the dome stands over it there (at least 12 pixels), as the
sprites cover it. DREAD-NOT lays its shoulders over the dome and its bladed shell over the jaw (polish_dread_parts.py,
which builds them over this head's heights: heights()).

As the sprites and their 4x upscales draw it (the picture's columns and rows; symmetric about the middle of column 35,
x = -0.5; lit from the upper left): a dome of grey armour plates (ramp 0, rows 8-36) with a raised Y seam down to a
steel knob (columns 28-42 of rows 36-48) and panel lines; over each side a thick glossy red brow (ramp 4, columns 3-30
and 41-67 of rows 24-43) curling down at its outer end; under the brows dark slots with two black pipes each (rows
38-41 and 43-46) and a small red pad (columns 8-16 and 54-62 of rows 42-46); below them the broad jaw plate (rows
47-82): its top edge rolled into a lit lip, a ridge down its middle, four glossy red bulbs in sockets in a V (columns
10-18 and 52-60 of rows 55-65, 22-30 and 40-48 of rows 61-72), its lower edge in two lobes either side of a notch.

Built for the game's camera, with polish_sheet9_kit (the picture's plane sheared along the camera's line of sight; a
heightfield body on the sprites' grid; solids cut along the pieces' boxes; painted by the picture): the body's dome a
crown (DOME) rolling over at the outline (EDGE_ROLL), the brows plates of their red pixels standing BROW_T over it,
the slots carved to SLOT_FLOOR between them and the jaw, the jaw a plate (JAW) with its lip, its ridge and its
sockets; the sprite's dark lines creased, its fine shading (the panel lines, the seam) a little relief. Solids: the
knob (a steel ball with a collar), the pipes (black tubes lying in the slots, ringed), the bulbs (glossy red
ellipsoids sunk into their sockets). Heights: z 0 (the base) to 14.2 (the knob's top; the dome 13.5): low enough for
the sky (under background 3) and for what DREAD-NOT lays over it.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera (z 0: the base).
The whole's origin is the picture's middle (column 36, row 42): column c is x = c + 0.5 - 36, row r is y = 41.5 - r; a
piece whose sprite's top left pixel is (c0, r0) has its origin at (c0 - 24, 28 - r0) (models.cfg origin).

models.cfg: the ten model lines stay (dome_head_<sprite> enemies/dome_head_<sprite>.glb origin); the sprite lines get
height=-4 (on the terrain: drawn at its origin a ground piece stands 4 pixels over it; in LAVA RUN's sky 4 pixels lower,
under background 3). DREAD-NOT's other parts and UNDERDELI's capsule get the same (see their scripts).

Replaces wave3_aj_head.py (all of it: delete it; wave3_aj_dread.py imported its heights: it is replaced too).

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

LEFT, TOP = -36.0, 42.0
ROW0 = 8                          # the art below starts at the picture's row 8 (rows 0-7 and 83 are empty)
W, H = 72, 84
AXIS_C = 35.5                     # the mirror line: the middle of column 35 (x = -0.5)

# --- Heights (picture columns C and rows R, continuous: pixel c spans C c .. c + 1) ------------------------------------
DOME = ((35.5, 29.0), (42.0, 30.0), 6.0, 14.0)   # the crown: centre, radii, height at its rim and at its middle
EDGE_ROLL = 5.5                   # the dome rolls over to its outline within this
BROW_T, BROW_ROLL = 3.2, 2.4      # the brows: how far they stand over the dome, how far in from their outline
BROW_BASE = 8.6                   # their underside at least this high (where the dome falls away under their ends)
SLOT_FLOOR = 4.2                  # the slots' floor
SLOT_ROWS = (36.6, 47.4)          # the slots' upper and lower edge (rows)
KNOB_C = 7.6                      # the slots stop this far from the axis (the knob)
POST = (7.6, 11.0, 42.6, 11.6)    # the brows' inner ends hanging down beside the knob (from, to the axis; their lower
                                  # row; their top): they keep the slots off the blob UNDERDELI hides under the dome
PAD_T = 2.4                       # the red pads stand this high over the slots' floor
JAW = (5.4, 9.0)                  # the jaw plate's height at its sides and in its middle
JAW_TOP = 47.3                    # the jaw's top edge (row)
LIP = (51.2, 2.2, 1.3)            # its lip: the crest's row, its half width, its height
RIDGE = (5.2, 1.6, (49.0, 80.0))  # the ridge down the middle: half width, height, rows
JAW_ROLL = 2.6                    # the jaw rolls over to its outline within this
SOCKET = (1.0, 1.6)               # the bulbs' sockets: how far beyond a bulb, how deep
CREASE = 1.0                      # the sprite's dark lines inside the head cut this deep
DETAIL = (0.22, 0.45)             # its fine shading as relief: per shade, its limit

# The bulbs (from the sprite's red pixels): (column, row, radius across, radius along) and their tilt (degrees).
BULBS = [(14.6, 60.6, 4.6, 5.8, 10.0), (56.4, 60.6, 4.6, 5.8, -10.0),
         (26.1, 66.8, 4.6, 6.2, 12.0), (44.9, 66.8, 4.6, 6.2, -12.0)]
BULB_RZ, BULB_SINK = 3.4, 1.4     # their height (half), how far their middle lies under the jaw's surface
KNOB = ((35.5, 41.9), (7.3, 6.4, 5.6), 9.6)       # the knob: middle (column, row), radii, its middle's height
PIPES = [  # (from column, to column, row, radius): the left slot's (the right one's mirrored)
    (8.4, 26.4, 39.7, 2.05), (16.8, 27.6, 44.8, 1.55)]

# The pieces: sprite -> (top left pixel of its box, the part of the picture it keeps: columns c0 c1, rows r0 r1).
PIECES = {10: ((12, 0), (12, 36, 0, 28)), 12: ((36, 0), (36, 60, 0, 28)),
          28: ((0, 14), (0, 12, 14, 28)), 32: ((48, 14), (60, 72, 14, 28)),
          47: ((0, 28), None), 49: ((24, 28), None), 51: ((48, 28), None),
          85: ((0, 56), None), 87: ((24, 56), None), 89: ((48, 56), None)}

GREY = [0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c]
RED = [0x43, 0x45, 0x47, 0x49, 0x4b, 0x4d]
PIPE = [0x01, 0x02, 0x03, 0x05, 0x07, 0x0a]
FINISH = {"grey": (0.32, 0.36), "red": (0.08, 0.22), "pipe": (0.45, 0.24), "knob": (0.45, 0.26), "dark": (0.2, 0.5)}

HEAD_ART = """
    ..............................................................010101010101010101................................................................
    ............................................................0101030404040404030201010101........................................................
    ......................................................0102020706060606060606060505050301010101..................................................
    ..................................................020103030208070707070707070606060506050203040101..............................................
    ........................................0101..02030505050505090808070707070707070806050407050404040101..........................................
    ....................................0101050203050506060606050a08080808080807080805050708060505040404030101......................................
    ..................................010405080305050606060606050a090a0a0909090908050506040508060505040404030201....................................
    ..............................0101050507080305050607070707060a0b05060606080907070a070606040805050504040404030101................................
    ............................010505060707070905050607070707090a0607070707070707090808070706030805050404040505030201..............................
    ..........................010406070707080807090706060708090906070708080808070809080807070705030705050404040505050201............................
    ........................01050607070708080808080a0909090909090607080808080808070908080707070605020705040404040506050201..........................
    ......................010406070708080808080808090a0908070707090708080808080807090808070707060604030504030304040506050301........................
    ....................0104050707080808080808080a0a0706060707070709070808080808070a080807070706060502040403030304040506050401......................
    ..................0104050707080808080808080a09060606060607070707090708080807090a08070707060606050502030303030304040506050401....................
    ..................01040707080808080808080a09060605040505050607070809070607090b0807070707060606050502030303030303040405060501....................
    ................010405070701010101010809090506050405060606050507080909090a0a08080707070606060505050402020301010101010305060301..................
    ................01040607014142444443010908060604060607070707060508090908080808070707060606060505050402030141434242410104060401..................
    ................01040701424445464644424006070306070707070707070605090909080808070706060606050505040302014345464645444201040501..................
    ................01040144454647484948454401060406070707070706060606050907070808070606060605050504040301444647464646454644010301..................
    ................010145464647474a4a49484501050306060606060606060605050907070708060606060505050404030301454749474646464546450101..................
    ................0144464647474a4d4d49494742010206060606060606060505050906060608060605050505040403030145484947464646464645464501..................
    ..............014345464647494d4f4e4a4949474401010101010101050505050509060606080606050101010101010145484a474646464646464545464401................
    ............01444446464747494c4f4f4a494949484848484745454501050505050a0606060806040143454646464647494b4746464646464646454545464501..............
    ..........01434445464647474a4d4e4e49494949494949494948474645010505050a06060608060144444a4b4b4b4b4b4b48464646464646464645454445464401............
    ........014344464646464747484a4a4948494949494949494949494745010304040a06060608060144484d4f4c4a4947474746464646464646454545444445464401..........
    ........0144454646464647474747474848484949494949494949494744010404040a07060608060144464b4b48474747474646464646464545454544444445454601..........
    ......0143454646464646464747474747484848484849494949484745450104030409080807070501434647474747474746464645454545454545444444444545464501........
    ......0144454646464646464646464647474747474747474747464544444005050405050504040401434545454545454545454545454545454444444444444545464601........
    ....01444545464646464645444241424344424140404141434444434301050606060606060605050401434546454444444444444444444444444444444445454546474501......
    ....01434445464646454401010101010101010101010101014340430105060707070707060606050302014343420101010101010104060301010101434445454546474401......
    ....014344454545440101030303040504040103030303030301420104060708090909080706030202030201430102030302020302040a0805050403010144454647464401......
    ....014342444443010303030305070a0c0701030307050403034003040607080b0b0908080405040403040301020307050302040203060503030304040401444646454301......
    ....01014242430103020202020202040404010202080b0403024003050607080c0b090905080605040304030102070b070302050102030301010101030506014242420101......
    ......01010101020202020201010101020201020204070603024003050607080b0a08050a070605040305030104090c0702030501010101010101010101050801010101........
    ..........010202020201014445454301020101010101404002400305060708090a040a080706050403060301020405010102040101014545444301010101040801............
    ..........01030202014444464646440102010101010140010240010201030304040308070606040404060301030404040404040101014547484645430101010601............
    ..........01030201444446484646444301010509090705050303010204060808090307060605040305070103040101010102040101444445474645454301010101............
    ............0101444446464644440101010103040202020303030103040506060603060505040405070401020201010102040101010101444445454545430101..............
    ..............014545444401010104040401030302020202030303010104050606030504040405070401020202010101050201010303030101014444444401................
    ................01010101050505040404010202020202020302020102030404040104040406070202010202020104040201010103030303030301010101..................
    ............0101040707070708070606050301010101010102020202020204030402050506060404020201020303020101010103030303030303030202020101..............
    ........010103040506070808080808060505050101030304040404040103030304020403020102020203030303010101010103030303030303020202020203040101..........
    ....0101030406060607080808080808080805050505010101010101010305080a0b0a09090908070603020201010101010303030303030303020203030304040404040101......
    ..010303060606070707070808090909080807060606050606070707060603040606050505040406030305050403030303030303030303030202020203040405040404040401....
    ..02040506070707070708090a0a0a0a090908080606070708080809080606030406050505050603010506060504030304040404040404020202020303030505050404040404....
    0205050606070707070708090a0b0c0c0b0a0a0a0b0b09080808090a09080605010705050505050204060706050304040504040404020203030303030203040405050404040403..
    030505060607070707080809020202020201010202040a0b0808090909080806040805050505060204050606050405040401010101010101010101030102040404050505040403..
    0305050606070707080809014240424401010204040402040b09080808080705040806050505070203050505060705010102020201010143434242010203030404040505040403..
    030505060606070708070141424446444301030505040505040a070707070705060806060505070303050505070601030401010101014244444342420103030304040404040303..
    03050505060606070801414447474745434401050707060404030a0907060704060906060605070502040507070103030502010101424445454543424401010303040404030303..
    030405050504040304014146474a4b4743430205070706060504040906050407090707060606060804030407020303040505020101444648474545434501010101020303030302..
    0204050201020506070143474749494745444601060606060603060306070609070707070606060708040201030302040202010141454649474545424601030101010103020202..
    0103020102070809070144474748494746444601050606060301020303080907070707070706060607060101010101020201010143454546454544424601040403010101010202..
    ..01010205090b080701444647474747454446030506060344454544440408070707070707070706050144444343420102010101444445454544444244010404040402010102....
    ..010103050808070707014446464645444446030406034445474747464403070707070707070707034345464645434201020101444444444444434201040404040403010102....
    ..010103030506060607014444444444444547030203444547474746454503070707070707070705034446474645444343010101434444444342424201040404040505040201....
    ....010203040405060607014444454646474701010344474a4947464446460307070607070706034345474a47454443420101014243424242414202050404040505050501......
    ....010203030405060606060146474747470102040345484a4947464446450307070606060606034445464745454444420101010140414242420205040405050505060401......
    ....01020203040505060606060101010201010306034747484847464445450307060605050605034345454545444443430101010101010202020504050505050506060401......
    ....01020203030405050606060708020204030406034747474747454445460307070809080706034245454544444343430101010101010306050505050505060606040101......
    ....01020202030304050606060607080802020506034647474645444346030708070506080807040344454444434242430101010101040705050505050606060705020202......
    ......0101020203030505060606060607070701050344464544444345470408060505050504080501424444434242434401010103040704050505060606070705020201........
    ........010102020303050506060606060607070302444344444445470408070605050504040408060141424242434543010104080704050506060607070704020101..........
    ............01010104040505060606060606060702454445454647030a0706060404040404030509040142434445444201070806040505060607070604010102..............
    ..................0101040405050405060606060701454546460208070506040404040303030305080401424343420104040404050606060606050102....................
    ......................01010305050505050606060601010101050606040403030303030302030407040301010101030304040506060606060303........................
    ..........................010104040404050505060606060605050604040303020202020303030a04040404030202030405050605050303............................
    ..............................01010303040405050505050505050504040202020202020303030b0404040403030303040506050203................................
    ..................................0101030404050505050505050403030201010101010303030a040504040303030304040202....................................
    ......................................010304040404040404040403030101......010103030805050404030303030202........................................
    ........................................010304040404040404040301..............010408050504040303030301..........................................
    ..........................................01020303030303030301..................01080504040303020301............................................
    ............................................010303030303030301..................010706040303030301..............................................
    ..............................................0101030303030301..................0106040301010101................................................
    ..................................................010101010101..................020202010203....................................................
"""


def picture():
    rows = parse(HEAD_ART)
    rows = [[None] * W for _ in range(ROW0)] + rows
    rows += [[None] * W for _ in range(H - len(rows))]
    return Pic(rows, LEFT, TOP)


def CR(X, Y):
    return np.asarray(X, float) - LEFT, TOP - np.asarray(Y, float)


def XY(c, r):
    return c + LEFT, TOP - r


class Head:
    """The head's shapes in the picture's plane."""

    def __init__(self, pic):
        self.pic = pic
        a = pic.a
        rows = np.arange(pic.h)[:, None] * np.ones((1, pic.w))
        cols = np.ones((pic.h, 1)) * np.arange(pic.w)[None, :]
        own = a >= 0
        self.own = own
        self.red = own & (a >> 4 == 4)
        self.brow = self.red & (rows < 42)
        self.pads = self.red & (rows >= 42) & (rows < 48) & (np.abs(cols + 0.5 - AXIS_C) > 15)
        self.bulb = self.red & (rows >= 53)
        self.region = Region(pic, own, sigma=0.5)
        self.brow_region = Region(pic, self.brow, sigma=0.55)
        self.pad_region = Region(pic, self.pads, sigma=0.5)
        # The jaw's own outline (rows 47 on) for its roll.
        self.jaw_region = Region(pic, own & (rows >= 46), sigma=0.5)
        dark = own & (a >> 4 == 0) & ((a & 15) <= 1)
        h, w = a.shape
        p = np.pad(own, 1)
        surrounded = np.ones_like(own)
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            surrounded &= p[1 + dr:1 + dr + h, 1 + dc:1 + dc + w]
        self.crease = blur((dark & surrounded & (rows < 37)).astype(float), 0.45)
        shade = np.where(own, a & 15, 0).astype(float)
        grey = own & (a >> 4 == 0)
        self.soft = blur(nk.fill(shade, grey), 0.6)
        self.broad = blur(nk.fill(shade, grey), 2.0)

    # The parts' heights ------------------------------------------------------------------------------------------------
    def dome(self, X, Y, d):
        C, R = CR(X, Y)
        (cc, cr), (rx, ry), h0, h1 = DOME
        q = np.clip(1.0 - ((C - cc) / rx) ** 2 - ((R - cr) / ry) ** 2, 0.0, 1.0)
        crown = h0 + (h1 - h0) * np.sqrt(q)
        return crown * round_rise(d, EDGE_ROLL)

    def slot_amount(self, X, Y):
        C, R = CR(X, Y)
        rows = smoothstep(SLOT_ROWS[0] - 0.6, SLOT_ROWS[0] + 0.6, R) * (1.0 - smoothstep(SLOT_ROWS[1] - 0.6, SLOT_ROWS[1] + 0.4, R))
        side = smoothstep(KNOB_C - 0.5, KNOB_C + 0.8, np.abs(C - AXIS_C))
        return rows * side

    def post_amount(self, X, Y):
        C, R = CR(X, Y)
        u = np.abs(C - AXIS_C)
        return (smoothstep(POST[0] - 0.3, POST[0] + 0.3, u) * (1.0 - smoothstep(POST[1] - 0.6, POST[1] + 0.4, u)) *
                (1.0 - smoothstep(POST[2] - 0.8, POST[2] + 0.4, R)))

    def jaw(self, X, Y):
        C, R = CR(X, Y)
        u = np.clip(np.abs(C - AXIS_C) / 36.0, 0.0, 1.0)
        top = JAW[0] + (JAW[1] - JAW[0]) * (1.0 - u ** 1.6)
        top = top - 0.045 * np.clip(R - 56.0, 0.0, None)                       # falling a little towards its foot
        lip = LIP[2] * np.exp(-((R - LIP[0]) / LIP[1]) ** 2)
        rw, rh, (r0, r1) = RIDGE
        ridge = rh * (1.0 - smoothstep(rw - 1.0, rw + 0.6, np.abs(C - AXIS_C))) * smoothstep(r0, r0 + 2.5, R) * \
            (1.0 - smoothstep(r1 - 3.0, r1, R))
        # The jaw's top edge rolls down to the slots' floor.
        rise = smoothstep(JAW_TOP - 0.6, JAW_TOP + 2.6, R)
        z = SLOT_FLOOR + (top + lip + ridge - SLOT_FLOOR) * rise
        for bc, br, rx, ry, _t in BULBS:
            q = ((C - bc) / (rx + SOCKET[0])) ** 2 + ((R - br) / (ry + SOCKET[0])) ** 2
            z = z - SOCKET[1] * (1.0 - smoothstep(0.55, 1.0, q))
        return z

    def heights(self, X, Y):
        """The head's top over the plane (0 off it)."""
        X, Y = np.asarray(X, float), np.asarray(Y, float)
        C, R = CR(X, Y)
        d = self.region.depth(X, Y)
        z = self.dome(X, Y, d)
        # The slots: carved to their floor under the brows, between the knob and the head's sides.
        s = self.slot_amount(X, Y)
        post = self.post_amount(X, Y)
        floor = SLOT_FLOOR + (POST[3] - SLOT_FLOOR) * post
        z = z + (np.minimum(z, floor) - z) * s
        # The jaw from its top edge down.
        jz = self.jaw(X, Y) * round_rise(self.jaw_region.depth(X, Y), JAW_ROLL)
        z = np.where(R > JAW_TOP - 1.5, smax(z * (1.0 - smoothstep(JAW_TOP - 1.0, JAW_TOP + 1.0, R)), jz, 0.8), z)
        # The sprite's dark lines and fine shading.
        pic = self.pic
        z = z - CREASE * pic.sample(self.crease, X, Y) * np.clip(z / 4.0, 0.0, 1.0)
        fine = pic.sample(self.soft, X, Y) - pic.sample(self.broad, X, Y)
        z = z + np.clip(DETAIL[0] * fine, -DETAIL[1], DETAIL[1]) * smoothstep(1.0, 3.0, z) * (R < JAW_TOP)
        # The brows over the dome, the pads over the slots.
        bd = self.brow_region.depth(X, Y)
        base = np.maximum(self.dome(X, Y, np.maximum(d, 0.0)) - 0.6, BROW_BASE * (R > 30.0) * smoothstep(29.0, 33.0, R))
        brow = np.where(bd > -0.2, base + BROW_T * round_rise(bd + 0.2, BROW_ROLL), 0.0)
        z = np.where(bd > -0.2, np.maximum(z, brow), z)
        pd = self.pad_region.depth(X, Y)
        pad = np.where(pd > -0.2, SLOT_FLOOR + PAD_T * round_rise(pd + 0.2, 1.4), 0.0)
        z = np.maximum(z, pad)
        return np.where(d > 0, np.maximum(z, 0.0), 0.0)

    def cells(self, X, Y):
        return self.region.inside(X, Y)

    def top(self, X, Y):
        """The head's top with its solids (the knob, the bulbs) over the plane: what DREAD-NOT lays its parts over."""
        X, Y = np.asarray(X, float), np.asarray(Y, float)
        z = self.heights(X, Y)
        C, R = CR(X, Y)
        (kc, kr), (rx, ry, rz), kz = KNOB
        q = ((C - kc) / rx) ** 2 + ((R - kr) / ry) ** 2
        z = np.maximum(z, np.where(q < 1.0, kz + rz * np.sqrt(np.clip(1.0 - q, 0.0, 1.0)), 0.0))
        for bc, br, brx, bry, _t in BULBS:
            x, y = XY(bc, br)
            surface = float(self.jaw(np.array([x]), np.array([y]))[0])
            q = ((C - bc) / brx) ** 2 + ((R - br) / bry) ** 2
            z = np.maximum(z, np.where(q < 1.0, surface - BULB_SINK + SOCKET[1] * 0.5 +
                                       BULB_RZ * np.sqrt(np.clip(1.0 - q, 0.0, 1.0)), 0.0))
        return z


def zones(pic, head):
    a = pic.a
    own = a >= 0
    rows = np.arange(pic.h)[:, None] * np.ones((1, pic.w))
    grey = own & (a >> 4 == 0)
    slot = grey & (rows >= 37) & (rows < 47)
    return [Zone("grey", grey, GREY, FINISH["grey"]),
            Zone("red", head.red, RED, FINISH["red"], sigma=0.7),
            Zone("pipe", slot, PIPE, FINISH["pipe"], sigma=0.6, lift=0.6, comp=1.2, pick=False),
            Zone("knob", grey, GREY, FINISH["knob"], sigma=0.6, lift=1.6, comp=2.4, pick=False),
            Zone("dark", grey, [0x01, 0x02], FINISH["dark"], lift=0.0, comp=0.0, pick=False)]


def plate_keys(head, painter):
    def keys(obj, kinds, wall_z):
        centres, normals = nk.face_data(obj)
        X, Y = centres[:, 0], centres[:, 1]
        C, R = CR(X, Y)
        bd = head.brow_region.depth(X, Y)
        pd = head.pad_region.depth(X, Y)
        post = head.post_amount(X, Y)
        z = centres[:, 2]
        zone_names = []
        for i in range(len(X)):
            if kinds[i] != 0:
                zone_names.append("dark")
            elif bd[i] > 0.0 or pd[i] > 0.0 or (post[i] > 0.5 and SLOT_ROWS[0] < R[i] and z[i] > SLOT_FLOOR + 1.0):
                zone_names.append("red")
            elif SLOT_ROWS[0] < R[i] < SLOT_ROWS[1] and z[i] < SLOT_FLOOR + 0.6:
                zone_names.append("dark")
            else:
                zone_names.append("grey")
        out = painter.keys(obj, zones=zone_names)
        return [("dark", 0x01) if kinds[i] != 0 else key for i, key in enumerate(out)]
    return keys


def solids(head, painter):
    """The knob, the pipes and the bulbs, painted."""
    out = []
    (kc, kr), (rx, ry, rz), kz = KNOB
    x, y = XY(kc, kr)
    knob = nk.ellipsoid("knob", (x, y, kz), (rx, ry, rz), count=14, around=36, cut_below=SLOT_FLOOR - 0.5)
    nk.assign(knob, painter.keys(knob, zone="knob"), painter)
    out.append(knob)
    collar = nk.lathe_axis("knob_collar", [(-0.5, rx + 0.35), (-0.25, rx + 0.75), (0.25, rx + 0.75), (0.5, rx + 0.35)],
                           (x, y, kz - 1.6), (0, 0, 1), around=36)
    nk.assign(collar, painter.keys(collar, zone="pipe", offset=1.0), painter)
    out.append(collar)
    for side in (-1, 1):
        for i, (c0, c1, r, rad) in enumerate(PIPES):
            if side > 0:
                c0, c1 = 2 * AXIS_C - c1, 2 * AXIS_C - c0
            x0, y0 = XY(c0, r)
            x1, y1 = XY(c1, r)
            n = 8
            pts = [(x0 + (x1 - x0) * j / n, y0, SLOT_FLOOR + rad * 0.72) for j in range(n + 1)]
            pipe = nk.loft_path("pipe%d_%d" % (side, i), pts, [rad] * (n + 1), around=18, squash=0.92)
            nk.assign(pipe, painter.keys(pipe, zone="pipe"), painter)
            out.append(pipe)
            # A ring round each pipe near its inner end.
            cring = c1 - 3.2 if side < 0 else c0 + 3.2
            xr, _ = XY(cring, r)
            ring = nk.lathe_axis("pipe_ring%d_%d" % (side, i), [(-0.45, rad + 0.05), (-0.25, rad + 0.32),
                                                               (0.25, rad + 0.32), (0.45, rad + 0.05)],
                                 (xr, y0, SLOT_FLOOR + rad * 0.72), (1, 0, 0), around=18, squash=0.92)
            nk.assign(ring, painter.keys(ring, zone="knob", offset=-1.0), painter)
            out.append(ring)
    for i, (bc, br, rx, ry, tilt) in enumerate(BULBS):
        x, y = XY(bc, br)
        surface = float(head.jaw(np.array([x]), np.array([y]))[0])
        bulb = nk.ellipsoid("bulb%d" % i, (x, y, surface - BULB_SINK + SOCKET[1] * 0.5), (rx, ry, BULB_RZ), count=12,
                            around=32, angle=tilt, cut_below=surface - SOCKET[1] - 0.6)
        nk.assign(bulb, painter.keys(bulb, zone="red", offset=0.4), painter)
        out.append(bulb)
    return out


def build_all(options):
    pic = picture()
    head = Head(pic)
    plate = nk.gw.Plate((LEFT, LEFT + W, TOP - H, TOP), head.heights, cells=head.cells)
    painter = Painter(pic, zones(pic, head), "dome_head")
    parts = solids(head, painter)
    for p in parts:
        p.hide_render = True
    return pic, head, plate, painter, parts


def build():
    options = k.args()
    out = mk.outdir(options)
    only = set(options["only"].split(",")) if "only" in options else None
    k.reset()
    pic, head, plate, painter, parts = build_all(options)
    keys = plate_keys(head, painter)
    for sprite, ((c0, r0), keep) in PIECES.items():
        name = "dome_head_%d" % sprite
        if only is not None and name not in only:
            continue
        box = nk.own_box(pic, c0, r0, keep)
        owns = nk.box_owner(box)
        pieces = nk.piece_parts(plate, keys, parts, box, owns, name, painter, ("dark", 0x01))
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
        origin = (LEFT + c0 + 12, TOP - r0 - 14)
        piece = nk.finish(name, pieces, box, out, options, painter, mask=mask, origin=origin)
        bpy.data.objects.remove(piece)


if __name__ == "__main__":
    build()
