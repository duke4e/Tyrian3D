"""The slate-steel machine with two cyan windows of GRYPHON, MISTAKES, MIGRATION and STATION (sheet H
sprite 284, 2x2: 24 x 28 pixels; top layer, 105 of them; not animated), polished (2026-10-18; it
replaces wave2_f.py's twin_panel). models.cfg: sprite h 284 twin_panel yaw=0.

As the 4x upscale draws it (columns are the sprite's, rows from its top): a symmetric machine of dark
slate steel (the sprite's ramp 6), like a moth with folded wings. Two upright housings stand side by
side at its back (columns 5-10 and 13-18 of rows 1-9), a dark slot with a small knob between them
(columns 11-12), each with a tall cyan window (the sprite's ramp 13, columns 7-8 and 15-16 of rows
3-9) framed in light steel, its glass lightest across its middle (row 7). One light rim runs under
the windows (rows 10-11) and on down the front edges of the two wings to their tips (rows 12-15 at
columns 5 to 1 and 18 to 22): the wings droop from the body out and down, their tops ribbed (light
ribs at columns 2 and 4, rows 7-11), their fronts falling steeply from the rim (to row 16). Under the
rim's middle hangs a shield-shaped keel that narrows to a point (rows 12-20), a ridge down its middle
catching the light on its left (column 10).

The housings' tops slope down towards the front, so the windows face up and towards the game's
slanted camera.

Origin at the sprite's centre (pixel 12, 14); +Y up the sprite, +Z towards the camera (the game
centres top-layer objects in height).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the
silhouette against H 284's pixels, written below), --preview <prefix>.
"""
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402

# H 284's pixels ('#').
SPRITE = """
........................
......#####..#####......
.....##############.....
.....##############.....
...##################...
.######################.
########################
########################
########################
########################
########################
########################
########################
########################
########################
########################
########################
.......##########.......
........########........
.........######.........
..........####..........
........................
........................
........................
........................
........................
........................
........................
"""

# The body under the housings (columns 5-18 of rows 4-11) and its height.
HULL = [(-6.8, 1.6), (6.8, 1.6), (6.8, 9.0), (6.0, 9.8), (-6.0, 9.8), (-6.8, 9.0)]
HULL_TOP = 4.6
# The left housing (the right one is its mirror image): plan, and its top sloping from the back
# (y, z) to the front (y, z).
TOWER = [(-6.7, 3.3), (-1.25, 3.3), (-1.25, 12.0), (-1.95, 12.7), (-6.0, 12.7), (-6.7, 12.0)]
TOWER_BACK, TOWER_FRONT = (12.7, 9.3), (3.3, 7.4)
WINDOW = (-5.25, -2.75, 4.0, 11.6)     # x0, x1, y0, y1 (columns 7-8 of rows 2-9)
GLINT = (6.0, 7.1)                      # the lighter band across the glass (row 7), y
FRAME_X = 2.6                           # the light bar down each window's inner edge (columns 9 and 14)
SLOT = (1.3, 3.5, 12.05, 5.3)           # the dark slot between the housings: half width, y0, y1, top
KNOB = ((0.0, 5.3), 0.95)               # the small knob in it (row 8)
# The rim: from the left wing's tip up its front edge, across under the windows, down the right wing
# (x, y, z); its radius.
RIM = [(-11.55, -1.55, 1.75), (-9.2, 0.35, 2.75), (-6.9, 2.2, 3.85), (-6.1, 2.55, 4.55), (6.1, 2.55, 4.55),
       (6.9, 2.2, 3.85), (9.2, 0.35, 2.75), (11.55, -1.55, 1.75)]
RIM_R = 0.72
# The left wing (the right one mirrored), in sections from its root (inside the body) out to its tip:
# x, its back edge (y), the rim along its front (y), its top's height at the back and at the rim, its
# bottom's.
WING = [(-4.6, 10.0, 2.45, 4.0, 3.75, 1.2), (-7.1, 10.0, 2.05, 3.85, 3.55, 1.15), (-8.3, 9.85, 1.1, 3.5, 3.05, 1.0),
        (-9.5, 9.45, 0.15, 3.1, 2.6, 0.85), (-10.6, 8.85, -0.75, 2.75, 2.15, 0.7), (-11.67, 7.5, -1.6, 2.4, 1.75, 0.55)]
WING_FRONT, WING_LIP = -2.62, 0.55     # the front's lower edge (row 16): y, how far above the bottom
WING_RIBS = [(-7.75, 8.9, 2.6), (-9.45, 8.4, 1.0), (-11.0, 7.0, -0.8)]  # x, from y, to y (on the top)
# The keel: its half-width and its ridge's and sides' heights, from under the rim down to its point
# (rows 12-20).
KEEL = [(2.6, 5.15, 4.55, 3.3), (0.5, 5.15, 4.45, 3.1), (-1.5, 5.0, 4.2, 2.85), (-3.0, 4.65, 3.85, 2.55),
        (-4.2, 3.85, 3.5, 2.3), (-5.3, 2.8, 3.1, 2.05), (-6.2, 1.7, 2.7, 1.85),
        (-6.72, 0.5, 2.35, 1.75)]  # y, half-width, ridge, side


