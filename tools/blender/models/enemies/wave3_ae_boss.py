"""FRUIT's boss (wave 3, batch AE; sheet ', written x27 in models.cfg), modelled as its sprites look (models.cfg:
yaw=0); the rest of the sheet is in wave3_ae.py, wave3_ae_lemon.py and wave3_ae_coral.py, the kit in
wave3_ae_kit.py, the pixels in wave3_ae_art.py.

The level draws it from 31 sprites on the ground (enemies 1265-1295): four rows of eight (' 153-167, 191-205,
229-243, odd) from (x, y), then five (' 270-278, even) from (x + 36, y + 84), then two (' 281, 283) from
(x + 72, y + 112); 192 x 140 pixels. Built whole, cut into its sprites (pineapple_<sprite>, origin):

- a giant pineapple in the middle, its skin in raised diamond scales with darker creases, a tall black glass
  window down its front with a pale glowing shape inside it, its green crown fanning out under it (down the
  screen);
- behind it a broad grey wing plate with bevelled edges and panel lines, a lemon slice glowing in a round socket
  on each side;
- at each side a tan pylon standing on the wing, a rod hanging under it, three ribbed steel bolts from it into
  the pineapple, two yellow banana claws between them hugging the pineapple and a bigger one under each side of
  it.

It stands on the ground (z = 0), the pineapple rising about 34 pixels.

usage: Blender -b --factory-startup -P wave3_ae_boss.py -- [--only name,name] [--preview <prefix>]
       [--check 1] [--stats 1] [--whole <prefix>]
"""
import math
import os
import sys

import bmesh
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_ae_kit as kit  # noqa: E402
from wave3_ae_kit import k, sh, w, pal, Painter  # noqa: E402

BOSS = kit.frame("BOSS", 192, (96, 70))
F = BOSS

# The pineapple (an ellipsoid; its top is cut off by the sprite's top edge), the wing plate's top.
PINE_C, PINE_R = Vector((0.0, 20.0, 2.0)), (40.0, 54.0, 32.0)
WING_TOP = 6.0
SCALE = 10.0  # the diamond scales' size (pixels, across)


def P(c, r, z=0.0):
    """A point at continuous pixel coordinates (column, row) of the whole."""
    return (c - F.ox, F.oy - r, z)


def ramp_pixels(keep, c0=0, c1=192, r0=0, r1=140):
    return [(c, r) for r in range(r0, min(r1, F.height)) for c in range(c0, c1)
            if F.get(c, r) is not None and keep(F.get(c, r))]


def centroid(pixels):
    n = max(1, len(pixels))
    return (sum(c for c, _ in pixels) / n + 0.5, sum(r for _, r in pixels) / n + 0.5)


def pine_z(x, y):
    """The height of the pineapple's smooth skin over (x, y)."""
    cx, cy, cz = PINE_C
    rx, ry, rz = PINE_R
    q = 1.0 - ((x - cx) / rx) ** 2 - ((y - cy) / ry) ** 2
    return cz + rz * math.sqrt(q) if q > 0 else None


def scale_height(x, y):
    """0 in the creases between the diamond scales, 1 on their middles."""
    a = (x + y) / SCALE
    b = (x - y) / SCALE
    return (abs(math.sin(math.pi * a)) * abs(math.sin(math.pi * b))) ** 0.6


# --- The wing plate and its lamps ---------------------------------------------------------------------------

def wing():
    grey = Painter("pwing", shades={0: (1, 2, 3, 4, 5, 6, 7, 8, 9, 0xa, 0xb, 0xc, 0xd)}, metallic=0.35, roughness=0.4)
    # Its outline, from the sprite's left half (mirrored): the top edge, the outer edge, the bevelled lower
    # edge running in to under the pylon; behind the pineapple it runs straight across.
    corners = [(1.0, 3.0), (191.0, 3.0), (192.0, 4.5), (192.0, 54.6), (189.5, 56.6), (152.0, 74.6), (149.0, 76.6),
               (132.0, 80.0), (60.0, 80.0), (43.0, 76.6), (40.0, 74.6), (2.5, 56.6), (0.0, 54.6), (0.0, 4.5)]
    outline = [(c - F.ox, F.oy - r) for c, r in corners]
    plate = kit.relief("pwing", [outline], grey(0x07), sh.pillow_profile(WING_TOP - 1.4, 2.4, crown=0.0), bottom=0.0,
                       base=0.0, rim=1.4, spacing=1.0, flat=True)
    kit.pixelate(plate, F)
    kit.paint_sprite(plate, F, grey, wall_steps=-2, keep=lambda val: val >> 4 == 0, default=grey(0x06),
                     under=grey(0x02))
    kit.merge_flat(plate)
    # The lamps: lemon slices in round sockets.
    socket = pal("pwing_socket", 0x04, metallic=0.5, roughness=0.35)
    lamps = []
    for side in (-1, 1):
        pix = ramp_pixels(lambda val: val >> 4 == 7, 0 if side < 0 else 150, 42 if side < 0 else 192, 15, 40)
        c, r = centroid(pix)
        x, y, _ = P(c, r)
        kit.torus(f"pwing_socket{side:+d}", (x, y, WING_TOP + 0.4), 9.6, 1.5, socket, 48, 10, squash=0.8)
        kit.lemon_slice(f"pwing_lamp{side:+d}", x, y, WING_TOP + 0.9, 8.6, 0.0, glow=1.2)
        lamps.append((x, y))
    return lamps


