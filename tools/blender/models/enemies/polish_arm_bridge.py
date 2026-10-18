"""The blue steel bridge of GEM WAR, GLACIER, GRYPHON, MIGRATION and STATION, drawn from three sprites of
sheet V (2x2 each, 24 x 28 pixels; sky, ground and top layers): the left block with its red ball, V 89,
the bridge between, V 91 (its animation 91 129 129 129 91), and the right block, V 93 (V 89's mirror
image), polished (2026-10-18). The levels place them as one 72 x 28 picture: 796 (V 89) at x, the
middle (797, 807 or 808: V 91) at x + 24 and 798 (V 93) at x + 48, on one row (GEM WAR's events at 60,
160, 400 ...; MIGRATION, GLACIER and STATION alike), and they move together. models.cfg: model
arm_ball_left / arm_bridge / arm_ball_right / arm_bridge_129 ... origin; sprite v 89 arm_ball_left
yaw=0, sprite v 91 arm_bridge yaw=0, sprite v 93 arm_ball_right yaw=0, frame v 129 arm_bridge_129.

The object is built whole and cut along the sprites' edges into the three pieces, each moved so that
its sprite's centre is its origin (polish_redjet.py's method): drawn at their own places they meet
again, the pieces keeping the whole's shading across the cuts.

As the 4x upscales draw it: two chunky blocks of blue steel (columns 1-25 of the picture and their
mirror image) joined at their backs by a lower bridge. Each block has a high deck (rows 4-14) whose
front edge (row 14, a light line) rolls over into a broad slope down to the block's front (rows 15-24),
a light seam ridge running over deck and slope (column 15), three bright fins on the deck's outer
back corner (columns 9, 11, 13 of rows 6-10) and, at its outer end, a dull red ball (columns 2-7 of
rows 8-12) in a darker collar (rows 13-15) on a low jaw that juts out under it (rows 13-19). The
blocks' inner ends reach into V 91: shoulders at the back (its columns 0-3 and 20-23 of rows 6-14),
a dark seam between them and the bridge (columns 4 and 19), and below them the blocks' inner faces,
each with a red lamp low down (columns 0 and 23 of rows 19-20). Between the shoulders a glossy blue
hump (rows 7-13, brightest along its top) ends in front in a light ledge (row 14); under the ledge a
vent glows dull red between grey posts (row 15), then a sloping lip (rows 16-17) with two short
emitters under it (columns 7 and 16 of rows 18-19), and below that the bridge is open: the ground
shows between the blocks. Frame 129 fires: a red beam, white-yellow in its middle, runs from lamp to
lamp under the lip (rows 18-21), the vent glows orange (arm_bridge_129: the middle piece with the
beam, the vent, the lamps and the emitters' tips alight; no other enemy of sheet V uses 129).

The blocks' steel is rounded softly all over, as the upscales paint it (their CAD shapes remeshed,
smoothed and decimated: polish_machine_kit.soften), their tops bulging a little across their width so
that the light runs over them; the seam ridge, the trim along the deck's front edge and the fins are
laid on that surface. The beam is three glowing layers, each narrower but taller than the one round
it, so that its hot core shows along its middle as the sprite's yellow does.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera;
the whole's origin is V 91's centre (the picture's pixel 36, 14), its base on z = 0. The blocks are
built for the left side and mirrored.

Replaces wave1_b.py's arm_ball_left / arm_ball_right (arm_ball()) and wave3_t.py's arm_bridge
(bridge_whole()): remove those from their registries so that they don't overwrite these models.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the
silhouettes of the pieces and of the whole; the sprites' masks are written below), --preview
<prefix> (each piece's top and 3/4 view and the whole's), --only <name,...> (which of the four
models to export).
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402

# The sprites' pixels ('#'), rows 0-27 (V 93 is V 89's mirror image).
V89 = """
........................
........................
........................
........................
..............########..
........################
........################
...#####################
..######################
.#######################
.#######################
.#######################
.#######################
.#######################
.#######################
.#######################
.#######################
..######################
..######################
...#####################
.......#################
.........###############
...........############.
.............#########..
...............######...
........................
........................
........................
"""
V91 = """
........................
........................
........................
........................
........................
........................
######............######
########################
########################
########################
########################
########################
########################
########################
########################
########################
#...################...#
#....##############....#
##....############....##
##....###......###....##
##....................##
##....................##
........................
........................
........................
........................
........................
........................
"""
V129 = """
........................
........................
........................
........................
........................
........................
######............######
########################
########################
########################
########################
########################
########################
########################
########################
########################
#...################...#
#....##############....#
##..################..##
########################
##..################..##
##.....##########.....##
........................
........................
........................
........................
........................
........................
"""

# name, sprite, the box it covers in the whole's coordinates (x0, x1, y0, y1), its sprite's centre x.
PIECES = [("arm_ball_left", 89, (-36.0, -12.0, -20.0, 20.0), -24.0),
          ("arm_bridge", 91, (-12.0, 12.0, -20.0, 20.0), 0.0),
          ("arm_ball_right", 93, (12.0, 36.0, -20.0, 20.0), 24.0)]
FIRING = ("arm_bridge_129", 129, (-12.0, 12.0, -20.0, 20.0), 0.0)

# --- The left block (the right one is its mirror image) -------------------------------------------
# Its plan, counter-clockwise from its lower left: the slanting lower edge (rows 19-24), the inner face
# (V 91's columns 0-1), the shoulder (V 91's columns 0-3 of rows 6-14), the back (rows 4-6), the
# outer face (column 8 above the ball).
HOUSING = [(-29.4, -6.3), (-27.0, -7.5), (-25.0, -8.5), (-23.0, -9.5), (-21.2, -10.55), (-15.0, -10.55),
           (-13.8, -9.45), (-12.8, -8.4), (-12.0, -7.65), (-10.7, -7.65), (-10.7, -0.9), (-7.65, -0.9),
           (-7.65, 7.65), (-12.2, 7.65), (-13.3, 8.65), (-14.4, 9.62), (-21.6, 9.62), (-22.7, 8.65),
           (-27.3, 8.65), (-27.75, 8.2), (-27.75, 1.2)]
# Its side profile: the deck from its back (BACK_Y, DECK_BACK) to the crease along its front edge
# (CREASE_Y, CREASE_Z, row 14), the slope from there towards the front (FRONT_Y, FRONT_Z).
BACK_Y, DECK_BACK = 9.9, 11.0
CREASE_Y, CREASE_Z = -0.75, 10.6
FRONT_Y, FRONT_Z = -10.9, 2.8
# The jaw under the ball (columns 1-7 of rows 13-19): plan, its top and front heights.
JAW = [(-32.7, -5.65), (-29.4, -5.65), (-28.5, -6.25), (-27.0, -6.25), (-27.0, 2.3), (-34.0, 2.3), (-34.67, 1.4),
       (-34.67, -2.7), (-33.67, -3.4), (-33.67, -4.67), (-32.7, -5.05)]
JAW_BACK_Y, JAW_TOP, JAW_SLOPE_Y, JAW_FRONT_Z = 2.3, 5.3, -1.8, 3.2
BALL = (Vector((-30.85, 3.3, 7.35)), 3.35)  # the red ball (columns 2-7 of rows 8-12)
COLLAR = [(0.0, 3.9), (2.5, 3.9), (3.15, 4.15), (3.38, 4.8), (3.25, 5.55), (2.75, 6.0), (0.0, 6.0)]
# The fins on the deck's outer back corner (columns 9, 11, 13 of rows 6-10), in a shallow pocket.
FINS_X, FINS_Y = (-26.5, -24.5, -22.5), (3.3, 7.95)
POCKET = (-27.45, -21.55, 2.65, 8.4, 0.75)  # x0, x1, y0, y1, depth
RIDGE_X = -20.5             # the seam ridge over deck and slope (column 15)
# The blocks' edges all rounded softly, as the upscales paint them: voxel size, smoothing, decimation.
SOFT_VOXEL, SOFT_ITERATIONS, SOFT_RATIO = 0.3, 7, 0.16
# Their tops bulge a little across their width (CROWN higher over CROWN_X than at CROWN_HALF from it).
CROWN, CROWN_X, CROWN_HALF = 1.0, -18.5, 11.5
TRIM_X = (-20.0, -7.9)      # the light trim along the deck's front edge (row 14, columns 16-27)
LAMP = (Vector((-10.7, -5.6, 2.6)), 0.85, 0.95)  # on the inner face: centre, radius, how far it stands out

# --- The bridge (V 91's columns 4-19) -------------------------------------------------------------
CORE = (-8.7, 8.7, -1.0, 6.9, 3.6, 7.2)        # under the hump, dark in the seams beside it
SADDLE = (7.35, 3.05, 6.05, 3.75, 3.6, 0.07)   # half length, axis y and z, radii y and z, bulge in the middle
LEDGE = (10.4, -0.88, 6.55, 0.62)             # half length, y, z, radius (row 14)
VENT = (4.45, -1.65, -0.9, 4.85, 6.15)        # half width, y0, y1, z0, z1 (row 15)
VENT_POSTS = (2.5, 4.55)                       # grey posts in it (columns 9 and 14 of V 91) and at its ends
LIP = ([(-7.15, -1.65), (7.15, -1.65), (6.25, -4.62), (-6.25, -4.62)], 3.4, 5.95, 4.45)  # plan, bottom, top back/front
FANGS = (4.5, (Vector((0.0, -3.9, 3.95)), 0.95), (Vector((0.0, -5.8, 3.05)), 0.42))  # x, root, tip
# The beam of frame 129 (rows 18-21): its middle, and its layers from outside in (radii, palette index,
# glow), each narrower but a little taller than the one round it, so that the hotter ones show along
# its middle as the sprite's yellow does.
BEAM = (Vector((0.0, -6.0, 2.6)), [((10.0, 2.05, 0.75), 0x76, 1.5), ((7.4, 1.35, 0.98), 0x79, 2.2),
                                   ((4.0, 0.8, 1.2), 0x7d, 3.0)])


def mirror_plan(points, side):
    """A plan built for the left block, for the side wanted (1 left, -1 right), counter-clockwise."""
    return points if side > 0 else [(-x, y) for x, y in reversed(points)]


def materials(firing):
    glow = k.level_palette()

    def lit(name, index, strength, **kw):
        return k.material(name, palette=index, emission=glow[index], emission_strength=strength, **kw)
    m = {
        "deck": k.material("armbridge_steel_hull", palette=0x3b, metallic=0.6, roughness=0.24),
        "trim": k.material("armbridge_trim", palette=0x3e, metallic=0.55, roughness=0.22),
        "seam": k.material("armbridge_seam", palette=0x33, metallic=0.4, roughness=0.5),
        "saddle": k.material("armbridge_saddle", palette=0x3c, metallic=0.65, roughness=0.16),
        "ledge": k.material("armbridge_ledge", palette=0x3a, metallic=0.55, roughness=0.28),
        "steel": k.material("armbridge_steel", palette=0x38, metallic=0.5, roughness=0.34),
        "ball": lit("armbridge_ball", 0x47, 0.35, metallic=0.2, roughness=0.22),
        "collar": k.material("armbridge_collar", palette=0x43, metallic=0.4, roughness=0.35),
        "lamp": lit("armbridge_lamp", 0x77 if firing else 0x46, 1.6 if firing else 0.7, roughness=0.15),
        "vent": lit("armbridge_vent", 0x7a if firing else 0x44, 2.0 if firing else 0.6, roughness=0.4),
    }
    if firing:
        for i, (_, index, strength) in enumerate(BEAM[1]):
            m[("beam", i)] = lit(f"armbridge_beam_{index:x}", index, strength, roughness=0.3)
    return m


def housing_side():
    """The block's side profile (y, z)."""
    slope = (CREASE_Z - FRONT_Z) / (CREASE_Y - FRONT_Y)
    return [(FRONT_Y - 3, 0.0), (BACK_Y + 1, 0.0), (BACK_Y + 1, DECK_BACK + 0.04),
            (CREASE_Y, CREASE_Z), (FRONT_Y - 3, FRONT_Z - 3 * slope)]


