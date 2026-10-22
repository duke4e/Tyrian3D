"""The eye sphere of LAVA RUN (in the sky) and EYESPY (on the top layer): sheet 9 sprites 153 155 157 / 191 193 195 /
210 212 214 (2x2 each), one 72 x 70 picture; polished (2026-10-22, round 36), rebuilt from solids (2026-10-23, round 38:
round 36's was one heightfield painted from the sprite's pixels, its iris pixel blocks). It replaced wave3_aj_eye.py.

Where the levels put it (the enemy events): nine pieces as the sheet lays them out, 153 155 157 at (x, y - 56), (x + 24,
y - 56), (x + 48, y - 56), 191 193 195 28 pixels lower, 210 212 214 14 pixels lower still (their boxes overlap 191-195's
lower half): episode 4's enemies 327-335, LAVA RUN t2800 (event 15, the sky) and EYESPY t4400 (event 7, the top
layer). One frame each, no damaged look, nothing launched; 333 and 335 (210, 214) have armour 0 (shots pass through),
the rest 255; 334 (212) fires. The overlapping rows 42-55 are kept by 210-214 (191-195 keep rows 28-41). No other
sprite of any sheet is these pixels mirrored, turned or in other ramps (the ball is round, 97.5 % its own mirror image
in outline, but its plates and lighting are not); no other enemy shows them; episode 6's EYESPY and LAVA RUN waves
(DELI RUIN, GLACIER, ROOST) don't hold it.

As the sprites and their 4x upscales draw it (the picture's columns and rows; lit from the upper left): a big steel ball
(columns 0-71, rows 0-68) of grey armour plates (ramp 0) with dark seams: a seam round its waist above the eye (rows
27-29), seams from its top down to it (columns 24-38 and 50-54), one across its upper right (to column 70 at row 24); on
its upper left a raised silver plate (bright greys, columns 14-37 of rows 8-28) with rounded bosses, on its upper right
a curved strip of light blue glass set into it (ramp 8, columns 36-50 of rows 9-26); a piston on each side above the eye
(columns 5-17 of rows 28-42 and 55-67 of rows 28-42: a grey sleeve, a bright rod, its end on the eye's rim); on its
lower front a great glass eye (columns 15-57 of rows 36-65) in a dark steel rim: a light blue iris (ramps 8 and 9) with
radial fibres, deep blue (ramp 3) at its rim, a black pupil (columns 29-39 of rows 46-57, left of the middle) and dark
crosshairs through it (column 36, row 51).

Built from solids (polish_sheet9_solids): the core a dark ball (an ellipsoid lofted from explicit rings); over it nine
armour plates (shell plates over smooth outlines traced from the sprite's seams, each 1.8 over the ball with a 0.9
quarter-round bevel, 0.84 apart: the core shows in the seams and as the dark outline); the silver plate a thicker plate
over the upper left one with two machined bosses and a knob; the glass strip a glass slab sunk in a hole of its plate
(a dark gasket round it); the eye's rim a lofted ring standing proud of the plates with sixteen rivets; the eye a glass
cap bulging from the ball, meshed round its pupil (rings out to the rim, so its bands are clean curves: a pale wavy
collarette, the teal iris with bright blue fibres and navy crypts curling a little, a navy outer band, the limbus sunk
in a groove under the rim, the pupil sunk and glossy black), two thin dark wires across it (the crosshairs); the
pistons turned parts (a sleeve with a collar, a chrome rod down to the eye's rim, pins across both ends) on machined
mounts; rivets along the waist seam. Materials by part (palette indices of the sprite's ramps): the plates 0x08, the
core, seams and cuts 0x02, the silver plate 0x0c and its bosses 0x0b, the rim 0x04, rivets and pins 0x0a, sleeves
0x07, rods 0x0e, the strip's glass 0x85 (glowing 0.2), the iris 0x84 / fibres 0x9d / collarette 0x9e (glowing
0.16-0.26), crypts 0x36, the outer band 0x37 (0.1), the limbus 0x34, the pupil 0x61, the wires 0x02.

Built TALL (30) high, as round as the sprite paints it, and flattened to FLAT of that with its built normals kept
(turned ROUNDER times rounder still; polish_sheet9_solids.flatten): the game's camera sees it shaded as a ball while it
stays as low as round 36's (z 0 to 13.3; the old ball of round 35 rose 32 pixels, through the player's plane on the top
layer). Then cut along the sprites' edges (the cuts capped in the core's colour), sheared along the camera's line of
sight, each piece moved to its origin.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera (z 0: the base, its
layer's plane). The whole's origin is the picture's middle (column 36, row 35): column c's left edge is x = c - 36, row
r's top edge y = 35 - r; a piece whose sprite's top left pixel is (c0, r0) has its origin at (c0 - 24, 21 - r0)
(models.cfg origin).

models.cfg: the nine model and sprite lines stay as they are (eye_sphere_<sprite> ... origin; yaw=0).

Replaces round 36's version of this script (its heightfield, polish_sheet9_kit's Plate and Painter); wave3_aj_eye.py is
already gone.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each piece's outline as the
camera sees it against its sprite's pixels), --preview <prefix> (the whole: top and 3/4 views; --pieces 1: each piece),
--only <name,...>, --dump <file.json> (the plates' outlines, for a look over the sprite).
"""
import json
import math
import os
import sys