def materials():
    glow = k.level_palette()
    return {
        "hull": k.material("twinpanel_hull", palette=0x6a, metallic=0.55, roughness=0.28),
        "housing": k.material("twinpanel_steel", palette=0x69, metallic=0.55, roughness=0.3),  # housings, wings
        "trim": k.material("twinpanel_trim", palette=0x6c, metallic=0.6, roughness=0.24),
        "slot": k.material("twinpanel_slot", palette=0x62, metallic=0.3, roughness=0.6),
        "glass": k.material("twinpanel_glass", palette=0xd5, metallic=0.1, roughness=0.08, emission=glow[0xd5],
                            emission_strength=0.6),
        "glint": k.material("twinpanel_glint", palette=0xd9, metallic=0.1, roughness=0.08, emission=glow[0xd9],
                            emission_strength=0.8),
    }


def mirror(points):
    return [(-x, y) for x, y in reversed(points)]


def hull(m):
    body = mk.prism("hull", HULL, 0.0, HULL_TOP, m["hull"])
    mk.bevel(body, 0.7, 3, 35)
    mk.shade(body, 40)
    x, y0, y1, top = SLOT
    slot = mk.box("slot", -x, x, y0, y1, 0.0, top, m["slot"])
    mk.bevel(slot, 0.2, 2, 35)
    mk.shade(slot, 40)


def housings(m):
    (yb, zb), (yf, zf) = TOWER_BACK, TOWER_FRONT
    top = mk.plane((0, yb, zb), (1, yb, zb), (0, yf, zf))
    for side in (1, -1):
        plan = TOWER if side > 0 else mirror(TOWER)
        housing = mk.wedge(f"housing{side}", plan, 0.0, top, m["housing"])
        mk.bevel(housing, 0.45, 3, 35)
        mk.shade(housing, 40)
        x0, x1, y0, y1 = WINDOW
        xa, xb = sorted((side * x0, side * x1))
        glass = mk.wedge(f"window{side}", [(xa, y0), (xb, y0), (xb, y1), (xa, y1)], 0.0,
                         lambda x, y: top(x, y) + 0.16, m["glass"], bottom=lambda x, y: top(x, y) - 0.3)
        mk.bevel(glass, 0.12, 2, 35)
        mk.shade(glass, 40)
        g0, g1 = GLINT
        glint = mk.wedge(f"glint{side}", [(xa + 0.15, g0), (xb - 0.15, g0), (xb - 0.15, g1), (xa + 0.15, g1)], 0.0,
                         lambda x, y: top(x, y) + 0.22, m["glint"], bottom=lambda x, y: top(x, y) - 0.1)
        mk.shade(glint, 40, weighted=False)
        # The light frame bar down the window's inner edge.
        fx = side * -FRAME_X
        k.smooth(mk.tube(f"frame{side}", [(fx, y0, top(fx, y0) + 0.2), (fx, y1, top(fx, y1) + 0.2)], 0.38,
                         m["trim"], 10), 50)
    # The rim under the windows and down the wings' fronts.
    points = mk.chaikin(RIM, 2, closed=False)
    k.smooth(mk.tube("rim", points, RIM_R, m["trim"], 16), 50)
    (kx, ky), kr = KNOB
    mk.ball("knob", (kx, ky, SLOT[3] + 0.1), (kr, kr, 0.7), m["slot"], 16, 8)


def wing(name, side, m):
    """A wing: sections in (y, z) from its root out to its tip, its top falling from its back edge to
    the rim, its front falling steeply from the rim to its lower edge."""
    rings = []
    for x, y_back, y_rim, z_back, z_rim, z_bottom in WING:
        ring = [(WING_FRONT, z_bottom), (y_back, z_bottom), (y_back, z_back), (y_rim, z_rim),
                (WING_FRONT, z_bottom + WING_LIP)]
        rings.append([Vector((side * x, y, z)) for y, z in ring])
    obj = k.loft(name, rings, m["housing"])
    mk.bevel(obj, 0.3, 3, 30)
    mk.paint(obj, lambda c, n: m["hull"] if n.y < -0.5 else None)
    return mk.shade(obj, 40)


def wings(m):
    for side in (1, -1):
        wing_obj = wing(f"wing{side}", side, m)
        hit = mk.surface([wing_obj])
        for i, (rx, ya, yb) in enumerate(WING_RIBS):
            points, ups = [], []
            for j in range(12):
                h = hit(side * rx, ya + (yb - ya) * j / 11)
                if h is not None:
                    points.append(h[0])
                    ups.append(h[1])
            k.smooth(mk.bar(f"rib{side}_{i}", points, ups, 0.36, 0.3, 0.4, m["trim"], 12, 3.0), 40)


def keel(m):
    """Cross-sections from under the rim down to the point: a ridge along its middle."""
    rings = []
    for y, hw, ridge, side in KEEL:
        rings.append([Vector((-hw, y, 0.4)), Vector((hw, y, 0.4)), Vector((hw, y, side)),
                      Vector((hw * 0.5, y, (side + ridge) / 2 + 0.1)), Vector((0.0, y, ridge)),
                      Vector((-hw * 0.5, y, (side + ridge) / 2 + 0.1)), Vector((-hw, y, side))])
    obj = k.loft("keel", rings, m["hull"])
    mk.bevel(obj, 0.3, 2, 30)
    mk.shade(obj, 40)


def build():
    options = k.args()
    k.reset()
    m = materials()
    hull(m)
    housings(m)
    wings(m)
    keel(m)
    parts = mk.meshes()
    if "check" in options:
        mk.compare("twin_panel (H 284)", mk.coverage(parts, 24, 28),
                   [[c == "#" for c in line] for line in SPRITE.strip().splitlines()])
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    mk.report("twin_panel", parts, os.path.join(mk.outdir(options), "twin_panel.glb"))
    if "preview" in options:
        mk.preview(options["preview"] + "twin_panel", parts)


if __name__ == "__main__":
    build()
