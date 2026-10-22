"""SURFACE's two lamp blocks, the stone sledges its plank turrets stand on (sheet 3: 84 beside 86 and 122 beside 124,
2x2 each; enemies 206, 207 and 203, 204 of episode 4, ground layer, armour 20; one frame each), polished (2026-10-22,
round 31; they replace wave3_n.py's lamp_block(), a pillow inflated from the sprites' outline with a square, two ribs
and two tubes for lamps). models.cfg: model lamp_block_84 / lamp_block_86 / lamp_block_122 / lamp_block_124
enemies/lamp_block_*.glb origin (unchanged); sprite 3 84 lamp_block_84 yaw=0 height=-4, the same for 86, 122 and 124;
and the turret on them: sprite 3 12 plank_turret yaw=aim height=TURRET_HEIGHT (see below).

How SURFACE uses them (its events, tools/content/tyrevents.py): every block is two pieces side by side, 206 (84) at x
and 207 (86) at x + 24 (10 times) or 203 (122) at x and 204 (124) at x + 24 (11 times), one link, and every block
carries a plank turret (enemy 205, polish_plank_turret.py): the event that makes a block makes the turret too, at x + 16
(on 84/86) or x + 9 (on 122/124) and 3 pixels up the screen, on a link one lower: right on the square on the block's
top (its middle is 4 pixels right of the block's, 122/124's 3 left, both 3.5 up), which is the turret's mount. All 21
turrets of SURFACE stand on its 21 blocks (three put it a little right of the mount, still on the top). Some blocks
slide sideways with their turret (events 19 move both links alike: the lamps go first, 122/124 to the right, 84/86 to
the left). Shot down, a block takes its turret with it (links over 40 of a block of 20); when its armour falls to 6
its pieces switch to their damaged sprite, which is their own sprite again (no damaged look), and the turret, which
has none, dies then. No other level, episode 6's included, uses them, and no other enemy, launched ones included,
shows these sprites. 122/124 is 84/86's pixels mirrored a pixel right (column c is 48 - c; the outline exactly, three
quarters of the pixels alike, the shading repainted for the same light): the second block is the first one's model
mirrored about x 0.5.

As the sprites and their 4x upscales draw the first block (columns and rows of its 48 x 28 picture; ramp 10's browns, as
the plank turret's): a block of brown stone shaped like an ingot, seen from above and a little from the south: its flat
top (columns 14-38, rows 3-16, shades 8-a, its north edge lit, a dark rim behind it at row 2) with a lit rib along its
west edge (columns 15-16) and the square mount (columns 21-34, rows 5-15: a raised frame, lit on its west, east and
south bands, round a raised plate (columns 25-29, rows 6-12, its west edge lit, grooves round it) and a narrow bar
(columns 31-32)); its ends battered: the west end (columns 6-13, mid shades) with two lamps of red glass in slots along
it, the lower one near its foot (columns 8-9, rows 9-16), the upper one at its top edge (columns 12-13, rows 6-15),
each dark red on its outer side and glowing on its inner one (0x72 to 0x78); the east end (columns 39-45) in a mid
shade with two small studs; its corners cut (the north-west and north-east corners of its plan chamfered); its front a
dark battered face (rows 17-23, shades 3-4, streaked) with a notch in its foot (columns 15-22 of rows 22-23).

Built as that ingot of stone (a CAD solid: the convex hull of its top's and its foot's outlines, so that from straight
above it covers the sprites' pixels, its edges bevelled), TOP_H high, the notch and the lamps' slots cut into it
(exact booleans; the result rebuilt in a fixed order, polish_powerups_specials.canonical(), so the output is the same
every run); on it the rib, the mount (the frame's four bands, the plate and the bar, rounded bars and a bevelled box)
and the studs, the lamps' lenses in their slots (rounded bars of red glass, a little emission in their own reds: they
glow as the sprite draws them, under 0.65). Painted by the faces' directions and places as the sprite shades them
(the block's faces split on a grid GRID apart for that: palette materials have no textures): the top mottled in its
middle shades (smooth noise), its bevelled rim lit (most on the west, as the rib), the west end mid, the east end a
shade darker than the top, the front two shades lighter than the sprite's 3-4 and streaked along its length (the
game's sun leaves it in shade: so it shows as light as the sprite's front), the notch and the slots dark; stone a
little glossy, as the upscales paint it. Not sheared for the camera: the turret is a model of its own, drawn at its
own place on the block's top, so the top lies where the sprites draw it (the game's slanted camera sees the top a
little higher up the screen, TOP_H tan 20, the turret with it).

The turret on it: models.cfg draws the plank turret centred in height on the ground enemies' layer (4 pixels up: it
reaches 1.1-6.9 pixels over the terrain), inside a block TOP_H high. sprite 3 12 plank_turret yaw=aim
height=TURRET_HEIGHT sets it on the mount (its foot on the frame, FRAME_TOP; every plank turret in the game stands on
one of these blocks). (Its wreck, if the block stays, keeps that height: the game slumps a wreck about its middle.)

The whole is cut along the sprites' edge into the two pieces (x 0, the cuts capped with the stone's inside, CAP), each
piece's normals those of the uncut whole (polish_machine_kit.cut's way, cut() here, with a steadier lookup), each
moved so that its sprite's centre is its origin; every mesh triangulated before the export (polish_k_pod.triangulate);
the checks and previews work on copies, so the output is the same with and without them. height=-4 sets the pieces
on the terrain (the game keeps two pieces side by side moving alike at one height, the terrain's under their middle).

Coordinates: 1 unit = 1 game pixel; +X right, +Y up the screen, +Z up from the ground (z = 0); the whole's origin is
the middle of the picture (where the two sprites meet, half way down): the pixel edges of column c and row r are x =
c - 24 and y = 14 - r. The pieces' centres: the left sprite's (-12, 0), the right one's (12, 0).

Replaces wave3_n.py's lamp blocks: remove BLOCK_ORIGIN, lamp_block(), block_piece(), the two n.pieced("lamp_block_a"
/"lamp_block_b", ...) registrations, the lamp blocks' paragraph of its docstring (and its section header), and
wave3_n_art.py's BLOCK_A and BLOCK_B (only those lines read them). The hooded figure stays.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes of the wholes
and of each piece against enemy_3.png, from straight above and as the game's camera sees them), --preview <prefix>
(each piece's views), --whole <prefix> (the wholes' views and GLBs, for looking at), --only <name,...>.
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
sys.path.insert(0, os.path.join(HERE, "..", "items"))
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_powerups_specials import canonical  # noqa: E402
from polish_rock_arch import noise3  # noqa: E402

# The pieces: model, sprite, the first block (84/86) or the second (122/124), its box in the whole, its sprite's centre.
PIECES = [("lamp_block_84", 84, "a", (-24.0, 0.0), (-12.0, 0.0)),
          ("lamp_block_86", 86, "a", (0.0, 24.0), (12.0, 0.0)),
          ("lamp_block_122", 122, "b", (-24.0, 0.0), (-12.0, 0.0)),
          ("lamp_block_124", 124, "b", (0.0, 24.0), (12.0, 0.0))]
MIRROR_X = 0.5              # the second block is the first mirrored about x 0.5 (column c -> 48 - c)

# The form: the foot's outline (the sprites' outline, its corners as they cut them) and the top's, its height.
FOOT = [(-16.0, -10.0), (20.0, -10.0), (22.0, -8.0), (22.0, 6.0), (16.0, 12.0), (-9.0, 12.0), (-18.0, 7.0),
        (-18.0, -8.0)]
TOP = [(-10.0, -3.0), (15.0, -3.0), (15.0, 10.4), (14.4, 11.0), (-9.4, 11.0), (-10.0, 10.4)]
TOP_H = 7.0
SKIRT = 0.6                 # how far the block reaches under the ground (upright there)
GRID = 1.0                  # the broad faces split every GRID pixels, to be painted in patches
BEVEL = 1.1                 # the edges' rounding (the upscales round the block's edges broadly)
# The notch in the front's foot: its mouth (x0, x1 at the foot, x0, x1 at its roof), how far it reaches in, its roof.
NOTCH = ((-10.0, 0.0), (-9.0, -1.0), -6.2, 2.1)
# The lamps along the west end: their middle across (x in plan), their ends (y), the slot's half-width; the lens's.
LAMPS = [(-14.9, (-2.7, 4.7)), (-11.15, (-1.7, 7.7))]
SLOT_HW, SLOT_DEPTH = 1.05, 0.75
LENS_HW, LENS_OUT, LENS_IN = 0.78, 0.22, 0.6
# The rib along the top's west edge; the mount (the frame's outer and inner edges, its top over the top; the plate,
# the bar); the studs on the east end (x, y, radius).
RIB = (-8.0, (-2.4, 10.4), 0.95, 0.55)
FRAME_OUT = (-3.0, 11.0, -1.6, 9.0)
FRAME_IN = (-1.9, 9.9, -0.5, 7.9)
FRAME_RISE = 0.9
PLATE = (1.0, 6.0, 1.0, 7.8, 0.7)
BAR = (7.0, 9.0, 1.0, 7.8, 0.45)
STUDS = [(19.1, 5.6, 0.75), (19.3, -0.6, 0.75)]
FRAME_TOP = TOP_H + FRAME_RISE
# The plank turret's model reaches 0-5.86 (polish_plank_turret.py), drawn centred on the layer's 4 pixels: the height
# option that sets its foot on the frame.
TURRET_HEIGHT = round(FRAME_TOP - (4.0 - 5.86 / 2.0), 1)
CAP = 0xa5
VIEW_TILT = math.radians(20.0)


# --- Materials --------------------------------------------------------------------------------------------------------

def materials():
    m = {i: k.material("lamp_block_stone", palette=i, metallic=0.05, roughness=0.62) for i in range(0xa1, 0xac)}
    pal = k.level_palette()
    m["lens"] = k.material("lamp_block_lens", palette=0x74, metallic=0.0, roughness=0.25, emission=pal[0x75],
                           emission_strength=0.3)
    m["lens_hot"] = k.material("lamp_block_lens_hot", palette=0x77, metallic=0.0, roughness=0.25, emission=pal[0x77],
                               emission_strength=0.5)
    return m


# --- The block --------------------------------------------------------------------------------------------------------

def body(m):
    """The ingot: the convex hull of the foot's and the top's outlines, its edges bevelled; the notch and the slots
    cut."""
    bm = bmesh.new()
    for x, y in FOOT:
        bm.verts.new((x, y, 0.0))
        bm.verts.new((x, y, -SKIRT))
    for x, y in TOP:
        bm.verts.new((x, y, TOP_H))
    bmesh.ops.convex_hull(bm, input=bm.verts[:])
    mesh = bpy.data.meshes.new("block")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("block", mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.data.materials.append(m[0xa6])
    mk.cleanup(obj, dissolve=0.5)
    mk.bevel(obj, BEVEL, 3, 25.0)
    # The notch: a prism of its mouth's trapezoid (in x, z) reaching from in front of the foot to its back.
    (fx0, fx1), (rx0, rx1), back, roof = NOTCH
    notch = mk.prism("notch", [(fx0, -1.0), (fx1, -1.0), (rx1, roof), (rx0, roof)], -11.5, back, m[0xa1], axis="y")
    mk.boolean(obj, notch, "DIFFERENCE")
    # The lamps' slots: rounded bars along the west end, sunk into it.
    for i, (xc, (y0, y1)) in enumerate(LAMPS):
        pts, ups = slope_line(xc, y0 - 0.35, y1 + 0.35)
        cutter = mk.bar("slot%d" % i, pts, ups, SLOT_HW, 1.2, SLOT_DEPTH, m[0xa2], segments=16, power=4.0)
        mk.boolean(obj, cutter, "DIFFERENCE")
    mk.cleanup(obj, dissolve=0.0)
    canonical(obj)
    grid(obj)
    return obj


def grid(obj, step=GRID):
    """Splits the block's faces along a grid of planes (x, y and z every step pixels), so that its broad faces can be
    painted in patches and streaks (the palette's materials have no textures)."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    planes = [((x, 0.0, 0.0), (1.0, 0.0, 0.0)) for x in frange(-18.0, 22.0, step)]
    planes += [((0.0, y, 0.0), (0.0, 1.0, 0.0)) for y in frange(-10.0, 12.0, step)]
    planes += [((0.0, 0.0, z), (0.0, 0.0, 1.0)) for z in frange(0.5, TOP_H - 0.5, step)]
    for co, no in planes:
        bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-5, plane_co=co, plane_no=no)
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def frange(a, b, step):
    n = int(math.floor((b - a) / step + 1e-6))
    return [a + i * step for i in range(1, n)]


