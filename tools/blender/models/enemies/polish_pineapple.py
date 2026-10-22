"""FRUIT's pineapple boss (sheet ', written x27 in models.cfg: 31 2x2 sprites, enemies 1265-1295 of episode 5, on the
ground), polished (2026-10-22, round 35; it replaces wave3_ae_boss.py, a relief painted pixel by pixel).

Where it appears: FRUIT's fight (tools/content/tyrevents.py 5 FRUIT, all with link 254 and the boss bar): t 5000, events
6 (ground) 1282-1287 (' 231-241) at (84 + 24 i, y - 56), 1289-1293 (' 270-278) at (96 + 24 i, y - 28), 1294 1295 (' 281
283) at (132, y), (156, y), events 10 (ground 2, also drawn as ground enemies) 1273-1280 (' 191-205) at (60 + 24 i,
y - 84), 1281 (' 229) at (60, y - 56), 1288 (' 243) at (228, y - 56); t 5028 (28 ticks of scroll later: on top of
them) 1265-1272 (' 153-167) at (60 + 24 i, y - 84): one 192 x 140 picture, four rows of eight, five 36 pixels in, two 72
pixels in. Episode 6's THE CORE takes FRUIT's boss waves (its placement "boss", episode 5, FRUIT, at 5600). Each piece
is an enemy of its own (armour 254, 229 and 243 armour 0: never hit), one frame, no damaged look (dgr 0), not animated;
155 and 165 carry gun 45, 274 gun 30, 270 and 278 (the barrels) launch enemy 1244 (' 207 245, a pale green flame) when
event 31 sets their launch frequency. No other enemy (launched ones included) shows these sprites, none is another
sprite's pixels mirrored, turned or in other ramps; the picture is its own mirror image about its middle (coverage 97 %,
shading too but for the window's figure): built symmetric, the figure on its own.

As the sprites and their 4x upscales draw it (columns and rows of the 192 x 140 picture): a giant pineapple lying down
the screen (columns 61-130, rows 0-102: a blunt end just over the picture's top, its narrow end at row 102) in a lattice
of diamond scales about 8 pixels across (browns of ramps 1 and 11, darker creases, pale specks), a tall black glass
window down its front (columns 85-107 of rows 27-79) with a pale glowing figure in it (a blob at columns 91-98 of rows
42-52, a thin stem down to a bigger blob at columns 94-102 of rows 61-71, a dim halo round it); its green crown
fanning out under it like a fir branch (rows 94-137: a dense middle, short leaves out to the left, longer ones to the
right); behind it a broad grey wing plate (rows 3-90: its top edge at row 3, its sides at columns 0 and 191, its lower
edges one straight bevel each from row 55 at the side to under the pineapple, lit), panel seams (columns 27 and 22, row
31), a lemon slice glowing in a round dark socket on each side (columns 16-32 of rows 20-36 and the mirror image); at
each side a tan pylon on the plate (columns 40-55 of rows 26-81) narrowing into a rod pointing down the screen (columns
47-52 of rows 82-98), three ribbed steel bolts (rows 26-33, 50-57, 74-81: five four-pixel beads each, columns 51-70)
from the pylon over the pineapple's flank, a yellow banana claw between each two (columns 55-64 of rows 33-49 and
57-73), and a big claw under each side (columns 66-78 of rows 88-106).

Built as such a machine, modelled in the picture's plane (x, y as the sprites draw them, z up) and then sheared along
the game camera's line of sight (y - z tan 20, the normals with it: polish_lemon_beetle's shear_to_camera), so that
the camera sees every point where the sprites draw it, however high it stands (the pineapple rises 31 pixels):
- the plate: a constrained Delaunay mesh of each half's outline (its inner edge 4 pixels inside the pineapple's), of
  the chamfer's inner line and of the seams' edges and bottoms, with a coarse lattice between them, its heights exact
  along those lines (a chamfer 1.7 wide and 1.3 deep round its edge, seams 0.9 wide and 0.55 deep), walls and a flat
  underside; painted grey 0x08, the chamfers by the light they get, the bevelled lower edges lit (0x0b) as the
  sprites draw them, the seams' walls lit or shaded;
- the lamps: polish_lemon_beetle's lemon slice (scaled to the sprite's 17 pixels) in a rolled steel socket ring,
  glowing more than the beetle's eyes (0.2-0.56);
- the pylons: lofted rounded boxes (superellipse sections, power 5) with a rounded upper end, narrowing into the
  barrel, its muzzle rounded round a dark bore; the bolts lathed along axes rising from inside the pylon into the
  pineapple's flank (z 10 to 20.6: they lie over the flank as the sprites draw them and screw into it), five beads
  each where the sprites' ribs are, a flange where each leaves the pylon; the claws lens-sectioned lofts along the
  sprites' crescents (ramp 7's yellows glowing a little, as the lemon beetle's), the small ones bridging the bolts
  over the flank, the big ones running from inside the flank along it to points by the crown;
- the pineapple: rings of a smooth fruit round its axis (its outline R(y): two superellipse arcs fitted to the sprites'
  (rms 0.35 px); height 0.75 times its half-width over an axis 4 up), about 2 pixels apart along its surface, cut
  along the scales' creases (the lattice (s +- y) / 8.4, s the arc round it) and along the window's outline and the
  halo round the figure (polish_coral_manta.split_contour: mesh lines), each scale raised 0.4 in its middle, the scales
  fading out at the fruit's tips; painted in four browns by the creases and the light (band_split: contours along the
  cushions), its flat bottom at z 0; inside the window's outline the skin stays smooth and is painted as the window's
  floor (0x01, lighter round the figure: 0x04, 0x07, glowing a little); over it the smoky glass (0x02, alpha 0.3) bulging
  up to 2.9 over the skin, a dark rolled rim round it, and between them the figure, a flattened loft along the sprites'
  S of light glowing white (0x0f at 0.6, its edges 0x0b at 0.4);
- the crown: a stem out of the fruit's narrow end and 17 lens-sectioned leaves along quadratic curves to where the
  sprites' leaves end, the middle ones rising along the stem (z up to 12.5), painted in four greens by the light.
Each part's faces are painted by how they face the game's sun (light_value, polish_fruit_pods.py's). The whole is cut
into the 31 pieces in the picture's plane along the sprites' edges (polish_coral_manta.cut: the caps the part's inside
colour, the fruit's flesh 0x7b; the boxes of the picture's edge pieces reach out past it, so the fruit's blunt end
stays whole), before the shear; each piece moved so that its sprite's middle is its origin, its parts joined, every
mesh triangulated (polish_k_pod.triangulate). Deterministic (md5 identical over runs, with and without --check): no
random numbers, no booleans.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up. The whole's origin is the picture's
middle (its pixel edge 96, 70): column c's left edge is x = c - 96, row r's top edge y = 70 - r; a piece whose sprite's
top left pixel is (c0, r0) has its origin at (c0 + 12 - 96, 56 - r0). Heights in the picture's plane: the plate 0-5,
the pylons 4.6-17.5, the bolts' tops to 24, the pineapple to 30.9, the glass to 33.8, the crown 1-12.5; drawn at the
pieces' origins on the ground layer (models.cfg origin: 4 over the terrain; FRUIT's fight is over open space).

models.cfg: the model lines stay (model pineapple_<sprite> enemies/pineapple_<sprite>.glb origin); the sprite lines get
glows for the lamps and the figure: sprite x27 155 pineapple_155 yaw=0 glow=22:0.22:125:-11.5:14.5, sprite x27 165
pineapple_165 yaw=0 glow=22:0.22:125:11.5:14.5, sprite x27 199 pineapple_199 yaw=0 glow=24:0.18:14:-11.5:14.5.

Replaces wave3_ae_boss.py (all of it: the boss is all it builds; nothing imports it) and wave3_ae_art.py's BOSS (read
only by it through wave3_ae_kit.frame()).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the whole's silhouette as the
camera sees it, and each piece's, against enemy_x27.png), --preview <prefix> (the whole's top and 3/4 views; --pieces 1
also each piece's), --only <name,...> (pieces to export; "none": none), --whole <file.glb> (the sheared whole as well,
for looking at), --stats 1 (each piece's largest parts).
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector, geometry

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_deli_boss import join, drop_unused  # noqa: E402
from polish_coral_manta import cut, split_contour  # noqa: E402
from polish_orb_red import band_split  # noqa: E402
from polish_torm_beetle import tube  # noqa: E402
from polish_lemon_beetle import slice_obj, SLICE_C, SLICE_Z  # noqa: E402

VIEW_TILT = 20.0                  # the game's camera: this far off straight down, from the bottom of the screen
TAN_T = math.tan(math.radians(VIEW_TILT))
LIGHT = Vector((-0.6, 0.6, 1.0)).normalized()   # towards the game's sun (render_gpu.c: from above and the top left)
FLAT = LIGHT.z
W, H = 192, 140                   # the whole picture; its origin is its middle, the pixel edge (96, 70)


def px(c, r):
    """A pixel edge (column c, row r) of the whole picture in the picture's plane."""
    return (c - 96.0, 70.0 - r)


