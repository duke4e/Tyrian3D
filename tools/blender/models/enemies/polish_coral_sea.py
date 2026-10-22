"""CORAL's last old models on sheet T (2x2 sprites of 24 x 28 pixels; episode 5, CORAL only): the purple dome and its
wreck, the spiral shell, the small submarine and the starfish it throws. Polished (2026-10-22, round 35); it replaces
wave3_v_sea.py (all of it) and wave3_ap_coral.py (all of it).

- coral_dome_tl, _tr, _bl, _br (T 15, 17 above 53, 55; enemies 1201-1204: 1201 at (x - 24, y - 29), 1202 at (x, y - 29),
  1203 at (x - 24, y - 1), 1204 at (x, y - 1), ground, one link, armour 30 each; t 244-4108, five times): a purple dome
  on the sea floor, 46 x 36 (rows 11-46), a gold band round its foot, one over its middle from its back to its front
  foot (4 pixels wide, widening into a plate at the front, rows 34-46), one curving down its left side from the foot
  (row 31) to the plate (row 37), a round boss on its left lobe (columns 13-16, rows 26-29), a raised window block on
  its right lobe (columns 30-38, rows 25-33). The water round it (ramps 3 and 8) and its shadow are the map's.
  Shot, the four die together: 1201 and 1202 (dlevel -1) become T 91 and 93 and stay; 1203 and 1204 leave wrecks
  (tyrian2.c: slumped and dark).
- coral_dome_tl_damaged, coral_dome_tr_damaged (T 91, 93): the dome's back blown out: the sprites keep the dome's front
  and top (rows 19-27, a jagged broken edge, the dark inside showing over its low places), the water where its back was,
  the middle band standing on as a broken arch (columns 23-24 up to row 15), the foot band's right part (columns 40-45).
- coral_shell_top, coral_shell_base (T 13 above 51; enemies 1199, 1200 at (x, y - 29) and (x, y - 1), ground, one link;
  t 3688-4052, three times): a long tan spiral shell lying on the floor, its point up the screen (column 14, row 5),
  about nine whorls widening to the body whorl (columns 1-21, rows 42-46), its dark mouth at the foot to the right
  (columns 16-21, rows 44-51).
- coral_sub_top, coral_sub_base (T 195 above 233; enemies 1210, 1211 at (x, y - 56) and (x, y - 28), ground 2, one link,
  moving down the screen; t 5130-5180, three times): a blue-grey submarine heading down the screen, 16 pixels wide
  (columns 4-19, rows 3-55), a ducted propeller at its stern (rows 0-2), side fins (rows 27-34, out to the sprites'
  edges), a low hump on its back (rows 26-31), a dark window with a lamp in its bow (rows 43-48).
- coral_starfish (T 127; enemy 1223, sky or ground: what CORAL's small starfish (T 89, enemy 1212) leaves when shot, and
  what event 68 turns them into): a tan five-armed starfish filling its sprite (an arm straight up to row 2, two out to
  the sides (columns 0 and 23, rows 10-13), two down and out (rows 22-23)), knobs along its arms' ridges; its frames
  (129, 131, 245, two cycles each) turn it clockwise 18 degrees each (models.cfg yaw=frames:40:0, as before; T 131 is
  T 127 mirrored: twins3.py). Built as polish_coral_starlet.py's starfish, bigger.
No other enemy, launched ones included, shows these sprites; twins3.py finds T 53 and 55 pixel for pixel on sheet M
(281, 283), which no enemy uses.

Built for the game's camera (20 degrees off straight down, from the bottom of the screen): the dome, the shell and the
submarine are solids in the world (on the floor, z 0), sized so that the camera sees their outlines where the sprites
draw them (the camera sees a point at y + z tan 20); what lies on them (the bands, the boss, the window block, the
submarine's window) is placed where the camera sees it at its sprite's place (on_surface: along the camera's line of
sight onto the surface). Painted in the sprites' palette indices in bands by the light each face gets (the game's sun
from the top left). Cut into their pieces in the picture's plane (polish_coral_manta.cut, after taking the solids to
the camera's frame: y + z tan 20, and back), so each piece holds what its sprite draws; the cuts capped in the
inside's colour (seen when the dome's wreck stands over its slumped lower half). Each piece moved so that its sprite's
middle is its origin, every mesh triangulated (polish_k_pod.triangulate: the same output with and without --check)
and joined (polish_deli_boss.join). Deterministic: no random numbers, no booleans (the jagged break is a fixed sum of
sines).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the sea floor. Each whole's
origin is its picture's middle: the dome's (48 x 56) column c is x = c + 0.5 - 24, row r is y = 27.5 - r, its pieces'
origins (-12, 14), (12, 14), (-12, -14), (12, -14); the shell's and the submarine's (24 x 56) column c is x = c + 0.5 - 12,
the pieces' origins (0, 14) and (0, -14); the starfish's (24 x 28) column c is x = c + 0.5 - 12, row r is y = 13.5 - r.

models.cfg: the model lines stay (coral_dome_tl/_tr/_bl/_br, coral_dome_tl_damaged/_tr_damaged, coral_shell_top/_base,
coral_sub_top/_base: origin; coral_starfish: no origin); the dome's, its wreck's and the shell's sprite lines get
height=-4 (on the sea floor: drawn at their origin, ground pieces otherwise stand 4 pixels over it); the submarine
swims (no height option: 4 pixels over the floor); the starfish's line stays (sprite t 127 coral_starfish
yaw=frames:40:0). No frame lines (none of them animates but the starfish, whose frames are turns).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each whole's and piece's
silhouette as the camera sees it and from straight above against enemy_T.png), --preview <prefix> (each whole: top and
3/4 views), --only <name,...>, --whole <prefix> (the uncut wholes as <prefix><object>.glb).
"""
import math
import os
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_deli_boss import join, drop_unused  # noqa: E402
from polish_coral_manta import cut, split_contour  # noqa: E402
from polish_orb_red import band_split  # noqa: E402
from polish_coral_citadel import shear_to_camera, sheared, light, loft_axis  # noqa: E402

TAN_T = math.tan(math.radians(20.0))
LIGHT = Vector((-0.6, 0.6, 1.0)).normalized()

