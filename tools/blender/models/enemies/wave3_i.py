"""Enemies of wave 3, batch I: the remaining enemy types of sheet ^ (enemy_x5e; models.cfg: x5e),
modelled as their sprites look (models.cfg: yaw=0). Objects the game draws from several sprites are
built whole and cut into the sprites' pieces, drawn at their own origins (models.cfg: origin):

- core_machine_* (^ 83, 85, 87, 89 above 121, 123, 125, 127): the grey and red machine of CORE,
  BRAINIAC, the ICE, LAVA and SIDE exits and UNDERDELI, 96 x 56 pixels: a red core column between
  two grey shoulders with chimneys, red chest plates, arms ending in upright posts, and legs and red
  claws reaching down. Built on its left half and mirrored (the sprite's right half is its shadow).
- deli_mite (^ 68): UNDERDELI's small purple crawler with a green window.
- deli_floor_eye (^ 45): a machine set in UNDERDELI's floor with a glowing orange eye.
- brick_crab_left, _mid, _right (^ 157, 159, 161): UNDERDELI's red-clawed machine in a brick wall.
- blue_gate_* (^ 16, 18 above 54, 56): the blue gate of BRAINIAC and the ICE levels.
- cruiser_rear, _mid, _nose (^ 198, 200, 201) and cruiser_rear_l, _mid_l, _nose_l (^ 206, 204, 203):
  UNDERDELI's blue cruiser flying sideways, to the right and (mirrored) to the left. 201 overlaps 200
  by 12 pixels (203 overlaps 204): each piece is the part of the ship its sprite shows.
- eyespy_lips_left, eyespy_lips_right (^ 196, 208): EYESPY's lips.
- brick_bulb_* (^ 153, 155 above 191, 193): a red bulb under a grey hood and two rings round red
  cylinders, in UNDERDELI's brick wall.
- rock_machine_* (^ 77, 79, 81 above 115, 117, 119): SURFACE's grey machine half buried in tan rock.
- spike_hand_* (^ 11, 13, 49 (1x1), 50, 52) and spike_hand_r_* (^ 92, 94, 129, 131, 133 (1x1)): the
  two spiked hands with blue eyes of SURFACE's boss.
- nosedrip_nostrils, nosedrip_tongue (^ 267, 269): NOSE DRIP's nose tip and tongue.

Parts are raised from regions of the sprites' pixels (wave3_i_art.py holds their palette indices) and
coloured in bands of the pixels' shades, with the helpers of wave3_i_kit.py.

usage: Blender -b --factory-startup -P wave3_i.py -- [--only name,name] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1]
       Blender -b --factory-startup -P wave3_i.py -- --whole core_machine,gate,crab,ring,cruiser,sand,hand,hand_r
       --preview <prefix>
"""
import math
import os
import sys

from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_i_art as art  # noqa: E402
import wave3_i_kit as w  # noqa: E402
from wave3_i_kit import k, model, pal  # noqa: E402

GREY = [(0.0, 3), (4.0, 5), (6.0, 7), (8.0, 9), (10.0, 11), (11.6, 12)]
RED = [(0.0, 3), (4.0, 5), (6.0, 7), (8.0, 9), (10.0, 11), (12.0, 13)]


def region(name, a, rows, chars, height, radius=1.2, base=0.0, crown=0.0, bands=None, z_fn=None, select=None,
           smooth=2, epsilon=0.5, grow=0.0, spacing=0.5, min_area=1.0, blur=2, relief=0.0, side=None, polys=None,
           coarse_from=2.0, rim=0.0, aspect=None, target=None):
    """A part raised over the pixels of `rows` whose char is in `chars`, coloured in `bands` of the
    shades of the pixels select(index, column, row) keeps (default: the part's own pixels)."""
    polys = polys or a.polys(rows, chars, smooth=smooth, epsilon=epsilon, min_area=min_area, grow=grow)
    if not polys:
        return None
    sel = select or (lambda v, c, r: rows[r][c] in chars)
    shade = a.field(sel, blur=blur)
    fn = z_fn
    if relief:
        def fn(x, y, z, z_fn=z_fn):
            z = z + relief * (shade(x, y) - 7.0) / 7.0 * min(1.0, (z - base) / max(radius, 0.5))
            return z_fn(x, y, z) if z_fn else z
    obj = w.raise_part(name, polys, height, radius, base=base, crown=crown, z_fn=fn, mat=bands[0][1],
                       spacing=spacing, band=coarse_from, rim=rim, aspect=aspect)
    w.lighten(obj)
    if target:
        w.decimate(obj, target * 0.6)
    w.paint_bands(obj, shade, bands, side=side)
    w.planar(obj, 0.8)
    return k.smooth(obj, 50)


# --- ^ 83 ... 127: the core machine ----------------------------------------------------------------

MACH = w.Art(art.MACHINE, 96, (48, 28))


def machine_label(v, c, r):
    """The machine's parts by pixel (left half; the right half is its mirror image)."""
    red = v >> 4 == 4
    s = v & 15
    lit = v >> 4 != 0 or s >= 2
    if 44 <= c <= 51 and 11 <= r <= 31 and red:
        return "K"  # the core column
    if red:
        if 13 <= c <= 28 and 18 <= r <= 21:
            return "a"  # the red strip along the arm
        if 29 <= c <= 44 and 16 <= r <= 28 and not (r >= 26 and c <= 39):
            return "R"  # the chest plate
        if 22 <= c <= 39 and 26 <= r <= 34:
            return "r"  # the lower plate
        if 34 <= c <= 43 and 35 <= r <= 48:
            return "W"  # the claw
        if 13 <= c <= 28 and 22 <= r <= 25:
            return "l"  # lights on the arm
        if 13 <= c <= 28 and 12 <= r <= 16:
            return "x"  # the slot in the shoulder
        return "-"
    # The chimney and the post are upright: the sprite draws them in the oblique view, their height
    # up the screen above their footprints. Those pixels ("^") are left out (no part, no hull).
    if 29 <= c <= 38 and 4 <= r <= 10:
        return "^"  # the chimney's height, as drawn
    if 5 <= c <= 10 and 19 <= r <= 24:
        return "^"  # the post's height, as drawn
    if not lit:
        return ","
    if 30 <= c <= 37 and 11 <= r <= 17 and s >= 2:
        return "C"  # the chimney's footprint
    if 14 <= c <= 41 and 7 <= r <= 18:
        return "T"  # the shoulder
    if 5 <= c <= 10 and 25 <= r <= 31:
        return "E"  # the post's footprint, at the arm's end
    if 11 <= c <= 31 and 20 <= r <= 30:
        return "A"  # the arm
    if 34 <= c <= 47 and 28 <= r <= 34:
        return "B"  # the block under the chest
    if 13 <= c <= 31 and 31 <= r <= 49:
        return "L"  # the leg
    return "M"  # machinery


