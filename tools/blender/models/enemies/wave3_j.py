"""Enemies of wave 3, batch J (sheet D, the asteroid levels), the machines; modelled as their sprites
look (models.cfg: yaw=0). The rocks and the stone face are in wave3_j_rocks.py.

- cage_turret (D 275): AST. CITY's tan machine on the tiled floor: a lattice of tan bars over dark
  steel windows with a lens, steel pipes to red lamps at both sides and a gun pointing down the
  screen with a red muzzle (its frames light the lamps and the muzzle: they glow).
- red_furnace (D 267): the red housing on the tiled floor with a glowing element in a deep well inside
  a raised rim, steel knobs in dark side slots and red rails clamped to its sides (its frames heat the
  element up: it glows).
- eye_tub (D 193): the bronze tub on the tiled floor, its iris open on a glowing red eye with a red
  light on its front (the frames open the iris from shut to the eye, 169; the model shows it open).
- dome_cannon_barrel, dome_cannon_dome (D 245 above D 283): the brown dome on the tiled floor with a
  red band of lights and a heavy dark cannon reaching up the screen from its ribbed bronze collar,
  in two pieces (origin); the dome's lights flash (281): they glow.
- vent_dome (D 241): the grey armoured block on the tiled floor, reaching in from the top of its
  sprite, a red-hot crescent vent under its rounded front (the frames 239, 243 brighten it: it glows).
- shell_ship (D 157): the ship of two dark curved shells round a red eye (its frames close the shells;
  the model shows them open).
- medallion_red (D 117): the red winged medallion with an orange gem, D 79's red relative.
- bronze_beetle (D 16): the bronze beetle with red wing cases and green hooked legs.

The ground machines stand on a low slab of the tiled floor the sprites draw round them (wave3_j_kit.floor).

usage: Blender -b --factory-startup -P wave3_j.py -- [--only name,name] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1] [--whole dome_cannon --preview <prefix>]
"""
import math
import os
import sys

from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_j_kit as w  # noqa: E402
from wave3_j_kit import art, k, sh, pal, px, py, model, whole  # noqa: E402

D = "enemy_D"


# --- D 275: the cage turret ----------------------------------------------------------------------

