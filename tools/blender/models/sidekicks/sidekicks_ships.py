"""The companion ships and big cannons: 2x2 sprites of the power-ups sheet (24 x 28 pixels), seen beside
the player's ship.

- sk_warfly (sprite 87): Companion Ship Warfly, a red flying wing with a glass dome and a glowing engine
- sk_frontblaster (83): MicroSol FrontBlaster (I and II) and BattleShip-Class Firebomb, a white
  horseshoe craft, red lamps on its shoulders and arms, a bronze beak in the middle
- sk_gerund (49): Companion Ship Gerund, a round steel-blue craft with a big glass eye, curved fins
  and rounded wings
- sk_indigo (45): Protron Cannon Indigo, two teal crystal shields on curved legs round a small hull
- sk_quicksilver (47): Companion Ship Quicksilver, a blue fighter between two pods with glowing tips
- sk_tangerine (85): Protron Cannon Tangerine, a grey beetle with white arms curving down into claws
  with red lamps and bronze tips, a bronze keel in the middle
- sk_beno (43): Beno Wallop Beam and Beno Protron System -B- (and the unnamed sidekicks 33-37 that
  share the sprite), a long grey cannon with a glowing muzzle lying in a slot of a purple disc

Pixel (column c, row r) covers x = c - 12 .. c - 11, y = 13 - r .. 14 - r (sx, sy with large=True).
Run: Blender -b --factory-startup -P sidekicks_ships.py -- [--only ...] [--preview <dir>] [--check <sheets dir>]
"""
import math
import os
import sys

from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sidekick_kit as s  # noqa: E402
from sidekick_kit import k, model  # noqa: E402


def mirrored(points, axis):
    """Points of a left half mirrored to the right across x = axis (reversed, so an outline runs on)."""
    return [(2 * axis - x, y) for x, y in reversed(points)]


# --- Warfly ---------------------------------------------------------------------------------------

@model("sk_warfly", "powerups", 87, large=True)
def warfly():
    """A red flying wing (rows 7-22, its tips at columns 3 and 20, rows 15-16): a glass dome at the
    front (columns 10-14, rows 10-12), a keel down the middle, puffed wing lobes with panels, the
    engine glowing at the tail (rows 18-21)."""
    red = s.pal("warfly", 0x47, metallic=0.35, roughness=0.25)
    light = s.pal("warfly_light", 0x4a, metallic=0.35, roughness=0.22)
    dark = s.pal("warfly_dark", 0x43, metallic=0.3, roughness=0.35)
    keel = s.pal("warfly_keel", 0x44, metallic=0.35, roughness=0.25)
    blue = s.pal("warfly_blue", 0x37, metallic=0.45, roughness=0.25)
    dome = s.pal("warfly_dome", 0x6c, metallic=0.2, roughness=0.06, glow=(120, 170, 190), strength=0.2)
    fire = s.pal("warfly_fire", 0x7a, metallic=0.0, roughness=0.3, glow=(255, 130, 20), strength=0.8)
    hot = s.light("warfly_hot", (255, 235, 120), 2.6)
    vent = s.pal("warfly_vent", 0xa3, metallic=0.3, roughness=0.4)
    ax = 0.5
    left = [(ax, 7.3), (-2.5, 4.4), (-5.5, 1.6), (-8.0, -0.4), (-9.4, -1.5), (-8.2, -3.0), (-6.6, -4.6), (-3.0, -4.9),
            (-1.4, -5.6), (-0.6, -7.4)]
    wing = left + [(ax, -8.8)] + mirrored(left[1:], ax)
    s.puff("wing", s.smooth_outline(wing, 0.8), -0.6, 2.0, red, side=0.25, power=1.7, centre=(ax, -0.6), steps=6)
    for side in (-1, 1):
        lobe = s.superellipse(0, 0, 3.9, 2.6, power=2.3, count=32)
        obj = s.puff("lobe", lobe, 0.0, 1.4, light, side=0.2, power=2.2, steps=6)
        obj.data.transform(Matrix.Translation((ax + side * 4.6, -1.2, 0.9)) @ Matrix.Rotation(math.radians(side * -35), 4, "Z"))
        ring = s.hoop("panel", (0, 0, 0), 2.6, 1.6, 0.18, dark, 32, 6)
        ring.data.transform(Matrix.Translation((ax + side * 4.8, -1.3, 2.15)) @ Matrix.Rotation(math.radians(side * -35), 4, "Z"))
        s.sphere("vent", (ax + side * 1.6, -4.4, 1.5), (0.6, 0.9, 0.4), vent, 10, 6)
        s.sphere("intake", (ax + side * 1.5, -2.6, 1.95), (0.55, 0.9, 0.35), blue, 10, 6)
    s.lathe_y("keel", [(-7.0, 0.0), (-6.6, 0.9), (-5.0, 1.3), (-1.0, 1.4), (2.0, 1.3), (3.5, 1.0), (4.2, 0.0)], keel,
              x=ax, z=0.9, squash=0.9, segments=16)
    s.sphere("dome", (ax, 2.1, 1.9), (2.4, 2.1, 1.7), dome, 24, 12)
    s.hoop("dome_ring", (ax, 2.1, 1.9), 2.35, 2.05, 0.28, dark, 32, 6)
    s.lathe_y("engine", [(-8.6, 0.0), (-8.3, 1.0), (-7.2, 1.7), (-5.6, 1.8), (-4.6, 1.2), (-4.3, 0.0)], fire, x=ax,
              z=0.9, squash=0.8, segments=20)
    s.sphere("engine_hot", (ax, -6.3, 2.0), (0.9, 1.5, 0.5), hot, 12, 8)


