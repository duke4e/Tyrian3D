"""MARKERS' copper car (sheet V sprite 163, 2x2: 13 x 22 pixels in the 24 x 28 cell; episode 2's enemy 813, on the
ground; one frame, not animated), polished (2026-10-21; it replaces wave3_t_ships.py's copper_car(), a cushion of the
sprite's plan with a glazed block and a roof on it). models.cfg: sprite v 163 copper_car yaw=0 (unchanged).

MARKERS' events put seven of them across the road at the start (x 40-220, placed 120 pixels down the screen) and send
more up from the bottom of the screen (ground-bottom events at 40, 200, 680, 1346, 2146, 2466): enemy 813 drives up the
screen (y move -2 against the ground's scroll), front first, as the sprite draws it (yaw=0). No damaged look (dgr 0);
shot, it leaves the game's slumped wreck. No other enemy shows V 163, and no other sprite of any sheet is its pixels
mirrored, turned or in other ramps.

As the sprite and its 4x upscale draw it (columns and rows of the 24 x 28 cell; symmetric about column 11, x -0.5): a
copper car (ramp 4) seen from above, its front up the screen. A long rounded hood (rows 3-7), lighter down its middle,
yellow lamps at its front corners (0x7b: columns 7-8 and 15-16 of rows 5-6, slanting with the corners) and a dark nose
(row 3); a dark cowl across (row 8), then the cabin glazed in blue all round (ramp 9): the windscreen (rows 9-11,
narrowing to the front), the side windows (columns 7-8 and 14-15 of rows 11-18, parted by the B-pillar at row 15) and
the rear window (rows 19-20), copper pillars at its corners, the copper roof (columns 9-13 of rows 12-18) lit along its
left; the rear deck (rows 21-24) with two small tail lamps (columns 9 and 13 of row 24). Four dark wheels stick out a
pixel at the sides (columns 5 and 17 of rows 9-11 and 20-21), the fenders' dark lips over them (rows 8 and 19).

Built from lofts (tyrkit): the body one loft along the car (superellipse sections, boxy and well rounded) whose plan
follows the sprite's, the hood and the deck sloping down to the nose and the tail, the fenders swelling over the wheels;
the greenhouse a loft of rounded sections tapering up to the roof, glossy blue glass glowing a little in its own colour
(dark blue reads black from the game's slanted camera otherwise); the roof a low rounded panel on it; the pillars thin
copper bars laid over the glass from its foot to the roof's corners, a dark cowl across the windscreen's foot and a sill
under the rear window; the wheels turned parts (tyre, hub); the lamps small lenses glowing amber (well under 1: the bloom
adds).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the ground (z = 0); origin at the
sprite's centre (pixel 12, 14): column c is x = c + 0.5 - 12, row r is y = 13.5 - r. The car stands on its wheels on
z = 0 (the game centres ground models in height and lifts them onto the ground).

Replaces wave3_t_ships.py's copper_car() (its "# --- V 163: the copper car" section with the @model("copper_car",
[163]) registration, and the docstring's copper_car lines) and wave3_t_art.py's CAPSULE (V 163's pixels, which nothing
reads): remove them so that they don't overwrite this model.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouette against
enemy_V.png sprite 163), --preview <prefix>, --stats 1.
"""
import math
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
from polish_green_beetle import thin_tube  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_redjet import Curve, smoothstep  # noqa: E402

NAME = "copper_car"
AX = -0.5                    # the car's middle line (column 11)
# The body along y: half-width (through the middles of the sprite's steps, the fenders' swell left out: see FENDERS),
# the height of its top on the middle line, of its underside.
BODY = Curve([(-11.0, 1.2, 2.6, 1.3), (-10.75, 2.9, 2.8, 1.1), (-10.2, 3.9, 3.0, 1.0), (-9.4, 4.75, 3.2, 0.95),
              (-8.4, 5.35, 3.35, 0.9), (-7.0, 5.5, 3.45, 0.9), (0.0, 5.5, 3.5, 0.9), (5.5, 5.5, 3.45, 0.9),
              (6.8, 5.45, 3.3, 0.9), (7.8, 5.15, 3.15, 0.95), (8.7, 4.6, 3.0, 1.0), (9.6, 3.85, 2.85, 1.05),
              (10.4, 2.9, 2.65, 1.15), (10.85, 1.6, 2.45, 1.3), (11.0, 0.5, 2.3, 1.4)])
