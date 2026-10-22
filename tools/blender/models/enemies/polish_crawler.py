"""MINERS's crawler train on its rail (sheet L sprites 275, the head, and 277, the wagon, 2x2 each; enemies 1160 and
1161 of episode 5, ground layers, armour 20 and 15, worth 25 and 15), polished (2026-10-22, round 35; it replaces
wave3_z_train.py's head and wagon, boxes on tracks with domes, a ribbed spine and lamps). models.cfg: model
crawler_head / crawler_wagon ... origin (unchanged); the sprite lines of L 275 and 277 get height=-4.

Where the level puts it (the level events, tools/content/tyrevents.py; the enemy data, tools/content/tyrdata.py):
MINERS puts the train three times (t1392 at column 4, t1476 at 3, t1812 at 9): the head (1160) at (x, y) on ground 2,
two wagons (1161) at (x, y - 24) and (x, y - 48) on the ground layer, each with a link of its own (each car is shot
alone; the game leaves its slumped wreck), standing still on the map, on one of MINERS's long grey rails (the map's
pipe runs on under the head and the wagons: the train rides it). The cars overlap by 4 rows, the car in front drawn
over the one behind. The wagon's frames (277 279 279, animate 2) would show when it fires, but it has no gun (tur 0)
and no event animates it: the game never shows L 279, so it gets no frame model. No other enemy, launched ones
included, shows L 275 or 277; neither is another sprite's pixels mirrored, turned or in other ramps; no episode 6 level
places the train.

As the sprites and their 4x upscales draw it (columns and rows of the 24 x 28 sprites; ramp 6's dark blue-greys
0x61-0x6c, outlined 0x30):
- The wagon: a narrow car (columns 3-20) seen from above and its front: its roof (rows 1-17) dark, lit along its back
  right corner (0x6a-0x6c), a brown dome turret on it (columns 8-15 of rows 4-8: ramp 1's 0x11-0x1d, its rim dark) with
  twin barrels pointing down the screen (columns 10 and 13 of rows 9-12), a light band at the roof's front edge (row
  17); its front (rows 18-25) darker, panel lines in deep blue (0xd0), a light blue lamp in its middle (columns 11-12
  of rows 21-22, 0x3c 0x3e).
- The head: the same car, its roof ribbed across (light ribs 0x6a-0x6c at rows 2, 6 and 10, columns 8-14), three pairs
  of vents glowing orange-yellow along its sides (columns 5-6 and 17-18 of rows 3-4, 7-8 and 11-12: 0x76-0x7d), a pale
  blue glass dome in front (columns 8-15 of rows 15-23, 0x38-0x3e) and a dark bumper under it (rows 24-27, 0x01-0x05).

Built as such cars riding the rail, for the game's camera (20 degrees from straight down, from the bottom of the
screen): a car is CAR_W wide, its roof CAR_H over the ground drawn where the sprites draw it (a point at height z shows
z tan 20 further up the screen than its ground point: back_y()), its front a face leaning back from the roof's front
edge (row 17.5) to the ground at the sprite's bottom (row 26: the sprites draw the cars' fronts tall), its underside
over a bogie that grips the rail (BOGIE: a saddle with two pairs of wheels over the pipe, the map's rail running under
it). The wagon's turret a brown dome on a collar, its barrels round tubes along the roof; the head's ribs raised bands
across its roof, its vents slits in its sides with glowing slats (0x77, 0x7b: emission 0.35, 0.45), its glass dome a
pale blue shell with a lighter crown, lit a little from inside (0x3c, 0x3e: emission 0.12, 0.18), the bumper a dark bar; each car's
coupling a short bar under its front. Painted by how the faces meet the game's light (from the upper left and above).
Each car is its own model, its sprite's centre its origin (no cut), its parts joined (polish_deli_boss.join),
triangulated (polish_k_pod.triangulate).

Coordinates: 1 unit = 1 game pixel; +X right, +Y up the screen, +Z up from the ground (z = 0); a car's origin is its
sprite's centre: the pixel corner (c, r) is (c - 12, 14 - r). Drawn at their origins (origin) on the ground layers:
height=-4 sets the train on the terrain (the game lifts the three cars, moving alike on the sprites' grid, together).

Replaces wave3_z_train.py (all of it: the head and the wagon were all it built) and the pixels only it reads
(wave3_z_art.py's TRAIN_HEAD and TRAIN_WAGON).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each car's silhouette as the
camera sees it against its sprite's pixels), --preview <prefix>, --only <name,...>, --train <prefix> (the three cars
placed as the level places them, for looking at).
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_deli_boss import join, drop_unused  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_stone_face import view_coverage  # noqa: E402

TILT = math.tan(math.radians(20.0))
LIGHT = Vector((-0.55, 0.45, 0.7)).normalized()

CAR_X = (-8.6, 8.6)                     # columns 3.4-20.6 (the outline's middle)
CAR_H = 9.0                             # the roof's height
CAR_BOTTOM = 1.6                        # the hull's underside (its skirts over the bogie)
CORNER = 2.6                            # the hull's corners rounded (in plan)
ROOF_BACK_ROW, ROOF_FRONT_ROW, FRONT_ROW = 0.1, 17.5, 26.3
BOGIE = dict(y=(-6.0, 4.0), z=(0.0, 1.9), half=4.2, wheel_r=1.2)
RAIL_R = 2.0                            # the map's pipe, round which the bogie's wheels sit


def back_y(row, h):
    """Where a point h high must be so that the camera sees it at the top edge of a row."""
    return 14.0 - row - h * TILT


def mat(name, index, metallic=0.4, roughness=0.4, glow=None):
    if glow is not None:
        return k.material(name, palette=index, metallic=0.0, roughness=0.4, emission=k.level_palette()[index],
                          emission_strength=glow)
    return k.material(name, palette=index, metallic=metallic, roughness=roughness)


def materials():
    return {"hull": mat("crawler_hull", 0x65, 0.4, 0.38), "hull_lit": mat("crawler_hull_lit", 0x68, 0.4, 0.35),
            "hull_dark": mat("crawler_hull_dark", 0x62, 0.4, 0.42), "edge": mat("crawler_edge", 0x6a, 0.4, 0.32),
            "line": mat("crawler_line", 0xd0, 0.3, 0.5), "black": mat("crawler_black", 0x30, 0.3, 0.6),
            "brown": mat("crawler_brown", 0x17, 0.45, 0.32), "brown_lit": mat("crawler_brown_lit", 0x1b, 0.45, 0.3),
            "brown_dark": mat("crawler_brown_dark", 0x12, 0.45, 0.36), "steel": mat("crawler_steel", 0x03, 0.6, 0.35),
            "steel_lit": mat("crawler_steel_lit", 0x06, 0.6, 0.3),
            "lamp": mat("crawler_lamp", 0x3c, glow=0.35), "glass": mat("crawler_glass", 0x3c, glow=0.12),
            "glass_lit": mat("crawler_glass_lit", 0x3e, glow=0.18),
            "vent": mat("crawler_vent", 0x77, glow=0.35), "vent_hot": mat("crawler_vent_hot", 0x7b, glow=0.45)}


def paint_light(obj, top, lit, dark, under=None, lit_at=0.62, dark_at=0.2):
    def pick(c, n):
        if under is not None and n.z < -0.55:
            return under
        d = n.dot(LIGHT)
        return lit if d > lit_at else dark if d < dark_at else top
    mk.paint(obj, pick)
    return obj


def round_corners(obj, radius):
    """Rounds the hull's corner edges running up its sides (the sprites draw the cars' corners round)."""
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    def side(e):
        return all(abs(abs(v.co.x) - (CAR_X[1] - CAR_X[0]) / 2) < 0.01 for v in e.verts)
    # the back corners (the edges standing up at the hull's back) well rounded, the front ones a little
    for pick, r in ((lambda d: abs(d.z) > 0.95, radius), (lambda d: 0.3 < abs(d.z) < 0.95, 0.7)):
        edges = [e for e in bm.edges if side(e) and pick((e.verts[0].co - e.verts[1].co).normalized())]
        if edges:
            bmesh.ops.bevel(bm, geom=edges, offset=r, offset_type="OFFSET", segments=5, profile=0.5, affect="EDGES",
                            clamp_overlap=True)
    bm.to_mesh(obj.data)
    bm.free()


def hull(name, m, front_row=FRONT_ROW, nose=0.0):
    """A car's hull: its roof drawn from row ROOF_BACK_ROW to ROOF_FRONT_ROW, its front leaning back from the roof's
    front edge to the ground line under the sprite's front_row; nose rounds the front's upper edge."""
    x0, x1 = CAR_X
    yb = back_y(ROOF_BACK_ROW, CAR_H)
    yr = back_y(ROOF_FRONT_ROW, CAR_H)
    yf = back_y(front_row, CAR_BOTTOM)
    profile = [(yb, CAR_BOTTOM), (yb, CAR_H), (yr, CAR_H), (yf, CAR_BOTTOM)]
    body = mk.prism(name, profile, x0, x1, m["hull"], axis="x")
    round_corners(body, CORNER)
    mk.bevel(body, 1.0 + nose, 3, 25)
    mk.shade(body, 30)

    def pick(c, n):
        if n.z < -0.5:
            return m["hull_dark"]
        if n.z > 0.85:
            return m["hull"]
        if n.y < -0.3 and n.z > 0.2:            # the front
            return m["hull_dark"] if n.dot(LIGHT) < 0.45 else m["hull"]
        return m["hull_lit"] if n.dot(LIGHT) > 0.55 else m["hull_dark"]
    mk.paint(body, pick)
    return body, (yb, yr, yf)


def bogie(m, y_mid):
    """The saddle under the car gripping the rail: a dark block, two pairs of small wheels on the pipe's flanks."""
    b = BOGIE
    y0, y1 = y_mid + b["y"][0], y_mid + b["y"][1]
    saddle = mk.box("saddle", -b["half"], b["half"], y0, y1, RAIL_R + 0.6, CAR_BOTTOM + 0.3, m["steel"])
    mk.bevel(saddle, 0.4, 2, 35)
    mk.shade(saddle, 35)
    parts = [saddle]
    for side in (-1, 1):
        for y in (y0 + 1.6, y1 - 1.6):
            w = mk.tube(f"wheel{side}{y:.0f}", [Vector((side * (RAIL_R + 0.2), y - 0.0, RAIL_R + 0.2)),
                                                Vector((side * (RAIL_R + 1.2), y, RAIL_R + 0.2))],
                        b["wheel_r"], m["steel"], 12)
            parts.append(w)
        plate = mk.box(f"cheek{side}", side * (RAIL_R + 1.2) - 0.4, side * (RAIL_R + 1.2) + 0.4, y0, y1, 0.4,
                       CAR_BOTTOM, m["steel"])
        parts.append(plate)
    for p in parts:
        paint_light(p, m["steel"], m["steel_lit"], m["steel"], lit_at=0.5)
    return parts


