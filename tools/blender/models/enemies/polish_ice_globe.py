"""The grey globe on purple legs of CAMANIS and ICESECRET (sheet 7: sprites 161, 163 above 199, 201, 2x2 each: one
48 x 56 picture; enemies 89, 90 above 87, 88 of episodes 3 and 4, on the ground: 7 in CAMANIS, 20 in ICESECRET; one
frame each, not animated), polished (2026-10-21; it replaces wave3_ac_ice.py's globe, a plain ellipsoid with tubes
for seams on lofted legs). models.cfg: model ice_globe_tl / _tr / _bl / _br enemies/ice_globe_*.glb origin
(unchanged); sprite 7 161 ice_globe_tl yaw=0 height=-4 and the same for 163, 199, 201 (see below). No other enemy
shows these sprites; none is another sprite's pixels mirrored, turned or in other ramps, and the right half is not
the left one mirrored (the sprite lights the object from the left), though the object itself is symmetric about
the middle of column 18 (x = -5.5).

The levels lay the four as a square (event 12: the enemy, the next one 24 pixels to its right and the two after them
28 pixels above): 89 (161) above 87 (199), 90 (163) above 88 (201), as the sheet arranges them, all on the ground
layer, moving together (the game lifts the four onto the terrain at one height, the terrain's under their middle).

As the sprites and their 4x upscales draw it (columns and rows of the 48 x 56 picture): a steel sphere (columns 4-32
of rows 2-27, its middle at column 18, row 16) with a white highlight at its upper left (columns 11-16 of rows 8-13)
and panel seams, each with a lit lip on one side: two running down the screen (columns 20 and 25), one across it
(row 12, from the left edge to column 20), two more down its lower left quarter (columns 9 and 13) with a short
slanting one between them (rows 15-18). Purple armour (ramp 5) holds it: an arm at each side (columns 2-4 and 32-34
of rows 15-27, lit on the left one's outer face, its top at the sphere's middle), a hip under each side of the
sphere's lower half (columns 5-9 and 27-31 of rows 21-27), and two legs reaching forward, down the screen: a broad
thigh (columns 5-16 and 20-30 of rows 25-35) with a dark channel along its middle (columns 10-11 and 25), the knee
(rows 35-36), a narrower shin (columns 9-13 and 23-27 of rows 36-40) with a lit ridge near its inner side, and a
foot (rows 41-47) whose inner toe points in towards the other's (to columns 16 and 20 at row 41), tapering to its
tip at the bottom. Between the thighs, a black gap; round it all the ice of CAMANIS' plateau and the object's shadow
on it (ramp 3 and the black beyond the outline to the right and between the feet): the map's ground and the game's
own shadow, left out (the silhouette is checked against the object's own pixels: the steel, the purple and the
outline next to them).

Built as a crouching walker whose body is a ball turret: the sphere (29 x 26 pixels as the sprite draws it, so a
little flattened up the screen) is held at its sides on an axle (its poles there, in hubs), high above the ice; an
arm at each side comes down from the axle's cap to the hip, a raised panel along its outer face; over each hip a
cradle of armour hugs the sphere's lower side (as the sprite's purple wraps the sphere's lower edge); from the hips
the legs reach forward and down: each thigh a broad slab sloping from under the sphere's front (its back rising in
front of the sphere's lower edge, as the sprite draws the thighs' tops over it) down to the knee, a piston rod
lying in the channel along its middle; the knee an axle across the leg; the shin a ridged bar sloping down to the
foot, a ridged wedge whose inner side reaches out into the toe; the soles on the ice (z = 0). The sphere is turned
about its axle (a lathe about the x axis), the two seams down the screen grooves in its profile; the seam across
the screen and the three on the lower left are cut by exact booleans (thin slabs less a sphere 0.3 smaller). The
armour is CAD-like (polish_machine_kit): prisms of plans and profiles, wedges, lofted ridged bars, bevelled, flat
faces kept flat. The left half of the armour is built and mirrored about x = -5.5 (the sun shades the halves as the
sprite does). The whole object is then cut along the sprites' edges (x = 0, y = 0; polish_arch.py's cut(): the pieces
keep the whole's shading across the cuts), each piece moved so that its sprite's centre is its origin.

Colours as the sprites': the steel ramp 0 (the shell 0x0b, a little emission in 0x08 so that its shaded side doesn't
read black from the game's slanted camera; seams 0x07, hubs 0x09), the armour ramp 5 (0x59; the axle caps 0x5c, the
channels 0x55, undersides 0x53, the pelvis between the hips and the cuts 0x51). No lamps: nothing glows.

Where it stands: models drawn at their origin stand at the ground enemies' layer, 4 pixels above the terrain;
height=-4 on the four sprite lines sets the feet on the ice (their soles reach 0.5 below z = 0). ICESECRET's ice is
raised ground now (its rough ice 12 pixels over the smooth floor) and CAMANIS' plateau has its own terrain: the
pieces stand at the terrain's height under their middle, so the feet stand on it where the ground under the walker
is level.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the ice (z = 0); the whole's
origin is the middle of the picture (the corner where the four sprites meet): column c is x = c + 0.5 - 24, row r
is y = 27.5 - r. The pieces' centres: 161 (-12, 14), 163 (12, 14), 199 (-12, -14), 201 (12, -14).

Replaces wave3_ac_ice.py's globe: remove its section ("# --- 7 161 163 / 199 201: the globe on its legs": GLOBE,
GX, G_CENTRE, G_RADII, on_globe(), build_globe() and the a.pieced("ice_globe", ...) registration) and the
ice_globe paragraph of its docstring; and wave3_ac_art.py's SPHERE (only that section reads it). quarters() stays
(the bunker uses it), and so does build_drill() (wave3_at_misc.py imports wave3_ac_ice and calls it).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes of the
whole and of each piece against the object's own pixels of enemy_7.png), --preview <prefix> (the whole's top and
3/4 views; --pieces 1 also each piece's), --only <name,...> (pieces to export), --whole <file.glb> (the uncut walker
as well, for looking at).
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_arch import cut  # noqa: E402  (polish_machine_kit.cut without its material indices shifted twice)
from polish_k_pod import triangulate  # noqa: E402

PIECES = [("ice_globe_tl", 161, (-24.0, 0.0, 0.0, 28.0)), ("ice_globe_tr", 163, (0.0, 24.0, 0.0, 28.0)),
          ("ice_globe_bl", 199, (-24.0, 0.0, -28.0, 0.0)), ("ice_globe_br", 201, (0.0, 24.0, -28.0, 0.0))]
SPRITE_CELLS = {161: (0, 0), 163: (24, 0), 199: (0, 28), 201: (24, 28)}

AX = -5.5                      # the object's middle (column 18)

# The sphere: its middle and radii (the sprite draws it 29 pixels across and 26 up the screen, its outline
# included); it turns on an axle along x through its middle, its poles under the hubs.
YC, ZC = 13.0, 18.5
RX, RY, RZ = 14.5, 13.0, 13.75
RINGS, AROUND = 44, 64         # the lathe's rings (from pole to pole) and points round each
SEAM_W, SEAM_D = 0.42, 0.3     # the seams' width and depth
SEAMS_X = [2.0, 7.0]           # the seams down the screen (columns 20 and 25): offsets from the middle, in the profile
SEAM_ACROSS = YC + 2.5         # the seam across the screen (row 12)
# The seams on the lower left quarter (columns 9 and 13, the slanting one between them, rows 15-18): offsets from the
# middle and how far up the screen they run.
SEAM_LOW = [(-9.0, YC + 2.5), (-4.8, YC - 3.5)]
SEAM_SLANT = ((-9.0, YC - 0.5), (-4.8, YC - 3.5))
HUB = (13.3, 14.75, 3.6)       # the hubs round the poles: from, to (offsets from the middle), radius
AXLE = (12.9, 17.3, 1.4)

# The arms: plates beside the sphere (offsets from the middle) from the axle (a round end of radius ARM_TOP_R) down
# to the hip (ARM_FOOT, radius ARM_FOOT_R); a cap on the axle's end.
ARM_X = (14.65, 17.15)
ARM_TOP_R, ARM_FOOT, ARM_FOOT_R = 1.75, (3.0, 8.0), 2.95
CAP = (17.25, 18.0, 1.45)
ARM_PANEL = (0.75, 0.32)     # the raised panel on the arm's outer face: inset from its edges, how far it stands out
# The hips: blocks under the sphere's lower sides (offsets, y, z), joining the arms to the thighs; over them the
# cradle, armour hugging the sphere's lower sides (a shell CRADLE_T thick round it, inside the box: offsets, y, z).
HIP = (8.3, 16.9, 0.1, 6.5, 3.2, 9.6)
CRADLE_T = 1.8
CRADLE = (8.4, 17.2, -1.0, 9.0, 2.0, 15.0)
# The thighs: offsets, back and front (y), their top and bottom at the back and at the front (each thigh slopes down
# from the hip to the knee; its back end rises in front of the sphere's lower edge, as the sprite draws the thighs'
# tops over it); the channel along the middle (offsets, its back end (y), its depth under the top) and the piston rod
# lying in it (radius).
THIGH = (0.9, 13.5, 2.0, -8.4, (11.3, 6.2), (7.0, 2.6))
CHANNEL = (6.35, 8.35, 1.4, 2.0)
ROD_R = 0.6
# The knee: an axle across the leg (offsets, y, z, radius) under the thigh's front.
KNEE = (4.2, 9.8, -7.7, 5.4, 2.05)
# The shin and the foot: ridged bars, lofted through sections (y, outer side, inner side, ridge (offsets), bottom,
# outer and inner sides' tops, ridge (z)); the foot's sections run from the ankle to the tip, its inner side
# reaching out into the toe that points in towards the other foot (row 41-43).
SHIN = [(-6.6, 10.05, 3.95, 6.4, 3.9, 6.2, 6.2, 7.5), (-9.6, 10.05, 3.95, 6.4, 2.3, 4.5, 4.5, 5.8),
        (-12.6, 10.05, 3.95, 6.4, 0.4, 2.8, 2.8, 4.1)]
SOLE = -0.5                    # the soles, a little below the ice
FOOT = [(-11.7, 10.05, 3.95, 6.6, SOLE, 1.9, 1.9, 3.7), (-12.6, 10.05, 2.5, 6.6, SOLE, 1.8, 1.3, 3.5),
        (-13.5, 10.05, 1.35, 6.6, SOLE, 1.7, 0.9, 3.25), (-14.3, 10.05, 0.9, 6.7, SOLE, 1.6, 0.7, 3.0),
        (-15.1, 10.05, 1.7, 6.8, SOLE, 1.45, 0.75, 2.75), (-16.5, 10.0, 3.0, 6.9, SOLE, 1.25, 0.8, 2.35),
        (-18.0, 9.8, 4.5, 7.0, SOLE, 1.0, 0.75, 1.9), (-19.2, 9.0, 5.7, 7.1, SOLE, 0.75, 0.6, 1.45),
        (-19.85, 7.8, 6.5, 7.15, SOLE, 0.5, 0.45, 0.95)]
PELVIS = (-8.6, 8.6, 0.0, 6.5, 3.4, 7.2)  # the beam between the hips under the sphere (offsets, y, z)


def materials():
    pal = k.level_palette()
    return {
        "shell": k.material("globe_shell", palette=0x0b, metallic=0.45, roughness=0.3, emission=pal[0x08],
                            emission_strength=0.08),
        "seam": k.material("globe_seam", palette=0x07, metallic=0.45, roughness=0.45),
        "hub": k.material("globe_hub", palette=0x09, metallic=0.6, roughness=0.28),
        "axle": k.material("globe_axle", palette=0x07, metallic=0.6, roughness=0.35),
        "armour": k.material("globe_armour", palette=0x59, metallic=0.35, roughness=0.34),
        "light": k.material("globe_armour_light", palette=0x5c, metallic=0.35, roughness=0.3),
        "recess": k.material("globe_armour_recess", palette=0x55, metallic=0.3, roughness=0.45),
        "under": k.material("globe_armour_under", palette=0x53, metallic=0.25, roughness=0.5),
        "deep": k.material("globe_armour_deep", palette=0x51, metallic=0.2, roughness=0.6),
    }


def X(offset):
    """The left half's x of an offset from the middle (the left half is built, then mirrored)."""
    return AX - offset


