"""The jawed guns lying in the leaves of TORM, BOTANY A, BOTANY B and BONUS (episode 2) and ROOST (episode 6):
sheet G sprites 229 beside 231 (gun A; enemies 753 and 754) and 267 beside 269 (gun B; enemies 756 and 757),
2x2 each: one 48 x 28 picture per gun; ground layer; the animations 229 233 237 237 237 237 233 233 233 233 229
(and 231 235 239 ..., 267 271 275 ..., 269 273 277 ...: no other enemy shows these sprites), polished (2026-10-19;
it replaces wave3_r.py's gun_whole() and gun_piece(), lofted hulls with boxes stuck on). models.cfg: model
jaw_gun_a_left / jaw_gun_a_right / jaw_gun_b_left / jaw_gun_b_right and their frame models ... origin; sprite g
229 jaw_gun_a_left yaw=0 height=-4 and so on; frame g 233 jaw_gun_a_left_233, frame g 235 jaw_gun_a_right_235 ...
The levels put the halves side by side: 753 (229) at x and 754 (231) at x + 24, at the same y (TORM's events 273,
413, 1029, ...; 756 (267) and 757 (269) likewise); ROOST (tools/content/episode6) shows 753 and 757 alone.

Gun B is gun A mirrored: 267 + 269 are 229 + 231 flipped left to right one pixel over (column c of B is column
46 - c of A, pixel for pixel, in every frame; only the leaves differ), so B is built as A, mirrored about x = -0.5
and cut again (the cut falls a pixel elsewhere on it).

As the sprites and their 4x upscales draw gun A (columns and rows of the 48 x 28 picture): a long grey jaw lying
along the screen, its mouth to the front (down the screen). The upper jaw (columns 7-31 of rows 0-8): a flat deck
(rows 1-6) whose back edge catches the light (row 1) and whose front lip is lit (row 6), a slot in it (columns
14-25 of rows 2-5) holding a pale lens (column 15) and a vent of light slats (columns 19-24); at its left end the
deck steps down (its lit edge, column 9) and the jaw's hinge, a thick grey C (columns 0-5 of rows 3-15, its rim
lit down column 3), wraps round its end from the deck down to the lower jaw, a groove between them; under the
deck's front the mouth (columns 7-30 of rows 9-13): teeth hanging from the upper jaw and standing on the lower one
(columns 10-19), a dark red lamp glowing in its throat (columns 20-24 of rows 10-13), the lower jaw along the
bottom (rows 13-15) and three fangs reaching down from it into the leaves (columns 13-21 of rows 15-18). At the
deck's right end a flange (column 31), two rods out from it (columns 32-37, rows 3 and 5) to the gun's bracket: a
post (columns 38-40 of rows 1-7) that bends down to the left as a brace to the jaw's front corner (rows 8-14), a
box on the post's right side (columns 42-45 of rows 3-7) and under it the gun's red lens (columns 39-43 of rows
9-13), its long axis slanting (the barrel points down the screen and to the right).

The frames fire it: in 233 the vent's slats turn (the slot darkens), a fireball swells in the mouth (red to
yellow, rows 9-14) and the lens burns hotter; in 237 the slats stand open (the slot black), the fireball is bigger
and white-hot inside and the lens flares white in a long flash (columns 36-44 of rows 8-15). One model per frame
and half: the same jaw, the slats, the fireball and the muzzle changed.

The leaves round it (and the black of their shadows) are the map's: TORM's and BOTANY's leaves; the model leaves
them out. Built as a CAD modeller would (polish_machine_kit): the jaws are side profiles extruded across and
bevelled, the slot cut in with an exact boolean, the C and the bracket bars swept along their paths, the rods,
the lens and the barrel turned. The whole gun is then cut along the sprites' edge (polish_arch.py's cut(): the
pieces keep the whole's shading across the cut), each piece moved so its sprite's centre is its origin.

Where it stands: models drawn at their origin stand at the ground enemies' layer, about 4 pixels above the terrain;
"height=-4" on the sprite lines sets the jaw on the leaves (its base reaches SKIRT below z = 0, so no gap shows on
uneven ground).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the ground (z = 0); the
whole's origin is the edge between the two sprites at their middle (column c of the picture is x = c + 0.5 - 24,
row r is y = 13.5 - r).

Replaces wave3_r.py's jawed guns: remove GUN_ORIGIN, gpx(), gpy(), hull_along_x(), gun_whole(), the two
r.whole("gun_a" / "gun_b", ...) lines, gun_piece() and the four r.model("jaw_gun_...") lines (and the guns' lines of
its docstring and usage; keep the mortar, which wave3_ap_mortar.py loads), and wave3_r_art.py's GUN_A, GUN_A_FIRE and
GUN_B (nothing reads them), so that they don't overwrite these models.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes of the
whole and of each piece against the gun's own pixels, written below), --preview <prefix>, --only <name,...> (model
names, or a, b, cold, charge, fire).
"""
import math
import os
import sys

