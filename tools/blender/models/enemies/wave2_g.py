"""Enemies of wave 2, batch G, modelled as their sprites look (models.cfg: yaw=0):

- ore_hauler (sheet D 115): the brown hauler of ASTEROID2 and AST ROCK, a heavy crossbar over a
  keeled spine, glowing red engine pods at both sides and a red light bar at the top.
- rock_tip (sheet 8 245): the lower tip of a narrow rock column of IXMUCANE and SAWBLADES, in the
  sprite's top right corner (the column's upper part is sprite 207): a piece (origin).
- deli_tower_tl (sheet U 1): the top left corner of DELI's tower, which the game puts together from
  six sprites (U 1, 3, 5 above 39, 41, 43): the tops of a post and two red pipes: a piece (origin).
- boom_ship_right, boom_ship_left (sheet 2 269, 2 271, mirror images): the grey ship of TYRIAN,
  HOLES and ASSASSIN flying sideways, a pointed hull with a red sensor in a tan collar, held in a
  frame of two rails.
- warp_orb (sheet P 85): the swirling fire orb that leads to a secret level; its frames brighten it
  (glow option).
- stone_plant (sheet J 1): the grey stone plant of TORM, BOTANY B and BONUS, standing on the ground:
  a bud on a stalk, a round bulb, leaves and a small bud at the side.
- pipe_arm_2 (sheet 4 269): the second of the four pieces of the brown pipe arm of TYRIAN's boss
  (4 267-273); the whole arm is built and cut (origin).
- hatch_ship (sheet S 93): the grey shield-shaped ship of the asteroid levels, a hatch in its middle
  opening on a red eye (frames 93, 131), red lights at its corners and a blue canopy at its tip.
- lava_star (sheet 5 278): the spiked star of glowing lava of BRAINIAC and SQUADRON (its frames
  shrink it; the model keeps the first frame's size).
- pink_torpedo_front, pink_torpedo_rear (sheet 8 125, 8 127): the two halves of the pink torpedo of
  IXMUCANE and SAWBLADES lying on its side, its muzzle glowing at the front (origin).
- horseshoe: now built by polish_horseshoe.py.
- gem_bud: now built by polish_gem_bud.py.
- bomb_pickup (coins sheet 89): the pick-up of a super bomb: the word BOMB in glowing orange
  letters beside a blue bomb (assets/models/items).
- fork_ship (sheet F 87): the tan fork-shaped ship of SAVARA, swept wings, grey fins and a port
  with a light in its belly.

Parts are mostly inflated from the outlines of regions of the sprites' pixels (wave2_g_art.py holds
the pixels' palette indices), with the helpers of wave1_d_shapes.py; flat undersides are simplified
to keep the models light.

usage: Blender -b --factory-startup -P wave2_g.py -- [--only name,name] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1]
       Blender -b --factory-startup -P wave2_g.py -- --whole torpedo|pipe_arm --preview <prefix>
--preview renders <prefix><name>_top.png and _3q.png; --check prints each model's silhouette overlap
with its sprite; --stats prints the triangles per part; --whole renders a whole object the game
draws in pieces (the pieces are cut from it) instead of exporting.
"""
import math
import os
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import wave1_d_shapes as sh  # noqa: E402
import wave2_g_art as art  # noqa: E402

ROOT = os.path.join(HERE, "..", "..", "..", "..", "assets", "models")
MODELS = []  # (name, builder, sheet, sprites, size, kind)
WHOLES = {}  # name: (builder, size in pixels): objects the game draws in pieces, for --whole previews


def model(name, sheet, sprite, size=(24, 28), kind="enemies", check=None):
    def register(fn):
        MODELS.append((name, fn, sheet, check or [sprite], size, kind))
        return fn
    return register


# --- Pixels ----------------------------------------------------------------------------------------

def grid(text, width):
    """The art's rows as lists of palette indices (None: transparent), `width` pixels each."""
    out = []
    for line in text.strip("\n").split("\n"):
        line = line.ljust(2 * width, ".")
        out.append([None if line[2 * i:2 * i + 2] == ".." else int(line[2 * i:2 * i + 2], 16) for i in range(width)])
    return out


def regions(g, fn):
    """Char rows of a grid: fn(index, column, row) -> a char ('.' for nothing)."""
    return ["".join("." if v is None else fn(v, c, r) for c, v in enumerate(row)) for r, row in enumerate(g)]


def window(rows, c0, r0, w, h):
    return [row[c0:c0 + w].ljust(w, ".") for row in rows[r0:r0 + h]]


def pal(name, index, metallic=0.3, roughness=0.4, glow=None, color=None):
    """A palette material; glow: emission strength, in the palette colour (or color)."""
    if glow:
        return k.material(name, palette=index, metallic=metallic, roughness=roughness,
                          emission=color or k.level_palette()[index], emission_strength=glow)
    return k.material(name, palette=index, metallic=metallic, roughness=roughness)


def part(name, rows, chars, mat, profile, origin=(12, 14), bottom=0.0, base=0.0, z_fn=None, smooth=2, epsilon=0.5,
         spacing=0.5, grow=0.0, sigma=1.2, min_area=0.3, rim=0.15, extra=None):
    """A part inflated from the pixels of rows whose char is in chars (see wave1_d_shapes.inflate);
    grow moves its outline outwards (tucks it under its neighbours)."""
    polys = sh.outlines(rows, chars, origin, smooth=smooth, epsilon=epsilon, min_area=min_area)
    if grow:
        polys = [sh.inset(p, -grow) for p in polys]
    if extra:
        polys += extra
    return sh.inflate(name, polys, mat, profile, bottom=bottom, base=base, rim=rim, spacing=spacing, z_fn=z_fn,
                      sigma=sigma)


# --- Mesh helpers ----------------------------------------------------------------------------------

def simplify_bottom(obj, angle=0.999):
    """Dissolves the flat, downward faces of a part into as few faces as possible (the underside of
    something standing on its base), to keep the model light."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.normal_update()
    zmin = min(v.co.z for v in bm.verts)
    faces = [f for f in bm.faces if f.normal.z < -angle and all(abs(v.co.z - zmin) < 1e-3 for v in f.verts)]
    if faces:
        try:
            bmesh.ops.dissolve_faces(bm, faces=faces, use_verts=True)
        except Exception:  # noqa: BLE001 (leave it as it is)
            pass
        ngons = [f for f in bm.faces if len(f.verts) > 3]
        if ngons:
            bmesh.ops.triangulate(bm, faces=ngons, quad_method="BEAUTY", ngon_method="EAR_CLIP")
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def decimate(obj, target):
    """Collapses the part's mesh to about `target` triangles (if it has more)."""
    tris = sum(len(p.vertices) - 2 for p in obj.data.polygons)
    if tris > target:
        mod = obj.modifiers.new("decimate", "DECIMATE")
        mod.ratio = target / tris
        mod.use_collapse_triangulate = True
        sh.apply_modifiers(obj)
    return obj


