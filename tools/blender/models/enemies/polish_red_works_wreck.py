"""The wreck of TYRIAN's red works in the rocks (sheet 2: 15, 17 above 53, 55; their stand-ins: what TYRIAN's
background 3 map ad33fadb8ad32f83 paints where the works ride, before they come and once they are destroyed, at 444..468,
9927..9955), built on polish_red_works.py (2026-10-25, the clean ground's stage 5: the top enemies riding background 3).
models.cfg: model red_works_tl_wreck / _tr_wreck / _bl_wreck / _br_wreck enemies/red_works_*_wreck.glb origin;
wreck 2 15 red_works_tl_wreck, wreck 2 17 red_works_tr_wreck, wreck 2 53 red_works_bl_wreck, wreck 2 55
red_works_br_wreck (drawn with the live sprite lines' options: yaw=0 height=-6).

As the map paints it (background 3's tiles 161 162 above 171 172 at 4x in the HD tiles; it lies a row higher up the
screen than the sprites, PAINT_DY; the works' coordinates below are the painting's, x = column - 24, y = 28 - row): the
works burnt out, the deck black (0x01) all over; the top row standing but dark: the drum (its red caps kept), the rail
panel black with its tan rail darker and its brass collars, the knob grey; the big red arm at the upper left and the red
block at the upper right still red (0x44-0x4b), the arm's lower right end burnt; the tan rods beside the red block and
at the right edge darker tan, the upper one whole, the right one only down to y 1; the pipe's run from x -1 to the
right edge and down the right side to y 2 left (its left part and its branch gone); the grilles gone to black holes
(the upper box's rim left), the tan box blown out to its rim (a tan strip along its top and left side) and its brass
strip, a broken piece of its brass rail; the dark box gone but for its tan panel's upper half, burnt dark brown (0x12,
0x13), and three grey slats; twisted grey metal across the black middle; at the lower left the tall tan block (0xa3-0xa5
lit brass) and the red wedge (0x43) standing, the small red block burnt with a dull ember (0x70); everything else gone,
and the deck's lower right blown away to the rubble of the cobbles (x 0..14, y -4..-22).

The model: polish_red_works.py's parts (its build_whole(), its materials), moved up PAINT_DY, then broken: the parts the
painting does not show taken away, the pipe, the rails, the right rod and the tan panel cut where the painting ends
them (plane cuts closed in the part's own material), the deck rebuilt over the painting's outline (its lower right a
jagged broken edge), black; the parts that stand scorched by noise fields along their contours (polish_bronze_pump_
wreck.scorch_map: each step one of the works' own darker shades, or the brown-black 0x10), the tan box's rim, twisted
bars, charred chunks and torn deck plates added, grey rubble at the lower right, two dull embers (0x72 at 0.24, 0x75 at
0.3: under the bloom's white). Then cut along the sprites' edges, sheared along the camera's line of sight, moved to
each sprite's middle, triangulated and joined exactly as the live pieces (polish_red_works.build()'s steps).

Coordinates as polish_red_works.py's: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera (z 0:
background 3's plane, with height=-6); the whole's origin the picture's middle.

Options after "--": --outdir <dir> (default assets/models/enemies), --preview <prefix>, --only <name,...>,
--whole <file.glb> (the uncut wreck, unsheared, for looking at).
"""
import math
import os
import random
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
import polish_red_works as rw  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_deli_boss import join, drop_unused  # noqa: E402
from polish_coral_manta import cut  # noqa: E402
from polish_fleet_walker import shear_to_camera, merge_materials  # noqa: E402
import polish_panel_pills_wreck as wk  # noqa: E402
from polish_jaw_gun_wreck import bent_bar, ccw, ember, ember_material, grid_cut, rock  # noqa: E402
from polish_bronze_pump_wreck import scorch_map  # noqa: E402
from polish_pyramid_wreck import chunk  # noqa: E402

