"""The damaged look of DELI's green twin-tank ship (sky layer): sheet C sprites 45, the left half, and 47, the
right half (2x2 each), which the game shows in place of 197 and 199 once a half is hit hard (each half on its
own: one may be damaged while the other is not; DELI, BONUS, New Deli, STATION, VAULT, DEEP ICE). models.cfg:
model tank_pod_dmg_left / tank_pod_dmg_right ... origin; sprite c 45 tank_pod_dmg_left yaw=0, sprite c 47
tank_pod_dmg_right yaw=0. Polished (2026-10-19; it replaces wave3_ao_deli.py's tank_damaged(), which wrecked
wave1_b.py's old tank_pod()).

The ship is polish_tank_pod.py's (its parts imported, unchanged), built whole, damaged, and cut along the
sprites' edge (x = 0) into the two halves as that script cuts the intact ones: the same origin, scale and cut,
so that a damaged half meets its partner, damaged or not. Nothing is moved at the cut: the block's gash fades
out towards it, and the tanks, rails and coils are damaged far from it.

What C 45 draws differently from C 197 (C 47 is its mirror image, but for a few pixels of the core), read
pixel by pixel into DAMAGE below:
- the tank's outer half burnt black (columns 1-10 of rows 4-10), scorched darker green round it and along
  its far edge (row 3), with red cracks in the black: down columns 4 and 7 (rows 5-9), across row 7 between
  and beyond them (hottest where they cross, column 4), and down the tank's end into the bumper (column 2,
  rows 8-10); dark holes where the cracks end;
- the rail burnt through in its middle (columns 9-14 of rows 10-11) and scorched along its front (rows
  11-12), the bumper's front charred (columns 4-9 of row 13);
- the coil's outer half burnt black (columns 8-12 of rows 14-18), a red crack down its rib at column 13 and
  along row 15;
- a black gash across the block's sloping front (rows 5-7), its top and foot scorched (rows 3-4, 8-9);
- the core between the halves blown out: only short stumps of its shell are left on the necks (columns
  21-22), dark red, black inside.

How: where the camera sees a part's damage, its faces are cut across its length into a regular grid, then
along smooth borders (split_along: the burns' and the scorches'), painted by the blurred damage map with
ragged edges (noise), and dented: broad dents and crumpling in the burns, grooves along the cracks with torn
lips, holes at their ends, pushed in along the undamaged surface's normals (nothing moves near the cut). The
cracks are jagged glowing strips laid in the grooves (dropped onto the part from above, strips()): dark red,
red and wider where they cross. The halves get the same damage (mirrored, as the sprites draw it) but their
own jags, crumpling and ragged edges. The core's stumps are new: a broken shell (dull dark red, black inside
and scorched outside, embers along parts of its break and fallen inside). The materials are
polish_tank_pod.py's (fewer: its bumper, neck and cut caps share the block's, rail's and coil grooves'
colours) and the damage's: 15.

Coordinates as in polish_tank_pod.py: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the
camera; the whole ship's x = 0 is the edge between the two sprites, y = 0 the sprites' centre row. Points are
given as (column, row) of C 45 (P()). The left half's damage is built on the left parts; the right half's on
a second set of left parts, mirrored.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes of
the whole ship and of each half against enemy_C.png), --preview <prefix> (the whole ship's and each half's top
and 3/4 views), --only <names>.
"""
import math
import os
import random
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector, noise
from mathutils.bvhtree import BVHTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_tank_pod as tp  # noqa: E402
from polish_sphere_nozzle import smoothstep, split_along  # noqa: E402

# The halves: (name, sprite, the box it covers in the ship's coordinates, its centre), as polish_tank_pod.py.
HALVES = [("tank_pod_dmg_left", 45, (-30.0, 0.0, -20.0, 20.0), -12.0),
          ("tank_pod_dmg_right", 47, (0.0, 30.0, -20.0, 20.0), 12.0)]
SEEDS = {"left": 1, "right": 2}


def P(c, r):
    """A point of C 45 (column, row; pixel (C, R) covers C..C+1, R..R+1) in the whole ship's coordinates."""
    return (c - 24.0, 14.0 - r)


