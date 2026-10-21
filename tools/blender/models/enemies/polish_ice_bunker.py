"""The grey and blue bunker of CAMANIS and ICESECRET (sheet 7: sprites 1, 3 above 39, 41, 2x2 each: one 48 x 56
picture, the bunker 44 x 52 of it; enemies 82, 83 above 80, 81 of episodes 3 and 4, on the ground: 2 in CAMANIS, 16
in ICESECRET), polished (2026-10-21; it replaces wave3_ac_ice.py's bunker, slabs and a lofted barrel of a body with
balls for the lamps and the lens, glowing up to 2.8). models.cfg: model ice_bunker_tl / _tr / _bl / _br
enemies/ice_bunker_*.glb origin (unchanged); sprite 7 1 ice_bunker_tl yaw=0 height=-4 and the same for 3, 39, 41
(height=-4 is new, see below). No other enemy (launched ones included) shows these sprites or their frames; none of
them is another sprite's pixels mirrored, turned or in other ramps, and the right half is not the left one mirrored
(the sprite lights it from the upper left and draws its shadow to the right), though the bunker is symmetric about
the pixel edge 22 (x = -2), its skylight, lamps and lens about x = -1.5.

Its frames: each piece's animation (17 frames: 1 5 9 153 77 81 85 229 233 and back, the same for 3, 39, 41) raises a
grey gun with a red eye out of the hatch and brightens the lens. The enemies have animate 2 (the frames play only when
they fire or launch) but no gun and no launch (tur, freq and elaunchfreq all 0), and no level event starts their
animation (no event 19 / 20 / 24 of CAMANIS or ICESECRET reaches their links; episode 6 does not use them): the game
only ever shows the first frame, the hatch shut, so there are no frame models.

The levels lay the four as a square (event 12: the enemy, the next one 24 pixels to its right and the two after them
28 pixels above): 82 (1) above 80 (39), 83 (3) above 81 (41), as the sheet arranges them, all on the ground layer,
moving with the map (CAMANIS t 3520 and 4192; ICESECRET 16 times, t 244-2540).

As the sprites and their 4x upscales draw it (columns and rows of the 48 x 56 picture): a flat grey deck (columns 0-43
of rows 0-37) with a lit rim (row 1, column 1) and a beam across its back (rows 3-5); blue-grey panels in its back
corners (columns 3-7 and 36-40 of rows 3-7); down each side a column of grey panels (rows 9-12 and 15-18 with a small
blue stud on their inner side, rows 21-25 and 27-34); two rails (columns 9-13 and 30-34 of rows 6-18) either side of a
sunken hatch (columns 14-29 of rows 6-18, its back and left walls in shadow) in which the gun's blue housing lies
(columns 19-26: a narrow block, rows 7-11, a wide one, rows 12-16, a small one in front, rows 17-18, lit on their left
and back edges). On the deck's front half the bunker's head (columns 4-39 of rows 19-51): its back corners cut off
(rows 19-24), its sides sloping (lit on the left, columns 5-10, in shadow on the right, 33-38), its flat top (columns
11-32 of rows 20-33) holding a glass skylight (columns 17-28 of rows 19-30: four panes between three dark ribs, light
blue at the back, teal at the front) between two plates with seams across (rows 26 and 30), a blue lamp on each
(columns 14-15 and 29-30 of rows 24-25), a bright rail along each plate's outer edge (columns 11 and 32) running on
down the front (to row 40); the front sloping down to the ice (rows 34-50), a dark recess in it (columns 14-29)
holding two blue windows (columns 15-19 and 24-28 of rows 38-41) with light sills (rows 36-37) either side of a grey
divider, and under them a big glowing blue lens (columns 17-28 of rows 42-48, its glint at its upper left) in a black
socket; dim blue-grey slots down the side slopes near the front (columns 5-6 and 37-38 of rows 40-48), two small vents
at the front's foot (columns 12-13 and 30-31 of rows 47-49), the sides reaching a pixel further down the screen than
the middle (rows 51 and 50). Round it CAMANIS' ice (ramp 3: columns 0-3 and 40-47 beside the head, 44-47 beside the
deck, rows 51-55) and the bunker's shadow on it and on the deck (the black right of the head, columns 38-42 of rows
26-37): the map's ground and the game's own shadow, left out (the silhouette is checked against the bunker's own
pixels: the deck and the head with what lies in them, the lens' transparent pixels included).

Built as a CAD modeller would (polish_machine_kit): the deck a bevelled slab with the hatch sunk into it by an exact
boolean, the beam, panels, studs and rails bevelled boxes (the rails' grooves cut across them), the gun's housing
three bevelled blocks on the hatch's floor; the head a prism of its plan cut by the planes of its sloping sides, its
front and its top (exact booleans), its edges rounded (a bevel of 1.25), then the recess, the windows, the seams, the
slots and the vents cut into it; the rails bars laid along its surface; the skylight four rounded glass panes lofted
along the screen in a frame whose dark floor shows between them (the sprite's ribs), each pane light at its back and
front and teal between (polish_orb_red.band_split along the rows); the lamps domes on dark rings; the lens a glossy
ellipsoid set into the front's slope, lighter towards its upper left with its glint there (band_split along smooth
borders), on a black socket. Faces are painted by how they face, as the sprite paints them: tops and the faces turned
to the sun light grey (0x0a), the rounded edges facing it most brighter (0x0c), the faces turned away a shade darker
(0x08), undersides dark (0x02); the deck 0x06 with its rim lit (0x08); the left half's parts are built and mirrored
about x = -2, the skylight, the lamps, the lens and the housing built where the sprite draws them. The glows are well
under 1: the skylight's light panes 0.3 (0x9e), its teal panes 0.12 (0x83, also the sills and the side slots), the
lamps and windows 0.4 (0x9a), the lens 0.35 (0x99), its light middle 0.4 and 0.3 (0x9a, 0x9e) and its glint 0.55
(0x8e). The whole is cut along the sprites' edges (x = 0, y = 0; polish_savara_boss.cut, which keeps each face's
winding: the pieces keep the whole's shading across the cuts, their cuts capped dark), each piece moved so that its
sprite's centre is its origin, its parts joined into one mesh and triangulated (the same output with and without
--check).

Where it stands: models drawn at their origin stand at the ground enemies' layer, 4 pixels above the terrain;
height=-4 on the four sprite lines sets the deck on the ice (its skirt reaches 1 pixel below z = 0), as the globe on
its legs stands (polish_ice_globe.py): the game lifts the four pieces onto the terrain at one height, the terrain's
under their middle.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the ice (z = 0); the whole's
origin is the middle of the picture (the corner where the four sprites meet): column c's left edge is x = c - 24, row
r's top edge y = 28 - r. The pieces' centres: 1 (-12, 14), 3 (12, 14), 39 (-12, -14), 41 (12, -14).

Replaces wave3_ac_ice.py's bunker: remove its section ("# --- 7 1 3 / 39 41: the bunker": BUNKER, bunker_keep(),
build_bunker() and the a.pieced("ice_bunker", ...) registration), quarters() (only the bunker uses it now) and the
ice_bunker paragraph of its docstring; and wave3_ac_art.py's BUNKER and BUNKER_OPEN (only that section reads them).
build_drill() stays (wave3_at_misc.py quiet_imports wave3_ac_ice and calls it), and so do wave3_ac_kit.py and
wave3_ac_art.py's DRILL / DRILL_B.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes of the whole
and of each piece against the bunker's own pixels of enemy_7.png), --preview <prefix> (the whole's top and 3/4 views;
--pieces 1 also each piece's), --only <name,...> (pieces to export; "none": none), --whole <file.glb> (the uncut
bunker as well, for looking at), --stats 1 (the whole's parts' triangles).
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
import polish_deli_boss as db  # noqa: E402  (join, drop_unused)
from polish_savara_boss import cut  # noqa: E402  (polish_arch.cut keeping each face's winding)
from polish_k_pod import triangulate  # noqa: E402
from polish_orb_red import band_split  # noqa: E402

PIECES = [("ice_bunker_tl", 1, (-24.0, 0.0, 0.0, 28.0)), ("ice_bunker_tr", 3, (0.0, 24.0, 0.0, 28.0)),
          ("ice_bunker_bl", 39, (-24.0, 0.0, -28.0, 0.0)), ("ice_bunker_br", 41, (0.0, 24.0, -28.0, 0.0))]
SPRITE_CELLS = {1: (0, 0), 3: (24, 0), 39: (0, 28), 41: (24, 28)}

AX = -2.0                       # the bunker's axis (the pixel edge 22)
LIGHT = Vector((-0.6, 0.6, 1.0)).normalized()   # towards the sun (from the upper left and above)


def XE(c):
    """The left edge of the picture's column c (fractions allowed)."""
    return c - 24.0


