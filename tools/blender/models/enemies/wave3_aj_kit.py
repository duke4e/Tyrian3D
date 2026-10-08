"""Helpers for the batch AJ models of wave 3 (sheet 9: the lens pods of LAVA RUN, UNDERDELI and EYESPY, the armoured
head of UNDERDELI, LAVA RUN and DREAD-NOT, the eye sphere of LAVA RUN and EYESPY, DREAD-NOT's shoulders and bladed
shell, TIME WAR's blue capsule): the sprites' pixels (wave3_aj_art.py), and the kit of batch AE (wave3_ae_kit:
pixel frames, painting faces by the sprite's pixel under them, reliefs and plates inflated from pixel regions,
limbs along curves, discs, rings; stand-alone models and whole objects cut into their sprites' pieces, the
silhouette check and the build loop), with heightfield parts and grooves (wave3_q_kit), and a few of its own:
pieces that keep only part of their sprite (where the levels' sprites overlap, each region goes to one of them),
smooth blends of height functions, glossy bulbs sunk into a surface.

Coordinates as in tyrkit: 1 unit = 1 game pixel, X right, Y up the screen, Z up (towards the camera);
the origin is the sprite's centre (or the whole object's, for objects the game draws in pieces).
Pixel (column c, row r) of an art with origin (ox, oy) covers x = c - ox .. c + 1 - ox,
y = oy - r - 1 .. oy - r.
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
import tyrkit as k  # noqa: E402,F401
import wave1_d_shapes as sh  # noqa: E402,F401
import wave3_j_kit as w  # noqa: E402,F401
import wave3_n_kit as n  # noqa: E402,F401
import wave3_q_kit as q  # noqa: E402,F401
import wave3_ae_kit as ae  # noqa: E402,F401
import wave3_aj_art as art  # noqa: E402,F401
from wave3_j_kit import (pal, paint_faces, lathe_axis, hoop, catmull, sphere, rounded_box, meshes, bake,  # noqa: E402,F401
                         transform)
from wave3_v_kit import (Frame, Painter, paint_sprite, pixelate, merge_flat, relief, outlines_of,  # noqa: E402,F401
                         mirror_copies, lift, smoothstep)
from wave3_ae_kit import (displace_z, bumps, plate, limb, band_y, pipe, disc, ellipse_ring, superellipse,  # noqa: E402,F401
                          surface_z, delete_faces, join, flatten_under, bisect_mesh, rotate_z)

model = n.model
pieced = n.pieced
run = ae.run
PROTECT = ae.PROTECT
lens = ae.lens
ellipsoid_point = ae.ellipsoid_point
loft_path = ae.loft_path
torus = ae.torus
heightfield = q.heightfield
groove = q.groove
cone = q.cone


def frame(name, width, origin):
    """A Frame of one of wave3_aj_art's pixel arts."""
    return Frame(getattr(art, name), width, origin)


# --- Pieces ------------------------------------------------------------------------------------------

def piece(name, f, c0, r0, keep=None):
    """The 24 x 28 sprite at pixel (c0, r0) of the whole frame f, keeping only the pixel box keep (c0, c1, r0, r1,
    end exclusive; default: all of it): where the levels' sprites overlap, each region is kept by one of them, so
    the pieces meet without doubled faces. Returns (piece name, its box in the whole's coordinates, its sprite's
    centre there, its mask for --check)."""
    kc0, kc1, kr0, kr1 = keep or (c0, c0 + 24, r0, r0 + 28)
    e = 0.01  # faces lying on a piece's edge stay with neither piece
    box = (kc0 - f.ox + e, kc1 - f.ox - e, f.oy - kr1 + e, f.oy - kr0 - e)
    centre = (c0 + 12 - f.ox, f.oy - r0 - 14)

    def mask():
        return [[kc0 <= c < kc1 and kr0 <= r < kr1 and f.get(c, r) is not None for c in range(c0, c0 + 24)]
                for r in range(r0, r0 + 28)]
    return (name, box, centre, mask)


# --- Height functions ----------------------------------------------------------------------------------

def smin(a, b, r=1.0):
    """A smooth minimum (blends two heights over about r)."""
    h = max(r - abs(a - b), 0.0) / r
    return min(a, b) - h * h * r * 0.25


def smax(a, b, r=1.0):
    return -smin(-a, -b, r)


def dome(x, y, cx, cy, rx, ry, h, power=2.0):
    """The height of an elliptic dome (h at its middle, 0 at its rim, negative outside, falling on)."""
    d = (abs(x - cx) / rx) ** power + (abs(y - cy) / ry) ** power
    if d < 1.0:
        return h * (1.0 - d) ** (1.0 / power)
    return -h * (d ** (1.0 / power) - 1.0) * 3.0


def seg_dist(x, y, a, b):
    """The distance from (x, y) to the segment a-b and where along it (0..1) the nearest point lies."""
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    t = max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / max(dx * dx + dy * dy, 1e-9)))
    return math.hypot(x - ax - t * dx, y - ay - t * dy), t


def path_dist(x, y, pts):
    """The distance from (x, y) to a polyline."""
    return min(seg_dist(x, y, a, b)[0] for a, b in zip(pts, pts[1:]))


# --- Parts -----------------------------------------------------------------------------------------------

def bulb(name, centre, radii, mat, surface=None, sink=0.45, segments=32, rings=16, angle=0.0):
    """A glossy bulb (an ellipsoid turned `angle` degrees about Z) sitting on a surface: its centre's height is
    surface(x, y) plus (1 - sink) of its height (surface None: centre as given)."""
    cx, cy, cz = centre
    if surface is not None:
        cz = surface(cx, cy) + radii[2] * (1.0 - 2.0 * sink)
    obj = sphere(name, (0.0, 0.0, 0.0), radii, mat, segments, rings)
    obj.data.transform(Matrix.Translation((cx, cy, cz)) @ Matrix.Rotation(math.radians(angle), 4, "Z"))
    return obj


def ring_on(name, points2d, surface, lift_, radius, mat, segments=10, closed=True):
    """A thin tube following a closed (or open) path over a surface, `lift_` above it."""
    pts = [(x, y, surface(x, y) + lift_) for x, y in points2d]
    if closed:
        pts = pts + [pts[0]]
    return w.tube(name, pts, radius, mat, segments)


def inside(poly, x, y):
    """Whether (x, y) lies inside the polygon [(x, y)] (even-odd)."""
    hit = False
    for i in range(len(poly)):
        (ax, ay), (bx, by) = poly[i], poly[i - 1]
        if (ay > y) != (by > y) and x < ax + (y - ay) * (bx - ax) / (by - ay):
            hit = not hit
    return hit


def merge_bottom(obj, angle=1.0):
    """Merges the flat underside (faces looking straight down, never seen) into few triangles, leaving the painted
    top as it is (merging its flat stretches leaves long slivers that shade badly)."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.normal_update()
    down = {f for f in bm.faces if f.normal.z < -0.999}
    edges = [e for e in bm.edges if e.link_faces and all(f in down for f in e.link_faces)]
    verts = [v for v in bm.verts if v.link_faces and all(f in down for f in v.link_faces)]
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(angle), verts=verts, edges=edges, delimit={"MATERIAL"})
    ngons = [f for f in bm.faces if len(f.verts) > 3]
    if ngons:
        bmesh.ops.triangulate(bm, faces=ngons, quad_method="BEAUTY", ngon_method="BEAUTY")
    bm.to_mesh(obj.data)
    bm.free()
    return obj