# --- The damage ----------------------------------------------------------------------------------------
# C 45 against C 197, rows 0-19 (the rest is empty): '.' as intact, 't' a shade darker, 's' scorched
# (two or more shades darker), 'c' burnt black, 'x' a black hole, 'e' 'E' 'H' a red crack (dark red, red,
# bright red), ':' dark in both (the outline and the gaps: left out of the blur), 'k' and '_' the core (red
# left, gone), ' ' empty.
DAMAGE = [
    "                        ",
    "                    ::::",
    "    :::::::::::::::::...",
    "  ::tssssssst.......:s..",
    " :.tsscxccccs.......:sss",
    ":cscxccecccst.......:ccc",
    ":cccecceccsst.......:ccc",
    ":cxeHeeEccst........:ccc",
    ":cexeccecc......:.:.:ss.",
    ":cEcx::x:::::::::::::st.",
    ":cEc.t.ssccccccs........",
    "::ssssssssccccs.........",
    ":.ssscssssssss....::::::",
    "::tscccc:::::::::::..:  ",
    " ::sccct::ts:e:::c:..kk_",
    "  :::::::ccceEee:.:..kk_",
    "       ::ccc:e:t:.:..k__",
    "       ::ccc:e:.:.:.ckk_",
    "       ::ctte::.:::::   ",
    "       :::::x::::::     ",
]
BURN = {".": 0.0, "t": 0.42, "s": 0.58, "c": 1.0, "x": 1.0, "e": 1.0, "E": 1.0, "H": 1.0}
BLUR = 0.6                      # the map's blur (pixels)
RAGGED = (0.09, 0.45, 0.04, 1.3)  # noise on it: the edges' broad waves (amplitude, frequency), their jags
CHAR, SCORCH = 0.66, 0.33       # burnt black above this, scorched above that
# The cracks (lines of (column, row)), made jagged (points every JAG_STEP, moved up to JAG across): glowing
# strips laid in grooves pressed into the surface. The strips' half-width (and how much wider where they
# glow hottest; they narrow to their ends), how far off the surface they lie, how often they are sampled; the
# groove's half-width and depth, the torn lips beside it; where the cracks glow hottest ((column, row),
# radius); the holes where they end.
CRACKS = [
    [(7.5, 4.4), (7.4, 5.5), (7.6, 6.5), (7.5, 7.5), (7.45, 8.5), (7.5, 9.6)],
    [(4.5, 5.2), (4.4, 6.4), (4.5, 7.5), (4.6, 8.5), (4.5, 9.5)],
    [(2.3, 7.4), (3.5, 7.6), (4.5, 7.5), (5.5, 7.45), (6.5, 7.55), (7.5, 7.5)],
    [(3.4, 7.6), (2.6, 8.4), (2.45, 9.5), (2.5, 10.7)],
    [(13.5, 13.8), (13.55, 15.0), (13.45, 16.4), (13.3, 17.4), (12.6, 18.3), (12.5, 19.4)],
    [(12.1, 15.5), (13.5, 15.45), (14.5, 15.55), (15.7, 15.5)],
]
JAG_STEP, JAG = 0.55, 0.2
STRIP_HALF, STRIP_HOT, STRIP_LIFT, STRIP_STEP = 0.16, 0.16, 0.05, 0.3
CRACK_HALF, CRACK_DEPTH, CRACK_LIP = 0.8, 0.42, 0.06
HOT = [((4.5, 7.5), 0.9), ((7.5, 7.5), 0.5), ((13.5, 15.5), 0.7), ((2.5, 10.0), 0.6)]
PITS = [((7.5, 4.5), 0.5), ((4.5, 5.5), 0.45), ((2.4, 7.5), 0.45), ((3.5, 8.5), 0.4), ((4.5, 9.6), 0.45),
        ((7.5, 9.6), 0.45), ((12.5, 19.4), 0.4)]
