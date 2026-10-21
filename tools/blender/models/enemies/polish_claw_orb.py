"""The black orb of the asteroid levels (sheet S sprites 39 and 41 above 77 and 79, 2x2 each: one 48 x 56 picture;
ground layer; ASTEROID1, ASTEROID2, ASTEROID?, ASTCITY and AST. CITY, enemies 309-312 of episodes 1-3, AST ROCK and
GREY MOON, enemies 1001-1004 of episodes 5 and 6), polished (2026-10-21; it replaces wave3_u_orb.py's orb_whole(), a
plain black ellipsoid with a glint between bronze ellipsoids, tubes for claws and a small glowing ball). models.cfg:
model claw_orb_tl / _tr / _bl / _br ... origin (unchanged) and the frame models claw_orb_bl_81, claw_orb_bl_85,
claw_orb_br_83, claw_orb_br_87 (new); sprite s 39 claw_orb_tl yaw=0 height=-4 and the same for 41, 77, 79; frame s
81 claw_orb_bl_81, frame s 85 claw_orb_bl_85, frame s 83 claw_orb_br_83, frame s 87 claw_orb_br_87.

The levels always place the four as a square (event 12, "4-part enemy": 309 (77) at (x, y), 310 (79) 24 pixels to its
right, 311 (39) 28 pixels up the screen, 312 (41) both), on the ground. Each runs the same 20 frames, in step: 39 39
39 39 43 43 47 47 43 43 39 ... (the top pieces: 43 and 47 are 39's pixels exactly, 45 and 49 41's: they don't change)
and 77 77 77 77 81 81 85 85 81 81 77 ... (79 83 87 likewise): the small ball under the orb heats, black with a white
glint (77, 79), glossy red (81, 83), hot pink-white (85, 87), and cools again. No other enemy (launched ones included)
shows S 81, 83, 85 or 87, so they get frame models: the bottom pieces with the ball heated, the rest the same. None of
these sprites is another sprite's pixels mirrored, turned or in other ramps.

As the sprites and their 4x upscales draw it (columns and rows of the 48 x 56 picture; the grey brick floor round it
is the map's ground, drawn into the sprites: left out): a big glossy black orb (columns 4-39 of rows 3-39, its middle
at column 21.5, row 21.5), a soft white glint on its upper left (columns 11-16 of rows 10-16), small light spots and
grey smudges of reflections on it, a grey rim of reflected light along its lower right and its lower front; at its
sides bronze shoulders (columns 1-5 and 37-41 of rows 23-35, a seam across them at row 28); between them, round the
orb's foot, a bronze band (columns 10-31 of rows 35-39), four light ribs at its middle; from the shoulders' inner ends
two tan claws curving out and down to their points beside a black pit (left: from columns 9-13 of row 29 to column 7
of row 43; the right one its mirror image about column 21.5); in the pit, under the band, the small ball (columns
15-30 of rows 38-50), in a dark cup whose walls catch the light on its right.

Built as such a machine for the game's camera, 20 degrees from straight down from the bottom of the screen, which
shows a point at height z about 0.36 z pixels further up the screen than its place on the ground: every part is laid
out so that the camera sees it where the sprites draw it (at(c, r, z): the picture's pixel (c, r) seen at height z),
the outline from straight above still the sprites'. The orb is an ellipsoid of even triangles (18.2 pixels round, 14.5
high, its middle 3 over the ground; what lies more than a pixel under the ground left off) painted in bands cut along
smooth contours (polish_orb_red.band_split): black glass (0x01, glossy), the glint a soft disc of 0x08 to 0x0f with a
little emission (0.1-0.48) round its white core, the spots, the smudges and the rims in greys (0x03-0x06), laid out
where the camera sees the orb's face as the sprites draw it. The shoulders, the band and the claws are swept along
paths: the shoulders and the band bars of rounded section from below the ground up to their tops (the shoulders thick
bronze brackets along the orb's flanks from its middle height down to the ground, a dark groove across them; the band
across the orb's foot, thinner in its middle over the ball, four ribs across it there), the claws horns tapering to
their points on the ground (tan, ramp 10); the right side's parts are the left's mirrored about column 21.1 (the
sprites draw them a little in from the orb's axis). Their faces are painted along smooth contours of how they meet the
light (from the upper left: the bronze 0x19 over 0x16 and 0x13, the tan 0xa7 over 0xa5 and 0xa3). The small ball is a
sphere in a dark cup, the pit round it a dark plate a little over the ground (both in the orb's glass: 0x01, the cup's
wall 0x03, its right inner wall lit 0x06); the ball's paint is the frame's, bands round its glint: black glass with a
white glint (the orb's whites, 0x08-0x0f, emission 0.1-0.48: 77, 79), red glass glowing in its own reds (ramp 4: 0x43,
0x46, 0x49, 0x4d, emission 0.2-0.5: 81, 83) or hot pink-white (0x48, 0x4b, 0x4e, emission 0.36-0.58: 85, 87). No glow
option: the ball is cold most of the time.

The whole is cut along the sprites' edges (x = 0, y = 0; polish_savara_boss.cut: the pieces keep the whole's shading
across the cuts and each face its own winding), each part's cuts closed in its own inside's colour (the orb's black,
the bronze's dark), each piece moved so that its sprite's centre is its origin and its parts joined. Drawn at their
origins (origin), on the ground layer 4 pixels up: height=-4 on the four sprite lines sets it on the terrain (the orb
and the shoulders reach 1 to 3 pixels below the ground).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the ground (z = 0); the
whole's origin is the corner where the four sprites meet (pixel 24, 28 of the picture): column c's middle is x = c +
0.5 - 24, row r's middle y = 27.5 - r. The pieces' centres: 39 (-12, 14), 41 (12, 14), 77 (-12, -14), 79 (12, -14).

Replaces wave3_u_orb.py (the claw orb is all it builds: delete it; nothing imports it, wave3_u_kit.py stays for
wave3_u_carrier.py and wave3_u_hangar.py).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the whole's and each piece's
silhouette against the orb's own pixels in enemy_S.png, the floor left out), --preview <prefix> (the whole's and each
piece's views), --only <name,...>, --whole <file.glb> (the uncut whole, frame 1, as well), --stats 1.
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_orb_red import band_split, icosphere, smoothstep  # noqa: E402
from polish_savara_boss import cut  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
import polish_deli_boss as db  # noqa: E402

# The pieces: (name, its sprite in each frame, the box it covers in the whole's coordinates (x0, x1, y0, y1)).
PIECES = [("claw_orb_tl", (39, 39, 39), (-24.0, 0.0, 0.0, 28.0)),
          ("claw_orb_tr", (41, 41, 41), (0.0, 24.0, 0.0, 28.0)),
          ("claw_orb_bl", (77, 81, 85), (-24.0, 0.0, -28.0, 0.0)),
          ("claw_orb_br", (79, 83, 87), (0.0, 24.0, -28.0, 0.0))]
SPRITE_AT = {"tl": (0, 0), "tr": (24, 0), "bl": (0, 28), "br": (24, 28)}  # top left corners in the picture

TILT = math.tan(math.radians(20.0))   # how far up the screen the game's camera shows a point, per pixel of height
AX = -2.0                             # the machine's axis (the sprites' column 21.5)


def at(c, r, z):
    """The point at height z that the game's camera shows at the picture's pixel (c, r) (its middle)."""
    return Vector((c + 0.5 - 24.0, 27.5 - r - z * TILT, z))


def view(p):
    """Where the camera shows the point p, in the picture's coordinates (x, y)."""
    return Vector((p.x, p.y + p.z * TILT))


