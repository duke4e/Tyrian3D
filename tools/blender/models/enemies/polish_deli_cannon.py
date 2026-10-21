"""DELI's long blue cannons on the top layer (sheet C; DELI, New Deli, VAULT, DEEP ICE), polished (2026-10-21; it
replaces wave3_x_cannon.py, a lofted capsule and boxes on a purple block). The level events lay each cannon out as four
sprites side by side on the top layer: pointing right C 269 (2x2), 271 (2x2), 273 (2x2) and the 1x1 275, pointing left
the 1x1 C 238, 239, 241, 243 (enemies 228-231 and 232-235, and episode 6's copies 1590, 1591, 1626-1635). models.cfg:
model deli_cannon_breech / _mount / _barrel / _muzzle and deli_cannon_l_muzzle / _l_barrel / _l_mount / _l_breech ...
origin; sprite c 269 deli_cannon_breech yaw=0 height=-6 and so on (height=-6: the cannon stands on background 3's
plane, the purple platform it is set on; without it the pieces float 6 pixels over it). The damaged looks (C 231 233
235 237 and 276 277 279 281) are polish_deli_cannon_dmg.py's, built from this script's cannon.

Where the levels put the pieces (DELI 1:19 and New Deli 3:23, read from the .lvl events): four top-layer events (7) at
one time with one link; pointing right 228 at x, 229 at x + 24, 230 at x + 48 and the 1x1 231 at x + 76; pointing left
the 1x1 232 at x, 233 at x + 8, 234 at x + 32, 235 at x + 56. Both levels turn the small enemies' adjustment on (event
26) while the cannons come, so the 1x1 pieces are drawn 10 pixels left and 7 up: the muzzle cell's edge meets the
barrel's, in the top half of the row, exactly as the sheet draws them side by side (one 84 x 28 picture). (VAULT and
DEEP ICE copy New Deli's waves without its event 26: there the 1x1 pieces sit 10 pixels right of and 7 below that
place; the episode 6 composer's matter, not the models'.)

C 238 + 239 + 241 + 243 are C 269 + 271 + 273 + 275 mirrored about the cannon's middle in shape (the silhouettes are
equal but for the muzzle cap's tip, a pixel shorter on the left one, and 3 outline pixels), but not pixel for pixel:
the artist lit the left one from the left too (the sight's and the pedestal's lit sides are not mirrored). So one
cannon is built and mirrored (the renderer lights it). No other sprite of any sheet is these mirrored, turned or in
other ramps.

The purple round the mount (C 271's ramp-5 pixels, and the gaps inside the gun) is DELI's background 3 painted into the
sprite: every one of them equals the top layer's purple platform tile (the cannons stand on those platforms). It is the
map's: left out, and the silhouettes are checked against the cannon's own pixels.

As the sprites draw it (columns and rows of the 84 x 28 picture pointing right): a silver breech (columns 0-19 of rows
2-9), its rear end rounded, two narrow rings and grooves near its front (columns 15-18); under it a blue handle (rows
10-13) from a rounded knob at its rear (columns 1-7, down to row 14) forward into the receiver; under that a finned
block (columns 7-20 of rows 13-19): a rounded end, then four fins between dark slots; a tall blue block at the breech's
front (columns 20-26 of rows 1-12); the receiver (columns 26-51): a lower box with a lit rail (row 10) and a small box
on its top (columns 30-33 of rows 2-6), the raised sight (columns 33-42 of rows 0-8, a darker window in its face, a
darker base band, rows 7-8), a dark slot under the sight (columns 34-38 of rows 9-12), the front hull round the
barrel's root (columns 42-51 of rows 2-7) over a lower block and a lit ledge (columns 39-49 of rows 8-13); under the
receiver the trunnion block (columns 29-43 of rows 13-24) standing on the platform: a lit sloping face at its lower
left under a dark diagonal edge, a dark recessed panel, a groove, a narrow plate and a base strip; the barrel (columns
52-66 of rows 3-7) with a collar at its root, a taller collar (columns 55-58) and a rim where it enters the muzzle
housing; a loop hanging under it (columns 55-62 of rows 7-12, a hole in it) and a block beside it (columns 62-65); the
muzzle housing (columns 66-77 of rows 1-12): the upper jaw lit along its top, the rounded cap bulging down at its end,
a lower jaw, and between them the glowing port (columns 66-72 of rows 8-10), hottest at its left end.

The sprites draw the cannon from the side, as DELI's tower and its gun on the mast: as those, the cannon is built
upright (x along the gun, h up, d back: its front, which the game's camera sees, towards -d) and leaned back up the
screen BETA degrees about x, so that the game's camera (20 degrees from straight down) sees its side face on, the
picture as the sprites draw it (each part's height h is the picture's y: the game view is the sprites' layout; seen
from straight above the parts' tops show too, so the plan reaches a little past the sprites' pixels). Its foot (the
trunnion's base) stands on the platform (z = 0), the gun rising from it up the screen, its back half under the
platform at the foot cut away. Built whole, then cut along the sprites' edges (x = -18, 6, 30; the 1x1 muzzle cell
y = 0..14) with polish_arch.cut (the pieces keep the whole's shading across the cuts), each piece moved to its sprite's
centre; the left cannon is the whole mirrored about x = 0 and cut along its sprites' edges (x = -30, -6, 18).

Parts: the breech, the barrel and its collars turned about x (the breech a little square in section, its rings raised
and grooves sunk); the handle a round bar along its path; the blocks, the loop (a frame round its hole), the trunnion's
brace and the muzzle housing prisms of their side profiles extruded across and bevelled (exact booleans cut the fin
slots, the sight's window, the trunnion's recessed panel and groove, the loop's hole and the port into them); painted as
the sprites shade them (the front its shade, tops and their rounded edges lighter, as the sprites' lit top lines, lower
faces darker; the paint's edges cut along smooth lines where the sprite's are not the parts' edges): blues 0x32-0x3e
(the even shades), the breech's greys 0x05-0x0d, the cuts and slots 0x01. On the trunnion's face a brace along the
sprites' dark diagonal, the recessed panel to its right. The port's lens glows (well under 1: 0x76 0.3, 0x7a 0.42, 0x7c
0.55 from its rim in), a dimmer strip along the port's floor to its right (0x7a, 0x76, 0x74 0.22). Each part is split
along the cuts before the lean (presplit: its shape and shading kept), so that polish_deli_cannon_dmg.py's finer faces
leave the pieces' edges as they are; the mirror sets the corner normals again (mirrored()), so that the left pieces
are shaded as the right ones.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the platform (z = 0); the
whole's origin is the middle of the picture (column c is x = c + 0.5 - 42, row r is y = 13.5 - r).

Replaces wave3_x_cannon.py: delete it (nothing else is in it; only wave3_ao_deli.py imports it, whose cannon section
goes with it: polish_deli_cannon_dmg.py replaces that, see its docstring), and wave3_x_art.py's CANNON and CANNON_L
(only wave3_ao_deli.py's C_FRAMES reads them).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the whole's and each piece's
silhouette against enemy_C.png, the platform's pixels left out, seen from straight above and as the game's camera sees
it), --preview <prefix>, --only <name,...>, --whole <prefix> (the leaned wholes, both ways, as <prefix>cannon.glb and
<prefix>cannon_l.glb).
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
from polish_arch import cut  # noqa: E402  (polish_machine_kit.cut without its material indices shifted twice)
from polish_k_pod import triangulate  # noqa: E402

# The pieces: (name, sprite, 2x2, the box it covers in the whole's coordinates (x0, x1, y0, y1)), pointing right and
# pointing left.
PIECES = [("deli_cannon_breech", 269, True, (-42.0, -18.0, -14.0, 14.0)),
          ("deli_cannon_mount", 271, True, (-18.0, 6.0, -14.0, 14.0)),
          ("deli_cannon_barrel", 273, True, (6.0, 30.0, -14.0, 14.0)),
          ("deli_cannon_muzzle", 275, False, (30.0, 42.0, 0.0, 14.0))]
PIECES_L = [("deli_cannon_l_muzzle", 238, False, (-42.0, -30.0, 0.0, 14.0)),
            ("deli_cannon_l_barrel", 239, True, (-30.0, -6.0, -14.0, 14.0)),
            ("deli_cannon_l_mount", 241, True, (-6.0, 18.0, -14.0, 14.0)),
            ("deli_cannon_l_breech", 243, True, (18.0, 42.0, -14.0, 14.0))]
# The sprites side by side as the levels lay them out (sprite, 2x2, first column of the 84 x 28 picture).
LAYOUT = {False: [(269, True, 0), (271, True, 24), (273, True, 48), (275, False, 72)],
          True: [(238, False, 0), (239, True, 12), (241, True, 36), (243, True, 60)]}

# The lean: the cannon's up turned back up the screen this far from upright (the game's camera then sees its side face
# on); the upright frame's origin is put at (0, PY, PZ).
BETA = math.radians(70.0)
PY, PZ = -0.25, 4.6
LEAN = Matrix.Translation((0.0, PY, PZ)) @ Matrix.Rotation(-BETA, 4, "X")
FLOOR_CUT = -0.6                 # nothing below this (the platform hides it)

# --- The parts' measures, in the upright frame: x along the gun, h up (the picture's y), d back ------------------
# The breech: its axis's height, radius, the superellipse power of its section, its tip and front end; the rings
# (raised) and grooves (sunk) near its front: its profile there (x, radius), and the bands (x0, x1, raised).
BREECH = (8.0, 3.9, 2.3, -41.9, -21.6)
BREECH_RINGS = [(-27.3, 3.9), (-27.15, 4.06), (-26.2, 4.06), (-26.05, 3.62), (-25.2, 3.62), (-25.05, 4.06),
                (-24.2, 4.06), (-24.05, 3.62), (-23.2, 3.62), (-23.05, 3.9)]
BREECH_BANDS = [(-27.2, -26.12, True), (-26.12, -25.12, False), (-25.12, -24.12, True), (-24.12, -23.12, False)]
# The handle: its path (x, h, radius) from its front end in the block to its knob and up into the breech's rear.
HANDLE = [(-20.6, 2.05, 1.9), (-26.0, 2.0, 1.95), (-33.0, 1.85, 2.0), (-37.4, 1.45, 2.15), (-39.6, 1.25, 2.25),
          (-40.8, 2.0, 2.0), (-41.1, 3.4, 1.6), (-40.7, 4.6, 1.25)]
# The finned block: its side profile, depth, and slots (x, width) cut into its front and foot.
FIN_BLOCK = [(-34.6, 0.0), (-34.6, -4.6), (-33.8, -5.5), (-23.2, -5.6), (-21.9, -4.8), (-21.0, -3.4), (-21.0, 0.45),
             (-33.6, 0.45)]
FIN_D = 3.0
FIN_SLOTS = [(-29.55, 0.75), (-27.5, 0.6), (-25.5, 0.6), (-23.5, 0.6)]
# The tall block at the breech's front: side profile, depth.
REAR_BLOCK = [(-22.2, 0.8), (-15.8, 0.8), (-15.8, 12.9), (-20.7, 12.9), (-22.2, 11.4)]
REAR_D = 4.4
# The receiver: its core (x0, x1, h0, h1, depth), the lower box's profile and depth, its rail (x0, x1, h0, h1), the
# small box and the sight (x0, x1, h0, h1, depth), the sight's base band, its window (x0, x1, h0, h1, how deep), the
# front hull, the lower block and the ledge (x0, x1, h0, h1, depth); the rod in the slot under the sight (x0, x1, h, r).
CORE = (-16.0, 4.0, 1.0, 9.0, 3.1)
LOWER_BOX = [(-16.3, 0.4), (-8.4, 0.4), (-8.4, 6.6), (-12.3, 6.6), (-12.3, 9.6), (-16.3, 9.6)]
LOWER_D = 3.9
RAIL = (-15.7, -8.9, 3.25, 4.55)
SMALL_BOX = (-12.1, -8.6, 7.0, 12.2, 2.9)
SIGHT = (-8.8, 0.8, 7.1, 13.9, 3.4)
SIGHT_BASE = (-8.8, 0.8, 5.0, 7.3, 3.75)
WINDOW = (-6.5, -1.1, 9.5, 11.6, 0.35)
HULL = (0.4, 10.0, 6.1, 11.9, 3.5)
LOWER_BLOCK = (-3.3, 4.4, 2.2, 6.5, 3.8)
LEDGE = (-3.3, 8.3, -0.3, 2.6, 4.1)
SLOT_ROD = (-7.3, -3.8, 4.0, 0.5)
# The trunnion block: side profile, depth; its recessed panel's outline (its left edge the sprites' dark diagonal, the
# face below it painted lit), how deep; the groove beside it (x0, x1); the brace along the diagonal; the base strip
# (h0, h1, how far out).
TRUNNION = [(-12.6, -10.8), (1.0, -10.8), (1.0, 0.4), (-12.6, 0.4)]
TRUNNION_D = 4.6
PANEL = [(-11.8, -0.9), (-2.45, -0.9), (-2.45, -7.0), (-6.6, -7.0)]
PANEL_DEEP = 0.7
GROOVE_X = (-3.25, -2.45)
STRUT = ((-11.75, 0.25), (-6.45, -7.35), 0.62)   # its ends (x, h), half-width
BASE_STRIP = (-10.4, -7.4, 0.3)
# The barrel: its axis's height, radius, from x to x; the collars (x0, x1, radius).
BARREL = (8.7, 2.45, 9.4, 24.9)
COLLARS = [(9.4, 10.9, 3.0), (13.6, 17.1, 3.1), (23.3, 24.6, 2.8)]
# The loop under the barrel: a frame (x0, x1, h0, h1, its corners' radius, depth) with a hole (x0, x1, h0, h1); the
# block beside it (x0, x1, h0, h1, depth).
LOOP = (12.9, 20.6, 1.5, 7.3, 0.9, 1.1)
LOOP_HOLE = (15.5, 19.5, 3.5, 6.4)
SIDE_BLOCK = (19.9, 24.5, 0.7, 7.0, 2.6)
# The muzzle housing: (x0, x1, h0, h1), its corners' radii (bottom left, bottom right, top right, top left), depth; the
# port's outline (an L: under the upper jaw's left part and the lower jaw), how deep; the lens (x, h, radius) and the
# strip along the port's floor (x0, x1, h0, h1).
HOUSING = (24.0, 35.6, 2.0, 13.0)
HOUSING_RADII = (0.5, 1.6, 3.0, 0.5)
HOUSING_D = 3.4
PORT = [(23.7, 2.95), (31.1, 2.95), (31.1, 4.15), (28.15, 4.15), (28.15, 6.4), (23.7, 6.4)]
PORT_DEEP = 1.3
LENS = (25.6, 4.55, 1.6)
GLOW_STRIP = (26.6, 30.9, 3.05, 4.05)


def materials():
    pal = k.level_palette()

    def mat(name, index, metallic=0.3, roughness=0.36, glow=0.0):
        if glow > 0:
            return k.material(name, palette=index, metallic=0.0, roughness=roughness, emission=pal[index],
                              emission_strength=glow)
        return k.material(name, palette=index, metallic=metallic, roughness=roughness)
    m = {"seam": mat("dcan_seam", 0x01, 0.2, 0.6)}
    for s in (5, 7, 9, 11, 13):
        m["g%x" % s] = mat("dcan_grey%x" % s, s, 0.3, 0.3)
    for s in (2, 4, 6, 8, 10, 12, 14):
        m["b%x" % s] = mat("dcan_blue%x" % s, 0x30 | s, 0.18, 0.4)
    m["glow_tail"] = mat("dcan_glow_tail", 0x74, roughness=0.35, glow=0.22)
    m["glow_rim"] = mat("dcan_glow_rim", 0x76, roughness=0.3, glow=0.3)
    m["glow_mid"] = mat("dcan_glow_mid", 0x7a, roughness=0.2, glow=0.42)
    m["glow_core"] = mat("dcan_glow_core", 0x7c, roughness=0.1, glow=0.55)
    return m


BLUES = ("b2", "b4", "b6", "b8", "ba", "bc", "be")


def blue(shade):
    """The blue material key nearest a shade (2-14)."""
    return min(BLUES, key=lambda key: abs(int(key[1], 16) - shade))


# --- Helpers ------------------------------------------------------------------------------------------------------

def side_prism(name, outline, depth, mat, d_mid=0.0):
    """A side profile [(x, h)] extruded across d_mid - depth .. d_mid + depth."""
    return mk.prism(name, outline, d_mid - depth, d_mid + depth, mat, axis="y")


def rect(x0, x1, h0, h1):
    return [(x0, h0), (x1, h0), (x1, h1), (x0, h1)]


def lathe_x(name, profile, ch, mat, segments=28, power=2.0, cd=0.0):
    """A part turned about an axis along x through (d, h) = (cd, ch): profile [(x, radius)], increasing x; its section a
    superellipse of power."""
    unit = [mk.superellipse_point(2 * math.pi * j / segments, power) for j in range(segments)]
    rings = [[Vector((x, cd + r * u, ch + r * v)) for u, v in unit] for x, r in profile]
    return k.loft(name, rings, mat, start_point=(profile[0][0], cd, ch), end_point=(profile[-1][0], cd, ch))


def shaded(base, top=2, edge=4, bottom=-4, low=-2, back=-2):
    """A painter for blue parts (pick(centre, normal) -> material key): the base shade on the front, lighter on the
    top and the top's rounded edge (the sprites' lit top lines), darker underneath."""
    def pick(c, n):
        if n.z > 0.75:
            return blue(base + top)
        if n.z > 0.3 and n.y < -0.2:
            return blue(base + edge)
        if n.z < -0.55:
            return blue(base + bottom)
        if n.z < -0.2 and n.y < 0:
            return blue(base + low)
        if n.y > 0.5:
            return blue(base + back)
        return blue(base)
    return pick


def split_by(obj, fields):
    """Cuts an object's faces along the contours where each field (a function of a point) crosses its threshold, so
    that paint edges follow smooth lines (polish_ball_mast.py's)."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    for fn, threshold in fields:
        mk.split_along(bm, {v: fn(v.co) for v in bm.verts}, threshold)
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    return obj


def paint(obj, m, pick):
    """Every face its material by pick(centre, normal) -> a material key (None keeps the face's)."""
    def chosen(c, n):
        key = pick(c, n)
        return None if key is None else m[key]
    mk.paint(obj, chosen)
    return obj


def solid(name, outline, depth, m, pick, bevel=0.5, segments=2, d_mid=0.0, splits=(), cuts=()):
    """A part: a side profile extruded across, bevelled, its faces cut along the paint's edges (splits: [(field,
    threshold)]) and painted (pick), then the cutters (prisms whose faces carry their own material) cut out of it, its
    shading smoothed across its bevels."""
    obj = side_prism(name, outline, depth, m["seam"], d_mid)
    if bevel:
        mk.bevel(obj, bevel, segments, 30)
    if splits:
        split_by(obj, splits)
    paint(obj, m, pick)
    if cuts:
        mk.boolean(obj, list(cuts), "DIFFERENCE")
    mk.shade(obj, 35)
    return obj


def block(name, x0, x1, h0, h1, depth, m, pick, bevel=0.5, segments=2, d_mid=0.0, **kw):
    return solid(name, rect(x0, x1, h0, h1), depth, m, pick, bevel, segments, d_mid, **kw)


def cutter(name, outline, d0, d1, mat):
    """A cutting prism of a side outline from d0 to d1 (its faces' material goes to the cut's walls)."""
    return mk.prism(name, outline, d0, d1, mat, axis="y")


def rounded_outline(x0, x1, h0, h1, radii, steps=6):
    """A rectangle's outline with its corners rounded (radii: bottom left, bottom right, top right, top left)."""
    rbl, rbr, rtr, rtl = radii
    pts = []
    for (cx, cy, r, a0) in ((x0 + rbl, h0 + rbl, rbl, 180), (x1 - rbr, h0 + rbr, rbr, 270),
                            (x1 - rtr, h1 - rtr, rtr, 0), (x0 + rtl, h1 - rtl, rtl, 90)):
        for i in range(steps + 1):
            a = math.radians(a0 + 90 * i / steps)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    out = []
    for p in pts:
        if not out or (abs(p[0] - out[-1][0]) > 1e-4 or abs(p[1] - out[-1][1]) > 1e-4):
            out.append(p)
    return out


# --- The parts ----------------------------------------------------------------------------------------------------

def breech(m):
    """The silver breech: turned about x, a little square in section, its rear end rounded, two raised rings and two
    grooves near its front; lit along its top, darker under it."""
    ch, r, power, tip, front = BREECH
    prof = [(tip, 0.01), (tip + 0.05, 1.2), (tip + 0.25, 2.1), (tip + 0.7, 2.9), (tip + 1.35, 3.45), (tip + 2.2, 3.8),
            (tip + 3.0, r)]
    prof += BREECH_RINGS + [(front, r)]
    obj = lathe_x("breech", prof, ch, m["g9"], 36, power)
    k.smooth(obj, 40)

    def pick(c, n):
        x = c.x
        for x0, x1, raised in BREECH_BANDS:
            if x0 <= x <= x1:
                if not raised:
                    return "g5" if n.z < 0.3 else "g7"
                return "gd" if n.z > 0.35 else "gb" if n.z > -0.3 else "g7"
        if x < tip + 2.4:                           # the rounded rear end, turning away
            return "gb" if n.z > 0.2 else "g9" if n.z > -0.4 else "g7"
        if n.z > 0.3:
            return "gd"
        if n.z > -0.4:
            return "gb"
        if n.z > -0.8:
            return "g7"
        return "g5"
    return paint(obj, m, pick)


def handle(m):
    """The blue handle under the breech: a round bar from the block in front, back to a rounded knob, then up into the
    breech's rear end; lit on top, its knob's top brightest."""
    pts = [(x, 0.0, h, r) for x, h, r in HANDLE]
    bar = mk.smooth_tube("handle", pts, m["ba"], 18)
    k.smooth(bar, 55)
    return paint(bar, m, lambda c, n: "be" if (c.x < -36.0 and n.z > 0.25 and n.y < 0.2) else
                 "bc" if n.z > 0.45 else "b6" if n.z < -0.45 else "ba")


def fin_block(m):
    """The finned block under the handle: a prism of its side profile, bevelled, four slots cut into its front and foot
    (dark), its rounded left end lighter."""
    left = FIN_SLOTS[0][0] - FIN_SLOTS[0][1] / 2
    fins, end = shaded(8, top=2, edge=4, bottom=-4, low=-2), shaded(10, top=2, edge=4, bottom=-4, low=-2)
    cuts = [cutter(f"fin_slot{i}", rect(x - wdt / 2, x + wdt / 2, -7.0, -0.25), -FIN_D - 1.0, -FIN_D + 1.7, m["seam"])
            for i, (x, wdt) in enumerate(FIN_SLOTS)]
    return solid("fin_block", FIN_BLOCK, FIN_D, m, lambda c, n: end(c, n) if c.x < left else fins(c, n), 0.55,
                 splits=[(lambda co: co.x, left)], cuts=cuts)


def rear_block(m):
    """The tall block at the breech's front, its top's back corner bevelled off."""
    return solid("rear_block", REAR_BLOCK, REAR_D, m, shaded(10, top=2, edge=4, bottom=-4, low=-2), 0.7, 3)


def receiver(m):
    """The receiver: a dark core (seen in the slot under the sight), the lower box with its rail, the small box on it,
    the sight (its base band, a window in its face), the front hull round the barrel's root, the lower block and the
    ledge, the rod in the slot."""
    x0, x1, h0, h1, dd = CORE
    block("core", x0, x1, h0, h1, dd, m, lambda c, n: "b2", 0.3)
    solid("lower_box", LOWER_BOX, LOWER_D, m, shaded(8, top=2, edge=4, bottom=-4, low=-2), 0.5)
    rx0, rx1, rh0, rh1 = RAIL
    block("rail", rx0, rx1, rh0, rh1, 0.45, m, shaded(10, top=2, edge=2, bottom=-4, low=-2), 0.3, d_mid=-LOWER_D)
    sx0, sx1, sh0, sh1, sd = SMALL_BOX
    block("small_box", sx0, sx1, sh0, sh1, sd, m, shaded(10, top=2, edge=4, bottom=-4, low=-2), 0.55)
    tx0, tx1, th0, th1, td = SIGHT
    wx0, wx1, wh0, wh1, deep = WINDOW
    window = cutter("window", rect(wx0, wx1, wh0, wh1), -td - 1.0, -td + deep, m["b8"])
    sight = block("sight", tx0, tx1, th0, th1, td, m, shaded(10, top=2, edge=4, bottom=-4, low=-2), 0.75, 3,
                  cuts=[window])
    bx0, bx1, bh0, bh1, bd = SIGHT_BASE
    block("sight_base", bx0, bx1, bh0, bh1, bd, m, shaded(6, top=2, edge=2, bottom=-2, low=-2), 0.35)
    hx0, hx1, hh0, hh1, hd = HULL
    block("hull", hx0, hx1, hh0, hh1, hd, m, shaded(8, top=2, edge=4, bottom=-4, low=-2), 0.95, 3)
    lx0, lx1, lh0, lh1, ld = LOWER_BLOCK
    block("lower_block", lx0, lx1, lh0, lh1, ld, m, shaded(8, top=2, edge=2, bottom=-4, low=-2), 0.5)
    gx0, gx1, gh0, gh1, gd = LEDGE
    block("ledge", gx0, gx1, gh0, gh1, gd, m, shaded(6, top=6, edge=6, bottom=-2, low=-2), 0.45)
    ox0, ox1, oh, orad = SLOT_ROD
    rod = lathe_x("slot_rod", [(ox0, 0.01), (ox0 + 0.05, orad), (ox1 - 0.05, orad), (ox1, 0.01)], oh, m["b6"], 12,
                  cd=-CORE[4] - 0.25)
    k.smooth(rod, 50)
    paint(rod, m, lambda c, n: "b8" if n.z > 0.3 else "b4" if n.z < -0.4 else "b6")
    # A rivet on the hull's face.
    rivet = mk.ball("rivet", (5.5, -HULL[4] - 0.05, 10.2), (0.55, 0.3, 0.55), m["bc"], 12, 6)
    paint(rivet, m, lambda c, n: "be" if n.z > 0.2 else "ba")
    return sight


def trunnion(m):
    """The trunnion block under the receiver, standing on the platform: a prism, bevelled, a lit sloping face painted
    below the diagonal (the recessed panel's left edge), its recessed panel and the groove cut into its face; a base
    strip along its foot, its neck up into the receiver."""
    d_front = -TRUNNION_D
    (ax, ah), (bx, bh) = PANEL[0], PANEL[3]

    def diag(co):          # > 0 left of (below) the diagonal through the panel's left edge
        return (co.x - ax) * (bh - ah) - (co.z - ah) * (bx - ax)
    rest = shaded(6, top=2, edge=4, bottom=-4, low=-2)

    def pick(c, n):
        if n.y < -0.6 and c.y < d_front + 0.2:          # the face
            if c.z < BASE_STRIP[1]:
                return "b8"
            return "ba" if diag(c) > 0.0 else "b6"
        return rest(c, n)
    panel = cutter("panel", PANEL, d_front - 1.0, d_front + PANEL_DEEP, m["b4"])
    groove = cutter("groove", rect(GROOVE_X[0], GROOVE_X[1], -7.0, -0.9), d_front - 1.0, d_front + 1.3, m["seam"])
    obj = solid("trunnion", TRUNNION, TRUNNION_D, m, pick, 0.6,
                splits=[(diag, 0.0), (lambda co: co.z, BASE_STRIP[1])], cuts=[panel, groove])
    # The brace along the diagonal, standing out of the face over the recessed panel's left edge (its lower side's
    # shadow the sprites' dark diagonal line).
    (sx0, sh0), (sx1, sh1), half = STRUT
    length = math.hypot(sx1 - sx0, sh1 - sh0)
    ux, uh = (sx1 - sx0) / length, (sh1 - sh0) / length
    nx, nh = -uh * half, ux * half
    pts = [(sx0 - nx, sh0 - nh), (sx1 - nx, sh1 - nh), (sx1 + nx, sh1 + nh), (sx0 + nx, sh0 + nh)]
    solid("strut", pts, 0.85, m, shaded(10, top=2, edge=4, bottom=-4, low=-2), 0.25, d_mid=d_front + 0.35)
    # The base strip, standing out a little along the foot.
    h0, h1, out = BASE_STRIP
    block("base_strip", TRUNNION[0][0] + 0.2, TRUNNION[1][0] - 0.2, h0, h1, 0.5, m,
          shaded(8, top=2, edge=2, bottom=-4, low=-2), 0.25, d_mid=d_front - out + 0.5)
    # The neck between the trunnion's top and the receiver.
    block("neck", -8.3, -3.6, -0.3, 1.6, 3.0, m, lambda c, n: "b4", 0.25, 1)
    return obj


def barrel(m):
    """The barrel, its collars turned about x; the loop hanging under it and the block beside it."""
    ch, r, x0, x1 = BARREL
    bar = lathe_x("barrel", [(x0, 0.01), (x0 + 0.02, r), (x1 - 0.02, r), (x1, 0.01)], ch, m["b8"], 28)
    k.smooth(bar, 40)
    paint(bar, m, lambda c, n: "bc" if n.z > 0.8 else "ba" if n.z > 0.4 else "b4" if n.z < -0.55 else
          "b6" if n.z < -0.2 else "b8")
    for i, (a, b, rr) in enumerate(COLLARS):
        e = min(0.35, (b - a) / 4)
        prof = [(a, 0.01), (a + 0.02, rr - e), (a + e, rr), (b - e, rr), (b - 0.02, rr - e), (b, 0.01)]
        col = lathe_x(f"collar{i}", prof, ch + (0.25 if i == 1 else 0.0), m["ba"], 28)
        k.smooth(col, 50)
        paint(col, m, lambda c, n: "be" if n.z > 0.55 else "bc" if n.z > 0.2 else "b6" if n.z < -0.45 else "ba")
    x0, x1, h0, h1, rad, dd = LOOP
    hx0, hx1, hh0, hh1 = LOOP_HOLE
    hole = cutter("loop_hole", rounded_outline(hx0, hx1, hh0, hh1, (0.5, 0.5, 0.5, 0.5), 3), -dd - 1.0, dd + 1.0,
                  m["b4"])
    solid("loop", rounded_outline(x0, x1, h0, h1, (rad, rad, 0.2, 0.2), 4), dd, m,
          shaded(8, top=2, edge=4, bottom=-4, low=-2), 0.4, cuts=[hole])
    x0, x1, h0, h1, dd = SIDE_BLOCK
    block("side_block", x0, x1, h0, h1, dd, m, shaded(6, top=2, edge=4, bottom=-2, low=-2), 0.6)
    return bar


def housing(m):
    """The muzzle housing: a prism of its side profile (the cap's end rounded), bevelled, painted lit along its top,
    the upper jaw's lower part and the lower jaw darker; the port cut into its lower left, in it the glowing lens and
    the strip along its floor."""
    x0, x1, h0, h1 = HOUSING
    d_front = -HOUSING_D

    def pick(c, n):
        if n.z > 0.75:
            return "bc"
        if n.z > 0.3 and n.y < -0.2:
            return "be"
        if n.z < -0.55:
            return "b4"
        if c.x > 31.4 and c.z < 7.2:                   # the cap's bulge
            return "ba" if n.z > -0.2 else "b6"
        if c.z < 7.2:                                  # the lower jaw
            return "b6"
        if c.z < 9.3:                                  # the upper jaw's lower part
            return "b6" if n.z < 0.2 else "b8"
        return "ba"
    port = cutter("port", PORT, d_front - 1.0, d_front + PORT_DEEP, m["seam"])
    obj = solid("housing", rounded_outline(x0, x1, h0, h1, HOUSING_RADII), HOUSING_D, m, pick, 0.8, 3,
                splits=[(lambda co: co.z, 9.3), (lambda co: co.z, 7.2), (lambda co: co.x, 31.4)], cuts=[port])
    # The lens: a low dome facing the camera, set into the port's floor, hottest in its middle.
    lx, lh, lr = LENS
    floor = d_front + PORT_DEEP
    prof = [(lr, floor + 0.02), (lr * 0.92, floor - 0.25), (lr * 0.72, floor - 0.5), (lr * 0.42, floor - 0.66),
            (0.01, floor - 0.72)]
    lens = lathe_y("lens", prof, (lx, lh), m["glow_rim"], 24)
    k.smooth(lens, 70)
    paint(lens, m, lambda c, n: "glow_core" if math.hypot(c.x - lx, c.z - lh) < 0.5 * lr else
          "glow_mid" if math.hypot(c.x - lx, c.z - lh) < 0.82 * lr else "glow_rim")
    gx0, gx1, gh0, gh1 = GLOW_STRIP
    block("glow_strip", gx0, gx1, gh0, gh1, 0.25, m, lambda c, n: "glow_mid" if c.x < gx0 + 0.9 else
          "glow_rim" if c.x < gx0 + 2.6 else "glow_tail", 0.12, 1, d_mid=floor - 0.2,
          splits=[(lambda co: co.x, gx0 + 0.9), (lambda co: co.x, gx0 + 2.6)])
    return obj


def lathe_y(name, profile, centre, mat, segments=24):
    """A round part about an axis along d (towards the camera) at (x, h) = centre: profile [(radius, d)], its last
    point on the axis."""
    cx, ch = centre
    rings = [[Vector((cx + r * math.cos(2 * math.pi * j / segments), d, ch + r * math.sin(2 * math.pi * j / segments)))
              for j in range(segments)] for r, d in profile[:-1]]
    return k.loft(name, rings, mat, start_point=(cx, profile[0][1], ch), end_point=(cx, profile[-1][1], ch))


# --- The whole ----------------------------------------------------------------------------------------------------

def build_parts(m):
    """Every part, upright."""
    breech(m)
    handle(m)
    fin_block(m)
    rear_block(m)
    receiver(m)
    trunnion(m)
    barrel(m)
    housing(m)


def lean(objects):
    for obj in objects:
        obj.data.transform(LEAN)
        obj.data.update()


def floor_cut(objects, z=FLOOR_CUT):
    """Everything below z taken away (the platform hides it), the cut left open (under the platform)."""
    for obj in objects:
        if min(v.co.z for v in obj.data.vertices) >= z:
            continue
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-5, plane_co=(0, 0, z),
                               plane_no=(0, 0, -1), clear_outer=True)
        bm.to_mesh(obj.data)
        bm.free()
        obj.data.update()


