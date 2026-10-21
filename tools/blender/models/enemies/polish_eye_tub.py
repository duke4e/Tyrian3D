"""The bronze eye tub of the asteroid levels (sheet D sprite 193, 2x2: 24 x 28 pixels; ground layer; ASTEROID1,
ASTEROID2, ASTCITY, AST. CITY and AST ROCK, enemy 273 of episodes 1, 2, 3 and 5), polished (2026-10-21; it replaces
wave3_j.py's eye_tub(), an upright column with hoops and petals of single faces, and wave3_at_d.py's frame models
built from it). Its animation runs all the time: 193 195 197 199 201 203 205 207 169 207 205 203 201 199 197 195
193 193 193 193 (its iris opens on the eye, the eye lights up and dims, the iris shuts and stays shut a while).

models.cfg: model eye_tub_199 enemies/eye_tub_199.glb and model eye_tub_203 enemies/eye_tub_203.glb (new), the
frame lines frame d 199 eye_tub_199 and frame d 203 eye_tub_203 (for the old eye_tub_201 ones; their front shutter
stands a pixel lower and higher than 201's); the other lines stay: sprite d 193 eye_tub yaw=0 (eye_tub is 169, the
eye fully lit), frame d 193 eye_tub_193 ... frame d 207 eye_tub_207. No other enemy shows sheet D's 169 or 193-207.
No frame is another's pixels mirrored or in other ramps; the tub itself (all but the opening and the front
shutter's window) is the same pixels in all of them.

As the sprites and their 4x upscales draw it (the grey stone tiles round it, columns 0-1 and 22-23 and rows 24-27,
are the map's ground, drawn into the sprite, and left out here): a tub of bronze staves (ramp 1) seen from the front
and above, its mouth at the top (rows 0-15: a rounded rim, columns 1-21, round the opening, columns 4-17 of rows
2-14), its front wall below (rows 15-23, the bottom rounded), dark seams between the staves (columns 8 and 14 on the
front, running over the rim; on the rim's sides at row 7). On the front stave (columns 8-13) a lit band under the
rim (rows 15-17) over a shutter (rows 18-23). The frames: 193 the iris shut, four grey petals meeting in a low dome,
a cross of seams between them; 195 and 197 the petals sliding apart along the diagonals (the cross 3 and 5 pixels
wide), the dark inside showing; 199-203 only the petals' tips left at the rim on the diagonals, the inside a dark
housing of four faces (lit at the left, darker at the right) between the black arms of an X, the eye dark where the
arms cross; meanwhile the shutter rises a pixel a frame (its lower edge at rows 23, 22, 21, 20 and 19 in 193-197,
199, 201, 203 and 205-169) on a window at the tub's foot, a red lamp in it that lights in 203; 205, 207 and 169 the
eye lighting up from a small diamond (205) to a white-hot heart (207) and a big glowing orb (169), the lamp with it.

The sprite draws the tub from about 45 degrees above the horizon; the game's camera looks 20 degrees from straight
down. So the tub leans back up the screen (LEAN, 22 degrees) as the polished machines' oblique parts do
(polish_core_machine.py, polish_green_tower.py): seen from straight above it covers the sprite's outline, and the
game's camera sees its mouth and its front wall as the sprite draws them (the mouth 21 x 15 pixels, the wall 8.5
pixels high). It stands on the floor (its foot cut by z = 0), 12 pixels high at the mouth's front.

Built in the tub's own frame (u across, v from front to back across the mouth, w up its axis; TUB_FRAME turns it
into place): the tub a loft round its axis, its cross-section a superellipse (squarer than a circle, as the sprite's
outline), up the outer wall, over a rolled rim and down the inner wall to a dark floor, six staves with grooves
between them along the outside and over the rim; the window cut into the front stave with an exact boolean, the lamp
a red glass plate in it, the shutter, its dark lip and the band over it plates following the wall; the iris four
petals, each a quarter of the opening domed with the others and pillowed along its seams, slid out along its
diagonal (0, 1, 2 and 4.5 pixels) and clipped by the opening (their rest is under the rim); the housing four dark
faces sloping up to the middle between the X's arms (gaps down to the floor), the eye a red glass ball where they
meet, its heat in bands of the sprites' shades round the point facing the game's camera (polish_orb_red.band_split),
glowing well under 1 (the game's bloom adds to it; no glow option: it would light the floor round the tub when the
eye is dark). Colours are the sprites' own indices: the bronze 0x15-0x19 (the wall 0x16, the lightest of the sprite's
front, 0x12-0x16: in the game the tub's own glowing shots and the ship's lamp light it, and lighter it read orange
beside the 2D sprite's dark bronze), the seams and the shutter's lip 0x11, the petals 0x0a
and 0x05, the housing 0x05, the inside 0x01, the eye and the lamp ramp 7. One model per frame; the tub is the same
in all of them, so they share their bounds.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the ground (z = 0); origin at
the sprite's centre (pixel 12, 14): column c's left edge is x = c - 12, row r's top edge y = 14 - r.

Replaces wave3_j.py's eye_tub() (its "D 193: the eye tub" section, the @model("eye_tub", [(D, 193, True)])
registration, and the eye_tub lines of its docstring) and wave3_at_d.py's eye tub (its "The eye tub's iris" section:
TUB, TUB_H, IRIS_R, petal_poly(), iris(), eye_tub(), TUB_FRAMES and the loop registering eye_tub_<sprite>, and the
eye_tub lines of its docstring; its shell ship stays, it uses wave3_j's shell_ship()); wave3_j_art.py's D193 and D169
are read by nothing. Remove them so that they don't overwrite these models.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each frame's silhouette
against the tub's own pixels, the map's tiles round it left out), --preview <prefix>, --only <name,...>.
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_orb_red import band_split  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402

# --- The tub's frame ------------------------------------------------------------------------------------------------
LEAN = math.radians(22.0)       # how far the tub leans back up the screen
FOOT = (-0.5, 0.8)              # where its axis meets the floor (x, y): columns 1-21, rows 0-23 from above
MOUTH = 8.7                     # the mouth's plane, up the axis from the foot
E_U = Vector((1.0, 0.0, 0.0))
E_V = Vector((0.0, math.cos(LEAN), -math.sin(LEAN)))
E_W = Vector((0.0, math.sin(LEAN), math.cos(LEAN)))
TUB_FRAME = Matrix(((E_U.x, E_V.x, E_W.x, FOOT[0]), (E_U.y, E_V.y, E_W.y, FOOT[1]), (E_U.z, E_V.z, E_W.z, 0.0),
                    (0.0, 0.0, 0.0, 1.0)))
CAMERA = TUB_FRAME.to_3x3().inverted() @ Vector((0.0, -math.sin(math.radians(20)), math.cos(math.radians(20))))

# The cross-section: a superellipse (power) of the outer wall's radii (u, v), the opening's (the inner wall's).
POWER = 3.2
OUTER = (10.3, 10.0)
INNER = (7.3, 8.3)
SEGMENTS = 120
# The profile up the outer wall, over the rim and down the inner wall: (from outer (0) to inner (1), pushed out,
# up the axis from the mouth's plane); the floor's height under the mouth.
RIM = [(0.0, 0.0, -1.05), (0.0, 0.3, -0.62), (0.0, 0.33, -0.22), (0.09, 0.15, 0.18), (0.3, 0.0, 0.38),
       (0.55, 0.0, 0.36), (0.8, 0.0, 0.22), (0.95, 0.0, -0.05), (1.0, 0.0, -0.45)]
FLOOR = MOUTH - 4.5
# The staves: the seams' angles (the front pair and the back pair at u = -3 and 3, the sides), their groove's
# half-width (degrees) and depth.
SEAM_U = 3.0
SEAM_HALF, SEAM_DEPTH = 1.7, 0.3

# The front: the window (u half-width; its top up the axis), the lamp's depth in it; the shutter (u half-width, its
# top), its lip; the band over it (u half-width, from w to w, how proud).
WINDOW_HALF, WINDOW_TOP, WINDOW_DEPTH = 2.25, 1.05, 0.7
SHUTTER_HALF, SHUTTER_TOP = 2.75, 4.7
LIP = 0.55
BAND = (3.0, 4.35, 7.55, 0.55)
# The shutter's lower edge in the frames (along the front stave from the floor, 0, to the rim, 1).
SHUTTER = {"down": 0.0, 199: 0.105, 201: 0.22, 203: 0.34, "up": 0.457}

# The iris: the petals' seam (half the cross's width when shut), the dome (its outer edge under the rim, its rise to
# the middle), the petals' thickness.
PETAL_SEAM, PETAL_EDGE, PETAL_DOME, PETAL_THICK = 0.35, MOUTH - 0.55, 1.5, 0.65
PETAL_ROUND, PETAL_ROUND_REACH = 0.45, 1.3   # how far each petal's edges along the seams are rounded down
# The housing: its middle and its foot at the inner wall (up the axis), the X's arms' width.
HOUSING_TOP, HOUSING_FOOT, ARM = MOUTH - 1.3, MOUTH - 3.6, 1.7
# The eye: up the axis, radii (u; v follows the opening; w).
EYE_W, EYE_R, EYE_RW = MOUTH - 1.6, 3.3, 1.7

# The frames: model, sprite, how far the petals have slid out (u), the shutter, the eye's bands ((lowest heat,
# palette index, glow); one band: dark), the lamp's (index, glow).
DARK_EYE = [(-9.0, 0x70, 0.0)]
FRAMES = [
    ("eye_tub_193", 193, 0.0, "down", DARK_EYE, (0x70, 0.0)),
    ("eye_tub_195", 195, 1.0, "down", DARK_EYE, (0x70, 0.0)),
    ("eye_tub_197", 197, 2.0, "down", DARK_EYE, (0x70, 0.0)),
    ("eye_tub_199", 199, 4.5, 199, DARK_EYE, (0x70, 0.0)),
    ("eye_tub_201", 201, 4.5, 201, DARK_EYE, (0x70, 0.0)),
    ("eye_tub_203", 203, 4.5, 203, DARK_EYE, (0x70, 0.12)),
    ("eye_tub_205", 205, 4.5, "up", [(-9.0, 0x70, 0.0), (0.8, 0x72, 0.15), (0.9, 0x75, 0.3), (0.96, 0x7a, 0.5)],
     (0x72, 0.15)),
    ("eye_tub_207", 207, 4.5, "up", [(-9.0, 0x71, 0.05), (0.55, 0x74, 0.2), (0.75, 0x77, 0.35), (0.88, 0x7a, 0.5),
                                     (0.96, 0x7e, 0.6)], (0x74, 0.2)),
    ("eye_tub", 169, 4.5, "up", [(-9.0, 0x73, 0.12), (0.35, 0x76, 0.25), (0.62, 0x79, 0.4), (0.84, 0x7c, 0.5),
                                 (0.95, 0x7f, 0.6)], (0x76, 0.25)),
]

# The tub's own pixels (the map's tiles round it left out), by rows: (first row, last row, first column, last column).
OWN = [(0, 0, 6, 16), (1, 1, 4, 18), (2, 2, 3, 19), (3, 3, 2, 20), (4, 19, 1, 21), (20, 20, 2, 20), (21, 21, 3, 19),
       (22, 22, 4, 18), (23, 23, 5, 17)]


def own_mask():
    mask = [[False] * 24 for _ in range(28)]
    for r0, r1, c0, c1 in OWN:
        for r in range(r0, r1 + 1):
            for c in range(c0, c1 + 1):
                mask[r][c] = True
    return mask


# --- Superellipses --------------------------------------------------------------------------------------------------

def unit(phi):
    """The point at angle phi (radians) on the unit superellipse of POWER."""
    return mk.superellipse_point(phi, POWER)


def inside(u, v, radii, grow=0.0):
    return (abs(u) / (radii[0] + grow)) ** POWER + (abs(v) / (radii[1] + grow)) ** POWER < 1.0


def boundary_hit(origin, direction, radii, reach=30.0):
    """Where the ray from origin (inside) along direction leaves the superellipse of radii."""
    lo, hi = 0.0, reach
    for _ in range(50):
        mid = (lo + hi) / 2
        p = origin + direction * mid
        if inside(p.x, p.y, radii):
            lo = mid
        else:
            hi = mid
    return origin + direction * lo


def boundary_angle(p, radii):
    """The superellipse parameter of a point on its boundary."""
    x, y = p.x / radii[0], p.y / radii[1]
    return math.atan2(math.copysign(abs(y) ** (POWER / 2), y), math.copysign(abs(x) ** (POWER / 2), x))


def wall_normal(u, v, radii):
    nu = POWER * abs(u) ** (POWER - 1) / radii[0] ** POWER
    nv = POWER * abs(v) ** (POWER - 1) / radii[1] ** POWER
    n = Vector((math.copysign(nu, u), math.copysign(nv, v)))
    return n.normalized()


def floor_w(v):
    """How far up the axis the floor (z = 0) is at v (the tub leans back: lower at the front)."""
    return v * math.tan(LEAN)


# --- Materials ------------------------------------------------------------------------------------------------------

def materials(frame):
    glow = k.level_palette()
    _, _, _, _, eye_bands, lamp = frame

    def mat(name, index, metallic=0.55, roughness=0.36):
        return k.material(name, palette=index, metallic=metallic, roughness=roughness)

    def lit(name, index, strength, roughness=0.22):
        if strength <= 0:  # unlit: dark glass, its shine dulled (the sprites draw it near black)
            return k.material(name, palette=index, metallic=0.2, roughness=0.5)
        return k.material(name, palette=index, metallic=0.0, roughness=roughness, emission=glow[index],
                          emission_strength=strength)
    m = {
        "wall": mat("tub_wall", 0x16, metallic=0.3, roughness=0.45),
        "rim": mat("tub_rim", 0x19, roughness=0.3),
        "seam": mat("tub_seam", 0x11, roughness=0.5),
        "band": mat("tub_band", 0x18, roughness=0.3),
        "shutter": mat("tub_shutter", 0x15, metallic=0.35, roughness=0.42),
        "inside": mat("tub_inside", 0x01, metallic=0.3, roughness=0.7),
        "housing": mat("tub_housing", 0x05, metallic=0.45, roughness=0.34),
        "petal": mat("tub_petal", 0x0a, metallic=0.65, roughness=0.28),
        "petal_side": mat("tub_petal_side", 0x05, metallic=0.6, roughness=0.35),
    }
    bands = []
    for lowest, index, strength in eye_bands:
        key = ("lit", index, strength)
        if key not in m:
            m[key] = lit(f"tub_eye_{index:x}_{int(round(strength * 100))}", index, strength)
        bands.append((lowest, m[key]))
    m["eye_bands"] = bands
    key = ("lit", lamp[0], lamp[1])
    if key not in m:
        m[key] = lit(f"tub_eye_{lamp[0]:x}_{int(round(lamp[1] * 100))}", lamp[0], lamp[1])
    m["lamp"] = m[key]
    return m


# --- Mesh building --------------------------------------------------------------------------------------------------

def build_mesh(name, verts, faces, mats, face_mats):
    """A mesh object from vertices, faces and each face's material (an index into mats)."""
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata([tuple(v) for v in verts], [], faces)
    for mt in mats:
        mesh.materials.append(mt)
    for poly, mi in zip(mesh.polygons, face_mats):
        poly.material_index = mi
    mesh.validate()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    k.recalc_normals(obj)
    return obj