def pix(c, r):
    """The picture's pixel (c, r) (its middle) in the whole's coordinates."""
    return Vector((c + 0.5 - 24.0, 27.5 - r))


# --- The orb ------------------------------------------------------------------------------------------------------
ORB_R = (18.2, 18.2, 14.5)
ORB_Z = 3.0                            # its middle's height (its foot sunk below the ground)
ORB_VIEW = pix(21.5, 21.5)             # where the sprites draw its middle
ORB_C = Vector((AX, ORB_VIEW.y - ORB_Z * TILT * 0.25, ORB_Z))  # a quarter of the camera's shift: the outline from
#                                                                above stays the sprites' too
GLINT = (pix(13.4, 13.2), 1.12, [(0.0, 15.0), (1.9, 15.0), (2.5, 12.6), (3.1, 9.4), (3.8, 6.6), (4.6, 4.6),
                                (5.6, 3.0), (6.6, 0.0)])
# Spots and smudges of reflected light (where the sprites draw them, stretch, shade by distance).
SPOTS = [
    (pix(24.6, 9.2), 1.0, [(0.0, 9.0), (0.6, 9.0), (1.1, 5.0), (1.5, 0.0)]),
    (pix(27.0, 19.3), 1.0, [(0.0, 8.2), (0.5, 8.0), (1.0, 4.0), (1.4, 0.0)]),
    (pix(27.0, 8.6), 1.2, [(0.0, 5.2), (1.2, 4.6), (2.1, 2.4), (2.6, 0.0)]),
    (pix(21.6, 20.6), 1.1, [(0.0, 4.6), (1.4, 4.2), (2.4, 2.0), (3.0, 0.0)]),
    (pix(26.0, 13.0), 1.0, [(0.0, 3.6), (1.0, 3.2), (1.7, 0.0)]),
    (pix(13.8, 8.8), 2.2, [(0.0, 3.6), (1.0, 3.2), (1.6, 0.0)]),
]
# The rims of reflected light: along the lower right edge (angles round the orb's middle as the camera sees it,
# degrees from the right, counter-clockwise; how far out (a fraction of the radius) it starts, its shade) and along
# the lower front over the band.
RIM = (-78.0, -12.0, 0.8, 6.2)
FRONT = (pix(21.5, 31.5).y, 3.2, 4.4)    # its middle (y), half height, shade

