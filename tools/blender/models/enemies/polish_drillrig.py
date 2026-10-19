"""The drilling machine of GRYPHON, MISTAKES, STATION, REEF, MIGRATION and GLACIER, drawn from two sprites of sheet V,
2x2 each: 1, the blue armoured head, above 39, the drill bit (models.cfg: model drillrig_head / drillrig_bit /
drillrig_head_3 / drillrig_bit_41 ... origin; sprite v 1 drillrig_head yaw=0, sprite v 39 drillrig_bit yaw=0,
frame v 3 drillrig_head_3, frame v 41 drillrig_bit_41). The levels place them as one 24 x 56 picture, V 1 28
pixels above V 39, and they move together (enemies 790 above 791 on the ground of GRYPHON and MISTAKES; 1059 above
1060 in the sky of STATION, REEF, MIGRATION and GLACIER), polished (2026-10-19; it replaces wave2_f_more.py's
drillrig_whole(), drillrig_head() and drillrig_bit()).

The machine is built whole, drill down the screen, and cut along the sprites' edge (y = 0 here) into the two
pieces, each moved so that its sprite's centre is its origin (base on the layer): drawn at their own places they
meet again; the cut pieces keep the whole's shading across the cut (polish_redjet.py's method).

As the 4x upscales draw it: the head (rows 0-17 of V 1) is blue armour (the sprite's ramp 3, dark navy 0x35-0x38,
its edges catching the light 0x3a-0x3e): a tall crown plate on top in the middle (columns 9-16 of rows 0-8), a
rounded shoulder plate on the left (columns 1-8 of rows 1-9), a cheek plate below it (columns 2-6 of rows 9-16),
a grey hatch open in the front left (columns 6-11 of rows 10-15) beside a narrow middle plate (columns 12-16) and a
right cheek with a chamfered edge (columns 16-22 of rows 8-16); a grey ribbed piston sticks out on the right
(columns 18-21 of rows 4-9). Under it a dark collar holds the drill (row 17), whose broad grey shoulder fills the
rest of V 1 (rows 18-27: 21 pixels across) and which tapers down V 39 to its point (column 12 of row 27), two
spiral flutes winding down it (dark grooves slanting from the upper left to the lower right where the camera sees
it). The animation (1 3 and 39 41) turns the drill: one model per frame, the flutes turned a quarter turn (half
the flutes' spacing) in drillrig_head_3 and drillrig_bit_41; no other enemy of sheet V shows sprites 3 or 41.

The drill lies along y, its section a little flatter than round (DRILL_SQUASH) so that the machine rests on the
ground (z 0) in GRYPHON and MISTAKES without towering; its flutes are cut into the turned surface (each ring's
points follow the helix, so the grooves run clean along it). The armour plates are reliefs over the sprite's
outlines with rounded edges, on a housing over the drill's back end.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera. The whole's
x = 0 is the sprites' column 12's left edge, its y = 0 the edge between the two sprites (V 1's row r is y = 27.5 -
r, V 39's row r is y = -0.5 - r); the drill's axis runs along x = AXIS_X (column 12's middle).

Replaces wave2_f_more.py's drillrig_whole(), drillrig_head() and drillrig_bit() (its @model("drillrig_head") and
@model("drillrig_bit") entries, DRILL_PROFILE and the "drillrig" entry of WHOLE): remove them so that they don't
overwrite these models.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes of the
whole and of each piece against enemy_V.png), --preview <prefix> (the whole's and each piece's views).
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
from polish_jets import Curve  # noqa: E402
from polish_ring_machine import ccw, chaikin, relief, round_edge  # noqa: E402
from polish_sphere_nozzle import smoothstep  # noqa: E402
from polish_tank_pod import check_mask, cut, export, move, preview, triangles  # noqa: E402

AXIS_X = 0.5
# The pieces: (name of the first frame's model, its sprite, the box it covers (x0, x1, y0, y1), its centre's y).
PIECES = [("drillrig_head", 1, (-12.0, 12.0, 0.0, 28.0), 14.0),
          ("drillrig_bit", 39, (-12.0, 12.0, -28.0, 0.0), -14.0)]
# The frames: (the head's and the bit's sprites, the flutes' turn in degrees).
FRAMES = [((1, 39), 0.0), ((3, 41), 90.0)]


def head_px(c, r):
    """A point of V 1 given as (column, row) of its pixel grid (corners) in the whole's coordinates."""
    return (c - 12.0, 28.0 - r)


