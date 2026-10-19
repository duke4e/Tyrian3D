"""The green tower of TORM, BOTANY A and BONUS (sheet J sprites 13 and 15 above 51 and 53, 2x2 each: one 48 x 56
picture; ground and ground2 layers; not animated), polished (2026-10-19; it replaces wave3_m.py's tower_whole() and
tower_piece(), a pillow plate, a fluted tube and a lathed pod painted in blocks). models.cfg: model green_tower_tl
/ green_tower_tr / green_tower_bl / green_tower_br ... origin; sprite j 13 green_tower_tl yaw=0, sprite j 15
green_tower_tr yaw=0, sprite j 51 green_tower_bl yaw=0, sprite j 53 green_tower_br yaw=0. The levels always put the
four together: 13 at (x, y - 28), 15 at (x + 24, y - 28), 51 at (x, y), 53 at (x + 24, y) (TORM's events 120 and
330, BOTANY A's 90, BONUS's 599 and 1199). Nothing round it is ground: every pixel outside its dark outline is
transparent (no upscale of these sprites exists; modelled from the original pixels).

As the sprites draw it (columns and rows of the 48 x 56 picture), symmetric about column 24: at the top a long pod
lying across the screen (columns 2-46 of rows 4-17): three pale bulging segments (columns 10-19, 21-28 and 29-38,
the middle one a little lower), dark grooves between them, darker green end caps with a light rib (column 5) and a
red lamp on their backs (rows 6-7); under the caps red claws hook down the screen and in towards the middle
(columns 4-11 of rows 16-23), a glowing yellow slit down their middle. Under the pod's front a green neck
narrows down to the stem (columns 9-39 of row 16 to 13-35 of row 23), a grille of dark slats across its front
(columns 17-31 of rows 19-23), small red lamps at its foot (columns 18-19 and 29-30 of rows 24-26). The stem, a
fluted column of pale and green stripes (columns 20-27 of rows 23-38; narrower, 6 pixels, in its middle), stands
on a broad oval plate (columns 2-46 of rows 35-52): its top light green with a light rim along its back and sides
(columns 3-4 and 44-45), two pairs of ribs running up the screen (columns 11-12 and 14, 34 and 36-37), a flange
round the stem's foot; its front face dark (rows 47-51), two light bars across its middle (rows 48 and 50).

Built as the sprites lay it out, so that seen from straight above its silhouette matches theirs and the game's
slanted camera sees it as they do: the plate on the ground at the front, the stem rising from it and leaning back
(up the screen) to the neck, the pod held high at the back. The plate's back is a steep wall, its front a sloping
apron, so the camera sees the dark front face as the sprites draw it. The tower is built whole about x = 0 and
moved to its axis (x = 0.5, column 24), then cut along the sprites' edges (polish_arch.py's cut(): the pieces keep
the whole's shading across the cuts) into the four pieces, each moved so its sprite's centre is its origin.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the ground (z = 0); the
whole's origin is the corner where the four sprites meet (column c of the picture is x = c + 0.5 - 24, row r is
y = 27.5 - r).

Replaces wave3_m.py's tower: remove TOWER_ORIGIN, tower_whole() (its @whole("tower", ...) registration),
tower_piece() and the four model("green_tower_..") lines, and wave3_m_art.py's TOWER (nothing else uses it);
pod(), plate_outline(), plate(), plate_details() and greens() stay: the green skiff (J 169, 207, 245, 283) is
made of them.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes of the
whole and of each piece against enemy_J.png), --preview <prefix> (the whole's and each piece's top and 3/4 views).
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

AXIS_X = 0.5
# The pieces: (name, sprite, the box it covers in the whole's coordinates (x0, x1, y0, y1)).
PIECES = [("green_tower_tl", 13, (-24.0, 0.0, 0.0, 28.0)), ("green_tower_tr", 15, (0.0, 24.0, 0.0, 28.0)),
          ("green_tower_bl", 51, (-24.0, 0.0, -28.0, 0.0)), ("green_tower_br", 53, (0.0, 24.0, -28.0, 0.0))]
SPRITE_AT = {13: (0, 0), 15: (24, 0), 51: (0, 28), 53: (24, 28)}  # top left corners in the 48 x 56 picture

# The plate: its plan at its foot (z = 0) and at its top's edge, superellipses: (centre y, half-width, half-depth
# up the screen, its power, half-depth down the screen, its power). The back is a steep wall, the front an apron.
PLATE_FOOT = (-15.8, 22.4, 8.6, 2.6, 9.0, 1.6)
PLATE_TOP = (-13.5, 21.2, 6.2, 3.0, 6.0, 3.2)
PLATE_H, PLATE_DOME = 4.3, 0.9          # the top's edge, and how much more its middle rises
# The side profile from the foot to the top's edge: (share of the way from the foot's plan to the top's, z).
PLATE_SIDE = [(0.0, 0.0), (0.03, 0.45), (0.3, 1.7), (0.62, 2.95), (0.84, 3.7), (0.93, 4.05), (0.98, 4.24),
              (1.0, PLATE_H)]
LIP_ANGLES = (-28.0, 208.0)            # the lip runs round the back and sides (degrees round the top's middle)
RIBS = [(-12.2, 0.42), (-9.8, 0.36)]   # x of the ribs on the plate's top (left; mirrored) and their half-width
RIB_Y = (-8.9, -16.6)
FRONT_BARS = [(-20.7, 4.4), (-22.9, 3.6)]  # the light bars across the plate's front: (y, half-length)

# The stem: from its foot on the plate up and back to its top, its radius along it (distance from the foot,
# radius): flared at both ends, fluted (FLUTES ridges round it, light and green).
STEM_FOOT, STEM_TOP = Vector((0.0, -9.4, 4.4)), Vector((0.0, 4.5, 13.3))
STEM_PROFILE = [(-1.2, 5.0), (0.0, 4.9), (1.2, 4.6), (2.6, 4.15), (4.0, 3.75), (5.6, 3.5), (8.5, 3.4), (12.0, 3.5),
                (13.8, 3.9), (15.3, 4.3), (16.6, 4.4)]
FLUTES, FLUTE_DEPTH = 10, 0.11
FLANGE_R = 5.9

# The neck: rounded-rectangle sections across the stem's axis, from its top on back into the pod's underside:
# (distance from the stem's foot, half-width, half-depth, corner radius); its front, which the camera sees, carries
# the grille between GRILLE_T along the axis.
NECK = [(15.6, 4.4, 4.4, 4.3), (16.9, 6.9, 4.5, 3.0), (18.4, 11.0, 4.6, 2.4), (20.0, 14.2, 4.7, 2.2),
        (21.8, 15.6, 4.7, 2.0), (23.6, 15.6, 4.5, 2.0), (25.2, 14.8, 4.0, 1.8)]
GRILLE_T = (18.6, 23.4)
GRILLE_X = 7.3                         # its half-width
SLATS = 2                              # light slats across it
PRONG = (9.5, 1.4, 2.0, 13.4, 18.6)   # the prongs down either side of the stem's top: |x|, half-width, half-depth,
#                                        from, to along the axis
NECK_LAMP = (5.9, 15.6, 2.5)           # the red lamps between the prongs and the stem: |x|, along the axis, forward

# The pod: lying across the screen at (POD_Y, POD_Z), POD_SQUASH of its radius in height; the middle segment
# (|x| < GROOVES[0]) of radius R_MID, the side ones R_SIDE, the caps R_CAP rounded off from |x| = POD_CAP to
# POD_END; grooves between them at |x| = GROOVES.
POD_Y, POD_Z, POD_SQUASH = 17.3, 21.4, 0.8
R_MID, R_SIDE, R_CAP = 6.05, 6.85, 5.7
POD_CAP, POD_END = 17.4, 22.6
GROOVES = (4.55, 15.6)
CAP_RIB = 18.6
LAMP = (18.0, 3.5)                     # the red lamps on the caps' backs: |x|, y from the pod's axis
# The claw (left; mirrored): its path under the cap (x, y, height below the pod's axis) and its sections there
# (half-width, half-height).
CLAW = [(-19.0, 12.6, 3.4, 1.8, 1.35), (-19.4, 9.8, 6.0, 1.95, 1.4), (-18.6, 7.2, 8.5, 1.8, 1.3),
        (-16.6, 5.2, 10.1, 1.45, 1.1), (-14.2, 4.3, 10.8, 0.9, 0.7), (-12.4, 4.2, 11.0, 0.18, 0.18)]
CLAW_SLIT = (0.22, 0.62)               # the glowing slit's span along the claw


def materials():
    glow = k.level_palette()

    def mat(name, index, metallic=0.35, roughness=0.4):
        return k.material(name, palette=index, metallic=metallic, roughness=roughness)

    def lit(name, index, strength, roughness=0.25):
        return k.material(name, palette=index, metallic=0.0, roughness=roughness, emission=glow[index],
                          emission_strength=strength)
    return {
        "green": mat("tower_green", 0x28, 0.35, 0.38),
        "green_side": mat("tower_green_side", 0x27, 0.35, 0.42),
        "green_top": mat("tower_green_top", 0x29, 0.35, 0.38),
        "light": mat("tower_light", 0x2b, 0.35, 0.32),
        "dark": mat("tower_dark", 0x24, 0.3, 0.5),
        "slot": mat("tower_slot", 0x21, 0.2, 0.6),
        "slat": mat("tower_slat", 0x26, 0.3, 0.45),
        "pale": mat("tower_pale", 0x2d, 0.15, 0.16),
        "flute": mat("tower_flute", 0x2e, 0.15, 0.22),
        "red": mat("tower_red", 0x75, 0.35, 0.3),
        "red_dark": mat("tower_red_dark", 0x72, 0.35, 0.4),
        "slit": lit("tower_slit", 0x7c, 1.9, 0.2),
        "lamp": lit("tower_lamp", 0x76, 1.2, 0.15),
        "seam": mat("tower_seam", 0x22, 0.3, 0.6),
    }


# --- Helpers ----------------------------------------------------------------------------------------------------

def superellipse_ring(params, z, segments=96, scale=1.0, centre_x=0.0):
    """Points round a superellipse plan (centre y, half-width, up depth, its power, down depth, its power) at z,
    scaled about its centre; the upper and lower halves have their own powers."""
    cy, hw, top, ptop, bottom, pbottom = params
    pts = []
    for j in range(segments):
        a = 2 * math.pi * j / segments
        c, s = math.cos(a), math.sin(a)
        p = ptop if s >= 0 else pbottom
        depth = top if s >= 0 else bottom
        x = math.copysign(abs(c) ** (2 / p), c) * hw * scale
        y = math.copysign(abs(s) ** (2 / p), s) * depth * scale
        pts.append(Vector((centre_x + x, cy + y, z)))
    return pts


def lerp_params(a, b, t):
    return tuple(u + (v - u) * t for u, v in zip(a, b))


def axis_frame(d):
    """Two directions across the axis d: along x, and the one perpendicular to both (pointing forward and up for
    an axis leaning back)."""
    u = Vector((1.0, 0.0, 0.0))
    v = d.cross(u).normalized()
    if v.z < 0:
        v = -v
    return u, v


def rounded_rect_points(hw, hd, r, segments):
    """Points round a rounded rectangle (half-width hw along u, half-depth hd along v), on rays at equal angles."""
    pts = mk.rounded_rect_ring((0.0, 0.0), hw, hd, r, 0.0, segments)
    return [(p.x, p.y) for p in pts]


# --- The parts --------------------------------------------------------------------------------------------------

def plate_top_z(x, y):
    """The plate's top surface height inside its top's edge (the dome)."""
    cy, hw, top, ptop, bottom, pbottom = PLATE_TOP
    dy = y - cy
    p = ptop if dy >= 0 else pbottom
    depth = top if dy >= 0 else bottom
    s = (abs(x / hw) ** p + abs(dy / depth) ** p) ** (1 / p)
    return PLATE_H + PLATE_DOME * max(0.0, 1 - s * s)


def plate(m):
    """The plate: lofted from its foot's plan up its sides (a steep back, a sloping apron at the front), over a
    rounded edge, to its domed top."""
    segments = 84
    rings = []
    for t, z in PLATE_SIDE:
        rings.append(superellipse_ring(lerp_params(PLATE_FOOT, PLATE_TOP, t), z, segments))
    for i in range(1, 9):  # the top, domed, in to its middle
        f = 1 - i / 9
        rings.append(superellipse_ring(PLATE_TOP, PLATE_H + PLATE_DOME * (1 - f * f), segments, scale=f))
    body = k.loft("plate", rings, m["green_top"], start_point=(0, PLATE_FOOT[0], 0.0),
                  end_point=(0, PLATE_TOP[0], PLATE_H + PLATE_DOME))
    k.smooth(body, 50)

    def pick(c, n):
        if n.z > 0.93:
            return None
        if n.y < -0.25:
            return m["dark"]
        return m["green_side"]
    mk.paint(body, pick)
    return body


def plate_details(m, hit):
    """The lip along the top's back and sides, the ribs up the screen, the stem's flange, the bars across the
    front."""
    # The lip: a rounded bead just inside the top's edge.
    a0, a1 = (math.radians(a) for a in LIP_ANGLES)
    pts = []
    count = 30
    for i in range(count + 1):
        a = a0 + (a1 - a0) * i / count
        cy, hw, top, ptop, bottom, pbottom = PLATE_TOP
        c, s = math.cos(a), math.sin(a)
        p = ptop if s >= 0 else pbottom
        depth = top if s >= 0 else bottom
        x = math.copysign(abs(c) ** (2 / p), c) * hw * 0.955
        y = cy + math.copysign(abs(s) ** (2 / p), s) * depth * 0.93
        h = hit(x, y)
        z = h[0].z if h else PLATE_H
        pts.append((x, y, z + 0.05, 0.42))
    lip = mk.smooth_tube("lip", pts, m["light"], 8, iterations=1)
    for v in lip.data.vertices:  # flattened a little: a bead, not a pipe
        h = hit(v.co.x, v.co.y)
        if h and v.co.z > h[0].z:
            v.co.z = h[0].z + (v.co.z - h[0].z) * 0.75
    k.smooth(lip, 60)
    # The ribs: rounded bars following the top.
    for side in (-1, 1):
        for i, (x, hw) in enumerate(RIBS):
            xs = side * abs(x)
            ys = [RIB_Y[0] + (RIB_Y[1] - RIB_Y[0]) * j / 8 for j in range(9)]
            points, ups = [], []
            for y in ys:
                h = hit(xs, y)
                points.append(Vector((xs, y, h[0].z if h else PLATE_H)))
                ups.append(h[1] if h else Vector((0, 0, 1)))
            bar = mk.bar(f"rib{side}_{i}", points, ups, hw, 0.42, 0.3, m["light"], 10, 3.0)
            k.smooth(bar, 50)
    # The flange round the stem's foot: a low collar plate, bolted.
    fx, fy = STEM_FOOT.x, STEM_FOOT.y
    zf = plate_top_z(fx, fy)
    prof = [(FLANGE_R + 0.15, zf - 0.6), (FLANGE_R + 0.15, zf + 0.12), (FLANGE_R - 0.1, zf + 0.42),
            (FLANGE_R - 0.9, zf + 0.55), (3.6, zf + 0.62)]
    flange = mk.lathe("flange", prof, (fx, fy), m["light"], 48)
    k.smooth(flange, 45)
    for i in range(8):
        a = 2 * math.pi * (i + 0.5) / 8
        bx, by = fx + (FLANGE_R - 0.75) * math.cos(a), fy + (FLANGE_R - 0.75) * math.sin(a)
        mk.dome(f"bolt{i}", (bx, by), (0.38, 0.38, 0.28), zf + 0.45, m["green_top"], 8, 3)
    # The bars across the front apron: capsules lying on its slope.
    for i, (y, half) in enumerate(FRONT_BARS):
        pts = []
        for j in range(11):
            x = -half + 2 * half * j / 10
            h = hit(x, y)
            z = h[0].z if h else 1.0
            pts.append((x, y, z + 0.05, 0.42))
        bar = mk.smooth_tube(f"front_bar{i}", pts, m["light"], 10, iterations=1)
        k.smooth(bar, 60)


def stem_frame():
    d = (STEM_TOP - STEM_FOOT).normalized()
    u, v = axis_frame(d)
    return d, u, v


def stem(m):
    """The stem: a fluted column from its flared foot on the plate up to its flared top, leaning back."""
    d, u, v = stem_frame()
    prof = k.profile(STEM_PROFILE, 0.8)
    segments = FLUTES * 4
    rings = []
    for t, r in prof:
        c = STEM_FOOT + d * t
        ring = []
        for j in range(segments):
            a = 2 * math.pi * j / segments
            rr = r * (1 - FLUTE_DEPTH * (0.5 - 0.5 * math.cos(FLUTES * a)))
            ring.append(c + (u * math.cos(a) + v * math.sin(a)) * rr)
        rings.append(ring)
    obj = k.loft("stem", rings, m["flute"], start_point=tuple(STEM_FOOT + d * prof[0][0]),
                 end_point=tuple(STEM_FOOT + d * prof[-1][0]))
    k.smooth(obj, 70)

    def pick(c, n):
        rel = Vector(c) - STEM_FOOT
        rel -= d * rel.dot(d)
        a = math.atan2(rel.dot(v), rel.dot(u))
        return None if math.cos(FLUTES * a) > 0 else m["green_top"]
    mk.paint(obj, pick)
    return obj


def neck_size(t):
    """The neck's half-width and half-depth at t along the stem's axis (between its sections)."""
    for (ta, wa, da, _), (tb, wb, db, _) in zip(NECK, NECK[1:]):
        if ta <= t <= tb:
            f = (t - ta) / (tb - ta)
            return wa + (wb - wa) * f, da + (db - da) * f
    return NECK[-1][1], NECK[-1][2]


def neck(m):
    """The neck: from the stem's top it widens back and up into the pod's underside; a grille of slats across
    its front, prongs down either side of the stem's top and red lamps between them and the stem."""
    d, u, v = stem_frame()
    segments = 48
    rings = []
    for t, hw, hd, r in k.profile(NECK, 0.55):
        c = STEM_FOOT + d * t
        rings.append([c + u * px + v * py for px, py in rounded_rect_points(hw, hd, r, segments)])
    obj = k.loft("neck", rings, m["green"], start_point=tuple(STEM_FOOT + d * NECK[0][0]),
                 end_point=tuple(STEM_FOOT + d * NECK[-1][0]))
    k.smooth(obj, 65)
    t0, t1 = GRILLE_T

    def pick(c, n):
        rel = Vector(c) - STEM_FOOT
        t, x = rel.dot(d), rel.dot(u)
        facing = Vector(n).dot(v)
        if t0 < t < t1 and abs(x) < GRILLE_X and facing > 0.55:
            return m["slot"]
        if facing < -0.3:
            return m["dark"]
        return m["green_side"] if abs(Vector(n).dot(u)) > 0.6 else None
    mk.paint(obj, pick)
    # The slats: rounded bars across the grille, on its face.
    for i in range(SLATS):
        t = t0 + (t1 - t0) * (i + 1) / (SLATS + 1)
        hw, hd = neck_size(t)
        c = STEM_FOOT + d * t + v * (hd - 0.08)
        pts = [tuple(c + u * x) + (0.5,) for x in (-GRILLE_X + 0.5, -GRILLE_X * 0.3, GRILLE_X * 0.3, GRILLE_X - 0.5)]
        slat = mk.smooth_tube(f"slat{i}", pts, m["slat"], 10, iterations=1)
        for vv in slat.data.vertices:  # flattened onto the face
            rel = vv.co - c
            vv.co = c + rel - v * rel.dot(v) * 0.45
        k.smooth(slat, 60)
    # The prongs down either side of the stem's top: rounded bars along the axis.
    px, phw, phd, pa, pb = PRONG
    for side in (-1, 1):
        rings = []
        for i in range(7):
            t = pa + (pb - pa) * i / 6
            c = STEM_FOOT + d * t + u * (side * px) + v * 0.6
            f = 1.0 if i > 0 else 0.7
            rings.append([c + u * qx * f + v * qy * f for qx, qy in rounded_rect_points(phw, phd, 0.9, 20)])
        prong = k.loft(f"prong{side}", rings, m["dark"], start_point=tuple(STEM_FOOT + d * (pa - 0.4) + u * (side * px)
                                                                         + v * 0.6))
        k.smooth(prong, 45)
        mk.paint(prong, lambda c, n: m["green_side"] if Vector(n).dot(v) > 0.5 else None)
    # The red lamps between the prongs and the stem.
    lx, lt, lv = NECK_LAMP
    for side in (-1, 1):
        p = STEM_FOOT + d * lt + u * (side * lx) + v * lv
        mk.ball(f"neck_lamp{side}", tuple(p), (0.9, 0.9, 0.9), m["lamp"], 14, 7)
        mk.ball(f"neck_lamp_seat{side}", tuple(p - v * 0.4), (1.25, 1.25, 1.05), m["red_dark"], 14, 6)
    return obj