def seam_angles():
    """The seams' angles: where the outer wall is at u = -SEAM_U and SEAM_U, front and back, and the sides."""
    c = (SEAM_U / OUTER[0]) ** (POWER / 2)  # |cos phi| there
    a = math.acos(c)
    return sorted({0.0, math.pi, a, math.pi - a, math.pi + a, 2 * math.pi - a})


def angles():
    """The loft's angles round the axis: even steps, and three at each seam (its groove's two edges and middle)."""
    seams = seam_angles()
    half = math.radians(SEAM_HALF)
    out = []
    for i in range(SEGMENTS):
        a = 2 * math.pi * i / SEGMENTS
        if all(abs((a - s + math.pi) % (2 * math.pi) - math.pi) > half * 1.6 for s in seams):
            out.append((a, False))
    for s in seams:
        out += [((s - half) % (2 * math.pi), False), (s % (2 * math.pi), True), ((s + half) % (2 * math.pi), False)]
    return sorted(out)


def tub(m):
    """The tub: up the outer wall from the floor, over the rim, down the inner wall to the dark floor; grooves at the
    seams along the outer wall and over the rim."""
    ring_angles = angles()
    n = len(ring_angles)
    mats = [m["wall"], m["rim"], m["seam"], m["inside"]]
    profile = [(0.0, 0.0, None)] + RIM + [(1.0, 0.0, FLOOR - MOUTH)]
    rings = []
    for li, (lam, push, dw) in enumerate(profile):
        ring = []
        for a, seam in ring_angles:
            cu, cv = unit(a)
            ru = OUTER[0] + lam * (INNER[0] - OUTER[0]) + push
            rv = OUTER[1] + lam * (INNER[1] - OUTER[1]) + push
            w = None if dw is None else MOUTH + dw
            if seam and lam < 0.5:  # the groove: into the outer wall, down into the rim
                if li <= 1:
                    ru, rv = ru - SEAM_DEPTH, rv - SEAM_DEPTH
                else:
                    w -= SEAM_DEPTH
            u, v = ru * cu, rv * cv
            if w is None:
                w = floor_w(v)
            ring.append((u, v, w))
        rings.append(ring)
    verts = [p for ring in rings for p in ring]
    faces, face_mats = [], []
    seam_of = [s for _, s in ring_angles]
    for i in range(len(rings) - 1):
        lam = profile[i][0]
        for j in range(n):
            jj = (j + 1) % n
            faces.append((i * n + j, i * n + jj, (i + 1) * n + jj, (i + 1) * n + j))
            on_seam = (seam_of[j] or seam_of[jj]) and lam < 0.5 and i < len(rings) - 2
            if on_seam:
                face_mats.append(2)
            elif i == 0:
                face_mats.append(0)
            elif i < len(rings) - 2:
                face_mats.append(1)
            else:
                face_mats.append(3)
    # The foot (on the floor) and the dark floor inside, closed by fans to the axis.
    verts.append((0.0, 0.0, 0.0))
    foot = len(verts) - 1
    faces += [((j + 1) % n, j, foot) for j in range(n)]
    face_mats += [0] * n
    verts.append((0.0, 0.0, FLOOR))
    middle = len(verts) - 1
    last = (len(rings) - 1) * n
    faces += [(last + j, last + (j + 1) % n, middle) for j in range(n)]
    face_mats += [3] * n
    body = build_mesh("tub", verts, faces, mats, face_mats)
    # The window at the foot of the front stave.
    v_front = -OUTER[1]
    cutter = mk.box("window_cut", -WINDOW_HALF, WINDOW_HALF, v_front - 2.0, v_front + WINDOW_DEPTH,
                    floor_w(v_front) + 0.3, WINDOW_TOP, m["inside"])
    mk.boolean(body, cutter, "DIFFERENCE")
    k.smooth(body, 40)
    return body


