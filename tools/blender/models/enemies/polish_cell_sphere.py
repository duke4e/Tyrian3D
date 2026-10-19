"""The sphere of cells, polished (2026-10-19; it replaces wave1_b.py's cell_sphere()): one model for two sprites
that draw the same picture in two ramps, models.cfg's color=sprite giving each its colour:

- sheet 3 sprite 229 (2x2: a 23 x 23 ball in the 24 x 28 cell; ramp 7, lava; SIDE EXIT, ICE EXIT, BRAINIAC,
  ICESECRET, sky and top layers, and CORE and THE CORE, where enemy 254 pulses: 229 231 233 235 233 231,
  three game frames each);
- sheet 5 sprite 89 (the same picture in ramp 3, ice; SURFACE, LAVA EXIT, BRAINIAC, NOSE DRIP, sky and top).

As the 4x upscales draw it: a ball whose shell is a lattice of rounded strands round deep round holes, a
dozen of them on the side seen (the larger ones about five pixels across), through which a darker core
shows; where three holes meet, the strands widen into knots. The strands are the light colour (yellow to
orange in lava, light steel blue in ice), brightest at the upper left where the light falls, the holes'
walls dark and their floors a little lighter (the core's glow in lava), the whole ringed by a dark rim.

The holes on the side seen are placed where the upscale of 3 229 draws them (FRONT); those round the back
are spread evenly. The shell is the Voronoi diagram of the holes' middles on the ball (from their convex
hull): each cell's hole is the cell drawn in by the strand's half-width, its corners rounded, and the
surface rounds over its edge into it and drops to its floor. Each cell is built as rings round its middle
that follow those contours (rays from the middle to points along the cell's edges, the rings where the
distance in from the hole's edge takes given values), so the holes are smooth and the colours change
along the rings: the strands, the walls and the floors. The cells round the back, which the game's camera
doesn't see, have fewer rings and rays.

The materials are palette shades of ramp 7 without coloured emission: models.cfg colours them with the
sprite's frame (color=sprite: every index takes the frame's ramp and keeps its shade), so the same model is
the lava ball and the ice ball; emission would keep its own colour. The game's camera sees much of the
ball's side away from its sun: the strands take the sprite's lighter middle shade (9) and the holes' floors
a lighter shade than their walls, so the lattice still reads there in both ramps (checked in the game's
view; a white glow would turn the lava's strands pink). The dark rim is painted where the surface turns
away from the game's camera (20 degrees from straight down, from the bottom of the screen), as the
sprite's outline rings the ball, and the holes grow shallow there so that the outline stays round.

The frames of CORE's pulsing ball are the same ball smaller (frame models, which no other enemy uses: 3 231,
233 and 235 appear only in enemy 254's animation): 231 is 19 pixels across, 233 17 and 235 13, all round the
same middle (pixel 11.5, 13.5): cell_sphere_231, cell_sphere_233 and cell_sphere_235 (models.cfg: frame 3 231
cell_sphere_231 and so on), with fewer rays the smaller they are.

Origin at the sprite's centre (pixel 12, 14); +Y up the sprite, +Z towards the camera. The game centres sky
objects in height, so the ball's height doesn't matter.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each model's
silhouette against its sprite), --preview <prefix>, --only <name,...>, --ramp <0-15> (the models in another
ramp, as color=sprite shows them, written as <name>_r<ramp>.glb: for checks only).
"""
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
from polish_sphere_nozzle import fibonacci_points, smoothstep, split_along  # noqa: E402

CENTRE = Vector((-0.5, 0.5, 0.0))   # the ball's middle (the sprite's columns 0-22, rows 2-24)
RADII = Vector((11.3, 11.3, 10.7))   # to the strands' tops (the sprite's outline half a pixel outside)
SCALE = 11.2                         # pixels per radian along the shell, for widths and distances
VIEW = Vector((0.0, -math.sin(math.radians(20)), math.cos(math.radians(20))))  # towards the game's camera
RAMP = 7
SEED = 229

# The holes the upscale of 3 229 draws on the side seen: (column, row) of their middles in the sprite's
# pixel grid, and how wide the strands round them are (half-widths, pixels).
FRONT = [((7.6, 7.6), 0.6), ((12.0, 7.4), 0.55), ((17.2, 5.6), 0.65), ((4.3, 11.2), 0.65), ((9.6, 11.0), 0.5),
         ((17.6, 10.4), 0.65), ((13.6, 13.6), 0.55), ((21.0, 13.6), 0.7), ((7.4, 16.4), 0.6), ((2.4, 16.8), 0.7),
         ((17.0, 17.2), 0.6), ((12.2, 20.2), 0.55), ((16.2, 21.2), 0.65), ((6.6, 21.6), 0.7)]