@model("cage_turret", [(D, 275, True)])
def cage_turret():
    """A tan armoured body whose top is a lattice of raised bars over dark steel windows (a lens in
    the lower middle one), steel pipes out to red lamps at both sides, a tan stub with two steel
    knobs at the back and a tan gun pointing down the screen, its muzzle glowing red."""
    g = w.grid(art.D275, 24)
    tan = pal("cage_tan", 0xa8, metallic=0.55, roughness=0.35)
    tan_light = pal("cage_tan_light", 0xab, metallic=0.55, roughness=0.3)
    tan_dark = pal("cage_tan_dark", 0xa4, metallic=0.5, roughness=0.45)
    steel = pal("cage_steel", 0x63, metallic=0.6, roughness=0.35)
    steel_light = pal("cage_steel_light", 0x69, metallic=0.7, roughness=0.2)
    lens = pal("cage_lens", 0x6c, metallic=0.4, roughness=0.08, glow=0.25)
    lamp = pal("cage_lamp", 0x75, metallic=0.1, roughness=0.3, glow=1.1)
    muzzle = pal("cage_muzzle", 0x76, metallic=0.0, roughness=0.3, glow=1.4)

    w.floor("floor", g, w.floor_bands("cage"), lambda v, c, r: v >> 4 == 0)
    top = 6.0  # the body's top (the windows); the bars stand on it
    # The body: a rounded block under the lattice, tan sides, its top the dark steel of the windows.
    body = w.block("body", (-0.5, 4.4), 8.9, 8.1, top, tan, taper=0.7, rounding=1.0, power=5.0, segments=36)
    w.paint_faces(body, lambda c, n: steel if n.z > 0.6 else tan_dark if c.z < 1.6 else None)

    def bar(name, c0, c1, r0, r1, height=1.5):
        """A tan bar of the lattice over pixel columns c0..c1 and rows r0..r1 (edges)."""
        x0, x1, y0, y1 = c0 - 12, c1 - 12, 14 - r1, 14 - r0
        b = w.rounded_box(name, ((x0 + x1) / 2, (y0 + y1) / 2, top + height / 2 - 0.3), (x1 - x0, y1 - y0, height + 0.6),
                          tan, bevel=0.45, segments=2)
        sh.apply_modifiers(b)
        return w.paint_faces(b, lambda c, n: tan_light if n.z > 0.8 else None)

    bar("bar_top", 3.4, 19.6, 2.2, 4.8, 1.7)
    bar("bar_bottom", 3.4, 19.6, 15.6, 17.4, 1.5)
    bar("bar_left", 3.2, 5.2, 3.0, 17.0, 1.5)
    bar("bar_right", 17.8, 19.8, 3.0, 17.0, 1.5)
    bar("bar_inner_left", 7.0, 9.0, 3.5, 16.5, 1.9)
    bar("bar_inner_right", 13.8, 15.8, 3.5, 16.5, 1.9)
    bar("bar_middle", 8.5, 14.3, 8.7, 10.7, 1.6)
    # The lens in the lower middle window and a slot in the upper one.
    w.hoop("lens_ring", (px(11.0), py(13.3), top), [(1.5, 0.0), (2.4, -0.5), (2.5, 0.4), (2.0, 0.85)], steel_light, 24)
    w.sphere("lens", (px(11.0), py(13.3), top + 0.7), (1.6, 1.6, 0.9), lens, 16, 8)
    w.rounded_box("slot", (px(11.0), py(7.2), top + 0.15), (4.0, 1.2, 0.6), steel_light, bevel=0.25)
    # The steel pipes out to the lamps, through the side windows.
    for side in (-1, 1):
        x_in, x_out = px(11.0) + side * 5.0, px(11.0) + side * 10.2
        w.tube(f"pipe{side}", [(x_in, py(9.8), top - 0.4), (x_out, py(9.8), top - 2.2)], 1.05, steel_light, 12)
        w.sphere(f"pipe_ball{side}", (px(11.0) + side * 6.0, py(9.8), top + 0.2), (0.95, 0.95, 0.9), steel_light, 12, 6)
    # The lamps: red capsules standing along the sides.
    for side, x in ((-1, px(1.6)), (1, px(21.4))):
        w.tube(f"lamp{side}", [(x, py(7.3), 3.6), (x, py(13.0), 3.6)], 1.75, lamp, 14, squash=1.15)
        w.lathe_axis(f"lamp_cap{side}", [(0.0, 1.9), (0.5, 2.1), (1.0, 1.9)], steel, (x, py(6.4), 3.6), (0, -1, 0), 14)
        w.lathe_axis(f"lamp_capb{side}", [(0.0, 1.9), (0.5, 2.1), (1.0, 1.9)], steel, (x, py(13.6), 3.6), (0, 1, 0), 14)
    # At the back: a tan stub into the floor, two steel knobs beside it.
    w.tube("stub", [(px(11.0), py(3.0), top - 1.4), (px(11.0), py(0.6), top - 2.6), (px(11.0), py(-0.4), 0.4)], 1.5,
           tan, 14)
    for x in (px(7.6), px(15.6)):
        w.sphere(f"knob{x}", (x, py(0.8), 1.6), (1.3, 1.1, 1.3), steel_light, 14, 8)
    # At the front: a steel neck and the gun pointing down the screen, its muzzle glowing.
    w.lathe_axis("neck", [(0.0, 2.1), (1.0, 2.3), (2.6, 1.9), (3.2, 2.2)], steel_light, (px(11.0), py(17.0), 3.4),
                 (0, -1, 0), 20)
    gun = [(0.0, 2.8), (0.4, 3.2), (4.0, 3.0), (4.4, 3.3), (6.2, 3.3), (6.6, 2.9), (6.7, 2.2), (6.75, 0.01)]
    w.lathe_axis("gun", k.profile(gun, 0.4), tan, (px(11.0), py(19.6), 3.4), (0, -1, 0.18), 24, squash=0.95)
    w.lathe_axis("muzzle", [(6.4, 2.45), (6.8, 2.2), (6.95, 1.4), (7.0, 0.01)], muzzle, (px(11.0), py(19.6), 3.4),
                 (0, -1, 0.18), 20, squash=0.95)


# --- D 267: the red furnace ----------------------------------------------------------------------