def machine_whole():
    a = MACH
    X, Y = a.X, a.Y
    labels = a.rows(machine_label)
    left = [row[:48].ljust(96, ".") for row in labels]
    # The sprite is dark: its greys a shade darker than the usual bands.
    grey = w.ramp_bands("cm_grey", 0, [(0.0, 2), (4.0, 4), (6.0, 6), (8.0, 8), (10.0, 10), (11.6, 11)], metallic=0.5,
                        roughness=0.4)
    red = w.ramp_bands("cm_red", 4, RED, metallic=0.35, roughness=0.3)
    dark = w.ramp_bands("cm_dark", 0, [(0.0, 1), (1.6, 2), (2.6, 3), (3.6, 4), (4.6, 5), (6.0, 6)], metallic=0.25,
                        roughness=0.6)
    core = w.ramp_bands("cm_core", 4, [(0.0, 7), (8.6, 9), (9.6, 10), (10.6, 11), (11.6, 12), (12.6, 13),
                                       (13.6, 14), (14.6, 15)], metallic=0.2, roughness=0.25,
                        glow=lambda s: 0.15 * max(0, s - 9))
    steel = pal("cm_steel", 0x08, metallic=0.65, roughness=0.3)
    steel_light = pal("cm_steel_light", 0x0b, metallic=0.65, roughness=0.25)
    steel_dark = pal("cm_steel_dark", 0x04, metallic=0.55, roughness=0.4)
    parts = []
    # The hull: everything, low and dark, under the parts.
    hull_rows = ["".join("." if ch in ".^" else "#" for ch in row[:48]).ljust(96, ".") for row in labels]
    parts.append(region("hull", a, hull_rows, "#", 2.4, radius=0.9, bands=dark[1:4:2], select=lambda v, c, r: True,
                        smooth=2, epsilon=0.6, min_area=2.0, spacing=0.6, side=0, coarse_from=1.2))

    def slope(z0, z1, r0, r1):
        """A top rising from z0 at row r0 to z1 at row r1."""
        y0, y1 = Y(r0), Y(r1)
        return lambda x, y, z: z + z0 + (z1 - z0) * w.hk.smoothstep(y0, y1, y)

    # The shoulder with its red vent, and the chimney standing upright beside it, with a cap.
    parts.append(region("shoulder", a, left, "TC", 7.5, radius=0.6, crown=0.2, bands=grey, smooth=1, epsilon=0.9,
                        min_area=2.0, target=1500))
    parts.append(region("vent", a, left, "x", 5.6, radius=0.4, bands=red, smooth=1, epsilon=0.3, min_area=0.5))
    parts.append(region("chimney", a, left, "C", 14.0, radius=0.7, crown=0.2, bands=grey, smooth=1, epsilon=0.9,
                        target=700))
    w.rounded_box("chimney_cap", (X(33.5), Y(14.0), 14.2), (8.6, 7.6, 0.9), steel_dark, bevel=0.35)
    w.rounded_box("chimney_mouth", (X(33.5), Y(14.0), 14.45), (5.2, 4.2, 0.6), pal("cm_soot", 0x01, metallic=0.1,
                                                                                    roughness=0.9), bevel=0.2)
    # The arm, the red strip along it, its red studs, the upright post at its end.
    parts.append(region("arm", a, left, "Al", 6.0, radius=0.6, crown=0.2, bands=grey, smooth=1, epsilon=0.9,
                        select=lambda v, c, r: left[r][c] == "A"))
    parts.append(region("strip", a, left, "a", 6.9, radius=0.7, crown=0.2, bands=red, grow=0.2))
    for c, r in ((15.5, 23), (21.0, 23)):
        w.rounded_box(f"stud{c}", (X(c), Y(r), 6.2), (1.6 if c < 20 else 1.0, 2.6, 1.0),
                      pal("cm_stud", 0x47, metallic=0.35, roughness=0.3), bevel=0.3)
    post = (X(8.0), Y(28.0))
    w.lathe("post", [(0.0, 3.0), (1.0, 3.0), (1.3, 2.6), (11.0, 2.6), (11.6, 1.9), (11.9, 0.4)], steel, axis="z",
            at=post, segments=20)
    for z in (3.4, 8.6):
        w.lathe(f"post_band{z}", [(z - 0.6, 2.75), (z + 0.6, 2.75)], steel_dark, axis="z", at=post, segments=20)
    # The red plates.
    parts.append(region("chest", a, left, "R", 9.5, radius=0.8, crown=0.5, bands=red, smooth=1, epsilon=0.8,
                        target=800))
    parts.append(region("plate", a, left, "r", 6.5, radius=0.6, crown=0.3, bands=red, smooth=1, epsilon=0.8))
    # Below the chest: the block and the axle across the middle.
    parts.append(region("block", a, left, "B", 7.0, radius=0.6, crown=0.2, bands=grey, smooth=1, epsilon=0.9))
    w.lathe("axle", [(X(39.5), 0.3), (X(39.8), 1.3), (X(47.99), 1.3)], steel_light, axis="x", at=(Y(32.0), 7.3),
            segments=16)
    # The leg and the red claw reaching down, and the machinery between them.
    parts.append(region("leg", a, left, "L", 6.0, radius=0.6, crown=0.2, bands=grey, smooth=1, epsilon=0.9,
                        z_fn=slope(0.0, -1.6, 32, 48)))
    parts.append(region("claw", a, left, "W", 5.4, radius=0.6, crown=0.3, bands=red, smooth=1, epsilon=0.8))
    parts.append(region("machinery", a, left, "M", 4.0, radius=0.5, crown=0.1, bands=dark, smooth=1, epsilon=0.9,
                        min_area=1.5))
    parts = [p for p in w.meshes()]
    w.mirror_copy(parts, 0.0)
    # The core column down the middle.
    region("core", a, labels, "K", 12.5, radius=3.0, crown=0.6, bands=core, epsilon=0.5, target=1800)
    w.sh.flat_bottom(w.meshes())


def machine_piece(x0, x1, y0, y1):
    machine_whole()
    w.piece(x0, x1, y0, y1)


w.WHOLES["core_machine"] = (machine_whole, (96, 56))
for name, sprite, box in (("core_machine_tl", 83, (-48, -24, 0, 28)), ("core_machine_tcl", 85, (-24, 0, 0, 28)),
                          ("core_machine_tcr", 87, (0, 24, 0, 28)), ("core_machine_tr", 89, (24, 48, 0, 28)),
                          ("core_machine_bl", 121, (-48, -24, -28, 0)), ("core_machine_bcl", 123, (-24, 0, -28, 0)),
                          ("core_machine_bcr", 125, (0, 24, -28, 0)), ("core_machine_br", 127, (24, 48, -28, 0))):
    model(name, [(sprite, True)])(lambda box=box: machine_piece(*box))


# --- ^ 68: the purple mite ------------------------------------------------------------------------

