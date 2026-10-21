"""SAVARA's big red and grey jet fighter (sheet I), polished (2026-10-21; it replaces wave3_k.py's redwing_whole(),
a lathed body on flat painted wings). Seven 2x2 sprites, each an enemy of its own (302-308), which the levels
always place as one 96 x 84 picture and move together (SAVARA's events at 400, 500, 600...: 302 at x and 303 at
x + 24, 56 pixels above 308; 304, 305, 306, 307 at x - 24, x, x + 24, x + 48, 28 pixels above 308; 308 at x + 12):
the tail I 201, 203 (columns 24-71 of rows 0-27 of the picture), the wings and the middle I 237, 239, 241, 243
(columns 0-95 of rows 28-55) and the beak I 278 (columns 36-59 of rows 56-83). They are top enemies in episode 1's
SAVARA and episode 3's SAVARA Y, ground enemies in episode 5's SAVARA, where they fly at their own speed as well
(eyc 4-5): the fighter flies, low there; no height=-4. models.cfg: model redwing_<sprite> enemies/redwing_<sprite>.glb
origin; sprite i <sprite> redwing_<sprite> yaw=0 (as before). No other enemy shows these sprites and none of them
animates. The fighter is symmetric about the middle of the picture's column 48, so the sprites' halves mirror with
a pixel's shift (201/203, 237/243, 239/241, 278's halves: 97-99.6 % of their silhouettes), but none is another's
pixels mirrored (31-63 % of the indices: each is shaded on its own, the light from the left): built as one half and
its mirror image.

As the sprites and their 4x upscales draw it, nose down the screen, flying (about 2 to 16 pixels high):
- The beak (rows 56-83): a long red cone from the cockpit to its point (row 83), drooping a little, a low crest
  along its top (the lit line, column 47), narrowing faster in front of row 68, a thin dark chine along each side
  there (the dark pixels beside it, rows 69-80), a hatch's outline on its top (columns 46-50 of rows 71-75). At its
  cheeks the intakes (columns 39-40 and 56-57 of rows 55-65): red fairings growing out of its sides, their dark
  mouths facing forward, a dark splitter gap between them and the beak in front (columns 41 and 55, rows 59-64).
- The cockpit (rows 41-55): the red body at its widest, two glossy black canopies either side (columns 40-44 and
  52-56 of rows 44-53) in dark sills, a small black dome on the middle at the spine's front (columns 45-51 of rows
  40-44), each with a light glint (columns 43 and 53 of row 47, column 47 of row 41).
- The dark grey ducts along the body's flanks, from their dark mouths beside the wing roots' front (columns 35-38 of
  row 55) back and in over the body's waist into the shoulders, a dark groove between them and the body; a dark
  fillet along each wing's root beside them (columns 34-37 of rows 31-48). Round the dome the body's red narrows to
  strips beside the spine (columns 42-44 and 52-54 of rows 34-40), its flanks beyond them grey, a groove between.
- The red shoulders either side of the spine (columns 39-44 and 52-57 of rows 24-34), three slats across them
  (grooves at rows 28, 30 and 32), rounded at their back.
- The grey spine down the middle from the dome to the tail (columns 45-51), lit along its left, and the darker
  grey tail cone behind (rows 6-19) with a lighter ridge either side of the fin (columns 45 and 51), a dark end.
- The wings: straight (the trailing edge along row 29), the leading edge straight from the rounded grey tips
  (columns 2-7 and 89-94) to column 16 and sweeping forward into a glove beside the ducts (rows 42-54); on each,
  from the tip in: a vent grille, four red slats in a dark frame (columns 8-15 of rows 30-35), and a dark box with
  two small red lamps (columns 10 and 14 of rows 38-40, glowing a little) by the leading edge; the red panel
  (columns 19-27), its back part a grille of three slats (rows 30-35) over a groove across it (row 35), a light
  rib along its inner edge (columns 26-27); the grey root panel's H (columns 29-34): a light raised bar (columns
  32-34) parted round the crossbar (row 36), the groove beside it (column 31) broken by the crossbar.
- The tail (rows 3-27): two grey engine nacelles beside the fuselage (columns 29-41 and 55-67), each with a red cap
  in its intake (rows 19-22), its front a little outwards, a red pod along each side (rows 11-18) and a rounded
  rear with a dark nozzle (rows 7-8) glowing a little inside; dark pylons between them and the fuselage (columns
  40-42 of rows 19-20); under them a tailplane whose tips carry the fins canted outwards (columns 25-28 and 68-71,
  rows 7-18); the tall middle fin (column 48, rows 3-15), swept back past the tail cone, its top edge light.

Built as a real aircraft: the fuselage, the cheeks' fairings, the ducts and the shoulders are lofts of elliptical
sections running into one another, dark seams along the grooves where they meet; wings, tailplane and fins lofted
from airfoil sections (polish_jets.py's lifting surfaces); panels, vents, slats and lamps lie on the wings' tops;
nacelles, pods, caps and nozzles lathed. The sprites' dark outline is not geometry: the plans reach about two thirds
into the outline pixels. The fighter is built whole and cut along the sprites' edges into the seven pieces
(polish_arch.cut: the pieces keep the whole's shading across the cuts, their cuts capped), each moved so that its
sprite's centre is its origin (its base on the layer: z = 0): drawn at their own places, they meet again.

Coordinates: 1 unit = 1 game pixel; x = the picture's column edge - 48, y = 42 - the row edge, +Z up (the parts
are built about X = x - 0.5 = 0, the picture's axis, and moved there: AXIS_X). Colours are the sprites' palette
indices (palette materials): the reds 0x43-0x49, the greys 0x02-0x0c.

Replaces wave3_k.py (redwing_whole and its helpers, REDWING_PIECES, OBJECTS; nothing else is left in it).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes of the
whole and of each piece against enemy_I.png), --preview <prefix> (the whole's and each piece's top and 3/4 views),
--only <model,...> (pieces to export; "none": none), --whole <file.glb> (the uncut fighter as well, for looking
at), --stats 1 (each piece's largest parts).
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
from polish_arch import cut  # noqa: E402  (polish_machine_kit.cut without its material indices shifted twice)
from polish_jets import (Curve, Plan, lifting_surface, mirrored, smoothstep, spaced, surface_height,  # noqa: E402
                         tip_planform, to_fin, tube)

AXIS_X = 0.5
# name, sprite, the box it covers in the whole's coordinates (x0, x1, y0, y1)
PIECES = [("redwing_201", 201, (-24, 0, 14, 42)), ("redwing_203", 203, (0, 24, 14, 42)),
          ("redwing_237", 237, (-48, -24, -14, 14)), ("redwing_239", 239, (-24, 0, -14, 14)),
          ("redwing_241", 241, (0, 24, -14, 14)), ("redwing_243", 243, (24, 48, -14, 14)),
          ("redwing_278", 278, (-12, 12, -42, -14))]


def materials():
    pal = k.level_palette()

    def mat(name, index, metallic=0.0, roughness=0.5, **kw):
        return k.material("redwing_" + name, palette=index, metallic=metallic, roughness=roughness, **kw)
    return {
        "body": mat("body", 0x49, 0.25, 0.32),          # the cockpit, the beak, the cheeks
        "red": mat("red", 0x48, 0.2, 0.36),             # shoulders, pods, caps, slats
        "red_dark": mat("red_dark", 0x43, 0.25, 0.42),  # grooves, the hatch's outline
        "panel": mat("panel", 0x44, 0.2, 0.38),         # the wings' red panels
        "steel": mat("steel", 0x07, 0.5, 0.34),         # wings, nacelles, tailplane, the middle fin
        "duct": mat("duct", 0x04, 0.5, 0.34),           # the ducts, the tip fins, the fuselage's grey flanks
        "spine": mat("spine", 0x08, 0.5, 0.3),          # the spine, the H's bar, the middle fin's top edge
        "tail": mat("tail", 0x03, 0.5, 0.36),           # the tail cone
        "seam": mat("seam", 0x03, 0.4, 0.5),            # grooves on the grey
        "dark": mat("dark", 0x02, 0.4, 0.5),            # vents, mouths, sills, chines, pylons, the roots' fillets
        "glass": mat("glass", 0x02, 0.2, 0.18),         # canopies, the dome
        "glint": mat("glint", 0x0c, 0.0, 0.3),          # their glints
        "lamp": mat("lamp", 0x48, 0.0, 0.3, emission=pal[0x4a], emission_strength=0.35),
        "exhaust": mat("exhaust", 0x4a, 0.0, 0.4, emission=pal[0x4c], emission_strength=0.3),
    }


def end_round(y, y0, y1, r0, r1):
    """1 inside [y0, y1], falling on a quarter circle to 0 within r0 of y0 and r1 of y1."""
    f = 1.0
    for d, r in ((y - y0, r0), (y1 - y, r1)):
        if d <= 0:
            return 0.0
        if r > 0 and d < r:
            f = min(f, math.sqrt(max(0.0, 1 - (1 - d / r) ** 2)))
    return f


# --- The hull -------------------------------------------------------------------------------------------------
# The fuselage, the cheeks' intake fairings, the ducts and the shoulders are lofts of their own (elliptical
# sections) running into one another; dark seams lie along the grooves where the ducts and the cheeks meet the
# fuselage (where their sections' outlines cross).

# The fuselage: y, half-width, axis height, top, bottom. The beak's point at row 83, narrowing faster in front of
# row 68 (the sprite's step, the dark chines beside it); the cockpit at its widest (rows 42-55, the outline at
# columns 38 and 58), as wide behind it under the ducts (rows 34-41), narrow between the shoulders (rows 25-33);
# the tail cone narrowing behind the nacelles' pods (rows 10-6). A low crest along the top of the beak and the
# cockpit (the sprite's lit line, column 47).
CORE = Curve([(-41.1, 0, 4.9, 0, 0), (-40.6, 0.5, 4.95, 0.42, 0.36), (-39.6, 1, 5, 0.88, 0.72),
              (-38.6, 1.5, 5.05, 1.32, 1.06), (-37.6, 2, 5.1, 1.78, 1.4), (-36.5, 2.5, 5.15, 2.2, 1.72),
              (-35.5, 2.95, 5.2, 2.6, 2), (-34.5, 3.4, 5.25, 2.96, 2.26), (-33.5, 3.85, 5.3, 3.34, 2.52),
              (-32.5, 4.3, 5.35, 3.7, 2.76), (-31.5, 4.72, 5.4, 4.06, 3), (-30.5, 5.1, 5.45, 4.38, 3.2),
              (-29.7, 5.4, 5.5, 4.6, 3.34), (-28.6, 5.78, 5.53, 4.86, 3.48), (-27.6, 6.25, 5.57, 5.14, 3.64),
              (-26.6, 6.75, 5.61, 5.38, 3.8), (-25.6, 6.98, 5.65, 5.45, 3.82), (-24.0, 7.0, 5.72, 5.45, 3.75),
              (-22.5, 6.95, 5.8, 5.45, 3.66), (-18, 6.8, 5.9, 5.42, 3.55), (-15.2, 6.85, 5.98, 5.42, 3.57),
              (-14.2, 7.4, 6, 5.5, 3.65), (-13.3, 8.8, 6, 5.65, 3.69), (-12.4, 9.7, 6, 5.8, 3.69),
              (-10, 9.95, 6, 5.9, 3.69), (-5, 9.9, 6, 5.9, 3.69), (-2.6, 9.75, 6, 5.8, 3.65),
              (0, 9.65, 6, 5.6, 3.57), (4, 9.6, 6, 5.45, 3.49), (7, 9.45, 6, 5.35, 3.4),
              (8.2, 8.9, 6, 5.3, 3.36), (9.2, 7, 6.02, 5.2, 3.28), (10.2, 5.5, 6.03, 5.1, 3.2),
              (12, 5.1, 6.04, 5, 3.16), (16, 5.1, 6.05, 4.9, 3.12), (17.3, 5.7, 6.06, 4.85, 3.08),
              (18.4, 6.8, 6.08, 4.75, 3.03), (20, 7, 6.1, 4.5, 2.95),
              (22, 6.75, 6.15, 4.3, 2.83), (23.5, 6.55, 6.2, 4.15, 2.79),
              (27, 6.5, 6.3, 4, 2.66), (30.4, 6.35, 6.4, 3.85, 2.72), (31.4, 5.45, 6.45, 3.45, 2.7),
              (32.6, 4.75, 6.5, 3.1, 2.4), (33.8, 3.95, 6.55, 2.72, 2.1), (34.9, 2.95, 6.6, 2.2, 1.7),
              (35.6, 1.7, 6.6, 1.45, 1.1), (36.05, 0, 6.6, 0, 0)])
NOSE_Y, TAIL_Y = -41.1, 36.05


def crest_of(y):
    """The low crest along the top of the beak and the cockpit."""
    return 0.38 * smoothstep(-39.5, -36.0, y) * (1 - smoothstep(-4.5, -2.2, y))


def red_edge(y):
    """How far out the fuselage's top is red, the flanks beyond grey: all of it in front of row 44, narrowing
    round the dome to the strips beside the spine (columns 42-44 and 52-54 of rows 34-40), the shoulders' inner
    edges between them; none behind the shoulders."""
    if y < -2.2:
        return 99.0
    if y < 1.0:
        return 9.8 - 2.3 * smoothstep(-2.2, 1.0, y)
    if y < 8.25:
        return 7.5 - 0.8 * smoothstep(1.0, 7.0, y)
    if y < 18.6:
        return 4.6
    return 0.0


# The left cheek's intake fairing (columns 39-40, rows 55-65): y, x, z, half-width, top, bottom; its blunt front
# (the dark mouth) at y -23.15, growing out of the beak's side behind and running into the cockpit.
CHEEK = Curve([(-23.15, -8.3, 6.3, 1.42, 1.95, 1.6), (-20.0, -8.2, 6.35, 1.52, 2.05, 1.7),
               (-17.0, -8.0, 6.4, 1.64, 2.15, 1.8), (-14.5, -7.7, 6.45, 1.86, 2.25, 1.85),
               (-12.2, -7.4, 6.4, 1.7, 2.0, 1.7)])
CHEEK_Y = (-23.15, -12.2)
SLOT_Y = -16.8      # in front of this the dark splitter gap between the cheek and the beak (rows 59-64)

# The left duct (rows 34-55): y, x, z, half-width, top, bottom; from its blunt front (the dark mouth) beside the
# wing root's glove (row 55), low there, back and in over the waist, into the shoulder.
DUCT = Curve([(-14.05, -11.8, 5.9, 2.3, 1.1, 1.75), (-12.0, -11.82, 5.95, 2.38, 1.35, 1.85),
              (-8.0, -11.8, 6.05, 2.4, 1.8, 1.9), (-4.0, -11.6, 6.1, 2.45, 1.95, 1.9),
              (-1.0, -11.0, 6.2, 2.66, 2.05, 1.95), (2.0, -10.1, 6.3, 2.8, 2.15, 2.0),
              (4.5, -9.4, 6.4, 2.72, 2.25, 2.0), (7.0, -8.7, 6.5, 2.3, 2.35, 2.0), (9.0, -8.35, 6.6, 1.6, 2.3, 1.8),
              (10.0, -8.25, 6.6, 1.2, 2.1, 1.6)])
DUCT_Y = (-14.05, 10.0)

# The left shoulder (columns 39-44 of rows 24-34): y, x, z, half-width, top, bottom (a superellipse's: boxy); its
# front face over the duct (row 34), rounded behind (row 24). Three slats across it: grooves at rows 28, 30, 32.
SHOULDER = Curve([(7.7, -6.9, 6.4, 3.45, 4.5, 2.2), (9.0, -6.95, 6.4, 3.62, 4.85, 2.3),
                  (12.0, -6.95, 6.4, 3.62, 4.9, 2.3), (15.0, -6.8, 6.4, 3.45, 4.75, 2.3),
                  (16.5, -6.2, 6.4, 2.9, 4.3, 2.1), (17.5, -5.6, 6.3, 2.3, 3.7, 1.9),
                  (18.3, -5.05, 6.2, 1.6, 2.9, 1.5), (18.8, -4.7, 6.1, 1.0, 2.1, 1.2)])
SHOULDER_Y = (7.7, 18.8)
SLATS_Y = (9.6, 11.6, 13.6)
SLAT_DEPTH, SLAT_HALF = 0.5, 0.42


def slat_dip(y):
    return sum(max(0.0, 1 - ((y - s) / SLAT_HALF) ** 2) for s in SLATS_Y)


def section_angles(top_count, bottom_count, lo=-15.0, hi=195.0):
    """Angles round an elliptical section: top_count from lo to hi degrees (its top and sides), bottom_count
    underneath."""
    top = [lo + (hi - lo) * i / (top_count - 1) for i in range(top_count)]
    gap = 360.0 - (hi - lo)
    bottom = [hi + gap * (i + 1) / (bottom_count + 1) for i in range(bottom_count)]
    return [math.radians(a) for a in top + bottom]


CORE_ANGLES = section_angles(33, 6)
LOBE_ANGLES = section_angles(17, 4)
DUCT_ANGLES = section_angles(13, 3)


def ellipse(y, x, z, hw, top, bottom, angles, crest=0.0, power=2.0):
    """An elliptical section at y round (x, z): half-width hw, its upper half top high, its lower bottom; crest
    raises a narrow ridge along its top; power > 2 makes it a fuller superellipse (boxier)."""
    def f(v):
        return math.copysign(abs(v) ** (2.0 / power), v)
    return [Vector((x + hw * f(math.cos(a)), y, z + (top if math.sin(a) >= 0 else bottom) * f(math.sin(a)) +
                    crest * max(0.0, math.sin(a)) ** 14)) for a in angles]


def stations(spans):
    """y values from (y0, y1, step) spans."""
    ys = []
    for y0, y1, step in spans:
        count = max(1, int(round((y1 - y0) / step)))
        ys += [y0 + (y1 - y0) * i / count for i in range(count)]
    ys.append(spans[-1][1])
    return ys


def core_top(x, y):
    """The fuselage's top at (x, y)."""
    hw, zc, top, _ = CORE(y)
    if hw <= 0.02 or abs(x) >= hw:
        return zc
    s = math.sqrt(1 - (x / hw) ** 2)
    return zc + top * s + crest_of(y) * s ** 14