def wall_point(u, w, offset, radii=OUTER):
    """The point on the tub's front wall at u, w, `offset` out from it (along its normal)."""
    f = 1.0 - (abs(u) / radii[0]) ** POWER
    v = -radii[1] * max(f, 0.0) ** (1.0 / POWER)
    n = wall_normal(u, v, radii)
    return Vector((u + n.x * offset, v + n.y * offset, w))


def wall_slab(name, u0, u1, w0, w1, off0, off1, mat, nu=12, nw=8, bottom=None):
    """A plate on the front wall: from u0 to u1, from w0 (or bottom(u), whichever is higher) to w1, between `off0`
    and `off1` out from the wall."""
    verts, faces = [], []
    grid = []
    for side, off in enumerate((off0, off1)):
        layer = []
        for i in range(nu + 1):
            u = u0 + (u1 - u0) * i / nu
            lo = max(w0, bottom(u)) if bottom else w0
            col = []
            for j in range(nw + 1):
                w = lo + (w1 - lo) * j / nw
                verts.append(wall_point(u, w, off))
                col.append(len(verts) - 1)
            layer.append(col)
        grid.append(layer)
    inner, outer = grid
    for i in range(nu):
        for j in range(nw):
            faces.append((outer[i][j], outer[i + 1][j], outer[i + 1][j + 1], outer[i][j + 1]))
            faces.append((inner[i][j], inner[i][j + 1], inner[i + 1][j + 1], inner[i + 1][j]))
    for i in range(nu):  # the bottom and top edges
        faces.append((inner[i][0], inner[i + 1][0], outer[i + 1][0], outer[i][0]))
        faces.append((inner[i][nw], outer[i][nw], outer[i + 1][nw], inner[i + 1][nw]))
    for j in range(nw):  # the sides
        faces.append((inner[0][j], outer[0][j], outer[0][j + 1], inner[0][j + 1]))
        faces.append((inner[nu][j], inner[nu][j + 1], outer[nu][j + 1], outer[nu][j]))
    return build_mesh(name, verts, faces, [mat], [0] * len(faces))


