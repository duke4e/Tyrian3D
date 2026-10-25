"""What is left of the foot of MINERS's banded rock column once the column is destroyed (sheet M sprites 239 and 241:
their stand-ins, the column's broken stump the map paints in the tile row under them, before the column comes, once
it is shot and where none comes; 5 of them, MINERS 8362fe151f78556b), stage 4 of the clean ground (2026-10-25), built
on polish_rock_column.py. The column's upper four pieces have the game's own broken look (rock_column_wreck_tl / _tr
/ _ml / _mr: dgr 167 169 205 207, which stay); these are the lower two's wrecks. models.cfg: model
rock_column_bl_wreck / rock_column_br_wreck enemies/rock_column_bl_wreck.glb / rock_column_br_wreck.glb origin; wreck
m 239 rock_column_bl_wreck, wreck m 241 rock_column_br_wreck (drawn with the live sprite lines' options, yaw=0
height=-4).

As MINERS paints it at 4x (at 576, 3878; columns and rows of the 48 x 84 picture): the column's foot in its own outline
(rows 56-77, columns 1-46: the lower drum's sides and the plinth's flare round it, its rim dark), but the drum within it
shattered: big broken lumps of the tan stone (0xa2-0xab), lit on their tops, flecked with gold (0x17-0x1d), lying at
different heights (a big one at the upper left, columns 2-10 of rows 56-63; a tall lit piece at columns 20-23 of rows
56-64; a heap at columns 26-37 of rows 57-67; smaller ones low down at columns 11-19 of rows 62-71), between them black
gaps (0x00, 0x01, 0x10; the deepest at columns 12-19 of rows 56-63) and dark purple-brown shadow (0xf0, 0xf1) along the
bottom of the bowl.

The model: polish_rock_column.py's lower drum, plinth and lower joint core (built as its build_column() builds them, the
same random numbers), broken as its broken look is (its funnel cutters, exact booleans with self-intersection, the
meshes put in a fixed order after them): the drum's whole front inside the rim broken down by a jagged funnel (SHATTER:
its floor up to 1.45 under the surface, its points jittered: broken faces in the stone's colour), the painting's black
gaps cut deeper as hollows (polish_rock_column.hollow_mask() of the painting against the intact picture, its
hollow_cutters()), V cracks across the rim; faces deeper than DEEP under the old surface are the holes' dark insides
(0x61), those deeper than SHADOW the stone's darker shade (0xa4), the shallower broken faces the stone's own (0xa7);
broken lumps, their tops lit (0xaa), (faceted hulls, polish_rock_column.rubble()) lying on the broken floor where the
painting draws them; gold flecks where its gold is (polish_rock_column.details() with the painting as the look). Cut and
sheared along the camera's lines of sight as the live pieces (polish_rock_column.export_pieces()).

Coordinates as polish_rock_column.py's: designed in the picture's plane (pic_xy(c, r)), then sheared to the camera; 1
unit = 1 game pixel; the whole's origin is the corner where 201 and 203 meet; the pieces' centres (-12, -28), (12, -28).

Options after "--": --outdir <dir> (default assets/models/enemies), --preview <prefix>.
"""
import math
import os
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
import polish_rock_column as live  # noqa: E402

PIC_X, PIC_Y = 552, 3808                            # where MINERS (8362fe151f78556b) has the picture's corner
ROW0 = 56                                           # the stump's rows: from here down
PIECES = [("rock_column_bl_wreck", 239, (None, 0.0, None, -14.0), (-12.0, -28.0)),
          ("rock_column_br_wreck", 241, (0.0, None, None, -14.0), (12.0, -28.0))]
SHATTER = (1.45, 0.8, 1.0, 1.6)     # the broken drum's floor: depth (under DEEP: the stone's own colour), slope (per
#                                     pixel in from the rim), jitter, the rim left standing
RUBBLE = [(6.0, 59.4, 5.8), (21.6, 60.4, 3.6), (31.0, 62.0, 6.0), (38.0, 66.0, 3.6), (16.0, 66.6, 4.6),
          (11.6, 70.0, 3.0), (26.4, 70.0, 3.0), (41.0, 60.4, 2.8), (27.0, 58.8, 2.6), (20.6, 69.6, 2.6)]
CRACKS = [[(4.0, 66.0), (6.4, 70.2), (9.6, 73.0)], [(43.2, 64.0), (40.6, 69.0), (37.0, 72.6)]]
SHADOW = 0.75                       # broken faces deeper than this under the old surface: the stone's darker shade


