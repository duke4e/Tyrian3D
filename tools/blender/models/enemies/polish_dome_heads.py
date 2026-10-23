"""The armoured head of UNDERDELI, DREAD-NOT, GRAVITRON (on the ground) and LAVA RUN (in the sky): sheet 9 sprites
10 12 / 28 32 / 47 49 51 / 85 87 89 (2x2 each), one 72 x 84 picture; rebuilt as a hard-surface machine (2026-10-23,
round 38: the quality redo). It replaces round 36's heightfield of the whole picture painted by its pixels (itself
replacing wave3_aj_head.py).

Where the levels put it (the enemy events): ten armoured pieces (armour 255, never destroyed) as the sheet lays them
out, 85 87 89 at (x, y), (x + 24, y), (x + 48, y), 47 49 51 28 pixels above them, 28 and 32 at (x, y - 42) and
(x + 48, y - 42), 10 and 12 at (x + 12, y - 56) and (x + 36, y - 56): episode 4's enemies 309-318 (336, 87 again, for
310 in LAVA RUN), UNDERDELI t4600 and t9600 and DREAD-NOT t100 on the ground (event 6), LAVA RUN t2880 in the sky
(event 15), GRAVITRON (episode 6) t6000 on the ground (its enemies 1665-1669 are 49 51 85 87 47 again; episode 6's
composer brings only the head there, none of DREAD-NOT's other parts). One frame each, no damaged look (dgr 0), nothing
launched (313's launch, enemy 337, needs a launch frequency no event gives it). The sprites overlap: 10 and 28, 12 and
32 share a tile; 28 and 32 reach into 47 and 51's rows; each region is kept by one piece: 10 and 12 the dome's top
(columns 12-59, rows 0-27), 28 and 32 only its sides (columns 0-11 and 60-71 of rows 14-27), the others their whole
boxes. No other sprite of any sheet is these pixels mirrored, turned or in other ramps (the head is symmetric about the
middle of column 35 in outline, 99.5 %, but lit from the upper left); no other enemy shows them: built symmetric.
What stands on it: UNDERDELI puts its lilac capsule (9 123, polish_deli_capsule.py) on the jaw's middle (columns 23-46,
rows 57-84) and, a tick before the head, the pulsing blob (5 121, blob_big, 10.9 pixels tall, its bottom lifted to 0.3)
that fires its shots under the dome's middle (columns 25-47, rows 17-39): the dome stands over it there (12 and more,
the knob and the brows' inner ends beside it), as the sprites cover it. DREAD-NOT lays its shoulders over the dome and
its bladed shell over the jaw, its anchors beside it, its cannons under its sides (polish_dread_parts.py builds them
over this head: Head).

As the sprites and their 4x upscales draw it (the picture's columns and rows; symmetric about the middle of column 35,
x = -0.5; lit from the upper left): a dome of grey armour (rows 8-36) with a raised seam down its middle to a steel
knob (columns 28-42 of rows 36-48), an oval boss on its crown and the seam's arms out to its sides, an inset panel on
each side of the seam; over each side a thick glossy red brow (ramp 4, columns 3-30 and 41-67 of rows 24-43), its
upper end swelling, its outer end curling down, a dark line down beside the knob from its inner end; under the brows dark
slots with two black pipes each (rows 38-41 and 43-46) and a small red pad (columns 8-16 and 54-62 of rows 42-46);
below them the broad jaw plate (rows 47-82): its top edge rolled into a lip, a ridge down its middle, four glossy red
bulbs in dark sockets in a V (columns 10-18 and 52-60 of rows 55-65, 22-30 and 40-48 of rows 61-72), its lower edge in
two lobes either side of a notch.

Built as such a machine, from separate solids (polish_dread_kit.py), each in one palette material from the sprite's
own ramps, its shading left to the geometry and the game's light: the dome a shell over the outline of the sprite's
pixels above the jaw (a crown rolling over at its rim, the inset panels sunk into it with dark seams round them
(PANEL_GROOVE), as the sprite's panel lines, the slots carved to SLOT_Z under the brows); the seam, its boss and arms
raised ribs on it; the brows thick red pads over their pixels' outlines (the sprite's darkest red, its outline and
the line down beside the knob, left out), standing BROW_T over the dome, rounded over BROW_R, the upper end swelling
(HUMP); the pads, the pipes (glossy dark tubes, ringed), the knob (a steel ball on a collar ring); the jaw a plate over
its pixels' outline, crowned (JAW_Z), its rim rolled up along its top edge and sides (LIP), a hollow between its lobes
over the notch (THROAT), holes where the sockets are; the ridge a raised strip down its middle, the sockets dark wells,
the bulbs glossy red ellipsoids glowing a little in them. Every outline smooth (the pixel masks' outlines traced
through their boundary edges' midpoints and smoothed; hand-drawn ones rounded). Materials: armour 0x08 (metallic 0.3),
dark 0x03 (the slots, sockets, seams and cuts), the pipes 0x05 (glossy), steel 0x09 (the knob, the rings), red 0x47
(the brows, the pads; emission 0.05), the bulbs 0x48 (emission 0.16), the red parts' insides 0x43. Heights: z 0 (the
base, on the terrain) to 15.9 (the brows' upper ends; the knob 15.0, the dome's crown 13, the jaw 5.4-10.6): low enough
for the sky (under background 3) and for what DREAD-NOT lays over it. UNDERDELI's blob stays hidden under the dome in
all three of its frames with more than a pixel to spare (raised 1.5 it first shows through the inset panels).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera (z 0: the base).
The whole's origin is the picture's middle (column 36, row 42): column c is x = c + 0.5 - 36, row r is y = 41.5 - r; a
piece whose sprite's top left pixel is (c0, r0) has its origin at (c0 - 24, 28 - r0) (models.cfg origin).

models.cfg: unchanged (the ten model lines dome_head_<sprite> enemies/dome_head_<sprite>.glb origin; the sprite lines
with height=-4: on the terrain, in LAVA RUN's sky 4 pixels lower, under background 3).

Replaces round 36's polish_dome_heads.py (this file, rewritten: nothing else to remove). polish_deli_capsule.py reads
Head(picture()).top() (the jaw under the capsule) and LEFT, TOP; polish_dread_parts.py builds over Head.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each piece's outline as the
camera sees it against its sprite's own pixels), --preview <prefix>, --only <name,...>.
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
import polish_dread_kit as dk  # noqa: E402

LEFT, TOP = -36.0, 42.0
W, H = 72, 84
ROW0 = 8                          # the art below starts at the picture's row 8 (rows 0-7 and 83 are empty)
AXIS = -0.5                       # the mirror line: the middle of column 35
MID_C = 35.5                      # its column

MATS = {   # palette index, metallic, roughness, emission (in its own colour)
    "armour": (0x08, 0.3, 0.32, 0.0),     # the painted steel of the dome, its ribs, the jaw, its lip and ridge
    "dark": (0x03, 0.3, 0.5, 0.0),        # the slots' floor, the sockets; the cuts' insides
    "pipe": (0x05, 0.6, 0.12, 0.0),       # the black pipes
    "steel": (0x09, 0.6, 0.2, 0.0),       # the knob and the rings
    "red": (0x47, 0.12, 0.13, 0.05),      # the brows and the pads
    "redcut": (0x43, 0.1, 0.4, 0.0),      # their insides
    "bulb": (0x48, 0.05, 0.14, 0.16),     # the red glass bulbs
}

# --- The dome (picture columns C and rows R, continuous: pixel c spans C c .. c + 1) ------------------------------------
DOME_C = (35.5, 29.0)             # the crown's middle
DOME_R = (33.0, 22.0, 34.0)       # its radii: across, up the screen, down
DOME_Z = (3.2, 13.0)              # its height at its rim and at its middle
DOME_EDGE = (1.2, 2.4)            # its outline's height, how far in it rolls up to the crown
PANEL = ((26.4, 22.5), (4.4, 5.2, 2.7), 0.5)     # the inset panel: middle, half width, half height, corner; its depth
PANEL_GROOVE = 0.24               # the dark seam round it: half its width
SLOT_Z = 3.4                      # the slots' floor
SLOT_ROWS = (36.4, 37.8)          # the slots' upper edge (under the brows), carved from to
RIB_UP = (0.35, 0.8, 1.0)         # the seam's ribs: how high their edge, how much more their crest, its rounding
STEM = (33.4, (19.0, 36.8))       # the seam's stem: its left edge (its right one mirrored), its rows
BOSS = ((35.5, 15.2), (5.4, 3.8), (0.5, 1.1, 1.6))   # the oval boss on the crown: middle, radii; its rim, top, rounding
ARM = [(30.6, 14.6, 1.25), (27.0, 13.2, 1.15), (23.0, 12.3, 1.0), (20.6, 12.2, 0.9)]   # the seam's left arm (column, row,
                                  # half width); the right one mirrored

# --- The brows, the pads, the pipes, the knob ---------------------------------------------------------------------------
BROW_T, BROW_R = 3.3, 3.2         # the brows stand this far over the dome, round over this
BROW_FALL = 0.55                  # below row 36 (their curled outer end, their hanging inner end) they fall per row
HUMP = ((14.6, 26.4), (5.8, 4.4), 1.6)           # the swelling upper end: middle, radii, how much thicker
PAD = (2.1, 1.5)                  # the red pads: how high over the slots' floor, their rounding
PIPES = [((8.0, 28.0, 39.7), 2.1), ((16.6, 28.6, 44.9), 1.7)]    # (from column, to column, row), radius: the left slot's
RING = (3.4, 0.5, 0.32)           # a ring on each pipe this far from its inner end: half width, how far it stands out
KNOB = ((35.5, 41.8), (7.1, 6.3, 5.6), 9.4)      # the knob: middle, radii, its middle's height
COLLAR = (7.5, 5.6, (0.75, 0.9))  # the knob's collar ring: radius, height, its section's half height and thickness

# --- The jaw ------------------------------------------------------------------------------------------------------------
JAW_Z = (5.4, 8.8)                # the jaw plate's height at its sides and in its middle
JAW_FALL = 0.035                  # falling this much a row below row 56
JAW_EDGE = (2.0, 1.7)             # its outline's height, how far in it rounds up
LIP = ([(29.6, 50.6), (24.6, 49.6), (19.0, 49.1), (13.0, 49.0), (8.4, 49.3), (5.3, 50.3), (3.1, 52.1), (2.1, 54.6),
        (2.0, 58.0), (2.3, 63.0), (3.1, 66.8), (4.4, 69.6)], 1.75, 1.9)   # its rolled rim: path (left half), height,
                                  # half width
RIDGE = ([(30.8, 50.2), (31.6, 56.0), (31.6, 68.0), (32.3, 71.6), (33.8, 73.6), (35.5, 74.2)], (0.35, 1.1, 1.1))   # the ridge (left
                                  # half of its outline; rim, crest, rounding)
THROAT = ((35.5, 76.2), (5.2, 4.6), 2.6)        # the hollow between the lobes above the notch: middle, radii, depth
BULBS = [(14.6, 60.6, 4.6, 5.8, 10.0), (26.1, 66.8, 4.6, 6.2, 12.0)]   # (column, row, radius across, along, tilt): the
                                  # left ones; the right ones mirrored
BULB = (3.3, 1.3, 0.85)           # the bulbs' half height, how far their middle lies under the jaw's surface; how far the
                                  # sockets reach round them

# The pieces: sprite -> (top left pixel of its box, the part of the picture it keeps: columns c0 c1, rows r0 r1).
PIECES = {10: ((12, 0), (12, 36, 0, 28)), 12: ((36, 0), (36, 60, 0, 28)),
          28: ((0, 14), (0, 12, 14, 28)), 32: ((48, 14), (60, 72, 14, 28)),
          47: ((0, 28), None), 49: ((24, 28), None), 51: ((48, 28), None),
          85: ((0, 56), None), 87: ((24, 56), None), 89: ((48, 56), None)}

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
    """The head's pixels: an index array (84 rows, 72 columns; -1 empty)."""
    return dk.parse_art(HEAD_ART, W, H, ROW0)


