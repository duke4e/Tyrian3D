"""Panel with gems (sheet D sprite 127, 2x2: 24 x 28 pixels; ASTEROID1, ASTEROID2, ASTEROID?), as
the sprite draws it (models.cfg: yaw=0). The animation (127, 129, 131) only brightens the gems.

A square stone tile filling the whole sprite: a low bevelled slab of stone blocks carrying a raised
round grey stone disc (the sprite's columns 0-23, rows 4-24, centred on row 14) carved into four
cushions by a raised cross. The cross's upright arm (columns 8-15, rows 5-22) stands highest and
holds two red gems one above the other (columns 10-13 of rows 9-12 and 15-18), diamond-cut and
set in dark bezels, joined by a fine groove; its cross arm (rows 12-15) runs the disc's width a
little lower. Origin at the sprite's centre (pixel 12, 14).

Polish (2026-10-18): replaces later_episodes.py's panel_gems (a dark disc without the tile).
"""
import math
import os
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import tyrkit as k  # noqa: E402

TILE = (12.0, 14.0)                  # the slab's half-width and half-depth: the whole sprite
SLAB_HEIGHT, SLAB_BEVEL = 1.4, 0.4
SEAMS_X = (-8.5, 7.5)                # the joints between the slab's stones (the sprite's columns 3, 19)
SEAMS_Y = (9.6, -10.6)               # (rows 4, 24)
JOINT = 0.16                         # half the gap between two stones

DISC_CENTRE = (0.0, -0.5)            # the disc: its middle and radii (to the sprite's outline)
DISC_RADII = (11.4, 9.9)
# The disc's profile from its foot to its flat top: (fraction of the radii, height).
DISC = [(1.0, SLAB_HEIGHT - 0.3), (1.0, SLAB_HEIGHT + 0.25), (0.996, 2.2), (0.985, 2.8), (0.965, 3.22),
        (0.94, 3.48), (0.91, 3.62), (0.89, 3.65)]
DISC_TOP = 3.65
TOP_EDGE = 0.89                      # the flat top's edge (fraction of the radii)

UPRIGHT = 3.9                        # the cross: the upright arm's half-width (columns 8-15)
ARM = (0.0, 2.0)                     # the cross arm's middle (y) and half-depth (rows 12-15)
UPRIGHT_TOP, ARM_TOP, CUSHION_TOP = 5.05, 4.6, 4.4
GROOVE = 0.45                        # the gap between the cross and the cushions
CAP_FROM = 5.6                       # the block on the upright's top end, from this y up

GEMS = (3.0, -3.0)                   # the gems' middles (y) on the upright arm
GEM_RADIUS, BEZEL_RADIUS = 1.75, 2.3


def offset(outline, d):
    """The polygon `outline` (counter-clockwise) moved d inwards, each corner along its bisector."""
    n = len(outline)
    out = []
    for i in range(n):
        p0, p1, p2 = outline[i - 1], outline[i], outline[(i + 1) % n]
        e1, e2 = (p1 - p0).normalized(), (p2 - p1).normalized()
        n1, n2 = Vector((-e1.y, e1.x)), Vector((-e2.y, e2.x))
        nv = (n1 + n2).normalized()
        out.append(p1 + nv * d / max(0.3, nv.dot(n1)))
    return out


def round_corners(outline, radius, steps=4, min_turn=20.0):
    """The polygon with its sharp corners (turning more than min_turn degrees) rounded: each
    replaced by a curve tangent to both its edges (a quadratic Bezier through the corner)."""
    n = len(outline)
    out = []
    for i in range(n):
        prev, p, nxt = outline[i - 1], outline[i], outline[(i + 1) % n]
        d1, d2 = p - prev, nxt - p
        turn = d1.angle(d2, 0.0)
        if math.degrees(turn) < min_turn:
            out.append(p)
            continue
        t = min(radius * math.tan(turn / 2), 0.45 * d1.length, 0.45 * d2.length)
        a, b = p - d1.normalized() * t, p + d2.normalized() * t
        for j in range(steps + 1):
            u = j / steps
            out.append(a * (1 - u) ** 2 + p * 2 * (1 - u) * u + b * u * u)
    return out


