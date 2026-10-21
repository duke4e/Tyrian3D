"""FLEET's turret (sheet K sprite 281, 2x2: 24 x 28 pixels; enemy 708 of episodes 3 and 6, FLEET and THE CORE, sky
layer; one frame, not animated), polished (2026-10-21; it replaces wave3_o_machines.py's k_turret(), the pincer
machine's core_unit() upside down on pixel-art pillows). models.cfg: model k_turret enemies/k_turret.glb; sprite k
281 k_turret yaw=0 glow=12:0.2:121:-1.5:-2.6 (a faint orange light round the core's heart).

The sprite is two others' pixels put together: its rows 14-27 are the claw block's (K 283) rows 0-13 upside down,
index for index, and its rows 0-13 are the pincer machine's (K 153 above K 191) rows 14-27 upside down (all but a
few pixels): the machine's core unit standing on the claw block's block, upside down. So its lower half is
polish_k_clawblock.py's block, roof and flanges, built by that script's own functions and mirrored across y = 0
(the window's floor lighter at its top, the lit bevel along its lower edge and the hip roof with its two dark blue
lamps down the screen, as K 281 draws them); its upper half is the core unit (core_unit()), built here.

As the sprite and its 4x upscale draw the core unit (rows 0-13): a red core in the middle (columns 7-17 of rows
4-13), rounder than a ball, a rounded square seen from above, dark red but for a glowing heart low on its left
(column 10, row 11: white-hot, rings of orange and red round it) and a rim light at its upper right (columns 15-17
of rows 5-6); either side of it a grey sleeve across to the sprite's edge (rows 5-13: a lit collar where it meets
the core, a groove near its outer end), lit along its lower half; from the sleeves' inner ends two grey arms rise
round the core's upper half to the top edge (columns 4-9 and 15-20 of rows 0-5; the stray dark pixels outside them,
columns 4-5 and 19-20 of rows 0-4, are what the artist left of the outline when he erased the pincer machine's arms
flaring out to its crossbar: left out); between them the glowing red neck pointing up the screen like a barrel
(columns 11-13 of rows 0-3), dark at its root (row 3), hottest near its end (row 1).

Built as a CAD modeller would: the core a superellipsoid (square in plan, round in height) cut into bands of heat
(polish_orb_red.band_split) glowing in their own colours, well under 1, a dark hoop round its middle (the sprite's
outline round it); the sleeves turned along x (an end cap, an outer collar, a groove, the tube, the inner collar
against the core); the arms rounded bars rising out of the sleeves round the core to a dark crossbar under the
neck's end (a yoke holding the barrel); the neck turned along y in a dark steel collar at its root, glowing hotter
towards its muzzle and along its top (rings of heat round it read as stripes). The turret flies (sky layer); it is
10.3 pixels high, centred in height by the game.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; origin at the
sprite's centre (pixel 12, 14): column c's left edge is x = c - 12, row r's top edge y = 14 - r. Symmetric about the
middle of column 12 (x = 0.5) but for the sprite's edges (x -12 .. 12) and the core's heat.

Replaces wave3_o_machines.py's k_turret(): remove its section ("# --- K 281: the turret", the
@o.model("k_turret", [(281, True)]) registration and k_turret()) and k_turret's lines in the docstring.
core_unit(), slot_block() and wave3_o_art.py's K283 stay (the pincer's machine uses core_unit(); k_lampgun uses
slot_block() and K283); wave3_o_art.py's K281 is read by nothing (it can go).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouette against
enemy_K.png), --preview <prefix>.
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
import polish_k_clawblock as clawblock  # noqa: E402
from polish_k_pod import mirror_y, triangulate  # noqa: E402
from polish_orb_red import band_split  # noqa: E402

NAME = "k_turret"
MID = 0.5                       # the middle of column 12

# The core: its middle, its radii (across, up the screen, in height) and how square its plan is (superellipse
# power); its surface's heat seen from above: the heart (x, y, peak, radius of its core, of its glow, the glow's
# peak) and the rim light along its edge; the bands (lowest heat, palette index, glow).
CORE = (Vector((MID, 5.0, 5.4)), (5.55, 5.05, 4.9), 2.8)
HEART = (-1.5, 2.6, 1.0, 1.1, 3.6, 0.5)
RIM = (50.0, 0.45, 0.5)          # the rim light: its direction in plan (degrees from +x), spread (radians), peak
CORE_BANDS = [(-9.0, 0x71, 0.18), (0.16, 0x73, 0.26), (0.3, 0x75, 0.34), (0.45, 0x77, 0.42), (0.6, 0x79, 0.5),
              (0.75, 0x7b, 0.56), (0.9, 0x7d, 0.62)]
# The sleeves: their axis (y, z); the profile from the core outwards: (distance from the core's side, radius);
# where they meet the core (x of the left one's inner end, the right one's) and the sprite's edges.
SLEEVE_AXIS = (4.55, 5.2)
SLEEVE_INNER = (-4.85, 5.85)
EDGES = (-12.0, 12.0)
# From the inner end: (distance, radius) of the inner collar; then from the outer end: (distance, radius) of the
# groove, the outer collar and the end cap, listed outwards; the tube between them.
INNER_COLLAR = [(0.0, 3.7), (0.25, 4.5), (1.45, 4.5), (1.7, 4.2)]
OUTER_END = [(3.0, 4.2), (2.85, 3.85), (2.25, 3.85), (2.1, 4.45), (0.4, 4.45), (0.15, 4.15), (0.0, 3.6)]
# The arms: their path from inside the sleeve up round the core to the yoke's crossbar (the left one; x, y, z),
# half-width, half-height.
ARM = [(-6.9, 5.9, 7.7), (-6.5, 7.6, 8.5), (-5.15, 9.5, 8.5), (-3.9, 11.3, 7.7), (-3.0, 13.1, 6.2)]
ARM_HALF = (1.35, 0.85)
# The yoke's crossbar under the neck, joining the arms' tips: y, half-depth, its top under the neck's axis, height.
YOKE = (13.1, 0.75, 1.55, 1.5)
# The dark hoop round the core's middle (the sprite's outline round it): how far out of the core, its radius.
HOOP = (0.15, 0.5)
# The neck: its axis height; the steel collar round its root (y from, to, radius); the glowing tube from inside the
# collar to its muzzle: its profile along it (y, radius), its heat along it (from y, palette index).
NECK_Z = 6.4
COLLAR = (8.9, 10.85, 1.95)
NECK = [(9.5, 1.42), (13.35, 1.42), (13.5, 1.62), (13.9, 1.62), (14.0, 1.45), (14.0, 0.75)]
# The neck's heat: rising along it from its root to the sprite's row 1 and falling to the muzzle, hottest along its
# top (the sprite's middle column): (y, heat) along it, how much more along the top; the bands (lowest, index).
NECK_HEAT = [(9.5, 0.1), (11.0, 0.22), (12.2, 0.5), (12.9, 0.62), (13.9, 0.42)]
NECK_TOP = 0.42
NECK_BANDS = [(-9.0, 0x73), (0.3, 0x75), (0.45, 0x77), (0.6, 0x79), (0.75, 0x7b), (0.9, 0x7d)]


def materials():
    glow = k.level_palette()

    def mat(name, index, metallic=0.55, roughness=0.32):
        return k.material(name, palette=index, metallic=metallic, roughness=roughness)

    def lit(name, index, strength, roughness=0.18, emission_index=None):
        return k.material(name, palette=index, metallic=0.1, roughness=roughness,
                          emission=glow[index if emission_index is None else emission_index],
                          emission_strength=strength)
    m = {
        # polish_k_clawblock's (its block, roof and flanges use these keys)
        "grey": mat("kturret_grey", 0x09),
        "side": mat("kturret_side", 0x07, 0.55, 0.36),
        "light": mat("kturret_light", 0x0b, 0.55, 0.28),
        "bright": mat("kturret_bright", 0x0d, 0.55, 0.25),
        "groove": mat("kturret_groove", 0x05, 0.5, 0.4),
        "slot": mat("kturret_slot", 0x03, 0.45, 0.45),
        "slot_floor": mat("kturret_slot_floor", 0x06, 0.5, 0.4),
        "lamp": k.material("kturret_lamp", palette=0x31, metallic=0.2, roughness=0.15),
    }
    for _, index, strength in CORE_BANDS:
        m[("core", index)] = lit(f"kturret_core_{index:x}", index, strength,
                                 emission_index=0x72 if index == 0x71 else None)
    return m


# --- The block (polish_k_clawblock's, upside down) -----------------------------------------------------------------

def block(m):
    """polish_k_clawblock.py's block, roof and flanges, mirrored across y = 0."""
    before = set(mk.meshes())
    clawblock.block(m)
    clawblock.roof(m)
    clawblock.flanges(m)
    parts = [obj for obj in mk.meshes() if obj not in before]
    for obj in parts:
        obj.name = "base_" + obj.name
    return mirror_y(parts)


