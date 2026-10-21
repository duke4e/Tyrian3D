"""IXMUCANE's and SAWBLADES' red ship docked between two grey engines (sheet 8 sprites 39, 41, 43 above 77, 79, 81,
2x2 each: one 72 x 56 picture; enemies 434-439 of episode 3, one frame each, armour 40 each), polished (2026-10-21; it
replaces wave3_y_boss.py's dock: rounded boxes for the engines, an egg for the dome, a lofted keel with three slabs).
models.cfg: model ixm_dock_tl / _tc / _tr / _bl / _bc / _br enemies/ixm_dock_*.glb origin (unchanged); sprite 8 39
ixm_dock_tl yaw=0, 41 _tc, 43 _tr, 79 _bc unchanged; sprite 8 77 ixm_dock_bl yaw=0 glow=14:0.2:119:2.5:2.9 and sprite
8 81 ixm_dock_br yaw=0 glow=14:0.2:119:-2.5:3.9 (the halo moved onto the exhaust grilles). No other enemy shows these
sprites, and none is another sprite's pixels mirrored, turned or in other ramps (twins2.py); the right engine is the
left one mirrored, though, as below.

The levels lay the six out as the sheet does (IXMUCANE's events 7 at 1100-2630: enemies 434, 435, 436 at x, x + 24,
x + 48, 28 pixels above 437, 438, 439, all on the top layer; SAWBLADES' events 15 at 700-3300, the same in the sky);
each piece is an enemy of its own (armour 40), so any of them can be shot away alone. No episode 6 level takes them.

As the sprites and their 4x upscales draw it (columns c 0-71 and rows r 0-55 of the 72 x 56 picture):
- Two engines (columns 3-23 and 48-68, rows 11-53 and 11-54): grey blocks (ramp 0), the right one the left one
  mirrored about the picture's middle (x = 0), but a row longer: from row 28 down it is drawn a pixel lower (its last
  louvre slat a row taller). From their front (the top of the screen) back: two red caps on the front edge (ramp 4: a
  wide one outside, columns 6-14, a small one inside, 18-20, rows 12-13, a gap between); the louvred vent (rows 18-27,
  columns 8-17: five lit slats with dark gaps between, their ends running on over the dark chamfer of the outer edge,
  columns 4-7); a raised square panel lit along its left edge (columns 10-18 of rows 28-32); a red light, a slot
  across (columns 11-17 of rows 33-34); a ledge (rows 35-38); a dark seam (row 39); at the back the exhaust grille in a
  rounded housing: five glowing tubes along the screen (rows 40-48, hot down their middles at columns 8, 11, 14, 17
  and 20: 0x7a-0x7f, cooler between: 0x71-0x77), the well dark red behind them (rows 49-50), the housing's lit rim
  round the back with two notches, its outer bar standing free (column 5 of rows 41-48 is transparent: a slot right
  through), and a rail along the engine's inner side (column 23 of rows 21-48).
- Between them the red ship (ramp 4, symmetric about column 35, x = -0.5, lit from the left): a head block (columns
  32-38 of rows 17-22, a lip a pixel wider at its front, a ridge down its middle between two grooves); the first cross
  bar (columns 29-41 of rows 23-25) with its ends bent back (columns 29 and 41 down to row 26); a neck (columns 33-37);
  the second cross bar (columns 28-42 of rows 31-34); the wings, the widest (columns 25-45 of rows 35-37, touching the
  engines' rails), their trailing edges sweeping in along the tail to a spike (column 35 of rows 47-54); a lit ridge
  down the middle of it all.
- Under its head a grey dome (columns 25-45 of rows 6-16: glossy, near black, lit at its upper left, a groove down
  its middle with a lit edge); under its tail two grey pods, teardrops leaning in to the spike (columns 27-33 and
  37-43 of rows 40-51); grey clamps holding the wings' tips to the engines (columns 23-25 and 45-48 of rows 39-41).

Built as such a machine: CAD-like solids (polish_machine_kit: plans and sections extruded and intersected by exact
booleans, pockets, slots and grooves cut, edges bevelled, flat faces kept flat). The engines are blocks 11 pixels
high (their outer top edge a broad chamfer), the caps rounded bars on their front edges, the louvres a pocket through
the top and the chamfer with five slats in it following the block's section (each tilted a little, its back edge up),
the panel a bevelled plate in a shallow pocket, the red light a glowing lens in a slot, the grille a well 4.7 deep
with five glowing tubes (painted in heat bands: hot along their tops, cooler down their sides) between dim fins, the
outer bar's slot cut right through; the right engine is built the same way, mirrored, its back a pixel longer. The
ship is a stack of plates on a keel: a lofted ridge from the head to the spike, the head a bevelled block, the cross
bars and the arrowhead of the wings and tail wedges whose tops fall away down the screen (so their fronts catch the
light, as the sprite's bright upper rows), the wings drooping to the engines' rails; the dome a glossy half
ellipsoid with a groove cut down its middle; the pods glossy ellipsoids leaning in, tucked under the tail.
Colours are the sprites' palette indices: the engines ramp 0 (tops 0x07, slats 0x09, rims and the rails 0x0a, lit
bevels 0x0c, chamfers and walls 0x05, gaps and pocket floors 0x02), the caps, the ship and the light ramp 4 (0x42-0x4c,
the light 0x47 glowing 0.35), the grille ramp 7 (the tubes in heat bands 0x74, 0x77, 0x7a, 0x7d glowing 0.22, 0.32,
0.45, 0.6, the fins 0x72 at 0.12, the well 0x40), the dome ramp 0 (0x03, 0x05, 0x07, 0x0a) and the pods a little
lighter (0x04, 0x06, 0x08, 0x0b), glossy, banded by how much they face a light from the upper left
(polish_orb_red.band_split), glowing 0.06-0.08 so that they don't read black from the slanted camera. Emission stays
well under 1 (the game's bloom and the glow halo add to it). The engines' blocks are shaded flat (their big tops,
cut into many faces by the pockets, would take the bevels' normals at their edges and streak the light).

The whole is then cut along the sprites' edges (x = -12 and 12, y = 0; polish_savara_boss.cut: the cuts capped, the
faces' winding kept; the pieces keep the whole's shading across the cuts, its corner normals looked up on the source
triangle in each face's own plane (Shading: the nearest triangle, at a crease between flat faces, can be the
neighbour's)), each piece moved so that its sprite's centre is its origin; every mesh is triangulated before export
(polish_k_pod.triangulate) and each piece's parts are joined into one mesh (polish_deli_boss.join).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up (towards the camera) from the
layer (z = 0); the whole's origin is the picture's middle (pixel edge 36, 28): column c's left edge is x = c - 36,
row r's top edge y = 28 - r. The pieces' centres: 39 (-24, 14), 41 (0, 14), 43 (24, 14), 77 (-24, -14), 79 (0, -14),
81 (24, -14).

Replaces wave3_y_boss.py's dock: remove its section ("# --- 8 39 41 43 / 77 79 81: the docked ship": BOSS, AX,
dock_mats(), engine(), build_dock(), _DOCK and the y.pieced("ixm_dock", ...) registration) and the ixm_dock
paragraph of its docstring, so that it no longer overwrites these models (re-running the trimmed script changes the
dock's GLBs a little).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes of the
whole and of each piece against enemy_8.png), --preview <prefix> (the whole's and each piece's top and 3/4 views),
--only <model,...>, --whole <file.glb> (the uncut machine as well, for looking at), --stats 1.
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
import polish_deli_boss as db  # noqa: E402  (join, drop_unused)
from polish_arch import plane_box  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_orb_red import band_split  # noqa: E402
from polish_savara_boss import cut  # noqa: E402  (polish_arch.cut keeping the faces' winding)

# The pieces: model, sprite, the box it covers in the whole (x0, x1, y0, y1).
PIECES = [("ixm_dock_tl", 39, (-36.0, -12.0, 0.0, 28.0)), ("ixm_dock_tc", 41, (-12.0, 12.0, 0.0, 28.0)),
          ("ixm_dock_tr", 43, (12.0, 36.0, 0.0, 28.0)), ("ixm_dock_bl", 77, (-36.0, -12.0, -28.0, 0.0)),
          ("ixm_dock_bc", 79, (-12.0, 12.0, -28.0, 0.0)), ("ixm_dock_br", 81, (12.0, 36.0, -28.0, 0.0))]
# The sprites' top left corners in the 72 x 56 picture (for the whole's silhouette).
CELLS = {39: (0, 0), 41: (24, 0), 43: (48, 0), 77: (0, 28), 79: (24, 28), 81: (48, 28)}

BAKE = Vector((0.0, 0.42, 0.91))   # the light the round parts' colours are banded by: from above and up the screen


def X(c):
    return c - 36.0


def Y(r):
    return 28.0 - r


# --- Materials -------------------------------------------------------------------------------------------------------

def materials():
    pal = k.level_palette()

    def mat(name, index, metallic=0.45, roughness=0.38, glow=0.0):
        kw = dict(emission=pal[index], emission_strength=glow) if glow else {}
        return k.material("dock_" + name, palette=index, metallic=metallic, roughness=roughness, **kw)
    return {
        # the engines' steel
        "gap": mat("gap", 0x02, 0.3, 0.6),
        "wall": mat("wall", 0x05, 0.5, 0.4),
        "steel": mat("steel", 0x07, 0.5, 0.36),
        "slat": mat("slat", 0x09, 0.5, 0.32),
        "rim": mat("rim", 0x0a, 0.5, 0.3),
        "edge": mat("edge", 0x0c, 0.5, 0.28),
        # the red: the caps, the ship, the light
        "red_deep": mat("red_deep", 0x42, 0.35, 0.45),
        "red_dark": mat("red_dark", 0x44, 0.4, 0.36),
        "red": mat("red", 0x47, 0.4, 0.32),
        "red_lit": mat("red_lit", 0x49, 0.4, 0.3),
        "red_top": mat("red_top", 0x4b, 0.4, 0.28),
        "red_edge": mat("red_edge", 0x4c, 0.4, 0.26),
        "lamp": mat("lamp", 0x47, 0.0, 0.25, 0.35),
        # the grille's heat
        "well": mat("well", 0x40, 0.2, 0.7),
        "fin": mat("fin", 0x72, 0.2, 0.5, 0.12),
        "tube_low": mat("tube_low", 0x74, 0.0, 0.4, 0.22),
        "tube": mat("tube", 0x77, 0.0, 0.35, 0.32),
        "tube_hot": mat("tube_hot", 0x7a, 0.0, 0.3, 0.45),
        "tube_core": mat("tube_core", 0x7d, 0.0, 0.3, 0.6),
        # the dome and the pods: glossy, near black
        "glass1": mat("glass1", 0x03, 0.55, 0.2, 0.06),
        "glass2": mat("glass2", 0x05, 0.55, 0.18, 0.06),
        "glass3": mat("glass3", 0x07, 0.55, 0.16, 0.07),
        "glass4": mat("glass4", 0x0a, 0.55, 0.14, 0.08),
        "pod1": mat("pod1", 0x04, 0.55, 0.2, 0.06),
        "pod2": mat("pod2", 0x06, 0.55, 0.18, 0.06),
        "pod3": mat("pod3", 0x08, 0.55, 0.16, 0.07),
        "pod4": mat("pod4", 0x0b, 0.55, 0.14, 0.08),
        "cut": mat("cut", 0x03, 0.3, 0.6),
    }


def bake_bands(obj, bands, angle=40.0, light=BAKE):
    """Gives the faces of obj the material of their band of how much they face the light (bands: [(lowest value,
    material)], ascending), the bands' borders smooth contours (band_split)."""
    values = [v.normal.dot(light) for v in obj.data.vertices]
    band_split(obj, values, bands)
    return k.smooth(obj, angle)