# --- The sphere ----------------------------------------------------------------------------------------------------

def sphere_profile(rx=RX, depth=SEAM_D, seams=SEAMS_X):
    """(x offset, radius as a share of the middle's) from pole to pole (the poles themselves left out: lathe_x
    closes on them): the sphere (rx across), with the grooves of the seams down the screen, depth deep."""
    pts = []
    for i in range(1, RINGS):
        t = math.pi * i / RINGS
        pts.append((-rx * math.cos(t), math.sin(t)))
    unit = (RY + RZ) / 2
    for s in seams:
        pts = [p for p in pts if abs(p[0] - s) > SEAM_W / 2 + 0.12]
        for dx, dip in ((-SEAM_W / 2 - 0.06, 0.0), (-SEAM_W / 2 + 0.06, depth), (SEAM_W / 2 - 0.06, depth),
                        (SEAM_W / 2 + 0.06, 0.0)):
            x = s + dx
            pts.append((x, math.sqrt(max(0.0, 1 - (x / rx) ** 2)) - dip / unit))
    pts.sort()
    return pts


def lathe_x(name, profile, mat, poles, around=AROUND, centre=(AX, YC, ZC), radii=(RY, RZ), seam_at=None,
            seam_mat=None):
    """A solid turned about an axis along x through centre: profile [(x offset, radius)] (the radius a share of
    radii, across the screen and up), its ends closing on the axis at the poles (x offsets). Faces between profile
    points inside a seam (seam_at: [(x0, x1)]) get seam_mat."""
    cx, cy, cz = centre
    ry, rz = radii
    rings = []
    for dx, r in profile:
        r = max(r, 1e-4)
        rings.append([Vector((cx + dx, cy + ry * r * math.cos(2 * math.pi * j / around),
                              cz + rz * r * math.sin(2 * math.pi * j / around))) for j in range(around)])
    obj = k.loft(name, rings, mat, start_point=(cx + poles[0], cy, cz), end_point=(cx + poles[1], cy, cz))
    if seam_at:
        def pick(c, n):
            d = c.x - cx
            return seam_mat if any(a <= d <= b for a, b in seam_at) else None
        mk.paint(obj, pick)
    return obj