@model("deli_mite", [(68, False)], size=(12, 14))
def deli_mite():
    """UNDERDELI's small purple crawler on the ground: a round head with a green window split by a
    purple bar, a shoulder pod on each side, a bright collar and a tail tapering down the screen."""
    a = w.Art(art.S68, 12, (6, 7))
    X, Y = a.X, a.Y

    def label(v, c, r):
        if r >= 8:
            return "t"
        if 3 <= c <= 9 or r <= 1:
            return "h"
        return "s"
    rows = a.rows(label)
    purple = w.ramp_bands("mite", 5, [(0.0, 3), (4.0, 5), (6.0, 7), (8.0, 9), (10.0, 11), (11.6, 12)], metallic=0.35,
                          roughness=0.35)
    glass = pal("mite_glass", 0xc6, metallic=0.1, roughness=0.1, glow=0.9, color=(40, 230, 70))
    region("head", a, rows, "h", 4.4, radius=1.8, crown=0.5, bands=purple, smooth=2, epsilon=0.3, min_area=0.3,
           blur=1, spacing=0.35, coarse_from=None, select=lambda v, c, r: rows[r][c] == "h" and v & 15 > 1)
    region("pods", a, rows, "s", 3.2, radius=1.5, crown=0.2, bands=purple, smooth=2, epsilon=0.3, min_area=0.3,
           blur=1, spacing=0.35, coarse_from=None, select=lambda v, c, r: rows[r][c] == "s" and v & 15 > 1)

    def taper(x, y, z):
        return z * (0.45 + 0.55 * w.hk.smoothstep(Y(13.5), Y(8), y))
    region("tail", a, rows, "t", 3.6, radius=1.8, crown=0.2, bands=purple, smooth=2, epsilon=0.3, min_area=0.3,
           blur=1, spacing=0.35, z_fn=taper, coarse_from=None, select=lambda v, c, r: rows[r][c] == "t" and v & 15 > 1)
    # The window, its bar and the collar.
    w.ellipsoid("window", (X(6), Y(3.2), 4.75), (1.9, 1.75, 0.75), glass, 18, 9)
    w.rounded_box("window_bar", (X(6), Y(3.7), 5.3), (0.7, 2.2, 0.7), purple[4][1], bevel=0.25)
    w.ellipsoid("collar", (X(6), Y(8.2), 3.0), (2.6, 0.85, 0.9), purple[5][1], 16, 8)
    w.sh.flat_bottom(w.meshes())


# --- ^ 45: the floor eye ---------------------------------------------------------------------------

@model("deli_floor_eye", [(45, True)])
def deli_floor_eye():
    """A machine standing on UNDERDELI's dark floor (none of the floor is modelled: the map draws
    it): two upright ribbed pillars (the sprite draws them in the oblique view, rows 2-10; here they
    stand on their footprints, rows 6-10, their height along z), a dark housing between them with a
    glowing orange eye on its sloping front, a rounded body in front of them and two feet below."""
    a = w.Art(art.S45, 24, (12, 14))
    X, Y = a.X, a.Y

    def label(v, c, r):
        s = v & 15
        if 11 <= r <= 16 and 2 <= c <= 19 and s >= 4:
            return "H"
        if 18 <= r <= 20 and (2 <= c <= 9 or 14 <= c <= 20) and s >= 4:
            return "S"
        return "-"
    rows = a.rows(label)
    grey = w.ramp_bands("feye_grey", 0, GREY, metallic=0.55, roughness=0.35)
    steel = pal("feye_steel", 0x09, metallic=0.6, roughness=0.3)
    steel_light = pal("feye_steel_light", 0x0b, metallic=0.6, roughness=0.25)
    steel_dark = pal("feye_steel_dark", 0x05, metallic=0.5, roughness=0.4)
    socket = pal("feye_socket", 0x02, metallic=0.3, roughness=0.6)
    # The pillars: upright, ribbed, on a plinth, with a cap. Symmetric about the eye (column 11).
    eye_x = X(11)
    for name, dx in (("pillar_left", -5.75), ("pillar_right", 5.75)):
        x, y = eye_x + dx, Y(8.5)
        w.rounded_box(f"{name}_plinth", (x, y, 0.7), (6.4, 5.6, 1.4), steel_dark, bevel=0.35)
        w.rounded_box(name, (x, y, 5.9), (5.4, 4.6, 10.0), steel, bevel=0.9, segments=3)
        for i, rx in enumerate((-1.3, 0.0, 1.3)):  # ribs down the front
            w.rounded_box(f"{name}_rib{i}", (x + rx, y - 2.2, 5.8), (0.7, 0.8, 8.4), steel_light, bevel=0.25)
        w.rounded_box(f"{name}_band", (x, y, 8.8), (5.8, 5.0, 0.8), steel_dark, bevel=0.25)
        w.rounded_box(f"{name}_cap", (x, y, 11.2), (6.2, 5.4, 1.2), steel_light, bevel=0.45)
    # The housing between the pillars, its front sloping back so the eye looks up and forward.
    hx0, hx1, hy0, hy1 = eye_x - 2.6, eye_x + 2.6, Y(10.5), Y(3.0)
    housing = k.mesh_object("housing", [
        (hx0, hy0, 0.0), (hx1, hy0, 0.0), (hx1, hy1, 0.0), (hx0, hy1, 0.0),
        (hx0, hy0, 4.0), (hx1, hy0, 4.0), (hx1, hy1, 9.4), (hx0, hy1, 9.4),
        (hx0, hy1 - 2.4, 9.4), (hx1, hy1 - 2.4, 9.4)],
        [(0, 3, 2, 1), (0, 1, 5, 4), (4, 5, 9, 8), (8, 9, 6, 7), (1, 2, 6, 9, 5), (0, 4, 8, 7, 3), (3, 7, 6, 2)],
        socket)
    k.recalc_normals(housing)
    k.bevel(housing, 0.4, 2)
    w.sh.apply_modifiers(housing)
    k.smooth(housing, 40)
    w.rounded_box("housing_cap", (eye_x, hy1 - 1.2, 9.6), (5.6, 3.0, 0.7), steel_light, bevel=0.3)
    # The eye: a glowing lens on the slope, facing up and forward.
    lens = pal("feye_lens", 0x77, metallic=0.0, roughness=0.15, glow=1.4, color=(255, 80, 10))
    hot = pal("feye_hot", 0x7d, metallic=0.0, roughness=0.1, glow=2.2, color=(255, 220, 90))
    tilt = Matrix.Rotation(math.atan2(5.4, hy1 - 2.4 - hy0), 4, "X")
    ey, ez = (hy0 + hy1 - 2.4) / 2, 6.7
    for name, radii, mat, lift in (("eye_rim", (2.2, 2.9, 0.6), steel_dark, 0.0), ("lens", (1.6, 2.3, 0.9), lens, 0.3),
                                   ("lens_hot", (0.7, 0.9, 0.5), hot, 0.95)):
        obj = w.ellipsoid(name, (0.0, 0.0, 0.0), radii, mat, 18, 9)
        obj.data.transform(Matrix.Translation((eye_x, ey, ez)) @ tilt @ Matrix.Translation((0, 0, lift)))
    # The body in front of the pillars, rising to them, and the two feet.

    def body_slope(x, y, z):
        return z + 2.2 * w.hk.smoothstep(Y(16.5), Y(11.0), y)
    region("body", a, rows, "H", 4.4, radius=1.2, crown=0.6, bands=grey, smooth=1, epsilon=0.6, z_fn=body_slope)
    region("feet", a, rows, "S", 2.8, radius=0.6, crown=0.2, bands=grey, smooth=1, epsilon=0.5)
    w.sh.flat_bottom(w.meshes())


# --- ^ 157, 159, 161: the brick crab ---------------------------------------------------------------

CRAB = w.Art(art.CRAB, 72, (36, 14))