def planar(obj, degrees=1.5):
    """Merges the nearly flat stretches of a part's surface into larger faces (keeping the borders
    between materials), then triangulates: flat tops cost few triangles."""
    mod = obj.modifiers.new("planar", "DECIMATE")
    mod.decimate_type = "DISSOLVE"
    mod.angle_limit = math.radians(degrees)
    mod.delimit = {"MATERIAL"}
    sh.apply_modifiers(obj)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method="BEAUTY", ngon_method="BEAUTY")
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def lathe_x(name, profile, mat, segments=24, y=0.0, z=0.0, squash=1.0):
    """A round part along X: profile is (x, radius) pairs in increasing x."""
    obj = k.lathe(name, profile, mat, segments=segments, squash=squash)
    obj.data.transform(Matrix.Rotation(math.radians(-90), 4, "Z"))
    obj.data.transform(Matrix.Translation((0.0, y, z)))
    k.recalc_normals(obj)
    return obj


def tube(name, points, radius, mat, segments=12, squash=1.0):
    """A tube through points (x, y, z) with rounded ends; radius a number or one per point."""
    pts = [Vector(p) for p in points]
    radii = radius if isinstance(radius, (list, tuple)) else [radius] * len(pts)
    rings = []
    for i, p in enumerate(pts):
        a, b = pts[max(i - 1, 0)], pts[min(i + 1, len(pts) - 1)]
        tangent = (b - a).normalized()
        side = tangent.cross(Vector((0, 0, 1)))
        if side.length < 1e-6:
            side = Vector((1, 0, 0))
        side.normalize()
        up = side.cross(tangent).normalized()
        rings.append([p + (side * math.cos(2 * math.pi * j / segments) +
                           up * math.sin(2 * math.pi * j / segments) * squash) * radii[i] for j in range(segments)])
    t0, t1 = (pts[1] - pts[0]).normalized(), (pts[-1] - pts[-2]).normalized()
    obj = k.loft(name, rings, mat, start_point=pts[0] - t0 * radii[0] * 0.7, end_point=pts[-1] + t1 * radii[-1] * 0.7)
    return k.smooth(obj, 60)


def mirror_objects(objects, axis_x=0.0):
    for obj in objects:
        obj.data.transform(Matrix.Translation((axis_x, 0, 0)) @ Matrix.Scale(-1, 4, (1, 0, 0)) @
                           Matrix.Translation((-axis_x, 0, 0)))
        obj.data.flip_normals()


def scene_objects():
    return [o for o in bpy.context.scene.objects if o.type == "MESH"]


def paint_faces(obj, fn):
    """Gives each face the material fn(face centre, normal) returns (None: keep), appending the
    materials to the object."""
    mats = list(obj.data.materials)
    for poly in obj.data.polygons:
        mat = fn(poly.center, poly.normal)
        if mat is None:
            continue
        if mat.name not in [m.name for m in mats]:
            obj.data.materials.append(mat)
            mats.append(mat)
        poly.material_index = [m.name for m in mats].index(mat.name)
    return obj


def sampler(g, origin=(12, 14), shade=lambda v: v & 15, blur=1):
    """A function (x, y) -> the grid's value (shade) at a point, bilinear between pixel centres and
    blurred `blur` times; outside the sprite, the nearest pixel's."""
    h, w = len(g), len(g[0])
    field = np.full((h, w), np.nan)
    for r in range(h):
        for c in range(w):
            if g[r][c] is not None:
                field[r, c] = shade(g[r][c])
    for _ in range(blur):
        out = field.copy()
        for r in range(h):
            for c in range(w):
                if np.isnan(field[r, c]):
                    continue
                vals, wts = [], []
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        rr, cc = r + dr, c + dc
                        if 0 <= rr < h and 0 <= cc < w and not np.isnan(field[rr, cc]):
                            vals.append(field[rr, cc])
                            wts.append(2.0 if dr == dc == 0 else 1.0 if dr == 0 or dc == 0 else 0.5)
                out[r, c] = np.average(vals, weights=wts)
        field = out
    known = [(r, c) for r in range(h) for c in range(w) if not np.isnan(field[r, c])]
    ox, oy = origin

    def at(x, y):
        c, r = x + ox - 0.5, oy - y - 0.5
        c0, r0 = math.floor(c), math.floor(r)
        total = weight = 0.0
        for rr, cc, wt in ((r0, c0, (1 - (r - r0)) * (1 - (c - c0))), (r0, c0 + 1, (1 - (r - r0)) * (c - c0)),
                           (r0 + 1, c0, (r - r0) * (1 - (c - c0))), (r0 + 1, c0 + 1, (r - r0) * (c - c0))):
            if 0 <= rr < h and 0 <= cc < w and not np.isnan(field[rr, cc]):
                total += field[rr, cc] * wt
                weight += wt
        if weight > 0.05:
            return total / weight
        rr, cc = min(known, key=lambda p: (p[0] - r) ** 2 + (p[1] - c) ** 2)
        return field[rr, cc]
    return at


def gauss(x, y, cx, cy, sx, sy):
    return math.exp(-(((x - cx) / sx) ** 2 + ((y - cy) / sy) ** 2))


# --- D 115: the ore hauler -------------------------------------------------------------------------

