"""Enemies of wave 3, batch Z (sheet L): MINERS's ore tug and the red ore boulder it tows, modelled as their sprites
look (models.cfg: yaw=0). The kit is wave3_z_kit.py, the pixels wave3_z_art.py; the rest of the sheet is in
wave3_z_small.py, wave3_z_rock.py, wave3_z_train.py and wave3_z_station.py.

MINERS puts the tug and its load together from eight enemies, again and again (enemies 1162-1169, all on the
ground layers): the tug's halves (L 131 left, 93 right) side by side, below them the tow ring (L 95) and the hook
(L 114), and below those the boulder's four quarters (L 17 169 above 55 207). The tug is 48 x 28 pixels, the
boulder 48 x 56, the ring and the hook 12 x 14 each, the whole 48 x 84; most events set the boulder and the hook
two pixels to the right of the tug and the ring, the first ones exactly under them (as built here).

- miners_tug_l, miners_tug_r (L 131, 93): a tan wing hovering over the ground between two ribbed brown fuel
  tanks with blue thruster bells at their ends, a glossy black canopy on its middle, its tail ending in a grey
  hitch whose pin goes down through the tow ring. Built whole, cut into its two halves (origin).
- miners_tow_ring (L 95): the steel ring lying flat on the hitch's pin.
- miners_tow_hook (L 114): two chain links from the ring to a grapple whose two arms bite into the boulder.
- miners_ore_tl, miners_ore_tr, miners_ore_bl, miners_ore_br (L 17, 169, 55, 207): the lumpy red ore boulder
  on the ground, its knobs where the sprite draws them lit. Built whole, cut into its quarters (origin).

All are drawn at their own origin, their heights in one frame (the ground at z = 0): the tug flies with its
wing at z = 12, so that it, the ring, the hook and the boulder's top meet.

usage: Blender -b --factory-startup -P wave3_z.py -- [--only name,name] [--preview <prefix>] [--check 1]
       [--stats 1] [--whole <prefix>] [--assembly <prefix>]
"""
import math
import os
import sys

from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_z_kit as kit  # noqa: E402
from wave3_z_kit import k, sh, w, pal  # noqa: E402

TUG = kit.frame("TUG", 48, (24, 14))
ORE = kit.frame("ORE", 48, (24, 28))
RING = kit.frame("RING", 12, (6, 7))
HOOK = kit.frame("HOOK", 12, (6, 7))

# Where each part's origin lies in the whole (48 x 84, its centre the origin).
TUG_AT, RING_AT, HOOK_AT, ORE_AT = (0.0, 28.0), (0.0, 12.0), (0.0, 2.0), (0.0, -14.0)
WING_Z = 15.0     # the tug's wing (and its tanks' axes)
RING_Z = 13.4     # the ring's middle
ROCK_TOP = 15.0   # the boulder's highest point


# --- The tug (L 131, 93) ---------------------------------------------------------------------------

