"""A link of BRAINIAC's and GRAVITRON's chain of red brains in steel clamps (sheet 5 sprite 168, 2x2: columns
5-20 of the 24 x 28 cell, all its rows; static; top layer; enemy 520: 9 in BRAINIAC, 16 in GRAVITRON),
polished (2026-10-19; it replaces wave3_l.py's red_link()). models.cfg: sprite 5 168 red_link yaw=0.

The levels stack the links down the screen: one at x 120 every 28 of the event clock (BRAINIAC's events
808-976, seven links, and 6856-6884; GRAVITRON's 4583-4611, 4874-5042 and 5426-5594), which on BRAINIAC's top
layer, scrolling a pixel a tick, puts each link's top against the bottom of the one above. Nothing else is
placed against them (the brain clamps, 5 166, lie in rows across the screen at other times and places). So
the sprite's ends are half brackets: its rows 24-27 and the next link's rows 0-3 make one steel bracket over
the seam (columns 7-15).

The link is brain_clamp's (polish_brain_clamp.py, 5 166) turned on end, and drawn in the same style: the
same red lobes folded together (the sprite's ramp 7), glowing orange along the middle lobe's top edge (row
11) and down its left side (column 10), an orange eye on the upper lobe (columns 13-14 of rows 6-7), and
blue-grey steel (ramp 6): a rail from the top bracket down the middle (column 11, rows 0-7) ending in a hook
to the left and down (row 7, column 7); two rails from the bottom bracket up (columns 11 and 13, rows 19-27),
the right one bending at row 19 and running up column 15 to a plate clamped over the right side (columns
15-21 of rows 11-14), which bends down over the brain's edge.

The brain, the eye, the rails and the plate are polish_brain_clamp.py's builders (brain(), eye(), rail(),
strap()), which read their layout from that module: this link's is swapped in while they run (layout()),
and they make the same materials, heights and shading. The bracket is this script's own (a block over the
seam rather than an arch, as the sprite draws it), built with polish_ring_machine.py's relief() like
brain_clamp's, whole over the seam at y = 14 and cut there with polish_tank_pod.py's cut() (which keeps the
uncut shading): the part below the seam is this link's top end, the part above it, moved 28 pixels down,
its bottom end, so that stacked links meet into one bracket.

Origin at the sprite's centre (pixel 12, 14); +Y up the sprite, +Z towards the camera. Points are given as
(column, row) of the sprite.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <dir with enemy_5.png, or the
sheet itself> (the silhouette), --preview <prefix>, --chain <prefix> (three stacked, as the levels place them:
<prefix>_top.png and _3q.png).
"""
import contextlib
import os
import sys

import bpy
from mathutils import Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_brain_clamp as clamp  # noqa: E402
from polish_ring_machine import ccw, chaikin, relief, round_edge  # noqa: E402
from polish_sphere_nozzle import smoothstep  # noqa: E402
from polish_tank_pod import cut  # noqa: E402

# This link's layout for polish_brain_clamp.py's builders (their names there; see that script for what each
# holds). The brain's outline (column, row), under the brackets at its ends: rows 3.6-24.4, columns 5-20.
LAYOUT = {
    "BRAIN": [(7.0, 3.6), (12.0, 3.5), (16.0, 3.6), (18.4, 4.1), (19.5, 4.9), (20.0, 6.2), (20.05, 9.5),
              (20.05, 15.0), (20.0, 21.5), (19.5, 23.1), (18.4, 23.9), (16.0, 24.4), (12.0, 24.5), (7.0, 24.4),
              (6.0, 23.3), (5.25, 22.0), (4.95, 19.0), (4.95, 9.0), (5.2, 5.9), (5.9, 4.7)],
    # The lobes (name, column, row, half-width, half-height (rows), height): three across the top (the eye
    # on the middle one), folded off at row 10 from the glowing middle lobe, a tall one down the left, one
    # under the plate, and two at the bottom, the middle one folded off at row 18.
    "LOBES": [
        ("UL", 8.0, 7.1, 2.6, 3.1, 3.3),
        ("UC", 13.3, 6.6, 2.4, 3.0, 3.55),
        ("UR", 17.6, 7.2, 2.3, 3.2, 3.2),
        ("MC", 11.9, 14.4, 2.2, 3.6, 3.85),
        ("ML", 7.4, 16.6, 2.6, 6.0, 3.6),
        ("MR", 17.9, 12.4, 2.6, 2.4, 3.0),
        ("LM", 12.6, 21.4, 2.5, 2.7, 3.1),
        ("LR", 17.5, 19.2, 2.5, 4.5, 3.5),
    ],
    "BRIGHT": ("MC", "LR"),
    # The glow: across the middle lobe's top (row 11, columns 8-13) and down its left side (column 10, rows
    # 11-17), widest where they meet.
    "GLOW": [((8.3, 11.45), (10.55, 11.5), 0.3, 0.66), ((10.55, 11.5), (12.9, 11.45), 0.66, 0.3),
             ((10.5, 11.6), (10.55, 17.6), 0.66, 0.32)],
    "EYE": (14.0, 7.0, 1.1),
}
# The rails (paths of (column, row)): down from the top bracket, the hook, up from the bottom bracket (the
# right one bending at row 19 up column 15 to the plate); their ends inside the brackets.
RAILS = [
    [(11.0, 1.0), (11.0, 4.0), (11.0, 7.45)],
    [(11.0, 7.5), (9.6, 7.5), (8.1, 7.55), (7.6, 8.2), (7.55, 9.9)],
    [(11.0, 18.9), (11.0, 22.0), (11.0, 27.0)],
    [(15.5, 13.6), (15.5, 16.4), (15.45, 18.7), (15.0, 19.3), (13.95, 19.4), (13.45, 19.9), (13.45, 22.5),
     (13.45, 27.0)],
]
# The plate clamped over the right side (columns 15-21 of rows 11-14), lying on the brain and bending
# down over its edge (polish_brain_clamp.py's strap()).
PLATE = [(14.8, 10.7), (20.3, 10.65), (20.95, 11.2), (21.0, 13.9), (20.4, 14.45), (14.8, 14.45)]
# The bracket over the seam between two links (column, rows from the seam: negative up into the link
# above): a block (columns 7-16), its edges rounded as brain_clamp's bracket, its top falling away towards
# its right side (from column 12.5 to 16, by BRACKET_FALL), which the sprite draws darker.
BRACKET = [(7.1, -3.95), (15.2, -3.95), (15.85, -3.35), (16.05, -1.8), (16.05, 1.8), (15.85, 3.35), (15.2, 3.95),
           (7.1, 3.95), (6.85, 3.3), (6.85, -3.3)]
