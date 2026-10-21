"""Wave 3, batch T of the enemy models: the stand-alone enemies of sheet V (episode 2's MARKERS and MISTAKES),
modelled as their sprites look (models.cfg: yaw=0; the green beetle, V 165: polish_green_beetle.py):

- chevron_ship (V 159): MARKERS' steel-blue ship: a rounded hood with an orange band arching over it
  and a blue gem inside the arch, a pod below it with a bulging nose in a dark groove, flared blades
  either side.
- swirl_machine (V 161): MARKERS' machine on the ground: a lilac shell round a blue orb with a dark
  swirl, red streaks on its flanks, a grey body below with a steel-blue nose and a glowing red tip,
  lilac claws either side.
- copper_car (V 163): MARKERS' copper car on the ground, its front up the screen: four grey wheels,
  yellow lamps at its corners, a cabin glazed in blue all round under a copper roof.
- robot_head (V 48): MARKERS' and MISTAKES' blue steel robot head: a helmet with a crest and rounded
  pads, a grey visor bar with a glowing red eye, side plates, a ribbed jaw and grey hinges.
- blue_torpedo, blue_torpedo_l (V 235, V 237): MARKERS' small blue torpedoes on the ground (custom
  enemies), nose right and its mirror image nose left: a round body, a tail ring, two pairs of
  wings, blue lights on struts.

The large parts are inflated from the sprites' pixels (wave3_t_art.py) and collapsed to a few
hundred triangles before they are painted. The objects drawn from several sprites are in wave3_t.py;
the shared helpers in wave3_t_kit.py.

usage: Blender -b --factory-startup -P wave3_t_ships.py -- [--only name,name] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1]
"""
import math
import os
import sys

from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_t_art as art  # noqa: E402
import wave3_t_kit as w  # noqa: E402
from wave3_t_kit import sh, pal, model, grid, regions, ramp, smoothstep  # noqa: E402


# --- V 159: the steel ship with the orange chevron --------------------------------------------------------

