"""Sidekick pick-ups (values 32001-32015: the sidekick they give), green orbs with the sidekick's
symbol, and the dragonwing's green orb (value 30000: in Galaga mode it brings the second player's
ship, otherwise it is a purple ball):

- pu_single_shot (205): a red pod (Single Shot Option)
- pu_dual_shot (207): two red pods (Dual Shot Option)
- pu_charge_cannon (229): a glowing blue dome with tendrils (Charge Cannon)
- pu_vulcan_shot (231): three red needles (Vulcan Shot Option)
- pu_atom_bombs (233): two grey canisters with red bands (Atom Bombs)
- pu_mini_missile (235): three steel-blue missiles (Mini-Missile)
- pu_mega_missile (237): a silver S over a red missile (MegaMissile)
- pu_microbomb (239): a steel ball with a glowing band (MicroBomb)
- pu_postit_mine (241): two crossed blades (Post-It Mine)
- pu_dragonwing (281): the red dragonwing ship (Galaga mode's second ship)
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import powerups_parts as p  # noqa: E402
from powerups_parts import k, px, py  # noqa: E402
from mathutils import Matrix  # noqa: E402

ICON_237 = (5, """
...........44...........
..........4444..........
........33333333........
.......333333333........
......333.4444..........
......333.4444..........
......3333333333........
.......3333333333.......
........4.4444333.......
........444444333.......
.......3333333333.......
.......333333333........
........44.44.44........
........44.44.44........
""")

ICON_281 = (7, """
............4...........
...........444..........
..........44444.........
.........4466644........
.......4446366644o......
......4444666o64444.....
.....444444666444444....
....44444444444444o44...
...44444444343444o4444..
...44444443a4a344o4444..
....4444437444734444o...
.....o444o77477o444o....
..........o7y7o.........
...........ooo..........
""")


def red_pod_materials():
    red = k.material("pod", palette=0x75, metallic=0.4, roughness=0.2, emission=(150, 10, 0), emission_strength=0.5)
    core = p.glow("pod_core", (255, 130, 20), 2.2, color=(250, 140, 30))
    return red, core


def single_shot():
    """A red pod, round at the top, pointed below (column 12, rows 8-18)."""
    p.orb(p.RAMP_GREEN)
    red, core = red_pod_materials()
    p.pod("pod", px(12), py(8) + 0.4, px(12), py(18) - 0.2, 2.5, red, core, shape="bullet")


def dual_shot():
    """Two red pods side by side (columns 8 and 15, rows 9-19)."""
    p.orb(p.RAMP_GREEN)
    red, core = red_pod_materials()
    for col in (8, 15):
        p.pod("pod", px(col), py(9) + 0.4, px(col), py(19) - 0.2, 2.5, red, core, shape="bullet")


def charge_cannon():
    """A glowing blue dome with a pale heart, tendrils below (columns 6-17, rows 6-20)."""
    p.orb(p.RAMP_GREEN)
    rim = p.glow("charge_rim", (20, 50, 255), 1.4, color=(20, 50, 220))
    blue = p.glow("charge", (60, 130, 255), 2.0, color=(70, 140, 245))
    heart = p.glow("charge_heart", (190, 235, 255), 3.0, color=(210, 245, 255))
    cx, cy = px(11.5), py(12)
    z = p.surf(cx, cy)
    k.smooth(k.ellipsoid("dome", (cx, cy, z + 0.2), (5.8, 6.2, 2.8), rim, 32, 16), 80)
    k.smooth(k.ellipsoid("dome_mid", (cx, cy + 0.6, z + 1.1), (4.6, 4.6, 2.6), blue, 28, 14), 80)
    k.smooth(k.ellipsoid("heart", (cx, cy + 1.2, z + 2.1), (2.6, 2.8, 2.0), heart, 20, 12), 80)
    for x, length in ((px(7.6), 2.6), (px(10.4), 2.2), (px(12.6), 2.2), (px(15.4), 2.6)):
        y = py(17.4)
        tendril = k.lathe("tendril", [(y - length, 0.0), (y - length * 0.6, 0.45), (y, 0.8), (y + 0.8, 0.0)], rim, 10,
                          axis_x=x, axis_z=p.surf(x, y) + 0.3, squash=0.8)
        k.smooth(tendril, 60)


def vulcan_shot():
    """Three thin red needles, staggered (columns 11, 13 and 9)."""
    p.orb(p.RAMP_GREEN)
    red, core = red_pod_materials()
    for col, top, bottom in ((11, 6.6, 17.5), (13, 8.6, 18.5), (9, 10.6, 21.4)):
        p.pod("needle", px(col), py(top), px(col), py(bottom), 1.4, red, core, shape="bullet")


def canister(x, y0, y1, grey, red, dark):
    """A grey canister lying along Y with a red band round its middle and dark rings by its caps."""
    z = p.surf(x, (y0 + y1) / 2) - 0.6
    length = y1 - y0
    shape = [(0.0, 0.0), (0.02, 0.6), (0.06, 0.9), (0.12, 1.0), (0.88, 1.0), (0.94, 0.9), (0.98, 0.6), (1.0, 0.0)]
    body = k.lathe("canister", [(y0 + length * t, 3.15 * r) for t, r in shape], grey, 28, axis_x=x, axis_z=z, squash=0.95)
    k.smooth(body, 50)
    ym = (y0 + y1) / 2 + 0.3
    band = k.lathe("band", [(ym - 2.2, 3.05), (ym - 2.0, 3.35), (ym + 2.0, 3.35), (ym + 2.2, 3.05)], red, 28,
                   axis_x=x, axis_z=z, squash=0.95)
    k.smooth(band, 50)
    for yr in (y0 + length * 0.2, y1 - length * 0.2):
        ring = k.lathe("ring", [(yr - 0.25, 3.1), (yr - 0.15, 3.3), (yr + 0.15, 3.3), (yr + 0.25, 3.1)], dark, 28,
                       axis_x=x, axis_z=z, squash=0.95)
        k.smooth(ring, 50)


def atom_bombs():
    """Two grey canisters side by side, red bands round their middles (columns 4-10 and 12-19)."""
    p.orb(p.RAMP_GREEN)
    grey = k.material("canister", palette=0x0a, metallic=0.6, roughness=0.25)
    red = k.material("canister_band", palette=0x76, metallic=0.4, roughness=0.2, emission=(200, 20, 0),
                     emission_strength=0.6)
    dark = k.material("canister_ring", palette=0x03, metallic=0.4, roughness=0.4)
    for x in (px(7.5), px(15.5)):
        canister(x, py(20) - 0.3, py(7) + 0.3, grey, red, dark)


def mini_missile(x, top, bottom, steel, red, dark):
    """A small missile pointing up: a lathed body, red canards by the nose, dark tail fins."""
    zc = p.surf(x, (top + bottom) / 2) + 0.2
    length = top - bottom
    shape = [(0.0, 0.0), (0.02, 0.8), (0.1, 1.0), (0.72, 1.0), (0.85, 0.85), (0.94, 0.5), (1.0, 0.0)]
    body = k.lathe("missile", [(bottom + length * t, 1.75 * r) for t, r in shape], steel, 20, axis_x=x, axis_z=zc,
                   squash=0.9)
    k.smooth(body, 50)
    yc = top - length * 0.25
    canards = [(x - 3.3, yc - 0.6), (x - 1.0, yc + 0.4), (x + 1.0, yc + 0.4), (x + 3.3, yc - 0.6), (x + 3.3, yc - 1.4),
               (x - 3.3, yc - 1.4)]
    k.smooth(k.slab("canards", canards, zc - 0.35, zc + 0.35, red, bevel_width=0.2), 40)
    yf = bottom + 0.3
    fins = [(x - 2.6, yf - 0.4), (x - 1.0, yf + 2.4), (x + 1.0, yf + 2.4), (x + 2.6, yf - 0.4), (x + 1.2, yf - 0.4),
            (x, yf + 0.6), (x - 1.2, yf - 0.4)]
    k.smooth(k.slab("fins", fins, zc - 0.35, zc + 0.35, dark, bevel_width=0.2), 40)


def mini_missiles():
    """Three steel-blue missiles, staggered (columns 12, 17 and 7)."""
    p.orb(p.RAMP_GREEN)
    steel = k.material("missile", palette=0x3b, metallic=0.6, roughness=0.25)
    red = k.material("missile_canard", palette=0x76, metallic=0.4, roughness=0.25, emission=(200, 20, 0),
                     emission_strength=0.6)
    dark = k.material("missile_fin", palette=0x66, metallic=0.5, roughness=0.3)
    for col, top, bottom in ((12, 4, 16), (17, 7, 19), (7, 10, 22)):
        mini_missile(px(col), py(top) + 0.5, py(bottom) - 0.4, steel, red, dark)


def mega_missile():
    """A silver S over a red missile with three red legs below."""
    p.orb(p.RAMP_GREEN)
    dark = k.material("s_dark", palette=0x33, metallic=0.3, roughness=0.4)
    red = k.material("s_red", palette=0x48, metallic=0.4, roughness=0.25)
    silver = k.material("s_silver", palette=0x3d, metallic=0.7, roughness=0.18)
    p.emblem("s_base", ICON_237, "34", -1.5, 0.6, dark, bevel=0.3)
    p.emblem("s_red", ICON_237, "4", -0.6, 1.4, red, bevel=0.35)
    p.emblem("s", ICON_237, "3", -0.6, 2.3, silver, bevel=0.45)


def microbomb():
    """A steel ball with a glowing red and yellow band round it (columns 6-16, rows 9-19)."""
    p.orb(p.RAMP_GREEN)
    steel = k.material("bomb", palette=0x3a, metallic=0.6, roughness=0.2)
    band = p.glow("bomb_band", (255, 80, 10), 2.0, color=(230, 60, 10))
    hot = p.glow("bomb_band_hot", (255, 220, 90), 3.0, color=(255, 225, 120))
    cx, cy = px(11.5), py(14)
    z = p.surf(cx, cy) + 0.6
    k.smooth(k.ellipsoid("bomb", (cx, cy, z), (5.3, 5.2, 4.6), steel, 32, 18), 80)
    # The band: round the ball in an upright plane across the screen (seen from above, a stripe).
    yb = py(14) + 0.2
    ring = [(cx + 5.3 * math.cos(a), yb, z + 4.6 * math.sin(a)) for a in [2 * math.pi * i / 48 for i in range(48)]]
    p.tube("band", ring, 1.3, band, 12, closed=True)
    k.smooth(k.ellipsoid("band_hot", (cx - 1.2, yb + 0.4, z + 4.9), (2.2, 0.8, 0.6), hot, 12, 8), 60)


def postit_mine():
    """Two crossed blades, dark steel with bronze edges, crossing at a bronze hub."""
    p.orb(p.RAMP_GREEN)
    steel = k.material("blade", palette=0x05, metallic=0.6, roughness=0.25)
    bronze = k.material("blade_edge", palette=0xbb, metallic=0.7, roughness=0.2)
    cx, cy = px(11.5), py(12.5)
    z = p.surf(cx, cy) + 0.4
    for i, angle in enumerate((45, -45)):
        blade = p.star4(f"blade{i}", 0, 0, 1.0, 1.0, 1.0, steel)
        # A long diamond: stretched along X, then turned.
        blade.data.transform(Matrix.Rotation(math.radians(angle), 4, "Z") @ Matrix.Diagonal((8.4, 1.6, 1.0, 1.0)))
        blade.data.transform(Matrix.Translation((cx, cy, z)))
        edge = p.star4(f"edge{i}", 0, 0, 1.0, 1.0, 1.0, bronze)
        edge.data.transform(Matrix.Rotation(math.radians(angle), 4, "Z") @ Matrix.Diagonal((6.0, 0.7, 1.35, 1.0)))
        edge.data.transform(Matrix.Translation((cx, cy, z + 0.1)))
    k.smooth(k.ellipsoid("hub", (cx, cy, z + 0.9), (1.8, 1.8, 0.9), bronze, 16, 8), 60)


def dragonwing():
    """The dragonwing: a red bat-winged ship (rows 7-20, columns 3-22, centred on x 0.5) with a
    grey canopy, steel intakes and a glowing engine between notched trailing edges."""
    p.orb(p.RAMP_GREEN)
    red = k.material("dragon", palette=0x48, metallic=0.45, roughness=0.25)
    dark = k.material("dragon_dark", palette=0x44, metallic=0.4, roughness=0.3)
    grey = k.material("dragon_canopy", palette=0x6c, metallic=0.6, roughness=0.15)
    steel = k.material("dragon_steel", palette=0x3a, metallic=0.6, roughness=0.25)
    engine = p.glow("dragon_engine", (255, 120, 30), 3.0, color=(240, 90, 20))
    wing = [(0.5, 7.2), (-1.0, 5.5), (-3.0, 4.0), (-5.0, 3.0), (-7.0, 1.0), (-9.0, -0.5), (-9.0, -2.5), (-7.0, -5.0),
            (-4.5, -4.2), (-2.0, -5.0), (-1.0, -6.6), (2.0, -6.6), (3.0, -5.0), (5.5, -4.2), (8.0, -5.0), (10.0, -2.5),
            (10.0, -0.5), (8.0, 1.0), (6.0, 3.0), (4.0, 4.0), (2.0, 5.5)]
    wings = k.slab("wings", wing, -1.2, 0.9, red, bevel_width=0.45)
    p.conform(wings, lift=0.0, floor=2.5)
    k.smooth(wings, 40)
    x = 0.5
    spine = k.lathe("spine", [(-6.6, 0.0), (-6.2, 1.4), (-4.0, 2.0), (0.0, 2.3), (3.0, 2.0), (5.5, 1.2), (7.0, 0.0)],
                    dark, 20, axis_x=x, squash=0.6)
    p.conform(spine, lift=0.6)
    k.smooth(spine, 50)
    k.smooth(k.ellipsoid("canopy", (x, py(11.3), p.surf(x, py(11.3)) + 1.9), (1.6, 2.4, 1.1), grey, 16, 10), 60)
    for ix in (px(11) - 0.2, px(14) + 0.2):
        k.smooth(k.ellipsoid("intake", (ix, py(15.6), p.surf(ix, py(15.6)) + 1.3), (0.9, 1.3, 0.6), steel, 12, 8), 60)
    k.smooth(k.ellipsoid("engine", (x, py(19.2), p.surf(x, py(19.2)) + 0.9), (1.3, 1.0, 0.8), engine, 12, 8), 60)


MODELS = {
    "pu_single_shot": (205, single_shot),
    "pu_dual_shot": (207, dual_shot),
    "pu_charge_cannon": (229, charge_cannon),
    "pu_vulcan_shot": (231, vulcan_shot),
    "pu_atom_bombs": (233, atom_bombs),
    "pu_mini_missile": (235, mini_missiles),
    "pu_mega_missile": (237, mega_missile),
    "pu_microbomb": (239, microbomb),
    "pu_postit_mine": (241, postit_mine),
    "pu_dragonwing": (281, dragonwing),
}
