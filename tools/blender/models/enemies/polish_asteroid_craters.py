"""ASTEROIDS' crater (sheet E sprites 51 53 above 55 93, 2x2 each: one 48 x 56 picture; episode 5's enemies 1138-1141,
armour 200 each), the red glass dome round it (E 203 and its frames 205 207; enemy 1142, armour 50) and the blue glass
dome on its far rim (E 243 and its frames 245 167; enemy 1143, armour 100), polished (2026-10-22, round 37; it replaces
wave3_aa.py's crater (a lathed ring painted by the sprite) and its two domes (wave3_aa_kit.dome_parts)). models.cfg:
model tan_crater_tl / _tr / _bl / _br enemies/*.glb origin, model crater_dome origin, model dome_magma (unchanged); new
model dome_magma_205 / _207 enemies/*.glb, model crater_dome_245 / _167 enemies/*.glb origin, frame e 205 dome_magma_205,
frame e 207 dome_magma_207, frame e 245 crater_dome_245, frame e 167 crater_dome_167; the sprite lines stay.

Where the level puts them (ASTEROIDS' events, tools/content/tyrevents.py; the enemy data, tools/content/tyrdata.py): once,
t2800: event 6 puts 1138 (51) at (130, y - 42), 1139 (53) at (154, y - 42), 1140 (55) at (130, y - 14) and 1141 (93) at
(154, y - 14), the picture whole, one link; event 10 puts the blue dome 1143 on ground 2 at (142, y - 48), its middle
over the crater's far rim and the top of its shaft (the picture's (0, 20)), and four red domes 1142 at (142, y - 61),
(142, y + 3), (80, y - 22) and (204, y - 36): above, below, left and right of it, none over the crater. All drift down
together (vy +1). ASTEROIDS' map is space (tile 1, no terrain): the crater floats, the domes with it. The red domes
animate always (203 205 205 205 207 207 207 203 203: the molten swirls in the glass brighten and fade), the blue one
when it fires (243 245 245 245 167 167 167 243 243: its reflections move and brighten); no other enemy shows E 51 53 55
93 203 205 207 243 245 167, so the frames are frame models. The domes are one picture: E 243 is E 205's shades in ramp 3
(97 % of its glass), E 167 nearly 207's (87 %), their pedestals pixel for pixel the same. No other twin. Not in
episode 6.

As the sprites and their 4x upscales draw them (columns and rows): the crater (ramp 1's tans 0x10-0x1e) a broad ring of
rock (columns 1-46, rows 9-45), its shaft (columns 16-31, rows 14-26: dark 0x10-0x15, its far inner wall lit 0x15-0x17)
in its upper half, so that the far rim (rows 9-13) is thin and the near slope (rows 26-45) broad; lit in a band down its
right (0x1c-0x1d), darker at its left, a dark crack across its lower left (rows 30-33). The domes (24 x 28): a glass
dome (columns 1-21, rows 3-21) on a grey pedestal ring that shows round its sides and below it (rows 6-24, 0x04-0x0b); the
red one's glass dark red with molten swirls (0x70-0x7c in 203, two and three shades hotter in 205 and 207), the blue one's
deep blue with pale reflections (0x33-0x3e).

Built for the game's camera in the picture's plane (polish_sheet9_kit: heightfield solids on the sprites' grid, sheared
along the camera's line of sight, painted from the pixels under them): the crater one plate whose top rises from its
outline (round, over CRATER_SLOPE: narrow at its far side, broad at its near side) to its crest (CRATER_H: lower at the
far rim) and falls into the shaft over SHAFT_LIP to its floor (CRATER_FLOOR), the sprite's dark crack creased into it,
its fine shading a little relief (DETAIL); cut on the sprites' grid lines into its four pieces (their walls painted dark,
seen only when a piece is gone). Each dome one plate too: the pedestal a disc PED_H high (rounded over PED_ROLL), the
glass a dome GLASS_H over it (the picture's ellipse), painted by its frame's picture: the glass in its ramp's shades
(LIFT lighter, glowing in the red dome: GLOW_MAGMA, a faint glint on the blue one's lightest), the pedestal in the
sprite's greys. The blue dome stands RIM_Z higher (on the crater's far rim, its plate reaching down to z 0 inside the
shaft), so that the camera sees it over the rim as the game draws ground 2 over the ground. The frames are the same
solids painted with their pictures: the same bounds.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; the crater's picture
column c's middle at x = c + 0.5 - 24, row r's at y = 27.5 - r; a dome's at x = c + 0.5 - 12, y = 13.5 - r. Each piece's
sprite middle is its origin.

Replaces wave3_aa.py (all of it: the crater and the two domes were all it still built: nothing imports it) and its
pixels wave3_aa_art.py (only it read them); wave3_aa_kit.py stays (wave3_ag_kit.py and wave3_ae_kit.py use its piece(),
grid_pieces(), lens(), cone() and ellipsoid_point()) without its dome_parts() and its import of wave3_aa_art.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each piece's outline as the
camera sees it against its sprite), --preview <prefix>, --only <model,...>.
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
from polish_sheet9_kit import Pic, Painter, Zone, Region, parse, blur, fill, smoothstep, round_rise  # noqa: E402

# The pictures' pixels (two hex digits a pixel, '..' none), rows top to bottom: the crater's rows 9-45, the domes' rows
# 3-24 (the rest of each picture is empty).
CRATER_ART = """
....................................141415161717171717161514....................................
..............................151516171818181818181818181817161514..............................
........................141617181818181818171717171717171718181616151413........................
....................15161718181819191919191919181817171616171718181515151412....................
..................15171819191a1a1a1a1a1a1a1a1919191818181818181817161717151414..................
................161818191a1a1b1c1d1d1d1c1615141616141617181816151617181918161414................
..............1618191a1a1a1b1c1d1d1e1713141513151513151615171617181919191918161515..............
............1618191a1a1a1b1c1d1d1e17141214151315151314161517161919171819191918181715............
..........1618191a1a1a1b1b1c1d1d171314121314131414121415151716171a1918191a191918181715..........
........1618191a1a1a1a1b1c1c1d1a12131311131412141412141515161517181a18191a1a191818171715........
......141719191a1a1a1b1b1c1c1d1612121311131312141412141414161517161a18191a1a19191818171714......
......1518191a1a1a1a1b1b1c1c1d1512111211131312131312141414161517151a18191a1a1a191818171716......
....151719191a1a1a1a1b1b1c1c1c1513101211131312131312141414151517151a18191a1c1b19191818171715....
....161819191a1a1a1a1b1b1b1c1c1513101211131311131312141513151415151c18191a1d1b1a191818171715....
....181819191a1a1a1a1b1b1b1b1c19151212111212111313121212121514151c1919191b1d1c1a191818171716....
..16181819191a1a1a1a1b1b1b1b1b1b1815121111111112121213131215151c1a18191a1b1d1c1a19181818171614..
..1618181919191a1a1a1a1b1b1b1a1a16141512111212101010121312151c1a1919191a1b1d1c1a19181818171615..
..171818181919191a1a1a1a1a1919161618171712131413131314161a1b1a191919191a1c1d1b1a19181818171615..
..1718181818191919191919191916151a17171718191919191a1b1b1b19181819191a1b1d1d1a1919181818161614..
....17181818181818181818181816161a17171717171818181817171818181819191a1c1d1c1a1918181818161514..
....161818181818171717171715151917171717171718181817161617181819191a1b1d1d1b191918181818161513..
....1518181817171716161615141817161616171717181817161516171819191a1a1c1d1b1a191818181918151513..
......181816141716161515131716161616161717171818171616171819191a1a1b1d1b1a191918181819181514....
......1716131414161615141516141516161617171818181717171819191a1a1b1d1b1a19191818181919171514....
......15141415151416151416151515161617171818181818181819191a1a1b1c1b1a1919181818181919161413....
........1415161615141417171616161717171818181818181819191a1a1b1c1b1a1919181818181919191513......
........15151616161514161717171717181818181818181819191a1a1b1c1b1a191918181818191a19161413......
..........1516161515161516171718181818181818181919191a1a1b1c1b1a191918181818191a1a181513........
............1516141617161515171818181818181919191a1a1b1b1b1a19191918181818191b1a191513..........
..............1513161616161615161818191919191a1a1b1b1b1a1919191818181718191b1c191613............
................10151616161616151619191a1a1a1a1b1a1a191919181818171718191b1c191613..............
..................131516161616151619191919191919191818181818171717181a1b1b191514................
....................13151616161417181818181818181817171717171718191a1a19181413..................
......................13131515141717171717171717171616171718191a1a1918161413....................
..........................1212141516161616171818191919191919191816151413........................
................................1314141515151515161616161515151414..............................
......................................1313131313141414131313....................................
"""
DOME_203 = """
................71727272727271..................
............7171727373737373727171..............
..........73757775747373747673737271............
......057275797c7b7874717574727272727004........
....057273757b7c7c777372727273737375737105......
..0573737376797c7a73717372747476747173737205....
0505737372747576737271737173757b77717373710405..
0672737471747372737371737373757475727473727105..
0671747272747273717678777372737173727574737205..
067174717172727371797a787371737073727577737106..
0771747472727276737878767371727171727578727106..
0771737372717270737273717371717170737878727206..
0705727371707271727073717171737172757a76710406..
0608717272737373727072727071717273787772700506..
0508057173747372737171727172727476767271040605..
..070a06727474737372727373727474747271040606....
..05060b067274747474747474757473717004050605....
....06070a06717173737373737372717004050605......
......06080a0704717171717171710404060605........
........060708080806060505040405060605..........
..........05060606060606050505050504............
..............050505050505050505................
"""
DOME_205 = """
................74757575757574..................
............7474757676767676757474..............
..........76787a78777676777976767574............
......0575787c7f7e7b77747877757575757304........
....057576787e7f7f7a7675757576767678767405......
..05767676797c7f7d76747675777779777476767505....
0505767675777879767574767476787e7a747676740405..
0675767774777675767674767676787778757776757405..
067477757577757674797b7a7675767476757877767505..
0674777474757576747c7d7b767476737675787a767406..
0774777775757579767b7b79767475747475787b757406..
0774767675747573767576747674747473767b7b757506..
0705757674737574757376747474767475787d79740406..
06087475757676767573757573747475767b7a75730506..
0508057476777675767474757475757779797574040605..
..070a06757777767675757676757777777574040606....
..05060b067577777777777777787776747304050605....
....06070a06747476767676767675747304050605......
......06080a0704747474737373730404060605........
........060708080806060505040405060605..........
..........05060606060606050505050504............
..............050505050505050505................
"""
DOME_207 = """
................78797979797978..................
............7878797a7a7a7a7a797878..............
..........7a7c7e7c7b7a7a7b7d7a7a7978............
......05797c7f7f7f7f7b787c7b797979797704........
....05797a7c7f7f7f7e7a7979797a7a7a7c7a7805......
..057a7a7a7d7f7f7f7a787a797b7b7d7b787a7a7905....
05057a7a797b7c7d7a79787a787a7c7f7e787a7a780405..
06797a7b787b7a797a7a787a7a7a7c7b7c797b7a797805..
06787b79797b797a787d7f7e7a797a787a797c7b7a7905..
06787a787879797a787f7f7f7a787a777a797c7e7a7706..
0778797b7979797d7a7f7f7d7a78797878797c7f797606..
0778787a797879777a797a787a787878777a7f7f797606..
070577797877797879777a7878787a78797c7f7c770406..
06087777797a7a7a79777979777878797a7f7e77740506..
05080576787a7a797a7878797879797b7d7d7975040605..
..070a0678797a7a7a79797a7a797b7b7b7976040606....
..05060b0678797a7b7b7b7b7b7c7b7a787604050605....
....06070a0677767879797a7a7a79777604050605......
......06080a0704757677767674730404060605........
........060708080806060505040405060605..........
..........05060606060606050505050504............
..............050505050505050505................
"""
DOME_243 = """
................34353535353534..................
............3434353636363636353434..............
..........36383a38373636373936363534............
......0535383c3e3e3b37343837353535353304........
....053536383e3e3e3a3635353536363638363405......
..05363636393c3e3d36343635373739373436363505....
0505363635373839363534363436383e3a343636340405..
0635363734373635363634363636383738353736353405..
063437353537353634393b3a3635363436353837363505..
0634373434353536343c3d3b363436333635383a363406..
0734373735353539363b3b39363435343435383b353406..
0734363635343533363536343634343433363b3b353506..
0705353634333534353336343434363435383d39340406..
06083435353636363533353533343435363b3a35330506..
0508053436373635363434353435353739393534040605..
..070a06353737363635353636353737373534040606....
..05060b063537373737373737383736343304050605....
....06070a06343436363636363635343304050605......
......06080a0704343434343434340404060605........
........060708080806060505040405060605..........
..........05060606060606050505050504............
..............050505050505050505................
"""
DOME_245 = """
................37383838383837..................
............3737383939393939383737..............
..........393b3d3b3a39393a3c39393837............
......05383b3f3f3f3e3a373b3a383838383604........
....0538393b3f3f3f3d393838383939393b393705......
..053939393c3f3f3f393739383a3a3c3a3739393805....
05053939383a3b3c3938373937393b3f3d373939370405..
0638393a373a39383939373939393b3a3b383a39383505..
06373a38383a3839373c3e3d3938393739383b3a393705..
06373a3737383839373f3f3e3937393639383b3d393706..
0737393a3838383c393e3e3c3937383737383b3e383706..
0736383938373836393839373937373736393e3e383606..
07053739373638373836393737373937383b3f3c370406..
06083638383939393836383836373738393e3d38360506..
05080536383a3938393737383738383a3c3c3837040605..
..070a0637393a393938383939383a3a3a3837040606....
..05060b0637393a3a3a3a3a3a3b3a39373604050605....
....06070a06363738393939393938373604050605......
......06080a0704363737373736360404060605........
........060708080806060505040405060605..........
..........05060606060606050505050504............
..............050505050505050505................
"""
DOME_167 = """
................38393939393938..................
............3838393a3a3a3a3a393837..............
..........3a3c3e3c3b3a3a3b3d3a3a3938............
......05393c3f3f3f3f3b383c3b393939393704........
....05393a3c3f3f3f3e3a3939393a3a3a3c3a3805......
..053a3a3a3d3f3f3f3a383a393b3b3d3b383a3a3805....
05053a3a393b3c3d3a39383a383a3c3f3e383a3a380405..
06393a3b383b3a393a3a383a3a3a3c3b3c393b3a393605..
06383b39393b393a383d3f3e3a393a383a393c3b3a3705..
06383b383839393a383f3f3f3a383a373a393c3e3a3706..
07383b3b3939393d3a3f3f3d3a38393838393c3f393706..
07373a3a393839373a393a383a383838373a3f3f393506..
0705393a3837393839373a3838383a38393c3f3d380406..
06083739393a3a3a39373939373838393a3f3e39360506..
050805383a3b3a393a3838393839393b3d3d3936040605..
..070a06393b3b3a3a39393a3a393b3b3b3937040606....
..05060b06393b3b3b3b3b3b3b3c3b3a383604050605....
....06070a0637383a3a3a3a3a3a39383604050605......
......06080a0704353536373736360404060605........
........060708080806060505040405060605..........
..........05060606060606050505050504............
..............050505050505050505................
"""

# --- The crater ----------------------------------------------------------------------------------------------------------
CRATER_TOP = 28.0 - 9                 # the art's first row (9) in the picture's plane
CRATER_H = (5.6, 9.4)                 # its crest: at the far rim, at the near slope
CRATER_SLOPE = (2.6, 11.0)            # how far in from its outline it rises to the crest: far, near
CRATER_FLOOR = 0.08                   # the shaft's floor (a share of the crest)
SHAFT_LIP = (-0.5, 2.6)               # the shaft's wall: from this far outside its rim to this far inside
CREASE = 1.1                          # the dark crack's depth
DETAIL = (0.18, 0.45)                 # the fine shading's relief: per shade, its limit
ROCK_LIFT = (0.5, 1.4)                # the rock painted this many shades lighter (and more where the sun misses it)
TANS = [0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e]
CRATER_PIECES = [("tan_crater_tl", 51, (0, 0)), ("tan_crater_tr", 53, (24, 0)), ("tan_crater_bl", 55, (0, 28)),
                 ("tan_crater_br", 93, (24, 28))]

# --- The domes -----------------------------------------------------------------------------------------------------------
DOME_TOP = 14.0 - 3                   # the art's first row (3)
PED = ((-0.5, -1.2), (11.6, 10.2))    # the pedestal disc: middle (x, y), radii
PED_H, PED_ROLL = 3.0, 1.4
GLASS = ((-0.5, 1.5), (10.6, 9.6))    # the glass's ellipse
GLASS_H = 7.5
RIM_Z = 6.5                           # how much higher the blue dome stands (on the crater's far rim)
GREYS = [0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c]
REDS = [0x70, 0x71, 0x72, 0x73, 0x74, 0x75, 0x76, 0x77, 0x78, 0x79, 0x7a, 0x7b, 0x7c, 0x7d, 0x7e]
BLUES = [0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x3a, 0x3b, 0x3c, 0x3d, 0x3e]
GLOW_MAGMA = {0x72: 0.08, 0x73: 0.1, 0x74: 0.14, 0x75: 0.18, 0x76: 0.22, 0x77: 0.28, 0x78: 0.32, 0x79: 0.38,
              0x7a: 0.42, 0x7b: 0.48, 0x7c: 0.54, 0x7d: 0.6, 0x7e: 0.65}
GLOW_BLUE = {0x3d: 0.12, 0x3e: 0.2}
DOMES = [("dome_magma", 203, DOME_203, False), ("dome_magma_205", 205, DOME_205, False),
         ("dome_magma_207", 207, DOME_207, False), ("crater_dome", 243, DOME_243, True),
         ("crater_dome_245", 245, DOME_245, True), ("crater_dome_167", 167, DOME_167, True)]


class Crater:
    def __init__(self):
        self.pic = Pic(parse(CRATER_ART), -24.0, CRATER_TOP)
        a = self.pic.a
        own = a >= 0
        shade = np.where(own, a & 15, 0)
        rows = np.arange(self.pic.h)[:, None] + 9
        cols = np.arange(self.pic.w)[None, :]
        self.own = own
        self.outer = Region(self.pic, own, sigma=0.6)
        hole = own & (shade <= 5) & (rows >= 14) & (rows <= 26) & (cols >= 15) & (cols <= 32)
        hole = nk.erode(nk.dilate(hole, 1), 1)
        self.hole = Region(self.pic, hole, sigma=0.8)
        crack = own & (shade <= 4) & (rows >= 29) & (rows <= 34) & (cols <= 12)
        self.crack = blur(crack.astype(float), 0.5)
        self.soft = blur(fill(shade.astype(float), own), 0.6)
        self.broad = blur(fill(shade.astype(float), own), 2.0)

    def heights(self, X, Y):
        X, Y = np.asarray(X, float), np.asarray(Y, float)
        d = self.outer.depth(X, Y)
        dh = self.hole.depth(X, Y)
        t = smoothstep(16.0, -10.0, Y)
        h = CRATER_H[0] + (CRATER_H[1] - CRATER_H[0]) * t
        w = CRATER_SLOPE[0] + (CRATER_SLOPE[1] - CRATER_SLOPE[0]) * t
        rise = round_rise(np.maximum(d, 0.0), w)
        lip = 1.0 - smoothstep(SHAFT_LIP[0], SHAFT_LIP[1], dh)
        z = h * rise * (CRATER_FLOOR + (1.0 - CRATER_FLOOR) * lip)
        pic = self.pic
        fine = pic.sample(self.soft, X, Y) - pic.sample(self.broad, X, Y)
        z = z + np.clip(DETAIL[0] * fine, -DETAIL[1], DETAIL[1]) * np.clip(z / 3.0, 0.0, 1.0)
        z = z - CREASE * pic.sample(self.crack, X, Y) * np.clip(z / 4.0, 0.0, 1.0)
        return np.where(d > 0, np.maximum(z, 0.05), 0.0)

    def cells(self, X, Y):
        return self.outer.inside(X, Y)


def crater_zones(cr):
    own = cr.own
    return [Zone("rock", own, TANS, (0.05, 0.62), lift=ROCK_LIFT[0], comp=ROCK_LIFT[1]),
            Zone("dark", own, [0x10, 0x11, 0x12], (0.05, 0.8), lift=0.0, comp=0.0, pick=False)]


def crater_keys(cr, painter):
    """The rock painted by the picture; the shaft's floor and the deep part of its walls dark (the picture's darkest),
    the pieces' walls dark."""
    def keys(obj, kinds, wall_z):
        centres, normals = nk.face_data(obj)
        dh = cr.hole.depth(centres[:, 0], centres[:, 1])
        out = painter.keys(obj, zones=["rock"] * len(kinds))
        return [("dark", 0x11) if kinds[i] != 0 else ("dark", 0x10) if dh[i] > SHAFT_LIP[1] - 0.6 else
                ("dark", 0x12) if dh[i] > 0.9 and key[1] > 0x13 else key for i, key in enumerate(out)]
    return keys


