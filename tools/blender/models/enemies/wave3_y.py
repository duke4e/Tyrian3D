"""Batch Y of wave 3 (sheet 8: IXMUCANE and SAWBLADES), the creatures and small ships, modelled as their
sprites look (models.cfg: yaw=0). The rock wall is in wave3_y_wall.py; the red ship between its engines, the
red pod and the big spider (objects the game draws in pieces) in wave3_y_boss.py; the kit is wave3_y_kit.py,
the pixels wave3_y_art.py. (The twin tube, 8 19: polish_twin_tube.py; the small crab, 8 267:
polish_tan_crab.py.)

- prong_ship (8 1): the red ship with two long prongs: a pod with a glowing core in the middle, a grey
  crossbar and two long red prongs tipped with grey (its frames pulse the core: it glows).
- claw_dome (8 115): the grey dome with a glowing red eye at its front and a red lamp on top, on two
  brown claws curling under it (its frames pulse the eye: it glows).
- sawblades_carrot (8 129): SAWBLADES' carrot: an orange root with rings and a dark hollow at its middle, its green
  leaves on top.

usage: Blender -b --factory-startup -P wave3_y.py -- [--only name,name] [--preview <prefix>] [--check 1]
       [--stats 1]
"""
import math
import os
import sys

from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_y_kit as y  # noqa: E402
from wave3_y_kit import k, pal, tube, sphere, lathe_axis, smoothstep  # noqa: E402


# --- 8 1: the red ship with two prongs ---------------------------------------------------------------

RED_SHIP = y.frame("RED_SHIP", 24, (12, 14))


def red_mats(prefix):
    return {"red": pal(f"{prefix}_red", 0x48, metallic=0.35, roughness=0.35),
            "red_light": pal(f"{prefix}_red_light", 0x4c, metallic=0.35, roughness=0.3),
            "red_side": pal(f"{prefix}_red_side", 0x45, metallic=0.35, roughness=0.4),
            "red_dark": pal(f"{prefix}_red_dark", 0x41, metallic=0.3, roughness=0.5),
            "grey": pal(f"{prefix}_grey", 0x08, metallic=0.6, roughness=0.3),
            "grey_light": pal(f"{prefix}_grey_light", 0x0c, metallic=0.6, roughness=0.25),
            "grey_dark": pal(f"{prefix}_grey_dark", 0x05, metallic=0.55, roughness=0.35)}


def shade_red(m, light_side=None):
    """Paints a red hull: tops red (the side towards light_side(x) lighter), sides darker, undersides dark."""
    def pick(c, nrm):
        if nrm.z < -0.3:
            return m["red_dark"]
        if nrm.z < 0.45:
            return m["red_side"]
        if light_side is not None and light_side(c, nrm):
            return m["red_light"]
        return m["red"]
    return pick


