"""Enemies of wave 3, batch N (sheet 3, SURFACE and DESERTRUN): the rock arch and the stepped pyramid,
each built whole and cut into its sprites' pieces (models.cfg: origin; authored as the sprites look,
yaw=0). The machines and ships are in wave3_n.py.

- rock_arch_<sprite> (3 198, 162, 200, 164, 202, 166, 204, 168, 206, 170, 208, 241, 262, 279, 281, 282):
  the tan rock arch of SURFACE and DESERTRUN. The levels put it together from 2x2 sprites (events 6,
  7, 10): its left leg and the start of its span (198, 162/200, 164/202), optionally three more
  columns of span (166/204, 168/206, 170/208), and its right leg (241, 262, 279, 281, 282), which
  joins whichever column comes last. Built whole (the long version, 204 x 56 pixels) as a sinewy
  ridge of tan rock, its shades the sprites', its cross-section where the right leg may join (after
  164/202 and after 170/208) the same, so either version meets. The right leg's sprites overlap; each
  piece keeps a part of it (262 the top, 281 the left, 282 the right of the bottom row). The 1x1 nub
  in the notch of the left leg (3 180) is desert_rock_tip (wave2_h.py).
- pyramid_<sprite> (3 153, 155, 191, 193): SURFACE's stepped pyramid on the sand, four tiers with
  battered walls, the sand round it a low slab; the levels place the four as a block (event 12) and
  put the capstone (3 3, pyramid_cap) on its top platform (event 10, 10 pixels right and 33 up from
  the bottom left piece).
- pyramid_cap (3 3, 1x1): the golden capstone on the pyramid, drawn at its own origin on the
  platform's height; its frames 4 and 5 brighten it (it glows a little).

usage: Blender -b --factory-startup -P wave3_n_rocks.py -- [--only name,name] [--preview <prefix>]
       [--check 1] [--stats 1] [--whole <prefix>]
"""
import math
import os
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_n_kit as n  # noqa: E402
from wave3_n_kit import art, k, sh, w, pal  # noqa: E402


# --- The rock arch -------------------------------------------------------------------------------

ARCH_ORIGIN = (0, 28)  # the whole's x runs along the columns, y = 0 between the two rows of sprites
JOINTS = (72.0, 144.0)  # where the right leg may join (the right ends of 164/202 and of 170/208)
BASE = -5.0  # the underside: the arch hangs a little below its layer


def arch_grid():
    return n.joined((w.grid(art.ROCK_A, 144), 144), (w.grid(art.ROCK_B, 60), 60))


