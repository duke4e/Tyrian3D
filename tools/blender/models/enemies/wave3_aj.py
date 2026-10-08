"""Enemies of wave 3, batch AJ (sheet 9), modelled as their sprites look (models.cfg: yaw=0). The kit is
wave3_aj_kit.py, the pixels wave3_aj_art.py; the armoured head of UNDERDELI, LAVA RUN and DREAD-NOT is in
wave3_aj_head.py, the eye sphere of LAVA RUN and EYESPY in wave3_aj_eye.py, DREAD-NOT's shoulders and bladed shell
in wave3_aj_dread.py, TIME WAR's blue capsule in wave3_aj_capsule.py.

- lens_pod_grey (9 41, enemies 325 and 326 on the ground of LAVA RUN and UNDERDELI): a squat armoured pod, a
  hooded neck with a black knob on top, two black ball joints at its shoulders, its body creased in a V and
  sloping down to a red lens glowing in a dark socket at its foot.
- lens_pod_blue (9 43, enemy 357 of EYESPY): the same pod in blue armour, its lens dark (the sprite is the grey
  one in other colours).

usage: Blender -b --factory-startup -P wave3_aj.py -- [--only name,name] [--preview <prefix>] [--check 1]
       [--stats 1]
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_aj_kit as kit  # noqa: E402
from wave3_aj_kit import k, pal, Painter, smoothstep  # noqa: E402


# --- 9 41 and 43: the lens pods ----------------------------------------------------------------------------

POD = kit.frame("TURRET", 24, (12, 14))
POD_BLUE = kit.frame("TURRET_BLUE", 24, (12, 14))
AXIS_C = 11.75   # the pod's middle (pixel column)


def pod_v_row(c):
    """The row of the V crease across the body at pixel column c (its tip at row 16.5 in the middle)."""
    return 16.5 - 6.4 * min(1.0, abs(c - AXIS_C) / 9.75)


def pod_height(x, y):
    """The body's height over (x, y): a plateau above the V crease, sloping down below it to the lens; the
    hooded neck and the spine down its middle raised over it."""
    c, r = x + 12.0, 14.0 - y
    u = abs(c - AXIS_C)
    v = pod_v_row(c)
    # Above the crease: the upper plate, a shallow dome over the shoulders, its lower edge a rounded lip at
    # the crease; below it the lower plate, tucked a step under that lip and sloping down to the foot.
    upper = 7.4 + 1.3 * (1.0 - (min(1.0, u / 11.0)) ** 2) - 0.10 * max(0.0, v - r - 3.0)
    lip = smoothstep(-0.9, 0.5, v - r)          # 1 above the crease, 0 below it
    lower = 6.9 - 0.8 * min(1.0, u / 10.5) - (0.42 + 0.22 * min(1.0, u / 8.0)) * max(0.0, r - v)
    z = lower + (upper + 0.35 * math.exp(-((r - v + 0.6) / 0.7) ** 2) - lower) * lip
    # The neck (rows 2-8) and the spine below it (columns 9-14, to the crease's tip): a rounded hood raised
    # over the upper plate.
    neck_w = 6.5 if r < 8.0 else 6.5 - 3.3 * smoothstep(7.6, 9.4, r)
    across = max(0.0, 1.0 - (u / max(neck_w, 0.1)) ** 4)
    neck = 9.9 - 0.18 * max(0.0, r - 8.0) + 0.9 * math.sqrt(across)
    inside = smoothstep(0.0, 0.9, neck_w - u) * smoothstep(0.0, 1.0, 17.2 - r) * smoothstep(0.0, 1.0, r - 1.4)
    z = kit.smax(z, neck * inside + z * (1.0 - inside), 0.8)
    return max(z, 1.2)


def pod(f, lens_glow):
    """The pod, painted by frame f's pixels (lens_glow: the lens's light, 0 for the dark lens)."""
    armour = Painter("lpod", shades={6: tuple(range(2, 16)), 9: tuple(range(2, 16)), 0: (1, 2, 3, 4, 5, 6, 7, 9, 0xa, 0xc)},
                     metallic=0.45, roughness=0.32)
    black = Painter("lpod_ball", shades={0: (1, 2, 3, 4, 5, 6, 7, 9, 0xa, 0xc), 6: (0, 1, 2, 3, 4, 5, 6, 7, 9, 0xb, 0xd)},
                    metallic=0.55, roughness=0.2)
    glow = {0xf0 + s: lens_glow * (0.35 + 0.1 * s) for s in range(16)} if lens_glow else {}
    lens_mats = Painter("lpod_lens", shades={15: (1, 2, 3, 4, 5, 6, 8, 9, 0xb, 0xd), 6: (0, 1, 2, 3, 4, 5, 6, 7, 9, 0xb, 0xd),
                                            0: (1, 2, 3, 4, 5, 6, 7)},
                        metallic=0.1, roughness=0.12, glow=glow)
    polys = kit.outlines_of(f, lambda val, c, r: True, smooth=2, epsilon=0.3)

    def z_of(x, y, e):
        return 0.9 + (pod_height(x, y) - 0.9) * e
    body = kit.heightfield("lpod_body", polys, z_of, armour(0x69), spacing=1.0, edge=1.8)
    k.smooth(body, 40)
    kit.pixelate(body, f)
    kit.paint_sprite(body, f, armour, wall_steps=-1, default=armour(0x65), under=armour(0x62))

    # The crease's lip catches the light (the sprite's bright V).
    def lip(c, nrm):
        col, row = c.x + 12.0, 14.0 - c.y
        val = f.at(c.x, c.y)
        if val is None or val >> 4 not in (6, 9) or nrm.z < 0.2 or abs(col - AXIS_C) > 10.2:
            return None
        d = pod_v_row(col) - row
        if -0.5 < d < 0.9:
            return armour((val >> 4) * 16 + (0xc if col < AXIS_C + 3.0 else 0xa))
        return None
    kit.paint_faces(body, lip)
    kit.merge_bottom(body)

    # The black knob on top of the neck and the ball joints at the shoulders.
    for name, (c, r), radii, z in (("knob", (11.9, 2.7), (3.1, 2.2, 2.3), 9.6),
                                   ("ball_l", (4.9, 11.3), (3.0, 3.2, 3.0), 6.9),
                                   ("ball_r", (18.6, 11.3), (3.0, 3.2, 3.0), 6.9)):
        ball = kit.sphere(f"lpod_{name}", (c - 12.0, 14.0 - r, z), radii, black(0x03), 20, 10)
        kit.paint_sprite(ball, f, black, wall_steps=-1, default=black(0x02), probe=-0.6)

    # The lens at the foot: a dark socket ring and the glowing lens in it, looking down the screen.
    lc = (12.4 - 12.0, 14.0 - 22.6)
    socket = pal("lpod_socket", 0x01 if f is POD else 0x60, metallic=0.5, roughness=0.3)
    base = pod_height(*lc)
    kit.torus("lpod_socket", (lc[0], lc[1], base - 0.6), 4.3, 0.9, socket, 32, 8, squash=0.9)
    lens = kit.sphere("lpod_lens", (lc[0], lc[1] - 0.2, base - 0.9), (3.9, 3.7, 3.2), lens_mats(0xf4), 28, 14)
    kit.paint_sprite(lens, f, lens_mats, wall_steps=-1, default=lens_mats(0xf3 if f is POD else 0x61),
                     keep=lambda val: val >> 4 in (15, 6, 0) and (f is POD or val >> 4 == 6))
    # The blue pod's lens has the sprite's dark blue-greys; any face over the body's blue keeps its dark glass.
    if f is not POD:
        kit.paint_faces(lens, lambda c, nrm: lens_mats(0x61) if f.at(c.x, c.y) is None or f.at(c.x, c.y) >> 4 != 6
                        else None)
    kit.flatten_under(kit.meshes(), 0.0)


kit.PROTECT += ["lpod_body", "lpod_lens"]


@kit.model("lens_pod_grey", mask=lambda: POD.mask())
def lens_pod_grey():
    pod(POD, 1.0)


@kit.model("lens_pod_blue", mask=lambda: POD_BLUE.mask())
def lens_pod_blue():
    pod(POD_BLUE, 0.0)


if __name__ == "__main__":
    kit.run()
