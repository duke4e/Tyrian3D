"""The store's illustration of the ship in 3D (batch AU, part front_guns): the guns on the ship's FRONT mount,
one model per weapon picture (the store's weapon shapes), named store_gun_<weapon sprite>.

Units are the store screen's pixels (pixel column c, row r of a w x h picture is x = c - w / 2 .. c + 1 - w / 2,
y = h / 2 - r - 1 .. h / 2 - r); X right, +Y up the screen (the ship's nose), Z up. Each model's origin is
the centre of its picture (the store draws it at x + w / 2, y + h / 2), its base at z = 0: the game puts it on
the ship's deck (z 12), so its model line takes `origin`. The colours are the pictures' (the store's palette is
fixed: explicit RGB materials, not palette ones); lamps and energy chambers glow.

- store_gun_0 (33 x 34): Pulse-Cannon, Mega Pulse, Hyper Pulse, HotDog Front, Needle Laser, Pretzel Missile
  and the specials: two pairs of faceted barrels with chisel tips leaning outwards, on a shoulder bar with a
  raised head between them, a two-legged breech block behind with a brass breech in its channel.
- store_gun_1 (51 x 46): Multi-Cannon (front), Guided Bombs, RetroBall, Dragon Frost/Flame, People Pretzels:
  a ribbed drum on a stem up front, four bores in its face, two sleeved barrels angled out to the sides, a
  chevron body and a rounded tail.
- store_gun_2 (46 x 44): Mega Cannon, Banana Blast, Sonic Impulse: a grey frame round a big cut red crystal
  with a glowing table, a glowing red rail across its front behind a grey lip, and a toothed jaw behind.
- store_gun_3 (32 x 27): Laser: twin barrels with blue glass chambers in grey cages, muzzle caps up front,
  a bridge between them and a body with side plates behind.
- store_gun_4 (22 x 39): Zica Laser: a single barrel, its glowing orange chamber between grey rails, on a
  body with a red lamp.
- store_gun_5 (52 x 47): Protron Z, Wild Ball (front and rear): a blue glass energy capsule between two
  shell halves with pointed tips, a sickle blade on each side, small blue lamps on the base.
- store_gun_6 (48 x 53): Vulcan Cannon: an eight-barrel rotary cannon (muzzle clamp, rear ring, hub) on a
  motor housing and body with four red lamps, a curved blade sweeping back on each side.
- store_gun_7 (22 x 28): Lightning Cannon: a dark blue glass dome with glowing lightning arcs over it, in a
  grey cradle, a collar and three blue pods behind.
- store_gun_14 (36 x 43): Missile Launcher, Heavy Missile Launcher: three brass missiles with cross fins in a
  grey rack.
- store_gun_21 (52 x 47): Protron (front): the Protron Z's shells round a glowing red-orange chamber, thin
  antennae beside them and a horseshoe hoop round the base.

usage: Blender -b --factory-startup -P au_front_guns.py -- [--only 0,1,...] [--preview <dir>]
       [--check <dir with weapon_<n>.png>] [--ship <option_31.png>] [--deck 1] [--stats 1]
--check prints the top view's overlap with the picture's outline; --preview renders the top, store, 3/4 and
side views, or with --ship the gun on the USP Talon's picture where the store draws it.
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
import tyrkit as k  # noqa: E402

ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
OUT = os.path.join(ROOT, "assets", "models", "store")

# The weapon pictures' sizes (store.json "sprites"/"weapon").
SIZES = {0: (33, 34), 1: (51, 46), 2: (46, 44), 3: (32, 27), 4: (22, 39), 5: (52, 47), 6: (48, 53), 7: (22, 28),
         14: (36, 43), 21: (52, 47)}


# --- Materials -------------------------------------------------------------------------------------------------

def materials():
    """The guns' materials: the pictures' greys as steel, dark recesses, brass, glowing red, orange and blue."""
    m = {}
    m["steel"] = k.material("gun_steel", (150, 153, 150), metallic=0.55, roughness=0.3)
    m["light"] = k.material("gun_steel_light", (186, 188, 186), metallic=0.55, roughness=0.26)
    m["mid"] = k.material("gun_steel_mid", (121, 123, 121), metallic=0.5, roughness=0.34)
    m["dark"] = k.material("gun_steel_dark", (88, 90, 88), metallic=0.5, roughness=0.4)
    m["gunmetal"] = k.material("gun_gunmetal", (62, 63, 64), metallic=0.5, roughness=0.42)
    m["black"] = k.material("gun_black", (26, 26, 28), metallic=0.2, roughness=0.6)
    m["brass"] = k.material("gun_brass", (196, 172, 124), metallic=0.5, roughness=0.3)
    m["brass_dark"] = k.material("gun_brass_dark", (142, 116, 70), metallic=0.5, roughness=0.36)
    m["red"] = k.material("gun_red_glow", (190, 20, 0), roughness=0.22, emission=(200, 24, 0), emission_strength=0.7)
    m["red_deep"] = k.material("gun_red_deep", (120, 6, 0), roughness=0.15, emission=(150, 8, 0),
                               emission_strength=0.45)
    m["orange"] = k.material("gun_orange_glow", (230, 90, 10), roughness=0.22, emission=(240, 100, 12),
                             emission_strength=0.9)
    m["yellow"] = k.material("gun_yellow_glow", (250, 190, 50), roughness=0.22, emission=(255, 180, 40),
                             emission_strength=1.2)
    m["lamp_red"] = k.material("gun_lamp_red", (220, 30, 8), roughness=0.2, emission=(255, 40, 8),
                               emission_strength=2.0)
    m["blue"] = k.material("gun_blue_glass", (52, 98, 132), metallic=0.1, roughness=0.08, emission=(40, 110, 190),
                           emission_strength=0.35)
    m["blue_deep"] = k.material("gun_blue_deep", (22, 56, 86), metallic=0.1, roughness=0.08, emission=(20, 70, 140),
                                emission_strength=0.3)
    m["blue_light"] = k.material("gun_blue_light", (140, 190, 225), roughness=0.1, emission=(120, 200, 255),
                                 emission_strength=1.6)
    return m


# --- Parts -----------------------------------------------------------------------------------------------------

def lathe_axis(name, profile, mat, start, direction, segments=24, squash=1.0, smooth_angle=50, up=(0, 0, 1)):
    """A turned part along any axis: profile is (t, radius) pairs in increasing t along `direction` from
    `start`; squash scales the cross-sections towards `up`."""
    obj = k.lathe(name, profile, mat, segments=segments, squash=squash)
    d = Vector(direction).normalized()
    upv = Vector(up)
    side = d.cross(upv)
    if side.length < 1e-6:
        side = d.cross(Vector((1, 0, 0)))
    side.normalize()
    upv = side.cross(d).normalized()
    rot = Matrix(((side.x, d.x, upv.x, 0), (side.y, d.y, upv.y, 0), (side.z, d.z, upv.z, 0), (0, 0, 0, 1)))
    obj.data.transform(Matrix.Translation(Vector(start)) @ rot)
    k.recalc_normals(obj)
    if smooth_angle:
        k.smooth(obj, smooth_angle)
    return obj


def tube(name, points, radius, mat, segments=12, smooth_angle=60, squash=1.0):
    """A round tube through 3D points with rounded ends; radius a number or one per point."""
    pts = [Vector(p) for p in points]
    radii = radius if isinstance(radius, (list, tuple)) else [radius] * len(pts)
    rings = []
    for i, p in enumerate(pts):
        a, b = pts[max(i - 1, 0)], pts[min(i + 1, len(pts) - 1)]
        tangent = (b - a).normalized()
        side = tangent.cross(Vector((0, 0, 1)))
        if side.length < 1e-6:
            side = tangent.cross(Vector((1, 0, 0)))
        side.normalize()
        up = side.cross(tangent).normalized()
        rings.append([p + (side * math.cos(2 * math.pi * j / segments) +
                           up * math.sin(2 * math.pi * j / segments) * squash) * radii[i] for j in range(segments)])
    t0, t1 = (pts[1] - pts[0]).normalized(), (pts[-1] - pts[-2]).normalized()
    obj = k.loft(name, rings, mat, start_point=pts[0] - t0 * radii[0] * 0.5, end_point=pts[-1] + t1 * radii[-1] * 0.5)
    return k.smooth(obj, smooth_angle)


def catmull(points, step=0.5):
    """A smooth path through 3D points, sampled about every step."""
    pts = [Vector(p) for p in points]
    out = []
    for i in range(len(pts) - 1):
        p0, p1, p2, p3 = pts[max(i - 1, 0)], pts[i], pts[i + 1], pts[min(i + 2, len(pts) - 1)]
        count = max(1, int(math.ceil((p2 - p1).length / step)))
        for j in range(count):
            t = j / count
            t2, t3 = t * t, t * t * t
            out.append(0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 +
                              (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(pts[-1])
    return out


def block(name, centre, half_w, half_d, height, mat, taper=0.0, rounding=1.0, power=4.0, segments=28, z0=0.0,
          dome=0.0, smooth_angle=45):
    """A block standing on z0 at centre (x, y): rounded corners (a superellipse of `power` in plan), its
    sides leaning in by `taper` from bottom to top, its top edge rounded over `rounding` and its top
    bulging by `dome`."""
    cx, cy = centre

    def rect(z, hw, hd):
        pts = []
        for i in range(segments):
            a = 2 * math.pi * i / segments
            c, s = math.cos(a), math.sin(a)
            pts.append(Vector((cx + math.copysign(abs(c) ** (2 / power), c) * hw,
                               cy + math.copysign(abs(s) ** (2 / power), s) * hd, z)))
        return pts
    rings = [rect(z0, half_w, half_d)]
    side_top = height - rounding
    rings.append(rect(z0 + side_top * 0.5, half_w - taper * 0.5 * side_top / height,
                      half_d - taper * 0.5 * side_top / height))
    for i in range(0, 6):
        a = math.radians(90 * i / 5)
        shrink = taper * (side_top / height) + rounding * (1 - math.cos(a))
        rings.append(rect(z0 + side_top + rounding * math.sin(a) + dome * 0.2 * (i / 5) ** 2,
                          half_w - shrink, half_d - shrink))
    inner = (half_w - taper - rounding, half_d - taper - rounding)
    for j in (0.66, 0.33):
        rings.append(rect(z0 + height + dome * (1 - j * j), inner[0] * j, inner[1] * j))
    obj = k.loft(name, rings, mat, start_point=(cx, cy, z0), end_point=(cx, cy, z0 + height + dome))
    return k.smooth(obj, smooth_angle)


def rbox(name, x0, y0, x1, y1, z0, z1, mat, bevel=0.4, segments=2, smooth_angle=35):
    """A box between two corners, its edges bevelled."""
    obj = k.box(name, ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), (abs(x1 - x0), abs(y1 - y0), abs(z1 - z0)), mat)
    if bevel:
        k.bevel(obj, bevel, segments)
    return k.smooth(obj, smooth_angle)


def ccw(points):
    area = sum(points[i][0] * points[(i + 1) % len(points)][1] - points[(i + 1) % len(points)][0] * points[i][1]
               for i in range(len(points)))
    return points if area > 0 else points[::-1]


def plate(name, outline, z0, z1, mat, bevel=0.0, segments=2, smooth_angle=35):
    """A flat part from an outline [(x, y), ...] (either winding), from z0 to z1."""
    obj = k.slab(name, ccw(list(outline)), z0, z1, mat, bevel_width=bevel, bevel_segments=segments)
    return k.smooth(obj, smooth_angle)


def side_plate(name, outline_yz, x0, x1, mat, bevel=0.0, segments=2, smooth_angle=35):
    """A flat part drawn in the side view: outline [(y, z), ...], from x0 to x1."""
    obj = k.slab(name, ccw(list(outline_yz)), x0, x1, mat, bevel_width=bevel, bevel_segments=segments)
    # (y, z, x) -> (x, y, z): new x = old z, new y = old x, new z = old y.
    obj.data.transform(Matrix(((0, 0, 1, 0), (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 0, 1))))
    return k.smooth(obj, smooth_angle)


def housing(name, stations, mat, segments=32, power=2.0, smooth_angle=50, cap_start=True, cap_end=True):
    """A hull lofted along +Y through stations (y, x, z, half width, half height above, half height below
    [, power]): cross-sections are superellipses centred at (x, z)."""
    rings = []
    for st in stations:
        y, x, z, hw, top, bottom = st[:6]
        pw = st[6] if len(st) > 6 else power
        rings.append(k.ring(y, hw, 1.0, segments, z=z, x=x, top=top, bottom=bottom, power=pw))
    obj = k.loft(name, rings, mat, cap_start=cap_start, cap_end=cap_end)
    return k.smooth(obj, smooth_angle)


def chisel_barrel(name, cx, y0, y_tip0, y_tip, r, axis_z, mat, outer, segments=8, squash=1.0, smooth_angle=0,
                  lean=0.8, apex=0.12):
    """A faceted barrel along +Y from y0, its front cut into a chisel point leaning to the outer side
    (outer = -1: left, +1: right): from y_tip0 to y_tip the section shrinks and slides outwards."""
    rings = []
    rings.append(k.ring(y0, r, r * squash, segments, z=axis_z, x=cx))
    rings.append(k.ring(y_tip0, r, r * squash, segments, z=axis_z, x=cx))
    steps = 6
    for i in range(1, steps + 1):
        t = i / steps
        f = 1 - t * (1 - apex)
        shift = outer * r * lean * t
        rings.append(k.ring(y_tip0 + (y_tip - y_tip0) * t ** 0.9, r * f, r * squash * f, segments, z=axis_z,
                            x=cx + shift))
    obj = k.loft(name, rings, mat)
    if smooth_angle:
        k.smooth(obj, smooth_angle)
    return obj


def cone(name, base, tip, radius, mat, segments=12, tip_radius=0.1, smooth_angle=50):
    d = Vector(tip) - Vector(base)
    return lathe_axis(name, [(0.0, radius), (d.length, tip_radius)], mat, base, d, segments, smooth_angle=smooth_angle)


def lamp(name, centre, radius, mat, rim_mat=None, height=0.9, segments=12):
    """A round lamp lens, set in a rim, its top at centre's z + height."""
    x, y, z = centre
    objs = []
    if rim_mat is not None:
        objs.append(k.smooth(lathe_axis(name + "_rim", [(0.0, radius + 0.55), (height * 0.6, radius + 0.45),
                                                        (height * 0.65, radius)],
                                        rim_mat, (x, y, z), (0, 0, 1), segments, up=(0, 1, 0)), 40))
    objs.append(k.smooth(floor(k.ellipsoid(name, (x, y, z + height * 0.35), (radius, radius, height * 0.75), mat,
                                           segments, 6), z), 70))
    return objs