BODY_Y = (-11.05, 11.02)
BODY_POWER = (3.0, 2.4)      # the sections' superellipse powers: top, underside
SIDE_Z = 2.2                 # the height of the body's sides
FENDERS = [(4.15, 1.05), (-6.35, 1.05)]   # y of the wheels' middles, how far the fenders swell out
# The wheels: their middles (y), radius, the tyre's inner and outer faces (out from the middle line).
WHEELS = [4.1, -6.4]
WHEEL_R = 1.85
TYRE = (4.6, 6.45)
# The greenhouse: half-width by y at its foot (on the body), its foot's and top's heights; the share of the width left
# at its top (where the roof sits).
GLASS = Curve([(-7.15, 1.2), (-6.9, 3.6), (-6.4, 4.35), (-5.6, 4.45), (1.5, 4.45), (2.4, 4.3), (3.4, 3.5),
               (4.4, 2.6), (5.05, 1.6), (5.3, 0.6)])
GLASS_Y = (-7.2, 5.35)
GLASS_Z = (3.0, 6.05)
GLASS_TOP = 0.58
# The roof (columns 9-13 of rows 12-18): its plan, its thickness over the glass.
ROOF = (-5.05, 2.1, 2.5, 0.38)
# The pillars: (y at the glass's foot, y at the roof's edge) for the A-, B- and C-pillars.
PILLARS = [(3.35, 2.0), (-1.45, -1.45), (-6.0, -5.0)]
# The lamps: the headlamps' ends (x out from the middle line, y), the tail lamps (x, y).
HEADLAMP = ((3.0, 8.75), (4.15, 7.45))
TAIL_LAMPS = [(-2.0, -10.45), (2.0, -10.45)]


def materials():
    pal = k.level_palette()

    def copper(name, index, metallic=0.5, roughness=0.3):
        return k.material(name, palette=index, metallic=metallic, roughness=roughness)

    def lit(name, index, strength, roughness=0.08, metallic=0.3, glow=None):
        return k.material(name, palette=index, metallic=metallic, roughness=roughness, emission=pal[glow or index],
                          emission_strength=strength)
    return {
        "body": copper("car_body", 0x47, 0.5, 0.28),
        "light": copper("car_light", 0x49, 0.5, 0.24),
        "dark": copper("car_dark", 0x44, 0.45, 0.38),
        "deep": copper("car_deep", 0x42, 0.3, 0.55),
        "glass": lit("car_glass", 0x94, 0.28, 0.06, 0.35, glow=0x95),
        "glass_hi": lit("car_glass_hi", 0x97, 0.4, 0.05, 0.3),
        "tyre": k.material("car_tyre", palette=0x63, metallic=0.15, roughness=0.65),
        "hub": k.material("car_hub", palette=0x68, metallic=0.6, roughness=0.3),
        "lamp": lit("car_lamp", 0x7b, 0.55, 0.2, 0.0),
    }


# --- Helpers ---------------------------------------------------------------------------------------------------------

def section(y, hw, zc, top, under, segments, power):
    """A superellipse section across the car at y: half-width hw, its top `top` and underside `under` (the sides at
    zc); power: (top half, lower half)."""
    pts = []
    for j in range(segments):
        a = 2 * math.pi * j / segments
        c, s = math.cos(a), math.sin(a)
        p = power[0] if s >= 0 else power[1]
        u = math.copysign(abs(c) ** (2 / p), c)
        v = math.copysign(abs(s) ** (2 / p), s)
        pts.append(Vector((AX + hw * u, y, zc + (top - zc) * v if s >= 0 else zc + (zc - under) * v)))
    return pts


def fender_swell(y):
    return sum(d * math.exp(-((y - fy) / 1.35) ** 2) for fy, d in FENDERS)


