"""UNDERDELI's brick bulb: a machine set in the brick floor, a red bulb on a stalk under a grey hood between two grey
rings round red pistons (sheet ^, x5e in models.cfg: 153 beside 155 above 191 beside 193, 2x2 each, one 48 x 56
picture); polished (2026-10-22, round 37). It replaces wave3_i.py's ring_whole() (pixel regions raised in bands,
ellipsoids, a lathed piston and tubes).

Where the level puts it: UNDERDELI's event 12 (four ground enemies as one 2x2 block, x and x + 24, y and y - 28) with
enemy 33, six times (t216 x 18, t384 x 138, t496 x 210, t1392 x 138, t3268 x 66, t3324 x 66): 33 (191) at the lower
left, 34 (193) right of it, 35 (153) above 191, 36 (155) above 193; ground enemies of episode 4, armour 30, one frame
each, no damaged look, nothing fired or launched; the four share the event's link, so shooting one down destroys the
block (each leaves the game's wreck of its model). Every block lies on the map's tile grid, on two by two tiles that
paint a dimmer, broken copy of the same machine in the bricks (what stays when it is shot down): the sprites' bricks
round it equal the map's in five of the six placements (the sixth is a pixel off the grid), so they are left out, and
the model covers the machine's whole outline over the map's painting. No other level (episode 6 included) and no other
enemy, launched ones included, shows these sprites; no other sprite is their pixels mirrored, turned or in other ramps.
The picture is symmetric about column 24's middle (x 0.5), shading apart.

As the sprites and their 4x upscales draw it (columns and rows of the 48 x 56 picture; grey ramp 0, red ramp 4, lit
from the upper left): a grey hood like a fan over the bulb (columns 13-35 of rows 9-20, its rim an arc, lit at its
upper left); the bulb, a glossy red ball (columns 19-29 of rows 14-22) with a white-pink highlight at its upper left;
under it a pinched red neck (rows 21-24) on a red foot block (columns 21-27 of rows 25-29); either side of it, lower
down, a grey bracket (columns 3-21 of rows 26-44 on the left): a thick C of a ring round a dark recessed face (a groove
along its inside, a grey bar across its foot at row 40), a red piston lying up the screen on its inner side (columns
10-14 of rows 28-39) on a wider red foot (rows 41-44), and a grey wedge between the piston and the stalk; the right
bracket the same mirrored.

Built for the game's camera with polish_sheet9_kit: one heightfield of the whole machine in the picture's plane on the
sprites' grid (the hood a plate rounding over at its rim, the neck and the foot lying tubes and a block, each bracket a
low plate with its ring a lying tube along its C, the recess sunk, the piston and its foot lying round tubes, the bar
and the wedge; joined by smooth maxima, the dark lines creased), the bulb a solid ellipsoid on it (cut along the pieces'
edge, its caps dark red), glossy and glowing a little in its own reds (0.12-0.3: round things read near black from the
slanted camera); everything painted by the pixels under it (polish_sheet9_kit.Painter) and sheared along the camera's
line of sight. Heights: z 0 to 8.0 (the bulb's top), the brackets 3.7-4.4, the hood 3.6.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the bricks (z 0). The whole's
origin is the middle of the picture: column c is x = c + 0.5 - 24, row r is y = 27.5 - r; the pieces' origins (their
sprites' middles) (-12, 14) 153, (12, 14) 155, (-12, -14) 191, (12, -14) 193 (models.cfg origin).

models.cfg: the four model lines stay (brick_bulb_tl ... origin); the sprite lines get height=-4 (pieces drawn at their
own origin stand at the ground enemies' layer, 4 pixels over the terrain: height=-4 sets them on the bricks, as
UNDERDELI's brick crab, core machine and floor eye are): sprite x5e 153 brick_bulb_tl yaw=0 height=-4, and the same for
155, 191 and 193.

Replaces wave3_i.py's brick bulb: RING, ring_whole(), its w.WHOLES["ring"] entry and the loop registering
brick_bulb_tl ... _br, the brick_bulb paragraph of its docstring ("ring," in its --whole usage line), and
wave3_i_art.py's RING (only ring_whole() reads it).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each piece's outline as the
camera sees it against its sprite's own pixels, the bricks left out), --preview <prefix>, --only <name,...>.
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

AXIS_U = 24.5                     # the picture's mirror line (column 24's middle): u' = 2 AXIS_U - u
HOOD = ((24.5, 21.0), 12.0, 20.9, 3.2, 1.4, 0.45)  # disc middle, radius, its lower edge (row), height, rounding, dome
BALL = ((24.5, 18.35), (5.35, 4.7, 4.2), 3.8)      # middle (column, row), radii, its middle's height (top at 8.0)
NECK = [(24.5, 20.6, 2.5, 3.1), (24.5, 25.0, 2.6, 3.2)]  # a lying tube: (column, row, half width, height)
FOOT = ((21.0, 28.0), (25.0, 30.0), 4.2, 1.0)      # the stalk's foot block: columns, rows, height, rounding
BRACKET = (2.3, 1.0)              # the brackets' plate: height, rounding
RING = [(9.2, 27.5), (6.7, 28.5), (4.9, 30.3), (4.05, 33.0), (3.95, 36.5), (4.1, 40.0), (5.0, 42.2), (6.8, 43.5),
        (9.4, 44.3)]              # the ring's C (column, row) on the left
RING_W = (1.75, 3.7)              # its half width, height
RECESS = ((7.55, 35.0), (2.35, 4.9), 1.35)         # the recessed face inside the ring: middle, radii, depth
PISTON = [(12.5, 28.3, 2.65, 4.4), (12.5, 39.7, 2.65, 4.4)]
PISTON_FOOT = [(12.95, 41.4, 3.05, 4.0), (12.95, 43.5, 3.05, 4.0)]
BAR = [(4.0, 40.55, 0.85, 3.0), (16.6, 40.55, 0.85, 3.0)]  # the grey bar across the bracket's foot
WEDGE = [(17.4, 28.6, 2.7, 3.1), (17.0, 38.8, 2.5, 3.0)]   # the grey wedge between the piston and the stalk
CREASE = 0.5
DETAIL = (0.05, 0.15)
GREY = [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b]
RED = [0x43, 0x44, 0x45, 0x46, 0x47, 0x48, 0x49, 0x4a, 0x4b, 0x4c, 0x4d, 0x4e]
BULB_GLOW = {0x43: 0.12, 0x44: 0.13, 0x45: 0.14, 0x46: 0.15, 0x47: 0.17, 0x48: 0.19, 0x49: 0.21, 0x4a: 0.23,
             0x4b: 0.25, 0x4c: 0.27, 0x4d: 0.29, 0x4e: 0.3}
FINISH = {"grey": (0.28, 0.4), "red": (0.22, 0.3), "bulb": (0.18, 0.18), "dark": (0.2, 0.5)}
PIECES = [("brick_bulb_tl", (0, 0)), ("brick_bulb_tr", (24, 0)), ("brick_bulb_bl", (0, 28)), ("brick_bulb_br", (24, 28))]

# The machine's own pixels (palette indices; the bricks round it, the map's, left out).
ART = """
    ................................................................................................
    ................................................................................................
    ................................................................................................
    ................................................................................................
    ................................................................................................
    ................................................................................................
    ................................................................................................
    ................................................................................................
    ................................................................................................
    ........................................030707070707060503......................................
    ....................................03070706060606060606060403..................................
    ..................................050907060606060606060606060504................................
    ................................0509060606060606060606060606060604..............................
    ..............................06090606060605040404040405060606060604............................
    ..............................090606060605444a4a4a494704050606060606............................
    ............................090606060605444b49484848484604050606060606..........................
    ............................0606060606034a4948494948484746030506060606..........................
    ..........................0104060606060449484b4b4b4948474702040506060401........................
    ..............................030606060449484c4e4c484746480204050603............................
    ..............................010406060449484a4b48474646480204040201............................
    ..............................01010205044948484847464647480202010101............................
    ........................................464947474646474846......................................
    ..........................................46484747474846........................................
    ..........................................01104848481001........................................
    ..........................................4613474747a246........................................
    ..........................................49464747474447........................................
    ..............................01..........4a474747474748..........05............................
    ..............................0101020302024a484848484848020203020105............................
    ..............................0204050402024b494949494949010104050405............................
    ..........04090602024b020203040506050103024b4a4a4a4a4a4a010301050606040302024a0202060604........
    ........0409060102034a060606060606020403..................03040306060606060649020202060604......
    ......0409060102040349490606060602040403..................03040403060606064b4902030302060604....
    ......08060102040403494849050403040504......................0405050404054b484902030403020606....
    ......07060103040403494848494904050503......................030505054d4b48484902030404020706....
    ......06060103040403494848484905050407......................060405054a4848484901030404010706....
    ......06060102020202494848484905040806......................060604054a4848484901020202010706....
    ......06060104040403494848484904080503......................03050604494848484902040404020706....
    ......060603040505044948484849060603..........................030606494848484903040505040706....
    ......0606060405050449484848490606..............................0606494848484903040504080606....
    ......0506060604050449494949490606..............................0606494949494902040408060605....
    ......0306060606040403040404050605..............................0506050444040301040806060603....
    ........0406060607044e4c4a494948..................................484b49494949040806060604......
    ..........04060606054a4848484947..................................4749484848490506060604........
    ..........0104060604494949494744..................................4447494949490406060401........
    ..........020202030246474746..........................................464747460203020102........
    ................................................................................................
    ................................................................................................
    ................................................................................................
    ................................................................................................
    ................................................................................................
    ................................................................................................
    ................................................................................................
    ................................................................................................
    ................................................................................................
    ................................................................................................
    ................................................................................................