def light_value(n, base, a=3.2, b=1.2):
    """How much light a face facing n gets, on the scale of a flat face's `base` (polish_fruit_pods.py's)."""
    return base + a * (n.dot(LIGHT) - FLAT) + b * (n.z - 1.0)


def pick_band(value, bands):
    key = bands[0][1]
    for lowest, k_ in bands:
        if value >= lowest:
            key = k_
    return key


def smoothstep(e0, e1, x):
    t = min(1.0, max(0.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


# --- Materials ------------------------------------------------------------------------------------------------------
# (key, palette index, metallic, roughness, emission strength in its own colour, alpha)
MATS = [
    # the wing plate, the bolts, the window's rim: steel greys
    ("g3", 0x03, 0.35, 0.4, 0.0, None), ("g5", 0x05, 0.35, 0.38, 0.0, None), ("g8", 0x08, 0.35, 0.34, 0.0, None),
    ("gb", 0x0b, 0.35, 0.3, 0.0, None),
    # the lamps' sockets
    ("sock", 0x04, 0.55, 0.3, 0.0, None),
    # the lemon slices (polish_lemon_beetle.slice_obj's keys; glowing more than the lemon beetle's eyes: they are lamps)
    ("rind", 0x7c, 0.1, 0.22, 0.2, None), ("pith", 0x7e, 0.0, 0.5, 0.24, None), ("membrane", 0x7f, 0.0, 0.3, 0.34, None),
    ("juice", 0x7d, 0.0, 0.12, 0.46, None), ("crest", 0x7e, 0.0, 0.1, 0.56, None), ("core", 0x7f, 0.0, 0.2, 0.42, None),
    # the pylons and their barrels: tan
    ("t5", 0x15, 0.3, 0.42, 0.0, None), ("t7", 0x17, 0.3, 0.4, 0.0, None), ("t9", 0x19, 0.3, 0.38, 0.0, None),
    ("bore", 0x10, 0.2, 0.6, 0.0, None),
    # the banana claws (ramp 7's yellows, glowing a little in their own colour as the lemon beetle's); 0x7b is also the
    # pineapple's flesh where the pieces are cut
    ("yb", 0x7b, 0.15, 0.3, 0.09, None), ("yc", 0x7c, 0.15, 0.28, 0.11, None), ("yd", 0x7d, 0.15, 0.26, 0.13, None),
    # the pineapple's skin
    ("s0", 0xb2, 0.0, 0.6, 0.0, None), ("s3", 0xb5, 0.0, 0.5, 0.0, None), ("s5", 0xb7, 0.0, 0.46, 0.0, None),
    ("s7", 0xb9, 0.0, 0.42, 0.0, None),
    # the window: its dark floor (lighter round the figure), the glowing figure, the smoky glass
    ("cav", 0x01, 0.1, 0.6, 0.0, None), ("cav2", 0x04, 0.1, 0.6, 0.12, None), ("cav4", 0x07, 0.1, 0.6, 0.22, None),
    ("fig", 0x0f, 0.0, 0.2, 0.6, None), ("fig_edge", 0x0b, 0.0, 0.25, 0.4, None),
    ("glass", 0x02, 0.3, 0.05, 0.0, 0.3),
    # the crown
    ("c2", 0x22, 0.0, 0.75, 0.06, None), ("c4", 0x24, 0.0, 0.7, 0.08, None), ("c6", 0x26, 0.0, 0.65, 0.1, None),
    ("c8", 0x28, 0.0, 0.6, 0.12, None),
]


def materials():
    pal = k.level_palette()
    m = {}
    for key, index, metallic, roughness, glow, alpha in MATS:
        extra = dict(emission=pal[index], emission_strength=glow) if glow > 0 else {}
        if alpha is not None:
            extra["alpha"] = alpha
        m[key] = k.material(f"pine_{key}", palette=index, metallic=metallic, roughness=roughness, **extra)
    return m


def paint_light(obj, m, bands, base, a=3.2, b=1.2, extra=None):
    """band_split by how the vertices face the game's sun and up (light_value), plus extra(co) if given."""
    mesh = obj.data
    values = []
    for v in mesh.vertices:
        val = light_value(Vector(v.normal), base, a, b)
        if extra is not None:
            val += extra(v.co)
        values.append(val)
    band_split(obj, values, [(lo, m[key]) for lo, key in bands])
    return obj


def mesh_from_bm(name, bm, mats, keys):
    """An object from a bmesh whose faces have keys (one per face, in bm.faces' order) naming their materials."""
    mesh = bpy.data.meshes.new(name)
    slots = []
    for key in keys:
        if key not in slots:
            slots.append(key)
    for f, key in zip(bm.faces, keys):
        f.material_index = slots.index(key)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    for key in slots:
        mesh.materials.append(mats[key])
    return obj


def mirror_obj(obj, name):
    """A copy of obj mirrored about x = 0 (its faces turned back out, its custom normals mirrored)."""
    copy = obj.copy()
    copy.data = obj.data.copy()
    copy.name = name
    copy.data.name = name
    bpy.context.scene.collection.objects.link(copy)
    mesh = copy.data
    had_custom = mesh.has_custom_normals
    normals = [Vector(cn.vector) for cn in mesh.corner_normals]
    mesh.transform(Matrix.Scale(-1.0, 4, (1.0, 0.0, 0.0)))
    mesh.flip_normals()
    if had_custom:
        # flip_normals reverses each face's corners: the corner normals follow in the same order
        out = []
        for poly in mesh.polygons:
            start, n = poly.loop_start, poly.loop_total
            src = [normals[start + i] for i in range(n)]
            src = [src[0]] + src[1:][::-1]
            out += [Vector((-v.x, v.y, v.z)) for v in src]
        mesh.normals_split_custom_set([tuple(v) for v in out])
    mesh.update()
    return copy


def section_loft(name, stations, mat, segments=16):
    """A hull through stations (x, y, z, half-width, half-height, power) as given (no smoothing in between):
    superellipse sections lying flat (their width level), closed to points just beyond its first and last stations."""
    pts = [Vector(s_[:3]) for s_ in stations]
    rings = []
    for i, st in enumerate(stations):
        t = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        side = t.cross(Vector((0.0, 0.0, 1.0)))
        side = side.normalized() if side.length > 1e-6 else Vector((1.0, 0.0, 0.0))
        up = side.cross(t).normalized()
        hw, hh, pw = st[3], st[4], st[5]
        ring = []
        for j in range(segments):
            a = 2 * math.pi * j / segments
            c, s_ = math.cos(a), math.sin(a)
            ring.append(pts[i] + side * (math.copysign(abs(c) ** (2 / pw), c) * hw) +
                        up * (math.copysign(abs(s_) ** (2 / pw), s_) * hh))
        rings.append(ring)
    first = pts[0] - (pts[1] - pts[0]).normalized() * 0.05
    last = pts[-1] + (pts[-1] - pts[-2]).normalized() * 0.05
    return k.loft(name, rings, mat, start_point=first, end_point=last)


def flat_bottom(obj, mat, z=0.0):
    """Cuts away what lies below z, closing the cut with a flat cap of mat."""
    index = mk.slot_of(obj, mat)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    result = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-6, plane_co=(0, 0, z),
                                    plane_no=(0, 0, 1), clear_inner=True)
    edges = [e for e in result["geom_cut"] if isinstance(e, bmesh.types.BMEdge) and e.is_valid and
             len(e.link_faces) == 1]
    if edges:
        filled = bmesh.ops.holes_fill(bm, edges=edges, sides=0)
        for f in bmesh.ops.triangulate(bm, faces=filled["faces"])["faces"]:
            f.material_index = index
            f.normal_update()
            if f.normal.z > 0:
                f.normal_flip()
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    return obj


# --- The pineapple's outline and surface ----------------------------------------------------------------------------
# Its half-width R(y) in the picture's plane: two superellipse arcs fitted to the sprites' outline (columns 61-130 at
# rows 24-25, 62-129 at rows 58-73, 81-110 at row 0, 84-107 at row 101): widest A at YC, closing at YC + BT (just over
# the picture's top edge) and YC - BB (where the crown comes out).
A, YC, BT, BB, PT, PB = 35.9, 27.0, 43.9, 59.7, 2.79, 2.58
Y_TOP, Y_END = YC + BT, YC - BB
Z0, ZS = 4.0, 0.75                # its axis' height and its height over its half-width (a lying, slightly flat fruit)


def R(y):
    if y >= YC:
        t, p = (y - YC) / BT, PT
    else:
        t, p = (YC - y) / BB, PB
    t = min(1.0, max(0.0, t))
    return A * max(0.0, 1.0 - t ** p) ** (1.0 / p)


def skin_z(x, y):
    """The smooth skin's height over (x, y) (None outside the outline)."""
    r = R(y)
    if abs(x) >= r:
        return None
    return Z0 + ZS * math.sqrt(r * r - x * x)


# --- The wing plate -------------------------------------------------------------------------------------------------
PLATE_Z = 5.0                     # its top
CH, CH_DROP = 1.7, 1.3            # the chamfer round its edge: width, drop
SEAM_W, SEAM_D = 0.9, 0.55        # the panel seams: width, depth
INSET = 4.0                       # its inner edge runs this far inside the pineapple's outline (hidden)
LAMP = (-71.5, 41.5)              # the left lamp's middle (columns 16-32 of rows 20-36: the sprite's lemon)
LAMP_R = 8.5                      # the slice's radius
SOCKET = (8.6, 10.6, 0.9)         # the socket ring round it: inner, outer radius, height over the plate


def diag_y(x):
    """The plate's bevelled lower edge: one straight line from (column 0, row 55) under the pylon to the pineapple
    (row 82 at column 55, row 89 at column 69)."""
    return 15.0 - 0.5 * (x + 96.0)


def plate_outline():
    """The left half's outline (counter-clockwise): the top edge (row 3), the left edge (column 0), the bevelled
    lower edge, then up along the pineapple INSET inside its outline."""
    # where the lower edge meets the inner edge
    lo, hi = -40.0, -10.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if -(R(diag_y(mid)) - INSET) < mid:
            hi = mid
        else:
            lo = mid
    x_meet = (lo + hi) / 2
    y_meet = diag_y(x_meet)
    pts = []
    x_top = -(R(67.0) - INSET)
    pts.append((x_top, 67.0))
    pts += [(-94.6, 67.0), (-96.0, 65.6), (-96.0, 16.0), (-95.2, 15.0 - 0.4)]
    pts.append((x_meet, y_meet))
    n = 40
    for i in range(1, n):
        y = y_meet + (67.0 - y_meet) * i / n
        pts.append((-(R(y) - INSET), y))
    return pts


def resample_loop(points, step):
    out = []
    n = len(points)
    for i in range(n):
        a, b = Vector(points[i]), Vector(points[(i + 1) % n])
        count = max(1, int(math.ceil((b - a).length / step)))
        for j in range(count):
            out.append(a.lerp(b, j / count))
    return out


def resample_line(points, step):
    out = []
    for i in range(len(points) - 1):
        a, b = Vector(points[i]), Vector(points[i + 1])
        count = max(1, int(math.ceil((b - a).length / step)))
        for j in range(count):
            out.append(a.lerp(b, j / count))
    out.append(Vector(points[-1]))
    return out


def inside_poly(p, poly):
    x, y = p
    inside = False
    n = len(poly)
    for i in range(n):
        x0, y0 = poly[i]
        x1, y1 = poly[(i + 1) % n]
        if (y0 > y) != (y1 > y):
            xc = x0 + (y - y0) * (x1 - x0) / (y1 - y0)
            if xc > x:
                inside = not inside
    return inside


def seg_distance(p, a, b):
    ab = b - a
    t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-12)))
    return (a + ab * t - p).length


