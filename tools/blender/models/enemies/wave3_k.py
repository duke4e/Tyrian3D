"""Batch K of wave 3: the remaining enemies of sheet I (SAVARA, SAVARA V, SAVARA Y), two large
objects the game draws from several 2x2 sprites, each built whole and cut into the sprites' pieces
(models.cfg: origin, yaw=0, authored as the sprites look):

- zeppelin_<sprite> (I 3, 5, 39, 41, 43, 45, 77, 79, 81, 83, 115, 117, 119, 121, 154, 156, 158):
  the grey airship, 96 x 130 pixels, its nose down the screen. A netted envelope; at its stern a
  red ducted fan ring with white blades turning under a grey bridge that carries a row of red lights;
  swept grey fins and red frames on its back, a red sensor pod; two long gun pods hang at its
  sides on red struts, their muzzles glowing. It floats a little above its layer. The animation
  frames of I 3, 5, 41 and 43 (17, 55, 93, 131) turn the fan's blades: the model keeps them still.
- redwing_<sprite> (I 201, 203, 237, 239, 241, 243, 278): the red and grey propeller-less fighter,
  96 x 80 pixels, nose down the screen: a red beak with intakes at its cheeks, two black canopies at
  the wing roots, a grey spine, straight wings with red panels and vents, two engine nacelles on a
  tailplane with fins at its tips and a fin in the middle.

usage: Blender -b --factory-startup -P wave3_k.py -- [--only name,name] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1] [--whole <prefix>]
--only takes object names (zeppelin, redwing) or piece names; --whole renders the whole objects
(<prefix><object>_top.png, _3q.png) instead of exporting.
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
import tyrkit as k  # noqa: E402
import wave1_d_shapes as sh  # noqa: E402
import wave2_f_kit as w  # noqa: E402
from wave2_f_kit import pal  # noqa: E402

ENEMIES = w.ENEMIES


# --- Helpers ---------------------------------------------------------------------------------------

def tube(name, points, radius, mat, segments=12, squash=1.0, smooth_angle=60, caps=True):
    """A tube through 3D points with rounded ends; radius a number or one per point; squash scales
    its cross-section towards the up direction (a band taller or flatter than wide)."""
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
    obj = k.loft(name, rings, mat, start_point=pts[0] - t0 * radii[0] * 0.6, end_point=pts[-1] + t1 * radii[-1] * 0.6)
    return k.smooth(obj, smooth_angle)


def lathe_y(name, profile, mat, x, z, segments=24, squash=1.0, smooth_angle=50):
    """A turned part along Y: profile is (y, radius) pairs in increasing y."""
    return k.smooth(k.lathe(name, profile, mat, segments=segments, axis_x=x, axis_z=z, squash=squash), smooth_angle)


def rounded_section(r0, r1, t0, t1, round_=0.5, steps=3):
    """A closed cross-section (radius, height) for revolve(): the rectangle r0..r1, t0..t1 with its
    corners rounded."""
    pts = []
    for (cr, ct), start in (((r1 - round_, t0 + round_), -90), ((r1 - round_, t1 - round_), 0),
                            ((r0 + round_, t1 - round_), 90), ((r0 + round_, t0 + round_), 180)):
        for i in range(steps + 1):
            a = math.radians(start + 90 * i / steps)
            pts.append((cr + round_ * math.cos(a), ct + round_ * math.sin(a)))
    return pts


def revolve(name, section, mat, centre, axis, side, segments=48):
    """A ring: the closed section [(radius, height along axis)] turned about axis through centre
    (side: a direction perpendicular to the axis, where the turn starts)."""
    axis, side = Vector(axis).normalized(), Vector(side).normalized()
    other = axis.cross(side)
    verts, faces, n = [], [], len(section)
    for j in range(segments):
        a = 2 * math.pi * j / segments
        radial = side * math.cos(a) + other * math.sin(a)
        verts += [Vector(centre) + radial * r + axis * h for r, h in section]
    for j in range(segments):
        for i in range(n):
            a, b = j * n + i, j * n + (i + 1) % n
            c, d = ((j + 1) % segments) * n + (i + 1) % n, ((j + 1) % segments) * n + i
            faces.append((a, b, c, d))
    obj = k.mesh_object(name, verts, faces, mat)
    k.recalc_normals(obj)
    return k.smooth(obj, 50)


def paint(obj, fn):
    """Gives each face the material fn(face centre, normal) returns (None: keep)."""
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


def cut_lines(obj, xs=(), ys=()):
    """Cuts the faces of obj along the planes x = each of xs and y = each of ys (so that painting
    by position gets straight borders)."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    for value, normal in [(x, (1, 0, 0)) for x in xs] + [(y, (0, 1, 0)) for y in ys]:
        geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
        co = (value, 0, 0) if normal[0] else (0, value, 0)
        bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-5, plane_co=co, plane_no=normal)
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def mirror(objects, axis_x):
    return w.mirror(objects, axis_x)


