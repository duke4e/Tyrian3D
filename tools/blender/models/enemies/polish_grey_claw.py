"""The grey steel claw of GRYPHON, MISTAKES and STATION, drawn from two sprites of sheet V (2x2 each,
24 x 28 pixels; custom enemies, events 50, 52 and 49: sky in GRYPHON and MISTAKES, ground and ground2
in STATION), polished (2026-10-19). The levels place the left claw as V 44 at x and V 46 at x + 24 on
one row (GRYPHON's events at 1200, 1260, 1320 ...: graphic 44 at x -60, 46 at x -36, one link; it
flies in from the screen's left), the right claw as V 85 at x and V 87 at x + 24 (from the right;
pixel for pixel the left claw's mirror image), and each pair moves together. models.cfg: model
claw_body_l / claw_hook_l / claw_hook_r / claw_body_r ... origin; sprite v 44 claw_body_l yaw=0,
sprite v 46 claw_hook_l yaw=0, sprite v 85 claw_hook_r yaw=0, sprite v 87 claw_body_r yaw=0. None of
the four is animated, and no other enemy uses them.

V 44 is the left block of the blue bridge of GEM WAR, GRYPHON and STATION (V 89, polish_arm_bridge.py)
pixel for pixel in grey steel (the sprite's ramp 6 for the bridge's ramp 3), but for the seam ridge,
which here runs over the deck only (V 89's column 15 is light down the slope as well), and for the
ball, which glows: red with an orange-yellow hot spot (ramp 7) where V 89's is dull brown. V 46's
first columns are V 91's: the block's shoulder and inner face with the red lamp low on it (columns
0-1 of rows 19-20), the glossy hump rising out of a dark core (rows 7-13), the light ledge in front of
it (rows 13-14), the vent with its red slats between grey posts (row 15; three slats here, the
bridge's posts at columns 9 and 12) and the lip below (rows 16-17) with an emitter under it (column 7
of row 18). Where the bridge goes on to the right block, the claw's hump ends in a hook: its end
bevelled off (the outline's 45-degree run over columns 18-21 of rows 10-13) and curling down the screen
into a broad blunt talon (columns 15-22 of rows 13-19), lit down its front, its point low above the
ground.

So the claw is built from the bridge's own parts: polish_arm_bridge.block() makes the block (housing,
jaw, ball in its collar, the fins in their pocket, the deck's trim, the lamp) in the bridge's
coordinates, its ridge cut back to the deck; the core, the ledge, the vent, the lip and the emitter
are the bridge's (its constants), cut short; the hump and its hook are new: a tube following the
hump's line and curling down and forward, intersected with the hook's plan (the sprite's outline) and
softened like the block's steel (polish_machine_kit.soften), two dark grooves round it where it starts
to curl and across the talon, so that it reads as a jointed finger. The materials are the bridge's in
grey; the ball and the lamps glow (emission), a round orange-yellow lens on the ball for its hot spot.

The claw is built whole in the bridge's coordinates (V 44 over x -36..-12, V 46 over -12..12; 1 unit =
1 game pixel, +X right, +Y up the screen, +Z towards the camera, the base on z = 0) and cut along the
sprites' edge (polish_redjet.py's method: the pieces keep the whole's shading across the cut), each
piece moved so that its sprite's centre is its origin. The right claw is built mirrored (the bridge's
right block, the arm mirrored about x = 0) and moved 24 to the left, so that its pieces lie in the
same boxes: V 85 (the hook) over -36..-12, V 87 (the body) over -12..12.

Replaces wave3_t.py's claw (claw_whole(), claw_preview(), claw_piece() and the claw_body_l /
claw_hook_l / claw_hook_r / claw_body_r models): remove them so that they don't overwrite these
models (wave3_t_art.py's CLAW, which nothing reads, can go too).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the
silhouettes of the whole and of each piece against enemy_V.png), --preview <prefix> (each piece's top
and 3/4 view and the whole's), --only <name,...> (which of the four models to export).
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_arm_bridge as ab  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402

# name, sprite, the box it covers (x0, x1, y0, y1), its sprite's centre x; the right claw is moved by
# RIGHT_SHIFT after it is built.
LEFT = [("claw_body_l", 44, (-36.0, -12.0, -20.0, 20.0), -24.0), ("claw_hook_l", 46, (-12.0, 12.0, -20.0, 20.0), 0.0)]
RIGHT = [("claw_hook_r", 85, (-36.0, -12.0, -20.0, 20.0), -24.0), ("claw_body_r", 87, (-12.0, 12.0, -20.0, 20.0), 0.0)]
RIGHT_SHIFT = -24.0

# --- The arm (V 46; the left claw's, mirrored for the right one) ------------------------------------
# The hump's line: (x, y, z, half-width, half-height): along the bridge's saddle (axis y 3.05, z 6.05)
# from inside the shoulder, then curling down the screen and towards the ground into the talon, which
# flattens towards its blunt point (END_ROUND long, its end rounded like a superellipse of END_POWER).
HUMP = [(-8.4, 3.05, 6.05, 3.62, 3.6), (-2.0, 3.05, 6.05, 3.62, 3.6), (1.0, 3.0, 6.0, 3.62, 3.5),
        (3.4, 2.6, 5.85, 3.75, 3.3), (5.4, 1.4, 5.4, 3.9, 3.0), (6.6, -0.4, 4.7, 3.9, 2.6),
        (7.0, -2.4, 3.8, 3.6, 2.25), (7.0, -4.2, 2.95, 3.55, 1.9), (6.95, -5.3, 2.4, 3.35, 1.6)]
END_ROUND, END_POWER = 1.5, 2.6
KNUCKLES = (3.0, 5.6)  # the grooves round it: stations along HUMP (where it starts to curl, across the talon)
# The hook's plan (the sprite's outline two thirds covered): the top edge along row 7 (left uncut: the
# hump's own edge), stepping down over columns 13-17 and the bevel over columns 18-21 to the talon's
# outer side (column 22); the talon's sides and its point are the tube's own. Then back under the hump, behind
# the vent and the lip.
ARM_PLAN = [(-9.0, -1.2), (2.6, -1.2), (2.3, -4.0), (2.0, -9.0), (12.5, -9.0), (12.5, -2.6), (10.66, -1.9),
            (10.25, -1.15), (9.7, -0.6), (9.66, 0.55), (8.5, 1.7), (7.5, 2.7), (6.5, 3.7), (5.5, 4.65), (4.4, 5.05),
            (3.0, 5.6), (1.6, 5.72), (1.1, 5.85), (0.95, 6.7), (0.6, 7.4), (-9.0, 7.4)]
# The bridge's parts in front of the hump, cut short: the core's, the ledge's and the lip's right ends,
# the vent's span and its posts (V 46's columns 7-14 of row 15: dark ends, slats at 8, 10-11, 13).
CORE_X1 = 3.0
LEDGE_X = (-10.4, 4.6)
VENT_X = (-4.45, 2.45)
VENT_POSTS = (-4.55, -2.5, 0.5, 2.55)
LIP_X1 = 4.3
FANG_X = -4.5               # the emitter under the lip (column 7 of row 18)
# The ridge over the deck only (V 44's column 15, rows 5-13).
RIDGE_Y = (9.35, -0.35)
HOT_LENS = (1.3, 1.15, 0.5)  # the ball's hot spot: radii across it and its depth


def materials():
    glow = k.level_palette()

    def lit(name, index, strength, **kw):
        return k.material(name, palette=index, emission=glow[index], emission_strength=strength, **kw)
    return {
        "deck": k.material("greyclaw_hull", palette=0x6b, metallic=0.6, roughness=0.24),
        "trim": k.material("greyclaw_trim", palette=0x6e, metallic=0.55, roughness=0.22),
        "seam": k.material("greyclaw_seam", palette=0x63, metallic=0.4, roughness=0.5),
        "saddle": k.material("greyclaw_hump", palette=0x6c, metallic=0.65, roughness=0.16),
        "ledge": k.material("greyclaw_ledge", palette=0x6a, metallic=0.55, roughness=0.28),
        "steel": k.material("greyclaw_steel", palette=0x68, metallic=0.5, roughness=0.34),
        "collar": k.material("greyclaw_collar", palette=0x64, metallic=0.4, roughness=0.35),
        "ball": lit("greyclaw_ball", 0x76, 0.9, metallic=0.1, roughness=0.18),
        "hot": lit("greyclaw_ball_hot", 0x7b, 1.6, roughness=0.15),
        "lamp": lit("greyclaw_lamp", 0x76, 1.2, roughness=0.15),
        "vent": lit("greyclaw_vent", 0x74, 0.8, roughness=0.4),
    }


def mirrored_points(points, side):
    return [(side * x, y) for x, y in points] if side > 0 else [(-x, y) for x, y in reversed(points)]


def hump_rings(side):
    """The hump's sections along its line (sampled finely, the line a smooth curve through HUMP)."""
    dense = mk.chaikin([tuple(p) for p in HUMP], 3, closed=False)
    rings = []
    segments = 40
    for i, (x, y, z, a, b) in enumerate(dense):
        p = Vector((side * x, y, z))
        q0 = Vector((side * dense[max(i - 1, 0)][0], dense[max(i - 1, 0)][1], dense[max(i - 1, 0)][2]))
        q1 = Vector((side * dense[min(i + 1, len(dense) - 1)][0], dense[min(i + 1, len(dense) - 1)][1],
                     dense[min(i + 1, len(dense) - 1)][2]))
        t = (q1 - q0).normalized()
        across = t.cross(Vector((0, 0, 1))).normalized()
        up = across.cross(t).normalized()
        if up.z < 0:
            up = -up
        rings.append([p + across * a * math.cos(2 * math.pi * j / segments) +
                      up * b * math.sin(2 * math.pi * j / segments) for j in range(segments)])
    # The blunt point: the last section carried on along the line, shrinking as a superellipse.
    centre = sum(rings[-1], Vector()) / segments
    t = (centre - sum(rings[-2], Vector()) / segments).normalized()
    last = [v - centre for v in rings[-1]]
    for i in range(1, 6):
        d = END_ROUND * i / 6
        f = (1 - (d / END_ROUND) ** END_POWER) ** (1 / END_POWER)
        rings.append([centre + t * d + v * f for v in last])
    return rings, centre + t * END_ROUND


