"""The steel rings of the maces' chains in GAUNTLET and MACES (sheet A sprites 87, 125 and 127, 2x2 each; ground layer;
one frame each), polished (2026-10-21; they replace wave3_q_mace.py's chain_ring(), a plain torus painted dark
underneath). models.cfg: model chain_ring_s / chain_ring_m / chain_ring_l ... origin and sprite a 87 chain_ring_s
yaw=0, sprite a 125 chain_ring_m yaw=0, sprite a 127 chain_ring_l yaw=0 (all unchanged: no height=-4, so that the
rings stay at the height of the anchor's ball, CHAIN_Z, as the anchor and the mace do). No other enemy shows these
sprites. They are three sizes of one ring, none of them another's pixels mirrored, turned or in other ramps (ramp 0,
the greys, all three). No 4x upscale of them exists: modelled from the original pixels.

As the sprites draw them: rings seen from straight above, each a perfect annulus of the sprite's pixels (an annulus
covers each one's pixels exactly, overlap 1.0): A 87 the small one round (0.5, -0.5), 8.3 pixels out and 4.5 in
(columns 4-20, rows 6-22), A 125 the middle one round (0.5, -0.5), 10.5 out and 6.4 in (columns 2-22, rows 4-24), A
127 the large one round (0, 0), 11.8 out and 6.7 in (columns 0-23, rows 2-25), its bar the thickest; dark outlines
(shade 1) along both edges, the band between them shaded as a round bar lit from the upper left: lightest along its
middle at the upper left (shades 12-13), where the bar's outside faces the light, and on its inner side at the lower
right (shade 12), where its inside does; darkest on its outer edge at the lower right and its inner edge at the upper
left (3-5). Flat rings, then: an upright ring would be drawn as a bar.

How the levels place them (custom enemies of events 49-52, each ring an enemy of its own with linknum 61, 62, 63, the
"mace" 64): GAUNTLET's first chain hangs from the anchor (A 83 ... 123) down the screen to the skull chest, the
rings made one after the other where the chest came out, so they hang in a stack 14 pixels apart, the small one on
the anchor, the large one at the chest (its handle reaches up into it), overlapping their neighbours by 3-5 pixels;
then they swing sideways, each further than the one above it. Its second chain and MACES' run from the anchor to the
mace in a line 24-30 pixels apart (they don't touch) and circle round, each further out than the one before it. A
ring can't turn with the chain (yaw=0) and is seen from above whichever way the chain points: so the rings lie flat,
their middles at CHAIN_Z. Where the stacked rings overlap they cross like links of a chain: each is tilted TILT
degrees about the screen's vertical axis, the small and the large one with their left side raised, the middle one
with its right side raised, so that each passes over its neighbour on one side of the overlap and under it on the
other (in the overlap's middle the bars meet); drawn out across the screen by 1 / cos(TILT), they are round from
above again. Tilted so little, a ring looks flat from the game's camera (and the one raised on its right, towards the
sun, glints hardly more than its neighbours); in the line they don't touch.

Built as forged steel rings: a round bar, hammered a little flat (FLAT: its height across its width), bent into a
ring a little out of round (OUT_OF_ROUND) and forge-welded: the bar swells a little over WELD degrees of the ring
(WELD_SWELL); its surface hammered (HAMMER: gentle facets that break the glint up, seeded: every run gives the same
ring). Palette greys of ramp 0 as the sprites': the steel shade 10, glossy and metallic, with a little emission in
its own grey so that the side the game's sun doesn't reach doesn't read black; the underside 6.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the ground; the origin is
the sprite's centre (pixel 12, 14): column c is x = c + 0.5 - 12, row r is y = 13.5 - r. Each ring at its sprite's
middle, at the height CHAIN_Z (origin keeps it).

Replaces wave3_q_mace.py's chain_ring() and its three q.model("chain_ring_...") lines (its "A 87, 125, 127: the chain
rings" section) and the chain_ring lines of its docstring; its CHAIN_Z is then unused there (only chain_ring() read
it; polish_mace_anchor.py and this script define their own).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouette of each ring
against enemy_A.png, and how the stacked rings cross), --preview <prefix> (each ring's top and 3/4 views),
--only <name,...>.
"""
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402

