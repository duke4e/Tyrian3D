"""The bronze pump of the asteroid levels on its block house, and its golden onion dome (sheet P sprites 229 and 231
above 267 and 269, the pump on the house, and 115, the dome, 2x2 each: one 48 x 84 picture, the dome's sprite above
the pump's top left one; ground layer; ASTEROID1, ASTEROID2, ASTEROID?, ASTCITY and AST. CITY, enemies 338 (the dome)
and 339-342 (the pump) of episodes 1-3; episode 6's enemies of those numbers are other things), polished (2026-10-21;
it replaces wave3_w_works.py's pump_whole(), a pump of slabs on wave3_w_kit.py's old house with the dome upright on a
short shaft, the dome's piece standing 30 pixels below its sprite, and wave3_ao_works.py's pump_wreck()). models.cfg:
model pump_dome / bronze_pump_tl / _tr / _bl / _br ... origin (unchanged) and the new model pump_dome_117,
pump_dome_119 ... origin; sprite p 115 pump_dome yaw=0 height=-4, sprite p 229 bronze_pump_tl yaw=0 height=-4 and the
same for 231, 267, 269; frame p 117 pump_dome_117, frame p 119 pump_dome_119; sprite p 121 pump_dome_wreck yaw=0
height=-4 (its model line, origin, unchanged).

Where the levels put them: event 12 ("4-part enemy") puts 339 (267) at (x, y), 340 (269) 24 pixels to its right,
341 (229) 28 pixels up the screen and 342 (231) both; event 6 at the same time puts the dome (338) at the same x with
d5 -56 against 339's 0 (ASTEROID1 t3968, 5256, 6488; ASTEROID2 t2484, 3128; ASTEROID? t580; ASTCITY t693 ... 5229;
AST. CITY t384 ... 6628; both with the same link number): the dome's sprite sits right above 229, as the sheet lays
them. The dome is an enemy of its own (armour 30, worth 100; the pump's pieces are worth nothing): shot, it leaves its
wreck (P 121, dgr with dlevel -1) in its place on the shaft; each pump piece can be shot away alone.

The pump's sprites draw it on the grey block house of these levels (P 153 155 above 191 193 in its first frame: the
same slabs; the pump's shadows on them are left out, the game casts its own), so the house is polish_block_house.py's,
built by its own functions (frame 1: the hatches closed; its vent and its conduit left off, under the pump's cabinet
and arm), and the pump stands on its roof. As the sprites and their 4x upscales draw the pump (columns and rows of the
48 x 84 picture): a bronze cross on the roof (ramp 10, tan-brown 0xa3-0xae): a long arm across it (columns 6-39 of
rows 45-57), its right end a taller block (columns 30-39 of rows 45-59) with a gold plate (columns 33-36 of rows
52-55), a lobe under its left part (columns 6-21 of rows 55-62); a tower on its right (columns 24-39 of rows 36-46:
its top lit, its front darker, a gold inset over both, columns 28-32) and a golden cabinet behind it (columns 24-34 of
rows 28-35); a leg down the house's front (columns 11-19): from the arm over the lobe (a gold inset on it, rows
57-67), bent over the roof's edge (rows 68-69, lit), down the ribbed front to the floor, a gold band round its foot
(rows 76-78); and from the arm a dark bronze shaft (columns 11-19 of rows 28-48, a dark slot down its front, a dark
window in it at rows 33-35, a lit lamp below that) up to the golden onion dome above the house (the dome's sprite:
three tiers and a knob, columns 5-23 of rows 4-27, its axis at column 14.5; its frames 115, 117 and 119 light the
bottom, the middle and the top tier in turn, 117 again, and so on: 115 115 115 117 117 117 119 119 119 117 117 117).
No other enemy (launched ones included) shows P 115, 117, 119, 229, 231, 267 or 269; none of them is another sprite's
pixels mirrored, turned or in other ramps.

The shaft and the dome, which the sprites draw standing up the screen over the house (20 rows of shaft, 24 of dome),
are built standing on the arm and leaned back up the screen LEAN (50) degrees, so that the game's camera (20 degrees
from straight down, from the bottom of the screen) sees the shaft's front and the dome's tiers nearly face on (70
degrees off their axis), the dome where its sprite is (above the house) and the shaft running up to it from the arm as
the sprites draw it: each piece is seen where the game hits it (stood upright, as wave3_w_works.py had it, the dome
showed over the pump's top left piece, seen from above as rings, its sprite's place empty). The shaft's foot and
length (22 pixels, its top 29 over the floor) and the dome's place follow from LEAN (at(): a point at height z shows
0.36 (z - 10) pixels further up the screen than its place on the roof, whose own height the house's layout already
holds); the dome is the sprite's profile along its axis (DOME_T: 23 pixels), its knob 45 over the floor, so it casts
its shadow (the game's sun is from the upper left) over the cabinet and the tower. The dome's piece holds the dome and
its collar (all above the collar's foot, along the lean), not what lies in its sprite's box: its parts lie 1 to 24
pixels below its origin and 24 to 45 pixels up; the pump's top left piece holds the shaft. The house and the cross
are cut along the sprites' edges (x = 0, y = 0; polish_savara_boss.cut: the pieces keep the whole's shading across the
cuts and each face its own winding), the cuts closed in each part's inside colour, each piece moved so that its
sprite's centre is its origin and its parts joined.

The cross is built as machined bronze (polish_machine_kit's CAD solids: rounded prisms, bevels): the arm, the end
block and the lobe slabs on the roof, the tower a block whose front falls back to the arm (so that the camera sees it
as the sprites draw it), the cabinet a gold block behind it, the leg a prism along x following the roof and the
house's battered front down to the floor; the gold plates laid on. Painted by how their faces meet the game's light
(from the upper left): bronze tops 0xa8, lit 0xab, shaded 0xa5, undersides 0xa3; gold 0x18, lit 0x1b, shaded 0x15
(a little metallic: in the game's dim sky fully metallic gold reads dark). The shaft a rounded column (0xa5, its lit
side 0xa8), the slot and the window cut into its front (dark: the house's 0x02), the lamp a small gold boss glowing a
little (0x1c, emission 0.3). The dome is turned about the lean's axis from the sprite's profile (three tiers parted by
dark waists 0x12, a knob), polished gold (0x18, lit 0x1b, shaded 0x15), painted along smooth contours of the light
(polish_orb_red.band_split); in each frame its lit tier has a broad sheen where it faces the camera and the light
(0x1c, emission 0.22 in 0x1d), as the sprites light it: pump_dome (115) the bottom tier, pump_dome_117 the middle,
pump_dome_119 the top (frame models: the same geometry and bounds). Its wreck (P 121: WRECK, its pixels) is the same
dome looked up where the camera sees each point on the wreck's sprite: burnt (0xa2, 0xa5, 0xa8 as its browns run),
pressed in 2 pixels and black (0x01) where it is black, pressed in a little along the red-hot gash down its right
(0x72 and 0x76, emission 0.3 and 0.45), its collar the same; cut the same way.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the floor (z = 0); the whole's
origin is the corner where the four pump sprites meet (pixel 24, 56 of the picture, the block house's own origin):
E(c, r) turns a pixel corner into (c - 24, 56 - r). The pieces' centres: 229 (-12, 14), 231 (12, 14), 267 (-12, -14),
269 (12, -14), the dome 115 (-12, 42). Drawn at their origins (origin) on the ground layer: height=-4 on every line
(as the block house's) sets the house on the terrain (its walls reach 4 pixels below it), the dome with it.

Replaces wave3_w_works.py's pump: its section "P 115 above 229 231 / 267 269: the bronze pump and its golden dome"
(PUMP, PUMP_ROOF, PUMP_AXIS, PUMP_DOME_Z, PUMP_DOME_SCALE, PUMP_LEAN, PUMP_DOME, PUMP_DRAWN, pump_dome_as_drawn(),
pump_whole() and its drawn_pieced("bronze_pump", ...) registration), the pump_dome / bronze_pump bullet of its
docstring and along() (only pump_dome_as_drawn() uses it); bronze_mats(), paint_lit(), Drawn and drawn_pieced() stay
(the rig uses them). And wave3_ao_works.py's pump wreck: its section "P 121: the bronze pump's dome, wrecked" (PUMP,
PUMP_DMG, pump_wreck() and its works.drawn_pieced("pump_dome_wreck", ...) registration) and the pump_dome_wreck
bullet of its docstring; wave3_ao_art.py's PUMP_DMG (only that section reads it) and wave3_w_art.py's PUMP (only the
two removed sections read it). wave3_ao_works.py goes on importing wave3_w_works.py (its cargo pod's and rig's wrecks:
crate_whole(), rig_whole(), drawn_pieced(), RIG_DRAWN stay).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the pump pieces' silhouettes
from above against the house's outline, the dome's, its frames' and its wreck's as the game's camera sees them
against P 115's, 117's, 119's and 121's pixels), --preview <prefix>, --only <name,...>, --whole <file.glb> (the uncut
pump and dome), --stats 1.
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
import polish_block_house as bh  # noqa: E402
from polish_orb_red import band_split, smoothstep  # noqa: E402
from polish_savara_boss import cut  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
import polish_deli_boss as db  # noqa: E402

PIECES = [("bronze_pump_tl", 229, (-24.0, 0.0, 0.0, 28.0)), ("bronze_pump_tr", 231, (0.0, 24.0, 0.0, 28.0)),
          ("bronze_pump_bl", 267, (-24.0, 0.0, -28.0, 0.0)), ("bronze_pump_br", 269, (0.0, 24.0, -28.0, 0.0))]
DOME_ORIGIN = Vector((-12.0, 42.0, 0.0))     # the dome sprite's centre (its piece's origin)
DOMES = [("pump_dome", 115, 0), ("pump_dome_117", 117, 1), ("pump_dome_119", 119, 2), ("pump_dome_wreck", 121, None)]

H = bh.H                                      # the house's roof
TILT = math.tan(math.radians(20.0))           # the camera shows a point this much further up the screen per pixel up
LIGHT = Vector((-0.55, 0.45, 0.7)).normalized()


def E(c, r):
    """A pixel corner (column c, row r) of the 48 x 84 picture in the whole's coordinates."""
    return (c - 24.0, 56.0 - r)


