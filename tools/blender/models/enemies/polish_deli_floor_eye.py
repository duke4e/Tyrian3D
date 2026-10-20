"""A machine set in UNDERDELI's dark floor: sheet ^ (x5e in models.cfg) sprite 45, 2x2 (24 x 28 pixels); enemies 32 and
48 (one frame each), ground enemies the level puts on the floor's tiles (UNDERDELI's events 804-1364 and on, at map
columns). Polished 2026-10-20; it replaces wave3_i.py's deli_floor_eye() (boxes and a raised pixel region).
models.cfg: model deli_floor_eye enemies/deli_floor_eye.glb origin; sprite x5e 45 deli_floor_eye yaw=0 height=-4
glow=8:0.3:119:-0.5:-5.1 (models drawn at their origin stand at the ground enemies' layer, 4 pixels over the
terrain: height=-4 sets it on the floor; the glow is the eye's).

As the sprite and its 4x upscale draw it (columns and rows of the 24 x 28 sprite; it is symmetric about the middle of
column 11): at the back two pillars (columns 3-9 and 13-19 of rows 2-11), lit at their left, ribs down them, a grille
of bars between them (columns 9-13 of rows 2-6); in front of them a glowing eye (columns 10-12 of rows 7-11: a hot
yellow core at its upper left, orange, a red rim) in a dark socket; in front of it a hood like a chevron (columns
3-20 of rows 11-17, its peak under the eye, a notch in its middle at the bottom), lit at its upper left; and two
steps (columns 2-9 and 14-20 of rows 18-20), their front edges lit, a dark ramp between them. The floor round it (rows
0-1 and 21-27, the columns at the sides) is the map's: left out.

Built as a CAD modeller would (polish_machine_kit): the pillars, the hood and the steps are prisms of their plan under
sloping tops (wedges), bevelled; ribs and the grille's bars are bevelled boxes; the eye is a lens turned about its
axis (which leans towards the game's camera), cut along smooth contours into its bands (polish_orb_red.band_split),
each glowing moderately in its own colour (0.25-0.7: the game's bloom burns strong emission white).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the floor (z = 0); origin at the
sprite's centre (pixel 12, 14): column c's left edge is x = c - 12, row r's top edge y = 14 - r.

Replaces wave3_i.py's deli_floor_eye(): remove it with its @model("deli_floor_eye", ...) registration and its line in
the docstring, and wave3_i_art.py's S45 (only deli_floor_eye() reads it), so that it doesn't overwrite this model.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouette against the
machine's own pixels, the floor left out, written below), --preview <prefix>.
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
from polish_orb_red import band_split  # noqa: E402

AXIS_X = -0.5                   # symmetric about the middle of column 11


def XE(c):
    return c - 12.0


def YE(r):
    return 14.0 - r


def P(c, r):
    return (XE(c), YE(r))


def ccw(pts):
    area = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))
    return pts if area > 0 else pts[::-1]


def plan(points):
    return ccw([P(c, r) for c, r in points])


def mirror_cols(points):
    """The mirror image of a plan (pixel edges) about the middle of column 11."""
    return [(23.0 - c, r) for c, r in points]


# The machine's own pixels ('#'): the floor round it left out.
OWN = """
........................
........................
....######.##.######....
....######.###.#####....
...#################....
..##################....
..##################....
...#################....
...#################....
...####.###....#####....
...#################....
..##################....
..##################....
...#################....
...#################....
..##################....
..#################.....
..#################.....
..##################....
..##################....
..##################....
........................
........................
........................
........................
........................
........................
........................
"""

PILLAR = [(3.5, 2.5), (9.3, 2.5), (9.5, 3.4), (9.5, 11.6), (3.4, 11.6), (3.4, 3.4)]  # the left one; mirrored
PILLAR_Z = (7.6, 6.2)           # its top at the back (row 2.5) and the front (row 11.6)
PILLAR_RIBS = [5.4, 7.4]        # the grooves down it (columns)
GRILLE = (9.5, 13.5, 2.6, 7.4, 4.4)  # columns, rows, the recess' floor
GRILLE_BARS = [10.3, 11.5, 12.7]
GRILLE_Z = 6.4
EYE = (11.5, 8.9, 5.3)          # column, row, height of its centre
EYE_RADII = (1.75, 2.55, 1.35)  # across, along the lean, bulge
EYE_AXIS = Vector((0.0, -0.62, 0.78)).normalized()  # it looks up and down the screen, at the game's camera
HOT_DIR = Vector((-0.12, 0.62, 0.78)).normalized()  # where its core is: the lens' upper end
EYE_BANDS = (0.62, 0.84, 0.95)  # the bands' cosines of the angle to HOT_DIR: orange, yellow, the hot spot
SOCKET = (2.5, 3.3)             # its socket's half-width and half-length
HOOD = [(2.6, 18.0), (2.6, 15.6), (5.8, 12.7), (9.2, 11.3), (11.5, 10.8), (13.8, 11.3), (17.2, 12.7), (20.4, 15.6),
        (20.4, 18.0), (14.4, 18.0), (12.6, 15.2), (10.4, 15.2), (8.6, 18.0)]
HOOD_Z = 5.8                    # its ridge's height under the eye
HOOD_FALL = (0.26, 0.22)        # how fast its top falls away from the ridge: sideways, down the screen
STEP = [(2.4, 17.6), (10.0, 17.6), (10.0, 21.0), (2.4, 21.0)]  # the left one; mirrored
STEP_Z = 2.9
RAMP = [(9.6, 15.0), (13.4, 15.0), (13.4, 21.0), (9.6, 21.0)]
RAMP_Z = (1.9, 0.9)


def materials(glow_scale=1.0):
    glow = k.level_palette()

    def mat(name, index, metallic=0.5, roughness=0.38):
        return k.material(name, palette=index, metallic=metallic, roughness=roughness)

    def lit(name, index, strength):
        return k.material(name, palette=index, metallic=0.0, roughness=0.14, emission=glow[index],
                          emission_strength=strength * glow_scale)
    return {
        "black": mat("feye_black", 0x01, 0.2, 0.6),
        "dark": mat("feye_dark", 0x03, 0.4, 0.5),
        "shade": mat("feye_shade", 0x05, 0.5, 0.42),
        "steel": mat("feye_steel", 0x07, 0.55, 0.36),
        "lit": mat("feye_lit", 0x09, 0.55, 0.32),
        "light": mat("feye_light", 0x0b, 0.55, 0.28),
        "eye_rim": lit("feye_eye_rim", 0x74, 0.3),
        "eye": lit("feye_eye", 0x77, 0.45),
        "eye_orange": lit("feye_eye_orange", 0x7a, 0.55),
        "eye_hot": lit("feye_eye_hot", 0x7d, 0.65),
    }


SUN = Vector((-0.45, 0.45, 0.77)).normalized()


def paint_by_normal(obj, top, side, under=None, lit=None, top_min=0.8):
    def pick(c, n):
        if n.z > top_min:
            return top
        if under is not None and n.z < 0.05:
            return under
        if lit is not None and n.dot(SUN) > 0.45:
            return lit
        return side
    mk.paint(obj, pick)


def block(name, outline, top, mat, bevel=0.45, segments=3, angle=35.0, bottom=0.0):
    top_fn = top if callable(top) else (lambda x, y, t=top: t)
    body = mk.wedge(name, plan(outline), bottom, top_fn, mat)
    mk.bevel(body, bevel, segments, angle)
    mk.shade(body, angle)
    return body


def slope_y(r0, z0, r1, z1):
    a0, a1 = YE(r0), YE(r1)
    return lambda x, y: z0 + (z1 - z0) * (y - a0) / (a1 - a0)


# --- The parts --------------------------------------------------------------------------------------------------

def pillars(m):
    """The two pillars at the back, their tops sloping down to the front, ribs (grooves) down them."""
    top = slope_y(2.5, PILLAR_Z[0], 11.6, PILLAR_Z[1])
    for side, outline in (("l", PILLAR), ("r", mirror_cols(PILLAR))):
        body = block(f"pillar_{side}", outline, top, m["steel"], bevel=0.55)
        cuts = []
        for c in PILLAR_RIBS:
            cc = c if side == "l" else 23.0 - c
            cuts.append(mk.box(f"rib_cut_{side}{c}", XE(cc) - 0.24, XE(cc) + 0.24, YE(11.0), YE(2.0), 0.0, 9.0))
        mk.boolean(body, cuts, "DIFFERENCE")
        mk.cleanup(body)
        mk.shade(body, 35)

        def pick(c, n, side=side):
            if n.z > 0.8:
                return m["steel"]
            if n.z < 0.05:
                return m["dark"]
            if abs(n.x) > 0.9 and c.z < top(c.x, c.y) - 0.15 and 0.5 < (c.x - XE(3.4 if side == "l" else 13.5)) < 5.6:
                return m["dark"]  # the grooves' walls
            if n.dot(SUN) > 0.45:
                return m["lit"]
            return m["shade"]
        mk.paint(body, pick)


def grille(m):
    """The dark recess between the pillars and the bars across it, their tops lit."""
    c0, c1, r0, r1, floor = GRILLE
    recess = mk.box("grille_recess", XE(c0), XE(c1), YE(r1), YE(r0), 0.0, floor, m["black"])
    mk.bevel(recess, 0.2, 2, 35)
    for i, c in enumerate(GRILLE_BARS):
        bar = mk.box(f"grille_bar{i}", XE(c) - 0.36, XE(c) + 0.36, YE(r1) + 0.1, YE(r0) - 0.1, 0.0, GRILLE_Z,
                     m["steel"])
        mk.bevel(bar, 0.22, 2, 35)
        mk.shade(bar, 35)
        paint_by_normal(bar, m["lit"], m["shade"], lit=m["steel"])


def eye(m):
    """The eye: a dark socket ring leaning towards the camera, the lens in it in glowing bands (a hot core at its
    upper left, orange, red, a dark red rim)."""
    c, r, z = EYE
    centre = Vector((XE(c), YE(r), z))
    turn = EYE_AXIS.to_track_quat("Z", "Y").to_matrix().to_4x4()
    place = Matrix.Translation(centre) @ turn
    hw, hl = SOCKET
    socket = mk.lathe("eye_socket", [(0.62, -1.6), (1.0, -1.4), (1.0, 0.25), (0.93, 0.45), (0.8, 0.4), (0.78, -0.2)],
                      (0.0, 0.0), m["black"], 32, squash=(hw, hl))
    socket.data.transform(place)
    k.smooth(socket, 45)
    rx, ry, bulge = EYE_RADII
    profile = []
    for i in range(9):
        t = (math.pi / 2) * i / 8
        profile.append((max(0.02, math.cos(t)), -0.35 + bulge * math.sin(t)))
    lens = mk.lathe("eye_lens", profile, (0.0, 0.0), m["eye_rim"], 32, squash=(rx, ry))
    lens.data.transform(place)
    values = [((v.co - centre).normalized()).dot(HOT_DIR) for v in lens.data.vertices]
    a, b, cc = EYE_BANDS
    band_split(lens, values, [(-9.0, m["eye_rim"]), (0.3, m["eye"]), (a, m["eye_orange"]), (b, m["eye_hot"])])
    k.smooth(lens, 60)


def plane_box(name, top, size=40.0):
    """Everything under the plane z = top(x, y), for intersecting with (polish_arch.py's)."""
    return mk.wedge(name, [(-size, -size), (size, -size), (size, size), (-size, size)], 0.0, top,
                    bottom=lambda x, y: top(x, y) - 200.0)


def hood(m):
    """The hood: a chevron of armour under the eye, its top two planes falling away from its ridge (the middle) to its
    sides and down the screen, so its left half faces the light; its edges bevelled."""
    fall_x, fall_y = HOOD_FALL
    ridge_y = YE(10.8)
    left = lambda x, y: HOOD_Z + fall_x * (x - AXIS_X) + fall_y * (y - ridge_y)
    right = lambda x, y: HOOD_Z - fall_x * (x - AXIS_X) + fall_y * (y - ridge_y)
    body = mk.prism("hood", plan(HOOD), 0.0, HOOD_Z + 4.0, m["steel"])
    for i, top in enumerate((left, right)):
        mk.boolean(body, plane_box(f"hood_plane{i}", top), "INTERSECT")
    mk.cleanup(body)
    mk.bevel(body, 0.6, 3, 20)
    mk.shade(body, 20)

    def pick(c, n):
        if n.z < 0.05:
            return m["dark"]
        if n.z > 0.6:
            return m["light"] if c.x < AXIS_X - 0.3 else m["steel"]
        if n.dot(SUN) > 0.45:
            return m["lit"]
        return m["shade"]
    mk.paint(body, pick)


def steps(m):
    """The two steps in front, their front edges lit, the dark ramp between them."""
    for side, outline in (("l", STEP), ("r", mirror_cols(STEP))):
        body = block(f"step_{side}", outline, STEP_Z, m["steel"], bevel=0.5)

        def pick(c, n):
            if n.z > 0.8:
                return m["steel"]
            if n.z < 0.05:
                return m["dark"]
            if n.y < -0.5:
                return m["lit"]  # the front edges (row 20)
            return m["shade"]
        mk.paint(body, pick)
    ramp = block("ramp", RAMP, slope_y(15.0, RAMP_Z[0], 21.0, RAMP_Z[1]), m["dark"], bevel=0.35)
    paint_by_normal(ramp, m["shade"], m["dark"])


def own_mask():
    lines = [line for line in OWN.strip("\n").split("\n")]
    return [[ch == "#" for ch in line] for line in lines]


def build():
    k.reset()
    options = k.args()
    m = materials()
    pillars(m)
    grille(m)
    hood(m)
    eye(m)
    steps(m)
    parts = mk.meshes()
    for obj in parts:
        mk.apply(obj)
    bpy.context.view_layer.update()
    if "check" in options:
        mk.compare("deli_floor_eye (x5e 45, its own pixels)", mk.coverage(parts, 24, 28), own_mask())
    bpy.context.scene.view_settings.view_transform = "Standard"
    mk.report("deli_floor_eye", parts, os.path.join(mk.outdir(options), "deli_floor_eye.glb"))
    if "preview" in options:
        mk.preview(options["preview"] + "deli_floor_eye", parts)


if __name__ == "__main__":
    build()
