"""CORAL's pale bony fish, drawn from two sprites of sheet T (2x2 each, 24 x 28 pixels; not animated;
ground2 layer), polished (2026-10-19; it replaces wave3_v_sea.py's coral fish). The levels place it as one
48 x 28 picture: enemy 1197 (T 229) at x and enemy 1198 (T 231) at x + 24 on one row, one link (CORAL's
events at 100-140, 200-240 and 400-440: files of five swimming down the screen, vy +1), and the two
halves move together (each is its own enemy, armour 6: one can be shot away before the other).
models.cfg: model coral_fish_left / coral_fish_right ... origin; sprite t 229 coral_fish_left yaw=0,
sprite t 231 coral_fish_right yaw=0. They are two halves of one fish, not mirrored enemies: the spine
runs down columns 22-25 of the picture (229's last two columns, 231's first two), and the halves are
nearly but not exactly each other's mirror image (231 is lit, 229 in shadow). No other enemy uses them.

As the sprites and the 4x upscales draw it, head down the screen, in pale greys (ramps 0 and 6, a touch
of pink, ramp 5, where the light catches the head): a forked tail at the top (columns 20-27 of rows 1-3),
a slim body narrowing behind it to a thin stalk (row 5) and widening again to the shoulders (columns
21-26 of rows 13-17); in front a broad arrowhead, the head between two thin bony fins swept out to the
sides (columns 13-35 of row 18, narrowing to the snout's point at row 26); from the fins' back edge
three bony spines a side rise and sweep back: a short one beside the body (columns 19 and 28 of rows
16-17), a longer one (columns 15-16 and 31-32 of rows 14-17) and the long outer one curving out to its
tip (columns 9 and 38 of row 11).

Built as a bony creature: the body lofted round a vertebral line, a row of vertebrae along its back
(knuckled bumps, the "skeleton" the sprites' sparse pixels suggest), a skull-like head with a ridge down
its middle, the fins thin plates lofted like wings (polish_jets.py's lifting surfaces), the spines and
the tail's tines tapering bony tubes. The sprites have no dark outline: their pixels are the fish.

The fish floats above the sea floor (its belly about 1.8 above the layer; origin models stand on their
layer). Built whole, symmetric about x = 0 (the picture's column 24: x = column + 0.5 - 24, y = 13.5 -
row; +Z towards the camera) and cut there (polish_redjet.py's method: the halves keep the whole's
shading across the cut, the cut capped in bone), each half moved so that its sprite's centre is its
origin.

Replaces wave3_v_sea.py's coral fish (FISH, fish_whole(), fish_piece() and the v.pieced("coral_fish", ...)
registration; wave3_v_art.py's FISH, which only it reads): remove them so that they don't overwrite these
models.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the
silhouettes of the whole and of each half against enemy_T.png), --preview <prefix> (each half's top and
3/4 view and the whole's).
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
from polish_jets import Curve, Plan, lifting_surface, mirrored, spaced, tube  # noqa: E402

# name, sprite, the box it covers (x0, x1, y0, y1), its sprite's centre x
PIECES = [("coral_fish_left", 229, (-24.0, 0.0, -14.0, 14.0), -12.0),
          ("coral_fish_right", 231, (0.0, 24.0, -14.0, 14.0), 12.0)]

Z = 3.4                          # the height of the body's axis (the fish floats above the floor)
# The body along y from the tail's root to the snout's point: half-width, half-height above the axis,
# below it (the sprite: the stalk at row 5, columns 22-25 along rows 6-12, 21-26 at the shoulders).
BODY = Curve([(10.5, 0.5, 0.42, 0.36), (9.8, 1.6, 1.0, 0.8), (8.7, 1.05, 0.82, 0.7), (7.6, 1.6, 1.15, 0.95),
              (5.6, 1.88, 1.35, 1.1), (2.6, 1.98, 1.45, 1.2), (1.2, 2.45, 1.62, 1.3), (0.0, 2.85, 1.8, 1.42),
              (-2.0, 3.0, 1.9, 1.5), (-4.0, 3.0, 1.9, 1.5), (-5.6, 2.8, 1.8, 1.42), (-7.4, 2.35, 1.55, 1.22),
              (-9.2, 1.8, 1.22, 0.98), (-10.7, 1.22, 0.88, 0.74), (-11.9, 0.65, 0.5, 0.42), (-12.85, 0.05, 0.05, 0.05)])
BODY_Y = (10.6, -12.95)
VERTEBRAE = spaced(8.3, -2.9, 8)  # the knuckles along the back, from the stalk to the shoulders
# The head's ridge down its middle and the brows either side (y from, to).
RIDGE_Y = (-3.4, -11.6)
# The fin (left): its back edge along row 18's top, its front edge the arrowhead's side (rows 18-26:
# columns 13, 14, 15, 17, 19, 21, 22 from the outer corner to the snout).
FIN = [(0.0, -12.3), (-1.5, -11.9), (-2.4, -11.15), (-2.9, -10.4), (-3.2, -9.65), (-4.1, -9.0), (-6.2, -8.05),
       (-8.2, -7.0), (-9.7, -6.0), (-10.7, -5.0), (-11.25, -4.3), (-11.0, -3.85), (-8.0, -3.95), (-5.0, -3.85),
       (-2.0, -3.75), (0.0, -3.7)]
# The spines (left): their paths (x, y) from the fin's back edge, how far they rise to their tips, their
# roots' radii.
SPINES = [([(-10.4, -4.3), (-11.4, -3.0), (-12.4, -1.7), (-13.2, -0.4), (-13.9, 0.8), (-14.4, 2.0), (-14.55, 3.05)],
           2.3, 0.62),
          ([(-6.9, -4.0), (-7.6, -2.9), (-8.25, -1.8), (-8.5, -0.6), (-8.55, 0.05)], 1.7, 0.52),
          ([(-4.4, -4.0), (-4.5, -3.0), (-4.55, -1.95)], 1.2, 0.45)]
# The tail's tines (left): from the tail's root to the tip (column 20 of row 1).
TINE = ([(-0.3, 9.7, 0.15), (-1.7, 10.45, 0.3), (-2.5, 11.3, 0.45), (-3.05, 12.2, 0.55), (-3.55, 13.25, 0.65)], 0.95)


def materials():
    return {
        "bone": k.material("coralfish_bone", palette=0x0a, metallic=0.25, roughness=0.32),
        "pale": k.material("coralfish_pale", palette=0x0c, metallic=0.25, roughness=0.28),
        "fin": k.material("coralfish_fin", palette=0x6a, metallic=0.2, roughness=0.3),
        "dark": k.material("coralfish_dark", palette=0x66, metallic=0.2, roughness=0.5),
        "cut": k.material("coralfish_marrow", palette=0x08, metallic=0.1, roughness=0.6),
    }


def body(m):
    """The body lofted along y, closed at the tail's root and at the snout."""
    rings = []
    ys = spaced(BODY_Y[0] - 0.15, BODY_Y[1] + 0.12, 64, dense_a=0.3, dense_b=0.4)
    for y in ys:
        hw, top, bottom = BODY(y)
        rings.append(k.ring(y, max(hw, 0.03), 1.0, 28, z=Z, top=max(top, 0.03), bottom=max(bottom, 0.03), power=2.1))
    rings.reverse()
    obj = k.loft("body", rings, m["bone"], start_point=(0, BODY_Y[1], Z), end_point=(0, BODY_Y[0], Z + 0.1))
    obj.data.materials.append(m["dark"])
    for poly in obj.data.polygons:
        if poly.normal.z < -0.3:
            poly.material_index = 1      # the belly in shadow
    return k.smooth(obj, 55)


