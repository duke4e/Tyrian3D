"""The grey ship in a frame of two rails of TYRIAN, HOLES, ASSASSIN and TYRIAN X (sheet 2: 269 flying to the right,
271 its mirror image flying to the left; 2x2 each, 24 x 28 pixels, not animated; sky and top layers; enemies 24 and
25 of episodes 1 and 3), polished (2026-10-19; it replaces wave2_g.py's boom_ship()). models.cfg: model
boom_ship_right / boom_ship_left; sprite 2 269 boom_ship_right yaw=0 glow=..., sprite 2 271 boom_ship_left yaw=0
glow=... (not pieces of one object: the levels send 269 in from the left (x -10, 0) and 271 from the right (x 290,
240, 300), one at a time, swooping (xcaccel 10, ycaccel -20) and firing; 271 is 269's pixels mirrored exactly, so its
model is this one mirrored).

As the sprite (269) and its 4x upscale draw it: a grey pod lying across the screen, its blunt pointed nose to the
right (columns 4-23, rows 6-20: 15 rows across at its widest, its axis on row 13), its rear end rounded; on the
rear of its top a dark socket (columns 6-11 of rows 11-14) with two red lamps standing in it across the pod (columns
6 and 8, rows 12-14), a gold collar rim curving round the pod's rear either side of the socket (rows 7-10 and 15-19,
from column 9 at the flanks back to column 5), a small gold blade on the top behind the socket (columns 12-14 of
row 13); behind the pod the frame: a grey post across the screen (columns 1-2, rows 7-19) with a hub in its middle
(columns 0-3, rows 10-14) joined to the pod's rear, gold elbows from the post's ends bending out to two grey rails
that run forward above and below the pod (rows 3 and 23, columns 7-14), a dark joint between elbow and rail.

Built about the pod's axis (y = 0.5, z = 0: the game centres sky objects in height): the pod lathed, the socket a
shallow dish cut into its top (an ellipsoid taken away, its rear tipped down with the pod's top), the lamps (their own
colours, glowing) standing in it, the gold rim and the frame swept tubes. Coordinates as in tyrkit: 1 unit = 1 game
pixel, +X right, +Y up the screen, +Z towards the camera; column c and row r of the sprite are x = c + 0.5 - 12,
y = 13.5 - r.

Replaces wave2_g.py's boom ship: remove boom_ship() with its section header and its two model("boom_ship_...") lines,
mirror_objects() (only boom_ship() calls it), the boom ship's lines of its docstring, and E2_269 with its comment in
wave2_g_art.py (nothing reads it).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes against
enemy_2.png), --preview <prefix>, --only <name,...>.
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_redjet import Curve  # noqa: E402

AXIS_Y = 0.5
SQUASH = 0.85                      # the pod's height, of its width
SEGMENTS = 40
# The pod's radius along x (2/3 into the sprite's outline): the rounded rear, the body, the nose.
POD = Curve([(-8.45, 0.0), (-8.38, 1.6), (-8.15, 2.75), (-7.75, 3.75), (-7.2, 4.65), (-6.5, 5.45), (-5.7, 6.2),
             (-4.8, 6.8), (-3.8, 7.12), (-2.5, 7.2), (1.0, 7.2), (2.8, 7.12), (3.9, 6.75), (5.0, 6.05), (6.2, 5.2),
             (7.4, 4.35), (8.6, 3.5), (9.6, 2.7), (10.5, 1.9), (11.15, 1.15), (11.55, 0.5), (11.68, 0.0)])
POD_REAR, POD_NOSE = -8.45, 11.68
# The socket: its middle (x, y), half-lengths along x and y, how deep it is cut into the pod's top.
SOCKET = (-3.45, 1.0, 3.6, 2.25, 0.9)
SOCKET_TILT = math.radians(18.0)   # its rear end tipped down (degrees)
LAMPS = (-5.25, -3.35)             # the red lamps' x (columns 6 and 8), across the pod from y -1 to 2
# The gold rim: x round the pod (angle from its top), its arcs either side of the socket (degrees).
RIM_FRONT, RIM_BACK, RIM_FROM, RIM_TO = -3.0, -6.6, 19.0, 165.0
# The frame: the post's x, its ends; the hub; the rails' y (either side of the axis), their x.
POST_X, POST_Y0, POST_Y1, POST_R = -10.15, -6.1, 7.1, 0.95
HUB = (-10.6, 1.0, 2.05)           # x, y, radius
RAIL_DY, RAIL_X0, RAIL_X1, RAIL_R = 10.0, -4.6, 3.35, 1.1


def materials():
    glow = k.level_palette()
    return {
        "pod": k.material("boom_pod", palette=0x09, metallic=0.45, roughness=0.3),
        "pod_dark": k.material("boom_pod_dark", palette=0x06, metallic=0.45, roughness=0.35),
        "socket": k.material("boom_socket", palette=0x02, metallic=0.15, roughness=0.55),
        "lamp": k.material("boom_lamp", palette=0x77, metallic=0.0, roughness=0.3, emission=glow[0x77],
                           emission_strength=1.2),
        "lamp_hot": k.material("boom_lamp_hot", palette=0x79, metallic=0.0, roughness=0.25, emission=glow[0x79],
                               emission_strength=1.6),
        "gold": k.material("boom_gold", palette=0x1a, metallic=0.65, roughness=0.28),
        "gold_dark": k.material("boom_gold_dark", palette=0xa6, metallic=0.5, roughness=0.35),
        "frame": k.material("boom_frame", palette=0x08, metallic=0.6, roughness=0.28),
        "hub": k.material("boom_hub", palette=0x0a, metallic=0.6, roughness=0.25),
        "joint": k.material("boom_joint", palette=0x03, metallic=0.5, roughness=0.4),
    }


def pod_point(x, angle, lift=0.0):
    """The point on the pod's surface at x, `angle` degrees round from its top towards +y, `lift` out of it."""
    a = math.radians(angle)
    r = POD(min(max(x, POD_REAR), POD_NOSE)) + lift
    return Vector((x, AXIS_Y + r * math.sin(a), r * math.cos(a) * SQUASH))


