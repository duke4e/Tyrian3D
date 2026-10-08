"""The missiles and rockets of the shots sheet, nose up the screen as their upright sprites are drawn;
the diagonal sprites of the same missile are the model turned (shot lines with yaw=).

- shot_missile (sprite 31): Missile Launcher, a slim grey missile: pointed nose, a bulging warhead, a
  dark collar, a thin neck and a finned tail, a glowing exhaust
- shot_missile_big (32), shot_missile_red (33): the Missile Launcher's bigger missiles, a twin-pronged
  seeker head, a bulging warhead and six fins (grey; red for 33)
- shot_hmissile (57): Heavy Missile Launcher, a fat grey rocket with a round nose, a glowing blue band
  and four red fins; shot_hmissile_diag (13, 14): the same for the Rear Heavy Missile Launcher's
  diagonal sprites
- shot_hmissile_steel (95): steel-blue rocket, a broad arrowhead warhead, a red-hot band, mauve fins;
  shot_hmissile_steel_g (15, 53 diagonal): with a plain pointed head and green fins
- shot_hmissile_green (76): green rocket, a bulbous head, a tan band, brown fins;
  shot_hmissile_green_p (96, 115 diagonal): with a purple band
The diagonal sprites (turned 45 degrees) draw the rocket 1.5 pixels further forward than the upright
ones: their models are moved so along their axis.
- shot_microsol (52): MicroSol option's long blue missile, canards with red lamps at the nose

Run: Blender -b --factory-startup -P shots_missiles.py -- [--only ...] [--sheets <dir>] [--preview <dir>]
     [--cfg <dir>]
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shot_kit as sk  # noqa: E402
from mathutils import Matrix  # noqa: E402
from shot_kit import model, s  # noqa: E402

FLAME_CORE = (255, 236, 170)
FLAME = (255, 120, 25)


def flame_mats():
    return sk.light("flame_core", FLAME_CORE, 3.0), sk.light("flame", FLAME, 2.2)


# --- The Missile Launcher's missiles -------------------------------------------------------------------

@model("shot_missile", ("shots", 31), [("shots", 31, 0, "", "Missile Launcher")],
       note="slim grey missile, glowing exhaust")
def missile():
    """Columns 4-8 (the axis on column 6, x = 0.5), rows 1-13: the nose (rows 1-3), the warhead (rows
    4-5), a dark collar (row 6), the neck (rows 7-8), the tail and its fins (rows 9-12)."""
    x = 0.5
    grey = sk.pal("ms_grey", 0x0a, metallic=0.5, roughness=0.25)
    pale = sk.pal("ms_pale", 0x0d, metallic=0.5, roughness=0.2)
    dark = sk.pal("ms_dark", 0x04, metallic=0.4, roughness=0.4)
    core, outer = flame_mats()
    profile = [(-6.1, 0.9), (-5.9, 1.25), (-5.0, 1.35), (-3.2, 1.35), (-2.6, 1.15), (-2.2, 0.85), (-1.0, 0.8),
               (0.0, 0.85), (0.4, 1.05), (1.0, 1.45), (1.8, 1.7), (2.6, 1.65), (3.4, 1.3), (4.4, 0.9),
               (5.3, 0.55), (6.0, 0.22), (6.3, 0.0)]
    sk.body("ms_body", profile, [(-6.1, 0.05, grey), (0.05, 0.75, dark), (0.75, 3.6, pale), (3.6, 6.3, grey)], x=x,
         grow=0.3)
    sk.bevel_ring("ms_ring", x, -2.4, 1.62, 0.35, 0.2, dark)
    for a in (0, 90, 180, 270):
        sk.fin("ms_fin", (1.3, -2.9, -5.9), (3.0, -4.3, -6.4), a, grey if a != 90 else pale, 0.4, x=x)
    sk.nozzle("ms_", x, -6.0, 1.05, dark)
    sk.flame("ms_flame", x, -6.55, -7.6, 0.7, core, outer)


BIG_PROFILE = [(-5.4, 1.2), (-5.2, 1.7), (-4.2, 1.95), (-2.4, 2.0), (-1.6, 2.15), (-1.1, 1.8), (-0.6, 1.35),
               (0.6, 1.35), (1.2, 1.5), (2.0, 2.15), (2.8, 2.45), (3.6, 2.35), (4.3, 1.8), (4.9, 1.2),
               (5.3, 0.6), (5.45, 0.0)]
RED_PROFILE = [(-5.6, 1.3), (-5.3, 1.8), (-4.0, 2.05), (-2.8, 2.0), (-1.9, 2.2), (-1.0, 2.9), (0.3, 3.15),
               (1.4, 2.9), (2.1, 2.3), (2.7, 2.15), (3.6, 2.0), (4.3, 1.5), (5.0, 1.1), (5.6, 0.5), (5.8, 0.0)]


def big_missile(prefix, x, fin_tip, hull_index, pale_index, dark_index, mid_index, profile=BIG_PROFILE,
                parts=((-5.4, 0.9, "hull"), (0.9, 1.6, "dark"), (1.6, 4.5, "pale"), (4.5, 5.45, "mid")), ring=-1.6,
                fin_back=-6.3, grow=0.0):
    """The bigger missile: two prongs at the nose (rows 0-1), the nose (row 2), a bulging warhead
    (rows 3-4), a collar (row 5), the waist (rows 6-7), the tail (rows 8-11) with six fins whose
    outer pair reaches row 12."""
    mats = {"hull": sk.pal(prefix + "hull", hull_index, metallic=0.5, roughness=0.25),
            "pale": sk.pal(prefix + "pale", pale_index, metallic=0.5, roughness=0.2),
            "mid": sk.pal(prefix + "mid", mid_index, metallic=0.5, roughness=0.25),
            "dark": sk.pal(prefix + "dark", dark_index, metallic=0.4, roughness=0.4)}
    core, outer = flame_mats()
    sk.body(prefix + "body", profile, [(y0, y1, mats[m]) for y0, y1, m in parts], x=x, grow=grow)
    sk.bevel_ring(prefix + "ring", x, ring, sk.interp(profile, ring) + grow + 0.12, 0.4, 0.25, mats["dark"])
    # The seeker's twin prongs.
    tip_y = profile[-1][0]
    for side in (-1, 1):
        s.lathe_axis(prefix + "prong", [(0, 0.45), (0.9, 0.38), (1.6, 0.22), (2.0, 0.0)], mats["mid"],
                     (x + side * 0.85, tip_y - 0.65, 0.15), (side * 0.12, 1, 0.05), segments=8)
    tail = profile[0][0]
    for a in (0, 180):
        sk.fin(prefix + "fin", (1.6, -1.8, tail + 0.4), (fin_tip, -3.6, fin_back), a, mats["hull"], 0.4, x=x)
    for a in (60, 120, 240, 300):
        sk.fin(prefix + "fin", (1.6, -2.2, tail + 0.4), (fin_tip - 0.5, -3.6, fin_back + 0.7), a,
               mats["pale"] if a < 180 else mats["hull"], 0.4, x=x)
    sk.nozzle(prefix, x, tail + 0.1, 1.15, mats["dark"])
    sk.flame(prefix + "flame", x, tail - 0.45, tail - 1.9, 0.95, core, outer)


@model("shot_missile_big", ("shots", 32), [("shots", 32, 0, "", "Missile Launcher")],
       note="bigger grey missile, twin-pronged seeker, six fins")
def missile_big():
    big_missile("mb_", 0.5, 4.0, 0x0a, 0x0d, 0x04, 0x08, grow=0.3)


@model("shot_missile_red", ("shots", 33), [("shots", 33, 0, "", "Missile Launcher")],
       note="the bigger missile in red")
def missile_red():
    """Wider than the grey one: the warhead bulges lowest (rows 5-7), the fins reach row 13."""
    big_missile("mr_", -0.5, 4.3, 0x46, 0x4a, 0x43, 0x48, RED_PROFILE,
                ((-5.6, -1.4, "hull"), (-1.4, 1.9, "pale"), (1.9, 2.5, "dark"), (2.5, 5.8, "mid")), ring=-2.5,
                fin_back=-6.8)


# --- The heavy missiles ----------------------------------------------------------------------------------

def heavy(prefix, head, hull_i, pale_i, dark_i, band_i, band_glow, band_bright_i, fin_i, fin_dark_i, fin_tip,
          shift=0.0):
    """A fat rocket on x = 0: its head (rows 1-5; head "round", "arrow" or "bulb"), a band (rows
    6-8), the body (row 9) and four fins (rows 10-13), a nozzle and a flame between the fins.
    shift moves it along its axis: the diagonal sprites draw the rocket 1.5 pixels further forward."""
    hull = sk.pal(prefix + "hull", hull_i, metallic=0.5, roughness=0.25)
    pale = sk.pal(prefix + "pale", pale_i, metallic=0.5, roughness=0.2)
    dark = sk.pal(prefix + "dark", dark_i, metallic=0.4, roughness=0.4)
    band = sk.pal(prefix + "band", band_i, metallic=0.3, roughness=0.18, glow=band_glow,
                  strength=0.6 if band_glow else 1.0)
    band_bright = sk.pal(prefix + "band_bright", band_bright_i, metallic=0.2, roughness=0.15, glow=band_glow,
                         strength=1.2 if band_glow else 1.0)
    fins = sk.pal(prefix + "fins", fin_i, metallic=0.4, roughness=0.3)
    fin_dark = sk.pal(prefix + "fin_dark", fin_dark_i, metallic=0.4, roughness=0.4)
    core, outer = flame_mats()
    tail = [(-5.9, 1.3), (-5.7, 1.8), (-5.0, 1.95), (-2.2, 1.95)]
    if head == "round":
        nose = [(1.2, 1.95), (3.0, 2.0), (4.3, 1.95), (5.2, 1.6), (5.8, 1.0), (6.1, 0.4), (6.2, 0.0)]
    elif head == "cone":
        nose = [(1.2, 1.95), (2.2, 2.2), (3.2, 2.1), (4.3, 1.75), (5.3, 1.25), (6.2, 0.65), (6.75, 0.2), (6.9, 0.0)]
    elif head == "arrow":
        nose = [(1.2, 1.95), (1.3, 3.3), (1.55, 3.85), (2.1, 3.55), (3.1, 3.0), (4.1, 2.55), (5.1, 2.0),
                (6.0, 1.35), (6.6, 0.75), (6.95, 0.25), (7.1, 0.0)]
    else:  # bulb
        nose = [(1.2, 1.95), (1.6, 2.6), (2.4, 2.95), (3.6, 2.9), (4.5, 2.5), (5.2, 1.85), (5.8, 1.2),
                (6.2, 0.5), (6.3, 0.0)]
    # The band sits a little proud of the hull.
    sk.body(prefix + "tail", tail + [(-1.9, 1.95), (1.0, 1.95)], [(-5.9, -1.9, hull)])
    s.lathe_y(prefix + "band", [(-2.05, 1.9), (-1.95, 2.12), (0.95, 2.12), (1.05, 1.9)], band, segments=14)
    s.lathe_y(prefix + "band_bright", [(-0.95, 2.1), (-0.85, 2.2), (-0.15, 2.2), (-0.05, 2.1)], band_bright,
              segments=14)
    s.lathe_y(prefix + "band_seam", [(-2.25, 1.85), (-2.15, 2.05), (-1.95, 2.05), (-1.85, 1.85)], dark, segments=14)
    s.lathe_y(prefix + "band_seam2", [(0.95, 1.85), (1.05, 2.05), (1.25, 2.05), (1.35, 1.85)], dark, segments=14)
    if head == "arrow":
        sk.body(prefix + "head", nose, [(1.2, 2.3, pale), (2.3, 7.0, hull)])
    elif head == "cone":
        sk.body(prefix + "head", nose, [(1.2, 3.4, hull), (3.4, 6.9, pale)])
    else:
        sk.body(prefix + "head", nose, [(1.2, 4.6, hull), (4.6, nose[-1][0], pale)])
    for a in (0, 90, 180, 270):
        sk.fin(prefix + "fin", (1.6, -2.6, -5.7), (fin_tip, -4.1, -6.6), a, fins if a != 270 else fin_dark, 0.45)
    sk.nozzle(prefix, 0.0, -5.75, 1.25, dark)
    sk.flame(prefix + "flame", 0.0, -6.3, -7.7, 1.05, core, outer)
    if shift:
        s.transform(s.meshes(), Matrix.Translation((0, shift, 0)))


@model("shot_hmissile", ("shots", 57), [("shots", 57, 0, "", "Heavy Missile Launcher")],
       note="fat grey rocket, glowing blue band, red fins")
def hmissile():
    heavy("hm_", "round", 0x09, 0x0d, 0x04, 0x96, (40, 70, 255), 0x9a, 0x74, 0x71, 3.9)


@model("shot_hmissile_diag", None,
       [("shots", 13, 315, "", "Rear Heavy Missile Launcher, up and left"),
        ("shots", 14, 45, "", "Rear Heavy Missile Launcher, up and right")],
       note="the grey rocket 1.5 pixels forward, as the diagonal sprites draw it")
def hmissile_diag():
    heavy("hm_", "round", 0x09, 0x0d, 0x04, 0x96, (40, 70, 255), 0x9a, 0x74, 0x71, 3.9, shift=1.5)


@model("shot_hmissile_steel", ("shots", 95), [("shots", 95, 0, "", "Heavy Missile Launcher")],
       note="steel-blue rocket, arrowhead warhead, red-hot band, mauve fins")
def hmissile_steel():
    heavy("hs_", "arrow", 0x39, 0x3b, 0x34, 0x77, (255, 70, 10), 0x7c, 0x56, 0x53, 3.9)


@model("shot_hmissile_steel_g", None,
       [("shots", 15, 315, "", "Rear Heavy Missile Launcher, up and left"),
        ("shots", 53, 45, "", "Rear Heavy Missile Launcher, up and right")],
       note="the steel-blue rocket with green fins and a plain pointed head, 1.5 pixels forward, as the diagonal "
            "sprites draw it")
def hmissile_steel_g():
    heavy("hg_", "cone", 0x39, 0x3b, 0x34, 0x77, (255, 70, 10), 0x7c, 0x27, 0x24, 3.9, shift=1.5)


@model("shot_hmissile_green", ("shots", 76), [("shots", 76, 0, "", "Heavy Missile Launcher")],
       note="green rocket, bulbous head, tan band, brown fins")
def hmissile_green():
    heavy("hn_", "bulb", 0x28, 0x2b, 0x24, 0xb7, None, 0xbc, 0x17, 0x14, 3.3)


@model("shot_hmissile_green_p", None,
       [("shots", 96, 315, "", "Rear Heavy Missile Launcher, up and left"),
        ("shots", 115, 45, "", "Rear Heavy Missile Launcher, up and right")],
       note="the green rocket with a purple band, 1.5 pixels forward as the diagonal sprites draw it")
def hmissile_green_p():
    heavy("hp_", "bulb", 0x28, 0x2b, 0x24, 0x56, None, 0x59, 0x16, 0x13, 3.3, shift=1.5)


# --- MicroSol ----------------------------------------------------------------------------------------------

@model("shot_microsol", ("shots", 52), [("shots", 52, 0, "", "MicroSol option")],
       note="long blue missile, canards with red lamps")
def microsol():
    """Columns 5-7 (x = 0.5), rows 1-12: the nose (rows 1-2), canards with red lamps (row 3), a long
    body (rows 4-9), four fins (rows 10-12)."""
    x = 0.5
    hull = sk.pal("mso_hull", 0x3a, metallic=0.5, roughness=0.25)
    pale = sk.pal("mso_pale", 0x3c, metallic=0.5, roughness=0.2)
    dark = sk.pal("mso_dark", 0x34, metallic=0.4, roughness=0.4)
    lamp = sk.pal("mso_lamp", 0x77, metallic=0.1, roughness=0.2, glow=(255, 40, 10), strength=2.0)
    core, outer = flame_mats()
    profile = [(-5.7, 1.0), (-5.5, 1.4), (-4.5, 1.55), (2.6, 1.55), (3.8, 1.5), (4.8, 1.2), (5.6, 0.7), (6.1, 0.0)]
    sk.body("mso_body", profile, [(-5.7, 3.2, hull), (3.2, 6.1, pale)], x=x)
    for ring_y in (-2.6, 0.6):
        sk.bevel_ring("mso_ring", x, ring_y, 1.5, 0.3, 0.2, dark)
    for a in (0, 180):
        sk.fin("mso_canard", (1.2, 4.1, 2.8), (2.8, 3.5, 2.9), a, hull, 0.35, x=x)
        side = 1 if a == 0 else -1
        s.sphere("mso_lamp", (x + side * 2.85, 3.2, 0.0), (0.55, 0.5, 0.45), lamp, 10, 5)
    for a in (0, 90, 180, 270):
        sk.fin("mso_fin", (1.3, -2.4, -5.4), (3.2, -4.2, -6.2), a, hull if a != 90 else pale, 0.36, x=x)
    sk.nozzle("mso_", x, -5.6, 0.95, dark)
    sk.flame("mso_flame", x, -6.15, -7.5, 0.8, core, outer)


if __name__ == "__main__":
    sk.run()
