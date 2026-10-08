"""Batch AB of wave 3 (sheet 4): the tusked boss of TYRIAN, TYRIAN X, HOLES and ASSASSIN, and its small copy flying
up the screen in TYRIAN, modelled as their sprites look (models.cfg: yaw=0), each built whole and cut into its
sprites' pieces, drawn at their own origins (origin) so they meet. The kit is wave3_ab_kit.py, the pixels
wave3_ab_art.py; the boss's long arms are in wave3_ab_arms.py.

- tusk_boss_10 ... tusk_boss_132, tusk_boss_core: the boss, 120 x 112 pixels, which the level events put together
  from twenty 2x2 sprites (enemies 46-65, all in the sky: rows of five 24 pixels apart, the rows 28 apart):
  10 12 14 16 18 / 48 50 [core] 54 56 / 86 88 90 92 94 / 124 126 128 130 132. The core (enemy 53, sprite 1: its
  frames 1-45 light the ball in its mouth) fills the gap; 128 is the lower jaw, boss_chin of wave 1
  (wave1_d.py), which the model meets where 90 ends. A body down the middle: a grey dome under a gold collar,
  a barrel with gold side plates, rails and a red lamp, a red band, a neck, then a black belly with four red
  fins and the mouth where the ball glows, under a gold cross bar; the jaw below. Either side a gold wing
  reaching up and out to a red tip, a grey engine block above it with a brown cable looping from its end to
  the wing's tip; below, gold struts running down to the claws: grey blocks with red panels, each with a
  brown tusk and a grey hook curving down. The plates are a relief over the sprite's outline, its height
  following a map of the parts (bevelled where they meet) with the sprite's shading embossed on it; the body,
  the tusks, hooks and cables are round. Everything is painted with the colours of the pixels under it.
- tusk_boss_small_81, _83, _85, _119, _121, _123: TYRIAN's small copy of the boss flying up the screen (enemies
  468-473, not to be shot), the sprites drawing it at half the size and turned round (its tusks up the screen):
  the boss's model scaled and turned, cut into the six pieces. The level events place the lower row 24 pixels
  under the upper one (not 28): the pieces leave out the four rows the lower row covers, so they meet.

usage: Blender -b --factory-startup -P wave3_ab_boss.py -- [--only names] [--preview <prefix>] [--check 1]
       [--whole <prefix>]
"""
import math
import os
import sys

from mathutils import Matrix

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_ab_kit as ab  # noqa: E402
from wave3_ab_kit import k, sh, n, s, y, pal  # noqa: E402

BOSS = ab.frame("BOSS", 120, (60, 56))
# For painting: the outline pixels at the edge take the colour inside them.
PAINT = ab.frame("BOSS", 120, (60, 56)).fill({0x01, 0x02})
AX = 0.5  # the boss is symmetric about x = 0.5 (pixel column 60's centre): column c mirrors 120 - c
ZC = 3.5  # the body's axis height


def at(pc, pr, z=0.0):
    """A point given in the art's pixel coordinates (column, row: pixel c covers c .. c + 1)."""
    return (pc - 60.0, 56.0 - pr, z)


def clamp01(v):
    return max(0.0, min(1.0, v))


# --- The parts' map --------------------------------------------------------------------------------------

def inside(pt, poly):
    xx, yy = pt
    res = False
    for i in range(len(poly)):
        (x0, y0), (x1, y1) = poly[i], poly[(i + 1) % len(poly)]
        if (y0 > yy) != (y1 > yy) and xx < x0 + (yy - y0) * (x1 - x0) / (y1 - y0):
            res = not res
    return res


# The left wing (pixel columns, rows): from its red tip up and out, to the body.
WING = [(4, 20.4), (32.5, 33.4), (45.5, 33.8), (45.5, 38.2), (34.2, 38.2), (34.2, 51), (31, 53.5), (6.5, 38.5)]


def zone(v, c, r):
    """Which part a pixel belongs to (the left half's map, mirrored): E engine block, W wing, T the wing's red
    tip, P the dark plating, G the gold struts, C the claw blocks, S under the body; '-' the parts modelled
    on their own (cable, tusk, hook, jaw)."""
    if v is None:
        return None
    c = min(c, 120 - c)
    gold = v >> 4 == 1 and (v & 15) >= 4
    if (8 <= r <= 10 and c <= 19) or (11 <= r <= 21 and c < min(r + 7, 21)):
        return "-"          # the cable
    if r >= 84 and c <= 45:
        return "-"          # the tusk
    if ((r >= 76 and c >= 27) or (r >= 73 and c >= 29)) and c <= 47:
        return "-"          # the hook
    if r >= 73 and c >= 47:
        return "-"          # the jaw
    if c >= 46 or (12 <= r <= 18 and c >= 44):
        return "S"
    if c <= 11 and 23 <= r <= 39:
        return "T"
    if inside((c + 0.5, r + 0.5), WING) or (c <= 20 and r <= 38):
        return "W"
    if r <= 37 and c >= 20:
        return "E"
    if 57 <= r <= 84 and (c <= 31 or (c <= 37 and not gold)):
        return "C"
    if gold and r >= 42:
        return "G"
    return "P"