def west_slope():
    """The west end's plane: its top edge (x -10 at TOP_H), its foot (x -18 at 0): (outward normal, a point on it)."""
    n = Vector((-TOP_H, 0.0, 8.0)).normalized()
    return n, Vector((-10.0, 0.0, TOP_H))


def slope_line(x_plan, y0, y1, steps=6):
    """Points along y on the west end at x_plan (in plan), and the end's normal at each."""
    n, p0 = west_slope()
    z = TOP_H * (x_plan + 18.0) / 8.0
    pts = [Vector((x_plan, y0 + (y1 - y0) * i / steps, z)) for i in range(steps + 1)]
    return pts, [n] * len(pts)


def lenses(m):
    out = []
    n, _ = west_slope()
    for i, (xc, (y0, y1)) in enumerate(LAMPS):
        pts, ups = slope_line(xc, y0, y1)
        pts = [p - n * 0.1 for p in pts]
        lens = mk.bar("lens%d" % i, pts, ups, LENS_HW, LENS_OUT, LENS_IN, m["lens"], segments=16, power=2.4)
        k.smooth(lens, 60.0)
        # Its inner half (up the end, towards the top) glows hotter, as the sprite's right column.
        mk.paint(lens, lambda c, nrm, xc=xc: m["lens_hot"] if c.x > xc - 0.05 else None)
        out.append(lens)
    return out


