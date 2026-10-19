"""Enemies of wave 3, batch V (sheet T), CORAL's sea creatures and machines; modelled as their sprites look
(models.cfg: yaw=0 unless noted). DELI's boss is in wave3_v.py; the kit is wave3_v_kit.py, the pixels
wave3_v_art.py. Objects the levels put together from several sprites (the level files' enemy events say
how) are built whole and cut into their pieces, drawn at their own origins (origin). (CORAL's bony fish, T 229
beside T 231: polish_coral_fish.py; its seahorses, T 203 and 241: polish_coral_seahorse.py.)

- coral_starfish (T 127): the tan starfish thrown in CORAL (enemy 1223); its frames (129, 131, 245) turn it
  clockwise 18 degrees each, two cycles apiece (models.cfg: yaw=frames:40:0).
- coral_starlet (T 89): CORAL's small starfish (enemy 1212), a little above the sprite's middle.
- coral_manta_back, coral_manta_wing_left, coral_manta_wing_right, coral_manta_head (T 199, 197, 201, 237):
  CORAL's manta (events 1206-1209: 197 at (x, y), 199 at (x + 24, y - 10), 237 at (x + 24, y + 18), 201 at
  (x + 48, y)): blue-grey wings arched down to their gold-edged tips, a raised back with two dark windows,
  a gold spike of a tail up the screen, two dark horns at its mouth (the wings' frames flap them, 237's
  blow bubbles between the horns: the model keeps the wings spread). Built whole, cut in four (origin).
- coral_pylon_top, coral_pylon_mid, coral_pylon_base (T 279 above 281 above 283; events 1213-1215 at (x, y),
  (x, y + 28), (x, y + 56)): a long grey cylinder lying up the screen, a capped end with lugs, flanged
  collars, dark joints, a dark port with a glowing lamp and a nozzle at its near end. Cut in three (origin).
- coral_dome_tl, coral_dome_tr, coral_dome_bl, coral_dome_br (T 15, 17 above 53, 55; events 1201-1204): a
  purple dome on the sea floor with gold bands round its foot, over its middle and down its left side, a
  window block on its right lobe and a boss on its left. The sprites draw it on a square of water, which
  the model leaves to the map's water. Cut in four (origin).
- coral_shell_top, coral_shell_base (T 13 above 51; events 1199, 1200): a long tan spiral shell lying on
  the floor, its point up the screen, its dark mouth down and to the right (the water round it left to the
  map). Cut in two (origin).
- coral_sub_top, coral_sub_base (T 195 above 233; events 1210, 1211): a blue-grey submarine heading down the
  screen, a ringed propeller housing at its stern, side fins, a dark window with a glowing lamp in its bow.
  Cut in two (origin).

usage: Blender -b --factory-startup -P wave3_v_sea.py -- [--only name,name] [--preview <prefix>]
       [--check 1] [--stats 1] [--whole <prefix>]
"""
import math
import os
import sys

from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_v_kit as v  # noqa: E402
from wave3_v_kit import art, k, sh, w, n, pal  # noqa: E402


# --- T 127 and T 89: the starfish --------------------------------------------------------------------

