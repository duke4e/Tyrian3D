"""The red ship with two long prongs (sheet 8 sprite 1, 2x2: a 19 x 25 craft in the 24 x 28 cell; enemy 104 of episodes
3 and 5: on the ground in IXMUCANE and SAWBLADES (events of type 6 and 10, at 1150-1190 and 2950-2990, 950-990 and
3350-3390), in the sky in SAVARA (type 15 at 200); its animation 1 3 5 7, a frame a tick; it fires three guns and drops
a coin when it dies), polished (2026-10-22; it replaces wave3_y.py's prong_ship(): lofted prongs with boxes for plates,
a tube for the crossbar, an egg for the pod).

No other enemy shows 1, 3, 5 or 7 (catalog.json); none of them is another sprite's pixels mirrored, turned or in other
ramps. The frames move two things a pixel a frame: the pod slides down under the crossbar (its top from row 3 to 6, its
foot from row 16 to 19; its glowing core shows in 1 and 3 and is gone under the bar in 5 and 7) while the grey plates on
the prongs slide up (rows 5-8, 4-7, 3-6, 2-5), and back at once: a pumping engine. Frame models prong_ship_3, _5, _7.

As the sprite and its 4x upscales draw it (columns and rows of the cell; symmetric about column 11, x -0.5; the reds of
ramp 4, the greys of ramp 0): two long red prongs (columns 2-7 and 15-20, rows 1-25), broad at the top with a grey plate
on their outer flanks (columns 3-4 and 18-19), narrowing below the crossbar and tapering to points at the bottom, lit
along their inner sides; a thin grey crossbar between them (row 9) with bright collars beside the middle (columns 10 and
12); between the prongs the red pod hanging at the bar (columns 8-14 of rows 3-16): a grey cap at its top (row 4), a
glowing core (row 6: 75 7c 75), its widest just above the bar (row 8), below the bar between two grey guides (columns 8
and 15 of rows 11-12) narrowing to its foot.

Built as a hovering craft for the game's camera: each prong a hull lofted along y through superellipse sections (the
sprite's widths, rounded caps at the top, a point at the bottom, a little thicker at the top), painted in bands of the
light its faces get (polish_tan_crab's paint_bands: reds 0x43 0x45 0x46 0x48, their undersides 0x41, a lit strip
0x4b along their inner sides), a silver plate (0x0a, its lit top 0x0d, dark rims 0x41) lying on its outer flank; the
crossbar a grey rod over the pod and the prongs' middles, with two collars; the guides grey blocks hanging from it
beside the pod; the pod a red hull lofted along y (its top's end grey: the cap; two grooves round its lower part
between its bands), the core a glowing lens on its top
(0x7c 0.5 round 0x75 0.3: emission under 1, the cfg's glow and the bloom add; dark (0x72, no emission) in 5 and 7, where
the sprite draws none). The frame models are the same craft with the pod moved down 1, 2, 3 pixels and the plates up as
much; all span the same bounds (the game centres the model in height on its layer).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up; built about u = 0 (column 11) and
moved to x -0.5 (AXIS_X); column c is x = c + 0.5 - 12, row r is y = 13.5 - r.

models.cfg: the model line stays (model prong_ship enemies/prong_ship.glb), add model prong_ship_3
enemies/prong_ship_3.glb, model prong_ship_5 ..., model prong_ship_7 ..., frame 8 3 prong_ship_3, frame 8 5
prong_ship_5, frame 8 7 prong_ship_7; sprite 8 1 prong_ship yaw=0 glow=8:0.15:122:-0.5:-6.5 (the halo on the core, where
it shows in 1 and 3, a little weaker: it can't go out in 5 and 7; it was glow=10:0.25:122 at the sprite's centre).

Replaces wave3_y.py's prong_ship() (its section "# --- 8 1: the red ship with two prongs": RED_SHIP, red_mats(),
shade_red() and the @y.model("prong_ship", ...) function, and the prong_ship paragraph of its docstring) and
wave3_y_art.py's RED_SHIP (nothing else reads them).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each frame's silhouette
against its sprite, also leaving the sprite's black outline out), --preview <prefix>, --only <name,...>.
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
from polish_claw_dome import ball, compare_core, outline_ring  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_tan_crab import band, light, paint_bands  # noqa: E402

AXIS_X = -0.5
# The left prong (the right one mirrored): key sections along y: (y, u of its middle, half-width, height over and
# depth under its middle's z), its middle's z, the superellipse power of its sections.
PRONG = [(12.95, -6.9, 0.35, 0.3, 0.25), (12.45, -6.9, 1.3, 1.05, 0.85), (11.5, -6.6, 2.05, 1.5, 1.15),
         (10.4, -6.35, 2.55, 1.75, 1.3), (8.4, -6.4, 2.85, 1.85, 1.35), (5.6, -6.3, 2.8, 1.8, 1.35),
         (4.4, -6.15, 2.6, 1.7, 1.3), (2.0, -6.0, 2.4, 1.55, 1.2), (-3.0, -6.0, 2.3, 1.45, 1.1),
         (-6.1, -6.3, 1.9, 1.25, 0.95), (-9.0, -6.75, 1.4, 0.95, 0.75), (-11.0, -7.0, 0.9, 0.65, 0.5),
         (-11.95, -7.0, 0.3, 0.25, 0.2)]
PRONG_Z, PRONG_POWER = 2.3, 2.8
STRIP = (0.3, 0.45)        # the prongs' lit strip along their inner sides: faces turned this far inwards and up
# The grey plate on its outer flank (frame 1): its rows' y (top and bottom edges), its u (outer and inner edges).
PLATE = (9.0, 5.0, -8.7, -6.9)
# The crossbar: its y, z, radius, its ends' u; the collars' u and radius.
BAR = (4.5, 4.25, 0.7, 7.3)
COLLARS = (1.25, 0.95)
# The guides beside the pod: u (inner and outer face), y (top and bottom), z (top and bottom).
GUIDES = (2.95, 3.8, 3.9, 1.15, 4.0, 1.5)
# The pod (frame 1): key sections (y, half-width, height over and depth under its middle), its middle's z; where its
# grey cap begins (y); the core: its middle (y), radii (across, along, up).
POD = [(11.05, 0.3, 0.3, 0.25), (10.6, 1.35, 1.1, 0.95), (9.6, 2.25, 1.6, 1.4), (7.5, 2.6, 1.8, 1.55),
       (5.6, 3.15, 1.9, 1.6), (3.6, 2.85, 1.8, 1.55), (1.6, 2.45, 1.65, 1.4), (-0.6, 1.9, 1.4, 1.15),
       (-2.2, 1.05, 0.9, 0.7), (-2.95, 0.3, 0.3, 0.2)]
POD_Z, POD_CAP = 1.75, 9.15
POD_BANDS = (1.55, -0.75)     # the grooves round its lower part (y, frame 1), between its bands
CORE = (7.5, (1.55, 1.05, 0.55))
# The frames: (model, sprite, the pod's shift down, the plates' shift up, the core lit).
FRAMES = [("prong_ship", 1, 0.0, 0.0, True), ("prong_ship_3", 3, 1.0, 1.0, True),
          ("prong_ship_5", 5, 2.0, 2.0, False), ("prong_ship_7", 7, 3.0, 3.0, False)]
RED = ((0.32, 0.52, 0.8), (0x43, 0x45, 0x46, 0x48))
RED_LIT = 0x4b
RED_UNDER = 0x41
GREYS = (0x07, 0x0a, 0x0d)


def materials():
    pal = k.level_palette()
    m = {i: k.material(f"prong_red_{i:x}", palette=i, metallic=0.3, roughness=0.32) for i in RED[1]}
    m[RED_UNDER] = k.material("prong_red_under", palette=RED_UNDER, metallic=0.25, roughness=0.45)
    m[RED_LIT] = k.material("prong_red_lit", palette=RED_LIT, metallic=0.3, roughness=0.3)
    for g in GREYS:
        m[g] = k.material(f"prong_grey_{g:x}", palette=g, metallic=0.5, roughness=0.28)
    m["core"] = k.material("prong_core", palette=0x7c, metallic=0.0, roughness=0.2, emission=pal[0x7c],
                           emission_strength=0.5)
    m["core_rim"] = k.material("prong_core_rim", palette=0x75, metallic=0.0, roughness=0.25, emission=pal[0x75],
                               emission_strength=0.3)
    m["core_off"] = k.material("prong_core_off", palette=0x72, metallic=0.1, roughness=0.3)
    return m


def red_paint(m, inner):
    def paint(c, n):
        if n.z < -0.4:
            return m[RED_UNDER]
        if inner and n.x * inner > STRIP[0] and n.z > STRIP[1]:
            return m[RED_LIT]
        return m[band(RED, light(n))]
    return paint


def hull(name, keys, z_mid, power, m, around=24, inner=0.0, grooves=(), step=None):
    """A hull lofted along y through superellipse sections (y, u, half-width, top, bottom) (keys from the top down:
    the loft runs up y; with step, sampled smoothly that far apart), painted in red light bands, a lit strip along its
    inner side (inner: +1 or -1, the side towards the craft's middle), grooves sunk round it at the given y."""
    rings = []
    sections = list(reversed(keys))
    if step:
        sections = k.profile(sections, step)
    for y, u, hw, top, bottom in sections:
        sink = max([0.0] + [0.22 * max(0.0, 1.0 - abs(y - g) / 0.3) for g in grooves])
        hw, top, bottom = hw - sink, top - sink, bottom - sink
        ring = []
        for j in range(around):
            a = 2 * math.pi * j / around
            c, s = math.cos(a), math.sin(a)
            du = math.copysign(abs(c) ** (2 / power), c) * hw
            dz = math.copysign(abs(s) ** (2 / power), s) * (top if s >= 0 else bottom)
            ring.append(Vector((u + du, y, z_mid + dz)))
        rings.append(ring)
    first, last = keys[-1], keys[0]
    obj = k.loft(name, rings, m[RED[1][1]], start_point=(first[1], first[0] - 0.12, z_mid),
                 end_point=(last[1], last[0] + 0.12, z_mid))
    k.recalc_normals(obj)
    k.smooth(obj, 60)
    fields = [(lambda co, n, b=b: light(n) - b, 0.0) for b in RED[0]] + [(lambda co, n: n.z + 0.4, 0.0)]
    if inner:
        fields += [(lambda co, n: min(n.x * inner - STRIP[0], n.z - STRIP[1]), 0.0)]
    paint_bands(obj, fields, red_paint(m, inner))
    return k.smooth(obj, 60)


def section_at(keys, y):
    """The prong's section (u, half-width, top) at y (linear between the keys)."""
    for a, b in zip(keys, keys[1:]):
        if b[0] <= y <= a[0]:
            t = (a[0] - y) / (a[0] - b[0])
            return tuple(a[i] + (b[i] - a[i]) * t for i in (1, 2, 3))
    k0 = keys[0] if y > keys[0][0] else keys[-1]
    return k0[1], k0[2], k0[3]


def prong_surface(y, u):
    """A point on the left prong's top at (u, y) and its outward normal (the superellipse's)."""
    uc, hw, top = section_at(PRONG, y)
    t = max(-1.0, min(1.0, (u - uc) / hw))
    s = (1.0 - abs(t) ** PRONG_POWER) ** (1.0 / PRONG_POWER)
    z = PRONG_Z + top * s
    # the normal of |du/hw|^p + |dz/top|^p = 1
    nu = math.copysign(abs(t) ** (PRONG_POWER - 1), t) / hw
    nz = (s ** (PRONG_POWER - 1)) / top
    n = Vector((nu, 0.0, nz)).normalized()
    return Vector((u, y, z)), n


def plate(m, lift):
    """The grey plate lying on the left prong's outer flank (raised 0.18, 0.25 thick), lifted up the prong by lift;
    its top edge lit, its rims dark."""
    y0, y1, u0, u1 = PLATE
    y0, y1 = y0 + lift, y1 + lift
    rows, cols = 8, 5
    top, low = [], []
    for i in range(rows + 1):
        y = y0 + (y1 - y0) * i / rows
        trow, lrow = [], []
        for j in range(cols + 1):
            u = u0 + (u1 - u0) * j / cols
            p, n = prong_surface(y, u)
            edge = min(i, rows - i, j, cols - j)
            trow.append(p + n * (0.18 + (0.12 if edge > 0 else 0.0)))
            lrow.append(p - n * 0.3)
        top.append(trow)
        low.append(lrow)
    verts, faces = [], []
    for grid in (top, low):
        for row in grid:
            verts += [tuple(p) for p in row]
    w = cols + 1
    off = (rows + 1) * w
    for i in range(rows):
        for j in range(cols):
            a, b, c, d = i * w + j, i * w + j + 1, (i + 1) * w + j + 1, (i + 1) * w + j
            faces.append((a, b, c, d))
            faces.append((off + d, off + c, off + b, off + a))
    ring = [(0, j) for j in range(cols + 1)] + [(i, cols) for i in range(1, rows + 1)] + \
           [(rows, j) for j in range(cols - 1, -1, -1)] + [(i, 0) for i in range(rows - 1, 0, -1)]
    for (i0, j0), (i1, j1) in zip(ring, ring[1:] + ring[:1]):
        a, b = i0 * w + j0, i1 * w + j1
        faces.append((b, a, off + a, off + b))
    obj = k.mesh_object("plate", verts, faces, m[GREYS[1]])
    k.recalc_normals(obj)
    ylit = y0 - (y0 - y1) * 0.3
    mk.paint(obj, lambda c, n: m[RED_UNDER] if (c.y > y0 - 0.45 or c.y < y1 + 0.45) else
             m[GREYS[2]] if c.y > ylit else None)
    return k.smooth(obj, 40)


def bar(m):
    """The crossbar over the pod, its ends in the prongs' inner flanks; two collars beside the middle."""
    y, z, r, end = BAR
    parts = []
    obj = k.mesh_object("bar", *tube_mesh([(-end, y, z), (end, y, z)], r, 14))
    obj.data.materials.append(m[GREYS[1]])
    k.recalc_normals(obj)
    mk.paint(obj, lambda c, n: m[GREYS[2]] if n.z > 0.6 else m[GREYS[0]] if n.z < -0.3 else None)
    parts.append(k.smooth(obj, 50))
    cu, cr = COLLARS
    for side in (-1.0, 1.0):
        col = k.mesh_object(f"collar{side}", *tube_mesh([(side * cu - 0.35, y, z), (side * cu + 0.35, y, z)], cr, 14))
        col.data.materials.append(m[GREYS[2]])
        k.recalc_normals(col)
        mk.paint(col, lambda c, n: m[GREYS[1]] if n.z < 0.2 else None)
        parts.append(k.smooth(col, 50))
    return parts


def tube_mesh(points, radius, around):
    """A closed cylinder between two points along x (vertices, faces)."""
    (x0, y, z), (x1, _, _) = points
    verts = []
    for x in (x0, x1):
        for j in range(around):
            a = 2 * math.pi * j / around
            verts.append((x, y + radius * math.cos(a), z + radius * math.sin(a)))
    faces = [(j, (j + 1) % around, around + (j + 1) % around, around + j) for j in range(around)]
    faces.append(tuple(range(around - 1, -1, -1)))
    faces.append(tuple(range(around, 2 * around)))
    return verts, faces


def guides(m):
    parts = []
    ui, uo, yt, yb, zt, zb = GUIDES
    for side in (-1.0, 1.0):
        a, b = sorted((side * ui, side * uo))
        g = mk.box(f"guide{side}", a, b, yb, yt, zb, zt, m[GREYS[1]])
        mk.cleanup(g)
        mk.bevel(g, 0.22, 2, 35)
        mk.shade(g, 35)
        mk.paint(g, lambda c, n: m[GREYS[2]] if n.z > 0.6 else m[GREYS[0]] if n.z < 0.3 and n.y < 0.5 else None)
        parts.append(g)
    return parts


def pod(m, shift, lit):
    """The pod moved down by shift: a red hull, its top's end grey (the cap), the core a lens on its top."""
    keys = [(y - shift, 0.0, hw, top, bottom) for y, hw, top, bottom in POD]
    obj = hull("pod", keys, POD_Z, 2.0, m, around=20, grooves=[g - shift for g in POD_BANDS], step=0.4)
    cap = POD_CAP - shift
    mk.paint(obj, lambda c, n: (m[GREYS[1]] if n.z > 0.5 else m[GREYS[0]]) if c.y > cap else None)
    cy, (rx, ry, rz) = CORE
    cy -= shift
    top = POD_Z + section_top(POD, cy + shift)
    lens = ball("core", Vector((0.0, cy, top - 0.15)), Vector((rx, ry, rz)), m["core" if lit else "core_off"],
                around=20, rings=8, z_min=top - 0.25)
    if lit:
        mk.paint(lens, lambda c, n: m["core_rim"] if math.hypot(c.x / rx, (c.y - cy) / ry) > 0.62 else None)
    return [obj, lens]


def section_top(keys, y):
    for a, b in zip(keys, keys[1:]):
        if b[0] <= y <= a[0]:
            t = (a[0] - y) / (a[0] - b[0])
            return a[2] + (b[2] - a[2]) * t
    return keys[0][2]


def build_model(m, shift, lift, lit):
    parts = []
    left = hull("prong_l", PRONG, PRONG_Z, PRONG_POWER, m, inner=1.0)
    right = hull("prong_r", [(y, -u, hw, top, bottom) for y, u, hw, top, bottom in PRONG], PRONG_Z, PRONG_POWER, m,
                 inner=-1.0)
    parts += [left, right]
    plate_l = plate(m, lift)
    plate_r = plate_l.copy()
    plate_r.data = plate_l.data.copy()
    plate_r.name = "plate_r"
    bpy.context.scene.collection.objects.link(plate_r)
    plate_r.data.transform(Matrix.Scale(-1.0, 4, (1.0, 0.0, 0.0)))
    plate_r.data.flip_normals()
    parts += [plate_l, plate_r]
    parts += bar(m) + guides(m) + pod(m, shift, lit)
    for obj in parts:
        mk.apply(obj)
    mk.transform(parts, Matrix.Translation((AXIS_X, 0.0, 0.0)))
    return triangulate(parts)


def build():
    options = k.args()
    out = mk.outdir(options)
    only = set(options["only"].split(",")) if "only" in options else None
    for name, sprite, shift, lift, lit in FRAMES:
        if only is not None and name not in only:
            continue
        k.reset()
        bpy.context.scene.view_settings.view_transform = "Standard"
        m = materials()
        parts = build_model(m, shift, lift, lit)
        bpy.context.view_layer.update()
        if "check" in options:
            sheet = os.path.join(options["check"], "enemy_8.png")
            covered, mask = mk.coverage(parts, 24, 28), k.sprite_mask(sheet, sprite)
            mk.compare("%s (8 %d)" % (name, sprite), covered, mask)
            compare_core("%s (8 %d)" % (name, sprite), covered, mask, outline_ring(sheet, sprite))
        mk.report(name, parts, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, parts)


if __name__ == "__main__":
    build()
