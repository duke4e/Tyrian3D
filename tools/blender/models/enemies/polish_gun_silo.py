"""The blue-grey gun emplacement in the fortress of SAVARA, SAVARA IV, SAVARA Y and SAVARA (episode 5), also DIG
SITE and REEF (sheet F sprites 43 above 81 above 119, 2x2 each: one 24 x 84 picture; ground layer; enemies 171,
172, 173 and their episode 6 copies; the animations 43 45 45 43, 81 83 83 81, 119 121 121 119), polished
(2026-10-19; it replaces wave3_s.py's silo_whole() and its pieces, pixel-painted slabs). models.cfg: model
gun_silo_43 / gun_silo_81 / gun_silo_119 / gun_silo_83 / gun_silo_121 ... origin; sprite f 43 gun_silo_43 yaw=0,
sprite f 81 gun_silo_81 yaw=0, sprite f 119 gun_silo_119 yaw=0, frame f 83 gun_silo_83, frame f 121 gun_silo_121.
The levels stack the three exactly (SAVARA's events 104 and 216, SAVARA Y's 2036, episode 5's 3492 and 4024: 43
at y - 56, 81 at y - 28, 119 at y, the same x; only SAVARA IV sets 43 six pixels right and six down, as its
sprite is drawn there too).

As the sprites draw it, from the top of the picture: the fortress' roof (rows 0-6) and its walls either side are
the map's (SAVARA's bay tiles 342 / 352 / 362, or the wreck 326 / 336 / 346 that the 3D view's erasures turn into
them), and so are the grey apron and the grating in front (rows 48-83 round the gun); the emplacement is what stands
in the bay: two tall blue armour blocks (columns 3-6 and 19-22 of rows 7-16) with a cyan lamp each, between them
a grey housing whose flat top (rows 9-13) breaks into a front sloping down the screen (rows 14-27), a blue panel and
a grey hatch on the slope and two blue light strips at its foot; the bay itself black, blue pillars in its corners
(rows 29-35 and 41-47); in it the gun's cradle, a blue cross bar with two cyan lamps braced back to the housing
and across to the right pillar (rows 36-47), and the gun lying in it pointing down the screen, its barrel with a
blue collar (rows 51-52) out over the apron to the muzzle ring round a dark bore (rows 56-61).

The second frames fire: 45 is 43 again; in 83 the gun has recoiled up the screen (its collar 2 rows up, its muzzle
4 rows, out of 119 into 83) and in 121 a flame bursts from it (ramp 7 from red to white-yellow, rows 57-66). So the
emplacement is built whole twice, cold and firing (the barrel back RECOIL pixels and a flame of three layers, the
hot ones inside, glowing), and each cut along the sprites' edges (polish_redjet.py's method, polish_arch.py's
cut(): the pieces keep the whole's shading across the cuts) into its three pieces, each moved so its sprite's
centre is its origin: cold 43 / 81 / 119 and firing 83 / 121 (45, like 43, needs no model of its own; the cut
leaves the top piece unchanged).

The bay is black in the sprite: a dark floor plate covers it (and hides what the map paints there), so the gun
lies over a dark pit as drawn; the gun points down the screen rising a little (GUN_RISE), so the game's slanted
camera looks into its bore.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the ground (z = 0); the
whole's origin is the middle sprite's centre (column c of the picture is x = c + 0.5 - 12, row r is y = 41.5 - r).

Replaces wave3_s.py's gun silo: remove SILO, silo_painter(), silo_whole(), silo_piece() and the s.pieced("gun_silo",
...) call (and wave3_s_art.py's SILO_A and SILO_B, which nothing else uses), so that it doesn't overwrite these
models.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes of the
pieces against the emplacement's own pixels, written below, and of the whole), --preview <prefix> (the wholes' and
each piece's top and 3/4 views).
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_arch import cut  # noqa: E402  (polish_machine_kit.cut without its material indices shifted twice)


def XE(c):
    """The left edge of the picture's column c."""
    return c - 12.0


def YE(r):
    """The top edge of the picture's row r."""
    return 42.0 - r


# The pieces: (name, sprite, the rows of the picture it covers, firing).
PIECES = [("gun_silo_43", 43, 0, False), ("gun_silo_81", 81, 28, False), ("gun_silo_119", 119, 56, False),
          ("gun_silo_83", 83, 28, True), ("gun_silo_121", 121, 56, True)]

