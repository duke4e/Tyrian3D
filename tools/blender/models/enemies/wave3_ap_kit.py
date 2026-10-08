"""Helpers for batch AP of wave 3: the damaged looks of objects that earlier batches modelled (wave3_ap_*.py). An
enemy hit hard switches its sprite to its damaged sprite (the enemy data's dgr), drawn in the same place; its model is
the intact model's whole object, built by the original script's own builders, damaged (dented, burnt, broken parts as
the damaged sprite shows) and cut into the same pieces, so that each piece swaps in place.

- load(): an original script as a module, without running its build loop (several run it at their top level), its
  registrations left out of the build (forget()).
- Damage: the pixels where a damaged sprite differs from the intact one (both in the intact art's frame, the damaged
  ones in wave3_ap_art.py); repaint() paints the faces over them with the damaged sprite's colours, sink() presses
  the plating in where the damaged sprite is darker (burnt holes, cracks), lift() raises it where lighter.
- From earlier kits: dents and debris (wave3_ak_kit), jagged (snapped) ends and soot (wave3_ag_kit), pixel frames and
  painters (wave3_s_kit).

Coordinates as in tyrkit: 1 unit = 1 game pixel, X right, Y up the screen, Z up (towards the camera); the origin is
the whole object's centre, as in the original script.
"""
import ast
import math
import os
import sys
import types

import bmesh
import bpy
from mathutils import Matrix, Vector, noise

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402,F401
import wave1_d_shapes as sh  # noqa: E402,F401
import wave3_j_kit as w  # noqa: E402,F401
import wave3_s_kit as s  # noqa: E402,F401
import wave3_ag_kit as ag  # noqa: E402,F401
import wave3_ak_kit as ak  # noqa: E402,F401
import wave3_ap_art as art  # noqa: E402,F401
from wave3_j_kit import pal, paint_faces, meshes, bake, triangles  # noqa: E402,F401
from wave3_s_kit import Frame, Painter, pixelate, merge_flat, smoothstep  # noqa: E402,F401
from wave3_ag_kit import jag, scorch  # noqa: E402,F401
from wave3_ak_kit import dent, debris  # noqa: E402,F401


# --- The original scripts ------------------------------------------------------------------------------

def load(name, drop=("run", "main")):
    """The original script `name` (in this directory) as a module, without its top-level calls of the functions
    named in `drop` (its build loop, which several scripts run unguarded; drop="all": every top-level call of a
    plain function, for scripts that build and export each model as they go): its builders and registrations
    only."""
    if name in sys.modules:
        return sys.modules[name]
    path = os.path.join(HERE, name + ".py")
    tree = ast.parse(open(path).read(), path)
    body = []
    for node in tree.body:
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            f = node.value.func
            called = f.attr if isinstance(f, ast.Attribute) else f.id if isinstance(f, ast.Name) else None
            if called in drop or (drop == "all" and isinstance(f, ast.Name)):
                continue
        body.append(node)
    tree.body = body
    mod = types.ModuleType(name)
    mod.__file__ = path
    sys.modules[name] = mod
    exec(compile(tree, path, "exec"), mod.__dict__)
    return mod


def forget(*registries):
    """Empties build registries (lists, dicts) the original scripts filled, so that only this batch's models are
    built."""
    for reg in registries:
        reg.clear()


# --- Frames -----------------------------------------------------------------------------------------------

def frame(name, width, origin):
    """A Frame of one of wave3_ap_art's arts (in the frame of the original's art: same width and origin)."""
    return Frame(getattr(art, name), width, origin)


def luminance(index):
    if index is None:
        return 0.0
    r, g, b = k.level_palette()[index]
    return (0.3 * r + 0.59 * g + 0.11 * b) / 255.0