def triangles(obj):
    return sum(len(p.vertices) - 2 for p in obj.data.polygons)


def planar(obj, degrees=1.0):
    """Merges nearly flat stretches into larger faces (keeping material borders), then
    triangulates: flat parts cost few triangles."""
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


# --- The zeppelin (I 3 ... 158) -------------------------------------------------------------------
# The whole airship in pixel coordinates of its 96 x 140 block of the sheet (columns 0-95, rows
# 0-139, sprite I 3 at column 24, row 0): x = column - 48, y = 70 - row (pixel edges). It is
# symmetric about column 48's middle (x = 0.5).

ZX = 0.5      # its axis
ZC = 17.0     # the envelope's axis height (its underside about 2 above the layer)
SQ = 0.44     # the envelope's height over its width


def zx(col):
    """A pixel column's centre."""
    return col + 0.5 - 48


def zy(row):
    """A pixel row's centre."""
    return 70 - (row + 0.5)


# The envelope's half-width along it (y, half-width), measured from the sprite's outline; the stern
# end is under the fan's bridge, the nose at the bottom.
HULL = [(-70.3, 0.01), (-70.0, 3.2), (-69.5, 5.6), (-68.5, 8.5), (-67.5, 10.5), (-65.5, 13.5), (-63.5, 16.5),
        (-60.5, 19.5), (-57.5, 22.5), (-54.5, 24.6), (-50.5, 27.5), (-46.5, 29.5), (-42.5, 30.8), (-38.5, 32.4),
        (-34.5, 33.6), (-30.5, 34.4), (-24.0, 34.6), (-10.0, 34.6), (4.5, 34.5), (7.5, 34.0), (13.5, 33.0),
        (19.5, 30.8), (25.5, 27.4), (31.5, 23.0), (35.5, 19.8), (38.5, 16.2), (40.5, 12.6), (41.5, 10.0),
        (42.3, 6.0), (42.6, 0.01)]
_HULL_SAMPLES = None


def hull_radius(y):
    global _HULL_SAMPLES
    if _HULL_SAMPLES is None:
        _HULL_SAMPLES = k.profile(HULL, 0.25)
    s = _HULL_SAMPLES
    if y <= s[0][0] or y >= s[-1][0]:
        return 0.0
    for (y0, r0), (y1, r1) in zip(s, s[1:]):
        if y0 <= y <= y1:
            return r0 + (r1 - r0) * (y - y0) / max(y1 - y0, 1e-6)
    return 0.0


def hull_top(x, y):
    """The envelope's top at (x, y) (its axis height outside it)."""
    r = hull_radius(y)
    d = abs(x - ZX)
    if r <= 0 or d >= r:
        return ZC
    return ZC + SQ * r * math.sqrt(1 - (d / r) ** 2)


