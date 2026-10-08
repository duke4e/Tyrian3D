"""Rear weapon pick-ups (values 31009-31022: the weapon port they give), red orbs with the weapon's
symbol:

- pu_starburst (169): two glowing four-pointed stars (Starburst)
- pu_multi_rear (191): a crown of red flames (Multi-Cannon, rear)
- pu_sonic_wave (193): a glowing green chevron (Sonic Wave)
- pu_protron_rear (195): four blue balls in a diamond (Protron, rear)
- pu_wild_ball (197): a green ball on two steel lumps (Wild Ball)
- pu_vulcan_rear (199): two flames slanting in (Vulcan Cannon, rear)
- pu_heavy_missile_rear (243): steel wings with red launchers (Rear Heavy Missile Launcher)
- pu_mega_pulse_rear (245): a red ring with a glowing heart (Rear Mega Pulse)
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import powerups_parts as p  # noqa: E402
from powerups_parts import k, px, py  # noqa: E402

ICON_191 = (7, """
........o7....7o........
.......o77o..o77o.......
.......777oo.o777.......
......o777oooo777o......
.....o777o7777o777o.....
......777o7777o777......
....o7777.7777.7777o....
..o.17y77.7777.77y71.o..
...o7yy7..7777..7yy7o...
...o7yy7o.7y77.o7yy7o...
.....77...7yy7...77.....
.....oo..o7yy7o..oo.....
..........o77...........
...........oo...........
""")

ICON_193 = (8, """
.......o........o.......
.......cc......cc.......
.......cc......cc.......
.......ccc....ccc.......
.......cccc..cccc.......
.......cccccccccc.......
.......cccccccccc.......
.......occcccccco.......
........cccccccc........
........cccccccc........
........occcccco........
.........cccccc.........
..........occo..........
""")

ICON_243 = (8, """
.ooooo............ooooo.
.o3333o..........o3333o.
.o33333o........o33333o.
.o33333o........o33333o.
.o3333770o....o0773333o.
..o3377776o..o6777733o..
...oo7y7333oo3337y7oo...
.....07331322313370.....
......633322223336......
......o3323223233o......
.......o222oo222o.......
.......o222..222o.......
........ooo..ooo........
""")

ICON_245 = (7, """
.........oo.............
........o77oo...........
.......o77777oooo.......
......o7777tttttto......
......o77oo7tttoo.......
.....o77oy7o7ttoo.......
.....o77o7oo7tttoo......
.....o77oooo7tttto......
.....o77oo7o7ttto.......
......o77oo7tttto.......
......o777777tttto......
.......o77777oooo.......
........o77oo...........
.........oo.............
""")


def starburst():
    """Two four-pointed stars of fire, red with yellow hearts (centred on column 7 row 13 and
    column 17 row 14)."""
    p.orb(p.RAMP_RED)
    red = p.glow("star", (255, 50, 0), 1.6, color=(220, 40, 0))
    yellow = p.glow("star_heart", (255, 220, 80), 3.5, color=(255, 230, 120))
    for i, (x, y) in enumerate(((px(7), py(13)), (px(17), py(14)))):
        outer = p.star4(f"star{i}", x, y, 6.0, 1.5, 1.3, red)
        p.conform(outer, lift=0.3, step=0.6, floor=2.0)
        inner = p.star4(f"star_heart{i}", x, y, 3.6, 1.0, 1.1, yellow)
        p.conform(inner, lift=1.0, step=0.6)


def multi_rear():
    """A crown of red flames with glowing yellow tips."""
    p.orb(p.RAMP_RED)
    dark = k.material("flame_dark", palette=0x71, metallic=0.3, roughness=0.35)
    red = k.material("flame", palette=0x76, metallic=0.3, roughness=0.25, emission=(200, 20, 0),
                     emission_strength=0.35)
    yellow = p.glow("flame_tip", (255, 190, 40), 3.0, color=(255, 200, 60))
    p.emblem("flames_base", ICON_191, "o17y", -1.4, 0.8, dark, bevel=0.3)
    p.emblem("flames", ICON_191, "17y", -0.6, 1.6, red, bevel=0.35)
    p.emblem("flame_tips", ICON_191, "y", 0.0, 2.2, yellow, bevel=0.3, smoothing=2)


def sonic_wave():
    """A thick glowing green chevron pointing down."""
    p.orb(p.RAMP_RED)
    dark = k.material("chevron_dark", palette=0xc2, metallic=0.3, roughness=0.3)
    green = k.material("chevron", palette=0xcb, metallic=0.2, roughness=0.15, emission=(30, 230, 70),
                       emission_strength=0.6)
    p.emblem("chevron_base", ICON_193, "oc", -1.4, 1.0, dark, bevel=0.3)
    p.emblem("chevron", ICON_193, "c", -0.6, 2.4, green, bevel=0.7, smoothing=2)


def protron_rear():
    """Four glossy blue balls in a diamond, in dark sockets."""
    p.orb(p.RAMP_RED)
    blue = k.material("ball_blue", palette=0x9a, metallic=0.2, roughness=0.12, emission=(30, 60, 200),
                      emission_strength=0.4)
    socket = k.material("ball_socket", palette=0x31, roughness=0.5)
    for col, row in ((13, 8), (8.6, 11.6), (15.4, 14.4), (11, 17.2)):
        x, y, r = px(col), py(row), 2.25
        z = p.surf(x, y)
        k.smooth(k.ellipsoid("ball", (x, y, z + 0.9), (r, r, r * 0.95), blue, 20, 12), 80)
        ring = [(x + (r + 0.2) * math.cos(a), y + (r + 0.2) * math.sin(a)) for a in
                [2 * math.pi * i / 24 for i in range(24)]]
        p.tube("socket", [(cx, cy, p.surf(cx, cy) + 0.25) for cx, cy in ring], 0.4, socket, 6, closed=True)


def wild_ball():
    """A glossy green ball resting on two blue-grey steel lumps."""
    p.orb(p.RAMP_RED)
    steel = k.material("lump", palette=0x39, metallic=0.6, roughness=0.25)
    green = k.material("wild_ball", palette=0xc8, metallic=0.2, roughness=0.1, emission=(20, 160, 40),
                       emission_strength=0.6)
    for x in (px(6.5), px(17.5)):
        y = py(15.6)
        k.smooth(k.ellipsoid("lump", (x, y, p.surf(x, y) - 0.6), (4.7, 4.4, 3.2), steel, 24, 12), 70)
    x, y = px(12), py(10.2)
    k.smooth(k.ellipsoid("ball", (x, y, p.surf(x, y) + 0.8), (4.6, 4.4, 4.0), green, 28, 16), 80)


def vulcan_rear():
    """Two red flames slanting in towards the bottom, glowing yellow inside."""
    p.orb(p.RAMP_RED)
    red = k.material("flame", palette=0x75, roughness=0.25, emission=(200, 20, 0), emission_strength=1.0)
    core = p.glow("flame_core", (255, 170, 40), 2.6, color=(255, 180, 60))
    for side in (-1, 1):
        x0, y0 = side * (px(18.5) - 0.0), py(10.3)
        x1, y1 = side * (px(14.6)), py(19.6)
        p.pod("flame", x0, y0, x1, y1, 2.3, red, core, lift=0.0)


def heavy_missile_rear():
    """Swept steel wings carrying red launchers, a green body between them."""
    p.orb(p.RAMP_RED)
    dark = k.material("wing_dark", palette=0x31, metallic=0.4, roughness=0.35)
    steel = k.material("wing", palette=0x3a, metallic=0.6, roughness=0.25)
    red = k.material("launcher", palette=0x76, metallic=0.4, roughness=0.25, emission=(200, 20, 0),
                     emission_strength=0.8)
    green = k.material("wing_body", palette=0x26, metallic=0.4, roughness=0.3)
    p.emblem("wings_base", ICON_243, "o02367y", -1.6, 0.8, dark, bevel=0.3, floor=3.0)
    p.emblem("wings", ICON_243, "3", -0.6, 1.6, steel, bevel=0.35, floor=3.0)
    p.emblem("launchers", ICON_243, "67y", -0.6, 2.1, red, bevel=0.35, floor=3.0)
    p.emblem("body", ICON_243, "2", -0.6, 1.8, green, bevel=0.35, floor=3.0)


def mega_pulse_rear():
    """A thick red ring round a dark hollow, swept out to the right like a vortex, with a glowing
    spark in the hollow (the ring's hole is at column 9.8, row 13.5)."""
    p.orb(p.RAMP_RED)
    dark = k.material("ring_dark", palette=0x71, metallic=0.3, roughness=0.35)
    red = k.material("ring", palette=0x76, metallic=0.45, roughness=0.22, emission=(180, 20, 0),
                     emission_strength=0.35)
    heart = p.glow("ring_heart", (255, 180, 50), 3.0, color=(255, 190, 70))
    p.emblem("ring_base", ICON_245, "o7ty", -1.4, 0.7, dark, bevel=0.3)
    p.emblem("ring_tail", ICON_245, "t", -0.6, 1.5, red, bevel=0.45, smoothing=2)
    cx, cy = px(9.8), py(13.5)
    ring = [(cx + 3.4 * math.cos(a), cy + 3.9 * math.sin(a)) for a in [2 * math.pi * i / 48 for i in range(48)]]
    p.tube("ring", [(x, y, p.surf(x, y) + 0.9) for x, y in ring], 1.55, red, 14, closed=True)
    k.smooth(k.ellipsoid("heart", (px(9.2), py(12.4), p.surf(cx, cy) + 0.6), (1.1, 1.1, 0.8), heart, 12, 8), 70)


MODELS = {
    "pu_starburst": (169, starburst),
    "pu_multi_rear": (191, multi_rear),
    "pu_sonic_wave": (193, sonic_wave),
    "pu_protron_rear": (195, protron_rear),
    "pu_wild_ball": (197, wild_ball),
    "pu_vulcan_rear": (199, vulcan_rear),
    "pu_heavy_missile_rear": (243, heavy_missile_rear),
    "pu_mega_pulse_rear": (245, mega_pulse_rear),
}