class Damage:
    """Where a damaged frame differs from the intact one: the pixels whose ramp differs, or whose shade differs by
    more than `tolerance` (small shade changes, the damaged sprite's redrawing, are left alone), or that one of them
    leaves transparent. keep(c, r) -> False leaves a pixel out; lone pixels are dropped (despeckle)."""

    def __init__(self, intact, damaged, tolerance=1, keep=None, despeckle=True):
        self.f0, self.f1 = intact, damaged
        self.ox, self.oy = intact.ox, intact.oy
        cells = set()
        for r in range(max(len(intact.g), len(damaged.g))):
            for c in range(intact.width):
                a, b = intact.get(c, r), damaged.get(c, r)
                if a == b or (keep is not None and not keep(c, r)):
                    continue
                if a is None or b is None or a >> 4 != b >> 4 or abs((a & 15) - (b & 15)) > tolerance:
                    cells.add((c, r))
        if despeckle:
            cells = {(c, r) for c, r in cells
                     if sum((c + dc, r + dr) in cells for dc in (-1, 0, 1) for dr in (-1, 0, 1)) >= 3}
        self.cells = cells

    def cell(self, x, y):
        return int(math.floor(x + self.ox)), int(math.floor(self.oy - y))

    def hit(self, x, y):
        return self.cell(x, y) in self.cells

    def at(self, x, y):
        """The damaged pixel at (x, y) where the damage is (None elsewhere, or where it is transparent)."""
        c, r = self.cell(x, y)
        return self.f1.get(c, r) if (c, r) in self.cells else None

    def gone(self, x, y):
        """True where the damaged sprite leaves out a pixel the intact one has (a part blown away)."""
        c, r = self.cell(x, y)
        return (c, r) in self.cells and self.f1.get(c, r) is None and self.f0.get(c, r) is not None

    def darker(self, x, y):
        """How much darker the damaged sprite is than the intact one at (x, y) (0 where it is not damaged)."""
        c, r = self.cell(x, y)
        if (c, r) not in self.cells:
            return 0.0
        a, b = self.f0.get(c, r), self.f1.get(c, r)
        if a is None or b is None:
            return 0.0
        return max(0.0, luminance(a) - luminance(b))

    def box(self, pad=1.0):
        """The damage's extent (x0, x1, y0, y1)."""
        if not self.cells:
            return None
        cs = [c for c, _ in self.cells]
        rs = [r for _, r in self.cells]
        return (min(cs) - self.ox - pad, max(cs) + 1 - self.ox + pad, self.oy - max(rs) - 1 - pad,
                self.oy - min(rs) + pad)

    def near(self, x, y, radius=1.5):
        """True if a damaged pixel is within `radius` pixels of (x, y)."""
        c, r = self.cell(x, y)
        n = int(math.ceil(radius))
        return any((c + dc, r + dr) in self.cells for dc in range(-n, n + 1) for dr in range(-n, n + 1)
                   if dc * dc + dr * dr <= radius * radius)


def _get(self, c, r):
    if 0 <= r < len(self.g) and 0 <= c < self.width:
        return self.g[r][c]
    return None


Frame.get = _get  # (wave3_s_kit's Frame has no get; wave3_ak_kit.patched expects one)


def overlaps(obj, box):
    if box is None:
        return False
    xs = [v.co.x for v in obj.data.vertices]
    ys = [v.co.y for v in obj.data.vertices]
    if not xs:
        return False
    return not (max(xs) < box[0] or min(xs) > box[1] or max(ys) < box[2] or min(ys) > box[3])


# --- Painting --------------------------------------------------------------------------------------------

def darker(painter, index, steps):
    """The painter's material `steps` shades darker than index (wave3_s_kit's Painter.darker, wave3_v_kit's
    Painter.shifted)."""
    if hasattr(painter, "darker"):
        return painter.darker(index, steps)
    return painter.shifted(index, -steps)


