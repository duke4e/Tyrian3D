"""The small red ember that BRAINIAC's brain and NOSE DRIP's face launch (sheet 5 sprite 19, 1x1: an 11 x 11 blob in the
12 x 14 cell; its animation 19 19 19 19 38 38 cycles (animate 1): 38 is the blob a little narrower and a pixel lower,
a hot spot moving across it), polished (2026-10-22, round 37; it had no model: the game drew it as the sprite with
volume). The enemies 640 (BRAINIAC's brain pieces 631 633 636 637 639 launch it from t7050, every 100 ticks, event
31; COLLECTOR's brain the same) and 791 (NOSE DRIP's tongue, 793, while it is out, every tick for about ten, t1178,
1278, 1350; the boss's blob, 790, every 120 ticks from t5150) are one frame set, homing on the player (xaccel and
yaccel 94), armour 5-6, no damaged look; no other enemy shows 5 19 or 38 (catalog.json misses both launched enemies),
and no other sprite has their pixels (mirrored or in other ramps). They fly on their launchers' layer, the top one.

As the sprites draw it (palette ramp 7, the fire's, 0x70-0x75 its dark reds, a hot spot 0x79-0x7b at its upper left
in 19, 0x78-0x79 a pixel lower and to the right in 38, a black outline 0x01): a lumpy dark-red ember glowing at one
side, as a coal does.

The model: a lumpy ball (RADII, its lumps LUMPS, seeded) lofted from explicit rings (the same every run), painted for
the game's camera (each face the heat of the sprite's pixel where the camera sees it: its picture point is
(x, y + z tan 20), polish_dark_orb.py's VIEW_TILT way) in polish_drip.py's bands of the fire (each band glowing in its
own colour, 0.08-0.55, cooler where the ball turns away from the camera: the outline), the hottest parts swelling a
little. The frame model red_ember_38 is the same ball in 38's place and width with 38's heat; both have the same
height (the game centres sky and top objects in height: the same bounds in z).

Origin at the sprite's centre (pixel 6, 7); +Y up the screen, +Z towards the camera; column c's middle is x = c - 5.5,
row r's y = 6.5 - r.

models.cfg (new): model red_ember enemies/red_ember.glb, model red_ember_38 enemies/red_ember_38.glb,
sprite 5 19 red_ember yaw=0 glow=8:0.2, frame 5 38 red_ember_38.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes against
enemy_5.png), --preview <prefix>, --only <name,...>.
"""
import math
import os
import random
import sys

import bpy
import numpy as np
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
import polish_gyges_wall as gw  # noqa: E402  (blur, fill)
from polish_drip import BANDS, FACING, HEAT  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402

TAN_T = math.tan(math.radians(20.0))
# model, sprite, the blob's middle (x, y), its radii (x, y, z), its lean (its lower part this much further left per
# pixel down: the sprites' blobs narrow down to the lower left)
MODELS = [("red_ember", 19, (-0.6, 1.4), (4.85, 4.75, 4.4), 0.2),
          ("red_ember_38", 38, (-0.6, 0.4), (4.05, 4.85, 4.4), 0.12)]
Z_RANGE = (-4.4, 5.0)            # both frames' heights mapped onto this (the game centres them in height: same bounds)
LUMPS = (7, 0.55, 0.14)          # how many, their width (radians on the ball), their height (of the radius)
RINGS, AROUND = 26, 52
SWELL, SWELL_FROM = 0.25, 8.0    # the hottest parts swell out by up to SWELL (polish_drip's way)
OUTLINE = 0.25                   # the ball's rim (its normal towards the camera below this): the outline's dark red


def heat_field(sprite, sheets=None):
    """The sprite's shades (ramp 7; its black outline as shade 0), smoothed, as a sampler of (x, y)."""
    rows = PIXELS[sprite]
    a = np.array([[-1 if t == ".." else int(t, 16) for t in (line[2 * c:2 * c + 2] for c in range(12))]
                  for line in rows.split()])
    shade = np.where(a >> 4 == 7, a & 15, 0).astype(float)
    known = a >= 0
    soft = gw.blur(gw.fill(shade, known), 0.5)
    h, w = soft.shape

    def sample(x, y):
        c = min(max(x + 5.5, 0.0), w - 1.001)
        r = min(max(6.5 - y, 0.0), h - 1.001)
        c0, r0 = int(c), int(r)
        fc, fr = c - c0, r - r0
        return ((soft[r0, c0] * (1 - fc) + soft[r0, c0 + 1] * fc) * (1 - fr) +
                (soft[r0 + 1, c0] * (1 - fc) + soft[r0 + 1, c0 + 1] * fc) * fr)
    return sample


