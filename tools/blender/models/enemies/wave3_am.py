"""Enemies of wave 3, batch AM (sheet o, written o in models.cfg): the walker of FLEET and STATION and the hatches on
it, modelled as their sprites look (models.cfg: yaw=0). The kit is wave3_am_kit.py, the pixels wave3_am_art.py.

The levels build the walker once each (FLEET at t 5020, STATION at t 3320), on the ground, from the sheet's layout
(192 x 140 pixels: the sheet's pixel (c, r) at the level's (c + 60, r - 112)): custom enemies of bank 19 (events
49, and 52 for the top row 28 ticks later, so that it lands above the second row) for its hull, rows of 24 x 28
sprites: 1-15 (odd) above 39-53 above 77-91, then 118-126 (columns 36-155) and the two feet, enemies 735 (156) and
736 (164); 118 and 126 (the legs' upper halves) have 60 armour and are linked to the feet. Three hatches (enemies
737 and 738: 191 beside 193) lie over the dark panels of its shoulders and of the box at its front, at the sheet's
(8, 42), (135, 42) and (71, 72) (the shoulders' panels are drawn a pixel higher in the hull's art); their frames
(195 197 ... 229 231) roll a shutter up into the dark when they launch their fighters (enemy 703).

- fleet_walker_<sprite> (o 1 ... 164, origin): the walker, a heavy grey machine with blue armour, built whole and cut
  into its 31 sprites' pieces. Two broad shoulder pods, their tops of blue armour plate with a grey strap and
  turrets on their back edges (a box with a short barrel pointing back, a small box with a knob); under the armour
  a deep bay for a hatch, framed in grey; below it the pod's lower body, chamfered at its outer corner, a grille
  and two blue slots in it. Between the pods the head: a raised grey block with vents along its back edge, its
  shoulders sloping down to the pods, blue cheek plates; under it a dark cavity where a great glossy black eye
  sits in a blue horseshoe collar, a thick grey bumper curving under it. Under the bumper a box with a third hatch
  bay, framed in blue. Hydraulic hips with ball joints lead to two legs reaching down the screen: an axle under
  the pod, a strut with pistons, a heavy housing, a round armoured foot with a ringed hub. It stands on z = 0,
  its pods' armour about 29 pixels high, the head 34 (the heights below are stretched by kit.Z_SCALE).
- fleet_hatch_l, fleet_hatch_r (o 191, 193, origin): the hatch: a grey frame round a dark lid with a raised
  stepped plate and vent slits; it sits in the bays (its foot at kit.HATCH_FOOT, the bays' floors just below it).
  The model shows it closed (frame 191); the animation's open frames are not modelled.

usage: Blender -b --factory-startup -P wave3_am.py -- [--only name,name] [--preview <prefix>] [--check 1]
       [--stats 1] [--whole <prefix>]
"""
import math
import os
import sys

from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_am_kit as kit  # noqa: E402
from wave3_am_kit import k, pal, Painter, smoothstep  # noqa: E402

W = kit.frame("WALKER", 192, (96, 70))
WF = kit.frame("WALKER", 192, (96, 70)).fill({0x01, 0x02})   # for painting: the outline gives way to the inside
HATCH = kit.frame("HATCH", 48, (24, 14))
HF = kit.frame("HATCH", 48, (24, 14)).fill({0x01, 0x03})

AX = 95.5          # the walker's middle (continuous column)
POD = 24.0         # the pods' armour
HEAD = 28.5        # the head's top
CAVITY = 8.5       # the cavity's floor round the eye


def P(c, r, z=0.0):
    """A point at continuous pixel coordinates (column, row) of the whole."""
    return (c - W.ox, W.oy - r, z)


def cr(x, y):
    return x + W.ox, W.oy - y


def U(c):
    """The column mirrored onto the left half."""
    return c if c <= AX else 2.0 * AX - c


def pix(c, r):
    """The palette index of the pixel at continuous (c, r) (None: transparent)."""
    return W.get(int(math.floor(c)), int(math.floor(r)))