from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
import polish_sheet9_solids as ss  # noqa: E402

LEFT, TOP = -36.0, 35.0
BALL_C = (36.1, 34.7)              # the ball's middle (column, row) and radii
BALL_R = (35.9, 34.3)
TALL = 30.0                        # its height as built
FLAT = 0.39                        # ... flattened to this of it
KEEP = 1.0                         # how much of the built normals the flattened ball keeps
ROUNDER = 1.4                      # ... turned as if it were this much taller still (rounder than a sphere)
CORE_SINK = 1.0                    # the core under the plates' foot
THICK, BEVEL, GAP = 1.8, 0.9, 0.42 # the plates: over the ball, their edge's rounding, half the seam
RIM_INSET = 0.38                   # the plates stop this far inside the ball's outline (the core's dark rim)
CORNER = 1.3                       # the plates' corners rounded over this (more than their bevel)
SILVER = (1.7, 0.85)               # the silver plate over its plate: thickness, rounding
GLASS_UP, GLASS_GAP = 0.8, 0.6     # the glass strip's top over the ball, its gap in the plate
EYE_C = (36.5, 50.5)               # the eye (column, row), its glass's radii, the rim's outer radii
EYE_R = (20.4, 13.8)
BEZEL_R = (22.5, 15.7)
EYE_LIFT, BULGE = 0.6, 4.6         # the eye's rim over the ball, its crown over that
PUPIL = ((34.4, 51.4), 4.9, 1.3)   # middle (column, row), radius, how deep it is sunk
GROOVE = (0.9, 1.0, 0.9)           # the limbus groove: from, to (t of the glass's mesh), depth
COLLARETTE = (0.16, 0.02, 12)     # the pale ring round the pupil: its edge (t), how far it waves, how many waves
OUTER = (0.76, 0.025, 15)          # the iris's dark outer band from here (waving likewise)
LIMBUS = 0.93                      # the navy limbus from here to the rim
FIBRES = 48                        # radial fibres round the iris (light ones, every fourth a dark crypt)
TWIST = 9.0                        # degrees the fibres curl from the pupil to the rim
WIRES = (36.6, 50.9, 0.42, 0.45)   # the crosshairs: column, row, half width, over the glass
PISTONS = [((7.9, 29.9), (16.9, 41.3)), ((64.3, 30.3), (56.1, 41.7))]   # upper and lower pivots (column, row)
SLEEVE_R, ROD_R = 2.35, 1.0

