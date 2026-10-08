"""Batch U of wave 3 (sheet S), the tracked carrier of ASTEROID2 and AST. CITY and what it carries; modelled as
the sprites look (models.cfg: yaw=0).

- track_carrier_tl, track_carrier_tr, track_carrier_bl, track_carrier_br (S 165, 167 above 203, 205): the
  levels place it as four sprites (event 12: enemies 548, 549 above 546, 547), its nose down the screen: two
  broad tracks reaching out in front, a grey hull over their back halves with grilled engine decks, red
  beams across it and red side armour, a ball mount on a turret base in the middle and a red glacis
  between the tracks. Its frames (241 and the others) roll the treads and the grilles: a static model.
  Built whole, 48 x 56, and cut into its four pieces (origin).
- carrier_launcher (S 267): the missile launcher the levels set on the carrier's ball mount (enemy 550,
  10 pixels above the carrier's middle): a grey pod with a red stripe, pitched up, seven tubes in its
  sloping face. Drawn at its own origin (origin), raised to sit on the mount.
- carrier_robot (S 271): the grey robot the levels set there instead (enemy 844): a domed head, broad
  shoulders, two arm guns reaching out forward and a gun between them. Drawn at its own origin (origin),
  standing on the mount.

usage: Blender -b --factory-startup -P wave3_u_carrier.py -- [--only name,name] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1] [--whole carrier,loaded --preview <prefix>]
"""
import math
import os
import sys

from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_u_kit as u  # noqa: E402
from wave3_u_kit import art, k, sh, w, pal  # noqa: E402

ORIGIN = (24, 28)   # the art: S 165, 167 above 203, 205, 48 x 56
AX = 0.5            # the carrier's middle (the tracks span x -21 .. 22)
MOUNT = (-0.5, 10.0)  # the ball mount; the launcher's and robot's sprites are centred 10 pixels up
MOUNT_Z = 9.0       # the ball's centre height
MOUNT_R = (6.0, 6.0, 4.6)
SEAT = 12.6         # where the launcher and the robot sit on it


def px(col):
    return col + 0.5 - ORIGIN[0]


def edge(col):
    """A pixel column's left edge as x."""
    return col - ORIGIN[0]


def py(row):
    return ORIGIN[1] - (row + 0.5)


def row_edge(row):
    """A pixel row's top edge as y."""
    return ORIGIN[1] - row


def mats(prefix):
    m = {s: pal(f"{prefix}_grey{s}", s, metallic=0.45, roughness=0.4) for s in range(1, 15)}
    m.update({f"r{s}": pal(f"{prefix}_red{s}", 0x40 | s, metallic=0.4, roughness=0.38) for s in range(1, 12)})
    m["maroon"] = pal(f"{prefix}_maroon", 0xa2, metallic=0.4, roughness=0.45)
    return m


def slab(name, x0, x1, y0, y1, z0, z1, mat, bevel=0.5):
    return w.rounded_box(name, ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), (x1 - x0, y1 - y0, z1 - z0), mat,
                         bevel=bevel, segments=2)


