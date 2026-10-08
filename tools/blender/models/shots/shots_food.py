"""The fun weapons' food on the shots sheets: bananas, hot dogs, an orange and pretzels.

- shot_banana (sprites 153, 154, 155): Banana Blast, a ripe banana, its stalk and blossom end dark;
  the frames are the banana turning, each sprite the model at its own yaw
- shot_hotdog (159, 160, 161): HotDog, a sausage with a zigzag of mustard in a split bun; 160 is
  upright, 159 and 161 lean left and right
- shot_orange (88): The Orange Juicer, an orange with a dimpled peel and its navel
- shot_pretzel (shots2 163-169): People Pretzels, a salted pretzel; the frames are it turning
- shot_pretzel_stick (shots2 120), shot_pretzel_stick_salt (shots2 121): Pretzel Missile, thin
  pretzel sticks (the second salted)
- shot_pretzel_rod (shots2 122), shot_pretzel_rod_big (shots2 127): Pretzel Missile, salted pretzel
  rods with scored crusts

Run: Blender -b --factory-startup -P shots_food.py -- [--only ...] [--sheets <dir>] [--preview <dir>]
     [--cfg <dir>]
"""
import math
import os
import random
import sys

from mathutils import Matrix, Vector, noise

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shot_kit as sk  # noqa: E402
from shot_kit import model, s, k  # noqa: E402


# --- Banana ----------------------------------------------------------------------------------------------

@model("shot_banana", ("shots", 153),
       [("shots", 153, 0, "", "Banana Blast (the banana turning)"),
        ("shots", 154, 90, "", ""),
        ("shots", 155, 180, "", "")],
       note="ripe banana, dark stalk and blossom end")
def banana():
    """As sprite 153 draws it: from its blossom end at the left (columns 0-2, rows 3-5) along the top
    (rows 2-4), bending down the right side (columns 9-11) to the stalk at the bottom (rows 11-12)."""
    yellow = sk.pal("ba_yellow", 0x7b, metallic=0.0, roughness=0.4)
    ripe = sk.pal("ba_ripe", 0x7c, metallic=0.0, roughness=0.35)
    brown = sk.pal("ba_brown", 0x72, metallic=0.0, roughness=0.6)
    path = [(-5.0, 3.1), (-3.5, 3.2), (-1.8, 3.25), (-0.3, 2.8), (0.9, 1.7), (1.9, 0.5), (2.8, -0.8), (3.5, -2.2),
            (3.95, -3.6), (4.1, -4.8)]
    pts = [Vector((x, y, 0.0)) for x, y in path]
    pts = s.catmull(pts, 0.45)
    shape = [(0.0, 1.05), (0.1, 1.6), (0.3, 2.1), (0.5, 2.35), (0.7, 2.05), (0.88, 1.5), (1.0, 0.95)]
    radii = []
    for i in range(len(pts)):
        t = i / (len(pts) - 1)
        radii.append(sk.interp(shape, t))
    body = s.tube("ba_body", pts, radii, yellow, 10, smooth_angle=45, squash=0.85)
    # A riper streak along the outer curve (the sprite's light pixels) and the dark ends.
    streak = [p + Vector((0, 0, 0.0)) for p in pts[2:-3]]
    for p in streak:
        p.z = 0.95
    s.tube("ba_streak", streak, [0.15, 0.55, 0.65, 0.55, 0.15], ripe, 6, squash=0.4)
    s.sphere("ba_blossom", (pts[0].x - 0.05, pts[0].y - 0.05, 0.0), (0.55, 0.55, 0.5), brown, 8, 5)
    stalk_dir = (pts[-1] - pts[-2]).normalized()
    s.tube("ba_stalk", [pts[-1] - stalk_dir * 0.3, pts[-1] + stalk_dir * 0.7], [0.5, 0.42], brown, 6)


# --- Hot dog -----------------------------------------------------------------------------------------------

@model("shot_hotdog", ("shots", 160),
       [("shots", 160, 0, "", "HotDog Front"),
        ("shots", 159, ("~", 325), "", "HotDog Rear, leaning left"),
        ("shots", 161, ("~", 35), "", "HotDog Rear, leaning right")],
       note="sausage with a zigzag of mustard in a split bun")