# The emplacement's own pixels in the 24 x 84 picture (the fortress round it left out), by rows: (first row, last
# row, [(first column, last column), ...]).
OWN = [(7, 16, [(3, 6), (19, 22)]), (9, 27, [(7, 17)]), (25, 48, [(1, 22)]), (49, 55, [(10, 12)]),
       (56, 61, [(9, 13)])]
# Firing: the muzzle 4 rows up (rows 52-55 of 83), the flame below it (rows 57-66 of 121).
OWN_FIRING = OWN[:3] + [(49, 51, [(10, 12)]), (52, 55, [(9, 13)]), (57, 62, [(9, 13)]), (63, 64, [(10, 13)]),
                        (65, 66, [(10, 12)])]


ARMOUR = [(XE(3), XE(7)), (XE(19), XE(23))]  # the blue blocks' x (rows 7-16)
ARMOUR_Y = (YE(17), YE(7))
ARMOUR_TOP = 10.2
HOUSING_X = (XE(7), XE(18))
HOUSING_BACK, HOUSING_EDGE, HOUSING_FOOT = YE(9), YE(14), YE(27) + 0.3   # its top from back to edge, its slope's foot
HOUSING_TOP, HOUSING_FOOT_Z = 9.3, 2.9
BAY = (XE(1), XE(23), YE(48) - 0.5, YE(25))                       # the dark floor
PILLARS = [((XE(1), XE(4)), (YE(36), YE(29)), 6.8), ((XE(20), XE(23)), (YE(36), YE(29)), 6.8),
           ((XE(1), XE(5)), (YE(48), YE(41)), 6.0), ((XE(20), XE(23)), (YE(48), YE(41)), 6.0)]
CRADLE = (XE(7.6), XE(18), YE(44), YE(41), 2.5, 5.0)               # the cross bar (x0, x1, y0, y1, z0, z1)
CRADLE_LAMPS = [XE(8) + 0.5, XE(11) + 0.5]
GUN_X = XE(11) + 0.5        # the gun's axis
GUN_Z = 4.1                 # its height at the breech
GUN_BREECH = YE(44)         # where the barrel leaves the breech block
GUN_RISE = math.radians(8)  # the barrel rises towards the muzzle
MUZZLE_END = YE(62)         # the muzzle's front (cold)
RECOIL = 3.5                # how far the barrel goes back when it fires (83, 121)
# The barrel along its axis from the breech (distance, radius): the breech's ring, the barrel, the blue collar,
# the muzzle brake.
BARREL = [(0.0, 1.55), (0.6, 1.55), (0.9, 1.25), (6.8, 1.25), (7.0, 1.5), (9.2, 1.5), (9.4, 1.25), (12.6, 1.25),
          (13.0, 1.9), (13.4, 2.3), (16.3, 2.35), (16.9, 2.15)]
COLLAR = (6.9, 9.3)
MUZZLE_FROM = 12.8          # where the muzzle brake begins (lighter steel: the sprite's pale ring)
BORE_R = 1.15
# The flame (121) from the muzzle along the barrel, FLAME_LENGTH long, FLAME_W wide at most (half-width) and
# FLAME_H high (half-height), in three layers: (share of its length, of its width, of its height, palette index,
# glow); each inner layer shorter and narrower but a little taller, so it shows on top of the one round it, as the
# sprite's flame is hottest down its middle and at its root (rows 57-66 of the picture).
FLAME_LENGTH, FLAME_W, FLAME_H = 8.6, 2.5, 1.55
FLAME = [(1.0, 1.0, 1.0, 0x76, 1.8), (0.8, 0.72, 1.2, 0x7b, 2.6), (0.55, 0.45, 1.38, 0x7f, 3.4)]