PAINT_DY = 1.0                 # the painting lies this much higher up the screen than the live sprites
SEED = 15
# The parts the painting does not show (polish_red_works.py's object names).
GONE = ("red_under_l", "red_under_r", "grey_under", "grey_ur", "grey_box_left", "grey_low_a", "grey_low_b",
        "slat_low_a", "slat_low_b", "grille_0", "grille_1", "grille_bar_0", "grille_bar_1", "grille_box_1",
        "pipe_branch", "pipe_flange", "pipe_flange_b", "tan_box", "tan_socket", "button", "dark_box", "lid",
        "lid_knob", "slat_3", "red_valve", "brass_bar", "rod_low", "ledge", "floor_plate", "floor_plate_b", "red_bar",
        "red_bar_slot", "red_bar_rod", "valve", "rod_ur_clip_b", "deck")
# The parts cut where the painting ends them: (name, a point of the plane, its normal: the side it points to goes).
CUTS = [("pipe_main", (-1.2, 0.0, 0.0), (-1.0, 0.12, 0.0)), ("pipe_main", (0.0, 2.0, 0.0), (0.1, -1.0, 0.0)),
        ("brass_rail", (-18.0, 0.0, 0.0), (-1.0, -0.1, 0.0)), ("rod_right", (0.0, 1.2, 0.0), (0.05, -1.0, 0.0)),
        ("tan_panel", (0.0, 4.6, 0.0), (0.12, -1.0, 0.0)), ("rail_lip", (-5.6, 0.0, 0.0), (-1.0, 0.0, 0.0))]
# How burnt each standing part is (its base level; the noise adds about +-0.25): levels 0.3 and 0.75 are one and two
# steps darker.
BURN = {"drum": 0.45, "drum_cradle": 0.8, "drum_cap": 0.2, "rail_panel": 1.2, "rail": 0.5, "rail_collar": -1.0,
        "rail_lip": 0.55, "knob_foot": 0.9, "knob": 0.3, "red_arm": 0.12, "red_arm_low": 0.22, "red_ur": 0.18,
        "red_small": 0.8, "grey_beside": 0.4, "grille_box_0": 1.3, "pipe_main": 0.18, "brass_strip": 0.05,
        "brass_rail": 0.45, "tan_panel": 1.3, "slat": 0.6, "rod_ur_clip": 0.8, "rod_ur": 0.5, "rod_right": 0.55,
        "tan_tall": 0.36, "red_wedge": 0.4}
LEVELS = (0.3, 0.75)
# The red arm's lower right end burnt (centre, radii of the burn).
ARM_BURN = ((-10.5, 15.0), (4.5, 3.6))
# The deck over the painting's outline (x, y), its broken edge (from the right side down to the bottom) roughened.
DECK_TOP, DECK_BEVEL = rw.DECK_TOP, rw.DECK_BEVEL
DECK_EDGE = [(14.5, 24.5), (14.5, -3.2)]
DECK_BUCKLE = 0.32
# Where the deck sank under the parts burnt away: centre, radii, depth.
DECK_DIPS = [((-7.6, 9.4), (3.0, 2.4), 0.45), ((-18.6, 7.0), (3.2, 4.0), 0.5), ((-8.6, 3.4), (3.6, 3.0), 0.5),
             ((2.8, 3.0), (3.0, 2.4), 0.45), ((-8.4, -7.0), (3.0, 2.6), 0.45), ((6.6, -2.8), (3.0, 2.2), 0.5)]
DECK_BROKEN = [(14.5, -3.2), (11.0, -4.6), (9.4, -6.3), (7.0, -7.4), (5.2, -9.2), (2.6, -9.7), (0.7, -11.2),
               (0.4, -13.8), (-0.4, -15.6), (-0.6, -18.2), (-1.5, -19.6), (-6.0, -20.4), (-8.0, -22.0), (-14.0, -22.0),
               (-16.6, -20.4), (-17.6, -18.0)]
DECK_REST = [(-17.6, -18.0), (-17.2, -8.0), (-19.0, -6.4), (-23.5, -6.0), (-23.5, -0.4), (-24.0, -0.4), (-24.0, 13.5),
             (-21.2, 13.5), (-21.2, 22.0), (-19.6, 22.0), (-19.6, 27.0), (-10.0, 27.0), (-10.0, 25.5), (6.0, 25.5),
             (6.0, 27.5), (11.0, 27.5), (11.0, 24.5)]
