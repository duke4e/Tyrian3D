"""Enemies of wave 3, batch N (sheet 3: SURFACE, DESERTRUN and CORE), the machines and ships; modelled
as their sprites look (models.cfg: yaw=0 unless noted). The rock arch and the stepped pyramid are in
wave3_n_rocks.py, CORE's fire in wave3_n_fire.py.

- hatch_bunker (3 18): DESERTRUN's grey bunker in the grey ground, a red-framed hatch on its top; its
  frames (56, 94, 284) slide the hatch's doors open on a grey sensor with a red eye and close them
  again. The model shows it open, the doors drawn back under the frame, the eye glowing.
- lava_bubble (3 128): CORE's glossy dark red bubble of lava on the ground, splashes round its foot
  (its frames 130 and 132 burst it).
- horned_pod (3 1): SURFACE's grey flying pod: a round hull with a belt, a deck across its top
  carrying a tower with a dark visor and two horn-like blades sweeping up the screen.
- plank_turret (3 12): SURFACE's brown turret, a box of planks with two guns; its eight frames are
  headings the level picks, so the model points up the screen (as 3 14) and aims at the player
  (yaw=aim).
- lamp_block_84, lamp_block_86 (3 84, 86) and lamp_block_122, lamp_block_124 (3 122, 124): SURFACE's
  two stone blocks, each drawn in two pieces side by side (origin), with a square relief on top and
  red lamps in slots at one end (glowing).
- hooded_top, hooded_bottom (3 237 above 275): CORE's hooded figure, a grey stone face in a red hood
  and cloak, in two pieces (origin).

usage: Blender -b --factory-startup -P wave3_n.py -- [--only name,name] [--preview <prefix>]
       [--check 1] [--stats 1] [--whole <prefix>]
"""
import math
import os
import sys

from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_n_kit as n  # noqa: E402
from wave3_n_kit import art, k, sh, w, pal, px, py  # noqa: E402


def mask_of(name, width):
    return lambda: n.art_mask(w.grid(getattr(art, name), width))


# --- 3 18: the hatch bunker ----------------------------------------------------------------------