@model("chevron_ship", [159])
def chevron_ship():
    """A steel-blue ship: a rounded hood (rows 3-16) with an orange band arching over it and a blue gem
    inside the arch; below it a pod with a bulging nose in a dark groove, flared blades either side."""
    g = grid(art.SPEAR, 24)
    steel = pal("chv_steel", 0x3b, metallic=0.55, roughness=0.28)
    light = pal("chv_light", 0x3d, metallic=0.55, roughness=0.24)
    shine = pal("chv_shine", 0x3e, metallic=0.6, roughness=0.2)
    dark = pal("chv_dark", 0x35, metallic=0.5, roughness=0.4)
    groove = pal("chv_groove", 0x33, metallic=0.4, roughness=0.5)
    orange = pal("chv_orange", 0x76, metallic=0.3, roughness=0.28, glow=0.35)
    orange_hi = pal("chv_orange_hi", 0x79, metallic=0.25, roughness=0.22, glow=0.7)
    red = pal("chv_red", 0x73, metallic=0.3, roughness=0.3, glow=0.3)
    blue = pal("chv_blue", 0x96, metallic=0.4, roughness=0.1, glow=0.45)
    blue_hi = pal("chv_blue_hi", 0x9d, metallic=0.3, roughness=0.08, glow=0.9)

    def label(v, c, r):
        if r <= 16:
            return "U"
        if 5 <= c <= 18:
            return "P"
        if c <= 3 or c >= 20 or r >= 25:
            return "F"
        return "."
    rows = regions(g, label)
    hood = w.lite(w.part("hood", rows, "U", steel, sh.round_profile(0.75, max_height=6.2), base=2.0, bottom=0.3,
                         spacing=0.5, smooth=2), 1300)
    w.paint_faces(hood, lambda c, n: dark if n.z < 0.3 else None)
    pod = w.lite(w.part("pod", rows, "P", steel, sh.round_profile(0.7, max_height=4.0), base=1.6, bottom=0.3,
                        spacing=0.45, smooth=2), 1100)
    w.paint_faces(pod, lambda c, n: dark if n.z < 0.3 else None)
    for side in (-1, 1):
        side_rows = ["".join(ch if (c < 12) == (side < 0) else "." for c, ch in enumerate(row)) for row in rows]
        fin = w.lite(w.part(f"blade{side}", side_rows, "F", steel, sh.round_profile(0.8, max_height=2.6), base=1.8,
                            bottom=0.4, spacing=0.35, smooth=2), 500)
        w.paint_faces(fin, lambda c, n: dark if n.z < 0.3 else None)

    # The orange band arching over the hood, brighter on its inner side.
    for side in (-1, 1):
        pts = [(0.0, 9.6), (1.5, 7.6), (3.0, 5.5), (4.3, 3.5), (4.9, 1.5), (5.5, -0.5), (6.6, -2.0), (7.4, -2.6)]
        path = [Vector((p.x, p.y, sh.surface_z(hood, p.x, p.y, 3.0) + 0.05)) for p in
                w.catmull([(side * x, y, 0.0) for x, y in pts], 0.4)]
        band = w.tube(f"band{side}", path, 1.15, orange, 10, squash=0.55)
        w.paint_faces(band, lambda c, n: orange_hi if n.z > 0.5 and n.x * side < -0.1 else None)
        w.sphere(f"band_end{side}", (side * 7.6, -2.7, sh.surface_z(hood, side * 7.4, -2.4, 3.0)), (0.8, 0.7, 0.6), red,
                 10, 5)
    # The blue gem inside the arch (rows 9-12).
    gz = sh.surface_z(hood, 0.0, 3.0, 7.0)
    w.hoop("gem_setting", (0.0, 3.0, gz - 0.2), [(1.8, -0.5), (2.3, -0.3), (2.3, 0.3), (1.8, 0.4)], dark, 24)
    w.sphere("gem", (0.0, 3.0, gz), (2.1, 2.2, 1.3), blue, 18, 9)
    w.sphere("gem_glint", (-0.6, 3.6, gz + 1.05), (0.7, 0.7, 0.3), blue_hi, 10, 5)

    # The pod's nose: a bulge in a dark groove (the arch of rows 17-26).
    pz = sh.surface_z(pod, 0.0, -8.5, 4.5)
    nose = w.sphere("nose", (0.0, -8.6, pz - 1.6), (3.3, 4.6, 2.2), light, 20, 10)
    w.paint_faces(nose, lambda c, n: shine if n.z > 0.8 and n.x < -0.1 else None)
    groove_pts = [(-5.0, -12.6), (-4.6, -9.0), (-3.2, -6.0), (-1.3, -3.7), (0.0, -3.2), (1.3, -3.7), (3.2, -6.0),
                  (4.6, -9.0), (5.0, -12.6)]
    path = [Vector((p.x, p.y, sh.surface_z(pod, p.x, p.y, 3.0) - 0.05)) for p in
            w.catmull([(x, y, 0.0) for x, y in groove_pts], 0.4)]
    w.tube("groove", path, 0.45, groove, 6)


# --- V 161: the lilac machine with the blue swirl ---------------------------------------------------------

def ellipsoid_z(centre, radii, x, y, default=0.0):
    cx, cy, cz = centre
    rx, ry, rz = radii
    q = 1.0 - ((x - cx) / rx) ** 2 - ((y - cy) / ry) ** 2
    return cz + rz * math.sqrt(q) if q > 0 else default


