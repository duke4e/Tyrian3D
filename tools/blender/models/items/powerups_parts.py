"""Shared parts of the power-up models (tools/blender/models/items/powerups.py builds them).

The power-ups sheet's rear weapon and sidekick pick-ups are one orb, drawn in the colour of
its kind (flesh red: rear weapons, green: sidekicks; the front weapons' ice-blue orbs and the dual
MegaLaser's brown one are polish_powerups_front.py's and polish_powerups_specials.py's), with the weapon's
symbol in front. Here the orb is a glossy panelled ball, slightly
squashed and flattened on top, and each symbol a raised emblem or small 3D object resting on it.

The orb spans the sprite's columns 2-21 and rows 3-23: centre (0, 0.5), radii 10.3 by 10.5.
Every orb sprite draws the same panel pattern in its ramp: a cross of grooves through the middle
(column 11 and row 13) and lighter panel edges, which the ball takes as grooves and seams.

Symbols are placed with the sprite's pixel coordinates (px, py: the centre of a column and a
row), and emblems are built from the sprite's own pixels: ICON maps (one character per pixel:
'.' the orb or nothing, 'o' a dark outline pixel (shade 0 or 1), 'y' a bright red-to-yellow
pixel (ramp 7, shades 10-15), otherwise the pixel's ramp as a hex digit, from the indices
tools/blender/sprite_profile.py lists) give the outline of each layer, smoothed.

The previews (powerups.py --preview) use Blender's Standard view transform: the game clamps
bright colours rather than tone-mapping them, so glowing parts keep their colour.
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
import tyrkit as k  # noqa: E402

# --- The orb -----------------------------------------------------------------------------------

ORB_X, ORB_Y = 0.0, 0.5
ORB_RX, ORB_RY, ORB_RZ = 10.3, 10.5, 6.6
ORB_POWER = 2.5      # profile of the upper half: 2 a sphere, higher flatter on top
GROOVE_X, GROOVE_Y = -0.5, 0.5   # the sprite's cross of grooves (column 11, row 13)

RAMP_RED, RAMP_GREEN = 4, 2


def px(col):
    """The centre of a sprite column (of a 2x2 sprite) in model units."""
    return col + 0.5 - 12


def py(row):
    """The centre of a sprite row in model units."""
    return 14 - (row + 0.5)


def _rho(x, y):
    dx, dy = (x - ORB_X) / ORB_RX, (y - ORB_Y) / ORB_RY
    return math.sqrt(dx * dx + dy * dy)


def surf(x, y, floor=0.0):
    """Height of the orb's top at (x, y) (floor beyond its edge)."""
    r = _rho(x, y)
    if r >= 1:
        return floor
    return max(floor, ORB_RZ * (1 - r ** ORB_POWER) ** (1 / ORB_POWER))


def _profile(t):
    """The orb's profile at parameter t (0 the top pole, pi the bottom one): (radius factor, z)."""
    s, c = math.sin(t), math.cos(t)
    rho = abs(s) ** (2 / ORB_POWER)
    z = math.copysign(abs(c) ** (2 / ORB_POWER), c)
    # The lower half is shallower (the camera hardly sees it).
    return rho, z * (ORB_RZ if c >= 0 else ORB_RZ * 0.8)


def orb_point(azimuth, t, inset=0.0):
    rho, z = _profile(t)
    p = Vector((ORB_X + ORB_RX * rho * math.cos(azimuth), ORB_Y + ORB_RY * rho * math.sin(azimuth), z))
    if inset:
        p -= orb_normal(p) * inset
    return p


def orb_normal(p):
    """Approximate outward normal of the orb at point p."""
    dx, dy = (p.x - ORB_X) / ORB_RX, (p.y - ORB_Y) / ORB_RY
    zr = ORB_RZ if p.z >= 0 else ORB_RZ * 0.8
    dz = p.z / zr
    pw = ORB_POWER if p.z >= 0 else 2.0
    r = math.sqrt(dx * dx + dy * dy)
    # Gradient of rho^p + |z|^p (in scaled coordinates).
    g_r = pw * r ** (pw - 1) if r > 1e-6 else 0.0
    g_z = pw * abs(dz) ** (pw - 1) * math.copysign(1, dz)
    gx = g_r * (dx / r if r > 1e-6 else 0) / ORB_RX
    gy = g_r * (dy / r if r > 1e-6 else 0) / ORB_RY
    gz = g_z / zr
    n = Vector((gx, gy, gz))
    return n.normalized() if n.length > 1e-9 else Vector((0, 0, 1))


