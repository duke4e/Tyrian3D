"""Enemies of wave 3, batch AE (sheet ', written x27 in models.cfg): FRUIT's strawberry wing,
modelled as its sprites look (models.cfg: yaw=0); the rest of the sheet is in wave3_ae_boss.py and
polish_*.py (the lemon beetle: polish_lemon_beetle.py), the kit in wave3_ae_kit.py, the pixels in wave3_ae_art.py.
It is built whole and cut into the sprites the level puts it together from (origin).

- strawberry_wing_tl, _tm, _tr, _bl, _br (' 86 88 90 above 125 127; enemies 1233-1235 at (x, y - 28),
  (x + 24, y - 28), (x + 48, y - 28), 1236, 1237 at (x + 12, y), (x + 36, y), in the sky or on top): a red
  chevron of strawberry flesh studded with golden seeds, 72 x 56, grey pipes bent along its two arms in an M,
  a grey missile pod down its middle.

usage: Blender -b --factory-startup -P wave3_ae_lemon.py -- [--only name,name] [--preview <prefix>]
       [--check 1] [--stats 1] [--whole <prefix>]
"""
import os
import sys

from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_ae_kit as kit  # noqa: E402
from wave3_ae_kit import sh, w, pal, Painter  # noqa: E402


# --- ' 86 88 90 / 125 127: the strawberry wing ----------------------------------------------------------

BERRY = kit.frame("BERRY", 72, (36, 28))
POD_BOX = (32, 39, 19, 41)  # the missile pod's pixels (columns, rows, inclusive), modelled apart


def is_steel(f, c, r):
    """The pipes' pixels: grey, or a brass stripe between grey ones."""
    val = f.get(c, r)
    if val is None:
        return False
    if val >> 4 == 0:
        return True
    if val >> 4 == 1:
        grey = sum(1 for dc, dr in ((-1, 0), (1, 0), (0, -1), (0, 1))
                   if f.get(c + dc, r + dr) is not None and f.get(c + dc, r + dr) >> 4 == 0)
        return grey >= 2
    return False


def in_pod(c, r):
    return POD_BOX[0] <= c <= POD_BOX[1] and POD_BOX[2] <= r <= POD_BOX[3]