# --- The core unit -------------------------------------------------------------------------------------------------

def superellipsoid(name, centre, radii, power, subdivisions=4, below=-0.45):
    """An icosphere pushed out to the surface (|x/a|^p + |y/b|^p)^(2/p) + (z/c)^2 = 1 (a rounded square in plan,
    round in height), its faces facing further down than `below` (the camera never sees them) left out."""
    a, b, c = radii
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subdivisions, radius=1.0)
    for v in bm.verts:
        d = v.co.normalized()
        f = (abs(d.x / a) ** power + abs(d.y / b) ** power) ** (2 / power) + (d.z / c) ** 2
        v.co = centre + d / math.sqrt(f)
    hidden = [f for f in bm.faces if (f.calc_center_median() - centre).normalized().z < below]
    bmesh.ops.delete(bm, geom=hidden, context="FACES")
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    k.recalc_normals(obj)
    return obj


def core_heat(p):
    """The core's heat at its surface point p: the heart's glow low on its left (seen from above), the rim light
    along its upper right edge."""
    hx, hy, peak, r0, r1, glow = HEART
    d = math.hypot(p.x - hx, p.y - hy)
    heat = peak * math.exp(-(d / r0) ** 2) + glow * math.exp(-(d / r1) ** 2)
    centre, radii, _ = CORE
    n = Vector(((p.x - centre.x) / radii[0], (p.y - centre.y) / radii[1], (p.z - centre.z) / radii[2])).normalized()
    angle, spread, rim_peak = RIM
    off = math.atan2(n.y, n.x) - math.radians(angle)
    off = (off + math.pi) % (2 * math.pi) - math.pi
    edge = mk.smoothstep(0.75, 0.4, n.z) * mk.smoothstep(-0.15, 0.15, n.z)
    return max(heat, rim_peak * math.exp(-(off / spread) ** 2) * edge)