def zeppelin_whole():
    """The whole airship (see the module's docstring)."""
    hull = pal("zep_hull", 10, metallic=0.1, roughness=0.55)
    net = pal("zep_net", 12, metallic=0.1, roughness=0.45)
    steel = pal("zep_steel", 8, metallic=0.6, roughness=0.32)
    steel_light = pal("zep_steel_light", 10, metallic=0.6, roughness=0.28)
    dark = pal("zep_dark", 2, metallic=0.3, roughness=0.6)
    red = pal("zep_red", 71, metallic=0.45, roughness=0.32)
    red_dark = pal("zep_red_dark", 69, metallic=0.45, roughness=0.35)
    red_ring = pal("zep_red_ring", 72, metallic=0.45, roughness=0.3)
    red_pod = pal("zep_red_pod", 73, metallic=0.4, roughness=0.25)
    blade = pal("zep_blade", 15, metallic=0.2, roughness=0.3)
    lamp = pal("zep_lamp", 119, roughness=0.2, glow=2.2, emission=(255, 40, 10))
    muzzle = pal("zep_muzzle", 121, roughness=0.2, glow=3.0, emission=(255, 120, 30))
    glass = pal("zep_glass", 1, metallic=0.5, roughness=0.12)

    # The envelope.
    env = lathe_y("hull", k.profile(HULL, 1.0), hull, ZX, ZC, segments=48, squash=SQ, smooth_angle=70)
    # The net over it: girders along it, converging at the nose, and a few hoops bowed towards it.
    def on_hull(x, y, lift=0.0):
        return (x, y, hull_top(x, y) + lift)
    for f in (-0.74, -0.42, 0.0, 0.42, 0.74):
        y_end = -5.5 if f == 0.0 else 22.0 - 10.0 * abs(f)
        ys = [-69.6 + t * (y_end + 69.6) / 40 for t in range(41)]
        pts = [on_hull(ZX + f * hull_radius(y), y, -0.12) for y in ys]
        tube(f"girder{f}", pts, 0.3, net, segments=6, squash=0.8)
    for y0, bow in ((-31.0, 5.0), (-46.0, 5.0), (-59.0, 4.0)):
        pts = []
        for i in range(25):
            t = -0.94 + 1.88 * i / 24
            y = y0 - bow * (1 - t * t)
            pts.append(on_hull(ZX + t * hull_radius(y), y, -0.12))
        tube(f"hoop{y0}", pts, 0.27, net, segments=6, squash=0.8)

    # The stern: the fan's red duct, a short tube whose top leans forward (seen from above, a thick
    # crescent at the back and thin sides, as the sprite draws it), its front sunk in the envelope;
    # the fan's white blades in it and the grey bridge with its red lamps from its back to the stern.
    t = math.radians(35.0)
    centre, radius, height = Vector((ZX, 37.0, 17.5)), 22.6, 10.0
    axis, back, side = Vector((0, -math.sin(t), math.cos(t))), Vector((0, math.cos(t), math.sin(t))), Vector((1, 0, 0))
    section = rounded_section(radius - 0.8, radius + 0.8, -height / 2, height / 2, 0.6)
    revolve("duct", section, red_ring, centre, axis, side, 60)
    for end_, mat in ((height / 2, red), (-height / 2, red_ring)):
        revolve(f"duct_rim{end_:.0f}", rounded_section(radius - 1.3, radius + 1.3, end_ - 0.7, end_ + 0.7, 0.5, 2),
                mat, centre, axis, side, 60)
    hub = centre - axis * 1.2
    for angle in (40.0, 140.0):
        a = math.radians(angle)
        d = side * math.cos(a) + back * math.sin(a)
        q = (-side * math.sin(a) + back * math.cos(a)).normalized()
        outline = [(4.5, -1.8), (16.6, -3.0), (19.0, -2.4), (20.0, -0.6), (19.4, 1.8), (16.6, 3.4), (4.5, 2.0)]
        b = k.slab(f"blade{angle:.0f}", outline, -0.3, 0.3, blade, bevel_width=0.12)
        sh.apply_modifiers(b)
        basis = Matrix(((d.x, q.x, axis.x, hub.x), (d.y, q.y, axis.y, hub.y), (d.z, q.z, axis.z, hub.z), (0, 0, 0, 1)))
        b.data.transform(basis @ Matrix.Rotation(math.radians(8 if angle < 90 else -8), 4, "X"))
        k.smooth(b, 30)
    # The bridge: two rails sloping from the duct's back down to the hub dome on the stern, a dark
    # channel between them with five red lamps, a clamp where it holds the duct.
    p0, p1 = Vector((ZX, 39.5, 25.0)), Vector((ZX, 57.6, 31.4))
    slope = math.atan2(p1.z - p0.z, p1.y - p0.y)

    def along(name, y0, y1, x, width, height_, lift, mat, bevel):
        a0, a1 = p0.lerp(p1, (y0 - p0.y) / (p1.y - p0.y)), p0.lerp(p1, (y1 - p0.y) / (p1.y - p0.y))
        box = w.rounded_box(name, (0, 0, 0), (width, (a1 - a0).length, height_), mat, bevel=bevel)
        sh.apply_modifiers(box)
        mid = (a0 + a1) / 2
        box.data.transform(Matrix.Translation((x, mid.y, mid.z)) @ Matrix.Rotation(slope, 4, "X") @
                           Matrix.Translation((0, 0, lift)))
        return box
    along("rail_l", p0.y, p1.y, -3.5, 3.0, 3.6, 0.0, steel_light, 0.7)
    along("rail_r", p0.y, p1.y, 4.5, 3.0, 3.6, 0.0, steel_light, 0.7)
    along("channel", p0.y + 0.4, p1.y - 0.4, ZX, 5.4, 2.4, -0.9, dark, 0.3)
    for i, (y, h) in enumerate(((55.5, 1.0), (53.5, 1.0), (51.0, 2.0), (48.0, 2.0), (45.0, 2.0))):
        along(f"lamp{i}", y - h * 0.45, y + h * 0.45, ZX + 0.5, 4.0, 0.9, 0.5, lamp, 0.25)
    clamp = w.rounded_box("clamp", (0, 0, 0), (13.6, 3.6, 10.4), steel, bevel=1.0)
    sh.apply_modifiers(clamp)
    c = centre + back * radius
    clamp.data.transform(Matrix.Translation(c) @ Matrix.Rotation(t, 4, "X"))
    # The hub dome on the stern, under the bridge's end.
    w.sphere("hub_dome", (ZX, 33.0, hull_top(ZX, 33.0) - 0.6), (5.6, 7.0, 3.4), steel_light, 24, 12)
    # The swept fins on the stern's flanks that hold the duct's sides, sloping down to them.
    root_z = hull_top(-10.5, 32.0) - 0.4
    fin_rings = []
    for x, y0, y1, th in ((-22.4, 30.6, 38.2, 1.3), (-18.0, 27.6, 38.8, 1.6), (-14.0, 25.6, 39.2, 1.8),
                          (-10.5, 24.6, 39.4, 2.0)):
        f = (x + 22.4) / 11.9
        zc_ = 18.4 + (root_z - 18.4) * f ** 0.8
        yc, half = (y0 + y1) / 2, (y1 - y0) / 2
        fin_rings.append([Vector((x, yc + half * math.cos(2 * math.pi * j / 16) * (0.9 if math.cos(2 * math.pi * j / 16)
                                                                                        > 0 else 1.0),
                                  zc_ + th / 2 * math.sin(2 * math.pi * j / 16))) for j in range(16)])
    fin = k.loft("stern_fin", fin_rings, steel)
    k.smooth(fin, 50)
    mirror([fin], ZX)

    # The red frames on the back: two brackets beside the hub, the frame like a gate below it with
    # its feet, and the red sensor pod further down.
    def bar(name, x0, x1, y0, y1, height=1.6, mat=red):
        cx, cy_ = (x0 + x1) / 2, (y0 + y1) / 2
        z = max(hull_top(x, y) for x in (x0, x1) for y in (y0, y1))
        w.rounded_box(name, (cx, cy_, z + height / 2 - 0.5), (x1 - x0, y1 - y0, height + 0.6), mat, bevel=0.45)
    bar("bracket_l", -11.0, -8.2, 26.6, 33.0)
    bar("bracket_l_prong", -11.0, -5.2, 29.0, 31.8)
    bar("bracket_r", 9.0, 11.6, 26.6, 33.0)
    bar("bracket_r_prong", 6.0, 11.6, 29.0, 31.4)
    bar("gate_stem", -1.0, 2.0, 24.0, 28.6, 1.4)
    bar("gate_bar", -7.0, 8.0, 21.6, 25.0, 2.0)
    for name, x, y1 in (("gate_leg_li", -3.0, 8.0), ("gate_leg_ri", 4.2, 8.6), ("gate_leg_lo", -8.4, 11.2),
                        ("gate_leg_ro", 7.6, 11.2)):
        pts = [(x, y, hull_top(x, y) + 0.35) for y in (22.5, (22.5 + y1) / 2, y1)]
        tube(name, pts, 0.95, red, segments=8, squash=0.9)
    bar("gate_foot_l", -9.2, -2.2, 10.6, 12.4, 1.2, red_dark)
    bar("gate_foot_r", 3.4, 8.6, 10.6, 12.4, 1.2, red_dark)
    zp = hull_top(ZX, 0.2)
    w.sphere("pod", (ZX, 0.2, zp + 0.2), (2.7, 5.1, 2.1), red_pod, 20, 12)
    w.sphere("pod_slot", (ZX, 0.4, zp + 1.55), (1.05, 3.2, 0.9), glass, 14, 8)
    w.sphere("pod_ring", (ZX, 0.2, zp - 0.3), (3.4, 5.9, 1.2), red_dark, 20, 8)

    # The gun pod on the left (mirrored to the right): a grey body hanging beside the envelope with
    # a red band and a red pipe along its top, a red mount at its upper end on a strut to the
    # envelope and a curved red pipe from the envelope's back, a thin red barrel and a grey muzzle
    # glowing at its end.
    gx, gz = -41.8, 13.0
    hang = [  # the pod itself, leaning out a little towards its muzzle
        lathe_y("gun_body", [(-22.4, 0.01), (-22.2, 2.6), (-21.4, 4.3), (-19.5, 4.8), (6.0, 4.6), (7.6, 4.0),
                             (8.2, 0.01)], steel, gx, gz, 24),
        lathe_y("gun_band", [(-10.0, 4.6), (-9.7, 5.25), (-5.0, 5.25), (-4.7, 4.6)], red, gx, gz, 24),
        lathe_y("gun_band2", [(-19.0, 4.6), (-18.7, 5.1), (-17.0, 5.1), (-16.7, 4.6)], red_dark, gx, gz, 24),
        tube("gun_pipe", [(gx, 8.5, gz + 4.6), (gx, 2.0, gz + 4.9), (gx, -4.5, gz + 4.9)], 1.15, red, segments=10),
        lathe_y("gun_barrel", [(-30.0, 1.6), (-21.0, 1.6)], red, gx, gz, 16),
        lathe_y("gun_muzzle", [(-35.4, 2.6), (-35.0, 3.3), (-30.2, 3.3), (-29.6, 2.4), (-29.5, 0.01)], steel_light,
                gx, gz, 20),
        lathe_y("gun_fire", [(-36.0, 0.01), (-35.95, 1.4), (-35.4, 2.1), (-35.3, 0.01)], muzzle, gx, gz, 16),
    ]
    w.transform(hang, Matrix.Translation((gx, 12.0, 0)) @ Matrix.Rotation(math.radians(-3.2), 4, "Z") @
                Matrix.Translation((-gx, -12.0, 0)))
    gun = list(hang)
    gun.append(w.rounded_box("gun_mount", (gx - 0.2, 12.3, gz + 0.4), (8.4, 7.6, 9.4), red, bevel=1.2))
    gun.append(w.rounded_box("gun_mount_plate", (gx - 0.2, 12.3, gz + 5.0), (5.6, 5.0, 0.8), red_dark, bevel=0.3))
    gun.append(w.sphere("gun_cap", (-38.6, 18.4, gz + 2.0), (4.0, 2.6, 3.2), steel, 20, 10))
    gun.append(w.rounded_box("gun_strut", (-34.2, 12.9, gz + 1.4), (8.0, 6.2, 3.2), steel, bevel=0.8))
    gun.append(w.rounded_box("gun_strut_bar", (-33.6, 10.3, gz + 2.4), (9.6, 1.9, 2.2), red, bevel=0.5))
    gun.append(w.rounded_box("gun_arm", (-31.0, 22.9, 20.0), (11.0, 3.6, 2.4), steel, bevel=0.6))
    pipe = [(-25.6, 23.6, hull_top(-25.6, 23.6) - 0.2), (-30.0, 23.6, 21.9), (-34.0, 23.4, 21.6),
            (-36.8, 22.4, 20.6), (-38.4, 20.4, 19.2), (-38.8, 18.6, 17.8)]
    gun.append(tube("gun_hose", w.catmull(pipe, 0.7), 1.2, red, segments=10))
    mirror(gun, ZX)