def at(c, r, z):
    """The point at height z that the camera shows where the sprites draw the pixel corner (c, r), relative to the
    roof (whose own height the house's layout holds)."""
    x, y = E(c, r)
    return Vector((x, y - (z - H) * TILT, z))


def rel_view(p):
    """Where the camera shows the point p, relative to the roof, in the picture's coordinates (x, y)."""
    return Vector((p.x, p.y + (p.z - H) * TILT))


# --- The lean: the shaft stands on the arm, leaned back up the screen; the dome on its top ---------------------------
LEAN = 50.0
AXIS_X = -9.0                                 # the shaft's and the dome's axis (the sprites' column 14.5)
ARM_TOP = H + 5.0                             # the arm's top, where the shaft stands
SHAFT_FOOT_ROW, COLLAR_ROW = 48.0, 26.0       # where the sprites draw the shaft's foot and the dome's collar
_a = math.radians(LEAN)
AXIS = Vector((0.0, math.sin(_a), math.cos(_a)))
FOOT = at(AXIS_X + 24.0, SHAFT_FOOT_ROW, ARM_TOP)
# The shaft's length: its top shows at the collar's row.
SHAFT_L = (E(0, COLLAR_ROW)[1] - E(0, SHAFT_FOOT_ROW)[1]) / (AXIS.y + AXIS.z * TILT)
LEANED = Matrix.Translation(FOOT) @ Matrix.Rotation(-_a, 4, "X")   # upright (x, front -y, up z) -> leaned
SHAFT = (8.0, 6.0)                            # the shaft's width (x) and depth
# The dome's profile (distance along its axis from the collar's foot, radius), as the sprite draws it (rows): the
# widest of each tier at rows 22, 14.5 and 8; DOME_T scales it along the axis.
DOME_PROFILE = [(0.0, 3.6), (1.2, 6.5), (2.8, 8.8), (5.1, 9.6), (7.4, 9.0), (9.2, 7.2), (10.1, 6.4), (11.2, 6.9),
                (13.5, 7.6), (15.3, 6.6), (16.8, 5.0), (18.2, 5.4), (20.8, 5.6), (22.6, 4.2), (23.6, 2.4), (24.2, 2.2),
                (25.2, 2.1), (26.0, 1.0), (26.3, 0.0)]