import bmesh
import bpy
import mathutils.noise as noise
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_arch import cut  # noqa: E402  (polish_machine_kit.cut without its material indices shifted twice)


def XE(c):
    """The left edge of the picture's column c (fractions allowed)."""
    return c - 24.0


def YE(r):
    """The top edge of the picture's row r."""
    return 14.0 - r


def P(c, r):
    return (XE(c), YE(r))


# Gun A's own pixels in the 48 x 28 picture, by rows (row, [(first column, last column), ...]): the jaw, the
# bracket, the gun and their dark outline; the leaves and their shadows left out. Gun B's are these mirrored (column c
# of B is column 46 - c of A).
OWN = [(0, [(10, 31), (37, 41)]), (1, [(8, 32), (37, 41)]), (2, [(7, 46)]), (3, [(6, 46)]), (4, [(3, 46)]),
       (5, [(2, 46)]), (6, [(1, 46)]), (7, [(0, 46)]), (8, [(0, 45)]), (9, [(0, 44)]), (10, [(0, 44)]), (11, [(0, 44)]),
       (12, [(0, 43)]), (13, [(0, 42)]), (14, [(1, 25), (30, 41)]), (15, [(2, 23), (30, 36)]), (16, [(10, 23)]),
       (17, [(11, 23)]), (18, [(10, 24)])]

# The models: (gun, state, left name, right name, left sprite, right sprite).
MODELS = [
    ("a", "cold", "jaw_gun_a_left", "jaw_gun_a_right", 229, 231),
    ("a", "charge", "jaw_gun_a_left_233", "jaw_gun_a_right_235", 233, 235),
    ("a", "fire", "jaw_gun_a_left_237", "jaw_gun_a_right_239", 237, 239),
    ("b", "cold", "jaw_gun_b_left", "jaw_gun_b_right", 267, 269),
    ("b", "charge", "jaw_gun_b_left_271", "jaw_gun_b_right_273", 271, 273),
    ("b", "fire", "jaw_gun_b_left_275", "jaw_gun_b_right_277", 275, 277),
]
MIRROR_X = -0.5                 # gun B is gun A mirrored about x = MIRROR_X
SKIRT = 1.5                     # how far the base reaches below the ground (z = 0)

# --- Gun A's measures ----------------------------------------------------------------------------------------
# The upper jaw: its side profile (y, z), from its foot at the back round over the deck, down its lit lip and front
# face, under the palate (the mouth's roof) and down the throat; extruded across from JAW_X[0] to JAW_X[1].
JAW_X = (XE(5.6), XE(31.0))
DECK_Z = 8.6
JAW_PROFILE = [(13.35, -SKIRT), (13.35, 7.1), (12.35, DECK_Z), (7.3, DECK_Z), (6.4, 7.75), (5.35, 6.05),
               (5.3, 5.0), (6.1, 4.45), (9.6, 4.45), (10.2, -SKIRT)]
# Its plan: the back left corner cut off (rows 1-3: the outline runs from column 8 to column 6).
JAW_PLAN = [P(5.6, 15.0), P(31.2, 15.0), P(31.2, -0.5), P(8.6, -0.5), P(5.6, 3.6)]
# The deck's left end steps down (its edge lit, column 9) to the jaw's end (columns 6-8).
STEP_X, STEP_Z = XE(9.2), 7.7
LIP_Y = (5.9, 7.4)              # the lit lip along the deck's front
# The slot in the deck (columns 14-25 of rows 2-5): x0, x1, y0, y1, depth; the divider between the lens and the vent.
SLOT = (XE(14.25), XE(25.05), YE(5.75), YE(2.25), 1.35)
DIVIDER = (XE(18.05), XE(18.9))
BEZEL = 0.5                     # the raised frame round the slot
RIVETS = [P(27.4, 2.6), P(29.6, 2.6), P(27.4, 5.2), P(29.6, 5.2), P(11.6, 3.0), P(11.6, 5.0)]
LENS = (XE(15.75), YE(3.75), 1.1, 1.0, 0.9)        # x, y, radii, height (on the slot's floor)
VENT = (XE(19.15), XE(24.85))   # the slats' x
SLATS = 4                       # how many slats across the vent (each turns about its own axis, along x)
SLAT_TURN = {"cold": 0.0, "charge": 52.0, "fire": 86.0}
# The hinge's C round the jaw's left end (columns 1-4 of rows 3-14, lit down column 3; a groove, column 5, between
# it and the upper jaw): its path (x, y, z), half-width, height above the path.
C_PATH = [(XE(9.8), YE(3.3), 7.2), (XE(6.6), YE(3.7), 7.2), (XE(4.4), YE(4.8), 7.1), (XE(2.9), YE(6.9), 6.8),
          (XE(2.4), YE(9.4), 6.2), (XE(2.8), YE(12.0), 5.0), (XE(4.2), YE(13.8), 3.8), (XE(6.6), YE(14.6), 3.0),
          (XE(9.0), YE(14.8), 2.6)]