def pu(pc):
    """A pixel column mirrored onto the left half."""
    return pc if pc <= 95 else 190 - pc


def is_turret_px(pc, r):
    return r <= 19 and pu(pc) <= 62


def is_leg_px(pc, r):
    return r >= 83 and 39 <= pu(pc) <= 58


# --- The hull's heights ----------------------------------------------------------------------------------------

def box_h(c, r, u):
    """The box at the front (rows 68-102) with the middle hatch's bay."""
    if 72.0 <= c < 118.0 and 74.0 <= r < 96.0:
        return kit.BAY_FLOOR
    if r < 73.5:
        if u >= 91.5 and r >= 69.5:
            return 18.2                                   # the neck up to the bumper
        return 16.0 if u >= 84.5 else 14.5
    if r >= 96.0:
        if 92.0 <= c < 99.0 and r >= 100.5:
            return 15.5                                   # the tab under the box
        if 82.0 <= u < 86.0 and 97.0 <= r < 101.0:
            return 19.4                                   # grey blocks
        return 18.4
    return 20.2                                           # the blue frame


def pod_h(c, r, u):
    """The shoulder pod (left half; u the mirrored column)."""
    # The bay for a hatch, under the armour's front edge (a row deeper than the art, for the hatch the level
    # puts a pixel lower).
    if 9.0 <= u < 55.0 and 43.0 <= r < 66.0:
        return kit.BAY_FLOOR
    if r < 43.0 and (u < 57.5 or r < 29.0):
        z = POD - 0.05 * max(0.0, r - 21.0)
        if 41.0 <= u < 48.0 and r < 38.5:
            z += 1.1 * smoothstep(20.5, 22.0, r) * smoothstep(38.5, 37.0, r)    # the grey strap
        elif 48.0 <= u < 49.0 and 21.0 <= r < 38.5:
            z -= 0.8                                                            # the seam beside it
        # The armour's front edge rolls down into the bay.
        z -= 1.4 * smoothstep(40.5, 43.0, r) if u >= 9.0 else 0.0
        # The outer diagonal edge: bevelled.
        s = (r + 0.87 * u - 44.4) / 1.32          # pixels inside the line (5, 40)-(28, 20)
        z -= 4.5 * (1.0 - smoothstep(0.0, 5.5, s)) ** 1.6
        return z
    if u < 9.0 and r < 66.0:
        return 21.6                                       # the left frame
    if u >= 55.0 and r < 66.0:
        # The grey rail down the pod's inner side.
        zr = 22.6 - 0.12 * max(0.0, r - 39.0)
        across = 1.0 - ((u - 57.8) / 3.4) ** 2
        return zr - 3.0 * (1.0 - max(0.0, across)) ** 1.5
    # The lower body.
    z = 20.5
    if 25.0 <= u < 51.0 and 65.0 <= r < 76.0:
        z = 18.6                                          # the grille's well
        v = pix(c, r)
        if v is not None and (v & 15) >= 5 and r >= 67.0:
            z += 0.7                                      # its slats
    elif (30.0 <= u < 34.0 or 38.0 <= u < 42.0) and r >= 76.0:
        z = 19.5                                          # the blue slots
    s = r - u - CHAMFER                                   # the chamfered outer corner
    if s > 0.0:
        z -= 7.5 * min(1.0, s / 10.0) ** 1.2
    return z


CHAMFER = 50.5     # the chamfer's inner edge: r - u