PIT_DEPTH = 0.6
# Dents ((column, row), radius, depth): the tank's burnt end, the rail burnt through, the bumper's charred
# front, the coil's burnt end; and the crumpling all over the burns (mean, amplitude, frequency).
DENTS = [((5.8, 6.2), 2.2, 0.65), ((9.3, 7.3), 1.6, 0.45), ((1.5, 6.6), 1.8, 0.55), ((3.2, 4.3), 1.3, 0.3),
         ((11.9, 10.8), 2.4, 0.85), ((9.4, 10.6), 1.3, 0.45),
         ((6.0, 13.6), 2.0, 0.6),
         ((10.0, 16.0), 2.3, 0.6)]
CRUMPLE = (0.05, 0.12, 0.75)
# The gash across the block's front (rows 5-7): its middle row, half-width (pixels), depth. No surface is
# moved within SEAM of the cut, nor more than partly within SEAM_FADE of it, so that a damaged half meets
# its partner as the intact ones do.
GASH_ROW, GASH_HALF, GASH_DEPTH = 6.5, 1.5, 0.75
SEAM, SEAM_FADE = 0.15, 1.2
# How fine the damaged surfaces are cut where the camera sees them: a grid across the parts' length.
GRID = 1.0

# The core's broken shell: its thickness, and where it breaks off (x) by the angle round its axis (degrees:
# 0 up the screen, 90 towards the camera, 180 down the screen), for each half as its sprite draws it (the
# right half's as seen mirrored, C 47 read right to left); the teeth along the break.
SHELL = 0.34
BREAKS = {
    "left": [(0, -1.1), (35, -1.0), (65, -1.9), (90, -2.35), (115, -2.1), (140, -1.1), (180, -1.15), (230, -1.5),
             (290, -1.85), (330, -1.35)],
    "right": [(0, -1.2), (35, -1.0), (70, -2.2), (100, -1.35), (135, -0.3), (165, -0.45), (200, -0.9), (250, -1.6),
              (300, -1.9), (335, -1.4)],
}
TEETH, TOOTH = 11, 0.2
# Embers fallen inside the shell: (x, angle round the axis, radius, hot).
BITS = {"left": [(-2.05, 262, 0.42, True), (-2.6, 288, 0.34, False), (-1.75, 238, 0.3, False)],
        "right": [(-1.95, 275, 0.4, True), (-2.55, 250, 0.33, False)]}


def materials():
    """polish_tank_pod.py's materials (its bumper as the block, its neck as the rail, its cut caps as the coil's
    grooves: the same colours, fewer materials) and the damage's."""
    pal = k.level_palette()
    m = tp.materials({})
    m["bumper"], m["neck"], m["cut"] = m["block"], m["rail"], m["coil_groove"]
    m.update({
        "char": k.material("tankd_char", palette=0x21, metallic=0.2, roughness=0.62),
        "scorch_green": k.material("tankd_scorch_green", palette=0x25, metallic=0.3, roughness=0.5),
        "scorch": k.material("tankd_scorch", palette=0x54, metallic=0.35, roughness=0.5),
        "ember": k.material("tankd_ember", palette=0x72, roughness=0.5, emission=pal[0x73], emission_strength=0.85),
        "ember_hot": k.material("tankd_ember_hot", palette=0x75, roughness=0.45, emission=pal[0x76],
                                emission_strength=1.3),
        "core": k.material("tankd_core", palette=0x71, metallic=0.1, roughness=0.3, emission=pal[0x71],
                           emission_strength=0.3),
    })
    return m


def jagged(points, rng):
    """A crack's line, resampled every JAG_STEP and each inner point moved across it at random."""
    out = []
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        n = max(1, round(math.hypot(x1 - x0, y1 - y0) / JAG_STEP))
        out += [(x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n) for i in range(n)]
    out.append(points[-1])
    moved = [out[0]]
    for i in range(1, len(out) - 1):
        tx, ty = out[i + 1][0] - out[i - 1][0], out[i + 1][1] - out[i - 1][1]
        length = math.hypot(tx, ty) or 1.0
        o = rng.uniform(-JAG, JAG)
        moved.append((out[i][0] - ty / length * o, out[i][1] + tx / length * o))
    return moved + [out[-1]]