def rounded_rect(x0, x1, y0, y1, radius, count=10):
    """A rectangle with rounded corners as a polygon (counter-clockwise)."""
    pts = []
    for cx, cy, a0 in ((x1 - radius, y1 - radius, 0), (x0 + radius, y1 - radius, 90), (x0 + radius, y0 + radius, 180),
                       (x1 - radius, y0 + radius, 270)):
        for i in range(count + 1):
            a = math.radians(a0 + 90 * i / count)
            pts.append((cx + radius * math.cos(a), cy + radius * math.sin(a)))
    return pts


@model("red_furnace", [(D, 267, True)])
def red_furnace():
    """A red housing with rounded edges on the tiled floor: a deep well down its middle with a
    glowing element in it, a raised rim round the well, dark slots at both sides with steel knobs,
    and red rails clamped to its sides."""
    g = w.grid(art.D267, 24)
    red = pal("furnace_red", 0x47, metallic=0.45, roughness=0.35)
    red_light = pal("furnace_red_light", 0x4b, metallic=0.45, roughness=0.3)
    red_dark = pal("furnace_red_dark", 0x43, metallic=0.4, roughness=0.45)
    pit = pal("furnace_pit", 0x71, metallic=0.1, roughness=0.6, glow=0.5)
    core = pal("furnace_core", 0x77, metallic=0.0, roughness=0.4, glow=1.2)
    slot = pal("furnace_slot", 0x10, metallic=0.3, roughness=0.5)
    knob = pal("furnace_knob", 0x0b, metallic=0.75, roughness=0.2)
    bolt = pal("furnace_bolt", 0x17, metallic=0.6, roughness=0.35)

    w.floor("floor", g, w.floor_bands("furnace"), lambda v, c, r: v >> 4 == 0)
    height = 7.2
    outline = rounded_rect(-10.0, 7.0, -12.0, 14.0, 3.0)
    well = rounded_rect(-4.0, 1.0, -5.0, 9.0, 1.0, 4)
    slots = [rounded_rect(-9.0, -6.0, -3.0, 7.0, 1.0, 4), rounded_rect(3.0, 6.0, -3.0, 7.0, 1.0, 4)]
    housing = sh.inflate("housing", [outline, well] + slots, red, sh.pillow_profile(height, 2.2, crown=0.4),
                         bottom=0.0, spacing=0.7, rim=0.3)
    w.simplify_bottom(housing)
    w.decimate(housing, 1600)
    k.smooth(housing, 60)
    # The well: its floor glows, the element along it glows hotter.
    w.rounded_box("well_floor", (-1.5, 2.0, 1.2), (5.4, 14.4, 1.6), pit, bevel=0.3)
    w.tube("element", [(-2.0, 8.0, 2.4), (-2.0, -4.0, 2.4)], 0.75, core, 12)
    for y in (8.4, -4.4):
        w.rounded_box(f"element_post{y}", (-2.0, y, 2.0), (1.6, 1.0, 2.2), red_dark, bevel=0.3)
    # The raised rim round the well.
    rim = rounded_rect(px(6.6), px(13.4), py(19.6), py(2.6), 2.2, 4)
    loop = [(x, y, height + 0.35) for x, y in rim]
    loop = [p for p in w.catmull(loop + loop[:3], 0.6)]
    w.tube("well_rim", loop[:-6], 0.95, red_light, 10, squash=0.8)
    # The slots: dark floors, two steel knobs each.
    for x in (-7.5, 4.5):
        w.rounded_box(f"slot_floor{x}", (x, 2.0, 1.0), (3.4, 10.4, 1.4), slot, bevel=0.3)
        for y in (5.0, -1.0):
            w.sphere(f"knob{x}{y}", (x, y, 2.6), (1.25, 1.25, 1.4), knob, 16, 8)
    # The rails clamped to the sides.
    for x, xin in ((px(0.9), -9.6), (px(19.6), 6.6)):
        w.tube(f"rail{x}", [(x, py(6.0), 2.6), (x, py(17.6), 2.6)], 1.2, red, 12)
        for y in (py(7.3), py(16.0)):
            w.tube(f"clamp{x}{y}", [(x, y, 2.6), (xin, y, 3.4)], 0.55, bolt, 8)


# --- D 193: the eye tub --------------------------------------------------------------------------

