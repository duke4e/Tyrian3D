"""Shard (episode 2 enemies 792-794, sheet V sprites 10, 12 and 50: a crystal shard pointing up the
screen, up and right, up and left): a six-sided crystal with a long point forward and a short one
behind, its girdle across the sprite's row 19. models.cfg turns the one model for each sprite.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import tyrkit as k  # noqa: E402


def by(row):
    return 14 - row


def build():
    k.reset()
    front_mat = k.material("shard_front", palette=91, roughness=0.15, metallic=0.1)
    back_mat = k.material("shard_back", palette=88, roughness=0.2, metallic=0.1)

    cx = 0.5
    # Half-widths by row: a convex point forward, the girdle at row 19, a short blunt back.
    front = [(0.6, 0.0), (2.0, 1.8), (4.0, 3.3), (6.5, 4.6), (9.5, 5.9), (12.5, 7.0), (15.5, 7.8), (18.6, 8.0)]
    back = [(18.6, 8.0), (20.5, 8.1), (22.0, 7.0), (23.5, 5.0), (24.6, 2.6), (25.4, 0.0)]

    def part(name, profile, mat):
        rows = sorted(profile, key=lambda q: by(q[0]))
        rings = [k.ring(by(r), w, w * 0.6, 6, x=cx) for r, w in rows if w > 0]
        first, last = rows[0], rows[-1]
        k.loft(name, rings, mat, start_point=(cx, by(first[0]), 0.0), end_point=(cx, by(last[0]), 0.0))

    part("front", front, front_mat)
    part("back", back, back_mat)

    here = os.path.dirname(os.path.abspath(__file__))
    k.finish(os.path.join(here, "..", "..", "..", "..", "assets", "models", "enemies", "shard.glb"))


build()
