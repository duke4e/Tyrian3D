"""Slugs, shells, bombs, a throwing star and balls of the shots sheet, as their sprites are drawn.

- shot_rail_slug (sprite 72; 91 is the same slug flying down): Atomic RailGun, a grey slug with a
  pointed nose, two driving bands and a hot base
- shot_rail_shell (11): Atomic RailGun, a mauve bottle-necked shell with a black cap and two grooves
- shot_rail_canister (12): Atomic RailGun, a grey canister with a green glowing core behind a caged
  window and a yellow lamp on its shoulder
- shot_guided_bomb (19; 171 turned 45 degrees): Guided Bombs and Guided Micro Bombs, a squat
  steel-blue disc in four plates round a glowing red eye
- shot_poison_bomb (103): Poison Bomb, a capsule of green glowing poison between two brown caps
- shot_shuriken (109): Shuriken Field, a dark four-bladed throwing star with curved blades (spins)
- shot_steel_ball (126): Wild Ball, a polished steel ball
- shot_green_orb (214, 215, 216): Protron Z and Wild Ball, a glossy green marble
- shot_retroball (shots2 20), shot_retroball_s (shots2 1): RetroBall, a bright green marble

Run: Blender -b --factory-startup -P shots_objects.py -- [--only ...] [--sheets <dir>] [--preview <dir>]
     [--cfg <dir>]
"""
import math
import os
import sys

from mathutils import Matrix, Vector, noise

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shot_kit as sk  # noqa: E402
from shot_kit import model, s  # noqa: E402


# --- Atomic RailGun ---------------------------------------------------------------------------------------

@model("shot_rail_slug", ("shots", 72),
       [("shots", 72, 0, "", "Atomic RailGun"),
        ("shots", 91, 180, "", "an enemy's slug flying down")],
       note="grey slug, pointed nose, two driving bands, hot base")
def rail_slug():
    """Columns 4-7 (x = 0) inside a dark outline, rows 0-11: the nose (rows 0-4), the body with two
    dark bands (rows 5 and 9), a flat base (row 11)."""
    metal = sk.pal("rs_metal", 0x0a, metallic=0.6, roughness=0.2)
    pale = sk.pal("rs_pale", 0x0d, metallic=0.6, roughness=0.15)
    dark = sk.pal("rs_dark", 0x03, metallic=0.5, roughness=0.35)
    hot = sk.light("rs_hot", (255, 170, 80), 1.6)
    profile = [(-4.95, 1.7), (-4.8, 2.2), (-4.4, 2.45), (-2.9, 2.45), (-2.7, 2.2), (-2.3, 2.2), (-2.1, 2.45),
               (1.1, 2.45), (1.3, 2.2), (1.7, 2.2), (1.9, 2.45), (3.0, 2.45), (4.0, 2.25), (4.8, 1.8),
               (5.6, 1.2), (6.4, 0.6), (6.9, 0.0)]
    sk.body("rs_body", profile, [(-4.95, -2.8, metal), (-2.8, -2.0, dark), (-2.0, 1.2, metal), (1.2, 2.0, dark),
                                 (2.0, 3.6, metal), (3.6, 6.9, pale)], step=0.45, segments=14)
    s.sphere("rs_base", (0, -4.95, 0), (1.5, 0.12, 1.5), hot, 14, 4)


@model("shot_rail_shell", ("shots", 11), [("shots", 11, 0, "", "Atomic RailGun")],
       note="mauve bottle-necked shell, black cap")
def rail_shell():
    """Columns 3-7 (x = -0.5) inside a dark outline, rows 0-12: a black cap (rows 0-1), the neck and
    shoulder (rows 2-3), the body (rows 4-11) with dark grooves at rows 6 and 10."""
    x = -0.5
    metal = sk.pal("rsh_metal", 0x5a, metallic=0.55, roughness=0.22)
    pale = sk.pal("rsh_pale", 0x5d, metallic=0.55, roughness=0.18)
    dark = sk.pal("rsh_dark", 0x52, metallic=0.4, roughness=0.35)
    cap = sk.pal("rsh_cap", 0x50, metallic=0.3, roughness=0.15)
    profile = [(-5.3, 2.0), (-5.1, 2.6), (-4.7, 2.85), (-3.9, 2.85), (-3.7, 2.55), (-3.3, 2.55), (-3.1, 2.85),
               (0.1, 2.85), (0.3, 2.55), (0.7, 2.55), (0.9, 2.85), (2.6, 2.85), (3.2, 2.3), (3.6, 1.75),
               (4.8, 1.65), (5.1, 1.5), (5.4, 1.35), (6.3, 1.25), (6.8, 0.8), (7.0, 0.0)]
    sk.body("rsh_body", profile, [(-5.3, -3.8, metal), (-3.8, -3.0, dark), (-3.0, 0.2, metal), (0.2, 1.0, dark),
                                  (1.0, 3.0, pale), (3.0, 5.2, metal), (5.2, 7.0, cap)], x=x, step=0.45, segments=14)
    s.lathe_y("rsh_rim", [(-5.35, 2.4), (-5.25, 2.95), (-4.85, 2.95), (-4.75, 2.6)], dark, x=x, segments=16)