def pod(m):
    xs = [POD_REAR + (POD_NOSE - POD_REAR) * (0.5 - 0.5 * math.cos(math.pi * i / 44)) for i in range(45)]
    rings = []
    for x in xs[1:-1]:
        r = POD(x)
        rings.append([Vector((x, AXIS_Y + r * math.sin(2 * math.pi * j / SEGMENTS),
                              r * SQUASH * math.cos(2 * math.pi * j / SEGMENTS))) for j in range(SEGMENTS)])
    obj = k.loft("pod", rings, m["pod"], start_point=(POD_REAR, AXIS_Y, 0.0), end_point=(POD_NOSE, AXIS_Y, 0.0))
    k.smooth(obj, 50)
    # The underside a shade darker (the sprite's lower half).
    mk.paint(obj, lambda c, n: m["pod_dark"] if n.z < -0.55 else None)
    return obj


def socket(m, pod_obj):
    """The dark socket on the pod's top: a shallow dish cut into it (an ellipsoid taken away, its faces the socket's
    dark), the lamps standing in it."""
    cx, cy, ax, ay, sink = SOCKET
    top = surface_z(cx, cy)
    # An ellipsoid, its rear end tipped down as the pod's top falls away towards its rear.
    cutter = k.ellipsoid("socket_cutter", (0.0, 0.0, 0.0), (ax, ay, 1.2 + sink), m["socket"], 40, 20)
    cutter.data.transform(Matrix.Translation((cx, cy, top + 1.2 * math.cos(SOCKET_TILT))) @
                          Matrix.Rotation(-SOCKET_TILT, 4, "Y"))
    mk.boolean(pod_obj, cutter, "DIFFERENCE")
    k.smooth(pod_obj, 50)
    hit = mk.surface([pod_obj])

    def floor(p):
        h = hit(*p)
        return h[0].z if h else None
    made = []
    # The red lamps: upright slabs across the pod, glowing, hotter in their middles.
    for i, x in enumerate(LAMPS):
        z_floor = floor((x, AXIS_Y))
        base = z_floor if z_floor is not None else surface_z(x, cy) - sink
        lamp = k.ellipsoid(f"lamp{i}", (x, AXIS_Y, base + 0.15), (0.5, 1.55, 0.62), m["lamp"], 14, 10)
        k.smooth(lamp, 60)
        mk.paint(lamp, lambda c, n: m["lamp_hot"] if abs(c.y - AXIS_Y) < 0.7 and n.z > 0.3 else None)
        made.append(lamp)
    return made


def surface_z(x, y):
    """The pod's top surface at (x, y)."""
    r = POD(min(max(x, POD_REAR), POD_NOSE))
    dy = y - AXIS_Y
    return SQUASH * math.sqrt(max(0.0, r * r - dy * dy))


def rim(m):
    """The gold rim of the pod's rear cowl: two arcs on the pod's surface, from the socket's sides round the flanks
    (where they come forward to RIM_FRONT) towards its underside."""
    made = []
    for side in (-1, 1):
        pts, radii = [], []
        steps = 26
        for i in range(steps + 1):
            ang = RIM_FROM + (RIM_TO - RIM_FROM) * i / steps
            s = math.sin(math.radians(ang)) ** 2
            x = RIM_BACK + (RIM_FRONT - RIM_BACK) * s
            pts.append(pod_point(x, side * ang, 0.12))
            f = min(1.0, (ang - RIM_FROM) / 10.0, (RIM_TO - ang) / 10.0)
            radii.append(0.45 + 0.52 * max(f, 0.0))
        tube = mk.tube(f"rim{side:+d}", pts, 0.7, m["gold"], 12, radii=radii)
        k.smooth(tube, 50)
        mk.paint(tube, lambda c, n: m["gold_dark"] if n.z < -0.2 else None)
        made.append(tube)
    return made