def sphere(m):
    seams = [(s - SEAM_W / 2 - 0.07, s + SEAM_W / 2 + 0.07) for s in SEAMS_X]
    ball = lathe_x("sphere", sphere_profile(), m["shell"], (-RX, RX), seam_at=seams, seam_mat=m["seam"])
    k.smooth(ball, 50)
    # The seam across the screen and the three on the lower left: thin slabs less a sphere SEAM_D smaller.
    big = RX + 2
    cutters = [mk.box("seam_across", AX - big, AX + SEAMS_X[0], SEAM_ACROSS - SEAM_W / 2, SEAM_ACROSS + SEAM_W / 2,
                      ZC - big, ZC + big, m["seam"])]
    for off, top in SEAM_LOW:
        cutters.append(mk.box("seam_low%g" % off, AX + off - SEAM_W / 2, AX + off + SEAM_W / 2, YC - big, top,
                              ZC - big, ZC + big, m["seam"]))
    (a0, b0), (a1, b1) = SEAM_SLANT
    p, q = Vector((AX + a0, b0)), Vector((AX + a1, b1))
    d = (q - p).normalized()
    nrm = Vector((-d.y, d.x)) * (SEAM_W / 2)
    ends = [p - d * 0.25, q + d * 0.25]
    cutters.append(mk.prism("seam_slant", [tuple(ends[0] - nrm), tuple(ends[1] - nrm), tuple(ends[1] + nrm),
                                           tuple(ends[0] + nrm)], ZC - big, ZC + big, m["seam"]))
    d = SEAM_D
    inner = lathe_x("seam_inner", [(-(RX - d) * math.cos(math.pi * i / 36), math.sin(math.pi * i / 36))
                                   for i in range(1, 36)], m["seam"], (-(RX - d), RX - d), radii=(RY - d, RZ - d))
    groove = cutters[0]
    mk.boolean(groove, cutters[1:], "UNION")
    mk.boolean(groove, inner, "DIFFERENCE")
    mk.boolean(ball, groove, "DIFFERENCE")
    k.smooth(ball, 50)
    # The hubs round the poles and the axle through them (built on the left; the right ones are mirrored).
    a, b, r = HUB
    hub = mk.tube("hub", [(X(a), YC, ZC), (X(b), YC, ZC)], r, m["hub"], 32)
    mk.bevel(hub, 0.25, 2, 40)
    k.smooth(hub, 40)
    a, b, r = AXLE
    k.smooth(mk.tube("axle", [(X(a), YC, ZC), (X(b), YC, ZC)], r, m["axle"], 20), 40)
    return ball