@model("eye_tub", [(D, 193, True)])
def eye_tub():
    """A bronze tub of staves with two dark bands and a rolled rim, standing on the tiled floor; its
    iris is open (four grey petals drawn back against the rim) on a glowing red eye, and a red
    light burns on its front."""
    g = w.grid(art.D169, 24)
    cx, cy = -0.5, 3.4
    bronze = pal("tub_bronze", 0x15, metallic=0.55, roughness=0.4)
    stave = pal("tub_stave", 0x13, metallic=0.5, roughness=0.45)
    rim_mat = pal("tub_rim", 0x19, metallic=0.6, roughness=0.3)
    band = pal("tub_band", 0x11, metallic=0.7, roughness=0.35)
    inside = pal("tub_inside", 0x01, metallic=0.3, roughness=0.6)
    petal = pal("tub_petal", 0x06, metallic=0.7, roughness=0.3)
    eye = pal("tub_eye", 0x77, metallic=0.0, roughness=0.2, glow=1.2)
    core = pal("tub_eye_core", 0x7b, metallic=0.0, roughness=0.2, glow=1.8)
    light = pal("tub_light", 0x74, metallic=0.0, roughness=0.3, glow=1.0)

    def on_tub(c, r):
        return ((c + 0.5 - 12 - cx) / 11.2) ** 2 + ((14 - r - 0.5 - cy) / 13.0) ** 2 < 1.0 and r < 24
    w.floor("floor", g, w.floor_bands("tub"), lambda v, c, r: v >> 4 == 0 and not on_tub(c, r))
    height = 8.4
    # The tub: up the outside, over the rolled rim, down the inside to a floor.
    profile = [(0.0, 10.2), (2.0, 10.6), (4.2, 10.8), (6.4, 10.6), (7.9, 10.3), (8.3, 10.0), (height, 9.4),
               (height - 0.2, 8.9), (height - 0.8, 8.7), (3.2, 8.5), (3.0, 0.01)]
    tub = w.column("tub", profile, bronze, cx, cy, segments=48, smooth_angle=40)
    # The staves: every third face round the outside darker (the planks' seams).
    w.paint_faces(tub, lambda c, n: inside if n.z > 0.5 and c.z < 3.5 else
                  stave if (n.z < 0.5 and int((math.degrees(math.atan2(c.y - cy, c.x - cx)) + 360) / 7.5) % 3 == 0
                            and math.hypot(c.x - cx, c.y - cy) > 9.6) else None)
    w.hoop("rim", (cx, cy, height - 0.35), [(9.3, -0.2), (10.0, -0.6), (10.7, -0.3), (10.8, 0.1), (10.2, 0.45),
                                             (9.5, 0.3)], rim_mat, 48)
    for z in (2.0, 6.0):
        w.hoop(f"band{z}", (cx, cy, z), [(10.5, -0.45), (11.0, -0.35), (11.05, 0.35), (10.5, 0.45)], band, 48)
    # The iris drawn back: four grey petals leaning against the inside of the rim.
    for i in range(4):
        a = math.radians(45 + 90 * i)
        d = Vector((math.cos(a), math.sin(a), 0.0))
        side = Vector((-d.y, d.x, 0.0))
        base = Vector((cx, cy, height - 3.4)) + d * 6.4
        top = Vector((cx, cy, height - 0.3)) + d * 8.6
        tip = Vector((cx, cy, height - 2.2)) + d * 4.6
        verts = [base - side * 3.2, base + side * 3.2, top + side * 3.6, top - side * 3.6, tip]
        p = k.mesh_object(f"petal{i}", verts, [(0, 1, 2, 3), (1, 0, 4)], petal)
        mod = p.modifiers.new("solid", "SOLIDIFY")
        mod.thickness = 0.5
        k.smooth(p, 30)
    # The eye, glowing, its hot middle; the red light on the front.
    w.sphere("eye", (cx - 0.3, cy + 1.4, 4.6), (3.7, 3.7, 3.0), eye, 24, 12)
    w.sphere("eye_core", (cx - 0.3, cy + 1.4, 7.2), (1.6, 1.6, 0.7), core, 16, 6)
    w.rounded_box("front_light", (cx - 0.5, cy - 10.75, 3.9), (5.2, 1.0, 2.4), light, bevel=0.35)


# --- D 245 above D 283: the dome cannon ----------------------------------------------------------