def bend(obj, fn):
    """Moves each vertex up by fn(x, y) (bends a flat part)."""
    for v in obj.data.vertices:
        v.co.z += fn(v.co.x, v.co.y)
    obj.data.update()
    return obj


def floor(obj, z=0.0):
    """Flattens whatever of a part reaches below z onto z (a flat bottom where it sits on the deck)."""
    for v in obj.data.vertices:
        v.co.z = max(v.co.z, z)
    obj.data.update()
    return obj


def gem(name, centre, levels, mat, table_mat=None, segments=12):
    """A cut gem: rings (z, half width, half depth) from the bottom up, each turned half a facet from the
    one below; the top ring is the table, its own part (table_mat) when given."""
    cx, cy = centre
    verts, faces = [], []
    for i, (z, rx, ry) in enumerate(levels):
        off = math.pi / segments * (i % 2)
        for j in range(segments):
            a = 2 * math.pi * j / segments + off
            verts.append((cx + rx * math.cos(a), cy + ry * math.sin(a), z))
    n = segments
    for i in range(len(levels) - 1):
        for j in range(n):
            a, b = i * n + j, i * n + (j + 1) % n
            c, d = (i + 1) * n + j, (i + 1) * n + (j + 1) % n
            if i % 2 == 0:
                faces += [(a, b, c), (b, d, c)]
            else:
                faces += [(a, b, d), (a, d, c)]
    faces.append(tuple(range(n - 1, -1, -1)))
    top = len(levels) - 1
    faces.append(tuple(top * n + j for j in range(n)))
    obj = k.mesh_object(name, verts, faces, mat)
    k.recalc_normals(obj)
    if table_mat is not None:
        z, rx, ry = levels[-1]
        off = math.pi / segments * (top % 2)
        outline = [(cx + rx * 0.999 * math.cos(2 * math.pi * j / n + off),
                    cy + ry * 0.999 * math.sin(2 * math.pi * j / n + off)) for j in range(n)]
        plate(name + "_table", outline, z - 0.4, z + 0.12, table_mat, smooth_angle=0)
    return obj