def strawberry_wing_whole():
    f = BERRY
    flesh = Painter("sberry", shades={7: (0, 1, 2, 3, 4, 5, 6)}, metallic=0.0, roughness=0.55)
    # The flesh: a thick chevron, its top bulging and knobbly, painted by the sprite's reds.
    polys = kit.outlines_of(f, lambda val, c, r: True, smooth=2, epsilon=0.3, min_area=3.0)
    body = kit.relief("sberry_flesh", polys, flesh(0x73), sh.pillow_profile(3.4, 3.0, crown=1.4), bottom=0.0,
                      base=0.0, rim=0.6, spacing=0.5)
    kit.bumps(body, 0.12, 1.6, seed=5.0, min_z=1.0)
    kit.paint_sprite(body, f, flesh, wall_steps=-1, keep=lambda val: val >> 4 == 7, default=flesh(0x72),
                     under=flesh(0x70))
    # The golden seeds, set into the flesh where the sprite draws them.
    seed = pal("sberry_seed", 0x17, metallic=0.5, roughness=0.3)
    seeds = []
    for i, (cx, cy, count, best) in enumerate(kit.aa.blobs(f.g, lambda val: val is not None and val >> 4 == 1)):
        c, r = int(cx), int(cy)
        if is_steel(f, c, r) or in_pod(c, r):
            continue
        x, y = cx - f.ox, f.oy - cy
        z = kit.surface_z([body], x, y, 3.0)
        seeds.append(w.sphere(f"sberry_seed{i}", (x, y, z - 0.15), (0.75, 0.95, 0.5), seed, 8, 4))
    kit.join(seeds, "sberry_seeds")
    # The pipes: an M of bent steel pipe across the top, two straight ones along the lower arms, brass bands on
    # them where the sprite draws brass.
    steel = pal("spipe", 0x0a, metallic=0.5, roughness=0.28)
    steel_dark = pal("spipe_dark", 0x06, metallic=0.5, roughness=0.35)
    brass = pal("spipe_brass", 0x17, metallic=0.7, roughness=0.3)

    def P(c, r, z):
        return (c - f.ox, f.oy - r, z)
    zp = 5.0
    m_path = [P(10.6, 22.6, zp - 0.6), P(24.5, 8.6, zp), P(36.0, 20.0, zp - 0.4), P(47.5, 8.6, zp), P(61.4, 22.6, zp - 0.6)]
    pipes = [kit.pipe("spipe_m", m_path, 3.15, steel, bend=3.0)]
    for side in (-1, 1):
        c0, c1 = (19.8, 28.9) if side < 0 else (52.2, 43.1)
        pipes.append(kit.pipe(f"spipe_low{side:+d}", [P(c0, 28.9, zp - 0.8), P(c1, 37.8, zp - 0.8)], 2.85, steel))
        a0, a1 = Vector(P(c0, 28.9, zp - 0.8)), Vector(P(c1, 37.8, zp - 0.8))
        axis = (a1 - a0).normalized()
        for j, t in enumerate((0.22, 0.5, 0.78)):
            band = kit.torus(f"spipe_band{side:+d}_{j}", (0.0, 0.0, 0.0), 2.95, 0.42, brass, 28, 8)
            band.data.transform(Matrix.Translation(a0 + (a1 - a0) * t) @ axis.to_track_quat("Z", "Y").to_matrix().to_4x4())
        # Bands near the M's outer ends.
        e0, e1 = Vector(m_path[0 if side < 0 else -1]), Vector(m_path[1 if side < 0 else -2])
        axis = (e1 - e0).normalized()
        band = kit.torus(f"spipe_mband{side:+d}", (0.0, 0.0, 0.0), 3.25, 0.45, brass, 28, 8)
        band.data.transform(Matrix.Translation(e0 + (e1 - e0) * 0.16) @ axis.to_track_quat("Z", "Y").to_matrix().to_4x4())
    for p_ in pipes:
        kit.paint_faces(p_, lambda c, nrm: steel_dark if nrm.z < -0.2 else None)
    # The missile pod down the middle, its nose down the screen.
    pod = Painter("spod", shades={0: (5, 6, 7, 8, 9, 0xa, 0xb, 0xc, 0xd)}, metallic=0.55, roughness=0.25)
    x0 = (POD_BOX[0] + POD_BOX[1] + 1) / 2 - f.ox
    top, nose = f.oy - POD_BOX[2], f.oy - POD_BOX[3] - 0.5
    length = top - nose
    profile = [(0.0, 2.0), (0.06 * length, 2.9), (0.25 * length, 3.2), (0.6 * length, 3.0), (0.8 * length, 2.3),
               (0.93 * length, 1.1), (length, 0.2)]
    shell = kit.lathe_axis("spod", profile, pod(0x09), (x0, top, 5.2), (0, -1, 0), 24, squash=0.95)
    kit.paint_sprite(shell, f, pod, wall_steps=-1, keep=lambda val: val >> 4 == 0, default=pod(0x08), blur=1,
                     probe=-0.8)
    ring = pal("spod_ring", 0x17, metallic=0.7, roughness=0.3)
    kit.band_y("spod_ring", (x0, top - 0.25 * length, 5.2), 3.15, 0.45, ring, squash=0.95)
    kit.band_y("spod_ring2", (x0, top - 0.6 * length, 5.2), 2.95, 0.45, ring, squash=0.95)


kit.PROTECT += ["sberry_flesh"]
kit.pieced("strawberry_wing", strawberry_wing_whole, (72, 56),
           [kit.piece("strawberry_wing_tl", BERRY, 0, 0), kit.piece("strawberry_wing_tm", BERRY, 24, 0),
            kit.piece("strawberry_wing_tr", BERRY, 48, 0), kit.piece("strawberry_wing_bl", BERRY, 12, 28),
            kit.piece("strawberry_wing_br", BERRY, 36, 28)])


if __name__ == "__main__":
    kit.run()
