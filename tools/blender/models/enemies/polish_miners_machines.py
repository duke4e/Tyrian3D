"""MINERS's grey roller and blue tank (sheet M sprites 155 beside 157, and 159 beside 161, 2x2 each: two 48 x 28
pictures; enemies 1187 and 1188, and 1189 and 1190, of episode 5, ground layer, armour 10 and 12, worth 10 each),
polished (2026-10-22, round 35; it replaces wave3_ah.py's roller and tank, boxes and lathes painted by the sprites'
ramps on their pixel grid). models.cfg: model miners_roller_l / _r, miners_tank_l / _r ... origin (unchanged); every
sprite line gets height=-4.

Where the level puts them (the level events, tools/content/tyrevents.py; the enemy data, tools/content/tyrdata.py):
MINERS puts each pair side by side on the ground layer (the right piece at x + 24, the same y and link), always on the
map's row above tiles of their own, which paint the machine wrecked (the roller's wheel and block broken, the tank
burst): the roller at t132 (column 10), t3632 (9) and t4248 (columns 3 and 10), the tank at t104 (4), t244 (8), t4164
(6) and t4192 (2). Shot, a pair's pieces die together (one link), the game leaving its slumped wrecks of their models
over the painted wrecks. Neither animates; no other enemy, launched ones included, shows these sprites; none is another
sprite's pixels mirrored, turned or in other ramps; no episode 6 level places them. The red sand round them (ramp 4) is
the map's, painted in: left out.

As the sprites and their 4x upscales draw them (columns and rows of the 48 x 28 pictures):
- The roller: a big grey wheel at the left (columns 2-11, rows 1-24: its rim seen from above, toothed, ramp 0's greys
  0x04-0x0c and ramp 6's blue-greys), a black drum (columns 10-32, rows 7-19, 0x01-0x04, a little narrower in its
  middle, ribbed round) and a tall grey block at the right (columns 32-44): its top (rows 1-18) laid with eight bright
  plates, two by four (0x0b-0x0f with ramp 5's and 6's pale tints), its front (rows 19-25) grey, cracked at the bottom
  right (columns 37-41 of rows 22-26).
- The tank: a long blue body (columns 12-42; ramp 3's blues 0x34-0x3a) whose top (rows 8-18) is two rows of panels with
  light cyan edges and rivets (ramp 8, 0x80-0x84), a tan rail along its back edge (rows 6-7, 0xa4-0xa8), its front
  (rows 19-22) darker; at its left end a taller rounded bolster (columns 4-11, rows 1-22: its top blue, lit along its
  middle, its sides and front blue-black, ramp 6's 0x60-0x65), reaching further back; a small spout under the body's
  right end (columns 34-36, rows 22-24).

Built as real machines standing on the ground (z 0), their heights read from the sprites as the game's camera sees
them (20 degrees from straight down, from the bottom of the screen: a face of height h shows h tan 20 rows): the tank's
front shows 3.5 rows, so the body is BODY_H high and BODY deep (its top drawn at rows 6-19), the bolster BOLSTER_H, its
far end further back; the roller's wheel shows 24 rows (2.13 times its radius: WHEEL_R), so its axle stands WHEEL_R
over the ground, the drum on it held off the ground between the wheel and the block, whose front shows 7 rows (BLOCK_H).
CAD solids (polish_machine_kit.py: prisms, exact booleans, bevels, lathes), painted by how their faces meet the game's
light (from the upper left and above) in the sprites' own palette indices. The roller's greys are a little metallic
(0.3), the drum rubber; the tank's blues painted metal (0.35).

Each is cut at x = 0 (the sprites' edge: polish_stone_face.view_cut, an upright plane) into its two pieces, the cuts
closed in the part's inside colour, each piece moved so that its sprite's centre is its origin, triangulated
(polish_k_pod.triangulate) and its parts joined (polish_deli_boss.join).

Coordinates: 1 unit = 1 game pixel; +X right, +Y up the screen, +Z up from the ground (z = 0); each whole's origin is
its picture's middle (where the two sprites meet, half way down): the pixel corner (c, r) is (c - 24, 14 - r). The
pieces' centres: (-12, 0) and (12, 0). Drawn at their origins (origin) on the ground layer: height=-4 sets them on the
terrain (the game lifts two pieces side by side moving alike to the terrain under their middle).

Replaces wave3_ah.py's roller and tank (its sections "M 155, 157: the roller" and "M 159, 161: the tank"); with its
broken blocks (polish_block_rubble.py) they were all wave3_ah.py still built, so it goes (and with wave3_ah_rock.py and
wave3_ah_rig.py gone too, its kit wave3_ah_kit.py and its pixels wave3_ah_art.py, ROLLER and TANK among them).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each piece's silhouette as the
game's camera sees it against its sprite's own pixels, the sand left out), --preview <prefix>, --whole <prefix> (the
uncut machines: views and GLBs), --only <name,...>.
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_deli_boss import join, drop_unused  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_stone_face import view_cut, view_coverage  # noqa: E402

TILT = math.tan(math.radians(20.0))
LIGHT = Vector((-0.55, 0.45, 0.7)).normalized()

PIECES = {"roller": [("miners_roller_l", 155, (None, 0.0, None, None), (-12.0, 0.0)),
                     ("miners_roller_r", 157, (0.0, None, None, None), (12.0, 0.0))],
          "tank": [("miners_tank_l", 159, (None, 0.0, None, None), (-12.0, 0.0)),
                   ("miners_tank_r", 161, (0.0, None, None, None), (12.0, 0.0))]}


def P(c, r):
    """A pixel corner (column c, row r) of a 48 x 28 picture in the whole's coordinates."""
    return (c - 24.0, 14.0 - r)


