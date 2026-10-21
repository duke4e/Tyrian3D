"""The asteroid levels' eye turret damaged (sheet S sprite 275, 2x2: 24 x 28 pixels): the dgr of S 269, enemy 568 of
episodes 1-3 (dlevel 15: the turret turns into it once it is shot down to 15 armour, and goes on firing so until it is
destroyed; ASTEROID?, MINEMAZE, BONUS, ** ALE **, AST. CITY; not in episode 6). Polished (2026-10-21, round 26); it
replaces eye_turret_damaged.glb, which wave3_ap_ast.py once built from misc.py's old eye turret (both gone since round
5, so the GLB had no generator and was a ball, not the polished turret's oval housing). models.cfg: model
eye_turret_damaged enemies/eye_turret_damaged.glb, stand-alone without origin as the intact eye_turret is (both are
centred in height on the ground enemies' layer, so the same bounds keep it in place); sprite s 275 eye_turret_damaged
yaw=0. No other enemy shows S 275; no sprite of any sheet is its pixels mirrored, turned or in other ramps.

Built from polish_eye_turret.py's turret (S 269), as polish_lens_pad.py builds its damaged pad from the new pad: the
same housing, dome, lens, gasket, bracket ribs and lugs (its own functions, loaded without its top-level build(), which
would write the intact turret into assets), so the turret keeps its size and place when it is hit (x -10.7..11.7,
y -12.55..13.55, z 0..10.04, as eye_turret.glb). What S 275 draws differently from S 269, read pixel by pixel into
DAMAGE below:
- the housing sooted black down both flanks and over its left shoulder (columns 2-8 of rows 2-24, 15-22 of rows
  11-24: greys 0x04-0x0e burnt to 0x01-0x03), its rim's top, the bracket's ribs and the lugs left grey (the few
  lighter pixels at the bracket's lower left, columns 6-8 of rows 22-24, are left out: specks of the redrawing);
- the red glass dome dimmed round its highlight (0x77-0x7c down to 0x72-0x76) and cracked: two dark cracks (0x70-0x72)
  from its crown down to the lens, one at its left (columns 6-9 of rows 4-9), one in its middle (columns 10-13), and
  embers glowing in cracks beside them (0x76-0x79: along the middle one's right, columns 13-15 of rows 4-8, and down
  the dome's left side, column 6 of rows 8-10); the highlight itself (0x7f, 0x7b-0x7c) is left;
- the lens burnt black (0x01-0x03; a little grey left along its upper left and its lower right, 0x04-0x07).

How: the housing is painted by the soot (a quarter for each shade of grey the damaged sprite lost, blurred) in bands
cut along smooth contours (polish_orb_red.band_split; its edges the bands' borders cross are first cut in two, so the
borders follow the soot closely): 0x03, 0x02 and 0x01, matte so that they read black under the game's sky, the intact
metal (0x05) where the sprite keeps its greys; the glass is a shade darker red (0x73) and glows less (0.1, the intact
dome 0.2), darker again (0x71, 0.05) round the highlight where the sprite's red dimmed most; the cracks are dark strips
(0x70, matte) laid on the glass (each edge point dropped onto the dome from above and lifted a little off it,
narrowing to their ends), the ember cracks with a glowing core (0x76 at 0.3, 0x79 at 0.45 where HOT_AT puts the
sprite's hottest pixels: the game's bloom adds); the lens is painted in the damaged sprite's burnt shades (blurred:
0x01, 0x03 and the housing's 0x05), its slit black. Every mesh is triangulated before the export (the same output with
and without --check).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the ground (z = 0); origin at
the sprite's centre (pixel 12, 14): column c is x = c + 0.5 - 12, row r is y = 13.5 - r. The cracks are given in the
sprite's columns and rows (continuous: pixel c, r spans c..c+1, r..r+1).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouette against S 275
in enemy_S.png), --preview <prefix> (top and 3/4 views).
"""
import ast
import math
import os
import sys
import types

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k, smoothstep  # noqa: E402
from polish_orb_red import band_split  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_deli_boss import drop_unused  # noqa: E402