def YE(r):
    """The top edge of the picture's row r."""
    return 28.0 - r


def MX(x):
    """The mirror image of x about the axis."""
    return 2 * AX - x


# --- The measures ----------------------------------------------------------------------------------------------------
DECK_Z, SKIRT = 2.4, -1.0       # the deck's top; how far everything reaches below the ice
DECK_BEVEL = 0.6
HATCH = (14, 30, 6, 19)         # the hatch's columns and rows (edges)
HATCH_FLOOR = DECK_Z - 1.4
BEAM = (9, 35, 3, 6, 0.55)      # the beam across the deck's back: columns, rows (edges), how far it stands up
CORNER_PANELS = [(3, 8, 3, 8)]  # the blue-grey panels (left; mirrored)
SIDE_PANELS = [(3, 8, 9, 13), (3, 8, 15, 19), (1.4, 5.2, 21, 26), (1.4, 5.2, 27, 35)]   # grey panels down the sides
STUDS = [(6, 8, 9, 11), (6, 8, 15, 17)]   # the blue studs on the first two
RAIL = (9.6, 13.8, 6.6, 19.0)   # the rails beside the hatch (columns, rows)
RAIL_GROOVES = (12.6, 17.0)     # rows of the grooves across the rails
# The gun's housing in the hatch: columns, rows (edges) and height over the hatch's floor of its three blocks.
HOUSING = [(20, 26, 7, 12, 1.8), (19, 27, 12, 17, 2.3), (20, 25, 17, 19, 1.5)]