def tug_whole():
    f = TUG
    X, Y = f.X, f.Y
    tan = kit.Painter("tug", shades={0xa: (3, 5, 6, 7, 8, 9, 10, 11)}, metallic=0.35, roughness=0.45,
                      remap={0x10: 0xa3, 0x12: 0xa3, 0x14: 0xa4})
    brown = [(s_, pal(f"tug_tank_{s_:x}", 0x10 + s_, metallic=0.45, roughness=0.4)) for s_ in (2, 3, 4, 5, 6, 7, 8, 9)]
    rib = pal("tug_rib", 0x13, metallic=0.5, roughness=0.45)
    blue = pal("tug_blue", 0xd4, metallic=0.5, roughness=0.35)
    blue_lit = pal("tug_blue_lit", 0xd6, metallic=0.5, roughness=0.3)
    blue_dark = pal("tug_blue_dark", 0x33, metallic=0.4, roughness=0.45)
    glow = pal("tug_thrust", 0xd9, metallic=0.0, roughness=0.5, glow=0.9)
    black = pal("tug_canopy", 0x02, metallic=0.35, roughness=0.12)
    glint = pal("tug_canopy_glint", 0x08, metallic=0.3, roughness=0.1)
    steel = pal("tug_hitch", 0x0a, metallic=0.7, roughness=0.25)
    steel_dark = pal("tug_hitch_dark", 0x06, metallic=0.6, roughness=0.35)

    # The wing: the tan pixels between the tanks and down the tail (and under the canopy), a plate with
    # rounded edges, thicker in the middle; its upper edge (towards the top of the screen) a little higher.
    def wing_keep(v, c, r):
        return 9 <= c <= 38 and r <= 22 and v >> 4 in (0xa, 0x0, 0xf, 0x1)
    polys = kit.polys_of(f, wing_keep, smooth=2, epsilon=0.3)
    yc = Y(9.0)

    def wing_z(x, y, z):
        return z + 0.10 * (y - yc) + 1.2 * math.exp(-(x / 7.0) ** 2)
    wing = sh.inflate("wing", polys, tan(0xa6), sh.pillow_profile(2.0, 2.6, crown=0.8), bottom=0.55, base=WING_Z - 0.8,
                      rim=0.3, spacing=0.5, z_fn=wing_z, sigma=1.2)
    k.smooth(wing, 45)
    # Painted by the sprite's tan, its outline and the canopy's pixels taking the tan next to them.
    paint = kit.frame("TUG", 48, (24, 14)).fill({v for row in f.g for v in row if v is not None and v >> 4 != 0xa},
                                                 edge_only=False)
    kit.pixelate(wing, paint)
    kit.paint_sprite(wing, paint, tan, wall_steps=2, under=tan(0xa3), blur=2)
    kit.paint_faces(wing, lambda c, nrm: tan(0xa4) if -0.5 <= nrm.z < 0.45 else None)
    kit.merge_flat(wing)
    wing.data.validate()

    # The canopy: a glossy black teardrop on the wing's middle, widest a third of the way down, pointed at
    # the tail (rows 1-15, columns 20-27).
    rings_ = []
    top_y, tip_y = f.top(1) + 0.2, f.bottom(15)
    length = top_y - tip_y
    for i in range(1, 24):
        t = i / 24
        y = top_y - t * length
        width = 4.1 * (math.sin(math.pi * min(1.0, t / 0.36) / 2) if t < 0.36 else
                       (1 - ((t - 0.36) / 0.64) ** 1.6) ** 0.8)
        width = max(width, 0.25)
        zc = WING_Z + 2.2 - 0.06 * (y - Y(7))
        rings_.append(k.ring(y, width, width * 0.9, 28, z=zc, top=1.0, bottom=0.5))
    canopy = k.loft("canopy", rings_, black, start_point=(0, top_y, WING_Z + 2.4), end_point=(0, tip_y, WING_Z + 1.9))
    k.smooth(canopy, 60)
    kit.paint_faces(canopy, lambda c, nrm: glint if (nrm.z > 0.82 and -1.4 < c.x < 0.2 and c.y > Y(11)) else None)

    # The tanks: ribbed brown cylinders along y, rounded at the top end, the blue thruster bells at the
    # bottom (rows 19-26), their mouths glowing.
    for side, col in (("l", 5.5), ("r", 41.5)):
        x = X(col)
        start = (x, f.top(0), WING_Z)
        tank = w.lathe_axis(f"tank_{side}", [(0.0, 0.01), (0.25, 1.9), (0.8, 3.0), (1.7, 3.75), (2.6, 3.95),
                                             (17.0, 3.95), (18.6, 3.7), (19.2, 3.0)], brown[4][1], start, (0, -1, 0),
                            28, smooth_angle=50)
        def tank_shade(px_, py_, x0=x):
            # The sprite's tank shades across (light on the left), in ramps 1 and b alike.
            v = f.at(px_, py_)
            return (v & 15) if v is not None and v >> 4 in (1, 0xb) else 5
        kit.paint_faces(tank, lambda c, nrm, x0=x: (brown[0][1] if nrm.z < -0.3 else
                                                   kit.nearest_band(brown, tank_shade(c.x, c.y) - (1.5 if nrm.z < 0.35 else 0))))
        for t in (4.6, 8.6, 12.6, 16.4):
            w.lathe_axis(f"tank_rib_{side}{t:.0f}", [(t - 0.45, 3.9), (t - 0.3, 4.3), (t + 0.3, 4.3), (t + 0.45, 3.9)],
                         rib, (x, f.top(0), WING_Z), (0, -1, 0), 28)
        # The collar and the bell.
        w.lathe_axis(f"collar_{side}", [(18.8, 3.4), (19.0, 3.6), (20.0, 3.6), (20.2, 2.6)], blue_dark, start,
                     (0, -1, 0), 24)
        bell = w.lathe_axis(f"bell_{side}", [(19.9, 2.4), (20.6, 2.2), (21.6, 2.9), (23.0, 4.2), (24.6, 4.85),
                                             (26.6, 5.0), (27.0, 4.7), (26.9, 3.9), (26.0, 3.2)], blue, start,
                            (0, -1, 0), 28)
        kit.paint_faces(bell, lambda c, nrm: blue_lit if (nrm.z > 0.55 and nrm.x < 0.3) else blue_dark if nrm.z < -0.2
                        else None)
        w.lathe_axis(f"bell_glow_{side}", [(25.6, 3.3), (25.7, 0.01)], glow, start, (0, -1, 0), 20)

    # The hitch at the tail's end (rows 23-26): a grey lug, its pin going down through the ring.
    w.lathe_axis("hitch", [(0.0, 1.5), (0.4, 1.7), (3.6, 1.6), (4.6, 1.2)], steel, (0.0, f.top(23) + 0.4, WING_Z - 0.3),
                 (0, -1, 0), 16)
    pin_y = -13.5
    w.sphere("hitch_knob", (0.0, pin_y, WING_Z - 0.4), (1.5, 1.3, 1.3), steel, 14, 7)
    w.column("hitch_pin", [(RING_Z - 2.0, 0.6), (RING_Z - 1.6, 0.85), (WING_Z - 0.6, 0.85), (WING_Z - 0.2, 0.7)],
             steel_dark, 0.0, pin_y, 14)