def seams():
    """The panel seams (polylines in the picture's plane): from the top border down to the lamp's socket (column 27),
    from the socket down to the lower edge (column 22), from the left border to the socket (row 31)."""
    lx, ly = LAMP
    r = SOCKET[1] + 0.6
    top = 67.0 - CH - 0.6
    left = -96.0 + CH + 0.6
    xa, xb = -68.5, -73.5
    ya = ly + math.sqrt(r * r - (xa - lx) ** 2)
    yb = ly - math.sqrt(r * r - (xb - lx) ** 2)
    yc = 38.5
    xc = lx - math.sqrt(r * r - (yc - ly) ** 2)
    # the lower seam stops before the chamfer of the bevelled edge (whose inner line lies CH in from it)
    yb_end = diag_y(xb) + CH / math.cos(math.atan(0.5)) + 0.6
    return [[(xa, top), (xa, ya)], [(xb, yb), (xb, yb_end)], [(left, yc), (xc, yc)]]


def plate_half(m):
    """The left half of the wing plate: a constrained Delaunay mesh of its outline, the chamfer's inner line, the
    seams' edges and bottoms and a coarse lattice between them, its heights set per vertex (the chamfer and the seams
    exact along the mesh's lines); straight walls down to z 0 and a flat underside."""
    outline = plate_outline()
    loop = resample_loop(outline, 0.8)
    n = len(loop)
    # the chamfer's inner line: each outline point moved in along its normal
    inner = []
    for i in range(n):
        t = (loop[(i + 1) % n] - loop[i - 1]).normalized()
        nrm = Vector((-t.y, t.x))
        inner.append(loop[i] + nrm * CH)
    pts, kinds, edges = [], [], []

    def add_chain(chain, kind, closed):
        start = len(pts)
        for p in chain:
            pts.append(Vector((p[0], p[1])))
            kinds.append(kind)
        count = len(chain)
        for i in range(count - (0 if closed else 1)):
            edges.append((start + i, start + (i + 1) % count))
    add_chain(loop, "edge", True)
    add_chain(inner, "flat", True)
    seam_lines = seams()
    for s in seam_lines:
        a, b = Vector(s[0]), Vector(s[1])
        d = (b - a).normalized()
        side = Vector((-d.y, d.x)) * (SEAM_W / 2)
        add_chain(resample_line([a, b], 1.2), "seam", False)
        add_chain(resample_line([a + side, b + side], 1.2), "flat", False)
        add_chain(resample_line([a - side, b - side], 1.2), "flat", False)
    # the coarse lattice between them
    step = 3.2
    xs = [p.x for p in loop]
    ys = [p.y for p in loop]
    j = 0
    y = min(ys) + 0.5
    inner_poly = [(p.x, p.y) for p in inner]
    seg_list = [(Vector(s[0]), Vector(s[1])) for s in seam_lines]
    while y < max(ys):
        x = min(xs) + (step / 2 if j % 2 else 0.0)
        while x < max(xs):
            p = Vector((x, y))
            if inside_poly((x, y), inner_poly) and all(seg_distance(p, a, b) > SEAM_W / 2 + 0.9 for a, b in seg_list):
                # away from the chamfer's inner line too
                if min((p - q).length for q in inner[::3]) > 1.2:
                    pts.append(p)
                    kinds.append("flat")
            x += step
        y += step * math.sqrt(3) / 2
        j += 1
    verts, _e, faces, orig, *_ = geometry.delaunay_2d_cdt(pts, edges, [], 0, 1e-5)
    poly = [(p.x, p.y) for p in loop]
    bm = bmesh.new()
    bverts = []
    for i, v in enumerate(verts):
        kind = kinds[orig[i][0]] if orig[i] else "flat"
        z = PLATE_Z - (CH_DROP if kind == "edge" else (SEAM_D if kind == "seam" else 0.0))
        bverts.append(bm.verts.new((v.x, v.y, z)))
    for f in faces:
        if len(f) != 3:
            continue
        cx = sum(verts[i].x for i in f) / 3
        cy = sum(verts[i].y for i in f) / 3
        if not inside_poly((cx, cy), poly):
            continue
        try:
            bm.faces.new([bverts[i] for i in f])
        except ValueError:
            pass
    for v in [v for v in bm.verts if not v.link_faces]:
        bm.verts.remove(v)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    for f in bm.faces:
        if f.normal.z < 0:
            f.normal_flip()
    tops = list(bm.faces)
    # the walls along the outline, the underside
    rim = [e for e in bm.edges if len(e.link_faces) == 1]
    lower = {}
    for e in rim:
        for v in e.verts:
            if v not in lower:
                lower[v] = bm.verts.new((v.co.x, v.co.y, 0.0))
    for e in rim:
        a, b = e.verts
        f = e.link_faces[0]
        # keep the wall's winding consistent with the top face's
        loop_ = [l for l in f.loops if l.edge == e][0]
        if loop_.vert == a:
            bm.faces.new([b, a, lower[a], lower[b]])
        else:
            bm.faces.new([a, b, lower[b], lower[a]])
    ring = list(lower.values())
    index = {v: i for i, v in enumerate(ring)}
    under, _e2, under_faces, under_orig, *_ = geometry.delaunay_2d_cdt(
        [Vector((v.co.x, v.co.y)) for v in ring],
        [(index[lower[e.verts[0]]], index[lower[e.verts[1]]]) for e in rim], [], 0, 1e-6)
    for f in under_faces:
        if len(f) != 3 or not all(under_orig[i] for i in f):
            continue
        cx = sum(under[i].x for i in f) / 3
        cy = sum(under[i].y for i in f) / 3
        if inside_poly((cx, cy), poly):
            try:
                bm.faces.new([ring[under_orig[i][0]] for i in reversed(f)])
            except ValueError:
                pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.normal_update()
    keys = [plate_paint(f) for f in bm.faces]
    obj = mesh_from_bm("plate_l", bm, m, keys)
    k.smooth(obj, 30)
    return obj