def mirrored(objects):
    """The objects mirrored about x = 0, their corner normals mirrored with them (set again after the mirror: Blender's
    own handling of custom normals under a mirror differs with the faces round each corner, so that a damaged piece's
    shading would not meet an intact one's)."""
    flip = Matrix.Scale(-1, 4, (1, 0, 0))
    for obj in objects:
        mesh = obj.data
        saved = {}
        for poly in mesh.polygons:
            for li in poly.loop_indices:
                n = mesh.corner_normals[li].vector
                saved[(poly.index, mesh.loops[li].vertex_index)] = (-n.x, n.y, n.z)
        mesh.transform(flip)
        mesh.flip_normals()
        normals = [saved[(poly.index, mesh.loops[li].vertex_index)] for poly in mesh.polygons
                   for li in poly.loop_indices]
        mesh.normals_split_custom_set(normals)
        mesh.update()
    return objects


# Where the pieces meet across the gun (x, pointing right; the left cannon's are these mirrored).
CUTS = (-18.0, 6.0, 30.0)


def corner_normals_from(obj, source):
    """Sets every corner normal of obj to the source's (a NormalSource) at that corner's place."""
    mesh = obj.data
    normals = [tuple(n.vector) for n in mesh.corner_normals]
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            n = source.normal(mesh.vertices[mesh.loops[li].vertex_index].co, poly.center)
            if n is not None:
                normals[li] = tuple(n)
    mesh.normals_split_custom_set(normals)