@whole("dome_cannon", (24, 56))
def dome_cannon_whole():
    """A brown dome on the tiled floor: its north half ribbed bronze, a red band across it with two
    lights in a tan frame, a seam down its south side; from its top a heavy dark cannon reaches up
    the screen through a grey, a tan and a red collar, its muzzle open. Built whole (the floor of
    both sprites included) and cut in two at y = 0."""
    g = w.grid(art.TOWER, 24)
    origin = (12, 28)
    brown = pal("cannon_brown", 0x14, metallic=0.5, roughness=0.4)
    rib_light = pal("cannon_rib", 0x18, metallic=0.55, roughness=0.35)
    rib_dark = pal("cannon_rib_dark", 0x15, metallic=0.5, roughness=0.4)
    seam = pal("cannon_seam", 0x1a, metallic=0.6, roughness=0.3)
    red = pal("cannon_red", 0x46, metallic=0.4, roughness=0.35)
    lamp = pal("cannon_lamp", 0x4c, metallic=0.1, roughness=0.2, glow=0.9)
    tan = pal("cannon_tan", 0xa4, metallic=0.5, roughness=0.4)
    black = pal("cannon_black", 0x02, metallic=0.75, roughness=0.25)
    grey = pal("cannon_grey", 0x09, metallic=0.7, roughness=0.3)
    bore = pal("cannon_bore", 0x01, metallic=0.2, roughness=0.7)

    def on_object(c, r):
        return (3 <= c <= 18 and r <= 19) or ((c - 10.5) / 10.5) ** 2 + ((r - 32.0) / 13.0) ** 2 < 1.0
    w.floor("floor", g, w.floor_bands("cannon"), lambda v, c, r: v >> 4 == 0 and not on_object(c, r), origin=origin)
    # The dome.
    dcx, dcy = -1.5, -4.6
    dome = k.ellipsoid("dome", (dcx, dcy, 0.0), (9.8, 12.2, 9.0), brown, 40, 20)
    sh.flat_bottom([dome])
    k.smooth(dome, 50)

    def paint(c, n):
        if n.z < -0.5:
            return None
        if -3.8 < c.y < 0.4:
            return red
        if c.y >= 0.4:
            return rib_light if int((c.x - dcx + 20.0) / 1.6) % 2 == 0 else rib_dark
        return None
    w.paint_faces(dome, paint)
    # The lights on the band, in a tan frame, and the seam down the south side.
    for y in (-1.0, -5.4):
        z = sh.surface_z(dome, -1.8, y, 8.0)
        w.rounded_box(f"lamp_frame{y}", (-1.8, y, z - 0.4), (4.6, 3.2, 1.6), tan, bevel=0.4)
        w.sphere(f"lamp{y}", (-1.8, y, z + 0.3), (1.8, 1.25, 0.8), lamp, 16, 8)
    path = [(-1.5, y, sh.surface_z(dome, -1.5, y, 4.0) + 0.05) for y in (-8.0, -10.5, -13.0, -15.0, -16.2)]
    w.tube("seam", path, 0.5, seam, 8)
    # The cannon.
    start, direction = Vector((-1.2, 4.5, 5.6)), Vector((0.0, 1.0, 0.12))
    w.lathe_axis("cannon_neck", [(0.0, 4.2), (6.0, 4.4), (6.2, 4.6)], black, start, direction, 32)
    w.lathe_axis("collar_grey", [(5.6, 4.9), (5.9, 5.5), (7.6, 5.5), (7.9, 5.0)], grey, start, direction, 32)
    w.lathe_axis("collar_tan", [(7.8, 5.0), (8.0, 5.3), (8.9, 5.3), (9.1, 5.0)], tan, start, direction, 32)
    w.lathe_axis("collar_red", [(9.0, 5.0), (9.2, 5.4), (10.1, 5.4), (10.3, 5.0)], red, start, direction, 32)
    barrel = [(10.0, 5.2), (10.4, 5.7), (19.6, 5.7), (20.6, 5.5), (21.2, 5.0), (21.3, 4.0), (20.4, 3.4), (20.3, 0.01)]
    w.lathe_axis("barrel", barrel, black, start, direction, 32, smooth_angle=40)
    w.lathe_axis("bore", [(20.0, 3.45), (20.45, 3.45), (20.5, 0.01)], bore, start, direction, 24)


def dome_cannon_piece(y0, y1):
    dome_cannon_whole()
    w.bake()
    w.piece(w.meshes(), -12, 12, y0, y1)


model("dome_cannon_barrel", [(D, 245, True)])(lambda: dome_cannon_piece(0, 28))
model("dome_cannon_dome", [(D, 283, True)])(lambda: dome_cannon_piece(-28, 0))


