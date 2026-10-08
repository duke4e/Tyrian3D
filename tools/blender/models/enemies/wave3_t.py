"""Wave 3, batch T of the enemy models: the remaining enemies of sheet V (episode 2's GEM WAR, GRYPHON, MISTAKES
and MARKERS, episode 4's UNDERDELI and DREAD-NOT, episode 5's STATION), modelled as their sprites look
(models.cfg: yaw=0). Objects the game draws from several sprites are built whole and cut into the sprites'
pieces (models.cfg: origin); the level files' enemy events say how the pieces are placed.

- arm_bridge (V 91): the middle of GEM WAR's, GRYPHON's and STATION's blue structure, between its arms
  with the red balls (V 89 and V 93, arm_ball_left and arm_ball_right of wave1_b.py; the events put
  89, 91 and 93 side by side, 24 pixels apart, on one layer): the arms' housings end in shoulders
  either side, a glossy blue saddle between them, a lip in front over a vent glowing red behind its
  slats and two emitter nozzles under it whose tips glow red (the frames 129 flash a red beam from
  them when it fires; the model keeps the vent and the tips glowing). Built in the arms' coordinates
  so the pieces meet (origin).
- claw_body_l, claw_hook_l (V 44, V 46) and their mirror images claw_hook_r, claw_body_r (V 85, V 87):
  the grey claw ship of GRYPHON, MISTAKES and STATION (custom enemies: the events put 44 and 46, and
  85 and 87, side by side 24 pixels apart; the left ones fly in from the screen's left, the right ones
  from its right): a ribbed housing like the blue arms', a glowing red ball at its outer end, a
  sloping belly with a red lamp, and a long round arm reaching inwards that bends down into a hook,
  red lights under it (origin).
- cannon_barrel, cannon_breech (V 14, V 16) and their mirror images cannon_breech_r, cannon_barrel_r
  (V 167, V 169): the cannons of UNDERDELI and DREAD-NOT, a long steel barrel with a blue band, its
  breech between two swept fins on a hub, on a round blue-grey turntable (the events put 14 and 16,
  and 167 and 169, side by side; DREAD-NOT adds a second barrel, 14 or 169 alone, below each). The
  frames 52 and 207 recoil the barrel by a pixel: the models keep it still (origin).

The stand-alone enemies of sheet V are in wave3_t_ships.py; the shared helpers in wave3_t_kit.py, the
pixel art in wave3_t_art.py.

usage: Blender -b --factory-startup -P wave3_t.py -- [--only name,name] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1] [--whole arms,claw,cannon --preview <prefix>]
"""
import math
import os
import sys

from mathutils import Matrix

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_t_kit as w  # noqa: E402
from wave3_t_kit import pal, model, whole, smoothstep, bake  # noqa: E402


def X(col, ox=12):
    """A pixel column's centre."""
    return col + 0.5 - ox


def Y(row, oy=14):
    """A pixel row's centre."""
    return oy - (row + 0.5)


# --- V 91: the middle of the blue structure ------------------------------------------------------------
# In V 91's coordinates; the arms (wave1_b.arm_ball) stand at x = -24 and x = 24, their housings reaching
# to x = -11.2 and 11.2, their tops 9 high at the back sloping to 5.6 at the front (housing_top).

def housing_top(y):
    """The arms' housing top (wave1_b.arm_ball's housing_top)."""
    return 9.0 - 3.4 * smoothstep(2.5, -10.5, y)


