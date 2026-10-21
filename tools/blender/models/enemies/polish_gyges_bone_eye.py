"""GYGES' ring of knobbly bone in a square of tube wall round a pit with a green eye (sheet H sprite 39, 2x2: the whole
24 x 28 cell; enemy 153 of episode 2, in the sky, sixteen of them; its animation 39 1 3 3 3 1 39, played when it
fires: the eye in the pit lights up and dims again), polished (2026-10-22, round 29; it replaces wave3_ad.py's
gyges_bone_eye, a slab of tube wall with a hoop and an always-lit eye). models.cfg: model gyges_bone_eye
enemies/gyges_bone_eye.glb (unchanged), new frame models gyges_bone_eye_1 and gyges_bone_eye_3 (frame h 1, frame h 3).
No other enemy, launched ones included, shows H 39, 1 or 3; none is another sprite's pixels mirrored, turned or in
other ramps.

Where GYGES puts it (event 15, the sky, eyc +2: it moves down the screen with background 2, which scrolls 2 pixels a
tick; at t348 five in a row at x -42 ... 246, then one or two at a time to t5192): always exactly over a tile of
background 2's tube wall that draws the same bone ring (its shapes 62, 64 and 72; the enemy's sprite covers the tile
pixel for pixel), so that the wall's ring comes alive and fires. In the 3D view background 2 is a solid (its top at
16 pixels) and the sky enemies fly at 58, aligned with the planes below them: the model covers its ring tile in the
camera's view, its square of wall standing in for the tile's.

As the sprite and its 4x upscales draw it: the grey-blue tube wall of GYGES (palette ramp 6: glossy tubes woven
together, light where they bulge, dark in the gaps) filling the square; in it a thick ring of knobbly bone (ramp
10, its brightest shades 0x1c and 0x1d of ramp 1), seven rounded knuckles round a dark pit (columns 4-21, rows
4-21; its middle at column 12.4, row 12.5), brightest on the knuckles at its top and bottom, a dark crease between
each two; the pit (columns 9-15 of rows 10-16) nearly black green (0x20-0x22), a faint dark ball in it. Frame 1
lights the ball (0xc0-0xc9, a dim green eye), frame 3 makes it glow (0xcc-0xcf round a white middle, the pit's rim
lit green).

Built for the game's camera: a slab of tube wall the size of the cell (its top a heightfield of the sprite's wall
shades: tubes raised up to a pixel where the sprite is light, sunk where it is dark, the relief fading out towards
the edges, which lie flat like the tile's plane round it; painted in five shades of ramp 6 by the sprite's shade
there, its sides in the wall's colour as the wall going on, for the camera's view of them off the screen's middle),
the pit sunk into it in a bowl; the bone ring a hoop lofted round the pit whose inner and outer edges follow the
sprite's bone pixels along rays out of the ring's middle and whose height follows their brightness, swollen into
seven knuckles where the sprite's bone is brightest with a crease between each two, painted bone by how it faces
the sun (lit on the knuckles' upper left, the plain bone on top, darker sides, dark at its foot and in the
creases); the eye a ball in the pit, darker round its rim where it turns from the camera, its core a small lens
where the camera's ray through the ball's middle meets it (VIEW_TILT: the camera sees the core in the eye's middle,
where the sprite draws it). The frame models are the same model with the eye's and the pit's colours of their frame
(dark; a dim green eye glowing 0.22-0.42; bright green 0.38-0.45 round a white core at 0.6: emission well under 1,
the game's bloom adds), so their bounds are the same: the game, which draws them centred in height, keeps them in
place. models.cfg's glow (glow=12:0.25:198 on h 39) lit the pit even while its eye is dark (frame 39, most of the
time: the animation plays only when it fires): the frame models light it now, so the glow is best dropped.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; origin at the
sprite's centre (pixel 12, 14): column c is x = c + 0.5 - 12, row r is y = 13.5 - r. The slab's bottom is z = 0.

Replaces wave3_ad.py's bone eye (its section "# --- H 39: the bone ring with its eye": RING, RING_LIT and
bone_eye(), and its docstring paragraph) and wave3_ad_art.py's RING and RING_3 (only that section reads them).
wave3_ad_kit.py's tube_wall() stays (wave3_ad_wall.py's creatures use it).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouette against
enemy_H.png, and the ring's against the sprite's bone pixels), --preview <prefix>, --only <name,...>.
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402

# The sprite (frame 39): each pixel its palette index as two hex digits, rows top to bottom.
PIXELS = """
646668676466686562636467686663696765646363636362
64676665626768656362676b696464696967656263666663
6567666362676c646363696c656363666969666360646564
6767666362666c6463636767ff66666467676a6a63616263
66676464626568656464680aa9a7076765666b6f69616163
6668656460616507090809ab1ca8aaa90562656769620162
666965640101050aacaaaa1c1ca81d1d0703016366650163
66686665016006abafaf1d1d1ca8aeaeaaa5606264650163
666c6865010468a9aeafae6caaa61caf1ca7036664626264
686e65626407a803a81c686565a0a51caaa703a9a8646366
696a6560656cafa80365610120202067a7a7a8afaa056367
68666301656b1da7026020222022222064a6a71da8046365
656563600306a7a664202020202021206003aa1ca5a56365
6462620102a5a6a7642022202020200101a5a8a6a7a80362
6264636002a6a8aa656022202020222061a7a8a6a9070361
6567656102a71d1c0363012122212061a51ca50507666162
6769676102a8ae1ca566646201016166a7a8036465606062
676967646007ab1da7a769696767686b1ca6016160616462
66696a64626709aaa81caaaaaa1daeaeaa02013060636462
65696e656162680706a8a91dafafacaaa702306060666462
65686c67616064646506aaaeafab09060361016264686462
66676664636360600166090a09066664616060636a6e6562
66686663636463630163656563636261016361636a6b6461
646666646365656461696662610160646665626568676462
6566656162656966626764626061656a6a66626669686461
6565626264656a66016363626062686d696563686a676460
646264666665696561636262626465686766646867646360
646467686566696562636163666564686765646465646160
"""
GRID = [[int(row[2 * c:2 * c + 2], 16) for c in range(24)] for row in PIXELS.split()]

# The ring's middle (x, y) and the pit: its radius and its floor's height.
CENTRE = (0.9, 1.0)
PIT_R, PIT_FLOOR = 4.0, 0.45
# The slab: its top's height, the tubes' relief (pixels per unit of the wall's normalised shade, its limits), how far
# in from the edges the relief fades in (the edges flat, as the tile's plane round it), the grid's step.
SLAB_TOP = 1.6
RELIEF, RELIEF_LIMITS = 1.0, (-0.75, 0.95)
EDGE_FADE = 1.6
STEP = 0.64
# The slab's paint: the wall's shades (ramp 6) it is painted in, by the sprite's shade there.
WALL_SHADES = [0x62, 0x64, 0x66, 0x68, 0x6a]
# The ring of bone, a hoop round the pit lofted round CENTRE: along each ray out of CENTRE (every RAY_STEP degrees)
# the sprite's bone pixels (ramp 10, the highlights 0x1c, 0x1d and the greys 0x05-0x0b that shade its edge) give its
# inner and outer edge (smoothed round the ring over RADIUS_SMOOTH degrees, a little outside the pixels) and their
# brightness its height (smoothed over HEIGHT_SMOOTH: the bright knuckles stand up, the creases between them sink):
# from RING_LOW to RING_HIGH above the slab; its section a rounded hump, sunk into the slab at its foot.
RAY_STEP = 3
RADIUS_SMOOTH, HEIGHT_SMOOTH = 18.0, 12.0
RING_LOW, RING_HIGH = 1.5, 3.0
RING_SECTION = 16
# The knuckles on it, where the sprite's bone is brightest (its upscale at radii 5-8 round the ring's middle), degrees
# round CENTRE from +X anticlockwise: each swells the ring (higher by KNUCKLE_UP, wider by KNUCKLE_OUT) over about
# KNUCKLE_WIDTH degrees; between each two a crease (lower by CREASE_DOWN, narrower, over CREASE_WIDTH degrees).
KNUCKLES = [16, 66, 118, 166, 212, 266, 338]
KNUCKLE_UP, KNUCKLE_OUT, KNUCKLE_WIDTH = 0.9, 0.35, 15.0
CREASE_DOWN, CREASE_IN, CREASE_WIDTH = 0.75, 0.25, 6.0
# The eye: its middle (x, y, z) and radii; VIEW_TILT: its face turned to the game's camera.
EYE = ((0.9, 0.85, 1.1), (2.95, 2.95, 1.1))
VIEW_TILT = 20.0
VIEW = Vector((0.0, -math.sin(math.radians(VIEW_TILT)), math.cos(math.radians(VIEW_TILT))))
SUN = Vector((-0.6, 0.6, 1.0)).normalized()      # towards the game's sun (from the upper left)

# The frames: (model, sprite, the eye's colours: its rim (where the ball turns from the camera: facing it less than
# RIM_FACING), its body and its core (palette index, emission strength; the core's radius), the pit's colour round
# the eye). 39: dark (the sprite's near-black greens); 1: a dim green eye; 3: glowing, a white core.
RIM_FACING = 0.62
FRAMES = [
    ("gyges_bone_eye", 39, (0x21, 0.0), (0x22, 0.0), (0x23, 0.0, 0.9), 0x21),
    ("gyges_bone_eye_1", 1, (0xc1, 0.22), (0xc4, 0.3), (0xc9, 0.42, 0.75), 0x21),
    ("gyges_bone_eye_3", 3, (0xc8, 0.38), (0xcc, 0.45), (0x0f, 0.6, 1.05), 0x24),
]


def smoothstep(e0, e1, x):
    t = min(1.0, max(0.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


def wall_shade_field():
    """The wall's shade (0-15) at each pixel, its other pixels (bone, pit, the odd stray) taking their wall
    neighbours' average; then a light blur."""
    shade = [[None] * 24 for _ in range(28)]
    for r in range(28):
        for c in range(24):
            v = GRID[r][c]
            if v >> 4 == 6:
                shade[r][c] = float(v & 15)
    for _ in range(12):
        filled = [row[:] for row in shade]
        for r in range(28):
            for c in range(24):
                if shade[r][c] is None:
                    near = [shade[rr][cc] for rr in range(max(0, r - 1), min(28, r + 2))
                            for cc in range(max(0, c - 1), min(24, c + 2)) if shade[rr][cc] is not None]
                    if near:
                        filled[r][c] = sum(near) / len(near)
        shade = filled
    blurred = [[0.0] * 24 for _ in range(28)]
    for r in range(28):
        for c in range(24):
            total = weight = 0.0
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    rr, cc = min(27, max(0, r + dr)), min(23, max(0, c + dc))
                    w = 4.0 if dr == dc == 0 else (2.0 if dr == 0 or dc == 0 else 1.0)
                    total += w * (shade[rr][cc] if shade[rr][cc] is not None else 5.0)
                    weight += w
            blurred[r][c] = total / weight
    return shade, blurred