# The tan box's rim left standing (x0, x1, y0, y1, top), tan_dark.
TAN_RIM = [(-23.3, -15.7, 11.8, 13.3, 3.7), (-23.2, -21.8, 2.0, 12.0, 3.4), (-16.5, -15.4, 9.6, 12.2, 3.0)]
# Twisted metal across the black middle: points (x, y, z), radius, material.
BARS = [([(-12.6, 13.4, 1.6), (-11.0, 11.0, 3.0), (-10.2, 8.2, 2.8), (-9.6, 5.0, 1.8)], 0.38, "glint"),
        ([(0.2, 9.4, 1.6), (-1.6, 6.6, 3.2), (-2.2, 3.4, 3.0), (-1.0, 0.0, 2.4), (0.4, -3.4, 1.4)], 0.45, "glint"),
        ([(3.0, 7.6, 2.6), (5.0, 6.4, 3.0), (6.6, 4.2, 2.6), (6.4, 1.8, 1.6)], 0.34, "glint"),
        ([(-18.2, 9.4, 1.6), (-18.0, 5.0, 2.4), (-18.4, 0.0, 1.6)], 0.3, "glint"),
        ([(-8.0, -6.6, 1.4), (-5.6, -5.0, 2.2), (-2.6, -4.6, 1.6)], 0.3, "steel_light"),
        ([(-15.2, 9.4, 1.3), (-14.0, 7.4, 2.0), (-14.6, 4.6, 1.5)], 0.28, "steel_dark")]
# The tan box's face torn off and lying broken in the middle: outline (x, y), z, thickness, tilt, material.
SHARDS = [([(-18.4, 1.6), (-14.6, 1.8), (-14.2, 4.6), (-18.0, 4.4)], 1.4, 0.7, (14.0, -10.0), "tan_dark"),
          ([(-14.4, 2.0), (-12.2, 2.4), (-12.0, 4.0), (-14.0, 3.8)], 1.5, 0.5, (-8.0, 18.0), "brass"),
          ([(-20.2, 1.6), (-18.2, 1.4), (-18.4, -1.6), (-20.4, -1.2)], 1.2, 0.6, (10.0, 6.0), "red_dark")]
# Charred chunks on the deck (x, y, size) and the rubble at the lower right on the ground (x, y, size, material).
CHUNKS = [(-12.6, 2.6, 2.8), (-6.4, 6.4, 2.4), (-3.2, -4.8, 3.0), (2.4, 6.4, 2.2), (-8.6, -7.0, 2.6), (5.8, -2.4, 2.6),
          (-12.0, 14.6, 1.8), (9.0, 7.6, 1.8), (-15.6, -2.4, 2.0), (-4.8, 12.4, 1.6)]
RUBBLE = [(4.6, -12.0, 2.4, "steel_dark"), (8.4, -9.6, 2.0, "steel"), (11.6, -6.6, 1.8, "steel_dark"),
          (2.8, -16.4, 2.2, "steel"), (6.8, -15.0, 1.6, "dark"), (12.2, -11.4, 1.6, "steel"),
          (1.6, -20.6, 1.8, "steel_dark")]
# Torn deck plates lying in the rubble: outline (x, y), z, thickness, tilt (degrees about x and y).
PLATES = [([(3.0, -8.6), (7.2, -7.8), (6.4, -11.0), (2.6, -11.0)], 0.2, 0.5, (8.0, -12.0)),
          ([(9.6, -5.0), (13.6, -4.4), (12.8, -7.6), (10.0, -7.4)], 0.1, 0.45, (-6.0, 10.0))]
# Dull embers: centre, radii, rim and core glow.
EMBERS = [((-19.6, -3.0, 2.6), (1.2, 1.3, 0.5)), ((-7.8, 15.6, 3.8), (0.9, 0.7, 0.3))]