@model("ore_hauler", "D", 115)
def ore_hauler():
    """A heavy brown crossbar over a spine that narrows to a point at the bottom, a raised rim round
    the spine and a bar along its middle, red engine pods glowing along both sides of the spine
    (hot spots where the sprite has its yellow pixels) and a red light bar along the crossbar's top."""
    g = grid(art.D115, 24)

    def where(v, c, r):
        if v >> 4 == 7:
            return "t" if r <= 1 else "p"
        if r <= 8 and not (8 <= c <= 16 and r >= 7) or r == 9 and (c < 5 or c > 19):
            return "c"
        return "s"
    rows = regions(g, where)
    brown = pal("hauler_brown", 0xa7, metallic=0.45, roughness=0.45)
    rim = pal("hauler_rim", 0xa9, metallic=0.5, roughness=0.35)
    deep = pal("hauler_deep", 0xa5, metallic=0.4, roughness=0.55)
    red = pal("hauler_red", 0x74, metallic=0.1, roughness=0.3, glow=0.45)
    orange = pal("hauler_orange", 0x79, metallic=0.0, roughness=0.3, glow=0.8)
    yellow = pal("hauler_yellow", 0x7c, metallic=0.0, roughness=0.3, glow=1.0)

    # The crossbar: a heavy rounded beam.
    bar = part("crossbar", rows, "c", brown, sh.pillow_profile(5.0, 1.8, crown=0.6), smooth=2, epsilon=0.5,
               spacing=0.6)
    # The spine: a low body under a rim and a middle bar.
    spine = part("spine", rows, "s", deep, sh.pillow_profile(3.4, 1.2, crown=0.3), smooth=1, epsilon=0.5,
                 spacing=0.6, grow=0.35)
    rim_path = [(-3.3, 7.5), (-3.3, 2.0), (-3.3, -4.0), (-3.2, -6.5), (-2.8, -8.6), (-1.7, -10.2), (0.5, -11.0),
                (2.7, -10.2), (3.8, -8.6), (4.2, -6.5), (4.3, -4.0), (4.3, 2.0), (4.3, 7.5)]
    path = []
    for (x0, y0), (x1, y1) in zip(rim_path, rim_path[1:]):
        for t in np.linspace(0, 1, 5)[:-1]:
            path.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))
    path.append(rim_path[-1])
    tube("rim", [(x, y, sh.surface_z(spine, x, y, 3.0) + 0.1) for x, y in path], 0.85, rim, segments=8, squash=0.9)
    ridge = [(0.5, y) for y in np.linspace(7.5, -8.8, 14)]
    tube("ridge", [(x, y, sh.surface_z(spine, x, y, 3.0) + 0.25) for x, y in ridge],
         [1.15] * 11 + [1.0, 0.8, 0.6], rim, squash=0.75)

    # The pods, and their hot spots.
    pods = part("pods", rows, "p", red, sh.round_profile(1.3, max_height=4.4), smooth=2, epsilon=0.4,
                spacing=0.55, grow=0.45, bottom=0.0)
    for x, y, rx, ry, mat, sink in ((-6.5, 3.6, 1.0, 1.0, orange, 0.35), (7.5, 3.6, 1.0, 1.0, orange, 0.35),
                                    (-5.5, -2.0, 1.5, 2.8, orange, 0.45), (6.5, -1.6, 1.4, 2.5, orange, 0.45),
                                    (-5.5, -2.0, 0.9, 1.8, yellow, 0.2), (6.5, -1.6, 0.8, 1.5, yellow, 0.2)):
        z = sh.surface_z(pods, x, y, 3.0)
        k.smooth(k.ellipsoid(f"spot{x}{y}{rx}", (x, y, z - sink), (rx, ry, 0.7), mat, 12, 6), 60)
    # The light bar, partly under the crossbar.
    light = part("light_bar", rows, "t", red, sh.round_profile(1.0, max_height=2.6), smooth=2,
                 epsilon=0.4, spacing=0.5, grow=0.3, base=1.6, bottom=0.6)
    light.data.transform(Matrix.Translation((0, -0.4, 0)))
    for x, mat in ((-2.5, yellow), (2.5, orange)):
        k.smooth(k.ellipsoid(f"bar_spot{x}", (x, 12.6, sh.surface_z(light, x, 12.6, 3.5) - 0.5), (1.3, 0.7, 0.6),
                             mat, 12, 6), 60)
    # Bolts at the crossbar's ends.
    for x in (-8.6, 9.6):
        z = sh.surface_z(bar, x, 9.5, 5.0)
        k.smooth(k.ellipsoid(f"bolt{x}", (x, 9.5, z - 0.15), (0.9, 0.9, 0.5), rim, 12, 6), 60)
    for obj in (bar, spine, pods):
        simplify_bottom(obj)
        decimate(obj, 850)
        k.smooth(obj, 50)
    k.smooth(decimate(light, 400), 50)


# --- 2 269 / 2 271: the boom ship -----------------------------------------------------------------

def boom_ship(mirror):
    """A grey hull pointed to the right (sprite 269; 271 is its mirror image), a dark face plate at
    its rear with two red lights, wrapped in a tan collar, held in a frame: a light grey post behind
    the hull and two rails above and below it, joined to the post by tan elbows. Symmetric about
    the hull's axis (y = 0.5)."""
    grey = pal("boom_grey", 0x08, metallic=0.6, roughness=0.3)
    light = pal("boom_light", 0x0b, metallic=0.6, roughness=0.25)
    dark = pal("boom_dark", 0x03, metallic=0.4, roughness=0.5)
    tan = pal("boom_tan", 0x1a, metallic=0.55, roughness=0.3)
    brown = pal("boom_brown", 0xa6, metallic=0.4, roughness=0.45)
    red = pal("boom_red", 0x77, metallic=0.1, roughness=0.25, glow=0.9)
    cy = 0.5
    # The hull.
    hull_profile = [(-7.6, 0.01), (-7.5, 1.7), (-7.2, 3.3), (-6.4, 4.9), (-5.0, 6.0), (-3.0, 6.8), (0.0, 7.1),
                    (2.5, 6.9), (4.5, 6.1), (6.5, 4.9), (8.5, 3.5), (10.3, 2.2), (11.6, 1.0), (12.1, 0.01)]
    hull = lathe_x("hull", k.profile(hull_profile, 0.7), grey, 28, y=cy, z=0.0, squash=0.64)
    k.smooth(hull, 60)
    paint_faces(hull, lambda c, n: dark if c.x < -1.2 and abs(c.y - cy) < 4.2 and n.z > 0.05 else None)
    # A tan canopy strip along the top and the seam round the face plate.
    k.smooth(k.ellipsoid("canopy", (2.4, cy, 3.9), (2.6, 1.0, 0.7), tan, 16, 8), 60)
    # The red lights on the face plate.
    for x in (-5.5, -3.5):
        k.smooth(k.ellipsoid(f"light{x}", (x, cy, sh.surface_z(hull, x, cy, 3.0) - 0.4), (0.7, 1.6, 0.7), red, 12, 8),
                 60)
    # The tan collar round the rear of the hull.
    collar = []
    for a in np.linspace(-115, 115, 17):
        t = math.radians(a)
        collar.append((-3.6 - 3.6 * math.cos(t), cy + 4.9 * math.sin(t), 0.6 + 1.6 * math.cos(t)))
    tube("collar", collar, 1.05, tan, segments=10, squash=0.9)
    for side in (-1, 1):
        k.smooth(k.ellipsoid(f"collar_end{side}", (-2.6, cy + side * 5.0, 0.4), (1.3, 1.6, 1.0), brown, 12, 6), 60)
    # The frame: the post behind the hull, the elbows and the rails.
    tube("post", [(-10.0, cy + y, 0.0) for y in np.linspace(-6.0, 6.0, 7)], 2.0, light, segments=12, squash=0.8)
    for side in (-1, 1):
        elbow = [(-10.2, cy + side * 5.0, 0.0), (-10.6, cy + side * 6.8, 0.2), (-9.3, cy + side * 8.4, 0.4),
                 (-7.4, cy + side * 9.7, 0.5), (-5.6, cy + side * 10.0, 0.5)]
        tube(f"elbow{side}", elbow, 1.45, tan, segments=10)
        rail = [(x, cy + side * 10.0, 0.5) for x in np.linspace(-6.5, 3.6, 6)]
        tube(f"rail{side}", rail, 1.4, grey, segments=10, squash=0.75)
        k.smooth(lathe_x(f"band{side}", [(-6.4, 1.4), (-6.2, 1.6), (-5.0, 1.6), (-4.8, 1.4)], tan, 12,
                         y=cy + side * 10.0, z=0.5, squash=0.8), 50)
    objects = scene_objects()
    if mirror:
        mirror_objects(objects)
    for obj in objects:
        k.recalc_normals(obj)


