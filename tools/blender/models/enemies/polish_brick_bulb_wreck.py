"""What is left of UNDERDELI's brick bulb once it is destroyed (stage 4 of the clean ground: the wreck models that stand
in for the map's painting of it; sheet ^ (x5e) sprites 153 beside 155 above 191 beside 193), built on
polish_brick_bulb.py (2026-10-25). models.cfg: model brick_bulb_tl_wreck / _tr_wreck / _bl_wreck / _br_wreck
enemies/brick_bulb_*_wreck.glb origin; wreck x5e 153 brick_bulb_tl_wreck, wreck x5e 155 brick_bulb_tr_wreck, wreck x5e
191 brick_bulb_bl_wreck, wreck x5e 193 brick_bulb_br_wreck. The game draws them where the map paints the wreck
(UNDERDELI's six bulbs), with the live sprite lines' options (yaw=0 height=-4), at the live pieces' places.

The painting (the same on all six: at 564, 6733 where the sprites lie, two rows higher up the screen at four places
and one at the sixth; at 1x and in the HD tiles): the machine as the live sprites draw it, its outline the same, a dim
broken copy of it: the hood over the bulb burnt black and broken away in its middle (columns 19-30 of rows 9-14 dark,
only its rim's ends left as dark grey arcs either side, columns 14-18 and 31-35 of rows 11-20); the bulb's glass a
cracked shell of dark reds (0x41-0x4a, the live 0x44-0x4e), its crown broken off (its top row and its white-pink
highlight gone), a crack across it (column 25 of rows 19-21, black); the stalk's neck and foot as they were, darker;
the brackets' rings and wedges burnt dark (0x01-0x06 where the live greys are 0x02-0x0a), their lit edges dim; the red
pistons standing, a shade darker.

The model: the live machine (polish_brick_bulb.Bulb: one heightfield of it in the picture's plane, the bulb a solid on
it), its hood broken (lowered to jagged stumps along its rim's ends, its middle gone to a low burnt floor of rubble),
the whole a little lower where it is burnt (BURNT_LOW); the bulb's crown broken away along a jagged fracture lower to its
upper right (an exact boolean with a height-field cutter, polish_panel_pills_wreck's), the bulb split in two along the
painting's crack (polish_panel_pills_wreck.split_piece: its right part fallen away to the lower right, the left one
leaning a little; the crack's faces dark), a dull glow left in its glass (0.06-0.15); everything painted by the
PAINTING's pixels under it (the live Painter's zones and finish, its lift lower, the greys' lowest: the HD painting's
burnt rings and hood read nearly black; so the burnt greys and the darker reds are the painting's own), sheared along the camera's line of sight as the live pieces (the camera sees each
point where the painting draws it); a few charred shards of the hood and red shards of the glass on the bricks round
it. Cut into the four pieces along the sprites' edges as the live machine (polish_sheet9_kit.piece_parts and finish).

Coordinates as polish_brick_bulb.py's: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the bricks; the
whole's origin is the middle of the picture: column c is x = c + 0.5 - 24, row r is y = 27.5 - r.

Options after "--": --outdir <dir> (default assets/models/enemies), --preview <prefix>, --only <name,...>.
"""
import math
import os
import sys

import bpy
import numpy as np
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
import polish_sheet9_kit as nk  # noqa: E402
from polish_sheet9_kit import Pic, parse, blur, smoothstep, smax, Zone, Painter, round_rise  # noqa: E402
from polish_panel_pills_wreck import heightfield_cutter, break_away, fbm, perlin  # noqa: E402
import polish_brick_bulb as live  # noqa: E402