def bridge_whole(with_arms=False):
    if with_arms:
        import_arms()
    steel = pal("arm_steel", 56, metallic=0.55, roughness=0.35)
    light = pal("arm_light", 59, metallic=0.55, roughness=0.3)
    dark = pal("arm_dark", 53, metallic=0.5, roughness=0.45)
    gloss = pal("brg_gloss", 0x3b, metallic=0.6, roughness=0.22)
    gloss_hi = pal("brg_gloss_hi", 0x3d, metallic=0.6, roughness=0.18)
    plate = pal("brg_plate", 0x3a, metallic=0.55, roughness=0.3)
    seam = pal("brg_seam", 0x34, metallic=0.4, roughness=0.5)
    vent = pal("brg_vent", 0x44, metallic=0.2, roughness=0.4, glow=0.9, emission=(150, 20, 6))
    slat = pal("brg_slat", 0x38, metallic=0.55, roughness=0.32)
    tip = pal("brg_tip", 0x76, metallic=0.1, roughness=0.25, glow=1.6)
    lamp = pal("brg_lamp", 0x46, metallic=0.2, roughness=0.3, glow=0.8, emission=(170, 40, 20))

    # The shoulders: the housings' ends, 4 pixels into this sprite, flush with the arms' tops (a hair
    # lower where they overlap); a seam where they meet the saddle.
    for side in (-1, 1):
        x_out, x_in = 14.2, 8.15
        poly = [(-x_out, -1.1), (-x_in - 0.4, -1.1), (-x_in, -0.5), (-x_in, 6.9), (-x_in - 0.5, 7.45), (-x_out, 7.45)]
        if side > 0:
            poly = [(-x, y) for x, y in poly]
        body = w.cushion(f"shoulder{side}", w.ccw(poly), steel, lambda x, y: housing_top(y) - 0.04, rounding=1.3,
                         spacing=0.45)
        w.paint_faces(body, lambda c, n: light if c.z > 8.55 and n.z > 0.6 else None)
        # A red lamp on the housing's side low down (V 91's columns 0 and 23, rows 19-20).
        w.sphere(f"lamp{side}", (side * 11.15, Y(19.5), 2.8), (0.75, 0.95, 0.85), lamp, 12, 6)
    # The seams between the shoulders and the saddle.
    for side in (-1, 1):
        w.rounded_box(f"seam{side}", (side * 8.0, 3.1, 3.6), (0.9, 8.6, 7.0), seam, bevel=0.3)

    # The saddle: a glossy blue hump along x between the shoulders, highest in the middle.
    secs = []
    for x in [-8.6] + [i * 0.6 for i in range(-14, 15)] + [8.6]:
        f = 1.0 - (abs(x) / 8.6) ** 2
        secs.append((x, 2.75, 3.4, 3.45, 3.25 + 0.75 * f, 3.4))
    saddle = w.loft_x("saddle", secs, gloss, segments=36, power=2.3)
    gloss_mid = pal("brg_gloss_mid", 0x3c, metallic=0.6, roughness=0.2)
    back = pal("brg_back", 0x38, metallic=0.55, roughness=0.3)
    # Shades as the sprite's: an oval glint on the crest (rows 9-11), lighter round it, the back darker.
    w.paint_faces(saddle, lambda c, n: gloss_hi if n.z > 0.75 and (c.x / 3.6) ** 2 + ((c.y - 3.4) / 1.5) ** 2 < 1 else
                  gloss_mid if n.z > 0.6 and (c.x / 6.6) ** 2 + ((c.y - 3.0) / 2.6) ** 2 < 1 else
                  back if n.y > 0.55 else None)

    # The ledge in front of it, across the whole width (row 14), and the lip below (rows 15-17).
    w.loft_x("ledge", [(x, -0.75, 4.4, 0.75, 0.75, 0.75) for x in (-11.4, -10.8, 0.0, 10.8, 11.4)], plate,
             segments=14)
    lip = [(-8.1, -1.4), (8.1, -1.4), (8.1, -2.6), (7.2, -3.6), (6.4, -4.25), (-6.4, -4.25), (-7.2, -3.6), (-8.1, -2.6)]
    lp = w.cushion("lip", w.ccw(lip), plate, lambda x, y: 4.0 - 0.35 * smoothstep(-2.4, -4.2, y), rounding=0.9,
                   spacing=0.4)
    w.paint_faces(lp, lambda c, n: light if n.z > 0.7 and c.y > -3.0 and abs(c.x) < 7.0 else None)
    # The vent between the ledge and the lip: a red glow behind slats, posts at its ends.
    w.rounded_box("vent", (0.0, -1.55, 3.6), (8.4, 1.3, 1.6), vent, bevel=0.3)
    for x in (-2.5, 2.5):
        w.rounded_box(f"slat{x:+.0f}", (x, -1.5, 3.9), (0.8, 1.4, 1.9), slat, bevel=0.25)
    for side in (-1, 1):
        w.rounded_box(f"post{side}", (side * 6.5, -1.6, 4.0), (1.4, 1.6, 2.6), light, bevel=0.35)
    # The emitters under the lip, pointing down the screen, their tips glowing.
    for side in (-1, 1):
        x = side * 4.5
        w.lathe_axis(f"emitter{side}", [(0.0, 0.95), (1.4, 0.95), (1.9, 0.75), (2.3, 0.7), (2.4, 0.0)], dark,
                     (x, -3.6, 1.7), (0, -1, 0), 14)
        w.sphere(f"emitter_tip{side}", (x, -5.85, 1.7), (0.6, 0.45, 0.6), tip, 10, 5)


