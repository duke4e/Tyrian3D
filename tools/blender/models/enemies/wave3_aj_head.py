"""The armoured head of UNDERDELI, LAVA RUN and DREAD-NOT (wave 3, batch AJ; sheet 9), modelled as its sprites look
(models.cfg: yaw=0); the rest of the sheet is in wave3_aj.py, wave3_aj_eye.py, wave3_aj_dread.py and
wave3_aj_capsule.py, the kit in wave3_aj_kit.py, the pixels in wave3_aj_art.py.

The levels draw it from ten sprites as the sheet lays them out, 72 x 84 pixels (enemies 317, 318 at
(x + 12, y - 56), (x + 36, y - 56); 315, 316 at (x, y - 42), (x + 48, y - 42); 312-314 at (x, y - 28) ..
(x + 48, y - 28); 309-311 at (x, y) .. (x + 48, y), 336 for 310 in LAVA RUN): on the ground in UNDERDELI and
DREAD-NOT, in the sky in LAVA RUN. The sprites overlap (10 and 28, 12 and 32 share a tile; 28 and 32 reach into
47 and 51's rows), so each region is kept by one piece (dome_head_<sprite>, origin):

- 10 and 12: the dome's top, columns 12-59, rows 0-27; 28 and 32: the dome's sides, columns 0-11 and 60-71, rows
  14-27; 47, 49, 51: rows 28-55 (the brows, the slots, the knob); 85, 87, 89: rows 56-83 (the jaw plate).

The head: a grey dome of armour plates, a raised Y seam down its middle to a steel knob; over each side a thick
glossy red brow, curling down outwards; under the brows dark slots with black pipes and small red pads; below
them a broad jaw plate, its top edge rolled, a ridge down its middle to a notch, four red bulbs sunk in sockets
in a V, a shallow cradle in its middle (8 pixels high) where UNDERDELI's lilac capsule (9 123, enemy 319 at
(x + 23, y + 2), drawn over the head) rests: models.cfg raises the capsule onto it (height=11.5). It stands on
z = 0, the dome rising about 22 pixels, the brows a little more.

usage: Blender -b --factory-startup -P wave3_aj_head.py -- [--only name,name] [--preview <prefix>] [--check 1]
       [--stats 1] [--whole <prefix>]
"""
import math
import os
import sys

from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_aj_kit as kit  # noqa: E402
from wave3_aj_kit import k, sh, pal, Painter, smoothstep  # noqa: E402

HEAD = kit.frame("HEAD", 72, (36, 42))
F = HEAD
AX = 35.6        # the head's middle (pixel column)
FLOOR = 4.5      # the slots' floor


def P(c, r, z=0.0):
    """A point at continuous pixel coordinates (column, row) of the whole."""
    return (c - F.ox, F.oy - r, z)


def cr(x, y):
    return x + F.ox, F.oy - y


# --- Heights -------------------------------------------------------------------------------------------------

def dome_h(c, r):
    """The dome: highest a little above its middle, falling to the front (down the screen) more slowly."""
    dx = (c - AX) / 31.5
    dy = (r - 25.0) / (17.5 if r < 25.0 else 27.0)
    q = 1.0 - dx * dx - dy * dy
    return 22.5 * math.sqrt(q) if q > 0 else -6.0 * (math.sqrt(-q) if q < 0 else 0.0)


BULBS = [  # (column, row, radius across, radius along, turn): the red bulbs on the jaw plate
    (14.6, 60.6, 4.7, 5.7, -12.0), (56.6, 60.6, 4.7, 5.7, 12.0),
    (26.1, 66.8, 4.6, 6.1, 18.0), (45.1, 66.8, 4.6, 6.1, -18.0),
]


def bulb_q(c, r, b, grow=0.0):
    bc, br, rx, ry, turn = b
    a = math.radians(turn)
    u, v = (c - bc) * math.cos(a) + (br - r) * math.sin(a), -(c - bc) * math.sin(a) + (br - r) * math.cos(a)
    return (u / (rx + grow)) ** 2 + (v / (ry + grow)) ** 2


def plate_h(c, r, dents=True):
    """The jaw plate under the slots: its top edge rolled over (rows 46-51), highest in its middle, a ridge
    down its middle, sockets round the bulbs."""
    u = abs(c - AX) / 36.0
    top = 4.8 + 7.8 * (1.0 - u ** 1.4) - 0.07 * max(0.0, r - 52.0)
    du = abs(c - AX)
    top += 1.7 * max(0.0, 1.0 - (du / 5.8) ** 4) * smoothstep(47.0, 52.0, r) * (1.0 - smoothstep(74.0, 79.0, r))
    roll = math.sqrt(max(0.0, min(1.0, (r - 45.8) / 5.0)) * (2.0 - max(0.0, min(1.0, (r - 45.8) / 5.0))))
    z = FLOOR + (top - FLOOR) * roll
    if dents:
        for b in BULBS:
            q = bulb_q(c, r, b, 1.2)
            z -= 2.2 * (1.0 - smoothstep(0.55, 1.0, q))
    # The bay in the jaw's middle where UNDERDELI's lilac capsule (9 123) rests: a shallow cradle.
    qc = ((c - CRADLE_C[0]) / CRADLE_R[0]) ** 2 + ((r - CRADLE_C[1]) / CRADLE_R[1]) ** 2
    if z > CRADLE_Z:
        z = CRADLE_Z + (z - CRADLE_Z) * smoothstep(0.5, 1.0, qc)
    return z


