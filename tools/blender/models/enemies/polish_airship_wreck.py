"""What is left of SAVARA's grey airship where the maps paint it burnt out in its dock (stage 4 of the clean ground: the
wreck models that stand in for the maps' painting; sheet I sprites 41 and 79, and 43 and 81 beside them), built with
polish_airship.py's materials and parts (2026-10-25). models.cfg: model zeppelin_41_wreck / _43_wreck / _79_wreck /
_81_wreck enemies/zeppelin_*_wreck.glb origin; wreck i 41 zeppelin_41_wreck, wreck i 43 zeppelin_43_wreck, wreck i 79
zeppelin_79_wreck, wreck i 81 zeppelin_81_wreck. The game draws them where the maps paint the wreck (REEF, SAVARA V,
DIG SITE and SAVARA put 41 above 79 at the docks of their piers, SAVARA IV 79 alone, SAVARA once 41 43 above 79 81),
with the live sprite lines' options (yaw=0; no height=: the pieces stand on the ground layer, 4 pixels over the
terrain, so the wreck lies at z = GROUND, -4), at the live pieces' places.

The painting (REEF, SAVARA V and DIG SITE paint the same two tiles under 41 and 79; SAVARA a taller version of them,
SAVARA IV the lower one alone): in the dock's slot down the pier, where the airship's middle lay (from x -10 to 6 of
the airship's picture, a pixel left of its axis, up the screen from y 21 to 41), a black burnt-out heap with red-hot
wreckage in it: a red frame like the airship's gate (two uprights and two crossbars, x -6 to 0 of y 27-41) and two
red hooks like its brackets below it (x -9 to -4 and 1 to 5 of y 21-26), dark red, glowing (ramp 7, 0x70-0x73); under
it, at the pier's edge over the water, a heap of black rubble (x -14 to 8 of y 4-13). The pier round them, its stone
blocks and the water are the map's.

The model: the envelope gone, its frame burnt out and fallen into the slot: a low black heap (a heightfield over the
slot's outline, its top 1-2 pixels over the terrain, rough), across it four of the frame's rings broken into arcs and
fallen over (dark steel, their edges lit), its keel bent along it, burnt shreds of the envelope's fabric draped over
its sides; in it the red gate and the brackets as red-hot bars (polish_airship's red ramp lit to ramp 7's embers,
emission 0.25-0.35) where the painting draws them, a few small flames licking out of it (0x75, 0.4); the rubble
heap at the pier's edge (79) with a fallen arc, shreds and embers; 43 and 81 hold the shreds and lumps that lie right
of the slot (SAVARA only). The heap is one solid cut along y = 14 between 41 and 79 and along x = 10 between 41 and 43
(the slot lies in 41's and 79's records at every place, a pixel left of the airship's axis, reaching 10 pixels into
43's cell: there the wreck belongs to 41 and 79, which are stand-ins wherever it is painted; 43 and 81 are stand-ins
at one place only).

Coordinates as polish_airship.py's (after its AXIS_X shift): 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up
from the ground layer; the whole's origin is the airship picture's (41's centre at (-12, 28), 43's (12, 28), 79's
(-12, 0), 81's (12, 0)).

Options after "--": --outdir <dir> (default assets/models/enemies), --preview <prefix>, --whole <prefix>, --only <name,...>.
"""
import math
import os
import random
import sys

import bpy
import numpy as np
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
import polish_gyges_wall as gw  # noqa: E402
from polish_arch import cut  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_deli_boss import join  # noqa: E402
from polish_jaw_gun_wreck import rock, shard, bent_bar, inside, jagged, ccw, lump  # noqa: E402
from polish_pyramid_wreck import Noise  # noqa: E402
import polish_airship as live  # noqa: E402

GROUND = -4.0                         # the terrain under the ground layer
SKIRT = 1.5                           # how far the heap's walls reach under it
SEED = 41
# The heap in the slot: its outline (x, y), its height over the terrain (mean, how much it wanders, how fast it falls
# to its outline).
SLOT = [(-9.6, 21.6), (-6.4, 20.0), (-3.0, 20.8), (0.4, 19.8), (3.6, 20.6), (6.4, 22.4), (5.6, 25.6), (6.8, 29.0),
        (5.8, 32.4), (6.6, 36.0), (5.2, 40.2), (2.4, 41.6), (-1.2, 40.6), (-4.6, 41.8), (-8.0, 40.8), (-10.0, 37.6),
        (-9.0, 34.2), (-10.6, 30.6), (-9.6, 27.4), (-10.8, 24.4)]
