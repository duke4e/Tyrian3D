"""Helpers shared by round 36's polished models of sheet 9 (UNDERDELI, LAVA RUN, DREAD-NOT, GRAVITRON, EYESPY, TIME
WAR) and DREAD-NOT's cannons (sheet V): polish_dome_heads.py, polish_eye_spheres.py, polish_dread_parts.py,
polish_dread_anchors.py, polish_time_capsule.py, polish_eyespy_boss.py, polish_deli_capsule.py, polish_dread_cannons.py.
Not a model script itself.

Every object is modelled whole in the picture's plane (x, y as its sprites draw it, z up towards the camera) and
sheared along the game camera's line of sight (y - z tan 20, normals with it: polish_gyges_wall.shear_to_camera), so
that the camera sees every point where the sprites draw it and whatever stands higher in the plane covers what lies
under it, as the game's draw order does (the parts of DREAD-NOT's machine are built over each other that way).
- Its body is one heightfield solid (polish_gyges_wall.Plate: a grid STEP = 0.5 pixels apart whose lines are the
  sprites' edges, so a piece is the cells of its sprite's box and needs no mesh cutting), its heights smooth shapes of
  the plane (domes, lying tubes, plates inflated from the sprites' outlines) joined by smooth maxima, falling to the
  outline over a pixel or two; the sprites' dark lines creased into it, their fine shading a little relief.
- Its parts (bulbs, knobs, pipes, lenses, barrels) are solids lofted from explicit rings (the same every run), cut along
  the pieces' boxes (polish_coral_manta.cut: the cuts capped in the part's dark inside colour).
- Every face is painted by the picture under it (Painter): each zone of the picture (a ramp or a part of it) has its
  pixels' shades filled outwards and blurred; a face takes its zone's shade there, LIFT shades lighter (the game reads
  palette colours darker than Blender) and COMP lighter where the game's sun lights the face less than LIT_MEAN (so that
  the drawn light and the game's don't add up: polish_gyges_wall's way), the nearest of its zone's palette indices.
  At most 15 materials a piece (the rarest shades merged into their neighbours).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; a picture's column
c is x = left + c + 0.5, row r is y = top - r - 0.5; each piece is moved so that its sprite's middle is its origin
(models.cfg origin).
"""
import math
import os
import sys

import bpy
import numpy as np
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
import polish_gyges_wall as gw  # noqa: E402  (the picture-plane heightfield, its shear to the camera)
from polish_gyges_wall import Pic, parse, blur, fill, dilate, erode, smoothstep, smax, dome, tube, Region  # noqa: E402,F401
from polish_k_pod import triangulate  # noqa: E402
from polish_deli_boss import join, drop_unused  # noqa: E402
from polish_coral_manta import cut  # noqa: E402

TAN_T = gw.TAN_T
STEP = gw.STEP
SUN = np.array([-0.6, 0.6, 1.0]) / np.linalg.norm([-0.6, 0.6, 1.0])
LIFT = 1.2
COMP = 2.2
LIT_MEAN = 0.72
MAX_MATERIALS = 15


def smin(a, b, kk):
    return -smax(-np.asarray(a, float), -np.asarray(b, float), kk)


def round_rise(d, width):
    """0 at an outline, rising to 1 at `width` inside it with a round (quarter circle) section."""
    t = np.clip(np.asarray(d, float) / width, 0.0, 1.0)
    return np.sqrt(1.0 - (1.0 - t) ** 2)


def max_filter(a, radius):
    """The largest value within `radius` cells (a disc) of each cell."""
    r = int(math.ceil(radius))
    h, w = a.shape
    p = np.pad(a, r, mode="edge")
    out = a.copy()
    for dr in range(-r, r + 1):
        for dc in range(-r, r + 1):
            if dr * dr + dc * dc <= radius * radius:
                out = np.maximum(out, p[r + dr:r + dr + h, r + dc:r + dc + w])
    return out


def lifted(own, under, gap, reach=4.0, sigma=3.0):
    """A top function on the plate's grid: own(X, Y) lifted smoothly wherever it would lie lower than gap over
    under(X, Y) (what the part lies over), so it rides over it keeping its shape (the lift spread over `reach` cells and
    blurred over sigma cells, never less than needed)."""
    def top(X, Y):
        z = own(X, Y)
        need = np.where(z > 0.0, np.maximum(0.0, under(X, Y) + gap - z), 0.0)
        lift = blur(max_filter(need, reach), sigma) if need.any() else need
        lift = np.maximum(lift, need)
        return np.where(z > 0.0, z + lift, 0.0)
    return top