C_HALF, C_TOP = 1.85, 1.2
CHEEK = (XE(4.4), XE(8.2), YE(14.2), YE(8.4), 3.4)      # the mouth's dark left wall inside the C: x0, x1, y0, y1, top
# The lower jaw (rows 13-15): its profile (y, z), extruded across.
LOW_X = (XE(5.4), XE(19.7))
LOW_PROFILE = [(-1.35, -SKIRT), (-1.35, 1.9), (-0.55, 3.0), (1.55, 3.2), (2.35, 2.5), (2.4, -SKIRT)]
FLOOR = (XE(4.4), XE(30.6), YE(13.9), YE(4.6), 0.9)     # the mouth's dark floor
# The teeth: the upper ones hang from the palate's front edge, the lower ones stand on the lower jaw (x of each).
UPPER_TEETH = [XE(c) + 0.5 for c in (11, 13, 15, 17, 19)]
LOWER_TEETH = [XE(c) + 0.5 for c in (10, 12, 14, 16, 18)]
# The fangs from the lower jaw's front down into the leaves: (root x, tip x).
FANGS = [(XE(13.6), XE(15.9)), (XE(16.6), XE(18.9)), (XE(19.6), XE(21.9))]
FANG_ROOT = (YE(14.9), 2.0)     # y, z of the roots
FANG_TIP = (YE(18.8), -0.6)     # y, z of the tips
# The throat's lamp (cold) and the fireball (charge, fire): centre, radii.
THROAT = Vector((XE(22.0) + 0.5, YE(11.7), 2.3))
FIREBALL = {"charge": (Vector((XE(22.0), YE(11.9), 2.5)), 2.35), "fire": (Vector((XE(22.0), YE(12.0), 2.9)), 3.05)}
# The flange at the deck's right end (column 31): x0, x1 and its outline (y, z).
FLANGE_X = (XE(30.9), XE(31.85))
FLANGE = [(6.55, -SKIRT), (6.55, 8.2), (7.45, 9.25), (12.3, 9.25), (13.15, 8.4), (13.15, -SKIRT)]
RODS = [(YE(3.5), 6.6), (YE(5.6), 6.2)]       # the two rods: y, z (from the flange to the post)
ROD_R = 0.82
# The bracket: the post (columns 38-40 of rows 1-7) bending into the brace down to the jaw's front corner; the path
# (x, y, z) of its top's middle, half-width, height above the path (its bottom reaches the ground).
BRACKET = [(XE(39.55), YE(0.75), 9.4), (XE(39.55), YE(6.2), 9.4), (XE(38.8), YE(8.0), 8.7), (XE(35.8), YE(11.0), 6.3),
           (XE(33.2), YE(13.6), 4.0)]
BRACKET_HALF, BRACKET_TOP = 1.5, 0.95
FOOT = (XE(30.6), XE(35.4), YE(14.9), YE(11.7), 3.6)     # the brace's foot on the jaw's corner
BASE = (XE(30.6), XE(37.6), YE(11.8), YE(5.9), 3.9)      # the dark base under the rods (rows 6-11)
POD = (XE(40.95), XE(46.4), YE(7.75), YE(2.35), 7.3)      # the box on the post: x0, x1, y0, y1, top
# The gun: the lens' centre, the barrel's axis (out of the lens), the barrel's length behind it, radii.
MUZZLE = Vector((XE(41.3), YE(11.5), 3.5))
MUZZLE_AXIS = Vector((0.52, -0.52, 0.68)).normalized()
BARREL_LENGTH, BARREL_R, RING_R, LENS_R = 4.0, 2.05, 2.4, 1.95

# The red lights by state: the throat's lamp or fireball (layers: palette index, glow) and the gun's lens (rim and
# core), and the flash.
LIGHTS = {
    "cold": {"throat": [(0x72, 1.0), (0x74, 1.5)], "lens": [(0x75, 1.4), (0x7b, 2.2)]},
    "charge": {"throat": [(0x75, 1.6), (0x79, 2.3), (0x7b, 3.0)], "lens": [(0x77, 1.9), (0x7d, 2.8)]},
    "fire": {"throat": [(0x76, 1.9), (0x7b, 2.7), (0x7e, 3.4)], "lens": [(0x7a, 2.5), (0x7f, 3.4)]},
}