def materials():
    m = rw.materials()
    m["soot"] = k.material("works_soot", palette=0x10, metallic=0.2, roughness=0.8)
    m["red_dark"] = k.material("works_red_burnt", palette=0x44, metallic=0.25, roughness=0.5)
    m["tan_burnt"] = k.material("works_tan_burnt", palette=0xa3, metallic=0.2, roughness=0.6)
    m["brown"] = k.material("works_brown", palette=0x12, metallic=0.2, roughness=0.65)
    m["ember"] = ember_material(0x72, 0.24)
    m["ember_hot"] = ember_material(0x75, 0.3)
    m["char"] = k.material("works_char", palette=0x01, metallic=0.0, roughness=0.95)
    m["glint"] = k.material("works_glint", palette=0x6c, metallic=0.4, roughness=0.3)
    return m


def remap(m):
    """The scorch's steps: material name -> (one step darker, two steps)."""
    steps = {"steel_light": ("steel", "steel_dark"), "steel": ("steel_dark", "dark"), "steel_dark": ("dark", "soot"),
             "knob": ("steel", "steel_dark"), "red": ("red_dark", "soot"), "tan": ("tan_dark", "tan_burnt"),
             "tan_dark": ("tan_burnt", "soot"), "rod": ("tan_dark", "tan_burnt"), "brass": ("tan_burnt", "soot"),
             "deck": ("dark", "soot"), "dark": ("soot", "soot")}
    return {m[a].name: (m[b], m[c]) for a, (b, c) in steps.items()}


def burn_of(name):
    for prefix in sorted(BURN, key=len, reverse=True):
        if name.startswith(prefix):
            return BURN[prefix]
    return 0.4


def field_for(name):
    base = burn_of(name)

    def f(co):
        v = base + 0.25 * wk.fbm(co.x * 0.35 + 3.7, co.y * 0.35 - 1.1, co.z * 0.3, 2)
        if name.startswith("red_arm"):
            (cx, cy), (rx, ry) = ARM_BURN
            d = ((co.x - cx) / rx) ** 2 + ((co.y - cy) / ry) ** 2
            v += 0.9 * math.exp(-1.6 * d)
        return v
    return f


def deck(m):
    """The deck over the painting's outline, its broken edge roughened; black."""
    broken = []
    for (x0, y0), (x1, y1) in zip(DECK_BROKEN, DECK_BROKEN[1:]):
        d = Vector((x1 - x0, y1 - y0))
        n = max(1, int(d.length / 0.7))
        normal = Vector((d.y, -d.x)).normalized()
        for i in range(n):
            t = i / n
            p = Vector((x0, y0)) + d * t
            off = 0.0 if i == 0 else 0.55 * wk.perlin(p.x * 0.8 + 2.3, p.y * 0.8 - 5.1, 0.7)
            broken.append(tuple(p + normal * off))
    outline = DECK_EDGE[:1] + broken + DECK_REST
    obj = mk.prism("wreck_deck", ccw(outline), -0.4, DECK_TOP, m["char"])
    # Buckled by the blast: its top cut into a grid, pushed up and down by noise, sunk where the parts burnt away
    # (never below the standing parts' feet, 0.6).
    grid_cut(obj, 1.4)
    for v in obj.data.vertices:
        if v.co.z > DECK_TOP - 1e-4:
            dz = DECK_BUCKLE * wk.fbm(v.co.x * 0.22 + 1.9, v.co.y * 0.22 - 4.4, 0.3, 3)
            for (cx, cy), (rx, ry), depth in DECK_DIPS:
                dz -= depth * math.exp(-(((v.co.x - cx) / rx) ** 2 + ((v.co.y - cy) / ry) ** 2))
            v.co.z = max(0.68, DECK_TOP + dz)
    obj.data.update()
    return mk.shade(obj, 35)


def tan_rim(m):
    out = []
    for i, (x0, x1, y0, y1, top) in enumerate(TAN_RIM):
        box = mk.box(f"tan_rim{i}", x0, x1, y0, y1, 0.0, top, m["tan_dark"])
        mk.bevel(box, 0.35, 2, 30)
        out.append(mk.shade(box, 40))
    return out