@model("swirl_machine", [161])
def swirl_machine():
    """MARKERS' machine on the ground: a lilac shell like a hood (rows 3-16) round a blue orb with a dark
    swirl, red streaks on its flanks; below it a grey body of two rounded lobes, a steel-blue nose with a
    glowing red tip, and lilac claws either side."""
    g = grid(art.LILAC, 24)
    lilac = pal("swl_lilac", 0x58, metallic=0.4, roughness=0.32)
    lilac_hi = pal("swl_lilac_hi", 0x5c, metallic=0.4, roughness=0.26)
    lilac_dark = pal("swl_lilac_dark", 0x55, metallic=0.35, roughness=0.4)
    grey = pal("swl_grey", 0x6b, metallic=0.55, roughness=0.3)
    grey_hi = pal("swl_grey_hi", 0x6d, metallic=0.6, roughness=0.22)
    grey_dark = pal("swl_grey_dark", 0x66, metallic=0.5, roughness=0.38)
    steel = pal("swl_steel", 0x39, metallic=0.55, roughness=0.28)
    steel_hi = pal("swl_steel_hi", 0x3d, metallic=0.6, roughness=0.2)
    blue = pal("swl_blue", 0x94, metallic=0.35, roughness=0.12, glow=0.35)
    blue_hi = pal("swl_blue_hi", 0x9b, metallic=0.3, roughness=0.08, glow=0.9)
    swirl = pal("swl_swirl", 0x91, metallic=0.3, roughness=0.3)
    red = pal("swl_red", 0x74, metallic=0.3, roughness=0.3, glow=0.6)
    red_hot = pal("swl_red_hot", 0x78, metallic=0.1, roughness=0.2, glow=1.6)

    def label(v, c, r):
        rp = ramp(v)
        if r <= 16 and rp in (5, 7, 9):
            return "S"
        if rp == 5 and r >= 17:
            return "A"
        if rp == 6 or (r in (14, 15, 16) and rp in (6, 9)):
            return "G"
        if rp in (3, 7) and r >= 19:
            return "N"
        return "."
    rows = regions(g, label)
    shell = w.lite(w.part("shell", rows, "S", lilac, sh.pillow_profile(3.2, 2.6, crown=1.4), base=2.4, bottom=0.3,
                          spacing=0.5, smooth=2), 1400)
    w.paint_faces(shell, lambda c, n: lilac_dark if n.z < 0.3 else None)
    body = w.lite(w.part("body", rows, "G", grey, sh.round_profile(0.7, max_height=4.2), base=1.4, bottom=0.3,
                         spacing=0.45, smooth=2), 1200)
    w.paint_faces(body, lambda c, n: grey_dark if n.z < 0.3 else None)
    for side in (-1, 1):
        side_rows = ["".join(ch if (c < 12) == (side < 0) else "." for c, ch in enumerate(row)) for row in rows]
        claw = w.lite(w.part(f"claw{side}", side_rows, "A", lilac, sh.round_profile(0.8, max_height=2.4), base=1.6,
                             bottom=0.4, spacing=0.35, smooth=2), 450)
        w.paint_faces(claw, lambda c, n: lilac_dark if n.z < 0.3 else None)
    # The spine between the body's lobes, dark grooves either side.
    for x, r, m in ((-0.9, 0.35, grey_dark), (0.9, 0.35, grey_dark), (0.0, 0.55, grey_hi)):
        path = [Vector((x, y, sh.surface_z(body, x, y, 4.0) - (0.1 if m is grey_hi else 0.2))) for y in (-1.2, -3.0, -5.0)]
        w.tube(f"spine{x:+.1f}", path, r, m, 8)

    # The blue orb in the shell (rows 4-15), its dark swirl and its glint.
    oc, orad = (0.0, 4.2, 4.4), (4.3, 5.9, 4.0)
    w.hoop("orb_rim", (0.0, 4.2, 5.6), [(4.0, -0.6), (4.9, -0.3), (4.9, 0.4), (4.0, 0.6)], lilac_dark, 32,
           scale_y=1.38)
    w.sphere("orb", oc, orad, blue, 28, 14)
    spiral = []
    for i in range(46):
        t = i / 45
        a = math.radians(70 + 560 * t)
        r = 0.5 + 2.9 * t
        x, y = r * math.cos(a) * 0.95, 4.2 + r * math.sin(a) * 1.25 - 0.4
        spiral.append((x, y, ellipsoid_z(oc, orad, x, y, 5.0) + 0.02))
    w.tube("swirl", spiral, 0.42, swirl, 8, squash=0.6)
    w.sphere("orb_glint", (-1.4, 6.0, 8.1), (0.9, 1.2, 0.3), blue_hi, 10, 5)
    # The red streaks on the shell's flanks.
    for side in (-1, 1):
        pts = [(side * 5.6, 8.7), (side * 7.5, 6.6), (side * 9.0, 4.4), (side * 9.6, 2.6)]
        path = [Vector((p.x, p.y, sh.surface_z(shell, p.x, p.y, 4.0) - 0.15)) for p in
                w.catmull([(x, y, 0.0) for x, y in pts], 0.4)]
        w.tube(f"streak{side}", path, 0.55, red, 8, squash=0.7)

    # The nose: a steel-blue dome pointing down the screen (rows 19-26), its red tip glowing.
    nose = w.loft_y("nose", [(-12.6, 0.0, 3.6, 0.6, 0.6, 1.0), (-11.8, 0.0, 3.6, 2.3, 2.0, 1.4),
                             (-10.2, 0.0, 3.6, 3.9, 2.9, 1.6), (-8.6, 0.0, 3.6, 4.6, 3.2, 1.6),
                             (-7.0, 0.0, 3.6, 4.2, 2.9, 1.6), (-6.0, 0.0, 3.6, 2.4, 1.8, 1.4)], steel, segments=24,
                    power=2.2, start=(0.0, -12.9, 3.6), end=(0.0, -5.6, 3.6))
    w.paint_faces(nose, lambda c, n: steel_hi if n.z > 0.7 and n.x < 0.0 else None)
    w.sphere("tip", (0.0, -11.6, 4.2), (1.6, 1.5, 1.0), red, 14, 7)
    w.sphere("tip_hot", (-0.2, -11.3, 4.9), (0.7, 0.6, 0.4), red_hot, 10, 5)