class Damage:
    """The damage at points of the whole ship's left half (fold: points right of the cut are read as their
    mirror images, for the block across the middle); seed: the half's own jags and noise."""

    def __init__(self, seed, fold=False):
        cells = [(P(c + 0.5, r + 0.5), BURN[ch]) for r, line in enumerate(DAMAGE) for c, ch in enumerate(line)
                 if ch in BURN]
        self.centres = np.array([p for p, _ in cells], dtype=float)
        self.values = np.array([v for _, v in cells], dtype=float)
        rng = random.Random(seed * 7919)
        self.lines = [jagged([P(*q) for q in line], rng) for line in CRACKS]
        segments = [s for points in self.lines for s in zip(points, points[1:])]
        self.a = np.array([s[0] for s in segments], dtype=float)
        self.d = np.array([s[1] for s in segments], dtype=float) - self.a
        self.dd = np.maximum((self.d * self.d).sum(1), 1e-12)
        self.hots = [(P(*c), r) for c, r in HOT]
        self.pits = [(P(*c), r) for c, r in PITS]
        self.dents = [(P(*c), r, depth) for c, r, depth in DENTS]
        self.offset = Vector((seed * 7.31, seed * -3.17, seed * 5.53))
        self.fold = fold

    def xy(self, points):
        a = np.array([(p[0], p[1]) for p in points], dtype=float).reshape(-1, 2)
        if self.fold:
            a[:, 0] = -np.abs(a[:, 0])
        return a

    def wobble(self, p, scale=1.0):
        """Smooth noise, -1..1 (broad), at p."""
        return noise.noise(Vector(p) * scale + self.offset)

    def burn(self, points):
        """How burnt (0 intact, about 0.5 scorched, 1 black): the map blurred, its edges in waves and jags."""
        xy = self.xy(points)
        out = np.empty(len(xy))
        for i in range(0, len(xy), 2048):
            q = xy[i:i + 2048]
            d2 = ((q[:, None, :] - self.centres[None]) ** 2).sum(2)
            w = np.exp(-d2 / (2 * BLUR * BLUR))
            out[i:i + 2048] = (w * self.values[None]).sum(1) / np.maximum(w.sum(1), 1e-300)
        a0, f0, a1, f1 = RAGGED
        return out + np.array([a0 * self.wobble(p, f0) + a1 * noise.noise(Vector(p) * f1 - self.offset)
                               for p in points])

    def heat(self, p):
        """How near a hot spot of the cracks (1 at its middle, 0 beyond twice its radius)."""
        x, y = self.xy([p])[0]
        return max(1.0 - smoothstep(0.0, 2.0 * r, math.hypot(x - c[0], y - c[1])) for c, r in self.hots)

    def crack(self, points):
        """The distance to the nearest crack in the top view (pixels)."""
        xy = self.xy(points)
        out = np.empty(len(xy))
        for i in range(0, len(xy), 4096):
            q = xy[i:i + 4096]
            rel = q[:, None, :] - self.a[None]
            t = np.clip((rel * self.d[None]).sum(2) / self.dd[None], 0.0, 1.0)
            near = self.a[None] + t[:, :, None] * self.d[None]
            out[i:i + 4096] = np.sqrt(((q[:, None, :] - near) ** 2).sum(2)).min(1)
        return out

    def pit(self, p):
        """1 at a hole's middle, 0 at its edge (negative outside)."""
        x, y = self.xy([p])[0]
        return max(1.0 - math.hypot(x - c[0], y - c[1]) / r for c, r in self.pits)

    def dented(self, p):
        x, y = self.xy([p])[0]
        return any(math.hypot(x - c[0], y - c[1]) < r for c, r, _ in self.dents)

    def depth(self, p, burn, crack):
        """How far the surface is pushed in at p (negative: out)."""
        x, y = self.xy([p])[0]
        d = 0.0
        for c, radius, depth in self.dents:
            t = math.hypot(x - c[0], y - c[1]) / radius
            if t < 1:
                d += depth * (1 - t * t) ** 2 * (0.85 + 0.15 * self.wobble(p, 0.6))
        for c, radius in self.pits:
            t = math.hypot(x - c[0], y - c[1]) / radius
            if t < 1:
                d += PIT_DEPTH * (1 - t * t) ** 1.5
        if crack < CRACK_HALF:
            d += CRACK_DEPTH * (1 - (crack / CRACK_HALF) ** 2)
        b = min(1.0, max(0.0, burn))
        d -= CRACK_LIP * b * math.exp(-((crack - CRACK_HALF - 0.1) / 0.3) ** 2)
        mean, amplitude, frequency = CRUMPLE
        d += b * (mean + amplitude * noise.noise(Vector(p) * frequency + self.offset * 1.7))
        return d

    def damaged(self, p, band=None):
        """Whether p needs the finer grid: burnt or dented (band: only where band(p) is true)."""
        if band:
            return band(p)
        return self.burn([p])[0] > 0.2 or self.dented(p)