# --- The dome (world): a superellipsoid cap; its base's middle, radii and power, its height; a shallow valley
# along its middle (the band lies in it). DOME_C and DOME_R make the camera see the sprites' outline (fitted:
# middle (-0.09, -2.25), radii 22.93 x 18.46, power 2.12, as the camera sees it).
DOME_C, DOME_R, DOME_P, DOME_H = (0.0, -2.77), (22.93, 17.93), 2.12, 17.0
VALLEY = (0.05, 4.0)                # its depth (of the height), half width
FOOT = [(0.985, 0.0), (1.04, 0.0), (1.055, 1.0), (1.045, 2.0), (1.0, 2.6)]   # the foot band: radius scale, height
BAND_W, PLATE_W, PLATE_FROM = 2.0, 3.0, -6.5   # the middle band's half width, the plate's (from picture y PLATE_FROM)
BAND_H = 0.55                       # how far the bands stand over the shell
LEFT_BAND = [(-22.6, -3.6), (-19.5, -5.0), (-16.5, -6.0), (-14.5, -7.0), (-11.5, -8.0), (-6.5, -9.0), (-2.6, -9.5)]
LEFT_W = 1.25
BOSS = ((-9.5, 0.0), 2.7, 1.5)      # picture position, radius, height
WINDOW = ((10.5, -1.6), (6.4, 7.0, 2.0), (4.0, 4.6, 0.35))   # picture position, frame size, pane size
DOME_PIECES = [("coral_dome_tl", 15, (-24.0, 0.0, 0.0, 28.0)), ("coral_dome_tr", 17, (0.0, 24.0, 0.0, 28.0)),
               ("coral_dome_bl", 53, (-24.0, 0.0, -28.0, 0.0)), ("coral_dome_br", 55, (0.0, 24.0, -28.0, 0.0))]
WRECK_PIECES = [("coral_dome_tl_damaged", 91, (-24.0, 0.0, 0.0, 28.0)),
                ("coral_dome_tr_damaged", 93, (0.0, 24.0, 0.0, 28.0))]
# The wreck: the shell's thickness; the broken edge where the camera sees it (picture x, y: the damaged sprites'
# topmost shell pixels; the dip at x 8-11 shows the dark inside), a jagged wobble over it; the middle band broken off
# at BAND_BREAK (its angle over the top, 0 the front foot); a dark floor inside up to FLOOR_BACK (world y).
SHELL_T = 1.4
WRECK_BREAK = [(-24.5, -1.5), (-21.0, 1.5), (-20.0, 2.5), (-18.0, 3.5), (-16.0, 4.5), (-15.0, 5.5), (-14.0, 6.5),
               (-13.0, 7.5), (-11.5, 8.5), (-8.5, 8.5), (-7.5, 7.5), (-6.5, 6.5), (-5.5, 5.5), (-4.5, 4.2),
               (-3.5, 5.5), (-2.5, 6.0), (2.5, 6.2), (3.5, 7.4), (4.5, 8.3), (6.5, 8.0), (7.6, 6.4), (8.6, 3.6),
               (10.6, 3.2), (11.8, 6.0), (13.5, 5.5), (15.0, 4.6), (17.0, 3.8), (19.0, 3.0), (21.0, 2.0), (24.5, -1.5)]
BREAK_JAG = 0.55
BAND_BREAK = 118.0
FLOOR_BACK = 6.5

PURPLE = [(-99, 0x54), (4.0, 0x55), (4.8, 0x56), (5.6, 0x57), (6.4, 0x58), (7.2, 0x59), (8.0, 0x5a)]
GOLD = [(-99, 0x15), (4.4, 0x16), (5.4, 0x18), (6.4, 0x1a), (7.4, 0x1c)]
INSIDE = 0x51
PANE = 0x52
FINISH = dict(metallic=0.25, roughness=0.42)
GOLD_FINISH = dict(metallic=0.55, roughness=0.32)

# --- The shell (world): its point and its foot's middle, radius along it, whorls, flattening; its mouth.
SHELL_TIP, SHELL_FOOT = (2.4, 21.6), (-0.5, -21.5)
SHELL_R = (0.45, 10.3, 0.9)        # radius at the point, at the body whorl, the profile's power
SHELL_TURNS, SHELL_SQUASH = 9.0, 0.8
SUTURE = (0.045, 0.5)              # the suture's depth (of the radius), width (radians of the whorl)
MOUTH = ((6.2, -17.2), (3.3, 3.6, 1.8))   # picture position (on the body whorl's upper right), radii, depth
TAN = [(-99, 0xa3), (3.8, 0xa4), (4.6, 0xa5), (5.4, 0xa6), (6.2, 0xa7), (7.0, 0xa8), (7.8, 0xa9), (8.6, 0xaa)]
SHELL_FINISH = dict(metallic=0.1, roughness=0.45)
SHELL_PIECES = [("coral_shell_top", 13, (-12.0, 12.0, 0.0, 28.0)), ("coral_shell_base", 51, (-12.0, 12.0, -28.0, 0.0))]

# --- The submarine (world): its axis' height and its sections' flattening, its half widths along the picture (rows
# of the sprites' outline: y, half width), moved down the screen by AXIS_Z tan 20 (the camera sees its widest line
# that much up the screen).
SUB_AXIS, SUB_SQUASH = 6.8, 0.85
SUB_HW = [(24.5, 3.2), (24.0, 4.0), (23.0, 5.0), (21.5, 6.0), (19.5, 7.0), (16.5, 7.8), (15.5, 8.0), (-15.5, 8.0),
          (-17.0, 7.4), (-20.0, 6.4), (-23.0, 5.2), (-25.0, 4.0), (-26.4, 2.8), (-27.4, 1.4), (-27.9, 0.0)]
DUCT = (25.6, 4.4, 3.3, 2.6)       # the propeller's duct: its middle (picture y), outer and inner radius, length
FIN = [(-8.0, 1.0), (-12.0, 0.2), (-12.0, -3.4), (-10.2, -5.6), (-8.0, -7.2)]   # the left fin (picture), mirrored
HUMP = ((0.0, -1.0), (2.6, 5.0, 1.4))    # the hump on its back: picture position, half sizes, height
SUB_WINDOW = ((0.0, -17.8), (4.3, 2.6)) # picture position, half sizes
LAMP = ((0.0, -18.8), 0.95)
HULL = [(-99, 0x64), (4.2, 0x66), (5.6, 0x68), (7.0, 0x6a), (8.2, 0x6b)]
STEEL = [(-99, 0x05), (4.6, 0x07), (5.8, 0x09), (7.0, 0x0b)]
SUB_FINISH = dict(metallic=0.25, roughness=0.42)
SUB_PIECES = [("coral_sub_top", 195, (-12.0, 12.0, 0.0, 28.0)), ("coral_sub_base", 233, (-12.0, 12.0, -28.0, 0.0))]

# --- The starfish (polish_coral_starlet.py's star, bigger): the disc's middle, radius and height; the arms (direction,
# length from the middle to the tip's outer edge, half width at the root and at the tip, ridge height at the root and
# at the tip); knobs along the ridges.
STAR_C, STAR_DISC = (0.25, 1.0), (5.3, 3.0)
STAR_ARMS = [(91.0, 11.1, 3.7, 1.25, 2.3, 0.8), (175.0, 12.3, 3.2, 1.2, 2.0, 0.7), (5.0, 11.9, 3.2, 1.2, 2.0, 0.7),
             (234.0, 13.3, 3.9, 1.3, 2.2, 0.75), (304.0, 13.1, 3.9, 1.3, 2.2, 0.75)]