def presplit(objects):
    """Every part's faces split along the cuts and into triangles, its shape and shading kept: the pieces' cuts then
    run along edges, so that faces cut finer or split for paint (polish_deli_cannon_dmg.py) leave the pieces' edges as
    they are."""
    for obj in objects:
        source = mk.NormalSource(obj)
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        for x in CUTS:
            bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-6, plane_co=(x, 0, 0),
                                   plane_no=(1, 0, 0))
        bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3], quad_method="BEAUTY",
                              ngon_method="BEAUTY")
        bm.to_mesh(obj.data)
        bm.free()
        obj.data.update()
        corner_normals_from(obj, source)


def upright_parts(m, parts=build_parts):
    """The parts, upright, their modifiers applied, split along the cuts."""
    parts(m)
    objects = mk.meshes()
    for obj in objects:
        mk.apply(obj)
    presplit(objects)
    return objects


def build_whole(m, mirror=False, parts=upright_parts):
    """The cannon's parts (parts(m) -> the upright meshes), leaned and cut at the platform (mirrored about x = 0:
    pointing left); returns the meshes."""
    parts(m)
    whole = mk.meshes()
    for obj in whole:
        mk.apply(obj)
    lean(whole)
    floor_cut(whole)
    if mirror:
        mirrored(whole)
    bpy.context.view_layer.update()
    return [o for o in whole if len(o.data.polygons) > 0]