def ground_y(row):
    """The ground line (z 0) the camera sees at the bottom edge of a row."""
    return 14.0 - row


def back_y(row, h):
    """Where a top face h high must end so that the camera sees its back edge at the top edge of a row."""
    return 14.0 - row - h * TILT


def mat(name, index, metallic=0.4, roughness=0.4):
    return k.material(name, palette=index, metallic=metallic, roughness=roughness)


def paint_light(obj, top, lit, dark, under=None, lit_at=0.62, dark_at=0.2):
    def pick(c, n):
        if under is not None and n.z < -0.55:
            return under
        d = n.dot(LIGHT)
        return lit if d > lit_at else dark if d < dark_at else top
    mk.paint(obj, pick)
    return obj


def rounded_box(name, x0, x1, y0, y1, z0, z1, m, radius):
    obj = mk.box(name, x0, x1, y0, y1, z0, z1, m)
    mk.bevel(obj, radius, 3, 35)
    mk.shade(obj, 35)
    return obj


# --- The roller -------------------------------------------------------------------------------------------------------
WHEEL_R = 10.3                      # (22 rows of wheel, 2-23: 2.13 times its radius)
AXLE_Y = 1.0 - WHEEL_R * TILT       # the axle's place on the ground plan (the wheel drawn round row 12.5)
WHEEL_X = (-20.7, -13.2)            # its faces (columns 3.3-10.8)
TEETH = 14
DRUM_X = (-13.2, 8.4)
DRUM_R, DRUM_WAIST = 6.1, 5.6       # (rows 7-19 at its ends, 8-18 in its middle)
BLOCK = dict(x0=8.2, x1=21.0, h=19.2)
BLOCK_FRONT = ground_y(26.0)        # its front stands on the bottom edge of row 25
BLOCK_BACK = back_y(1.0, BLOCK["h"])