def crown(obj, side):
    """Bulges a block's top a little across its width, so that the light runs over it as over the
    upscale's rounded steel."""
    for v in obj.data.vertices:
        u = (v.co.x - side * CROWN_X) / CROWN_HALF
        v.co.z += CROWN * max(0.0, 1 - u * u) * mk.smoothstep(3.0, 8.0, v.co.z)
    obj.data.update()


def block(side, m):
    """The left (side 1) or right (side -1) block: housing, jaw, ball, fins, ridge, lamp."""
    s = side
    body = mk.prism(f"housing{s}", mirror_plan(HOUSING, s), -1.0, 14.0, m["deck"])
    mk.boolean(body, mk.prism("housing_side", housing_side(), -40.0, 40.0, axis="x"))
    x0, x1, y0, y1, depth = POCKET
    xa, xb = sorted((s * x0, s * x1))
    pocket = mk.box("pocket", xa, xb, y0, y1, DECK_BACK - depth, 20.0, m["seam"])
    mk.boolean(body, pocket, "DIFFERENCE")
    mk.soften(body, SOFT_VOXEL, SOFT_ITERATIONS, 0.6, SOFT_RATIO)
    crown(body, s)
    mk.paint(body, lambda c, n: m["seam"] if c.z < DECK_BACK - depth + 0.25 + CROWN and
             xa + 0.3 < c.x < xb - 0.3 and y0 + 0.3 < c.y < y1 - 0.3 and n.z > 0.5 else None)

    # The jaw under the ball.
    jaw = mk.prism(f"jaw{s}", mirror_plan(mk.chaikin(JAW, 2), s), -1.0, 10.0, m["deck"])
    profile = [(-12.0, 0.0), (JAW_BACK_Y + 1, 0.0), (JAW_BACK_Y + 1, JAW_TOP), (JAW_SLOPE_Y, JAW_TOP),
               (-6.25, JAW_FRONT_Z), (-12.0, JAW_FRONT_Z - 1.5)]
    mk.boolean(jaw, mk.prism("jaw_side", profile, -40.0, 40.0, axis="x"))
    mk.soften(jaw, SOFT_VOXEL, SOFT_ITERATIONS, 0.6, SOFT_RATIO)

    # The ball in its collar.
    centre, r = BALL
    c = Vector((s * centre.x, centre.y, centre.z))
    k.smooth(mk.lathe(f"collar{s}", COLLAR, (c.x, c.y), m["collar"], segments=40), 50)
    mk.ball(f"ball{s}", tuple(c), (r, r, r * 0.97), m["ball"], 36, 18)

    # The fins in their pocket.
    for i, fx in enumerate(FINS_X):
        fin = mk.box(f"fin{s}_{i}", s * fx - 0.42, s * fx + 0.42, FINS_Y[0], FINS_Y[1], DECK_BACK - depth - 0.1,
                     DECK_BACK + 0.28, m["trim"])
        mk.bevel(fin, 0.3, 2, 35)
        mk.shade(fin, 40)

    # The seam ridge over the deck and down the slope.
    hit = mk.surface([body])
    points, ups = [], []
    for i in range(40):
        y = 9.35 - (9.35 + 10.1) * i / 39
        h = hit(s * RIDGE_X, y)
        if h is not None:
            points.append(h[0])
            ups.append(h[1])
    k.smooth(mk.bar(f"ridge{s}", points, ups, 0.36, 0.3, 0.4, m["trim"], 12, 3.0), 40)
    # The light trim along the deck's front edge, from the ridge to the shoulder's end (row 14).
    points, ups = [], []
    for i in range(24):
        x = s * (TRIM_X[0] + (TRIM_X[1] - TRIM_X[0]) * i / 23)
        h = hit(x, CREASE_Y + 0.1)
        if h is not None:
            points.append(h[0])
            ups.append(h[1])
    k.smooth(mk.bar(f"crease{s}", points, ups, 0.42, 0.22, 0.4, m["trim"], 12, 3.0), 40)

    # The lamp low on the inner face, a short red glass emitter facing across the bridge.
    centre, r, out = LAMP
    x = s * centre.x
    rings = []
    for dx, rr in ((-0.3, r + 0.25), (0.25, r + 0.25), (0.3, r), (out * 0.7, r), (out, r * 0.6)):
        rings.append([Vector((x + s * dx, centre.y + rr * math.cos(2 * math.pi * j / 20),
                              centre.z + rr * math.sin(2 * math.pi * j / 20))) for j in range(20)])
    lamp = k.loft(f"lamp{s}", rings, m["lamp"])
    mk.paint(lamp, lambda c, n: m["seam"] if abs(c.x - x) < 0.28 else None)
    k.smooth(lamp, 50)


