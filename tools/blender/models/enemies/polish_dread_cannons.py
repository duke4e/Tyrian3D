"""The cannons of UNDERDELI and DREAD-NOT on their round turntables (sheet V sprites 14 and 16 side by side, 48 x 28,
the cannon pointing left; 167 and 169 their mirror image, pixel for pixel, pointing right), and the barrel's recoil
when they fire (V 52 for 14, V 207 for 169); polished (2026-10-22, round 36). It replaces wave3_t.py (all of it: its
cannon_whole() and the four models it cut from it, the barrel kept still).

Where the levels put them (episode 4's enemies 321-324 and 450-451): UNDERDELI t4900 in the sky (event 15), the
right-pointing one at the screen's left edge (167 at x 0, 169 at x 24: 321, 322) and the left-pointing one at its right
edge (14 at x 220, 16 at x 242: 323, 324, two pixels closer than the sheet lays them); DREAD-NOT t99 on the ground
with its machine (polish_dread_parts.py): 14 + 16 at (120, -56) and 167 + 169 at (164, -56) over the head's dome, a
second barrel alone (14 at (120, -28), 169 at (188, -28)) by the head's sides, all under the shoulders and the head
(the game draws them first): only the barrels' ends show there. 322, 323, 450 and 451 fire (animate 2): their
animation 169 207 207 207 169 (14 52 52 52 14) slides the barrel back into its band; the frame models
cannon_barrel_52 and cannon_barrel_r_207 do it (no other enemy, launched ones included, shows V 52 or 207). What they
launch (enemies 43 44, x5e 190 152; 452 453, 5 286 267: the white darts) has its models. No damaged look.

As the sprites and their 4x upscales draw it (the 48 x 28 picture of 14 + 16, pointing left; lit from the upper left):
a long round steel barrel (columns 0-27 of rows 4-13: ramp 0) with a dark muzzle ring at its left end and a blue band
(ramps 3 and 8: columns 10-11) a third of the way along; at its right end the breech, a dark blue collar standing across
it (columns 26-30 of rows 1-24, ramp 3); behind it a turned neck and a bright round knob (columns 31-40 of rows 5-13),
the rear block (columns 40-47 of rows 5-17); two swept dark fins, a small one over the barrel's end (columns 17-29 of
rows 0-4) and a big one under it (columns 15-28 of rows 14-26); under it all a round blue-grey turntable (ramp 6,
columns 28-41 of rows 1-25, seen above and below the breech). The recoil frame (52): the barrel's front slid a pixel
into its band.

Built for the game's camera, with polish_sheet9_kit: the turntable, the fins and the rear block one heightfield (a
low disc with a bevelled rim, wedge fins rising from it, a rounded block), the barrel, its band, the collar, the neck
and the knob turned solids; painted by the picture. The right-pointing cannon is the left one mirrored about its
middle (x 0), painted by its own (mirrored) pixels. Heights: z 0 to 10.3 (the barrel's top).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera. The whole's origin
is the picture's middle (column 24, row 14): column c is x = c + 0.5 - 24, row r is y = 13.5 - r; the pieces' origins
(-12, 0) and (12, 0) (models.cfg origin).

models.cfg: the four model and sprite lines stay; new: model cannon_barrel_52 enemies/cannon_barrel_52.glb origin, model
cannon_barrel_r_207 enemies/cannon_barrel_r_207.glb origin, frame v 52 cannon_barrel_52, frame v 207
cannon_barrel_r_207. The sprite lines get height=-4 (on the terrain in DREAD-NOT with the machine; 4 pixels lower in
UNDERDELI's sky).

Replaces wave3_t.py (all of it: delete it) and wave3_t_kit.py (only wave3_t.py imports it: delete it).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each piece's outline as the
camera sees it against its sprite's pixels), --preview <prefix>, --only <name,...>.
"""
import os
import sys

import bpy
import numpy as np
from mathutils import Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
import polish_sheet9_kit as nk  # noqa: E402
from polish_sheet9_kit import Pic, parse, blur, smoothstep, smax, Region, Zone, Painter, round_rise  # noqa: E402

LEFT, TOP = -24.0, 14.0
BARREL = (9.0, 4.55, 5.1)         # the barrel's axis (row), radius, the axis' height
MUZZLE = (0.0, 1.6)               # the muzzle ring: its left end (column), its length
BAND = (9.8, 12.2)                # the blue band (columns)
BARREL_END = 27.0                 # the barrel goes into the collar here
COLLAR = ((26.0, 30.6), (1.2, 24.6), 7.6)        # the breech's collar: columns, rows, height
NECK = ((30.6, 33.6), 3.0)        # the neck (columns), radius
KNOB = ((36.6, 9.0), (3.6, 4.4, 3.7), 5.4)        # the knob: middle, radii, height of its middle
TABLE = ((34.8, 13.0), (12.6, 12.6), 1.7, 0.6)    # the turntable: middle, radii, height, rim bevel
REAR = ((40.0, 47.6), (4.6, 17.6), 6.4, 1.6)      # the rear block: columns, rows, height, rounding
FINS = [([(16.6, 5.0), (20.6, 1.6), (23.0, 0.4), (29.0, 0.4), (29.6, 5.0)], 4.6),
        ([(12.6, 14.0), (30.0, 14.0), (29.4, 25.6), (23.6, 26.4), (21.6, 24.6), (18.6, 21.6), (15.4, 18.4)], 4.4)]
