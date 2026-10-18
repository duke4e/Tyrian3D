"""The three red capsules sunk in the ground of the asteroid levels (sheet S sprites 191 and 153, 2x2:
24 x 28 pixels; ASTEROID1, ASTEROID2, ASTEROID?, ASTCITY, AST. CITY, AST ROCK, GREY MOON), polished
(2026-10-18; it replaces later_episodes.py's panel_pills, three capsules on grey cradles). Built as
S 191 draws it, the capsules up the screen; S 153 draws them across it, and models.cfg turns the
model for it (yaw=90 puts S 191's right capsule at S 153's bottom, so the two animations match
frame for frame).

As the 4x upscale draws it: three glossy dark red capsules side by side (columns 1-6, 9-14 and
17-22 of rows 5-22: 6 x 18 pixels, their ends tapering to two pixels), each sunk into a socket
with a raised lighter rim a pixel wide (the light pixels round them: columns 0, 7, 8, 15, 16 and
23, rows 4 and 23). Between two capsules their rims make one low divider, a seam across the left
one (row 16). The grey stone round them is the asteroid city's ground, which the 3D view draws
from the map: no plate here, the rims stand about a pixel above the ground and fall to it (z = 0)
at their outer edges.

The animation lights the capsules in turn, right, middle, left (191 193 191, 195 197 195, 199 201
199): a capsule glows (the sprite's red ramp up to shade 5), shines (up to shade 7), glows again.
One model per frame, the same geometry with the capsules' materials changed: panel_pills (191, the
right capsule glowing), panel_pills_193 (the right one shining), panel_pills_195 and _197 (the
middle one), panel_pills_199 and _201 (the left one). S 153's frames 153-163 show the same states
in the same order.

Origin at the sprite's centre (pixel 12, 14); +Y up the sprite, +Z towards the camera.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <enemy_S.png> (the
glass against the sprite's red, the whole against the red and a pixel round it; for S 191 and,
turned, for S 153), --preview <prefix>.
"""
import math
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
from polish_sphere_nozzle import smoothstep  # noqa: E402
from sprite_profile import sprite_indices  # noqa: E402

CAPSULES = (-8.0, 0.0, 8.0)  # the capsules' middles, x (columns 1-6, 9-14, 17-22)
HALF_WIDTH = 3.0             # the glass and its socket: 6 pixels
# The glass's sides run straight to GLASS_STRAIGHT from its middle (rows 7-20), then taper at a slant
# to a blunt tip GLASS_TIP wide at GLASS_LENGTH (rows 5 and 22): a superellipse of power GLASS_TAPER,
# nearly straight between rounded corners, as the upscale draws the ends.
GLASS_STRAIGHT, GLASS_LENGTH, GLASS_TIP, GLASS_TAPER = 5.8, 8.9, 0.8, 1.3
# The socket is rounder: its sides run on to SOCKET_STRAIGHT and its ends are near semicircles
# reaching SOCKET_LENGTH, so that its dark floor shows beside the glass's slanted ends (the sprite's
# dark pixels there, rows 5-6 and 21-22) and its rim crosses rows 4 and 23.
SOCKET_STRAIGHT, SOCKET_LENGTH, SOCKET_POWER = 6.3, 9.0, 2.2
END_STEPS = 8                # points along each quarter of an end
# The glass: the foot of its edge above the socket's floor, how much higher its crest is, the power
# of its cross-section (2: an ellipse). Its ends round down to the foot.
GLASS_FOOT, GLASS_RISE, GLASS_POWER = 0.25, 1.55, 2.2
# Points across the glass, fractions of its half-width from left to right, and the borders of its
# bands: edge, side, crest, side, edge (the crest right of the middle, as the sprite's lightest
# columns are).
ACROSS = (-1.0, -0.94, -0.82, -0.62, -0.46, -0.3, 0.0, 0.3, 0.55, 0.7, 0.82, 0.93, 1.0)
BANDS = (-0.62, -0.3, 0.55, 0.82)
# Along the straight sides (y, ascending): the divider's ends and the seam across the left divider.
SIDE_YS = (-5.8, -5.3, -4.8, -3.6, -2.75, -2.6, -2.4, -2.25, -1.0, 1.2, 3.4, 4.8, 5.3, 5.8)
SEAM = (-2.5, 0.12, 0.3)     # its middle (row 16), half-width and depth
DIVIDER_ENDS = (5.3, 6.3)    # the divider falls to the ground over this |y| (to where the sockets' ends begin)
# The rim out from the socket's edge (offset, height): where it borders the ground, and where it
# meets its neighbour's rim halfway between two capsules (the divider, highest along that line).
# Inside the socket's edge lies its floor (dark), out to the glass; the rim's first two bands, its
# foot, are dark too.
RIM_EDGE = [(0.06, 0.0), (0.16, 0.2), (0.3, 0.62), (0.46, 0.9), (0.62, 0.97), (0.8, 0.8), (0.95, 0.4), (1.12, 0.0)]
RIM_DIVIDER = [(0.06, 0.0), (0.16, 0.2), (0.3, 0.62), (0.46, 0.86), (0.62, 0.93), (0.78, 0.975), (0.92, 0.997),
               (1.0, 1.0)]