def details(m):
    parts = []
    up = Vector((0.0, 0.0, 1.0))

    def along_y(name, x, y0, y1, hw, top, bottom, mat, z=TOP_H, power=4.0):
        pts = [Vector((x, y0 + (y1 - y0) * i / 4, z)) for i in range(5)]
        return mk.bar(name, pts, [up] * len(pts), hw, top, bottom, mat, segments=16, power=power)

    def along_x(name, y, x0, x1, hw, top, bottom, mat, z=TOP_H, power=4.0):
        pts = [Vector((x0 + (x1 - x0) * i / 4, y, z)) for i in range(5)]
        return mk.bar(name, pts, [up] * len(pts), hw, top, bottom, mat, segments=16, power=power)

    x, (y0, y1), hw, rise = RIB
    parts.append(k.smooth(along_y("rib", x, y0, y1, hw, rise, 0.3, m[0xaa], power=2.6), 50.0))
    ox0, ox1, oy0, oy1 = FRAME_OUT
    ix0, ix1, iy0, iy1 = FRAME_IN
    wx, ex = (ox0 + ix0) / 2, (ix1 + ox1) / 2
    sy, ny = (oy0 + iy0) / 2, (iy1 + oy1) / 2
    band_w, band_e = (ix0 - ox0) / 2, (ox1 - ix1) / 2
    band_s, band_n = (iy0 - oy0) / 2, (oy1 - iy1) / 2
    parts.append(along_y("frame_w", wx, oy0 + 0.05, oy1 - 0.05, band_w, FRAME_RISE, 0.3, m[0xa9]))
    parts.append(along_y("frame_e", ex, oy0 + 0.05, oy1 - 0.05, band_e, FRAME_RISE, 0.3, m[0xa9]))
    parts.append(along_x("frame_s", sy, ix0 - 0.2, ix1 + 0.2, band_s, FRAME_RISE, 0.3, m[0xa9]))
    parts.append(along_x("frame_n", ny, ix0 - 0.2, ix1 + 0.2, band_n, FRAME_RISE, 0.3, m[0xa9]))
    for name, (x0, x1, yb0, yb1, rise), mat in (("plate", PLATE, m[0xa9]), ("bar", BAR, m[0xa7])):
        box = mk.box(name, x0, x1, yb0, yb1, TOP_H - 0.3, TOP_H + rise, mat)
        mk.bevel(box, 0.22, 2, 30.0)
        parts.append(box)
    for i, (sx, sy_, r) in enumerate(STUDS):
        z = TOP_H * (22.0 - sx) / 7.0
        stud = mk.dome("stud%d" % i, (sx, sy_), (r, r, 0.55), z - 0.45, m[0xa8], segments=16, steps=5)
        parts.append(stud)
    for p in parts:
        mk.shade(p, 40.0, weighted=False)
    return parts


