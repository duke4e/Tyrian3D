"""Batch U of wave 3 (sheet S: MINEMAZE, GAUNTLET and the asteroid levels), modelled as their sprites look
(models.cfg: yaw=0). The black orb is in wave3_u_orb.py, the tracked carrier with its launcher and robot in
wave3_u_carrier.py, the hangar in wave3_u_hangar.py; the kit is wave3_u_kit.py, the pixels wave3_u_art.py. (The
bunker with the green lamp, S 277, is built by polish_green_lamp_bunker.py.)

- maze_pipe_end_l, maze_pipe, maze_pipe_cage, maze_pipe_end_r (S 1, 7, 115, 3): the dark blue pipe the
  levels lay across MINEMAZE's and GAUNTLET's corridors, one sprite after another along a row (enemies 586,
  588 or 589 repeated, 587): its left end, a plain segment, the segment with the ring cage round its red
  core (115: the frames 117-123 swell the core; the model shows it glowing, half grown) and its right end.
  The pipe's sections meet in collars at the sprites' edges; all four drawn at their own origins (origin)
  so they line up.

usage: Blender -b --factory-startup -P wave3_u.py -- [--only name,name] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1] [--whole pipe --preview <prefix>]
"""
import math
import os
import sys

from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_u_kit as u  # noqa: E402
from wave3_u_kit import art, k, sh, w, pal, px, py  # noqa: E402


# --- S 1, 7, 115, 3: the pipe across the maze ------------------------------------------------------

PIPE_Y = -1.0      # the pipe's axis (rows 5-24 of the sprites: y 9 .. -11)
PIPE_R = 10.0      # its half-width across the screen
PIPE_H = 7.2       # its half-height
PIPE_Z = 6.6       # its axis' height (it lies a little sunk in the ground)
PIPE_SHADES = {    # the sprite's shades across the pipe, by row (S 7), for painting its faces
    5: 1, 6: 9, 7: 3, 8: 2, 9: 1, 10: 1, 11: 2, 12: 4, 13: 9, 14: 14, 15: 10, 16: 3, 17: 0, 18: 0, 19: 0, 20: 1,
    21: 2, 22: 3, 23: 6, 24: 1}


def pipe_mats():
    m = {s: pal(f"mp_blue{s}", 0x30 | s, metallic=0.55, roughness=0.22) for s in range(0, 16)}
    m["line"] = pal("mp_line", 0x3d, metallic=0.3, roughness=0.15, glow=0.35)
    m["collar"] = pal("mp_collar", 0x35, metallic=0.6, roughness=0.3)
    m["collar_light"] = pal("mp_collar_light", 0x38, metallic=0.6, roughness=0.25)
    m["red"] = pal("mp_red", 0x47, metallic=0.1, roughness=0.3, glow=1.4)
    m["red_core"] = pal("mp_red_core", 0x49, metallic=0.1, roughness=0.25, glow=1.8)
    m["ring"] = pal("mp_ring", 0x37, metallic=0.6, roughness=0.25)
    m["ring_light"] = pal("mp_ring_light", 0x3a, metallic=0.6, roughness=0.2)
    return m


def section(y, z, power=2.3, segments=40):
    """The pipe's cross-section at x (a superellipse in the YZ plane)."""
    pts = []
    for i in range(segments):
        a = 2 * math.pi * i / segments
        c, s = math.cos(a), math.sin(a)
        pts.append((PIPE_Y + math.copysign(abs(c) ** (2 / power), c) * y, PIPE_Z + math.copysign(abs(s) ** (2 / power), s) * z))
    return pts


def pipe_body(name, x0, x1, m, cap_left=False, cap_right=False, step=1.0, line="line"):
    """The pipe from x0 to x1 along X; capped ends round off over their last 5 pixels; `line`: the material
    of the light line along its crest."""
    rings = []
    xs = []
    count = max(2, int(math.ceil((x1 - x0) / step)))
    for i in range(count + 1):
        xs.append(x0 + (x1 - x0) * i / count)
    cap = 5.0
    if cap_left:
        xs = [x0 + cap * (1 - math.cos(math.radians(a))) for a in (0, 18, 36, 54, 72)] + [x for x in xs if x > x0 + cap]
    if cap_right:
        xs = [x for x in xs if x < x1 - cap] + [x1 - cap * (1 - math.cos(math.radians(a))) for a in (72, 54, 36, 18, 0)]
    for x in xs:
        f = 1.0
        if cap_left and x < x0 + cap:
            f = math.sin(math.acos(max(-1.0, min(1.0, (x0 + cap - x) / cap))))
        if cap_right and x > x1 - cap:
            f = math.sin(math.acos(max(-1.0, min(1.0, (x - (x1 - cap)) / cap))))
        f = 0.68 + 0.32 * f
        rings.append([Vector((x, yy, zz)) for yy, zz in section(PIPE_R * f, PIPE_H * f)])
    # Lofted along x (k.loft takes rings in order along any axis).
    obj = k.loft(name, rings, m[1])
    k.smooth(obj, 50)

    def paint(c, n):
        if n.z < -0.3:
            return m[1]
        if abs(n.x) > 0.75:  # the end caps' faces
            return m[7] if n.z > 0.3 else m[3]
        row = int(math.floor(14 - c.y))
        s = PIPE_SHADES.get(row, 1)
        return m[line] if s >= 13 else m[min(15, s + 1)]
    w.paint_faces(obj, paint)
    return obj


