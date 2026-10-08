"""Items of wave 3, batch AI (the coins sheet's remaining sprites), modelled as their sprites look; the kit is
enemies/wave3_ai_kit.py, the pixels enemies/wave3_ai_art.py. The fruit and the gem turn slowly (spin) as the other
loose items do; the things with letters or symbols (the tick, the hot dog) and the key keep still.

- strawberry (coins 75, 300 credits): a glossy red strawberry lying tip down the screen, yellow seeds in it, a
  green calyx of seven leaves and a stalk at its top.
- grapes_purple, grapes_green (coins 19 and 38 / 114: 750, 1000 and 500 credits): a bunch of grapes hanging from
  a curled brown twig; the sprites differ only by the grapes' colour (the twig stays brown), so two models.
- fruit_round (coins 37 and 113: a lime of 150 and an orange of 500 credits): a round citrus fruit with dimpled
  peel and a small navel; one model in the orange's shades that takes each sprite's colour (color=sprite).
- gem_pyramid_purple (coins 57, 2000 or 100 credits): gem_pyramid (wave2_e.py) cut in violet.

usage: Blender -b --factory-startup -P wave3_ai_items.py -- [--only name,name] [--preview <prefix>] [--check 1]
       [--stats 1]
"""
import math
import os
import sys

from mathutils import Matrix, Vector

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "enemies"))
import wave3_ai_kit as kit  # noqa: E402
from wave3_ai_kit import k, sh, w, pal, Painter  # noqa: E402

SMALL = (12, 14)


# --- Coins 75: the strawberry ------------------------------------------------------------------------------

STRAWBERRY = kit.frame("STRAWBERRY", 12, (6, 7))
# The berry's half-width and half-height along the screen (y): blunt at its tip, widest above the middle.
BERRY_PROFILE = [(-7.05, 0.2, 0.2), (-6.8, 1.9, 1.7), (-6.2, 3.1, 2.8), (-5.0, 4.4, 3.8), (-3.4, 5.4, 4.5),
                 (-1.4, 5.95, 4.9), (0.6, 6.05, 5.0), (2.2, 5.8, 4.8), (3.4, 5.1, 4.3), (4.2, 3.9, 3.4),
                 (4.7, 2.2, 2.0), (4.9, 0.2, 0.2)]


def berry_surface(x, y):
    """The top of the strawberry's body over (x, y) (None outside)."""
    for (y0, w0, h0), (y1, w1, h1) in zip(BERRY_PROFILE, BERRY_PROFILE[1:]):
        if y0 <= y <= y1:
            t = (y - y0) / (y1 - y0)
            wd, ht = w0 + (w1 - w0) * t, h0 + (h1 - h0) * t
            q = 1.0 - (x / wd) ** 2
            return None if q <= 0 else ht * math.sqrt(q)
    return None


