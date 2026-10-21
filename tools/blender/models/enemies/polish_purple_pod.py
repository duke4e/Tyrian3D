"""The purple pod of HARVEST and LAVA RUN with a red strap and a golden clasp (sheet 5 sprite 47, 2x2: 24 x 28 pixels;
enemies 71 (top layer, both levels' events; the catalogue also lists it in the sky) and 72 (dropped) of episode 4; its
animation 47 999: it shows 47 until it is gone, so no frame models), polished (2026-10-21; it replaces wave1_c.py's
purple_pod(), an ellipsoid in two halves with a lathed strap and a box for a clasp). models.cfg: model purple_pod
enemies/purple_pod.glb; sprite 5 47 purple_pod yaw=0 (both unchanged). No other sprite has its pixels mirrored, turned
or in other ramps, and no other enemy shows it.

As the sprite and its 4x upscale draw it: an oval pod (columns 0-23 of rows 0-26, its middle at row 13: 24 x 27
pixels) of glossy purple (ramp 5), the upper half lit (0x55-0x58), a soft white glare above its middle (columns 10-12
of rows 4-7, 0x5a-0x5d), the edges dark (0x50-0x53); the lower half in shade (0x50-0x53), a lighter crescent along its
lower right rim (columns 17-21 of rows 18-24, 0x57-0x5a) and its bottom a little lighter (0x55-0x56). Across its
middle (rows 11-16) a strap of dark crimson leather (ramp 15: 0xf1-0xf4, lighter along its upper edge either side of
the clasp, 0xf5-0xf7, darker where it turns away at the sides), a dark line along both its edges (rows 10 and 17); in
its middle the clasp: a golden bar across the strap (columns 11-12 of rows 11-16: 0xfa, darker 0xf9 below, a light
0xfb at its foot), a pale glint at its upper end (0x5e). Seen from above the strap crosses the pod, so it runs round
the pod's axis up the screen, and the clasp sits on top.

Built for the game's camera (20 degrees off straight down, from the bottom of the screen; VIEW_TILT): the pod, its
strap and its clasp are built as the sprite draws them seen from straight above, then turned about the x axis through
the pod's middle by VIEW_TILT, so the camera sees them where the sprite draws them (the strap across the middle, the
glare above it), as polish_dark_orb.py paints its face. The shell is an even ellipsoid (an icosphere, finer round the
glare) cut along smooth contours into its painted parts (polish_machine_kit's split_along): the dark rim where it turns
away from the camera, the lower half's shade, the crescent, the glare; the parts glow a little in their own colours
(0.12-0.3: a ball seen by the slanted camera shows mostly its side away from the sun and reads near black; the game's
bloom adds). The strap is a band lofted round the shell, standing out of it with rounded edges, a thin dark seam sunk
into the shell along each of its edges (rows 10 and 17); the clasp a rounded bar lying on it with a stud at its upper
end. The pod flies: the game centres
it in height (its middle is the origin's height).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; origin at the
sprite's centre (pixel 12, 14): column c is x = c + 0.5 - 12, row r is y = 13.5 - r. The pod's middle is (0, 0.5);
the strap spans y -3 .. 3 (rows 11-16) before the turn.

Replaces wave1_c.py's purple_pod(): wave1_c.py holds nothing else (its MODELS table has only "purple_pod", and its
ellipsoid_part() helper only purple_pod() uses), so the whole file can go. Nothing imports wave1_c (polish_orb_crimson.py
only mentions it in its docstring: "(purple_pod() and the others use them)", about helpers it no longer has).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouette against
enemy_5.png), --preview <prefix>.
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
from polish_machine_kit import k, smoothstep, split_along  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402

NAME = "purple_pod"
VIEW_TILT = 20.0
CENTRE = Vector((0.0, 0.5, 0.0))
# The shell's radii before the turn (y a little longer: turned, the pod spans rows 0-26 seen from above).
RADII = Vector((11.85, 13.75, 10.0))

# The strap (before the turn): its edges (y), how far it stands out of the shell, the power of its cross-section
# (flat top, rounded edges); the dark seams along its edges (rows 10 and 17): how far beyond the edges they lie, their
# radius and how deep they are sunk into the shell.
STRAP_Y = (-3.0, 3.0)
STRAP_OUT = 0.55
STRAP_POWER = 4.0
STRAP_SEGMENTS = 72
SEAM_OUT, SEAM_R, SEAM_SINK = 0.4, 0.42, 0.2
# Where the strap turns away (degrees round the pod's axis from straight up): darker beyond SIDE; its upper edge
# lighter (t above LIGHT_T) within LIGHT_A of the top.
SIDE = 58.0
LIGHT_T, LIGHT_A = 0.6, 34.0

# The clasp: its half-width, its ends (y), how far it stands over the strap, its half-thickness; the stud at its upper
# end (y, radii).
CLASP_HW = 1.05
CLASP_Y = (-3.1, 3.1)
CLASP_UP, CLASP_HALF = 0.5, 0.45
STUD = (2.45, (0.75, 0.62, 0.42))

# The shell's painted parts (the fields of the direction d from its middle, before the turn): the dark rim where the
# surface turns away from the camera (its normal's z below RIM); the lower half's shade (y below LOWER, blended over
# LOWER_W); the crescent along the lower right rim (round the angle CRESCENT_AT in the top view, CRESCENT_SPREAD
# either side, where the normal's z is about CRESCENT_Z) and the lighter bottom (round BOTTOM_AT); the glare (its
# middle and half-sizes in the top view: columns 10-12 of rows 4-7).
RIM = 0.26
LOWER, LOWER_W = -4.2, 1.6
CRESCENT_AT, CRESCENT_SPREAD = -48.0, 34.0
CRESCENT_Z, CRESCENT_WIDTH = 0.5, 0.16
BOTTOM_AT, BOTTOM_SPREAD = -95.0, 30.0
GLARE, GLARE_SIZE = Vector((-0.8, 7.7)), Vector((3.3, 2.4))


def materials():
    pal = k.level_palette()

    def mat(name, index, strength=0.0, metallic=0.15, roughness=0.3):
        if strength > 0:
            return k.material(name, palette=index, metallic=metallic, roughness=roughness, emission=pal[index],
                              emission_strength=strength)
        return k.material(name, palette=index, metallic=metallic, roughness=roughness)
    return {
        "shell": mat("ppod_shell", 0x57, 0.22),
        "lower": mat("ppod_lower", 0x55, 0.3),
        "rim": mat("ppod_rim", 0x53, 0.25, roughness=0.35),
        "seam": mat("ppod_seam", 0x51, 0.0, roughness=0.5),
        "crescent": mat("ppod_crescent", 0x59, 0.3, roughness=0.25),
        "glare": mat("ppod_glare", 0x59, 0.15, roughness=0.18),
        "glare_mid": mat("ppod_glare_mid", 0x5a, 0.18, roughness=0.15),
        "glare_core": mat("ppod_glare_core", 0x5c, 0.2, roughness=0.12),
        "strap": mat("ppod_strap", 0xf4, 0.12, metallic=0.05, roughness=0.55),
        "strap_side": mat("ppod_strap_side", 0xf2, 0.1, metallic=0.05, roughness=0.55),
        "strap_light": mat("ppod_strap_light", 0xf5, 0.12, metallic=0.05, roughness=0.5),
        "gold": mat("ppod_gold", 0xfa, 0.12, metallic=0.85, roughness=0.25),
        "gold_dark": mat("ppod_gold_dark", 0xf9, 0.08, metallic=0.85, roughness=0.3),
        "gold_light": mat("ppod_gold_light", 0xfb, 0.15, metallic=0.85, roughness=0.22),
        "glint": mat("ppod_glint", 0x5e, 0.15, metallic=0.6, roughness=0.15),
    }


# --- The shell -------------------------------------------------------------------------------------------------------

def surface(d):
    """The shell's point and normal in the direction d (a unit vector) from its middle (before the turn)."""
    point = CENTRE + Vector((d.x * RADII.x, d.y * RADII.y, d.z * RADII.z))
    normal = Vector((d.x / RADII.x, d.y / RADII.y, d.z / RADII.z)).normalized()
    return point, normal