def materials(state):
    glow = k.level_palette()

    def mat(name, index, metallic=0.5, roughness=0.4):
        return k.material(name, palette=index, metallic=metallic, roughness=roughness)

    def lit(name, index, strength, roughness=0.2):
        return k.material(name, palette=index, metallic=0.0, roughness=roughness, emission=glow[index],
                          emission_strength=strength)
    m = {
        "black": mat("jaw_black", 0x01, 0.2, 0.7),
        "dark": mat("jaw_dark", 0x02, 0.45, 0.5),
        "steel": mat("jaw_steel", 0x04, 0.55, 0.42),
        "face": mat("jaw_face", 0x06, 0.5, 0.4),
        "grey": mat("jaw_grey", 0x08, 0.5, 0.36),
        "light": mat("jaw_light", 0x0a, 0.5, 0.32),
        "edge": mat("jaw_edge", 0x0c, 0.5, 0.28),
        "lens": lit("jaw_lens", 0x0d, 0.7, 0.08),
    }
    for role in ("throat", "lens"):
        for i, (index, strength) in enumerate(LIGHTS[state][role]):
            m[(role, i)] = lit(f"jaw_{role}{i}_{index:x}", index, strength)
    return m


# --- Helpers -----------------------------------------------------------------------------------------------------

def swept(name, path, half_width, top, mat, power=3.2, segments=16, iterations=2):
    """A bar swept along a path of (x, y, z) (its corners rounded): rounded-box sections half_width across, reaching
    top above the path and down to below the ground; its bottom cut off at -SKIRT."""
    dense = mk.chaikin([tuple(p) for p in path], iterations, closed=False)
    points = [Vector(p) for p in dense]
    ups = [Vector((0, 0, 1))] * len(points)
    depth = max(p.z for p in points) + SKIRT + 0.5
    obj = mk.bar(name, points, ups, half_width, top, depth, mat, segments, power)
    clip_below(obj, -SKIRT)
    return obj