def starfish(prefix, centre, radius, inner, height, bumps=4):
    """A five-armed starfish, one arm up the screen: arms round in section, tapering to rounded tips, a
    domed middle, rows of pale knobs along the arms, tan with lighter ridges."""
    cx, cy = centre
    bands = v.bands_of(prefix, 1, (6, 7, 8, 0xa, 0xb, 0xc), metallic=0.1, roughness=0.65)
    knob = pal(f"{prefix}_knob", 0x1c, metallic=0.1, roughness=0.5)
    pts = []
    for i in range(10):
        a = math.radians(90 + 36 * i)
        if i % 2 == 0:  # a tip, and the arm's slimmer outer half after it
            pts.append((cx + radius * math.cos(a), cy + radius * math.sin(a)))
            b = a + math.radians(9.0)
            r = inner + 0.5 * (radius - inner)
            pts.append((cx + r * math.cos(b), cy + r * math.sin(b)))
        else:
            pts.append((cx + inner * math.cos(a), cy + inner * math.sin(a)))
            b = a + math.radians(27.0)
            r = inner + 0.5 * (radius - inner)
            pts.append((cx + r * math.cos(b), cy + r * math.sin(b)))
    poly = sh._chaikin(pts, 1)

    def dome(x, y, z):
        d = math.hypot(x - cx, y - cy)
        return z + height * 0.35 * math.exp(-(d / (inner * 0.9)) ** 2)
    body = v.relief("star", [poly], bands[2][1], sh.round_profile(0.62, max_height=height), bottom=0.35,
                    z_fn=dome, spacing=0.45 if radius > 8 else 0.33)
    top = max(vt.co.z for vt in body.data.vertices)

    def light(x, y):
        return 6.0 + 6.0 * (sh.surface_z(body, x, y, 0.0) / top)
    n.paint_shades(body, light, bands, wall_drop=1.5)
    # The knobs along each arm's ridge.
    for arm in range(5):
        a = math.radians(90 + 72 * arm)
        for j in range(bumps):
            t = (j + 1.2) / (bumps + 1.0)
            r = inner * 0.4 + (radius * 0.86 - inner * 0.4) * t
            x, y = cx + r * math.cos(a), cy + r * math.sin(a)
            z = sh.surface_z(body, x, y, height)
            size = (0.75 - 0.35 * t) * radius / 12.0 + 0.12
            w.sphere(f"knob{arm}_{j}", (x, y, z - size * 0.2), (size, size, size * 0.8), knob, 10, 5)


@v.model("coral_starfish", mask=lambda: v.Frame(art.STAR, 24, (12, 14)).mask())
def coral_starfish():
    """The tan starfish CORAL's creatures throw (enemy 1223), turning as its frames do (yaw=frames)."""
    starfish("starfish", (0.0, -0.2), 12.9, 6.2, 4.4)


@v.model("coral_starlet", mask=lambda: v.Frame(art.STARLET, 24, (12, 14)).mask())
def coral_starlet():
    """CORAL's small starfish (enemy 1212), lying a little above the sprite's middle as the sprite draws it."""
    starfish("starlet", (0.0, 1.7), 5.8, 2.8, 2.2, bumps=2)



# --- T 199, 197, 201, 237: the manta -----------------------------------------------------------------

MANTA = v.Frame(art.MANTA, 72, (36, 28))
MANTA_AXIS = -0.5  # the middle of pixel column 35