def bridge(m, firing):
    x0, x1, y0, y1, z0, z1 = CORE
    core = mk.box("core", x0, x1, y0, y1, z0, z1, m["seam"])
    mk.bevel(core, 0.3, 2, 35)
    # The hump: elliptic sections along x, a little fuller in the middle.
    half, ay, az, ry, rz, bulge = SADDLE
    rings = []
    count = 25
    for i in range(count):
        x = -half + 2 * half * i / (count - 1)
        f = 1 + bulge * (1 - (x / half) ** 2)
        rings.append([Vector((x, ay + ry * f * math.cos(a), az + rz * f * math.sin(a)))
                      for a in (2 * math.pi * j / 48 for j in range(48))])
    hump = k.loft("saddle", rings, m["saddle"])
    k.smooth(hump, 50)
    # The ledge across its front.
    half, y, z, r = LEDGE
    k.smooth(mk.tube("ledge", [(-half, y, z), (half, y, z)], r, m["ledge"], 16), 50)
    # The vent under the ledge: glowing slats between grey posts.
    hw, vy0, vy1, vz0, vz1 = VENT
    vent = mk.box("vent", -hw, hw, vy0, vy1 + 0.6, vz0, vz1, m["vent"])
    mk.bevel(vent, 0.15, 1, 35)
    for i, px in enumerate((-VENT_POSTS[1], -VENT_POSTS[0], VENT_POSTS[0], VENT_POSTS[1])):
        post = mk.box(f"post{i}", px - 0.38, px + 0.38, vy0 - 0.1, vy1 + 0.5, vz0 - 0.1, vz1 + 0.1, m["steel"])
        mk.bevel(post, 0.2, 2, 35)
        mk.shade(post, 40)
    # The lip: a plate sloping down towards the front.
    plan, bottom, top_back, top_front = LIP
    lip = mk.prism("lip", plan, bottom, 12.0, m["ledge"])
    slope = (top_back - top_front) / (plan[0][1] - plan[2][1])
    profile = [(plan[2][1] - 1, 0.0), (plan[0][1] + 1, 0.0), (plan[0][1] + 1, top_back + slope),
               (plan[2][1] - 1, top_front - slope)]
    mk.boolean(lip, mk.prism("lip_side", profile, -20.0, 20.0, axis="x"))
    mk.cleanup(lip)
    mk.bevel(lip, 0.35, 3, 30)
    mk.paint(lip, lambda c, n: m["ledge"] if n.z > 0.5 else m["steel"])
    mk.shade(lip, 35)
    # The emitters under it.
    fx, (root, r0), (tip, r1) = FANGS
    for side in (-1, 1):
        points, radii = [], []
        for i in range(8):
            t = i / 7
            points.append(Vector((side * fx, root.y + (tip.y - root.y) * t, root.z + (tip.z - root.z) * t)))
            radii.append(r0 + (r1 - r0) * t ** 1.3)
        k.smooth(mk.tube(f"fang{side}", points, r0, m["steel"], 14, radii=radii), 50)
        k.smooth(mk.ball(f"fang_tip{side}", tuple(points[-1]), (r1 + 0.08,) * 3, m["lamp" if firing else "steel"],
                         12, 6), 60)
    if firing:
        centre, layers = BEAM
        for i, (radii, _, _) in enumerate(layers):
            mk.ball(f"beam{i}", tuple(centre), radii, m[("beam", i)], 40, 16)