@kit.model("strawberry", mask=lambda: STRAWBERRY.mask(), size=SMALL)
def strawberry():
    red = pal("straw_red", 0x76, metallic=0.05, roughness=0.22)
    seed = pal("straw_seed", 0x7b, metallic=0.1, roughness=0.35)
    leaf = pal("straw_leaf", 0x27, metallic=0.05, roughness=0.45)
    leaf_dark = pal("straw_leaf_dark", 0x24, metallic=0.05, roughness=0.5)
    stalk = pal("straw_stalk", 0x29, metallic=0.05, roughness=0.5)
    pts = k.profile([(y, wd, ht) for y, wd, ht in BERRY_PROFILE], step=0.45)
    rings = [k.ring(y, max(wd, 0.05), max(ht, 0.05), 24) for y, wd, ht in pts]
    body = k.loft("straw_body", rings, red)
    k.smooth(body, 70)
    # Seeds: little golden pips in a staggered pattern over the top, sunk into the skin.
    seeds = []
    for row, y in enumerate([-5.4, -3.6, -1.8, 0.0, 1.8]):
        shift = 0.0 if row % 2 == 0 else 1.3
        for x in [-5.0 + shift + 2.6 * j for j in range(5)]:
            z = berry_surface(x, y)
            if z is None or z < 2.0:
                continue
            nrm = Vector((x / 6.0 ** 2, 0.0, z / 5.0 ** 2)).normalized()
            seeds.append(kit.pip(f"straw_seed{len(seeds)}", (x, y, z), nrm, (0.3, 0.42, 0.2), seed, sink=0.08))
    kit.join(seeds, "straw_seeds")
    # The calyx: seven pointed leaves from the stalk's foot over the berry's top, spreading up the screen and
    # sideways (the sprite's green crown), and a short stalk.
    foot = Vector((0.0, 3.9, 4.0))
    leaves = []
    for j, (angle, length) in enumerate(((-100, 4.6), (-62, 5.4), (-25, 5.0), (8, 4.6), (40, 5.2), (75, 5.6),
                                          (112, 4.4))):
        a = math.radians(angle)
        d = Vector((math.sin(a), math.cos(a), 0.0))
        tip = foot + d * length
        tip.z = max(1.2, (berry_surface(tip.x, tip.y) or 0.0) + 0.3) if tip.y < 4.6 else 2.2
        mid = foot + d * length * 0.5
        mid.z = (berry_surface(mid.x, mid.y) or 2.6) + 0.55
        leaves.append(kit.limb(f"straw_leaf{j}", [tuple(foot), tuple(mid), tuple(tip)], [0.95, 0.85, 0.1],
                               leaf if j % 2 else leaf_dark, segments=8, squash=0.35))
    kit.join(leaves, "straw_calyx")
    kit.limb("straw_stalk", [(0.0, 3.9, 4.1), (0.2, 5.4, 4.6), (0.7, 6.6, 4.4)], [0.55, 0.45, 0.4], stalk,
             segments=8)


# --- Coins 19, 38, 114: the grapes ---------------------------------------------------------------------------

GRAPES = kit.frame("GRAPES_P", 12, (6, 7))


def grapes(ramp, name):
    berry = pal(f"{name}_berry", ramp * 16 + 9, metallic=0.1, roughness=0.2)
    berry_back = pal(f"{name}_berry_back", ramp * 16 + 6, metallic=0.1, roughness=0.3)
    twig = pal(f"{name}_twig", 0x16, metallic=0.05, roughness=0.6)
    twig_light = pal(f"{name}_twig_light", 0x18, metallic=0.05, roughness=0.6)
    f = GRAPES
    # The grapes the sprite draws, each a 2 x 2 ball lit at its top left (index 0x5c): front grapes there.
    front = []
    for r, row in enumerate(f.g):
        for c, val in enumerate(row):
            if val == 0x5c:
                front.append((c + 1 - f.ox, f.oy - (r + 1)))
    parts = []
    for i, (x, y) in enumerate(front):
        # The bunch bulges towards the camera in its upper middle.
        z = 2.0 + 1.3 * max(0.0, 1.0 - (x / 6.0) ** 2) * max(0.0, 1.0 - ((y - 1.0) / 7.0) ** 2)
        parts.append(kit.berry(f"{name}_g{i}", (x, y, z), 1.55, berry, segments=14, rings=8))
    # Grapes behind, filling the bunch between the front ones.
    back = [(-2.2, 2.6), (0.6, 2.4), (3.2, 2.4), (-1.0, 0.4), (1.6, 0.2), (-2.4, -1.4), (0.4, -1.8), (2.8, -1.2),
            (-0.6, -3.6), (1.8, -3.8), (0.0, -5.2), (-1.6, 4.0), (1.6, 4.0)]
    for i, (x, y) in enumerate(back):
        parts.append(kit.berry(f"{name}_b{i}", (x, y, 0.8), 1.5, berry_back, segments=12, rings=6))
    kit.join(parts, f"{name}_bunch")
    # The twig: curling from the top left over to the right and down, a stalk from it into the bunch.
    kit.limb(f"{name}_twig", [(-3.4, 4.6, 2.6), (-3.6, 5.7, 3.0), (-2.4, 6.6, 3.3), (-0.4, 6.5, 3.4),
                              (1.6, 5.7, 3.4), (3.4, 5.0, 3.2), (4.8, 3.9, 2.9), (5.3, 2.4, 2.6)],
               [0.45, 0.55, 0.62, 0.66, 0.62, 0.55, 0.5, 0.35], twig, segments=8)
    kit.limb(f"{name}_stalk", [(0.4, 6.3, 3.4), (0.6, 5.0, 3.6), (0.3, 3.4, 3.5)], [0.5, 0.45, 0.4], twig_light,
             segments=8)