# --- Damaging a part -------------------------------------------------------------------------------------

def facing(n):
    """How much a surface with normal n faces the game's camera (20 degrees from straight down, from the
    bottom of the screen): above 0 seen."""
    return 0.94 * n.z - 0.342 * n.y


def grid(bm, region):
    """Cuts the faces for which region(face) is true across x, between the x positions their vertices
    already have (the parts' rings), into strips no wider than GRID."""
    faces = {f for f in bm.faces if region(f)}
    xs = sorted({round(v.co.x, 3) for f in faces for v in f.verts})
    cuts = []
    for a, b in zip(xs, xs[1:]):
        n = math.ceil((b - a) / GRID - 0.2)
        cuts += [a + (b - a) * i / n for i in range(1, n)]
    for x in cuts:
        before = set(bm.faces)
        geom = list(faces) + list({e for f in faces for e in f.edges}) + list({v for f in faces for v in f.verts})
        bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-5, plane_co=(x, 0.0, 0.0), plane_no=(1.0, 0.0, 0.0))
        faces = {f for f in faces if f.is_valid} | (set(bm.faces) - before)


def damage(obj, dmg, scorch, mats, smooth_angle, extra=None, band=None, force_char=None):
    """Burns, dents and grooves a part (the cracks' glowing strips are laid in afterwards, strips()): scorch
    names the material of its scorched faces (None: none, black or as it was); extra(p): more depth (the
    block's gash), band(p): where that needs the grid; force_char(centre): faces painted black whatever the
    map says."""
    source = tp.NormalSource(obj)  # the undamaged surface's shading, to push along

    def seen(p, least=-0.15):
        n = source.normal(p, p)
        return n is not None and facing(n) > least

    bm = bmesh.new()
    bm.from_mesh(obj.data)
    if min(v.co.x for v in bm.verts) < 0.0 < max(v.co.x for v in bm.verts):
        # Across the cut (the block): edges along it, which stay where they are (SEAM).
        bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-5,
                               plane_co=(0.0, 0.0, 0.0), plane_no=(1.0, 0.0, 0.0))
    bm.normal_update()
    grid(bm, lambda f: facing(f.normal) > 0.05 and dmg.damaged(f.calc_center_median(), band))
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    # The borders where the camera looks (the vertices it doesn't see are given the threshold, so that no
    # edge of theirs is cut): the burns' and the scorches'.
    looked = dict(zip(bm.verts, (seen(v.co) for v in bm.verts)))
    burn = dict(zip(bm.verts, dmg.burn([v.co for v in bm.verts])))
    for threshold in ((CHAR, SCORCH) if scorch else (CHAR,)):
        split_along(bm, {v: (burn[v] if looked[v] else threshold) for v in bm.verts}, threshold)
        for v in bm.verts:
            if v not in burn:
                burn[v], looked[v] = threshold, True
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    bm.normal_update()
    # The paint, by the faces' middles.
    slots = list(obj.data.materials)

    def slot(key):
        if mats[key] not in slots:
            obj.data.materials.append(mats[key])
            slots.append(mats[key])
        return slots.index(mats[key])

    faces = list(bm.faces)
    centres = [f.calc_center_median() for f in faces]
    for f, c, b in zip(faces, centres, dmg.burn(centres)):
        if b > CHAR or dmg.pit(c) > 0.0 or (force_char and force_char(c)):
            f.material_index = slot("char")
        elif b > SCORCH and scorch:
            f.material_index = slot(scorch)
    # The dents, along the undamaged surface's normals (where the camera looks).
    verts = list(bm.verts)
    points = [v.co.copy() for v in verts]
    for v, p, b, cr in zip(verts, points, dmg.burn(points), dmg.crack(points)):
        n = source.normal(p, p) or v.normal
        weight = smoothstep(-0.3, 0.0, facing(n)) * smoothstep(SEAM, SEAM_FADE, abs(p.x))
        if weight > 0.0:
            v.co = p - n * (dmg.depth(p, b, cr) + (extra(p) if extra else 0.0)) * weight
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    return k.smooth(obj, smooth_angle)