ZEPPELIN_PIECES = [  # (sprite, x0, x1, y0, y1)
    (3, -24, 0, 42, 70), (5, 0, 24, 42, 70),
    (39, -48, -24, 14, 42), (41, -24, 0, 14, 42), (43, 0, 24, 14, 42), (45, 24, 48, 14, 42),
    (77, -48, -24, -14, 14), (79, -24, 0, -14, 14), (81, 0, 24, -14, 14), (83, 24, 48, -14, 14),
    (115, -48, -24, -42, -14), (117, -24, 0, -42, -14), (119, 0, 24, -42, -14), (121, 24, 48, -42, -14),
    (154, -36, -12, -70, -42), (156, -12, 12, -70, -42), (158, 12, 36, -70, -42),
]


# --- The red fighter (I 201 ... 278) --------------------------------------------------------------
# The whole plane in pixel coordinates of its 96 x 84 block of the sheet (columns 96-191, rows
# 140-223): x = column - 144, y = 182 - row (pixel edges); symmetric about column 144's middle.

PX = 0.5      # its axis
PZ = 7.5      # the fuselage's axis height
PSQ = 0.7     # the fuselage's height over its width

FUSELAGE = [(-41.0, 0.01), (-40.3, 0.9), (-38.5, 1.8), (-36.5, 2.8), (-34.5, 3.7), (-32.5, 4.5), (-30.5, 5.3),
            (-28.0, 6.4), (-25.0, 6.9), (-21.0, 7.2), (-16.5, 7.6), (-13.5, 8.8), (-10.0, 10.1), (-5.0, 10.6),
            (5.0, 10.6), (12.0, 10.4), (15.5, 9.6), (18.0, 7.8), (20.5, 6.4), (24.0, 6.0), (30.0, 5.8), (33.5, 5.0),
            (35.5, 3.6), (36.6, 1.8), (37.0, 0.01)]