def debris(m):
    rng = random.Random(SEED)
    out = []
    for i, (points, radius, key) in enumerate(BARS):
        out.append(bent_bar(f"twisted{i}", points, radius, m[key], 8))
    for i, (x, y, size) in enumerate(CHUNKS):
        out.append(mk.shade(chunk(f"char_chunk{i}", (x, y, DECK_TOP - 0.2), size, rng, m["soot" if i % 2 else "char"],
                                  0.55), 30))
    for i, (x, y, size, key) in enumerate(RUBBLE):
        out.append(mk.shade(chunk(f"rubble{i}", (x, y, -0.3), size, rng, m[key], 0.5), 30))
    from polish_jaw_gun_wreck import shard
    for i, (outline, z, thick, tilt) in enumerate(PLATES):
        out.append(shard(f"torn_plate{i}", outline, z, thick, m["dark"], tilt))
    for i, (outline, z, thick, tilt, key) in enumerate(SHARDS):
        out.append(shard(f"tan_face{i}", outline, z, thick, m[key], tilt))
    for i, (centre, radii) in enumerate(EMBERS):
        out += ember(f"ember{i}", centre, radii, (m["ember"], m["ember_hot"]), 7.0 + 3.1 * i)
    return out


def build_whole(m):
    """The live works moved up PAINT_DY, broken as the painting shows them."""
    whole = rw.build_whole(m)
    for obj in whole:
        mk.apply(obj)
        obj.data.transform(Matrix.Translation((0.0, PAINT_DY, 0.0)))
    for obj in list(whole):
        if obj.name.split(".")[0] in GONE:
            whole.remove(obj)
            bpy.data.objects.remove(obj)
    for name, co, no in CUTS:
        obj = bpy.data.objects[name]
        cap = obj.data.materials[0]
        gone = wk.split_piece(obj, co, no, cap, name + "_gone")
        if gone is not None:
            bpy.data.objects.remove(gone)
    steps = remap(m)
    for obj in whole:
        name = obj.name.split(".")[0]
        if burn_of(name) < 0:
            continue
        scorch_map(obj, field_for(name), steps, LEVELS, step=1.5)
        mk.shade(obj, 40)
    # The tan panel burnt dark brown, as painted.
    panel = bpy.data.objects["tan_panel"]
    for i, mat in enumerate(panel.data.materials):
        if mat is not None and mat.name in (m["tan_dark"].name, m["tan_burnt"].name):
            panel.data.materials[i] = m["brown"]
    added = [deck(m)] + tan_rim(m) + debris(m)
    for obj in added:
        mk.apply(obj)
    parts = mk.meshes()
    wk.clip_below(parts, -0.4)
    bpy.context.view_layer.update()
    return [o for o in parts if len(o.data.polygons) > 0]


def build():
    options = k.args()
    out = mk.outdir(options)
    only = set(options["only"].split(",")) if "only" in options else None
    k.reset()
    bpy.context.scene.view_settings.view_transform = "Standard"
    m = materials()
    whole = build_whole(m)
    print("whole red works wreck: %d triangles, %d objects" % (mk.triangles(whole), len(whole)))
    if "whole" in options:
        mk.export(whole, options["whole"])
    for name, sprite, box, origin, _ in rw.PIECES:
        name = name + "_wreck"
        if only is not None and name not in only:
            continue
        parts = []
        for src in whole:
            cap = src.data.materials[0] if src.data.materials else m["dark"]
            piece = cut(src, box, cap)
            if piece is not None:
                piece.name = src.name + "_" + name
                parts.append(piece)
        drop_unused(parts)
        for src in whole:
            src.hide_render = True
        shear_to_camera(parts)
        mk.transform(parts, Matrix.Translation((-origin[0], -origin[1], 0.0)))
        bpy.context.view_layer.update()
        triangulate(parts)
        obj = join(parts, name)
        obj.data.name = name
        merge_materials(obj, 15)
        mk.report(name, [obj], os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, [obj])
        bpy.data.objects.remove(obj)
        for src in whole:
            src.hide_render = False


if __name__ == "__main__":
    build()