@kit.model("grapes_purple", mask=lambda: GRAPES.mask(), size=SMALL)
def grapes_purple():
    grapes(5, "grapes_purple")


@kit.model("grapes_green", mask=lambda: GRAPES.mask(), size=SMALL)
def grapes_green():
    grapes(2, "grapes_green")


# --- Coins 37 and 113: the lime and the orange ----------------------------------------------------------------

ROUND = kit.frame("ORANGE", 12, (6, 7))


@kit.model("fruit_round", mask=lambda: ROUND.mask(), size=SMALL)
def fruit_round():
    peel = pal("fruit_peel", 0x7a, metallic=0.05, roughness=0.42)
    navel = pal("fruit_navel", 0x79, metallic=0.05, roughness=0.6)
    nub = pal("fruit_nub", 0x77, metallic=0.05, roughness=0.6)
    ball = w.sphere("fruit_ball", (0.0, 0.0, 0.0), (6.05, 6.05, 5.6), peel, 36, 18)
    kit.bumps(ball, 0.13, 0.7, seed=2.0, centre=(0.0, 0.0, 0.0))
    k.smooth(ball, 70)
    # The navel at its lower left (the sprite's small dark mark): a little star of creases round a nub.
    at, nrm = kit.ellipsoid_point((0.0, 0.0, 0.0), (6.05, 6.05, 5.6), -2.2, -2.6)
    marks = [kit.pip("fruit_nub", tuple(at), tuple(nrm), (0.42, 0.42, 0.3), nub, sink=0.0)]
    for j in range(5):
        a = 2 * math.pi * j / 5 + 0.3
        tangent = nrm.cross(Vector((math.cos(a), math.sin(a), 0.0))).normalized()
        p = at + tangent * 0.75
        marks.append(kit.pip(f"fruit_crease{j}", tuple(p), tuple(nrm), (0.18, 0.5, 0.06), navel, sink=0.04))
        k.recalc_normals(marks[-1])
    kit.join(marks, "fruit_navel")


# --- Coins 57: the violet pyramid gem ---------------------------------------------------------------------------

@kit.model("gem_pyramid_purple", mask=lambda: kit.frame("PYRAMID_P", 12, (6, 7)).mask(), size=SMALL)
def gem_pyramid_purple():
    """gem_pyramid's cut (wave2_e.py): a pyramid on a square turned 45 degrees (the sprite's diamond), its bright
    apex a small table, a shallow pyramid below the girdle; in the violet of the sprite."""
    body = k.material("pyramid_violet", palette=0x57, metallic=0.25, roughness=0.15, emission=(150, 110, 190),
                      emission_strength=0.12)
    light = k.material("pyramid_violet_table", palette=0x5b, metallic=0.2, roughness=0.1, emission=(215, 190, 240),
                       emission_strength=0.2)
    cx, cy = 0.5, -0.5
    r, t = 6.05, 1.1
    dirs = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    verts = [(cx + dx * t, cy + dy * t, 3.6) for dx, dy in dirs]
    verts += [(cx + dx * r, cy + dy * r, 0.45) for dx, dy in dirs]
    verts += [(cx + dx * r, cy + dy * r, -0.35) for dx, dy in dirs]
    verts.append((cx, cy, -2.9))
    faces = [(0, 1, 2, 3)]
    for i in range(4):
        j = (i + 1) % 4
        faces.append((i, 4 + i, 4 + j, j))
        faces.append((4 + i, 8 + i, 8 + j, 4 + j))
        faces.append((8 + i, 12, 8 + j))
    obj = k.mesh_object("gem", verts, faces)
    k.recalc_normals(obj)
    obj.data.materials.append(body)
    obj.data.materials.append(light)
    obj.data.polygons[0].material_index = 1
    k.bevel(obj, 0.18, 1)


# --- Coins 243: SOH JIN's golden key ----------------------------------------------------------------------------