@n.model("hatch_bunker", mask=mask_of("BUNKER", 24))
def hatch_bunker():
    """A grey concrete housing in the grey ground, its south and east sides leaning out; on its top
    a red frame round a deep hatch whose two doors are drawn back under the frame; in the hatch a
    grey sensor dome on a collar, its big red eye glowing."""
    g = w.grid(art.BUNKER_OPEN, 24)
    grey = pal("bunker_grey", 0x05, metallic=0.25, roughness=0.6)
    grey_light = pal("bunker_grey_light", 0x07, metallic=0.25, roughness=0.55)
    grey_dark = pal("bunker_grey_dark", 0x03, metallic=0.25, roughness=0.65)
    red = pal("bunker_red", 0x48, metallic=0.35, roughness=0.4)
    red_light = pal("bunker_red_light", 0x4b, metallic=0.35, roughness=0.35)
    pit = pal("bunker_pit", 0x01, metallic=0.2, roughness=0.7)
    door = pal("bunker_door", 0x02, metallic=0.5, roughness=0.4)
    sensor = pal("bunker_sensor", 0x06, metallic=0.6, roughness=0.3)
    sensor_light = pal("bunker_sensor_light", 0x09, metallic=0.6, roughness=0.25)
    eye = pal("bunker_eye", 0x75, metallic=0.0, roughness=0.15, glow=1.1)
    eye_core = pal("bunker_eye_core", 0x7b, metallic=0.0, roughness=0.1, glow=1.8)

    ground = [(0, pal("bunker_ground3", 0x03, metallic=0.05, roughness=0.85)),
              (4.4, pal("bunker_ground5", 0x05, metallic=0.05, roughness=0.8)),
              (5.6, pal("bunker_ground6", 0x06, metallic=0.05, roughness=0.8)),
              (6.6, pal("bunker_ground7", 0x07, metallic=0.05, roughness=0.75))]

    n.soft_floor("ground", g, ground, lambda v, c, r: v >> 4 == 0, top=0.7, relief=0.5, blur=1)
    # The housing: a block with a hole (the hatch), its edges rounded over wider to the south and east
    # (the light strips the sprite draws there).
    top = 5.2
    outline = [(-10.2, 12.2), (-10.2, -10.6), (10.0, -10.6), (10.0, 12.2)]
    hole = [(-8.0, 10.0), (6.6, 10.0), (6.6, -7.0), (-8.0, -7.0)]

    def lean(x, y, z):
        # The south and east edges fall away over about two pixels.
        fall = max(n.smoothstep(-8.8, -10.6, y), n.smoothstep(8.4, 10.0, x))
        return z - (z - 0.3) * 0.75 * fall
    housing = sh.inflate("housing", [outline, hole], grey, sh.pillow_profile(top - 0.3, 0.9), bottom=0.0,
                         spacing=0.45, rim=0.3, z_fn=lean)
    w.simplify_bottom(housing)
    k.smooth(housing, 40)
    w.paint_faces(housing, lambda c, nrm: grey_light if (nrm.y < -0.35 or nrm.x > 0.35) and nrm.z > 0.2 else
                  grey_dark if (nrm.y > 0.35 or nrm.x < -0.35) and c.z < top - 0.5 and abs(c.x + 0.7) < 7.5 and
                  -7.2 < c.y < 10.2 else None)
    # The hatch: dark walls and floor, the doors drawn back under the frame (north and south).
    w.rounded_box("pit_floor", (-0.7, 1.5, 0.9), (14.4, 16.8, 1.0), pit, bevel=0.3)
    w.rounded_box("door_n", (-0.7, 8.9, top - 1.2), (14.2, 2.6, 0.7), door, bevel=0.25)
    w.rounded_box("door_s", (-0.7, -5.8, top - 1.2), (14.2, 2.8, 0.7), door, bevel=0.25)
    # The red frame round the hatch, its top lighter.
    loop = [(-8.6, 10.6), (7.2, 10.6), (7.2, -7.6), (-8.6, -7.6)]
    pts = []
    for i in range(4):
        a, b = Vector(loop[i]), Vector(loop[(i + 1) % 4])
        for t in range(6):
            p = a + (b - a) * (t / 6)
            pts.append((p.x, p.y, top + 0.2))
    pts.append(pts[0])
    frame = w.tube("frame", pts, 0.85, red, 8, smooth_angle=50, squash=0.9)
    w.paint_faces(frame, lambda c, nrm: red_light if nrm.z > 0.7 else None)
    # The sensor: a collar, a grey dome, the red eye on its top.
    cx, cy = px(11.5), py(12.2)
    w.hoop("collar", (cx, cy, 1.5), [(3.0, -0.2), (4.6, -0.2), (4.8, 0.6), (4.0, 1.0), (3.0, 0.8)], sensor_light, 28)
    for s in (-1, 1):
        w.rounded_box(f"strut{s}", (cx + s * 4.6, cy - 1.6, 2.2), (1.4, 4.4, 2.2), sensor, bevel=0.35)
    w.sphere("dome", (cx, cy, 1.4), (3.9, 3.7, 3.4), sensor, 24, 12)
    w.sphere("eye", (cx, cy + 0.2, 3.4), (2.7, 2.6, 1.7), eye, 24, 12)
    w.sphere("eye_core", (cx - 0.5, cy + 0.6, 4.8), (1.0, 1.0, 0.45), eye_core, 12, 6)


# --- 3 128: the lava bubble ----------------------------------------------------------------------

