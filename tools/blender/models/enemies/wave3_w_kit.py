"""Helpers for the batch W models of wave 3 (sheet P: the asteroid levels ASTEROID1, ASTEROID2, ASTEROID?,
ASTCITY, AST. CITY and AST ROCK; wave3_w.py, the block house and its small doors; wave3_w_works.py, the
works built on the same house: the drilling rig, the bronze pump with its golden dome and the cargo pod;
wave3_w_launcher.py, the tan launcher). The sprites' pixels are in wave3_w_art.py; the parts and the build
loop come from the earlier batches' kits (wave3_s_kit: pixel frames, bevelled slabs and prisms, painting by
the sprite; wave3_n_kit: whole objects cut into their sprites' pieces, the silhouette check; wave3_p_kit:
heightfield beds, chamfered plates; wave3_j_kit: palette materials, turned parts, tubes).

The sheet's ground objects all stand on the asteroid levels' floor (map tile 372, FLOOR in the art), which
their sprites draw round them, with the object's shadow drawn on it below and to the right. The game casts
its own shadows now, so the models lay the floor as it lies in the levels (a thin bed in the floor's
colours, pixel for pixel: it continues the map's floor seamlessly) and leave the drawn shadows out.

Most of them are built on one house: a block 40 x 43 pixels with rounded corners, its roof laid with
raised panels (block_house_*, and under the rig, the pump and the pod).

Coordinates as in tyrkit: 1 unit = 1 game pixel, X right, Y up the screen, Z up (towards the camera);
the origin is the sprite's centre (or the whole object's, for objects the game draws in pieces).
Pixel (column c, row r) of an art with origin (ox, oy) covers x = c - ox .. c + 1 - ox,
y = oy - r - 1 .. oy - r.
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
import tyrkit as k  # noqa: E402,F401
import wave1_d_shapes as sh  # noqa: E402,F401
import wave3_j_kit as w  # noqa: E402,F401
import wave3_n_kit as n  # noqa: E402,F401
import wave3_p_kit as p  # noqa: E402,F401
import wave3_s_kit as s  # noqa: E402,F401
import wave3_w_art as art  # noqa: E402,F401
from wave3_j_kit import (pal, grid, paint_faces, lathe_axis, hoop, tube, catmull, sphere, rounded_box, block,  # noqa: E402,F401
                         meshes, bake)
from wave3_s_kit import Frame, Painter, slab, prism_x, prism_y, paint_sprite, pixelate, merge_flat  # noqa: E402,F401

model = n.model
pieced = n.pieced
run = n.run
merge = n.merge_by_material


# --- The floor -------------------------------------------------------------------------------------

FLOOR = grid(art.FLOOR, 24)


def floor_at(c, r):
    """The floor's palette index under sprite pixel (c, r) (the sprites are laid on the map's grid)."""
    return FLOOR[r % 28][c % 24]


def refill(g, replace):
    """A copy of the grid whose pixels replace(index, column, row) accepts (the floor and the shadows the
    sprite draws on it) show the floor as it lies in the levels."""
    return [[floor_at(c, r) if replace(v, c, r) else v for c, v in enumerate(row)] for r, row in enumerate(g)]


FLOOR_SHADES = (2, 4, 5, 6, 7, 8, 10)


def floor_bed(name, size, keep, origin, top=0.3, prefix="floor", shades=FLOOR_SHADES):
    """The floor as a thin bed over the pixels keep(column, row) of a sprite (or whole object) of `size`
    (width, height) accepts, each pixel the floor's colour there (shades snapped to `shades`): a flat top
    whose like pixels are merged into few faces, its outer edges turned down to the ground (no bottom: the
    camera looks down on it)."""
    wd, h = size
    ox, oy = origin
    mats, index = [], {}
    bm = bmesh.new()
    verts = {}

    def vert(c, r):
        if (c, r) not in verts:
            verts[(c, r)] = bm.verts.new((c - ox, oy - r, top))
        return verts[(c, r)]
    for r in range(h):
        for c in range(wd):
            if not keep(c, r):
                continue
            v = floor_at(c, r)
            shade = min(shades, key=lambda x: abs(x - (v & 15)))
            if shade not in index:
                index[shade] = len(mats)
                mats.append(pal(f"{prefix}_{shade:x}", shade, metallic=0.05, roughness=0.85))
            face = bm.faces.new((vert(c, r + 1), vert(c + 1, r + 1), vert(c + 1, r), vert(c, r)))
            face.material_index = index[shade]
    bm.normal_update()
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(1.0), verts=bm.verts[:], edges=bm.edges[:],
                             delimit={"MATERIAL"})
    bmesh.ops.triangulate(bm, faces=[f_ for f_ in bm.faces if len(f_.verts) > 3], quad_method="BEAUTY",
                          ngon_method="EAR_CLIP")
    # The edges turned down to the ground.
    border = [e for e in bm.edges if len(e.link_faces) == 1]
    if border:
        made = bmesh.ops.extrude_edge_only(bm, edges=border)
        down = [v for v in made["geom"] if isinstance(v, bmesh.types.BMVert)]
        bmesh.ops.translate(bm, verts=down, vec=(0.0, 0.0, -top))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    # The top must face up (recalc may flip an open surface).
    if bm.faces and sum(f_.normal.z * f_.calc_area() for f_ in bm.faces) < 0:
        bmesh.ops.reverse_faces(bm, faces=bm.faces[:])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    for m_ in mats:
        obj.data.materials.append(m_)
    return obj


# --- Outlines --------------------------------------------------------------------------------------

def rrect(x0, x1, y0, y1, radii=(0.0, 0.0, 0.0, 0.0), steps=5):
    """A rectangle with rounded corners, counter-clockwise: radii (bottom-left, bottom-right, top-right,
    top-left)."""
    bl, br, tr, tl = radii
    out = []
    for (cx, cy, r, a0) in ((x0 + bl, y0 + bl, bl, 180), (x1 - br, y0 + br, br, 270),
                            (x1 - tr, y1 - tr, tr, 0), (x0 + tl, y1 - tl, tl, 90)):
        if r <= 1e-6:
            out.append((cx, cy))
            continue
        for i in range(steps + 1):
            a = math.radians(a0 + 90 * i / steps)
            out.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return out


def inside_poly(poly, x, y):
    """Whether (x, y) lies inside the polygon (even-odd rule)."""
    inside = False
    n_ = len(poly)
    for i in range(n_):
        (ax, ay), (bx, by) = poly[i], poly[(i + 1) % n_]
        if (ay > y) != (by > y) and x < ax + (bx - ax) * (y - ay) / (by - ay):
            inside = not inside
    return inside


def greys(prefix, metallic=0.35, roughness=0.5):
    """The grey ramp's shades 1-14 as palette materials."""
    return {v: pal(f"{prefix}_grey{v:x}", v, metallic=metallic, roughness=roughness) for v in range(1, 15)}