def orb_shell(name, mat, segments=64, rings=32):
    verts, faces = [], []
    top = len(verts)
    verts.append((ORB_X, ORB_Y, ORB_RZ))
    for i in range(1, rings):
        t = math.pi * i / rings
        for j in range(segments):
            verts.append(tuple(orb_point(2 * math.pi * j / segments, t)))
    bottom = len(verts)
    verts.append((ORB_X, ORB_Y, -ORB_RZ * 0.8))
    for j in range(segments):
        faces.append((top, 1 + j, 1 + (j + 1) % segments))
    for i in range(rings - 2):
        a, b = 1 + i * segments, 1 + (i + 1) * segments
        for j in range(segments):
            faces.append((a + j, b + j, b + (j + 1) % segments, a + (j + 1) % segments))
    last = 1 + (rings - 2) * segments
    for j in range(segments):
        faces.append((last + (j + 1) % segments, last + j, bottom))
    obj = k.mesh_object(name, verts, faces, mat)
    k.recalc_normals(obj)
    return k.smooth(obj, 80)


def tube(name, points, radius, mat, segments=8, closed=False, radii=None, caps=True):
    """A tube along a path of points (Vectors); radii: one radius per point (taper)."""
    pts = [Vector(p) for p in points]
    n = len(pts)
    rings = []
    previous_normal = None
    for i, p in enumerate(pts):
        if closed:
            t = pts[(i + 1) % n] - pts[i - 1]
        else:
            t = pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]
        t.normalize()
        ref = previous_normal if previous_normal is not None else Vector((0, 0, 1))
        if abs(ref.dot(t)) > 0.95:
            ref = Vector((1, 0, 0)) if abs(t.x) < 0.9 else Vector((0, 1, 0))
        b = t.cross(ref).normalized()
        nrm = b.cross(t).normalized()
        previous_normal = nrm
        r = radii[i] if radii else radius
        rings.append([p + r * (math.cos(2 * math.pi * s / segments) * nrm + math.sin(2 * math.pi * s / segments) * b)
                      for s in range(segments)])
    verts = [v for ring in rings for v in ring]
    faces = []
    count = n if closed else n - 1
    for i in range(count):
        a, b2 = i * segments, ((i + 1) % n) * segments
        for s in range(segments):
            faces.append((a + s, a + (s + 1) % segments, b2 + (s + 1) % segments, b2 + s))
    if not closed and caps:
        verts.append(pts[0])
        c = len(verts) - 1
        faces += [((s + 1) % segments, s, c) for s in range(segments)]
        verts.append(pts[-1])
        c = len(verts) - 1
        base = (n - 1) * segments
        faces += [(base + s, base + (s + 1) % segments, c) for s in range(segments)]
    obj = k.mesh_object(name, verts, faces, mat)
    k.recalc_normals(obj)
    return k.smooth(obj, 70)


def orb(ramp, shade=7, groove_shade=3, metallic=0.35, roughness=0.3, rim=None):
    """The orb in a palette ramp, with its cross of grooves and a few panel seams. rim: a palette
    index for a dark band round the orb's middle (the brown orb's outline)."""
    shell_mat = k.material(f"orb_{ramp}", palette=ramp * 16 + shade, metallic=metallic, roughness=roughness)
    groove_mat = k.material(f"orb_groove_{ramp}", palette=ramp * 16 + groove_shade, metallic=0.2, roughness=0.5)
    seam_mat = k.material(f"orb_seam_{ramp}", palette=ramp * 16 + min(15, shade + 3), metallic=0.3, roughness=0.3)
    orb_shell("orb", shell_mat)

    def meridian(azimuth, t_max, steps=40, inset=0.12):
        """Points over the top from one side to the other, t_max from the pole each way."""
        out = []
        for i in range(steps + 1):
            t = -t_max + 2 * t_max * i / steps
            out.append(orb_point(azimuth + (math.pi if t < 0 else 0.0), abs(t), inset))
        return out

    # The cross: two grooves over the top, down to just above the middle.
    for azimuth in (0.0, math.pi / 2):
        line = meridian(azimuth, 1.38)
        # The sprite's grooves sit half a pixel off the orb's centre.
        off = Vector((GROOVE_X - ORB_X, 0, 0)) if azimuth else Vector((0, GROOVE_Y - ORB_Y, 0))
        tube("groove", [p + off for p in line], 0.42, groove_mat, 8)
    # Panel seams, lighter (the sprite's lit panel edges): a '#' of raised lines over the ball,
    # beside the cross.
    for axis in (0, 1):
        for c in ((-3.8, 3.8) if axis == 0 else (ORB_Y - 3.6, ORB_Y + 3.6)):
            line = []
            for i in range(49):
                s = -1 + 2 * i / 48
                x, y = (c, ORB_Y + s * ORB_RY) if axis == 0 else (ORB_X + s * ORB_RX, c)
                if _rho(x, y) < 0.985:
                    line.append(Vector((x, y, surf(x, y))))
            line = [q - orb_normal(q) * 0.08 for q in line]
            tube("seam", line, 0.2, seam_mat, 6)
    if rim is not None:
        rim_mat = k.material("orb_rim", palette=rim, metallic=0.4, roughness=0.35)
        ring = [orb_point(2 * math.pi * i / 64, math.pi / 2, inset=0.75) for i in range(64)]
        tube("rim", ring, 0.85, rim_mat, 10, closed=True)
    return shell_mat