# The head: its plan (the left half, from the back's middle to the front's middle; pixel edges), its flat top, the
# planes of its sloping sides (from the top's edge at column 11 down to the ice at column 4) and of its front (from
# the top's front edge, row 33.5, down to the foot, row 50.6).
HEAD_PLAN = [(22.0, 19.0), (10.0, 19.0), (4.6, 24.4), (3.3, 34.0), (3.0, 50.4), (3.6, 51.9), (8.6, 51.9),
             (9.4, 51.0), (22.0, 51.0)]
TOP_Z = 10.5
SIDE = (11.0, TOP_Z, 4.0, 0.0)  # column, height; column, height (the left side's plane)
FRONT = (33.5, TOP_Z, 50.6, 1.5)
HEAD_BEVEL = 1.25               # the head's edges rounded (its top's edges catch the light in a soft band)
# On the front: the recess (columns, rows, depth), the window band in it (rows: the sills, the panes), the divider,
# the windows (columns), the lens (middle, half-axes, how far it stands out of the recess' floor).
RECESS = (14.0, 30.0, 34.0, 49.6, 1.0)
WINDOW_ROWS = (36.0, 37.8, 38.2, 42.0)          # sill top, sill bottom, pane top, pane bottom
WINDOWS = [(15.0, 20.0)]                      # (left; mirrored)
DIVIDER = (20.0, 24.0)
LENS = (22.5, 45.4, 6.1, 3.55, 1.25)          # column, row of its middle; half-axes; height
LENS_GLINT = (20.0, 44.8, 1.6, 1.0)           # the glint's middle and half-axes
SIDE_SLOT = (5.0, 7.0, 40.0, 49.0, 0.5)       # the slot down the side's slope (left; mirrored)
VENT = (12.0, 14.0, 47.0, 50.0, 0.6)          # the vent at the foot (left; mirrored)
# On the top: the rail along each plate's edge (columns, from row to row), the seams across the plates (rows,
# columns), the lamps (column, row of the middle, radius), the skylight (columns, rows, height, frame width).
HEAD_RAIL = (11.0, 13.4, 19.4, 40.6, 0.5)
SEAMS = [26.5, 30.5]
SEAM_COLS = (12.0, 17.0)
LAMPS = [(15.0, 25.0), (30.0, 25.0)]
LAMP_R = 1.15
SKY = (17.0, 29.0, 19.0, 31.0, 1.5)
SKY_PANES = [XE(19.0), XE(22.0), XE(25.0), XE(28.0)]   # the panes' middles (columns 18-19, 21-22, 24-25, 27-28)
PANE_W = 1.12                   # their half-width (the ribs between them about 0.8 wide)
SKY_BANDS = (24.0, 29.0)        # rows where the light panes turn teal, and teal turns light again


def materials():
    pal = k.level_palette()

    def mat(name, index, metallic, roughness, glow=None):
        if glow:
            return k.material(name, palette=index, metallic=metallic, roughness=roughness, emission=pal[index],
                              emission_strength=glow)
        return k.material(name, palette=index, metallic=metallic, roughness=roughness)
    return {
        "deck": mat("ibunker_deck", 0x06, 0.25, 0.55),
        "steel": mat("ibunker_steel", 0x08, 0.2, 0.45),
        "lit": mat("ibunker_lit", 0x0a, 0.2, 0.4),
        "hi": mat("ibunker_hi", 0x0c, 0.25, 0.36),
        "dark": mat("ibunker_dark", 0x02, 0.25, 0.6),
        "black": mat("ibunker_black", 0x01, 0.2, 0.45),
        "panel": mat("ibunker_panel", 0x82, 0.3, 0.32),
        "panel_dark": mat("ibunker_panel_dark", 0x81, 0.3, 0.36),
        "housing": mat("ibunker_housing", 0x38, 0.3, 0.36),
        "housing_dark": mat("ibunker_housing_dark", 0x35, 0.25, 0.45),
        "glass": mat("ibunker_glass", 0x9e, 0.1, 0.08, 0.3),
        "glass_teal": mat("ibunker_glass_teal", 0x83, 0.15, 0.12, 0.12),
        "light": mat("ibunker_light", 0x9a, 0.0, 0.15, 0.4),
        "lens": mat("ibunker_lens", 0x99, 0.0, 0.1, 0.35),
        "lens_hot": mat("ibunker_lens_hot", 0x8e, 0.0, 0.08, 0.55),
    }


