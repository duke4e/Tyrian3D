"""Enemies of wave 3, batch I: the remaining enemy types of sheet ^ (enemy_x5e; models.cfg: x5e),
modelled as their sprites look (models.cfg: yaw=0). (The core machine,
UNDERDELI's mite, floor eye and brick crab: polish_core_machine.py, polish_deli_mite.py, polish_deli_floor_eye.py,
polish_brick_crab.py; the blue gate of BRAINIAC and the ICE levels: polish_blue_gate.py.)

(UNDERDELI's blue cruiser, ^ 198-206, and EYESPY's lips, ^ 196 208: polish_cruiser.py, polish_lips.py; UNDERDELI's
brick bulb, ^ 153 155 191 193, SURFACE's rock machine, ^ 77-119 and its wreck 1-43, and its boss's spiked hands, ^ 11-52
and 92-133: polish_brick_bulb.py, polish_rock_machine.py, polish_spike_hand.py.)
- nosedrip_nostrils, nosedrip_tongue (^ 267, 269): NOSE DRIP's nose tip and tongue.

Parts are raised from regions of the sprites' pixels (wave3_i_art.py holds their palette indices) and
coloured in bands of the pixels' shades, with the helpers of wave3_i_kit.py.

usage: Blender -b --factory-startup -P wave3_i.py -- [--only name,name] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1]
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_i_art as art  # noqa: E402
import wave3_i_kit as w  # noqa: E402
from wave3_i_kit import k, model, pal  # noqa: E402


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
