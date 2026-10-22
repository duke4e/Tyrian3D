"""FRUIT's strawberry wing (sheet ', written x27 in models.cfg: sprites 86 88 90 above 125 127, 2x2 each; enemies 1233
to 1237 of episode 5, in the sky or on the top layer), polished (2026-10-22, round 35; it replaces wave3_ae_lemon.py's
strawberry wing, a relief painted pixel by pixel with ball seeds).

The levels always put its five sprites together as one 72 x 56 picture (FRUIT's events 15 at t 1100, 1440 and 2040 and
7 at t 3700, all five with link 15: 1233 (' 86) at (x, y - 28), 1234 (' 88) at (x + 24, y - 28), 1235 (' 90) at
(x + 48, y - 28), 1236 (' 125) at (x + 12, y), 1237 (' 127) at (x + 36, y): the lower two half a sprite to the right).
Each piece is an enemy of its own (armour 40, one frame, no damaged look (dgr 0), not animated; 1236 and 1237 carry the
ember 1262 as their launch type with launch frequency 0); they share their link, so tyrian2.c destroys all five when
one is shot down: the wing always dies whole. No other enemy (launched ones included) shows these sprites, no episode 6
level takes these waves, and none of the five is another sprite's pixels mirrored, turned or in other ramps; the
picture is its own mirror image about its middle (column 36), but for the shading of a few pixels: built symmetric.

As the sprites and their 4x upscales draw it (columns and rows of the 72 x 56 picture): a chevron of red strawberry
flesh (ramp 7's reds 0x70-0x77) pointing down the screen (its lower edges the lines column = row - 14 and its mirror,
meeting at the point (36, 50)), a rounded lobe at each wing tip (columns 0-14 of rows 5-17), a small red nub at the
top of its middle (columns 34-37 of rows 8-11); over it an M of bent grey steel pipe (6 pixels thick: from its left
end at (10.6, 22.2) up to its peak at (24.5, 8.3), down into its valley at (36, 18.3), up and down again to (61.4,
22.2)); two straight pipes along the lower arms (from (17.4, 26.7) down to (28.6, 38.6) and its mirror image), each
with four gold bands every three pixels down the diagonal; a grey missile pod down the middle (columns 32-39 of rows
18-41), its nose down the screen, a gold collar at its top, a gold hook on each side at row 31, a white glint at
(36, 33); and golden pips in the flesh along the lower edges (the sprites' gold crescents at (6.5, 13.7), (9.5,
16.7), (15.5, 22.7), (18.5, 25.7) and their mirror images).

Built as such: the flesh a solid over its outline (polish_ring_machine.relief: a pillowed top 3.4 over a flat belly,
its edges rounded, gentle lumps (mathutils.noise, the same every run), a dimple under each pip), painted in four
reds by the light it gets and glowing a little in them (reds read dark from the game's camera); the pips small golden
ovals lying in their dimples; the pipes round bars with rounded bends (the M) and rounded ends, sunk a little into the
flesh, painted in four greys by their light; the gold bands rings round them; the pod a lathe along its axis, its
glint a small white patch; the nub a glossy red ball. Modelled in the picture's plane (x, y as the sprite draws them,
z up) and then sheared along the game camera's line of sight (y - z tan 20, the normals with it:
polish_lemon_beetle.shear_to_camera), so the camera sees every point where the sprite draws it. Cut into the five
pieces in the picture's plane along the sprites' edges (polish_coral_manta.cut: the caps the part's inside colour),
before the shear; each piece moved so that its sprite's middle is its origin, its parts joined, every mesh
triangulated (polish_k_pod.triangulate: the same output with and without --check). Deterministic: no random numbers,
no booleans.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up. The whole's origin is the picture's
middle (its pixel edge 36, 28): column c is x = c + 0.5 - 36, row r is y = 27.5 - r. The pieces' origins (their
sprites' middles): 86 (-24, 14), 88 (0, 14), 90 (24, 14), 125 (-12, -14), 127 (12, -14). In the picture's plane the
belly lies at z -1, the flesh's top at 3.4, the pipes' tops at 8, the pod's at 9.2; drawn at their origins on the sky
or the top layer (models.cfg origin).

models.cfg (unchanged): model strawberry_wing_tl/_tm/_tr/_bl/_br enemies/strawberry_wing_*.glb origin, sprite x27 86
strawberry_wing_tl yaw=0 (88 _tm, 90 _tr, 125 _bl, 127 _br).

Replaces wave3_ae_lemon.py (all that is left of it: BERRY, POD_BOX, is_steel(), in_pod(), strawberry_wing_whole(), the
kit.PROTECT += ["sberry_flesh"] line and the kit.pieced("strawberry_wing", ...) registration): with it the whole file
goes; and wave3_ae_art.py's BERRY (read only by wave3_ae_lemon.py).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the whole's silhouette as the
camera sees it, and each piece's, against enemy_x27.png), --preview <prefix> (the whole's top and 3/4 views; --pieces 1
also each piece's), --only <name,...>, --whole <file.glb> (the sheared whole as well, for looking at).
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector, noise

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_deli_boss import join, drop_unused  # noqa: E402
from polish_coral_manta import cut  # noqa: E402
from polish_ring_machine import ccw, chaikin, relief, round_edge  # noqa: E402
from polish_pineapple import section_loft, paint_light, shear_to_camera, smoothstep  # noqa: E402

W, H = 72, 56

# (key, palette index, metallic, roughness, emission strength in its own colour)
MATS = [
    ("r1", 0x71, 0.0, 0.42, 0.06), ("r3", 0x73, 0.0, 0.36, 0.08), ("r5", 0x75, 0.0, 0.3, 0.1),
    ("r7", 0x77, 0.0, 0.26, 0.12),
    ("pip", 0x1a, 0.6, 0.26, 0.14), ("pip_lit", 0x1c, 0.6, 0.22, 0.2),
    ("g5", 0x05, 0.5, 0.34, 0.0), ("g8", 0x08, 0.5, 0.3, 0.0), ("ga", 0x0a, 0.5, 0.26, 0.0),
    ("gc", 0x0c, 0.5, 0.22, 0.0), ("glint", 0x0e, 0.2, 0.15, 0.3),
]


def materials():
    pal = k.level_palette()
    m = {}
    for key, index, metallic, roughness, glow in MATS:
        extra = dict(emission=pal[index], emission_strength=glow) if glow > 0 else {}
        m[key] = k.material(f"sberry_{key}", palette=index, metallic=metallic, roughness=roughness, **extra)
    return m


def px(c, r):
    """A pixel edge (column c, row r) of the picture in the picture's plane."""
    return (c - 36.0, 28.0 - r)