@y.model("prong_ship", lambda: y.frame_mask(RED_SHIP))
def prong_ship():
    """Two long red prongs (x -6.5 and 5.5, the sprite is symmetric about x = -0.5), wider at the top with
    a grey plate on their outer sides, tapering to the bottom; a grey crossbar through them at y 4.5; between
    them a red pod hanging from it, a grey cap on its top, its core glowing under the cap, grey clamps at its
    sides."""
    ax = -0.5
    m = red_mats("prong")
    core = pal("prong_core", 0x7a, metallic=0.0, roughness=0.3, glow=2.0)
    core_rim = pal("prong_core_rim", 0x75, metallic=0.1, roughness=0.35, glow=0.9)
    for side in (-1, 1):
        keys = [(13.5, -6.4, 0.3), (12.7, -6.4, 1.6), (11.0, -6.2, 2.35), (8.0, -6.0, 2.5), (5.6, -6.0, 2.45),
                (3.8, -6.0, 2.15), (0.0, -6.0, 2.0), (-5.0, -6.2, 1.9), (-9.0, -6.6, 1.6), (-11.2, -7.0, 1.2),
                (-12.4, -7.1, 0.3)]
        secs = []
        for yy, xc, hw in reversed(keys):
            secs.append((yy, ax + side * -xc, 2.4, hw, max(0.35, 1.1 * hw), max(0.3, 0.8 * hw)))
        prong = y.loft_y(f"prong{side}", y.smooth_sections(secs, 0.7), m["red"], segments=16, power=2.2)
        y.paint_faces(prong, shade_red(m, lambda c, nrm, side=side: nrm.x * side < -0.25))
        # The grey plate on its outer side, at the top.
        y.rounded_box(f"plate{side}", (ax + side * 8.0, 7.6, 2.9), (1.9, 5.0, 2.8), m["grey"], bevel=0.45)
        y.rounded_box(f"plate_rib{side}", (ax + side * 8.25, 7.6, 4.3), (1.0, 4.0, 0.5), m["grey_light"], bevel=0.2)
    # The crossbar.
    tube("bar", [(ax - 8.9, 4.5, 5.2), (ax + 8.9, 4.5, 5.2)], 0.85, m["grey"], 14)
    for side in (-1, 1):
        lathe_axis(f"bar_collar{side}", [(0.0, 0.95), (0.15, 1.1), (0.9, 1.1), (1.05, 0.95)], m["grey_light"],
                   (ax + side * 4.6, 4.5, 5.2), (side, 0, 0), segments=14)
    # The pod.
    keys = [(-3.1, 0.2), (-2.4, 1.3), (-1.4, 2.1), (0.0, 3.0), (1.5, 3.7), (3.0, 3.9), (4.5, 3.5), (6.0, 2.6),
            (7.5, 2.0), (9.0, 1.9), (10.6, 1.5), (11.4, 0.2)]
    secs = [(yy, ax, 2.0, hw, max(0.4, 1.0 * hw), max(0.3, 0.8 * hw)) for yy, hw in keys]
    pod = y.loft_y("pod", y.smooth_sections(secs, 0.5), m["red"], segments=20)
    y.paint_faces(pod, shade_red(m, lambda c, nrm: nrm.x > 0.2 and c.y < 4.0))
    sphere("cap", (ax, 10.1, 3.3), (1.75, 1.5, 1.6), m["grey"], 16, 8)
    sphere("core", (ax, 7.5, 3.75), (1.45, 0.95, 0.9), core, 16, 8)
    y.torus("core_rim", (ax, 7.5, 3.5), 1.55, 0.35, core_rim, 20, 8, scale_y=0.7)
    for side in (-1, 1):
        y.rounded_box(f"clamp{side}", (ax + side * 3.9, 2.2, 3.0), (1.6, 2.4, 2.6), m["grey_dark"], bevel=0.4)
    # A spine down the pod's back below the bar.
    tube("spine", [(ax, 3.6, 5.6), (ax, 1.0, 5.3), (ax, -1.4, 3.9)], 0.45, m["red_light"], 10)


# --- 8 115: the dome on two claws ------------------------------------------------------------------

DOME = y.frame("DOME", 24, (12, 14))