# The painting's pixels (UNDERDELI at 564, 6733: the picture's top left at 552, 6719), the live machine's own pixels
# only (the bricks round it left out).
PAINT = """
    ................................................................................................
    ................................................................................................
    ................................................................................................
    ................................................................................................
    ................................................................................................
    ................................................................................................
    ................................................................................................
    ................................................................................................
    ................................................................................................
    ........................................010101010101010101......................................
    ....................................01010104040305060605030101..................................
    ..................................010101020404020304040305030201................................
    ................................0101020102020303030103040304020101..............................
    ..............................01040601010102030501010403010101020101............................
    ..............................05060504030101010302040401010101010303............................
    ............................050603040402010145494a49470101010101030704..........................
    ............................080102030402014241444747474601020104080606..........................
    ..........................0305010101030149464544464446454502010706030502........................
    ..............................010101030449484a4544434244480101030202............................
    ..............................01030406044947494846014349470102020201............................
    ..............................02050606044744454544414846460102010101............................
    ........................................434141444440464744......................................
    ..........................................01414242414847........................................
    ..........................................01434344454844........................................
    ..........................................01014645470101........................................
    ..........................................4313464647a244........................................
    ..............................06..........42484747454245..........07............................
    ..............................01010101020249474745444447020201010104............................
    ..............................01010203020248474646454648020101010101............................
    ..........01040a0706480101010102040504020248454646464748010101040101010101014d0706060501........
    ........0503060502024b010101010406040103..................0101040201010101014a010106060401......
    ......010204030102034a050201010103010202..................0102010201010102064901010106060401....
    ......04070401020403494805030101010102......................010101010104064b4901030101050402....
    ......08060102040403484546050301030404......................0303020304054b484701010102010404....
    ......07060103040201474545464803050502......................030402044d4b48474601020404010403....
    ......06050103040101464546454802030406......................060201044a4747464601010204010302....
    ......04030101010102464646454601010705......................050101034a4746464501010101010302....
    ......030301030202034645454543010404..........................010101484646454501040102020402....
    ......0201010303030445454345430104..............................0101464645454501020101020504....
    ......0102040403030445424245010506..............................0104464443424201010102050305....
    ......0104040403010443434346410606..............................0404454341424301010103020303....
    ........040403020104030404040506..................................050504010403010102010102......
    ..........03010307044b4946444647..................................4648444547430408020101........
    ..........0102030505474544424647..................................4747444243430506050101........
    ..........010104050446454240..........................................454342420406040101........
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
# The hood's breakage: its rim's ends kept (how far from the axis they begin, how high they stand: a share of the live
# height), its middle gone to a low floor of rubble (height, how much the rubble wanders).
HOOD_KEEP = (5.8, 8.6, 0.62)
RUBBLE = (0.22, 0.06)
BURNT_LOW = 0.86                      # the burnt machine stands this much of the live height
# The bulb's fracture: its height over the bulb's middle, how much it wanders; the crack (from, to: columns, rows; its
# width; how deep under the bulb's top); the dull glow left in it (palette index: emission).
FRACTURE = (2.2, 0.5)
FRACTURE_DARK = -1.5                  # the fracture's broken glass: this many shades darker than the shell
CRACK = ((25.9, 16.6), (24.6, 22.8), (26.0, 0.6, 9.0))   # from, to; the right part's turn and drop, the left's turn
DULL_GLOW = {0x41: 0.0, 0x42: 0.06, 0x43: 0.07, 0x44: 0.08, 0x45: 0.09, 0x46: 0.1, 0x47: 0.11, 0x48: 0.12,
             0x49: 0.13, 0x4a: 0.14, 0x4b: 0.15}
# The shards on the bricks round it: (column, row, size, heading, kind): charred shards of the hood ("hood") and red
# shards of the glass ("glass").
SHARDS = [(15.2, 9.6, 1.6, 30.0, "hood"), (33.8, 10.4, 1.4, -40.0, "hood"), (12.6, 21.8, 1.2, 75.0, "hood"),
          (36.4, 21.0, 1.1, 15.0, "hood"), (29.6, 9.0, 0.9, 120.0, "glass"), (19.4, 8.6, 0.8, -15.0, "glass"),
          (31.6, 23.6, 0.7, 60.0, "glass"), (17.2, 24.4, 0.75, 200.0, "hood")]
PIECES = [(name + "_wreck", place) for name, place in live.PIECES]
LIFT = 0.3                            # the painter's lift (the live's 1.2): the burnt machine reads darker,
GREY_LIFT = -0.6                      # its greys the darkest (the HD painting's burnt black rings and hood)


class Wreck(live.Bulb):
    """The live machine's heights (its shapes, creases and relief from the live sprite), its hood broken and its burnt
    parts a little lower."""

    def __init__(self):
        super().__init__()
        self.paint = Pic(parse(PAINT), -24.0, 28.0)

    def hood_keep(self, u, v):
        """How much of the hood stands: its rim's ends, jagged."""
        a0, a1, share = HOOD_KEEP
        side = smoothstep(a0, a1, np.abs(u - live.AXIS_U) + 0.9 * np.vectorize(lambda x, y: fbm(x * 0.6, y * 0.6, 3.0))(u, v))
        return share * side

    def heights(self, X, Y):
        X, Y = np.asarray(X, float), np.asarray(Y, float)
        u, v = X + 24.0, 28.0 - Y
        d = self.region.depth(X, Y)
        z = np.maximum(self.half(u, v, d), self.half(2 * live.AXIS_U - u, v, d))
        (hc, hr), radius, low, hh, rnd, domed = live.HOOD
        rad = np.hypot(u - hc, v - hr)
        hood = (hh * round_rise(d, rnd) + domed * np.clip(1.0 - (rad / radius) ** 2, 0.0, 1.0)) * (v < low + 0.6)
        in_hood = (v < low + 0.6) & (rad < radius + 1.0)
        hood = hood * self.hood_keep(u, v)
        z = smax(z, hood, 0.4)
        z = smax(z, live.lying(u, v, live.NECK), 0.5)
        (c0, c1), (r0, r1), fh, fr = live.FOOT
        uu = np.minimum(u - c0, c1 - u)
        vv = np.minimum(v - r0, r1 - v)
        z = smax(z, fh * round_rise(np.minimum(uu, vv), fr) * (uu > 0) * (vv > 0), 0.5)
        (bc, br), (bx, by, bz), bmid = live.BALL
        qb = ((u - bc) / bx) ** 2 + ((v - br) / by) ** 2
        z = np.where(qb < 1.0, np.minimum(z, bmid - 0.6), z)
        pic = self.pic
        z = z - live.CREASE * pic.sample(self.crease, X, Y) * np.clip(z / 3.0, 0.0, 1.0)
        fine = pic.sample(self.soft, X, Y) - pic.sample(self.broad, X, Y)
        z = z + np.clip(live.DETAIL[0] * fine, -live.DETAIL[1], live.DETAIL[1]) * smoothstep(1.0, 2.5, z)
        z = z * round_rise(d, 0.8) * BURNT_LOW
        # where the hood is gone: a low floor of burnt rubble
        floor = RUBBLE[0] + RUBBLE[1] * np.vectorize(lambda x, y: perlin(x * 0.9, y * 0.9, 5.0))(X, Y)
        z = np.where(in_hood & (qb >= 1.0), np.maximum(z, floor * round_rise(d, 0.6)), z)
        return np.where(d > 0, np.maximum(z, 0.0), 0.0)