_FUSELAGE_SAMPLES = None


def fuselage_radius(y):
    global _FUSELAGE_SAMPLES
    if _FUSELAGE_SAMPLES is None:
        _FUSELAGE_SAMPLES = k.profile(FUSELAGE, 0.25)
    s = _FUSELAGE_SAMPLES
    if y <= s[0][0] or y >= s[-1][0]:
        return 0.0
    for (y0, r0), (y1, r1) in zip(s, s[1:]):
        if y0 <= y <= y1:
            return r0 + (r1 - r0) * (y - y0) / max(y1 - y0, 1e-6)
    return 0.0


def fuselage_top(x, y):
    r = fuselage_radius(y)
    d = abs(x - PX)
    if r <= 0 or d >= r:
        return PZ
    return PZ + PSQ * r * math.sqrt(1 - (d / r) ** 2)


def yz_plate(name, outline, x, thickness, mat, bevel=0.3, cant=0.0):
    """A vertical plate (a fin): outline [(y, z), ...] counter-clockwise, `thickness` wide in x
    around x, leaning outwards by `cant` degrees (positive: its top towards +x)."""
    plate = k.slab(name, outline, -thickness / 2, thickness / 2, mat, bevel_width=bevel)
    sh.apply_modifiers(plate)
    base_z = min(z for _, z in outline)
    swap = Matrix(((0, 0, 1, 0), (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 0, 1)))  # (a, b, c) -> (c, a, b)
    plate.data.transform(Matrix.Translation((x, 0, base_z)) @ Matrix.Rotation(math.radians(-cant), 4, "Y") @
                         Matrix.Translation((0, 0, -base_z)) @ swap)
    k.recalc_normals(plate)
    return k.smooth(plate, 35)