# The bands of shade (lowest value, palette index, emission strength): black glass, greys, the glint.
ORB_BANDS = [(-9.0, 0x01, 0.0), (2.5, 0x03, 0.0), (3.9, 0x04, 0.0), (5.4, 0x06, 0.0), (7.2, 0x08, 0.1),
             (9.6, 0x0b, 0.2), (12.0, 0x0d, 0.32), (14.4, 0x0f, 0.48)]

# --- The cradle and the claws ------------------------------------------------------------------------------------
# The camera sees these from above (it is 20 degrees off straight down): they are laid out over the sprites' pixels
# as bars swept along plan paths (the pixel (column, row) as the camera sees it at the bar's top), each section a
# rounded box from below the ground up to its top, reaching in towards the orb and out.
# The left shoulder: (column, row, top, reach in (towards the orb), reach out).
SHOULDER = [(3.6, 22.6, 8.4, 1.6, 0.9), (3.2, 24.4, 9.4, 2.6, 1.6), (3.1, 26.6, 9.8, 3.4, 2.4),
            (3.0, 29.0, 9.2, 3.4, 2.5), (2.8, 31.4, 7.8, 3.0, 2.2), (2.5, 33.4, 6.0, 2.4, 1.7),
            (2.3, 35.0, 3.8, 1.8, 1.2), (2.3, 36.4, 1.4, 1.1, 0.7)]
SHOULDER_GROOVE = 28.3                 # the seam across it (the row)
# The band round the orb's foot: (column, row, top, reach up the screen (towards the orb), reach down the screen).
BAND = [(10.4, 37.0, 6.0, 1.8, 2.2), (13.0, 37.2, 6.6, 2.0, 2.2), (16.0, 37.2, 7.0, 2.0, 2.2),
        (18.6, 36.5, 7.4, 1.8, 1.4), (21.5, 36.2, 7.6, 1.8, 1.2), (24.4, 36.5, 7.4, 1.8, 1.4),
        (27.0, 37.2, 7.0, 2.0, 2.2), (30.0, 37.2, 6.6, 2.0, 2.2), (32.6, 37.0, 6.0, 1.8, 2.2)]
RIBS = [18.8, 20.8, 22.8, 24.8]        # the light ribs across its middle (columns)
# The left claw: (column, row, height, radius) as the camera sees it; its root on the orb's lower front.
CLAW = [(11.8, 29.6, 10.6, 2.4), (10.2, 30.8, 9.8, 2.8), (8.2, 32.8, 8.2, 2.7), (6.6, 35.2, 6.0, 2.3),
        (5.8, 37.8, 4.0, 1.8), (5.8, 40.2, 2.3, 1.3), (6.4, 42.3, 1.0, 0.8), (7.2, 43.8, 0.25, 0.25)]