CHAIN_Z = 14.0   # the chain's height (wave3_q_mace.py, polish_mace_anchor.py: the anchor's ball's middle)
TILT = 7.0       # degrees about the screen's vertical axis (each ring raised on the side RINGS gives)
FLAT = 0.92      # the bar's height across its width
# The rings: (name, sprite, middle (x, y), radius of the bar's middle line, the bar's half width, the side it is
# raised on (-1 left, 1 right), where its weld is (degrees from +X, counter-clockwise seen from above), the seed of
# its hammering).
RINGS = [
    ("chain_ring_s", 87, (0.5, -0.5), 6.4, 1.9, -1, 205.0, 87),
    ("chain_ring_m", 125, (0.5, -0.5), 8.45, 2.05, 1, -25.0, 125),
    ("chain_ring_l", 127, (0.0, 0.0), 9.25, 2.55, -1, 155.0, 127),
]
# How GAUNTLET's first chain stacks them: each ring's sprite below the small one's (for the crossing check).
STACK = {"chain_ring_s": 0.0, "chain_ring_m": -14.0, "chain_ring_l": -28.0}
AROUND, ACROSS = 112, 20         # segments round the ring and round the bar
OUT_OF_ROUND = 0.012             # the ring's radius varies by this part (twice round)
HAMMER = 0.022                   # the hammered facets' depth, a part of the bar's half width
WELD = 22.0                      # the weld's length round the ring, degrees
WELD_SWELL = 0.08                # how much thicker the bar is at the weld (a part of its half width)


def materials():
    def steel(name, index, metallic, roughness, glow=None):
        if glow:
            return k.material(name, palette=index, metallic=metallic, roughness=roughness,
                              emission=k.level_palette()[index], emission_strength=glow)
        return k.material(name, palette=index, metallic=metallic, roughness=roughness)
    return {
        "steel": steel("chain_steel", 0x0a, 0.75, 0.26, glow=0.06),
        "under": steel("chain_under", 0x06, 0.7, 0.34),
    }


def hammering(seed):
    """The hammered facets: a smooth field over (angle round the ring, angle round the bar), about -1 to 1."""
    rng = random.Random(seed)
    terms = [(rng.randint(9, 23), rng.randint(2, 4), rng.uniform(0, 2 * math.pi), rng.uniform(0, 2 * math.pi),
              rng.uniform(0.5, 1.0)) for _ in range(8)]
    total = sum(t[4] for t in terms)

    def field(t, s):
        return sum(a * math.sin(m * t + p) * math.cos(n * s + q) for m, n, p, q, a in terms) / total * 2.0
    return field


def angle_diff(a, b):
    """a - b in degrees, wrapped to -180..180."""
    return (a - b + 180.0) % 360.0 - 180.0