# --- FrontBlaster ---------------------------------------------------------------------------------

@model("sk_frontblaster", "powerups", 83, large=True)
def frontblaster():
    """A white horseshoe (columns 3-22, centred on x = 1): two shoulders (rows 3-14) with red lamps
    (rows 7-9), arms down to row 21 with red lamps (row 17), a bronze beak between the shoulders
    (columns 9-16, rows 9-17), a small dome and two gun barrels at the top."""
    white = s.pal("fb_white", 0x0b, metallic=0.35, roughness=0.22)
    grey = s.pal("fb_grey", 0x08, metallic=0.4, roughness=0.25)
    dark = s.pal("fb_dark", 0x02, metallic=0.3, roughness=0.45)
    bronze = s.pal("fb_bronze", 0x18, metallic=0.45, roughness=0.22)
    glass = s.pal("fb_glass", 0x6a, metallic=0.2, roughness=0.06)
    lamp = s.pal("fb_lamp", 0x75, metallic=0.1, roughness=0.1, glow=(255, 30, 10), strength=1.0)
    muzzle = s.light("fb_muzzle", (255, 150, 40), 3.0)
    ax = 1.0
    shoulder = s.smooth_outline([(1.6, 10.6), (4.0, 11.2), (6.8, 10.0), (9.4, 7.8), (10.9, 5.0), (11.0, 0.8), (9.6, -1.2),
                                 (6.6, -1.3), (4.6, 0.2), (2.6, 3.5), (1.4, 7.5)], 0.85)
    right = s.puff("shoulder", shoulder, -0.8, 3.6, white, side=0.35, power=2.6, centre=(6.6, 5.0), steps=6)
    s.mirror(right, ax)
    s.puff("waist", s.smooth_outline([(-2.6, 7.5), (4.6, 7.5), (5.4, 0.0), (ax, -3.0), (-3.4, 0.0)], 0.9), -0.6, 2.6,
           grey, side=0.4, power=2.0, steps=5)
    beak = s.smooth_outline([(-2.4, 4.6), (ax, 5.2), (4.4, 4.6), (3.6, 0.6), (ax, -3.8), (-1.6, 0.6)], 0.8)
    s.puff("beak", beak, 0.5, 4.0, bronze, side=0.3, power=1.6, centre=(ax, 1.6), steps=6)
    s.rbox("slot", (ax, 8.6, 2.6), (1.4, 4.0, 1.2), dark, bevel=0.4)
    s.sphere("dome", (ax, 6.9, 3.6), (1.4, 1.1, 0.8), glass, 16, 8)
    for side in (-1, 1):
        x = ax + side * 7.0
        s.sphere("lamp", (x, 5.6, 2.9), (1.9, 1.6, 1.0), lamp, 16, 8)
        s.hoop("lamp_ring", (x, 5.6, 2.85), 1.9, 1.6, 0.3, grey, 20, 6)
        arm = s.catmull([(ax + side * 7.3, 0.5, 1.6), (ax + side * 7.6, -3.0, 1.8), (ax + side * 7.0, -6.0, 1.4),
                         (ax + side * 6.4, -7.4, 1.0)], 0.6)
        s.tube("arm", arm, [2.0, 1.9, 1.5, 1.0], white, 12, squash=0.85)
        s.tube("arm_band", [(ax + side * 5.6, -2.0, 2.3), (ax + side * 7.5, -1.9, 3.5), (ax + side * 9.4, -2.0, 2.3)],
               0.35, grey, 8)
        s.sphere("arm_lamp", (ax + side * 7.5, -3.4, 3.15), (1.0, 0.75, 0.55), lamp, 14, 8)
        s.lathe_axis("gun", [(0, 0.85), (1.6, 0.75), (1.7, 0.9), (2.2, 0.9), (2.25, 0.6)], grey, (ax + side * 2.6, 9.4, 2.4),
                     (0, 1, 0.1), segments=14)
        s.sphere("gun_flash", (ax + side * 2.6, 11.7, 2.62), (0.45, 0.12, 0.45), muzzle, 10, 6)