def fuselage(m):
    ys = stations(((NOSE_Y, -38.0, 0.42), (-38.0, -28.4, 0.62), (-28.4, -26.4, 0.4), (-26.4, -15.6, 0.72),
                   (-15.6, -12.0, 0.45), (-12.0, -2.8, 0.75), (-2.8, 1.6, 0.5), (1.6, 30.0, 0.75),
                   (30.0, TAIL_Y, 0.42)))
    rings = []
    for y in ys:
        if NOSE_Y + 0.05 < y < TAIL_Y - 0.05:
            hw, zc, top, bottom = CORE(y)
            rings.append(ellipse(y, 0.0, zc, hw, top, bottom, CORE_ANGLES, crest_of(y)))
    body = k.loft("fuselage", rings, m["body"], start_point=(0, NOSE_Y, CORE(NOSE_Y)[1]),
                  end_point=(0, TAIL_Y, CORE(TAIL_Y)[1]))
    # Its faces cut along the red's edge round the dome and beside the spine, so that it runs smoothly.
    bm = bmesh.new()
    bm.from_mesh(body.data)
    values = {v: abs(v.co.x) - red_edge(v.co.y) for v in bm.verts}
    for e in list(bm.edges):
        a, b = e.verts
        if not (-2.4 < a.co.y < 8.2 and -2.4 < b.co.y < 8.2):
            continue
        fa, fb = values[a], values[b]
        if fa * fb < 0:
            _, v = bmesh.utils.edge_split(e, a, fa / (fa - fb))
            values[v] = 0.0
    for f in list(bm.faces):
        ends = [v for v in f.verts if values.get(v) == 0.0]
        if len(ends) == 2 and not any(ends[1] in e.verts for e in ends[0].link_edges):
            bmesh.utils.face_split(f, ends[0], ends[1])
    bm.to_mesh(body.data)
    bm.free()

    def pick(c, n):
        if c.y > 35.3:
            return m["dark"]
        if c.y > 23.4:
            return m["tail"]
        if abs(c.x) > red_edge(c.y):
            return m["duct"] if c.y < 8.3 else m["steel"]
        return m["body"]
    mk.paint(body, pick)
    return k.smooth(body, 42)


