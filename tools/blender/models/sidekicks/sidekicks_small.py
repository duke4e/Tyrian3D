"""The small sidekicks: 1x1 sprites of the ships sheet (12 x 14 pixels), seen beside the player's ship.

- sk_single (sprite 168): Single Shot Option, a grey gun pod with a muzzle at its nose and a row of
  white lamps along its spine
- sk_dual (169): Dual Shot Option, two such pods side by side on a common base
- sk_charge (258): Charge Cannon, a steel-blue spool with two flanges round a glowing core
- sk_vulcan (167): Vulcan Shot Option, three barrels in a clamp over a bronze drum between grey cheeks
- sk_wobbley (246): Wobbley, a glossy blue blob of energy with a curling tail
- sk_canister (165): Atom Bombs, Buster Rocket, MicroBomb, 8-Way MicroBomb and Post-It Mine, a bronze
  bomb (a bottle with a round belly) in a bronze hoop
- sk_phoenix (171): Phoenix Device, a fireball
- sk_plasma (224): Plasma Storm, a green plasma bell on a grey saucer
- sk_minimissile (163): Mini-Missile, a grey cup on a round foot holding a glowing warhead, a red core
  in its stem
- sk_zica_super (3): Zica SuperCharger, a steel-blue cage round a glowing egg, a neck on top, claws below
- sk_zica_flame (87): Zica Flamethrower, a ribbed barrel between two curved blades
- sk_sideship (245): Side Ship, a little blue fighter with a cyan canopy and a glowing exhaust
- sk_mint (112), sk_cherry (113): Mint-O-Ship and Tropical Cherry Companion, swirled candy gems
- sk_marlo (152): Satellite Marlo, a small red orb with a glowing window
- sk_bubblegum (95): Bubble Gum-Gun, a dark glass globe of gum balls in a steel-blue rim, a nozzle on top
- sk_punch (2): Flying Punch, a red fist, knuckles up the screen

Pixel (column c, row r) of a sprite covers x = c - 6 .. c - 5, y = 6 - r .. 7 - r (sx, sy: its centre).
Run: Blender -b --factory-startup -P sidekicks_small.py -- [--only ...] [--preview <dir>] [--check <sheets dir>]
"""
import math
import os
import sys

from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sidekick_kit as s  # noqa: E402
from sidekick_kit import k, model  # noqa: E402


# --- Single and dual shot -------------------------------------------------------------------------

POD_SHAPE = [  # (fraction of the length from the back, half-width / 5, top / height, bottom / 1.8)
    (0.0, 0.45, 0.45, 0.5), (0.04, 0.64, 0.66, 0.72), (0.1, 0.84, 0.86, 0.9), (0.17, 0.97, 0.97, 1.0),
    (0.25, 1.0, 1.0, 1.0), (0.5, 1.0, 1.0, 1.0), (0.57, 0.93, 0.96, 0.95), (0.63, 0.8, 0.9, 0.88),
    (0.69, 0.66, 0.84, 0.8), (0.79, 0.6, 0.78, 0.74), (0.86, 0.48, 0.62, 0.6)]


def gun_pod(prefix, x, y_bottom, y_top, half, height, hull, dark, trim, lamp, muzzle):
    """A grey gun pod from y_bottom to its muzzle at y_top, `half` wide at its widest (half-width):
    a round body, a narrower head (a dark seam between them) and a short barrel, white lamps along
    the spine, curved plates on its flanks."""
    length = y_top - y_bottom
    f = half / 5.0

    def section(t):
        for (t0, w0, a0, b0), (t1, w1, a1, b1) in zip(POD_SHAPE, POD_SHAPE[1:]):
            if t0 <= t <= t1:
                u = (t - t0) / (t1 - t0)
                return w0 + (w1 - w0) * u, a0 + (a1 - a0) * u, b0 + (b1 - b0) * u
        return POD_SHAPE[-1][1:]

    samples = k.profile([(y_bottom + length * t, w, tp, b) for t, w, tp, b in POD_SHAPE], step=0.4)
    segments = 22 if f >= 0.8 else 16
    rings = [k.ring(y, 5.0 * f * w, 1.0, segments, x=x, top=height * tp, bottom=1.8 * b, power=2.4)
             for y, w, tp, b in samples]
    body = k.loft(prefix + "hull", rings, hull, start_point=(x, y_bottom - 0.1, 0.2),
                  end_point=(x, samples[-1][0] + 0.2, height * 0.3))
    k.smooth(body, 50)
    # The seam between head and body.
    t = 0.635
    w, tp, b = section(t)
    seam = k.ring(y_bottom + length * t, 5.0 * f * w + 0.05, 1.0, segments, x=x, top=height * tp + 0.05,
                  bottom=1.8 * b, power=2.4)
    s.tube(prefix + "seam", seam, 0.2, dark, 6, closed=True)
    # The barrel to the muzzle, a ring round its end, a dark bore that glows inside.
    y0 = y_bottom + length * 0.8
    z = height * 0.38
    r = 1.6 * min(1.0, f * 1.5)
    reach = y_top - y0
    s.lathe_axis(prefix + "barrel", [(0, r * 0.95), (reach - 0.7, r * 0.9), (reach - 0.6, r * 1.12), (reach - 0.05, r * 1.1),
                                     (reach, r * 0.8)], trim, (x, y0, z), (0, 1, 0), segments=18)
    s.lathe_axis(prefix + "bore", [(0, r * 0.6), (0.3, r * 0.6)], dark, (x, y_top - 0.29, z), (0, 1, 0), segments=14)
    s.sphere(prefix + "flash", (x, y_top - 0.1, z), (r * 0.45, 0.16, r * 0.45), muzzle, 12, 6)
    # Lamps along the spine (the sprite's white highlights).
    for t, size in ((0.74, 0.72), (0.49, 1.0), (0.27, 0.82)):
        w, tp, b = section(t)
        s.sphere(prefix + "lamp", (x, y_bottom + length * t, height * tp - 0.1),
                 (1.15 * size * min(1.0, f * 1.4), 0.62 * size, 0.42), lamp, 12, 6)
    # Curved plates on the flanks.
    for side in (-1, 1):
        if f < 0.8:
            pts = [(x + side * 2.3 * f / 0.6, y_bottom + length * 0.55, height * 0.55),
                   (x + side * 2.7 * f / 0.6, y_bottom + length * 0.35, height * 0.5),
                   (x + side * 2.2 * f / 0.6, y_bottom + length * 0.14, height * 0.42)]
            s.tube(prefix + "plate", s.catmull(pts, 0.3), 0.32, trim, 8, squash=0.7)
            continue
        pts = [(x + side * 3.6 * f, y_bottom + length * 0.6, height * 0.66),
               (x + side * 4.6 * f, y_bottom + length * 0.42, height * 0.6),
               (x + side * 4.3 * f, y_bottom + length * 0.2, height * 0.52),
               (x + side * 2.8 * f, y_bottom + length * 0.05, height * 0.4)]
        s.tube(prefix + "plate", s.catmull(pts, 0.3), 0.55, trim, 10, squash=0.7)