HEAP = (1.4, 0.8, 1.4)
# The rubble at the pier's edge (79): its outline, its height.
RUBBLE = [(-13.6, 5.6), (-10.4, 4.0), (-6.6, 4.8), (-3.0, 3.2), (1.0, 4.2), (4.6, 3.6), (7.8, 5.6), (7.2, 8.6),
          (8.0, 11.0), (4.2, 12.6), (0.4, 11.8), (-3.6, 13.2), (-7.6, 12.0), (-11.4, 12.8), (-14.2, 9.4)]
RUBBLE_H = (0.8, 0.6, 1.1)
# The frame's rings fallen across the slot: (y of the middle, x of the middle, radius, the arc's ends (degrees, 0:
# +x, 90: up), how far it has fallen over (degrees about x), its tube's radius).
RINGS = [(38.6, -2.4, 6.6, (35.0, 120.0), 38.0, 0.38), (38.0, -2.6, 6.4, (140.0, 168.0), 44.0, 0.36),
         (31.8, -2.0, 7.2, (12.0, 72.0), -34.0, 0.4), (32.4, -2.2, 7.0, (100.0, 160.0), -40.0, 0.38),
         (26.4, -2.2, 7.0, (60.0, 150.0), 42.0, 0.38), (21.8, -1.6, 6.4, (18.0, 64.0), -50.0, 0.34),
         (8.6, -4.0, 6.0, (40.0, 130.0), 58.0, 0.36)]
# The keel along the slot, bent and broken: its two pieces (x, y, height over the terrain).
KEEL = [[(-2.6, 20.6, 0.6), (-2.0, 25.0, 1.7), (-1.4, 29.6, 2.1), (-1.8, 31.6, 1.4)],
        [(-2.2, 33.0, 0.9), (-3.0, 36.4, 1.9), (-2.6, 40.8, 1.2)]]
# The red-hot wreckage (the gate and the brackets): bars of (x, y) points lying on the heap, their radius.
RED_BARS = [([(-5.2, 40.4), (-5.5, 37.4), (-5.0, 34.8)], 0.48), ([(-5.3, 33.6), (-5.0, 30.6)], 0.45),
            ([(-2.6, 40.0), (-2.3, 36.2), (-2.8, 30.2)], 0.48),
            ([(-6.4, 37.0), (-3.8, 37.4), (-1.0, 36.6)], 0.42), ([(-6.0, 33.4), (-3.6, 33.0), (0.2, 34.0)], 0.42),
            ([(-2.2, 29.8), (-1.8, 27.6)], 0.4), ([(2.0, 30.4), (2.3, 27.4)], 0.38),
            ([(-8.6, 26.2), (-8.9, 23.0), (-7.4, 21.4), (-5.0, 21.8)], 0.44),
            ([(1.2, 25.2), (2.0, 22.2), (3.8, 21.2), (5.0, 22.8)], 0.42)]
FLAMES = [(-4.0, 38.6, 1.6), (-3.8, 31.6, 1.3), (-7.6, 23.4, 1.2), (3.0, 23.0, 1.0)]   # (x, y, height)
# Burnt shreds of the envelope's fabric: (outline, z over the terrain, thickness, tilt about x and y).
SHREDS = [([(-11.8, 24.4), (-10.0, 23.6), (-9.4, 27.6), (-11.4, 28.4)], 0.2, 0.2, (0.0, 24.0)),
          ([(5.6, 33.4), (7.8, 32.6), (8.2, 36.6), (6.0, 37.2)], 0.2, 0.2, (0.0, -22.0)),
          ([(-11.2, 34.4), (-9.6, 34.8), (-10.0, 38.6), (-11.8, 38.0)], 0.2, 0.2, (8.0, 18.0)),
          ([(-11.0, 6.2), (-8.4, 5.4), (-8.0, 8.0), (-10.2, 8.8)], 0.5, 0.2, (10.0, -12.0)),
          ([(3.4, 10.0), (5.8, 9.6), (6.2, 11.6), (3.8, 12.0)], 0.5, 0.2, (-8.0, 10.0)),
          # (right of the slot, 43's and 81's: SAVARA)
          ([(10.8, 24.0), (13.2, 23.4), (13.8, 26.8), (11.2, 27.4)], 0.15, 0.2, (0.0, -14.0)),
          ([(11.2, 34.6), (12.8, 34.0), (13.4, 37.2), (11.6, 37.8)], 0.15, 0.2, (6.0, 10.0)),
          ([(10.6, 4.8), (12.8, 4.4), (13.2, 7.2), (11.0, 7.6)], 0.3, 0.2, (-6.0, -10.0))]
