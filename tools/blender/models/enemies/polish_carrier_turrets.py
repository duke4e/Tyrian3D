"""The missile launcher and the grey robot the asteroid levels set on the tracked carrier's ball mount (sheet S sprites
267 and 271, 2x2 each: 24 x 28 pixels; ground layer; ASTEROID2 and AST. CITY: the launcher is enemy 550 of episodes 1-3
(armour 80, it launches the white darts, D 171, every 10 ticks), the robot enemy 844 of episode 3 (armour 20)), and
their damaged looks (S 273, the launcher's dgr at armour 40; S 237, the robot's at 15), polished (2026-10-21; they
replace wave3_u_carrier.py's launcher_parts() and robot_parts(), a slab pod and a robot of tubes and spheres standing
on the old mount, and wave3_ap_ast.py's small_damaged() looks of them). models.cfg: model carrier_launcher,
carrier_robot, carrier_launcher_damaged, carrier_robot_damaged ... origin (unchanged); sprite s 267 carrier_launcher
yaw=0 height=-4, sprite s 271 carrier_robot yaw=0 height=-4, sprite s 273 carrier_launcher_damaged yaw=0 height=-4,
sprite s 237 carrier_robot_damaged yaw=0 height=-4 (with the carrier's).

Where the levels put them: event 10 (ground2) at the carrier's event 12's x + 12, y -52 (the carrier's first piece at
y -28): the sprite's centre 10 pixels up the screen from the carrier's middle, at its x (ASTEROID2 t 7482, the
launcher; AST. CITY: the launcher at t 412, 1812, 2260, 6460, the robot at 3688, 3940, 4164, 5424, 6488, 6824). Episode
6 sets neither on its carriers. Neither sprite is another's pixels mirrored, turned or in other ramps (twins3.py);
enemy 278, whose frames run through S 267-275, is in no level.

As the sprites and their 4x upscales draw them (columns and rows of the 24 x 28 sprite):
- the launcher (S 267): a grey box (columns 3-21 of rows 2-24), its back corners rounded; along its top's middle a
  raised red stripe (columns 10-14 of rows 2-15, lit along its left), its right wall dark; the grey either side
  lit at its left, a seam across at row 7, a dark slot in each side at rows 9-10; its front face (rows 17-23) holds
  seven tubes, four (centred on columns 6, 10, 14 and 18, rows 17-19) over three (columns 8, 12, 16, rows 21-23), their
  mouths dark; a lip under it (row 24). Damaged (S 273): the grey either side burnt black in patches (the left side's
  middle, the right side's back and front), the stripe scorched dark down its middle, the lower tubes' rims gone dark.
- the robot (S 271): a drum head (columns 6-17 of rows 5-13), its top a lit rim round a dark dish, its front side
  lit; under it a broad yoke of shoulders (columns 4-19 of rows 14-17), lit along its top; two arm guns from its ends
  out and down the screen (to columns 1-3 and 20-22 of rows 19-22), dark muzzles at their ends; between them a thick
  gun (columns 8-15 of rows 18-26) whose round muzzle faces the viewer (rows 23-26, its bore dark). Damaged (S 237):
  the dish and the head's front burnt black, the shoulders and the left arm scorched, the gun's barrel black.

Built as such machines for the game's camera, as the carrier is (polish_track_carrier.py: each part where the sprite
draws it, moved down the screen by S(its top's height), its walls upright): seated on the carrier's ball (MOUNT, its
top 15.6 over the ground, 4.5 pixels down the screen from the sprite's middle as the camera's shift puts it), so their
tops, 21-25 pixels up, lie 8-9 pixels down the screen from where the sprites draw them and the camera sees them there.
The launcher a pod on a pivot ring: its body the intersection of a side profile (its top level, its front a 45-degree
slope that faces the camera) and a plan with rounded corners, bevelled; the stripe a raised bar, the seams and slots
cut in, the seven tubes short turned rims along the face's normal round dark bores. The robot: hips (a turned drum on
the ball), a torso block reaching back under the head, the head an oval drum with a dish sunk in its top, shoulder
balls and arm guns (tubes to blocky muzzles aimed forward and a little up, at the camera), the heavy gun under the
torso's front aimed forward and up at 35 degrees, so that the camera sees its muzzle round, as the sprite draws it.
Painted with the carrier's materials (polish_track_carrier.materials: greys 0x02-0x0c, reds 0xa2, 0x42, 0x45, 0x48)
by how their faces meet the game's light. The damaged looks are the same models with soot laid over them where the
damaged sprites draw them darker (polish_track_carrier.soot: the parts cut along the camera's pixel lines, the soot
0x03, 0x02, 0x01 by how much darker, along smooth contours; the maps below are sootmap.py's, S 267 -> 273, 271 -> 237);
the launcher's lower tubes and the robot's dish and gun bore burnt out.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the ground (z = 0); origin at
the sprite's centre (pixel 12, 14), which the levels put 10 pixels up the screen from the carrier's middle: the
carrier's MOUNT is (MOUNT.x, MOUNT.y - 10, MOUNT.z) here. Drawn at their origins (origin), on the ground layer as the
carrier (height=-4 on their sprite lines, as on the carrier's).

Replaces wave3_u_carrier.py's launcher_parts(), carrier_launcher(), robot_parts(), carrier_robot(), loaded_whole() and
MOUNT, MOUNT_Z, MOUNT_R, SEAT (with polish_track_carrier.py, all of wave3_u_carrier.py: delete it), and wave3_ap_ast.py's
"The launcher and the robot on the carrier" section (small_damaged() and the two u.model(...) registrations) and its
docstring bullets for carrier_launcher_damaged and carrier_robot_damaged; wave3_ap_ast.py's loading of wave3_u_carrier
("carrier = kit.load(...)") goes with them; wave3_ap_art.py's LAUNCHER_DMG and ROBOT_DMG and wave3_u_art.py's LAUNCHER
and ROBOT (read only by those) can go.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each model's silhouette
against its sprite in enemy_S.png, from straight above and as the game's camera sees it), --preview <prefix>, --only
<model,...>, --with-carrier <glb> (no effect on the output: for gameview checks).
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
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_deli_boss import join, drop_unused  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
import polish_track_carrier as tc  # noqa: E402
from polish_track_carrier import S, TILT, AX, light_paint, profiled, GREY_BANDS, RED_BANDS  # noqa: E402

# The turrets' greys a shade lighter than the hull's (the sprites draw them 0x09-0x0d): tops 0x0a, rims 0x0c.
POST_BANDS = [(-9.0, "shade"), (0.3, "steel"), (0.7, "lit"), (0.93, "bright")]

SEAT = Vector((tc.MOUNT.x, tc.MOUNT.y - 10.0, tc.MOUNT.z))   # the ball's top in the turrets' coordinates

# --- The launcher (as the sprite draws it, then moved by S) -----------------------------------------------------------
POD_X = (-9.0, 10.0)
POD_BOTTOM, POD_TOP = 16.3, 22.3
POD_BACK_DRAWN, POD_FRONT_DRAWN = 12.0, -2.6     # the top's back and front edges as the sprite draws them (y)
POD_BACK = POD_BACK_DRAWN - S(POD_TOP)
POD_TOP_FRONT = POD_FRONT_DRAWN - S(POD_TOP)
POD_FACE_FOOT = POD_TOP_FRONT - (POD_TOP - POD_BOTTOM)   # the face slopes at 45 degrees down to the pod's bottom
STRIPE = (-2.0, 3.0, 0.7)                        # x0, x1, how high over the top
STRIPE_FRONT_DRAWN = -1.5
SEAM_DRAWN = 6.6                                 # the seam across the top (y as drawn)
SLOTS_DRAWN = [(-3.5, 4.4), (7.5, 4.4)]          # the slots (x, y as drawn)
TUBES_DRAWN = [(-5.5, -4.5), (-1.5, -4.5), (2.5, -4.5), (6.5, -4.5), (-3.5, -8.5), (0.5, -8.5), (4.5, -8.5)]
TUBE_R, BORE_R = 1.75, 1.35

# --- The robot (physical: laid out from the sprite as above) ---------------------------------------------------------
YOKE = (-8.2, 9.2, -12.2, -6.6, 16.8, 21.0)       # the shoulders: x0, x1, y0, y1, z0, z1 (a capsule across x)
NECK = (-3.6, 4.6, -7.4, 0.6, 16.6, 20.6)        # the block under the head, behind the yoke
HEAD = (AX, -2.9, 6.0, 3.2, 19.8, 24.8)           # centre x, y, radii x, y, bottom, top
DISH = (0.7, 0.9)                                # the dish's size (of the head's radii) and depth
ARMS = [((-6.6, -9.5, 18.4), (-9.0, -14.0, 18.8)), ((7.6, -9.5, 18.4), (10.0, -14.0, 18.8))]
ARM_R = 2.1
GUN = ((AX, -10.6, 16.0), (0.0, -0.97, 0.24), 7.0, 3.0, 1.3)   # root, direction, length, radius, bore

def materials(prefix):
    m = tc.materials(prefix)
    return tc.soot_materials(m, prefix)


def turned(name, profile, origin, direction, mat, segments=24):
    """A turned part about an axis from origin along direction: profile [(radius, distance along it)]."""
    obj = mk.lathe(name, profile, (0.0, 0.0), mat, segments=segments)
    d = Vector(direction).normalized()
    rot = d.to_track_quat("Z", "Y").to_matrix().to_4x4()
    obj.data.transform(Matrix.Translation(Vector(origin)) @ rot)
    return obj


def rounded_plan(x0, x1, y0, y1, r_back, r_front, steps=6):
    """A rectangle's outline (counter-clockwise) with its back corners (y1) rounded r_back, its front ones r_front."""
    pts = []
    for cx, cy, r, a0 in ((x1 - r_front, y0 + r_front, r_front, -90), (x1 - r_back, y1 - r_back, r_back, 0),
                          (x0 + r_back, y1 - r_back, r_back, 90), (x0 + r_front, y0 + r_front, r_front, 180)):
        for i in range(steps + 1):
            a = math.radians(a0 + 90 * i / steps)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