# --- D 241: the vent dome ------------------------------------------------------------------------

@model("vent_dome", [(D, 241, True)])
def vent_dome():
    """A grey armoured block reaching in from the top of the sprite, its south end rounded, panel
    seams across and along it, and a red-hot crescent vent under its rounded front."""
    g = w.grid(art.D241, 24)
    grey = pal("vent_grey", 0x09, metallic=0.6, roughness=0.3)
    grey_light = pal("vent_grey_light", 0x0b, metallic=0.6, roughness=0.25)
    seam_mat = pal("vent_seam", 0x06, metallic=0.5, roughness=0.4)
    hot = pal("vent_hot", 0x73, metallic=0.0, roughness=0.4, glow=1.0)
    hotter = pal("vent_hotter", 0x76, metallic=0.0, roughness=0.3, glow=1.5)
    cx, cy, half, r_end = -1.0, 2.5, 8.0, 4.6

    def on_dome(c, r):
        x, y = c + 0.5 - 12, 14 - r - 0.5
        return abs(x - cx) < half + 0.6 and (y > cy or ((x - cx) / (half + 0.6)) ** 2 + ((y - cy) / (r_end + 0.6)) ** 2 < 1)
    w.floor("floor", g, w.floor_bands("vent"), lambda v, c, r: v >> 4 == 0 and not on_dome(c, r))
    outline = [(cx + half, 18.0), (cx - half, 18.0)]
    for i in range(25):
        a = math.radians(180 + 180 * i / 24)
        outline.append((cx + half * math.cos(a), cy + r_end * math.sin(a)))

    def grooves(x, y, z):
        d = 0.0
        d += math.exp(-((y - 7.5) / 0.35) ** 2)
        if y > 7.5:
            d += math.exp(-((x + 4.5) / 0.35) ** 2) + math.exp(-((x - 3.5) / 0.35) ** 2)
        else:
            d += math.exp(-((x + 2.5) / 0.3) ** 2) + math.exp(-((x + 0.5) / 0.3) ** 2)
        return z - 0.55 * min(1.0, d) * min(1.0, max(0.0, z - 1.5) / 2.0)
    block = sh.inflate("block", [outline], grey, sh.pillow_profile(7.0, 3.2, crown=0.8), bottom=0.0, spacing=0.45,
                       z_fn=grooves)
    w.simplify_bottom(block)
    sh.cut_planes([block], [((0, 14.0, 0), (0, 1, 0))])
    w.decimate(block, 2200)
    k.smooth(block, 50)
    w.paint_faces(block, lambda c, n: seam_mat if n.z > 0.2 and (abs(c.y - 7.5) < 0.45 or
                  (c.y > 7.5 and min(abs(c.x + 4.5), abs(c.x - 3.5)) < 0.45) or
                  (c.y < 7.5 and min(abs(c.x + 2.5), abs(c.x + 0.5)) < 0.4)) and c.z > 2.5 else
                  grey_light if n.z > 0.85 and c.z > 7.0 and c.y > 8.0 else None)
    # The crescent vent under the front.
    arc = []
    for i in range(17):
        a = math.radians(195 + 150 * i / 16)
        arc.append((cx + (half + 0.4) * math.cos(a), cy + (r_end + 2.2) * math.sin(a), 1.0))
    w.tube("vent", arc, 1.35, hot, 12, squash=0.8)
    inner = [(x, y + 0.4, 1.7) for x, y, _ in arc[3:-3]]
    w.tube("vent_core", inner, 0.6, hotter, 8)


# --- D 157: the shell ship -----------------------------------------------------------------------