# Lumps of rubble and embers: (x, y, size, kind).
LUMPS = [(-12.4, 7.4, 1.6, "char"), (-6.6, 10.6, 1.4, "dark"), (-1.4, 6.2, 1.8, "char"), (4.4, 6.8, 1.3, "dark"),
         (-4.2, 4.4, 1.1, "char"), (1.8, 11.4, 1.0, "dark"), (-8.8, 30.0, 1.0, "dark"), (4.8, 28.4, 1.1, "char"),
         (-7.6, 38.6, 1.2, "char"), (3.0, 38.4, 1.3, "dark"), (-0.4, 24.0, 1.0, "char"), (4.4, 33.8, 0.9, "char"),
         (-8.4, 34.6, 0.9, "dark"), (0.8, 31.4, 0.8, "char"),
         (12.6, 30.4, 1.0, "dark"), (12.0, 10.0, 1.1, "char"), (-3.4, 8.8, 0.6, "ember"), (2.6, 4.6, 0.5, "ember"),
         (-7.2, 6.0, 0.45, "ember")]
PIECES = [("zeppelin_41_wreck", (-24.0, 10.0, 14.0, 60.0), (-12.0, 28.0)),
          ("zeppelin_43_wreck", (10.0, 24.0, 14.0, 60.0), (12.0, 28.0)),
          ("zeppelin_79_wreck", (-24.0, 10.0, -14.0, 14.0), (-12.0, 0.0)),
          ("zeppelin_81_wreck", (10.0, 24.0, -14.0, 14.0), (12.0, 0.0))]


def materials():
    m = live.materials()
    pal = k.level_palette()

    def mat(name, index, metallic=0.2, roughness=0.8, glow=0.0):
        extra = dict(emission=pal[index], emission_strength=glow) if glow > 0 else {}
        return k.material("zepw_" + name, palette=index, metallic=metallic, roughness=roughness, **extra)
    m["char"] = mat("char", 0x01, 0.1, 0.85)
    m["char2"] = mat("char2", 0x02, 0.2, 0.8)
    m["iron"] = mat("iron", 0x04, 0.5, 0.45)
    m["iron_lit"] = mat("iron_lit", 0x07, 0.5, 0.4)
    m["shred"] = mat("shred", 0x03, 0.0, 0.8)
    m["shred_lit"] = mat("shred_lit", 0x05, 0.0, 0.78)
    m["ember_dim"] = mat("ember_dim", 0x71, 0.0, 0.6, 0.25)
    m["ember"] = mat("ember", 0x73, 0.0, 0.5, 0.3)
    m["ember_hot"] = mat("ember_hot", 0x75, 0.0, 0.5, 0.35)
    m["flame"] = mat("flame", 0x76, 0.0, 0.5, 0.4)
    return m


def heightfield(name, outline, height, mat, seed):
    """A low heap over a plan outline: a heightfield solid (polish_gyges_wall.Plate on its 0.5 grid) whose top wanders
    by noise round height[0] over the terrain and falls to the outline over height[2], its walls down under it."""
    mean, wander, fall = height
    noise = Noise(seed, 1.6)
    xs = [p[0] for p in outline]
    ys = [p[1] for p in outline]
    x0, x1 = math.floor(min(xs) * 2) / 2 - 0.5, math.ceil(max(xs) * 2) / 2 + 0.5
    y0, y1 = math.floor(min(ys) * 2) / 2 - 0.5, math.ceil(max(ys) * 2) / 2 + 0.5
    poly = jagged(outline, seed * 0.37, 0.7, 0.7)

    def dist(x, y):
        best = 1e9
        for (ax, ay), (bx, by) in zip(poly, poly[1:] + poly[:1]):
            dx, dy = bx - ax, by - ay
            t = max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / max(dx * dx + dy * dy, 1e-9)))
            best = min(best, math.hypot(x - ax - t * dx, y - ay - t * dy))
        return best if inside((x, y), poly) else -best

    def top(X, Y):
        out = np.empty(X.shape)
        for idx in np.ndindex(X.shape):
            x, y = float(X[idx]), float(Y[idx])
            d = dist(x, y)
            rise = math.sqrt(max(0.0, min(1.0, d / fall)) * (2 - max(0.0, min(1.0, d / fall))))
            out[idx] = GROUND + 0.15 + (mean + wander * noise.fbm(x, y, 3)) * rise
        return out

    def cells(X, Y):
        return np.vectorize(lambda x, y: inside((x, y), poly))(X, Y)
    plate = gw.Plate((x0, x1, y0, y1), top, base=lambda X, Y: np.full(X.shape, GROUND - SKIRT), cells=cells,
                     bottom=False)   # (no bottom: under the terrain, never seen)
    obj, kinds, _ = plate.mesh(name, lambda X, Y: np.ones(X.shape, bool))
    obj.data.materials.append(mat)
    return obj


def paint_heap(obj, m, seed):
    """The heap's top black with dark patches; its walls black."""
    noise = Noise(seed, 1.3)
    mk.paint(obj, lambda c, n: m["char2"] if n.z > 0.5 and noise(c.x, c.y) > 0.3 else m["char"])