# --- V 163: the copper car ---------------------------------------------------------------------------------

@model("copper_car", [163])
def copper_car():
    """MARKERS' copper car on the ground, its front up the screen: a rounded body on four grey wheels,
    yellow lamps at its corners, a cabin glazed in blue all round (windscreen, side and rear windows)
    under a copper roof with a lighter ridge (its axis at x = -0.5)."""
    ax = -0.5
    copper = pal("car_copper", 0x46, metallic=0.5, roughness=0.3)
    copper_hi = pal("car_copper_hi", 0x49, metallic=0.5, roughness=0.24)
    copper_dark = pal("car_copper_dark", 0x43, metallic=0.45, roughness=0.4)
    glass = pal("car_glass", 0x93, metallic=0.3, roughness=0.06, glow=0.25)
    glass_hi = pal("car_glass_hi", 0x96, metallic=0.3, roughness=0.05, glow=0.5)
    tyre = pal("car_tyre", 0x63, metallic=0.2, roughness=0.6)
    hub = pal("car_hub", 0x66, metallic=0.6, roughness=0.3)
    lamp = pal("car_lamp", 0x7b, metallic=0.0, roughness=0.2, glow=1.2)

    # The body: a pill (rows 3-24, columns 6-16), its sides rounded, lower than the cabin.
    body = w.cushion("body", w.ccw(sh.ellipse(ax, 0.0, 5.6, 10.9, count=48)), copper,
                     lambda x, y: 3.6 + 0.4 * smoothstep(10.5, 6.0, abs(y)), rounding=1.6, spacing=0.45, base=0.8)
    # Squarer than an ellipse: push its outline towards a rounded rectangle.
    for v in body.data.vertices:
        dx, dy = (v.co.x - ax) / 5.6, v.co.y / 10.9
        d = math.hypot(dx, dy)
        if d > 0.05:
            f = (abs(dx) ** 3.2 + abs(dy) ** 3.2) ** (1 / 3.2) / d
            v.co.x = ax + (v.co.x - ax) / f
            v.co.y = v.co.y / f
    w.lite(body, 1300)
    w.paint_faces(body, lambda c, n: copper_hi if n.z > 0.7 and n.x < -0.2 else copper_dark if n.z < 0.3 else None)
    # The cabin: a glass band all round (rows 8-20), the copper roof on it with a light ridge.
    cabin = w.block("cabin", (ax, -0.5), 4.6, 6.6, 2.7, glass, taper=1.4, rounding=0.8, power=3.2, segments=40, z0=3.4)
    w.paint_faces(cabin, lambda c, n: glass_hi if n.x < -0.5 and n.z > 0.2 else None)
    roof = w.block("roof", (ax, -1.0), 2.9, 4.0, 1.1, copper, rounding=0.6, power=3.0, segments=32, z0=5.6)
    w.paint_faces(roof, lambda c, n: copper_hi if n.z > 0.6 and n.x < 0.0 else None)
    w.tube("roof_ridge", [(ax - 0.6, 2.2, 6.75), (ax - 0.6, -4.4, 6.75)], 0.45, copper_hi, 8)
    # The wheels, sticking out at the sides (rows 9-11 and 19-21).
    for y in (3.5, -6.5):
        for side in (-1, 1):
            x = ax + side * 5.7
            w.lathe_axis(f"wheel{side}{y:+.0f}", [(0.0, 1.5), (0.15, 1.75), (1.3, 1.75), (1.45, 1.5)], tyre,
                         (x - side * 0.75, y, 1.75), (side, 0, 0), 16)
            w.lathe_axis(f"hub{side}{y:+.0f}", [(0.0, 0.9), (0.2, 0.9), (0.25, 0.0)], hub, (x + side * 0.7, y, 1.75),
                         (side, 0, 0), 12)
    # The lamps at the corners: two at the front (rows 5-6), two at the back (row 24).
    for side in (-1, 1):
        w.sphere(f"head_lamp{side}", (ax + side * 3.9, 8.5, 3.7), (0.65, 0.6, 0.4), lamp, 10, 5)
        w.sphere(f"tail_lamp{side}", (ax + side * 2.0, -10.3, 3.5), (0.5, 0.45, 0.35), lamp, 10, 5)