BACK = 24              # holes spread round the rest of the ball
STRAND = (0.6, 0.75)   # the back holes' strand half-widths: a random value in this range
RIM = 0.75             # the radius of the strand's edge rounding over into a hole
WALL = 0.9             # how far in from the rim the wall reaches the floor
DEPTH = (2.2, 3.2)     # how deep the holes are: small to large holes
CREST = 0.25           # how much higher the strands' middles are than their edges
FLAT = -0.55           # the strands' tops are level farther than this from the holes (t below it)
HOLE_CORNER = 1.2      # the radius of a hole's rounded corners at its edge (growing with the depth)

# The rings round each cell's middle by t (pixels in from the hole's edge) and the colour of the band
# inside each: on the side seen, and round the back.
RINGS = [(0.0, "strand"), (0.15, "wall"), (0.4, "wall"), (0.75, "wall"), (1.15, "wall"), (1.65, "floor")]
RINGS_BACK = [(0.15, "wall"), (0.75, "wall"), (1.65, "floor")]
SPACING = 1.0          # rays along the cells' edges on the side seen (pixels apart; twice that round the back)
SEEN = -0.3            # cells whose middle faces the game's camera more than this are built finely
EDGE = 0.12            # the outline where the ball's facing towards the camera is below this

# The colours: (shade of the ramp, roughness). The strands, the holes' walls, their floors (lighter: the
# core showing through), and the strands and holes darker towards the ball's rim (the sprite's outline).
SHADES = {
    "strand": (9, 0.4),
    "wall": (3, 0.5),
    "floor": (6, 0.45),
    "edge_strand": (6, 0.4),
    "edge_hole": (1, 0.5),
}

# The frames: (model, sprite, its size against 229's).
FRAMES = [("cell_sphere", "3:229", 1.0), ("cell_sphere_231", "3:231", 19.0 / 23.0),
          ("cell_sphere_233", "3:233", 17.0 / 23.0), ("cell_sphere_235", "3:235", 13.0 / 23.0)]
CHECKS = {"cell_sphere": ["3:229", "5:89"]}


def to_direction(col, row):
    """The direction from the ball's middle to the point of the sprite at (column, row) on the side seen."""
    u = (col - 12.0 - CENTRE.x) / RADII.x
    v = (14.0 - row - CENTRE.y) / RADII.y
    w = math.sqrt(max(0.0, 1.0 - u * u - v * v))
    return Vector((u, v, w)).normalized()


def base_normal(d):
    return Vector((d.x / RADII.x, d.y / RADII.y, d.z / RADII.z)).normalized()


def facing(d):
    return base_normal(d).dot(VIEW)


def direction_of(co, scale):
    """The direction (of the unit ball) of a point of the scaled shell."""
    c = (co - CENTRE) / scale
    return Vector((c.x / RADII.x, c.y / RADII.y, c.z / RADII.z)).normalized()


