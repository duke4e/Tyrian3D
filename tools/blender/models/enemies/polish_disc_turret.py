"""The bronze disc turret of SAVARA, SAVARA Y, SOH JIN and DIG SITE (sheet F sprite 39, 2x2: 24 x 28
pixels; ground layer, 113 of them; its animation 39 41 41 41 39 39 39), polished (2026-10-18; it
replaces rounds.py's disc_turret(), a dark disc with a bronze ellipsoid and a pipe). models.cfg:
sprite f 39 disc_turret yaw=0 glow=8:0.3:121:-2.8:-1.8 (the eye's light), frame f 41 disc_turret_41.

As the 4x upscale draws it: a round turret of polished bronze sitting in the sand (columns 1-17 of
rows 4-18): a big pale dome, its top left catching the sun almost white (rows 5-9), on a narrow base
ring that shows lit along its lower right edge (rows 14-17); in the dome's crown a red eye (columns
7-11 of rows 9-13) in a dark socket; a stubby knob leaning out from the ring's upper right (columns
15-19 of rows 3-7); and a short gun pointing down the screen from under the dome (columns 9-12 of
rows 18-25), a thin barrel ending in a rounded muzzle. Frame 41 lights the eye up: its middle
white-yellow, the rest orange (the sprite's ramp 7 four shades lighter).

The sand round it and the dark shadows it and its knob cast to the lower right (rows 5-22, the
sprite's darkest browns and blacks) are the map's ground and the turret's own shadow: every pixel outside the turret
is the SAVARA map's sand tile (shape 12) under it, pixel for pixel. The model is the turret alone
and casts its shadow itself. Its plan is a little squarer than a circle (a superellipse), as the
sprite's outline is.

One model per frame, the same geometry: disc_turret (39) and disc_turret_41, the eye's colours and
glow changed.

Origin at the sprite's centre (pixel 12, 14); +Y up the sprite, +Z up from the ground (z = 0).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the
silhouette against the turret's own pixels, written below), --preview <prefix>.
"""
import math
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402

# The turret's own pixels in F 39 (the sand and the cast shadow left out): '#'.
TURRET = """
........................
........................
........................
...............####.....
......#############.....
....###############.....
...###############......
..###############.......
..###############.......
.################.......
.################.......
.################.......
.#################......
.#################......
.#################......
.################.......
.################.......
.###############........
..############..........
...###...####...........
.........###............
.........###............
.........###............
.........####...........
.........#####..........
.........#####..........
........................
........................
"""

AXIS = Vector((-2.8, 1.8))   # the turret's axis (columns 1-17, rows 4-18)
SQUASH = (1.0, 0.965)        # its plan a little wider than deep,
PLAN_POWER = 2.2             # and a little squarer than a circle, as the sprite's outline
SEGMENTS = 80
RING_R = 8.5                 # the base ring's outer radius
# The base ring from the ground up, (radius, z): its foot, a rounded rim, its top falling towards
# the dome.
RING = [(RING_R - 0.3, 0.0), (RING_R, 0.3), (RING_R, 0.9), (RING_R - 0.2, 1.3), (RING_R - 0.55, 1.55),
        (RING_R - 0.95, 1.6), (RING_R - 1.3, 1.45)]
# The dome: a superellipse of power DOME_POWER from DOME_R at DOME_Z up to its crown, where it
# turns over into a lip round the eye's socket; its foot is dark (the groove where it sits in the
# ring) up to FOOT_Z.
DOME_R, DOME_Z, DOME_H, DOME_POWER = 7.35, 1.0, 6.4, 2.2
FOOT_Z = 1.75
LIP_R = 2.55                 # where the dome meets the lip round the socket
EYE_R = 1.8                  # the eye's glass in the socket
RIVETS = 12                  # round the ring's top
# The knob at the upper right: a stubby post leaning out, from its foot by the ring to its top.
KNOB = (Vector((4.4, 7.6, 1.45)), Vector((6.0, 10.35, 3.7)), 1.45)
# The gun: its axis (x, z), from under the dome down the screen to the muzzle's end (y).
GUN_X, GUN_Z = -1.5, 2.05
GUN_FROM, MUZZLE_FROM, GUN_TO = -2.5, -9.2, -11.6
BARREL_R, MUZZLE_R = 1.05, 1.32

