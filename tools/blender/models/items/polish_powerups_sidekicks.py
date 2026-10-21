"""The sidekick pick-ups of the power-ups sheet ("twoplayer" in the catalogue; values 32001-32015, the sidekick they
give) and the dragonwing's pick-up (value 30000), polished (2026-10-21; they replace powerups_sidekicks.py's
models): a green orb with the sidekick's symbol on its face. 2x2 sprites, 24 x 28 pixels, one frame each; dropped by
enemies in every episode (episode 1's MicroBomb also lies on the ground: catalogue layer "ground"). models.cfg: model
pu_<name> items/pu_<name>.glb and sprite powerups <n> pu_<name> yaw=0, unchanged (no spin: the symbols stay upright as
the sprites draw them, and the orb is painted for the camera).

- pu_single_shot (205): a red-hot shot, round at its nose, tapering to its tail (Single Shot Option)
- pu_dual_shot (207): two of them side by side (Dual Shot Option)
- pu_charge_cannon (229): a blob of blue plasma with a white-hot heart and three tendrils (Charge Cannon)
- pu_vulcan_shot (231): three red-hot needles flying up, staggered (Vulcan Shot Option)
- pu_atom_bombs (233): two grey canisters with a glowing red band round their waists, ribbed below (Atom Bombs)
- pu_mini_missile (235): three steel-blue missiles with red canards and swept fins (Mini-Missile)
- pu_mega_missile (237): a silver S over a salmon missile (MegaMissile)
- pu_microbomb (239): a steel ball with a glowing band round it (MicroBomb)
- pu_postit_mine (241): two crossed ridged blades, one steel, one gold, on a gold hub (Post-It Mine)
- pu_dragonwing (281): a red flying wing with a glass dome and a glowing engine (value 30000, see below)

Twins (checked against every sprite of the sheet, shifted, mirrored, turned and in other ramps): 205's shot is the
front Vulcan Cannon's bullet (165) pixel for pixel, and 207's two shots are 205's, the right one as it is and the left
one mirrored (only its shading is): all three are polish_powerups_front.vulcan()'s bullet (shots()). 229's outline
is the front Mega Cannon's (157) in blues: its FIRE shape. 281's ship is the Companion Ship Warfly's second frame
(powerups 89, pixel for pixel; sidekicks_ships.py's sk_warfly is its first frame, 87), on the same green orb. The
others have no twins. No other enemy shows these sprites (catalog.json, the launched enemies too).

The dragonwing's pick-up (281, enemy types 200 of episode 1, "** ALE **", and 729 of episode 4, SQUADRON): taking it
(mainint.c) brings the second player's ship in Galaga mode (the Dragonwing, ships 13 and 51: a wide bronze craft,
ships/dragonwing.py), and is a purple ball otherwise (a power level); its sprite draws the Warfly on the sidekicks'
green orb, so it is built like the sidekick pick-ups: the ship a relief on the orb's face.

The orb is polish_powerups_front.orb(2): the front weapons' orb of glazed ice, shade for shade in ramp 2 (green),
built in view space (the game camera's view, 20 degrees from straight down, from the bottom of the screen) and tilted
by to_world(), so that every symbol shows where the sprite draws it. The symbols are made as the front ones are:
reliefs (polish_powerups_front.relief(): a 2D field over the sprite's pixels raised over the orb's dome, its edge a
profile, its normals the shape's own) on a dark setting in the sprite's outline colour, painted in bands
(polish_powerups_front.paint()), the round bodies lathed and bent with the dome, glowing parts at 0.2-0.6 in their
own palette colours; at most 14 materials per model.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; origin at the
sprite's centre (pixel 12, 14); column c is x = c + 0.5 - 12, row r is y = 13.5 - r. The game centres the models in
height on their layer.

Replaces powerups_sidekicks.py (all of it: ICON_237, ICON_281, red_pod_materials(), the ten builders, canister(),
mini_missile(), MODELS), powerups_parts.py's RAMP_GREEN and POD_SHAPES' "bullet" (only powerups_sidekicks.py used
them), and powerups.py's import of powerups_sidekicks and its place in the MODELS loop.

Options after "--": --outdir <dir> (default assets/models/items), --check <sheets dir or powerups.png> (each model's
silhouette as the game's camera sees it and from straight above against its sprite, and the symbol's own against
the symbol's pixels), --preview <prefix> (top and 3/4 views), --only <name,...>.
"""
import collections
import math
import os
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_item_kit as kit  # noqa: E402
from polish_item_kit import k  # noqa: E402
import polish_powerups_front as front  # noqa: E402
from polish_powerups_front import (capsule, circle, depth_of, dome, ellipse, exact, glowing,  # noqa: E402
                                   grow, intersect, material, mirror_half, paint, polygon, relief,
                                   round_profile, rounded, union)

ORB_RAMP = 2   # green


def surface(shape, top, profile, base=dome):
    """The height of a relief's top at (x, y) (the relief of shape, top and profile, over base): to set other
    reliefs on it."""
    f = exact(shape)
    depths = [d for d, _ in profile]
    unders = [u for _, u in profile]

    def height(x, y):
        d = -float(f(x, y))
        return base(x, y) + top - float(np.interp(d, depths, unders))
    return height


def bent(obj, base=dome, lift=0.0):
    """Raises an object built over z = 0 by base(x, y) (plus lift) under each vertex."""
    for v in obj.data.vertices:
        v.co.z += base(v.co.x, v.co.y) + lift
    obj.data.update()
    return obj


# --- Single Shot Option and Dual Shot Option: the Vulcan Cannon's bullets ---------------------------------------------
# 205's shot is pixel for pixel one of the front Vulcan Cannon's three bullets (165: columns 10-14 from row 5), three
# rows lower (columns 10-14 from row 8); 207's two are 205's moved to columns 6-10 (mirrored) and 13-17, a row lower.
# So they are built by the front's vulcan() itself, its bullets moved: a red bullet (0x74, 0x77) with a hot stripe
# along its top (0x76 at the tail, 0x79, 0x7c at the nose), on a dark setting (0x41: the sprite's 0x41, 0x10, 0x70).