def stave_w(t):
    """Up the axis at t along the front stave (0 at the floor, 1 at the mouth's plane)."""
    w0 = floor_w(-OUTER[1])
    return w0 + (MOUTH - w0) * t


def front(m, shutter):
    """The band under the rim, the shutter (its lower edge at `shutter` along the stave) with its dark lip, the lamp
    in the window."""
    half, w0, w1, proud = BAND
    band = wall_slab("band", -half, half, w0, w1, -0.2, proud, m["band"])
    mk.bevel(band, 0.22, 2, 30)
    edge = stave_w(SHUTTER[shutter])

    def ground(u):
        return floor_w(wall_point(u, 0.0, 0.0).y) + 0.18
    plate = wall_slab("shutter", -SHUTTER_HALF, SHUTTER_HALF, edge + LIP * 0.6, SHUTTER_TOP, -0.15, 0.22,
                      m["shutter"], bottom=ground)
    lip = wall_slab("shutter_lip", -SHUTTER_HALF, SHUTTER_HALF, edge, edge + LIP, -0.12, 0.3, m["seam"], nw=2,
                    bottom=ground)
    for part in (plate, lip):
        mk.bevel(part, 0.08, 1, 30)
    deep = -WINDOW_DEPTH - 0.3
    lamp = wall_slab("lamp", -WINDOW_HALF - 0.2, WINDOW_HALF + 0.2, floor_w(-OUTER[1]), WINDOW_TOP + 0.2, deep,
                     -WINDOW_DEPTH + 0.05, m["lamp"], bottom=lambda u: floor_w(wall_point(u, 0.0, deep).y) + 0.06)
    parts = [band, plate, lip, lamp]
    for p in parts:
        k.smooth(p, 40)
    return parts