def lobe(name, table, y_range, rounding, side, spans, mat, angles=LOBE_ANGLES, dip=None, power=2.0):
    """A loft along y through the table's sections (y -> x, z, half-width, top, bottom; the left side's), on the
    given side, rounded at its ends over rounding (front, back); dip(y) lowers its top; power: its sections'
    (ellipse()'s)."""
    y0, y1 = y_range
    rings = []
    for y in stations(spans):
        if not (y0 + 0.01 < y < y1 - 0.01):
            continue
        x, z, w, t, b = table(y)
        f = max(end_round(y, y0, y1, rounding[0], rounding[1]), 0.05)
        if dip is not None:
            t -= dip(y)
        rings.append(ellipse(y, side * abs(x), z, w * f, t * f, b * f, angles, power=power))
    (xa, za, *_), (xb, zb, *_) = table(y0), table(y1)
    obj = k.loft(name, rings, mat, start_point=(side * abs(xa), y0, za), end_point=(side * abs(xb), y1, zb))
    return obj


def crease(y, lob, side):
    """Where the fuselage's section at y meets a lobe's (x, z, half-width, top, bottom) on top: the first point
    of the fuselage's outline from its top towards the side that lies in the lobe; None if it doesn't meet it."""
    hw, zc, top, bottom = CORE(y)
    lx, lz, lw, lt, lb = lob
    if lw < 0.05 or hw < 0.05:
        return None

    def point(a):
        return Vector((hw * math.cos(a), y, zc + (top if math.sin(a) >= 0 else bottom) * math.sin(a)))

    def inside(p):
        h = lt if p.z >= lz else lb
        return ((p.x - lx) / lw) ** 2 + ((p.z - lz) / h) ** 2 <= 1.0
    a_prev = math.radians(90.0)
    for i in range(1, 131):
        a = math.radians(90.0 - side * i)
        if inside(point(a)):
            lo, hi = a_prev, a
            for _ in range(20):
                mid = (lo + hi) / 2
                if inside(point(mid)):
                    hi = mid
                else:
                    lo = mid
            return point((lo + hi) / 2)
        a_prev = a
    return None