def plate_paint(f):
    """A face of the plate by where it lies: the chamfers by the light they get (the bevelled lower edge lit, as the
    sprites draw it), the seams' walls dark or lit, the top in the sprites' grey."""
    c = f.calc_center_median()
    n = f.normal
    if n.z < 0.2:
        return "g3"                                     # walls and underside
    if n.z < 0.985:
        if min_seam_distance(c) < SEAM_W / 2 + 0.05:
            return "gb" if (n.x * LIGHT.x + n.y * LIGHT.y) > 0 else "g3"   # a seam's lit or shaded wall
        if n.y < -0.25 and n.x < 0.1:
            return "gb"                                 # the bevelled lower edge, lit
        return pick_band(light_value(n, 6.6), [(-99, "g5"), (6.2, "g8"), (7.0, "gb")])
    return "g8"


def min_seam_distance(c):
    p = Vector((c.x, c.y))
    return min(seg_distance(p, Vector(s[0]), Vector(s[1])) for s in seams())


# --- The lamps ------------------------------------------------------------------------------------------------------

def lamp(m, side):
    """A lemon slice in a socket ring on the plate (polish_lemon_beetle.slice_obj, scaled to the sprite's 17 pixels
    across)."""
    lx, ly = LAMP
    lx *= -side
    parts = []
    # the socket: a rolled ring standing on the plate, its inside dropping to the slice
    ri, ro, h = SOCKET
    prof = [(ro + 0.4, PLATE_Z - 0.4), (ro, PLATE_Z + h * 0.55), (ro - 0.35, PLATE_Z + h), ((ri + ro) / 2, PLATE_Z + h + 0.15),
            (ri + 0.25, PLATE_Z + h * 0.8), (ri, PLATE_Z + 0.1), (ri - 0.4, PLATE_Z - 0.3)]
    sock = mk.lathe(f"socket{side:+d}", prof, (lx, ly), m["sock"], segments=56)
    k.recalc_normals(sock)
    k.smooth(sock, 50)
    paint_light(sock, m, [(-99, "g3"), (4.6, "sock"), (6.4, "g8"), (7.4, "gb")], 5.6)
    parts.append(sock)
    # the slice
    sl = slice_obj(f"lamp{side:+d}", -1, m)
    s = LAMP_R / 7.45
    cx, cy = -SLICE_C[0], SLICE_C[1]
    sl.data.transform(Matrix.Translation((lx, ly, PLATE_Z + 0.55)) @ Matrix.Diagonal((s, s, 1.0, 1.0)) @
                      Matrix.Translation((-cx, -cy, -SLICE_Z)))
    sl.data.update()
    parts.append(sl)
    return parts


# --- The pylons, their barrels, the bolts and the claws -------------------------------------------------------------
PYLON_X = -48.0                   # its middle (columns 40-55)
PYLON_HW = 8.1
PYLON_Z = (PLATE_Z - 0.4, 17.5)   # its underside (sunk into the plate) and top
BARREL_X, BARREL_Z, BARREL_R = -46.0, 11.0, 3.0   # the rod under it (columns 47-52 of rows 82-98)
BOLT_Y = [40.0, 16.0, -8.0]       # the bolts' axes (rows 26-33, 50-57, 74-81)
BOLT_FROM, BOLT_TO = (-47.0, 10.0), (-25.6, 20.6)   # (x, z) where each bolt's axis starts (in the pylon) and ends
BOLT_R = 3.35                     # between its beads
BEAD = 0.7                        # the beads' height over that
BEAD_X = [-45.0, -41.0, -37.0, -33.0, -29.0, -25.0]   # the beads' edges in the picture (columns 51, 55 ... 71)