def pod_materials():
    hull = s.pal("pod_hull", 0x07, metallic=0.45, roughness=0.28)
    dark = s.pal("pod_dark", 0x02, metallic=0.3, roughness=0.5)
    trim = s.pal("pod_trim", 0x0b, metallic=0.5, roughness=0.2)
    lamp = s.light("pod_lamp", (225, 240, 255), 1.8)
    muzzle = s.light("pod_muzzle", (255, 120, 30), 3.0)
    return hull, dark, trim, lamp, muzzle


@model("sk_single", "ships", 168)
def single():
    """Rows 0-11, columns 1-10: a round body (rows 4-11), the head and barrel (rows 0-3)."""
    hull, dark, trim, lamp, muzzle = pod_materials()
    gun_pod("", 0.0, -5.0, 7.0, 5.0, 3.4, hull, dark, trim, lamp, muzzle)


@model("sk_dual", "ships", 169)
def dual():
    """Two narrower pods (columns 0-5 and 6-11, rows 1-12) joined at the back."""
    hull, dark, trim, lamp, muzzle = pod_materials()
    for x in (-3.0, 3.0):
        gun_pod("l_" if x < 0 else "r_", x, -5.6, 6.0, 3.0, 3.0, hull, dark, trim, lamp, muzzle)
    s.rbox("base", (0, -3.4, 0.5), (9.0, 4.2, 2.4), hull, bevel=0.8, segments=3)
    s.rbox("base_rail", (0, -5.3, 1.0), (6.4, 1.0, 1.6), dark, bevel=0.4)


# --- Charge cannon --------------------------------------------------------------------------------

@model("sk_charge", "ships", 258)
def charge():
    """A spool along Y (rows 0-13): the cap (rows 0-3), a flange (row 4), the glowing core (rows 5-8),
    the lower body (row 9), a flange (row 10) and the foot (rows 11-13)."""
    steel = s.pal("charge_steel", 0x3b, metallic=0.45, roughness=0.25)
    light_steel = s.pal("charge_light", 0x3d, metallic=0.5, roughness=0.2)
    dark = s.pal("charge_dark", 0x33, metallic=0.4, roughness=0.4)
    core = s.pal("charge_core", 0x73, metallic=0.1, roughness=0.1, glow=(230, 55, 15), strength=0.35)
    hot = s.light("charge_hot", (255, 210, 110), 2.4)
    sq = 0.72
    s.lathe_y("cap", [(3.4, 2.4), (3.9, 3.3), (4.6, 3.6), (5.6, 3.6), (6.3, 3.3), (6.8, 2.6), (7.0, 1.4), (7.05, 0.0)],
              steel, squash=sq, segments=32)
    s.lathe_y("cap_ring", [(5.0, 3.55), (5.1, 3.75), (5.5, 3.75), (5.6, 3.55)], dark, squash=sq, segments=32)
    s.lathe_y("flange_top", [(2.0, 3.0), (2.1, 4.6), (2.4, 4.95), (2.8, 4.95), (3.1, 4.6), (3.3, 3.2)], light_steel,
              squash=sq, segments=32)
    s.lathe_y("core", [(-2.4, 2.6), (-2.0, 3.25), (-1.0, 3.45), (1.0, 3.45), (2.0, 3.25), (2.4, 2.6)], core,
              squash=sq, segments=32)
    s.sphere("core_hot", (-1.2, 0.4, 3.45 * sq - 0.3), (1.1, 1.2, 0.45), hot, 16, 8)
    for y in (-2.1, 2.1):  # dark collars at the core's ends
        s.lathe_y("collar", [(y - 0.3, 3.2), (y - 0.2, 3.6), (y + 0.2, 3.6), (y + 0.3, 3.2)], dark, squash=sq, segments=32)
    s.lathe_y("lower", [(-3.0, 3.0), (-2.8, 3.8), (-2.4, 3.8), (-2.2, 3.0)], steel, squash=sq, segments=32)
    s.lathe_y("flange_bottom", [(-4.2, 3.2), (-4.05, 4.6), (-3.8, 4.95), (-3.3, 4.95), (-3.05, 4.6), (-2.9, 3.0)],
              light_steel, squash=sq, segments=32)
    s.lathe_y("foot", [(-7.05, 0.0), (-7.0, 1.6), (-6.6, 2.7), (-5.6, 3.3), (-4.7, 3.6), (-4.1, 3.3)], steel,
              squash=sq, segments=32)
    s.lathe_y("foot_ring", [(-6.0, 3.1), (-5.9, 3.35), (-5.5, 3.45), (-5.4, 3.2)], dark, squash=sq, segments=32)
    # Fins on the flanges, as the sprite's notches.
    for y in (2.55, -3.6):
        for side in (-1, 1):
            fin = [(side * 4.6, y - 0.55), (side * 5.6, y - 0.25), (side * 5.6, y + 0.25), (side * 4.6, y + 0.55)]
            s.slab("fin", fin, -0.5, 0.5, dark, bevel=0.15)


# --- Vulcan ---------------------------------------------------------------------------------------