def mottle(c):
    """Smooth noise over the stone (the same every run), about -0.5 .. 0.5."""
    import numpy as np
    return float(noise3(np.array([c.x / 3.1]), np.array([c.y / 3.1]), np.array([c.z / 3.1]), 211)[0])


def paint_body(obj, m):
    """The block's faces by their direction and place, as the sprite shades them."""
    def pick(c, n):
        if c.z < 2.25 and -9.4 < c.x < -0.6 and c.y < -6.0 and n.z < 0.9:
            return m[0xa1]                                   # the notch
        if n.z > 0.92 and c.z > TOP_H - 0.2:
            if c.y > 10.0:
                return m[0xaa]                               # the top's north edge, lit
            v = mottle(c)
            return m[0xa9] if v > 0.36 else m[0xa7] if v < -0.12 else m[0xa8]   # the top, mottled
        if n.z > 0.55 and c.z > TOP_H - 1.6:
            if n.y < -0.2:                                   # the top's front edge: lit on its west part, as row 16
                return m[0xaa] if c.x < -2.0 else m[0xa9]
            return m[0xab] if n.x < -0.2 else m[0xaa]       # the bevel round the top: lit, most on the west
        if n.y > 0.55:
            return m[0xa4]                                   # the back
        if n.x < -0.45 and n.y > -0.6:
            return m[0xa6] if c.z > 1.0 else m[0xa5]         # the west end
        if n.x > 0.45 and n.y > -0.6:
            return m[0xa7] if c.z > 2.4 + 1.5 * mottle(c) else m[0xa6]   # the east end, a shade darker than the top
        if n.y < -0.3:
            # The front (in the sun's shade: two shades lighter than the sprite's 3-4, so that the game shows it as
            # light), streaked along its length.
            streak = math.sin(c.z * 1.5 + 0.8 * math.sin(c.x * 0.27) + 1.2 * mottle(c))
            if c.z < 0.9:
                return m[0xa5]
            return m[0xa7] if streak > 0.55 else m[0xa5] if streak < -0.6 else m[0xa6]
        if n.z < -0.5:
            return m[0xa2]
        return m[0xa5]
    mk.paint(obj, pick)
    # The slots' insides: the faces of the body sunk below the west end's plane round the lamps.
    nrm, p0 = west_slope()
    for poly in obj.data.polygons:
        c = poly.center
        if c.x < -9.5 and (c - p0).dot(nrm) < -0.12 and any(abs(c.x - xc) < SLOT_HW + 0.3 and y0 - 0.6 < c.y < y1 + 0.6
                                                         for xc, (y0, y1) in LAMPS):
            poly.material_index = mk.slot_of(obj, m[0xa2])