def finish(obj, width, segments=2, angle=35.0, flat=False):
    """Merged, bevelled (edges sharper than angle), shaded: smooth across the bevels with the flat faces kept flat
    (weighted normals), or flat (the engines' blocks: their big tops cut into many faces by the pockets would take
    the bevels' normals at their edges, streaking the light across them)."""
    mk.cleanup(obj)
    mk.bevel(obj, width, segments, angle)
    if flat:
        k.smooth(obj, 20.0)       # (a 2-segment bevel's first face turns 22.5 degrees from its face)
    else:
        mk.shade(obj, 35)
    return obj


def rounded_plan(x0, x1, y0, y1, radii, steps=5):
    """A rectangle's outline counter-clockwise seen from above, its corners rounded: radii (x0y0, x1y0, x1y1, x0y1)."""
    corners = [((x0, y0), (1, 1), radii[0], 180.0), ((x1, y0), (-1, 1), radii[1], 270.0),
               ((x1, y1), (-1, -1), radii[2], 0.0), ((x0, y1), (1, -1), radii[3], 90.0)]
    pts = []
    for (cx, cy), (sx, sy), r, a0 in corners:
        if r <= 0.01:
            pts.append((cx, cy))
            continue
        ox, oy = cx + sx * r, cy + sy * r
        for i in range(steps + 1):
            a = math.radians(a0 + 90.0 * i / steps)
            pts.append((ox + r * math.cos(a), oy + r * math.sin(a)))
    return pts


