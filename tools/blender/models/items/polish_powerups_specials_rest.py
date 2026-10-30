"""The power-ups sheet's other special weapon icons ("twoplayer" in the catalogue, powerups in models.cfg), the ones
polish_powerups_specials.py left (2026-10-30): sprites 55, 91, 93, 125, 127, 129, 131, 279 and 283, and 53, which no
special uses. All 2x2 (24 x 28 pixels), one frame each. The same small fighter as the six specials modelled there,
pixel for pixel (its outline 0xf0), with its special's effect round it:

  sprite  model                   the effect, as the sprite draws it                     the specials (item data)
  55      pu_pulse_blast          two fireballs over the nose (ramp 7)                   17 Pulse Blast
  91      pu_megalaser            a blue laser beam up from the nose (ramp 9)            18 MegaLaser
  279     pu_megalaser_dual_red   two red laser beams up from the blade tips (ramp 7)    15 MegaLaser Dual
  53      pu_megalaser_twin_blue  two blue laser beams over the nose (ramp 9)            none
  93      pu_lightning_zone       a blue zigzag of lightning up from the nose (ramp 9)   40 Lightning Zone, 48 Dragon
                                                                                         Lightning
  125     pu_question_mark        a green question mark over the nose (ramp 2)           7 Blade Field, 8 SandStorm,
                                                                                         11 Banana Bomb, 12 Protron
                                                                                         Dispersal, 13 Astral Zone,
                                                                                         16 Orange Shield, 19 Missile
                                                                                         Pod, 41 SDF Main Gun
  127     pu_xega_ball            a red ball over the nose, cross-hatched (ramp 4)       14 Xega Ball
  129     pu_pearl_ring           eight pale blue pearls round the fighter (ramp 8)      37 Invulnerability, 45 8-Way
                                                                                         Microbomb, 47 Super Pretzel
  131     pu_dual_vulcan          four orange sparks in two columns (ramp 7)             10 Dual Vulcan
  283     pu_minefield            Soul of Zinglon's capsule round the fighter, six       9 MineField
                                  small blue mines round it (ramp 3)

(Specials 1-48's item graphics, tyrian.hdt as tools/content/tyrdata.py reads it, the same in episodes 1-5; the
specials without a graphic (Minefield 20, Post-It Blast, Drone, the Lightning directions, the MicroSol Options, Atom
Bomb, ...) have no icon. Sprite 53, two blue beams beside the nose, is the item graphic of no special: its model only
completes the sheet.) No enemy draws any of these sprites (catalog.json), so no level shows these models: they are
seen as icons, the modern HUD's special weapon (bottom left, beside its name, about 40 pixels at 1600 x 900) and the
rogue run's cards, both drawing the model's render (assets/models/icons/<model>.png, render_gpu.c rgpu_ui_model_icon,
made by TYR3D_RENDER_ICONS); game_menu.c special_item_model finds the model by its "sprite powerups <n> <model>" line.
So every effect is built to read at that size first: bold, lit in its own colours, a little larger than the sprite's
pixels where it is thin.

The fighter is polish_powerups_specials.fighter() (imported, not changed), moved where each sprite draws it: rows 6-19
as in the six (55, 127, 129, 131, 279, 283), 7 rows lower in 53, 91 and 93 (rows 13-26), 8 lower in 125 (rows 14-27),
under the effect over its nose.

The effects (each glowing in its own palette colours, 0.3-0.62, as the six do):
- 55 Pulse Blast: two fireballs (columns 7-11 and 13-17 of rows 2-8: a round head, a red rim round orange round
  yellow, 0x7c at its top, a tail of dark red falling 3 rows under it), side by side over the nose. A ball for each head
  in bands by its slope (red rim, orange, yellow top), a pale yellow core standing out of its top, and a flame trailing
  from under it (a tube tapering to a point, its tip swinging a little outwards) from orange to red to a dark red tip,
  the borders waving round it (flame tongues). (Teardrops, band() from a pointed tail to a round head, looked like
  sweets; three separate tongues under each head like claws.)
- 91 MegaLaser, 53, 279 MegaLaser Dual: laser beams 3 pixels wide (an edge of 0x9a round a core of 0x9f and 0x8f, the
  blue ones; 0x75 round 0x7d and 0x7e, the red ones). Rods with round ends: a sheath, lighter on top than at its sides,
  a pale core standing out of its top, a flare where each beam leaves the fighter (91: the nose; 279: the blade tips,
  columns 7 and 17); 53's two beams float beside the nose (columns 9 and 15 of rows 2-14). The red beams' sheath is a
  shade or two darker than the sprite's and their yellow core thinner: with the icon's light and bloom they read
  orange-yellow otherwise.
- 93 Lightning Zone: a jagged bolt from the nose up (columns 9-14 of rows 1-12: five kinks, 0x93 at its edges, 0x8f and
  0x9e in its middle). A tube along the zigzag, sharp at its kinks, blue (0x9b), a white-blue core along its top; a
  flare at the nose.
- 125 the question mark (columns 8-15 of rows 2-12, ramp 2: 0x29 and 0x2b on a dark 0x25 outline): a tube along its
  hook and stem, rounded at its ends, its top lighter than its sides, and a ball for its dot.
- 127 Xega Ball (columns 9-15 of rows 1-6, ramp 4, its pixels a diagonal check of 0x45 and 0x48-0x4b): a ball in bands
  by its slope (lightest on top), caged in dark ribs crossing diagonally (arcs of the ball's circles in two sets of
  three upright planes at 45 degrees to the screen), standing over the nose.
- 129 the pearls (4 x 4 pixels each: 0x82 round 0x89, 0x8e at the upper left): eight glossy pearls where the sprite
  draws them, in bands by their slope.
- 131 Dual Vulcan: four sparks (3 x 4 pixels: 0x7b over 0x79 in a rim of 0x71) over the blade tips in two columns:
  hot drops flying up the screen, a yellow head over an orange body, a red tail, a pale core in the head.
- 283 MineField: polish_powerups_specials.soul_of_zinglon() (its capsule is the Zinglon's pixel for pixel) and six small
  mines round it (3 x 4-pixel crosses of 0x37 and 0x3a, 0x35 under them): blue balls with four spikes across and one up,
  in the cradle's own materials (lighter than the sprite's, to show at the icon's size): the game keeps a model's
  first 16 materials only (render_gpu.c LoadedModel.materials, silently), and the capsule and the fighter have 15, so
  mines with materials of their own were dropped (build() asserts every model has at most 16).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; the origin is the
sprite's centre (pixel 12, 14): column c is x = c + 0.5 - 12, row r is y = 13.5 - r. Every model stands on z = 0. Every
mesh is triangulated before export (polish_powerups_specials.triangulate).

models.cfg: the model lines (model pu_pulse_blast items/pu_pulse_blast.glb, ...) and the sprite lines (sprite powerups
55 pu_pulse_blast yaw=0, ...: they keep still as the other power-ups) after the six specials' block.

Run: Blender -b --factory-startup -P tools/blender/models/items/polish_powerups_specials_rest.py -- [--outdir <dir>]
     (default assets/models/items) [--check <sheets dir or powerups.png>] (each model's silhouette against its sprite)
     [--preview <prefix>] [--only <name,...>]
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_item_kit as kit  # noqa: E402
from polish_item_kit import k  # noqa: E402
import polish_powerups_specials as ps  # noqa: E402
from polish_powerups_specials import AXIS, band, banded_by_normal, catmull, glow_mat, lozenge  # noqa: E402


# --- Shared pieces -------------------------------------------------------------------------------------------------

def fighter_at(dy, z=0.0):
    """polish_powerups_specials' fighter, moved dy along the screen's y (the sprites draw it lower under a tall
    effect)."""
    parts = ps.fighter(z)
    if dy:
        for obj in parts:
            obj.data.transform(Matrix.Translation((0.0, dy, 0.0)))
    return parts


def rod(start, end, radius, caps=(True, True), steps=12, cap_steps=5):
    """A straight path from start to end (x, y, z) and its widths: radius along it, falling to 0 in a quarter circle
    over the last radius at a capped end (a round end)."""
    a, b = Vector(start), Vector(end)
    length = (b - a).length
    distances = set()
    for i in range(cap_steps + 1):
        d = radius * (1.0 - math.cos(math.radians(90.0 * i / cap_steps)))
        if caps[0]:
            distances.add(round(d, 6))
        if caps[1]:
            distances.add(round(length - d, 6))
    lo = radius if caps[0] else 0.0
    hi = length - radius if caps[1] else length
    for i in range(steps + 1):
        distances.add(round(lo + (hi - lo) * i / steps, 6))
    path, widths = [], []
    for d in sorted(distances):
        path.append(a + (b - a) * (d / length))
        w = radius
        if caps[0] and d < radius:
            w = radius * math.sqrt(max(0.0, 1.0 - (1.0 - d / radius) ** 2))
        if caps[1] and length - d < radius:
            w = radius * math.sqrt(max(0.0, 1.0 - (1.0 - (length - d) / radius) ** 2))
        widths.append(w)
    return path, widths


def ball(name, centre, radii, mats, borders, segments=32, rings=16, floor=None):
    """An ellipsoid (a UV sphere scaled to radii round centre), its underside cut flat at z = floor, painted in bands
    by its normal's z (borders: the bands' lower borders but the first's; mats: one per band)."""
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=segments, v_segments=rings, radius=1.0)
    cx, cy, cz = centre
    rx, ry, rz = radii
    for v in bm.verts:
        z = cz + v.co.z * rz
        v.co = Vector((cx + v.co.x * rx, cy + v.co.y * ry, z if floor is None else max(z, floor)))
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-4)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    keys = banded_by_normal(bm, borders)
    obj = kit.from_bmesh(name, bm)
    for mat in mats:
        obj.data.materials.append(mat)
    for poly, key in zip(obj.data.polygons, keys):
        poly.material_index = key
    # (The faces come out of the cuts in an order that changes from run to run: rebuilt in a fixed order, so that the
    # GLBs are the same every build.)
    return k.smooth(ps.canonical(obj), 80)