def crab_whole():
    """UNDERDELI's red-clawed machine on its brick wall (the wall is the map's, not modelled): a grey
    dome with a red Y on it between two red balls, grey balls beside them, big red hooks at both ends
    and two small red pincers below, joined by steel arms."""
    a = CRAB
    X, Y = a.X, a.Y
    grey = w.ramp_bands("crab_grey", 0, GREY, metallic=0.55, roughness=0.35)
    red = w.ramp_bands("crab_red", 4, RED, metallic=0.35, roughness=0.3)

    def label(v, c, r):
        red_ = v >> 4 == 4
        s = v & 15
        if red_ and (c <= 14 or c >= 57):
            return "H"
        if red_ and r >= 16 and 26 <= c <= 47:
            return "p"
        return "-"
    rows = a.rows(label)
    # The dome and the red Y on it.
    cx, cy, rx, ry, rz = X(36), Y(8.3), 11.4, 6.4, 7.5
    shade = a.field(lambda v, c, r: v >> 4 == 0 and 24 <= c <= 48 and 1 <= r <= 13, blur=2)
    dome = w.ellipsoid("dome", (cx, cy, 0.0), (rx, ry, rz), grey[0][1], 36, 14)
    w.paint_bands(dome, shade, grey)

    def dome_z(x, y):
        q = 1 - ((x - cx) / rx) ** 2 - ((y - cy) / ry) ** 2
        return rz * math.sqrt(max(q, 0.0))
    ymark = a.rows(lambda v, c, r: "y" if v >> 4 == 4 and 32 <= c <= 41 and 2 <= r <= 12 else ".")
    region("emblem", a, ymark, "y", 0.45, radius=0.3, bands=red[2:], smooth=1, epsilon=0.35, min_area=0.4, blur=1,
           z_fn=lambda x, y, z: z + dome_z(x, y) - 0.15, spacing=0.4, coarse_from=None, target=700)
    # The red balls and the grey balls.
    redball = w.ramp_bands("crab_ball", 4, [(0.0, 5), (6.0, 7), (8.0, 9), (10.0, 11), (12.0, 13)], metallic=0.4,
                           roughness=0.25)
    for name, c, r, rr in (("ball_l", 27.0, 9.7, 4.4), ("ball_r", 45.5, 9.7, 4.3)):
        ball = w.ellipsoid(name, (X(c), Y(r), 2.6), (rr, 4.1, 4.4), redball[0][1], 28, 14)
        w.paint_bands(ball, a.field(lambda v, c_, r_: v >> 4 == 4 and abs(c_ - c) < 6 and 5 <= r_ <= 14, blur=1),
                      redball)
    steel = w.ramp_bands("crab_steel", 0, [(0.0, 5), (6.0, 7), (8.0, 9), (10.0, 11)], metallic=0.6, roughness=0.3)
    for name, c, r in (("knob_l", 18.0, 10.2), ("knob_r", 54.0, 10.2)):
        knob = w.ellipsoid(name, (X(c), Y(r), 1.2), (3.6, 3.4, 3.6), steel[0][1], 24, 12)
        w.paint_bands(knob, a.field(lambda v, c_, r_: v >> 4 == 0 and abs(c_ - c) < 5 and 6 <= r_ <= 14, blur=1),
                      steel)
    # The hooks, the pincers and the grey shoulders under the balls.

    def hook_slope(x, y, z):
        return z * (0.55 + 0.45 * w.hk.smoothstep(Y(22), Y(9), y))
    region("hooks", a, rows, "H", 5.5, radius=2.4, crown=0.4, bands=red, smooth=2, epsilon=0.4, z_fn=hook_slope,
           blur=1)
    region("pincers", a, rows, "p", 3.6, radius=1.6, crown=0.2, bands=red, smooth=2, epsilon=0.4, blur=1, target=900)
    for name, c, r in (("shoulder_l", 25.0, 15.0), ("shoulder_r", 46.0, 15.5)):
        joint_ball = w.ellipsoid(name, (X(c), Y(r), 1.4), (3.4, 2.6, 2.6), steel[0][1], 22, 11)
        w.paint_bands(joint_ball, a.field(lambda v, c_, r_: v >> 4 == 0 and abs(c_ - c) < 5 and 12 <= r_ <= 18,
                                          blur=1), steel)
    # No wall under it (the map draws the wall): the parts are joined by steel arms instead, from
    # the dome through the red ball and the grey knob to the hook, and from under the red ball by
    # the grey shoulder to the pincer.
    joint = pal("crab_joint", 0x05, metallic=0.6, roughness=0.35)
    for arm, leg in ((((31.0, 9.6, 3.2), (27.0, 9.7, 3.0), (18.0, 10.2, 2.8), (12.6, 9.4, 3.2)),
                      ((26.5, 12.0, 2.0), (25.0, 15.0, 2.2), (29.0, 18.8, 1.5))),
                     (((41.0, 9.6, 3.2), (45.5, 9.7, 3.0), (54.0, 10.2, 2.8), (59.4, 9.4, 3.2)),
                      ((45.5, 12.0, 2.0), (46.0, 15.5, 2.2), (43.0, 19.0, 1.5)))):
        side = "l" if arm[0][0] < 36 else "r"
        w.tube(f"arm_{side}", w.catmull([(X(c), Y(r), z) for c, r, z in arm], 0.5), 1.5, joint, segments=12)
        w.tube(f"leg_{side}", w.catmull([(X(c), Y(r), z) for c, r, z in leg], 0.5), 1.25, joint, segments=10)
    w.sh.flat_bottom(w.meshes())


w.WHOLES["crab"] = (crab_whole, (72, 28))
for name, sprite, box in (("brick_crab_left", 157, (-36, -12, -14, 14)), ("brick_crab_mid", 159, (-12, 12, -14, 14)),
                          ("brick_crab_right", 161, (12, 36, -14, 14))):
    model(name, [(sprite, True)])(lambda box=box: (crab_whole(), w.piece(*box)))


# --- ^ 16, 18 above 54, 56: the blue gate ---------------------------------------------------------

GATE = w.Art(art.GATE, 48, (24, 28))


