"""Batch AG of wave 3 (sheet u): DELI's two towers (DELI and New Deli, on the ground) and their damaged looks,
modelled as the sprites look (models.cfg: yaw=0). The kit is wave3_ag_kit.py, the pixels wave3_ag_art.py
(TOWER_A, TOWER_B in TOWER_A's frame, TOWER_A_DMG).

The level events put each tower together from its sprites: tower A from u 1, 3, 5 above 39, 41, 43 (enemies
245-250 at (x, y - 56) ... (x + 48, y - 28)) and u 79 under the middle (enemy 251 at (x + 24, y)); tower B, the
same tower with its left third left off, from u 15, 17 above 53, 55 (enemies 253, 254, 256, 257), u 79 under
the left (258), and two small sprites, u 19 above u 38 (252 at (x - 18, y - 50), 255 at (x - 18, y - 36)),
for its rounded bow. Both are 72 x 84 here (tower B in tower A's frame, its columns 12-72), origin (36, 42).

What it is: a long hull lying across the screen on a mast that runs down the screen into a turret in a
square bay of floor; from the hull's far side five spires reach up the screen, rising a little towards
their tips (a capped red column, the tallest with a purple crystal and a red rail, a red stub, a grey
block cabin, a small capped post), and at its right end a capsule holds an eye-like lens (purple in tower
A, red in tower B).
- Tower A (deli_tower_1, 3, 5, 39, 41, 43): the hull is open, its plating stripped to a framework of grey
  girders, red blocks and purple plates over dark gaps (each kind of pixel raised to its own depth under
  the hull's curve). deli_tower_1 replaces wave2_g's deli_tower_tl (the same corner, now cut from the
  whole tower so that it meets the other pieces).
- Tower B (deli_tower_15, 17, 19, 38, 53, 55): the hull is shut, a smooth grey shell with red vents along
  its bow and a red hatch under it.
- deli_tower_79: the turret in its bay, under either tower (both put u 79 under the column whose mast it
  is): a dark rounded housing with a pit where the mast comes down, a red panel at its side, a purple vent.
- The damaged looks (dgr, which an enemy switches to when hit hard, in place): deli_tower_7, 9, 11 (of u 1,
  3, 5 and of u 19, 15, 17): the spires snapped off to scorched stumps, the cabin broken, everything burnt
  grey; deli_tower_127 (of u 43 and u 55): the capsule shot away, wreckage strewn where it was;
  deli_tower_77 (of u 79): the turret burnt out, its vent gone, a crack glowing. (39, 41, 38 and 53
  switch to burning animations instead, which keep their intact models.)

usage: Blender -b --factory-startup -P wave3_ag_tower.py -- [--only name,name] [--preview <prefix>]
       [--check 1] [--stats 1] [--whole <prefix>]
"""
import math
import os
import sys

from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_ag_kit as kit  # noqa: E402
from wave3_ag_kit import k, w, pal, Painter, smoothstep  # noqa: E402

ORIGIN = (36, 42)
TOWER_A = kit.frame("TOWER_A", 72, ORIGIN)
TOWER_B = kit.frame("TOWER_B", 72, ORIGIN)
TOWER_D = kit.frame("TOWER_A_DMG", 72, ORIGIN)


def X(col):
    return col + 0.5 - ORIGIN[0]


def Y(row):
    return ORIGIN[1] - (row + 0.5)


def painter(prefix):
    return Painter(prefix, shades={0: (1, 2, 3, 4, 5, 6, 7, 8, 9, 0xa, 0xb, 0xc, 0xd),
                                   4: (2, 4, 5, 6, 7, 8, 9, 0xa, 0xb, 0xc, 0xd),
                                   5: (1, 2, 4, 5, 6, 7, 8, 9, 0xa, 0xb, 0xc, 0xd, 0xe),
                                   6: (1, 3, 5), 1: (0, 1, 2, 3), 0xa: (1, 2, 4, 6, 7),
                                   7: (0, 2, 4, 6, 8, 0xa, 0xc, 0xe)},
                   metallic=0.55, roughness=0.35,
                   glow={0x74: 0.4, 0x76: 0.7, 0x78: 1.0, 0x7a: 1.3, 0x7c: 1.6, 0x7e: 2.0},
                   finish={4: (0.35, 0.38), 5: (0.3, 0.28), 6: (0.1, 0.75), 1: (0.3, 0.5), 0xa: (0.3, 0.5),
                           7: (0.0, 0.4)},
                   remap={0x00: 0x01})


