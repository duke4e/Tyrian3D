"""The drop of fire of BRAINIAC, CORE, ICE EXIT, NOSE DRIP and SAVARA (sheet 3 sprite 267, 2x2: 18 x 27
pixels in the 24 x 28 cell; sky and top layers, about 120 of them; its animation 267 267 269 269 269 267),
polished (2026-10-19; it replaces wave1_b.py's flame_drop(), a lumpy glowing loft). models.cfg: sprite 3
267 flame_drop yaw=0 glow, frame 3 269 flame_drop_269.

As the sprite and its 4x upscale draw it: a drop of fire, its point up the screen (column 12 of row
0), swelling to a round bottom (columns 4-21 of rows 15-21, rows 24-26 closing it), outlined in the
darkest red (the sprite's ramp 7, shade 0); inside, tongues of flame rise towards the point in layers
of red, orange and yellow round a white-yellow heart low in the drop (columns 9-13 of rows 15-20,
shades 13-15). 269, the flicker, leans the drop's lower half a pixel to the left and moves the
tongues: a model of its own, flame_drop_269 (no other enemy uses 3 269).

The model: a glossy drop of fire, round in section, its surface the sprite's heat: the shades of the
sprite (smoothed, as the 4x upscale softens them) painted on in bands of the fire's ramp, each band
glowing in its own colour, more the hotter (polish_lava_ball.py's and polish_blobs.py's drops), the
hotter parts swelling out of the surface (the tongues raised, the cooler red between them lower), so
that the game's sun puts glints on them as on molten glass. The underside is the dark red of the
outline. The fire's own pieces (fire_body() and the rest) also build polish_comet.py's comet;
polish_fin_chevron.py uses monotone().

Origin at the sprite's centre (pixel 12, 14); +Y up the screen, +Z towards the camera; the drop's
axis lies in z = 0 (the game centres sky objects in height).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the
silhouette of each frame against <dir>/enemy_3.png), --preview <prefix>, --only <name,...>.
"""
import math
import os
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402

# The sprites' shades (palette index - 0x70: ramp 7, the fire), '.' transparent.
FLAME_267 = """
............0...........
...........030..........
..........04730.........
.........016830.........
.........047a510........
.........0799740........
........038a86620.......
........038c88750.......
.......0459c97870.......
.......047aeb78720......
.......059bdc69740......
......045aaba59860......
.....0187baa8477760.....
.....0498ca97a668930....
.....0797dc9db868a60....
....02796eebeda48a950...
....04497dfcedb69ba710..
....05267dedeeb78a9620..
....05337cccdcd8a88720..
....02558accacdd998630..
....02468bed9bdbba9730..
....01467acdbaba9a9530..
.....03579a9998787540...
.....02458aaa98654410...
......03456888544210....
.......022456533200.....
........000000000.......
........................
"""

FLAME_269 = """
............0...........
...........030..........
..........03740.........
..........038610........
.........015a740........
.........0479970........
........02668a830.......
........05788c830.......
........07879c9540......
.......02787bea740......
.......04796cdb950......
.......06895abaa540.....
......0677748aab7810....
.....039866a79ac8940....
.....06a868bd9cd7970....
....059a84adebee69720...
...017ab96bdecfd79440...
...0269a87beeded76250...
...02788a8dcdccc73350...
...036899ddcacca85520...
...0379abbdb9deb86420...
...0359a9ababdca76410...
....0457878999a97530....
....01445689aaa85420....
.....01244588865430.....
......002335654220......
........000000000.......
........................
"""

# The heat bands: (lowest heat, palette index, emission strength in the palette colour), ramp 7 from
# the outline's darkest red to white; the hotter, the more it glows.
FIRE_BANDS = [(-99.0, 0x70, 0.35), (1.2, 0x72, 0.45), (2.6, 0x74, 0.6), (4.0, 0x76, 0.75), (5.4, 0x77, 0.9),
              (6.8, 0x78, 1.05), (8.0, 0x79, 1.2), (9.1, 0x7a, 1.35), (10.2, 0x7b, 1.5), (11.2, 0x7c, 1.7),
              (12.2, 0x7d, 1.9), (13.1, 0x7e, 2.1), (14.0, 0x7f, 2.3)]

# The drop's body: the half-depths above and below its axis (times the half-width), how far the
# hottest parts swell out (pixels) and the shade under which the surface sinks a little instead, the
# smoothing of the sprite's shades (pixels across and along y), the rings' spacing and the segments
# round each ring (on its upper half, which the cameras see, and its lower half).
DEPTH = (0.72, 0.55)
SWELL, SWELL_FROM = 1.25, 5.5
SIGMA = (0.5, 0.85)
STEP = 0.36
SEGMENTS = (24, 10)

FRAMES = [("flame_drop", 267, FLAME_267), ("flame_drop_269", 269, FLAME_269)]