def clip_below(obj, z):
    """Cuts an object off below z (closing the cut)."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    result = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-5, plane_co=(0, 0, z),
                                    plane_no=(0, 0, -1), clear_outer=True)
    edges = [e for e in result["geom_cut"] if isinstance(e, bmesh.types.BMEdge) and e.is_valid and e.is_boundary]
    if edges:
        bmesh.ops.holes_fill(bm, edges=edges, sides=0)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    return obj


def axis_frame(d):
    """Two unit vectors across a direction d (the first level)."""
    d = Vector(d).normalized()
    a = d.cross(Vector((0, 0, 1)))
    if a.length < 1e-6:
        a = Vector((1, 0, 0))
    a.normalize()
    return a, d.cross(a).normalized()


def turned(name, profile, origin, d, mat, segments=24, start=None, end=None):
    """A round part about the axis from origin along d: profile [(distance along d, radius), ...]."""
    a, b = axis_frame(d)
    rings = []
    for t, r in profile:
        c = origin + d * t
        rings.append([c + (a * math.cos(2 * math.pi * j / segments) + b * math.sin(2 * math.pi * j / segments)) * r
                      for j in range(segments)])
    return k.loft(name, rings, mat, start_point=start, end_point=end)


def lumpy_ball(name, centre, radius, mat, squash=(1.0, 1.0, 0.85), wobble=0.12, seed=0.0, subdivisions=3):
    """A fireball: an icosphere of radius (scaled by squash), its surface wobbled by noise."""
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subdivisions, radius=1.0)
    for v in bm.verts:
        d = v.co.normalized()
        n = noise.noise(d * 2.2 + Vector((seed, seed * 0.7, 0.3)))
        r = radius * (1.0 + wobble * n)
        v.co = centre + Vector((d.x * squash[0], d.y * squash[1], d.z * squash[2])) * r
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.data.materials.append(mat)
    return k.smooth(obj, 80)


# --- The parts (gun A) ------------------------------------------------------------------------------------------

def upper_jaw(m):
    """The upper jaw: its side profile extruded across, the slot cut into its deck, its edges bevelled; the deck
    grey, its back edge and front lip lit, its front face darker, the slot black inside."""
    body = mk.prism("upper_jaw", JAW_PROFILE, JAW_X[0], JAW_X[1], m["grey"], axis="x")
    mk.boolean(body, mk.prism("upper_jaw_plan", JAW_PLAN, -SKIRT - 1.0, DECK_Z + 2.0), "INTERSECT")
    mk.boolean(body, mk.box("step_cut", JAW_X[0] - 1.0, STEP_X, -5.0, 20.0, STEP_Z, DECK_Z + 2.0), "DIFFERENCE")
    mk.cleanup(body)
    mk.bevel(body, 0.42, 3, 30)
    # The slot cut after the bevel: its edges stay sharp under the bezel, so the deck's normals stay flat.
    x0, x1, y0, y1, depth = SLOT
    slot = mk.box("slot_cut", x0, x1, y0, y1, DECK_Z - depth, DECK_Z + 2.0)
    mk.boolean(body, slot, "DIFFERENCE")
    mk.cleanup(body, dissolve=0.0)
    mk.shade(body, 35)

    def pick(c, n):
        in_slot = x0 - 0.05 < c.x < x1 + 0.05 and y0 - 0.05 < c.y < y1 + 0.05 and c.z < DECK_Z - 0.05
        if in_slot:
            return m["black"] if n.z > 0.8 else m["dark"]
        if c.z > DECK_Z - 0.6 and n.z > 0.5 and n.y > 0.3:
            return m["edge"]        # the back edge (row 1)
        if abs(c.x - STEP_X) < 0.7 and n.x < -0.35 and c.z > STEP_Z - 0.3:
            return m["edge"]        # the step at the deck's left end (column 9)
        if LIP_Y[0] < c.y < LIP_Y[1] + 0.3 and c.z > 6.0 and n.z > 0.2:
            return m["light"]       # the lit lip (row 6)
        if c.z < 4.6 and n.z < 0.5:
            return m["black"]       # the palate and the throat
        if n.z < 0.45 and n.y < -0.3:
            return m["face"]        # the front face (rows 7-8)
        return None
    mk.paint(body, pick)
    return body


def slot_parts(m, state):
    """In the slot: the lens on its floor (left), the divider, the vent's slats (right), turned by state."""
    x0, x1, y0, y1, depth = SLOT
    floor = DECK_Z - depth
    # A raised bezel round the slot, its top lit.
    bezel = mk.box("bezel", x0 - BEZEL, x1 + BEZEL, y0 - BEZEL, y1 + BEZEL, DECK_Z - 0.5, DECK_Z + 0.32, m["grey"])
    mk.boolean(bezel, mk.box("bezel_hole", x0, x1, y0, y1, DECK_Z - 1.0, DECK_Z + 1.0), "DIFFERENCE")
    mk.cleanup(bezel)
    mk.bevel(bezel, 0.16, 2, 35)
    mk.shade(bezel, 35)
    mk.paint(bezel, lambda c, n: m["light"] if n.z > 0.85 else m["dark"] if x0 - 0.05 < c.x < x1 + 0.05 and
             y0 - 0.05 < c.y < y1 + 0.05 else None)
    # Rivets on the deck either side of the slot.
    for i, (x, y) in enumerate(RIVETS):
        mk.dome(f"rivet{i}", (x, y), (0.38, 0.38, 0.22), DECK_Z - 0.05, m["light"], 12, 4)
    d0, d1 = DIVIDER
    div = mk.box("divider", d0, d1, y0 - 0.1, y1 + 0.1, floor - 0.2, DECK_Z - 0.15, m["steel"])
    mk.bevel(div, 0.15, 2, 35)
    mk.shade(div, 35)
    lx, ly, rx, ry, h = LENS
    socket = mk.lathe("lens_socket", [(1.0, floor - 0.05), (1.0, floor + 0.3), (0.86, floor + 0.42),
                                      (0.7, floor + 0.3)], (lx, ly), m["dark"], 32, squash=(rx + 0.25, ry + 0.25))
    k.smooth(socket, 45)
    mk.dome("lens", (lx, ly), (rx, ry, h), floor + 0.1, m["lens"], 32, 8)
    # The slats: thin plates across the vent, each turned about its axis along x (their front edges dropping).
    v0, v1 = VENT
    pitch = (y1 - y0 - 0.2) / SLATS
    turn = math.radians(SLAT_TURN[state])
    for i in range(SLATS):
        yc = y0 + 0.1 + pitch * (i + 0.5)
        zc = DECK_Z - 0.45
        slat = mk.box(f"slat{i}", v0 + 0.05, v1 - 0.05, -pitch * 0.47, pitch * 0.47, -0.09, 0.09, m["light"])
        mk.bevel(slat, 0.05, 1, 35)
        slat.data.transform(Matrix.Translation((0, yc, zc)) @ Matrix.Rotation(turn, 4, "X"))
        mk.shade(slat, 35)
        mk.paint(slat, lambda c, n: m["steel"] if n.z < 0.6 else None)
    # A pivot rod along each end of the vent.
    for i, x in enumerate((v0 - 0.15, v1 + 0.15)):
        mk.box(f"slat_rail{i}", x - 0.2, x + 0.2, y0 + 0.05, y1 - 0.05, floor, DECK_Z - 0.3, m["dark"])