def prism(name, outline, z0, z1, radius, mat, steps=3, dome=0.0, centre=None):
    """A raised part: the polygon `outline` (counter-clockwise, every point seen from its centre)
    standing from z0 to z1, its top edge rounded by `radius`, its top bulging by `dome`."""
    centre = centre or sum(outline, Vector((0, 0))) / len(outline)
    rings = [[Vector((p.x, p.y, z0)) for p in outline], [Vector((p.x, p.y, z1 - radius)) for p in outline]]
    for i in range(1, steps + 1):
        a = (math.pi / 2) * i / steps
        rings.append([Vector((p.x, p.y, z1 - radius + radius * math.sin(a)))
                      for p in offset(outline, radius * (1 - math.cos(a)))])
    if dome > 0:  # rings part way in, so the bulge is round rather than a cone
        edge = offset(outline, radius)
        for f in (0.8, 0.6, 0.4, 0.2):
            rings.append([Vector((q.x, q.y, z1 + dome * (1 - f * f))) for q in (centre.lerp(p, f) for p in edge)])
    return k.loft(name, rings, mat, start_point=(centre.x, centre.y, z0), end_point=(centre.x, centre.y, z1 + dome))


def ellipse_point(t, scale):
    return Vector((DISC_CENTRE[0] + DISC_RADII[0] * scale * math.cos(t),
                   DISC_CENTRE[1] + DISC_RADII[1] * scale * math.sin(t)))


def on_ellipse_x(x, scale, upper):
    """The point of the ellipse (scaled) above (upper) or below the middle at x."""
    a, b = DISC_RADII[0] * scale, DISC_RADII[1] * scale
    dy = b * math.sqrt(max(0.0, 1 - ((x - DISC_CENTRE[0]) / a) ** 2))
    return Vector((x, DISC_CENTRE[1] + (dy if upper else -dy)))


def on_ellipse_y(y, scale, right):
    a, b = DISC_RADII[0] * scale, DISC_RADII[1] * scale
    dx = a * math.sqrt(max(0.0, 1 - ((y - DISC_CENTRE[1]) / b) ** 2))
    return Vector((DISC_CENTRE[0] + (dx if right else -dx), y))


def angle_of(p):
    return math.atan2((p.y - DISC_CENTRE[1]) / DISC_RADII[1], (p.x - DISC_CENTRE[0]) / DISC_RADII[0])


def arc(p0, p1, scale, step=0.12):
    """Points along the ellipse (scaled) from p0 to p1 counter-clockwise (both on it), ends excluded."""
    t0, t1 = angle_of(p0), angle_of(p1)
    while t1 <= t0:
        t1 += 2 * math.pi
    count = max(1, int((t1 - t0) / step))
    return [ellipse_point(t0 + (t1 - t0) * i / count, scale) for i in range(1, count)]


def rounded_rect(hw, hd, r, corner_steps=4):
    """A rectangle with rounded corners, counter-clockwise from its bottom right."""
    points = []
    for cx, cy, a0 in ((hw - r, -hd + r, -90), (hw - r, hd - r, 0), (-hw + r, hd - r, 90), (-hw + r, -hd + r, 180)):
        for i in range(corner_steps + 1):
            a = math.radians(a0 + 90 * i / corner_steps)
            points.append(Vector((cx + r * math.cos(a), cy + r * math.sin(a))))
    return points


def gem(name, x, y, z, radius, mat):
    """A diamond-cut gem (a square turned 45 degrees in plan): a girdle at z, a crown of eight facets
    up to a table, a pavilion below."""
    girdle, table = [], []
    for i in range(8):
        a = math.radians(45 * i)
        r = radius if i % 2 == 0 else radius * math.cos(math.radians(45))
        girdle.append((x + r * math.cos(a), y + r * math.sin(a), z))
        table.append((x + 0.38 * r * math.cos(a), y + 0.38 * r * math.sin(a), z + 0.72 * radius))
    vertices = girdle + table + [(x, y, z - 0.6 * radius)]
    faces = [(i, (i + 1) % 8, 8 + (i + 1) % 8, 8 + i) for i in range(8)]
    faces.append(tuple(range(8, 16)))
    faces += [((i + 1) % 8, i, 16) for i in range(8)]
    obj = k.mesh_object(name, vertices, faces, mat)
    k.recalc_normals(obj)
    return obj