def gate_whole():
    """The blue gate of BRAINIAC and the ICE levels: two tall organic blue arms with grey brackets
    sticking out at their middles and grey struts down their inner sides, joined at the bottom by a
    blue bowl with a spike rising in its middle over a small glowing emitter."""
    a = GATE
    X, Y = a.X, a.Y

    def label(v, c, r):
        ramp, s = v >> 4, v & 15
        if 16 <= r <= 21 and (c <= 11 or c >= 36) and (ramp != 3 or s <= 1):
            return "b"
        if ramp in (0, 5, 6) and s >= 2:
            if 43 <= r <= 47 and 20 <= c <= 28:
                return "e"
            return "s"
        if 36 <= r <= 44 and 20 <= c <= 27:
            return "S"
        if r >= 37:
            return "U"
        return "A"
    rows = a.rows(label)
    blue = w.ramp_bands("gate_blue", 3, [(0.0, 3), (3.5, 5), (5.5, 7), (7.5, 9), (9.5, 11), (11.5, 13)],
                        metallic=0.3, roughness=0.3)
    grey = w.ramp_bands("gate_grey", 0, GREY, metallic=0.6, roughness=0.3)
    dark = pal("gate_dark", 0x31, metallic=0.4, roughness=0.5)
    # A dark core under everything (the outline).
    hull = a.rows(lambda v, c, r: "#")
    region("core", a, hull, "#", 2.2, radius=0.8, bands=[(0.0, dark)], smooth=2, epsilon=0.5, min_area=2.0,
           select=lambda v, c, r: True, spacing=0.6, coarse_from=1.0)
    # The arms: tall rounded blue limbs, highest along their middles.
    for side, cols in ((-1, range(0, 24)), (1, range(24, 48))):
        arm_rows = ["".join(ch if (c in cols and ch == "A") else "." for c, ch in enumerate(row)) for row in rows]
        region(f"arm{side}", a, arm_rows, "A", 9.0, radius=4.2, crown=0.6, bands=blue, smooth=2, epsilon=0.5,
               select=lambda v, c, r: v >> 4 == 3, grow=0.3, rim=1.5, aspect=1.6, min_area=3.0, spacing=0.75,
               target=3000)
    region("bowl", a, rows, "U", 7.0, radius=3.6, crown=0.4, bands=blue, smooth=2, epsilon=0.5,
           select=lambda v, c, r: v >> 4 == 3, grow=0.3, rim=1.5, aspect=1.6, spacing=0.75, target=3000)
    region("spike", a, rows, "S", 8.5, radius=2.8, crown=0.4, bands=blue, smooth=2, epsilon=0.4, blur=1,
           select=lambda v, c, r: v >> 4 == 3, grow=0.2, rim=1.0, aspect=2.0, target=900)
    # The brackets, the struts and the emitter.
    region("brackets", a, rows, "b", 9.6, radius=0.8, crown=0.2, bands=grey, smooth=1, epsilon=0.6, grow=0.1,
           select=lambda v, c, r: rows[r][c] == "b" and v & 15 >= 3)
    region("struts", a, rows, "s", 6.0, radius=1.0, crown=0.3, bands=grey, smooth=2, epsilon=0.5, min_area=1.0,
           grow=0.2, rim=1.0, aspect=2.0, target=1600)
    glow = pal("gate_emitter", 0x0c, metallic=0.2, roughness=0.2, glow=0.8, color=(200, 230, 255))
    w.ellipsoid("emitter", (X(24.0), Y(45.6), 4.2), (2.4, 1.6, 1.4), glow, 16, 8)
    w.sh.flat_bottom(w.meshes())


w.WHOLES["gate"] = (gate_whole, (48, 56))
for name, sprite, box in (("blue_gate_tl", 16, (-24, 0, 0, 28)), ("blue_gate_tr", 18, (0, 24, 0, 28)),
                          ("blue_gate_bl", 54, (-24, 0, -28, 0)), ("blue_gate_br", 56, (0, 24, -28, 0))):
    model(name, [(sprite, True)])(lambda box=box: (gate_whole(), w.piece(*box)))


# --- ^ 198, 200, 201 and 206, 204, 203: the blue cruiser ------------------------------------------

def cruiser_whole(mirror=False):
    """UNDERDELI's blue cruiser flying sideways, its nose to the right (the mirror image to the left):
    a round engine at the rear, a ribbed waist with bulges above and below, the long hull with a big
    swept wing on each side, a second smaller pair of wings at the front and a long pointed nose."""
    a = w.Art(art.SHIP, 60, (30, 14))
    X, Y = a.X, a.Y
    cy, cz = 0.5, 5.0
    hull = pal("cruiser_hull", 0x37, metallic=0.55, roughness=0.3)
    hull_light = pal("cruiser_light", 0x3a, metallic=0.55, roughness=0.25)
    deep = pal("cruiser_deep", 0x34, metallic=0.5, roughness=0.35)
    teal = pal("cruiser_teal", 0xd9, metallic=0.5, roughness=0.25)
    pale = pal("cruiser_pale", 0xdc, metallic=0.5, roughness=0.2)
    dark = pal("cruiser_dark", 0x32, metallic=0.4, roughness=0.5)
    glow = pal("cruiser_glow", 0xdd, metallic=0.0, roughness=0.2, glow=1.2, color=(150, 230, 255))
    # The engine: a ball at the rear with a glowing core, a collar in front of it.
    w.ellipsoid("engine", (X(5.0), cy, cz), (4.4, 4.7, 4.0), hull, 28, 14)
    w.ellipsoid("engine_glow", (X(1.2), cy, cz), (1.3, 2.4, 2.1), glow, 14, 8)
    w.lathe("collar", [(X(8.5), 3.0), (X(9.0), 4.3), (X(11.0), 4.3), (X(11.5), 3.0)], deep, axis="x", at=(cy, cz),
            segments=24, squash=0.85)
    # The waist: rings and two bulges above and below.
    w.lathe("waist", [(X(10.0), 3.3), (X(12.0), 3.7), (X(14.0), 3.2), (X(16.0), 3.8), (X(18.0), 3.3), (X(20.5), 4.0)],
            hull, axis="x", at=(cy, cz), segments=24, squash=0.85)
    for side in (-1, 1):
        w.ellipsoid(f"bulge{side}", (X(12.6), cy + side * 5.8, cz - 0.6), (3.3, 2.9, 2.4), hull_light, 18, 9)
        w.ellipsoid(f"bump{side}", (X(17.2), cy + side * 6.4, cz - 0.9), (2.0, 1.9, 1.6), hull, 14, 7)
    # The hull.
    w.lathe("hull", [(X(19.5), 3.8), (X(22.0), 4.6), (X(30.0), 4.9), (X(38.0), 4.9), (X(42.0), 4.7), (X(46.0), 4.4),
                     (X(49.0), 3.8), (X(51.0), 2.9), (X(52.5), 1.6), (X(53.2), 0.5)], hull, axis="x", at=(cy, cz),
            segments=28, squash=0.8)
    w.lathe("hull_band", [(X(24.0), 4.85), (X(25.0), 5.0), (X(26.0), 4.85)], deep, axis="x", at=(cy, cz), segments=28,
            squash=0.8)
    # The ridge along the hull's top and the nose spike.
    w.tube("ridge", [(X(26.0), cy, cz + 3.6), (X(36.0), cy, cz + 3.7), (X(44.0), cy, cz + 2.8)], 0.8, hull_light, 10)
    w.tube("nose", [(X(44.0), cy, cz + 0.4), (X(50.0), cy, cz + 0.3), (X(55.6), cy, cz + 0.2)], [1.2, 1.0, 0.25], pale,
           12)
    # The wings: the big swept pair along the hull and the small pair at the front.

    def wing(name, outline, z0, z1, mat):
        for side in (-1, 1):
            pts = [(X(c), cy + side * h) for c, h in outline]
            if side < 0:
                pts = pts[::-1]
            obj = k.slab(f"{name}{side}", pts, z0, z1, mat, bevel_width=0.35)
            w.sh.apply_modifiers(obj)
            k.smooth(obj, 35)
    wing("wing", [(19.3, 4.0), (19.8, 8.0), (24.0, 9.2), (26.6, 12.6), (39.4, 12.6), (40.2, 10.5), (37.5, 4.0)],
         cz - 0.9, cz + 0.5, teal)
    wing("wing_top", [(21.0, 4.6), (21.6, 7.4), (25.2, 8.4), (27.6, 11.6), (37.6, 11.6), (38.0, 10.0), (35.5, 4.6)],
         cz + 0.5, cz + 1.1, deep)
    wing("fin", [(37.5, 4.0), (40.5, 8.5), (44.4, 12.4), (48.6, 12.4), (51.6, 10.0), (54.0, 7.0), (53.0, 4.0)],
         cz - 0.7, cz + 0.6, hull_light)
    wing("fin_top", [(39.5, 4.4), (42.0, 8.2), (45.0, 11.2), (48.2, 11.3), (50.8, 9.4), (52.4, 7.0), (51.4, 4.4)],
         cz + 0.6, cz + 1.1, hull)
    # A glowing slit along the hull's side, under the ridge.
    for side in (-1, 1):
        w.tube(f"slit{side}", [(X(28.0), cy + side * 2.6, cz + 3.0), (X(40.0), cy + side * 2.4, cz + 2.7)], 0.45,
               dark, 8)
    if mirror:
        w.mirror_all()