def coupling(m, yf):
    bar = mk.tube("coupling", [Vector((0.0, yf + 1.5, 2.3)), Vector((0.0, yf - 3.2, 2.3))], 0.7, m["steel"], 10)
    knob = mk.ball("coupling_knob", (0.0, yf - 3.2, 2.3), (1.0, 1.0, 1.0), m["steel_lit"], 12, 6)
    return [bar, knob]


def front_panels(m, yr, yf, lamp=True):
    """The front's panel lines (deep blue, as the sprite's 0xd0) and the lamp in its middle."""
    parts = []
    for i, x in enumerate((-5.6, -2.9, 2.9, 5.6)):
        a = Vector((x, yr - 0.15, CAR_H - 1.6))
        b = Vector((x, yf + 1.0, CAR_BOTTOM + 0.9))
        line = mk.tube(f"line{i}", [a, b], 0.32, m["line"], 6)
        parts.append(line)
    if lamp:
        t = 0.45
        p = Vector((0.0, yr + (yf - yr) * t - 0.25, CAR_H + (CAR_BOTTOM - CAR_H) * t))
        rim = mk.ball("lamp_rim", tuple(p), (1.6, 1.0, 1.6), m["line"], 14, 7)
        bulb = mk.ball("lamp", tuple(p + Vector((0.0, -0.45, 0.1))), (1.1, 0.8, 1.1), m["lamp"], 14, 7)
        parts += [rim, bulb]
    return parts


