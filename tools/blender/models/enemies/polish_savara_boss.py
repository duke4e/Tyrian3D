"""SAVARA's boss, the red war machine at the end of SAVARA, SAVARA IV, SAVARA Y and TORM (ground enemies) and of
SAVARA V (sky enemies), 144 x 112: sheet F, twenty 2x2 sprites, each an enemy of its own (480-499), which the levels
always place as one picture and move together (SAVARA's events at t 4801, type 6: 480-485 = F 153 155 157 159 161 163
at x 80 + 24 i, y -28-84; 486-491 = F 191 ... 201 under them; 492-496 = F 230 232 234 236 238 12 pixels to the right,
y -28-28; 497-499 = F 270 272 274 36 pixels to the right, y -28; SAVARA IV, SAVARA V, SAVARA Y and TORM the same, and
episode 6's ROOST and GREY MOON take SAVARA's and TORM's boss blocks). Polished 2026-10-21; it replaces wave3_s_boss.py
(reliefs inflated from the pixels and painted pixel by pixel) and wave1_c.py's outer fins (savara_fin_left / _right).
models.cfg: model savara_boss_<sprite> enemies/savara_boss_<sprite>.glb origin (the frame models below too); sprite f
<sprite> savara_boss_<sprite> yaw=0 (153, 155, 161 and 163, which hold the fins' hot backs, with a faint orange glow);
frame f <frame> savara_boss_<frame>. No damaged look (dgr 0 for all twenty).

The windows of 232 and 236 animate (enemies 493 and 495: 232 165 165 203 203 241 241 279 279 279 241 241 241 203 203
203 165 165 165 232, the same with 236 167 205 243 281; no other enemy, launched ones included, shows these sprites):
frame models savara_boss_<frame> (frame f <frame> savara_boss_<frame>), the same piece with the windows' contents
changed: 232 and 236 the windows dark (the shutters drawn up, the lens dark), 165 / 167 the grey shutters coming down,
203 / 205 the shutters lower and a dim red eye under them, 241 / 243 the eye bigger and lit, 279 / 281 hot, a yellow
core in it; all with their piece's bounds. (In the sprites the frames also move everything under the band up a pixel;
the models keep the rest of the piece as it is.)

The picture is its own mirror image about the middle of pixel column 72 (column c is column 144 - c): the left half is
built and mirrored, the parts across the middle are built whole. What differs: the light, from the upper left (the
left edges drawn lit, the right ones outlined black, the right half darker), the right outer fin and the right half's
outer outline drawn a row lower than the left ones (rows 12-42 against 11-41), and the right pod's tip a pixel longer.
As the sprites and their 4x upscales draw it (the picture's columns and rows):
- The hull: a broad red body (columns 5-139 of rows 13-78), its sides rolling down to the outline (columns 5-13); on its
  back a deck (rows 13-42) of beams between three bays on each side (columns 14-22, 26-34, 38-46), a groove along each
  beam, an inner panel by the prow (columns 47-60: a groove, a lit rib, a hatch); in front of it a lower shelf (rows
  43-56) with grooves across, its front edge falling to the band; the channels in front of the fins run on through
  the shelf (columns 16-21, 29-32, 41-44), the outer one through the fender round the band's end (rows 56-78), the inner
  one through the lower flank.
- Six heat fins (columns 14-22 of rows 11-41, 26-34 of 5-35, 38-46 of 1-30 and their mirror images), set in the bays
  and rising towards their back ends past the hull's back edge: black frames round glowing panels, dark red at their
  roots, red and orange towards their backs, three hot slats across them (the sprite's yellow lines), the very end a
  little cooler.
- The domed prow (columns 61-83 of rows 5-42): a faceted hood, a seam down its middle, its back rounded and sloping,
  its front a tall face over the pit.
- The pit (columns 61-83 of rows 42-72): two steel rods (columns 68-71 and 73-76) running from under the prow's front
  over the band to the gate's block, a collar on each (rows 50-53), dark plates beside them.
- The band (columns 29-115 of rows 57-69): a black bar across the machine, grey bumpers rounding its ends (columns
  29-36), four windows on it (columns 37-47, 49-59 and their mirror images): grey frames, a sill under each, the shutter
  and the eye inside (the frames above).
- In front (rows 70-111): the lower flanks (columns 37-48, sloping down to the front), the pods (columns 49-59 to row
  111): long rounded pontoons, a slot in each holding a glowing pink rod (columns 54-56 of rows 74-103); between them
  the gate's block (columns 61-83 of rows 73-103): a ledge across its back, small vents, a dark doorway at its front
  (columns 65-80 of rows 85-103) holding two red barrels; a dark floor under it all, seen in the gaps between them
  (the sprites' black lines).

Built as a CAD modeller would (polish_machine_kit): plates are prisms of their plans cut by the planes of their tops and
chamfers (exact booleans), their bays, channels, grooves, slots and the doorway cut by booleans, edges bevelled, flat
faces kept flat; round parts lofted (the hull's sides, the bumpers, the rods, the pink rods, the barrels, the lenses).
Faces are painted by how they face the light from the upper left (a few shades of the sprite's own palette indices:
the red ramp 0x42-0x49, the greys 0x02-0x0b), the left half's parts after the mirroring, each copy by its own faces
(so the right half is lit from the upper left too, darker, as the sprites draw it); smooth parts in bands along smooth
borders (polish_orb_red.band_split). The glows are well under 1: the fins (0x72-0x7b: 0.2-0.55, matte), the pink rods
(0x4c, 0x4f: 0.35, 0.5), the eyes (0x72-0x7c: 0.2-0.6); the black band a little (0.06-0.08, so that it doesn't read
as a hole). The whole boss is then cut along the sprites' edges (polish_arch.cut, here keeping the faces' own winding:
the pieces keep the whole's shading across the cuts, their cuts capped dark) into the twenty pieces, each moved so
that its sprite's centre is its origin; no face lies on a cut (grooves and walls kept off the pieces' edges); every
mesh is triangulated before the export (polish_k_pod.triangulate), so the output is the same with and without --check;
each piece's parts are joined into one mesh. The pieces stand from z 0 (the layer) up to 14.6.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera. The whole's
origin is the picture's middle (pixel edge 72, 56: the corner where F 157, 159, 195 and 197 meet): column c's left
edge is x = c - 72, row r's top edge y = 56 - r; the pieces' edges are x = -72, -48, ... 72 (rows 0-55), -60, -36, ...
(rows 56-83), -36 ... 36 (rows 84-111) and y = 56, 28, 0, -28, -56. Built about X = x - 0.5 = 0 (the middle of column
72) and moved there at the end (AXIS_X).

Replaces wave3_s_boss.py (all of it: the boss is all it builds) and wave1_c.py's savara_fin_left / savara_fin_right
(unused since wave3_s_boss.py took F 153 and 163): remove them so that they don't overwrite these models.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes of the whole
and of each piece and frame against enemy_F.png), --preview <prefix> (the whole's and each piece's top and 3/4 views),
--only <model,...> (pieces and frames to export; "none": none), --whole <file.glb> (the uncut boss as well, for
looking at), --stats 1 (each piece's largest parts).
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
import polish_deli_boss as db  # noqa: E402  (its generic helpers: plates, mirroring, the pieces' export)
import polish_tusk_boss as tb  # noqa: E402  (ngons_to_triangles, banded)
from polish_k_pod import triangulate  # noqa: E402
from polish_orb_red import band_split  # noqa: E402

AXIS_X = 0.5                 # the middle of column 72, where the built boss's X = 0 goes

# The pieces: sprite, the picture's column and row of its top left corner.
PLACES = [(153, 0, 0), (155, 24, 0), (157, 48, 0), (159, 72, 0), (161, 96, 0), (163, 120, 0),
          (191, 0, 28), (193, 24, 28), (195, 48, 28), (197, 72, 28), (199, 96, 28), (201, 120, 28),
          (230, 12, 56), (232, 36, 56), (234, 60, 56), (236, 84, 56), (238, 108, 56),
          (270, 36, 84), (272, 60, 84), (274, 84, 84)]
CELLS = [("savara_boss_%d" % s, s, c, r) for s, c, r in PLACES]


def box_of(col, row):
    """A piece's box in the whole's coordinates (x0, x1, y0, y1): the picture's pixel edge (72, 56) is the origin."""
    return (col - 72.0, col - 48.0, 28.0 - row, 56.0 - row)