NAME = "eye_turret_damaged"

# S 275's pixels where they differ from S 269's (row, then "column:intact>damaged", palette indices).
DAMAGE = """
2 5:03>02 6:08>04
3 4:05>01 5:05>08 6:0b>01 7:09>03 15:72>73
4 4:09>05 5:05>03 6:06>01 7:73>71 8:74>73 12:76>75 13:73>71 14:73>72 15:73>76
5 3:09>07 4:0e>04 5:04>01 6:72>70 7:73>71 8:77>75 11:7b>7a 12:77>73 13:74>70 15:72>76
6 2:05>03 3:0c>06 4:06>01 6:75>72 7:74>70 8:78>74 10:7c>7a 11:7a>76 12:78>70 13:74>71 14:73>78 15:72>74
7 3:0c>0a 4:04>01 6:75>73 7:74>71 8:77>72 9:79>76 10:79>76 11:79>72 12:79>70 13:75>79 14:73>74
8 6:74>76 7:74>72 8:78>72 9:7b>73 10:7b>74 11:7a>71 12:79>73 13:78>79
9 6:73>78 7:75>73 8:7a>72 9:77>72 10:07>05 11:06>04 12:04>02 13:05>03 14:05>01
10 6:72>75 7:77>76 9:06>04 10:07>02 11:08>02 12:05>01 13:08>03 14:07>01 15:05>01
11 9:07>04 10:09>06 11:0c>07 12:05>01 13:0c>01 14:08>01 15:06>01 16:05>03
12 3:04>02 8:05>03 9:07>04 10:07>02 11:09>01 12:05>01 13:0a>01 14:07>01 15:06>03 16:06>04 21:04>02
13 2:0a>09 3:04>01 8:04>03 9:06>01 10:06>01 11:07>01 12:04>01 13:06>01 14:05>03 21:04>01 22:05>03
14 1:05>04 2:09>06 3:05>01 4:04>01 9:04>01 10:04>01 11:05>01 20:03>01 21:04>01 22:06>05
15 2:07>03 3:07>01 4:04>01 10:03>02 12:01>04 13:03>05 14:03>02 20:04>01 21:05>01 22:06>04
16 2:05>03 3:07>01 4:06>01 5:04>02 19:04>01 20:05>01 21:06>01 22:05>03
17 3:07>03 4:07>01 5:05>01 6:04>01 18:04>01 19:05>01 20:06>02 21:06>01 22:04>02
18 3:05>03 4:07>01 5:06>01 6:05>01 7:04>01 17:04>01 18:04>01 19:06>04 20:06>02 21:03>01 22:03>01
19 4:05>01 5:07>01 6:06>01 7:06>01 8:03>01 15:03>01 16:04>01 17:05>01 18:06>04 19:06>02 20:04>01 21:03>01
20 4:04>02 5:04>01 6:07>01 7:07>01 8:05>01 9:07>05 16:07>05 17:07>05 18:06>02 19:04>01 20:03>01 21:03>01
21 5:03>01 6:04>01 7:04>01 8:04>01 17:04>02 18:03>01 19:03>01 20:03>01
22 6:03>01 7:03>01 8:02>04 16:05>03 17:03>01 18:03>01 19:03>01
23 6:03>05 7:03>05 8:01>08 9:03>01 14:04>02 16:04>01 17:03>01 18:03>01
24 6:03>04 7:03>05 8:01>02 9:03>01 10:02>01 13:02>01 14:04>01 16:03>01 17:03>02
25 9:03>02 10:02>03 11:02>03 12:03>04 13:02>03 14:03>04 15:01>04 16:03>04
26 9:02>01 10:02>01 11:02>01 12:02>01 14:02>01
"""
# The lens as S 275 draws it (columns 8-16 of rows 9-15; ".." the dome round it): its burnt shades.
LENS_PIXELS = [
    ".. .. 05 04 02 03 01 .. ..",
    ".. 04 02 02 01 03 01 01 ..",
    "06 04 06 07 01 01 01 01 03",
    "03 04 02 01 01 01 01 03 04",
    "03 01 01 01 01 01 03 05 04",
    ".. 01 01 01 02 04 05 04 ..",
    ".. .. 02 03 04 05 02 .. ..",
]
LENS_ROW, LENS_COL = 9, 8