def manta_whole():
    """A blue-grey manta swimming down the screen, its broad wings arched down to their tips and edged with
    gold, a raised back with two dark windows either side of a gold strip, a thin gold spike of a tail
    up the screen, two dark horns curling in at its mouth."""
    f = MANTA
    paint = v.Painter("manta", shades={6: (4, 5, 6, 7, 8, 9), 8: (3, 6, 8), 0xa: (4, 7, 0xa, 0xb), 1: (1, 3, 5),
                                       3: (1, 3, 5), 5: (4, 5, 6)}, metallic=0.35, roughness=0.32)
    skin = paint(0x67)
    gold = pal("manta_gold", 0xa9, metallic=0.6, roughness=0.3)
    horn = pal("manta_horn", 0x64, metallic=0.3, roughness=0.3)
    horn_light = pal("manta_horn_light", 0x67, metallic=0.3, roughness=0.3)
    glass = pal("manta_glass", 0x30, metallic=0.3, roughness=0.06)
    glass_light = pal("manta_glass_light", 0x35, metallic=0.3, roughness=0.06)

    def bulge(x, y):
        """The raised back: high along the middle from the tail's root to the mouth."""
        return math.exp(-((x - MANTA_AXIS) / 7.5) ** 2) * v.smoothstep(f.Y(6.0), f.Y(12.0), y) * \
            v.smoothstep(f.Y(39.0), f.Y(31.0), y)

    def droop(x, y):
        return 4.6 - 0.1 * abs(x - MANTA_AXIS)

    keep = lambda i, c, r: 7 <= r <= 38 and not (r == 38 and (c <= 30 or c >= 40))
    body = v.relief("body", v.outlines_of(f, keep, grow=0.0, smooth=1), skin,
                    sh.round_profile(0.42, max_height=2.4, min_height=0.4), bottom=0.45,
                    z_fn=lambda x, y, z: z + 4.2 * bulge(x, y), spacing=0.62)
    for vt in body.data.vertices:
        vt.co.z += droop(vt.co.x, vt.co.y)
    v.paint_sprite(body, f, paint, wall_steps=-1, default=skin)

    def top(x, y):
        return sh.surface_z(body, x, y, 6.0)

    # The windows: two dark panes set into the back.
    for c0, c1 in ((30, 33), (36, 39)):
        cx = (f.X(c0) + f.X(c1)) / 2
        for r0, r1, mat, dz in ((11, 21, glass, 0.0), (11.6, 14.0, glass_light, 0.18)):
            cy = (f.Y(r0) + f.Y(r1)) / 2
            z = top(cx, cy)
            hw, hd = (c1 - c0 + 1) / 2 - 0.15 - dz, (r1 - r0 + 1) / 2 - 0.1 - dz
            w.rounded_box(f"window{c0}_{r0}", (cx, cy, z - 0.35 + dz), (2 * hw, 2 * hd, 1.2), mat, bevel=0.3)

    # The tail: a thin gold spike up the screen from the back.
    root = (MANTA_AXIS, f.Y(8.5), top(MANTA_AXIS, f.Y(8.5)) - 0.4)
    pts = w.catmull([root, (MANTA_AXIS, f.Y(4.5), root[2] + 0.3), (MANTA_AXIS, f.Y(0.2), root[2] + 0.6)], 0.4)
    w.tube("tail", pts, [1.25 - 0.95 * j / (len(pts) - 1) for j in range(len(pts))], gold, 10)

    # The horns at the mouth, curling in at their tips.
    for side, path in ((-1, [(28.2, 35.5), (27.6, 39.5), (27.6, 43.0), (28.4, 45.8), (29.0, 46.6)]),
                       (1, [(42.4, 35.5), (43.2, 39.5), (43.0, 43.0), (42.2, 45.0), (41.6, 46.2)])):
        pts = [(f.X(c), f.Y(r), 3.2 - 0.25 * j) for j, (c, r) in enumerate(path)]
        pts = w.catmull(pts, 0.4)
        last = len(pts) - 1
        hn = w.tube(f"horn{side}", pts, [2.6 - 1.7 * (j / last) ** 1.6 for j in range(len(pts))], horn, 14, squash=0.8)
        w.paint_faces(hn, lambda c, nrm, s=side: horn_light if nrm.z > 0.5 and nrm.x * s < 0.2 else None)
    v.stats(*w.meshes())


def manta_piece(name, box, centre, cols, rows):
    return (name, box, centre, lambda: MANTA.mask((cols[0], cols[1], rows[0], rows[1])))


v.pieced("coral_manta", manta_whole, (72, 56), [
    manta_piece("coral_manta_wing_left", (-36.0, -12.0, -10.0, 18.0), (-24.0, 4.0), (0, 24), (10, 38)),
    manta_piece("coral_manta_back", (-12.0, 12.0, 0.0, 28.0), (0.0, 14.0), (24, 48), (0, 28)),
    manta_piece("coral_manta_wing_right", (12.0, 36.0, -10.0, 18.0), (24.0, 4.0), (48, 72), (10, 38)),
    manta_piece("coral_manta_head", (-12.0, 12.0, -28.0, 0.0), (0.0, -14.0), (24, 48), (28, 56))])



# --- T 279 above 281 above 283: the segmented column --------------------------------------------------

COLUMN = v.Frame(art.COLUMN, 24, (12, 42))