model("boom_ship_right", "2", 269)(lambda: boom_ship(False))
model("boom_ship_left", "2", 271)(lambda: boom_ship(True))


# --- P 85: the warp orb ---------------------------------------------------------------------------

def shade_bands(g, bands, origin=(12, 14), blur=1, low=None):
    """A painter for paint_faces: the material of the band of the sprite's shade under a face
    (bands: [(lowest shade, material)], ascending); faces facing down (or below `low`) take the
    first band."""
    shade = sampler(g, origin, blur=blur)

    def pick(centre, normal):
        if normal.z < -0.2 or (low is not None and centre.z < low):
            return bands[0][1]
        s = shade(centre.x, centre.y)
        chosen = bands[0][1]
        for lowest, mat in bands:
            if s >= lowest:
                chosen = mat
        return chosen
    return pick


@model("warp_orb", "P", 85)
def warp_orb():
    """A ball of swirling fire: its top in the sprite's shades of the fire ramp, all glowing (the
    frames 131 and 233 brighten it: glow option); a darker ball underneath."""
    g = grid(art.P85, 24)
    bands = [(lowest, pal(f"warp_{index:x}", index, metallic=0.0, roughness=0.55, glow=0.45 + 0.07 * (index - 0x72)))
             for lowest, index in ((0.0, 0x72), (2.5, 0x73), (4.0, 0x75), (5.5, 0x76), (7.0, 0x78), (8.5, 0x79),
                                   (10.0, 0x7b), (11.5, 0x7c), (13.5, 0x7e))]
    cx, cy, radius, squash = -0.5, -0.5, 10.4, 0.82
    circle = sh.ellipse(cx, cy, radius, radius, count=96)

    def dome(d, w):
        r = np.clip(radius - d, 0.0, radius)
        return squash * np.sqrt(np.maximum(0.0, radius ** 2 - r ** 2))
    top = sh.inflate("orb", [circle], bands[0][1], dome, bottom=0.0, rim=0.0, spacing=0.45)
    paint_faces(top, shade_bands(g, bands, blur=0))
    simplify_bottom(top)
    k.smooth(top, 80)
    under = k.ellipsoid("orb_under", (cx, cy, 0.0), (radius - 0.05, radius - 0.05, radius * squash * 0.9), bands[0][1],
                        40, 20)
    sh.cut_planes([under], [((0, 0, 0.05), (0, 0, 1))])
    k.smooth(under, 80)


# --- S 93: the hatch ship -------------------------------------------------------------------------

def rounded_rect(x0, y0, x1, y1, radius, count=6):
    """A rectangle with rounded corners, counter-clockwise."""
    out = []
    for cx, cy, a0 in ((x1 - radius, y0 + radius, -90), (x1 - radius, y1 - radius, 0), (x0 + radius, y1 - radius, 90),
                       (x0 + radius, y0 + radius, 180)):
        for i in range(count + 1):
            a = math.radians(a0 + 90 * i / count)
            out.append((cx + radius * math.cos(a), cy + radius * math.sin(a)))
    return out


@model("hatch_ship", "S", 93)
def hatch_ship():
    """A grey shield-shaped hull with a raised rim, red lights in its upper corners, a ribbed hatch
    in its middle that opens on a red eye (the frames 93 and 131 open and shut it: the model shows
    it open), angled plates at its shoulders and a keel down to a blue canopy at its tip."""
    g = grid(art.S93, 24)
    rows = regions(g, lambda v, c, r: "#")
    hull_mat = pal("hatch_hull", 0x05, metallic=0.55, roughness=0.35)
    rim_mat = pal("hatch_rim", 0x08, metallic=0.6, roughness=0.3)
    dark = pal("hatch_dark", 0x02, metallic=0.4, roughness=0.6)
    plate_mat = pal("hatch_plate", 0x06, metallic=0.6, roughness=0.3)
    red = pal("hatch_red", 0x76, metallic=0.1, roughness=0.15, glow=0.8)
    pupil = pal("hatch_pupil", 0x7a, metallic=0.0, roughness=0.2, glow=1.0)
    lamp = pal("hatch_lamp", 0x74, metallic=0.1, roughness=0.2, glow=0.8)
    blue = pal("hatch_blue", 0x96, metallic=0.2, roughness=0.1, glow=0.35, color=(40, 80, 255))
    outline = sh.outlines(rows, "#", (12, 14), smooth=1, epsilon=0.5)
    hull = sh.inflate("hull", outline, hull_mat, sh.pillow_profile(2.7, 1.0, crown=0.15), bottom=0.0, spacing=0.5)
    simplify_bottom(hull)
    decimate(hull, 1200)
    k.smooth(hull, 45)
    # The raised frame round the upper half, the keel down the lower half.
    frame_path = [(-8.9, -0.6), (-9.0, 4.0), (-9.0, 8.5), (-8.6, 10.2), (-7.2, 10.9), (-3.0, 11.0), (3.0, 11.0),
                  (7.2, 10.9), (8.6, 10.2), (9.0, 8.5), (9.0, 4.0), (8.9, -0.6)]
    path = []
    for (x0, y0), (x1, y1) in zip(frame_path, frame_path[1:]):
        for t in np.linspace(0, 1, 4)[:-1]:
            path.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))
    path.append(frame_path[-1])
    tube("frame", [(x, y, sh.surface_z(hull, x, y, 2.7) - 0.1) for x, y in path], 1.0, rim_mat, segments=8,
         squash=0.8)
    keel_rows = [row if 13 <= r <= 26 else "." * len(row) for r, row in enumerate(regions(
        g, lambda v, c, r: "#" if 9 <= c <= 14 else "."))]
    keel = part("keel", keel_rows, "#", rim_mat, sh.round_profile(0.8, max_height=1.8), base=2.2, spacing=0.5,
                smooth=2, epsilon=0.5)
    k.smooth(simplify_bottom(keel), 50)
    # The hatch: a ribbed frame round the eye.
    frame = sh.inflate("hatch", [rounded_rect(-3.1, 1.0, 3.1, 6.6, 1.4), rounded_rect(-1.9, 2.0, 1.9, 5.6, 0.9)[::-1]],
                       rim_mat, sh.round_profile(1.0, max_height=1.1), bottom=0.0, base=2.4, spacing=0.45)
    k.smooth(frame, 50)
    k.smooth(k.ellipsoid("socket", (0.0, 3.8, 2.4), (2.3, 2.1, 1.0), dark, 20, 8), 60)
    k.smooth(k.ellipsoid("eye", (0.0, 3.7, 2.7), (1.9, 1.7, 1.1), red, 20, 10), 60)
    k.smooth(k.ellipsoid("pupil", (0.0, 3.6, 3.55), (0.8, 0.75, 0.35), pupil, 12, 6), 60)
    # The ribs leading down to the hatch.
    for x in (-1.5, 1.5):
        tube(f"rib{x}", [(x, 10.0, 3.0), (x, 8.5, 3.1), (x, 7.0, 3.2)], 0.45, rim_mat, segments=8)
    # The shoulder plates.
    for side in (-1, 1):
        poly = [(side * 4.4, 1.6), (side * 9.6, 0.2), (side * 9.8, -1.5), (side * 7.0, -3.4), (side * 4.0, -5.2)]
        plate = sh.inflate(f"shoulder{side}", [poly], rim_mat, sh.pillow_profile(1.1, 0.7, crown=0.3), bottom=0.0,
                           base=2.3, spacing=0.45)
        k.smooth(simplify_bottom(plate), 40)
    # The red lights in the upper corners and the blue canopy at the tip.
    for x in (-7.5, 7.5):
        k.smooth(k.ellipsoid(f"lamp{x}", (x, 10.9, 3.35), (1.05, 1.0, 0.6), lamp, 12, 6), 60)
    k.smooth(k.ellipsoid("canopy", (0.0, -7.9, 4.1), (1.9, 3.3, 1.6), blue, 20, 12), 60)