def on_ellipsoid(centre, radii, x, y, lift=0.0):
    """The point of an ellipsoid's upper half above (x, y), lifted along z."""
    cx, cy, cz = centre
    rx, ry, rz = radii
    q = 1.0 - ((x - cx) / rx) ** 2 - ((y - cy) / ry) ** 2
    return (x, y, cz + rz * math.sqrt(max(q, 0.0)) + lift)


# --- Gun 0: Pulse-Cannon (33 x 34) ----------------------------------------------------------------------------

def gun_0(m):
    # The breech block behind: two angular legs either side of a channel; in the channel the brass breech,
    # braced by a V of bright struts meeting behind it, and a tail block.
    for side in (-1, 1):
        sx = side
        outline = [(sx * 3.4, -17.0), (sx * 10.5, -17.0), (sx * 10.5, -6.0), (sx * 9.4, -4.6), (sx * 3.4, -4.6)]
        plate(f"leg_{side}", outline, 0.0, 4.4, m["mid"], bevel=0.6)
        # Its top: a raised plate with a vent of slots, the back notched (the picture's dark gaps, row 32).
        plate(f"leg_top_{side}", [(sx * 4.4, -15.0), (sx * 9.6, -15.0), (sx * 9.6, -7.0), (sx * 8.6, -6.0),
                                   (sx * 4.4, -6.0)], 4.0, 5.0, m["steel"], bevel=0.35)
        for i in range(3):
            y = -8.2 - i * 1.7
            rbox(f"leg_vent_{side}_{i}", sx * 7.1 - 1.9, y - 0.35, sx * 7.1 + 1.9, y + 0.35, 4.6, 5.15,
                 m["black"], 0.1)
        rbox(f"leg_notch_{side}", sx * 5.6 - 0.8, -17.2, sx * 5.6 + 0.8, -15.4, 1.2, 3.9, m["black"], 0.15)
        # The V's strut, from the shoulder's back corner to behind the breech.
        tube(f"strut_{side}", [(sx * 5.2, -4.0, 3.6), (sx * 1.0, -12.6, 3.2)], 0.75, m["light"], 8)
    rbox("channel", -3.6, -17.0, 3.6, -4.5, 0.0, 2.0, m["gunmetal"], 0.3)
    lathe_axis("breech", [(-11.6, 1.2), (-11.2, 2.1), (-5.6, 2.1), (-5.0, 1.7), (-4.0, 1.7)], m["brass"],
               (0.0, 0.0, 2.6), (0, 1, 0), 20, up=(0, 0, 1))
    lathe_axis("breech_band", [(0.0, 2.3), (0.8, 2.3)], m["brass_dark"], (0.0, -9.6, 2.6), (0, 1, 0), 20)
    side_plate("tail", [(-17.0, 0.0), (-12.4, 0.0), (-12.4, 3.4), (-13.6, 4.2), (-17.0, 4.2)], -2.6, 2.6,
               m["steel"], bevel=0.4)

    # The shoulder: a low bar, and round housings the barrels come out of.
    block("shoulder", (0.0, -0.6), 15.0, 4.2, 3.8, m["dark"], taper=0.4, rounding=1.0, power=4.0)
    for side in (-1, 1):
        x, ox = side * 7.5, side * 13.9
        kn = housing(f"knuckle_{side}", [(-4.6, x, 4.2, 3.4, 3.0, 3.0), (-4.0, x, 4.2, 4.8, 4.2, 4.2),
                                         (3.4, x, 4.2, 4.8, 4.2, 4.2), (4.0, x, 4.2, 4.4, 3.9, 3.9)],
                     m["steel"], segments=8, smooth_angle=0)
        k.bevel(kn, 0.2, 1)
        kn = housing(f"knuckle_out_{side}", [(-4.4, ox, 3.0, 2.2, 2.2, 2.2), (-3.8, ox, 3.0, 3.0, 3.0, 3.0),
                                             (3.8, ox, 3.0, 3.0, 3.0, 3.0), (4.4, ox, 3.0, 2.7, 2.7, 2.7)],
                     m["steel"], segments=8, smooth_angle=0)
        k.bevel(kn, 0.15, 1)
    # The raised head between the inner barrels, its front leaning back with a dark port.
    side_plate("head", [(-5.0, 0.0), (3.0, 0.0), (3.0, 4.4), (1.4, 6.8), (-5.0, 6.8)], -3.4, 3.4, m["light"],
               bevel=0.5)
    rbox("head_slot", -1.5, 1.7, 1.5, 2.6, 4.4, 6.0, m["black"], 0.2)
    rbox("head_ridge", -0.6, -4.6, 0.6, 1.2, 6.5, 7.4, m["mid"], 0.25)

    # The inner barrels: faceted, chisel tips leaning out; a dark collar where they leave the housing.
    for side in (-1, 1):
        cx = side * 7.5
        b = chisel_barrel(f"barrel_{side}", cx, -3.0, 11.5, 16.4, 3.8, 4.2, m["light"], side, segments=8,
                          squash=0.88, lean=0.85)
        k.bevel(b, 0.15, 1)
        lathe_axis(f"collar_{side}", [(0.0, 4.15), (1.2, 4.15)], m["gunmetal"], (cx, 4.0, 4.2), (0, 1, 0), 8,
                   squash=0.88, smooth_angle=0)
        # A dark groove along the barrel's top facet.
        rbox(f"barrel_groove_{side}", cx - 0.45, 6.0, cx + 0.45, 10.6, 7.25, 7.7, m["gunmetal"], 0.1)
        # The outer spikes: thinner, their tips at the picture's corners.
        ox = side * 14.0
        s = chisel_barrel(f"spike_{side}", ox, -3.6, 9.5, 17.0, 2.35, 3.0, m["steel"], side, segments=8,
                          squash=1.0, lean=0.95, apex=0.06)
        k.bevel(s, 0.12, 1)
        lathe_axis(f"spike_collar_{side}", [(0.0, 2.7), (1.0, 2.7)], m["gunmetal"], (ox, 4.4, 3.0), (0, 1, 0), 8,
                   smooth_angle=0)


# --- Gun 1: Multi-Cannon (51 x 46) ----------------------------------------------------------------------------