def ccw(points):
    area = sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(points, points[1:] + points[:1]))
    return points if area > 0 else points[::-1]


# --- The engines -----------------------------------------------------------------------------------------------------
# Built in u (the distance out from the picture's middle, x = side * u) and y; the right engine (side 1) is the left
# one (side -1) mirrored, everything from y 0 down DROP lower.
TOP = 11.0                       # the top's height
U_IN, U_OUT = 13.3, 32.7         # the block's inner and outer faces
Y_FRONT, Y_BACK = 13.75, -25.75  # its front and back edges (the left engine's; the right one's back is DROP lower)
DROP = {-1: 0.0, 1: 1.0}
# The section across it (u, z): the inner face, the inner bevel, the top, the broad outer chamfer, the outer face.
SECTION = [(U_IN, 1.4), (U_IN, 9.85), (14.75, TOP), (28.3, TOP), (U_OUT, 7.2), (U_OUT, 2.2), (31.2, 0.5), (14.8, 0.5)]
CHAMFER = ((28.3, TOP), (U_OUT, 7.2))
BACK_R, FRONT_R = 4.6, 0.7       # the plan's rounded corners
FRONT_OUT_R = {-1: 0.7, 1: 3.6}  # the front outer corner (the right engine's is cut off)
# The caps on the front edge: (u from, to), and their y and z extents.
CAPS = [(20.4, 30.6), (14.75, 18.85)]
CAP_OUT = {-1: 30.6, 1: 29.7}    # the wide cap's outer end (the right engine's corner is cut off)
CAP_Y, CAP_Z = (12.6, 16.6), (7.7, 10.75)
# The louvres: the pocket (u from, through the chamfer; y from (+ the drop), to), its depth; the slats' y centres.
LOUVRE_U, LOUVRE_Y, LOUVRE_D = 17.85, (0.0, 10.0), 1.2
SLATS = [8.5, 6.5, 4.5, 2.5, 0.5]
SLAT_W, SLAT_TILT = 0.98, 10.0
# The raised panel (u, y boxes) in its shallow pocket, the red light's slot and its lens (y before the drop).
PANEL_POCKET = (18.0, 26.95, -5.1, -0.05)
PANEL = (18.55, 26.3, -4.65, -0.45)
LIGHT_SLOT = (18.25, 24.9, -6.95, -5.05)
# The seam in front of the housing, the notches across the ledge.
SEAM = (13.9, 30.6, -11.95, -11.05)
NOTCHES = [(23.1, 23.9), (19.1, 19.9)]
NOTCH_Y = (-10.95, -9.3)
# The grille: its well (u, y), floor; the tubes' u, their y extent, radius and axis height; the fins' u.
WELL = (14.25, 29.95, -23.2, -12.2)
WELL_FLOOR = 6.3
TUBES = [27.5, 24.5, 21.5, 18.5, 15.5]
TUBE_Y, TUBE_R, TUBE_Z = (-21.15, -12.65), 1.2, 8.2
FINS = [29.15, 26.0, 23.0, 20.0, 17.0, 14.55]
# The slot freeing the housing's outer bar, the notches in its back rim.
BAR_SLOT = (30.05, 30.95, -21.0, -13.0)
RIM_NOTCHES = [(26.1, 26.85), (21.1, 21.85)]
# The rail along the inner face (u from, to; y from, to before the drop; z from, to).
RAIL = (13.55, -21.2, 6.9, 3.3, 9.3)       # its outer u, y from, to (before the drop), z from, to
RAIL_IN = {-1: (11.4, 12.1), 1: (10.4, 11.2)}   # its inner u along the top and by the housing (y under RAIL_STEP;
RAIL_STEP = -11.2                                # the right engine's rail is a pixel wider)