STAR_BLEND, STAR_RIDGE, STAR_GRID = 0.5, 0.45, 0.44
STAR_KNOBS, STAR_KNOB, STAR_CENTRE_KNOB = [0.3, 0.55, 0.8], (0.5, 0.3), (0.8, 0.45)
STAR_BANDS = [(-99, 0x14), (3.6, 0x15), (4.6, 0x16), (5.6, 0x17), (6.6, 0x18), (7.6, 0x19), (8.6, 0x1a), (9.6, 0x1b)]
STAR_KNOB_BANDS = [(-99, 0x18), (6.4, 0x19), (7.6, 0x1b), (8.8, 0x1c)]
STAR_FINISH = dict(metallic=0.08, roughness=0.55)


def sstep(e0, e1, x):
    t = np.clip((np.asarray(x, float) - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


# --- The camera's frame --------------------------------------------------------------------------------------------------

def to_picture(objects):
    """Moves every point along the camera's line of sight to the ground (y + z tan 20: where the camera sees it), the
    normals with it (the inverse of shear_to_camera)."""
    for obj in objects:
        mesh = obj.data
        normals = [Vector(cn.vector) for cn in mesh.corner_normals]
        for v in mesh.vertices:
            v.co.y += v.co.z * TAN_T
        out = [Vector((n.x, n.y, n.z - TAN_T * n.y)).normalized() for n in normals]
        mesh.normals_split_custom_set([tuple(n) for n in out])
        mesh.update()


def on_surface(zfun, x, ys, y_lo, y_hi):
    """The world y where the camera sees the surface z = zfun(x, y) at picture y ys (its first crossing up the screen
    from y_lo, its front)."""
    ys_ = np.linspace(y_lo, y_hi, 2001)
    g = ys_ + np.array([zfun(x, y) for y in ys_]) * TAN_T - ys
    i = int(np.argmax(g >= 0.0))
    if g[i] < 0:
        return y_hi
    if i == 0:
        return y_lo
    a, b = ys_[i - 1], ys_[i]
    for _ in range(40):
        mid = 0.5 * (a + b)
        if mid + zfun(x, mid) * TAN_T - ys >= 0:
            b = mid
        else:
            a = mid
    return 0.5 * (a + b)


def surface_frame(zfun, x, y, h=0.02):
    """A point of the surface and its normal."""
    z = zfun(x, y)
    zx = (zfun(x + h, y) - zfun(x - h, y)) / (2 * h)
    zy = (zfun(x, y + h) - zfun(x, y - h)) / (2 * h)
    return Vector((x, y, z)), Vector((-zx, -zy, 1.0)).normalized()


def place_on(obj, point, normal, sink=0.0):
    """Turns a part built at the origin standing on z = 0 up to stand on the surface at point along normal."""
    rot = Vector((0, 0, 1)).rotation_difference(normal).to_matrix().to_4x4()
    obj.data.transform(Matrix.Translation(point - normal * sink) @ rot)


TIE = 0.0137   # added to every light value: flat faces' values would otherwise sit exactly on band borders, and
#               band_split's cuts along them would come out differently from run to run


def vertex_normals(mesh):
    """The mesh's vertex normals, rounded (Blender's carry float noise that differs from run to run: band_split's
    cuts would move with it, and the output would change)."""
    return np.round(np.array([tuple(v.normal) for v in mesh.vertices]), 4)


def paint_light(obj, bands, m, lift=0.0, flat=False):
    """band_split by the light the faces get (their vertices' smooth normals, in the world), then smooth shading."""
    mesh = obj.data
    nn = vertex_normals(mesh)
    lv = light(nn) + TIE + lift
    band_split(obj, lv, [(lo, m[i]) for lo, i in bands])
    k.smooth(obj, 30 if flat else 70)
    return obj


def fan_slab(name, outline, z0, z1, mat):
    """A flat solid over a convex outline from z0 to z1, its top and bottom fans round their middle (tyrkit.slab's
    BEAUTY split of the n-gons breaks ties differently from run to run)."""
    n = len(outline)
    cx = sum(p[0] for p in outline) / n
    cy = sum(p[1] for p in outline) / n
    verts = [(x, y, z0) for x, y in outline] + [(x, y, z1) for x, y in outline] + [(cx, cy, z0), (cx, cy, z1)]
    faces = []
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, j, n + j, n + i))
        faces.append((2 * n, j, i))
        faces.append((2 * n + 1, n + i, n + j))
    obj = k.mesh_object(name, verts, faces, mat)
    k.recalc_normals(obj)
    return obj


def section_loft(name, stations, mat, closed_ends=True):
    """A solid through closed cross-sections (lists of points of equal counts), its ends closed by fans."""
    obj = k.loft(name, stations, mat, cap_start=closed_ends, cap_end=closed_ends)
    k.recalc_normals(obj)
    return obj


# --- The dome --------------------------------------------------------------------------------------------------------------

def dome_q(x, y):
    cx, cy = DOME_C
    rx, ry = DOME_R
    return (abs((x - cx) / rx) ** DOME_P + abs((y - cy) / ry) ** DOME_P) ** (1.0 / DOME_P)


def dome_z(x, y):
    q = dome_q(x, y)
    if q >= 1.0:
        return 0.0
    v = 1.0 - VALLEY[0] * math.exp(-(x / VALLEY[1]) ** 2) * (1.0 - q) ** 0.5
    return DOME_H * math.sqrt(1.0 - q * q) * v


def ring_point(s, phi):
    """The base superellipse scaled by s, at the angle phi."""
    cx, cy = DOME_C
    rx, ry = DOME_R
    c, sn = math.cos(phi), math.sin(phi)
    return (cx + s * rx * math.copysign(abs(c) ** (2 / DOME_P), c),
            cy + s * ry * math.copysign(abs(sn) ** (2 / DOME_P), sn))


def dome_shell(m, segments=128, steps=22):
    """The dome's outer surface (a loft of rings from its foot to its top) closed by a flat floor."""
    rings = []
    for i in range(steps):
        a = (math.pi / 2) * i / steps
        s = math.cos(a)
        ring = []
        for j in range(segments):
            x, y = ring_point(s, 2 * math.pi * j / segments)
            ring.append(Vector((x, y, dome_z(x, y) if i else 0.0)))
        rings.append(ring)
    top = (DOME_C[0], DOME_C[1], dome_z(*DOME_C))
    obj = k.loft("dome_shell", rings, m[0x56], cap_start=True, cap_end=True, start_point=(DOME_C[0], DOME_C[1], 0.0),
                 end_point=top)
    k.smooth(obj, 60)
    return paint_light(obj, PURPLE, m)