def redwing_whole():
    """The whole fighter (see the module's docstring)."""
    red = pal("rw_red", 70, metallic=0.4, roughness=0.32)
    red_light = pal("rw_red_light", 73, metallic=0.4, roughness=0.28)
    red_dark = pal("rw_red_dark", 67, metallic=0.4, roughness=0.4)
    grey = pal("rw_grey", 6, metallic=0.6, roughness=0.32)
    grey_light = pal("rw_grey_light", 9, metallic=0.6, roughness=0.28)
    dark = pal("rw_dark", 2, metallic=0.3, roughness=0.55)
    glass = pal("rw_glass", 1, metallic=0.6, roughness=0.08)

    # The fuselage: red, its tail grey; a grey spine along its back from the tail to the canopies.
    body = lathe_y("fuselage", k.profile(FUSELAGE, 0.8), red, PX, PZ, segments=36, squash=PSQ, smooth_angle=60)
    paint(body, lambda c, n: grey if c.y > 17.5 else None)
    spine = [(PX, y, fuselage_top(PX, y) - 0.9) for y in [36.0 - i * 1.5 for i in range(27)]]
    tube("spine", spine, [min(3.4, 0.55 * fuselage_radius(y) + 0.4) for _, y, _ in spine], grey_light, segments=14,
         squash=0.55)
    # Slats on the red sides behind the canopies.
    for side in (-1, 1):
        for i, y in enumerate((14.8, 12.4, 10.0, 7.6, 5.2)):
            pts = []
            for j in range(6):
                d = 4.4 + 5.4 * j / 5
                x = PX + side * d
                pts.append((x, y, fuselage_top(x, y) + 0.05))
            tube(f"slat{side}{i}", pts, 0.42, red_dark, segments=6, squash=0.8)
    # The beak: a ridge along its top, a collar near its tip, the cheeks' intakes.
    ridge = [(PX, y, fuselage_top(PX, y) - 0.25) for y in [-13.0 - i * 1.5 for i in range(17)]]
    tube("ridge", ridge, [max(0.5, min(1.3, 0.2 * fuselage_radius(y))) for _, y, _ in ridge], red_light, segments=10,
         squash=0.7)
    for i, (y, r, length) in enumerate(((-27.2, 7.4, 1.8),)):
        w.lathe_axis(f"collar{i}", [(0.0, r - 0.7), (0.3, r), (length - 0.3, r), (length, r - 0.7)], red_dark,
                     (PX, y, PZ), (0, -1, 0), 32, squash=PSQ)
    for side in (-1, 1):
        x = side * 8.1
        lathe_y(f"cheek{side}", [(-23.6, 0.01), (-23.4, 1.2), (-22.6, 1.9), (-15.0, 1.9), (-13.4, 1.4), (-12.8, 0.01)],
                red_dark, x, PZ + 1.6, 16, squash=1.3)
        w.sphere(f"cheek_intake{side}", (x, -23.3, PZ + 1.6), (1.3, 0.5, 1.8), dark, 12, 6)
    # The canopies at the wing roots, set in red frames, and the small dark window between them.
    for side in (-1, 1):
        x = PX + side * 8.2
        z = fuselage_top(x, -7.0)
        w.sphere(f"canopy_frame{side}", (PX + side * 8.4, -6.8, z - 1.4), (5.5, 7.2, 3.6), red, 28, 14)
        w.sphere(f"canopy{side}", (PX + side * 8.0, -6.6, z + 0.4), (3.7, 5.3, 2.8), glass, 28, 14)
    w.sphere("window", (PX, -1.0, fuselage_top(PX, -1.0) - 0.3), (3.6, 3.0, 1.9), glass, 20, 10)

    # The wings: straight trailing edges, the leading edges swept near the roots; grey with red
    # panels and vents, a little dihedral.
    wing_l = [(-43.0, 13.0), (-8.0, 13.0), (-8.0, -14.0), (-13.0, -14.0), (-14.5, -12.5), (-15.0, -9.0), (-33.0, 0.0),
              (-41.0, 0.0), (-44.5, 1.5), (-46.0, 4.5), (-46.0, 9.5), (-45.0, 12.0)]
    wing = sh.inflate("wing", [wing_l], grey, sh.pillow_profile(0.75, 1.3), bottom=1.0, base=0.0, spacing=0.6)
    for v in wing.data.vertices:
        d = max(0.0, abs(v.co.x - PX) - 10.0)
        v.co.z = v.co.z * (1.0 - 0.35 * d / 36.0) + 5.6 + 0.06 * d
    xs = [-39, -38, -37, -36, -35, -34, -33, -32, -29, -20]
    cut_lines(wing, xs=xs, ys=[7.0, 12.0, 1.0, 4.0])
    stripes = [(-39, -38), (-37, -36), (-35, -34), (-33, -32)]

    def wing_paint(c, n):
        if n.z < 0.25:
            return None
        if -29 <= c.x <= -20:
            return red
        if 7.0 <= c.y <= 12.0 and any(a <= c.x <= b for a, b in stripes):
            return red
        if 1.0 <= c.y <= 4.0 and (-38 <= c.x <= -37 or -34 <= c.x <= -32):
            return red
        return None
    paint(wing, wing_paint)
    k.smooth(wing, 50)
    # Panel lines: the grey H by the root and the edge of the red panel.
    lines = []
    for name, path in (("hline_a", [(-18.6, 12.0), (-18.6, -3.4)]), ("hline_b", [(-13.6, 12.0), (-13.6, -7.4)]),
                       ("hline_c", [(-18.6, 5.0), (-13.6, 5.0)])):
        pts = [(x, y, 0.0) for x, y in path]
        pts = [(x, y, sh.surface_z(wing, x, y, 7.0) - 0.12) for x, y, _ in w.catmull(pts, 0.8)]
        lines.append(tube(name, pts, 0.3, dark, segments=6, squash=0.7))
    mirror([wing] + lines, PX)

    # The tail: a tailplane with an engine nacelle on each side (grey on top, red at the sides, a
    # red intake at the front), a small fin at each tip and a fin on the fuselage's back.
    tail = [(-23.4, 32.0), (-3.0, 32.0), (-3.0, 23.4), (-23.4, 23.4)]
    plane = sh.inflate("tailplane", [tail], grey, sh.pillow_profile(0.55, 0.9), bottom=1.0, base=PZ - 0.4,
                       spacing=0.6)
    k.smooth(plane, 50)
    nac_x, nac_z = -12.4, PZ + 0.8
    nacelle = [
        lathe_y("nacelle", [(19.6, 0.01), (19.8, 2.4), (21.0, 3.4), (30.0, 3.6), (32.6, 3.2), (34.4, 2.2), (35.2, 1.0),
                            (35.4, 0.01)], grey_light, nac_x, nac_z + 0.6, 24),
        lathe_y("nacelle_lip", [(19.4, 3.0), (19.7, 3.9), (22.4, 4.0), (22.8, 3.4)], red, nac_x, nac_z + 0.6, 24),
        w.sphere("nacelle_intake", (nac_x, 19.5, nac_z + 0.6), (2.5, 0.5, 2.5), dark, 14, 6),
    ]
    for side in (-1, 1):
        nacelle.append(lathe_y(f"nacelle_side{side}", [(21.4, 0.01), (21.8, 1.6), (23.0, 2.1), (30.4, 2.1),
                                                       (32.2, 1.4), (32.8, 0.01)], red, nac_x + side * 4.7, nac_z,
                               16, squash=1.3))
    tip_fin = yz_plate("tip_fin", [(24.2, PZ), (31.6, PZ), (35.4, PZ + 6.0), (33.4, PZ + 6.4), (27.0, PZ + 2.8)],
                       -20.6, 2.8, grey, bevel=0.4, cant=-15.0)
    mirror([plane, tip_fin] + nacelle, 0.25)
    yz_plate("dorsal_fin", [(20.0, PZ + 5.0), (33.0, PZ + 3.0), (38.8, PZ + 10.0), (36.4, PZ + 10.6),
                            (26.0, PZ + 7.6)], PX, 2.4, grey_light, bevel=0.4)


