"""Batch AH of wave 3 (sheet M): MINERS' tan drilling rig and the parts the level puts on it, modelled as the sprites
look (models.cfg: yaw=0). The kit is wave3_ah_kit.py, the pixels wave3_ah_art.py.

MINERS puts the rig together once, from fourteen ground enemies (1174-1185, at t 4472): the rig itself, 191, 193,
195 at (x + 24 i, y - 40) above 229, 231, 233 at (x + 24 i, y - 16) (the lower row drawn over the upper one's last
four rows: 72 x 52 pixels), two guns (235 at (x + 4, y - 34) and (x + 44, y - 34)), two hatches (197 at (x - 2,
y - 12) and (x + 52, y - 12)), two torches (275 at (x - 16, y - 21), 277 at (x + 64, y - 21)), MINERS' black egg
in the hatch on its top (271, obsidian_egg, at (x + 24, y - 40)) and the drill in the socket at its front (267 at
(x + 24, y - 12)). Everything is built in the frame of the whole (RIG_ALL, 104 x 56, the rig at columns 16-87) in
one frame of heights (the ground at z = 0), so that the separate models meet; all are drawn at their own origin.

- drill_rig_tl, _tm, _tr, _bl, _bm, _br (M 191, 193, 195, 229, 231, 233): the rig: two wings of pleated tan
  stone, their pleats rising to points towards the middle, and between them a tan block with an oval pit in its
  top (the black egg lies in it) and a round socket in its lower front ringed with grey steel (the drill comes out
  of it); dark recesses low in the wings for the hatches; grey claws under the wings. The upper pieces keep what
  lies above the lower row (24 rows), as the game draws the lower row over them.
- rig_gun_post (M 235): the guns on the wings: a tan barrel lying up the screen on the middle pleat, an orange
  light glowing round its middle.
- rig_hatch (M 197; frames 199, 237 open its doors on a red light): a small tan cabinet with two doors in the
  wings' recesses, a red light glowing in the slit between them.
- rig_drill_bit (M 267; frame 269 turns its stripes): the grey drill, a cone with spiral flutes pointing down
  the screen and into the ground from the socket.
- rig_torch_l, rig_torch_r (M 275, 277): the poles at the rig's sides, a lamp head on each with its flame
  glowing on its outer side.

usage: Blender -b --factory-startup -P wave3_ah_rig.py -- [--only name,name] [--preview <prefix>] [--check 1]
       [--stats 1] [--whole <prefix>] [--assembly <prefix>]
"""
import math
import os
import sys

from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_ah_kit as kit  # noqa: E402
from wave3_ah_kit import k, sh, w, pal  # noqa: E402

ALL = kit.frame("RIG_ALL", 104, (52, 28))
RIG = kit.frame("RIG", 72, (36, 26))      # the rig alone: its column c, row r is ALL's column c + 16, row r
HATCH = kit.frame("HATCH", 24, (12, 14))
GUN = kit.frame("GUN", 24, (12, 14))
DRILL = kit.frame("DRILL", 24, (12, 14))
TORCH_L = kit.frame("TORCH_L", 24, (12, 14))
TORCH_R = kit.frame("TORCH_R", 24, (12, 14))

# Where the sprites' centres lie in ALL's frame (x, y): the parts are built there and moved to their own origin.
GUN_AT = [(ALL.X(16 + 4 + 11.5), ALL.Y(6 + 13.5)), (ALL.X(16 + 44 + 11.5), ALL.Y(6 + 13.5))]
HATCH_AT = [(ALL.X(16 - 2 + 11.5), ALL.Y(28 + 13.5)), (ALL.X(16 + 52 + 11.5), ALL.Y(28 + 13.5))]
TORCH_AT = [(ALL.X(16 - 16 + 11.5), ALL.Y(19 + 13.5)), (ALL.X(16 + 64 + 11.5), ALL.Y(19 + 13.5))]
DRILL_AT = (ALL.X(16 + 24 + 11.5), ALL.Y(28 + 13.5))


def rx(col):
    """A column of the rig's art (RIG) as x in ALL's frame."""
    return ALL.X(col + 16)


def ry(row):
    return ALL.Y(row)