def line_point(station, side):
    """The hump's line at a station (an index into HUMP, fractions between): its point and direction."""
    i = min(int(station), len(HUMP) - 2)
    f = station - i
    a, b = Vector(HUMP[i][:3]), Vector(HUMP[i + 1][:3])
    p = a.lerp(b, f)
    t = (b - a).normalized()
    if i > 0 and f < 0.5:
        t = (t + (a - Vector(HUMP[i - 1][:3])).normalized() * (0.5 - f)).normalized()
    elif i + 2 < len(HUMP) and f > 0.5:
        t = (t + (Vector(HUMP[i + 2][:3]) - b).normalized() * (f - 0.5)).normalized()
    return Vector((side * p.x, p.y, p.z)), Vector((side * t.x, t.y, t.z))


def arm(m, side):
    """The core, the hump with its hook, the ledge, the vent, the lip and the emitter."""
    s = side
    # The dark core behind the hump.
    x0, _, y0, y1, z0, z1 = ab.CORE
    xa, xb = sorted((s * x0, s * CORE_X1))
    core = mk.box("core", xa, xb, y0, y1, z0, z1, m["seam"])
    mk.bevel(core, 0.3, 2, 35)

    # The hump and its hook: the tube intersected with the hook's plan, softened.
    rings, end = hump_rings(s)
    start = Vector((s * (HUMP[0][0] - 0.5), HUMP[0][1], HUMP[0][2]))
    tube = k.loft("hump", rings, m["saddle"], start_point=start, end_point=end)
    plan = mk.prism("hump_plan", mirrored_points(mk.chaikin(ARM_PLAN, 1), s), -1.0, 20.0)
    mk.boolean(tube, plan)
    mk.soften(tube, 0.22, 8, 0.6, 0.2)
    mk.paint(tube, lambda c, n: m["saddle"] if n.z > 0.5 else m["deck"])
    # The knuckles: dark grooves round the hump where it starts to curl and across the talon, each a
    # thin ring laid round the softened surface (found by rays from the line out to it) and sunk into it.
    tree = BVHTree.FromObject(tube, bpy.context.evaluated_depsgraph_get())
    for i, station in enumerate(KNUCKLES):
        p, t = line_point(station, s)
        across = t.cross(Vector((0, 0, 1))).normalized()
        up = across.cross(t).normalized()
        points = []
        for j in range(33):
            a = 2 * math.pi * j / 32
            d = across * math.cos(a) + up * math.sin(a)
            hit = tree.ray_cast(p + d * 8.0, -d, 8.0)
            if hit[0] is not None:
                points.append(hit[0] - d * 0.12)
        if len(points) > 20:
            k.smooth(mk.tube(f"knuckle{i}", points, 0.2, m["seam"], 8), 60)
    # The ledge in front of the hump (row 14), into the hook.
    _, y, z, r = ab.LEDGE
    k.smooth(mk.tube("ledge", [(s * LEDGE_X[0], y, z), (s * LEDGE_X[1], y, z)], r, m["ledge"], 16), 50)
    # The vent under it: glowing slats between grey posts.
    _, vy0, vy1, vz0, vz1 = ab.VENT
    xa, xb = sorted((s * VENT_X[0], s * VENT_X[1]))
    vent = mk.box("vent", xa, xb, vy0, vy1 + 0.6, vz0, vz1, m["vent"])
    mk.bevel(vent, 0.15, 1, 35)
    for i, px in enumerate(VENT_POSTS):
        px *= s
        post = mk.box(f"post{i}", px - 0.38, px + 0.38, vy0 - 0.1, vy1 + 0.5, vz0 - 0.1, vz1 + 0.1, m["steel"])
        mk.bevel(post, 0.2, 2, 35)
        mk.shade(post, 40)
    # The lip: a plate sloping down towards the front, its end in the hook.
    lip_plan, bottom, top_back, top_front = ab.LIP
    outline = [(lip_plan[0][0], lip_plan[0][1]), (LIP_X1, lip_plan[1][1]), (LIP_X1, lip_plan[2][1]),
               (lip_plan[3][0], lip_plan[3][1])]
    lip = mk.prism("lip", mirrored_points(outline, s), bottom, 12.0, m["ledge"])
    slope = (top_back - top_front) / (outline[0][1] - outline[2][1])
    profile = [(outline[2][1] - 1, 0.0), (outline[0][1] + 1, 0.0), (outline[0][1] + 1, top_back + slope),
               (outline[2][1] - 1, top_front - slope)]
    mk.boolean(lip, mk.prism("lip_side", profile, -40.0, 40.0, axis="x"))
    mk.cleanup(lip)
    mk.bevel(lip, 0.35, 3, 30)
    mk.paint(lip, lambda c, n: m["ledge"] if n.z > 0.5 else m["steel"])
    mk.shade(lip, 35)
    # The emitter under the lip.
    _, (root, r0), (tip, r1) = ab.FANGS
    points, radii = [], []
    for i in range(8):
        t = i / 7
        points.append(Vector((s * FANG_X, root.y + (tip.y - root.y) * t, root.z + (tip.z - root.z) * t)))
        radii.append(r0 + (r1 - r0) * t ** 1.3)
    k.smooth(mk.tube("fang", points, r0, m["steel"], 14, radii=radii), 50)
    k.smooth(mk.ball("fang_tip", tuple(points[-1]), (r1 + 0.08,) * 3, m["steel"], 12, 6), 60)


