"""Batch O of wave 3 (sheet K, FLEET and STATION), the grey machines; modelled as their sprites look
(models.cfg: yaw=0). The fire column, the WARNING sign and the sparks are in wave3_o.py.

The sheet builds its machines from a few shared parts, and so do the models: a grey armoured helmet
with a grille, a glowing red core ball held between two side sleeves over a cradle, a crossbar with a
red lamp on two long legs, and a slotted block with legs or clawed fins under it.

- pincer_core_top, pincer_core_legs (K 153 above K 191): the machine that sits between the pincer's two
  arms (pincer_*, wave1_d.py) in FLEET and STATION: the helmet with its grille, the red core in its
  sleeves (the arms' gun tubes plug into the sleeves, at the same height), the cradle and a glowing
  neck down to the crossbar with its lamp and its two long legs. Built whole and cut in two (origin).
  Its frames heat the core (153-159) and flash the lamp (191, 193): both glow.
- k_pod (K 276): the round grey pod: two helmets back to back round a belt with a glowing slot.
- k_turret (K 281): the red core ball on its sleeves, its glowing neck pointing up the screen like a
  barrel, on a slotted grey block (the frames launch its shots; the ball glows).
- k_clawblock (K 283): the slotted grey block on two grey claws with glowing red strips down their
  inner sides, the claws hooking inwards at their feet.
- k_lampgun (K 278): the crossbar with its lamp (lit) on two short legs pointing up the screen, on a
  block with tan windows and a salmon grille (the gun that drops K 171's red bombs).

usage: Blender -b --factory-startup -P wave3_o_machines.py -- [--only name,name] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1] [--whole pincer_core --preview <prefix>]
"""
import math
import os
import sys

from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_o_kit as o  # noqa: E402
from wave3_o_kit import art, k, sh, pal  # noqa: E402

CORE_ORIGIN = (12, 28)  # the machine's art (K 153 above K 191) is 24 x 56
SPRITE = (12, 14)


def mats():
    return {
        "steel": pal("kmach_steel", 0x09, metallic=0.55, roughness=0.32),
        "steel_light": pal("kmach_steel_light", 0x0b, metallic=0.6, roughness=0.28),
        "steel_bright": pal("kmach_steel_bright", 0x0d, metallic=0.6, roughness=0.25),
        "steel_dark": pal("kmach_steel_dark", 0x06, metallic=0.5, roughness=0.42),
        "seam": pal("kmach_seam", 0x02, metallic=0.3, roughness=0.6),
        "core": pal("kmach_core", 0x74, metallic=0.3, roughness=0.1, glow=0.45),
        "neck": pal("kmach_neck", 0x76, metallic=0.2, roughness=0.3, glow=0.7),
        "lamp": pal("kmach_lamp", 0x77, metallic=0.1, roughness=0.25, glow=0.8),
        "lamp_hot": pal("kmach_lamp_hot", 0x78, metallic=0.05, roughness=0.2, glow=0.9),
        "red_dark": pal("kmach_red_dark", 0x72, metallic=0.4, roughness=0.4),
        "blue": pal("kmach_blue", 0x34, metallic=0.3, roughness=0.25, glow=0.35),
    }


def paint_grey(obj, g, origin, m, min_nz=0.75, dark=2):
    """Paints the seams of a grey part: the faces facing up over the sprite's dark lines inside it (dark
    grey pixels with pixels all round them, not its outline); the rest keeps the part's material."""
    ox, oy = origin

    def seam(c, n):
        if n.z <= min_nz:
            return None
        col, row = int(math.floor(c.x + ox)), int(math.floor(oy - c.y))
        v = o.at(g, col, row)
        if v is None or v >> 4 != 0 or v & 15 > dark:
            return None
        around = [o.at(g, col + dc, row + dr) for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1))]
        if any(a is None for a in around):
            return None
        # A line: at least one dark neighbour.
        if not any(a >> 4 == 0 and a & 15 <= dark for a in around):
            return None
        return m["seam"]
    o.paint_faces(obj, seam)
    return obj


def grey_rows(g, keep):
    """Char rows: '#' for the grey pixels keep(column, row) accepts."""
    return o.char_rows(g, lambda v, c, r: "#" if v >> 4 == 0 and keep(c, r) else ".")


# --- Shared parts --------------------------------------------------------------------------------