def seam_along(name, ys, lob_of, side, mat, radius, sink=0.08, radii=None):
    """A dark seam along the crease between the fuselage and a lobe (lob_of(y) its section), over ys; split
    where they don't meet."""
    runs, run = [], []
    for y in ys:
        p = crease(y, lob_of(y), side)
        if p is None:
            if len(run) > 2:
                runs.append(run)
            run = []
            continue
        run.append(p - Vector((0, 0, sink)))
    if len(run) > 2:
        runs.append(run)
    for i, pts in enumerate(runs):
        tube("%s%d" % (name, i), pts, radius, mat, radii=[radii(p.y) for p in pts] if radii else None)


def hull(m):
    fuselage(m)
    for side, tag in ((-1, "_l"), (1, "_r")):
        cheek = lobe("cheek" + tag, CHEEK, CHEEK_Y, (0.25, 0.9), side,
                     ((CHEEK_Y[0], -21.5, 0.25), (-21.5, CHEEK_Y[1], 0.6)), m["body"])
        mk.paint(cheek, lambda c, n: m["dark"] if c.y < CHEEK_Y[0] + 0.1 and n.y < -0.9 else None)
        k.smooth(cheek, 50)
        duct = lobe("duct" + tag, DUCT, DUCT_Y, (0.3, 1.2), side,
                    ((DUCT_Y[0], -12.8, 0.3), (-12.8, 8.5, 0.95), (8.5, DUCT_Y[1], 0.4)), m["duct"],
                    angles=DUCT_ANGLES)
        mk.paint(duct, lambda c, n: m["dark"] if c.y < DUCT_Y[0] + 0.3 and n.y < -0.55 else None)
        k.smooth(duct, 50)
        shoulder = lobe("shoulder" + tag, SHOULDER, SHOULDER_Y, (0.55, 1.1), side,
                        ((SHOULDER_Y[0], 8.6, 0.25), (8.6, 14.6, 0.24), (14.6, SHOULDER_Y[1], 0.5)), m["red"],
                        angles=DUCT_ANGLES, dip=lambda y: SLAT_DEPTH * slat_dip(y), power=2.6)
        mk.paint(shoulder, lambda c, n: m["red_dark"] if slat_dip(c.y) > 0.35 and n.z > 0.2 else None)
        k.smooth(shoulder, 50)

        def duct_section(y, side=side):
            x, z, w, t, b = DUCT(y)
            f = end_round(y, DUCT_Y[0], DUCT_Y[1], 0.3, 1.2)
            return (side * abs(x), z, w * f, t * f, b * f)

        def cheek_section(y, side=side):
            x, z, w, t, b = CHEEK(y)
            f = end_round(y, CHEEK_Y[0], CHEEK_Y[1], 0.25, 0.9)
            return (side * abs(x), z, w * f, t * f, b * f)
        seam_along("duct_seam" + tag, spaced(-13.4, 7.6, 26), duct_section, side, m["seam"], 0.22)
        pts = [Vector((side * red_edge(y), y, core_top(red_edge(y), y) - 0.07)) for y in spaced(2.6, 7.75, 9)]
        tube("waist_groove" + tag, pts, 0.19, m["seam"])
        seam_along("slot" + tag, spaced(-23.0, SLOT_Y, 14), cheek_section, side, m["dark"], 0.3,
                   radii=lambda y: 0.34 - 0.2 * smoothstep(SLOT_Y - 1.5, SLOT_Y, y))