# --- The launcher ----------------------------------------------------------------------------------------------------

def pivot(m, radius=3.4):
    ring = mk.lathe("pivot", [(radius, SEAT.z - 1.2), (radius, SEAT.z + 0.5), (radius - 0.5, SEAT.z + 0.95),
                              (0.01, SEAT.z + 0.95)], (SEAT.x, SEAT.y), m["shade"], segments=32)
    light_paint(ring, m, GREY_BANDS)
    k.smooth(ring, 40)
    return ring


def launcher_parts(m):
    parts = [pivot(m)]
    x0, x1 = POD_X
    plan = rounded_plan(x0, x1, POD_FACE_FOOT, POD_BACK, 3.4, 1.2)
    side = [(POD_BACK + 1.0, POD_BOTTOM), (POD_BACK + 1.0, POD_TOP), (POD_TOP_FRONT, POD_TOP),
            (POD_FACE_FOOT, POD_BOTTOM)]
    pod = profiled("pod", plan, side, None, POD_BOTTOM, m["steel"])
    # The seam across the top either side of the stripe, the slots.
    seam_y = SEAM_DRAWN - S(POD_TOP)
    cutters = [mk.box("seam_l", x0 - 1.0, STRIPE[0] - 0.2, seam_y - 0.3, seam_y + 0.3, POD_TOP - 0.45, POD_TOP + 2.0),
               mk.box("seam_r", STRIPE[1] + 0.2, x1 + 1.0, seam_y - 0.3, seam_y + 0.3, POD_TOP - 0.45, POD_TOP + 2.0)]
    for sx, sy in SLOTS_DRAWN:
        y = sy - S(POD_TOP)
        cutters.append(mk.box(f"slot{sx}", sx - 0.5, sx + 0.5, y - 0.8, y + 0.8, POD_TOP - 0.7, POD_TOP + 2.0))
    for c in cutters:
        mk.boolean(pod, c, "DIFFERENCE")
    mk.cleanup(pod)
    mk.bevel(pod, 0.55, 3, 30)
    face_n = Vector((0.0, -1.0, 1.0)).normalized()

    def pick(c, n):
        if c.z > POD_TOP - 0.8 and n.z > 0.5 and (abs(c.y - seam_y) < 0.32 or
                                                   any(abs(c.x - sx) < 0.52 and abs(c.y - (sy - S(POD_TOP))) < 0.82
                                                       for sx, sy in SLOTS_DRAWN)) and c.z < POD_TOP - 0.1:
            return "deep"
        if n.dot(face_n) > 0.9:
            return "steel"                     # the tubes' face
        if abs(n.x) > 0.8:
            return "shade"
        return None
    light_paint(pod, m, POST_BANDS, pick)
    mk.shade(pod, 30)
    parts.append(pod)
    # The red stripe along the top.
    sx0, sx1, high = STRIPE
    front = STRIPE_FRONT_DRAWN - S(POD_TOP + high)
    stripe = mk.box("stripe", sx0, sx1, front, POD_BACK - 0.3, POD_TOP - 0.5, POD_TOP + high, m["red"])
    mk.bevel(stripe, 0.3, 2, 35)
    light_paint(stripe, m, RED_BANDS, lambda c, n: "red_deep" if n.x > 0.7 else "red_lit" if n.z > 0.9 else None)
    mk.shade(stripe, 35)
    parts.append(stripe)
    # The tubes in the face: rims along its normal round dark bores.
    for i, (tx, ty) in enumerate(TUBES_DRAWN):
        # A point of the face at height z is at y = POD_TOP_FRONT - (POD_TOP - z) and is seen at y + S(z).
        z = (ty - POD_TOP_FRONT + POD_TOP) / (1.0 + TILT)
        y = POD_TOP_FRONT - (POD_TOP - z)
        centre = Vector((tx, y, z))
        rim = turned(f"tube{i}", [(TUBE_R, -0.6), (TUBE_R, 0.3), (TUBE_R - 0.25, 0.45), (BORE_R + 0.1, 0.45),
                                  (BORE_R, 0.3), (BORE_R, -0.6)], centre, face_n, m["steel"], segments=20)
        light_paint(rim, m, POST_BANDS)
        k.smooth(rim, 45)
        parts.append(rim)
        bore = turned(f"bore{i}", [(BORE_R + 0.02, -0.5), (BORE_R + 0.02, 0.0), (0.01, 0.0)], centre - face_n * 0.4,
                      face_n, m["deep"], segments=16)
        parts.append(bore)
    return parts


