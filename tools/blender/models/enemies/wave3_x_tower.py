"""Batch X of wave 3 (sheet C): DELI's and New Deli's tall objects, which the level events place as sprites
one above the other (C 77 above 115 above 17 above 55), modelled whole as their sprites
look (models.cfg: yaw=0) and cut into the sprites' pieces, drawn at their own origins (origin) so they meet.
It stands on the ground layer; the sprites draw them as tall towers seen from the side, so the models lean
up the screen from their foot on the floor (as the green tower of wave3_m.py does), their tops high above it.

- red_tower_head, red_tower_vents, red_tower_shaft, red_tower_base (C 77, 115, 17, 55): the grey tower with
  the salmon red bands: a round base on the floor tiles with a red door on its left, two bulging sections on
  a ribbed shaft (red plates on their shoulders and a red lamp under each), a crown with two vents in it
  (the frames 117-127 make them glow: they glow throughout) and at the top a dome with a dark gun port in it
  and a red skirt round it (the frames 79-89 tilt the dome towards the player; the model keeps the first).
(The gun on the mast over the ball, C 245 above 283: polish_ball_mast.py.)

usage: Blender -b --factory-startup -P wave3_x_tower.py -- [--only name,name] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1] [--whole tower --preview <prefix>]
"""
import math
import os
import sys

from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_x_kit as x  # noqa: E402
from wave3_x_kit import art, sh, w, pal  # noqa: E402


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


if __name__ == "__main__":
    x.run()
