"""Enemies of wave 3, batch V (sheet T), CORAL's sea creatures and machines; modelled as their sprites look
(models.cfg: yaw=0 unless noted). DELI's boss is in wave3_v.py; the kit is wave3_v_kit.py, the pixels
wave3_v_art.py. Objects the levels put together from several sprites (the level files' enemy events say
how) are built whole and cut into their pieces, drawn at their own origins (origin).

- coral_fish_left, coral_fish_right (T 229 beside T 231): CORAL's pale spiny fish, swimming down the
  screen in files of five (events: 1197 = 229 at (x, y), 1198 = 231 at (x + 24, y)): a silvery body from
  a forked tail at the top to a pointed head, a fan of fins round the head whose spines sweep back and
  out, two long curved spines at its ends. Built whole and cut in two (origin).
- coral_seahorse_left (T 203) and coral_seahorse_right (T 241, its mirror image): CORAL's brown seahorses
  in profile, swimming in from the right (1221) and the left (1205): a ridged body arching from the crowned
  head to the curled tail, a long snout, a pale eye, a frilly pale blue fin at the back of the head (its
  second frame flickers the fin).
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


# --- T 229 beside T 231: the spiny fish ------------------------------------------------------------

FISH = v.Frame(art.FISH, 48, (24, 14))


def fish_whole():
    """A silvery fish swimming down the screen: a slim body from the forked tail to the pointed head, a
    fan of fins round the head with spines sweeping back and out, two long curved spines at its ends."""
    f = FISH
    bands = v.bands_of("fish", 0, (6, 8, 0xa, 0xc, 0xd), metallic=0.3, roughness=0.3)
    blue = v.bands_of("fish_fin", 6, (9, 0xb, 0xc), metallic=0.3, roughness=0.3)
    shade = f.shade((0, 5, 6), blur=1)
    body_mat = bands[2][1]
    fin_mat = blue[1][1]
    spine_mat = bands[3][1]
    eye = pal("fish_eye", 0x01, metallic=0.2, roughness=0.15)

    # The body: along the screen from the tail (row 4) to the head's point (row 26.6), round in section,
    # its back higher than its belly; the widths from the sprite.
    widths = [(4.0, 0.9), (5.5, 1.7), (8.0, 1.9), (11.0, 2.1), (13.5, 2.8), (16.0, 3.0), (19.0, 3.3), (21.5, 3.2),
              (23.5, 2.7), (25.0, 1.8), (26.2, 0.9), (26.8, 0.3)]
    rings = []
    for row, hw in reversed(widths):
        y = f.Y(row - 0.5)
        rings.append(k.ring(y, hw, hw * 0.95, 20, z=3.0, top=1.0, bottom=0.75))
    body = k.loft("body", rings, body_mat, start_point=(0.0, f.Y(27.0), 3.0), end_point=(0.0, f.Y(3.3), 3.4))
    k.smooth(body, 60)
    # A ridge along the back.
    ridge = [(0.0, f.Y(r), 3.0 + 0.95 * hw + 0.2) for r, hw in ((6.0, 1.8), (10.0, 2.0), (14.0, 2.85), (18.0, 3.2),
                                                               (21.5, 3.2), (24.0, 2.5))]
    w.tube("ridge", w.catmull(ridge, 0.6), 0.55, spine_mat, 10, squash=0.8)
    # Eyes on the head's sides.
    for s in (-1, 1):
        w.sphere(f"eye{s}", (s * 2.3, f.Y(22.6), 3.7), (0.7, 0.8, 0.6), eye, 12, 6)

    # The tail: a fork of two thin fins up the screen.
    for s, tip in ((-1, (20.0, 1.0)), (1, (27.0, 1.0))):
        root = (s * 0.6, f.Y(4.6), 3.3)
        mid = ((f.X(tip[0]) + root[0]) * 0.55, f.Y(2.6), 3.5)
        end = (f.X(tip[0]), f.Y(tip[1]), 3.6)
        pts = w.catmull([root, mid, end], 0.4)
        w.tube(f"tail{s}", pts, [0.9 - 0.75 * i / (len(pts) - 1) for i in range(len(pts))], fin_mat, 10, squash=0.45)

    # The fan of fins round the head (rows 17-22): a thin plate under the body, its edge dipping.
    fan = [(f.X(13.0), f.Y(18.0)), (f.X(16.5), f.Y(17.6)), (f.X(23.5), f.Y(17.0)), (f.X(30.5), f.Y(17.6)),
           (f.X(35.0), f.Y(18.0)), (f.X(33.0), f.Y(19.8)), (f.X(29.5), f.Y(21.7)), (f.X(26.0), f.Y(23.4)),
           (f.X(21.0), f.Y(23.4)), (f.X(17.5), f.Y(21.7)), (f.X(14.5), f.Y(19.8))]

    def fan_z(x, y, z):
        return z + 1.6 - 0.05 * abs(x) ** 1.4 * 0.5
    plate = v.relief("fan", [fan], fin_mat, sh.pillow_profile(0.9, 0.8, crown=0.4), bottom=0.6, base=2.2,
                     z_fn=fan_z, spacing=0.45)
    n.paint_shades(plate, lambda x, y: shade(x, y) - 0.6, bands[:3] + blue[2:], wall_drop=1.5)
    # Rays across the fan, from the body out to its edge.
    for s in (-1, 1):
        for x_end, row_end, row_root in ((10.0, 18.6, 19.0), (8.0, 19.8, 20.0), (5.5, 21.2, 21.0), (3.2, 22.6, 22.0)):
            pts = [(s * 2.6, f.Y(row_root)), (s * (2.6 + x_end) / 2, f.Y((row_root + row_end) / 2)),
                   (s * x_end, f.Y(row_end))]
            pts = [(x, y, sh.surface_z(plate, x, y, 3.0) + 0.02) for x, y in pts]
            w.tube(f"ray{s}{x_end}", w.catmull(pts, 0.5), 0.3, spine_mat, 8, squash=0.6)

    # The spines: the long outer ones curving out and up the screen to their tips (columns 9 and 38, row
    # 11), the shorter ones between them, all rising from the fan.
    spines = [
        ([(14.5, 19.2), (12.4, 17.2), (11.0, 15.0), (10.2, 13.0), (9.4, 11.0)], 0.75),
        ([(33.0, 19.2), (35.2, 17.2), (36.5, 15.0), (37.4, 13.0), (38.3, 11.2)], 0.75),
        ([(17.6, 18.6), (16.4, 16.4), (15.4, 14.2)], 0.6),
        ([(30.0, 18.6), (31.2, 16.4), (32.2, 14.2)], 0.6),
        ([(20.0, 18.4), (19.4, 16.2)], 0.5),
        ([(27.8, 18.4), (28.2, 16.2)], 0.5),
    ]
    for i, (path, radius) in enumerate(spines):
        pts = [(f.X(c), f.Y(r), 3.1 + 0.35 * j) for j, (c, r) in enumerate(path)]
        pts = w.catmull(pts, 0.4)
        last = len(pts) - 1
        w.tube(f"spine{i}", pts, [radius * (1.0 - 0.8 * (j / last) ** 1.3) for j in range(len(pts))], spine_mat,
               10, squash=0.8)
    # The webbing between the spines' roots: low fins along the fan's edge.
    for s in (-1, 1):
        web = [(s * x, y) for x, y in ((3.0, f.Y(17.0)), (9.3, f.Y(17.2)), (11.2, f.Y(16.0)), (10.6, f.Y(18.3)),
                                       (4.0, f.Y(18.8)))]
        if s < 0:
            web = web[::-1]
        v.relief(f"web{s}", [web], fin_mat, sh.pillow_profile(0.5, 0.5), bottom=0.5, base=2.9, spacing=0.4)

    # Paint the body by the sprite's shades (its light along the middle).
    n.paint_shades(body, lambda x, y: shade(x, y) + 1.2 * math.exp(-(x / 1.6) ** 2), bands, wall_drop=1.5)


def fish_piece(name, sprite, left):
    box = (-24.0, 0.0, -14.0, 14.0) if left else (0.0, 24.0, -14.0, 14.0)
    centre = (-12.0, 0.0) if left else (12.0, 0.0)
    cols = (0, 24) if left else (24, 48)
    return (name, box, centre, lambda: FISH.mask((cols[0], cols[1], 0, 28)))


v.pieced("coral_fish", fish_whole, (48, 28), [fish_piece("coral_fish_left", 229, True),
                                              fish_piece("coral_fish_right", 231, False)])



# --- T 203 (and T 241, its mirror image): the seahorses ----------------------------------------------

SEAHORSE = v.Frame(art.SEAHORSE, 24, (12, 14))


def seahorse(mirrored):
    """A brown seahorse in profile, as the sprite draws it (203 faces left; 241, its mirror image, right):
    a ridged body arching from the crowned head down to the curled tail, a long snout, a pale eye and a
    frilly pale blue fin at the back of its head."""
    f = SEAHORSE
    paint = v.Painter("seahorse", shades={1: (0, 2, 4, 5, 6, 7, 8, 9, 0xb, 0xd)}, metallic=0.25, roughness=0.45)
    brown = paint(0x16)
    fin = pal("seahorse_fin", 0x3c, metallic=0.1, roughness=0.2, glow=0.35)
    fin_light = pal("seahorse_fin_light", 0x3e, metallic=0.1, roughness=0.2, glow=0.5)
    eye = pal("seahorse_eye", 0x3e, metallic=0.1, roughness=0.1, glow=0.4)
    pupil = pal("seahorse_pupil", 0x10, metallic=0.2, roughness=0.1)
    shade = f.shade(1, blur=0)

    # The body: every brown pixel, round in section, its rings standing out where the sprite draws them
    # lighter.
    def body_z(x, y, z):
        return z + 0.22 * (shade(x, y) - 5.5) * min(1.0, (z - 0.2) / 1.5)
    keep = lambda i, c, r: i >> 4 == 1 or (i >> 4 == 3 and not (c >= 13))
    body = v.relief("body", v.outlines_of(f, keep, grow=0.1, smooth=1), brown,
                    sh.round_profile(0.8, max_height=4.6, min_height=0.6), bottom=0.75, base=0.0, z_fn=body_z,
                    spacing=0.55)
    v.paint_sprite(body, f, paint, wall_steps=-1, keep=lambda i: i >> 4 == 1, default=brown)

    # The crown of spines on the head's top.
    for i, (c, r, h) in enumerate(((11.5, 0.6, 1.2), (9.5, 1.0, 1.0), (13.0, 0.4, 0.9))):
        w.tube(f"crown{i}", [(f.X(c), f.Y(r + 1.4), 3.2), (f.X(c) + 0.2, f.Y(r), 3.6 + h)], [0.55, 0.15], paint(0x19),
               8)

    # The eye on the head's side, pale with a dark pupil.
    ex, ey = f.X(7.6), f.Y(2.6)
    w.sphere("eye", (ex, ey, 3.6), (1.15, 1.0, 0.8), eye, 14, 7)
    w.sphere("pupil", (ex - 0.25, ey + 0.05, 4.2), (0.5, 0.5, 0.35), pupil, 10, 5)

    # The frilly fin at the back of the head: three pale blue blades fanning out behind it.
    for i, (dy, dx) in enumerate(((2.2, 0.6), (0.0, 1.2), (-2.4, 0.8))):
        root = (f.X(12.8), f.Y(4.0) + dy, 3.2)
        tip = (root[0] + dx + 1.0, root[1] + dy * 0.35, 3.8)
        pts = w.catmull([root, ((root[0] + tip[0]) / 2, (root[1] + tip[1]) / 2 + 0.15, 3.9), tip], 0.4)
        w.tube(f"fin{i}", pts, [0.65 - 0.5 * j / (len(pts) - 1) for j in range(len(pts))],
               fin_light if i == 1 else fin, 10, squash=0.4)
    # The small fin on the back of the neck (columns 12-14, rows 8-11).
    dorsal = [(f.X(11.0), f.Y(8.6)), (f.X(13.6), f.Y(8.2)), (f.X(14.4), f.Y(9.6)), (f.X(12.8), f.Y(11.4)),
              (f.X(11.0), f.Y(11.6))]
    v.relief("dorsal", [dorsal], paint(0x17), sh.pillow_profile(0.7, 0.5), bottom=0.5, base=1.6, spacing=0.35)
    if mirrored:
        v.mirror_scene(0.0)


v.model("coral_seahorse_left", mask=lambda: SEAHORSE.mask())(lambda: seahorse(False))
v.model("coral_seahorse_right", mask=lambda: v.Frame(art.SEAHORSE_R, 24, (12, 14)).mask())(lambda: seahorse(True))


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
