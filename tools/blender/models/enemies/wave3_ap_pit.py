"""Batch AP of wave 3 (sheet E): what is left of the boulders in the pit of TYRIAN (wave3_aa_rocks.py) once they are
blown away, modelled as the sprites look (models.cfg: yaw=0). The kit is wave3_ap_kit.py, the pixels wave3_ap_art.py
(ROCKS_DMG, in wave3_aa_art.ROCKS' frame).

Each of the six pieces leaves its wreck in its place when destroyed (enemies 522-527, dlevel -1): E 1 -> 7, 3 -> 9,
5 -> 11, 39 -> 45, 41 -> 47, 43 -> 49. The boulders are gone; in the dark pit they hid lies a pool of glowing blue
water, rubble and stones strewn round it, the brown dirt round the pit as before.

- holes_rocks_tl_damaged ... holes_rocks_br_damaged (E 7, 9, 11, 45, 47, 49): wave3_aa_rocks' whole (rocks_whole)
  built with no boulders and painted by the damaged sprites (the same dirt and pit floor), the pool and the rubble
  added, cut as holes_rocks_tl ... _br are (origin).

usage: Blender -b --factory-startup -P wave3_ap_pit.py -- [--only name,name] [--preview <prefix>] [--check 1]
       [--stats 1] [--whole <prefix>]
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_ap_kit as kit  # noqa: E402
from wave3_ap_kit import k, w, pal  # noqa: E402

orig = kit.load("wave3_aa_rocks")
aa = orig.kit
n = aa.n
kit.forget(n.MODELS, n.OBJECTS)

DAMAGED = orig.Frame(kit.art.ROCKS_DMG, 72, (36, 28))
POOL_RAMPS = (5, 9, 0xa)


def is_pool(v):
    return v is not None and v >> 4 in POOL_RAMPS


def pit_damaged():
    # The original whole without its boulders and stones, from the damaged pixels (its dirt and its pit floor).
    saved = orig.ROCKS, orig.BOULDERS, orig.PEBBLES
    orig.ROCKS, orig.BOULDERS, orig.PEBBLES = DAMAGED, [], []
    try:
        orig.rocks_whole()
    finally:
        orig.ROCKS, orig.BOULDERS, orig.PEBBLES = saved
    w.bake()
    f = DAMAGED
    # The pool: a still, glossy surface over the blue pixels, a little under the dirt's top, glowing faintly.
    paint = aa.Painter("pit_dmg_pool", shades={9: (0, 1, 2, 3, 4, 5, 6, 8, 10, 12, 14), 0xa: (0, 1, 2, 3),
                                              5: (0, 1, 2)},
                       metallic=0.1, roughness=0.06,
                       glow={0x90 + s: 0.15 + 0.07 * s for s in range(16)})
    polys = aa.outlines_of(f, lambda v, c, r: is_pool(v), grow=0.4, smooth=2)
    pool = kit.ag.heightfield("pool", polys, lambda x, y, e: 0.35 + 0.25 * e, None, spacing=0.8, edge=1.2)
    aa.pixelate(pool, f)
    aa.paint_sprite(pool, f, paint, wall_steps=-2, keep=is_pool, blur=1)
    kit.delete_faces_down(pool)
    aa.merge_flat(pool)
    # The rubble: a stone over each clump of the sprite's grey pixels round the pool.
    greys = {s: pal(f"pit_dmg_grey{s:x}", s, metallic=0.08, roughness=0.75) for s in (2, 3, 4, 5, 6, 7, 8, 9)}
    seen = set()
    rnd = random.Random(5)
    stones = 0
    for r in range(len(f.g)):
        for c in range(f.width):
            v = f.get(c, r)
            if (c, r) in seen or v is None or v >> 4 != 0 or (v & 15) < 2:
                continue
            clump, todo = [], [(c, r)]
            seen.add((c, r))
            while todo:
                cc, rr = todo.pop()
                clump.append((cc, rr, f.get(cc, rr)))
                for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nv = f.get(cc + dc, rr + dr)
                    if (cc + dc, rr + dr) not in seen and nv is not None and nv >> 4 == 0 and (nv & 15) >= 2:
                        seen.add((cc + dc, rr + dr))
                        todo.append((cc + dc, rr + dr))
            if len(clump) < 2:
                continue
            mc = sum(p[0] for p in clump) / len(clump)
            mr = sum(p[1] for p in clump) / len(clump)
            shade = sum(p[2] & 15 for p in clump) / len(clump) - 0.5
            rad = 0.55 * math.sqrt(len(clump)) + 0.3
            sx = max(p[0] for p in clump) - min(p[0] for p in clump) + 1
            sy = max(p[1] for p in clump) - min(p[1] for p in clump) + 1
            rx, ry = max(0.7, min(rad * 1.3, sx * 0.55)), max(0.7, min(rad * 1.3, sy * 0.55))
            mat = greys[min(greys, key=lambda s: abs(s - shade))]
            w.lumpy(f"stone{stones}", (f.X(mc), f.Y(mr), 0.3), (rx, ry, min(rx, ry) * rnd.uniform(0.6, 0.9)), mat,
                    seed=30 + stones, amount=0.35, segments=8, rings=5)
            stones += 1
    for obj in w.meshes():
        if obj.name.startswith("stone"):
            k.smooth(obj, 50)


aa.pieced("holes_rocks_damaged", pit_damaged, (72, 56),
          aa.grid_pieces("holes_rocks_", DAMAGED, [s + "_damaged" for s in ("tl", "tm", "tr", "bl", "bm", "br")], 3, 2))


if __name__ == "__main__":
    aa.run()