DOME_T = 0.88
WAISTS = [(9.5, 10.8), (16.2, 17.5), (23.0, 24.1)]   # the dark waists between the tiers (profile rows)
TIERS = [(0.0, 9.5), (10.8, 16.2), (17.5, 23.0)]     # the tiers each frame lights: bottom, middle, top
COLLAR = [(-1.8, 4.3), (-1.6, 5.3), (0.3, 5.3), (0.6, 4.2)]   # (along the axis, radius)


def materials():
    def mat(name, index, metallic=0.3, roughness=0.5, glow=0.0, glow_index=None):
        emission = k.level_palette()[glow_index if glow_index is not None else index] if glow > 0 else None
        return k.material(name, palette=index, metallic=metallic, roughness=roughness, emission=emission,
                          emission_strength=glow)
    m = bh.materials(0x0a)
    m["hatch"] = m["roof"]          # frame 1: the hatches as the slabs (one material less)
    m.update({
        "bz": mat("pump_bronze", 0xa8, 0.35, 0.4),
        "bz_lit": mat("pump_bronze_lit", 0xab, 0.35, 0.36),
        "bz_dark": mat("pump_bronze_dark", 0xa5, 0.3, 0.44),
        "bz_deep": mat("pump_bronze_deep", 0xa3, 0.3, 0.5),
        "gold": mat("pump_gold", 0x18, 0.45, 0.3),
        "gold_lit": mat("pump_gold_lit", 0x1b, 0.45, 0.28),
        "gold_dark": mat("pump_gold_dark", 0x15, 0.4, 0.34),
        "lamp": mat("pump_lamp", 0x1c, 0.2, 0.3, 0.3),
        "dome": mat("pump_dome", 0x18, 0.5, 0.24),
        "dome_lit": mat("pump_dome_lit", 0x1b, 0.5, 0.22),
        "dome_dark": mat("pump_dome_dark", 0x15, 0.45, 0.3),
        "waist": mat("pump_dome_waist", 0x12, 0.4, 0.36),
        "dome_glow": mat("pump_dome_glow", 0x1c, 0.5, 0.22, 0.22, 0x1d),
    })
    m["slot"] = m["well"]           # the shaft's slot and window: the house's dark
    return m