@n.model("lava_bubble", mask=mask_of("DOME", 24))
def lava_bubble():
    """A glossy dark red bubble of lava standing on the ground, a little lighter towards its east side
    and darker at its foot, a faint glow in it; drops and lumps splashed round its foot, some still
    hot."""
    import random
    g = w.grid(art.DOME, 24)
    skin = pal("bubble_skin", 0x72, metallic=0.1, roughness=0.1, glow=0.15)
    skin_dark = pal("bubble_dark", 0x70, metallic=0.1, roughness=0.2, glow=0.05)
    lump_dark = pal("bubble_lump", 0x72, metallic=0.05, roughness=0.25, glow=0.1)
    lump_hot = pal("bubble_hot", 0x76, metallic=0.0, roughness=0.3, glow=1.0)
    cx, cy, rx, ry = 0.0, 1.6, 11.2, 9.4
    dome = k.ellipsoid("dome", (cx, cy, 0.0), (rx, ry, 9.5), skin, 48, 24)
    sh.flat_bottom([dome])
    k.smooth(dome, 60)
    w.paint_faces(dome, lambda c, nrm: skin_dark if c.z < 1.2 else None)
    # A lip of lava round its foot.
    w.hoop("lip", (cx, cy, 0.0), [(rx - 0.8, 0.0), (rx + 0.6, 0.0), (rx + 0.5, 0.6), (rx - 0.4, 1.1)], skin_dark, 48,
           scale_y=ry / rx)
    # The splashes: a drop at the sprite's pixels outside the dome (one per pixel or two), the bright
    # ones hot.
    rnd = random.Random(128)
    drops = []
    for r in range(len(g)):
        for c in range(24):
            v = g[r][c]
            if v is None:
                continue
            x, y = px(c), py(r)
            if ((x - cx) / (rx + 0.3)) ** 2 + ((y - cy) / (ry + 0.3)) ** 2 < 1.0:
                continue
            if y > cy - 2.0 or any((x - dx) ** 2 + (y - dy) ** 2 < 2.5 ** 2 for dx, dy, _ in drops):
                continue
            drops.append((x, y, v))
    for i, (x, y, v) in enumerate(drops):
        hot = (v & 15) >= 5
        size = rnd.uniform(0.9, 1.35)
        # A splat, flattened, stretched away from the bubble.
        d = Vector((x - cx, y - cy)).normalized()
        drop = w.sphere(f"drop{i}", (0.0, 0.0, 0.0), (size, size * 1.35, size * 0.55), lump_hot if hot else lump_dark,
                        12, 6)
        angle = math.atan2(d.y, d.x) - math.pi / 2
        drop.data.transform(Matrix.Translation((x, y, 0.15)) @ Matrix.Rotation(angle, 4, "Z"))


# --- 3 1: the horned pod -------------------------------------------------------------------------