# The seams (column, row), from end to end; * ends lie on the ball's outline (o) or the rim's (b).
SEAMS = {
    "eq1": [("o", 0.3, 29.2), (6.0, 28.4), (13.6, 28.0)],
    "eq2": [(13.6, 28.0), (19.0, 28.05)],
    "eq3": [(19.0, 28.05), (27.0, 28.25), (38.0, 28.45)],
    "eq4": [(38.0, 28.45), (46.0, 28.5), (53.6, 28.55)],
    "eq5": [(53.6, 28.55), (60.0, 29.1), (66.0, 29.9), ("o", 72.0, 30.8)],
    "sa": [("o", 25.0, 1.9), (29.0, 5.0), (33.0, 8.6), (36.4, 12.0), (37.8, 17.0), (38.0, 22.0), (38.0, 28.45)],
    "sb": [("o", 2.8, 21.0), (7.5, 21.9), (11.4, 24.0), (13.6, 28.0)],
    "sc1": [("o", 50.0, 2.9), (51.3, 8.0), (52.0, 13.0)],
    "sc2": [(52.0, 13.0), (52.5, 19.0), (52.9, 24.0), (53.6, 28.55)],
    "sd": [(52.0, 13.0), (57.0, 14.6), (62.0, 17.6), (66.2, 21.4), ("o", 70.8, 24.5)],
    "sl": [(19.0, 28.05), (20.3, 33.4), ("b", 21.6, 38.6)],
    "sr": [(53.6, 28.55), (52.6, 33.8), ("b", 51.4, 38.8)],
    "sbl": [("b", 23.6, 63.3), ("o", 20.5, 65.8)],
    "sbr": [("b", 49.4, 63.3), ("o", 52.5, 65.6)],
}
# The plates: their outlines as seams (+ forwards, - backwards) and arcs of the outline (o) or the rim (b) between them,
# counter-clockwise (ccw) or clockwise (cw) on the screen.
PLATES = {
    "top_left": [("o", "ccw"), "+sb", "+eq2", "+eq3", "-sa"],
    "low_left": [("o", "ccw"), "+eq1", "-sb"],
    "top": [("o", "ccw"), "+sa", "+eq4", "-sc2", "-sc1"],
    "top_right": [("o", "ccw"), "+sc1", "+sd"],
    "right": [("o", "ccw"), "-sd", "+sc2", "+eq5"],
    "brow": ["+eq3", "+eq4", "+sr", ("b", "ccw"), "-sl"],
    "cheek_left": ["-eq2", "-eq1", ("o", "ccw"), "-sbl", ("b", "cw"), "-sl"],
    "cheek_right": ["+eq5", ("o", "cw"), "-sbr", ("b", "ccw"), "-sr"],
    "chin": ["+sbl", ("o", "ccw"), "-sbr", ("b", "cw")],
}
SILVER_PLATE = [(15.8, 11.8), (18.6, 9.6), (23.0, 8.7), (28.6, 8.8), (32.6, 10.0), (35.2, 12.6), (36.4, 16.6),
                (36.5, 21.6), (35.2, 25.2), (31.2, 27.0), (25.0, 27.2), (19.5, 26.6), (16.4, 24.6), (14.9, 20.8),
                (14.8, 15.6)]
# The silver plate's bosses: middle (column, row), radius, height (turned: a collar, a chamfer, a low crown).
BOSSES = [((26.8, 16.8), 3.4, 1.5), ((32.2, 21.4), 2.3, 1.2), ((33.9, 13.4), 1.6, 1.3)]
WINDOW = [(38.6, 10.4), (41.0, 9.4), (44.6, 10.4), (47.8, 12.8), (49.8, 16.6), (50.4, 21.6), (49.6, 25.8),
          (46.6, 26.6), (45.0, 25.4), (44.6, 21.6), (43.4, 17.6), (41.2, 14.2), (39.0, 12.4)]
RIVETS = [(3.6, 26.6), (8.6, 26.6), (58.4, 27.5), (63.6, 28.3), (68.6, 29.2),
          (3.6, 30.6), (13.6, 29.7), (24.0, 29.9), (30.0, 30.0), (36.0, 30.1), (42.0, 30.1), (48.0, 30.1),
          (58.6, 30.9), (68.4, 32.0),
          (17.4, 12.9), (16.9, 22.8), (34.8, 23.9)]