# --- Helpers -----------------------------------------------------------------------------------

def apply_modifiers(obj):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    mesh = bpy.data.meshes.new_from_object(obj.evaluated_get(depsgraph))
    obj.modifiers.clear()
    old = obj.data
    obj.data = mesh
    bpy.data.meshes.remove(old)
    return obj


def merge_by_material():
    """Joins the scene's parts that share a material into one object each (fewer draw calls),
    after applying their modifiers."""
    groups = {}
    for obj in list(bpy.context.scene.objects):
        if obj.type != "MESH" or len(obj.data.materials) != 1:
            continue
        apply_modifiers(obj)
        groups.setdefault(obj.data.materials[0].name, []).append(obj)
    for name, objs in groups.items():
        if len(objs) < 2:
            continue
        with bpy.context.temp_override(active_object=objs[0], selected_editable_objects=objs, object=objs[0]):
            bpy.ops.object.join()
        objs[0].name = name.split("@")[0]


def grid_cut(obj, step=0.9):
    """Cuts a part into a grid of `step` (in X and Y), so that bending it follows the orb."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    xs = [v.co.x for v in bm.verts]
    ys = [v.co.y for v in bm.verts]
    for axis, lo, hi in ((0, min(xs), max(xs)), (1, min(ys), max(ys))):
        c = math.floor(lo / step) * step + step
        while c < hi:
            co = [0.0, 0.0, 0.0]
            co[axis] = c
            no = [0.0, 0.0, 0.0]
            no[axis] = 1.0
            geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
            bmesh.ops.bisect_plane(bm, geom=geom, plane_co=co, plane_no=no)
            c += step
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def bend(obj, lift=0.0, floor=0.0):
    """Raises every vertex by the orb's height under it (plus lift)."""
    for v in obj.data.vertices:
        v.co.z += surf(v.co.x, v.co.y, floor) + lift
    obj.data.update()
    k.recalc_normals(obj)
    return obj


def conform(obj, lift=0.0, step=0.9, floor=0.0):
    """Bends a part built on z = 0 onto the orb: every vertex rises by the orb's height under it
    (plus lift); the part is first cut into a grid so that it follows the curve."""
    apply_modifiers(obj)
    grid_cut(obj, step)
    return bend(obj, lift, floor)


# --- Outlines from the sprite's pixels -----------------------------------------------------------

def _grid(icon, chars):
    first, text = icon
    rows = [r for r in text.split("\n") if r]
    return first, [[1 if (ch in chars) else 0 for ch in row.ljust(24, ".")] for row in rows]