# --- The armour (left half) ------------------------------------------------------------------------------------------

def capsule_outline(p0, r0, p1, r1, count=40):
    """The outline (2D, counter-clockwise) of two circles joined by their outer tangents: the convex hull of the two."""
    samples = []
    for i in range(count):
        ang = 2 * math.pi * i / count
        samples.append((p0[0] + r0 * math.cos(ang), p0[1] + r0 * math.sin(ang)))
        samples.append((p1[0] + r1 * math.cos(ang), p1[1] + r1 * math.sin(ang)))
    return convex_hull_2d(samples)


def convex_hull_2d(points):
    pts = sorted(set((round(x, 6), round(y, 6)) for x, y in points))
    if len(pts) <= 2:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 1e-9:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 1e-9:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def paint_armour(obj, m):
    """Armour faces: the down-facing ones darker."""
    mk.paint(obj, lambda c, n: m["under"] if n.z < -0.55 else None)


def arm(m):
    """The arm beside the sphere: a plate from the axle down to the hip, its edges rounded, a raised panel along its
    outer face; the cap on the axle."""
    outline = capsule_outline((YC, ZC), ARM_TOP_R, ARM_FOOT, ARM_FOOT_R)
    plate = mk.prism("arm", outline, X(ARM_X[1]), X(ARM_X[0]), m["armour"], axis="x")
    mk.bevel(plate, 0.55, 3, 35)
    paint_armour(plate, m)
    mk.shade(plate, 35)
    inset = ARM_PANEL[0]
    panel_outline = capsule_outline((YC, ZC), ARM_TOP_R - inset, ARM_FOOT, ARM_FOOT_R - inset)
    panel = mk.prism("arm_panel", panel_outline, X(ARM_X[1] + ARM_PANEL[1]), X(ARM_X[1] - 0.2), m["armour"],
                     axis="x")
    mk.bevel(panel, 0.22, 2, 35)
    paint_armour(panel, m)
    mk.shade(panel, 35)
    a, b, r = CAP
    pts = [(X(a), YC, ZC), (X(b - 0.35), YC, ZC), (X(b - 0.1), YC, ZC), (X(b), YC, ZC)]
    cap = mk.tube("arm_cap", pts, r, m["light"], 28, radii=[r, r, r * 0.8, r * 0.35])
    k.smooth(cap, 50)
    return plate


