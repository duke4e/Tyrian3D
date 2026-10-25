"""The wreck of the middle right purple pad of TYRIAN's panel (sheet 2 sprite 207, purple_pad_r; its stand-in: what
TYRIAN's background 3 map ad33fadb8ad32f83 paints where it rides, before it comes and once it is destroyed, at 516,
10261 and 612, 12277, both the same painting), built on polish_purple_pads.py (2026-10-25, the clean ground's stage 5:
the top enemies riding background 3). The other pads are painted as they are (their stand-ins, where they have any, are
their own models). models.cfg: model purple_pad_r_wreck enemies/purple_pad_r_wreck.glb origin; wreck 2 207
purple_pad_r_wreck (drawn with sprite 2 207's options: yaw=0 height=-6).

As the map paints it (background 3's tile at 4x in the HD tiles; the sprite's coordinates, +y up the screen): the pad
and the floor round it in the sprite's place and outline (the purple reaches x 0 at the top, x 7-8 down the middle, x 1
at the bottom, as the sprite's), but broken into rounded purple lumps, each lit along its upper left (0x5a-0x5c) and
shaded to the lower right, dark cracks between them (0x52-0x54); the pad's right and lower right lumps sunk and darker
(0x52-0x56); a dark shadow along its broken right edge (x 3..9, y -2..-13: the only pixels the clean ground erases here,
146 of them: the purple tiles are ordinary ones, so the painted lumps stay on the ground under the model).

The model: polish_purple_pads.py's floor plate, pads and the junctions on the piece's left edge (its build functions and
materials), cut to the sprite's box as the live piece (polish_arch.cut, the seams' purple), then cracked: split into
lumps along the edges of a Voronoi partition of the piece (plane cuts, closed over each cut in the cracks' dark purple),
each lump drawn in a little from its neighbours, rounded into a boulder (polish_machine_kit.soften: a voxel remesh,
smoothed, decimated), sunk and tilted (the right and lower right ones most), and painted by its normals as the live pads are (lit upper left, darker lower right; the sunk lumps'
tops a shade darker); under them a dark purple bed (0x52) that the cracks show; a few small purple chips and dark soot
bits along the broken right edge; all moved PAINT_DY down the screen, where the painting lies (a pixel lower than the
sprite at both places).

Coordinates as polish_purple_pads.py's, moved to the piece's middle (the live piece's origin, models.cfg origin): 1 unit
= 1 game pixel, +X right, +Y up the screen, +Z up from background 3's plane (z = 0).

Options after "--": --outdir <dir> (default assets/models/enemies), --preview <prefix>.
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
from polish_arch import cut  # noqa: E402
from polish_deli_boss import join  # noqa: E402
import polish_purple_pads as pp  # noqa: E402
import polish_panel_pills_wreck as wk  # noqa: E402
from polish_jaw_gun_wreck import rock  # noqa: E402

NAME, SPRITE, BOX = next(p for p in pp.PIECES if p[1] == 207)
CENTRE = ((BOX[0] + BOX[1]) / 2, (BOX[2] + BOX[3]) / 2)
# The lumps: the Voronoi seeds (the piece's coordinates), and for each its fall (how far it sinks, its tilt about x
# and y in degrees) and whether its top is the darker shade (the sunk ones).
LUMPS = [((-10.8, 7.0), (0.15, 2.0, -2.0), False),      # the floor's left column, upper
         ((-10.8, -4.0), (0.2, -2.0, 2.0), False),      # and lower
         ((-6.4, 12.4), (0.25, 3.0, 2.0), False),       # the band at the top
         ((-1.2, 10.6), (0.4, 4.0, 3.0), False),        # the pad's top
         ((-4.4, 3.2), (0.35, -3.0, -3.0), False),      # the pad's middle left
         ((4.8, 2.2), (0.9, 4.0, 7.0), True),           # the pad's right, sunk
         ((-3.8, -5.4), (0.55, -5.0, 3.0), False),      # the pad's lower part
         ((2.4, -6.8), (1.1, -5.0, 7.0), True),         # its lower right, sunk
         ((-7.0, -11.6), (0.35, -3.0, -2.0), False),    # the band at the bottom
         ((-0.6, -11.8), (0.7, -3.0, 5.0), True)]
PAINT_DY = -1.0                # the painting lies a pixel lower down the screen than the live sprite (both places)
GAP = 0.32                     # how far each lump is drawn in from its cell's edges
ROUND = (0.3, 10, 0.7, 0.2)    # its edges rounded (polish_machine_kit.soften: voxel, iterations, factor, ratio)
# The dark bed under the lumps (the piece's purple outline, a little in) and its top.
BED = [(-12.0, 14.0), (0.0, 14.0), (0.0, 10.4), (3.8, 10.4), (8.6, 5.0), (8.6, -0.8), (3.6, -5.8), (1.4, -5.8),
       (1.4, -14.0), (-12.0, -14.0)]
BED_TOP = 0.35
# Chips along the broken right edge (centre, radii, material key).
CHIPS = [((7.4, -2.2, 0.1), (1.0, 0.8, 0.6), "wall"), ((5.4, -4.8, 0.1), (0.9, 0.8, 0.5), "dark"),
         ((3.2, -8.6, 0.1), (0.8, 0.9, 0.5), "wall"), ((8.2, 2.4, 0.1), (0.7, 0.8, 0.45), "seam"),
         ((6.6, -6.0, 0.0), (0.9, 0.7, 0.4), "soot"), ((4.4, -11.2, 0.0), (0.8, 0.7, 0.35), "soot")]


def live_piece(m):
    """The live piece's parts: the floor, the pads and the junctions on its left edge, cut to its box, moved to its
    middle, joined into one mesh."""
    pp.floor_plate(m)
    pp.pads(m)
    for i, (X, Y) in enumerate(pp.JUNCTIONS):
        if X > 0:
            pp.junction(i, X, Y, m)
    whole = mk.meshes()
    for obj in whole:
        mk.apply(obj)
    pieces = [p for p in (cut(src, BOX, m["seam"]) for src in whole) if p is not None]
    for src in whole:
        bpy.data.objects.remove(src)
    mk.transform(pieces, Matrix.Translation((-CENTRE[0], -CENTRE[1], 0.0)))
    bpy.context.view_layer.update()
    for obj in pieces:
        mk.apply(obj)
    return join(pieces, "piece")


def lump(source, i, m):
    """Lump i: the part of the source nearer its seed than any other, closed over its cuts, drawn in, sunk, tilted,
    rounded and painted."""
    seed, (sink, tx, ty), sunk = LUMPS[i]
    obj = source.copy()
    obj.data = source.data.copy()
    obj.name = f"lump{i}"
    bpy.context.scene.collection.objects.link(obj)
    cap = mk.slot_of(obj, m["recess"])
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    s = Vector((seed[0], seed[1], 0.0))
    for j, (other, _, _) in enumerate(LUMPS):
        if j == i or not bm.faces:
            continue
        o = Vector((other[0], other[1], 0.0))
        n = (o - s).normalized()
        co = (s + o) / 2 - n * GAP
        bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-5, plane_co=co, plane_no=n,
                               clear_outer=True)
        edges = [e for e in bm.edges if e.is_boundary]
        edges.sort(key=lambda e: tuple(sorted((tuple(e.verts[0].co), tuple(e.verts[1].co)))))
        if edges:
            for f in bmesh.ops.holes_fill(bm, edges=edges, sides=0)["faces"]:
                f.material_index = cap
    if not bm.faces:
        bm.free()
        bpy.data.objects.remove(obj)
        return None
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(obj.data)
    bm.free()
    if obj.data.has_custom_normals:
        with bpy.context.temp_override(object=obj, active_object=obj, selected_editable_objects=[obj]):
            bpy.ops.mesh.customdata_custom_splitnormals_clear()
    mk.soften(obj, ROUND[0], ROUND[1], ROUND[2], ROUND[3])
    centre = sum((v.co for v in obj.data.vertices), Vector()) / max(1, len(obj.data.vertices))
    pivot = Vector((centre.x, centre.y, 0.0))
    obj.data.transform(Matrix.Translation(pivot - Vector((0.0, 0.0, sink))) @
                       Matrix.Rotation(math.radians(tx), 4, "X") @ Matrix.Rotation(math.radians(ty), 4, "Y") @
                       Matrix.Translation(-pivot))
    k.smooth(obj, 180.0)
    pp.paint_by_normal(obj, m, top="dark" if sunk else "top", lit="light" if sunk else "lit",
                       mid="wall" if sunk else "floor", dark="seam" if sunk else "dark")
    return obj


def build():
    options = k.args()
    k.reset()
    m = pp.materials()
    m["soot"] = k.material("pads_soot", palette=0x50, metallic=0.1, roughness=0.85)
    source = live_piece(m)
    for i in range(len(LUMPS)):
        lump(source, i, m)
    bpy.data.objects.remove(source)
    bed = mk.prism("bed", pp.ccw(list(BED)), pp.SKIRT, BED_TOP, m["recess"])
    mk.shade(bed, 35)
    for i, (centre, radii, key) in enumerate(CHIPS):
        rock(f"chip{i}", centre, radii, m[key], 71.0 + 1.7 * i, flat=0.0)
    mk.transform(mk.meshes(), Matrix.Translation((0.0, PAINT_DY, 0.0)))
    wk.clip_below(mk.meshes(), pp.SKIRT)
    wk.finish(NAME + "_wreck", options)


if __name__ == "__main__":
    build()