def core(m):
    """The core in its bands of heat, and the dark hoop round its middle."""
    centre, radii, power = CORE
    ball = superellipsoid("core", centre, radii, power)
    band_split(ball, [core_heat(v.co) for v in ball.data.vertices],
               [(lowest, m[("core", index)]) for lowest, index, _ in CORE_BANDS])
    k.smooth(ball, 80)
    out, r = HOOP
    ring = []
    for j in range(64):
        a = 2 * math.pi * j / 64
        ux, uy = mk.superellipse_point(a, power)
        ring.append((centre.x + (radii[0] + out) * ux, centre.y + (radii[1] + out) * uy, centre.z))
    hoop = mk.tube("hoop", ring + ring[:1], r, m["groove"], 12, cap=False)
    k.smooth(hoop, 60)
    return [ball, hoop]


def sleeve(m, side):
    """A sleeve from the core's side out to the sprite's edge (side -1: the left one), turned along x: the inner
    collar against the core, the tube, a groove, the outer collar and the end cap; painted (lit collars, a dark
    groove, the end cap's face)."""
    inner = SLEEVE_INNER[0] if side < 0 else SLEEVE_INNER[1]
    edge = EDGES[0] if side < 0 else EDGES[1]
    length = abs(edge - inner)
    y, z = SLEEVE_AXIS
    profile = list(INNER_COLLAR) + [(length - d, r) for d, r in OUTER_END]   # (distance from the inner end, radius)
    obj = mk.tube(f"sleeve{side}", [(inner + side * d, y, z) for d, _ in profile], 1.0, m["grey"], 32,
                  radii=[r for _, r in profile])
    k.smooth(obj, 40)

    def pick(c, n):
        d = abs(c.x - inner)
        if d < INNER_COLLAR[-1][0] - 0.1:
            return m["light"]                                      # the inner collar
        if length - OUTER_END[0][0] + 0.05 < d < length - OUTER_END[3][0] - 0.05:
            return m["groove"]                                     # the groove
        if d > length - OUTER_END[3][0] - 0.05:
            return m["side"] if d > length - 0.2 and abs(n.x) > 0.7 else m["light"]  # the outer collar, the cap
        return None
    mk.paint(obj, pick)
    return obj