SHADE, SHADE_SOFT = wall_shade_field()


def bilinear(field, x, y):
    """A pixel field at a point, between the pixels' centres."""
    fc, fr = x + 12.0 - 0.5, 13.5 - y
    c0, r0 = int(math.floor(fc)), int(math.floor(fr))
    tc, tr = fc - c0, fr - r0

    def at(r, c):
        return field[min(27, max(0, r))][min(23, max(0, c))]
    return ((at(r0, c0) * (1 - tc) + at(r0, c0 + 1) * tc) * (1 - tr) +
            (at(r0 + 1, c0) * (1 - tc) + at(r0 + 1, c0 + 1) * tc) * tr)


def materials():
    finish = dict(metallic=0.2, roughness=0.32)
    m = {"wall%d" % i: k.material("bone_eye_wall_%x" % s, palette=s, **finish) for i, s in enumerate(WALL_SHADES)}
    bone = dict(metallic=0.05, roughness=0.42)
    m["bone_dark"] = k.material("bone_eye_bone_dark", palette=0xa5, **bone)
    m["bone_side"] = k.material("bone_eye_bone_side", palette=0xa8, **bone)
    m["bone"] = k.material("bone_eye_bone", palette=0xab, **bone)
    m["bone_light"] = k.material("bone_eye_bone_light", palette=0xae, metallic=0.05, roughness=0.36)
    m["pit"] = k.material("bone_eye_pit", palette=0x20, metallic=0.0, roughness=0.7)
    return m


