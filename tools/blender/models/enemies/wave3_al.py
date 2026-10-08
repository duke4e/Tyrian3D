"""Enemies of wave 3, batch AL (sheet %, written x25 in models.cfg): FRUIT's machines in their hexagonal sockets,
modelled as their sprites look (models.cfg: yaw=0), on the ground. The kit is wave3_al_kit.py, the pixels
wave3_al_art.py; FRUIT's geodesic ball is in wave3_al_ball.py, CORAL's citadel in wave3_al_citadel.py.

Nearly every FRUIT sprite of the sheet stands in the same socket: a hexagon 16 x 14 pixels in the lower half of
its sprite, a bevelled blue rim round a sunken floor. What stands in it:

- fruit_hex_pod (% 195; enemy 1250, frames 195 197 199): a round vent grille over the floor, eight radial slots
  in it (dark blue across and down, darker on the diagonals), a red lamp in a square bezel at its hub (its frames
  brighten the lamp to orange: the model's lamp glows).
- fruit_hex_eye (% 233; enemy 1251, frames 233 235 237): a grey metal cup in the socket, black inside, a glowing
  orb sitting in it (its frames brighten it from dark red to gold).
- fruit_glyph_tree, fruit_glyph_hook, fruit_glyph_swirl (% 269, 275, 283; enemies 1252-1254): the socket as a
  floor tile with a glyph inlaid in its floor, a green branching sign, a red hook and a white swirl, glowing (their
  frames pulse the glyph's light; the model keeps a middle shade).
- fruit_pillar_r, fruit_pillar_l (% 205, 243; enemies 1259, 1260, placed on their own): a square grey pillar
  standing in the socket, drawn from the side and above; the model leans it up the screen from its foot so that
  its pale end rises highest, a grey valve box clamped to its right (205) or left (243) side near the top.
- fruit_crystal_t, fruit_crystal_b (% 201 above 239; enemies 1255 at (x, y - 29) and 1256 at (x, y - 1)): a slender
  pale ice crystal standing in the socket, leaning up the screen to its point. Cut in two (origin).
- fruit_capsule_t, fruit_capsule_b (% 169 above 207; enemies 1257 at (x, y - 29), 1258 at (x, y - 1)): a
  hexagonal glass capsule standing in the socket under a blue lid with a green light, two rods up its sides,
  leaning up the screen. Cut in two (origin).

usage: Blender -b --factory-startup -P wave3_al.py -- [--only name,name] [--preview <prefix>]
       [--check 1] [--stats 1] [--whole <prefix>]
"""
import math
import os
import sys

from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_al_kit as kit  # noqa: E402
from wave3_al_kit import k, sh, w, pal, Painter  # noqa: E402

HEX_C = (0.0, -7.0)


def is_socket(val):
    return val >> 4 == 3


# --- % 195: the vent pod ---------------------------------------------------------------------------------

POD = kit.frame("POD", 24, (12, 14))
POD_LAMP = 0x76


def pod_grille(x, y, z):
    """The grille over the floor: a low round boss with eight radial slots and a raised bezel at its hub."""
    cx, cy = HEX_C
    dx, dy = x - cx, y - cy
    r = math.hypot(dx, dy)
    boss = 1.2 * max(0.0, 1.0 - (r / 6.2) ** 2) ** 0.5
    a = math.atan2(dy, dx)
    step = math.pi / 4
    off = abs((a + step / 2) % step - step / 2)  # angle to the nearest slot's axis
    across = r * math.sin(off)
    slot = 0.75 * kit.smoothstep(0.95, 0.55, across) * kit.smoothstep(1.7, 2.4, r) * kit.smoothstep(5.6, 4.9, r)
    bezel = 0.35 * kit.smoothstep(2.0, 1.4, max(abs(dx), abs(dy)))
    return z + boss - slot + bezel


@kit.model("fruit_hex_pod", mask=lambda: POD.mask())
def fruit_hex_pod():
    painter = kit.socket_painter("pod", extra={6: (2, 3)})
    kit.socket("socket", POD, painter, inner=pod_grille, floor_keep=lambda val: val >> 4 in (3, 6))
    # The lamp at the hub, glowing red, and its bolts on the diagonals.
    lamp = pal("pod_lamp", POD_LAMP, metallic=0.0, roughness=0.15, glow=2.2)
    top = pod_grille(0.0, -7.0, kit.SOCKET_FLOOR)
    w.sphere("lamp", (0.0, -7.0, top - 0.1), (1.05, 1.05, 0.75), lamp, 20, 10)
    bolt = pal("pod_bolt", 0x64, metallic=0.6, roughness=0.3)
    for sx in (-1, 1):
        for sy in (-1, 1):
            bx, by = sx * 3.1, -7.0 + sy * 3.1
            w.sphere(f"bolt{sx}{sy}", (bx, by, pod_grille(bx, by, kit.SOCKET_FLOOR) - 0.05), (0.6, 0.6, 0.4), bolt,
                     10, 5)


