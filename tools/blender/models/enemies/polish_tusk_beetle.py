"""The golden beetle of SOH JIN and MISTAKES (sheet G sprite 49, 2x2: 24 x 28 pixels; episode 2's enemy 778, on the
ground; its animation closes its tusks and horns: 49 49 49 51 51 51 53 53 53 51 51 51), polished (2026-10-21; it
replaces wave3_r_beasts.py's tusk_beetle() and wave3_at_g.py's tusk_beetle_<sprite> frames). models.cfg: sprite g 49
tusk_beetle yaw=0, frame g 51 tusk_beetle_51, frame g 53 tusk_beetle_53 (all three unchanged). No other enemy shows
these sprites; they are no other sprites' pixels mirrored or in other ramps.

As the sprite and its 4x upscale draw it (columns and rows of the 24 x 28 cell): a beetle of polished gold and bronze
(the brown ramp 1) in a dark outline, symmetric about the middle of column 12. Its carapace (columns 8-16 of rows
0-12) is a shield with a straight top edge (row 0), its sides round, a keel down its middle that catches the light
(column 12, the sprite's whitest pixels), its right flank in shadow; below the side plates it narrows to a point
between the tusks' roots (column 12 of row 13). From its upper sides two horns sweep up and out to points at the
top corners (columns 2 and 22 of row 0), broad at the root (rows 5-8), lit along their outer edges. Under each
horn a leaf-shaped plate (columns 4-8 and 16-20 of rows 8-11, the left one bright), a dark notch between it and the
carapace's lower part (columns 8-10 of row 11). From under the carapace two long tusks run down and out (rows 12-18),
straight down (rows 19-24) and curl in to their points (columns 8 and 16 of row 27), round an open ring.
The frames close the tusks and horns (frame for frame as the sprites draw them): in 51 the tusks and the upper
horns (rows 0-7) are a pixel further in; in 53 the tusks two pixels, the horns' middles (rows 5-7) a pixel and
their upper parts (rows 0-4) two, so that their tips, still on row 0, are two pixels in. The carapace and the
plates don't change.

Built from lofts (tyrkit): the carapace a loft of rounded sections with a crest, its top end rounded off, a raised
keel bar along the crest that catches the light; the horns, the plates and the tusks tapering tubes along curved
paths (polish_twin_claw.horn), the horns rising a little to their tips, the plates short leaves from the carapace's
sides out and down to points, the tusks sinking to the ground along their curves. The left half is built about u = 0
and mirrored (the beetle's middle is x = 0.5). The frames slide the tusks across and slide and bend the horns
across (the bend grows from row 6 to rows 2-3), so every frame model has the same bounds in height and the game,
which centres the models in height, keeps them in place. It stands on z = 0 (the tusks' lower curves touch it).
Every mesh is triangulated before the export (polish_k_pod.triangulate), so --check doesn't change the output.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; origin at the
sprite's centre (pixel 12, 14): column c is x = c + 0.5 - 12, row r is y = 13.5 - r.

Replaces wave3_r_beasts.py's tusk_beetle() (its "# --- G 49: the tusked beetle" section with the
@r.model("tusk_beetle", [(49, True)]) registration and its docstring lines; wave3_r_art.py's BEETLE, which nothing
reads) and wave3_at_g.py (its tusk beetle frames are all that is left in it: delete the file; nothing imports it):
remove them so that they don't overwrite these models.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each frame's silhouette
against its sprite in enemy_G.png), --preview <prefix>, --only <name,...>.
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_redjet import Curve  # noqa: E402
from polish_twin_claw import horn, paint_sections  # noqa: E402

AXIS_X = 0.5            # the beetle's middle (column 12); u = x - AXIS_X

# The carapace along y: its half-width in plan, the height of its top and of its underside, the keel's rise (its
# outline through the middles of the sprite's steps: columns 8-16 with their outline, row 0's corners cut).
CARAPACE = Curve([
    (-0.7, 0.25, 2.6, 2.1, 0.0),
    (0.2, 0.9, 3.3, 1.8, 0.15),
    (0.9, 1.35, 3.8, 1.6, 0.25),
    (1.7, 2.0, 4.4, 1.3, 0.4),
    (2.8, 3.3, 5.1, 1.1, 0.55),
    (4.2, 4.25, 5.6, 1.0, 0.65),
    (6.5, 4.6, 6.0, 1.0, 0.7),
    (9.5, 4.7, 6.25, 1.0, 0.7),
    (12.0, 4.65, 6.2, 1.1, 0.65),
    (13.0, 4.3, 5.95, 1.3, 0.5),
])
CARAPACE_Y = (-0.7, 13.0)
CARAPACE_TOP_ROUND = 0.75       # the top end's rounding (rows 0-1)
KEEL_Y, KEEL_RADIUS = (1.6, 12.85), 0.42   # the keel along the crest (column 12 of rows 1-12)
CARAPACE_POWER = 2.4
# The left horn's middle line from its root (inside the carapace) to its tip: (u, y, z, half-width in plan,
# half-height); its pivot for the frames (u, y).
HORN = [(-3.2, 5.5, 3.7, 2.05, 1.4), (-4.7, 6.3, 3.95, 2.15, 1.4), (-6.1, 7.4, 4.2, 2.0, 1.3),
        (-7.45, 8.7, 4.45, 1.72, 1.12), (-8.55, 10.1, 4.7, 1.4, 0.92), (-9.35, 11.5, 4.9, 1.05, 0.72),
        (-9.85, 12.75, 5.0, 0.62, 0.45), (-10.05, 13.75, 5.05, 0.12, 0.12)]
HORN_BEND = (7.5, 11.0)         # the frames bend the horn in from this y, fully at the second (rows 6 and 2-3)
# The left plate under the horn (columns 4-8 of rows 8-11), a leaf from the carapace's side out and down to its
# point: its middle line (u, y, z, half-width in plan, half-height).
PLATE = [(-3.6, 4.9, 2.7, 1.35, 0.95), (-5.0, 4.3, 2.65, 1.95, 1.15), (-6.35, 3.3, 2.3, 1.9, 1.05),
         (-7.2, 2.25, 1.85, 1.2, 0.7), (-7.45, 1.45, 1.55, 0.15, 0.15)]
# The left tusk's middle line from under the carapace to its point: (u, y, z, half-width in plan, half-height).
TUSK = [(-2.2, 2.2, 2.75, 1.55, 1.45), (-3.15, -0.2, 2.65, 2.05, 1.7), (-4.35, -2.4, 2.45, 2.4, 1.82),
        (-5.5, -4.4, 2.2, 2.35, 1.78), (-6.2, -6.4, 1.95, 2.15, 1.66), (-6.45, -8.4, 1.7, 1.92, 1.52),
        (-6.25, -10.3, 1.42, 1.65, 1.32), (-5.5, -12.0, 1.1, 1.3, 1.02), (-4.3, -13.1, 0.78, 0.85, 0.66),
        (-3.0, -13.6, 0.55, 0.12, 0.12)]

# The frames: (model, sprite, the tusks moved in by, the horns moved in by, their upper parts bent in by as well).
FRAMES = [("tusk_beetle", 49, 0.0, 0.0, 0.0),
          ("tusk_beetle_51", 51, 1.0, 1.0, 0.0),
          ("tusk_beetle_53", 53, 2.0, 1.0, 1.0)]


def materials():
    def gold(name, index, metallic=0.55, roughness=0.28):
        return k.material(name, palette=index, metallic=metallic, roughness=roughness)
    return {
        "shell": gold("tsk_shell", 0x18),
        "keel": gold("tsk_keel", 0x1c, 0.5, 0.2),
        "flank": gold("tsk_flank", 0x15, 0.5, 0.34),
        "dark": gold("tsk_dark", 0x12, 0.4, 0.5),
        "horn": gold("tsk_horn", 0x19, 0.55, 0.26),
        "plate": gold("tsk_plate", 0x1b, 0.5, 0.26),
        "tusk": gold("tsk_tusk", 0x18, 0.55, 0.24),
        "tusk_light": gold("tsk_tusk_light", 0x1b, 0.5, 0.2),
    }


# --- The parts (the left half about u = 0) -----------------------------------------------------------------------

def carapace(m):
    """The shield: rounded sections with a keel, from its point between the tusks to its rounded top end."""
    y0, y1 = CARAPACE_Y
    ys = [y0 + (y1 - y0) * (i / 30) ** 1.15 for i in range(31)]
    rings = []
    for y in ys:
        hw, top, under, crest = CARAPACE(y)
        zc = under + 0.35
        rings.append(k.ring(y, max(hw, 0.08), 1.0, 40, z=zc, top=max(top - zc - crest, 0.1), bottom=0.35,
                            power=CARAPACE_POWER, crest=crest))
    # The top end, rounded off (row 0's corners).
    hw, top, under, crest = CARAPACE(y1)
    zc = under + 0.35
    for q in (0.3, 0.6, 0.85):
        a = q * math.pi / 2
        shrink = CARAPACE_TOP_ROUND * (1 - math.cos(a))
        y = y1 + CARAPACE_TOP_ROUND * math.sin(a) * 0.9
        rings.append(k.ring(y, hw - shrink * 1.6, 1.0, 40, z=zc, top=max(top - zc - crest - shrink * 1.4, 0.1),
                            bottom=0.35, power=CARAPACE_POWER, crest=crest * (1 - q * 0.5)))
    obj = k.loft("carapace", rings, m["shell"], start_point=(0.0, y0 - 0.1, 2.2),
                 end_point=(0.0, y1 + CARAPACE_TOP_ROUND * 0.95, top - 0.9))
    k.smooth(obj, 50)

    mk.paint(obj, lambda c, n: m["dark"] if n.z < -0.2 else m["flank"] if n.z < 0.35 else None)
    # The keel down its middle, catching the light (the sprite's column 12).
    k0, k1 = KEEL_Y
    path = [Vector((0.0, y, CARAPACE(y)[1] - 0.12)) for y in [k0 + (k1 - k0) * i / 16 for i in range(17)]]
    keel = mk.tube("keel", path, KEEL_RADIUS, m["keel"], 8,
                   radii=[KEEL_RADIUS * max(0.0, min(1.0, (p.y - k0) / 1.2, (k1 - p.y) / 0.6)) ** 0.5 + 0.04
                          for p in path])
    k.smooth(keel, 60)
    return [obj, keel]


def left_horn(m):
    obj, centres = horn("horn_l", HORN, m["horn"], 16)

    def pick(c, n):
        if n.z < -0.2:
            return m["dark"]
        if n.z < 0.3:
            return m["flank"]
        return None
    paint_sections(obj, centres, 16, pick)
    return [obj]


def left_plate(m):
    obj, centres = horn("plate_l", PLATE, m["plate"], 16)
    paint_sections(obj, centres, 16, lambda c, n: m["dark"] if n.z < -0.2 else m["flank"] if n.z < 0.3 else None)
    return [obj]


def left_tusk(m):
    obj, centres = horn("tusk_l", TUSK, m["tusk"], 16)

    def pick(c, n):
        if n.z < -0.2:
            return m["dark"]
        if n.z < 0.32:
            return m["flank"]
        if n.z > 0.8 and n.x > -0.25:
            return m["tusk_light"]
        return None
    paint_sections(obj, centres, 16, pick)
    return [obj]


# --- Building ----------------------------------------------------------------------------------------------------

def mirrored(objects):
    """Copies of the left half's parts mirrored about u = 0 (normals flipped back outwards)."""
    out = []
    for obj in objects:
        copy = obj.copy()
        copy.data = obj.data.copy()
        copy.name = obj.name[:-2] + "_r"
        bpy.context.scene.collection.objects.link(copy)
        copy.data.transform(Matrix.Scale(-1, 4, (1, 0, 0)))
        copy.data.flip_normals()
        out.append(copy)
    return out


