"""DREAD-NOT's shoulders and bladed shell (wave 3, batch AJ; sheet 9), modelled as their sprites look (models.cfg:
yaw=0); the rest of the sheet is in wave3_aj.py, wave3_aj_head.py, wave3_aj_eye.py and wave3_aj_capsule.py, the
kit in wave3_aj_kit.py, the pixels in wave3_aj_art.py.

At DREAD-NOT's start the level puts a machine together on the ground from the head of wave3_aj_head.py (enemies
309-318 at x 130-202), the anchors of wave2_e_parts.py, these two shoulders over the head's dome and this shell
under its jaw; the shoulders and the shell are "ground 2" enemies, drawn over the head:

- dread_shoulder_l_<sprite> (9 77, 79 above 115, 117; enemies 434-437 at (120, -80) .. (144, -52)), 48 x 56, and
  dread_shoulder_r_<sprite> (9 81, 83 above 119, 121; enemies 438-441 at (162, -80) .. (186, -52)), its mirror
  image: a tall rounded shoulder cap with a raised square plate on top, and under it an armoured arm reaching
  down and out, four glossy red bulbs set in it and a white lamp at its end. The arm lies over the head's dome
  (24 rows of it), so its underside follows the dome: it is built standing on the ground and draped over the
  head as the level places them (the head from wave3_aj_head.py's heights).
- dread_shell_<sprite> (9 159-165 above 197-203, odd; enemies 442-445 above 446-449, x 118-214), 96 x 56: two
  domed shells at the top, three curved blades fanning out under each, their points down and out, and between
  them a broad segmented plate round a notch at its top (where the head's jaw shows through).

usage: Blender -b --factory-startup -P wave3_aj_dread.py -- [--only name,name] [--preview <prefix>] [--check 1]
       [--stats 1] [--whole <prefix>]
"""
import math
import os
import sys

import numpy as np
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_aj_kit as kit  # noqa: E402
from wave3_aj_kit import k, sh, pal, Painter, smoothstep  # noqa: E402
import wave3_aj_head as hd  # noqa: E402

# Only the head's heights are wanted here, not its pieces.
kit.n.OBJECTS[:] = [o for o in kit.n.OBJECTS if o[0] != "dome_head"]

SHOULDER_L = kit.frame("SHOULDER_L", 48, (24, 28))
SHOULDER_R = kit.frame("SHOULDER_R", 48, (24, 28))
GAP = 3.2   # the arm's thickness over the head


# --- The head under the shoulders ----------------------------------------------------------------------------

def _head_field():
    """The head's top (its shell, the brows) over its pixels on a half-pixel grid, spread out a little and
    smoothed (what the shoulders rest on)."""
    step = 0.5
    cs = np.arange(-6.0, 78.0, step)
    rs = np.arange(-6.0, 90.0, step)
    hf = np.zeros((len(rs), len(cs)))
    for j, r in enumerate(rs):
        for i, c in enumerate(cs):
            val = hd.F.get(int(math.floor(c)), int(math.floor(r)))
            if val is None:
                continue
            z = hd.shell_h(c, r)
            if val >> 4 == 4 and 23 <= r <= 41:
                z = max(z, kit.smax(hd.dome_h(c, r) - 1.4, 8.0, 2.5) + 4.6)
            hf[j, i] = z
    # Spread by 1.5 pixels (a max over a disc), then smoothed.
    out = hf.copy()
    reach = 3
    for dj in range(-reach, reach + 1):
        for di in range(-reach, reach + 1):
            if dj * dj + di * di <= reach * reach:
                out = np.maximum(out, np.roll(np.roll(hf, dj, 0), di, 1))
    for _ in range(3):
        out = (out + np.roll(out, 1, 0) + np.roll(out, -1, 0) + np.roll(out, 1, 1) + np.roll(out, -1, 1)) / 5.0
    return cs, rs, out


_HEAD = None


def head_top(c, r):
    """The head's (smoothed) top at its pixel coordinates (0 off it)."""
    global _HEAD
    if _HEAD is None:
        _HEAD = _head_field()
    cs, rs, hf = _HEAD
    i = (c - cs[0]) / 0.5
    j = (r - rs[0]) / 0.5
    if not (0 <= i < len(cs) - 1 and 0 <= j < len(rs) - 1):
        return 0.0
    i0, j0 = int(i), int(j)
    fi, fj = i - i0, j - j0
    return (hf[j0, i0] * (1 - fi) * (1 - fj) + hf[j0, i0 + 1] * fi * (1 - fj) + hf[j0 + 1, i0] * (1 - fi) * fj +
            hf[j0 + 1, i0 + 1] * fi * fj)


# --- The shoulders -------------------------------------------------------------------------------------------