# --- 5 278: the lava star --------------------------------------------------------------------------

@model("lava_star", "5", 278)
def lava_star():
    """A star of lava crust, eight points (four long ones up, down and to the sides, four short
    ones on the diagonals) rising in ridges to its middle, bulging where the sprite glows and
    glowing there in the sprite's shades (its frames shrink it; the model keeps the first frame's
    size). It lies on the ground."""
    g = grid(art.E5_278, 24)
    rows = regions(g, lambda v, c, r: "#")
    shade = sampler(g, blur=1)
    bands = [(lowest, pal(f"lava_{index:x}", index, metallic=0.0, roughness=0.6, glow=glow))
             for lowest, index, glow in ((0.0, 0x71, 0.25), (3.0, 0x73, 0.4), (5.0, 0x75, 0.55), (6.5, 0x77, 0.7),
                                         (8.0, 0x79, 0.9), (10.0, 0x7b, 1.1), (12.5, 0x7d, 1.3))]

    def ridges(d, w):
        return np.minimum(0.95 * d, 6.0) + 0.25

    def bulge(x, y, z):
        return z + 0.9 * max(0.0, shade(x, y) - 5.0) / 10.0 * min(1.0, z / 1.5)
    star = part("star", rows, "#", bands[0][1], ridges, smooth=0, epsilon=0.6, spacing=0.4, z_fn=bulge, rim=0.3)
    paint_faces(star, shade_bands(g, bands, blur=0))
    simplify_bottom(star)
    k.smooth(star, 35)


# --- F 87: the fork ship ---------------------------------------------------------------------------

@model("fork_ship", "F", 87)
def fork_ship():
    """A tan ship shaped like a fork: a prong in the middle (a ridge along the hull), a grey fin at
    each side of it, swept wings reaching up at both sides, the hull narrowing to a point at the
    bottom with a port in its belly where a light glows; small blue-grey lights by the ridge."""
    g = grid(art.F87, 24)

    def where(v, c, r):
        if r <= 9 and 9 <= c <= 17 and v == 0x01:
            return "."  # the outlines between the prongs: the fork stays open
        if v >> 4 in (0, 6) and v & 15 >= 6:
            if r <= 6 and (9 <= c <= 11 or 15 <= c <= 17):
                return "f"
        return "#"
    rows = regions(g, where)
    tan = pal("fork_tan", 0x19, metallic=0.45, roughness=0.4)
    light = pal("fork_light", 0x1c, metallic=0.5, roughness=0.3)
    grey = pal("fork_grey", 0x0a, metallic=0.6, roughness=0.3)
    dark = pal("fork_dark", 0x11, metallic=0.3, roughness=0.6)
    glow = pal("fork_glow", 0x1e, metallic=0.0, roughness=0.2, glow=0.9, color=(255, 240, 200))
    stud = pal("fork_stud", 0x6c, metallic=0.6, roughness=0.2, glow=0.2)
    hull = part("hull", rows, "#", tan, sh.round_profile(0.8, max_height=3.6), smooth=1, epsilon=0.45,
                spacing=0.4, rim=0.25, grow=0.35)
    simplify_bottom(hull)
    decimate(hull, 1800)
    k.smooth(hull, 55)
    fins = part("fins", rows, "f", grey, sh.round_profile(1.0, max_height=1.8), smooth=1, epsilon=0.3, spacing=0.3,
                grow=0.45, base=0.0, min_area=0.5)
    k.smooth(fins, 50)
    # The ridge along the middle, from the prong's tip down the hull.
    cx = 1.5
    ridge = [(cx, y) for y in np.linspace(12.4, -3.0, 14)]
    tube("ridge", [(x, y, sh.surface_z(hull, x, y, 1.0) + 0.1) for x, y in ridge],
         [0.55, 0.65, 0.75, 0.85, 0.95, 1.0, 1.05, 1.05, 1.05, 1.0, 0.95, 0.85, 0.7, 0.5], light, segments=10)
    # Grey edges along the wings' inner sides.
    for side, path in ((-1, [(-5.3, 6.6), (-4.2, 4.6), (-3.0, 2.8)]), (1, [(6.3, 7.0), (5.3, 4.8), (4.3, 2.8)])):
        tube(f"wing_edge{side}", [(x, y, sh.surface_z(hull, x, y, 1.0) - 0.3) for x, y in path], 0.55, grey,
             segments=8)
    # The port and its light, the small lights by the ridge.
    z = sh.surface_z(hull, cx, -4.5, 3.0)
    k.smooth(k.ellipsoid("port", (cx, -4.6, z - 0.5), (1.8, 2.1, 0.8), dark, 16, 8), 60)
    k.smooth(k.ellipsoid("port_light", (cx, -4.7, z - 0.25), (1.1, 1.2, 0.75), glow, 12, 6), 60)
    for x, y in ((0.5, 2.2), (0.5, 1.4), (2.5, 1.4)):
        k.smooth(k.ellipsoid(f"stud{x}{y}", (x, y, sh.surface_z(hull, x, y, 3.0) - 0.1), (0.45, 0.45, 0.35), stud,
                             8, 4), 60)