def helmet(g, origin, r0, r1, m, height=5.6, grille=True, prefix="helmet", rail_rows=(5, 12)):
    """The armoured helmet: the grey pixels of rows r0..r1 inflated to a slab with rounded edges and
    shoulders, a recess with three ribs (the grille) in its middle (columns 9-15, rows 7-12 of the
    machine's art: given in the art's own rows) and a raised rail down each side (columns 2-4 and
    19-21, rows rail_rows)."""
    rows = grey_rows(g, lambda c, r: r0 <= r <= r1)
    ox, oy = origin
    gx0, gx1 = 9 - ox, 16 - ox
    gy0, gy1 = oy - 12.8, oy - 7.0  # rows 7-12 (the art's rows are those of the machine's top)

    def recess(x, y, z):
        if not grille:
            return z
        inside = min(o.smoothstep(gx0 - 0.4, gx0 + 0.3, x), o.smoothstep(gx1 + 0.4, gx1 - 0.3, x),
                     o.smoothstep(gy0 - 0.4, gy0 + 0.3, y), o.smoothstep(gy1 + 0.4, gy1 - 0.3, y))
        return z - 1.7 * inside

    body = o.part(prefix, rows, "#", m["steel"], sh.pillow_profile(height, 2.0, crown=0.5), origin=origin,
                  bottom=0.55, smooth=2, epsilon=0.45, spacing=0.45, z_fn=recess, rim=0.1)
    paint_grey(body, g, origin, m)
    parts = [body]
    ya, yb = origin[1] - rail_rows[1] - 0.6, origin[1] - rail_rows[0] - 0.2
    for side, x in ((-1, -8.4), (1, 8.6)):
        rail = o.rounded_box(f"{prefix}_rail{side}", (x, (ya + yb) / 2, height - 0.2), (2.6, yb - ya, 1.4),
                             m["steel_light"], bevel=0.5, segments=2)
        parts.append(rail)
    if grille:
        top = height + 0.1
        for i, cx in enumerate((gx0 + 1.5, gx0 + 3.5, gx0 + 5.5)):
            parts.append(o.rounded_box(f"{prefix}_rib{i}", (cx, (gy0 + gy1) / 2, top - 1.3),
                                       (0.95, gy1 - gy0 - 0.5, 1.6), m["steel_light"], bevel=0.3))
    return parts


def core_unit(m, neck_end=-1.0):
    """In the machine's coordinates (CORE_ORIGIN): the red core ball between the two side sleeves, the
    collar round it, the cradle's two arms under it and the glowing neck down to the crossbar (to y =
    neck_end)."""
    axis_y = 10.0  # the sleeves' axis: the pincer's gun tubes reach in here, at z = 0
    parts = [o.sphere("core", (0.5, axis_y, 0.9), (5.6, 5.5, 5.3), m["core"], 32, 16)]
    parts.append(o.hoop("core_collar", (0.5, axis_y, 1.2), [(5.45, -0.5), (6.1, -0.2), (6.15, 0.35), (5.6, 0.55)],
                        m["steel_dark"], 40, scale_y=1.0))
    # The sleeves: collars at both ends, ribs between.
    sleeve = [(0.0, 3.9), (0.25, 4.7), (1.5, 4.75), (1.8, 4.45), (3.0, 4.45), (3.2, 4.6), (3.8, 4.6), (4.0, 4.45),
              (5.3, 4.45), (5.55, 4.9), (6.7, 4.9), (6.95, 4.2)]
    parts.append(o.lathe_axis("sleeve_l", sleeve, m["steel"], (-12.2, axis_y, 0.0), (1, 0, 0), 28))
    parts.append(o.lathe_axis("sleeve_r", sleeve, m["steel"], (12.2, axis_y, 0.0), (-1, 0, 0), 28))
    for side, x in ((-1, -12.2), (1, 12.2)):
        parts.append(o.lathe_axis(f"sleeve_bore{side}", [(-0.05, 3.3), (0.05, 3.3), (0.06, 0.01)], m["seam"],
                                  (x, axis_y, 0.0), (-side, 0, 0), 24))
    # The cradle's arms, converging from under the sleeves to the crossbar's collar.
    for side, (x0, x1) in ((-1, (-5.6, -3.0)), (1, (6.6, 4.2))):
        parts.append(o.tube(f"cradle{side}", [(x0, 6.0, 0.2), (x0 + 0.35 * (x1 - x0), 3.2, 0.5), (x1, 0.6, 0.6)],
                            [1.35, 1.25, 1.2], m["steel_light"], 14, squash=0.9))
    # The neck: a glowing pipe from the core down into the crossbar, in a steel sleeve at its top.
    length = 5.2 - neck_end
    parts.append(o.lathe_axis("neck", [(0.0, 1.35), (length - 0.4, 1.35), (length, 1.1)], m["neck"], (0.5, 5.2, 0.6),
                              (0, -1, 0), 16))
    parts.append(o.lathe_axis("neck_ring", [(0.0, 1.55), (0.25, 1.85), (1.1, 1.85), (1.35, 1.55)], m["steel_dark"],
                              (0.5, 4.6, 0.6), (0, -1, 0), 18))
    return parts