def hotdog():
    """Sprite 160: the bun's halves (columns 1-3 and 8-10, rows 1-12), the sausage between them
    (columns 4-7) poking out at both ends (rows 0 and 13), mustard along its top."""
    crust = sk.pal("hd_crust", 0x1b, metallic=0.0, roughness=0.55)
    crumb = sk.pal("hd_crumb", 0x1d, metallic=0.0, roughness=0.6)
    sausage = sk.pal("hd_sausage", 0x75, metallic=0.05, roughness=0.3)
    mustard = sk.pal("hd_mustard", 0x7c, metallic=0.0, roughness=0.35)
    for side in (-1, 1):
        cx = side * 3.25
        outline = s.superellipse(cx, 0.0, 1.95, 6.05, power=2.6, count=26)
        loaf = s.puff("hd_bun", outline, -1.6, 1.9, crust, side=0.25, steps=4, power=2.2, bottom=0.8)
        # Each half leans out a little, showing its cut face: the crumb along its inner edge.
        crumb_strip = s.tube("hd_crumb", [(cx - side * 1.05, y, 1.0) for y in (-5.0, -2.5, 0.0, 2.5, 5.0)],
                             [0.25, 0.6, 0.65, 0.6, 0.25], crumb, 8, squash=0.55)
        lean = Matrix.Translation((cx, 0, -1.6)) @ Matrix.Rotation(math.radians(-side * 14), 4, "Y") @ \
            Matrix.Translation((-cx, 0, 1.6))
        for obj in (loaf, crumb_strip):
            obj.data.transform(lean)
    s.lathe_y("hd_sausage", [(-7.0, 0.0), (-6.85, 0.8), (-6.4, 1.35), (-5.5, 1.65), (5.5, 1.65), (6.4, 1.35),
                             (6.85, 0.8), (7.0, 0.0)], sausage, z=0.9, squash=0.95, segments=14)
    zig = []
    for i in range(15):
        y = -5.6 + 11.2 * i / 14
        zig.append((0.75 * (1 if i % 2 else -1), y, 0.9 + 1.5))
    s.tube("hd_mustard", s.catmull(zig, 0.6), 0.34, mustard, 5, squash=0.6)


# --- Orange -----------------------------------------------------------------------------------------------

@model("shot_orange", ("shots", 88), [("shots", 88, 0, "", "The Orange Juicer")],
       note="orange with a dimpled peel and its navel")
def orange():
    """Columns 0-11, rows 1-12 (centred) inside a dark outline: a round orange."""
    peel = sk.pal("or_peel", 0x79, metallic=0.0, roughness=0.42)
    dark = sk.pal("or_dark", 0x75, metallic=0.0, roughness=0.6)
    ball = s.sphere("or_ball", (0, 0, 0), (5.75, 5.75, 5.3), peel, 28, 14, smooth_angle=80)
    for v in ball.data.vertices:
        n = Vector(v.co).normalized()
        dent = noise.noise(n * 3.1) * 0.12 + noise.noise(n * 9.0) * 0.1
        v.co = v.co + n * dent
    # The navel, lower left on the top, and the stalk's scar opposite it.
    d = Vector((-0.45, -0.45, 0.77)).normalized()
    p = Vector((d.x * 5.75, d.y * 5.75, d.z * 5.3))
    s.hoop("or_navel", (p.x, p.y, p.z - 0.15), 0.55, 0.55, 0.22, dark, 12, 5)
    d = Vector((0.5, 0.45, 0.74)).normalized()
    p = Vector((d.x * 5.75, d.y * 5.75, d.z * 5.3))
    s.sphere("or_scar", (p.x, p.y, p.z - 0.05), (0.45, 0.45, 0.2), dark, 8, 4)


# --- Pretzels ----------------------------------------------------------------------------------------------

PRETZEL = [  # The rope from one end round both loops to the other end (x, y, z); z lifts the strands that
    # cross over others (the ends over the belly, one arm over the other where they twist).
    (-5.0, -6.2, 0.5), (-3.4, -3.8, 0.8), (-2.4, -1.75, 1.0), (-1.8, 0.0, 0.5), (-0.8, 1.55, 0.1),
    (0.0, 2.4, -0.1), (0.7, 3.2, 0.0), (1.7, 4.7, 0.0), (3.4, 5.85, 0.0), (4.9, 4.9, 0.0), (5.25, 2.6, 0.0),
    (4.5, 0.3, 0.0), (2.8, -1.45, 0.0), (0.0, -2.2, 0.0), (-2.8, -1.45, 0.0), (-4.5, 0.3, 0.0),
    (-5.25, 2.6, 0.0), (-4.9, 4.9, 0.0), (-3.4, 5.85, 0.0), (-1.7, 4.7, 0.0), (-0.7, 3.2, 0.4), (0.0, 2.4, 0.9),
    (0.8, 1.55, 0.6), (1.8, 0.0, 0.5), (2.4, -1.75, 1.0), (3.4, -3.8, 0.8), (5.0, -6.2, 0.5)]


def salt(prefix, mat, points, rng, size=0.42):
    """Coarse salt: small tilted cubes on the given surface points."""
    for p in points:
        cube = k.box(prefix + "salt", (0, 0, 0), (size, size, size * 0.8), mat)
        cube.data.transform(Matrix.Translation(p) @ Matrix.Rotation(rng.uniform(0, 3.14), 4, "Z") @
                            Matrix.Rotation(rng.uniform(-0.5, 0.5), 4, "X"))