def track(name, x0, x1, m):
    """A track from the hull's back (y 9) to the front (y -27.6): the belt with tread bars across its top
    and round its front, skirts at both sides."""
    parts = []
    y_back, y_front, height = 9.0, row_edge(56) + 0.4, 8.2
    xc = (x0 + x1) / 2
    r = height / 2
    # The belt: a rounded box whose front wraps round a wheel.
    rings = []
    for i in range(13):
        a = math.radians(-90 + 180 * i / 12)  # round the front wheel, bottom to top
        y = y_front + r - r * math.cos(a)
        z = r + r * math.sin(a)
        rings.append((y, z))
    outline = [(y_back, 0.3)] + rings + [(y_back, height)]
    # Built as a slab in the YZ plane, extruded along x.
    belt = k.slab(name + "_belt", outline, x0 + 2.4, x1 - 2.4, m[3])
    belt.data.transform(_yz_to_xyz())
    k.recalc_normals(belt)
    k.smooth(belt, 35)
    parts.append(belt)
    # Tread bars across the top and round the front.
    path = [(yy, zz) for yy, zz in reversed(rings)]  # top to bottom round the front
    top_pts = [(y, height) for y in [y_back - 6.0 - 2.3 * i for i in range(20)] if y > y_front + r]
    pts = top_pts + path[1:-3]
    for i, (yy, zz) in enumerate(pts):
        if yy > 0.0:
            continue
        n_y, n_z = (0.0, 1.0)
        if zz < height - 0.01:
            n_y, n_z = (yy - (y_front + r)) / r, (zz - r) / r
        bar = w.rounded_box(f"{name}_tread{i}", (0.0, 0.0, 0.0), (x1 - x0 - 5.2, 1.3, 1.0), m[7] if n_z > 0.7 else m[5],
                            bevel=0.35)
        sh.apply_modifiers(bar)
        bar.data.transform(Matrix.Translation((xc, yy + n_y * 0.35, zz + n_z * 0.35)) @
                           Matrix.Rotation(-math.atan2(n_y, n_z), 4, "X"))
        parts.append(bar)
    # The skirts: plates at both sides of the belt, rounded at the front.
    for j, (sx0, sx1) in enumerate(((x0, x0 + 2.6), (x1 - 2.6, x1))):
        skirt_poly = [(y_back, 0.0)] + [(y_front + r - (r + 0.3) * math.cos(math.radians(a)),
                                         r + (r + 0.3) * math.sin(math.radians(a))) for a in range(-90, 91, 15)] + [(y_back, height + 0.3)]
        skirt = k.slab(f"{name}_skirt{j}", skirt_poly, sx0, sx1, m[6])
        skirt.data.transform(_yz_to_xyz())
        k.recalc_normals(skirt)
        k.bevel(skirt, 0.35, 2)
        sh.apply_modifiers(skirt)
        k.smooth(skirt, 35)
        w.paint_faces(skirt, lambda c, n: m[8] if n.z > 0.6 else m[4] if n.z < -0.3 else None)
        parts.append(skirt)
        # Hubs along the skirt's outer face.
        for hy in (-8.0, -15.0, -22.0):
            outer = sx0 if j == 0 else sx1
            parts.append(w.lathe_axis(f"{name}_hub{j}{hy}", [(0.0, 1.7), (0.4, 1.8), (0.8, 1.2), (0.9, 0.01)], m[8],
                                      (outer, hy, r), (-1 if j == 0 else 1, 0, 0), 14))
    return parts


def _yz_to_xyz():
    """k.slab builds outlines in its XY plane extruded along Z: this turns (y, z, x) into (x, y, z)."""
    return Matrix(((0, 0, 1, 0), (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 0, 1)))