def whole_block(m):
    obj = body(m)
    paint_body(obj, m)
    mk.shade(obj, 30.0, weighted=True)
    parts = [obj] + details(m) + lenses(m)
    return join(parts, "block_a")


def join(objects, name):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objects:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.join()
    obj = bpy.context.view_layer.objects.active
    obj.name = obj.data.name = name
    return obj


def mirror(src, name):
    """The block mirrored about x = MIRROR_X (its faces' winding turned, its corner normals mirrored)."""
    obj = src.copy()
    obj.data = src.data.copy()
    obj.name = obj.data.name = name
    bpy.context.scene.collection.objects.link(obj)
    mesh = obj.data
    normals = [Vector(n.vector) for n in mesh.corner_normals]
    corner = {}
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            n = normals[li]
            corner[(poly.index, mesh.loops[li].vertex_index)] = (-n.x, n.y, n.z)
    for v in mesh.vertices:
        v.co.x = 2.0 * MIRROR_X - v.co.x
    mesh.flip_normals()
    new = [None] * len(mesh.loops)
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            new[li] = corner[(poly.index, mesh.loops[li].vertex_index)]
    mesh.normals_split_custom_set(new)
    mesh.update()
    return obj


# --- Checks -----------------------------------------------------------------------------------------------------------

def view_coverage(objects, w, h, centre):
    """What the game's camera sees of the objects (each point seen tan 20 * its height further up the screen), on
    copies (moving the objects there and back would change their points by rounding: the output must not depend on
    --check)."""
    shear = Matrix(((1, 0, 0, 0), (0, 1, math.tan(VIEW_TILT), 0), (0, 0, 1, 0), (0, 0, 0, 1)))
    copies = []
    for obj in objects:
        c = obj.copy()
        c.data = obj.data.copy()
        bpy.context.scene.collection.objects.link(c)
        c.data.transform(shear)
        copies.append(c)
    covered = mk.coverage(copies, w, h, centre=centre)
    for c in copies:
        data = c.data
        bpy.data.objects.remove(c)
        bpy.data.meshes.remove(data)
    return covered