def materials():
    glow = k.level_palette()

    def lit(name, index, strength, roughness=0.2):
        return k.material(name, palette=index, metallic=0.0, roughness=roughness, emission=glow[index],
                          emission_strength=strength)
    m = {
        "blue": k.material("silo_blue", palette=0x38, metallic=0.45, roughness=0.35),
        "blue_top": k.material("silo_blue_top", palette=0x82, metallic=0.45, roughness=0.3),
        "grey": k.material("silo_grey", palette=0x06, metallic=0.45, roughness=0.4),
        "grey_top": k.material("silo_grey_top", palette=0x09, metallic=0.45, roughness=0.35),
        "steel": k.material("silo_steel", palette=0x07, metallic=0.6, roughness=0.28),
        "muzzle": k.material("silo_muzzle", palette=0x0a, metallic=0.6, roughness=0.25),
        "dark": k.material("silo_dark", palette=0x02, metallic=0.2, roughness=0.6),
        "bore": k.material("silo_bore", palette=0x01, metallic=0.1, roughness=0.7),
        "lamp": lit("silo_lamp", 0x9d, 1.6),
        "strip": lit("silo_strip", 0x83, 0.7, 0.3),
    }
    for i, (_, _, _, index, strength) in enumerate(FLAME):
        m[("flame", i)] = lit(f"silo_flame_{index:x}", index, strength, 0.5)
    return m


def gun_axis():
    """The gun's axis: its breech point and its direction (down the screen, rising)."""
    start = Vector((GUN_X, GUN_BREECH, GUN_Z))
    d = Vector((0.0, -math.cos(GUN_RISE), math.sin(GUN_RISE)))
    return start, d


def armour(m):
    for i, (x0, x1) in enumerate(ARMOUR):
        block = mk.box(f"armour{i}", x0, x1, ARMOUR_Y[0], ARMOUR_Y[1], 0.0, ARMOUR_TOP, m["blue"])
        mk.bevel(block, 0.45, 3, 35)
        mk.shade(block, 35)
        mk.paint(block, lambda c, n: m["blue_top"] if n.z > 0.85 else None)
        # A cyan lamp in its top near its outer edge (the sprite's columns 3 and 21 of row 12).
        x = x0 + 0.95 if i == 0 else x1 - 1.45
        mk.dome(f"armour_lamp{i}", (x, YE(12) - 0.5), (0.7, 0.85, 0.45), ARMOUR_TOP - 0.05, m["lamp"], 16, 5)


def housing_z(y):
    """The housing's top at y: flat to its edge, then the slope down to its foot."""
    if y >= HOUSING_EDGE:
        return HOUSING_TOP
    t = (HOUSING_EDGE - y) / (HOUSING_EDGE - HOUSING_FOOT)
    return HOUSING_TOP + (HOUSING_FOOT_Z - HOUSING_TOP) * t


def housing(m):
    """The housing: its side profile (flat top, a lip at the edge, the slope down the screen) across its width;
    a blue panel and a grey hatch on the slope, a blue strip, two light strips at its foot."""
    x0, x1 = HOUSING_X
    profile = [(HOUSING_FOOT, 0.0), (HOUSING_BACK, 0.0), (HOUSING_BACK, HOUSING_TOP), (HOUSING_EDGE, HOUSING_TOP),
               (HOUSING_FOOT, HOUSING_FOOT_Z)]
    body = mk.prism("housing", profile, x0, x1, m["grey"], axis="x")
    mk.bevel(body, 1.1, 4, 25)
    mk.shade(body, 35)
    mk.paint(body, lambda c, n: m["grey_top"] if n.z > 0.85 else None)

    def on_slope(name, c0, c1, r0, r1, mat, proud=0.18):
        xa, xb = XE(c0) + 0.15, XE(c1) - 0.15
        ya, yb = YE(r1) + 0.15, YE(r0) - 0.15
        rise = (HOUSING_TOP - HOUSING_FOOT_Z) / (HOUSING_EDGE - HOUSING_FOOT)  # the slope: dz per pixel up the screen

        def top(x, y):
            return HOUSING_TOP + rise * (y - HOUSING_EDGE) + proud
        plate = mk.wedge(name, [(xa, ya), (xb, ya), (xb, yb), (xa, yb)], 0.0, top, mat,
                         bottom=lambda x, y: top(x, y) - 0.8)
        mk.bevel(plate, 0.14, 2, 30)
        mk.shade(plate, 35)
        return plate
    on_slope("panel", 8, 13, 18, 25, m["blue"])
    on_slope("hatch", 14, 18, 21, 25, m["steel"])
    on_slope("strip", 15, 18, 18, 20, m["blue_top"])
    # Light strips along its foot (row 26).
    for i, (c0, c1) in enumerate(((8, 12), (14, 18))):
        bar = mk.box(f"foot_light{i}", XE(c0) + 0.1, XE(c1) - 0.1, HOUSING_FOOT - 0.55, HOUSING_FOOT + 0.25, 0.0,
                     HOUSING_FOOT_Z * 0.55, m["strip"])
        mk.bevel(bar, 0.12, 1, 35)