def P(c, r):
    return (c + LEFT, TOP - r)


def CR(x, y):
    return x - LEFT, TOP - y


def materials():
    return dk.materials("dome_head", MATS)


# --- Heights ------------------------------------------------------------------------------------------------------------

def crown(x, y):
    """The dome's crown over the plane (no rim)."""
    c, r = CR(x, y)
    cc, rc = DOME_C
    rx, ry_up, ry_down = DOME_R
    ry = ry_up if r < rc else ry_down
    q = 1.0 - ((c - cc) / rx) ** 2 - ((r - rc) / ry) ** 2
    return DOME_Z[0] + (DOME_Z[1] - DOME_Z[0]) * math.sqrt(max(q, 0.0))


def slot_amount(x, y):
    c, r = CR(x, y)
    return dk.sstep(SLOT_ROWS[0], SLOT_ROWS[1], r)


def panel_sd(x, y):
    """The signed distance to the left or right inset panel's outline (negative inside)."""
    c, r = CR(x, y)
    (pc, pr), (hw, hh, rad), _ = PANEL
    u = abs(c - MID_C) - (MID_C - pc)
    return mk.rounded_rect_distance(u, r - pr, hw, hh, rad)


def dome_top(x, y, d):
    e, roll = DOME_EDGE
    z = e + (crown(x, y) - e) * dk.rounded(d, roll)
    # the inset panels, sunk with a crisp step
    s = panel_sd(x, y)
    z -= PANEL[2] * dk.sstep(0.2, -0.2, s)
    # the slots under the brows
    a = slot_amount(x, y)
    return z + (min(z, SLOT_Z) - z) * a