# --- 8 125 / 8 127: the pink torpedo ---------------------------------------------------------------

def build_torpedo():
    """The whole torpedo, 48 x 28 pixels, centred on its middle (the halves' common edge): it lies
    along the screen's x, its glowing muzzle to the left, a grey barrel with a tan hatch, a brown
    collar with armour fins reaching up and down the screen (pink tips), and a bulbous pink body
    with two glowing red slits, narrowing to the right. Flat underneath (it lies on the ground)."""
    grey = pal("torpedo_grey", 0x09, metallic=0.6, roughness=0.3)
    hatch = pal("torpedo_hatch", 0x14, metallic=0.4, roughness=0.5)
    hatch_rim = pal("torpedo_hatch_rim", 0x41, metallic=0.4, roughness=0.6)
    collar = pal("torpedo_collar", 0xa5, metallic=0.5, roughness=0.4)
    armour = pal("torpedo_armour", 0x15, metallic=0.5, roughness=0.4)
    pink = pal("torpedo_pink", 0x48, metallic=0.35, roughness=0.35)
    tip = pal("torpedo_tip", 0x4a, metallic=0.35, roughness=0.3)
    red = pal("torpedo_red", 0x75, metallic=0.1, roughness=0.3, glow=0.7)
    hot = pal("torpedo_hot", 0x7b, metallic=0.0, roughness=0.3, glow=1.2)
    slit = pal("torpedo_slit", 0x78, metallic=0.0, roughness=0.3, glow=1.0)
    axis_y, squash = 2.5, 0.62
    axis_z = 3.2
    body = [(-18.2, 6.4), (-17.6, 6.6), (-7.0, 6.6), (-4.6, 7.1), (-2.5, 7.5), (0.0, 8.3), (3.0, 9.3), (5.0, 9.6),
            (10.0, 9.6),
            (14.5, 9.0), (17.5, 7.8), (20.0, 6.2), (22.0, 4.6), (23.3, 3.0), (23.9, 0.01)]
    hull = lathe_x("hull", [(-18.4, 0.01)] + k.profile(body, 0.7), grey, 28, y=axis_y, z=axis_z, squash=squash)
    sh.paint_x(hull, [(-4.4, 30.0, pink)])
    k.smooth(hull, 50)
    # The muzzle: a glowing cap with a hot core.
    k.smooth(lathe_x("muzzle", [(-21.6, 3.6), (-21.3, 4.5), (-19.5, 4.7), (-18.0, 4.4)], red, 24, y=axis_y - 0.6,
                     z=axis_z, squash=0.8), 50)
    k.smooth(lathe_x("muzzle_core", [(-24.0, 0.01), (-23.9, 1.8), (-23.4, 3.0), (-22.4, 3.8), (-21.0, 4.0),
                                     (-20.0, 3.6)], hot, 24, y=axis_y - 0.6, z=axis_z, squash=0.85), 50)
    for side in (-1, 1):  # the pink lips round the muzzle
        k.smooth(k.ellipsoid(f"lip{side}", (-19.8, axis_y - 0.6 + side * 4.4, axis_z), (1.5, 0.9, 1.3), pink, 12, 6),
                 60)
    # The tan hatch on the barrel.
    top = axis_z + 6.6 * squash
    k.smooth(simplify_bottom(sh.inflate("hatch_rim", [rounded_rect(-17.2, 0.4, -9.8, 4.6, 0.6)], hatch_rim,
                                        sh.pillow_profile(0.5, 0.3), bottom=0.0, base=top - 0.6, spacing=0.5)), 40)
    k.smooth(simplify_bottom(sh.inflate("hatch", [rounded_rect(-16.4, 1.1, -10.6, 3.9, 0.4)], hatch,
                                        sh.pillow_profile(0.55, 0.3), bottom=0.0, base=top - 0.45, spacing=0.5)), 40)
    # The collar and its armour fins (pink tips).
    k.smooth(lathe_x("collar", [(-7.2, 6.4), (-7.0, 7.0), (-4.6, 7.4), (-4.3, 7.1)], collar, 32, y=axis_y, z=axis_z,
                     squash=squash), 50)
    for side in (-1, 1):
        y0 = axis_y + side * 5.0
        y1 = axis_y + side * 10.1
        poly = [(-11.6, y0), (-0.3, y0), (-0.3, y1 - side * 0.6), (-1.3, y1), (-6.2, y1), (-9.6, y0 + side * 2.4)]
        fin = sh.inflate(f"fin{side}", [poly], armour, sh.pillow_profile(1.5, 0.6, crown=0.3), bottom=1.0,
                         base=axis_z + 1.2, spacing=0.6)
        k.smooth(fin, 40)
        k.smooth(k.ellipsoid(f"fin_tip{side}", (-4.5, axis_y + side * 10.3, axis_z + 0.6), (2.3, 1.6, 1.3), tip,
                             16, 8), 60)
    # A raised segment round the pink body, which the slits cut through, and a seam behind it.
    k.smooth(lathe_x("segment", [(2.6, 9.0), (3.2, 9.95), (8.3, 9.95), (8.9, 9.3)], tip, 40, y=axis_y, z=axis_z,
                     squash=squash), 50)
    k.smooth(lathe_x("seam", [(13.6, 8.9), (14.0, 9.35), (14.8, 9.2), (15.2, 8.7)], tip, 40, y=axis_y, z=axis_z,
                     squash=squash), 50)
    # The glowing slits on the pink body.
    for x in (4.5, 6.5):
        z = axis_z + 9.95 * squash
        k.smooth(k.ellipsoid(f"slit{x}", (x, axis_y + 0.4, z - 0.3), (0.55, 3.2, 0.6), slit, 12, 8), 60)
    return sh.flat_bottom(scene_objects())


def torpedo_half(left):
    objects = build_torpedo()
    x0, x1 = (-24.0, 0.0) if left else (0.0, 24.0)
    kept = sh.cut_box(objects, x0, x1, -14.0, 14.0)
    sh.move(kept, -(x0 + 12.0), 0.0)
    for obj in kept:
        k.smooth(obj, 50)


WHOLES["torpedo"] = (build_torpedo, (48, 28))
model("pink_torpedo_front", "8", 125)(lambda: torpedo_half(True))
model("pink_torpedo_rear", "8", 127)(lambda: torpedo_half(False))


# --- 4 269: a piece of the boss's pipe arm --------------------------------------------------------

