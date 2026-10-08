"""Enemies of wave 3, batch S (sheet F: SAVARA, SAVARA IV, SAVARA Y), modelled as their sprites look
(models.cfg: yaw=0). SAVARA's boss is in wave3_s_boss.py; the kit is wave3_s_kit.py, the pixels
wave3_s_art.py.

- gun_silo_43, gun_silo_81, gun_silo_119: the blue-grey gun emplacement sunk in the ground of SAVARA,
  SAVARA IV and SAVARA Y, which the level events place as three sprites, 43 above 81 above 119 (enemies
  171, 172, 173; SAVARA IV sets the top one 6 pixels right and 6 down). An armoured roof with two
  diagonal ribs at its far end, blue armour blocks at its sides, a housing with a sloped blue front
  over a dark bay between two walls; in the bay blue pillars and the gun's cradle, the gun lying in it
  with its muzzle over the apron and the grating in front. The frames (45, 83, 121) show the muzzle's
  flash: the model keeps the gun cold but for a dim glow in its bore. Built whole, 24 x 67, and cut
  into its three pieces (origin).
- jet_emerald (F 53): the big green jet of SAVARA and SAVARA Y, nose down the screen: a long fuselage
  with the cockpit near the nose, big wings swept back towards the top, tail planes and a fin.
- jet_twin_tail (F 55): SAVARA's green jet with brown wings and two tail booms, blue lights on its
  wings, nose down the screen.

usage: Blender -b --factory-startup -P wave3_s.py -- [--only name,name] [--preview <prefix>]
       [--check 1] [--stats 1] [--whole <prefix>]
"""
import os
import sys

from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_s_kit as s  # noqa: E402
from wave3_s_kit import art, k, sh, w, n, pal  # noqa: E402


# --- F 43 / 81 / 119: the gun silo ------------------------------------------------------------------

SILO = s.Frame(art.SILO_A, 24, (12, 42))


def silo_painter():
    return s.Painter("silo", shades={0: (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12), 3: (6, 8, 9, 10), 6: (1, 3, 4),
                                     8: (2, 3, 5), 9: (13, 14)},
                     metallic=0.5, roughness=0.4, glow={0x9d: 1.4, 0x9e: 1.6},
                     finish={0: (0.45, 0.45), 3: (0.55, 0.3), 8: (0.55, 0.3), 6: (0.5, 0.4)})