@y.model("claw_dome", lambda: y.frame_mask(DOME))
def claw_dome():
    """A grey dome (round at the back, its sides straight), a dark rim low round it, a red lamp glowing on
    its back; in front a tan jaw plate with the glowing red eye in a socket; two brown claws reaching down
    the screen from under the jaw and curling outwards and up at their ends."""
    ax = 0.5
    grey = y.Painter("cdome", shades={0: [3, 5, 7, 9, 11, 13]}, metallic=0.35, roughness=0.35)
    rim = pal("cdome_rim", 0x03, metallic=0.5, roughness=0.4)
    tan = pal("cdome_tan", 0x17, metallic=0.25, roughness=0.5)
    tan_light = pal("cdome_tan_light", 0x1a, metallic=0.25, roughness=0.45)
    tan_dark = pal("cdome_tan_dark", 0x13, metallic=0.2, roughness=0.55)
    eye = pal("cdome_eye", 0x77, metallic=0.0, roughness=0.25, glow=1.8)
    eye_hot = pal("cdome_eye_hot", 0x7c, metallic=0.0, roughness=0.2, glow=2.4)
    lamp = pal("cdome_lamp", 0x79, metallic=0.0, roughness=0.3, glow=1.8)
    lamp_rim = pal("cdome_lamp_rim", 0x72, metallic=0.1, roughness=0.35, glow=0.8)
    socket = pal("cdome_socket", 0x02, metallic=0.4, roughness=0.45)

    # The dome: a half ellipse at the back (y > 1.5), straight sides down to its front at y = -0.6.
    outline = [(ax + 10.6 * math.cos(a), 1.5 + 11.0 * math.sin(a)) for a in [math.pi * i / 28 for i in range(29)]]
    outline += [(ax - 10.6, -0.6), (ax + 10.6, -0.6)]

    def dome_z(x, yy, e=1.0):
        r2 = ((x - ax) / 11.2) ** 2 + (max(0.0, yy - 1.5) / 11.6) ** 2
        z = 1.2 + 7.6 * math.sqrt(max(0.0, 1.0 - r2))
        z *= 0.8 + 0.2 * smoothstep(-0.6, 2.0, yy)  # its front leans back
        return max(0.4, z * e)
    dome = y.heightfield("dome", [outline], dome_z, grey(0x08), spacing=0.45, edge=1.4)
    y.simplify_bottom(dome)
    y.decimate(dome, 1800)

    def paint(c, nrm):
        if nrm.z < -0.3:
            return rim
        if 1.4 < c.y < 3.6 or nrm.z < 0.35:
            return rim if 1.4 < c.y < 3.6 else grey(0x05)
        v = DOME.shade(0, 2)(c.x, c.y)
        return grey(int(min(13, max(7, round(0.55 * v + 6.0)))))
    y.paint_faces(dome, paint)
    # The lamp on its back.
    sphere("lamp", (ax, 12.0, 4.0), (3.2, 1.7, 1.9), lamp, 18, 8)
    y.torus("lamp_rim", (ax, 12.0, 3.7), 3.2, 0.45, lamp_rim, 24, 8, scale_y=0.55)

    # The jaw: a tan plate across the front, lower than the dome.
    jaw = y.prism_x("jaw", [(-4.5, 0.0), (0.4, 0.0), (0.4, 3.2), (-0.4, 4.1), (-2.4, 4.0), (-3.9, 3.1), (-4.5, 1.6)],
                    ax - 10.4, ax + 10.4, tan, bevel=0.5, segments=2)
    y.paint_faces(jaw, lambda c, nrm: tan_light if nrm.z > 0.7 and c.x < ax - 3 else tan if nrm.z > 0.4 else tan_dark)
    # The eye in its socket, half in the jaw, half in the dome's front.
    y.torus("socket", (-0.5, -0.4, 4.2), 2.55, 0.65, socket, 24, 10, scale_y=0.95)
    sphere("eye", (-0.5, -0.4, 4.1), (2.45, 2.3, 1.7), eye, 20, 10)
    sphere("eye_core", (-0.5, -0.6, 5.0), (1.1, 1.0, 0.9), eye_hot, 14, 7)

    # The claws: from under the jaw down the screen, curling outwards and up at their ends.
    for side in (-1, 1):
        sx = lambda v: ax + side * v
        path = [(sx(3.6), -1.5, 2.6), (sx(3.8), -5.0, 2.4), (sx(4.4), -8.6, 2.0), (sx(6.6), -11.2, 1.7),
                (sx(9.4), -11.0, 1.7), (sx(10.6), -8.8, 2.1), (sx(10.8), -6.8, 2.6)]
        pts = y.resample(path, 22)
        secs = []
        for i in range(len(pts)):
            t = i / (len(pts) - 1)
            hw = 1.9 + 0.5 * math.sin(math.pi * min(1.0, t / 0.75)) - (2.2 * (t - 0.7) if t > 0.7 else 0.0)
            secs.append((max(0.4, hw), max(0.4, hw * 0.7)))
        claw = y.loft_path(f"claw{side}", pts, secs, tan, segments=12)
        y.paint_faces(claw, lambda c, nrm: tan_light if nrm.z > 0.75 else tan if nrm.z > 0.2 else tan_dark)


# --- 8 129: the carrot -------------------------------------------------------------------------------

CARROT = y.frame("CARROT", 24, (12, 14))


def leaf(name, base, tip, width, mat, rib_mat, lift=2.0):
    """A leaf from base to tip (3D points): a thin blade, widest a third of the way, curving up by `lift`
    in its middle, a lighter rib along it."""
    b, t = Vector(base), Vector(tip)
    pts = []
    count = 12
    for i in range(count + 1):
        f = i / count
        p = b.lerp(t, f)
        p.z += lift * math.sin(math.pi * f) * 0.8
        pts.append(p)
    secs = [(max(0.12, width * math.sin(math.pi * min(1.0, (i / count) ** 0.8)) * (1.0 - 0.4 * i / count)), 0.22)
            for i in range(count + 1)]
    blade = y.loft_path(name, pts, secs, mat, segments=8, smooth_angle=70)
    tube(name + "_rib", [(p.x, p.y, p.z + 0.12) for p in pts[:-2]], 0.16, rib_mat, 6)
    return blade