def flare(name, centre, size, mat, lean=0.0):
    """A four-pointed star of light (two crossed lozenges, as Ice Beam's sparkles) lying at centre."""
    parts = []
    for j, (length, width) in enumerate(((size, size * 0.3), (size * 0.3, size))):
        star = lozenge(f"{name}_{j}", length, width, size * 0.35, mat)
        star.data.transform(Matrix.Translation(centre) @ Matrix.Rotation(math.radians(lean), 4, "Z"))
        parts.append(star)
    return parts


# --- Laser beams (91, 53, 279) -------------------------------------------------------------------------------------

# The blue beams (ramp 9) and the red ones (ramp 7): the sheath's sides and top (palette index, glowing in, glow), the
# core along its top, the flare where a beam leaves the fighter.
BLUE = {"side": (0x99, 0x9a, 0.42), "top": (0x9b, 0x9c, 0.5), "core": (0x8f, 0x8f, 0.6), "flare": (0x8e, 0x8f, 0.6)}
RED = {"side": (0x72, 0x73, 0.34), "top": (0x74, 0x75, 0.4), "core": (0x7b, 0x7c, 0.52), "flare": (0x7c, 0x7d, 0.56)}
# The beam's half-width, the sheath's height over it, the core's half-width and how far it stands out of the sheath.
BEAM_R, BEAM_SQUASH, CORE_R, CORE_OUT = 1.45, 0.8, 0.55, 0.3
RED_CORE_R = 0.4  # (the red beams' yellow core thinner: their red reads at the icon's size)


