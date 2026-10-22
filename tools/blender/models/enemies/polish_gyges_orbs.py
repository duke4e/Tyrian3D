"""GYGES' glossy green balls and green spike that swing round over the grey stalk (sheet h, 2x2 sprites; episode 2's
enemies 417, 418, 419 (h 89, 127, 91) and 420 above 421 (h 77 above 115), one frame each), polished (2026-10-22, round
35; it replaces wave3_ad.py's orbs, spheres painted pixel by pixel, and its spike, a lathe round the sprites' rows
painted pixel by pixel).

Where GYGES puts them (t150-153, right after the stalk, polish_gyges_wall.py, in the sky; again on the top layer at
t2936-2939 after the stalk's second appearance): the balls at x 110, 104 and 70, the spike's two pieces at x 30 (115
28 pixels under 77, the same movement: one object), each swinging round its own middle (xcaccel and ycaccel with
xrev 2/2, 4/4, 8/4 and the spike 16/8: ever wider circles). No other enemy, launched ones included, shows these sprites;
no episode 6 level makes them.

- gyges_orb_s (h 89, 15 x 14 pixels: columns 5-19, rows 6-19) and gyges_orb_l (h 91, 21 x 19: columns 2-22, rows
  4-22): polish_balls.py's glossy ball (the asteroid levels' M 115, its dark frames A 165 203 241) in other sizes and
  in green (ramp 12): the ball outlined by a dark rim, lighter at its upper left, a white glare above its middle on the
  left, a bright crescent inside its rim at the lower right. h 89 is drawn in ball_dark_203's shades (its body shade 7,
  the glare 12-15, the crescent 12 and 14), h 91 in ball_dark's (5; 11-15; 10 and 13); built with polish_balls.ball()
  on their own ellipsoids (BALL, the glare's place and size moved and scaled with them, the crescent where the sprites
  draw it), so that the family matches.
- h 127 (18 x 17) is A 165 (ball_dark) shade for shade in ramp 12 (outline 0x01 for its rim): no model of its own;
  models.cfg shows it as ball_dark with color=sprite (the ball's materials are all palette shades of ramp 3 without
  emission, so the renderer's recolouring makes it the green ball), and gyges_orb_m.glb goes.
- gyges_spike_top, gyges_spike_tip (h 77 above 115: a 24 x 56 picture, built whole and cut along the sprites' edge,
  origin): a green crystal spike: a faceted knob (rows 6-22 of the picture: a pointed cap, a head whose dark green
  (ramp 2) facets are lit in V-shaped bands of bright green (ramp 12)), a ringed neck (rows 23-27), and a long blade
  (rows 28-52) with a ridge down it (column 12.5: its left face the pale green of the sprite's light, 0x29-0x2c, its
  right face dark, 0x24-0x26) tapering to a point. One loft along the picture's rows: per row its span from the
  sprite, its section an octagon (the knob, the neck) or a rhombus (the blade) whose top ridge stands where the
  sprite draws it, symmetric about z = 0 (it flies: drawn at its origin, half of it under the sky's plane, which
  nothing shows); flat faces painted as the upscales draw it (the knob bright green cut by dark grooves along V lines,
  darker down its sides, the neck's rings, the blade's pale and dark faces and its pale ridge), in shades by how they
  face the game's sun.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; each ball's origin
at its sprite's centre (pixel 12, 14: column c is x = c + 0.5 - 12, row r is y = 13.5 - r), drawn centred in height;
the spike's whole has its origin at (12, 28) of its picture (column c is x = c + 0.5 - 12, row r is y = 27.5 - r), the
top piece's at (0, 14), the tip's at (0, -14).

models.cfg: model gyges_orb_s / gyges_orb_l and gyges_spike_top / gyges_spike_tip stay (the spike with origin); the
gyges_orb_m model line goes, sprite h 127 ball_dark yaw=0 color=sprite.

Replaces wave3_ad.py (all of it: the orbs and the spike are all it still builds; delete it, and wave3_ad_kit.py and
wave3_ad_art.py with it: only it imports them).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes against
enemy_H.png), --preview <prefix>, --only <model,...>.
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
import polish_balls as pb  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_deli_boss import join, drop_unused  # noqa: E402
from polish_coral_manta import cut  # noqa: E402

RAMP = 12                         # the balls' green

# The balls: model, sprite, the ball's middle (x, y) and radii (its outline included), the glare's middle (x, y) and
# size's scale, the body's shade, the glare's shades (edge, middle, core) and scale, the crescent's shades (outer, core)
# and scale (polish_balls.BALL_FRAMES' terms).
ORBS = [("gyges_orb_s", 89, (0.5, 1.0), (7.6, 7.1, 6.9), (-1.6, 3.6), 0.78, 7, (12, 13, 15), 0.78, (12, 14), 0.85),
        ("gyges_orb_l", 91, (0.5, 0.5), (10.6, 9.6, 9.4), (-1.9, 3.4), 1.0, 5, (11, 13, 15), 0.62, (10, 13), 0.9)]


def ball(name, centre, radii, glare_at, glare_size, body, glare, glare_scale, crescent, crescent_scale):
    """polish_balls.ball() on its own ellipsoid, the glare where this sprite draws it."""
    saved = pb.BALL, pb.GLARE, pb.GLARE_SIZE
    try:
        pb.BALL = pb.Ellipsoid((centre[0], centre[1], radii[2]), radii)
        pb.GLARE = Vector(glare_at)
        pb.GLARE_SIZE = Vector((2.6, 2.0)) * glare_size
        pb.ball(name, body, glare, glare_scale, crescent, crescent_scale, RAMP)
    finally:
        pb.BALL, pb.GLARE, pb.GLARE_SIZE = saved
    obj = bpy.data.objects[name]
    # Its middle at z 0 (the game draws it centred in height anyway).
    obj.data.transform(Matrix.Translation((0.0, 0.0, -radii[2])))
    return obj


# --- The spike -----------------------------------------------------------------------------------------------------

def SX(c):
    return c + 0.5 - 12.0


def SY(r):
    return 27.5 - r


# Per row of the picture: the left and right edge (columns, the pixels' outer edges), the ridge's column (edge), the
# section's half-height, its kind (8: an octagon, the knob and neck; 4: a rhombus, the blade).
SPIKE = [(6.2, 10.4, 14.6, 12.5, 0.6, 8), (7.0, 9.2, 15.8, 12.5, 1.4, 8), (8.0, 8.2, 16.8, 12.5, 2.0, 8),
         (9.0, 7.2, 17.8, 12.5, 2.5, 8), (10.0, 6.2, 18.8, 12.5, 2.9, 8), (11.2, 5.3, 19.7, 12.5, 3.2, 8),
         (13.0, 5.1, 19.9, 12.5, 3.4, 8), (16.0, 5.1, 19.9, 12.5, 3.4, 8), (19.0, 5.1, 19.9, 12.5, 3.3, 8),
         (21.8, 5.2, 19.8, 12.5, 3.0, 8), (22.8, 5.8, 19.2, 12.5, 2.5, 8), (23.6, 6.6, 18.4, 12.5, 2.6, 8),
         (24.4, 7.1, 17.9, 12.5, 2.2, 8), (25.2, 7.2, 17.8, 12.5, 2.4, 8), (26.4, 7.2, 17.8, 12.5, 2.4, 8),
         (27.4, 7.2, 17.8, 12.5, 2.1, 8), (28.3, 7.0, 18.0, 12.7, 2.3, 4), (29.3, 6.0, 19.0, 12.9, 2.6, 4),
         (30.6, 5.2, 19.8, 12.9, 2.8, 4), (33.2, 5.2, 19.8, 12.9, 2.8, 4), (35.6, 5.9, 19.1, 12.9, 2.6, 4),
         (38.6, 6.8, 18.2, 12.9, 2.3, 4), (41.6, 7.6, 17.4, 12.9, 2.0, 4), (44.4, 8.4, 16.6, 12.9, 1.6, 4),
         (47.2, 9.3, 15.7, 12.8, 1.2, 4), (49.4, 10.2, 14.8, 12.7, 0.8, 4), (51.0, 11.1, 13.9, 12.6, 0.5, 4)]
SPIKE_TIP = (12.5, 53.0)
SPIKE_SUN = Vector((-0.6, 0.6, 1.0)).normalized()
# Its paint, as the upscales draw it: the knob bright green (ramp 12) cut by dark green grooves (GROOVES: polylines of
# (row, column), a V under its cap and two strokes lower down, the line where it meets the neck), darker down its
# sides; the neck two bright rings; the blade's left face the pale green of the sprite's light with a paler strip along
# the ridge, its right face dark (ramp 2). Shades by how the faces face the game's sun.
BRIGHT = [0xc3, 0xc5, 0xc8, 0xcb]
KNOB_SIDE = [0x24, 0x26, 0x28]
GROOVE = [0x21, 0x22, 0x23]
PALE = [0x27, 0x28, 0x29, 0x2a]
RIDGE = [0x2a, 0x2b, 0x2c]
DARK = [0x23, 0x24, 0x25, 0x26]
GROOVES = [[(10.6, 5.6), (15.2, 12.5), (10.6, 19.4)], [(16.2, 5.6), (19.8, 9.6)], [(16.2, 19.4), (19.8, 15.4)],
           [(22.4, 5.4), (22.4, 19.6)], [(24.3, 6.8), (24.3, 18.2)], [(26.4, 6.8), (26.4, 18.2)]]
GROOVE_W = 0.55


def spike_ring(row, left, right, ridge, half_h, kind):
    y = SY(row)
    x0, x1, xr = left - 12.0, right - 12.0, ridge - 12.0
    if kind == 4:
        pts = [(x0, 0.0), (xr, half_h), (x1, 0.0), (xr, -half_h)]
    else:
        a, b = x0 + (xr - x0) * 0.32, xr + (x1 - xr) * 0.68
        pts = [(x0, 0.0), (a, half_h * 0.78), (xr, half_h), (b, half_h * 0.78), (x1, 0.0), (b, -half_h * 0.78),
               (xr, -half_h), (a, -half_h * 0.78)]
    # Every ring 24 points (the rhombus' sides split in six, the octagon's in three), in a fixed order.
    split = 6 if len(pts) == 4 else 3
    full = []
    for i in range(len(pts)):
        p, q = pts[i], pts[(i + 1) % len(pts)]
        full += [(p[0] + (q[0] - p[0]) * j / split, p[1] + (q[1] - p[1]) * j / split) for j in range(split)]
    return [Vector((px, y, pz)) for px, pz in full]


def dense(specs, step=0.5):
    """The rows' specs every `step` rows (linear between them; the section kind of the row before)."""
    out = []
    for a, b in zip(specs, specs[1:]):
        n = max(1, int(round((b[0] - a[0]) / step)))
        for i in range(n):
            t = i / n
            out.append(tuple(a[j] + (b[j] - a[j]) * t for j in range(5)) + (a[5],))
    out.append(specs[-1])
    return out


