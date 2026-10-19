"""Episode 1's purple and grey arch (sheet 2 sprites 49, the left half, and 51, the right half, 2x2 each: 24 x 28
pixels; TYRIAN, HOLES, ASSASSIN, TYRIAN X, SAVARA (episode 5); top, sky and ground layers; enemies 26 + 27 and
28 + 29), polished (2026-10-19; it replaces wave2_f_more.py's arch_whole(), arch_left() and arch_right(), arms
inflated from the outline with flat plates laid on). models.cfg: model arch_left / arch_right ... origin; sprite 2
49 arch_left yaw=0, sprite 2 51 arch_right yaw=0. The levels place the halves as one 48 x 28 picture: 49 at x and
51 at x + 24, at the same y (TYRIAN's events 1568-1938 and 2100-2330, HOLES' 463-1863, TYRIAN X's 1568-1938);
only ASSASSIN stacks lone left halves (enemy 26) down the screen.

As the sprites draw it (the 4x upscales, made half by half, don't join): a ship like an arch over a small hub.
From the hub's top a grey band sweeps out either side (rows 0-4), a purple plate on it next to the middle (columns
17-21 and 26-30), and bends down into broad outer plates (columns 2-9 and 38-45 of rows 9-26) that taper to points
at the bottom; each outer plate carries two purple panels split by a grey stripe running down and out (rows 10-17
and 18-24), lit on the left half and dark on the right, as plates sloping down to the outside are under the sun
from the upper left. Under the band's middle the hub: a grey block either side (columns 13-17, rows 5-8) braced to
two pylons by the middle (columns 21-22 and 25-26), a thin link between them (rows 6-7); down the pylons thin rods
(rows 9-11) to two housings with bright edges (rows 12-17) and, below them, two red nozzles pointing down the screen
(columns 20-21 and 26-27, rows 18-23), glowing.

The arch is built whole about x = 0 (the edge between the two sprites; the picture is symmetric about it), as a
CAD modeller would: the wings are prisms of their plan, cut by the planes of their top (the band level, the outer
plates sloping down outwards and towards their points) with exact booleans, their edges bevelled, flat faces kept
flat; the purple panels are thin plates on those planes; the hub is boxes and the nozzles lathed. It is then cut
along x = 0 (polish_redjet.py's method, cut() below): each half keeps the whole's shading across the cut, so that
drawn at their own places the halves meet without a seam; each is moved so its sprite's centre is its origin (base on
the layer: models.cfg origin).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; column c of
the 48 x 28 picture is x = c + 0.5 - 24, row r is y = 13.5 - r; the arch's bottom at z = 0.

Replaces wave2_f_more.py's arch: remove ARCH, ARCH_PLATES, arch_whole(), arch_left(), arch_right() and the "arch"
entry of WHOLE, so that it doesn't overwrite these models.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes of the
whole and of each half against enemy_2.png), --preview <prefix> (the whole's and each half's top and 3/4 views).
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

# name, sprite, the box it covers in the whole's coordinates (x0, x1, y0, y1)
PIECES = [("arch_left", 49, (-24.0, 0.0, -14.0, 14.0)), ("arch_right", 51, (0.0, 24.0, -14.0, 14.0))]


def P(c, r):
    """A point of the 48 x 28 picture (pixel edges: c, r) in the whole's coordinates."""
    return (c - 24.0, 14.0 - r)


# The left wing's plan, round from the band's right end (pixel edges of the picture).
WING = [P(22.3, 1.7), P(21.4, 0.55), P(12.0, 0.45), P(10.0, 0.9), P(8.0, 1.8), P(6.2, 2.8), P(5.0, 4.0),
        P(4.8, 8.0), P(3.5, 9.0), P(2.45, 10.1), P(2.45, 25.4), P(3.0, 26.55), P(4.1, 26.1), P(5.4, 24.6),
        P(7.4, 22.4), P(9.55, 20.0), P(9.55, 14.2), P(14.6, 9.1), P(14.8, 4.7), P(22.3, 4.7)]