def block(m, side):
    """polish_arm_bridge's block in grey, its ridge over the deck only, its ball glowing."""
    ab.block(side, m)
    s = side
    for obj in list(bpy.context.scene.objects):
        if obj.name == f"ridge{s}":
            bpy.data.objects.remove(obj)
    housing = bpy.data.objects[f"housing{s}"]
    hit = mk.surface([housing])
    points, ups = [], []
    for i in range(30):
        y = RIDGE_Y[0] + (RIDGE_Y[1] - RIDGE_Y[0]) * i / 29
        h = hit(s * ab.RIDGE_X, y)
        if h is not None:
            points.append(h[0])
            ups.append(h[1])
    k.smooth(mk.bar(f"ridge{s}", points, ups, 0.36, 0.3, 0.4, m["trim"], 12, 3.0), 40)
    # The ball's hot spot, towards the sun (upper left) as the sprite's yellow (columns 4-5 of rows 9-10):
    # a round lens sunk into it.
    centre, r = ab.BALL
    centre = Vector((s * centre.x, centre.y, centre.z))
    hot = Vector((-0.3 * s, 0.4, 1.0)).normalized()
    lens = mk.ball(f"ball_hot{s}", (0.0, 0.0, 0.0), HOT_LENS, m["hot"], 24, 10)
    lens.data.transform(Matrix.Translation(centre + hot * (r - HOT_LENS[2] * 0.45)) @
                        hot.to_track_quat("Z", "Y").to_matrix().to_4x4())