RIVET = (0.62, 0.75)               # radius, height
BEZEL_RIVETS = 16


def P(c, r):
    return (c + LEFT, TOP - r)


def ball_c():
    return P(*BALL_C)


def ball_z(x, y):
    (cx, cy), (rx, ry) = ball_c(), BALL_R
    q = 1.0 - ((x - cx) / rx) ** 2 - ((y - cy) / ry) ** 2
    return TALL * math.sqrt(max(0.0, q))


def ball_normal(x, y):
    (cx, cy), (rx, ry) = ball_c(), BALL_R
    z = max(ball_z(x, y), 0.3)
    return Vector(((x - cx) / rx ** 2, (y - cy) / ry ** 2, z / TALL ** 2)).normalized()


def eye_c():
    return P(*EYE_C)


def eye_rho(x, y):
    (ex, ey), (a, b) = eye_c(), EYE_R
    return math.hypot((x - ex) / a, (y - ey) / b)


def eye_z(x, y):
    """The eye's glass over the ball (its crown at the middle, its rim EYE_LIFT over the ball)."""
    rho = eye_rho(x, y)
    return ball_z(x, y) + EYE_LIFT + BULGE * math.sqrt(max(0.0, 1.0 - rho * rho))


def plate_top(x, y):
    return ball_z(x, y) + THICK


# --- Materials ------------------------------------------------------------------------------------------------------

def materials():
    p = ss.pal
    return {
        "plate": p("eyes_plate", 0x08, 0.25, 0.36), "core": p("eyes_core", 0x02, 0.3, 0.55),
        "silver": p("eyes_silver", 0x0c, 0.45, 0.26), "boss": p("eyes_boss", 0x0b, 0.45, 0.34),
        "rivet": p("eyes_rivet", 0x0a, 0.45, 0.3), "bezel": p("eyes_bezel", 0x04, 0.4, 0.3),
        "sleeve": p("eyes_sleeve", 0x07, 0.35, 0.32), "rod": p("eyes_rod", 0x0e, 0.6, 0.12),
        "glass": p("eyes_glass", 0x85, 0.0, 0.06, 0.2),
        "collar": p("eyes_icollar", 0x9e, 0.0, 0.08, 0.26), "iris": p("eyes_iris", 0x84, 0.0, 0.08, 0.16),
        "fibre": p("eyes_ifibre", 0x9d, 0.0, 0.08, 0.24), "crypt": p("eyes_icrypt", 0x36, 0.0, 0.1, 0.06),
        "outer": p("eyes_iouter", 0x37, 0.0, 0.1, 0.1),
        "limbus": p("eyes_limbus", 0x34, 0.0, 0.2), "pupil": p("eyes_pupil", 0x61, 0.1, 0.05),
        "wire": p("eyes_wire", 0x02, 0.5, 0.25),
    }


# --- Outlines -------------------------------------------------------------------------------------------------------

def snapped(item):
    """A seam point in the plane, snapped onto the outline (o) or the rim (b)."""
    if len(item) == 3:
        which, c, r = item
        p = P(c, r)
        if which == "o":
            return ss.on_ellipse(ball_c(), BALL_R, p)
        return ss.on_ellipse(eye_c(), BEZEL_R, p)
    return P(*item)


def seam(name):
    return ss.chaikin_open([snapped(it) for it in SEAMS[name]], 2)


def arc_between(which, p0, p1, sense):
    centre, radii = (ball_c(), BALL_R) if which == "o" else (eye_c(), BEZEL_R)
    a0, a1 = ss.angle_on(centre, radii, p0), ss.angle_on(centre, radii, p1)
    if sense == "ccw":
        while a1 <= a0:
            a1 += 360.0
    else:
        while a1 >= a0:
            a1 -= 360.0
    return ss.ellipse_arc(centre, radii, a0, a1, 0.4)