@n.model("horned_pod", mask=mask_of("CLAW_SHIP", 24))
def horned_pod():
    """A grey flying pod: a round hull with a dark seam down its top and a belt round it; a deck
    across the hull's north side carrying a tower with a dark visor between two horn-like blades that
    sweep up the screen, rising towards their tips."""
    g = w.grid(art.CLAW_SHIP, 24)
    grey = pal("pod_grey", 0x07, metallic=0.65, roughness=0.3)
    grey_light = pal("pod_grey_light", 0x0a, metallic=0.65, roughness=0.25)
    grey_shine = pal("pod_grey_shine", 0x0c, metallic=0.7, roughness=0.2)
    grey_dark = pal("pod_grey_dark", 0x04, metallic=0.6, roughness=0.35)
    seam = pal("pod_seam", 0x12, metallic=0.3, roughness=0.6)
    visor = pal("pod_visor", 0x03, metallic=0.4, roughness=0.15)
    # The hull: a round pod, its seam and belt.
    hx, hy = px(11.5), py(19.8)
    hull = k.ellipsoid("hull", (hx, hy, 0.0), (8.6, 6.4, 6.0), grey, 40, 20)
    k.smooth(hull, 60)
    w.paint_faces(hull, lambda c, nrm: grey_light if nrm.z > 0.55 and nrm.x < 0.1 else
                  grey_dark if nrm.z < -0.3 else None)
    w.tube("hull_seam", [(hx, hy - 6.2, 1.8), (hx, hy - 4.5, 4.6), (hx, hy - 1.0, 5.9), (hx, hy + 3.0, 5.4),
                         (hx, hy + 5.6, 3.2)], 0.35, seam, 8)
    w.hoop("belt", (hx, hy, 0.6), [(8.3, -0.7), (9.1, -0.5), (9.2, 0.5), (8.4, 0.8)], grey_shine, 48,
           scale_y=6.6 / 8.6)
    w.hoop("belt_seam", (hx, hy, 1.4), [(8.0, -0.15), (8.75, -0.15), (8.75, 0.15), (8.0, 0.15)], seam, 48,
           scale_y=6.6 / 8.6)
    # The deck across the hull's north side.
    w.rounded_box("deck", (px(11.5), py(11.2), 3.0), (19.6, 3.8, 3.4), grey, bevel=1.0, segments=3)
    # The tower with its visor.
    w.block("tower", (px(11.5), py(7.8)), 3.0, 5.2, 10.5, grey_light, taper=0.5, rounding=1.2, power=4.0,
            segments=32, z0=1.0)
    w.rounded_box("visor", (px(11.5), py(4.6), 9.2), (4.0, 1.6, 1.6), visor, bevel=0.4)
    w.rounded_box("tower_slot", (px(11.5), py(8.4), 11.3), (1.3, 4.6, 0.7), seam, bevel=0.2)
    # The blades: inflated thin from the sprite's horns, their inner edges and tips raised (curved up
    # like wings), a light stripe along them.
    rows = w.regions(g, lambda v, c, r: "L" if c <= 8 and r <= 12 else "R" if c >= 15 and r <= 12 else ".")
    for label, sign, outer in (("L", -1, -11.0), ("R", 1, 11.0)):
        def curl(x, y, z, s=sign, o=outer):
            inward = abs(x - o)
            return z + 0.55 * inward + 0.32 * max(0.0, y - 1.0) + 1.0
        blade = w.part(f"blade{label}", rows, label, grey, sh.round_profile(0.7, max_height=1.4), bottom=0.8,
                       base=2.0, z_fn=curl, spacing=0.35, smooth_angle=45, grow=-0.25)
        w.paint_faces(blade, lambda c, nrm, s=sign: grey_shine if nrm.z > 0.3 and nrm.x * s < -0.25 else
                      grey_dark if nrm.z < -0.2 else None)


# --- 3 12: the plank turret ----------------------------------------------------------------------

@n.model("plank_turret", mask=None)
def plank_turret():
    """A brown box of planks, two raised lids either side of a groove along its middle, iron bands
    across them; two guns reach up the screen from its north side, their muzzles light. Centred on its
    box (it turns to aim)."""
    wood = pal("turret_wood", 0xa8, metallic=0.05, roughness=0.6)
    wood_light = pal("turret_wood_light", 0xab, metallic=0.05, roughness=0.55)
    wood_dark = pal("turret_wood_dark", 0xa4, metallic=0.05, roughness=0.65)
    plank = pal("turret_plank", 0xa9, metallic=0.05, roughness=0.6)
    groove = pal("turret_groove", 0xa2, metallic=0.1, roughness=0.7)
    iron = pal("turret_iron", 0x03, metallic=0.7, roughness=0.35)
    muzzle = pal("turret_muzzle", 0xaa, metallic=0.4, roughness=0.3)
    bore = pal("turret_bore", 0x01, metallic=0.2, roughness=0.7)
    body = w.block("body", (0.0, 0.0), 6.6, 6.6, 5.0, wood, taper=0.5, rounding=0.8, power=8.0, segments=40)
    w.paint_faces(body, lambda c, nrm: wood_dark if nrm.y < -0.4 else wood_light if nrm.y > 0.4 else None)
    for s in (-1, 1):
        lid = w.block(f"lid{s}", (s * 3.15, -0.2), 2.6, 5.6, 1.2, wood, rounding=0.5, power=6.0, segments=28, z0=4.6)
        # Planks: alternate faces a shade lighter.
        w.paint_faces(lid, lambda c, nrm: plank if nrm.z > 0.8 and int((c.x + 20) / 1.3) % 2 == 0 else None)
        for y in (-3.6, 3.2):
            w.rounded_box(f"band{s}{y}", (s * 3.15, y, 5.75), (5.4, 0.8, 0.5), iron, bevel=0.2)
    w.rounded_box("groove", (0.0, -0.2, 4.95), (1.2, 11.0, 0.6), groove, bevel=0.2)
    # The guns.
    for s in (-1, 1):
        x = s * 4.0
        w.lathe_axis(f"gun{s}", [(0.0, 1.5), (5.0, 1.4), (5.3, 1.55), (6.2, 1.55), (6.3, 0.01)], wood_dark,
                     (x, 5.6, 3.0), (0, 1, 0.05), 16)
        w.lathe_axis(f"muzzle{s}", [(5.2, 1.62), (6.4, 1.62), (6.5, 0.01)], muzzle, (x, 5.6, 3.0), (0, 1, 0.05), 16)
        w.lathe_axis(f"bore{s}", [(6.4, 0.8), (6.6, 0.01)], bore, (x, 5.6, 3.0), (0, 1, 0.05), 12)
        w.rounded_box(f"mount{s}", (x, 6.0, 2.6), (3.8, 1.6, 3.6), iron, bevel=0.4)