def build_pipe_arm():
    """The brown pipe arm of TYRIAN's boss, 96 x 28 pixels (sprites 267, 269, 271, 273 side by side),
    centred on its middle: a pipe whose width follows the sprites' columns, narrowing and swelling
    at a joint and thickening at its right end; a grey clamp on its left part, a rib and a
    blue-grey bolt on the second piece. It lies on its layer (flat underneath)."""
    g = grid(art.E4_PIPE, 96)
    brown = pal("pipe_brown", 0x17, metallic=0.5, roughness=0.35)
    rib_mat = pal("pipe_rib", 0x19, metallic=0.55, roughness=0.3)
    clamp = pal("pipe_clamp", 0x6a, metallic=0.65, roughness=0.3)
    bolt = pal("pipe_bolt", 0x6c, metallic=0.7, roughness=0.2)
    squash = 0.7
    spans = []
    for c in range(96):
        rows = [r for r in range(len(g)) if g[r][c] is not None]
        top, bottom = rows[0], rows[-1]
        spans.append((c + 0.5 - 48.0, 14.0 - (top + bottom + 1) / 2.0, (bottom - top + 1) / 2.0))
    # Smoothed a little along the pipe, the ends kept.
    smooth_spans = []
    for i, (x, yc, r) in enumerate(spans):
        near = spans[max(0, i - 2):i + 3]
        smooth_spans.append((x, sum(s[1] for s in near) / len(near), sum(s[2] for s in near) / len(near)))
    smooth_spans[0] = (-48.0, smooth_spans[0][1], smooth_spans[0][2])
    smooth_spans[-1] = (48.0, smooth_spans[-1][1], smooth_spans[-1][2])
    rings = [k.ring(0.0, r, r * squash, 28) for x, yc, r in smooth_spans]
    # ring() builds in XZ at y; place each section across the pipe (along y) at its x.
    sections = []
    for (x, yc, r), points in zip(smooth_spans, rings):
        sections.append([Vector((x, yc + p.x, r * squash + p.z)) for p in points])
    pipe = k.loft("pipe", sections, brown, start_point=(smooth_spans[0][0], smooth_spans[0][1], smooth_spans[0][2] * squash),
                  end_point=(smooth_spans[-1][0], smooth_spans[-1][1], smooth_spans[-1][2] * squash))
    k.recalc_normals(pipe)
    k.smooth(pipe, 50)

    def band(name, x0, x1, mat, extra):
        out = []
        for x, yc, r in smooth_spans:
            if x0 - 0.6 <= x <= x1 + 0.6:
                rr = r + (extra if x0 <= x <= x1 else extra * 0.4)
                out.append([Vector((x, yc + p.x, r * squash + p.z)) for p in k.ring(0.0, rr, rr * squash, 28)])
        obj = k.loft(name, out, mat)
        k.recalc_normals(obj)
        return k.smooth(obj, 50)
    band("clamp", -40.5, -36.0, clamp, 0.45)
    band("rib", -16.5, -15.0, rib_mat, 0.35)
    band("rib2", -13.5, -12.2, rib_mat, 0.3)
    # The bolt on the side of the second piece (sprite 269's columns 13-16, rows 2-3).
    z = sh.surface_z(pipe, -9.2, 10.4, 5.0)
    k.smooth(k.ellipsoid("bolt", (-9.2, 10.4, z - 0.5), (1.6, 1.2, 1.0), bolt, 14, 8), 60)
    return sh.flat_bottom(scene_objects())


WHOLES["pipe_arm"] = (build_pipe_arm, (96, 28))


@model("pipe_arm_2", "4", 269)
def pipe_arm_2():
    objects = build_pipe_arm()
    kept = sh.cut_box(objects, -24.0, 0.0, -14.0, 14.0)
    sh.move(kept, 12.0, 0.0)
    for obj in kept:
        k.smooth(obj, 50)


# --- 8 245: the tip of a rock column -----------------------------------------------------------------

@model("rock_tip", "8", 245)
def rock_tip():
    """The lower tip of a narrow brown rock column (its upper part is sprite 207, above this one):
    a rough rock narrowing to a point, in the sprite's top right corner, cut flat at the sprite's
    top edge where the column goes on. A piece (origin): it stands on its layer."""
    g = grid(art.E8_245, 24)
    shade = sampler(g, blur=1)
    rows = regions(g, lambda v, c, r: "#")
    # The column goes on above the sprite: its top row repeated, so the cut at the edge is clean.
    rows = [rows[0]] * 4 + rows
    bands = [(0.0, pal("rock_dark", 0x14, metallic=0.05, roughness=0.8)),
             (2.5, pal("rock_mid", 0x16, metallic=0.05, roughness=0.75)),
             (4.5, pal("rock_brown", 0x17, metallic=0.05, roughness=0.7)),
             (6.5, pal("rock_light", 0x19, metallic=0.05, roughness=0.6))]

    def rough(x, y, z):
        if z < 0.3:
            return z
        return z + 0.35 * math.sin(1.7 * x + 0.9 * y) * math.sin(1.3 * y - 0.6 * x) + 0.12 * shade(x, min(y, 13.5))
    rock = part("rock", rows, "#", bands[0][1], sh.round_profile(1.3, max_height=4.4), origin=(12, 18), smooth=1,
                epsilon=0.3, spacing=0.35, z_fn=rough, sigma=1.0, rim=0.2)
    paint_faces(rock, shade_bands(g, bands, blur=1))
    kept = sh.cut_box([rock], -12.0, 12.0, -14.0, 14.0)
    for obj in kept:
        simplify_bottom(obj)
        k.smooth(obj, 55)


# --- U 1: the top left corner of DELI's tower -----------------------------------------------------

