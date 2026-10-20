"""The flying crystal shards of GRYPHON, MISTAKES, STATION, GLACIER, REEF, MIGRATION and CRUSTGATE (sheet V
sprites 10, 12 and 50, 2x2: a 15 x 25 shard in the 24 x 28 cell; sky layer; enemies 792-794, 1061, 1062 and
1522-1526, about 685 of them; not animated), polished (2026-10-20; it replaces shard.py, a dull purple lump of
two six-sided cones). models.cfg: sprite v 10 shard yaw=0, sprite v 12 shard_12 yaw=0, sprite v 50 shard_50
yaw=0.

V 10 points up the screen (194 of them); V 12 points up and to the right (250): V 10 turned 45 degrees about
its own middle and redrawn (the silhouettes overlap 0.93 at 43-46 degrees, 0.91 at 40); V 50 (241) is V 12
mirrored, pixel for pixel (its light too). The game turns a model about the sprite's centre, which is half a
pixel left of the shard's axis and nearly two pixels above the point V 12 is turned about, so one model turned
by yaw lands 1.2 pixels (V 12) and 2 pixels (V 50) off the sprites (overlaps 0.82 and 0.68 at yaw 45 and -45).
So the same shard is written three times: shard as built (V 10), shard_12 turned TURN degrees clockwise about
PIVOT (its best fit to V 12: overlap 0.95) and shard_50, shard_12 mirrored (V 50).

As the sprite and its 4x upscale draw it: a pale lilac crystal (ramp 5, shades 0x58-0x5f; the outline 0x50)
pointing up: a long point (rows 1-18, widening a pixel every two rows to 15 pixels at row 14, its sides curving
in to the tip) with a white spine down its middle (column 12), a light ridge either side five pixels out
(columns 7 and 17) and darker facets beyond them; a dark groove across it (row 19, a pixel narrower: shade
0x58); below that a short blunt end (rows 20-25), brightest just under the groove.

Built as a gem cutter cuts a crystal: every cross-section the same octagon (a corner up at the camera: the
spine; corners at the sides: the outline; the corners between them: the side ridges, 0.71 of the half-width
out, as the sprite's columns 7 and 17), a little flatter than wide (ZS), its corners ground off into narrow
facets (the ridges); scaled along the shard so every facet is a plane: the prism of the body (rows 14-18),
a shoulder, the termination in two tiers to the tip; the groove an octagonal neck between flat steps; the blunt
end a bright band, two tiers and a small end facet. Flat shading: crisp facets. Each facet takes its palette
shade by the way it faces round the shard (the game's sun shades it further: the sprite's light, from the
upper left, is left to it, as the three sprites light the shard differently), the ridges the light ones, each
glowing a little in its own colour (a crystal lets light through: the game's slanted camera sees much of its
shaded side).

Origin at the sprite's centre (pixel 12, 14); +Y up the screen, +Z towards the camera (the game centres sky
models in height); the shard's axis along x = 0.5 (column 12), from its tip at y = 13 to its end at y = -12.

Replaces tools/blender/models/enemies/shard.py (it builds only the shard): delete it, so that it doesn't
overwrite this model.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each model's
silhouette against its sprite in enemy_V.png), --preview <prefix>, --only <name,...> (shard, shard_12,
shard_50).
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
from polish_balls import preview  # noqa: E402

AXIS_X = 0.5
ZS = 0.85            # the cross-section's height over its width
# The octagon's corners, counter-clockwise from the spine (degrees from +X towards +Z), and how much of the
# facets either side each ridge grinds off (a fraction of the facet's width each way).
CORNERS = [90.0, 135.0, 180.0, 225.0, 270.0, 315.0, 0.0, 45.0]
CHAMFER = {90.0: 0.085, 45.0: 0.06, 135.0: 0.06, 0.0: 0.05, 180.0: 0.05, 225.0: 0.04, 315.0: 0.04, 270.0: 0.04}

# The shard from its end up to its tip: (y, the octagon's half-width, the band from this ring to the next).
# The half-widths follow the sprite's outline (pixel edges, the outline pixels included) through the middles
# of its steps: the blunt end (rows 20-25), the groove (row 19: steps in and out at y = -6 and -5), the
# body (rows 14-18), the shoulder (rows 11-13) and the point (rows 1-10), blunter in its last two pixels.
RINGS = [
    (-12.0, 1.35, "culet_tier"),
    (-10.75, 3.7, "end_low"),
    (-8.35, 6.9, "end_band"),
    (-6.05, 7.5, "step"),
    (-6.05, 6.55, "groove"),
    (-4.95, 6.55, "step"),
    (-4.95, 7.5, "body"),
    (-0.6, 7.5, "shoulder"),
    (2.9, 6.15, "point"),
    (10.4, 2.25, "point_tip"),
]
TIP_Y = 13.0

# Palette shades (ramp 5) by band and by facet: the facets named by the way they face round the shard (top:
# either side of the spine; side: between the side ridges and the outline; low and under: beneath).
SHADES = {
    "point": {"top": 0x5c, "side": 0x5a, "low": 0x58, "under": 0x57},
    "end": {"top": 0x5b, "side": 0x5a, "low": 0x58, "under": 0x57},
    "end_band": {"top": 0x5d, "side": 0x5b, "low": 0x59, "under": 0x57},
}
RIDGES = {90.0: 0x5f, 45.0: 0x5e, 135.0: 0x5e, 0.0: 0x5c, 180.0: 0x5c, 225.0: 0x59, 315.0: 0x59, 270.0: 0x58}
END_RIDGES = {90.0: 0x5e, 45.0: 0x5d, 135.0: 0x5d, 0.0: 0x5b, 180.0: 0x5b, 225.0: 0x59, 315.0: 0x59, 270.0: 0x58}
GROOVE, CULET = 0x56, 0x5a
# How strongly each shade glows in its own colour: the lighter, the more.
GLOW = {0x56: 0.0, 0x57: 0.06, 0x58: 0.08, 0x59: 0.1, 0x5a: 0.12, 0x5b: 0.16, 0x5c: 0.2, 0x5d: 0.26, 0x5e: 0.4,
        0x5f: 0.6}


def materials():
    pal = k.level_palette()
    return {i: k.material(f"shard_{i:x}", palette=i, metallic=0.1, roughness=0.14 if i >= 0x5c else 0.2,
                          emission=pal[i] if GLOW[i] > 0 else None, emission_strength=GLOW[i])
            for i in GLOW}


def section():
    """The cross-section at half-width 1: [(x, z, kind, corner)] counter-clockwise from the spine, two points
    per corner (where its ridge's facet meets the facets either side); kind names the face from this point to
    the next: "ridge" (a corner's narrow facet) or "facet"."""
    corners = [Vector((math.cos(math.radians(a)), ZS * math.sin(math.radians(a)))) for a in CORNERS]
    points = []
    for i, a in enumerate(CORNERS):
        c, prev, nxt = corners[i], corners[i - 1], corners[(i + 1) % len(corners)]
        t = CHAMFER[a]
        p0, p1 = c + (prev - c) * t, c + (nxt - c) * t
        points.append((p0.x, p0.y, "ridge", a))
        points.append((p1.x, p1.y, "facet", a))
    return points


def facet_kind(a0, a1):
    """The facet between the corners at a0 and a1 (degrees): top, side, low or under."""
    mid = math.radians((a0 + a1) / 2 if abs(a1 - a0) < 180 else (a0 + a1 + 360) / 2)
    s = math.sin(mid)
    return "top" if s > 0.6 else "side" if s > 0 else "low" if s > -0.6 else "under"


def shade_of(band, kind, corner, next_corner):
    if band in ("groove", "step"):
        return GROOVE
    if band == "culet_tier":
        group = "end"
    elif band == "end_band":
        group = "end_band"
    elif band.startswith("end"):
        group = "end"
    else:
        group = "point"
    if kind == "ridge":
        return (END_RIDGES if group.startswith("end") else RIDGES)[corner]
    return SHADES[group][facet_kind(corner, next_corner)]


def shard(m):
    sec = section()
    n = len(sec)
    verts, faces, shades = [], [], []
    for y, r, _ in RINGS:
        verts += [(AXIS_X + r * x, y, r * z) for x, z, _, _ in sec]
    for i, (_, _, band) in enumerate(RINGS[:-1]):
        for j in range(n):
            a, b = i * n + j, i * n + (j + 1) % n
            faces.append((a, b, b + n, a + n))
            x, z, kind, corner = sec[j]
            shades.append(shade_of(band, kind, corner, sec[(j + 1) % n][3]))
    # The point: from the last ring to the tip.
    last = (len(RINGS) - 1) * n
    tip = len(verts)
    verts.append((AXIS_X, TIP_Y, 0.0))
    for j in range(n):
        faces.append((last + j, last + (j + 1) % n, tip))
        x, z, kind, corner = sec[j]
        shades.append(shade_of("point", kind, corner, sec[(j + 1) % n][3]))
    # The end facet (flat, facing down the screen).
    faces.append(tuple(reversed(range(n))))
    shades.append(CULET)
    obj = k.mesh_object("shard", verts, faces)
    used = sorted(set(shades))
    for i in used:
        obj.data.materials.append(m[i])
    for poly, s in zip(obj.data.polygons, shades):
        poly.material_index = used.index(s)
        poly.use_smooth = False
    k.recalc_normals(obj)
    return obj


def triangles():
    return sum(len(p.vertices) - 2 for o in bpy.context.scene.objects if o.type == "MESH" for p in o.data.polygons)


# The turned copies: (name, sprite, mirrored); shard_12 turned TURN degrees clockwise about PIVOT.
MODELS = [("shard", 10, None), ("shard_12", 12, False), ("shard_50", 50, True)]
TURN, PIVOT = 44.0, (0.5, -1.75)


def turned(mirrored):
    """The transform from the shard as built to a turned copy (None: as built)."""
    if mirrored is None:
        return Matrix.Identity(4)
    m = Matrix.Translation((*PIVOT, 0.0)) @ Matrix.Rotation(math.radians(-TURN), 4, "Z") @ \
        Matrix.Translation((-PIVOT[0], -PIVOT[1], 0.0))
    if mirrored:
        m = Matrix.Scale(-1, 4, (1, 0, 0)) @ m
    return m


def build():
    options = k.args()
    outdir = options.get("outdir", os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "enemies"))
    only = set(options["only"].split(",")) if "only" in options else None
    for name, sprite, mirrored in MODELS:
        if only is not None and name not in only:
            continue
        k.reset()
        obj = shard(materials())
        m = turned(mirrored)
        obj.data.transform(m)
        if m.determinant() < 0:
            obj.data.flip_normals()
        obj.data.update()
        used = sorted({mat.name for mat in obj.data.materials})
        print("== %s (V %d): %d triangles, %d materials: %s" % (name, sprite, triangles(), len(used),
                                                             ", ".join(used)))
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        path = os.path.join(outdir, name + ".glb")
        k.export(path)
        print("%s: %d bytes" % (path, os.path.getsize(path)))
        if "check" in options:
            k.check_silhouette(os.path.join(options["check"], "enemy_V.png"), sprite)
        if "preview" in options:
            preview(options["preview"] + name, distance=0.7)


if __name__ == "__main__":
    build()