KEY = kit.frame("KEY", 24, (12, 14))
SHADOW = (0xa0, 0xa1)  # the sprites' drop shadows (the game's light casts the models' own)


@kit.model("key_gold", mask=lambda: KEY.mask_where(lambda val: val not in SHADOW))
def key_gold():
    """A golden key lying with its bit up the screen: a round shaft from a looped bow to a bit of two prongs
    pointing left, each with a small lip; bevelled and rounded, polished gold."""
    gold = pal("key_gold", 0x19, metallic=0.75, roughness=0.28)
    gold_light = pal("key_gold_light", 0x1c, metallic=0.75, roughness=0.25)
    f = KEY
    # The key's pixels (gold and its black outline, no shadow), inflated into rounded metal; the bow's eye cut
    # through it (the sprite's dark gold in its lower middle).
    polys = kit.polys_where(f, lambda val, c, r: val not in SHADOW and (val >> 4 == 1 or (
        val == 0x01 and any((f.get(c + dc, r + dr) or 0) >> 4 == 1 for dc in (-1, 0, 1) for dr in (-1, 0, 1)))),
        smooth=2, epsilon=0.3, min_area=1.0, grow=-0.35)
    eye = sh.ellipse(0.9, -6.1, 2.3, 1.15, angle=-8.0, count=24)
    body = sh.inflate("key_body", polys + [eye[::-1]], gold, sh.round_profile(aspect=0.75, max_height=1.5),
                      bottom=0.55, base=0.0, rim=0.25, spacing=0.4, sigma=1.0)
    k.smooth(body, 50)
    # The shaft's top edge: a thin bright ridge along it.
    kit.limb("key_ridge", [(1.5, -2.2, 1.55), (1.5, 3.0, 1.62), (1.5, 9.4, 1.6)], [0.42, 0.42, 0.38], gold_light,
             segments=8, squash=0.6)


# --- Coins 245: the rainbow tick --------------------------------------------------------------------------------

CHECK = kit.frame("CHECK", 24, (12, 14))


@kit.model("check_rainbow", mask=lambda: CHECK.mask_where(lambda val: val not in SHADOW))
def check_rainbow():
    """A tick in raised, rounded strokes, glossy and glowing a little, coloured as the sprite's rainbow runs along
    it: red in the short stroke, orange and yellow round the bottom, then green, blue and violet up the long
    one; its sides a shade darker."""
    f = CHECK
    polys = kit.polys_where(f, lambda val, c, r: val not in SHADOW, smooth=2, epsilon=0.3, min_area=2.0,
                            grow=-0.3)
    bands = [(0x74, 0x72), (0x77, 0x75), (0x7a, 0x78), (0x7c, 0x7a), (0x29, 0x26), (0x2b, 0x28), (0x85, 0x82),
             (0x83, 0x80), (0x59, 0x56), (0x5b, 0x58)]
    tops = [pal(f"tick_{a:02x}", a, metallic=0.15, roughness=0.22, glow=0.35) for a, _ in bands]
    sides = [pal(f"tick_side_{b:02x}", b, metallic=0.15, roughness=0.35, glow=0.2) for _, b in bands]
    under = pal("tick_under", 0x01, metallic=0.1, roughness=0.6)
    tick = kit.relief("tick", polys, tops[0], sh.pillow_profile(2.6, 1.4, crown=0.5), bottom=0.0, base=0.0,
                      rim=0.4, spacing=0.4)
    # The rainbow's path: from the short stroke's top down to the bottom corner, then up the long stroke.
    path = [Vector((-6.6, 2.4)), Vector((-2.6, -5.0)), Vector((7.6, 7.6))]
    lengths = [(b - a).length for a, b in zip(path, path[1:])]
    total = sum(lengths)

    def along(x, y):
        best, best_t, run = None, 0.0, 0.0
        for (a, b), length in zip(zip(path, path[1:]), lengths):
            d = b - a
            u = max(0.0, min(1.0, (Vector((x, y)) - a).dot(d) / d.length_squared))
            dist = (a + d * u - Vector((x, y))).length
            if best is None or dist < best:
                best, best_t = dist, (run + u * length) / total
            run += length
        return best_t

    # Where each colour ends along the path (the short stroke red, the bottom orange and yellow ...).
    ends = [0.12, 0.2, 0.27, 0.34, 0.45, 0.55, 0.66, 0.77, 0.88, 1.01]

    def pick(c, nrm):
        if nrm.z < -0.5:
            return under
        t = along(c.x, c.y)
        i = next(j for j, e in enumerate(ends) if t < e)
        return sides[i] if abs(nrm.z) < 0.45 else tops[i]
    kit.paint_faces(tick, pick)


