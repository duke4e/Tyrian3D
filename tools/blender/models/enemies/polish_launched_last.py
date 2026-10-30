"""The last launched shots that had no model (enemies the player can shoot, made by their launchers; the game drew them
as their sprites with volume: no generator made models of these sprites and models.cfg had no lines for them),
polished (2026-10-22, round 34; nothing replaced). Both come from ground enemies, so they fly on the ground2 layer
(drawn on the ground enemies' layer, height 4: the game centres them in height there).

- fruit_ember, fruit_ember_96, fruit_ember_115 (sheet ' (x27) sprites 77 96 115, 1x1; episode 5's enemy 1262, armour 6,
  launched every 30 game frames by FRUIT's orb in its cup (% 233, enemy 1251, fruit_hex_eye; four of them, ground events
  at t2708, 3324, 3716 and 6320) and aimed at the player at launch, speed 4 (1262's elaunchtype 4 with no launch of its
  own: tyrian2.c aims a launched enemy whose launchtype is under 90)). The sprite: a ball of the fire ramp 7, 6 pixels
  across (columns 3-8 of rows 4-9, the corners cut), its rim dark red (0x71-0x73), its body 0x74-0x76, hottest at its
  upper right (0x77-0x79 at columns 6-7 of rows 5-6). Its animation 77 77 96 96 115 115 96 96 is the same ball two and
  three shades hotter (every pixel's index + 2, + 3): it pulses. A frame model each (no other enemy shows these sprites,
  launched ones included; no other sprite is their pixels mirrored, turned or in other ramps), the same mesh, its bands
  two and three shades hotter and glowing more. Built as FRUIT's vent pods' green grape is (polish_launched_fruit.py:
  polish_grape_wing.grape()'s painting on a painted icosphere, the rim darker where the slanted camera sees it edge-on),
  in fire: a glowing ember of the orb that shoots it, its hot spot where the sprite draws it (EMBER_HOT, as the camera
  sees the ball) in rings of heat (EMBER_RINGS), every band glowing in its own colour (0.2-0.4 in 77, up to 0.3-0.58
  in 115).

- slot_rocket, slot_rocket_38, slot_rocket_57, slot_rocket_76 (sheet P sprites 19 38 57 76, 1x1; episode 1's enemy 458,
  armour 5, launched every 20 game frames by ASTEROID?'s small block with its lid open over a dark well (P 53, enemy
  457, block_slot; ground events at t384 and t552) and flying down the screen (0, 3), nose first). The sprite (columns
  3-9 of rows 0-13, its axis column 6): a small missile in a dark outline (0x20): a grey warhead (rows 10-12, its point
  at row 13), a tan casing (rows 5-9, ramp 1, a light stripe down its middle), a grey tail (rows 1-4) between two slate
  fins (columns 4 and 8, ramp 6) and its nozzle at the top, where its exhaust burns: 19 a dark red spark (0x73), 38 a
  red flame (0x78 in a 0x74 sheath), 57 and 76 hotter (0x79 / 0x7a in red tongues either side, 0x71-0x76) with the
  nozzle's mouth glowing grey-white (0x0c, 0x0e). Its animation 19 19 38 38 57 57 76 76 57 57 38 38: the exhaust
  flickering. P 95, 114, 133 and 152 are the same picture with the casing in ramp 2 (green; thought unused, but
  ASTEROID? shows them, the sweep of every level found it on 2026-10-30): slot_rocket_green and its frames. Built in
  the white dart's family (polish_launched_darts.py: a turned body painted by its normals, cruciform fins with rounded
  rims, its fin()): the warhead an ogive with a dark seam where it meets the casing, the casing a shade wider, the tail
  narrower, four fins (the two the sprite draws flat either side, two smaller ones upright above and below, not to hide
  the exhaust from the camera), the nozzle
  a dark-mouthed can, the exhaust a glowing cone of fire from the nozzle up the screen (hot where it faces the camera
  and near the nozzle, red down its sides and at its tip) whose length, width, colours and glow rise with the frames (ROCKET_FLAMES; the frame models, the rest of the mesh the same, their bounds in height the same).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; origin at the
sprite's centre (a 1x1 sprite's pixel 6, 7: column c is x = c + 0.5 - 6, row r is y = 6.5 - r). The game centres these
models in height. Every mesh is triangulated (polish_k_pod.triangulate: the same output with and without --check) and a
model's parts joined; no random numbers, no booleans.

models.cfg (new): model fruit_ember (and fruit_ember_96, _115) enemies/fruit_ember*.glb, sprite x27 77 fruit_ember yaw=0
glow=8:0.25, frame x27 96 fruit_ember_96, frame x27 115 fruit_ember_115; model slot_rocket (and slot_rocket_38, _57,
_76) enemies/slot_rocket*.glb, sprite p 19 slot_rocket yaw=0 glow=6:0.2:120:0.5:-6 (the exhaust, 6 pixels up the
screen), frame p 38 slot_rocket_38, frame p 57 slot_rocket_57, frame p 76 slot_rocket_76.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each model's silhouette
against its frame), --preview <prefix>, --only <name,...>.
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
from polish_balls import Ellipsoid, painted_ball  # noqa: E402
from polish_deli_boss import join  # noqa: E402
from polish_grape_wing import SUN, TOWARDS_VIEW  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_launched_darts import fin, plain  # noqa: E402
from polish_launched_flames import lit, vertex_normals  # noqa: E402
from polish_orb_red import band_split  # noqa: E402
from polish_sphere_nozzle import smoothstep  # noqa: E402

TAN_T = math.tan(math.radians(20.0))


# --- ' 77: the ember FRUIT's orbs shoot ------------------------------------------------------------------------------

EMBER_C = (0.0, 0.0, 0.0)          # the ball's middle (columns 3-8 of rows 4-9)
EMBER_R = (3.0, 3.0, 2.75)
EMBER_HOT = (0.75, 0.75, 1.25)     # its hot spot as the camera sees it (x, y over the middle) and its radius
EMBER_RIM = 0.32                   # the rim, where the camera sees the surface edge-on
# Per frame: (palette index, glow) for the rim, the body and three rings in to the hot spot: the sprite's shades, two
# and three up the ramp in 96 and 115.
EMBER_FRAMES = {
    77: ((0x72, 0.2), (0x74, 0.24), (0x76, 0.28), (0x77, 0.32), (0x79, 0.4)),
    96: ((0x74, 0.26), (0x76, 0.3), (0x78, 0.34), (0x79, 0.4), (0x7b, 0.48)),
    115: ((0x75, 0.3), (0x77, 0.34), (0x79, 0.4), (0x7a, 0.46), (0x7c, 0.58)),
}
EMBER_RINGS = (-1.0, -0.45, 0.15)  # the heat's borders between the body, its rings and the hot spot


def ember(name, frame):
    """polish_grape_wing.grape()'s painting (the rim darker as the slanted camera sees it) on a fine icosphere, its hot
    spot at the upper right as the camera sees the ball (EMBER_HOT: where the sprite draws it)."""
    (rim, rim_g), (body, body_g), (glow, glow_g), (warm, warm_g), (hot, hot_g) = EMBER_FRAMES[frame]
    m = {"rim": lit(f"ember{frame}_rim", rim, rim_g, roughness=0.32),
         "body": lit(f"ember{frame}_body", body, body_g, roughness=0.28),
         "glow": lit(f"ember{frame}_glow", glow, glow_g, roughness=0.26),
         "warm": lit(f"ember{frame}_warm", warm, warm_g, roughness=0.25),
         "hot": lit(f"ember{frame}_hot", hot, hot_g, roughness=0.22)}
    hx, hy, hr = EMBER_HOT

    def heat(p, n):
        # how far from the hot spot the camera sees the point (the camera's view: y + z tan 20), facing it
        seen = Vector((p.x - hx, p.y + p.z * TAN_T - hy))
        return (1.0 - seen.length / hr) if n.dot(TOWARDS_VIEW) > 0.2 else -9.0
    paint = [(lambda p, n: n.dot(TOWARDS_VIEW), (EMBER_RIM,), ("rim", "body")),
             (heat, EMBER_RINGS, (None, "glow", "warm", "hot"))]
    return [painted_ball(name, Ellipsoid(EMBER_C, EMBER_R), paint, m, subdivisions=3, smooth_angle=80)]


# --- P 19: the rocket from ASTEROID?'s small block -------------------------------------------------------------------

ROCKET_X = 0.5            # its axis: the sprite's column 6
# The body in four turned parts, each a profile (y, radius) up the screen: the warhead (from its point), the dark seam
# where it meets the casing, the tan casing (a shade wider), the grey tail (narrower) up to the nozzle.
ROCKET_PARTS = [
    ("warhead", "grey", [(-6.95, 0.0), (-6.75, 0.6), (-6.4, 1.15), (-5.8, 1.62), (-5.0, 1.98), (-4.2, 2.12),
                         (-3.15, 2.15)]),
    ("seam", "dark", [(-3.2, 2.0), (-2.9, 2.0)]),
    ("casing", "casing", [(-3.0, 2.2), (-2.0, 2.2), (-0.5, 2.2), (1.0, 2.2), (2.0, 2.2)]),
    ("tail", "grey", [(1.9, 1.82), (3.2, 1.82), (4.4, 1.82), (5.45, 1.7)]),
]
ROCKET_NOZZLE = (5.3, 6.15, 1.25)     # from y, to y, radius
# The fins (x out from the axis, y): the two the sprite draws flat either side (columns 4 and 8 of rows 1-4, two thirds
# into the outline); the upright ones above and below FIN_UPRIGHT of their span.
ROCKET_FIN = [(1.6, 6.5), (3.0, 6.35), (3.25, 6.0), (3.25, 2.4), (2.95, 1.8), (1.6, 1.3)]
FIN_UPRIGHT = 0.55
ROCKET = {"casing": 0x17, "casing_lit": 0x1a, "casing_dark": 0x14, "grey": 0x08, "grey_lit": 0x0b, "grey_dark": 0x05,
          "fin": 0x67, "fin_edge": 0x65, "dark": 0x20, "nozzle": 0x07}
# Per frame: the exhaust's length (pixels up the screen from the nozzle's mouth), radius, its core and sheath (palette
# index, glow), and the nozzle mouth's own glow (palette index, glow; None: dark).
ROCKET_FLAMES = {
    19: (1.0, 0.6, (0x73, 0.32), (0x71, 0.22), None),
    38: (1.7, 0.85, (0x78, 0.42), (0x74, 0.3), None),
    57: (2.3, 1.25, (0x79, 0.5), (0x72, 0.34), (0x0c, 0.32)),
    76: (2.7, 1.45, (0x7a, 0.58), (0x73, 0.38), (0x0e, 0.42)),
}


def rocket(name, frame, casing=0):
    """casing: added to the casing's palette indices (0x10: the green twin, ramp 2 for ramp 1)."""
    m = {key: plain(f"rocket_{key}", index + (casing if key.startswith("casing") else 0),
                    metallic=0.3 if key not in ("dark",) else 0.1,
                    roughness=0.34 if key != "dark" else 0.5) for key, index in ROCKET.items()}
    length, radius, (core_i, core_g), (sheath_i, sheath_g), mouth = ROCKET_FLAMES[frame]
    core = lit(f"rocket{frame}_core", core_i, core_g, roughness=0.3)
    sheath = lit(f"rocket{frame}_sheath", sheath_i, sheath_g, roughness=0.32)
    objects = []
    # The body, turned about its axis in parts, painted by their normals (the light they get): grey, tan, the seam dark.
    tones = {"grey": [(-99.0, m["grey_dark"]), (0.35, m["grey"]), (0.78, m["grey_lit"])],
             "casing": [(-99.0, m["casing_dark"]), (0.35, m["casing"]), (0.78, m["casing_lit"])],
             "dark": [(-99.0, m["dark"])]}
    for part, tone, prof in ROCKET_PARTS:
        obj = k.lathe(part, [(prof[0][0], 0.0)] + prof + [(prof[-1][0], 0.0)], None, 24, axis_x=ROCKET_X)
        values = [0.65 * n.z + 0.35 * max(0.0, n.dot(SUN)) for n in vertex_normals(obj)]
        band_split(obj, values, tones[tone])
        k.smooth(obj, 60)
        objects.append(obj)
    # The nozzle: a can with a dark mouth (glowing in the hot frames).
    y0, y1, nr = ROCKET_NOZZLE
    mouth_mat = m["dark"] if mouth is None else lit(f"rocket{frame}_mouth", mouth[0], mouth[1], roughness=0.3)
    can = k.lathe("nozzle", [(y0, 0.0), (y0, nr), (y1 - 0.15, nr * 1.04), (y1, nr - 0.1), (y1 - 0.08, nr - 0.3),
                             (y1 - 0.45, nr - 0.32), (y1 - 0.45, 0.0)], m["nozzle"], 20, axis_x=ROCKET_X)
    k.smooth(can, 50)
    mouth_disc = k.lathe("mouth", [(y1 - 0.43, 0.0), (y1 - 0.43, nr - 0.31), (y1 - 0.4, nr - 0.31), (y1 - 0.4, 0.0)],
                         mouth_mat, 20, axis_x=ROCKET_X)
    objects += [can, mouth_disc]
    # The exhaust: a cone of fire up the screen from the mouth, hot (the core's colour) where it faces the camera and
    # near the nozzle, the sheath's red down its sides and towards its tip.
    prof = [(y1 - 0.35, 0.0), (y1 - 0.35, radius * 0.9), (y1 + 0.2 * length, radius), (y1 + 0.55 * length, radius * 0.72),
            (y1 + 0.85 * length, radius * 0.32), (y1 + length, 0.0)]
    flame = k.lathe("flame", prof, sheath, 16, axis_x=ROCKET_X)
    values = [0.6 * n.z + 0.5 * (1.0 - min(1.0, max(0.0, (v.co.y - y1) / length)))
              for v, n in zip(flame.data.vertices, vertex_normals(flame))]
    band_split(flame, values, [(-99.0, sheath), (0.62, core)])
    k.smooth(flame, 70)
    objects.append(flame)
    # The fins: either side flat (the sprite's), above and below upright and smaller.
    for side in (-1, 1):
        objects.append(fin(f"fin{'lr'[side > 0]}", [(side * x, y) for x, y in ROCKET_FIN], ROCKET_X, m["fin"],
                           m["fin_edge"]))
    for up in (-1, 1):
        f = fin(f"fin{'du'[up > 0]}", [(x * FIN_UPRIGHT, y) for x, y in ROCKET_FIN], 0.0, m["fin"], m["fin_edge"])
        f.data.transform(Matrix.Translation((ROCKET_X, 0, 0)) @ Matrix.Rotation(math.radians(-90 * up), 4, "Y"))
        objects.append(f)
    return objects