def repaint(objects, dmg, painter, min_nz=0.2, walls=2, keep=None, step=1.0, merge=True, probe=0.5, blur=1, shift=0.0,
            soot=0, soot_radius=2.0, soot_chance=0.75, gone=None):
    """Paints the faces over the damage with the damaged sprite's colours (painter: index -> material), walls
    `walls` shades darker (sampling `probe` out along their normal, the outline pixels); keep(obj, index) -> False
    leaves those faces. blur > 0: each pixel's ramp in its shade smoothed that many times (less pixel noise),
    shifted by `shift`. soot > 0: the faces round the damage (within soot_radius pixels) burnt that many shades
    darker first, patchily. gone: the material of faces over pixels the damaged sprite leaves out (parts blown
    away: a burnt-out hole; None leaves them). The faces are first cut along the pixel grid over the damage (so the paint follows the
    pixels), flat stretches of one colour merged again afterwards."""
    box = dmg.box()
    for obj in objects:
        if not overlaps(obj, box):
            continue
        sh.apply_modifiers(obj)
        pixelate(obj, dmg.f1, step=step, box=box)
        if soot:
            char([obj], painter, amount=soot, chance=soot_chance, seed=len(obj.name),
                 where=lambda x, y: dmg.near(x, y, soot_radius))

        def pick(c, nrm, obj=obj):
            if nrm.z < -0.3:
                return None
            wall = nrm.z < min_nz
            x, y = c.x, c.y
            if wall:
                x += nrm.x * probe
                y += nrm.y * probe
            index = dmg.at(x, y)
            if index is None:
                return gone if gone is not None and dmg.gone(x, y) else None
            if keep is not None and not keep(obj, index):
                return None
            if blur:
                ramp = index >> 4
                shade = int(round(dmg.f1.shade(ramp, blur)(x, y) + shift))
                index = ramp * 16 + max(1 if ramp == 0 else 0, min(15, shade))
            return darker(painter, index, walls) if wall else painter(index)
        paint_faces(obj, pick)
        if merge:
            merge_flat(obj)
    return objects


def sink(objects, dmg, depth, min_z=0.3, power=1.0, noisy=0.4, seed=0.0, along_normal=True, keep=None, mode="darker",
         min_nz=-1.0):
    """Presses the surface in where the damage is (burnt holes, cracks, torn plating): each vertex over a damaged
    pixel moves in by depth * (change ** power) (noisy), along its normal (or down). mode: "darker" (the change is
    how much darker the damaged pixel is), "lighter" (how much lighter: light cracks drawn on dark parts) or
    "changed" (either), "gone" (pixels the damaged sprite leaves out: depth in full). keep(obj) -> False leaves an object; vertices whose normal's z is under min_nz stay."""
    off = Vector((seed * 3.1, seed * 5.7, seed * 1.9))

    def change(x, y):
        c, r = dmg.cell(x, y)
        if (c, r) not in dmg.cells:
            return 0.0
        a, b = dmg.f0.get(c, r), dmg.f1.get(c, r)
        if mode == "gone":
            return 1.0 if a is not None and b is None else 0.0
        if a is None or b is None:
            return 0.0
        d = luminance(a) - luminance(b)
        if mode == "darker":
            return max(0.0, d)
        if mode == "lighter":
            return max(0.0, -d)
        return abs(d)
    for obj in objects:
        if keep is not None and not keep(obj):
            continue
        sh.apply_modifiers(obj)
        obj.data.update()
        moves = []
        for vt in obj.data.vertices:
            if vt.co.z <= min_z or vt.normal.z < min_nz:
                moves.append(None)
                continue
            d = max(change(vt.co.x + dx, vt.co.y + dy) for dx in (-0.3, 0.3) for dy in (-0.3, 0.3))
            if d <= 0.0:
                moves.append(None)
                continue
            amount = depth * min(1.0, d * 2.5) ** power * (1.0 - noisy + noisy * (0.5 + 0.5 * noise.noise(vt.co / 1.4 + off)))
            nrm = vt.normal if along_normal else Vector((0, 0, 1))
            moves.append(-nrm * amount)
        for vt, mv in zip(obj.data.vertices, moves):
            if mv is not None:
                vt.co += mv
                vt.co.z = max(min_z, vt.co.z)
        obj.data.update()
    return objects