def gun_1(m):
    axis = 4.6
    # The drum up front: ribbed, its front a flat face with four bores round a hub; a groove and two rings.
    drum = [(9.2, 4.4), (9.8, 6.2), (10.5, 7.1), (11.3, 7.3), (11.7, 6.8), (13.5, 6.8), (13.9, 7.3), (17.3, 7.3),
            (17.7, 7.7), (18.7, 7.7), (19.1, 7.2), (20.6, 6.8), (21.8, 6.0), (22.5, 5.0), (22.8, 4.4), (22.8, 0.01)]
    lathe_axis("drum", drum, m["light"], (0.0, 0.0, axis), (0, 1, 0), 32, squash=0.6)
    lathe_axis("drum_groove", [(11.6, 6.95), (13.6, 6.95)], m["gunmetal"], (0.0, 0.0, axis), (0, 1, 0), 32,
               squash=0.6)
    lathe_axis("drum_face", [(0.0, 3.9), (0.3, 3.9)], m["dark"], (0.0, 22.65, axis), (0, 1, 0), 24, squash=0.6)
    lathe_axis("drum_hub", [(0.0, 1.0), (0.6, 1.0), (0.9, 0.6)], m["steel"], (0.0, 22.8, axis), (0, 1, 0), 12)
    for bx, bz in ((-2.2, 1.0), (2.2, 1.0), (-2.2, -1.0), (2.2, -1.0)):
        lathe_axis(f"drum_bore_{bx}_{bz}", [(0.0, 0.85), (0.4, 0.85)], m["black"], (bx, 22.75, axis + bz),
                   (0, 1, 0), 10)
    # The neck and the stem behind it, on the body.
    lathe_axis("neck", [(0.0, 3.4), (0.6, 2.7), (4.8, 2.7), (5.4, 3.3)], m["steel"], (0.0, 4.6, axis), (0, 1, 0), 20,
               squash=0.9)
    lathe_axis("stem", [(0.0, 2.6), (0.8, 3.6), (1.4, 4.0), (14.2, 4.0), (15.0, 3.4), (15.6, 2.6)], m["steel"],
               (0.0, -10.4, axis), (0, 1, 0), 24, squash=0.9)
    for y in (-4.0, 1.6):
        lathe_axis(f"stem_band_{y}", [(0.0, 4.2), (0.9, 4.2)], m["dark"], (0.0, y, axis), (0, 1, 0), 24, squash=0.9)
    # The body: a chevron plate under the barrels' roots, a raised panel on it.
    body = [(-10.5, -0.5), (10.5, -0.5), (15.0, -5.0), (9.5, -15.5), (-9.5, -15.5), (-15.0, -5.0)]
    plate("body", body, 0.0, 4.4, m["mid"], bevel=1.0)
    plate("body_panel", [(-8.6, -2.0), (8.6, -2.0), (12.0, -5.4), (8.2, -13.6), (-8.2, -13.6), (-12.0, -5.4)],
          4.0, 4.9, m["steel"], bevel=0.4)
    # The barrels, angled out to the sides: a sleeve at the muzzle, a dark bore.
    for side in (-1, 1):
        root = Vector((side * 7.6, -8.4, axis))
        tip = Vector((side * 23.6, 6.8, axis))
        d = (tip - root).normalized()
        length = (tip - root).length
        lathe_axis(f"barrel_{side}", [(0.0, 3.2), (length - 6.4, 3.2), (length - 6.2, 4.0), (length - 5.8, 4.3),
                                      (length - 0.7, 4.3), (length - 0.3, 3.9), (length, 2.2)],
                   m["light"], root, d, 24, squash=0.95)
        lathe_axis(f"barrel_ring_{side}", [(0.0, 4.5), (1.0, 4.5)], m["dark"], root + d * (length - 4.6), d, 24,
                   squash=0.95)
        lathe_axis(f"barrel_bore_{side}", [(0.0, 1.7), (0.6, 1.7)], m["black"], root + d * (length - 0.4), d, 16)
        lathe_axis(f"barrel_root_{side}", [(0.0, 4.4), (5.0, 4.4), (5.8, 3.6)], m["steel"], root + d * 1.0, d, 24,
                   squash=0.95)
        lathe_axis(f"barrel_root_ring_{side}", [(0.0, 4.6), (0.8, 4.6)], m["gunmetal"], root + d * 3.2, d, 24,
                   squash=0.95)
    # The tail: a rounded can behind, a bright collar where it meets the body.
    lathe_axis("tail", [(0.0, 4.6), (0.4, 5.3), (1.4, 5.3), (1.8, 4.9), (6.0, 4.9), (7.2, 4.3), (8.0, 3.0),
                        (8.5, 1.0)], m["steel"], (0.0, -14.4, 3.7), (0, -1, 0), 28, squash=0.72)
    lathe_axis("tail_band", [(0.0, 5.05), (0.7, 5.05)], m["dark"], (0.0, -18.6, 3.7), (0, -1, 0), 28, squash=0.72)


# --- Gun 2: Mega Cannon (46 x 44) -----------------------------------------------------------------------------

def gun_2(m):
    # The frame: a pillar either side (a tall inner part and a lower outer step with grooves), a bar across.
    for side in (-1, 1):
        s = side
        plate(f"pillar_{side}", [(s * 13.0, 15.6), (s * 19.4, 15.6), (s * 20.0, 14.6), (s * 20.0, -9.6),
                                 (s * 19.0, -11.0), (s * 13.0, -11.0)], 0.0, 7.4, m["steel"], bevel=1.1)
        plate(f"pillar_step_{side}", [(s * 18.0, 13.6), (s * 21.2, 13.6), (s * 22.8, 12.0), (s * 22.8, -8.0),
                                      (s * 21.2, -9.6), (s * 18.0, -9.6)], 0.0, 4.8, m["mid"], bevel=0.8)
        for gx in (20.4, 21.8):
            rbox(f"pillar_groove_{side}_{gx}", s * gx - 0.3, -6.5, s * gx + 0.3, 10.5, 4.3, 5.0, m["black"], 0.1)
        # The rail's collar where it enters the pillar.
        lathe_axis(f"rail_collar_{side}", [(0.0, 3.9), (1.6, 3.9)], m["dark"], (s * 13.6, 15.5, 4.4),
                   (-s, 0, 0), 20, squash=0.92)
    rbox("bar", -21.0, 9.0, 21.0, 11.6, 0.0, 6.4, m["light"], 0.8)
    # The glowing rail across the front, a hot line along its top, the grey lip in front of it.
    lathe_axis("rail", [(0.0, 3.4), (30.0, 3.4)], m["red"], (-15.0, 15.5, 4.4), (1, 0, 0), 24, squash=0.92)
    lathe_axis("rail_core", [(0.0, 0.7), (26.0, 0.7)], m["yellow"], (-13.0, 15.0, 7.25), (1, 0, 0), 10, squash=0.7)
    rbox("lip", -11.5, 18.6, 12.0, 21.4, 0.0, 5.8, m["light"], 1.1)
    rbox("nub", -3.6, 20.6, 5.6, 22.0, 0.6, 4.4, m["steel"], 0.5)
    # The big red crystal in the frame, a hot core in it.
    gem("crystal", (0.3, -0.8), [(0.0, 10.6, 8.0), (3.0, 12.8, 9.8), (5.6, 10.2, 7.8), (7.2, 6.4, 5.0)], m["red_deep"],
        m["orange"])
    # The toothed jaw behind.
    jaw = [(-22.0, -10.6), (22.5, -10.6), (22.5, -13.6), (20.5, -16.6), (17.5, -19.6), (10.0, -21.6),
           (-9.0, -21.6), (-16.5, -19.6), (-19.5, -16.6), (-22.0, -13.6)]
    plate("jaw", jaw, 0.0, 3.6, m["steel"], bevel=0.9)
    for x, tip in ((-18.0, (-21.0, -17.0)), (-11.0, (-13.0, -20.5)), (-4.0, (-4.5, -21.6)), (4.8, (5.3, -21.6)),
                   (11.8, (13.8, -20.5)), (18.8, (21.6, -17.0))):
        cone(f"tooth_{x}", (x, -11.0, 3.4), (tip[0], tip[1], 2.2), 3.4, m["light"], segments=4, tip_radius=0.15,
             smooth_angle=0)


# --- Gun 3: Laser (32 x 27) -----------------------------------------------------------------------------------

def gun_3(m):
    x0, axis, squash = 0.5, 4.6, 0.7
    for side in (-1, 1):
        cx = x0 + side * 8.0
        # The muzzle cap, a dark bore in its rounded front.
        lathe_axis(f"cap_{side}", [(0.0, 2.6), (0.4, 4.4), (1.2, 5.3), (3.6, 5.5), (3.8, 6.3), (5.6, 6.3), (6.0, 5.2)],
                   m["light"], (cx, 13.5, axis), (0, -1, 0), 28, squash=squash)
        lathe_axis(f"bore_{side}", [(0.0, 1.7), (0.7, 1.7)], m["black"], (cx, 13.8, axis), (0, -1, 0), 16,
                   squash=0.8)
        # The blue glass chamber behind it, in a cage: rings and side rails.
        lathe_axis(f"chamber_{side}", [(0.0, 4.4), (10.6, 4.4)], m["blue"], (cx, 7.6, axis), (0, -1, 0), 24,
                   squash=squash)
        for y in (2.4, -2.6):
            lathe_axis(f"cage_ring_{side}_{y}", [(0.0, 4.8), (0.9, 4.8)], m["dark"], (cx, y + 0.45, axis),
                       (0, -1, 0), 24, squash=squash)
        for rx in (-1, 1):
            tube(f"cage_rail_{side}_{rx}", [(cx + rx * 4.75, 7.6, axis + 0.8), (cx + rx * 4.75, -3.0, axis + 0.8)],
                 0.6, m["steel"], 8)
    # The bridge between the barrels.
    rbox("bridge", -2.6, -3.0, 3.6, 0.8, 1.8, 6.2, m["light"], 0.6)
    # The body behind: side plate on the left, a vent on the right, a raised spine.
    body = [(-14.5, -2.4), (15.5, -2.4), (15.5, -9.0), (13.0, -12.0), (10.0, -13.5), (-9.0, -13.5), (-12.0, -12.0),
            (-14.5, -9.0)]
    plate("body", body, 0.0, 4.2, m["mid"], bevel=0.8)
    plate("side_plate", [(-14.0, -3.4), (-5.2, -3.4), (-4.4, -4.4), (-4.4, -8.8), (-14.0, -8.8)], 3.8, 5.2,
          m["light"], bevel=0.35)
    for i in range(4):
        y = -5.6 - i * 1.3
        rbox(f"vent_{i}", 6.8, y - 0.35, 13.6, y + 0.35, 3.9, 4.35, m["black"], 0.1)
    block("spine", (x0, -8.2), 3.4, 5.6, 6.2, m["steel"], taper=0.4, rounding=1.2, power=4.0)
    rbox("spine_slot", x0 - 0.5, -11.0, x0 + 0.5, -5.0, 5.9, 6.4, m["black"], 0.1)


