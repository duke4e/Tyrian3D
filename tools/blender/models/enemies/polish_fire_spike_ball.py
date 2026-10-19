"""The spiked ball of fire of TIME WAR and SQUADRON (sheet L sprite 116, 1x1: an 11 x 14 ball in the 12 x 14 cell;
enemies 670 on top and 725 on the ground; not animated), polished (2026-10-19; it replaces wave3_z_small.py's
fire_spike_ball()). models.cfg: sprite l 116 fire_spike_ball yaw=0 glow=14:0.35:121:-0.5:0.5 (it was a bare glow).
No other enemy shows this sprite; it is no other sprite's pixels mirrored or in other ramps.

As the sprite and its 4x upscale draw it: a squarish ball of fire (columns 1-9 of rows 3-11, ramp 7), white-hot a
little above its middle (0x7f at column 5 of row 6) and yellow-orange round that and to the left (0x7a-0x7c), deep red
towards its rim and darker red crust in its lower half (0x70-0x73); a long thin spike straight up the screen (column
5 of rows 0-2), a shorter one down (rows 12-13) and stubby ones left and right (columns 0 and 10 of rows 6-8); its
corners (the outline's dark pixels) the tips of four short spikes between them.

The ball: an icosphere made lumpy with smooth noise and drawn out into the spikes (one surface: each spike a cone
grown out of the ball along its direction, its tip on a vertex so that it ends sharp), a few short ones rising
towards the camera as well, so that it reads as a spiked ball from the game's slanted camera too. The heat painted
on it is cut into bands of the sprite's own palette indices (polish_orb_red.band_split), the hot bands glowing in
their own colours; the spikes cool from their roots (orange) to their dark red tips.

Origin at the sprite's centre (pixel 6, 7); +Y up the sprite, +Z towards the camera; the ball's middle at
(-0.5, -0.5), standing on z = 0 (the game centres it in height on its layer).

Replaces wave3_z_small.py's fire_spike_ball() (its @kit.model("fire_spike_ball", ...) function, the SPIKY =
kit.frame("SPIKY", ...) line and the fire_spike_ball lines of its docstring; wave3_z_art.py's SPIKY, which only it
reads): remove them so that they don't overwrite this model.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouette against
enemy_L.png), --preview <prefix>.
"""
import math
import os
import sys

import bmesh
import bpy
import mathutils.noise as noise
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
from polish_balls import preview, triangles  # noqa: E402
from polish_orb_red import band_split  # noqa: E402
from polish_sphere_nozzle import smoothstep  # noqa: E402

RADIUS = 4.55
PLAN_POWER = 2.9                      # the ball squarish in plan (its corners the sprite's)
CENTRE = Vector((-0.5, -0.5, RADIUS * 0.92))
# The spikes: (direction (x, y, z), length beyond the ball, half-angle of its root (degrees)).
SPIKES = [
    ((0.0, 1.0, 0.0), 3.0, 17.0),      # up the screen (rows 0-2)
    ((0.0, -1.0, 0.0), 2.1, 16.0),     # down (rows 12-13)
    ((-1.0, 0.0, 0.0), 1.5, 16.0),     # left (column 0)
    ((1.0, 0.0, 0.0), 1.5, 16.0),      # right (column 10)
    ((-1.0, 1.0, 0.3), 0.55, 13.0),    # the corners
    ((1.0, 1.0, 0.3), 0.55, 13.0),
    ((-1.0, -1.0, 0.3), 0.5, 13.0),
    ((1.0, -1.0, 0.3), 0.5, 13.0),
    ((-0.45, 0.35, 0.82), 0.9, 12.0),  # rising towards the camera
    ((0.6, -0.25, 0.76), 0.85, 12.0),
    ((-0.2, -0.75, 0.62), 0.8, 12.0),
    ((0.55, 0.65, 0.5), 0.8, 12.0),
]
HOT = Vector((-0.6, 0.6))             # the white-hot spot in the top view (column 5 of row 6)
HOT_RADIUS = 1.9
FLARE = Vector((-3.2, 0.7))           # the yellow flare to its left (column 2 of row 6)
FLARE_RADIUS = 1.3

# The bands of heat: (lowest heat, palette index, emission strength in the palette colour).
BANDS = [
    (-9.0, 0x71, 0.1),
    (0.14, 0x72, 0.25),
    (0.24, 0x73, 0.35),
    (0.32, 0x74, 0.5),
    (0.42, 0x76, 0.75),
    (0.54, 0x78, 1.0),
    (0.66, 0x7a, 1.3),
    (0.78, 0x7c, 1.7),
    (0.9, 0x7e, 2.1),
    (1.0, 0x7f, 2.5),
]