def body_top(x, y):
    hw, top, _ = BODY(y)
    if abs(x) >= hw:
        return Z
    return Z + top * math.sqrt(1 - (x / hw) ** 2)


def vertebrae(m):
    """Knuckles along the back: each a bony bead on the body's top, a short spine raked back over it."""
    for i, y in enumerate(VERTEBRAE):
        hw, top, _ = BODY(y)
        z = body_top(0.0, y)
        size = 0.55 + 0.25 * min(1.0, hw / 2.9)
        bead = k.ellipsoid(f"vertebra{i}", (0.0, y, z - 0.15), (size * 1.15, size * 0.85, size * 0.62), m["pale"],
                           14, 7)
        k.smooth(bead, 60)
        points = [Vector((0.0, y - 0.2, z + 0.1)), Vector((0.0, y + 0.45, z + 0.55 * size + 0.25)),
                  Vector((0.0, y + 0.95, z + 0.75 * size + 0.3))]
        tube(f"neural{i}", points, 0.2, m["pale"], segments=6, radii=[0.24, 0.16, 0.06])


def head(m):
    """The ridge down the head's middle, brows over where the eyes would be."""
    ys = spaced(RIDGE_Y[0], RIDGE_Y[1], 14)
    points = [Vector((0.0, y, body_top(0.0, y) - 0.05)) for y in ys]
    radii = [0.42 * (1 - 0.65 * ((y - RIDGE_Y[0]) / (RIDGE_Y[1] - RIDGE_Y[0])) ** 1.5) for y in ys]
    tube("head_ridge", points, 0.4, m["pale"], segments=8, radii=radii, squash=0.7)
    # The brows: low bony arcs either side of the ridge.
    for side in (-1, 1):
        pts = []
        for i in range(7):
            t = i / 6
            y = -5.2 - 2.4 * t
            x = side * (1.55 + 0.55 * math.sin(math.pi * t) - 0.5 * t)
            pts.append(Vector((x, y, body_top(x, y) - 0.08)))
        tube(f"brow{side}", pts, 0.26, m["pale"], segments=6, radii=[0.12, 0.24, 0.3, 0.3, 0.26, 0.2, 0.1])