def sample_plate(plate, x, y):
    """The plate's top at a point (bilinear between its grid's points)."""
    fx = (x - plate.X[0, 0]) / STEP
    fy = (y - plate.Y[0, 0]) / STEP
    i = int(min(max(math.floor(fx), 0), plate.X.shape[1] - 2))
    j = int(min(max(math.floor(fy), 0), plate.X.shape[0] - 2))
    tx, ty = fx - i, fy - j
    Z = plate.Z
    return float((Z[j, i] * (1 - tx) + Z[j, i + 1] * tx) * (1 - ty) + (Z[j + 1, i] * (1 - tx) + Z[j + 1, i + 1] * tx) * ty)


def polygon_mask(pic, poly, supersample=4):
    """The picture's pixels whose middles lie inside a polygon of (column, row) points (continuous)."""
    cs = np.arange(pic.w) + 0.5
    rs = np.arange(pic.h) + 0.5
    C, R = np.meshgrid(cs, rs)
    inside = np.zeros(C.shape, bool)
    n = len(poly)
    for i in range(n):
        (c0, r0), (c1, r1) = poly[i], poly[(i + 1) % n]
        cond = (r0 > R) != (r1 > R)
        with np.errstate(divide="ignore", invalid="ignore"):
            xi = c0 + (R - r0) * (c1 - c0) / np.where(r1 == r0, 1e-9, r1 - r0)
        inside ^= cond & (C < xi)
    return inside


# --- Painting ----------------------------------------------------------------------------------------------------------

class Zone:
    """A part of the picture painted in one set of palette indices: its pixels (mask), the indices it may take (one
    ramp's shades, dark to light), its finish (metallic, roughness) and glows ({index: emission strength})."""

    def __init__(self, name, mask, shades, finish, glow=None, sigma=0.8, lift=None, comp=None, values=None, pick=True):
        self.name, self.mask, self.shades, self.finish = name, mask, list(shades), finish
        self.pick = pick          # whether faces may take it as the zone drawn nearest (zone_at); else only by name
        self.glow = glow or {}
        self.sigma, self.lift, self.comp, self.values = sigma, lift, comp, values


class Painter:
    """Paints faces of the picture's plane by the picture under them (see the module's docstring)."""

    def __init__(self, pic, zones, prefix, lift=LIFT, comp=COMP, lit_mean=LIT_MEAN):
        self.pic, self.zones, self.prefix = pic, {z.name: z for z in zones}, prefix
        self.order = [z.name for z in zones]
        self.lift, self.comp, self.lit_mean = lift, comp, lit_mean
        shade = pic.shade()
        for z in zones:
            values = z.values if z.values is not None else shade
            z.soft = blur(fill(values, z.mask), z.sigma) if z.mask.any() else np.full(shade.shape, 5.0)
            z.weight = blur(z.mask.astype(float), 0.6)
        self.mats = {}

    def zone_at(self, X, Y):
        names = [n for n in self.order if self.zones[n].pick]
        w = np.round(np.stack([self.pic.sample(self.zones[n].weight, X, Y) for n in names], 0), 6)
        return [names[i] for i in w.argmax(0)]

    def shade_of(self, zone, X, Y, normals, offset=0.0):
        z = self.zones[zone]
        lift = self.lift if z.lift is None else z.lift
        comp = self.comp if z.comp is None else z.comp
        lit = sun_on(normals)
        return self.pic.sample(z.soft, X, Y) + lift + offset + comp * (self.lit_mean - lit)

    def keys(self, obj, zone=None, offset=0.0, zones=None, faces=None):
        """Material keys (zone, palette index) of the object's faces: of one zone, or each face its own (zones: a list
        of zone names a face, or the zone drawn nearest), offset shades lighter."""
        centres, normals = face_data(obj)
        X, Y = centres[:, 0], centres[:, 1]
        if zones is None:
            zones = [zone] * len(X) if zone is not None else self.zone_at(X, Y)
        out = [None] * len(X)
        for name in sorted(set(zones)):
            idx = np.array([i for i, zn in enumerate(zones) if zn == name])
            s = self.shade_of(name, X[idx], Y[idx], normals[idx], offset)
            picks = gw.nearest(s, self.zones[name].shades)
            for i, v in zip(idx, picks):
                out[i] = (name, int(v))
        return out

    def material(self, key):
        if key not in self.mats:
            zone, index = key
            z = self.zones[zone]
            self.mats[key] = gw.pal("%s_%s" % (self.prefix, zone), index, z.finish[0], z.finish[1], z.glow.get(index, 0.0))
        return self.mats[key]