def spike_dirs():
    return [(Vector(d).normalized(), length, math.radians(width)) for d, length, width in SPIKES]


def build_ball(mats):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=4, radius=1.0)
    # Twice as fine on the side the game's camera sees (and round the spikes in the plane).
    seen = [e for e in bm.edges if all(v.co.z > -0.25 for v in e.verts)]
    bmesh.ops.subdivide_edges(bm, edges=seen, cuts=1, use_grid_fill=True)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    for v in bm.verts:
        v.co.normalize()
    bm.verts.index_update()
    spikes = spike_dirs()
    # Each spike's tip on the vertex nearest its direction, so that it ends in a point.
    tips = {}
    for i, (d, _, _) in enumerate(spikes):
        v = max(bm.verts, key=lambda v: v.co.normalized().dot(d))
        tips[v.index] = i
    values = []
    for v in bm.verts:
        d = v.co.normalized()
        flat = math.hypot(d.x, d.y)
        if flat > 1e-6:  # squarish in plan: a superellipse's radius in this direction
            cx, cy = abs(d.x) / flat, abs(d.y) / flat
            square = (cx ** PLAN_POWER + cy ** PLAN_POWER) ** (-1.0 / PLAN_POWER)
            square = 1.0 + (square - 1.0) * flat ** 2
        else:
            square = 1.0
        r = RADIUS * square * (1.0 + 0.05 * noise.noise(d * 2.4 + Vector((3.0, 8.0, 1.0))))
        spike_heat = None
        for i, (sd, length, width) in enumerate(spikes):
            a = d.angle(sd)
            if a < width:
                f = (1 - a / width) ** 1.7
                if v.index in tips and tips[v.index] == i:
                    f = 1.0
                r += length * f
                spike_heat = max(spike_heat, f) if spike_heat is not None else f
        p = CENTRE + d * r
        v.co = p
        # The heat: white-hot round the spot seen from above, cooling towards the rim and into the crust below.
        q = Vector((p.x - HOT.x, p.y - HOT.y))
        top = max(0.0, d.z)
        flare = Vector((p.x - FLARE.x, p.y - FLARE.y))
        heat = 0.4 + 0.68 * math.exp(-(q.length / HOT_RADIUS) ** 2) * smoothstep(0.1, 0.6, top)
        heat += 0.45 * math.exp(-(flare.length / FLARE_RADIUS) ** 2) * smoothstep(0.0, 0.5, top)
        heat += 0.08 * math.exp(-((q.length - 2.6) / 0.9) ** 2) * smoothstep(0.2, 0.7, top)  # the orange round it
        heat += 0.13 * noise.noise(d * 3.4 + Vector((7.0, 2.0, 5.0)))
        heat += 0.09 * noise.noise(d * 7.0 + Vector((1.0, 9.0, 4.0)))
        heat -= 0.2 * smoothstep(-0.2, -0.75, d.y) * smoothstep(0.0, 0.5, top)  # the crust in its lower half
        heat -= 0.2 * smoothstep(0.1, -0.5, d.z)                               # the underside
        if spike_heat is not None:
            heat = heat * (1 - spike_heat) + (0.45 - 0.4 * spike_heat) * spike_heat
        values.append(heat)
    mesh = bpy.data.meshes.new("fire_spike_ball")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("fire_spike_ball", mesh)
    bpy.context.scene.collection.objects.link(obj)
    band_split(obj, values, [(lowest, mats[index]) for lowest, index, _ in BANDS])
    return k.smooth(obj, 50)


def build():
    options = k.args()
    outdir = options.get("outdir", os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "enemies"))
    k.reset()
    pal = k.level_palette()
    mats = {index: k.material(f"spikeball_{index:x}", palette=index, metallic=0.0, roughness=0.42,
                              emission=pal[index] if glow > 0 else None, emission_strength=glow)
            for _, index, glow in BANDS}
    build_ball(mats)
    used = {m.name for obj in bpy.context.scene.objects if obj.type == "MESH" for m in obj.data.materials}
    print("== fire_spike_ball (L 116): %d triangles, %d materials: %s" % (triangles(), len(used),
                                                                         ", ".join(sorted(used))))
    if "check" in options:
        k.check_silhouette(os.path.join(options["check"], "enemy_L.png"), 116, large=False)
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    path = os.path.join(outdir, "fire_spike_ball.glb")
    k.export(path)
    print("%s: %d bytes" % (path, os.path.getsize(path)))
    if "preview" in options:
        preview(options["preview"] + "fire_spike_ball", size=(12, 14), distance=0.5)


if __name__ == "__main__":
    build()