@model("shot_rail_canister", ("shots", 12), [("shots", 12, 0, "", "Atomic RailGun")],
       note="grey canister, green glowing core in a caged window, yellow lamp")
def rail_canister():
    """Columns 3-8 (x = 0), rows 1-12: a rounded cap (rows 1-2), the shoulder with a yellow lamp
    (rows 3-4), a dark groove (row 5), a bright ring (row 6), the green window (rows 7-9), a bright
    ring (row 10), a dark groove (row 11), the base ring (row 12)."""
    grey = sk.pal("rc_grey", 0x0a, metallic=0.55, roughness=0.22)
    pale = sk.pal("rc_pale", 0x0e, metallic=0.55, roughness=0.15)
    dark = sk.pal("rc_dark", 0x04, metallic=0.4, roughness=0.4)
    core = sk.pal("rc_core", 0x27, metallic=0.1, roughness=0.08, glow=(50, 230, 70), strength=0.35)
    lamp = sk.pal("rc_lamp", 0x7c, metallic=0.1, roughness=0.2, glow=(255, 215, 60), strength=2.0)
    profile = [(-6.0, 2.2), (-5.8, 2.75), (-5.2, 2.9), (-4.85, 2.9), (-4.7, 2.55), (-4.3, 2.55), (-4.15, 2.95),
               (-3.0, 2.95), (-2.9, 2.6), (-0.1, 2.6), (0.0, 2.95), (0.95, 2.95), (1.1, 2.55), (1.9, 2.55),
               (2.05, 2.9), (3.5, 2.9), (4.0, 2.5), (4.3, 2.05), (5.3, 1.95), (5.8, 1.5), (6.1, 0.0)]
    sk.body("rc_body", profile, [(-6.0, -4.9, grey), (-4.9, -4.1, dark), (-4.1, -2.95, pale), (-2.95, -0.05, core),
                                 (-0.05, 1.0, pale), (1.0, 2.0, dark), (2.0, 4.2, grey), (4.2, 6.1, pale)],
            step=0.45, segments=14)
    # The cage over the window: four bars.
    for a in (35, 145, 215, 325):
        r = math.radians(a)
        p0 = (2.75 * math.cos(r), -3.0, 2.75 * math.sin(r))
        p1 = (2.75 * math.cos(r), 0.0, 2.75 * math.sin(r))
        s.tube("rc_bar", [p0, p1], 0.3, grey, 6)
    s.sphere("rc_lamp", (0, 3.3, 2.75), (0.95, 0.75, 0.5), lamp, 12, 6)


# --- Bombs ---------------------------------------------------------------------------------------------

@model("shot_guided_bomb", ("shots", 19),
       [("shots", 19, 0, "", "Guided Bombs, Heavy Guided Bombs"),
        ("shots", 171, 45, "", "Guided Micro Bombs: the same bomb turned")],
       note="squat steel-blue disc in four plates round a glowing red eye")