REDWING_PIECES = [  # (sprite, x0, x1, y0, y1)
    (201, -24, 0, 14, 42), (203, 0, 24, 14, 42),
    (237, -48, -24, -14, 14), (239, -24, 0, -14, 14), (241, 0, 24, -14, 14), (243, 24, 48, -14, 14),
    (278, -12, 12, -42, -14),
]


# --- Main ------------------------------------------------------------------------------------------

OBJECTS = {  # name: (builder, whole size in pixels, sheet, pieces, extra views for --whole)
    "zeppelin": (zeppelin_whole, (96, 140), "enemy_I", ZEPPELIN_PIECES,
                 (("side", (-230, -10, 30), (0, -5, 14)), ("stern", (-70, 120, 75), (0, 30, 18)),
                  ("stern_top", (-30, -20, 95), (0, 34, 18)))),
    "redwing": (redwing_whole, (96, 84), "enemy_I", REDWING_PIECES,
                (("side", (-200, -40, 25), (0, 0, 7)), ("front", (40, -120, 70), (0, -5, 6)))),
}


def clear_extras():
    for obj in list(bpy.context.scene.objects):
        if obj.type != "MESH":
            bpy.data.objects.remove(obj)


def build(builder):
    k.reset()
    builder()
    w.bake()
    for obj in w.meshes():
        planar(obj, 0.6)