# --- Gerund ---------------------------------------------------------------------------------------

@model("sk_gerund", "powerups", 49, large=True)
def gerund():
    """A round steel-blue body (columns 8-16, rows 7-18, centred on x = 0.5) with a big glass eye
    (columns 10-14, rows 10-14), curved fins (columns 7 and 17, rows 8-15), rounded wings out to
    columns 3 and 21 (rows 10-15) and two exhausts below (rows 15-18)."""
    steel = s.pal("ge_steel", 0x39, metallic=0.45, roughness=0.25)
    pale = s.pal("ge_pale", 0x3c, metallic=0.5, roughness=0.18)
    dark = s.pal("ge_dark", 0x33, metallic=0.4, roughness=0.4)
    fin = s.pal("ge_fin", 0x5b, metallic=0.4, roughness=0.2)
    eye = s.pal("ge_eye", 0x66, metallic=0.3, roughness=0.05, glow=(60, 140, 200), strength=0.25)
    shine = s.light("ge_shine", (215, 240, 255), 1.6)
    exhaust = s.light("ge_exhaust", (255, 140, 40), 2.6)
    bronze = s.pal("ge_engine", 0xa4, metallic=0.4, roughness=0.3)
    ax = 0.5
    s.puff("body", s.superellipse(ax, 1.0, 4.6, 5.8, power=2.2, count=40), -1.0, 3.4, steel, side=0.3, power=2.2,
           steps=6)
    s.sphere("eye", (ax, 1.6, 2.9), (2.6, 2.6, 1.6), eye, 24, 12)
    s.hoop("eye_ring", (ax, 1.6, 2.95), 2.6, 2.6, 0.38, pale, 36, 8)
    s.sphere("eye_shine", (ax - 0.7, 2.5, 4.3), (0.8, 0.7, 0.3), shine, 10, 6)
    for side in (-1, 1):
        x = ax + side * 5.0
        wing = s.smooth_outline([(ax + side * 3.6, 3.4), (ax + side * 6.6, 2.9), (ax + side * 8.6, 1.4), (ax + side * 9.7, -0.4),
                                 (ax + side * 8.8, -1.8), (ax + side * 6.0, -2.0), (ax + side * 3.6, -1.6)], 0.8)
        s.puff("wing", wing, -0.6, 1.6, steel, side=0.3, power=1.6, centre=(ax + side * 6.4, 0.4), steps=6)
        s.tube("wing_edge", s.catmull([(ax + side * 6.0, 2.6, 1.0), (ax + side * 8.6, 1.0, 0.9),
                                       (ax + side * 8.9, -1.0, 0.7)], 0.5), 0.3, pale, 8)
        crescent = s.catmull([(x - side * 0.2, 5.6, 1.2), (x + side * 0.4, 3.4, 3.0), (x + side * 0.5, 0.4, 3.4),
                              (x + side * 0.2, -2.4, 2.6), (x - side * 0.4, -3.6, 1.2)], 0.5)
        s.tube("fin", crescent, [0.35, 0.65, 0.75, 0.6, 0.3], fin, 10, squash=1.4)
        s.lathe_axis("nozzle", [(0, 0.9), (1.6, 0.85), (2.0, 0.6)], bronze, (ax + side * 1.05, -2.6, 1.6),
                     (side * 0.08, -1, -0.1), segments=12)
        s.sphere("exhaust", (ax + side * 1.2, -4.65, 1.4), (0.5, 0.2, 0.5), exhaust, 10, 6)
    s.rbox("keel", (ax, -3.0, 1.9), (1.0, 3.2, 1.6), dark, bevel=0.4)