@u.whole("carrier", (48, 56))
def carrier_whole():
    m = mats("tc")
    grille = pal("tc_grille", 0x01, metallic=0.3, roughness=0.6)
    parts = []

    # The tracks.
    parts += track("track_l", edge(3), edge(19), m)
    parts += track("track_r", edge(30), edge(46), m)

    # The hull over the tracks' back halves: a low body from the back (row 9) to row 31.
    hull_y0, hull_y1 = row_edge(31) + 0.5, row_edge(9)
    parts.append(slab("hull", edge(4), edge(45), hull_y0, hull_y1 - 1.0, 2.0, 8.6, m[4], bevel=0.8))
    # The engine decks at the back, grilles in them.
    for name, c0, c1 in (("deck_l", 6, 17), ("deck_r", 33, 45)):
        x0, x1 = edge(c0), edge(c1)
        parts.append(slab(name, x0, x1, row_edge(14), row_edge(8.6), 6.0, 10.0, m[3], bevel=0.6))
        parts.append(slab(name + "_grille", x0 + 1.0, x1 - 1.0, row_edge(13.4), row_edge(9.4), 9.6, 10.25, grille, bevel=0.2))
        for i in range(4):
            yy = row_edge(10.0) - i * 1.0
            parts.append(w.rounded_box(f"{name}_slat{i}", ((x0 + x1) / 2, yy, 10.2), (x1 - x0 - 2.4, 0.45, 0.5), m[6],
                                       bevel=0.15))
    # The turret base in the middle with its red plate, the ball mount on it.
    base = w.block("turret_base", (MOUNT[0], 13.0), 8.6, 6.8, 9.6, m[6], taper=0.8, rounding=1.2, power=4.5, segments=40)
    w.paint_faces(base, lambda c, n: m[9] if n.z > 0.8 else m[7] if n.z > 0.3 else m[4])
    parts.append(base)
    parts.append(slab("red_plate", edge(22), edge(28), row_edge(14.5), row_edge(8.6), 8.4, 10.3, m["r6"], bevel=0.4))
    ball = w.sphere("ball", (MOUNT[0], MOUNT[1], MOUNT_Z), MOUNT_R, m[9], 32, 16)
    w.paint_faces(ball, lambda c, n: m[12] if n.z > 0.75 and n.x < 0.2 else m[10] if n.z > 0.4 else m[7])
    parts.append(ball)
    parts.append(u.torus("ball_collar", (MOUNT[0], MOUNT[1], 8.6), 5.7, 0.8, m[5], 40, 8))

    # The red beams at either side of the mount (rows 17-21), and the red side armour outside them (rows 17-28).
    for name, c0, c1 in (("beam_l", 10, 19), ("beam_r", 31, 39)):
        beam = slab(name, edge(c0), edge(c1), row_edge(22), row_edge(17), 7.6, 11.4, m["r5"], bevel=0.6)
        sh.apply_modifiers(beam)
        w.paint_faces(beam, lambda c, n: m["r7"] if n.z > 0.8 else m["r3"])
        parts.append(beam)
    for name, x0, x1 in (("side_l", edge(3) - 0.2, edge(9)), ("side_r", edge(40), edge(46) + 0.2)):
        armour = slab(name, x0, x1, row_edge(28.5), row_edge(17.5), 1.0, 10.2, m["r4"], bevel=0.7)
        sh.apply_modifiers(armour)
        w.paint_faces(armour, lambda c, n: m["r6"] if n.z > 0.8 else m["r2"])
        parts.append(armour)
        parts.append(slab(name + "_edge", x0 + 0.6, x1 - 0.6, row_edge(18.6), row_edge(17.3), 9.6, 10.8, m["maroon"],
                          bevel=0.35))
    # The fenders over the tracks (rows 22-31): cowls rounding down at their front and outer edges, and the
    # deck between them with a hatch.
    for name, x_in, x_out in (("fender_l", edge(17), edge(5)), ("fender_r", edge(31), edge(43))):
        lo, hi = min(x_in, x_out), max(x_in, x_out)
        y_back, y_front = row_edge(21), row_edge(31.5)

        def fender_z(x, y, xi=x_in, xo=x_out, yb=y_back, yf=y_front):
            t = abs(x - xi) / abs(xo - xi)                      # 0 inside .. 1 outside
            f = min(1.0, (y - yf) / 3.0)                        # rounding down over the front 3 pixels
            lift = 10.4 - 1.2 * t * t
            edge_fall = math.sqrt(max(0.0, 1.0 - max(0.0, (t - 0.82) / 0.18) ** 2))
            return 2.0 + (lift - 2.0) * math.sqrt(max(0.0, f * (2 - f))) * (0.35 + 0.65 * edge_fall)

        fender = u.q.heightfield(name, [[(lo, y_front), (hi, y_front), (hi, y_back), (lo, y_back)]], fender_z, m[7],
                                 spacing=0.6)
        w.simplify_bottom(fender)
        w.paint_faces(fender, lambda c, n, xi=x_in: m[9] if n.z > 0.9 and abs(c.x - xi) > 6.5 else m[7] if n.z > 0.85
                      else m[5])
        parts.append(fender)
    parts.append(slab("deck", edge(16), edge(31), row_edge(31), row_edge(22), 6.0, 9.0, m[4], bevel=0.5))
    parts.append(slab("hatch", edge(19), edge(28), row_edge(29.5), row_edge(23.5), 8.6, 9.6, m[6], bevel=0.45))

    # The red armour box between the tracks (rows 31-44), its top sloping down to the front, its edges rounded.
    glacis = w.block("glacis", (px(23.5), py(37.5)), 5.6, 7.0, 7.6, m["r5"], taper=0.6, rounding=1.6, power=5.0,
                     segments=40)
    w.paint_faces(glacis, lambda c, n: m["r7"] if n.z > 0.8 and c.x < px(21) else m["r5"] if n.z > 0.8 else m["r2"])
    for v in glacis.data.vertices:  # the top slopes down towards the front
        if v.co.z > 2.0:
            v.co.z -= (row_edge(31) - v.co.y) * 0.25
    parts.append(glacis)
    parts.append(slab("glacis_band", px(17.5), px(29.5), py(33.0), py(31.2), 6.0, 8.7, m[6], bevel=0.5))
    return parts


def carrier_piece(cx, cy):
    objects = carrier_whole()
    u.cut(objects, (cx - 12.0, cx + 12.0, cy - 14.0, cy + 14.0), (cx, cy))
    u.budget(4800)


for _name, _sprite, _cx, _cy in (("track_carrier_tl", 165, -12.0, 14.0), ("track_carrier_tr", 167, 12.0, 14.0),
                                 ("track_carrier_bl", 203, -12.0, -14.0), ("track_carrier_br", 205, 12.0, -14.0)):
    u.model(_name, [(_sprite, True)])(lambda cx=_cx, cy=_cy: carrier_piece(cx, cy))


# --- S 267: the launcher -------------------------------------------------------------------------