def engine_xy(side, u, y, drop):
    return (side * u, y - (drop if y < 0.0 else 0.0))


def u_box(name, side, u0, u1, y0, y1, z0, z1, mat, drop=0.0):
    """A box in engine coordinates (y from 0 down moved by the drop)."""
    xa, ya = engine_xy(side, u0, y0, drop)
    xb, yb = engine_xy(side, u1, y1, drop)
    return mk.box(name, min(xa, xb), max(xa, xb), min(ya, yb), max(ya, yb), z0, z1, mat)


def section_prism(name, side, section, y0, y1, mat):
    """A section (u, z) extruded along y from y0 to y1."""
    outline = ccw([(side * u, z) for u, z in section])
    return mk.prism(name, outline, y0, y1, mat, axis="y")


def chamfer_z(u):
    (ua, za), (ub, zb) = CHAMFER
    return za + (zb - za) * (u - ua) / (ub - ua)


def paint_engine(obj, m, side):
    """The engine's faces by their facing: the top (steel), the chamfer (wall), walls, gaps under the top."""
    def pick(c, n):
        out = n.x * side          # how much it faces outwards
        if n.z > 0.95:
            if c.z < TOP - 0.3:
                return m["gap"]   # pocket floors
            return m["steel"]
        if n.z > 0.4:
            if out > 0.4:
                return m["wall"]  # the broad chamfer
            return m["rim"] if n.y > 0.3 or n.x * side < -0.3 else m["wall"]
        if n.z < -0.5:
            return m["gap"]
        return m["wall"]
    mk.paint(obj, pick)