def build_whole(firing):
    m = materials(firing)
    for side in (1, -1):
        block(side, m)
    bridge(m, firing)
    return m


def mask_rows(text):
    return [[c == "#" for c in line] for line in text.strip().splitlines()]


def whole_mask():
    """The three sprites side by side (72 x 28)."""
    left = mask_rows(V89)
    middle = mask_rows(V91)
    right = [list(reversed(row)) for row in left]
    return [left[y] + middle[y] + right[y] for y in range(28)]


def piece_mask(sprite):
    if sprite == 89:
        return mask_rows(V89)
    if sprite == 93:
        return [list(reversed(row)) for row in mask_rows(V89)]
    return mask_rows(V91 if sprite == 91 else V129)


def cut_and_export(whole, m, pieces, options):
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    for name, sprite, box, centre_x in pieces:
        if only and name not in only:
            continue
        parts = [p for p in (mk.cut(src, box, m["seam"]) for src in whole) if p is not None]
        mk.transform(parts, Matrix.Translation((-centre_x, 0.0, 0.0)))
        if "check" in options:
            mk.compare("%s (V %d)" % (name, sprite), mk.coverage(parts, 24, 28), piece_mask(sprite))
        mk.report(name, parts, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, parts)
        for obj in parts:
            bpy.data.objects.remove(obj)


def build():
    options = k.args()
    for firing in (False, True):
        k.reset()
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        m = build_whole(firing)
        whole = mk.meshes()
        if not firing:
            print("whole: %d triangles, %d objects" % (mk.triangles(whole), len(whole)))
            if "check" in options:
                mk.compare("whole (V 89, 91, 93 side by side)", mk.coverage(whole, 72, 28), whole_mask())
            if "preview" in options:
                mk.preview(options["preview"] + "arm_whole", whole, size=(72, 28), scale=8, distance=2.0)
        cut_and_export(whole, m, [FIRING] if firing else PIECES, options)


if __name__ == "__main__":
    build()
