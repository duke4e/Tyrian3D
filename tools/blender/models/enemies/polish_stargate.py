"""STARGATE's glowing red crystal gate (sheet E sprite 199 above sprite 237, 2x2 each: one 24 x 56 picture; ground
layer; enemies 679 and 680 of episode 3, armour 255; not animated), polished (2026-10-19; it replaces wave1_c.py's
stargate_blade(), a relief inflated from the outline with glowing lines laid on). models.cfg: model stargate_top /
stargate_bottom ... origin (unchanged); sprite e 199 stargate_top yaw=0, sprite e 237 stargate_bottom yaw=0. The level
always places the two together: 679 (199) 28 pixels above 680 (237) at the same x (STARGATE's events 100-400 and
1250-1430).

As the sprites and their 4x upscales draw it: a crystal shard lying on the ground, red, glowing from inside, its
outline a pointed arch at the top (rows 1-7 of the picture), straight sides (columns 3-22) and a shield's point at the
bottom (row 54). A white-hot spine runs down it (column 12: white from row 8 to row 19, orange down the middle, yellow
again near the point, rows 46-50); the broad face left of it is dark red and lit only along the rim (column 4, and the
lower left curve, rows 32-45, yellow); the narrow face right of it falls to a slit (columns 14-16 of rows 10-42, open
to the ground) and, beyond it, a narrow strip of the crystal runs down the right side, its rim glowing orange
(column 21). Round the top, two or three pixels inside the outline, a bright line follows the arch (rows 3-7): the
edge of the crystal's termination.

Built as a gem cutter cuts a crystal: a convex solid of flat facets, every facet a plane (polish_crystal_blue.py's
method, solved here with numpy): the girdle (short vertical walls round the outline: the picture's pixels' convex
hull, a little inside); round the sides and the point a steep bezel rising from it (the glowing rim); round the arch
the termination, a band of facets less steep (its edge with the faces ground off into a narrow facet: the bright
line); and the top, two broad faces meeting in the spine along x = RIDGE_X, each turned down near the top (above
TOP_FROM) and near the point (below BOTTOM_FROM); the spine is ground off into a narrow facet (the white-hot line).
The slit and a small notch above it (rows 7-8) are then cut through with exact booleans, their walls dark. The facets
glow in their own colours (emission in their palette colours, stronger for the lighter shades): the broad faces in
bands, brighter towards the spine (the sprite's columns 10-11 and 13); the spine in sections along the crystal and the
rim by the way it faces, as the sprite colours them.

The crystal is built whole and cut along the sprites' edge (y = 0) into its two pieces (as polish_arch.py's cut(),
but every facet keeps its own flat normal: cut_flat()), each moved so its sprite's centre is its origin, its base on
the ground (z = 0; models with origin stand at the ground enemies' layer height, about 4 pixels above the terrain:
height=-4 on the sprite lines would set them on it). Drawn at their places, the pieces meet without a seam.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the ground; the whole's origin
is the point where the two sprites meet (column c of the picture is x = c + 0.5 - 12, row r is y = 27.5 - r).

Replaces wave1_c.py's STARGATE section: remove BLADE_TOP, BLADE_BOTTOM, stargate_blade(), inset_lines() (only
stargate_blade() uses it), stargate_top(), stargate_bottom(), their two MODELS entries and the stargate lines of its
docstring, so that it doesn't overwrite these models.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes of the whole
and of each piece against enemy_E.png), --preview <prefix> (the whole's and each piece's top and 3/4 views),
--only <name,...>.
"""
import itertools
import math
import os
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_crystal_blue import Lin, X, Y, chamfer, over, under, wall  # noqa: E402

# name, sprite, the box it covers in the whole's coordinates (x0, x1, y0, y1)
PIECES = [("stargate_top", 199, (-12.0, 12.0, 0.0, 28.0)), ("stargate_bottom", 237, (-12.0, 12.0, -28.0, 0.0))]