def hull_h(c, r):
    u = U(c)
    # The box at the front.
    if r >= 67.5 and u >= 65.5:
        return box_h(c, r, u)
    # The head: its block, the shoulders sloping down to the pods, the cheeks.
    if r < 20.5 and u >= 62.0:
        z = HEAD - 0.32 * max(0.0, 84.0 - u)
        if 10.5 <= r < 12.0 and u >= 83.5:
            v = pix(c, r)
            if v is not None and (v & 15) <= 2:
                z -= 1.2                                  # the vents
        return max(z, POD)
    if r < 37.0 and u >= 79.0:
        if 80.5 <= u < 88.0 and r >= 24.5:
            return 25.2                                   # the blue cheeks
        return HEAD - 0.06 * max(0.0, r - 20.0)
    if 37.0 <= r < 42.0 and u >= 77.5:
        return 21.0                                       # the collar's band under the head
    # The bumper's bed and the cavity.
    if 52.0 <= r < 68.0 and u >= 69.0:
        return 10.5
    if u >= 69.5 and r >= 21.5 and r < 58.0:
        return CAVITY
    if 21.5 <= r < 29.0 and u >= 69.5:
        return CAVITY
    # The collar's bed (the collar is a part of its own).
    v = pix(c, r)
    if v is not None and v >> 4 in (3, 6, 8, 9) and 57.0 <= u < 80.0 and 29.0 <= r < 63.0:
        return 14.0
    # The hips.
    if (u >= 56.5 and r >= 64.0) or (u >= 61.0 and r >= 56.0):
        z = 11.5
        if v is not None and (v & 15) >= 5:
            z += 1.0
        return z
    return pod_h(c, r, u)


# The pieces' borders in the whole's coordinates (the lower rows' pieces start half a sprite to the right).
CUT_X = tuple(sorted({c - 96.0 for c in range(0, 193, 24)} | {c - 96.0 for c in range(36, 157, 24)}))
CUT_Y = tuple(70.0 - r for r in range(0, 141, 28))


def hull():
    paint = Painter("whull", shades={0: (1, 2, 3, 4, 5, 6, 7, 8, 9, 0xa, 0xc, 0xe), 3: (6, 7, 8, 9, 0xa),
                                     6: (1, 3, 4, 5), 8: (0, 3, 5, 6), 9: (0xe, 0xf)},
                    metallic=0.45, roughness=0.38, finish={3: (0.35, 0.3), 8: (0.35, 0.28), 9: (0.35, 0.25)})
    cells = kit.enclosed(W, lambda v, c, r: not is_turret_px(c, r) and not is_leg_px(c, r))
    polys = kit.cells_polys(W, cells, smooth=3, epsilon=0.45)

    def z_of(x, y, e):
        c, r = cr(x, y)
        z = hull_h(c, r)
        return z - min(2.4, 0.2 * z) * (1.0 - e)
    body = kit.field("whull", polys, z_of, paint(0x05), spacing=0.5, edge=2.0)
    kit.paint_sprite(body, WF, paint, wall_steps=-1, default=paint(0x04), under=paint(0x01))
    kit.paint_walls(body, WF, paint)
    kit.paint_under(body, paint(0x01))

    # The cavity's floor and the beds under the eye, the bumper and the collar's arms lie in the dark or out of
    # sight: one colour (and few triangles).
    def hidden(c, nrm):
        if nrm.z < 0.9 or c.z > 14.2:
            return None
        cc, r = cr(c.x, c.y)
        if U(cc) >= 64.0 and c.z < 11.0 and r < 68.0:
            return paint(0x02)
        if abs(c.z - 14.0) < 0.05:
            return paint(0x36)
        return None
    kit.paint_faces(body, hidden)
    kit.split_at(body, CUT_X, CUT_Y)
    kit.merge_seamed(body, 0.5)
    kit.sharpen_flats(body)
    return paint


# --- Parts on the hull ---------------------------------------------------------------------------------------------

def chamfer_ribs():
    """Two ribs along each pod's chamfered corner: one at its inner edge, a lit rim near its outer edge."""
    rib = pal("wrib", 0x07, metallic=0.5, roughness=0.3)
    for side in (-1, 1):
        def C(u):
            return u if side < 0 else 2 * AX - u
        for i, (a, b) in enumerate((((8.6, 66.4), (20.0, 77.8)), ((15.0, 65.6), (19.8, 70.4)))):
            pts = []
            for j in range(13):
                t = j / 12.0
                u, r = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
                pts.append(P(C(u), r, pod_h(C(u), r, u) + 0.15))
            kit.w.tube(f"wrib{side:+d}_{i}", pts, 0.55, rib, 10, squash=0.7)


