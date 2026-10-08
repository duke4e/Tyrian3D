"""Wave 3, batch P of the enemy models: the remaining enemies of sheet 2 (episode 1: TYRIAN, HOLES, TYRIAN X,
and SAVARA, ASSASSIN, BONUS, GYGES, EYESPY), modelled as their sprites look (models.cfg: yaw=0). Objects the
game draws from several sprites are built whole and cut into the sprites' pieces (models.cfg: origin);
the level files' enemy events say how the pieces are placed.

- walker_left, walker_right (2 85, 2 87): the grey and blue machine of TYRIAN, HOLES, BONUS, ASSASSIN
  and SAVARA, left and right halves: a grey hull with a steel-blue window and a glowing vent at its
  back, orange lamps on its shoulders, bent blue fins, two long steel-blue legs reaching down the
  screen and two dark struts, a neck ending in a grey ball with a red eye (origin). The levels often
  put the grabber (2 123, 125: wave2_f_more.py) 16 pixels below it on the same layer (the events give
  85/87 y - 16), as the machine's lower half; the ball then sits on the grabber's neck.
- rod_butt, rod_segment, rod_tip (2 1, 2 3, 2 5) and their mirror images rod_tip_l, rod_segment_l,
  rod_butt_r (2 7, 2 9, 2 11): the long grey rods of TYRIAN that push in from the screen's sides,
  red collars and bands round them and a polished tip: the events lay a butt, a row of segments (the
  levels repeat 3 and 9 every 24 pixels) and a tip side by side, so the segments' ends are the plain
  rod and meet (origin).
- hood_turret (2 153): the hooded turret sunk in the rocks of TYRIAN: a dark pyramid hood over a red
  band with a red eye that glows (its frames brighten the eye), red claws below it, grey boulders and
  tan stones round it (origin, as TYRIAN's purple pads near it).

The ground sprites drawn on rock and dirt (the purple pads and the eye block, the golden domes, the
golden pyramid, the red works) are in wave3_p_ground.py; the shared helpers in wave3_p_kit.py, the
pixel art in wave3_p_art.py.

usage: Blender -b --factory-startup -P wave3_p.py -- [--only name,name] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1] [--whole walker,rod --preview <prefix>]
"""
import math
import os
import sys

from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_p_kit as w  # noqa: E402
from wave3_p_kit import art, k, sh, pal, model, whole, grid, regions, ramp, shade  # noqa: E402


# --- 2 85, 2 87: the walker (48 x 28, its axis at x = -1) -------------------------------------------

AX = -1.0


def X(col):
    return col + 0.5 - 24


def Y(row):
    return 14 - (row + 0.5)


def walker_labels(g):
    """The walker's pixels by part: L legs, E orange lamps, B blue fins, W window, O the vent at the
    back, N the neck, P the ball, R its red eye, S the struts, H the hull."""
    def label(v, c, r):
        rp = ramp(v)
        if rp == 7 and r == 0:
            return "O"
        if rp == 7 and r <= 6 and (c <= 14 or c >= 31):
            return "E"
        if rp == 9 and not (19 <= c <= 26):
            return "B"
        if 19 <= c <= 26 and 2 <= r <= 7 and rp in (3, 8, 9):
            return "W"
        if r >= 18 and 18 <= c <= 27:
            return "R" if rp == 7 else "P"
        if (c <= 10 or c >= 35) and r >= 3:
            return "L"
        if 9 <= r <= 17 and (11 <= c <= 15 or 30 <= c <= 34):
            return "S"
        if 10 <= r <= 17 and 16 <= c <= 29:
            return "N"
        return "H"
    return regions(g, label)