def pod_radius(x):
    """The pod's radius across (y) at x: the middle segment, the side ones and the caps, each a cushion rounding
    off into the grooves between them, the caps rounded off at the ends."""
    ax = abs(x)
    g0, g1 = GROOVES
    if ax < g0:
        u = ax / g0
        r = R_MID * (1 - 0.13 * u ** 4)
    elif ax < g1:
        u = abs(ax - (g0 + g1) / 2) / ((g1 - g0) / 2)
        r = R_SIDE * (1 - 0.13 * u ** 4)
    else:
        r = R_CAP * (1 - 0.1 * math.exp(-((ax - g1) / 0.7) ** 2))
        if ax > POD_CAP:
            f = (ax - POD_CAP) / (POD_END - POD_CAP)
            r *= math.sqrt(max(0.0, 1 - f * f))
    # The grooves: a narrow dip where the segments meet.
    for g in GROOVES:
        r -= 0.35 * math.exp(-((ax - g) / 0.3) ** 2)
    return max(r, 0.02)


def pod_z(x, dy, upper=True):
    """The pod's surface height at x, dy across from its axis (upper or lower side)."""
    r = pod_radius(x)
    f = math.sqrt(max(0.0, 1 - (dy / max(r, 0.05)) ** 2))
    return POD_Z + (1 if upper else -1) * r * POD_SQUASH * f