def import_arms():
    """The arms (wave1_b.arm_ball), built by wave1_b.py's own code at x = -24 and 24 (for --whole)."""
    import bpy
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wave1_b.py")
    src = open(path).read().rsplit("\nmain()", 1)[0]
    ns = {"__file__": path, "__name__": "wave1_b_preview"}
    exec(compile(src, path, "exec"), ns)
    for mirror, dx in ((True, 24.0), (False, -24.0)):  # the mirrored one first: arm_ball mirrors the scene
        before = set(bpy.context.scene.objects)
        ns["arm_ball"](mirror)
        bake()
        for o in [o for o in bpy.context.scene.objects if o not in before and o.type == "MESH"]:
            o.data.transform(Matrix.Translation((dx, 0, 0)))


@whole("arms", (72, 28))
def arms_preview():
    bridge_whole(with_arms=True)


@model("arm_bridge", [91])
def arm_bridge():
    bridge_whole()


# --- V 44, 46 and their mirror image V 85, 87: the grey claw ship (48 x 28, x = column - 24) -------------

def C(col):
    return col - 24.0


def R(row):
    return 14.0 - row


def claw_whole():
    grey = pal("claw_grey", 0x69, metallic=0.55, roughness=0.32)
    top = pal("claw_top", 0x6b, metallic=0.55, roughness=0.28)
    rib = pal("claw_rib", 0x6e, metallic=0.6, roughness=0.22)
    face = pal("claw_face", 0x66, metallic=0.5, roughness=0.38)
    dark = pal("claw_dark", 0x63, metallic=0.45, roughness=0.45)
    gloss = pal("claw_gloss", 0x6d, metallic=0.6, roughness=0.2)
    streak = pal("claw_streak", 0x6c, metallic=0.6, roughness=0.25)
    ball = pal("claw_ball", 0x74, metallic=0.25, roughness=0.2, glow=0.45)
    ball_hot = pal("claw_ball_hot", 0x7a, metallic=0.0, roughness=0.15, glow=1.6)
    red = pal("claw_red", 0x74, metallic=0.1, roughness=0.25, glow=1.4)

    # The housing: a deck high at the back, its front sloping down to the ridge (row 14).
    deck = [(C(8.3), R(15.2)), (C(8.3), R(6.6)), (C(9.0), R(6.0)), (C(13.0), R(6.0)), (C(13.6), R(5.0)), (C(22.2), R(5.0)),
            (C(23.2), R(6.0)), (C(25.4), R(6.6)), (C(25.4), R(15.2))]

    def deck_top(x, y):
        return 9.2 - 2.4 * smoothstep(4.0, -1.5, y) - 0.5 * smoothstep(-12.0, -16.5, x)
    body = w.cushion("deck", w.ccw(deck), grey, deck_top, rounding=1.5, spacing=0.45)
    w.paint_faces(body, lambda c, n: top if n.z > 0.85 and c.y > 3.6 else face if n.z < 0.55 and n.y < -0.3 else None)
    # The ribs on the deck (columns 9, 11, 13 and 15, rows 6-10) and the ridge along its front (row 14).
    for col in (9, 11, 13, 15):
        x = C(col) + 0.5
        w.tube(f"rib{col}", [(x, R(6.3), deck_top(x, 7.0) - 0.05), (x, R(10.4), deck_top(x, 3.6) - 0.05)], 0.45, rib, 8)
    w.tube("ridge", [(C(16.6), R(14.3), 6.75), (C(24.8), R(14.3), 6.75)], 0.5, streak, 8)

    # The belly under it: a lower plate reaching under the ball and narrowing to a keel at the front.
    belly = [(C(2.7), R(14.6)), (C(25.3), R(14.6)), (C(25.3), R(20.6)), (C(23.2), R(21.4)), (C(22.0), R(22.4)),
             (C(20.8), R(23.6)), (C(15.2), R(23.8)), (C(13.0), R(22.8)), (C(11.0), R(21.8)), (C(9.0), R(20.8)),
             (C(7.0), R(19.8)), (C(3.2), R(19.0)), (C(2.7), R(18.0))]
    bl = w.cushion("belly", w.ccw(belly), grey, lambda x, y: 5.2 - 1.2 * smoothstep(-2.0, -9.5, y), rounding=1.1,
                   spacing=0.45)
    w.paint_faces(bl, lambda c, n: face if n.z < 0.6 and n.y < -0.3 else None)
    w.tube("belly_streak", [(C(19.2), R(19.4), 4.45), (C(23.8), R(19.4), 4.45)], 0.45, streak, 8)
    w.sphere("belly_lamp", (C(24.6), R(19.9), 3.9), (0.8, 1.0, 0.8), red, 12, 6)

    # The red ball at the housing's outer end, sunk into its side, a dark collar round it.
    w.sphere("ball", (C(5.0), R(12.0), 5.4), (3.25, 3.95, 3.4), ball, 28, 14)
    w.sphere("ball_hot", (C(4.4), R(10.6), 7.75), (0.9, 1.0, 0.45), ball_hot, 12, 6)
    collar = w.hoop("ball_collar", (0, 0, 0), [(3.0, -0.6), (3.9, -0.5), (3.9, 0.5), (3.0, 0.6)], dark, 28)
    collar.data.transform(Matrix.Translation((C(8.3), R(12.0), 5.4)) @ Matrix.Rotation(math.radians(90), 4, "Y"))

    # The arm: a round bar from the housing's side reaching in, bending down into the hook.
    path = w.catmull([(C(22.0), 3.0, 5.4), (C(27.0), 2.9, 5.5), (C(33.0), 2.7, 5.5), (C(37.5), 2.1, 5.3),
                      (C(41.0), 0.3, 4.9), (C(42.4), -2.1, 4.4), (C(42.5), -3.9, 4.0)], 0.5)
    n = len(path)
    radii = []
    for i, p in enumerate(path):
        t = i / (n - 1)
        radii.append(3.85 - 0.45 * t if t < 0.85 else 3.47 - 3.0 * (t - 0.85))
    arm = w.tube("arm", path, radii, grey, 24, squash=0.9)
    w.paint_faces(arm, lambda c, nn: gloss if nn.z > 0.8 and C(30) < c.x < C(41) else top if nn.z > 0.8 else
                  face if nn.z < 0.3 and nn.y < -0.5 else None)
    # The lower finger under the arm (rows 15-17), red lights in the slot between them.
    w.loft_x("jaw", [(C(27.8), -2.3, 2.4, 1.3, 1.4, 2.4), (C(28.6), -2.4, 2.4, 1.6, 1.7, 2.4),
                     (C(34.0), -2.5, 2.4, 1.6, 1.8, 2.4), (C(38.5), -2.5, 2.4, 1.6, 1.8, 2.4),
                     (C(40.0), -2.5, 2.4, 1.4, 1.6, 2.4)], top, segments=16, power=2.6)
    for col in (32.5, 34.5, 36.5):
        w.sphere(f"slot_light{col:.0f}", (C(col), R(15.4), 4.1), (0.6, 0.55, 0.5), red, 10, 5)
    w.rounded_box("slot", (C(34.8), R(15.5), 3.4), (7.4, 1.1, 1.6), dark, bevel=0.3)