def arms(m):
    """The arms from the sleeves' inner collars up round the core to the yoke's crossbar under the neck's end."""
    parts = []
    for side in (-1, 1):
        pts = [(x if side < 0 else 2 * MID - x, y, z) for x, y, z in ARM]
        dense = [Vector(p) for p in mk.chaikin(pts, 2, closed=False)]
        hw, hh = ARM_HALF
        arm = mk.bar(f"arm{side}", dense, [Vector((0, 0, 1))] * len(dense), hw, hh, hh, m["grey"], 16, 4.0)
        k.smooth(arm, 50)
        parts.append(arm)
    # The yoke's crossbar under the neck's end from one arm's tip to the other's, dark.
    yy, half, below, height = YOKE
    x0, x1 = ARM[-1][0] - 0.6, 2 * MID - ARM[-1][0] + 0.6
    top = NECK_Z - below + height
    bar = mk.box("yoke", x0, x1, yy - half, yy + half, top - height, top, m["slot"])
    mk.bevel(bar, 0.3, 2, 30)
    mk.shade(bar, 35)
    parts.append(bar)
    return parts


def neck(m):
    """The neck: the dark steel collar round its root where it leaves the core; the tube turned along y from inside
    the collar to its muzzle, glowing hotter towards its end (the sprite's row 1), the muzzle's lip; the dark bore."""
    y0, y1, r = COLLAR
    collar = mk.tube("neck_collar", [(MID, y, NECK_Z) for y in (y0, y0 + 0.2, y1 - 0.2, y1)], 1.0, m["groove"], 24,
                     radii=[r - 0.25, r, r, r - 0.3])
    k.smooth(collar, 50)
    obj = mk.tube("neck", [(MID, y, NECK_Z) for y, _ in NECK], 1.0, m[("core", 0x73)], 24, radii=[r for _, r in NECK])

    def heat(p):
        along = NECK_HEAT[0][1]
        for (ya, ha), (yb, hb) in zip(NECK_HEAT, NECK_HEAT[1:]):
            if ya <= p.y <= yb:
                along = ha + (hb - ha) * (p.y - ya) / (yb - ya)
        if p.y > NECK_HEAT[-1][0]:
            along = NECK_HEAT[-1][1]
        up = (p.z - NECK_Z) / max(1e-6, math.hypot(p.x - MID, p.z - NECK_Z))
        return along + NECK_TOP * mk.smoothstep(0.2, 0.95, up) * mk.smoothstep(10.0, 12.0, p.y)
    band_split(obj, [heat(v.co) for v in obj.data.vertices],
               [(lowest, m[("core", index)]) for lowest, index in NECK_BANDS])
    k.smooth(obj, 50)
    bore = mk.tube("bore", [(MID, 13.95, NECK_Z), (MID, 14.02, NECK_Z)], 0.78, m["slot"], 16)
    return [collar, obj, bore]


def core_unit(m):
    """The core, its sleeves, the arms with the yoke's crossbar and the neck (K 281's rows 0-13; the pincer's machine
    has them upside down)."""
    return core(m) + [sleeve(m, -1), sleeve(m, 1)] + arms(m) + neck(m)


def build():
    options = k.args()
    out = mk.outdir(options)
    k.reset()
    m = materials()
    parts = triangulate(block(m) + core_unit(m))
    bpy.context.view_layer.update()
    if "check" in options:
        sheet = os.path.join(options["check"], "enemy_K.png")
        mk.compare("k_turret (K 281)", mk.coverage(parts, 24, 28), k.sprite_mask(sheet, 281))
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    mk.report(NAME, parts, os.path.join(out, NAME + ".glb"))
    if "preview" in options:
        mk.preview(options["preview"] + NAME, parts, distance=0.6)


if __name__ == "__main__":
    build()