# --- The block house -------------------------------------------------------------------------------

HOUSE_HEIGHT = 10.0
# The house's outline in pixels of its sprites (columns 4-42, its top row to 42 rows below it) and its
# corners' radii (bottom-left, bottom-right, top-right, top-left).
HOUSE_COLS = (4, 42)
HOUSE_ROWS = 43
HOUSE_RADII = (5.0, 4.0, 2.4, 2.0)
# The panels laid on its roof (columns, rows from its top row, inclusive; the seams between them are the
# pixels left out), as block_house's sprites draw them. Hatches (the frames sink them) are marked.
HOUSE_PANELS = [
    ("a", 4, 25, 0, 5), ("b", 27, 42, 0, 9), ("c", 4, 10, 7, 19), ("d", 12, 25, 7, 19, "hatch"),
    ("e", 27, 36, 11, 14), ("f", 38, 42, 11, 18, "hatch"), ("g", 27, 36, 16, 25), ("h", 38, 42, 20, 25),
    ("i", 4, 14, 21, 29), ("j", 16, 18, 21, 42), ("k", 20, 25, 21, 25), ("l", 20, 32, 27, 34, "hatch"),
    ("m", 34, 42, 27, 42), ("n", 20, 32, 36, 42), ("o", 4, 14, 31, 42),
]


def house_outline(f, row0):
    x0, x1 = f.left(HOUSE_COLS[0]), f.right(HOUSE_COLS[1])
    y1 = f.top(row0) - 0.05  # off the top piece's edge (the pieces are cut there)
    return rrect(x0, x1, y1 - HOUSE_ROWS, y1, HOUSE_RADII)


def house_mats(prefix):
    g = greys(prefix, metallic=0.3, roughness=0.55)
    return {"roof": g[9], "lit": g[0xb], "shade": g[7], "seam": g[5], "wall": g[7], "gap": g[3], "bolt": g[0xc],
            "grey": g}


def paint_plate(obj, m, top=None):
    """A panel's faces: its top in `top` (the roof's grey), its chamfers lit towards the upper left and
    shaded towards the lower right, its sides as the walls."""
    top = top or m["roof"]

    def pick(c, nrm):
        if nrm.z > 0.95:
            return top
        if nrm.z < -0.5:
            return m["wall"]
        if nrm.z > 0.3:
            return m["lit"] if (nrm.x < -0.25 or nrm.y > 0.25) else m["shade"]
        return m["wall"]
    return paint_faces(obj, pick)


