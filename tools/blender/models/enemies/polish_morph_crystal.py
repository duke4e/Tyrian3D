"""The molten crystal of GYGES and MISTAKES (sheet G 77, 2x2: 24 x 28 pixels; enemies 186-189 of episode 2, the top
layer), polished (2026-10-22, round 34; it had no model: wave3_r_beasts.py left it to its sprite's volume, which
followed the frames). Its animation turns a pyramid into a ball, the ball into a cube and the cube back into a
pyramid: 77 79 81 83 85 87 89 91 93 115 117 119, one game frame each, run once whenever it fires (animate 2: the
enemy data's shot 116 every 60 ticks), so it shows 77 until its first shot and rests on 119 between shots (119 then
77 when the next one starts). They fly across the screen (excc 3 or -3) on the top layer: GYGES t1 (189), t2010-2160
(186, 187), t2310-2400 (186, 188), t2710-2800 (187, 189), t3701 and t3751 (189); MISTAKES t3201 and t3501 (189). No
other enemy, launched ones included, shows these sprites (catalog.json), so the frames are frame models, and none is
another sprite's pixels mirrored, turned or in other ramps.

WHAT THE SPRITES SHOW (columns and rows; the 4x upscales)

A crystal of molten red glass (ramp 7: dark reds 0x70-0x75 on its faces, its edges glowing orange to yellow,
0x76-0x7e), a black outline round it:
- 77: a three-sided pyramid seen from above its apex: its base a triangle (the top corner at column 12 row 2, the
  lower corners at columns 3 and 21 of row 22), its apex at (12, 17), white-hot (0x7e), its three edges from the apex
  glowing (up to the top corner, down to the lower corners), the left face lit (0x73-0x74), the right face dark
  (0x72), the small front face between the lower edges mixed.
- 79, 81, 83: the pyramid swelling and its edges softening into a ball, a molten spot lighting at its upper left
  (ramp 4's dark reds first, then a pale hot spot, 0xaa-0xad, at columns 8-11 of rows 9-12).
- 85, 87: the ball (columns 2-22, rows 4-24): the hot spot white at its upper left, a bright crescent of light at its
  lower right (columns 13-19, rows 16-21), a dark swirl down its right side (ramp 4).
- 89, 91: the ball squaring into a cube (a hexagon's outline, then a rounded cube), the hot spot fading.
- 93: a cube standing on a corner, seen along it: its top face a rhombus (columns 4-23, rows 1-10), its left and
  right faces down to row 22, the edge down its front (column 13) and the top face's front left edge glowing
  (0x78-0x7d), hottest at the front corner (13, 10).
- 115, 117, 119: the cube turning and narrowing back into the pyramid: its front edge rising through the middle,
  its top closing to a point; 119 the pyramid again, its apex at (12, 17), but fuller than 77: its top corner at
  row 1, its sides bulging out to columns 4-21 from row 14 down, its foot to a point at row 22 (the cube's leftover).

THE MODEL

A frame model per frame (molten_crystal, molten_crystal_79 ... _119), each a solid of the shape that frame shows,
modelled in the picture's plane (x, y as the sprite draws them, z towards the viewer: the sprite is the solid's view
from straight above) and then turned VIEW_TILT about x towards the game's camera (20 degrees off straight down, from
the bottom of the screen), so that the camera sees each solid as the sprite draws it; each frame then moved along the
camera's line of sight until its height's bounds are centred (the game centres top enemies in height: no frame
jumps, the camera sees no move).
- The base shapes are read off the sprites: the pyramid (TETRA: its base's corners fitted to 77's outline, the apex
  where 77 draws it, over the base towards the viewer, so that its front face is the small one), the pyramid at rest
  (TETRA_REST: 119's, its base wider at the shoulders and bulging at its foot, the cube's last frames' leftover; only
  the edges from the apex that 119 draws glow, the others are soft folds), the cube (CUBE: its front corner and the
  three edges from it as 93 draws them, their depths solved so that they are square to each other: a corner up, the
  camera looking almost along its diagonal; the top face's front left edge and the edge down its front glow) and the
  ball (SPHERE, 87's).
- The pure frames (77, 93, 119) are those polyhedra, their faces flat and their edges sharp (each face a grid of
  GRID_STEP triangles, for the glow's contours). The frames between are blends of two shapes (MORPHS): along each
  direction from the blended middle the weighted mean of the shapes' distances, the polyhedra's edges rounded by a
  p-norm of their faces (the larger p, the sharper), the molten ball a little lumpy (LUMPS), each blend scaled and
  moved to its sprite's outline; on an icosphere of even triangles (built here by halving edges: the same every run),
  smooth.
- Painted by heat in HEAT bands of ramp 7, cut along smooth contours (band_split), every band glowing a little in its
  own colour (0.16 for the darkest to 0.6 for the white-hot: the game's slanted camera shows dark reds brown and the
  ball's shaded side black otherwise): the faces dark red, the hot edges glowing (EDGE_W wide; white-hot at the hot
  corner, CORE, through yellow and orange to red EDGE_FAR along them), the other edges barely (OTHER_EDGES); on the
  ball the hot spot at its upper left (HOT_SPOT) and the crescent of light inside its lower right rim (CRESCENT);
  the blends take each shape's heat by its weight, the rounded edges' glow smoothed over the triangles (HEAT_SMOOTH)
  and brought back to its peak. Glossy (roughness 0.22), a little metallic sheen.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; origin at the
sprite's centre (pixel 12, 14): column c is x = c + 0.5 - 12, row r is y = 13.5 - r (before the turn).

models.cfg: model molten_crystal enemies/molten_crystal.glb and molten_crystal_79 ... _119 (centred in height, no
origin); sprite g 77 molten_crystal yaw=0 glow=18:0.3:120; frame g 79 molten_crystal_79, ... frame g 119
molten_crystal_119. Replaces nothing that builds a model: wave3_r_beasts.py's docstring paragraph on G 77 and
wave3_r_art.py's MORPH_PYRAMID, MORPH_SPHERE and MORPH_CUBE (pixels nothing reads) go; polish_violet_shell.py (round
34) deletes wave3_r_beasts.py, wave3_r_kit.py and wave3_r_art.py whole, these with them.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each frame's outline as the
camera sees it against its sprite in enemy_G.png), --preview <prefix>, --only <model,...>.
"""
import math
import os
import sys