def guided_bomb():
    """Columns 1-10, rows 2-11 (centred): a squat disc, a cross of seams between four plates, a
    glowing red eye in a dark socket (columns 4-7, rows 5-8)."""
    steel = sk.pal("gb_steel", 0x39, metallic=0.55, roughness=0.22)
    pale = sk.pal("gb_pale", 0x3c, metallic=0.55, roughness=0.18)
    dark = sk.pal("gb_dark", 0x34, metallic=0.4, roughness=0.4)
    eye = sk.pal("gb_eye", 0x77, metallic=0.1, roughness=0.15, glow=(255, 50, 10), strength=1.4)
    hot = sk.light("gb_hot", (255, 210, 120), 2.6)
    # The underside and the rim.
    s.sphere("gb_belly", (0, 0, 0), (4.85, 4.85, 2.2), steel, 20, 6)
    s.hoop("gb_rim", (0, 0, 0.2), 4.65, 4.65, 0.45, dark, 32, 6)
    # Four plates on a dome, with gaps between them along the axes over a dark floor.
    def dome(x, y):
        return 0.2 + 2.35 * math.sqrt(max(0.0, 1 - (x * x + y * y) / 4.95 ** 2))
    s.sphere("gb_floor", (0, 0, 0.2), (4.7, 4.7, 2.3), dark, 20, 8)
    for q in range(4):
        a0, a1 = math.radians(90 * q + 6), math.radians(90 * q + 84)
        mid = math.radians(90 * q + 45)
        outline = [(0.75 * math.cos(mid), 0.75 * math.sin(mid))]
        for i in range(7):
            a = a0 + (a1 - a0) * i / 6
            outline.append((4.75 * math.cos(a), 4.75 * math.sin(a)))
        s.puff("gb_plate", outline, 0.0, 0.5, pale if q == 1 else steel, side=0.4, steps=3, power=3.0,
               z_fn=lambda x, y, z: z + dome(x, y) - 0.15)
    s.hoop("gb_socket", (0, 0, 2.55), 1.75, 1.75, 0.38, dark, 24, 6)
    s.sphere("gb_eye", (0, 0, 2.5), (1.55, 1.55, 0.8), eye, 16, 6)
    s.sphere("gb_hot", (-0.25, 0.25, 3.15), (0.7, 0.7, 0.3), hot, 12, 6)