# --- The flesh ------------------------------------------------------------------------------------------------------
# The left half of its outline (pixel edges, from the middle of its top round the wing tip's lobe down the lower edge to
# the point); under the M pipe its top edge runs straight (the pipe hides it).
LEFT = [(36.0, 11.8), (33.6, 11.4), (31.6, 10.0), (17.2, 10.0), (15.4, 10.8), (14.2, 9.4), (12.6, 7.4), (10.6, 5.4),
        (9.0, 5.0), (7.4, 5.6), (5.0, 8.0), (2.4, 10.6), (0.6, 12.4), (0.0, 13.6), (0.2, 14.8), (1.2, 15.6),
        (35.4, 49.8), (36.0, 50.0)]
TOP, BELLY = 3.4, -1.0            # the flesh's top and its belly
EDGE = 2.4                        # its edge rounds down over this many pixels
LUMPS = (0.32, 5.0)               # its lumps: height, size (pixels)
MOTTLE = (0.95, 6.5)              # its paint's patches: strength, size (pixels)
# The pips: the sprites' gold crescents in the flesh (pixel centres), their direction along the lower edge.
PIPS = [(6.5, 13.7), (9.5, 16.7), (15.5, 22.7), (18.5, 25.7)]
PIP = (0.75, 1.15, 0.42)          # half-sizes across, along, high
DIMPLE = (0.4, 1.5)               # the dimple under each: depth, radius