# --- The small ball, its cup and the pit -------------------------------------------------------------------------
BALL_VIEW = pix(22.0, 44.0)
BALL_R = (7.4, 6.6, 6.4)
BALL_Z = 2.4
BALL_C = Vector((-1.6, BALL_VIEW.y - BALL_Z * TILT, BALL_Z))
CUP = (8.0, 6.9, 2.0)                  # its outer radii and height (round the ball's middle)
# The pit: the dark hole the ball sits in, wide under the band between the claws, narrowing below the ball (pixel
# corners of the picture; the grey floor shows either side of its lower part).
PIT = [(8.0, 38.0), (34.6, 38.0), (35.0, 40.0), (33.0, 42.0), (31.2, 44.0), (30.6, 47.0), (29.2, 50.0), (26.6, 52.4),
       (23.0, 53.4), (19.6, 53.0), (17.2, 50.6), (15.6, 47.6), (15.0, 44.4), (12.6, 42.2), (9.0, 41.2), (8.0, 40.0)]
MIRROR = 42.2                          # the right side's column c is the left side's MIRROR - c (the sprites draw it
#                                        a little in from the mirror image about the orb's axis)

# The ball's paint in each frame: bands of (lowest value, palette index, emission strength, emission's index) by
# distance from its glint (the value: 15 at the glint, falling off).
BALL_FRAMES = {
    0: (pix(20.6, 43.0), [(-9.0, 0x01, 0.0, None), (7.0, 0x08, 0.1, None), (9.6, 0x0b, 0.2, None),
                          (12.0, 0x0d, 0.32, None), (14.0, 0x0f, 0.48, None)],
        [(0.0, 15.0), (0.9, 15.0), (1.4, 12.4), (1.9, 9.8), (2.5, 7.4), (3.1, 0.0)]),
    1: (pix(20.0, 43.0), [(-9.0, 0x43, 0.2, 0x44), (4.0, 0x46, 0.3, 0x47), (8.0, 0x49, 0.4, 0x4a),
                          (12.0, 0x4d, 0.5, 0x4e)],
        [(0.0, 15.0), (1.6, 14.0), (2.6, 11.0), (4.0, 8.2), (5.6, 5.0), (7.2, 2.0), (8.4, 0.0)]),
    2: (pix(21.0, 43.6), [(-9.0, 0x48, 0.36, 0x49), (6.0, 0x4b, 0.45, 0x4b), (10.5, 0x4e, 0.58, 0x4e)],
        [(0.0, 15.0), (4.2, 14.0), (5.6, 10.6), (6.8, 6.4), (7.8, 2.0), (8.6, 0.0)]),
}


def materials(frame):
    def mat(name, index, metallic=0.3, roughness=0.5, glow=0.0, glow_index=None):
        emission = k.level_palette()[glow_index if glow_index is not None else index] if glow > 0 else None
        return k.material(name, palette=index, metallic=metallic, roughness=roughness, emission=emission,
                          emission_strength=glow)
    m = {
        "bronze_lit": mat("co_bronze_lit", 0x19, 0.6, 0.3),
        "bronze": mat("co_bronze", 0x16, 0.6, 0.34),
        "bronze_dark": mat("co_bronze_dark", 0x13, 0.55, 0.4),
        "tan_lit": mat("co_tan_lit", 0xa7, 0.2, 0.5),
        "tan": mat("co_tan", 0xa5, 0.2, 0.52),
        "tan_dark": mat("co_tan_dark", 0xa3, 0.2, 0.55),
    }
    m["orb"] = {}
    for low, index, glow in ORB_BANDS:
        m["orb"][index] = mat("co_orb_%02x" % index, index, 0.35, 0.12, glow)
    # The cup, the pit and the cold ball are the orb's glass (its black, its greys, its glint's whites).
    m["black"] = m["pit"] = m["orb"][0x01]
    m["cup"], m["cup_lit"] = m["orb"][0x03], m["orb"][0x06]
    centre, bands, profile = BALL_FRAMES[frame]
    m["ball"] = [(low, m["orb"][index] if index in m["orb"] and glow == dict((i, g) for _, i, g in ORB_BANDS)[index]
                  else mat("co_ball_%02x" % index, index, 0.3, 0.22, glow, gi))
                 for low, index, glow, gi in bands]
    return m