def build_crater(options, out, only):
    cr = Crater()
    plate = nk.gw.Plate((-24.0, 24.0, -28.0, 28.0), cr.heights, cells=cr.cells)
    painter = Painter(cr.pic, crater_zones(cr), "crater")
    keys = crater_keys(cr, painter)
    full = Pic(parse(CRATER_ART), -24.0, CRATER_TOP)
    for name, sprite, (c0, r0) in CRATER_PIECES:
        if only and name not in only:
            continue
        box = (-24.0 + c0, -24.0 + c0 + 24, 28.0 - r0 - 28, 28.0 - r0)
        parts = nk.piece_parts(plate, keys, [], box, nk.box_owner(box), name, painter, ("dark", 0x11))
        mask = None
        if "check" in options:
            mask = k.sprite_mask(os.path.join(options["check"], "enemy_E.png"), sprite)
        piece = nk.finish(name, parts, box, out, options, painter, mask=mask)
        bpy.data.objects.remove(piece)


class Dome:
    def __init__(self, art, raised):
        self.pic = Pic(parse(art), -12.0, DOME_TOP)
        a = self.pic.a
        self.own = a >= 0
        self.region = Region(self.pic, self.own, sigma=0.5)
        self.base = RIM_Z if raised else 0.0

    def heights(self, X, Y):
        X, Y = np.asarray(X, float), np.asarray(Y, float)
        d = self.region.depth(X, Y)
        (px, py), (prx, pry) = PED
        qp = ((X - px) / prx) ** 2 + ((Y - py) / pry) ** 2
        ped = PED_H * round_rise(np.maximum(d, 0.0), PED_ROLL)
        (gx, gy), (grx, gry) = GLASS
        qg = ((X - gx) / grx) ** 2 + ((Y - gy) / gry) ** 2
        glass = PED_H * 0.7 + GLASS_H * np.sqrt(np.clip(1.0 - qg, 0.0, 1.0))
        z = np.where(qg < 1.0, np.maximum(ped, glass), ped)
        return np.where(d > 0, self.base + z, 0.0)

    def cells(self, X, Y):
        return self.region.inside(X, Y)