def shots(places):
    """polish_powerups_front.vulcan()'s bullets at places [(x, top), ...] (its setting, bullets and stripes)."""
    kept = front.BULLETS
    front.BULLETS = [tuple(p) for p in places]
    try:
        return front.vulcan()
    finally:
        front.BULLETS = kept


def single_shot():
    """205: one shot (column 12, from row 8)."""
    return shots([(0.5, 6.0)])


def dual_shot():
    """207: two shots (columns 8 and 15, from row 9)."""
    return shots([(-3.5, 5.0), (3.5, 5.0)])


# --- Charge Cannon: a blob of blue plasma -----------------------------------------------------------------------------
# The sprite's blob is the front Mega Cannon's fireball outline (157: columns 6-17, rows 6-20, three tongues below)
# drawn in blues: mid blue inside its dark outline (0x30, 0x32, 0x90), lighter inwards (0x98, 0x9c), a pale heart in
# its upper middle (0x89-0x8f, white-hot at rows 10-11), darker downwards (0x99-0x93) into its three tendrils (0x92,
# 0x90). A dome of glowing plasma (FIRE, the fireball's profile), banded by its depth falling off downwards, the
# heart a pale halo round a white core.

CHARGE_FALL = 0.24                          # how much shallower the bands lie per pixel down (darker downwards)
CHARGE_BANDS = [0.45, 1.15, 1.95]
CHARGE_HEART = ellipse(0.0, 2.5, 1.95, 2.75)
CHARGE_CORE = ellipse(0.0, 3.0, 0.95, 1.35)
CHARGE_HALO = 0.75


def charge_cannon():
    """229: a blob of blue plasma."""
    setting = material("charge_setting", 0x32, 0.3, 0.3)
    body = [glowing("charge0", 0x93, 0x95, 0.28, 0.05, 0.2), glowing("charge1", 0x96, 0x97, 0.32, 0.05, 0.2),
            glowing("charge2", 0x99, 0x9a, 0.38, 0.05, 0.2), glowing("charge3", 0x9c, 0x9d, 0.44, 0.05, 0.2)]
    heart = [glowing("charge_halo", 0x9f, 0x8a, 0.46, 0.05, 0.15),
             glowing("charge_heart", 0x8c, 0x8d, 0.52, 0.05, 0.15),
             glowing("charge_core", 0x8f, 0x8f, 0.6, 0.05, 0.15)]
    shape = rounded(front.FIRE, 0.2, 0.6)
    plasma = grow(shape, -0.75)
    parts = [relief("charge_setting", shape, 0.4, setting, bevel=0.3, segments=2, inner=0, hollow=1.6),
             relief("charge", plasma, 2.9, body[0], profile=round_profile(4.4, 2.5, 7, power=1.3), inner=1,
                    spacing=0.5)]
    depth = depth_of(plasma)

    def falling(x, y, z):
        a = np.arctan2(y - 2.0, x)
        return depth(x, y, z) + CHARGE_FALL * (y - 2.0) + 0.14 * np.sin(5 * a + 0.7)
    paint(parts[1], falling, CHARGE_BANDS, body)
    halo, core = exact(CHARGE_HEART), exact(CHARGE_CORE)
    paint(parts[1], lambda x, y, z: -halo(x, y), [-CHARGE_HALO, 0.0], [None, heart[0], heart[1]])
    paint(parts[1], lambda x, y, z: -core(x, y), [0.0], [None, heart[2]])
    return parts


# --- Vulcan Shot Option: three needles --------------------------------------------------------------------------------
# The sprite's three needles (columns 11, 13 and 9 from rows 7, 9 and 11, ten pixels long), each one pixel wide in a
# dark slot of 0x70 round them all, red-hot near the nose (0x75, 0x7a, 0x7c, 0x79, 0x77 from the top), dark red down
# its tail (0x75, 0x73, 0x71). Slim spindles (reliefs, round across), pointed at the nose, tapering to the tail, in
# the Vulcan Cannon's reds, banded along their length.

NEEDLES = [(-0.5, 7.0), (1.5, 5.0), (-2.5, 3.0)]    # (x, top of the red) of each
NEEDLE_LENGTH = 10.0
NEEDLE_W = 0.78                                      # half its width at its widest


def needle_shape(x, top):
    """A needle nose up: a long point over its first 2.6 pixels, widest below it, tapering to a blunt tail."""
    w, length = NEEDLE_W, NEEDLE_LENGTH
    right = [(0.0, top + 0.35), (0.28 * w, top - 0.3), (0.62 * w, top - 1.1), (0.9 * w, top - 2.0), (w, top - 3.0),
             (w, top - 5.5), (0.9 * w, top - 7.5), (0.72 * w, top - 9.0), (0.5 * w, top - length + 0.1),
             (0.0, top - length - 0.2)]
    return polygon([(x + px, py) for px, py in mirror_half(right)])


def vulcan_shot():
    """231: three needles."""
    setting = material("needle_setting", 0x70, 0.3, 0.3)
    mats = [glowing("needle_tail", 0x72, 0x73, 0.28, 0.2, 0.22), glowing("needle_low", 0x75, 0x76, 0.36, 0.2, 0.22),
            glowing("needle_mid", 0x78, 0x79, 0.46, 0.2, 0.2), glowing("needle_hot", 0x7b, 0x7c, 0.56, 0.2, 0.2),
            glowing("needle_tip", 0x76, 0x77, 0.4, 0.2, 0.2)]
    shapes = [needle_shape(x, top) for x, top in NEEDLES]
    parts = [relief("needle_setting", rounded(grow(union(*shapes), 0.85), 0.0, 0.6), 0.45, setting, bevel=0.3,
                    segments=2, inner=1)]
    for i, ((x, top), shape) in enumerate(zip(NEEDLES, shapes)):
        obj = relief(f"needle{i}", shape, 1.75, mats[0], profile=round_profile(NEEDLE_W, 1.15, 5), inner=0,
                     spacing=0.3)

        def along(xs, ys, zs, top=top):
            return ys - top
        paint(obj, along, [-7.0, -4.6, -2.8, -0.6], mats)
        parts.append(obj)
    return parts