# The left arm's blue pixels by row (first and last column; the right arm is its mirror image), down to where
# the bumper's end hides it.
ARM = {30: (58, 70), 31: (58, 70), 32: (58, 71), 33: (58, 71), 34: (58, 72), 35: (58, 72), 36: (58, 72),
       37: (58, 73), 38: (58, 73), 39: (59, 73), 40: (60, 74), 41: (61, 74), 42: (61, 74), 43: (61, 75), 44: (62, 75),
       45: (62, 75), 46: (62, 76), 47: (62, 76), 48: (62, 77), 49: (62, 77), 50: (62, 77), 51: (63, 78), 52: (63, 78),
       53: (64, 77), 54: (65, 76), 55: (65, 75), 56: (66, 74), 57: (66, 73), 58: (67, 72)}


def collars():
    """The blue horseshoe's arms, from under the pods' grey tops down under the bumper's ends: round-topped
    armour beams following the sprite's outline row by row."""
    blue = Painter("wcollar", shades={3: (7, 9, 0xa)}, metallic=0.35, roughness=0.28)
    rows = sorted(ARM)
    for side in (-1, 1):
        def edges(r):
            # Smoothed over three rows; continuous columns (the last pixel's right edge).
            near = [ARM[q] for q in (r - 1, r, r + 1) if q in ARM]
            a = sum(e[0] for e in near) / len(near)
            b = sum(e[1] + 1.0 for e in near) / len(near)
            return a, b
        rings = []
        samples = [rows[0] - 0.4] + [q + 0.5 for q in rows] + [rows[-1] + 1.4]
        for r in samples:
            a, b = edges(min(max(int(r), rows[0]), rows[-1]))
            if side > 0:
                a, b = 2 * AX - b, 2 * AX - a
            xc, hw = (a + b) / 2.0, (b - a) / 2.0 + 0.15
            top = 24.0 - 0.115 * (r - 30.0)
            height = 3.4
            ring = [Vector(P(xc - hw, r, 11.0))]
            for i in range(17):
                th = math.pi * (1.0 - i / 16.0)
                ring.append(Vector(P(xc + hw * math.cos(th), r, top - height + height * math.sin(th) ** 0.55)))
            ring.append(Vector(P(xc + hw, r, 11.0)))
            rings.append(ring)
        arm = k.loft(f"wcollar{side:+d}", rings, blue(0x3a))
        k.smooth(arm, 50)
        kit.paint_faces(arm, lambda c, nrm: blue(0x37) if nrm.z < 0.3 else None)


def eye():
    """The great glossy black eye in the cavity, painted with the sprite's highlight and reflections."""
    glass = Painter("weye", shades={0: (1, 2, 3, 4, 6, 9, 0xc)}, metallic=0.2, roughness=0.06)
    ball = kit.sphere("weye", P(AX, 48.2, 12.0), (13.6, 9.6, 10.0), glass(0x02), 32, 16)
    kit.pixelate(ball, W, box=(-14.5, 14.5, 12.0, 32.0))
    kit.paint_sprite(ball, W, glass, wall_steps=-1, keep=lambda val: val >> 4 == 0, default=glass(0x01), probe=-0.5,
                     blur=1)
    kit.merge_flat(ball, 0.5)
    rim = pal("weye_rim", 0x03, metallic=0.5, roughness=0.35)
    kit.torus("weye_rim", P(AX, 48.2, 13.2), 13.4, 1.0, rim, 36, 6, squash=0.8, scale_y=9.6 / 13.4)


