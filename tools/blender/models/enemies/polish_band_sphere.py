"""The banded glass sphere of HOLES (sheet E sprite 13, 2x2: an 18 x 17 ball in the 24 x 28 cell; top
layer, 104 of them; its animation 13 13 13 15 15 15 17 17 17 15 15 15), polished (2026-10-18; it
replaces rounds.py's band_sphere(), a dull sphere with an orange ring). models.cfg: sprite e 13
band_sphere yaw=0, frame e 15 band_sphere_15, frame e 17 band_sphere_17.

As the 4x upscale draws it: a glossy ball of dark blue glass (the sprite's ramp 3, columns 3-20 of
rows 5-21), a white highlight above its middle on the left (columns 8-11, rows 9-11) and a bright
crescent inside its rim at the lower right (rows 16-20), where the light through the glass gathers,
as in a glass marble. Round its middle runs a glowing band (rows 12-14, the ball's full width),
standing out of the glass a little: orange-yellow along its middle row, red-orange at its edges,
darker at its ends where it turns away round the ball. Seen from above the band crosses the ball,
so it runs round the ball's axis up the screen.

The animation only dims the band: in 15 every shade of it is two lighter shades of ramp 7 darker
(an orange middle, red edges), in 17 four (a red middle, dark red edges); the glass stays the same.
One model per frame: band_sphere (13), band_sphere_15 and band_sphere_17, the same shapes with the
band's own colours and glow.

The glass carries the sprite's light painted on: the glare (where the game's sun, from above and the
top left, puts its own highlight too), the crescent, glowing faintly, and the dark rim the sprite
draws round the ball (the glass thickest seen edge-on). The band glows in its palette colours.

Origin at the sprite's centre (pixel 12, 14); +Y up the sprite, +Z towards the camera. The ball's
middle is at (0, 0.5, 0) (columns 3-20 and rows 5-21 round pixel 12, 13.5).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the
silhouette of each frame against enemy_E.png), --preview <prefix>.
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
from polish_sphere_nozzle import smoothstep, split_along  # noqa: E402

CENTRE = Vector((0.0, 0.5, 0.0))
RADII = Vector((8.9, 8.45, 8.7))

# The band: its edges (y, rows 12-14), how far it stands out of the glass at its crest, the power of
# its cross-section (higher: flatter crest, steeper edges), its middle row (|t| below CORE, t from -1
# at its lower edge to 1 at its upper one) and where its ends begin (degrees round the ball's axis
# from straight up; columns 3-4 and 19-20 of the sprite).
BAND_Y = (-1.0, 2.0)
BAND_OUT = 0.5
BAND_POWER = 4.0
CORE = 0.36
END = 62.0
BAND_SEGMENTS = 72

# The glass: the dark rim where its surface turns away from the camera (the normal's z below RIM);
# the crescent at the lower right, round the direction CRESCENT_AT in the top view (degrees from +X,
# counter-clockwise), CRESCENT_SPREAD wide either side, its middle where the normal's z is
# CRESCENT_Z, CRESCENT_WIDTH wide either side (rows 16-20 of the sprite: brightest at columns 13-17,
# about 0.84 of the radius out); and the glare above the band on the left (columns 8-11 of rows 9-11):
# its middle and half-sizes in the top view.
RIM = 0.3
CRESCENT_AT, CRESCENT_SPREAD = -57.0, 30.0
CRESCENT_Z, CRESCENT_WIDTH = 0.52, 0.12
GLARE, GLARE_SIZE = Vector((-2.0, 3.55)), Vector((2.6, 1.7))

# The frames: (model, sprite, the band's (middle, edges) palette indices and emission strengths for
# its face and its ends).
FRAMES = [
    ("band_sphere", 13, {"core": (0x7b, 1.1), "edge": (0x78, 0.95), "core_end": (0x78, 0.85),
                         "edge_end": (0x75, 0.6)}),
    ("band_sphere_15", 15, {"core": (0x79, 1.05), "edge": (0x76, 0.85), "core_end": (0x76, 0.75),
                            "edge_end": (0x73, 0.5)}),
    ("band_sphere_17", 17, {"core": (0x77, 0.95), "edge": (0x74, 0.7), "core_end": (0x74, 0.6),
                            "edge_end": (0x71, 0.38)}),
]


def glass_materials():
    return {
        # The game's camera sees mostly the ball's front and underside, which face away from its sun:
        # lit by the sky alone they read near black. The sprite paints the ball lit all over, so the
        # glass glows a little in its own blue (in the game it then shows the sprite's colour there).
        "glass": k.material("bsphere_glass", palette=0x3a, roughness=0.4,
                            emission=k.level_palette()[0x3a], emission_strength=0.6),
        "rim": k.material("bsphere_rim", palette=0x38, roughness=0.45,
                          emission=k.level_palette()[0x38], emission_strength=0.45),
        "glare": k.material("bsphere_glare", palette=0x3b, metallic=0.1, roughness=0.1),
        "glare_mid": k.material("bsphere_glare_mid", palette=0x3d, metallic=0.1, roughness=0.1),
        "glare_core": k.material("bsphere_glare_core", palette=0x3f, metallic=0.1, roughness=0.1),
        "crescent": k.material("bsphere_crescent", palette=0x3c, metallic=0.1, roughness=0.12,
                               emission=k.level_palette()[0x3c], emission_strength=0.3),
        "crescent_core": k.material("bsphere_crescent_core", palette=0x3e, metallic=0.1, roughness=0.12,
                                    emission=k.level_palette()[0x3e], emission_strength=0.5),
    }


def band_materials(colours):
    return {key: k.material(f"bsphere_band_{key}_{index:x}", palette=index, roughness=0.3,
                            emission=k.level_palette()[index], emission_strength=strength)
            for key, (index, strength) in colours.items()}


def surface(d):
    """The glass's point and normal in the direction d (a unit vector) from its middle."""
    point = CENTRE + Vector((d.x * RADII.x, d.y * RADII.y, d.z * RADII.z))
    normal = Vector((d.x / RADII.x, d.y / RADII.y, d.z / RADII.z)).normalized()
    return point, normal


