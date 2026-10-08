"""Batch AH of wave 3 (sheet M): the armoured dome of ASTEROID1, AST. CITY, AST ROCK and TYRIAN X and its burnt-out
wreck, modelled as the sprites look (models.cfg: yaw=0). The kit is wave3_ah_kit.py, the pixels wave3_ah_art.py.

The levels put the dome together from six ground enemies (536-541, or 1082-1087 in episode 5): 45, 47, 49 at
(x, y - 28), (x + 24, y - 28), (x + 48, y - 28) above 83, 85, 87 at (x, y), (x + 24, y), (x + 48, y): 72 x 56
pixels on its square of stone floor. Each piece is an enemy of its own, and each leaves its wreck in its place
when destroyed (dgr 39, 41, 43, 77, 79, 81; dlevel -1), so the wreck is cut exactly as the dome.

- armour_dome_tl, _tm, _tr, _bl, _bm, _br (M 45, 47, 49, 83, 85, 87): a low grey shell on the stone floor tiles;
  on its top a raised red housing, two pillars joined in a U round a recess in which a red capsule lies on a grey
  mount, pointing up the screen; light ridges curving from the housing down to the rim on both sides, two small
  dark ports above them and two large bronze lenses in grey bezels below; red armour on the lower flanks; at the
  front, grey plates over and under a recessed band with the gun port in its middle (85's frames 7, 9, 11 open it
  and fire: the model shows the slot with its ember glowing) and a vent grille on the right.
- armour_dome_wreck_tl ... _br (M 39, 41, 43, 77, 79, 81): the same shell burnt black and dented, the housing
  scorched to bronze, the capsule broken off, the red armour charred, the lenses dark.

usage: Blender -b --factory-startup -P wave3_ah_dome.py -- [--only name,name] [--preview <prefix>] [--check 1]
       [--stats 1] [--whole <prefix>]
"""
import math
import os
import sys

from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_ah_kit as kit  # noqa: E402
from wave3_ah_kit import k, sh, w, pal  # noqa: E402

DOME = kit.frame("DOME", 72, (36, 28))
WRECK = kit.frame("WRECK", 72, (36, 28))

CX, CY, RX, RY = 0.5, 1.0, 30.7, 25.3   # the shell's outline (cols 6-66, rows 2-51)
FLOOR = 0.6                              # the floor tiles' top
RIM = 1.0                                # the shell's foot above the tiles
HEIGHT = 15.5                            # the shell's top above its foot


def rr(x, y):
    return math.sqrt(((x - CX) / RX) ** 2 + ((y - CY) / RY) ** 2)


def shell_z(x, y):
    r = min(1.0, rr(x, y))
    return FLOOR + RIM + HEIGHT * max(0.0, 1.0 - r ** 2.4) ** 0.6


def inside(x, y, margin=0.0):
    return rr(x, y) < 1.0 - margin / min(RX, RY)


# --- Regions of the art ----------------------------------------------------------------------------------------

def housing_polys():
    """The red housing (rows 3-28, cols 24-49): two pillars up to the rim, widening inwards over rows 16-21,
    joined below by the U's bottom (rows 22-28, cols 30-43); the capsule lies between the pillars."""
    poly = [(-12.0, 26.0), (-12.0, 7.0), (-6.0, 7.0), (-6.0, -1.0), (8.0, -1.0), (8.0, 7.0), (14.0, 7.0), (14.0, 26.0),
            (8.2, 26.0), (8.2, 12.6), (4.4, 7.4), (-2.8, 7.4), (-6.6, 12.6), (-6.6, 26.0)]
    return [clip_ellipse(poly, 0.3)]


def flank_polys(f):
    """The red armour of the lower flanks (rows 29-49), with the short bars beside the gun band, kept 0.4 inside
    the shell's outline (so that it ends on the shell, not over its foot)."""
    polys = kit.polys_of(f, lambda v, c, r: v >> 4 == 4 and r >= 29, smooth=2, epsilon=0.35, min_area=2.0)
    return [clip_ellipse(p, 1.2) for p in polys]


def clip_ellipse(poly, margin):
    """The polygon's points outside the shell's outline (less `margin`) moved in onto it."""
    limit = 1.0 - margin / min(RX, RY)
    out = []
    for x, y in poly:
        r = rr(x, y)
        if r > limit:
            x, y = CX + (x - CX) * limit / r, CY + (y - CY) * limit / r
        out.append((x, y))
    return out


PLATE_X = (-11.6, 12.6)          # the front plates between the flanks' bars (cols 24-48)
BAND = (-16.6, -5.6)             # the recessed gun band (rows 34-44)


