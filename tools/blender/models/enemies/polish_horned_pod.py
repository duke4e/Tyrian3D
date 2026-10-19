"""The grey steel pod with two curved horns of SURFACE, COLLECTOR and ROOST (sheet 3 sprite 1, 2x2: 22 x 27 pixels in
the 24 x 28 cell; enemy 201, sky layer: 50 in SURFACE, 21 in COLLECTOR and ROOST; static), polished (2026-10-19;
it replaces wave3_n.py's horned_pod()). models.cfg: sprite 3 1 horned_pod yaw=0.

As the 4x upscale draws it: grey steel (the sprite's ramp 0, 0x03-0x0f) outlined in a dark brown (0x12). The pod's
body below (rows 14-26): a ribbed dome (columns 5-18 of rows 14-21), split down its middle by a dark seam, each
half bulging with its own highlight; round its lower half a bright collar (its front lip along row 22) and under
it a skirt with two feet either side of a notch (columns 7-9 and 14-16 of rows 23-26). Across the body's top end a
deck (rows 12-13) carries a tower in the middle (columns 9-14 of rows 3-13: a pale head with a dark visor, a
darker panel with a slot below it) and the two horns: curved steel blades rising up the screen (columns 1-7 and
16-22, their points at row 0), each with a straight inner edge, a convex outer edge and a ridge sweeping along
it.

The pod is assembled from solids: the skirt, the collar and the dome (a relief of two bulging halves either side of
the seam), the deck, the tower (a block with a sunk visor and panel) and the horns (blades whose ridge follows
their outer edge, rising towards the points). Steel in the sprite's greys: lighter on the crests, darker in the
seams and the visor.

Origin at the sprite's centre (pixel 12, 14); +Y up the sprite, +Z towards the camera; the game centres sky objects
in height. The sprite is symmetric about x = 0 (between columns 11 and 12): the parts are built on the left and
mirrored where they come in pairs.

Replaces wave3_n.py's horned_pod() (its @n.model("horned_pod") entry): remove it so that it doesn't overwrite this
model.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouette against
enemy_3.png), --preview <prefix>.
"""
import math
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
from polish_ring_machine import ccw, chaikin, mirrored, relief, round_edge  # noqa: E402
from polish_sphere_nozzle import smoothstep  # noqa: E402


def px(c, r):
    """A point given as (column, row) of the sprite's pixel grid (its corners) in model coordinates."""
    return (c - 12.0, 14.0 - r)


def outline(points, iterations=2):
    return ccw(chaikin([px(c, r) for c, r in points], iterations))


def symmetric(left):
    """A closed outline from its left half (column, row), top middle to bottom middle, mirrored."""
    pts = [px(c, r) for c, r in left]
    return ccw(chaikin(pts + mirrored(pts), 2))


# --- The body ------------------------------------------------------------------------------------
# The skirt under the collar (rows 21-26.5), its two feet either side of the notch (columns 9.5-14.5 of rows
# 24-26.5): the outline's left half, from under the dome's middle down round the foot to the notch.
SKIRT = [(12.0, 19.0), (8.0, 19.0), (4.5, 19.6), (3.2, 21.0), (3.35, 22.7), (4.2, 23.9), (5.2, 25.0), (6.3, 26.1),
         (7.3, 26.75), (9.7, 26.75), (10.5, 26.2), (11.0, 25.6), (12.0, 25.5)]
SKIRT_Z = (-1.0, 2.0, 1.3)          # its underside, its top, the rounding of its edge
# The collar round the dome's lower half (a U open at the top, under the deck): its outer edge and its inner edge
# (the dome's foot), left halves from the top down to the middle.
COLLAR_OUTER = [(3.6, 15.4), (3.1, 16.4), (3.05, 18.5), (3.15, 20.5), (3.8, 21.9), (5.2, 22.9), (7.2, 23.5),
                (9.6, 23.75), (12.0, 23.8)]
