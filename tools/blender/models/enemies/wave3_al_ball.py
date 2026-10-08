"""Enemies of wave 3, batch AL (sheet %, written x25 in models.cfg): FRUIT's geodesic ball, modelled as its sprites
look (models.cfg: yaw=0), on the ground. The kit is wave3_al_kit.py, the pixels wave3_al_art.py (BALL); the rest
of the sheet is in wave3_al.py and wave3_al_citadel.py.

FRUIT puts the ball together from four ground enemies (1246-1249): % 191, 193 at (x - 30, y - 29), (x - 6, y - 29)
above 229, 231 at (x - 30, y - 1), (x - 6, y - 1): 48 x 56 pixels, the ball 47 across in the middle.

- fruit_geoball_tl, _tr, _bl, _br (% 191, 193, 229, 231): a big ball of blue glass panels set in a light frame,
  stitched like a football (a truncated icosahedron: twelve pentagons among twenty hexagons), a pentagon on its
  top as the sprites draw it (its flat side up the screen, a seam running down the screen from its lowest
  corner). The panels bulge a little between raised ribs; the ball sits a little sunk into the ground. Built
  whole, cut in four (origin).

usage: Blender -b --factory-startup -P wave3_al_ball.py -- [--only name,name] [--preview <prefix>]
       [--check 1] [--stats 1] [--whole <prefix>]
"""
import itertools
import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Quaternion, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_al_kit as kit  # noqa: E402
from wave3_al_kit import k, sh, w, pal  # noqa: E402

BALL = kit.frame("BALL", 48, (24, 28))
CENTRE = Vector((0.5, 0.5, 4.0))   # the ball's middle (cols 1-47, rows 4-50), sunk a little
RADIUS = 23.6
TILT = 8.6                          # the top pentagon's middle lies this many degrees up the screen from the top
PHI = (1 + 5 ** 0.5) / 2
STRETCH = 1.24                      # the sprites draw the panels larger than a football's: angles from the top
TOP = Vector((0.0, math.sin(math.radians(TILT)), math.cos(math.radians(TILT))))


def warp(d):
    """A direction of the pattern on the ball as drawn: its angle from the top pentagon's middle stretched."""
    d = d.normalized()
    a = TOP.angle(d) if (d - TOP).length > 1e-9 else 0.0
    if a < 1e-6 or a > math.pi - 1e-3:
        return d
    axis = TOP.cross(d).normalized()
    return (Quaternion(axis, min(a * STRETCH, math.pi - 1e-3) - a) @ d).normalized()


def truncated_icosahedron():
    """The ball's pattern on the unit sphere, turned as the sprites draw it: faces [(kind, centre, corners)],
    edges [(a, b)] (unit vectors)."""
    ico = [Vector(p) for s1 in (-1, 1) for s2 in (-1, 1)
           for p in ((0, s1, s2 * PHI), (s1, s2 * PHI, 0), (s2 * PHI, 0, s1))]
    near = {i: [j for j in range(12) if j != i and abs((ico[i] - ico[j]).length - 2.0) < 1e-6] for i in range(12)}
    tris = [t for t in itertools.combinations(range(12), 3)
            if all(abs((ico[a] - ico[b]).length - 2.0) < 1e-6 for a, b in itertools.combinations(t, 2))]
    # Turn icosahedron vertex 0 to the top pentagon's place, a neighbour of it down the screen.
    top = ico[0].normalized()
    target = TOP
    q1 = top.rotation_difference(target)
    nb = (q1 @ ico[near[0][0]]).normalized()
    # About the target axis: bring the neighbour's direction (projected) to -y.
    def flat(vv):
        p = vv - target * vv.dot(target)
        return p.normalized()
    down = flat(Vector((0.0, -1.0, 0.0)))
    cur = flat(nb)
    ang = math.atan2(cur.cross(down).dot(target), cur.dot(down))
    q = Quaternion(target, ang) @ q1
    pts = [q @ p for p in ico]

    def third(a, b, t):
        return pts[a] + (pts[b] - pts[a]) * t
    faces, edges = [], []
    for i in range(12):
        corners = [third(i, j, 1 / 3) for j in near[i]]
        c = sum(corners, Vector()) / 5
        axis = c.normalized()
        ref = (corners[0] - c).normalized()
        corners.sort(key=lambda p: math.atan2(axis.dot(ref.cross(p - c)), ref.dot(p - c)))
        faces.append(("pent", c, corners))
        for a, b in zip(corners, corners[1:] + corners[:1]):
            edges.append((a, b))
    for a, b, c_ in tris:
        corners = [third(a, b, 1 / 3), third(a, b, 2 / 3), third(b, c_, 1 / 3), third(b, c_, 2 / 3),
                   third(c_, a, 1 / 3), third(c_, a, 2 / 3)]
        c = sum(corners, Vector()) / 6
        axis = c.normalized()
        ref = (corners[0] - c).normalized()
        corners.sort(key=lambda p: math.atan2(axis.dot(ref.cross(p - c)), ref.dot(p - c)))
        faces.append(("hex", c, corners))
    for a, b in itertools.combinations(range(12), 2):
        if b in near[a]:
            edges.append((third(a, b, 1 / 3), third(a, b, 2 / 3)))
    scale = 1.0 / faces[0][2][0].length
    faces = [(kind, c * scale, [p * scale for p in cs]) for kind, c, cs in faces]
    edges = [(a * scale, b * scale) for a, b in edges]
    return faces, edges