def face_data(obj):
    """Face centres and normals, rounded (Blender's normals carry float noise from run to run)."""
    centres, normals = gw.face_data(obj)
    return np.round(centres, 5), np.round(normals, 4)


def sun_on(normals):
    """How much the game's sun lights faces of the picture's plane (their normals sheared to the camera)."""
    world = np.asarray(normals, float).copy()
    world[:, 2] += TAN_T * world[:, 1]
    world /= np.maximum(1e-9, np.linalg.norm(world, axis=1))[:, None]
    return np.clip(world @ SUN, 0.0, 1.0)


def assign(obj, keys, painter):
    """Gives the object's faces the materials of their keys (in a fixed order)."""
    mesh = obj.data
    order = sorted(set(keys), key=str)
    mesh.materials.clear()
    for key in order:
        mesh.materials.append(painter.material(key))
    slot = {key: i for i, key in enumerate(order)}
    mesh.polygons.foreach_set("material_index", [slot[key] for key in keys])
    mesh.update()
    obj["keys"] = [str(key) for key in order]
    return obj


def limit_materials(obj, painter, limit=MAX_MATERIALS):
    """Merges the rarest shades of a joined piece into the nearest shade of their zone until it has at most `limit`
    materials."""
    mesh = obj.data
    while len(mesh.materials) > limit:
        n = len(mesh.materials)
        idx = np.zeros(len(mesh.polygons), int)
        mesh.polygons.foreach_get("material_index", idx)
        counts = np.bincount(idx, minlength=n)
        names = [m.name for m in mesh.materials]
        keyed = {}
        for key, m in painter.mats.items():
            keyed[m.name] = key
        best = None
        for i in np.argsort(counts, kind="stable"):
            key = keyed.get(names[i])
            if key is None:
                continue
            zone, index = key
            same = [j for j in range(n) if j != i and keyed.get(names[j]) is not None and keyed[names[j]][0] == zone]
            if not same:
                continue
            j = min(same, key=lambda j: (abs(keyed[names[j]][1] - index), -counts[j]))
            best = (i, j)
            break
        if best is None:
            break
        i, j = best
        idx[idx == i] = j
        idx[idx > i] -= 1
        mesh.materials.pop(index=i)
        mesh.polygons.foreach_set("material_index", idx)
        mesh.update()


# --- Solids ------------------------------------------------------------------------------------------------------------

def ellipsoid(name, centre, radii, count=14, around=32, cut_below=None, angle=0.0, tilt=None):
    """An ellipsoid lofted from explicit rings; angle turns it about z (degrees), tilt (axis, degrees) about x/y."""
    obj = gw.ellipsoid(name, (0.0, 0.0, 0.0), radii, None, count=count, around=around,
                       cut_below=None if cut_below is None else cut_below - centre[2])
    m = Matrix.Translation(centre) @ Matrix.Rotation(math.radians(angle), 4, "Z")
    if tilt is not None:
        m = m @ Matrix.Rotation(math.radians(tilt[1]), 4, tilt[0])
    obj.data.transform(m)
    k.smooth(obj, 80)
    return obj


def loft_path(name, points, radii, around=16, squash=1.0, cap=True, up=(0.0, 0.0, 1.0)):
    """A round part along a path of (x, y, z) points, its radius per point, its sections squashed towards `up`; the
    ends closed by fans to points a little beyond them."""
    pts = [Vector(p) for p in points]
    up = Vector(up)
    rings = []
    for i, p in enumerate(pts):
        a, b = pts[max(i - 1, 0)], pts[min(i + 1, len(pts) - 1)]
        d = (b - a).normalized()
        side = d.cross(up)
        if side.length < 1e-6:
            side = Vector((1.0, 0.0, 0.0))
        side.normalize()
        u = side.cross(d).normalized()
        r = radii[i]
        rings.append([p + side * (r * math.cos(2 * math.pi * j / around)) + u * (r * squash * math.sin(2 * math.pi * j / around))
                      for j in range(around)])
    d0 = (pts[1] - pts[0]).normalized()
    d1 = (pts[-1] - pts[-2]).normalized()
    obj = k.loft(name, rings, None, cap_start=cap, cap_end=cap, start_point=pts[0] - d0 * radii[0] * 0.55,
                 end_point=pts[-1] + d1 * radii[-1] * 0.55)
    k.smooth(obj, 60)
    return obj