# The outline, counter-clockwise from above: the convex hull of the gate's pixels (their corners); the girdle's walls
# INSET inside it (the hull reaches the stairs' outer corners). Its segments facing up the screen (the arch) carry
# the termination, the others the bezel.
HULL = [(-9, -4), (-8, -10), (-7, -13), (-5, -18), (-1, -26), (0, -27), (1, -27), (3, -25), (8, -15), (9, -12),
        (11, -4), (11, 22), (9, 24), (3, 27), (-1, 27), (-5, 25), (-9, 21)]
INSET = 0.3
GIRDLE_Z, BEZEL_SLOPE = 2.0, 1.5    # the bezel: from the girdle's top, rising this much per pixel inwards
GIRDLE_LOW_Z = 1.2                  # lower round the point's left side: a broader rim there (the yellow curve)
CROWN_Z, CROWN_SLOPE = 1.6, 1.2     # the termination round the arch, likewise
# The top: the spine along x = RIDGE_X at SPINE_Z; the faces fall to EDGE_Z at the outline's sides (x -9 and 11);
# above TOP_FROM the spine falls to APEX_Z at the top (y 27), below BOTTOM_FROM to TIP_Z at the point (y -27).
RIDGE_X, SPINE_Z, EDGE_Z = 0.5, 7.2, 2.9
TOP_FROM, APEX_Z = 18.5, 3.9
BOTTOM_FROM, TIP_Z = -9.0, 2.5
SPINE_W, ARCH_LINE_W, ARCH_RIM_W = 1.0, 0.55, 0.6   # the spine's facet, the arch's bright line and its rim
# The slit (columns 14-16 of rows 10-42: x 4..5 at the top, 3..5 from row 17, 2..5 from row 32, narrowing to its end
# at row 42), its steps smoothed into a curve, and the notch above it (rows 7-8); their corners rounded (Chaikin).
SLIT = [(4.05, 18.1), (3.9, 14.5), (3.35, 10.5), (3.0, 6.0), (2.7, 0.0), (2.2, -4.5), (2.0, -9.0), (2.05, -12.5),
        (2.45, -14.6), (2.95, -15.1), (3.5, -14.6), (4.1, -12.8), (4.75, -10.2), (5.0, -6.0), (5.0, 15.0),
        (4.85, 17.6), (4.5, 18.4)]
NOTCH = [(4.0, 21.0), (4.0, 20.0), (5.0, 20.0), (5.0, 19.0), (6.0, 19.0), (6.0, 21.0)]

# Colours (palette indices). The broad faces in bands by their distance from the spine: within the first, the second,
# beyond.
FACE_BANDS = [(1.3, 0x77), (2.4, 0x74), (99.0, 0x72)]
# The spine's sections along y (from, colour): white-hot rows 8-19, cooler to the top and down the middle, hot again
# near the point.
SPINE = [(-99.0, 0x79), (-24.0, 0x7d), (-16.0, 0x7a), (-14.5, 0x78), (2.0, 0x7a), (7.5, 0x7f), (20.5, 0x7b)]
# The rim (bezel) by the way it faces: the lit left side and its lower curve brightest; the termination and its line.
RIM_LEFT, RIM_LOW_LEFT, RIM_RIGHT, RIM_LOW_RIGHT = 0x79, 0x7a, 0x76, 0x74
CROWN, ARCH_LINE, ARCH_RIM, WALL, SLIT_WALL = 0x74, 0x79, 0x77, 0x71, 0x40
FACE, SPINE_ROLE = 1, 2              # the facets' roles (a face attribute), for painting them in bands
# How strongly each shade glows (emission in its own colour): the lighter, the stronger.
STRENGTH = {0x71: 0.35, 0x72: 0.55, 0x74: 0.75, 0x76: 0.95, 0x77: 1.05, 0x78: 1.15, 0x79: 1.3, 0x7a: 1.45,
            0x7b: 1.6, 0x7d: 1.9, 0x7f: 2.2}