BAND_TOP = 5.2              # the band's top
# The outer plate's top: down outwards (z = BAND_TOP at x = PLATE_HINGE, PLATE_SLOPE per pixel) and towards its
# point (z = TIP_Z0 at y = TIP_Y0, TIP_SLOPE per pixel down the screen).
PLATE_HINGE, PLATE_SLOPE = -10.8, 0.36
TIP_Y0, TIP_Z0, TIP_SLOPE = -1.5, 4.5, 0.17
# The purple panels (picture pixel edges), each on the wing's top, PANEL_PROUD above it.
PANELS = [
    [P(17.0, 1.25), P(21.55, 1.25), P(21.55, 3.95), P(17.0, 3.95)],
    [P(3.05, 10.15), P(9.95, 10.15), P(9.95, 11.9), P(8.4, 14.5), P(5.0, 17.85), P(3.05, 17.85)],
    [P(7.0, 18.2), P(8.1, 18.2), P(8.1, 20.8), P(6.0, 23.5), P(5.0, 24.95), P(3.05, 24.95), P(3.05, 23.0),
     P(4.0, 21.0), P(5.0, 20.0)],
]
PANEL_PROUD = 0.22
# The hub (left half; mirrored): the block under the band (x0, x1, y0, y1, z0, z1), the brace to the pylon, the
# pylon's top block, the link between the pylons, the rod down to the housing, the housing.
HUB_BLOCK = (P(12.9, 0)[0], P(18.1, 0)[0], P(0, 8.6)[1], P(0, 4.5)[1], 0.6, 3.7)
BRACE = (P(17.8, 0)[0], P(21.2, 0)[0], P(0, 7.3)[1], P(0, 5.9)[1], 1.5, 2.9)
PYLON = (P(20.9, 0)[0], P(23.15, 0)[0], P(0, 9.3)[1], P(0, 4.6)[1], 0.9, 3.6)
LINK = (P(22.8, 0)[0], 0.0, P(0, 7.6)[1], P(0, 5.8)[1], 1.6, 2.8)
ROD = (P(21.0, 0)[0] + 0.5, P(0, 12.3)[1], P(0, 9.0)[1], 2.2, 0.55)     # x, y0, y1, z, radius
HOUSING = (P(18.9, 0)[0], P(23.1, 0)[0], P(0, 17.6)[1], P(0, 12.2)[1], 0.5, 3.9)
# The red nozzle: its axis (x, z), from the housing's front (y0) to its tip (y1), radius.
NOZZLE = (P(21.0, 0)[0], 2.2, P(0, 17.4)[1], P(0, 23.7)[1], 1.05)


def cut(source, box_xy, cap_mat):
    """polish_machine_kit.cut (the part of an object inside a box (x0, x1, y0, y1), its cuts capped with cap_mat,
    its normals the uncut object's), without its last step: dropping the materials no face uses any more shifted
    the faces' material indices twice (Blender's materials.pop shifts them itself), which gave the caps, and could
    give other faces, the wrong material. Unused material slots export nothing; they are left. None if nothing of
    the object is inside the box."""
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
                caps |= set(bmesh.ops.triangulate(bm, faces=filled["faces"])["faces"])
    caps = {f for f in caps if f.is_valid}
    if not bm.faces:
        bm.free()
        bpy.data.objects.remove(obj)
        return None
    for f in caps:
        f.material_index = cap_index
        f.smooth = False
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
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


def plane_box(name, top, size=60.0):
    """Everything under the plane z = top(x, y) (a thick slab along it), for intersecting with."""
    s = size
    return mk.wedge(name, [(-s, -s), (s, -s), (s, s), (-s, s)], 0.0, top, bottom=lambda x, y: top(x, y) - 400.0)


def wing_top(x, y):
    """The wing's top height at (x, y): the band's level, the outer plate's slopes."""
    z = BAND_TOP
    z = min(z, BAND_TOP + PLATE_SLOPE * (x - PLATE_HINGE))
    z = min(z, TIP_Z0 + TIP_SLOPE * (y - TIP_Y0))
    return z