def pod(m):
    """The pod: lathed across the screen, an oval section; its segments pale on top and down their front, the
    grooves dark, the caps green, its underside dark; a rib round each cap, a red lamp on each cap's back."""
    xs = []
    x = -POD_END
    while x < POD_END:
        xs.append(x)
        ax = abs(x)
        near = min(abs(ax - g) for g in GROOVES)
        x += 0.3 if near < 1.1 else 0.45 if ax > POD_CAP else 0.7 if near < 2.6 else 1.15
    xs.append(POD_END)
    segments = 36
    rings = []
    for x in xs[1:-1]:
        r = pod_radius(x)
        rings.append([Vector((x, POD_Y + r * math.cos(2 * math.pi * j / segments),
                              POD_Z + r * POD_SQUASH * math.sin(2 * math.pi * j / segments))) for j in range(segments)])
    obj = k.loft("pod", rings, m["green"], start_point=(-POD_END, POD_Y, POD_Z), end_point=(POD_END, POD_Y, POD_Z))
    # The pale paint's edge: split along a line round the segments (lower down the front than at the back).
    bm = bmesh.new()
    bm.from_mesh(obj.data)

    def pale_field(co):
        dy = co.y - POD_Y
        limit = -0.15 if dy < 0 else 0.3
        return (co.z - POD_Z) / (R_SIDE * POD_SQUASH) - limit
    mk.split_along(bm, {vv: pale_field(vv.co) for vv in bm.verts}, 0.0)
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
    bm.to_mesh(obj.data)
    bm.free()
    k.smooth(obj, 60)

    def pick(c, n):
        ax = abs(c.x)
        if any(abs(ax - g) < 0.3 for g in GROOVES):
            return m["seam"]
        if n.z < -0.45:
            return m["dark"]
        if ax < GROOVES[1] - 0.25 and pale_field(c) > 0:
            return m["pale"]
        return None
    mk.paint(obj, pick)
    # The ribs round the caps.
    for side in (-1, 1):
        x = side * CAP_RIB
        r = pod_radius(x)
        prof = [(-0.45, r * 0.97), (-0.25, r + 0.3), (0.25, r + 0.3), (0.45, r * 0.97)]
        rings = [[Vector((x + t, POD_Y + rr * math.cos(2 * math.pi * j / 40),
                          POD_Z + rr * POD_SQUASH * math.sin(2 * math.pi * j / 40))) for j in range(40)]
                 for t, rr in prof]
        rib = k.loft(f"cap_rib{side}", rings, m["light"], cap_start=False, cap_end=False)
        k.smooth(rib, 50)
        # The red lamp on the cap's back: a red glass dome on a dark seat.
        lx, ly = side * LAMP[0], POD_Y + LAMP[1]
        z = pod_z(lx, LAMP[1])
        mk.dome(f"lamp_seat{side}", (lx, ly), (1.5, 1.4, 0.75), z - 0.5, m["red_dark"], 16, 4)
        mk.dome(f"lamp{side}", (lx, ly), (1.0, 0.95, 0.8), z - 0.08, m["lamp"], 16, 5)
    return obj