# --- Helpers ----------------------------------------------------------------------------------------------------

def rrect(x0, x1, y0, y1, radii, steps=5):
    return [(p.x, p.y) for p in bh.rrect(x0, x1, y0, y1, radii, 0.0, steps)]


def paint_block(obj, m, top="bz", lit="bz_lit", dark="bz_dark", deep="bz_deep"):
    """A machined block's faces by how they meet the light: its tops, lit slopes and walls, shaded ones, its
    underside."""
    def pick(c, n):
        if n.z < -0.5:
            return m[deep]
        if n.z > 0.92:
            return m[top]
        d = n.dot(LIGHT)
        if n.z > 0.3:
            return m[lit] if d > 0.62 else m[dark]
        return m[top] if d > 0.25 else m[dark]
    mk.paint(obj, pick)
    return obj


def block(name, outline, z0, z1, m, bevel=0.9, top="bz", lit="bz_lit", dark="bz_dark", deep="bz_deep", mat=None):
    obj = mk.prism(name, outline, z0, z1, m[mat or top])
    mk.bevel(obj, bevel, 3, 35)
    mk.shade(obj, 35)
    return paint_block(obj, m, top, lit, dark, deep)


# --- The house -----------------------------------------------------------------------------------------------------

def house(m):
    """polish_block_house's house in its first frame (the hatches flush), without the vent and the conduit."""
    bh.body(m)
    hatches = bh.slabs(m, 0.0)
    bh.wells(m, hatches)
    bh.ribs(m)
    return [o for o in mk.meshes()]


# --- The cross -----------------------------------------------------------------------------------------------------