@model("shell_ship", [(D, 157, True)])
def shell_ship():
    """Two dark curved shells standing like wings either side of a small hub with a glowing red
    eye (the frames close the shells over it; the model shows them open)."""
    shell = pal("shell_dark", 0x05, metallic=0.75, roughness=0.25)
    inner = pal("shell_inner", 0x02, metallic=0.6, roughness=0.45)
    hub_mat = pal("shell_hub", 0x03, metallic=0.6, roughness=0.4)
    rim = pal("shell_rim", 0x07, metallic=0.7, roughness=0.3)
    eye = pal("shell_eye", 0x77, metallic=0.0, roughness=0.2, glow=1.4)
    # A shell: half of a pointed egg along y, cut flat on the inside.
    prof = k.profile([(-10.4, 0.01), (-9.4, 1.8), (-6.0, 4.4), (-1.0, 6.6), (4.0, 7.4), (8.0, 6.8), (11.0, 5.0),
                      (12.6, 2.6), (13.3, 0.01)], 0.6)
    for side in (-1, 1):
        x_in = side * 3.6
        body = w.lathe_axis(f"shell{side}", prof, shell, (x_in, 0.0, 0.0), (0, 1, 0), 32, squash=1.15)
        kept = sh.cut_planes([body], [((x_in, 0, 0), (-side, 0, 0))])
        for obj in kept:
            k.smooth(obj, 40)
            w.paint_faces(obj, lambda c, n, s=side: inner if n.x * s < -0.9 else None)
        # A rim along the shell's inner edge, over its top.
        top = [(x_in + side * 0.3, y, max(0.3, 1.15 * r - 0.2)) for y, r in prof[2:-2]]
        w.tube(f"rim{side}", top, 0.45, rim, 8)
    # The hub between them, the eye on it.
    w.rounded_box("hub", (0.0, 3.0, 0.0), (7.6, 10.0, 5.0), hub_mat, bevel=0.8)
    w.rounded_box("neck", (0.0, -2.6, -0.4), (4.0, 3.6, 3.4), inner, bevel=0.6)
    w.hoop("eye_ring", (0.0, 5.3, 2.4), [(1.4, -0.3), (2.2, -0.2), (2.3, 0.3), (1.6, 0.5)], rim, 20, scale_y=0.8)
    w.sphere("eye", (0.0, 5.3, 2.3), (1.6, 1.2, 0.9), eye, 16, 8)


# --- D 117: the red medallion --------------------------------------------------------------------

@model("medallion_red", [(D, 117, True)])
def medallion_red():
    """A winged medallion of pink-red metal, like D 79's golden one (ornament): a shield-shaped
    plate with rounded wings, ridges from its corners to an orange gem in a setting low in its
    middle, a ridge up to a ring at its top. It flies, so its back is rounded too."""
    g = w.grid(art.D117, 24)
    metal = pal("medal_red", 0x47, metallic=0.75, roughness=0.3)
    light = pal("medal_red_light", 0x4b, metallic=0.75, roughness=0.25)
    dark = pal("medal_red_dark", 0x43, metallic=0.7, roughness=0.35)
    gem = pal("medal_gem", 0x79, metallic=0.1, roughness=0.08, glow=0.9)
    gem_core = pal("medal_gem_core", 0x7c, metallic=0.0, roughness=0.05, glow=1.3)
    rows = w.regions(g, lambda v, c, r: "#")
    rows = w.relabel(rows, [("#", ".", 8, 15, 0, 5)])  # the ring is turned
    plate = w.part("plate", rows, "#", metal, sh.pillow_profile(2.6, 1.3, crown=1.1), bottom=0.45, smooth=2,
                   epsilon=0.4, spacing=0.45)
    w.decimate(plate, 2400)
    k.smooth(plate, 50)
    w.paint_faces(plate, lambda c, n: dark if n.z < -0.2 else None)

    def on_plate(x, y, lift=0.0):
        return (x, y, sh.surface_z(plate, x, y, 2.6) + lift)
    # The ridges: from the wings' tops and the lower corners to the gem, and up to the ring.
    gx, gy = px(11.5), py(17.2)
    for (c0, r0), (c1, r1) in (((3.0, 6.0), (10.0, 15.5)), ((20.0, 6.0), (13.0, 15.5)), ((2.5, 15.0), (9.0, 18.0)),
                               ((21.0, 15.0), (14.0, 18.0)), ((11.5, 6.0), (11.5, 13.8))):
        pts = [on_plate(px(c0 + (c1 - c0) * t), py(r0 + (r1 - r0) * t), 0.15) for t in (0.0, 0.25, 0.5, 0.75, 1.0)]
        w.tube(f"ridge{c0}{r0}", pts, 0.65, light, 10, squash=0.8)
    # The gem in its setting.
    z = sh.surface_z(plate, gx, gy, 3.0)
    w.hoop("setting", (gx, gy, z), [(1.9, -0.3), (2.9, -0.2), (3.0, 0.4), (2.3, 0.8)], light, 28, scale_y=0.95)
    w.sphere("gem", (gx, gy, z + 0.3), (2.1, 2.0, 1.4), gem, 20, 10)
    w.sphere("gem_core", (gx - 0.4, gy + 0.4, z + 1.35), (0.8, 0.8, 0.35), gem_core, 12, 6)
    # The ring at the top.
    w.hoop("ring", (px(11.5), py(4.0), 1.6), [(1.0, -0.6), (2.5, -0.6), (2.9, 0.0), (2.5, 0.6), (1.0, 0.6),
                                             (0.7, 0.0)], metal, 28, scale_y=0.85)