@model("sk_vulcan", "ships", 167)
def vulcan():
    """Three barrels (columns 3, 5-6 and 8, rows 2-5) in a clamp (row 3), a bronze drum (columns 4-7,
    rows 7-12) between grey cheeks (columns 2-3 and 8-9, rows 6-12)."""
    grey = s.pal("vulcan_grey", 0x09, metallic=0.45, roughness=0.25)
    light_grey = s.pal("vulcan_light", 0x0c, metallic=0.5, roughness=0.18)
    dark = s.pal("vulcan_dark", 0x02, metallic=0.3, roughness=0.5)
    bronze = s.pal("vulcan_bronze", 0x18, metallic=0.5, roughness=0.25)
    bronze_dark = s.pal("vulcan_bronze_dark", 0x13, metallic=0.45, roughness=0.35)
    muzzle = s.light("vulcan_muzzle", (255, 130, 30), 3.0)
    zc = 1.7
    s.lathe_y("drum", [(-6.0, 0.0), (-5.9, 1.6), (-5.6, 2.1), (-1.0, 2.2), (0.4, 2.1), (0.9, 1.5), (1.0, 0.0)],
              bronze, z=zc, segments=28)
    for y in (-4.4, -2.6, -0.8):
        s.lathe_y("drum_band", [(y - 0.2, 2.15), (y - 0.1, 2.32), (y + 0.1, 2.32), (y + 0.2, 2.15)], bronze_dark,
                  z=zc, segments=28)
    for side in (-1, 1):
        cheek = s.smooth_outline([(side * 2.0, 1.2), (side * 3.4, 1.0), (side * 4.05, -0.5), (side * 4.05, -4.6),
                                  (side * 3.4, -6.0), (side * 2.0, -5.9), (side * 1.8, -2.5)], 0.5)
        s.puff("cheek", cheek, -0.6, 3.3, grey, side=0.45, power=2.6)
        s.tube("cheek_edge", s.catmull([(side * 3.5, 0.6, 2.5), (side * 3.75, -2.5, 2.75), (side * 3.4, -5.3, 2.3)], 0.3),
               0.32, light_grey, 8)
    # The clamp holding the barrels, and the barrels' housing behind it.
    s.rbox("housing", (0, 0.6, 1.9), (5.6, 1.6, 2.2), grey, bevel=0.5)
    s.rbox("clamp", (0, 3.5, 2.2), (6.6, 1.0, 1.6), light_grey, bevel=0.35)
    for x, r in ((-2.5, 0.55), (0.0, 0.8), (2.5, 0.55)):
        z = 2.3 if x == 0 else 2.15
        s.lathe_axis("barrel", [(0, r), (4.0, r), (4.1, r * 1.15), (4.5, r * 1.15), (4.55, r * 0.8)], light_grey,
                     (x, 0.6, z), (0, 1, 0), segments=14)
        s.lathe_axis("bore", [(0, r * 0.55), (0.2, r * 0.55)], dark, (x, 4.95, z), (0, 1, 0), segments=10)
        s.sphere("flash", (x, 5.1, z), (r * 0.45, 0.12, r * 0.45), muzzle, 10, 6)


# --- Wobbley --------------------------------------------------------------------------------------

@model("sk_wobbley", "ships", 246)
def wobbley():
    """A blue blob (rows 4-9, columns 1-8, its head lower left) with a tail curling up on the right
    (columns 9-11, rows 5-7) and fins below."""
    blue = s.pal("wobbley", 0x9b, metallic=0.15, roughness=0.12, glow=(40, 90, 255), strength=0.35)
    pale = s.light("wobbley_shine", (170, 215, 255), 1.6, color=(200, 230, 255))
    deep = s.pal("wobbley_deep", 0x97, metallic=0.15, roughness=0.15, glow=(20, 40, 230), strength=0.35)
    body = s.sphere("body", (0, 0, 0), (4.1, 2.5, 2.1), blue, 32, 16)
    body.data.transform(Matrix.Translation((-0.6, 0.1, 1.2)) @ Matrix.Rotation(math.radians(-18), 4, "Z"))
    tail = s.catmull([(2.4, 0.2, 1.3), (4.2, 0.0, 1.2), (5.4, 0.9, 1.1), (5.2, 2.0, 1.0), (4.4, 2.3, 0.9)], 0.3)
    s.tube("tail", tail, [1.25, 0.95, 0.75, 0.55, 0.4], blue, 14, squash=0.65)
    s.tube("fin_back", s.catmull([(-3.6, -1.4, 0.8), (-4.4, -2.2, 0.6), (-4.6, -2.8, 0.5)], 0.25), [0.75, 0.55, 0.3],
           deep, 10, squash=0.6)
    s.tube("fin_low", s.catmull([(0.2, -1.5, 0.9), (0.6, -2.4, 0.6), (0.9, -2.8, 0.5)], 0.25), [0.8, 0.6, 0.35],
           deep, 10, squash=0.6)
    s.tube("crest", s.catmull([(-2.0, 1.6, 2.0), (-0.4, 2.6, 1.6), (1.0, 2.2, 1.5)], 0.25), [0.55, 0.6, 0.35], deep, 10,
           squash=0.6)
    # The sprite's white streaks.
    for pts in (((-2.6, -0.6, 3.0), (-1.0, 0.4, 3.25), (0.8, 0.9, 3.0)),
                ((-0.4, -1.4, 2.8), (1.3, -0.5, 2.85), (2.6, 0.0, 2.3))):
        s.tube("shine", s.catmull(pts, 0.25), 0.3, pale, 8, squash=0.5)
    s.sphere("eye", (-3.2, -0.9, 2.15), (0.45, 0.45, 0.3), pale, 10, 6)


# --- Bombs ----------------------------------------------------------------------------------------

