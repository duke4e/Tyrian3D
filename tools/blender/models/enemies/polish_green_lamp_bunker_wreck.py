"""The grey sentry post's wreck (sheet S sprite 277's stand-in: what the asteroid maps paint where green_lamp_bunker
stands once it is destroyed, before it comes and where none comes; 73 of them in ASTEROID1, ASTEROID2, ASTEROID?,
ASTCITY, AST. CITY and GREY MOON), built on polish_green_lamp_bunker.py (2026-10-25, the clean ground's stage 4).

As the maps paint it at 4x (the asteroid tiles' 385, the most common of its paintings; ASTEROID2 14a0d01cd2b01f4c at
540, 3206): the post burst open: the head's left and right ends still standing (grey, 0x07-0x0b), its middle with the
visor blown out, a hollow glowing red inside (0x70-0x74); the shield split down its middle, its left half peeled out
(its lit edge, 0x0b-0x0e, running down the left, red showing inside it, 0x70-0x73), its right half crumpled into a
grey heap (0x07-0x0b); the pipes torn away (stubs and the dark marks of them along the ground); soot all round it
(0x01-0x03).

The model: the live post (polish_green_lamp_bunker: head, shield, pipes) with the lamp out (frame 11's grey glass);
the head's middle blasted away by a lumpy exact boolean (its faces burnt, 0x02), its two ends left standing to their
full height (8.2: more than 7.4, so the game sets the wreck on the ground as it does the live post), sooted in patches
(0x05, 0x03); in the hollow a bed of embers glowing faintly (0x72, 0x74 and 0x76 at 0.3-0.4) among dark lumps (0x70,
0x02); the shield cut in two: the left half peeled out to the left, its inside an ember's dull red (0x72 at 0.25), the
right half cut again and crumpled down; the rivets, the straps, the lens and the visor's right bolts gone; of the
pipes only broken lengths along the ground with their flanges, sooted; bent plates of the armour and dark rubble lying
round it.

The same frame as green_lamp_bunker: origin at the sprite's centre (pixel 12, 14), +Y up the sprite, +Z up from the
ground (z = 0); drawn as the live model (models.cfg: model green_lamp_bunker_wreck enemies/green_lamp_bunker_wreck.glb;
wreck s 277 green_lamp_bunker_wreck, so the game draws it with sprite s 277's options, yaw=0; its glow is the live
enemy's only).

Options after "--": --outdir <dir> (default assets/models/enemies), --preview <prefix>.
"""
import os
import sys

import bpy
from mathutils import Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k, smoothstep  # noqa: E402
import polish_green_lamp_bunker as live  # noqa: E402
import polish_panel_pills_wreck as wk  # noqa: E402

# The blast through the head's middle: centre, radii, seed.
BLAST = ((1.0, 9.6, 8.6), (5.6, 5.2, 5.6), 2.0)
# The head's right end knocked lower: a second blast.
BLAST_RIGHT = ((8.8, 8.0, 9.6), (3.0, 3.2, 3.6), 5.0)
# The embers in the hollow: (x, y, z, radius, shade, glow or 0).
EMBERS = [(-1.6, 11.2, 3.8, 2.0, 0x76, 0.35), (1.4, 11.8, 3.6, 2.2, 0x74, 0.4), (3.0, 9.4, 3.4, 1.4, 0x70, 0.0),
          (-0.4, 9.0, 3.6, 1.5, 0x74, 0.35), (2.4, 12.9, 4.0, 1.2, 0x72, 0.3), (-3.2, 12.8, 4.2, 1.1, 0x02, 0.0),
          (4.0, 11.4, 3.8, 1.1, 0x76, 0.3), (-1.6, 6.6, 3.0, 1.3, 0x70, 0.0), (0.4, 13.2, 4.4, 1.0, 0x70, 0.0)]