# --- Atom Bombs: two canisters ----------------------------------------------------------------------------------------
# The sprite's two canisters (columns 4-11 and 12-19, rows 7-20, the right one the left one's pixels moved 8 to the
# right), drawn lying along the screen: a grey top half (rows 7-11, its end rounded, lit at the left: 0x04-0x0f), a
# glowing red band in a narrower waist (rows 12-15: 0x72-0x7c, hottest at its left, its edges 0x72 and dark sides
# 0xa1, 0x10), a lighter ribbed bottom half (rows 16-19: light ribs 0x0d, 0x0e between darker grooves) ending in short
# teeth (row 20), in a dark outline (0x01, 0x02, 0x20). Lathed (a section through every part), the bottom half fluted,
# lying on the dome.

CANISTERS = [-4.0, 4.0]          # their axes' x
CANISTER_SQUASH, CANISTER_LIFT = 0.74, 0.35
FLUTES, FLUTE_DEPTH = 6, 0.32
# The canister's profile from its top down: (y, radius, part) (the part of the band from it to the next section).
CANISTER = [(7.0, 0.0, "top"), (6.93, 1.25, "top"), (6.75, 2.05, "top"), (6.45, 2.62, "top"), (6.05, 3.0, "top"),
            (5.55, 3.18, "top"), (4.6, 3.22, "top"), (2.6, 3.22, "top"), (2.35, 3.12, "ring"), (2.05, 2.7, "ring"),
            (1.85, 2.62, "band"), (1.3, 2.78, "band"), (0.5, 2.86, "band"), (-0.5, 2.86, "band"),
            (-1.3, 2.78, "band"), (-1.85, 2.62, "ring"), (-2.05, 2.7, "ring"), (-2.35, 3.12, "low"),
            (-2.6, 3.24, "low"), (-5.3, 3.24, "low"), (-5.75, 3.05, "low"), (-6.05, 2.6, "end"), (-6.25, 1.7, "end"),
            (-6.3, 0.0, "end")]
# The band's hot spot (the sprite's 0x7a, 0x7c at columns 6-7 of rows 13-14: left of the top): between these
# heights, and these angles round the axis (degrees from the top, negative to the left).
BAND_HOT = (-0.6, 1.4, -68.0, -12.0)
CANISTER_FINISH = {
    "top": (0x0a, 0.35, 0.28), "ring": (0x03, 0.3, 0.4), "low": (0x0c, 0.35, 0.28), "groove": (0x0a, 0.3, 0.3),
    "end": (0x08, 0.3, 0.32),
}


def canister(name, x, mats, segments=40):
    """A canister lying along y at x (its sections CANISTER, flutes round its bottom half), set on the dome."""
    bm = bmesh.new()
    rings = []
    for y, r, part in CANISTER:
        if r <= 0.0:
            rings.append([bm.verts.new((x, y, 0.0))])
            continue
        ring = []
        for j in range(segments):
            a = 2 * math.pi * j / segments
            rr = r
            if part in ("low",) or (part == "end" and r > 2.0):
                rr = r - FLUTE_DEPTH * (0.5 + 0.5 * math.cos(FLUTES * a)) ** 2
            ring.append(bm.verts.new((x + rr * math.sin(a), y, rr * CANISTER_SQUASH * math.cos(a))))
        rings.append(ring)
    order = list(mats)
    y0, y1, a0, a1 = BAND_HOT
    for i, (a, b) in enumerate(zip(rings, rings[1:])):
        part = CANISTER[i][2]
        y_mid = (CANISTER[i][0] + CANISTER[i + 1][0]) / 2
        for j in range(segments):
            j1 = (j + 1) % segments
            if len(a) == 1:
                f = bm.faces.new((a[0], b[j1], b[j]))
            elif len(b) == 1:
                f = bm.faces.new((a[j], a[j1], b[0]))
            else:
                f = bm.faces.new((a[j], a[j1], b[j1], b[j]))
            key = part
            angle = (math.degrees(2 * math.pi * (j + 0.5) / segments) + 180.0) % 360.0 - 180.0
            if part == "low" and math.cos(FLUTES * 2 * math.pi * (j + 0.5) / segments) > 0.7:
                key = "groove"
            elif part == "band" and y0 < y_mid < y1 and a0 < angle < a1:
                key = "band_hot"
            f.material_index = order.index(key)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    obj = kit.from_bmesh(name, bm)
    for key in order:
        obj.data.materials.append(mats[key])
    bent(obj, lift=CANISTER_LIFT)
    k.smooth(obj, 50.0)
    kit.drop_unused_materials(obj)
    return obj


def canister_plan(x):
    """The canister's outline from above."""
    right = [(r, y) for y, r, _ in CANISTER]
    return polygon([(x + px, py) for px, py in mirror_half(right)])


def atom_bombs():
    """233: two canisters."""
    setting = material("canister_setting", 0x01, 0.3, 0.35)
    mats = {key: material("canister_" + key, index, metallic, roughness)
            for key, (index, metallic, roughness) in CANISTER_FINISH.items()}
    mats["band"] = glowing("canister_band", 0x75, 0x77, 0.4, 0.2, 0.2)
    mats["band_hot"] = glowing("canister_band_hot", 0x7a, 0x7c, 0.55, 0.2, 0.2)
    plan = union(*[canister_plan(x) for x in CANISTERS])
    parts = [relief("canister_setting", rounded(grow(plan, 0.75), 0.0, 0.8), 0.4, setting, bevel=0.3, segments=2,
                    inner=1)]
    for i, x in enumerate(CANISTERS):
        parts.append(canister(f"canister{i}", x, dict(mats)))
    return parts