def rim(d):
    """0 on the dark rim, 1 inside it."""
    return smoothstep(RIM - 0.07, RIM + 0.07, surface(d)[1].z)


def lower(d):
    """1 on the lower half (below the strap's line), 0 above it."""
    return 1.0 - smoothstep(LOWER - LOWER_W, LOWER + LOWER_W, surface(d)[0].y)


def crescent(d):
    point, normal = surface(d)
    if normal.z <= 0:
        return 0.0
    angle = math.degrees(math.atan2(point.y - CENTRE.y, point.x - CENTRE.x))
    off = ((angle - CRESCENT_AT + 180) % 360 - 180) / CRESCENT_SPREAD
    bottom = ((angle - BOTTOM_AT + 180) % 360 - 180) / BOTTOM_SPREAD
    across = math.exp(-((normal.z - CRESCENT_Z) / CRESCENT_WIDTH) ** 2)
    return across * max(math.exp(-off * off), 0.62 * math.exp(-bottom * bottom))


def glare(d):
    point, normal = surface(d)
    if normal.z <= 0.3:
        return 0.0
    u, v = (point.x - GLARE.x) / GLARE_SIZE.x, (point.y - GLARE.y) / GLARE_SIZE.y
    return math.exp(-u * u - v * v)


# The painted parts in order (later ones over earlier ones): (field, its borders, the materials from the lowest band
# up; None keeps what lies under it).
PAINT = [
    (lower, (0.5,), (None, "lower")),
    (rim, (0.5,), ("rim", None)),
    (crescent, (0.32, 0.7), (None, "crescent", "crescent")),
    (glare, (0.25, 0.52, 0.78), (None, "glare", "glare_mid", "glare_core")),
]