def roller_materials():
    return {"grey": mat("roller_grey", 0x0a, 0.3, 0.38), "grey_lit": mat("roller_grey_lit", 0x0c, 0.3, 0.34),
            "grey_dark": mat("roller_grey_dark", 0x06, 0.3, 0.4), "blue_grey": mat("roller_blue_grey", 0x69, 0.45, 0.35),
            "blue_lit": mat("roller_blue_lit", 0x6c, 0.45, 0.32), "plate": mat("roller_plate", 0x0c, 0.5, 0.25),
            "plate_lit": mat("roller_plate_lit", 0x6e, 0.5, 0.22), "plate_tint": mat("roller_plate_tint", 0x5e, 0.5, 0.25),
            "rubber": mat("roller_rubber", 0x02, 0.15, 0.6), "rubber_lit": mat("roller_rubber_lit", 0x05, 0.15, 0.5),
            "crack": mat("roller_crack", 0x01, 0.1, 0.8)}


def wheel(m):
    """The wheel on the axle: a thick grey wheel with a well rounded rim (so the camera sees it narrowing at its far and
    near ends, as the sprite draws it), knobs round its tread, a hub cap on its outer face."""
    x0, x1 = WHEEL_X
    xc, half = (x0 + x1) / 2, (x1 - x0) / 2
    rho = 3.4                                   # the rim's rounding
    profile = []
    n = 14
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        d = max(0.0, abs(x - xc) - (half - rho))
        profile.append((x, WHEEL_R - rho + math.sqrt(max(0.0, rho * rho - d * d))))
    profile = [(x0, 0.05)] + profile + [(x1, 0.05)]
    seg = 48
    rings = [[Vector((x, AXLE_Y + r * math.cos(2 * math.pi * j / seg), WHEEL_R + r * math.sin(2 * math.pi * j / seg)))
              for j in range(seg)] for x, r in profile]
    disc = k.loft("wheel", rings, m["grey"])
    k.smooth(disc, 50)
    parts = [disc]
    for i in range(TEETH):
        a = 2 * math.pi * (i + 0.5) / TEETH
        c, s = math.cos(a), math.sin(a)
        knob = mk.ball(f"knob{i}", (xc, AXLE_Y + (WHEEL_R - 0.9) * c, WHEEL_R + (WHEEL_R - 0.9) * s),
                       (half - 1.2, 1.9, 1.9), m["grey"], 16, 8)
        knob.data.transform(Matrix.Translation((xc, AXLE_Y + (WHEEL_R - 0.9) * c, WHEEL_R + (WHEEL_R - 0.9) * s)) @
                            Matrix.Rotation(a, 4, "X") @
                            Matrix.Translation((-xc, -(AXLE_Y + (WHEEL_R - 0.9) * c), -(WHEEL_R + (WHEEL_R - 0.9) * s))))
        parts.append(knob)
    hub = mk.lathe("hub", [(0.01, 0.0), (3.6, 0.0), (3.4, 0.9), (2.4, 1.6), (0.01, 1.8)], (0.0, 0.0), m["blue_grey"], 28)
    hub.data.transform(Matrix.Translation((x0 + 0.6, AXLE_Y, WHEEL_R)) @ Matrix.Rotation(-math.pi / 2, 4, "Y"))
    k.smooth(hub, 50)
    parts.append(hub)
    for p in parts:
        paint_light(p, m["grey"], m["grey_lit"], m["grey_dark"], lit_at=0.6, dark_at=0.15)
    paint_light(hub, m["blue_grey"], m["blue_lit"], m["grey_dark"])
    return parts