def silo_whole():
    """The emplacement on its ground plate, 24 x 67 pixels (rows 0-66 of the three sprites)."""
    f = SILO
    X, Y = f.X, f.Y
    p = silo_painter()
    grey = p(0x06)
    dark = p(0x02)
    black = p(0x01)
    blue = p(0x38)
    cyan = p(0x83)
    lamp = pal("silo_lamp", 0x9e, metallic=0.1, roughness=0.15, glow=1.8)
    steel = p(0x08)
    hot = pal("silo_bore", 0x72, metallic=0.0, roughness=0.4, glow=0.8)
    parts = []

    # The ground plate under the whole: the trench's floor between the walls, the apron in front.
    plate = s.slab("plate", f.rect(0, 23, 0, 65), 0.0, 1.0, grey, bevel=0.3)
    parts.append(plate)
    # The walls either side of the bay, their tops rounded.
    for name, c0, c1 in (("wall_l", 0, 2), ("wall_r", 21, 23)):
        parts.append(s.slab(name, f.rect(c0, c1, 8, 49), 0.0, 6.2, grey, bevel=0.7, segments=3))
    # The roof at the far end: an armoured plate falling a little towards the bay, two diagonal ribs
    # converging on the housing and a seam down its middle.
    roof = s.slab("roof", f.rect(0, 23, 0, 8), 0.0, 8.0, grey, bevel=0.8, segments=3,
                  z_fn=lambda x, y, z: z - (0.9 * (f.top(0) - y) / 9.0 if z > 4.0 else 0.0))
    parts.append(roof)

    def roof_z(y):
        return 8.0 - 0.9 * (f.top(0) - y) / 9.0
    for name, a, b in (("rib_l", (f.left(3) + 0.4, f.top(0) - 0.3), (X(9.5), Y(7.0))),
                       ("rib_r", (f.right(21) - 0.6, f.top(0) - 0.6), (X(15.0), Y(7.0)))):
        pts = [(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t) for t in (0.0, 0.33, 0.66, 1.0)]
        parts.append(w.tube(name, [(x, y, roof_z(y) + 0.05) for x, y in pts], 0.75, steel, 10, squash=0.7))
    parts.append(s.slab("seam", f.rect(12, 12, 0, 8, inset=0.15), 0.0, 0.6, dark, bevel=0.1,
                        z_fn=lambda x, y, z: z + roof_z(y) - 0.4))
    # The blue armour blocks at the roof's lower corners, a blue lamp in each.
    for name, c0, c1, lamp_c in (("armour_l", 3, 6, 3), ("armour_r", 19, 22, 21)):
        parts.append(s.slab(name, f.rect(c0, c1, 7, 16), 0.0, 9.6, blue, bevel=0.6, segments=3))
        parts.append(w.sphere(name + "_lamp", (X(lamp_c), Y(12.0), 7.6), (0.75, 1.1, 0.75), lamp, 12, 6))
    # The housing: a block with a flat top (rows 9-13) and a sloped front down to the bay (row 27).
    housing = s.prism_x("housing", [(f.top(9), 0.0), (f.top(9), 11.2), (Y(13.0), 11.2), (f.bottom(26), 3.2),
                                    (f.bottom(26), 0.0)], f.left(7), f.right(17), grey, bevel=0.7, segments=3)
    parts.append(housing)

    def slope_z(y):
        t = (Y(13.0) - y) / (Y(13.0) - f.bottom(26))
        return 11.2 + (3.2 - 11.2) * t
    # The grey hatch on the right of the slope and the blue panel on its left.
    for name, c0, c1, r0, r1, mat in (("hatch", 13, 17, 18, 24, steel), ("panel", 7, 12, 18, 24, blue)):
        poly = f.rect(c0, c1, r0, r1, inset=0.3)
        parts.append(s.slab(name, poly, 0.0, 0.7, mat, bevel=0.25,
                            z_fn=lambda x, y, z: z + slope_z(y) - 0.2))
    # The lamps along its foot.
    for c in (7.5, 13.5):
        parts.append(w.sphere(f"foot_lamp{c}", (X(c), Y(25.8), 3.4), (0.7, 0.5, 0.45), cyan, 10, 5))
    # Blue pillars against the walls in the bay.
    for name, c0, c1, r0, r1, top in (("pillar_l1", 1, 3, 29, 35, 7.4), ("pillar_r1", 20, 22, 29, 35, 7.4),
                                      ("pillar_l2", 1, 4, 41, 47, 6.8), ("pillar_r2", 20, 23, 41, 47, 6.8)):
        parts.append(s.slab(name, f.rect(c0, c1, r0, r1), 0.0, top, blue, bevel=0.5, segments=2))
    parts.append(w.sphere("pillar_lamp", (X(20.0), Y(29.6), 7.2), (0.7, 0.7, 0.45), lamp, 10, 5))
    # The gun's cradle: a cross bar with two lamps, arms back to the housing, a brace to the right pillar.
    gz = 4.2
    parts.append(w.rounded_box("cradle", ((f.left(8) + f.right(14)) / 2, Y(43.0), gz - 0.4),
                               (f.right(14) - f.left(8), 2.6, 2.4), blue, bevel=0.5))
    for c in (8.5, 11.5):
        parts.append(w.sphere(f"cradle_lamp{c}", (X(c), Y(43.3), gz + 0.85), (0.6, 0.55, 0.4), lamp, 10, 5))
    for name, path, r in (("arm_l", [(X(9.5), Y(42.0), gz), (X(9.5), Y(36.5), gz + 0.6), (X(9.5), Y(27.6), 3.6)], 0.75),
                          ("arm_r", [(X(14.0), Y(42.5), gz), (X(14.0), Y(36.5), gz + 0.6), (X(14.0), Y(27.6), 3.6)],
                           0.75),
                          ("brace", [(X(16.0), Y(43.0), gz - 0.4), (X(16.0), Y(38.5), gz + 0.4),
                                     (X(20.0), Y(38.5), 5.6)], 0.6),
                          ("brace_l", [(X(7.0), Y(40.0), gz - 0.6), (X(9.5), Y(40.0), gz)], 0.55)):
        parts.append(w.tube(name, path, r, cyan if name.startswith("arm") else blue, 10))
    # The gun: breech, barrel with a blue ring, the muzzle brake, rising a little towards the muzzle.
    gx = X(11.0)
    start = Vector((gx, Y(44.0), gz))
    end = Vector((gx, Y(60.5), gz + 1.9))
    d = (end - start).normalized()
    length = (end - start).length
    prof = [(0.0, 0.01), (0.05, 1.7), (0.6, 2.2), (3.4, 2.2), (3.8, 1.5), (9.0, 1.35), (10.0, 1.35), (10.2, 1.8),
            (11.6, 1.8), (11.8, 1.4), (12.2, 1.45), (12.5, 2.3), (16.0, 2.3), (16.3, 2.0), (length - 0.05, 2.0),
            (length, 1.1)]
    barrel = w.lathe_axis("barrel", prof, steel, tuple(start), tuple(d), 24)

    def paint_barrel(c, nrm):
        t = (Vector(c) - start).dot(d)
        if 10.1 < t < 11.7:
            return blue
        if t < 3.6:
            return p(0x05)
        if nrm.z < -0.2:
            return dark
        return None
    w.paint_faces(barrel, paint_barrel)
    parts.append(barrel)
    # The bore, dark with a dim glow deep inside.
    mouth = end - d * 0.15
    parts.append(w.lathe_axis("bore", [(0.0, 0.01), (0.02, 1.15), (0.6, 1.1), (0.62, 0.01)], black,
                              tuple(mouth - d * 0.5), tuple(d), 16))
    parts.append(w.sphere("bore_glow", tuple(mouth - d * 0.3), (0.6, 0.6, 0.6), hot, 10, 5))
    # In front of the bay: the lip, the plates and the grating.
    parts.append(s.slab("lip", f.rect(0, 23, 50, 52), 0.0, 2.8, grey, bevel=0.6, segments=2))
    parts.append(s.slab("apron", f.rect(0, 23, 53, 58), 0.0, 2.0, grey, bevel=0.4,
                        z_fn=lambda x, y, z: z - 0.35 * (Y(53.0) - y) / 5.0 if z > 1.0 else z))
    parts.append(s.slab("grating", f.rect(0, 23, 59, 65), 0.0, 1.5, dark, bevel=0.3))
    for c in range(1, 23, 2):
        parts.append(s.slab(f"slat{c}", f.rect(c, c, 59, 64, inset=0.1), 1.2, 1.9, grey, bevel=0.15))
    # The sprite's colours on everything but the lamps, the gun's bore and the slats' grey.
    skip = {"bore", "bore_glow", "barrel", "cradle"}
    for obj in parts:
        if obj.name in skip or "lamp" in obj.name:
            continue
        if obj.name.startswith(("rib", "arm", "brace", "foot")):
            s.paint_sprite(obj, f, p, wall_steps=2, under=black, probe=0.6, keep=lambda v: v >> 4 != 9)
        else:
            # The plate (the bay's black floor) keeps the pixels as they are, the rest a little smoothed.
            s.paint_pixels(obj, f, p, wall_steps=2, under=black, probe=0.6, blur=0 if obj.name == "plate" else 1,
                           keep=lambda v: v >> 4 != 9)
    n.merge_by_material(parts)