# The cracks in the glass (lines of (column, row)): dark ones from the crown down to the lens; ember ones glowing.
# Each: (points, half-width, glowing core or not).
CRACKS = [
    ([(7.6, 3.8), (7.0, 4.9), (7.2, 6.2), (7.9, 7.4), (8.5, 8.5), (9.3, 9.5)], 0.34, False),
    ([(13.7, 3.7), (13.5, 5.0), (12.8, 6.3), (12.3, 7.5), (11.4, 8.5), (10.3, 9.4)], 0.34, False),
    ([(7.1, 5.4), (6.2, 5.9), (5.7, 6.8)], 0.22, False),
    ([(15.7, 3.6), (15.5, 5.0), (14.8, 6.3), (13.9, 7.4), (13.6, 8.6)], 0.36, True),
    ([(6.9, 7.6), (6.5, 8.6), (6.4, 9.6), (6.6, 10.7)], 0.3, True),
]
STRIP_STEP = 0.25                  # how often the strips are sampled along their lines
STRIP_LIFT, CORE_LIFT = 0.05, 0.08  # how far off the glass they lie
CORE_SHARE = 0.5                    # the glowing core's share of an ember crack's width
HOT_AT = [((13.5, 7.5), 1.3), ((14.5, 6.5), 1.0), ((6.5, 9.5), 1.0)]   # where the embers glow hottest ((col, row), r)

# Paint bands: the soot (how many shades of grey the housing lost, quartered, blurred: lowest value, material key),
# the glass dimmed (how many shades of red it lost, blurred), the lens' burnt shade (blurred).
SOOT_BANDS = [(-9.0, "metal"), (0.16, "soot3"), (0.32, "soot2"), (0.5, "char")]
DIM = 0.18
LENS_BANDS = [(-9.0, "dark"), (2.6, "soot3"), (4.4, "metal")]


def intact():
    """polish_eye_turret.py as a module, without its top-level build() call (run, it builds the intact turret and
    writes it into assets): its builders and measures."""
    path = os.path.join(HERE, "polish_eye_turret.py")
    tree = ast.parse(open(path).read(), path)
    tree.body = [node for node in tree.body
                 if not (isinstance(node, ast.Expr) and isinstance(node.value, ast.Call) and
                         isinstance(node.value.func, ast.Name) and node.value.func.id == "build")]
    mod = types.ModuleType("polish_eye_turret")
    mod.__file__ = path
    exec(compile(tree, path, "exec"), mod.__dict__)
    return mod


def materials():
    pal = k.level_palette()

    def grey(name, index, metallic, roughness):
        return k.material(name, palette=index, metallic=metallic, roughness=roughness)

    def glow(name, index, light, strength, roughness=0.3):
        return k.material(name, palette=index, metallic=0.0, roughness=roughness, emission=pal[light],
                          emission_strength=strength)
    return {
        # polish_eye_turret.py's housing, trim and dark parts
        "metal": grey("eyeturret_metal", 5, 0.5, 0.4),
        "trim": grey("eyeturret_trim", 7, 0.4, 0.45),
        "dark": grey("eyeturret_dark", 1, 0.3, 0.7),
        # the soot (matte, so that it reads black under the sky)
        "soot3": grey("eyeturret_soot", 3, 0.25, 0.62),
        "soot2": grey("eyeturret_soot_dark", 2, 0.2, 0.7),
        "char": grey("eyeturret_char", 1, 0.15, 0.8),
        # the glass, dimmed, its cracks and embers
        "glass": glow("eyeturret_glass", 0x73, 0x74, 0.1, 0.26),
        "glass_dim": glow("eyeturret_glass_dim", 0x71, 0x72, 0.05, 0.3),
        "crack": grey("eyeturret_crack", 0x70, 0.0, 0.85),
        "ember": glow("eyeturret_ember", 0x76, 0x77, 0.3, 0.4),
        "ember_hot": glow("eyeturret_ember_hot", 0x79, 0x7a, 0.45, 0.4),
    }