def body(m, count=40, segments=40):
    y0, y1 = BODY_Y
    rings = []
    for i in range(1, count):
        t = i / count
        y = y0 + (y1 - y0) * (0.5 - 0.5 * math.cos(math.pi * t))
        hw, top, under = BODY(y)
        rings.append(section(y, hw + fender_swell(y), SIDE_Z, top, under, segments, BODY_POWER))
    obj = k.loft("body", rings, m["body"], start_point=(AX, y0, 1.9), end_point=(AX, y1, 1.9))
    k.smooth(obj, 50)

    def pick(c, n):
        if n.z < 0.1:
            return m["deep"]
        if n.z < 0.5:
            return m["dark"]
        if abs(c.x - AX) < 2.2 and c.y > 5.3 and n.z > 0.75:
            return m["light"]
        return None
    mk.paint(obj, pick)
    # The nose and the tail dark along their edges (rows 3 and 24).
    mk.paint(obj, lambda c, n: m["dark"] if (c.y > 10.55 or c.y < -10.7) and n.z < 0.92 else None)
    return obj


def greenhouse(m, count=34, segments=36):
    y0, y1 = GLASS_Y
    z0, z1 = GLASS_Z
    rings = []
    for i in range(1, count):
        t = i / count
        y = y0 + (y1 - y0) * (0.5 - 0.5 * math.cos(math.pi * t))
        hw = GLASS(y)
        # The windscreen and the rear window slope: the top shrinks towards the ends.
        end = min(smoothstep(y1, y1 - 3.2, y), smoothstep(y0, y0 + 2.0, y))
        top = z0 + (z1 - z0) * (0.35 + 0.65 * end)
        pts = []
        for j in range(segments):
            a = 2 * math.pi * j / segments
            c, s = math.cos(a), math.sin(a)
            u = math.copysign(abs(c) ** (2 / 2.6), c)
            v = math.copysign(abs(s) ** (2 / 2.6), s)
            if s >= 0:
                # Sides leaning in: the half-width shrinks to GLASS_TOP of the foot's at the top.
                w = hw * (1 - (1 - GLASS_TOP) * v ** 1.6)
                pts.append(Vector((AX + w * u, y, z0 + (top - z0) * v)))
            else:
                pts.append(Vector((AX + hw * u, y, z0 + 0.9 * v)))
        rings.append(pts)
    obj = k.loft("glass", rings, m["glass"], start_point=(AX, y0, z0), end_point=(AX, y1, z0))
    k.smooth(obj, 55)
    # A light glint on the windscreen and the rear window, upper left.
    mk.paint(obj, lambda c, n: m["glass_hi"] if (n.y > 0.45 and n.x < -0.05 and c.y > 2.6) or
             (n.y < -0.5 and n.x < -0.1 and c.y < -5.6) else None)
    return obj


def glass_top(x, y):
    """The greenhouse's top height at (x, y), by ray (for laying the roof and the pillars on it); the body's where the
    glass isn't."""
    hit = GLASS_SURFACE(x, y)
    if hit is None:
        hit = BODY_SURFACE(x, y)
    return hit[0].z if hit else GLASS_Z[0]


GLASS_SURFACE = None


def roof(m):
    y0, y1, hw, thick = ROOF
    rings = []
    count = 16
    for i in range(1, count):
        t = i / count
        y = y0 + (y1 - y0) * (0.5 - 0.5 * math.cos(math.pi * t))
        end = min(1.0, (y - y0) / 0.9, (y1 - y) / 0.9)
        w = hw * math.sqrt(max(0.05, end * (2 - end)))
        z = glass_top(AX, y)
        rings.append(section(y, w, z - 0.1, z + thick, z - 0.5, 28, (2.6, 2.0)))
    zs, ze = glass_top(AX, y0), glass_top(AX, y1)
    obj = k.loft("roof", rings, m["body"], start_point=(AX, y0 - 0.1, zs), end_point=(AX, y1 + 0.1, ze))
    k.smooth(obj, 55)
    mk.paint(obj, lambda c, n: m["light"] if n.z > 0.6 and c.x < AX - 0.4 else m["dark"] if n.z < 0.3 else None)
    return obj