"""


def lying(u, v, points, power=0.5):
    """polish_gyges_wall.tube in the picture's columns and rows (v down the picture)."""
    return nk.tube(u, -v, [(c, -r, hw, hh) for c, r, hw, hh in points], power)


class Bulb:
    def __init__(self):
        self.pic = Pic(parse(ART), -24.0, 28.0)
        a = self.pic.a
        own = a >= 0
        self.region = Region(self.pic, own, sigma=0.5)
        shade = np.where(own, a & 15, 0).astype(float)
        h, w = a.shape
        p = np.pad(own, 1)
        surrounded = np.ones_like(own)
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            surrounded &= p[1 + dr:1 + dr + h, 1 + dc:1 + dc + w]
        dark = own & (shade <= 1) & (a >> 4 == 0)
        self.crease = blur((dark & surrounded).astype(float), 0.45)
        self.soft = blur(nk.fill(shade, own), 0.6)
        self.broad = blur(nk.fill(shade, own), 2.0)

    def half(self, u, v, d):
        """The left half's shapes (the brackets; the middle's shapes are symmetric themselves)."""
        z = np.zeros_like(u)
        side = (v > 26.0) & (u < 21.5)
        z = np.where(side, BRACKET[0] * round_rise(d, BRACKET[1]), z)
        ring = lying(u, v, [(c, r, RING_W[0], RING_W[1]) for c, r in RING])
        z = smax(z, ring, 0.5)
        (rc, rr), (rx, ry), depth = RECESS
        q = ((u - rc) / rx) ** 2 + ((v - rr) / ry) ** 2
        z = z - depth * (1.0 - smoothstep(0.55, 1.0, q)) * (ring < 0.5)
        z = smax(z, lying(u, v, WEDGE, power=0.3), 0.6)
        z = smax(z, lying(u, v, BAR), 0.3)
        z = smax(z, lying(u, v, PISTON), 0.35)
        z = smax(z, lying(u, v, PISTON_FOOT, power=0.35), 0.35)
        return z

    def heights(self, X, Y):
        X, Y = np.asarray(X, float), np.asarray(Y, float)
        u, v = X + 24.0, 28.0 - Y
        d = self.region.depth(X, Y)
        z = np.maximum(self.half(u, v, d), self.half(2 * AXIS_U - u, v, d))
        (hc, hr), radius, low, hh, rnd, domed = HOOD
        rad = np.hypot(u - hc, v - hr)
        hood = (hh * round_rise(d, rnd) + domed * np.clip(1.0 - (rad / radius) ** 2, 0.0, 1.0)) * (v < low + 0.6)
        z = smax(z, hood, 0.4)
        z = smax(z, lying(u, v, NECK), 0.5)
        (c0, c1), (r0, r1), fh, fr = FOOT
        uu = np.minimum(u - c0, c1 - u)
        vv = np.minimum(v - r0, r1 - v)
        foot = fh * round_rise(np.minimum(uu, vv), fr) * (uu > 0) * (vv > 0)
        z = smax(z, foot, 0.5)
        # Under the bulb (a solid of its own) the plate stays low enough for the ball to show all round.
        (bc, br), (bx, by, bz), bmid = BALL
        qb = ((u - bc) / bx) ** 2 + ((v - br) / by) ** 2
        z = np.where(qb < 1.0, np.minimum(z, bmid - 0.6), z)
        pic = self.pic
        z = z - CREASE * pic.sample(self.crease, X, Y) * np.clip(z / 3.0, 0.0, 1.0)
        fine = pic.sample(self.soft, X, Y) - pic.sample(self.broad, X, Y)
        z = z + np.clip(DETAIL[0] * fine, -DETAIL[1], DETAIL[1]) * smoothstep(1.0, 2.5, z)
        z = z * round_rise(d, 0.8)
        return np.where(d > 0, np.maximum(z, 0.0), 0.0)