# --- The iris -------------------------------------------------------------------------------------------------------

def fan_patch(name, corner, arc, top, bottom, mats, pick, steps=6):
    """A closed plate over the region between a corner and an arc of points (seen from the corner it is star-shaped):
    its top at top(u, v), its bottom flat at `bottom`; pick(centre, normal) chooses each face's material (an index)."""
    rows = []
    verts = [Vector((corner.x, corner.y, top(corner.x, corner.y)))]
    apex_top = 0  # the corner's top
    for a in arc:
        row = []
        for i in range(1, steps + 1):
            p = corner.lerp(a, i / steps)
            verts.append(Vector((p.x, p.y, top(p.x, p.y))))
            row.append(len(verts) - 1)
        rows.append(row)
    verts.append(Vector((corner.x, corner.y, bottom)))
    apex_bottom = len(verts) - 1
    low = [len(verts) + i for i in range(len(arc))]
    verts += [Vector((a.x, a.y, bottom)) for a in arc]
    faces = []
    for j in range(len(arc) - 1):
        r0, r1 = rows[j], rows[j + 1]
        faces.append((apex_top, r0[0], r1[0]))
        for i in range(steps - 1):
            faces.append((r0[i], r0[i + 1], r1[i + 1], r1[i]))
        faces.append((r0[-1], low[j], low[j + 1], r1[-1]))   # the outer side, down to the bottom
        faces.append((low[j], apex_bottom, low[j + 1]))      # the bottom
    # The two straight sides.
    first, last = rows[0], rows[-1]
    faces.append(tuple([apex_bottom, apex_top] + first + [low[0]]))
    faces.append(tuple([apex_top, apex_bottom, low[-1]] + list(reversed(last))))
    obj = build_mesh(name, verts, faces, mats, [0] * len(faces))
    for poly in obj.data.polygons:
        poly.material_index = pick(poly.center, poly.normal)
    return obj