# --- The robot -------------------------------------------------------------------------------------------------------

def robot_parts(m):
    parts = []
    hips = mk.lathe("hips", [(3.9, SEAT.z - 1.0), (4.1, SEAT.z + 0.4), (3.7, NECK[4] + 0.6), (0.01, NECK[4] + 0.6)],
                    (SEAT.x, SEAT.y), m["shade"], segments=32)
    light_paint(hips, m, GREY_BANDS)
    k.smooth(hips, 45)
    parts.append(hips)
    # The yoke of shoulders: a capsule across the robot's front, its top lit; the neck block behind it under the head.
    x0, x1, y0, y1, z0, z1 = YOKE
    r = (y1 - y0) / 2
    plan = rounded_plan(x0, x1, y0, y1, r - 0.05, r - 0.05, steps=8)
    side = [(y1 + 0.5, z0), (y1 + 0.5, z1 - 0.6), (y1 - 1.6, z1), (y0 + 1.2, z1), (y0, z1 - 1.0), (y0 + 0.4, z0)]
    yoke = profiled("yoke", plan, side, None, z0, m["steel"])
    mk.bevel(yoke, 1.0, 3, 28)
    light_paint(yoke, m, POST_BANDS)
    mk.shade(yoke, 28)
    parts.append(yoke)
    x0, x1, y0, y1, z0, z1 = NECK
    neck = mk.box("neck", x0, x1, y0, y1, z0, z1, m["shade"])
    mk.bevel(neck, 0.6, 2, 35)
    light_paint(neck, m, GREY_BANDS)
    mk.shade(neck, 35)
    parts.append(neck)
    # The head: an oval drum, a dish sunk in its top, its rim and its front lit.
    hx, hy, rx, ry, hz0, hz1 = HEAD
    ring = [(math.cos(2 * math.pi * j / 48), math.sin(2 * math.pi * j / 48)) for j in range(48)]
    head = mk.prism("head", [(hx + rx * u, hy + ry * v) for u, v in ring], hz0, hz1, m["steel"])
    f, depth = DISH
    dish = mk.ball("dish_cut", (hx, hy, hz1 + 2.2 - depth), (rx * f * 1.12, ry * f * 1.12, 2.2), m["shade"], 32, 16)
    mk.boolean(head, dish, "DIFFERENCE")
    mk.cleanup(head)
    mk.bevel(head, 0.6, 3, 30)

    def pick_head(c, n):
        u = math.hypot((c.x - hx) / (rx * f), (c.y - hy) / (ry * f))
        if u < 1.05 and c.z < hz1 - 0.15:
            return "shade" if n.dot(tc.LIGHT) > 0.75 else "deep"
        if n.y < -0.5 and abs(n.z) < 0.5 and abs(c.x - hx) < rx * 0.55:
            return "lit"                       # the front of the drum, facing the camera
        return None
    light_paint(head, m, POST_BANDS, pick_head)
    mk.shade(head, 30)
    parts.append(head)
    # The arms: shoulder balls, thick tubes out and forward to blocky gun ends, their dark muzzles facing forward.
    for side_i, (root, end) in enumerate(ARMS):
        root, end = Vector(root), Vector(end)
        d = (end - root).normalized()
        parts.append(light_paint(mk.ball(f"shoulder{side_i}", tuple(root), (2.4, 2.4, 2.2), m["steel"], 20, 10), m,
                                 POST_BANDS))
        length = (end - root).length
        arm = turned(f"arm{side_i}", [(ARM_R, 0.0), (ARM_R, length - 2.6), (ARM_R + 0.4, length - 2.3),
                                      (ARM_R + 0.4, length), (ARM_R - 0.2, length + 0.3), (0.85, length + 0.3),
                                      (0.8, length - 0.7), (0.01, length - 0.7)], root, d, m["steel"], segments=16)
        light_paint(arm, m, POST_BANDS, lambda c, n, e=end, dd=d: "deep" if (c - e).length < 1.0 and
                    n.dot(dd) > 0.5 else None)
        k.smooth(arm, 40)
        parts.append(arm)
    # The heavy gun under the yoke's front, aimed forward and a little up, its cradle to the yoke.
    root, direction, length, radius, bore = GUN
    root, d = Vector(root), Vector(direction).normalized()
    gun = turned("gun", [(radius * 0.8, -1.5), (radius, -0.5), (radius, length - 0.9), (radius + 0.3, length - 0.7),
                         (radius + 0.3, length), (radius - 0.2, length + 0.25), (bore + 0.25, length + 0.25),
                         (bore, length - 0.5), (0.01, length - 0.5)], root, d, m["steel"], segments=24)
    light_paint(gun, m, POST_BANDS, lambda c, n: "deep" if (c - (root + d * length)).length < bore + 0.3 and
                n.dot(d) > 0.4 else None)
    k.smooth(gun, 40)
    parts.append(gun)
    cradle = mk.box("cradle", AX - 2.4, AX + 2.4, root.y - 1.0, root.y + 3.4, root.z - 0.6, YOKE[4] + 1.2, m["shade"])
    mk.bevel(cradle, 0.5, 2, 35)
    light_paint(cradle, m, GREY_BANDS)
    mk.shade(cradle, 35)
    parts.append(cradle)
    return parts


