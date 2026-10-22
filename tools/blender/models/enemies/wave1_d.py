"""Batch D of the first wave of enemy models, facing the way their sprites do (models.cfg: yaw=0):

- pincer_* (sheet K 161-243): the grey pincer of FLEET and STATION, two arms with red lights and
  red coils at the jaws, which the game puts together from ten indestructible sprites. The whole
  pincer is built once and cut into the ten pieces, so they join up again in the game.
- ring_frame (sheet 3 271): the grey frame with a blue orb of BRAINIAC, DREAD-NOT and ICE EXIT.
(The tusked boss's jaw, sheet 4 128, is a piece of polish_tusk_boss.py's boss.)

Curved outlines come from the sprites' pixels (wave1_d_art.py) and get their volume by inflation
(wave1_d_shapes.py): rounded like tubes or like pillows, holes and all.

usage: blender -b --factory-startup -P wave1_d.py -- [--only name,name] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--assembled <prefix>]
--preview renders <prefix><name>_top.png and _3q.png for each model; --check prints each model's
silhouette overlap with its sprite; --assembled renders the whole pincer (<prefix>pincer_top.png).
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
import wave1_d_art as art  # noqa: E402
import wave1_d_shapes as sh  # noqa: E402

OUT = os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "enemies")
MODELS = []  # (name, builder, sheet, sprite)


def model(name, sheet, sprite):
    def register(fn):
        MODELS.append((name, fn, sheet, sprite))
        return fn
    return register


def lathe_x(name, profile, mat, segments=24, y=0.0, z=0.0, squash=1.0):
    """A round part along X: profile is (x, radius) pairs in increasing x."""
    obj = k.lathe(name, profile, mat, segments=segments, squash=squash)
    # Built along Y: turn so that +Y becomes +X, then place.
    obj.data.transform(Matrix.Rotation(math.radians(-90), 4, "Z"))
    obj.data.transform(Matrix.Translation((0.0, y, z)))
    return obj


# --- The pincer (sheet K) ------------------------------------------------------------------------

# The art is 96 x 84 pixels; its centre is the model's origin while it is built.
CLAW_ORIGIN = (48, 42)
# The pieces: sprite, name, the left and top of the sprite in the art (pixels).
CLAW_PIECES = [
    (161, "pincer_l_hook", 0, 0),
    (163, "pincer_l_tubes", 24, 0),
    (199, "pincer_l_side", 0, 28),
    (237, "pincer_l_jaw", 0, 56),
    (238, "pincer_l_coil", 12, 56),
    (165, "pincer_r_tubes", 48, 0),
    (167, "pincer_r_hook", 72, 0),
    (205, "pincer_r_side", 72, 28),
    (242, "pincer_r_coil", 60, 56),
    (243, "pincer_r_jaw", 72, 56),
]


def claw_materials():
    return {
        "hull": k.material("pincer_hull", palette=11, metallic=0.55, roughness=0.28),
        "dark": k.material("pincer_dark", palette=3, metallic=0.5, roughness=0.5),
        "light": k.material("pincer_light", palette=119, metallic=0.1, roughness=0.2, emission=(255, 40, 0),
                            emission_strength=0.6),
        "coil": k.material("pincer_coil", palette=117, metallic=0.4, roughness=0.3, emission=(255, 40, 0),
                           emission_strength=0.5),
        "core": k.material("pincer_core", palette=114, metallic=0.5, roughness=0.4),
    }


def art_x(x, mirror):
    """An x in the art's pixels (of the left arm) as model x, mirrored for the right arm."""
    return (97.0 - x if mirror else x) - CLAW_ORIGIN[0]


def art_y(y):
    return CLAW_ORIGIN[1] - y


def lathe_between(name, profile, mat, mirror, y, segments=24):
    """lathe_x with the profile's x given in the left arm's art pixels (mirrored for the right)."""
    obj = lathe_x(name, [(art_x(x, False), r) for x, r in profile], mat, segments, y=art_y(y))
    if mirror:
        obj.data.transform(Matrix.Translation((art_x(0, True) + art_x(0, False), 0, 0)) @
                           Matrix.Scale(-1, 4, (1, 0, 0)))
        obj.data.flip_normals()
    k.recalc_normals(obj)
    return k.smooth(obj, 50)