def drum(m):
    """The black drum on the axle, a little narrower in its middle, ribbed round."""
    x0, x1 = DRUM_X
    n = 40
    profile = []
    for i in range(n + 1):
        t = i / n
        x = x0 + (x1 - x0) * t
        r = DRUM_WAIST + (DRUM_R - DRUM_WAIST) * (2 * t - 1) ** 2
        # ribs: shallow grooves round it every 3.1 pixels
        rib = 0.25 * (math.cos(2 * math.pi * (x - x0) / 3.1) ** 8)
        profile.append((x, r - rib))
    rings = []
    seg = 32
    for x, r in profile:
        rings.append([Vector((x, AXLE_Y + r * math.cos(2 * math.pi * j / seg), WHEEL_R + r * math.sin(2 * math.pi * j / seg)))
                      for j in range(seg)])
    obj = k.loft("drum", rings, m["rubber"])
    k.smooth(obj, 60)
    paint_light(obj, m["rubber"], m["rubber_lit"], m["rubber"], lit_at=0.55)
    axle = mk.tube("axle", [Vector((x0 - 1.0, AXLE_Y, WHEEL_R)), Vector((x1 + 1.0, AXLE_Y, WHEEL_R))], 2.4,
                   m["grey_dark"], 20)
    return [obj, axle]


def block(m):
    """The tall grey block at the right, eight plates on its top, cracked at its front's bottom right."""
    b = BLOCK
    body = rounded_box("block", b["x0"], b["x1"], BLOCK_FRONT, BLOCK_BACK, -0.6, b["h"], m["grey"], 0.9)
    # The crack: a jagged notch cut into the front's bottom right (columns 37-41 of rows 22-26).
    x, _ = P(37.0, 0)
    pts = [(x, BLOCK_FRONT - 1.0), (x + 1.4, BLOCK_FRONT - 1.0), (x + 2.3, BLOCK_FRONT + 0.9), (x + 3.3, BLOCK_FRONT - 1.0),
           (x + 4.4, BLOCK_FRONT - 1.0), (x + 3.0, BLOCK_FRONT + 2.2), (x + 1.2, BLOCK_FRONT + 1.6)]
    crack = mk.prism("crack", pts, -1.0, 6.5, m["crack"])
    crack.data.transform(Matrix.Translation((0.0, 0.0, 0.0)))
    mk.boolean(body, crack, "DIFFERENCE")
    mk.cleanup(body)
    paint_light(body, m["grey"], m["grey_lit"], m["grey_dark"], lit_at=0.6, dark_at=0.12)
    mk.paint(body, lambda c, n: m["crack"] if (c.z < 6.6 and c.y < BLOCK_FRONT + 2.4 and x - 0.2 < c.x < x + 4.6 and
                                             abs(n.y) < 0.98 and n.z < 0.9) else None)
    parts = [body]
    # The plates: two by four, a little raised, their tints as the sprite's (the bright ones 0x6e, the pale 0x5e).
    gx0, gx1 = b["x0"] + 1.0, b["x1"] - 1.0
    gy0, gy1 = BLOCK_FRONT + 1.0, BLOCK_BACK - 1.0
    w = (gx1 - gx0 - 0.8) / 2
    d = (gy1 - gy0 - 2.4) / 4
    tints = [["plate_lit", "plate_tint"], ["plate", "plate_lit"], ["plate_tint", "plate"], ["plate_lit", "plate_lit"]]
    for i in range(2):
        for j in range(4):
            px0 = gx0 + i * (w + 0.8)
            py1 = gy1 - j * (d + 0.8)
            plate = rounded_box(f"plate{i}{j}", px0, px0 + w, py1 - d, py1, b["h"] - 0.3, b["h"] + 0.55,
                                m[tints[j][i]], 0.35)
            mk.paint(plate, lambda c, n, m=m: m["grey_dark"] if n.z < 0.5 and n.dot(LIGHT) < 0.2 else None)
            parts.append(plate)
    return parts


def roller(m):
    return wheel(m) + drum(m) + block(m)


# --- The tank ---------------------------------------------------------------------------------------------------------
BODY = dict(x0=-12.0, x1=19.2, h=9.6)
BODY_FRONT = ground_y(23.0)
BODY_BACK = back_y(6.0, BODY["h"])
BOLSTER = dict(x0=-20.0, x1=-11.6, h=11.4, r=3.6)
BOLSTER_BACK = back_y(1.0, BOLSTER["h"])
PANEL_SEAM_Y = back_y(12.5, BODY["h"] + 0.5)        # (the seam between the two rows of panels, drawn at row 12.5)
PANEL_X = [-11.0, -4.6, 1.2, 7.2, 13.0, 18.2]        # the panels' ends along the body