# The frames: (model, sprite, the eye's glass from its middle out: (palette index, emission)).
FRAMES = [
    ("disc_turret", 39, [(0x7c, 2.2), (0x79, 1.6), (0x76, 1.1), (0x73, 0.6)]),
    ("disc_turret_41", 41, [(0x7f, 3.0), (0x7d, 2.6), (0x7b, 2.1), (0x78, 1.5)]),
]
EYE_BANDS = (0.32, 0.58, 0.82)  # the glass's rings (fractions of its radius) where the colour changes


def ring_points(r, z, power=PLAN_POWER, centre=AXIS):
    pts = []
    for j in range(SEGMENTS):
        u, v = mk.superellipse_point(2 * math.pi * j / SEGMENTS, power)
        pts.append(Vector((centre.x + r * SQUASH[0] * u, centre.y + r * SQUASH[1] * v, z)))
    return pts


def radius_of(c, power=PLAN_POWER):
    return mk.plan_radius(c.x - AXIS.x, c.y - AXIS.y, SQUASH, power)


def materials(eye):
    glow = k.level_palette()
    m = {
        "ring": k.material("discturret_ring", palette=0x1a, metallic=0.5, roughness=0.3),
        "foot": k.material("discturret_foot", palette=0x13, metallic=0.3, roughness=0.55),
        "dome": k.material("discturret_dome", palette=0x1d, metallic=0.4, roughness=0.18),
        "lip": k.material("discturret_lip", palette=0x18, metallic=0.5, roughness=0.28),
        "socket": k.material("discturret_socket", palette=0x10, metallic=0.2, roughness=0.6),
        "rivet": k.material("discturret_rivet", palette=0x1c, metallic=0.6, roughness=0.25),
        "gun": k.material("discturret_gun", palette=0x1b, metallic=0.5, roughness=0.25),
        "muzzle": k.material("discturret_muzzle", palette=0x17, metallic=0.5, roughness=0.3),
    }
    for i, (index, strength) in enumerate(eye):
        m[("eye", i)] = k.material(f"discturret_eye_{index:x}", palette=index, roughness=0.12, emission=glow[index],
                                   emission_strength=strength)
    return m


def base_ring(m):
    rings = [ring_points(r, z) for r, z in RING]
    body = k.loft("ring", rings, m["ring"], start_point=(AXIS.x, AXIS.y, 0.0), end_point=(AXIS.x, AXIS.y, 1.45))
    k.smooth(body, 40)
    # Rivets round its top, where it is broadest.
    r = RING_R - 0.6
    for i in range(RIVETS):
        u, v = mk.superellipse_point(2 * math.pi * (i + 0.5) / RIVETS, PLAN_POWER)
        mk.ball(f"rivet{i}", (AXIS.x + r * SQUASH[0] * u, AXIS.y + r * SQUASH[1] * v, 1.55), (0.28, 0.28, 0.2),
                m["rivet"], 10, 5)


def dome(m):
    """The dome, squarish at its foot like the ring and round at its crown, the lip round the eye's
    socket and the socket's floor. Returns the crown's height."""
    rings = [ring_points(DOME_R + 0.15, 0.6)]
    steps = 18
    crown = DOME_Z + DOME_H * (1 - (LIP_R / DOME_R) ** DOME_POWER) ** (1 / DOME_POWER)
    for i in range(steps + 1):
        t = (math.pi / 2) * i / steps
        r = DOME_R * math.cos(t) ** (2 / DOME_POWER)
        if r <= LIP_R:
            break
        z = DOME_Z + DOME_H * math.sin(t) ** (2 / DOME_POWER)
        rings.append(ring_points(r, z, PLAN_POWER + (2.0 - PLAN_POWER) * min(1.0, 1.6 * i / steps)))
    for r, dz in ((LIP_R, 0.0), (LIP_R - 0.18, 0.3), (LIP_R - 0.45, 0.4), (LIP_R - 0.68, 0.18), (EYE_R + 0.05, -0.25),
                  (EYE_R - 0.15, -0.45)):
        rings.append(ring_points(r, crown + dz, 2.0))
    shell = k.loft("dome", rings, m["dome"], start_point=(AXIS.x, AXIS.y, 0.6),
                   end_point=(AXIS.x, AXIS.y, crown - 0.45))

    def pick(c, n):
        r = radius_of(c, 2.0)
        if r < EYE_R + 0.2:
            return m["socket"]
        if r < LIP_R + 0.05:
            return m["lip"]
        if c.z < FOOT_Z:
            return m["foot"]
        return None
    mk.paint(shell, pick)
    k.smooth(shell, 50)
    return crown