def outline():
    left = [px(c, r) for c, r in LEFT]
    right = [(-x, y) for x, y in reversed(left[1:-1])]
    return ccw(chaikin(left + right, 2))


def pips():
    out = []
    for c, r in PIPS:
        x, y = px(c, r)
        out += [(x, y), (-x, y)]
    return out


def flesh_height(x, y, d):
    z = BELLY + 0.2 + (TOP - BELLY - 0.2) * round_edge(d, EDGE)
    lump = noise.noise(Vector((x / LUMPS[1], y / LUMPS[1], 0.37))) * LUMPS[0]
    z += lump * smoothstep(0.5, 2.5, d)
    for sx, sy in pips():
        q = math.hypot(x - sx, y - sy) / DIMPLE[1]
        if q < 1.0:
            z -= DIMPLE[0] * (1.0 - q * q) ** 2
    return z


def flesh(m):
    obj = relief("flesh", [outline()], flesh_height, m, paint=lambda x, y, d: "r3", side="r1", bottom=BELLY,
                 spacing=1.0, smooth_angle=80, band=2.6)
    # by the light it gets, mottled in large soft patches (the upscale's folds of flesh)
    paint_light(obj, m, [(-99, "r1"), (5.3, "r3"), (6.4, "r5"), (7.3, "r7")], 6.5, a=2.2, b=1.0,
                extra=lambda co: MOTTLE[0] * noise.noise(Vector((co.x / MOTTLE[1], co.y / MOTTLE[1], 2.1))))
    return obj


def pip_objects(m):
    out = []
    lean = Vector((1.0, -1.0, 0.0)).normalized()        # along the lower edge (the left ones; mirrored for the right)
    for i, (x, y) in enumerate(pips()):
        d = Vector((lean.x * (1 if x < 0 else -1), lean.y, 0.0))
        z = flesh_height(x, y, 9.0) + PIP[2] * 0.35
        obj = mk.ball(f"pip{i}", (0.0, 0.0, 0.0), PIP, m["pip"], segments=12, rings=6, angle=80)
        rot = Vector((0.0, 1.0, 0.0)).rotation_difference(d).to_matrix().to_4x4()
        obj.data.transform(Matrix.Translation((x, y, z)) @ rot)
        k.recalc_normals(obj)
        paint_light(obj, m, [(-99, "pip"), (6.6, "pip_lit")], 6.4)
        out.append(obj)
    return out


# --- The pipes ------------------------------------------------------------------------------------------------------
M_PATH = [(10.6, 22.2), (24.5, 8.3), (36.0, 18.3), (47.5, 8.3), (61.4, 22.2)]
M_Z = 4.8                         # its axis' height
PIPE_R = 3.15
BEND = 3.4                        # the M's bends' radius
LOW_PIPE = ((17.4, 26.7), (28.6, 38.6))   # the left lower pipe's axis' ends (pixel edges); the right one mirrored
LOW_Z, LOW_R = 4.4, 3.0
# The gold bands on the lower pipe: the sprites' gold crescents on it (pixel centres), and the one on the M's ends.
BANDS = [(21.5, 28.7), (24.5, 31.7), (27.5, 34.7), (30.5, 37.7)]
M_BAND = (12.5, 19.7)


def fillet(points, radius, step=0.75):
    """A path through 2D points, its corners rounded (polish_berry_ring's way: quadratic arcs), sampled every step."""
    pts = [Vector(p) for p in points]
    out = [pts[0]]
    for i in range(1, len(pts) - 1):
        a, b, c = pts[i - 1], pts[i], pts[i + 1]
        d0, d1 = (b - a).normalized(), (c - b).normalized()
        ang = d0.angle(d1)
        cutl = min(radius * math.tan(ang / 2), (b - a).length * 0.45, (c - b).length * 0.45)
        p0, p1 = b - d0 * cutl, b + d1 * cutl
        seg = p0 - out[-1]
        n = max(1, int(seg.length / step))
        out += [out[-1] + seg * (j / n) for j in range(1, n + 1)]
        n = max(3, int(ang * radius / step))
        for j in range(1, n + 1):
            t = j / n
            out.append(p0 * (1 - t) ** 2 + b * 2 * t * (1 - t) + p1 * t * t)
    seg = pts[-1] - out[-1]
    n = max(1, int(seg.length / step))
    out += [out[-1] + seg * (j / n) for j in range(1, n + 1)]
    return out