def sk_circle(r, n, cx=0.0, cy=0.0):
    return [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


@model("shot_poison_bomb", ("shots", 103), [("shots", 103, 0, "", "Poison Bomb")],
       note="capsule of glowing green poison between two brown caps")
def poison_bomb():
    """Columns 2-10 (x = 0.5), rows 1-12: brown caps (rows 1-4 and 9-12), the green middle
    (rows 5-8) narrower."""
    x = 0.5
    brown = sk.pal("pb_brown", 0x16, metallic=0.15, roughness=0.6)
    pale = sk.pal("pb_pale", 0x1b, metallic=0.15, roughness=0.5)
    dark = sk.pal("pb_dark", 0x13, metallic=0.1, roughness=0.7)
    poison = sk.pal("pb_poison", 0x27, metallic=0.05, roughness=0.08, glow=(60, 220, 50), strength=0.35)
    squash = 0.72
    for sign in (1, -1):
        prof = [(1.9, 3.2), (2.05, 4.0), (2.4, 4.35), (3.5, 4.45), (4.6, 4.35), (5.3, 3.9), (5.8, 3.0),
                (6.05, 1.8), (6.15, 0.0)]
        pts = [(y, r) for y, r in prof] if sign > 0 else [(-y, r) for y, r in reversed(prof)]
        cap = s.lathe_y("pb_cap", pts, brown if sign > 0 else pale, x=x, squash=squash, segments=20)
        # Lumpy, like a stuffed sack.
        for v in cap.data.vertices:
            radial = Vector((v.co.x - x, 0, v.co.z))
            if radial.length > 1e-3:
                bump = noise.noise(Vector((v.co.x, v.co.y, v.co.z)) * 0.9 + Vector((sign * 3.0, 0, 0))) * 0.35
                v.co += radial.normalized() * bump
        for y in (3.0, 4.6):
            s.lathe_y("pb_rope", [(sign * y - 0.25, 4.3), (sign * y - 0.15, 4.62), (sign * y + 0.15, 4.62),
                                  (sign * y + 0.25, 4.3)], dark, x=x, squash=squash, segments=20)
    s.lathe_y("pb_glass", [(-2.2, 3.0), (-2.0, 3.4), (2.0, 3.4), (2.2, 3.0)], poison, x=x, squash=squash, segments=20)
    # Brown straps across the glass.
    for a in (40, 140, 220, 320):
        r = math.radians(a)
        p = (x + 3.45 * math.cos(r), 0, 3.45 * math.sin(r) * squash)
        s.tube("pb_strap", [(p[0], -2.3, p[2]), (p[0], 2.3, p[2])], 0.32, dark, 6)


# --- Shuriken -----------------------------------------------------------------------------------------------

@model("shot_shuriken", ("shots", 109), [("shots", 109, 0, "spin=24", "Shuriken Field (spins)")],
       note="polished steel four-bladed throwing star, curved blades")
def shuriken():
    """Four curved blades round a hub (the sprite's centre at x = 0, y = 0.5), each running out from
    the hub and hooking round clockwise. Polished steel lighter than the sprite's near-black greys (0x05,
    0x09: on every ground the spinning stars read as soot or bats, not as the player's shots), its rim
    bright."""
    steel = sk.pal("sh_steel", 0x0b, metallic=0.75, roughness=0.18)
    edge = sk.pal("sh_edge", 0x0e, metallic=0.85, roughness=0.1)
    dark = sk.pal("sh_dark", 0x04, metallic=0.4, roughness=0.5)
    cy = 0.5
    # One blade, pointing up and hooking right: its outline from the hub out along the outer edge
    # to the tip and back along the inner edge.
    outer = [(-1.3, 0.6), (-1.45, 2.6), (-1.1, 4.4), (-0.1, 5.6), (1.6, 6.25), (3.6, 6.2), (5.5, 5.5)]
    inner = [(5.5, 5.5), (3.8, 4.85), (2.3, 4.25), (1.35, 3.3), (1.0, 2.0), (1.15, 0.6)]
    outline = s.smooth_outline(outer + inner[1:], step=0.75)
    for q in range(4):
        blade = s.slab("sh_blade", outline, -0.38, 0.38, steel, bevel=0.3, segments=1)
        blade.data.transform(Matrix.Translation((0, cy, 0)) @ Matrix.Rotation(math.radians(-90 * q), 4, "Z"))
    hub = s.lathe_y("sh_hub", [(-0.6, 1.6), (-0.45, 2.05), (0.45, 2.05), (0.6, 1.6)], steel, segments=14)
    hub.data.transform(Matrix.Translation((0, cy, 0)) @ Matrix.Rotation(math.radians(90), 4, "X"))
    s.hoop("sh_hub_ring", (0, cy, 0.62), 1.45, 1.45, 0.25, edge, 24, 6)
    s.sphere("sh_hole", (0, cy, 0.55), (0.75, 0.75, 0.2), dark, 14, 4)


# --- Balls ----------------------------------------------------------------------------------------------------

@model("shot_steel_ball", ("shots", 126), [("shots", 126, 0, "", "Wild Ball")],
       note="polished steel ball")
def steel_ball():
    """Columns 0-10, rows 2-12: a ball centred at (-0.5, -0.5) inside a dark outline."""
    steel = sk.pal("sb_steel", 0x3b, metallic=0.5, roughness=0.12)
    s.sphere("sb_ball", (-0.5, -0.5, 0), (5.3, 5.3, 5.0), steel, 24, 12)


def marble(prefix, centre, radius, base, bright, glow, crescent=True):
    """A glossy green ball; crescent: a bright crescent glowing inside its lower right (the light
    through the glass, as the sprites draw it)."""
    glass = sk.pal(prefix + "glass", base, metallic=0.05, roughness=0.06, glow=glow, strength=0.2)
    cx, cy = centre
    s.sphere(prefix + "ball", (cx, cy, 0), (radius, radius, radius * 0.92), glass, 24, 12)
    if crescent:
        inner = sk.pal(prefix + "inner", bright, metallic=0.05, roughness=0.1, glow=glow, strength=0.8)
        pts = []
        for i in range(9):
            a = math.radians(-100 + 110 * i / 8)
            r = radius * 0.74
            z = radius * 0.92 * math.sqrt(1 - 0.74 ** 2)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a), z - 0.12))
        s.tube(prefix + "crescent", pts, [0.15, 0.5, 0.6, 0.5, 0.15], inner, 8, squash=0.45)


@model("shot_green_orb", ("shots", 214),
       [("shots", 214, 0, "", "Protron Z, Wild Ball, enemies' green orb"),
        ("shots", 215, 0, "", ""), ("shots", 216, 0, "", "")],
       note="glossy green marble")
def green_orb():
    marble("go_", (-0.5, 0.5), 5.4, 0xc5, 0xcb, (20, 200, 40))


@model("shot_retroball", ("shots2", 20), [("shots2", 20, 0, "", "RetroBall")],
       note="bright green marble")
def retroball():
    marble("rb_", (0.0, 0.0), 5.8, 0xc9, 0xcd, (30, 230, 60), crescent=False)


@model("shot_retroball_s", ("shots2", 1), [("shots2", 1, 0, "", "RetroBall")],
       note="bright green marble, smaller")
def retroball_s():
    marble("rbs_", (0.0, 0.0), 4.85, 0xc9, 0xcd, (30, 230, 60), crescent=False)


if __name__ == "__main__":
    sk.run()