def blade(m):
    """The small gold blade on the pod's top behind the socket (columns 12-14 of row 13)."""
    rings = []
    for x in [0.2 + 3.4 * i / 10 for i in range(11)]:
        f = math.sin(math.pi * (x - 0.2) / 3.4) ** 0.5
        base = surface_z(x, AXIS_Y) - 0.3
        rings.append([Vector((x, AXIS_Y + 0.42 * f * math.cos(2 * math.pi * j / 12),
                              base + (0.3 + 0.75 * f) * (0.5 + 0.5 * math.sin(2 * math.pi * j / 12))))
                      for j in range(12)])
    return k.smooth(k.loft("blade", rings, m["gold"]), 50)


def frame(m):
    """The post with its hub, the shaft to the pod, the gold elbows and the grey rails."""
    made = []
    post = mk.tube("post", [(POST_X, POST_Y0, 0.0), (POST_X, POST_Y1, 0.0)], POST_R, m["frame"], 14)
    made.append(k.smooth(post, 50))
    hx, hy, hr = HUB
    made.append(k.smooth(k.ellipsoid("hub", (hx, hy, 0.0), (hr * 0.85, hr, hr * 0.8), m["hub"], 20, 12), 50))
    made.append(k.smooth(mk.tube("shaft", [(hx + 0.5, hy - 0.2, 0.0), (POD_REAR + 0.6, AXIS_Y, 0.0)], 1.15,
                                 m["frame"], 14), 50))
    for side in (-1, 1):
        y_end = POST_Y1 if side > 0 else POST_Y0
        rail_y = AXIS_Y + side * RAIL_DY
        # The elbow: from the post's end out to the left edge's corner and diagonally up to the rail's end.
        path = [(POST_X, y_end - side * 0.9, 0.0), (POST_X - 0.45, y_end + side * 0.15, 0.0),
                (-9.6, AXIS_Y + side * 7.75, 0.0), (-7.7, AXIS_Y + side * 8.95, 0.0), (-6.2, AXIS_Y + side * 9.85, 0.0),
                (-5.2, rail_y, 0.0), (RAIL_X0 - 0.2, rail_y, 0.0)]
        elbow = mk.smooth_tube(f"elbow{side:+d}", [p + (1.05,) for p in path], m["gold"], segments=12)
        k.smooth(elbow, 50)
        mk.paint(elbow, lambda c, n: m["gold_dark"] if n.z < -0.3 else None)
        made.append(elbow)
        joint = k.loft(f"joint{side:+d}", [[Vector((x, rail_y + r * math.sin(2 * math.pi * j / 14),
                                                     r * math.cos(2 * math.pi * j / 14))) for j in range(14)]
                                            for x, r in ((RAIL_X0 - 0.45, 1.05), (RAIL_X0 + 0.25, 1.05))], m["joint"])
        made.append(k.smooth(joint, 50))
        profile = [(RAIL_X0, RAIL_R), (RAIL_X1 - 0.5, RAIL_R), (RAIL_X1 - 0.15, RAIL_R * 0.8), (RAIL_X1, RAIL_R * 0.4)]
        rail = k.loft(f"rail{side:+d}", [[Vector((x, rail_y + r * math.sin(2 * math.pi * j / 14),
                                                   r * math.cos(2 * math.pi * j / 14))) for j in range(14)]
                                          for x, r in profile], m["frame"], end_point=(RAIL_X1 + 0.05, rail_y, 0.0))
        made.append(k.smooth(rail, 45))
    return made


def build_ship(m):
    socket(m, pod(m))
    rim(m)
    blade(m)
    frame(m)
    objs = mk.meshes()
    for obj in objs:
        mk.apply(obj)
    bpy.context.view_layer.update()
    return objs


PIECES = [("boom_ship_right", 269, False), ("boom_ship_left", 271, True)]


def build():
    options = k.args()
    out = mk.outdir(options)
    only = options.get("only", "").split(",") if "only" in options else None
    sheet = os.path.join(options["check"], "enemy_2.png") if "check" in options else None
    for name, sprite, mirror in PIECES:
        if only and name not in only:
            continue
        k.reset()
        m = materials()
        objs = build_ship(m)
        if mirror:  # 271 is 269 mirrored about the sprite's middle (x = 0)
            mirrored = []
            for obj in objs:
                copy = k.mirror_x(obj, obj.name + "_m")
                copy.data.name = copy.name
                mirrored.append(copy)
            for obj in objs:
                bpy.data.objects.remove(obj)
            objs = mirrored
            bpy.context.view_layer.update()
        bpy.context.scene.view_settings.view_transform = "Standard"
        if sheet:
            mk.compare("%s (2 %d)" % (name, sprite), mk.coverage(objs, 24, 28), k.sprite_mask(sheet, sprite))
        mk.report(name, objs, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, objs)


if __name__ == "__main__":
    build()