def pylon(m, side):
    """The pylon: a long tan block on the plate (a superellipse section, its upper end rounded, its lower end
    narrowing into the barrel), the barrel a rod with a rounded muzzle and a dark bore."""
    hz = (PYLON_Z[1] - PYLON_Z[0]) / 2
    zc = PYLON_Z[0] + hz
    x0 = PYLON_X
    st = []
    # the upper end (row 26), rounded
    for y, f in ((44.8, 0.12), (44.55, 0.5), (44.1, 0.72), (43.4, 0.87), (42.4, 0.96), (41.0, 1.0)):
        st.append((x0, y, zc - hz * (1 - f) * 0.3, PYLON_HW * f, hz * f, 2.0 + 3.0 * f))
    st += [(x0, 20.0, zc, PYLON_HW, hz, 5.0), (x0, -3.0, zc, PYLON_HW, hz, 5.0)]
    # the lower end narrowing (rows 74-81: its outer edge from column 41 to 45)
    st += [(x0 + 0.5, -6.0, zc - 0.3, PYLON_HW - 0.8, hz - 0.4, 4.0), (x0 + 1.2, -8.8, zc - 0.9, 6.0, hz - 1.5, 3.0),
           (BARREL_X - 0.3, -11.2, BARREL_Z + 0.1, BARREL_R + 1.4, BARREL_R + 1.3, 2.2),
           (BARREL_X, -12.6, BARREL_Z, BARREL_R + 0.25, BARREL_R + 0.25, 2.0)]
    # the barrel (rows 82-98), its muzzle rounded
    st += [(BARREL_X, -14.0, BARREL_Z, BARREL_R, BARREL_R, 2.0), (BARREL_X, -26.0, BARREL_Z, BARREL_R, BARREL_R, 2.0),
           (BARREL_X, -27.3, BARREL_Z, BARREL_R - 0.25, BARREL_R - 0.25, 2.0),
           (BARREL_X, -27.95, BARREL_Z, BARREL_R - 0.85, BARREL_R - 0.85, 2.0),
           (BARREL_X, -28.2, BARREL_Z, 1.25, 1.25, 2.0), (BARREL_X, -28.3, BARREL_Z, 0.06, 0.06, 2.0)]
    if side > 0:
        st = [(-s_[0],) + tuple(s_[1:]) for s_ in st]
    obj = section_loft(f"pylon{side:+d}", st, m["t7"], segments=36)
    k.smooth(obj, 60)
    paint_light(obj, m, [(-99, "t5"), (5.6, "t7"), (6.6, "t9")], 6.5)
    bx = BARREL_X * side
    mk.paint(obj, lambda c, n: m["bore"] if c.y < -28.0 and math.hypot(c.x - bx, c.z - BARREL_Z) < 1.6 else None)
    return [obj]


def bolt(m, side, y):
    """A ribbed steel bolt from the pylon into the pineapple's flank: five beads (the sprite's four-pixel ribs), its
    end rounded, a flange where it leaves the pylon."""
    sx = -side                                   # the constants are the left one's
    (xa, za), (xb, zb) = BOLT_FROM, BOLT_TO
    a, b = Vector((xa * sx, y, za)), Vector((xb * sx, y, zb))
    axis = b - a
    length = axis.length
    d = axis.normalized()

    def t_at(x):
        """How far along the axis the picture's column edge x (the left bolt's) lies."""
        return (x - xa) / (xb - xa) * length
    edges = [t_at(x) for x in BEAD_X]
    prof = [(0.0, 0.01), (0.05, BOLT_R)]
    for t0, t1 in zip(edges, edges[1:]):
        for i in range(1, 4):
            u = i / 4
            prof.append((t0 + (t1 - t0) * u, BOLT_R + BEAD * math.sin(math.pi * u) ** 0.8))
        prof.append((t1, BOLT_R))
    tail = edges[-1]
    for i in range(1, 5):
        u = i / 4
        prof.append((tail + 1.6 * math.sin(u * math.pi / 2), BOLT_R * math.cos(u * math.pi / 2) + 0.01))
    seg = 11
    rings = [[Vector((r * math.cos(2 * math.pi * j / seg), r * math.sin(2 * math.pi * j / seg), t)) for j in range(seg)]
             for t, r in prof[1:-1]]
    obj = k.loft(f"bolt{side:+d}_{y:.0f}", rings, m["g8"], start_point=(0, 0, prof[0][0]),
                 end_point=(0, 0, prof[-1][0]))
    rot = Vector((0, 0, 1)).rotation_difference(d).to_matrix().to_4x4()
    obj.data.transform(Matrix.Translation(a) @ rot)
    k.recalc_normals(obj)
    k.smooth(obj, 50)
    paint_light(obj, m, [(-99, "g3"), (4.6, "g5"), (5.8, "g8"), (6.9, "gb")], 7.5)
    # the flange on the pylon's inner face
    centre = a + d * t_at(PYLON_X + PYLON_HW * 0.92)
    fl = [(BOLT_R + 0.6, -0.6), (BOLT_R + 1.5, -0.6), (BOLT_R + 1.7, 0.1), (BOLT_R + 1.4, 0.55), (BOLT_R + 0.4, 0.65)]
    rings = [[Vector((r * math.cos(2 * math.pi * j / 20), r * math.sin(2 * math.pi * j / 20), t)) for j in range(20)]
             for r, t in fl]
    flange = k.loft(f"flange{side:+d}_{y:.0f}", rings, m["g8"], cap_start=False, cap_end=False)
    flange.data.transform(Matrix.Translation(centre) @ rot)
    k.recalc_normals(flange)
    k.smooth(flange, 40)
    paint_light(flange, m, [(-99, "g3"), (4.8, "g5"), (6.0, "g8"), (7.0, "gb")], 6.2)
    return [obj, flange]


# The claws between the bolts (the left ones; rows 33-49 and 57-73: crescents 7 pixels wide, their convex side out)
# and the big ones under the pineapple's sides (columns 66-78 of rows 88-106): stations (x, y, z, half-width,
# half-height).
CLAW = [(-34.2, 39.2, 16.0, 0.7, 0.6), (-35.0, 37.6, 16.0, 2.9, 1.8), (-36.4, 34.0, 15.6, 4.0, 2.4),
        (-37.0, 29.0, 15.3, 4.2, 2.5), (-36.4, 24.0, 15.6, 4.0, 2.4), (-35.1, 20.4, 16.0, 2.9, 1.8),
        (-34.4, 18.8, 16.0, 0.7, 0.6)]
BIG_CLAW = [(-27.4, -15.8, 8.2, 0.7, 0.7), (-26.8, -18.6, 8.0, 1.5, 1.2), (-25.2, -23.0, 7.4, 2.3, 1.6),
            (-23.1, -27.4, 6.6, 2.9, 1.8), (-21.1, -31.4, 5.8, 3.0, 1.8), (-19.9, -34.0, 5.1, 2.1, 1.3),
            (-18.6, -36.0, 4.6, 0.9, 0.6), (-17.6, -37.1, 4.3, 0.08, 0.08)]


def densified(stations, step):
    from polish_torm_beetle import densify
    return [tuple(float(v) for v in d) for d in densify(stations, step)]


def claws(m, side):
    out = []
    for i, dy in enumerate((0.0, -24.0)):
        st = [(-side * x, y + dy, z, hw, hh, 1.7) for x, y, z, hw, hh in CLAW]
        obj = section_loft(f"claw{side:+d}_{i}", densified(st, 1.5), m["yc"], segments=10)
        k.smooth(obj, 70)
        paint_light(obj, m, [(-99, "yb"), (5.6, "yc"), (6.8, "yd")], 6.4)
        out.append(obj)
    st = [(-side * x, y, z, hw, hh, 1.8) for x, y, z, hw, hh in BIG_CLAW]
    obj = section_loft(f"big_claw{side:+d}", densified(st, 1.5), m["yc"], segments=10)
    k.smooth(obj, 70)
    paint_light(obj, m, [(-99, "yb"), (5.6, "yc"), (6.8, "yd")], 6.4)
    out.append(obj)
    return out


