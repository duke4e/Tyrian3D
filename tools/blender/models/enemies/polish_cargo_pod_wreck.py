"""What is left of the cargo pod "812" on the block house of the asteroid levels once it is destroyed, under its back
end (stage 4 of the clean ground: the wreck models that stand in for the maps' painting of it; sheet P sprites 203
beside 205 above 241 beside 243; the back end's own damaged look, P 169 and 207, stands above them as the stand-in of
165 and 167), built on polish_cargo_pod.py (2026-10-25). models.cfg: model cargo_pod_ml_wreck / _mr_wreck / _bl_wreck
/ _br_wreck enemies/cargo_pod_*_wreck.glb origin; wreck p 203 cargo_pod_ml_wreck, wreck p 205 cargo_pod_mr_wreck,
wreck p 241 cargo_pod_bl_wreck, wreck p 243 cargo_pod_br_wreck. The game draws them where the maps paint the wreck
(ASTEROID1, ASTEROID2, ASTCITY, AST. CITY, AST ROCK: nine pods), with the live sprite lines' options (yaw=0 height=-4),
at the live pieces' places.

The painting (in the HD tiles and at 1x; columns and rows of the 48 x 84 picture; two versions: A at ASTEROID2's
left pod, ASTCITY's two, ASTEROID1's and AST. CITY's, B at ASTEROID2's right pod and AST ROCK's three; 203 and 205
are stand-ins at all nine, 241 only at the A's (the B's paint it as the live sprite), 243 only at the B's): the pod
torn open from its back end's break (row 28) to its front: its top gone, a burnt-out hollow down to the roof
(columns 13-35, black, 0x01-0x04) with red-hot seams glowing in it (ramp 7, 0x70-0x75: down its left side at column
11, a double line at columns 25 and 27, another at 28-29, a bar across at row 51 joined to a stem down the front), its
left chamfer and side still lit as before, its right chamfer a torn plate (lit, columns 36-38 of rows 34-45); its
front cap broken away; the dock in front of it burnt black (rows 56-65), red-hot lines across it (A: a stem at column
22 under a bar at row 56; B: a frame of lines at columns 25-33 joined across at row 61); the house's ribbed front and
its sides as the live sprites draw them.

The model: polish_cargo_pod.py's house, pod, dock and cradle, then broken: the pod's top and front torn out down to a
little over the roof (an exact boolean with a jagged prism, its walls and floor black), the left chamfer and the
right one's torn edge standing; everything scorched by a field strongest in the hollow and over the dock
(polish_jaw_gun_wreck.scorch: shades three darker), its clamps and vents blown away
(a few black lumps left), its bay black; the red-hot seams as glowing bars lying where the painting draws them (placed so that the camera sees them
there: y - S(z), as polish_cargo_pod lays everything out), ramp 7 at emission 0.3-0.38; torn plates curling up out of
the hollow's rim, black lumps and embers in it. Cut along the planes the camera sees as the sprites' edges as the live
pod (polish_stone_face.view_cut at the roof's height), each piece moved so that its sprite's centre is its origin.

Coordinates as polish_cargo_pod.py's: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the floor (the
roof at 10); E(c, r) is the picture's pixel corner (c, r): (c - 24, 56 - r).

Options after "--": --outdir <dir> (default assets/models/enemies), --preview <prefix>, --whole <prefix>, --only <name,...>.
"""
import math
import os
import random
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_stone_face import view_cut  # noqa: E402
from polish_jaw_gun_wreck import scorch, jagged, ccw, shard, bent_bar, rock  # noqa: E402
from polish_pyramid_wreck import break_with, Noise  # noqa: E402
import polish_cargo_pod as live  # noqa: E402

H, S, E = live.H, live.S, live.E
SEED = 203
# The hollow torn through the pod's top and front (plan, the pod's own coordinates), its floor.
HOLLOW = [(-15.2, 19.6), (-12.4, 21.0), (-9.0, 22.4), (-6.0, 23.2), (-3.0, 24.8), (0.6, 24.2), (4.0, 25.0),
          (7.6, 24.0), (10.6, 24.8), (13.4, 23.2), (15.6, 20.4), (14.6, 17.0), (12.6, 15.4), (12.8, 11.0),
          (15.4, 8.6), (15.8, 4.2), (14.6, 0.6), (10.0, -1.6), (5.0, -1.2), (0.0, -1.8), (-5.0, -1.2), (-10.0, -1.6),
          (-14.8, -0.6), (-15.6, 3.4), (-15.0, 7.6), (-15.8, 11.8), (-15.0, 15.6)]
HOLLOW_FLOOR = H + 0.7
# The scorch: spots (column, row of the picture, radii, strength), its noise and levels.
SPOTS = [(24.0, 42.0, 13.0, 15.0, 1.3), (24.0, 61.0, 12.0, 5.5, 1.25), (9.0, 40.0, 3.5, 12.0, 0.45),
         (37.5, 40.0, 3.0, 12.0, 0.55), (6.0, 68.0, 4.0, 3.0, 0.5)]