def materials():
    """{palette index: material}: the crystal's shades, each glowing in its own colour; the slit's walls dark."""
    glow = k.level_palette()
    m = {}
    for index, strength in STRENGTH.items():
        m[index] = k.material(f"gate_{index:x}", palette=index, metallic=0.15, roughness=0.18, emission=glow[index],
                              emission_strength=strength)
    m[SLIT_WALL] = k.material("gate_slit", palette=SLIT_WALL, metallic=0.0, roughness=0.9)
    return m


# --- A convex solid of planes (polish_crystal_blue.solid, vectorised) ------------------------------------------------

def convex(planes, eps=1e-7):
    """The convex solid where every half-space (unit normal, d: n . p <= d) holds: its points and its faces (point
    indices, counter-clockwise seen from outside) with the index of the plane each lies on."""
    N = np.array([p[0] for p in planes], float)
    D = np.array([p[1] for p in planes], float)
    triples = np.array(list(itertools.combinations(range(len(planes)), 3)))
    A = N[triples]
    keep = np.abs(np.linalg.det(A)) > 1e-9
    A, b = A[keep], D[triples[keep]]
    P = np.linalg.solve(A, b[..., None])[..., 0]
    P = P[(P @ N.T <= D + eps).all(axis=1)]
    points = []
    for p in P:
        if not any(np.linalg.norm(p - q) < 1e-6 for q in points):
            points.append(p)
    points = np.array(points)
    faces, owners = [], []
    for m in range(len(planes)):
        on = np.nonzero(np.abs(points @ N[m] - D[m]) < 1e-6)[0]
        if len(on) < 3:
            continue
        centre = points[on].mean(axis=0)
        u = points[on[0]] - centre
        u /= np.linalg.norm(u)
        w = np.cross(N[m], u)
        rel = points[on] - centre
        order = on[np.argsort(np.arctan2(rel @ w, rel @ u))]
        loop = []
        for i, idx in enumerate(order):
            a, c = points[order[i - 1]], points[order[(i + 1) % len(order)]]
            if np.linalg.norm(np.cross(points[idx] - a, c - points[idx])) > 1e-9:
                loop.append(int(idx))
        if len(loop) >= 3:
            faces.append(loop)
            owners.append(m)
    return points, faces, owners


def meeting(planes, points, a, b, min_length=0.05):
    """Whether the planes a and b meet in an edge of the solid (two of its points on both, apart)."""
    on = []
    for i in (a, b):
        n, d = planes[i]
        on.append({j for j, p in enumerate(points) if abs(float(np.dot(n, p)) - d) < 1e-6})
    common = [points[j] for j in on[0] & on[1]]
    return len(common) >= 2 and max(float(np.linalg.norm(p - q)) for p in common for q in common) >= min_length


# --- The crystal -----------------------------------------------------------------------------------------------------

def tops():
    """The top's facets as functions z = f(x, y): {name: Lin}."""
    a_left = (SPINE_Z - EDGE_Z) / (RIDGE_X + 9.0)
    a_right = (SPINE_Z - EDGE_Z) / (11.0 - RIDGE_X)
    left = Lin(SPINE_Z) + a_left * X(-RIDGE_X)
    right = Lin(SPINE_Z) - a_right * X(-RIDGE_X)
    b_top = (SPINE_Z - APEX_Z) / (27.0 - TOP_FROM)
    b_bottom = (SPINE_Z - TIP_Z) / (BOTTOM_FROM + 27.0)
    return {"left": left, "right": right, "left_top": left - b_top * Y(-TOP_FROM),
            "right_top": right - b_top * Y(-TOP_FROM), "left_low": left + b_bottom * Y(-BOTTOM_FROM),
            "right_low": right + b_bottom * Y(-BOTTOM_FROM)}


def rim_colour(nx, ny, y):
    """The bezel's colour for a facet facing (nx, ny) in the top view, at y."""
    low = ny < -0.15 and y < -2.0
    if nx < 0:
        return RIM_LOW_LEFT if low else RIM_LEFT
    return RIM_LOW_RIGHT if low else RIM_RIGHT