def frame_materials(frame):
    """The eye's materials of a frame (rim, body, core) and its pit's rim colour."""
    _, _, rim, body, core, pit = frame
    pal = k.level_palette()
    out = []
    for key, (index, glow) in (("rim", rim), ("body", body), ("core", core[:2])):
        extra = dict(emission=pal[index], emission_strength=glow) if glow > 0 else {}
        out.append(k.material("bone_eye_eye_%s_%x" % (key, index), palette=index, metallic=0.0, roughness=0.12,
                              **extra))
    return out, k.material("bone_eye_pit_rim_%x" % pit, palette=pit, metallic=0.0, roughness=0.6)


# --- The slab of tube wall -----------------------------------------------------------------------------------------

def slab_height(x, y):
    """The slab's top: the tubes' relief (fading in from the edges), the pit's bowl."""
    s = bilinear(SHADE_SOFT, x, y)
    t = (s - 5.0) / 4.0
    relief = min(RELIEF_LIMITS[1], max(RELIEF_LIMITS[0], RELIEF * t))
    edge = min(x + 12.0, 12.0 - x, y + 14.0, 14.0 - y)
    relief *= smoothstep(0.0, EDGE_FADE, edge)
    d = math.hypot(x - CENTRE[0], y - CENTRE[1])
    bowl = smoothstep(PIT_R + 0.6, PIT_R - 1.4, d)
    return SLAB_TOP + relief * (1 - bowl) - (SLAB_TOP - PIT_FLOOR) * bowl