# --- V 48: the blue robot head --------------------------------------------------------------------------------

@model("robot_head", [48])
def robot_head():
    """MARKERS' and MISTAKES' blue steel robot head: a broad helmet with a crest down its middle and
    rounded pads either side (rows 0-9), a grey visor bar across with a glowing red eye (rows 10-12),
    side plates, a long ribbed jaw narrowing to the chin and grey hinges at its sides (rows 17-22)."""
    g = grid(art.ROBOT, 24)
    steel = pal("rob_steel", 0x38, metallic=0.55, roughness=0.3)
    light = pal("rob_light", 0x3b, metallic=0.55, roughness=0.26)
    shine = pal("rob_shine", 0x3d, metallic=0.6, roughness=0.2)
    dark = pal("rob_dark", 0x34, metallic=0.5, roughness=0.4)
    grey = pal("rob_grey", 0x07, metallic=0.6, roughness=0.3)
    grey_hi = pal("rob_grey_hi", 0x0a, metallic=0.6, roughness=0.26)
    grey_dark = pal("rob_grey_dark", 0x03, metallic=0.5, roughness=0.4)
    eye = pal("rob_eye", 0x75, metallic=0.1, roughness=0.2, glow=1.5)
    eye_hot = pal("rob_eye_hot", 0x7a, metallic=0.0, roughness=0.15, glow=2.6)

    def label(v, c, r):
        if ramp(v) == 0:
            return "V" if r <= 13 else "G"
        if ramp(v) == 7:
            return "V"
        if r <= 9:
            return "T"
        if c <= 5 or c >= 18:
            return "C" if r <= 16 else "."
        return "J"
    rows = regions(g, label)
    top = w.lite(w.part("helmet", rows, "T", steel, sh.pillow_profile(3.6, 2.4, crown=1.0), base=3.2, bottom=0.4,
                        spacing=0.5, smooth=2), 1300)
    w.paint_faces(top, lambda c, n: dark if n.z < 0.3 else None)
    jaw = w.lite(w.part("jaw", rows, "J", pal("rob_jaw", 0x39, metallic=0.55, roughness=0.28), sh.pillow_profile(2.8, 1.8, crown=0.8), base=2.6, bottom=0.4,
                        spacing=0.5, smooth=2, z_fn=lambda x, y, z: z - 1.2 * smoothstep(-2.0, -13.0, y)), 1100)
    w.paint_faces(jaw, lambda c, n: dark if n.z < 0.3 else None)
    for side in (-1, 1):
        side_rows = ["".join(ch if (c < 12) == (side < 0) else "." for c, ch in enumerate(row)) for row in rows]
        cheek = w.lite(w.part(f"cheek{side}", side_rows, "C", steel, sh.pillow_profile(2.6, 1.4, crown=0.4), base=2.8,
                              bottom=0.4, spacing=0.45, smooth=2), 400)
        w.paint_faces(cheek, lambda c, n: dark if n.z < 0.3 else None)
        hinge = w.lite(w.part(f"hinge{side}", side_rows, "G", grey, sh.round_profile(0.9, max_height=2.4), base=2.2,
                              bottom=0.5, spacing=0.4, smooth=2), 300)
        w.paint_faces(hinge, lambda c, n: grey_dark if n.z < 0.3 else None)
        # The rounded pads either side of the crest (rows 1-6).
        pad = w.sphere(f"pad{side}", (side * 7.0, 10.4, 6.9), (3.2, 3.0, 1.3), steel, 20, 10)
        w.paint_faces(pad, lambda c, n: shine if n.z > 0.7 and n.x < -0.1 else light if n.z > 0.55 else None)
        # The jaw's ribs (columns 9-10 and 13-14).
        x = side * 1.6
        path = [Vector((x, y, sh.surface_z(jaw, x, y, 4.0) - 0.05)) for y in (-0.6, -4.0, -7.5, -11.0)]
        w.tube(f"jaw_rib{side}", path, 0.45, shine, 8)
        w.tube(f"jaw_groove{side}", [Vector((side * 4.4, y, sh.surface_z(jaw, side * 4.4, y, 4.0) - 0.2))
                                     for y in (-0.5, -4.5, -9.0)], 0.35, dark, 8)
    # The crest down the helmet's middle, a dark slot in it.
    crest = [(0.0, 14.2, 6.8), (0.0, 11.0, 8.0), (0.0, 7.0, 8.0), (0.0, 4.6, 7.4)]
    w.tube("crest", w.catmull(crest, 0.5), [1.9, 2.4, 2.4, 2.2, 2.2, 2.2, 2.1, 2.0, 2.0, 1.9, 1.9, 1.8, 1.8, 1.7, 1.6,
                                           1.6, 1.6, 1.6, 1.6, 1.6, 1.6], steel, 16, squash=0.7)
    w.rounded_box("crest_slot", (0.0, 9.5, 9.5), (1.3, 4.2, 0.8), dark, bevel=0.3)
    for side in (-1, 1):
        w.tube(f"crest_edge{side}", [(side * 2.2, 13.4, 7.6), (side * 2.4, 10.0, 8.6), (side * 2.3, 6.0, 8.4)], 0.4,
               shine, 8)
    # The band under the helmet (rows 7-9) and the visor bar across (rows 10-12) with the red eye.
    w.loft_x("band", [(x, 5.5, 4.4, 1.3, 1.5, 1.0) for x in (-10.2, -9.4, 0.0, 9.4, 10.2)], dark, segments=14)
    visor = w.loft_x("visor", [(x, 2.3, 5.0, 1.7, 1.6, 1.2) for x in (-6.4, -5.6, -2.0, 2.0, 5.6, 6.4)], grey,
                     segments=16, power=2.6)
    w.paint_faces(visor, lambda c, n: grey_hi if n.z > 0.7 else grey_dark if n.z < 0.2 else None)
    w.sphere("eye", (0.0, 2.4, 6.4), (1.5, 1.5, 1.0), eye, 14, 7)
    w.sphere("eye_hot", (-0.3, 2.7, 7.2), (0.6, 0.6, 0.35), eye_hot, 8, 4)