def crystal(m):
    """The convex crystal: its facets solved from their planes, the spine and the arch's line ground off; each facet
    in its colour (the broad faces in FACE_BANDS' last for now)."""
    planes, colours = [over(Lin(0.0))], [WALL]
    crowns = []
    for p, q in zip(HULL, HULL[1:] + HULL[:1]):
        nx, ny = q[1] - p[1], -(q[0] - p[0])
        length = math.hypot(nx, ny)
        nx, ny = nx / length, ny / length
        d = nx * p[0] + ny * p[1] - INSET
        planes.append(wall(nx, ny, d))
        colours.append(WALL)
        if ny > 0.35:  # the arch: the termination
            crowns.append(len(planes))
            planes.append(under(Lin(CROWN_Z + CROWN_SLOPE * d, -CROWN_SLOPE * nx, -CROWN_SLOPE * ny)))
            colours.append(CROWN)
        else:
            colour = rim_colour(nx, ny, (p[1] + q[1]) / 2)
            girdle = GIRDLE_LOW_Z if colour == RIM_LOW_LEFT else GIRDLE_Z
            planes.append(under(Lin(girdle + BEZEL_SLOPE * d, -BEZEL_SLOPE * nx, -BEZEL_SLOPE * ny)))
            colours.append(colour)
    index, roles = {}, {}
    for name, f in tops().items():
        index[name] = len(planes)
        roles[len(planes)] = FACE
        planes.append(under(f))
        colours.append(FACE_BANDS[-1][1])
    points, _, _ = convex(planes)
    extra = []
    for a, b in (("left", "right"), ("left_top", "right_top"), ("left_low", "right_low")):
        if meeting(planes, points, index[a], index[b]):
            extra.append((chamfer(planes[index[a]], planes[index[b]], SPINE_W), SPINE[0][1], SPINE_ROLE))
    for c in crowns:
        for name in ("left_top", "right_top", "left", "right"):
            if meeting(planes, points, c, index[name]):
                extra.append((chamfer(planes[c], planes[index[name]], ARCH_LINE_W), ARCH_LINE, 0))
        if meeting(planes, points, c - 1, c):  # the girdle's top edge round the arch: the outer line
            extra.append((chamfer(planes[c - 1], planes[c], ARCH_RIM_W), ARCH_RIM, 0))
    for plane, colour, role in extra:
        if role:
            roles[len(planes)] = role
        planes.append(plane)
        colours.append(colour)
    points, faces, owners = convex(planes)
    obj = k.mesh_object("crystal", [tuple(p) for p in points], faces)
    used = sorted({colours[o] for o in owners})
    for colour in used:
        obj.data.materials.append(m[colour])
    role = obj.data.attributes.new("role", "INT", "FACE")
    for poly, owner in zip(obj.data.polygons, owners):
        poly.material_index = used.index(colours[owner])
        poly.use_smooth = False
        role.data[poly.index].value = roles.get(owner, 0)
    return obj


def holes(m):
    """The slit and the notch, to cut through the crystal; their walls dark."""
    return [mk.prism(name, mk.chaikin(outline, 2), -1.0, SPINE_Z + 4.0, m[SLIT_WALL])
            for name, outline in (("slit", SLIT), ("notch", NOTCH))]


