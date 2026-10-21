"""The two long arms TYRIAN and TYRIAN X sweep across the screen before the tusked boss comes (episodes 1 and 3, sheet
4; seven sprites each, each an enemy of its own on the top layer), polished (2026-10-21, round 27; it replaces
wave3_ab_arms.py, a round hull along the middle of the sprites' pixels, painted pixel by pixel). models.cfg: the model
lines tusk_arm_a_<sprite> and tusk_arm_b_<sprite> (origin) and the sprite lines 4 <sprite> tusk_arm_<a|b>_<sprite>
yaw=0 stay as they are.

The events (TYRIAN and TYRIAN X alike; tools/content/tyrevents.py): "WARNING: Spikes ahead!!" at t 3480; at t 3525 arm
B (enemies 73-79 = 231 233 235 267 269 271 273, event 7: the top layer, link 2) at x 156, 180 ... 300, at t 3574 arm A
(66-72 = 153 155 157 159 191 193 195, link 1) at x 48 ... 192: each piece 24 pixels right of the one before, all at
the same height, so each arm is one 168 x 28 picture; event 20 (global accel, excc -2 then +2 ten ticks later, +2 then
-2 for A) thrusts each arm in from its own side of the screen and draws it back out; A comes again at t 3798 (x 72 ...
216) and 4068, B at 3863 and 3928 (x 108 ... 252). No episode 6 level takes these waves (compose.expand of every level:
DIG SITE takes TYRIAN X's boss block, which starts after them). Each piece has armour 50 and can be shot away alone
(A's tusk end and B's root end are worth 1000); one frame (ani 1), no damaged look (dgr 0), no guns; no other enemy,
launched ones included, shows these sprites.

Arm B is arm A's pixels mirrored one pixel over (B's column c is A's column 168 - c: the outlines differ in 30 of about
2050 pixels, the root, the ball, the clamps and the tusk are shaded alike), but not exactly: its first band is drawn
otherwise (A: a steel collar at columns 57-64, lit above and black below, a lit gold ring at 66 and a brown T-shaped
strap at 76-82; B: a small steel eye on the far side at 56-59 and lit ring grooves at 60, 64, 74 and 78) and its tusk's
underside is drawn lighter. So B is A's model mirrored (x -> 1 - x) with its own band; both are painted after the
mirror, by the game's light from the upper left (B's sprite keeps A's highlights mirrored).

As the sprites and their 4x upscales draw arm A (its picture's columns and rows; B mirrored):
- the thick pipe (rows 1-21) from the picture's left edge, its end rounded down (columns 22-33) into a short neck
  (33-36); the ball joint (36-49, rows 1-19), a big highlight on its upper left;
- the thinner pipe (rows 1-12 at column 55), its far edge level, sinking and narrowing to the right, its near rim lit
  (the sprite's row 12): the steel collar (57-64), the gold ring (66), a small steel lug on its near side (70-72),
  the brown strap (a band at 80-82, a bar over its far half at 76-79), a steel clamp (84-88) and two more (105-110,
  124-129), each on the pipe's far half;
- the tusk: the pipe running on from a lip at column 130, narrowing and curving down to its point (column 165-166,
  row 25).

Built as a CAD modeller would, in the tusked boss's family (polish_tusk_boss.py: its materials, tusk_*, and their
finishes; the gold of its plates and cables for the pipes, its steel for the clamps, its tusks' brown for the tusk, its
glossy black for the collar's lower half): the root, its shoulder (a bell) and neck one loft of superellipse sections
(ROOT...), the ball a superellipsoid (fuller at its far corners, BALL_POWER), the pipe a loft along a smooth middle line
fitted to the sprites' columns (TABLE and each arm's TAILS: the sections square to the line in plan, as wide as the
pixels across it; flaring into the ball in plan only, PIPE_FLARE), ending in a lip; these three joined by an exact
union. The tusk is a loft along the same line from inside the lip to its point, sinking a little as it curves. The
collar, rings, grooves, strap, clamps and lug are shells lying on the pipe (shell: a band of its sections grown out by
their lift and sunk into it, over the angles of the pipe's section the sprite draws them on, inside the sprites'
outline), their edges bevelled; B's eye a lathed steel dome in a dark recess, square to the pipe's surface (a little
higher than the sprite draws it, so that the slanted camera sees it face on). Painted after the mirror: the gold parts
in bands of the light (polish_orb_red.band_split along smooth contours; PAINT_LIGHT a little lower than the game's sun,
so that the far shoulder carries the highlight and the near side falls dark as the sprites shade them; a smooth bias
darkens the waist's crease and the thinner pipe, WAIST_SHADE, PIPE_SHADE): gold 0x13 0x16 0x19 0x1b 0x1d (0x13 a
shade under the boss's darkest, for the near side the sprites draw near black), the pipe's near rim 0x19 (the
sprites' lit lower rim); the tusk as the boss's tusks are painted (their light and band: brown 0xa7, lit 0xaa), 0xa4
under it; the small parts face by face (the clamps and the lug dark steel 0x04 with 0x07 / 0x0a edges towards the
light, the collar lit steel 0x07-0x0d over its far half and the boss's glossy black 0x02 over its near side (glowing
0.1 as the boss's), its lowest edge 0x07; the strap 0xa4 0xa7; the eye steel 0x04-0x0d, its recess 0x01). No other
glow. In the game camera the arms render about 1.3 times as bright as their upscales (the polished boss 1.5 times).
The ball is lofted from explicit rings: bmesh's create_uvsphere orders its faces differently on every call.

Each arm is cut along its sprites' edges into its seven pieces (cut: polish_coral_manta.cut's, the caps the inside's
colour: 0x01 for the metal, 0xa4 for the tusk, shaded as a top; the uncut normals kept), each moved so that its
sprite's middle is its origin (drawn at their own origins on the top layer they meet again); every mesh triangulated
before the export (polish_k_pod.triangulate): the same output every run, with and without --check (md5 of all 14).
The pieces stand from z -8 to 6 (the arm's axis at Z0 = -1; the top layer at 0, 6 pixels under the player's).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera. An arm's origin is
its picture's middle (pixel edge 84, 14): column c's left edge is x = c - 84, row r's top edge y = 14 - r; piece i
(0-6) spans x -84 + 24 i .. -60 + 24 i, its origin at x -72 + 24 i, y 0. B's model is built in A's frame (its pixels
mirrored, column c of the mirror = B's column 168 - c) and moved by x -> 1 - x.

Replaces wave3_ab_arms.py (all of it: delete it; nothing imports it) and wave3_ab_art.py (its ARM_A and ARM_B are all
that is left in it, and only wave3_ab_arms.py reads them: delete it). wave3_ab_kit.py stays (wave3_ai_gryphon.py and
wave3_ai_kit.py use its field, paint, polys_of, brightness, loft_path, simplify_bottom, sharpen_walls and s / q
helpers), but its `import wave3_ab_art as art` must go with the art file, and frame() with it (frame_mask(), pieced,
run, relief, transformed_copies and surface have no other users either). Also replaces wave2_g.py's pipe_arm_2 (4 269,
cut from the pipe alone, dead since the arms took 269: its section, WHOLES and the --whole option, wave2_g_art.py's
E4_PIPE) with models.cfg's model pipe_arm_2 line and its GLB.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each piece's silhouette
against its sprite in enemy_4.png, and each arm's whole against its seven sprites side by side), --preview <prefix>
(each arm's whole and each piece: top and 3/4 views), --only <model,...> (pieces to export; "none": none), --arm a|b
(one arm only), --whole <prefix> (the uncut arms as <prefix>a.glb, <prefix>b.glb, for looking at), --stats 1.
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
import polish_tusk_boss as tb  # noqa: E402  (the boss's materials and banded painting: the same family)
from polish_k_pod import triangulate  # noqa: E402
from polish_orb_red import band_split  # noqa: E402

ARMS = {"a": (153, 155, 157, 159, 191, 193, 195), "b": (231, 233, 235, 267, 269, 271, 273)}
Z0 = -1.0                      # the arm's axis height (its layer at 0)
POWER = 2.2                    # the sections' superellipse
PAINT_LIGHT = (-0.45, 0.68, 0.58)
CAP_NORMAL = (0.0, 0.0, 1.0)   # the cuts shaded as the inside, lit like a top (seen when a neighbour is gone)

# The root, its shoulder and the neck into the ball: (x, y of the axis, half-width, half-height); the shoulder a bell
# (a smooth step) from x SHOULDER[0] (half-width ROOT_HW) to SHOULDER[1] (the neck's NECK_HW), steepest where the
# sprites narrow it (columns 32-33), its axis rising with it so that its far edge stays near the pipe's.
ROOT_Y, ROOT_HW, ROOT_HH = 2.5, 10.45, 6.5
SHOULDER = (-55.5, -49.0)
NECK_Y, NECK_HW, NECK_HH = 4.4, 6.6, 4.4
NECK_END = -45.5
# The ball joint: middle (x, y), radii (x, y, z), its plan a superellipse of these powers over its far and near
# halves (fuller at its far corners, where the sprites square it off under the pipe's level edge).
BALL = ((-41.2, 3.6), (6.9, 9.5, 7.0))
BALL_POWER = (2.6, 2.0)
# The pipe and the tusk: their middle line and the half-height of their pixels across it, (x, y, half-height): a
# smooth fit to the columns' extents of both arms (A, and B mirrored).
TABLE = [(-41.0, 5.0, 7.6), (-37.5, 5.4, 7.55), (-34.5, 5.65, 7.35), (-32.8, 6.15, 6.85), (-31.5, 6.45, 6.45),
         (-28.0, 6.75, 6.2),
         (-22.0, 6.95, 6.1), (-16.0, 7.0, 5.95), (-10.0, 6.95, 5.8), (-4.0, 6.8, 5.62), (2.0, 6.55, 5.45),
         (8.0, 6.2, 5.25), (14.0, 5.78, 5.07), (20.0, 5.25, 4.9), (26.0, 4.6, 4.75), (32.0, 3.84, 4.63),
         (38.0, 2.92, 4.53), (44.0, 1.84, 4.39), (50.0, 0.54, 4.21), (56.0, -0.97, 3.95), (62.0, -2.74, 3.56)]
# ... and the tusk's last pixels, each arm's own: B's tusk is drawn a pixel longer and fuller at its end (in A's frame).
TAILS = {"a": [(67.0, -4.45, 3.1), (71.0, -6.15, 2.65), (74.5, -7.6, 2.15), (77.5, -9.0, 1.65), (80.0, -10.3, 1.05),
               (82.4, -11.7, 0.05)],
         "b": [(67.0, -4.3, 3.15), (71.0, -5.85, 2.75), (74.5, -7.25, 2.3), (77.5, -8.5, 1.9), (80.0, -9.7, 1.45),
               (82.0, -10.75, 0.95), (83.1, -11.6, 0.05)]}
PIPE_RATIO, TUSK_RATIO = 0.8, 0.82   # half-height to half-width
PIPE_FLARE = (-28.0, 4.95)           # before this x the pipe flares into the ball in plan only: its half-height kept
PIPE_X = (-41.0, 45.6)               # the pipe; its lip (grows, flat to, closes at) after it
LIP = (45.95, 46.85, 47.25, 0.4)     # ... (x where it has grown, x where it starts closing, its end; how proud)
TUSK_X = (45.6, 82.4)                # the tusk, from inside the lip to its point (B's: TAILS' last x)
TUSK_SINK = 1.5                      # how far its point sinks under the axis
RIM = (-34.0, 45.5, -0.9)            # the pipe's near rim, lit: from x to x, faces facing down the screen beyond this
# The parts on the pipe, (x0, x1, angle 0, angle 1 (degrees round the pipe's section: 0 its far side, up the screen;
# 90 its top; 180 its near side), how proud): the angles where the sprites draw them.
CLAMPS = [(0.0, 5.0, 26.0, 104.0, 0.6), (21.0, 27.0, 34.0, 106.0, 0.6), (40.0, 46.0, 26.0, 106.0, 0.6)]
LUG = (-14.4, -11.2, 110.0, 162.0, 0.8)
COLLAR = (-27.0, -19.0, 0.3)        # A: the steel collar (a band all round)
GOLD_RING = (-18.1, -16.9, 0.28)     # A: the lit ring after it
STRAP = (-4.1, -1.0, 0.25)            # A: the brown strap's band
STRAP_BAR = (-8.1, -4.1, 26.0, 96.0, 0.35)   # ... and its bar over the far half
EYE = (-26.0, 48.0)                  # B: the steel eye (x, angle; a little higher than the sprite's far edge, so that
# the slanted camera sees it face on): a collar, a dark recess (EYE_RECESS: radii, under this height), a steel dome
EYE_PROFILE = [(2.05, -0.5), (2.05, 0.38), (1.88, 0.58), (1.66, 0.56), (1.6, 0.44), (1.46, 0.48), (1.42, 0.74),
               (1.18, 1.06), (0.8, 1.27), (0.32, 1.36)]
EYE_RECESS = (1.43, 1.86, 0.6)
GROOVES = [-23.5, -19.5, -9.5, -5.5]  # B: the lit ring grooves (x of their middles)
GROOVE = (0.9, 0.25)                  # ... their width, how proud

GOLD_BANDS = [(-9.0, "gold_deep"), (0.42, "gold_dark"), (0.64, "gold"), (0.8, "gold_lit"), (0.87, "gold_light")]
# Darker where the sprites draw it so: a crease at the waist, the thinner pipe (a smooth bias of the bands' value).
WAIST_SHADE = (-50.3, 1.9, 0.16)     # x, width, how much
PIPE_SHADE = (-36.0, -28.0, 0.07)    # from x to x, how much
TUSK_BANDS = [(-9.0, "brown_dark"), (0.15, "brown"), (0.72, "brown_lit")]   # by the boss's tusk light (TUSK_LIGHT),
TUSK_LIGHT = (-0.6, 0.3, 0.75)                                                # its band at 0.72 as on its tusks
CAPS = {"body": "core", "tusk": "brown_dark"}   # the cut caps' material by part (others: core)


def sstep(e0, e1, x):
    t = min(1.0, max(0.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


def se(phi):
    """The unit superellipse's point at angle phi: (across, up)."""
    c, s = math.cos(phi), math.sin(phi)
    return math.copysign(abs(c) ** (2 / POWER), c), math.copysign(abs(s) ** (2 / POWER), s)