def column_whole():
    """A long grey cylinder lying up the screen, in segments: a wide cap with three lugs at its far end,
    flanged collars along it, dark joints between the segments, and at its near end a dark port with a
    lamp glowing in it and a rounded nozzle."""
    f = COLUMN
    greys = {s_: pal(f"column_grey{s_:x}", s_, metallic=0.55, roughness=0.35) for s_ in (4, 6, 8, 9, 0xa, 0xb, 0xc)}
    seam = pal("column_seam", 0x02, metallic=0.3, roughness=0.6)
    pit = pal("column_pit", 0x01, metallic=0.2, roughness=0.3)
    lamp = pal("column_lamp", 0x0e, metallic=0.0, roughness=0.2, glow=1.2)
    axis_z, squash = 6.4, 0.85

    def turned(name, profile, mat, segments=32):
        """A part turned round the column's axis: profile [(row, half width)] down the screen."""
        pts = [(f.Y(r), hw) for r, hw in profile]
        pts.sort()
        obj = k.lathe(name, pts, mat, segments=segments, axis_z=axis_z, squash=squash)
        return k.smooth(obj, 45)

    def shade_paint(obj, lift=0.0):
        """Lit along the top: the sprite's light across the cylinder, as bands."""
        def pick(c, nrm):
            if nrm.z < -0.2:
                return greys[4]
            t = nrm.z
            value = 5.5 + 6.0 * t ** 1.5 + lift
            return greys[min(greys, key=lambda s_: abs(s_ - value))]
        w.paint_faces(obj, pick)

    # The body: segments between the joints.
    body = turned("body", [(1.0, 6.2), (2.0, 7.0), (71.0, 7.0), (72.5, 7.6), (78.0, 7.6), (79.0, 5.2), (82.0, 4.6),
                           (83.4, 3.4), (84.0, 0.8)], greys[9], 40)
    shade_paint(body)
    # The cap at the far end and its three lugs.
    cap = turned("cap", [(0.6, 8.6), (1.2, 10.0), (11.0, 10.0), (12.0, 8.0), (12.4, 6.0)], greys[9], 40)
    shade_paint(cap, 0.5)
    for x in (f.X(4.0), 0.0 - 0.0, f.X(19.0)):
        wdt = 5.0 if x == 0.0 else 2.6
        w.rounded_box(f"lug{x:.0f}", (x, f.Y(0.8), axis_z + (5.0 if x == 0.0 else 3.6)), (wdt, 2.4, 2.6), greys[8],
                      bevel=0.5)
    # The collars: a flanged ring and two plain ones.
    for name, r0, r1, hw in (("collar_a", 19.0, 27.6, 12.0), ("collar_b", 39.0, 52.6, 10.0),
                             ("collar_c", 66.0, 71.8, 11.0)):
        prof = [(r0, 7.2), (r0 + 0.8, hw - 0.8), (r0 + 1.6, hw), (r1 - 1.6, hw), (r1 - 0.8, hw - 0.8), (r1, 7.2)]
        c = turned(name, prof, greys[8], 40)
        shade_paint(c, 0.3)
    # The joints: dark rings round the body.
    for r in (16.5, 36.5, 53.5, 63.5):
        turned(f"joint{r}", [(r - 0.45, 6.9), (r - 0.3, 7.22), (r + 0.3, 7.22), (r + 0.45, 6.9)], seam, 40)
    # The port on the near end's top: a dark round pit, a lamp glowing in it.
    pz = axis_z + 7.6 * squash
    w.sphere("port", (0.0, f.Y(74.6), pz - 0.6), (4.0, 3.4, 1.4), pit, 24, 10)
    w.sphere("lamp", (0.2, f.Y(74.2), pz + 0.2), (1.3, 1.5, 0.8), lamp, 14, 7)


def column_piece(name, row0):
    y1 = 42 - row0
    return (name, (-12.0, 12.0, y1 - 28.0, y1), (0.0, y1 - 14.0), lambda: COLUMN.mask((0, 24, row0, row0 + 28)))


v.pieced("coral_pylon", column_whole, (24, 84), [column_piece("coral_pylon_top", 0),
                                                 column_piece("coral_pylon_mid", 28),
                                                 column_piece("coral_pylon_base", 56)])


# --- T 15, 17 above 53, 55: the purple dome ----------------------------------------------------------

DOME = v.Frame(art.DOME, 48, (24, 28))
DOME_MASK = lambda box: lambda: DOME.mask_where(lambda i: i >> 4 in (1, 5), box)