def cross(m):
    parts = []
    # The arm across the roof (columns 6-39 of rows 45-57).
    (ax0, ay1), (ax1, ay0) = E(6, 45), E(40, 57.5)
    parts.append(block("arm", rrect(ax0, ax1, ay0, ay1, (2.0, 1.2, 1.2, 2.6)), H - 0.4, ARM_TOP, m, 1.0))
    # Its right end, a taller block (columns 30-39 of rows 45-59), and the gold plate on it (columns 33-36 of 52-55).
    (bx0, by1), (bx1, by0) = E(30, 45), E(40, 60)
    end_top = ARM_TOP + 0.7
    parts.append(block("arm_end", rrect(bx0, bx1, by0, by1, (1.4, 1.4, 1.4, 1.2)), H - 0.4, end_top, m, 0.9))
    (px0, py1), (px1, py0) = E(33, 52), E(37, 56)
    parts.append(block("arm_plate", rrect(px0, px1, py0, py1, (0.5,) * 4), end_top - 0.4, end_top + 0.55, m, 0.3,
                       "gold", "gold_lit", "gold_dark", "gold_dark"))
    # The lobe under its left part (columns 6-21 of rows 55-62).
    (lx0, ly1), (lx1, ly0) = E(6, 55), E(22, 63)
    parts.append(block("lobe", rrect(lx0, lx1, ly0, ly1, (3.0, 1.6, 0.6, 0.6)), H - 0.4, H + 4.2, m, 0.9))
    # The tower on the arm's right (columns 24-39 of rows 36-46): its top lit, its front falling back to the arm; the
    # gold inset over both (columns 28-32).
    t_top = H + 8.6
    back = at(0, 36.0, t_top).y
    edge = at(0, 39.6, t_top).y
    foot = at(0, 46.6, ARM_TOP).y
    x0, x1 = E(24, 0)[0], E(39.6, 0)[0]
    profile = [(foot, ARM_TOP - 1.0), (foot, ARM_TOP), (edge, t_top), (back, t_top), (back, H - 0.4),
               (foot + 0.5, H - 0.4)]
    tower = mk.prism("tower", profile, x0, x1, m["bz"], axis="x")
    mk.bevel(tower, 0.9, 3, 35)
    mk.shade(tower, 35)
    paint_block(tower, m)
    parts.append(tower)
    ix0, ix1 = E(28, 0)[0], E(33, 0)[0]
    grown = [(foot - 0.3, ARM_TOP + 0.4), (edge + 0.15, t_top + 0.45), (back - 0.6, t_top + 0.45),
             (back - 0.6, t_top - 1.0), (foot + 1.6, ARM_TOP - 0.4)]
    inset = mk.prism("tower_inset", grown, ix0, ix1, m["gold"], axis="x")
    mk.bevel(inset, 0.3, 2, 35)
    mk.shade(inset, 35)
    paint_block(inset, m, "gold", "gold_lit", "gold_dark", "gold_dark")
    parts.append(inset)
    # The golden cabinet behind it (columns 24-34 of rows 28-35).
    c_top = H + 10.2
    cy1 = at(0, 28.0, c_top).y
    cy0 = back - 0.4
    cx0, cx1 = E(24, 0)[0], E(34.4, 0)[0]
    parts.append(block("cabinet", rrect(cx0, cx1, cy0, cy1, (0.6, 0.6, 1.4, 1.4)), H - 0.4, c_top, m, 0.9,
                       "gold", "gold_lit", "gold_dark", "gold_dark"))
    # The leg down the front (columns 11-19): over the roof from the arm, bent over the roof's edge, down the house's
    # battered front to the floor; a gold inset on its top (rows 57-62), a gold band round its foot (rows 76-78).
    lx0, lx1 = E(11, 0)[0], E(20, 0)[0]
    y_edge, y_foot = bh.Y_FRONT, bh.Y_FOOT
    slope = (H - bh.EDGE) / (y_edge - y_foot)       # the glacis' rise per pixel up the screen
    top_z = H + 2.6
    over = H + 4.8                                   # over the lobe (rows 56-63)
    y_end = E(0, 81.6)[1]
    top_line = [(E(0, 56.5)[1], over), (E(0, 63.0)[1], over), (E(0, 65.6)[1], top_z + 0.4), (y_edge + 1.2, top_z),
                (y_edge - 0.6, top_z - 1.0), (y_foot + 3.2, 3.2 * slope + 2.4), (y_foot + 1.4, 2.6),
                (y_end + 0.6, 2.0), (y_end, 1.2)]
    leg_profile = top_line + [(y_end, -1.0), (y_foot - 0.5, -1.0), (y_edge - 0.8, H - 1.6), (y_edge + 0.8, H - 0.4),
                              (E(0, 56.5)[1], H - 0.4)]
    leg = mk.prism("leg", leg_profile, lx0, lx1, m["bz"], axis="x")
    mk.bevel(leg, 0.8, 3, 35)
    mk.shade(leg, 35)
    paint_block(leg, m)
    parts.append(leg)

    def leg_top(y):
        for (ya, za), (yb, zb) in zip(top_line, top_line[1:]):
            if yb <= y <= ya:
                return za + (zb - za) * (y - ya) / (yb - ya)
        return top_line[-1][1]

    def hugging(name, y0, y1, proud, x0, x1, mat_keys):
        """A plate laid over the leg's top from y0 down to y1 (y0 > y1), proud of it."""
        ys = [y0 + (y1 - y0) * i / 8 for i in range(9)]
        outline = [(y, leg_top(y) + proud) for y in ys] + [(y1, leg_top(y1) - 1.2), (y0, leg_top(y0) - 1.2)]
        obj = mk.prism(name, outline, x0, x1, m[mat_keys[0]], axis="x")
        mk.bevel(obj, 0.3, 2, 35)
        mk.shade(obj, 35)
        paint_block(obj, m, *mat_keys)
        return obj
    gold = ("gold", "gold_lit", "gold_dark", "gold_dark")
    # The gold inset on its top (columns 13-17 of rows 57-67), the band round its foot (rows 76-78).
    parts.append(hugging("leg_inset", E(0, 57.0)[1], E(0, 67.4)[1], 0.55, E(13, 0)[0], E(18, 0)[0], gold))
    band = hugging("leg_band", E(0, 76.0)[1], E(0, 79.2)[1], 0.6, lx0 - 0.45, lx1 + 0.45, gold)
    parts.append(band)
    return parts


# --- The shaft and the dome (built upright, then leaned) -------------------------------------------------------------

def leaned(objects):
    for obj in objects:
        obj.data.transform(LEANED)
        obj.data.update()
    return objects


def shaft(m):
    """The shaft, upright about its axis (front towards -y): a rounded column from below the arm's top to the
    collar, the slot and the window cut into its front, the lamp on it."""
    w, d = SHAFT
    x0 = 0.0                  # (the lean moves it onto AXIS_X)
    col = mk.box("shaft", x0 - w / 2, x0 + w / 2, -d / 2, d / 2, -3.0, SHAFT_L, m["bz_dark"])
    mk.bevel(col, 1.0, 3, 35)

    def t_of(row):            # how far up the shaft the camera shows it at the sprites' row
        return (E(0, row)[1] - E(0, SHAFT_FOOT_ROW)[1]) / (AXIS.y + AXIS.z * TILT)
    # The slot down its front (the sprites' column 16) and the window in it (columns 13-17, rows 33-35).
    slot = mk.box("shaft_slot", x0 + 0.2, x0 + 1.3, -d / 2 - 1.0, -d / 2 + 0.55, 1.2, SHAFT_L - 0.8, m["slot"])
    window = mk.box("shaft_window", x0 - 3.0, x0 + 1.4, -d / 2 - 1.0, -d / 2 + 0.9, t_of(35.6), t_of(32.8), m["slot"])
    mk.boolean(col, slot, "DIFFERENCE")
    mk.boolean(col, window, "DIFFERENCE")
    mk.cleanup(col)
    mk.shade(col, 35)
    lamp = mk.ball("shaft_lamp", (x0 - 1.6, -d / 2 - 0.05, t_of(40.0)), (0.95, 0.55, 0.95), m["lamp"], 12, 6)
    return [col, lamp]