def block_gash(dmg):
    """The gash across the block's front: its depth(p), and where it is."""
    y0 = P(0, GASH_ROW + 0.5)[1]

    def depth(p):
        dy = (p[1] - y0 - 0.3 * dmg.wobble(p, 0.6)) / GASH_HALF
        if abs(dy) >= 1.0:
            return 0.0
        return GASH_DEPTH * (1 - dy * dy) ** 1.5 * (0.75 + 0.25 * dmg.wobble(p, 0.9))
    return depth, lambda p: abs(p[1] - y0) < GASH_HALF + 0.4


def resample(points, step):
    """A line's points about step apart along it, with the distance along it of each."""
    out, along = [points[0]], [0.0]
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        length = math.hypot(x1 - x0, y1 - y0)
        n = max(1, round(length / step))
        for i in range(1, n + 1):
            out.append((x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n))
            along.append(along[-1] + length / n)
    return out, along


def strips(part, dmg, mats):
    """The cracks over a damaged part: glowing strips along them, each edge point dropped onto the part
    from above (so that they lie in its grooves) and lifted a little off it, narrowing to their ends, wider
    where they glow hottest (red there, dark red elsewhere). None if no crack lies on the part."""
    mesh = part.data
    bvh = BVHTree.FromPolygons([v.co.copy() for v in mesh.vertices], [tuple(p.vertices) for p in mesh.polygons])
    bm = bmesh.new()
    keys = []

    def lay(run):
        for (l0, r0, n0, h0), (l1, r1, n1, h1) in zip(run, run[1:]):
            verts = [bm.verts.new(c) for c in (l0, r0, r1, l1)]
            face = bm.faces.new(verts)
            face.normal_update()
            if face.normal.dot(n0 + n1) < 0:
                face.normal_flip()
            keys.append("ember_hot" if (h0 + h1) / 2 > 0.5 else "ember")

    for line in dmg.lines:
        points, along = resample(line, STRIP_STEP)
        total = along[-1]
        run = []
        for i, (x, y) in enumerate(points):
            a, b = points[max(i - 1, 0)], points[min(i + 1, len(points) - 1)]
            tx, ty = b[0] - a[0], b[1] - a[1]
            length = math.hypot(tx, ty) or 1.0
            sx, sy = -ty / length, tx / length
            heat = dmg.heat((x, y, 0.0))
            ends = smoothstep(0.0, 0.9, along[i]) * smoothstep(0.0, 0.9, total - along[i])
            w = (STRIP_HALF + STRIP_HOT * heat) * (0.3 + 0.7 * ends)
            hits = []
            for sign in (1.0, -1.0):
                loc, normal, _, _ = bvh.ray_cast(Vector((x + sx * w * sign, y + sy * w * sign, 60.0)),
                                                 Vector((0.0, 0.0, -1.0)))
                if loc is None:
                    break
                if normal.z < 0:
                    normal = -normal
                hits.append((loc + normal * STRIP_LIFT, normal))
            if len(hits) < 2:
                lay(run)
                run = []
                continue
            run.append((hits[0][0], hits[1][0], hits[0][1] + hits[1][1], heat))
        lay(run)
    if not keys:
        bm.free()
        return None
    names = sorted(set(keys))
    out = bpy.data.meshes.new("cracks")
    for key in names:
        out.materials.append(mats[key])
    bm.faces.ensure_lookup_table()
    for f, key in zip(bm.faces, keys):
        f.material_index = names.index(key)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-4)
    bm.to_mesh(out)
    bm.free()
    obj = bpy.data.objects.new("cracks", out)
    bpy.context.scene.collection.objects.link(obj)
    return k.smooth(obj, 60)


