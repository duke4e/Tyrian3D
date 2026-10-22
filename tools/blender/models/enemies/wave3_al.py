"""Enemies of wave 3, batch AL (sheet %, written x25 in models.cfg): FRUIT's machines in their hexagonal sockets,
modelled as their sprites look (models.cfg: yaw=0), on the ground. The kit is wave3_al_kit.py, the pixels
wave3_al_art.py; FRUIT's geodesic ball is in wave3_al_ball.py, CORAL's citadel in wave3_al_citadel.py; the vent pod
and the swirl glyph are polish_fruit_pods.py's.

Nearly every FRUIT sprite of the sheet stands in the same socket: a hexagon 16 x 14 pixels in the lower half of
its sprite, a bevelled blue rim round a sunken floor. The socket is the map's (FRUIT's ground is those hexagons, and
the sprites carry a copy of it): the models are what stands in it, on the ground, and things the sprites draw
standing (seen from the side and above, in the oblique view) stand upright, their height along z:

- fruit_hex_eye (% 233; enemy 1251, frames 233 235 237): a grey metal cup, black inside, a glowing orb sitting in
  it (its frames brighten it from dark red to gold).
- fruit_glyph_tree, fruit_glyph_hook (% 269, 275; enemies 1252, 1253): the glyph inlaid in the socket's floor, a green
  branching sign and a red hook, as glowing strokes on the ground
  (their frames pulse the glyph's light; the model keeps a middle shade).
- fruit_pillar_r, fruit_pillar_l (% 205, 243; enemies 1259, 1260, placed on their own): a square grey pillar
  standing upright, 17 high, a grey valve drum clamped to its right (205) or left (243) side near the top.
- fruit_crystal_t, fruit_crystal_b (% 201 above 239; enemies 1255 at (x, y - 29) and 1256 at (x, y - 1)): a slender
  pale ice crystal standing upright, 24 high. The upper sprite draws its upper part, so the two pieces are cut
  across its height (origin), not along the sprites' seam: 201 is the crystal above 70% of its height.
- fruit_capsule_t, fruit_capsule_b (% 169 above 207; enemies 1257 at (x, y - 29), 1258 at (x, y - 1)): a
  hexagonal glass capsule standing upright, 26 high, under a blue lid with a green light, two rods up its sides;
  cut across its height as the crystal (169 above 72% of it: the lid and the glass's top).

usage: Blender -b --factory-startup -P wave3_al.py -- [--only name,name] [--preview <prefix>]
       [--check 1] [--stats 1] [--whole <prefix>]
"""
import math
import os
import sys

from mathutils import Matrix

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_al_kit as kit  # noqa: E402
from wave3_al_kit import k, sh, w, pal  # noqa: E402


def is_socket(val):
    return val >> 4 == 3


# --- % 233: the orb in its cup ---------------------------------------------------------------------------

EYE = kit.frame("EYE", 24, (12, 14))
ORB = 0xf7


@kit.model("fruit_hex_eye", mask=lambda: EYE.mask())
def fruit_hex_eye():
    # The grey cup (cols 7-16), standing on the ground in the map's socket (not modelled): a short tube with a
    # rolled lip, black inside.
    grey = pal("eye_cup", 0x09, metallic=0.7, roughness=0.28)
    grey_dark = pal("eye_cup_dark", 0x06, metallic=0.65, roughness=0.32)
    black = pal("eye_inside", 0x01, metallic=0.2, roughness=0.6)
    cx, cy = 0.0, -6.4
    fl = 0.4  # the cup's floor (its foot on the ground)
    cup = w.lathe_axis("cup", [(fl - 0.4, 4.7), (fl + 0.6, 5.0), (fl + 2.4, 4.9), (fl + 2.9, 4.6), (fl + 3.1, 4.2),
                               (fl + 2.9, 3.7), (fl + 1.0, 3.6), (fl + 0.6, 0.01)], grey, (cx, cy, 0.0), (0, 0, 1), 40,
                       up=(0, 1, 0))
    w.paint_faces(cup, lambda c, nrm: black if (math.hypot(c.x - cx, c.y - cy) < 3.75 and nrm.z > -0.2 and
                                                 c.z < fl + 2.8) else (grey_dark if nrm.z < 0.3 else grey))
    # The orb, glowing, sitting in the cup.
    orb = pal("eye_orb", ORB, metallic=0.0, roughness=0.12, glow=0.9)
    w.sphere("orb", (cx, cy + 0.5, fl + 2.6), (2.35, 2.35, 2.25), orb, 28, 14)
    shine = pal("eye_shine", 0xfb, metallic=0.0, roughness=0.1, glow=1.2)
    w.sphere("shine", (cx - 0.8, cy + 1.4, fl + 4.4), (0.6, 0.5, 0.25), shine, 12, 6)