def paint(obj, m, top, side, lit=None, under="dark", top_min=0.9, lit_min=0.5, keep=()):
    """Faces by how they face: up (n.z > top_min) top, down under, turned to the sun's side (n . LIGHT > lit_min) lit,
    the others side; faces of the materials named in keep are kept."""
    names = {m[n].name for n in keep}
    mats = obj.data.materials

    def pick(c, n):
        if n.z > top_min:
            return m[top]
        if n.z < -0.3:
            return m[under]
        if lit and n.dot(LIGHT) > lit_min:
            return m[lit]
        return m[side]
    slots = {}
    for poly in obj.data.polygons:
        cur = mats[poly.material_index]
        if cur is not None and cur.name in names:
            continue
        mat = pick(poly.center, poly.normal)
        if mat.name not in slots:
            slots[mat.name] = mk.slot_of(obj, mat)
        poly.material_index = slots[mat.name]
    return obj


def bevelled_box(name, x0, x1, y0, y1, z0, z1, mat, bevel, segments=2):
    obj = mk.box(name, min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1), z0, z1, mat)
    if bevel > 0:
        mk.bevel(obj, bevel, segments, 35.0)
    return obj


def mirror_about_axis(objects):
    """Copies of objects mirrored about x = AX, keeping their shading (corner normals) and materials
    (polish_ice_globe.py's)."""
    flip = Matrix.Translation((AX, 0, 0)) @ Matrix.Scale(-1, 4, (1, 0, 0)) @ Matrix.Translation((-AX, 0, 0))
    out = []
    for obj in objects:
        mk.apply(obj)
        copy = obj.copy()
        copy.data = obj.data.copy()
        copy.name = obj.name + "_r"
        bpy.context.scene.collection.objects.link(copy)
        mesh = copy.data
        corner = {}
        for poly in mesh.polygons:
            for li in poly.loop_indices:
                n = mesh.corner_normals[li].vector
                corner[(poly.index, mesh.loops[li].vertex_index)] = (-n.x, n.y, n.z)
        mesh.transform(flip)
        mesh.flip_normals()
        normals = [None] * len(mesh.loops)
        for poly in mesh.polygons:
            for li in poly.loop_indices:
                normals[li] = corner[(poly.index, mesh.loops[li].vertex_index)]
        mesh.normals_split_custom_set(normals)
        out.append(copy)
    return out


# --- The deck ---------------------------------------------------------------------------------------------------------

def deck(m):
    """The deck, its rim bevelled and lit, the hatch sunk into it."""
    slab = bevelled_box("deck", XE(0), XE(44), YE(38), YE(0), SKIRT, DECK_Z, m["deck"], DECK_BEVEL, 2)
    c0, c1, r0, r1 = HATCH
    hole = mk.box("hatch_cut", XE(c0), XE(c1), YE(r1), YE(r0), HATCH_FLOOR, DECK_Z + 2.0, m["dark"])
    mk.boolean(slab, hole, "DIFFERENCE")
    mk.cleanup(slab, dissolve=0.0)
    paint(slab, m, "deck", "deck", lit="steel", keep=("dark",), lit_min=0.6)
    mk.paint(slab, lambda c, n: m["dark"] if n.y < -0.5 and n.z < 0.6 else None)
    # the hatch's floor: the deck's grey (the cut's material is on its walls and floor)
    mk.paint(slab, lambda c, n: m["deck"] if n.z > 0.9 and c.z < DECK_Z - 0.5 else None)
    mk.shade(slab, 35.0)
    return slab