def shell(m):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=4, radius=1.0)
    # Finer round the glare, whose contours are small: its edges halved twice (back on the sphere each time).
    for _ in range(2):
        edges = [e for e in bm.edges if glare(((e.verts[0].co + e.verts[1].co) / 2).normalized()) > 0.06]
        bmesh.ops.subdivide_edges(bm, edges=edges, cuts=1, use_grid_fill=True)
        for v in bm.verts:
            v.co = v.co.normalized()
        bmesh.ops.triangulate(bm, faces=bm.faces[:])
    for field, borders, _ in PAINT:
        for t in borders:
            split_along(bm, {v: field(v.co.normalized()) for v in bm.verts}, t)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    kinds = []
    for f in bm.faces:
        d = f.calc_center_median().normalized()
        kind = "shell"
        for field, borders, names in PAINT:
            band = sum(field(d) > t for t in borders)
            if names[band] is not None:
                kind = names[band]
        kinds.append(kind)
    for v in bm.verts:
        v.co = surface(v.co.normalized())[0]
    mesh = bpy.data.meshes.new("shell")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("shell", mesh)
    bpy.context.scene.collection.objects.link(obj)
    names = []
    for kind in kinds:
        if m[kind].name not in names:
            names.append(m[kind].name)
            mesh.materials.append(m[kind])
    for poly, kind in zip(mesh.polygons, kinds):
        poly.material_index = names.index(m[kind].name)
    k.recalc_normals(obj)
    return k.smooth(obj, 80)


# --- The strap and the clasp ------------------------------------------------------------------------------------------

def shell_ring(y):
    """The shell's cross-section at y (before the turn): its half-width and half-height there."""
    s = math.sqrt(max(0.0, 1 - ((y - CENTRE.y) / RADII.y) ** 2))
    return RADII.x * s, RADII.z * s


def strap_profile():
    """The strap's cross-section from its lower edge up: (t, y, how far out of the shell), its feet a little inside."""
    out = [(-1.04, -0.15)]
    for i in range(17):
        t = -1 + 2 * i / 16
        out.append((t, STRAP_OUT * max(0.0, 1 - abs(t) ** STRAP_POWER) ** (1 / STRAP_POWER)))
    out.append((1.04, -0.15))
    out.append((LIGHT_T, STRAP_OUT * (1 - LIGHT_T ** STRAP_POWER) ** (1 / STRAP_POWER)))
    out.sort()
    y0, y1 = STRAP_Y
    return [(t, (y0 + y1) / 2 + (y1 - y0) / 2 * t, lift) for t, lift in out]


def strap(m):
    """The strap round the pod's axis (along Y): rings round the shell at each y of its cross-section, raised out of
    it; darker where it turns away, lighter along its upper edge near the top."""
    angles = sorted({360.0 * i / STRAP_SEGMENTS for i in range(STRAP_SEGMENTS)} |
                    {a % 360.0 for a in (SIDE, -SIDE, LIGHT_A, -LIGHT_A)})
    profile = strap_profile()
    rings = []
    for t, y, lift in profile:
        hw, hh = shell_ring(y)
        rings.append([Vector((CENTRE.x + (hw + lift) * math.sin(math.radians(a)), y,
                              CENTRE.z + (hh + lift) * math.cos(math.radians(a)))) for a in angles])
    obj = k.loft("strap", rings, None, cap_start=False, cap_end=False)
    n = len(angles)
    names = []
    for poly in obj.data.polygons:
        row, j = divmod(poly.index, n)
        t = (profile[row][0] + profile[row + 1][0]) / 2
        a0, a1 = angles[j], angles[(j + 1) % n] + (360.0 if j + 1 == n else 0.0)
        a = ((a0 + a1) / 2 + 180) % 360 - 180
        if abs(a) > SIDE:
            key = "strap_side"
        elif t > LIGHT_T and abs(a) < LIGHT_A:
            key = "strap_light"
        else:
            key = "strap"
        if m[key].name not in names:
            names.append(m[key].name)
            obj.data.materials.append(m[key])
        poly.material_index = names.index(m[key].name)
    k.recalc_normals(obj)
    return k.smooth(obj, 60)


