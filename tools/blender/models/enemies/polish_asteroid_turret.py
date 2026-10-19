"""ASTEROID2's grey turret with a bronze dome (sheet P sprite 13, 2x2: 24 x 28 pixels; enemy 194 of episode 1, ground
layer, ASTEROID2 and ASTEROID?; its eight sprites 13 15 17 51 55 89 91 93 are headings the level picks, not an
animation), polished (2026-10-19; it replaces wave2_h.py's asteroid_turret(), parts inflated from the pixel art).
models.cfg: model asteroid_turret enemies/asteroid_turret.glb; sprite p 13 asteroid_turret yaw=aim (unchanged: the
model points up the screen, as P 15, and turns to face the player about its dome).

P 13's eight sprites are, pixel for pixel, sheet 2's 91 45 93 39 43 129 41 131 (P 15 is 2 45 and so on; P 13 and 2 91
differ in ten pixels): the frames of TYRIAN's small grey gunship with a bronze dome (2 91, enemy 15, dome_gunship,
yaw=velocity). So this model is that gunship too: "sprite 2 91 asteroid_turret yaw=velocity" would replace
dome_gunship (wave1_c.py's).

As P 15 and its 4x upscale draw it (pointing up the screen): a grey armoured hull like a heart, two rounded lobes at
its back (rows 16-19) with a notch between them where a red light shines (columns 11-12 of row 17), its flanks
(columns 5-7 and 15-17, lit on the left) narrowing forwards into two prongs either side of the gun (columns 8-9 and
13-14 of rows 7-10); in its middle a bronze dome, a rounded square (columns 9-13 of rows 11-14) on a dark collar; the
gun from the dome forwards between the prongs, a steel barrel with a dark ring and a brass muzzle (column 11, rows
2-10).

The hull is cast armour, as the upscale paints it (soft, rounded, glossy): two thick arms swept along the flanks
(rounded-box sections), from the lobes at the back to the prongs, the back between the lobes swept likewise and a
floor between them round the dome, a little lower, merged by a voxel remesh and smoothed (polish_machine_kit.soften),
its underside flat; a dark ring round the dome. The dome is turned with a squarish plan (superellipse) on a dark collar; the mantlet, the
barrel, its ring and the brass muzzle round a dark bore are turned parts; the red lamp a glowing lens in a socket on
the back. The game centres a ground model in height on the ground enemies' layer (4) and lifts it to 0.3 if it would
reach lower: a speck at PIN_Z (a triangle a thousandth of a pixel across, over the dome, invisible) makes the model
tall enough to be set on the ground (bottom at 0.3) rather than float.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen (the gun's way), +Z up from the ground;
the origin is the dome's middle (the sprite's columns 9-13, rows 11-14: x -0.5, y 1 of P 15), so the turret turns
about it; P 15's column c, row r is (c - 11, 12.5 - r).

Replaces wave2_h.py's asteroid turret: remove TURRET (the pixel art), asteroid_turret() and its MODELS entry
("asteroid_turret", ...), and its lines in the docstring, so that it doesn't overwrite this model.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouette against P 15,
moved so its dome is on the origin), --preview <prefix>.
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402

DOME_AT = (-0.5, 1.0)               # the dome's middle in P 15 (the sprite's centre is the origin there)
# The right arm of the hull (mirrored for the left), from its lobe at the back round the flank to the prong beside
# the gun: points (x, y, half-width, height) (the sprite's columns 5-7 and 15-17 of rows 11-19, the prongs 8-9 and
# 13-14 of rows 7-10).
ARM = [(1.6, -6.05, 1.0, 2.5), (2.9, -6.35, 1.45, 2.9), (4.5, -5.6, 1.6, 3.2), (5.15, -3.6, 1.5, 3.4),
       (5.1, -1.1, 1.45, 3.45), (4.55, 1.1, 1.4, 3.35), (3.45, 2.85, 1.35, 3.2), (2.85, 4.6, 1.35, 3.05),
       (2.8, 6.1, 1.3, 2.85)]
# The back between the lobes, across behind the dome (rows 15-18): points (x, y, half-width, height) likewise.
BACK = [(-3.6, -4.0, 1.3, 2.9), (0.0, -3.95, 1.35, 2.75), (3.6, -4.0, 1.3, 2.9)]
FLOOR = (3.7, 3.4, 2.3)                 # the floor round the dome, between the arms: x and y radius (round y -0.3), top
RING_R = 3.2                            # the dark ring round the collar (the sprite's dark pixels round the dome)
HULL_SOFTEN = 3                         # smoothing passes after the remesh (how round the casting is)
ARM_POWER = 4.0                         # the arms' sections: rounded boxes
COLLAR = (2.85, 2.3, 1.1, 2.6)      # the dark collar: outer and inner radius at its foot, its foot and top
DOME_R, DOME_FOOT, DOME_TOP, DOME_POWER = 2.55, 2.4, 5.4, 3.0    # the bronze dome (a rounded square in plan)
GUN_Z = 3.75                        # the gun's axis
# The gun along y: the mantlet where it leaves the dome, the barrel, the dark ring, the brass muzzle (y, radius).
MANTLET = [(1.6, 1.15), (2.6, 1.15), (2.9, 0.85)]
BARREL = (2.6, 7.2, 0.62)
RING = (7.0, 7.9, 0.74)
MUZZLE = [(7.8, 0.8), (8.0, 0.86), (10.3, 0.86), (10.65, 0.72), (10.75, 0.42)]
BORE_R = 0.38
LAMP = (0.5, -4.2, 0.95, 0.55)      # the red lamp on the back: x, y, radius, how far it stands out
PIN_Z = 7.4

# The turret's pixels in P 15 (rows, columns), to check the silhouette against, moved like the model.
OWN = [(2, 5, [(10, 12)]), (6, 6, [(8, 14)]), (7, 10, [(7, 15)]), (11, 11, [(6, 16)]), (12, 17, [(5, 17)]),
       (18, 18, [(6, 16)]), (19, 19, [(7, 9), (13, 15)])]


def materials():
    glow = k.level_palette()
    return {
        "hull": k.material("turret_hull", palette=0x05, metallic=0.55, roughness=0.32),
        "hull_top": k.material("turret_hull_top", palette=0x06, metallic=0.55, roughness=0.3),
        "hull_dark": k.material("turret_hull_dark", palette=0x04, metallic=0.45, roughness=0.45),
        "pocket": k.material("turret_pocket", palette=0x02, metallic=0.4, roughness=0.5),
        "collar": k.material("turret_collar", palette=0x02, metallic=0.5, roughness=0.4),
        "dome": k.material("turret_dome", palette=0x17, metallic=0.45, roughness=0.3),
        "steel": k.material("turret_steel", palette=0x08, metallic=0.7, roughness=0.25),
        "ring": k.material("turret_ring", palette=0x02, metallic=0.6, roughness=0.35),
        "brass": k.material("turret_brass", palette=0x18, metallic=0.8, roughness=0.22),
        "bore": k.material("turret_bore", palette=0x01, metallic=0.2, roughness=0.7),
        "lamp": k.material("turret_lamp", palette=0x74, metallic=0.0, roughness=0.2, emission=glow[0x74],
                           emission_strength=1.6),
        "lamp_hot": k.material("turret_lamp_hot", palette=0x77, metallic=0.0, roughness=0.15, emission=glow[0x77],
                               emission_strength=2.2),
    }


def arm(name, path, mat, segments=20, power=2.6):
    """An arm of the hull: rounded-box sections (superellipse of `power`) along a path of points (x, y, half-width,
    height) on the ground, Chaikin-rounded; its ends closed round."""
    pts = mk.chaikin([tuple(p) for p in path], 2, closed=False)
    rings = []
    for i, (x, y, w, h) in enumerate(pts):
        a, b = pts[max(i - 1, 0)], pts[min(i + 1, len(pts) - 1)]
        t = Vector((b[0] - a[0], b[1] - a[1], 0.0)).normalized()
        side = Vector((t.y, -t.x, 0.0))
        ring = []
        for j in range(segments):
            u, v = mk.superellipse_point(2 * math.pi * j / segments, power)
            ring.append(Vector((x, y, h / 2)) + side * (u * w) + Vector((0, 0, v * h / 2)))
        rings.append(ring)
    first, last = pts[0], pts[-1]
    t0 = Vector((pts[1][0] - first[0], pts[1][1] - first[1], 0)).normalized()
    t1 = Vector((last[0] - pts[-2][0], last[1] - pts[-2][1], 0)).normalized()
    return k.loft(name, rings, mat, start_point=Vector((first[0], first[1], first[3] / 2)) - t0 * first[2] * 0.9,
                  end_point=Vector((last[0], last[1], last[3] / 2)) + t1 * last[2] * 0.9)


def join(name, objects):
    """The objects' meshes in one object (overlapping: a voxel remesh unites them)."""
    bm = bmesh.new()
    for obj in objects:
        bm.from_mesh(obj.data)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    joined = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(joined)
    joined.data.materials.append(objects[0].data.materials[0])
    for obj in objects:
        data = obj.data
        bpy.data.objects.remove(obj)
        if data.users == 0:
            bpy.data.meshes.remove(data)
    return joined


