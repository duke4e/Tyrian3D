"""Batch X of wave 3 (sheet C): DELI's and New Deli's tall objects, which the level events place as sprites
one above the other (the C 77 above 115 above 17 above 55; C 245 above 283), modelled whole as their sprites
look (models.cfg: yaw=0) and cut into the sprites' pieces, drawn at their own origins (origin) so they meet.
Both stand on the ground layer; the sprites draw them as tall towers seen from the side, so the models lean
up the screen from their foot on the floor (as the green tower of wave3_m.py does), their tops high above it.

- red_tower_head, red_tower_vents, red_tower_shaft, red_tower_base (C 77, 115, 17, 55): the grey tower with
  the salmon red bands: a round base on the floor tiles with a red door on its left, two bulging sections on
  a ribbed shaft (red plates on their shoulders and a red lamp under each), a crown with two vents in it
  (the frames 117-127 make them glow: they glow throughout) and at the top a dome with a dark gun port in it
  and a red skirt round it (the frames 79-89 tilt the dome towards the player; the model keeps the first).
- ball_mast_gun, ball_mast_ball (C 245, 283): the gun on a mast over a banded ball on the floor tiles: the
  grey and blue ball, a blue mast rising from it up the screen through a grey yoke to a grey gun pointing
  left with a pale blue stem, and a blue fin curving down from the gun's back.

usage: Blender -b --factory-startup -P wave3_x_tower.py -- [--only name,name] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1] [--whole tower|mast --preview <prefix>]
"""
import math
import os
import sys

from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_x_kit as x  # noqa: E402
from wave3_x_kit import art, k, sh, w, pal  # noqa: E402


# --- C 77 above 115 above 17 above 55: the tower ---------------------------------------------------------

TOWER_ORIGIN = (12, 56)           # the whole tower's art: 24 x 112, its centre between 115 and 17
LEAN = math.radians(16.0)         # the tower's axis, leaning up the screen from its foot
FOOT = Vector((0.5, -42.0, 0.0))  # where the axis leaves the floor (row 98)
AXIS = Vector((0.0, math.cos(LEAN), math.sin(LEAN)))


def ty(row):
    """The y of a row of the whole tower's art (its centre)."""
    return TOWER_ORIGIN[1] - row - 0.5


def t_of_row(row):
    """The distance along the axis whose point lies over the row's centre."""
    return (ty(row) - FOOT.y) / AXIS.y


def on_axis(t):
    return FOOT + AXIS * t


def tower_mats():
    grey = {s: pal(f"rt_grey{s}", s, metallic=0.5, roughness=0.35) for s in range(2, 13)}
    red = {s: pal(f"rt_red{s}", 0x40 | s, metallic=0.35, roughness=0.4) for s in range(4, 12)}
    return grey, red


# The tower's turned sections: (row, radius) from the foot up, as the sprite's widths give them.
TOWER_PROFILE = [
    # The base on the floor.
    (99.5, 8.3), (98.0, 9.0), (95.0, 9.4), (88.0, 9.4), (83.0, 9.2), (81.0, 8.6), (79.5, 7.6), (78.5, 6.9),
    # The lower bulb.
    (77.0, 6.9), (75.5, 7.8), (73.5, 8.8), (70.0, 9.2), (67.0, 9.0), (65.5, 8.0), (64.5, 6.9),
    # The ribbed shaft.
    (60.0, 6.6), (56.0, 6.6), (54.5, 6.9),
    # The upper bulb.
    (53.5, 7.4), (51.5, 8.4), (49.0, 9.1), (44.0, 9.1), (42.5, 8.2), (41.3, 7.0), (40.6, 5.2),
    # The neck and the crown.
    (39.5, 4.4), (38.6, 5.4), (37.6, 7.0), (36.0, 8.6), (31.0, 8.8), (29.4, 7.8), (28.5, 6.8),
    # The cup under the head.
    (26.0, 6.8), (24.6, 6.2), (23.4, 5.2), (22.4, 4.4),
]

HEAD_PROFILE = [(21.6, 5.2), (20.6, 7.2), (19.4, 8.5), (18.0, 9.1), (12.0, 9.1)]  # the skirt, red
DOME_ROW, DOME_R, DOME_L = 11.5, 9.0, 11.6   # the dome's base (grey), its radius and its length along the axis