def paint(obj, f, p, walls=-2, probe=-0.6, default=None, blur=0, grid=False, side=None, shift=0.0):
    """Paints a part by the sprite's pixels (its underside one dark colour), then merges flat stretches of
    one colour into few triangles; grid: its faces cut along the pixel grid first (boxes, slabs: large faces
    that would take one pixel's colour); side: (material, normal z) faces steeper than that take the material
    (the sides of domed parts, which would otherwise take stripes of pixels)."""
    if grid:
        kit.pixelate(obj, f, step=1.0)
    kit.paint_sprite(obj, f, p, wall_steps=walls, blur=blur, probe=probe, under=p(0x01),
                     default=default if default is not None else p(0x03), shade_shift=shift)
    if side is not None:
        mat, nz = side
        kit.paint_faces(obj, lambda c, nrm: mat if -0.5 <= nrm.z < nz else None)
    # Faces looking straight down are never seen from above: left out.
    kit.delete_faces(obj, lambda c, nrm: nrm.z < -0.95)
    return kit.merge_flat(obj, angle=1.0)


def region(f, keep, smooth=1):
    """The outlines of the frame's pixels keep(index, column, row) accepts (smooth: rounds of corner
    cutting, for large parts whose pixel steps should not show as ridges down their sides)."""
    return kit.polys_of(f, lambda v, c, r: v is not None and keep(v, c, r), smooth=smooth,
                        epsilon=0.3 if smooth < 2 else 0.45, min_area=1.0)


# --- The hull's curve -------------------------------------------------------------------------------------

HULL_RIDGE = 9.0      # y of the hull's ridge
HULL_NORTH = 8.6      # the ridge to its far (north) edge
HULL_SOUTH = 14.2     # the ridge to its near (south) edge, where it curves under


def hull_env(x, y):
    """The height of the shut hull's top over (x, y): a long body lying across the screen, its ridge
    nearer its far side, lower towards its bow (left) and its stern (right)."""
    t = (y - HULL_RIDGE) / (HULL_NORTH if y > HULL_RIDGE else HULL_SOUTH)
    across = math.sqrt(max(0.0, 1.0 - t * t))
    along = (0.5 + 0.5 * smoothstep(-31.0, -12.0, x)) * (1.0 - 0.22 * smoothstep(12.0, 21.0, x))
    return 1.2 + 12.8 * across ** 0.85 * along


# --- The spires ---------------------------------------------------------------------------------------------

def tilt(y):
    """The spires' axis height: rising up the screen."""
    return 11.0 + (y - 12.0) * 0.17


def spire(name, x, profile, mat, segments=16):
    """A turned spire lying along the screen at x, its axis rising with tilt(); profile: (y, radius) pairs,
    increasing y (from the foot inside the hull to the tip)."""
    dense = [profile[0]]
    for (ya, ra), (yb, rb) in zip(profile, profile[1:]):  # a ring every pixel, for painting
        steps = max(1, int(round(yb - ya)))
        dense += [(ya + (yb - ya) * i / steps, ra + (rb - ra) * i / steps) for i in range(1, steps + 1)]
    profile = dense
    y0, y1 = profile[0][0], profile[-1][0]
    start = Vector((x, y0, tilt(y0)))
    end = Vector((x, y1, tilt(y1)))
    scale = (end - start).length / (y1 - y0)
    return w.lathe_axis(name, [((y - y0) * scale, r) for y, r in profile], mat, tuple(start), tuple(end - start),
                        segments, smooth_angle=50)