def outline(points, iterations=1):
    return ccw(chaikin([head_px(c, r) for c, r in points], iterations))


# --- The drill ------------------------------------------------------------------------------------
# Its radius in plan along y (a third of a pixel inside the sprites' outlines): the shoulder under the head's
# collar, the broadest part (V 1 rows 23-27), the cone down V 39 to the point.
DRILL = Curve([(-27.95, 0.0), (-27.6, 0.45), (-26.0, 1.25), (-23.5, 2.3), (-20.5, 3.3), (-17.5, 4.3), (-14.0, 5.35),
               (-11.0, 6.35), (-7.5, 7.4), (-4.0, 8.5), (-1.5, 9.35), (0.5, 9.95), (2.5, 10.2), (4.3, 10.15),
               (5.6, 9.65), (6.7, 8.95), (7.8, 8.25), (8.9, 7.85), (10.0, 7.7), (11.2, 7.6)])
DRILL_TOP, DRILL_TIP = 11.2, -27.95
DRILL_SQUASH = 0.68     # its section's height over its width
AXIS_Z = 7.0            # the axis' height: the broadest part's underside just above the ground
# The flutes: how many start round it, how far down the axis one turns once, the groove's share of a flute's
# pitch round the drill and its depth (a fraction of the radius); they fade out up the shoulder (FLUTE_END).
STARTS, LEAD = 2, 11.0
GROOVE_SHARE, GROOVE_DEPTH = 0.42, 0.16
FLUTE_END = (5.0, 8.4)
DRILL_SEGMENTS = 48     # points round a section (24 per flute)
DRILL_STEP = 0.75

# --- The head -------------------------------------------------------------------------------------
# Outlines as (column, row) of V 1; heights (z) of each part's top, its underside, the rounding of its edges.
HOUSING = [(2.2, 2.2), (16.6, 2.0), (17.2, 8.0), (21.0, 9.4), (21.6, 12.0), (21.3, 16.4), (17.0, 17.3), (7.0, 17.3),
           (2.6, 16.6), (1.8, 9.0)]   # stepped in round the piston
HOUSING_Z = (0.0, 11.3, 1.2)
CROWN = [(9.3, 0.25), (13.3, 0.15), (16.3, 0.8), (16.7, 4.0), (16.6, 8.7), (9.2, 8.7), (8.9, 4.0)]
CROWN_Z = (6.0, 16.2, 0.8)
SHOULDER = [(2.6, 1.3), (8.6, 1.0), (8.9, 4.0), (8.9, 9.8), (5.6, 10.2), (2.6, 9.8), (1.15, 7.6), (1.2, 3.6)]
SHOULDER_Z = (5.0, (12.8, 15.1), 0.95)     # its top slopes up from its outer to its inner edge
CHEEK_L = [(1.6, 8.6), (6.0, 8.8), (6.4, 13.0), (6.6, 16.9), (3.2, 17.1), (1.9, 15.6), (1.5, 12.0)]
CHEEK_L_Z = (4.0, 12.9, 0.8)
HATCH = [(6.2, 9.3), (12.0, 9.3), (12.0, 16.4), (6.4, 16.4)]   # the opening between the plates
HATCH_Z = (3.0, 9.0, 0.6)                   # the grey block inside it
HATCH_LID = (9.3, 11.6, 0.7)                # its lighter upper part (rows), raised this much
MIDDLE = [(11.9, 8.5), (16.4, 8.5), (16.3, 13.0), (16.0, 17.2), (12.0, 17.2)]
MIDDLE_Z = (4.0, 13.5, 0.7)
CHEEK_R = [(16.2, 7.8), (19.4, 8.6), (22.2, 11.2), (22.4, 14.6), (21.4, 16.6), (16.2, 17.1)]
CHEEK_R_Z = (4.0, 12.9, 0.8)
CHAMFER = ((17.0, 9.6), (21.0, 13.6), 1.6)  # the right cheek's diagonal edge (column, row): beyond it (up to the
                                            # right) its top drops this much, towards the piston