def rounded_block(name, x0, x1, y0, y1, z0, z1, mat, bevel_w, segments=3):
    obj = mk.box(name, min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1), z0, z1, mat)
    mk.bevel(obj, bevel_w, segments, 35)
    return obj


def hip(m):
    """The hip block, and the cradle over it hugging the sphere's lower side."""
    a, b, y0, y1, z0, z1 = HIP
    block = rounded_block("hip", X(a), X(b), y0, y1, z0, z1, m["armour"], 1.6)
    paint_armour(block, m)
    mk.shade(block, 35)
    t = CRADLE_T
    profile = [(-(RX + t) * math.cos(math.pi * i / 40), math.sin(math.pi * i / 40)) for i in range(1, 40)]
    shell = lathe_x("cradle", profile, m["armour"], (-(RX + t), RX + t), around=56, radii=(RY + t, RZ + t))
    a, b, y0, y1, z0, z1 = CRADLE
    mk.boolean(shell, mk.box("cradle_box", X(b), X(a), y0, y1, z0, z1, m["armour"]), "INTERSECT")
    mk.cleanup(shell)
    mk.bevel(shell, 0.5, 2, 35)
    paint_armour(shell, m)
    mk.shade(shell, 40)
    return block


def thigh(m):
    """The thigh: a broad slab sloping down from the hip under the sphere to the knee, a channel along its middle
    (open at the knee) with a piston rod lying in it, its edges rounded."""
    a, b, back, front, (top_b, bottom_b), (top_f, bottom_f) = THIGH
    plan = [(X(a), front), (X(a), back), (X(b), back), (X(b), front)]
    top = mk.plane((X(a), back, top_b), (X(b), back, top_b), (X(a), front, top_f))
    bottom = mk.plane((X(a), back, bottom_b), (X(b), back, bottom_b), (X(a), front, bottom_f))
    block = mk.wedge("thigh", plan, 0.0, top, m["armour"], bottom=bottom)
    mk.bevel(block, 1.5, 4, 35)
    c0, c1, cback, depth = CHANNEL
    floor = lambda x, y: top(x, y) - depth  # noqa: E731
    channel = mk.wedge("thigh_channel", [(X(c1), front - 2.0), (X(c1), cback), (X(c0), cback), (X(c0), front - 2.0)],
                       0.0, lambda x, y: 30.0, m["recess"], bottom=floor)
    mk.bevel(channel, 0.35, 2, 35)
    mk.boolean(block, channel, "DIFFERENCE")
    mk.cleanup(block)
    paint_armour(block, m)
    mk.shade(block, 35)
    mid = X((c0 + c1) / 2)
    ends = [(mid, y, floor(mid, y) + ROD_R) for y in (cback - 0.4, KNEE[2])]
    rod = mk.tube("thigh_rod", ends, ROD_R, m["axle"], 12)
    k.smooth(rod, 50)
    return block