# The shield's cuts and how its pieces lie: the left half peeled out about an axis along its foot.
SPLIT_X = -1.2
PEEL = ((-7.4, 3.0, 0.0), (0.05, 1.0, 0.0), -38.0)
SPLIT_RIGHT = ((0.0, 3.2, 0.0), (0.25, 1.0, 0.0))
CRUMPLE = [("shield_r", (4.0, -0.6, 0.0), (1.0, 0.25, 0.0), 16.0, 2.4),
           ("shield_rb", (6.4, 6.0, 0.0), (0.3, 1.0, 0.0), 22.0, 2.0)]
# What is left of the pipes: (pipe, from y, to y) broken lengths along the ground.
PIPE_LENGTHS = [("pipe0", -9.6, -6.2), ("pipe0", -5.4, -3.6), ("pipe1", -9.6, -7.0), ("pipe_side", -9.6, -7.6)]
# Bent plates of armour: (x, y, heading, length, width, rise, shade); dark rubble: (x, y, z, radius, seed, shade).
PLATES = [(9.0, 2.2, 250, 3.4, 2.2, 0.9, "head_top"), (6.6, -6.4, 200, 2.8, 1.8, 0.6, "head"),
          (-9.8, -2.4, 300, 2.6, 1.6, 0.7, "shield"), (2.6, -4.6, 160, 2.2, 1.5, 0.5, "flange")]
RUBBLE = [(8.4, 7.4, 0.4, 0.9, 1.0, "char"), (10.2, -1.2, 0.35, 0.7, 2.0, "flange"), (-8.6, 5.8, 0.4, 0.7, 3.0, "soot"),
          (4.2, -8.8, 0.3, 0.6, 4.0, "char"), (-3.4, -6.6, 0.3, 0.55, 5.0, "head"), (6.0, 12.6, 0.4, 0.7, 6.0, "burnt"),
          (-6.2, -8.0, 0.3, 0.5, 7.0, "soot"), (3.2, 6.0, 2.2, 1.0, 8.0, "burnt"), (6.4, 3.0, 1.4, 0.9, 9.0, "char")]


def keep_between(obj, y0, y1, cap, name):
    """A copy of the part of obj between y0 and y1 (closed over its cuts with cap)."""
    piece = obj.copy()
    piece.data = obj.data.copy()
    piece.name = name
    bpy.context.scene.collection.objects.link(piece)
    rest = wk.split_piece(piece, (0, y1, 0), (0, 1, 0), cap, name + "_x")
    if rest is not None:
        bpy.data.objects.remove(rest)
    rest = wk.split_piece(piece, (0, y0, 0), (0, -1, 0), cap, name + "_y")
    if rest is not None:
        bpy.data.objects.remove(rest)
    return piece


def soot_field(c):
    near = 1.0 - smoothstep(0.0, 6.0, abs(c.x - BLAST[0][0]))
    return wk.fbm(c.x * 0.3 + 6.0, c.y * 0.3, c.z * 0.3, 2) + 0.35 * near