@model("sk_canister", "ships", 165)
def canister():
    """A bronze bomb: the neck (columns 3-8, rows 0-3) and a round belly (rows 8-12) in a hoop
    (columns 0-11, rows 4-13), dark gaps between them."""
    bronze = s.pal("bomb_bronze", 0x19, metallic=0.5, roughness=0.22)
    pale = s.pal("bomb_pale", 0x1b, metallic=0.5, roughness=0.18)
    dark = s.pal("bomb_dark", 0x12, metallic=0.4, roughness=0.4)
    muzzle = s.light("bomb_fuse", (255, 150, 40), 2.5)
    zc = 2.0
    s.hoop("hoop", (0, -2.1, 1.5), 4.55, 3.9, 1.4, bronze, 48, 12, squash=1.0)
    s.hoop("hoop_groove", (0, -2.1, 1.5 + 1.38), 4.55, 3.9, 0.25, dark, 48, 6)
    s.lathe_y("bomb", [(-6.5, 0.0), (-6.4, 2.0), (-5.9, 3.2), (-4.8, 3.8), (-3.6, 3.85), (-2.4, 3.4), (-1.4, 2.5),
                       (-0.6, 2.0), (0.4, 2.05), (1.8, 2.35), (3.2, 2.4), (4.2, 2.25), (5.4, 2.3), (6.2, 2.45),
                       (6.7, 2.25), (6.9, 1.4), (6.95, 0.0)], pale, z=zc, squash=0.9, segments=28)
    s.lathe_y("waist", [(-1.1, 2.2), (-0.9, 2.45), (-0.1, 2.45), (0.1, 2.2)], dark, z=zc, squash=0.9, segments=24)
    s.lathe_y("neck_band", [(3.9, 2.2), (4.05, 2.55), (4.6, 2.55), (4.75, 2.2)], bronze, z=zc, squash=0.9, segments=24)
    s.lathe_y("lip", [(6.0, 2.3), (6.1, 2.6), (6.7, 2.55), (6.85, 2.2)], dark, z=zc, squash=0.9, segments=24)
    s.sphere("fuse", (0, 6.95, zc), (1.2, 0.15, 1.2), muzzle, 12, 6)
    # Struts tying the bomb to the hoop.
    for side in (-1, 1):
        s.lathe_axis("strut", [(0, 0.6), (1.6, 0.5)], dark, (side * 2.0, 0.4, zc - 0.3), (side, 0.15, -0.1), segments=10)


# --- Phoenix device -------------------------------------------------------------------------------

@model("sk_phoenix", "ships", 171)
def phoenix():
    """A fireball (rows 1-11, columns 1-11): a bright core upper left, a hot rim lower right."""
    rim = s.pal("phoenix_rim", 0x73, metallic=0.0, roughness=0.35, glow=(170, 20, 0), strength=0.5)
    fire = s.pal("phoenix_fire", 0x7a, metallic=0.0, roughness=0.3, glow=(255, 120, 15), strength=0.55)
    hot = s.pal("phoenix_hot", 0x7c, metallic=0.0, roughness=0.3, glow=(255, 200, 60), strength=0.8)
    core = s.light("phoenix_core", (255, 245, 190), 2.4, color=(255, 250, 225))
    s.sphere("rim", (0.5, 0.5, 2.0), (5.5, 5.5, 2.6), rim, 32, 14)
    s.sphere("fire", (0.3, 0.7, 2.6), (4.7, 4.7, 4.0), fire, 32, 16)
    s.sphere("hot", (-0.4, 1.4, 3.5), (3.5, 3.5, 3.4), hot, 28, 14)
    s.sphere("core", (-0.8, 1.8, 5.1), (2.2, 2.2, 1.9), core, 24, 12)
    crescent = s.sphere("crescent", (0, 0, 0), (3.0, 1.1, 1.3), hot, 20, 10)
    crescent.data.transform(Matrix.Translation((3.2, -3.0, 2.4)) @ Matrix.Rotation(math.radians(45), 4, "Z"))
    # Flares licking off the ball.
    for a, length in ((35, 1.8), (150, 1.4), (250, 1.6), (310, 1.8)):
        r = math.radians(a)
        p0 = Vector((0.5 + 4.6 * math.cos(r), 0.5 + 4.6 * math.sin(r), 2.6))
        p1 = p0 + Vector((math.cos(r + 0.6), math.sin(r + 0.6), -0.2)) * length
        s.tube("flare", [p0, (p0 + p1) / 2, p1], [0.9, 0.6, 0.15], fire, 8, squash=0.6)


# --- Plasma storm ---------------------------------------------------------------------------------

@model("sk_plasma", "ships", 224)
def plasma():
    """A green plasma bell (columns 2-8, rows 1-7) on a grey saucer (columns 0-10, rows 8-12), a grey
    clasp up its front (rows 5-7)."""
    green = s.pal("plasma_green", 0xc4, metallic=0.1, roughness=0.06, glow=(20, 230, 70), strength=0.18)
    bright = s.light("plasma_bright", (150, 255, 170), 2.0)
    grey = s.pal("plasma_grey", 0x0a, metallic=0.45, roughness=0.22)
    pale = s.pal("plasma_pale", 0x0d, metallic=0.5, roughness=0.15)
    dark = s.pal("plasma_dark", 0x04, metallic=0.4, roughness=0.4)
    cx = -0.5
    saucer = s.lathe_y("saucer", [(-6.0, 0.0), (-5.9, 2.0), (-5.4, 3.0), (-4.2, 3.45), (-3.0, 3.35), (-2.0, 2.7),
                                  (-1.3, 1.6), (-1.1, 0.0)], grey, x=cx, z=1.2, squash=0.6, segments=32)
    saucer.data.transform(Matrix.Translation((cx, 0, 0)) @ Matrix.Diagonal((1.62, 1.0, 1.0, 1.0)) @
                          Matrix.Translation((-cx, 0, 0)))
    s.hoop("rim", (cx, -3.5, 1.2), 5.2, 2.0, 0.42, pale, 48, 8)
    s.lathe_y("bell", [(-2.6, 0.0), (-2.5, 2.4), (-1.6, 3.25), (0.5, 3.45), (3.0, 3.2), (4.6, 2.6), (5.6, 1.7),
                       (6.1, 0.8), (6.25, 0.0)], green, x=cx, z=1.7, squash=0.92, segments=32)
    s.sphere("bell_glow", (cx - 0.2, 4.4, 3.95), (1.1, 0.9, 0.45), bright, 14, 8)
    s.lathe_y("bell_ring", [(-1.0, 3.3), (-0.9, 3.55), (-0.5, 3.6), (-0.4, 3.35)], dark, x=cx, z=1.7, squash=0.92,
              segments=32)
    # The clasp: a grey strap from the saucer up the bell's front, a stud on it.
    strap = s.catmull([(cx, -2.6, 3.0), (cx, -1.0, 4.4), (cx, 0.8, 4.9), (cx, 2.0, 4.85)], 0.3)
    s.tube("clasp", strap, [0.95, 1.0, 0.85, 0.6], pale, 12, squash=0.5)
    s.sphere("stud", (cx, -0.4, 4.85), (0.9, 0.9, 0.5), grey, 14, 8)
    s.rbox("slot", (cx, -4.6, 2.2), (4.0, 0.6, 0.6), dark, bevel=0.25)


