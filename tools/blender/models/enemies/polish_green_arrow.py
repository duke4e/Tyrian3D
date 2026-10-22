"""The glowing green arrows of EYESPY, DREAD-NOT and (episode 6) DELI RUIN and GLACIER: sheet 5 sprites 266 (pointing
right) and 247 (pointing left), 1x1 (12 x 14 cells; the arrow in rows 3-9); top layer; enemies 349 (266) and 350 (247)
of episodes 4 and 6 (five of each over EYESPY and DREAD-NOT, two over DELI RUIN and GLACIER); armour 0, value 0; their
animation 20 frames, always running: 7 x 266, 5 x 228, 2 x 114, 6 x 228 (and 247, 209, 95 for the left one)),
polished (2026-10-22; they replace wave3_l.py's green_arrow(), a bevelled slab with a tube laid on). models.cfg: model
arrow_left / arrow_left_209 / arrow_left_95 / arrow_right / arrow_right_228 / arrow_right_114 enemies/....glb;
sprite 5 247 arrow_left yaw=0 glow=10:0.25 and sprite 5 266 arrow_right yaw=0 glow=10:0.25 (as they are), frame 5
209 arrow_left_209, frame 5 95 arrow_left_95, frame 5 228 arrow_right_228, frame 5 114 arrow_right_114.

Where they stand: pointers the levels raise for a moment at the top of the screen, pointing at what comes: EYESPY's
3820 and 5120 (a right-pointing 349 at x 140 / 120 and a left-pointing 350 at x 180 / 210, both 17 pixels down,
pointing at each other, then sent off up the screen, event 19 eyc -8), DREAD-NOT's 349 and 1249 (one, at the boss's
side as its armour is set) and 3099 (two 349 at x 100 over two 350 at x 190, rows 30 and 58), DELI RUIN's 5051 and
GLACIER's 3776 (EYESPY's pairs). Always apart, never side by side: each is an object of its own.

Twins and frames: 266 is 247 mirrored exactly (column c of the cell is column 11 - c, every index equal), and so are
228 / 209 and 114 / 95: the right arrow is the left one mirrored (x -> -x about the cell's middle). The frames only
light the arrow up, the same pixels in brighter shades of green ramp 12 and white (ramp 2's 0x2f): 247 a dark green
outline 0xc0, a line 0xc8 down the middle, the head's core 0xcb / 0xcd; 209 four shades brighter (0xc4, 0xcc, 0xcf,
its tip white); 95 the outline 0xc7, the line and the head's core white (0x2f), the head's chevron 0xcf. No other
enemy, launched ones included, shows 95, 114, 209 or 228: frame models with the frames' colours (the same geometry,
equal bounds), so the arrows pulse as the original's do.

As the sprite and its 4x upscales draw the left arrow (columns and rows of the 12 x 14 cell): its head a chevron from
the tip (column 0 of row 6) back to column 4 (rows 3-9), its shaft three rows tall (rows 5-7) from column 4 to column
11, a line down the shaft's middle (row 6) into the head; the upscales make it a green gem: the head a faceted point,
the shaft a ridged bar lit along its ridge, glowing.

Built as such a gem: one solid over the arrow's outline (polish_ring_machine.relief) whose top rises with the distance
to the outline (a roof: a ridge down the shaft's middle, a low pyramid over the head, higher than the shaft), its rim
rounded, a flat underside; cut into bands by that distance along smooth lines (the outline's shade at the rim, the
line along the ridge, the head's core and its hot middle in the head), each band glowing in its own colour (0.2-0.65:
the game's bloom and the cfg's halo add on top). Triangulated before the export (polish_k_pod.triangulate).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; origin at the
cell's centre (pixel 6, 7): column c's left edge is x = c - 6, row r's top edge y = 7 - r. The game centres them in
height on their layer.

Replaces wave3_l.py's green_arrow() (its section "# --- 5 247, 5 266: the green arrows": green_arrow() and the
model("arrow_left", 247, ...) and model("arrow_right", 266, ...) registrations, and the arrow_left, arrow_right line
of its docstring): remove them so that they don't overwrite these models.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <dir with enemy_5.png, or the sheet itself>
(each model's silhouette against its sprite), --preview <prefix> (top and 3/4 views), --only <name,...>.
"""
import os
import sys

import bpy
from mathutils import Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_deli_boss import join  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_ring_machine import ccw, chaikin, relief, round_edge  # noqa: E402

# The left arrow's outline (pixel edges, a little inside the stairs' corners where the sprite steps diagonally): the
# tip, the head's upper edge to its back (x -1), the shaft to its end (x 6), the lower half mirrored about y 0.5.
UPPER = [(-6.25, 0.5), (-5.55, 1.2), (-4.55, 2.2), (-3.55, 3.2), (-2.9, 3.95), (-1.0, 3.95), (-1.0, 2.0), (5.65, 2.0),
         (6.0, 1.65)]