# The painting's rows ROW0..79 (MINERS's 1x pixels at PIC_X, PIC_Y + ROW0), as polish_rock_column's ART: a hex digit a
# shade (the tan, brown and grey ramps), G gold (ramp 1, shades 7-12), K the near-blacks (0x00-0x02, 0x10, 0x11, 0xf0,
# 0xf1), '.' none or the red ground (ramp 4, the map's: left out).
PAINTING = """
....65757445KKKKKKKK6aa9786433KKKKKKK3462.434...
..67656778984KKKKKKKK47643.KKKKK235553343335432.
..375487887a94KKKKKKK4633KK.234233343234334533K.
..266588798a83KKKKKK26954466423432434223335443K.
..K7558a99864KKKKKKK28bG57766223324332.223G543K.
..K7558d89883KKKKKKKK59G5675655445422.K.243433K.
..K765688885KKKKKKKKK59G5533553235543333245343K.
..K767696642KKK65KKKK6875754576652K53433335343K.
..K7675854KKKK2785KKK7a95742577GGG33.K23233443K.
..57766432K22247995KK69867K2477GGG33.KKK..34432.
..764753KK223543975KK566566356746644332.KK34222.
..262K6KKK2666776995269755643446663443432K4KK22.
..K23KKKKK257778699835765544553534.2333425KKKK2.
...K2KKKKKK5777644675366555544342.2322345KK2K2..
....KKKKKK2357655455567555554444433222762K2KK...
....2KKKKKK46888a344577655665.339866555522KK....
....22KKKK22KK223568GGb665b87764KKKKK3443KK.....
......KKKKK2443KKKKKKK67875KKKKKKK233322KK......
......KKKKKKKKK2K343KK37762K233K2KKKKKKKK0......
......KKKKKKKKKKKKKKKK34653KKKKKKKKKK234K.......
......KKK.....22KKKKKKKKKKKKKKKK33322KK0........
.......2...........332KKKKK222K2222200..........
......................2KK..0KK.22..22...........
.....................222...2....................
"""


def painting(base):
    """The painting as polish_rock_column.art() arrays (84 x 48: shades, gold, quartz, black): its rows ROW0..79 from
    PAINTING, the rows above base's (the intact picture's: not cut)."""
    shade, gold, quartz, black = (a.copy() for a in base)
    for i, line in enumerate(PAINTING.strip("\n").split("\n")):
        r = ROW0 + i
        shade[r, :] = np.nan
        gold[r, :] = quartz[r, :] = black[r, :] = False
        for c, ch in enumerate(line):
            if ch == ".":
                continue
            if ch == "G":
                shade[r, c], gold[r, c] = 9.0, True
            elif ch == "K":
                shade[r, c], black[r, c] = 1.5, True
            else:
                shade[r, c] = int(ch, 16)
    return shade, gold, quartz, black


def stones(m):
    """The lower drum, the plinth and the lower joint's core, as build_column() builds them."""
    rand = live.Rand(7)
    lower = live.drum("drum_low", live.PLINTH[-1][0] - 1.5, live.J1 - live.GAP, m["drum"], rand)
    foot = live.plinth(m["drum"], rand)
    core = live.joint("joint_1", live.J1, m["joint"])
    for obj in (lower, foot, core):
        live.slice_off(obj, [(Vector((0, 0, -live.SKIRT)), Vector((0, 0, -1)))])
    bpy.context.view_layer.update()
    return lower, foot, core


def shatter_cutter(own, hit, mat):
    """The drum broken down inside the rim: a funnel over the stump's outline shrunk by the rim."""
    depth, slope, jag, rim = SHATTER
    mask = own.copy()
    mask[:ROW0, :] = False
    mask = live.morph(mask, 3, False)
    out = []
    for i, loop in enumerate(live.mask_loops(mask, -24.0, 42.0, chaikin=1, sigma=0.9)):
        if live.area(loop) < 20.0:
            continue
        poly = live.safe_grow(loop, -rim, 0.5, 300 + i)
        out.append(live.funnel("shatter_%d" % i, poly, depth, slope, hit, 0.0, mat, 301 + i, spacing=1.15,
                               jag_floor=jag))
    return out


