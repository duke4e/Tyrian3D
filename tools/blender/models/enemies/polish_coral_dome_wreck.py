"""CORAL's purple dome's wreck, its lower half (sheet T sprites 53 and 55's stand-ins: what CORAL's map paints in the
tiles under the dome's lower half once it is destroyed, before it comes and where none comes; 5 of each), built on
polish_coral_sea.py's dome and its wreck (2026-10-25, the clean ground's stage 4). The upper pieces stand in as their
own damaged looks (T 91 and 93: coral_dome_tl_damaged, coral_dome_tr_damaged, the dome's back blown out); this is
the same wreck's lower half, broken as the map paints it.

As the map paints it at 4x (CORAL 2ff0cd9f3b388afd at 588 and 612, 4046): the dome's front half still standing on the
sea floor, purple, its outline the live dome's (columns 9-40 of the picture's rows 28-46), the middle band and its
plate gold down its front, the foot band's ends rising up its sides at the left and the right, but the shell crumpled:
dark folds down it (columns 11, 21 and 33), and holes broken through it under the broken edge, their insides black and
dark red (columns 12-19 of rows 28-34 left of the band, columns 27-31 of rows 28-33 right of it, a round one on the
right lobe, columns 35-39 of rows 31-36); the left band broken in two (a gold streak curving at the upper left, its
lower end by the plate).

Built as polish_coral_sea.wreck_whole() (the shell where the camera still sees it under the broken edge, SHELL_T thick,
its inside, its broken edge and the dark floor; the foot band's front half and right stub, the middle band broken
over the top, the left band, the boss, the window), with the holes cut along their smooth jagged outlines in the
picture's plane as the broken edge is (polish_coral_manta.split_contour; the shell's rim closed round them, the dark
floor seen through them (a dull 0x51), dark red lumps of the inside on it, 0x71 and 0x70, unlit), the folds painted three shades
darker (burnt_material), the left band in two lengths. Cut into the lower pieces in the picture's plane as the live
dome (polish_coral_sea.export_pieces: the cuts capped in the inside's colour, the pieces moved to their sprites'
middles, triangulated, joined).

Coordinates as polish_coral_sea.py's dome (the whole's origin the picture's middle). models.cfg: model
coral_dome_bl_wreck enemies/coral_dome_bl_wreck.glb origin, model coral_dome_br_wreck enemies/coral_dome_br_wreck.glb
origin; wreck t 53 coral_dome_bl_wreck, wreck t 55 coral_dome_br_wreck (drawn with the live sprite lines' options,
yaw=0 height=-4, at the live pieces' places).

Options after "--": --outdir <dir> (default assets/models/enemies), --preview <prefix>, --whole <prefix>.
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
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
import polish_coral_sea as live  # noqa: E402
from polish_coral_manta import split_contour  # noqa: E402
from polish_jaw_gun_wreck import rock, scorch  # noqa: E402
from polish_orb_red import band_split  # noqa: E402

TAN_T = live.TAN_T
# The holes through the shell (picture x, y; radii; how jagged).
HOLES = [((-8.6, -1.4), (5.0, 4.0), 0.35), ((5.8, -1.0), (3.0, 4.0), 0.3), ((13.6, -5.6), (2.4, 2.8), 0.2)]
# Dark red lumps of the inside lying on the floor in the holes: (picture x, y, radius, palette index).
LUMPS = [(-10.2, -1.6, 1.4, 0x71), (-7.0, -3.0, 1.1, 0x70), (-5.6, -0.8, 0.9, 0x71), (5.2, -1.4, 1.0, 0x71),
         (6.0, -3.4, 0.8, 0x70), (13.4, -5.4, 0.9, 0x70)]
# The folds down the shell (picture x, half width) and across its left lobe (picture y, half width, from x, to x).
FOLDS = [(-13.0, 0.9), (-2.2, 0.8), (8.8, 0.9)]
FOLD_ACROSS = (-7.4, 0.7, -20.0, -10.0)
# The left band in two lengths (indices into polish_coral_sea.LEFT_BAND).
LEFT_LENGTHS = [(0, 3), (4, 7)]
PIECES = [("coral_dome_bl_wreck", 53, live.DOME_PIECES[2][2]), ("coral_dome_br_wreck", 55, live.DOME_PIECES[3][2])]


def hole_field(x, yp):
    """Negative inside a hole (picture coordinates), positive outside; jagged as the broken edge (live.jag)."""
    best = 9.0
    for (cx, cy), (rx, ry), amount in HOLES:
        a = math.atan2((yp - cy) / ry, (x - cx) / rx)
        d = math.hypot((x - cx) / rx, (yp - cy) / ry)
        best = min(best, (d - 1.0 - amount * live.jag(3.0 * a + cx)) * min(rx, ry))
    return best


def fold_field(co):
    """How strongly a point (world) lies in a fold: positive in them."""
    x, yp = co.x, co.y + co.z * TAN_T
    v = -1.0
    for fx, half in FOLDS:
        v = max(v, 1.0 - abs(x - fx) / half + 0.3 * math.sin(1.7 * yp + fx))
    fy, half, x0, x1 = FOLD_ACROSS
    if x0 < x < x1:
        v = max(v, 1.0 - abs(yp - fy) / half)
    return v


def wreck_shell(m, segments=128, steps=22):
    """polish_coral_sea.wreck_shell() with the holes: the shell kept under the broken edge and outside the holes (both
    cut along their contours), SHELL_T thick, its rim closed round the edge and the holes; a dark floor inside."""
    bm = bmesh.new()
    rings = []
    for i in range(steps):
        a = (math.pi / 2) * i / steps
        s_ = math.cos(a)
        ring = []
        for j in range(segments):
            x, y = live.ring_point(s_, 2 * math.pi * j / segments)
            ring.append(bm.verts.new((x, y, live.dome_z(x, y) if i else 0.0)))
        rings.append(ring)
    apex = bm.verts.new((live.DOME_C[0], live.DOME_C[1], live.dome_z(*live.DOME_C)))
    for i in range(steps - 1):
        for j in range(segments):
            j2 = (j + 1) % segments
            bm.faces.new((rings[i][j], rings[i][j2], rings[i + 1][j2], rings[i + 1][j]))
    for j in range(segments):
        bm.faces.new((rings[-1][j], rings[-1][(j + 1) % segments], apex))
    vals = {"f": {v: live.break_line(v.co.x) - (v.co.y + v.co.z * TAN_T) for v in bm.verts},
            "h": {v: hole_field(v.co.x, v.co.y + v.co.z * TAN_T) for v in bm.verts}}
    split_contour(bm, vals, "f", 0.0)
    split_contour(bm, vals, "h", 0.0)

    def gone(fc):
        n = len(fc.verts)
        return (sum(vals["f"][v] for v in fc.verts) / n < 0) or (sum(vals["h"][v] for v in fc.verts) / n < 0)
    bmesh.ops.delete(bm, geom=[fc for fc in bm.faces if gone(fc)], context="FACES")
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    outer = list(bm.faces)
    inner_of = {}
    for v in list(bm.verts):
        _, n = live.surface_frame(live.dome_z, v.co.x, v.co.y)
        if v.co.z < 0.05:
            n = Vector((v.co.x - live.DOME_C[0], v.co.y - live.DOME_C[1], 0.0)).normalized()
        p = v.co - n * live.SHELL_T
        p.z = max(p.z, -0.6)
        inner_of[v] = bm.verts.new(p)
    inner = [bm.faces.new([inner_of[v] for v in reversed(fc.verts)]) for fc in outer]
    rim = []
    for e in [e for e in bm.edges if e.is_boundary and all(v in inner_of for v in e.verts)]:
        a_, b_ = e.verts
        rim.append(bm.faces.new((b_, a_, inner_of[a_], inner_of[b_])))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    inside = set(inner) | set(rim)
    mesh = bpy.data.meshes.new("dome_wreck")
    for fc in bm.faces:
        fc.material_index = 1 if fc in inside else 0
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("dome_wreck", mesh)
    bpy.context.scene.collection.objects.link(obj)
    mesh.materials.append(m[0x57])
    mesh.materials.append(m[live.INSIDE])
    k.smooth(obj, 45)
    mesh = obj.data
    nn = live.vertex_normals(mesh)
    lv = live.light(nn) + live.TIE
    is_in = np.zeros(len(mesh.vertices), bool)
    for poly in mesh.polygons:
        if poly.material_index == 1:
            for vi in poly.vertices:
                is_in[vi] = True
    lv = np.where(is_in, -50.0, lv)
    band_split(obj, lv, [(-99.0, m[live.INSIDE])] + [(lo if lo > -99 else -40.0, mt) for lo, mt in
                                                      [(lo_, m[i]) for lo_, i in live.PURPLE]])
    k.smooth(obj, 45)
    pts = []
    for j in range(96):
        x, y = live.ring_point(0.95, 2 * math.pi * j / 96)
        pts.append((x, min(y, live.FLOOR_BACK)))
    # (dull: through the holes it shows dark, not the sky's sheen)
    dull = k.material("coral_dome_floor", palette=live.INSIDE, metallic=0.0, roughness=0.95)
    floor = live.fan_slab("dome_floor", pts, -0.4, 0.25, dull)
    return [obj, floor]


def left_band(m):
    """polish_coral_sea.left_band() in two lengths (the band broken between them)."""
    saved = live.LEFT_BAND
    parts = []
    try:
        for i, (a, b) in enumerate(LEFT_LENGTHS):
            live.LEFT_BAND = saved[a:b]
            part = live.left_band(m)
            part.name = "left_band%d" % i
            parts.append(part)
    finally:
        live.LEFT_BAND = saved
    return parts


def wreck_whole(m):
    keep_foot = lambda phi: math.sin(phi) < -0.05 or (math.cos(phi) > 0.8 and math.sin(phi) < 0.5)  # noqa: E731
    shell = wreck_shell(m)
    parts = shell + [live.foot_band(m, keep=keep_foot), live.middle_band(m, theta1=live.BAND_BREAK)]
    parts += left_band(m) + [live.boss(m)] + live.window(m)
    # The folds down the shell, three shades darker.
    scorch(shell[0], fold_field, levels=(0.0, 9.0))
    k.smooth(shell[0], 45)
    # Dark red lumps of the inside on the floor in the holes (world: the camera sees the floor at its picture place).
    for i, (x, yp, r, index) in enumerate(LUMPS):
        mat = k.material("coral_dome_inside_red", palette=index, metallic=0.0, roughness=0.8)
        parts.append(rock("lump%d" % i, (x, yp - 0.25 * TAN_T, 0.0), (r, r * 0.9, r * 0.7), mat, 4.0 + i, flat=0.0))
    for obj in parts:
        mk.apply(obj)
    return parts


def build():
    options = k.args()
    out = mk.outdir(options)
    k.reset()
    m = live.materials()
    bpy.context.scene.view_settings.view_transform = "Standard"
    live.export_pieces("coral_dome_wreck", wreck_whole(m), PIECES, m[live.INSIDE], (48, 56), options, out, None)


if __name__ == "__main__":
    build()