def deck_parts(m):
    """The beam across the back, the panels, studs and rails (the left half's; mirrored after) and the housing."""
    left, whole = [], []
    c0, c1, r0, r1, up = BEAM
    beam = bevelled_box("beam", XE(c0), XE(c1), YE(r1), YE(r0), DECK_Z - 0.3, DECK_Z + up, m["deck"], 0.22)
    paint(beam, m, "deck", "dark", lit="steel", lit_min=0.4)
    whole.append(mk.shade(beam, 35.0))
    for i, (c0, c1, r0, r1) in enumerate(CORNER_PANELS):
        plate = bevelled_box(f"corner{i}", XE(c0), XE(c1), YE(r1), YE(r0), DECK_Z - 0.3, DECK_Z + 0.42, m["panel"],
                             0.22)
        pocket = mk.box(f"corner{i}_pocket", XE(c0) + 0.85, XE(c1) - 0.85, YE(r1) + 0.85, YE(r0) - 0.85,
                        DECK_Z + 0.28, DECK_Z + 2.0, m["panel_dark"])
        mk.boolean(plate, pocket, "DIFFERENCE")
        paint(plate, m, "panel", "panel_dark", lit="panel", keep=("panel_dark",), lit_min=0.4)
        left.append(mk.shade(plate, 35.0))
    for i, (c0, c1, r0, r1) in enumerate(SIDE_PANELS):
        plate = bevelled_box(f"side_panel{i}", XE(c0), XE(c1), YE(r1), YE(r0), DECK_Z - 0.3, DECK_Z + 0.36,
                             m["deck"], 0.2)
        paint(plate, m, "deck", "dark", lit="steel", lit_min=0.4)
        left.append(mk.shade(plate, 35.0))
    for i, (c0, c1, r0, r1) in enumerate(STUDS):
        stud = bevelled_box(f"stud{i}", XE(c0) + 0.15, XE(c1) - 0.15, YE(r1) + 0.15, YE(r0) - 0.15, DECK_Z,
                            DECK_Z + 0.95, m["panel"], 0.3)
        paint(stud, m, "panel", "panel_dark", lit="panel", lit_min=0.4)
        left.append(mk.shade(stud, 40.0))
    c0, c1, r0, r1 = RAIL
    rail = bevelled_box("rail", XE(c0), XE(c1), YE(r1), YE(r0), DECK_Z - 0.3, DECK_Z + 0.85, m["deck"], 0.3)
    for i, r in enumerate(RAIL_GROOVES):
        groove = mk.box(f"rail_groove{i}", XE(c0) - 1.0, XE(c1) + 1.0, YE(r) - 0.28, YE(r) + 0.28, DECK_Z + 0.55,
                        DECK_Z + 3.0, m["dark"])
        mk.boolean(rail, groove, "DIFFERENCE")
    paint(rail, m, "steel", "deck", lit="lit", keep=("dark",), lit_min=0.6)
    left.append(mk.shade(rail, 35.0))
    # The gun's housing, lying in the hatch.
    for i, (c0, c1, r0, r1, h) in enumerate(HOUSING):
        block = bevelled_box(f"housing{i}", XE(c0) + 0.1, XE(c1) - 0.1, YE(r1) + 0.1, YE(r0) - 0.1, HATCH_FLOOR - 0.2,
                             HATCH_FLOOR + h, m["housing"], 0.42, 2)
        paint(block, m, "housing", "housing_dark", lit="panel_dark", lit_min=0.42, under="housing_dark")
        whole.append(mk.shade(block, 35.0))
    return left, whole


# --- The head ---------------------------------------------------------------------------------------------------------

def plane_box(name, top, size=80.0):
    """Everything under the plane z = top(x, y) (a thick slab along it), for intersecting with (polish_arch.py's)."""
    s = size
    return mk.wedge(name, [(-s, -s), (s, -s), (s, s), (-s, s)], 0.0, top, bottom=lambda x, y: top(x, y) - 400.0)


def side_z(x, y):
    """The left side's plane (the right one is its mirror image)."""
    c0, z0, c1, z1 = SIDE
    a0, a1 = XE(c0), XE(c1)
    return z0 + (z1 - z0) * (x - a0) / (a1 - a0)


def front_z(x, y):
    r0, z0, r1, z1 = FRONT
    a0, a1 = YE(r0), YE(r1)
    return z0 + (z1 - z0) * (y - a0) / (a1 - a0)


def head_z(x, y):
    """The head's (unbevelled) surface over (x, y)."""
    d = abs(x - AX)
    return min(TOP_Z, side_z(AX - d, y), front_z(x, y))


def head_plan():
    left = [(XE(c), YE(r)) for c, r in HEAD_PLAN]
    right = [(MX(x), y) for x, y in reversed(left[1:-1])]
    pts = left + right
    area = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))
    return pts if area > 0 else pts[::-1]


def head(m):
    """The head: its plan cut by the planes of its sides, front and top, bevelled; the recess, the windows, the seams,
    the slots and the vents cut into it."""
    body = mk.prism("head", head_plan(), SKIRT, 40.0, m["steel"])
    for i, top in enumerate((side_z, lambda x, y: side_z(MX(x), y), front_z, lambda x, y: TOP_Z + 0.0 * x)):
        mk.boolean(body, plane_box(f"head_plane{i}", top), "INTERSECT")
    mk.cleanup(body)
    mk.bevel(body, HEAD_BEVEL, 5, 24.0)
    # tops and the faces turned to the sun light grey (the sprite's 0x07-0x0a), the rounded edges facing it most
    # brighter (its 0x0a-0x0d rims), the faces turned away a shade darker (the sun darkens them further)
    mk.paint(body, lambda c, n: m["dark"] if n.z < -0.3 else m["hi"] if (n.z < 0.86 and n.dot(LIGHT) > 0.84) else
             m["lit"] if (n.z > 0.86 or n.dot(LIGHT) > 0.6) else m["steel"])
    # The recess in the front (its floor parallel to the front), the window band's divider left standing in it.
    c0, c1, r0, r1, depth = RECESS
    floor = lambda x, y: front_z(x, y) - depth  # noqa: E731
    recess = mk.wedge("recess", [(XE(c0), YE(r1)), (XE(c1), YE(r1)), (XE(c1), YE(r0)), (XE(c0), YE(r0))], 0.0,
                      lambda x, y: 40.0, m["dark"], bottom=floor)
    mk.boolean(body, recess, "DIFFERENCE")
    # The seams across the plates, the slots down the sides and the vents at the foot (both sides).
    cutters = []
    for r in SEAMS:
        for x0, x1 in ((XE(SEAM_COLS[0]), XE(SEAM_COLS[1])), (MX(XE(SEAM_COLS[1])), MX(XE(SEAM_COLS[0])))):
            cutters.append(mk.box(f"seam{r}_{x0:.0f}", x0, x1, YE(r) - 0.24, YE(r) + 0.24, TOP_Z - 0.3, TOP_Z + 3.0,
                                  m["dark"]))
    c0, c1, r0, r1, d = SIDE_SLOT
    for sign in (1, -1):
        x0, x1 = (XE(c0), XE(c1)) if sign > 0 else (MX(XE(c1)), MX(XE(c0)))
        if sign > 0:
            top = lambda x, y: side_z(x, y) - d  # noqa: E731
        else:
            top = lambda x, y: side_z(MX(x), y) - d  # noqa: E731
        cutters.append(mk.wedge(f"slot{sign}", [(x0, YE(r1)), (x1, YE(r1)), (x1, YE(r0)), (x0, YE(r0))], 0.0,
                                lambda x, y: 40.0, m["glass_teal"], bottom=top))
    c0, c1, r0, r1, d = VENT
    for x0, x1 in ((XE(c0), XE(c1)), (MX(XE(c1)), MX(XE(c0)))):
        cutters.append(mk.wedge(f"vent{x0:.0f}", [(x0, YE(r1) - 2.0), (x1, YE(r1) - 2.0), (x1, YE(r0)), (x0, YE(r0))],
                                0.0, lambda x, y: 40.0, m["housing_dark"], bottom=lambda x, y: front_z(x, y) - d))
    for c in cutters:
        mk.boolean(body, c, "DIFFERENCE")
    mk.cleanup(body, dissolve=0.0)
    mk.shade(body, 35.0)
    return body