def house(prefix, f, row0, skip=(), hatches=True, height=HOUSE_HEIGHT, m=None, plain=False):
    """The block house standing on the floor: a block with rounded corners and bevelled edges, its top
    row at `row0` of frame f, its roof laid with raised panels with seams between them (panels named in
    `skip` left out, for the works built over them). Hatches: the three panels the frames sink, set a
    little lower in dark gaps (False: plain panels). plain: no panels, a flat roof. Returns (the parts,
    the roof's height)."""
    m = m or house_mats(prefix)
    outline = house_outline(f, row0)
    parts = []
    body = slab(prefix + "_body", outline, 0.0, height, m["wall"], bevel=0.9, segments=3)
    paint_faces(body, lambda c, nrm: (m["roof"] if plain else m["seam"]) if nrm.z > 0.95 else
                (m["lit"] if nrm.z > 0.3 and (nrm.x < -0.25 or nrm.y > 0.25) else
                 m["shade"] if nrm.z > 0.3 else m["wall"]))
    parts.append(body)
    if plain:
        return parts, height
    edge = sh.inset(outline, 1.05)  # the panels keep off the bevel
    for spec in HOUSE_PANELS:
        name, c0, c1, r0, r1 = spec[:5]
        if name in skip:
            continue
        hatch = hatches and len(spec) > 5
        x0, x1 = f.left(c0) + 0.1, f.right(c1) - 0.1
        y0, y1 = f.bottom(row0 + r1) + 0.1, f.top(row0 + r0) - 0.1
        # Panels at the house's edges stop short of its bevel, round where its corners are round.
        ex0, ex1 = min(x for x, _ in edge), max(x for x, _ in edge)
        ey0, ey1 = min(y for _, y in edge), max(y for _, y in edge)
        x0, x1, y0, y1 = max(x0, ex0), min(x1, ex1), max(y0, ey0), min(y1, ey1)
        radii = []
        for (cx, cy), r in zip(((ex0, ey0), (ex1, ey0), (ex1, ey1), (ex0, ey1)), HOUSE_RADII):
            near = abs((x0 if cx == ex0 else x1) - cx) < 0.05 and abs((y0 if cy == ey0 else y1) - cy) < 0.05
            radii.append(r - 1.05 if near else 0.0)
        if hatch:
            # The hatch's dark gap, then the hatch a little lower than the panels round it.
            gap = rrect(x0, x1, y0, y1, radii)
            parts.append(p.chamfered(f"{prefix}_{name}_gap", gap, height - 0.2, height + 0.1, m["gap"], chamfer=0.05))
            plate = rrect(x0 + 0.55, x1 - 0.55, y0 + 0.55, y1 - 0.55, [r - 0.5 if r > 0.9 else 0.0 for r in radii])
            obj = p.chamfered(f"{prefix}_{name}", plate, height - 0.1, height + 0.45, m["roof"], chamfer=0.3)
            paint_plate(obj, m)
            parts.append(obj)
            # Two bolts at its ends.
            cx = (x0 + x1) / 2
            for yb in (y0 + 1.6, y1 - 1.6):
                if y1 - y0 > 5:
                    parts.append(sphere(f"{prefix}_{name}_bolt{yb:.0f}", (cx, yb, height + 0.45), (0.55, 0.45, 0.3),
                                        m["bolt"], 10, 5))
        else:
            obj = p.chamfered(f"{prefix}_{name}", rrect(x0, x1, y0, y1, radii), height - 0.1, height + 0.8,
                              m["roof"], chamfer=0.45)
            paint_plate(obj, m)
            parts.append(obj)
    return parts, height + 0.8


def house_floor(prefix, f, row0, extra=None):
    """The floor round the house (all of the frame's pixels but those under the house; extra(c, r) -> True
    keeps more pixels out)."""
    outline = sh.inset(house_outline(f, row0), 1.0)

    def keep(c, r):
        if extra is not None and extra(c, r):
            return False
        return not inside_poly(outline, f.X(c), f.Y(r))
    return floor_bed(prefix + "_floor", (f.width, len(f.g)), keep, (f.ox, f.oy), prefix=prefix)


# --- Pieces ----------------------------------------------------------------------------------------

def quarter(name, f, c0, r0, check_mask=True):
    """A 24 x 28 piece of a whole object at pixel (c0, r0) of frame f: (piece name, its box in the whole's
    coordinates, its sprite's centre there, its mask for --check)."""
    x0, y1 = f.left(c0), f.top(r0)
    e = 0.01  # faces lying on a piece's edge stay with neither piece
    return (name, (x0 + e, x0 + 24.0 - e, y1 - 28.0 + e, y1 - e), (x0 + 12.0, y1 - 14.0),
            (lambda: f.mask((c0, c0 + 24, r0, r0 + 28))) if check_mask else None)


def rotate_about(objects, axis, angle, pivot):
    """Turns objects by angle (radians) about an axis ('X', 'Y', 'Z') through pivot."""
    m = Matrix.Translation(pivot) @ Matrix.Rotation(angle, 4, axis) @ Matrix.Translation(-Vector(pivot))
    for obj in objects:
        sh.apply_modifiers(obj)
        obj.data.transform(m)
    return objects


def cut_hole(obj, x0, x1, y0, y1, z0, z1):
    """Cuts a box out of a part (a boolean difference): wells, slots, openings."""
    sh.apply_modifiers(obj)
    cutter = k.box(obj.name + "_cutter", ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), (x1 - x0, y1 - y0, z1 - z0),
                   obj.data.materials[0] if obj.data.materials else None)
    mod = obj.modifiers.new("hole", "BOOLEAN")
    mod.operation = "DIFFERENCE"
    mod.object = cutter
    sh.apply_modifiers(obj)
    bpy.data.objects.remove(cutter)
    return obj