# --- Materials --------------------------------------------------------------------------------------------------------

def materials():
    """The boss's (polish_tusk_boss.materials: tusk_*) and two shades under its gold and its tusks' brown."""
    m = tb.materials()
    m["gold_deep"] = k.material("tusk_gold_deep", palette=0x13, metallic=0.4, roughness=0.42)
    m["brown_dark"] = k.material("tusk_brown_dark", palette=0xa4, metallic=0.3, roughness=0.5)
    return m


# --- The middle line ----------------------------------------------------------------------------------------------

class Path:
    """A tube's middle line: TABLE sampled smooth (Catmull-Rom) every step along x; at each station its middle (x, y,
    z), the direction square to it in plan (towards up the screen), its half-width (the pixels' half-height times
    the line's cosine) and half-height."""

    def __init__(self, table, tip, step=0.4):
        self.tip = tip
        pts = k.profile(table, step)
        self.xs, self.st = [], []
        n = len(pts)
        for i, (x, y, hv) in enumerate(pts):
            a, b = pts[max(0, i - 1)], pts[min(n - 1, i + 1)]
            slope = (b[1] - a[1]) / (b[0] - a[0])
            cos = 1.0 / math.sqrt(1.0 + slope * slope)
            side = Vector((-slope * cos, cos, 0.0))
            hw = max(0.03, hv * cos)
            ratio = PIPE_RATIO + (TUSK_RATIO - PIPE_RATIO) * sstep(TUSK_X[0], TUSK_X[0] + 6.0, x)
            hh = hw * ratio
            if x < PIPE_FLARE[0]:
                hh = min(hh, PIPE_FLARE[1])
            z = Z0 - TUSK_SINK * max(0.0, (x - TUSK_X[0]) / (tip - TUSK_X[0])) ** 2
            self.xs.append(x)
            self.st.append((Vector((x, y, z)), side, hw, hh))

    def at(self, x):
        xs = self.xs
        if x <= xs[0]:
            return self.st[0]
        if x >= xs[-1]:
            return self.st[-1]
        lo, hi = 0, len(xs) - 1
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if xs[mid] <= x:
                lo = mid
            else:
                hi = mid
        t = (x - xs[lo]) / (xs[hi] - xs[lo])
        (c0, s0, w0, h0), (c1, s1, w1, h1) = self.st[lo], self.st[hi]
        return c0.lerp(c1, t), s0.lerp(s1, t).normalized(), w0 + (w1 - w0) * t, h0 + (h1 - h0) * t

    def point(self, x, phi, grow=0.0):
        """The point of the section at x at angle phi (radians; 0 the far side, pi/2 the top), grown out by grow."""
        c, side, hw, hh = self.at(x)
        u, v = se(phi)
        return c + side * ((hw + grow) * u) + Vector((0.0, 0.0, (hh + grow) * v))

    def ring(self, x, grow=0.0, segments=32):
        return [self.point(x, 2 * math.pi * j / segments, grow) for j in range(segments)]