def remove(prefixes):
    """Deletes the scene's mesh objects whose names start with one of `prefixes` (parts the damage took away)."""
    gone = []
    for obj in meshes():
        if any(obj.name.startswith(p) for p in prefixes):
            gone.append(obj.name)
            bpy.data.objects.remove(obj)
    return gone


def delete_over(objects, pred, whole=False, any_vertex=False, close=False):
    """Deletes the faces whose centres lie over points pred(x, y) accepts (parts blown away; any_vertex: faces with
    any corner there); whole: the objects whose centres do, entirely; close: the holes left closed again (broken
    ends of solid parts). Objects left empty are removed."""
    for obj in list(objects):
        sh.apply_modifiers(obj)
        if whole:
            vs = obj.data.vertices
            if vs and pred(sum(v.co.x for v in vs) / len(vs), sum(v.co.y for v in vs) / len(vs)):
                bpy.data.objects.remove(obj)
            continue
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        faces = [f for f in bm.faces if pred(f.calc_center_median().x, f.calc_center_median().y) or
                 (any_vertex and any(pred(v.co.x, v.co.y) for v in f.verts))]
        if faces:
            bmesh.ops.delete(bm, geom=faces, context="FACES")
            if close:
                edges = [e for e in bm.edges if e.is_boundary]
                if edges:
                    try:
                        bmesh.ops.holes_fill(bm, edges=edges, sides=0)
                    except Exception:  # noqa: BLE001 (left open)
                        pass
                    ngons = [f for f in bm.faces if len(f.verts) > 3]
                    if ngons:
                        bmesh.ops.triangulate(bm, faces=ngons, quad_method="BEAUTY", ngon_method="EAR_CLIP")
                bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        empty = not bm.faces
        bm.to_mesh(obj.data)
        bm.free()
        if empty:
            bpy.data.objects.remove(obj)
    return objects


def budget(target=4800, objects=None):
    """wave3_n_kit.budget: the larger meshes decimated until the model has about `target` triangles."""
    import wave3_n_kit as n
    return n.budget(target, objects)


def cut_plane(obj, point, normal):
    """Cuts away what lies on the side of a plane its normal points to, closing the cut (wave3_ah_kit.cut_plane)."""
    import wave3_ah_kit as ah
    return ah.cut_plane(obj, point, normal)


def split(obj, point, normal, suffix="_part"):
    """Splits obj by a plane into two closed objects: obj keeps the side against the normal, the copy (returned) the
    side it points to."""
    other = obj.copy()
    other.data = obj.data.copy()
    other.name = obj.name + suffix
    bpy.context.scene.collection.objects.link(other)
    cut_plane(obj, point, normal)
    cut_plane(other, point, tuple(-c for c in normal))
    return other


def named(prefix):
    return [o for o in meshes() if o.name.startswith(prefix)]


def recolour(obj, mapping):
    """Swaps an object's palette materials by index: mapping {old index: new material}."""
    for i, mat in enumerate(obj.data.materials):
        if mat is None or "@" not in mat.name:
            continue
        try:
            index = int(mat.name.rsplit("@", 1)[1].split(".")[0])
        except ValueError:
            continue
        if index in mapping:
            obj.data.materials[i] = mapping[index]
    return obj