w.WHOLES["cruiser"] = (cruiser_whole, (60, 28))
for name, sprite, box, mirror in (("cruiser_rear", 198, (-30, -6, -14, 14), False),
                                  ("cruiser_mid", 200, (-6, 18, -14, 14), False),
                                  ("cruiser_nose", 201, (6, 30, -14, 14), False),
                                  ("cruiser_rear_l", 206, (6, 30, -14, 14), True),
                                  ("cruiser_mid_l", 204, (-18, 6, -14, 14), True),
                                  ("cruiser_nose_l", 203, (-30, -6, -14, 14), True)):
    model(name, [(sprite, True)])(lambda box=box, mirror=mirror: (cruiser_whole(mirror), w.piece(*box)))


# --- ^ 196, 208: the lips --------------------------------------------------------------------------

def lips(mirror=False):
    """EYESPY's lips, the corner of a mouth pointing left (208: right): a full upper and lower lip,
    parted along a dark line, glossy."""
    a = w.Art(art.LIPS, 24, (12, 14))

    def label(v, c, r):
        if v >> 4 == 1 or (v & 15) <= 1:
            return ","
        return "u" if r <= 12 - (0 if c > 14 else 0) and not (r == 12 and c >= 14) else "l"
    rows = a.rows(label)
    red = w.ramp_bands("lips", 4, [(0.0, 3), (3.6, 4), (4.6, 5), (5.6, 6), (6.6, 7), (7.6, 8), (8.6, 9), (9.6, 10),
                                    (10.6, 11), (11.6, 12)], metallic=0.0, roughness=0.18)
    dark = pal("lips_dark", 0x41, metallic=0.0, roughness=0.5)
    whole = a.rows(lambda v, c, r: "#")
    region("lips_base", a, whole, "#", 2.0, radius=1.0, bands=[(0.0, dark)], smooth=2, epsilon=0.4,
           select=lambda v, c, r: True, coarse_from=1.2)
    region("upper", a, rows, "u", 6.0, radius=3.6, crown=0.5, bands=red, smooth=2, epsilon=0.4, min_area=2.0,
           select=lambda v, c, r: rows[r][c] == "u", blur=1, grow=0.55, rim=0.8, aspect=1.4, target=1400)
    region("lower", a, rows, "l", 6.8, radius=3.8, crown=0.6, bands=red, smooth=2, epsilon=0.4, min_area=2.0,
           select=lambda v, c, r: rows[r][c] == "l", blur=1, grow=0.55, rim=0.8, aspect=1.4, target=1400)
    w.sh.flat_bottom(w.meshes())
    w.sh.cut_planes(w.meshes(), [((12.0, 0, 0), (1, 0, 0))])  # the sprite's edge: the mouth goes on beyond it
    if mirror:
        w.mirror_all()


model("eyespy_lips_left", [(196, True)])(lambda: lips(False))
model("eyespy_lips_right", [(208, True)])(lambda: lips(True))


# --- ^ 153, 155 above 191, 193: the brick bulb ----------------------------------------------------

RING = w.Art(art.RING, 48, (24, 28))


def ring_whole():
    """A machine of UNDERDELI on its brick wall (the wall is the map's, not modelled): a red bulb on a
    red stalk under a grey hood, and below it two grey rings, each round a red cylinder, held by a
    yoke under the stalk's foot."""
    a = RING
    X, Y = a.X, a.Y
    grey = w.ramp_bands("ring_grey", 0, GREY, metallic=0.55, roughness=0.35)
    red = w.ramp_bands("ring_red", 4, RED, metallic=0.35, roughness=0.3)

    def label(v, c, r):
        red_ = v >> 4 == 4
        s = v & 15
        if red_ and 19 <= c <= 30 and 13 <= r <= 31:
            return "s" if r >= 22 else "-"
        if not red_ and s >= 4 and 9 <= r <= 21 and 12 <= c <= 36:
            return "D"
        return "-"
    rows = a.rows(label)
    region("hood", a, rows, "D", 6.5, radius=2.6, crown=0.4, bands=grey, smooth=2, epsilon=0.5, rim=1.0, aspect=1.4,
           target=2400, min_area=3.0)
    bulb = w.ellipsoid("bulb", (X(24.5), Y(18.2), 3.4), (5.0, 4.6, 4.8), red[0][1], 28, 14)
    w.paint_bands(bulb, a.field(lambda v, c, r: v >> 4 == 4 and 12 <= r <= 23, blur=1), red)
    region("stalk", a, rows, "s", 4.6, radius=2.0, crown=0.2, bands=red, smooth=2, epsilon=0.4, rim=0.8, aspect=1.4,
           grow=0.2)
    steel = pal("ring_steel", 0x06, metallic=0.6, roughness=0.3)
    ring_light = pal("ring_light", 0x09, metallic=0.6, roughness=0.3)
    # The rings: lying on the wall, their outer sides (towards the edges) heavier.
    for name, c, side in (("ring_l", 10.6, -1), ("ring_r", 37.4, 1)):
        cx, cy = X(c), Y(35.6)
        path, radii = [], []
        for i in range(41):
            t = 2 * math.pi * i / 40
            path.append((cx + 6.1 * math.cos(t), cy + 7.6 * math.sin(t), 2.0))
            radii.append(1.5 + 0.7 * max(0.0, side * math.cos(t)))
        ring_obj = w.tube(name, path, radii, steel, segments=12, squash=1.0)
        w.paint_bands(ring_obj, a.field(lambda v, c_, r_: v >> 4 == 0 and abs(c_ - c) <= 9 and 26 <= r_ <= 45,
                                        blur=2), grey)
    for name, c in (("piston_l", 12.0), ("piston_r", 36.0)):
        x = X(c)
        piston = w.lathe(name, [(Y(44.2), 0.4), (Y(43.9), 2.3), (Y(43.0), 2.7), (Y(28.6), 2.7), (Y(27.8), 2.2),
                                (Y(27.4), 0.4)], red[0][1], axis="y", at=(x, 3.2), segments=20)
        w.paint_bands(piston, a.field(lambda v, c_, r_: v >> 4 == 4 and abs(c_ - c) <= 3 and 27 <= r_ <= 44,
                                      blur=1), red)
        w.lathe(f"{name}_band", [(Y(40.9), 2.85), (Y(39.6), 2.85)], steel, axis="y", at=(x, 3.2), segments=20)
    # No wall under it (the map draws the wall): a steel yoke under the stalk's foot holds the rings.
    yoke = pal("ring_yoke", 0x05, metallic=0.6, roughness=0.35)
    w.tube("yoke", w.catmull([(X(c), Y(r), z) for c, r, z in ((15.2, 34.0, 2.0), (19.5, 31.4, 2.4),
                                                                (29.5, 31.4, 2.4), (33.8, 34.0, 2.0))], 0.5),
           1.3, yoke, segments=12)
    w.ellipsoid("hub", (X(24.5), Y(30.8), 1.4), (3.8, 2.2, 2.4), yoke, 20, 10)
    w.sh.flat_bottom(w.meshes())