def wing(m):
    """The left wing: its plan as a prism, cut by its top's planes, its edges bevelled."""
    body = mk.prism("wing", WING, 0.0, BAND_TOP + 3.0, m["hull"])
    planes = [lambda x, y: BAND_TOP + 0.0 * x,
              lambda x, y: BAND_TOP + PLATE_SLOPE * (x - PLATE_HINGE),
              lambda x, y: TIP_Z0 + TIP_SLOPE * (y - TIP_Y0)]
    for i, top in enumerate(planes):
        mk.boolean(body, plane_box(f"plane{i}", top), "INTERSECT")
    mk.cleanup(body)
    mk.bevel(body, 0.42, 3, 28)
    mk.shade(body, 35)
    mk.paint(body, lambda c, n: m["hull_top"] if n.z > 0.85 else None)
    return body


def panels(m):
    for i, outline in enumerate(PANELS):
        # The panel's top: the wing's top under it (its own plane), PANEL_PROUD above.
        cx = sum(p[0] for p in outline) / len(outline)
        cy = sum(p[1] for p in outline) / len(outline)
        # The plane of the wing's top at the panel (from its middle's slopes).
        e = 0.01
        z0 = wing_top(cx, cy)
        dzx = (wing_top(cx + e, cy) - z0) / e
        dzy = (wing_top(cx, cy + e) - z0) / e
        top = (lambda z0, dzx, dzy, cx, cy: lambda x, y: z0 + dzx * (x - cx) + dzy * (y - cy) + PANEL_PROUD)(
            z0, dzx, dzy, cx, cy)
        bottom = (lambda f: lambda x, y: f(x, y) - 0.6)(top)
        plate = mk.wedge(f"panel{i}", outline, 0.0, top, m["panel"], bottom=bottom)
        mk.bevel(plate, 0.16, 2, 30)
        mk.shade(plate, 35)
        mk.paint(plate, lambda c, n: m["panel_edge"] if n.z < 0.6 else None)


def hub(m):
    """The left half of the hub: the block under the band, the brace to the pylon, the pylon's block, half the
    link between the pylons, the rod down to the housing, the housing and its red nozzle."""
    for name, (x0, x1, y0, y1, z0, z1), mat, bev in (("hub_block", HUB_BLOCK, "hub", 0.35),
                                                     ("brace", BRACE, "hub", 0.25), ("pylon", PYLON, "pylon", 0.3),
                                                     ("link", LINK, "dark", 0.2), ("housing", HOUSING, "pylon", 0.38)):
        part = mk.box(name, x0, x1, y0, y1, z0, z1, m[mat])
        mk.bevel(part, bev, 2, 35)
        mk.shade(part, 35)
        mk.paint(part, lambda c, n, mat=mat: m[mat + "_top"] if n.z > 0.85 and (mat + "_top") in m else None)
    x, y0, y1, z, r = ROD
    rings = [[Vector((x + r * math.cos(2 * math.pi * j / 12), y, z + r * math.sin(2 * math.pi * j / 12)))
              for j in range(12)] for y in (y0, y1)]
    k.smooth(k.loft("rod", rings, m["pylon"]), 50)
    # A bright edge strip along the housing's inner top (the sprite's light column 22, rows 13-15).
    hx0, hx1, hy0, hy1, hz0, hz1 = HOUSING
    strip = mk.box("housing_strip", hx1 - 1.0, hx1 - 0.35, hy0 + 1.2, hy1 - 0.9, hz1 - 0.1, hz1 + 0.18, m["light"])
    mk.bevel(strip, 0.08, 1, 35)
    # The nozzle: a collar at the housing, the red body tapering to a rounded glowing tip.
    nx, nz, ny0, ny1, nr = NOZZLE
    profile = [(ny0 + 0.4, 0.0), (ny0 + 0.4, nr + 0.18), (ny0 - 0.4, nr + 0.18), (ny0 - 0.5, nr),
               (ny1 + 1.6, nr * 0.95)]
    for i in range(1, 6):
        a = (math.pi / 2) * i / 6
        profile.append((ny1 + 1.6 * (1 - math.sin(a)), nr * 0.95 * math.cos(a) + 0.05))
    rings = [[Vector((nx + rr * math.cos(2 * math.pi * j / 18), yy, nz + rr * math.sin(2 * math.pi * j / 18)))
              for j in range(18)] for yy, rr in profile if rr > 0]
    nozzle = k.loft("nozzle", rings, m["red"], end_point=(nx, ny1, nz))
    mk.paint(nozzle, lambda c, n: m["collar"] if c.y > ny0 - 0.55 else m["red_hot"] if c.y < ny1 + 1.2 else None)
    k.smooth(nozzle, 50)


