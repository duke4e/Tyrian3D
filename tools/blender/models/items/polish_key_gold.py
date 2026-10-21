"""SOH JIN's golden key (the coins sheet's sprite 243, enemy type 475 of episode 1: 500 credits; 2x2, 24 x 28 pixels;
28 of them, all on the ground in SOH JIN; one frame, not animated), polished (2026-10-21; it replaces
wave3_ai_items.py's key_gold(), the sprite's pixels inflated into one rounded blob with a ridge along its shaft).
models.cfg: model key_gold items/key_gold.glb (unchanged) and sprite coins 243 key_gold spin=1.5 (see below). No
other enemy shows it, and it is no other sprite's pixels mirrored, turned or in other ramps.

As the sprite and its 4x upscale draw it: a gold key (ramp 1, shades 0-14, in a black outline) lying with its bit up
the screen and its bow down, its shadow (indices a0, a1) cast to the lower right, which is left out (the game casts
the model's own). A straight shaft three pixels wide (columns 12-14) from the top (row 4) down into the bow; at its
top, on the left, the bit: a prong along the top (row 4, columns 6-11) turning down at its end into a short lip
(column 7, row 5), and a second prong lower down (row 10, columns 8-11) turning up into its lip (column 8, row 9),
the two lips a pixel apart (row 7), so that the bit is a C open to the left with a notch in its side; a dark band
across the shaft between them (row 7). The bow (columns 5-18 of rows 15-23): an oval 14 pixels across, its top band
broad (rows 16-19, lit at its upper left), its holes small and low (rows 19-21), one either side of the shaft,
which runs on through the bow to its bottom (columns 12-13).

Built as a cast and polished key: the shaft turned (a lathe along the screen's y), a groove ringing it between the
bit's prongs, a collar where it meets the bow, its top flat and chamfered, flush with the bit's; the bit two plates
(the top prong with its lip, the lower one with its), their edges rounded; the bow a rounded oblong plate (a
superellipse, its top tilted so that the left lobe stands higher, as the sprite's), its edges rounded broadly, a
wide hole sunk into it low down (a recess with a dark floor: the sprite draws the holes in dark gold, not
see-through), the shaft lying over the bow down to its bottom band, so that the hole shows either side of it.
Polished gold in ramp 1 (0x1a, very metallic), a little emission in a darker gold (0x16) so that its shaded sides
don't read black from the game's slanted camera; the groove and the recess darker (0x14). The parts reach half a
pixel into the sprite's black outline, which is the key's edge.

How the game shows it: an item drawn on the ground layer, centred in height there (it floats about 2 pixels over the
ground). The other loose items turn slowly (the fruit spin=1.5, the gems and crystals by their frames); the key's
line had yaw=0, the bit up the screen as the sprite draws it. Recommended: spin=1.5, turning slowly as the fruit does
(it is a key from every side, unlike the tick, the HOT DOG or the beer mug, which keep still; it turns about the
sprite's centre, which is the key's middle to within half a pixel). No color=sprite (one sprite, one colour), no glow
(it is metal, like the coins). yaw=0 stays possible if the keys should lie still as drawn.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; the origin is the
sprite's centre (pixel 12, 14): column c is x = c + 0.5 - 12, row r is y = 13.5 - r. The key lies on z = 0.

Replaces wave3_ai_items.py's key_gold() (its "# --- Coins 243: SOH JIN's golden key" section: KEY and the
@kit.model("key_gold", ...) function; SHADOW stays, check_rainbow() uses it) and the key's mention in that file's
docstring; and wave3_ai_art.py's KEY (only key_gold() reads it).

Options after "--": --outdir <dir> (default assets/models/items), --check <sheets dir> (the silhouette against
coins.png, the shadow's pixels left out), --preview <prefix>.
"""
import math
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_item_kit as kit  # noqa: E402
from polish_item_kit import k  # noqa: E402

NAME, SPRITE = "key_gold", 243
SHADOW = (0xa0, 0xa1)          # the shadow's palette indices (left out of the silhouette)

# The shaft: its axis (x, z), from its foot in the bow's bottom band to its flat top; radius above the bow and in it;
# the groove between the bit's prongs (y, half-length, radius); the collar where it meets the bow.
AXIS_X, AXIS_Z = 1.5, 2.05
SHAFT_FOOT, SHAFT_TOP = -10.55, 10.7
SHAFT_R, SHAFT_R_BOW = 2.05, 1.55
GROOVE = (6.5, 0.42, 1.6)
COLLAR = (-1.05, 0.55, 2.3)    # y, half-length, radius
# The bit's two plates (x, y), the top prong with its lip, the lower prong with its; their thickness (z).
BIT_TOP = [(-5.85, 10.75), (-5.85, 7.25), (-3.15, 7.25), (-3.15, 8.3), (AXIS_X, 8.3), (AXIS_X, 10.75)]
BIT_LOW = [(-4.85, 2.3), (AXIS_X, 2.3), (AXIS_X, 4.7), (-2.15, 4.7), (-2.15, 5.75), (-4.85, 5.75)]
PLATE_Z = (0.6, 3.2)
# The bow: a rounded oblong (a superellipse of power BOW_POWER: centre, half-width, half-heights above and below the
# middle), its top tilted so that the left lobe stands higher than the right (TILT a pixel per pixel across), as the
# sprite draws it; its hole (a recess, dark at its floor as the sprite's holes are: centre, semi-axes, floor), how
# round its edges are.
BOW = ((0.0, -5.85), 6.65, 4.5, 4.25)
BOW_POWER, TILT = 2.9, 0.1
HOLE = ((0.75, -6.75), (4.3, 1.55), 1.35)
BOW_ROUND = 1.2