def radial(profile, r):
    for (r0, v0), (r1, v1) in zip(profile, profile[1:]):
        if r <= r1:
            return v0 + (v1 - v0) * max(0.0, r - r0) / (r1 - r0)
    return profile[-1][1]


# --- Helpers ------------------------------------------------------------------------------------------------------

def sweep(name, centres, frames, mat, cap=True):
    """A body swept along a path: centres (Vector) and at each a section [(u, v), ...] in its own frame (two
    Vectors: across and out)."""
    rings = []
    for c, (across, out, section) in zip(centres, frames):
        rings.append([c + across * u + out * v for u, v in section])
    start = sum(rings[0], Vector()) / len(rings[0])
    end = sum(rings[-1], Vector()) / len(rings[-1])
    return k.loft(name, rings, mat, start_point=start if cap else None, end_point=end if cap else None,
                  cap_start=cap, cap_end=cap)


def bar(name, plan, mat, power=3.0, count=20, bottom=-1.2):
    """A bar swept along a plan path [(x, y, top, reach left, reach right), ...] (left and right of the path's
    direction, in plan): its section a rounded box from bottom up to top."""
    pts = [Vector((x, y, 0.0)) for x, y, *_ in plan]
    centres, frames = [], []
    for i, (x, y, top, left, right) in enumerate(plan):
        t = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        side = Vector((-t.y, t.x, 0.0))      # to the left of the path
        a, b = (left + right) / 2, (top - bottom) / 2
        cu, cv = (left - right) / 2, (top + bottom) / 2
        section = [(cu + a * u, cv + b * v) for u, v in superellipse(1.0, 1.0, power, count)]
        centres.append(Vector((x, y, 0.0)))
        frames.append((side, Vector((0.0, 0.0, 1.0)), section))
    return sweep(name, centres, frames, mat)


def superellipse(a, b, power, count, offset=0.0):
    """Points round a superellipse of half-widths a (u) and b (v)."""
    pts = []
    for i in range(count):
        t = 2 * math.pi * (i + offset) / count
        c, s = math.cos(t), math.sin(t)
        pts.append((a * math.copysign(abs(c) ** (2 / power), c), b * math.copysign(abs(s) ** (2 / power), s)))
    return pts


def chaikin_rows(rows, iterations=2):
    """A path of tuples rounded (Chaikin), every value of a row interpolated with it."""
    return mk.chaikin([tuple(r) for r in rows], iterations, closed=False)


LIGHT = Vector((-0.55, 0.45, 0.7)).normalized()   # the game's sun, from the upper left and above


def light_split(obj, bands, extra=None):
    """Paints a body by how its surface faces the light (bands: [(lowest value, material)], the value the vertex
    normal's dot with LIGHT, plus extra(co) if given), the bands' borders cut along smooth contours."""
    obj.data.update()
    normals = [Vector() for _ in obj.data.vertices]
    for poly in obj.data.polygons:
        for vi in poly.vertices:
            normals[vi] += poly.normal * poly.area
    values = [n.normalized().dot(LIGHT) + (extra(v.co) if extra else 0.0)
              for n, v in zip(normals, obj.data.vertices)]
    band_split(obj, values, bands)
    return obj


def orb_normal(p):
    rel = p - ORB_C
    return Vector((rel.x / ORB_R[0] ** 2, rel.y / ORB_R[1] ** 2, rel.z / ORB_R[2] ** 2)).normalized()


# --- The parts ----------------------------------------------------------------------------------------------------