import bpy
import numpy as np
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402

VIEW_TILT = 20.0
FRAMES = [77, 79, 81, 83, 85, 87, 89, 91, 93, 115, 117, 119]


def model_name(sprite):
    return "molten_crystal" if sprite == 77 else "molten_crystal_%d" % sprite


# --- The base shapes, in the picture's plane -----------------------------------------------------------------------

def P(c, r, z):
    """The point the sprite draws at pixel corner (c, r), at depth z towards the viewer."""
    return np.array([c - 12.0, 14.0 - r, z])


# The pyramids: their apex (white-hot, over the base towards the viewer, where 77 and 119 draw it), then their base's
# corners round from the top one (fitted to the sprites' outlines: 77's a triangle, 119's wider at its shoulders and
# bulging at its foot, as the cube's last frames leave it); the edges from the apex to the corners listed as hot glow.
TETRA = ([P(12.5, 17.5, 7.5)], [P(12.5, 1.2, -6.0), P(2.1, 21.85, -6.0), P(22.9, 21.85, -6.0)], (1, 2, 3))
TETRA_REST = ([P(12.6, 17.4, 8.0)],
              [P(12.6, 0.9, -6.5), P(8.0, 6.5, -6.5), P(4.0, 14.5, -6.5), P(3.42, 21.25, -6.5), P(13.8, 22.9, -6.5),
               P(22.5, 21.3, -6.5), P(21.4, 15.65, -6.5), P(17.75, 7.0, -6.5)],
              (1, 4, 6))