def char(objects, painter, amount=3, ramps=None, chance=1.0, seed=0.0, where=None):
    """Burns objects' palette materials darker: each face's colour `amount` shades darker (only ramps in `ramps`;
    where(x, y) -> False leaves a face; chance < 1: patchily, by noise)."""
    off = Vector((seed * 2.3, seed * 4.1, seed * 3.3))
    for obj in objects:
        mats = list(obj.data.materials)
        names = [m.name if m else "" for m in mats]
        for poly in obj.data.polygons:
            if poly.material_index >= len(mats):
                continue
            mat = mats[poly.material_index]
            if mat is None or "@" not in mat.name:
                continue
            try:
                index = int(mat.name.rsplit("@", 1)[1].split(".")[0])
            except ValueError:
                continue
            if ramps is not None and index >> 4 not in ramps:
                continue
            c = poly.center
            if where is not None and not where(c.x, c.y):
                continue
            if chance < 1.0 and 0.5 + 0.5 * noise.noise(Vector((c.x, c.y, c.z)) / 1.7 + off) > chance:
                continue
            new = darker(painter, index, amount)
            if new.name not in names:
                obj.data.materials.append(new)
                names.append(new.name)
                mats.append(new)
            poly.material_index = names.index(new.name)
    return objects


def paint_by(obj, f, painter, walls=2, blur=0, shift=0.0, probe=0.4, min_nz=0.2, under=None, keep=None):
    """Paints every face by the pixel of frame f under its centre (painter: index -> material), walls `walls` shades
    darker (sampled `probe` out along their normal), faces looking down `under` (None: kept); blur > 0: the pixel's
    ramp in its shade smoothed. keep(index) -> False leaves a face."""
    def pick(c, nrm):
        if nrm.z < -0.5:
            return under
        wall = nrm.z < min_nz
        x, y = c.x, c.y
        if wall:
            x += nrm.x * probe
            y += nrm.y * probe
        index = f.at(x, y)
        if index is None or (keep is not None and not keep(index)):
            return None
        if blur:
            ramp = index >> 4
            shade = int(round(f.shade(ramp, blur)(x, y) + shift))
            index = ramp * 16 + max(1 if ramp == 0 else 0, min(15, shade))
        return darker(painter, index, walls) if wall else painter(index)
    return paint_faces(obj, pick)


def remnant(name, f, keep, z0, height, painter, edge=1.0, crumple=0.5, seed=0.0, spacing=0.5, walls=2, smooth=1,
            min_area=0.8, blur=0):
    """A broken fragment where the damaged sprite still draws part of something blown apart: a low relief over the
    pixels of frame f that keep(column, row) accepts, from z0 up `height`, its edges rounded over `edge` pixels, its
    top crumpled by noise (`crumple` of its height), painted by the sprite. Returns the objects (one per piece)."""
    import wave3_z_kit as z
    polys = z.polys_of(f, lambda v, c, r: v is not None and keep(c, r), smooth=smooth, epsilon=0.3, min_area=min_area)
    if not polys:
        return []
    off = Vector((seed * 3.3, seed * 1.7, seed * 0.9))

    def z_of(x, y, e):
        nz = 0.5 + 0.5 * noise.noise(Vector((x, y, 0.0)) / 1.6 + off)
        return max(0.05, height * (0.35 + 0.65 * e) * (1.0 - crumple + crumple * nz))
    obj = z.heightfield(name, polys, z_of, None, spacing=spacing, edge=edge)
    sh.apply_modifiers(obj)
    obj.data.transform(Matrix.Translation((0.0, 0.0, z0)))
    pixelate(obj, f)
    paint_by(obj, f, painter, walls=walls, blur=blur, under=None)
    delete_faces_down(obj)
    merge_flat(obj)
    return [obj]


def z_polys(f, keep, smooth=1, epsilon=0.3, min_area=0.8):
    """The outlines of frame f's pixels keep(index, column, row) accepts (wave3_z_kit.polys_of)."""
    import wave3_z_kit as z
    return z.polys_of(f, lambda v, c, r: v is not None and keep(v, c, r), smooth=smooth, epsilon=epsilon,
                      min_area=min_area)