FIN_ROLL = 1.0
RECOIL = 1.0                      # the recoil frames slide the barrel's front this far into its band

GREY = [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e]
BLUE = [0x35, 0x37, 0x39, 0x3a]
LIGHT = [0x84, 0x88, 0x8c, 0x8d]
TABLE_SHADES = [0x63, 0x64, 0x66, 0x67, 0x68]
FINISH = {"grey": (0.55, 0.26), "blue": (0.45, 0.24), "light": (0.4, 0.2), "table": (0.4, 0.3), "dark": (0.3, 0.5)}

CANNON_ART = """
    ..............................................010101010101......................................
    ..........................................01010608070606043a39393939396766......................
    ......................................0101040706060505050339676767676767676664..................
    ..................................0202050706060505050505033967676767676767676663................
    ........010201010101....01010101010102030303030303040405033967676767676767676764..01............
    010102020208030405063637080606060606060606060606050401050339676767676767060706070601010101......
    01070505050a0506070837380a08080808080808080808080706010303036467676739060a0c070a070505050501....
    01090707070c0708090a393a0c0a0a0a0a0a0a0a0a0a0a0a09080107070604030304040a0e0f0a0f0b090909070501..
    010c0707070f0c0d0e0f8d8d0f0d0d0d0c0c0c0c0c0c0b0b0a0901090a0a0a07090a0a0b0e0f090c09080707070601..
    010a0606060d08090a0b88880d0b0b0b0b0b0b0b0b0b0b0b0a0901090c0c0c07090a090b0c0e070b08060505050501..
    01090505050c0708090a383a0c0a0a0a0a0a0a0a0a0a0a0a090801070d0d0d060708090a0a0b060a0504040404040101
    01070404040b0607080937390b0909090909090909090909080701060b0b0b0303040509090a05080404040404040301
    01050101010a0506070837380a0808080808080808080808060601040707070202030405080905070404040404040401
    010301010108030405056637070606060606060606060606040401030404040102646404060703060404040404040301
    010101010106010102036565040404040404040404040404030201010303030163646664030303050303030203030201
    ........0107020202036363030101010101010101010103020201010303030163646667660303040303020202020101
    ........01070202030465650401020202020202020201010202010101010101636466676766646403030101010101..
    ........010804050507383806020705060303030303030201020101010101010264666767676666660401..........
    ........0102010101010101010101020406040404040403030101020164636364666767676767676767............
    ..............................010304070404040404040303020166646466676767676767676767............
    ................................0103050805050505050505050339676767676767676767676766............
    ..................................0103050906050505050505033a676767676767676767676664............
    ....................................0103050a080605050505033a6767676767676767676664..............
    ......................................010204060707060606033a67676767676767676664................
    ........................................01010304050707070583676767676767666664..................
    ............................................010103030303016764646464646464......................
    ................................................010101010101....................................
    ................................................................................................
"""
CANNON_52_ART = """
    ..............................................010101010101......................................
    ..........................................01010608070606043a39393939396766......................
    ......................................0101040706060505050339676767676767676664..................
    ..................................0202050706060505050505033967676767676767676663................
    ......010201010101......01010101010102030303030303040405033967676767676767676764..01............
    ..0101020803040506363737080606060606060606060606050401050339676767676767060706070601010101......
    ..0107050a050607083738380a08080808080808080808080706010303036467676739060a0c070a070505050501....
    ..0109070c0708090a393a3a0c0a0a0a0a0a0a0a0a0a0a0a09080107070604030304040a0e0f0a0f0b090909070501..
    ..010c070f0c0d0e0f8d8d8d0f0d0d0d0c0c0c0c0c0c0b0b0a0901090a0a0a07090a0a0b0e0f090c09080707070601..
    ..010a060d08090a0b8888880d0b0b0b0b0b0b0b0b0b0b0b0a0901090c0c0c07090a090b0c0e070b08060505050501..
    ..0109050c0708090a383a3a0c0a0a0a0a0a0a0a0a0a0a0a090801070d0d0d060708090a0a0b060a0504040404040101
    ..0107040b060708093739390b0909090909090909090909080701060b0b0b0303040509090a05080404040404040301
    ..0105010a050607083738380a0808080808080808080808060601040707070202030405080905070404040404040401
    ..0103010803040505663737070606060606060606060606040401030404040102646404060703060404040404040301
    ..0101010601010203656565040404040404040404040404030201010303030163646664030303050303030203030201
    ......010702020203636363030101010101010101010103020201010303030163646667660303040303020202020101
    ......0107020203046565650401020202020202020201010202010101010101636466676766646403030101010101..
    ......01080405050738383806020705060303030303030201020101010101010264666767676666660401..........
    ......010201010101010101010101020406040404040403030101020164636364666767676767676767............
    ..............................010304070404040404040303020166646466676767676767676767............
    ................................0103050805050505050505050339676767676767676767676766............
    ..................................0103050906050505050505033a676767676767676767676664............
    ....................................0103050a080605050505033a6767676767676767676664..............
    ......................................010204060707060606033a67676767676767676664................
    ........................................01010304050707070583676767676767666664..................
    ............................................010103030303016764646464646464......................
    ................................................010101010101....................................
    ................................................................................................
"""


