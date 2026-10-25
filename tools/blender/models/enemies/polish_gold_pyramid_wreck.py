"""What is left of TYRIAN's golden pyramid machine once it is destroyed (stage 4 of the clean ground: the wreck models
that stand in for the map's painting of it; sheet 2 sprites 81 beside 83 above 119 beside 121), built on
polish_gold_machines.py (2026-10-25). models.cfg: model gold_pyramid_tl_wreck / _tr_wreck / _bl_wreck / _br_wreck
enemies/gold_pyramid_*_wreck.glb origin; wreck 2 81 gold_pyramid_tl_wreck, wreck 2 83 gold_pyramid_tr_wreck, wreck 2
119 gold_pyramid_bl_wreck, wreck 2 121 gold_pyramid_br_wreck. The game draws them where the map paints the wreck
(TYRIAN's three machines, at 660, 7463; 660, 7771; 540, 7995: the painting lies where the sprites do), with the live
sprite lines' options (yaw=0 height=-4), at the live pieces' places.

The painting (the same at the three places; at 1x and in the HD tiles; columns and rows of the 48 x 56 picture): the
machine as the live sprites draw it, burnt on its right: the capsule's rounded top still lit steel, but blackened at
its upper left edge (columns 9-14 of rows 8-12) and holed at its upper right (a black hole, columns 21-28 of rows
3-11); the golden pyramid's left face standing, dimmer, its ridge and its point a gold chevron, its right face blown
out (black, columns 22-30 of rows 13-24) down into the capsule; the narrow faces along its lower edges and the rod
under its front point left; the horns, dim gold, on both sides; the right leg black with a few steel ribs left
(columns 22-31 of rows 29-46), the left one lit steel, sooted at its foot; a black ring of soot round the whole (the
ground's: left to the 3D terrain).

The model: the live machine (polish_gold_machines.capsule(), pyramid(), horns(): the capsule and its panels, the
pyramid, its rod and collar, the four horns; its materials), then broken: the pyramid's right face blown out and the
capsule under it holed (an exact boolean with a jagged prism, its walls and floor soot), the left face's middle
broken out down to the capsule's top (its edges left: the painting's gold chevron), a hole torn into the capsule's
top right; the steel and the gold scorched by a field strongest round the holes, along the capsule's right
side, its right leg and its upper left edge (polish_jaw_gun_wreck.scorch: faces cut along the field's contours, their
shades three darker or burnt to the brown-black 0x10); the blown-out face's gold in shards (one standing tilted in the
hole, two on the dirt to the right), lumps of steel in the holes, a few embers among them glowing faintly in the gold
(0x1c, emission 0.25). Cut along the sprites' edges as the live machine (polish_savara_boss.cut), each piece moved so
that its sprite's centre is its origin.

Coordinates as polish_gold_machines.py's: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the dirt;
P(c, r) turns a pixel edge of the picture (column c, row r) into the whole's coordinates (x = c - 24, y = 28 - r).

Options after "--": --outdir <dir> (default assets/models/enemies), --preview <prefix>, --whole <prefix> (the uncut
wreck too), --only <model,...>.
"""
import math
import os
import random
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_deli_boss import join  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_savara_boss import cut  # noqa: E402
from polish_jaw_gun_wreck import scorch, jagged, ccw, shard  # noqa: E402
from polish_pyramid_wreck import break_with, chunk, emissive, Noise  # noqa: E402
import polish_gold_machines as live  # noqa: E402

P = live.P
SEED = 81
# The holes (columns, rows of the picture: outlines before roughening), their floors' height.
FACE_HOLE = [(21.2, 12.4), (23.6, 13.4), (26.4, 15.4), (29.6, 17.8), (32.6, 20.6), (35.4, 23.6), (36.6, 26.8),
             (34.0, 28.2), (30.0, 28.6), (26.0, 28.9), (22.4, 29.0), (21.4, 27.0), (21.1, 23.0), (21.0, 18.0)]
# The left face's middle broken out, its edges left (the painting's gold chevron), down to the capsule's top.
LEFT_HOLE = [(19.3, 15.6), (17.0, 18.6), (13.6, 22.0), (10.4, 25.4), (12.2, 26.6), (15.6, 26.4), (19.2, 26.8),
             (19.6, 22.6)]
TOP_HOLE = [(21.8, 3.8), (24.0, 3.3), (26.6, 4.3), (28.3, 6.0), (28.6, 8.4), (27.5, 10.4), (25.4, 11.2),
            (23.1, 10.7), (21.7, 9.0), (21.2, 6.4)]
FLOORS = (live.HC - 2.2, live.HC - 2.0, live.HC - 0.25)
# The scorch: spots (column, row, radii in columns and rows, strength) and the noise over them; its levels (three
# shades darker, then the brown-black soot).
SPOTS = [(26.0, 20.0, 7.0, 8.5, 1.2), (25.0, 7.2, 5.0, 5.0, 1.1), (11.8, 10.0, 3.2, 3.0, 0.9),
         (26.5, 38.0, 5.5, 10.0, 1.1), (30.5, 26.0, 3.0, 6.0, 0.8), (12.5, 42.0, 3.5, 4.5, 0.7),
         (20.5, 44.0, 6.0, 2.5, 0.6), (29.0, 28.0, 4.0, 18.0, 0.7), (14.5, 20.0, 4.0, 5.0, 0.5),
         (6.5, 16.0, 3.5, 7.0, 0.32), (34.5, 16.5, 3.5, 7.0, 0.42)]   # (the last two: the horns, dimmed)