def beam_mats(prefix, colours):
    return {key: glow_mat(f"{prefix}_{key}", index, emit, strength, 0.0, 0.3)
            for key, (index, emit, strength) in colours.items()}


def beam(name, x, y0, y1, z, mats, radius=BEAM_R, core=CORE_R):
    """A laser beam up the screen from y0 to y1 at x, its middle at height z: a sheath with round ends, lighter on top,
    and a pale core standing out of its top."""
    path, widths = rod((x, y0, z), (x, y1, z), radius)
    heights = [w * BEAM_SQUASH for w in widths]
    parts = [band(name, path, widths, heights, {"*": mats["side"], "top": mats["top"]},
                  lambda t, a: "top" if 48.0 < a < 132.0 else "*", segments=16)]
    core_r = core * radius / BEAM_R
    zc = z + radius * BEAM_SQUASH + CORE_OUT - core_r * 0.7
    path, widths = rod((x, y0 + radius * 0.5, zc), (x, y1 - radius * 0.5, zc), core_r)
    parts.append(band(name + "_core", path, widths, [w * 0.7 for w in widths], {"*": mats["core"]}, segments=10))
    return parts


def megalaser():
    """91: one blue beam up from the nose (columns 11-13 of rows 2-14), the fighter 7 rows lower."""
    parts = fighter_at(-7.0)
    mats = beam_mats("megalaser", BLUE)
    parts += beam("beam", AXIS, 0.4, 12.0, 1.75, mats)
    parts += flare("muzzle", (AXIS, 1.0, 2.2), 2.1, mats["flare"])
    return parts