def wagon(m):
    body, (yb, yr, yf) = hull("wagon", m)
    parts = [body]
    parts += bogie(m, (yb + yf) / 2)
    parts += coupling(m, yf)
    parts += front_panels(m, yr, yf)
    # The light band along the roof's front edge, the lit panel on its back right corner.
    band = mk.box("band", CAR_X[0] + 1.3, CAR_X[1] - 1.3, yr + 0.15, yr + 0.85, CAR_H - 0.2, CAR_H + 0.25, m["edge"])
    parts.append(band)
    hatch = mk.box("hatch", 3.6, 7.2, back_y(4.4, CAR_H), back_y(1.2, CAR_H), CAR_H - 0.2, CAR_H + 0.3, m["edge"])
    mk.bevel(hatch, 0.3, 2, 35)
    parts.append(hatch)
    # The turret: a brown dome on a dark collar (drawn at rows 4-8), its twin barrels along the roof.
    tz = CAR_H + 0.2
    ty = back_y(6.4, tz + 1.4)
    collar = mk.lathe("turret_collar", [(0.01, tz), (3.6, tz), (3.6, tz + 0.7), (0.01, tz + 0.7)], (0.0, ty),
                      m["brown_dark"], 28)
    dome = mk.dome("turret", (0.0, ty), (3.9, 3.5, 2.6), tz + 0.6, m["brown"], 28, 8)
    paint_light(dome, m["brown"], m["brown_lit"], m["brown_dark"], lit_at=0.7)
    parts += [collar, dome]
    for x in (-1.6, 1.6):
        a = Vector((x, ty - 2.2, tz + 1.1))
        b = Vector((x, back_y(12.6, tz + 1.0), tz + 1.0))
        barrel = mk.tube(f"barrel{x:.0f}", [a, b], 0.62, m["brown"], 10)
        k.smooth(barrel, 50)
        paint_light(barrel, m["brown"], m["brown_lit"], m["brown_dark"], lit_at=0.5)
        muzzle = mk.tube(f"muzzle{x:.0f}", [b + (b - a).normalized() * -0.3, b + (b - a).normalized() * 0.15], 0.66,
                         m["brown_dark"], 10)
        parts += [barrel, muzzle]
    return parts