def orb_value(p):
    """The orb's shade at its surface point p (bands: ORB_BANDS), as the camera sees it there."""
    towards = Vector((0.0, -math.sin(math.radians(20)), math.cos(math.radians(20))))
    n = orb_normal(p)
    facing = n.dot(towards)
    if facing <= 0.0:
        return 0.0
    v = view(p)
    centre, stretch, profile = GLINT
    d = Vector(((v.x - centre.x) / stretch, v.y - centre.y)).length
    value = radial(profile, d)
    for c, s, prof in SPOTS:
        d = Vector(((v.x - c.x) / s, v.y - c.y)).length
        value = max(value, radial(prof, d))
    # The rims: how far out the point is seen (a fraction of the radius) and its angle round the middle.
    rel = v - view(ORB_C)
    rho = math.hypot(rel.x / ORB_R[0], rel.y / ORB_R[1])
    angle = math.degrees(math.atan2(rel.y, rel.x))
    a0, a1, start, shade = RIM
    weight = smoothstep(a0 - 22.0, a0, angle) * (1.0 - smoothstep(a1, a1 + 22.0, angle))
    value = max(value, shade * smoothstep(start, 0.97, rho) * weight)
    fy, half, fshade = FRONT
    value = max(value, fshade * (1.0 - smoothstep(0.0, half, abs(v.y - fy))) *
                (1.0 - smoothstep(9.0, 13.0, abs(v.x - AX))))
    return value * smoothstep(0.0, 0.12, facing)


def orb(m):
    obj = icosphere("orb", tuple(ORB_C), ORB_R, subdivisions=5)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if max(v.co.z for v in f.verts) < -1.2], context="FACES")
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    bm.to_mesh(obj.data)
    bm.free()
    values = [orb_value(v.co) for v in obj.data.vertices]
    band_split(obj, values, [(low, m["orb"][index]) for low, index, _ in ORB_BANDS])
    k.smooth(obj, 80)
    return obj


def shoulder_parts(m, side):
    """A shoulder (side -1 the left, 1 the right): a thick bronze bracket along the orb's flank, from its middle
    height down to the ground, reaching in to the orb; a groove across it."""
    rows = SHOULDER if side < 0 else [(MIRROR - c, r, top, inner, outer) for c, r, top, inner, outer in SHOULDER]
    path = chaikin_rows(rows, 2)
    plan = []
    for c, r, top, inner, outer in path:
        p = at(c, r, top)
        # The path runs down the screen, so its left is +x: towards the orb for the left shoulder, away from it for
        # the right one.
        left, right = (inner, outer) if side < 0 else (outer, inner)
        plan.append((p.x, p.y, top, left, right))
    body = bar(f"shoulder{side}", plan, m["bronze"], power=3.6)

    def groove(co):  # the seam across it, dark
        row = 27.5 - view(co).y
        return -1.6 * (1.0 - smoothstep(0.3, 0.75, abs(row - SHOULDER_GROOVE))) * smoothstep(1.0, 3.0, co.z)
    light_split(body, [(-9.0, m["bronze_dark"]), (0.1, m["bronze"]), (0.62, m["bronze_lit"])], groove)
    k.smooth(body, 50)
    return [body]


def band_parts(m):
    """The band round the orb's foot: a rounded bar across its front, lower over the ball; its ribs."""
    path = chaikin_rows(BAND, 2)
    plan = []
    for c, r, top, up, down in path:
        p = at(c, r, top)
        plan.append((p.x, p.y, top, up, down))   # the path runs to the right: its left is up the screen
    body = bar("band", plan, m["bronze"], power=2.6)
    light_split(body, [(-9.0, m["bronze_dark"]), (0.2, m["bronze"]), (0.72, m["bronze_lit"])])
    k.smooth(body, 55)
    parts = [body]
    for i, col in enumerate(RIBS):
        top = 7.6
        p = at(col, 36.2, top)
        rib = mk.box(f"rib{i}", p.x - 0.45, p.x + 0.45, p.y - 2.2, p.y + 1.0, top - 2.0, top + 0.6, m["bronze_lit"])
        mk.bevel(rib, 0.22, 2, 35)
        mk.shade(rib, 35)
        parts.append(rib)
    return parts


def claw_parts(m, side):
    rows = CLAW if side < 0 else [(MIRROR - c, r, z, rad) for c, r, z, rad in CLAW]
    path = chaikin_rows(rows, 2)
    centres, frames = [], []
    for i, (c, r, z, rad) in enumerate(path):
        p = at(c, r, z)
        q = at(*path[min(i + 1, len(path) - 1)][:3]) - at(*path[max(i - 1, 0)][:3])
        t = q.normalized()
        ref = Vector((0.0, 0.0, 1.0))
        out = (ref - t * ref.dot(t)).normalized()
        across = t.cross(out).normalized()
        rad = max(rad, 0.06)
        section = superellipse(rad * 1.1, rad * 0.9, 2.0, 14)
        centres.append(p)
        frames.append((across, out, section))
    body = sweep(f"claw{side}", centres, frames, m["tan"])
    light_split(body, [(-9.0, m["tan_dark"]), (0.12, m["tan"]), (0.62, m["tan_lit"])])
    k.smooth(body, 60)
    return [body]