# The cube: its front corner (13, 10) and the edges from it to the top face's left and right corners and down its
# front: where 93 draws them, their depths solved so that the three are square to each other; the first and the
# third glow (the top face's front left edge and the edge down the front).
CUBE_CORNER = P(13.65, 9.95, 0.0)
CUBE_EDGES = [(-9.57, 4.37), (10.19, 4.37), (0.0, -12.9)]
SPHERE = (P(12.5, 14.55, 0.0), 10.6)      # the ball's middle and radius (with its outline)


def cube_edges():
    """The cube's three edges from its front corner, their depths solved for right angles: z_i z_j = -(e_i . e_j)."""
    (ax, ay), (bx, by), (cx, cy) = CUBE_EDGES
    ab, ac, bc = ax * bx + ay * by, ax * cx + ay * cy, bx * cx + by * cy
    za = -math.sqrt(abs(ab * ac / bc))   # negative: the corner is the cube's highest point
    zb, zc = -ab / za, -ac / za
    return [np.array([ax, ay, za]), np.array([bx, by, zb]), np.array([cx, cy, zc])]


class Poly:
    """A convex polyhedron: its vertices, faces (counter-clockwise from outside), planes (unit normal, offset), edges
    and its hot corner (the vertex whose edges glow)."""

    def __init__(self, verts, faces, hot, hot_edges, folds=()):
        self.verts = [np.asarray(v, float) for v in verts]
        self.faces = faces
        self.hot = hot
        self.hot_edges = {tuple(sorted(e)) for e in hot_edges}
        self.folds = {tuple(sorted(e)) for e in folds}
        self.centre = sum(self.verts) / len(self.verts)
        self.planes = []
        for f in faces:
            a, b, c = (self.verts[i] for i in f[:3])
            n = np.cross(b - a, c - a)
            n /= np.linalg.norm(n)
            if np.dot(n, a - self.centre) < 0:
                n = -n
            self.planes.append((n, float(np.dot(n, a - self.centre))))
        edges = set()
        for f in faces:
            for i in range(len(f)):
                edges.add(tuple(sorted((f[i], f[(i + 1) % len(f)]))))
        self.edges = sorted(edges)

    def radius(self, u, p=None):
        """The distance from the middle to the surface along unit directions u (n, 3): the polyhedron's (p None) or
        its edges rounded by the p-norm of the faces' supports."""
        s = np.stack([np.clip(u @ n / d, 0.0, None) for n, d in self.planes], -1)
        if p is None:
            return 1.0 / s.max(-1)
        m = s.max(-1, keepdims=True)
        return 1.0 / (m[..., 0] * (((s / m) ** p).sum(-1)) ** (1.0 / p))

    def heat(self, pts, width):
        """Heat at surface points (relative to nothing: absolute picture coordinates): the edges from the hot corner
        glowing, hottest at it; the other edges warm."""
        out = np.zeros(len(pts))
        hot = self.verts[self.hot]
        d_hot = np.linalg.norm(pts - hot, axis=-1)
        for a, b in self.edges:
            if (a, b) in self.folds:
                continue
            pa, pb = self.verts[a], self.verts[b]
            ab = pb - pa
            t = np.clip(((pts - pa) @ ab) / (ab @ ab), 0.0, 1.0)
            d = np.linalg.norm(pts - (pa + t[:, None] * ab), axis=-1)
            near = smoothstep(width, 0.0, d)
            if (a, b) in self.hot_edges:
                out = np.maximum(out, near * (0.62 + 0.38 * smoothstep(EDGE_FAR, 0.0, d_hot)))
            else:
                out = np.maximum(out, OTHER_EDGES * near)
        return np.maximum(out, smoothstep(CORE[0], CORE[1], d_hot))


def pyramid(spec):
    """A pyramid: its apex (vertex 0) over a convex base (counter-clockwise from above: the corners listed round
    from the top one, which runs clockwise on the screen, are reversed), the apex's edges to the listed corners hot,
    its other apex edges folds (no glow)."""
    (apex,), base, hot = spec
    n = len(base)
    verts = [apex] + list(base)
    faces = [(0, 1 + (i + 1) % n, 1 + i) for i in range(n)] + [tuple(range(1, n + 1))]
    folds = [(0, 1 + i) for i in range(n) if 1 + i not in hot]
    return Poly(verts, faces, 0, [(0, h) for h in hot], folds)