def bumper():
    """The thick grey bumper curving under the eye."""
    path = [(70.0, 59.3), (74.0, 60.2), (80.0, 61.2), (88.0, 61.9), (AX, 62.1)]
    path = path + [(2 * AX - c, r) for c, r in reversed(path[:-1])]
    pts = [P(c, r, 14.4) for c, r in path]
    widths = [4.6, 5.2, 5.6, 5.6, 5.4, 5.6, 5.6, 5.2, 4.6]
    rings = kit.catmull(pts, 1.0)
    # Widths along the path by x.
    xs = [p[0] for p in pts]

    def width_at(x):
        for i in range(len(xs) - 1):
            if xs[i] <= x <= xs[i + 1]:
                t = (x - xs[i]) / max(xs[i + 1] - xs[i], 1e-6)
                return widths[i] + (widths[i + 1] - widths[i]) * t
        return widths[0] if x < xs[0] else widths[-1]
    sections = [(width_at(p.x), 5.4) for p in rings]
    grey = pal("wbumper", 0x08, metallic=0.4, roughness=0.28)
    kit.loft_path("wbumper", rings, sections, grey, segments=20, smooth_angle=55)


def turrets(paint):
    """On each pod's back edge: a box with a short barrel pointing back, a small box with a knob."""
    for side in (-1, 1):
        def C(u):
            return u if side < 0 else 2 * AX - u
        cx = (C(42.2) + C(59.6)) / 2.0
        box = kit.rounded_box(f"wturret{side:+d}", P(cx, 16.2, 12.6), (17.4, 8.8, 25.2), paint(0x06), bevel=1.2,
                              segments=3)
        kit.pixelate(box, W)
        kit.paint_sprite(box, WF, paint, wall_steps=-1, default=paint(0x05), probe=-0.4)
        # The barrel lying back up the screen, its rounded end over the box's back edge.
        bx = C(48.9)
        barrel = kit.lathe_axis(f"wbarrel{side:+d}", [(0.0, 2.2), (8.5, 2.2), (9.6, 1.9), (10.4, 1.2), (10.7, 0.3)],
                                paint(0x09), P(bx, 18.6, 26.2), (0.0, 1.0, 0.0), 20)
        kit.pixelate(barrel, W)
        kit.paint_sprite(barrel, WF, paint, wall_steps=-1, default=paint(0x06), probe=-0.5)
        # The posts at its sides.
        for u in (43.8, 58.5):
            post = kit.lathe_axis(f"wpost{side:+d}_{u}", [(0.0, 0.9), (26.4, 0.9), (27.0, 0.4)], paint(0x07),
                                  P(C(u), 15.6, 0.0), (0.0, 0.0, 1.0), 10)
            kit.paint_sprite(post, WF, paint, wall_steps=-1, default=paint(0x06), probe=-0.3)
        # The lamp on the box's front.
        lamp = pal("wlamp", 0x0e, metallic=0.1, roughness=0.2, glow=1.2)
        kit.sphere(f"wlamp{side:+d}", P(C(53.8), 17.3, 25.0), (0.9, 0.9, 0.7), lamp, 12, 6)
        # The small box and its knob.
        sx = (C(30.0) + C(42.8)) / 2.0
        small = kit.rounded_box(f"wtsmall{side:+d}", P(sx, 18.9, 12.4), (12.8, 7.4, 24.8), paint(0x06), bevel=1.0,
                                segments=3)
        kit.pixelate(small, W)
        kit.paint_sprite(small, WF, paint, wall_steps=-1, default=paint(0x05), probe=-0.4)
        kit.lathe_axis(f"wknob{side:+d}", [(0.0, 1.5), (3.0, 1.5), (3.6, 1.1), (3.9, 0.3)], paint(0x08),
                       P(C(37.9), 20.0, 25.6), (0.0, 1.0, 0.0), 14)


def hips():
    """Ball joints in the hips and a piston from each down to its leg."""
    steel = Painter("wball", shades={0: (2, 3, 4, 5, 6, 7, 8, 9, 0xa, 0xc)}, metallic=0.6, roughness=0.25)
    for side in (-1, 1):
        def C(u):
            return u if side < 0 else 2 * AX - u
        for i, (u, r, rad, z) in enumerate(((64.6, 62.3, 2.7, 12.6), (59.6, 69.2, 3.0, 12.4), (65.6, 78.0, 2.2, 11.0))):
            ball = kit.sphere(f"wball{side:+d}_{i}", P(C(u), r, z), (rad, rad, rad * 0.9), steel(0x06), 16, 8)
            kit.paint_sprite(ball, W, steel, wall_steps=-1, keep=lambda val: val >> 4 == 0, default=steel(0x04),
                             probe=-0.5)
        # A piston from the hip down to the leg.
        rod = pal("wpiston", 0x06, metallic=0.6, roughness=0.25)
        kit.w.tube(f"wpiston{side:+d}", [P(C(60.0), 70.5, 12.0), P(C(58.0), 77.0, 11.0), P(C(55.5), 83.0, 10.0)], 1.1,
                   rod, 10)