# The piston on the right: its axis (column, row) from its foot under the cheek to its end, its height, radius,
# the ribs (count, depth).
PISTON = ((19.4, 11.0), (19.8, 3.4), 10.6, 1.9, (5, 0.34))
# The collar round the drill under the head (row 17): its y, its half-width along y, its radius in plan.
COLLAR = (10.9, 0.75, 8.45)


def drill_radius(y):
    return DRILL(min(max(y, DRILL_TIP), DRILL_TOP))


def flute_profile(u):
    """How far (0-1 of GROOVE_DEPTH) the surface sinks at u (0-1 round one flute's pitch): a rounded groove
    over GROOVE_SHARE of it, steeper on its leading side."""
    if u >= GROOVE_SHARE:
        return 0.0
    t = u / GROOVE_SHARE
    return math.sin(math.pi * t ** 0.8) ** 1.3


def drill(mats, turn):
    """The drill: sections along y whose points follow the flutes' helix, closed at the point and at the top."""
    ys = []
    y = DRILL_TIP + 0.35
    while y < DRILL_TOP:
        ys.append(y)
        y += DRILL_STEP if y < 4.0 else 0.45
    ys.append(DRILL_TOP)
    rings, kinds = [], []
    n = DRILL_SEGMENTS
    for y in ys:
        r = drill_radius(y)
        fade = 1.0 - smoothstep(FLUTE_END[0], FLUTE_END[1], y)
        twist = 2 * math.pi * (y / LEAD) + math.radians(turn)
        ring = []
        for j in range(n):
            u = (j * STARTS / n) % 1.0
            sink = GROOVE_DEPTH * flute_profile(u) * fade
            a = 2 * math.pi * j / n + twist
            rr = r * (1.0 - sink)
            ring.append(Vector((AXIS_X + rr * math.cos(a), y, AXIS_Z + DRILL_SQUASH * rr * math.sin(a))))
        rings.append(ring)
    obj = k.loft("drill", rings, None, start_point=(AXIS_X, DRILL_TIP, AXIS_Z), end_point=(AXIS_X, DRILL_TOP, AXIS_Z))
    for key in ("steel", "groove", "edge", "steel_dark"):
        obj.data.materials.append(mats[key])
    for poly in obj.data.polygons:
        if poly.index >= (len(rings) - 1) * n:
            poly.material_index = 0
            continue
        i, j = divmod(poly.index, n)
        u = ((j + 0.5) * STARTS / n) % 1.0
        y = poly.center.y
        if y > FLUTE_END[1] - 0.5:
            poly.material_index = 3 if y > 9.6 else 0
        elif u < GROOVE_SHARE * 0.92:
            poly.material_index = 1
        elif u < GROOVE_SHARE + 0.07:
            poly.material_index = 2   # the flute's edge, catching the light
        else:
            poly.material_index = 0
    return k.smooth(obj, 50)


def collar(mats):
    """The dark ring under the head that holds the drill."""
    y, half, radius = COLLAR
    rings = []
    profile = [(-half, radius - 0.3), (-half * 0.6, radius + 0.35), (0.0, radius + 0.55), (half * 0.6, radius + 0.35),
               (half, radius - 0.3)]
    for dy, r in profile:
        rings.append([Vector((AXIS_X + r * math.cos(2 * math.pi * j / 40), y + dy,
                              AXIS_Z + DRILL_SQUASH * r * math.sin(2 * math.pi * j / 40))) for j in range(40)])
    obj = k.loft("collar", rings, mats["blue_dark"], start_point=(AXIS_X, y - half, AXIS_Z),
                 end_point=(AXIS_X, y + half, AXIS_Z))
    return k.smooth(obj, 60)


EDGE_LIGHT = 0.95      # the light band along a plate's left edge (catching the light from the upper left)