def build_whole(side):
    m = materials()
    block(m, side)
    arm(m, side)
    return m


# --- Checks, export ---------------------------------------------------------------------------------

def sprite_mask(sheets, sprite):
    return k.sprite_mask(os.path.join(sheets, "enemy_V.png"), sprite)


def whole_mask(sheets, sprites):
    a, b = (sprite_mask(sheets, s) for s in sprites)
    return [a[y] + b[y] for y in range(28)]


def build():
    options = k.args()
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    for side, pieces in ((1, LEFT), (-1, RIGHT)):
        k.reset()
        bpy.context.scene.view_settings.view_transform = "Standard"
        m = build_whole(side)
        whole = mk.meshes()
        if side < 0:
            mk.transform(whole, Matrix.Translation((RIGHT_SHIFT, 0.0, 0.0)))
        bpy.context.view_layer.update()  # the objects' bounds, which cut() tests, follow the moves
        label = "left (V 44 beside V 46)" if side > 0 else "right (V 85 beside V 87)"
        print("whole %s: %d triangles, %d objects" % (label, mk.triangles(whole), len(whole)))
        if "check" in options:
            mk.compare("whole " + label, mk.coverage(whole, 48, 28, centre=(-12.0, 0.0)),
                       whole_mask(options["check"], [p[1] for p in pieces]))
        if "preview" in options:
            mk.preview(options["preview"] + ("claw_whole_l" if side > 0 else "claw_whole_r"), whole, size=(48, 28),
                       scale=10, distance=1.6, centre=(-12.0, 0.0))
            bpy.context.view_layer.update()
        for name, sprite, box, centre_x in pieces:
            if only and name not in only:
                continue
            parts = [p for p in (mk.cut(src, box, m["seam"]) for src in whole) if p is not None]
            mk.transform(parts, Matrix.Translation((-centre_x, 0.0, 0.0)))
            if "check" in options:
                mk.compare("%s (V %d)" % (name, sprite), mk.coverage(parts, 24, 28),
                           sprite_mask(options["check"], sprite))
            mk.report(name, parts, os.path.join(out, name + ".glb"))
            if "preview" in options:
                mk.preview(options["preview"] + name, parts)
            for obj in parts:
                bpy.data.objects.remove(obj)


if __name__ == "__main__":
    build()