# --- Damage -------------------------------------------------------------------------------------------------------------

# How much darker the damaged sprites draw each pixel than the intact ones (sootmap.py: S 267 -> 273, S 271 -> 237).
LAUNCHER_SOOT = """
........................
........................
......0000000000000.....
.....000000000001121....
....00022200000126730...
....00446701000148850...
...0024100011201388800..
...0020002212300244520..
...3020364433300136620..
...6002623432100003020..
...5156822531002535020..
...1487942400003679500..
...2699992200002684000..
...2677772010002552000..
...0249887000002675510..
...0026696000002766600..
...2026245542242237510..
...5030202021000000220..
...7400000001001000000..
...4431002113313200000..
...1343224555854000000..
...1143303331340000000..
...0004001400100000000..
...0000313431000000000..
....00002220000000000...
........................
........................
........................
"""
ROBOT_SOOT = """
........................
........................
........................
........................
........................
........00010000........
.......0023532200.......
......002688866200......
......002667786200......
......002664868200......
......000466876200......
......000499966200......
......004488700000......
......014367000000......
.....04673811222000.....
....0266008444662000....
....0434068846662000....
...044522443546620000...
..02893552003222000000..
.0049631100172000000000.
0002640.00249320.0000000
000020..01299200..000000
.0000...10799200...0000.
..00....16876000....00..
........02200000........
........00000000........
.........000000.........
........................
"""