def crossbar(g, origin, m, leg_end=-18.6, hot=False, lamp_scale=1.0):
    """In the machine's coordinates: the crossbar (the grey pixels of rows 28-37) with the red lamp in a
    recess in its middle, and two long round legs from its ends down the screen to small feet."""
    rows = grey_rows(g, lambda c, r: 28 <= r <= 37 and not (r >= 36 and 4 <= c <= 19))
    lamp_c = (1.0, -6.0)

    def recess(x, y, z):
        inside = min(o.smoothstep(-2.6, -1.8, x), o.smoothstep(4.6, 3.8, x), o.smoothstep(-9.6, -8.8, y),
                     o.smoothstep(-2.4, -3.2, y))
        return z - 1.3 * inside

    beam = o.part("crossbar", rows, "#", m["steel"], sh.pillow_profile(3.6, 1.6, crown=0.4), origin=origin,
                  base=-1.6, bottom=0.5, smooth=2, epsilon=0.45, spacing=0.45, z_fn=recess, rim=0.1)
    parts = [beam]
    parts.append(o.sphere("lamp", (lamp_c[0], lamp_c[1], 0.9), (2.3 * lamp_scale, 2.6 * lamp_scale, 1.7),
                          m["lamp_hot" if hot else "lamp"], 24, 12))
    for side, x in ((-1, -9.5), (1, 9.6)):
        top = (x, -1.2, 0.4)
        parts.append(o.rounded_box(f"leg_top{side}", (x - side * 0.2, -5.5, 0.6), (3.4, 8.4, 3.6), m["steel_light"],
                                   bevel=0.9, segments=3))
        path = [top, (x, -9.5, -0.2), (x + side * 0.15, leg_end + 2.6, -1.0), (x + side * 0.2, leg_end + 1.0, -1.3)]
        parts.append(o.tube(f"leg{side}", path, [1.2, 1.05, 0.95, 0.9], m["steel"], 12))
        parts.append(o.lathe_axis(f"knee{side}", [(0.0, 1.15), (0.2, 1.45), (0.9, 1.45), (1.1, 1.15)], m["steel_light"],
                                  (x, -10.0, -0.25), (0, -1, 0), 16))
        parts.append(o.sphere(f"foot{side}", (x + side * 0.2, leg_end + 0.9, -1.3), (1.35, 1.1, 1.0),
                              m["steel_bright"], 14, 8))
    return parts