PIECES = [(name, sprite, box_of(col, row)) for name, sprite, col, row in CELLS]


def X(c):
    """The left edge of the picture's column c (fractions allowed), in the built frame (X = 0: column 72's middle)."""
    return c - 72.5


def Y(r):
    """The top edge of the picture's row r."""
    return 56.0 - r


def P(c, r):
    return (X(c), Y(r))


def ccw(pts):
    area = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))
    return pts if area > 0 else pts[::-1]


def plan(points, rounding=0):
    """A plan given in pixel edges (c, r), counter-clockwise seen from above; rounding: Chaikin passes."""
    pts = ccw([P(c, r) for c, r in points])
    return mk.chaikin(pts, rounding) if rounding else pts


def whole_plan(left_path, rounding=0):
    """A plan symmetric about the middle from the path of its left half (pixel edges, from the middle at one end to
    the middle at the other)."""
    left = [P(c, r) for c, r in left_path]
    right = [(-x, y) for x, y in reversed(left[1:-1])]
    pts = ccw(left + right)
    return mk.chaikin(pts, rounding) if rounding else pts


def rect(c0, c1, r0, r1):
    return plan([(c0, r0), (c1, r0), (c1, r1), (c0, r1)])


def level(z):
    return lambda x, y: z + 0.0 * x


def y_plane(r0, z0, r1, z1):
    a0, a1 = Y(r0), Y(r1)
    return lambda x, y: z0 + (z1 - z0) * (y - a0) / (a1 - a0)