def petals(m, slide):
    """The four petals slid out by `slide` (u; v follows the opening's shape) along their diagonals, clipped by the
    opening; domed together (low at the rim, highest where they meet)."""
    out = []
    clip = (INNER[0] - 0.12, INNER[1] - 0.12)
    for i, (su, sv) in enumerate(((1, 1), (-1, 1), (-1, -1), (1, -1))):
        shift = Vector((su * slide, sv * slide * INNER[1] / INNER[0]))
        corner = shift + Vector((su * PETAL_SEAM, sv * PETAL_SEAM))
        if not inside(corner.x, corner.y, clip, -0.3):
            continue
        a = boundary_hit(corner, Vector((su, 0.0)), clip)
        b = boundary_hit(corner, Vector((0.0, sv)), clip)
        pa, pb = boundary_angle(a, clip), boundary_angle(b, clip)
        d = (pb - pa + math.pi) % (2 * math.pi) - math.pi
        count = max(6, int(abs(d) / math.radians(4)))
        arc = []
        for j in range(count + 1):
            cu, cv = unit(pa + d * j / count)
            arc.append(Vector((clip[0] * cu, clip[1] * cv)))
        arc[0], arc[-1] = a, b

        def top(u, v, shift=shift, corner=corner):
            q = ((abs(u - shift.x) / INNER[0]) ** POWER + (abs(v - shift.y) / INNER[1]) ** POWER) ** (1 / POWER)
            # Each petal's edges along the seams rounded down (pillowed, as the upscale draws them).
            edge = min(abs(u - corner.x), abs(v - corner.y))
            round_off = PETAL_ROUND * (1.0 - min(1.0, edge / PETAL_ROUND_REACH)) ** 2
            return PETAL_EDGE + PETAL_DOME * max(0.0, 1.0 - q * q) - round_off
        if d < 0:  # keep the arc counter-clockwise round the corner
            arc = arc[::-1]
        petal = fan_patch(f"petal{i}", corner, arc, top, PETAL_EDGE - PETAL_THICK,
                          [m["petal"], m["petal_side"], m["inside"]],
                          lambda c, nrm: 0 if nrm.z > 0.75 else 1 if nrm.z > -0.5 else 2)
        k.smooth(petal, 35)
        out.append(petal)
    return out