def build():
    k.reset()
    stones = [k.material("gems_slab", palette=index, metallic=0.0, roughness=0.85) for index in (5, 6, 7)]
    joint = k.material("gems_joint", palette=2, metallic=0.0, roughness=0.9)
    disc_mat = k.material("gems_disc", palette=6, metallic=0.05, roughness=0.75)
    cushion_mat = k.material("gems_cushion", palette=9, metallic=0.05, roughness=0.7)
    cross_mat = k.material("gems_cross", palette=11, metallic=0.05, roughness=0.6)
    bezel = k.material("gems_bezel", palette=112, metallic=0.3, roughness=0.4)
    red = k.material("gems_red", palette=118, metallic=0.1, roughness=0.08, emission=(255, 50, 6),
                     emission_strength=0.9)

    # The slab: nine bevelled stones on a dark bed filling the tile, the joints between them
    # (the sprite's floor lines) dark gaps.
    k.box("bed", (0, 0, 0.35), (2 * TILE[0] - 0.2, 2 * TILE[1] - 0.2, 0.7), joint)
    xs = (-TILE[0], *SEAMS_X, TILE[0])
    ys = (-TILE[1], *sorted(SEAMS_Y), TILE[1])
    for i in range(3):
        for j in range(3):
            x0 = xs[i] + (JOINT if i > 0 else 0.0)
            x1 = xs[i + 1] - (JOINT if i < 2 else 0.0)
            y0 = ys[j] + (JOINT if j > 0 else 0.0)
            y1 = ys[j + 1] - (JOINT if j < 2 else 0.0)
            outline = [p + Vector(((x0 + x1) / 2, (y0 + y1) / 2)) for p in rounded_rect((x1 - x0) / 2, (y1 - y0) / 2, 0.3, 2)]
            uneven = (i * 7 + j * 3) % 3  # the stones a little uneven in height and shade
            stone_height = SLAB_HEIGHT - 0.12 * uneven
            k.smooth(prism(f"stone{i}{j}", outline, 0.0, stone_height, SLAB_BEVEL, stones[(uneven + i) % 3], steps=2,
                           centre=Vector(((x0 + x1) / 2, (y0 + y1) / 2))), 40)

    # The disc: a round boss with a rounded edge and a flat top.
    rings = []
    for scale, z in DISC:
        rings.append([Vector((*ellipse_point(2 * math.pi * i / 64, scale), z)) for i in range(64)])
    disc = k.loft("disc", rings, disc_mat, start_point=(*DISC_CENTRE, SLAB_HEIGHT - 0.3), end_point=(*DISC_CENTRE, DISC_TOP))
    k.smooth(disc, 40)
    # A dark crevice round its foot, where it stands in the slab (the sprite's dark outline).
    foot = [[Vector((*ellipse_point(2 * math.pi * i / 64, scale), z)) for i in range(64)]
            for scale, z in ((0.99, SLAB_HEIGHT + 0.12), (1.035, SLAB_HEIGHT + 0.06), (1.06, SLAB_HEIGHT - 0.1))]
    k.smooth(k.loft("crevice", foot, joint, cap_start=False, cap_end=False), 40)

    # The cross: the upright arm and the cross arm, ending at the edge of the disc's flat top.
    edge = TOP_EDGE - 0.02
    bottom, top = on_ellipse_x(-UPRIGHT, edge, False), on_ellipse_x(UPRIGHT, edge, True)
    upright = ([bottom] + arc(bottom, on_ellipse_x(UPRIGHT, edge, False), edge) + [on_ellipse_x(UPRIGHT, edge, False),
               top] + arc(top, on_ellipse_x(-UPRIGHT, edge, True), edge) + [on_ellipse_x(-UPRIGHT, edge, True)])
    upright = round_corners(upright, 0.5, 2)
    k.smooth(prism("upright", upright, DISC_TOP - 0.3, UPRIGHT_TOP, 0.45, cross_mat, centre=Vector((0, ARM[0]))), 40)
    # The block capping the upright's top end (the sprite's brightest pixels, rows 5-8).
    cap_bottom = Vector((UPRIGHT - 0.25, CAP_FROM))
    cap = [Vector((-UPRIGHT + 0.25, CAP_FROM)), cap_bottom]
    cap += [p for p in upright if p.y > CAP_FROM + 0.3 and abs(p.x) < UPRIGHT - 0.25]
    cap = sorted(cap, key=lambda p: math.atan2(p.y - (CAP_FROM + 1.0), p.x))
    cap = round_corners(cap, 0.4, 2)
    k.smooth(prism("cap", cap, UPRIGHT_TOP - 0.3, UPRIGHT_TOP + 0.35, 0.3, cross_mat, steps=2,
                   centre=Vector((0, CAP_FROM + 1.0))), 40)

    y0, y1 = ARM[0] - ARM[1], ARM[0] + ARM[1]
    right0, right1, left1, left0 = (on_ellipse_y(y0, edge, True), on_ellipse_y(y1, edge, True),
                                    on_ellipse_y(y1, edge, False), on_ellipse_y(y0, edge, False))
    arm = [right0] + arc(right0, right1, edge) + [right1, left1] + arc(left1, left0, edge) + [left0]
    arm = round_corners(arm, 0.5, 2)
    k.smooth(prism("arm", arm, DISC_TOP - 0.3, ARM_TOP, 0.4, cross_mat, centre=Vector((0, ARM[0]))), 40)

    # The four cushions between the arms.
    inner_x, inner_y = UPRIGHT + GROOVE, ARM[1] + GROOVE
    rim = TOP_EDGE - 0.03
    for sx in (1, -1):
        for sy in (1, -1):
            corner = Vector((sx * inner_x, ARM[0] + sy * inner_y))
            along_arm = on_ellipse_y(corner.y, rim, sx > 0)       # where the cross arm's side meets the rim
            along_upright = on_ellipse_x(corner.x, rim, sy > 0)   # where the upright's side meets the rim
            if sx * sy > 0:   # counter-clockwise: corner, along the arm, round the rim, back down the upright
                pad = [corner, along_arm] + arc(along_arm, along_upright, rim) + [along_upright]
            else:
                pad = [corner, along_upright] + arc(along_upright, along_arm, rim) + [along_arm]
            middle = sum(pad, Vector((0, 0))) / len(pad)
            pad = round_corners(pad, 1.1, 4)
            k.smooth(prism(f"cushion{sx}{sy}", pad, DISC_TOP - 0.3, CUSHION_TOP, 0.8, cushion_mat, steps=4, dome=0.3,
                           centre=middle), 60)

    # The gems in their bezels on the upright arm, a fine groove between them.
    for i, y in enumerate(GEMS):
        diamond = [Vector((BEZEL_RADIUS * math.cos(math.radians(a)), y + BEZEL_RADIUS * math.sin(math.radians(a))))
                   for a in range(-90, 270, 90)]
        k.smooth(prism(f"bezel{i}", diamond, UPRIGHT_TOP - 0.3, UPRIGHT_TOP + 0.3, 0.12, bezel, steps=1,
                       centre=Vector((0, y))), 30)
        gem(f"gem{i}", 0.0, y, UPRIGHT_TOP + 0.3, GEM_RADIUS, red)
    k.box("groove", (0, 0, UPRIGHT_TOP), (0.3, GEMS[0] - GEMS[1] - 2 * BEZEL_RADIUS + 0.6, 0.12), joint)

    print("triangles:", triangles())
    here = os.path.dirname(os.path.abspath(__file__))
    k.finish(os.path.join(here, "..", "..", "..", "..", "assets", "models", "enemies", "panel_gems.glb"))


def triangles():
    depsgraph = bpy.context.evaluated_depsgraph_get()
    total = 0
    for obj in bpy.context.scene.objects:
        if obj.type == "MESH":
            evaluated = obj.evaluated_get(depsgraph)
            mesh = evaluated.to_mesh()
            mesh.calc_loop_triangles()
            total += len(mesh.loop_triangles)
            evaluated.to_mesh_clear()
    return total


build()
