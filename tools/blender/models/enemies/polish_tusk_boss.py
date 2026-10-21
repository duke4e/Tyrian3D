"""The tusked boss of TYRIAN, TYRIAN X, HOLES and ASSASSIN (episodes 1 and 3; episode 6's DIG SITE and DEEP ICE take
TYRIAN X's and ASSASSIN's boss blocks), the game's first boss: sheet 4, twenty 2x2 sprites, each an enemy of its own
(46-65; all sky enemies), which the levels always place as one 120 x 112 picture and move together (TYRIAN's and TYRIAN
X's events at t 5300-5384, type 15: rows of five at x 90 + 24 i, 28 frames apart; HOLES at 2500 and 3300; ASSASSIN at
1900 with y offsets 0, -28, -56, -84): 10 12 14 16 18 / 48 50 [core] 54 56 / 86 88 90 92 94 / 124 126 128 130 132, the
core (sprite 1: enemy 53, in ASSASSIN enemy 1 itself) in the second row's gap. Polished 2026-10-21; it replaces
wave3_ab_boss.py's boss (a relief over the pixels painted pixel by pixel) and wave1_d.py's boss_chin (the jaw, 4 128,
built apart: here cut from the whole as tusk_boss_128). models.cfg: model tusk_boss_<sprite> enemies/
tusk_boss_<sprite>.glb origin (tusk_boss_core for sprite 1; tusk_boss_128 new); sprite 4 <sprite> <model> yaw=0
(sprite 4 128 and 4 280 tusk_boss_128). Its damaged look is polish_tusk_boss_dmg.py's, its small copy flying up
the screen polish_tusk_boss_small.py's, both built from this one.

The core is also enemy 1 on its own (MINEMAZE, MINES, TYRIAN, WINDY; GYGES; GAUNTLET, MACES), so its piece is a whole
part of the body: the barrel's foot, the red band, the glossy neck, the yoke's crossbar and the belly's top with the
mouth. Its animation (1 3 5 7 39 41 43 45, played when it fires; no other enemy, launched ones included, shows these
sprites) opens the mouth and charges the ball in it: frame models tusk_boss_core_3 ... _45 (frame 4 <sprite>
tusk_boss_core_<sprite>), the same piece with the lips parting (3, 5, 7: on a dull red lens), the mouth open (39) and
the ball charged, bigger and hotter (41, 43, 45: fire, its hot spot at the upper left), all with the same bounds.

The picture is its own mirror image about the middle of pixel column 60 (column c is column 120 - c; four pixels of
the outline and the light from the upper left differ): the left half is built and mirrored, the parts across the
middle are built whole. As the sprites and their 4x upscales draw it (the picture's columns and rows):
- Down the middle: a grey dome (rows 6-13) under a gold collar round its foot (rows 13-18), a tab over the collar's
  crown up onto the dome with a pink jewel at its top end; a dark band (rows 18-22) with a red lamp in it; the gold
  barrel (rows 22-34): a frame on its top with two grey windows and two studs at its top corners, bright rails down
  its shoulders (columns 51-54), big gold plates curving down over its flanks (columns 43-50 of rows 22-40); the red
  band round its foot (rows 33-38), a glossy black neck (rows 37-45); the gold yoke: the crossbar over the belly's
  top (rows 44-50, a gap in its middle) and its struts running down and out (to rows 57-72), each ending in a shield
  on the claw's arm, a red stud on each outer corner; the glossy black belly (rows 45-75), two lobes at its top
  either side of the mouth (rows 47-54), two red ribs either side on it with a gold panel between them (rows 54-68);
  the jaw: a grey cap (rows 73-80) over a grey wedge falling to its front (rows 75-92), spikes at its back corners,
  a red band down its ridge and gold (left) and brown (right) faces either side of it at its front.
- The wings: a gold plate from its tip (column 5 of row 20) down to the body, its leading edge rising to a bevel, a
  rib along its root (rows 35-38) and a lower plate under the rib (rows 38-52), sloping down outwards; a red pod on
  its tip with a dark block beside it; the engine (columns 19-45 of rows 3-23): a boxy grey housing angled down to
  the body, gold strips along it, a round cap on its upper end tilted to the camera (the sprite's tall ellipse), a
  grey pylon under its back down to the wing's rib; the gold cable from the cap looping round to the pod; red parts
  under the wing's root and the side plate (rows 39-44); a dark floor under it all.
- The claws (columns 14-46 of rows 57-107): a grey block with two red panels in light frames, its arm to the yoke's
  shield with a gold plate on it; the brown tusk from a grey sleeve under the block curving down and right to its
  point (column 37 of row 106), the grey hook curving down and right from under the arm (to column 45 of row 89).

Built as a CAD modeller would (polish_machine_kit: plates are prisms of their plan cut by the planes of their tops,
bevelled; booleans for the windows and the mouth), the round parts lofted (the hull, the collar, the neck, the belly
with its lobes, the red band, the engine's housing and cap), tapering horns along curved paths for the cable, the
tusks and the hooks (polish_twin_claw.horn), ribs, tabs and panels laid on the surfaces under them (riser). Each part
is painted by how its faces face the light from the upper left (gold, steel, red: a few shades each of the sprite's
own palette indices; the glossy black and the tusks in bands along smooth borders, polish_orb_red.band_split). The
glows (well under 1): the lamp and the jewel (0x49, 0x4e: 0.4-0.5), the ball (lens 0x43-0x4c: 0.12-0.28; fire 0x77,
0x7b, 0x7e: 0.4-0.6), the glossy black a little (0.1-0.12, so that it doesn't read as holes); the red pods and the
belly's ribs are plain red (the sprites draw them so). The whole boss is then cut along the sprites' edges
(polish_arch.cut: the pieces keep the whole's shading across the cuts, their cuts capped dark) into the twenty
pieces, each moved so that its sprite's centre is its origin; the faces of more than four corners that the booleans
cut into the curved lofts are split into triangles at once, every mesh is triangulated before the export
(polish_k_pod.triangulate), so the output is the same with and without --check; each piece's parts are joined into
one mesh. The pieces stand from z -3 to 16 (the body's axis at z 3.5; the sky layer at 0).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera. The whole's
origin is the picture's middle (pixel edge 60, 56: the middle of the edge between the core and 90): column c's left
edge is x = c - 60, row r's top edge y = 56 - r; the pieces' edges are x = -36, -12, 12, 36 and y = 28, 0, -28. Built
about X = x - 0.5 = 0 (the middle of column 60) and moved there at the end (AXIS_X).

Replaces wave3_ab_boss.py (all of it, with polish_tusk_boss_small.py: the boss and its small copy are all it builds;
wave3_ao_boss.py imports it, see polish_tusk_boss_dmg.py), wave3_ab_art.py's BOSS and CORE_45 (read only by
wave3_ab_boss.py) and wave1_d.py's boss_chin (its section "The chin of the tusked boss", its model registration and
its docstring line; models.cfg's model boss_chin): remove them so that they don't overwrite these models.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes of the whole
and of each piece and frame against enemy_4.png), --preview <prefix> (the whole's and each piece's top and 3/4
views), --only <model,...> (pieces and frames to export; "none": none), --whole <file.glb> (the uncut boss as well,
for looking at), --stats 1 (each piece's largest parts).
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
import polish_deli_boss as db  # noqa: E402  (its generic helpers: plates, mirroring, cutting, the pieces' export)
from polish_k_pod import triangulate  # noqa: E402
from polish_orb_red import band_split  # noqa: E402
from polish_twin_claw import horn  # noqa: E402

AXIS_X = 0.5                 # the middle of column 60, where the built boss's X = 0 goes
ZC = 3.5                     # the body's axis height

# The pieces: model, sprite, the picture's column and row of its top left corner (rows of five 24 apart, 28 apart).
LAYOUT = [[10, 12, 14, 16, 18], [48, 50, 1, 54, 56], [86, 88, 90, 92, 94], [124, 126, 128, 130, 132]]
NAMES = {1: "tusk_boss_core"}
CELLS = [(NAMES.get(s, "tusk_boss_%d" % s), s, 24 * j, 28 * i)
         for i, row in enumerate(LAYOUT) for j, s in enumerate(row)]


def box_of(col, row):
    """A piece's box in the whole's coordinates (x0, x1, y0, y1): the picture's pixel edge (60, 56) is the origin."""
    return (col - 60.0, col - 36.0, 28.0 - row, 56.0 - row)


PIECES = [(name, sprite, box_of(col, row)) for name, sprite, col, row in CELLS]


def X(c):
    """The left edge of the picture's column c (fractions allowed), in the built frame (X = 0: column 60's middle)."""
    return c - 60.5


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