def spires(f, p, broken=False):
    """The five spires on the hull's far side (rows 0-27 of the sprites, the same in both towers)."""
    parts = []
    grey = p(0x08)
    # S1 (columns 30-32 in an outline from 29 to 33): a red column with a grey cap, thinner below (rows
    # 18-23, columns 31-32).
    s1 = [(12.0, 1.8), (18.5, 1.8), (19.5, 1.85), (24.6, 1.9), (25.2, 2.35), (31.0, 2.35), (31.4, 2.6),
          (32.0, 2.6), (32.3, 2.45), (36.2, 2.45), (37.2, 1.9), (37.8, 1.0), (38.0, 0.2)]
    sx = X(31) + 0.15
    if not broken:
        parts.append(spire("s1", sx, s1, grey))
    else:
        stump = spire("s1", sx, [pt for pt in s1 if pt[0] < 23.5] + [(23.8, 1.9)], grey)
        kit.jag(stump, (sx, 23.8, tilt(23.8)), (0, 1, 0.17), 1.6, seed=1.0)
        parts.append(stump)
    # S3 (columns 36-37): a short red stub, a thin grey rod beside it (column 34), and the grey cross-piece
    # at their feet (columns 33-40, rows 20-24).
    parts.append(spire("s3", X(36.5), [(12.0, 1.6), (26.2, 1.6), (27.0, 1.1), (27.6, 0.2)], grey, 12))
    parts.append(spire("s3_rod", X(34), [(12.0, 0.6), (23.5, 0.6), (24.0, 0.2)], grey, 8))
    parts.append(w.rounded_box("s_cross", (X(36.5), Y(22.0), tilt(Y(22.0)) + 0.6), (8.2, 5.0, 2.8), grey, bevel=0.7))
    # S2 (columns 42-46): the tallest, a red block column; on it a purple crystal (columns 41-43) and a red
    # rail (columns 45-46).
    if not broken:
        parts.append(spire("s2", X(44), [(12.0, 3.0), (28.6, 3.1), (29.3, 2.8), (29.7, 1.4)], grey, 18))
        parts.append(spire("s2_collar", X(42.5), [(28.8, 2.2), (31.3, 2.2), (31.7, 1.6)], grey, 10))
        parts.append(spire("s2_crystal", X(42), [(31.0, 1.8), (37.5, 2.0), (40.2, 1.5), (41.9, 0.25)], grey, 6))
        parts.append(spire("s2_rail", X(45.6), [(29.0, 1.3), (35.8, 1.3), (36.4, 0.9), (36.8, 0.2)], grey, 10))
    else:
        stump = spire("s2", X(44), [(12.0, 3.0), (25.8, 3.05)], grey, 18)
        kit.jag(stump, (X(44), 25.8, tilt(25.8)), (0, 1, 0.17), 2.2, seed=2.0)
        parts.append(stump)
    # S4 (columns 47-56): the grey block cabin, a wide lower block on the hull and a smaller one on it.
    if not broken:
        parts.append(w.rounded_box("s4_low", (X(50.5), Y(24.0), tilt(Y(24.0)) - 0.8), (9.6, 10.0, 7.5), grey,
                                   bevel=1.4))
        parts.append(w.rounded_box("s4_high", (X(50.5), Y(16.0), tilt(Y(16.0)) - 0.4), (7.6, 8.0, 6.6), grey,
                                   bevel=1.6))
    else:
        low = w.rounded_box("s4_low", (X(50.5), Y(25.0), tilt(Y(25.0)) - 1.4), (9.6, 8.0, 6.8), grey, bevel=1.2)
        kit.jag(low, (X(50.5), Y(20.0), 0.0), (0, 1, 0), 2.6, scale=1.1, seed=3.0)
        parts.append(low)
    # S5 (columns 20-23 in an outline from 19 to 24): a small post with a grey cap.
    parts.append(spire("s5", X(21.5), [(12.5, 2.2), (19.0, 2.2), (19.4, 2.55), (21.9, 2.55), (22.5, 1.8),
                                       (22.9, 0.3)], grey, 14))
    for obj in parts:
        paint(obj, f, p, walls=-2, probe=-0.4, grid=obj.name.startswith(("s4", "s_cross")))
    return parts


# --- The hulls ----------------------------------------------------------------------------------------------

def is_hull(c, r):
    return 24 <= r < 48 and c < 55