# In the left shoulder's pixels (u column, v row); the head's pixel is (u - 10, v - 24).
CAP = [(32.0, 5.0), (44.2, 5.0), (45.9, 7.0), (45.9, 22.6), (44.4, 24.8), (31.0, 25.4), (25.0, 24.0), (20.6, 21.0),
       (19.8, 15.0), (23.4, 10.2), (29.0, 6.0)]
CAP_TOP = 22.5
SPINE = [(31.0, 24.0), (26.0, 30.5), (23.5, 37.5), (20.0, 44.5), (15.0, 50.0), (11.0, 52.0)]
SH_BULBS = [  # (u, v, radius across, along, turn)
    (8.9, 29.6, 4.3, 4.9, 30.0), (22.0, 29.4, 3.8, 3.4, 0.0), (36.8, 32.9, 6.4, 4.9, 10.0), (28.2, 44.0, 4.3, 4.9, 25.0),
]
LAMP = (11.6, 46.9)


def arm_own(u, v):
    """The arm's own height: a rounded limb along its spine, rising to the cap."""
    d = kit.path_dist(u, v, SPINE)
    z = 8.6 + 6.0 * max(0.0, 1.0 - (d / 10.0) ** 2)
    z += 5.0 * (1.0 - smoothstep(20.0, 30.0, v)) * smoothstep(14.0, 24.0, u)
    return z


def arm_h(u, v):
    under = head_top(u - 10.0, v - 24.0)
    z = arm_own(u, v)
    if under > 0.0:
        z = kit.smax(z, under + GAP, 3.0)
    return z


def shoulder_whole(side):
    """The shoulder of `side` (-1 left, 1 right: the left one mirrored, a pixel to the right), painted by its own
    sprite."""
    f = SHOULDER_L if side < 0 else SHOULDER_R

    def X(u):
        x = u - 24.0
        return x if side < 0 else 1.0 - x

    def uv(x, y):
        return (x + 24.0 if side < 0 else 25.0 - x), 28.0 - y

    def M(u, v, z=0.0):
        return (X(u), 28.0 - v, z)

    grey = Painter("dsh", shades={0: (1, 2, 3, 4, 5, 6, 7, 8, 9, 0xa, 0xb, 0xc, 0xd)}, metallic=0.45, roughness=0.34,
                   remap={0xfe: 0x01})
    red = Painter("dsh_bulb", shades={4: (1, 2, 3, 4, 5, 6, 7, 8, 9, 0xa, 0xb, 0xd)}, metallic=0.1, roughness=0.16)
    # The arm: the whole outline, draped over the head.
    left_f = SHOULDER_L
    polys = kit.outlines_of(left_f, lambda val, c, r: True, smooth=2, epsilon=0.35)
    if side > 0:
        polys = [[(1.0 - x, y) for x, y in reversed(p)] for p in polys]

    def z_of(x, y, e):
        u, v = uv(x, y)
        return 1.0 + (arm_h(u, v) - 1.0) * e
    arm = kit.heightfield(f"dsh_arm{side:+d}", polys, z_of, grey(0x05), spacing=1.0, edge=2.4)
    k.smooth(arm, 45)
    kit.pixelate(arm, f)
    kit.paint_sprite(arm, f, grey, wall_steps=-1, keep=lambda val: val >> 4 == 0, default=grey(0x04),
                     under=grey(0x02))
    # Its steep sides (where it drops off the head) one dark steel.
    kit.paint_faces(arm, lambda c, nrm: grey(0x03) if nrm.z < 0.35 else None)
    kit.merge_bottom(arm)
    # The cap: a tall rounded block, a raised square plate on its top.
    cap_poly = [M(u, v)[:2] for u, v in CAP]
    if side > 0:
        cap_poly = cap_poly[::-1]
    cap = kit.relief(f"dsh_cap{side:+d}", [cap_poly], grey(0x06), sh.pillow_profile(CAP_TOP - 1.0, 4.2, crown=1.2),
                     bottom=0.0, base=0.0, rim=1.0, spacing=1.0, angle=45)
    kit.pixelate(cap, f)
    kit.paint_sprite(cap, f, grey, wall_steps=-1, keep=lambda val: val >> 4 == 0, default=grey(0x05),
                     under=grey(0x02))
    kit.merge_bottom(cap)
    x0, x1 = sorted((X(36.0), X(43.6)))
    y0, y1 = 28.0 - 19.2, 28.0 - 12.6
    plate = kit.rounded_box(f"dsh_plate{side:+d}", ((x0 + x1) / 2, (y0 + y1) / 2, CAP_TOP + 0.6),
                            (x1 - x0, y1 - y0, 1.8), grey(0x08), bevel=0.5)
    sh.apply_modifiers(plate)
    kit.paint_sprite(plate, f, grey, wall_steps=-1, keep=lambda val: val >> 4 == 0, default=grey(0x07), blur=1)
    # The red bulbs, set in the arm (or under the cap's edge).
    socket = pal("dsh_socket", 0x01, metallic=0.4, roughness=0.45)
    for i, (u, v, rx, ry, turn) in enumerate(SH_BULBS):
        surf = arm_h(u, v) if i != 2 else arm_h(u, v) + 1.0
        rz = min(rx, ry) * 0.8
        b = kit.bulb(f"dsh_bulb{side:+d}_{i}", (X(u), 28.0 - v, surf - 0.4), (rx, ry, rz), red(0x45), segments=24,
                     rings=12, angle=turn if side < 0 else -turn)
        kit.paint_sprite(b, f, red, wall_steps=-1, keep=lambda val: val >> 4 == 4, default=red(0x43), blur=1,
                         probe=-0.6)
        kit.torus(f"dsh_socket{side:+d}_{i}", (X(u), 28.0 - v, surf - 0.1), max(rx, ry) * 0.95, 0.65, socket, 32, 8,
                  squash=0.8)
        obj = kit.meshes()[-1]
        s = (rx / max(rx, ry), ry / max(rx, ry))
        cx, cy = X(u), 28.0 - v
        a = math.radians(turn if side < 0 else -turn)
        obj.data.transform(Matrix.Translation((cx, cy, 0)) @ Matrix.Rotation(a, 4, "Z") @
                           Matrix.Diagonal((s[0], s[1], 1.0, 1.0)) @ Matrix.Rotation(-a, 4, "Z") @
                           Matrix.Translation((-cx, -cy, 0)))
    # The white lamp at the arm's end.
    lamp = pal("dsh_lamp", 0x0e, metallic=0.1, roughness=0.1, glow=1.2)
    u, v = LAMP
    kit.sphere(f"dsh_lamp{side:+d}", M(u, v, arm_h(u, v) - 0.3), (1.7, 1.6, 1.3), lamp, 16, 8)
    kit.flatten_under(kit.meshes(), 0.0)