def broken_bulb(painter):
    """The bulb: the live solid, its crown broken away along a jagged fracture, split in two along the painting's crack
    (its right part fallen away to the lower right, the left one leaning a little), its glass painted by the painting's
    reds (glowing dully), the fracture a little darker, the crack's faces dark."""
    from polish_panel_pills_wreck import split_piece, turn
    (bc, br), radii, bz = live.BALL
    cx, cy = bc - 24.0, 28.0 - br
    ball = nk.ellipsoid("brick_bulb_ball", (cx, cy, bz), radii, count=12, around=32, cut_below=0.3)
    mk.apply(ball)
    ball.data.materials.append(painter.material(("bulb", 0x48)))
    rim = painter.material(("bulb", 0x41))
    crack = painter.material(("dark", 0x01))
    base, jag = FRACTURE

    def fracture(x, y):
        # (lower towards the upper right, where the painting's bulb has lost most)
        return (bz + base + jag * fbm(x * 0.5 + 3.0, y * 0.5, 1.0, 3) -
                0.8 * max(0.0, (x - cx) / radii[0] + (y - cy) / radii[1]))
    cutter = heightfield_cutter("bulb_cut", cx - radii[0] - 0.5, cx + radii[0] + 0.5, cy - radii[1] - 0.5,
                                cy + radii[1] + 0.5, 0.4, fracture, bz + radii[2] + 3.0, rim)
    break_away(ball, cutter)
    from polish_pyramid_wreck import canonical
    canonical(ball)
    (ca, ra), (cb, rb), (tilt_r, drop_r, tilt_l) = CRACK
    a, b = Vector((ca - 24.0, 28.0 - ra, 0.0)), Vector((cb - 24.0, 28.0 - rb, 0.0))
    along = (b - a).normalized()
    normal = Vector((-along.y, along.x, 0.0))
    if normal.x < 0:
        normal = -normal
    right = split_piece(ball, (a + b) / 2, normal, crack, "brick_bulb_ball_right")
    parts = [ball] + ([right] if right is not None else [])
    for obj, tilt, drop, sign in ((ball, tilt_l, 0.0, -1.0), (right, tilt_r, drop_r, 1.0)):
        if obj is None:
            continue
        # turned about its foot's outer edge along the crack, falling away from it
        foot = (a + b) / 2 + normal * sign * radii[0] * 0.8 + Vector((0.0, 0.0, 0.3))
        turn([obj], foot, along * sign, tilt)
        obj.data.transform(Matrix.Translation(normal * sign * drop * 0.5 + Vector((0.0, -drop * 0.3, -drop))))
        canonical(obj)
        k.smooth(obj, 60)
        keys = painter.keys(obj, zone="bulb")
        broken = painter.keys(obj, zone="bulb", offset=FRACTURE_DARK)
        names = [m.name for m in obj.data.materials]
        for i, poly in enumerate(obj.data.polygons):
            if names[poly.material_index] == rim.name:
                keys[i] = broken[i]
            elif names[poly.material_index] == crack.name:
                keys[i] = ("dark", 0x01)
        nk.assign(obj, keys, painter)
    return parts