def hull(m):
    """The hull, cast: two thick arms round the flanks (from the lobes at the back to the prongs either side of the
    gun), the back between the lobes and a low floor under the dome, merged into one body and rounded all over
    (polish_machine_kit.soften: a voxel remesh, smoothed); its underside flat on the ground. The arms' tops lighter,
    their low sides and the pocket round the dome darker."""
    parts = []
    for side in (1, -1):
        path = [(side * x, y, w, h) for x, y, w, h in ARM]
        parts.append(arm(f"arm{side}", path, m["hull"], power=ARM_POWER))
    parts.append(arm("back", BACK, m["hull"], power=ARM_POWER))
    parts.append(mk.lathe("floor", [(0.01, 0.0), (FLOOR[0], 0.0), (FLOOR[0], FLOOR[2]), (0.01, FLOOR[2])], (0.0, -0.3),
                          m["pocket"], 40, squash=(1.0, FLOOR[1] / FLOOR[0])))
    body = join("hull", parts)
    mk.soften(body, voxel=0.2, iterations=HULL_SOFTEN, factor=0.6, ratio=0.24)  # the remesh unites them
    flatten_base(body)

    def pick(c, n):
        if math.hypot(c.x, c.y + 0.2) < RING_R and c.z < FLOOR[2] + 0.4:
            return m["pocket"]
        if n.z > 0.72 and c.z > 2.4:
            return m["hull_top"]
        if c.z < 1.1 and n.z < 0.3:
            return m["hull_dark"]
        return None
    mk.paint(body, pick)
    return body