def plate_outline(spec):
    """A plate's outline: its seams in order, the arcs between them."""
    parts = []
    for item in spec:
        if isinstance(item, str):
            pts = seam(item[1:])
            parts.append(pts if item[0] == "+" else pts[::-1])
        else:
            parts.append(item)
    out = []
    n = len(parts)
    for i, part in enumerate(parts):
        if isinstance(part, tuple):
            prev = parts[i - 1]
            nxt = parts[(i + 1) % n]
            out += arc_between(part[0], prev[-1], nxt[0], part[1])[1:-1]
        else:
            out += part
    return ss.dedupe(out)


def outlines():
    """Every plate's outline (inset from its seams), the silver plate's, the window's and its hole."""
    shapes = {}
    for name, spec in PLATES.items():
        poly = ss.inset(plate_outline(spec), GAP)
        # (the plates stop RIM_INSET inside the ball's outline; corners rounded so their bevels offset cleanly)
        shapes[name] = ss.round_corners([clip_to_ball(p) for p in poly], CORNER)
    shapes["silver"] = ss.round_corners(mk.chaikin([P(c, r) for c, r in SILVER_PLATE], 2), CORNER)
    shapes["window"] = ss.round_corners(mk.chaikin([P(c, r) for c, r in WINDOW], 2), CORNER)
    shapes["window_hole"] = ss.round_corners(ss.inset(shapes["window"], -GLASS_GAP), CORNER)
    return shapes


def clip_to_ball(p):
    """A point pulled inside the ball's outline by RIM_INSET at least."""
    (cx, cy), (rx, ry) = ball_c(), BALL_R
    dx, dy = p[0] - cx, p[1] - cy
    q = math.hypot(dx / rx, dy / ry)
    lim = 1.0 - RIM_INSET / (0.5 * (rx + ry))
    if q <= lim:
        return p
    return (cx + dx * lim / q, cy + dy * lim / q)


# --- Parts ----------------------------------------------------------------------------------------------------------

def core(m, rings=18, around=96):
    """The dark ball under the plates (lofted from explicit rings: the same mesh every run)."""
    (cx, cy), (rx, ry) = ball_c(), BALL_R
    h = TALL - CORE_SINK
    stations = []
    for i in range(rings):
        a = (math.pi / 2) * i / rings
        s, z = math.cos(a), h * math.sin(a)
        stations.append([Vector((cx + s * rx * math.cos(2 * math.pi * j / around),
                                 cy + s * ry * math.sin(2 * math.pi * j / around), z)) for j in range(around)])
    obj = k.loft("eye_core", stations, m["core"], start_point=(cx, cy, 0.0), end_point=(cx, cy, h))
    return k.smooth(obj, 60)


def plates(m, shapes):
    out = []
    for name in PLATES:
        polys = [shapes[name]]
        if name == "top":
            polys.append(shapes["window_hole"])
        out.append(ss.shell_plate("eye_plate_" + name, polys[0], polys[1:], ball_z, ball_normal, THICK, BEVEL,
                                  m["plate"], m["core"]))
    return out


def boss_profile(rad, h):
    """A machined boss: a collar, a chamfer, a low crown (radius, z from its foot, sunk 0.6)."""
    return [(rad, -0.6), (rad, 0.45 * h), (0.9 * rad, 0.62 * h), (0.8 * rad, 0.7 * h), (0.6 * rad, 0.86 * h),
            (0.3 * rad, 0.97 * h), (0.001, h)]


def silver(m, shapes):
    t, b = SILVER
    obj = ss.shell_plate("eye_silver", shapes["silver"], [], plate_top, ball_normal, t, b, m["silver"], m["bezel"])
    parts = [obj]
    for i, ((c, r), rad, h) in enumerate(BOSSES):
        x, y = P(c, r)
        z = plate_top(x, y) + t
        parts.append(ss.turned_on("eye_boss%d" % i, (x, y, z), ball_normal(x, y), boss_profile(rad, h), m["boss"],
                                  segments=22, smooth=40.0))
    return parts


def window(m, shapes):
    return ss.shell_plate("eye_window", shapes["window"], [], ball_z, ball_normal, GLASS_UP, 0.5, m["glass"],
                          m["core"], edge=0.45, inner=0.9)