def bay(m):
    """The bay's dark floor, the blue pillars in its corners, a cyan lamp on the upper right one."""
    x0, x1, y0, y1 = BAY
    floor = mk.box("bay_floor", x0, x1, y0, y1, 0.0, 0.12, m["dark"])
    mk.bevel(floor, 0.05, 1, 35)
    for i, ((px0, px1), (py0, py1), top) in enumerate(PILLARS):
        pillar = mk.box(f"pillar{i}", px0, px1, py0, py1, 0.0, top, m["blue"])
        mk.bevel(pillar, 0.4, 3, 35)
        mk.shade(pillar, 35)
        mk.paint(pillar, lambda c, n: m["blue_top"] if n.z > 0.85 else None)
    mk.dome("pillar_lamp", (XE(20) + 0.6, YE(29) - 0.6), (0.6, 0.6, 0.4), PILLARS[1][2] - 0.05, m["lamp"], 14, 5)


def cradle(m):
    """The gun's cradle: the blue cross bar with two cyan lamps, two arms back to the housing's foot, a brace
    across to the right pillar."""
    x0, x1, y0, y1, z0, z1 = CRADLE
    bar = mk.box("cradle", x0, x1, y0, y1, z0, z1, m["blue"])
    mk.bevel(bar, 0.4, 3, 35)
    mk.shade(bar, 35)
    mk.paint(bar, lambda c, n: m["blue_top"] if n.z > 0.85 else None)
    for i, x in enumerate(CRADLE_LAMPS):
        mk.dome(f"cradle_lamp{i}", (x, YE(43) - 0.5), (0.55, 0.5, 0.35), z1 - 0.05, m["lamp"], 12, 4)
    for i, (x, r) in enumerate(((XE(9) + 0.6, 0.72), (XE(14) + 0.5, 0.72), (XE(16) + 0.5, 0.55))):
        mk.smooth_tube(f"arm{i}", [(x, y1 - 0.3, z1 - 0.8, r), (x, YE(39), z1 - 0.2, r), (x, YE(36.5), 3.6, r),
                                   (x, HOUSING_FOOT - 0.2, HOUSING_FOOT_Z * 0.8, r)], m["blue"], 10)
    mk.smooth_tube("brace", [(x1 - 0.4, YE(39), z1 - 0.6, 0.5), (XE(19), YE(39), z1 - 0.3, 0.5),
                             (XE(20.5), YE(39) - 0.3, PILLARS[3][2] - 0.6, 0.5)], m["blue"], 10)
    k.smooth(bpy.data.objects["brace"], 60)
    for i in range(3):
        k.smooth(bpy.data.objects[f"arm{i}"], 60)