COLLAR_INNER = [(5.7, 15.4), (5.5, 16.6), (5.6, 18.2), (6.2, 19.6), (7.4, 20.7), (9.3, 21.4), (12.0, 21.6)]
COLLAR_Z = (0.5, 4.3, 0.95)         # its underside, its crest, its rounding (from either edge)
# The dome: its outline (a half disc under the deck), its foot's height, its rise, the seam down its middle
# (half-width, depth) and how much each half bulges on its own (LOBE: the halves' middles, x).
DOME = [(12.0, 13.8), (8.0, 13.8), (5.9, 14.2), (5.75, 16.3), (6.0, 18.0), (6.7, 19.4), (8.0, 20.6), (9.9, 21.4),
        (12.0, 21.7)]
DOME_FOOT, DOME_RISE = 2.4, 5.6
SEAM_HALF, SEAM_DEPTH = 0.55, 1.1
LOBE_X, LOBE_BULGE = 3.4, 0.55

# --- The top: the deck, the tower, the horns -------------------------------------------------------
DECK = [(1.6, 11.4), (12.0, 11.2), (22.4, 11.4), (22.5, 13.0), (21.5, 14.3), (12.0, 14.4), (2.5, 14.3), (1.5, 13.0)]
DECK_Z = (2.5, 5.6, 1.0)
TOWER = [(8.95, 2.95), (15.05, 2.95), (15.05, 13.6), (8.95, 13.6)]
TOWER_Z = (3.0, 9.6, 1.0)
# The tower's face: the visor (a dark slot across its upper part), the pale head round it, the darker panel
# below: (column, row) boxes and depths.
VISOR = ((10.2, 4.1), (13.8, 6.7), 0.75)
HEAD = (3.25, 8.9)                  # the head's rows; below it the panel
PANEL = ((10.1, 9.6), (13.9, 13.2), 0.45)
# The left horn: its outline (column, row): the point, down the straight inner edge, round the convex outer edge;
# its underside, its crest's height above the underside at the root and at the point, the rounding of its edge.
HORN = [(6.2, -0.05), (7.6, 0.1), (7.9, 1.2), (7.9, 5.0), (7.9, 8.0), (7.95, 11.0), (8.0, 13.2), (6.0, 13.6),
        (3.5, 13.5), (1.8, 13.0), (1.15, 11.5), (1.2, 9.5), (1.7, 7.6), (2.6, 5.6), (3.7, 3.6), (4.9, 1.5)]
HORN_BOTTOM = 3.2
HORN_CREST = (3.6, 2.4)
HORN_ROUND = 2.6
HORN_RISE = 2.4                     # the point rises this much above the root (the horn sweeps up)
# The ridge along the blade, inside its outer edge: its distance from the outer edge (in units of the blade's
# width there) and its sharpness.
RIDGE_AT, RIDGE_SHARP = 0.42, 2.2

SPACING = 0.42
BAND = 1.3          # grid points farther than this from an outline: on a lattice twice as coarse