def materials():
    glow = k.level_palette()
    return {
        "hull": k.material("arch_hull", palette=0x06, metallic=0.35, roughness=0.45),
        "hull_top": k.material("arch_hull_top", palette=0x07, metallic=0.35, roughness=0.42),
        "panel": k.material("arch_panel", palette=0x59, metallic=0.3, roughness=0.4),
        "panel_edge": k.material("arch_panel_edge", palette=0x55, metallic=0.3, roughness=0.45),
        "hub": k.material("arch_hub", palette=0x06, metallic=0.55, roughness=0.32),
        "hub_top": k.material("arch_hub_top", palette=0x07, metallic=0.55, roughness=0.3),
        "pylon": k.material("arch_pylon", palette=0x07, metallic=0.6, roughness=0.28),
        "pylon_top": k.material("arch_pylon_top", palette=0x09, metallic=0.6, roughness=0.25),
        "light": k.material("arch_light", palette=0x6e, metallic=0.5, roughness=0.2),
        "dark": k.material("arch_dark", palette=0x03, metallic=0.4, roughness=0.5),
        "collar": k.material("arch_collar", palette=0x04, metallic=0.6, roughness=0.35),
        "red": k.material("arch_red", palette=0x74, metallic=0.1, roughness=0.3, emission=glow[0x74],
                          emission_strength=0.6),
        "red_hot": k.material("arch_red_hot", palette=0x77, metallic=0.0, roughness=0.25, emission=glow[0x77],
                              emission_strength=1.4),
        "seam": k.material("arch_seam", palette=0x03, metallic=0.4, roughness=0.5),
    }


def whole_mask(sheet):
    mask = [[False] * 48 for _ in range(28)]
    for sprite, c0 in ((49, 0), (51, 24)):
        part = k.sprite_mask(sheet, sprite)
        for y in range(28):
            for x in range(24):
                if part[y][x]:
                    mask[y][c0 + x] = True
    return mask


def build():
    k.reset()
    options = k.args()
    m = materials()
    wing(m)
    panels(m)
    hub(m)
    left = mk.meshes()
    for obj in left:
        k.mirror_x(obj, obj.name + "_r")
    whole = mk.meshes()
    for obj in whole:
        mk.apply(obj)
    print("whole arch: %d triangles, %d objects" % (mk.triangles(whole), len(whole)))
    sheet = os.path.join(options["check"], "enemy_2.png") if "check" in options else None
    if sheet:
        mk.compare("whole (2 49 + 51)", mk.coverage(whole, 48, 28), whole_mask(sheet))
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    if "preview" in options:
        mk.preview(options["preview"] + "arch_whole", whole, size=(48, 28), scale=8, distance=1.6)
    out = mk.outdir(options)
    for name, sprite, box in PIECES:
        pieces = [p for p in (cut(src, box, m["seam"]) for src in whole) if p is not None]
        shift = Matrix.Translation((-(box[0] + box[1]) / 2, -(box[2] + box[3]) / 2, 0))
        mk.transform(pieces, shift)
        bpy.context.view_layer.update()
        for src in whole:
            src.hide_render = True
        if sheet:
            mk.compare("%s (2 %d)" % (name, sprite), mk.coverage(pieces, 24, 28), k.sprite_mask(sheet, sprite))
        mk.report(name, pieces, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, pieces)
        for obj in pieces:
            bpy.data.objects.remove(obj)
        for src in whole:
            src.hide_render = False


if __name__ == "__main__":
    build()