# --- Mini-missile ---------------------------------------------------------------------------------

@model("sk_minimissile", "ships", 163)
def minimissile():
    """A glowing warhead (columns 4-7, rows 1-4) in a grey cup (columns 2-9, rows 4-7), a red core
    in the stem (rows 6-9), a round foot (rows 10-13)."""
    grey = s.pal("mm_grey", 0x0a, metallic=0.45, roughness=0.22)
    pale = s.pal("mm_pale", 0x0d, metallic=0.5, roughness=0.15)
    dark = s.pal("mm_dark", 0x03, metallic=0.4, roughness=0.4)
    warhead = s.pal("mm_warhead", 0x7c, metallic=0.1, roughness=0.2, glow=(255, 200, 60), strength=0.8)
    red = s.pal("mm_core", 0x77, metallic=0.1, roughness=0.15, glow=(230, 40, 0), strength=1.0)
    tip = s.light("mm_tip", (255, 250, 200), 2.5)
    zc, sq = 1.8, 0.66
    s.lathe_y("foot", [(-7.0, 0.0), (-6.9, 2.0), (-6.5, 3.2), (-5.4, 3.9), (-4.3, 3.8), (-3.5, 2.8), (-3.1, 1.9)],
              grey, z=zc, squash=sq, segments=32)
    s.lathe_y("foot_ring", [(-5.6, 3.75), (-5.4, 4.05), (-4.9, 4.05), (-4.7, 3.75)], pale, z=zc, squash=sq, segments=32)
    s.lathe_y("stem", [(-3.4, 1.9), (-2.6, 1.6), (-1.6, 1.7), (-1.0, 2.2)], dark, z=zc, squash=sq, segments=24)
    s.lathe_y("cup", [(-1.6, 1.6), (-1.1, 3.2), (-0.2, 3.9), (1.6, 4.05), (2.8, 3.9), (3.3, 3.3), (3.2, 2.6)], grey,
              z=zc, squash=sq, segments=32)
    s.lathe_y("cup_rim", [(2.6, 3.7), (2.8, 4.1), (3.2, 4.1), (3.4, 3.6)], pale, z=zc, squash=sq, segments=32)
    s.lathe_y("warhead", [(2.0, 2.6), (3.2, 2.7), (4.3, 2.4), (5.2, 1.8), (5.9, 1.0), (6.25, 0.0)], warhead, z=zc,
              squash=0.85, segments=24)
    s.sphere("tip", (0, 5.2, zc + 1.2), (0.9, 1.0, 0.5), tip, 12, 8)
    # The red core, seen through the cup's top and the stem.
    s.sphere("core", (0, -0.8, zc + 4.0 * sq - 0.45), (1.35, 1.9, 0.5), red, 20, 10)
    s.sphere("core_low", (0, -2.4, zc + 1.6 * sq - 0.2), (0.9, 1.1, 0.5), red, 14, 8)


# --- Zica supercharger ----------------------------------------------------------------------------

@model("sk_zica_super", "ships", 3)
def zica_super():
    """A steel-blue cage (columns 1-11) round a glowing egg (columns 4-8, rows 4-9), a neck on top
    (rows 0-3), a base with red lamps (rows 10-12) and claws below (row 13). Centred on x = 0.5."""
    steel = s.pal("zs_steel", 0x3a, metallic=0.45, roughness=0.25)
    pale = s.pal("zs_pale", 0x3d, metallic=0.5, roughness=0.18)
    dark = s.pal("zs_dark", 0x33, metallic=0.4, roughness=0.4)
    egg = s.pal("zs_egg", 0x76, metallic=0.1, roughness=0.1, glow=(255, 80, 10), strength=0.4)
    hot = s.light("zs_hot", (255, 235, 150), 2.6)
    lamp = s.light("zs_lamp", (255, 40, 10), 2.5)
    cx = 0.5
    s.lathe_y("neck", [(2.4, 3.2), (3.0, 3.4), (4.6, 3.4), (5.0, 2.5), (5.8, 2.4), (6.2, 3.0), (6.8, 3.1), (7.0, 2.2),
                       (7.05, 0.0)], steel, x=cx, z=1.6, squash=0.75, segments=28)
    s.lathe_y("neck_ring", [(5.2, 2.5), (5.3, 2.75), (5.7, 2.75), (5.8, 2.5)], pale, x=cx, z=1.6, squash=0.75,
              segments=28)
    s.lathe_axis("bore", [(0, 1.2), (0.2, 1.2)], dark, (cx, 6.9, 1.6), (0, 1, 0), segments=14)
    s.sphere("egg", (cx, -0.4, 2.0), (2.7, 3.2, 2.5), egg, 28, 14)
    s.sphere("egg_hot", (cx - 0.7, 0.4, 3.6), (1.2, 1.5, 0.9), hot, 16, 8)
    s.hoop("cradle", (cx, -0.4, 1.3), 3.0, 3.4, 0.55, dark, 40, 8)
    base = s.smooth_outline([(cx - 5.4, -2.6), (cx - 2.5, -3.0), (cx + 2.5, -3.0), (cx + 5.4, -2.6), (cx + 5.5, -5.6),
                             (cx + 4.0, -6.2), (cx - 4.0, -6.2), (cx - 5.5, -5.6)], 0.55)
    s.puff("base", base, -0.4, 2.4, steel, side=0.45, power=3.0)
    for side in (-1, 1):
        # The cage's bars, bowing out round the egg from the neck to the base.
        bar = s.catmull([(cx + side * 2.7, 3.2, 1.8), (cx + side * 4.6, 1.2, 2.2), (cx + side * 4.9, -1.2, 2.2),
                         (cx + side * 4.6, -3.2, 1.9)], 0.3)
        s.tube("bar", bar, [0.75, 0.85, 0.85, 0.75], pale, 10, squash=0.8)
        s.tube("bar_in", s.catmull([(cx + side * 1.8, 2.9, 3.1), (cx + side * 3.0, 0.8, 4.0),
                                    (cx + side * 2.9, -1.8, 3.6), (cx + side * 1.6, -3.1, 2.7)], 0.3),
               0.42, steel, 8)
        s.sphere("lamp", (cx + side * 3.0, -4.6, 2.35), (0.6, 0.7, 0.35), lamp, 10, 6)
    for i, x in enumerate((-4.0, -2.0, 0.0, 2.0, 4.0)):
        s.lathe_axis("claw", [(0, 0.55), (0.7, 0.4), (1.2, 0.0)], dark, (cx + x, -6.0, 0.9), (x * 0.06, -1, -0.2),
                     segments=10)