# --- % 269, 275: the glyph tiles ---------------------------------------------------------------------

def glyph_tile(name, f, ramp, index, glow):
    """The glyph as glowing strokes joining its pixels, lying on the ground: the socket it is inlaid in is the
    map's (not modelled)."""
    tile = kit.frame(f, 24, (12, 14))
    segs, _ = kit.pixel_strokes(tile, lambda val: val >> 4 == ramp and not is_socket(val))
    polys = kit.stroke_polys(segs, 0.42, (12, 14), res=6, smooth=1, epsilon=0.25)
    mat = pal(f"{name}_glyph", index, metallic=0.0, roughness=0.25, glow=glow)
    return kit.relief("glyph", polys, mat, sh.round_profile(aspect=0.5, max_height=0.45), bottom=0.0, base=0.0,
                      rim=0.12, spacing=0.2)


@kit.model("fruit_glyph_tree", mask=lambda: kit.frame("GLYPH_G2", 24, (12, 14)).mask())
def fruit_glyph_tree():
    glyph_tile("glyph_g", "GLYPH_G2", 2, 0x28, 1.6)


@kit.model("fruit_glyph_hook", mask=lambda: kit.frame("GLYPH_R2", 24, (12, 14)).mask())
def fruit_glyph_hook():
    glyph_tile("glyph_r", "GLYPH_R2", 7, 0x77, 1.6)


# --- % 205, 243: the pillars ----------------------------------------------------------------------------------

PIPE_A = kit.frame("PIPE_A", 24, (12, 14))
PIPE_B = kit.frame("PIPE_B", 24, (12, 14))
PILLAR_FOOT = (0.0, -6.5)   # its axis, in the socket's middle
PILLAR_H = 17.0             # its height: the sprites draw it in the oblique view, about 21 pixels up the screen


def pillar(name, f, side):
    """A square grey pillar standing upright in the map's socket (the socket is the map's: not modelled), a
    collar at its foot and one under its pale end; a valve drum clamped to its side (side +1: right, -1: left)
    near the top."""
    body = pal(f"{name}_body", 0x68, metallic=0.55, roughness=0.32)
    cap = pal(f"{name}_cap", 0x6b, metallic=0.55, roughness=0.3)
    edge = pal(f"{name}_edge", 0x66, metallic=0.5, roughness=0.35)
    fx, fy = PILLAR_FOOT
    H = PILLAR_H
    col = w.block("pillar", (fx, fy), 4.0, 4.0, H, body, rounding=0.9, power=7.0, segments=32, z0=0.0, dome=0.25)
    w.paint_faces(col, lambda c, nrm: cap if nrm.z > 0.8 else (edge if abs(nrm.x) > 0.7 else body))
    # Two collars: one at the foot, one under the end.
    ring_mat = pal(f"{name}_ring", 0x66, metallic=0.6, roughness=0.3)
    for z0, hgt in ((0.0, 1.6), (H - 3.6, 1.1)):
        w.block(f"collar{z0:.0f}", (fx, fy), 4.45, 4.45, hgt, ring_mat, rounding=0.4, power=7.0, segments=32, z0=z0)
    # The valve: a grey drum on a short arm, its axis across the screen.
    grey = pal(f"{name}_valve", 0x0a, metallic=0.65, roughness=0.28)
    grey_dark = pal(f"{name}_valve_dark", 0x07, metallic=0.6, roughness=0.32)
    rim = pal(f"{name}_valve_rim", 0x0c, metallic=0.65, roughness=0.25)
    h = H - 5.6                                # the drum's axis
    w.lathe_axis("arm", [(0.0, 1.6), (1.6, 1.6), (2.0, 1.2)], grey_dark, (fx + side * 3.6, fy, h), (side, 0, 0), 16)
    drum = w.lathe_axis("drum", [(0.0, 3.6), (0.4, 4.6), (1.0, 4.9), (5.6, 4.9), (6.2, 4.6), (6.6, 3.8), (6.8, 2.0),
                                 (6.9, 0.01)], grey, (fx + side * 5.2, fy, h), (side, 0, 0), 32)
    w.paint_faces(drum, lambda c, nrm: grey_dark if nrm.z < -0.2 else None)
    for x0 in (1.2, 4.6):
        band = kit.torus(f"band{x0}", (0.0, 0.0, 0.0), 4.95, 0.35, rim, 24, 6)
        sh.apply_modifiers(band)
        band.data.transform(Matrix.Translation((fx + side * (5.2 + x0), fy, h)) @
                            Matrix.Rotation(math.radians(90), 4, "Y"))