def ball_parts(m, frame):
    """The small ball in its cup, and the pit round it."""
    obj = icosphere("ball", tuple(BALL_C), BALL_R, subdivisions=4)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if max(v.co.z for v in f.verts) < -0.6], context="FACES")
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    bm.to_mesh(obj.data)
    bm.free()
    centre, bands, profile = BALL_FRAMES[frame]
    towards = Vector((0.0, -math.sin(math.radians(20)), math.cos(math.radians(20))))

    def value(p):
        rel = p - BALL_C
        n = Vector((rel.x / BALL_R[0] ** 2, rel.y / BALL_R[1] ** 2, rel.z / BALL_R[2] ** 2)).normalized()
        facing = n.dot(towards)
        v = view(p)
        d = (v - centre).length
        base = radial(profile, d)
        # The far side and the rim (where the camera sees the ball edge on) darker.
        return base * smoothstep(-0.15, 0.35, facing) - 2.5 * (1.0 - smoothstep(0.0, 0.45, facing))
    values = [value(v.co) for v in obj.data.vertices]
    band_split(obj, values, m["ball"])
    k.smooth(obj, 80)
    parts = [obj]
    # The cup round it: a short collar, dark, its walls lit on the right.
    rx, ry, h = CUP
    ring_out = [(rx * math.cos(2 * math.pi * i / 48), ry * math.sin(2 * math.pi * i / 48)) for i in range(48)]
    cup = mk.prism("cup", [(BALL_C.x + x, BALL_C.y + y) for x, y in ring_out], -1.0, h, m["cup"])
    hole = mk.prism("cup_hole", [(BALL_C.x + x * 0.86, BALL_C.y + y * 0.86) for x, y in ring_out], -0.2, h + 1.0,
                    m["pit"])
    mk.boolean(cup, hole, "DIFFERENCE")
    mk.cleanup(cup)
    mk.bevel(cup, 0.35, 2, 35)
    mk.shade(cup, 35)

    def pick_cup(c, n):
        if n.z > 0.9 and c.z < 0.0:
            return m["pit"]
        rel = Vector((c.x - BALL_C.x, c.y - BALL_C.y))
        if rel.x > 1.5 and n.z < 0.9 and rel.length < rx * 0.92:   # the inner wall on the right (lit)
            return m["cup_lit"]
        return None
    mk.paint(cup, pick_cup)
    parts.append(cup)
    # The pit: a dark plate a little over the ground, its outline rounded.
    outline = mk.chaikin([(c - 24.0, 28.0 - r) for c, r in PIT], 3, closed=True)
    plate = mk.prism("pit", outline[::-1], -1.0, 0.18, m["pit"])
    mk.bevel(plate, 0.12, 1, 35)
    parts.append(plate)
    return parts


# --- Build ----------------------------------------------------------------------------------------------------------

CAPS = {"orb": "black", "ball": "black", "cup": "pit", "pit": "pit", "band": "bronze_dark", "rib": "bronze_dark",
        "shoulder": "bronze_dark", "claw": "tan_dark"}


def build_whole(frame):
    m = materials(frame)
    parts = [orb(m)]
    for side in (-1, 1):
        parts += shoulder_parts(m, side)
        parts += claw_parts(m, side)
    parts += band_parts(m)
    parts += ball_parts(m, frame)
    for obj in parts:
        mk.apply(obj)
    bpy.context.view_layer.update()
    return parts, m


def cap_of(obj, m):
    for prefix, key in CAPS.items():
        if obj.name.startswith(prefix):
            return m[key]
    return m["black"]