def foot_band(m, segments=128, keep=None):
    """The gold band round the dome's foot (keep(phi): the angles it stays at, for the wreck)."""
    sections = []
    for j in range(segments):
        phi = 2 * math.pi * j / segments
        sec = []
        for s, z in FOOT:
            x, y = ring_point(s, phi)
            sec.append(Vector((x, y, z)))
        sections.append(sec)
    verts, faces = [], []
    n = len(FOOT)
    for sec in sections:
        verts += sec
    for j in range(segments):
        if keep and not (keep(2 * math.pi * j / segments) and keep(2 * math.pi * (j + 1) / segments)):
            continue
        j2 = (j + 1) % segments
        for i in range(n):
            i2 = (i + 1) % n
            faces.append((j * n + i, j2 * n + i, j2 * n + i2, j * n + i2))
    obj = k.mesh_object("dome_foot", verts, faces, m[0x18])
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    edges = [e for e in bm.edges if e.is_boundary]
    if edges:
        bmesh.ops.holes_fill(bm, edges=edges, sides=0)
    bm.to_mesh(obj.data)
    bm.free()
    k.recalc_normals(obj)
    k.smooth(obj, 50)
    return paint_light(obj, GOLD, m)


def strip(name, path, half_width, m, zfun, height=BAND_H, across=9, width_of=None):
    """A band lying on the surface along a path of (x, y) points: closed sections (a rounded top standing `height`
    over the surface, its sides and bottom under it)."""
    stations = []
    pts = [Vector((p[0], p[1], 0.0)) for p in path]
    for i, p in enumerate(pts):
        t = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)])
        t.z = 0.0
        t.normalize()
        side = Vector((-t.y, t.x, 0.0))
        w = width_of(i, p) if width_of else half_width
        sec = []
        for kk in range(across):
            u = -1.0 + 2.0 * kk / (across - 1)
            q = p + side * (u * w)
            prof = height * max(0.0, 1.0 - abs(u) ** 6) ** 0.5 - 0.12
            sec.append(Vector((q.x, q.y, zfun(q.x, q.y) + prof)))
        for u in (1.0, -1.0):
            q = p + side * (u * w)
            sec.append(Vector((q.x, q.y, zfun(q.x, q.y) - 0.8)))
        stations.append(sec)
    obj = section_loft(name, stations, m[0x18])
    k.smooth(obj, 50)
    return paint_light(obj, GOLD, m)


def middle_band(m, theta1=180.0):
    """The band over the dome's middle (x 0) from its front foot (angle 0) over its top to theta1 (degrees; 180 its
    back foot), widening into the plate at its front; dense near the feet (the shell is steep there)."""
    cy, ry = DOME_C[1], DOME_R[1]
    plate_y = on_surface(dome_z, 0.0, PLATE_FROM, cy - ry, cy)

    def width_of(i, p):
        return BAND_W + (PLATE_W - BAND_W) * float(sstep(plate_y + 1.5, plate_y - 1.5, p.y))
    thetas = sorted({round(float(t), 4) for t in np.concatenate([np.linspace(0.5, 30.0, 26),
                                                                np.linspace(31.0, 150.0, 60),
                                                                np.linspace(151.0, 179.5, 29)]) if t < theta1}
                    | {round(theta1 if theta1 < 180.0 else 179.5, 4)})
    path = [(0.0, cy - ry * math.cos(math.radians(th))) for th in thetas]
    return strip("dome_band_mid", path, BAND_W, m, dome_z, width_of=width_of)


def left_band(m):
    cy, ry = DOME_C[1], DOME_R[1]
    pts = []
    for x, ys in LEFT_BAND:
        lim = (1.0 - abs(x / DOME_R[0]) ** DOME_P) ** (1 / DOME_P) * ry
        y = on_surface(dome_z, x, ys, cy - lim, cy + lim)
        pts.append((x, y))
    dense = []
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
        count = max(2, int(math.hypot(x1 - x0, y1 - y0) / 0.6))
        for i in range(count):
            dense.append((x0 + (x1 - x0) * i / count, y0 + (y1 - y0) * i / count))
    dense.append(pts[-1])
    return strip("dome_band_left", dense, LEFT_W, m, dome_z)


def boss(m):
    (px, py), r, h = BOSS
    cy, ry = DOME_C[1], DOME_R[1]
    y = on_surface(dome_z, px, py, cy - ry, cy + ry)
    point, normal = surface_frame(dome_z, px, y)
    obj = mk.dome("dome_boss", (0.0, 0.0), (r, r, h + 0.5), -0.5, m[0x58], segments=20, steps=6)
    place_on(obj, point, normal)
    k.smooth(obj, 60)
    return paint_light(obj, PURPLE, m, lift=1.2)


def window(m):
    (px, py), (fw, fh, fz), (pw, ph, pz) = WINDOW
    cy, ry = DOME_C[1], DOME_R[1]
    y = on_surface(dome_z, px, py, cy - ry, cy + ry)
    point, normal = surface_frame(dome_z, px, y)
    frame = mk.box("dome_window", -fw / 2, fw / 2, -fh / 2, fh / 2, -1.2, fz, m[0x57])
    mk.bevel(frame, 0.55, 2, 30)
    triangulate([frame])
    pane = mk.box("dome_window_pane", -pw / 2, pw / 2, -ph / 2, ph / 2, fz - 0.6, fz + pz, m[PANE])
    mk.bevel(pane, 0.3, 2, 30)
    triangulate([pane])
    for obj in (frame, pane):
        place_on(obj, point, normal)
        k.smooth(obj, 35)
    paint_light(frame, PURPLE, m, lift=0.6, flat=True)
    return [frame, pane]


def dome_whole(m):
    parts = [dome_shell(m), foot_band(m), middle_band(m), left_band(m), boss(m)]
    parts += window(m)
    return parts


# --- The dome's wreck --------------------------------------------------------------------------------------------------

def jag(x):
    """A fixed jagged wobble of the broken edge (a sum of sines; no random numbers)."""
    return (math.sin(1.9 * x + 0.4) * 0.5 + math.sin(3.7 * x + 1.9) * 0.3 + math.sin(6.1 * x + 0.7) * 0.25 +
            math.copysign(abs(math.sin(8.3 * x + 2.3)) ** 3, math.sin(8.3 * x + 2.3)) * 0.4)


def break_line(x):
    xs = [p[0] for p in WRECK_BREAK]
    ys = [p[1] for p in WRECK_BREAK]
    return float(np.interp(x, xs, ys)) + BREAK_JAG * jag(x)