def brow_base(x, y):
    c, r = CR(x, y)
    base = crown(*P(c, min(r, 36.0)))
    return base - BROW_FALL * max(0.0, r - 36.0)


def brow_top(x, y, d):
    c, r = CR(x, y)
    (hc, hr), (hrx, hry), hz = HUMP
    u = abs(c - MID_C) - (MID_C - hc)
    q = max(0.0, 1.0 - (u / hrx) ** 2 - ((r - hr) / hry) ** 2)
    t = 0.45 + (BROW_T - 0.45) * dk.rounded(d, BROW_R)
    return brow_base(x, y) + t + hz * q * dk.rounded(d, BROW_R * 1.5)


def jaw_z(x, y):
    c, r = CR(x, y)
    u = min(1.0, abs(c - MID_C) / 36.0)
    return JAW_Z[0] + (JAW_Z[1] - JAW_Z[0]) * (1.0 - u ** 1.6) - JAW_FALL * max(0.0, r - 56.0)


_LIP_PATH = None


def lip_bump(x, y):
    """The rolled rim along the jaw's top edge and sides: how much it raises the plate."""
    global _LIP_PATH
    path, height, half = LIP
    if _LIP_PATH is None:
        _LIP_PATH = [P(c, r) for c, r in mk.chaikin(path, 2, closed=False)]
    c, r = CR(x, y)
    fx, fy = P(MID_C - abs(c - MID_C), r)            # folded onto the left half
    best = 1e9
    for (ax, ay), (bx, by) in zip(_LIP_PATH, _LIP_PATH[1:]):
        ex, ey = bx - ax, by - ay
        t = max(0.0, min(1.0, ((fx - ax) * ex + (fy - ay) * ey) / (ex * ex + ey * ey)))
        best = min(best, math.hypot(fx - ax - t * ex, fy - ay - t * ey))
    s = best / half
    return height * max(0.0, 1.0 - s * s) ** 1.5


