"""TYRIAN's small copy of the tusked boss flying up the screen (sky; episode 1's enemies 468-473, not to be shot; the
level's events at t 5000, type 18 from the bottom: 468-470 = 4 81 83 85 at x 100, 124, 148, 24 pixels above 471-473
= 4 119 121 123 at the same x), polished (2026-10-21; it replaces wave3_ab_boss.py's build_small() and its six
small_piece()s). models.cfg (as before): model tusk_boss_small_<sprite> enemies/tusk_boss_small_<sprite>.glb origin;
sprite 4 <sprite> tusk_boss_small_<sprite> yaw=0. The sprites are still (one frame each); no other enemy shows them.

The sprites draw the boss at half its size and turned round, its tusks up the screen, lit (as every sprite) from the
upper left; as wave3_ab_boss.py did, the model is polish_tusk_boss.py's whole boss (its builders, unchanged), scaled
by a half and turned by 180 degrees about the vertical, its axis (x 0.5) moved to x -5, in the sheet's frame of the
six sprites (72 x 56: the upper row's centres at y 14, the lower row's at y -14). Turning it turned its painted light
round too, so its faces are painted again by how they face the light from the upper left (each material family by
its own rule: gold, steel, red, the glossy black, the brown tusks; the lamps and the cuts' dark kept). The game draws
the lower row 24 pixels under the upper one (not 28): the upper pieces keep their sprites' first 26 rows (y 2..28),
the lower ones their last 26 (y -28..-2), so that drawn 24 apart they meet (the model's middle 4 rows left out, as
before). The pieces are cut as polish_tusk_boss.py's (polish_arch.cut: the whole's shading across the cuts, the cuts
capped dark), each moved so that its sprite's centre is its origin; every mesh triangulated before the export.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; the sheet frame's
origin is the middle of the six sprites (72 x 56).

Replaces wave3_ab_boss.py's small copy (its "The small copy flying up the screen" section: BEETLE, build_small,
small_piece and the ab.pieced("tusk_boss_small", ...) registration, and wave3_ab_art.py's BEETLE, which only it reads;
wave3_ab_kit.py's transformed_copies is then unused: it may go too).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each piece's silhouette
against its sprite in enemy_4.png, and the whole against the six sprites as the sheet places them), --preview
<prefix>, --only <model,...>.
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_tusk_boss as tb  # noqa: E402
from polish_tusk_boss import mk, k, db  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402

# The boss at half its size, turned round, its axis (x 0.5) at x -5, in the sheet's frame of the six sprites.
SMALL = Matrix.Translation((-4.75, 0.5, 0.0)) @ Matrix.Rotation(math.pi, 4, "Z") @ Matrix.Scale(0.5, 4)
# model, sprite, the part of the whole it keeps (x0, x1, y0, y1), its sprite's centre.
PIECES = []
for i, (upper, lower) in enumerate(((81, 119), (83, 121), (85, 123))):
    cx = 24.0 * i - 24.0
    PIECES.append(("tusk_boss_small_%d" % upper, upper, (cx - 12.0, cx + 12.0, 2.0, 28.0), (cx, 14.0)))
    PIECES.append(("tusk_boss_small_%d" % lower, lower, (cx - 12.0, cx + 12.0, -28.0, -2.0), (cx, -14.0)))
PIECES.sort(key=lambda p: p[1])
LIGHT = Vector((-0.55, 0.45, 0.7)).normalized()
GLOSS = Vector((-0.35, 0.45, 0.82)).normalized()
# At half the size fewer shades do (at most 15 materials a piece): these take the next one's place.
MERGE = {"gold_light": "gold_lit", "steel_light": "steel_lit", "red_dark": "red", "black_glare": "black_mid",
         "lamp_hot": "lamp"}
# ... and fewer faces: the larger parts decimated (faces over the first number: the ratio kept).
DECIMATE = [(1200, 0.35), (500, 0.45), (220, 0.65)]


def family_pick(name, n):
    """The material a face of a family gets by how it faces the light from the upper left (the rules of
    polish_tusk_boss.py's painting, by face)."""
    d = n.dot(LIGHT)
    if name.startswith("tusk_gold"):
        return "gold_light" if d > 0.9 else "gold_lit" if d > 0.64 else "gold" if n.z > 0.3 or d > 0.2 else \
            "gold_dark"
    if name.startswith("tusk_steel"):
        return "steel_light" if d > 0.92 else "steel_lit" if d > 0.6 else "steel" if n.z > 0.3 or d > 0.2 else \
            "steel_dark"
    if name.startswith("tusk_red"):
        return "red_lit" if d > 0.7 else "red" if d > 0.2 else "red_dark"
    if name.startswith("tusk_brown"):
        return "brown_lit" if d > 0.72 else "brown"
    if name.startswith("tusk_black"):
        g = n.dot(GLOSS)
        return "black_glare" if g > 0.975 else "black_mid" if g > 0.86 else "black"
    return None


def repaint(objects, m):
    by_name = {mat.name: key for key, mat in m.items()}
    for obj in objects:
        mesh = obj.data
        names = [mm.name if mm is not None else "" for mm in mesh.materials]
        slots = {}
        for poly in mesh.polygons:
            if poly.material_index >= len(names):
                continue
            pick = family_pick(names[poly.material_index], poly.normal) or by_name.get(names[poly.material_index])
            if pick is None:
                continue
            pick = MERGE.get(pick, pick)
            if pick not in slots:
                slots[pick] = mk.slot_of(obj, m[pick])
            poly.material_index = slots[pick]
    db.drop_unused(objects)


def decimate(objects):
    """The larger parts with fewer faces (Blender's collapse decimation, the same every run)."""
    for obj in objects:
        faces = len(obj.data.polygons)
        for limit, ratio in DECIMATE:
            if faces > limit:
                mod = obj.modifiers.new("decimate", "DECIMATE")
                mod.decimate_type = "COLLAPSE"
                mod.ratio = ratio
                mk.apply(obj)
                break


def whole_mask(sheet):
    """The six sprites as the sheet places them (72 x 56: the rows 28 apart)."""
    mask = [[False] * 72 for _ in range(56)]
    for i, (upper, lower) in enumerate(((81, 119), (83, 121), (85, 123))):
        for row, sprite in ((0, upper), (28, lower)):
            part = k.sprite_mask(sheet, sprite)
            for y in range(28):
                for x in range(24):
                    if part[y][x]:
                        mask[row + y][24 * i + x] = True
    return mask


def build_whole():
    whole, m = tb.build_whole()
    for obj in whole:
        mk.apply(obj)
        obj.data.transform(SMALL)
        obj.data.update()
    bpy.context.view_layer.update()
    repaint(whole, m)
    decimate(whole)
    for obj in whole:
        k.smooth(obj, 50)
    bpy.context.view_layer.update()
    return whole, m


def build():
    k.reset()
    options = k.args()
    whole, m = build_whole()
    print("whole small boss: %d triangles, %d objects" % (mk.triangles(whole), len(whole)))
    sheet = os.path.join(options["check"], "enemy_4.png") if "check" in options else None
    if sheet:
        mk.compare("whole small (4 81 83 85 above 119 121 123, as the sheet places them)", mk.coverage(whole, 72, 56),
                   whole_mask(sheet))
    bpy.context.scene.view_settings.view_transform = "Standard"
    if "preview" in options:
        mk.preview(options["preview"] + "tusk_boss_small_whole", whole, size=(72, 56), scale=10, distance=2.0)
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    for name, sprite, box, centre in PIECES:
        if only and name not in only:
            continue
        parts = [p for p in (db.cut(src, box, m["core"]) for src in whole) if p is not None]
        db.drop_unused(parts)
        mk.transform(parts, Matrix.Translation((-centre[0], -centre[1], 0)))
        bpy.context.view_layer.update()
        triangulate(parts)
        parts = [db.join(parts, name)]
        for src in whole:
            src.hide_render = True
        if sheet:
            mk.compare("%s (4 %d)" % (name, sprite), mk.coverage(parts, 24, 28), k.sprite_mask(sheet, sprite))
        mk.report(name, parts, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, parts)
        for obj in parts:
            bpy.data.objects.remove(obj)
        for src in whole:
            src.hide_render = False


if __name__ == "__main__":
    build()