def walker_whole():
    g = grid(art.SHIP, 48)
    rows = walker_labels(g)
    o = (24, 14)
    grey = pal("wlk_grey", 0x07, metallic=0.6, roughness=0.32)
    mid = pal("wlk_mid", 0x09, metallic=0.6, roughness=0.3)
    light = pal("wlk_light", 0x0b, metallic=0.6, roughness=0.26)
    dark = pal("wlk_dark", 0x03, metallic=0.5, roughness=0.45)
    leg = pal("wlk_leg", 0x37, metallic=0.55, roughness=0.3)
    leg_light = pal("wlk_leg_light", 0x3b, metallic=0.55, roughness=0.26)
    leg_dark = pal("wlk_leg_dark", 0x63, metallic=0.5, roughness=0.4)
    steel = pal("wlk_steel", 0x3a, metallic=0.5, roughness=0.3)
    glass = pal("wlk_glass", 0x3a, metallic=0.35, roughness=0.06)
    glass_hi = pal("wlk_glass_hi", 0x88, metallic=0.2, roughness=0.05)
    blue = pal("wlk_blue", 0x9b, metallic=0.35, roughness=0.22, glow=0.7)
    blue_hi = pal("wlk_blue_hi", 0x9d, metallic=0.3, roughness=0.2, glow=1.2)
    orange = pal("wlk_lamp", 0x79, metallic=0.1, roughness=0.3, glow=1.4)
    orange_hot = pal("wlk_lamp_hot", 0x7c, metallic=0.0, roughness=0.2, glow=2.4)
    red = pal("wlk_red", 0x76, metallic=0.1, roughness=0.25, glow=1.2)
    red_hot = pal("wlk_red_hot", 0x7b, metallic=0.0, roughness=0.15, glow=2.2)

    # The hull: the middle block, its back (row 0) against the sprite's top, the shoulders either side,
    # higher in the middle.
    hull = [(X(14) - 0.5, Y(0) + 0.5), (X(31) + 0.5, Y(0) + 0.5), (X(34) + 0.5, Y(1) + 0.5), (X(35) + 0.5, Y(3)),
            (X(35) + 0.3, Y(7) - 0.3), (X(30) + 0.5, Y(9) - 0.3), (X(15) - 0.5, Y(9) - 0.3), (X(10) - 0.3, Y(7) - 0.3),
            (X(10) - 0.5, Y(3)), (X(11) - 0.5, Y(1) + 0.5)]
    hull = list(reversed(hull)) if sum(hull[i][0] * hull[(i + 1) % len(hull)][1] - hull[(i + 1) % len(hull)][0] *
                                       hull[i][1] for i in range(len(hull))) < 0 else hull
    body = sh.inflate("hull", [hull], grey, sh.pillow_profile(5.6, 1.6, crown=0.6), bottom=0.0, base=1.2, rim=0.2,
                      spacing=0.9, z_fn=lambda x, y, z: 1.2 + (z - 1.2) * (0.7 + 0.3 * sh.smoothstep(10.5, 6.0,
                                                                                                    abs(x - AX))))
    k.smooth(w.simplify_bottom(body), 45)
    w.paint_faces(body, lambda c, n: light if n.z > 0.45 and n.x < -0.4 else mid if n.z > 0.45 and n.y > 0.4 else
                  dark if n.y < -0.6 or n.x > 0.75 else None)

    def hull_z(x, y):
        return sh.surface_z(body, x, y, 6.0)
    top_z = hull_z(AX, Y(4.5))
    # Raised plates either side of the window, lit on the left.
    for side, (c0, c1) in ((-1, (14, 18)), (1, (27, 31))):
        cx = (X(c0) + X(c1)) / 2
        plate = w.block(f"plate{side}", (cx, Y(4.5)), 2.6, 3.3, 1.0, mid, rounding=0.45, power=4.0, segments=16,
                        z0=hull_z(cx, Y(4.5)) - 0.4)
        w.paint_faces(plate, lambda c, n: light if n.x < -0.4 else None)
    # The window: steel-blue glass in a dark frame, a pale glint along its upper left.
    w.rounded_box("window_frame", (AX, Y(4.5), top_z), (7.6, 7.4, 1.4), dark, bevel=0.5)
    w.rounded_box("window", (AX, Y(4.5), top_z + 0.45), (6.0, 6.0, 1.4), glass, bevel=0.55)
    w.tube("window_glint", [(X(20) + 0.3, Y(6.5), top_z + 1.2), (X(20) + 0.3, Y(3), top_z + 1.2),
                            (X(23), Y(2.4), top_z + 1.2)], 0.4, glass_hi, 6)
    # The vent at the back: a glowing orange slot in the hull's end.
    w.rounded_box("vent_housing", (AX, Y(1.0), 4.2), (9.6, 2.4, 4.6), dark, bevel=0.5)
    w.rounded_box("vent", (AX, Y(0.4), 4.2), (7.6, 1.4, 3.0), orange, bevel=0.4)
    w.rounded_box("vent_hot", (AX, Y(0.2), 4.4), (4.0, 0.8, 1.6), orange_hot, bevel=0.3)

    # The neck under the hull, narrowing down the screen, and the rod to the ball.
    neck = [(X(16) - 0.4, Y(9)), (X(29) + 0.4, Y(9)), (X(29) + 0.2, Y(12)), (X(27) + 0.5, Y(13) - 0.2),
            (X(26) + 0.5, Y(14.5)), (X(19) - 0.5, Y(14.5)), (X(18) - 0.5, Y(13) - 0.2), (X(16) - 0.2, Y(12))]
    nb = sh.inflate("neck", [neck], dark, sh.round_profile(0.55, max_height=3.2), bottom=0.0, base=1.6, rim=0.2,
                    spacing=0.8)
    k.smooth(w.simplify_bottom(nb), 50)
    # A light spine down the neck's middle, from under the window to the rod.
    w.tube("spine", w.catmull([(AX, Y(8.5), 5.4), (AX, Y(11.0), 5.1), (AX, Y(13.5), 4.4), (AX, Y(14.8), 3.9)], 0.5),
           1.25, grey, 10, squash=0.7)
    w.tube("spine_hi", [(AX - 0.45, Y(9.0), 6.2), (AX - 0.45, Y(13.0), 5.2)], 0.35, light, 6)
    for side, col in ((-1, 18), (1, 27)):  # steel-blue ribs down the neck's sides
        w.tube(f"neck_rib{side}", [(X(col), Y(9.5), 4.0), (X(col), Y(13), 3.4)], 0.55, steel, 8)
    for side, col in ((-1, 20), (1, 25)):  # the red slits
        w.rounded_box(f"neck_slit{side}", (X(col), Y(11.5), 4.35), (0.9, 2.0, 0.6), red, bevel=0.25)
    w.tube("neck_rod", [(AX, Y(14), 3.2), (AX, Y(16.5), 3.0), (AX, Y(18.2), 3.2)], 1.25, grey, 10)
    w.tube("neck_rod_hi", [(AX - 0.4, Y(14.5), 4.1), (AX - 0.4, Y(17.8), 4.0)], 0.35, light, 6)
    # The ball and its red eye.
    bc = (AX, Y(21.5), 3.4)
    w.sphere("ball", bc, (3.9, 3.9, 3.1), mid, 20, 10)
    w.hoop("ball_rim", (AX, Y(21.0), 5.6), [(2.1, -0.4), (2.9, -0.2), (2.9, 0.25), (2.2, 0.35)], dark, 24)
    w.sphere("eye", (AX, Y(21.0), 5.7), (2.1, 2.0, 1.0), red, 14, 7)
    w.sphere("eye_hot", (AX - 0.5, Y(20.5), 6.3), (0.8, 0.7, 0.4), red_hot, 10, 5)

    # The orange lamps on the shoulders, glowing towards the back.
    for side, col in ((-1, 12), (1, 33)):
        x = X(col)
        w.lathe_axis(f"lamp{side}", [(0.0, 1.5), (0.6, 1.9), (4.0, 1.9), (4.6, 1.4), (5.0, 0.6)], orange,
                     (x, Y(6.5), 6.4), (0, 1, 0), 12)
        w.sphere(f"lamp_hot{side}", (x, Y(2.6), 7.3), (1.0, 1.4, 0.7), orange_hot, 12, 6)
        collar = w.hoop(f"lamp_collar{side}", (0, 0, 0), [(1.8, -0.5), (2.3, -0.4), (2.3, 0.4), (1.8, 0.5)], dark, 16)
        collar.data.transform(Matrix.Translation((x, Y(5.6), 6.4)) @ Matrix.Rotation(math.radians(90), 4, "X"))

    # The blue fins: bent bars from the hull's sides out over the shoulders and down into the struts.
    for side in (-1, 1):
        def mx(col):
            return X(col) if side < 0 else 2 * AX - X(col)
        path = w.catmull([(mx(16.5), Y(5.5), 7.0), (mx(13.0), Y(6.0), 7.2), (mx(11.2), Y(8.0), 6.6),
                          (mx(13.0), Y(9.6), 6.0), (mx(13.5), Y(12.0), 4.9), (mx(13.5), Y(14.5), 4.2)], 0.5)
        w.tube(f"fin{side}", path, 1.35, blue, 8, squash=0.6)
        w.tube(f"fin_hi{side}", w.catmull([(mx(16.0), Y(5.2), 7.75), (mx(13.2), Y(5.6), 7.9), (mx(11.6), Y(7.4), 7.4)],
                                          0.5), 0.42, blue_hi, 6)

    # The struts: grey frames round the fins' lower ends, a red light on their outer side.
    for side in (-1, 1):
        cx = X(13.0) if side < 0 else 2 * AX - X(13.0)
        frame = w.block(f"strut{side}", (cx, Y(13.0)), 2.6, 4.6, 3.6, dark, rounding=0.8, power=3.0, segments=16)
        w.paint_faces(frame, lambda c, n: grey if n.z > 0.5 and n.x < -0.3 else None)
        w.sphere(f"strut_light{side}", (cx + side * -2.2, Y(11.5), 2.9), (0.75, 0.8, 0.7), orange, 10, 6)

    # The legs: long steel-blue bars from under the shoulders' knuckles down to the sprite's bottom,
    # sloping down to their feet, a dark groove along each.
    sections = [(3.0, 8.6, 1.4, 4.6, 1.2), (5.0, 8.0, 2.2, 4.0, 1.6), (8.0, 7.2, 2.8, 3.0, 1.9), (12.0, 6.9, 3.0, 2.2, 1.9),
                (17.0, 6.9, 3.0, 1.8, 1.8), (21.0, 7.0, 2.6, 1.6, 1.6), (24.0, 7.3, 2.0, 1.4, 1.3),
                (25.6, 7.6, 1.0, 1.2, 0.8)]
    for side in (-1, 1):
        def lx(col):
            return X(col) if side < 0 else -3.0 - X(col)
        rings = [k.ring(Y(r), hw, 1.0, 20, z=zc, x=lx(c), top=top, bottom=max(0.05, zc - 0.5), power=2.6)
                 for r, c, hw, zc, top in sections]
        last = sections[-1]
        lb = k.loft(f"leg{side}", rings, leg, start_point=(lx(sections[0][1]), Y(2.4), 4.6),
                    end_point=(lx(last[1]), Y(26.2), 1.1))
        k.smooth(lb, 50)
        w.paint_faces(lb, lambda c, n: leg_light if n.z > 0.35 and n.x < -0.45 else
                      leg_dark if n.z > 0.35 and n.x > 0.55 else None)
        groove = [(lx(c) + 0.5, Y(r), zc + top - 0.12) for r, c, hw, zc, top in sections[1:-1]]
        w.tube(f"leg_groove{side}", w.catmull(groove, 0.6), 0.4, leg_dark, 6, squash=0.6)
        # A steel-blue knuckle where each leg leaves its shoulder.
        w.sphere(f"knee{side}", (X(8.0) if side < 0 else X(37.0), Y(6.0), 6.3), (1.7, 1.9, 1.3), steel, 14, 8)