def ring(name, centre, radius, half, side, weld_at, seed, m):
    """The ring: a bar of half width `half` (FLAT of it high) round a circle of `radius` about centre (x, y), lying
    flat at CHAIN_Z, then tilted TILT degrees about the screen's vertical axis through its middle, its `side` raised."""
    rng = random.Random(seed)
    field = hammering(seed)
    round_phase = rng.uniform(0, math.pi)
    bm = bmesh.new()
    rows = []
    for i in range(AROUND):
        t = 360.0 * i / AROUND
        tr = math.radians(t)
        u = angle_diff(t, weld_at) / (WELD / 2)
        swell = WELD_SWELL * max(0.0, 1.0 - u * u) ** 1.5
        r_ring = radius * (1.0 + OUT_OF_ROUND * math.cos(2 * tr + round_phase))
        row = []
        for j in range(ACROSS):
            s = 2 * math.pi * j / ACROSS
            a = half * (1.0 + swell + HAMMER * field(tr, s))
            rho = r_ring + a * math.cos(s)
            row.append(bm.verts.new((centre[0] + rho * math.cos(tr), centre[1] + rho * math.sin(tr),
                                     CHAIN_Z + a * FLAT * math.sin(s))))
        rows.append(row)
    for i in range(AROUND):
        a, b = rows[i], rows[(i + 1) % AROUND]
        for j in range(ACROSS):
            jj = (j + 1) % ACROSS
            bm.faces.new((a[j], b[j], b[jj], a[jj]))
    # Drawn out across the screen by 1 / cos(TILT), then tilted about the vertical axis: from above round again.
    stretch = Matrix.Diagonal((1.0 / math.cos(math.radians(TILT)), 1.0, 1.0, 1.0))
    tilt = (Matrix.Translation((centre[0], centre[1], CHAIN_Z)) @ Matrix.Rotation(math.radians(-side * TILT), 4, "Y") @
            stretch @ Matrix.Translation((-centre[0], -centre[1], -CHAIN_Z)))
    bmesh.ops.transform(bm, matrix=tilt, verts=bm.verts)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.normal_update()
    for f in bm.faces:
        f.material_index = 1 if f.normal.z < -0.35 else 0
        f.smooth = True
    obj = mk._link(name, bpy.data.meshes.new(name), None)
    obj.data.materials.append(m["steel"])
    obj.data.materials.append(m["under"])
    bm.to_mesh(obj.data)
    bm.free()
    return k.smooth(obj, 60.0)


def crossings(objects):
    """How the stacked rings of the first chain cross: where both cover the same point seen from above, which one is
    on top, left and right of the overlap's middle (each should be over its neighbour on one side, under on the
    other)."""
    pairs = (("chain_ring_s", "chain_ring_m"), ("chain_ring_m", "chain_ring_l"))
    for upper, lower in pairs:
        if upper not in objects or lower not in objects:
            continue
        a, b = objects[upper], objects[lower]
        # The lower ring where the stack puts it, relative to the upper one.
        shift = Matrix.Translation((0, STACK[lower] - STACK[upper], 0))
        b.data.transform(shift)
        hit_a, hit_b = mk.surface([a]), mk.surface([b])
        counts = {"left": [0, 0], "right": [0, 0]}
        for ix in range(-40, 41):
            x = 0.5 + ix * 0.2
            for iy in range(-140, 1):
                y = iy * 0.2
                ha, hb = hit_a(x, y), hit_b(x, y)
                if ha is None or hb is None or abs(x - 0.5) < 0.6:
                    continue
                key = "left" if x < 0.5 else "right"
                counts[key][0 if ha[0].z > hb[0].z else 1] += 1
        b.data.transform(shift.inverted())
        for key in ("left", "right"):
            over, under = counts[key]
            print("stacked %s and %s, %s of the overlap: %s on top (%d points %s, %d %s)" % (
                upper, lower, key, upper if over > under else lower, over, upper, under, lower))


def preview(prefix, obj):
    """The top view and the three-quarter view, the ring lowered to the ground for the latter's framing."""
    mk.transform([obj], Matrix.Translation((0, 0, -CHAIN_Z)))
    mk.preview(prefix, [obj], size=(24, 28), scale=16, distance=0.8)
    mk.transform([obj], Matrix.Translation((0, 0, CHAIN_Z)))


def build():
    options = k.args()
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    sheet = os.path.join(options["check"], "enemy_A.png") if "check" in options else None
    k.reset()
    m = materials()
    built = {}
    for name, sprite, centre, radius, half, side, weld_at, seed in RINGS:
        if only and name not in only:
            continue
        obj = ring(name, centre, radius, half, side, weld_at, seed, m)
        built[name] = obj
        bpy.context.view_layer.update()
        for other in built.values():
            other.hide_render = other is not obj
        bpy.context.scene.view_settings.view_transform = "Standard"
        if sheet:
            mk.compare("%s (A %d)" % (name, sprite), mk.coverage([obj], 24, 28), k.sprite_mask(sheet, sprite))
        mk.report(name, [obj], os.path.join(out, name + ".glb"))
        if "preview" in options:
            preview(options["preview"] + name, obj)
    for obj in built.values():
        obj.hide_render = False
    if sheet:
        crossings(built)


if __name__ == "__main__":
    build()