def wreck_shell(m, segments=128, steps=22):
    """The dome's shell where the camera still sees it (under the broken edge), SHELL_T thick: its outer surface,
    its inner one (the inside's colour), the broken edge and its foot closed between them; a dark floor inside."""
    bm = bmesh.new()
    rings = []
    for i in range(steps):
        a = (math.pi / 2) * i / steps
        s_ = math.cos(a)
        ring = []
        for j in range(segments):
            x, y = ring_point(s_, 2 * math.pi * j / segments)
            ring.append(bm.verts.new((x, y, dome_z(x, y) if i else 0.0)))
        rings.append(ring)
    apex = bm.verts.new((DOME_C[0], DOME_C[1], dome_z(*DOME_C)))
    for i in range(steps - 1):
        for j in range(segments):
            j2 = (j + 1) % segments
            bm.faces.new((rings[i][j], rings[i][j2], rings[i + 1][j2], rings[i + 1][j]))
    for j in range(segments):
        bm.faces.new((rings[-1][j], rings[-1][(j + 1) % segments], apex))
    vals = {"f": {v: break_line(v.co.x) - (v.co.y + v.co.z * TAN_T) for v in bm.verts}}
    split_contour(bm, vals, "f", 0.0)
    bmesh.ops.delete(bm, geom=[fc for fc in bm.faces if sum(vals["f"][v] for v in fc.verts) / len(fc.verts) < 0],
                     context="FACES")
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    outer = list(bm.faces)
    inner_of = {}
    for v in list(bm.verts):
        _, n = surface_frame(dome_z, v.co.x, v.co.y)
        if v.co.z < 0.05:
            d = Vector((v.co.x - DOME_C[0], v.co.y - DOME_C[1], 0.0)).normalized()
            n = d
        p = v.co - n * SHELL_T
        p.z = max(p.z, -0.6)
        inner_of[v] = bm.verts.new(p)
    inner = [bm.faces.new([inner_of[v] for v in reversed(fc.verts)]) for fc in outer]
    rim = []
    for e in [e for e in bm.edges if e.is_boundary and all(v in inner_of for v in e.verts)]:
        a_, b_ = e.verts
        rim.append(bm.faces.new((b_, a_, inner_of[a_], inner_of[b_])))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    inside = set(inner) | set(rim)
    mesh = bpy.data.meshes.new("dome_wreck")
    for fc in bm.faces:
        fc.material_index = 1 if fc in inside else 0
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("dome_wreck", mesh)
    bpy.context.scene.collection.objects.link(obj)
    mesh.materials.append(m[0x57])
    mesh.materials.append(m[INSIDE])
    k.smooth(obj, 45)
    mesh = obj.data
    nn = vertex_normals(mesh)
    lv = light(nn) + TIE
    is_in = np.zeros(len(mesh.vertices), bool)
    for poly in mesh.polygons:
        if poly.material_index == 1:
            for vi in poly.vertices:
                is_in[vi] = True
    lv = np.where(is_in, -50.0, lv)
    band_split(obj, lv, [(-99.0, m[INSIDE])] + [(lo if lo > -99 else -40.0, mt) for lo, mt in
                                                 [(lo_, m[i]) for lo_, i in PURPLE]])
    k.smooth(obj, 45)
    # the floor inside (its front part: the dome's back is gone)
    pts = []
    for j in range(96):
        x, y = ring_point(0.95, 2 * math.pi * j / 96)
        pts.append((x, min(y, FLOOR_BACK)))
    floor = fan_slab("dome_floor", pts, -0.4, 0.25, m[INSIDE])
    return [obj, floor]


def wreck_whole(m):
    # the foot band: its front half and a short stub up the right (the sprites' columns 40-45)
    keep_foot = lambda phi: math.sin(phi) < -0.05 or (math.cos(phi) > 0.8 and math.sin(phi) < 0.5)  # noqa: E731
    parts = wreck_shell(m) + [foot_band(m, keep=keep_foot), middle_band(m, theta1=BAND_BREAK), left_band(m), boss(m)]
    parts += window(m)
    return parts


# --- The shell ---------------------------------------------------------------------------------------------------------

def shell_radius(t):
    r0, r1, pw = SHELL_R
    r = r0 + (r1 - r0) * t ** pw
    if t > 0.9:
        r *= 0.3 + 0.7 * max(0.0, 1.0 - ((t - 0.9) / 0.1) ** 2) ** 0.5
    return r


def shell_whole(m, rings=112, segments=32):
    """The shell lying on the floor: a cone lofted from its point to its body whorl, its whorls bulging a little
    between the spiral suture, its mouth a dark hollow sunk into the body whorl's foot at the right, a pale rim
    painted round it; painted by the light, the whorls' crests a little lighter, the suture darker."""
    tip = Vector((SHELL_TIP[0], SHELL_TIP[1], 0.0))
    foot = Vector((SHELL_FOOT[0], SHELL_FOOT[1], 0.0))
    axis = foot - tip
    d = axis.normalized()
    side = Vector((-d.y, d.x, 0.0))
    up = Vector((0, 0, 1))

    def whorl(t, a):
        # the suture sweeps a whole turn over the top half (seen) and runs round the underside (never seen), so it
        # slopes down to the right across the shell by a whorl, as the sprites draw it
        a = a % (2 * math.pi)
        g = 2.0 * a if a <= math.pi else 0.0
        phase = (SHELL_TURNS * t * 2 * math.pi + g) % (2 * math.pi)
        return min(phase, 2 * math.pi - phase)
    stations = []
    for i in range(rings + 1):
        t = i / rings
        r = shell_radius(t)
        c = tip + axis * t
        c.z = r * SHELL_SQUASH + 0.25
        ring = []
        for j in range(segments):
            a = 2 * math.pi * j / segments
            dist = whorl(t, a)
            groove = SUTURE[0] * math.exp(-(dist / SUTURE[1]) ** 2)
            bulge = 0.025 * math.cos(dist - math.pi)
            rr = r * (1.0 - groove + bulge)
            ring.append(c + side * (math.cos(a) * rr) + up * (math.sin(a) * rr * SHELL_SQUASH))
        stations.append(ring)
    end = tip + axis + d * 0.4
    end.z = shell_radius(1.0) * SHELL_SQUASH + 0.25
    body = k.loft("shell_body", stations, m[0xa6], start_point=tuple(tip + Vector((0, 0, 0.25)) - d * 0.3),
                  end_point=tuple(end))
    k.smooth(body, 50)
    # the mouth: where the camera sees the sprite's dark mouth (an ellipse in the picture), a hollow pressed into the
    # body whorl's front (its faces dark), a pale rim painted round it
    (px, py), (rx, ry, depth) = MOUTH
    mesh = body.data
    nn0 = [Vector(tuple(n)) for n in vertex_normals(mesh)]
    inside = []
    for v, n in zip(mesh.vertices, nn0):
        qx, qy = (v.co.x - px) / rx, (v.co.y + v.co.z * TAN_T - py) / ry
        q = math.hypot(qx, qy)
        front = n.z > 0.15 or n.y < -0.3
        inside.append(q if front else 9.0)
        if front and q < 1.0:
            v.co -= n * depth * (1.0 - q * q)
    k.smooth(body, 50)
    # painted: the light, the whorls' crests lighter, the suture darker, the body whorl kept light, the mouth dark
    nn = vertex_normals(mesh)
    lv = light(nn) + TIE
    extra = []
    for v, q in zip(mesh.vertices, inside):
        rel = Vector((v.co.x, v.co.y, 0.0)) - tip
        t = max(0.0, min(1.0, rel.dot(d) / axis.length))
        c = tip + axis * t
        c.z = shell_radius(t) * SHELL_SQUASH + 0.25
        off = v.co - c
        a = math.atan2(off.z / SHELL_SQUASH, off.dot(side))
        dist = whorl(t, a)
        e = 1.4 + 0.5 * math.cos(dist - math.pi) * 0.5 - 2.0 * math.exp(-(dist / 0.26) ** 2)
        e += 1.6 * float(sstep(0.8, 0.97, t))
        e += 2.0 * math.exp(-((q - 1.12) / 0.14) ** 2)
        if q < 1.0:
            e = -60.0
        extra.append(e)
    lv = lv + np.array(extra)
    band_split(body, lv, [(-99.0, m[0xb0])] + [(lo if lo > -99 else -40.0, m[i]) for lo, i in TAN])
    k.smooth(body, 50)
    return [body]