@model("shot_pretzel", ("shots2", 163),
       [("shots2", 163, 0, "", "People Pretzels (the pretzel turning)")] +
       [("shots2", 164 + i, 45 * (i + 1), "", "") for i in range(6)],
       note="salted pretzel")
def pretzel():
    """As sprite 163 draws it: two loops on top (holes at columns 2-3 and 8-9, rows 2-5), the ends
    crossing in the middle over a small hole (row 6-7) and over the belly (rows 8-9), down to the
    bottom corners."""
    dough = sk.pal("pz_dough", 0xb7, metallic=0.0, roughness=0.32)
    white = sk.pal("pz_salt", 0xbf, metallic=0.0, roughness=0.5)
    pts = s.catmull([Vector(p) for p in PRETZEL], 0.7)
    rope = s.tube("pz_rope", pts, 1.1, dough, 8, smooth_angle=60, squash=0.85)
    rng = random.Random(7)
    spots = [pts[i] + Vector((rng.uniform(-0.35, 0.35), rng.uniform(-0.35, 0.35), 0.95))
             for i in range(3, len(pts) - 3, 7)]
    salt("pz_", white, spots, rng)
    s.transform(s.meshes(), Matrix.Translation((0, 0.45, 0)))


def stick(prefix, x, y0, y1, radius, squash, dough_i, scored, salts, rng):
    """A pretzel stick or rod along Y from y0 to y1: a baked crust, scored with darker cuts (rods),
    and coarse salt on top."""
    dough = sk.pal(prefix + "dough", dough_i, metallic=0.0, roughness=0.35)
    dark = sk.pal(prefix + "cut", dough_i - 3, metallic=0.0, roughness=0.5)
    white = sk.pal(prefix + "salt", 0xbf, metallic=0.0, roughness=0.5)
    cap = min(radius * 0.9, 1.4)
    prof = [(y0, 0.0), (y0 + 0.05, radius * 0.55), (y0 + cap * 0.35, radius * 0.85), (y0 + cap, radius)]
    prof += [(y1 - cap, radius), (y1 - cap * 0.35, radius * 0.85), (y1 - 0.05, radius * 0.55), (y1, 0.0)]
    s.lathe_y(prefix + "body", prof, dough, x=x, squash=squash, segments=14 if radius > 2 else 10)
    if scored:
        # Diagonal cuts across the top, as the rods' crust is scored.
        for i in range(scored):
            yc = y0 + cap + (y1 - y0 - 2 * cap) * (i + 0.5) / scored
            a0, a1 = math.radians(40), math.radians(140)
            pts = []
            for j in range(7):
                a = a0 + (a1 - a0) * j / 6
                pts.append((x + radius * 0.98 * math.cos(a), yc + 0.9 * (j / 6 - 0.5), radius * squash * 0.98 * math.sin(a)))
            s.tube(prefix + "score", pts, 0.2, dark, 5, squash=0.6)
    spots = []
    for _ in range(salts):
        a = math.radians(rng.uniform(55, 125))
        yy = rng.uniform(y0 + cap * 0.8, y1 - cap * 0.8)
        spots.append(Vector((x + radius * math.cos(a), yy, radius * squash * math.sin(a) + 0.05)))
    salt(prefix, white, spots, rng, size=0.5 if radius > 2 else 0.42)


@model("shot_pretzel_stick", ("shots2", 120), [("shots2", 120, 0, "", "Pretzel Missile")],
       note="thin pretzel stick")
def pretzel_stick():
    """Columns 4-5 (x = -1), rows 1-10."""
    stick("ps_", -1.0, -4.0, 6.0, 1.0, 0.9, 0xb7, 0, 1, random.Random(3))


@model("shot_pretzel_stick_salt", ("shots2", 121), [("shots2", 121, 0, "", "Pretzel Missile")],
       note="salted pretzel stick")
def pretzel_stick_salt():
    """Columns 4-6 (x = -0.5), rows 1-10, three grains of salt."""
    stick("pss_", -0.6, -4.0, 6.0, 1.3, 0.9, 0xb7, 0, 4, random.Random(5))


@model("shot_pretzel_rod", ("shots2", 122), [("shots2", 122, 0, "", "Pretzel Missile")],
       note="salted pretzel rod")
def pretzel_rod():
    """Columns 3-8 (x = 0), rows 0-13, salt scattered over it."""
    stick("pr_", 0.0, -7.0, 7.0, 3.1, 0.8, 0xb8, 4, 8, random.Random(11))


@model("shot_pretzel_rod_big", ("shots2", 127), [("shots2", 127, 0, "", "Pretzel Missile")],
       note="thicker salted pretzel rod")
def pretzel_rod_big():
    """Columns 2-9 (x = 0), rows 0-13."""
    stick("prb_", 0.0, -7.0, 7.0, 3.85, 0.8, 0xb8, 4, 9, random.Random(13))


if __name__ == "__main__":
    sk.run()