def arch_whole():
    """A ridge of tan rock through the arch's pixels: a rounded cross-section higher where the
    sprites are lighter (the top of the ridge, along the north side of the span), the sprites' light
    lobes standing out a little and their dark creases sunk in; painted in the sprites' shades. Near
    the joints its cross-section is a fixed one, so that the right leg meets either version."""
    g = arch_grid()
    ox, oy = ARCH_ORIGIN
    tan = lambda v: v is not None and v >> 4 == 1  # noqa: E731
    sharp = w.sampler(g, ARCH_ORIGIN, value=lambda v: v & 15, blur=0, keep=tan)
    fine = w.sampler(g, ARCH_ORIGIN, value=lambda v: v & 15, blur=1, keep=tan)
    coarse = w.sampler(g, ARCH_ORIGIN, value=lambda v: v & 15, blur=4, keep=tan)
    # The joints' cross-section: the mean of the sprites' columns there (they are nearly the same).
    joint_cols = [71, 72, 143, 144]

    def joint_shade(y, column):
        r = int(math.floor(oy - y))
        vals = []
        for c in joint_cols:
            for rr in (r - 1, r, r + 1):
                if 0 <= rr < len(g) and g[rr][c] is not None and tan(g[rr][c]):
                    vals.append(g[rr][c] & 15)
        return sum(vals) / len(vals) if vals else 4.0

    top_row, bottom_row = 2.0, 41.0  # the joints' edges (rows)

    def lift(d, wd):
        """The rounded cross-section: up to 11 pixels over the underside, edges rounded over 6."""
        h = min(0.7 * wd, 13.5)
        t = min(1.0, max(0.0, d / min(max(wd, 0.5), 6.0)))
        return h * math.sqrt(max(0.0, 1.0 - (1.0 - t) ** 2))

    def shaped(base_lift, s1, s4):
        detail = s1 - s4  # light lobes stand out, dark creases (s1 the unblurred shade there) sink in
        return BASE + 0.4 + base_lift * (0.48 + 0.05 * s4) + (0.3 * detail if detail > 0 else 0.45 * detail)

    def z_fn(x, y, z):
        s0, s4 = sharp(x, y), coarse(x, y)
        s1 = fine(x, y)
        s1 = s0 if s0 < s1 - 1.0 else s1
        z_nat = shaped(z - BASE - 0.4, s1, s4)
        for xj in JOINTS:
            wj = n.smoothstep(9.0, 2.0, abs(x - xj))
            if wj > 0:
                row = oy - y
                d = max(0.0, min(row - top_row, bottom_row - row))
                sj = joint_shade(y, xj)
                z_nat = z_nat * (1 - wj) + shaped(lift(d, (bottom_row - top_row) / 2), sj, sj) * wj
        return z_nat

    def profile(d, wd):
        import numpy as np
        return np.array([lift(a, b) for a, b in zip(d, wd)])

    rows = w.regions(g, lambda v, c, r: "#")
    polys = sh.outlines(rows, "#", ARCH_ORIGIN, smooth=2, epsilon=0.35, min_area=2.0)
    stone = pal("arch_tan6", 0x16, metallic=0.0, roughness=0.8)
    rock = sh.inflate("arch", polys, stone, profile, bottom=0.0, base=BASE, rim=0.4, spacing=0.6, z_fn=z_fn,
                      sigma=1.5)
    w.simplify_bottom(rock)
    bands = [(s - 0.5 if s > 1 else 0, pal(f"arch_tan{s:x}", 0x10 + s, metallic=0.0, roughness=0.8)) for s in range(1, 14)]

    def paint(x, y):
        s0, s1 = sharp(x, y), fine(x, y)
        return 0.5 * (s0 + s1) if s0 < s1 - 1.6 else s1
    n.paint_shades(rock, paint, bands, wall_drop=2.5)
    k.smooth(rock, 38)


def arch_piece(sprite, col, row, keep=None):
    """A piece of the arch: the sprite whose top left pixel is at (col, row) of the whole; keep (c0,
    c1, r0, r1) narrows the part it keeps (overlapping sprites)."""
    ox, oy = ARCH_ORIGIN
    c0, c1, r0, r1 = keep or (col, col + 24, row, row + 28)
    box = (c0 - ox, c1 - ox, oy - r1, oy - r0)
    centre = (col + 12 - ox, oy - row - 14)

    def mask():
        g = arch_grid()
        part = [[g[r][c] is not None and c0 <= c < c1 and r0 <= r < r1 if 0 <= c < len(g[0]) else False
                 for c in range(col, col + 24)] for r in range(row, row + 28)]
        return part
    return (f"rock_arch_{sprite}", box, centre, mask)


n.pieced("arch", arch_whole, (204, 56), [
    arch_piece(198, 0, 28),
    arch_piece(162, 24, 0), arch_piece(200, 24, 28),
    arch_piece(164, 48, 0), arch_piece(202, 48, 28),
    arch_piece(166, 72, 0), arch_piece(204, 72, 28),
    arch_piece(168, 96, 0), arch_piece(206, 96, 28),
    arch_piece(170, 120, 0), arch_piece(208, 120, 28),
    arch_piece(241, 144, 0), arch_piece(279, 144, 28),
    arch_piece(262, 168, 14, keep=(168, 192, 14, 28)),
    arch_piece(281, 168, 28, keep=(168, 180, 28, 56)),
    arch_piece(282, 180, 28, keep=(180, 204, 28, 56)),
])