# --- Checks ---------------------------------------------------------------------------------------------------------

def sprite_own(sheet, sprite, large):
    """A sprite's own pixels (rows of bools): not transparent and not the platform's purple (ramp 5)."""
    w, h = (24, 28) if large else (12, 14)
    mask = k.sprite_mask(sheet, sprite, large)
    raw = open(sheet[:-4] + ".idx", "rb").read()
    x0, y0 = (sprite - 1) % 19 * 12, (sprite - 1) // 19 * 14
    return [[bool(mask[r][c]) and raw[(y0 + r) * 228 + x0 + c] >> 4 != 5 for c in range(w)] for r in range(h)]


def whole_mask(sheet, layout):
    """The 84 x 28 picture's own pixels as the levels lay the sprites out (layout: [(sprite, 2x2, first column)])."""
    out = [[False] * 84 for _ in range(28)]
    for sprite, large, c0 in layout:
        own = sprite_own(sheet, sprite, large)
        for r, row in enumerate(own):
            for c, v in enumerate(row):
                if v:
                    out[r][c0 + c] = True
    return out


CAMERA = math.radians(20.0)       # the game's camera: this far from straight down, from the bottom of the screen


def camera_coverage(objects, w, h, supersample=4):
    """Which pixels of a w x h picture the objects cover as the game's camera sees them (orthographic, CAMERA from
    straight down), framed so that the picture's rows are the upright frame's heights (row r: h = 13.5 - r for 28
    rows): rows of bools."""
    import numpy as np
    scene = bpy.context.scene
    hidden = {}
    for obj in scene.objects:
        if obj.type == "MESH":
            hidden[obj.name] = obj.hide_render
            obj.hide_render = obj not in objects
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.film_transparent = True
    scene.render.resolution_x, scene.render.resolution_y = w * supersample, h * supersample
    scene.render.resolution_percentage = 100
    data = bpy.data.cameras.new("camera_check")
    data.type = "ORTHO"
    data.ortho_scale = max(w, h)
    data.clip_end = 1000
    cam = bpy.data.objects.new("camera_check", data)
    up = Vector((0.0, math.cos(CAMERA), math.sin(CAMERA)))
    view = Vector((0.0, math.sin(CAMERA), -math.cos(CAMERA)))
    # A point's height on the camera's picture is h + up . (0, PY, PZ) (the lean keeps h): centre the picture there.
    target = up * up.dot(Vector((0.0, PY, PZ)))
    cam.location = target - view * 300.0
    cam.rotation_euler = (CAMERA, 0.0, 0.0)
    scene.collection.objects.link(cam)
    scene.camera = cam
    path = os.path.join(bpy.app.tempdir or "/tmp", "camera_check.png")
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    image = bpy.data.images.load(path)
    rw, rh = image.size
    alpha = np.array(image.pixels[:]).reshape(rh, rw, 4)[::-1, :, 3]
    bpy.data.images.remove(image)
    bpy.data.objects.remove(cam)
    for obj in scene.objects:
        if obj.name in hidden:
            obj.hide_render = hidden[obj.name]
    return (alpha.reshape(h, supersample, w, supersample).mean(axis=(1, 3)) > 0.5).tolist()