def megalaser_twin_blue():
    """53: two blue beams beside the nose (columns 8-10 and 14-16 of rows 2-14), the fighter 7 rows lower."""
    parts = fighter_at(-7.0)
    mats = beam_mats("twin", BLUE)
    for side, dx in (("l", -3.0), ("r", 3.0)):
        parts += beam("beam_" + side, AXIS + dx, -0.6, 12.0, 1.75, mats)
    return parts


def megalaser_dual_red():
    """279: two red beams up from the blade tips (columns 6-8 and 16-18 of rows 1-12)."""
    parts = fighter_at(0.0)
    mats = beam_mats("dual", RED)
    tip_x, tip_y, tip_z = ps.BLADE_TIP
    for side, x in (("l", tip_x + 0.05), ("r", 2 * AXIS - tip_x - 0.05)):
        parts += beam("beam_" + side, x, tip_y - 0.6, 13.0, tip_z + 0.75, mats, core=RED_CORE_R)
        parts += flare("muzzle_" + side, (x, tip_y + 0.2, tip_z + 1.35), 1.8, mats["flare"])
    return parts


# --- 55: Pulse Blast -----------------------------------------------------------------------------------------------

# The fireballs: their x, the middle of their heads (y), the heads' radius and height, how high their middles float;
# the heads' bands by their slope (lower border, palette index, glowing in, glow) and the core on top (offset up the
# screen from the head's middle, radii, palette index, glowing in, glow); the flame trailing from under each head
# (where its tip ends, its half-width at the root, how far its tip swings aside) and its colours along it (from where,
# palette index, glowing in, glow: the first two the head's middle and rim), their borders waving round it (flame
# tongues: how many round, how far along).
FIREBALLS = (AXIS - 3.0, AXIS + 3.0)
FIRE_HEAD_Y, FIRE_R, FIRE_H, FIRE_Z = 9.6, 2.45, 2.0, 2.35
FIRE_BANDS = [(-1.0, 0x76, 0x77, 0.42), (0.4, 0x79, 0x7a, 0.48), (0.78, 0x7b, 0x7c, 0.54)]
FIRE_CORE = ((-0.05, 0.4), (1.15, 1.3, 0.62), (0x7e, 0x7e, 0.62))
FIRE_TAIL_Y, FIRE_TAIL_W, FIRE_SWING = 4.8, 2.3, 0.35
TAIL_SHADES = [(0.0, 0x79, 0x7a, 0.48), (0.4, 0x76, 0x77, 0.42), (0.75, 0x73, 0x74, 0.32)]
FLAME_TONGUES, FLAME_REACH = 3, 0.13