def fin_mid(u):
    """The height of the fins' middle at u (x on the left): a little lower towards their tips."""
    return Z - 0.45 - 0.07 * max(0.0, -u - 2.0)


def fins(m):
    """The fins either side of the head: thin bony plates swept out to the outer spines' roots."""
    plan = Plan(FIN, rounding=2)

    def fin_thick(u):
        return min(0.5, max(0.12, 0.09 * plan.chord(u)))

    us = plan.stations(20)
    fin = lifting_surface("fin_l", us, plan, fin_mid, fin_thick, m["fin"], under=0.6, camber=0.25, tip=plan.tip)
    mirrored(fin)
    # The rays across each fin, from the head out to the spines' roots.
    for i, (path, _, _) in enumerate(SPINES):
        root = Vector((path[0][0], path[0][1], 0.0))
        start = Vector((-1.8, -6.2 - 0.9 * i, 0.0))
        pts = []
        for j in range(7):
            t = j / 6
            p = start.lerp(root, t)
            pts.append(Vector((p.x, p.y, fin_mid(p.x) + 0.18)))
        ray = tube(f"ray_l{i}", pts, 0.2, m["pale"], segments=6, radii=[0.16, 0.2, 0.22, 0.22, 0.24, 0.26, 0.28])
        mirrored(ray, f"ray_r{i}")


def spines(m):
    for i, (path, rise, r0) in enumerate(SPINES):
        dense = mk.chaikin(path, 2, closed=False)
        n = len(dense)
        z0 = fin_mid(path[0][0]) + 0.12
        pts = [Vector((x, y, z0 + rise * (j / (n - 1)) ** 1.2)) for j, (x, y) in enumerate(dense)]
        radii = [r0 * (1 - 0.85 * (j / (n - 1)) ** 2.2) for j in range(n)]
        left = tube(f"spine_l{i}", pts, r0, m["pale"], segments=8, radii=radii)
        mirrored(left, f"spine_r{i}")


def tail(m):
    path, r0 = TINE
    pts = [Vector((x, y, Z + dz)) for x, y, dz in mk.chaikin(path, 2, closed=False)]
    n = len(pts)
    radii = [r0 * (1 - 0.82 * (j / (n - 1)) ** 1.6) for j in range(n)]
    left = tube("tine_l", pts, r0, m["fin"], segments=10, radii=radii, squash=0.45)
    mirrored(left, "tine_r")


def build_whole():
    m = materials()
    body(m)
    vertebrae(m)
    head(m)
    fins(m)
    spines(m)
    tail(m)
    return m


def masks(sheets):
    left = k.sprite_mask(os.path.join(sheets, "enemy_T.png"), 229)
    right = k.sprite_mask(os.path.join(sheets, "enemy_T.png"), 231)
    return left, right, [left[y] + right[y] for y in range(28)]


def build():
    options = k.args()
    out = mk.outdir(options)
    k.reset()
    bpy.context.scene.view_settings.view_transform = "Standard"
    m = build_whole()
    whole = mk.meshes()
    print("whole fish: %d triangles, %d objects" % (mk.triangles(whole), len(whole)))
    if "check" in options:
        left, right, both = masks(options["check"])
        mk.compare("whole (T 229 beside T 231)", mk.coverage(whole, 48, 28), both)
    if "preview" in options:
        mk.preview(options["preview"] + "coral_fish_whole", whole, size=(48, 28), scale=10, distance=1.4)
        bpy.context.view_layer.update()
    for name, sprite, box, centre_x in PIECES:
        parts = [p for p in (mk.cut(src, box, m["cut"]) for src in whole) if p is not None]
        mk.transform(parts, Matrix.Translation((-centre_x, 0.0, 0.0)))
        if "check" in options:
            mk.compare("%s (T %d)" % (name, sprite), mk.coverage(parts, 24, 28), left if sprite == 229 else right)
        mk.report(name, parts, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, parts)
        for obj in parts:
            bpy.data.objects.remove(obj)


if __name__ == "__main__":
    build()