def head(m):
    body, (yb, yr, yf) = hull("head", m, front_row=FRONT_ROW + 1.0, nose=0.3)
    parts = [body]
    parts += bogie(m, (yb + yf) / 2)
    # The ribs across the roof (drawn at rows 2, 6 and 10) and the vents along its sides between them.
    for i, row in enumerate((2.2, 6.2, 10.2)):
        y = back_y(row, CAR_H + 0.4)
        rib = mk.box(f"rib{i}", -3.8, 3.4, y - 0.7, y + 0.7, CAR_H - 0.3, CAR_H + 0.6, m["edge"])
        mk.bevel(rib, 0.3, 2, 35)
        mk.shade(rib, 35)
        paint_light(rib, m["edge"], m["hull_lit"], m["hull_dark"], lit_at=0.85, dark_at=0.3)
        parts.append(rib)
    for i, row in enumerate((4.2, 8.2, 12.2)):
        for side in (-1, 1):
            y = back_y(row, CAR_H - 1.5)
            x = side * (CAR_X[1] - 2.6)
            pts = [(x - side * 1.3, y + 1.3), (x + side * 0.9, y - 0.9)]
            vent = mk.tube(f"vent{i}{side}", [Vector((px, py, CAR_H + 0.1)) for px, py in pts], 0.55,
                           m["vent_hot"] if i == 1 else m["vent"], 10)
            k.smooth(vent, 50)
            parts.append(vent)
            frame = mk.tube(f"vent_frame{i}{side}", [Vector((px, py, CAR_H - 0.45)) for px, py in pts], 0.8,
                            m["black"], 10)
            parts.append(frame)
    # The glass dome on the front (drawn at rows 15-23) and the dark bumper under it (rows 24-27).
    t = 0.42
    p = Vector((0.0, yr + (yf - yr) * t, CAR_H + (CAR_BOTTOM - CAR_H) * t))
    normal = Vector((0.0, -(CAR_H - CAR_BOTTOM), -(yr - yf))).normalized()
    if normal.z < 0:
        normal = -normal
    dome = mk.ball("glass", (0.0, 0.0, 0.0), (4.4, 4.6, 3.4), m["glass"], 28, 14)
    rot = normal.to_track_quat("Z", "Y").to_matrix().to_4x4()
    dome.data.transform(Matrix.Translation(p) @ rot)
    k.smooth(dome, 70)
    mk.paint(dome, lambda c, n: m["glass_lit"] if n.dot(LIGHT) > 0.75 else None)
    ring = mk.tube("glass_rim", [p - normal * 0.3, p + normal * 0.5], 4.4, m["black"], 28, radii=[4.5, 4.3])
    parts += [dome, ring]
    bumper = mk.box("bumper", -4.6, 4.6, yf - 1.2, yf + 1.2, 0.8, CAR_BOTTOM + 1.0, m["steel"])
    mk.bevel(bumper, 0.6, 2, 35)
    mk.shade(bumper, 35)
    paint_light(bumper, m["steel"], m["steel_lit"], m["steel"])
    parts.append(bumper)
    return parts


CARS = [("crawler_wagon", 277, wagon), ("crawler_head", 275, head)]


def export(parts, name, sprite, options, sheets):
    out = mk.outdir(options)
    for obj in parts:
        mk.apply(obj)
    bpy.context.view_layer.update()
    if sheets:
        mk.compare("%s (L %d) as the camera sees it, its sprite's pixels" % (name, sprite),
                   view_coverage(parts, 24, 28, (0.0, 0.0)), k.sprite_mask(os.path.join(sheets, "enemy_L.png"), sprite))
    drop_unused(parts)
    triangulate(parts)
    obj = join(parts, name)
    obj.data.name = name
    bpy.context.view_layer.update()
    mk.report(name, [obj], os.path.join(out, name + ".glb"))
    if "preview" in options:
        mk.preview(options["preview"] + name, [obj])
    return obj


def build():
    options = k.args()
    only = options["only"].split(",") if "only" in options else None
    sheets = options.get("check")
    made = {}
    for name, sprite, builder in CARS:
        if only and name not in only:
            continue
        k.reset()
        bpy.context.scene.view_settings.view_transform = "Standard"
        m = materials()
        obj = export(builder(m), name, sprite, options, sheets)
        if "train" in options:
            made[name] = obj
            mk.export([obj], options["train"] + name + ".glb")


if __name__ == "__main__":
    build()