def engine(m, side):
    drop = DROP[side]
    yb = Y_BACK - drop
    # The block: its plan (rounded at the back) intersected with its section.
    if side < 0:
        plan = rounded_plan(-U_OUT, -U_IN, yb, Y_FRONT, (BACK_R, BACK_R, FRONT_R, FRONT_OUT_R[side]))
    else:
        plan = rounded_plan(U_IN, U_OUT, yb, Y_FRONT, (BACK_R, BACK_R, FRONT_OUT_R[side], FRONT_R))
    body = mk.prism(f"engine{side}", plan, 0.0, TOP + 1.0, m["steel"])
    mk.boolean(body, section_prism(f"engine_section{side}", side, SECTION, yb - 2.0, Y_FRONT + 2.0, m["steel"]),
               "INTERSECT")
    mk.cleanup(body)
    # The louvres' pocket, through the top and the chamfer.
    (ua, za), (ub, zb) = CHAMFER
    slope = (zb - za) / (ub - ua)
    floor = TOP - LOUVRE_D
    pocket = [(LOUVRE_U, floor), (ua, floor), (U_OUT + 1.5, floor + slope * (U_OUT + 1.5 - ua)),
              (U_OUT + 2.0, floor + slope * (U_OUT + 1.5 - ua)), (U_OUT + 2.0, TOP + 3.0), (LOUVRE_U, TOP + 3.0)]
    cutters = [section_prism(f"louvre_pocket{side}", side, pocket, LOUVRE_Y[0] - drop, LOUVRE_Y[1], m["gap"])]
    # The raised panel's pocket, the light's slot, the seam, the ledge's notches.
    u0, u1, y0, y1 = PANEL_POCKET
    cutters.append(u_box(f"panel_pocket{side}", side, u0, u1, y0, y1, TOP - 0.45, TOP + 2.0, m["gap"], drop))
    u0, u1, y0, y1 = LIGHT_SLOT
    cutters.append(u_box(f"light_slot{side}", side, u0, u1, y0, y1, TOP - 1.1, TOP + 2.0, m["gap"], drop))
    u0, u1, y0, y1 = SEAM
    cutters.append(u_box(f"seam{side}", side, u0, u1, y0, y1, TOP - 0.8, TOP + 2.0, m["gap"], drop))
    for i, (u0, u1) in enumerate(NOTCHES):
        cutters.append(u_box(f"notch{side}_{i}", side, u0, u1, NOTCH_Y[0], NOTCH_Y[1], TOP - 0.5, TOP + 2.0, m["gap"],
                             drop))
    # The grille's well, the outer bar's slot (right through), the rim's notches.
    u0, u1, y0, y1 = WELL
    cutters.append(u_box(f"well{side}", side, u0, u1, y0, y1, WELL_FLOOR, TOP + 2.0, m["well"], drop))
    u0, u1, y0, y1 = BAR_SLOT
    cutters.append(u_box(f"bar_slot{side}", side, u0, u1, y0, y1, -1.0, TOP + 2.0, m["well"], drop))
    for i, (u0, u1) in enumerate(RIM_NOTCHES):
        cutters.append(u_box(f"rim_notch{side}_{i}", side, u0, u1, Y_BACK - 1.0, WELL[2] - 0.05, TOP - 0.45,
                             TOP + 2.0, m["gap"], drop))
    mk.boolean(body, cutters, "DIFFERENCE")
    finish(body, 0.26, 2, 50.0, flat=True)
    paint_engine(body, m, side)
    # The well's walls and floor dark red, its slot's walls too.
    for poly in body.data.polygons:
        c, n = poly.center, poly.normal
        u, y = c.x * side, c.y + (drop if c.y < -11.0 else 0.0)
        if (WELL[0] - 0.1 < u < WELL[1] + 0.1 and WELL[2] - 0.1 < y < WELL[3] + 0.1 and
                WELL_FLOOR - 0.3 < c.z < TOP - 0.2):
            poly.material_index = mk.slot_of(body, m["well"])
        elif (BAR_SLOT[0] - 0.1 < u < BAR_SLOT[1] + 0.1 and BAR_SLOT[2] - 0.1 < y < BAR_SLOT[3] + 0.1 and
              abs(n.z) < 0.5):
            poly.material_index = mk.slot_of(body, m["well"])
    parts = [body]

    # The caps on the front edge: rounded red bars.
    for i, (u0, u1) in enumerate(CAPS):
        u1 = CAP_OUT[side] if i == 0 else u1
        cap = u_box(f"cap{side}_{i}", side, u0, u1, CAP_Y[0], CAP_Y[1], CAP_Z[0], CAP_Z[1], m["red"])
        mk.bevel(cap, 1.05, 4, 30.0)
        mk.shade(cap, 50, weighted=False)
        bake_bands(cap, [(-9.0, m["red_deep"]), (0.2, m["red_dark"]), (0.55, m["red"]), (0.85, m["red_lit"]),
                         (0.97, m["red_edge"])], 50.0)
        parts.append(cap)

    # The slats: bars following the top and the chamfer, each tilted a little (its back edge up).
    for i, yc in enumerate(SLATS):
        y0, y1 = yc - SLAT_W / 2, yc + SLAT_W / 2
        if i == len(SLATS) - 1:
            y0 -= drop
        top = TOP - 0.12
        edge = chamfer_z(U_OUT)
        prof = [(LOUVRE_U + 0.05, floor + 0.1), (LOUVRE_U + 0.05, top), (ua, top), (U_OUT - 0.05, edge - 0.12),
                (U_OUT - 0.05, edge - 1.1), (ua + 0.4, floor + 0.1)]
        slat = section_prism(f"slat{side}_{i}", side, prof, y0, y1, m["slat"])
        pivot = Vector((0.0, (y0 + y1) / 2, top))
        slat.data.transform(Matrix.Translation(pivot) @ Matrix.Rotation(-math.radians(SLAT_TILT), 4, "X") @
                            Matrix.Translation(-pivot))
        finish(slat, 0.16, 2, 30.0)
        mk.paint(slat, lambda c, n: m["slat"] if n.z > 0.75 and n.x * side < 0.4 else
                 m["steel"] if n.z > 0.4 and n.x * side >= 0.4 else m["rim"] if n.z > 0.3 and n.y < -0.3 else m["gap"])
        parts.append(slat)

    # The raised panel and the red light's lens.
    u0, u1, y0, y1 = PANEL
    panel = u_box(f"panel{side}", side, u0, u1, y0, y1, TOP - 0.9, TOP + 0.38, m["steel"], drop)
    finish(panel, 0.32, 2, 30.0)
    mk.paint(panel, lambda c, n: None if n.z > 0.95 else m["edge"] if (n.x < -0.3 or n.y > 0.3) and n.z > 0.2 else
             m["wall"])
    parts.append(panel)
    u0, u1, y0, y1 = LIGHT_SLOT
    lens = u_box(f"lens{side}", side, u0 + 0.3, u1 - 0.3, y0 + 0.25, y1 - 0.25, TOP - 1.6, TOP - 0.28, m["lamp"], drop)
    mk.bevel(lens, 0.55, 3, 30.0)
    mk.shade(lens, 50, weighted=False)
    parts.append(lens)

    # The grille: glowing tubes along the screen between dim fins.
    ya, yb2 = TUBE_Y[0] - drop, TUBE_Y[1] - drop
    ends = [math.radians(a) for a in (0, 20, 40, 60, 75, 90)]
    prof = ([(ya + TUBE_R * (1 - math.sin(a)), TUBE_R * math.cos(a)) for a in reversed(ends)] +
            [(yb2 - TUBE_R * (1 - math.sin(a)), TUBE_R * math.cos(a)) for a in ends])
    prof = [(ya, 0.0)] + sorted(prof) + [(yb2, 0.0)]
    for i, u in enumerate(TUBES):
        tube = k.lathe(f"tube{side}_{i}", prof, m["tube"], segments=16, axis_x=side * u, axis_z=TUBE_Z)
        values = [v.normal.z for v in tube.data.vertices]
        band_split(tube, values, [(-9.0, m["tube_low"]), (0.4, m["tube"]), (0.8, m["tube_hot"]),
                                  (0.955, m["tube_core"])])
        k.smooth(tube, 60.0)
        parts.append(tube)
    for i, u in enumerate(FINS):
        fin = u_box(f"fin{side}_{i}", side, u - 0.22, u + 0.22, WELL[2] + 0.35, WELL[3] - 0.15, WELL_FLOOR - 0.2,
                    TUBE_Z + 1.55, m["fin"], drop)
        finish(fin, 0.1, 1, 30.0)
        parts.append(fin)

    # The rail along the inner face.
    u1, y0, y1, z0, z1 = RAIL
    upper, lower = RAIL_IN[side]
    rail = u_box(f"rail{side}", side, upper, u1, RAIL_STEP - drop, y1, z0, z1, m["rim"])
    mk.boolean(rail, u_box(f"rail_low{side}", side, lower, u1, y0 - drop, RAIL_STEP - drop + 0.5, z0, z1, m["rim"]),
               "UNION")
    finish(rail, 0.45, 2, 30.0)
    mk.paint(rail, lambda c, n: m["rim"] if n.z > 0.3 or n.x * side < -0.3 else m["wall"])
    parts.append(rail)
    return parts