def materials():
    pal = k.level_palette()
    return {
        "gold": k.material("key_gold", palette=0x1a, metallic=0.85, roughness=0.24, emission=pal[0x16],
                           emission_strength=0.1),
        "dark": k.material("key_gold_dark", palette=0x14, metallic=0.75, roughness=0.35),
    }


def shaft(m):
    """The shaft, turned along y: its foot rounded, narrower through the bow, the collar, the groove, the flat top
    chamfered."""
    gy, gh, gr = GROOVE
    cy, ch, cr = COLLAR
    prof = [(SHAFT_FOOT, 0.4), (SHAFT_FOOT + 0.25, SHAFT_R_BOW * 0.85), (SHAFT_FOOT + 0.7, SHAFT_R_BOW),
            (cy - ch - 0.6, SHAFT_R_BOW), (cy - ch - 0.15, cr * 0.92), (cy - ch + 0.1, cr), (cy + ch - 0.1, cr),
            (cy + ch + 0.15, cr * 0.92), (cy + ch + 0.5, SHAFT_R), (gy - gh - 0.12, SHAFT_R), (gy - gh + 0.1, gr),
            (gy + gh - 0.1, gr), (gy + gh + 0.12, SHAFT_R), (SHAFT_TOP - 0.32, SHAFT_R), (SHAFT_TOP, SHAFT_R - 0.3)]
    bar = k.lathe("shaft", prof, m["gold"], segments=28, axis_x=AXIS_X, axis_z=AXIS_Z)
    dark = kit.slot_of(bar, m["dark"])
    for poly in bar.data.polygons:
        if abs(poly.center.y - gy) < gh:   # the groove
            poly.material_index = dark
    return k.smooth(bar, 50)


def bit(m):
    """The bit: the two prongs with their lips, plates as thick as the shaft's middle, their edges rounded."""
    parts = []
    for name, outline in (("bit_top", BIT_TOP), ("bit_low", BIT_LOW)):
        plate = kit.prism(name, outline, PLATE_Z[0], PLATE_Z[1], m["gold"])
        kit.bevel(plate, 0.42, 3, 30)
        parts.append(kit.weighted(plate, 40))
    return parts


def ellipse(centre, axes, count):
    (cx, cy), (a, b) = centre, axes
    return [(cx + a * math.cos(2 * math.pi * i / count), cy + b * math.sin(2 * math.pi * i / count))
            for i in range(count)]


def bow_outline(count=64):
    (cx, cy), half_w, top, bottom = BOW
    pts = []
    for i in range(count):
        t = 2 * math.pi * i / count
        c, s = math.cos(t), math.sin(t)
        x = half_w * math.copysign(abs(c) ** (2 / BOW_POWER), c)
        v = math.copysign(abs(s) ** (2 / BOW_POWER), s)
        y = cy + (top * v - TILT * x * v if s >= 0 else bottom * v)
        pts.append((cx + x, y))
    return pts


def bow(m):
    """The bow: the plate of its outline, the hole sunk into it (a recess, its floor dark), its edges rounded
    broadly."""
    plate = kit.prism("bow", bow_outline(), PLATE_Z[0], PLATE_Z[1], m["gold"])
    (hx, hy), (ha, hb), floor = HOLE
    hole = kit.prism("bow_hole", ellipse((hx, hy), (ha, hb), 40), floor, PLATE_Z[1] + 1.0, m["dark"])
    kit.boolean(plate, hole, "DIFFERENCE")
    kit.bevel(plate, BOW_ROUND, 4, 30)

    def pick(c, n):
        inside = ((c.x - hx) / (ha + 0.9)) ** 2 + ((c.y - hy) / (hb + 0.9)) ** 2 < 1.0
        return m["dark"] if inside and (n.z < 0.6 or c.z < floor + 0.05) else m["gold"]
    for poly in plate.data.polygons:
        poly.material_index = kit.slot_of(plate, pick(poly.center, poly.normal))
    return kit.weighted(plate, 40)


def triangulate(objects):
    """Splits every face into triangles here, the same way every run (the exporter's own split of the n-gons changed
    after a --check render), keeping the custom normals."""
    for obj in objects:
        mod = obj.modifiers.new("triangulate", "TRIANGULATE")
        mod.quad_method = "BEAUTY"
        mod.ngon_method = "BEAUTY"
        mod.min_vertices = 4
        mod.keep_custom_normals = True
        kit.apply(obj)
    return objects


def build():
    opts = kit.options()
    k.reset()
    m = materials()
    parts = [shaft(m)] + bit(m) + [bow(m)]
    for obj in parts:
        kit.apply(obj)
        kit.drop_unused_materials(obj)
    triangulate(parts)
    bpy.context.view_layer.update()
    kit.finish(opts, NAME, parts, SPRITE, large=True, skip=SHADOW, distance=0.8)


if __name__ == "__main__":
    build()