# --- The core's broken shell --------------------------------------------------------------------------

def periodic(table, angle):
    """Interpolates (degrees, value) pairs round the circle (smoothly)."""
    angle %= 360.0
    pts = table + [(table[0][0] + 360.0, table[0][1])]
    for (a0, v0), (a1, v1) in zip(pts, pts[1:]):
        if a0 <= angle <= a1:
            return v0 + (v1 - v0) * smoothstep(0.0, 1.0, (angle - a0) / (a1 - a0))
    return table[0][1]


def stump(mats, side, seed):
    """The core's shell broken off its neck (built for the left half; the right one's is mirrored): from
    inside the neck to a jagged break, dull dark red outside with black scorch, black inside, embers along
    parts of the break and a few fallen inside."""
    x0 = tp.NECK[1] - 0.05  # where the intact core starts, inside the neck
    x1 = -x0
    offset = Vector((seed * 4.1, seed * 1.3, -seed * 2.7))

    def radius(x):
        return tp.CORE_R + tp.CORE_BULGE * math.cos(math.pi * x / (2 * x1)) ** 2

    def edge(deg):
        t = (deg / 360.0 * TEETH + 0.25 * seed) % 1.0
        tooth = TOOTH * (1 - 4 * abs(t - 0.5))  # a triangle wave: the break's teeth
        x = periodic(BREAKS[side], deg) + tooth + 0.12 * noise.noise(Vector((deg / 40.0, seed, 0.0)) + offset)
        return min(x, -0.12)

    segments, rows = 20, 3
    cy, cz = tp.COIL_Y, tp.COIL_Z
    bm = bmesh.new()
    outer, inner = [], []
    for i in range(rows + 1):
        ro, ri = [], []
        for j in range(segments):
            deg = 360.0 * j / segments
            x = x0 + (edge(deg) - x0) * i / rows
            r = radius(x)
            c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
            ro.append(bm.verts.new((x, cy + r * c, cz + r * s)))
            ri.append(bm.verts.new((x, cy + (r - SHELL) * c, cz + (r - SHELL) * s)))
        outer.append(ro)
        inner.append(ri)
    kinds = {}
    for i in range(rows):
        for j in range(segments):
            jn = (j + 1) % segments
            kinds[bm.faces.new((outer[i][j], outer[i][jn], outer[i + 1][jn], outer[i + 1][j]))] = "outer"
            kinds[bm.faces.new((inner[i][j], inner[i + 1][j], inner[i + 1][jn], inner[i][jn]))] = "char"
    for j in range(segments):
        jn = (j + 1) % segments
        kinds[bm.faces.new((outer[rows][j], outer[rows][jn], inner[rows][jn], inner[rows][j]))] = "rim"
        kinds[bm.faces.new((outer[0][jn], outer[0][j], inner[0][j], inner[0][jn]))] = "char"
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    keys = []
    for f in bm.faces:
        c = f.calc_center_median()
        kind = kinds[f]
        if kind == "outer":
            # Black scorch over the dull red, more of it towards the break.
            soot = noise.noise(c * 1.3 + offset) + 0.5 * smoothstep(x0 + 0.8, -1.0, c.x)
            keys.append("char" if soot > 0.55 else "core")
        elif kind == "rim":
            keys.append("ember" if noise.noise(c * 1.7 - offset) > -0.15 else "char")
        else:
            keys.append("char")
    names = []
    for key in keys:
        if key not in names:
            names.append(key)
    mesh = bpy.data.meshes.new("stump")
    for key in names:
        mesh.materials.append(mats[key])
    for f, key in zip(bm.faces, keys):
        f.material_index = names.index(key)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("stump", mesh)
    bpy.context.scene.collection.objects.link(obj)
    k.smooth(obj, 40)
    parts = [obj]
    # The embers fallen inside: small lumps on the shell's floor.
    for n, (x, deg, r, hot) in enumerate(BITS[side]):
        ri = radius(x) - SHELL - r * 0.55
        c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
        bm = bmesh.new()
        bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
        for v in bm.verts:
            v.co *= 1.0 + 0.3 * noise.noise(v.co * 2.5 / r + offset + Vector((n, 0, 0)))
            v.co.z *= 0.75
            v.co += Vector((x, cy + ri * c, cz + ri * s))
        mesh = bpy.data.meshes.new(f"ember_bit{n}")
        bm.to_mesh(mesh)
        bm.free()
        bit = bpy.data.objects.new(f"ember_bit{n}", mesh)
        bpy.context.scene.collection.objects.link(bit)
        bit.data.materials.append(mats["ember_hot" if hot else "ember"])
        parts.append(k.smooth(bit, 60))
    return parts