def zone_height(z, c, r):
    c = min(c, 120 - c)
    if z == "E":
        return 10.2 - 1.2 * clamp01((r - 24) / 12.0)
    if z == "W":
        return 5.6 + 2.8 * clamp01((c - 6) / 34.0)
    if z == "T":
        return 6.8
    if z == "P":
        return 4.8
    if z == "G":
        return 7.4 + 1.6 * clamp01((70 - r) / 26.0)
    if z == "C":
        return 8.4
    return 3.4


# --- Materials ----------------------------------------------------------------------------------------------

def painter():
    return s.Painter("tboss", shades={0: (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14),
                                      1: (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14),
                                      4: (2, 3, 4, 5, 6, 7, 8, 9, 11, 13),
                                      10: (3, 4, 5, 6, 7, 8, 10)},
                     metallic=0.5, roughness=0.38,
                     finish={0: (0.45, 0.42), 1: (0.35, 0.4), 4: (0.25, 0.45), 10: (0.1, 0.55)})


def paint(obj, p, wall_steps=2, wall_z=0.45):
    return ab.paint(obj, PAINT, p, wall_steps=wall_steps, under=p(0x02), wall_z=wall_z)


# --- The body -----------------------------------------------------------------------------------------------

# Its sections down the screen: (row, half-width, height above the axis).
BODY = [(5.6, 1.6, 3.0), (6.2, 5.4, 6.4), (7.2, 7.5, 8.4), (8.6, 9.2, 10.0), (10.2, 10.5, 11.0), (12.0, 11.0, 11.6),
        (14.0, 12.2, 12.0), (17.0, 13.6, 12.2), (19.0, 14.1, 12.3), (27.0, 14.2, 12.4), (34.0, 13.9, 12.1),
        (36.4, 12.4, 11.4), (37.8, 8.4, 9.4), (40.4, 6.6, 8.4), (42.8, 8.6, 9.4), (44.4, 11.0, 10.8),
        (47.0, 11.8, 11.6), (52.0, 11.8, 12.2), (58.0, 11.7, 12.2), (64.0, 11.5, 11.6), (68.0, 10.6, 10.6),
        (70.5, 9.4, 9.2), (72.2, 8.0, 7.6), (73.2, 5.0, 5.0), (73.8, 1.5, 2.5)]
COLLAR = [(12.3, 10.6, 11.9), (13.2, 11.8, 13.2), (14.6, 13.8, 13.7), (16.2, 15.3, 13.6), (17.6, 15.7, 13.1),
          (18.7, 14.8, 12.4)]
CROSSBAR = [(43.5, 12.0, 10.6), (44.2, 13.6, 11.8), (46.7, 13.5, 12.4), (47.5, 12.2, 12.0)]


def body_loft(name, rows, mat, power=2.4, extra=0.0):
    secs = []
    for r, hw, top in reversed(rows):  # increasing y
        hw += extra
        top += extra
        secs.append((56.0 - r, AX, ZC, hw, top, 0.42 * hw + 1.0))
    return y.loft_y(name, y.smooth_sections(secs, 0.5), mat, segments=40, power=power)


def jaw_top(mat):
    """The upper part of the lower jaw, under the belly: its section where sprite 90 ends (y = -28) is boss_chin's
    (wave1_d.py) where it begins: 10.5 either side of x = 0.5, 6.2 high and 2.48 deep, a superellipse of power
    2.6, so the two meet."""
    keys = [(-29.6, 10.5, 6.05, 2.42), (-28.0, 10.5, 6.2, 2.48), (-26.0, 11.3, 6.5, 2.6), (-23.0, 11.5, 6.8, 2.7),
            (-21.2, 11.2, 6.8, 2.7), (-20.0, 9.0, 6.4, 2.5), (-19.0, 7.0, 5.8, 2.2), (-17.8, 6.2, 4.8, 1.9),
            (-17.1, 3.0, 3.0, 1.2)]
    secs = [(yy, AX, 0.0, hw, top, bottom) for yy, hw, top, bottom in keys]
    return y.loft_y("jaw", y.smooth_sections(secs, 0.4), mat, segments=48, power=2.6)


def mirrored(objs):
    return objs + s.mirror_copies(objs, AX)