def throat(x, y):
    """The hollow between the jaw's lobes above the notch: how deep."""
    c, r = CR(x, y)
    (tc, tr), (trx, try_), depth = THROAT
    q = ((c - tc) / trx) ** 2 + ((r - tr) / try_) ** 2
    return depth * max(0.0, 1.0 - q) ** 1.5


def jaw_top(x, y, d):
    e, roll = JAW_EDGE
    return e + (jaw_z(x, y) + lip_bump(x, y) - throat(x, y) - e) * dk.rounded(d, roll)


# --- The parts ------------------------------------------------------------------------------------------------------------

class Outlines:
    """The parts' outlines in model coordinates (from the pixels where the sprite draws a part's own outline)."""

    def __init__(self):
        a = picture()
        own = a >= 0
        rows = np.arange(H)[:, None] * np.ones((1, W), int)
        cols = np.ones((H, 1), int) * np.arange(W)[None, :]
        red = own & (a >> 4 == 4)
        left = cols < MID_C
        self.art = a
        stray = (rows == 12) & (cols <= 21)          # two outline pixels standing off the dome's edge
        self.dome = dk.mask_outline(own & (rows <= 47) & ~stray, LEFT, TOP, sigma=1.8)
        self.jaw = dk.mask_outline(own & (rows >= 47), LEFT, TOP, sigma=1.8)
        pad = red & (rows >= 41) & (rows <= 47) & (cols <= 18) & left
        brow = red & left & ~pad & (rows <= 41) & ((rows <= 36) | (cols <= 12))
        self.brow = dk.mask_outline(brow, LEFT, TOP, sigma=1.1)
        self.pad = dk.mask_outline(pad, LEFT, TOP, sigma=1.0)


def bulb_list():
    """All four bulbs (model x, y, radii, tilt)."""
    out = []
    for c, r, rx, ry, tilt in BULBS:
        x, y = P(c, r)
        out.append((x, y, rx, ry, tilt))
        out.append((2 * AXIS - x, y, rx, ry, -tilt))
    return out