# --- Coins 153 155 157: the orbiting asteroid killer -------------------------------------------------------------

ORBITER = kit.frame("ORBITER", 24, (12, 14))


@kit.model("orbiter", mask=lambda: ORBITER.mask())
def orbiter():
    """A glowing ball of fire and two blue crystal points aiming at it from up and down the screen (its frames
    swing them round it: models.cfg turns the model with them, yaw=frames)."""
    fire = pal("orb_fire", 0x7a, metallic=0.0, roughness=0.35, glow=0.9)
    ice = pal("orb_point", 0xd9, metallic=0.35, roughness=0.15, glow=0.25)
    ball = w.sphere("orb_ball", (0.0, 0.0, 0.0), (6.05, 6.05, 5.8), fire, 32, 16)
    kit.bumps(ball, 0.25, 1.6, seed=4.0, centre=(0.0, 0.0, 0.0))
    k.smooth(ball, 70)
    for side in (1, -1):
        # A square pyramid: its base (8 wide) facing out, its point aiming at the ball.
        y0, y1, half, hz = 10.9 * side, 6.7 * side, 4.0, 2.3
        verts = [(-half, y0, hz), (half, y0, hz), (half, y0, -hz), (-half, y0, -hz), (0.0, y1, 0.0)]
        faces = [(0, 1, 2, 3), (0, 4, 1), (1, 4, 2), (2, 4, 3), (3, 4, 0)]
        point = k.mesh_object(f"orb_point{side:+d}", verts, faces, ice)
        k.recalc_normals(point)
        k.bevel(point, 0.3, 1)


# --- Coins 279: the red armour shell ----------------------------------------------------------------------------

RED_PLATE = kit.frame("RED_PLATE", 24, (12, 14))


@kit.model("red_keel_shell", mask=lambda: RED_PLATE.mask())
def red_keel_shell():
    """Enemy 560 (100 credits, armour 5): a red shell shaped like a T, a thick rolled bar across its top over a
    gold rod, a grooved keel running down to a blunt point, and two ribbed gold pods either side of the keel
    under the bar. Symmetric about x = 0.5, as the sprite."""
    ax = 0.5
    red = pal("rks_red", 0x47, metallic=0.3, roughness=0.32)
    red_light = pal("rks_red_light", 0x4a, metallic=0.3, roughness=0.28)
    groove = pal("rks_groove", 0x42, metallic=0.2, roughness=0.5)
    gold = pal("rks_gold", 0x17, metallic=0.7, roughness=0.3)
    gold_light = pal("rks_gold_light", 0x1b, metallic=0.7, roughness=0.25)
    # The gold rod behind the bar's top edge.
    w.lathe_axis("rks_rod", [(0.0, 0.01), (0.3, 1.0), (1.0, 1.35), (11.0, 1.35), (11.7, 1.0), (12.0, 0.01)], gold,
                 (ax - 6.0, 12.5, 3.2), (1, 0, 0), segments=16)
    # The rolled bar: a capsule across, a little flattened, its middle fuller.
    bar = w.lathe_axis("rks_bar", [(0.0, 0.01), (0.25, 1.6), (0.9, 2.7), (2.0, 3.3), (5.0, 3.5), (11.0, 3.7),
                                   (17.0, 3.5), (20.0, 3.3), (21.1, 2.7), (21.75, 1.6), (22.0, 0.01)], red,
                       (ax - 11.0, 8.7, 3.4), (1, 0, 0), segments=28, squash=0.95)
    # The bar's top lighter, as the sprite shades it.
    kit.paint_faces(bar, lambda c, nrm: red_light if nrm.z > 0.75 else None)
    # The keel: from under the bar down to its blunt point, round on top with a groove down its middle.
    sections = [(6.5, 4.4, 4.0), (3.0, 4.6, 4.4), (-1.0, 4.6, 4.2), (-5.0, 4.4, 3.8), (-8.0, 3.9, 3.3),
                (-10.5, 2.9, 2.6), (-12.5, 1.7, 1.8), (-13.6, 0.4, 0.8)]
    pts = k.profile([(yy, hw, hh) for yy, hw, hh in reversed(sections)], step=0.5)
    rings = [k.ring(yy, hw, hh, 28, x=ax, z=0.4, power=2.3, bottom=0.25) for yy, hw, hh in pts]
    keel = k.loft("rks_keel", rings, red)
    k.smooth(keel, 55)
    kit.limb("rks_groove", [(ax, 5.0, 4.45), (ax, 0.0, 4.55), (ax, -5.0, 4.15), (ax, -9.5, 3.0), (ax, -12.6, 1.8)],
             [0.38, 0.4, 0.38, 0.32, 0.2], groove, segments=8, squash=0.5)
    # The gold pods: ribbed, rounded, either side of the keel.
    for side in (-1, 1):
        cx = ax + side * 6.6
        pod = w.sphere(f"rks_pod{side:+d}", (cx, -0.6, 2.4), (2.4, 7.4, 2.6), gold, 20, 14)
        for vt in pod.data.vertices:  # ribs across it
            vt.co.x += side * 0.18 * math.cos((vt.co.y + 0.6) * 1.9) * max(0.0, vt.co.z - 1.0) / 3.0
        kit.paint_faces(pod, lambda c, nrm: gold_light if nrm.z > 0.8 else None)
        k.smooth(pod, 60)