# --- Protron cannon Indigo ------------------------------------------------------------------------

@model("sk_indigo", "powerups", 45, large=True)
def indigo():
    """Two teal crystal shields (columns 2-10 and 15-23, rows 7-14, centred on x = 1) with raised inner
    panels, legs curving down from them (rows 15-21), a small blue hull between them (columns
    9-16, rows 10-17)."""
    teal = s.pal("in_teal", 0x84, metallic=0.35, roughness=0.12)
    panel = s.pal("in_panel", 0x87, metallic=0.35, roughness=0.08, glow=(110, 200, 210), strength=0.15)
    edge = s.pal("in_edge", 0x8c, metallic=0.4, roughness=0.1)
    deep = s.pal("in_deep", 0x81, metallic=0.35, roughness=0.2)
    blue = s.pal("in_blue", 0x37, metallic=0.45, roughness=0.25)
    pale = s.pal("in_pale", 0x3d, metallic=0.5, roughness=0.18)
    lamp = s.light("in_lamp", (140, 230, 255), 2.2)
    ax = 1.0
    shield = [(-5.0, 7.3), (-7.4, 4.9), (-9.7, 2.4), (-9.7, -1.4), (-6.5, -1.4), (-3.4, -1.0), (-1.4, 2.1), (-2.6, 4.6)]
    parts = [s.puff("shield", shield, -0.5, 2.0, teal, side=0.5, power=1.4, centre=(-5.4, 2.4))]
    inner = [(-5.2, 5.2), (-7.9, 2.4), (-7.8, 0.0), (-4.2, 0.2), (-2.9, 2.2)]
    parts.append(s.puff("panel", inner, 1.2, 3.1, panel, side=0.3, power=1.5, centre=(-5.4, 2.0)))
    parts.append(s.tube("rim", s.catmull([(-5.0, 6.7, 1.7), (-7.2, 4.6, 1.75), (-9.1, 2.4, 1.6)], 0.5), 0.32, edge, 8))
    leg = s.smooth_outline([(-8.6, -0.8), (-4.4, -0.8), (-4.4, -4.0), (-4.6, -7.4), (-5.6, -7.9), (-7.4, -6.6),
                            (-8.6, -4.4)], 0.5)
    parts.append(s.puff("leg", leg, -0.4, 2.0, teal, side=0.45, power=2.2, centre=(-6.4, -3.6)))
    parts.append(s.tube("leg_band", [(-8.4, -3.6, 1.4), (-6.5, -3.5, 2.25), (-4.6, -3.6, 1.4)], 0.3, deep, 8))
    parts.append(s.tube("leg_rib", s.catmull([(-5.4, -1.4, 2.0), (-5.4, -4.4, 2.1), (-5.8, -6.8, 1.6)], 0.5), 0.3, edge, 8))
    s.mirror(parts, ax)
    hull = s.smooth_outline([(ax, 4.2), (ax + 3.8, 0.4), (ax + 1.0, -4.0), (ax - 1.0, -4.0), (ax - 3.8, 0.4)], 0.5)
    s.puff("hull", hull, -0.3, 3.0, blue, side=0.35, power=1.8, centre=(ax, 0.2))
    s.tube("spine", s.catmull([(ax, 3.4, 2.4), (ax, 0.6, 3.15), (ax, -3.2, 2.0)], 0.5), 0.45, pale, 10)
    s.sphere("lamp", (ax, 1.0, 3.15), (0.7, 0.9, 0.35), lamp, 12, 6)


# --- Quicksilver ----------------------------------------------------------------------------------