def dome_parts(m):
    """The collar and the onion dome, upright on the shaft's top (z = SHAFT_L)."""
    prof = [(max(r, 1e-3), SHAFT_L + t * DOME_T) for t, r in k.profile(DOME_PROFILE, 0.55)]
    dome = mk.lathe("dome", prof, (0.0, 0.0), m["dome"], segments=36)
    k.smooth(dome, 60)
    collar = mk.lathe("dome_collar", [(r, SHAFT_L + t) for t, r in COLLAR], (0.0, 0.0), m["dome_dark"], segments=40)
    k.smooth(collar, 40)
    return [dome, collar]


def dome_t(p):
    """How far along the dome's profile (its rows, unscaled) a leaned point lies."""
    return (p - FOOT).dot(AXIS) / DOME_T - SHAFT_L / DOME_T


def paint_dome(dome, m, lit_tier):
    """The dome's gold by the light, the waists dark, the frame's lit tier glowing on the side the camera sees."""
    towards = Vector((0.0, -math.sin(math.radians(20)), math.cos(math.radians(20))))

    def extra(co):
        t = dome_t(co)
        value = 0.0
        for t0, t1 in WAISTS:
            value -= 3.0 * smoothstep(t0 - 0.35, t0 + 0.05, t) * (1.0 - smoothstep(t1 - 0.05, t1 + 0.35, t))
        return value
    dome.data.update()
    normals = [Vector() for _ in dome.data.vertices]
    for poly in dome.data.polygons:
        for vi in poly.vertices:
            normals[vi] += poly.normal * poly.area
    values = []
    for n, v in zip(normals, dome.data.vertices):
        n = n.normalized()
        val = n.dot(LIGHT) + extra(v.co)
        if lit_tier is not None:
            # The lit tier: a broad sheen where it faces the camera and the light (as the sprites light it).
            t0, t1 = TIERS[lit_tier]
            t = dome_t(v.co)
            inside = smoothstep(t0 - 0.2, t0 + 0.9, t) * (1.0 - smoothstep(t1 - 0.9, t1 + 0.2, t))
            sheen = inside * smoothstep(0.3, 0.6, n.dot(towards)) * smoothstep(-0.35, 0.1, n.dot(LIGHT))
            val += 6.0 * sheen
        values.append(val)
    band_split(dome, values, [(-9.0, m["waist"]), (-0.9, m["dome_dark"]), (-0.15, m["dome"]), (0.6, m["dome_lit"]),
                              (4.0, m["dome_glow"])])
    k.smooth(dome, 60)


def paint_shaft(parts, m):
    """The shaft's faces turned to the light (its left side) a shade lighter."""
    col = parts[0]
    for poly in col.data.polygons:
        n = poly.normal
        if col.data.materials[poly.material_index].name.startswith("house_well"):
            continue
        if n.dot(LIGHT) > 0.5:
            poly.material_index = mk.slot_of(col, m["bz"])


def build_whole(lit_tier=0):
    m = materials()
    parts = house(m)
    parts += cross(m)
    s = shaft(m)
    d = dome_parts(m)
    for obj in s + d:
        mk.apply(obj)
    leaned(s + d)
    paint_shaft(s, m)
    raw = copies(d)                 # the dome unpainted, for its other frames and its wreck
    for obj in raw:
        obj.hide_render = True
    paint_dome(d[0], m, lit_tier)
    parts += s
    for obj in parts + d:
        mk.apply(obj)
    bpy.context.view_layer.update()
    return parts, d, raw, m


# --- Checks ----------------------------------------------------------------------------------------------------------

def view_coverage(objects, c0, r0, w, h):
    """Which pixels of the picture (columns c0.., rows r0..) the camera sees the objects at, relative to the roof
    (rows of bools): a ray down the camera's line of sight through each pixel's middle."""
    depsgraph = bpy.context.evaluated_depsgraph_get()
    trees = [BVHTree.FromObject(o, depsgraph) for o in objects]
    d = Vector((0.0, TILT, -1.0)).normalized()
    out = []
    for r in range(r0, r0 + h):
        row = []
        for c in range(c0, c0 + w):
            x, yv = c + 0.5 - 24.0, 56.0 - (r + 0.5)
            z0 = 140.0
            origin = Vector((x, yv - (z0 - H) * TILT, z0))
            row.append(any(t.ray_cast(origin, d)[0] is not None for t in trees))
        out.append(row)
    return out


# --- Build -----------------------------------------------------------------------------------------------------------

CAPS = {"house": "seam", "slab": "seam", "hatch": "seam", "rib": "seam", "bolt": "seam", "hinge": "seam",
        "arm_plate": "gold_dark", "tower_inset": "gold_dark", "cabinet": "gold_dark", "leg_inset": "gold_dark",
        "leg_band": "gold_dark", "shaft": "bz_deep"}