# --- Coins 92: the HOT DOG pick-up ------------------------------------------------------------------------------

HOTDOG = kit.frame("HOTDOG", 24, (12, 14))
kit.PROTECT += ["hd_letters"]


def plate_ellipse(f):
    """The blue plate's ellipse from its pixels' moments: centre, semi-axes and angle (radians)."""
    pts = [(f.X(c), f.Y(r)) for r, row in enumerate(f.g) for c, val in enumerate(row)
           if val is not None and val >> 4 in (1, 3) or (val is not None and val >> 4 == 7 and 6 <= r <= 20)]
    n_ = len(pts)
    mx, my = sum(p[0] for p in pts) / n_, sum(p[1] for p in pts) / n_
    sxx = sum((p[0] - mx) ** 2 for p in pts) / n_
    syy = sum((p[1] - my) ** 2 for p in pts) / n_
    sxy = sum((p[0] - mx) * (p[1] - my) for p in pts) / n_
    angle = 0.5 * math.atan2(2 * sxy, sxx - syy)
    tr, det = sxx + syy, sxx * syy - sxy * sxy
    l1 = tr / 2 + math.sqrt(max(0.0, tr * tr / 4 - det))
    l2 = tr / 2 - math.sqrt(max(0.0, tr * tr / 4 - det))
    return (mx, my), 2 * math.sqrt(l1), 2 * math.sqrt(l2), angle