@model("sk_quicksilver", "powerups", 47, large=True)
def quicksilver():
    """A blue fighter (columns 9-15, rows 6-18, centred on x = 0.5) with a dark canopy (rows 10-12) and
    two tail prongs with red lamps (row 17), wings out to pods (columns 3-5 and 19-21, rows 6-17) with
    glowing pink tips (rows 7-9) and red lamps (rows 12-14), small fins at the wing tips."""
    steel = s.pal("qs_steel", 0x3a, metallic=0.45, roughness=0.25)
    pale = s.pal("qs_pale", 0x3c, metallic=0.5, roughness=0.18)
    dark = s.pal("qs_dark", 0x34, metallic=0.4, roughness=0.35)
    canopy = s.pal("qs_canopy", 0x65, metallic=0.3, roughness=0.05, glow=(80, 120, 160), strength=0.2)
    tip = s.pal("qs_tip", 0x4a, metallic=0.2, roughness=0.15, glow=(255, 110, 90), strength=0.6)
    lamp = s.pal("qs_lamp", 0x77, metallic=0.1, roughness=0.1, glow=(255, 70, 10), strength=1.2)
    strut = s.pal("qs_strut", 0x56, metallic=0.4, roughness=0.3)
    engine = s.light("qs_engine", (255, 150, 50), 2.6)
    ax = 0.5
    rows = [(-4.8, 1.0, 0.8, 0.6), (-3.6, 2.4, 1.8, 0.9), (-1.8, 3.0, 2.5, 1.1), (0.5, 3.2, 2.8, 1.2), (3.0, 3.0, 2.7, 1.1),
            (4.6, 2.3, 2.2, 0.9), (6.2, 1.3, 1.4, 0.6), (7.4, 0.5, 0.7, 0.4)]
    samples = k.profile(rows, step=0.4)
    body = k.loft("body", [k.ring(y, w, 1.0, 22, x=ax, top=t, bottom=b, power=2.4, crest=0.25) for y, w, t, b in samples],
                  steel, start_point=(ax, -5.0, 0.3), end_point=(ax, 7.6, 0.3))
    k.smooth(body, 50)
    s.sphere("canopy", (ax, 2.0, 2.2), (1.6, 2.4, 1.0), canopy, 18, 10)
    s.sphere("canopy_shine", (ax - 0.4, 2.8, 3.05), (0.5, 0.7, 0.2), s.light("qs_shine", (220, 240, 255), 1.4), 8, 6)
    s.sphere("engine", (ax, -4.2, 1.3), (1.0, 0.9, 0.6), engine, 12, 6)
    for side in (-1, 1):
        px = ax + side * 8.0
        prong = s.catmull([(ax + side * 1.6, -0.5, 1.6), (ax + side * 2.0, -2.8, 1.3), (ax + side * 2.1, -4.6, 1.0)], 0.5)
        s.tube("prong", prong, [0.9, 0.8, 0.6], dark, 10)
        s.sphere("prong_lamp", (ax + side * 2.1, -4.0, 1.75), (0.55, 0.55, 0.35), lamp, 10, 6)
        wing = [(ax + side * 2.6, 3.4), (px - side * 1.0, 3.0), (px - side * 1.0, -2.6), (ax + side * 2.6, -2.2)]
        s.slab("wing", wing, 0.0, 1.0, steel, bevel=0.35)
        s.tube("wing_edge", [(ax + side * 2.8, 3.2, 1.0), (px - side * 1.2, 2.8, 1.0)], 0.3, pale, 8)
        s.slab("strut", [(ax + side * 4.6, 3.6), (ax + side * 5.4, 3.6), (ax + side * 5.4, 1.4), (ax + side * 4.6, 1.4)],
               0.8, 2.0, strut, bevel=0.25)
        s.lathe_y("pod", [(-4.4, 0.0), (-4.2, 1.0), (-3.2, 1.5), (3.8, 1.55), (4.4, 1.4)], steel, x=px, z=1.4,
                  segments=18)
        s.lathe_y("pod_tip", [(4.2, 1.42), (5.4, 1.35), (6.6, 1.0), (7.4, 0.5), (7.7, 0.0)], tip, x=px, z=1.4,
                  segments=18)
        s.sphere("pod_lamp", (px, 0.5, 2.7), (0.7, 1.6, 0.45), lamp, 12, 8)
        fin = [(px + side * 1.2, 1.4), (px + side * 3.3, -0.4), (px + side * 3.3, -1.8), (px + side * 1.2, -1.6)]
        s.slab("tip_fin", fin, 0.4, 1.3, dark, bevel=0.25)
        s.sphere("fin_lamp", (px + side * 2.9, -1.2, 1.3), (0.4, 0.5, 0.3), lamp, 8, 6)


# --- Protron cannon Tangerine ---------------------------------------------------------------------