def tower_whole():
    """The tower along its leaning axis, painted by the sprite: the base, the bulbs and the shaft, the crown
    with its two vents, the head with its red skirt and the dome with the gun port; the floor tiles round the
    base."""
    g = x.grid(art.TOWER, 24)
    grey, red = tower_mats()
    origin = TOWER_ORIGIN
    vent = pal("rt_vent", 0x77, metallic=0.0, roughness=0.3, glow=1.3)
    vent_core = pal("rt_vent_core", 0x7a, metallic=0.0, roughness=0.3, glow=1.8)
    port = pal("rt_port", 0x01, metallic=0.2, roughness=0.6)

    # The floor: the tiles round the base and below it, the base's shadow given the floor's shades.
    def floorish(v, c, r):
        return r >= 84 and (v >> 4 == 6 or r >= 99)
    shadow = lambda v, c, r: v >> 4 == 0 or (v & 15 <= 2 and c >= 18) or (98 <= r <= 107 and v & 15 <= 2)
    fg = x.floor_grid(g, floorish, shadow, seed=4)
    # Under the base the floor is hidden: fill it so that no gap shows round the base.
    for r in range(84, 112):
        for c in range(24):
            if fg[r][c] is None:
                fg[r][c] = 0x64
    x.floor_bed("tiles", fg, origin, top=0.35, prefix="rt_floor")

    # The body: one turned part from the foot to the cup, sunk a little into the floor at its foot.
    prof = [(t_of_row(r) - t_of_row(99.5), rad) for r, rad in TOWER_PROFILE]
    start = on_axis(t_of_row(99.5)) - Vector((0, 0, 3.2))
    body = w.lathe_axis("body", [(0.0, 8.3)] + prof[1:], grey[7], start, AXIS, 36)
    # The head: the red skirt and the grey dome.
    t0 = t_of_row(99.5)
    skirt = w.lathe_axis("skirt", [(t_of_row(r) - t0, rad) for r, rad in HEAD_PROFILE], red[8], start, AXIS, 36)
    td = t_of_row(DOME_ROW) - t0
    dome_prof = [(td + DOME_L * math.sin(math.radians(a)), DOME_R * math.cos(math.radians(a)) + 0.01)
                 for a in range(0, 91, 6)]
    dome = w.lathe_axis("dome", [(td - 0.6, DOME_R)] + dome_prof, grey[8], start, AXIS, 36)

    # Painting: grey, a shade lighter on the bulbs and darker down the sides, eased towards the sprite's
    # shading (blurred, the outline left out); the skirt red.
    shade = x.shades(g, origin, lambda v: v >> 4 == 0 and v & 15 >= 3, blur=2)
    bulbs = [(41.0, 53.5), (65.0, 76.5), (29.0, 37.5), (80.0, 98.5)]

    def grey_at(c, n, base=7.0):
        row = origin[1] - c.y
        s_ = base + (0.8 if any(a <= row <= b for a, b in bulbs) else 0.0)
        s_ = 0.6 * s_ + 0.4 * (shade(c.x, c.y) + 1.0)
        if n.z < 0.35:
            s_ -= 1.6
        elif n.z > 0.85:
            s_ += 0.6
        return grey[int(max(3, min(12, round(s_))))]
    w.paint_faces(body, grey_at)
    w.paint_faces(skirt, lambda c, n: red[7] if n.z < 0.35 else red[9] if n.z > 0.85 else red[8])
    w.paint_faces(dome, lambda c, n: grey_at(c, n, 7.5))

    # The gun port in the dome, near its top, and the red stripe from it down the dome.
    up = Vector((0, 0, 1))
    side_axis = AXIS.cross(up).normalized()
    normal_up = side_axis.cross(AXIS).normalized()    # square to the axis, towards the camera
    centre = start + AXIS * td

    def on_dome(angle, across=0.0, lift=0.0):
        """A point on the dome `angle` degrees from its apex towards the camera (`across`: sideways), and the
        dome's normal there."""
        a = math.radians(angle)
        u = Vector((math.cos(a), math.sin(a), across)).normalized()
        pt = centre + AXIS * (DOME_L * u.x) + normal_up * (DOME_R * u.y) + side_axis * (DOME_R * u.z)
        nv = (AXIS * (u.x / DOME_L) + normal_up * (u.y / DOME_R) + side_axis * (u.z / DOME_R)).normalized()
        return pt + nv * lift, nv
    p, d = on_dome(30.0, -0.1)
    w.lathe_axis("port_rim", [(-0.6, 3.1), (0.1, 3.1), (0.35, 2.3), (0.2, 1.6), (-0.4, 1.6)], grey[4], p, d, 24)
    w.lathe_axis("port", [(-1.6, 1.7), (0.15, 1.7), (0.16, 0.01)], port, p, d, 18)
    stripe = [on_dome(a, 0.0, 0.05)[0] for a in (40, 50, 60, 70)]
    w.tube("stripe", stripe, 0.75, red[9], 8, squash=0.45)

    # The crown's vents: two glowing windows either side of its front, in red frames.
    for sx in (-1, 1):
        tt = t_of_row(32.2) - t0
        ang = math.radians(sx * 36.0)
        d = (normal_up * math.cos(ang) + side_axis * math.sin(ang)).normalized()
        p = start + AXIS * tt + d * 8.3
        frame = w.rounded_box(f"vent_frame{sx}", (0, 0, 0), (4.0, 5.0, 1.2), red[6], bevel=0.35, segments=1)
        frame.data.transform(_frame_matrix(p, d))
        glow = w.rounded_box(f"vent{sx}", (0, 0, 0.35), (2.8, 3.6, 1.0), vent, bevel=0.3, segments=1)
        glow.data.transform(_frame_matrix(p, d))
        core = w.sphere(f"vent_core{sx}", (0, 0, 0.75), (0.9, 1.3, 0.4), vent_core, 10, 5)
        core.data.transform(_frame_matrix(p, d))

    # The red lamps under the bulbs, facing the camera, and the bulbs' red shoulders.
    for row in (52.0, 75.0):
        tt = t_of_row(row) - t0
        p = start + AXIS * tt + normal_up * 7.9
        lamp = w.rounded_box(f"lamp{row}", (0, 0, 0), (3.6, 3.0, 1.4), red[9], bevel=0.45)
        lamp.data.transform(_frame_matrix(p, normal_up))
    for sx in (-1, 1):
        tt = t_of_row(42.6) - t0
        ang = math.radians(sx * 55.0)
        d = (normal_up * math.cos(ang) + side_axis * math.sin(ang)).normalized()
        w.sphere(f"shoulder{sx}", start + AXIS * tt + d * 7.9, (2.6, 2.6, 1.6), red[8], 14, 8)
    # The shaft's ribs: thin rings round it.
    for row in (57.0, 60.0, 63.0):
        tt = t_of_row(row) - t0
        w.lathe_axis(f"rib{row}", [(-0.35, 6.55), (-0.2, 6.95), (0.2, 6.95), (0.35, 6.55)], grey[9], start + AXIS * tt,
                     AXIS, 32)
    # The base's red door on its left.
    tt = t_of_row(89.0) - t0
    ang = math.radians(-50.0)
    d = (normal_up * math.cos(ang) + side_axis * math.sin(ang)).normalized()
    door = w.rounded_box("door", (0, 0, 0), (5.8, 6.8, 1.4), red[7], bevel=0.5)
    door.data.transform(_frame_matrix(start + AXIS * tt + d * 8.9, d))
    w.paint_faces(door, lambda c, n: red[8] if n.z > 0.6 else red[5])
    # The skirt's seams: dark ribs along it, dividing it into panels.
    for ang in (-62.0, -22.0, 22.0, 62.0):
        a = math.radians(ang)
        d = (normal_up * math.cos(a) + side_axis * math.sin(a)).normalized()
        pts = [start + AXIS * (t_of_row(r) - t0) + d * (rad + 0.05) for r, rad in ((19.6, 8.4), (18.0, 9.1), (12.4, 9.1))]
        w.tube(f"seam{ang:.0f}", pts, 0.42, red[4], 6)
    # The dome's rim over the skirt.
    w.lathe_axis("dome_rim", [(-0.45, 9.0), (-0.3, 9.45), (0.3, 9.45), (0.45, 9.0)], grey[9],
                 start + AXIS * (t_of_row(11.8) - t0), AXIS, 36)