# --- The housing and the eye ----------------------------------------------------------------------------------------

def housing(m):
    """Four dark faces sloping up from the inner wall to the middle, between the X's arms (gaps down to the floor)."""
    out = []
    diag = Vector((INNER[0], INNER[1])).normalized()
    wall = (INNER[0] - 0.05, INNER[1] - 0.05)
    for i, (axis, sign) in enumerate((("u", -1), ("v", 1), ("u", 1), ("v", -1))):
        # The face between the two diagonals round its axis, each edge ARM / 2 in from its diagonal.
        if axis == "u":
            d1, d2 = Vector((sign * diag.x, -diag.y)), Vector((sign * diag.x, diag.y))
            out_dir = Vector((sign, 0.0))
        else:
            d1, d2 = Vector((diag.x, sign * diag.y)), Vector((-diag.x, sign * diag.y))
            out_dir = Vector((0.0, sign))
        n1 = Vector((-d1.y, d1.x))
        n2 = Vector((-d2.y, d2.x))
        if n1.dot(out_dir) < 0:
            n1 = -n1
        if n2.dot(out_dir) < 0:
            n2 = -n2
        # The corner where the two inset edges meet: c . n1 = c . n2 = ARM / 2.
        det = n1.x * n2.y - n1.y * n2.x
        h = ARM / 2
        corner = Vector(((h * n2.y - n1.y * h) / det, (n1.x * h - h * n2.x) / det))
        a = boundary_hit(corner, d1, wall)
        b = boundary_hit(corner, d2, wall)
        pa, pb = boundary_angle(a, wall), boundary_angle(b, wall)
        d = (pb - pa + math.pi) % (2 * math.pi) - math.pi
        count = max(8, int(abs(d) / math.radians(4)))
        arc = [a] + [Vector((wall[0] * unit(pa + d * j / count)[0], wall[1] * unit(pa + d * j / count)[1]))
                     for j in range(1, count)] + [b]
        if d < 0:
            arc = arc[::-1]
        reach = INNER[0] if axis == "u" else INNER[1]
        slope = (HOUSING_TOP - HOUSING_FOOT) / reach

        def top(u, v, axis=axis, slope=slope):
            return HOUSING_TOP - slope * abs(u if axis == "u" else v)
        face = fan_patch(f"housing{i}", corner, arc, top, FLOOR - 0.3, [m["housing"], m["inside"]],
                         lambda c, nrm: 0 if nrm.z > 0.6 else 1)
        k.smooth(face, 30)
        out.append(face)
    return out


