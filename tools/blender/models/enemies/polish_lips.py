"""EYESPY's and GLACIER's big red lips (sheet ^, x5e in models.cfg), polished (2026-10-21; it replaces wave3_i.py's
lips(), two lips raised from the pixels, the right half the left one mirrored). Two 2x2 sprites, each an enemy of its
own (342 and 343, one frame each, sky enemies), which the levels always place side by side as one 48 x 28 mouth: 196
at x and 208 at x + 24, the same link, coming down the screen (EYESPY's events 20-1150, 25 pairs; episode 6's GLACIER
takes five of EYESPY's waves). models.cfg: model eyespy_lips_left enemies/eyespy_lips_left.glb origin, model
eyespy_lips_right enemies/eyespy_lips_right.glb origin (origin: drawn at their own origins the halves meet); sprite
x5e 196 eyespy_lips_left yaw=0, sprite x5e 208 eyespy_lips_right yaw=0.

The two sprites are not each other's mirror image (the mouth is lit from the left, and it is symmetric about the
middle of the picture's column 24, not about the sprites' edge between columns 23 and 24): the mouth is built whole
and cut along that edge. As the sprites and their 4x upscales draw it (the picture's columns c 0-47, rows r 0-27):
- The upper lip (rows 4-13): from the corners (columns 2 and 46, row 12) up to a Cupid's bow (two peaks at columns
  16-19 and 29-32, row 4, the dip between them at row 6), its lower edge the parting line, which waves: low by the
  corners (row 14), up under the peaks (row 12), down again in the middle, where the lip's tubercle hangs (row 13).
  Lit on its upper slope (shades 6-8 of the red ramp), darker on its lower slope down to the parting (4-5).
- The lower lip (rows 13-20): fuller, its bottom edge a long curve (row 20 in the middle), lit on its upper slope (8-b,
  a glossy highlight on its left part), darker towards its bottom edge.
- A dark outline round the mouth and along the parting (palette 0x10).

Built as one surface over the mouth's plan: across it from the lower lip's bottom edge to the upper lip's top edge
(through the parting) and along it between the corners, each lip a smooth bulge (its crest a little nearer the
parting on the upper lip, nearer the middle on the lower one), the two meeting in a crease at the parting; the plan's
curves (the top edge, the parting, the bottom edge) are the sprites' pixel edges, smoothed; a skirt down to the layer
round the edge and a flat underside close it. The heights fall towards the corners. Colours are the sprites' red
ramp in bands of how much the surface faces the light from the upper left and above (polish_orb_red.band_split; the
game's sun is there too): 0x42 0x43 0x44 0x45 0x46 0x47 and 0x49 on the most lit, glossy, with a faint emission in
their own reds (0.08: a bulge reads dark from the slanted camera); the crease, the outer edge and the cut caps dark
(0x41). The mouth is then cut along the
sprites' edge (polish_savara_boss.cut, the cut capped: it stands edge-on to the game's camera) into the two halves,
each moved so that its sprite's centre is its origin. Every mesh is triangulated before the export.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up (towards the camera) from the
layer; the whole's origin is the picture's middle (pixel edge 24, 14): column c's left edge is x = c - 24, row r's
top edge y = 14 - r. Built about X = 0 (the middle of column 24) and moved there (AXIS_X).

Replaces wave3_i.py's lips() and its two model registrations (eyespy_lips_left, eyespy_lips_right), their line in its
docstring, and wave3_i_art.py's LIPS and LIPS_R (only lips() reads LIPS; LIPS_R is read by nothing), so that they
don't overwrite these models.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes of the mouth
and of each half against enemy_x5e.png), --preview <prefix> (the mouth's and each half's top and 3/4 views),
--only <model,...>, --whole <file.glb> (the uncut mouth as well).
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
import polish_deli_boss as db  # noqa: E402  (join, drop_unused)
from polish_k_pod import triangulate  # noqa: E402
from polish_orb_red import band_split  # noqa: E402
from polish_savara_boss import cut  # noqa: E402  (polish_arch.cut keeping the faces' winding)

AXIS_X = 0.5                 # the middle of column 24, where the built mouth's X = 0 goes
LIGHT = Vector((-0.42, 0.5, 0.76)).normalized()     # the light the colours are banded by: the upper left and above
# The halves: model, sprite, the columns of the whole they keep (x0, x1).
PIECES = [("eyespy_lips_left", 196, (-24.0, 0.0)), ("eyespy_lips_right", 208, (0.0, 24.0))]

# The plan, from the corner (X -22.6) to the middle (the other half mirrored), in the built frame (X = x - 0.5):
# the upper lip's top edge, the parting line (the middle of the dark line) and the lower lip's bottom edge.
CORNER = (-22.6, 1.45)
TOP = [(-22.6, 1.45), (-21.6, 1.9), (-19.6, 2.2), (-17.6, 3.0), (-16.0, 4.0), (-15.0, 5.0), (-14.0, 6.0), (-13.0, 7.0),
       (-11.5, 8.0), (-9.5, 9.0), (-6.6, 9.95), (-4.5, 9.65), (-3.3, 8.9), (-2.0, 8.15), (0.0, 7.9)]
PARTING = [(-22.6, 1.45), (-21.0, 0.75), (-19.4, -0.15), (-16.5, -0.5), (-14.4, -0.4), (-12.5, 0.45), (-10.6, 1.35),
           (-7.5, 1.6), (-5.0, 1.3), (-3.6, 0.55), (-2.1, -0.35), (0.0, -0.5)]
BOTTOM = [(-22.6, 1.45), (-22.0, 0.95), (-20.5, 0.0), (-19.0, -1.0), (-17.5, -2.0), (-16.0, -3.0), (-15.0, -4.0),
          (-14.0, -5.0), (-12.5, -6.0), (-10.5, -7.0), (-8.0, -7.8), (-5.0, -8.0), (0.0, -8.05)]
# Heights: (|X|, the upper lip's crest, the lower lip's crest, the crease at the parting, the edge before the skirt).
HEIGHTS = [(0.0, 4.0, 6.3, 1.5, 0.55), (4.0, 4.25, 6.2, 1.55, 0.55), (8.0, 4.2, 5.8, 1.5, 0.55),
           (12.0, 3.6, 4.8, 1.3, 0.5), (16.0, 2.6, 2.9, 0.95, 0.45), (19.5, 1.45, 1.35, 0.6, 0.4),
           (22.6, 0.35, 0.35, 0.3, 0.3)]
CREST_U, CREST_L = 0.42, 0.55     # where across each lip its crest is (0 at the parting, 1 at its outer edge)
SKIRT = 0.25                     # how far out the skirt's foot is


def curve(points, x):
    """The value at |x| of a piecewise smooth curve through points (sorted by x, given for x <= 0)."""
    x = -abs(x)
    pts = points
    if x <= pts[0][0]:
        return pts[0][1]
    for i in range(len(pts) - 1):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        if x0 <= x <= x1:
            t = (x - x0) / (x1 - x0)
            p0 = pts[max(i - 1, 0)][1]
            p3 = pts[min(i + 2, len(pts) - 1)][1]
            # Catmull-Rom between y0 and y1 (uneven spacing is close enough here)
            return 0.5 * (2 * y0 + (-p0 + y1) * t + (2 * p0 - 5 * y0 + 4 * y1 - p3) * t * t +
                          (-p0 + 3 * y0 - 3 * y1 + p3) * t ** 3)
    return pts[-1][1]


def heights(x):
    a = min(abs(x), HEIGHTS[-1][0])
    for i in range(len(HEIGHTS) - 1):
        h0, h1 = HEIGHTS[i], HEIGHTS[i + 1]
        if h0[0] <= a <= h1[0]:
            t = mk.smoothstep(h0[0], h1[0], a)
            return [u + (v - u) * t for u, v in zip(h0[1:], h1[1:])]
    return list(HEIGHTS[-1][1:])


def rise(u, power):
    """0 at u = 0 to 1 at u = 1, rounded at the top (a lip's slope)."""
    u = min(max(u, 0.0), 1.0)
    return math.sin(math.pi / 2 * u) ** power


def section(x, v):
    """The surface across the mouth at x: v from -1 (the lower lip's bottom edge) through 0 (the parting) to 1 (the
    upper lip's top edge): the point's y and height."""
    top, part, bot = curve(TOP, x), curve(PARTING, x), curve(BOTTOM, x)
    hu, hl, hc, he = heights(x)
    if v >= 0:
        y = part + v * (top - part)
        if v < CREST_U:
            z = hc + (hu - hc) * rise(v / CREST_U, 0.75)
        else:
            z = he + (hu - he) * rise((1 - v) / (1 - CREST_U), 0.55)
    else:
        y = part + v * (part - bot)
        s = -v
        if s < CREST_L:
            z = hc + (hl - hc) * rise(s / CREST_L, 0.75)
        else:
            z = he + (hl - he) * rise((1 - s) / (1 - CREST_L), 0.5)
    return y, z


def across(n):
    """The v of the points across: closer at the parting and the edges."""
    out = []
    for i in range(n + 1):
        t = -1 + 2 * i / n
        out.append(math.copysign(abs(t) ** 1.0, t))
    # a little closer round the parting (the crease) and the edges
    extra = [-0.985, -0.95, -0.04, -0.015, 0.015, 0.04, 0.95, 0.985]
    return sorted(set([round(v, 4) for v in out + extra]))


def stations(n=64):
    """The x of the sections, closer towards the corners."""
    half = -CORNER[0]
    return [half * (0.55 * t + 0.45 * math.sin(math.pi / 2 * t)) for t in (-1 + 2 * i / n for i in range(1, n))]


def mouth(m):
    vs = across(36)
    rings = []
    for x in stations():
        top_y, bot_y = curve(TOP, x), curve(BOTTOM, x)
        ring = [Vector((x, bot_y - SKIRT, 0.0))]
        ring += [Vector((x,) + section(x, v)) for v in vs]
        ring.append(Vector((x, top_y + SKIRT, 0.0)))
        # the underside, back along the floor
        for j in range(1, 6):
            t = j / 6
            ring.append(Vector((x, top_y + SKIRT + (bot_y - top_y - 2 * SKIRT) * t, 0.0)))
        rings.append(ring)
    end = Vector((CORNER[0] - 0.15, CORNER[1], 0.25))
    obj = k.loft("lips", rings, m["red4"], start_point=end, end_point=Vector((-end.x, end.y, end.z)))
    k.recalc_normals(obj)
    # Colours: bands of the light; the crease and the outer edge (low down) dark.
    values = []
    for v in obj.data.vertices:
        value = v.normal.dot(LIGHT)
        x, y, z = v.co
        part = curve(PARTING, x)
        hc = heights(x)[2]
        if abs(y - part) < 0.12 and z < hc + 0.35:
            value = -5.0
        elif z < 0.42:
            value = -3.0
        values.append(value)
    band_split(obj, values, [(-9.0, m["edge"]), (-4.0, m["crease"]), (-2.0, m["red1"]), (0.0, m["red2"]),
                             (0.3, m["red3"]), (0.52, m["red4"]), (0.7, m["red5"]), (0.84, m["red6"]),
                             (0.94, m["red7"])])
    return k.smooth(obj, 60.0)


# --- Materials -------------------------------------------------------------------------------------------------------

def materials():
    pal = k.level_palette()

    def mat(name, index, roughness=0.26, glow=0.08):
        kw = dict(emission=pal[index], emission_strength=glow) if glow else {}
        return k.material("lips_" + name, palette=index, metallic=0.05, roughness=roughness, **kw)
    dark = mat("dark", 0x41, 0.45, 0.0)
    return {
        "edge": dark,
        "crease": dark,
        "red1": mat("red1", 0x42),
        "red2": mat("red2", 0x43),
        "red3": mat("red3", 0x44),
        "red4": mat("red4", 0x45),
        "red5": mat("red5", 0x46),
        "red6": mat("red6", 0x47, 0.22),
        "red7": mat("red7", 0x49, 0.18),
    }


# --- Build ------------------------------------------------------------------------------------------------------

def build_whole():
    m = materials()
    whole = [mouth(m)]
    for obj in whole:
        mk.apply(obj)
        obj.data.transform(Matrix.Translation((AXIS_X, 0.0, 0.0)))
        obj.data.update()
    bpy.context.view_layer.update()
    return whole, m


def whole_mask(sheet):
    """The two sprites' silhouettes side by side: 48 x 28."""
    left, right = k.sprite_mask(sheet, 196), k.sprite_mask(sheet, 208)
    return [left[y] + right[y] for y in range(28)]


def export_pieces(whole, m, options, sheet=None):
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    for name, sprite, (x0, x1) in PIECES:
        if only and name not in only:
            continue
        parts = [p for p in (cut(src, (x0, x1, -14.0, 14.0), m["crease"]) for src in whole) if p is not None]
        db.drop_unused(parts)
        mk.transform(parts, Matrix.Translation((-(x0 + x1) / 2, 0.0, 0.0)))
        bpy.context.view_layer.update()
        triangulate(parts)
        piece = db.join(parts, name)
        piece.data.name = name
        for src in whole:
            src.hide_render = True
        if sheet:
            mk.compare("%s (x5e %d)" % (name, sprite), mk.coverage([piece], 24, 28), k.sprite_mask(sheet, sprite))
        mk.report(name, [piece], os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, [piece])
        bpy.data.objects.remove(piece)
        for src in whole:
            src.hide_render = False


def build():
    k.reset()
    options = k.args()
    whole, m = build_whole()
    print("whole mouth: %d triangles" % mk.triangles(whole))
    sheet = os.path.join(options["check"], "enemy_x5e.png") if "check" in options else None
    if sheet:
        mk.compare("mouth (x5e 196 208)", mk.coverage(whole, 48, 28), whole_mask(sheet))
    bpy.context.scene.view_settings.view_transform = "Standard"
    if "preview" in options:
        mk.preview(options["preview"] + "lips_whole", whole, size=(48, 28), scale=10, distance=1.5)
    if "whole" in options:
        triangulate(whole)
        mk.export(whole, options["whole"])
    if options.get("only") != "none":
        export_pieces(whole, m, options, sheet)


if __name__ == "__main__":
    build()