def dome_whole():
    """A purple dome standing on the sea floor (the sprite's water left to the map), a gold band round its
    foot, one over its middle up the screen and one curving down its left side; a square window block on
    its right lobe and a round boss on its left."""
    f = DOME
    paint = v.Painter("dome", shades={5: (3, 4, 5, 6, 7, 8, 9, 0xb), 1: (4, 6, 8, 0xa)}, metallic=0.3,
                      roughness=0.35)
    purple = paint(0x56)
    gold = pal("dome_gold", 0x19, metallic=0.7, roughness=0.3)
    gold_light = pal("dome_gold_light", 0x1b, metallic=0.7, roughness=0.28)
    cx, cy, rx, ry, height = 0.0, f.Y(28.8), 23.2, 17.8, 17.0

    def zdome(x, y):
        d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
        return height * math.sqrt(max(0.0, 1.0 - d)) ** 0.9

    # The dome: an ellipsoid's upper half, its foot on the floor.
    rings = []
    for i in range(14):
        t = i / 13
        a = t * math.pi / 2
        rr = math.cos(a)
        z = height * math.sin(a)
        rings.append([Vector((cx + rx * rr * math.cos(b), cy + ry * rr * math.sin(b), z))
                      for b in (2 * math.pi * j / 64 for j in range(64))])
    dome = k.loft("dome", rings, purple, cap_start=True, cap_end=True, start_point=(cx, cy, 0.0),
                  end_point=(cx, cy, height))
    k.smooth(dome, 60)
    v.paint_sprite(dome, f, paint, wall_steps=0, keep=lambda i: i >> 4 == 5, default=purple)

    def on_dome(x, y, lift):
        return zdome(x, y) + lift

    # The bands: up the middle, and down the left side to the middle band's foot.
    mid = [(0.0, cy + ry * t, 0.0) for t in (-0.98, -0.7, -0.35, 0.0, 0.35, 0.7, 0.98)]
    mid = [(x, y, on_dome(x, y, 0.15)) for x, y, _ in mid]
    w.tube("band_mid", w.catmull(mid, 0.5), 2.0, gold, 12, squash=0.45)
    left = [(f.X(c), f.Y(r)) for c, r in ((1.6, 30.0), (5.0, 32.0), (9.0, 34.4), (14.0, 35.6), (19.0, 36.4),
                                         (22.0, 36.6))]
    w.tube("band_left", w.catmull([(x, y, on_dome(x, y, 0.2)) for x, y in left], 0.5), 1.1, gold, 10, squash=0.5)
    # The band round the foot.
    w.hoop("band_foot", (cx, cy, 0.0), [(rx - 0.4, 0.0), (rx + 0.9, 0.0), (rx + 0.9, 1.6), (rx - 0.2, 2.2)], gold_light,
           72, scale_y=ry / rx)
    # The window block on the right lobe, the boss on the left.
    wx, wy = f.X(33.6), f.Y(26.5)
    wz = zdome(wx, wy)
    lean = math.atan2((wx - cx) / rx ** 2, wz / height ** 2)  # the dome's slope there
    tilt = Matrix.Translation((wx, wy, wz)) @ Matrix.Rotation(lean, 4, "Y") @ Matrix.Translation((-wx, -wy, -wz))
    win = w.rounded_box("window", (wx, wy, wz + 0.2), (6.6, 7.8, 2.4), paint(0x58), bevel=0.8)
    pane = w.rounded_box("window_pane", (wx, wy, wz + 1.2), (4.2, 5.4, 1.0), paint(0x53), bevel=0.35)
    for obj in (win, pane):
        obj.data.transform(tilt)
    bx, by = f.X(10.0), f.Y(22.6)
    w.sphere("boss", (bx, by, zdome(bx, by) - 0.4), (2.6, 2.8, 1.6), paint(0x59), 16, 8)


def dome_piece(name, col0, row0):
    x0, y1 = col0 - 24, 28 - row0
    return (name, (x0, x0 + 24.0, y1 - 28.0, y1), (x0 + 12.0, y1 - 14.0), DOME_MASK((col0, col0 + 24, row0, row0 + 28)))


v.pieced("coral_dome", dome_whole, (48, 56), [dome_piece("coral_dome_tl", 0, 0), dome_piece("coral_dome_tr", 24, 0),
                                              dome_piece("coral_dome_bl", 0, 28), dome_piece("coral_dome_br", 24, 28)])