AXIS_Y = 0.5
BASE, BOTTOM = 0.35, -0.55     # the outline's height (its rounded rim's foot) and the flat underside
RISE, CAP = 0.78, 1.62         # how fast the top rises with the distance to the outline, and where it stops
RIM = 0.32                     # the rim's rounding
HEAD_X = -0.9                  # the head lies left of this
# The bands by the distance to the outline: the outline's shade, the line (along the shaft's ridge and the head's
# chevron), the head's core and its hot middle.
LINE_D, CORE_D, HOT_D = 0.92, 1.36, 1.8

# The frames (left sprite, right sprite): (palette index, emission strength) of the outline, the line, the head's core,
# its hot middle. 95's line is white down the shaft (0x2f) but its head's chevron 0xcf: HEAD_LINE gives the head's.
FRAMES = [
    (247, 266, "", ((0xc0, 0.2), (0xc8, 0.42), (0xcb, 0.5), (0xcd, 0.55)), None),
    (209, 228, "_%d", ((0xc4, 0.28), (0xcc, 0.5), (0xcf, 0.58), (0x2f, 0.62)), None),
    (95, 114, "_%d", ((0xc7, 0.34), (0x2f, 0.62), (0x2f, 0.64), (0x2f, 0.65)), (0xcf, 0.58)),
]


def outline():
    lower = [(x, 2 * AXIS_Y - y) for x, y in reversed(UPPER[1:-1])]
    end = [(6.0, 1.65), (6.0, -0.65)]
    pts = UPPER[:-1] + end + lower
    return ccw(chaikin(pts, 1))


def materials(colours, head_line):
    pal = k.level_palette()
    m = {}
    keys = ("edge", "line", "core", "hot")
    for key, (index, glow) in zip(keys, colours):
        m[key] = k.material(f"arrow_{key}_{int(round(glow * 100))}", palette=index, metallic=0.1, roughness=0.25,
                            emission=pal[index], emission_strength=glow)
    if head_line is not None:
        index, glow = head_line
        m["head_line"] = k.material(f"arrow_head_line_{int(round(glow * 100))}", palette=index, metallic=0.1,
                                    roughness=0.25, emission=pal[index], emission_strength=glow)
    else:
        m["head_line"] = m["line"]
    return m


def arrow(m):
    """The left arrow: a roof over its outline, in bands by the distance to the outline."""
    def height(x, y, d):
        top = BASE + min(RISE * d, CAP)
        return BOTTOM + 0.1 + (top - BOTTOM - 0.1) * round_edge(d, RIM) if d < RIM else top

    def paint(x, y, d):
        head = x < HEAD_X
        if d < LINE_D:
            return "edge"
        if head and d > HOT_D:
            return "hot"
        if head and d > CORE_D:
            return "core"
        return "head_line" if head else "line"
    borders = [(lambda x, y, d: d, LINE_D), (lambda x, y, d: d if x < HEAD_X else 0.0, CORE_D),
               (lambda x, y, d: d if x < HEAD_X else 0.0, HOT_D), (lambda x, y, d: x, HEAD_X)]
    obj = relief("arrow", [outline()], height, m, paint=paint, side="edge", bottom=BOTTOM, spacing=0.26,
                 borders=borders, smooth_angle=38.0)
    return obj


def build_model(name, colours, head_line, mirror):
    m = materials(colours, head_line)
    obj = arrow(m)
    if mirror:
        obj.data.transform(Matrix.Scale(-1.0, 4, (1.0, 0.0, 0.0)))
        obj.data.flip_normals()
        obj.data.update()
    mk.apply(obj)
    bpy.context.view_layer.update()
    triangulate([obj])
    obj = join([obj], name)
    obj.data.name = name
    return obj


def build():
    options = k.args()
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    for left, right, suffix, colours, head_line in FRAMES:
        for base, sprite, mirror in (("arrow_left", left, False), ("arrow_right", right, True)):
            name = base + (suffix % sprite if suffix else "")
            if only and name not in only:
                continue
            k.reset()
            obj = build_model(name, colours, head_line, mirror)
            if "check" in options:
                sheet = options["check"]
                sheet = os.path.join(sheet, "enemy_5.png") if os.path.isdir(sheet) else sheet
                mk.compare("%s (5 %d)" % (name, sprite), mk.coverage([obj], 12, 14),
                           k.sprite_mask(sheet, sprite, large=False))
            bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
            mk.report(name, [obj], os.path.join(out, name + ".glb"))
            if "preview" in options:
                mk.preview(options["preview"] + name, [obj], size=(12, 14), scale=24)


if __name__ == "__main__":
    build()