def pulse_blast():
    parts = fighter_at(0.0)
    head = [glow_mat(f"fire{i}", index, emit, strength, 0.0, 0.5)
            for i, (_, index, emit, strength) in enumerate(FIRE_BANDS)]
    shades = {"1": head[1], "0": head[0]}
    shades["2"] = glow_mat("fire_tip", *TAIL_SHADES[2][1:3], TAIL_SHADES[2][3], 0.0, 0.5)
    (dx, dy), radii, (index, emit, strength) = FIRE_CORE
    core = glow_mat("fire_core", index, emit, strength, 0.0, 0.4)

    def shade(t, a):
        # Orange at the root (the head's middle), red (its rim), the dark red tip; the borders waving round the flame.
        u = t + FLAME_REACH * math.sin(math.radians(a) * FLAME_TONGUES)
        return ("1", "0", "2")[sum(u >= start for start, _, _, _ in TAIL_SHADES[1:])]
    for i, x in enumerate(FIREBALLS):
        parts.append(ball(f"fireball{i}", (x, FIRE_HEAD_Y, FIRE_Z), (FIRE_R, FIRE_R, FIRE_H), head,
                          [b[0] for b in FIRE_BANDS[1:]], 28, 14))
        centre = (x + dx, FIRE_HEAD_Y + dy, FIRE_Z + FIRE_H - radii[2] * 0.55)
        parts.append(k.smooth(k.ellipsoid(f"fire_core{i}", centre, radii, core, 14, 8), 80))
        # The flame trailing from under the head, its tip swinging a little outwards.
        swing = FIRE_SWING if x > AXIS else -FIRE_SWING
        y0 = FIRE_HEAD_Y + 0.2
        path = catmull([(x, y0, FIRE_Z - 0.15), (x - 0.3 * swing, y0 + (FIRE_TAIL_Y - y0) * 0.4, FIRE_Z - 0.25),
                        (x + swing, FIRE_TAIL_Y, FIRE_Z - 0.55)], 10)
        n = len(path)
        widths = [FIRE_TAIL_W * (1.0 - m / (n - 1)) ** 0.7 for m in range(n)]
        parts.append(band(f"flame{i}", path, widths, [w * 0.82 for w in widths], shades, shade, segments=24))
    return parts


# --- 93: Lightning Zone --------------------------------------------------------------------------------------------

# The bolt's kinks from its top down to the nose (the sprite's brightest pixels), its half-width and height, the core's;
# its colours.
BOLT = [(AXIS - 0.3, 12.9), (AXIS - 2.75, 10.35), (AXIS + 2.05, 7.45), (AXIS - 1.1, 5.35), (AXIS + 1.3, 3.25),
        (AXIS, 1.25)]
BOLT_W, BOLT_H, BOLT_Z, BOLT_CORE_W = 0.95, 0.8, 1.9, 0.4
LIGHTNING = {"*": (0x9a, 0x9b, 0.5), "top": (0x9d, 0x9e, 0.55), "core": (0x8f, 0x8f, 0.62), "flare": (0x8e, 0x8f, 0.6)}


def jagged(points, z, per_segment=4):
    """The zigzag through the points, straight between them (points along each segment for the tube's rings)."""
    out = []
    for (ax, ay), (bx, by) in zip(points, points[1:]):
        for i in range(per_segment):
            t = i / per_segment
            out.append((ax + (bx - ax) * t, ay + (by - ay) * t, z))
    out.append((*points[-1], z))
    return out


def lightning_zone():
    parts = fighter_at(-7.0)
    mats = {key: glow_mat(f"bolt_{key}", index, emit, strength, 0.0, 0.25)
            for key, (index, emit, strength) in LIGHTNING.items()}
    path = jagged(BOLT, BOLT_Z)
    n = len(path)
    # Pointed at its top, full down to the nose.
    widths = [BOLT_W * min(1.0, 0.25 + i / 3.0) for i in range(n)]
    parts.append(band("bolt", path, widths, [w * BOLT_H / BOLT_W for w in widths],
                      {"*": mats["*"], "top": mats["top"]}, lambda t, a: "top" if 50.0 < a < 130.0 else "*",
                      segments=12))
    zc = BOLT_Z + BOLT_H - 0.12
    core = jagged(BOLT, zc)[1:-1]
    cw = [BOLT_CORE_W * min(1.0, 0.3 + i / 3.0) for i in range(len(core))]
    cw[-1] = 0.0
    parts.append(band("bolt_core", core, cw, [w * 0.75 for w in cw], {"*": mats["core"]}, segments=8))
    parts += flare("bolt_flare", (AXIS, 1.0, 2.3), 2.0, mats["flare"], 45.0)
    return parts


# --- 125: the question mark ----------------------------------------------------------------------------------------