def hull_shut(g, f, p):
    """Tower B's shell: the hull's pixels, its top on hull_env, its edges rounded under; a red hatch under it."""
    polys = region(g, lambda v, c, r: is_hull(c, r), smooth=3)
    shell = kit.heightfield("hull", polys, lambda x, y, e: hull_env(x, y) * (0.1 + 0.9 * e * e), p(0x07),
                            spacing=0.7, edge=3.2)
    paint(shell, f, p, walls=-1, probe=-0.8, side=(p(0x04), 0.45), blur=1)
    # The hatch under the hull (columns 36-41, rows 38-43) and the ledge over it (row 35-36).
    hatch = w.rounded_box("hatch", (X(38.5), Y(41.0), hull_env(X(38.5), Y(41.0)) - 0.6), (6.6, 7.0, 2.6), p(0x46),
                          bevel=0.6)
    ledge = w.rounded_box("ledge", (X(36.0), Y(35.2), hull_env(X(36.0), Y(35.2)) - 0.4), (11.6, 2.2, 2.0), p(0x0a),
                          bevel=0.5)
    for obj in (hatch, ledge):
        paint(obj, f, p, walls=-2, probe=-0.4, grid=True)
    return [shell, hatch, ledge]


DEPTH = {"gap": 0.5, "dark": 0.72, "mid": 0.8, "light": 0.88, "red": 0.86, "purple": 0.97, "brown": 0.55}


def kind(v):
    ramp, shade = v >> 4, v & 15
    if ramp == 0:
        return "gap" if shade <= 2 else "dark" if shade <= 5 else "mid" if shade <= 8 else "light"
    if ramp == 4:
        return "red"
    if ramp == 5:
        return "purple"
    if ramp == 7:
        return "gap"
    return "brown"


def cleaned_kinds(f, inside):
    """The kinds of the pixels inside(c, r), each taking the kind most of its 3 x 3 neighbourhood has when
    it is alone (single stray pixels join their surroundings)."""
    out = {}
    for r in range(f.height):
        for c in range(f.width):
            v = f.get(c, r)
            if v is None or not inside(c, r):
                continue
            out[(c, r)] = kind(v)
    clean = {}
    for (c, r), kd in out.items():
        counts = {}
        for dc in (-1, 0, 1):
            for dr in (-1, 0, 1):
                n = out.get((c + dc, r + dr))
                if n is not None:
                    counts[n] = counts.get(n, 0) + 1
        clean[(c, r)] = kd if counts.get(kd, 0) >= 2 else max(counts, key=counts.get)
    return clean


def nest(polys):
    """Polygons (even-odd outlines) as (outer, [holes]): each hole with the smallest outline round it."""
    def inside(poly, pt):
        x, y = pt
        hit = False
        for i in range(len(poly)):
            (ax, ay), (bx, by) = poly[i], poly[i - 1]
            if (ay > y) != (by > y) and x < ax + (y - ay) * (bx - ax) / (by - ay):
                hit = not hit
        return hit

    def area(poly):
        return abs(sum(poly[i][0] * poly[i - 1][1] - poly[i - 1][0] * poly[i][1] for i in range(len(poly)))) / 2
    containers = [[j for j, q in enumerate(polys) if j != i and inside(q, polys[i][0])] for i in range(len(polys))]
    out = {i: [] for i, c in enumerate(containers) if len(c) % 2 == 0}
    for i, c in enumerate(containers):
        if len(c) % 2 == 1:
            owner = min((j for j in c if j in out), key=lambda j: area(polys[j]), default=None)
            if owner is not None:
                out[owner].append(polys[i])
    return [(polys[i], holes) for i, holes in out.items()]


