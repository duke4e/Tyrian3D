"""The wrecks of FRUIT's machines in their sockets (sheet %, written x25 in models.cfg), built on polish_fruit_ground.py
(2026-10-25, the clean ground's stage 4): what FRUIT's map (194753bd5ac5f6cc) paints where they stand once destroyed,
before they come and where none comes, which tools/terrain/make_cleanground.py erases and the game shows as stand-ins
(models.cfg "wreck x25 <sprite> <live>_wreck", drawn with the live sprite lines' options: yaw=0 height=-4). The
paintings at 4x in the HD tiles (every place of a look paints the same):

- fruit_hex_eye_wreck (x25 233, the orb in its cup; 3 places): the map's tile 101, the same as under FRUIT's vent pod
  (polish_fruit_pods_wreck.py): the socket blown open into a dark pit, a black X across it, four bent plates between
  its arms. The model: that pit (pods_wreck.pit()), the orb's thick grey bowl (live.hex_eye's cup) broken in four along
  the X's diagonals (black breaks), each piece's rim torn off to a jagged edge (0x03), pushed out and tipped into the
  pit, turned a little, its greys burnt one to five shades darker (0x02-0x07: as dark as the painting's plates); the orb
  fallen into the middle, cracked in two, cold (0xf2, glowing 0.08), its inside still faintly hot
  (0xf5, 0.26); a few dark chunks in the X.
- fruit_pillar_r_wreck, fruit_pillar_l_wreck (x25 205, 243; 5 and 3 places): one tile under both, not mirrored: the
  slate pillar's stump (columns 8-15 of rows 7-22 of 205's place), its top broken off on a slant, high at the left (its
  top edge at y 7) and down to the right (y 2.5), a lighter broken face along its top left, a dark rim round the break,
  a dark curved crack up its front from its foot to the right; the drum and its arm gone. The model: live.pillar's
  body (its collars, the cap, the drum, its arm and electrode gone: the painting's stump has none), its top broken
  away above a
  fracture surface (an exact boolean with a heightfield: its front edge's heights fitted to the painting, falling
  0.7 per pixel towards the back so the camera sees the broken face as the painting's narrow light band, roughened by
  noise), its slates a shade or two darker than live (0x66-0x6b, glowing 0.09), the broken face by its light in
  lighter slate (0x67-0x6b), a dark band (0x64) round the break, the crack a dark groove (0x62). The paintings at
  243's places lie 6 px left and 7 px down the screen from where 243's enemies stand (they stand off the map's tile
  grid, 205's on it), so fruit_pillar_l_wreck is the same stump moved by (-6, -7).
- fruit_capsule_b_wreck (x25 207, the capsule's lower sprite; 3 places; its upper sprite 169 has no stand-in): the
  capsule broken open: its base, jagged glass walls (the far rim at y 5 of the lower sprite, the sides higher), the
  lid gone, shards of glass leaning inside, white crack lines, the right corner rod bent in. The model: live.capsule's
  base, its core cut down to a jagged stump (its broken top glowing faintly, a few blue sparks), the glass walls
  rebuilt jagged and thick (see-through as the live glass, a shade darker and less clear: 0x3b at alpha 0.66; their
  broken edges lit 0x3d; the sides standing 7 high, the far and near walls 4-5), five shards inside (0x38-0x3b, their
  thin edges white 0x0e: the painting's crack lines), three white cracks down the far walls, the left rod snapped, the
  right one broken high and bent in; the lid, its plate, light and glints gone.
- fruit_crystal_b_wreck (x25 239, the crystal's lower sprite; 3 places; 201 has no stand-in): the ice crystal's stump,
  about 11 high: a sharp peak at its left (y 5), the break running down to a notch (y 1.5), a thinner spike at its
  right (y 3), the break's faces light (0x8e), a small chip at its foot. The model: live.crystal's body broken off above
  a fracture surface (exact boolean, fitted to the painting as the pillar's), its ice a shade or two paler than live
  (0x8a-0x8d glowing 0.32: the painting's stump is paler than the live sprite), the break light ice (0x8d-0x8f glowing
  0.34-0.42), the left foot shard snapped short, the right one gone, two ice chips at its foot.

Each is built as the live one is (upright, then oblique(K) for the pillars, crystal and capsule, then the camera shear
of polish_lemon_beetle; the eye sheared without oblique as the live; the crystal and capsule in their wholes' frames and
moved to the lower piece's origin: all of the wreck lies under the pieces' seam, so it is the lower piece's whole).
Every mesh triangulated (polish_k_pod.triangulate) and joined into one. Deterministic: no random numbers (mathutils'
Perlin noise).

Coordinates as in polish_fruit_ground.py: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the socket's
floor (z 0); origins at the live pieces' (a single sprite's middle; the lower pieces' middles, (0, -14) of the 24 x 56
wholes). models.cfg (origin on every model line, as the live ones):
model fruit_hex_eye_wreck enemies/fruit_hex_eye_wreck.glb origin; wreck x25 233 fruit_hex_eye_wreck
model fruit_pillar_r_wreck enemies/fruit_pillar_r_wreck.glb origin; wreck x25 205 fruit_pillar_r_wreck
model fruit_pillar_l_wreck enemies/fruit_pillar_l_wreck.glb origin; wreck x25 243 fruit_pillar_l_wreck
model fruit_capsule_b_wreck enemies/fruit_capsule_b_wreck.glb origin; wreck x25 207 fruit_capsule_b_wreck
model fruit_crystal_b_wreck enemies/fruit_crystal_b_wreck.glb origin; wreck x25 239 fruit_crystal_b_wreck

Options after "--": --outdir <dir> (default assets/models/enemies), --preview <prefix>, --only <name,...>.
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
import polish_fruit_ground as live  # noqa: E402
import polish_fruit_pods_wreck as pw  # noqa: E402
import polish_panel_pills_wreck as wk  # noqa: E402
from polish_jaw_gun_wreck import grid_cut, rock, palette_index  # noqa: E402
from polish_coral_manta import split_contour  # noqa: E402
from polish_pineapple import shear_to_camera  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_deli_boss import join  # noqa: E402


def delete(objects):
    for obj in objects:
        data = obj.data
        bpy.data.objects.remove(obj)
        if data is not None and data.users == 0:
            bpy.data.meshes.remove(data)


def remap(obj, table, glow=0.0, metallic=0.35, roughness=0.45):
    """Gives each face whose material has a palette index in table the material of the index it maps to."""
    mesh = obj.data
    for i, mat in enumerate(mesh.materials):
        index = palette_index(mat)
        if index in table:
            mesh.materials[i] = pw.pmat(table[index], glow, metallic, roughness)
    return obj


def keep_side(obj, centre, normal, cap, name):
    """Cuts obj along the vertical plane through centre: keeps the side `normal` points to, capped with cap."""
    no = Vector((-normal[0], -normal[1], 0.0))
    gone = wk.split_piece(obj, (centre[0], centre[1], 0.0), no, cap, name)
    if gone is not None:
        delete([gone])
    return obj


def fracture_profile(points):
    """A function of x interpolating [(x, z)] linearly (held flat past its ends)."""
    def f(x):
        if x <= points[0][0]:
            return points[0][1]
        for (x0, z0), (x1, z1) in zip(points, points[1:]):
            if x <= x1:
                return z0 + (z1 - z0) * (x - x0) / (x1 - x0)
        return points[-1][1]
    return f


def break_top(obj, plan, fracture, mat, step=0.35):
    """obj broken away above the surface z = fracture(x, y) (an exact boolean with a heightfield over plan
    (x0, x1, y0, y1)); the broken faces take mat."""
    x0, x1, y0, y1 = plan
    cutter = wk.heightfield_cutter(obj.name + "_break", x0, x1, y0, y1, step, fracture, 60.0, mat)
    return wk.break_away(obj, cutter)


def band_near(obj, field, mat, t=0.0):
    """Cuts obj along the contour field = t and gives the faces beyond it (field > t) mat."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    vals = {"f": {v: field(v.co) for v in bm.verts}}
    split_contour(bm, vals, "f", t)
    slot = mk.slot_of(obj, mat)
    for f in bm.faces:
        if sum(vals["f"][v] for v in f.verts) / len(f.verts) > t + 1e-6:
            f.material_index = slot
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    return obj