# --- T 13 above 51: the spiral shell -----------------------------------------------------------------

SHELL = v.Frame(art.SHELL, 24, (12, 28))
SHELL_MASK = lambda box: lambda: SHELL.mask_where(lambda i: i >> 4 in (0xa, 0xb), box)


def shell_whole():
    """A long tan spiral shell lying on the sea floor, its point up the screen, ridged whorls widening to
    the body whorl at its foot, the dark mouth opening down and to the right with a pale lip."""
    f = SHELL
    bands = v.bands_of("shell", 0xa, (3, 4, 5, 6, 7, 8, 9), metallic=0.15, roughness=0.45)
    pit = pal("shell_pit", 0xa0, metallic=0.1, roughness=0.5)
    lip = pal("shell_lip", 0xab, metallic=0.2, roughness=0.3)
    tip = Vector((f.X(14.0), f.Y(5.0), 1.2))
    base = Vector((f.X(11.2), f.Y(50.6), 0.0))
    axis = (base - tip)
    length = axis.length
    d = axis.normalized()
    side = d.cross(Vector((0, 0, 1))).normalized()
    up = side.cross(d).normalized()
    turns = 9.0
    rings = []
    count = 90
    for i in range(count + 1):
        t = i / count
        r = 0.4 + 10.0 * t ** 0.9
        if t > 0.93:  # the body whorl rounds off
            r *= 0.35 + 0.65 * math.sqrt(max(0.0, 1.0 - ((t - 0.93) / 0.07) ** 2))
        centre = tip + axis * t
        ring = []
        for j in range(36):
            a = 2 * math.pi * j / 36
            phase = turns * t * 2 * math.pi - a
            ridge = 1.0 + 0.09 * (0.5 + 0.5 * math.cos(phase)) ** 3 - 0.05 * (0.5 + 0.5 * math.cos(phase + 2.4)) ** 6
            rr = r * ridge
            p = centre + (side * math.cos(a) + up * math.sin(a) * 0.82) * rr
            ring.append(p)
        rings.append(ring)
    body = k.loft("shell", rings, bands[3][1], start_point=tuple(tip - d * 0.3), end_point=tuple(base + d * 0.2))
    k.smooth(body, 50)
    # Lying on the floor: lift it so its underside touches z = 0.
    zmin = min(vt.co.z for vt in body.data.vertices)
    body.data.transform(Matrix.Translation((0, 0, -zmin - 0.8)))
    shade = f.shade((0xa,), blur=1)
    n.paint_shades(body, lambda x, y: shade(x, y), bands, wall_drop=1.0)
    # The mouth, down and to the right on the body whorl.
    mx, my = f.X(16.8), f.Y(47.6)
    top = sh.surface_z(body, mx, my, 6.0)
    w.sphere("mouth", (mx, my, top - 1.4), (3.2, 3.6, 2.2), pit, 18, 9)
    w.hoop("lip", (mx, my, top - 0.8), [(3.0, -0.5), (3.9, -0.4), (3.9, 0.4), (3.2, 0.6)], lip, 28, scale_y=1.1)
    sh.flat_bottom(w.meshes(), 0.0)


def shell_piece(name, row0):
    y1 = 28 - row0
    return (name, (-12.0, 12.0, y1 - 28.0, y1), (0.0, y1 - 14.0), SHELL_MASK((0, 24, row0, row0 + 28)))


v.pieced("coral_shell", shell_whole, (24, 56), [shell_piece("coral_shell_top", 0), shell_piece("coral_shell_base", 28)])


# --- T 195 above 233: the small submarine ------------------------------------------------------------

SUB = v.Frame(art.SUB, 24, (12, 28))


