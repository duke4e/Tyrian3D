"""Enemies of wave 3, batch I: the remaining enemy types of sheet ^ (enemy_x5e; models.cfg: x5e),
modelled as their sprites look (models.cfg: yaw=0). Objects the game draws from several sprites are
built whole and cut into the sprites' pieces, drawn at their own origins (models.cfg: origin). (The core machine,
UNDERDELI's mite, floor eye and brick crab: polish_core_machine.py, polish_deli_mite.py, polish_deli_floor_eye.py,
polish_brick_crab.py; the blue gate of BRAINIAC and the ICE levels: polish_blue_gate.py.)

(UNDERDELI's blue cruiser, ^ 198-206, and EYESPY's lips, ^ 196 208: polish_cruiser.py, polish_lips.py.)
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
       Blender -b --factory-startup -P wave3_i.py -- --whole ring,sand,hand,hand_r
       --preview <prefix>
"""
import math
import os
import sys

from mathutils import Vector

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