def _frame_matrix(p, normal):
    """A matrix putting a part made round the origin (its top facing +z) at p, its top facing `normal`, its
    y along the tower's axis."""
    from mathutils import Matrix
    n = normal.normalized()
    yv = (AXIS - n * AXIS.dot(n)).normalized()
    xv = yv.cross(n).normalized()
    return Matrix(((xv.x, yv.x, n.x, p.x), (xv.y, yv.y, n.y, p.y), (xv.z, yv.z, n.z, p.z), (0, 0, 0, 1)))


x.whole("tower", (24, 112))(tower_whole)

TOWER_PIECES = [("red_tower_head", 77, 42.0), ("red_tower_vents", 115, 14.0), ("red_tower_shaft", 17, -14.0),
                ("red_tower_base", 55, -42.0)]


def tower_piece(cy):
    tower_whole()
    x.bake()
    sh.flat_bottom([o for o in x.meshes() if not o.name.startswith("tiles")])
    x.cut(x.meshes(), (-12.0, 12.0, cy - 14.0, cy + 14.0), (0.0, cy))
    x.drop_slivers()
    x.budget(4800)
    x.report()


for _name, _sprite, _cy in TOWER_PIECES:
    x.model(_name, [(_sprite, True)])(lambda cy=_cy: tower_piece(cy))