def sub_whole():
    """A dark grey submarine heading down the screen: a long round hull, a ringed propeller housing at its
    stern, a fin out to each side and a small fin on its back in the middle, a dark heart-shaped window in
    its bow with a lamp shining in it."""
    f = SUB
    greys = {s_: pal(f"sub_grey{s_:x}", 0x60 + s_, metallic=0.55, roughness=0.3) for s_ in (3, 5, 6, 7, 8, 9, 0xb)}
    glass = pal("sub_glass", 0x60, metallic=0.3, roughness=0.06)
    lamp = pal("sub_lamp", 0x0e, metallic=0.0, roughness=0.1, glow=1.4)
    axis_z, squash = 6.6, 0.85

    def paint_lit(obj, lift=0.0):
        def pick(c, nrm):
            if nrm.z < -0.2:
                return greys[3]
            value = 4.5 + 4.5 * max(0.0, nrm.z) ** 1.5 + lift
            return greys[min(greys, key=lambda s_: abs(s_ - value))]
        w.paint_faces(obj, pick)

    # The hull: the sprite's half widths, row by row.
    prof = [(2.6, 3.2), (3.5, 4.6), (4.5, 5.0), (6.5, 6.0), (8.5, 7.0), (11.5, 7.8), (14.0, 8.0), (40.0, 8.0),
            (43.0, 7.8), (46.0, 7.0), (49.0, 6.0), (51.5, 4.8), (53.5, 3.2), (55.0, 1.6), (55.6, 0.4)]
    pts = sorted((f.Y(r), hw) for r, hw in prof)
    hull = k.lathe("hull", pts, greys[6], segments=40, axis_z=axis_z, squash=squash)
    k.smooth(hull, 50)
    paint_lit(hull)
    # The propeller housing at the stern: a ring and a hub.
    ring_y = f.Y(1.2)
    housing = k.lathe("housing", sorted([(f.Y(0.0), 3.4), (f.Y(0.4), 4.1), (f.Y(2.2), 4.1), (f.Y(3.0), 3.2)]),
                      greys[8], segments=32, axis_z=axis_z, squash=squash)
    k.smooth(housing, 40)
    paint_lit(housing, 1.0)
    w.lathe_axis("hub", [(0.0, 1.6), (0.6, 1.9), (1.4, 1.2), (1.8, 0.2)], greys[9], (0.0, ring_y - 0.4, axis_z),
                 (0, 1, 0), 16)
    # The side fins: swept plates from the hull out to the sprite's edges (rows 27-34).
    for s_ in (-1, 1):
        fin = [(s_ * 6.0, f.Y(26.5)), (s_ * 11.6, f.Y(28.0)), (s_ * 12.0, f.Y(31.0)), (s_ * 10.0, f.Y(34.6)),
               (s_ * 6.0, f.Y(35.0))]
        if s_ < 0:
            fin = fin[::-1]
        plate = v.slab(f"fin{s_}", fin, axis_z - 1.0, axis_z + 0.6, greys[5], bevel=0.45)
        paint_lit(plate, 0.5)
    # The small fin on the back.
    w.rounded_box("dorsal", (0.0, f.Y(27.5), axis_z + 8.0 * squash + 0.4), (1.6, 5.0, 2.2), greys[8], bevel=0.6)
    # The window in the bow and its lamp.
    wy = f.Y(45.8)
    top = axis_z + 7.2 * squash
    w.sphere("window", (0.0, wy + 0.3, top - 0.9), (4.4, 2.9, 1.5), glass, 24, 10)
    w.sphere("window_point", (0.0, wy - 1.5, top - 1.0), (2.2, 2.0, 1.3), glass, 16, 8)
    w.sphere("lamp", (0.0, wy, top + 0.15), (1.0, 1.1, 0.7), lamp, 12, 6)
    # The belly band (rows 27-33: the darker band round the hull under the fins).
    band = k.lathe("band", sorted([(f.Y(26.6), 8.0), (f.Y(26.9), 8.25), (f.Y(34.6), 8.25), (f.Y(34.9), 8.0)]),
                   greys[5], segments=40, axis_z=axis_z, squash=squash)
    paint_lit(band, -0.5)


def sub_piece(name, row0):
    y1 = 28 - row0
    return (name, (-12.0, 12.0, y1 - 28.0, y1), (0.0, y1 - 14.0), lambda: SUB.mask((0, 24, row0, row0 + 28)))


v.pieced("coral_sub", sub_whole, (24, 56), [sub_piece("coral_sub_top", 0), sub_piece("coral_sub_base", 28)])


if __name__ == "__main__":
    v.run()