def stations(x0, x1, step):
    count = max(1, int(math.ceil((x1 - x0) / step)))
    return [x0 + (x1 - x0) * i / count for i in range(count + 1)]


# --- The body: root, ball, pipe ------------------------------------------------------------------------------------

def root_sections():
    """(x, y, half-width, half-height) from beyond the picture's edge to inside the ball."""
    out = [(-84.6, ROOT_Y, ROOT_HW, ROOT_HH), (-75.0, ROOT_Y, ROOT_HW, ROOT_HH), (-66.0, ROOT_Y, ROOT_HW, ROOT_HH)]
    s0, s1 = SHOULDER
    for x in stations(-60.0, s0, 1.0)[:-1]:
        out.append((x, ROOT_Y, ROOT_HW, ROOT_HH))
    for i in range(21):
        x = s0 + (s1 - s0) * i / 20
        f = sstep(s0, s1, x)
        out.append((x, ROOT_Y + (NECK_Y - ROOT_Y) * f, ROOT_HW + (NECK_HW - ROOT_HW) * f,
                    ROOT_HH + (NECK_HH - ROOT_HH) * f))
    for x in stations(s1, NECK_END, 0.8)[1:]:
        out.append((x, NECK_Y, NECK_HW - 0.05, NECK_HH))
    return out