def claw_details(side, mats):
    """The parts of one arm that are better turned than inflated: the two tubes reaching
    inwards at the top (gun barrels), the red coil at the jaw and the slot light on the side."""
    mirror = side == "right"
    end = 36.0 if not mirror else 35.0  # the right arm's tubes are a pixel shorter
    parts = []
    # The thick tube: a collar where it leaves the arm, a band at the muzzle, a dark bore.
    parts.append(lathe_between(f"tube_{side}", [(19.0, 3.3), (20.0, 3.9), (end - 2.6, 3.9), (end - 2.5, 4.2),
                                                (end - 0.4, 4.2), (end, 3.8), (end + 0.01, 0.01)],
                               mats["hull"], mirror, 18.0))
    parts.append(lathe_between(f"tube_collar_{side}", [(21.0, 3.9), (21.3, 4.3), (23.2, 4.3), (23.5, 3.9)],
                               mats["hull"], mirror, 18.0))
    parts.append(lathe_between(f"bore_{side}", [(end - 1.0, 2.6), (end + 0.08, 2.6), (end + 0.09, 0.01)],
                               mats["dark"], mirror, 18.0, segments=20))
    # The thin tube above it.
    parts.append(lathe_between(f"rod_{side}", [(17.5, 1.2), (18.0, 1.45), (end - 0.4, 1.45), (end, 1.15),
                                               (end + 0.01, 0.01)], mats["hull"], mirror, 9.5, segments=16))
    # The coil: a dark core, a collar against the jaw and five ribs.
    parts.append(lathe_between(f"coil_core_{side}", [(24.3, 2.4), (34.6, 2.4), (35.0, 1.6), (35.01, 0.01)],
                               mats["core"], mirror, 76.5, segments=20))
    parts.append(lathe_between(f"coil_collar_{side}", [(24.0, 4.0), (24.4, 4.6), (26.5, 4.6), (27.0, 3.4)],
                               mats["coil"], mirror, 76.5))
    for i in range(5):
        cx = 26.5 + 2 * i
        parts.append(lathe_between(f"rib{i}_{side}", [(cx - 0.45, 2.6), (cx - 0.35, 3.4), (cx + 0.35, 3.4),
                                                      (cx + 0.45, 2.6)], mats["coil"], mirror, 76.5))
    # The slot light on the inner side (the red strip at art x 9-11, rows 42-52).
    cx = art_x(10.5, mirror)
    light = k.ellipsoid(f"slot_light_{side}", (cx, art_y(47.5), 0.4), (1.7, 5.7, 2.0), mats["light"], 24, 14)
    parts.append(k.smooth(light, 60))
    return parts


def slot_hole(mirror):
    """The hole in the arm the slot light sits in: an ellipse a little smaller than the light, whose
    rim tucks under the arm's edge."""
    cx, cy = art_x(10.5, mirror), art_y(47.5)
    return [(cx + 1.55 * math.cos(2 * math.pi * i / 32), cy + 5.5 * math.sin(2 * math.pi * i / 32)) for i in range(32)]