DARK_RINGS = 2               # the floor and the rim's foot

# The glass's bands in each state, edge, side, crest: (palette index, emission strength).
STATES = {
    "dark": ((0x71, 0.0), (0x72, 0.0), (0x73, 0.0)),
    "glow": ((0x72, 0.15), (0x74, 0.45), (0x75, 0.75)),
    "shine": ((0x73, 0.4), (0x76, 1.1), (0x77, 1.6)),
}
# The frames: (model, sprite, the lit capsule (0 left, 1 middle, 2 right), its state).
FRAMES = [
    ("panel_pills", 191, 2, "glow"),
    ("panel_pills_193", 193, 2, "shine"),
    ("panel_pills_195", 195, 1, "glow"),
    ("panel_pills_197", 197, 1, "shine"),
    ("panel_pills_199", 199, 0, "glow"),
    ("panel_pills_201", 201, 0, "shine"),
]
S153 = {191: 153, 193: 155, 195: 157, 197: 159, 199: 161, 201: 163}


def taper_t(y):
    """How far along the glass's taper y is: 0 where it begins, 1 at the tip."""
    return min(1.0, max(0.0, (abs(y) - GLASS_STRAIGHT) / (GLASS_LENGTH - GLASS_STRAIGHT)))


def glass_width(y):
    t = taper_t(y)
    return GLASS_TIP + (HALF_WIDTH - GLASS_TIP) * (1 - t ** GLASS_TAPER) ** (1 / GLASS_TAPER)


def glass_height(y):
    return GLASS_RISE * math.sqrt(max(0.0, 1 - taper_t(y) ** 2))


def glass_end(step):
    """A point of the glass's upper right end: step 0 where the side ends, END_STEPS the tip's corner."""
    a = (math.pi / 2) * step / END_STEPS
    return Vector((GLASS_TIP + (HALF_WIDTH - GLASS_TIP) * math.cos(a) ** (2 / GLASS_TAPER),
                   GLASS_STRAIGHT + (GLASS_LENGTH - GLASS_STRAIGHT) * math.sin(a) ** (2 / GLASS_TAPER)))


def glass_outline():
    """The glass's outline round its middle, counter-clockwise from the right side's lower end."""
    quarter = [glass_end(s) for s in range(1, END_STEPS + 1)]
    points = [Vector((HALF_WIDTH, y)) for y in SIDE_YS] + quarter + [Vector((0.0, GLASS_LENGTH))]
    points += [Vector((-p.x, p.y)) for p in reversed(quarter)]
    points += [Vector((-HALF_WIDTH, y)) for y in reversed(SIDE_YS)]
    points += [Vector((-p.x, -p.y)) for p in quarter] + [Vector((0.0, -GLASS_LENGTH))]
    points += [Vector((p.x, -p.y)) for p in reversed(quarter)]
    return points


def inside_socket(p):
    if abs(p.x) > HALF_WIDTH:
        return False
    if abs(p.y) <= SOCKET_STRAIGHT:
        return True
    t = (abs(p.y) - SOCKET_STRAIGHT) / (SOCKET_LENGTH - SOCKET_STRAIGHT)
    return t < 1 and (abs(p.x) / HALF_WIDTH) ** SOCKET_POWER + t ** SOCKET_POWER <= 1


def socket_outline(glass_points):
    """The socket's edge where the rays from the capsule's middle through the glass's outline leave
    it (so its points pair with the glass's): [(point, outward normal)]."""
    points = []
    for g in glass_points:
        direction = g.normalized()
        lo, hi = 0.0, 12.0
        for _ in range(48):
            mid = (lo + hi) / 2
            if inside_socket(direction * mid):
                lo = mid
            else:
                hi = mid
        points.append(direction * lo)
    n = len(points)
    normals = [Vector(((points[(i + 1) % n] - points[i - 1]).y, -(points[(i + 1) % n] - points[i - 1]).x)).normalized()
               for i in range(n)]
    return list(zip(points, normals))