def eye(m, crown):
    """The eye's glass: a low dome in the socket, in rings of the sprite's shades, hottest in the middle."""
    floor = crown - 0.45
    profile = [(0.0, floor - 0.1), (EYE_R, floor - 0.1)]
    steps = 10
    for i in range(1, steps + 1):
        t = (math.pi / 2) * i / steps
        profile.append((EYE_R * math.cos(t), floor + 0.95 * math.sin(t)))
    glass = mk.lathe("eye", profile, tuple(AXIS), m[("eye", 3)], segments=40)
    mk.paint(glass, lambda c, n: m[("eye", sum(radius_of(c, 2.0) / EYE_R > b for b in EYE_BANDS))])
    k.smooth(glass, 60)


def knob(m):
    """A stubby post leaning out from beside the ring, its top rounded."""
    foot, top, r = KNOB
    axis = (top - foot).normalized()
    points = [foot + (top - foot) * t for t in (0.0, 0.2, 0.75)]
    radii = [r * 1.1, r, r]
    for i in range(1, 6):
        a = (math.pi / 2) * i / 6
        points.append(top - axis * r * (1 - math.sin(a)) * 0.9)
        radii.append(r * math.cos(a) + 0.05)
    post = mk.tube("knob", points, r, m["gun"], 16, radii=radii)
    k.smooth(post, 50)


def gun(m):
    """The barrel along -y from under the dome, a collar where it leaves the ring, the rounded
    muzzle round a dark bore."""
    def ring_at(y, r, z=GUN_Z):
        return [Vector((GUN_X + r * math.cos(2 * math.pi * j / 20), y, z + r * math.sin(2 * math.pi * j / 20)))
                for j in range(20)]
    barrel = k.loft("barrel", [ring_at(GUN_FROM, BARREL_R), ring_at(MUZZLE_FROM + 0.1, BARREL_R)], m["gun"])
    k.smooth(barrel, 50)
    edge = AXIS.y - SQUASH[1] * RING_R * 0.99
    collar = k.loft("collar", [ring_at(edge + 1.4, 1.32), ring_at(edge - 0.1, 1.32), ring_at(edge - 0.45, 1.12)],
                    m["muzzle"])
    k.smooth(collar, 40)
    rings = [ring_at(MUZZLE_FROM + 0.3, BARREL_R), ring_at(MUZZLE_FROM, MUZZLE_R - 0.08),
             ring_at(MUZZLE_FROM - 0.4, MUZZLE_R)]
    for i in range(1, 6):
        t = (math.pi / 2) * i / 6
        rings.append(ring_at(GUN_TO + 0.75 * (1 - math.sin(t)), 0.42 + (MUZZLE_R - 0.42) * math.cos(t)))
    muzzle = k.loft("muzzle", rings, m["muzzle"], end_point=(GUN_X, GUN_TO + 0.15, GUN_Z))
    mk.paint(muzzle, lambda c, n: m["socket"] if c.y < GUN_TO + 0.4 and math.hypot(c.x - GUN_X, c.z - GUN_Z) < 0.48
             else None)
    k.smooth(muzzle, 50)


def build_turret(eye_shades):
    m = materials(eye_shades)
    base_ring(m)
    crown = dome(m)
    eye(m, crown)
    knob(m)
    gun(m)


def turret_mask():
    return [[c == "#" for c in line] for line in TURRET.strip().splitlines()]


def build():
    options = k.args()
    out = mk.outdir(options)
    for name, sprite, eye_shades in FRAMES:
        k.reset()
        build_turret(eye_shades)
        parts = mk.meshes()
        if "check" in options:
            mk.compare("%s (F %d, the turret's own pixels)" % (name, sprite), mk.coverage(parts, 24, 28), turret_mask())
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        mk.report(name, parts, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, parts)


if __name__ == "__main__":
    build()