def slab(m, pit_rim):
    """The slab: a grid over the cell at the top (each square split along its flatter diagonal), straight sides down
    to z = 0 and a flat bottom."""
    nx, ny = int(round(24 / STEP)), int(round(28 / STEP))
    bm = bmesh.new()
    rows = []
    for j in range(ny + 1):
        y = -14.0 + 28.0 * j / ny
        rows.append([bm.verts.new((-12.0 + 24.0 * i / nx, y, slab_height(-12.0 + 24.0 * i / nx, y)))
                     for i in range(nx + 1)])
    top = []
    for j in range(ny):
        for i in range(nx):
            a, b, c, d = rows[j][i], rows[j][i + 1], rows[j + 1][i + 1], rows[j + 1][i]
            if abs(a.co.z - c.co.z) <= abs(b.co.z - d.co.z):
                top += [bm.faces.new((a, b, c)), bm.faces.new((a, c, d))]
            else:
                top += [bm.faces.new((a, b, d)), bm.faces.new((b, c, d))]
    ring = [rows[0][i] for i in range(nx + 1)] + [rows[j][nx] for j in range(1, ny + 1)] + \
           [rows[ny][i] for i in range(nx - 1, -1, -1)] + [rows[j][0] for j in range(ny - 1, 0, -1)]
    low = [bm.verts.new((p.co.x, p.co.y, 0.0)) for p in ring]
    count = len(ring)
    sides = [bm.faces.new((ring[(i + 1) % count], ring[i], low[i], low[(i + 1) % count])) for i in range(count)]
    bottom = bm.faces.new(low[::-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    mesh = bpy.data.meshes.new("slab")
    keys = ["wall%d" % i for i in range(len(WALL_SHADES))] + ["pit"]
    slots = {key: i for i, key in enumerate(keys)}
    slots["pit_rim"] = len(keys)
    for f in top:
        cx = sum(v.co.x for v in f.verts) / 3
        cy = sum(v.co.y for v in f.verts) / 3
        d = math.hypot(cx - CENTRE[0], cy - CENTRE[1])
        if d < PIT_R - 1.2:
            f.material_index = slots["pit"]
        elif d < PIT_R + 0.4:
            f.material_index = slots["pit_rim"]
        else:
            s = bilinear(SHADE, cx, cy) if SHADE[0][0] is not None else 5.0
            shade = min(range(len(WALL_SHADES)), key=lambda i: abs((WALL_SHADES[i] & 15) - (s + 0.4)))
            f.material_index = slots["wall%d" % shade]
    for f in sides + [bottom]:
        f.material_index = slots["wall1"]       # the sides in the wall's colour, as the wall going on
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("slab", mesh)
    bpy.context.scene.collection.objects.link(obj)
    for key in keys:
        obj.data.materials.append(m[key])
    obj.data.materials.append(pit_rim)
    return k.smooth(obj, 45)


# --- The bone ring -------------------------------------------------------------------------------------------------

def luminance(index):
    r, g, b = k.level_palette()[index]
    return (0.3 * r + 0.59 * g + 0.11 * b) / 255.0


def is_bone(v):
    return v >> 4 == 0xa or v in (0x1c, 0x1d) or 0x05 <= v <= 0x0b


def angle_off(a, b):
    """The angle between two directions (degrees, 0-180)."""
    return abs((a - b + 180.0) % 360.0 - 180.0)


def circular_smooth(values, step, width):
    """Values round a circle (one every `step` degrees) smoothed with a Gaussian `width` degrees wide."""
    n = len(values)
    reach = int(math.ceil(2.5 * width / step))
    out = []
    for i in range(n):
        total = weight = 0.0
        for d in range(-reach, reach + 1):
            w = math.exp(-((d * step) / width) ** 2)
            total += w * values[(i + d) % n]
            weight += w
        out.append(total / weight)
    return out


def ring_profile():
    """Round the ring (every RAY_STEP degrees): the bone's inner and outer edge along the ray out of CENTRE and its
    brightness, from the sprite's pixels."""
    inner, outer, bright = [], [], []
    for i in range(360 // RAY_STEP):
        a = math.radians(i * RAY_STEP)
        hits = []
        r = 3.0
        while r < 10.5:
            x, y = CENTRE[0] + r * math.cos(a), CENTRE[1] + r * math.sin(a)
            c, row = int(math.floor(x + 12.0)), int(math.floor(14.0 - y))
            if 0 <= c < 24 and 0 <= row < 28 and is_bone(GRID[row][c]):
                hits.append((r, luminance(GRID[row][c])))
            r += 0.2
        if hits:
            inner.append(hits[0][0] - 0.3)
            outer.append(hits[-1][0] + 0.35)
            bright.append(sum(h for _, h in hits) / len(hits))
        else:
            inner.append(None)
            outer.append(None)
            bright.append(None)
    for values, default in ((inner, 5.0), (outer, 7.5), (bright, 0.4)):
        known = [v for v in values if v is not None]
        for i, v in enumerate(values):
            if v is None:
                values[i] = sum(known) / len(known) if known else default
    inner = circular_smooth(inner, RAY_STEP, RADIUS_SMOOTH)
    outer = circular_smooth(outer, RAY_STEP, RADIUS_SMOOTH)
    bright = circular_smooth(bright, RAY_STEP, HEIGHT_SMOOTH)
    lo, hi = min(bright), max(bright)
    height = [RING_LOW + (RING_HIGH - RING_LOW) * (b - lo) / max(1e-6, hi - lo) for b in bright]
    creases = [(a + (b if b > a else b + 360)) / 2 % 360 for a, b in zip(KNUCKLES, KNUCKLES[1:] + KNUCKLES[:1])]
    for i in range(len(height)):
        a = i * RAY_STEP
        swell = sum(math.exp(-(angle_off(a, kn) / KNUCKLE_WIDTH) ** 2) for kn in KNUCKLES)
        crease = sum(math.exp(-(angle_off(a, cr) / CREASE_WIDTH) ** 2) for cr in creases)
        height[i] += KNUCKLE_UP * swell - CREASE_DOWN * crease
        outer[i] += KNUCKLE_OUT * swell - CREASE_IN * crease
        inner[i] -= 0.5 * KNUCKLE_OUT * swell - 0.5 * CREASE_IN * crease
    return inner, outer, height


def ring(m):
    """The bone ring: a hoop lofted round CENTRE through its sections (a closed loop)."""
    inner, outer, height = ring_profile()
    sections, n = len(inner), RING_SECTION
    verts, faces = [], []
    for i in range(sections):
        a = math.radians(i * RAY_STEP)
        ca, sa = math.cos(a), math.sin(a)
        rc, hw, h = (inner[i] + outer[i]) / 2, max(1.2, (outer[i] - inner[i]) / 2), height[i]
        for j in range(n):
            t = 2 * math.pi * j / n
            u, v = math.cos(t), math.sin(t)
            r = rc + hw * math.copysign(abs(u) ** 0.85, u)
            z = SLAB_TOP - 0.4 + (h + 0.4) * max(v, 0.0) ** 0.75 - 0.7 * max(-v, 0.0)
            verts.append((CENTRE[0] + r * ca, CENTRE[1] + r * sa, z))
    for i in range(sections):
        i2 = (i + 1) % sections
        for j in range(n):
            j2 = (j + 1) % n
            faces.append((i * n + j, i2 * n + j, i2 * n + j2, i * n + j2))
    obj = k.mesh_object("ring", verts, faces, m["bone_side"])
    k.recalc_normals(obj)
    return k.smooth(obj, 55)


def paint_bone(objects, m):
    """Bone by how a face meets the light: lit on the knuckles' upper left, the plain bone on top, its sides, dark
    underneath and in the creases."""
    for obj in objects:
        mats = [m["bone_dark"], m["bone_side"], m["bone"], m["bone_light"]]
        obj.data.materials.clear()
        for mat in mats:
            obj.data.materials.append(mat)
        for poly in obj.data.polygons:
            n = poly.normal
            lit = n.dot(SUN)
            if poly.center.z < SLAB_TOP + 0.15 or n.z < 0.05:
                poly.material_index = 0
            elif lit > 0.86 and n.z > 0.5:
                poly.material_index = 3
            elif n.z > 0.62:
                poly.material_index = 2
            else:
                poly.material_index = 1


# --- The eye -------------------------------------------------------------------------------------------------------

def ellipsoid(name, centre, radii, mat, count=16, around=40):
    """An ellipsoid lofted from explicit rings (the same every run)."""
    (cx, cy, cz), (rx, ry, rz) = centre, radii
    rings = []
    for i in range(1, count):
        p = math.pi * i / count - math.pi / 2
        r, z = math.cos(p), math.sin(p)
        rings.append([Vector((cx + rx * r * math.cos(2 * math.pi * j / around),
                              cy + ry * r * math.sin(2 * math.pi * j / around), cz + rz * z)) for j in range(around)])
    return k.loft(name, rings, mat, start_point=(cx, cy, cz - rz), end_point=(cx, cy, cz + rz))


def eye(eye_mats, frame):
    """A ball in the pit, its rim darker where it turns from the camera (VIEW), and its core: a small lens where the
    camera's ray through the ball's middle meets it (VIEW_TILT), so that the camera sees the core in the eye's middle,
    where the sprite draws it."""
    (cx, cy, cz), (rx, ry, rz) = EYE
    ball = ellipsoid("eye", EYE[0], EYE[1], None)
    for mat in eye_mats[:2]:
        ball.data.materials.append(mat)
    for poly in ball.data.polygons:
        c = poly.center
        nrm = Vector(((c.x - cx) / rx ** 2, (c.y - cy) / ry ** 2, (c.z - cz) / rz ** 2)).normalized()
        poly.material_index = 1 if nrm.dot(VIEW) >= RIM_FACING else 0
    k.smooth(ball, 70)
    t = 1.0 / math.sqrt((VIEW.x / rx) ** 2 + (VIEW.y / ry) ** 2 + (VIEW.z / rz) ** 2)
    p = Vector((cx, cy, cz)) + VIEW * (t - 0.18)
    radius = frame[4][2]
    core = ellipsoid("eye_core", tuple(p), (radius, radius * 0.92, 0.42), eye_mats[2], count=10, around=24)
    return [ball, k.smooth(core, 70)]


# --- Build ---------------------------------------------------------------------------------------------------------

def triangulate(objects):
    """Every face split into triangles (the same split every run, the custom normals kept; polish_k_pod.py)."""
    for obj in objects:
        mod = obj.modifiers.new("triangulate", "TRIANGULATE")
        mod.quad_method = "BEAUTY"
        mod.ngon_method = "BEAUTY"
        mod.min_vertices = 4
        mod.keep_custom_normals = True
        mk.apply(obj)
    return objects


def join(objects, name):
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.join()
    obj = bpy.context.view_layer.objects.active
    obj.name = obj.data.name = name
    return obj


def bone_mask(sheet):
    """The sprite's bone pixels (ramp 10 and the bone's highlights 0x1c, 0x1d)."""
    from sprite_profile import sprite_indices
    return [[v is not None and (v >> 4 == 0xa or v in (0x1c, 0x1d)) for v in row] for row in sprite_indices(sheet, 39)]


def build():
    options = k.args()
    out = mk.outdir(options)
    only = set(options["only"].split(",")) if "only" in options else None
    sheet = None
    if "check" in options:
        sheets = options["check"]
        sheet = os.path.join(sheets, "enemy_H.png") if os.path.isdir(sheets) else sheets
    for frame in FRAMES:
        name, sprite = frame[0], frame[1]
        if only is not None and name not in only:
            continue
        k.reset()
        m = materials()
        eye_mats, pit_rim = frame_materials(frame)
        ring_ = [ring(m)]
        paint_bone(ring_, m)
        parts = [slab(m, pit_rim)] + ring_ + eye(eye_mats, frame)
        triangulate(parts)
        if sheet and frame is FRAMES[0]:
            mk.compare("%s's ring (bone pixels)" % name, mk.coverage(ring_, 24, 28), bone_mask(sheet))
        model = join(parts, name)
        bpy.context.scene.view_settings.view_transform = "Standard"
        if sheet:
            mk.compare("%s (H %d)" % (name, sprite), mk.coverage([model], 24, 28), k.sprite_mask(sheet, sprite))
        mk.report(name, [model], os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, [model])


if __name__ == "__main__":
    build()