def rivets(m):
    out = []
    for i, (c, r) in enumerate(RIVETS):
        x, y = P(c, r)
        top = plate_top(x, y) + (SILVER[0] if i >= 14 else 0.0)
        out.append(ss.dome_on("eye_rivet%d" % i, (x, y, top), ball_normal(x, y), RIVET[0], RIVET[1], m["rivet"],
                              segments=10, steps=3, sink=0.5))
    return out


def bezel_point(phi, u):
    """A point of the rim's band at angle phi (degrees), u from its inner edge (0: over the glass's rim) out (1)."""
    (ex, ey), (a, b), (A, B) = eye_c(), EYE_R, BEZEL_R
    c, s = math.cos(math.radians(phi)), math.sin(math.radians(phi))
    x0, y0 = ex + 0.975 * a * c, ey + 0.975 * b * s
    x1, y1 = ex + A * c, ey + B * s
    return x0 + (x1 - x0) * u, y0 + (y1 - y0) * u


# The rim's section: (u from its inner to its outer edge, height over the ball).
BEZEL_SECTION = [(0.0, 0.2), (0.0, 2.2), (0.04, 2.65), (0.14, 2.95), (0.3, 3.1), (0.55, 2.95), (0.78, 2.45),
                 (0.93, 1.8), (1.0, 1.35), (1.0, -0.8)]


def bezel(m, count=128):
    sections = []
    for i in range(count):
        phi = 360.0 * i / count
        sec = []
        for u, dz in BEZEL_SECTION:
            x, y = bezel_point(phi, u)
            sec.append(Vector((x, y, ball_z(x, y) + dz)))
        sections.append(sec)
    ring = ss.loop_loft("eye_bezel", sections, m["bezel"], smooth=40.0)
    out = [ring]
    for i in range(BEZEL_RIVETS):
        phi = 360.0 * (i + 0.5) / BEZEL_RIVETS
        x, y = bezel_point(phi, 0.4)
        out.append(ss.dome_on("eye_brivet%d" % i, (x, y, ball_z(x, y) + 3.05), ball_normal(x, y), 0.55, 0.62,
                              m["rivet"], segments=10, steps=3, sink=0.5))
    return out


def ring_point(t, phi):
    """The eye's mesh round its pupil: t 0 on the pupil's edge, 1 on the glass's rim (beyond: under the rim); the
    radial lines curl TWIST degrees from the pupil to the rim."""
    (ex, ey), (a, b) = eye_c(), EYE_R
    (pc, pr), prad, _ = PUPIL
    px, py = P(pc, pr)
    f = math.radians(phi + TWIST * min(t, 1.0))
    c, s = math.cos(f), math.sin(f)
    x0, y0 = px + prad * c, py + prad * s
    x1, y1 = ex + a * c, ey + b * s
    return x0 + (x1 - x0) * t, y0 + (y1 - y0) * t


def eye_height(x, y, t):
    """The glass's height at a point of its mesh (t as ring_point's): the limbus sunk in a groove under the rim."""
    z = eye_z(x, y)
    g0, g1, gd = GROOVE
    if t > 1.0:
        return ball_z(x, y) + EYE_LIFT - gd - 0.9 * min(1.0, (t - 1.0) / 0.04)
    if t > g0:
        z -= gd * math.sin(math.pi * 0.5 * min(1.0, (t - g0) / (g1 - g0)))
    return z


def eye_rings():
    """The glass's rings: (t, wave amplitude, waves round) and the band of the faces out from each to the next."""
    c0, ca, cn = COLLARETTE
    o0, oa, on = OUTER
    rings = [((0.0, 0, 0), "collar"), ((0.05, 0, 0), "collar"), ((0.11, 0, 0), "collar"), ((c0, ca, cn), "iris"),
             ((0.25, 0, 0), "iris"), ((0.34, 0, 0), "iris"), ((0.44, 0, 0), "iris"), ((0.54, 0, 0), "iris"),
             ((0.64, 0, 0), "iris"), ((o0, oa, on), "outer"), ((0.8, 0, 0), "outer"), ((0.87, 0, 0), "outer"),
             ((LIMBUS, 0, 0), "limbus"), ((0.97, 0, 0), "limbus"), ((1.0, 0, 0), "limbus"), ((1.03, 0, 0), "limbus"),
             ((1.06, 0, 0), None)]
    return rings