# --- The bladed shell ---------------------------------------------------------------------------------------

SHELL = kit.frame("CRAB", 96, (48, 28))
SHELL_AXIS = 48.25   # its middle (pixel column); the right half is the left one mirrored about it
# The left half's plates (pixel columns, rows): the dome, the three blades under it (the first under the dome's
# rim, each further one lower and further down, their points down and out), and the plate in the middle
# (both halves).
DOME = [(8.0, 10.0), (12.0, 6.0), (18.0, 4.2), (30.0, 4.2), (36.0, 6.0), (40.0, 9.0), (41.6, 14.0), (41.2, 20.0),
        (39.8, 25.0), (37.4, 27.8), (33.5, 25.6), (28.0, 22.2), (20.0, 20.2), (12.0, 18.6), (5.0, 17.6), (3.4, 15.0),
        (5.0, 12.0)]
BLADES = [  # (outline, height): generous, the sprite's pixels and the plates above them trim them
    ([(-2.0, 10.0), (10.0, 12.0), (24.0, 14.0), (36.0, 18.0), (42.0, 26.0), (40.0, 31.0), (33.0, 31.4),
      (24.0, 28.8), (16.0, 27.4), (10.0, 28.4), (6.2, 31.4), (3.6, 35.6), (-2.0, 36.0)], 10.5),
    ([(-2.0, 30.0), (8.0, 26.0), (16.0, 25.0), (24.0, 26.0), (34.0, 28.0), (33.4, 37.0), (26.0, 37.8), (18.0, 37.4),
      (12.6, 40.0), (8.6, 44.0), (6.8, 50.0), (-2.0, 50.0)], 8.6),
    ([(2.0, 40.0), (14.0, 34.0), (24.0, 34.0), (31.0, 36.0), (29.0, 40.0), (27.4, 44.2), (22.4, 48.2), (19.0, 49.4),
      (15.4, 50.6), (14.0, 57.0), (2.0, 57.0)], 6.8),
]
PLATE = [(25.6, 40.4), (29.6, 36.2), (34.0, 33.0), (38.4, 31.6), (42.6, 33.2), (44.4, 34.4), (48.25, 33.8)]
PLATE_BOTTOM = [(48.25, 58.0), (40.0, 58.0), (30.0, 54.0), (25.0, 48.6), (24.0, 44.0)]


def mirrored(poly):
    return [(2 * SHELL_AXIS - c, r) for c, r in poly]


def plate_outline():
    left = PLATE + PLATE_BOTTOM
    # The right half: the left one mirrored (without the points on the axis twice), going round.
    right = [(2 * SHELL_AXIS - c, r) for c, r in reversed(PLATE[:-1])]
    right_bottom = [(2 * SHELL_AXIS - c, r) for c, r in reversed(PLATE_BOTTOM[1:])]
    return PLATE + right + right_bottom + PLATE_BOTTOM