def body(m):
    skirt_bottom, skirt_top, skirt_round = SKIRT_Z
    relief("skirt", [symmetric(SKIRT)], lambda x, y, d: skirt_top - 0.8 + 0.8 * round_edge(d, skirt_round), m,
           paint=lambda x, y, d: "steel_dark" if d < 0.45 else "steel", side="steel_dark", bottom=skirt_bottom,
           spacing=0.5, borders=[(lambda x, y, d: d, 0.45)], smooth_angle=55, band=1.0)

    collar_bottom, collar_top, collar_round = COLLAR_Z
    outer = [px(c, r) for c, r in COLLAR_OUTER]
    inner = [px(c, r) for c, r in COLLAR_INNER]
    # The U: down the outer edge's left half, up its right half, down the inner edge's right half, up its left.
    ring = ccw(outer + [(-x, y) for x, y in reversed(outer[:-1])] + [(-x, y) for x, y in inner[:-1]] +
               list(reversed(inner)))

    def collar_height(x, y, d):
        return collar_top - 1.6 + 1.6 * round_edge(d, collar_round)

    def collar_paint(x, y, d):
        return "steel_shine" if d > 0.55 * collar_round and y < -6.0 else "steel_light" if d > 0.4 else "seam"

    relief("collar", [ring], collar_height, m, paint=collar_paint, side="seam", bottom=collar_bottom,
           spacing=0.5, borders=[(lambda x, y, d: d, 0.4), (lambda x, y, d: d, 0.55 * collar_round)],
           smooth_angle=60, band=BAND)

    dome = symmetric(DOME)
    lobe = lambda x, y: math.exp(-((abs(x) - LOBE_X) / 3.2) ** 2 - ((y + 3.5) / 4.0) ** 2)

    def dome_height(x, y, d):
        # A quarter ellipse rising from the foot to the top, each half bulging, the seam sunk along x = 0.
        z = DOME_FOOT + DOME_RISE * round_edge(d, 5.2) + LOBE_BULGE * lobe(x, y) * round_edge(d, 2.0)
        return z - SEAM_DEPTH * max(0.0, 1.0 - (abs(x) / SEAM_HALF) ** 2) ** 0.6 * smoothstep(0.0, 1.6, d)

    def dome_paint(x, y, d):
        return "seam" if abs(x) < SEAM_HALF * 0.85 else "dome"

    relief("dome", [dome], dome_height, m, paint=dome_paint, side="seam", bottom=0.6, spacing=0.46,
           borders=[(lambda x, y, d: abs(x), SEAM_HALF * 0.85)], smooth_angle=60, band=2.2)


def deck(m):
    bottom, top, rnd = DECK_Z
    relief("deck", [outline(DECK, 1)], lambda x, y, d: top - rnd + rnd * round_edge(d, rnd), m,
           paint=lambda x, y, d: "steel_light" if d > 0.5 else "steel", side="steel_dark", bottom=bottom,
           spacing=0.46, borders=[(lambda x, y, d: d, 0.5)], smooth_angle=55, band=1.1)


def tower(m):
    bottom, top, rnd = TOWER_Z
    (v0c, v0r), (v1c, v1r), visor_depth = VISOR
    (p0c, p0r), (p1c, p1r), panel_depth = PANEL
    vx0, vy1 = px(v0c, v0r)
    vx1, vy0 = px(v1c, v1r)
    qx0, qy1 = px(p0c, p0r)
    qx1, qy0 = px(p1c, p1r)

    def box_d(x, y, x0, x1, y0, y1):
        """Inside distance to a box's edge (negative outside)."""
        return min(x - x0, x1 - x, y - y0, y1 - y)

    def height(x, y, d):
        z = top - rnd + rnd * round_edge(d, rnd)
        z -= visor_depth * smoothstep(-0.05, 0.35, box_d(x, y, vx0, vx1, vy0, vy1))
        z -= panel_depth * smoothstep(-0.05, 0.35, box_d(x, y, qx0, qx1, qy0, qy1))
        return z

    head_y = px(0, HEAD[1])[1]

    def paint(x, y, d):
        if box_d(x, y, vx0, vx1, vy0, vy1) > 0.1:
            return "visor"
        if box_d(x, y, qx0, qx1, qy0, qy1) > 0.1:
            return "steel_dark"
        if d < 0.35:
            return "steel"
        return "steel_pale" if y > head_y else "steel_light"

    relief("tower", [outline(TOWER, 1)], height, m, paint=paint, side="steel_dark", bottom=bottom, spacing=0.46,
           borders=[(lambda x, y, d: box_d(x, y, vx0, vx1, vy0, vy1), 0.1),
                    (lambda x, y, d: box_d(x, y, qx0, qx1, qy0, qy1), 0.1),
                    (lambda x, y, d: d, 0.35), (lambda x, y, d: y, head_y)],
           smooth_angle=50)