@kit.model("fruit_pillar_r", mask=lambda: PIPE_A.mask())
def fruit_pillar_r():
    pillar("pillar_r", PIPE_A, 1)


@kit.model("fruit_pillar_l", mask=lambda: PIPE_B.mask())
def fruit_pillar_l():
    pillar("pillar_l", PIPE_B, -1)


# --- % 201 / 239: the crystal ---------------------------------------------------------------------------------

CRYSTAL = kit.frame("CRYSTAL", 24, (12, 28))
CRYSTAL_FOOT = (0.0, -21.0)          # its axis, in the socket's middle
CRYSTAL_H = 24.0                     # its height (the sprites draw it about 30 pixels up the screen)
CRYSTAL_SPLIT = 0.7 * CRYSTAL_H      # the sprites' seam (row 28) on the crystal as drawn: 21 of its 30 pixels


def split_piece(build, split, top):
    """One of the two sprites of an upright object the sprites draw in the oblique view, one above the other:
    the upper sprite draws the object's upper part, so the pieces are cut across its height at `split` (not
    along the sprites' seam); each is drawn at its sprite's centre (origin), 28 pixels apart, so they meet."""
    build()
    w.bake()
    kept = sh.cut_planes(w.meshes(), [((0.0, 0.0, split), (0.0, 0.0, -1.0 if top else 1.0))])
    sh.move(kept, 0.0, -14.0 if top else 14.0)


def crystal_whole():
    """A slender pale six-sided ice crystal standing upright in the map's socket (the socket is the map's: not
    modelled), two small shards leaning out at its foot."""
    ice = kit.glossy("crystal_ice", 0x89, roughness=0.06, metallic=0.15, glow=0.18)
    ice_light = kit.glossy("crystal_ice_light", 0x8c, roughness=0.05, metallic=0.15, glow=0.3)
    tip = kit.glossy("crystal_tip", 0x8e, roughness=0.05, metallic=0.1, glow=0.5)
    fx, fy = CRYSTAL_FOOT
    H = CRYSTAL_H
    body = kit.prism("crystal", [(0.0, 3.0), (H - 6.5, 3.0), (H - 2.6, 1.7), (H, 0.0)], ice, fx, fy, 6, phase=-90.0,
                     smooth_angle=20)
    tip_z = H - 6.0

    def pick(c, nrm):
        if c.z > tip_z:
            return tip
        return ice_light if nrm.x < -0.3 and nrm.y < 0.2 else ice
    w.paint_faces(body, pick)
    # Two small shards at its foot, leaning out.
    parts = [body]
    for i, (dx, ang, ln, r) in enumerate(((-2.6, 28.0, 7.5, 1.3), (2.4, -24.0, 6.0, 1.1))):
        shard = kit.prism(f"shard{i}", [(-2.0, r), (ln - 2.0, r), (ln, 0.0)], ice, 0.0, 0.0, 6, phase=-90.0,
                          smooth_angle=20)
        m = Matrix
        shard.data.transform(m.Translation((fx + dx, fy - 0.5, 0.0)) @
                             m.Rotation(math.radians(ang), 4, "Y") @ m.Rotation(math.radians(-20), 4, "X"))
        k.recalc_normals(shard)
        parts.append(shard)
    for obj in parts:
        kit.clip_below(obj, 0.0)


kit.model("fruit_crystal_t", mask=kit.piece("fruit_crystal_t", CRYSTAL, 0, 0)[3])(
    lambda: split_piece(crystal_whole, CRYSTAL_SPLIT, True))
kit.model("fruit_crystal_b", mask=kit.piece("fruit_crystal_b", CRYSTAL, 0, 28)[3])(
    lambda: split_piece(crystal_whole, CRYSTAL_SPLIT, False))