# --- Gun 4: Zica Laser (22 x 39) ------------------------------------------------------------------------------

def gun_4(m):
    x0, axis, squash = 0.5, 4.8, 0.75
    # The muzzle cap, a dark bore in front.
    lathe_axis("cap", [(0.0, 2.4), (0.4, 4.0), (1.0, 4.6), (2.6, 4.6), (2.8, 5.2), (6.6, 5.2), (7.0, 6.0),
                       (9.0, 6.0), (9.2, 5.0)], m["light"], (x0, 19.5, axis), (0, -1, 0), 28, squash=squash)
    lathe_axis("cap_band", [(0.0, 5.4), (0.6, 5.4)], m["dark"], (x0, 16.4, axis), (0, -1, 0), 28, squash=squash)
    lathe_axis("bore", [(0.0, 1.6), (0.7, 1.6)], m["black"], (x0, 19.8, axis), (0, -1, 0), 16, squash=0.85)
    # The glowing chamber between grey rails, dark rings across it.
    lathe_axis("chamber", [(0.0, 3.7), (12.2, 3.7)], m["orange"], (x0, 10.6, axis), (0, -1, 0), 24, squash=squash)
    for y in (6.4, 2.4):
        lathe_axis(f"chamber_ring_{y}", [(0.0, 4.0), (0.8, 4.0)], m["dark"], (x0, y, axis), (0, -1, 0), 24,
                   squash=squash)
    for side in (-1, 1):
        tube(f"rail_{side}", [(x0 + side * 4.9, 10.8, axis), (x0 + side * 4.9, -1.6, axis)], 1.1, m["steel"], 10)
    # The body: a collar across its front, a raised deck with a red lamp, pods on its sides.
    body = [(x0 - 7.5, 2.2), (x0 + 7.5, 2.2), (x0 + 10.5, -1.5), (x0 + 10.5, -17.0), (x0 + 8.5, -19.5),
            (x0 - 8.5, -19.5), (x0 - 10.5, -17.0), (x0 - 10.5, -1.5)]
    plate("body", body, 0.0, 4.0, m["mid"], bevel=0.8)
    rbox("collar", x0 - 7.4, -3.6, x0 + 7.4, -1.0, 0.0, 6.8, m["light"], 0.7)
    block("deck", (x0, -10.4), 5.0, 6.4, 5.6, m["steel"], taper=0.5, rounding=1.0, power=4.0)
    lamp("lamp", (x0, -7.2, 5.4), 2.1, m["lamp_red"], m["dark"], 1.0)
    for i in range(3):
        y = -12.0 - i * 1.4
        rbox(f"deck_vent_{i}", x0 - 2.8, y - 0.3, x0 + 2.8, y + 0.3, 5.3, 5.75, m["black"], 0.1)
    for side in (-1, 1):
        px = x0 + side * 8.0
        lathe_axis(f"pod_{side}", [(0.0, 1.4), (0.8, 2.4), (14.2, 2.4), (15.0, 1.4)], m["light"], (px, -3.0, 4.0),
                   (0, -1, 0), 20, squash=1.0)
        lamp(f"pod_lamp_{side}", (px, -12.2, 6.0), 0.75, m["lamp_red"], None, 0.6, 10)


# --- Gun 7: Lightning Cannon (22 x 28) ------------------------------------------------------------------------

def gun_7(m):
    x0 = 0.5
    # The blue crystal dome, lightning arcs over it.
    centre, radii = (x0, 4.6, 0.6), (10.4, 9.4, 7.4)
    k.smooth(floor(k.ellipsoid("dome", centre, radii, m["blue_deep"], 32, 16), 0.0), 60)
    for name, path in (("arc_a", [(-6.0, 11.4), (-3.4, 9.6), (-4.6, 8.4), (-1.6, 6.4), (-3.0, 4.8), (0.6, 2.8),
                                  (-0.6, 1.2), (2.2, -1.6)]),
                       ("arc_b", [(6.2, 10.0), (3.8, 8.0), (5.4, 6.6), (3.0, 4.2), (4.6, 2.6), (3.4, 0.4)]),
                       ("arc_c", [(-8.6, 4.0), (-6.4, 3.0), (-7.2, 1.0), (-5.0, -0.8)])):
        pts = []
        for (ax, ay), (bx, by) in zip(path, path[1:]):  # straight strokes, following the dome
            for t in (0.0, 0.34, 0.67):
                pts.append(on_ellipsoid(centre, radii, x0 + ax + (bx - ax) * t, ay + (by - ay) * t, 0.08))
        pts.append(on_ellipsoid(centre, radii, x0 + path[-1][0], path[-1][1], 0.08))
        tube(name, pts, 0.36, m["blue_light"], 6, smooth_angle=30)
    # The cradle: a base plate, arms either side of the dome, a collar behind it.
    base = [(x0 - 10.5, 1.0), (x0 + 10.5, 1.0), (x0 + 10.5, -12.5), (x0 + 9.0, -14.0), (x0 - 9.0, -14.0),
            (x0 - 10.5, -12.5)]
    plate("base", base, 0.0, 3.4, m["mid"], bevel=0.6)
    for side in (-1, 1):
        rbox(f"arm_{side}", x0 + side * 8.6, -5.0, x0 + side * 10.9, 3.2, 0.0, 6.0, m["light"], 0.6)
    rbox("collar", x0 - 10.4, -5.6, x0 + 10.4, -3.8, 0.0, 5.4, m["light"], 0.6)
    # The blue pods behind, in dark sockets.
    for name, (x, y), r in (("pod_l", (-6.0, -9.6), (3.1, 3.6, 2.6)), ("pod_r", (6.0, -9.6), (3.1, 3.6, 2.6)),
                            ("pod_c", (0.5, -7.6), (2.6, 2.2, 2.4))):
        lathe_axis(name + "_socket", [(0.0, max(r[0], r[1]) + 0.6), (3.9, max(r[0], r[1]) + 0.5)], m["dark"],
                   (x0 + x, y, 0.0), (0, 0, 1), 20, squash=min(r[0], r[1]) / max(r[0], r[1]), up=(0, 1, 0))
        k.smooth(floor(k.ellipsoid(name, (x0 + x, y, 3.4), r, m["blue"], 20, 10), 0.5), 60)


# --- Gun 14: Missile Launcher (36 x 43) -----------------------------------------------------------------------