def root(m):
    rings = []
    for x, y, hw, hh in root_sections():
        ring = []
        for j in range(40):
            u, v = se(2 * math.pi * j / 40)
            ring.append(Vector((x, y + hw * u, Z0 + hh * v)))
        rings.append(ring)
    first, last = root_sections()[0], root_sections()[-1]
    return k.loft("root", rings, m["gold"], start_point=(first[0], first[1], Z0), end_point=(last[0], last[1], Z0))


def pipe(m, path):
    """The pipe from inside the ball to its lip, the lip closing inside the tusk's root."""
    rings = [path.ring(x, 0.0, 28) for x in stations(PIPE_X[0], PIPE_X[1], 0.6)]
    grown, closing, end, proud = LIP
    for x, g in ((grown, proud), (closing, proud), (closing + 0.2 * (end - closing), proud * 0.7),
                 (end - 0.12, proud * 0.2), (end, -0.3)):
        rings.append(path.ring(x, g, 28))
    c0, c1 = path.at(PIPE_X[0])[0], path.at(end)[0]
    return k.loft("pipe", rings, m["gold"], start_point=tuple(c0), end_point=tuple(c1))


def joint_ball(m, segments=40, rings=20):
    """The ball: rings round the x axis (its poles inside the neck and the pipe) pushed out to a superellipsoid,
    (|x/rx|^p + |y/ry|^p)^(2/p) + (z/rz)^2 = 1, p the far half's power where y is above its middle and the near half's
    below. (Lofted from explicit rings: bmesh's create_uvsphere orders its faces differently every run.)"""
    (bx, by), (rx, ry, rz) = BALL
    p_far, p_near = BALL_POWER

    def surface(d):
        p = p_far if d.y > 0 else p_near
        f = (abs(d.x / rx) ** p + abs(d.y / ry) ** p) ** (2.0 / p) + (d.z / rz) ** 2
        t = f ** -0.5
        return Vector((bx + d.x * t, by + d.y * t, Z0 + d.z * t))
    out = []
    for i in range(1, rings):
        th = math.pi * i / rings
        out.append([surface(Vector((-math.cos(th), math.sin(th) * math.cos(2 * math.pi * j / segments),
                                    math.sin(th) * math.sin(2 * math.pi * j / segments)))) for j in range(segments)])
    return k.loft("ball", out, m["gold"], start_point=tuple(surface(Vector((-1.0, 0.0, 0.0)))),
                  end_point=tuple(surface(Vector((1.0, 0.0, 0.0)))))