def flatten_base(obj, z=0.0):
    """The softened hull's underside flat again on the ground (its vertices below the rounding's reach, down)."""
    for v in obj.data.vertices:
        if v.co.z < 0.45:
            v.co.z = z
    obj.data.update()


def dome(m):
    """The dark collar and the bronze dome on it: a rounded square in plan, its top full."""
    r_out, r_in, z0, z1 = COLLAR
    collar = mk.lathe("collar", [(r_in, z0), (r_out, z0), (r_out, z1 - 0.3), (r_out - 0.3, z1), (r_in, z1)],
                      (0.0, 0.0), m["collar"], 48)
    k.smooth(collar, 40)
    profile = []
    steps = 12
    for i in range(steps + 1):
        t = (math.pi / 2) * i / steps
        profile.append((max(0.01, DOME_R * math.cos(t) ** 0.7), DOME_FOOT + (DOME_TOP - DOME_FOOT) * math.sin(t) ** 1.1))
    shell = mk.lathe("dome", profile, (0.0, 0.0), m["dome"], 48, power=DOME_POWER)
    k.smooth(shell, 70)


def gun(m):
    """The mantlet, the barrel, its dark ring and the brass muzzle round a dark bore, along y at GUN_Z."""
    def turned(name, profile, mat, segments=24):
        rings = [[Vector((r * math.cos(2 * math.pi * j / segments), y, GUN_Z + r * math.sin(2 * math.pi * j / segments)))
                  for j in range(segments)] for y, r in profile]
        obj = k.loft(name, rings, mat)
        k.smooth(obj, 45)
        return obj
    turned("mantlet", MANTLET, m["collar"])
    y0, y1, r = BARREL
    turned("barrel", [(y0, r), (y1, r)], m["steel"])
    y0, y1, r = RING
    turned("ring", [(y0, r - 0.05), (y0 + 0.1, r), (y1 - 0.1, r), (y1, r - 0.05)], m["ring"])
    end = MUZZLE[-1][0]
    muzzle = turned("muzzle", MUZZLE + [(end - 0.02, BORE_R), (end - 1.2, BORE_R)], m["brass"])
    mk.paint(muzzle, lambda c, n: m["bore"] if math.hypot(c.x, c.z - GUN_Z) < BORE_R + 0.03 and c.y > end - 1.3
             else None)