def dome(m, ol):
    groove = PANEL_GROOVE

    def paint(x, y, d):
        return "dark" if slot_amount(x, y) > 0.5 or abs(panel_sd(x, y)) < groove else "top"
    shell = dk.plate("dome_shell", ol.dome, dome_top, m["armour"], side=m["dark"], mats={"dark": m["dark"]},
                     paint=paint, borders=[(lambda x, y, d: slot_amount(x, y), 0.5),
                                           (lambda x, y, d: -panel_sd(x, y), -groove),
                                           (lambda x, y, d: -panel_sd(x, y), groove)],
                     bottom=0.0, spacing=0.55, band=2.6, smooth_angle=55.0)
    parts = [shell]
    # the seam's stem
    c0, (r0, r1) = STEM
    stem_poly = dk.rounded_poly([(c0, r1), (c0, r0 + 1.0), (c0 + 0.6, r0), (2 * MID_C - c0 - 0.6, r0),
                                 (2 * MID_C - c0, r0 + 1.0), (2 * MID_C - c0, r1)], LEFT, TOP, 1)
    up, crest, rnd = RIB_UP

    def rib_top(x, y, d):
        return crown(x, y) + up + crest * dk.rounded(d, rnd)
    parts.append(dk.plate("dome_stem", [stem_poly], rib_top, m["armour"], bottom=1.0, spacing=0.32, band=1.2,
                          smooth_angle=60.0))
    # the arms out to the dome's sides
    for side in (-1, 1):
        pts = [P(c if side < 0 else 2 * MID_C - c, r) for c, r, _ in ARM]
        hw = [w for _, _, w in ARM]
        edge_a, edge_b = [], []
        for i, (x, y) in enumerate(pts):
            ax, ay = pts[max(i - 1, 0)]
            bx, by = pts[min(i + 1, len(pts) - 1)]
            dx, dy = bx - ax, by - ay
            ln = math.hypot(dx, dy)
            nx, ny = -dy / ln, dx / ln
            edge_a.append((x + nx * hw[i], y + ny * hw[i]))
            edge_b.append((x - nx * hw[i], y - ny * hw[i]))
        poly = mk.chaikin(edge_a + list(reversed(edge_b)), 1, closed=True)
        parts.append(dk.plate("dome_arm%d" % side, [poly], rib_top, m["armour"], bottom=1.0, spacing=0.25,
                              smooth_angle=60.0))
    # the oval boss on the crown
    (bc, br), (brx, bry), (brim, btop, brnd) = BOSS
    bx, by = P(bc, br)

    def boss_top(x, y, d):
        return crown(x, y) + brim + btop * dk.rounded(d, brnd)
    parts.append(dk.plate("dome_boss", [dk.ellipse_poly(bx, by, brx, bry, segments=48)], boss_top, m["armour"],
                          bottom=1.0, spacing=0.4))
    return parts


def brows(m, ol):
    parts = []
    for i, poly in enumerate(ol.brow):
        parts.append(dk.plate("brow%d" % i, [poly], brow_top, m["red"], bottom=1.0, spacing=0.4, band=2.2,
                              smooth_angle=50.0))

    def pad_top(x, y, d):
        return SLOT_Z + 0.4 + PAD[0] * dk.rounded(d, PAD[1])
    for i, poly in enumerate(ol.pad):
        parts.append(dk.plate("pad%d" % i, [poly], pad_top, m["red"], bottom=SLOT_Z - 1.0, spacing=0.35,
                              smooth_angle=60.0))
    return parts


def pipes(m):
    parts = []
    for i, ((c0, c1, r), rad) in enumerate(PIPES):
        x0, y = P(c0, r)
        x1, _ = P(c1, r)
        z = SLOT_Z + rad * 0.8
        n = 10
        pts = [(x0 + (x1 - x0) * j / n, y, z) for j in range(n + 1)]
        pipe = dk.tube_path("pipe%d" % i, pts, rad, m["pipe"], segments=16, squash=0.92)
        k.smooth(pipe, 60)
        parts.append(pipe)
        half, out, _ = RING
        xr = x1 - RING[0]
        ring = dk.turned("pipe_ring%d" % i, [(-half, rad + 0.02), (-half * 0.6, rad + out), (half * 0.6, rad + out),
                                             (half, rad + 0.02)], (xr, y, z), (1, 0, 0), m["steel"], segments=20,
                         squash=0.92)
        k.smooth(ring, 50)
        parts.append(ring)
    return parts