def window_band(m):
    """In the recess: the band of the windows (a grey frame across it, the divider standing out of it a little), the
    sills over the panes, the panes glowing; the lens' black socket under them."""
    c0, c1, r0, r1, depth = RECESS
    s0, s1, p0, p1 = WINDOW_ROWS
    floor = lambda x, y: front_z(x, y) - depth  # noqa: E731
    parts = []
    # The frame: from the recess' floor up to 0.25 under the front's surface.
    frame = mk.wedge("window_frame", [(XE(c0), YE(p1)), (XE(c1), YE(p1)), (XE(c1), YE(s0)), (XE(c0), YE(s0))],
                     0.0, lambda x, y: front_z(x, y) - 0.25, m["steel"], bottom=lambda x, y: floor(x, y) - 0.2)
    mk.bevel(frame, 0.18, 2, 30.0)
    # The window openings cut into it, the panes and the sills in them.
    openings = []
    for x0, x1 in ((XE(WINDOWS[0][0]), XE(WINDOWS[0][1])), (MX(XE(WINDOWS[0][1])), MX(XE(WINDOWS[0][0])))):
        openings.append((x0, x1))
        cutter = mk.wedge(f"window_cut{x0:.0f}", [(x0, YE(p1)), (x1, YE(p1)), (x1, YE(s0)), (x0, YE(s0))], 0.0,
                          lambda x, y: 40.0, m["dark"], bottom=lambda x, y: front_z(x, y) - 0.75)
        mk.boolean(frame, cutter, "DIFFERENCE")
    paint(frame, m, "steel", "steel", lit="lit", keep=("dark",), top_min=0.99, lit_min=0.75)
    mk.shade(frame, 35.0)
    parts.append(frame)
    for x0, x1 in openings:
        pane = mk.wedge(f"pane{x0:.0f}", [(x0 + 0.05, YE(p1) + 0.1), (x1 - 0.05, YE(p1) + 0.1), (x1 - 0.05, YE(p0)),
                                          (x0 + 0.05, YE(p0))], 0.0, lambda x, y: front_z(x, y) - 0.62, m["light"],
                        bottom=lambda x, y: front_z(x, y) - 0.9)
        sill = mk.wedge(f"sill{x0:.0f}", [(x0 + 0.05, YE(s1)), (x1 - 0.05, YE(s1)), (x1 - 0.05, YE(s0) - 0.1),
                                          (x0 + 0.05, YE(s0) - 0.1)], 0.0, lambda x, y: front_z(x, y) - 0.45,
                        m["glass_teal"], bottom=lambda x, y: front_z(x, y) - 0.9)
        mk.bevel(sill, 0.12, 1, 30.0)
        parts += [mk.shade(pane, 30.0), mk.shade(sill, 30.0)]
    d0, d1 = DIVIDER
    divider = mk.wedge("divider", [(XE(d0) + 0.1, YE(p1) - 0.1), (XE(d1) - 0.1, YE(p1) - 0.1), (XE(d1) - 0.1, YE(s0)),
                                   (XE(d0) + 0.1, YE(s0))], 0.0, lambda x, y: front_z(x, y) - 0.05, m["steel"],
                       bottom=lambda x, y: floor(x, y))
    mk.bevel(divider, 0.25, 2, 30.0)
    paint(divider, m, "steel", "deck", lit="lit", top_min=0.99, lit_min=0.6)
    parts.append(mk.shade(divider, 35.0))
    return parts