# --- % 233: the orb in its cup ---------------------------------------------------------------------------

EYE = kit.frame("EYE", 24, (12, 14))
ORB = 0xf7


@kit.model("fruit_hex_eye", mask=lambda: EYE.mask())
def fruit_hex_eye():
    painter = kit.socket_painter("eye")
    kit.socket("socket", EYE, painter, floor_keep=is_socket)
    # The grey cup (cols 7-16): a short tube with a rolled lip, black inside.
    grey = pal("eye_cup", 0x09, metallic=0.7, roughness=0.28)
    grey_dark = pal("eye_cup_dark", 0x06, metallic=0.65, roughness=0.32)
    black = pal("eye_inside", 0x01, metallic=0.2, roughness=0.6)
    cx, cy = 0.0, -6.4
    fl = kit.SOCKET_FLOOR
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


# --- % 269, 275, 283: the glyph tiles ---------------------------------------------------------------------

def glyph_tile(name, f, ramp, index, glow):
    """The socket as a floor tile, the glyph inlaid in its floor as glowing strokes joining its pixels."""
    painter = kit.socket_painter(name)
    tile = kit.frame(f, 24, (12, 14))
    kit.socket("socket", tile, painter, floor_keep=is_socket, floor_index=0x3a)
    segs, _ = kit.pixel_strokes(tile, lambda val: val >> 4 == ramp and not is_socket(val))
    polys = kit.stroke_polys(segs, 0.42, (12, 14), res=6, smooth=1, epsilon=0.25)
    mat = pal(f"{name}_glyph", index, metallic=0.0, roughness=0.25, glow=glow)
    return kit.relief("glyph", polys, mat, sh.round_profile(aspect=0.5, max_height=0.45), bottom=0.0,
                      base=kit.SOCKET_FLOOR - 0.1, rim=0.12, spacing=0.2)


@kit.model("fruit_glyph_tree", mask=lambda: kit.frame("GLYPH_G2", 24, (12, 14)).mask())
def fruit_glyph_tree():
    glyph_tile("glyph_g", "GLYPH_G2", 2, 0x28, 1.6)


@kit.model("fruit_glyph_hook", mask=lambda: kit.frame("GLYPH_R2", 24, (12, 14)).mask())
def fruit_glyph_hook():
    glyph_tile("glyph_r", "GLYPH_R2", 7, 0x77, 1.6)


@kit.model("fruit_glyph_swirl", mask=lambda: kit.frame("GLYPH_W2", 24, (12, 14)).mask())
def fruit_glyph_swirl():
    glyph_tile("glyph_w", "GLYPH_W2", 0, 0x0b, 1.4)


# --- % 205, 243: the pillars ----------------------------------------------------------------------------------

PIPE_A = kit.frame("PIPE_A", 24, (12, 14))
PIPE_B = kit.frame("PIPE_B", 24, (12, 14))
PILLAR_LEAN = 30.0                  # degrees above the ground
PILLAR_FOOT = (0.0, -6.5, -1.06)    # its axis where it leaves the floor (its front face there at y -8.5, z 2.4)
PILLAR_LEN = 21.4                   # its axis, foot to end (the end's far edge at the sprite's top, y 14)