def smoothstep(e0, e1, x):
    t = min(1.0, max(0.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


def build_model(tusk_in, horn_in, horn_bend):
    k.reset()
    m = materials()
    middle = carapace(m)
    horn_l = left_horn(m)
    # The frame's pose: the horn moved in, its upper part bent in further (its tip keeps its height on the screen).
    for obj in horn_l:
        for v in obj.data.vertices:
            v.co.x += horn_in + horn_bend * smoothstep(HORN_BEND[0], HORN_BEND[1], v.co.y)
        obj.data.update()
    tusk_l = left_tusk(m)
    for obj in tusk_l:
        obj.data.transform(Matrix.Translation((tusk_in, 0.0, 0.0)))
    left = horn_l + left_plate(m) + tusk_l
    parts = middle + left + mirrored(left)
    for obj in parts:
        obj.data.transform(Matrix.Translation((AXIS_X, 0.0, 0.0)))
    triangulate(parts)
    bpy.context.view_layer.update()
    return parts


def build():
    options = k.args()
    out = mk.outdir(options)
    only = set(options["only"].split(",")) if "only" in options else None
    for name, sprite, tusk_in, horn_in, horn_bend in FRAMES:
        if only and name not in only:
            continue
        parts = build_model(tusk_in, horn_in, horn_bend)
        if "check" in options:
            sheet = os.path.join(options["check"], "enemy_G.png")
            mk.compare("%s (G %d)" % (name, sprite), mk.coverage(parts, 24, 28), k.sprite_mask(sheet, sprite))
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        mk.report(name, parts, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, parts, distance=0.7)


if __name__ == "__main__":
    build()