def hinge(m):
    """The jaw's hinge at its left end: a thick C swept round the upper jaw's end (a groove between them) from the
    deck down to the lower jaw, lit along its rim; the mouth's dark left wall inside it."""
    c = swept("hinge", C_PATH, C_HALF, C_TOP, m["grey"], power=5.0, segments=24)
    k.smooth(c, 50)
    mk.paint(c, lambda c_, n: m["face"] if n.z < 0.25 else None)
    x0, x1, y0, y1, top = CHEEK
    cheek = mk.box("cheek", x0, x1, y0, y1, -SKIRT, top, m["dark"])
    mk.bevel(cheek, 0.4, 2, 35)
    mk.shade(cheek, 35)


def lower_jaw(m):
    """The lower jaw along the bottom: its profile extruded across, bevelled; the teeth on it and under the palate,
    the mouth's dark floor; the three fangs reaching down from its front into the leaves."""
    body = mk.prism("lower_jaw", LOW_PROFILE, LOW_X[0], LOW_X[1], m["steel"], axis="x")
    mk.bevel(body, 0.35, 3, 30)
    mk.shade(body, 35)
    mk.paint(body, lambda c, n: m["face"] if n.z > 0.8 else m["dark"] if n.y < -0.6 and c.z < 1.4 else None)
    x0, x1, y0, y1, top = FLOOR
    floor = mk.box("mouth_floor", x0, x1, y0, y1, -SKIRT, top, m["black"])
    mk.bevel(floor, 0.2, 1, 35)
    # The upper teeth: blades hanging from the palate's front edge, pointing down and a little forward.
    for i, x in enumerate(UPPER_TEETH):
        tooth = mk.wedge(f"upper_tooth{i}", [(x - 0.55, 3.7), (x + 0.55, 3.7), (x + 0.4, 6.0), (x - 0.4, 6.0)], 0.0,
                         lambda x_, y_: 4.9, m["grey"], bottom=lambda x_, y_: 1.6 + 1.1 * (y_ - 3.7))
        mk.bevel(tooth, 0.14, 2, 30)
        mk.shade(tooth, 35)
        mk.paint(tooth, lambda c, n: m["light"] if n.y < -0.5 else None)
    for i, x in enumerate(LOWER_TEETH):
        tooth = mk.wedge(f"lower_tooth{i}", [(x - 0.4, 1.0), (x + 0.4, 1.0), (x + 0.32, 2.2), (x - 0.32, 2.2)], 0.0,
                         lambda x_, y_: 3.0 + 0.8 * (y_ - 1.0), m["face"], bottom=lambda x_, y_: 1.0)
        mk.bevel(tooth, 0.12, 2, 30)
        mk.shade(tooth, 35)
    # The fangs: curved cones from the lower jaw's front down into the leaves, slanting to the right.
    ry, rz = FANG_ROOT
    ty, tz = FANG_TIP
    for i, (rx, tx) in enumerate(FANGS):
        path = [(rx, ry + 0.9, rz + 0.6, 0.95), (rx + 0.5, ry - 0.6, rz + 0.1, 0.85),
                ((rx + tx) / 2 + 0.3, (ry + ty) / 2 - 0.2, (rz + tz) / 2 + 0.35, 0.6), (tx, ty, tz, 0.12)]
        fang = mk.smooth_tube(f"fang{i}", path, m["steel"], 12, iterations=2)
        k.smooth(fang, 60)
        mk.paint(fang, lambda c, n: m["face"] if n.z > 0.6 else None)


def throat(m, state):
    """The red lamp glowing in the throat (cold), or the fireball swelling out of it (charge, fire)."""
    layers = LIGHTS[state]["throat"]
    if state == "cold":
        # A capsule lamp lying across the throat, a hotter core showing along its top.
        lamp = turned("throat_lamp", [(0.0, 0.01), (0.25, 0.75), (0.8, 1.05), (3.6, 1.05), (4.15, 0.75), (4.4, 0.01)],
                      THROAT - Vector((2.2, 0, 0)), Vector((1, 0, 0)), m[("throat", 0)], 20)
        k.smooth(lamp, 70)
        core = k.ellipsoid("throat_core", tuple(THROAT + Vector((-0.15, 0.1, 0.55))), (1.6, 0.55, 0.45),
                           m[("throat", 1)], 16, 8)
        k.smooth(core, 70)
        return
    centre, radius = FIREBALL[state]
    # Three layers, concentric seen from above (a red rim, an orange ring, a yellow core): the outer one flat, each
    # inner one rounder and raised (and a little nearer the camera, down the screen) so it bulges out of the one
    # round it, as the sprite's fireball is hottest in its middle.
    shapes = [(1.0, (1.0, 0.92, 0.62), 0.0), (0.74, (1.0, 0.95, 0.9), 0.3), (0.46, (1.0, 1.0, 1.0), 0.66)]
    for i, (share, squash, rise) in enumerate(shapes[:len(layers)]):
        offset = Vector((0.0, -0.18 * rise, rise)) * radius
        lumpy_ball(f"fireball{i}", centre + offset, radius * share, m[("throat", i)], squash, 0.16 - 0.04 * i,
                   seed=1.7 * i + (0.0 if state == "charge" else 3.1))