def pillar(name, f, side):
    """A square grey pillar standing in the socket, leaning up the screen; a valve drum clamped to its side
    (side +1: right, -1: left) near the top."""
    painter = kit.socket_painter(name, extra={6: (3, 5)})
    hole = painter(0x35)
    sock = kit.socket("socket", f, painter, floor_keep=is_socket)
    # The floor dark round the pillar's foot (the hole it stands in).
    w.paint_faces(sock, lambda c, nrm: hole if (abs(c.x) < 5.2 and -10.5 < c.y < -3.5 and nrm.z > 0.5 and
                                                kit.hex_dist(c.x, c.y) > 2.4) else None)
    body = pal(f"{name}_body", 0x68, metallic=0.55, roughness=0.32)
    cap = pal(f"{name}_cap", 0x6b, metallic=0.55, roughness=0.3)
    edge = pal(f"{name}_edge", 0x66, metallic=0.5, roughness=0.35)
    fx, fy, fz = PILLAR_FOOT
    # Built standing (its axis along +z from the foot), then leaned: the face towards -y faces the camera.
    col = w.block("pillar", (fx, fy), 4.0, 4.0, PILLAR_LEN + 4.0, body, rounding=0.9, power=7.0, segments=32,
                  z0=fz - 4.0, dome=0.25)
    w.paint_faces(col, lambda c, nrm: cap if nrm.z > 0.8 else (edge if abs(nrm.x) > 0.7 else body))
    # Two collars: one at the foot, one under the end.
    ring_mat = pal(f"{name}_ring", 0x66, metallic=0.6, roughness=0.3)
    parts = [col]
    for z0, hgt in ((fz + 2.6, 1.4), (fz + PILLAR_LEN - 4.2, 1.1)):
        parts.append(w.block(f"collar{z0:.0f}", (fx, fy), 4.45, 4.45, hgt, ring_mat, rounding=0.4, power=7.0, segments=32,
                             z0=z0))
    # The valve: a grey drum on a short arm, its axis across the screen.
    grey = pal(f"{name}_valve", 0x0a, metallic=0.65, roughness=0.28)
    grey_dark = pal(f"{name}_valve_dark", 0x07, metallic=0.6, roughness=0.32)
    rim = pal(f"{name}_valve_rim", 0x0c, metallic=0.65, roughness=0.25)
    h = 15.0                                   # along the pillar: the drum's centre (sprite y 6.5)
    arm_x0 = side * 3.6
    parts.append(w.lathe_axis("arm", [(0.0, 1.6), (1.6, 1.6), (2.0, 1.2)], grey_dark, (arm_x0, fy, fz + h),
                              (side, 0, 0), 16))
    drum = w.lathe_axis("drum", [(0.0, 3.6), (0.4, 4.6), (1.0, 4.9), (5.6, 4.9), (6.2, 4.6), (6.6, 3.8), (6.8, 2.0),
                                 (6.9, 0.01)], grey, (side * 5.2, fy, fz + h), (side, 0, 0), 32)
    w.paint_faces(drum, lambda c, nrm: grey_dark if nrm.z < -0.2 else None)
    parts.append(drum)
    for x0 in (1.2, 4.6):
        band = kit.torus(f"band{x0}", (0.0, 0.0, 0.0), 4.95, 0.35, rim, 24, 6)
        sh.apply_modifiers(band)
        band.data.transform(Matrix.Translation((side * (5.2 + x0), fy, fz + h)) @
                            Matrix.Rotation(math.radians(90), 4, "Y"))
        parts.append(band)
    kit.lean(parts, PILLAR_FOOT, PILLAR_LEAN)
    for obj in parts:
        kit.clip_below(obj, 0.0)


@kit.model("fruit_pillar_r", mask=lambda: PIPE_A.mask())
def fruit_pillar_r():
    pillar("pillar_r", PIPE_A, 1)


@kit.model("fruit_pillar_l", mask=lambda: PIPE_B.mask())
def fruit_pillar_l():
    pillar("pillar_l", PIPE_B, -1)


# --- % 201 / 239: the crystal ---------------------------------------------------------------------------------

CRYSTAL = kit.frame("CRYSTAL", 24, (12, 28))
CRYSTAL_LEAN = 32.0
CRYSTAL_FOOT = (0.0, -21.4, -0.14)   # the socket's middle (its front edge meets the floor at y -23)
CRYSTAL_LEN = 35.8                   # foot to point (the point at the sprite's row 19, y 9)


def crystal_whole():
    f = CRYSTAL
    painter = kit.socket_painter("crystal", extra={8: (7, 9)})
    hole = painter(0x37)
    sock = kit.socket("socket", f, painter, cy=-21.0, floor_keep=is_socket)
    w.paint_faces(sock, lambda c, nrm: hole if (abs(c.x) < 4.0 and -25.0 < c.y < -17.5 and nrm.z > 0.5 and
                                                kit.hex_dist(c.x, c.y, 0.0, -21.0) > 2.4) else None)
    ice = kit.glossy("crystal_ice", 0x89, roughness=0.06, metallic=0.15, glow=0.18)
    ice_light = kit.glossy("crystal_ice_light", 0x8c, roughness=0.05, metallic=0.15, glow=0.3)
    tip = kit.glossy("crystal_tip", 0x8e, roughness=0.05, metallic=0.1, glow=0.5)
    fx, fy, fz = CRYSTAL_FOOT
    L = CRYSTAL_LEN
    body = kit.prism("crystal", [(fz - 3.0, 3.0), (fz + L - 6.5, 3.0), (fz + L - 2.6, 1.7), (fz + L, 0.0)], ice,
                     fx, fy, 6, phase=-90.0, smooth_angle=20)
    tip_z = fz + L - 6.0

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
        shard.data.transform(m.Translation((fx + dx, fy - 0.5, kit.SOCKET_FLOOR - 0.4)) @
                             m.Rotation(math.radians(ang), 4, "Y") @ m.Rotation(math.radians(-20), 4, "X"))
        k.recalc_normals(shard)
        parts.append(shard)
    kit.lean([body], CRYSTAL_FOOT, CRYSTAL_LEAN)
    for obj in parts:
        kit.clip_below(obj, 0.0)