def body(m, path):
    """Root, ball and pipe joined by an exact union."""
    main = root(m)
    ball = joint_ball(m)
    tube = pipe(m, path)
    mk.boolean(main, [ball, tube], "UNION")
    mk.cleanup(main, dissolve=0.0)
    tb.ngons_to_triangles(main)
    main.name = main.data.name = "body"
    return main


def tusk(m, path):
    rings = [path.ring(x, 0.0, 24) for x in stations(TUSK_X[0], path.tip - 0.15, 0.55)]
    c0 = path.at(TUSK_X[0])[0]
    tip = path.at(path.tip)[0]
    direction = (tip - path.at(path.tip - 0.6)[0]).normalized()
    obj = k.loft("tusk", rings, m["brown"], start_point=tuple(c0), end_point=tuple(tip + direction * 0.25))
    return obj


# --- The parts on the pipe --------------------------------------------------------------------------------------------

def shell(name, path, x0, x1, a0, a1, lift, mat, sink=0.3, bevel=0.2, step=1.6):
    """A band of the pipe's sections from x0 to x1 over the angles a0..a1 (degrees; all round if they span 360),
    lift out of its surface and sunk sink into it; its edges bevelled."""
    full = a1 - a0 >= 359.9
    xs = stations(x0, x1, step)
    if full:
        phis = [2 * math.pi * j / 28 for j in range(28)]
    else:
        count = max(4, int(math.ceil((a1 - a0) / 9.0)))
        phis = [math.radians(a0 + (a1 - a0) * j / count) for j in range(count + 1)]
    bm = bmesh.new()
    outer = [[bm.verts.new(path.point(x, p, lift)) for p in phis] for x in xs]
    inner = [[bm.verts.new(path.point(x, p, -sink)) for p in phis] for x in xs]
    n, J = len(xs) - 1, len(phis)
    spans = range(J) if full else range(J - 1)
    for i in range(n):
        for j in spans:
            j2 = (j + 1) % J
            bm.faces.new((outer[i][j], outer[i + 1][j], outer[i + 1][j2], outer[i][j2]))
            bm.faces.new((inner[i][j2], inner[i + 1][j2], inner[i + 1][j], inner[i][j]))
    for i in (0, n):
        for j in spans:
            j2 = (j + 1) % J
            bm.faces.new((outer[i][j], outer[i][j2], inner[i][j2], inner[i][j]))
    if not full:
        for j in (0, J - 1):
            for i in range(n):
                bm.faces.new((outer[i][j], inner[i][j], inner[i + 1][j], outer[i + 1][j]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.data.materials.append(mat)
    if bevel > 0:
        mk.bevel(obj, bevel, 2, 30.0)
    return obj


def surface_frame(path, x, phi):
    """A frame on the pipe's surface at (x, angle phi): its point, and axes (along the pipe, across, out)."""
    p = path.point(x, phi)
    across = (path.point(x, phi + 0.01) - path.point(x, phi - 0.01)).normalized()
    along = (path.point(x + 0.05, phi) - path.point(x - 0.05, phi)).normalized()
    out = along.cross(across).normalized()
    if out.dot(p - path.at(x)[0]) < 0:
        out = -out
    across = out.cross(along).normalized()
    return p, along, across, out


def stud(name, path, x, angle, profile, mat, recess=None, recess_mat=None):
    """A lathed part standing square to the pipe's surface at (x, angle in degrees); its faces between the radii
    recess[0] and recess[1] under the height recess[2] given recess_mat."""
    p, along, across, out = surface_frame(path, x, math.radians(angle))
    obj = mk.lathe(name, profile, (0.0, 0.0), mat, segments=28)
    if recess is not None:
        r0, r1, top = recess
        mk.paint(obj, lambda c, n: recess_mat if r0 < math.hypot(c.x, c.y) < r1 and c.z < top else None)
    frame = Matrix(((along.x, across.x, out.x, p.x), (along.y, across.y, out.y, p.y), (along.z, across.z, out.z, p.z),
                    (0.0, 0.0, 0.0, 1.0)))
    obj.data.transform(frame)
    obj.data.update()
    k.recalc_normals(obj)
    return obj


def common_parts(m, path):
    parts = []
    for i, (x0, x1, a0, a1, lift) in enumerate(CLAMPS):
        parts.append(shell(f"clamp{i}", path, x0, x1, a0, a1, lift, m["steel"], bevel=0.25))
    x0, x1, a0, a1, lift = LUG
    parts.append(shell("lug", path, x0, x1, a0, a1, lift, m["steel"], bevel=0.25))
    return parts


def band_a(m, path):
    """Arm A's band: the steel collar, the gold ring after it, the brown strap and its bar."""
    x0, x1, lift = COLLAR
    collar = shell("collar", path, x0, x1, 0.0, 360.0, lift, m["steel"], bevel=0.3)
    x0, x1, lift = GOLD_RING
    ring = shell("gold_ring", path, x0, x1, 0.0, 360.0, lift, m["gold"], bevel=0.2)
    x0, x1, lift = STRAP
    strap = shell("strap", path, x0, x1, 0.0, 360.0, lift, m["brown"], bevel=0.18)
    x0, x1, a0, a1, lift = STRAP_BAR
    bar = shell("strap_bar", path, x0, x1, a0, a1, lift, m["brown"], bevel=0.18)
    return [collar, ring, strap, bar]


def band_b(m, path):
    """Arm B's band: the steel eye on the far side (a domed boss in a dark recess), the four ring grooves."""
    x, angle = EYE
    parts = [stud("eye", path, x, angle, EYE_PROFILE, m["steel"], EYE_RECESS, m["core"])]
    width, lift = GROOVE
    for i, xm in enumerate(GROOVES):
        parts.append(shell(f"groove{i}", path, xm - width / 2, xm + width / 2, 0.0, 360.0, lift, m["gold"],
                           bevel=0.16, step=0.9))
    return parts


# --- Painting ---------------------------------------------------------------------------------------------------------

def banded(obj, light, bands, bias=None):
    """polish_tusk_boss.banded (faces in bands of the light at their vertices, split along smooth borders) with a
    bias(point) added to each vertex's value."""
    lv = Vector(light).normalized()
    me = obj.data
    normals = [Vector() for _ in me.vertices]
    for poly in me.polygons:
        for vi in poly.vertices:
            normals[vi] += poly.normal * poly.area
    values = [(n.normalized().dot(lv) if n.length > 0 else 0.0) + (bias(v.co) if bias else 0.0)
              for n, v in zip(normals, me.vertices)]
    band_split(obj, values, bands)
    return obj


def body_shade(to_a):
    wx, ww, wd = WAIST_SHADE
    p0, p1, pd = PIPE_SHADE

    def bias(co):
        x = to_a(co.x)
        return -wd * math.exp(-((x - wx) / ww) ** 2) - pd * sstep(p0, p1, x)
    return bias


def paint_body(obj, m, to_a):
    banded(obj, PAINT_LIGHT, [(lo, m[name]) for lo, name in GOLD_BANDS], body_shade(to_a))
    x0, x1, ny = RIM
    mk.paint(obj, lambda c, n: m["gold"] if x0 <= to_a(c.x) <= x1 and n.y < ny and abs(n.z) < 0.4 else None)
    k.smooth(obj, 50)


def paint_tusk(obj, m, to_a):
    tb.banded(obj, TUSK_LIGHT, [(lo, m[name]) for lo, name in TUSK_BANDS])
    k.smooth(obj, 60)


def paint_gold_part(obj, m, to_a):
    light = Vector(PAINT_LIGHT).normalized()

    def pick(c, n):
        d = n.dot(light)
        return m["gold_light"] if d > 0.84 else m["gold_lit"] if d > 0.66 else m["gold"] if d > 0.4 else \
            m["gold_dark"] if d > 0.0 else m["gold_deep"]
    mk.paint(obj, pick)
    k.smooth(obj, 40)


def paint_clamp(obj, m, to_a):
    """The clamps dark steel as the sprites draw them (0x02-0x08), their edges towards the light lit."""
    light = Vector((-0.55, 0.45, 0.7)).normalized()

    def pick(c, n):
        d = n.dot(light)
        return m["steel_lit"] if d > 0.88 else m["steel"] if d > 0.76 else m["steel_dark"] if n.z > -0.3 else \
            m["core"]
    mk.paint(obj, pick)
    k.smooth(obj, 40)


def paint_collar(obj, m, to_a):
    """Lit steel over its far half and top, glossy black over its near side, its lowest edge steel (the sprite's
    lit rim)."""
    light = Vector((-0.55, 0.45, 0.7)).normalized()

    def pick(c, n):
        if n.z < -0.5:
            return m["core"]
        if n.y < -0.9 and n.z < 0.35:
            return m["steel"]
        if n.y < -0.3:
            return m["black"]
        d = n.dot(light)
        return m["steel_light"] if d > 0.88 else m["steel_lit"] if d > 0.6 else m["steel"]
    mk.paint(obj, pick)
    k.smooth(obj, 40)


def paint_strap(obj, m, to_a):
    light = Vector((-0.55, 0.45, 0.7)).normalized()
    mk.paint(obj, lambda c, n: m["brown"] if n.dot(light) > 0.75 else m["brown_dark"] if n.z > -0.3 else m["core"])
    k.smooth(obj, 40)


def paint_eye(obj, m, to_a):
    """Steel by the light, its recess (core) kept."""
    light = Vector((-0.55, 0.45, 0.7)).normalized()
    core = obj.data.materials.find(m["core"].name)

    def pick(c, n):
        d = n.dot(light)
        return m["steel_light"] if d > 0.9 else m["steel_lit"] if d > 0.6 else m["steel"] if d > 0.2 else \
            m["steel_dark"]
    for poly in obj.data.polygons:
        if poly.material_index != core:
            poly.material_index = mk.slot_of(obj, pick(poly.center, poly.normal))
    k.smooth(obj, 45)


PAINTERS = {"body": paint_body, "tusk": paint_tusk, "gold_ring": paint_gold_part, "collar": paint_collar,
            "strap": paint_strap, "strap_bar": paint_strap, "eye": paint_eye}


def painter_of(name):
    if name.startswith("groove"):
        return paint_gold_part
    if name.startswith("clamp") or name == "lug":
        return paint_clamp
    return PAINTERS[name]


# --- Whole ------------------------------------------------------------------------------------------------------------

def build_arm(arm, m):
    """An arm's parts, whole, in its own frame (B mirrored), painted."""
    path = Path(TABLE + TAILS[arm], TAILS[arm][-1][0])
    parts = [body(m, path), tusk(m, path)] + common_parts(m, path)
    parts += band_a(m, path) if arm == "a" else band_b(m, path)
    for obj in parts:
        mk.apply(obj)
    if arm == "b":
        flip = Matrix.Translation((1.0, 0.0, 0.0)) @ Matrix.Scale(-1.0, 4, (1.0, 0.0, 0.0))
        for obj in parts:
            obj.data.transform(flip)
            obj.data.flip_normals()
            obj.data.update()
    to_a = (lambda x: x) if arm == "a" else (lambda x: 1.0 - x)
    for obj in parts:
        k.recalc_normals(obj)
        painter_of(obj.name)(obj, m, to_a)
    bpy.context.view_layer.update()
    return parts


def cut(source, box, cap_mat):
    """polish_coral_manta.cut: the part of an object inside a box (x0, x1, y0, y1), its cuts capped with cap_mat facing
    out of their cut (given their material at once, so that a cap a later plane splits keeps it), its normals the uncut
    object's, its faces' winding kept. None if nothing of it is inside."""
    x0, x1, y0, y1 = box
    corners = [source.matrix_world @ Vector(c) for c in source.bound_box]
    if (max(c.x for c in corners) <= x0 or min(c.x for c in corners) >= x1 or
            max(c.y for c in corners) <= y0 or min(c.y for c in corners) >= y1):
        return None
    obj = source.copy()
    obj.data = source.data.copy()
    bpy.context.scene.collection.objects.link(obj)
    cap_index = mk.slot_of(obj, cap_mat)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    layer = bm.faces.layers.int.new("cap")
    planes = (((x0, 0, 0), (-1, 0, 0)), ((x1, 0, 0), (1, 0, 0)), ((0, y0, 0), (0, -1, 0)), ((0, y1, 0), (0, 1, 0)))
    for co, no in planes:
        if not bm.faces:
            break
        result = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-6, plane_co=co,
                                        plane_no=no, clear_outer=True)
        edges = [e for e in result["geom_cut"] if isinstance(e, bmesh.types.BMEdge) and e.is_valid]
        open_edges = [e for e in edges if len(e.link_faces) == 1]
        if not open_edges:
            continue
        filled = bmesh.ops.holes_fill(bm, edges=open_edges, sides=0)
        if not filled["faces"]:
            continue
        for f in bmesh.ops.triangulate(bm, faces=filled["faces"])["faces"]:
            f.normal_update()
            if f.normal.dot(Vector(no)) < 0:
                f.normal_flip()
            f.material_index = cap_index
            f.smooth = False
            f[layer] = 1
    if not bm.faces:
        bm.free()
        bpy.data.objects.remove(obj)
        return None
    bm.normal_update()
    bm.faces.index_update()
    cap_ids = {f.index for f in bm.faces if f[layer] == 1}
    bm.faces.layers.int.remove(layer)
    bm.to_mesh(obj.data)
    bm.free()
    shading = mk.NormalSource(source)
    mesh = obj.data
    normals = []
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            n = None
            if poly.index not in cap_ids:
                n = shading.normal(mesh.vertices[mesh.loops[li].vertex_index].co, poly.center)
            normals.append(tuple(n if n is not None else CAP_NORMAL))
    mesh.normals_split_custom_set(normals)
    return obj


def pieces_of(arm):
    return [("tusk_arm_%s_%d" % (arm, sprite), sprite, (-84.0 + 24 * i, -60.0 + 24 * i, -14.0, 14.0))
            for i, sprite in enumerate(ARMS[arm])]


def export_pieces(arm, whole, m, options, sheet):
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    scores = {}
    for name, sprite, box in pieces_of(arm):
        if only and name not in only:
            continue
        parts = []
        for src in whole:
            cap = m[CAPS.get(src.name, "core")]
            piece = cut(src, box, cap)
            if piece is not None:
                parts.append(piece)
        tb.db.drop_unused(parts)
        mk.transform(parts, Matrix.Translation((-(box[0] + box[1]) / 2, -(box[2] + box[3]) / 2, 0.0)))
        bpy.context.view_layer.update()
        triangulate(parts)
        if "stats" in options:
            for obj in sorted(parts, key=lambda o: -mk.triangles([o]))[:10]:
                print("    %-14s %6d" % (obj.name, mk.triangles([obj])))
        joined = tb.db.join(parts, name)
        for src in whole:
            src.hide_render = True
        if sheet:
            scores[name] = mk.compare("%s (4 %d)" % (name, sprite), mk.coverage([joined], 24, 28),
                                      k.sprite_mask(sheet, sprite))
        mk.report(name, [joined], os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, [joined])
        bpy.data.objects.remove(joined)
        for src in whole:
            src.hide_render = False
    return scores


def build():
    k.reset()
    options = k.args()
    m = materials()
    sheet = os.path.join(options["check"], "enemy_4.png") if "check" in options else None
    arms = [options["arm"]] if "arm" in options else ["a", "b"]
    for arm in arms:
        for obj in mk.meshes():
            bpy.data.objects.remove(obj)
        whole = build_arm(arm, m)
        print("arm %s: %d triangles, %d objects" % (arm, mk.triangles(whole), len(whole)))
        for obj in sorted(whole, key=lambda o: -mk.triangles([o])):
            print("   %-14s %6d" % (obj.name, mk.triangles([obj])))
        if sheet:
            mk.compare("arm %s whole (4 %s)" % (arm, " ".join(str(s) for s in ARMS[arm])),
                       mk.coverage(whole, 168, 28), k.sprite_mask(sheet, list(ARMS[arm])))
        bpy.context.scene.view_settings.view_transform = "Standard"
        if "preview" in options:
            mk.preview(options["preview"] + "tusk_arm_%s_whole" % arm, whole, size=(168, 28), scale=6, distance=3.6)
        if "whole" in options:
            copies = []
            for obj in whole:
                c = obj.copy()
                c.data = obj.data.copy()
                bpy.context.scene.collection.objects.link(c)
                copies.append(c)
            triangulate(copies)
            mk.export(copies, options["whole"] + arm + ".glb")
            for c in copies:
                bpy.data.objects.remove(c)
        if options.get("only") != "none":
            scores = export_pieces(arm, whole, m, options, sheet)
            if scores:
                print("arm %s silhouettes: %s" % (arm, ", ".join("%s %.3f" % (n, s) for n, s in scores.items())))


if __name__ == "__main__":
    build()