CENTRE_X = rx(35.5)          # the rig's middle
PIT = (CENTRE_X, ry(12.5), 8.6, 10.6)            # the oval pit in the top block (cols 27-44, rows 2-23)
SOCKET = (CENTRE_X, ry(37.8), 11.4)              # the round socket (cols 25-46, rows 27-48)
RECESSES = [(rx(3.6), rx(16.4), ry(45.4), ry(36.6)), (rx(54.6), rx(67.4), ry(45.4), ry(36.6))]
TOP_Z, LOW_Z = 12.5, 9.5     # the middle block's top over the pit and over the socket
FLOOR_Z = 0.4


def wing_z(x, y):
    """The wings' pleated stone: rising from 7 at the outer edges to 11.5 by the middle block, pleats 8 pixels
    apart with their ridges at columns 7.5, 15.5, 23.5 (and the mirror image)."""
    d = abs(x - CENTRE_X)                       # 0 at the middle, 36 at the outer edges
    base = 7.0 + 4.5 * max(0.0, min(1.0, (36.0 - d) / 24.0))
    phase = ((36.0 - d) - 7.5) / 8.0            # ridges at whole numbers
    tri = 1.0 - 2.0 * abs(phase - math.floor(phase + 0.5))   # 1 on a ridge, -1 in a valley
    return base + 1.9 * math.copysign(abs(tri) ** 0.7, tri)


def body_z(x, y):
    d = abs(x - CENTRE_X)
    if d < 12.2:
        t = kit.smoothstep(ry(27.0), ry(23.0), y)
        return LOW_Z + (TOP_Z - LOW_Z) * t
    return wing_z(x, y)


def _ellipse_poly(cx, cy, rx_, ry_, count=48):
    return kit.ellipse(cx, cy, rx_, ry_, count)


