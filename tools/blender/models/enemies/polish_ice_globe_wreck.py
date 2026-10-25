"""What is left of the grey globe on purple legs of CAMANIS once it is destroyed (sheet 7 sprites 161 and 163 above 199
and 201: their stand-ins, what CAMANIS paints where the globe stands, before it comes, once it is shot and where none
comes; 7 of them, CAMANIS 89e6d1810ded7622), stage 4 of the clean ground (2026-10-25), built on polish_ice_globe.py.
models.cfg: model ice_globe_tl_wreck / _tr_wreck / _bl_wreck / _br_wreck enemies/ice_globe_*_wreck.glb origin; wreck 7
161 ice_globe_tl_wreck, wreck 7 163 ice_globe_tr_wreck, wreck 7 199 ice_globe_bl_wreck, wreck 7 201 ice_globe_br_wreck
(drawn with the live sprite lines' options, yaw=0 height=-4).

As CAMANIS paints it at 4x (at 552, 2381; columns and rows of the 48 x 56 picture): the same walker, its legs and armour
standing, but the steel ball smashed open: a black hole (0x20, 0x01) over most of its top (columns 10-27 of rows 5-24),
its jagged rim the shell's broken edge catching the light; the shell left round it, lit along its left (a crescent,
columns 5-10 of rows 3-24, 0x06-0x0f) and over its top (columns 12-23 of rows 2-5), dark at its right (0x01-0x0b in
shadow); a big curved piece of the shell fallen in, lying in the hole at its right (columns 19-30 of rows 11-22, 0x05-
0x0b, lit on its upper left); the purple armour a shade or two darker (0x50-0x58 where it was 0x53-0x5c), with black
between its parts.

The model: polish_ice_globe.py's walker (its build_whole(): the ball with its seams and hubs, the arms, hips, cradles,
thighs, knees, shins and feet), then broken: the ball hollowed (less an ellipsoid 0.9 smaller: its inside black, 0x01)
and its top broken off above a jagged height field (polish_panel_pills_wreck.heightfield_cutter, exact booleans; the
break's faces the steel's light 0x0c), a piece of the broken top (the cap's right part) folded down into the hole about
the rim, so the camera sees its lit outer face; the shell sooted round the hole, the armour scorched a shade or two
(polish_bronze_pump_wreck.scorch_map: its own darker shades, no new materials) by a noise field, more on the right.
Cut along the sprites' edges as the live walker (polish_arch.cut, the caps in the armour's deep shade).

Coordinates as polish_ice_globe.py's: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the ice; the whole's
origin is the corner where the four sprites meet.

Options after "--": --outdir <dir> (default assets/models/enemies), --preview <prefix>, --only <name,...>.
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
import polish_ice_globe as live  # noqa: E402
from polish_panel_pills_wreck import drop_unused, fbm, heightfield_cutter  # noqa: E402
from polish_pyramid_wreck import canonical  # noqa: E402
from polish_bronze_pump_wreck import scorch_map  # noqa: E402

PIECES = [(name + "_wreck", box) for name, _, box in live.PIECES]
# The break: its middle in plan (x, y), its height over the ball's middle and how much it wanders; the shell's wall.
BREAK_C = (live.AX - 0.5, live.YC + 1.0)
BREAK_DZ, BREAK_JAG, WALL = 9.6, 1.5, 0.9
# The piece folded in: the broken cap's part right of FOLD_X (from the axis), turned FOLD degrees about a line along y
# through its rim (FOLD_HINGE x from the axis, height over the ball's middle), then sunk.
FOLD_X, FOLD, FOLD_HINGE, FOLD_SINK = 1.5, -52.0, (9.0, 10.0), 1.2


def break_z(x, y):
    """The break's height: about BREAK_DZ over the ball's middle, jagged, lower towards the front left (where the
    painting's hole reaches farthest)."""
    u, v = x - BREAK_C[0], y - BREAK_C[1]
    tilt = 0.06 * u + 0.3 * v
    return live.ZC + BREAK_DZ + tilt + BREAK_JAG * fbm(x * 0.35 + 3.0, y * 0.35 - 1.0, 0.7, 3)


def materials(m):
    m["inside"] = k.material("globewreck_inside", palette=0x01, metallic=0.2, roughness=0.7)
    m["break"] = k.material("globewreck_break", palette=0x0c, metallic=0.45, roughness=0.3)
    return m


def remaps(m):
    """The scorch's steps: the armour into its own darker shades, the steel into its seams' and the inside's."""
    a = {"armour": ("recess", "deep"), "light": ("armour", "recess"), "recess": ("under", "deep"),
         "under": ("deep", "inside"), "deep": ("deep", "inside"), "shell": ("seam", "inside"),
         "hub": ("axle", "seam"), "axle": ("seam", "inside"), "seam": ("seam", "inside"), "break": ("hub", "seam")}
    return {m[key].name: tuple(m[x] for x in steps) for key, steps in a.items()}


def break_ball(m):
    """The ball hollowed, its top broken off; the piece of its top folded in."""
    ball = bpy.data.objects["sphere"]
    mk.apply(ball)
    inner = live.lathe_x("ball_inner", [(-(live.RX - WALL) * math.cos(math.pi * i / 18), math.sin(math.pi * i / 18))
                                        for i in range(1, 18)], m["inside"], (-(live.RX - WALL), live.RX - WALL),
                         around=30, radii=(live.RY - WALL, live.RZ - WALL))
    mk.boolean(ball, inner, "DIFFERENCE")
    span = live.RX + 2.0
    # (the cutter's grid and the piece's box are the same for both cuts)
    cap = ball.copy()
    cap.data = ball.data.copy()
    cap.name = "shell_piece"
    bpy.context.scene.collection.objects.link(cap)
    cutter = heightfield_cutter("break", live.AX - span, live.AX + span, live.YC - span, live.YC + span, 1.3,
                                break_z, live.ZC + live.RZ + 3.0, m["break"])
    mk.boolean(ball, cutter, "DIFFERENCE", keep=True)
    mk.cleanup(ball, dissolve=0.0)
    canonical(ball)
    # The piece: the cap's part right of FOLD_X, folded in about the rim.
    mk.boolean(cap, cutter, "INTERSECT")
    box = mk.box("piece_box", live.AX + FOLD_X, live.AX + span, live.YC - 7.5, live.YC + 6.5, live.ZC,
                 live.ZC + live.RZ + 4.0, m["break"])
    mk.boolean(cap, box, "INTERSECT")
    mk.cleanup(cap, dissolve=0.0)
    canonical(cap)
    hx, hz = FOLD_HINGE
    pivot = Vector((live.AX + hx, live.YC, live.ZC + hz))
    turn = (Matrix.Translation(pivot) @ Matrix.Rotation(math.radians(FOLD), 4, "Y") @ Matrix.Translation(-pivot))
    cap.data.transform(Matrix.Translation((0.0, 0.0, -FOLD_SINK)) @ turn)
    for obj in (ball, cap):
        k.smooth(obj, 50)
    return ball, cap


def burn(name):
    def armour(co):
        right = 0.25 * max(0.0, min(1.0, (co.x - live.AX) / 12.0))
        return 0.48 + right + 0.3 * fbm(co.x * 0.3 + 5.0, co.y * 0.3, co.z * 0.3, 3)

    def shell(co):
        r = math.hypot(co.x - BREAK_C[0], co.y - BREAK_C[1])
        near = max(0.0, 1.0 - max(0.0, r - 8.0) / 4.0) * max(0.0, (co.z - live.ZC) / live.RZ)
        right = max(0.0, min(1.0, (co.x - live.AX - 2.0) / 9.0))
        return 0.05 + 0.5 * near + 0.55 * right + 0.25 * fbm(co.x * 0.4, co.y * 0.4 + 2.0, co.z * 0.4, 2)
    return shell if name.startswith(("sphere", "shell_piece")) else armour


def build_whole():
    whole, m = live.build_whole()
    materials(m)
    break_ball(m)
    remap = remaps(m)
    whole = [o for o in mk.meshes() if len(o.data.polygons) > 0]
    for obj in whole:
        mk.apply(obj)
        scorch_map(obj, burn(obj.name), remap, levels=(0.3, 0.72), step=None)
    live.triangulate(whole)
    bpy.context.view_layer.update()
    return whole, m


def build():
    options = k.args()
    only = options["only"].split(",") if "only" in options else None
    k.reset()
    whole, m = build_whole()
    print("whole globe wreck: %d triangles" % mk.triangles(whole))
    bpy.context.scene.view_settings.view_transform = "Standard"
    if "preview" in options:
        mk.preview(options["preview"] + "ice_globe_wreck_whole", whole, size=(48, 56), scale=10, distance=1.9)
    for name, box in PIECES:
        if only and name not in only:
            continue
        pieces = [p for p in (live.cut(src, box, m["deep"]) for src in whole) if p is not None]
        mk.transform(pieces, Matrix.Translation((-(box[0] + box[1]) / 2, -(box[2] + box[3]) / 2, 0)))
        drop_unused(pieces)
        bpy.context.view_layer.update()
        for src in whole:
            src.hide_render = True
        mk.report(name, pieces, os.path.join(mk.outdir(options), name + ".glb"))
        if "preview" in options and options.get("pieces") == "1":
            mk.preview(options["preview"] + name, pieces)
        for obj in pieces:
            bpy.data.objects.remove(obj)
        for src in whole:
            src.hide_render = False


if __name__ == "__main__":
    build()