def cut(source, box_xy, cap_mat):
    """polish_machine_kit.cut with a steadier normal lookup: the part of the block inside box (x0, x1, y0, y1), its cuts
    closed with flat caps of cap_mat, its corners' normals those of the uncut block where its faces lie, found a sixth
    of the way in from each corner (the kit's 2% can tie between two faces at a corner of a small face, and then the
    pick changed between runs); the underside and the caps flat."""
    x0, x1, y0, y1 = box_xy
    obj = source.copy()
    obj.data = source.data.copy()
    bpy.context.scene.collection.objects.link(obj)
    cap_index = mk.slot_of(obj, cap_mat)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    caps = set()
    planes = (((x0, 0, 0), (-1, 0, 0)), ((x1, 0, 0), (1, 0, 0)), ((0, y0, 0), (0, -1, 0)), ((0, y1, 0), (0, 1, 0)))
    for co, no in planes:
        result = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-6, plane_co=co,
                                        plane_no=no, clear_outer=True)
        edges = [e for e in result["geom_cut"] if isinstance(e, bmesh.types.BMEdge) and e.is_valid]
        open_edges = [e for e in edges if len(e.link_faces) == 1]
        if open_edges:
            filled = bmesh.ops.holes_fill(bm, edges=open_edges, sides=0)
            if filled["faces"]:
                for f in bmesh.ops.triangulate(bm, faces=filled["faces"])["faces"]:
                    f.normal_update()
                    if f.normal.dot(Vector(no)) < 0:
                        f.normal_flip()
                    caps.add(f)
    for f in caps:
        if f.is_valid:
            f.material_index = cap_index
            f.smooth = False
    bm.faces.index_update()
    cap_ids = {f.index for f in caps if f.is_valid}
    bm.to_mesh(obj.data)
    bm.free()
    src = mk.NormalSource(source)
    mesh = obj.data
    normals = []
    for poly in mesh.polygons:
        flat = poly.index in cap_ids or poly.normal.z < -0.9
        for li in poly.loop_indices:
            n = None
            if not flat:
                co = mesh.vertices[mesh.loops[li].vertex_index].co
                _, _, index, _ = src.bvh.find_nearest(co + (poly.center - co) / 6.0)
                if index is not None:
                    (ia, ib, ic), (la, lb, lc) = src.tris[index]
                    w = mk.barycentric(co, src.verts[ia], src.verts[ib], src.verts[ic])
                    v = src.normals[la] * w[0] + src.normals[lb] * w[1] + src.normals[lc] * w[2]
                    n = v.normalized() if v.length > 1e-8 else None
            normals.append(tuple(n if n is not None else poly.normal))
    mesh.normals_split_custom_set(normals)
    used = {p.material_index for p in mesh.polygons}
    for i in reversed(range(len(mesh.materials))):
        if i not in used and len(mesh.materials) > 1:
            mesh.materials.pop(index=i)
    return obj