# --- The pylons, rods, bolts and claws -------------------------------------------------------------------

def pylons():
    pylon_shade = BOSS.shade((1,), 2)
    tan = Painter("ppylon", shades={1: (4, 6, 8, 9, 0xa, 0xb, 0xc, 0xd), 0xa: (4, 6, 8, 0xa, 0xc)}, metallic=0.25,
                  roughness=0.4)
    steel = pal("pbolt", 0x0b, metallic=0.55, roughness=0.28)
    steel_dark = pal("pbolt_dark", 0x05, metallic=0.6, roughness=0.35)
    banana = Painter("pclaw", shades={7: (0xa, 0xb, 0xc, 0xd, 0xe)}, metallic=0.1, roughness=0.3)
    for side in (-1, 1):
        def X(c):
            return (c - F.ox) if side < 0 else (F.ox - c)
        # The pylon: a tall rounded block on the wing.
        x0, x1 = X(40.0), X(64.0)
        y0, y1 = F.oy - 80.5, F.oy - 26.0
        block = w.block(f"ppylon{side:+d}", ((x0 + x1) / 2, (y0 + y1) / 2), abs(x1 - x0) / 2, (y1 - y0) / 2, 17.0,
                        tan(0x19), taper=0.6, rounding=2.2, power=5.0, segments=64, z0=0.0, dome=0.8)
        # Painted by the shades of the sprite's visible strip of pylon (columns 41-55), smoothed.
        xa, xb = sorted((X(41.0), X(55.0)))

        def paint(c, nrm, xa=xa, xb=xb):
            s_ = pylon_shade(min(xb, max(xa, c.x)), c.y)
            if nrm.z < 0.45:
                s_ -= 2.0
            return tan(0x10 + max(3, min(13, int(round(s_)))))
        kit.paint_faces(block, paint)
        # The rod under it, its end rounded.
        rx = X(50.0)
        rod = kit.lathe_axis(f"ppylon_rod{side:+d}", [(0.0, 3.0), (14.0, 3.0), (18.5, 2.8), (20.2, 2.0), (21.0, 0.4)],
                             tan(0x19), (rx, F.oy - 78.0, 7.0), (0, -1, 0), 20)
        kit.paint_sprite(rod, F, tan, wall_steps=-2, keep=lambda val: val >> 4 in (1, 0xa), default=tan(0x18),
                         blur=1, probe=-0.6)
        # Three ribbed bolts from the pylon into the pineapple.
        for j, row in enumerate((29.8, 53.8, 77.8)):
            y = F.oy - row
            length = 22.0
            profile = []
            for i in range(41):
                t = length * i / 40
                profile.append((t, 3.5 + 0.6 * math.cos(2 * math.pi * t / 4.3)))
            profile.append((length + 0.5, 2.0))
            start = (X(51.5), y, 19.0)
            bolt = kit.lathe_axis(f"pbolt{side:+d}_{j}", profile, steel, start, (-side, 0, 0), 20, squash=1.0)
            kit.paint_faces(bolt, lambda c, nrm: steel_dark if nrm.z < -0.25 else None)
        # The claws between the bolts, hugging the pineapple: bananas bulging outwards.
        for j, (r0, r1) in enumerate(((34.0, 49.5), (58.0, 73.5))):
            pts = [(X(60.5), F.oy - r0, 18.6), (X(58.6), F.oy - (r0 + r1) / 2 + 2.0, 19.6),
                   (X(58.6), F.oy - (r0 + r1) / 2 - 2.0, 19.6), (X(60.5), F.oy - r1, 18.6)]
            claw = kit.limb(f"pclaw{side:+d}_{j}", pts, [1.4, 3.7, 3.7, 1.4], banana(0x7c), segments=14, squash=0.8)
            kit.paint_sprite(claw, F, banana, wall_steps=-1, keep=lambda val: val >> 4 == 7, default=banana(0x7b),
                             probe=-0.8)
        # The big claws under the pineapple's sides, curving down to their tips.
        path = [(68.4, 87.5, 11.0), (69.5, 92.0, 9.5), (71.0, 95.5, 8.0), (72.6, 99.5, 6.5), (74.2, 102.5, 5.2),
                (76.2, 104.6, 4.2), (78.4, 106.6, 3.4)]
        pts = [(X(c), F.oy - r, z) for c, r, z in path]
        claw = kit.limb(f"pclaw_big{side:+d}", pts, [2.6, 2.9, 3.4, 3.4, 2.8, 1.8, 0.4], banana(0x7c), segments=14,
                        squash=0.8)
        kit.paint_sprite(claw, F, banana, wall_steps=-1, keep=lambda val: val >> 4 == 7, default=banana(0x7b),
                         probe=-0.8)