def tank_materials():
    return {"blue": mat("tank_blue", 0x37, 0.35, 0.35), "blue_lit": mat("tank_blue_lit", 0x39, 0.35, 0.32),
            "blue_dark": mat("tank_blue_dark", 0x34, 0.35, 0.4), "black": mat("tank_black", 0x62, 0.35, 0.4),
            "black_lit": mat("tank_black_lit", 0x65, 0.35, 0.38), "cyan": mat("tank_cyan", 0x82, 0.35, 0.3),
            "seam": mat("tank_seam", 0x61, 0.3, 0.5), "rail": mat("tank_rail", 0xa6, 0.5, 0.3),
            "rail_lit": mat("tank_rail_lit", 0xa9, 0.5, 0.28), "rivet": mat("tank_rivet", 0x84, 0.5, 0.3)}


def tank(m):
    b = BODY
    body = rounded_box("tank_body", b["x0"], b["x1"], BODY_FRONT, BODY_BACK, -0.6, b["h"], m["blue"], 0.8)
    paint_light(body, m["blue"], m["blue_lit"], m["blue_dark"], lit_at=0.66, dark_at=0.25)
    mk.paint(body, lambda c, n: m["black"] if n.y < -0.7 and c.z < 2.0 else None)
    parts = [body]
    # The panels on its top: two rows, raised a little, their lit edges cyan.
    rows = [(BODY_FRONT + 0.9, PANEL_SEAM_Y - 0.45), (PANEL_SEAM_Y + 0.45, BODY_BACK - 2.2)]
    for j, (y0, y1) in enumerate(rows):
        for i in range(len(PANEL_X) - 1):
            x0, x1 = PANEL_X[i] + 0.4, PANEL_X[i + 1] - 0.4
            panel = rounded_box(f"panel{j}{i}", x0, x1, y0, y1, b["h"] - 0.3, b["h"] + 0.45, m["blue"], 0.35)
            paint_light(panel, m["blue"], m["cyan"], m["blue_dark"], lit_at=0.8, dark_at=0.3)
            parts.append(panel)
            for rx in (x0 + 0.9, x1 - 0.9):
                rivet = mk.ball(f"rivet{j}{i}{rx:.0f}", (rx, (y0 + y1) / 2, b["h"] + 0.5), (0.45, 0.45, 0.3),
                                m["rivet"], 10, 5)
                parts.append(rivet)
    # The front's panel line: a dark seam along the front, a cyan lip over it.
    seam = mk.box("front_seam", b["x0"] + 1.0, b["x1"] - 1.0, BODY_FRONT - 0.15, BODY_FRONT + 0.3, 4.6, 5.3, m["seam"])
    parts.append(seam)
    # The rail along the back edge: a tan bar on posts.
    ry = BODY_BACK - 1.1
    rail = mk.tube("rail", [Vector((b["x0"] + 0.8, ry, b["h"] + 1.3)), Vector((b["x1"] - 0.8, ry, b["h"] + 1.3))], 0.65,
                   m["rail"], 12)
    k.smooth(rail, 50)
    paint_light(rail, m["rail"], m["rail_lit"], m["rail"], lit_at=0.4)
    parts.append(rail)
    for i, x in enumerate((b["x0"] + 2.0, (b["x0"] + b["x1"]) / 2, b["x1"] - 2.0)):
        post = mk.tube(f"post{i}", [Vector((x, ry, b["h"] - 0.2)), Vector((x, ry, b["h"] + 1.3))], 0.4, m["rail"], 8)
        parts.append(post)
    # The bolster at the left end: a beam along y, its top rounded across, reaching further back, its far end round.
    bo = BOLSTER
    xs = [bo["x0"] + (bo["x1"] - bo["x0"]) * i / 16 for i in range(17)]
    half = (bo["x1"] - bo["x0"]) / 2
    mid = (bo["x0"] + bo["x1"]) / 2
    outline = [(x, bo["h"] - bo["r"] + math.sqrt(max(0.0, bo["r"] ** 2 - max(0.0, abs(x - mid) - (half - bo["r"])) ** 2)))
               for x in xs]
    profile = [(bo["x1"], -0.6)] + outline[::-1] + [(bo["x0"], -0.6)]
    beam = mk.prism("bolster", [(x, z) for x, z in profile], BODY_FRONT, BOLSTER_BACK, m["blue"], axis="y")
    mk.bevel(beam, 0.9, 3, 30)
    mk.shade(beam, 35)

    def pick(c, n):
        if n.z > 0.75:
            return m["blue_lit"] if abs(c.x - mid) < 1.6 else m["blue"]
        if n.z < -0.5:
            return m["black"]
        return m["black_lit"] if n.dot(LIGHT) > 0.5 else m["black"]
    mk.paint(beam, pick)
    parts.append(beam)
    # The spout under the body's right end, pointing down the screen.
    sx, _ = P(35.5, 0)
    spout = mk.tube("spout", [Vector((sx, BODY_FRONT + 0.6, 1.6)), Vector((sx, BODY_FRONT - 1.4, 1.3)),
                              Vector((sx, BODY_FRONT - 2.4, 0.9))], 1.2, m["blue"], 14, radii=[1.3, 1.0, 0.35])
    k.smooth(spout, 50)
    paint_light(spout, m["blue"], m["blue_lit"], m["blue_dark"])
    parts.append(spout)
    return parts