# --- The whole ship ------------------------------------------------------------------------------------

def mirror_in_place(obj, angle):
    obj.data.transform(Matrix.Scale(-1, 4, (1, 0, 0)))
    obj.data.flip_normals()
    return k.smooth(obj, angle)


def build_whole(mats):
    """The damaged ship: each half's tank, rail, coil, webs and core stump (the right ones built as left
    ones with their own noise and mirrored), the block across the middle."""
    for side, seed in SEEDS.items():
        dmg = Damage(seed)
        parts = [
            (damage(tp.tank(mats), dmg, "scorch_green", mats, 50), 50),
            (damage(tp.rail(mats), dmg, "scorch", mats, 50), 50),
            # The coil is dark already (no scorch); its end at the core (the neck's end face) shows inside the
            # broken shell: black.
            (damage(tp.coil(mats), dmg, None, mats, 55, force_char=lambda c: c.x > tp.NECK[1] - 0.08), 55),
        ]
        for part, _ in list(parts):
            crack = strips(part, dmg, mats)
            if crack:
                crack.name = "cracks_" + part.name
                parts.append((crack, 60))
        parts += [(o, 55) for o in tp.webs(mats)] + [(o, 40 if o.name.startswith("stump") else 60)
                                                    for o in stump(mats, side, seed)]
        for obj, angle in parts:
            obj.name = obj.data.name = obj.name.split(".")[0] + ("_l" if side == "left" else "_r")
            if side == "right":
                mirror_in_place(obj, angle)
    dmg = Damage(3, fold=True)
    gash, band = block_gash(dmg)
    damage(tp.block(mats), dmg, "scorch", mats, 45, extra=gash, band=band)
    return [o for o in bpy.context.scene.objects if o.type == "MESH"]


def masks(sheet):
    left, right = k.sprite_mask(sheet, 45), k.sprite_mask(sheet, 47)
    return left, right, [left[y] + right[y] for y in range(28)]


def build():
    options = k.args()
    outdir = options.get("outdir", os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "enemies"))
    only = options["only"].split(",") if "only" in options else None
    sheets = options.get("check")
    sheet = None
    if sheets:
        sheet = os.path.join(sheets, "enemy_C.png") if os.path.isdir(sheets) else sheets
    k.reset()
    mats = materials()
    whole = build_whole(mats)
    used = {m.name for o in whole for m in o.data.materials}
    print("== whole damaged ship (C 45 + 47): %d triangles, %d objects, %d materials" % (
        tp.triangles(whole), len(whole), len(used)))
    if sheet:
        tp.check_mask(masks(sheet)[2], "whole (45 + 47)", whole)
    if "preview" in options:
        tp.preview(options["preview"] + "tank_pod_dmg_whole", whole, size=(48, 28), scale=10, distance=1.15)
    for (name, sprite, box, centre), mask in zip(HALVES, masks(sheet)[:2] if sheet else (None, None)):
        if only and name not in only:
            continue
        pieces = [p for p in (tp.cut(src, box, mats["cut"]) for src in whole) if p is not None]
        tp.move(pieces, -centre, 0.0)
        used = {m.name for o in pieces for m in o.data.materials}
        print("== %s (C %d): %d triangles, %d materials: %s" % (name, sprite, tp.triangles(pieces), len(used),
                                                               ", ".join(sorted(used))))
        if mask:
            tp.check_mask(mask, "%s (C %d)" % (name, sprite), pieces)
        tp.export(pieces, os.path.join(outdir, name + ".glb"))
        if "preview" in options:
            tp.preview(options["preview"] + name, pieces)
        for obj in pieces:
            bpy.data.objects.remove(obj)


if __name__ == "__main__":
    build()