# --- The damage's fields ---------------------------------------------------------------------------------------------

def blur(a, sigma=0.6):
    import numpy as np
    rad = 2
    kernel = np.exp(-0.5 * (np.arange(-rad, rad + 1) / sigma) ** 2)
    kernel /= kernel.sum()
    for axis in (0, 1):
        p = np.pad(a, [(rad, rad) if ax == axis else (0, 0) for ax in (0, 1)], mode="edge")
        a = sum(w * np.take(p, range(i, i + a.shape[axis]), axis=axis) for i, w in enumerate(kernel))
    return a


def sampler(a):
    """A 28 x 24 grid of the sprite's pixels as a function of (x, y) (bilinear between pixel centres)."""
    def at(x, y):
        u, v = x + 12.0 - 0.5, 13.5 - y
        c0, r0 = int(math.floor(u)), int(math.floor(v))
        fu, fv = u - c0, v - r0

        def px(r, c):
            return a[min(max(r, 0), 27), min(max(c, 0), 23)]
        return float((1 - fu) * (1 - fv) * px(r0, c0) + fu * (1 - fv) * px(r0, c0 + 1) + (1 - fu) * fv * px(r0 + 1, c0) +
                     fu * fv * px(r0 + 1, c0 + 1))
    return at


def fields():
    """Samplers of the damage: soot (the greys' lost shades, a quarter each), dim (the glass' lost shades of red, an
    eighth each) and the lens' burnt shade."""
    import numpy as np
    soot, dim = np.zeros((28, 24)), np.zeros((28, 24))
    for line in DAMAGE.strip().splitlines():
        row, *cells = line.split()
        r = int(row)
        for cell in cells:
            c, change = cell.split(":")
            a, b = (int(v, 16) for v in change.split(">"))
            c = int(c)
            if a >> 4 == 0 and b >> 4 == 0:
                soot[r, c] = max(0.0, min(1.0, ((a & 15) - (b & 15)) / 4.0))
            elif a >> 4 == 7 and b >> 4 == 7:
                dim[r, c] = max(0.0, min(1.0, ((a & 15) - (b & 15)) / 8.0))
    lens = np.full((28, 24), 1.0)
    for i, line in enumerate(LENS_PIXELS):
        for j, tok in enumerate(line.split()):
            if tok != "..":
                lens[LENS_ROW + i, LENS_COL + j] = int(tok, 16) & 15
    # outside the drawn lens, its nearest drawn shade (so its rim does not blur towards the dome's)
    known = [(r, c) for r in range(28) for c in range(24) if LENS_ROW <= r < LENS_ROW + len(LENS_PIXELS) and
             LENS_COL <= c < LENS_COL + 9 and LENS_PIXELS[r - LENS_ROW].split()[c - LENS_COL] != ".."]
    for r in range(28):
        for c in range(24):
            if (r, c) not in known:
                rr, cc = min(known, key=lambda p: (p[0] - r) ** 2 + (p[1] - c) ** 2)
                lens[r, c] = lens[rr, cc]
    return sampler(blur(soot)), sampler(blur(dim, 0.8)), sampler(blur(lens, 0.55))


# --- The turret ------------------------------------------------------------------------------------------------------