def slot_block(g, origin, m, style="slot", prefix="block"):
    """In K 283's coordinates: the grey block of rows 0-13, rounded at the top, a dark seam along its
    bottom (row 13). style "slot": a window slot across its middle (rows 7-9) between framed side
    panels and two small blue studs on its shoulders; "tan" (K 278): tan-framed windows at its sides and
    a salmon grille down its middle instead."""
    rows = grey_rows(g, lambda c, r: r <= 13)

    def recess(x, y, z):
        if style == "slot":
            inside = min(o.smoothstep(-4.4, -3.6, x), o.smoothstep(4.4, 3.6, x), o.smoothstep(3.6, 4.3, y),
                         o.smoothstep(7.3, 6.6, y))
            return z - 1.3 * inside
        inside = min(o.smoothstep(-3.4, -2.6, x), o.smoothstep(4.4, 3.6, x), o.smoothstep(-0.5, 0.3, y),
                     o.smoothstep(13.2, 12.4, y))
        return z - 1.1 * inside

    body = o.part(prefix, rows, "#", m["steel"], sh.pillow_profile(5.2, 2.2, crown=0.5), origin=origin,
                  bottom=0.4, smooth=2, epsilon=0.45, spacing=0.45, z_fn=recess, rim=0.1)
    parts = [body]
    if style == "slot":
        paint_grey(body, g, origin, m)
        parts.append(o.rounded_box(f"{prefix}_slot", (0.0, 5.5, 4.35), (7.6, 2.6, 0.8), m["seam"], bevel=0.3))
        for side in (-1, 1):
            parts.append(o.rounded_box(f"{prefix}_panel{side}", (side * 8.5, 5.5, 4.9), (3.2, 8.2, 1.2),
                                       m["steel_light"], bevel=0.45))
            parts.append(o.sphere(f"{prefix}_stud{side}", (side * 7.5, 10.4, 4.2), (0.8, 0.8, 0.6), m["blue"], 10, 5))
    else:
        tan = pal("kmach_tan", 0x1b, metallic=0.45, roughness=0.35)
        tan_dark = pal("kmach_tan_dark", 0x18, metallic=0.4, roughness=0.45)
        salmon = pal("kmach_salmon", 0x46, metallic=0.35, roughness=0.35)
        for side in (-1, 1):
            for cy in (3.0, 8.0):
                frame = [(side * 8.5 - 1.6, cy - 2.0), (side * 8.5 + 1.6, cy - 2.0), (side * 8.5 + 1.6, cy + 2.0),
                         (side * 8.5 - 1.6, cy + 2.0)]
                hole = sh.inset(frame, 1.0)
                parts.append(o.k.smooth(sh.inflate(f"{prefix}_window{side}{cy}", [frame, hole], tan,
                                                   sh.pillow_profile(0.8, 0.35), base=4.6, bottom=0.0,
                                                   spacing=0.3), 45))
                parts.append(o.rounded_box(f"{prefix}_pane{side}{cy}", (side * 8.5, cy, 4.9), (1.6, 2.2, 0.6),
                                           tan_dark, bevel=0.2))
        for x in (-1.5, 2.5):
            parts.append(o.rounded_box(f"{prefix}_bar{x}", (x, 7.4, 4.0), (1.3, 10.8, 1.4), salmon, bevel=0.4))
        parts.append(o.rounded_box(f"{prefix}_spine", (0.5, 7.0, 3.6), (1.0, 11.0, 0.9), m["steel_light"], bevel=0.3))
    return parts


def claws(g, origin, m):
    """In K 283's coordinates: the two grey claws under the block (rows 14-27), hooking inwards at their
    feet, with glowing red strips down their inner sides (columns 7-9 and 13-15)."""
    red = pal("kmach_strip", 0x77, metallic=0.2, roughness=0.3, glow=0.9)
    red_dim = pal("kmach_strip_dim", 0x71, metallic=0.4, roughness=0.4)
    parts = []
    for side in ("l", "r"):
        keep = (lambda c, r: r >= 14 and c <= 8) if side == "l" else (lambda c, r: r >= 14 and c >= 15)
        rows = grey_rows(g, keep)
        claw = o.part(f"claw_{side}", rows, "#", m["steel"], sh.pillow_profile(4.4, 1.6, crown=0.4), origin=origin,
                      base=-0.4, bottom=0.4, smooth=2, epsilon=0.4, spacing=0.4, rim=0.1)
        parts.append(claw)
        # The red strips: a dark red panel set lower against the claw's inner side, two glowing bars on it.
        strip_rows = o.char_rows(g, lambda v, c, r: "r" if 14 <= r <= 24 and (6 <= c <= 10 if side == "l" else
                                                                              13 <= c <= 17) else ".")
        parts.append(o.part(f"strip_{side}", strip_rows, "r", red_dim, sh.pillow_profile(2.2, 0.8), origin=origin,
                            base=-0.4, bottom=0.3, smooth=1, epsilon=0.3, spacing=0.4, rim=0.1))
        for i, c in enumerate((7, 9) if side == "l" else (13, 15)):
            x = c + 0.5 - origin[0]
            parts.append(o.tube(f"strip_bar_{side}{i}", [(x, -0.6, 1.9), (x, -10.4, 1.9)], 0.5, red, 10,
                                squash=0.8))
    return parts


# --- K 153 above K 191: the pincer's core machine ---------------------------------------------------

@o.whole("pincer_core", (24, 56))
def pincer_core_whole():
    g = o.grid(art.CORE, 24)
    m = mats()
    parts = []
    # The cap at the top, on the helmet's crown.
    parts.append(o.block("cap", (0.5, 26.3), 6.3, 1.6, 4.9, m["steel_light"], rounding=0.9, power=4.0, z0=0.4))
    parts.append(o.rounded_box("cap_seam", (0.5, 24.7, 3.4), (11.4, 0.8, 2.6), m["seam"], bevel=0.25))
    parts += helmet(g, CORE_ORIGIN, 3, 12, m)
    parts += core_unit(m)
    parts += crossbar(g, CORE_ORIGIN, m)
    return parts