def launcher_parts():
    """The launcher in its sprite's coordinates (24 x 28, its centre the carrier's mount), sitting at SEAT:
    a grey pod pitched up, a red stripe along its top, seven tubes in its sloping face."""
    m = mats("cl")
    hole = pal("cl_hole", 0x01, metallic=0.2, roughness=0.7)
    parts = []
    x0, x1 = -8.6, 7.6
    xc = (x0 + x1) / 2
    z0 = SEAT
    back, face_top, face_bottom = 12.2, -2.6, -10.6   # y of the pod's back, its face's top and bottom edges
    top_z, bottom_z = z0 + 8.6, z0 + 0.8
    # The pod: a side profile (y, z) extruded across x, its corners rounded.
    profile = [(back, z0 + 1.6), (back, top_z - 1.8), (back - 1.8, top_z), (face_top, top_z), (face_bottom, bottom_z + 0.6),
               (face_bottom + 2.0, z0), (back - 1.5, z0)]
    pod = k.slab("pod", profile, x0, x1, m[8])
    pod.data.transform(_yz_to_xyz())
    k.recalc_normals(pod)
    k.bevel(pod, 0.7, 3)
    sh.apply_modifiers(pod)
    k.smooth(pod, 35)

    def paint_pod(c, n):
        if n.z > 0.85:
            return m[10] if c.x < xc - 4.0 else m[9]
        if n.z > 0.3 and n.y < -0.3:  # the sloping face
            return m[6]
        return m[5] if n.z > -0.3 else m[3]
    w.paint_faces(pod, paint_pod)
    parts.append(pod)
    # Ribs along the top at both sides of the stripe.
    for x in (xc - 6.0, xc + 1.8, xc + 6.0):
        parts.append(w.rounded_box(f"rib{x}", (x, (back + face_top) / 2, top_z + 0.2), (1.2, back - face_top - 2.0, 0.8),
                                   m[11] if x < xc else m[7], bevel=0.35))
    # The red stripe.
    stripe = w.rounded_box("stripe", (-2.4, (back + face_top) / 2 + 0.6, top_z + 0.25), (4.8, back - face_top - 0.8, 0.9),
                           m["r6"], bevel=0.35)
    sh.apply_modifiers(stripe)
    w.paint_faces(stripe, lambda c, n: m["r8"] if n.z > 0.8 and c.x < -2.4 else m["r6"] if n.z > 0.8 else m["r3"])
    parts.append(stripe)
    # The tubes: four over three, in the sloping face, their mouths dark.
    slope = Vector((0.0, face_bottom - face_top, bottom_z + 0.6 - top_z)).normalized()
    normal = Vector((0.0, -slope.z, slope.y)).normalized()  # out of the face, forward and up
    if normal.z < 0:
        normal = -normal
    face_origin = Vector((xc, face_top, top_z))
    for i, (tx, t) in enumerate([(-6.0, 0.28), (-2.0, 0.28), (2.0, 0.28), (6.0, 0.28), (-4.0, 0.72), (0.0, 0.72),
                                 (4.0, 0.72)]):
        length = (Vector((0, face_bottom - face_top, bottom_z + 0.6 - top_z))).length
        centre = face_origin + Vector((tx, 0, 0)) + slope * (t * length)
        parts.append(w.lathe_axis(f"tube{i}", [(-0.6, 1.75), (0.5, 1.75), (0.8, 1.45), (0.85, 0.01)], m[9],
                                  tuple(centre), tuple(normal), 18))
        parts.append(w.lathe_axis(f"mouth{i}", [(0.5, 1.15), (0.86, 1.15), (0.9, 0.01)], hole, tuple(centre),
                                  tuple(normal), 14))
    # The pivot down into the mount.
    parts.append(w.column("pivot", [(z0 - 1.6, 3.4), (z0 + 0.6, 3.4), (z0 + 1.2, 2.6)], m[4], xc, 2.0, 24))
    return parts


@u.model("carrier_launcher", [(267, True)])
def carrier_launcher():
    launcher_parts()
    u.budget(4800)


# --- S 271: the robot ----------------------------------------------------------------------------