def ring(name, spec, m):
    """A ring of the frame broken into an arc and fallen over: dark iron, its upper side lit."""
    y, x, radius, (a0, a1), fall, tube = spec
    pts = []
    steps = max(6, int(abs(a1 - a0) / 9))
    for i in range(steps + 1):
        a = math.radians(a0 + (a1 - a0) * i / steps)
        p = Vector((radius * math.cos(a), 0.0, radius * math.sin(a)))
        # fallen over about x (towards the screen's top or bottom), its foot on the heap
        q = Matrix.Rotation(math.radians(fall), 3, "X") @ p
        pts.append((x + q.x, y + q.y, GROUND + 1.2 + q.z * 0.55, tube))
    obj = mk.smooth_tube(name, pts, m["iron"], 6, 1)
    k.smooth(obj, 55)
    mk.paint(obj, lambda c, n: m["iron_lit"] if n.z > 0.6 and n.x < 0.3 else None)
    return obj


def build_whole(m):
    heap = heightfield("heap", SLOT, HEAP, m["char"], SEED)
    paint_heap(heap, m, SEED)
    rubble = heightfield("rubble", RUBBLE, RUBBLE_H, m["char"], SEED + 5)
    paint_heap(rubble, m, SEED + 5)
    surface = mk.surface([heap, rubble])

    def on_top(x, y, lift=0.0):
        h = surface(x, y)
        return (h[0].z if h else GROUND) + lift
    for i, spec in enumerate(RINGS):
        ring(f"ring{i}", spec, m)
    for i, path in enumerate(KEEL):
        bent_bar(f"keel{i}", [(x, y, GROUND + z, 0.62) for x, y, z in path], 0.62, m["iron"], 6)
    for i, (path, radius) in enumerate(RED_BARS):
        pts = [(x, y, on_top(x, y, radius * 0.55), radius) for x, y in path]
        bar = bent_bar(f"red{i}", pts, radius, m["ember"], 6)
        mk.paint(bar, lambda c, n: m["ember_hot"] if n.z > 0.75 else (m["ember_dim"] if n.z < -0.2 else None))
    for i, (x, y, h) in enumerate(FLAMES):
        base = on_top(x, y, -0.2)
        flame = lump(f"flame{i}", (x, y, base + h * 0.5), (0.55, 0.45, h * 0.5), m["flame"], 9.0 + i, 0.3, 1)
        k.smooth(flame, 70)
    for i, (outline, z, thick, tilt) in enumerate(SHREDS):
        cx = sum(p[0] for p in outline) / len(outline)
        cy = sum(p[1] for p in outline) / len(outline)
        sh = shard(f"shred{i}", jagged(outline, 2.0 + i, 0.35, 0.5), on_top(cx, cy, z - 0.1), thick, m["shred"], tilt)
        mk.paint(sh, lambda c, n: m["shred_lit"] if n.z > 0.8 and (c.x + c.y) % 3.0 > 1.4 else None)
    rng = random.Random(SEED)
    for i, (x, y, size, kind) in enumerate(LUMPS):
        mat = {"char": m["char"], "dark": m["dark"], "ember": m["ember_dim"]}[kind]
        rock(f"lump{i}", (x, y, on_top(x, y, -0.25)), (size, size * rng.uniform(0.6, 0.9), size * 0.5), mat,
             3.0 + 1.3 * i, flat=GROUND - 0.5)
    whole = mk.meshes()
    for obj in whole:
        mk.apply(obj)
    bpy.context.view_layer.update()
    return whole


def build():
    options = k.args()
    out = mk.outdir(options)
    only = set(options["only"].split(",")) if "only" in options else None
    k.reset()
    bpy.context.scene.view_settings.view_transform = "Standard"
    m = materials()
    whole = build_whole(m)
    triangulate(whole)
    print("whole airship wreck: %d triangles, %d objects" % (mk.triangles(whole), len(whole)))
    if "whole" in options:
        mk.export(whole, options["whole"] + "zeppelin_wreck.glb")
    if "preview" in options:
        mk.preview(options["preview"] + "zeppelin_wreck_whole", whole, size=(48, 56), scale=8, distance=1.6,
                   centre=(0.0, 22.0))
    for name, box, centre in PIECES:
        if only and name not in only:
            continue
        parts = [p for p in (cut(src, box, m["char"]) for src in whole) if p is not None]
        mk.transform(parts, Matrix.Translation((-centre[0], -centre[1], 0.0)))
        triangulate(parts)
        piece = join(parts, name)
        bpy.context.view_layer.update()
        for src in whole:
            src.hide_render = True
        mk.report(name, [piece], os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, [piece])
        bpy.data.objects.remove(piece)
        for src in whole:
            src.hide_render = False


if __name__ == "__main__":
    build()