def pipe(name, path2d, z, r, m):
    """A round steel pipe along a 2D path at height z, its ends rounded."""
    t0 = (path2d[1] - path2d[0]).normalized()
    t1 = (path2d[-1] - path2d[-2]).normalized()
    st = []
    for f, d in ((0.05, 1.0), (0.55, 0.85), (0.85, 0.55)):
        p = path2d[0] - t0 * r * d * 0.62
        st.append((p.x, p.y, z, r * f, r * f, 2.0))
    st += [(p.x, p.y, z, r, r, 2.0) for p in path2d]
    for f, d in ((0.85, 0.55), (0.55, 0.85), (0.05, 1.0)):
        p = path2d[-1] + t1 * r * d * 0.62
        st.append((p.x, p.y, z, r * f, r * f, 2.0))
    obj = section_loft(name, st, m["g8"], segments=12)
    k.smooth(obj, 55)
    paint_light(obj, m, [(-99, "g5"), (4.6, "g8"), (5.9, "ga"), (7.0, "gc")], 7.2)
    return obj


def band(name, centre, axis, r, m):
    """A gold band round a pipe: a flattened ring about the axis."""
    obj = mk.lathe(name, [(r - 0.1, -0.75), (r + 0.4, -0.6), (r + 0.6, 0.0), (r + 0.4, 0.6), (r - 0.1, 0.75)],
                   (0.0, 0.0), m["pip"], segments=16)
    rot = Vector((0.0, 0.0, 1.0)).rotation_difference(axis).to_matrix().to_4x4()
    obj.data.transform(Matrix.Translation(centre) @ rot)
    k.recalc_normals(obj)
    k.smooth(obj, 50)
    paint_light(obj, m, [(-99, "pip"), (6.6, "pip_lit")], 6.4)
    return obj


def pipes(m):
    out = []
    path = fillet([px(c, r) for c, r in M_PATH], BEND)
    out.append(pipe("m_pipe", path, M_Z, PIPE_R, m))
    # its ends' gold bands
    for sx in (1, -1):
        bx, by = px(*M_BAND)
        a, b = Vector(px(*M_PATH[0])), Vector(px(*M_PATH[1]))
        axis = (b - a).normalized()
        p = Vector((bx, by))
        t = (p - a).dot(axis)
        centre = a + axis * t
        c3 = Vector((centre.x * sx, centre.y, M_Z))
        ax3 = Vector((axis.x * sx, axis.y, 0.0))
        out.append(band(f"m_band{sx:+d}", c3, ax3, PIPE_R, m))
    for sx in (1, -1):
        (c0, r0), (c1, r1) = LOW_PIPE
        a, b = Vector(px(c0, r0)), Vector(px(c1, r1))
        a.x *= sx
        b.x *= sx
        path = [a.lerp(b, i / 8) for i in range(9)]
        out.append(pipe(f"low_pipe{sx:+d}", path, LOW_Z, LOW_R, m))
        axis = (b - a).normalized()
        for i, (c, r) in enumerate(BANDS):
            p = Vector(px(c, r))
            p.x *= sx
            t = (p - a).dot(axis)
            centre = a + axis * t
            out.append(band(f"low_band{sx:+d}_{i}", Vector((centre.x, centre.y, LOW_Z)),
                            Vector((axis.x, axis.y, 0.0)), LOW_R, m))
    return out