def dome_zones(dome, raised):
    a = dome.pic.a
    own = a >= 0
    if raised:
        glass = Zone("glass", own & (a >> 4 == 3), BLUES, (0.25, 0.08), glow=GLOW_BLUE, sigma=0.55, lift=0.8, comp=1.0)
    else:
        glass = Zone("glass", own & (a >> 4 == 7), REDS, (0.15, 0.12), glow=GLOW_MAGMA, sigma=0.55, lift=0.6, comp=0.6)
    return [glass, Zone("grey", own & (a >> 4 == 0), GREYS, (0.45, 0.35), sigma=0.6),
            Zone("dark", own, [0x02, 0x03], (0.2, 0.7), lift=0.0, comp=0.0, pick=False)]


def dome_keys(dome, painter):
    (gx, gy), (grx, gry) = GLASS

    def keys(obj, kinds, wall_z):
        centres, normals = nk.face_data(obj)
        X, Y = centres[:, 0], centres[:, 1]
        qg = ((X - gx) / grx) ** 2 + ((Y - gy) / gry) ** 2
        zones = ["glass" if qg[i] < 0.97 else "grey" for i in range(len(X))]
        out = painter.keys(obj, zones=zones)
        return [("dark", 0x02) if kinds[i] != 0 else key for i, key in enumerate(out)]
    return keys


def build_domes(options, out, only):
    for name, sprite, art, raised in DOMES:
        if only and name not in only:
            continue
        k.reset()
        dome = Dome(art, raised)
        plate = nk.gw.Plate((-12.0, 12.0, -14.0, 14.0), dome.heights, cells=dome.cells)
        painter = Painter(dome.pic, dome_zones(dome, raised), name)
        box = (-12.0, 12.0, -14.0, 14.0)
        parts = nk.piece_parts(plate, dome_keys(dome, painter), [], box, nk.box_owner(box), name, painter,
                               ("dark", 0x02))
        mask = k.sprite_mask(os.path.join(options["check"], "enemy_E.png"), sprite) if "check" in options else None
        piece = nk.finish(name, parts, box, out, options, painter, mask=mask)
        bpy.data.objects.remove(piece)


def build():
    options = k.args()
    out = mk.outdir(options)
    only = set(options["only"].split(",")) if "only" in options else None
    k.reset()
    bpy.context.scene.view_settings.view_transform = "Standard"
    build_crater(options, out, only)
    build_domes(options, out, only)


if __name__ == "__main__":
    build()