CRADLE_C, CRADLE_R, CRADLE_Z = (35.5, 72.5), (8.2, 10.5), 8.0


SLOTS = [(3.0, 28.5, 37.2, 46.8), (43.0, 68.5, 37.2, 46.8)]  # (c0, c1, r0, r1)


def slot_amount(c, r):
    out = 0.0
    for c0, c1, r0, r1 in SLOTS:
        out = max(out, smoothstep(c0 - 0.5, c0 + 1.0, c) * smoothstep(-c1 - 0.5, -c1 + 1.0, -c) *
                  smoothstep(r0 - 0.4, r0 + 0.8, r) * smoothstep(-r1 - 0.8, -r1 + 0.4, -r))
    return out


def shell_h(c, r):
    d = dome_h(c, r)
    s = slot_amount(c, r)
    d = d + (min(d, FLOOR) - d) * s
    z = max(d, FLOOR)
    if r > 45.0:
        z = kit.smax(z, plate_h(c, r), 0.8)
    return z


# --- Parts -------------------------------------------------------------------------------------------------------

def shell():
    grey = Painter("hshell", shades={0: (1, 2, 3, 4, 5, 6, 7, 8, 9, 0xa, 0xb)}, metallic=0.4, roughness=0.36)
    polys = kit.outlines_of(F, lambda val, c, r: True, smooth=2, epsilon=0.35)

    def z_of(x, y, e):
        c, r = cr(x, y)
        return 1.2 + (shell_h(c, r) - 1.2) * e
    body = kit.heightfield("hshell", polys, z_of, grey(0x06), spacing=1.0, edge=3.6)
    k.smooth(body, 45)
    kit.pixelate(body, F)
    kit.paint_sprite(body, F, grey, wall_steps=-1, keep=lambda val: val >> 4 == 0, default=grey(0x04),
                     under=grey(0x02))
    kit.merge_bottom(body)
    # The seams on the dome: a raised Y from the panel at its top down to the knob.
    seam = pal("hseam", 0x09, metallic=0.45, roughness=0.3)

    def surf(x, y):
        return shell_h(*cr(x, y))
    for i, path in enumerate((
            [(30.0, 12.2), (30.1, 15.5), (30.3, 18.6), (27.0, 18.6), (24.4, 18.8), (22.4, 21.2), (20.6, 24.2)],
            [(30.2, 14.4), (34.0, 14.3), (37.6, 14.4), (40.4, 16.0), (40.6, 18.6), (40.4, 21.2), (36.8, 23.2)],
            [(30.8, 19.0), (32.8, 21.2), (34.6, 23.2), (34.6, 27.0), (34.6, 31.0), (34.6, 35.0)])):
        pts = [P(c, r)[:2] for c, r in path]
        kit.groove(f"hseam{i}", pts, surf, seam, radius=0.5, sink=0.12)


def brows():
    red = Painter("hbrow", shades={4: (1, 2, 3, 4, 5, 6, 7, 8, 9, 0xa, 0xb, 0xd, 0xf)}, metallic=0.12, roughness=0.2)
    for side, (c0, c1) in (("l", (0, 31)), ("r", (40, 72))):
        polys = kit.outlines_of(F, lambda val, c, r: val >> 4 == 4 and c0 <= c < c1 and 23 <= r <= 41 and
                                (r <= 36 or c < 10 or c > 61), smooth=2,
                                epsilon=0.3, grow=0.35)

        def z_fn(x, y, z):
            c, r = cr(x, y)
            base = kit.smax(dome_h(c, r) - 1.4, 8.0, 2.5)
            return base + z
        brow = kit.relief(f"hbrow_{side}", polys, red(0x45), sh.round_profile(0.8, max_height=5.4), bottom=0.0,
                          base=0.0, rim=0.3, spacing=0.7, z_fn=z_fn, angle=55)
        kit.paint_sprite(brow, F, red, wall_steps=-2, keep=lambda val: val >> 4 == 4, default=red(0x43), blur=1,
                         probe=-0.5)
        kit.merge_bottom(brow)
        # The small pads under the brows' outer ends.
        polys = kit.outlines_of(F, lambda val, c, r: val >> 4 == 4 and c0 <= c < c1 and 42 <= r <= 47 and
                                (c < 20 or c > 50), smooth=2, epsilon=0.3, grow=0.3)
        pad = kit.relief(f"hbrow_pad_{side}", polys, red(0x44), sh.round_profile(0.7, max_height=2.6), bottom=0.0,
                         base=0.0, rim=0.2, spacing=0.6, z_fn=lambda x, y, z: z + FLOOR + 0.6, angle=55)
        kit.paint_sprite(pad, F, red, wall_steps=-2, keep=lambda val: val >> 4 == 4, default=red(0x43), blur=1,
                         probe=-0.5)
        kit.merge_bottom(pad)