# --- Build ------------------------------------------------------------------------------------------------------------

MODELS = [
    # name, sheet file, sprite (for the check), 2x2, make
    ("fruit_ember", "enemy_x27", 77, False, lambda name: ember(name, 77)),
    ("fruit_ember_96", "enemy_x27", 96, False, lambda name: ember(name, 96)),
    ("fruit_ember_115", "enemy_x27", 115, False, lambda name: ember(name, 115)),
    ("slot_rocket", "enemy_P", 19, False, lambda name: rocket(name, 19)),
    ("slot_rocket_38", "enemy_P", 38, False, lambda name: rocket(name, 38)),
    ("slot_rocket_57", "enemy_P", 57, False, lambda name: rocket(name, 57)),
    ("slot_rocket_76", "enemy_P", 76, False, lambda name: rocket(name, 76)),
    # The green twin (P 95 and its frames 114 133 152: the same pixels with the casing in ramp 2), found by the sweep
    # of every level (2026-10-30: ASTEROID?).
    ("slot_rocket_green", "enemy_P", 95, False, lambda name: rocket(name, 19, casing=0x10)),
    ("slot_rocket_green_114", "enemy_P", 114, False, lambda name: rocket(name, 38, casing=0x10)),
    ("slot_rocket_green_133", "enemy_P", 133, False, lambda name: rocket(name, 57, casing=0x10)),
    ("slot_rocket_green_152", "enemy_P", 152, False, lambda name: rocket(name, 76, casing=0x10)),
]


