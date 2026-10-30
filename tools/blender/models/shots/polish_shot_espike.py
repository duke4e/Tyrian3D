"""The enemies' green drop (shots sheet sprites 117 and 118 above 136 and 137, all 1x1: 12 x 14 cells), modelled
(2026-10-29, round 2 of the energy shots' models; until then each piece was drawn as its sprite with volume, flat, from
the 4x sheets, with the automatic glow).

Who fires it: enemy weapon 154 (27 enemy types: DELI's, New Deli's and HARVEST's turrets (T 401-411), AST ROCK's,
HARVEST's and NOSE DRIP's craft once fire override events give them a frequency) and 136 (FLEET's and UNDERDELI's), in
episodes 1-5. Each fires two shots at once that fall together down the screen at 6 pixels a frame: 117 fourteen
pixels above 136 (weapon 154: by -14 and 0; 136: 0 and 14), so the two sprites draw one drop 12 pixels wide and 27
high. Both animate (weapani 2: 117 and 118, 136 and 137 by turns, a game frame each, in step since the two shots are
made together); the second frames are the first one or two shades lighter.

As the sprites draw it (ramp 12, the greens): 117 the drop's upper part, a cone pointing up the screen (from 3 pixels
across at its tip, row 1, to the cell's whole width at row 13; its axis a quarter of a pixel left of the cell's
middle); 136 its lower part, the whole width down to row 10, its bottom rounded off in three rows. A glossy drop of
green plasma: its body dark green at its edges (0xc0-0xc2), green inside (0xc4-0xc9); a bright streak down its left
side (columns 3-4: 0xcf, pale green), from the cone's middle down to the lower part's row 8; another down its right
side (column 9: 0xcc) that curves round the bottom (rows 9-11) to the left: together a U of light, its left arm the
brighter and the longer (the sprites' "arc").

The model: the drop built whole, then cut at the sprites' border into the two pieces (polish_machine_kit.cut, each
moved so that its sprite's centre is its origin; models.cfg draws them at their origin, so they meet again as the
comet's pieces do). The body: polish_shot_pellet.py's bead with the drop's outline (round on top and flat underneath,
as high all along its middle and rounding off at its edges, leant towards the camera so that the camera sees it laid
out as the sprites draw it), in bands of ramp 12 by a heat that falls from its middle to its edges and is lower up
the cone. On it the U of light: a filament of green plasma lying on the body (a half-tube draped over its surface,
standing 0.5 pixels proud), down the left side from the cone, round the bottom and up the right side, pale green
(0xce) down its left arm and green (0xcc) round the bottom and up the right, fading into the body's green at its
ends. The second frames are the same meshes with every band a shade lighter (frame models). Every band glows in its
own colour, more the brighter (0.2-0.48 the body, 0.56-0.62 the filament). The upper piece 262 triangles, the lower
1 150, 7 materials each (the cuts closed in the body's middle green, already one of them).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; each piece's
origin at its sprite's centre (pixel 6, 7 of its cell: column c is x = c + 0.5 - 6, row r is y = 6.5 - r); built
whole round 136's centre (117's 14 pixels up), on z = 0.

models.cfg (the shots section; origin: drawn at their own origin, so that the pieces meet):
    model shot_espike_117 shots/shot_espike_117.glb origin   (and _118, _136, _137, each with origin)
    shot shots 117 shot_espike_117 glow=12:0.35:201:-0.3:4    # the drop's cone (first frame)
    shot shots 118 shot_espike_118 glow=12:0.35:201:-0.3:4    # a shade lighter (second frame)
    shot shots 136 shot_espike_136 glow=16:0.5:204:0.8:1.5    # its lower part with the U of light (first frame)
    shot shots 137 shot_espike_137 glow=16:0.5:204:0.8:1.5    # a shade lighter (second frame)

Run: Blender -b --factory-startup -P tools/blender/models/shots/polish_shot_espike.py -- [--only <name,...>]
     [--outdir <dir>] (default assets/models/shots) [--check <sheets dir>] [--preview <prefix>]
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from polish_shot_pellet import Bead, body, materials, run  # noqa: E402
from polish_shot_eminor import polygon_radius  # noqa: E402
from polish_shot_pulse import mesh_from_rings  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_flame_drop import monotone  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
import tyrkit as k  # noqa: E402

PIECE = 14.0  # 117's centre above 136's
CUT = 7.0  # the sprites' border (y, round 136's centre)

# The drop's outline (both sprites' rows smoothed, round 136's centre) and the middle its rings are built round.
OUTLINE = [(0.0, -7.0), (2.4, -6.8), (4.2, -5.9), (5.4, -4.6), (6.0, -3.0), (6.0, 7.5), (5.5, 9.5), (5.0, 11.5),
           (4.4, 13.5), (3.6, 15.5), (2.8, 17.0), (1.7, 18.6), (0.4, 19.8), (-0.6, 20.0), (-1.6, 19.6),
           (-2.4, 18.4), (-3.2, 16.8), (-4.0, 15.0), (-4.7, 13.0), (-5.3, 11.0), (-5.8, 9.0), (-6.0, 7.0),
           (-6.0, -3.0), (-5.4, -4.6), (-4.2, -5.9), (-2.4, -6.8)]
MIDDLE = (0.0, 2.5)
HEIGHT, DEPTH = 3.6, 0.75  # (the body's height at most, and over its half-width)
# The body's heat: from its middle out to the outline (u), highest towards the bottom and the sides and lower up the
# cone (PEAK by the angle's sine: down, across, up).
PEAK = (9.0, 9.0, 6.6)
FALL = ((0.0, 1.0), (0.45, 0.93), (0.7, 0.72), (0.88, 0.4), (1.0, 0.12))
# Each frame's body bands ((lowest heat, palette index, emission), the rim first) and the filament's ((palette index,
# emission): its arms' and bottom's, its left arm's hottest).
BANDS = {
    1: [(-99.0, 0xc1, 0.2), (2.2, 0xc3, 0.26), (4.0, 0xc5, 0.31), (5.8, 0xc7, 0.38), (7.6, 0xc9, 0.45)],
    2: [(-99.0, 0xc2, 0.22), (2.2, 0xc4, 0.28), (4.0, 0xc6, 0.34), (5.8, 0xc8, 0.42), (7.6, 0xca, 0.48)],
}
FILAMENT_BANDS = {1: ((0xcc, 0.56), (0xce, 0.6)), 2: ((0xcd, 0.58), (0xcf, 0.62))}
FIRE_ROUGHNESS, FILAMENT_ROUGHNESS = 0.5, 0.4
# The filament: its path (round 136's centre: down the left arm, round the bottom, up the right arm), each point with
# the filament's radius there and its band (0 the body's brightest, fading into it; 1 the filament's; 2 its hottest,
# down the left arm), rounded off (Chaikin) so that it bends smoothly; its ends taper to points.
PATH = [(-2.3, 15.2, 0.0, 0), (-2.2, 13.0, 0.55, 2), (-2.05, 10.5, 0.85, 2), (-2.0, 8.0, 0.95, 2), (-2.0, 5.5, 0.95, 2),
        (-2.0, 3.0, 0.95, 2), (-2.05, 0.8, 0.9, 2), (-2.0, -1.2, 0.8, 1), (-1.6, -2.8, 0.72, 1), (-0.6, -4.0, 0.68, 1),
        (0.8, -4.5, 0.66, 1), (2.2, -4.0, 0.66, 1), (3.2, -2.8, 0.66, 1), (3.6, -1.2, 0.66, 1), (3.65, 1.0, 0.66, 1),
        (3.6, 3.5, 0.64, 1), (3.5, 6.0, 0.6, 1), (3.3, 8.2, 0.5, 0), (3.0, 10.0, 0.0, 0)]
SECTION = 5  # points round the half-tube
FILAMENT_DEPTH, FILAMENT_SINK = 0.75, 0.3


def half_widths(outline, step=0.05):
    """The outline's middle and half-width across it at each y (every step pixels; Chaikin-smoothed as
    polygon_radius smooths it), as a function y -> (middle, half-width)."""
    smooth = mk.chaikin(outline, 2, closed=True)
    low, high = min(p[1] for p in smooth), max(p[1] for p in smooth)
    table = []
    y = low
    while y <= high + 1e-9:
        xs = []
        for (ax, ay), (bx, by) in zip(smooth, smooth[1:] + smooth[:1]):
            if (ay - y) * (by - y) <= 0 and ay != by:
                xs.append(ax + (bx - ax) * (y - ay) / (by - ay))
        table.append((y, (min(xs) + max(xs)) / 2, (max(xs) - min(xs)) / 2) if xs else (y, 0.0, 0.0))
        y += step

    def at(y):
        i = min(max(int((y - low) / step), 0), len(table) - 2)
        f = min(max((y - table[i][0]) / step, 0.0), 1.0)
        return (table[i][1] + (table[i + 1][1] - table[i][1]) * f, table[i][2] + (table[i + 1][2] - table[i][2]) * f)
    return at


def drop(frame):
    radius = polygon_radius(OUTLINE, MIDDLE)
    fall = monotone([p[0] for p in FALL], [p[1] for p in FALL])
    across = half_widths(OUTLINE)

    def height(p):
        """Round across the drop (a half-ellipse over its width at that y), as high as DEPTH of its half-width but
        HEIGHT at most."""
        middle, w = across(p[1])
        if w <= 1e-6:
            return 0.0
        u = min(abs(p[0] - middle) / w, 1.0)
        return min(HEIGHT, DEPTH * w) * math.sqrt(max(0.0, 1.0 - u * u))

    def heat(u, angle):
        s = math.sin(angle)  # (-1 down, 1 up)
        peak = PEAK[1] + (PEAK[0] - PEAK[1]) * max(-s, 0.0) + (PEAK[2] - PEAK[1]) * max(s, 0.0) ** 1.5
        return peak * fall(u)
    return Bead(*MIDDLE, radius, HEIGHT, heat, BANDS[frame], None, flames=(7, 0.025, 1.9, 0.0), segments=40,
                head_rings=(0.35, 0.7), rim_rings=(0.93, 0.975, 1.0), height_fn=height)


def filament(name, bead, mats, under):
    """The U of light: a half-tube along PATH draped over the body (its sides sunk into it, its crest FILAMENT_DEPTH
    times its radius proud of it), its ends tapering to points; mats: the body's brightest band, then the filament's
    two."""
    path = mk.chaikin(PATH, 1, closed=False)
    rings = []
    for i in range(1, len(path) - 1):
        x, y, r, _ = path[i]
        tx, ty = path[i + 1][0] - path[i - 1][0], path[i + 1][1] - path[i - 1][1]
        length = math.hypot(tx, ty)
        nx, ny = ty / length, -tx / length  # (to the path's right)
        ring = []
        for j in range(SECTION + 1):
            a = math.pi * j / SECTION
            px, py = x + nx * r * math.cos(a), y + ny * r * math.cos(a)
            z = bead.height_at((px, py)) - FILAMENT_SINK + (FILAMENT_SINK + r * FILAMENT_DEPTH) * math.sin(a)
            ring.append(Vector((px, py - bead.lean * z, z)))
        rings.append(ring)
    tips = []
    for x, y, _, _ in (path[0], path[-1]):
        z = bead.height_at((x, y)) - FILAMENT_SINK
        tips.append((x, y - bead.lean * z, z))
    # the band of each stretch: its middle's (rounded); faces between ring i and i + 1 (the path's points i + 1 and
    # i + 2), then the first and the last fans
    band = [int(round((path[i][3] + path[i + 1][3]) / 2)) for i in range(len(path) - 1)]
    bands = band[1:-1] + [band[0], band[-1]]
    obj = mesh_from_rings(name, rings, bands, tips, mats, under)
    return k.smooth(obj, 80)


def whole(name, frame):
    """The whole drop (round 136's centre): its body and its filament; the materials (the body's, then the
    filament's two)."""
    spec = drop(frame)
    fire = materials("espike_body", spec.bands, FIRE_ROUGHNESS)
    light = [k_lit for k_lit in materials("espike_light", [(0, i, g) for i, g in FILAMENT_BANDS[frame]],
                                          FILAMENT_ROUGHNESS)]
    parts = [body(name + "_body", spec, fire), filament(name + "_light", spec, [fire[-1]] + light, 0)]
    return parts, fire


def pieces(name, frame, top):
    """One piece of the drop: the part above the sprites' border (top: 117/118, moved down to its own centre) or below
    it (136/137); the cuts closed in the body's middle green."""
    parts, fire = whole(name + "_whole", frame)
    box = (-20.0, 20.0, CUT, 40.0) if top else (-20.0, 20.0, -40.0, CUT)
    out = []
    for p in parts:
        piece = mk.cut(p, box, fire[2])
        if piece is not None:
            piece.name = p.name.replace("_whole", "")
            out.append(piece)
    for p in parts:
        mesh = p.data
        bpy.data.objects.remove(p)
        bpy.data.meshes.remove(mesh)
    if top:
        mk.transform(out, Matrix.Translation((0.0, -PIECE, 0.0)))
    return out


MODELS = [
    ("shot_espike_117", 117, "the drop's upper part, a cone (the first frame)", 1, True),
    ("shot_espike_118", 118, "the drop's upper part a shade lighter (the second frame)", 2, True),
    ("shot_espike_136", 136, "the drop's lower part with the U of light (the first frame)", 1, False),
    ("shot_espike_137", 137, "the drop's lower part a shade lighter (the second frame)", 2, False),
]


def build_model(name, sprite, frame, top):
    return triangulate(pieces(name, frame, top))


if __name__ == "__main__":
    run(MODELS, build_model)