# --- D 16: the bronze beetle ---------------------------------------------------------------------

@model("bronze_beetle", [(D, 16, True)])
def bronze_beetle():
    """A bronze beetle: a ribbed body between two raised wing cases (bronze frames round red
    panels, two on each), red eyes at its head, and green hooked legs reaching down the screen with
    red claws between them."""
    bronze = pal("beetle_bronze", 0x18, metallic=0.7, roughness=0.3)
    bronze_light = pal("beetle_bronze_light", 0x1b, metallic=0.7, roughness=0.25)
    bronze_dark = pal("beetle_bronze_dark", 0x14, metallic=0.6, roughness=0.4)
    red = pal("beetle_red", 0x46, metallic=0.45, roughness=0.3)
    green = pal("beetle_green", 0x24, metallic=0.4, roughness=0.35)
    eye = pal("beetle_eye", 0x75, metallic=0.0, roughness=0.2, glow=1.0)
    # The body: a long ribbed hull down the middle.
    hull = [(-4.0, 0.01), (-3.6, 1.6), (-2.0, 2.9), (2.0, 3.5), (6.0, 3.5), (8.5, 3.0), (10.2, 2.0), (11.0, 0.01)]
    w.lathe_axis("body", k.profile(hull, 0.6), bronze, (px(11.5), 0.0, 1.0), (0, 1, 0), 24, squash=1.1)
    for x in (-1.6, 0.0, 1.6):
        w.tube(f"rib{x}", [(px(11.5) + x, y, 3.9 - 0.04 * (y - 5) ** 2 * 0.3) for y in (-2.0, 2.0, 6.0, 10.0)], 0.4,
               bronze_light, 8)
    # The wing cases: a bronze frame round two red panels each, leaning out.
    for side in (-1, 1):
        cx = px(11.5) + side * 6.1
        frame = w.block(f"case{side}", (cx, 5.6), 2.5, 7.8, 3.2, bronze_dark, rounding=1.0, power=3.0, segments=24,
                        z0=0.8)
        for y0, y1 in ((12.0, 6.2), (4.2, -0.8)):
            w.block(f"panel{side}{y0}", (cx, (y0 + y1) / 2), 2.0, (y0 - y1) / 2 - 0.3, 0.8, red, rounding=0.4,
                    power=3.0, segments=20, z0=3.6)
        w.tube(f"case_edge{side}", [(cx + side * 2.4, y, 3.4) for y in (12.6, 8.0, 3.0, -1.6)], 0.5, bronze_light, 8)
        frame.data.transform(Matrix.Translation((cx, 0, 0)) @ Matrix.Rotation(math.radians(-8 * side), 4, "Y") @
                             Matrix.Translation((-cx, 0, 0)))
    # The eyes at the head.
    for side in (-1, 1):
        w.sphere(f"eye{side}", (px(11.5) + side * 2.2, 10.0, 3.6), (1.0, 1.2, 0.9), eye, 12, 6)
    # The legs: green hooks from the body's lower corners down the screen, the claws between them.
    for side in (-1, 1):
        x0 = px(11.5)
        leg = [(x0 + side * 5.4, -2.6, 2.2), (x0 + side * 7.9, -5.6, 2.0), (x0 + side * 7.8, -9.4, 1.6),
               (x0 + side * 6.0, -11.9, 1.2), (x0 + side * 3.8, -13.0, 1.0)]
        w.tube(f"leg{side}", w.catmull(leg, 0.7), 0.62, green, 10)
        claw = [(x0 + side * 1.4, -3.5, 1.8), (x0 + side * 1.6, -6.0, 1.5), (x0 + side * 1.1, -7.6, 1.2)]
        w.tube(f"claw{side}", claw, 0.5, bronze_light, 8)
        w.sphere(f"claw_tip{side}", (x0 + side * 1.1, -7.8, 1.2), (0.6, 0.7, 0.5), eye, 10, 5)


w.run()