def shell_top_z(body):
    """The shell's top surface as a function (for placing the mouth): a ray down onto its mesh."""
    from mathutils.bvhtree import BVHTree
    mesh = body.data
    tree = BVHTree.FromPolygons([v.co.copy() for v in mesh.vertices], [tuple(p.vertices) for p in mesh.polygons])

    def zf(x, y):
        hit = tree.ray_cast(Vector((x, y, 60.0)), Vector((0, 0, -1)))
        return hit[0].z if hit[0] is not None else 0.0
    return zf


# --- The submarine -------------------------------------------------------------------------------------------------------

def sub_profile():
    """The hull's half widths along the world's y (the sprites' moved down the screen by the axis' height)."""
    shift = SUB_AXIS * TAN_T
    return sorted([(y - shift, hw) for y, hw in SUB_HW])


def sub_hw(y):
    prof = sub_profile()
    ys = [p[0] for p in prof]
    hs = [p[1] for p in prof]
    return float(np.interp(y, ys, hs, left=0.0, right=0.0))


def sub_top(x, y):
    hw = sub_hw(y)
    if abs(x) >= hw:
        return 0.0
    return SUB_AXIS + SUB_SQUASH * math.sqrt(hw * hw - x * x)


def sub_whole(m):
    prof = sub_profile()
    pts = []
    for (y0, h0), (y1, h1) in zip(prof[:-1], prof[1:]):
        count = max(1, int((y1 - y0) / 0.6))
        for i in range(count):
            t = i / count
            # smooth the profile's corners (a cosine ease between its points)
            e = 0.5 - 0.5 * math.cos(math.pi * t)
            pts.append((y0 + (y1 - y0) * t, h0 + (h1 - h0) * e))
    pts.append(prof[-1])
    hull = k.lathe("sub_hull", pts, m[0x66], segments=40, axis_z=SUB_AXIS, squash=SUB_SQUASH)
    k.smooth(hull, 50)
    mesh = hull.data
    nn = vertex_normals(mesh)
    lv = light(nn) + TIE + 0.5 + np.array([1.1 * math.exp(-(v.co.x / 1.6) ** 2) * (v.co.z > SUB_AXIS)
                                     for v in mesh.vertices])
    band_split(hull, lv, [(lo, m[i]) for lo, i in HULL])
    k.smooth(hull, 50)
    parts = [hull]
    # the duct at the stern (its open end faces up the screen, away from the camera: a ring round the hull's end)
    # and the propeller's hub showing behind it
    yd, ro, ri, ln = DUCT
    yw = yd - SUB_AXIS * TAN_T
    duct = k.lathe("sub_duct", [(yw - ln / 2 - 0.4, ri), (yw - ln / 2, ro), (yw + ln / 2 - 0.3, ro),
                                (yw + ln / 2, ro - 0.5)], m[0x07], segments=36, axis_z=SUB_AXIS, squash=SUB_SQUASH)
    k.smooth(duct, 50)
    paint_light(duct, STEEL, m)
    hub = k.lathe("sub_hub", [(yw + ln / 2 - 0.2, 1.7), (yw + ln / 2 + 0.6, 1.3), (yw + ln / 2 + 1.2, 0.0)], m[0x07],
                  segments=20, axis_z=SUB_AXIS, squash=1.0)
    k.smooth(hub, 60)
    paint_light(hub, STEEL, m, lift=0.5)
    parts += [duct, hub]
    # the fins: flat swept plates at the axis' height
    shift = SUB_AXIS * TAN_T
    for s in (-1, 1):
        outline = [(s * x, y - shift) for x, y in FIN]
        if s > 0:
            outline = outline[::-1]
        fin = fan_slab("sub_fin%d" % s, outline, SUB_AXIS - 0.55, SUB_AXIS + 0.55, m[0x66])
        mk.bevel(fin, 0.4, 2, 30)
        triangulate([fin])
        k.smooth(fin, 35)
        paint_light(fin, HULL, m, lift=-0.4, flat=True)
        parts.append(fin)
    # the hump on its back
    (hx, hy), (hw_, hl, hh) = HUMP
    y = on_surface(sub_top, hx, hy, -26.0, 22.0)
    point, normal = surface_frame(sub_top, hx, y)
    hump = mk.dome("sub_hump", (0.0, 0.0), (hw_, hl, hh + 0.6), -0.6, m[0x66], segments=24, steps=6, power=2.6)
    place_on(hump, point, Vector((0, 0, 1)))
    k.smooth(hump, 60)
    paint_light(hump, HULL, m, lift=0.6)
    parts.append(hump)
    # the window in the bow: a dark glass lens, the lamp in it
    (wx, wy), (ww, wl) = SUB_WINDOW
    y = on_surface(sub_top, wx, wy, -32.0, 10.0)
    point, normal = surface_frame(sub_top, wx, y)
    glass = mk.ball("sub_window", (0.0, 0.0, 0.0), (ww, wl, 0.9), m["glass"], 28, 10)
    glass.data.transform(Matrix.Scale(1.0, 4))
    # a heart: narrower towards the bow
    for v in glass.data.vertices:
        f = 0.65 + 0.35 * min(1.0, max(0.0, (v.co.y + wl) / (2 * wl)))
        v.co.x *= f
    place_on(glass, point, normal, sink=0.35)
    k.smooth(glass, 60)
    (lx, ly), lr = LAMP
    y = on_surface(sub_top, lx, ly, -32.0, 10.0)
    point, normal = surface_frame(sub_top, lx, y)
    lamp = mk.ball("sub_lamp", (0.0, 0.0, 0.0), (lr, lr, lr * 0.8), m["lamp"], 16, 8)
    place_on(lamp, point, normal, sink=0.15)
    k.smooth(lamp, 60)
    parts += [glass, lamp]
    return parts


# --- The starfish -------------------------------------------------------------------------------------------------------

def arm_dir(arm):
    a = math.radians(arm[0])
    return np.array([math.cos(a), math.sin(a)])