def build():
    options = k.args()
    out = mk.outdir(options)
    only = set(options["only"].split(",")) if "only" in options else None
    k.reset()
    bulb = Bulb()
    pic = bulb.pic
    a = pic.a
    own = a >= 0
    red = own & np.isin(a >> 4, (1, 4, 10))     # ramp 4, and the stalk's dark brown specks (ramps 1 and 10)
    painter = Painter(pic, [Zone("grey", own & (a >> 4 == 0), GREY, FINISH["grey"]),
                            Zone("red", red, RED, FINISH["red"], sigma=0.6),
                            Zone("bulb", red, RED, FINISH["bulb"], glow=BULB_GLOW, sigma=0.6, lift=1.4, comp=1.6,
                                 pick=False),
                            Zone("dark", own, [0x01, 0x02], FINISH["dark"], lift=0.0, comp=0.0, pick=False)],
                      "bulb")
    plate = nk.gw.Plate((-24.0, 24.0, -28.0, 28.0), bulb.heights, cells=bulb.region.inside)
    (bc, br), radii, bz = BALL
    ball = nk.ellipsoid("brick_bulb_ball", (bc - 24.0, 28.0 - br, bz), radii, count=12, around=32, cut_below=0.3)
    nk.assign(ball, painter.keys(ball, zone="bulb"), painter)
    ball.hide_render = True

    def keys(obj, kinds, wall_z):
        centres, normals = nk.face_data(obj)
        near = painter.zone_at(centres[:, 0], centres[:, 1])
        out_ = painter.keys(obj, zones=["dark" if kinds[i] != 0 else near[i] for i in range(len(kinds))])
        return [("dark", 0x01) if kinds[i] != 0 else key for i, key in enumerate(out_)]
    for name, (c0, r0) in PIECES:
        if only is not None and name not in only:
            continue
        box = nk.sprite_box(pic, c0, r0)
        parts = nk.piece_parts(plate, keys, [ball], box, nk.box_owner(box), name, painter, ("red", 0x43))
        for p in parts:
            p.hide_render = False
        mask = nk.sprite_mask(pic, c0, r0) if "check" in options else None
        piece = nk.finish(name, parts, box, out, options, painter, mask=mask,
                          origin=(pic.left + c0 + 12, pic.top - r0 - 14))
        bpy.data.objects.remove(piece)


if __name__ == "__main__":
    build()