def missile(name, m, x, y_tail, y_tip, axis, r=2.9):
    length = y_tip - y_tail
    lathe_axis(name, [(0.0, 1.3), (0.6, 2.0), (1.0, r), (length - 6.4, r), (length - 4.2, r * 0.9),
                      (length - 2.2, r * 0.66), (length - 0.8, r * 0.36), (length, 0.0)],
               m["brass"], (x, y_tail, axis), (0, 1, 0), 20)
    for t in (3.6, length - 8.6):
        lathe_axis(f"{name}_band_{t}", [(0.0, r + 0.15), (0.9, r + 0.15)], m["brass_dark"], (x, y_tail + t, axis),
                   (0, 1, 0), 20)
    lathe_axis(f"{name}_nozzle", [(0.0, 1.0), (0.8, 1.5)], m["gunmetal"], (x, y_tail - 0.6, axis), (0, 1, 0), 12)
    # Cross fins at the tail: two flat ones out to the sides, one up.
    for side in (-1, 1):
        plate(f"{name}_fin_{side}", [(x + side * r * 0.8, y_tail + 11.0), (x + side * r * 0.8, y_tail + 0.4),
                                     (x + side * 5.8, y_tail + 0.4), (x + side * 5.8, y_tail + 4.0)],
              axis - 0.35, axis + 0.35, m["brass_dark"], bevel=0.14)
    side_plate(f"{name}_fin_up", [(y_tail + 11.0, axis + r * 0.8), (y_tail + 0.4, axis + r * 0.8),
                                  (y_tail + 0.4, axis + r + 1.8), (y_tail + 4.0, axis + r + 1.8)],
               x - 0.35, x + 0.35, m["brass_dark"], bevel=0.14)


def gun_14(m):
    x0, axis = 0.5, 4.8
    for name, dx, tip, tail in (("left", -12.0, 19.5, -19.6), ("centre", 0.0, 21.5, -20.6),
                                ("right", 12.0, 18.5, -20.6)):
        missile(f"missile_{name}", m, x0 + dx, tail, tip, axis)
    # The rack: a clamp over the missiles' middles, a hump over each, a dark groove across; brackets in front.
    plate("rack", [(x0 - 15.6, 0.6), (x0 + 15.8, 0.6), (x0 + 15.8, -10.4), (x0 - 15.6, -10.4)], 0.0, 8.4, m["steel"],
          bevel=0.9)
    for dx in (-6.0, 6.0):  # the rack's tongues between the missiles' tails
        side_plate(f"rack_tongue_{dx}", [(-19.0, 0.0), (-9.0, 0.0), (-9.0, 5.0), (-13.0, 3.4), (-19.0, 1.6)],
                   x0 + dx - 1.6, x0 + dx + 1.6, m["mid"], bevel=0.4)
    for dx in (-12.0, 0.0, 12.0):
        housing(f"rack_hump_{dx}", [(-10.0, x0 + dx, 8.2, 2.4, 0.6, 0.3), (-9.6, x0 + dx, 8.2, 3.3, 1.0, 0.3),
                                    (0.0, x0 + dx, 8.2, 3.3, 1.0, 0.3), (0.4, x0 + dx, 8.2, 2.4, 0.6, 0.3)],
                m["light"], segments=20, smooth_angle=50)
    rbox("rack_groove", x0 - 15.0, -5.0, x0 + 15.2, -3.8, 8.0, 8.65, m["black"], 0.1)
    for side in (-1, 1):
        cx = x0 + side * 6.0
        side_plate(f"bracket_{side}", [(0.4, 0.0), (5.6, 0.0), (5.6, 1.6), (1.8, 6.6), (0.4, 6.6)],
                   cx - 2.2, cx + 2.2, m["light"], bevel=0.45)


# --- Guns 5 and 21: Protron Z / Wild Ball and Protron (52 x 47) -----------------------------------------------

def protron(m, red):
    """The Protron frame: two shell halves with pointed tips round an energy chamber (blue capsule for 5,
    red-orange column for 21), a base with blue lamps and a tail; sickle blades (5) or antennae and a
    horseshoe hoop (21) at the sides."""
    x0 = 0.5
    for side in (-1, 1):
        s = side
        # The shell: a curved half, its crest near the chamber, its tip pointing up the screen. Stations:
        # (y, distance of the section's middle from the centre line, height, half width).
        stations = [(-9.0, 10.4, 5.0, 5.2), (-6.0, 10.4, 7.6, 5.2), (-2.0, 10.4, 8.4, 5.2), (6.0, 10.4, 8.6, 5.2),
                    (11.5, 10.3, 8.2, 5.1), (15.5, 9.4, 7.4, 4.2), (19.5, 8.4, 6.0, 3.2), (22.0, 7.4, 4.4, 2.2),
                    (23.4, 6.8, 2.8, 1.0), (23.8, 6.6, 1.8, 0.3)]
        housing(f"shell_{side}", [(y, x0 + s * u, 0.0, hw, top, 0.0, 2.3) for y, u, top, hw in stations],
                m["steel"], segments=24, smooth_angle=55)
        # A bright rim along its crest, the inner edge.
        crest = [(x0 + s * 6.4, 22.6, 2.4), (x0 + s * 7.2, 19.0, 5.2), (x0 + s * 7.8, 14.0, 6.9),
                 (x0 + s * 8.0, 6.0, 7.6), (x0 + s * 8.0, -4.0, 7.3)]
        tube(f"shell_rim_{side}", catmull(crest, 2.0), 0.55, m["light"], 8)
        # A seam across the shell.
        housing(f"shell_seam_{side}", [(3.6, x0 + s * 10.4, 0.0, 5.35, 8.75, 0.0, 2.3),
                                       (4.4, x0 + s * 10.4, 0.0, 5.35, 8.75, 0.0, 2.3)], m["gunmetal"], segments=24)
    if not red:
        # The blue capsule between the shells, glowing coils round its front.
        def capsule(y):
            t = (y - 6.7) / 9.9
            f = math.sqrt(max(0.0, 1 - t ** 4))
            return 5.6 * f, 6.4 * f
        ys = [-3.2 + 19.8 * (0.5 - 0.5 * math.cos(math.pi * i / 10)) for i in range(11)]
        housing("capsule", [(y, x0, 0.4, max(capsule(y)[0], 0.3), max(capsule(y)[1], 0.3), 0.0) for y in ys],
                m["blue"], segments=24, smooth_angle=60)
        for i, y in enumerate((14.0, 12.4, 10.8, 4.0)):
            hw, top = capsule(y)
            mat = m["blue_light"] if i < 3 else m["blue_deep"]
            housing(f"coil_{i}", [(y - 0.35, x0, 0.4, hw + 0.25, top + 0.25, 0.0),
                                  (y + 0.35, x0, 0.4, hw + 0.25, top + 0.25, 0.0)], mat, segments=24)
    else:
        # The red column with glowing rings, a hot cross-bar at its front, bright cheeks either side.
        lathe_axis("column", [(0.0, 2.6), (0.6, 3.4), (15.4, 3.4), (16.0, 2.6)], m["red"], (x0, -3.0, 3.7), (0, 1, 0),
                   24, squash=1.0)
        for y in (8.4, 5.6, 2.8, 0.2):
            lathe_axis(f"column_ring_{y}", [(0.0, 3.65), (0.9, 3.65)], m["orange"], (x0, y, 3.7), (0, 1, 0), 24)
        lathe_axis("crossbar", [(0.0, 1.6), (0.5, 2.2), (10.0, 2.2), (10.5, 1.6)], m["yellow"], (x0 - 5.25, 14.6, 4.2),
                   (1, 0, 0), 20)
        housing("crossbar_back", [(11.6, x0, 0.0, 5.4, 4.0, 0.0, 4.0), (13.4, x0, 0.0, 5.4, 4.0, 0.0, 4.0)],
                m["red_deep"], segments=24)
        for side in (-1, 1):
            rbox(f"cheek_{side}", x0 + side * 3.5, 4.0, x0 + side * 5.6, 12.0, 0.0, 6.6, m["light"], 0.5)
    # The base behind: a dark box with a lid in its middle, blue lamps either side, a tail.
    base = [(x0 - 16.5, -2.6), (x0 + 16.5, -2.6), (x0 + 17.6, -4.6), (x0 + 17.6, -16.0), (x0 + 15.6, -18.0),
            (x0 - 15.6, -18.0), (x0 - 17.6, -16.0), (x0 - 17.6, -4.6)]
    plate("base", base, 0.0, 3.8, m["mid"], bevel=0.8)
    rbox("box", x0 - 5.4, -10.2, x0 + 5.4, -3.6, 2.6, 4.8, m["gunmetal"], 0.4)
    rbox("lid", x0 - 3.8, -9.0, x0 + 3.8, -4.6, 4.4, 5.4, m["light"], 0.35)
    for side in (-1, 1):
        lamp(f"lamp_{side}", (x0 + side * 11.0, -12.6, 3.6), 1.7, m["blue_light"], m["dark"], 1.1)
    plate("tail", [(x0 - 10.0, -17.0), (x0 + 10.5, -17.0), (x0 + 9.0, -23.4), (x0 - 8.5, -23.4)], 0.0, 2.8, m["mid"],
          bevel=0.6)
    rbox("tail_rib", x0 - 1.2, -23.0, x0 + 1.2, -17.0, 2.2, 3.5, m["steel"], 0.4)
    if not red:
        # The sickle blades either side, from the base's back corners up to their tips.
        for side in (-1, 1):
            s = side
            path = [(x0 + s * 15.0, -15.6, 2.0), (x0 + s * 19.6, -16.4, 2.6), (x0 + s * 22.8, -12.6, 3.0),
                    (x0 + s * 23.2, -4.0, 3.4), (x0 + s * 22.2, 2.0, 3.8), (x0 + s * 21.0, 5.6, 4.2)]
            pts = catmull(path, 1.6)
            radii = [2.0 + 1.0 * math.sin(math.pi * min(1.0, i / (len(pts) * 0.55))) if i < len(pts) * 0.55 else
                     3.0 * (1 - (i - len(pts) * 0.55) / (len(pts) * 0.45)) + 0.2 for i in range(len(pts))]
            tube(f"sickle_{side}", pts, radii, m["steel"], 10, squash=0.8)
    else:
        for side in (-1, 1):
            s = side
            # A thin antenna beside each shell, on a bracket.
            tube(f"antenna_{side}", [(x0 + s * 18.6, 3.4, 2.6), (x0 + s * 18.0, 11.0, 3.6), (x0 + s * 17.2, 19.6, 4.6)],
                 [1.1, 0.8, 0.12], m["light"], 8)
            rbox(f"antenna_bracket_{side}", x0 + s * 14.6, 6.2, x0 + s * 18.6, 8.6, 0.6, 3.8, m["mid"], 0.4)
        # The horseshoe hoop round the base, from beside one shell round the back to the other.
        half = [(-15.6, -0.6, 3.2), (-20.6, -3.4, 3.0), (-24.0, -9.0, 2.8), (-24.0, -15.4, 2.6), (-20.6, -20.0, 2.4),
                (-11.0, -22.4, 2.2)]
        path = ([(x0 + x, y, z) for x, y, z in half] + [(x0, -22.8, 2.2)] +
                [(x0 - x, y, z) for x, y, z in reversed(half)])
        tube("hoop", catmull(path, 2.0), 2.1, m["steel"], 10, squash=0.85)