# --- The stepped pyramid -------------------------------------------------------------------------

PYRAMID_ORIGIN = (24, 28)
CAP_CENTRE = (-2.0, 19.0)  # the capstone's sprite centre in the whole (event 10: 10 right, 33 up of 191's)
CAP_BASE = 17.0  # the top platform's height, where the capstone stands
# The tiers: (west, east, south, north) of the outer edge at their foot, the insets of their top face
# (west, east, south, north) and the top's height. The south walls lean most (the sprite's risers).
TIERS = [((-22.0, 17.0, -15.0, 17.0), (1.6, 1.6, 6.0, 1.0), 5.0),
         ((-19.0, 14.0, -5.0, 19.0), (1.6, 1.6, 2.2, 1.0), 9.0),
         ((-16.0, 11.0, 1.0, 21.0), (1.6, 1.6, 2.2, 1.0), 13.0),
         ((-12.0, 8.0, 7.0, 23.5), (1.6, 1.6, 2.2, 1.0), CAP_BASE)]


def frustum(name, outer, inset, z_prev, z_top, mats, bevel=0.35):
    """A tier: straight walls round the outer rectangle up to z_prev (inside the tier below, or its
    back wall), then leaning walls up to the top face. mats: (top, south, west, east, north)."""
    import bmesh
    x0, x1, y0, y1 = outer
    iw, ie, i_s, i_n = inset
    rings = [((x0, x1, y0, y1), 0.0), ((x0, x1, y0, y1), z_prev),
             ((x0 + iw, x1 - ie, y0 + i_s, y1 - i_n), z_top)]
    bm = bmesh.new()
    loops = []
    for (a0, a1, b0, b1), z in rings:
        loops.append([bm.verts.new(p) for p in ((a0, b0, z), (a1, b0, z), (a1, b1, z), (a0, b1, z))])
    for lo, hi in zip(loops, loops[1:]):
        for i in range(4):
            j = (i + 1) % 4
            bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
    bm.faces.new(loops[-1])
    bm.faces.new(list(reversed(loops[0])))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    for m in mats:
        obj.data.materials.append(m)
    k.bevel(obj, bevel, 2)
    sh.apply_modifiers(obj)
    top, south, west, east, north = range(5)
    for poly in obj.data.polygons:
        nz, nx, ny = poly.normal.z, poly.normal.x, poly.normal.y
        if nz > 0.85:
            poly.material_index = top
        elif abs(ny) >= abs(nx):
            poly.material_index = south if ny < 0 else north
        else:
            poly.material_index = west if nx < 0 else east
    return k.smooth(obj, 35)


def pyramid_whole():
    """SURFACE's stepped pyramid: four tiers of tan stone, their leaning walls dark on the south, light
    on the west and mid on the east as the sprite draws them, and a platform on top where the capstone
    stands (a model of its own, pyramid_cap); round it the sand of the sprites as a low slab."""
    g = w.grid(art.TEMPLE, 48)
    sand = [(0, pal("pyramid_sand4", 0xa4, metallic=0.0, roughness=0.9)),
            (5.5, pal("pyramid_sand6", 0xa6, metallic=0.0, roughness=0.9)),
            (7.5, pal("pyramid_sand8", 0xa8, metallic=0.0, roughness=0.9)),
            (9.0, pal("pyramid_sand9", 0xa9, metallic=0.0, roughness=0.9))]
    n.soft_floor("sand", g, sand, lambda v, c, r: v >> 4 == 0xa, origin=PYRAMID_ORIGIN, top=0.8, relief=0.8)
    top = pal("pyramid_top", 0x15, metallic=0.0, roughness=0.75)
    south = pal("pyramid_south", 0x12, metallic=0.0, roughness=0.8)
    west = pal("pyramid_west", 0x1a, metallic=0.0, roughness=0.7)
    east = pal("pyramid_east", 0x16, metallic=0.0, roughness=0.75)
    north = pal("pyramid_north", 0x13, metallic=0.0, roughness=0.8)
    z_prev = 0.0
    for i, (outer, inset, z_top) in enumerate(TIERS):
        frustum(f"tier{i}", outer, inset, z_prev, z_top, (top, south, west, east, north))
        z_prev = z_top - 0.3
    # Courses: a thin dark groove along the foot of each tier's south wall, as the sprite's lines.
    groove = pal("pyramid_groove", 0x11, metallic=0.0, roughness=0.85)
    for i, (outer, inset, z_top) in enumerate(TIERS[1:]):
        x0, x1, y0, _ = outer
        z = TIERS[i][2]
        w.tube(f"course{i}", [(x0 + 0.8, y0 - 0.25, z + 0.05), (x1 - 0.8, y0 - 0.25, z + 0.05)], 0.3, groove, 6)
    if "whole" in k.args():  # the previews show the capstone in its place
        before = set(w.meshes())
        pyramid_cap()
        sh.move([o for o in w.meshes() if o not in before], *CAP_CENTRE)


