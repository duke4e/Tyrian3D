"""GYGES' bronze worm: its pointed head in tiers (sheet H sprite 17 above 55, 2x2 each: one 24 x 56 picture; enemies
422 and 423 of episode 2, one link) and its ribbed tail with a dome and shoulder hooks (H 131, 2x2; enemy 425), on
the top layer or in the sky, one frame each, no damaged look, polished (2026-10-22, round 29; they replace
wave3_ad.py's worm head and tail, a lathe round the sprites' rows painted pixel by pixel). The worm's five body
segments between them are the bronze ingot, bronze_yuanbao (H 93, polish_yuanbao.py): head and tail are its family
(the same glossy bronze in the same palette shades, the same crease down the front, the same thickness) and are
built round its height, so that the chain reads as one creature. models.cfg (all unchanged): model
gyges_worm_head_tip / gyges_worm_head_base enemies/<name>.glb origin, model gyges_worm_tail enemies/gyges_worm_tail.glb;
sprite h 17 gyges_worm_head_tip yaw=0, sprite h 55 gyges_worm_head_base yaw=0, sprite h 131 gyges_worm_tail yaw=0.
No other enemy, launched ones included, shows these sprites; none is another sprite's pixels mirrored, turned or in
other ramps (a search over every sheet).

How GYGES lays the worm out (its events, e.g. t29/t30: event 7, the top layer; t269 event 15, the sky; no episode 6
level takes these waves): 422 (17) at (x, y - 78) and 423 (55) at (x, y - 50), link 120; five segments 424 (93) at
(x, y - 40), (x, y - 30) ... (x, y), each its own link (121-125); the tail 425 (131) at (x, y + 10), link 126. So the
segments lie 10 pixels apart below the head base (their middles 10, 20 ... 50 pixels below its middle) and the tail's
middle 60 below it. Event 20 then starts each link swaying (exc steps 1 a tick between -4 and +4) two ticks after the
one behind it, from the tail up to the head: the links slide a few pixels sideways against each other, so each
junction is built to read when its neighbour is beside it as well as in line.

As the sprites and their 4x upscales draw them (glossy dark bronze, palette ramp 1, lit from the upper left; a dark
outline round them):
- the head (17 over 55; rows of the 24 x 56 picture): a pointed spearhead, its point at column 12 of row 14, a crease
  down its middle (column 12 bright, 13 dark: the left facet lit, the right one dark, rim light on its right edge);
  a plain cone down to row 34 (11 pixels wide), then in tiers like stacked arrowheads: three light bands run like a
  ^ from the crease down and out to the sides (from row 31 to the step at row 35, from 37 to the step at 42, from 41
  to row 46 at the side), each tier's outline a step wider (13, 15, then 19 pixels from row 43); its end rounds off
  at rows 51-54, a round knob at the bottom of the crease (columns 9-14 of rows 46-51) like the ingots' dome;
- the tail (131): a ribbed shell like a shield, 21 pixels at its widest (rows 11-15), with the crease down its middle
  and ribs along its sides, tapering to a point at column 12 of row 25; at its front (rows 0-3) a small dome, at its
  shoulders (columns 2-4 and 20-22 of rows 5-7) two little hooks curling out.

Built for the game's camera (20 degrees off straight down, from the bottom of the screen), in the segments' frame:
bronze_yuanbao is drawn centred in height (its bounds' middle on the layer: z 2.175 of its own frame), so z = 0
here is the segments' middle height. The head's pieces are origin models (their z = 0 on the layer); the tail is drawn
centred in height too, and its bounds are centred on z = 0 (its underside as deep as its crease is high), so all
three lie at one height. The ingots reach z 5.3 at their crease and nest like cups: each one's bottom sits in the
dish of the one below, inside its horns, the lower one's dome peeking out under it.
- The head is one loft from its point to its end, its sections creased superellipses (two facets meeting at the
  crease, rounded over the sides, a flatter underside), along chevron lines (each section's sides lie SLOPE further
  down the screen than its middle), so that the tiers' ledges follow the sprite's ^ bands: at each ledge the
  section steps wider and higher over a short slope that faces up the screen and catches the sun (the sprite's
  light bands); the outline follows the sprite's. Its top rises from the point towards the tiers and is highest on
  the last (z 5.7, the segments' crease height), and the end dives into the first segment's dish: the head's knob
  (an ingot's dome on the crease) rests where the segment's dome is, in front of it, and the head's end goes behind
  the segment's front, the segment's horns round its sides. Cut along the sprites' edge (y = 14) into its two
  pieces, each moved to its sprite's centre (the pieces keep the whole's shading across the cut).
- The tail is an ingot's top on a long shell: the shell a loft of creased sections with a groove and a rib along
  each side (they meet at the point; the groove three shades darker than its facet, the rib's crest lit on the
  left), its front a shallow dish between its shoulders, the dome standing in the dish (both mostly behind the last
  segment's front, as the sprite's dome is under it, and coming out when the worm sways), the hooks curling up and
  in at the shoulders beside the segment's bottom, where the sprite draws them, as the ingots' horns curl. Its top
  is low (z 3.6 at the dish's rim, under the segment's front) and its crease highest (z 5.1) over its widest part.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera. The head is built
with the base sprite's centre as origin (its pixel 12, 14; the tip's centre is 28 up); the sprites are symmetric
about x = 0.5 (column 12's middle), as the ingot is. Row r of the head's picture is y = 41.5 - r; row r of the tail is
y = 13.5 - r.

Replaces wave3_ad.py's worm (its sections "# --- H 17 / 55: the worm's head" (HEAD, worm_head() and the
kit.pieced("gyges_worm_head", ...) registration) and "# --- H 131: the worm's tail" (TAIL, worm_tail()), bronze_painter()
and the docstring's two worm paragraphs) and wave3_ad_art.py's BRONZE_HEAD and BRONZE_TAIL (only those sections read
them; BRONZE_SEG nothing reads).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes of the
whole head, of each piece and of the tail against enemy_H.png), --preview <prefix> (each model's top and 3/4 views,
and the whole worm as GYGES lays it out, with five bronze_yuanbao segments built by polish_yuanbao.py), --only
<name,...> (models to export), --whole <file.glb> (the uncut head, for looking at), --chain <file.glb> (the whole
worm, for looking at).
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
import polish_machine_kit as mk  # noqa: E402
from polish_jets import Curve  # noqa: E402

AXIS_X = 0.5            # the sprites' middle (column 12's middle)
SEGMENTS = 5            # the chain (for the previews): five segments 10 pixels apart, the first 10 below the head
SEGMENT_STEP = 10.0     # base's middle, the tail's middle 60 below it
TAIL_BELOW = 60.0

# --- The head --------------------------------------------------------------------------------------------------

# The head's outline: half-widths about AXIS_X by height y (the sprite's rows, their edge pixels half covered).
HEAD_OUTLINE = Curve([(28.05, 0.0), (27.5, 0.4), (26.0, 1.1), (24.0, 2.0), (22.0, 2.85), (20.0, 3.6), (18.0, 4.3),
                      (16.5, 4.85), (15.0, 5.3), (13.5, 5.45), (7.6, 5.45), (6.5, 6.4), (5.5, 7.35), (0.5, 7.45),
                      (-0.5, 8.4), (-1.5, 9.35), (-8.0, 9.45), (-9.0, 9.2), (-9.7, 8.4), (-10.2, 7.1), (-10.7, 6.2),
                      (-11.5, 5.4), (-12.5, 4.3), (-12.95, 2.6), (-13.1, 0.0)])
SLOPE = 0.6             # the chevrons: a section's sides lie this much (times their distance out) below its middle
# Where the sections leave the chevron for straight across (towards the rounded end): from y = 0.5 to -9.5.
SLOPE_FADE = (0.5, -9.5)
# The ledges: (the middle's height, its slope's length along the middle). Each ledge is the sprite's light band; under
# it the next tier, a step wider (the outline's steps) and higher.
LEDGES = [(10.0, 1.0), (4.5, 1.0), (0.5, 0.9)]
LEDGE_LIGHT = 0.75      # the light band goes on this far below each ledge (along the middle), over the tier's roll
# The tiers' crease lines (z by the middle's y), from the point down: the plain cone, two narrow tiers, the last and
# widest, highest under its ledge and diving into the first segment's dish towards the end. Each tier falls a little
# down the screen from its ledge (its face turned from the sun, darker, as the sprite shades it) and reaches a little
# past its ledges; the ledges blend one into the next over their slopes.
TIERS = [Curve([(28.1, 0.5), (26.0, 1.15), (22.0, 2.05), (18.0, 2.75), (14.0, 3.3), (10.5, 3.7), (9.0, 3.8)]),
         Curve([(11.0, 4.62), (9.5, 4.66), (7.0, 4.58), (4.0, 4.45)]),
         Curve([(5.0, 5.25), (4.0, 5.3), (2.0, 5.22), (-0.5, 5.12)]),
         Curve([(1.0, 5.72), (0.0, 5.75), (-1.5, 5.62), (-3.0, 5.3), (-4.5, 4.75), (-6.0, 3.95), (-7.5, 3.1),
                (-9.0, 2.3), (-10.5, 1.6), (-12.0, 0.9), (-13.1, 0.15)])]
# The underside's depth (z below the axis) by the middle's y: no steps.
HEAD_UNDER = Curve([(28.1, 0.3), (26.0, 0.9), (22.0, 1.6), (18.0, 2.2), (14.0, 2.65), (10.0, 3.0), (4.5, 3.45),
                    (0.5, 3.8), (-3.0, 3.9), (-6.0, 3.4), (-9.0, 2.4), (-11.0, 1.5), (-12.5, 0.7), (-13.1, 0.1)])
TENT = 0.24             # the crease's tent: this share of the top's height, over TENT_REACH of the half-width
TENT_REACH = 0.85
SECTION_POWER = 2.6     # the sections' superellipse
SECTION_POINTS = 44
# The knob at the end of the crease: its middle, half-sizes (x, y) and its top's height; sunk into the head.
KNOB = ((AXIS_X, -8.6), (3.45, 3.35), 5.0, 2.6)

# --- Materials --------------------------------------------------------------------------------------------------

def materials():
    """bronze_yuanbao's: the same palette shades and finish (polish_yuanbao.materials), and a cap colour for the cuts
    (the bronze's inside)."""
    bronze = dict(metallic=0.5, roughness=0.2)
    return {
        "bronze": k.material("worm_bronze", palette=0x19, **bronze),
        "shade": k.material("worm_shade", palette=0x16, **bronze),
        "rim": k.material("worm_rim", palette=0x1c, metallic=0.5, roughness=0.16),
        "dish": k.material("worm_dish", palette=0x13, metallic=0.45, roughness=0.3),
        "under": k.material("worm_under", palette=0x15, **bronze),
        "dome": k.material("worm_dome", palette=0x1a, metallic=0.5, roughness=0.14),
        "cap": k.material("worm_cap", palette=0x14, metallic=0.4, roughness=0.4),
    }


def smoothstep(e0, e1, x):
    t = min(1.0, max(0.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


# --- Sections ---------------------------------------------------------------------------------------------------

def superellipse(t, power):
    c, s = math.cos(t), math.sin(t)
    return math.copysign(abs(c) ** (2 / power), c), math.copysign(abs(s) ** (2 / power), s)


def head_slope(yc):
    """The chevron's slope of the section whose middle lies at yc."""
    a, b = SLOPE_FADE
    return SLOPE * smoothstep(b, a, yc)


def head_top(yc):
    """The crease line's height at the section whose middle lies at yc: the tiers' lines, each ledge blending one
    into the next over its slope."""
    z = TIERS[0](yc)
    for (top, length), tier in zip(LEDGES, TIERS[1:]):
        z += (tier(yc) - z) * smoothstep(top + 0.5 * length, top - 0.5 * length, yc)
    return z


def head_width(yc):
    """The section's half-width: its sides (SLOPE x half-width below its middle) on the sprite's outline."""
    w = HEAD_OUTLINE(yc)
    s = head_slope(yc)
    for _ in range(30):
        w = 0.5 * w + 0.5 * HEAD_OUTLINE(yc - s * w)
    return w


def head_section(yc):
    """The section whose middle lies at yc: points round it from the crease (its top's middle, the first point) over
    the left side, the underside and the right side."""
    w = head_width(yc)
    s = head_slope(yc)
    top = head_top(yc)
    under = HEAD_UNDER(yc)
    points = []
    for j in range(SECTION_POINTS):
        t = math.pi / 2 + 2 * math.pi * j / SECTION_POINTS
        u, v = superellipse(t, SECTION_POWER)
        x = AXIS_X + w * u
        y = yc - s * w * abs(u)
        if v >= 0:
            tent = max(0.0, 1.0 - abs(u) / TENT_REACH)
            z = top * ((1 - TENT) * v + TENT * tent * v)
        else:
            z = under * v
        points.append(Vector((x, y, z)))
    return points


def head_stations():
    """The sections' middles from the point to the end: every 0.55 pixels, closer at the ledges (a section at each
    end of a ledge's slope) and towards the ends."""
    ys = [27.95, 27.7, 27.35, 26.9]
    y = 26.4
    while y > -12.75:
        ys.append(y)
        y -= 0.55
    for top, length in LEDGES:
        band = top - 0.5 * length - LEDGE_LIGHT
        ys = [v for v in ys if abs(v - top) > 0.5 * length + 0.12 and abs(v - band) > 0.2]
        ys += [top + 0.5 * length, top + 0.25 * length, top - 0.25 * length, top - 0.5 * length, band]
    ys += [-12.75, -12.95, -13.05]
    return sorted(set(round(v, 4) for v in ys), reverse=True)


def head_body(m):
    rings = [head_section(yc) for yc in head_stations()]
    obj = k.loft("head_body", rings, None, start_point=(AXIS_X, 28.12, 0.45), end_point=(AXIS_X, -13.12, 0.0))
    for key in ("bronze", "shade", "rim", "under"):
        obj.data.materials.append(m[key])
    n = SECTION_POINTS
    ledge_rows = set()
    stations = head_stations()
    for i in range(len(stations) - 1):
        for top, length in LEDGES:
            if top - 0.5 * length - LEDGE_LIGHT - 1e-6 <= stations[i + 1] and stations[i] <= top + 0.5 * length + 1e-6:
                ledge_rows.add(i)
    for poly in obj.data.polygons:
        c, nrm = poly.center, poly.normal
        i = poly.index // n
        if poly.index >= (len(rings) - 1) * n:      # the end fans
            i = 0 if poly.index < (len(rings) - 1) * n + n else len(rings) - 2
        if nrm.z < -0.25:
            poly.material_index = 3
        elif i in ledge_rows and nrm.z > 0.3:
            poly.material_index = 2 if c.x < AXIS_X else 0     # the band: lit on the left, the bronze on the right
        elif c.x > AXIS_X + 0.02:
            poly.material_index = 1
        else:
            poly.material_index = 0
    # The crease: the edges along its points sharp, so that the two facets meet in a line.
    mesh = obj.data
    for e in mesh.edges:
        a, b = e.vertices
        if a < len(rings) * n and b < len(rings) * n and a % n == 0 and b % n == 0:
            e.use_edge_sharp = True
    return k.smooth(obj, 48)


def head_knob(m):
    """The ingot's dome at the end of the crease: a rounded cap (a superellipse profile turned round its axis)
    standing in the head, its foot sunk."""
    (cx, cy), (rx, ry), top, height = KNOB
    rings = []
    count = 12
    for i in range(count):
        t = i / count
        s = (1 - t ** 2.2) ** (1 / 2.2)
        z = top - height + height * t
        rings.append([Vector((cx + rx * s * math.cos(2 * math.pi * j / 36),
                              cy + ry * s * math.sin(2 * math.pi * j / 36), z)) for j in range(36)])
    obj = k.loft("head_knob", rings, m["dome"], start_point=(cx, cy, top - height), end_point=(cx, cy, top))
    return k.smooth(obj, 60)


def build_head(m):
    return [head_body(m), head_knob(m)]


# --- The tail --------------------------------------------------------------------------------------------------

# The shell's outline (half-widths about AXIS_X by y; the hooks apart): its rounded top where the dome stands, the
# collar at its front (rows 5-8) with the small notch under it (row 9), the widest part (rows 11-15), the taper to
# the point (rows 16-25).
TAIL_OUTLINE = Curve([(9.85, 0.0), (9.78, 4.6), (9.55, 7.5), (9.1, 8.55), (8.5, 8.9), (7.5, 9.05), (6.5, 9.2),
                      (5.5, 9.35), (4.6, 8.85), (3.6, 9.45), (2.5, 10.35), (-1.5, 10.4), (-3.0, 9.45), (-5.0, 8.45),
                      (-6.5, 7.4), (-7.5, 6.4), (-8.5, 5.4), (-9.5, 4.35), (-10.3, 2.6), (-10.9, 1.25), (-11.5, 0.5),
                      (-11.95, 0.0)])
# The crease line's height (z by y: highest over the widest part, as the segments' crease; low at the top, which
# lies behind the last segment's front) and the underside's depth, as deep as the crease is high (the tail's bounds
# are centred on z = 0 like the ingot's, so it lies at the segments' height whether drawn at its origin or centred).
TAIL_TOP = Curve([(9.85, 1.2), (9.6, 2.4), (9.1, 3.3), (8.0, 3.85), (7.0, 4.3), (5.0, 4.8), (2.0, 5.1), (0.0, 5.1),
                  (-3.0, 4.7), (-6.0, 3.9), (-9.0, 2.7), (-11.0, 1.4), (-11.95, 0.45)])
TAIL_UNDER = Curve([(9.85, 0.6), (9.1, 2.9), (7.0, 4.2), (2.0, 5.1), (-3.0, 4.7), (-7.0, 3.5), (-10.0, 1.9),
                    (-11.95, 0.3)])
# The ribs along the shell's sides: (where across the half-width, height (negative: a groove), width across, as
# shares of the half-width); they fade out towards the top (from RIB_FADE[0] to [1]) and at the point. The groove
# parts the lit facet by the crease from the flank, whose rounded rib catches the light, as the sprite draws them.
RIBS = [(0.5, -0.045, 0.085), (0.78, 0.06, 0.11)]
RIB_FADE = (7.0, 4.8)
# The dish at the shell's front between its shoulders, where the dome stands: its depth by y, falling off across.
TAIL_DISH = Curve([(5.8, 0.0), (7.0, 0.6), (8.3, 1.45), (9.3, 1.9), (9.85, 1.2)])
TAIL_POINTS = 48
# The dome at the front: its middle (x, y, z) and half-sizes; mostly behind the last segment's front.
TAIL_DOME = ((AXIS_X, 10.6, 0.9), (6.4, 3.35, 3.35))
# The hooks at the shoulders (the left one, x from AXIS_X; the right one mirrored): points along it from its root on
# the collar's side up the screen to its tip, curling in at the top as the yuanbao's horns do, and its thickness.
HOOK = [(-9.05, 5.3, 2.0), (-9.2, 6.25, 2.35), (-8.9, 7.2, 2.65), (-8.35, 8.0, 2.85), (-7.75, 8.65, 2.95)]
HOOK_R = [0.8, 0.75, 0.62, 0.45, 0.22]


def tail_section(y):
    """The shell's section at y: points round it from the crease over the left side, the underside and the right
    side; the share of each point's height that is rib (for the paint)."""
    w = TAIL_OUTLINE(y)
    top, under = TAIL_TOP(y), TAIL_UNDER(y)
    rib_on = smoothstep(RIB_FADE[0], RIB_FADE[1], y) * smoothstep(-11.6, -9.5, y)
    points, ribs = [], []
    for j in range(TAIL_POINTS):
        t = math.pi / 2 + 2 * math.pi * j / TAIL_POINTS
        u, v = superellipse(t, SECTION_POWER)
        x = AXIS_X + w * u
        if v >= 0:
            tent = max(0.0, 1.0 - abs(u) / TENT_REACH)
            z = top * ((1 - TENT) * v + TENT * tent * v)
            bumps = [h * math.exp(-((abs(u) - at) / width) ** 2) * rib_on for at, h, width in RIBS]
            z += sum(bumps) * w * v
            z -= TAIL_DISH(y) * max(0.0, 1.0 - u * u / 0.55) ** 2 * v
            ribs.append(bumps[1] / RIBS[1][1] - bumps[0] / RIBS[0][1])
        else:
            z = under * v
            ribs.append(0.0)
        points.append(Vector((x, y, z)))
    return points, ribs


def tail_stations():
    ys = [9.82, 9.75, 9.62, 9.45, 9.25, 9.0]
    y = 8.6
    while y > -11.6:
        ys.append(y)
        y -= 0.5
    ys += [-11.6, -11.8, -11.9]
    return ys


def tail_shell(m):
    stations = tail_stations()
    sections = [tail_section(y) for y in stations]
    rings = [pts for pts, _ in sections]
    obj = k.loft("tail_shell", rings, None, start_point=(AXIS_X, 9.9, 0.9), end_point=(AXIS_X, -11.98, 0.4))
    for key in ("bronze", "shade", "rim", "under", "dish"):
        obj.data.materials.append(m[key])
    n = TAIL_POINTS
    for poly in obj.data.polygons:
        c, nrm = poly.center, poly.normal
        rib = 0.0
        if poly.index < (len(rings) - 1) * n:
            i, j = divmod(poly.index, n)
            rib = min(sections[i][1][j], sections[i][1][(j + 1) % n], sections[i + 1][1][j],
                      sections[i + 1][1][(j + 1) % n])
        if nrm.z < -0.25:
            poly.material_index = 3
        elif rib > 0.55:
            poly.material_index = 2 if c.x < AXIS_X else 0     # the flank's rib: lit on the left
        elif rib < -0.7:
            poly.material_index = 1 if c.x < AXIS_X else 4      # the groove, three shades darker than its facet
        elif c.x > AXIS_X + 0.02:
            poly.material_index = 1
        else:
            poly.material_index = 0
    mesh = obj.data
    for e in mesh.edges:
        a, b = e.vertices
        if a < len(rings) * n and b < len(rings) * n and a % n == 0 and b % n == 0:
            e.use_edge_sharp = True
    return k.smooth(obj, 48)


def tail_dome(m):
    """The dome at the shell's front: an ellipsoid lofted from explicit rings (the same every run), its lower part
    inside the shell."""
    (cx, cy, cz), (rx, ry, rz) = TAIL_DOME
    rings = []
    count = 14
    for i in range(1, count):
        a = math.pi * i / count - math.pi / 2           # from the bottom up
        r, z = math.cos(a), math.sin(a)
        rings.append([Vector((cx + rx * r * math.cos(2 * math.pi * j / 40), cy + ry * r * math.sin(2 * math.pi * j / 40),
                              cz + rz * z)) for j in range(40)])
    obj = k.loft("tail_dome", rings, m["dome"], start_point=(cx, cy, cz - rz), end_point=(cx, cy, cz + rz))
    return k.smooth(obj, 60)


def tail_hooks(m):
    hooks = []
    for side in (-1, 1):
        pts = [(AXIS_X - side * dx, y, z) for dx, y, z in HOOK]
        obj = mk.tube("tail_hook%d" % side, pts, 0.0, m["bronze"], segments=10, radii=HOOK_R)
        hooks.append(k.smooth(obj, 60))
    return hooks


def build_tail(m):
    return [tail_shell(m), tail_dome(m)] + tail_hooks(m)


# --- Checks, cutting, export ------------------------------------------------------------------------------------

def triangulate(objects):
    """Every face split into triangles (the same split every run, the custom normals kept), so that the export
    doesn't split the n-gons itself (polish_k_pod.triangulate)."""
    for obj in objects:
        mod = obj.modifiers.new("triangulate", "TRIANGULATE")
        mod.quad_method = "BEAUTY"
        mod.ngon_method = "BEAUTY"
        mod.min_vertices = 4
        mod.keep_custom_normals = True
        mk.apply(obj)
    return objects


def join(objects, name):
    if len(objects) == 1:
        objects[0].name = objects[0].data.name = name
        return objects[0]
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.join()
    obj = bpy.context.view_layer.objects.active
    obj.name = name
    obj.data.name = name
    return obj


def mask_of(sheet, sprites):
    """The sprites' masks stacked as the level lays them (sprites: rows of sprite numbers, top first)."""
    rows = []
    for sprite in sprites:
        rows += k.sprite_mask(sheet, sprite)
    return rows


def chain(options):
    """The whole worm as GYGES lays it out (head, five segments, tail), each at the height the game draws it: the
    segments (polish_yuanbao.py's ingot) centred in height on their bounds, head and tail as built."""
    import polish_yuanbao as yb
    k.reset()
    seg_mats = yb.materials()
    yb.body(seg_mats)
    yb.dome(seg_mats)
    yb.place()
    segment = join(mk.meshes(), "segment")
    low, high = mk.bounds([segment])
    mk.transform([segment], Matrix.Translation((0.0, 0.0, -(low.z + high.z) / 2)))
    print("   chain: the segment's bounds' middle at z %.3f of its own frame" % ((low.z + high.z) / 2))
    parts = [segment]
    for i in range(1, SEGMENTS):
        copy = segment.copy()
        copy.data = segment.data.copy()
        bpy.context.scene.collection.objects.link(copy)
        mk.transform([copy], Matrix.Translation((0.0, -SEGMENT_STEP * i, 0.0)))
        parts.append(copy)
    mk.transform([segment], Matrix.Translation((0.0, -SEGMENT_STEP, 0.0)))
    mk.transform(parts[1:], Matrix.Translation((0.0, -SEGMENT_STEP, 0.0)))
    m = materials()
    head = build_head(m)
    tail = build_tail(m)
    mk.transform(tail, Matrix.Translation((0.0, -TAIL_BELOW, 0.0)))
    objects = parts + head + tail
    triangulate(objects)
    bpy.context.scene.view_settings.view_transform = "Standard"
    if "chain" in options:
        mk.export(objects, options["chain"])
    if "preview" in options:
        mk.preview(options["preview"] + "gyges_worm_chain", objects, size=(28, 116), scale=8, distance=2.2,
                   centre=(0.0, -16.0))


def build():
    options = k.args()
    out = mk.outdir(options)
    only = set(options["only"].split(",")) if "only" in options else None
    sheet = None
    if "check" in options:
        sheets = options["check"]
        sheet = os.path.join(sheets, "enemy_H.png") if os.path.isdir(sheets) else sheets
    k.reset()
    m = materials()
    head = build_head(m)
    triangulate(head)
    bpy.context.scene.view_settings.view_transform = "Standard"
    if sheet:
        mk.compare("head, whole (H 17 above 55)", mk.coverage(head, 24, 56, centre=(0.0, 14.0)),
                   mask_of(sheet, [17, 55]))
    if "whole" in options:
        mk.export(head, options["whole"])
    if "preview" in options:
        # Of copies: the preview moves what it shows to the frame's middle and back, which would change the head's
        # coordinates in their last bits (and the pieces cut from it).
        copies = []
        for obj in head:
            copy = obj.copy()
            copy.data = obj.data.copy()
            bpy.context.scene.collection.objects.link(copy)
            copies.append(copy)
        for obj in head:
            obj.hide_render = True
        mk.preview(options["preview"] + "gyges_worm_head", copies, size=(24, 56), scale=12, distance=1.4,
                   centre=(0.0, 14.0))
        for obj in copies:
            bpy.data.objects.remove(obj)
        for obj in head:
            obj.hide_render = False
    for name, sprite, box, centre in (("gyges_worm_head_tip", 17, (-12.0, 12.0, 14.0, 42.0), (0.0, 28.0)),
                                      ("gyges_worm_head_base", 55, (-12.0, 12.0, -14.0, 14.0), (0.0, 0.0))):
        if only is not None and name not in only:
            continue
        parts = [p for p in (mk.cut(src, box, m["cap"]) for src in head) if p is not None]
        mk.transform(parts, Matrix.Translation((-centre[0], -centre[1], 0.0)))
        triangulate(parts)
        piece = join(parts, name)
        for src in head:
            src.hide_render = True
        if sheet:
            mk.compare("%s (H %d)" % (name, sprite), mk.coverage([piece], 24, 28), k.sprite_mask(sheet, sprite))
        mk.report(name, [piece], os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, [piece])
        bpy.data.objects.remove(piece)
        for src in head:
            src.hide_render = False
    for obj in head:
        bpy.data.objects.remove(obj)
    if only is None or "gyges_worm_tail" in only:
        tail = triangulate(build_tail(m))
        tail = [join(tail, "gyges_worm_tail")]
        if sheet:
            mk.compare("gyges_worm_tail (H 131)", mk.coverage(tail, 24, 28), k.sprite_mask(sheet, 131))
        low, high = mk.bounds(tail)
        print("   gyges_worm_tail: bounds' middle at z %.3f (0: drawn centred, it lies at the segments' height)" % (
            (low.z + high.z) / 2))
        mk.report("gyges_worm_tail", tail, os.path.join(out, "gyges_worm_tail.glb"))
        if "preview" in options:
            mk.preview(options["preview"] + "gyges_worm_tail", tail)
    if "chain" in options or "preview" in options:
        chain(options)


if __name__ == "__main__":
    build()