def spine(m):
    """The grey rail down the middle from the dome to the tail cone (columns 45-51, rows 22-40)."""
    y0, y1 = 1.7, 24.4
    rings = []
    for i in range(30):
        y = y0 + (y1 - y0) * i / 29
        f = end_round(y, y0, y1, 1.0, 2.6)
        w = 3.3 * max(f, 0.1) * (1 - 0.12 * smoothstep(20, 24.4, y))
        base = core_top(0.0, y)
        rings.append(k.ring(y, w, 1.0, 16, z=base - 0.9, top=0.9 + 0.38 * max(f, 0.15), bottom=0.6, power=3.0))
    return k.smooth(k.loft("spine", rings, m["spine"]), 55)


def tail_ridges(m):
    """The two lighter ridges along the tail cone either side of the fin (columns 45 and 51 of rows 8-17)."""
    for side, tag in ((-1, "_l"), (1, "_r")):
        ys = spaced(24.3, 33.6, 14)
        pts = [Vector((side * 3.0 * (1 - 0.25 * smoothstep(30.5, 33.6, y)), y, 0.0)) for y in ys]
        pts = [Vector((p.x, p.y, core_top(p.x, p.y) - 0.12)) for p in pts]
        tube("tail_ridge" + tag, pts, 0.36, m["duct"], radii=[0.36 * (1 - 0.6 * smoothstep(31.5, 33.6, p.y))
                                                              for p in pts])


def dome_and_canopies(m):
    """The black dome at the spine's front (columns 45-51 of rows 40-44) and the two black canopies either side
    of the cockpit (columns 40-44 and 52-56 of rows 44-53), in dark sills, leaning with the body's top."""
    z = core_top(0.0, -0.15)
    glasses = [k.smooth(k.ellipsoid("dome", (0.0, -0.15, z - 0.95), (3.25, 2.45, 2.35), m["glass"], 20, 10), 60)]
    for side in (-1, 1):
        x, y = side * 6.0, -7.1
        z = core_top(x, y)
        lean = Matrix.Translation((x, y, z)) @ Matrix.Rotation(math.radians(17 * side), 4, "Y") @ \
            Matrix.Translation((-x, -y, -z))
        sill = k.ellipsoid("canopy_sill" + ("_l" if side < 0 else "_r"), (x, y, z - 1.25), (2.72, 5.18, 1.75),
                           m["dark"], 18, 10)
        glass = k.ellipsoid("canopy" + ("_l" if side < 0 else "_r"), (x, y + 0.1, z - 0.75), (2.42, 4.85, 2.25),
                            m["glass"], 20, 12)
        for obj in (sill, glass):
            obj.data.transform(lean)
            k.smooth(obj, 60)
        glasses.append(glass)
    # The glints (the sprite's light pixels: column 43 and 53 of row 47, column 47 of row 41), lying on the glass.
    bpy.context.view_layer.update()
    hit = mk.surface(glasses)
    for name, (x, y), (rx, ry) in (("glint_dome", (-1.0, 0.45), (0.55, 0.5)), ("glint_l", (-5.15, -5.4), (0.5, 0.8)),
                                   ("glint_r", (5.15, -5.4), (0.5, 0.8))):
        location, normal = hit(x, y)
        glint = k.ellipsoid(name, (0, 0, 0), (rx, ry, 0.14), m["glint"], 10, 6)
        glint.data.transform(Matrix.Translation(location - normal * 0.06) @
                             normal.to_track_quat("Z", "Y").to_matrix().to_4x4())
        k.smooth(glint, 60)


def beak_details(m):
    """The chines along the beak's sides, the hatch's outline on its top."""
    # The chines: thin dark blades along the beak's widest line (rows 69-80).
    ys = spaced(-38.7, -26.9, 28)
    for side in (-1, 1):
        rings = []
        for y in ys:
            hw, zc, top, bottom = CORE(y)
            f = end_round(y, ys[0], ys[-1], 1.6, 0.45)
            width = (0.75 + 0.62 * smoothstep(-29.9, -27.5, y)) * max(f, 0.12)  # wider at the step (rows 69-70)
            rings.append(k.ring(y, width, 0.17 * max(f, 0.4), 8, x=side * (hw + 0.05), z=zc + 0.25, power=2.0))
        k.smooth(k.loft("chine" + ("_l" if side < 0 else "_r"), rings, m["dark"]), 50)
    # The hatch's outline on the beak's top (columns 46-50 of rows 71-75).
    u, y0, y1 = 2.3, -33.4, -29.4
    path = [(-u, y0), (u, y0), (u, y1), (-u, y1), (-u, y0)]
    pts = []
    for (xa, ya), (xb, yb) in zip(path, path[1:]):
        for i in range(6):
            x, y = xa + (xb - xa) * i / 6, ya + (yb - ya) * i / 6
            pts.append(Vector((x, y, core_top(x, y) - 0.06)))
    pts.append(pts[0] + Vector((0.01, 0, 0)))
    tube("hatch", pts, 0.14, m["red_dark"])


# --- Raised parts on a surface --------------------------------------------------------------------------------