def knob(m):
    (kc, kr), radii, kz = KNOB
    x, y = P(kc, kr)
    ball = dk.ball("knob", (x, y, kz), radii, m["steel"], segments=28, rings=14)
    rad, z, (hh, th) = COLLAR
    collar = dk.turned("knob_collar", [(-hh, rad - th), (-hh * 0.5, rad), (hh * 0.5, rad), (hh, rad - th)],
                       (x, y, z), (0, 0, 1), m["steel"], segments=40)
    k.smooth(collar, 50)
    return [ball, collar]


def jaw(m, ol):
    holes = []
    sockets = []
    bulbs = []
    reach = BULB[2]
    for i, (x, y, rx, ry, tilt) in enumerate(bulb_list()):
        holes.append(dk.ellipse_poly(x, y, rx + reach, ry + reach, tilt, segments=40))
        z = jaw_z(x, y)
        sockets.append(mk.prism("socket%d" % i, dk.ellipse_poly(x, y, rx + reach + 0.05, ry + reach + 0.05, tilt, 40),
                                0.0, z - 2.2, m["dark"]))
        bulbs.append(dk.ball("bulb%d" % i, (x, y, z - BULB[1]), (rx, ry, BULB[0]), m["bulb"], segments=28, rings=14,
                             angle=tilt))
    plate = dk.plate("jaw", ol.jaw + holes, jaw_top, m["armour"], side=m["dark"], bottom=0.0, spacing=0.55, band=3.4,
                     smooth_angle=70.0)
    parts = [plate] + sockets + bulbs
    # the ridge down its middle
    half, (rim, crest, rnd) = RIDGE
    poly = dk.rounded_poly(half + [(2 * MID_C - c, r) for c, r in reversed(half[:-1])], LEFT, TOP, 2)

    def ridge_top(x, y, d):
        return jaw_z(x, y) + rim + crest * dk.rounded(d, rnd)
    parts.append(dk.plate("ridge", [poly], ridge_top, m["armour"], bottom=1.0, spacing=0.5, band=1.6))
    return parts


def build_head(m):
    """The whole head in the picture's plane (head model coordinates, not sheared)."""
    ol = Outlines()
    whole = dome(m, ol) + jaw(m, ol) + knob(m)
    left = brows(m, ol) + pipes(m)
    whole += left + dk.mirror(left, AXIS)
    for obj in whole:
        mk.apply(obj)
    bpy.context.view_layer.update()
    return whole


class Head:
    """The head's top over the plane, its solids included, as polish_deli_capsule.py and polish_dread_parts.py read
    it: the head built once (its solids left in the scene, hidden from renders), cast straight down onto."""

    def __init__(self, pic=None):
        self.m = materials()
        self.objects = build_head(self.m)
        for obj in self.objects:
            obj.hide_render = True
        self.surface = dk.Surface(self.objects)

    def top(self, X, Y):
        return self.surface.top(X, Y)


def cap_of(m):
    def cap(src):
        name = src.name
        if name.startswith(("brow", "pad", "bulb")):
            return m["redcut"]
        return m["dark"]
    return cap


def pieces():
    art = picture()
    boxes = {}
    for sprite, ((c0, r0), keep) in PIECES.items():
        kc0, kc1, kr0, kr1 = keep if keep is not None else (c0, c0 + 24, r0, r0 + 28)
        boxes[sprite] = (LEFT + kc0, LEFT + kc1, TOP - kr1, TOP - kr0)
    rects = dk.own_rects(boxes, list(PIECES))
    out = []
    for sprite, ((c0, r0), keep) in PIECES.items():
        out.append(("dome_head_%d" % sprite, rects[sprite], (c0 - 24.0, 28.0 - r0), dk.sprite_mask_of(art, c0, r0, keep)))
    return out


def build():
    options = k.args()
    out = mk.outdir(options)
    only = set(options["only"].split(",")) if "only" in options else None
    k.reset()
    m = materials()
    whole = build_head(m)
    low, high = mk.bounds(whole)
    print("== head: %d triangles, x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f" % (
        mk.triangles(whole), low.x, high.x, low.y, high.y, low.z, high.z))
    if "whole" in options:
        dk.export_whole(whole, options["whole"])
    results = dk.export_pieces(whole, pieces(), cap_of(m), options, out, only, check="check" in options)
    for name, score in results.items():
        if score is not None:
            print("overlap %-16s %.3f" % (name, score))


if __name__ == "__main__":
    build()
