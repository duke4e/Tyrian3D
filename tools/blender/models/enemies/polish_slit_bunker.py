"""DELI's grey slit bunker (sheet C sprite 39, 2x2: 24 x 28 pixels; enemy 143 of episodes 1 and 3: DELIANI and New
Deli on the ground (t2456, the map's column 8 of row 203, over tile 582: the bunker's own wreck painted on the floor),
BONUS (3:6) in the sky, four of them; TORM, SOH JIN, GRYPHON, BOTANY A and B, BONUS 2:24 and SAVARA list it only among
their random enemies, which they switch off at once (event 13) and never on), polished (2026-10-22; it replaces
wave3_x.py's slit_bunker(): a heightfield of the sprite's plan painted pixel by pixel on a carpet of the map's floor
tiles, its slits glowing at 1.6-2.2 in every frame). models.cfg: model slit_bunker enemies/slit_bunker.glb (as before,
centred in height: it flies in BONUS) and the new model slit_bunker_41 / slit_bunker_43 enemies/slit_bunker_41.glb /
_43.glb; sprite c 39 slit_bunker yaw=0 (as before); frame c 41 slit_bunker_41, frame c 43 slit_bunker_43.

The frames: the bunker fires weapon 144 every 30 ticks and plays its five frames each time (animate 2: 39 41 43 41 39),
which light its two slits from inside, the glow rising from their near edges: 39 a dim red line along the upper slit's
near edge; 41 the upper slit's near half glowing (an orange core in its middle), the lower slit's near edge dim; 43
the upper slit's glow risen to its middle (hottest there), the lower slit's near two thirds glowing, its core orange
(frame models: the same geometry, the slits' floors in bands of glowing materials). No other enemy shows C 39, 41 or
43 (launched ones included), and no sprite of any sheet is these mirrored, turned or in other ramps. The sprite's
ramp-6 pixels round the bunker are the map's floor (in the sky the sprite carries a square of it): left out, the
silhouettes are checked against the bunker's own pixels.

As the sprites and their 4x upscales draw it (columns and rows of C 39, pixel edges): a grey bunker, its plan the
sprite's columns 1-21 of rows 1-25, its back corners cut off on the diagonal (columns 1-5 and 17-21 of rows 1-5). Down
its middle (columns 6-16) a raised spine, its top flat, lit along its left edge and its back; in it two slits (columns
8-15 of rows 4-8 and 11-14), a lit sill between them (row 8); under the lower slit a lit ledge (row 14), where the
spine's top breaks over the bunker's front, a glacis falling from row 15 to the floor at row 25, grooved into toes
(dark grooves at columns 10 and 13 from row 17.6, at columns 8 and 15 from row 19.6). Either side of the spine the
bunker's flanks slope down to its edges (the left one lit, the right one in shadow), each with two diagonal grooves
running down and out from the spine (from rows 6.5 and 12.5).

Built as a CAD modeller would: the plan extruded and cut by the planes of its top (the spine, the flanks, the back,
the glacis: exact booleans, intersected), its slits and grooves cut by booleans, its edges bevelled, flat faces kept
flat; painted as the sprite shades it; the slits' floors are grids of bands, glowing as each frame lights them
(emission well under 1: 0x72 0.22, 0x75 0.32, 0x79 0.45, 0x7a 0.5; the bloom adds to it). It is modelled in the
sprite's plane (x, y as the sprite draws them, z up from the floor) and then sheared along the game camera's line of
sight (y - z tan 20, the normals with it: polish_lava_grub.shear_to_camera), so that the camera sees every point where
the sprite draws it; seen from straight above, its top lies up to 3.3 pixels nearer the bottom of the screen than its
sprite. 9 pixels high (the old one 9.4): the game centres it in height (half its height is more than the ground
enemies' layer, 4, less 0.3) and lifts it to stand on the ground; every frame has the same bounds.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the floor (z = 0); origin at
the sprite's centre: column c is x = c - 12 at its left edge, row r is y = 14 - r at its top edge.

Replaces wave3_x.py's slit_bunker(): it is all that is left in wave3_x.py, so delete wave3_x.py (nothing imports it)
and wave3_x_art.py (only BUNKER and BUNKER_LIT are left in it, which only wave3_x.py reads), and take wave3_x_kit.py's
import of wave3_x_art out (wave3_x_kit.py stays: wave3_ah_kit.py imports it).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each frame's silhouette as the
game's camera sees it against the bunker's own pixels in enemy_C.png), --preview <prefix>, --only <name,...>.
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_arch import plane_box  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
import polish_deli_boss as db  # noqa: E402  (drop_unused, join)

TAN20 = math.tan(math.radians(20.0))
VIEW = Vector((0.0, math.sin(math.radians(20.0)), -math.cos(math.radians(20.0))))
NAMES = {39: "slit_bunker", 41: "slit_bunker_41", 43: "slit_bunker_43"}


def X(c):
    return c - 12.0


def Y(r):
    return 14.0 - r


def plan(points):
    """Pixel-edge points (column, row) as (x, y), counter-clockwise seen from above."""
    pts = [(X(c), Y(r)) for c, r in points]
    area = sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(pts, pts[1:] + pts[:1]))
    return pts if area > 0 else pts[::-1]


# --- The shape (the sprite's plane, before the shear) --------------------------------------------------------------
PLAN = [(1.0, 5.0), (5.0, 1.0), (17.0, 1.0), (21.0, 5.0), (21.7, 6.4), (21.7, 17.4), (21.0, 18.6), (21.0, 24.1),
        (20.1, 25.0), (1.9, 25.0), (1.0, 24.1)]
TOP = 9.0                                    # the spine's top
SPINE = (6.0, 16.0)                          # its columns
FLANK = 0.68                                 # the flanks fall this much per pixel out from the spine
BACK = (2.6, 1.55)                           # the back rounds down from this row, falling this much per row
GLACIS = (14.7, 25.0, 0.7)                   # the glacis falls from TOP at this row to this height at that row
SLITS = [(8.0, 15.0, 4.0, 8.0), (8.0, 15.0, 11.0, 14.0)]   # columns, rows
SLIT_DEPTH = 2.2
GROOVES = [(9.85, 11.1, 17.6), (12.85, 14.1, 17.6), (7.8, 8.9, 19.6), (15.0, 16.1, 19.6)]  # columns, from row
GROOVE_DEPTH = 1.0
TIERS = [((6.0, 6.5), (1.6, 10.4)), ((6.0, 12.5), (1.4, 17.4)), ((16.0, 6.5), (20.4, 10.4)),
         ((16.0, 12.5), (20.6, 17.4))]       # the flanks' diagonal grooves: from (column, row) to (column, row)
TIER_DEPTH = 0.45
# The slits' floors in bands from their near edge (the bottom of the sprite) up: each frame's light per band, the
# middle of a hot band hotter (its columns).
BANDS = 4
HOT_MIDDLE = (10.0, 13.5)
LIGHT = {39: ([("dim", None), None, None, None], [None, None, None]),
         41: ([("mid", "hot"), ("dim", None), None, None], [("dim", None), None, None]),
         43: ([("mid", None), ("mid", "hot"), ("dim", None), None], [("mid", "hotter"), ("dim", None), None])}


def spine_top(x, y):
    return TOP


def left_flank(x, y):
    return TOP + FLANK * (x - X(SPINE[0]))


def right_flank(x, y):
    return TOP - FLANK * (x - X(SPINE[1]))


def back(x, y):
    return TOP - BACK[1] * (y - Y(BACK[0]))


def glacis(x, y):
    r0, r1, z1 = GLACIS
    return TOP - (TOP - z1) * (Y(r0) - y) / (Y(r0) - Y(r1))


def top_of(x, y):
    return min(spine_top(x, y), left_flank(x, y), right_flank(x, y), back(x, y), glacis(x, y))


def materials():
    pal = k.level_palette()

    def mat(name, index, metallic=0.45, roughness=0.42, glow=0.0):
        if glow > 0:
            return k.material(name, palette=index, metallic=0.0, roughness=0.35, emission=pal[index],
                              emission_strength=glow)
        return k.material(name, palette=index, metallic=metallic, roughness=roughness)
    m = {"g1": mat("sbunk_g1", 0x01, 0.3, 0.6), "g2": mat("sbunk_g2", 0x02, 0.3, 0.6),
         "g3": mat("sbunk_g3", 0x03, 0.4, 0.5), "g4": mat("sbunk_g4", 0x04), "g5": mat("sbunk_g5", 0x05),
         "g6": mat("sbunk_g6", 0x06), "g7": mat("sbunk_g7", 0x07), "g8": mat("sbunk_g8", 0x08, 0.45, 0.38),
         "g9": mat("sbunk_g9", 0x09, 0.45, 0.36), "ga": mat("sbunk_ga", 0x0a, 0.45, 0.34)}
    m["dim"] = mat("sbunk_glow_dim", 0x72, glow=0.22)
    m["mid"] = mat("sbunk_glow_mid", 0x75, glow=0.32)
    m["hot"] = mat("sbunk_glow_hot", 0x79, glow=0.45)
    m["hotter"] = mat("sbunk_glow_hotter", 0x7a, glow=0.5)
    m["dark"] = m["g2"]
    return m


def body(m):
    """The bunker: its plan cut by the planes of its top, its slits, grooves and tiers cut in, bevelled, painted."""
    obj = mk.prism("bunker", plan(PLAN), 0.0, TOP + 1.0, m["g7"])
    for i, top in enumerate((spine_top, left_flank, right_flank, back, glacis)):
        mk.boolean(obj, plane_box("bunker_plane%d" % i, top), "INTERSECT")
    mk.cleanup(obj)
    cutters = []
    for i, (c0, c1, r0, r1) in enumerate(SLITS):
        cutters.append(mk.box("slit_cut%d" % i, X(c0), X(c1), Y(r1), Y(r0), TOP - SLIT_DEPTH, TOP + 2.0))
    for i, (c0, c1, r0) in enumerate(GROOVES):
        cutters.append(mk.wedge("groove_cut%d" % i, plan([(c0, r0), (c1, r0), (c1, 26.0), (c0, 26.0)]), 0.0,
                                lambda x, y: TOP + 2.0, bottom=lambda x, y: glacis(x, y) - GROOVE_DEPTH))
    for i, ((ca, ra), (cb, rb)) in enumerate(TIERS):
        a, b = Vector((X(ca), Y(ra))), Vector((X(cb), Y(rb)))
        side = (b - a).normalized()
        n = Vector((-side.y, side.x)) * 0.3
        quad = [tuple(a + n), tuple(a - n), tuple(b - n), tuple(b + n)]
        flank = left_flank if ca < 11 else right_flank
        cutters.append(mk.wedge("tier_cut%d" % i, quad, 0.0, lambda x, y: TOP + 2.0,
                                bottom=lambda x, y, f=flank: f(x, y) - TIER_DEPTH))
    for c in cutters:
        mk.boolean(obj, c, "DIFFERENCE")
    mk.cleanup(obj)
    mk.bevel(obj, 0.32, 2, 35)
    slit_boxes = [(X(c0), X(c1), Y(r1), Y(r0)) for c0, c1, r0, r1 in SLITS]
    groove_boxes = [(X(c0), X(c1), Y(26.0), Y(r0)) for c0, c1, r0 in GROOVES]
    sun = Vector((-0.6, 0.6, 1.0)).normalized()

    def inside(c, box, pad=0.02):
        x0, x1, y0, y1 = box
        return x0 - pad <= c.x <= x1 + pad and y0 - pad <= c.y <= y1 + pad

    def pick(c, n):
        top = top_of(c.x, c.y)
        if any(inside(c, b) for b in slit_boxes) and c.z < TOP - 0.05:
            return m["g2"] if n.z > 0.7 else m["g3"]          # the slits' walls (their floors: the glow plates)
        if any(inside(c, b, 0.0) for b in groove_boxes) and c.z < top - 0.1:
            return m["g1"]                                     # the toes' grooves
        if c.z < 1.9 and n.y < -0.2:
            return m["g2"]                                     # the toes' feet in shadow
        if c.z < top - TIER_DEPTH * 0.5 and abs(n.z) < 0.95 and c.z > 3.0 and abs(c.x - X(11.0)) > 5.2:
            return m["g2"] if n.dot(sun) < 0.5 else m["g7"]   # the tiers: a shadowed wall, a lit edge
        d = n.dot(sun)
        if n.z > 0.97:
            return m["g7"]                                     # the spine's top
        if n.y > 0.3 and n.z > 0.3:
            return m["g9"] if d > 0.8 else m["g8"]             # the back, lit
        if n.y < -0.3 and n.z > 0.2:
            # the glacis (facing away from the sun: light greys, to read as the sprite's), the toes' lit sides
            return m["ga"] if d > 0.6 or n.x < -0.15 else m["g9"]
        if n.x < -0.2:
            return m["ga"] if d > 0.9 else m["g6"] if d > 0.6 else m["g5"]    # the left flank and the spine's edge
        if n.x > 0.2:
            return m["g4"] if n.z > 0.6 else m["g3"]           # the right flank, in shadow
        return m["g4"]
    mk.paint(obj, pick)
    return obj


def slit_floors(m):
    """The slits' floors: grids of bands across each slit (from its near edge up), a hot band's middle split off."""
    floors = []
    for i, (c0, c1, r0, r1) in enumerate(SLITS):
        bands = BANDS if i == 0 else 3
        x0, x1 = X(c0) + 0.05, X(c1) - 0.05
        y_near, y_far = Y(r1) + 0.05, Y(r0) - 0.05
        z = TOP - SLIT_DEPTH + 0.04
        cols = [x0, X(HOT_MIDDLE[0]), X(HOT_MIDDLE[1]), x1]
        bm = bmesh.new()
        grid = []
        for b in range(bands + 1):
            y = y_near + (y_far - y_near) * b / bands
            grid.append([bm.verts.new((x, y, z)) for x in cols])
        for b in range(bands):
            for j in range(3):
                bm.faces.new((grid[b][j], grid[b][j + 1], grid[b + 1][j + 1], grid[b + 1][j]))
        mesh = bpy.data.meshes.new("slit_floor%d" % i)
        bm.to_mesh(mesh)
        bm.free()
        obj = bpy.data.objects.new("slit_floor%d" % i, mesh)
        bpy.context.scene.collection.objects.link(obj)
        obj.data.materials.append(m["dark"])
        floors.append(obj)
    return floors


def light_slits(floors, frame, m):
    """Gives the slits' floors a frame's light: each band's material, a hot band's middle its own."""
    for i, obj in enumerate(floors):
        spec = LIGHT[frame][0 if i == 0 else 1]
        mesh = obj.data
        mesh.materials.clear()
        mesh.materials.append(m["dark"])
        bands = BANDS if i == 0 else 3
        for poly in mesh.polygons:
            b, j = divmod(poly.index, 3)
            light = spec[b] if b < len(spec) else None
            mat = m["dark"]
            if light is not None:
                base, middle = light
                mat = m[middle] if (middle is not None and j == 1) else m[base]
            poly.material_index = mk.slot_of(obj, mat)
        db.drop_unused([obj])
        mesh.update()
        assert bands == len(mesh.polygons) // 3


# --- To the game's camera --------------------------------------------------------------------------------------------

def shear_to_camera(objects):
    """polish_lava_grub.shear_to_camera: every point moved along the camera's line of sight to its height (y - z tan
    20), so that the camera sees it where the sprite draws it; the normals follow (the shear's inverse transpose)."""
    for obj in objects:
        mesh = obj.data
        normals = [Vector(cn.vector) for cn in mesh.corner_normals]
        for v in mesh.vertices:
            v.co.y -= v.co.z * TAN20
        out = [Vector((n.x, n.y, n.z + TAN20 * n.y)).normalized() for n in normals]
        mesh.normals_split_custom_set([tuple(n) for n in out])
        mesh.update()


def own_mask(sheet, sprite):
    """The bunker's own pixels: the sprite's but its ramp-6 floor."""
    mask = k.sprite_mask(sheet, sprite)
    raw = open(sheet[:-4] + ".idx", "rb").read()
    x0, y0 = (sprite - 1) % 19 * 12, (sprite - 1) // 19 * 14
    return [[mask[r][c] and raw[(y0 + r) * 228 + x0 + c] >> 4 != 6 for c in range(24)] for r in range(28)]


def view_coverage(objects, sub=3):
    """Which pixels of the 24 x 28 picture the game's camera sees the objects at (rays along its line of sight)."""
    depsgraph = bpy.context.evaluated_depsgraph_get()
    trees = [BVHTree.FromObject(o, depsgraph) for o in objects]
    out = []
    for r in range(28):
        line = []
        for c in range(24):
            hits = 0
            for i in range(sub):
                for j in range(sub):
                    origin = Vector((X(c + (i + 0.5) / sub), Y(r + (j + 0.5) / sub), 0.0)) - VIEW * 200.0
                    if any(t.ray_cast(origin, VIEW, 400.0)[0] is not None for t in trees):
                        hits += 1
            line.append(hits * 2 > sub * sub)
        out.append(line)
    return out


def build():
    options = k.args()
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    sheet = os.path.join(options["check"], "enemy_C.png") if "check" in options else None
    k.reset()
    m = materials()
    bunker = body(m)
    floors = slit_floors(m)
    for frame in (39, 41, 43):
        name = NAMES[frame]
        if only and name not in only:
            continue
        light_slits(floors, frame, m)
        parts = []
        for src in [bunker] + floors:
            c = src.copy()
            c.data = src.data.copy()
            bpy.context.scene.collection.objects.link(c)
            parts.append(c)
        for src in [bunker] + floors:
            src.hide_render = True
        mk.shade(parts[0], 35)
        triangulate(parts)
        shear_to_camera(parts)
        obj = db.join(parts, name)
        obj.data.name = name
        bpy.context.view_layer.update()
        if sheet:
            mk.compare("%s (C %d), as the game's camera sees it" % (name, frame), view_coverage([obj]),
                       own_mask(sheet, frame))
        bpy.context.scene.view_settings.view_transform = "Standard"
        mk.report(name, [obj], os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, [obj], distance=0.7)
        data = obj.data
        bpy.data.objects.remove(obj)
        if data.users == 0:
            bpy.data.meshes.remove(data)
        for src in [bunker] + floors:
            src.hide_render = False


if __name__ == "__main__":
    build()