def plate(name, x0, x1, y_front, y_back, surf, height, mat, rim=0.3, sink=0.4, nx=10, ny=10):
    """A raised plate lying on the surface z = surf(x, y): from x0 to x1, from y_front(x) to y_back(x), `height`
    over the surface with its edges rounded over `rim`; closed underneath (sunk `sink` under its edges)."""
    def samples(length, count):
        r = min(rim / max(length, 1e-6), 0.3)
        inner = [r + (1 - 2 * r) * i / count for i in range(count + 1)]
        return [0.0, r * 0.3, r * 0.65] + inner + [1 - r * 0.65, 1 - r * 0.3, 1.0]

    def lift(d):
        if d >= rim:
            return 1.0
        return math.sqrt(max(0.0, 1 - (1 - d / rim) ** 2))
    us = samples(x1 - x0, nx)
    vs = samples(max(y_back((x0 + x1) / 2) - y_front((x0 + x1) / 2), 0.5), ny)
    nu, nv = len(us), len(vs)
    top = []
    for u in us:
        x = x0 + (x1 - x0) * u
        yf, yb = y_front(x), y_back(x)
        for v in vs:
            y = yf + (yb - yf) * v
            d = min(u * (x1 - x0), (1 - u) * (x1 - x0), v * (yb - yf), (1 - v) * (yb - yf))
            top.append((x, y, surf(x, y) + height * lift(d)))
    faces = [(i * nv + j, (i + 1) * nv + j, (i + 1) * nv + j + 1, i * nv + j + 1)
             for i in range(nu - 1) for j in range(nv - 1)]
    loop = [i * nv for i in range(nu)] + [(nu - 1) * nv + j for j in range(1, nv)] + \
        [i * nv + nv - 1 for i in range(nu - 2, -1, -1)] + [j for j in range(nv - 2, 0, -1)]
    o = len(top)
    bottom = [(top[i][0], top[i][1], surf(top[i][0], top[i][1]) - sink) for i in loop]
    centre = tuple(sum(v[j] for v in bottom) / len(bottom) for j in range(3))
    c = o + len(bottom)
    for a in range(len(loop)):
        b = (a + 1) % len(loop)
        faces.append((loop[a], loop[b], o + b, o + a))
        faces.append((o + b, o + a, c))  # the bottom: a fan (no n-gon for the exporter to triangulate)
    obj = k.mesh_object(name, top + bottom + [centre], faces, mat)
    k.recalc_normals(obj)
    return k.smooth(obj, 50)


def bar_on(name, x, y0, y1, surf, mat, hw=0.42, height=0.32, sink=0.35, steps=6, segments=10):
    """A small bar along y lying on the surface z = surf(x, y) (a slat, a lamp)."""
    rings = []
    for i in range(steps + 1):
        y = y0 + (y1 - y0) * i / steps
        f = end_round(y, y0, y1, 0.35, 0.35)
        rings.append(k.ring(y, hw * max(f, 0.3), 1.0, segments, z=surf(x, y), x=x, top=height * max(f, 0.3),
                            bottom=sink, power=2.6))
    return k.smooth(k.loft(name, rings, mat), 55)


def seam_on(name, points, surf, mat, radius=0.17, sink=0.07, count=10):
    """A groove (a thin dark tube sunk into the surface) along a polyline [(x, y)] on z = surf(x, y)."""
    pts = []
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        for i in range(count):
            t = i / count
            pts.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))
    pts.append(points[-1])
    return tube(name, [Vector((x, y, surf(x, y) - sink)) for x, y in pts], radius, mat)


# --- The wings ------------------------------------------------------------------------------------------------
# The left wing's plan (u = X, the root inside the duct): the trailing edge along row 29; the leading edge along
# row 41 from the rounded tip (columns 2-7) to column 16, then sweeping forward to the glove beside the duct
# (column 34, row 50) and down the duct's flank to row 55; the root's trailing edge stepping down into the
# shoulder (columns 35-37, rows 29-31).
WING = Plan([(-10.6, -12.85), (-13.9, -12.85), (-14.3, -9.95), (-14.75, -9.05), (-31.3, -0.62), (-32.0, 0.22),
             (-41.0, 0.28), (-42.7, 0.95), (-44.3, 2.4), (-45.6, 4.2), (-46.25, 6.0), (-46.3, 8.4), (-45.9, 10.3),
             (-44.85, 11.75), (-43.4, 12.72), (-42.0, 12.8), (-12.8, 12.8), (-12.5, 11.45), (-12.2, 10.7),
             (-10.6, 10.45)], rounding=2)
WING_US = [-10.62, -11.3, -12.0, -12.7, -13.3, -13.75, -14.1, -14.45, -14.9, -15.6, -16.5, -17.5, -18.5, -19.6,
           -20.4, -21.5, -22.5, -23.5, -24.5, -25.5, -26.5, -27.5, -28.5, -29.6, -30.6, -31.4, -32.4, -33.5, -34.6,
           -35.7, -36.8, -37.9, -39.0, -40.0, -41.0, -41.9, -42.8, -43.6, -44.3, -44.9, -45.4, -45.8, -46.05,
           -46.2]


def wing_mid(u):
    return 5.25 + 0.035 * max(0.0, -u - 11.0)


def wing_thick(u):
    """Thin, a little fuller at the rounded tip (its lit edge, columns 2-3)."""
    return 0.85 - 0.3 * smoothstep(-12.0, -46.0, u) + 0.26 * smoothstep(-41.5, -46.2, u)


WING_UNDER = 0.55
wing_top = surface_height(WING, wing_mid, wing_thick, under=WING_UNDER)