def across_of(t):
    """The claw section's across direction for a path tangent t (as claw() builds it)."""
    across = t.cross(Vector((0, 0, 1)))
    if across.length < 1e-4:
        across = Vector((1, 0, 0))
    return across.normalized()


def up_of(t):
    up = across_of(t).cross(t).normalized()
    return up if up.z >= 0 else -up


def claw(m, side):
    """A red claw hooking down from under a cap, forward and in towards the middle, a glowing slit down its outer
    face."""
    pts = mk.chaikin([(-side * x, y, POD_Z - h, w, hh) for x, y, h, w, hh in CLAW], 2, closed=False)
    rings = []
    n = len(pts)
    for i, (x, y, z, hw, hh) in enumerate(pts):
        a, b = Vector(pts[max(i - 1, 0)][:3]), Vector(pts[min(i + 1, n - 1)][:3])
        t = (b - a).normalized()
        across = t.cross(Vector((0, 0, 1)))
        if across.length < 1e-4:
            across = Vector((1, 0, 0))
        across.normalize()
        up = across.cross(t).normalized()
        if up.z < 0:
            up = -up
        ring = []
        for j in range(16):
            cu, sv = mk.superellipse_point(2 * math.pi * j / 16, 2.4)
            ring.append(Vector((x, y, z)) + across * (cu * hw) + up * (sv * hh))
        rings.append(ring)
    obj = k.loft(f"claw{side}", rings, m["red"], start_point=tuple(Vector(pts[0][:3]) + Vector((0, 0.6, 0.4))),
                 end_point=tuple(pts[-1][:3]))
    k.smooth(obj, 55)
    mk.paint(obj, lambda c, nrm: m["red_dark"] if nrm.z < -0.5 else None)
    # The glowing slit: a thin strip set into the claw's outer face, tapering at its ends.
    s0, s1 = CLAW_SLIT
    total = len(pts) - 1
    strip = []
    for i, (x, y, z, hw, hh) in enumerate(pts):
        f = i / total
        if not s0 <= f <= s1:
            continue
        a_, b_ = Vector(pts[max(i - 1, 0)][:3]), Vector(pts[min(i + 1, total)][:3])
        t = (b_ - a_).normalized()
        out = Vector((side * 0.55, -0.25, 0.8))
        out -= t * out.dot(t)
        out.normalize()
        taper = math.sin(math.pi * (f - s0) / (s1 - s0)) ** 0.5
        reach = 1.0 / math.sqrt((out.dot(across_of(t)) / hw) ** 2 + (out.dot(up_of(t)) / hh) ** 2)
        strip.append(tuple(Vector((x, y, z)) + out * (reach * 0.92)) + (0.4 * taper + 0.05,))
    slit = mk.smooth_tube(f"slit{side}", strip, m["slit"], 8, iterations=2)
    k.smooth(slit, 60)
    return obj