def lathe_axis(name, profile, origin, axis, around=28, squash=1.0):
    """A turned part: profile (t, radius) along axis from origin (t increasing), its sections squashed in z."""
    o, a = Vector(origin), Vector(axis).normalized()
    side = a.cross(Vector((0.0, 0.0, 1.0)))
    if side.length < 1e-6:
        side = Vector((1.0, 0.0, 0.0))
    side.normalize()
    u = side.cross(a).normalized()
    rings = [[o + a * t + side * (r * math.cos(2 * math.pi * j / around)) + u * (r * squash * math.sin(2 * math.pi * j / around))
              for j in range(around)] for t, r in profile]
    t0, t1 = profile[0][0], profile[-1][0]
    obj = k.loft(name, rings, None, start_point=o + a * (t0 - 0.01), end_point=o + a * (t1 + 0.01))
    k.smooth(obj, 50)
    return obj


def mirror_x(obj, axis_x):
    """Mirrors an object about the line x = axis_x (its faces' winding kept outward)."""
    obj.data.transform(Matrix.Translation((axis_x, 0, 0)) @ Matrix.Scale(-1, 4, (1, 0, 0)) @
                       Matrix.Translation((-axis_x, 0, 0)))
    obj.data.flip_normals()
    obj.data.update()
    return obj


# --- Pieces ------------------------------------------------------------------------------------------------------------

def box_owner(box):
    x0, x1, y0, y1 = box
    return lambda cx, cy: (cx >= x0) & (cx < x1) & (cy >= y0) & (cy < y1)


def piece_parts(plate, plate_keys, solids, box, owns, name, painter, cap_key):
    """A piece's parts in the picture's plane: the plate's cells it owns (painted by plate_keys(obj, kinds, wall_z)),
    each solid's part inside its box (solids: painted objects; cut with caps of cap_key)."""
    parts = []
    bpy.context.view_layer.update()       # (the solids' bounding boxes are stale after moving their vertices)
    if plate is not None:
        obj, kinds, wall_z = plate.mesh(name + "_body", owns)
        if obj is not None:
            assign(obj, plate_keys(obj, kinds, wall_z), painter)
            parts.append(obj)
    cap = painter.material(cap_key)
    for src in solids:
        p = cut(src, box[:4], cap)
        if p is not None:
            parts.append(p)
    return parts


def finish(name, parts, box, out, options, painter, mask=None, origin=None):
    """Checks a piece's outline as the camera sees it (its parts before the shear, from straight above) against its
    sprite's pixels (mask: 28 rows of 24), shears it to the camera, moves its sprite's middle (or origin) to the
    origin, triangulates and joins it, limits its materials, exports it; returns it."""
    centre = origin if origin is not None else ((box[0] + box[1]) / 2, (box[2] + box[3]) / 2)
    bpy.context.view_layer.update()
    if mask is not None:
        h, w = len(mask), len(mask[0])
        mk.compare(name, mk.coverage(parts, w, h, centre=centre), mask)
    gw.shear_to_camera(parts)
    mk.transform(parts, Matrix.Translation((-centre[0], -centre[1], 0.0)))
    bpy.context.view_layer.update()
    triangulate(parts)
    piece = join(parts, name) if len(parts) > 1 else parts[0]
    piece.name = name
    drop_unused([piece])
    limit_materials(piece, painter)
    bpy.context.scene.view_settings.view_transform = "Standard"
    mk.report(name, [piece], os.path.join(out, name + ".glb"))
    if "preview" in options:
        mk.preview(options["preview"] + name, [piece])
    return piece


def sprite_mask(pic, c0, r0, w=24, h=28):
    """The picture's pixels in a sprite's box (rows of bools)."""
    sub = np.full((h, w), -1)
    rr0, cc0 = max(0, r0), max(0, c0)
    rr1, cc1 = min(pic.h, r0 + h), min(pic.w, c0 + w)
    sub[rr0 - r0:rr1 - r0, cc0 - c0:cc1 - c0] = pic.a[rr0:rr1, cc0:cc1]
    return (sub >= 0).tolist()


def own_box(pic, c0, r0, keep=None, w=24, h=28):
    """A piece's box in the plane (x0, x1, y0, y1) from its sprite's top left pixel, or only the part `keep` (columns c0
    c1, rows r0 r1 of the picture) of it."""
    if keep is not None:
        a, b, c, d = keep
        return (pic.left + a, pic.left + b, pic.top - d, pic.top - c)
    return (pic.left + c0, pic.left + c0 + w, pic.top - r0 - h, pic.top - r0)


def sprite_box(pic, c0, r0, w=24, h=28):
    return (pic.left + c0, pic.left + c0 + w, pic.top - r0 - h, pic.top - r0)