def whole_mask(sheet, sprites):
    return k.sprite_mask(sheet, sprites)


def build():
    options = k.args()
    out = mk.outdir(options)
    only = set(options["only"].split(",")) if "only" in options else None
    sheet = os.path.join(options["check"], "enemy_3.png") if "check" in options else None
    k.reset()
    bpy.context.scene.view_settings.view_transform = "Standard"
    m = materials()
    whole_a = whole_block(m)
    whole_b = mirror(whole_a, "block_b")
    wholes = {"a": (whole_a, [84, 86]), "b": (whole_b, [122, 124])}
    print("whole: %d faces; the turret's height option: height=%.1f (its foot on the frame at %.2f)" % (
        len(whole_a.data.polygons), TURRET_HEIGHT, FRAME_TOP))
    for key, (obj, sprites) in wholes.items():
        if sheet:
            mask = whole_mask(sheet, sprites)
            mk.compare("whole %s (3 %d + %d) from straight above" % (key, sprites[0], sprites[1]),
                       mk.coverage([obj], 48, 28), mask)
            mk.compare("whole %s (3 %d + %d) as the game's camera sees it" % (key, sprites[0], sprites[1]),
                       view_coverage([obj], 48, 28, (0.0, 0.0)), mask)
        if "whole" in options:
            copy = obj.copy()
            copy.data = obj.data.copy()
            bpy.context.scene.collection.objects.link(copy)
            for o, _ in wholes.values():
                o.hide_render = True
            mk.preview(options["whole"] + "lamp_block_whole_" + key, [copy], size=(48, 28), scale=12, distance=1.3)
            triangulate([copy])
            mk.export([copy], options["whole"] + "lamp_block_whole_%s.glb" % key)
            bpy.data.objects.remove(copy)
            for o, _ in wholes.values():
                o.hide_render = False
    for name, sprite, key, (x0, x1), (ox, oy) in PIECES:
        if only and name not in only:
            continue
        whole = wholes[key][0]
        piece = cut(whole, (x0, x1, -14.0, 14.0), m[CAP])
        piece.name = piece.data.name = name
        for o, _ in wholes.values():
            o.hide_render = True
        if sheet:
            mask = k.sprite_mask(sheet, sprite)
            mk.compare("%s (3 %d) from straight above" % (name, sprite), mk.coverage([piece], 24, 28, (ox, oy)), mask)
            mk.compare("%s (3 %d) as the game's camera sees it" % (name, sprite),
                       view_coverage([piece], 24, 28, (ox, oy)), mask)
        piece.data.transform(Matrix.Translation((-ox, -oy, 0.0)))
        triangulate([piece])
        bpy.context.view_layer.update()
        mk.report(name, [piece], os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, [piece])
        bpy.data.objects.remove(piece)
        for o, _ in wholes.values():
            o.hide_render = False


if __name__ == "__main__":
    build()