BRACKET_FALL = 0.7


def px(c, r):
    return (c - 12.0, 14.0 - r)


@contextlib.contextmanager
def layout(**more):
    """polish_brain_clamp.py's module with this link's layout (and more) swapped in, restored afterwards."""
    values = dict(LAYOUT, **more)
    saved = {name: getattr(clamp, name) for name in values}
    for name, value in values.items():
        setattr(clamp, name, value)
    try:
        yield
    finally:
        for name, value in saved.items():
            setattr(clamp, name, value)


def bracket(mats):
    """The bracket, whole over the seam at this link's top (y = 14): a block as tall as brain_clamp's
    bracket, its edges rounded, its top lit and falling away to the right, its rim dark."""
    poly = ccw(chaikin([px(c, r) for c, r in BRACKET], 2))
    x0, x1 = px(12.5, 0)[0], px(16.0, 0)[0]

    def height(x, y, d):
        top = clamp.BRACKET_TOP - BRACKET_FALL * smoothstep(x0, x1, x)
        return 1.0 + (top - 1.0) * round_edge(d, clamp.BRACKET_RIM)

    return relief("bracket", [poly], height, mats, paint=lambda x, y, d: "steel" if d > 0.3 else "steel_dark",
                  side="steel_dark", bottom=clamp.BRACKET_BOTTOM, spacing=0.34, borders=[(lambda x, y, d: d, 0.3)],
                  band=1.3)


def build_link(mats):
    with layout():
        b = clamp.Brain()
        clamp.brain(mats, b)
        clamp.eye(mats, b)
        for i, points in enumerate(RAILS):
            clamp.rail(f"rail{i}", points, mats, b)
    with layout(STRAP=PLATE):
        clamp.strap(mats, b).name = "plate"
    whole = bracket(mats)
    # Cut at the seam: the part below it is this link's top end, the part above it (moved 28 pixels down)
    # its bottom end.
    top = cut(whole, (-100.0, 100.0, -100.0, 14.0), mats["steel_dark"])
    bottom = cut(whole, (-100.0, 100.0, 14.0, 100.0), mats["steel_dark"])
    bottom.data.transform(Matrix.Translation((0.0, -28.0, 0.0)))
    top.name, bottom.name = "bracket_top", "bracket_bottom"
    bpy.data.objects.remove(whole)


def chain_preview(prefix):
    """Three stacked, as the levels place them (renders <prefix>_top.png and _3q.png)."""
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    copies = []
    for dy in (-28.0, 28.0):
        for obj in meshes:
            copy = obj.copy()
            copy.data = obj.data.copy()
            bpy.context.scene.collection.objects.link(copy)
            copy.location.y += dy
            copies.append(copy)
    k.preview(prefix, size=(28, 84), scale=8)
    for obj in copies:
        bpy.data.objects.remove(obj)
    for obj in [o for o in bpy.context.scene.objects if o.type in ("CAMERA", "LIGHT")]:
        bpy.data.objects.remove(obj)


def build():
    options = k.args()
    outdir = options.get("outdir", os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "enemies"))
    k.reset()
    build_link(clamp.materials())
    used = {m.name for o in bpy.context.scene.objects if o.type == "MESH" for m in o.data.materials}
    print("== red_link (5 168): %d triangles, %d materials" % (clamp.triangles(), len(used)))
    if "check" in options:
        sheet = options["check"]
        k.check_silhouette(os.path.join(sheet, "enemy_5.png") if os.path.isdir(sheet) else sheet, 168)
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    path = os.path.join(outdir, "red_link.glb")
    k.export(path)
    print("%s: %d bytes" % (path, os.path.getsize(path)))
    if "chain" in options:
        chain_preview(options["chain"])
    if "preview" in options:
        k.preview(options["preview"] + "red_link")


if __name__ == "__main__":
    build()