def turret(et, m):
    """polish_eye_turret.py's turret, as its build() makes it (housing, dome, lens with its slit, gasket, the bracket's
    ribs and slots, the lugs), in the damaged look's materials: {part: object or [objects]}."""
    parts = {"housing": et.housing(m["metal"]), "dome": et.dome(m["glass"]), "lens": et.lens(m["dark"], m["dark"]),
             "gasket": et.gasket(m["dark"]), "bars": [], "lugs": []}
    on_body = et.surface([parts["housing"]])
    for x in et.RIBS:
        side = 1 if x > et.RIB_MIDDLE else -1
        for name, dx, hw, top, mat in (("slot", 0.95 * side, 0.42, 0.05, m["dark"]), ("rib", 0.0, 0.55, 0.5, m["trim"])):
            hits = [on_body(x + dx, et.RIB_TOP - (et.RIB_TOP - et.RIB_BOTTOM) * i / 8) for i in range(9)]
            hits = [h for h in hits if h is not None]
            parts["bars"].append(et.bar(f"{name}{x}", [h[0] for h in hits], [h[1] for h in hits], hw, top, 0.3, mat,
                                        power=5.0))
    for i, (x, y) in enumerate(et.LUGS):
        z = on_body(x, y)[0].z
        parts["lugs"].append(k.smooth(k.ellipsoid(f"lug{i}", (x, y, z + 0.1), (0.95, 0.75, 0.6), m["trim"], 12, 6),
                                      50))
    return parts


def refine_near(obj, value, thresholds, rounds=1):
    """Cuts the edges a band's border crosses in two, rounds times: the paint's contours then follow its field closely
    without the whole mesh cut finer."""
    for _ in range(rounds):
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        vals = {v: value(v.co.x, v.co.y) for v in bm.verts}
        edges = [e for e in bm.edges
                 if any((vals[e.verts[0]] - t) * (vals[e.verts[1]] - t) < 0 for t in thresholds)]
        if edges:
            bmesh.ops.subdivide_edges(bm, edges=edges, cuts=1, use_grid_fill=True)
        bm.to_mesh(obj.data)
        bm.free()
    obj.data.update()
    return obj


def paint_soot(parts, m, soot):
    housing = refine_near(parts["housing"], soot, [lowest for lowest, _ in SOOT_BANDS[1:]])
    band_split(housing, [soot(v.co.x, v.co.y) for v in housing.data.vertices],
               [(lowest, m[key]) for lowest, key in SOOT_BANDS])
    k.smooth(housing, 40)


def paint_glass(dome, m, dim):
    band_split(dome, [dim(v.co.x, v.co.y) for v in dome.data.vertices], [(-9.0, m["glass"]), (DIM, m["glass_dim"])])
    k.recalc_normals(dome)
    k.smooth(dome, 50)


def paint_lens(lens, m, shade):
    lens.data.update()
    band_split(lens, [shade(v.co.x, v.co.y) for v in lens.data.vertices], [(lowest, m[key]) for lowest, key in LENS_BANDS])
    k.recalc_normals(lens)
    k.smooth(lens, 60)


def resample(points, step):
    """A line's points about step apart along it, with the distance along it of each."""
    out, along = [points[0]], [0.0]
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        length = math.hypot(x1 - x0, y1 - y0)
        n = max(1, round(length / step))
        for i in range(1, n + 1):
            out.append((x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n))
            along.append(along[-1] + length / n)
    return out, along


def heat(col, row):
    return max(0.0, max(1.0 - math.hypot(col - c, row - r) / radius for (c, r), radius in HOT_AT))