class Lattice:
    """The holes: their middles on the unit ball, the strand's half-width round each, their depths, and
    the Voronoi diagram of the middles (each cell's corners in order and its neighbours)."""

    def __init__(self):
        rng = random.Random(SEED)
        self.seeds = [to_direction(*p) for p, _ in FRONT]
        self.half = [w for _, w in FRONT]
        fixed = len(self.seeds)
        # The back: evenly spread points kept away from the front's, relaxed a few times so that they
        # don't crowd each other (the front's stay put).
        candidates = fibonacci_points(BACK * 3, rng, jitter=0.5)
        candidates = [c for c in candidates if min(c.angle(s) for s in self.seeds[:fixed]) > 0.42]
        rng.shuffle(candidates)
        back = []
        for c in candidates:
            if all(c.angle(b) > 0.5 for b in back) and len(back) < BACK:
                back.append(c)
        for _ in range(12):
            moved = []
            for b in back:
                push = Vector()
                for o in self.seeds[:fixed] + back:
                    if o is b:
                        continue
                    a = b.angle(o)
                    if a < 0.75:
                        away = b - o * b.dot(o)
                        if away.length > 1e-9:
                            push += away.normalized() * (0.75 - a) * 0.3
                moved.append((b + push).normalized())
            back = moved
        self.seeds += back
        self.half += [rng.uniform(*STRAND) for _ in back]
        self.voronoi()
        # Each hole's size: the distance to its nearest neighbour (pixels); bigger holes are deeper.
        self.size = [min(self.seeds[i].angle(self.seeds[j]) for j in self.neighbours[i]) * SCALE
                     for i in range(len(self.seeds))]
        lo, hi = min(self.size), max(self.size)
        self.depth = [DEPTH[0] + (DEPTH[1] - DEPTH[0]) * (s - lo) / max(hi - lo, 1e-6) for s in self.size]

    def voronoi(self):
        """The cells: the convex hull of the middles is their Delaunay triangulation; its triangles'
        circumcentres on the ball are the cells' corners."""
        bm = bmesh.new()
        verts = [bm.verts.new(s) for s in self.seeds]
        bmesh.ops.convex_hull(bm, input=verts)
        bm.verts.index_update()
        tris = [tuple(v.index for v in f.verts) for f in bm.faces]
        bm.free()
        self.corners = []
        incident = [[] for _ in self.seeds]
        for t, (a, b, c) in enumerate(tris):
            pa, pb, pc = self.seeds[a], self.seeds[b], self.seeds[c]
            n = (pb - pa).cross(pc - pa).normalized()
            if n.dot(pa + pb + pc) < 0:
                n = -n
            self.corners.append(n)
            for i in (a, b, c):
                incident[i].append(t)
        self.cells, self.neighbours = [], []
        for i, s in enumerate(self.seeds):
            # The corners round the middle, counter-clockwise seen from outside.
            ref = (self.corners[incident[i][0]] - s * s.dot(self.corners[incident[i][0]])).normalized()
            side = s.cross(ref)
            def angle(t, s=s, ref=ref, side=side):
                d = self.corners[t] - s * s.dot(self.corners[t])
                return math.atan2(d.dot(side), d.dot(ref))
            ring = sorted(incident[i], key=angle)
            self.cells.append(ring)
            neighbours = set()
            for t in ring:
                neighbours |= set(tris[t])
            neighbours.discard(i)
            self.neighbours.append(sorted(neighbours))

    def plane(self, i):
        """Cell i in the plane touching the ball at its seed (gnomonic: the edges stay straight), in pixels:
        the basis, the edges as (outward normal, distance from the seed) and the incentre (the point
        farthest from the edges) with its distance from them."""
        sd = self.seeds[i]
        e1 = (self.corners[self.cells[i][0]] - sd * sd.dot(self.corners[self.cells[i][0]])).normalized()
        e2 = sd.cross(e1)
        pts = [self.project(self.corners[t], sd, e1, e2) for t in self.cells[i]]
        edges = []
        for a, b in zip(pts, pts[1:] + pts[:1]):
            n = Vector((b.y - a.y, a.x - b.x)).normalized()
            h = n.dot(a)
            if h < 0:
                n, h = -n, -h
            edges.append((n, h))

        def clearance(c):
            return min(h - n.dot(c) for n, h in edges)
        # The incentre: a grid search over the corners' box, narrowed round the best point.
        lo = Vector((min(p.x for p in pts), min(p.y for p in pts)))
        hi = Vector((max(p.x for p in pts), max(p.y for p in pts)))
        best = Vector((0.0, 0.0))
        size = hi - lo
        centre = (lo + hi) / 2
        for _ in range(6):
            cands = [centre + Vector((size.x * (u / 8 - 0.5), size.y * (v / 8 - 0.5))) for u in range(9) for v in range(9)]
            best = max(cands + [best], key=clearance)
            centre, size = best, size * 0.35
        return sd, e1, e2, edges, best, clearance(best)

    @staticmethod
    def project(q, sd, e1, e2):
        g = q / q.dot(sd) - sd
        return Vector((g.dot(e1), g.dot(e2))) * SCALE

    @staticmethod
    def unproject(p, sd, e1, e2):
        return (sd + (e1 * p.x + e2 * p.y) / SCALE).normalized()

    @staticmethod
    def inset(edges, d):
        """The cell drawn in by d (a convex polygon, its corners), or [] if nothing is left."""
        poly = [Vector((-60.0, -60.0)), Vector((60.0, -60.0)), Vector((60.0, 60.0)), Vector((-60.0, 60.0))]
        for n, h in edges:
            out = []
            for k_, a in enumerate(poly):
                b = poly[(k_ + 1) % len(poly)]
                fa, fb = n.dot(a) - (h - d), n.dot(b) - (h - d)
                if fa <= 0:
                    out.append(a)
                if fa * fb < 0:
                    out.append(a + (b - a) * (fa / (fa - fb)))
            poly = out
            if len(poly) < 3:
                return []
        return poly

    @staticmethod
    def distance(p, poly):
        """From p to the convex polygon (0 inside)."""
        inside = True
        best = 1e9
        for k_, a in enumerate(poly):
            b = poly[(k_ + 1) % len(poly)]
            e = b - a
            if e.x * (p.y - a.y) - e.y * (p.x - a.x) < 0:
                inside = False
            f = max(0.0, min(1.0, (p - a).dot(e) / max(e.dot(e), 1e-12)))
            best = min(best, (p - a - e * f).length)
        return 0.0 if inside else best

    def contour(self, edges, r_in, i, t):
        """The hole's contour at t (pixels in from its edge): the cell drawn in by half-width + t with its
        corners rounded (radius HOLE_CORNER + t, so that the floors are round), as (polygon, radius): the
        points within radius of the polygon. None where the hole doesn't reach so deep."""
        d = self.half[i] + max(t, 0.0)
        if d >= r_in - 0.02:
            return None
        radius = min(HOLE_CORNER + max(t, 0.0), r_in - d - 0.01)
        poly = self.inset(edges, d + radius)
        return (poly, radius) if poly else None

    def reach(self, shape, origin, direction, limit):
        """How far from origin along direction the ray leaves the shape (polygon, radius)."""
        poly, radius = shape
        lo, hi = 0.0, limit
        if self.distance(origin + direction * hi, poly) <= radius:
            return hi
        for _ in range(26):
            mid = (lo + hi) / 2
            if self.distance(origin + direction * mid, poly) <= radius:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2

    def height(self, t, i):
        """How far the surface lies below the strands' tops at t in cell i (pixels)."""
        if t <= 0.0:
            return CREST * smoothstep(FLAT, 0.0, t)
        # The rim rounding over (a quarter circle), then the wall down to the floor.
        r = min(t, RIM)
        drop = RIM - math.sqrt(max(0.0, RIM * RIM - r * r))
        if t > RIM:
            drop += (self.depth[i] - RIM) * smoothstep(0.0, WALL, t - RIM)
        return CREST + drop