# --- The pod and the nub ----------------------------------------------------------------------------------------------
POD_Z = 5.2
# (y, radius) from its top (the gold collar, row 18) down to its nose (row 41)
POD = [(10.4, 0.2), (10.2, 1.6), (9.4, 2.9), (8.0, 3.6), (5.0, 3.95), (0.0, 4.0), (-4.5, 3.85), (-7.5, 3.3),
       (-9.8, 2.5), (-11.6, 1.5), (-12.6, 0.7), (-13.0, 0.12)]
POD_BANDS = [9.0, -1.4]           # gold bands round it (the sprites' collar at row 18-19 and a band at row 29)
HOOKS = [(32.4, 31.1)]            # gold hooks on its sides (the left one; mirrored)
NUB = ((36.0, 10.0), 2.1, 2.6)    # the red nub: middle (pixel edges), radius, height of its middle


def pod(m):
    out = []
    seg = 22
    rings = []
    for y, r in POD[1:-1]:
        rings.append([Vector((r * math.cos(2 * math.pi * j / seg), y, POD_Z + r * 0.92 * math.sin(2 * math.pi * j / seg)))
                      for j in range(seg)])
    obj = k.loft("pod", rings, m["g8"], start_point=(0.0, POD[0][0], POD_Z), end_point=(0.0, POD[-1][0], POD_Z))
    k.recalc_normals(obj)
    k.smooth(obj, 60)
    paint_light(obj, m, [(-99, "g5"), (4.6, "g8"), (5.9, "ga"), (7.0, "gc")], 7.2)
    # the white glint (the sprites' (36, 33)) on its sun side
    gx, gy = px(35.6, 32.6)
    mk.paint(obj, lambda c, n: m["glint"] if math.hypot(c.x - gx, (c.y - gy) * 0.55) < 1.0 and n.z > 0.75 else None)
    out.append(obj)
    for i, y in enumerate(POD_BANDS):
        r = max(r_ for yy, r_ in POD if abs(yy - y) < 2.6)
        b = band(f"pod_band{i}", Vector((0.0, y, POD_Z)), Vector((0.0, 1.0, 0.0)), r * 0.98, m)
        b.data.transform(Matrix.Translation((0.0, y, POD_Z)) @ Matrix.Diagonal((1.0, 1.0, 0.92, 1.0)) @
                         Matrix.Translation((0.0, -y, -POD_Z)))
        out.append(b)
    for sx in (1, -1):
        for c, r in HOOKS:
            x, y = px(c, r)
            x *= sx
            st = [(x + sx * 0.9, y + 1.6, POD_Z - 0.4, 0.2, 0.15, 2.0), (x + sx * 0.2, y + 0.6, POD_Z - 0.6, 0.7, 0.45, 2.0),
                  (x - sx * 0.3, y - 0.6, POD_Z - 1.0, 0.65, 0.4, 2.0), (x - sx * 0.1, y - 1.7, POD_Z - 1.4, 0.15, 0.1, 2.0)]
            hook = section_loft(f"hook{sx:+d}", st, m["pip"], segments=10)
            k.smooth(hook, 70)
            paint_light(hook, m, [(-99, "pip"), (6.6, "pip_lit")], 6.4)
            out.append(hook)
    (c, r), rad, z = NUB
    x, y = px(c, r)
    nub = mk.ball("nub", (x, y, z), (rad, rad, rad * 0.9), m["r5"], segments=20, rings=10, angle=80)
    paint_light(nub, m, [(-99, "r1"), (5.2, "r3"), (6.3, "r5"), (7.1, "r7")], 6.4)
    out.append(nub)
    return out


# --- Build, checks, export ----------------------------------------------------------------------------------------------

def build_whole():
    k.reset()
    m = materials()
    parts = [flesh(m)] + pip_objects(m) + pipes(m) + pod(m)
    for obj in parts:
        mk.apply(obj)
    triangulate(parts)
    bpy.context.view_layer.update()
    return parts, m