# --- The pineapple, its window and its crown --------------------------------------------------------------

def window_halfwidth():
    """The window's half-width row by row (from the sprite's grey pixels in the pineapple's middle), smoothed:
    {row: (centre x, half-width)}."""
    rows = {}
    for r in range(18, 96):
        cols = [c for c in range(78, 116) if F.get(c, r) is not None and F.get(c, r) >> 4 == 0]
        if len(cols) >= 2:
            rows[r] = ((min(cols) + max(cols) + 1) / 2 - F.ox, (max(cols) - min(cols) + 1) / 2)
    out = {}
    for r in rows:
        near = [rows[q] for q in range(r - 2, r + 3) if q in rows]
        out[r] = (sum(v[0] for v in near) / len(near), sum(v[1] for v in near) / len(near))
    return out


def pineapple():
    skin = Painter("pskin", shades={1: (1, 2, 3, 4, 5, 6, 7, 8, 9, 0xa, 0xb, 0xc), 0xb: (1, 2, 3, 4, 5, 6, 7, 8, 9, 0xa, 0xb, 0xc),
                                    0xa: (3, 5, 7, 9, 0xb, 0xd)},
                   metallic=0.05, roughness=0.5)
    body = w.sphere("pineapple", tuple(PINE_C), PINE_R, skin(0x14), 176, 110)
    sh.flat_bottom([body], 0.0)
    # The diamond scales: raised in their middles, creased between them.
    for vt in body.data.vertices:
        if vt.co.z < 1.0:
            continue
        h = scale_height(vt.co.x, vt.co.y)
        d = (vt.co - PINE_C)
        nrm = Vector((d.x / PINE_R[0] ** 2, d.y / PINE_R[1] ** 2, d.z / PINE_R[2] ** 2)).normalized()
        vt.co += nrm * (h - 0.55) * 1.3
    body.data.update()
    k.smooth(body, 70)

    # Painted by the sprite's browns (smoothed), the creases darker, the scales' middles lighter.
    shade_at = BOSS.shade((1, 0xb), 2)

    def paint(c, nrm):
        val = F.at(c.x, c.y)
        ramp = val >> 4 if val is not None and val >> 4 in (1, 0xb, 0xa) else 1
        if ramp == 0xa:
            ramp = 1
        s = shade_at(c.x, c.y)
        h = scale_height(c.x, c.y)
        s += -3.2 if h < 0.3 else (-1.2 if h < 0.55 else (0.0 if h < 0.85 else 1.4))
        if nrm.z < -0.3:
            s -= 2
        return skin(ramp * 16 + max(1, min(12, int(round(s)))))
    kit.paint_faces(body, paint)

    # The window: smooth black glass over the scales, as tall and narrow as the sprite's, a pale shape glowing
    # inside it.
    glass = Painter("pglass", shades={0: (1, 2, 3, 4, 5, 7, 9, 0xb, 0xd, 0xe)}, metallic=0.3, roughness=0.06,
                    glow={0x0b: 0.25, 0x0d: 0.45, 0x0e: 0.7})
    win = window_halfwidth()
    lo, hi = min(win), max(win)
    shell = w.sphere("pwindow", tuple(PINE_C), (PINE_R[0] + 1.0, PINE_R[1] + 1.0, PINE_R[2] + 1.0), glass(0x02), 176, 110)
    bm = bmesh.new()
    bm.from_mesh(shell.data)

    def inside(x, y, margin=0.0):
        r = F.oy - y
        ri = int(math.floor(r))
        if ri < lo or ri > hi or ri not in win:
            return False
        cx, hw = win[ri]
        return abs(x - cx) <= hw + margin and pine_z(x, y) is not None
    doomed = [f for f in bm.faces if not inside(f.calc_center_median().x, f.calc_center_median().y)
              or f.calc_center_median().z < PINE_C.z]
    bmesh.ops.delete(bm, geom=doomed, context="FACES")
    bm.to_mesh(shell.data)
    bm.free()
    kit.paint_sprite(shell, F, glass, wall_steps=0, keep=lambda val: val >> 4 == 0, default=glass(0x02), blur=2)
    # A dark rim round it.
    rim = pal("pwindow_rim", 0x12, metallic=0.4, roughness=0.4)
    loop = []
    rows = sorted(win)
    for r in rows:
        cx, hw = win[r]
        loop.append((cx - hw - 0.3, F.oy - r - 0.5))
    for r in reversed(rows):
        cx, hw = win[r]
        loop.append((cx + hw + 0.3, F.oy - r - 0.5))
    pts = []
    for i in range(0, len(loop), 2):
        x, y = loop[i]
        z = pine_z(x, y)
        if z is not None:
            pts.append((x, y, z + 0.7))
    pts.append(pts[0])
    kit.limb("pwindow_rim", pts, [0.9] * len(pts), rim, segments=8, step=0.8)

    # The crown: green leaves from a stem coming out under the pineapple, fanning out down the screen.
    green = pal("pcrown", 0x24, metallic=0.05, roughness=0.45)
    green2 = pal("pcrown2", 0x25, metallic=0.05, roughness=0.45)
    dark = pal("pcrown_dark", 0x22, metallic=0.05, roughness=0.5)

    def stem_z(row):
        y = F.oy - row
        top = pine_z(0.0, y)
        return max((top or 0.0) + 0.6, 3.6 + 0.16 * (137.0 - row))
    rows = [92.0, 96.0, 100.0, 105.0, 110.0, 116.0, 122.0, 128.0, 133.0, 137.0]
    stem = kit.limb("pcrown_stem", [P(96.0, r, stem_z(r)) for r in rows], [0.9, 1.9, 2.0, 1.9, 1.8, 1.6, 1.4, 1.2, 0.9,
                                                                             0.3], green, segments=10, squash=0.7)
    leaves = [stem]
    spec = [(98.0, (80.0, 111.0)), (103.0, (77.0, 117.0)), (108.0, (74.5, 122.5)), (113.0, (72.0, 126.5)),
            (118.0, (77.5, 133.0)), (124.0, (84.0, 136.0)),
            (97.0, (112.0, 107.5)), (102.0, (114.5, 113.0)), (107.0, (116.5, 119.5)), (112.0, (117.5, 126.0)),
            (118.0, (112.5, 132.5)), (124.0, (106.0, 136.0))]
    for i, (row, (tc, tr)) in enumerate(spec):
        side = -1 if tc < 96 else 1
        s0 = Vector(P(96.0 + side * 0.8, row, stem_z(row)))
        tip = Vector(P(tc, tr, 3.0 + 0.06 * (140.0 - tr)))
        mid = (s0 + tip) / 2 + Vector((side * -0.8, 1.2, 1.6))
        leaf = kit.limb(f"pcrown_leaf{i}", [tuple(s0), tuple(s0 + (mid - s0) * 0.5 + Vector((0, 0, 0.6))), tuple(mid),
                                            tuple(tip)], [2.3, 3.1, 2.5, 0.3], green if i % 2 else green2,
                        segments=8, squash=0.4)
        kit.paint_faces(leaf, lambda c, nrm: dark if nrm.z < -0.2 else None)
        leaves.append(leaf)
    kit.join(leaves, "pcrown")


def boss_whole():
    wing()
    pylons()
    pineapple()


# The pieces: four rows of eight, five, two (sprite numbers, their top left pixel in the whole).
PIECES = [(153 + 2 * i, 24 * i, 0) for i in range(8)] + [(191 + 2 * i, 24 * i, 28) for i in range(8)] + \
         [(229 + 2 * i, 24 * i, 56) for i in range(8)] + [(270 + 2 * i, 36 + 24 * i, 84) for i in range(5)] + \
         [(281, 72, 112), (283, 96, 112)]

kit.PROTECT += ["pwing", "pineapple", "pwindow", "pcrown"]
kit.pieced("pineapple", boss_whole, (192, 140), [kit.piece(f"pineapple_{s}", F, c0, r0) for s, c0, r0 in PIECES])


if __name__ == "__main__":
    kit.run()