# --- The pineapple --------------------------------------------------------------------------------------------------
SCALE = 8.4                       # the diamond scales' size (pixels across and along; the sprites' lattice)
R0 = 32.0                         # the scale lattice's radius: arc length round the fruit is v * R0
SCALE_AMP = 0.8                   # how far a scale's middle stands out over its creases
WIN_C, WIN_R, WIN_P = (0.5, 16.5), (11.6, 26.6), 2.15   # the window (columns 85-107 of rows 27-79)
GLASS_LIFT, GLASS_BULGE = 0.3, 2.6                      # the glass lens over it: at its rim, in its middle
FIG_LIFT = 1.0                    # the figure's axis over the window's floor (the skin)
HALO = (1.2, 3.4)                 # the floor lighter within these distances of the figure


def window_e(x, y):
    """< 0 inside the window's outline."""
    return (abs(x - WIN_C[0]) / WIN_R[0]) ** WIN_P + (abs(y - WIN_C[1]) / WIN_R[1]) ** WIN_P - 1.0


def lattice(v, y):
    s_ = v * R0
    return (s_ + y) / SCALE, (s_ - y) / SCALE


def cushion(a, b):
    """0 in the creases between the scales, 1 in their middles."""
    fa, fb = a - math.floor(a), b - math.floor(b)
    return (math.sin(math.pi * fa) * math.sin(math.pi * fb)) ** 0.6


def body_point(v, y):
    """The smooth skin's point at angle v round the fruit (0 on top, +-pi/2 its sides) and y, with its normal."""
    r = max(R(y), 1e-3)
    x = r * math.sin(v)
    z = Z0 + ZS * r * math.cos(v)
    dy = 0.05
    dr = (R(min(Y_TOP, y + dy)) - R(max(Y_END, y - dy))) / (2 * dy)
    nx = x / (r * r)
    nz = (z - Z0) / (ZS * ZS * r * r)
    ny = -(x * x / r ** 3 + (z - Z0) ** 2 / (ZS * ZS * r ** 3)) * dr
    n = Vector((nx, ny, nz))
    return Vector((x, y, z)), (n.normalized() if n.length > 1e-9 else Vector((0.0, 0.0, 1.0)))


RING_STEP = 2.0                   # the fruit's rings this far apart along its surface


def end_fade(y):
    """1 over the fruit, fading to 0 at its ends (no scales on its tips)."""
    return smoothstep(Y_END + 1.0, Y_END + 7.0, y) * smoothstep(Y_TOP - 0.8, Y_TOP - 5.0, y)


def ring_positions(step):
    """y of the fruit's rings, about `step` apart along its outline (closer in y towards its ends)."""
    fine = [Y_END + (Y_TOP - Y_END) * i / 4000 for i in range(4001)]
    length = [0.0]
    for y0, y1 in zip(fine, fine[1:]):
        length.append(length[-1] + math.hypot(y1 - y0, R(y1) - R(y0)))
    total = length[-1]
    count = int(round(total / step))
    out, j = [], 0
    for i in range(1, count):
        target = total * i / count
        while length[j + 1] < target:
            j += 1
        f = (target - length[j]) / (length[j + 1] - length[j])
        out.append(fine[j] + (fine[j + 1] - fine[j]) * f)
    return [Y_END + 0.05] + out + [Y_TOP - 0.05]


def pineapple(m):
    """The fruit: rings of its smooth skin round its axis (y), cut along the scales' creases, the window's outline and
    the halo round the figure (the mesh's lines), the scales raised in their middles; painted by the creases and the
    light, the window's floor dark, lighter round the figure; its bottom cut flat at z 0."""
    bm = bmesh.new()
    names = ("v", "y", "g1", "g2", "win", "fig")
    vals = {n_: {} for n_ in names}
    ys = ring_positions(RING_STEP)
    seg = 80
    rings = []
    for y in ys:
        ring = []
        for j in range(seg):
            v = -math.pi + 2 * math.pi * j / seg
            p, _n = body_point(v, y)
            vert = bm.verts.new(p)
            a, b = lattice(v, y)
            vals["v"][vert] = v
            vals["y"][vert] = y
            vals["g1"][vert] = math.sin(math.pi * a)
            vals["g2"][vert] = math.sin(math.pi * b)
            vals["win"][vert] = window_e(p.x, p.y)
            vals["fig"][vert] = figure_distance(p.x, p.y)
            ring.append(vert)
        rings.append(ring)
    for r0, r1 in zip(rings, rings[1:]):
        for j in range(seg):
            jn = (j + 1) % seg
            bm.faces.new((r0[j], r0[jn], r1[jn], r1[j]))
    for ring, y, flip in ((rings[0], ys[0] - 0.1, True), (rings[-1], ys[-1] + 0.1, False)):
        c = bm.verts.new((0.0, y, Z0))
        for n_ in names:
            vals[n_][c] = 0.0
        vals["y"][c] = y
        vals["win"][c] = 1.0
        vals["fig"][c] = 99.0
        for j in range(seg):
            jn = (j + 1) % seg
            bm.faces.new((ring[jn], ring[j], c) if not flip else (ring[j], ring[jn], c))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    # the window's outline, the creases outside it, the halo inside it: mesh lines
    split_contour(bm, vals, "win", 0.0)
    outside = {f for f in bm.faces if sum(vals["win"][v] for v in f.verts) / len(f.verts) > 0.0}
    inside = set(bm.faces) - outside
    outside = {f for f in outside if end_fade(sum(vals["y"][v] for v in f.verts) / len(f.verts)) > 0.05}
    outside = split_contour(bm, vals, "g1", 0.0, outside)
    split_contour(bm, vals, "g2", 0.0, outside)
    inside = split_contour(bm, vals, "fig", HALO[0], inside)
    split_contour(bm, vals, "fig", HALO[1], inside)
    # the scales: each vertex moved out along the smooth skin's normal by its cushion (none in the window)
    values = []
    for v in bm.verts:
        vv, yy = vals["v"][v], vals["y"][v]
        p, n = body_point(vv, yy)
        a, b = lattice(vv, yy)
        end = end_fade(yy)
        c = 0.5 + (cushion(a, b) - 0.5) * end if vals["win"][v] > 0.0 else 0.5
        fade = smoothstep(0.0, 0.25, vals["win"][v])
        v.co = p + n * (SCALE_AMP * (c - 0.5) * fade)
        values.append(light_value(n, 1.6 + 3.2 * c, 2.6, 1.0))
    obj = mesh_from_bm("pineapple", bm, m, ["s5"] * len(bm.faces))
    # band_split by the values (it rebuilds the faces: the window's floor is painted after it, by position)
    band_split(obj, values, [(-99, m["s0"]), (2.3, m["s3"]), (3.6, m["s5"]), (4.6, m["s7"])])

    def floor(c, n):
        if window_e(c.x, c.y) < -0.002:
            d = figure_distance(c.x, c.y)
            return m["cav4"] if d < HALO[0] else (m["cav2"] if d < HALO[1] else m["cav"])
        return None
    mk.paint(obj, floor)
    k.smooth(obj, 55)
    flat_bottom(obj, m["s0"])
    return obj