BURN_BASE, BURN_NOISE, LEVELS = 0.1, 0.2, (0.45,)      # (one level: three shades darker; the black is the hollow's)
# The red-hot seams: (points (column, row of the picture, where the camera sees them), height over the roof, radius,
# glow: "dim", "mid", "hot").
SEAMS = [([(11.5, 34.0), (11.4, 40.0), (11.6, 47.5)], 1.2, 0.42, "mid"),
         ([(25.5, 30.0), (25.4, 34.0), (25.6, 38.5)], 1.2, 0.4, "mid"),
         ([(27.5, 29.0), (27.6, 33.0), (27.4, 38.0)], 1.2, 0.4, "dim"),
         ([(28.5, 36.0), (28.8, 42.0), (28.6, 49.5)], 1.2, 0.45, "hot"),
         ([(16.0, 51.5), (19.5, 51.2), (23.5, 51.6)], 1.2, 0.45, "hot"),
         ([(20.5, 52.0), (20.4, 54.0), (20.6, 56.0)], 1.0, 0.4, "mid"),
         ([(17.0, 53.4), (20.0, 53.6)], 1.2, 0.35, "dim"),
         # the dock, A (left): a bar across and a stem down
         ([(19.0, 56.4), (22.5, 56.6), (26.5, 56.3)], 0.35, 0.42, "hot"),
         ([(22.4, 57.0), (22.6, 61.0), (22.4, 65.5)], 0.3, 0.42, "mid"),
         # the dock, B (right): uprights joined across
         ([(25.5, 54.0), (25.4, 59.0), (25.6, 66.0)], 0.3, 0.4, "mid"),
         ([(27.5, 55.0), (27.6, 60.0), (27.4, 64.5)], 0.3, 0.4, "dim"),
         ([(31.5, 53.5), (31.8, 57.0), (31.6, 61.0)], 0.3, 0.4, "mid"),
         ([(27.0, 61.4), (30.0, 61.2), (33.5, 61.5)], 0.32, 0.42, "hot")]
GLOWS = {"dim": (0x73, 0.26), "mid": (0x73, 0.3), "hot": (0x75, 0.38)}
# Torn plates curling up out of the hollow's rim: (outline (plan), z, thickness, tilt about x and y); lumps and embers
# in the hollow (plan x, y, size, kind).
PLATES = [([(-11.6, 18.6), (-9.0, 19.8), (-8.4, 22.4), (-11.0, 21.6)], H + 8.0, 0.3, (-30.0, 24.0)),
          ([(-6.4, 21.4), (-3.2, 22.4), (-3.6, 24.0), (-6.6, 23.2)], H + 8.8, 0.3, (-42.0, 6.0)),
          ([(8.2, 21.6), (11.0, 22.4), (11.4, 24.2), (8.4, 23.6)], H + 8.6, 0.3, (-36.0, -20.0)),
          ([(-4.0, 6.0), (0.4, 5.2), (1.2, 8.4), (-3.2, 9.2)], HOLLOW_FLOOR + 0.2, 0.28, (14.0, -10.0)),
          ([(4.4, 14.0), (8.0, 13.2), (8.6, 16.4), (5.0, 17.2)], HOLLOW_FLOOR + 0.3, 0.28, (-18.0, 16.0))]
LUMPS = [(-6.4, 12.4, 1.6, "char"), (-1.0, 17.6, 1.4, "dark"), (6.6, 8.0, 1.5, "char"), (-8.0, 3.6, 1.2, "dark"),
         (9.4, 18.6, 1.1, "char"), (2.6, 2.4, 1.0, "char"), (-2.6, 10.2, 0.6, "ember"), (7.8, 12.4, 0.55, "ember")]
# what is left of the clamps and vents on the dock (plan x, y, size, kind; on the dock's floor)
DOCK_LUMPS = [(-4.6, -2.2, 1.3, "dark"), (6.0, -2.0, 1.2, "char"), (-8.0, -6.4, 1.0, "char"), (10.6, -7.0, 0.9, "dark")]
GONE = ("dock_clamp", "vent")
WRECK_PIECES = [(name + "_wreck", sprite, box, centre) for name, sprite, box, centre in live.PIECES[2:]]


def burn(co):
    c, r = co.x + 24.0, 56.0 - (co.y + S(co.z))     # (where the camera sees the point)
    v = BURN_BASE + BURN_NOISE * burn.noise.fbm(c, r, 2)
    for sc, sr, rc, rr, s in SPOTS:
        v += s * math.exp(-(((c - sc) / rc) ** 2 + ((r - sr) / rr) ** 2))
    return v


burn.noise = Noise(SEED + 1, 2.0)