# --- 3 84/86 and 3 122/124: the lamp blocks ------------------------------------------------------

BLOCK_ORIGIN = (24, 14)


def lamp_block(art_text, lamps, square, ribs, prefix):
    """A stone block (one of SURFACE's two, each drawn from two sprites side by side): its top face a
    little domed, its sides and its wide south face leaning as the sprite draws them, a notch under its
    south edge; on its top a square relief (a raised frame round a raised panel) between two ribs, and
    at one end two red lamps glowing in dark slots. lamps: [(column, first row, last row)], square:
    (c0, c1, r0, r1) of its frame, ribs: [(column, first row, last row)] (pixels of the art)."""
    g = w.grid(art_text, 48)
    stone = pal(f"{prefix}_stone", 0xa8, metallic=0.05, roughness=0.7)
    stone_light = pal(f"{prefix}_stone_light", 0xaa, metallic=0.05, roughness=0.65)
    stone_side = pal(f"{prefix}_stone_side", 0xa5, metallic=0.05, roughness=0.75)
    stone_front = pal(f"{prefix}_stone_front", 0xa4, metallic=0.05, roughness=0.8)
    groove = pal(f"{prefix}_groove", 0xa2, metallic=0.05, roughness=0.85)
    slot = pal(f"{prefix}_slot", 0xa1, metallic=0.1, roughness=0.7)
    lamp = pal(f"{prefix}_lamp", 0x75, metallic=0.0, roughness=0.2, glow=1.2)
    lamp_hot = pal(f"{prefix}_lamp_hot", 0x78, metallic=0.0, roughness=0.2, glow=1.8)
    ox, oy = BLOCK_ORIGIN
    height, front_row, bottom_row = 8.0, 16.5, 23.5
    rows = w.regions(g, lambda v, c, r: "#")
    polys = sh.outlines(rows, "#", BLOCK_ORIGIN, smooth=2, epsilon=0.35, min_area=1.0)

    def front(x, y, z):
        row = oy - y
        if row > front_row:  # the south face leans out down to the foot
            t = (row - front_row) / (bottom_row - front_row)
            z = min(z, height - (height - 0.6) * t ** 1.2)
        return z
    body = sh.inflate("body", polys, stone, sh.pillow_profile(height - 0.3, 2.6, crown=0.5), bottom=0.0, spacing=0.45,
                      rim=0.3, z_fn=front)
    w.simplify_bottom(body)
    k.smooth(body, 35)
    w.paint_faces(body, lambda c, nrm: stone_front if nrm.y < -0.45 and nrm.z < 0.85 else
                  stone_side if abs(nrm.x) > 0.4 and nrm.z < 0.85 else
                  stone_light if nrm.z > 0.97 and c.z > height else None)

    def on_top(x, y, lift=0.0):
        return sh.surface_z(body, x, y, height) + lift
    # The square relief: a groove round a raised frame round a raised panel.
    c0, c1, r0, r1 = square
    x0, x1, y0, y1 = c0 - ox, c1 + 1 - ox, oy - r1 - 1, oy - r0
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    z = on_top(cx, cy)
    w.rounded_box("square_groove", (cx, cy, z - 0.25), (x1 - x0 + 0.6, y1 - y0 + 0.6, 0.6), groove, bevel=0.2)
    for name, (bx, by, sx, sy) in {"n": (cx, y1 - 0.9, x1 - x0, 1.6), "s": (cx, y0 + 0.9, x1 - x0, 1.6),
                                   "w": (x0 + 0.9, cy, 1.6, y1 - y0), "e": (x1 - 0.9, cy, 1.6, y1 - y0)}.items():
        w.rounded_box(f"square_{name}", (bx, by, z + 0.3), (sx, sy, 1.4), stone_light, bevel=0.4)
    w.rounded_box("panel", (cx, cy, z + 0.2), (x1 - x0 - 5.0, y1 - y0 - 5.0, 1.6), stone, bevel=0.5)
    # The ribs.
    for c, ra, rb in ribs:
        x = c + 0.5 - ox
        pts = [(x, oy - r - 0.5, on_top(x, oy - r - 0.5, 0.15)) for r in (ra, (ra + rb) / 2, rb)]
        w.tube(f"rib{c}", pts, 0.55, stone_light, 8, squash=0.8)
    # The lamps in their slots.
    for i, (c, ra, rb) in enumerate(lamps):
        x = c + 1.0 - ox
        ya, yb = oy - ra - 0.2, oy - rb - 0.8
        za, zb = on_top(x, ya), on_top(x, yb)
        w.tube(f"slot{i}", [(x, ya, za - 0.2), (x, yb, zb - 0.2)], 1.25, slot, 12, squash=0.6)
        w.tube(f"lamp{i}", [(x, ya - 0.5, za + 0.25), (x, yb + 0.5, zb + 0.25)], 0.8, lamp, 12)
        w.sphere(f"lamp_hot{i}", (x - 0.2, ya - 1.2, za + 0.8), (0.45, 0.8, 0.3), lamp_hot, 8, 4)