def check(whole, sheet, layout, label):
    """The whole's silhouette against the sprites' own pixels, seen from straight above and as the game's camera sees
    it; returns the sprites' masks and, per sprite, the camera's coverage of its cell."""
    own = whole_mask(sheet, layout)
    mk.compare(label + ", top view", mk.coverage(whole, 84, 28), own)
    seen = camera_coverage(whole, 84, 28)
    mk.compare(label + ", game camera", seen, own)
    cells = {}
    for sprite, large, c0 in layout:
        w, h = (24, 28) if large else (12, 14)
        cells[sprite] = [row[c0:c0 + w] for row in seen[:h]]
    return {sprite: sprite_own(sheet, sprite, large) for sprite, large, _ in layout}, cells


def drop_unused(objects):
    """Takes the material slots no face uses off the objects (the faces' indices moved to match)."""
    for obj in objects:
        mesh = obj.data
        used = sorted({p.material_index for p in mesh.polygons})
        if len(used) == len(mesh.materials):
            continue
        keep = [mesh.materials[i] for i in used]
        remap = {old: new for new, old in enumerate(used)}
        indices = [remap[p.material_index] for p in mesh.polygons]
        mesh.materials.clear()
        for mat in keep:
            mesh.materials.append(mat)
        mesh.polygons.foreach_set("material_index", indices)
        mesh.update()