def shards(painter):
    """The shards on the bricks round the machine (solids cut with the pieces)."""
    from polish_jaw_gun_wreck import rock
    out = []
    for i, (c, r, size, heading, kind) in enumerate(SHARDS):
        x, y = c - 24.0, 28.0 - r
        mat = painter.material(("grey", 0x03) if kind == "hood" else ("red", 0x45))
        flat = 0.35 if kind == "hood" else 0.6
        obj = rock(f"bulb_shard{i}", (x, y, 0.0), (size, size * 0.65, size * flat), mat, 7.0 + 1.9 * i, flat=0.0)
        obj.data.transform(Matrix.Translation((x, y, 0.0)) @ Matrix.Rotation(math.radians(heading), 4, "Z") @
                           Matrix.Translation((-x, -y, 0.0)))
        out.append(obj)
    return out


def build():
    options = k.args()
    out = mk.outdir(options)
    only = set(options["only"].split(",")) if "only" in options else None
    k.reset()
    wreck = Wreck()
    pic = wreck.paint
    a = pic.a
    own = a >= 0
    red = own & np.isin(a >> 4, (1, 4, 10))
    grey = own & (a >> 4 == 0)
    painter = Painter(pic, [Zone("grey", grey, live.GREY, live.FINISH["grey"], lift=GREY_LIFT),
                            Zone("red", red, [0x41, 0x42] + live.RED, live.FINISH["red"], sigma=0.6),
                            Zone("bulb", red, [0x41, 0x42] + live.RED, live.FINISH["bulb"], glow=DULL_GLOW, sigma=0.6,
                                 lift=1.2, comp=1.4, pick=False),
                            Zone("dark", own, [0x01, 0x02], live.FINISH["dark"], lift=0.0, comp=0.0, pick=False)],
                      "bulbwreck", lift=LIFT)
    # (the live region: the machine's outline as the live sprite has it; the heights where the painting burns it)
    plate = nk.gw.Plate((-24.0, 24.0, -28.0, 28.0), wreck.heights, cells=wreck.region.inside)
    solids = broken_bulb(painter) + shards(painter)
    for obj in solids:
        obj.hide_render = True

    def keys(obj, kinds, wall_z):
        centres, normals = nk.face_data(obj)
        near = painter.zone_at(centres[:, 0], centres[:, 1])
        out_ = painter.keys(obj, zones=["dark" if kinds[i] != 0 else near[i] for i in range(len(kinds))])
        return [("dark", 0x01) if kinds[i] != 0 else key for i, key in enumerate(out_)]
    for name, (c0, r0) in PIECES:
        if only is not None and name not in only:
            continue
        box = nk.sprite_box(pic, c0, r0)
        parts = nk.piece_parts(plate, keys, solids, box, nk.box_owner(box), name, painter, ("bulb", 0x41))
        for p in parts:
            p.hide_render = False
        piece = nk.finish(name, parts, box, out, options, painter, origin=(pic.left + c0 + 12, pic.top - r0 - 14))
        bpy.data.objects.remove(piece)


if __name__ == "__main__":
    build()