kit.pieced("fruit_crystal", crystal_whole, (24, 56),
           [kit.piece("fruit_crystal_t", CRYSTAL, 0, 0), kit.piece("fruit_crystal_b", CRYSTAL, 0, 28)])


# --- % 169 / 207: the glass capsule ----------------------------------------------------------------------------

CAPSULE = kit.frame("CAPSULE", 24, (12, 28))
CAPSULE_LEAN = 35.0
CAPSULE_FOOT = (0.0, -23.5, -5.7)    # its axis at its base (its front face meets the ground at y -27.5)
CAPSULE_LEN = 34.8                   # base to the lid's top (the lid's far edge at the sprite's row 19, y 9)


def capsule_whole():
    fx, fy, fz = CAPSULE_FOOT
    L = CAPSULE_LEN
    m = Matrix
    blue_dark = pal("capsule_base", 0x36, metallic=0.5, roughness=0.32)
    blue = pal("capsule_lid", 0x3a, metallic=0.45, roughness=0.3)
    blue_light = pal("capsule_lid_rim", 0x3c, metallic=0.45, roughness=0.28)
    rod_mat = pal("capsule_rod", 0x38, metallic=0.6, roughness=0.3)
    glass = kit.glossy("capsule_glass", 0x3b, alpha=0.55, roughness=0.04, metallic=0.2)
    core = pal("capsule_core", 0x37, metallic=0.2, roughness=0.4, glow=0.15)
    glint = pal("capsule_glint", 0x8f, metallic=0.0, roughness=0.1, glow=0.8)
    green = pal("capsule_light", 0x29, metallic=0.0, roughness=0.15, glow=1.5)
    parts = []
    # The base collar, the glass, the lid (hex prisms, corners left and right).
    base = kit.prism("base", [(fz - 2.0, 8.6), (fz + 6.0, 8.0), (fz + 6.6, 7.5)], blue_dark, fx, fy, 6, smooth_angle=30)
    k.bevel(base, 0.4, 2)
    parts.append(base)
    parts.append(kit.prism("glass", [(fz + 6.0, 7.2), (fz + L - 6.0, 7.2)], glass, fx, fy, 6, smooth_angle=20))
    parts.append(kit.prism("core", [(fz + 6.0, 4.2), (fz + L - 6.0, 4.2)], core, fx, fy, 6, smooth_angle=20))
    lid = kit.prism("lid", [(fz + L - 6.6, 7.4), (fz + L - 6.0, 7.9), (fz + L - 0.8, 7.9), (fz + L, 7.2)], blue_dark,
                    fx, fy, 6, smooth_angle=30)
    w.paint_faces(lid, lambda c, nrm: blue_light if nrm.z > 0.9 else None)
    parts.append(lid)
    # The lid's top: a raised hex plate inside a rim, the green light in its middle.
    plate = kit.prism("plate", [(fz + L - 0.2, 5.8), (fz + L + 0.5, 5.4)], blue, fx, fy, 6, smooth_angle=30)
    parts.append(plate)
    parts.append(w.sphere("light", (fx, fy, fz + L + 0.5), (1.6, 1.6, 0.9), green, 20, 10))
    # The rods up its left and right corners.
    for sx in (-1, 1):
        parts.append(w.lathe_axis(f"rod{sx}", [(0.0, 0.7), (L - 12.0, 0.7)], rod_mat, (fx + sx * 7.35, fy, fz + 6.0),
                                  (0, 0, 1), 12, up=(0, 1, 0)))
    # Glints on the glass towards the camera: thin slanted strips on its front faces.
    for i, (gx, gz, gl) in enumerate(((-3.2, 13.0, 5.0), (-1.4, 18.0, 4.0), (1.0, 11.0, 6.0), (2.6, 20.0, 3.0))):
        strip = w.rounded_box(f"glint{i}", (0.0, 0.0, 0.0), (0.5, 0.2, gl), glint, bevel=0.08, segments=1)
        sh.apply_modifiers(strip)
        strip.data.transform(m.Translation((fx + gx, fy - 6.35, fz + gz)) @ m.Rotation(math.radians(-25), 4, "Y"))
        parts.append(strip)
    kit.lean(parts, CAPSULE_FOOT, CAPSULE_LEAN)
    for obj in parts:
        kit.clip_below(obj, 0.0)


kit.pieced("fruit_capsule", capsule_whole, (24, 56),
           [kit.piece("fruit_capsule_t", CAPSULE, 0, 0), kit.piece("fruit_capsule_b", CAPSULE, 0, 28)])


if __name__ == "__main__":
    kit.run()