def picture(text, mirror=False):
    rows = parse(text)
    if mirror:
        rows = [row[::-1] for row in rows]
    return Pic(rows, LEFT, TOP)


def XY(c, r):
    return c + LEFT, TOP - r


class Cannon:
    def __init__(self, pic, mirror=False):
        self.pic, self.mirror = pic, mirror
        self.own = pic.a >= 0
        self.region = Region(pic, self.own, sigma=0.5)
        # (the shapes are the left-pointing cannon's: the mirrored one samples them at -x)
        self.fins = [(Region(pic, nk.polygon_mask(pic, self.cols(poly)) & self.own, sigma=0.5), h) for poly, h in FINS]

    def cols(self, poly):
        return [(48.0 - c, r) for c, r in poly] if self.mirror else poly

    def CR(self, X, Y):
        X = -np.asarray(X, float) if self.mirror else np.asarray(X, float)
        return X - LEFT, TOP - np.asarray(Y, float)

    def heights(self, X, Y):
        X, Y = np.asarray(X, float), np.asarray(Y, float)
        C, R = self.CR(X, Y)
        d = self.region.depth(X, Y)
        (tc, tr), (rx, ry), th, bev = TABLE
        q = np.sqrt(((C - tc) / rx) ** 2 + ((R - tr) / ry) ** 2)
        z = np.where(q < 1.0, th - bev * smoothstep(1.0 - bev / rx, 1.0, q), 0.0)
        (c0, c1), (r0, r1), rh, rr = REAR
        u = np.minimum(C - c0, c1 - C)
        v = np.minimum(R - r0, r1 - R)
        rear = rh * round_rise(np.minimum(u, v), rr) * (u > 0) * (v > 0)
        z = smax(z, rear, 0.5)
        for reg, h in self.fins:
            fd = reg.depth(X, Y)
            z = np.where(fd > -0.2, np.maximum(z, h * round_rise(np.maximum(fd + 0.2, 0.0), FIN_ROLL)), z)
        (cc0, cc1), (cr0, cr1), ch = COLLAR
        u = np.minimum(C - cc0, cc1 - C)
        v = np.minimum(R - cr0, cr1 - R)
        collar = ch * round_rise(np.minimum(u, v * 0.6), 1.2) * (u > 0) * (v > 0)
        z = np.maximum(z, collar)
        z = z * round_rise(d, 0.6)
        return np.where(d > 0, np.maximum(z, 0.0), 0.0)


def zones(pic):
    a = pic.a
    own = a >= 0
    return [Zone("grey", own & (a >> 4 == 0), GREY, FINISH["grey"], lift=1.4),
            Zone("blue", own & (a >> 4 == 3), BLUE, FINISH["blue"], sigma=0.5),
            Zone("light", own & (a >> 4 == 8), LIGHT, FINISH["light"], sigma=0.5, lift=0.5),
            Zone("table", own & (a >> 4 == 6), TABLE_SHADES, FINISH["table"], sigma=0.7),
            Zone("dark", own, [0x01, 0x02], FINISH["dark"], lift=0.0, comp=0.0, pick=False)]


