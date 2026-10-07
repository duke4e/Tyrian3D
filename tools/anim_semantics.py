#!/usr/bin/env python3
"""Classifies the enemies' sprite animations (plan M2.2), for models that should move as the
sprites do.

usage: <python with numpy> tools/anim_semantics.py <extract dir> <out.json>
       (Blender's Python has numpy: /Applications/Blender.app/Contents/Resources/<version>/python/bin/python3.*)

<extract dir> is the output of TYR3D_EXTRACT. For every enemy type whose animation has more than
one distinct frame, each frame is compared with the first one turned by every angle (in steps of
5 degrees, about the sprite's centre):

  rotation  the frames are the first one turned (spinning, or a turret's directions): a model
            turns with them. The result gives the turn of each frame and, for even steps, a
            models.cfg option yaw=frames:<n>:<first>[:ccw].
  roll      the silhouette narrows and widens again while keeping its length: the object spins
            about its long axis (seen from above). A model rolls with the frames.
  cycle     the frames match the first one unturned (blinking lights, small changes): a model
            keeps its heading.
  morph     none of these (opening, firing, parts moving): a model needs its own animation, or
            the sprite's volume.

Prints a summary and writes the details per enemy type.
"""
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "blender"))
from sprite_profile import sprite_pixels  # noqa: E402

STEP = 5
ANGLES = np.arange(0, 360, STEP)


def load(sheet, sprite, large):
    pixels = sprite_pixels(sheet, sprite, large)
    h, w = len(pixels), len(pixels[0])
    mask = np.zeros((h, w), bool)
    lum = np.zeros((h, w), np.float32)
    for y, line in enumerate(pixels):
        for x, p in enumerate(line):
            if p is not None:
                mask[y, x] = True
                lum[y, x] = 0.3 * p[0] + 0.59 * p[1] + 0.11 * p[2]
    return mask, lum


_maps = {}


def rotation_maps(h, w):
    """For each angle, the source pixel of each destination pixel (nearest), or -1 outside."""
    if (h, w) not in _maps:
        cy, cx = h / 2, w / 2
        ys, xs = np.mgrid[0:h, 0:w]
        dy, dx = ys + 0.5 - cy, xs + 0.5 - cx
        maps = []
        for a in np.radians(ANGLES):
            # Turned clockwise on screen by a (y down): the source is the destination turned back.
            sx = np.cos(a) * dx + np.sin(a) * dy + cx
            sy = -np.sin(a) * dx + np.cos(a) * dy + cy
            ix, iy = np.floor(sx).astype(int), np.floor(sy).astype(int)
            inside = (ix >= 0) & (ix < w) & (iy >= 0) & (iy < h)
            maps.append(np.where(inside, iy * w + ix, -1))
        _maps[(h, w)] = np.stack(maps)  # (angles, h, w)
    return _maps[(h, w)]


def scores(first, frame):
    """How well the first frame turned by each angle matches the frame (0..1)."""
    mask0, lum0 = first
    mask1, lum1 = frame
    h, w = mask0.shape
    maps = rotation_maps(h, w)
    flat_mask, flat_lum = mask0.ravel(), lum0.ravel()
    turned_mask = np.where(maps >= 0, flat_mask[np.maximum(maps, 0)], False)
    turned_lum = np.where(maps >= 0, flat_lum[np.maximum(maps, 0)], 0)
    both = turned_mask & mask1
    either = turned_mask | mask1
    iou = both.sum(axis=(1, 2)) / np.maximum(either.sum(axis=(1, 2)), 1)
    diff = np.abs(turned_lum - lum1) * both
    agreement = 1 - diff.sum(axis=(1, 2)) / np.maximum(both.sum(axis=(1, 2)), 1) / 255
    return iou * agreement


def extent(mask):
    """Width and height of a silhouette (pixels)."""
    xs, ys = np.nonzero(mask.any(axis=0))[0], np.nonzero(mask.any(axis=1))[0]
    return (xs[-1] - xs[0] + 1 if len(xs) else 0), (ys[-1] - ys[0] + 1 if len(ys) else 0)


def is_roll(frames):
    """The silhouette narrows to a sliver and widens again, its length the same."""
    sizes = [extent(mask) for mask, _ in frames]
    widths, heights = [w for w, _ in sizes], [h for _, h in sizes]
    if min(heights) < 0.8 * max(heights) or max(widths) == 0:
        return False
    return min(widths) <= 0.5 * max(widths) and len(frames) >= 4


def classify(frames):
    first = frames[0]
    turns, best, unturned = [0], [1.0], [1.0]
    for frame in frames[1:]:
        s = scores(first, frame)
        k = int(np.argmax(s))
        turns.append(int(ANGLES[k]))
        best.append(float(s[k]))
        unturned.append(float(s[0]))

    if min(unturned[1:]) > 0.8:
        return {"kind": "cycle", "match": round(min(unturned[1:]), 3)}
    if is_roll(frames):
        return {"kind": "roll"}
    # Pixel art redrawn for each direction matches a turned copy only roughly.
    rotated = [b > 0.5 and b - u > 0.1 for b, u in zip(best[1:], unturned[1:])]
    if sum(rotated) < max(1, 0.75 * (len(frames) - 1)):
        return {"kind": "morph", "match": round(min(best[1:]), 3)}

    # Turn per frame: the median step between frames, with its sign (clockwise > 0).
    steps = []
    for a, b in zip(turns, turns[1:]):
        d = (b - a + 180) % 360 - 180
        steps.append(d)
    step = float(np.median(steps))
    even = all(abs(d - step) <= STEP for d in steps) and abs(step) >= STEP
    result = {"kind": "rotation", "match": round(min(best[1:]), 3), "turns": turns, "step": step}
    if even:
        n = round(360 / abs(step))
        if abs(360 / n - abs(step)) <= STEP:
            result["yaw"] = f"yaw=frames:{n}:0" + (":ccw" if step < 0 else "")
    return result


def main():
    extract, out_path = sys.argv[1], sys.argv[2]
    catalog = json.load(open(os.path.join(extract, "catalog.json")))
    results, seen, counts = [], {}, {}
    for e in catalog["enemies"]:
        frames = list(dict.fromkeys(f for f in e["frames"] if f > 0))
        if len(frames) < 2:
            continue
        key = (e["sheet_file"], tuple(frames), e["large"])
        if key not in seen:
            sheet = os.path.join(extract, "sheets", e["sheet_file"] + ".png")
            try:
                images = [load(sheet, f, e["large"]) for f in frames]
            except IndexError:  # frames past the end of the sheet
                continue
            seen[key] = classify(images)
            counts[seen[key]["kind"]] = counts.get(seen[key]["kind"], 0) + 1
        results.append({"episode": e["episode"], "enemy": e["id"], "sheet": e["sheet"], "frames": frames,
                        "large": e["large"], **seen[key]})

    with open(out_path, "w") as f:
        json.dump(results, f, indent=1)
    print(f"{len(seen)} distinct animations:", ", ".join(f"{n} {k}" for k, n in sorted(counts.items())))
    rotations = [r for r in results if r["kind"] == "rotation" and "yaw" in r]
    print(f"{len(rotations)} enemy types turn evenly; e.g.:")
    for r in rotations[:10]:
        print(f"  episode {r['episode']} enemy {r['enemy']} (sheet {r['sheet']}, frames {r['frames'][:6]}...): "
              f"{r['yaw']}, match {r['match']}")


if __name__ == "__main__":
    main()