def slerp_points(a, b, count):
    """count + 1 points from a to b along the ball (normalised linear steps, a and b included)."""
    return [(a * (1 - f) + b * f).normalized() for f in (c / count for c in range(count + 1))]


def shell(name, lattice, mats, scale):
    """The ball: each cell's rings round its middle, joined into one closed surface."""
    keys = list(SHADES.keys())
    fine = [facing(s) > SEEN for s in lattice.seeds]
    # Points along each edge of the diagram, shared by the two cells it parts.
    edge_points = {}

    def edge(t0, t1, detailed):
        key = (min(t0, t1), max(t0, t1))
        if key not in edge_points:
            a, b = lattice.corners[key[0]], lattice.corners[key[1]]
            length = a.angle(b) * SCALE * scale
            count = max(1, int(round(length / (SPACING if detailed else 2 * SPACING))))
            edge_points[key] = slerp_points(a, b, count)
        pts = edge_points[key]
        return pts if key[0] == t0 else pts[::-1]

    verts, faces, face_keys = [], [], []

    def place(d, t, i):
        depth = lattice.height(t, i) * smoothstep(0.0, 0.4, facing(d))
        p = Vector((d.x * RADII.x, d.y * RADII.y, d.z * RADII.z)) - base_normal(d) * depth
        verts.append(p * scale + CENTRE)
        return len(verts) - 1

    for i in range(len(lattice.seeds)):
        sd, e1, e2, edges, centre, r_in = lattice.plane(i)
        ring = lattice.cells[i]
        detailed = fine[i] or any(fine[j] for j in lattice.neighbours[i])
        boundary = []
        for a, b in zip(ring, ring[1:] + ring[:1]):
            boundary += edge(a, b, detailed)[:-1]
        # The hole's middle: the incentre, as deep as the cell allows (t_mid).
        t_mid = r_in - lattice.half[i]
        levels = [(level, key) for level, key in (RINGS if fine[i] else RINGS_BACK) if level < t_mid - 0.1]
        shapes = [lattice.contour(edges, r_in, i, level) for level, _ in levels]
        keep = [n for n, shape in enumerate(shapes) if shape is not None]
        levels, shapes = [levels[n] for n in keep], [shapes[n] for n in keep]
        rows = []
        for b in boundary:
            pb = lattice.project(b, sd, e1, e2)
            direction = (pb - centre).normalized()
            r_b = (pb - centre).length
            row = [place(b, -9.0, i)]
            last = r_b
            for (level, _), shape in zip(levels, shapes):
                r = min(lattice.reach(shape, centre, direction, r_b), last)
                row.append(place(lattice.unproject(centre + direction * r, sd, e1, e2), level, i))
                last = r
            rows.append(row)
        middle = place(lattice.unproject(centre, sd, e1, e2), t_mid, i)
        bands = ["strand"] + [key for _, key in levels]
        n = len(rows)
        for m in range(n):
            r0, r1 = rows[m], rows[(m + 1) % n]
            for r in range(len(r0) - 1):
                faces.append((r0[r], r1[r], r1[r + 1], r0[r + 1]))
                face_keys.append(bands[r])
            faces.append((r0[-1], r1[-1], middle))
            face_keys.append(bands[-1])

    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata([tuple(v) for v in verts], [], faces)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    for key in keys:
        obj.data.materials.append(mats[key])
    for poly, key in zip(mesh.polygons, face_keys):
        poly.material_index = keys.index(key)
    # Shared and collapsed points merged, the slivers left by collapsed rings dissolved.
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-4)
    # The outline: cut along where the shell turns from the camera, painted darker beyond.
    split_along(bm, {v: facing(direction_of(v.co, scale)) for v in bm.verts}, EDGE)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    for f in bm.faces:
        if facing(direction_of(f.calc_center_median(), scale)) < EDGE:
            hole = keys[f.material_index] != "strand"
            f.material_index = keys.index("edge_hole" if hole else "edge_strand")
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    # Unused materials dropped (pop moves the faces' indices above the slot down itself).
    used = {p.material_index for p in mesh.polygons}
    for index in reversed(range(len(mesh.materials))):
        if index not in used:
            mesh.materials.pop(index=index)
    return k.smooth(obj, 80)