def plate_polys():
    """The grey front plates above and below the gun band, clipped to the shell."""
    x0, x1 = PLATE_X
    upper = [(x0, BAND[1]), (x1, BAND[1]), (x1, -0.6), (x0, -0.6)]
    bottom = []
    for i in range(25):  # the shell's outline under the band, left to right
        x = x0 + (x1 - x0) * i / 24
        t = max(0.0, 1.0 - ((x - CX) / RX) ** 2)
        bottom.append((x, CY - RY * math.sqrt(t) + 0.35))
    lower = [(x0, BAND[0])] + bottom + [(x1, BAND[0])]
    return [upper], [lower]


# --- The whole dome -------------------------------------------------------------------------------------------

def dome_whole(wreck=False):
    f = WRECK if wreck else DOME
    tag = "dw" if wreck else "dm"
    if not wreck:
        # Clean metal in one shade (the light shades it), darker only along the sprite's dark seams and edges.
        grey_value = DOME.shade(6, 2)

        def paint(obj, shift=0.0, wall=0.0):
            kit.band_paint(obj, tag + "_grey", 6,
                           lambda x, y: (7 if grey_value(x, y) < 5.2 and rr(x, y) < 0.9 else 9) + shift, (6, 7, 8, 9),
                           wall=wall, metallic=0.55, roughness=0.3)

        def red_paint(obj, shift=0.0, wall=0.0):
            kit.band_paint(obj, tag + "_red", 4, lambda x, y: 7.6 + shift, (5, 6, 7, 8, 9), wall=wall,
                           metallic=0.35, roughness=0.35)

        flank_paint = red_paint
    else:
        # Burnt: the wreck's blacks, greys and scorched browns wherever they lie (its rim grey).
        finish = {6: (0.3, 0.6), 4: (0.2, 0.6), 7: (0.2, 0.5), 10: (0.35, 0.5), 0: (0.1, 0.85), 1: (0.2, 0.7)}
        shades = {6: (1, 2, 3, 4, 6, 8), 4: (3, 5, 7), 7: (6, 9), 10: (3, 5, 7, 9), 0: (1, 2, 3), 1: (2, 4, 6),
                  15: (1, 3)}
        paint = kit.RampPainter(tag, f, ramps=None, fallback=6, shades=shades, blur=2, wall=1.0, finish=finish,
                                where=lambda x, y: rr(x, y) < 0.95)
        red_paint = kit.RampPainter(tag, f, ramps={10, 1, 0}, fallback=10, shades=shades, blur=2, wall=1.5,
                                    finish=finish, where=lambda x, y: rr(x, y) < 0.95)
        paint = kit.RampPainter(tag, f, ramps=None, fallback=6, shades=shades, blur=2, wall=0.0, finish=finish,
                                where=lambda x, y: rr(x, y) < 0.95, shift=-0.6)
        flank_paint = paint

    # The dents of the wreck: where its pixels are charred black, the shell is pushed in.
    dent = None
    if wreck:
        burnt = kit.field(f, lambda v: 1.0 if (v >> 4 in (0, 1) or (v >> 4 == 6 and (v & 15) <= 2)) else 0.0,
                          lambda v: True, blur=2)
        dent = kit.field_sampler(f, burnt)

    def surface(x, y):
        zz = shell_z(x, y)
        if dent is not None and inside(x, y, 1.5):
            zz -= 2.4 * max(0.0, dent(x, y) - 0.2) * min(1.0, (1.0 - rr(x, y)) * 6.0)
        return zz

    # The floor tiles round it (ramp 0): stones standing a little above their mortar.
    bands = [(0, pal(f"{tag}_floor1", 0x01, metallic=0.05, roughness=0.85)),
             (2.5, pal(f"{tag}_floor3", 0x03, metallic=0.05, roughness=0.85)),
             (4.5, pal(f"{tag}_floor5", 0x05, metallic=0.05, roughness=0.8)),
             (6.5, pal(f"{tag}_floor7", 0x07, metallic=0.05, roughness=0.8)),
             (8.5, pal(f"{tag}_floor9", 0x09, metallic=0.05, roughness=0.75))]
    is_floor = lambda v, c, r: v >> 4 == 0 and not inside(f.X(c), f.Y(r), -0.5)
    w.floor("tiles", f.g, bands, is_floor, origin=(36, 28), top=FLOOR, relief=0.5, edge=0.4)

    # The shell.
    shell = kit.heightfield("shell", [kit.ellipse(CX, CY, RX, RY, 120)], lambda x, y: surface(x, y), None,
                            spacing=1.4, smooth_angle=50)
    paint(shell)

    # The red housing: two pillars and the U joining them, 3 above the shell, its edges rounded.
    housing = kit.heightfield("housing", housing_polys(), lambda x, y, e: shell_z(x, y) + 0.4 + 2.8 * e, None,
                              spacing=0.8, smooth_angle=45, edge=0.8)
    red_paint(housing, shift=0.6, wall=1.6)

    # The capsule in the U, pointing up the screen, on its grey mount.
    cap_z = shell_z(0.0, 18.0) + 3.0
    red = pal(f"{tag}_capsule", 0x76 if not wreck else 0xa5, metallic=0.3, roughness=0.25,
              glow=0.35 if not wreck else None)
    red_lit = pal(f"{tag}_capsule_lit", 0x7a, metallic=0.2, roughness=0.2, glow=0.8)
    if not wreck:
        capsule = w.lathe_axis("capsule", [(0.0, 0.25), (0.35, 1.7), (1.0, 2.8), (2.1, 3.5), (3.6, 3.8), (10.6, 3.8),
                                           (11.4, 3.5), (12.0, 2.6)], red, (0.0, 24.6, cap_z), (0, -1, 0), 28,
                               squash=0.95)
        kit.paint_faces(capsule, lambda c, nrm: red_lit if (-0.75 < nrm.x < -0.4 and nrm.z > 0.45 and c.y > 13.5) else None)
    else:
        # Broken off: a stub with a jagged rim.
        stub = w.lathe_axis("capsule", [(8.0, 3.2), (8.4, 3.7), (10.6, 3.8), (11.4, 3.5), (12.0, 2.6)], red,
                            (0.0, 24.6, cap_z), (0, -1, 0), 20, squash=0.95)
        kit.jitter(stub, 0.35, seed=3, scale=0.9, min_z=-99)
        dark = pal(f"{tag}_hole", 0x01, metallic=0.1, roughness=0.9)
        w.sphere("capsule_hole", (0.0, 16.5, cap_z), (2.7, 0.5, 2.6), dark, 16, 8)
    grey = {s_: pal(f"{tag}_grey{s_:x}", 0x60 | s_, metallic=0.55, roughness=0.3) for s_ in (4, 6, 8, 10, 12)}
    if wreck:
        grey = {s_: pal(f"{tag}_grey{s_:x}", 0x60 | max(2, s_ - 4), metallic=0.35, roughness=0.55) for s_ in (4, 6, 8, 10, 12)}
    mount_path = [(0.0, 13.2, cap_z - 0.6), (0.0, 10.0, shell_z(0, 10) + 2.3), (0.0, 6.0, shell_z(0, 6) + 1.2),
                  (0.0, 2.0, shell_z(0, 2) + 0.4)]
    mount = w.tube("mount", mount_path, [3.4, 3.9, 2.3, 2.9], grey[10], 20)
    kit.paint_faces(mount, lambda c, nrm: grey[12] if nrm.z > 0.75 else grey[8] if nrm.z > 0.2 else grey[4])

    # Light ridges curving from the housing down to the rim.
    ridge = grey[12]
    for name, pts in (("ridge_l", [(-12.4, 11.4), (-16.5, 11.6), (-21.0, 10.5), (-25.5, 8.4), (-28.6, 6.0)]),
                      ("ridge_r", [(14.2, 9.9), (18.0, 9.3), (22.4, 7.8), (26.6, 5.7), (29.4, 3.4)])):
        kit.groove(name, pts, surface, ridge, radius=0.55, sink=0.2, step=0.6)
    # Dark seams: down the front plates and the right panel.
    seam = pal(f"{tag}_seam", 0x62 if not wreck else 0x01, metallic=0.3, roughness=0.6)

    # The front plates over and under the gun band.
    upper, lower = plate_polys()
    for name, polys in (("plate_up", upper), ("plate_low", lower)):
        plate = kit.heightfield(name, polys, lambda x, y, e: surface(x, y) + 0.2 + 0.9 * e, None, spacing=0.9,
                                smooth_angle=45, edge=0.6)
        paint(plate)
    kit.groove("seam_front_up", [(0.5, -0.8), (0.5, -3.3), (0.5, -5.6)], lambda x, y: surface(x, y) + 1.1, seam,
               radius=0.4, sink=0.15)
    kit.groove("seam_front_low", [(0.5, -16.8), (0.5, -20.0), (0.5, -23.6)], lambda x, y: surface(x, y) + 1.1, seam,
               radius=0.4, sink=0.15)
    kit.groove("seam_right", [(16.6, 10.4), (16.6, 5.0), (16.6, -0.4)], surface, seam, radius=0.45, sink=0.15)
    # The vent grille right of it.
    for i, y in enumerate((8.2, 5.6, 3.0, 0.4)):
        x0, x1 = 17.8, 21.6
        zc = surface((x0 + x1) / 2, y)
        w.rounded_box(f"vent{i}", ((x0 + x1) / 2, y, zc + 0.05), (x1 - x0, 0.9, 0.9), grey[10], bevel=0.25)

    # The gun port in the middle of the band: a dark slot with its ember glowing and the muzzle in it.
    slot_y = (BAND[0] + BAND[1]) / 2 - 0.3
    slot_z = surface(0.5, slot_y)
    dark = pal(f"{tag}_slot", 0x01, metallic=0.1, roughness=0.8)
    w.rounded_box("slot", (0.5, slot_y, slot_z - 0.1), (15.0, 5.0, 1.0), dark, bevel=0.3)
    if not wreck:
        ember = pal(f"{tag}_ember", 0x77, metallic=0.0, roughness=0.4, glow=1.8)
        core = pal(f"{tag}_ember_core", 0x7b, metallic=0.0, roughness=0.4, glow=2.6)
        w.sphere("ember", (0.5, slot_y, slot_z + 0.05), (5.6, 1.5, 0.5), ember, 20, 8)
        w.sphere("ember_core", (0.5, slot_y, slot_z + 0.2), (2.6, 0.7, 0.45), core, 16, 6)
    # Bezels round the band's ends.
    for x in (PLATE_X[0] + 0.9, PLATE_X[1] - 0.9):
        w.rounded_box(f"band_end{x:.0f}", (x, (BAND[0] + BAND[1]) / 2, surface(x, slot_y) + 0.2),
                      (1.6, BAND[1] - BAND[0], 1.2), grey[8], bevel=0.3)

    # The red armour of the flanks, 1 pixel over the shell.
    flanks = kit.heightfield("flanks", flank_polys(DOME), lambda x, y, e: surface(x, y) + 0.25 + 0.85 * e, None,
                             spacing=0.6, smooth_angle=45, edge=0.6)
    flank_paint(flanks)

    # The ports: small dark ones above the ridges, large bronze lenses below, each in a grey bezel.
    lens_dark = pal(f"{tag}_port", 0xa2 if not wreck else 0x01, metallic=0.3, roughness=0.2)
    bronze = pal(f"{tag}_lens", 0xa6 if not wreck else 0x02, metallic=0.5, roughness=0.18)
    bronze_hi = pal(f"{tag}_lens_hi", 0xa9 if not wreck else 0x04, metallic=0.5, roughness=0.15)
    for side, x in (("l", -18.0), ("r", 21.0)):
        p, nrm = kit.surface_point(surface, x, 14.4)
        kit.lens(f"port_{side}", p, nrm, (2.1, 1.8, 0.7), lens_dark, sink=0.2, segments=20)
        kit.ring_on(f"port_ring_{side}", p + nrm * 0.1, nrm, 2.4, 0.5, grey[10])
    for side, x in (("l", -19.4), ("r", 19.6)):
        p, nrm = kit.surface_point(surface, x, -6.9)
        lensobj = kit.lens(f"lens_{side}", p, nrm, (3.3, 4.2, 1.3), bronze, sink=0.15, segments=28)
        kit.paint_faces(lensobj, lambda c, nn, px=p.x, py=p.y: bronze_hi if (c.x - px) < -0.8 and (c.y - py) > 0.8 else None)
        kit.ring_on(f"lens_ring_{side}", p + nrm * 0.15, nrm, 3.9, 0.75, grey[10], scale_y=1.22)

    if wreck:
        # Charred: the parts take the wreck's pixels (blacks, browns) wherever they lie.
        for obj in kit.meshes():
            if obj.name.startswith(("ridge", "seam", "vent", "band_end", "mount", "port_ring", "lens_ring")):
                paint(obj, shift=-1.0)


def wreck_whole():
    dome_whole(wreck=True)


NAMES = ("tl", "tm", "tr", "bl", "bm", "br")
kit.pieced("armour_dome", dome_whole, (72, 56),
           [kit.quarter(f"armour_dome_{n_}", DOME, 24 * (i % 3), 28 * (i // 3)) for i, n_ in enumerate(NAMES)])
kit.pieced("armour_dome_wreck", wreck_whole, (72, 56),
           [kit.quarter(f"armour_dome_wreck_{n_}", WRECK, 24 * (i % 3), 28 * (i // 3)) for i, n_ in enumerate(NAMES)])


if __name__ == "__main__":
    kit.run()