def right_end(m):
    """The flange at the deck's right end, the two rods out to the bracket."""
    flange = mk.prism("flange", FLANGE, FLANGE_X[0], FLANGE_X[1], m["grey"], axis="x")
    mk.bevel(flange, 0.3, 2, 30)
    mk.shade(flange, 35)
    mk.paint(flange, lambda c, n: m["edge"] if n.z > 0.6 else None)
    x0, x1 = FLANGE_X[1] - 0.1, BRACKET[0][0] - BRACKET_HALF + 0.2
    for i, (y, z) in enumerate(RODS):
        rod = turned(f"rod{i}", [(0.0, ROD_R), (x1 - x0, ROD_R)], Vector((x0, y, z)), Vector((1, 0, 0)), m["grey"], 16)
        k.smooth(rod, 50)
        mk.paint(rod, lambda c, n: m["light"] if n.z > 0.75 else None)
        for j, t in enumerate((0.35, x1 - x0 - 0.35)):
            collar = turned(f"rod{i}_collar{j}", [(t - 0.35, ROD_R + 0.28), (t + 0.35, ROD_R + 0.28)],
                            Vector((x0, y, z)), Vector((1, 0, 0)), m["steel"], 16)
            k.smooth(collar, 40)


def bracket(m):
    """The gun's bracket: the post bending into the brace down to the jaw's front corner (one swept bar, its top
    lit), its foot; the box on the post."""
    bar = swept("bracket", BRACKET, BRACKET_HALF, BRACKET_TOP, m["grey"], power=4.5, segments=24, iterations=2)
    k.smooth(bar, 50)
    mk.paint(bar, lambda c, n: m["light"] if n.z > 0.8 else m["face"] if n.z < 0.2 else None)
    x0, x1, y0, y1, top = FOOT
    foot = mk.box("bracket_foot", x0, x1, y0, y1, -SKIRT, top, m["face"])
    mk.bevel(foot, 0.45, 3, 35)
    mk.shade(foot, 35)
    mk.paint(foot, lambda c, n: m["grey"] if n.z > 0.8 else None)
    x0, x1, y0, y1, top = BASE
    base = mk.box("base", x0, x1, y0, y1, -SKIRT, top, m["dark"])
    mk.bevel(base, 0.4, 2, 35)
    mk.shade(base, 35)
    x0, x1, y0, y1, top = POD
    pod = mk.box("pod", x0, x1, y0, y1, -SKIRT, top, m["grey"])
    mk.bevel(pod, 0.6, 3, 35)
    mk.shade(pod, 35)
    mk.paint(pod, lambda c, n: m["light"] if n.z > 0.85 else m["dark"] if n.y < -0.6 else
             m["face"] if n.z < 0.3 else None)
    # A seam round the pod's top, and two bolts on it.
    for i, x in enumerate((x0 + 1.1, x1 - 1.1)):
        mk.dome(f"pod_bolt{i}", (x, y1 - 1.0), (0.42, 0.42, 0.25), top - 0.05, m["steel"], 12, 4)