# --- The ship --------------------------------------------------------------------------------------------------------
AX = -0.5                    # its axis (the middle of column 35)
# The keel's ridge: (y, half-width, top, bottom) from inside the head back to the spike's tip.
KEEL = [(10.4, 1.6, 12.45, 9.8), (8.0, 1.8, 12.5, 9.6), (5.0, 2.1, 12.35, 9.4), (1.0, 2.45, 11.95, 9.1),
        (-3.0, 2.5, 11.6, 8.9), (-7.0, 2.6, 11.15, 8.6), (-11.0, 2.4, 10.4, 8.2), (-14.5, 2.0, 9.75, 7.8),
        (-17.5, 1.7, 9.2, 7.5), (-19.4, 1.3, 8.8, 7.4), (-23.0, 1.0, 8.4, 7.3), (-27.75, 0.55, 7.9, 7.45)]
# The head block (x half-width, y from, to, z from, to), its lip at the front, its grooves either side of the ridge.
HEAD = (3.45, 5.05, 10.9, 8.4, 11.75)
LIP = (4.4, 9.95, 11.45, 8.9, 11.45)
HEAD_GROOVES = (2.0, 0.28, 0.26)          # their distance from the axis, half-width, depth
# The cross bars' plans (x from the axis, y), their tops at their front and back (z), their thickness.
BAR1 = [(-7.2, 0.1), (-5.1, 0.1), (-5.1, 2.0), (5.1, 2.0), (5.1, 0.1), (7.2, 0.1), (7.2, 5.7), (-7.2, 5.7)]
BAR1_Z = (11.55, 10.0, 1.55)
BAR2 = [(-8.3, -2.2), (8.3, -2.2), (7.3, -6.95), (-7.3, -6.95)]
BAR2_Z = (11.15, 9.75, 1.6)
# The arrowhead of the wings and the tail (x from the axis, y), the right half (the left mirrored).
ARROW = [(0.0, -6.1), (7.0, -6.1), (9.3, -6.35), (11.3, -6.7), (11.3, -10.75), (9.9, -11.3), (8.4, -11.85),
         (6.4, -12.55), (5.4, -13.5), (4.4, -14.5), (3.0, -15.4), (2.2, -16.3), (2.0, -18.9), (1.3, -19.6),
         (0.0, -19.6)]
ARROW_Z = (10.35, 0.085, 0.13, 1.45)      # its top at the front middle, the fall per pixel out and back, thickness
WING_DROOP = (6.5, 0.32)                  # past this distance from the axis the tips fall this much per pixel
# The dome: centre (x, y), radii, its groove's half-width and depth.
DOME = ((AX, 14.0), (10.35, 8.0, 9.6))
DOME_POWER = 2.2                          # its plan a superellipse (fuller than an ellipse)
DOME_LOBES = 0.09                         # its halves bulge (a valley down the middle, two highlights)
DOME_GROOVE = (0.45, 0.55)
# The pods: centre, radii (across, along, height), lean (degrees, the lower end in towards the axis).
POD = ((-5.5, -18.7, 3.8), (3.6, 6.9, 3.5), 24.0)
# The clamps holding the wings' tips to the rails (x from, to for the left one; y; z).
CLAMPS = [(-13.3, -9.6), (8.7, 13.3)]     # x from, to (the left one, the right one)
CLAMP_YZ = (-14.9, -10.6, 4.8, 7.6)


def keel(m):
    """The ridge down the middle: lofted rounded diamonds from the head to the spike's tip."""
    rings = []
    for y, w, top, bottom in k.profile(list(reversed(KEEL)), 0.5):
        mid = bottom + (top - bottom) * 0.42
        ring = []
        for j in range(20):
            a = 2 * math.pi * j / 20
            s = math.sin(a)
            px, pz = mk.superellipse_point(a, 1.55 if s > 0 else 2.0)
            ring.append(Vector((AX + w * px, y, mid + (top - mid if s > 0 else mid - bottom) * pz)))
        rings.append(ring)
    first, last = KEEL[-1], KEEL[0]
    body = k.loft("keel", rings, m["red"], start_point=(AX, first[0] - 0.05, first[3] + 0.3 * (first[2] - first[3])),
                  end_point=(AX, last[0] + 0.05, last[3] + 0.5 * (last[2] - last[3])))
    bake_bands(body, [(-9.0, m["red_deep"]), (0.25, m["red_dark"]), (0.55, m["red"]), (0.8, m["red_lit"]),
                      (0.92, m["red_top"])], 45.0)
    return body


def paint_red(obj, m):
    """The ship's plates by their facing: tops lit, fronts and left bevels lighter, backs and sides dark."""
    def pick(c, n):
        if n.z > 0.9:
            return m["red_lit"] if n.y > -0.05 else m["red"]
        if n.z > 0.3:
            if n.y > 0.35 or n.x < -0.35:
                return m["red_top"]
            return m["red_dark"]
        if n.z < -0.3:
            return m["red_deep"]
        return m["red_dark"] if n.y < 0.3 else m["red"]
    mk.paint(obj, pick)


def head(m):
    hw, y0, y1, z0, z1 = HEAD
    block = mk.box("head", AX - hw, AX + hw, y0, y1, z0, z1, m["red"])
    lw, ly0, ly1, lz0, lz1 = LIP
    lip = mk.box("head_lip", AX - lw, AX + lw, ly0, ly1, lz0, lz1, m["red"])
    mk.boolean(block, lip, "UNION")
    d, hw_g, depth = HEAD_GROOVES
    grooves = [mk.box(f"head_groove{i}", AX + s * d - hw_g, AX + s * d + hw_g, y0 - 1.0, y1 - 0.9, z1 - depth, z1 + 2.0,
                      m["red_deep"]) for i, s in enumerate((-1, 1))]
    mk.boolean(block, grooves, "DIFFERENCE")
    finish(block, 0.3, 2, 30.0)
    paint_red(block, m)
    return block