def hull_open(g, f, p):
    """Tower A's framework: the hull's pixels in layers by kind, each raised to its depth under hull_env
    (purple plates of the skin highest, then light girders, red blocks, grey frames, dark machinery, and
    the dark gaps deep inside)."""
    kinds = cleaned_kinds(g, is_hull)
    parts = []
    # The dark inside, deep under the framework: a dark body following the hull's curve at half its height.
    base = kit.heightfield("hull_gaps", region(g, lambda v, c, r: is_hull(c, r), smooth=2),
                           lambda x, y, e: hull_env(x, y) * DEPTH["gap"] * (0.2 + 0.8 * e * e), p(0x04), spacing=1.5,
                           edge=2.0)
    kit.paint_faces(base, lambda c, nrm: p(0x04) if nrm.z > 0.5 else p(0x03) if nrm.z > -0.5 else p(0x01))
    kit.delete_faces(base, lambda c, nrm: nrm.z < -0.95)
    kit.merge_flat(base, angle=1.0)
    parts.append(base)
    for name in ("dark", "mid", "light", "red", "purple", "brown"):
        polys = kit.polys_of(g, lambda v, c, r, name=name: kinds.get((c, r)) == name, smooth=1, epsilon=0.3,
                             min_area=1.5)
        blocks = []
        for i, (outer, holes) in enumerate(nest(polys)):
            # Each block flat-topped at its depth under the hull's curve over its middle (few triangles once
            # painted and merged), its edges rounded.
            cx = sum(x for x, _ in outer) / len(outer)
            cy = sum(y for _, y in outer) / len(outer)
            top = hull_env(cx, cy) * DEPTH[name]
            blocks.append(kit.heightfield(f"hull_{name}_{i}", [outer] + holes,
                                          lambda x, y, e, top=top: top * (0.55 + 0.45 * e), p(0x05),
                                          spacing=0.65 if name in ("red", "purple", "light") else 0.9, edge=0.6))
        if blocks:
            parts.append(kit.join(blocks, f"hull_{name}"))
    # Painted two shades lighter than the sprite (the framework reads better lit), in fewer shades (flat tops
    # of one colour merge into few triangles).
    coarse = Painter("tower", shades={0: (3, 5, 7, 9, 0xb, 0xd), 4: (5, 7, 9, 0xb, 0xd), 5: (5, 7, 9, 0xb, 0xd),
                                      1: (1, 3), 0xa: (2, 5), 7: (2, 6, 0xa, 0xe), 6: (1, 3, 5)},
                     metallic=p.metallic, roughness=p.roughness, glow=p.glow, finish=p.finish, remap=p.remap)
    coarse.cache = p.cache
    for obj in parts[1:]:
        paint(obj, f, coarse, walls=-2, probe=-0.35, shift=2.0)
    return parts


# --- The capsule with its lens --------------------------------------------------------------------------------

def capsule(g, f, p, lens_ramp):
    """The capsule at the hull's right end (columns 55-71), a lens of the sprite's colour set in its top."""
    polys = region(g, lambda v, c, r: c >= 55 and 26 <= r < 48, smooth=3)

    def z_of(x, y, e):
        return (1.2 + 9.6 * math.sqrt(max(0.0, 1.0 - ((y - 4.6) / 11.5) ** 2))) * (0.08 + 0.92 * e * e)
    body = kit.heightfield("capsule", polys, z_of, p(0x07), spacing=0.6, edge=4.0)
    paint(body, f, p, walls=-1, probe=-0.8, side=(p(0x05), 0.62), blur=1)
    # The lens over the sprite's pixels of its colour; its pupil where they are brightest.
    pts = [(c, r, g.get(c, r)) for r in range(28, 44) for c in range(54, 72)
           if g.get(c, r) is not None and g.get(c, r) >> 4 == lens_ramp]
    c0, c1 = min(c for c, _, _ in pts), max(c for c, _, _ in pts)
    r0, r1 = min(r for _, r, _ in pts), max(r for _, r, _ in pts)
    lx, ly = X((c0 + c1) / 2), Y((r0 + r1) / 2)
    ax, ay = (c1 - c0 + 1) / 2, (r1 - r0 + 1) / 2
    at = Vector((lx, ly, z_of(lx, ly, 1.0)))
    rim = kit.lens("capsule_lens_rim", at, (0.0, 0.0, 1.0), (ax + 0.6, ay + 0.6, 0.9), p(0x02), sink=0.5, segments=24)
    lens = kit.lens("capsule_lens", at + Vector((0, 0, 0.15)), (0.0, 0.0, 1.0), (ax - 0.1, ay - 0.1, 1.3),
                    p(lens_ramp * 16 + 8), sink=0.3, segments=24)
    paint(lens, f, p, walls=0, probe=0.0)
    hot = [(c, r) for c, r, v in pts if v & 15 >= max(v2 & 15 for _, _, v2 in pts) - 1]
    bx, by = X(sum(c for c, _ in hot) / len(hot)), Y(sum(r for _, r in hot) / len(hot))
    bead = pal(f"capsule_bead_{lens_ramp:x}", lens_ramp * 16 + 0xd, metallic=0.1, roughness=0.15, glow=0.6)
    w.sphere("capsule_lens_bead", (bx, by, at.z + 1.25), (1.1, 1.0, 0.55), bead, 14, 7)
    return [body, rim, lens]