def slots():
    """Black pipes lying in the slots under the brows, a ring round each."""
    black = Painter("hpipe", shades={0: (2,)}, metallic=0.5, roughness=0.22)
    ring = pal("hpipe_ring", 0x05, metallic=0.55, roughness=0.3)
    for side in (-1, 1):
        def C(c):
            return c if side < 0 else 2 * AX - c
        for i, (ca, cb, r, rad) in enumerate(((4.0, 27.5, 39.6, 2.1), (16.5, 28.0, 44.3, 1.8))):
            a, b = P(C(ca), r, FLOOR + rad * 0.75), P(C(cb), r, FLOOR + rad * 0.75)
            length = (Vector(b) - Vector(a)).length
            kit.lathe_axis(f"hpipe{side:+d}_{i}", [(-0.6, rad * 0.4), (-0.35, rad * 0.85), (0.0, rad), (length, rad),
                                                    (length + 0.35, rad * 0.85), (length + 0.6, rad * 0.4)],
                           black(0x02), a, tuple(Vector(b) - Vector(a)), 12)
            mid = Vector(a).lerp(Vector(b), 0.55)
            band = kit.band_y(f"hpipe_ring{side:+d}_{i}", (0.0, 0.0, 0.0), rad + 0.15, 0.45, ring, 16, 6)
            band.data.transform(Matrix.Translation(mid) @ Matrix.Rotation(math.radians(90), 4, "Z"))


def knob():
    steel = Painter("hknob", shades={0: (1, 2, 3, 4, 5, 6, 7, 8, 9, 0xa, 0xb, 0xc)}, metallic=0.55, roughness=0.22)
    ball = kit.sphere("hknob", P(AX, 41.6, 15.4), (7.6, 6.2, 6.3), steel(0x07), 26, 13)
    kit.paint_sprite(ball, F, steel, wall_steps=-1, keep=lambda val: val >> 4 == 0, default=steel(0x04), blur=1,
                     probe=-0.6)
    # A collar where it leaves the dome.
    collar = pal("hknob_collar", 0x03, metallic=0.5, roughness=0.35)
    kit.torus("hknob_collar", P(AX, 41.0, 12.6), 7.0, 0.9, collar, 28, 6, squash=0.8)


def bulbs():
    red = Painter("hbulb", shades={4: (1, 2, 3, 4, 5, 6, 7, 8, 9, 0xa, 0xb, 0xd, 0xf)}, metallic=0.1, roughness=0.16)
    socket = pal("hbulb_socket", 0x01, metallic=0.4, roughness=0.45)
    for i, b in enumerate(BULBS):
        bc, br, rx, ry, turn = b
        x, y, _ = P(bc, br)
        surface = plate_h(bc, br, dents=False)
        rz = 3.9
        obj = kit.bulb(f"hbulb{i}", (x, y, surface - 0.9 - rz * 0.25), (rx, ry, rz), red(0x46), segments=24, rings=12,
                       angle=-turn)
        kit.paint_sprite(obj, F, red, wall_steps=-1, keep=lambda val: val >> 4 == 4, default=red(0x43), blur=1,
                         probe=-0.6)
        # A dark rim round the socket.
        pts = []
        for j in range(32):
            t = 2 * math.pi * j / 32
            u, v = (rx + 0.9) * math.cos(t), (ry + 0.9) * math.sin(t)
            a = math.radians(turn)
            c = bc + u * math.cos(a) - v * math.sin(a)
            r = br - (u * math.sin(a) + v * math.cos(a))
            pts.append(P(c, r)[:2])
        kit.ring_on(f"hbulb_rim{i}", pts, lambda x, y: plate_h(*cr(x, y)), -0.25, 0.55, socket, 8)


def head_whole():
    shell()
    brows()
    slots()
    knob()
    bulbs()
    kit.flatten_under(kit.meshes(), 0.0)


# The pieces: (sprite, its top left pixel in the whole, the pixel box it keeps).
PIECES = [
    (10, 12, 0, (12, 36, 0, 28)), (12, 36, 0, (36, 60, 0, 28)),
    (28, 0, 14, (0, 12, 14, 28)), (32, 48, 14, (60, 72, 14, 28)),
    (47, 0, 28, None), (49, 24, 28, None), (51, 48, 28, None),
    (85, 0, 56, None), (87, 24, 56, None), (89, 48, 56, None),
]

kit.PROTECT += ["hshell", "hbrow", "hbulb"]
kit.pieced("dome_head", head_whole, (72, 84), [kit.piece(f"dome_head_{s}", F, c0, r0, keep)
                                                for s, c0, r0, keep in PIECES])


if __name__ == "__main__":
    kit.run()