def wing_parts(m):
    """The left wing and what lies on it (mirrored for the right)."""
    parts = [lifting_surface("wing_l", WING_US, WING, wing_mid, wing_thick, m["steel"], under=WING_UNDER,
                             tip=WING.tip)]

    def surf(x, y):
        return wing_top(x, y)

    def const(v):
        return lambda x: v
    # The vent grille near the tip: four red slats in a dark frame (columns 8-15 of rows 30-35).
    parts.append(plate("grille_l", -40.65, -31.35, const(6.05), const(12.45), surf, 0.14, m["dark"], rim=0.2,
                       nx=6, ny=4))
    for i, x in enumerate((-39.0, -37.0, -35.0, -33.0)):
        parts.append(bar_on("grille_slat%d_l" % i, x, 6.55, 12.15, surf, m["red"], hw=0.5, height=0.36))
    # The dark box by the leading edge with two small red lamps (columns 10 and 14 of rows 38-40).
    parts.append(plate("lamp_box_l", -40.5, -32.5, const(0.95), const(4.95), surf, 0.12, m["dark"], rim=0.2,
                       nx=6, ny=4))
    for i, x in enumerate((-38.0, -34.0)):
        parts.append(bar_on("lamp%d_l" % i, x, 1.2, 3.85, surf, m["lamp"], hw=0.44, height=0.42, steps=5))
    # The red panel (columns 19-27), from the trailing edge to the glove's leading edge; its back part a grille
    # of three slats (grooves at columns 19, 21, 23 and 25, rows 30-35) and a groove across under it (row 35).
    le_glove = Curve([(-31.3, -0.62), (-14.75, -9.05)])

    def panel_front(x):
        return le_glove(x) + 0.95

    parts.append(plate("panel_l", -29.6, -20.45, panel_front, const(12.5), surf, 0.3, m["panel"], rim=0.35,
                       nx=8, ny=10))

    def panel_top(x, y):
        return surf(x, y) + 0.3
    for i, x in enumerate((-29.0, -27.0, -25.0, -23.0)):
        parts.append(seam_on("panel_slot%d_l" % i, [(x, 7.0), (x, 12.2)], panel_top, m["red_dark"], radius=0.2,
                             sink=0.08, count=6))
    parts.append(seam_on("panel_groove_l", [(-29.2, 6.5), (-22.6, 6.5)], panel_top, m["red_dark"], radius=0.19,
                         sink=0.08, count=8))
    # The light rib along the panel's inner edge (columns 26-27).
    parts.append(plate("panel_rib_l", -22.45, -20.6, lambda x: le_glove(x) + 1.25, const(12.4), panel_top, 0.16,
                       m["body"], rim=0.3, nx=3, ny=10))
    # The root panel's H (columns 29-34): a light raised bar (columns 32-34) parted round the crossbar (row 36),
    # the groove beside it (column 31) broken by the crossbar.
    for i, (yf, yb) in enumerate(((lambda x: le_glove(x) + 1.0, const(4.0)), (const(4.95), const(6.05)),
                                  (const(7.0), const(12.45)))):
        parts.append(plate("h_bar%d_l" % i, -16.55, -13.85, yf, yb, surf, 0.26, m["spine"], rim=0.32, nx=4,
                           ny=8 if i != 1 else 2))
    for name, path in (("h_upper_l", [(-17.05, 12.5), (-17.05, 6.25)]),
                       ("h_lower_l", [(-17.05, 4.75), (-17.05, -6.4)]),
                       ("panel_edge_l", [(-20.1, 12.5), (-20.1, -5.0)])):
        parts.append(seam_on(name, path, surf, m["seam"], radius=0.17, sink=0.06, count=8))
    # The dark fillet along the wing's root beside the duct (columns 34-37 of rows 31-48).
    parts.append(plate("root_fillet_l", -13.85, -10.45, const(-6.5), const(10.9), surf, 0.32, m["dark"], rim=0.45,
                       nx=3, ny=6))
    for part in parts:
        mirrored(part)


# --- The tail -------------------------------------------------------------------------------------------------
NAC_X, NAC_Z = -12.5, 6.6     # the left nacelle's axis (columns 33-38 its grey body)
POD_OUT = (-17.15, 6.3, 2.05)  # the red pods along it: x, z, half-width (columns 29-32 and 39-41)
POD_IN = (-8.1, 6.3, 1.62)
POD_SQUASH = 0.78


def lathe_y(name, profile, mat, x, z, segments=24, squash=1.0, angle=50):
    return k.smooth(k.lathe(name, profile, mat, segments=segments, axis_x=x, axis_z=z, squash=squash), angle)