def build_boss():
    p = painter()
    grey = p(0x06)
    dark = p(0x03)
    gold = p(0x18)
    brown = p(0xa7)
    ball = pal("tboss_ball", 0x78, metallic=0.0, roughness=0.2, glow=1.4)
    ball_core = pal("tboss_ball_core", 0x7b, metallic=0.0, roughness=0.15, glow=2.4)
    lamp = pal("tboss_lamp", 0x49, metallic=0.1, roughness=0.2, glow=1.2)

    # --- The plates: one relief over everything but the round parts. -------------------------------------
    def zone_or_none(v, c, r):
        z = zone(v, c, r)
        return None if z in (None, "-") else zone_height(z, c, r)
    height = ab.field(BOSS, zone_or_none, blur=2)
    plates = ab.relief("plates", BOSS, lambda v, c, r: zone(v, c, r) not in (None, "-"), height, grey, edge=1.3,
                       bevel=1.1, emboss=1.8, spacing=0.55, smooth=1, epsilon=0.3, sigma=0.9)
    ab.simplify_bottom(plates)
    ab.sharpen_walls(plates)

    # --- The body down the middle. ---------------------------------------------------------------------------
    body = body_loft("body", BODY, grey)
    collar = body_loft("collar", COLLAR, gold, power=2.6)
    crossbar = body_loft("crossbar", CROSSBAR, gold, power=2.6)
    jaw = jaw_top(brown)
    round_parts = [body, collar, crossbar]

    def top(xx, yy):
        return ab.surface(round_parts, xx, yy, ZC)

    # Rails down the barrel's sides (the light columns of the sprite).
    rails = []
    for pc in (51.5,):
        xx = pc - 60.0
        path = [(xx, yy, top(xx, yy) - 0.35) for yy in (56 - 22.5, 56 - 26.0, 56 - 30.0, 56 - 34.0, 56 - 36.6)]
        rails.append(ab.tube("rail", path, 1.05, grey, 12, squash=0.8))
    rails = mirrored(rails)

    # The belly's four red fins: the sprite's red there, raised on the belly.
    fin_polys = ab.polys_of(BOSS, lambda v, c, r: 53 <= r <= 67 and 49 <= c <= 71 and v >> 4 == 4, smooth=1,
                            epsilon=0.3, min_area=2.0)
    fins = sh.inflate("fins", fin_polys, p(0x47), sh.pillow_profile(0.9, 0.5), bottom=0.0, base=0.0, rim=0.1,
                      spacing=0.35, z_fn=lambda xx, yy, z: top(xx, yy) - 0.45 + z)
    k.smooth(fins, 40)

    # The claws' red panels, raised a little in their frames.
    panel_polys = ab.polys_of(BOSS, lambda v, c, r: 57 <= r <= 80 and min(c, 120 - c) <= 27 and v >> 4 == 4, smooth=1,
                              epsilon=0.3, min_area=3.0)
    panels = sh.inflate("panels", panel_polys, p(0x46), sh.pillow_profile(0.7, 0.45), bottom=0.0, base=0.0, rim=0.05,
                        spacing=0.35, z_fn=lambda xx, yy, z: ab.surface([plates], xx, yy, 8.0) - 0.3 + z)
    k.smooth(panels, 40)

    # The mouth: a dark socket and the glowing ball (the core's frames light it; it glows throughout).
    bx, by = at(60.5, 50.6)[:2]
    bz = top(bx, by + 3.5)
    ab.q.torus("socket", (bx, by, bz - 1.0), 3.5, 0.9, dark, 32, 10, squash=0.8, scale_y=0.95)
    ab.sphere("ball", (bx, by, bz - 1.6), (3.0, 2.8, 2.5), ball, 24, 12)
    ab.sphere("ball_core", (bx - 0.6, by + 0.5, bz + 0.6), (1.5, 1.3, 0.6), ball_core, 12, 6)
    # The red lamp on the barrel.
    lx, ly = at(61.0, 21.6)[:2]
    ab.sphere("lamp", (lx, ly, top(lx, ly) - 0.2), (1.5, 1.7, 0.9), lamp, 14, 8)

    # --- The round limbs: cable, tusk and hook, built on the left and mirrored. -------------------------------
    cable_pts = [(21.0, 9.0, 7.2), (18.0, 9.0, 6.4), (15.0, 9.4, 6.0), (13.0, 10.4, 5.8), (11.4, 11.9, 5.7),
                 (10.0, 13.5, 5.6), (8.8, 15.2, 5.6), (7.8, 17.0, 5.6), (6.9, 18.8, 5.6), (6.2, 20.6, 5.6),
                 (6.0, 22.5, 5.6), (6.2, 24.5, 5.6)]
    cable = ab.tube("cable", [at(c, r, z) for c, r, z in cable_pts], 1.4, gold, 12)
    tusk_pts = [(20.0, 78.0, 6.4, 3.7), (20.0, 84.0, 5.9, 3.7), (20.0, 90.0, 5.4, 3.6), (20.4, 93.0, 5.1, 3.5),
                (21.4, 95.0, 4.9, 3.4), (22.6, 96.8, 4.7, 3.2), (24.0, 98.6, 4.4, 3.0), (25.6, 100.3, 4.1, 2.8),
                (27.3, 101.9, 3.8, 2.6), (29.2, 103.3, 3.4, 2.3), (31.4, 104.5, 3.0, 1.9), (34.0, 105.4, 2.6, 1.3),
                (37.6, 106.0, 2.2, 0.3)]
    tusk = ab.loft_path("tusk", [at(c, r, z) for c, r, z, _ in tusk_pts],
                        [(hw, 0.85 * hw) for *_, hw in tusk_pts], brown, segments=16)
    hook_pts = [(28.0, 73.5, 6.9, 2.1), (28.4, 76.0, 6.4, 2.1), (28.9, 78.3, 5.9, 2.1), (29.5, 80.2, 5.5, 2.1),
                (30.6, 82.0, 5.1, 2.1), (32.0, 83.6, 4.7, 2.1), (33.7, 85.0, 4.3, 2.0), (35.7, 86.3, 3.9, 1.9),
                (38.0, 87.4, 3.5, 1.7), (40.8, 88.2, 3.1, 1.3), (44.6, 88.7, 2.8, 0.3)]
    hook = ab.loft_path("hook", [at(c, r, z) for c, r, z, _ in hook_pts],
                        [(hw, 0.9 * hw) for *_, hw in hook_pts], grey, segments=14)
    limbs = mirrored([cable, tusk, hook])

    # --- Paint: the sprite's colours on everything but the lights. --------------------------------------------
    for obj in [plates, body, collar, crossbar, jaw, fins, panels] + rails + limbs:
        if obj is plates:
            paint(obj, p, wall_steps=2, wall_z=0.8)
        else:
            paint(obj, p, wall_steps=1 if obj in (body, collar, crossbar, jaw) else 2)
    for obj in (plates,):
        s.merge_flat(obj, 1.0)
    n.merge_by_material()