# --- Zica flamethrower ----------------------------------------------------------------------------

@model("sk_zica_flame", "ships", 87)
def zica_flame():
    """A ribbed barrel (columns 4-7, rows 1-13) between two curved blades (columns 0-2 and 9-11, rows
    3-13) joined to it at the back, red lamps on the barrel (rows 8 and 11)."""
    steel = s.pal("zf_steel", 0x3a, metallic=0.45, roughness=0.25)
    pale = s.pal("zf_pale", 0x3d, metallic=0.5, roughness=0.18)
    dark = s.pal("zf_dark", 0x34, metallic=0.4, roughness=0.4)
    bright = s.pal("zf_bright", 0x3e, metallic=0.5, roughness=0.15)
    lamp = s.light("zf_lamp", (255, 30, 10), 2.5)
    flame = s.light("zf_flame", (255, 140, 30), 3.0)
    zc = 2.2
    s.lathe_y("barrel", [(-6.9, 0.0), (-6.8, 1.5), (-6.3, 2.0), (5.2, 2.0), (5.6, 1.6), (6.0, 1.9), (6.4, 2.0),
                         (6.9, 1.7), (7.0, 0.0)], steel, z=zc, segments=24)
    for y in (5.5, 3.5, 1.5, -0.5, -2.5):
        s.lathe_y("rib", [(y - 0.35, 1.95), (y - 0.25, 2.3), (y + 0.25, 2.3), (y + 0.35, 1.95)], pale, z=zc, segments=24)
    s.lathe_axis("bore", [(0, 1.1), (0.25, 1.1)], dark, (0, 6.82, zc), (0, 1, 0), segments=14)
    s.sphere("pilot", (0, 7.0, zc), (0.8, 0.15, 0.8), flame, 12, 6)
    for y in (-1.5, -4.5):
        s.sphere("lamp", (0, y, zc + 1.95), (0.75, 0.55, 0.35), lamp, 12, 6)
    for side in (-1, 1):
        blade = s.smooth_outline([(side * 3.2, 4.2), (side * 4.6, 2.8), (side * 5.9, 0.8), (side * 6.05, -3.0),
                                  (side * 5.6, -6.2), (side * 4.4, -6.9), (side * 3.2, -6.6), (side * 3.4, -2.0),
                                  (side * 3.0, 1.0)], 0.5)
        s.puff("blade", blade, -0.4, 3.0, pale, side=0.4, power=2.4, centre=(side * 4.5, -2.0))
        s.tube("blade_edge", s.catmull([(side * 3.5, 3.4, 2.0), (side * 5.1, 0.8, 2.6), (side * 5.3, -3.0, 2.7),
                                        (side * 4.6, -6.0, 2.2)], 0.5), 0.36, bright, 8)
    s.rbox("yoke", (0, -3.8, 0.9), (7.4, 5.6, 1.8), dark, bevel=0.5)


# --- Side ship ------------------------------------------------------------------------------------

