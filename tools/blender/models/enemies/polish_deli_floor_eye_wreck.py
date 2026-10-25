"""The wreck of the machine set in UNDERDELI's dark floor (sheet ^, x5e in models.cfg, sprite 45, 2x2), stage 4 of the
clean ground (2026-10-25): what UNDERDELI's map paints where the machines stand (rows of two to seven), which
tools/terrain/make_cleanground.py erases and the game shows as stand-ins (models.cfg "wreck x5e 45
deli_floor_eye_wreck", drawn with the live sprite line's options: yaw=0 height=-4; the live line's glow is not drawn
for stand-ins).

As the map paints it (UNDERDELI's tiles at 4x; coordinates as below): most of the machine is gone, the dark floor
showing between what is left. The eye is out, its socket dark; of the left pillar its lit left wall still stands,
leaning back (x -9..-5, y 13..7), and a slab of its top lies fallen forward over the hood's place (from (-8, 4) down
to (0, 0), its lower right edge lit); of the right pillar only a bent strip of its outer wall stands (an arc from
(2.5, 13) to (7.5, 7)); the grille's dark recess at x -1..0; a torn cable's loop at (6, 2); the hood is gone, the two
steps (x -9..-1 and 1..8, y 0..-6, their front edges lit) and the dark ramp between them are left. No red: the eye's
light is out (so no embers).

Built on polish_deli_floor_eye.py: its parts and measures (the pillars' plans and tops, the grille, the steps and the
ramp; the hood, the socket and the lens left out), then broken: of the left pillar its left wall (its top cut on a
slant, leaning back) and a slab of its top laid forward, of the right pillar a bent strip of its outer wall round its
back right corner; the grille's recess narrower and lower, its bars taken but one, bent over; a cable loop, steel
shards and chunks on the floor; scorched round the eye (polish_jaw_gun_wreck.scorch).

Coordinates as in polish_deli_floor_eye.py: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the floor
(z = 0); origin at the sprite's centre (pixel 12, 14).

models.cfg: model deli_floor_eye_wreck enemies/deli_floor_eye_wreck.glb origin; wreck x5e 45 deli_floor_eye_wreck.

Options after "--": --outdir <dir> (default assets/models/enemies), --preview <prefix>.
"""
import math
import os
import sys

import bpy
import mathutils.noise as noise
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
import polish_deli_floor_eye as fe  # noqa: E402
import polish_jaw_gun_wreck as wk  # noqa: E402  (the shared wreck helpers)

# The left pillar: its left wall (x < WALL_X) stands, its top on a slant (z at its back, z at its front), leaning back
# by LEAN degrees about its foot's front edge; the rest of it is gone but a slab of its top (SLAB_Z thick, x > WALL_X),
# swung about z by SWING degrees, tipped forward by TOPPLE and laid with its middle at SLAB_AT, over the hood's place.
WALL_X, WALL_TOP, LEAN = -6.5, (7.4, 3.6), -12.0
SLAB_Z = 2.6                                # the slab's thickness
TOPPLE, SWING, SLAB_AT = 16.0, -52.0, (-4.4, 1.9, 1.35)
# The right pillar: a bent strip of its outer wall round its back right corner: the strip's path
# (x, y, its top's z), half-width.
RIGHT_STRIP = [(1.9, 11.0, 7.2), (4.4, 11.1, 6.7), (6.4, 10.6, 5.8), (7.0, 8.6, 4.6), (7.0, 5.6, 3.0), (6.8, 3.4, 1.7)]
STRIP_HALF = 0.55
GRILLE_KEEP = 1                             # the bar that stays, bent over
CABLE = ((6.1, 1.9, 1.3), 1.15, 0.32)       # the torn cable's loop: centre, radius, its bar's radius
SHARDS = [([(-10.6, 1.2), (-9.2, 1.8), (-9.4, 0.2)], 0.0, 0.3, (10.0, -6.0)),
          ([(9.0, 2.4), (10.4, 2.8), (10.2, 1.2), (9.0, 1.4)], 0.0, 0.3, (-6.0, 8.0)),
          ([(2.6, -0.6), (4.4, -0.2), (4.0, -2.0), (2.8, -1.8)], 0.0, 0.3, (0.0, 12.0)),
          ([(-3.2, 7.4), (-1.8, 8.2), (-2.0, 6.6)], 0.0, 0.25, (8.0, 0.0))]