def plate(name, points, z, mats, paint=None, sloped=None, spacing=0.5, band=1.0, borders=(), iterations=1,
          top_key="blue", lit_edge=True, holes=()):
    """An armour plate: a relief over the outline (column, row of V 1), its top at z (or sloping: sloped(x, y)),
    its edge rounded; painted top_key, a light band along its left edge (lit_edge). holes: outlines cut out."""
    bottom, top, rnd = z
    poly = outline(points, iterations)
    left = min(p[0] for p in poly) + EDGE_LIGHT

    def height(x, y, d):
        t = sloped(x, y) if sloped else top
        return t - rnd + rnd * round_edge(d, rnd)

    def default_paint(x, y, d):
        if d < 0.12:
            return "blue_dark"
        return "blue_edge" if lit_edge and x < left else top_key

    edge_borders = [(lambda x, y, d: d, 0.12)] + ([(lambda x, y, d: x, left)] if lit_edge else [])
    return relief(name, [poly] + [outline(h, 1) for h in holes], height, mats, paint=paint or default_paint,
                  side="blue_dark", bottom=bottom, spacing=spacing, band=band,
                  borders=list(borders) + edge_borders, smooth_angle=50)


def head(mats):
    plate("housing", HOUSING, HOUSING_Z, mats, spacing=0.75, band=1.2, top_key="blue_dark", lit_edge=False,
          holes=[HATCH])
    plate("crown", CROWN, CROWN_Z, mats, top_key="blue_light")
    (sx0, sy), (sx1, _) = head_px(1.2, 0), head_px(8.9, 0)
    low, high = SHOULDER_Z[1]
    plate("shoulder", SHOULDER, (SHOULDER_Z[0], high, SHOULDER_Z[2]), mats,
          sloped=lambda x, y: low + (high - low) * smoothstep(sx0, sx1, x))
    plate("cheek_l", CHEEK_L, CHEEK_L_Z, mats)
    plate("middle", MIDDLE, MIDDLE_Z, mats, top_key="blue_light")
    # The right cheek, its upper right corner dropping along the chamfer, a light band along the chamfer's edge.
    (c0, r0), (c1, r1), drop = CHAMFER
    ax, ay = head_px(c0, r0)
    bx, by = head_px(c1, r1)

    def chamfer_s(x, y, d=0.0):
        """Signed distance from the chamfer's line, positive towards the cheek's upper right corner."""
        nx, ny = -(by - ay), (bx - ax)
        return ((x - ax) * nx + (y - ay) * ny) / math.hypot(nx, ny)

    def chamfer(x, y):
        return CHEEK_R_Z[1] - drop * smoothstep(-0.3, 2.2, chamfer_s(x, y))

    def cheek_paint(x, y, d):
        s = chamfer_s(x, y)
        if d < 0.12:
            return "blue_dark"
        if -0.45 < s < 0.45:
            return "blue_edge"
        return "blue_dark" if s > 0.45 else "blue"

    plate("cheek_r", CHEEK_R, CHEEK_R_Z, mats, sloped=chamfer, paint=cheek_paint,
          borders=[(chamfer_s, -0.45), (chamfer_s, 0.45)])
    # The grey block in the hatch, its upper part lighter and raised.
    lid_y0 = head_px(0, HATCH_LID[1])[1]
    bottom, top, rnd = HATCH_Z

    def hatch_height(x, y, d):
        z = top - rnd + rnd * round_edge(d, rnd)
        return z + HATCH_LID[2] * smoothstep(lid_y0 - 0.3, lid_y0 + 0.3, y)

    relief("hatch", [outline(HATCH, 1)], hatch_height, mats,
           paint=lambda x, y, d: "grey_light" if y > lid_y0 else "grey", side="grey_dark", bottom=bottom,
           spacing=0.5, band=1.0, borders=[(lambda x, y, d: y, lid_y0)], smooth_angle=50)
    piston(mats)
    collar(mats)