def smoothstep(e0, e1, x):
    t = min(1.0, max(0.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


def interp(table, v):
    """Linear interpolation in a table [(key, value)] sorted by key (clamped at its ends)."""
    if v <= table[0][0]:
        return table[0][1]
    for (a, va), (b, vb) in zip(table, table[1:]):
        if v <= b:
            return va + (vb - va) * (v - a) / (b - a)
    return table[-1][1]


# --- Materials --------------------------------------------------------------------------------------------------------

def materials():
    pal = k.level_palette()

    def mat(name, index, metallic=0.4, roughness=0.4, glow=0.0, glow_index=None):
        if glow > 0:
            return k.material("savara_" + name, palette=index, metallic=metallic, roughness=roughness,
                              emission=pal[index if glow_index is None else glow_index], emission_strength=glow)
        return k.material("savara_" + name, palette=index, metallic=metallic, roughness=roughness)
    return {
        "core": mat("core", 0x01, 0.25, 0.65),
        # The red armour: dark (faces away from the light), red, mid (tops), lit (faces towards the light).
        "red_dark": mat("red_dark", 0x42, 0.25, 0.45),
        "red": mat("red", 0x44, 0.25, 0.4),
        "red_mid": mat("red_mid", 0x46, 0.25, 0.36),
        "red_lit": mat("red_lit", 0x49, 0.22, 0.32),
        # The fins' black frames.
        "frame": mat("frame", 0x02, 0.55, 0.3),
        "frame_lit": mat("frame_lit", 0x05, 0.5, 0.28),
        # The fins' glowing panels, cooler at their roots, hottest towards their backs; the slats across them.
        "fin_dark": mat("fin_dark", 0x72, 0.0, 0.8, glow=0.2),
        "fin_low": mat("fin_low", 0x74, 0.0, 0.78, glow=0.28),
        "fin": mat("fin", 0x76, 0.0, 0.75, glow=0.38),
        "fin_hot": mat("fin_hot", 0x78, 0.0, 0.72, glow=0.45),
        "fin_slat": mat("fin_slat", 0x7b, 0.0, 0.7, glow=0.55),
        # The black band (a little light of its own so that it doesn't read as a hole) and its glare.
        "band": mat("band", 0x02, 0.45, 0.16, glow=0.08, glow_index=0x03),
        "band_lit": mat("band_lit", 0x05, 0.4, 0.14, glow=0.06, glow_index=0x05),
        "steel_dark": mat("steel_dark", 0x04, 0.5, 0.36),
        "steel": mat("steel", 0x07, 0.55, 0.32),
        "steel_lit": mat("steel_lit", 0x0b, 0.5, 0.28),
        # The pods' pink rods.
        "rod": mat("rod", 0x4c, 0.05, 0.3, glow=0.35),
        "rod_hot": mat("rod_hot", 0x4f, 0.05, 0.25, glow=0.5),
        # The windows' lenses and eyes as the frames show them.
        "lens": mat("lens", 0x03, 0.4, 0.12, glow=0.06, glow_index=0x04),
        "eye_dim": mat("eye_dim", 0x72, 0.0, 0.3, glow=0.2),
        "eye": mat("eye", 0x75, 0.0, 0.28, glow=0.35),
        "eye_hot": mat("eye_hot", 0x79, 0.0, 0.25, glow=0.5),
        "eye_core": mat("eye_core", 0x7c, 0.0, 0.2, glow=0.6),
    }


LIGHT = Vector((-0.5, 0.45, 0.74)).normalized()


def paint_red(obj, m, light=LIGHT, keep=("core",), lit_min=0.82, mid_min=0.62):
    """Red faces by how they face the light from the upper left: lit, mid (tops), red, dark (away from it); the
    undersides dark."""
    keep_names = {m[n].name for n in keep}
    mats = obj.data.materials
    slots = {}
    for poly in obj.data.polygons:
        if mats[poly.material_index].name in keep_names:
            continue
        n = poly.normal
        d = n.dot(light)
        if n.z < -0.4:
            pick = "red_dark"
        elif d > lit_min:
            pick = "red_lit"
        elif d > mid_min:
            pick = "red_mid"
        elif n.z > 0.45 or d > 0.12:
            pick = "red"
        else:
            pick = "red_dark"
        if pick not in slots:
            slots[pick] = mk.slot_of(obj, m[pick])
        poly.material_index = slots[pick]
    return obj


def paint_steel(obj, m, light=LIGHT, lit_min=0.8):
    def pick(c, n):
        d = n.dot(light)
        if d > lit_min:
            return m["steel_lit"]
        if n.z > 0.5 or d > 0.25:
            return m["steel"]
        return m["steel_dark"]
    return mk.paint(obj, pick)


def paint_frame(obj, m, light=LIGHT):
    return mk.paint(obj, lambda c, n: m["frame_lit"] if n.dot(light) > 0.84 else m["frame"])


# The left half's parts are painted after the mirroring, each copy by its own faces (so that the right half is lit
# from the upper left too, as the sprites draw it): object name -> its paint.
PAINTS = {}


def later(obj, paint):
    PAINTS[obj.name] = paint
    return obj


def mirror_half(objects):
    """Mirrored copies of the left half's parts about X = 0 (polish_deli_boss.mirror_half), then the originals and
    their copies painted."""
    copies = db.mirror_half(objects)
    for obj, copy in zip(objects, copies):
        paint = PAINTS.get(obj.name)
        if paint is not None:
            paint(obj)
            paint(copy)
    return copies


def plate(name, outline, planes, mat, bevel=0.45, segments=3, bottom=0.0, cutters=()):
    return db.plate(name, outline, planes, mat, bevel=bevel, segments=segments, bottom=bottom, cutters=cutters)


def above_box(name, bottom, size=200.0):
    """Everything over the surface z = bottom(x, y) (a thick slab on it), for intersecting with."""
    s = size
    return mk.wedge(name, [(-s, -s), (s, -s), (s, s), (-s, s)], 0.0, lambda x, y: bottom(x, y) + 400.0, bottom=bottom)


def remove(obj):
    data = obj.data
    bpy.data.objects.remove(obj)
    if data.users == 0:
        bpy.data.meshes.remove(data)


# --- The hull ---------------------------------------------------------------------------------------------------------
Z_HULL = 4.5                 # the hull under the plates (the bays' and the pit's floor at 2.5)
Z_DECK = 8.0                 # the deck (rows 13-42)
Z_SHELF = 7.4                # the shelf (rows 42.5-56.5) and the fender round the band's end
Z_PIT = 2.5
# The outline of the hull's left side (pixel edges, row by row), from the back (row 25) to the front (row 78).
OUTLINE = [(13.0, 25.0), (12.0, 26.0), (11.0, 27.0), (10.0, 28.0), (9.0, 29.4), (8.4, 30.8), (7.6, 32.0),
           (6.8, 33.4), (6.0, 35.0), (5.3, 36.8), (5.0, 39.0), (5.0, 44.0), (5.4, 46.2), (6.2, 47.8), (7.0, 49.4),
           (7.8, 51.0), (8.6, 52.8), (9.6, 54.6), (10.8, 56.0), (12.0, 57.6), (12.8, 59.2), (13.6, 60.8),
           (14.4, 62.4), (15.4, 63.6), (16.6, 64.8), (17.8, 66.0), (19.0, 67.2), (20.2, 68.4), (21.4, 69.6),
           (22.6, 70.8), (23.6, 72.2), (24.6, 73.6), (25.6, 74.8), (27.0, 75.9), (28.6, 76.9), (30.2, 77.8),
           (31.4, 78.4)]
# The roll down the hull's side: its inner edge (rows: column), the outline outside it.
ROLL_INNER = [(25.0, 13.4), (27.0, 13.75), (56.0, 13.75), (58.5, 14.6), (61.0, 15.4), (63.6, 16.2)]
ROLL_ROWS = (25.3, 63.4)
ROLL_TOP = 7.6
ROLL_PROFILE = [(0.0, 0.0), (0.0, 1.0), (0.03, 1.8), (0.09, 2.8), (0.18, 3.8), (0.3, 4.8), (0.45, 5.7), (0.62, 6.5),
                (0.8, 7.1), (1.0, 7.6), (1.0, 0.0)]


def outline_x(r):
    """The outline's column at row r (a polyline through OUTLINE)."""
    pts = OUTLINE
    if r <= pts[0][1]:
        return pts[0][0]
    for (c0, r0), (c1, r1) in zip(pts, pts[1:]):
        if r <= r1:
            return c0 + (c1 - c0) * (r - r0) / (r1 - r0)
    return pts[-1][0]


def roll_inner_x(r):
    return interp(ROLL_INNER, r)


def roll(m):
    """The hull's left side rolling down to the outline: a loft of sections across it (from the outline to the
    deck's edge) down the screen."""
    r0, r1 = ROLL_ROWS
    count = 70
    rings = []
    for i in range(count + 1):
        r = r1 + (r0 - r1) * i / count          # from the front to the back: increasing y
        xo, xi = X(outline_x(r)), X(roll_inner_x(r))
        w = xi - xo
        top = ROLL_TOP * (0.55 + 0.45 * smoothstep(0.0, 3.0, w))
        ring = []
        for u, z in ROLL_PROFILE:
            ring.append(Vector((xo + u * w, Y(r), z * top / ROLL_TOP)))
        rings.append(ring)
    first, last = rings[0], rings[-1]
    body = k.loft("roll", rings, m["red"], start_point=sum(first, Vector()) / len(first),
                  end_point=sum(last, Vector()) / len(last))
    k.smooth(body, 50)
    return later(body, lambda o: k.smooth(tb.banded(o, LIGHT, [(-9.0, m["red_dark"]), (0.15, m["red"]),
                                                               (0.6, m["red_mid"]), (0.88, m["red_lit"])]), 50))


def hull_plan():
    """The hull under the plates (left half and mirrored): the back edge stepping out past the beams, the outline
    (inside the roll), the front edge."""
    back = [(72.5, 13.4), (47.0, 13.4), (47.0, 14.4), (35.0, 14.4), (35.0, 19.4), (23.0, 19.4), (23.0, 25.2),
            (13.8, 25.2)]
    side = [(outline_x(r) + 0.8, r) for r in [26.0 + 2.0 * i for i in range(19)]] + \
           [(c + 0.6, r) for c, r in OUTLINE if r > 63.0]
    front = [(37.0, 78.2), (37.0, 72.6), (72.5, 72.6)]
    return whole_plan(back + side + front, 1)


def hull(m):
    body = mk.prism("hull", hull_plan(), 0.0, Z_HULL, m["red"])
    mk.cleanup(body)
    pit = mk.prism("pit_cut", rect(61.1, 83.9, 42.6, 72.6), Z_PIT, 30.0, m["core"])
    mk.boolean(body, pit, "DIFFERENCE")
    mk.cleanup(body)
    mk.bevel(body, 0.4, 2, 30.0)
    mk.shade(body, 35.0)
    mk.paint(body, lambda c, n: m["core"] if (n.z < -0.5 or (abs(c.x) < 11.6 and Y(72.6) < c.y < Y(42.6) and
                                                             c.z < Z_PIT + 0.2)) else None)
    paint_red(body, m)
    return body


# --- The deck, the shelf, the fender ----------------------------------------------------------------------------------
# The deck (left half): beams between the fins' bays, the inner panel by the prow; its back edge at the beams' ends.
DECK = [(61.0, 13.0), (47.0, 13.0), (47.0, 31.0), (38.0, 31.0), (38.0, 14.0), (35.0, 14.0), (35.0, 36.0),
        (26.0, 36.0), (26.0, 19.0), (23.0, 19.0), (23.0, 42.6), (61.0, 42.6)]
SHELF = [(13.75, 42.4), (61.0, 42.4), (61.0, 56.6), (13.75, 56.6)]
SHELF_FRONT = (52.4, Z_SHELF, 56.6, 5.0)
FENDER = [(13.75, 51.6), (29.4, 51.6), (29.4, 56.2), (28.4, 57.0), (27.6, 58.4), (27.3, 60.5), (27.3, 65.5),
          (27.6, 67.6), (28.4, 69.0), (29.6, 69.8), (37.0, 69.8), (37.0, 78.2), (31.2, 78.2), (29.0, 77.0),
          (27.0, 75.7), (25.4, 74.3), (24.0, 72.6), (22.8, 71.0), (21.4, 69.4), (19.4, 67.6), (17.6, 65.8),
          (16.3, 64.2), (16.0, 63.5), (15.4, 61.0), (14.6, 58.5), (13.75, 56.0)]
# The channels in front of the fins (columns of their walls; rows), the beams' grooves, the inner panel's groove and
# hatch, the grooves across the shelf.
CHANNELS = [(16.0, 21.0, 41.6, 69.4), (29.0, 33.0, 35.6, 56.8), (41.0, 45.0, 30.6, 56.8)]
CHANNEL_DEPTH = 1.6
GROOVES = [(24.1, 24.9, 18.0, 69.4), (36.1, 36.9, 13.0, 56.8), (48.1, 48.9, 12.0, 43.0)]
GROOVE_DEPTH = 0.7
HATCH = (55.0, 60.0, 22.0, 40.0, 0.8)
INNER_RIB = (49.2, 50.8, 13.5, 42.3, 0.55)   # the lit rib down the inner panel: columns, rows, how high
SHELF_GROOVES = [(37.6, 61.5, 47.0, 47.9), (37.6, 61.5, 50.0, 51.2)]


def channel_cutter(name, c0, c1, r0, r1, top, depth, mat):
    """A channel along the screen: its left wall upright, its right wall sloping (lit, as the sprites draw it)."""
    x0, x1 = X(c0), X(c1)
    w = x1 - x0
    section = [(x0, top - depth), (x1 - 0.35 * w, top - depth), (x1, top + 0.01), (x1, 30.0), (x0, 30.0)]
    body = mk.prism(name, [(x, z) for x, z in section], Y(r1), Y(r0), mat, axis="y")
    return body


def groove_cutter(name, c0, c1, r0, r1, top, depth, mat):
    return mk.prism(name, rect(c0, c1, r0, r1), top - depth, 30.0, mat)


def deck(m):
    cutters = [channel_cutter(f"deck_ch{i}", c0, c1, r0, r1, Z_DECK, CHANNEL_DEPTH, m["red_dark"])
               for i, (c0, c1, r0, r1) in enumerate(CHANNELS)]
    cutters += [groove_cutter(f"deck_gr{i}", c0, c1, r0, r1, Z_DECK, GROOVE_DEPTH, m["red_dark"])
                for i, (c0, c1, r0, r1) in enumerate(GROOVES)]
    c0, c1, r0, r1, d = HATCH
    cutters.append(groove_cutter("deck_hatch", c0, c1, r0, r1, Z_DECK, d, m["red_dark"]))
    body = plate("deck", plan(DECK), [level(Z_DECK)], m["red"], bevel=0.4, segments=2, bottom=Z_HULL - 1.0,
                 cutters=cutters)
    tb.ngons_to_triangles(body)
    later(body, lambda o: paint_red(o, m, keep=("core", "red_dark")))
    c0, c1, r0, r1, h = INNER_RIB
    rib = plate("deck_rib", rect(c0, c1, r0, r1), [level(Z_DECK + h)], m["red"], bevel=0.3, segments=2,
                bottom=Z_DECK - 1.0)
    later(rib, lambda o: paint_red(o, m))
    return body


def shelf(m):
    cutters = [channel_cutter(f"shelf_ch{i}", c0, c1, r0, r1, Z_SHELF, CHANNEL_DEPTH, m["red_dark"])
               for i, (c0, c1, r0, r1) in enumerate(CHANNELS)]
    cutters += [groove_cutter(f"shelf_gr{i}", c0, c1, r0, r1, Z_SHELF, GROOVE_DEPTH, m["red_dark"])
                for i, (c0, c1, r0, r1) in enumerate(GROOVES)]
    cutters += [groove_cutter(f"shelf_x{i}", c0, c1, r0, r1, Z_SHELF, 0.5, m["red_dark"])
                for i, (c0, c1, r0, r1) in enumerate(SHELF_GROOVES)]
    body = plate("shelf", plan(SHELF), [level(Z_SHELF), y_plane(*SHELF_FRONT)], m["red"], bevel=0.4, segments=2,
                 bottom=Z_HULL - 1.0, cutters=cutters)
    tb.ngons_to_triangles(body)
    later(body, lambda o: paint_red(o, m, keep=("core", "red_dark")))
    return body


def fender(m):
    cutters = [channel_cutter("fender_ch", *CHANNELS[0], Z_SHELF, CHANNEL_DEPTH, m["red_dark"]),
               groove_cutter("fender_gr", *GROOVES[0], Z_SHELF, GROOVE_DEPTH, m["red_dark"])]
    body = plate("fender", plan(FENDER, 1), [level(Z_SHELF)], m["red"], bevel=0.5, segments=3, bottom=Z_HULL - 1.0,
                 cutters=cutters)
    tb.ngons_to_triangles(body)
    later(body, lambda o: paint_red(o, m, keep=("core", "red_dark")))
    return body


# --- The fins ---------------------------------------------------------------------------------------------------------
# Each fin: its frame's columns and rows (pixel edges: from its back end r0 to its front end r1).
FINS = [(14.0, 23.0, 11.0, 42.0), (26.0, 35.0, 5.0, 36.0), (38.0, 47.0, 1.0, 31.0)]
FIN_GAP = 0.25               # the fins narrower than their bays
FIN_FRONT, FIN_BACK = 8.9, 14.6   # the top's height at the front end and at the back end of the 31-row fin
FIN_THICK = 3.2
FIN_RIM = 0.95               # the frame's width round the panel
FIN_SINK = 0.3               # the panel under the frame's top
# The heat along a fin (rows from its front end): bands of the panel's materials.
FIN_BANDS = [(-9.0, "fin_dark"), (8.5, "fin_low"), (12.5, "fin"), (17.0, "fin_hot"), (27.6, "fin")]
FIN_SLATS = [(15.5, 1.0), (21.5, 0.55), (23.5, 1.0)]   # rows from the front end (their middles) and lengths
FIN_EDGE = (15.0, 27.0)      # the hot strip down the panel's left edge (rows from the front end)


def fin_top(r1):
    """The fin's top surface: FIN_FRONT at its front end r1, rising towards the back."""
    slope = (FIN_BACK - FIN_FRONT) / 31.0
    return lambda x, y: FIN_FRONT + slope * (y - Y(r1))


def fin(m, i):
    c0, c1, r0, r1 = FINS[i]
    top = fin_top(r1)
    bottom = lambda x, y: top(x, y) - FIN_THICK  # noqa: E731
    outline = rect(c0 + FIN_GAP, c1 - FIN_GAP, r0, r1)
    body = mk.prism(f"fin{i}", outline, -10.0, 40.0, m["frame"])
    mk.boolean(body, db.plane_box(f"fin{i}_top", top, size=120.0), "INTERSECT")
    mk.boolean(body, above_box(f"fin{i}_bottom", bottom), "INTERSECT")
    mk.cleanup(body)
    mk.bevel(body, 0.35, 2, 30.0)
    # The panel's recess.
    inner = rect(c0 + FIN_GAP + FIN_RIM, c1 - FIN_GAP - FIN_RIM, r0 + FIN_RIM, r1 - FIN_RIM)
    recess = mk.wedge(f"fin{i}_recess", inner, 0.0, lambda x, y: top(x, y) + 5.0,
                      m["frame"], bottom=lambda x, y: top(x, y) - FIN_SINK)
    mk.boolean(body, recess, "DIFFERENCE")
    mk.cleanup(body, dissolve=0.0)
    mk.shade(body, 35.0)
    later(body, lambda o: paint_frame(o, m))
    # The glowing panel in the recess, in bands of heat along the fin; the hot slats across it.
    panel = mk.wedge(f"fin{i}_panel", inner, 0.0, lambda x, y: top(x, y) - FIN_SINK + 0.02, m["fin"],
                     bottom=lambda x, y: top(x, y) - FIN_SINK - 0.6)
    mk.cleanup(panel)
    values = [r1 - (56.0 - v.co.y) for v in panel.data.vertices]
    band_split(panel, values, [(lo, m[name]) for lo, name in FIN_BANDS])
    parts = [body, panel]
    for j, (d, length) in enumerate(FIN_SLATS):
        rc = r1 - d
        a = c0 + FIN_GAP + FIN_RIM
        b = a + (c1 - c0 - 2 * (FIN_GAP + FIN_RIM)) * length
        slat = mk.wedge(f"fin{i}_slat{j}", rect(a, b, rc - 0.42, rc + 0.42), 0.0,
                        lambda x, y: top(x, y) - FIN_SINK + 0.3, m["fin_slat"],
                        bottom=lambda x, y: top(x, y) - FIN_SINK - 0.3)
        mk.bevel(slat, 0.12, 1, 30.0)
        k.smooth(slat, 40)
        parts.append(slat)
    return parts


def fin_edge(m, i, side):
    """The hot strip down the panel's left edge (lit from the upper left on both sides, where the slats of the right
    fins are the left ones' mirror image)."""
    c0, c1, r0, r1 = FINS[i]
    top = fin_top(r1)
    a = c0 + FIN_GAP + FIN_RIM if side > 0 else 145.0 - c1 + FIN_GAP + FIN_RIM
    d0, d1 = FIN_EDGE
    edge = mk.wedge(f"fin{i}_edge{'l' if side > 0 else 'r'}", rect(a, a + 0.75, r1 - d1, r1 - d0), 0.0,
                    lambda x, y: top(x, y) - FIN_SINK + 0.16, m["fin_slat"],
                    bottom=lambda x, y: top(x, y) - FIN_SINK - 0.3)
    mk.bevel(edge, 0.1, 1, 30.0)
    k.smooth(edge, 40)
    return edge


# --- The prow ---------------------------------------------------------------------------------------------------------
# The hood, its left half (mirrored): a cap over its back (a ridge along the seam, sloping to the back and the outer
# corner) and its front (a ridge along the half's middle, a facet falling outwards, one falling to the seam, one
# falling to the front's outer corner), the seam a slot between the halves.
DOME_CAP = [(72.5, 5.0), (67.0, 5.0), (64.6, 5.9), (62.6, 7.1), (61.0, 8.6), (61.0, 16.2), (72.5, 16.2)]
DOME_FRONT = [(72.5, 14.6), (61.0, 14.6), (61.0, 42.6), (72.5, 42.6)]
DOME_TOP = 12.6
DOME_SEAM = 0.45             # the seam's half-width
DOME_MID = 66.0              # the front's ridge (column edge)


CAP_TOP = 10.9              # the cap's ridge along the seam, under the front's back edge


def dome_cap_planes():
    return [lambda x, y: CAP_TOP + 0.2 * x,
            lambda x, y: CAP_TOP - 0.5 * (y - Y(15.0)),
            lambda x, y: CAP_TOP - 0.36 * ((y - Y(12.0)) + (-x - 4.5))]


def dome_front_planes():
    xm = X(DOME_MID)
    return [lambda x, y: DOME_TOP + 0.6 * (x - xm),
            lambda x, y: DOME_TOP - 0.26 * (x - xm),
            lambda x, y: DOME_TOP - 0.2 * ((Y(25.0) - y) + (-x - 3.0)),
            lambda x, y: DOME_TOP + 0.5 - 0.35 * (y - Y(15.5))]


def dome(m):
    """The hood's left half: the cap and the front, cut by their facets' planes, bevelled; clipped to the seam."""
    seam = X(72.5) - DOME_SEAM
    parts = []
    for name, path, planes in (("dome_cap", DOME_CAP, dome_cap_planes()), ("dome_front", DOME_FRONT,
                                                                           dome_front_planes())):
        outline = plan([(c if c < 72.0 else 72.5 - DOME_SEAM, r) for c, r in path], 1 if name == "dome_cap" else 0)
        body = plate(name, outline, planes, m["red"], bevel=0.4, segments=2, bottom=Z_HULL - 1.0)
        tb.ngons_to_triangles(body)
        later(body, lambda o: paint_red(o, m, lit_min=0.8, mid_min=0.6))
        parts.append(body)
    return parts


# --- The band, its bumpers and windows --------------------------------------------------------------------------------
BAND = (35.6, 56.8, 69.6, 1.0, 7.2)          # its outer end (left), rows, bottom, top
BAND_POWER = 5.0
BUMPER = (29.0, 37.6, 6.75, 3.45)             # its tip, its foot (columns), half-depth, half-height
WINDOWS = [(37.15, 47.85), (49.15, 59.85)]   # the frames' outer columns (left half)
WIN_ROWS = (57.5, 58.5, 66.4, 69.0)          # the frame's top, the interior's top and bottom, the sill's bottom
WIN_SIDE = 1.0
WIN_TOP = 7.9
WELL = 4.6                                    # the windows' floor in the band
# The windows' contents by frame: the shutter's lower edge (row; None: drawn up), the eye's middle row, radii and its
# bands of colour from its rim to its middle ((value, material): the value 1 at the rim, 0 at the middle).
EYES = {
    "closed": (None, 63.4, (2.4, 1.8, 0.9), [(-9.0, "lens")]),
    "shutter": (60.6, 63.6, (2.4, 1.8, 0.9), [(-9.0, "lens")]),
    "dim": (61.6, 63.9, (2.2, 1.35, 1.0), [(-9.0, "eye"), (0.55, "eye_dim")]),
    "lit": (62.6, 64.8, (3.1, 1.8, 1.45), [(-9.0, "eye_hot"), (0.35, "eye"), (0.75, "eye_dim")]),
    "hot": (62.6, 64.8, (3.1, 1.8, 1.45), [(-9.0, "eye_core"), (0.3, "eye_hot"), (0.7, "eye")]),
}
FRAMES = {232: "closed", 165: "shutter", 203: "dim", 241: "lit", 279: "hot",
          236: "closed", 167: "shutter", 205: "dim", 243: "lit", 281: "hot"}
EYE_X = [42.5, 54.5]                          # the eyes' middles (columns, left half)


def band_section(y0, y1, z0, z1, power, segments=40, scale=1.0):
    yc, zc, hy, hz = (y0 + y1) / 2, (z0 + z1) / 2, (y1 - y0) / 2 * scale, (z1 - z0) / 2 * scale
    pts = []
    for j in range(segments):
        u, v = mk.superellipse_point(2 * math.pi * j / segments, power)
        pts.append((yc + u * hy, zc + v * hz))
    return pts


def band(m):
    """The black bar across the machine (whole), the wells of its windows cut into it."""
    c, r0, r1, z0, z1 = BAND
    section = band_section(Y(r1), Y(r0), z0, z1, BAND_POWER)
    body = mk.prism("band", section, X(c), -X(c), m["band"], axis="x")
    mk.cleanup(body)
    cutters = []
    for side in (1, -1):
        for i, (a, b) in enumerate(WINDOWS):
            x0, x1 = sorted((side * X(a + WIN_SIDE), side * X(b - WIN_SIDE)))
            cutters.append(mk.box(f"well{i}{side}", x0, x1, Y(WIN_ROWS[2]), Y(WIN_ROWS[1]), WELL, 30.0, m["band"]))
    for cutter in cutters:
        mk.boolean(body, cutter, "DIFFERENCE")
    mk.cleanup(body, dissolve=0.0)
    tb.ngons_to_triangles(body)
    k.smooth(body, 40)
    mk.paint(body, lambda cc, n: m["band_lit"] if n.dot(LIGHT) > 0.86 else m["band"])
    return body


def bumper(m):
    """The grey bumper rounding the band's left end: its section swept from the band out to a rounded tip."""
    tip, foot, hy, hz = BUMPER
    _, r0, r1, z0, z1 = BAND
    yc, zc = (Y(r0) + Y(r1)) / 2, (z0 + z1) / 2
    length = X(foot) - X(tip)
    rings = []
    steps = 14
    for i in range(steps + 1):
        t = i / steps                       # 0 at the tip, 1 at the foot
        x = X(tip) + length * (1 - math.cos(t * math.pi / 2))
        s = math.sin(t * math.pi / 2) ** 0.85
        if i == 0:
            continue
        ring = []
        for j in range(36):
            u, v = mk.superellipse_point(2 * math.pi * j / 36, 3.2)
            ring.append(Vector((x, yc + u * hy * s, zc + v * hz * s)))
        rings.append(ring)
    rings.append([Vector((X(foot) + 0.6, p.y, p.z)) for p in rings[-1]])
    body = k.loft("bumper", rings, m["steel"], start_point=(X(tip), yc, zc), end_point=(X(foot) + 0.6, yc, zc))
    k.smooth(body, 60)
    return later(body, lambda o: k.smooth(tb.banded(o, LIGHT, [(-9.0, m["band"]), (0.1, m["steel_dark"]),
                                                               (0.62, m["steel"]), (0.93, m["steel_lit"])]), 60))


def window_frames(m):
    """The windows' grey frames on the band (left half): a top bar, the sides, a deep sill sloping to the front."""
    top, inner0, inner1, bottom = WIN_ROWS
    parts = []
    for i, (a, b) in enumerate(WINDOWS):
        outer = rect(a, b, top, bottom)
        hole = mk.prism(f"win_hole{i}", rect(a + WIN_SIDE, b - WIN_SIDE, inner0, inner1), WELL - 1.0, 30.0,
                        m["steel_dark"])
        body = plate(f"win_frame{i}", outer, [level(WIN_TOP), y_plane(66.9, WIN_TOP, bottom, 6.9)], m["steel"],
                     bevel=0.28, segments=2, bottom=5.0, cutters=[hole])
        tb.ngons_to_triangles(body)
        later(body, lambda o: paint_steel(o, m))
        parts.append(body)
    return parts


def window_contents(m, state, side=1):
    """The shutters and the eyes (lenses) of the windows of one side (1: left, -1: right) as a frame shows them;
    their objects are named win_<...>_<side>."""
    edge, row, (rx, ry, rz), bands = EYES[state]
    top, inner0, inner1, bottom = WIN_ROWS
    parts = []
    for i, (a, b) in enumerate(WINDOWS):
        tag = f"{i}{'l' if side > 0 else 'r'}"
        cx = X(EYE_X[i]) * side
        eye = k.ellipsoid(f"win_eye{tag}", (cx, Y(row), WELL + 0.05), (rx, ry, rz), m["lens"], 24, 12)
        values = [math.sqrt(((v.co.x - cx) / rx) ** 2 + ((v.co.y - Y(row)) / ry) ** 2 +
                            (max(0.0, WELL + rz - v.co.z) / (rz * 2.0)) ** 2) for v in eye.data.vertices]
        band_split(eye, values, [(lo, m[name]) for lo, name in bands])
        k.smooth(eye, 70)
        parts.append(eye)
        if edge is not None:
            x0, x1 = sorted((side * X(a + WIN_SIDE + 0.1), side * X(b - WIN_SIDE - 0.1)))
            slope = (7.55 - 6.5) / (edge - inner0)
            shutter_top = lambda x, y, s=slope: 7.55 - s * (Y(inner0) - y)  # noqa: E731
            body = mk.prism(f"win_shutter{tag}", [(x0, Y(edge)), (x1, Y(edge)), (x1, Y(inner0 - 0.4)),
                                                   (x0, Y(inner0 - 0.4))], 0.0, 30.0, m["steel"])
            mk.boolean(body, db.plane_box(f"win_shutter{tag}_top", shutter_top), "INTERSECT")
            mk.boolean(body, above_box(f"win_shutter{tag}_bottom", lambda x, y, f=shutter_top: f(x, y) - 1.1),
                       "INTERSECT")
            mk.cleanup(body)
            mk.bevel(body, 0.3, 2, 30.0)
            mk.shade(body, 35.0)
            # its face lit as the sprites draw it (a light grey lid), its edges darker
            mk.paint(body, lambda c, n: m["steel_lit"] if n.z > 0.75 else m["steel"] if n.dot(LIGHT) > 0.2 else
                     m["steel_dark"])
            parts.append(body)
    return parts


# --- The pit and its rods ---------------------------------------------------------------------------------------------
PIT_PLATE = (62.2, 67.0, 43.0, 53.0, 5.4)
RODS_X = 70.0                                 # the left rod's middle (column edge; mirrored)
# The rod down the pit: (row, radius) from under the prow's front to the gate's block; its axis height.
ROD = [(41.8, 1.9), (49.6, 1.9), (49.9, 2.45), (53.2, 2.45), (53.5, 1.9), (68.4, 1.9), (68.7, 2.3), (70.9, 2.3),
       (71.6, 2.0), (72.2, 1.2)]
ROD_Z = 7.3


def lathe_y(name, cx, cz, profile, mat, segments=24):
    """A round part along the screen: profile [(row, radius)] down it, its ends closed."""
    rings = []
    for r, rad in sorted(profile, key=lambda p: -p[0]):     # increasing y
        rings.append([Vector((cx + rad * math.cos(2 * math.pi * j / segments), Y(r),
                              cz + rad * math.sin(2 * math.pi * j / segments))) for j in range(segments)])
    first, last = sorted(profile, key=lambda p: -p[0])[0], sorted(profile, key=lambda p: -p[0])[-1]
    return k.loft(name, rings, mat, start_point=(cx, Y(first[0]), cz), end_point=(cx, Y(last[0]), cz))


def pit(m):
    c0, c1, r0, r1, z = PIT_PLATE
    plate_ = plate("pit_plate", rect(c0, c1, r0, r1), [level(z)], m["steel_dark"], bevel=0.3, segments=2,
                   bottom=Z_PIT - 0.5)
    later(plate_, lambda o: mk.paint(o, lambda c, n: m["steel"] if n.dot(LIGHT) > 0.8 else m["steel_dark"]))
    rod = lathe_y("rod", X(RODS_X), ROD_Z, ROD, m["steel"], 28)
    k.smooth(rod, 50)
    later(rod, lambda o: tb.banded(o, (-0.55, 0.35, 0.76), [(-9.0, m["steel_dark"]), (0.25, m["steel"]),
                                                          (0.8, m["steel_lit"])]))
    return [plate_, rod]


# --- The lower flanks, the pods, the gate's block ---------------------------------------------------------------------
LOWER = [(37.0, 69.6), (48.4, 69.6), (48.4, 97.2), (47.0, 96.8), (45.6, 95.2), (43.8, 92.8), (41.6, 89.8),
         (39.6, 86.2), (38.2, 82.6), (37.0, 79.0)]
LOWER_TOP = (69.6, 7.4, 97.2, 3.4)
LOWER_CHANNEL = (41.0, 45.0, 69.4, 91.0)
POD = [(48.8, 69.6), (60.2, 69.6), (60.2, 111.8), (57.0, 111.8), (49.0, 103.8)]
POD_TOP = 9.2
POD_NOSE = (99.0, POD_TOP, 112.0, 5.6)
POD_SLOT = (53.0, 58.2, 73.0, 104.6, 2.0)
PINK = [(74.2, 0.2), (74.5, 1.0), (75.2, 1.4), (76.0, 1.5), (102.0, 1.5), (102.8, 1.4), (103.5, 1.0), (103.8, 0.2)]
PINK_X = 55.6
BLOCK = [(72.5, 72.6), (61.1, 72.6), (61.1, 104.0), (72.5, 104.0)]
BLOCK_TOP = 8.2
LEDGE = (61.3, 73.0, 76.9, 8.9)              # its outer column, rows, top
DOOR = (64.6, 85.0, 2.8)                     # the doorway's outer column (mirrored), back row, floor
VENT = (61.8, 64.6, 77.6, 81.6, 0.6)
BARREL = [(88.6, 0.3), (88.8, 1.1), (89.4, 1.6), (90.2, 1.75), (104.2, 1.75)]
BARREL_X = 70.0


# The dark floor under the front (left half's path from the middle at the back to the middle at the front; its top),
# seen in the gaps between the lower flanks, the pods and the gate's block (the sprites' black lines).
FLOOR = [(72.5, 70.0), (37.6, 70.0), (37.6, 79.2), (39.0, 84.8), (41.4, 89.4), (44.0, 93.0), (47.4, 96.6),
         (49.4, 97.6), (49.4, 103.6), (72.5, 103.6)]
FLOOR_TOP = 3.0


def floor(m):
    body = mk.prism("floor", whole_plan(FLOOR), 0.0, FLOOR_TOP, m["core"])
    mk.cleanup(body)
    mk.shade(body, 35.0)
    return body


def lower(m):
    # The channel follows the sloping top: everything over the top lowered by its depth.
    groove = mk.prism("lower_ch", rect(*LOWER_CHANNEL), -5.0, 30.0, m["red_dark"])
    mk.boolean(groove, above_box("lower_ch_depth", lambda x, y: y_plane(*LOWER_TOP)(x, y) - 1.4), "INTERSECT")
    body = plate("lower", plan(LOWER, 1), [y_plane(*LOWER_TOP)], m["red"], bevel=0.45, segments=2, bottom=0.0,
                 cutters=[groove])
    tb.ngons_to_triangles(body)
    later(body, lambda o: paint_red(o, m, keep=("core", "red_dark")))
    return body


def pod(m):
    c0, c1, r0, r1, depth = POD_SLOT
    slot = mk.prism("pod_slot", plan([(c0, r0), (c1, r0), (c1, r1), (c0, r1)], 3), POD_TOP - depth, 30.0,
                    m["red_dark"])
    body = plate("pod", plan(POD, 1), [level(POD_TOP), y_plane(*POD_NOSE)], m["red"], bevel=1.0, segments=3,
                 bottom=0.0, cutters=[slot])
    tb.ngons_to_triangles(body)
    later(body, lambda o: paint_red(o, m, keep=("core", "red_dark")))
    rod = lathe_y("pink", X(PINK_X), POD_TOP - 1.55, PINK, m["rod"], 20)
    k.smooth(rod, 60)
    later(rod, lambda o: tb.banded(o, (-0.6, 0.3, 0.75), [(-9.0, m["rod"]), (0.72, m["rod_hot"])]))
    return [body, rod]


def block(m):
    """The gate's block (whole): its top, the ledge across its back, the vents, the doorway with two barrels."""
    c, r, floor = DOOR
    door = mk.box("door_cut", X(c), -X(c), Y(105.0), Y(r), floor, 30.0, m["red_dark"])
    c0, c1, r0, r1, d = VENT
    vents = [mk.box(f"vent{s}", *sorted((s * X(c0), s * X(c1))), Y(r1), Y(r0), BLOCK_TOP - d, 30.0, m["red_dark"])
             for s in (1, -1)]
    body = plate("block", whole_plan(BLOCK), [level(BLOCK_TOP)], m["red"], bevel=0.5, segments=2, bottom=0.0,
                 cutters=[door] + vents)
    tb.ngons_to_triangles(body)
    paint_red(body, m, keep=("core", "red_dark"))
    # the doorway's walls and floor dark
    mk.paint(body, lambda cc, n: m["red_dark"] if (abs(cc.x) < -X(c) + 0.05 and cc.y < Y(r) + 0.05 and
                                                   cc.z < BLOCK_TOP - 0.3) else None)
    oc, r0, r1, top = LEDGE
    ledge = plate("ledge", whole_plan([(72.5, r0), (oc, r0), (oc, r1), (72.5, r1)]), [level(top)], m["red"],
                  bevel=0.45, segments=2, bottom=BLOCK_TOP - 1.0)
    paint_red(ledge, m)
    parts = [body, ledge]
    for s in (1, -1):
        barrel = lathe_y(f"barrel{s}", s * X(BARREL_X), floor + 1.75, BARREL, m["red"], 20)
        k.smooth(barrel, 60)
        tb.banded(barrel, (-0.6, 0.35, 0.72), [(-9.0, m["red_dark"]), (0.2, m["red"]), (0.75, m["red_lit"])])
        parts.append(barrel)
    return parts


# --- Build ------------------------------------------------------------------------------------------------------------

def build_parts(m):
    """The whole parts and the left half's (mirrored about the middle); returns the meshes."""
    hull(m)
    before = set(mk.meshes())
    roll(m)
    deck(m)
    shelf(m)
    fender(m)
    for i in range(len(FINS)):
        fin(m, i)
    bumper(m)
    window_frames(m)
    pit(m)
    lower(m)
    pod(m)
    dome(m)
    mirror_half(sorted(set(mk.meshes()) - before, key=lambda o: o.name))
    for i in range(len(FINS)):
        for side in (1, -1):
            fin_edge(m, i, side)
    band(m)
    block(m)
    floor(m)
    for side in (1, -1):
        window_contents(m, "closed", side)
    return mk.meshes()


def set_windows(m, state, sides=(1, -1)):
    """The windows' contents (both sides, or one) as a frame shows them, replacing what was there."""
    for side in sides:
        tag = "l" if side > 0 else "r"
        for obj in [o for o in mk.meshes() if o.name.startswith(("win_eye", "win_shutter")) and o.name.endswith(tag)]:
            remove(obj)
        parts = window_contents(m, state, side)
        for obj in parts:
            mk.apply(obj)
            obj.data.transform(Matrix.Translation((AXIS_X, 0, 0)))
            obj.data.update()
    bpy.context.view_layer.update()


def cut(source, box_xy, cap_mat):
    """polish_arch.cut (the part of an object inside a box (x0, x1, y0, y1), its cuts capped with cap_mat, its normals
    the uncut object's) keeping the faces' own winding: the caps are turned to face out of their cut, and the faces
    are not recalculated (on a part whose cut could not be closed everywhere, a recalculation turned the deck's top
    over). None if nothing of the object is inside the box."""
    x0, x1, y0, y1 = box_xy
    corners = [source.matrix_world @ Vector(c) for c in source.bound_box]
    if (max(c.x for c in corners) <= x0 or min(c.x for c in corners) >= x1 or
            max(c.y for c in corners) <= y0 or min(c.y for c in corners) >= y1):
        return None
    obj = source.copy()
    obj.data = source.data.copy()
    bpy.context.scene.collection.objects.link(obj)
    cap_index = mk.slot_of(obj, cap_mat)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    caps = set()
    planes = (((x0, 0, 0), (-1, 0, 0)), ((x1, 0, 0), (1, 0, 0)), ((0, y0, 0), (0, -1, 0)), ((0, y1, 0), (0, 1, 0)))
    for co, no in planes:
        if not bm.faces:
            break
        result = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-6, plane_co=co,
                                        plane_no=no, clear_outer=True)
        edges = [e for e in result["geom_cut"] if isinstance(e, bmesh.types.BMEdge) and e.is_valid]
        open_edges = [e for e in edges if len(e.link_faces) == 1]
        if open_edges:
            filled = bmesh.ops.holes_fill(bm, edges=open_edges, sides=0)
            if filled["faces"]:
                faces = bmesh.ops.triangulate(bm, faces=filled["faces"])["faces"]
                for f in faces:
                    f.normal_update()
                    if f.normal.dot(Vector(no)) < 0:
                        f.normal_flip()
                caps |= set(faces)
    caps = {f for f in caps if f.is_valid}
    if not bm.faces:
        bm.free()
        bpy.data.objects.remove(obj)
        return None
    for f in caps:
        f.material_index = cap_index
        f.smooth = False
    bm.normal_update()
    bm.faces.index_update()
    cap_ids = {f.index for f in caps}
    bm.to_mesh(obj.data)
    bm.free()
    shading = mk.NormalSource(source)
    mesh = obj.data
    normals = []
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            n = None
            if poly.index not in cap_ids:
                n = shading.normal(mesh.vertices[mesh.loops[li].vertex_index].co, poly.center)
            normals.append(tuple(n if n is not None else poly.normal))
    mesh.normals_split_custom_set(normals)
    return obj


def export_pieces(whole, m, pieces, options, sheet=None, label="F"):
    """polish_deli_boss.export_pieces with this script's cut."""
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    for name, sprite, box in pieces:
        if only and name not in only:
            continue
        parts = [p for p in (cut(src, box, m["core"]) for src in whole) if p is not None]
        db.drop_unused(parts)
        mk.transform(parts, Matrix.Translation((-(box[0] + box[1]) / 2, -(box[2] + box[3]) / 2, 0)))
        bpy.context.view_layer.update()
        triangulate(parts)
        if "stats" in options:
            for obj in sorted(parts, key=lambda o: -mk.triangles([o]))[:12]:
                print("    %-22s %6d" % (obj.name, mk.triangles([obj])))
        parts = [db.join(parts, name)]
        parts[0].data.name = name        # (so the GLB is the same whichever pieces a run exports)
        for src in whole:
            src.hide_render = True
        if sheet:
            mk.compare("%s (%s %d)" % (name, label, sprite), mk.coverage(parts, 24, 28), k.sprite_mask(sheet, sprite))
        mk.report(name, parts, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, parts)
        for obj in parts:
            remove(obj)
        for src in whole:
            src.hide_render = False


def build_whole(m=None):
    m = m or materials()
    build_parts(m)
    whole = mk.meshes()
    for obj in whole:
        mk.apply(obj)
        obj.data.transform(Matrix.Translation((AXIS_X, 0, 0)))
        obj.data.update()
    bpy.context.view_layer.update()
    return [o for o in whole if len(o.data.polygons) > 0], m


def whole_mask(sheet, subst=None):
    """The twenty sprites' silhouettes placed as the levels place them: 144 x 112."""
    subst = subst or {}
    mask = [[False] * 144 for _ in range(112)]
    for name, sprite, col, row in CELLS:
        part = k.sprite_mask(sheet, subst.get(sprite, sprite))
        for y in range(28):
            for x in range(24):
                if part[y][x]:
                    mask[row + y][col + x] = True
    return mask


def build():
    k.reset()
    options = k.args()
    whole, m = build_whole()
    print("whole boss: %d triangles, %d objects" % (mk.triangles(whole), len(whole)))
    for obj in sorted(whole, key=lambda o: -mk.triangles([o]))[:16]:
        print("   %-22s %6d" % (obj.name, mk.triangles([obj])))
    sheet = os.path.join(options["check"], "enemy_F.png") if "check" in options else None
    if sheet:
        mk.compare("whole (F 153-163 / 191-201 / 230-238 / 270-274)", mk.coverage(whole, 144, 112), whole_mask(sheet))
    bpy.context.scene.view_settings.view_transform = "Standard"
    if "preview" in options:
        mk.preview(options["preview"] + "savara_boss_whole", whole, size=(144, 112), scale=6, distance=3.6)
    if "whole" in options:
        triangulate(whole)
        mk.export(whole, options["whole"])
    if options.get("only") != "none":
        export_pieces(whole, m, PIECES, options, sheet, label="F")
        export_frames(m, options, sheet)


# The window frames: (the piece's sprite and its windows' side, the frames after the first).
FRAME_PIECES = [(232, 1, (165, 203, 241, 279)), (236, -1, (167, 205, 243, 281))]


def export_frames(m, options, sheet):
    """232's and 236's pieces once more for each of their windows' other frames (models savara_boss_<frame>)."""
    only = options["only"].split(",") if "only" in options else None
    rest = {k_: v for k_, v in options.items() if k_ != "only"}
    boxes = {sprite: box for _, sprite, box in PIECES}
    for sprite, side, frames in FRAME_PIECES:
        for frame in frames:
            name = "savara_boss_%d" % frame
            set_windows(m, FRAMES[frame], (side,))
            if only and name not in only:
                continue
            parts = [o for o in mk.meshes() if len(o.data.polygons) > 0]
            export_pieces(parts, m, [(name, frame, boxes[sprite])], rest, sheet, label="F")
        set_windows(m, "closed", (side,))


if __name__ == "__main__":
    build()