def cap_of(obj, m):
    for prefix in sorted(CAPS, key=len, reverse=True):
        if obj.name.startswith(prefix):
            return m[CAPS[prefix]]
    return m["bz_deep"]


def export(parts, name, options, mask=None, label=""):
    out = mk.outdir(options)
    db.drop_unused(parts)
    triangulate(parts)
    if "stats" in options:
        for obj in sorted(parts, key=lambda o: -mk.triangles([o]))[:14]:
            print("    %-18s %6d" % (obj.name, mk.triangles([obj])))
    parts = [db.join(parts, name)]
    parts[0].data.name = name
    if mask is not None:
        mk.compare("%s (%s)" % (name, label), mk.coverage(parts, 24, 28), mask)
    bpy.context.scene.view_settings.view_transform = "Standard"
    mk.report(name, parts, os.path.join(out, name + ".glb"))
    if "preview" in options:
        mk.preview(options["preview"] + name, parts)
    for obj in parts:
        data = obj.data
        bpy.data.objects.remove(obj)
        if data.users == 0:
            bpy.data.meshes.remove(data)


def copies(objects):
    out = []
    for src in objects:
        obj = src.copy()
        obj.data = src.data.copy()
        bpy.context.scene.collection.objects.link(obj)
        out.append(obj)
    return out


def build():
    options = k.args()
    only = options["only"].split(",") if "only" in options else None
    sheet = os.path.join(options["check"], "enemy_P.png") if "check" in options else None
    want = lambda name: not only or name in only  # noqa: E731
    k.reset()
    whole, dome, raw, m = build_whole(0)
    triangulate(whole)  # (before any check renders: the cuts' shading then doesn't depend on them)
    if "stats" in options:
        for obj in sorted(whole + dome, key=lambda o: -mk.triangles([o]))[:20]:
            print("    %-18s %6d" % (obj.name, mk.triangles([obj])))
        print("whole: %d triangles" % mk.triangles(whole + dome))
    if sheet:
        house_mask = bh.house_mask()
        mk.compare("whole pump (P 229 231 above 267 269, the house's outline)", mk.coverage(whole, 48, 56), house_mask)
    if "preview" in options:
        mk.preview(options["preview"] + "bronze_pump_whole", whole + dome, size=(48, 84), scale=8, distance=2.4,
                   centre=(0.0, 14.0))
    if "whole" in options:
        triangulate(whole + dome)
        mk.export(whole + dome, options["whole"])
    for name, sprite, box in PIECES:
        if not want(name):
            continue
        parts = [p for p in (cut(src, box, cap_of(src, m)) for src in whole) if p is not None]
        mk.transform(parts, Matrix.Translation((-(box[0] + box[1]) / 2, -(box[2] + box[3]) / 2, 0)))
        bpy.context.view_layer.update()
        for src in whole + dome:
            src.hide_render = True
        mask = bh.piece_mask(name.rsplit("_", 1)[1]) if sheet else None
        export(parts, name, options, mask, "P %d, the house's outline" % sprite)
        for src in whole + dome:
            src.hide_render = False
    # The dome in its frames and its wreck: the same geometry, repainted (the wreck damaged).
    for name, sprite, tier in DOMES:
        if not want(name):
            continue
        parts = copies(raw)
        for obj in parts:
            obj.hide_render = False
        if tier is None:
            wreck(parts, m)
        else:
            paint_dome(parts[0], m, tier)
        bpy.context.view_layer.update()
        if sheet:
            mk.compare("%s as the camera sees it (P %d)" % (name, sprite), view_coverage(parts, 0, 0, 24, 28),
                       k.sprite_mask(sheet, sprite))
        mk.transform(parts, Matrix.Translation(-DOME_ORIGIN))
        bpy.context.view_layer.update()
        for src in whole + dome + raw:
            src.hide_render = True
        export(parts, name, options)
        for src in whole + dome:
            src.hide_render = False


# --- The wreck (P 121) -----------------------------------------------------------------------------------------------
# P 121's pixels: ' ' empty, '#' black (the holes), '0'-'c' the burnt dome's browns (ramp 10's shades), 'A'-'J' the
# red-hot gash (ramp 7's shades 0-9).
WRECK = [
    '                        ',
    '                        ',
    '                        ',
    '                        ',
    '           3333333      ',
    '          336655453     ',
    '         35895545443    ',
    '         47c96444454    ',
    '         35776212364    ',
    '         13560###5a3    ',
    '         1#10###0751    ',
    '         0######0231    ',
    '        #1871#2432453   ',
    '       104550##1225552  ',
    '       #4310##02444562  ',
    '       #01####38521892  ',
    '       #123458760#1862  ',
    '       253223433AA1000  ',
    '      2361234541BE##033 ',
    '     1456bcc9760CH##1543',
    '     1355ab9776#CJ##8553',
    '     #3545665763BH#84565',
    '     #3432235762#D#63686',
    '     #0220##031##B#45996',
    '     #100########A#37b75',
    '      22##########13984 ',
    '       11#########3684  ',
    '        21#####015654   ',
]
WRECK_BANDS = [(-99.0, 0x01, 0.0), (-4.0, 0xa2, 0.0), (4.0, 0xa5, 0.0), (7.0, 0xa8, 0.0), (19.5, 0x72, 0.3),
               (23.5, 0x76, 0.45)]