def silo_piece(sprite, row):
    y1 = 42.0 - 28.0 * row
    return (f"gun_silo_{sprite}", (-12.0, 12.0, y1 - 28.0, y1), (0.0, y1 - 14.0),
            lambda: SILO.mask((0, 24, 28 * row, 28 * row + 28)))


s.pieced("gun_silo", silo_whole, (24, 84), [silo_piece(43, 0), silo_piece(81, 1), silo_piece(119, 2)])


# --- F 55 and F 53: the green jets --------------------------------------------------------------------

def jet_plate(name, frame, mat, skip_rows=(), axis_x=0.0, height=1.1, dihedral=0.05):
    """The wings and tail planes: a thin part over the sprite's outline (rows in skip_rows left out),
    rounded over its edges above and below, rising a little towards the tips."""
    rows = s.regions(frame.g, lambda v, c, r: "." if r in skip_rows else "#")
    polys = sh.outlines(rows, "#", (frame.ox, frame.oy), smooth=2, epsilon=0.3, min_area=1.0)
    obj = sh.inflate(name, polys, mat, sh.round_profile(0.45, max_height=height, min_height=0.2), bottom=0.55,
                     base=-0.1, rim=0.12, spacing=0.55,
                     z_fn=lambda x, y, z: z + dihedral * abs(x - axis_x))
    # The underside follows the dihedral too.
    for v in obj.data.vertices:
        if v.co.z < -0.1:
            v.co.z += dihedral * abs(v.co.x - axis_x)
    return [k.smooth(obj, 50)]