def gun_5(m):
    protron(m, red=False)


def gun_21(m):
    protron(m, red=True)


# --- Gun 6: Vulcan Cannon (48 x 53) ---------------------------------------------------------------------------

def gun_6(m):
    x0, axis, squash = 0.5, 5.0, 0.43
    # The rotary cluster: eight barrels round a hub, held by a muzzle clamp and a rear ring.
    lathe_axis("clamp", [(0.0, 9.0), (0.4, 10.8), (1.0, 11.6), (5.8, 11.6), (6.4, 10.8), (7.0, 9.4)], m["steel"],
               (x0, 17.4, axis), (0, 1, 0), 32, squash=squash)
    for y in (19.0, 22.0):
        lathe_axis(f"clamp_groove_{y}", [(0.0, 11.75), (0.6, 11.75)], m["gunmetal"], (x0, y, axis), (0, 1, 0), 32,
                   squash=squash)
    lathe_axis("rear_ring", [(0.0, 9.2), (0.4, 10.0), (1.4, 10.0), (1.8, 9.2)], m["dark"], (x0, 8.4, axis),
               (0, 1, 0), 32, squash=squash)
    lathe_axis("hub", [(0.0, 3.0), (17.6, 3.0), (18.2, 2.0)], m["gunmetal"], (x0, 8.4, axis), (0, 1, 0), 16,
               squash=0.8)
    for i in range(8):
        a = math.radians(22.5 + 45 * i)
        bx, bz = x0 + 7.9 * math.cos(a), axis + 3.4 * math.sin(a)
        lathe_axis(f"barrel_{i}", [(0.0, 1.55), (18.0, 1.55), (18.1, 1.85), (18.9, 1.85), (19.0, 1.3)], m["light"],
                   (bx, 8.0, bz), (0, 1, 0), 10)
        lathe_axis(f"barrel_bore_{i}", [(0.0, 0.85), (0.3, 0.85)], m["black"], (bx, 26.9, bz), (0, 1, 0), 8)
    # The body: the motor housing behind the cluster, a wider block behind it, a ridge along them.
    housing_outline = [(-11.4, 8.6), (11.4, 8.6), (12.6, 7.2), (12.6, 1.6), (11.4, 0.2), (-11.4, 0.2), (-12.6, 1.6),
                       (-12.6, 7.2)]
    plate("housing", [(x0 + x, y) for x, y in housing_outline], 0.0, 8.0, m["mid"], bevel=1.2)
    body_outline = [(-13.6, 0.8), (13.6, 0.8), (15.6, -1.6), (15.6, -11.0), (13.0, -14.0), (-13.0, -14.0),
                    (-15.6, -11.0), (-15.6, -1.6)]
    plate("body", [(x0 + x, y) for x, y in body_outline], 0.0, 5.8, m["mid"], bevel=1.1)
    plate("body_top", [(x0 + x * 0.8, y * 0.8 - 2.6) for x, y in body_outline], 5.4, 6.3, m["steel"], bevel=0.4)
    for side in (-1, 1):
        for i in range(3):
            y = -8.6 - i * 1.3
            rbox(f"body_vent_{side}_{i}", x0 + side * 4.6 - 1.4, y - 0.3, x0 + side * 4.6 + 1.4, y + 0.3, 6.0, 6.45,
                 m["black"], 0.1)
    side_plate("ridge", [(-12.8, 4.8), (-0.6, 6.6), (2.0, 8.8), (8.4, 8.8), (8.4, 6.0), (-12.8, 4.2)], x0 - 2.4,
               x0 + 2.4, m["light"], bevel=0.5)
    rbox("ridge_slot", x0 - 0.5, -10.0, x0 + 0.5, -2.0, 5.2, 6.1, m["black"], 0.1)
    # Four red lamps.
    for x, y, z in ((-4.6, 3.4, 7.8), (4.6, 3.4, 7.8), (-8.4, -5.2, 6.1), (8.4, -5.2, 6.1)):
        lamp(f"lamp_{x}_{y}", (x0 + x, y, z), 1.5, m["lamp_red"], m["gunmetal"], 0.9)
    # The curved blades sweeping back either side.
    for side in (-1, 1):
        s = side
        px = [(12.5, 24.0), (10.0, 26.0), (8.0, 28.0), (6.0, 30.0), (4.0, 32.0), (2.6, 34.4), (1.6, 37.0), (1.0, 40.0),
              (0.8, 45.0), (1.0, 51.4), (2.2, 50.6), (3.6, 47.0), (5.2, 43.0), (7.0, 40.2), (11.0, 39.0), (13.6, 37.0),
              (15.4, 33.0), (15.4, 27.0), (14.0, 24.4)]
        outline = [(x0 - s * (24.0 - c), 26.5 - r) for c, r in px]
        drop = lambda x, y: -2.0 * max(0.0, min(1.0, (-2.0 - y) / 22.0)) ** 1.4
        blade = plate(f"blade_{side}", outline, 1.6, 3.8, m["steel"], bevel=0.7, smooth_angle=40)
        bend(blade, drop)
        # A bright rim along its outer edge.
        rim = [(x0 - s * (24.0 - c), 26.5 - r) for c, r in px[:10]]
        rim = catmull([(x + s * 0.9, y, 3.4 + drop(x, y)) for x, y in rim], 1.6)
        tube(f"blade_rim_{side}", rim, [0.9] * (len(rim) - 3) + [0.65, 0.4, 0.2], m["light"], 8)


GUNS = {0: gun_0, 1: gun_1, 2: gun_2, 3: gun_3, 4: gun_4, 5: gun_5, 6: gun_6, 7: gun_7, 14: gun_14, 21: gun_21}