def pillars(m):
    parts = []
    _, _, hw, _ = ROOF
    for i, (yf, yr) in enumerate(PILLARS):
        for side in (-1, 1):
            foot = GLASS(yf) - 0.15
            pts = []
            for k_ in range(7):
                t = k_ / 6
                x = AX + side * (foot + (hw - 0.2 - foot) * t)
                y = yf + (yr - yf) * t
                pts.append(Vector((x, y, glass_top(x, y) + 0.02)))
            parts.append(thin_tube(f"pillar{i}{'lr'[side > 0]}", pts, 0.36, m["body"], 6, squash=0.7, iterations=0))
    # The cowl across the windscreen's foot (row 8) and the sill under the rear window.
    for name, y, w in (("cowl", 5.55, 2.1), ("sill", -6.95, 3.4)):
        pts = [Vector((AX + x, y, glass_top(AX + x, y) - 0.05)) for x in (-w, -w * 0.5, 0.0, w * 0.5, w)]
        parts.append(thin_tube(name, pts, 0.38, m["dark"], 6, squash=0.6, iterations=1))
    return parts


def wheel(m, y, side):
    r = WHEEL_R
    x0, x1 = TYRE
    prof = [(x0, r * 0.78), (x0 + 0.1, r * 0.95), (x0 + 0.35, r), (x1 - 0.35, r), (x1 - 0.1, r * 0.92),
            (x1, r * 0.7)]
    segments = 20
    rings = [[Vector((AX + side * x, y + rr * math.cos(2 * math.pi * j / segments), r + rr * math.sin(2 * math.pi * j /
                                                                                                    segments)))
              for j in range(segments)] for x, rr in prof]
    tyre = k.loft(f"tyre{side}{y:+.0f}", rings, m["tyre"], start_point=(AX + side * x0, y, r),
                  end_point=(AX + side * x1, y, r))
    k.smooth(tyre, 45)
    hub = mk.tube(f"hub{side}{y:+.0f}", [Vector((AX + side * (x1 - 0.2), y, r)), Vector((AX + side * (x1 + 0.12), y, r))],
                  r * 0.52, m["hub"], 14)
    return [tyre, k.smooth(hub, 40)]


def lamps(m):
    parts = []
    (xa, ya), (xb, yb) = HEADLAMP
    for side in (-1, 1):
        pts = []
        for x, y in ((xa, ya), (xb, yb)):
            hit = BODY_SURFACE(AX + side * x, y)
            pts.append(Vector((AX + side * x, y, (hit[0].z if hit else 3.0) - 0.2)))
        parts.append(thin_tube(f"headlamp{'lr'[side > 0]}", pts, 0.55, m["lamp"], 8, squash=0.75, iterations=0))
    for i, (x, y) in enumerate(TAIL_LAMPS):
        hit = BODY_SURFACE(AX + x, y)
        z = (hit[0].z if hit else 2.6) - 0.15
        parts.append(mk.ball(f"tail_lamp{i}", (AX + x, y, z), (0.55, 0.42, 0.4), m["lamp"], 12, 6))
    return parts


BODY_SURFACE = None


def car():
    global GLASS_SURFACE, BODY_SURFACE
    m = materials()
    shell = body(m)
    glass = greenhouse(m)
    bpy.context.view_layer.update()
    GLASS_SURFACE = mk.surface([glass])
    BODY_SURFACE = mk.surface([shell])
    parts = [shell, glass, roof(m)] + pillars(m) + lamps(m)
    for y in WHEELS:
        for side in (-1, 1):
            parts += wheel(m, y, side)
    return parts


def build():
    options = k.args()
    out = mk.outdir(options)
    k.reset()
    parts = car()
    triangulate(parts)
    bpy.context.view_layer.update()
    if "stats" in options:
        for obj in parts:
            print("  %-16s %5d triangles" % (obj.name, len(obj.data.polygons)))
    if "check" in options:
        sheet = os.path.join(options["check"], "enemy_V.png")
        mk.compare("copper_car (V 163)", mk.coverage(parts, 24, 28), k.sprite_mask(sheet, 163))
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    mk.report(NAME, parts, os.path.join(out, NAME + ".glb"))
    if "preview" in options:
        mk.preview(options["preview"] + NAME, parts, distance=0.7)


if __name__ == "__main__":
    build()