def rim(d):
    """0 on the dark rim, 1 inside it."""
    return smoothstep(RIM - 0.08, RIM + 0.08, surface(d)[1].z)


def crescent(d):
    """0 to 1: the crescent's brightness."""
    point, normal = surface(d)
    if normal.z <= 0:
        return 0.0
    angle = math.degrees(math.atan2(point.y - CENTRE.y, point.x - CENTRE.x))
    off = ((angle - CRESCENT_AT + 180) % 360 - 180) / CRESCENT_SPREAD
    return math.exp(-off * off - ((normal.z - CRESCENT_Z) / CRESCENT_WIDTH) ** 2)


def glare(d):
    """0 to 1: the glare's brightness, seen from above."""
    point, normal = surface(d)
    if normal.z <= 0.3:
        return 0.0
    u, v = (point.x - GLARE.x) / GLARE_SIZE.x, (point.y - GLARE.y) / GLARE_SIZE.y
    return math.exp(-u * u - v * v)


# The painted parts: (field, its borders, the materials from the lowest band up).
PAINT = [
    (rim, (0.5,), ("rim", None)),
    (crescent, (0.3, 0.68), (None, "crescent", "crescent_core")),
    (glare, (0.25, 0.5, 0.74), (None, "glare", "glare_mid", "glare_core")),
]