@model("sk_sideship", "ships", 245)
def sideship():
    """A little fighter: the nose (rows 0-5) with a cyan canopy (rows 2-4), the body (columns 3-8),
    wings (columns 0-11, rows 8-12) with spikes forward (columns 1 and 10, rows 6-8), the exhaust
    (columns 5-6, rows 10-13), lamps by the canopy (row 6)."""
    steel = s.pal("ss_steel", 0x3a, metallic=0.45, roughness=0.25)
    pale = s.pal("ss_pale", 0x3c, metallic=0.5, roughness=0.18)
    dark = s.pal("ss_dark", 0x35, metallic=0.4, roughness=0.35)
    canopy = s.pal("ss_canopy", 0x8b, metallic=0.2, roughness=0.06, glow=(120, 220, 230), strength=0.35)
    flame = s.light("ss_flame", (255, 100, 50), 2.8)
    lamp = s.light("ss_lamp", (255, 60, 20), 2.5)
    rows = [(-6.6, 1.0, 0.9, 0.6), (-6.0, 1.8, 1.4, 0.9), (-4.5, 2.3, 2.0, 1.1), (-2.0, 2.8, 2.4, 1.2),
            (0.5, 3.0, 2.6, 1.2), (2.5, 2.8, 2.6, 1.1), (4.0, 2.2, 2.3, 1.0), (5.5, 1.6, 1.8, 0.8), (6.5, 0.9, 1.1, 0.5)]
    samples = k.profile(rows, step=0.4)
    body = k.loft("body", [k.ring(y, w, 1.0, 20, top=t, bottom=b, power=2.3, crest=0.3) for y, w, t, b in samples],
                  steel, start_point=(0, -6.8, 0.3), end_point=(0, 7.0, 0.4))
    k.smooth(body, 50)
    s.sphere("canopy", (0, 3.6, 2.1), (1.25, 2.1, 0.85), canopy, 16, 10)
    for side in (-1, 1):
        wing = [(side * 2.4, 0.2), (side * 4.2, -1.2), (side * 5.0, -2.6), (side * 6.0, -3.0), (side * 6.0, -5.8),
                (side * 4.8, -5.4), (side * 3.8, -6.0), (side * 2.6, -5.0), (side * 2.0, -5.6)]
        s.slab("wing", wing, -0.3, 1.0, steel, bevel=0.35)
        s.tube("wing_edge", s.catmull([(side * 2.6, -0.2, 1.05), (side * 4.4, -1.6, 1.0), (side * 5.6, -3.0, 0.95)], 0.3),
               0.3, pale, 8)
        s.lathe_axis("spike", [(0, 0.75), (1.4, 0.6), (3.2, 0.0)], pale, (side * 4.5, -1.8, 0.6), (side * 0.03, 1, 0.08),
                     segments=10)
        s.lathe_axis("tip", [(0, 0.5), (2.2, 0.4), (3.0, 0.0)], dark, (side * 5.5, -4.6, 0.4), (side * 0.15, -1, 0),
                     segments=8)
        s.sphere("lamp", (side * 1.5, 0.5, 2.55), (0.45, 0.45, 0.25), lamp, 10, 6)
    s.lathe_axis("nozzle", [(0, 1.0), (0.8, 1.15), (1.0, 0.9)], dark, (0, -5.6, 0.7), (0, -1, 0), segments=14)
    s.rbox("vent", (0, -4.4, 1.85), (2.2, 3.4, 0.6), dark, bevel=0.25)
    s.sphere("vent_glow", (0, -4.6, 2.05), (0.85, 1.7, 0.35), flame, 12, 8)
    s.lathe_axis("flame", [(0, 0.85), (0.6, 0.75), (1.2, 0.35), (1.6, 0.0)], flame, (0, -6.3, 0.7), (0, -1, 0),
                 segments=12)


# --- Candy gems -----------------------------------------------------------------------------------

def candy(prefix, base, ridge, groove, eye):
    """A swirled candy gem shaped like a leaf (rows 0-12, columns 2-11, centred on x = 1): pointed at
    both ends, a broad bright ridge spiralling from its top round the left and the bottom in to a
    glowing eye right of the middle, a dark groove inside the ridge."""
    cx, zc, sq = 1.0, 0.6, 0.62
    radius = [(-6.0, 0.0), (-5.6, 1.0), (-4.6, 2.4), (-3.4, 3.5), (-1.8, 4.6), (0.0, 5.0), (2.0, 4.85), (3.6, 4.2),
              (4.9, 3.2), (6.0, 1.9), (6.7, 0.9), (7.0, 0.0)]
    s.lathe_y(prefix + "gem", radius, base, x=cx, z=zc, squash=sq, segments=32)

    def r_at(y):
        for (y0, r0), (y1, r1) in zip(radius, radius[1:]):
            if y0 <= y <= y1:
                return r0 + (r1 - r0) * (y - y0) / (y1 - y0)
        return 0.0

    def top(x, y):
        r = r_at(y)
        d = r * r - (x - cx) ** 2
        return zc + sq * math.sqrt(max(d, 0.0))

    ox, oy = cx + 0.7, -0.3

    def spiral(offset, t0, t1, count, sink):
        pts = []
        for i in range(count):
            t = t0 + (t1 - t0) * i / (count - 1)
            a = math.radians(100) + t * 1.25 * 2 * math.pi
            r = 3.9 * (1 - t) + 0.7 * t + offset
            x, y = ox + r * math.cos(a) * 0.95, oy + r * math.sin(a) * 1.1
            pts.append((x, y, top(x, y) - sink))
        return pts

    s.tube(prefix + "ridge", spiral(0.0, 0.0, 1.0, 40, 0.25), [0.55, 1.0, 0.95, 0.75, 0.5], ridge, 10, squash=0.55)
    s.tube(prefix + "groove", spiral(-1.1, 0.1, 0.85, 30, 0.2), [0.2, 0.42, 0.4, 0.3], groove, 8, squash=0.5)
    s.sphere(prefix + "eye", (ox + 0.4, oy - 0.2, top(ox + 0.4, oy - 0.2) - 0.25), (1.2, 1.3, 0.55), eye, 14, 8)


@model("sk_mint", "ships", 112)
def mint():
    candy("", s.pal("mint", 0xc5, metallic=0.1, roughness=0.08, glow=(20, 200, 60), strength=0.15),
          s.pal("mint_ridge", 0xcb, metallic=0.1, roughness=0.08, glow=(40, 255, 110), strength=0.3),
          s.pal("mint_groove", 0xc1, metallic=0.1, roughness=0.2),
          s.light("mint_eye", (190, 255, 210), 1.6, color=(200, 255, 220)))


@model("sk_cherry", "ships", 113)
def cherry():
    candy("", s.pal("cherry", 0x77, metallic=0.1, roughness=0.08, glow=(230, 50, 0), strength=0.3),
          s.pal("cherry_ridge", 0x7c, metallic=0.1, roughness=0.08, glow=(255, 200, 60), strength=0.5),
          s.pal("cherry_groove", 0x73, metallic=0.1, roughness=0.2, glow=(120, 5, 0), strength=0.2),
          s.light("cherry_eye", (255, 250, 190), 2.0))


# --- Satellite Marlo ------------------------------------------------------------------------------