w.WHOLES["ring"] = (ring_whole, (48, 56))
for name, sprite, box in (("brick_bulb_tl", 153, (-24, 0, 0, 28)), ("brick_bulb_tr", 155, (0, 24, 0, 28)),
                          ("brick_bulb_bl", 191, (-24, 0, -28, 0)), ("brick_bulb_br", 193, (0, 24, -28, 0))):
    model(name, [(sprite, True)])(lambda box=box: (ring_whole(), w.piece(*box)))


# --- ^ 77, 79, 81 above 115, 117, 119: the machine in the rock -------------------------------------

SAND = w.Art(art.SAND, 72, (36, 28))


def sand_whole():
    """A grey machine of SURFACE half buried in tan rock: two arched grips at its sides, a tower in
    its middle, a body below it and two big claws reaching down (117's frames 7 and 9 show sparks
    between them: the model keeps the claws)."""
    a = SAND
    X, Y = a.X, a.Y

    def label(v, c, r):
        if v >> 4 == 1:
            return "R"
        if 28 <= c <= 39 and r <= 18:
            return "T"
        if r <= 19 and (c <= 22 or c >= 45):
            return "h"
        if r >= 34 and 14 <= c <= 52 and (c <= 30 or c >= 38):
            return "C"
        if 15 <= c <= 54 and 14 <= r <= 36:
            return "B"
        return "R"
    rows = a.rows(label)
    tan = w.ramp_bands("sand_tan", 1, [(0.0, 4), (4.5, 6), (6.5, 8), (8.5, 10), (10.5, 12), (12.5, 14)], metallic=0.0,
                       roughness=0.85)
    grey = w.ramp_bands("sand_grey", 0, GREY, metallic=0.55, roughness=0.35)
    region("rock", a, rows, "R", 4.5, radius=2.0, crown=0.6, bands=tan, smooth=2, epsilon=0.6, relief=1.2,
           select=lambda v, c, r: v >> 4 == 1, min_area=3.0, rim=0.6, target=4000)
    region("grips", a, rows, "h", 7.0, radius=2.2, crown=0.3, bands=grey, smooth=2, epsilon=0.5, rim=1.0, aspect=1.6,
           target=1800)
    region("tower", a, rows, "T", 10.5, radius=1.0, crown=0.3, bands=grey, smooth=1, epsilon=0.7, rim=1.0)
    region("body", a, rows, "B", 7.5, radius=1.4, crown=0.6, bands=grey, smooth=2, epsilon=0.6, rim=1.0, target=2600)

    def claw_slope(x, y, z):
        return z * (0.55 + 0.45 * w.hk.smoothstep(Y(53), Y(34), y))
    region("claws", a, rows, "C", 7.0, radius=2.0, crown=0.3, bands=grey, smooth=2, epsilon=0.5, rim=1.0, aspect=1.5,
           z_fn=claw_slope, target=2000)
    w.sh.flat_bottom(w.meshes())


w.WHOLES["sand"] = (sand_whole, (72, 56))
for name, sprite, box in (("rock_machine_tl", 77, (-36, -12, 0, 28)), ("rock_machine_tc", 79, (-12, 12, 0, 28)),
                          ("rock_machine_tr", 81, (12, 36, 0, 28)), ("rock_machine_bl", 115, (-36, -12, -28, 0)),
                          ("rock_machine_bc", 117, (-12, 12, -28, 0)), ("rock_machine_br", 119, (12, 36, -28, 0))):
    model(name, [(sprite, True)])(lambda box=box: (sand_whole(), w.piece(*box)))


# --- ^ 11, 13, 49, 50, 52 and 92, 94, 129, 131, 133: the spiked hands ------------------------------

HAND = w.Art(art.HAND, 60, (30, 28))
HAND_R = w.Art(art.HAND_R, 60, (30, 28))
# The spikes (fitted to the sprites' pixels): tip and base (column, row) and the radius at the base.
SPIKES = [((34.63, -0.08), (33.5, 19.9), 2.5), ((17.62, 1.18), (26.95, 20.55), 2.6),
          ((4.82, 7.15), (20.17, 24.96), 2.6), ((-0.48, 17.61), (14.85, 29.68), 2.6)]
SPIKES_R = [((24.23, -0.02), (26.14, 19.9), 2.0), ((40.91, 1.96), (31.69, 21.38), 2.1),
            ((53.22, 8.19), (37.91, 26.03), 2.1), ((58.96, 17.95), (43.92, 30.38), 2.0)]


def hand_whole(right=False):
    """The grey spiked hand of SURFACE's boss: a heavy gauntlet with a blue eye in it and four long
    spikes reaching up and to the left (its twin, drawn without outlines, up and to the right)."""
    a = HAND_R if right else HAND
    spikes = SPIKES_R if right else SPIKES
    eye_c = 19.4 if right else 39.6
    X, Y = a.X, a.Y

    def on_spike(c, r):
        for (tc, tr), (bc, br), rad in spikes:
            dx, dy = bc - tc, br - tr
            t = ((c - tc) * dx + (r - tr) * dy) / (dx * dx + dy * dy)
            if t < 0.93:
                px, py = tc + t * dx, tr + t * dy
                if math.hypot(c - px, r - py) <= rad + 1.2:
                    return True
        return False

    def label(v, c, r):
        if v >> 4 not in (0, 3):
            return "."
        if v >> 4 == 3:
            return "e"
        if on_spike(c, r):
            return "-"
        return "P"
    rows = a.rows(label)
    grey = w.ramp_bands("hand_grey", 0, GREY, metallic=0.6, roughness=0.32)
    steel = pal("hand_spike", 0x09, metallic=0.7, roughness=0.25)

    def knuckles(x, y, z):
        return z + 1.5 * w.hk.smoothstep(Y(50), Y(26), y)
    region("palm", a, rows, "Pe", 8.0, radius=2.0, crown=0.8, bands=grey, smooth=2, epsilon=0.6, rim=1.5,
           select=lambda v, c, r: rows[r][c] == "P", z_fn=knuckles, target=3200)
    # The eye, set into the palm.
    blue = w.ramp_bands("hand_eye", 3, [(0.0, 6), (5.0, 8), (7.0, 10), (9.0, 11), (11.0, 13), (12.5, 14)],
                        metallic=0.1, roughness=0.1, glow=lambda s: 0.25 + 0.12 * max(0, s - 8))
    palm = w.meshes()[0]
    ez = w.surface(palm, X(eye_c), Y(39.6), 9.0)
    eye = w.ellipsoid("eye", (X(eye_c), Y(39.6), ez - 1.3), (4.9, 4.2, 2.8), blue[0][1], 28, 14)
    w.paint_bands(eye, a.field(lambda v, c, r: v >> 4 == 3, blur=1), blue)
    rim_mat = pal("hand_eye_rim", 0x04, metallic=0.5, roughness=0.4)
    rim_pts = [(X(eye_c) + 5.4 * math.cos(t), Y(39.6) + 4.7 * math.sin(t), 0.0) for t in
               [2 * math.pi * i / 28 for i in range(29)]]
    rim_pts = [(x, y, w.surface(palm, x, y, ez) + 0.1) for x, y, _ in rim_pts]
    w.tube("eye_rim", rim_pts, 0.75, rim_mat, 10)
    # The spikes: long cones from the palm.
    for i, ((tc, tr), (bc, br), rad) in enumerate(spikes):
        base = Vector((X(bc), Y(br), 4.4))
        tip = Vector((X(tc), Y(tr), 3.2))
        d = tip - base
        n = d.length
        w.lathe_dir(f"spike{i}", [(-1.0, 0.3), (-0.6, rad), (0.45 * n, rad * 0.95), (0.75 * n, rad * 0.75),
                                  (0.92 * n, rad * 0.48), (n + 0.2, 0.25), (n + 0.5, 0.02)], steel, base, d,
                    segments=14, squash=0.85)
        w.lathe_dir(f"collar{i}", [(-0.4, rad * 1.15), (0.6, rad * 1.15)], rim_mat, base, d, segments=14,
                    squash=0.85)
    w.sh.flat_bottom(w.meshes())