def leg_h(r):
    """The leg's body by row: the dark mount under the pod, the strut, a low saddle under the pistons, the
    housing; the foot is a disc of its own."""
    if r < 91.0:
        return 8.0
    if r < 101.0:
        return 9.6
    if r < 108.0:
        return 5.2
    if r < 121.0:
        return 10.6
    return 3.0


def legs():
    """The legs: an axle under the pod, a strut with pistons, a heavy housing, a round foot with a ringed hub."""
    paint = Painter("wleg", shades={0: (1, 2, 3, 4, 5, 6, 7, 8, 9, 0xa, 0xc, 0xe)}, metallic=0.55, roughness=0.32)
    polys = kit.pixel_polys(W, lambda v, c, r: is_leg_px(c, r), smooth=2, epsilon=0.35)

    def z_of(x, y, e):
        c, r = cr(x, y)
        z = leg_h(r)
        return z - min(2.6, 0.3 * z) * (1.0 - e)
    body = kit.field("wleg", polys, z_of, paint(0x03), spacing=0.5, edge=2.2)
    kit.paint_sprite(body, WF, paint, wall_steps=-1, default=paint(0x03), under=paint(0x01))
    kit.paint_walls(body, WF, paint, grey=0x03)
    kit.paint_under(body, paint(0x01))
    kit.split_at(body, CUT_X, CUT_Y)
    kit.merge_seamed(body, 0.5)
    kit.sharpen_flats(body)
    for side in (-1, 1):
        def C(u):
            return u if side < 0 else 2 * AX - u
        parts = []
        # The axle across the mount.
        parts.append(kit.lathe_axis(f"wlaxle{side:+d}", [(0.0, 2.4), (0.7, 3.4), (15.6, 3.4), (16.3, 2.4)],
                                    paint(0x06), P(C(41.2), 87.6, 8.2), (-side * 1.0, 0.0, 0.0), 20))
        # The pistons: a cylinder and its rod, a thin rod beside them, a clamp where they enter the housing.
        parts.append(kit.lathe_axis(f"wlcyl{side:+d}", [(0.0, 1.5), (0.5, 2.3), (6.0, 2.3), (6.5, 1.7)], paint(0x07),
                                    P(C(51.2), 99.0, 7.6), (0.0, -1.0, 0.0), 16))
        parts.append(kit.lathe_axis(f"wlrod{side:+d}", [(0.0, 1.3), (10.0, 1.3)], paint(0x0a), P(C(51.2), 104.5, 7.4),
                                    (0.0, -1.0, 0.0), 14))
        parts.append(kit.lathe_axis(f"wlrod2{side:+d}", [(0.0, 0.9), (10.0, 0.9)], paint(0x06), P(C(47.6), 100.0, 7.0),
                                    (0.0, -1.0, 0.0), 10))
        parts.append(kit.rounded_box(f"wlclamp{side:+d}", P(C(47.6), 109.6, 9.6), (10.0, 2.0, 2.4), paint(0x06),
                                     bevel=0.6))
        # The foot: an armoured disc, a ring on it, the dark hub and a small sensor.
        kit.disc(f"wlfoot{side:+d}", P(C(49.6), 125.9, 0.0), 6.7, 7.6, paint(0x04), segments=36, bevel=1.7,
                 radius_y=6.1)
        ring = pal("wlring", 0x09, metallic=0.6, roughness=0.25)
        kit.torus(f"wlring{side:+d}", P(C(49.6), 125.9, 7.6), 4.3, 0.85, ring, 32, 8, squash=0.8, scale_y=0.92)
        hub = pal("wlhub", 0x01, metallic=0.4, roughness=0.4)
        kit.disc(f"wlhub{side:+d}", P(C(49.6), 125.9, 6.6), 3.0, 1.2, hub, segments=24, bevel=0.3)
        sensor = pal("wlsensor", 0x0b, metallic=0.5, roughness=0.25)
        kit.cone(f"wlsensor{side:+d}", P(C(49.6), 125.9, 7.6), (0.0, 0.0, 1.0), 1.4, 1.3, sensor, segments=3)
        for obj in parts:
            kit.paint_sprite(obj, WF, paint, wall_steps=-1, keep=lambda val: val >> 4 == 0, default=None, probe=-0.4,
                             blur=1)