def collar(name, x, half, m):
    """A collar round the pipe at x, `half` wide either side (a whole collar where two sprites meet)."""
    rings = []
    grow = 0.55
    for dx, f in ((-half, 0.0), (-half + 0.35, 1.0), (half - 0.35, 1.0), (half, 0.0)):
        rings.append([Vector((x + dx, yy, zz)) for yy, zz in section(PIPE_R + grow * f + 0.05, PIPE_H + grow * f + 0.05)])
    obj = k.loft(name, rings, m["collar"])
    k.smooth(obj, 40)
    w.paint_faces(obj, lambda c, n: m["collar_light"] if n.z > 0.6 and c.y > PIPE_Y else None)
    return obj


@u.whole("pipe", (96, 28))
def pipe_whole():
    """The pipe as the levels lay it: its left end, a plain segment, the caged segment, its right end
    (sprites at x -36, -12, 12, 36)."""
    m = pipe_mats()
    parts = []
    parts.append(pipe_body("end_l", -48.0, -24.0, m, cap_left=True))
    parts.append(pipe_body("plain", -24.0, 0.0, m))
    parts += cage_segment(m, 12.0)
    parts.append(pipe_body("end_r", 24.0, 48.0, m, cap_right=True))
    for x in (-24.0, 0.0, 24.0):
        parts.append(collar(f"collar{x}", x, 1.1, m))
    parts.append(collar("collar_l_end", -44.6, 0.7, m))
    parts.append(collar("collar_r_end", 44.6, 0.7, m))
    return parts


def band(name, cx, lean, m, mat, grow=0.7, radius=0.62, segments=56):
    """A band wound round the pipe at cx, its plane leaning along the pipe: its top crosses the pipe's crest
    `lean` pixels to the right of its sides (seen from above an arc, ")" leaning right, "(" left)."""
    pts = []
    for yy, zz in section(PIPE_R + grow, PIPE_H + grow, segments=segments):
        pts.append((cx + lean * (zz - PIPE_Z) / (PIPE_H + grow), yy, zz))
    return u.ring_path(name, pts, radius, mat, 10)


def cage_segment(m, cx):
    """The caged segment centred at cx: the pipe runs on through a cage of bands wound round it (two crossing
    in the middle, seen from above an O; one leaning out at each side), a glowing red line along its crest
    and the red core swelling from it in the middle."""
    parts = [pipe_body("cage_pipe", cx - 12.0, cx + 12.0, m, line="red")]
    for side in (-1, 1):
        parts.append(band(f"band_mid{side}", cx, 5.4 * side, m, m["ring_light"]))
        parts.append(band(f"band_out{side}", cx + 6.2 * side, 4.4 * side, m, m["ring"], grow=0.55, radius=0.55))
    # Bosses where the middle bands cross at the pipe's sides.
    for sy in (-1, 1):
        parts.append(w.sphere(f"boss{sy}", (cx, PIPE_Y + sy * (PIPE_R + 0.6), PIPE_Z), (1.3, 0.9, 1.4), m["ring_light"],
                              14, 8))
    # The core: a red blister glowing on the crest in the middle of the cage.
    top = PIPE_Z + PIPE_H
    parts.append(w.sphere("core", (cx, PIPE_Y, top - 1.2), (3.6, 4.8, 3.4), m["red_core"], 24, 12))
    parts.append(w.hoop("core_rim", (cx, PIPE_Y, top - 0.35), [(3.5, 0.0), (4.3, -0.3), (4.4, 0.35), (3.8, 0.55)],
                        m["collar"], 32, scale_y=1.3))
    return parts


PIPE_PIECES = [("maze_pipe_end_l", 1, -36.0), ("maze_pipe", 7, -12.0), ("maze_pipe_cage", 115, 12.0),
               ("maze_pipe_end_r", 3, 36.0)]


def pipe_piece(cx):
    objects = pipe_whole()
    u.cut(objects, (cx - 12.0, cx + 12.0, -14.0, 14.0), (cx, 0.0))
    u.budget(4800)


for _name, _sprite, _cx in PIPE_PIECES:
    u.model(_name, [(_sprite, True)])(lambda cx=_cx: pipe_piece(cx))


if __name__ == "__main__":
    u.run()