# --- Build ------------------------------------------------------------------------------------------------------

def build_whole(m):
    body = plate(m)
    bpy.context.view_layer.update()
    hit = mk.surface([body])
    plate_details(m, hit)
    stem(m)
    neck(m)
    pod(m)
    for side in (-1, 1):
        claw(m, side)
    whole = mk.meshes()
    for obj in whole:
        mk.apply(obj)
        obj.data.transform(Matrix.Translation((AXIS_X, 0, 0)))
        if min(v.co.z for v in obj.data.vertices) < -1e-4:  # nothing below the ground (the bars on the apron)
            bm = bmesh.new()
            bm.from_mesh(obj.data)
            bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-5, plane_co=(0, 0, 0),
                                   plane_no=(0, 0, -1), clear_outer=True)
            bm.to_mesh(obj.data)
            bm.free()
    bpy.context.view_layer.update()
    return [o for o in whole if len(o.data.polygons) > 0]


def sprite_mask(sheet, sprite):
    return k.sprite_mask(sheet, sprite)


def whole_mask(sheet):
    mask = [[False] * 48 for _ in range(56)]
    for sprite, (c0, r0) in SPRITE_AT.items():
        part = k.sprite_mask(sheet, sprite)
        for y in range(28):
            for x in range(24):
                if part[y][x]:
                    mask[r0 + y][c0 + x] = True
    return mask