kit.pieced("miners_tug", tug_whole, (48, 28), [kit.quarter("miners_tug_l", TUG, 0, 0),
                                               kit.quarter("miners_tug_r", TUG, 24, 0)])


# --- The tow ring (L 95) and the hook (L 114) -------------------------------------------------------

def tow_ring():
    steel = pal("ring_steel", 0x0b, metallic=0.75, roughness=0.22)
    ring = kit.torus("ring", (0.0, 0.0, RING_Z), 4.45, 1.3, steel, 40, 12, squash=0.8)
    return ring


kit.model("miners_tow_ring", mask=lambda: RING.mask(), size=(12, 14))(tow_ring)


def hook_parts():
    """The hook in its sprite's coordinates (centre at whole (0, 2)): the chain from the ring's near side
    (whole y 7) to the grapple biting into the boulder's top."""
    steel = pal("hook_steel", 0x0b, metallic=0.75, roughness=0.22)
    steel_dark = pal("hook_steel_dark", 0x08, metallic=0.7, roughness=0.3)
    tip = pal("hook_tip", 0x8b, metallic=0.6, roughness=0.25)
    f = HOOK
    X, Y = f.X, f.Y
    # Link 1 stands upright through the ring's tube (rows 0-3), link 2 lies flat (rows 4-7).
    link1 = kit.torus("link1", (0.0, 0.0, 0.0), 1.45, 0.75, steel, 20, 8)
    link1.data.transform(Matrix.Rotation(math.radians(90), 4, "Y"))
    kit.move([link1], X(5.5), Y(1.6), RING_Z)
    kit.torus("link2", (X(5.5), Y(5.2), RING_Z - 0.1), 1.2, 0.72, steel, 20, 8, scale_y=1.45)
    # The grapple: a shank down from link 2 to a crown, a bar across it arched up in the middle, its two arms
    # bending down at the ends into the boulder, their tips turned in (rows 8-13).
    w.tube("shank", [(X(5.5), Y(6.8), RING_Z - 0.1), (X(5.5), Y(9.6), RING_Z + 0.3)], 0.95, steel, 12)
    w.sphere("crown", (X(5.5), Y(9.8), RING_Z + 0.3), (1.9, 1.4, 1.3), steel_dark, 16, 8)
    for side in (-1, 1):
        path = w.catmull([(X(5.5), Y(10.0), RING_Z + 0.3), (X(5.5) + side * 2.5, Y(10.1), RING_Z + 0.5),
                          (X(5.5) + side * 4.3, Y(10.8), RING_Z - 0.2), (X(5.5) + side * 4.6, Y(11.9), RING_Z - 1.3),
                          (X(5.5) + side * 3.6, Y(12.9), RING_Z - 2.2)], 0.35)
        w.tube(f"arm{side}", path, 0.9, steel, 10)
        kit.cone(f"tip{side}", tuple(path[-1]), (-side * 0.35, -0.35, -1.0), 2.0, 0.9, tip, segments=10)