# --- Check and previews ----------------------------------------------------------------------------------------

def _look(cam, target):
    d = Vector(target) - cam.location
    cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


def _camera(name, location, target, ortho_scale):
    data = bpy.data.cameras.new(name)
    data.type = "ORTHO"
    data.ortho_scale = ortho_scale
    cam = bpy.data.objects.new(name, data)
    cam.location = location
    bpy.context.scene.collection.objects.link(cam)
    _look(cam, target)
    return cam


def check(n, sheet_dir, supersample=4):
    """The model's top view against the picture's outline: prints the overlap (intersection over union)."""
    w, h = SIZES[n]
    path = os.path.join(sheet_dir, f"weapon_{n}.png")
    image = bpy.data.images.load(path)
    iw, ih = image.size
    px = list(image.pixels)
    mask = [[px[((ih - 1 - y) * iw + x) * 4 + 3] > 0.5 for x in range(w)] for y in range(h)]
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.film_transparent = True
    scene.render.resolution_x, scene.render.resolution_y = w * supersample, h * supersample
    scene.render.resolution_percentage = 100
    cam = _camera("silhouette", (0, 0, 100), (0, 0, 0), max(w, h))
    cam.rotation_euler = (0, 0, 0)
    scene.camera = cam
    out = os.path.join(bpy.app.tempdir or "/tmp", "au_front_silhouette.png")
    scene.render.filepath = out
    bpy.ops.render.render(write_still=True)
    render = bpy.data.images.load(out)
    rw, rh = render.size
    pixels = list(render.pixels)
    covered = [[False] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            a = 0.0
            for sy in range(supersample):
                for sx in range(supersample):
                    pxx, pyy = x * supersample + sx, rh - 1 - (y * supersample + sy)
                    a += pixels[(pyy * rw + pxx) * 4 + 3]
            covered[y][x] = a / supersample ** 2 > 0.5
    both = sum(covered[y][x] and mask[y][x] for y in range(h) for x in range(w))
    either = sum(covered[y][x] or mask[y][x] for y in range(h) for x in range(w))
    score = both / max(either, 1)
    print(f"store_gun_{n} silhouette overlap: {score:.3f}")
    for y in range(h):
        print("".join("#" if covered[y][x] and mask[y][x] else "+" if covered[y][x] else "-" if mask[y][x] else "."
                      for x in range(w)))
    bpy.data.objects.remove(cam)
    return score


# Where the store draws each picture on the USP Talon's illustration (store.json, top-left corners), for the
# previews on the ship's picture.
PLACES = {0: (61, 48), 1: (52, 41), 2: (54, 36), 3: (61, 53), 4: (66, 41), 5: (51, 35), 6: (53, 39), 7: (66, 53),
          14: (59, 38), 21: (51, 35)}


def ship_plane(n, picture):
    """The ship's picture (option 31, drawn at (35, 33), 85 x 112) as a flat plane at the deck's height,
    placed under the gun as the store places them (preview only)."""
    w, h = SIZES[n]
    gx, gy = PLACES[n]
    cx, cy = (35 + 85 / 2) - (gx + w / 2), (gy + h / 2) - (33 + 112 / 2)
    image = bpy.data.images.load(picture)
    mat = bpy.data.materials.new("ship_picture")
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    tex = nodes.new("ShaderNodeTexImage")
    tex.image = image
    tex.interpolation = "Closest"
    bsdf = nodes["Principled BSDF"]
    links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])
    bsdf.inputs["Roughness"].default_value = 0.6
    obj = k.mesh_object("ship_picture", [(cx - 42.5, cy - 56, -0.05), (cx + 42.5, cy - 56, -0.05),
                                         (cx + 42.5, cy + 56, -0.05), (cx - 42.5, cy + 56, -0.05)], [(0, 1, 2, 3)], mat)
    uv = obj.data.uv_layers.new()
    for i, (u, v) in enumerate(((0, 0), (1, 0), (1, 1), (0, 1))):
        uv.data[i].uv = (u, v)
    return obj


def preview(prefix, n, deck=False, scale=12, ship=None):
    """Renders the top view (framed like the picture), the store's view (from above, tilted towards the
    viewer) and a three-quarter view from the front right."""
    w, h = SIZES[n]
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.film_transparent = True
    world = bpy.data.worlds.new("preview")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.35, 0.37, 0.42, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.8
    scene.world = world
    scene.view_settings.view_transform = "Standard"
    sun = bpy.data.lights.new("sun", "SUN")
    sun.energy = 3.0
    sun_obj = bpy.data.objects.new("sun", sun)
    sun_obj.rotation_euler = Vector((0.45, 0.35, -1.0)).to_track_quat("-Z", "Y").to_euler()
    scene.collection.objects.link(sun_obj)
    if deck:
        deck_mat = k.material("preview_deck", (150, 120, 70), metallic=0.3, roughness=0.4)
        rbox("preview_deck", -9, -h / 2 - 6, 9, h / 2 - 4, -6.0, 0.0, deck_mat, 1.0)
    if ship:
        ship_plane(n, ship)
        scene.render.resolution_x = scene.render.resolution_y = 640
        gx, gy = PLACES[n]
        target = ((35 + 42.5) - (gx + w / 2), (gy + h / 2) - (33 + 56), 0.0)
        for view, loc in (("ship_top", (0.0, 0.0, 150.0)), ("ship_store", (0.0, -85.0, 120.0))):
            cam = _camera(view, (target[0] + loc[0], target[1] + loc[1], loc[2]), target, 122)
            scene.camera = cam
            scene.render.filepath = f"{prefix}_{view}.png"
            bpy.ops.render.render(write_still=True)
        return
    size = max(w, h)
    scene.render.resolution_x, scene.render.resolution_y = w * scale, h * scale
    top = _camera("top", (0, 0, 100), (0, 0, 0), size)
    top.rotation_euler = (0, 0, 0)
    scene.camera = top
    scene.render.filepath = prefix + "_top.png"
    bpy.ops.render.render(write_still=True)
    scene.render.resolution_x = scene.render.resolution_y = 512
    for view, loc in (("store", (0.0, -60.0, 85.0)), ("3q", (60.0, 70.0, 55.0)), ("side", (-90.0, 10.0, 22.0))):
        cam = _camera(view, loc, (0, 0, 3.0), size * 1.25)
        scene.camera = cam
        scene.render.filepath = f"{prefix}_{view}.png"
        bpy.ops.render.render(write_still=True)


def triangles():
    total = 0
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for obj in bpy.context.scene.objects:
        if obj.type != "MESH":
            continue
        mesh = obj.evaluated_get(depsgraph).to_mesh()
        total += sum(len(p.vertices) - 2 for p in mesh.polygons)
    return total


def main():
    options = k.args()
    only = [int(v) for v in options["only"].split(",")] if "only" in options else sorted(GUNS)
    for n in only:
        k.reset()
        m = materials()
        GUNS[n](m)
        lowest = min((obj.matrix_world @ Vector(c)).z for obj in bpy.context.scene.objects if obj.type == "MESH"
                     for c in obj.bound_box)
        highest = max((obj.matrix_world @ Vector(c)).z for obj in bpy.context.scene.objects if obj.type == "MESH"
                      for c in obj.bound_box)
        print(f"store_gun_{n}: {triangles()} triangles, z {lowest:.2f} to {highest:.2f}")
        if "stats" in options:
            depsgraph = bpy.context.evaluated_depsgraph_get()
            counts = []
            for obj in bpy.context.scene.objects:
                if obj.type == "MESH":
                    mesh = obj.evaluated_get(depsgraph).to_mesh()
                    counts.append((sum(len(p.vertices) - 2 for p in mesh.polygons), obj.name))
            for c, name in sorted(counts, reverse=True)[:12]:
                print(f"    {c:5d} {name}")
        k.export(os.path.join(OUT, f"store_gun_{n}.glb"))
        if "check" in options:
            check(n, options["check"])
        if "preview" in options:
            os.makedirs(options["preview"], exist_ok=True)
            preview(os.path.join(options["preview"], f"store_gun_{n}"), n, deck=options.get("deck") == "1",
                    ship=options.get("ship"))


if __name__ == "__main__":
    main()