def band(u):
    """The glass's band at u across it: 0 its edges, 1 its sides, 2 its crest."""
    if u < BANDS[0] or u > BANDS[3]:
        return 0
    return 1 if u < BANDS[1] or u > BANDS[2] else 2


def glass(name, cx, mats):
    """A capsule: cross-sections along it, each a rounded arc over a short upright foot."""
    ys = sorted(set(SIDE_YS) | {s * glass_end(i).y for i in range(1, END_STEPS + 1) for s in (1, -1)})
    rings = []
    for y in ys:
        w, h = glass_width(y), glass_height(y)
        ring = [Vector((cx - w, y, 0.0))]
        ring += [Vector((cx + u * w, y, GLASS_FOOT + h * (1 - abs(u) ** GLASS_POWER) ** (1 / GLASS_POWER)))
                 for u in ACROSS]
        ring.append(Vector((cx + w, y, 0.0)))
        rings.append(ring)
    obj = k.loft(name, rings, None, start_point=(cx, -GLASS_LENGTH, GLASS_FOOT * 0.5),
                 end_point=(cx, GLASS_LENGTH, GLASS_FOOT * 0.5))
    for mat in mats:
        obj.data.materials.append(mat)
    for poly in obj.data.polygons:
        c = poly.center
        poly.material_index = band((c.x - cx) / glass_width(c.y)) if c.z > GLASS_FOOT + 0.01 else 0
    return finish_part(obj, 75)


def rim(name, cx, neighbours, seam_side, mats):
    """The socket round a capsule: its floor from the glass out to its edge, then its rim, rings
    offset from the edge rising to a crest and falling to the ground or, along a side facing a
    neighbour (neighbours: left, right), running on level to meet its rim. seam_side (-1, 1 or 0):
    the side with the seam across the divider."""
    glass_points = glass_outline()
    contour = socket_outline(glass_points)
    rings = []
    seam_points = []
    for g, (p, n) in zip(glass_points, contour):
        facing = (p.x > 0.5 and neighbours[1]) or (p.x < -0.5 and neighbours[0])
        f = 1 - smoothstep(DIVIDER_ENDS[0], DIVIDER_ENDS[1], abs(p.y)) if facing else 0.0
        seam = seam_side != 0 and p.x * seam_side > 0.5 and abs(p.y - SEAM[0]) < SEAM[1] + 0.02
        seam_points.append(seam)
        ring = [Vector((cx + g.x, g.y, 0.0))]  # the floor's inner edge, under the glass's foot
        for (d0, z0), (d1, z1) in zip(RIM_EDGE, RIM_DIVIDER):
            d, z = d0 + (d1 - d0) * f, z0 + (z1 - z0) * f
            if seam and d > 0.3:
                z -= SEAM[2] * smoothstep(0.3, 0.5, d)
            ring.append(Vector((cx + p.x + n.x * d, p.y + n.y * d, z)))
        rings.append(ring)
    m = len(contour)
    count = len(rings[0])
    vertices = [v for ring in rings for v in ring]
    faces, kinds = [], []
    for i in range(m):
        j = (i + 1) % m
        for r in range(count - 1):
            a, b = i * count + r, j * count + r
            faces.append((a, a + 1, b + 1, b))  # counter-clockwise seen from above
            dark = r < DARK_RINGS or (seam_points[i] and seam_points[j] and r >= 3)
            kinds.append(1 if dark else 0)
    obj = k.mesh_object(name, vertices, faces)
    obj.data.materials.append(mats["rim"])
    obj.data.materials.append(mats["socket"])
    for poly, kind in zip(obj.data.polygons, kinds):
        poly.material_index = kind
    if sum(poly.normal.z * poly.area for poly in obj.data.polygons) < 0:  # the faces look up
        obj.data.flip_normals()
    return finish_part(obj, 45)


def finish_part(obj, angle):
    """Faces lying flat with their neighbours merged (the straight runs), the colours' borders
    kept; smooth shading."""
    mod = obj.modifiers.new("dissolve", "DECIMATE")
    mod.decimate_type = "DISSOLVE"
    mod.angle_limit = math.radians(1.0)
    mod.delimit = {"MATERIAL"}
    return k.smooth(obj, angle)


def materials(state):
    rim_mat = k.material("pills_rim", palette=0x0b, metallic=0.2, roughness=0.35)
    socket = k.material("pills_socket", palette=0x03, metallic=0.1, roughness=0.8)
    glass_mats = {}
    for key in ("dark", state):
        glass_mats[key] = [k.material(f"pills_{key}_{part}", palette=index, metallic=0.0, roughness=0.12,
                                      emission=k.level_palette()[index] if glow > 0 else None, emission_strength=glow)
                           for part, (index, glow) in zip(("edge", "side", "crest"), STATES[key])]
    return {"rim": rim_mat, "socket": socket, "glass": glass_mats}