# --- Mini-Missile: three missiles -------------------------------------------------------------------------------------
# The sprite's three missiles nose up (columns 10-14 from row 4, 15-19 from row 7, 4-10 from row 10; each 13 rows
# long), staggered: a rounded nose (0x3b-0x3d), red canards a row under it (0x74, 0x73), a steel-blue body three
# pixels wide (0x36-0x3c, its middle lighter), a darker ring under the canards (0x36, 0x39, 0x33), swept fins at its
# tail (0x3a, 0x3b) and a dark nozzle (0x63, 0x01), all in a dark outline (0x30-0x32, 0x50, 0x51). The front Missile
# Launcher's way: lathed bodies bent with the dome, flat fins and canards, a dark setting under them.

MINI_MISSILES = [(0.5, 10.0), (5.5, 7.0), (-4.5, 4.0)]   # (x, top) of each
MINI = [(-12.0, 0.0), (-11.95, 0.5), (-11.8, 0.85), (-11.5, 1.15), (-11.0, 1.4), (-10.5, 1.45), (-8.7, 1.45),
        (-7.0, 1.45), (-5.2, 1.45), (-3.4, 1.45),
        (-3.2, 1.33), (-2.75, 1.33), (-2.5, 1.45), (-1.9, 1.42), (-1.35, 1.22), (-0.9, 0.9), (-0.6, 0.5),
        (-0.45, 0.0)]
MINI_FIN = [(1.1, -7.6), (1.75, -8.2), (2.4, -9.3), (2.75, -10.9), (2.75, -12.3), (2.2, -12.85), (1.65, -12.2),
            (1.35, -11.5), (1.1, -11.2)]
MINI_CANARD = [(1.1, -1.8), (1.7, -2.05), (2.3, -2.6), (2.4, -3.15), (1.1, -3.1)]


def mini_missile():
    """235: three mini missiles."""
    setting = material("mini_setting", 0x32, 0.3, 0.35)
    fin_mat = material("mini_fin", 0x3a, 0.35, 0.26)
    body = [material("mini_nozzle", 0x63, 0.3, 0.35), fin_mat, material("mini_body", 0x3b, 0.35, 0.24),
            material("mini_ring", 0x37, 0.3, 0.3), material("mini_head", 0x3c, 0.35, 0.22),
            material("mini_nose", 0x3d, 0.35, 0.2)]
    canard_mat = glowing("mini_canard", 0x74, 0x76, 0.28, 0.25, 0.25)
    plans = []
    for x, top in MINI_MISSILES:
        body_plan = front.silhouette([(top + y, r) for y, r in MINI])     # on x = 0: moved to x
        plans.append(lambda xs, ys, f=body_plan, x=x: f(np.asarray(xs) - x, ys))
        for side in (1, -1):
            plans.append(polygon([(x + side * fx, top + fy) for fx, fy in MINI_FIN]))
            plans.append(polygon([(x + side * fx, top + fy) for fx, fy in MINI_CANARD]))
    parts = [relief("mini_setting", rounded(grow(union(*plans), 0.75), 0.0, 0.5), 0.4, setting, bevel=0.3,
                    segments=2, inner=1)]
    for i, (x, top) in enumerate(MINI_MISSILES):
        for side in (1, -1):
            fin = polygon([(x + side * fx, top + fy) for fx, fy in MINI_FIN])
            parts.append(relief(f"mini_fin{i}{side}", rounded(fin, 0.25, 0.0), 1.15, fin_mat, bevel=0.25, segments=2,
                                inner=1))
            canard = polygon([(x + side * fx, top + fy) for fx, fy in MINI_CANARD])
            parts.append(relief(f"mini_canard{i}{side}", rounded(canard, 0.2, 0.0), 1.35, canard_mat, bevel=0.22,
                                segments=2, inner=0))
        obj = front.rocket_body(f"mini{i}", [(top + y, r) for y, r in MINI], body[2], 0.85, segments=22, squash=0.85)
        obj.data.transform(Matrix.Translation((x, 0.0, 0.0)))
        # the dome under the moved body (rocket_body bent it on x = 0)
        for v in obj.data.vertices:
            v.co.z += dome(v.co.x, v.co.y) - dome(v.co.x - x, v.co.y)
        obj.data.update()
        paint(obj, lambda xs, ys, zs, top=top: ys - top, [-11.45, -7.7, -3.4, -2.6, -1.05], body)
        parts.append(obj)
    return parts


# --- MegaMissile: a silver S over a missile ---------------------------------------------------------------------------
# The sprite's silver S (columns 6-16, rows 7-16: three bars two rows high and two upright strokes, light along its
# upper middle, 0x3a-0x3f) over a salmon missile (ramp 4: its nose above the S, rows 4-6, 0x4b-0x4e; its body in the
# S's gaps, 0x44-0x4b; three feet under the S, rows 17-18: its two fins and its nozzle), in a dark outline (0x20). A
# fat salmon rocket lathed along the middle with swept fins, and the S a relief over it, banded by height.

S_OUTLINE = [(-4.0, 7.0), (4.0, 7.0), (4.0, 5.0), (-3.0, 5.0), (-3.0, 3.0), (4.0, 3.0), (4.0, 2.0), (5.0, 2.0),
             (5.0, -2.0), (4.0, -2.0), (4.0, -3.0), (-5.0, -3.0), (-5.0, -1.0), (2.0, -1.0), (2.0, 1.0), (-5.0, 1.0),
             (-5.0, 2.0), (-6.0, 2.0), (-6.0, 5.0), (-5.0, 5.0), (-5.0, 6.0), (-4.0, 6.0)]