# name, sprite, box (x0, x1, y0, y1) in the picture's plane (the sprites' boxes, the outer ones reaching out)
PIECES = [("strawberry_wing_tl", 86, (-40.0, -12.0, 0.0, 32.0)), ("strawberry_wing_tm", 88, (-12.0, 12.0, 0.0, 32.0)),
          ("strawberry_wing_tr", 90, (12.0, 40.0, 0.0, 32.0)), ("strawberry_wing_bl", 125, (-24.0, 0.0, -32.0, 0.0)),
          ("strawberry_wing_br", 127, (0.0, 24.0, -32.0, 0.0))]
ORIGINS = {86: (-24.0, 14.0), 88: (0.0, 14.0), 90: (24.0, 14.0), 125: (-12.0, -14.0), 127: (12.0, -14.0)}
LAYOUT = [(86, 0, 0), (88, 24, 0), (90, 48, 0), (125, 12, 28), (127, 36, 28)]
CAPS = {"flesh": "r1", "pip": "pip", "m_pipe": "g5", "low_pipe": "g5", "m_band": "pip", "low_band": "pip",
        "pod_band": "pip", "pod": "g5", "hook": "pip", "nub": "r3"}


def cap_of(obj, m):
    best = None
    for prefix, key in CAPS.items():
        if obj.name.startswith(prefix) and (best is None or len(prefix) > len(best[0])):
            best = (prefix, key)
    return m[best[1] if best else "r1"]


def whole_mask(sheet):
    mask = [[False] * W for _ in range(H)]
    for sprite, c0, r0 in LAYOUT:
        for r, line in enumerate(k.sprite_mask(sheet, sprite)):
            for c, v in enumerate(line):
                if v:
                    mask[r0 + r][c0 + c] = True
    return mask


def build():
    options = k.args()
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    sheet = None
    if "check" in options:
        sheets = options["check"]
        sheet = os.path.join(sheets, "enemy_x27.png") if os.path.isdir(sheets) else sheets
    whole, m = build_whole()
    low, high = mk.bounds(whole)
    print("== whole: %d triangles, %d materials, x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f" % (
        mk.triangles(whole), len(mk.materials_of(whole)), low.x, high.x, low.y, high.y, low.z, high.z))
    bpy.context.scene.view_settings.view_transform = "Standard"
    if sheet:
        mk.compare("whole, as the camera sees it", mk.coverage(whole, W, H), whole_mask(sheet))
    if "whole" in options or "preview" in options:
        seen = []
        for o in whole:
            c = o.copy()
            c.data = o.data.copy()
            bpy.context.scene.collection.objects.link(c)
            seen.append(c)
        shear_to_camera(seen)
        for o in whole:
            o.hide_render = True
        if "whole" in options:
            mk.export(seen, options["whole"])
        if "preview" in options:
            mk.preview(options["preview"] + "strawberry_wing", seen, size=(W, H), scale=10, distance=1.6)
        for o in seen:
            mesh = o.data
            bpy.data.objects.remove(o)
            bpy.data.meshes.remove(mesh)
        for o in whole:
            o.hide_render = False
    bpy.context.view_layer.update()
    for name, sprite, box in PIECES:
        if only and name not in only:
            continue
        origin = ORIGINS[sprite]
        parts = [p for p in (cut(src, box, cap_of(src, m)) for src in whole) if p is not None]
        drop_unused(parts)
        for src in whole:
            src.hide_render = True
        if sheet:
            mk.compare("%s (x27 %d), as the camera sees it" % (name, sprite),
                       mk.coverage(parts, 24, 28, centre=origin), k.sprite_mask(sheet, sprite))
        shear_to_camera(parts)
        mk.transform(parts, Matrix.Translation((-origin[0], -origin[1], 0)))
        bpy.context.view_layer.update()
        triangulate(parts)
        parts = [join(parts, name)]
        parts[0].data.name = name
        mk.report(name, parts, os.path.join(out, name + ".glb"))
        if "preview" in options and options.get("pieces") == "1":
            mk.preview(options["preview"] + name, parts)
        for obj in parts:
            bpy.data.objects.remove(obj)
        for src in whole:
            src.hide_render = False


if __name__ == "__main__":
    build()