def star_fields(x, y):
    """(inside, top height, knob field) at arrays x, y (polish_coral_starlet.fields with these arms)."""
    px, py = x - STAR_C[0], y - STAR_C[1]
    r = np.hypot(px, py)
    inside = STAR_DISC[0] - r
    rd = np.clip(r / STAR_DISC[0], 0.0, 1.0)
    tops = [STAR_DISC[1] * np.sqrt(np.maximum(0.0, 1.0 - rd ** 2))]
    knob = STAR_CENTRE_KNOB[1] * np.exp(-(r / STAR_CENTRE_KNOB[0]) ** 2)
    for arm in STAR_ARMS:
        d = arm_dir(arm)
        length, w0, w1, h0, h1 = arm[1:]
        along = px * d[0] + py * d[1]
        t = np.clip(along / (length - w1), 0.0, 1.0)
        cx, cy = t * (length - w1) * d[0], t * (length - w1) * d[1]
        q = np.hypot(px - cx, py - cy)
        w = w0 + (w1 - w0) * t
        inside = np.maximum(inside, w - q)
        h = h0 + (h1 - h0) * t ** 0.9
        prof = np.sqrt(np.maximum(0.0, 1.0 - (q / w) ** 2))
        side = np.abs((px - cx) * -d[1] + (py - cy) * d[0]) / w
        tops.append(h * prof + STAR_RIDGE * prof * np.exp(-(side / 0.35) ** 2) * (1.0 - t))
        for f in STAR_KNOBS:
            kx, ky = f * (length - w1) * d[0], f * (length - w1) * d[1]
            rr = STAR_KNOB[0] * (1.15 - 0.45 * f)
            knob = knob + STAR_KNOB[1] * (1.1 - 0.5 * f) * np.exp(-((px - kx) ** 2 + (py - ky) ** 2) / rr ** 2)
    stack = np.stack(tops)
    top = STAR_BLEND * np.log(np.sum(np.exp(stack / STAR_BLEND), axis=0)) - STAR_BLEND * math.log(len(tops))
    top = np.maximum(top, 0.0) * np.clip(inside / 0.35, 0.0, 1.0) ** 0.5
    return inside, top + knob * np.clip(inside / 0.5, 0.0, 1.0), knob


def star_normals(x, y, which, h=0.02):
    gx = (star_fields(x + h, y)[which] - star_fields(x - h, y)[which]) / (2 * h)
    gy = (star_fields(x, y + h)[which] - star_fields(x, y - h)[which]) / (2 * h)
    if which == 0:
        n = np.stack([-gx, -gy, np.zeros_like(gx)], axis=1)
    else:
        n = np.stack([-gx, -gy, np.ones_like(gx)], axis=1)
    return n / np.maximum(np.linalg.norm(n, axis=1)[:, None], 1e-9)


def starfish(m):
    import mathutils.noise as noise
    xs = np.arange(-13.0, 13.0 + 1e-6, STAR_GRID)
    ys = np.arange(-13.0, 14.0 + 1e-6, STAR_GRID)
    X, Y = np.meshgrid(xs, ys)
    inside = star_fields(X.ravel(), Y.ravel())[0].reshape(X.shape)
    bm = bmesh.new()
    verts = {}
    for j in range(len(ys)):
        for i in range(len(xs)):
            if inside[j, i] > -2 * STAR_GRID:
                verts[i, j] = bm.verts.new((float(xs[i]), float(ys[j]), 0.0))
    for j in range(len(ys) - 1):
        for i in range(len(xs) - 1):
            corner = [(i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)]
            if not all(c in verts for c in corner) or max(inside[c[1], c[0]] for c in corner) <= 0:
                continue
            a, b, c, e = (verts[q] for q in corner)
            if (i + j) % 2 == 0:
                bm.faces.new((a, b, c))
                bm.faces.new((a, c, e))
            else:
                bm.faces.new((a, b, e))
                bm.faces.new((b, c, e))
    vals = {"in": {}}
    for v in bm.verts:
        vals["in"][v] = float(star_fields(np.array([v.co.x]), np.array([v.co.y]))[0][0])
    split_contour(bm, vals, "in", 0.0)
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if sum(vals["in"][v] for v in f.verts) / len(f.verts) < 0],
                     context="FACES")
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    verts = list(bm.verts)
    x = np.array([v.co.x for v in verts])
    y = np.array([v.co.y for v in verts])
    _, top, knob = star_fields(x, y)
    nn = star_normals(x, y, 1)
    out = star_normals(x, y, 0)
    rim = {v for v in verts if vals["in"][v] <= 1e-6}
    vals["knob"], vals["shade"], vals["n"] = {}, {}, {}
    for v, z, kv, n, o in zip(verts, top, knob, nn, out):
        n = Vector(n)
        if v in rim:
            v.co.z = 0.0
            n = Vector(o)
        else:
            v.co.z = float(z)
        mottle = 0.55 * noise.noise(Vector((v.co.x / 1.2, v.co.y / 1.2, 3.3)))
        vals["shade"][v] = (5.8 + 3.0 * (n.dot(LIGHT) - LIGHT.z) + 3.4 * (n.z - 0.75) + 1.2 * v.co.z / STAR_DISC[1] +
                            mottle)
        vals["knob"][v] = float(kv)
        vals["n"][v] = n
    for v in rim:
        inner = [w for e in v.link_edges for w in e.verts if w is not v and w not in rim]
        if inner:
            vals["shade"][v] = max(vals["shade"][v], sum(vals["shade"][w] for w in inner) / len(inner) - 1.1)
    faces = split_contour(bm, vals, "knob", 0.12)
    zone = {f: sum(vals["knob"][v] for v in f.verts) / len(f.verts) > 0.12 for f in faces}
    for is_knob, bands in ((False, STAR_BANDS), (True, STAR_KNOB_BANDS)):
        zf = {f for f in zone if zone[f] == is_knob and f.is_valid}
        for lowest, _ in bands[1:]:
            zf = split_contour(bm, vals, "shade", lowest, zf)
        for f in zf:
            zone[f] = is_knob
    slots = []
    for f in bm.faces:
        bands = STAR_KNOB_BANDS if zone.get(f) else STAR_BANDS
        value = sum(vals["shade"][v] for v in f.verts) / len(f.verts)
        key = bands[0][1]
        for lowest, i in bands:
            if value >= lowest:
                key = i
        key = ("star", key)
        if key not in slots:
            slots.append(key)
        f.material_index = slots.index(key)
    normals_of = [vals["n"][v] for v in bm.verts]
    boundary = [e for e in bm.edges if e.is_boundary]
    under = bmesh.ops.holes_fill(bm, edges=boundary, sides=0)["faces"]
    key = ("star", STAR_BANDS[0][1])
    if key not in slots:
        slots.append(key)
    for f in under:
        f.material_index = slots.index(key)
    bm.normal_update()
    mesh = bpy.data.meshes.new("coral_starfish")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("coral_starfish", mesh)
    bpy.context.scene.collection.objects.link(obj)
    for key in slots:
        mesh.materials.append(m[key])
    for p in mesh.polygons:
        p.use_smooth = True
    mesh.normals_split_custom_set_from_vertices([tuple(n) for n in normals_of])
    return obj


# --- Materials ------------------------------------------------------------------------------------------------------------