# --- % 169 / 207: the glass capsule ----------------------------------------------------------------------------

CAPSULE = kit.frame("CAPSULE", 24, (12, 28))
CAPSULE_FOOT = (0.0, -21.0)          # its axis, in the socket's middle
CAPSULE_H = 26.0                     # its base to its lid's top (the sprites draw it about 32 pixels up the screen)
CAPSULE_SPLIT = 0.72 * CAPSULE_H     # the sprites' seam (row 28) on the capsule as drawn


def capsule_whole():
    """A six-sided glass capsule standing upright in the map's socket (the socket is the map's: not modelled) on
    a dark base, under a blue lid with a green light, rods up its sides, glints on its glass."""
    fx, fy = CAPSULE_FOOT
    L = CAPSULE_H
    m = Matrix
    blue_dark = pal("capsule_base", 0x36, metallic=0.5, roughness=0.32)
    blue = pal("capsule_lid", 0x3a, metallic=0.45, roughness=0.3)
    blue_light = pal("capsule_lid_rim", 0x3c, metallic=0.45, roughness=0.28)
    rod_mat = pal("capsule_rod", 0x38, metallic=0.6, roughness=0.3)
    glass = kit.glossy("capsule_glass", 0x3b, alpha=0.55, roughness=0.04, metallic=0.2)
    core = pal("capsule_core", 0x37, metallic=0.2, roughness=0.4, glow=0.15)
    glint = pal("capsule_glint", 0x8f, metallic=0.0, roughness=0.1, glow=0.8)
    green = pal("capsule_light", 0x29, metallic=0.0, roughness=0.15, glow=1.5)
    # The base collar, the glass, the lid (hex prisms, corners left and right).
    base = kit.prism("base", [(0.0, 8.0), (6.0, 7.8), (6.6, 7.4)], blue_dark, fx, fy, 6, smooth_angle=30)
    k.bevel(base, 0.4, 2)
    kit.prism("glass", [(6.0, 7.2), (L - 6.0, 7.2)], glass, fx, fy, 6, smooth_angle=20)
    kit.prism("core", [(6.0, 4.2), (L - 6.0, 4.2)], core, fx, fy, 6, smooth_angle=20)
    lid = kit.prism("lid", [(L - 6.6, 7.4), (L - 6.0, 7.9), (L - 0.8, 7.9), (L, 7.2)], blue_dark, fx, fy, 6,
                    smooth_angle=30)
    w.paint_faces(lid, lambda c, nrm: blue_light if nrm.z > 0.9 else None)
    # The lid's top: a raised hex plate inside a rim, the green light in its middle.
    kit.prism("plate", [(L - 0.2, 5.8), (L + 0.5, 5.4)], blue, fx, fy, 6, smooth_angle=30)
    w.sphere("light", (fx, fy, L + 0.5), (1.6, 1.6, 0.9), green, 20, 10)
    # The rods up its left and right corners.
    for sx in (-1, 1):
        w.lathe_axis(f"rod{sx}", [(0.0, 0.7), (L - 12.0, 0.7)], rod_mat, (fx + sx * 7.35, fy, 6.0), (0, 0, 1), 12,
                     up=(0, 1, 0))
    # Glints on the glass towards the camera: thin slanted strips on its front faces (heights along the glass).
    for i, (gx, gt, gl) in enumerate(((-3.2, 0.42, 4.0), (-1.4, 0.7, 3.4), (1.0, 0.3, 5.0), (2.6, 0.78, 2.6))):
        strip = w.rounded_box(f"glint{i}", (0.0, 0.0, 0.0), (0.5, 0.2, gl), glint, bevel=0.08, segments=1)
        sh.apply_modifiers(strip)
        strip.data.transform(m.Translation((fx + gx, fy - 6.35, 6.0 + gt * (L - 12.0))) @
                             m.Rotation(math.radians(-25), 4, "Y"))


kit.model("fruit_capsule_t", mask=kit.piece("fruit_capsule_t", CAPSULE, 0, 0)[3])(
    lambda: split_piece(capsule_whole, CAPSULE_SPLIT, True))
kit.model("fruit_capsule_b", mask=kit.piece("fruit_capsule_b", CAPSULE, 0, 28)[3])(
    lambda: split_piece(capsule_whole, CAPSULE_SPLIT, False))


if __name__ == "__main__":
    kit.run()