def hollow_cutters(black, hit, mat):
    """polish_rock_column.hollow_cutters() with a coarser grid (fewer triangles: the stump's faces are flat facets)."""
    out = []
    for n, g in enumerate(live.components(black)):
        if len(g) < live.HOLLOW_MIN:
            continue
        mask = np.zeros(black.shape, bool)
        for r, c in g:
            mask[r, c] = True
        depth = live.HOLLOW_DEPTH[0] + (live.HOLLOW_DEPTH[1] - live.HOLLOW_DEPTH[0]) * min(1.0, len(g) / 60.0)
        rs = [p_[0] for p_ in g]
        cs = [p_[1] for p_ in g]
        fallback = hit(*live.pic_xy(sum(cs) / len(cs) + 0.5, sum(rs) / len(rs) + 0.5))
        z_miss = fallback[0].z if fallback is not None else 0.0
        for i, loop in enumerate(live.mask_loops(mask, -24.0, 42.0, chaikin=1, sigma=0.7)):
            if live.area(loop) < 1.5:
                continue
            poly = live.safe_grow(loop, live.HOLLOW_GROW, live.JAG, 7 * n + i)
            out.append(live.funnel("hollow_%d_%d" % (n, i), poly, depth, live.HOLLOW_SLOPE, hit, z_miss, mat, 11 + n,
                                   0.95))
    return out


def break_stones(parts, cutters, m):
    """build_column()'s cut: the joined cutter out of each part (exact, self-intersecting), the broken faces the part's
    stone, the deep ones dark; the meshes in a fixed order."""
    hit = live.ray_down(parts)
    cutter = live.join(cutters, "cutter")
    mesh = cutter.data
    names = [mt.name for mt in mesh.materials]
    deep = []
    for poly in mesh.polygons:
        c = poly.center
        h = hit(c.x, c.y)
        zs = h[0].z if h is not None else c.z
        broken = names[poly.material_index] == m["hollow"].name
        deep.append(2 if broken and zs - c.z > live.DEEP else 1 if broken and zs - c.z > SHADOW else 0)
    for obj in parts:
        tool = cutter.copy()
        tool.data = cutter.data.copy()
        bpy.context.scene.collection.objects.link(tool)
        tool.hide_render = True
        tool.data.materials.clear()
        tool.data.materials.append(obj.data.materials[0])
        tool.data.materials.append(m["drum_dark"])
        tool.data.materials.append(m["hollow"])
        tool.data.polygons.foreach_set("material_index", deep)
        mod = obj.modifiers.new("boolean", "BOOLEAN")
        mod.operation = "DIFFERENCE"
        mod.solver = "EXACT"
        mod.material_mode = "TRANSFER"
        mod.use_self = True
        mod.object = tool
        mk.apply(obj)
        data = tool.data
        bpy.data.objects.remove(tool)
        bpy.data.meshes.remove(data)
        live.canonical(obj)
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method="FIXED", ngon_method="EAR_CLIP")
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        bad = sum(1 for e in bm.edges if not e.is_manifold)
        bm.to_mesh(obj.data)
        bm.free()
        if bad:
            print("  %s: %d non-manifold edges after the cuts" % (obj.name, bad))
    data = cutter.data
    bpy.data.objects.remove(cutter)
    bpy.data.meshes.remove(data)
    bpy.context.view_layer.update()


def build_whole(m):
    pic = live.art(live.ART)
    look = painting(pic)
    lower, foot, core = stones(m)
    parts = [lower, foot, core]
    hit = live.ray_down(parts)
    hollows = live.hollow_mask(pic, look)
    hollows[:ROW0] = False
    live.CRACKS = CRACKS
    cutters = (shatter_cutter(live.own_pixels(look), hit, m["hollow"]) + hollow_cutters(hollows, hit, m["hollow"]) +
               live.crack_cutters(hit, m["hollow"]))
    break_stones(parts, cutters, m)
    live.RUBBLE = RUBBLE
    lumps = live.rubble(parts, m, live.Rand(73))
    for lump in lumps:     # (the broken lumps' tops lit, as the painting's)
        mk.paint(lump, lambda c, n: m["drum_lit"] if n.z > 0.55 else m["drum"])
    # The gold flecks of the painting (the intact picture's above the stump lie on the middle pieces: left out).
    flecks = (look[0], look[1].copy(), look[2].copy(), look[3])
    flecks[1][:ROW0] = False
    flecks[2][:ROW0] = False
    extra = live.details(flecks, [lower, foot], m, live.Rand(11), hollows)
    return parts + lumps + extra, look


def build():
    options = k.args()
    out = mk.outdir(options)
    k.reset()
    bpy.context.scene.view_settings.view_transform = "Standard"
    m = live.materials()
    m["drum_dark"] = k.material("column_drum_dark", palette=0xa4, metallic=0.0, roughness=0.88)
    m["drum_lit"] = k.material("column_drum_lit", palette=0xaa, metallic=0.0, roughness=0.82)
    parts, look = build_whole(m)
    print("rock column stump: %d parts, %d triangles" % (len(parts), mk.triangles(parts)))
    live.export_pieces(parts, PIECES, look, options, out, "rock_column_wreck")


if __name__ == "__main__":
    build()