# --- The sprite's heat --------------------------------------------------------------------------------------

def grid(art):
    """Rows of shades (0-15) or None, from the art's lines."""
    return [[None if ch == "." else int(ch, 16) for ch in line] for line in art.strip("\n").splitlines()]


class Heat:
    """The sprite's shades smoothed (a Gaussian over its pixels, sigma (across, along y) wide: flames
    rise, so their streaks are kept and the rows' steps evened out; only the sprite's own pixels
    counted), read anywhere: pixel (c, r) is at x = c + 0.5 - width / 2, y = top - r - 0.5."""

    def __init__(self, rows, top, sigma=SIGMA):
        self.h, self.w = len(rows), len(rows[0])
        self.top = top
        value = np.array([[0.0 if s is None else float(s) for s in line] for line in rows])
        mask = np.array([[0.0 if s is None else 1.0 for s in line] for line in rows])

        def blur(a, sx, sy):
            for axis, s in ((1, sx), (0, sy)):
                radius = int(math.ceil(s * 3))
                kernel = np.exp(-np.arange(-radius, radius + 1) ** 2 / (2 * s * s))
                pad = [(0, 0), (0, 0)]
                pad[axis] = (radius, radius)
                a = np.apply_along_axis(lambda line: np.convolve(line, kernel, "valid"), axis, np.pad(a, pad))
            return a
        weight = blur(mask, *sigma)
        near = blur(value * mask, *sigma) / np.maximum(weight, 1e-6)
        # Outside the sprite, the nearest pixels' shades (a wider blur), so the field runs on smoothly.
        far = blur(value * mask, 2.5, 2.5) / np.maximum(blur(mask, 2.5, 2.5), 1e-6)
        self.field = np.where(weight > 0.2, near, far)

    def __call__(self, x, y):
        """Bilinear in the smoothed shades."""
        c = x + self.w / 2 - 0.5
        r = self.top - y - 0.5
        c = min(max(c, 0.0), self.w - 1.001)
        r = min(max(r, 0.0), self.h - 1.001)
        c0, r0 = int(c), int(r)
        fc, fr = c - c0, r - r0
        f = self.field
        return ((f[r0, c0] * (1 - fc) + f[r0, c0 + 1] * fc) * (1 - fr) +
                (f[r0 + 1, c0] * (1 - fc) + f[r0 + 1, c0 + 1] * fc) * fr)


def monotone(xs, ys):
    """A smooth curve through (xs, ys) that never overshoots them (monotone cubic)."""
    n = len(xs)
    d = [(ys[i + 1] - ys[i]) / (xs[i + 1] - xs[i]) for i in range(n - 1)]
    m = [d[0]] + [(d[i - 1] + d[i]) / 2 if d[i - 1] * d[i] > 0 else 0.0 for i in range(1, n - 1)] + [d[-1]]
    for i in range(n - 1):
        if d[i] == 0:
            m[i] = m[i + 1] = 0.0
            continue
        a, b = m[i] / d[i], m[i + 1] / d[i]
        if a * a + b * b > 9:
            t = 3 / math.sqrt(a * a + b * b)
            m[i], m[i + 1] = t * a * d[i], t * b * d[i]

    def f(x):
        x = min(max(x, xs[0]), xs[-1])
        i = max(0, min(n - 2, next((j for j in range(n - 1) if x <= xs[j + 1]), n - 2)))
        h = xs[i + 1] - xs[i]
        t = (x - xs[i]) / h
        return ((2 * t ** 3 - 3 * t ** 2 + 1) * ys[i] + (t ** 3 - 2 * t ** 2 + t) * h * m[i] +
                (-2 * t ** 3 + 3 * t ** 2) * ys[i + 1] + (t ** 3 - t ** 2) * h * m[i + 1])
    return f


class Outline:
    """The sprite's silhouette row by row as a smooth body outline: its half-width and middle at any y
    (the rows' pixel steps evened out), closing to a point `point` past its top row's middle and
    rounding off past its bottom row (bottom_round: (how far below its middle, the width there as a
    fraction of its own))."""

    def __init__(self, rows, top, soften=1, point=0.5, bottom_round=((0.4, 0.82), (0.6, 0.5), (0.72, 0.0))):
        spans = []
        for r, line in enumerate(rows):
            cols = [c for c, s in enumerate(line) if s is not None]
            if cols:
                left, right = cols[0] - len(line) / 2, cols[-1] + 1 - len(line) / 2
                spans.append([top - r - 0.5, (right - left) / 2, (left + right) / 2])
        spans.sort()
        for _ in range(soften):
            spans = [spans[0]] + [[spans[i][0], (spans[i - 1][1] + 2 * spans[i][1] + spans[i + 1][1]) / 4,
                                   (spans[i - 1][2] + 2 * spans[i][2] + spans[i + 1][2]) / 4]
                                  for i in range(1, len(spans) - 1)] + [spans[-1]]
        y0, w0, c0 = spans[0]
        y1, w1, c1 = spans[-1]
        closing = [(y0 - below, w0 * f, c0) for below, f in sorted(bottom_round, reverse=True)]
        points = closing + spans + [(y1 + point, 0.0, c1)]
        self.y0, self.y1 = points[0][0], points[-1][0]
        ys = [p[0] for p in points]
        self.width = monotone(ys, [p[1] for p in points])
        self.middle = monotone(ys, [p[2] for p in points])