def solids(cannon, painter, recoil):
    """The barrel (its front a tube sliding into the band by `recoil`), the band, the collar's ring, the neck, the
    knob; built pointing left and mirrored for the other cannon."""
    row, rad, zc = BARREL
    out = []

    def axis_point(c):
        x, y = XY(c, row)
        return (x, y, zc)
    m0, ml = MUZZLE
    front0 = m0 + recoil
    front = nk.lathe_axis("barrel_front", [(0.0, rad - 1.1), (0.15, rad - 0.15), (0.6, rad), (ml, rad), (ml + 0.25, rad - 0.3),
                                           (BAND[0] - front0 + 0.6, rad - 0.3)], axis_point(front0), (1, 0, 0), around=28)
    bore = nk.lathe_axis("barrel_bore", [(-0.02, 0.01), (0.0, rad - 1.5), (0.8, rad - 1.5), (0.9, 0.01)],
                         axis_point(front0), (1, 0, 0), around=20)
    band = nk.lathe_axis("barrel_band", [(0.0, rad - 0.1), (0.2, rad + 0.25), (BAND[1] - BAND[0] - 0.2, rad + 0.25),
                                         (BAND[1] - BAND[0], rad - 0.1)], axis_point(BAND[0]), (1, 0, 0), around=28)
    rear = nk.lathe_axis("barrel_rear", [(0.0, rad - 0.15), (BARREL_END - BAND[1] + 0.5, rad - 0.15)],
                         axis_point(BAND[1] - 0.2), (1, 0, 0), around=28)
    (n0, n1), nr = NECK
    neck = nk.lathe_axis("neck", [(0.0, nr + 0.5), (0.6, nr), (n1 - n0 - 0.6, nr - 0.3), (n1 - n0 + 0.4, nr + 0.6)],
                         axis_point(n0), (1, 0, 0), around=24)
    (kc, kr), (krx, kry, krz), kz = KNOB
    kx, ky = XY(kc, kr)
    knob = nk.ellipsoid("knob", (kx, ky, kz), (krx, kry, krz), count=12, around=28, cut_below=0.5)
    parts = [(front, "grey", 1.4), (bore, "dark", 0.0), (band, "blue", 0.0), (rear, "grey", 1.2), (neck, "grey", 0.0),
             (knob, "grey", 2.4)]
    for obj, zone, off in parts:
        if cannon.mirror:
            nk.mirror_x(obj, 0.0)
        if zone == "blue":
            # the band: its blue, its light highlights where the sprite draws them
            centres, normals = nk.face_data(obj)
            near = painter.zone_at(centres[:, 0], centres[:, 1])
            names = ["light" if n == "light" else "blue" for n in near]
            nk.assign(obj, painter.keys(obj, zones=names), painter)
        else:
            nk.assign(obj, painter.keys(obj, zone=zone, offset=off), painter)
        obj.hide_render = True
        out.append(obj)
    return out


def plate_keys(cannon, painter):
    def keys(obj, kinds, wall_z):
        centres, normals = nk.face_data(obj)
        near = painter.zone_at(centres[:, 0], centres[:, 1])
        names = []
        for i in range(len(near)):
            if kinds[i] != 0:
                names.append("dark")
            elif near[i] in ("table", "blue"):
                names.append(near[i])
            else:
                names.append("grey")
        out = painter.keys(obj, zones=names)
        return [("dark", 0x01) if kinds[i] != 0 else key for i, key in enumerate(out)]
    return keys


MODELS = [  # (name, mirrored, recoil frame, the piece's columns in the picture: 0 or 24, the picture)
    ("cannon_barrel", False, False, 0, "base"), ("cannon_breech", False, False, 24, "base"),
    ("cannon_breech_r", True, False, 0, "base"), ("cannon_barrel_r", True, False, 24, "base"),
    ("cannon_barrel_52", False, True, 0, "recoil"), ("cannon_barrel_r_207", True, True, 24, "recoil")]


def build():
    options = k.args()
    out = mk.outdir(options)
    only = set(options["only"].split(",")) if "only" in options else None
    for mirror in (False, True):
        for frame in ("base", "recoil"):
            todo = [m for m in MODELS if m[1] == mirror and m[4] == frame and (only is None or m[0] in only)]
            if not todo:
                continue
            k.reset()
            pic = picture(CANNON_ART if frame == "base" else CANNON_52_ART, mirror)
            cannon = Cannon(pic, mirror)
            plate = nk.gw.Plate((-24.0, 24.0, -14.0, 14.0), cannon.heights,
                                cells=lambda X, Y: cannon.region.inside(X, Y) & (cannon.heights(X, Y) > 0.05))
            painter = Painter(pic, zones(pic), "cannon")
            parts = solids(cannon, painter, RECOIL if frame == "recoil" else 0.0)
            for name, _m, _f, c0, _p in todo:
                box = nk.sprite_box(pic, c0, 0)
                pieces = nk.piece_parts(plate, plate_keys(cannon, painter), parts, box, nk.box_owner(box), name,
                                        painter, ("dark", 0x01))
                for p in pieces:
                    p.hide_render = False
                mask = nk.sprite_mask(pic, c0, 0) if "check" in options else None
                piece = nk.finish(name, pieces, box, out, options, painter, mask=mask, origin=(LEFT + c0 + 12, 0.0))
                bpy.data.objects.remove(piece)


if __name__ == "__main__":
    build()