def iris_key(band, j, t, around):
    """The iris's paint of the cell between angles j and j+1 starting at ring t: FIBRES fibres round it, one cell
    wide, three light (of two lengths) and a dark crypt in every four (the same every run)."""
    if band not in ("iris", "outer"):
        return band
    per = around // FIBRES
    n, at = j // per, j % per
    if at != 0:
        return band
    kind = n % 4
    if kind == 0:
        return "crypt" if 0.3 <= t < 0.85 else band
    end = 0.7 if kind != 2 else 0.5
    return "fibre" if t < end else band


def eye_mesh(m, around=144):
    """The eye's glass: rings round the pupil from its sunk floor out under the rim, faces painted by band."""
    (pc, pr), prad, sink = PUPIL
    px, py = P(pc, pr)
    verts, faces, keys = [], [], []
    floor = [1.0, 0.72, 0.42, 0.18]
    rows = []
    for f in floor:
        row = []
        for j in range(around):
            phi = math.radians(360.0 * j / around)
            x, y = px + prad * f * math.cos(phi), py + prad * f * math.sin(phi)
            row.append(len(verts))
            verts.append((x, y, eye_z(x, y) - sink))
        rows.append(row)
    centre = len(verts)
    verts.append((px, py, eye_z(px, py) - sink))
    rings = eye_rings()
    iris_rows = []
    for (t0, amp, waves), _ in rings:
        row = []
        for j in range(around):
            phi = 360.0 * j / around
            t = t0 + amp * math.sin(math.radians(waves * phi + 37.0 * t0))
            x, y = ring_point(t, phi)
            row.append(len(verts))
            verts.append((x, y, eye_height(x, y, t)))
        iris_rows.append(row)

    def quad(r0, r1, key):
        for j in range(around):
            j2 = (j + 1) % around
            faces.append((r0[j], r0[j2], r1[j2], r1[j]))
            keys.append(key(j))
    for j in range(around):
        faces.append((centre, rows[-1][j], rows[-1][(j + 1) % around]))
        keys.append("pupil")
    for r0, r1 in zip(rows[::-1][:-1], rows[::-1][1:]):
        quad(r0, r1, lambda j: "pupil")
    quad(rows[0], iris_rows[0], lambda j: "pupil")
    for i in range(len(rings) - 1):
        (t0, _, _), band = rings[i]
        quad(iris_rows[i], iris_rows[i + 1], lambda j, band=band, t0=t0: iris_key(band, j, t0, around))
    obj = k.mesh_object("eye_glass", verts, faces)
    names = []
    for key in keys:
        if key not in names:
            names.append(key)
    for key in names:
        obj.data.materials.append(m[key])
    obj.data.polygons.foreach_set("material_index", [names.index(key) for key in keys])
    obj.data.update()
    k.recalc_normals(obj)
    return k.smooth(obj, 45)


def wires(m):
    """The crosshairs: two thin dark wires over the glass, their ends under the rim."""
    c, r, hw, up = WIRES
    x0, y0 = P(c, r)
    (ex, ey), (a, b) = eye_c(), EYE_R
    out = []
    ys = [ey - b * 1.04 + i * (2.08 * b) / 48 for i in range(49)]
    xs = [ex - a * 1.04 + i * (2.08 * a) / 64 for i in range(65)]
    for name, pts in (("v", [(x0, y) for y in ys]), ("h", [(x, y0) for x in xs])):
        path = []
        for x, y in pts:
            rho = eye_rho(x, y)
            z = eye_z(x, y) if rho < 1.0 else ball_z(x, y) + EYE_LIFT
            path.append((x, y, z + up * 0.4))
        out.append(ss.tube_along("eye_wire_" + name, path, [hw] * len(path), m["wire"], around=10, squash=0.9))
    return out