@model("sk_tangerine", "powerups", 85, large=True)
def tangerine():
    """A grey beetle (columns 2-22, rows 3-14, centred on x = 0.5): a bronze keel down its middle
    (columns 11-13, rows 5-13), white arms from the top curving down into claws (rows 13-21) with red
    lamps (row 17) and bronze tips (rows 19-21), two gun barrels at the top (row 3-4)."""
    grey = s.pal("tg_grey", 0x07, metallic=0.4, roughness=0.25)
    white = s.pal("tg_white", 0x0c, metallic=0.4, roughness=0.18)
    dark = s.pal("tg_dark", 0x02, metallic=0.3, roughness=0.45)
    bronze = s.pal("tg_bronze", 0x17, metallic=0.45, roughness=0.22)
    lamp = s.pal("tg_lamp", 0x76, metallic=0.1, roughness=0.1, glow=(255, 30, 10), strength=1.0)
    muzzle = s.light("tg_muzzle", (255, 150, 40), 3.0)
    ax = 0.5
    half = [(ax, 10.0), (-1.8, 11.1), (-4.0, 10.6), (-6.4, 9.2), (-8.8, 6.8), (-10.0, 4.4), (-10.0, 2.6), (-8.6, 1.0),
            (-6.8, -0.6), (-4.0, -0.6), (-2.0, -0.4)]
    body = half + [(ax, -1.2)] + mirrored(half[1:], ax)
    s.puff("body", s.smooth_outline(body, 0.85), -0.8, 3.4, grey, side=0.35, power=2.2, centre=(ax, 4.5), steps=6)
    keel = s.smooth_outline([(ax - 1.8, 9.2), (ax + 1.8, 9.2), (ax + 1.6, 2.0), (ax, -0.8), (ax - 1.6, 2.0)], 0.8)
    s.puff("keel", keel, 0.5, 4.4, bronze, side=0.3, power=2.0, centre=(ax, 4.0))
    s.rbox("keel_slot", (ax, 9.6, 3.2), (2.6, 1.0, 0.8), dark, bevel=0.3)
    for side in (-1, 1):
        arm = s.catmull([(ax + side * 3.4, 9.6, 3.0), (ax + side * 3.7, 5.0, 3.6), (ax + side * 4.8, 1.0, 3.0),
                         (ax + side * 6.5, -2.4, 2.3), (ax + side * 7.4, -4.4, 2.0), (ax + side * 6.8, -6.0, 1.7),
                         (ax + side * 5.2, -6.9, 1.4)], 0.6)
        s.tube("arm", arm, [1.2, 1.35, 1.35, 1.5, 1.6, 1.3, 1.0], white, 10, squash=0.8)
        s.lathe_axis("claw_tip", [(0, 0.95), (1.2, 0.75), (2.2, 0.0)], bronze, (ax + side * 5.0, -6.95, 1.35),
                     (-side * 1, -0.25, 0), segments=12)
        s.sphere("lamp", (ax + side * 7.4, -3.6, 3.25), (1.0, 0.8, 0.55), lamp, 14, 8)
        s.sphere("lamp_top", (ax + side * 8.0, 6.4, 2.4), (0.6, 0.6, 0.35), lamp, 10, 6)
        s.tube("ridge", s.catmull([(ax + side * 6.0, 8.6, 2.2), (ax + side * 8.6, 5.0, 2.1),
                                   (ax + side * 9.0, 2.6, 1.6)], 0.5), 0.35, white, 8)
        s.lathe_axis("gun", [(0, 0.9), (1.4, 0.8), (1.5, 0.95), (2.0, 0.95), (2.05, 0.6)], grey, (ax + side * 3.0, 9.6, 2.0),
                     (0, 1, 0.1), segments=14)
        s.sphere("gun_flash", (ax + side * 3.0, 11.65, 2.2), (0.45, 0.12, 0.45), muzzle, 10, 6)


# --- Beno -----------------------------------------------------------------------------------------