def seams(m):
    """The dark seams along the strap's edges: thin tubes round the shell just beyond them, sunk into it."""
    out = []
    for i, y in enumerate((STRAP_Y[0] - SEAM_OUT, STRAP_Y[1] + SEAM_OUT)):
        hw, hh = shell_ring(y)
        pts = [(CENTRE.x + (hw - SEAM_SINK) * math.sin(math.radians(a)), y,
                CENTRE.z + (hh - SEAM_SINK) * math.cos(math.radians(a))) for a in range(-180, 181, 5)]
        out.append(k.smooth(mk.tube(f"seam{i}", pts, SEAM_R, m["seam"], 10, cap=False), 60))
    return out


def strap_top(y):
    """The strap's top over the pod's middle line (x = 0) at y."""
    return CENTRE.z + shell_ring(y)[1] + STRAP_OUT


def clasp(m):
    """The golden bar across the strap on top, lying on it (following its curve), its ends rounded; a pale stud at its
    upper end."""
    y0, y1 = CLASP_Y
    rings = []
    count = 22
    for i in range(count + 1):
        y = y0 + (y1 - y0) * i / count
        # The bar's ends rounded off: its section shrinks over the last 0.5 pixel.
        end = min(y - y0, y1 - y) / 0.5
        f = math.sqrt(max(0.0, min(1.0, end) * (2 - min(1.0, end)))) if end < 1 else 1.0
        zc = strap_top(y) + CLASP_UP - CLASP_HALF
        rings.append(k.ring(y, max(CLASP_HW * (0.55 + 0.45 * f), 0.05), max(CLASP_HALF * f, 0.05), 24, z=zc,
                            power=3.2))
    obj = k.loft("clasp", rings, m["gold"], start_point=(0, y0, strap_top(y0) + CLASP_UP - CLASP_HALF),
                 end_point=(0, y1, strap_top(y1) + CLASP_UP - CLASP_HALF))
    k.smooth(obj, 50)

    def pick(c, n):
        if n.z < 0.35:
            return m["gold_dark"]
        if c.y < -2.35:
            return m["gold_light"]
        if c.y < -1.45:
            return m["gold_dark"]
        return None
    mk.paint(obj, pick)
    sy, radii = STUD
    stud = mk.ball("clasp_stud", (0.0, sy, strap_top(sy) + CLASP_UP - 0.05), radii, m["glint"], 20, 10)
    return [obj, stud]


def turn(objects):
    """Turns the objects about the x axis through the pod's middle by VIEW_TILT (the top towards the bottom of the
    screen), so the game's camera sees what was built seen from straight above."""
    rot = (Matrix.Translation(CENTRE) @ Matrix.Rotation(math.radians(VIEW_TILT), 4, "X") @
           Matrix.Translation(-CENTRE))
    for obj in objects:
        mk.apply(obj)
        mesh = obj.data
        # keep the shading: turn the custom corner normals with the mesh
        normals = [rot.to_3x3() @ c.vector for c in mesh.corner_normals]
        mesh.transform(rot)
        mesh.normals_split_custom_set([tuple(n.normalized()) for n in normals])
        mesh.update()
    return objects


def build():
    options = k.args()
    out = mk.outdir(options)
    k.reset()
    m = materials()
    parts = [shell(m), strap(m)] + seams(m) + clasp(m)
    parts = triangulate(turn(parts))
    bpy.context.view_layer.update()
    if "check" in options:
        sheet = os.path.join(options["check"], "enemy_5.png")
        mk.compare("purple_pod (5 47)", mk.coverage(parts, 24, 28), k.sprite_mask(sheet, 47))
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    mk.report(NAME, parts, os.path.join(out, NAME + ".glb"))
    if "preview" in options:
        mk.preview(options["preview"] + NAME, parts, distance=0.6)


if __name__ == "__main__":
    build()