def window(m):
    """The window's smoky glass lens over its dark floor, and the dark rolled rim round it."""
    parts = []
    cx, cy = WIN_C
    ax, ay = WIN_R
    seg, nr = 72, 12

    def outline(u, t):
        c, s_ = math.cos(t), math.sin(t)
        ex = math.copysign(abs(c) ** (2 / WIN_P), c)
        ey = math.copysign(abs(s_) ** (2 / WIN_P), s_)
        return cx + ax * ex * u, cy + ay * ey * u

    def base_z(x, y):
        z = skin_z(x, y)
        return z if z is not None else Z0

    bm = bmesh.new()
    rings = []
    centre = bm.verts.new((cx, cy, base_z(cx, cy) + GLASS_LIFT + GLASS_BULGE))
    for i in range(1, nr + 1):
        u = i / nr
        ring = []
        for j in range(seg):
            x, y = outline(u, 2 * math.pi * j / seg)
            ring.append(bm.verts.new((x, y, base_z(x, y) + GLASS_LIFT + GLASS_BULGE * (1.0 - u ** 2.4))))
        rings.append(ring)
    for j in range(seg):
        bm.faces.new((centre, rings[0][j], rings[0][(j + 1) % seg]))
    for r0, r1 in zip(rings, rings[1:]):
        for j in range(seg):
            jn = (j + 1) % seg
            bm.faces.new((r0[j], r1[j], r1[jn], r0[jn]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    for f in bm.faces:
        if f.normal.z < 0:
            f.normal_flip()
    glass = mesh_from_bm("glass", bm, m, ["glass"] * len(bm.faces))
    parts.append(k.smooth(glass, 60))
    pts = []
    for j in range(72):
        x, y = outline(1.0, 2 * math.pi * j / 72)
        pts.append((x, y, base_z(x, y) + 0.3, 1.1, 0.8, 2.0))
    rim = ring_loft("rim", pts, m["g3"], segments=8)
    k.smooth(rim, 60)
    paint_light(rim, m, [(-99, "cav"), (5.0, "g3"), (6.4, "g8")], 6.0)
    parts.append(rim)
    parts.append(figure(m))
    return parts


def ring_loft(name, stations, mat, segments=10):
    """A closed ring through stations (x, y, z, half-width, half-height, power): sections lying flat."""
    pts = [Vector(s_[:3]) for s_ in stations]
    n = len(pts)
    verts, faces = [], []
    for i, st in enumerate(stations):
        t = (pts[(i + 1) % n] - pts[i - 1]).normalized()
        side = t.cross(Vector((0.0, 0.0, 1.0))).normalized()
        up = side.cross(t).normalized()
        hw, hh, pw = st[3], st[4], st[5]
        for j in range(segments):
            a = 2 * math.pi * j / segments
            c, s_ = math.cos(a), math.sin(a)
            verts.append(pts[i] + side * (math.copysign(abs(c) ** (2 / pw), c) * hw) +
                         up * (math.copysign(abs(s_) ** (2 / pw), s_) * hh))
    for i in range(n):
        i2 = (i + 1) % n
        for j in range(segments):
            j2 = (j + 1) % segments
            faces.append((i * segments + j, i * segments + j2, i2 * segments + j2, i2 * segments + j))
    obj = k.mesh_object(name, verts, faces, mat)
    k.recalc_normals(obj)
    return obj


# The figure in the window (the sprites' pale S of light: a blob at columns 91-98 of rows 42-52, a thin stem down to
# a bigger blob at columns 94-102 of rows 61-71): stations along it (x, y, radius).
FIGURE = [(-1.2, 28.2, 0.3), (-1.4, 26.6, 1.5), (-1.2, 24.0, 2.6), (-0.9, 21.2, 2.8), (-0.5, 18.4, 1.9),
          (0.0, 15.6, 0.95), (0.6, 12.6, 0.85), (1.2, 9.6, 1.6), (1.8, 6.6, 2.9), (2.1, 3.6, 3.2), (1.9, 0.8, 2.5),
          (1.5, -1.6, 1.2), (1.2, -2.8, 0.3)]
FIG_FLAT = 0.3                    # its height over its width


def figure_distance(x, y):
    best = 99.0
    p = Vector((x, y))
    for (x0, y0, r0), (x1, y1, r1) in zip(FIGURE, FIGURE[1:]):
        a, b = Vector((x0, y0)), Vector((x1, y1))
        ab = b - a
        t = max(0.0, min(1.0, (p - a).dot(ab) / ab.length_squared))
        best = min(best, (a + ab * t - p).length - (r0 + (r1 - r0) * t))
    return best


def figure(m):
    st = []
    for i in range(len(FIGURE) - 1):
        (x0, y0, r0), (x1, y1, r1) = FIGURE[i], FIGURE[i + 1]
        for t in ((0.0, 0.5) if i < len(FIGURE) - 2 else (0.0, 0.5, 1.0)):
            x, y, r = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, r0 + (r1 - r0) * t
            z = (skin_z(x, y) or Z0) + FIG_LIFT
            st.append((x, y, z, r * 0.82, r * FIG_FLAT + 0.1, 2.0))
    obj = section_loft("figure", st, m["fig"], segments=16)
    k.smooth(obj, 70)
    view = Vector((0.0, -math.sin(math.radians(VIEW_TILT)), math.cos(math.radians(VIEW_TILT))))
    mk.paint(obj, lambda c, n: m["fig"] if n.dot(view) > 0.75 else m["fig_edge"])
    return obj


# --- The crown --------------------------------------------------------------------------------------------------------
# Leaves from the crown's stem (it comes out of the fruit's end, y Y_END): (base x, base y, tip x, tip y, z at the
# base, the middle and the tip, half-width): four pairs going out and down the screen from the stem (the sprites'
# leaves ending at columns 76 and 113 of rows 109-116, 75 and 114 of rows 121-125, 79 and 112 of rows 128-132, 90 and
# 108 of rows 136-137), the inner ones rising along it (the sprites' lighter middle, columns 84-103), short ones at
# its foot.
LEAVES = [
    # the middle: overlapping leaves rising along the stem, fanning out down the screen (columns 84-106)
    (0.0, -30.0, -7.5, -50.0, 6.0, 11.0, 8.5, 3.0), (0.0, -31.0, 6.5, -49.0, 6.0, 11.0, 8.5, 3.0),
    (0.0, -34.0, -9.5, -57.0, 6.5, 12.0, 9.0, 2.9), (0.0, -35.0, 7.5, -56.5, 6.5, 12.0, 9.0, 2.9),
    (0.0, -38.0, -4.5, -62.5, 7.0, 12.5, 9.5, 2.6), (0.0, -38.0, 4.0, -61.5, 7.0, 12.5, 9.5, 2.6),
    (0.0, -42.0, -1.0, -66.5, 7.0, 11.5, 8.5, 2.2),
    # out to the left (short, rows 113-116, 122-125, 130-132) and the right (longer, rows 107-109, 118-121,
    # 125-128, 132-136)
    (-2.0, -41.0, -19.5, -46.5, 5.5, 7.0, 4.5, 1.7), (-2.0, -50.0, -20.5, -55.5, 6.0, 7.4, 4.8, 1.7),
    (-2.0, -57.5, -17.0, -62.5, 6.2, 7.6, 5.0, 1.6),
    (2.0, -34.0, 17.5, -39.0, 5.2, 6.8, 4.2, 1.6), (2.0, -45.0, 18.5, -51.0, 5.8, 7.2, 4.6, 1.6),
    (2.0, -53.0, 17.5, -58.0, 6.0, 7.5, 4.8, 1.6), (1.5, -58.0, 13.0, -66.0, 6.3, 7.6, 5.2, 1.5),
    # the stalk's end (columns 90-92 of rows 132-137) and short ones at the foot
    (-1.0, -55.0, -5.5, -68.0, 6.0, 7.0, 5.5, 1.2),
    (-2.0, -30.0, -11.0, -35.5, 4.8, 5.6, 3.6, 1.5), (2.0, -30.0, 11.0, -35.0, 4.8, 5.6, 3.6, 1.5),
]
STEM = [(0.0, -26.0, Z0 + 0.5, 4.2), (0.0, -31.0, Z0 + 1.5, 3.8), (0.0, -38.0, Z0 + 2.4, 3.0),
        (0.0, -46.0, Z0 + 3.0, 2.2), (0.0, -54.0, Z0 + 3.2, 1.4), (0.0, -59.0, Z0 + 3.2, 0.6), (0.0, -60.5, Z0 + 3.2, 0.2)]


def crown(m):
    out = []
    st = [(x, y, z, r, r * 0.85, 2.0) for x, y, z, r in STEM]
    stem = section_loft("stem", st, m["c4"], segments=14)
    k.smooth(stem, 60)
    paint_light(stem, m, [(-99, "c2"), (5.2, "c4"), (6.3, "c6")], 6.0)
    out.append(stem)
    for i, (bx, by, tx, ty, zb, zm, zt, hw) in enumerate(LEAVES):
        base = Vector((bx, by, zb))
        tip = Vector((tx, ty, zt))
        mid = base.lerp(tip, 0.5)
        mid.x += 0.04 * (tx - bx)
        mid.z = zm
        st = []
        count = 11
        for j in range(count):
            t = j / (count - 1)
            p = (1 - t) ** 2 * base + 2 * t * (1 - t) * mid + t * t * tip
            w = 1.3 * hw * min(1.0, (1.0 - t) / 0.32) ** 0.8 * (0.72 + 0.28 * math.sin(math.pi * t))
            h = 0.42 * (1 - t) + 0.08
            st.append((p.x, p.y, p.z, max(w, 0.06), max(h, 0.06), 1.35))
        leaf = section_loft(f"leaf{i}", st, m["c4"], segments=10)
        k.smooth(leaf, 60)
        paint_light(leaf, m, [(-99, "c2"), (4.9, "c4"), (6.0, "c6"), (7.0, "c8")], 6.0)
        out.append(leaf)
    return out


# --- The whole --------------------------------------------------------------------------------------------------------

def build_whole():
    k.reset()
    m = materials()
    parts = []
    left = plate_half(m)
    parts += [left, mirror_obj(left, "plate_r")]
    for side in (-1, 1):
        parts += lamp(m, side)
        parts += pylon(m, side)
        for y in BOLT_Y:
            parts += bolt(m, side, y)
        parts += claws(m, side)
    parts.append(pineapple(m))
    parts += window(m)
    parts += crown(m)
    for obj in parts:
        mk.apply(obj)
    bpy.context.view_layer.update()
    return parts, m


def shear_to_camera(objects):
    """polish_lemon_beetle's: every point moved along the game camera's line of sight to its height (y - z tan T), so
    that the camera sees each where the sprite draws it; the normals follow."""
    for obj in objects:
        mesh = obj.data
        normals = [Vector(cn.vector) for cn in mesh.corner_normals]
        for v in mesh.vertices:
            v.co.y -= v.co.z * TAN_T
        out = [Vector((n.x, n.y, n.z + TAN_T * n.y)).normalized() for n in normals]
        mesh.normals_split_custom_set([tuple(n) for n in out])
        mesh.update()


# The pieces: (sprite, top left pixel (column, row) in the whole), as the level events lay them out.
LAYOUT = [(153 + 2 * i, 24 * i, 0) for i in range(8)] + [(191 + 2 * i, 24 * i, 28) for i in range(8)] + \
         [(229 + 2 * i, 24 * i, 56) for i in range(8)] + [(270 + 2 * i, 36 + 24 * i, 84) for i in range(5)] + \
         [(281, 72, 112), (283, 96, 112)]


def pieces():
    """(name, sprite, cutting box (x0, x1, y0, y1), origin (x, y)): the boxes of the picture's edge pieces reach out
    past it (the fruit's top end, the plate's edges)."""
    out = []
    for sprite, c0, r0 in LAYOUT:
        x0, y1 = px(c0, r0)
        x1, y0 = px(c0 + 24, r0 + 28)
        origin = ((x0 + x1) / 2, (y0 + y1) / 2)
        bx0 = x0 - 20.0 if c0 == 0 else x0
        bx1 = x1 + 20.0 if c0 + 24 == W else x1
        by1 = y1 + 20.0 if r0 == 0 else y1
        by0 = y0 - 20.0 if r0 + 28 == H else y0
        out.append((f"pineapple_{sprite}", sprite, (bx0, bx1, by0, by1), origin))
    return out


CAPS = {"plate": "g5", "socket": "g5", "lamp": "pith", "pylon": "t5", "bolt": "g5", "flange": "g5", "claw": "yb",
        "big_claw": "yb", "pineapple": "yb", "glass": "glass", "rim": "g3", "figure": "fig", "stem": "c4", "leaf": "c4"}


def cap_of(obj, m):
    best = None
    for prefix, key in CAPS.items():
        if obj.name.startswith(prefix) and (best is None or len(prefix) > len(best[0])):
            best = (prefix, key)
    return m[best[1] if best else "g5"]


def whole_mask(sheet):
    mask = [[False] * W for _ in range(H)]
    for sprite, c0, r0 in LAYOUT:
        for r, line in enumerate(k.sprite_mask(sheet, sprite)):
            for c, v in enumerate(line):
                if v:
                    mask[r0 + r][c0 + c] = True
    return mask


def build():
    options = k.args()
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    sheet = None
    if "check" in options:
        sheets = options["check"]
        sheet = os.path.join(sheets, "enemy_x27.png") if os.path.isdir(sheets) else sheets
    whole, m = build_whole()
    triangulate(whole)
    low, high = mk.bounds(whole)
    print("== whole: %d triangles, %d materials, x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f" % (
        mk.triangles(whole), len(mk.materials_of(whole)), low.x, high.x, low.y, high.y, low.z, high.z))
    bpy.context.scene.view_settings.view_transform = "Standard"
    if sheet:
        mk.compare("whole, as the camera sees it", mk.coverage(whole, W, H), whole_mask(sheet))
    if "whole" in options or "preview" in options:
        seen = []
        for o in whole:
            c = o.copy()
            c.data = o.data.copy()
            bpy.context.scene.collection.objects.link(c)
            seen.append(c)
        shear_to_camera(seen)
        for o in whole:
            o.hide_render = True
        if "whole" in options:
            mk.export(seen, options["whole"])
        if "preview" in options:
            mk.preview(options["preview"] + "pineapple", seen, size=(W, H), scale=5, distance=2.6)
        for o in seen:
            mesh = o.data
            bpy.data.objects.remove(o)
            bpy.data.meshes.remove(mesh)
        for o in whole:
            o.hide_render = False
    bpy.context.view_layer.update()
    for name, sprite, box, origin in pieces():
        if only and name not in only:
            continue
        parts = [p for p in (cut(src, box, cap_of(src, m)) for src in whole) if p is not None]
        drop_unused(parts)
        for src in whole:
            src.hide_render = True
        if sheet:
            mk.compare("%s (x27 %d), as the camera sees it" % (name, sprite),
                       mk.coverage(parts, 24, 28, centre=origin), k.sprite_mask(sheet, sprite))
        shear_to_camera(parts)
        mk.transform(parts, Matrix.Translation((-origin[0], -origin[1], 0)))
        bpy.context.view_layer.update()
        triangulate(parts)
        if "stats" in options:
            for obj in sorted(parts, key=lambda o: -mk.triangles([o]))[:8]:
                print("    %-18s %6d" % (obj.name, mk.triangles([obj])))
        parts = [join(parts, name)]
        parts[0].data.name = name
        mk.report(name, parts, os.path.join(out, name + ".glb"))
        if "preview" in options and options.get("pieces") == "1":
            mk.preview(options["preview"] + name, parts)
        for obj in parts:
            bpy.data.objects.remove(obj)
        for src in whole:
            src.hide_render = False


if __name__ == "__main__":
    build()