# --- V 235 and its mirror image V 237: the small blue torpedo ---------------------------------------------------

def torpedo(mirror):
    """A small steel-blue torpedo lying along x, its nose to the right: a round body, a cone behind a
    ring at its tail, a pair of broad wings in its middle and smaller ones near the nose, blue lights
    on short struts by the tail (its axis at y = 1)."""
    steel = pal("tor_steel", 0x38, metallic=0.55, roughness=0.3)
    light = pal("tor_light", 0x3c, metallic=0.6, roughness=0.22)
    dark = pal("tor_dark", 0x34, metallic=0.5, roughness=0.4)
    blue = pal("tor_blue", 0x9a, metallic=0.2, roughness=0.15, glow=1.6)
    yc, zc = 1.0, 3.2
    prof = [(-8.4, 1.4), (-8.0, 1.9), (-6.0, 1.8), (-4.0, 2.0), (-3.0, 2.6), (2.0, 2.8), (6.0, 2.8), (8.0, 2.6),
            (9.6, 2.1), (10.6, 1.4), (11.2, 0.6), (11.4, 0.0)]
    body = w.lathe_axis("body", [(x + 8.4, r) for x, r in prof], steel, (-8.4, yc, zc), (1, 0, 0), 24)
    w.paint_faces(body, lambda c, n: light if n.z > 0.55 and n.y > -0.2 else dark if n.z < -0.2 else None)
    # The tail ring and the cap behind it.
    ring = w.hoop("tail_ring", (0, 0, 0), [(2.2, -0.7), (3.4, -0.6), (3.4, 0.6), (2.2, 0.7)], steel, 28)
    ring.data.transform(Matrix.Translation((-10.0, yc, zc)) @ Matrix.Rotation(math.radians(90), 4, "Y"))
    w.paint_faces(ring, lambda c, n: light if n.z > 0.5 else None)
    w.lathe_axis("tail_cap", [(0.0, 0.0), (0.4, 1.4), (1.8, 1.6), (2.0, 1.2)], dark, (-10.9, yc, zc), (1, 0, 0), 16)
    # The wings: broad ones in the middle (columns 8-12), smaller ones near the nose (15-19).
    for side in (-1, 1):
        wing = [(-4.0, 0.0), (0.6, 0.0), (0.6, 4.6), (-0.2, 6.6), (-1.6, 7.6), (-3.2, 7.6), (-3.8, 6.4)]
        wing = [(x, yc + side * y) for x, y in wing]
        wg = w.chamfered(f"wing{side}", w.ccw(wing), zc - 0.5, zc + 0.5, steel, chamfer=0.35)
        w.paint_faces(wg, lambda c, n: light if n.z > 0.6 and side > 0 else None)
        fin = [(3.4, 0.0), (7.4, 0.0), (6.6, 3.0), (5.6, 5.6), (4.0, 5.6), (3.4, 4.0)]
        fin = [(x, yc + side * y) for x, y in fin]
        w.chamfered(f"canard{side}", w.ccw(fin), zc - 0.4, zc + 0.4, steel, chamfer=0.3)
        # The blue lights on struts by the tail (columns 5 and 7, rows 9 and 16).
        for x in (-6.5, -4.5):
            w.tube(f"strut{side}{x:.0f}", [(x, yc + side * 1.6, zc + 0.6), (x, yc + side * 3.3, zc + 0.9)], 0.35, dark, 6)
            w.sphere(f"light{side}{x:.0f}", (x, yc + side * 3.5, zc + 1.0), (0.55, 0.55, 0.5), blue, 10, 5)
    if mirror:
        w.mirror_all()


@model("blue_torpedo", [235])
def blue_torpedo():
    torpedo(False)


@model("blue_torpedo_l", [237])
def blue_torpedo_l():
    torpedo(True)


w.run()
