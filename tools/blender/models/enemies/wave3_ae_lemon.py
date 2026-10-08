"""Enemies of wave 3, batch AE (sheet ', written x27 in models.cfg): FRUIT's lemon beetle and strawberry wing,
modelled as their sprites look (models.cfg: yaw=0); the rest of the sheet is in wave3_ae.py, wave3_ae_coral.py and
wave3_ae_boss.py, the kit in wave3_ae_kit.py, the pixels in wave3_ae_art.py. Both are built whole and cut into the
sprites the level puts them together from (origin).

- lemon_beetle_tl, _tr, _ml, _mr, _bl, _br (' 16 18 above 54 56 above 92 94; enemies 1238-1243 at (x, y - 56),
  (x + 24, y - 56), (x, y - 28), (x + 24, y - 28), (x, y), (x + 24, y), on top): a yellow beetle, 48 x 84, its
  domed back in overlapping plates, two horns curving up and in from its shoulders, a broad head with two lemon
  slices for eyes (their juice glowing, white pith between the segments) and two long pincers curving down.
- strawberry_wing_tl, _tm, _tr, _bl, _br (' 86 88 90 above 125 127; enemies 1233-1235 at (x, y - 28),
  (x + 24, y - 28), (x + 48, y - 28), 1236, 1237 at (x + 12, y), (x + 36, y), in the sky or on top): a red
  chevron of strawberry flesh studded with golden seeds, 72 x 56, grey pipes bent along its two arms in an M,
  a grey missile pod down its middle.

usage: Blender -b --factory-startup -P wave3_ae_lemon.py -- [--only name,name] [--preview <prefix>]
       [--check 1] [--stats 1] [--whole <prefix>]
"""
import math
import os
import sys

from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_ae_kit as kit  # noqa: E402
from wave3_ae_kit import k, sh, w, pal, Painter  # noqa: E402


# --- ' 16 18 / 54 56 / 92 94: the lemon beetle ------------------------------------------------------------

LEMON = kit.frame("LEMON", 48, (24, 42))
BODY_C, BODY_R = Vector((0.0, 10.0, 1.0)), (20.2, 14.2, 12.5)
HEAD_C, HEAD_R = Vector((0.0, -12.3, 0.5)), (24.2, 9.0, 9.0)
SLICE_X, SLICE_Y, SLICE_R = 9.6, -12.2, 7.7


def ribbed(obj, centre, amount=1.1, period=5.2, top_row_y=20.6, bow=0.022):
    """The back's overlapping plates: each rises towards its lower edge (down the screen) and drops into
    the crease under it, the creases bowed like the sprite's (higher in the middle)."""
    c = Vector(centre)
    for vt in obj.data.vertices:
        if vt.co.z < c.z + 0.5:
            continue
        y = vt.co.y + bow * vt.co.x * vt.co.x
        s = (top_row_y - y) / period
        frac = s - math.floor(s)
        # A smooth sawtooth: up over the plate, a quick fall into the crease.
        rise = frac / 0.82 if frac < 0.82 else 1.0 - (frac - 0.82) / 0.18
        d = amount * (kit.smoothstep(0.0, 1.0, rise) - 0.5)
        fade = min(1.0, (vt.co.z - c.z) / 4.0)
        vt.co += (vt.co - c).normalized() * d * fade
    obj.data.update()
    return obj


def lemon_beetle_whole():
    f = LEMON
    yellow = Painter("lemon", shades={7: (0xa, 0xb, 0xc, 0xd, 0xe)}, metallic=0.1, roughness=0.32)
    # The back: a dome in overlapping plates, painted pixel by pixel (its creases and their lit edges).
    body = w.sphere("lemon_body", tuple(BODY_C), BODY_R, yellow(0x7c), 72, 40)
    ribbed(body, BODY_C)
    kit.pixelate(body, f)
    kit.paint_sprite(body, f, yellow, wall_steps=-1, default=yellow(0x7b), probe=-1.0, under=yellow(0x7a), blur=1)
    # The head: a broad, lower block with rounded edges under the back's lower edge, as wide as the sprite's.
    polys = kit.outlines_of(f, lambda val, c, r: 44 <= r <= 62, smooth=2, epsilon=0.3, min_area=2.0)
    head = kit.relief("lemon_head", polys, yellow(0x7c), sh.pillow_profile(6.0, 5.0, crown=1.8), bottom=0.0,
                      base=0.0, rim=0.6, spacing=0.5)
    kit.pixelate(head, f)
    kit.paint_sprite(head, f, yellow, wall_steps=-1, default=yellow(0x7b), probe=-1.0, under=yellow(0x7a), blur=1,
                     keep=lambda val: val not in (0x7e, 0x7f))
    # The lemon slices, glowing, lying on the head and tilted a little outwards.
    for side in (-1, 1):
        z = kit.surface_z([head], side * SLICE_X, SLICE_Y, 7.0)
        kit.lemon_slice(f"lemon_eye{side:+d}", side * SLICE_X, SLICE_Y, z + 0.4, SLICE_R, side * 12)
    # The horns: from the shoulders up and in, their tips nearly meeting over the middle.
    horn = Painter("lhorn", shades={7: (0xa, 0xb, 0xc, 0xd)}, metallic=0.15, roughness=0.3)
    horn_path = [(-10.6, 17.0, 7.5), (-10.4, 23.5, 10.5), (-10.6, 29.5, 12.0), (-8.6, 35.5, 12.2), (-5.6, 39.6, 11.2),
                 (-2.6, 41.6, 10.0)]
    horn_r = [3.6, 3.4, 3.3, 3.0, 2.3, 0.9]
    # The pincers: from under the head's sides down and in.
    pincer_path = [(-19.6, -16.5, 4.0), (-17.6, -21.5, 5.4), (-16.2, -26.0, 6.0), (-15.2, -31.0, 5.4), (-14.2, -35.5, 4.8),
                   (-12.6, -38.6, 4.2), (-10.0, -40.8, 3.8), (-8.6, -41.8, 3.6)]
    pincer_r = [5.0, 4.0, 3.6, 3.2, 2.9, 2.4, 1.4, 0.4]
    for side in (-1, 1):
        for name, path, radii in (("horn", horn_path, horn_r), ("pincer", pincer_path, pincer_r)):
            pts = [(-side * x if side > 0 else x, y, z) for x, y, z in path]
            limb = kit.limb(f"lemon_{name}{side:+d}", pts, radii, horn(0x7c), segments=16, squash=0.85)
            kit.paint_sprite(limb, f, horn, wall_steps=-1, default=horn(0x7b), probe=-0.6, under=horn(0x7a))
    sh.flat_bottom(kit.meshes(), 0.0)


kit.PROTECT += ["lemon_body", "lemon_head", "lemon_eye"]
kit.pieced("lemon_beetle", lemon_beetle_whole, (48, 84),
           kit.grid_pieces("lemon_beetle_", LEMON, ["tl", "tr", "ml", "mr", "bl", "br"], 2, 3))


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