@model("sk_beno", "powerups", 43, large=True)
def beno():
    """A purple disc (columns 2-21, rows 6-25, centred on (0, -2)) with a slot down its upper half where
    a long grey cannon lies (columns 9-15, rows 0-16, centred on x = 0.5), its muzzle glowing (rows 0-1);
    raised fins either side of the slot (columns 6-8 and 16-18, rows 9-14), a groove across the disc
    (rows 16-17) and a tongue below it (columns 9-14, rows 19-24)."""
    purple = s.pal("bn_purple", 0x57, metallic=0.35, roughness=0.25)
    light = s.pal("bn_light", 0x5a, metallic=0.35, roughness=0.2)
    pale = s.pal("bn_pale", 0x5c, metallic=0.4, roughness=0.18)
    deep = s.pal("bn_deep", 0x52, metallic=0.3, roughness=0.4)
    grey = s.pal("bn_grey", 0x08, metallic=0.45, roughness=0.22)
    steel = s.pal("bn_steel", 0x0b, metallic=0.5, roughness=0.16)
    dark = s.pal("bn_dark", 0x03, metallic=0.3, roughness=0.45)
    muzzle = s.pal("bn_muzzle", 0x7a, metallic=0.1, roughness=0.2, glow=(255, 130, 20), strength=1.0)
    hot = s.light("bn_hot", (255, 240, 150), 2.8)
    bx = 0.5
    zc = 3.4

    def disc_top(x, y):
        r2 = (x / 10.0) ** 2 + ((y + 2.0) / 10.0) ** 2
        return 0.8 + 2.6 * math.sqrt(max(0.0, 1 - r2 ** 1.2))

    disc = s.puff("disc", s.superellipse(0, -2.0, 10.0, 10.0, power=2.0, count=64), -1.0, 3.4, purple, side=0.3,
                  power=2.4)
    cutter = s.rbox("cutter", (bx, 5.6, 4.0), (7.6, 9.6, 6.0), dark, bevel=0.6)
    s.cut(disc, cutter)
    k.smooth(disc, 50)
    s.rbox("slot_floor", (bx, 5.6, 0.6), (7.2, 9.0, 0.8), deep, bevel=0.3)
    # The cannon: its breech at the disc's middle, the barrel with rings, the glowing muzzle.
    s.lathe_y("breech", [(-3.4, 0.0), (-3.2, 2.0), (-2.6, 2.6), (2.6, 2.6), (3.2, 2.3)], grey, x=bx, z=zc - 0.2,
              squash=0.9, segments=24)
    s.lathe_y("barrel", [(2.4, 2.7), (12.0, 2.95), (12.4, 3.2), (13.2, 3.2), (13.4, 3.0)], grey, x=bx, z=zc,
              squash=0.9, segments=28)
    for y in (11.0, 8.2, 5.4, 2.7):
        s.lathe_y("ring", [(y - 0.45, 2.85), (y - 0.3, 3.2), (y + 0.3, 3.2), (y + 0.45, 2.85)], steel, x=bx, z=zc,
                  squash=0.9, segments=28)
    s.lathe_y("muzzle", [(13.3, 3.05), (13.5, 3.15), (13.95, 2.9), (14.05, 1.8), (14.1, 0.0)], muzzle, x=bx, z=zc,
              squash=0.9, segments=28)
    s.sphere("muzzle_hot", (bx, 14.0, zc), (1.6, 0.2, 1.4), hot, 14, 6)
    s.tube("barrel_shine", [(bx - 1.2, 3.0, zc + 2.55), (bx - 1.3, 8.0, zc + 2.62), (bx - 1.3, 12.6, zc + 2.65)], 0.35,
           s.pal("bn_shine", 0x0e, metallic=0.5, roughness=0.1), 8)
    # Fins either side of the slot, the groove across the disc and the tongue below it.
    for side in (-1, 1):
        x = bx + side * 5.0
        fin = s.catmull([(x - side * 0.2, 5.4, disc_top(x, 5.4)), (x + side * 0.3, 2.8, disc_top(x, 2.8) + 0.8),
                         (x + side * 0.8, -0.6, disc_top(x, -0.6) + 0.4)], 0.5)
        s.tube("fin", fin, [0.45, 0.85, 0.5], pale, 10, squash=1.3)
    groove = [(x, -3.0 - 0.9 * (1 - (x / 9.4) ** 2), disc_top(x, -3.0 - 0.9 * (1 - (x / 9.4) ** 2)) + 0.05)
              for x in [-9.0 + 18.0 * i / 24 for i in range(25)]]
    s.tube("groove", groove, 0.35, deep, 8)
    tongue = s.superellipse(bx, -8.3, 2.8, 2.6, power=2.4, count=40)
    s.puff("tongue", tongue, 0.0, 1.0, light, side=0.3, power=2.2,
           z_fn=lambda x, y, z: z + disc_top(x, y) - 0.6)
    s.hoop("tongue_rim", (bx, -8.3, 0), 2.8, 2.6, 0.25, deep, 36, 6).data.transform(
        Matrix.Translation((0, 0, disc_top(bx, -8.3) - 0.25)))


s.run()