@y.model("sawblades_carrot", lambda: y.frame_mask(CARROT))
def sawblades_carrot():
    """An orange root (a cone lying down the screen, rings round it) with a dark brown hollow in its middle
    round a lighter knob, and three green leaves fanning up the screen from its top."""
    ax, az = 0.5, 5.0
    orange = pal("carrot_orange", 0x7a, metallic=0.05, roughness=0.55)
    orange_light = pal("carrot_orange_light", 0x7c, metallic=0.05, roughness=0.5)
    orange_dark = pal("carrot_orange_dark", 0x77, metallic=0.05, roughness=0.6)
    ring_m = pal("carrot_ring", 0x79, metallic=0.05, roughness=0.6)
    hollow = pal("carrot_hollow", 0xb3, metallic=0.05, roughness=0.7)
    hollow_rim = pal("carrot_hollow_rim", 0xb6, metallic=0.05, roughness=0.6)
    knob = pal("carrot_knob", 0xb9, metallic=0.1, roughness=0.45)
    green = pal("carrot_green", 0xc4, metallic=0.05, roughness=0.55)
    green_light = pal("carrot_green_light", 0xc9, metallic=0.05, roughness=0.5)
    green_dark = pal("carrot_green_dark", 0xc1, metallic=0.05, roughness=0.6)

    # The root, along -y from its shoulder (y 5) to its tip (y -14); slight bulges between the rings.
    keys = [(0.0, 0.01), (0.4, 3.2), (1.0, 5.2), (2.0, 6.2), (3.5, 6.6), (5.5, 6.5), (7.5, 6.0), (9.5, 5.1),
            (11.5, 4.1), (13.5, 3.0), (15.5, 1.9), (17.4, 0.9), (18.6, 0.3), (19.0, 0.01)]
    prof = [(t, r) for t, r in k.profile(keys, 0.35)]
    rings_at = [4.0, 6.6, 9.2, 11.8, 14.3]
    prof = [(t, r * (1.0 - 0.07 * max(0.0, 1.0 - min(abs(t - ra) for ra in rings_at) / 0.45))) for t, r in prof]
    root = lathe_axis("root", prof, orange, (ax, 5.0, az), (0, -1, 0), segments=28, squash=0.78)
    y.paint_faces(root, lambda c, nrm: orange_dark if nrm.z < 0.25 else
                  ring_m if min(abs((5.0 - c.y) - ra) for ra in rings_at) < 0.22 else
                  orange_light if nrm.x < -0.3 and nrm.z > 0.5 else orange)
    # The hollow: a dark brown patch on its middle in a raised rim, a lighter knob in it.
    def root_z(x, yy):
        r = y.interp(prof, 5.0 - yy)
        return az + 0.78 * math.sqrt(max(0.0, r * r - (x - ax) ** 2))
    cx, cy = 0.0, -2.4
    y.heightfield("hollow", [y.ellipse(cx, cy, 2.3, 2.3, 28)], lambda x, yy: root_z(x, yy) + 0.12, hollow, spacing=0.4)
    y.ring_path("hollow_rim", [(cx + 2.35 * math.cos(a), cy + 2.35 * math.sin(a),
                                root_z(cx + 2.35 * math.cos(a), cy + 2.35 * math.sin(a)) + 0.1)
                               for a in [2 * math.pi * i / 32 for i in range(32)]], 0.5, hollow_rim, 8)
    sphere("knob", (cx - 0.3, cy + 0.3, root_z(cx, cy) + 0.1), (1.15, 1.15, 0.8), knob, 16, 8)
    # The leaves, from the top of the root.
    base_z = az + 2.6
    leaf("leaf_l", (ax - 0.6, 4.6, base_z), (ax - 5.8, 12.4, base_z + 1.0), 1.5, green, green_light, lift=2.2)
    leaf("leaf_m", (ax + 0.0, 4.8, base_z + 0.4), (ax - 0.2, 13.4, base_z + 2.0), 1.3, green, green_light, lift=2.6)
    leaf("leaf_r", (ax + 0.6, 4.6, base_z), (ax + 5.2, 10.2, base_z + 0.6), 1.4, green_dark, green, lift=1.8)
    lathe_axis("stalk", [(0.0, 1.5), (1.4, 1.1), (1.8, 0.01)], green_dark, (ax, 4.2, base_z - 0.6), (0, 1, 0.3),
               segments=12)


if __name__ == "__main__":
    y.run()