def eye(m):
    """The eye where the housing's faces meet: a red glass ball, its heat in bands round the point facing the
    game's camera."""
    radii = (EYE_R, EYE_R * INNER[1] / INNER[0], EYE_RW)
    ball = mk.ball("eye", (0.0, 0.0, EYE_W), radii, m["eye_bands"][0][1], 40, 20)
    bands = m["eye_bands"]
    if len(bands) > 1:
        def heat(p):
            n = Vector((p.x / radii[0], p.y / radii[1], (p.z - EYE_W) / radii[2])).normalized()
            return n.dot(CAMERA)
        band_split(ball, [heat(v.co) for v in ball.data.vertices], bands)
    k.smooth(ball, 80)
    return [ball]


# --- Build ----------------------------------------------------------------------------------------------------------

def build_frame(frame, options):
    name, sprite, slide, shutter, _, _ = frame
    k.reset()
    m = materials(frame)
    parts = [tub(m)] + front(m, shutter) + petals(m, slide) + housing(m) + eye(m)
    for obj in parts:
        obj.data.transform(TUB_FRAME)
        obj.data.update()
    parts = triangulate(parts)
    bpy.context.view_layer.update()
    if "check" in options:
        mk.compare("%s (D %d)" % (name, sprite), mk.coverage(parts, 24, 28), own_mask())
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    mk.report(name, parts, os.path.join(mk.outdir(options), name + ".glb"))
    if "preview" in options:
        mk.preview(options["preview"] + name, parts, distance=0.6)


def build():
    options = k.args()
    only = options["only"].split(",") if "only" in options else [f[0] for f in FRAMES]
    for frame in FRAMES:
        if frame[0] in only:
            build_frame(frame, options)


if __name__ == "__main__":
    build()