def band_material(index, glow):
    return k.material("drip_%02x" % index, palette=index, metallic=0.0,
                      roughness=0.4 if index < 0x74 else 0.3 if index < 0x78 else 0.24,
                      emission=k.level_palette()[index], emission_strength=glow)


def ember(name, sprite, centre, radii, lean):
    rng = random.Random(1937)
    lumps = []
    for _ in range(LUMPS[0]):
        d = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-0.3, 1))).normalized()
        lumps.append((d, rng.uniform(0.6, 1.0)))
    heat = heat_field(sprite)
    cx, cy = centre
    rx, ry, rz = radii

    def point(theta, phi):
        d = Vector((math.sin(theta) * math.cos(phi), math.sin(theta) * math.sin(phi), math.cos(theta)))
        bump = sum(h * math.exp(-((d - ld).length / LUMPS[1]) ** 2) for ld, h in lumps)
        s = 1.0 + LUMPS[2] * bump
        x, y = rx * d.x * s, ry * d.y * s
        return Vector((cx + x + lean * y, cy + y, rz * d.z * s))

    rings = [[point(math.pi * i / RINGS, 2 * math.pi * j / AROUND) for j in range(AROUND)] for i in range(1, RINGS)]
    obj = k.loft(name, rings, None, start_point=point(0.0, 0.0), end_point=point(math.pi, 0.0))
    # Paint: each face the heat where the camera sees it, banded (polish_drip's bands, facing, swell).
    mesh = obj.data
    borders = [lowest for lowest, _, _ in BANDS[1:]]
    keys = []
    for poly in mesh.polygons:
        c = poly.center
        n = Vector((round(poly.normal.x, 4), round(poly.normal.y, 4), round(poly.normal.z, 4)))
        seen_z = Vector((0.0, -math.sin(math.radians(20.0)), math.cos(math.radians(20.0)))).dot(n)
        value = HEAT[0] * heat(c.x, c.y + c.z * TAN_T) + HEAT[1] + FACING[0] * (n.z - FACING[1])
        band = int(sum(value > t for t in borders))
        if seen_z < OUTLINE:
            band = 0
        keys.append(band)
    used = sorted(set(keys))
    mesh.materials.clear()
    for b in used:
        mesh.materials.append(band_material(BANDS[b][1], BANDS[b][2]))
    mesh.polygons.foreach_set("material_index", [used.index(b) for b in keys])
    # The hottest parts swell a little (along the vertex normals, by the heat of the faces round them).
    hot = {}
    for poly, b in zip(mesh.polygons, keys):
        for v in poly.vertices:
            hot[v] = max(hot.get(v, 0), b)
    top = len(BANDS) - 1
    for v in mesh.vertices:
        t = max(0.0, (hot.get(v.index, 0) - (top - 2)) / 2.0)
        v.co = v.co + Vector((round(v.normal.x, 4), round(v.normal.y, 4), round(v.normal.z, 4))) * SWELL * t
    zs = [v.co.z for v in mesh.vertices]
    z0, z1 = min(zs), max(zs)
    for v in mesh.vertices:
        v.co.z = Z_RANGE[0] + (v.co.z - z0) * (Z_RANGE[1] - Z_RANGE[0]) / (z1 - z0)
    mesh.update()
    k.recalc_normals(obj)
    k.smooth(obj, 70)
    return obj


def build():
    options = k.args()
    out = mk.outdir(options)
    only = set(options["only"].split(",")) if "only" in options else None
    for name, sprite, centre, radii, lean in MODELS:
        if only is not None and name not in only:
            continue
        k.reset()
        obj = ember(name, sprite, centre, radii, lean)
        triangulate([obj])
        bpy.context.scene.view_settings.view_transform = "Standard"
        mk.report(name, [obj], os.path.join(out, name + ".glb"))
        if "check" in options:
            sheets = options["check"]
            k.check_silhouette(os.path.join(sheets, "enemy_5.png") if os.path.isdir(sheets) else sheets, [sprite],
                               False)
        if "preview" in options:
            mk.preview(options["preview"] + name, [obj], size=(12, 14), scale=24, distance=0.5)


# --- The sprites' pixels ------------------------------------------------------------------------------------------------
# Each pixel its palette index as two hex digits ('..' none), the cell's 14 rows.

PIXELS = {
    19: """
........01707001........
......017272727001......
....7074757373727001....
..71757b79727473720101..
0173757676727373727101..
7073757271707472727270..
01737575727373727370....
017274757473727271......
..71747473727270........
..017171717170..........
....01707070............
........................
........................
........................
""",
    38: """
........................
......01017101..........
....017274747270........
..0172787671747170......
..017479777274717201....
..717573747274727470....
..727572727073727470....
..727575727372717370....
..7074757473717301......
..01727473727201........
....7071717101..........
....01707070............
........................
........................
""",
}


if __name__ == "__main__":
    build()
