"""Enemies of wave 3, batch S (sheet F): SAVARA's boss, modelled as its sprites look (models.cfg: yaw=0).
The other models of the batch are in wave3_s.py; the kit is wave3_s_kit.py, the pixels wave3_s_art.py.

- savara_boss_153 ... savara_boss_274: the red war machine at the end of SAVARA, SAVARA IV, SAVARA Y
  and TORM (on the ground) and of SAVARA V (in the sky), 144 x 112 pixels, which one level event puts
  together from twenty 2x2 sprites (enemies 480-499): 153 155 157 159 161 163 / 191 193 195 197 199
  201 / 12 pixels to the right 230 232 234 236 238 / 36 pixels to the right 270 272 274. A broad red
  hull, ribbed and panelled as the sprite draws it, rounded over its sides; six heat fins in black
  frames rising from its back, glowing red and orange; a domed prow between them; under the dome a
  pit with two steel rods running down across a black band, where four windows hold red eyes half
  uncovered by their shutters (232 and 236 animate them opening: 165, 203, 241, 279 and 167, 205,
  243, 281) between two grey bumpers; below, two pods with glowing pink rods either side of a block
  with a dark gate. Built whole and cut into its twenty pieces (origin). The outer fins' pieces
  (153, 163) replace savara_fin_left and savara_fin_right of wave 1 (wave1_c.py), which were built on
  their own and do not meet the rest.

usage: Blender -b --factory-startup -P wave3_s_boss.py -- [--only name,name] [--preview <prefix>]
       [--check 1] [--whole <prefix>]
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_s_kit as s  # noqa: E402
from wave3_s_kit import art, k, sh, w, n, pal  # noqa: E402

BOSS = s.Frame(art.BOSS, 144, (72, 56))
# For painting and relief: the outline pixels at the edge take the colour inside them.
PAINT = s.Frame(art.BOSS, 144, (72, 56)).fill({0x01})
AXIS = 0.5  # the boss is symmetric about x = 0.5 (pixel column 72's centre): column c mirrors 144 - c

# Fins: (first panel column, first panel row, last panel column, last panel row, top height).
FINS = [(15, 12, 21, 40, 11.0), (27, 6, 33, 34, 12.2), (39, 1, 45, 29, 13.4),
        (99, 1, 105, 29, 13.4), (111, 6, 117, 34, 12.2), (123, 13, 129, 41, 11.0)]
WINDOWS = [(37, 47), (49, 59), (85, 95), (97, 107)]  # columns of the eye windows' frames, rows 58-68
PIECES = [(153, 0, 0), (155, 24, 0), (157, 48, 0), (159, 72, 0), (161, 96, 0), (163, 120, 0),
          (191, 0, 28), (193, 24, 28), (195, 48, 28), (197, 72, 28), (199, 96, 28), (201, 120, 28),
          (230, 12, 56), (232, 36, 56), (234, 60, 56), (236, 84, 56), (238, 108, 56),
          (270, 36, 84), (272, 60, 84), (274, 84, 84)]


def boss_painter():
    return s.Painter("boss", shades={4: (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14), 0: (1, 2, 3, 5, 7, 9, 12, 14)},
                     metallic=0.5, roughness=0.38, finish={4: (0.3, 0.45), 0: (0.6, 0.35)})


def fin_painter():
    glow = {0x70 + i: 0.3 + 0.14 * i for i in range(13)}
    return s.Painter("boss_fin", shades={7: tuple(range(13))}, metallic=0.05, roughness=0.35, glow=glow)


def symmetric(fn):
    """A field averaged with its mirror image (the sprite's light from the left taken out)."""
    return lambda x, y: 0.5 * (fn(x, y) + fn(2 * AXIS - x, y))


def hull_mask_rows():
    """The hull's pixels: everything but the fins where they stand out beyond the hull's back."""
    g = BOSS.g
    cut = {}
    for pc0, pr0, pc1, pr1, _ in FINS:
        # The hull's back edge next to the fin: the first row the columns beside it have pixels in.
        def first_row(col):
            for r in range(len(g)):
                if g[r][col] is not None and g[r][col] >> 4 != 7 and not (pc0 - 1 <= col <= pc1 + 1):
                    return r
            return len(g)
        edge = min(first_row(pc0 - 3), first_row(pc1 + 3)) + 1
        for c in range(pc0 - 1, pc1 + 2):
            cut[c] = edge
    return s.regions(g, lambda v, c, r: "." if c in cut and r < cut[c] else "#")


def boss_whole():
    f = BOSS
    X, Y = f.X, f.Y
    p = boss_painter()
    fp = fin_painter()
    black = p(0x01)
    dark = p(0x02)
    grey = p(0x07)
    steel = pal("boss_steel", 0x0b, metallic=0.75, roughness=0.22)
    steel_dark = pal("boss_steel_dark", 0x06, metallic=0.7, roughness=0.3)
    red = p(0x46)
    pink = pal("boss_pink", 0x4d, metallic=0.2, roughness=0.15, glow=0.9)
    eye = pal("boss_eye", 0x76, metallic=0.0, roughness=0.15, glow=1.4)
    eye_core = pal("boss_eye_core", 0x7a, metallic=0.0, roughness=0.1, glow=2.2)

    # --- The hull: one relief over the whole outline, from the sprite's shades. ----------------------
    red_fine = symmetric(PAINT.shade(4, 1))
    red_coarse = symmetric(PAINT.shade(4, 4))
    any_px = lambda v: v is not None  # noqa: E731
    darkness = w.sampler(PAINT.g, (f.ox, f.oy), value=lambda v: 1.0 if v >> 4 == 0 and (v & 15) <= 2 else
                         (0.55 if v >> 4 == 0 else 0.0), blur=1, keep=any_px)
    redness = w.sampler(PAINT.g, (f.ox, f.oy), value=lambda v: 1.0 if v >> 4 == 4 else 0.0, blur=1, keep=any_px)

    def soft_box(x, y, x0, x1, y0, y1, edge=1.5):
        return (s.smoothstep(x0 - edge, x0 + edge, x) * (1 - s.smoothstep(x1 - edge, x1 + edge, x)) *
                s.smoothstep(y0 - edge, y0 + edge, y) * (1 - s.smoothstep(y1 - edge, y1 + edge, y)))

    def regions_height(x, y):
        h = 7.0 + 1.2 * max(0.0, 1.0 - ((x - AXIS) / 64.0) ** 2)
        for c in (55, 89):  # the pods, higher
            h += 2.6 * soft_box(x, y, X(c) - 6.0, X(c) + 6.0, f.bottom(110), f.top(72))
        h += 1.2 * soft_box(x, y, X(62), X(82), f.bottom(103), f.top(70))  # the gate's block
        return h

    def hull_z(x, y, z):
        edge = z  # 0 at the outline, 1 inside (the profile's rounding)
        carve = 3.9 * s.smoothstep(0.35, 0.9, darkness(x, y))
        relief = 0.09 * (red_fine(x, y) - red_coarse(x, y)) * redness(x, y)
        top = regions_height(x, y) + relief - carve
        return 0.7 + edge * max(0.6, top - 0.7)
    rows = hull_mask_rows()
    polys = sh.outlines(rows, "#", (f.ox, f.oy), smooth=2, epsilon=0.35, min_area=4.0)
    hull = sh.inflate("hull", polys, red, sh.pillow_profile(1.0, 4.0), bottom=0.0, base=0.0, rim=0.0, spacing=0.5,
                      z_fn=hull_z, sigma=1.5)
    w.simplify_bottom(hull)
    k.smooth(hull, 45)

    def top(x, y, default=7.0):
        return sh.surface_z(hull, x, y, default)

    # --- The dome over the prow. ----------------------------------------------------------------------
    dome_px = [(60, 42), (60, 9), (61.5, 7.5), (63, 6.2), (66, 5), (79, 5), (82, 6.2), (83.5, 7.5), (85, 9), (85, 42)]
    dome_poly = [(c - f.ox, f.oy - r) for c, r in dome_px][::-1]
    dome_fine = symmetric(PAINT.shade(4, 1))

    def dome_z(x, y, z):
        seam = 0.9 * math.exp(-((x - AXIS) / 0.55) ** 2)
        return z - seam + 0.18 * (dome_fine(x, y) - red_coarse(x, y))
    dome = sh.inflate("dome", [dome_poly], red, sh.pillow_profile(5.0, 4.5, crown=2.2), bottom=0.0, base=6.0,
                      rim=0.3, spacing=0.5, z_fn=dome_z, sigma=1.5)
    k.smooth(dome, 45)

    # --- The fins: black frames, glowing panels. --------------------------------------------------------
    fin_parts = []
    for i, (pc0, pr0, pc1, pr1, ztop) in enumerate(FINS):
        c0, c1, r0, r1 = pc0 - 1, pc1 + 1, max(1, pr0 - 1), pr1 + 1
        outer = f.rect(c0, c1, r0, r1)
        inner = f.rect(pc0, pc1, pr0, pr1, inset=0.15)
        body = s.slab(f"fin{i}", outer, 1.5, ztop - 0.6, dark, bevel=0.5, segments=2)
        rim = sh.inflate(f"fin_rim{i}", [outer, inner[::-1]], p(0x03), sh.pillow_profile(0.75, 0.35), bottom=0.0,
                         base=ztop - 0.75, rim=0.05, spacing=0.4)
        k.smooth(rim, 40)
        panel = s.slab(f"fin_panel{i}", inner, ztop - 1.2, ztop - 0.45, fp(0x74), bevel=0.12, segments=1)
        s.pixelate(panel, f)
        s.paint_sprite(panel, f, fp, wall_steps=0, under=dark, keep=lambda v: v >> 4 == 7)
        s.merge_flat(panel)
        fin_parts += [body, rim, panel]

    # --- The pit under the dome: two steel rods running down over the black band. ----------------------
    rod_parts = []
    for c0, c1 in ((68, 71), (73, 76)):
        x = (f.left(c0) + f.right(c1)) / 2
        y0, y1 = f.top(42) + 0.6, f.bottom(70) - 0.4
        prof = [(0.0, 1.2), (0.4, 1.75), (6.0, 1.85), (6.4, 2.15), (8.0, 2.15), (8.4, 1.8), (13.0, 1.8),
                (13.4, 2.1), (14.6, 2.1), (15.0, 1.75), (y0 - y1 - 0.4, 1.75), (y0 - y1, 1.2)]
        rod = w.lathe_axis(f"rod{c0}", prof, steel, (x, y0, 4.6), (0, -1, 0), 20, squash=0.85)
        w.paint_faces(rod, lambda c, nrm: steel_dark if nrm.z < 0.1 else None)
        rod_parts.append(rod)
    # The grey plates beside the rods in the pit.
    for c0, c1 in ((62, 66), (78, 82)):
        rod_parts.append(s.slab(f"pit_plate{c0}", f.rect(c0, c1, 44, 52, inset=0.2), 0.0, 4.4, steel_dark, bevel=0.4))

    # --- The black band: windows with eyes, bumpers at its ends. ----------------------------------------
    band_parts = []
    for c0, c1 in WINDOWS:
        outer = f.rect(c0, c1, 58, 68)
        inner = f.rect(c0 + 1, c1 - 1, 59, 67)
        frame = sh.inflate(f"window{c0}", [outer, inner[::-1]], grey, sh.pillow_profile(2.2, 0.6), bottom=0.0,
                           base=3.4, rim=0.1, spacing=0.4)
        k.smooth(frame, 40)
        well = s.slab(f"well{c0}", inner, 2.4, 3.8, black, bevel=0.1, segments=1)
        cx = (f.left(c0) + f.right(c1)) / 2
        # The shutter drawn up under the frame's top, the eye glowing below it.
        shutter = s.slab(f"shutter{c0}", f.rect(c0 + 1, c1 - 1, 59, 61, inset=0.1), 0.0, 0.6, steel, bevel=0.2,
                         z_fn=lambda x, y, z: z + 4.4 + 0.5 * (y - Y(61)))
        eyeball = w.sphere(f"eye{c0}", (cx, Y(64.0), 3.7), (3.6, 2.3, 1.5), eye, 20, 10)
        core = w.sphere(f"eye_core{c0}", (cx - 0.3, Y(63.8), 4.75), (1.5, 1.0, 0.5), eye_core, 12, 6)
        band_parts += [frame, well, shutter, eyeball, core]
    for x in (X(33.2), X(110.8)):
        bumper = w.sphere(f"bumper{x:.0f}", (x, Y(62.5), 4.6), (4.2, 6.0, 4.3), steel, 28, 14)
        w.paint_faces(bumper, lambda c, nrm: steel_dark if nrm.z < 0.0 else None)
        band_parts.append(bumper)

    # --- The pods' glowing pink rods. ----------------------------------------------------------------------
    pink_parts = []
    for c in (55, 89):
        x = X(c)
        path = [(x, y, top(x, y) - 0.25) for y in (Y(79.5), Y(85.0), Y(91.0), Y(97.0), Y(101.5))]
        pink_parts.append(w.tube(f"pink{c}", path, 1.0, pink, 12, squash=0.8))

    # --- Paint: the sprite's colours on the hull and the dome. --------------------------------------------
    red_paint = symmetric(PAINT.shade(4, 1))
    grey_paint = PAINT.shade(0, 1)

    def paint(c, nrm):
        if nrm.z < -0.5:
            return black
        index = PAINT.at(c.x, c.y)
        wall = abs(nrm.z) < 0.45
        if index is None:
            return p(0x43) if wall else None
        ramp = index >> 4
        if ramp == 0 and darkness(c.x, c.y) < 0.45:
            ramp = 4  # lone dark pixels in the red: dark red, not black specks
        if ramp == 4:
            shade = red_paint(c.x, c.y) - (2.0 if wall else 0.0)
            return p(0x40 + max(1, min(15, int(round(shade)))))
        if ramp == 0:
            shade = grey_paint(c.x, c.y) - (1.0 if wall else 0.0)
            return p(max(1, min(15, int(round(shade)))))
        return dark
    w.paint_faces(hull, paint)
    w.paint_faces(dome, paint)
    for obj in (hull, dome):
        s.merge_flat(obj, 1.5)
    n.merge_by_material()


def boss_piece(sprite, px, py):
    x0, y1 = px - 72.0, 56.0 - py
    return (f"savara_boss_{sprite}", (x0, x0 + 24.0, y1 - 28.0, y1), (x0 + 12.0, y1 - 14.0),
            lambda: BOSS.mask((px, px + 24, py, py + 28)))


s.pieced("savara_boss", boss_whole, (144, 112), [boss_piece(*pc) for pc in PIECES])


s.run()