kit.model("miners_tow_hook", mask=lambda: HOOK.mask(), size=(12, 14))(hook_parts)


# --- The ore boulder (L 17, 169, 55, 207) -----------------------------------------------------------

def ore_whole():
    f = ORE
    polys = kit.polys_of(f, lambda v, c, r: True, smooth=2, epsilon=0.3)
    # Knobs: the sprite's shades less their wide blur (the light from the upper left left out).
    is_rock = lambda v: v >> 4 == 4
    fine = kit.field(f, lambda v: (v & 15) if is_rock(v) else 2.0, lambda v: True, blur=2)
    wide = kit.field(f, lambda v: (v & 15) if is_rock(v) else 2.0, lambda v: True, blur=6)
    knob = kit.field_sampler(f, fine - wide)
    shade = kit.field_sampler(f, kit.field(f, lambda v: (v & 15) if is_rock(v) else 2.5, lambda v: True, blur=1))
    height = ROCK_TOP - 2.6

    def z_of(x, y, e):
        # A dome rising over the 9 pixels inside the outline, its top a little lower towards the bottom of the
        # screen (the boulder leans back), the knobs up to 2.4 pixels out of it.
        dome = 1.0 + height * e * (0.92 + 0.08 * max(-1.0, min(1.0, (y - 0.0) / 20.0)))
        return dome + 0.75 * knob(x, y) * min(1.0, 0.35 + e)
    rock = kit.heightfield("ore", polys, z_of, None, spacing=0.5, smooth_angle=55, edge=14.0)
    reds = kit.bands("ore", 4, (2, 3, 4, 5, 6, 7, 8, 9, 10, 11), metallic=0.15, roughness=0.6)
    kit.paint_by(rock, lambda x, y: shade(x, y) + 0.5 * knob(x, y) + 0.3, reds, wall_drop=1.0)
    kit.jitter(rock, 0.12, seed=4, scale=1.4, min_z=0.6)


kit.pieced("miners_ore", ore_whole, (48, 56), [kit.quarter("miners_ore_tl", ORE, 0, 0),
                                               kit.quarter("miners_ore_tr", ORE, 24, 0),
                                               kit.quarter("miners_ore_bl", ORE, 0, 28),
                                               kit.quarter("miners_ore_br", ORE, 24, 28)])

kit.assembly("miners_tow", (48, 84), [(tug_whole, TUG_AT), (tow_ring, RING_AT), (hook_parts, HOOK_AT),
                                      (ore_whole, ORE_AT)])


if __name__ == "__main__":
    kit.run()