def bands(obj, m):
    """The broad faces in bands by their distance from the spine, the spine in sections along y: their facets (by
    their role) are cut along those lines (bisected), then painted."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    layer = bm.faces.layers.int.get("role")
    cuts = [((RIDGE_X + side * limit, 0, 0), (1, 0, 0), FACE) for limit, _ in FACE_BANDS[:-1] for side in (-1, 1)]
    cuts += [((0, y, 0), (0, 1, 0), SPINE_ROLE) for y, _ in SPINE[1:]]
    for co, no, role in cuts:
        faces = [f for f in bm.faces if f[layer] == role]
        geom = list({v for f in faces for v in f.verts}) + list({e for f in faces for e in f.edges}) + faces
        bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-5, plane_co=co, plane_no=no)
    for f in bm.faces:
        centre = f.calc_center_median()
        if f[layer] == FACE:
            dist = abs(centre.x - RIDGE_X)
            colour = next(c for limit, c in FACE_BANDS if dist < limit)
        elif f[layer] == SPINE_ROLE:
            colour = SPINE[0][1]
            for y, c in SPINE:
                if centre.y > y:
                    colour = c
        else:
            continue
        f.material_index = mk.slot_of(obj, m[colour])
    bm.to_mesh(obj.data)
    bm.free()


def cut_flat(source, box_xy, cap_mat):
    """The part of a flat-shaded object inside box (x0, x1, y0, y1), its cuts closed with flat caps of cap_mat
    (polish_arch.cut() without taking the normals from the uncut object: every facet is flat, its normal its own;
    near the slit's sharp edges that lookup took the walls' normals for the faces' corners). None if nothing of the
    object is inside the box."""
    x0, x1, y0, y1 = box_xy
    obj = source.copy()
    obj.data = source.data.copy()
    bpy.context.scene.collection.objects.link(obj)
    cap_index = mk.slot_of(obj, cap_mat)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    for co, no in (((x0, 0, 0), (-1, 0, 0)), ((x1, 0, 0), (1, 0, 0)), ((0, y0, 0), (0, -1, 0)), ((0, y1, 0), (0, 1, 0))):
        if not bm.faces:
            break
        result = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-6, plane_co=co,
                                        plane_no=no, clear_outer=True)
        edges = [e for e in result["geom_cut"] if isinstance(e, bmesh.types.BMEdge) and e.is_valid]
        open_edges = [e for e in edges if len(e.link_faces) == 1]
        if open_edges:
            filled = bmesh.ops.holes_fill(bm, edges=open_edges, sides=0)
            for f in bmesh.ops.triangulate(bm, faces=filled["faces"])["faces"]:
                f.material_index = cap_index
    if not bm.faces:
        bm.free()
        bpy.data.objects.remove(obj)
        return None
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:
        f.smooth = False
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def build_whole(m):
    obj = crystal(m)
    bands(obj, m)
    obj.data.attributes.remove(obj.data.attributes["role"])  # only for painting; not exported
    mk.boolean(obj, holes(m), "DIFFERENCE")
    mk.cleanup(obj, dissolve=0.0)
    for poly in obj.data.polygons:
        poly.use_smooth = False
    return [obj]


def build():
    options = k.args()
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    k.reset()
    m = materials()
    whole = build_whole(m)
    print("whole gate: %d triangles, %d materials" % (mk.triangles(whole), len(mk.materials_of(whole))))
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    sheet = os.path.join(options["check"], "enemy_E.png") if "check" in options else None
    if sheet:
        mk.compare("whole (E 199 above E 237)", mk.coverage(whole, 24, 56),
                   k.sprite_mask(sheet, 199) + k.sprite_mask(sheet, 237))
    if "preview" in options:
        mk.preview(options["preview"] + "stargate_whole", whole, size=(24, 56), scale=8, distance=1.8)
    for name, sprite, box in PIECES:
        if only and name not in only:
            continue
        pieces = [p for p in (cut_flat(src, box, m[WALL]) for src in whole) if p is not None]
        mk.transform(pieces, Matrix.Translation((0.0, -(box[2] + box[3]) / 2, 0.0)))
        bpy.context.view_layer.update()
        for src in whole:
            src.hide_render = True
        if sheet:
            mk.compare("%s (E %d)" % (name, sprite), mk.coverage(pieces, 24, 28), k.sprite_mask(sheet, sprite))
        mk.report(name, pieces, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, pieces)
        for obj in pieces:
            bpy.data.objects.remove(obj)
        for src in whole:
            src.hide_render = False


if __name__ == "__main__":
    build()