def pyramid_piece(sprite, col, row):
    ox, oy = PYRAMID_ORIGIN
    box = (col - ox, col + 24 - ox, oy - row - 28, oy - row)
    centre = (col + 12 - ox, oy - row - 14)

    def mask():
        return n.art_mask(w.grid(art.TEMPLE, 48), (col, col + 24, row, row + 28))
    return (f"pyramid_{sprite}", box, centre, mask)


n.pieced("pyramid", pyramid_whole, (48, 56), [pyramid_piece(153, 0, 0), pyramid_piece(155, 24, 0),
                                             pyramid_piece(191, 0, 28), pyramid_piece(193, 24, 28)])


@n.model("pyramid_cap", mask=lambda: n.art_mask(w.grid(art.STUD3, 12)), size=(12, 14))
def pyramid_cap():
    """The capstone on the pyramid's top platform (drawn at its own origin, standing at the
    platform's height): a pyramid of golden stone, its apex a little towards the north as the sprite
    draws it, on a thin plinth; it glows a little (its frames brighten it)."""
    import bmesh
    south = pal("cap_south", 0x16, metallic=0.35, roughness=0.4, glow=0.25)
    west = pal("cap_west", 0x1b, metallic=0.35, roughness=0.35, glow=0.25)
    east = pal("cap_east", 0x18, metallic=0.35, roughness=0.4, glow=0.25)
    north = pal("cap_north", 0x14, metallic=0.35, roughness=0.45, glow=0.2)
    plinth = pal("cap_plinth", 0x13, metallic=0.2, roughness=0.6)
    x0, x1, y0, y1 = -5.6, 5.4, -6.8, 4.4
    z0 = CAP_BASE
    w.rounded_box("plinth", ((x0 + x1) / 2, (y0 + y1) / 2, z0 + 0.4), (x1 - x0 + 0.6, y1 - y0 + 0.6, 1.2), plinth,
                  bevel=0.3)
    apex = Vector((-0.1, 1.2, z0 + 8.2))
    bm = bmesh.new()
    base = [bm.verts.new(p) for p in ((x0, y0, z0 + 0.9), (x1, y0, z0 + 0.9), (x1, y1, z0 + 0.9), (x0, y1, z0 + 0.9))]
    top = bm.verts.new(apex)
    for i in range(4):
        bm.faces.new((base[i], base[(i + 1) % 4], top))
    bm.faces.new(list(reversed(base)))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    mesh = bpy.data.meshes.new("cap")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("cap", mesh)
    bpy.context.scene.collection.objects.link(obj)
    for m in (south, west, east, north):
        obj.data.materials.append(m)
    k.bevel(obj, 0.3, 2)
    sh.apply_modifiers(obj)
    for poly in obj.data.polygons:
        nx, ny = poly.normal.x, poly.normal.y
        poly.material_index = (0 if ny < 0 else 3) if abs(ny) >= abs(nx) else (1 if nx < 0 else 2)
    k.smooth(obj, 30)



n.run()