HOLE_DEPTH, GASH_DEPTH = 2.0, 0.7


def wreck_fields():
    """The wreck's map as fields over the dome sprite's pixels: hole (0-1), hot (0-1), heat (0-9) and shade (0-12),
    blurred a little (a 3 x 3 box) so that the dents and the paint follow smooth borders."""
    hole = [[0.0] * 26 for _ in range(30)]
    hot = [[0.0] * 26 for _ in range(30)]
    heat = [[0.0] * 26 for _ in range(30)]
    shade = [[4.0] * 26 for _ in range(30)]
    for r, line in enumerate(WRECK):
        for c, ch in enumerate(line):
            if ch == "#":
                hole[r + 1][c + 1] = 1.0
                shade[r + 1][c + 1] = 1.0
            elif ch in "0123456789abc":
                shade[r + 1][c + 1] = float(int(ch, 16))
            elif "A" <= ch <= "P":
                hot[r + 1][c + 1] = 1.0
                heat[r + 1][c + 1] = float(ord(ch) - ord("A"))
                shade[r + 1][c + 1] = 3.0

    def blur(f):
        out = [[0.0] * 26 for _ in range(30)]
        for r in range(30):
            for c in range(26):
                vals = [f[rr][cc] for rr in range(max(0, r - 1), min(30, r + 2))
                        for cc in range(max(0, c - 1), min(26, c + 2))]
                out[r][c] = 0.5 * f[r][c] + 0.5 * sum(vals) / len(vals)
        return out
    return blur(hole), blur(hot), heat, shade


def sample(field, fc, fr):
    """A field (padded by one pixel) bilinearly at the sprite's continuous pixel position (fc, fr)."""
    x, y = fc - 0.5 + 1.0, fr - 0.5 + 1.0
    c0, r0 = int(math.floor(x)), int(math.floor(y))
    tx, ty = x - c0, y - r0

    def at_(r, c):
        r = min(max(r, 0), len(field) - 1)
        c = min(max(c, 0), len(field[0]) - 1)
        return field[r][c]
    return ((1 - tx) * (1 - ty) * at_(r0, c0) + tx * (1 - ty) * at_(r0, c0 + 1) + (1 - tx) * ty * at_(r0 + 1, c0) +
            tx * ty * at_(r0 + 1, c0 + 1))


def wreck(parts, m):
    """The dome and its collar wrecked as P 121 draws them: each surface point looked up where the camera sees it
    on the dome's sprite (relative to the roof); pressed in where the wreck is black and along the gash, painted in
    its browns, black and hot reds."""
    hole, hot, heat, shade = wreck_fields()
    mats = {index: k.material("pump_wreck_%02x" % index, palette=index, metallic=0.25 if index >> 4 == 10 else 0.1,
                              roughness=0.6 if index >> 4 == 10 else 0.4,
                              emission=k.level_palette()[index] if glow > 0 else None, emission_strength=glow)
            for _, index, glow in WRECK_BANDS}
    towards = Vector((0.0, -math.sin(math.radians(20)), math.cos(math.radians(20))))
    origin = Vector((DOME_ORIGIN.x - 12.0, DOME_ORIGIN.y + 14.0))   # the dome sprite's top left corner
    for obj in parts:
        mesh = obj.data
        mesh.update()
        normals = [Vector() for _ in mesh.vertices]
        for poly in mesh.polygons:
            for vi in poly.vertices:
                normals[vi] += poly.normal * poly.area
        values = []
        for v, n in zip(mesh.vertices, normals):
            n = n.normalized()
            rv = rel_view(v.co)
            fc, fr = rv.x - origin.x, origin.y - rv.y
            h, g = sample(hole, fc, fr), sample(hot, fc, fr)
            if n.dot(towards) > -0.2:
                v.co -= n * (HOLE_DEPTH * smoothstep(0.35, 0.8, h) + GASH_DEPTH * smoothstep(0.3, 0.7, g))
            if g > 0.45:
                values.append(20.0 + sample(heat, fc, fr))
            elif h > 0.5:
                values.append(-10.0)
            else:
                values.append(sample(shade, fc, fr))
        mesh.update()
        band_split(obj, values, [(low, mats[index]) for low, index, _ in WRECK_BANDS])
        k.smooth(obj, 50)
    return parts


if __name__ == "__main__":
    build()