def materials(ramp):
    out = {}
    for key, (shade, roughness) in SHADES.items():
        out[key] = k.material(f"cells_{key}", palette=16 * ramp + shade, metallic=0.1, roughness=roughness)
    return out


def triangles():
    depsgraph = bpy.context.evaluated_depsgraph_get()
    total = 0
    for obj in bpy.context.scene.objects:
        if obj.type == "MESH":
            evaluated = obj.evaluated_get(depsgraph)
            mesh = evaluated.to_mesh()
            mesh.calc_loop_triangles()
            total += len(mesh.loop_triangles)
            evaluated.to_mesh_clear()
    return total


def build():
    options = k.args()
    outdir = options.get("outdir", os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "enemies"))
    only = set(options["only"].split(",")) if "only" in options else None
    ramp = int(options["ramp"]) if "ramp" in options else None
    lattice = Lattice()
    print("holes: %d (%d seen), sizes %.1f-%.1f px" % (len(lattice.seeds), len(FRONT), min(lattice.size),
                                                      max(lattice.size)))
    for name, sprite, scale in FRAMES:
        if only is not None and name not in only:
            continue
        k.reset()
        mats = materials(ramp if ramp is not None else RAMP)
        shell(name, lattice, mats, scale)
        used = {m.name for obj in bpy.context.scene.objects if obj.type == "MESH" for m in obj.data.materials}
        print("== %s (%s): %d triangles, %d materials: %s" % (name, sprite, triangles(), len(used),
                                                               ", ".join(sorted(used))))
        if "check" in options:
            for spec in CHECKS.get(name, [sprite]):
                sheet, index = spec.split(":")
                k.check_silhouette(os.path.join(options["check"], "enemy_%s.png" % sheet), int(index))
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        path = os.path.join(outdir, name + ("_r%d" % ramp if ramp is not None else "") + ".glb")
        k.export(path)
        print("%s: %d bytes" % (path, os.path.getsize(path)))
        if "preview" in options:
            k.preview(options["preview"] + name)


if __name__ == "__main__":
    build()