def build():
    options = k.args()
    only = set(options["only"].split(",")) if "only" in options else None
    for name, sheet, sprite, large, make in MODELS:
        if only is not None and name not in only:
            continue
        k.reset()
        objects = make(name)
        triangulate(objects)
        objects = [join(objects, name)] if len(objects) > 1 else objects
        bpy.context.view_layer.update()
        if "check" in options:
            w, h = (24, 28) if large else (12, 14)
            seen = []
            for obj in objects:   # the camera's view: points moved up the screen by their height (y + z tan 20)
                copy = obj.copy()
                copy.data = obj.data.copy()
                bpy.context.scene.collection.objects.link(copy)
                for v in copy.data.vertices:
                    v.co.y += v.co.z * TAN_T
                seen.append(copy)
            bpy.context.view_layer.update()
            mk.compare("%s (%s %d) in the camera's view" % (name, sheet, sprite), mk.coverage(seen, w, h),
                       k.sprite_mask(os.path.join(options["check"], sheet + ".png"), sprite, large=large))
            mk.compare("%s (%s %d) from straight above" % (name, sheet, sprite), mk.coverage(objects, w, h),
                       k.sprite_mask(os.path.join(options["check"], sheet + ".png"), sprite, large=large))
            for copy in seen:
                mesh = copy.data
                bpy.data.objects.remove(copy)
                bpy.data.meshes.remove(mesh)
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        mk.report(name, objects, os.path.join(mk.outdir(options), name + ".glb"))
        if "preview" in options:
            size = (24, 28) if large else (12, 14)
            mk.preview(options["preview"] + name, objects, size=size, scale=16 if large else 32,
                       distance=0.75 if large else 0.42)


if __name__ == "__main__":
    build()