def ridged(name, sections, mat):
    """A bar lofted through ridged sections (y, outer side, inner side, ridge (offsets), bottom, outer and inner
    sides' tops, ridge (z)), its edges rounded."""
    rings = []
    for y, out, inn, ridge, zb, zo, zi, zr in sections:
        rings.append([Vector((X(inn), y, zb)), Vector((X(out), y, zb)), Vector((X(out), y, zo)),
                      Vector((X(ridge), y, zr)), Vector((X(inn), y, zi))])
    bar = k.loft(name, rings, mat)
    mk.bevel(bar, 0.38, 2, 30)
    return bar


def knee_and_shin(m):
    a, b, y, z, r = KNEE
    knee = mk.tube("knee", [(X(a), y, z), (X(a + 0.4), y, z), (X(b - 0.4), y, z), (X(b), y, z)], r, m["armour"], 24,
                   radii=[r * 0.8, r, r, r * 0.8])
    k.smooth(knee, 45)
    shin = ridged("shin", SHIN, m["armour"])
    paint_armour(shin, m)
    mk.shade(shin, 30)
    return knee, shin


def foot(m):
    block = ridged("foot", FOOT, m["armour"])
    paint_armour(block, m)
    return mk.shade(block, 30)


def pelvis(m):
    a, b, y0, y1, z0, z1 = PELVIS
    beam = rounded_block("pelvis", AX + a, AX + b, y0, y1, z0, z1, m["deep"], 0.8, 2)
    return mk.shade(beam, 35)


# --- The whole -----------------------------------------------------------------------------------------------------

def mirror_about_axis(objects):
    """Copies of objects mirrored about x = AX, keeping their shading (corner normals) and materials."""
    flip = Matrix.Translation((AX, 0, 0)) @ Matrix.Scale(-1, 4, (1, 0, 0)) @ Matrix.Translation((-AX, 0, 0))
    out = []
    for obj in objects:
        mk.apply(obj)
        copy = obj.copy()
        copy.data = obj.data.copy()
        copy.name = obj.name + "_r"
        bpy.context.scene.collection.objects.link(copy)
        mesh = copy.data
        corner = {}
        for poly in mesh.polygons:
            for li in poly.loop_indices:
                n = mesh.corner_normals[li].vector
                corner[(poly.index, mesh.loops[li].vertex_index)] = (-n.x, n.y, n.z)
        mesh.transform(flip)
        mesh.flip_normals()
        normals = [None] * len(mesh.loops)
        for poly in mesh.polygons:
            for li in poly.loop_indices:
                normals[li] = corner[(poly.index, mesh.loops[li].vertex_index)]
        mesh.normals_split_custom_set(normals)
        out.append(copy)
    return out