def jet_fuselage(name, prof, mat, axis_x, nose_y, squash=0.75, z=0.0):
    """A round fuselage along y from the nose (nose_y) up the screen: prof [(distance from the nose,
    radius)]."""
    return w.lathe_axis(name, k.profile(prof, 0.5), mat, (axis_x, nose_y, z), (0, 1, 0), 24, squash=squash)


def jet_fin(name, x, profile, mat, thickness=1.2):
    """An upright fin at x: profile [(y, z)], counter-clockwise seen from +x."""
    return s.prism_x(name, profile, x - thickness / 2, x + thickness / 2, mat, bevel=min(0.4, thickness * 0.3),
                     segments=2, angle=35)


J55 = s.Frame(art.JET55, 24, (12, 14))
J55_PAINT = s.Frame(art.JET55, 24, (12, 14)).fill({0x01})


@s.model("jet_twin_tail", mask=lambda: J55.mask())
def jet_twin_tail():
    """SAVARA's green jet with brown wings, nose down the screen: a round green fuselage, wings with a
    straight trailing edge and swept leading edges banded in brown, brown tail planes, twin green tail
    fins reaching past the tail, a dark canopy near the nose and two blue lights on the wing roots."""
    f = J55
    ax = 1.0
    p = s.Painter("jet55", shades={2: (2, 4, 6, 8, 10, 12), 1: (2, 4, 6, 8), 0: (1, 3)},
                  metallic=0.45, roughness=0.35, remap={0x20: 0x21})
    green = p(0x27)
    dark = p(0x21)
    glass = pal("jet55_glass", 0x20, metallic=0.3, roughness=0.05)
    glint = pal("jet55_glint", 0x2c, metallic=0.1, roughness=0.1, glow=0.5)
    light = pal("jet55_light", 0x84, metallic=0.1, roughness=0.15, glow=1.8)
    plate = jet_plate("wing", f, green, skip_rows=(0, 1, 2, 3), axis_x=ax)
    body = jet_fuselage("fuselage", [(0.0, 0.05), (0.5, 0.7), (1.2, 1.25), (3.2, 2.0), (5.2, 2.7), (8.2, 3.0),
                                     (13.2, 3.0), (16.2, 2.7), (19.2, 2.0), (21.4, 1.6), (21.9, 0.05)], green, ax,
                        f.bottom(25) + 0.4, squash=0.72)
    # The nozzle at the tail, between the fins.
    w.lathe_axis("nozzle", [(0.0, 1.5), (0.4, 1.35), (1.1, 1.2), (1.15, 0.01)], dark, (ax, 9.6, 0.0), (0, 1, 0), 16)
    # Twin fins from the tail planes past the tail, leaning out a little.
    fins = []
    for x in (f.X(10), f.X(15)):
        fins.append(jet_fin(f"fin{x:.0f}", x, [(4.6, 0.2), (13.4, 0.2), (13.9, 0.9), (13.5, 4.3), (12.4, 4.6),
                                              (8.0, 1.9), (5.4, 1.2)], green, thickness=1.3))
    # The canopy near the nose, a glint on it.
    w.sphere("canopy", (ax, f.Y(17.6), 1.55), (1.45, 2.5, 1.25), glass, 20, 10)
    w.sphere("glint", (ax - 0.35, f.Y(16.6), 2.6), (0.4, 0.7, 0.2), glint, 10, 5)
    # The blue lights on the wing roots.
    for x in (f.X(10), f.X(15)):
        w.sphere(f"light{x:.0f}", (x, f.Y(12), 1.5 if abs(x - ax) < 3 else 0.6), (0.6, 0.6, 0.45), light, 12, 6)
    for obj in plate:
        s.paint_sprite(obj, J55_PAINT, p, wall_steps=2, under=dark, probe=0.4, blur=1)
    s.paint_sprite(body, J55_PAINT, p, wall_steps=1, under=dark, blur=1)
    for obj in fins:
        s.paint_sprite(obj, J55_PAINT, p, wall_steps=1, under=dark, keep=lambda v: v >> 4 == 2)
    n.merge_by_material()