def pistons(m):
    """Each piston: a sleeve with a collar on a mount at the waist seam, a chrome rod down to the eye's rim, pins
    across both ends."""
    out = []
    for i, ((c0, r0), (c1, r1)) in enumerate(PISTONS):
        x0, y0 = P(c0, r0)
        x1, y1 = P(c1, r1)
        z0 = plate_top(x0, y0) + SLEEVE_R * 0.95
        z1 = max(plate_top(x1, y1), ball_z(x1, y1) + 1.9) + ROD_R + 0.5
        p0, p1 = Vector((x0, y0, z0)), Vector((x1, y1, z1))
        L = (p1 - p0).length
        axis = (p1 - p0).normalized()
        up = ball_normal(x0, y0)
        R = SLEEVE_R
        sleeve = [(-1.0, 0.7), (-0.8, 0.75 * R), (-0.35, 0.92 * R), (0.3, R), (L * 0.42, R), (L * 0.43, R + 0.3),
                  (L * 0.49, R + 0.3), (L * 0.5, R), (L * 0.6, R), (L * 0.62, 0.72 * R), (L * 0.63, 1.2 * ROD_R)]
        out.append(ss.lathe_between("eye_sleeve%d" % i, sleeve, p0, p1, m["sleeve"], around=20, smooth=35.0, roll=up))
        rod = [(L * 0.58, ROD_R), (L - 1.0, ROD_R), (L - 0.8, 0.7 * ROD_R), (L - 0.6, 0.3)]
        out.append(ss.lathe_between("eye_rod%d" % i, rod, p0, p1, m["rod"], around=14, smooth=40.0))
        side = axis.cross(up).normalized()
        for j, (p, rad, length) in enumerate(((p0, 1.0, 5.0), (p1, 0.85, 3.2))):
            a = p - side * (length / 2)
            b = p + side * (length / 2)
            pin = [(0.0, rad * 0.6), (0.15, rad), (length - 0.15, rad), (length, rad * 0.6)]
            out.append(ss.lathe_between("eye_pin%d_%d" % (i, j), pin, a, b, m["rivet"], around=12, smooth=40.0))
        bx, by = x0 - axis.x * 0.4, y0 - axis.y * 0.4
        out.append(ss.turned_on("eye_mount%d" % i, (bx, by, plate_top(bx, by)), ball_normal(bx, by),
                                boss_profile(2.9, 1.2), m["bezel"], segments=18, smooth=40.0))
    return out


def whole(m):
    shapes = outlines()
    parts = [core(m)]
    parts += plates(m, shapes)
    parts += silver(m, shapes)
    parts.append(window(m, shapes))
    parts += rivets(m)
    parts += bezel(m)
    parts.append(eye_mesh(m))
    parts += wires(m)
    parts += pistons(m)
    return parts, shapes


PIECES = {153: ((0, 0), None), 155: ((24, 0), None), 157: ((48, 0), None),
          191: ((0, 28), (0, 14)), 193: ((24, 28), (0, 14)), 195: ((48, 28), (0, 14)),
          210: ((0, 42), None), 212: ((24, 42), None), 214: ((48, 42), None)}


def pieces():
    out = []
    for sprite, ((c0, r0), rows) in PIECES.items():
        x0, x1 = LEFT + c0, LEFT + c0 + 24
        y1 = TOP - r0
        y0 = y1 - (14 if rows is not None else 28)
        out.append(("eye_sphere_%d" % sprite, sprite, (x0, x1, y0, y1), (c0 - 24, 21 - r0), rows))
    return out


def build():
    options = k.args()
    k.reset()
    m = materials()
    parts, shapes = whole(m)
    if "dump" in options:
        json.dump({n: [list(p) for p in poly] for n, poly in shapes.items()}, open(options["dump"], "w"))
    ss.flatten(parts, FLAT, KEEP, ROUNDER)
    if "preview" in options:
        ss.whole_preview(options["preview"] + "eye_sphere", parts, (76, 74))
    sheet = os.path.join(options["check"], "enemy_9.png") if "check" in options else None
    ss.export_pieces(parts, pieces(), m["core"], options, sheet)


if __name__ == "__main__":
    build()