def front_frame():
    """The turn putting a part made lying flat (z up) onto the front's slope: (its normal, the matrix)."""
    r0, z0, r1, z1 = FRONT
    a0, a1 = YE(r0), YE(r1)
    slope = (z1 - z0) / (a1 - a0)         # dz/dy (positive: higher towards the back)
    n = Vector((0.0, -slope, 1.0)).normalized()
    ang = math.atan2(-n.y, n.z)
    return n, Matrix.Rotation(-ang, 4, "X")


def lens(m):
    """The lens: a glossy ellipsoid set into the recess' floor, standing out of it; its middle hotter, its glint at its
    upper left; a black socket round it."""
    c, r, ax, ay, h = LENS
    x0, y0 = XE(c), YE(r)
    depth = RECESS[4]
    _, turn = front_frame()
    base = Vector((x0, y0, front_z(x0, y0) - depth))
    socket = mk.ball("lens_socket", (0.0, 0.0, 0.0), (ax + 0.7, ay + 0.6, 0.55), m["black"], 36, 10)
    body = mk.ball("lens", (0.0, 0.0, 0.0), (ax, ay, h), m["lens"], 40, 16)
    gx, gy, gax, gay = LENS_GLINT
    gx, gy = XE(gx) - x0, YE(gy) - y0
    values = []
    for v in body.data.vertices:
        # lit from the upper left as the sprite draws it: its light middle shifted that way, the glint in it
        e = math.hypot((v.co.x + 0.22 * ax) / (0.78 * ax), (v.co.y - 0.1 * ay) / (0.8 * ay))
        g = math.hypot((v.co.x - gx) / gax, (v.co.y - gy) / gay)
        values.append(max(1.0 - e, 2.0 - g) if v.co.z > 0 else -1.0)
    band_split(body, values, [(-9.0, m["lens"]), (0.0, m["light"]), (0.45, m["glass"]), (1.0, m["lens_hot"])])
    k.smooth(body, 70)
    place = Matrix.Translation(base) @ turn
    for obj in (socket, body):
        obj.data.transform(place)
        obj.data.update()
    return [socket, body]


def head_rails(m, hit):
    """A bar along each plate's outer edge, on along the front down to the window band's foot."""
    c0, c1, r0, r1, proud = HEAD_RAIL
    out = []
    for name, x0, x1 in (("head_rail", XE(c0), XE(c1)), ("head_rail_r", MX(XE(c1)), MX(XE(c0)))):
        xm, hw = (x0 + x1) / 2, (x1 - x0) / 2
        points, ups = [], []
        steps = 44
        for i in range(steps + 1):
            y = YE(r0) + (YE(r1) - YE(r0)) * i / steps
            h = hit(xm, y)
            points.append(Vector((xm, y, h[0].z if h else head_z(xm, y))))
            ups.append(h[1] if h else Vector((0, 0, 1)))
        bar = mk.bar(name, points, ups, hw, proud, 0.6, m["lit"], 12, 3.0)
        paint(bar, m, "hi", "steel", lit="hi", top_min=0.8, lit_min=0.7)
        out.append(k.smooth(bar, 40))
    return out


def lamps(m, hit):
    out = []
    for i, (c, r) in enumerate(LAMPS):
        x, y = XE(c), YE(r)
        z = TOP_Z - 0.05
        ring = mk.lathe(f"lamp_ring{i}", [(LAMP_R + 0.45, z - 0.4), (LAMP_R + 0.45, z + 0.2), (LAMP_R + 0.2, z + 0.38),
                                          (LAMP_R, z + 0.38), (LAMP_R, z - 0.2), (0.01, z - 0.2)], (x, y), m["dark"],
                        28)
        k.smooth(ring, 40)
        dome = mk.dome(f"lamp{i}", (x, y), (LAMP_R, LAMP_R, 0.85), z, m["light"], 24, 7)
        out += [ring, dome]
    return out


