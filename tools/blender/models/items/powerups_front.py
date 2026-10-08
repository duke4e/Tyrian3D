"""Front weapon pick-ups (values 30001-30031: the weapon port they give), ice-blue orbs with the
weapon's symbol:

- pu_pulse_cannon (153): a white P on a red badge (Pulse-Cannon)
- pu_multi_cannon (155): a white M on a red winged badge (Multi-Cannon)
- pu_mega_cannon (157): a fireball (Mega Cannon)
- pu_laser (159): a glowing red and yellow rod (Laser)
- pu_zica_laser (161): a blue crystal drop (Zica Laser)
- pu_protron (163): three pale bubbles (Protron)
- pu_vulcan (165): three red bullets (Vulcan Cannon)
- pu_lightning (167): a blue lightning band (Lightning Cannon)
- pu_missile (201): a grey rocket (Missile Launcher)
- pu_heavy_missile (203): a green rocket with a gold band (Heavy Missile Launcher)
- pu_hyper_pulse (269): a white H-shaped arch on a red badge (Hyper Pulse)
- pu_guided_bombs (267): a dark disc with a red eye (Guided Bombs)
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import powerups_parts as p  # noqa: E402
from powerups_parts import k, px, py  # noqa: E402

ICON_153 = (6, """
...........oo...........
..........o77o..........
.......ooo7yy7ooo.......
......o7ooooooo77o......
.....o7o5555555oy7o.....
.....o7o55777o55o7o.....
.....o7o55oooo55o7o.....
.....o7o5555555o77o.....
.....o7o55ooooo777o.....
.....o7o55o7777777o.....
.....o77oooooo7777o.....
......777oooooo777......
......oooo....oooo......
.......oo......oo.......
""")

ICON_155 = (7, """
...........oo...........
..........o77o..........
.....oo..o7yy7o..oo.....
....o77ooo7yy7ooo77o....
...o7yo555oy7o555oy7o...
...o7yo5555oo5555oy7o...
....17o55o5555o55o71....
....o7o55oo55oo55o7o....
....ooo55o7oo7o55ooo....
.....oo55o7777o55oo.....
......ooo7oooo7ooo......
......o777oooo777o......
.......o77o..o77o.......
........o7o..o7o........
""")

ICON_269 = (5, """
...........oo...........
..........o77o..........
.........o7yy7o.........
........oo7yy7oo........
.......o55oy7o55o.......
......oo55oooo55oo......
.....o7o55555555o7o.....
.....o7o55555555o7o.....
.....o7o55oooo55o7o.....
.....o7o55o77o55o7o.....
.....o7o55o7oo55o7o.....
.....o7ooooooooo774.....
.....o7777oooo7777o.....
.....o7777o..o7777o.....
......o7oo....o7oo......
......ooo.....ooo.......
.......o.......o........
""")

ICON_161 = (3, """
.........oo33o..........
........o999999o........
........999999993.......
......o9998888999o......
......399888888993......
.....o998888888899o.....
.....39988888888993.....
.....39998888889993.....
.....o999988889999o.....
.....o999988889999o.....
.....o999998899999o.....
......999998899999......
......o9999999999o......
......o9999999999o......
.......o99999999o.......
.......o99999999o.......
........o999999o........
.........999999.........
..........9999..........
...........99...........
""")

ICON_167 = (3, """
........o99o.ooo........
........o999ooo.........
.......o9999o9o.........
.......o9999o9o.........
.......o93999oo.........
.......o93999o..........
.......o93999o..........
.......o939o99o.........
.......o939999o.........
.......o9339999o........
.......o9339999o........
........99399999o.......
........o9999999o.......
........o9999999o.......
.........o9999999o......
..........o999999o......
...........o99999o......
...........o99999o......
............99999o......
.............999o.......
.............ooo........
.............o..........
""")


def pulse_cannon():
    p.orb(p.RAMP_ICE)
    p.badge(ICON_153)


def multi_cannon():
    p.orb(p.RAMP_ICE)
    p.badge(ICON_155)


def hyper_pulse():
    p.orb(p.RAMP_ICE)
    p.badge(ICON_269, all_chars="o457y", red_chars="7y54")


def mega_cannon():
    """A fireball: a white-hot core in yellow and orange layers in a red rim, three drips of fire
    below (rows 18-20)."""
    p.orb(p.RAMP_ICE)
    rim = p.glow("fire_rim", (255, 30, 0), 1.4, color=(200, 20, 0))
    shell = p.glow("fire_shell", (255, 120, 10), 2.2, color=(240, 110, 10))
    core = p.glow("fire_core", (255, 240, 130), 4.0, color=(255, 240, 160))
    cx, cy = px(11.5), py(11.3)
    z = p.surf(cx, cy)
    k.smooth(k.ellipsoid("fire", (cx, cy, z + 0.2), (5.8, 6.0, 2.6), rim, 32, 16), 80)
    k.smooth(k.ellipsoid("fire_mid", (cx, cy + 0.3, z + 1.0), (4.8, 4.9, 2.6), shell, 32, 16), 80)
    k.smooth(k.ellipsoid("core", (cx, cy + 0.7, z + 2.0), (3.0, 3.2, 2.2), core, 24, 12), 80)
    for x, length in ((px(7.6), 3.0), (px(11.5), 3.2), (px(15.4), 3.0)):
        y = py(17.2)
        drip = k.lathe("drip", [(y - length, 0.0), (y - length * 0.7, 0.55), (y - length * 0.3, 0.95), (y, 1.1),
                                (y + 0.8, 0.0)], rim, 12, axis_x=x, axis_z=p.surf(x, y) + 0.3, squash=0.8)
        k.smooth(drip, 60)


def laser():
    """A rod of light (columns 7-16, rows 5-21): a red glowing capsule with a yellow-white core
    standing out of its top."""
    p.orb(p.RAMP_ICE)
    rim = k.material("laser_rim", palette=0x72, metallic=0.4, roughness=0.3)
    shell = p.glow("laser_shell", (255, 70, 10), 2.0, color=(230, 60, 10))
    core = p.glow("laser_core", (255, 240, 120), 4.0, color=(255, 245, 160))
    y0, y1 = py(21) - 0.2, py(5) + 0.2
    z = p.surf(0.0, 0.5)
    caps = [(0.0, 0.0), (0.06, 0.62), (0.16, 0.9), (0.3, 1.0), (0.7, 1.0), (0.84, 0.9), (0.94, 0.62), (1.0, 0.0)]
    rod = k.lathe("rod_rim", [(y0 + (y1 - y0) * t, 4.7 * r) for t, r in caps], rim, 32, axis_z=z - 1.4, squash=0.55)
    k.smooth(rod, 60)
    glow_rod = k.lathe("rod", [(y0 + 0.5 + (y1 - y0 - 1.0) * t, 3.9 * r) for t, r in caps], shell, 32,
                       axis_z=z - 0.6, squash=0.6)
    k.smooth(glow_rod, 60)
    k.smooth(k.lathe("rod_core", [(y0 + 2.3 + (y1 - y0 - 4.6) * t, 2.0 * r) for t, r in caps], core, 24,
                     axis_z=z + 0.6, squash=0.8), 60)


def zica_laser():
    """A faceted blue crystal drop, round on top, pointed below (columns 5-18, rows 3-22), with a
    pale glowing heart in its upper part."""
    p.orb(p.RAMP_ICE)
    blue = k.material("zica", palette=0x9a, metallic=0.25, roughness=0.1)
    heart = p.glow("zica_heart", (150, 220, 255), 2.2, color=(210, 240, 250))
    x = px(11.5)
    drop = k.lathe("drop", [(py(22) - 0.4, 0.0), (py(21), 1.1), (py(19), 2.6), (py(16), 4.6), (py(13), 6.1),
                            (py(10), 6.8), (py(7.5), 6.6), (py(5.5), 5.6), (py(4), 3.9), (py(3) + 0.4, 0.0)],
                   blue, 12, axis_x=x, squash=0.42)
    p.conform(drop, lift=-0.2)
    k.smooth(drop, 28)
    core = k.lathe("heart", [(py(15), 0.0), (py(13.5), 1.2), (py(11), 2.6), (py(8.5), 3.3), (py(6.6), 2.6),
                             (py(5.8), 0.0)], heart, 12, axis_x=x, squash=0.5)
    p.conform(core, lift=2.0)
    k.smooth(core, 28)


def protron():
    """Three pale bubbles in dark sockets, the middle one larger."""
    p.orb(p.RAMP_ICE)
    bubble = k.material("bubble", palette=0x8b, roughness=0.1, metallic=0.1, emission=(120, 200, 215),
                        emission_strength=0.35)
    socket = k.material("bubble_socket", palette=0x02, roughness=0.5)
    for x, y, r in ((px(12), py(11.2), 3.7), (px(5.5), py(13.8), 3.0), (px(17.5), py(13.8), 3.0)):
        z = p.surf(x, y)
        k.smooth(k.ellipsoid("bubble", (x, y, z + r * 0.35), (r, r, r * 0.85), bubble, 24, 14), 80)
        ring = [(x + (r + 0.15) * math.cos(a), y + (r + 0.15) * math.sin(a)) for a in
                [2 * math.pi * i / 32 for i in range(32)]]
        p.tube("socket", [(cx, cy, p.surf(cx, cy) + 0.3) for cx, cy in ring], 0.45, socket, 6, closed=True)


def vulcan():
    """Three red bullets, staggered (columns 10-14, 14-18 and 6-10), blunt at the top and tapering
    below like the shots they fire."""
    p.orb(p.RAMP_ICE)
    red = k.material("bullet", palette=0x75, metallic=0.4, roughness=0.2)
    core = p.glow("bullet_core", (255, 130, 20), 2.0, color=(250, 140, 30))
    for col, top, bottom in ((12, 5, 15.6), (16, 8, 18.6), (8, 11, 21.6)):
        p.pod("bullet", px(col), py(top) + 0.4, px(col), py(bottom), 2.3, red, core, shape="bullet")


def lightning():
    """A glowing blue bolt, bent like a wave and widening downwards, with a pale streak of light
    along its left edge."""
    p.orb(p.RAMP_ICE)
    blue = k.material("bolt", palette=0x98, metallic=0.3, roughness=0.15, emission=(30, 70, 240),
                      emission_strength=0.6)
    pale = p.glow("bolt_edge", (190, 225, 255), 2.6, color=(200, 230, 245))
    _, line = p.ribbon_from_rows("bolt", ICON_167, "39", blue, squash=0.5, grow=0.5, lift=0.4, floor=2.5)
    edge = []
    for y, xc, hw in line:
        if py(14.5) <= y <= py(6.5):
            x = xc - hw * 0.5
            edge.append((x, y, p.surf(x, y, 2.5) + 0.4 + 0.43 * hw + 0.15))
    p.tube("bolt_edge", edge, 0.5, pale, 8)


def rocket(prefix, x, profile_points, body_mat, fin_outline, fin_mat, band=None, band_mat=None, lift=0.0):
    """A rocket lying on the orb along +Y: a lathed body (profile (y, radius)) and flat fins."""
    zc = p.surf(x, sum(q[0] for q in profile_points) / len(profile_points)) + lift
    body = k.lathe(prefix, profile_points, body_mat, 24, axis_x=x, axis_z=zc, squash=0.85)
    k.smooth(body, 50)
    if band is not None:
        y0, y1, r = band
        ring = k.lathe(prefix + "_band", [(y0, r * 0.7), (y0 + 0.2, r), (y1 - 0.2, r), (y1, r * 0.7)], band_mat, 24,
                       axis_x=x, axis_z=zc, squash=0.85)
        k.smooth(ring, 50)
    fins = k.slab(prefix + "_fins", fin_outline, zc - 0.5, zc + 0.5, fin_mat, bevel_width=0.25)
    k.smooth(fins, 40)


def missile():
    """A grey rocket with a round head and swept fins (columns 7-16, rows 7-20)."""
    p.orb(p.RAMP_ICE)
    grey = k.material("rocket", palette=0x0c, metallic=0.55, roughness=0.25)
    dark = k.material("rocket_fin", palette=0x05, metallic=0.5, roughness=0.3)
    x = px(11.5)
    profile_points = [(py(19.6), 0.0), (py(19.3), 1.4), (py(18.5), 2.0), (py(16.5), 2.2), (py(14.6), 2.0),
                      (py(13.5), 1.6), (py(12.4), 2.4), (py(11), 3.0), (py(9.6), 2.9), (py(8.5), 2.3),
                      (py(7.4), 1.2), (py(7.0), 0.0)]
    fins = [(px(7) - 0.5, py(18.4)), (px(8.5), py(15.2)), (px(10), py(14.4)), (px(13), py(14.4)),
            (px(14.5), py(15.2)), (px(16) + 0.5, py(18.4)), (px(15), py(19.6)), (px(13), py(18.4)),
            (px(10), py(18.4)), (px(8), py(19.6))]
    rocket("rocket", x, profile_points, grey, fins, dark, band=(py(14.2), py(12.6), 2.0), band_mat=dark, lift=-0.2)


def heavy_missile():
    """A green rocket with a gold band and dark fins (columns 8-15, rows 6-19)."""
    p.orb(p.RAMP_ICE)
    green = k.material("rocket_green", palette=0x28, metallic=0.4, roughness=0.25)
    gold = k.material("rocket_band", palette=0xbb, metallic=0.7, roughness=0.25)
    dark = k.material("rocket_fin", palette=0x13, metallic=0.4, roughness=0.35)
    x = px(11.5)
    profile_points = [(py(19.4), 0.0), (py(19.0), 1.3), (py(17.6), 1.8), (py(15.6), 2.0), (py(14.5), 1.6),
                      (py(12.2), 1.6), (py(11), 2.6), (py(9), 2.9), (py(7.5), 2.5), (py(6.4), 1.4), (py(6.0), 0.0)]
    fins = [(px(8) - 0.5, py(19.4)), (px(8) - 0.5, py(17.5)), (px(10), py(15.6)), (px(13), py(15.6)),
            (px(15) + 0.5, py(17.5)), (px(15) + 0.5, py(19.4)), (px(13.5), py(19.4)), (px(12.5), py(18.6)),
            (px(10.5), py(18.6)), (px(9.5), py(19.4))]
    rocket("rocket", x, profile_points, green, fins, dark, band=(py(14.6), py(11.8), 2.2), band_mat=gold, lift=-0.2)


def guided_bombs():
    """A dark steel disc with a raised rim and a glowing red eye (columns 6-17, rows 8-19)."""
    p.orb(p.RAMP_ICE)
    steel = k.material("disc", palette=0x39, metallic=0.6, roughness=0.25)
    rim = k.material("disc_rim", palette=0x3c, metallic=0.6, roughness=0.2)
    eye = p.glow("eye", (255, 60, 20), 3.0, color=(220, 40, 10))
    pupil = p.glow("eye_core", (255, 200, 80), 4.0, color=(255, 210, 90))
    cx, cy = px(11.5), py(13.5)
    z = p.surf(cx, cy)
    k.smooth(k.ellipsoid("disc", (cx, cy, z - 0.2), (6.2, 6.2, 2.4), steel, 32, 14), 70)
    ring = [(cx + 5.4 * math.cos(a), cy + 5.4 * math.sin(a), z + 0.9) for a in [2 * math.pi * i / 48 for i in range(48)]]
    p.tube("disc_rim", ring, 0.7, rim, 10, closed=True)
    k.smooth(k.ellipsoid("eye", (cx, cy, z + 1.5), (2.3, 2.3, 1.4), eye, 20, 10), 70)
    k.smooth(k.ellipsoid("eye_core", (cx + 0.2, cy + 0.2, z + 2.5), (1.0, 1.0, 0.6), pupil, 12, 8), 70)


MODELS = {
    "pu_pulse_cannon": (153, pulse_cannon),
    "pu_multi_cannon": (155, multi_cannon),
    "pu_mega_cannon": (157, mega_cannon),
    "pu_laser": (159, laser),
    "pu_zica_laser": (161, zica_laser),
    "pu_protron": (163, protron),
    "pu_vulcan": (165, vulcan),
    "pu_lightning": (167, lightning),
    "pu_missile": (201, missile),
    "pu_heavy_missile": (203, heavy_missile),
    "pu_guided_bombs": (267, guided_bombs),
    "pu_hyper_pulse": (269, hyper_pulse),
}