# --- Build ------------------------------------------------------------------------------------------------------------

def own_mask(sheets, sprite):
    """A sprite's pixels, the sand round it (ramp 4) left out."""
    from sprite_profile import sprite_indices
    rows = sprite_indices(os.path.join(sheets, "enemy_M.png"), sprite)
    return [[v is not None and (v >> 4) != 4 for v in row] for row in rows]


def export_pieces(whole, specs, cap, options, sheets):
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    for name, sprite, box, centre in specs:
        if only and name not in only:
            continue
        parts = [p for p in (view_cut(src, box, cap, 0.0) for src in whole) if p is not None]
        for src in whole:
            src.hide_render = True
        if sheets:
            mk.compare("%s (M %d) as the camera sees it, its sprite's own pixels" % (name, sprite),
                       view_coverage(parts, 24, 28, centre), own_mask(sheets, sprite))
        mk.transform(parts, Matrix.Translation((-centre[0], -centre[1], 0.0)))
        drop_unused(parts)
        triangulate(parts)
        obj = join(parts, name)
        obj.data.name = name
        bpy.context.view_layer.update()
        mk.report(name, [obj], os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, [obj])
        bpy.data.objects.remove(obj)
        for src in whole:
            src.hide_render = False


def build():
    options = k.args()
    only = options["only"].split(",") if "only" in options else None
    sheets = options.get("check")
    for key, builder, materials, cap in (("roller", roller, roller_materials, "grey_dark"),
                                         ("tank", tank, tank_materials, "black")):
        if only and not any(n in only for n, *_ in PIECES[key]):
            continue
        k.reset()
        bpy.context.scene.view_settings.view_transform = "Standard"
        m = materials()
        whole = builder(m)
        for obj in whole:
            mk.apply(obj)
        bpy.context.view_layer.update()
        print("%s: %d triangles, %d objects" % (key, mk.triangles(whole), len(whole)))
        if "whole" in options:
            mk.export(whole, options["whole"] + "miners_%s.glb" % key)
            mk.preview(options["whole"] + "miners_" + key, whole, size=(48, 28), scale=12, distance=1.2)
        export_pieces(whole, PIECES[key], m[cap], options, sheets)


if __name__ == "__main__":
    build()