def groove_distance(row, col):
    best = 99.0
    for line in GROOVES:
        for (r0, c0), (r1, c1) in zip(line, line[1:]):
            dr, dc = r1 - r0, c1 - c0
            t = max(0.0, min(1.0, ((row - r0) * dr + (col - c0) * dc) / (dr * dr + dc * dc)))
            best = min(best, math.hypot(row - (r0 + t * dr), col - (c0 + t * dc)))
    return best


def pick(shades, lit):
    return shades[min(len(shades) - 1, int(lit * len(shades) * 0.999))]


def spike():
    rings = [spike_ring(*spec) for spec in dense(SPIKE)]
    tx, ty = SPIKE_TIP
    first = rings[0]
    obj = k.loft("spike", rings, None, start_point=(0.5, SY(5.6), 0.0), end_point=(tx - 12.0, SY(ty), 0.0))
    mesh = obj.data
    mesh.polygons.foreach_set("use_smooth", [False] * len(mesh.polygons))
    keys = []
    for poly in mesh.polygons:
        c, n = poly.center, poly.normal
        row, col = 28.0 - c.y, c.x + 12.0
        lit = max(0.0, min(1.0, n.dot(SPIKE_SUN) * 1.15 - 0.1))
        if n.z < -0.2:
            keys.append(("dark", 0x21))
        elif row < 27.8:
            if groove_distance(row, col) < GROOVE_W:
                keys.append(("g", pick(GROOVE, lit)))
            elif row < 22.6 and abs(col - 12.5) > 5.2:
                keys.append(("g", pick(KNOB_SIDE, lit)))
            else:
                keys.append(("g", pick(BRIGHT, lit)))
        elif abs(col - 12.9) < 0.7:
            keys.append(("g", pick(RIDGE, lit)))
        else:
            keys.append(("g", pick(PALE if col < 12.9 else DARK, lit)))
    order = sorted(set(keys), key=str)
    for key in order:
        kind, index = key
        glow = dict(emission=k.level_palette()[index], emission_strength=0.18) if index >> 4 == 12 else {}
        mesh.materials.append(k.material("spike_%x" % index, palette=index, metallic=0.15,
                                         roughness=0.22 if kind == "g" else 0.5, **glow))
    mesh.polygons.foreach_set("material_index", [order.index(key) for key in keys])
    mesh.update()
    return obj