def materials():
    m = live.materials()
    m["char"] = m["grey"][0x01]
    pal = k.level_palette()
    for key, (index, strength) in GLOWS.items():
        if key == "dim":
            continue
        m[key] = k.material("podw_seam_%s" % key, palette=index, metallic=0.0, roughness=0.5, emission=pal[index],
                            emission_strength=strength)
    m["dim"] = m["mid"]           # (at most 15 materials a piece: the dim seams the mid ones' material)
    return m


def build_whole(m):
    parts = live.build_whole(m)
    # the dock's clamps and vents blown away (the painting's dock is a black bay with red lines across it)
    for obj in [o for o in parts if o.name.startswith(GONE)]:
        parts.remove(obj)
        bpy.data.objects.remove(obj)
    cutter = mk.prism("hollow", ccw(jagged(HOLLOW, SEED * 0.1, 0.55, 0.6)), HOLLOW_FLOOR, H + 30.0, m["char"])
    lo, hi = mk.bounds([cutter])
    # (only the parts the hollow reaches go through the boolean: the rest keep their own meshes and shading)
    hit = [o for o in parts if (lambda a, b: a.x < hi.x and b.x > lo.x and a.y < hi.y and b.y > lo.y and
                                b.z > lo.z)(*mk.bounds([o]))]
    parts = [o for o in parts if o not in hit] + break_with(hit, cutter)
    dock = ("dock", "vent", "sill")
    for obj in parts:
        if obj in hit or obj.name.startswith(("dock", "vent", "sill", "pod")):
            scorch(obj, burn, LEVELS, step=1.0 if obj.name.startswith(("pod_body", "pod_frame", "dock_floor")) else None)
        if obj.name.startswith(("dock_floor", "dock_clamp", "vent")):
            # the bay, its clamps and vents burnt black (the painting's 0x01-0x02)
            mk.paint(obj, lambda c, n: m["grey"][0x01] if n.z > 0.3 else m["grey"][0x03])
        if obj in hit:
            k.smooth(obj, 35)
    # The red-hot seams, laid where the camera sees them.
    for i, (points, dz, radius, glow) in enumerate(SEAMS):
        z = H + dz
        pts = []
        for c, r in points:
            x, yv = E(c, r)
            pts.append((x, yv - S(z + radius), z, radius))
        bar = bent_bar(f"seam{i}", pts, radius, m[glow])
        hotter = {"dim": "mid", "mid": "hot", "hot": "hot"}[glow]
        mk.paint(bar, lambda c, n, h=hotter: m[h] if n.z > 0.8 else None)
    for i, (outline, z, thick, tilt) in enumerate(PLATES):
        plate = shard(f"torn{i}", [(x, y - S(z)) for x, y in outline], z, thick, m["grey"][0x07], tilt)
        live.paint_lit(plate, m["grey"][0x07], m["grey"][0x0a], m["grey"][0x04], under=m["grey"][0x02])
    rng = random.Random(SEED)
    for i, (x, y, size, kind) in enumerate(LUMPS):
        mat = {"char": m["grey"][0x01], "dark": m["grey"][0x03], "ember": m["dim"]}[kind]
        z = HOLLOW_FLOOR - 0.2
        rock(f"lump{i}", (x, y - S(z), z), (size, size * rng.uniform(0.6, 0.9), size * 0.5), mat, 5.0 + 1.1 * i,
             flat=HOLLOW_FLOOR - 0.3)
    for i, (x, y, size, kind) in enumerate(DOCK_LUMPS):
        mat = {"char": m["grey"][0x01], "dark": m["grey"][0x03]}[kind]
        z = H
        rock(f"dock_lump{i}", (x, y - S(z), z), (size, size * rng.uniform(0.6, 0.9), size * 0.45), mat, 9.0 + 1.3 * i,
             flat=H - 0.2)
    whole = mk.meshes()
    for obj in whole:
        mk.apply(obj)
    bpy.context.view_layer.update()
    return whole


def build():
    options = k.args()
    only = options["only"].split(",") if "only" in options else None
    k.reset()
    bpy.context.scene.view_settings.view_transform = "Standard"
    m = materials()
    whole = build_whole(m)
    triangulate(whole)
    print("whole cargo pod wreck: %d triangles, %d objects" % (mk.triangles(whole), len(whole)))
    if "whole" in options:
        mk.export(whole, options["whole"] + "cargo_pod_lower_wreck.glb")
    cap = m["grey"][0x03]
    for name, sprite, box, centre in WRECK_PIECES:
        if only and name not in only:
            continue
        parts = [p for p in (view_cut(src, box, cap, H) for src in whole) if p is not None]
        mk.transform(parts, Matrix.Translation((-centre[0], -centre[1], 0.0)))
        bpy.context.view_layer.update()
        for src in whole:
            src.hide_render = True
        live.export(parts, name, options)
        for src in whole:
            src.hide_render = False


if __name__ == "__main__":
    build()