BURN_BASE, BURN_NOISE, LEVELS = 0.3, 0.22, (0.5, 0.92)
# The blown-out face's shards: (outline (columns, rows), z, thickness, tilt (degrees about x and y)); the steel
# lumps and the embers in the holes (column, row, size, which hole's floor).
SHARDS = [([(24.0, 17.6), (27.4, 18.6), (26.6, 21.8), (23.6, 21.0)], FLOORS[0] + 0.6, 0.35, (34.0, -26.0)),
          ([(28.6, 22.4), (31.6, 23.8), (30.4, 26.4), (28.0, 25.4)], FLOORS[0] + 0.5, 0.3, (-22.0, 30.0)),
          ([(14.4, 22.6), (16.8, 22.0), (16.6, 24.6), (14.6, 24.8)], live.HC + 0.1, 0.3, (12.0, -18.0)),
          ([(36.0, 22.6), (39.4, 23.2), (38.6, 25.4), (35.6, 24.8)], 0.0, 0.3, (6.0, 10.0)),
          ([(34.4, 27.6), (36.8, 27.2), (37.2, 29.4), (34.8, 29.8)], 0.0, 0.3, (-8.0, 4.0)),
          ([(4.0, 31.0), (6.0, 30.4), (6.4, 32.2), (4.6, 32.6)], 0.0, 0.25, (4.0, -6.0))]
LUMPS = [(24.6, 22.4, 1.6, 0), (27.6, 20.2, 1.3, 0), (23.0, 15.6, 1.1, 0), (25.2, 6.6, 1.3, 1), (23.4, 9.2, 1.0, 1),
         (33.0, 34.0, 1.2, None), (31.6, 45.0, 1.0, None)]
EMBERS = [(25.6, 19.4, 0.8, 0), (23.6, 23.2, 0.6, 0), (26.4, 8.0, 0.6, 1)]


def materials():
    m = live.materials()
    m["soot"] = k.material("soot", palette=0x10, metallic=0.3, roughness=0.72)   # (scorch()'s own soot)
    m["ember"] = emissive("goldw_ember", 0x1c, 0.25, 0.2, 0.4)
    return m


def burn(co):
    noise = burn.noise
    c, r = co.x + 24.0, 28.0 - co.y
    v = BURN_BASE + BURN_NOISE * noise.fbm(c, r, 2)
    for sc, sr, rc, rr, s in SPOTS:
        v += s * math.exp(-(((c - sc) / rc) ** 2 + ((r - sr) / rr) ** 2))
    return v


burn.noise = Noise(SEED + 1, 2.2)


def hole_cutter(name, outline, floor, seed, mat):
    pts = [P(c, r) for c, r in outline]
    return mk.prism(name, ccw(jagged(pts, seed, 0.5, 0.7)), floor, 30.0, mat)


def build_whole(m):
    parts = live.capsule(m) + live.pyramid(m) + live.horns(m)
    for obj in parts:
        mk.apply(obj)
    for i, (outline, floor) in enumerate(((FACE_HOLE, FLOORS[0]), (TOP_HOLE, FLOORS[1]), (LEFT_HOLE, FLOORS[2]))):
        parts = break_with(parts, hole_cutter(f"hole{i}", outline, floor, SEED + 3 * i, m["soot"]))
    for obj in parts:
        hard = obj.name.startswith(("capsule", "panel", "pyramid"))
        scorch(obj, burn, LEVELS, step=1.8 if hard else None)
        if hard:
            mk.shade(obj, 35)
        else:
            k.smooth(obj, 50)
    rng = random.Random(SEED)
    surface = mk.surface([o for o in parts if o.name.startswith(("capsule", "panel"))])

    def ground(c, r, hole):
        x, y = P(c, r)
        if hole is None:
            return Vector((x, y, 0.0))
        h = surface(x, y)
        return Vector((x, y, h[0].z if h else FLOORS[hole]))
    for i, (outline, z, thick, tilt) in enumerate(SHARDS):
        shard(f"face_shard{i}", [P(c, r) for c, r in outline], z, thick,
              (m["gold_dark"], m["gold"], m["gold_shade"], m["gold_shade"], m["gold"], m["gold_shade"])[i], tilt)
    for i, (c, r, size, hole) in enumerate(LUMPS):
        chunk(f"lump{i}", ground(c, r, hole) - Vector((0, 0, 0.3)), size, rng,
              (m["steel_dark"], m["steel_shade"], m["soot"], m["steel"])[i % 4], rng.uniform(0.5, 0.75))
    for i, (c, r, size, hole) in enumerate(EMBERS):
        chunk(f"ember{i}", ground(c, r, hole) - Vector((0, 0, 0.15)), size, rng, m["ember"], 0.6, 8)
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
    print("whole gold pyramid wreck: %d triangles, %d objects" % (mk.triangles(whole), len(whole)))
    if "whole" in options:
        mk.export(whole, options["whole"] + "gold_pyramid_wreck.glb")
    if "preview" in options:
        mk.preview(options["preview"] + "gold_pyramid_wreck_whole", whole, size=(48, 56), scale=8, distance=1.8)
    for suffix, box, _ in live.QUARTERS:
        model = f"gold_pyramid_{suffix}_wreck"
        if only and model not in only:
            continue
        parts = [p for p in (cut(src, box, m["steel_dark"]) for src in whole) if p is not None]
        mk.transform(parts, Matrix.Translation((-(box[0] + box[1]) / 2, -(box[2] + box[3]) / 2, 0.0)))
        triangulate(parts)
        piece = join(parts, model)
        bpy.context.view_layer.update()
        for src in whole:
            src.hide_render = True
        mk.report(model, [piece], os.path.join(out, model + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + model, [piece])
        bpy.data.objects.remove(piece)
        for src in whole:
            src.hide_render = False


if __name__ == "__main__":
    build()