def materials():
    pal = k.level_palette()
    m = {}
    for _, i in PURPLE:
        m[i] = k.material("coral_dome", palette=i, **FINISH)
    for i in (INSIDE, PANE):
        m[i] = k.material("coral_dome", palette=i, **FINISH)
    m[PANE] = k.material("coral_dome_pane", palette=PANE, metallic=0.3, roughness=0.12)
    for _, i in GOLD:
        m[i] = k.material("coral_gold", palette=i, **GOLD_FINISH)
    for _, i in TAN + [(0, 0xa9)]:
        m[i] = k.material("coral_shell", palette=i, **SHELL_FINISH)
    m[0xb0] = k.material("coral_shell_mouth", palette=0xb0, metallic=0.05, roughness=0.6)
    for _, i in HULL:
        m[i] = k.material("coral_sub", palette=i, **SUB_FINISH)
    for _, i in STEEL:
        m[i] = k.material("coral_sub_steel", palette=i, metallic=0.5, roughness=0.3)
    m["glass"] = k.material("coral_sub_glass", palette=0x60, metallic=0.3, roughness=0.08)
    m["lamp"] = k.material("coral_sub_lamp", palette=0x0e, metallic=0.0, roughness=0.2, emission=pal[0x0e],
                           emission_strength=0.55)
    for _, i in STAR_BANDS + STAR_KNOB_BANDS:
        m[("star", i)] = k.material("coral_starfish", palette=i, **STAR_FINISH)
    return m


# --- Cutting, checks, export ---------------------------------------------------------------------------------------------

def sheet_path(options):
    if "check" not in options:
        return None
    sheets = options["check"]
    return os.path.join(sheets, "enemy_T.png") if os.path.isdir(sheets) else sheets


def own_mask(sheet, sprite, keep=None):
    """The sprite's pixels (rows of bools), only those whose palette index keep() takes (the object's own: the water
    and shadows the sprites paint round it are the map's)."""
    mask = k.sprite_mask(sheet, sprite)
    if keep is None:
        return mask
    w = 228
    idx = np.fromfile(sheet[:-4] + ".idx", dtype=np.uint8)
    idx = idx.reshape(len(idx) // w, w)
    x0, y0 = (sprite - 1) % 19 * 12, (sprite - 1) // 19 * 14
    return [[mask[r][c] and keep(int(idx[y0 + r, x0 + c])) for c in range(24)] for r in range(28)]


def keep_dome(i):
    return i >> 4 in (1, 5) or (i >> 4 == 6 and (i & 15) <= 4)


def keep_wreck(i):
    return i >> 4 not in (3, 8)


def keep_shell(i):
    return i >> 4 in (10, 11) or i in (0x01, 0x10)


KEEP = {"coral_dome": keep_dome, "coral_dome_damaged": keep_wreck, "coral_shell": keep_shell}


def whole_mask(sheet, pieces, size, keep=None):
    w, h = size
    mask = [[False] * w for _ in range(h)]
    for name, sprite, box in pieces:
        c0, r0 = int(box[0] + w / 2), int(h / 2 - box[3])
        for r, row in enumerate(own_mask(sheet, sprite, keep)):
            for c, v in enumerate(row):
                if v:
                    mask[r0 + r][c0 + c] = True
    return mask


def export_pieces(label, parts, pieces, cap, size, options, out, only):
    """The whole (world) checked, taken to the camera's frame, cut there into its pieces, each taken back, moved to
    its sprite's middle, checked and exported."""
    sheet = sheet_path(options)
    triangulate(parts)
    low, high = mk.bounds(parts)
    print("== %s whole: %d triangles, x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f" % (
        label, mk.triangles(parts), low.x, high.x, low.y, high.y, low.z, high.z))
    keep = KEEP.get(label)
    if sheet:
        mask = whole_mask(sheet, pieces, size, keep)
        mk.compare("%s whole, from straight above" % label, mk.coverage(parts, *size), mask)
    if "whole" in options:
        mk.export(parts, options["whole"] + label + ".glb")
    if "preview" in options:
        bpy.context.scene.view_settings.view_transform = "Standard"
        mk.preview(options["preview"] + label, parts, size=size, scale=12, distance=1.6)
    to_picture(parts)
    bpy.context.view_layer.update()   # (the cut's bounds test reads the objects' bound boxes)
    if sheet:
        mk.compare("%s whole, as the camera sees it" % label, mk.coverage(parts, *size), mask)
    for name, sprite, box in pieces:
        if only and name not in only:
            continue
        got = [p for p in (cut(src, box, cap) for src in parts) if p is not None]
        drop_unused(got)
        cx, cy = (box[0] + box[1]) / 2, (box[2] + box[3]) / 2
        mk.transform(got, Matrix.Translation((-cx, -cy, 0)))
        bpy.context.view_layer.update()
        triangulate(got)
        obj = join(got, name)
        obj.data.name = name
        for src in parts:
            src.hide_render = True
        if sheet:
            mk.compare("%s (T %d), as the camera sees it" % (name, sprite), mk.coverage([obj], 24, 28),
                       own_mask(sheet, sprite, keep))
        shear_to_camera([obj])
        if sheet:
            mk.compare("%s (T %d), from straight above" % (name, sprite), mk.coverage([obj], 24, 28),
                       own_mask(sheet, sprite, keep))
        mk.report(name, [obj], os.path.join(out, name + ".glb"))
        bpy.data.objects.remove(obj)
        for src in parts:
            src.hide_render = False
    for obj in parts:
        bpy.data.objects.remove(obj)


def build():
    options = k.args()
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None

    def wanted(names):
        return not only or any(n in only for n in names)
    k.reset()
    m = materials()
    bpy.context.scene.view_settings.view_transform = "Standard"
    if wanted(["coral_starfish"]):
        obj = starfish(m)
        triangulate([obj])
        sheet = sheet_path(options)
        if sheet:
            mk.compare("coral_starfish (T 127)", mk.coverage([obj], 24, 28), k.sprite_mask(sheet, 127))
        mk.report("coral_starfish", [obj], os.path.join(out, "coral_starfish.glb"))
        if "preview" in options:
            mk.preview(options["preview"] + "coral_starfish", [obj])
        bpy.data.objects.remove(obj)
    if wanted([p[0] for p in DOME_PIECES]):
        export_pieces("coral_dome", dome_whole(m), DOME_PIECES, m[INSIDE], (48, 56), options, out, only)
    if wanted([p[0] for p in WRECK_PIECES]):
        export_pieces("coral_dome_damaged", wreck_whole(m), WRECK_PIECES, m[INSIDE], (48, 56), options, out, only)
    if wanted([p[0] for p in SHELL_PIECES]):
        export_pieces("coral_shell", shell_whole(m), SHELL_PIECES, m[0xa4], (24, 56), options, out, only)
    if wanted([p[0] for p in SUB_PIECES]):
        export_pieces("coral_sub", sub_whole(m), SUB_PIECES, m[0x64], (24, 56), options, out, only)


if __name__ == "__main__":
    build()