def cube():
    e1, e2, e3 = cube_edges()
    f = CUBE_CORNER
    v = [f, f + e1, f + e2, f + e3, f + e1 + e2, f + e1 + e3, f + e2 + e3, f + e1 + e2 + e3]
    # the faces round the front corner (0) and their opposites
    faces = [(0, 1, 4, 2), (0, 3, 5, 1), (0, 2, 6, 3), (7, 5, 3, 6), (7, 6, 2, 4), (7, 4, 1, 5)]
    return Poly(v, faces, 0, [(0, 1), (0, 3)])


# --- The frames ----------------------------------------------------------------------------------------------------
# Each frame: a polyhedron as it is ("tetra", "rest", "cube"), or a blend [(shape, weight, rounding p or None)] of
# shapes ("sphere" too), scaled about its middle and moved (scale, dx, dy) to fit its sprite's outline (the blends'
# mean distances fall inside the shapes where they differ most).
MORPHS = {
    77: "tetra",
    79: ([("tetra", 0.93, 11.0), ("sphere", 0.07, None)], 1.16, 0.0, -0.25),
    81: ([("tetra", 0.66, 5.0), ("sphere", 0.34, None)], 1.2, 0.0, 0.0),
    83: ([("tetra", 0.36, 3.2), ("sphere", 0.64, None)], 1.12, 0.0, 0.25),
    85: ([("tetra", 0.12, 3.0), ("sphere", 0.88, None)], 1.06, 0.0, 0.25),
    87: ([("sphere", 1.0, None)], 1.0, 0.0, 0.0),
    89: ([("sphere", 0.62, None), ("cube", 0.38, 4.0)], 1.06, 0.0, 0.0),
    91: ([("sphere", 0.2, None), ("cube", 0.8, 7.5)], 1.1, -0.5, -0.25),
    93: "cube",
    115: ([("cube", 0.74, 12.0), ("rest", 0.26, 10.0)], 1.1, 0.0, 0.5),
    117: ([("cube", 0.36, 8.0), ("rest", 0.64, 10.0)], 1.1, 0.0, 0.25),
    119: "rest",
}
LUMPS = {85: 0.35, 83: 0.15, 87: 0.1}     # the molten ball's lumps (pixels)

EDGE_W = 1.25                # the glow's half-width along a sharp edge (wider as the edges round off)
EDGE_FAR = 9.0               # how far along the hot edges they cool to orange-red
OTHER_EDGES = 0.34           # the other edges' heat
CORE = (2.2, 0.0)            # the hot corner: white-hot within this far
HOT_SPOT = (np.array([-0.24, 0.42, 0.87]), (0.82, 0.985))   # the ball's hot spot: direction, and n.d where it glows
CRESCENT = (np.array([0.72, -0.69, 0.0]), (0.4, 0.78), (0.16, 0.38, 0.62), 0.82)  # the light inside its lower
#                            right rim: towards there in the picture, how far in from the rim (n.z), how bright
HEAT_SMOOTH = 2              # passes of averaging the edges' heat over the blends' neighbouring vertices
GRID_STEP = 0.55             # the polyhedra's faces: grid triangles this big
ICO_SUBDIVISIONS = 4

# Heat bands: (palette index, lowest heat, emission strength).
HEAT = [(0x72, -99.0, 0.16), (0x74, 0.2, 0.22), (0x76, 0.36, 0.3), (0x78, 0.5, 0.38), (0x7a, 0.63, 0.46),
        (0x7c, 0.76, 0.53), (0x7e, 0.89, 0.6)]
FINISH = dict(metallic=0.25, roughness=0.22)