def own_mask(sheet):
    """The orb's own pixels in the 48 x 56 picture (rows of bools): the sprites' bronze, tan and red pixels, the orb's
    disc, and the dark pixels of the pit round its foot (the grey brick floor round it left out)."""
    import numpy as np
    w = 228
    idx = np.fromfile(sheet[:-4] + ".idx", dtype=np.uint8)
    idx = idx[-(len(idx) // w) * w:].reshape(-1, w).astype(int)
    full = np.zeros((56, 48), int)
    for corner, sprite in (("tl", 39), ("tr", 41), ("bl", 77), ("br", 79)):
        c0, r0 = SPRITE_AT[corner]
        x, y = (sprite - 1) % 19 * 12, (sprite - 1) // 19 * 14
        full[r0:r0 + 28, c0:c0 + 24] = idx[y:y + 28, x:x + 24]
    mask = []
    for r in range(56):
        row = []
        for c in range(48):
            v = full[r, c]
            ramp, shade = v >> 4, v & 15
            in_orb = (c - 21.5) ** 2 + (r - 21.5) ** 2 <= 18.2 ** 2
            in_pit = inside((c + 0.5, r + 0.5), PIT)
            row.append(bool(ramp not in (0, 5, 6) or in_orb or in_pit))
        mask.append(row)
    return mask


def inside(p, poly):
    hit = False
    j = len(poly) - 1
    for i in range(len(poly)):
        (ax, ay), (bx, by) = poly[i], poly[j]
        if (ay > p[1]) != (by > p[1]) and p[0] < (bx - ax) * (p[1] - ay) / (by - ay) + ax:
            hit = not hit
        j = i
    return hit


def export_piece(whole, m, name, box, options, mask, label):
    out = mk.outdir(options)
    parts = [p for p in (cut(src, box, cap_of(src, m)) for src in whole) if p is not None]
    db.drop_unused(parts)
    mk.transform(parts, Matrix.Translation((-(box[0] + box[1]) / 2, -(box[2] + box[3]) / 2, 0)))
    bpy.context.view_layer.update()
    triangulate(parts)
    if "stats" in options:
        for obj in sorted(parts, key=lambda o: -mk.triangles([o])):
            print("    %-16s %6d" % (obj.name, mk.triangles([obj])))
    parts = [db.join(parts, name)]
    parts[0].data.name = name
    for src in whole:
        src.hide_render = True
    if mask is not None:
        mk.compare("%s (%s, its own pixels)" % (name, label), mk.coverage(parts, 24, 28), mask)
    bpy.context.scene.view_settings.view_transform = "Standard"
    mk.report(name, parts, os.path.join(out, name + ".glb"))
    if "preview" in options:
        mk.preview(options["preview"] + name, parts)
    for obj in parts:
        data = obj.data
        bpy.data.objects.remove(obj)
        if data.users == 0:
            bpy.data.meshes.remove(data)
    for src in whole:
        src.hide_render = False


def build():
    options = k.args()
    only = options["only"].split(",") if "only" in options else None
    sheet = os.path.join(options["check"], "enemy_S.png") if "check" in options else None
    mask = own_mask(sheet) if sheet else None
    for frame in (0, 1, 2):
        k.reset()
        whole, m = build_whole(frame)
        if frame == 0:
            if "stats" in options:
                for obj in sorted(whole, key=lambda o: -mk.triangles([o])):
                    print("    %-16s %6d" % (obj.name, mk.triangles([obj])))
                print("whole: %d triangles" % mk.triangles(whole))
            if mask is not None:
                mk.compare("whole (S 39 41 above 77 79, the orb's own pixels)", mk.coverage(whole, 48, 56), mask)
            if "preview" in options:
                mk.preview(options["preview"] + "claw_orb_whole", whole, size=(48, 56), scale=8, distance=1.9)
            if "whole" in options:
                triangulate(whole)
                mk.export(whole, options["whole"])
        for name, sprites, box in PIECES:
            corner = name.rsplit("_", 1)[1]
            if frame > 0 and corner in ("tl", "tr"):
                continue
            model = name if frame == 0 else "%s_%d" % (name, sprites[frame])
            if only and model not in only:
                continue
            piece_mask = None
            if mask is not None:
                c0, r0 = SPRITE_AT[corner]
                piece_mask = [row[c0:c0 + 24] for row in mask[r0:r0 + 28]]
            export_piece(whole, m, model, box, options, piece_mask, "S %d" % sprites[frame])


if __name__ == "__main__":
    build()