def lamp(m):
    """The red lamp on the back between the lobes (the sprite's columns 11-12 of row 17), a glowing lens in a dark
    socket, hottest on its top."""
    x, y, r, rise = LAMP
    z = BACK[1][3] - 0.25
    socket = mk.lathe("lamp_socket", [(0.01, z - 0.4), (r + 0.25, z - 0.4), (r + 0.25, z + 0.08), (r + 0.05, z + 0.12),
                                      (0.01, z + 0.12)], (x, y), m["pocket"], 32, squash=(1.0, 0.72))
    k.smooth(socket, 40)
    lens = mk.dome("lamp", (x, y), (r, r * 0.72, rise), z, m["lamp"], 32, 8)
    mk.paint(lens, lambda c, n: m["lamp_hot"] if n.z > 0.75 else None)


def pin(m):
    """A speck at PIN_Z over the dome (a triangle a thousandth of a pixel across): the model is tall enough for the
    game to set it on the ground."""
    e = 0.001
    return k.mesh_object("pin", [(0, 0, PIN_Z), (e, 0, PIN_Z), (0, e, PIN_Z)], [(0, 1, 2)], m["hull"])


def own_mask():
    mask = [[False] * 24 for _ in range(28)]
    for r0, r1, spans in OWN:
        for r in range(r0, r1 + 1):
            for c0, c1 in spans:
                for c in range(c0, c1 + 1):
                    mask[r][c] = True
    return mask


def build():
    options = k.args()
    out = mk.outdir(options)
    k.reset()
    m = materials()
    hull(m)
    dome(m)
    gun(m)
    lamp(m)
    pin(m)
    parts = mk.meshes()
    for obj in parts:
        mk.apply(obj)
    bpy.context.view_layer.update()
    if "check" in options:
        # The sprite's view: the model moved back so its dome is where P 15 draws it.
        shift = Matrix.Translation((DOME_AT[0], DOME_AT[1], 0.0))
        mk.transform(parts, shift)
        bpy.context.view_layer.update()
        mk.compare("asteroid_turret (P 15, its own pixels)", mk.coverage(parts, 24, 28), own_mask())
        mk.transform(parts, shift.inverted())
        bpy.context.view_layer.update()
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    mk.report("asteroid_turret", parts, os.path.join(out, "asteroid_turret.glb"))
    if "preview" in options:
        mk.preview(options["preview"] + "asteroid_turret", parts, centre=(-DOME_AT[0], -DOME_AT[1]))


if __name__ == "__main__":
    build()