def pieces_of(whole, box, cap):
    pieces = [p for p in (cut(src, box, cap) for src in whole) if p is not None]
    drop_unused(pieces)
    mk.transform(pieces, Matrix.Translation((-(box[0] + box[1]) / 2, -(box[2] + box[3]) / 2, 0)))
    bpy.context.view_layer.update()
    return pieces


def export_pieces(whole, m, options, table, sprite_masks, cap_key="seam"):
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    for name, sprite, large, box in table:
        if only and name not in only:
            continue
        pieces = pieces_of(whole, box, m[cap_key])
        triangulate(pieces)
        for src in whole:
            src.hide_render = True
        size = (24, 28) if large else (12, 14)
        if sprite_masks:
            masks, cells = sprite_masks
            mk.compare("%s (C %d), top view" % (name, sprite), mk.coverage(pieces, *size), masks[sprite])
            mk.compare("%s (C %d), game camera (in the whole)" % (name, sprite), cells[sprite], masks[sprite])
        mk.report(name, pieces, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, pieces, size=size, scale=16 if large else 24)
        for obj in pieces:
            bpy.data.objects.remove(obj)
        for src in whole:
            src.hide_render = False


def run(options, label, tables, build, cap_key="seam", layout=LAYOUT):
    """Builds the whole both ways (build(mirror) -> meshes, materials), checks it against the sprites as layout lays
    them out, previews it and exports its pieces (tables: the pieces pointing right and pointing left)."""
    only = options["only"].split(",") if "only" in options else None
    for mirror, table in ((False, tables[0]), (True, tables[1])):
        if only and not any(name in only for name, _, _, _ in table):
            continue
        k.reset()
        whole, m = build(mirror)
        side = "pointing left" if mirror else "pointing right"
        print("whole %s %s: %d triangles, %d objects" % (label, side, mk.triangles(whole), len(whole)))
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        sprite_masks = None
        if "check" in options:
            sprite_masks = check(whole, os.path.join(options["check"], "enemy_C.png"), layout[mirror],
                                 "whole %s %s" % (label, side))
        tag = "_l" if mirror else ""
        if "preview" in options:
            mk.preview(options["preview"] + label + tag + "_whole", whole, size=(84, 28), scale=8, distance=1.5)
        if "whole" in options:
            mk.export(whole, options["whole"] + label + tag + ".glb")
        export_pieces(whole, m, options, table, sprite_masks, cap_key)


def build():
    options = k.args()

    def make(mirror):
        m = materials()
        return build_whole(m, mirror), m
    run(options, "cannon", (PIECES, PIECES_L), make)


if __name__ == "__main__":
    build()