def glass(mats):
    """The ball: an icosphere, its faces cut along the painted parts' borders (so that they run
    smoothly), then stretched to the ball's radii."""
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=5, radius=1.0)
    for field, borders, _ in PAINT:
        for t in borders:
            split_along(bm, {v: field(v.co.normalized()) for v in bm.verts}, t)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    kinds = []
    for f in bm.faces:
        d = f.calc_center_median().normalized()
        kind = "glass"
        for field, borders, names in PAINT:
            band_index = sum(field(d) > t for t in borders)
            if names[band_index] is not None:
                kind = names[band_index]
        kinds.append(kind)
    for v in bm.verts:
        v.co = surface(v.co.normalized())[0]
    mesh = bpy.data.meshes.new("glass")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("glass", mesh)
    bpy.context.scene.collection.objects.link(obj)
    names = []
    for kind in kinds:
        if mats[kind].name not in names:
            names.append(mats[kind].name)
            mesh.materials.append(mats[kind])
    for poly, kind in zip(mesh.polygons, kinds):
        poly.material_index = names.index(mats[kind].name)
    k.recalc_normals(obj)
    return k.smooth(obj, 80)


def band_profile():
    """The band's cross-section from its lower edge up: (t, y, how far out of the glass), its feet a
    little inside the glass."""
    out = [(-1.06, -0.12)]
    for i in range(15):
        t = -1 + 2 * i / 14
        out.append((t, BAND_OUT * max(0.0, 1 - abs(t) ** BAND_POWER) ** (1 / BAND_POWER)))
    out.append((1.06, -0.12))
    # Rows at the core's borders, so that the colours meet along them.
    for t in (-CORE, CORE):
        out.append((t, BAND_OUT * (1 - abs(t) ** BAND_POWER) ** (1 / BAND_POWER)))
    out.sort()
    y0, y1 = BAND_Y
    return [(t, (y0 + y1) / 2 + (y1 - y0) / 2 * t, lift) for t, lift in out]


def band(mats):
    """The band round the ball's axis (along Y): rings round the glass's surface at each y of its
    cross-section, raised out of it."""
    angles = sorted({360.0 * i / BAND_SEGMENTS for i in range(BAND_SEGMENTS)} |
                    {a % 360.0 for a in (END, -END, 90.0, -90.0)})
    profile = band_profile()
    rings = []
    for t, y, lift in profile:
        s = math.sqrt(max(0.0, 1 - ((y - CENTRE.y) / RADII.y) ** 2))
        rx, rz = RADII.x * s + lift, RADII.z * s + lift
        rings.append([Vector((CENTRE.x + rx * math.sin(math.radians(a)), y,
                              CENTRE.z + rz * math.cos(math.radians(a)))) for a in angles])
    obj = k.loft("band", rings, None, cap_start=False, cap_end=False)
    n = len(angles)
    names = []
    for poly in obj.data.polygons:
        row, j = divmod(poly.index, n)
        t = (profile[row][0] + profile[row + 1][0]) / 2
        a0, a1 = angles[j], angles[(j + 1) % n] + (360.0 if j + 1 == n else 0.0)
        a = ((a0 + a1) / 2 + 180) % 360 - 180  # -180 to 180, 0 straight up
        key = ("core" if abs(t) < CORE else "edge") + ("_end" if abs(a) > END else "")
        mat = mats[key]
        if mat.name not in names:
            names.append(mat.name)
            obj.data.materials.append(mat)
        poly.material_index = names.index(mat.name)
    k.recalc_normals(obj)
    return k.smooth(obj, 60)


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
    for name, sprite, colours in FRAMES:
        k.reset()
        glass(glass_materials())
        band(band_materials(colours))
        used = {m.name for obj in bpy.context.scene.objects if obj.type == "MESH" for m in obj.data.materials}
        print("== %s (E %d): %d triangles, %d materials" % (name, sprite, triangles(), len(used)))
        if "check" in options:
            sheet = options["check"]
            k.check_silhouette(os.path.join(sheet, "enemy_E.png") if os.path.isdir(sheet) else sheet, sprite)
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        path = os.path.join(outdir, name + ".glb")
        k.export(path)
        print("%s: %d bytes" % (path, os.path.getsize(path)))
        if "preview" in options:
            k.preview(options["preview"] + name)


if __name__ == "__main__":
    build()