CORE_PIECES = [("pincer_core_top", 153, (0.0, 28.0), 14.0), ("pincer_core_legs", 191, (-28.0, 0.0), -14.0)]


def core_piece(box, cy):
    objects = pincer_core_whole()
    o.cut(objects, (-12.5, 12.5, box[0], box[1]), (0.0, cy))
    o.budget()


for _name, _sprite, _box, _cy in CORE_PIECES:
    o.model(_name, [(_sprite, True)])(lambda box=_box, cy=_cy: core_piece(box, cy))


# --- K 276: the round pod --------------------------------------------------------------------------

@o.model("k_pod", [(276, True)])
def k_pod():
    """Two helmets back to back (the machine's top, mirrored), a dark belt round their seam with a
    glowing slot in its middle, and two small lugs at each end where the machine has its cap."""
    g = o.grid(art.K276, 24)
    m = mats()
    helmet(g, SPRITE, 2, 12, m, height=5.4, prefix="top", rail_rows=(5, 13))
    bottom = helmet(g, SPRITE, 2, 12, m, height=5.4, prefix="bottom", rail_rows=(5, 13))
    o.mirror_y(bottom)
    belt = [(-11.4, -1.4), (11.4, -1.4), (11.4, 1.4), (-11.4, 1.4)]
    o.k.smooth(sh.inflate("belt", [belt], m["steel_dark"], sh.pillow_profile(3.4, 1.0), base=0.0, bottom=0.55,
                          spacing=0.4), 45)
    o.rounded_box("slot_frame", (0.5, 0.0, 3.6), (8.6, 3.6, 1.2), m["steel_light"], bevel=0.4)
    o.sphere("slot_light", (0.5, 0.0, 4.0), (3.6, 1.6, 0.9), m["lamp"], 20, 10)
    for sy in (1, -1):
        for x in (-4.5, 5.5):
            o.rounded_box(f"lug{sy}{x}", (x, sy * 12.7, 2.4), (2.6, 2.4, 2.2), m["steel_light"], bevel=0.6)
    o.budget()


# --- K 281: the turret -------------------------------------------------------------------------------

@o.model("k_turret", [(281, True)])
def k_turret():
    """The core ball on its sleeves (the machine's, upside down: the glowing neck points up the screen
    like a barrel), set on the slotted block (K 283's, upside down)."""
    m = mats()
    unit = core_unit(m, neck_end=0.8)
    # The machine's y to K 281's: y' = 14 - y (rows 27..14 of the machine are rows 0..13 here).
    o.mirror_y(unit, 7.0)
    o.move(unit, dz=1.6)
    barrel_tip = o.lathe_axis("muzzle", [(0.0, 1.25), (0.6, 1.5), (1.3, 1.5), (1.5, 1.1), (1.55, 0.01)],
                              m["lamp"], (0.5, 12.4, 2.2), (0, 1, 0), 16)
    g = o.grid(art.K283, 24)
    base = slot_block(g, SPRITE, m, prefix="base")
    o.mirror_y(base)
    o.move(base, dz=-0.8)
    o.budget()


# --- K 283: the clawed block -------------------------------------------------------------------------

@o.model("k_clawblock", [(283, True)])
def k_clawblock():
    g = o.grid(art.K283, 24)
    m = mats()
    slot_block(g, SPRITE, m)
    claws(g, SPRITE, m)
    o.budget()


# --- K 278: the lamp gun -----------------------------------------------------------------------------

@o.model("k_lampgun", [(278, True)])
def k_lampgun():
    """The machine's crossbar with its lamp lit, its legs short and pointing up the screen (the machine's
    y mirrored: y' = -y), on K 283's block upside down with tan windows and a salmon grille."""
    m = mats()
    core = o.grid(art.CORE_HOT, 24)
    bar = crossbar(core, CORE_ORIGIN, m, leg_end=-13.6, hot=True, lamp_scale=1.35)
    o.mirror_y(bar)
    o.move(bar, dz=1.2)
    g = o.grid(art.K283, 24)
    base = slot_block(g, SPRITE, m, style="tan", prefix="base")
    o.mirror_y(base)
    o.budget(4300)


if __name__ == "__main__":
    o.run()
