"""The small blue ice crystal of CAMANIS, ICE EXIT, APPROACH and ICESECRET (sheet 7 sprite 152, 1x1:
12 x 14 pixels), polished (2026-10-18; it replaces later_episodes.py's low-poly gem).

WORK IN PROGRESS
"""
import math
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
from polish_crystal_blue import (Lin, X, Y, across, crystal, materials, outline_facets,  # noqa: E402
                                 under)

# The outline (the girdle), counter-clockwise from above: the sprite's octagon, its outline pixels
# included.
OUTLINE = [(1.75, 7.0), (-1.75, 7.0), (-6.0, 2.75), (-6.0, -3.75), (-2.75, -7.0), (2.75, -7.0), (6.0, -3.75),
           (6.0, 2.75)]
OUTLINE_NAMES = ["top", "upper_left", "left", "lower_left", "bottom", "lower_right", "right", "upper_right"]
GIRDLE_TOP, GIRDLE_BOTTOM = 3.1, 2.5
BEZEL_SLOPE, PAVILION_SLOPE, CULET = 2.4, 1.25, -2.0


def design():
    """The crystal's facets {name: (half-space, material name)}, its ridges [(facet, facet, width,
    material name)] and its materials' palette indices {material name: index}."""
    sq = math.sqrt(2)
    # The table: highest along the sprite's light line across it (row 6), falling off a little
    # both ways; across, a gentle barrel of four strips (their edges at columns 4, 6 and 8), so that
    # the cap above it falls in the sprite's bands.
    crest = Lin(7.2)
    upper = crest - 0.10 * Y(-0.5)
    lower = crest + 0.12 * Y(-0.5)
    strip_b = 0.05 * X(0.0)
    strip_c = -0.05 * X(0.0)
    strip_a = Lin(strip_b(-2.0, 0)) + 0.14 * X(2.0)
    strip_d = Lin(strip_c(2.0, 0)) - 0.14 * X(-2.0)
    f = {}
    for half, base in (("u", upper), ("l", lower)):
        for strip, g in (("a", strip_a), ("b", strip_b), ("c", strip_c), ("d", strip_d)):
            f[f"table_{strip}{half}"] = base + g
    k_side = 1.35
    for half in "ul":
        # The sides, from the ridges down the sprite's light lines (columns 2 and 9).
        f["side_l" + half] = f["table_a" + half] + k_side * X(3.5)
        f["side_r" + half] = f["table_d" + half] - k_side * X(-3.5)
    # The lower end: the sprite's light lines from columns 2 and 9 down to a point at row 11, and
    # two facets below them; a small one at the very bottom.
    f["lower_left"] = f["table_bl"] + 1.0 * across(1, 1, 5 / sq)
    f["lower_right"] = f["table_cl"] - 1.0 * across(1, -1, -5 / sq)
    f["lower_mid"] = f["table_bl"] + 1.9 * Y(5.35)
    # The upper end (the sprite's dark cap): each strip of the top turned down from row 3.
    for strip in "abcd":
        f["cap_" + strip] = f[f"table_{strip}u"] - 1.15 * Y(-4.0)
    f["cap_left"] = f["side_lu"] - 1.4 * Y(-4.0)
    f["cap_right"] = f["side_ru"] - 1.4 * Y(-4.0)

    facets = {name: (under(fn), name) for name, fn in f.items()}
    facets.update(outline_facets(OUTLINE, OUTLINE_NAMES, GIRDLE_TOP, GIRDLE_BOTTOM, BEZEL_SLOPE, PAVILION_SLOPE,
                                 CULET, cap_sides=("top", "upper_left", "upper_right")))
    palette = {
        "table_au": 0x96, "table_bu": 0x97, "table_cu": 0x9a, "table_du": 0x98,
        "table_al": 0x9a, "table_bl": 0x9b, "table_cl": 0x9c, "table_dl": 0x9b,
        "side_lu": 0x9b, "side_ll": 0x9a, "side_ru": 0x9c, "side_rl": 0x9b,
        "lower_left": 0x98, "lower_mid": 0x96, "lower_right": 0x9c,
        "cap_a": 0x38, "cap_b": 0x3d, "cap_c": 0x36, "cap_d": 0x3a, "cap_left": 0x37, "cap_right": 0x33,
        "bezel": 0x96, "cap_bezel": 0x32, "girdle": 0x93, "pavilion": 0x96,
        "white": 0x8c, "light": 0x9e,
    }
    white, light = 0.6, 0.45
    ridges = [
        ("table_au", "side_lu", white, "white"), ("table_al", "side_ll", white, "white"),
        ("table_du", "side_ru", white, "white"), ("table_dl", "side_rl", white, "white"),
        ("table_al", "lower_left", white, "white"), ("table_bl", "lower_left", white, "white"),
        ("table_dl", "lower_right", white, "white"), ("table_cl", "lower_right", white, "white"),
        ("side_lu", "side_ll", white, "white"), ("side_ru", "side_rl", white, "white"),
        ("table_au", "table_al", light, "light"), ("table_bu", "table_bl", light, "light"),
        ("table_cu", "table_cl", light, "light"), ("table_du", "table_dl", light, "light"),
    ]
    return facets, ridges, palette


def build():
    k.reset()
    facets, ridges, palette = design()
    mats = materials(palette, "crystal_small")
    obj = crystal("crystal_small", {name: (plane, mats[m]) for name, (plane, m) in facets.items()},
                  [(a, b, w, mats[m]) for a, b, w, m in ridges])
    print("triangles:", sum(len(p.vertices) - 2 for p in obj.data.polygons), "materials:", len(obj.data.materials))
    options = k.args()
    if "sheets" in options:
        k.check_silhouette(os.path.join(options["sheets"], "enemy_7.png"), 152, large=False)
    # The game shows colours as they are (no filmic tone mapping): so do the previews.
    bpy.context.scene.view_settings.view_transform = "Standard"
    k.finish(os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "enemies", "crystal_small.glb"),
             size=(12, 14))


if __name__ == "__main__":
    build()