def skylight(m):
    """The skylight: four rounded glass panes lying along the screen in a frame whose dark floor shows between them (the
    sprite's ribs), each pane light at the back and the front, teal between (band_split along the rows)."""
    c0, c1, r0, r1, h = SKY
    x0, x1, y0, y1 = XE(c0), XE(c1), YE(r1), YE(r0)
    frame = bevelled_box("sky_frame", x0 - 0.55, x1 + 0.55, y0 - 0.55, y1 - 0.05, TOP_Z - 0.3, TOP_Z + 0.45,
                         m["steel"], 0.25)
    pocket = mk.box("sky_pocket", x0 + 0.05, x1 - 0.05, y0 + 0.05, y1 - 0.6, TOP_Z + 0.12, TOP_Z + 3.0,
                    m["panel_dark"])
    mk.boolean(frame, pocket, "DIFFERENCE")
    paint(frame, m, "lit", "steel", lit="hi", keep=("panel_dark",), lit_min=0.84)
    mk.shade(frame, 35.0)
    parts = [frame]
    t0, t1 = SKY_BANDS
    ya, yb = y0 + 0.25, y1 - 0.75
    for i, cx in enumerate(SKY_PANES):
        rings = []
        count = 26
        for j in range(count + 1):
            y = ya + (yb - ya) * j / count
            edge = min(y - ya, yb - y)
            f = math.sqrt(max(0.0, 1.0 - (1.0 - min(1.0, edge / 0.8)) ** 2))   # the ends rounded down
            w = max(0.05, PANE_W * (0.55 + 0.45 * f))
            rings.append(k.ring(y, w, max(0.05, h * f), 20, z=TOP_Z + 0.12, x=cx, bottom=0.05, power=2.6))
        pane = k.loft(f"sky_pane{i}", rings, m["glass"])
        rows = [28.0 - v.co.y for v in pane.data.vertices]
        values = [(t1 - t0) / 2 - abs(rv - (t0 + t1) / 2) for rv in rows]
        band_split(pane, values, [(-99.0, m["glass"]), (0.0, m["glass_teal"])])
        parts.append(k.smooth(pane, 60))
    return parts


def build_whole():
    m = materials()
    parts = [deck(m)]
    left, whole = deck_parts(m)
    parts += left + mirror_about_axis(left) + whole
    body = head(m)
    parts.append(body)
    parts += window_band(m)
    parts += lens(m)
    bpy.context.view_layer.update()
    hit = mk.surface([body])
    parts += head_rails(m, hit)
    parts += lamps(m, hit)
    parts += skylight(m)
    whole_parts = [o for o in mk.meshes() if len(o.data.polygons) > 0]
    for obj in whole_parts:
        mk.apply(obj)
    triangulate(whole_parts)
    bpy.context.view_layer.update()
    return whole_parts, m


# --- Checks, previews, export -----------------------------------------------------------------------------------------

def object_mask(sheet):
    """The bunker's own pixels in the 48 x 56 picture: the deck (columns 0-43 of rows 0-37) and the head (columns 4-39
    of rows 38-50, its sides' outline on row 51) with what lies in them (the lens' transparent pixels included); the
    ice round it and the shadow on the ice left out."""
    mask = [[False] * 48 for _ in range(56)]
    for r in range(56):
        for c in range(48):
            mask[r][c] = ((r <= 37 and c <= 43) or (38 <= r <= 50 and 4 <= c <= 39) or
                          (r == 51 and (4 <= c <= 14 or 29 <= c <= 39)))
    return mask


def build():
    k.reset()
    options = k.args()
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    whole, m = build_whole()
    low, high = mk.bounds(whole)
    print("== whole bunker: %d triangles, %d objects, %d materials, x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f" % (
        mk.triangles(whole), len(whole), len(mk.materials_of(whole)), low.x, high.x, low.y, high.y, low.z, high.z))
    if options.get("stats") == "1":
        for obj in sorted(whole, key=lambda o: -mk.triangles([o]))[:20]:
            print("   %-22s %6d" % (obj.name, mk.triangles([obj])))
    mask = None
    if "check" in options:
        sheets = options["check"]
        sheet = os.path.join(sheets, "enemy_7.png") if os.path.isdir(sheets) else sheets
        mask = object_mask(sheet)
        mk.compare("whole (7 1 3 above 39 41, the bunker's own pixels)", mk.coverage(whole, 48, 56), mask)
    bpy.context.scene.view_settings.view_transform = "Standard"   # previews in the game's colours
    if "preview" in options:
        mk.preview(options["preview"] + "ice_bunker_whole", whole, size=(48, 56), scale=10, distance=1.9)
    if "whole" in options:
        mk.export(whole, options["whole"])
    if only == ["none"]:
        return
    for name, sprite, box in PIECES:
        if only and name not in only:
            continue
        parts = [p for p in (cut(src, box, m["dark"]) for src in whole) if p is not None]
        db.drop_unused(parts)
        mk.transform(parts, Matrix.Translation((-(box[0] + box[1]) / 2, -(box[2] + box[3]) / 2, 0)))
        bpy.context.view_layer.update()
        triangulate(parts)
        parts = [db.join(parts, name)]
        parts[0].data.name = name
        for src in whole:
            src.hide_render = True
        if mask is not None:
            c0, r0 = SPRITE_CELLS[sprite]
            mk.compare("%s (7 %d)" % (name, sprite), mk.coverage(parts, 24, 28),
                       [row[c0:c0 + 24] for row in mask[r0:r0 + 28]])
        mk.report(name, parts, os.path.join(out, name + ".glb"))
        if "preview" in options and options.get("pieces") == "1":
            mk.preview(options["preview"] + name, parts)
        for obj in parts:
            data = obj.data
            bpy.data.objects.remove(obj)
            if data.users == 0:
                bpy.data.meshes.remove(data)
        for src in whole:
            src.hide_render = False


if __name__ == "__main__":
    build()