def panel(name, centre, corners, mat, inset=0.62, rings=5, per_edge=5, dome=0.55, skirt=1.4):
    """A glass panel on the ball: the face's polygon inset from its edges, its points pushed out to the sphere,
    bulging `dome` in its middle and dipping at its edge, a skirt down into the ball under its rim."""
    n = len(corners)
    c = centre
    # Corners moved towards the middle so each edge comes in by `inset` (in pixels on the ball).
    pull = inset / RADIUS / math.cos(math.pi / n)
    inner = [c + (p - c) * (1.0 - pull / (p - c).length) for p in corners]
    outline = []
    for i in range(n):
        a, b = inner[i], inner[(i + 1) % n]
        for m in range(per_edge):
            outline.append(a + (b - a) * (m / per_edge))
    bm = bmesh.new()

    def place(p, s):
        d = warp(p)
        r = RADIUS + dome * (1.0 - s * s) - 0.35 * kit.smoothstep(0.8, 1.0, s)
        return CENTRE + d * r
    middle = bm.verts.new(place(c, 0.0))
    prev = None
    for k_ in range(1, rings + 1):
        s = k_ / rings
        ring = [bm.verts.new(place(c + (p - c) * s, s)) for p in outline]
        if prev is None:
            for i in range(len(ring)):
                bm.faces.new((middle, ring[i], ring[(i + 1) % len(ring)]))
        else:
            for i in range(len(ring)):
                j = (i + 1) % len(ring)
                bm.faces.new((prev[i], ring[i], ring[j], prev[j]))
        prev = ring
    low = [bm.verts.new(CENTRE + (v.co - CENTRE).normalized() * (RADIUS - skirt)) for v in prev]
    for i in range(len(prev)):
        j = (i + 1) % len(prev)
        bm.faces.new((prev[i], low[i], low[j], prev[j]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.data.materials.append(mat)
    k.recalc_normals(obj)
    return k.smooth(obj, 50)


def rib(name, a, b, mat, radius=0.62, steps=6):
    """A raised rib of the frame along an edge of the pattern (an arc over the ball)."""
    pts = []
    for i in range(steps + 1):
        d = warp(a + (b - a) * (i / steps))
        pts.append(CENTRE + d * (RADIUS + 0.05))
    return w.tube(name, pts, radius, mat, 8, smooth_angle=60)


def ball_whole():
    f = BALL
    faces, edges = truncated_icosahedron()
    # The panels' shades: the sprite's blue under each panel's middle (lighter on the top and the right).
    shades = {s_: kit.glossy(f"geoball_glass", 0x30 + s_, roughness=0.12, metallic=0.35) for s_ in (7, 8, 9, 0xa, 0xb)}
    shade_at = f.shade(3, 2)
    frame_mat = pal("geoball_frame", 0x3c, metallic=0.55, roughness=0.25)
    core = pal("geoball_core", 0x33, metallic=0.3, roughness=0.5)
    # The ball under the panels (seen only through the frame's gaps), a little smaller.
    inner = w.sphere("core", tuple(CENTRE), (RADIUS - 1.0, RADIUS - 1.0, RADIUS - 1.0), core, 48, 24)
    kit.clip_below(inner, 0.0)
    count = 0
    for kind, c, corners in faces:
        if max((CENTRE + warp(p) * RADIUS).z for p in corners) < -0.5:
            continue
        top = CENTRE + warp(c) * RADIUS
        s_ = shade_at(top.x, top.y) + (1.4 if kind == "pent" else 0.8)
        mat = shades[min(shades, key=lambda v_: abs(v_ - s_))]
        obj = panel(f"panel{count}", c, corners, mat)
        kit.clip_below(obj, 0.0)
        count += 1
    for i, (a, b) in enumerate(edges):
        if (CENTRE + warp(a) * RADIUS).z < -1.0 and (CENTRE + warp(b) * RADIUS).z < -1.0:
            continue
        kit.clip_below(rib(f"rib{i}", a, b, frame_mat), 0.0)
    # One mesh per material (fewer parts).
    by_mat = {}
    for obj in w.meshes():
        by_mat.setdefault(obj.data.materials[0].name, []).append(obj)
    for name, objs in by_mat.items():
        kit.join(objs, "geoball_" + name.split("@")[0])


kit.pieced("fruit_geoball", ball_whole, (48, 56),
           [kit.piece("fruit_geoball_tl", BALL, 0, 0), kit.piece("fruit_geoball_tr", BALL, 24, 0),
            kit.piece("fruit_geoball_bl", BALL, 0, 28), kit.piece("fruit_geoball_br", BALL, 24, 28)])


if __name__ == "__main__":
    kit.run()