def mask_loops(icon, chars, smoothing=1, min_area=0.0):
    """The outlines of the pixels of an ICON map whose character is in chars: marching squares
    through the pixel centres (corners cut at 45 degrees), smoothed (Chaikin) `smoothing` times.
    Returns [(loop, is_hole)], loops [(x, y)] in model units."""
    first, grid = _grid(icon, chars)
    h, w = len(grid), 24

    def val(r, c):
        return grid[r][c] if 0 <= r < h and 0 <= c < w else 0

    def point(key):
        kind, r, c = key
        if kind == "h":  # between centres (r, c) and (r, c + 1)
            return (px(c) + 0.5, py(first + r))
        return (px(c), py(first + r) - 0.5)  # between (r, c) and (r + 1, c)

    segments = []
    for r in range(-1, h):
        for c in range(-1, w):
            tl, tr, br, bl = val(r, c), val(r, c + 1), val(r + 1, c + 1), val(r + 1, c)
            top, right, bottom, left = ("h", r, c), ("v", r, c + 1), ("h", r + 1, c), ("v", r, c)
            case = tl * 8 + tr * 4 + br * 2 + bl
            if case in (0, 15):
                continue
            if case == 10:  # tl and br inside: keep them joined
                segments += [(top, right), (bottom, left)]
            elif case == 5:  # tr and bl inside
                segments += [(left, top), (right, bottom)]
            else:
                edges = []
                if tl != tr:
                    edges.append(top)
                if tr != br:
                    edges.append(right)
                if br != bl:
                    edges.append(bottom)
                if bl != tl:
                    edges.append(left)
                segments.append(tuple(edges))
    links = {}
    for a, b in segments:
        links.setdefault(a, []).append(b)
        links.setdefault(b, []).append(a)
    loops, seen = [], set()
    for start in list(links):
        if start in seen:
            continue
        loop, previous, current = [start], None, start
        seen.add(start)
        while True:
            options = [n for n in links[current] if n != previous]
            if not options:
                break
            nxt = options[0]
            if nxt == start:
                break
            if nxt in seen:
                break
            seen.add(nxt)
            loop.append(nxt)
            previous, current = current, nxt
        if len(loop) >= 3:
            loops.append([point(key) for key in loop])
    out = []
    for loop in loops:
        for _ in range(smoothing):
            smoothed = []
            for i in range(len(loop)):
                (ax, ay), (bx, by) = loop[i], loop[(i + 1) % len(loop)]
                smoothed += [(0.75 * ax + 0.25 * bx, 0.75 * ay + 0.25 * by), (0.25 * ax + 0.75 * bx, 0.25 * ay + 0.75 * by)]
            loop = smoothed
        loop = _drop_straight(loop)
        if _area(loop) < 0:
            loop = loop[::-1]
        out.append(loop)
    out = [loop for loop in out if _area(loop) >= min_area]
    # Holes: loops inside an odd number of others.
    result = []
    for i, loop in enumerate(out):
        depth = sum(1 for j, other in enumerate(out) if j != i and _inside(loop[0], other))
        result.append((loop, depth % 2 == 1))
    return result


def _simplify(points, tolerance):
    """Douglas-Peucker on an open polyline."""
    if len(points) < 3:
        return points
    (ax, ay), (bx, by) = points[0], points[-1]
    dx, dy = bx - ax, by - ay
    length = math.hypot(dx, dy)
    worst, at = -1.0, 0
    for i in range(1, len(points) - 1):
        px_, py_ = points[i]
        d = abs(dy * (px_ - ax) - dx * (py_ - ay)) / length if length > 1e-9 else math.hypot(px_ - ax, py_ - ay)
        if d > worst:
            worst, at = d, i
    if worst <= tolerance:
        return [points[0], points[-1]]
    return _simplify(points[:at + 1], tolerance)[:-1] + _simplify(points[at:], tolerance)


def _drop_straight(loop, tolerance=0.03):
    """Leaves out points that lie (within tolerance) on the line through the points kept round
    them: a closed loop, split at its point farthest from the first."""
    if len(loop) < 8:
        return loop
    x0, y0 = loop[0]
    far = max(range(len(loop)), key=lambda i: (loop[i][0] - x0) ** 2 + (loop[i][1] - y0) ** 2)
    first = _simplify(loop[:far + 1], tolerance)
    second = _simplify(loop[far:] + [loop[0]], tolerance)
    return first[:-1] + second[:-1]


def _area(loop):
    return sum(loop[i][0] * loop[(i + 1) % len(loop)][1] - loop[(i + 1) % len(loop)][0] * loop[i][1]
               for i in range(len(loop))) / 2


def _inside(p, loop):
    x, y = p
    inside = False
    for i in range(len(loop)):
        (ax, ay), (bx, by) = loop[i], loop[(i + 1) % len(loop)]
        if (ay > y) != (by > y) and x < ax + (y - ay) * (bx - ax) / (by - ay):
            inside = not inside
    return inside