def gun(m, firing):
    """The gun: the breech block in the cradle, the barrel (back RECOIL when firing) with its blue collar and the
    muzzle brake round a dark bore; when firing, the flame from the muzzle."""
    start, d = gun_axis()
    if firing:
        start = start - d * RECOIL
    # The breech block, fixed in the cradle (the barrel slides back through it).
    breech = mk.box("breech", GUN_X - 1.9, GUN_X + 1.9, YE(48), CRADLE[2] + 0.4, GUN_Z - 1.9, GUN_Z + 1.5, m["steel"])
    mk.bevel(breech, 0.45, 3, 35)
    mk.shade(breech, 35)
    mk.paint(breech, lambda c, n: m["grey_top"] if n.z > 0.85 else None)
    length = (Vector((GUN_X, MUZZLE_END, 0)) - Vector((GUN_X, GUN_BREECH, 0))).length / math.cos(GUN_RISE)
    scale = length / BARREL[-1][0]
    profile = [(t * scale, r) for t, r in BARREL]
    # A frame along the axis.
    side = Vector((1, 0, 0))
    up = Vector((0.0, math.sin(GUN_RISE), math.cos(GUN_RISE)))
    seg = 24

    def ring(t, r):
        c = start + d * t
        return [c + (side * math.cos(2 * math.pi * j / seg) + up * math.sin(2 * math.pi * j / seg)) * r
                for j in range(seg)]
    rings = [ring(t, r) for t, r in profile]
    # Into the bore: the muzzle's face turns in and down the bore.
    t_end = profile[-1][0]
    rings.append(ring(t_end - 0.05, BORE_R + 0.15))
    rings.append(ring(t_end - 0.2, BORE_R))
    rings.append(ring(t_end - 1.8, BORE_R * 0.95))
    barrel = k.loft("barrel", rings, m["steel"], end_point=tuple(start + d * (t_end - 1.8)))
    collar = (COLLAR[0] * scale, COLLAR[1] * scale)

    def pick(c, n):
        t = (Vector(c) - start).dot(d)
        radial = (Vector(c) - (start + d * t)).length
        if t > t_end - 2.2 and radial < BORE_R + 0.08:  # down the bore
            return m["bore"]
        if collar[0] < t < collar[1]:
            return m["blue"]
        if t > MUZZLE_FROM * scale:
            return m["muzzle"]
        return None
    mk.paint(barrel, pick)
    k.smooth(barrel, 45)
    if firing:
        mouth = start + d * (t_end - 0.4)
        seg = 14
        for i, (reach, wide, tall, _, _) in enumerate(FLAME):
            end = FLAME_LENGTH * reach
            rings = []
            count = 12
            for j in range(1, count):
                t = j / count
                # Out of the bore, widest a quarter along, then to a point; the inner layers to their own tips.
                w = FLAME_W * (0.6 + 0.4 * math.sin(math.pi * min(1.0, t / 0.3) / 2)) * \
                    (1 - (max(0.0, t - 0.3) / 0.7) ** 1.6) ** 0.7
                w = max(0.05, w * wide)
                h = max(0.05, FLAME_H * tall * min(1.0, w / (FLAME_W * wide)) ** 0.6)
                c = mouth + d * (end * t)
                ring = []
                for q in range(seg):
                    a = 2 * math.pi * q / seg
                    u = math.copysign(abs(math.cos(a)) ** 0.8, math.cos(a))
                    ring.append(c + side * (w * u) + up * (h * math.sin(a)))
                rings.append(ring)
            cone = k.loft(f"flame{i}", rings, m[("flame", i)], start_point=tuple(mouth - d * 0.2),
                          end_point=tuple(mouth + d * end))
            k.smooth(cone, 70)


def build_whole(m, firing):
    armour(m)
    housing(m)
    bay(m)
    cradle(m)
    gun(m, firing)
    whole = mk.meshes()
    for obj in whole:
        mk.apply(obj)
    return whole


def own_mask(r0, rows=28, firing=False):
    mask = [[False] * 24 for _ in range(84)]
    spans_by_row = OWN_FIRING if firing else OWN
    for first, last, spans in spans_by_row:
        for r in range(first, last + 1):
            for c0, c1 in spans:
                for c in range(c0, c1 + 1):
                    mask[r][c] = True
    return mask[r0:r0 + rows]


def build():
    options = k.args()
    out = mk.outdir(options)
    for firing in (False, True):
        k.reset()
        m = materials()
        whole = build_whole(m, firing)
        state = "firing" if firing else "cold"
        print("whole emplacement (%s): %d triangles, %d objects" % (state, mk.triangles(whole), len(whole)))
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        if "check" in options and not firing:
            mk.compare("whole (43 + 81 + 119, the emplacement's own pixels)", mk.coverage(whole, 24, 84, (0.0, 0.0)),
                       own_mask(0, 84))
        if "preview" in options:
            mk.preview(options["preview"] + "gun_silo_whole_" + state, whole, size=(24, 84), scale=6, distance=1.8)
        for name, sprite, r0, piece_firing in PIECES:
            if piece_firing != firing:
                continue
            y1 = 42.0 - r0
            box = (-12.0, 12.0, y1 - 28.0, y1)
            pieces = [p for p in (cut(src, box, m["dark"]) for src in whole) if p is not None]
            mk.transform(pieces, Matrix.Translation((0, -(y1 - 14.0), 0)))
            bpy.context.view_layer.update()
            for src in whole:
                src.hide_render = True
            if "check" in options:
                mk.compare("%s (F %d)" % (name, sprite), mk.coverage(pieces, 24, 28), own_mask(r0, firing=firing))
            mk.report(name, pieces, os.path.join(out, name + ".glb"))
            if "preview" in options:
                mk.preview(options["preview"] + name, pieces)
            for obj in pieces:
                bpy.data.objects.remove(obj)
            for src in whole:
                src.hide_render = False


if __name__ == "__main__":
    build()