def cracks(dome, m):
    """The cracks: dark strips laid on the glass (each edge point dropped onto the dome from above, lifted a little off
    it), narrowing to their ends; the ember cracks with a glowing core along them, hotter where HOT_AT says."""
    mesh = dome.data
    bvh = BVHTree.FromPolygons([v.co.copy() for v in mesh.vertices], [tuple(p.vertices) for p in mesh.polygons])
    bm = bmesh.new()
    keys = []

    def drop(x, y, lift):
        loc, normal, _, _ = bvh.ray_cast(Vector((x, y, 60.0)), Vector((0.0, 0.0, -1.0)))
        if loc is None:
            return None
        if normal.z < 0:
            normal = -normal
        return loc + normal * lift, normal

    for line, half, glowing in CRACKS:
        points, along = resample(line, STRIP_STEP)
        total = along[-1]
        for width, lift, core in ((half, STRIP_LIFT, False), (half * CORE_SHARE, CORE_LIFT, True)):
            if core and not glowing:
                continue
            samples = []
            for i, (c, r) in enumerate(points):
                a, b = points[max(i - 1, 0)], points[min(i + 1, len(points) - 1)]
                tx, ty = b[0] - a[0], -(b[1] - a[1])           # (rows run down the screen)
                length = math.hypot(tx, ty) or 1.0
                sx, sy = -ty / length, tx / length
                ends = smoothstep(0.0, 0.8, along[i]) * smoothstep(0.0, 0.8, total - along[i])
                w = width * (0.35 + 0.65 * ends)
                x, y = c - 12.0, 14.0 - r
                hits = [drop(x + sx * w * s, y + sy * w * s, lift) for s in (1.0, -1.0)]
                samples.append(None if None in hits else (hits[0][0], hits[1][0], hits[0][1] + hits[1][1], heat(c, r)))
            for s0, s1 in zip(samples, samples[1:]):
                if s0 is None or s1 is None:
                    continue
                (l0, r0, n0, h0), (l1, r1, n1, h1) = s0, s1
                face = bm.faces.new([bm.verts.new(v) for v in (l0, r0, r1, l1)])
                face.normal_update()
                if face.normal.dot(n0 + n1) < 0:
                    face.normal_flip()
                keys.append(("ember_hot" if (h0 + h1) / 2 > 0.45 else "ember") if core else "crack")
    names = sorted(set(keys))
    out = bpy.data.meshes.new("cracks")
    for key in names:
        out.materials.append(m[key])
    bm.faces.ensure_lookup_table()
    for f, key in zip(bm.faces, keys):
        f.material_index = names.index(key)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-4)
    bm.to_mesh(out)
    bm.free()
    obj = bpy.data.objects.new("cracks", out)
    bpy.context.scene.collection.objects.link(obj)
    return k.smooth(obj, 60)


def build_damaged():
    k.reset()
    et = intact()
    m = materials()
    parts = turret(et, m)
    soot, dim, lens_shade = fields()
    paint_soot(parts, m, soot)
    paint_glass(parts["dome"], m, dim)
    paint_lens(parts["lens"], m, lens_shade)
    objects = [parts["housing"], parts["dome"], parts["lens"], parts["gasket"]] + parts["bars"] + parts["lugs"]
    objects.append(cracks(parts["dome"], m))
    drop_unused(objects)
    return triangulate(objects)


def mask(sheet, sprite):
    """The sprite's own pixels (all of them: the turret has no ground painted round it)."""
    return k.sprite_mask(sheet, sprite)


def build():
    options = k.args()
    out = mk.outdir(options)
    objects = build_damaged()
    bpy.context.view_layer.update()
    if "stats" in options:
        for obj in objects:
            print("    %-14s %6d triangles" % (obj.name, mk.triangles([obj])))
    if "check" in options:
        sheets = options["check"]
        sheet = os.path.join(sheets, "enemy_S.png") if os.path.isdir(sheets) else sheets
        mk.compare("%s (S 275)" % NAME, mk.coverage(objects, 24, 28), mask(sheet, 275))
    bpy.context.scene.view_settings.view_transform = "Standard"
    mk.report(NAME, objects, os.path.join(out, NAME + ".glb"))
    if "preview" in options:
        mk.preview(options["preview"] + NAME, objects)


if __name__ == "__main__":
    build()