def flat(name, loops, z0, z1, mat, bevel=0.0, bevel_segments=2):
    """A flat part from outlines with holes ([(loop, is_hole)]), extruded from z0 to z1."""
    bm = bmesh.new()
    edges = []
    for loop, _ in loops:
        verts = [bm.verts.new((x, y, z1)) for x, y in loop]
        for i in range(len(verts)):
            edges.append(bm.edges.new((verts[i], verts[(i + 1) % len(verts)])))
    bmesh.ops.triangle_fill(bm, use_beauty=True, use_dissolve=False, edges=edges, normal=(0, 0, 1))
    faces = bm.faces[:]
    for f in faces:
        if f.normal.z < 0:
            f.normal_flip()
    result = bmesh.ops.extrude_face_region(bm, geom=faces)
    moved = [e for e in result["geom"] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=moved, vec=(0, 0, z0 - z1))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-4)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.data.materials.append(mat)
    if bevel > 0:
        k.bevel(obj, bevel, bevel_segments)
    return obj


def emblem(name, icon, chars, z0, z1, mat, bevel=0.3, smoothing=1, on_orb=True, lift=0.0, smooth_angle=40,
           min_area=0.0, floor=0.0):
    """A raised layer of a symbol: the pixels of `icon` whose character is in chars, from z0 to z1
    above the orb's surface (bent onto it), or above z = lift if on_orb is False. Islands smaller
    than min_area (square pixels) are left out; floor: the lowest height it bends to (parts
    reaching past the orb's edge stay level there instead of hanging down)."""
    loops = mask_loops(icon, chars, smoothing, min_area)
    if not loops:
        return None
    obj = flat(name, loops, z0, z1, mat, bevel)
    if on_orb:
        conform(obj, lift, step=1.4, floor=floor)
    else:
        apply_modifiers(obj)
        obj.data.transform(Matrix.Translation((0, 0, lift)))
    return k.smooth(obj, smooth_angle)


def star4(name, x, y, long, short, depth, mat, turn=0.0):
    """A four-pointed star (a sparkle): points up/down/left/right of `long`, waist `short`,
    domed `depth` above and below."""
    rim = []
    for i in range(8):
        a = math.radians(45 * i + turn)
        r = long if i % 2 == 0 else short
        rim.append((x + r * math.cos(a), y + r * math.sin(a), 0.0))
    verts = rim + [(x, y, depth), (x, y, -depth * 0.5)]
    faces = [(i, (i + 1) % 8, 8) for i in range(8)] + [((i + 1) % 8, i, 9) for i in range(8)]
    obj = k.mesh_object(name, verts, faces, mat)
    k.recalc_normals(obj)
    return obj


def glow(name, rgb, strength=3.0, roughness=0.3, color=None):
    """An emissive material: rgb the emitted colour (0-255), color the surface (default rgb)."""
    return k.material(name, color or rgb, roughness=roughness, emission=rgb, emission_strength=strength)


POD_SHAPES = {
    # (fraction of the length from the round end, radius factor)
    "drop": [(0.0, 0.0), (0.04, 0.55), (0.12, 0.85), (0.28, 1.0), (0.5, 0.97), (0.7, 0.8), (0.86, 0.5),
             (0.96, 0.18), (1.0, 0.0)],
    "bullet": [(0.0, 0.0), (0.03, 0.65), (0.09, 0.93), (0.18, 1.0), (0.68, 1.0), (0.82, 0.8), (0.93, 0.45),
               (1.0, 0.0)],
}


def pod(name, x0, y0, x1, y1, radius, mat, core=None, lift=0.0, squash=0.85, shape="drop", on_orb=True):
    """A pod lying on the orb from its round end (x0, y0) to its pointed end (x1, y1) (the shot
    sidekicks, bullets, flames); core: a material for a glowing ridge along its top."""
    length = math.hypot(x1 - x0, y1 - y0)
    profile_points = [(-length / 2 + length * t, radius * r) for t, r in POD_SHAPES[shape]]
    body = k.lathe(name, profile_points, mat, segments=20, squash=squash)
    k.smooth(body, 60)
    parts = [body]
    if core is not None:
        ridge = k.ellipsoid(name + "_core", (0, -length * 0.05, radius * squash * 0.74),
                            (radius * 0.28, length * 0.3, radius * 0.28), core, 12, 10)
        parts.append(k.smooth(ridge, 60))
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    turn = Matrix.Rotation(math.atan2(-(x1 - x0), y1 - y0), 4, "Z")
    if on_orb:
        # Tipped with the orb's slope along it, and set on its surface.
        slope = math.atan2(surf(x1, y1) - surf(x0, y0), length) * 0.6
        turn = turn @ Matrix.Rotation(slope, 4, "X")
        place_at = Matrix.Translation((cx, cy, surf(cx, cy) + lift))
    else:
        place_at = Matrix.Translation((cx, cy, lift))
    for part in parts:
        part.data.transform(place_at @ turn)
    return parts