MEGA = [(-5.1, 0.0), (-5.0, 1.1), (-4.5, 1.05), (-3.7, 0.95), (-3.35, 1.45), (-3.0, 1.85), (-2.6, 2.0), (-1.4, 2.0),
        (-0.2, 2.0), (1.0, 2.0), (2.2, 2.0), (3.4, 2.0), (4.6, 2.0), (5.8, 2.0), (6.9, 2.0),
        (7.5, 1.85), (8.1, 1.45), (8.6, 0.95), (8.95, 0.45), (9.1, 0.0)]
MEGA_FIN = [(-1.9, 1.5), (-2.9, 0.4), (-3.75, -1.0), (-4.15, -2.8), (-4.05, -4.75), (-3.25, -5.0), (-2.45, -4.25),
            (-1.9, -3.4)]


def mega_missile():
    """237: a silver S over a missile."""
    setting = material("mega_setting", 0x20, 0.3, 0.35)
    salmon = [material("mega_nozzle", 0x43, 0.3, 0.32), material("mega_body", 0x48, 0.3, 0.26),
              material("mega_nose", 0x4b, 0.3, 0.24)]
    fin_mat = material("mega_fin", 0x46, 0.3, 0.28)
    s_low, s_mid, s_high = (material("s_low", 0x3b, 0.4, 0.22), material("s_mid", 0x3d, 0.4, 0.2),
                            material("s_high", 0x3e, 0.4, 0.2))
    silver = [s_low, s_mid, s_high, s_mid]     # from the bottom up: the S lightest along its upper middle
    letter = rounded(polygon(S_OUTLINE), 0.75, 0.3)
    fins = [polygon(MEGA_FIN), polygon([(-x, y) for x, y in MEGA_FIN])]
    plan = union(letter, front.silhouette(MEGA), *fins)
    parts = [relief("mega_setting", rounded(grow(plan, 0.75), 0.0, 0.6), 0.4, setting, bevel=0.3, segments=2,
                    inner=1)]
    for i, fin in enumerate(fins):
        parts.append(relief(f"mega_fin{i}", rounded(fin, 0.3, 0.0), 1.3, fin_mat, bevel=0.3, segments=2, inner=1))
    body = front.rocket_body("mega", MEGA, salmon[1], 0.6, segments=28, squash=0.8)
    paint(body, lambda x, y, z: y, [-3.3, 7.0], salmon)
    parts.append(body)
    s = relief("s", letter, 3.2, silver[0], bevel=0.42, segments=3, inner=2)
    paint(s, lambda x, y, z: y, [-1.2, 1.6, 4.6], silver)
    parts.append(s)
    return parts


# --- MicroBomb: a steel ball with a glowing band ----------------------------------------------------------------------
# The sprite's steel ball (columns 6-16, rows 9-19, round (-0.5, -0.5), in a dark outline 0x30: 0x34-0x3f, lit just
# above its band and again at its lower right) with a glowing band round its middle (rows 13-15, between dark red
# ends 0x70: 0x73-0x7f, white-hot at its upper left, 0x7f at column 9 of row 13). A full dome of steel (a little
# glow in its own blue, so that it doesn't read black from the slanted camera) with a raised belt over it, banded
# round its hot spot.

BOMB = (-0.5, -0.5)
BOMB_R = 5.95                     # the outline's
BALL_TOP, BALL_W, BALL_H = 3.75, 4.5, 3.35
BELT = (-1.95, 0.95)              # the band's lower and upper edge
BELT_HOT = (-2.2, 0.25, 2.3, 0.75)      # the hot streak: an ellipse (x, y, a, b)


def belt(name, centre, radius, y0, y1, base, mat, height=0.5, bevel=0.3, steps=44, across=7):
    """A band raised height over base(x, y) across a ball (its outline a circle round centre of radius) between y0
    and y1: sections across it every so often from one end to the other, each a wall up, a quarter round, a flat top
    and down again; its ends follow the ball's outline. (relief() fills a long straight band with triangles that
    span it end to end, chords sunk into a curved ball.)"""
    cx, cy = centre
    section = [(0.0, -0.8)]
    for i in range(4):
        a = math.pi / 2 * i / 3
        section.append((bevel * (1 - math.cos(a)), height - bevel + bevel * math.sin(a)))
    span = (y1 - y0) - 2 * bevel
    section += [(bevel + span * i / across, height) for i in range(1, across)]
    section += [((y1 - y0) - v, h) for v, h in reversed(section)]
    bm = bmesh.new()
    rings = []
    for s in range(steps + 1):
        u = s / steps
        ring = []
        for v, h in section:
            y = y0 + v
            reach = math.sqrt(max(radius * radius - (y - cy) ** 2, 0.0))
            x = cx - reach + 2 * reach * u
            ring.append(bm.verts.new((x, y, base(x, y) + h)))
        rings.append(ring)
    n = len(section)
    for a, b in zip(rings, rings[1:]):
        for j in range(n - 1):
            bm.faces.new((a[j], b[j], b[j + 1], a[j + 1]))
    for ring in (rings[0], rings[-1]):
        bm.faces.new(ring)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    if sum(f.normal.z * f.calc_area() for f in bm.faces) < 0:
        bmesh.ops.reverse_faces(bm, faces=bm.faces[:])
    obj = kit.from_bmesh(name, bm, mat)
    return k.smooth(obj, 50.0)