# --- C 245 above 283: the gun on the mast over the ball --------------------------------------------------

MAST_ORIGIN = (12, 28)            # the whole art: 24 x 56, its centre between 245 and 283
BALL = Vector((0.0, -10.0, 4.0))  # the ball's centre (rows 28-47, cols 3-20), sunk into the floor
BALL_R = (9.0, 9.6, 9.0)


def category_map(g):
    """Each pixel's ramp and shade, smoothed: the most common ramp among the pixel and its eight neighbours,
    and the mean shade of those of that ramp (fewer stray pixels for painting)."""
    out = [[None] * len(row) for row in g]
    for r, row in enumerate(g):
        for c, v in enumerate(row):
            if v is None:
                continue
            votes = {}
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    n = x.at(g, c + dc, r + dr)
                    if n is None or (n >> 4 == 0 and n & 15 <= 1):
                        continue
                    votes.setdefault(n >> 4, []).append(n & 15)
            if not votes:
                out[r][c] = (v >> 4, v & 15)
                continue
            ramp = max(votes, key=lambda key: (len(votes[key]), key == v >> 4))
            out[r][c] = (ramp, sum(votes[ramp]) / len(votes[ramp]))
    return out


def mast_whole():
    """The ball on the floor tiles, the mast rising from it up the screen through the yoke to the gun, the
    gun's pale stem, its body pointing left, and the blue fin curving down from its back."""
    g = x.grid(art.MAST, 24)
    origin = MAST_ORIGIN
    cat = category_map(g)
    grey = {s: pal(f"bm_grey{s}", s, metallic=0.5, roughness=0.35) for s in range(2, 13)}
    blue = {s: pal(f"bm_blue{s}", 0x30 | s, metallic=0.5, roughness=0.3) for s in range(3, 13)}
    pale = {s: pal(f"bm_pale{s}", 0x80 | s, metallic=0.45, roughness=0.3) for s in range(0, 10)}
    dark = pal("bm_dark", 0x01, metallic=0.3, roughness=0.6)

    # The floor round the ball, its shadow given the floor's shades; under the ball filled.
    floorish = lambda v, c, r: r >= 28 and (v >> 4 == 6 or r >= 47)
    shadow = lambda v, c, r: v >> 4 != 6 or (v & 15 <= 2 and (c >= 16 or r >= 45))
    fg = x.floor_grid(g, floorish, shadow, seed=8)
    for r in range(28, 56):
        for c in range(24):
            if fg[r][c] is None:
                fg[r][c] = 0x64
    x.floor_bed("tiles", fg, origin, top=0.35, prefix="bm_floor")

    def by_sprite(c, n, side_shade=4):
        """The sprite's (smoothed) colour under a face facing up; faces facing sideways darker."""
        col, row = int(math.floor(c.x + origin[0])), int(math.floor(origin[1] - c.y))
        k_ = x.at(cat, col, row)
        if k_ is None:
            return grey[side_shade]
        ramp, s_ = k_
        if n.z < 0.3:
            s_ -= 2
        s_ = int(round(s_))
        if ramp == 3:
            return blue[max(3, min(12, s_ + 1))]
        if ramp == 8:
            return pale[max(0, min(9, s_))]
        if ramp == 6:
            return blue[max(3, min(12, s_))]
        return grey[max(2, min(12, s_ + 1))]

    # The ball.
    ball = w.sphere("ball", BALL, BALL_R, grey[7], 36, 18)

    def paint_ball(c, n):
        dx, dy = c.x - BALL.x, c.y - BALL.y
        side = n.z < 0.3
        if abs(dx) < 1.9:
            return blue[7] if side else blue[9]
        if 1.2 < dy < 3.6:
            return pale[4] if side else pale[6]
        if dy < -0.6:
            if dx < 0 and dy > -7.5:
                return blue[6] if side else blue[8]
            return grey[5] if side else grey[7]
        if dy > 5.5 and abs(dx) > 3.5:
            return pale[3] if side else pale[5]
        return grey[6] if side else grey[9]
    w.paint_faces(ball, paint_ball)
    # The seam round the ball's middle.
    x.torus("ball_seam", (BALL.x, BALL.y - 0.6, BALL.z), 9.0, 0.45, grey[4], 40, 6, scale_y=BALL_R[1] / BALL_R[0])
    # The collar where the mast leaves the ball.
    top = BALL + Vector((0.3, 4.6, 7.4))
    up = Vector((0.0, 0.55, 0.83)).normalized()
    w.lathe_axis("collar", [(-0.8, 2.9), (0.0, 3.1), (0.7, 2.6), (1.1, 1.8)], grey[8], top, up, 24)

    # The mast: a blue rod from the ball up the screen to the yoke.
    a, b = top + up * 0.6, Vector((0.5, 6.0, 15.0))
    w.tube("mast", [a, (a + b) / 2, b], 1.8, blue[8], 14)
    w.tube("mast_line", [a + Vector((0.7, 0, 1.45)), b + Vector((0.7, 0, 1.45))], 0.4, pale[6], 6)

    # The yoke: a grey crescent cradling the stem, open up the screen.
    yc = Vector((0.6, 9.4, 16.0))
    lean = Vector((0.0, 0.9, 0.44)).normalized()
    pts = []
    for i in range(13):
        ang = math.radians(195 + 150 * i / 12)
        pts.append(yc + Vector((1, 0, 0)) * (3.6 * math.cos(ang)) + lean * (3.4 * math.sin(ang)))
    yoke = w.tube("yoke", pts, [0.9 + 0.5 * math.sin(math.pi * i / 12) for i in range(13)], grey[8], 12)
    w.paint_faces(yoke, lambda c, n: grey[10] if n.z > 0.7 else grey[5] if n.z < 0.2 else None)
    for sx in (-1, 1):
        w.sphere(f"yoke_end{sx}", pts[0 if sx < 0 else -1], (1.0, 1.0, 1.0), grey[9], 10, 6)

    # The pivot between the yoke and the gun: a grey neck from the yoke's middle up to the gun's underside.
    w.sphere("pivot_ball", (0.6, 9.6, 16.2), (2.5, 2.5, 2.4), grey[4], 16, 8)
    # The housing under the gun: a dark block from the grip to the fin, sloping down the screen.
    housing = w.rounded_box("housing", (0, 0, 0), (10.4, 7.0, 3.2), grey[4], bevel=1.0)
    from mathutils import Matrix
    housing.data.transform(Matrix.Translation((-1.0, 16.0, 15.6)) @ Matrix.Rotation(math.radians(-22.0), 4, "X"))
    w.paint_faces(housing, lambda c, n: grey[6] if n.z > 0.8 else grey[3])

    # The gun: a grey body along x pointing left, rounded at the muzzle, a pale window on top, the barrel.
    gz, gy = 19.2, 22.6
    secs = [(-11.2, gy, gz, 1.2, 1.4, 1.4), (-10.6, gy, gz, 2.2, 2.2, 2.2), (-9.2, gy, gz, 2.6, 2.7, 2.6),
            (2.4, gy - 0.3, gz, 2.9, 2.9, 2.6), (4.4, gy - 0.6, gz, 2.7, 2.7, 2.5), (5.2, gy - 0.6, gz, 2.0, 2.0, 2.0)]
    body = x.t.loft_x("gun", secs, grey[8], segments=28, power=3.0)
    w.paint_faces(body, lambda c, n: grey[10] if n.z > 0.85 else grey[8] if n.z > 0.4 else
                  grey[4] if n.y < -0.3 else grey[6])
    w.rounded_box("window", (-2.0, gy + 0.3, gz + 2.75), (6.4, 2.0, 0.6), pale[6], bevel=0.25, segments=1)
    w.lathe_axis("barrel", [(0.0, 1.0), (0.8, 1.0), (1.0, 1.3), (1.5, 1.3), (1.6, 0.6)], grey[9],
                 (-10.6, gy - 0.6, gz - 0.2), (-1, 0, 0), 14)
    w.lathe_axis("bore", [(0.0, 0.6), (0.3, 0.6), (0.31, 0.01)], dark, (-12.15, gy - 0.6, gz - 0.2), (-1, 0, 0), 10)
    # The grip under the gun's left half: a pale blue block hanging down the screen.
    grip = x.loft_axis("grip", [(0.0, 2.8, 1.3), (2.0, 2.8, 1.4), (6.4, 2.5, 1.3), (7.4, 1.8, 1.0)], pale[5],
                       (-6.0, 20.6, 19.4), (0.05, -0.93, -0.36), power=3.0, segments=20)
    w.paint_faces(grip, lambda c, n: pale[8] if n.z > 0.8 else pale[3] if n.z < 0.2 else None)
    # Seams round the body.
    for sx in (-7.6, 1.2):
        w.lathe_axis(f"gun_band{sx}", [(-0.3, 2.75), (-0.15, 3.0), (0.15, 3.0), (0.3, 2.75)], grey[5],
                     (sx, gy, gz), (1, 0, 0), 24, squash=0.95)

    # The fin: a blue blade curving down from the gun's back towards the ball, narrowing as it goes.
    path = [Vector((5.0, 21.2, 18.6)), Vector((5.7, 16.0, 17.8)), Vector((6.6, 10.0, 16.0)), Vector((7.3, 5.0, 14.0)),
            Vector((7.6, 1.6, 12.2))]
    path = x.catmull(path, 0.8)
    rings = []
    count = len(path)
    for i, p in enumerate(path):
        f = i / (count - 1)
        hw = 3.3 * (1 - f) + 1.1 * f
        hz = 1.0 * (1 - f) + 0.7 * f
        tangent = (path[min(i + 1, count - 1)] - path[max(i - 1, 0)]).normalized()
        side = tangent.cross(Vector((0, 0, 1))).normalized()
        upv = side.cross(tangent).normalized()
        ring = []
        for j in range(16):
            a = 2 * math.pi * j / 16
            cc, ss = math.cos(a), math.sin(a)
            ring.append(p + side * (math.copysign(abs(cc) ** 0.6, cc) * hw) + upv * (math.copysign(abs(ss) ** 0.6, ss) * hz))
        rings.append(ring)
    fin = k.loft("fin", rings, blue[8])
    k.smooth(fin, 45)
    w.paint_faces(fin, lambda c, n: pale[5] if n.z > 0.6 and c.x < 6.5 - 0.1 * (20 - c.y) * 0.1 else
                  blue[9] if n.z > 0.6 else blue[5])


x.whole("mast", (24, 56))(mast_whole)


def mast_piece(cy):
    mast_whole()
    x.bake()
    sh.flat_bottom([o for o in x.meshes() if not o.name.startswith("tiles")])
    x.cut(x.meshes(), (-12.0, 12.0, cy - 14.0, cy + 14.0), (0.0, cy))
    x.drop_slivers()
    x.budget(4800)
    x.report()


for _name, _sprite, _cy in (("ball_mast_gun", 245, 14.0), ("ball_mast_ball", 283, -14.0)):
    x.model(_name, [(_sprite, True)])(lambda cy=_cy: mast_piece(cy))


if __name__ == "__main__":
    x.run()