def build_panel(lit, state):
    mats = materials(state)
    glasses = []
    for i, cx in enumerate(CAPSULES):
        glasses.append(glass(f"glass{i}", cx, mats["glass"][state if i == lit else "dark"]))
        rim(f"rim{i}", cx, (i > 0, i < 2), 1 if i == 0 else -1 if i == 1 else 0, mats)
    return glasses


# --- Checks -----------------------------------------------------------------------------------------

def red_mask(sheet, sprite):
    return [[i is not None and 0x70 <= i <= 0x7f for i in row] for row in sprite_indices(sheet, sprite)]


def grow(mask):
    """The mask and a pixel round it."""
    h, w = len(mask), len(mask[0])
    return [[any(mask[yy][xx] for yy in range(max(0, y - 1), min(h, y + 2))
                 for xx in range(max(0, x - 1), min(w, x + 2))) for x in range(w)] for y in range(h)]


def turned(mask):
    """S 153's mask in the model's frame (the model turned by yaw=90 for it): the model's pixel
    (column c, row r) of a 28 x 24 view is S 153's (column 23 - r, row c)."""
    return [[mask[c][23 - r] for c in range(28)] for r in range(24)]


def coverage(objects, w, h, supersample=4):
    """Which pixels of a w x h top view round the origin the objects cover."""
    scene = bpy.context.scene
    hidden = {}
    for obj in scene.objects:
        if obj.type == "MESH":
            hidden[obj.name] = obj.hide_render
            obj.hide_render = obj not in objects
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.film_transparent = True
    scene.render.resolution_x, scene.render.resolution_y = w * supersample, h * supersample
    scene.render.resolution_percentage = 100
    data = bpy.data.cameras.new("check")
    data.type = "ORTHO"
    data.ortho_scale = max(w, h)
    cam = bpy.data.objects.new("check", data)
    cam.location = (0, 0, 100)
    scene.collection.objects.link(cam)
    scene.camera = cam
    path = os.path.join(bpy.app.tempdir or "/tmp", "pills_check.png")
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    image = bpy.data.images.load(path)
    rw, rh = image.size
    pixels = list(image.pixels)
    bpy.data.images.remove(image)
    bpy.data.objects.remove(cam)
    for obj in scene.objects:
        if obj.name in hidden:
            obj.hide_render = hidden[obj.name]
    covered = []
    for y in range(h):
        row = []
        for x in range(w):
            alpha = sum(pixels[((rh - 1 - (y * supersample + sy)) * rw + x * supersample + sx) * 4 + 3]
                        for sy in range(supersample) for sx in range(supersample))
            row.append(alpha / supersample ** 2 > 0.5)
        covered.append(row)
    return covered


def compare(label, covered, mask):
    h, w = len(mask), len(mask[0])
    both = sum(covered[y][x] and mask[y][x] for y in range(h) for x in range(w))
    either = sum(covered[y][x] or mask[y][x] for y in range(h) for x in range(w))
    print("%s: overlap %.3f" % (label, both / max(either, 1)))
    for y in range(h):
        print("".join("#" if covered[y][x] and mask[y][x] else "+" if covered[y][x] else "-" if mask[y][x] else "."
                      for x in range(w)))


def check(sheet, sprite, glasses):
    everything = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    red = red_mask(sheet, sprite)
    compare(f"S {sprite} glass against its red", coverage(glasses, 24, 28), red)
    compare(f"S {sprite} capsules and rims against the red and a pixel round it", coverage(everything, 24, 28),
            grow(red))
    red = turned(red_mask(sheet, S153[sprite]))
    compare(f"S {S153[sprite]} (turned) glass against its red", coverage(glasses, 28, 24), red)


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
    for name, sprite, lit, state in FRAMES:
        k.reset()
        glasses = build_panel(lit, state)
        used = {m.name for obj in bpy.context.scene.objects if obj.type == "MESH" for m in obj.data.materials}
        print("== %s (S %d, S %d): %d triangles, %d materials" % (name, sprite, S153[sprite], triangles(), len(used)))
        if "check" in options:
            check(options["check"], sprite, glasses)
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        path = os.path.join(outdir, name + ".glb")
        k.export(path)
        print("%s: %d bytes" % (path, os.path.getsize(path)))
        if "preview" in options:
            k.preview(options["preview"] + name)


if __name__ == "__main__":
    build()