def gun(m, state):
    """The gun under the box: a barrel pointing down the screen and to the right, a ring at its mouth and the red
    lens in it (hotter as it fires); firing, a flash flaring from the lens."""
    d = MUZZLE_AXIS
    back = MUZZLE - d * BARREL_LENGTH
    barrel = turned("barrel", [(0.0, BARREL_R * 0.9), (0.4, BARREL_R), (BARREL_LENGTH - 0.9, BARREL_R),
                               (BARREL_LENGTH - 0.75, RING_R), (BARREL_LENGTH + 0.1, RING_R),
                               (BARREL_LENGTH + 0.25, RING_R - 0.25), (BARREL_LENGTH + 0.25, LENS_R + 0.05)],
                    back, d, m["steel"], 28, start=tuple(back))
    k.smooth(barrel, 40)
    mk.paint(barrel, lambda c, n: m["face"] if (Vector(c) - back).dot(d) > BARREL_LENGTH - 0.8 else None)
    lens = turned("muzzle_lens", [(BARREL_LENGTH - 0.1, LENS_R + 0.05), (BARREL_LENGTH + 0.3, LENS_R),
                                  (BARREL_LENGTH + 0.55, LENS_R * 0.8), (BARREL_LENGTH + 0.7, LENS_R * 0.45),
                                  (BARREL_LENGTH + 0.75, 0.01)], back, d, m[("lens", 0)], 28)
    k.smooth(lens, 70)
    hot = turned("muzzle_core", [(BARREL_LENGTH + 0.35, LENS_R * 0.62), (BARREL_LENGTH + 0.62, LENS_R * 0.45),
                                 (BARREL_LENGTH + 0.8, 0.01)], back, d, m[("lens", 1)], 20)
    k.smooth(hot, 70)
    if state == "cold":
        return
    # The flash: flattened flares in front of the lens, broad across its face (the sprite's long slanting flash),
    # the hotter ones inside; firing, a short flame along the barrel's axis too.
    a, b = axis_frame(d)
    face = MUZZLE + d * 0.8
    flares = [(2.4, 0.55, ("lens", 0)), (1.6, 0.75, ("lens", 1))] if state == "charge" else \
        [(3.4, 0.7, ("lens", 0)), (2.4, 0.95, ("lens", 1))]
    frame = Matrix((a.to_4d(), d.to_4d(), b.to_4d(), (0, 0, 0, 1))).transposed()
    for i, (radius, thick, role) in enumerate(flares):
        # A lumpy flare, its thin axis along d, drawn out across the lens' face (along a: the sprite's long
        # slanting flash).
        flare = lumpy_ball(f"flare{i}", Vector((0, 0, 0)), radius, m[role], (1.3, thick / radius, 0.95), 0.2,
                           seed=4.3 + 2.1 * i + (0.0 if state == "charge" else 1.3))
        frame.translation = face + d * (thick * 0.6 + 0.15 * i)
        flare.data.transform(frame)
    if state == "fire":
        flame = turned("flame", [(0.2, 1.4), (1.0, 1.25), (2.0, 0.8), (2.9, 0.3), (3.4, 0.01)], face, d,
                       m[("lens", 1)], 18)
        k.smooth(flame, 70)


def build_whole(state):
    """Gun A in one state, every part's modifiers applied."""
    m = materials(state)
    upper_jaw(m)
    slot_parts(m, state)
    hinge(m)
    lower_jaw(m)
    throat(m, state)
    right_end(m)
    bracket(m)
    gun(m, state)
    whole = mk.meshes()
    for obj in whole:
        mk.apply(obj)
    bpy.context.view_layer.update()
    return whole, m


def mirrored(objects, axis_x):
    """The objects mirrored about x = axis_x (their shading kept: the corner normals follow)."""
    flip = Matrix.Translation((2 * axis_x, 0, 0)) @ Matrix.Scale(-1, 4, (1, 0, 0))
    for obj in objects:
        obj.data.transform(flip)
        obj.data.flip_normals()
        obj.data.update()
    return objects


def own_mask(gun, c0=0, columns=48):
    mask = [[False] * 48 for _ in range(28)]
    for r, spans in OWN:
        for first, last in spans:
            for c in range(first, last + 1):
                mask[r][c] = True
    if gun == "b":
        mask = [[row[46 - c] if 0 <= 46 - c < 48 else False for c in range(48)] for row in mask]
    return [row[c0:c0 + columns] for row in mask]


def build():
    options = k.args()
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    for gun, state, left, right, left_sprite, right_sprite in MODELS:
        if only and not ({gun, state, left, right} & set(only)):
            continue
        k.reset()
        whole, m = build_whole(state)
        if gun == "b":
            mirrored(whole, MIRROR_X)
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        print("whole gun %s (%s): %d triangles, %d objects" % (gun, state, mk.triangles(whole), len(whole)))
        if "check" in options and state == "cold":
            mk.compare("whole gun %s (%d + %d, its own pixels)" % (gun, left_sprite, right_sprite),
                       mk.coverage(whole, 48, 28), own_mask(gun))
        if "preview" in options:
            mk.preview(options["preview"] + "jaw_gun_%s_%s_whole" % (gun, state), whole, size=(48, 28), scale=8,
                       distance=1.7)
        for name, sprite, box, c0 in ((left, left_sprite, (-24.0, 0.0, -14.0, 14.0), 0),
                                      (right, right_sprite, (0.0, 24.0, -14.0, 14.0), 24)):
            pieces = [p for p in (cut(src, box, m["dark"]) for src in whole) if p is not None]
            mk.transform(pieces, Matrix.Translation((-(box[0] + box[1]) / 2, 0, 0)))
            bpy.context.view_layer.update()
            for src in whole:
                src.hide_render = True
            if "check" in options and state == "cold":
                mk.compare("%s (G %d)" % (name, sprite), mk.coverage(pieces, 24, 28), own_mask(gun, c0, 24))
            mk.report(name, pieces, os.path.join(out, name + ".glb"))
            if "preview" in options:
                mk.preview(options["preview"] + name, pieces)
            for obj in pieces:
                bpy.data.objects.remove(obj)
            for src in whole:
                src.hide_render = False


if __name__ == "__main__":
    build()