def bar_plate(name, outline, front_y, z_front, fall_y, thick, mat):
    """A cross bar: its plan (x from the axis, y) under a flat top falling away down the screen (fall_y per pixel from
    front_y), thick under it."""
    top = lambda x, y: z_front - fall_y * (front_y - y)  # noqa: E731
    return mk.wedge(name, ccw([(AX + x, y) for x, y in outline]), 0.0, top, mat, bottom=lambda x, y: top(x, y) - thick)


def arrow_plate(name, outline, front_y, z_front, fall_y, fall_x, thick, droop, mat):
    """The arrowhead: its plan (x from the axis, y) under two flat tops falling away from the ridge (fall_x per pixel)
    and down the screen (fall_y per pixel from front_y), thick under them; past droop[0] from the axis the tips fall
    droop[1] more per pixel (the top only: they thin out). Exact booleans with planes, so every face stays flat."""
    def half(s, extra=0.0, d0=0.0, d1=0.0):
        return lambda x, y: (z_front - fall_y * (front_y - y) - fall_x * s * (x - AX) - d1 * (s * (x - AX) - d0)
                             - extra)
    body = mk.prism(name, ccw([(AX + x, y) for x, y in outline]), z_front - 30.0, z_front + 5.0, mat)
    tops = [plane_box(f"{name}_top{i}", f) for i, f in enumerate(
        (half(-1), half(1), half(-1, 0.0, droop[0], droop[1]), half(1, 0.0, droop[0], droop[1])))]
    for cutter in tops:
        mk.boolean(body, cutter, "INTERSECT")
    under = plane_box(f"{name}_under0", half(-1, thick))
    mk.boolean(under, plane_box(f"{name}_under1", half(1, thick)), "INTERSECT")
    mk.boolean(body, under, "DIFFERENCE")
    return body


def plates(m):
    out = []
    z_front, z_back, thick = BAR1_Z
    bar1 = bar_plate("bar1", BAR1, 4.95, z_front, (z_front - z_back) / 3.9, thick, m["red"])
    z_front, z_back, thick = BAR2_Z
    bar2 = bar_plate("bar2", BAR2, -3.05, z_front, (z_front - z_back) / 3.95, thick, m["red"])
    z_front, fall_x, fall_y, thick = ARROW_Z
    outline = [(-x, y) for x, y in reversed(ARROW[1:-1])] + ARROW
    outline = [p for i, p in enumerate(outline) if i == 0 or p != outline[i - 1]]
    arrow = arrow_plate("arrow", outline, -6.0, z_front, fall_y, fall_x, thick, WING_DROOP, m["red"])
    for obj in (bar1, bar2, arrow):
        finish(obj, 0.3, 2, 30.0)
        paint_red(obj, m)
        out.append(obj)
    return out


def dome(m):
    (cx, cy), (rx, ry, rz) = DOME

    def half_ellipsoid(name, a, c, z0):
        prof = []
        for i in range(15):
            t = (math.pi / 2) * i / 14
            prof.append((max(1e-3, a * math.cos(t)), z0 + c * math.sin(t)))
        return k.smooth(mk.lathe(name, prof, (cx, cy), m["glass2"], segments=56, squash=(1.0, ry / rx),
                                 power=DOME_POWER), 70.0)
    body = half_ellipsoid("dome", rx, rz, 0.0)
    for v in body.data.vertices:          # the two lobes
        d = min(1.0, abs(v.co.x - cx) / rx)
        v.co.z *= 1.0 + DOME_LOBES * math.sin(math.pi * d) - DOME_LOBES * 0.35
    body.data.update()
    hw, depth = DOME_GROOVE
    groove = mk.box("dome_groove", cx - hw, cx + hw, cy - ry - 1.0, cy + ry + 1.0, 0.0, 30.0, m["glass1"])
    # The groove follows the dome's top: cut with a shell just inside it.
    inner = half_ellipsoid("dome_inner", rx - depth, rz - depth, -0.01)
    for v in inner.data.vertices:
        d = min(1.0, abs(v.co.x - cx) / (rx - depth))
        v.co.z = (v.co.z + 0.01) * (1.0 + DOME_LOBES * math.sin(math.pi * d) - DOME_LOBES * 0.35) - 0.01
    inner.data.update()
    mk.boolean(groove, inner, "DIFFERENCE")
    mk.boolean(body, groove, "DIFFERENCE")
    mk.cleanup(body, dissolve=0.0)
    bake_bands(body, [(-9.0, m["glass1"]), (0.45, m["glass2"]), (0.75, m["glass3"]), (0.93, m["glass4"])], 50.0,
               Vector((-0.42, 0.45, 0.79)))
    for poly in body.data.polygons:      # the groove's floor and left wall dark, its right wall lit
        c, n = poly.center, poly.normal
        if abs(c.x - cx) < hw + 0.05:
            lit = c.x > cx and n.x < -0.5
            poly.material_index = mk.slot_of(body, m["glass4"] if lit else m["glass1"])
    return body


def pods(m):
    out = []
    (px, py, pz), (rx, ry, rz), lean = POD
    for side in (-1, 1):
        pod = k.ellipsoid(f"pod{side}", (0.0, 0.0, 0.0), (rx, ry, rz), m["pod2"], 28, 16)
        angle = math.radians(lean) * (-side)
        x = px if side < 0 else 2 * AX - px
        pod.data.transform(Matrix.Translation((x, py, pz)) @ Matrix.Rotation(angle, 4, "Z"))
        k.recalc_normals(pod)
        bake_bands(pod, [(-9.0, m["pod1"]), (0.45, m["pod2"]), (0.75, m["pod3"]), (0.92, m["pod4"])], 60.0,
                   Vector((-0.42, 0.45, 0.79)))
        out.append(pod)
    return out