def wreckage(g, f, p):
    """Where the capsule was (u 127): low twisted wreckage over the sprite's pixels, scorched."""
    polys = region(g, lambda v, c, r: c >= 55 and 26 <= r < 48, smooth=2)

    def z_of(x, y, e):
        n = 0.5 + 0.5 * math.sin(x * 1.7 + y * 0.6) * math.cos(y * 1.3 - x * 0.4)
        return (1.0 + 2.6 * n) * (0.4 + 0.6 * e)
    junk = kit.heightfield("wreck", polys, z_of, p(0x04), spacing=0.5, edge=1.2)
    paint(junk, f, p, walls=-1, probe=-0.4)
    # A torn stub of the capsule's mount and a bent strut.
    stub = w.rounded_box("wreck_mount", (X(56.5), Y(36.0), 5.0), (4.0, 9.0, 6.0), p(0x05), bevel=0.8)
    kit.jag(stub, (X(58.5), Y(36.0), 5.0), (1, 0, 0), 1.8, seed=4.0)
    strut = kit.tube("wreck_strut", [(X(57), Y(33), 6.0), (X(62), Y(34), 4.5), (X(66), Y(37), 2.4)], 0.6, p(0x06))
    paint(stub, f, p, walls=-1, probe=-0.3, grid=True)
    paint(strut, f, p, walls=-1, probe=-0.3)
    return [junk, stub, strut]


# --- The mast and the turret in its bay ----------------------------------------------------------------------

def mast(g, f, p):
    polys = region(g, lambda v, c, r: 44 <= r < 63 and 28 <= c < 44, smooth=2)
    beam = kit.heightfield("mast", polys, lambda x, y, e: 6.6 * (0.3 + 0.7 * e), p(0x05), spacing=1.0, edge=1.6)
    paint(beam, f, p, walls=-2, probe=-0.4)
    pipe = kit.tube("mast_pipe", [(X(36), Y(45), 6.2), (X(36), Y(58), 6.2), (X(36), Y(61), 5.0)], 0.62, p(0x58))
    strip = w.rounded_box("mast_strip", (X(30.5), Y(51.0), 6.6), (2.2, 5.6, 1.4), p(0x58), bevel=0.4)
    box = w.rounded_box("mast_box", (X(38.5), Y(50.5), 4.6), (4.6, 4.6, 4.6), p(0x47), bevel=0.6)
    paint(pipe, f, p, walls=-2, probe=-0.4)
    paint(strip, f, p, walls=-2, probe=-0.4)
    paint(box, f, p, walls=-2, probe=-0.4, grid=True)
    return [beam, pipe, strip, box]