def smoothstep(e0, e1, x):
    t = np.clip((np.asarray(x, float) - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def shapes():
    return {"tetra": pyramid(TETRA), "rest": pyramid(TETRA_REST), "cube": cube()}


def icosphere(subdivisions):
    """Unit directions of an icosphere and its triangles (built by halving edges: the same every run)."""
    t = (1.0 + math.sqrt(5.0)) / 2.0
    verts = [(-1, t, 0), (1, t, 0), (-1, -t, 0), (1, -t, 0), (0, -1, t), (0, 1, t), (0, -1, -t), (0, 1, -t),
             (t, 0, -1), (t, 0, 1), (-t, 0, -1), (-t, 0, 1)]
    verts = [np.array(v, float) / np.linalg.norm(v) for v in verts]
    faces = [(0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11), (1, 5, 9), (5, 11, 4), (11, 10, 2), (10, 7, 6),
             (7, 1, 8), (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9), (4, 9, 5), (2, 4, 11), (6, 2, 10),
             (8, 6, 7), (9, 8, 1)]
    for _ in range(subdivisions):
        cache = {}

        def mid(a, b):
            key = (min(a, b), max(a, b))
            if key not in cache:
                m = verts[a] + verts[b]
                verts.append(m / np.linalg.norm(m))
                cache[key] = len(verts) - 1
            return cache[key]
        new = []
        for a, b, c in faces:
            ab, bc, ca = mid(a, b), mid(b, c), mid(c, a)
            new += [(a, ab, ca), (b, bc, ab), (c, ca, bc), (ab, bc, ca)]
        faces = new
    return np.array(verts), np.array(faces, int)


def vertex_normals(pts, tris):
    n = np.zeros_like(pts)
    fn = np.cross(pts[tris[:, 1]] - pts[tris[:, 0]], pts[tris[:, 2]] - pts[tris[:, 0]])
    for i in range(3):
        np.add.at(n, tris[:, i], fn)
    return n / np.linalg.norm(n, axis=-1, keepdims=True)


def blended(frame, polys):
    """A blended frame: points, triangles, normals and heat on the icosphere."""
    u, tris = icosphere(ICO_SUBDIVISIONS)
    parts, scale, dx, dy = MORPHS[frame]
    centre = sum(w * (polys[s].centre if s != "sphere" else SPHERE[0]) for s, w, _ in parts)
    r = np.zeros(len(u))
    heat = np.zeros(len(u))
    for s, w, p in parts:
        if s == "sphere":
            r += w * SPHERE[1]
        else:
            r += w * polys[s].radius(u, p)
    if frame in LUMPS:  # the molten ball's lumps: low smooth bumps
        a = LUMPS[frame]
        r += a * (np.sin(3.1 * u[:, 0] + 1.3) * np.sin(2.7 * u[:, 1] + 0.4) + 0.6 * np.sin(4.3 * u[:, 2] + 2.2) *
                  np.cos(3.7 * u[:, 0] - 0.8))
    pts = centre + scale * r[:, None] * u + np.array([dx, dy, 0.0])
    normals = vertex_normals(pts, tris)
    edges = np.zeros(len(u))
    for s, w, p in parts:
        if s == "sphere":
            d, (lo, hi) = HOT_SPOT
            facing = normals @ (d / np.linalg.norm(d))
            spot = smoothstep(lo, hi, facing)
            dc, (a0, a1), (r0, r1, r2), strength = CRESCENT
            side = normals @ (dc / np.linalg.norm(dc))
            nz = normals[:, 2]
            crescent = strength * smoothstep(a0, a1, side) * smoothstep(r0, r1, nz) * smoothstep(r2, r1, nz)
            heat = np.maximum(heat, w * np.maximum(spot, crescent))
        else:
            poly = polys[s]
            surf = poly.centre + poly.radius(u)[:, None] * u   # the polyhedron's own surface along u
            width = EDGE_W + 5.0 / p
            edges = np.maximum(edges, min(1.0, 0.25 + w) * poly.heat(surf, width) * smoothstep(0.0, 0.5, w))
    # The edges' glow smoothed over neighbouring vertices (along rounded edges it is narrower than the triangles),
    # its peaks brought back up.
    peak = edges.max()
    for _ in range(HEAT_SMOOTH):
        acc, count = edges.copy(), np.ones(len(edges))
        for a, b in ((0, 1), (1, 2), (2, 0)):
            np.add.at(acc, tris[:, a], edges[tris[:, b]])
            np.add.at(count, tris[:, a], 1.0)
        edges = acc / count
    if edges.max() > 0:
        edges = np.clip(edges * (peak / edges.max()), 0.0, 1.0)
    return pts, tris, normals, np.maximum(heat, edges)


def faceted(poly):
    """A polyhedron's faces as fine grids (flat normals, sharp edges), and their heat."""
    pts, tris, normals = [], [], []
    for f, (n, _) in zip(poly.faces, poly.planes):
        corners = [poly.verts[i] for i in f]
        pieces = [corners] if len(corners) <= 4 else [[corners[0], corners[i], corners[i + 1]]
                                                      for i in range(1, len(corners) - 1)]
        for piece in pieces:
            grid_face(piece, n, pts, tris, normals)
    pts, tris, normals = np.array(pts), np.array(tris, int), np.array(normals)
    # every triangle counter-clockwise from outside
    fn = np.cross(pts[tris[:, 1]] - pts[tris[:, 0]], pts[tris[:, 2]] - pts[tris[:, 0]])
    flip = (fn * normals[tris[:, 0]]).sum(-1) < 0
    tris[flip] = tris[flip][:, ::-1]
    return pts, tris, normals, poly.heat(pts, EDGE_W)


def grid_face(corners, n, pts, tris, normals):
    """A triangle or a quadrilateral as a grid of small triangles (appended to the lists); faces looking away from
    the viewer whole."""
    if len(corners) == 3:
        a, b, c = corners
        area = 0.5 * np.linalg.norm(np.cross(b - a, c - a))
        steps = 1 if n[2] < -0.05 else max(2, int(math.ceil(math.sqrt(2.0 * area) / GRID_STEP)))
        index = {}
        for i in range(steps + 1):
            for j in range(steps + 1 - i):
                index[(i, j)] = len(pts)
                pts.append(a + (b - a) * i / steps + (c - a) * j / steps)
                normals.append(n)
        for i in range(steps):
            for j in range(steps - i):
                tris.append((index[(i, j)], index[(i + 1, j)], index[(i, j + 1)]))
                if i + j < steps - 1:
                    tris.append((index[(i + 1, j)], index[(i + 1, j + 1)], index[(i, j + 1)]))
    else:
        a, b, c, d = corners
        area = np.linalg.norm(np.cross(b - a, d - a))
        steps = 1 if n[2] < -0.05 else max(2, int(math.ceil(math.sqrt(area) / GRID_STEP)))
        index = {}
        for i in range(steps + 1):
            for j in range(steps + 1):
                s, t = i / steps, j / steps
                index[(i, j)] = len(pts)
                pts.append(a * (1 - s) * (1 - t) + b * s * (1 - t) + c * s * t + d * (1 - s) * t)
                normals.append(n)
        for i in range(steps):
            for j in range(steps):
                tris += [(index[(i, j)], index[(i + 1, j)], index[(i + 1, j + 1)]),
                         (index[(i, j)], index[(i + 1, j + 1)], index[(i, j + 1)])]


# --- Painting ------------------------------------------------------------------------------------------------------

def band_split(pts, normals, heat, tris):
    """Cuts the triangles along the heat bands' contours (each edge once), the normals carried along; returns points,
    normals, triangles and each triangle's band."""
    co, no, val = [tuple(p) for p in pts.tolist()], [tuple(n) for n in normals.tolist()], list(heat.tolist())
    cuts = {}

    def cut(a, b, t):
        key = (min(a, b), max(a, b), t)
        if key not in cuts:
            f = (t - val[a]) / (val[b] - val[a])
            co.append(tuple(co[a][i] + (co[b][i] - co[a][i]) * f for i in range(3)))
            n = [no[a][i] + (no[b][i] - no[a][i]) * f for i in range(3)]
            length = math.sqrt(sum(c * c for c in n)) or 1.0
            no.append(tuple(c / length for c in n))
            val.append(t)
            cuts[key] = len(co) - 1
        return cuts[key]

    def clip(poly, t, above):
        out = []
        for i in range(len(poly)):
            a, b = poly[i], poly[(i + 1) % len(poly)]
            ina, inb = (val[a] >= t) == above, (val[b] >= t) == above
            if ina:
                out.append(a)
            if ina != inb:
                out.append(cut(a, b, t))
        return out

    out_tris, out_band = [], []
    for tri in tris.tolist():
        rest = tri
        for b in range(len(HEAT) - 1, -1, -1):
            if len(rest) < 3:
                break
            if b == 0:
                piece, rest = rest, []
            else:
                t = HEAT[b][1]
                vals = [val[i] for i in rest]
                if min(vals) >= t:
                    piece, rest = rest, []
                elif max(vals) < t:
                    continue
                else:
                    piece, rest = clip(rest, t, True), clip(rest, t, False)
            for i in range(1, len(piece) - 1):
                out_tris.append((piece[0], piece[i], piece[i + 1]))
                out_band.append(b)
    return np.array(co), np.array(no), np.array(out_tris, int), out_band


def materials():
    pal = k.level_palette()
    return [k.material("crystal", palette=index, emission=pal[index], emission_strength=glow, **FINISH)
            for index, _, glow in HEAT]


def frame_object(frame, polys, mats):
    """One frame's solid, painted, in the picture's plane."""
    shape = MORPHS[frame]
    if isinstance(shape, str):
        pts, tris, normals, heat = faceted(polys[shape])
    else:
        pts, tris, normals, heat = blended(frame, polys)
    co, no, tris, bands = band_split(pts, normals, heat, tris)
    used = sorted(set(bands))
    slot = {b: i for i, b in enumerate(used)}
    name = model_name(frame)
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata([tuple(v) for v in co.tolist()], [], [tuple(t) for t in tris.tolist()])
    for b in used:
        mesh.materials.append(mats[b])
    mesh.polygons.foreach_set("material_index", np.array([slot[b] for b in bands], np.int32))
    mesh.polygons.foreach_set("use_smooth", np.ones(len(tris), bool))
    mesh.update()
    mesh.normals_split_custom_set([tuple(n) for n in no[tris.ravel()].tolist()])
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def to_camera(obj):
    """Turned VIEW_TILT about x towards the camera, then moved along its line of sight until its height is centred."""
    turn = Matrix.Rotation(math.radians(VIEW_TILT), 4, "X")
    normals = [turn.to_3x3() @ Vector(c.vector) for c in obj.data.corner_normals]
    obj.data.transform(turn)
    obj.data.normals_split_custom_set([tuple(n) for n in normals])
    obj.data.update()
    zs = [v.co.z for v in obj.data.vertices]
    zc = (min(zs) + max(zs)) / 2
    sight = Vector((0.0, -math.sin(math.radians(VIEW_TILT)), math.cos(math.radians(VIEW_TILT))))
    obj.data.transform(Matrix.Translation(-sight * (zc / sight.z)))
    obj.data.update()


def build():
    options = k.args()
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    sheet = None
    if "check" in options:
        sheets = options["check"]
        sheet = os.path.join(sheets, "enemy_G.png") if os.path.isdir(sheets) else sheets
    k.reset()
    bpy.context.scene.view_settings.view_transform = "Standard"
    mats = materials()
    polys = shapes()
    for frame in FRAMES:
        name = model_name(frame)
        if only and name not in only:
            continue
        obj = frame_object(frame, polys, mats)
        triangulate([obj])
        if sheet:  # the solid from straight above in the picture's plane is what the camera sees
            mk.compare("%s (G %d) as the camera sees it" % (name, frame), mk.coverage([obj], 24, 28),
                       k.sprite_mask(sheet, frame))
        to_camera(obj)
        bpy.context.view_layer.update()
        mk.report(name, [obj], os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, [obj])
        data = obj.data
        bpy.data.objects.remove(obj)
        bpy.data.meshes.remove(data)


if __name__ == "__main__":
    build()