def nacelle_parts(m):
    parts = []
    body = lathe_y("nacelle_l", [(23.35, 2.5), (23.55, 2.92), (24.1, 3.05), (31.0, 3.05), (32.1, 2.98),
                                 (33.0, 2.8), (33.75, 2.45), (34.35, 1.95), (34.7, 1.45), (34.85, 1.15)], m["steel"],
                   NAC_X, NAC_Z, segments=28)
    body.data.materials.append(m["dark"])
    for poly in body.data.polygons:  # its front face, round the cap: the intake's dark mouth
        if poly.center.y < 23.45 and poly.normal.y < -0.5:
            poly.material_index = 1
    parts.append(body)
    # The red cap in its intake (rows 19-22), just inside the rim, its front a little outwards and down.
    cap = lathe_y("cap_l", [(19.75, 0.0), (19.86, 1.1), (20.15, 1.95), (20.7, 2.5), (21.5, 2.78),
                                   (22.4, 2.85), (23.2, 2.75), (23.75, 2.45)], m["red"], 0.0, 0.0, segments=22)
    cap.data.transform(Matrix.Translation((NAC_X - 0.5, 0.0, NAC_Z - 0.45)) @ Matrix.Translation((0, 23.7, 0)) @
                        Matrix.Rotation(math.radians(-14), 4, "Z") @ Matrix.Translation((0, -23.7, 0)))
    parts.append(cap)
    # The dark nozzle at its rear, glowing a little (rows 7-8).
    parts.append(lathe_y("nozzle_l", [(34.55, 1.3), (35.05, 1.3), (35.2, 1.15), (35.1, 0.95), (34.8, 0.9)],
                         m["dark"], NAC_X, NAC_Z, segments=16))
    parts.append(lathe_y("exhaust_l", [(34.75, 0.92), (34.95, 0.9), (35.0, 0.5)], m["exhaust"], NAC_X, NAC_Z,
                         segments=16))
    # The red pods along its sides (rows 11-18).
    for name, (x, z, r), y0, y1 in (("pod_out_l", POD_OUT, 23.15, 31.35), ("pod_in_l", POD_IN, 23.3, 31.3)):
        parts.append(lathe_y(name, [(y0, 0.0), (y0 + 0.06, r * 0.6), (y0 + 0.28, r * 0.88), (y0 + 0.75, r),
                                    (y1 - 1.0, r), (y1 - 0.45, r * 0.78), (y1 - 0.1, r * 0.4), (y1, 0.0)],
                             m["red"], x, z, segments=18, squash=POD_SQUASH))
    # The tailplane under them, its tip carrying the canted fin (columns 25-28 of rows 7-18).
    tail_plan = Plan([(-5.0, 24.6), (-20.4, 24.6), (-20.95, 25.4), (-20.95, 30.6), (-20.4, 31.3), (-5.0, 31.3)],
                     rounding=2)
    parts.append(lifting_surface("tailplane_l", [-5.02, -7.0, -9.0, -11.0, -13.0, -15.0, -17.0, -18.5, -19.5,
                                                 -20.2, -20.7, -20.9], tail_plan, lambda u: 4.75,
                                 lambda u: 0.36, m["steel"], under=0.7, camber=0.0, tip=tail_plan.tip))
    span = 6.6
    fin_le = Curve([(0.0, 24.2), (-span, 30.6)])
    fin_te = Curve([(0.0, 33.8), (-span, 35.15)])

    def fin_plan(u):
        return tip_planform(u, fin_le, fin_te, -span, 1.5, 0.6)
    us = [0.0] + [-span * t for t in (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.78, 0.85, 0.91, 0.95, 0.98, 0.995)]
    fin = lifting_surface("tip_fin_l", us, fin_plan, lambda u: 0.0, lambda u: 0.42 - 0.022 * (-u), m["steel"],
                          under=1.0, camber=0.0, tip=(-span, 33.8))
    to_fin(fin, x=-20.35, z=4.9, cant=25.0)
    parts.append(fin)
    # The pylon between the nacelle's front and the fuselage (the dark pixels of columns 40-42, rows 19-20).
    pylon = []
    for y in spaced(21.6, 24.6, 8):
        f = end_round(y, 21.6, 24.6, 0.6, 0.5)
        pylon.append(ellipse(y, -7.85, 5.9, 1.85 * max(f, 0.1), 1.5 * max(f, 0.1), 1.4 * max(f, 0.1), LOBE_ANGLES))
    parts.append(k.smooth(k.loft("pylon_l", pylon, m["dark"], start_point=(-7.85, 21.6, 5.9),
                                 end_point=(-7.85, 24.6, 5.9)), 50))
    for part in parts:
        mirrored(part)


def tail_fin(m):
    """The tall middle fin (column 48, rows 3-15), swept back past the tail cone."""
    le = Curve([(0.0, 27.25), (-8.0, 37.1)])
    te = Curve([(0.0, 35.7), (-8.0, 38.95)])

    def plan(u):
        return tip_planform(u, le, te, -8.0, 1.4, 0.6)
    us = [0.0, -0.8, -1.6, -2.4, -3.2, -4.0, -4.8, -5.6, -6.3, -6.9, -7.35, -7.7, -7.92]
    fin = lifting_surface("fin", us, plan, lambda u: 0.0, lambda u: 0.42 - 0.02 * (-u), m["steel"], under=1.0,
                          camber=0.0, tip=(-8.0, 38.3))
    to_fin(fin, x=0.0, z=8.25)
    fin.data.materials.append(m["spine"])
    for poly in fin.data.polygons:  # its top edge lit
        if poly.center.z > 15.4:
            poly.material_index = 1


# --- Checks, previews and export ------------------------------------------------------------------------------

def cell_of(box):
    """The top left pixel (column, row) of a piece's sprite in the 96 x 84 picture."""
    return int(box[0] + 48), int(42 - box[3])


def whole_mask(sheet):
    mask = [[False] * 96 for _ in range(84)]
    for _, sprite, box in PIECES:
        c0, r0 = cell_of(box)
        part = k.sprite_mask(sheet, sprite)
        for y in range(28):
            for x in range(24):
                if part[y][x]:
                    mask[r0 + y][c0 + x] = True
    return mask


def build_whole():
    m = materials()
    hull(m)
    spine(m)
    tail_ridges(m)
    dome_and_canopies(m)
    beak_details(m)
    wing_parts(m)
    nacelle_parts(m)
    tail_fin(m)
    whole = mk.meshes()
    mk.transform(whole, Matrix.Translation((AXIS_X, 0, 0)))
    bpy.context.view_layer.update()
    return whole, m


def build():
    k.reset()
    options = k.args()
    stats = "stats" in options
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    whole, m = build_whole()
    low, high = mk.bounds(whole)
    print("whole fighter: %d triangles, %d objects, z %.2f..%.2f" % (mk.triangles(whole), len(whole), low.z, high.z))
    for obj in sorted(whole, key=lambda o: -mk.triangles([o]))[:12]:
        print("   %-20s %6d" % (obj.name, mk.triangles([obj])))
    sheet = os.path.join(options["check"], "enemy_I.png") if "check" in options else None
    if sheet:
        mk.compare("whole (I 201 203 / 237-243 / 278)", mk.coverage(whole, 96, 84), whole_mask(sheet))
    bpy.context.scene.view_settings.view_transform = "Standard"
    if "preview" in options:
        mk.preview(options["preview"] + "redwing_whole", whole, size=(96, 84), scale=8, distance=1.7)
    if "whole" in options:
        mk.export(whole, options["whole"])
    for name, sprite, box in PIECES:
        if only and name not in only:
            continue
        parts = [p for p in (cut(src, box, m["dark"]) for src in whole) if p is not None]
        mk.transform(parts, Matrix.Translation((-(box[0] + box[1]) / 2, -(box[2] + box[3]) / 2, 0)))
        bpy.context.view_layer.update()
        for src in whole:
            src.hide_render = True
        if sheet:
            mk.compare("%s (I %d)" % (name, sprite), mk.coverage(parts, 24, 28), k.sprite_mask(sheet, sprite))
        mk.report(name, parts, os.path.join(out, name + ".glb"))
        if stats:
            for obj in sorted(parts, key=lambda o: -mk.triangles([o]))[:8]:
                print("    %-20s %6d" % (obj.name, mk.triangles([obj])))
        if "preview" in options:
            mk.preview(options["preview"] + name, parts)
        for obj in parts:
            bpy.data.objects.remove(obj)
        for src in whole:
            src.hide_render = False


if __name__ == "__main__":
    build()