def turret(g, f, p, burnt=False):
    """The bay (u 79 / 77): a floor slab over the whole sprite and the turret on it."""
    floor = k.box("bay_floor", (0.0, -28.0, 0.3), (24.0, 28.0, 0.6), p(0x63))
    kit.pixelate(floor, f, step=1.0)

    def tile(c, nrm):
        v = f.at(c.x, c.y)
        if nrm.z < 0.5:
            return p(0x61)
        return p(v) if v is not None and v >> 4 == 6 else p(0x61)
    kit.paint_faces(floor, tile)
    kit.merge_flat(floor, angle=1.0)
    polys = region(g, lambda v, c, r: r >= 60 and v >> 4 != 6, smooth=3)
    cx, cy = X(36.0), Y(70.0)

    def z_of(x, y, e):
        pit = math.exp(-(((x - X(35.0)) / 5.0) ** 2 + ((y - Y(66.0)) / 5.2) ** 2))
        return (7.0 - 3.4 * pit) * (0.1 + 0.9 * e * e)
    body = kit.heightfield("turret", polys, z_of, p(0x03), spacing=0.9, edge=2.4)
    paint(body, f, p, walls=-1, probe=-0.6, side=(p(0x04), 0.62), blur=1)
    parts = [floor, body]
    # The red panel at its left, the red box where the mast comes in, the purple vent at its right.
    panel = w.rounded_box("turret_panel", (X(26.0), Y(66.5), 4.6), (3.8, 10.4, 6.4), p(0x47), bevel=0.8)
    lid = w.rounded_box("turret_lid", (X(32.5), Y(60.0), 5.6), (5.0, 5.2, 4.4), p(0x48), bevel=0.6)
    parts += [panel, lid]
    if burnt:
        kit.jag(panel, (X(26.5), Y(66.5), 7.8), (0, 0, 1), 1.4, scale=0.8, seed=5.0)
    else:
        vent = w.rounded_box("turret_vent", (X(38.0), Y(67.0), 4.2), (7.0, 7.0, 3.8), p(0x56), bevel=0.6)
        parts.append(vent)
        for i in range(3):  # its slats
            parts.append(w.rounded_box(f"turret_slat{i}", (X(36.0 + 2.0 * i), Y(67.0), 6.1), (0.8, 5.6, 0.6),
                                       p(0x5a), bevel=0.2))
    for obj in parts[2:]:
        paint(obj, f, p, walls=-2, probe=-0.4, grid=True)
    return parts


# --- The towers -----------------------------------------------------------------------------------------------

OUTLINE = {0x00, 0x01, 0x02}


def paint_frame(name):
    """A tower's pixels for painting: the dark outline next to the outside replaced by the colour inside it,
    so that the parts' sides take their own colour."""
    return kit.frame(name, 72, ORIGIN).fill(OUTLINE)


def tower_a():
    p = painter("tower")
    g, f = TOWER_A, paint_frame("TOWER_A")
    spires(f, p)
    hull_open(g, f, p)
    capsule(g, f, p, 5)
    mast(g, f, p)
    turret(g, f, p)


def tower_b():
    p = painter("tower")
    g, f = TOWER_B, paint_frame("TOWER_B")
    spires(f, p)
    hull_shut(g, f, p)
    capsule(g, f, p, 4)
    mast(g, f, p)
    turret(g, f, p)


def tower_damaged():
    """Tower A's shapes (so that each damaged piece meets its intact neighbours) painted by the damaged
    sprites, with the spires snapped and the capsule gone."""
    p = painter("tower")
    f = paint_frame("TOWER_A_DMG")
    spires(f, p, broken=True)
    hull_open(TOWER_A, f, p)
    wreckage(TOWER_D, f, p)
    mast(TOWER_A, f, p)
    turret(TOWER_A, f, p, burnt=True)


def pieces(prefix, f, cells):
    return [kit.piece(f"{prefix}{name}", f, c0, r0, wd, ht) for name, (c0, r0, wd, ht) in cells.items()]


kit.PROTECT += ["hull", "capsule", "turret", "s1", "s2", "s4", "s5", "wreck", "mast", "hatch", "ledge"]
kit.pieced("deli_tower_a", tower_a, (72, 84), pieces("deli_tower_", TOWER_A, {
    "1": (0, 0, 24, 28), "3": (24, 0, 24, 28), "5": (48, 0, 24, 28),
    "39": (0, 28, 24, 28), "41": (24, 28, 24, 28), "43": (48, 28, 24, 28), "79": (24, 56, 24, 28)}))
kit.pieced("deli_tower_b", tower_b, (72, 84), pieces("deli_tower_", TOWER_B, {
    "15": (24, 0, 24, 28), "17": (48, 0, 24, 28), "53": (24, 28, 24, 28), "55": (48, 28, 24, 28),
    "19": (12, 13, 12, 14), "38": (12, 27, 12, 14)}))
kit.pieced("deli_tower_damaged", tower_damaged, (72, 84), pieces("deli_tower_", TOWER_D, {
    "7": (0, 0, 24, 28), "9": (24, 0, 24, 28), "11": (48, 0, 24, 28), "127": (48, 28, 24, 28),
    "77": (24, 56, 24, 28)}))


if __name__ == "__main__":
    kit.run()