w.WHOLES["hand"] = (hand_whole, (60, 56))
w.WHOLES["hand_r"] = (lambda: hand_whole(True), (60, 56))
for name, sprite, large, box in (("spike_hand_tl", 11, True, (-30, -6, 0, 28)),
                                 ("spike_hand_tr", 13, True, (-6, 18, 0, 28)),
                                 ("spike_hand_tip", 49, False, (-30, -18, -14, 0)),
                                 ("spike_hand_bl", 50, True, (-18, 6, -28, 0)),
                                 ("spike_hand_br", 52, True, (6, 30, -28, 0))):
    model(name, [(sprite, large)], size=(24, 28) if large else (12, 14))(
        lambda box=box: (hand_whole(False), w.piece(*box)))
for name, sprite, large, box in (("spike_hand_r_tl", 92, True, (-18, 6, 0, 28)),
                                 ("spike_hand_r_tr", 94, True, (6, 30, 0, 28)),
                                 ("spike_hand_r_bl", 129, True, (-30, -6, -28, 0)),
                                 ("spike_hand_r_bc", 131, True, (-6, 18, -28, 0)),
                                 ("spike_hand_r_tip", 133, False, (18, 30, -14, 0))):
    model(name, [(sprite, large)], size=(24, 28) if large else (12, 14))(
        lambda box=box: (hand_whole(True), w.piece(*box)))


# --- ^ 267, 269: NOSE DRIP's nose tip and tongue ---------------------------------------------------

@model("nosedrip_nostrils", [(267, True)])
def nosedrip_nostrils():
    """NOSE DRIP's fleshy nose seen end on: its two sides parted by a groove, the rounded tip at the
    top darkened round three nostrils glowing red inside; the flesh goes on down past the sprite's
    lower edge."""
    a = w.Art(art.NOSE, 24, (12, 14))
    X, Y = a.X, a.Y
    flesh = w.ramp_bands("nose_flesh", 4, [(0.0, 2), (2.5, 3), (3.5, 4), (4.5, 5), (5.5, 6), (6.5, 7), (7.5, 8),
                                           (8.5, 9), (9.5, 10), (10.5, 11), (11.5, 12)], metallic=0.0, roughness=0.3)
    whole = a.rows(lambda v, c, r: "f")
    gx = X(11.5)

    nostrils = ((3.6, 9.2, 1.9, 1.7), (10.2, 7.6, 2.0, 2.2), (15.2, 6.4, 1.4, 1.5))

    def shape(x, y, z):
        tip = w.hk.smoothstep(Y(2.0), Y(13.0), y)  # 0 at the top edge, 1 lower down
        z = z * (0.55 + 0.45 * tip)
        z -= 1.4 * math.exp(-((x - gx) / 1.3) ** 2) * w.hk.smoothstep(Y(9), Y(15), y)
        for c, r, rx, ry in nostrils:  # the nostrils: dents in the tip
            q = ((x - X(c)) / (rx * 1.15)) ** 2 + ((y - Y(r)) / (ry * 1.15)) ** 2
            z -= 2.2 * math.exp(-q ** 2)
        return max(z, 0.4)
    region("flesh", a, whole, "f", 9.0, radius=5.0, crown=0.8, bands=flesh, smooth=2, epsilon=0.4,
           select=lambda v, c, r: v >> 4 == 4, rim=1.0, target=2600, z_fn=shape, blur=1)
    hole = pal("nose_hole", 0x40, metallic=0.0, roughness=0.6)
    hot = pal("nose_hot", 0x77, metallic=0.0, roughness=0.4, glow=1.3, color=(230, 50, 10))
    for c, r, rx, ry in nostrils:
        x, y = X(c), Y(r)
        z = w.surface(w.meshes(), x, y, 5.0)
        w.ellipsoid(f"nostril{c}", (x, y, z - 0.45), (rx * 0.95, ry * 0.95, 0.5), hole, 16, 8)
        w.ellipsoid(f"nostril_hot{c}", (x, y, z - 0.2), (rx * 0.6, ry * 0.6, 0.4), hot, 12, 6)
    w.sh.flat_bottom(w.meshes())
    w.sh.cut_planes(w.meshes(), [((0, -14.0, 0), (0, -1, 0))])


@model("nosedrip_tongue", [(269, True)])
def nosedrip_tongue():
    """NOSE DRIP's tongue hanging down the screen, its rounded tip at the bottom, a groove down its
    middle, glossy."""
    a = w.Art(art.TONGUE, 24, (12, 14))
    X = a.X
    flesh = w.ramp_bands("tongue", 4, [(0.0, 3), (3.5, 4), (4.5, 5), (5.5, 6), (6.5, 7), (7.5, 8), (8.5, 9),
                                       (9.5, 10)], metallic=0.0, roughness=0.22)
    whole = a.rows(lambda v, c, r: "#")
    gx = X(11.6)

    def groove(x, y, z):
        return z - 1.3 * math.exp(-((x - gx) / 1.1) ** 2) * min(1.0, z / 3.0)
    region("tongue", a, whole, "#", 7.0, radius=5.0, crown=0.6, bands=flesh, smooth=2, epsilon=0.4,
           select=lambda v, c, r: v >> 4 == 4, rim=0.8, aspect=1.2, z_fn=groove, target=3200)
    w.sh.flat_bottom(w.meshes())
    w.sh.cut_planes(w.meshes(), [((0, 14.0, 0), (0, 1, 0))])


if __name__ == "__main__":
    w.run()