def shell_whole():
    f = SHELL
    grey = Painter("dshell", shades={0: (1, 2, 3, 4, 5, 6, 7, 8, 9, 0xa, 0xb, 0xc, 0xd, 0xe, 0xf)}, metallic=0.45,
                   roughness=0.32)

    def paint(obj, wall=-1):
        kit.pixelate(obj, f)
        kit.paint_sprite(obj, f, grey, wall_steps=wall, default=grey(0x03), under=grey(0x01))
        kit.merge_bottom(obj)

    # A low dark base over the whole outline (nothing shows through between the plates).
    polys = kit.outlines_of(f, lambda val, c, r: True, smooth=2, epsilon=0.35)
    base = kit.heightfield("dbase_shell", polys, lambda x, y, e: 0.6 + 2.8 * e, grey(0x02), spacing=1.0, edge=1.5)
    kit.merge_flat(base, 1.0)
    # Each pixel goes to the first plate whose outline holds it: the domes, the middle plate, then the blades
    # from the top down.
    regions = [("dome", -1, DOME), ("dome", 1, mirrored(DOME)), ("plate", 0, plate_outline())]
    for i, (points, _h) in enumerate(BLADES):
        regions += [(f"blade{i}", -1, points), (f"blade{i}", 1, mirrored(points))]
    owner = {}
    for rr in range(f.height):
        for cc in range(f.width):
            if f.get(cc, rr) is None:
                continue
            for j, (_n, _s, pts) in enumerate(regions):
                if kit.inside(pts, cc + 0.5, rr + 0.5):
                    owner[(cc, rr)] = j
                    break

    def region_polys(j):
        return kit.outlines_of(f, lambda val, c, r: owner.get((c, r)) == j, smooth=2, epsilon=0.3)

    for side in (-1, 1):
        k_ = 0 if side < 0 else 1
        # The dome: highest towards its lit right shoulder.
        dc = (24.0, 13.0) if side < 0 else (2 * SHELL_AXIS - 24.0, 13.0)

        def dome_z(x, y, z, dc=dc, side=side):
            c, r = x + f.ox, f.oy - y
            lean = 1.0 + 0.12 * ((c - dc[0]) * (-side) / 18.0)
            return 0.8 + z * max(0.6, lean)
        dome = kit.relief(f"dshell_dome{side:+d}", region_polys(k_), grey(0x07), sh.round_profile(1.25, max_height=16.5),
                          bottom=0.0, base=0.0, rim=0.8, spacing=1.0, z_fn=dome_z, sigma=1.6, angle=45)
        paint(dome)
        # The blades, each lower, their points bending down.
        for i, (points, height) in enumerate(BLADES):
            def blade_z(x, y, z, side=side, height=height):
                c = x + f.ox
                u = c if side < 0 else 2 * SHELL_AXIS - c
                droop = 1.0 - 0.38 * smoothstep(26.0, 2.0, u)
                return (0.8 + z) * droop
            blade = kit.relief(f"dshell_blade{side:+d}_{i}", region_polys(3 + 2 * i + k_), grey(0x05),
                               sh.pillow_profile(height - 1.2, 2.6, crown=0.9), bottom=0.0, base=0.0, rim=0.6,
                               spacing=1.0, z_fn=blade_z, angle=45)
            paint(blade)
    # The middle plate: a broad shield, highest in its middle.
    plate = kit.relief("dshell_plate", region_polys(2), grey(0x06),
                       sh.pillow_profile(9.0, 4.0, crown=3.0), bottom=0.0, base=0.0, rim=0.8, spacing=1.0, angle=45)
    paint(plate)
    kit.flatten_under(kit.meshes(), 0.0)


kit.PROTECT += ["dshell"]
kit.pieced("dread_shell", shell_whole, (96, 56),
           [kit.piece(f"dread_shell_{s}", SHELL, c0, r0) for s, (c0, r0) in
            zip((159, 161, 163, 165, 197, 199, 201, 203), [(24 * i, 0) for i in range(4)] + [(24 * i, 28) for i in range(4)])])


kit.PROTECT += ["dsh_arm", "dsh_cap", "dsh_bulb"]
for _side, _tag, _sprites in ((-1, "l", (77, 79, 115, 117)), (1, "r", (81, 83, 119, 121))):
    _f = SHOULDER_L if _side < 0 else SHOULDER_R
    kit.pieced(f"dread_shoulder_{_tag}", (lambda s=_side: shoulder_whole(s)), (48, 56),
               [kit.piece(f"dread_shoulder_{_tag}_{s}", _f, c0, r0)
                for s, (c0, r0) in zip(_sprites, ((0, 0), (24, 0), (0, 28), (24, 28)))])


if __name__ == "__main__":
    kit.run()