def microbomb():
    """239: a steel ball with a glowing band."""
    setting = material("bomb_setting", 0x30, 0.35, 0.3)
    steel = [glowing("bomb_rim", 0x38, 0x38, 0.12, 0.3, 0.24), glowing("bomb_steel", 0x3b, 0x3a, 0.14, 0.3, 0.2),
             glowing("bomb_light", 0x3d, 0x3c, 0.16, 0.3, 0.18)]
    band = [glowing("belt", 0x77, 0x78, 0.4, 0.15, 0.2), glowing("belt_warm", 0x79, 0x7a, 0.46, 0.15, 0.2),
            glowing("belt_hot", 0x7c, 0x7d, 0.54, 0.1, 0.18), glowing("belt_core", 0x7e, 0x7f, 0.6, 0.1, 0.18)]
    cx, cy = BOMB
    ball = circle(cx, cy, BOMB_R - 0.75)
    profile = round_profile(BALL_W, BALL_H, 8)
    parts = [relief("bomb_setting", circle(cx, cy, BOMB_R), 0.4, setting, bevel=0.3, segments=2, inner=0, hollow=1.6),
             relief("bomb", ball, BALL_TOP, steel[1], profile=profile, inner=1, spacing=0.45)]
    paint(parts[1], depth_of(ball), [0.45], [steel[0], None])
    light = circle(cx - 1.2, cy + 2.4, 1.8)
    paint(parts[1], lambda x, y, z: -light(x, y), [0.0], [None, steel[2]])
    ball_top = surface(ball, BALL_TOP, profile)
    obj = belt("belt", BOMB, BOMB_R - 0.6, BELT[0], BELT[1], ball_top, band[0])
    hot = ellipse(*BELT_HOT)
    paint(obj, lambda x, y, z: -hot(x, y), [-1.7, -0.75, 0.0], band)
    parts.append(obj)
    return parts


# --- Post-It Mine: two crossed blades ---------------------------------------------------------------------------------
# The sprite's X (columns 5-18, rows 6-19, round (0, 1)): a blade from the upper left to the lower right, dark steel
# (0x01-0x05) with a light steel ridge (0x64-0x6c), crossing a longer one from the upper right to the lower left, dark
# (0x02-0x05, 0x13, 0x16, 0xa2-0xa4) with a gold ridge (0xb6-0xbc), on a gold hub where they cross (0xb7-0xbf, white
# gold in its middle), in a dark outline (0x20, 0x50). Lofted blades, two facets meeting in a ridge along each (a
# narrow bright strip), their ends pointed, lying on the dome; a low four-sided gold pyramid over the crossing.

MINE_C = (0.0, 0.95)
BLADES = [((-5.25, 6.25), (5.5, -4.5), 1.8, "steel"), ((5.95, 7.15), (-6.05, -5.25), 1.85, "gold")]
BLADE_TAPER = 2.3  # how bluntly the blades narrow to their tips (higher: fuller)
HUB = 2.5          # the hub's half-diagonal along the blades


def blade(name, a, b, half_width, mats, z_edge=0.75, z_ridge=1.75, sections=22, ridge_w=0.42):
    """A straight blade from tip a to tip b, widest (half_width) at MINE_C's projection, its edges z_edge and its
    ridge z_ridge over the dome (both lower towards the tips); mats: "face", "ridge", "edge" (walls, underside)."""
    ax, ay = a
    bx, by = b
    d = Vector((bx - ax, by - ay))
    length = d.length
    d.normalize()
    n = Vector((-d.y, d.x))
    c = Vector(MINE_C)
    s_mid = (c - Vector(a)).dot(d) / length
    bm = bmesh.new()
    rings = []
    order = sorted(mats)
    for i in range(1, sections):
        s = i / sections
        t = (s - s_mid) / (s_mid if s < s_mid else 1.0 - s_mid)        # -1 at a, 0 at the middle, 1 at b
        w = half_width * (1.0 - abs(t) ** BLADE_TAPER)
        p = Vector(a) + d * (s * length)
        ze, zr = z_edge * (1.0 - 0.35 * abs(t)), z_ridge * (1.0 - 0.45 * abs(t) ** 1.5)
        rw = min(ridge_w, w * 0.3)
        pts = [(p - n * w, 0.0), (p - n * w, ze), (p - n * rw, zr - 0.04), (p, zr), (p + n * rw, zr - 0.04),
               (p + n * w, ze), (p + n * w, 0.0)]
        rings.append([bm.verts.new((q.x, q.y, z)) for q, z in pts])
    keys = ["edge", "face", "ridge", "ridge", "face", "edge"]          # from point j to j + 1
    m = len(rings[0])
    for r0, r1 in zip(rings, rings[1:]):
        for j in range(m - 1):
            f = bm.faces.new((r0[j], r0[j + 1], r1[j + 1], r1[j]))
            f.material_index = order.index(keys[j])
        f = bm.faces.new((r0[-1], r0[0], r1[0], r1[-1]))
        f.material_index = order.index("edge")
    for ring, tip in ((rings[0], a), (rings[-1], b)):
        apex = bm.verts.new((tip[0], tip[1], z_edge * 0.55))
        for j in range(m):
            f = bm.faces.new((ring[j], ring[(j + 1) % m], apex))
            f.material_index = order.index(keys[j] if j < m - 1 else "edge")
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    obj = kit.from_bmesh(name, bm)
    for key in order:
        obj.data.materials.append(mats[key])
    bent(obj)
    k.smooth(obj, 28.0)
    kit.drop_unused_materials(obj)
    return obj


def blade_plan(a, b, half_width, steps=22):
    """A blade's outline from above (as blade() builds it)."""
    ax, ay = a
    bx, by = b
    d = Vector((bx - ax, by - ay))
    length = d.length
    d.normalize()
    n = Vector((-d.y, d.x))
    c = Vector(MINE_C)
    s_mid = (c - Vector(a)).dot(d) / length
    left, right = [], []
    for i in range(steps + 1):
        s = i / steps
        t = (s - s_mid) / (s_mid if s < s_mid else 1.0 - s_mid)
        w = half_width * (1.0 - abs(t) ** BLADE_TAPER)
        p = Vector(a) + d * (s * length)
        left.append(tuple(p - n * w))
        right.append(tuple(p + n * w))
    return polygon(left + right[::-1])