def smoothstep(e0, e1, x):
    t = min(1.0, max(0.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


def lerp_table(table, v):
    """Linear interpolation in a table [(key, value...)] sorted by key (clamped at its ends)."""
    if v <= table[0][0]:
        return table[0][1:]
    for a, b in zip(table, table[1:]):
        if v <= b[0]:
            t = (v - a[0]) / (b[0] - a[0])
            return tuple(pa + (pb - pa) * t for pa, pb in zip(a[1:], b[1:]))
    return table[-1][1:]


def level(z):
    return lambda x, y: z + 0.0 * x


def x_plane(c0, z0, c1, z1):
    a0, a1 = X(c0), X(c1)
    return lambda x, y: z0 + (z1 - z0) * (x - a0) / (a1 - a0)


def y_plane(r0, z0, r1, z1):
    a0, a1 = Y(r0), Y(r1)
    return lambda x, y: z0 + (z1 - z0) * (y - a0) / (a1 - a0)


def line_plane(a, b, z0, slope, inside):
    """A plane z0 along the line through the pixel edges a and b, falling by slope per pixel away from it on the side
    away from the point inside (pixel edges), rising on the other."""
    ax, ay = P(*a)
    bx, by = P(*b)
    dx, dy = bx - ax, by - ay
    length = math.hypot(dx, dy)
    nx, ny = dy / length, -dx / length
    ix, iy = P(*inside)
    if nx * (ix - ax) + ny * (iy - ay) > 0:
        nx, ny = -nx, -ny
    return lambda x, y: z0 - slope * ((x - ax) * nx + (y - ay) * ny)


# --- Materials --------------------------------------------------------------------------------------------------------

def materials():
    pal = k.level_palette()

    def mat(name, index, metallic=0.5, roughness=0.4, glow=0.0, glow_index=None):
        if glow > 0:
            return k.material("tusk_" + name, palette=index, metallic=metallic, roughness=roughness,
                              emission=pal[index if glow_index is None else glow_index], emission_strength=glow)
        return k.material("tusk_" + name, palette=index, metallic=metallic, roughness=roughness)
    return {
        "core": mat("core", 0x01, 0.3, 0.7),
        # The glossy black of the neck and the belly, in bands of the sprite's light (a little light of its own so
        # that they don't read as holes from the slanted camera).
        "black": mat("black", 0x02, 0.45, 0.16, glow=0.1, glow_index=0x03),
        "black_mid": mat("black_mid", 0x04, 0.45, 0.14, glow=0.1, glow_index=0x05),
        "black_glare": mat("black_glare", 0x0b, 0.3, 0.1, glow=0.12, glow_index=0x0b),
        "steel_dark": mat("steel_dark", 0x04, 0.3, 0.48),
        "steel": mat("steel", 0x07, 0.32, 0.44),
        "steel_lit": mat("steel_lit", 0x0a, 0.32, 0.4),
        "steel_light": mat("steel_light", 0x0d, 0.3, 0.34),
        "gold_dark": mat("gold_dark", 0x16, 0.4, 0.4),
        "gold": mat("gold", 0x19, 0.42, 0.34),
        "gold_lit": mat("gold_lit", 0x1b, 0.42, 0.3),
        "gold_light": mat("gold_light", 0x1d, 0.4, 0.26),
        "brown": mat("brown", 0xa7, 0.3, 0.45),
        "brown_lit": mat("brown_lit", 0xaa, 0.3, 0.4),
        "red_dark": mat("red_dark", 0x45, 0.35, 0.4),
        "red": mat("red", 0x47, 0.35, 0.34),
        "red_lit": mat("red_lit", 0x4b, 0.3, 0.3),
        "lamp": mat("lamp", 0x49, 0.1, 0.25, glow=0.4),
        "lamp_hot": mat("lamp_hot", 0x4e, 0.1, 0.2, glow=0.5),
        # The ball in the mouth as the core's frames charge it: a dull red lens, then fire, hottest at its upper left.
        "lens_rim": mat("lens_rim", 0x43, 0.1, 0.3, glow=0.12),
        "lens": mat("lens", 0x47, 0.1, 0.25, glow=0.2),
        "lens_hot": mat("lens_hot", 0x4c, 0.1, 0.2, glow=0.28),
        "fire_rim": mat("fire_rim", 0x73, 0.0, 0.4, glow=0.3),
        "fire": mat("fire", 0x77, 0.0, 0.35, glow=0.4),
        "fire_hot": mat("fire_hot", 0x7b, 0.0, 0.3, glow=0.5),
        "fire_core": mat("fire_core", 0x7e, 0.0, 0.25, glow=0.6),
    }


# --- Helpers ----------------------------------------------------------------------------------------------------------

def plate(name, outline, planes, mat, bevel=0.45, segments=3, bottom=0.0, cutters=()):
    return db.plate(name, outline, planes, mat, bevel=bevel, segments=segments, bottom=bottom, cutters=cutters)


def paint_gold(obj, m, lit_dir=(-0.55, 0.45, 0.7), keep=("core",)):
    """Gold faces by how they face: tops gold, faces towards the light lit (the most light), the others dark."""
    keep_names = {m[n].name for n in keep}
    light = Vector(lit_dir).normalized()
    slots = {}
    mats = obj.data.materials
    for poly in obj.data.polygons:
        if mats[poly.material_index].name in keep_names:
            continue
        n = poly.normal
        d = n.dot(light)
        if d > 0.9:
            pick = "gold_light"
        elif d > 0.64:
            pick = "gold_lit"
        elif n.z > 0.3 or d > 0.2:
            pick = "gold"
        else:
            pick = "gold_dark"
        if pick not in slots:
            slots[pick] = mk.slot_of(obj, m[pick])
        poly.material_index = slots[pick]
    return obj


def paint_steel(obj, m, lit_dir=(-0.55, 0.45, 0.7), dark="steel_dark", base="steel", lit="steel_lit",
                light="steel_light", keep=("core",), light_min=0.92):
    keep_names = {m[n].name for n in keep}
    lv = Vector(lit_dir).normalized()
    slots = {}
    mats = obj.data.materials
    for poly in obj.data.polygons:
        if mats[poly.material_index].name in keep_names:
            continue
        n = poly.normal
        d = n.dot(lv)
        if light and d > light_min:
            pick = light
        elif d > 0.6:
            pick = lit
        elif n.z > 0.3 or d > 0.2:
            pick = base
        else:
            pick = dark
        if pick not in slots:
            slots[pick] = mk.slot_of(obj, m[pick])
        poly.material_index = slots[pick]
    return obj


def paint_mid(obj, m, lit_dir=(-0.55, 0.45, 0.7)):
    """Mid grey: tops steel, faces towards the light lit, the others dark."""
    return paint_steel(obj, m, lit_dir, dark="steel_dark", base="steel", lit="steel", light="steel_lit",
                       light_min=0.85)


def section_plan(name, section, outline, mat, y_range=(-80.0, 80.0), z_range=(-30.0, 40.0), bevel=0.4, segments=2):
    """A section (x, z) extruded along y, cut to a plan (x, y): fenders and shells; bevelled where the plan cut it."""
    body = mk.prism(name, section, y_range[0], y_range[1], mat, axis="y")
    clip = mk.prism(name + "_plan", outline, z_range[0], z_range[1], None)
    mk.boolean(body, clip, "INTERSECT")
    mk.cleanup(body)
    if bevel > 0:
        mk.bevel(body, bevel, segments, 30.0)
    mk.cleanup(body, dissolve=0.0)
    mk.shade(body, 35.0)
    return body


def super_ring(y, hw, z0, z1, power=2.4, segments=32, cx=0.0, top_fn=None):
    """A ring across y: a superellipse from z0 to z1, hw either side of cx; top_fn(x, z) may lower its upper half."""
    zc, hh = (z0 + z1) / 2, (z1 - z0) / 2
    ring = []
    for j in range(segments):
        a = 2 * math.pi * j / segments
        u, v = mk.superellipse_point(a, power)
        x, z = cx + u * hw, zc + v * hh
        if top_fn is not None and v > 0:
            z = top_fn(x, z, y)
        ring.append(Vector((x, y, z)))
    return ring


def loft_rows(name, stations, mat, power=2.4, segments=32, top_fn=None, tips=(0.0, 0.0)):
    """A body lofted down the screen through stations (row, half-width, bottom, top), its ends closed to points
    (tips: how far beyond the first and the last station, in rows)."""
    sts = sorted(stations, key=lambda s: -s[0])          # increasing y
    rings = [super_ring(Y(r), hw, z0, z1, power, segments, top_fn=top_fn) for r, hw, z0, z1 in sts]
    first, last = sts[0], sts[-1]
    return k.loft(name, rings, mat, start_point=(0.0, Y(first[0] + tips[1]), (first[2] + first[3]) / 2),
                  end_point=(0.0, Y(last[0] - tips[0]), (last[2] + last[3]) / 2))


def densify(points, step=0.8, closed=True):
    """A polygon's points with more points between them, at most step apart."""
    out = []
    n = len(points)
    for i in range(n if closed else n - 1):
        a, b = Vector(points[i]), Vector(points[(i + 1) % n])
        m = max(1, int(math.ceil((b - a).length / step)))
        out += [tuple(a.lerp(b, t / m)) for t in range(m)]
    if not closed:
        out.append(points[-1])
    return out


def riser(name, outline, hit, height, mat, sink=1.2, step=0.6, default=0.0):
    """A plan standing on a surface (hit: a ray cast down), its top height above it: ribs and fins laid on a body."""
    pts = densify(outline, step)

    def top(x, y):
        h = hit(x, y)
        return (h[0].z if h else default) + height

    def bottom(x, y):
        h = hit(x, y)
        return (h[0].z if h else default) - sink
    body = mk.wedge(name, pts, 0.0, top, mat, bottom=bottom)
    k.recalc_normals(body)
    return body


def remove(obj):
    data = obj.data
    bpy.data.objects.remove(obj)
    if data.users == 0:
        bpy.data.meshes.remove(data)


# --- The body down the middle -----------------------------------------------------------------------------------------
# The hull from the dome's front (row 5.8) down to the barrel's foot (row 37): stations (row, half-width, bottom, top).
HULL = [(6.1, 3.4, ZC - 1.2, ZC + 2.4), (6.6, 5.3, ZC - 2.0, ZC + 4.0),
        (7.3, 6.9, ZC - 2.8, ZC + 5.2), (8.2, 8.2, ZC - 3.4, ZC + 6.1), (9.3, 9.2, ZC - 3.9, ZC + 6.7),
        (10.6, 10.0, ZC - 4.3, ZC + 7.2), (12.0, 10.6, ZC - 4.6, ZC + 7.5), (13.5, 11.2, ZC - 4.9, ZC + 7.7),
        (15.0, 12.0, ZC - 5.2, ZC + 7.8), (16.8, 12.9, ZC - 5.5, ZC + 7.8), (18.4, 13.5, ZC - 5.7, ZC + 7.5),
        (20.4, 13.6, ZC - 5.7, ZC + 7.4), (22.4, 12.6, ZC - 5.5, ZC + 7.6), (23.4, 11.4, ZC - 5.2, ZC + 8.1),
        (25.0, 11.2, ZC - 5.0, ZC + 8.3), (31.0, 11.1, ZC - 5.0, ZC + 8.3), (33.4, 10.4, ZC - 4.8, ZC + 8.0),
        (35.4, 8.4, ZC - 4.0, ZC + 6.6), (37.0, 6.8, ZC - 3.6, ZC + 5.6)]
DOME_TO = 18.2               # the hull is the grey dome down to here (under the collar), then the dark band
BAND_TO = 22.6               # ... then the gold barrel
# The collar round the dome's foot: its top edge (row, how far out from the hull), its bottom edge; its crown's
# tab (columns, rows) and the jewel at its top end (column, row, radius).
COLLAR = (12.9, 18.5, 1.7)
TAB = (57.2, 63.8, 9.8, 15.2)
JEWEL = (60.5, 10.6, 0.95)
# The lamp in the band (column, row, radius) and its housing.
LAMP = (60.5, 21.4, 1.35)
# The barrel's top: the frame's windows (columns, rows) cut into it, how deep; the studs at its top corners.
WINDOWS = [((57.8, 63.2), (25.6, 27.6)), ((57.7, 63.3), (29.7, 33.6))]
WINDOW_DEPTH = 0.9
STUDS = [(57.0, 24.0, 0.7), (64.0, 24.0, 0.7)]
# The rails down the barrel's shoulders (left: column of their middle, rows, half-width) and the side plate (left:
# its section from the rail outwards, its plan).
RAIL = (52.6, 22.6, 35.0, 1.25)
SIDE_SECTION = [(-9.3, ZC + 7.3), (-10.6, ZC + 7.0), (-12.2, ZC + 6.2), (-13.8, ZC + 5.0), (-15.2, ZC + 3.4),
                (-16.4, ZC + 1.4), (-17.3, ZC - 0.8), (-17.4, ZC - 2.6), (-15.2, ZC - 2.6), (-14.6, ZC - 0.6),
                (-13.6, ZC + 1.6), (-12.2, ZC + 3.4), (-10.6, ZC + 4.6), (-9.3, ZC + 5.2)]
SIDE_PLAN = [(50.9, 21.8), (51.2, 38.0), (50.0, 39.6), (46.0, 40.4), (43.4, 39.2), (43.1, 27.0), (44.6, 24.6),
             (47.4, 22.6)]
# The red band round the barrel's foot (rows, half-width, top) and the glossy neck under it (stations).
RED_BAND = [(32.6, 7.8, ZC - 3.6, ZC + 6.8), (33.4, 8.4, ZC - 3.8, ZC + 7.5), (35.2, 8.2, ZC - 3.8, ZC + 7.4),
            (36.9, 7.4, ZC - 3.5, ZC + 6.7), (38.6, 6.2, ZC - 3.0, ZC + 5.4)]
NECK = [(36.8, 6.8, ZC - 3.4, ZC + 5.8), (38.4, 7.0, ZC - 3.4, ZC + 6.0), (40.5, 6.7, ZC - 3.3, ZC + 5.8),
        (42.6, 6.6, ZC - 3.3, ZC + 5.6), (44.4, 8.2, ZC - 3.6, ZC + 5.8), (46.0, 10.0, ZC - 4.0, ZC + 6.2)]
# The belly: stations (row, half-width, bottom, top); the groove between its lobes (rows, depth, half-width).
BELLY = [(44.6, 6.0, ZC - 2.6, ZC + 4.0), (45.6, 9.2, ZC - 3.8, ZC + 5.8), (47.0, 10.8, ZC - 4.4, ZC + 6.6),
         (49.0, 11.6, ZC - 4.8, ZC + 7.0), (52.0, 12.0, ZC - 5.0, ZC + 7.1), (56.0, 12.2, ZC - 5.0, ZC + 7.0),
         (60.0, 12.0, ZC - 4.9, ZC + 6.8), (64.0, 11.4, ZC - 4.7, ZC + 6.3), (67.5, 10.2, ZC - 4.2, ZC + 5.5),
         (70.4, 8.6, ZC - 3.6, ZC + 4.5), (72.6, 7.0, ZC - 3.0, ZC + 3.6), (74.2, 5.2, ZC - 2.4, ZC + 2.6),
         (75.0, 3.0, ZC - 1.8, ZC + 1.6)]
GROOVE = (45.0, 58.5, 1.3, 1.4)


def hull(m):
    """The dome, the band and the barrel: one loft, painted grey to the collar, dark in the band, gold below."""
    body = loft_rows("hull", HULL, m["steel"], power=2.5, segments=48, tips=(0.3, 0.0))
    k.smooth(body, 50)
    light = Vector((-0.45, 0.5, 0.75)).normalized()

    def pick(c, n):
        row = 56.0 - c.y
        d = n.dot(light)
        if row < DOME_TO:
            return m["steel_light"] if d > 0.9 else m["steel_lit"] if d > 0.6 else m["steel"] if d > 0.15 else \
                m["steel_dark"]
        if row < BAND_TO:
            return m["steel_dark"] if n.z > -0.2 else m["core"]
        return m["gold_light"] if d > 0.92 else m["gold_lit"] if d > 0.62 else m["gold"] if d > 0.2 else m["gold_dark"]
    mk.paint(body, pick)
    return body


def hull_hit():
    bpy.context.view_layer.update()
    return mk.surface([bpy.data.objects["hull"]])


def collar(m):
    """The gold collar round the dome's foot: a band standing out from the hull, its edges rounded; the tab over its
    crown (onto the dome's back), the jewel at the tab's top end."""
    r0, r1, out = COLLAR
    rows = [r0 + (r1 - r0) * i / 14 for i in range(15)]
    rings = []
    for i, r in enumerate(rows):
        hw, z0, z1 = lerp_table(HULL, r)
        t = i / 14
        f = min(1.0, math.sin(math.pi * min(1.0, t / 0.18) / 2), math.sin(math.pi * min(1.0, (1 - t) / 0.18) / 2))
        grow = out * (0.35 + 0.65 * f)
        zc = (z0 + z1) / 2
        rings.append(super_ring(Y(r), hw + grow, zc - (zc - z0) - grow * 0.6, z1 + grow, power=2.5, segments=48))
    body = k.loft("collar", rings[::-1], m["gold"])
    k.smooth(body, 55)
    paint_gold(body, m)
    # The tab: a plate laid on the collar's crown and the dome's back.
    hit = mk.surface([bpy.data.objects["hull"], body])
    c0, c1, ra, rb = TAB
    outline = plan([(c0, rb), (c1, rb), (c1, ra), (c0, ra)], 2)
    tab = riser("collar_tab", outline, hit, 1.15, m["gold"], sink=2.0, step=0.5)
    mk.bevel(tab, 0.3, 2, 30.0)
    k.smooth(tab, 40)
    paint_gold(tab, m)
    c, r, rad = JEWEL
    h = hit(X(c), Y(r))
    jz = (h[0].z if h else ZC + 8.0) + 1.15
    jewel = k.ellipsoid("jewel", (X(c), Y(r) - 0.1, jz), (rad, rad * 0.8, rad * 0.55), m["lamp"], 16, 8)
    k.smooth(jewel, 70)
    mk.paint(jewel, lambda cc, n: m["lamp_hot"] if n.dot(Vector((-0.4, 0.4, 0.8)).normalized()) > 0.85 else None)
    return body


def lamp(m):
    """The red lamp in the band under the collar, in a dark housing."""
    c, r, rad = LAMP
    hit = hull_hit()
    h = hit(X(c), Y(r))
    z = h[0].z if h else ZC + 7.4
    housing = mk.lathe("lamp_housing", [(rad + 0.9, z - 1.2), (rad + 0.9, z + 0.25), (rad + 0.6, z + 0.55),
                                         (rad + 0.15, z + 0.55), (rad + 0.15, z + 0.2)], (X(c), Y(r)),
                       m["steel_dark"], segments=24)
    k.smooth(housing, 40)
    body = k.ellipsoid("lamp", (X(c), Y(r), z + 0.3), (rad, rad, rad * 0.75), m["lamp"], 20, 10)
    k.smooth(body, 70)
    mk.paint(body, lambda cc, n: m["lamp_hot"] if n.dot(Vector((-0.45, 0.45, 0.77)).normalized()) > 0.86 else None)
    return body


def barrel_top(m):
    """The frame on the barrel's top: two windows cut into the hull (grey in them), the studs at its top corners."""
    body = bpy.data.objects["hull"]
    for i, ((c0, c1), (r0, r1)) in enumerate(WINDOWS):
        hit = hull_hit()
        top = min(hit(X(c), Y(r))[0].z for c in (c0, c1) for r in (r0, r1))
        cutter = mk.prism(f"window_cut{i}", plan([(c0, r0), (c1, r0), (c1, r1), (c0, r1)]), top - WINDOW_DEPTH, 30.0,
                          m["steel"])
        mk.boolean(body, cutter, "DIFFERENCE")
        mk.cleanup(body, dissolve=0.0)
    # The windows' floors and walls grey (lit at the back wall, dark at the front one).
    windows = [(X(c0), X(c1), Y(r1), Y(r0)) for (c0, c1), (r0, r1) in WINDOWS]

    def pick(c, n):
        for x0, x1, y0, y1 in windows:
            if x0 - 0.05 <= c.x <= x1 + 0.05 and y0 - 0.05 <= c.y <= y1 + 0.05:
                if n.z > 0.9:
                    return m["steel"]
                return m["steel_lit"] if n.y < -0.5 else m["black_mid"]
        return None
    mk.paint(body, pick)
    ngons_to_triangles(body)
    k.smooth(body, 50)
    hit = hull_hit()
    for i, (c, r, rad) in enumerate(STUDS):
        h = hit(X(c), Y(r))
        stud = k.ellipsoid(f"stud{i}", (X(c), Y(r), h[0].z + 0.1), (rad, rad, rad * 0.7), m["steel_lit"], 14, 7)
        k.smooth(stud, 70)
        mk.paint(stud, lambda cc, n: m["steel_light"] if n.dot(Vector((-0.4, 0.4, 0.8)).normalized()) > 0.8 else None)


def rails(m):
    """The bright rail down the barrel's left shoulder (mirrored): a bar laid on the hull."""
    c, r0, r1, hw = RAIL
    hit = hull_hit()
    pts, ups = [], []
    for i in range(25):
        r = r0 + (r1 - r0) * i / 24
        h = hit(X(c), Y(r))
        pts.append(h[0] + Vector((0, 0, -0.25)))
        ups.append(h[1])
    bar = mk.bar("rail", pts, ups, hw, 0.75, 0.6, m["steel_lit"], segments=12, power=3.0)
    k.smooth(bar, 50)
    paint_steel(bar, m, dark="steel", base="steel_lit", lit="steel_light", light=None)
    return bar


def side_plate(m):
    """The gold plate over the barrel's left flank: a curved shell from the rail out and down, cut to its plan."""
    body = section_plan("side_plate", SIDE_SECTION, plan(SIDE_PLAN, 2), m["gold"], bevel=0.45, segments=2)
    paint_gold(body, m)
    return body


def red_band(m):
    body = loft_rows("red_band", RED_BAND, m["red"], power=2.4, segments=40)
    k.smooth(body, 60)
    light = Vector((-0.45, 0.45, 0.77)).normalized()
    banded(body, (-0.45, 0.45, 0.77), [(-9.0, m["red"]), (0.55, m["red_lit"])])
    return body


def banded(obj, light, bands):
    """Faces in bands of the light (vertex normals against light), along smooth borders (polish_orb_red.band_split)."""
    lv = Vector(light).normalized()
    me = obj.data
    normals = [Vector() for _ in me.vertices]
    for poly in me.polygons:
        for vi in poly.vertices:
            normals[vi] += poly.normal * poly.area
    band_split(obj, [nv.normalized().dot(lv) if nv.length > 0 else 0.0 for nv in normals], bands)
    return obj


def glossy(obj, m, light=(-0.35, 0.45, 0.82), bands=(0.5, 0.86, 0.975)):
    """Glossy black in bands of the light: dark, base, a light band, a glare."""
    lv = Vector(light).normalized()
    values = []
    me = obj.data
    me.calc_loop_triangles()
    normals = [Vector() for _ in me.vertices]
    for poly in me.polygons:
        for vi in poly.vertices:
            normals[vi] += poly.normal * poly.area
    for nv in normals:
        values.append(nv.normalized().dot(lv) if nv.length > 0 else 0.0)
    band_split(obj, values, [(-9.0, m["core"]), (-0.2, m["black"]), (bands[0], m["black"]),
                             (bands[1], m["black_mid"]), (bands[2], m["black_glare"])])
    return obj


def neck(m):
    body = loft_rows("neck", NECK, m["black"], power=2.3, segments=40)
    k.smooth(body, 60)
    glossy(body, m)
    k.smooth(body, 60)
    return body


def belly_groove(x, z, y):
    r = 56.0 - y
    r0, r1, depth, hw = GROOVE
    f = smoothstep(r0, r0 + 2.0, r) * (1 - smoothstep(r1 - 3.0, r1, r))
    return z - depth * f * math.exp(-(x / hw) ** 2)


def smooth_stations(stations, step=1.0):
    """Stations (row, ...) resampled every step rows along a smooth curve through them (tyrkit.profile)."""
    by_y = sorted(((-r,) + tuple(rest) for r, *rest in stations))
    return [(-s[0],) + tuple(s[1:]) for s in k.profile(by_y, step)]


def ngons_to_triangles(obj):
    """Splits the faces of more than four corners (the booleans' cuts through curved lofts) into triangles, the
    same way every run, so that no later split folds them."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    faces = [f for f in bm.faces if len(f.verts) > 4]
    if faces:
        bmesh.ops.triangulate(bm, faces=faces, quad_method="BEAUTY", ngon_method="BEAUTY")
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    return obj


def belly(m):
    body = loft_rows("belly", smooth_stations(BELLY, 0.9), m["black"], power=2.3, segments=56, top_fn=belly_groove)
    k.smooth(body, 60)
    glossy(body, m)
    k.smooth(body, 60)
    return body


# The gold yoke (left): the crossbar's half over the neck and the strut from its outer end down to the claw, its foot
# a shield on the claw's arm; its top (level, then falling along the strut), the red stud on its outer corner.
YOKE = [(58.2, 43.8), (58.2, 46.6), (54.6, 49.6), (49.2, 50.2), (47.6, 51.4), (43.8, 55.4), (43.6, 56.6),
        (43.6, 63.4), (42.4, 65.4), (41.4, 68.4), (41.0, 71.0), (39.6, 72.0), (38.2, 71.4), (36.4, 67.6),
        (34.6, 64.8), (32.6, 61.8), (31.0, 59.4), (31.2, 57.8), (35.6, 56.6), (42.0, 50.4), (42.0, 45.6),
        (43.6, 44.2), (47.0, 43.8)]
YOKE_TOP, YOKE_FALL = ZC + 7.6, (50.0, ZC + 7.6, 64.0, ZC + 4.9)
YOKE_STUD = (45.4, 45.2, 0.8)
# The fins on the belly (left): the inner rib, the outer rib, the gold panel between them; how high they stand.
FIN_INNER = [(55.0, 57.0), (55.6, 54.8), (57.2, 53.6), (59.2, 53.8), (59.6, 55.2), (59.2, 66.6), (55.0, 66.8)]
FIN_OUTER = [(49.8, 58.6), (50.8, 57.0), (52.6, 56.6), (52.6, 67.6), (51.0, 67.8), (49.8, 64.4)]
FIN_PANEL = [(52.3, 58.0), (55.3, 57.2), (55.3, 66.9), (52.3, 67.3)]
FIN_H = (2.6, 2.3, 0.6)
# The mouth: the socket cut into the belly between its lobes (column of its middle, row, half-width, half-length,
# floor), the ball in it (row, height of its middle).
MOUTH = (60.5, 50.7, 4.9, 3.1, ZC + 2.9)
BALL = (50.8, ZC + 3.4)
# The jaw: the grey chin cap (column, row, half-width, half-length, bottom, top); the hull's left half (from the
# middle at its back to the middle at its front), its top at its back and its front, the V of its front faces (from
# a point, falling sideways), the red band down its middle (columns, rows, how high).
CHIN = (60.5, 76.4, 7.0, 3.9, ZC - 2.0, ZC + 4.6)
JAW = [(60.5, 76.6), (54.4, 76.6), (51.0, 75.6), (48.9, 74.9), (48.8, 77.6), (48.8, 83.4), (49.4, 85.8),
       (50.4, 87.0), (51.8, 88.4), (53.2, 89.6), (54.6, 90.6), (55.6, 91.6), (60.5, 92.2)]
JAW_TOP = (77.0, ZC + 3.4, 92.2, ZC - 0.6)
JAW_V = ((60.5, 79.4), (52.0, 90.4), ZC + 3.4, 0.55)
JAW_BAND = (58.7, 62.3, 78.4, 90.0, 0.45)
JAW_V_PLATE = [(57.0, 80.6), (58.7, 80.2), (58.7, 90.2), (55.2, 90.4), (52.8, 87.6), (52.9, 86.0)]


def yoke(m):
    """The gold yoke (left half): its plan cut by its top and the fall along the strut, bevelled."""
    planes = [level(YOKE_TOP), y_plane(*YOKE_FALL)]
    body = plate("yoke", plan(YOKE, 1), planes, m["gold"], bevel=0.6, segments=3, bottom=ZC + 1.0)
    paint_gold(body, m)
    c, r, rad = YOKE_STUD
    stud = k.ellipsoid("yoke_stud", (X(c), Y(r), YOKE_TOP + 0.05), (rad, rad, rad * 0.6), m["red"], 14, 7)
    k.smooth(stud, 70)
    mk.paint(stud, lambda cc, n: m["red_lit"] if n.dot(Vector((-0.4, 0.4, 0.8)).normalized()) > 0.8 else None)
    return body


def fins(m):
    """The red ribs on the belly's left (mirrored) with the gold panel between them."""
    bpy.context.view_layer.update()
    hit = mk.surface([bpy.data.objects["belly"]])
    parts = []
    for name, outline, h, mat in (("fin_inner", FIN_INNER, FIN_H[0], m["red"]), ("fin_outer", FIN_OUTER, FIN_H[1],
                                                                                   m["red"]),
                                  ("fin_panel", FIN_PANEL, FIN_H[2], m["gold"])):
        body = riser(name, plan(outline, 1), hit, h, mat, sink=1.6, step=0.5)
        mk.bevel(body, 0.22, 2, 30.0)
        k.smooth(body, 40)
        if mat is m["red"]:
            light = Vector((-0.5, 0.45, 0.74)).normalized()
            mk.paint(body, lambda c, n: m["red_lit"] if n.z > 0.6 or n.dot(light) > 0.45 else m["red"])
        else:
            mk.paint(body, lambda c, n: m["gold_dark"] if n.z > 0.5 else m["core"])
        parts.append(body)
    return parts


def mouth(m):
    """The socket cut into the belly between its lobes: its walls and floor dark. Returns the lips (the belly's top
    over the socket, as it was: left and right) and the ball's place."""
    c, r, hw, hl, floor = MOUTH
    belly_obj = bpy.data.objects["belly"]
    rings = []
    for z in (floor, 30.0):
        rings.append([Vector((X(c) + hw * math.cos(2 * math.pi * j / 40), Y(r) + hl * math.sin(2 * math.pi * j / 40),
                              z)) for j in range(40)])
    cutter = k.loft("mouth_cut", rings, m["core"])
    lips = belly_obj.copy()
    lips.data = belly_obj.data.copy()
    lips.name = "lips"
    bpy.context.scene.collection.objects.link(lips)
    keep = k.loft("mouth_keep", [[v + Vector((0, 0, 0)) for v in ring] for ring in rings], m["core"])
    mk.boolean(lips, keep, "INTERSECT")
    mk.cleanup(lips, dissolve=0.0)
    ngons_to_triangles(lips)
    k.smooth(lips, 60)
    mk.boolean(belly_obj, cutter, "DIFFERENCE")
    mk.cleanup(belly_obj, dissolve=0.0)
    ngons_to_triangles(belly_obj)
    k.smooth(belly_obj, 60)
    return lips


def jaw(m):
    """The jaw: a wedge falling to its front, its front faces a V either side of the ridge that the red band rides
    on; the grey chin cap over its back."""
    a, b, z0, slope = JAW_V
    v_left = line_plane(a, b, z0, slope, (40.0, 70.0))
    v_right = line_plane((121.0 - a[0], a[1]), (121.0 - b[0], b[1]), z0, slope, (81.0, 70.0))
    planes = [y_plane(*JAW_TOP), v_left, v_right]
    body = plate("jaw", whole_plan(JAW, 1), planes, m["steel"], bevel=0.4, segments=2, bottom=ZC - 2.4)
    light = Vector((-0.5, 0.45, 0.74)).normalized()

    def pick(cc, n):
        if n.z < -0.3:
            return m["core"]
        if n.dot(light) > 0.8:
            return m["steel_lit"]
        return m["steel"] if n.dot(light) > 0.3 else m["steel_dark"]
    mk.paint(body, pick)
    bpy.context.view_layer.update()
    hit = mk.surface([body])
    for name, outline, mat in (("jaw_v", JAW_V_PLATE, m["gold_lit"]),
                               ("jaw_v_r", [(121.0 - c, r) for c, r in JAW_V_PLATE], m["brown"])):
        v = riser(name, plan(outline, 1), hit, 0.22, mat, sink=0.8, step=0.5)
        k.smooth(v, 30)
    c0, c1, r0, r1, h = JAW_BAND
    band = riser("jaw_band", plan([(c0, r0), (c1, r0), (c1, r1), (c0, r1)], 1), hit, h, m["red"], sink=1.0, step=0.5)
    mk.bevel(band, 0.2, 2, 30.0)
    k.smooth(band, 40)
    mk.paint(band, lambda cc, n: m["red_lit"] if n.dot(light) > 0.75 else m["red"] if n.z > 0.4 else m["red_dark"])
    c, r, hw, hl, zb, zt = CHIN
    cap = mk.dome("chin", (X(c), Y(r)), (hw, hl, zt - zb), zb, m["steel"], segments=40, steps=10, power=2.3)
    paint_steel(cap, m, dark="steel", base="steel_lit", lit="steel_light", light=None)
    return body


# --- The wings, the engines, the claws (left; mirrored) ------------------------------------------------------------
# The wing: its upper plate (plan; top at the tip and at the root; the leading edge's chamfer), the rib along its root
# (plan, how high over the plate), the lower plate under the rib (plan, top).
WING = [(5.0, 19.4), (33.6, 33.7), (34.6, 34.6), (41.2, 34.6), (41.2, 38.3), (15.4, 38.3), (8.2, 37.8), (5.6, 35.8),
        (4.4, 22.0)]
WING_TOP = ((5.0, ZC + 0.7), (33.0, ZC + 4.6))
WING_EDGE = ((5.0, 19.4), (33.6, 33.7), ZC + 0.3, 0.85)
WING_RIB = ([(15.6, 35.0), (41.4, 35.0), (41.4, 38.5), (15.6, 38.5)], 0.7)
WING_LOW = ([(15.0, 37.6), (33.5, 37.6), (33.5, 50.6), (30.4, 52.5)], ((15.0, ZC + 1.6), (33.5, ZC + 4.0)))
# The red pod on the wing's tip (centre column, row; half-width, half-length; its foot and top), the grey block
# beside it (plan, top).
TIP_POD = (8.4, 31.3, 3.3, 6.0, ZC + 0.6, ZC + 4.0)
TIP_BLOCK = ([(10.6, 28.4), (14.8, 30.4), (14.8, 37.6), (10.6, 37.6)], ZC + 2.9)
# The cable from the engine's cap round to the pod (column, row, height), its radius.
CABLE = [(21.6, 9.6, ZC + 8.0), (18.2, 9.4, ZC + 7.6), (15.0, 9.8, ZC + 7.1), (12.4, 10.8, ZC + 6.5),
         (10.2, 12.3, ZC + 5.9), (8.6, 14.1, ZC + 5.3), (7.4, 16.1, ZC + 4.8), (6.6, 18.2, ZC + 4.4),
         (6.1, 20.3, ZC + 4.1), (6.0, 22.4, ZC + 3.9), (6.3, 24.4, ZC + 3.8), (7.0, 26.4, ZC + 3.6)]
CABLE_R = 1.45
# The engine: the housing's front middle (column, row), its direction in the plan (columns, rows per unit), length,
# half-width at its front and back, half-height, its axis height at its front and at its back; the cap over its
# front (its middle: column, row; the way its face looks in the plan: x, y; its radius, thickness, tilt up to the
# camera in degrees: the sprites draw it nearly upright, a tall narrow ellipse); the gold strips laid on it (column,
# row paths).
ENGINE = ((24.4, 11.0), (0.91, 0.414), 20.2, (7.2, 6.3), 4.2, ZC + 5.6, ZC + 4.6)
ENGINE_CAP = ((23.0, 10.2), (-0.99, 0.14), 7.0, 1.3, 21.0)
ENGINE_STRIPS = [[(25.0, 8.8), (31.0, 9.2), (31.6, 11.8), (40.4, 15.6)], [(26.6, 15.8), (34.0, 18.4), (40.8, 20.2)]]
# The pylon under the engine's back down to the wing's rib (plan, top), its lit rib (columns, rows).
PYLON = ([(29.6, 21.4), (37.4, 29.2), (37.4, 34.9), (43.6, 34.9), (43.6, 22.0), (42.4, 18.4), (33.0, 18.4)], ZC + 5.0)
PYLON_RIB = (40.6, 42.0, 20.8, 34.4)
# The dark floor under it all (left half's path from the middle at the back to the middle at the front; bottom, top).
FLOOR = [(60.5, 17.4), (44.2, 17.4), (40.0, 20.0), (33.2, 37.6), (32.4, 52.0), (30.6, 57.2), (36.0, 60.0),
         (43.6, 61.0), (48.6, 63.0), (51.6, 70.0), (55.0, 73.2), (60.5, 73.2)]
FLOOR_Z = (ZC - 3.0, ZC + 0.4)
# The red parts under the wing's root: a rounded block (column, row, half-width, half-length, top) and a bar (plan,
# top).
ROOT_KNOB = ([(37.6, 38.8), (44.6, 38.8), (44.6, 44.2), (37.6, 44.2)], ZC + 3.6)
ROOT_BAR = ([(44.6, 40.6), (53.8, 40.6), (53.8, 44.2), (44.6, 44.2)], ZC + 3.4)
# The claw: the block (plan, top), its red panels (plans) in light frames, the arm to the yoke's foot (plan, top),
# the gold plate on it (plan, top); the tusk's sleeve (rows, half-width), the tusk and the hook (column, row, height,
# half-width, half-height).
CLAW = ([(16.8, 56.6), (24.0, 56.6), (24.0, 80.2), (15.8, 80.2), (15.2, 72.0), (14.0, 70.0), (14.0, 59.8)], ZC + 4.8)
CLAW_PANELS = [[(15.9, 61.7), (21.9, 61.7), (21.9, 67.7), (15.9, 67.7)],
               [(17.7, 72.5), (21.7, 72.5), (21.7, 75.6), (19.7, 77.2), (17.7, 75.6)]]
CLAW_ARM = ([(23.0, 58.0), (30.6, 57.8), (36.8, 61.4), (39.0, 66.0), (41.8, 68.0), (41.8, 72.6), (36.0, 72.6),
             (34.4, 71.0), (31.6, 71.0), (30.0, 74.6), (28.6, 80.6), (23.6, 80.6)], ZC + 3.6)
CLAW_GOLD = ([(23.6, 67.8), (28.6, 67.8), (28.6, 74.0), (26.6, 75.6), (23.6, 75.6)], 0.55)
SLEEVE = (78.6, 86.6, 4.3)
TUSK = [(19.9, 78.6, ZC + 2.4, 3.9, 3.1), (19.9, 84.0, ZC + 2.2, 3.9, 3.0), (19.9, 89.0, ZC + 2.0, 3.9, 2.9),
        (20.4, 92.4, ZC + 1.8, 3.9, 2.8), (21.6, 95.4, ZC + 1.6, 3.8, 2.6), (23.2, 98.0, ZC + 1.4, 3.6, 2.4),
        (25.2, 100.3, ZC + 1.2, 3.3, 2.2), (27.4, 102.2, ZC + 1.0, 2.9, 1.9), (29.8, 103.8, ZC + 0.8, 2.4, 1.6),
        (32.4, 105.0, ZC + 0.6, 1.8, 1.2), (35.2, 105.9, ZC + 0.5, 1.0, 0.7), (38.2, 106.4, ZC + 0.4, 0.15, 0.15)]
HOOK = [(28.0, 76.0, ZC + 2.8, 2.3, 2.1), (28.8, 79.4, ZC + 2.6, 2.4, 2.1), (30.4, 82.4, ZC + 2.3, 2.4, 2.0),
        (32.6, 84.9, ZC + 2.0, 2.3, 1.8), (35.2, 86.8, ZC + 1.7, 2.0, 1.5), (38.2, 88.1, ZC + 1.4, 1.6, 1.2),
        (41.2, 88.9, ZC + 1.1, 1.1, 0.9), (43.6, 89.3, ZC + 0.9, 0.6, 0.5), (45.4, 89.6, ZC + 0.8, 0.12, 0.1)]


def wing(m):
    """The gold wing: the upper plate rising to its root, its leading edge chamfered; the rib along its root; the
    lower plate under the rib, a step lower."""
    (c0, z0), (c1, z1) = WING_TOP
    a, b, ze, slope = WING_EDGE
    planes = [x_plane(c0, z0, c1, z1), line_plane(a, b, ze, slope, (20.0, 36.0))]
    upper = plate("wing", plan(WING, 1), planes, m["gold"], bevel=0.4, segments=2, bottom=ZC - 1.2)
    paint_gold(upper, m)
    outline, rise = WING_RIB
    rib = plate("wing_rib", plan(outline), [lambda x, y: x_plane(c0, z0, c1, z1)(x, y) + rise], m["gold"], bevel=0.35,
                segments=2, bottom=ZC - 0.5)
    paint_gold(rib, m)
    outline, ((l0, h0), (l1, h1)) = WING_LOW
    low = plate("wing_low", plan(outline, 1), [x_plane(l0, h0, l1, h1)], m["gold"], bevel=0.4, segments=2,
                bottom=ZC - 1.4)
    paint_gold(low, m)
    return [upper, rib, low]


def wing_tip(m):
    c, r, hw, hl, z0, z1 = TIP_POD
    pod = mk.dome("tip_pod", P(c, r), (hw, hl, z1 - z0), z0, m["red"], segments=36, steps=10, power=2.8)
    light = Vector((-0.55, 0.4, 0.73)).normalized()
    mk.paint(pod, lambda cc, n: m["red_lit"] if n.dot(light) > 0.8 else m["red"] if n.dot(light) > 0.25 else
             m["red_dark"])
    outline, top = TIP_BLOCK
    block = plate("tip_block", plan(outline, 1), [level(top)], m["steel_dark"], bevel=0.4, segments=2, bottom=ZC - 0.5)
    paint_steel(block, m, dark="steel_dark", base="steel_dark", lit="steel", light=None)
    return [pod, block]


def cable(m):
    controls = [(X(c), Y(r), z, CABLE_R, CABLE_R) for c, r, z in CABLE]
    body, centres = horn("cable", controls, m["gold"], segments=14, iterations=2)
    paint_gold(body, m, lit_dir=(-0.5, 0.5, 0.7))
    return body


def engine_frame():
    (c, r), (dc, dr), length, hw, hh, z_cap, z_back = ENGINE
    origin = Vector((X(c), Y(r), z_cap))
    along = Vector((dc, -dr, (z_back - z_cap) / length)).normalized()
    across = Vector((-along.y, along.x, 0.0)).normalized()
    up = across.cross(along).normalized()
    if up.z < 0:
        up = -up
    return origin, along, across, up


def engine(m):
    """The engine: a boxy housing along its tilted axis, its back rounded; the cap on its front end (a disc tilted
    up to the camera, a dark ring round its lit face); the gold strips laid on it; the pylon under its back."""
    (c, r), _, length, (hw0, hw1), hh, z_cap, z_back = ENGINE
    origin, along, across, up = engine_frame()
    rings = []
    stations = [(0.0, 0.94), (0.6, 1.0), (length - 2.6, 1.0), (length - 1.4, 0.94), (length - 0.6, 0.8),
                (length - 0.15, 0.55)]
    for s, f in stations:
        hw = hw0 + (hw1 - hw0) * s / length
        ring = []
        for j in range(48):
            u, v = mk.superellipse_point(2 * math.pi * j / 48, 7.0)
            ring.append(origin + along * s + across * (u * hw * f) + up * (v * hh * f))
        rings.append(ring)
    body = k.loft("engine", rings, m["steel"], start_point=origin + along * -0.05,
                  end_point=origin + along * (length + 0.05))
    k.smooth(body, 40)
    lv = Vector((-0.55, 0.45, 0.7)).normalized()
    mk.paint(body, lambda cc, n: m["steel_lit"] if n.dot(lv) > 0.88 else m["steel"] if n.z > 0.75 or
             n.dot(lv) > 0.45 else m["steel_dark"])
    (cc_, rc_), (nx, ny), rad, thick, tilt = ENGINE_CAP
    t = math.radians(tilt)
    flat = Vector((nx, ny, 0.0)).normalized()
    normal = (flat * math.cos(t) + Vector((0, 0, 1)) * math.sin(t)).normalized()
    side = Vector((-flat.y, flat.x, 0.0))
    upv = normal.cross(side).normalized()
    centre = Vector((X(cc_), Y(rc_), z_cap + 0.2))
    profile = [(-0.2, 0.0), (-0.2, rad - 0.5), (0.1, rad), (thick - 0.3, rad), (thick, rad - 0.4),
               (thick, rad - 1.3), (thick - 0.45, rad - 1.7), (thick - 0.45, 0.0)]
    rings = []
    for d, rr in profile:
        rings.append([centre + normal * d + side * (math.cos(2 * math.pi * j / 40) * max(rr, 0.01)) +
                      upv * (math.sin(2 * math.pi * j / 40) * max(rr, 0.01)) for j in range(40)])
    cap = k.loft("engine_cap", rings, m["steel_lit"], start_point=centre + normal * -0.2,
                 end_point=centre + normal * (thick - 0.45))
    k.smooth(cap, 40)
    light = Vector((-0.6, 0.45, 0.66)).normalized()

    def pick(cc, n):
        d = (cc - centre).dot(normal)
        rr = ((cc - centre) - normal * d).length
        if d > thick - 0.5 and rr < rad - 1.6:
            return m["steel_light"] if n.dot(light) > 0.75 else m["steel_lit"]
        if d > thick - 0.5 and rr < rad - 0.5:
            return m["steel_dark"]
        return m["steel_light"] if n.dot(light) > 0.85 else m["steel_lit"] if n.dot(light) > 0.4 else m["steel"]
    mk.paint(cap, pick)
    bpy.context.view_layer.update()
    hit = mk.surface([body])
    for i, path in enumerate(ENGINE_STRIPS):
        pts, ups = [], []
        dense = densify([P(cc, rr) for cc, rr in path], 0.6, closed=False)
        for x, y in dense:
            h = hit(x, y)
            if h is None:
                continue
            pts.append(h[0] - Vector((0, 0, 0.15)))
            ups.append(h[1])
        strip = mk.bar(f"engine_strip{i}", pts, ups, 0.7, 0.45, 0.3, m["gold"], segments=8, power=3.0)
        k.smooth(strip, 50)
        paint_gold(strip, m)
    outline, top = PYLON
    pylon = plate("pylon", plan(outline, 1), [level(top)], m["steel"], bevel=0.5, segments=2, bottom=ZC - 1.5)
    paint_steel(pylon, m)
    c0, c1, r0, r1 = PYLON_RIB
    rib = plate("pylon_rib", plan([(c0, r0), (c1, r0), (c1, r1), (c0, r1)]), [level(top + 0.5)], m["steel_lit"],
                bevel=0.3, segments=2, bottom=top - 1.0)
    paint_steel(rib, m, dark="steel", base="steel_lit", lit="steel_light", light=None)
    return [body, cap, pylon, rib]


def root_parts(m):
    outline, top = ROOT_KNOB
    light = Vector((-0.5, 0.45, 0.74)).normalized()
    knob = plate("root_knob", plan(outline, 2), [level(top)], m["red"], bevel=0.9, segments=3, bottom=ZC - 1.0)
    mk.paint(knob, lambda cc, n: m["red_lit"] if n.dot(light) > 0.82 else m["red"] if n.dot(light) > 0.3 else
             m["red_dark"])
    outline, top = ROOT_BAR
    bar = plate("root_bar", plan(outline, 1), [level(top)], m["red"], bevel=0.4, segments=2, bottom=ZC - 1.0)
    mk.paint(bar, lambda cc, n: m["red_lit"] if n.dot(light) > 0.6 else m["red"])
    return [knob, bar]


def claw(m):
    """The claw: a grey block, its red panels in light frames; the arm from it to the yoke's foot, the gold plate on
    it; the tusk in its sleeve under the block; the hook curving down from under the arm."""
    outline, top = CLAW
    light = Vector((-0.5, 0.45, 0.74)).normalized()
    block = plate("claw", plan(outline, 1), [level(top)], m["steel"], bevel=0.6, segments=3, bottom=ZC - 1.6)
    paint_mid(block, m)
    parts = [block]
    for i, panel in enumerate(CLAW_PANELS):
        pts = plan(panel)
        frame = plate(f"claw_frame{i}", mk.chaikin(grow(pts, 0.55), 2), [level(top + 0.3)], m["steel_light"],
                      bevel=0.25, segments=2, bottom=top - 1.0)
        paint_steel(frame, m, dark="steel_lit", base="steel_light", lit="steel_light", light=None)
        red = plate(f"claw_panel{i}", mk.chaikin(pts, 2), [level(top + 0.55)], m["red"], bevel=0.3, segments=2,
                    bottom=top - 0.6)
        mk.paint(red, lambda cc, n: m["red_lit"] if n.dot(light) > 0.8 else m["red"] if n.z > 0.5 else m["red_dark"])
        parts += [frame, red]
    outline, top = CLAW_ARM
    arm = plate("claw_arm", plan(outline, 1), [level(top)], m["steel"], bevel=0.5, segments=2, bottom=ZC - 1.4)
    paint_mid(arm, m)
    outline, rise = CLAW_GOLD
    gold = plate("claw_gold", plan(outline, 1), [level(top + rise)], m["gold"], bevel=0.3, segments=2, bottom=top - 1.0)
    paint_gold(gold, m)
    r0, r1, hw = SLEEVE
    c = TUSK[0][0]
    rings = []
    for r, f in ((r0, 0.9), (r0 + 0.5, 1.0), (r1 - 0.6, 1.0), (r1, 0.88)):
        rings.append(super_ring(Y(r), hw * f, ZC - 1.4, ZC + 2.4 + 2.4 * f, power=2.6, segments=28, cx=X(c)))
    sleeve = k.loft("sleeve", rings, m["steel"])
    k.smooth(sleeve, 50)
    paint_mid(sleeve, m)
    tusk, centres = horn("tusk", [(X(c), Y(r), z, hw_, hh) for c, r, z, hw_, hh in TUSK], m["brown"], segments=18)
    banded(tusk, (-0.6, 0.3, 0.75), [(-9.0, m["brown"]), (0.72, m["brown_lit"])])
    hook, centres = horn("hook", [(X(c), Y(r), z, hw_, hh) for c, r, z, hw_, hh in HOOK], m["steel"], segments=16)
    banded(hook, (-0.6, 0.35, 0.72), [(-9.0, m["steel_dark"]), (0.35, m["steel"]), (0.8, m["steel_lit"]),
                                       (0.95, m["steel_light"])])
    return parts + [arm, gold, sleeve, tusk, hook]


def grow(pts, d):
    """A convex-ish polygon grown outwards by d (each point pushed away from the centre along its corner's bisector)."""
    n = len(pts)
    out = []
    for i in range(n):
        p0, p1, p2 = Vector(pts[i - 1]), Vector(pts[i]), Vector(pts[(i + 1) % n])
        e0 = (p1 - p0).normalized()
        e1 = (p2 - p1).normalized()
        n0 = Vector((e0.y, -e0.x))
        n1 = Vector((e1.y, -e1.x))
        bis = (n0 + n1)
        if bis.length < 1e-6:
            bis = n0
        bis.normalize()
        cosang = max(0.3, bis.dot(n0))
        out.append(tuple(p1 + bis * (d / cosang)))
    return out


def floor_plate(m):
    body = mk.prism("floor", whole_plan(FLOOR, 1), FLOOR_Z[0], FLOOR_Z[1], m["steel_dark"])
    mk.cleanup(body)
    mk.bevel(body, 0.4, 2, 30.0)
    mk.shade(body, 35.0)
    mk.paint(body, lambda c, n: m["black_mid"] if n.z > 0.3 else m["core"])
    return body


# --- The mouth's frames -----------------------------------------------------------------------------------------------
# The core's frames (sprite: how far the lips are still closed, the ball's radius, its bands of colour from its rim
# to its hot spot: (value, material), the value 0 at the hot spot rising to 1 at its rim): 1 closed; 3, 5 and 7 the
# lips parting on a dull red lens; 39 the mouth open on it; 41, 43 and 45 the ball charged, bigger and hotter.
MOUTH_FRAMES = [
    (1, 1.0, 2.2, [(-9.0, "core")]),
    (3, 0.88, 2.3, [(-9.0, "lens_hot"), (0.45, "lens"), (0.9, "core")]),
    (5, 0.68, 2.4, [(-9.0, "lens_hot"), (0.4, "lens"), (0.9, "core")]),
    (7, 0.52, 2.6, [(-9.0, "fire_hot"), (0.18, "lens_hot"), (0.45, "lens"), (0.9, "core")]),
    (39, 0.06, 2.8, [(-9.0, "lens_hot"), (0.35, "lens"), (0.85, "lens_rim")]),
    (41, 0.06, 3.0, [(-9.0, "fire_core"), (0.12, "fire_hot"), (0.4, "fire")]),
    (43, 0.06, 3.3, [(-9.0, "fire_core"), (0.2, "fire_hot"), (0.55, "fire")]),
    (45, 0.06, 3.5, [(-9.0, "fire_core"), (0.3, "fire_hot"), (0.65, "fire")]),
]
BALL_HOT = (59.6, 50.2)          # its hot spot (column, row): at the upper left, as the sprites draw it


def split_lips(m):
    """The lips (the belly's top over the socket, as it was) cut down the middle into a left and a right half."""
    lips = bpy.data.objects["lips"]
    left = db.cut(lips, (-60.0, 0.0, -60.0, 60.0), m["core"])
    right = db.cut(lips, (0.0, 60.0, -60.0, 60.0), m["core"])
    remove(lips)
    left.name, right.name = "lips_l", "lips_r"
    for obj in (left, right):
        obj.data.name = obj.name
    return left, right


def ball(m, frame, shift=0.0):
    """The ball in the socket for a frame (moved shift along x, onto the picture's axis)."""
    _, _, radius, bands = frame
    c, r, hw, hl, floor = MOUTH
    row, z = BALL
    body = k.ellipsoid("mouth_ball", (X(c) + shift, Y(row), z), (radius, radius * 0.85, radius * 0.8), m["core"], 28,
                       14)
    hx, hy = X(BALL_HOT[0]) + shift, Y(BALL_HOT[1])
    values = []
    for v in body.data.vertices:
        top = max(0.0, (v.co.z - z) / (radius * 0.8))
        values.append(math.hypot((v.co.x - hx) / radius, (v.co.y - hy) / (radius * 0.85)) * 0.8 + 0.25 * (1 - top))
    band_split(body, values, [(lo, m[name]) for lo, name in bands])
    k.smooth(body, 70)
    return body


def set_mouth(m, frame, shift=AXIS_X, saved=None):
    """The lips and the ball as a frame shows them: each lip pressed towards its outer edge (scaled in x about it) as
    far as the frame has it closed; the ball replaced. saved: the lips' vertices as built (for the frames after the
    first)."""
    _, closed, _, _ = frame
    hw = MOUTH[2]
    for name, edge in (("lips_l", -hw), ("lips_r", hw)):
        obj = bpy.data.objects[name]
        base = saved[name]
        for v, co in zip(obj.data.vertices, base):
            x = co.x - shift
            v.co = Vector((shift + edge + (x - edge) * closed, co.y, co.z))
        obj.data.update()
    if "mouth_ball" in bpy.data.objects:
        remove(bpy.data.objects["mouth_ball"])
    ball(m, frame, shift)
    bpy.context.view_layer.update()


# --- Build ------------------------------------------------------------------------------------------------------------

def build_parts(m):
    """The whole parts and the left half's (mirrored about the middle); returns the meshes."""
    hull(m)
    collar(m)
    lamp(m)
    barrel_top(m)
    red_band(m)
    neck(m)
    belly(m)
    before = set(mk.meshes())
    rails(m)
    side_plate(m)
    yoke(m)
    fins(m)
    wing(m)
    wing_tip(m)
    cable(m)
    engine(m)
    root_parts(m)
    claw(m)
    db.mirror_half(sorted(set(mk.meshes()) - before, key=lambda o: o.name))
    floor_plate(m)
    jaw(m)
    mouth(m)
    split_lips(m)
    ball(m, MOUTH_FRAMES[0])
    return mk.meshes()


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


def whole_mask(sheet, layout=None):
    """The twenty sprites' silhouettes placed as the levels place them: 120 x 112."""
    mask = [[False] * 120 for _ in range(112)]
    for i, row in enumerate(layout or LAYOUT):
        for j, sprite in enumerate(row):
            if not sprite:
                continue
            part = k.sprite_mask(sheet, sprite)
            for y in range(28):
                for x in range(24):
                    if part[y][x]:
                        mask[28 * i + y][24 * j + x] = True
    return mask


def build():
    k.reset()
    options = k.args()
    whole, m = build_whole()
    print("whole boss: %d triangles, %d objects" % (mk.triangles(whole), len(whole)))
    for obj in sorted(whole, key=lambda o: -mk.triangles([o]))[:16]:
        print("   %-22s %6d" % (obj.name, mk.triangles([obj])))
    sheet = os.path.join(options["check"], "enemy_4.png") if "check" in options else None
    if sheet:
        mk.compare("whole (4 10-18 / 48 50 1 54 56 / 86-94 / 124-132)", mk.coverage(whole, 120, 112), whole_mask(sheet))
    bpy.context.scene.view_settings.view_transform = "Standard"
    if "preview" in options:
        mk.preview(options["preview"] + "tusk_boss_whole", whole, size=(120, 112), scale=8, distance=3.2)
    if "whole" in options:
        triangulate(whole)
        mk.export(whole, options["whole"])
    if options.get("only") != "none":
        db.export_pieces(whole, m, PIECES, options, sheet, label="4")
        export_frames(whole, m, options, sheet)


def export_frames(whole, m, options, sheet):
    """The core's piece once more for each of its other frames (models tusk_boss_core_<sprite>)."""
    only = options["only"].split(",") if "only" in options else None
    saved = {n: [v.co.copy() for v in bpy.data.objects[n].data.vertices] for n in ("lips_l", "lips_r")}
    box = box_of(48, 28)
    for frame in MOUTH_FRAMES[1:]:
        name = "tusk_boss_core_%d" % frame[0]
        if only and name not in only:
            continue
        set_mouth(m, frame, AXIS_X, saved)
        parts = [o for o in mk.meshes() if len(o.data.polygons) > 0]
        db.export_pieces(parts, m, [(name, frame[0], box)], {k_: v for k_, v in options.items() if k_ != "only"},
                         sheet, label="4")


if __name__ == "__main__":
    build()