def horns(m):
    poly = outline(HORN, 2)
    inner_x = px(7.9, 0)[0]                       # the straight inner edge
    xs = [p[0] for p in poly]
    left_x = min(xs)
    ys = [p[1] for p in poly]
    y_root, y_tip = min(ys), max(ys)

    def outer_x(y):
        """The outer edge's x at y (the leftmost outline point near y)."""
        best = None
        for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1]):
            if (y0 - y) * (y1 - y) <= 0 and y0 != y1:
                x = x0 + (x1 - x0) * (y - y0) / (y1 - y0)
                best = x if best is None else min(best, x)
        return best if best is not None else left_x

    def across(x, y):
        """0 on the outer edge, 1 on the inner edge."""
        ox = outer_x(y)
        return min(1.0, max(0.0, (x - ox) / max(inner_x - ox, 0.3)))

    def height(x, y, d):
        t = (y - y_root) / (y_tip - y_root)
        crest = HORN_CREST[0] + (HORN_CREST[1] - HORN_CREST[0]) * t
        u = across(x, y)
        ridge = math.exp(-RIDGE_SHARP * ((u - RIDGE_AT) / 0.5) ** 2)
        z = HORN_BOTTOM + HORN_RISE * t ** 1.5 + crest * (0.55 + 0.45 * ridge) * round_edge(d, HORN_ROUND)
        return z

    def paint(x, y, d):
        u = across(x, y)
        if d < 0.3:
            return "seam"
        if abs(u - RIDGE_AT) < 0.16:
            return "steel_shine"
        return "steel_light" if u > RIDGE_AT else "steel_dark"

    left = relief("horn_l", [poly], height, m, paint=paint, side="seam", bottom=HORN_BOTTOM - 0.5, spacing=0.47,
                  borders=[(lambda x, y, d: d, 0.3), (lambda x, y, d: across(x, y), RIDGE_AT - 0.16),
                           (lambda x, y, d: across(x, y), RIDGE_AT + 0.16)], smooth_angle=55, band=1.6)
    right = k.mirror_x(left, "horn_r")
    right.data.name = "horn_r"
    k.smooth(right, 55)


def materials():
    steel = dict(metallic=0.6, roughness=0.28)
    return {
        "steel": k.material("hpod_steel", palette=0x07, **steel),
        "steel_light": k.material("hpod_steel_light", palette=0x09, **steel),
        "steel_shine": k.material("hpod_steel_shine", palette=0x0c, metallic=0.6, roughness=0.2),
        "steel_pale": k.material("hpod_steel_pale", palette=0x0b, **steel),
        "steel_dark": k.material("hpod_steel_dark", palette=0x05, **steel),
        "dome": k.material("hpod_dome", palette=0x0a, metallic=0.6, roughness=0.2),
        "seam": k.material("hpod_seam", palette=0x12, metallic=0.3, roughness=0.55),
        "visor": k.material("hpod_visor", palette=0x02, metallic=0.4, roughness=0.15),
    }


def triangles():
    depsgraph = bpy.context.evaluated_depsgraph_get()
    total = 0
    for obj in bpy.context.scene.objects:
        if obj.type == "MESH":
            evaluated = obj.evaluated_get(depsgraph)
            mesh = evaluated.to_mesh()
            mesh.calc_loop_triangles()
            total += len(mesh.loop_triangles)
            evaluated.to_mesh_clear()
    return total


def build():
    options = k.args()
    outdir = options.get("outdir", os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "enemies"))
    k.reset()
    m = materials()
    body(m)
    deck(m)
    tower(m)
    horns(m)
    used = {mat.name for o in bpy.context.scene.objects if o.type == "MESH" for mat in o.data.materials}
    zs = [v.co.z for o in bpy.context.scene.objects if o.type == "MESH" for v in o.data.vertices]
    print("== horned_pod (3 1): %d triangles, %d materials, z %.2f to %.2f" % (triangles(), len(used), min(zs),
                                                                              max(zs)))
    print("   " + ", ".join("%s %d" % (o.name, len(o.data.polygons)) for o in bpy.context.scene.objects
                            if o.type == "MESH"))
    sheet = options.get("check")
    if sheet:
        k.check_silhouette(os.path.join(sheet, "enemy_3.png") if os.path.isdir(sheet) else sheet, 1)
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    path = os.path.join(outdir, "horned_pod.glb")
    k.export(path)
    print("   horned_pod: %.1f KB" % (os.path.getsize(path) / 1024))
    if "preview" in options:
        k.preview(options["preview"] + "horned_pod")


if __name__ == "__main__":
    build()