@model("sk_marlo", "ships", 152)
def marlo():
    """A small red orb (columns 2-9, rows 2-9) with a glowing window lower right."""
    red = s.pal("marlo", 0x74, metallic=0.3, roughness=0.15, glow=(150, 10, 0), strength=0.3)
    window = s.pal("marlo_window", 0x79, metallic=0.1, roughness=0.15, glow=(255, 130, 20), strength=1.0)
    hot = s.light("marlo_hot", (255, 225, 120), 2.4)
    s.sphere("orb", (0, 1, 2.6), (3.9, 3.9, 3.5), red, 28, 14)
    s.sphere("window", (1.4, -0.5, 2.6 + 2.75), (1.9, 1.5, 0.75), window, 16, 8)
    s.sphere("window_hot", (1.6, -0.7, 2.6 + 3.3), (0.9, 0.7, 0.35), hot, 12, 6)


# --- Bubble gum gun -------------------------------------------------------------------------------

@model("sk_bubblegum", "ships", 95)
def bubblegum():
    """A dark glass globe (columns 1-10, rows 4-12) of gum balls (purple, orange, green, red) in a
    steel-blue rim, a grey nozzle on top (rows 2-3)."""
    rim = s.pal("bg_rim", 0x37, metallic=0.45, roughness=0.25)
    bowl = s.pal("bg_bowl", 0x32, metallic=0.3, roughness=0.3)
    glass = s.glass("bg_glass", 0x3a, alpha=0.35)
    grey = s.pal("bg_grey", 0x09, metallic=0.5, roughness=0.2)
    pale = s.pal("bg_pale", 0x0e, metallic=0.5, roughness=0.15)
    cy, zc = -1.5, 1.0
    s.sphere("bowl", (0, cy, zc), (4.5, 4.2, 1.6), bowl, 28, 12)
    s.hoop("rim", (0, cy, zc), 4.5, 4.2, 0.72, rim, 48, 10)
    s.sphere("glass", (0, cy, zc), (4.3, 4.0, 3.4), glass, 32, 14)
    balls = [((-1.0, 0.4), 1.35, 0x5b, (150, 90, 160)), ((-3.0, -1.8), 1.25, 0x79, (240, 100, 20)),
             ((0.6, -3.1), 1.35, 0x29, (40, 200, 60)), ((2.6, -1.6), 1.25, 0x4a, (230, 70, 60)),
             ((1.4, 0.4), 1.1, 0x3c, (90, 150, 230)), ((-1.4, -2.0), 1.1, 0x7c, (250, 210, 50))]
    for i, ((x, y), r, index, rgb) in enumerate(balls):
        mat = s.pal(f"bg_ball{i}", index, metallic=0.1, roughness=0.12, glow=rgb, strength=0.25)
        d = ((x / 4.3) ** 2 + ((y - cy) / 4.0) ** 2)
        z = zc + 3.4 * math.sqrt(max(0.0, 1 - d)) - r * 0.85
        s.sphere(f"ball{i}", (x, y, z), (r, r, r), mat, 16, 8)
    s.lathe_axis("stem", [(0, 0.7), (1.2, 0.6), (1.6, 0.75)], grey, (0.5, 2.0, zc + 0.6), (0, 1, 0.15), segments=12)
    s.lathe_axis("bar", [(0, 0.0), (0.05, 0.6), (4.6, 0.6), (4.65, 0.0)], grey, (-2.8, 4.45, zc + 0.9), (1, 0, 0),
                 segments=12)
    s.lathe_axis("bar_cap", [(0, 0.0), (0.05, 0.68), (1.0, 0.68), (1.05, 0.0)], pale, (1.0, 4.45, zc + 0.9), (1, 0, 0),
                 segments=12)


# --- Flying punch ---------------------------------------------------------------------------------

@model("sk_punch", "ships", 2)
def punch():
    """A red fist, knuckles up the screen: four curled fingers (rows 2-7; the middle two longer), the
    back of the hand (columns 1-10, rows 7-12) and the thumb lower left (columns 2-4, rows 9-12)."""
    red = s.pal("punch", 0x76, metallic=0.25, roughness=0.22, glow=(200, 20, 0), strength=0.2)
    orange = s.pal("punch_finger", 0x79, metallic=0.25, roughness=0.2, glow=(230, 80, 0), strength=0.3)
    hot = s.pal("punch_knuckle", 0x7b, metallic=0.2, roughness=0.15, glow=(255, 170, 30), strength=0.5)
    thumb = s.pal("punch_thumb", 0x49, metallic=0.2, roughness=0.25)
    hand = s.smooth_outline([(-5.3, 0.4), (5.3, 0.4), (5.4, -4.0), (4.0, -6.0), (-3.8, -6.0), (-5.3, -4.2)], 0.5)
    s.puff("hand", hand, -0.2, 3.4, red, side=0.45, power=2.6)
    # The fingers: x, half-width, tip y.
    # The fingers (x, half-width, front y): curled, so they slope down from the knuckles to the front.
    for x, half, tip in ((-4.85, 1.3, 4.1), (-1.5, 1.75, 5.1), (1.95, 1.65, 5.1), (4.95, 1.25, 4.1)):
        y0 = -1.4
        outline = s.superellipse(x, (tip + y0) / 2, half, (tip - y0) / 2, power=3.0, count=32)

        def slope(px, py, pz, y0=y0, tip=tip):
            u = min(max((py - y0) / (tip - y0), 0.0), 1.0)
            return pz * (1.0 - 0.5 * u * u) if pz > 0 else pz

        s.puff("finger", outline, 0.0, 4.7, orange, side=0.35, power=2.6, z_fn=slope)
        streak = [(x - half * 0.25, y, slope(0, y, 4.7 * math.sqrt(max(0.0, 1 - ((y - (tip + y0) / 2) / ((tip - y0) / 2)) ** 2)) ** 0.6) - 0.05)
                  for y in (0.2, 1.4, 2.6, tip - 1.0)]
        s.tube("streak", streak, [0.32, 0.4, 0.34, 0.2], hot, 8, squash=0.5)
    t = s.puff("thumb", s.superellipse(0, 0, 1.6, 2.7, power=2.6, count=28), 0.0, 1.6, thumb, side=0.3, power=2.0)
    t.data.transform(Matrix.Translation((-2.6, -3.8, 3.2)) @ Matrix.Rotation(math.radians(-22), 4, "Z"))


s.run()