# Its hook and stem from the hook's left end round to the stem's foot (the middles of its strokes, 3 pixels wide), the
# stroke's half-width and height, the dot (middle, radius), how high they lie; their colours.
HOOK = [(AXIS - 3.0, 7.5), (AXIS - 3.0, 8.9), (AXIS - 2.45, 10.25), (AXIS - 0.5, 11.0), (AXIS + 1.45, 10.3),
        (AXIS + 2.05, 9.0), (AXIS + 1.55, 7.55), (AXIS + 0.85, 6.6), (AXIS + 0.15, 5.6), (AXIS, 4.75)]
MARK_W, MARK_H, MARK_Z = 1.55, 1.2, 1.75
DOT, DOT_R = (AXIS, 2.45), 1.55
MARK = {"*": (0x29, 0x29, 0.42), "top": (0x2b, 0x2a, 0.46)}
DOT_BANDS = [(-1.0, 0x29, 0x29, 0.42), (0.55, 0x2b, 0x2a, 0.46)]


def question_mark():
    parts = fighter_at(-8.0)
    mats = {key: glow_mat(f"mark_{key}", index, emit, strength, 0.1, 0.22)
            for key, (index, emit, strength) in MARK.items()}
    path = catmull([(x, y, MARK_Z) for x, y in HOOK], 6)
    n = len(path)
    lengths = [0.0]
    for a, b in zip(path, path[1:]):
        lengths.append(lengths[-1] + (b - a).length)
    widths = []
    for d in lengths:
        end = min(d, lengths[-1] - d)
        widths.append(MARK_W * math.sqrt(max(0.0, 1.0 - (1.0 - min(end / MARK_W, 1.0)) ** 2)))
    # Round ends: the first and last rings close in points just beyond.
    parts.append(band("mark", path, widths, [w * MARK_H / MARK_W for w in widths], mats,
                      lambda t, a: "top" if 45.0 < a < 135.0 else "*", segments=16))
    dot_mats = [mats["*"], mats["top"]]
    parts.append(ball("mark_dot", (DOT[0], DOT[1], MARK_Z), (DOT_R, DOT_R, DOT_R * MARK_H / MARK_W), dot_mats,
                      [DOT_BANDS[1][0]], 24, 12))
    assert n > 2
    return parts


# --- 127: Xega Ball ------------------------------------------------------------------------------------------------

# The ball (middle, radii), its bands by slope (lower border, palette index, glowing in, glow), the ribs (offsets of the
# planes from its middle, their half-width) and their colour.
XEGA_C, XEGA_R = (AXIS, 10.0, 2.75), (3.45, 3.2, 3.05)
XEGA_BANDS = [(-1.0, 0x46, 0x47, 0.3), (0.3, 0x48, 0x49, 0.36), (0.65, 0x4a, 0x4b, 0.42), (0.88, 0x4b, 0x4c, 0.46)]
XEGA_RIBS, XEGA_RIB_W = (-1.75, 0.0, 1.75), 0.26
XEGA_RIB = (0x43, 0x44, 0.2)


def xega_ball():
    parts = fighter_at(0.0)
    mats = [glow_mat(f"xega{i}", index, emit, strength, 0.1, 0.3)
            for i, (_, index, emit, strength) in enumerate(XEGA_BANDS)]
    parts.append(ball("xega", XEGA_C, XEGA_R, mats, [b[0] for b in XEGA_BANDS[1:]], 40, 20, floor=0.0))
    index, emit, strength = XEGA_RIB
    rib = glow_mat("xega_rib", index, emit, strength, 0.2, 0.35)
    cx, cy, cz = XEGA_C
    rx, ry, rz = XEGA_R
    for turn in (45.0, -45.0):
        a = math.radians(turn)
        normal = Vector((math.cos(a), math.sin(a), 0.0))
        along = Vector((-math.sin(a), math.cos(a), 0.0))
        for j, d in enumerate(XEGA_RIBS):
            # The circle where the plane (at d along normal) cuts the unit sphere, scaled to the ball's radii and laid
            # a little out of its surface; its upper part (above the ball's widest).
            rho = math.sqrt(1.0 - (d / 3.3) ** 2)
            pts = []
            for i in range(25):
                th = math.radians(8.0 + 164.0 * i / 24)
                u = (d / 3.3) * normal + rho * (math.cos(th) * along + Vector((0, 0, math.sin(th))))
                p = Vector((u.x * rx, u.y * ry, u.z * rz))
                out = Vector((u.x / rx, u.y / ry, u.z / rz)).normalized()
                pts.append(Vector((cx, cy, cz)) + p + out * 0.06)
            widths = [XEGA_RIB_W * min(1.0, 4.0 * min(i, 24 - i) / 24 + 0.35) for i in range(25)]
            widths[0] = widths[-1] = 0.0
            parts.append(band(f"xega_rib{int(turn)}_{j}", pts, widths, widths, {"*": rib}, segments=8))
    return parts