def close_holes(obj):
    """Fills the openings of an open mesh (a part clipped at the floor), so that an exact boolean takes it."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    edges = [e for e in bm.edges if e.is_boundary]
    if edges:
        bmesh.ops.holes_fill(bm, edges=edges, sides=0)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    return obj


def finish(parts):
    for obj in parts:
        mk.apply(obj)
    triangulate(parts)
    bpy.context.view_layer.update()


# --- The orb's wreck (x25 233) ----------------------------------------------------------------------------------------
GAP = 9.0                         # the bowl broken along the diagonals: half the angle between its pieces
# Its pieces (towards, degrees): pushed out (pixels), tipped into the pit (degrees, about their outer rim), turned
# about the vertical (degrees).
SECTORS = [(0.0, 0.7, 16.0, 4.0, 1.7), (90.0, 0.55, 12.0, -3.0, 2.0), (180.0, 0.8, 19.0, -5.0, 1.4),
           (270.0, 0.6, 14.0, 3.0, 1.9)]
BOWL_TORN = 0.9                   # (and the last: how high its torn top is left, roughened by this much)
BOWL_BURNT = {0x03: 0x02, 0x06: 0x03, 0x08: 0x04, 0x0a: 0x05, 0x0c: 0x07}
ORB_DEAD = dict(at=(0.45, -7.4, 0.75), r=1.85, crack=30.0, apart=0.32, tilt=16.0)


def hex_eye_wreck():
    m = {}
    cup, orb = live.hex_eye(m, 233)
    delete([orb])
    mk.apply(cup)
    parts = pw.pit(seed=3.3)
    cx, cy = live.CUP_C
    rim = live.CUP[0] + 0.25
    black = pw.pmat(0x01, metallic=0.2, roughness=0.8)
    torn_edge = pw.pmat(0x03, 0.0, 0.25, 0.65)
    for i, (towards, push, sag, turn, torn) in enumerate(SECTORS):
        piece = cup.copy()
        piece.data = cup.data.copy()
        piece.name = f"bowl{i}"
        bpy.context.scene.collection.objects.link(piece)
        a0, a1 = math.radians(towards - 45.0 + GAP), math.radians(towards + 45.0 - GAP)
        keep_side(piece, (cx, cy), (-math.sin(a0), math.cos(a0)), black, f"bowl{i}_x")
        keep_side(piece, (cx, cy), (math.sin(a1), -math.cos(a1)), black, f"bowl{i}_y")
        # its rim torn off down to a jagged edge
        break_top(piece, (cx - 7.0, cx + 7.0, cy - 7.0, cy + 7.0),
                  lambda x, y, t=torn, j=i: t + BOWL_TORN * wk.fbm(x * 0.9 + 1.7 * j, y * 0.9, 0.6), torn_edge, 0.4)
        a = math.radians(towards)
        pw.spin(piece, turn, (cx, cy))
        piece.data.transform(Matrix.Translation((push * math.cos(a), push * math.sin(a), 0.0)))
        pw.tip(piece, towards, rim + push, sag, (cx, cy))
        remap(piece, BOWL_BURNT, metallic=0.25, roughness=0.6)
        k.smooth(piece, 45)
        parts.append(piece)
    delete([cup])
    # the orb, fallen into the middle, cracked in two, cold; its inside still faintly hot
    o = ORB_DEAD
    cold = pw.pmat(0xf2, 0.08, 0.0, 0.3)
    hot = pw.pmat(0xf5, 0.26, 0.0, 0.5)
    ball = mk.ball("dead_orb", o["at"], (o["r"], o["r"], o["r"] * 0.95), cold, segments=24, rings=12, angle=80)
    mk.apply(ball)
    c = Vector(o["at"])
    n = Vector((math.cos(math.radians(o["crack"])), math.sin(math.radians(o["crack"])), 0.0))
    other = wk.split_piece(ball, c, n, hot, "dead_orb_b")
    for half, sign in ((ball, -1.0), (other, 1.0)):
        foot = c + n * sign * 0.4 - Vector((0, 0, c.z))
        half.data.transform(Matrix.Translation(n * sign * o["apart"]))
        axis = Vector((-n.y, n.x, 0.0))
        half.data.transform(Matrix.Translation(foot) @ Matrix.Rotation(math.radians(o["tilt"] * sign), 4, axis) @
                            Matrix.Translation(-foot))
        k.smooth(half, 60)
        parts.append(half)
    parts += pw.bits("eye", embers=False)
    wk.clip_below(parts, 0.0)
    finish(parts)
    shear_to_camera(parts)
    return parts


# --- The pillars' stump (x25 205, 243) --------------------------------------------------------------------------------
# The heights of the fracture along the pillar's front edge (x, z), fitted to the painting's top edge (a visible
# top y + 2.6 over the front edge: the broken face falls BREAK_SLOPE per pixel towards the back).
PILLAR_BREAK = [(-4.4, 14.2), (-3.4, 14.9), (-2.5, 15.6), (-1.7, 15.4), (-0.9, 14.6), (-0.2, 14.0), (0.6, 13.5),
                (1.5, 13.0), (2.4, 12.2), (3.2, 11.0), (4.4, 9.8)]
BREAK_SLOPE = -0.7
BREAK_NOISE = 0.3
PILLAR_BURNT = {0x67: 0x66, 0x69: 0x68, 0x6b: 0x69, 0x6d: 0x6b}
FRESH_BANDS = [(-99, "f7"), (5.6, "f9"), (6.6, "fa"), (7.6, "fb")]
CRACK = [(-1.5, 0.6), (-1.3, 2.6), (-0.9, 4.6), (-0.3, 6.4), (0.6, 7.7), (1.6, 8.5), (2.3, 8.8)]   # (x, z) on its front
PILLAR_L_SHIFT = (-6.0, -7.0)     # where 243's places paint the stump, from where its enemies stand


def pillar_wreck(shift=(0.0, 0.0)):
    m = {}
    parts = live.pillar(m, 1)
    keep = [o for o in parts if o.name == "pillar"]   # (the collars too are gone: the painting's stump has none)
    delete([o for o in parts if o not in keep])
    body = next(o for o in keep if o.name == "pillar")
    cx, cy = live.PILLAR_C
    front = cy - live.PILLAR_HW
    zf = fracture_profile(PILLAR_BREAK)

    def fracture(x, y):
        return zf(x - cx) + BREAK_SLOPE * (y - front) + BREAK_NOISE * wk.fbm(x * 0.8 + 3.1, y * 0.8, 1.7)
    fresh = {key: live.mat(m, key, idx, 0.35, rough, 0.06) for key, idx, rough in
             (("f7", 0x67, 0.5), ("f9", 0x69, 0.48), ("fa", 0x6a, 0.45), ("fb", 0x6b, 0.42))}
    break_top(body, (cx - 5.0, cx + 5.0, cy - 5.0, cy + 5.0), fracture, fresh["f7"])
    broken = wk.split_off(body, fresh["f7"], "pillar_break")
    live.paint_front(broken, fresh, FRESH_BANDS, 6.8, 5.3)
    k.smooth(broken, 30)
    # the slates two or three shades darker, a dark band round the break
    for obj in keep:
        remap(obj, PILLAR_BURNT, 0.09)
    grid_cut(body, 0.6, axes=("z",))
    band_near(body, lambda co: co.z - (fracture(co.x, co.y) - 0.6), pw.pmat(0x64, 0.0, 0.3, 0.6))
    k.smooth(body, 35)
    # the crack: a dark groove up its front
    crack = mk.smooth_tube("crack", [(x + cx, front - 0.06, z, 0.2) for x, z in CRACK], pw.pmat(0x62, 0.0, 0.2, 0.7),
                           8, iterations=2)
    k.smooth(crack, 60)
    parts = keep + [broken, crack]
    finish(parts)
    if shift != (0.0, 0.0):
        mk.transform(parts, Matrix.Translation((shift[0], shift[1], 0.0)))
    live.oblique(parts, live.PILLAR_RISE / live.PILLAR_H)
    shear_to_camera(parts)
    return parts


# --- The crystal's stump (x25 239) ------------------------------------------------------------------------------------
CRYSTAL_BREAK = [(-3.2, 12.6), (-2.6, 12.2), (-1.6, 11.4), (-0.6, 10.7), (0.15, 9.6), (0.5, 8.9), (0.9, 9.6),
                 (1.4, 10.5), (1.9, 10.8), (2.4, 10.4), (3.2, 9.6)]
CRYSTAL_SLOPE = -0.7
CRYSTAL_NOISE = 0.15
ICE_BREAK = [(-99, "xd"), (5.6, "xe"), (6.6, "xf")]
ICE_BRIGHTER = {0x87: 0x8a, 0x89: 0x8b, 0x8b: 0x8d}   # (the painting's stump is paler than the live sprite)
CHIPS = [((-3.6, -24.4), (0.55, 0.45, 0.35)), ((2.9, -25.2), (0.45, 0.4, 0.3))]   # (whole frame)
SHARD_KEEP = 3.0                  # how much of the left foot shard is left


def crystal_wreck():
    m = {}
    parts = live.crystal(m)
    body = next(o for o in parts if o.name == "crystal")
    shard = next(o for o in parts if o.name == "shard0")
    delete([o for o in parts if o.name == "shard1"])
    fx, fy = live.CRYSTAL["foot"]
    r = live.CRYSTAL["r"]
    zf = fracture_profile(CRYSTAL_BREAK)

    def front(x):
        return fy - r + abs(x - fx) * math.tan(math.radians(30.0))

    def fracture(x, y):
        return zf(x - fx) + CRYSTAL_SLOPE * (y - front(x)) + CRYSTAL_NOISE * wk.fbm(x * 0.9, y * 0.9 + 2.0, 4.1)
    ice = {key: live.mat(m, key, idx, 0.15, rough, glow) for key, idx, rough, glow in
           (("xb", 0x8b, 0.08, 0.3), ("xd", 0x8d, 0.06, 0.34), ("xe", 0x8e, 0.05, 0.38), ("xf", 0x8f, 0.05, 0.42))}
    for obj in (body, shard):
        remap(obj, ICE_BRIGHTER, 0.32, 0.15, 0.08)
    mk.apply(body)
    close_holes(body)
    break_top(body, (fx - 4.0, fx + 4.0, fy - 4.0, fy + 4.0), fracture, ice["xd"], 0.25)
    broken = wk.split_off(body, ice["xd"], "crystal_break")
    live.paint_front(broken, ice, ICE_BREAK, 6.8, 5.0)
    k.smooth(broken, 25)
    # the left foot shard snapped short (along its own axis), its break light ice
    axis = (Matrix.Rotation(math.radians(-22.0), 3, "Y") @ Matrix.Rotation(math.radians(-14.0), 3, "X")) @ \
        Vector((0.0, 0.0, 1.0))
    root = Vector((fx - 2.0, fy - 0.6, 0.0))
    gone = wk.split_piece(shard, root + axis * SHARD_KEEP, axis, ice["xf"], "shard0_gone")
    if gone is not None:
        delete([gone])
    k.smooth(shard, 20)
    parts = [body, broken, shard]
    for i, ((x, y), radii) in enumerate(CHIPS):
        chip = rock(f"ice_chip{i}", (x, y, 0.0), radii, ice["xb"], 2.0 + 1.9 * i)
        parts.append(chip)
    wk.clip_below(parts, 0.0)
    finish(parts)
    live.oblique(parts, live.CRYSTAL["rise"] / live.CRYSTAL["h"])
    return parts


# --- The capsule's wreck (x25 207) ------------------------------------------------------------------------------------
WALL_R, WALL_T, WALL_FOOT = 7.4, 0.32, 2.4    # the glass walls: their radius (as the live glass), thickness, foot
# their broken tops by the side of the capsule (degrees round its middle: height) and their roughness
WALL_TOPS = [(0.0, 7.0), (30.0, 6.2), (60.0, 5.0), (90.0, 4.4), (120.0, 5.2), (150.0, 6.6), (180.0, 7.4),
             (210.0, 6.4), (240.0, 4.8), (270.0, 4.0), (300.0, 4.6), (330.0, 6.0), (360.0, 7.0)]
WALL_JAG = 0.75
CORE_BREAK = (3.3, 0.7)           # the core's stump: its top's mean height, roughness
# Shards inside: base (x, y over the foot, z), heading (degrees), length, width, rise, skew, sides, thickness.
SHARDS = [((-6.0, 0.6, 2.7), -26.0, 7.0, 3.2, 4.4, 0.2, 4, 0.2), ((5.0, 3.0, 2.8), 210.0, 6.0, 2.8, 4.0, -0.3, 3, 0.2),
          ((-1.0, -4.8, 2.7), 70.0, 5.0, 2.4, 4.6, 0.1, 3, 0.18),
          ((3.6, -3.4, 2.8), 130.0, 4.6, 2.0, 2.4, 0.0, 4, 0.18),
          ((-4.2, -3.4, 2.7), 20.0, 3.6, 1.8, 1.8, 0.2, 3, 0.16)]
# White cracks down the far walls' insides: (angle round the middle, degrees) per point and its height.
CRACKS = [[(128.0, 4.5), (134.0, 3.8), (131.0, 3.2), (138.0, 2.7)], [(74.0, 4.8), (80.0, 4.0), (86.0, 3.5)],
          [(100.0, 4.7), (104.0, 4.2), (112.0, 3.9), (110.0, 3.1)]]
ROD_L, ROD_R = 3.7, (8.6, 13.0)   # the left rod snapped at this height; the right one broken here, bent in (degrees)
SPARKS = [(-0.8, 1.2), (1.4, -0.6)]   # over the foot: faint blue sparks on the core's broken top


def wall_top(angle):
    a = angle % 360.0
    for (a0, h0), (a1, h1) in zip(WALL_TOPS, WALL_TOPS[1:]):
        if a <= a1:
            return h0 + (h1 - h0) * (a - a0) / (a1 - a0)
    return WALL_TOPS[-1][1]


def broken_walls(fx, fy, glass, edge):
    """The capsule's glass walls broken down to a jagged rim: a thick six-sided wall (its corners left and right, as
    the live glass) from its foot up to wall_top() roughened; its faces see-through glass, its broken top lit."""
    hexa = live.hexagon(fx, fy, WALL_R, 0.0)
    pts = []
    for i in range(6):
        a, b = Vector(hexa[i]), Vector(hexa[(i + 1) % 6])
        n = max(2, int(round((b - a).length / 0.4)))
        pts += [a + (b - a) * (j / n) for j in range(n)]
    c = Vector((fx, fy))
    verts, faces = [], []
    for j, p in enumerate(pts):
        d = p - c
        q = c + d * ((d.length - WALL_T) / d.length)
        ang = math.degrees(math.atan2(d.y, d.x))
        teeth = WALL_JAG * (abs(wk.perlin(p.x * 1.4 + 0.3, p.y * 1.4, 1.1)) * 1.6 - 0.35)
        h = wall_top(ang) + teeth + (0.25 if j % 3 == 0 else 0.0)
        hi = h - 0.12 * WALL_T
        verts += [(p.x, p.y, WALL_FOOT), (p.x, p.y, h), (q.x, q.y, hi), (q.x, q.y, WALL_FOOT)]
    n = len(pts)
    for j in range(n):
        a, b = 4 * j, 4 * ((j + 1) % n)
        faces += [(a, b, b + 1, a + 1), (a + 1, b + 1, b + 2, a + 2), (a + 2, b + 2, b + 3, a + 3),
                  (a + 3, b + 3, b, a)]
    obj = k.mesh_object("cap_walls", verts, faces, glass)
    k.recalc_normals(obj)
    slot = mk.slot_of(obj, edge)
    for i, poly in enumerate(obj.data.polygons):
        if i % 4 == 1:
            poly.material_index = slot
    k.smooth(obj, 30)
    return obj


def capsule_wreck():
    m = {}
    parts = live.capsule(m)
    by = {o.name: o for o in parts}
    base, core = by["cap_base"], by["cap_core"]
    rod_l, rod_r = by["cap_rod-1"], by["cap_rod+1"]
    delete([o for o in parts if o not in (base, core, rod_l, rod_r)])
    fx, fy = live.CAPSULE["foot"]
    glass = live.mat(m, "wreck_glass", 0x3b, 0.25, 0.06, 0.0, 0.66)
    edge = pw.pmat(0x3d, 0.12, 0.2, 0.3)
    white = pw.pmat(0x0e, 0.22, 0.0, 0.2)
    keep = [base]
    # the core cut down to a jagged stump, its broken top dim but faintly glowing
    mid, rough = CORE_BREAK
    stump_top = pw.pmat(0x3a, 0.14, 0.2, 0.4)
    break_top(core, (fx - 6.0, fx + 6.0, fy - 6.0, fy + 6.0),
              lambda x, y: mid + rough * wk.fbm(x * 0.6 + 1.3, y * 0.6, 2.2), stump_top, 0.5)
    remap(core, {0x38: 0x36}, 0.06, 0.2, 0.45)
    k.smooth(core, 30)
    keep.append(core)
    # the rods: the left snapped, the right broken high and bent in towards the middle
    for rod, at, bend in ((rod_l, ROD_L, 0.0), (rod_r, ROD_R[0], ROD_R[1])):
        tilt = Vector((math.sin(math.radians(25.0)), 0.0, math.cos(math.radians(25.0)))) if rod is rod_r else \
            Vector((0.0, 0.0, 1.0))
        x = fx + (live.CAPSULE["r"] - 0.8) * (1.0 if rod is rod_r else -1.0)
        gone = wk.split_piece(rod, (x, fy, at), tilt, edge, rod.name + "_gone")
        if gone is not None:
            delete([gone])
        if bend:
            foot = Vector((fx + (live.CAPSULE["r"] - 0.8), fy, 2.4))
            rod.data.transform(Matrix.Translation(foot) @ Matrix.Rotation(math.radians(-bend), 4, "Y") @
                               Matrix.Translation(-foot))
        k.smooth(rod, 50)
        keep.append(rod)
    keep.append(broken_walls(fx, fy, glass, edge))
    # shards inside, their thin edges white (the painting's crack lines)
    blue = {i: pw.pmat(i, 0.05, 0.3, 0.25) for i in (0x38, 0x39, 0x3a, 0x3b)}
    for i, ((x, y, z), heading, length, width, rise, skew, sides, thick) in enumerate(SHARDS):
        s = wk.shard(f"cap_shard{i}", (fx + x, fy + y, z), heading, length, width, rise, blue[0x3a], thick, skew, sides)
        mk.paint(s, lambda c, nn: white if abs(nn.z) < 0.45 else
                 blue[pw.live.band(live.light_value(nn, 6.3), [(-99, 0x38), (5.6, 0x39), (6.4, 0x3a), (7.1, 0x3b)])]
                 if nn.z > 0 else blue[0x38])
        keep.append(s)
    # white cracks down the far walls' insides
    for i, crack in enumerate(CRACKS):
        pts = []
        for ang, z in crack:
            a = math.radians(ang)
            rr = WALL_R - WALL_T - 0.06
            pts.append((fx + rr * math.cos(a), fy + rr * math.sin(a), z, 0.1))
        keep.append(k.smooth(mk.smooth_tube(f"cap_crack{i}", pts, white, 6, iterations=1), 60))
    # faint sparks on the core's broken top
    spark = pw.pmat(0x3d, 0.3, 0.0, 0.3)
    for i, (x, y) in enumerate(SPARKS):
        keep.append(mk.ball(f"cap_spark{i}", (fx + x, fy + y, mid + 0.6), (0.32, 0.32, 0.26), spark, 10, 6))
    wk.clip_below(keep, 0.0)
    finish(keep)
    live.oblique(keep, live.CAPSULE["rise"] / live.CAPSULE["h"])
    return keep


# --- Build ------------------------------------------------------------------------------------------------------------
LOWER = (0.0, -14.0)              # the lower piece's origin in the 24 x 56 wholes
MODELS = [
    # name, builder, whole (moved to the lower piece's origin after the camera shear)
    ("fruit_hex_eye_wreck", hex_eye_wreck, False),
    ("fruit_pillar_r_wreck", lambda: pillar_wreck(), False),
    ("fruit_pillar_l_wreck", lambda: pillar_wreck(PILLAR_L_SHIFT), False),
    ("fruit_capsule_b_wreck", capsule_wreck, True),
    ("fruit_crystal_b_wreck", crystal_wreck, True),
]


def build():
    options = k.args()
    out = mk.outdir(options)
    only = set(options["only"].split(",")) if "only" in options else None
    for name, make, whole in MODELS:
        if only is not None and name not in only:
            continue
        k.reset()
        pw.reset_materials()
        parts = make()
        if whole:
            # (all of it lies below the seam between the pieces, in the picture's plane: the lower piece's whole)
            top = max(v.co.y for o in parts for v in o.data.vertices)
            print("%s: highest point %.2f in the picture's plane (the seam at 0)" % (name, top))
            shear_to_camera(parts)
            mk.transform(parts, Matrix.Translation((-LOWER[0], -LOWER[1], 0.0)))
        bpy.context.view_layer.update()
        triangulate(parts)
        obj = join(parts, name)
        obj.data.name = name
        wk.drop_unused([obj])
        bpy.context.scene.view_settings.view_transform = "Standard"
        mk.report(name, [obj], os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, [obj], size=(24, 28), scale=16, distance=0.6)


if __name__ == "__main__":
    build()