CHUNKS = [((-1.6, 4.6, 0.0), (1.1, 0.9, 0.7)), ((2.8, 4.0, 0.0), (0.9, 0.8, 0.6)), ((1.4, 9.0, 0.0), (1.0, 0.9, 0.6)),
          ((-0.6, -1.4, 0.0), (0.9, 0.8, 0.5)), ((7.0, -0.6, 0.0), (0.8, 0.7, 0.5))]
BURN = ((-0.5, 6.0, 3.0), (6.5, 6.5, 6.0))


def burn(co):
    centre, radii = BURN
    d = Vector(((co.x - centre[0]) / radii[0], (co.y - centre[1]) / radii[1], (co.z - centre[2]) / radii[2]))
    return 1.0 * math.exp(-1.3 * d.length_squared) + 0.16 * noise.noise(co * 0.5 + Vector((4.1, 0.7, -2.3)))


def turn(obj, pivot, rotation, shift=(0.0, 0.0, 0.0)):
    obj.data.transform(Matrix.Translation(Vector(pivot) + Vector(shift)) @ rotation @
                       Matrix.Translation(-Vector(pivot)))


def build_whole():
    m = fe.materials()
    m["soot"] = k.material("soot", palette=0x10, metallic=0.2, roughness=0.8)
    fe.grille(m)
    fe.eye(m)
    fe.steps(m)
    for obj in mk.meshes():
        mk.apply(obj)
    by = {o.name: o for o in mk.meshes()}
    # The eye is gone, lens and socket.
    wk.delete([by.pop("eye_lens"), by.pop("eye_socket")])
    # The pillars' remains, built as polish_deli_floor_eye.pillars() builds the pillars (wedges of their plans under
    # their tops, bevelled; the live pillars' rib grooves don't take booleans cleanly): of the left one its left wall
    # (its top cut on a slant), leaning back, and a slab of its top fallen forward (its grooves cut in); of the right
    # one the bent strip of its outer wall.
    top = fe.slope_y(2.5, fe.PILLAR_Z[0], 11.6, fe.PILLAR_Z[1])
    y_back, y_front = fe.YE(2.5), fe.YE(11.6)
    zb, zf = WALL_TOP
    wall_c1 = WALL_X + 12.0                     # (the wall's right edge, in columns)
    wall = fe.block("pillar_l_wall", [(3.4, 3.4), (3.5, 2.5), (wall_c1, 2.5), (wall_c1, 11.6), (3.4, 11.6)],
                    lambda x, y: zb + (zf - zb) * (y - y_back) / (y_front - y_back) + 0.45 * math.sin(2.3 * y + 0.7),
                    m["steel"], bevel=0.4)
    turn(wall, (WALL_X, y_front, 0.0), Matrix.Rotation(math.radians(LEAN), 4, "X"))
    slab = fe.block("pillar_l_slab", [(wall_c1, 2.5), (9.3, 2.5), (9.5, 3.4), (9.5, 11.6), (wall_c1, 11.6)],
                    lambda x, y: top(x, y) - SLAB_Z + 0.4, m["steel"], bevel=0.45)
    cuts = [mk.box(f"slab_rib{i}", fe.XE(c) - 0.24, fe.XE(c) + 0.24, fe.YE(11.0), fe.YE(2.0), 0.9, 9.0)
            for i, c in enumerate(fe.PILLAR_RIBS) if fe.XE(c) > WALL_X + 0.3]
    if cuts:
        mk.boolean(slab, cuts, "DIFFERENCE")
        mk.cleanup(slab)
    centre = sum((Vector(c) for c in slab.bound_box), Vector()) / 8
    slab.data.transform(Matrix.Translation(SLAB_AT) @ Matrix.Rotation(math.radians(TOPPLE), 4, "X") @
                        Matrix.Rotation(math.radians(SWING), 4, "Z") @ Matrix.Translation(-centre))
    wk.clip_below(slab, 0.0)
    for obj in (wall, slab):
        mk.shade(obj, 35)
        fe.paint_by_normal(obj, m["steel"], m["shade"], under=m["dark"], lit=m["lit"])
    # The grille's recess, what is left of it: narrower and lower.
    recess = by["grille_recess"]
    recess.data.transform(Matrix.Translation((fe.AXIS_X, 0, 0)) @ Matrix.Diagonal((0.55, 1.0, 0.7, 1.0)) @
                          Matrix.Translation((-fe.AXIS_X, 0, 0)))
    dense = mk.chaikin(RIGHT_STRIP, 2, closed=False)
    points = [Vector((x, y, z - 0.45)) for x, y, z in dense]
    strip = mk.bar("pillar_r_strip", points, [Vector((0, 0, 1))] * len(points), STRIP_HALF, 0.45,
                   max(p.z for p in points) + 1.0, m["steel"], 12, 4.0)
    wk.clip_below(strip, 0.0)
    mk.shade(strip, 40)
    fe.paint_by_normal(strip, m["lit"], m["shade"], under=m["dark"], lit=m["steel"], top_min=0.6)
    # The grille: one bar left, bent over; the others gone.
    for i in range(len(fe.GRILLE_BARS)):
        if i != GRILLE_KEEP:
            wk.delete([by.pop(f"grille_bar{i}")])
    bar = by[f"grille_bar{GRILLE_KEEP}"]
    x = fe.XE(fe.GRILLE_BARS[GRILLE_KEEP])
    turn(bar, (x, fe.YE(fe.GRILLE[3]), 0.0), Matrix.Rotation(math.radians(24.0), 4, "Y") @
         Matrix.Rotation(math.radians(-10.0), 4, "X"))
    # On the floor: the torn cable's loop, steel shards, chunks.
    (cx, cy, cz), radius, thick = CABLE
    loop = [(cx + radius * math.cos(a), cy + 0.6 * radius * math.sin(a), cz + 0.9 * radius * math.sin(a) + 0.2 * a)
            for a in [2 * math.pi * j / 10 for j in range(11)]]
    wk.bent_bar("cable", [(cx - 2.4, cy - 0.6, 0.3)] + loop + [(cx + 1.6, cy - 1.8, 0.25)], thick, m["lit"], 8)
    for i, (outline, z, th, tilt) in enumerate(SHARDS):
        wk.shard(f"shard{i}", outline, z, th, m["shade"], tilt)
    for i, (c, radii) in enumerate(CHUNKS):
        wk.rock(f"chunk{i}", c, radii, m["dark"] if i % 2 else m["shade"], 41.0 + 1.3 * i, flat=0.0)
    parts = mk.meshes()
    for obj in parts:
        mk.apply(obj)
        wk.clip_below(obj, 0.0)
    for obj in parts:
        if obj.name.startswith(("chunk", "shard", "cable")):
            continue
        wk.scorch(obj, burn, levels=(0.32, 0.78), step=1.2 if obj.name.startswith("pillar") else None)
        wk.reshade(obj, 35)
    whole = mk.meshes()
    for obj in whole:
        mk.apply(obj)
    bpy.context.view_layer.update()
    return [o for o in whole if len(o.data.polygons) > 0], m


def build():
    k.reset()
    options = k.args()
    parts, m = build_whole()
    bpy.context.scene.view_settings.view_transform = "Standard"
    mk.report("deli_floor_eye_wreck", parts, os.path.join(mk.outdir(options), "deli_floor_eye_wreck.glb"))
    if "preview" in options:
        mk.preview(options["preview"] + "deli_floor_eye_wreck", parts)


if __name__ == "__main__":
    build()