@whole("claw", (48, 28))
def claw_preview():
    claw_whole()


def claw_piece(x0, mirror):
    claw_whole()
    bake()
    if mirror:
        w.mirror_all()
    w.piece(w.meshes(), x0, x0 + 24, -14, 14)


@model("claw_body_l", [44])
def claw_body_l():
    claw_piece(-24, False)


@model("claw_hook_l", [46])
def claw_hook_l():
    claw_piece(0, False)


@model("claw_hook_r", [85])
def claw_hook_r():
    claw_piece(-24, True)


@model("claw_body_r", [87])
def claw_body_r():
    claw_piece(0, True)


# --- V 14, 16 and their mirror image V 167, 169: the cannon on its turntable (48 x 28, x = column - 24) ----

def cannon_whole():
    grey = pal("can_grey", 0x0a, metallic=0.65, roughness=0.28)
    grey_hi = pal("can_grey_hi", 0x0d, metallic=0.7, roughness=0.2)
    grey_mid = pal("can_grey_mid", 0x07, metallic=0.6, roughness=0.32)
    grey_dark = pal("can_grey_dark", 0x04, metallic=0.5, roughness=0.4)
    bore = pal("can_bore", 0x01, metallic=0.2, roughness=0.7)
    band = pal("can_band", 0x88, metallic=0.5, roughness=0.2)
    band_dark = pal("can_band_dark", 0x38, metallic=0.5, roughness=0.3)
    table = pal("can_table", 0x66, metallic=0.45, roughness=0.3)
    table_hi = pal("can_table_hi", 0x68, metallic=0.5, roughness=0.25)
    rim = pal("can_rim", 0x3a, metallic=0.55, roughness=0.25)

    # The turntable: a round blue-grey plate under the breech (centred at column 29, row 13).
    tc = (C(29.0), R(13.0))
    w.disc("table", tc, 12.0, 0.0, 1.4, table, segments=48, bevel=0.5)
    w.hoop("table_rim", (tc[0], tc[1], 1.25), [(11.0, -0.25), (11.9, -0.2), (11.9, 0.25), (11.0, 0.3)], rim, 48)
    w.disc("table_hub", tc, 6.5, 1.2, 2.0, table_hi, segments=40, bevel=0.4)

    # The barrel along x (rows 5-13), its muzzle at the sprite's left edge, a blue band near it.
    yc, zc = R(9.5), 6.6
    prof = [(0.0, 3.6), (0.3, 4.5), (1.0, 4.6), (4.6, 4.6), (5.0, 4.9), (5.9, 4.9), (6.1, 4.5), (25.5, 4.6), (26.0, 4.9),
            (26.5, 4.9)]
    barrel = w.lathe_axis("barrel", prof, grey, (C(0.0) + 0.2, yc, zc), (1, 0, 0), 28, smooth_angle=35)
    w.paint_faces(barrel, lambda c, n: grey_hi if n.z > 0.75 and n.y > 0.0 else grey_dark if n.z < -0.2 else None)
    w.lathe_axis("muzzle_bore", [(0.0, 0.0), (0.1, 2.6), (1.5, 2.6)], bore, (C(0.0) + 0.1, yc, zc), (1, 0, 0), 20)
    w.lathe_axis("band", [(0.0, 4.75), (0.2, 4.95), (1.8, 4.95), (2.0, 4.75)], band, (C(10.0), yc, zc), (1, 0, 0), 28)
    w.lathe_axis("band_lip", [(0.0, 4.7), (0.2, 4.85), (0.4, 4.7)], band_dark, (C(12.0) - 0.2, yc, zc), (1, 0, 0), 28)

    # The breech behind it (columns 26-30), the hub with its round knob (31-37) and the rear block (38-46).
    w.rounded_box("breech", (C(28.5), R(9.5), 6.0), (5.0, 10.0, 8.4), grey_mid, bevel=0.8)
    w.lathe_axis("hub_neck", [(0.0, 3.4), (1.0, 2.6), (3.0, 2.4), (4.4, 3.2), (5.2, 3.6)], grey, (C(31.0), R(9.0), 7.0),
                 (1, 0, 0), 24)
    knob = w.sphere("hub_knob", (C(36.5), R(8.5), 7.4), (2.6, 3.4, 3.0), grey, 24, 12)
    w.paint_faces(knob, lambda c, n: grey_hi if n.z > 0.6 and n.x < 0.0 else None)
    rear = w.block("rear", (C(42.5), R(10.5)), 4.3, 6.2, 7.0, grey_mid, rounding=1.2, power=3.5, segments=32, z0=1.4)
    w.paint_faces(rear, lambda c, n: grey if n.z > 0.6 and n.y > -0.2 else grey_dark if n.y < -0.5 else None)
    w.rounded_box("rear_vent", (C(46.0), R(13.0), 4.6), (1.2, 6.0, 3.6), grey_dark, bevel=0.4)

    # The swept fins: a small one rising over the turntable behind the barrel, a big one below it.
    upper = [(C(16.6), R(5.2)), (C(20.6), R(1.6)), (C(23.0), R(0.4)), (C(29.0), R(0.4)), (C(29.6), R(5.2))]
    fu = w.chamfered("fin_upper", w.ccw(upper), 3.0, 4.6, grey_dark, chamfer=0.5)
    w.paint_faces(fu, lambda c, n: grey_mid if n.z > 0.6 and c.y > R(2.5) else None)
    lower = [(C(12.6), R(14.0)), (C(30.0), R(14.0)), (C(29.4), R(25.6)), (C(23.6), R(26.4)), (C(21.6), R(24.6)),
             (C(18.6), R(21.6)), (C(15.4), R(18.4))]
    fl = w.chamfered("fin_lower", w.ccw(lower), 2.2, 4.4, grey_dark, chamfer=0.6)
    w.paint_faces(fl, lambda c, n: grey_mid if n.z > 0.6 and c.y > R(17.0) else None)
    w.tube("fin_edge", [(C(15.6), R(18.0), 4.2), (C(22.0), R(24.6), 4.2), (C(23.6), R(25.6), 4.1)], 0.45, grey_hi, 8)


@whole("cannon", (48, 28))
def cannon_preview():
    cannon_whole()


def cannon_piece(x0, mirror):
    cannon_whole()
    bake()
    if mirror:
        w.mirror_all()
    w.piece(w.meshes(), x0, x0 + 24, -14, 14)


@model("cannon_barrel", [14])
def cannon_barrel():
    cannon_piece(-24, False)


@model("cannon_breech", [16])
def cannon_breech():
    cannon_piece(0, False)


@model("cannon_breech_r", [167])
def cannon_breech_r():
    cannon_piece(-24, True)


@model("cannon_barrel_r", [169])
def cannon_barrel_r():
    cannon_piece(0, True)


w.run()