# --- The fire's body ----------------------------------------------------------------------------------------

def fire_materials(prefix, bands=FIRE_BANDS):
    pal = k.level_palette()
    return [(lowest, k.material(f"{prefix}_{index:02x}", palette=index, metallic=0.0,
                                roughness=0.38 if index < 0x74 else 0.26, emission=pal[index],
                                emission_strength=glow))
            for lowest, index, glow in bands]


def fire_body(name, outline, heat, bands, depth=DEPTH, swell=SWELL, swell_from=SWELL_FROM, step=STEP,
              segments=SEGMENTS, axis_z=0.0, heat_of=None):
    """A body of fire along y: round sections (half-width from the outline, depth[0] and depth[1] of
    it above and below its axis), its faces in the bands of the heat (bands: [(lowest, material)]
    ascending; heat_of(x, y, normal) -> heat, by default the sprite's under the point, the underside
    the outline's dark red) cut along the bands' borders, then swollen out along the normals where it
    is hot."""
    count = max(8, int(round((outline.y1 - outline.y0) / step)))
    ys = [outline.y0 + (outline.y1 - outline.y0) * (i + 0.5) / count for i in range(count)]
    # Finer at the ends, where the outline closes.
    ys = sorted(set(ys) | {outline.y0 + d for d in (0.04, 0.1, 0.18)} | {outline.y1 - d for d in (0.05, 0.12)})
    up, down = segments
    angles = [math.pi * j / up for j in range(up)] + [math.pi + math.pi * j / down for j in range(down)]
    rings = []
    for y in ys:
        w = max(outline.width(y), 0.02)
        cx = outline.middle(y)
        rings.append([Vector((cx + w * math.cos(a), y, axis_z + w * math.sin(a) * (depth[0] if math.sin(a) >= 0 else
                                                                              depth[1]))) for a in angles])
    # Built along +Y with the points counter-clockwise seen from -Y: tyrkit.loft's faces then face out
    # after its normals are recalculated anyway.
    first, last = rings[0], rings[-1]
    obj = k.loft(name, rings, None,
                 start_point=(outline.middle(outline.y0), outline.y0, axis_z),
                 end_point=(outline.middle(outline.y1), outline.y1, axis_z))
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bpy.data.objects.remove(obj)
    bm.normal_update()
    if heat_of is None:
        def heat_of(x, y, n):
            return heat(x, y) if n.z > -0.05 else min(heat(x, y), 1.0)
    values = {v: heat_of(v.co.x, v.co.y, v.normal) for v in bm.verts}
    normals = {v: v.normal.copy() for v in bm.verts}
    borders = [lowest for lowest, _ in bands[1:]]
    for t in borders:
        made = mk.split_along(bm, values, t)
        for v in made:  # new points on an edge: the normal of the edge's ends, blended
            ends = [e.other_vert(v) for e in v.link_edges if e.other_vert(v) in normals]
            n = sum((normals[e] for e in ends), Vector())
            normals[v] = n.normalized() if n.length > 1e-6 else Vector((0, 0, 1))
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    kinds = [sum(sum(values[v] for v in f.verts) / len(f.verts) > t for t in borders) for f in bm.faces]
    for v in bm.verts:
        n = normals[v]
        lift = swell * max(-0.3, (values[v] - swell_from) / (15.0 - swell_from)) * mk.smoothstep(-0.1, 0.5, n.z)
        v.co = v.co + n * lift
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    used = sorted(set(kinds))
    for i in used:
        mesh.materials.append(bands[i][1])
    for poly, kind in zip(mesh.polygons, kinds):
        poly.material_index = used.index(kind)
    k.recalc_normals(obj)
    return k.smooth(obj, 70)


def triangles(objects):
    return mk.triangles(objects)


def build():
    options = k.args()
    only = set(options["only"].split(",")) if "only" in options else None
    for name, sprite, art in FRAMES:
        if only is not None and name not in only:
            continue
        k.reset()
        rows = grid(art)
        outline = Outline(rows, 14.0)
        heat = Heat(rows, 14.0)
        fire_body(name, outline, heat, fire_materials("flame"))
        parts = mk.meshes()
        if "check" in options:
            k.check_silhouette(os.path.join(options["check"], "enemy_3.png"), sprite)
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        mk.report(name, parts, os.path.join(mk.outdir(options), name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, parts)


if __name__ == "__main__":
    build()