def block_piece(name, art_name, sprite, side):
    """One sprite of a lamp block: side -1 is the left (its sprite centre at x = -12), 1 the right."""
    x0, x1 = (-24.0, 0.0) if side < 0 else (0.0, 24.0)

    def mask():
        c0 = 0 if side < 0 else 24
        return n.art_mask(w.grid(getattr(art, art_name), 48), (c0, c0 + 24, 0, 28))
    return (f"{name}_{sprite}", (x0, x1, -14.0, 14.0), (side * 12.0, 0.0), mask)


n.pieced("lamp_block_a", lambda: lamp_block(art.BLOCK_A, [(8, 10, 16), (12, 6, 15)], (22, 33, 5, 15),
                                            [(18, 4, 15), (35, 5, 15)], "block_a"), (48, 28),
         [block_piece("lamp_block", "BLOCK_A", 84, -1), block_piece("lamp_block", "BLOCK_A", 86, 1)])
n.pieced("lamp_block_b", lambda: lamp_block(art.BLOCK_B, [(35, 6, 15), (39, 9, 16)], (15, 26, 5, 15),
                                            [(13, 4, 15), (29, 5, 15)], "block_b"), (48, 28),
         [block_piece("lamp_block", "BLOCK_B", 122, -1), block_piece("lamp_block", "BLOCK_B", 124, 1)])


# --- 3 237 above 275: the hooded figure ----------------------------------------------------------

HOOD_ORIGIN = (12, 28)