def piston(mats):
    """The grey ribbed piston on the right: a cylinder along its axis, ribbed, its end rounded."""
    (c0, r0), (c1, r1), z, radius, (ribs, rib_depth) = PISTON
    a, b = Vector((*head_px(c0, r0), z)), Vector((*head_px(c1, r1), z))
    axis = (b - a)
    length = axis.length
    axis.normalize()
    side = axis.cross(Vector((0, 0, 1))).normalized()
    up = side.cross(axis).normalized()
    rings = []
    steps = 30
    for i in range(steps + 1):
        t = i / steps
        s = t * length
        rr = radius
        if t > 0.18:  # the ribbed part
            phase = (t - 0.18) / 0.82 * ribs
            rr -= rib_depth * (0.5 - 0.5 * math.cos(2 * math.pi * phase))
        if t > 0.92:  # the rounded end
            rr *= math.sqrt(max(0.0, 1.0 - ((t - 0.92) / 0.08) ** 2)) * 0.6 + 0.4
        centre = a + axis * s
        rings.append([centre + (side * math.cos(2 * math.pi * j / 20) + up * math.sin(2 * math.pi * j / 20)) * rr
                      for j in range(20)])
    obj = k.loft("piston", rings, mats["grey"], start_point=a, end_point=b + axis * 0.2)
    obj.data.materials.append(mats["grey_light"])
    for poly in obj.data.polygons:
        if poly.normal.z > 0.75:
            poly.material_index = 1
    return k.smooth(obj, 55)


def materials():
    blue = dict(metallic=0.45, roughness=0.3)
    steel = dict(metallic=0.6, roughness=0.28)
    return {
        "blue": k.material("drill_blue", palette=0x38, **blue),
        "blue_light": k.material("drill_blue_light", palette=0x39, **blue),
        "blue_edge": k.material("drill_blue_edge", palette=0x3c, metallic=0.45, roughness=0.24),
        "blue_dark": k.material("drill_blue_dark", palette=0x35, **blue),
        "grey": k.material("drill_grey", palette=0x08, **steel),
        "grey_light": k.material("drill_grey_light", palette=0x0b, **steel),
        "grey_dark": k.material("drill_grey_dark", palette=0x04, **steel),
        "steel": k.material("drill_steel", palette=0x0a, metallic=0.5, roughness=0.25),
        "groove": k.material("drill_groove", palette=0x06, metallic=0.5, roughness=0.35),
        "edge": k.material("drill_edge", palette=0x0c, metallic=0.5, roughness=0.2),
        "steel_dark": k.material("drill_steel_dark", palette=0x05, **steel),
    }


# --- Build ----------------------------------------------------------------------------------------

def whole_mask(sheet, sprites):
    """The two sprites' silhouettes, the head above the bit: 24 x 56."""
    head_mask, bit_mask = k.sprite_mask(sheet, sprites[0]), k.sprite_mask(sheet, sprites[1])
    return head_mask + bit_mask


def build():
    options = k.args()
    outdir = options.get("outdir", os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "enemies"))
    sheets = options.get("check")
    sheet = None
    if sheets:
        sheet = os.path.join(sheets, "enemy_V.png") if os.path.isdir(sheets) else sheets
    for f, (sprites, turn) in enumerate(FRAMES):
        k.reset()
        mats = materials()
        head(mats)
        drill(mats, turn)
        whole = [o for o in bpy.context.scene.objects if o.type == "MESH"]
        used = {m.name for o in whole for m in o.data.materials}
        zs = [v.co.z for o in whole for v in o.data.vertices]
        print("== whole machine (V %d above %d): %d triangles, %d objects, %d materials, z %.2f to %.2f" % (
            *sprites, triangles(whole), len(whole), len(used), min(zs), max(zs)))
        if sheet:
            check_mask(whole_mask(sheet, sprites), "whole (V %d above %d)" % sprites, whole)
        if "preview" in options:
            preview(options["preview"] + "drillrig_whole" + ("" if f == 0 else "_%d" % sprites[0]), whole,
                    size=(24, 56), scale=10, distance=1.6)
        for (name, first, box, centre), sprite in zip(PIECES, sprites):
            model = name if sprite == first else "%s_%d" % (name, sprite)
            pieces = [p for p in (cut(src, box, mats["grey_dark"]) for src in whole) if p is not None]
            move(pieces, 0.0, -centre)
            used = {m.name for o in pieces for m in o.data.materials}
            print("== %s (V %d): %d triangles, %d materials: %s" % (model, sprite, triangles(pieces), len(used),
                                                                   ", ".join(sorted(used))))
            if sheet:
                check_mask(k.sprite_mask(sheet, sprite), "%s (V %d)" % (model, sprite), pieces)
            export(pieces, os.path.join(outdir, model + ".glb"))
            if "preview" in options:
                preview(options["preview"] + model, pieces)
            for obj in pieces:
                bpy.data.objects.remove(obj)


if __name__ == "__main__":
    build()