J53 = s.Frame(art.JET53, 24, (12, 14))
J53_PAINT = s.Frame(art.JET53, 24, (12, 14)).fill({0x22})


@s.model("jet_emerald", mask=lambda: J53.mask())
def jet_emerald():
    """The big green jet of SAVARA and SAVARA Y, nose down the screen: a long round fuselage, big wings
    swept back towards the top of the screen, small tail planes and an upright fin along the top, a
    dark canopy near the nose."""
    f = J53
    ax = 0.5
    p = s.Painter("jet53", shades={2: (2, 4, 6, 8, 10, 12)}, metallic=0.45, roughness=0.35)
    green = p(0x27)
    dark = p(0x22)
    glass = pal("jet53_glass", 0x22, metallic=0.3, roughness=0.05)
    glint = pal("jet53_glint", 0x2b, metallic=0.1, roughness=0.1, glow=0.5)
    plate = jet_plate("wing", f, green, skip_rows=(0, 1), axis_x=ax)
    body = jet_fuselage("fuselage", [(0.0, 0.05), (0.5, 0.8), (1.0, 1.2), (3.0, 2.0), (5.0, 2.7), (8.0, 3.1),
                                     (14.0, 3.2), (18.0, 2.4), (20.0, 2.0), (23.0, 1.3), (24.4, 0.7), (24.8, 0.05)],
                        green, ax, f.bottom(26) + 0.4, squash=0.72)
    fin = jet_fin("fin", ax, [(4.0, 0.6), (13.7, 0.6), (13.9, 1.4), (13.3, 4.4), (12.2, 4.6), (7.0, 1.9)], green,
                  thickness=1.2)
    w.sphere("canopy", (ax, f.Y(17.4), 1.65), (1.4, 2.4, 1.2), glass, 20, 10)
    w.sphere("glint", (ax - 0.3, f.Y(16.6), 2.65), (0.4, 0.7, 0.2), glint, 10, 5)
    for obj in plate:
        s.paint_sprite(obj, J53_PAINT, p, wall_steps=2, under=dark, probe=0.4, blur=1)
    s.paint_sprite(body, J53_PAINT, p, wall_steps=1, under=dark, blur=1)
    s.paint_sprite(fin, f, p, wall_steps=1, under=dark)
    n.merge_by_material()


s.run()