def look_from(name, location, target, lens=50):
    cam = bpy.data.objects.new(name, bpy.data.cameras.new(name))
    cam.data.lens = lens
    bpy.context.scene.collection.objects.link(cam)
    cam.location = Vector(location)
    cam.rotation_euler = (Vector(target) - Vector(location)).to_track_quat("-Z", "Y").to_euler()
    return cam


def render_whole(prefix, name, size, views=()):
    """The whole object: a top view framed like its sprites, a three-quarter view and the views
    given as (suffix, camera location, target)."""
    bpy.context.scene.view_settings.view_transform = "Standard"
    k.preview(prefix + name, size, scale=6)
    scene = bpy.context.scene
    scene.render.resolution_x, scene.render.resolution_y = 900, 900
    s = max(size) / 36
    for suffix, location, target in (("3q", (38 * s, -48 * s, 42 * s), (0, 0, 0)),) + tuple(views):
        scene.camera = look_from(suffix, location, target)
        scene.render.filepath = f"{prefix}{name}_{suffix}.png"
        bpy.ops.render.render(write_still=True)


def main():
    options = k.args()
    only = set(options["only"].split(",")) if "only" in options else None
    for oname, (builder, size, sheet, pieces, views) in OBJECTS.items():
        names = {f"{oname}_{p[0]}" for p in pieces}
        if only and oname not in only and not names & only:
            continue
        build(builder)
        print(f"=== {oname}: {sum(triangles(o) for o in w.meshes())} triangles whole")
        if "whole" in options:
            render_whole(options["whole"], oname, size, views)
            continue
        whole = [(obj.name, obj.data) for obj in w.meshes()]
        for obj in w.meshes():
            bpy.data.objects.remove(obj)
        for sprite, x0, x1, y0, y1 in pieces:
            name = f"{oname}_{sprite}"
            if only and oname not in only and name not in only:
                continue
            objs = []
            for oname_, data in whole:
                obj = bpy.data.objects.new(oname_, data.copy())
                bpy.context.scene.collection.objects.link(obj)
                objs.append(obj)
            kept = w.piece(objs, x0, x1, y0, y1)
            total = sum(triangles(o) for o in kept)
            print(f"--- {name}: {total} triangles")
            if "stats" in options:
                for obj in sorted(kept, key=triangles, reverse=True)[:6]:
                    print(f"    {obj.name}: {triangles(obj)}")
            if "check" in options:
                k.check_silhouette(os.path.join(options["check"], sheet + ".png"), [sprite], True)
            k.export(os.path.join(ENEMIES, name + ".glb"))
            if "preview" in options:
                bpy.context.scene.view_settings.view_transform = "Standard"
                k.preview(options["preview"] + name, (24, 28))
            clear_extras()
            for obj in list(w.meshes()):
                bpy.data.objects.remove(obj)


if __name__ == "__main__":
    main()
