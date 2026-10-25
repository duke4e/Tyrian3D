"""The bronze disc turret's wreck (sheet F sprite 39's stand-in: what SAVARA's maps paint where disc_turret stands once
it is destroyed, before it comes and where none comes; 31 of them in SAVARA and SAVARA Y), built on
polish_disc_turret.py (2026-10-25, the clean ground's stage 4).

As the maps paint it at 4x (SAVARA 3b9fdfa4d722a381 at 492, 3459; 9b460f25bf449153 the same): the turret in its place,
its ring and dome still round and pale (the dome's top left still catching the sun), the knob at its upper right
standing, but the dome's crown blown out: a black hole where the red eye sat, wider than the eye's socket (columns 6-12
of rows 9-14), its rim a rounded pale lip, darker bronze down its inner slope towards the lower right; the gun under
the dome broken off short, a stub ending a little past the ring (rows 18-22 instead of 18-25), the muzzle gone.

The model: the live ring, rivets, dome, knob and gun (polish_disc_turret's parts, its materials), broken: the crown cut
out of the dome by a jagged funnel (an exact boolean; the pit's walls and floor the socket's black-brown 0x10), the
eye gone with it; the dome scorched round the hole (its shades three darker, soot in patches at the rim); two torn
plates of the dome bent up and out at the rim's back and left (the tallest reaching the live eye's crest, 7.61, so the
game, which centres these models in height, places the wreck as the live turret); a few dark chunks and a dull ember
(0x73 at 0.22) deep in the pit; the gun snapped at a slant past the collar (its broken end closed in the muzzle's bronze), the
muzzle gone.

The same frame as disc_turret: origin at the sprite's centre (pixel 12, 14), +Y up the sprite, +Z up from the ground
(z = 0); no origin flag (as the live model's line). models.cfg: model disc_turret_wreck enemies/disc_turret_wreck.glb;
wreck f 39 disc_turret_wreck (drawn with sprite f 39's options, yaw=0).

Options after "--": --outdir <dir> (default assets/models/enemies), --preview <prefix>.
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
import polish_disc_turret as live  # noqa: E402
import polish_panel_pills_wreck as wk  # noqa: E402
from polish_jaw_gun_wreck import ember_material, rock, scorch  # noqa: E402
from polish_pyramid_wreck import Hole  # noqa: E402

AX = live.AXIS
LIVE_TOP = 7.61                     # the live eye's crest (polish_disc_turret: the crown + 0.5)
# The hole blown through the crown: its middle (a little below and right of the eye's), radii, the funnel's rings
# (z, scale) from its floor up, the jag.
HOLE_CENTRE = (AX.x + 0.25, AX.y + 0.05)
HOLE_RADII = (3.4, 3.0)
HOLE_RINGS = [(2.4, 0.72), (4.4, 0.86), (6.2, 0.97), (7.4, 1.04), (12.0, 1.12)]
HOLE_JAG, HOLE_SEED = 0.32, 39.0
# The torn plates bent up at the rim: (from and to angle round the hole's middle, degrees; how far out they reach
# past the rim; how far they are bent up about their outer edge, degrees).
PETALS = [(98.0, 128.0, 1.25, 42.0), (160.0, 182.0, 1.0, 30.0)]
PETAL_THICK = 0.3
# Rubble deep in the pit: (centre, radii); the ember (centre, radii).
CHUNKS = [((AX.x - 0.9, AX.y + 0.5, 2.55), (0.9, 0.75, 0.45)), ((AX.x + 1.1, AX.y - 0.6, 2.5), (0.8, 0.7, 0.4)),
          ((AX.x + 0.2, AX.y + 1.4, 2.6), (0.7, 0.6, 0.4))]
EMBER = ((AX.x + 0.25, AX.y - 0.1, 2.4), (0.55, 0.45, 0.25))
# The gun snapped past its collar: a plane through (x, y, z) slanting by its normal (the part in front dropped).
SNAP = ((live.GUN_X, -8.55, live.GUN_Z), (0.18, -1.0, 0.32))
# The scorch: strongest at the hole's rim, falling off over the dome.
BURN_REACH = 2.6


def burn(co):
    d = HOLE.d(co.x, co.y)
    rim = math.exp(-((d - 1.0) * HOLE_RADII[0] / BURN_REACH) ** 2 * 2.2)
    # (the slope down to the lower right darker, as painted)
    side = max(0.0, min(1.0, ((co.x - HOLE.centre.x) - (co.y - HOLE.centre.y)) / 6.0))
    return rim * (0.62 + 0.4 * side + 0.16 * wk.perlin(co.x * 0.7 + 4.1, co.y * 0.7 - 2.3, co.z * 0.3))


HOLE = Hole(HOLE_CENTRE, HOLE_RADII, 2.0, HOLE_SEED, HOLE_JAG, 0.9)


def petal(name, hit, a0, a1, reach, lift, mat_):
    """A torn plate of the dome at the hole's rim: the dome's surface between angles a0 and a1 (degrees, round the
    hole's middle) from the rim out by reach (hit: the uncut dome's surface), thickened downwards, then bent up about
    its outer edge by lift degrees (its inner, torn edge rising)."""
    cx, cy = HOLE.centre.x, HOLE.centre.y
    na, nr = 6, 3
    top, bottom = [], []
    for i in range(na + 1):
        a = math.radians(a0 + (a1 - a0) * i / na)
        r0 = HOLE.radius(a) * 1.02
        for j in range(nr + 1):
            r = r0 + reach * j / nr * (1.0 - 0.25 * abs(2 * i / na - 1) ** 2)
            x, y = cx + r * math.cos(a), cy + r * math.sin(a)
            h = hit(x, y)
            p, n = (h[0], h[1]) if h else (Vector((x, y, 6.0)), Vector((0, 0, 1)))
            top.append(p + n * 0.03)
            bottom.append(p - n * PETAL_THICK)
    count = len(top)
    at = lambda i, j: i * (nr + 1) + j  # noqa: E731
    faces = []
    for i in range(na):
        for j in range(nr):
            faces.append((at(i, j), at(i + 1, j), at(i + 1, j + 1), at(i, j + 1)))
            faces.append(tuple(count + v for v in (at(i, j + 1), at(i + 1, j + 1), at(i + 1, j), at(i, j))))
    ring = [at(i, 0) for i in range(na + 1)] + [at(na, j) for j in range(1, nr + 1)] + \
        [at(i, nr) for i in range(na - 1, -1, -1)] + [at(0, j) for j in range(nr - 1, 0, -1)]
    for q in range(len(ring)):
        a, b = ring[q], ring[(q + 1) % len(ring)]
        faces.append((b, a, count + a, count + b))
    obj = k.mesh_object(name, [tuple(v) for v in top + bottom], faces, mat_)
    k.recalc_normals(obj)
    am = math.radians((a0 + a1) / 2)
    tangent = Vector((-math.sin(am), math.cos(am), 0.0))
    pivot = top[at(na // 2, nr)]
    obj.data.transform(Matrix.Translation(pivot) @ Matrix.Rotation(math.radians(lift), 4, tangent) @
                       Matrix.Translation(-pivot))
    return obj


def build():
    options = k.args()
    k.reset()
    m = live.materials(live.FRAMES[0][2])
    live.base_ring(m)
    live.dome(m)
    live.knob(m)
    live.gun(m)
    dome = bpy.data.objects["dome"]
    mk.apply(dome)
    hit = mk.surface([dome])
    # Torn plates of the dome bent up at the rim (the dome's bronze; the tallest reaching the live eye's crest).
    petals = [petal(f"petal{i}", hit, a0, a1, reach, lift, m["dome"]) for i, (a0, a1, reach, lift) in enumerate(PETALS)]
    dz = LIVE_TOP - wk.top_z(petals)
    for obj in petals:
        obj.data.transform(Matrix.Translation((0.0, 0.0, dz)))
    # The crown blown out: the funnel's walls and floor the socket's black-brown.
    cutter = HOLE.cutter("hole", HOLE_RINGS, m["socket"], step=0.35)
    mk.boolean(dome, cutter, "DIFFERENCE")
    mk.cleanup(dome, dissolve=0.0)
    # The gun snapped at a slant past its collar, the muzzle gone.
    for name in ("barrel", "muzzle"):
        obj = bpy.data.objects[name]
        mk.apply(obj)
        front = wk.split_piece(obj, SNAP[0], SNAP[1], m["muzzle"], name + "_gone")
        if front is not None:
            bpy.data.objects.remove(front)
        if not obj.data.polygons:
            bpy.data.objects.remove(obj)
    # Scorched round the hole (the petals stay bright: the pale lip the painting shows at the rim's back).
    scorch(dome, burn, levels=(0.42, 0.86))
    k.smooth(dome, 50)
    for obj in petals:
        mk.shade(obj, 35)
    # Rubble and a dull ember deep in the pit.
    char = k.material("discwreck_char", palette=0x10, metallic=0.0, roughness=0.95)
    for i, (centre, radii) in enumerate(CHUNKS):
        rock(f"chunk{i}", centre, radii, char, 7.0 + i)
    ember = ember_material(0x73, 0.22)
    rock("ember", EMBER[0], EMBER[1], ember, 3.3)
    wk.clip_below(mk.meshes())
    wk.finish("disc_turret_wreck", options, LIVE_TOP)


if __name__ == "__main__":
    build()