def hooded_whole():
    """CORE's hooded figure lying on the ground as the sprites draw it, 24 x 56: a cloak of red cloth
    over the whole, its folds raised where the sprite's red is light and sunk where it is dark, and
    out of it a smooth grey stone head in the hood and a grey face strip below it, the highest part."""
    g = w.grid(art.HOOD, 24)
    ox, oy = HOOD_ORIGIN
    red_px = lambda v: v is not None and v >> 4 == 7  # noqa: E731
    grey_px = lambda v: v is not None and v >> 4 == 0  # noqa: E731
    any_px = lambda v: v is not None  # noqa: E731
    red_fine = w.sampler(g, HOOD_ORIGIN, value=lambda v: v & 15, blur=1, keep=red_px)
    grey_fine = w.sampler(g, HOOD_ORIGIN, value=lambda v: v & 15, blur=1, keep=grey_px)
    fine = w.sampler(g, HOOD_ORIGIN, value=lambda v: v & 15, blur=1, keep=any_px)
    coarse = w.sampler(g, HOOD_ORIGIN, value=lambda v: v & 15, blur=4, keep=any_px)

    redness = w.sampler(g, HOOD_ORIGIN, value=lambda v: 1.0 if v >> 4 == 7 else 0.0, blur=1, keep=any_px)
    darkness = w.sampler(g, HOOD_ORIGIN, value=lambda v: 1.0 if v >> 4 == 0 and (v & 15) <= 2 else 0.0, blur=1,
                         keep=any_px)

    def ramp_at(x, y):
        return 7 if redness(x, y) >= 0.5 else 0

    def cloak_z(x, y, z):
        return z + 0.5 * (fine(x, y) - coarse(x, y))
    rows = w.regions(g, lambda v, c, r: "#")
    cloak = w.part("cloak", rows, "#", pal("hood_red", 0x74, metallic=0.0, roughness=0.6),
                   sh.pillow_profile(5.0, 3.0, crown=1.2), origin=HOOD_ORIGIN, bottom=0.0, z_fn=cloak_z, spacing=0.4,
                   smooth_angle=50)
    reds = [(s - 1.5 if s > 1 else 0, pal(f"hood_red{s:x}", 0x70 + s, metallic=0.0, roughness=0.55,
                                          glow=0.12 if s >= 7 else None)) for s in range(1, 11)]
    shadow = pal("hood_shadow", 0x01, metallic=0.0, roughness=0.9)
    greys = [(s - 0.5 if s > 0 else 0, pal(f"hood_grey{s:x}", s, metallic=0.1, roughness=0.5)) for s in range(1, 11)]

    def paint(c, nrm):
        if nrm.z < -0.5:
            return reds[0][1]
        if ramp_at(c.x, c.y) == 0:
            shade = grey_fine(c.x, c.y)
            if darkness(c.x, c.y) > 0.55 and c.y < -1.0:  # the black of the cloak's folds
                return shadow
            return greys[n.band_index(shade - (1.5 if nrm.z < 0.4 else 0), greys)][1]
        return reds[n.band_index(red_fine(c.x, c.y) - (1.5 if nrm.z < 0.4 else 0), reds)][1]
    w.paint_faces(cloak, paint)
    # The head in the hood and the face strip: the grey pixels of the upper part, raised on the cloak.
    head_rows = w.regions(g, lambda v, c, r: "h" if v >> 4 == 0 and (v & 15) >= 3 and r <= 29 else ".")

    def head_z(x, y, z):
        return z + 0.35 * (grey_fine(x, y) - 6.0)
    head = w.part("head", head_rows, "h", greys[6][1], sh.round_profile(0.8, max_height=6.0), origin=HOOD_ORIGIN,
                  bottom=0.0, base=4.2, z_fn=head_z, spacing=0.35, smooth_angle=55, min_area=6.0)
    w.paint_faces(head, lambda c, nrm: greys[n.band_index(grey_fine(c.x, c.y) + (1.0 if nrm.z > 0.6 else -1.0),
                                                          greys)][1])


def hooded_piece(name, sprite, top):
    y0, y1 = (0.0, 28.0) if top else (-28.0, 0.0)

    def mask():
        return n.art_mask(w.grid(art.HOOD, 24), (0, 24, 0, 28) if top else (0, 24, 28, 56))
    return (name, (-12.0, 12.0, y0, y1), (0.0, 14.0 if top else -14.0), mask)


n.pieced("hooded", hooded_whole, (24, 56), [hooded_piece("hooded_top", 237, True),
                                           hooded_piece("hooded_bottom", 275, False)])


n.run()