def clamps(m):
    out = []
    y0, y1, z0, z1 = CLAMP_YZ
    for i, (a, b) in enumerate(CLAMPS):
        clamp = mk.box(f"clamp{i}", a, b, y0, y1, z0, z1, m["steel"])
        finish(clamp, 0.35, 2, 30.0)
        mk.paint(clamp, lambda c, n: m["rim"] if n.z > 0.9 else m["edge"] if n.z > 0.2 and n.x < -0.3 else m["wall"])
        out.append(clamp)
    return out


# --- Build -----------------------------------------------------------------------------------------------------------

def build_whole():
    m = materials()
    for side in (-1, 1):
        engine(m, side)
    keel(m)
    head(m)
    plates(m)
    dome(m)
    pods(m)
    clamps(m)
    whole = [o for o in mk.meshes() if len(o.data.polygons) > 0]
    for obj in whole:
        mk.apply(obj)
    bpy.context.view_layer.update()
    return whole, m


def whole_mask(sheet):
    """The six sprites' silhouettes placed as the levels place them: 72 x 56."""
    mask = [[False] * 72 for _ in range(56)]
    for sprite, (col, row) in CELLS.items():
        part = k.sprite_mask(sheet, sprite)
        for y in range(28):
            for x in range(24):
                if part[y][x]:
                    mask[row + y][col + x] = True
    return mask


class Shading:
    """An uncut object's corner normals, looked up on the source triangle that holds a point and lies in the plane of
    the face asking (polish_machine_kit.NormalSource takes the nearest triangle, which at a crease between flat faces
    can be the neighbour's: its normal then streaks across the face)."""

    def __init__(self, obj):
        mesh = obj.data
        mesh.calc_loop_triangles()
        self.verts = [v.co.copy() for v in mesh.vertices]
        self.tris = [(tuple(tr.vertices), tuple(tr.loops)) for tr in mesh.loop_triangles]
        self.normals = [n.vector.copy() for n in mesh.corner_normals]
        self.face_n = [tr.normal.copy() for tr in mesh.loop_triangles]
        self.bvh = BVHTree.FromPolygons(self.verts, [tr[0] for tr in self.tris])

    def normal(self, co, face_normal):
        best, best_dot = None, -2.0
        for _, _, index, _ in self.bvh.find_nearest_range(co, 0.02):
            d = self.face_n[index].dot(face_normal)
            if d > best_dot:
                best, best_dot = index, d
        if best is None or best_dot < 0.95:
            return None
        (ia, ib, ic), (la, lb, lc) = self.tris[best]
        w = mk.barycentric(co, self.verts[ia], self.verts[ib], self.verts[ic])
        n = self.normals[la] * w[0] + self.normals[lb] * w[1] + self.normals[lc] * w[2]
        return n.normalized() if n.length > 1e-8 else None


def reshade(piece, shading, cap_mat):
    """Sets a cut piece's corner normals from its source's (Shading), the caps flat."""
    mesh = piece.data
    cap = mk.slot_of(piece, cap_mat)
    normals = []
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            n = None
            if poly.material_index != cap:
                n = shading.normal(mesh.vertices[mesh.loops[li].vertex_index].co, poly.normal)
            normals.append(tuple(n if n is not None else poly.normal))
    mesh.normals_split_custom_set(normals)


def export_pieces(whole, m, options, sheet=None):
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    shadings = {src.name: Shading(src) for src in whole}
    for name, sprite, box in PIECES:
        if only and name not in only:
            continue
        parts = []
        for src in whole:
            part = cut(src, box, m["cut"])
            if part is not None:
                reshade(part, shadings[src.name], m["cut"])
                parts.append(part)
        db.drop_unused(parts)
        mk.transform(parts, Matrix.Translation((-(box[0] + box[1]) / 2, -(box[2] + box[3]) / 2, 0.0)))
        bpy.context.view_layer.update()
        triangulate(parts)
        if "stats" in options:
            for obj in sorted(parts, key=lambda o: -mk.triangles([o]))[:12]:
                print("    %-22s %6d" % (obj.name, mk.triangles([obj])))
        piece = db.join(parts, name)
        piece.data.name = name
        for src in whole:
            src.hide_render = True
        if sheet:
            mk.compare("%s (8 %d)" % (name, sprite), mk.coverage([piece], 24, 28), k.sprite_mask(sheet, sprite))
        mk.report(name, [piece], os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, [piece])
        bpy.data.objects.remove(piece)
        for src in whole:
            src.hide_render = False


def build():
    k.reset()
    options = k.args()
    whole, m = build_whole()
    print("whole dock: %d triangles, %d objects" % (mk.triangles(whole), len(whole)))
    for obj in sorted(whole, key=lambda o: -mk.triangles([o]))[:16]:
        print("   %-22s %6d" % (obj.name, mk.triangles([obj])))
    sheet = os.path.join(options["check"], "enemy_8.png") if "check" in options else None
    if sheet:
        mk.compare("whole (8 39 41 43 / 77 79 81)", mk.coverage(whole, 72, 56), whole_mask(sheet))
    bpy.context.scene.view_settings.view_transform = "Standard"
    if "preview" in options:
        mk.preview(options["preview"] + "ixm_dock_whole", whole, size=(72, 56), scale=8, distance=2.0)
    if "whole" in options:
        triangulate(whole)
        mk.export(whole, options["whole"])
    if options.get("only") != "none":
        export_pieces(whole, m, options, sheet)


if __name__ == "__main__":
    build()