def burn_out(parts, m, names):
    """Parts burnt black (the launcher's lower tubes, the robot's dish and bore)."""
    for obj in parts:
        if obj.name.startswith(tuple(names)):
            obj.data.materials.clear()
            obj.data.materials.append(m["soot_dark"])
            for p in obj.data.polygons:
                p.material_index = 0


# --- Build ----------------------------------------------------------------------------------------------------------

MODELS = [("carrier_launcher", 267, launcher_parts, None), ("carrier_robot", 271, robot_parts, None),
          ("carrier_launcher_damaged", 273, launcher_parts, "launcher"),
          ("carrier_robot_damaged", 237, robot_parts, "robot")]


def build():
    options = k.args()
    only = options["only"].split(",") if "only" in options else None
    sheet = os.path.join(options["check"], "enemy_S.png") if "check" in options else None
    for name, sprite, parts_of, damaged in MODELS:
        if only and name not in only:
            continue
        k.reset()
        m = materials("ct")
        parts = parts_of(m)
        for obj in parts:
            mk.apply(obj)
        if damaged == "launcher":
            burn_out(parts, m, ("tube4", "tube5", "tube6"))
            tc.soot(parts, tc.soot_grid(LAUNCHER_SOOT), m, (-12.0, 14.0), (24, 28), skip=("bore", "tube4", "tube5",
                                                                                          "tube6"))
        elif damaged == "robot":
            burn_out(parts, m, ("gun",))
            tc.soot(parts, tc.soot_grid(ROBOT_SOOT), m, (-12.0, 14.0), (24, 28), skip=("gun",))
        drop_unused(parts)
        triangulate(parts)
        parts = [join(parts, name)]
        parts[0].data.name = name
        if sheet:
            mask = k.sprite_mask(sheet, sprite)
            mk.compare("%s (S %d, top view)" % (name, sprite), mk.coverage(parts, 24, 28), mask)
            mk.compare("%s (S %d, game camera)" % (name, sprite), tc.camera_coverage(parts, 24, 28), mask)
        bpy.context.scene.view_settings.view_transform = "Standard"
        mk.report(name, parts, os.path.join(mk.outdir(options), name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, parts)


if __name__ == "__main__":
    build()