def hub(name, mat, size=HUB, height=0.62, base=2.0):
    """A low four-sided pyramid over the crossing, its corners along the blades."""
    cx, cy = MINE_C
    corners = []
    for a, b, _, _ in BLADES:
        for tip in (a, b):
            v = Vector((tip[0] - cx, tip[1] - cy)).normalized()
            corners.append((cx + v.x * size, cy + v.y * size))
    corners.sort(key=lambda p: math.atan2(p[1] - cy, p[0] - cx))
    bm = bmesh.new()
    top = bm.verts.new((cx, cy, base + height))
    rim = [bm.verts.new((x, y, base)) for x, y in corners]
    # the waist between the corners, pulled in
    mids = []
    for i in range(4):
        (x0, y0), (x1, y1) = corners[i], corners[(i + 1) % 4]
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        mids.append(bm.verts.new((cx + (mx - cx) * 0.42, cy + (my - cy) * 0.42, base + height * 0.25)))
    low = [bm.verts.new((v.co.x, v.co.y, base - 1.0)) for v in rim]
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new((rim[i], mids[i], top))
        bm.faces.new((mids[i], rim[j], top))
        bm.faces.new((rim[i], low[i], low[j], rim[j]))
    bm.faces.new(low[::-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    obj = kit.from_bmesh(name, bm, mat)
    bent(obj)
    return obj


def postit_mine():
    """241: two crossed blades."""
    setting = material("mine_setting", 0x20, 0.3, 0.35)
    steel = {"face": material("blade_face", 0x05, 0.5, 0.3), "ridge": material("blade_ridge", 0x6d, 0.5, 0.18),
             "edge": material("blade_edge", 0x02, 0.4, 0.4)}
    gold = {"face": material("gold_face", 0xa4, 0.45, 0.3), "ridge": material("gold_ridge", 0xbd, 0.55, 0.16),
            "edge": steel["edge"]}
    hub_mat = glowing("mine_hub", 0xbc, 0xbe, 0.3, 0.5, 0.16)
    plans = [blade_plan(a, b, w) for a, b, w, _ in BLADES]
    parts = [relief("mine_setting", rounded(grow(union(*plans), 0.85), 0.0, 0.8), 0.4, setting, bevel=0.3,
                    segments=2, inner=1)]
    for i, (a, b, w, kind) in enumerate(BLADES):
        mats = steel if kind == "steel" else gold
        parts.append(blade(f"blade{i}", a, b, w, mats, z_edge=0.75 + 0.3 * i, z_ridge=1.7 + 0.3 * i))
    parts.append(hub("mine_hub", hub_mat))
    return parts


# --- The dragonwing's pick-up: the Warfly -----------------------------------------------------------------------------
# The sprite's ship (powerups 89's pixels: columns 3-21, rows 7-20): a red flying wing, its nose at column 12 of row
# 7, its tips at columns 3 and 21 of rows 15-16, its trailing edge along row 18, all in a dark outline (0x42, 0x41):
# a grey glass dome over the nose (columns 10-14 of rows 10-13: 0x60-0x6d, a white glint 0x3f), a keel down its
# middle (0x47-0x4b), puffed wing lobes either side (0x46-0x4e, lighter at their roots, the right one darker with a
# seam, 0x41), two steel intakes under the dome (0x33-0x38, 0xa3 vents) and the engine glowing at its tail (rows
# 18-19: 0x74-0x7a). A cushion of a wing (relief), the lobes raised on it with dark seams round them, the keel a
# ridge, the dome a glossy cabochon framed in the seams' dark red, the intakes, the engine a glowing nozzle.

SHIP = polygon(mirror_half([(0.0, 7.15), (0.6, 6.4), (1.75, 5.2), (2.75, 4.2), (3.7, 3.15), (5.6, 2.3), (6.9, 1.2),
                            (8.0, 0.2), (8.9, -0.75), (9.45, -1.5), (9.45, -2.6), (8.85, -3.45), (7.9, -4.3),
                            (6.6, -4.95), (2.9, -5.0), (2.35, -5.65), (1.6, -6.6), (0.0, -7.1)]))
SHIP_X = 0.5
SHIP_SHAPE = (lambda f: (lambda x, y: f(np.asarray(x) - SHIP_X, y)))(SHIP)
HULL_TOP, HULL_PROFILE = 1.65, round_profile(2.4, 1.15, 6)
LOBES = [(-4.3, -1.35, 3.35, 2.3, -33.0), (5.3, -1.35, 3.35, 2.3, 33.0)]    # (x, y, a, b, turn) of each
LOBE_TOP, LOBE_PROFILE = 0.8, round_profile(1.5, 0.9, 5)
DOME = (0.5, 2.05, 2.45, 2.0)
INTAKES = [(-1.1, -2.3, -35.0), (2.1, -2.3, 35.0)]
ENGINE = (0.5, -5.0, 1.65, 1.3)


def turned_ellipse(cx, cy, a, b, turn):
    c, s = math.cos(math.radians(turn)), math.sin(math.radians(turn))
    e = ellipse(0.0, 0.0, a, b)
    return lambda x, y: e((np.asarray(x) - cx) * c + (np.asarray(y) - cy) * s,
                          -(np.asarray(x) - cx) * s + (np.asarray(y) - cy) * c)


def dragonwing():
    """281: the Warfly on the green orb."""
    setting = material("wing_setting", 0x42, 0.3, 0.32)
    wing_mat = material("wing", 0x47, 0.35, 0.24)
    seam = material("wing_seam", 0x44, 0.3, 0.3)          # the hull's rim, the lobes' seams, the dome's frame
    lobe_mat = material("lobe", 0x4a, 0.35, 0.22)         # the lobes and the keel
    dome_mat = glowing("dome", 0x6c, 0x6d, 0.2, 0.2, 0.06)
    intake_mat = material("intake", 0x37, 0.45, 0.25)
    fire = [glowing("engine", 0x76, 0x77, 0.4, 0.1, 0.25), glowing("engine_hot", 0x7a, 0x7b, 0.55, 0.1, 0.2)]
    outline = rounded(SHIP_SHAPE, 0.35, 0.4)
    wing = grow(outline, -0.7)
    parts = [relief("wing_setting", outline, 0.4, setting, bevel=0.3, segments=2, inner=0, hollow=1.6),
             relief("wing", wing, HULL_TOP, wing_mat, profile=HULL_PROFILE, inner=3, spacing=0.5)]
    paint(parts[1], depth_of(wing), [0.45], [seam, None])
    top = surface(wing, HULL_TOP, HULL_PROFILE)
    for i, (x, y, a, b, turn) in enumerate(LOBES):
        lobe = intersect(turned_ellipse(x, y, a, b, turn), grow(wing, -0.35))
        obj = relief(f"lobe{i}", lobe, LOBE_TOP, lobe_mat, base=top, profile=LOBE_PROFILE, inner=1, spacing=0.4)
        paint(obj, depth_of(lobe), [0.35], [seam, None])
        parts.append(obj)
    keel = intersect(capsule(SHIP_X, 5.6, SHIP_X, -3.6, 0.95), grow(wing, -0.2))
    parts.append(relief("keel", keel, 0.5, lobe_mat, base=top, profile=round_profile(0.9, 0.5, 4), inner=0,
                        spacing=0.35))
    for i, (x, y, turn) in enumerate(INTAKES):
        parts.append(relief(f"intake{i}", turned_ellipse(x, y, 0.62, 1.15, turn), 0.45, intake_mat, base=top,
                            profile=round_profile(0.5, 0.4, 3), inner=0, spacing=0.3))
    dx, dy, da, db = DOME
    cab = ellipse(dx, dy, da, db)
    obj = relief("dome", cab, 1.45, dome_mat, base=top, profile=round_profile(1.9, 1.2, 6), inner=0, spacing=0.4)
    paint(obj, depth_of(cab), [0.32], [seam, None])
    parts.append(obj)
    ex, ey, ea, eb = ENGINE
    nozzle = ellipse(ex, ey, ea, eb)
    obj = relief("engine", nozzle, 0.5, fire[0], base=top, profile=round_profile(1.1, 0.75, 4), inner=1,
                 spacing=0.35)
    hot = ellipse(ex, ey - 0.3, ea * 0.55, eb * 0.55)
    paint(obj, lambda xs, ys, zs: -hot(xs, ys), [0.0], fire)
    parts.append(obj)
    return parts


MODELS = {
    "pu_single_shot": (205, single_shot),
    "pu_dual_shot": (207, dual_shot),
    "pu_charge_cannon": (229, charge_cannon),
    "pu_vulcan_shot": (231, vulcan_shot),
    "pu_atom_bombs": (233, atom_bombs),
    "pu_mini_missile": (235, mini_missile),
    "pu_mega_missile": (237, mega_missile),
    "pu_microbomb": (239, microbomb),
    "pu_postit_mine": (241, postit_mine),
    "pu_dragonwing": (281, dragonwing),
}


# --- Building ----------------------------------------------------------------------------------------------------

ORB_SPRITES = {13: [153, 155, 157, 159, 161, 163, 165, 167, 201, 203, 267, 269],
               4: [169, 191, 193, 195, 197, 199, 243, 245],
               2: [205, 207, 229, 231, 233, 235, 237, 239, 241, 281]}


def symbol_mask(opts, sprite):
    """The symbol's pixels: those not in the orb's ramp, and the orb ramp's darkest shades where the orb's picture
    (each pixel's most common shade over the sheet's thirty orbs) is lighter (the symbol's dark outline)."""
    sys.path.insert(0, os.path.join(HERE, "..", ".."))
    from sprite_profile import sprite_indices
    sheet = front.sheet_path(opts)
    picture = collections.defaultdict(list)
    for ramp, sprites in ORB_SPRITES.items():
        for n in sprites:
            for y, row in enumerate(sprite_indices(sheet, n)):
                for x, v in enumerate(row):
                    if v is not None and v >> 4 == ramp:
                        picture[(x, y)].append(v & 15)
    orb = {key: collections.Counter(shades).most_common(1)[0][0] for key, shades in picture.items()}
    rows = sprite_indices(sheet, sprite)
    return [[v is not None and (v >> 4 != ORB_RAMP or (v & 15 <= 1 < orb.get((x, y), 0))) for x, v in enumerate(row)]
            for y, row in enumerate(rows)]


def check_symbol(opts, name, sprite, objects):
    """The symbol's own silhouette as the game's camera sees it against the symbol's pixels."""
    if "check" not in opts:
        return None
    return kit.compare("%s (powerups %d): the symbol as the game's camera sees it" % (name, sprite),
                       kit.coverage(objects, 24, 28), symbol_mask(opts, sprite))


def build_model(name):
    """The model's parts in view space (the orb first)."""
    sprite, symbol = MODELS[name]
    k.reset()
    parts = [front.orb(ORB_RAMP)] + symbol()
    for obj in parts:
        kit.drop_unused_materials(obj)
    return sprite, parts


def build():
    opts = kit.options()
    for name in MODELS:
        if not kit.wanted(opts, name):
            continue
        sprite, parts = build_model(name)
        front.triangulate(parts)
        front.check_view(opts, name, sprite, parts)
        check_symbol(opts, name, sprite, parts[1:])
        front.to_world(parts)
        front.check_top(opts, name, sprite, parts)
        bpy.context.scene.view_settings.view_transform = "Standard"
        kit.report(name, parts, os.path.join(kit.outdir(opts), name + ".glb"))
        if "preview" in opts:
            kit.preview(opts["preview"] + name, parts, (24, 28), scale=16, distance=0.6)


if __name__ == "__main__":
    build()