def delete_faces_down(obj, nz=-0.95):
    """Faces looking straight down (never seen from above) left out."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.normal_update()
    faces = [f for f in bm.faces if f.normal.z < nz]
    if faces:
        bmesh.ops.delete(bm, geom=faces, context="FACES")
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def tilt(objects, pivot, axis, degrees):
    """Turns objects about an axis ('X', 'Y') through pivot (x, y, z): a bent fragment."""
    m = Matrix.Translation(Vector(pivot)) @ Matrix.Rotation(math.radians(degrees), 4, axis) @ \
        Matrix.Translation(-Vector(pivot))
    for obj in objects:
        sh.apply_modifiers(obj)
        obj.data.transform(m)
    return objects


def cracks(objects, mat, scale=3.0, width=0.09, depth=0.35, seed=0.0, where=None, glow_mat=None, glow_width=0.03):
    """Procedural cracks (where the sprite gives too few pixels for them): the faces along the lines where a noise
    field crosses zero (a web of cracks `scale` pixels across its cells) take `mat` (the thinnest middle `glow_mat`,
    embers), the vertices there pressed in by `depth`. where(x, y) -> False leaves a place. Cut the faces fine
    first (pixelate with a small step)."""
    off = Vector((seed * 7.1, seed * 3.7, seed * 5.3))

    def ridge(co):
        return abs(noise.noise(Vector(co) / scale + off))
    for obj in objects:
        sh.apply_modifiers(obj)

        def pick(c, nrm):
            if nrm.z < -0.2 or (where is not None and not where(c.x, c.y)):
                return None
            r = ridge(c)
            if glow_mat is not None and r < glow_width:
                return glow_mat
            return mat if r < width else None
        paint_faces(obj, pick)
        for vt in obj.data.vertices:
            if where is not None and not where(vt.co.x, vt.co.y):
                continue
            r = ridge(vt.co)
            if r < width:
                vt.co -= vt.normal * depth * (1.0 - r / width)
        obj.data.update()
    return objects


def crack_lines(name, surface, origin, mat, branches=5, length=6.0, step=0.7, radius=0.22, seed=1, spread=1.0,
                fork=0.3, lift=0.04, squash=0.5, ember=None):
    """Cracks as thin dark lines lying on a surface (z = surface(x, y), None off it): `branches` jagged lines
    running out from `origin` (x, y) about `length` pixels each, some forking; each a flattened tube of `radius`
    (ember: a material for a thinner glowing core). Returns the objects."""
    import random
    rnd = random.Random(seed)
    lines = []
    for b in range(branches):
        a = 2 * math.pi * (b + rnd.uniform(-0.3, 0.3) * spread) / branches
        lines.append(([origin], a, length * rnd.uniform(0.6, 1.2)))
    out = []
    i = 0
    while lines and i < 40:
        pts, a, ln = lines.pop()
        x, y = pts[-1]
        travelled = 0.0
        while travelled < ln:
            a += rnd.uniform(-0.6, 0.6)
            x += math.cos(a) * step
            y += math.sin(a) * step
            if surface(x, y) is None:
                break
            pts.append((x, y))
            travelled += step
            if rnd.random() < fork * step / ln and len(lines) < 30:
                lines.append(([(x, y)], a + rnd.choice((-1, 1)) * rnd.uniform(0.5, 1.1), (ln - travelled) * 0.7))
        if len(pts) >= 3:
            p3 = [(px_, py_, surface(px_, py_) + lift) for px_, py_ in pts]
            out.append(w.tube(f"{name}{i}", p3, radius, mat, 6, squash=squash))
            if ember is not None:
                out.append(w.tube(f"{name}_ember{i}", [(px_, py_, z_ + radius * squash * 0.6) for px_, py_, z_ in p3],
                                  radius * 0.45, ember, 5, squash=squash))
            i += 1
    return out


def crack_mesh(objects, dmg, depth=0.6, keep=None):
    """sink() for cracks: fine (pixelated) faces pressed in where the damage is darker."""
    return sink(objects, dmg, depth, power=0.7, noisy=0.3, keep=keep)