def build_claw():
    """The whole pincer, centred on the art's centre. Returns its objects."""
    mats = claw_materials()
    rows = sh.art(art.CLAW)
    # The arms without the slot lights and the straight parts of the tubes (turned instead).
    hull_rows = [list(row) for row in rows]
    for r, chars in enumerate(hull_rows):
        for c, ch in enumerate(chars):
            if 8 <= r <= 21 and 22 <= c < 75:
                chars[c] = "."
            elif ch == "r" and 40 <= r <= 53:
                chars[c] = "#"
            elif 70 <= r <= 73 and (23 <= c <= 28 or 68 <= c <= 73) and ch == "#":
                chars[c] = "."  # the collar's outline: the collar is turned
    # The thin outline between the jaws' lights and the outside belongs to the lights.
    at = lambda c, r: hull_rows[r][c] if 0 <= r < len(hull_rows) and 0 <= c < len(hull_rows[r]) else "."
    edge = [(c, r) for r in range(61, 75) for c in list(range(13, 25)) + list(range(72, 84))
            if at(c, r) == "#" and any(at(c + dc, r + dr) == "r" for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            and any(at(c + dc, r + dr) == "." for dc in (-1, 0, 1) for dr in (-1, 0, 1))]
    for c, r in edge:
        hull_rows[r][c] = "r"
    hull_rows = ["".join(chars) for chars in hull_rows]
    objects = []
    hull = sh.outlines(hull_rows, "#", CLAW_ORIGIN, smooth=3, epsilon=0.8)
    lights = sh.outlines(hull_rows, "r", CLAW_ORIGIN, smooth=2, epsilon=0.4)
    for side in ("left", "right"):
        mine = [p for p in hull if (sum(x for x, _ in p) / len(p) < 0.5) == (side == "left")]
        mine.append(slot_hole(side == "right"))
        objects.append(sh.inflate(f"hull_{side}", mine, mats["hull"], sh.round_profile(0.9), bottom=0.7, sigma=1.8))
        objects += claw_details(side, mats)
    for i, poly in enumerate(lights):
        objects.append(sh.inflate(f"light{i}", [sh.inset(poly, -0.3)], mats["light"],
                                  sh.round_profile(1.0, min_height=0.8), bottom=0.5))
    for obj in objects:
        k.smooth(obj, 50)
    return objects


def claw_piece(name, left, top):
    objects = build_claw()
    ox, oy = CLAW_ORIGIN
    x0, x1 = left - ox, left + 24 - ox
    y0, y1 = oy - top - 28, oy - top
    kept = sh.cut_box(objects, x0, x1, y0, y1)
    sh.move(kept, -(x0 + 12), -(y0 + 14))
    for obj in kept:
        k.smooth(obj, 50)


for _sprite, _name, _left, _top in CLAW_PIECES:
    model(_name, "K", _sprite)(lambda left=_left, top=_top, name=_name: claw_piece(name, left, top))


# --- The sprites' origin -------------------------------------------------------------------------

SPRITE_ORIGIN = (12, 14)


# --- The ring frame (sheet 3 271) ---------------------------------------------------------------

def relabel(rows, boxes):
    """The art with pixels relabelled: boxes are (from chars, to char, c0, c1, r0, r1), inclusive."""
    grid = [list(r) for r in rows]
    for src, dst, c0, c1, r0, r1 in boxes:
        for r in range(r0, r1 + 1):
            for c in range(c0, c1 + 1):
                if grid[r][c] in src:
                    grid[r][c] = dst
    return ["".join(line) for line in grid]


@model("ring_frame", "3", 271)
def ring_frame():
    """The device of BRAINIAC, DREAD-NOT and ICE EXIT: a heavy grey frame round a blue orb, with
    a blue canister below it, finned posts at its upper corners and a ribbed neck at the top. It
    stands on the ground (flat underneath)."""
    rows = relabel(sh.art(art.RING), [
        ("b", "n", 7, 17, 1, 5),     # the neck's blue stripes: inlays on the frame
        ("b", "n", 1, 4, 3, 9),      # the left post's stripe
        ("b", "n", 19, 23, 3, 9),    # the right post's stripe
        ("b", "o", 9, 15, 7, 13),    # the orb
        ("b", "c", 8, 16, 19, 25),   # the canister
        ("b", "l", 3, 7, 19, 23),    # the small lights beside it
        ("b", "l", 17, 21, 19, 23),
        ("#", ".", 9, 15, 13, 14),   # the orb's dark outline below it: the orb hangs free
        ("c", "#", 16, 16, 19, 19),  # a blue pixel of the frame beside the canister
    ])
    frame_mat = k.material("ringframe_frame", palette=8, metallic=0.6, roughness=0.3)
    blue = k.material("ringframe_blue", palette=58, metallic=0.4, roughness=0.25)
    orb = k.material("ringframe_orb", palette=57, metallic=0.2, roughness=0.08, emission=(40, 120, 255),
                     emission_strength=0.15)
    light = k.material("ringframe_light", palette=57, roughness=0.2, emission=(60, 150, 255), emission_strength=0.3)
    height = 4.5
    frame = sh.outlines(rows, "#n", SPRITE_ORIGIN, smooth=0, epsilon=0.6)
    frame_obj = sh.inflate("frame", frame, frame_mat, sh.pillow_profile(height, 1.1), bottom=0.0, spacing=0.35)
    k.smooth(frame_obj, 45)
    # Blue inlays along the neck and the posts.
    stripes = sh.outlines(relabel(rows, [("n", "#", 7, 17, 2, 2), ("n", "#", 15, 15, 5, 5)]), "n", SPRITE_ORIGIN,
                          smooth=0, epsilon=0.3)
    for i, poly in enumerate(stripes):
        cx = sum(x for x, _ in poly) / len(poly)
        cy = sum(y for _, y in poly) / len(poly)
        z = sh.surface_z(frame_obj, cx, cy, height)
        inlay = k.slab(f"inlay{i}", sh.inset(poly, 0.12), z - 0.3, z + 0.35, blue, bevel_width=0.15)
        k.smooth(inlay, 40)
    # The orb, hanging in the ring's opening.
    k.smooth(k.ellipsoid("orb", (0.5, 3.6, 3.4), (3.55, 3.55, 3.3), orb, 32, 16), 60)
    # The canister below: a round body along Y, its end rounded, banded.
    canister = k.lathe("canister", [(-12.0, 0.01), (-11.95, 1.7), (-11.7, 2.7), (-11.2, 3.35), (-10.4, 3.65),
                                    (-6.0, 3.65), (-5.6, 3.2), (-4.0, 3.2)], blue, 28, axis_x=0.5, axis_z=2.2)
    k.smooth(canister, 50)
    for y in (-9.0, -6.6):
        band = k.lathe("band", [(y - 0.45, 3.6), (y - 0.3, 3.95), (y + 0.3, 3.95), (y + 0.45, 3.6)], frame_mat, 28,
                       axis_x=0.5, axis_z=2.2)
        k.smooth(band, 50)
    for i, poly in enumerate(sh.outlines(rows, "l", SPRITE_ORIGIN, smooth=1, epsilon=0.3, min_area=0.5)):
        k.smooth(sh.inflate(f"light{i}", [sh.inset(poly, -0.3)], light, sh.round_profile(1.0, min_height=1.0),
                            bottom=0.0, base=1.2, spacing=0.25), 50)


# --- Main ----------------------------------------------------------------------------------------

def main():
    options = k.args()
    only = set(options["only"].split(",")) if "only" in options else None
    for name, build, sheet, sprite in MODELS:
        if only and name not in only:
            continue
        k.reset()
        build()
        if "check" in options:
            print(f"--- {name} (sheet {sheet} sprite {sprite})")
            k.check_silhouette(os.path.join(options["check"], f"enemy_{sheet}.png"), [sprite])
        k.export(os.path.join(OUT, name + ".glb"))
        if "preview" in options:
            k.preview(options["preview"] + name, (24, 28))
    if "assembled" in options:
        k.reset()
        build_claw()
        k.preview(options["assembled"] + "pincer", (96, 84), scale=8)
        # A three-quarter view from farther away, for the whole pincer.
        scene = bpy.context.scene
        cam = bpy.data.objects["3q"]
        cam.location = Vector((38, -48, 42)) * 3.2
        scene.camera = cam
        scene.render.resolution_x, scene.render.resolution_y = 1024, 768
        scene.render.filepath = options["assembled"] + "pincer_3q.png"
        bpy.ops.render.render(write_still=True)


main()