# --- 129: the pearls -----------------------------------------------------------------------------------------------

# The eight pearls' middles (the sprite's 4 x 4 pearls), their radius, height and how high they float; their bands.
PEARLS = [(0.0, 10.0), (-5.0, 6.0), (6.0, 6.0), (-8.0, 0.0), (9.0, 0.0), (-6.0, -5.0), (7.0, -5.0), (1.0, -8.0)]
PEARL_R, PEARL_SQUASH, PEARL_Z = 1.95, 0.88, 2.0
PEARL_BANDS = [(-1.0, 0x85, 0x86, 0.3), (0.3, 0x89, 0x8a, 0.36), (0.7, 0x8c, 0x8d, 0.42), (0.92, 0x8e, 0x8e, 0.46)]


def pearl_ring():
    parts = fighter_at(0.0)
    mats = [glow_mat(f"pearl{i}", index, emit, strength, 0.1, 0.15)
            for i, (_, index, emit, strength) in enumerate(PEARL_BANDS)]
    for i, (x, y) in enumerate(PEARLS):
        parts.append(ball(f"pearl{i}", (x, y, PEARL_Z), (PEARL_R, PEARL_R, PEARL_R * PEARL_SQUASH), mats,
                          [b[0] for b in PEARL_BANDS[1:]], 24, 12))
    return parts


# --- 131: Dual Vulcan ----------------------------------------------------------------------------------------------

# The sparks' middles (two columns over the blade tips), their length and half-width, how high they float; their bands
# along them and the core in the head.
SPARKS = [(AXIS - 5.0, 8.0), (AXIS + 5.0, 8.0), (AXIS - 5.0, 3.0), (AXIS + 5.0, 3.0)]
SPARK_L, SPARK_W, SPARK_Z, SPARK_SQUASH = 5.0, 1.55, 2.4, 0.85
SPARK = {"dark": (0x73, 0x74, 0.32), "*": (0x77, 0x78, 0.44), "hot": (0x7a, 0x7b, 0.52)}
SPARK_CORE = (0x7e, 0x7e, 0.62)


def dual_vulcan():
    parts = fighter_at(0.0)
    mats = {key: glow_mat(f"spark_{key}", index, emit, strength, 0.0, 0.45)
            for key, (index, emit, strength) in SPARK.items()}
    core = glow_mat("spark_core", *SPARK_CORE[:2], SPARK_CORE[2], 0.0, 0.4)

    def pick(t, a):
        if t < 0.3:
            return "dark"
        return "hot" if t > 0.5 and 50.0 < a < 130.0 else "*"
    for i, (x, y) in enumerate(SPARKS):
        y0, y1 = y - SPARK_L * 0.55, y + SPARK_L * 0.45
        head = y1 - SPARK_W
        path, widths = [], []
        for j in range(19):
            u = j / 18
            yy = y0 + (y1 - y0) * (1.0 - (1.0 - u) ** 1.3)
            if yy >= head:
                w = math.sqrt(max(0.0, SPARK_W ** 2 - (yy - head) ** 2))
            else:
                w = SPARK_W * ((yy - y0) / (head - y0)) ** 0.7
            path.append((x, yy, SPARK_Z))
            widths.append(w)
        parts.append(band(f"spark{i}", path, widths, [w * SPARK_SQUASH for w in widths], mats, pick, segments=14))
        centre = (x, head + 0.25, SPARK_Z + SPARK_W * SPARK_SQUASH - 0.3)
        parts.append(k.smooth(k.ellipsoid(f"spark_core{i}", centre, (0.65, 0.9, 0.45), core, 12, 6), 80))
    return parts