@model("deli_tower_tl", "U", 1)
def deli_tower_tl():
    """What of DELI's tower lies in its top left sprite (the tower is 72 x 56 pixels, U 1, 3, 5 above
    39, 41, 43): the top of a red column with a grey cap and a block at its foot, at the bottom right,
    and the top of a thin red pipe at the bottom; both go on into the sprites below and to the right
    (cut at the edges). A piece (origin), standing on the ground."""
    grey = pal("tower_grey", 0x09, metallic=0.6, roughness=0.3)
    cap = pal("tower_cap", 0x0c, metallic=0.6, roughness=0.25)
    pink = pal("tower_pink", 0x48, metallic=0.4, roughness=0.35)
    dark = pal("tower_dark", 0x44, metallic=0.4, roughness=0.5)
    # The column: lying up the screen as the sprite draws it, its cap at the top.
    k.smooth(k.lathe("column", [(-16.0, 2.5), (-8.6, 2.5), (-8.2, 2.8), (-7.6, 2.8), (-7.3, 2.5)], pink, 24,
                     axis_x=10.0, axis_z=3.4), 50)
    k.smooth(k.lathe("cap", [(-7.6, 2.75), (-7.0, 2.9), (-5.6, 2.9), (-5.2, 2.5), (-4.9, 1.6), (-4.75, 0.01)], cap, 24,
                     axis_x=10.0, axis_z=3.4), 50)
    k.smooth(lathe_x("cap_band", [(7.0, 2.9), (7.2, 3.1), (12.8, 3.1), (13.0, 2.9)], grey, 20, y=-7.9, z=3.4), 50)
    # The block at the column's foot and the thin pipe.
    block = sh.inflate("block", [rounded_rect(3.6, -16.0, 9.0, -10.8, 0.6)], dark, sh.pillow_profile(3.0, 0.6),
                       bottom=0.0, spacing=0.4)
    k.smooth(simplify_bottom(block), 40)
    k.smooth(k.lathe("pipe", [(-16.0, 1.15), (-12.6, 1.15), (-12.3, 0.9), (-12.1, 0.01)], pink, 14, axis_x=-3.0,
                     axis_z=3.2), 50)
    kept = sh.cut_box(sh.flat_bottom(scene_objects()), -12.0, 12.0, -14.0, 14.0)
    for obj in kept:
        k.smooth(obj, 50)


# --- coins 89: the bomb pick-up --------------------------------------------------------------------

@model("bomb_pickup", "coins", 89, kind="items")
def bomb_pickup():
    """The pick-up of a super bomb: the word BOMB down its left side in raised letters glowing in the
    sprite's fire shades on a dark red backing, and a blue-grey bomb beside it (a dome, a glowing blue
    band, a tail with four fins), lying up the screen. No spin: the letters must stay readable."""
    g = grid(art.BOMB, 24)
    letters = regions(g, lambda v, c, r: ("#" if v & 15 >= 2 else "o") if c <= 11 else ".")
    backing = pal("bomb_backing", 0x72, metallic=0.2, roughness=0.5, glow=0.2)
    fire = [(lowest, pal(f"bomb_fire_{index:x}", index, metallic=0.1, roughness=0.4, glow=glow))
            for lowest, index, glow in ((0.0, 0x76, 0.6), (6.5, 0x78, 0.8), (8.5, 0x7a, 1.0), (10.5, 0x7c, 1.2))]
    plate = part("letter_backing", letters, "#o", backing, sh.pillow_profile(1.0, 0.5), smooth=1, epsilon=0.5,
                 spacing=0.7)
    k.smooth(planar(simplify_bottom(plate)), 40)
    word = part("letters", letters, "#", fire[0][1], sh.pillow_profile(1.4, 0.45), smooth=0, epsilon=0.3,
                spacing=0.38, base=0.6, grow=0.1)
    paint_faces(word, shade_bands(g, fire, blur=0, low=0.9))
    k.smooth(planar(simplify_bottom(word)), 35)
    # The bomb.
    shell = pal("bomb_shell", 0x3b, metallic=0.35, roughness=0.25)
    shell_dark = pal("bomb_shell_dark", 0x39, metallic=0.35, roughness=0.3)
    band = pal("bomb_band", 0x99, metallic=0.2, roughness=0.15, glow=0.4)
    ax, az = 5.5, 2.6
    k.smooth(k.lathe("dome", [(4.0, 4.3), (4.6, 4.9), (6.5, 5.3), (8.5, 5.0), (10.2, 4.1), (11.3, 2.8), (11.9, 1.3),
                              (12.1, 0.01)], shell, 28, axis_x=ax, axis_z=az, squash=0.62), 50)
    k.smooth(k.lathe("band", [(-0.9, 3.9), (-0.7, 4.3), (4.2, 4.3), (4.4, 3.9)], band, 28, axis_x=ax, axis_z=az,
                     squash=0.62), 50)
    k.smooth(k.lathe("tail", [(-10.0, 0.01), (-9.9, 1.6), (-9.0, 2.2), (-4.0, 3.0), (-1.4, 3.8), (-0.6, 3.9)],
                     shell_dark, 24, axis_x=ax, axis_z=az, squash=0.62), 50)
    for side in (-1, 1):  # the fins at the sides, flat
        fin = [(ax + side * 2.0, -1.4), (ax + side * 6.0, -4.0), (ax + side * 6.2, -9.0), (ax + side * 5.2, -10.4),
               (ax + side * 2.0, -9.2)]
        if side < 0:
            fin = fin[::-1]
        k.smooth(k.slab(f"fin{side}", fin, az - 0.45, az + 0.45, shell, bevel_width=0.3), 40)
    # The fin standing up the middle.
    up = [(-1.4, 0.0), (-4.0, 4.3), (-9.0, 4.6), (-10.4, 3.6), (-9.2, 0.0)]
    top_fin = k.slab("fin_top", [(y, z) for y, z in up], -0.45, 0.45, shell, bevel_width=0.3)
    top_fin.data.transform(Matrix.Translation((ax, 0, az)) @ Matrix(((0, 0, 1, 0), (1, 0, 0, 0), (0, 1, 0, 0),
                                                                      (0, 0, 0, 1))))
    k.recalc_normals(top_fin)
    k.smooth(top_fin, 40)
    sh.flat_bottom(scene_objects())


# --- Main ------------------------------------------------------------------------------------------

def triangles(obj):
    return sum(len(p.vertices) - 2 for p in obj.data.polygons)


def main():
    options = k.args()
    if "whole" in options:
        build, size = WHOLES[options["whole"]]
        k.reset()
        build()
        bpy.context.scene.view_settings.view_transform = "Standard"
        k.preview(options["preview"] + options["whole"], size, scale=8)
        return
    only = set(options["only"].split(",")) if "only" in options else None
    for name, build, sheet, sprites, size, kind in MODELS:
        if only and name not in only:
            continue
        k.reset()
        build()
        for obj in scene_objects():
            sh.apply_modifiers(obj)
            planar(obj, 1.0)
        total = sum(triangles(o) for o in scene_objects())
        print(f"--- {name}: {total} triangles")
        if "stats" in options:
            for obj in sorted(scene_objects(), key=triangles, reverse=True)[:8]:
                print(f"    {obj.name}: {triangles(obj)}")
        if "check" in options and sheet is not None:
            sheet_file = "coins.png" if sheet == "coins" else f"enemy_{sheet}.png"
            k.check_silhouette(os.path.join(options["check"], sheet_file), sprites, large=size[0] > 12)
        k.export(os.path.join(ROOT, kind, name + ".glb"))
        if "preview" in options:
            # The game shows colours as they are (no filmic tone mapping): so do the previews.
            bpy.context.scene.view_settings.view_transform = "Standard"
            k.preview(options["preview"] + name, size)


main()