# --- The pieces -------------------------------------------------------------------------------------------------

BOSS_PIECES = [(10, 0, 0), (12, 24, 0), (14, 48, 0), (16, 72, 0), (18, 96, 0),
               (48, 0, 28), (50, 24, 28), ("core", 48, 28), (54, 72, 28), (56, 96, 28),
               (86, 0, 56), (88, 24, 56), (90, 48, 56), (92, 72, 56), (94, 96, 56),
               (124, 0, 84), (126, 24, 84), (130, 72, 84), (132, 96, 84)]  # 128: boss_chin (wave1_d.py)


def boss_piece(sprite, pc, pr):
    x0, y1 = pc - 60.0, 56.0 - pr
    return (f"tusk_boss_{sprite}", (x0, x0 + 24.0, y1 - 28.0, y1), (x0 + 12.0, y1 - 14.0),
            lambda: ab.frame_mask(BOSS, (pc, pc + 24, pr, pr + 28)))


ab.pieced("tusk_boss", build_boss, (120, 112), [boss_piece(*pc) for pc in BOSS_PIECES])


# --- The small copy flying up the screen ---------------------------------------------------------------------

BEETLE = ab.frame("BEETLE", 72, (36, 26))


def build_small():
    """The boss at half the size, turned round: in the coordinates of the sprites' art as the sheet draws it
    (72 x 56, origin (36, 28)); the boss's axis (x = 0.5) goes to x = -5."""
    build_boss()
    m = Matrix.Translation((-4.75, 0.5, 0.0)) @ Matrix.Rotation(math.pi, 4, "Z") @ Matrix.Scale(0.5, 4)
    ab.transformed_copies(ab.meshes(), m, "_small")


def small_piece(sprite, col, upper):
    cx = col * 24.0 - 24.0
    # The upper row keeps its first 26 rows, the lower row its last 26 (the game draws the rows 24 apart).
    box = (cx - 12.0, cx + 12.0, 2.0, 28.0) if upper else (cx - 12.0, cx + 12.0, -28.0, -2.0)
    centre = (cx, 14.0) if upper else (cx, -14.0)
    return (f"tusk_boss_small_{sprite}", box, centre,
            lambda: ab.frame_mask(BEETLE, (col * 24, col * 24 + 24) + ((0, 28) if upper else (24, 52))))


ab.pieced("tusk_boss_small", build_small, (72, 56),
          [small_piece(81, 0, True), small_piece(83, 1, True), small_piece(85, 2, True),
           small_piece(119, 0, False), small_piece(121, 1, False), small_piece(123, 2, False)])


ab.run()