def walker_whole():
    paint = hull()
    chamfer_ribs()
    collars()
    eye()
    bumper()
    turrets(paint)
    hips()
    legs()
    kit.flatten_under(kit.meshes(), 0.0)
    kit.stretch_z(kit.meshes())


# The pieces: (sprite, its top left pixel in the whole).
PIECES = ([(1 + 2 * i, 24 * i, 0) for i in range(8)] + [(39 + 2 * i, 24 * i, 28) for i in range(8)] +
          [(77 + 2 * i, 24 * i, 56) for i in range(8)] + [(118 + 2 * i, 36 + 24 * i, 84) for i in range(5)] +
          [(156, 36, 112), (164, 132, 112)])

kit.PROTECT += ["whull", "wcollar", "weye", "wbumper"]
kit.pieced("fleet_walker", walker_whole, (192, 140), [kit.piece(f"fleet_walker_{s}", W, c0, r0)
                                                     for s, c0, r0 in PIECES])


# --- The hatch ---------------------------------------------------------------------------------------------------

def hatch_whole():
    """The hatch in its own frame (48 x 28, its sprites 191 and 193 side by side), standing at HATCH_FOOT."""
    paint = Painter("whatch", shades={0: (1, 2, 3, 4, 5, 6, 7, 8, 0xc)}, metallic=0.5, roughness=0.34)
    foot = kit.HATCH_FOOT
    # The frame: a bevelled grey rim round the lid.
    outer = kit.box_poly(HATCH.X(1) - 0.5, HATCH.X(46) + 0.5, HATCH.Y(23) - 0.5, HATCH.Y(2) + 0.5)

    def z_of(x, y, e):
        c, r = x + HATCH.ox, HATCH.oy - y
        inner = 4.0 <= c < 43.0 and 5.0 <= r < 20.0
        if not inner:
            return foot + 1.7 - 0.6 * (1.0 - e)
        z = foot + 0.9
        v = HATCH.get(int(c), int(r))
        # The raised stepped plate in its middle and the vent slits at its sides.
        if 10.0 <= c < 37.0 and 9.0 <= r < 18.5 and not (c < 15.0 and r < 11.5) and not (c >= 33.0 and r < 11.5):
            z += 0.55
        if v is not None and (v & 15) == 1 and (c < 10.0 or c >= 37.0) and 13.0 <= r < 19.0:
            z -= 0.35
        return z
    lid = kit.field("whatch", [outer], z_of, paint(0x02), spacing=0.5, edge=1.2)
    kit.paint_sprite(lid, HF, paint, wall_steps=-1, default=paint(0x04), under=paint(0x01))
    kit.paint_under(lid, paint(0x01))
    kit.split_at(lid, (0.0,), ())
    kit.merge_seamed(lid, 0.5)
    kit.sharpen_flats(lid)
    # Only the part above its foot (the field stands on z = 0).
    kit.flatten_under([lid], foot - 0.3)
    kit.stretch_z([lid])


kit.PROTECT += ["whatch"]
kit.pieced("fleet_hatch", hatch_whole, (48, 28), [kit.piece("fleet_hatch_l", HATCH, 0, 0),
                                                   kit.piece("fleet_hatch_r", HATCH, 24, 0)])


if __name__ == "__main__":
    kit.run()
