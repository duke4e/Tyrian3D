"""The blocks of WINDY, SOH JIN and the asteroid levels (sheet M sprites 1, 15 and 17): glossy rounded
blocks the size of the sprite, which the game stacks in walls and columns. Red (block_red.glb),
green with a yellow dollar sign (block_dollar.glb) and orange with a blue gem (block_gem.glb).

The sprite shows the block's top and, below it, its front; the model stands on the whole cell, a little
smaller than it, as the sprites leave gaps between neighbours.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import tyrkit as k  # noqa: E402

HALF_W, HALF_D = 11.0, 12.6   # the block's half width and half depth (the sprites leave gaps)
HEIGHT = 9.0                   # to the top's edge; the top bulges a little more
DOME = 1.2
TOP = HEIGHT + DOME


def block(name, shell):
    return k.pillow(name, HALF_W, HALF_D, HEIGHT, shell, rounding=3.6, dome=DOME)


def stroke(name, path, half_width, z0, z1, mat):
    """A raised line along a path [(x, y), ...] (an emblem drawn on a top)."""
    left, right = [], []
    for i, (x, y) in enumerate(path):
        ax, ay = path[max(i - 1, 0)]
        bx, by = path[min(i + 1, len(path) - 1)]
        dx, dy = bx - ax, by - ay
        length = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / length * half_width, dx / length * half_width
        left.append((x + nx, y + ny))
        right.append((x - nx, y - ny))
    outline = left + right[::-1]
    # Counter-clockwise seen from above.
    area = sum(outline[i][0] * outline[(i + 1) % len(outline)][1] - outline[(i + 1) % len(outline)][0] * outline[i][1]
               for i in range(len(outline)))
    if area < 0:
        outline.reverse()
    return k.slab(name, outline, z0, z1, mat)


def arc(cx, cy, radius, start, end, steps=14):
    return [(cx + radius * math.cos(math.radians(start + (end - start) * i / steps)),
             cy + radius * math.sin(math.radians(start + (end - start) * i / steps))) for i in range(steps + 1)]


def export(name):
    here = os.path.dirname(os.path.abspath(__file__))
    k.export(os.path.join(here, "..", "..", "..", "..", "assets", "models", "enemies", name + ".glb"))


def build_red():
    k.reset()
    block("block", k.material("block_red", palette=71, metallic=0.05, roughness=0.3))
    export("block_red")


def build_dollar():
    k.reset()
    block("block", k.material("block_green", palette=39, metallic=0.05, roughness=0.3))
    gold = k.material("block_gold", palette=125, metallic=0.6, roughness=0.3)
    # The dollar sign: an S of two arcs and a bar through it, in the middle of the top.
    s = arc(0.0, 2.4, 2.4, 30, 270) + arc(0.0, -2.4, 2.4, 90, -150)[1:]
    k.smooth(stroke("dollar_s", s, 0.85, TOP - 0.4, TOP + 0.7, gold), 60)
    stroke("dollar_bar", [(0.0, -6.6), (0.0, 6.6)], 0.6, TOP - 0.4, TOP + 0.5, gold)
    export("block_dollar")


def build_gem():
    k.reset()
    block("block", k.material("block_orange", palette=249, metallic=0.05, roughness=0.3))
    gem = k.material("block_gem", palette=156, metallic=0.2, roughness=0.15, emission=(60, 120, 255),
                     emission_strength=0.6)
    setting = k.material("block_setting", palette=246, metallic=0.4, roughness=0.4)
    k.smooth(k.ellipsoid("setting", (0.0, 0.0, TOP - 0.5), (5.2, 5.2, 1.3), setting, 24, 8), 60)
    k.smooth(k.ellipsoid("gem", (0.0, 0.0, TOP + 0.3), (4.0, 4.0, 1.9), gem, 24, 10), 60)
    export("block_gem")


build_red()
build_dollar()
build_gem()