def build_whole():
    m = materials()
    sphere(m)
    left = [bpy.data.objects["hub"], bpy.data.objects["axle"], arm(m), bpy.data.objects["arm_panel"],
            bpy.data.objects["arm_cap"], hip(m), bpy.data.objects["cradle"], thigh(m), bpy.data.objects["thigh_rod"]]
    left += list(knee_and_shin(m)) + [foot(m)]
    mirror_about_axis(left)
    pelvis(m)
    whole = mk.meshes()
    for obj in whole:
        mk.apply(obj)
    triangulate(whole)
    bpy.context.view_layer.update()
    return whole, m


def object_mask(sheet):
    """The object's own pixels in the 48 x 56 picture: the steel, the purple and the edge pixels (palette ramps other
    than the ice's, 3), and the black and near-black (indices 1 and 2) next to them, its outline; the ice, the
    shadow on it and the black of the shadow beyond the outline left out."""
    sys.path.insert(0, os.path.join(HERE, "..", ".."))
    from sprite_profile import sprite_indices
    grid = [[None] * 48 for _ in range(56)]
    for sprite, (c0, r0) in SPRITE_CELLS.items():
        for r, row in enumerate(sprite_indices(sheet, sprite)):
            for c, v in enumerate(row):
                grid[r0 + r][c0 + c] = v
    body = [[v is not None and v >> 4 != 3 and v not in (1, 2) for v in row] for row in grid]
    mask = [[False] * 48 for _ in range(56)]
    for r in range(56):
        for c in range(48):
            v = grid[r][c]
            if body[r][c]:
                mask[r][c] = True
            elif v in (1, 2):
                mask[r][c] = any(0 <= r + dr < 56 and 0 <= c + dc < 48 and body[r + dr][c + dc]
                                 for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)))
    return mask


def build():
    k.reset()
    options = k.args()
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    whole, m = build_whole()
    low, high = mk.bounds(whole)
    print("== whole globe: %d triangles, %d objects, %d materials, x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f" % (
        mk.triangles(whole), len(whole), len(mk.materials_of(whole)), low.x, high.x, low.y, high.y, low.z, high.z))
    mask = None
    if "check" in options:
        sheets = options["check"]
        sheet = os.path.join(sheets, "enemy_7.png") if os.path.isdir(sheets) else sheets
        mask = object_mask(sheet)
        mk.compare("whole (7 161 163 above 199 201, the object's own pixels)", mk.coverage(whole, 48, 56), mask)
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    if "preview" in options:
        mk.preview(options["preview"] + "ice_globe_whole", whole, size=(48, 56), scale=10, distance=1.9)
    if "whole" in options:
        mk.export(whole, options["whole"])
    for name, sprite, box in PIECES:
        if only and name not in only:
            continue
        pieces = [p for p in (cut(src, box, m["deep"]) for src in whole) if p is not None]
        mk.transform(pieces, Matrix.Translation((-(box[0] + box[1]) / 2, -(box[2] + box[3]) / 2, 0)))
        bpy.context.view_layer.update()
        for src in whole:
            src.hide_render = True
        if mask is not None:
            c0, r0 = SPRITE_CELLS[sprite]
            mk.compare("%s (7 %d)" % (name, sprite), mk.coverage(pieces, 24, 28),
                       [row[c0:c0 + 24] for row in mask[r0:r0 + 28]])
        mk.report(name, pieces, os.path.join(out, name + ".glb"))
        if "preview" in options and options.get("pieces") == "1":
            mk.preview(options["preview"] + name, pieces)
        for obj in pieces:
            bpy.data.objects.remove(obj)
        for src in whole:
            src.hide_render = False


if __name__ == "__main__":
    build()