def spike_pieces(options, out, only, sheet):
    k.reset()
    whole = spike()
    dark = whole.data.materials[0]
    for name, sprite, box in (("gyges_spike_top", 77, (-12.0, 12.0, 0.0, 28.0)),
                              ("gyges_spike_tip", 115, (-12.0, 12.0, -28.0, 0.0))):
        if only is not None and name not in only:
            continue
        piece = cut(whole, box, dark)
        mk.transform([piece], Matrix.Translation((0.0, -(box[2] + box[3]) / 2, 0.0)))
        bpy.context.view_layer.update()
        triangulate([piece])
        piece.name = name
        drop_unused([piece])
        bpy.context.scene.view_settings.view_transform = "Standard"
        if sheet:
            mk.compare("%s (h %d)" % (name, sprite), mk.coverage([piece], 24, 28), k.sprite_mask(sheet, sprite))
        mk.report(name, [piece], os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, [piece])
        bpy.data.objects.remove(piece)


def build():
    options = k.args()
    out = mk.outdir(options)
    only = set(options["only"].split(",")) if "only" in options else None
    sheet = None
    if "check" in options:
        sheets = options["check"]
        sheet = os.path.join(sheets, "enemy_H.png") if os.path.isdir(sheets) else sheets
    for name, sprite, centre, radii, glare_at, glare_size, body, glare, gscale, crescent, cscale in ORBS:
        if only is not None and name not in only:
            continue
        k.reset()
        obj = ball(name, centre, radii, glare_at, glare_size, body, glare, gscale, crescent, cscale)
        triangulate([obj])
        bpy.context.scene.view_settings.view_transform = "Standard"
        if sheet:
            mk.compare("%s (h %d)" % (name, sprite), mk.coverage([obj], 24, 28), k.sprite_mask(sheet, sprite))
        mk.report(name, [obj], os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, [obj])
    spike_pieces(options, out, only, sheet)



if __name__ == "__main__":
    build()