def build():
    options = k.args()
    out = mk.outdir(options)
    k.reset()
    m = materials()
    whole = build_whole(m)
    print("whole tower: %d triangles, %d objects" % (mk.triangles(whole), len(whole)))
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    sheet = None
    if "check" in options:
        sheet = os.path.join(options["check"], "enemy_J.png")
        mk.compare("whole (J 13 + 15 above 51 + 53)", mk.coverage(whole, 48, 56), whole_mask(sheet))
    if "preview" in options:
        mk.preview(options["preview"] + "green_tower_whole", whole, size=(48, 56), scale=8, distance=1.8)
    only = options.get("only", "").split(",") if "only" in options else None
    for name, sprite, box in PIECES:
        if only and name not in only:
            continue
        pieces = [p for p in (cut(src, box, m["seam"]) for src in whole) if p is not None]
        mk.transform(pieces, Matrix.Translation((-(box[0] + box[1]) / 2, -(box[2] + box[3]) / 2, 0)))
        bpy.context.view_layer.update()
        for src in whole:
            src.hide_render = True
        if sheet:
            mk.compare("%s (J %d)" % (name, sprite), mk.coverage(pieces, 24, 28), sprite_mask(sheet, sprite))
        mk.report(name, pieces, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, pieces)
        for obj in pieces:
            bpy.data.objects.remove(obj)
        for src in whole:
            src.hide_render = False


if __name__ == "__main__":
    build()