def rig_parts():
    """The rig itself (in ALL's frame)."""
    f = RIG
    # The outline: every pixel of rows 0-46 (the claws below are parts of their own); holes for the pit, the socket
    # and the recesses.
    outer = kit.polys_of(f, lambda v, c, r: r <= 46, smooth=2, epsilon=0.4)
    shift = rx(0) - f.X(0)   # RIG's x to ALL's
    dy = ry(0) - f.Y(0)
    outer = [[(x + shift, y + dy) for x, y in p] for p in outer]
    holes = [_ellipse_poly(PIT[0], PIT[1], PIT[2], PIT[3]), _ellipse_poly(SOCKET[0], SOCKET[1], SOCKET[2], SOCKET[2])]
    for x0, x1, y0, y1 in RECESSES:
        holes.append([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
    body = kit.heightfield("body", outer + holes, lambda x, y, e: 0.6 + (body_z(x, y) - 0.6) * e, None, spacing=0.85,
                           smooth_angle=40, edge=1.6)
    # The pale stone in the sprite's tans (its shades a little smoothed), the dark seams and edges kept.
    # (Its dark outline replaced by the stone inside it, so that the walls take the stone's colour.)
    outline = {v for row in ALL.g for v in row if v is not None and (v & 15) <= 1}
    painted = kit.frame("RIG_ALL", 104, (52, 28)).fill(outline)
    paint = kit.RampPainter("rig", painted, ramps={10, 11, 1}, fallback=10, blur=1, wall=1.0, under=3.0,
                            shades={10: (5, 6, 7, 8, 9, 10, 11, 12), 11: (6, 8, 10, 12), 1: (1, 2, 3, 5)},
                            finish={10: (0.1, 0.6), 11: (0.1, 0.6), 1: (0.1, 0.7)}, shift=0.6)
    paint(body)

    # The pleats' ridges: thin lighter lines along them.
    ridge = pal("rig_ridge", 0xab, metallic=0.15, roughness=0.5)
    for side in (-1, 1):
        for col, top_row, bottom_row in ((7.5, 10.0, 36.0), (15.5, 5.5, 36.0), (23.5, 2.5, 25.0)):
            # Down to the recesses (and, by the middle block, to the socket's ring).
            x = CENTRE_X + side * (36.0 - col)
            y_top, y_bot = ry(top_row) - 1.0, ry(bottom_row)
            kit.groove(f"ridge{side}_{col}", [(x, y_top), (x, (y_top + y_bot) / 2), (x, y_bot)],
                       lambda xx, yy: body_z(xx, yy) + 0.05, ridge, radius=0.38, sink=0.15, step=1.0)

    dark = pal("rig_dark", 0x01, metallic=0.1, roughness=0.85)
    # The pit's floor and a lip round it.
    k.slab("pit_floor", _ellipse_poly(PIT[0], PIT[1], PIT[2] + 0.3, PIT[3] + 0.3), 0.0, FLOOR_Z, dark)
    lip = pal("rig_lip", 0xa9, metallic=0.2, roughness=0.45)
    kit.torus("pit_lip", (PIT[0], PIT[1], TOP_Z + 0.2), PIT[2] + 0.6, 0.75, lip, 48, 10, squash=0.8,
              scale_y=(PIT[3] + 0.6) / (PIT[2] + 0.6))
    # The socket: a dark well ringed with grey steel, lights glowing deep in it.
    k.slab("socket_floor", _ellipse_poly(SOCKET[0], SOCKET[1], SOCKET[2] + 0.3, SOCKET[2] + 0.3), 0.0, FLOOR_Z, dark)
    steel = pal("rig_steel", 0x6a, metallic=0.7, roughness=0.28)
    steel_dark = pal("rig_steel_dark", 0x66, metallic=0.7, roughness=0.32)
    ring = kit.torus("socket_ring", (SOCKET[0], SOCKET[1], LOW_Z + 0.1), SOCKET[2] + 0.6, 1.25, steel, 56, 12,
                     squash=0.9)
    kit.paint_faces(ring, lambda c, n: steel_dark if n.z < 0.2 else None)
    ember = pal("rig_ember", 0x7a, metallic=0.0, roughness=0.4, glow=1.6)
    for i, (dx, dy_) in enumerate(((-6.5, 3.0), (6.0, 4.0), (-4.0, -6.5), (7.0, -5.0))):
        w.sphere(f"socket_light{i}", (SOCKET[0] + dx, SOCKET[1] + dy_, FLOOR_Z + 0.2), (0.9, 0.9, 0.5), ember, 10, 5)
    # The recesses' floors.
    for i, (x0, x1, y0, y1) in enumerate(RECESSES):
        w.rounded_box(f"recess_floor{i}", ((x0 + x1) / 2, (y0 + y1) / 2, FLOOR_Z / 2), (x1 - x0 + 0.6, y1 - y0 + 0.6,
                      FLOOR_Z), dark, bevel=0.1)
    # The grey claws under the wings (rows 46-51, cols 6-15 and 56-65): two prongs each.
    for side in (-1, 1):
        for col in (7.5, 14.5):
            x = CENTRE_X + side * (36.0 - col)
            w.tube(f"claw{side}_{col}", [(x, ry(44.0), 2.4), (x, ry(48.0), 2.0), (x + side * 0.3 * (1 if col > 10 else -1),
                   ry(50.6), 0.8)], [1.2, 1.0, 0.45], steel, 10)
        xm = CENTRE_X + side * (36.0 - 11.0)
        w.rounded_box(f"claw_bar{side}", (xm, ry(47.0), 2.2), (8.6, 1.6, 1.6), steel_dark, bevel=0.4)


def surface(x, y):
    return body_z(x, y)


# --- The parts on it ----------------------------------------------------------------------------------------

def gun_parts(at):
    """A gun on the middle pleat of a wing: a tan barrel along y with rounded ends, an orange light round its
    middle (rows 9-10 of 235)."""
    gx, gy = at
    f = GUN
    tan = pal("gun_tan", 0xab, metallic=0.3, roughness=0.4)
    tan_dark = pal("gun_tan_dark", 0xa8, metallic=0.3, roughness=0.45)
    glow = pal("gun_light", 0x79, metallic=0.0, roughness=0.3, glow=1.6)
    y_top, y_light, y_bot = gy + f.Y(0.5), gy + f.Y(9.5), gy + f.Y(26.5)
    z = body_z(gx, gy) + 3.6
    w.lathe_axis("gun_back", [(0.0, 0.6), (0.5, 2.4), (1.5, 3.6), (3.0, 4.3), (y_top - y_light - 1.6, 4.3),
                              (y_top - y_light - 1.0, 3.6)], tan, (gx, y_top, z), (0, -1, 0), 24)
    w.lathe_axis("gun_light", [(0.0, 3.3), (0.4, 3.5), (2.0, 3.5), (2.4, 3.3)], glow, (gx, y_light + 1.2, z),
                 (0, -1, 0), 24)
    front = w.lathe_axis("gun_front", [(0.0, 3.6), (0.6, 4.4), (y_light - y_bot - 3.0, 4.4), (y_light - y_bot - 1.4, 3.6),
                                       (y_light - y_bot - 0.4, 2.2), (y_light - y_bot, 1.0)], tan, (gx, y_light - 1.0, z),
                         (0, -1, 0), 24)
    kit.paint_faces(front, lambda c, n: tan_dark if n.z < -0.2 else None)
    # Its mount down into the pleat.
    w.rounded_box("gun_mount", (gx, (y_top + y_bot) / 2 - 2.0, z / 2), (5.0, 8.0, z), tan_dark, bevel=0.8)


def hatch_parts(at, side):
    """A small tan cabinet in a recess (rows 9-17, cols 5-19 of 197), two doors with a red light in the slit."""
    hx, hy = at
    f = HATCH
    tan = pal("hatch_tan", 0xa9, metallic=0.2, roughness=0.45)
    door = pal("hatch_door", 0xa7, metallic=0.2, roughness=0.5)
    frame_dark = pal("hatch_dark", 0x11, metallic=0.2, roughness=0.6)
    red = pal("hatch_red", 0x48, metallic=0.0, roughness=0.4, glow=1.8)
    x0, x1 = hx + f.left(5) + 0.2, hx + f.right(19) - 0.2
    y0, y1 = hy + f.bottom(17) + 0.2, hy + f.top(9) - 0.2
    height = 6.0
    w.rounded_box("hatch_box", ((x0 + x1) / 2, (y0 + y1) / 2, height / 2), (x1 - x0, y1 - y0, height), tan,
                  bevel=0.6)
    xm = hx + f.X(11.5)
    for i, (a, b) in enumerate(((x0 + 1.2, xm - 0.6), (xm + 0.6, x1 - 1.2))):
        w.rounded_box(f"hatch_door{i}", ((a + b) / 2, (y0 + y1) / 2 - 0.5, height + 0.05), (b - a, y1 - y0 - 2.6, 0.7),
                      door, bevel=0.25)
    w.rounded_box("hatch_slit", (xm, (y0 + y1) / 2 - 0.5, height - 0.2), (1.2, y1 - y0 - 2.6, 1.0), frame_dark,
                  bevel=0.2)
    w.sphere("hatch_light", (xm, (y0 + y1) / 2 - 0.5, height + 0.25), (0.6, (y1 - y0 - 3.4) / 2, 0.4), red, 10, 6)


def drill_parts(at):
    """The drill: a cone with spiral flutes from the socket, pointing down the screen and into the ground."""
    dx, dy = at
    f = DRILL
    base = Vector((dx + f.X(11.5), dy + f.top(0.8), 9.5))
    tip = Vector((dx + f.X(11.5), dy + f.top(27.5), 1.0))
    axis = (tip - base)
    length = axis.length
    d = axis.normalized()
    steel = pal("drill_steel", 0x6c, metallic=0.75, roughness=0.22)
    flute = pal("drill_flute", 0x66, metallic=0.6, roughness=0.35)
    # Its half-width row by row as the sprite draws it: a rounded back, widest over rows 7-12, a cone to the tip.
    rows = [(0.8, 0.2), (1.5, 4.0), (2.5, 6.5), (3.5, 8.2), (5.0, 9.8), (7.0, 10.8), (9.5, 11.0), (12.0, 10.8),
            (14.0, 10.0), (17.0, 8.2), (20.0, 6.3), (23.0, 4.0), (25.5, 2.3), (27.5, 0.3)]
    coarse = [((r - 0.8) / (27.5 - 0.8) * length, rad) for r, rad in rows]
    profile = [(t, r) for t, r in k.profile(coarse, step=0.8)]
    body = w.lathe_axis("drill", profile, steel, tuple(base), tuple(d), 40, squash=0.75)
    # Spiral flutes: dark faces where the angle round the axis and the distance along it fall on a helix.
    side = d.cross(Vector((0, 0, 1))).normalized()
    up = side.cross(d).normalized()

    def pick(c, n):
        rel = c - base
        t = rel.dot(d)
        ang = math.atan2(rel.dot(up), rel.dot(side))
        phase = (ang / (2 * math.pi) * 3.0 + t / 5.5) % 1.0
        return flute if phase < 0.34 else None
    kit.paint_faces(body, pick)


def torch_parts(at, side):
    """A pole beside the rig with a lamp head at its top, the flame glowing on its outer side (side -1: left)."""
    tx, ty = at
    f = TORCH_L if side < 0 else TORCH_R
    tan = pal("torch_tan", 0xaa, metallic=0.25, roughness=0.45)
    tan_dark = pal("torch_tan_dark", 0xa7, metallic=0.25, roughness=0.5)
    flame = pal("torch_flame", 0x78, metallic=0.0, roughness=0.3, glow=2.0)
    core = pal("torch_core", 0x7b, metallic=0.0, roughness=0.3, glow=2.6)
    cx = tx + f.X(12.0 if side < 0 else 11.0)
    head_y = ty + f.Y(4.5)
    w.tube("torch_pole", [(cx, ty + f.Y(9.0), 5.4), (cx, ty + f.Y(17.0), 3.6), (cx, ty + f.Y(25.5), 0.8)],
           [1.2, 1.3, 1.0], tan, 12)
    w.sphere("torch_collar", (cx, ty + f.Y(10.0), 5.2), (2.1, 1.4, 1.8), tan_dark, 14, 8)
    w.sphere("torch_head", (cx, head_y, 6.0), (3.4, 4.6, 3.0), tan, 20, 10)
    w.sphere("torch_flame", (cx + side * 2.4, head_y, 6.2), (1.6, 3.6, 2.2), flame, 14, 8)
    w.sphere("torch_core", (cx + side * 3.1, head_y, 6.4), (0.8, 2.2, 1.4), core, 10, 6)


# --- Building and cutting --------------------------------------------------------------------------------------

def whole():
    rig_parts()


def everything():
    """The whole assembly with its parts (for --whole previews)."""
    rig_parts()
    for at in GUN_AT:
        gun_parts(at)
    for at, s_ in zip(HATCH_AT, (-1, 1)):
        hatch_parts(at, s_)
    for at, s_ in zip(TORCH_AT, (-1, 1)):
        torch_parts(at, s_)
    drill_parts(DRILL_AT)
    # The black egg (obsidian_egg, drawn centred in height: it lies from 3.7 under the rig's ground to 5.3 over it).
    egg = pal("egg_stand_in", 0x01, metallic=0.6, roughness=0.15)
    w.sphere("egg", (PIT[0], PIT[1], 0.8), (7.75, 12.4, 4.5), egg, 24, 12)


def rig_piece(name, col, row):
    """A piece of the rig: its sprite at (col, row) of RIG (24 x 28); the upper row keeps only its first 24 rows
    (the lower row is drawn over the rest)."""
    x0 = rx(col) - 0.5
    y1 = ry(row) + 0.5
    height = 24.0 if row == 0 else 28.0
    e = 0.01
    box = (x0 + e, x0 + 24 - e, y1 - height + e, y1 - e)
    centre = (x0 + 12.0, y1 - 14.0)
    return (name, box, centre, lambda: RIG.mask((col, col + 24, row, row + 28)))


kit.pieced("drill_rig", whole, (72, 52), [rig_piece("drill_rig_tl", 0, 0), rig_piece("drill_rig_tm", 24, 0),
                                          rig_piece("drill_rig_tr", 48, 0), rig_piece("drill_rig_bl", 0, 24),
                                          rig_piece("drill_rig_bm", 24, 24), rig_piece("drill_rig_br", 48, 24)])
kit.pieced("drill_rig_all", everything, (104, 56), [])


def at_origin(build, at):
    """A builder that builds a part at `at` (ALL's frame) and moves it to the origin."""
    def run():
        before = set(kit.meshes())
        build()
        kit.bake()
        kit.move([o for o in kit.meshes() if o not in before], -at[0], -at[1])
    return run


kit.model("rig_gun_post", mask=lambda: GUN.mask())(at_origin(lambda: gun_parts(GUN_AT[0]), GUN_AT[0]))
kit.model("rig_hatch", mask=lambda: HATCH.mask())(at_origin(lambda: hatch_parts(HATCH_AT[0], -1), HATCH_AT[0]))
kit.model("rig_drill_bit", mask=lambda: DRILL.mask())(at_origin(lambda: drill_parts(DRILL_AT), DRILL_AT))
kit.model("rig_torch_l", mask=lambda: TORCH_L.mask())(at_origin(lambda: torch_parts(TORCH_AT[0], -1), TORCH_AT[0]))
kit.model("rig_torch_r", mask=lambda: TORCH_R.mask())(at_origin(lambda: torch_parts(TORCH_AT[1], 1), TORCH_AT[1]))


if __name__ == "__main__":
    kit.run()