@whole("walker", (48, 28))
def walker_preview():
    walker_whole()


@model("walker_left", [85])
def walker_left():
    walker_whole()
    w.bake()
    w.piece(w.meshes(), -24, 0, -14, 14)


@model("walker_right", [87])
def walker_right():
    walker_whole()
    w.bake()
    w.piece(w.meshes(), 0, 24, -14, 14)


# --- 2 1, 3, 5 and their mirror images 2 7, 9, 11: the rods (72 x 28 whole) ----------------------------
# The whole rod runs along x from -36 (its butt, sprite 1) to 36 (the tip's end, sprite 5); sprite 3 is
# x -12..12, which the levels repeat: its ends are the plain rod, so the copies meet. t = x + 36.

ROD_Z = 8.0  # the axis's height: the big collars rest on the ground
ROD_Y = 1.0  # the axis's y (rows 7-18 of the sprites)


def rod_whole():
    steel = pal("rod_steel", 0x08, metallic=0.65, roughness=0.3)
    tip_mat = pal("rod_tip", 0x0b, metallic=0.8, roughness=0.18)
    dark = pal("rod_dark", 0x02, metallic=0.5, roughness=0.5)
    red = pal("rod_red", 0x48, metallic=0.4, roughness=0.3)
    red_light = pal("rod_red_light", 0x4b, metallic=0.4, roughness=0.26)
    brown = pal("rod_brown", 0x12, metallic=0.3, roughness=0.5)
    necks = [(11.0, 14.0), (36.0, 39.0), (44.0, 47.0)]
    collars = [(18.2, 23.8, 8.0), (27.0, 31.0, 7.0)]
    r0 = 6.0
    # The rod: a rounded butt, necks where the red bands sit, the long tip.
    prof = [(0.0, 0.0), (0.15, 3.4), (0.6, 5.0), (1.4, 5.8), (2.4, r0)]
    for a, b in necks:
        prof += [(a - 0.6, r0), (a, 5.4), (a + 0.6, 4.3), (b - 0.6, 4.3), (b, 5.4), (b + 0.6, r0)]
    prof += [(48.0, r0), (51.0, 5.85), (54.0, 5.5), (57.0, 4.9), (60.0, 4.1), (63.0, 3.0), (66.0, 1.8), (68.0, 0.7),
             (68.6, 0.0)]
    rod = w.lathe_axis("rod", prof, steel, (-36.0, ROD_Y, ROD_Z),
                       (1, 0, 0), 28, smooth_angle=40)
    # The tip is polished; a dark seam where it starts.
    w.paint_faces(rod, lambda c, n: tip_mat if c.x > 12.6 else None)
    w.lathe_axis("tip_seam", [(0.0, 6.05), (0.5, 6.15), (1.0, 6.05)], dark, (12.0, ROD_Y, ROD_Z), (1, 0, 0), 28)
    # The butt's dark cap.
    w.lathe_axis("butt_cap", [(0.0, 0.0), (0.05, 2.6), (0.35, 3.3), (0.6, 3.6)], dark, (-36.05, ROD_Y, ROD_Z), (1, 0, 0),
                 20)
    # Red bands round the necks.
    for i, (a, b) in enumerate(necks):
        band = w.lathe_axis(f"band{i}", [(0.0, 4.2), (0.3, 4.75), (b - a - 1.0 - 0.3, 4.75), (b - a - 1.0, 4.2)], red,
                            (-36.0 + a + 0.5, ROD_Y, ROD_Z), (1, 0, 0), 24)
        w.paint_faces(band, lambda c, n: red_light if n.z > 0.55 and n.x <= 0.2 else None)
    # The red collars, a dark lip either side; the big one sits on a brown clamp.
    for i, (a, b, rc) in enumerate(collars):
        x0 = -36.0 + a
        coll = w.lathe_axis(f"collar{i}", [(0.0, r0 - 0.2), (0.25, rc - 0.6), (0.6, rc), (b - a - 0.6, rc),
                                          (b - a - 0.25, rc - 0.6), (b - a, r0 - 0.2)], red, (x0, ROD_Y, ROD_Z),
                            (1, 0, 0), 28, smooth_angle=35)
        w.paint_faces(coll, lambda c, n: red_light if n.z > 0.6 else None)
        for x in (x0 + 0.15, x0 + (b - a) - 0.15):
            w.lathe_axis(f"collar_lip{i}_{x:.0f}", [(0.0, rc - 0.4), (0.3, rc + 0.15), (0.6, rc - 0.4)], dark,
                         (x - 0.3, ROD_Y, ROD_Z), (1, 0, 0), 28)
        foot_h = ROD_Z - rc + 1.2
        w.rounded_box(f"clamp{i}", (x0 + (b - a) / 2, ROD_Y - 0.5, foot_h / 2), (b - a - 0.6, 6.0, foot_h), brown,
                      bevel=0.4)