@kit.model("hot_dog", mask=lambda: HOTDOG.mask())
def hot_dog():
    """The HOT DOG pick-up (it arms the ship with the hot dog weapons): a hot dog in its bun on a blue oval plate,
    the words HOT above and DOG below in raised letters glowing in the sprite's fire shades on dark red backing.
    No spin: the letters stay readable."""
    f = HOTDOG
    blue = pal("hd_plate", 0x39, metallic=0.35, roughness=0.25)
    blue_rim = pal("hd_plate_rim", 0x3c, metallic=0.35, roughness=0.22)
    bun = pal("hd_bun", 0x1a, metallic=0.05, roughness=0.55)
    bun_light = pal("hd_bun_light", 0x1c, metallic=0.05, roughness=0.5)
    sausage = pal("hd_sausage", 0x75, metallic=0.1, roughness=0.3)
    mustard = pal("hd_mustard", 0x7c, metallic=0.05, roughness=0.4, glow=0.2)
    backing = pal("hd_backing", 0x72, metallic=0.2, roughness=0.5, glow=0.2)
    (cx, cy), a, b, angle = plate_ellipse(f)
    a, b = min(a, 12.6), min(b, 7.6)
    # The plate: a shallow dish, its rim raised and rounded.
    prof = [(0.0, 0.01), (0.02, 0.8), (0.35, 0.93), (1.1, 1.0), (1.45, 0.97), (1.4, 0.88), (0.85, 0.8),
            (0.75, 0.5), (0.75, 0.01)]
    plate = w.lathe_axis("hd_plate", prof, blue, (0.0, 0.0, 0.0), (0, 0, 1), segments=40, up=(0, 1, 0))
    plate.data.transform(Matrix.Translation((cx, cy, 0.0)) @ Matrix.Rotation(angle, 4, "Z") @
                         Matrix.Scale(a, 4, (1, 0, 0)) @ Matrix.Scale(b, 4, (0, 1, 0)))
    kit.paint_faces(plate, lambda c, nrm: blue_rim if c.z > 1.2 else None)
    k.smooth(plate, 50)
    # The hot dog across the plate, from its top right to its bottom left (the sprite's bun and sausage).
    top, bottom = Vector((3.2, 7.2, 0.0)), Vector((-4.6, -5.0, 0.0))
    d = (top - bottom).normalized()
    side = Vector((d.y, -d.x, 0.0))  # to the right of the dog (looking along it, up the screen)
    length = (top - bottom).length
    for i, off in enumerate((-1.25, 1.25)):
        start = bottom + side * off + Vector((0, 0, 2.2))
        kit.limb(f"hd_bun{i}", [tuple(start), tuple(start + d * length * 0.5 + Vector((0, 0, 0.5))),
                                tuple(start + d * length)], [1.9, 2.2, 1.9], bun if i else bun_light, segments=12,
                 squash=0.8, step=0.8)
    s0 = bottom - d * 1.0 - side * 0.5 + Vector((0, 0, 3.6))
    kit.limb("hd_sausage", [tuple(s0), tuple(s0 + d * (length + 2.0) * 0.5 + Vector((0, 0, 0.5))),
                            tuple(s0 + d * (length + 2.0))], [1.3, 1.45, 1.3], sausage, segments=10, step=0.8)
    zig = []
    for j in range(9):
        t = 0.1 + 0.8 * j / 8
        zig.append(tuple(s0 + d * (length + 2.0) * t + side * (0.55 if j % 2 else -0.55) +
                         Vector((0, 0, 1.45 + 0.5 * math.sin(math.pi * t)))))
    kit.limb("hd_mustard", zig, [0.32] * len(zig), mustard, segments=6)
    # The letters: HOT across the top, DOG across the bottom; the dark outline pixels a backing, the bright
    # ones raised on it.
    def letter(val, c, r):
        return val >> 4 == 7 and (r <= 5 or (r == 6 and c < 6) or r >= 21)
    back = kit.polys_where(f, letter, smooth=1, epsilon=0.2, min_area=0.5)
    plate_back = kit.relief("hd_letters_back", back, backing, sh.pillow_profile(0.8, 0.4), bottom=0.0, base=0.0,
                            rim=0.3, spacing=0.8, flat=True)
    lift = 2.6
    for obj in (plate_back,):
        obj.data.transform(Matrix.Translation((0, 0, lift)))
    bright = kit.polys_where(f, lambda val, c, r: letter(val, c, r) and (val & 15) >= 6, smooth=0, epsilon=0.05,
                             min_area=0.3, grow=0.12)
    fire = Painter("hd_fire", shades={7: (6, 8, 0xa)}, metallic=0.1, roughness=0.4,
                   glow={0x76: 0.6, 0x78: 0.8, 0x7a: 1.0})
    word = kit.relief("hd_letters", bright, fire(0x78), sh.pillow_profile(1.0, 0.35), bottom=0.0, base=lift + 0.6,
                      rim=0.2, spacing=0.5, sigma=0.6)
    kit.paint_sprite(word, f, fire, wall_steps=-2, keep=lambda val: val >> 4 == 7, blur=0)


if __name__ == "__main__":
    kit.run(items=True)