# --- 283: MineField ------------------------------------------------------------------------------------------------

# The six mines round the capsule (the sprite's 3 x 4-pixel crosses), their radius, how high they float, their spikes
# (length, radius at the root); their colours: the cradle's materials (the game keeps a model's first 16 materials
# only, render_gpu.c LoadedModel, and the Zinglon's capsule and fighter have 15), the body in bands by its slope
# (lower border, cradle band), the spikes.
MINES = [(-7.5, 4.0), (7.5, 6.0), (-8.5, -4.0), (10.5, -2.0), (9.5, -8.0), (-5.5, -10.0)]
MINE_R, MINE_Z, SPIKE_L, SPIKE_R = 1.2, 1.9, 1.05, 0.42
MINE_BANDS = [(-1.0, 2), (0.5, 1), (0.85, 0)]
MINE_SPIKE = 1


def spike(name, base, direction, length, radius, mat):
    """A cone from base along direction."""
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=8, radius1=radius, radius2=0.0, depth=length)
    # create_cone is centred on the origin along z: its base at -length / 2.
    turn = Vector((0, 0, 1)).rotation_difference(Vector(direction).normalized()).to_matrix().to_4x4()
    bmesh.ops.transform(bm, matrix=Matrix.Translation(base) @ turn @ Matrix.Translation((0, 0, length / 2)),
                        verts=bm.verts[:])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return k.smooth(kit.from_bmesh(name, bm, mat), 40)


def minefield():
    parts = ps.soul_of_zinglon()
    cradle = {i: bpy.data.materials["cradle%d@%d" % (i, index)] for i, (_, index, _, _) in enumerate(ps.CRADLE_BANDS)}
    mats = [cradle[i] for _, i in MINE_BANDS]
    for i, (x, y) in enumerate(MINES):
        parts.append(ball(f"mine{i}", (x, y, MINE_Z), (MINE_R, MINE_R, MINE_R), mats,
                          [b[0] for b in MINE_BANDS[1:]], 16, 8))
        for j, d in enumerate(((1, 0, 0), (0, 1, 0), (-1, 0, 0), (0, -1, 0), (0, 0, 1))):
            base = Vector((x, y, MINE_Z)) + Vector(d) * (MINE_R * 0.75)
            parts.append(spike(f"mine{i}_spike{j}", base, d, SPIKE_L, SPIKE_R, cradle[MINE_SPIKE]))
    return parts


# --- Building ------------------------------------------------------------------------------------------------------

MODELS = [
    ("pu_pulse_blast", 55, pulse_blast),
    ("pu_megalaser", 91, megalaser),
    ("pu_megalaser_dual_red", 279, megalaser_dual_red),
    ("pu_megalaser_twin_blue", 53, megalaser_twin_blue),
    ("pu_lightning_zone", 93, lightning_zone),
    ("pu_question_mark", 125, question_mark),
    ("pu_xega_ball", 127, xega_ball),
    ("pu_pearl_ring", 129, pearl_ring),
    ("pu_dual_vulcan", 131, dual_vulcan),
    ("pu_minefield", 283, minefield),
]


def build():
    opts = kit.options()
    for name, sprite, make in MODELS:
        if not kit.wanted(opts, name):
            continue
        k.reset()
        ps.FIGHTER.clear()
        parts = make()
        for obj in parts:
            kit.apply(obj)
            kit.drop_unused_materials(obj)
        ps.triangulate(parts)
        bpy.context.view_layer.update()
        # (The game keeps a model's first 16 materials only: render_gpu.c LoadedModel.materials.)
        assert len(kit.materials_of(parts)) <= 16, (name, kit.materials_of(parts))
        ps.check(opts, "%s (powerups %d)" % (name, sprite), parts, sprite)
        bpy.context.scene.view_settings.view_transform = "Standard"
        kit.report(name, parts, os.path.join(kit.outdir(opts), name + ".glb"))
        if "preview" in opts:
            kit.preview(opts["preview"] + name, parts, (24, 28), scale=16, distance=0.6)


if __name__ == "__main__":
    build()