@whole("rod", (72, 28))
def rod_preview():
    rod_whole()


def rod_piece(x0, mirror):
    rod_whole()
    w.bake()
    w.piece(w.meshes(), x0, x0 + 24, -14, 14)
    if mirror:
        w.mirror_all()


@model("rod_butt", [1])
def rod_butt():
    rod_piece(-36, False)


@model("rod_segment", [3])
def rod_segment():
    rod_piece(-12, False)


@model("rod_tip", [5])
def rod_tip():
    rod_piece(12, False)


@model("rod_tip_l", [7])
def rod_tip_l():
    rod_piece(12, True)


@model("rod_segment_l", [9])
def rod_segment_l():
    rod_piece(-12, True)


@model("rod_butt_r", [11])
def rod_butt_r():
    rod_piece(-36, True)


# --- 2 153: the hooded turret in the rocks --------------------------------------------------------------

def P(col, row):
    """A pixel corner (column, row) of a 24 x 28 sprite as (x, y)."""
    return (col - 12.0, 14.0 - row)


@model("hood_turret", [153])
def hood_turret():
    """A dark pyramid hood pointing up the screen, its ridge catching the light, sunk in grey rocks
    with tan stones; its front slopes down to a red band with a glowing red eye in the middle, a dark
    jaw below and two red claws curling down either side."""
    g = grid(art.TURRET, 24)
    hood_mat = pal("hood_grey", 0x04, metallic=0.55, roughness=0.35)
    hood_light = pal("hood_light", 0x08, metallic=0.55, roughness=0.3)
    ridge_mat = pal("hood_ridge", 0x0c, metallic=0.6, roughness=0.25)
    band = pal("hood_band", 0x46, metallic=0.4, roughness=0.3)
    band_light = pal("hood_band_light", 0x49, metallic=0.4, roughness=0.28)
    jaw = pal("hood_jaw", 0x02, metallic=0.5, roughness=0.4)
    claw = pal("hood_claw", 0x45, metallic=0.4, roughness=0.32)
    claw_light = pal("hood_claw_light", 0x48, metallic=0.4, roughness=0.3)
    eye = pal("hood_eye", 0x79, metallic=0.0, roughness=0.15, glow=1.8)
    eye_hot = pal("hood_eye_hot", 0x7c, metallic=0.0, roughness=0.1, glow=3.0)
    socket = pal("hood_socket", 0x41, metallic=0.3, roughness=0.4)

    # The rocks round it, low under the hood.
    def is_rock(v, c, r):
        if v is None:
            return False
        x, y = c + 0.5 - 12, 14 - r - 0.5
        inside_hood = y < 11.8 and y > -4.0 and abs(x + 0.3) < 0.4 + (11.8 - y) * 0.95 and abs(x + 0.3) < 9.0
        return ramp(v) in (0, 0xa) and not inside_hood and not (r >= 17 and ramp(v) == 4)
    w.grey_rocks("rocks", g, is_rock, prefix="hood", keep_base=lambda v, c, r: v is not None)

    # The hood: diamond sections along y, its ridge highest just behind the band.
    sections = [(11.9, 0.3, 0.6), (10.5, 1.4, 2.2), (8.5, 3.0, 3.9), (6.5, 4.6, 5.4), (4.5, 6.3, 6.9), (2.8, 7.8, 8.0),
                (1.8, 8.5, 8.2), (0.6, 8.8, 7.4), (-0.8, 8.7, 5.9), (-2.2, 8.0, 4.0), (-3.2, 6.6, 2.0), (-3.7, 5.0, 0.6)]
    rings = [k.ring(y, hw, 1.0, 24, z=0.3, x=-0.3, top=top, bottom=0.3, power=1.25) for y, hw, top in sections]
    split = 6  # the section at y = 1.8: the band starts there
    hood = k.loft("hood", rings[:split + 1], hood_mat, start_point=(-0.3, 12.2, 0.4), end_point=(-0.3, 1.0, 1.0))
    k.smooth(hood, 28)
    w.paint_faces(hood, lambda c, n: hood_light if n.x < -0.25 and n.z > 0.3 else None)
    front = k.loft("band", rings[split:], band, start_point=(-0.3, 2.6, 1.0), end_point=(-0.3, -3.9, 0.4))
    k.smooth(front, 28)
    w.paint_faces(front, lambda c, n: band_light if n.z > 0.7 else None)
    # The ridge: a bright edge along the top from the point to the band.
    ridge = [(-0.3, 11.6, 1.05), (-0.3, 8.5, 4.35), (-0.3, 4.5, 7.35), (-0.3, 2.4, 8.55)]
    w.tube("ridge", w.catmull(ridge, 0.5), 0.42, ridge_mat, 6)
    # The eye in the band's middle: a dark socket and the glowing lens.
    ex, ey, ez = -0.3, -0.2, 6.1
    w.sphere("socket", (ex, ey, ez - 0.4), (3.4, 2.4, 1.6), socket, 18, 8)
    w.sphere("eye", (ex, ey - 0.2, ez + 0.1), (2.6, 1.9, 1.5), eye, 18, 9)
    w.sphere("eye_hot", (ex - 0.4, ey + 0.1, ez + 1.2), (1.1, 0.8, 0.5), eye_hot, 10, 5)
    # The dark jaw under the band.
    w.block("jaw", (-0.3, -4.7), 3.0, 1.6, 1.8, jaw, rounding=0.6, power=3.0, segments=20)
    # The red claws curling down either side, thinning to their tips.
    for side, pts in ((-1, [(7.5, 16.8, 3.0), (5.2, 20.0, 2.6), (4.3, 23.0, 2.0), (5.4, 25.2, 1.5), (7.2, 25.6, 1.2)]),
                      (1, [(15.5, 16.8, 3.0), (17.8, 20.0, 2.6), (18.7, 23.0, 2.0), (17.6, 25.2, 1.5),
                           (15.8, 25.6, 1.2)])):
        path = w.catmull([(c - 12.0, 14.0 - r, z) for c, r, z in pts], 0.5)
        n = len(path)
        radii = [1.7 * (1.0 - 0.6 * (i / (n - 1)) ** 1.5) for i in range(n)]
        cl = w.tube(f"claw{side}", path, radii, claw, 10)
        w.paint_faces(cl, lambda c, nn: claw_light if nn.z > 0.6 else None)


w.run()