def build():
    options = k.args()
    k.reset()
    m = live.materials(live.FRAMES[2][2], live.FRAMES[2][3])   # frame 11's: the lamp out
    # (at most 15 materials a model: the game colours no more from the palette; the post's own greys serve the plates
    # and the rubble, its seam the char)
    burnt = wk.mat("lampwreck_burnt", 0x02, 0.1, 0.85)
    soot = wk.mat("lampwreck_soot", 0x05, 0.2, 0.7)
    char = m["seam"]
    embers = {0x72: wk.mat("lampwreck_ember_72", 0x72, 0.0, 0.5, 0.3),
              0x74: wk.mat("lampwreck_ember_74", 0x74, 0.0, 0.5, 0.38),
              0x76: wk.mat("lampwreck_ember_76", 0x76, 0.0, 0.5, 0.35),
              0x70: wk.mat("lampwreck_cinder", 0x70, 0.0, 0.6), 0x02: burnt}
    inside = embers[0x72]
    named = dict(m, burnt=burnt, soot=soot, char=char)
    live.head(m)
    live.shield(m)
    live.pipes(m)
    objects = {o.name: o for o in mk.meshes()}
    # Gone: the lens, the right bolts, the rivets, the straps (and the pipes, but for their lengths on the ground).
    for name in list(objects):
        if (name == "lens" or name.startswith("rivet") or name.startswith("strap") or
                (name.startswith("bolt") and objects[name].data.vertices[0].co.x > 0)):
            bpy.data.objects.remove(objects.pop(name))
    for i, (name, y0, y1) in enumerate(PIPE_LENGTHS):
        keep_between(objects[name], y0, y1, char, f"pipe_left{i}").data.materials[0] = soot
    for name in ("pipe0", "pipe1", "pipe_side"):
        bpy.data.objects.remove(objects.pop(name))
    # The head's middle blasted away; embers in the hollow; the ends sooted.
    (cx, cy, cz), radii, seed = BLAST
    head = objects["head"]
    wk.break_away(head, wk.rock("blast", (cx, cy, cz), radii, burnt, seed, subdivisions=2, rough=0.3))
    (cx, cy, cz), radii, seed = BLAST_RIGHT
    wk.break_away(head, wk.rock("blast", (cx, cy, cz), radii, burnt, seed, subdivisions=2, rough=0.3))
    k.smooth(head, 40)
    soot_slot, char_slot = mk.slot_of(head, soot), mk.slot_of(head, char)
    for poly in head.data.polygons:
        if head.data.materials[poly.material_index].name == burnt.name:
            continue
        v = soot_field(poly.center)
        if v > 0.6:
            poly.material_index = char_slot
        elif v > 0.25:
            poly.material_index = soot_slot
    for j, (x, y, z, r, shade, glow) in enumerate(EMBERS):
        mat_ = embers[shade]
        mk.apply(wk.rock(f"ember{j}", (x, y, z), (r, r * 0.85, r * 0.55), mat_, 10.0 + j, 1, 0.3))
    # The shield split; its left half peeled out, its right half crumpled.
    shield = objects["shield"]
    right = wk.split_piece(shield, (SPLIT_X, 0, 0), (1, 0, 0), burnt, "shield_r")
    i = [mm.name for mm in shield.data.materials].index(burnt.name)
    shield.data.materials[i] = inside   # (the left half's cut face: its inside, seen as it peels out)
    pivot, axis, degrees = PEEL
    wk.turn([shield], pivot, axis, degrees)
    rb = wk.split_piece(right, *SPLIT_RIGHT, burnt, "shield_rb")
    pieces = {"shield_r": right, "shield_rb": rb}
    for name, pivot, axis, degrees, sink in CRUMPLE:
        wk.turn([pieces[name]], pivot, axis, degrees)
        pieces[name].data.transform(Matrix.Translation((0, 0, -sink)))
    for obj in (shield, right, rb):
        (cx, cy, cz), radii, seed = BLAST
        wk.break_away(obj, wk.rock("blast", (cx, cy - 1.0, cz), radii, burnt, seed, subdivisions=2, rough=0.3))
        k.smooth(obj, 50)
        soot_slot, char_slot = mk.slot_of(obj, soot), mk.slot_of(obj, char)
        for poly in obj.data.polygons:
            if obj.data.materials[poly.material_index].name in (burnt.name, inside.name):
                continue
            v = soot_field(poly.center) - 0.15
            if v > 0.6:
                poly.material_index = char_slot
            elif v > 0.2:
                poly.material_index = soot_slot
    # Bent plates of armour and dark rubble round it.
    for j, (x, y, heading, length, width, rise, shade) in enumerate(PLATES):
        plate = wk.shard(f"plate{j}", (x, y, 0.1), heading, length, width, rise, named[shade], 0.3,
                         0.2 * ((j % 3) - 1), 4)
        mk.bevel(plate, 0.08, 1, 40)
    for j, (x, y, z, r, seed, shade) in enumerate(RUBBLE):
        mat_ = named[shade]
        mk.apply(wk.rock(f"rubble{j}", (x, y, z), (r, r * 0.8, r * 0.6), mat_, seed + 20.0, 1, 0.3))
    wk.clip_below(mk.meshes())
    wk.finish("green_lamp_bunker_wreck", options, None)


if __name__ == "__main__":
    build()