def robot_parts():
    """The robot in its sprite's coordinates (24 x 28, its centre the carrier's mount), standing at SEAT: a
    round hood at the back with a recessed top, broad shoulders, two arm guns reaching forward and out, a
    heavy gun between them pointing down the screen."""
    m = mats("cr")
    hole = pal("cr_hole", 0x01, metallic=0.2, roughness=0.7)
    eye = pal("cr_eye", 0x0e, metallic=0.1, roughness=0.15, glow=0.6)
    parts = []
    z0 = SEAT
    # The hips on the mount.
    parts.append(w.column("hips", [(z0 - 1.6, 3.8), (z0 + 0.6, 3.8), (z0 + 1.4, 3.2)], m[4], 0.0, -1.5, 24))
    # The hood: a squat drum, its rim light, its top recessed, on a neck.
    hx, hy = 0.0, 4.6
    parts.append(w.column("neck", [(z0 + 0.5, 3.0), (z0 + 4.0, 3.0)], m[5], hx, hy - 0.5, 20))
    drum = w.block("hood", (hx, hy), 5.6, 4.7, 4.2, m[10], taper=0.4, rounding=1.4, power=2.6, segments=40, z0=z0 + 3.6)
    w.paint_faces(drum, lambda c, n: m[12] if n.z > 0.6 and c.x < hx - 1.0 else m[10] if n.z > 0.6 else m[7])
    parts.append(drum)
    parts.append(w.block("hood_top", (hx, hy + 0.2), 3.5, 2.9, 0.7, m[8], rounding=0.3, power=2.4, segments=32,
                         z0=z0 + 7.3))
    parts.append(w.rounded_box("visor", (hx, hy - 3.9, z0 + 5.8), (5.4, 1.2, 1.6), m[3], bevel=0.4))
    for ex in (-1.4, 1.4):
        parts.append(w.sphere(f"eye{ex}", (hx + ex, hy - 4.35, z0 + 5.9), (0.7, 0.45, 0.55), eye, 10, 6))
    # The shoulders: a broad yoke (rows 14-17).
    yoke = w.block("yoke", (0.0, -2.0), 7.4, 2.2, 3.0, m[9], taper=0.5, rounding=1.0, power=3.0, segments=40, z0=z0 + 2.6)
    w.paint_faces(yoke, lambda c, n: m[11] if n.z > 0.7 and c.x < 0 else m[9] if n.z > 0.7 else m[5])
    parts.append(yoke)
    # The arm guns: from the shoulders out and forward to blocky guns with dark muzzles.
    for side in (-1, 1):
        pts = [(side * 5.8, -2.6, z0 + 4.2), (side * 7.9, -5.2, z0 + 3.0), (side * 9.2, -7.0, z0 + 2.4)]
        parts.append(w.tube(f"arm{side}", u.catmull(pts, 0.5), 2.2, m[8], 14))
        parts.append(w.sphere(f"elbow{side}", pts[1], (2.4, 2.4, 2.0), m[10], 14, 8))
        d = Vector((side * 0.45, -1.0, 0.4)).normalized()
        gun = w.lathe_axis(f"arm_gun{side}", [(0.0, 2.5), (2.6, 2.5), (3.0, 2.1), (3.1, 0.01)], m[7], pts[2], tuple(d), 4,
                           smooth_angle=30)
        parts.append(gun)
        parts.append(w.lathe_axis(f"arm_muzzle{side}", [(2.7, 1.0), (3.12, 1.0), (3.15, 0.01)], hole, pts[2], tuple(d), 12))
    # The heavy gun between them (rows 18-26): a squared barrel housing, its muzzle at the front.
    gun = w.block("gun", (0.0, -8.0), 4.0, 4.8, 4.6, m[8], taper=0.4, rounding=1.0, power=4.0, segments=40, z0=z0 - 0.2)
    w.paint_faces(gun, lambda c, n: m[10] if n.z > 0.7 and c.x < 0 else m[8] if n.z > 0.7 else m[5])
    parts.append(gun)
    parts.append(w.lathe_axis("gun_snout", [(0.0, 2.3), (2.2, 2.3), (2.6, 1.9), (2.7, 0.01)], m[9], (0.0, -10.6, z0 + 2.0),
                              (0, -0.8, 0.6), 20))
    parts.append(w.lathe_axis("gun_muzzle", [(2.3, 1.3), (2.72, 1.3), (2.75, 0.01)], hole, (0.0, -10.6, z0 + 2.0),
                              (0, -0.8, 0.6), 16))
    parts.append(w.rounded_box("gun_rib", (0.0, -8.0, z0 + 4.5), (1.4, 7.6, 0.8), m[11], bevel=0.3))
    return parts


@u.model("carrier_robot", [(271, True)])
def carrier_robot():
    robot_parts()
    u.budget(4800)


@u.whole("loaded", (48, 56))
def loaded_whole():
    """The carrier with the launcher on its mount, for a look at how they meet."""
    carrier_whole()
    objs = launcher_parts()
    u.move(objs, MOUNT[0] + 0.5, MOUNT[1])
    return u.meshes()


if __name__ == "__main__":
    u.run()
