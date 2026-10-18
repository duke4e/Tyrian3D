"""The domed turrets of the mine levels (sheet A sprites 17 and 93, 2x2: 24 x 28 cells; ground layer;
MINEMAZE, MINES, GAUNTLET, about 400 of them; models.cfg: sprite a 17 dome_green yaw=0, sprite a 93
dome_red yaw=0).

As the 4x upscale draws them: a glossy dome inside a raised collar, a dark groove between the two.
dome_green: a dark green dome (ramp 2) in a bright green collar that glows (ramp 12); dome_red: a red
dome (ramp 4) in a tan collar (ramp 14). The collar's outline fills the sprite's width (columns 0-23,
rows 3-23: 24 x 21 pixels round (0, 0.5)), a little fuller at the bottom than at the top; the dome
(columns 3-21, rows 6-20) sits in it nearly centred. The sprites, drawn from the front, show the
collar wider at the bottom (3 pixels) than at the top (2): the game's tilted camera does that by
itself, so the collar is kept nearly even. The sprites paint the levels' asteroid ground round them
(grey cobbles, tan stones): the game shows that ground already, so the models leave it out and stand
on z = 0; their silhouettes are checked against the collar's outline.

The animations blink: A 17 shows sprite 55 once in 20 frames, A 93 sprite 131. In 55 the collar
flares bright green (ramp 12's lightest shades) and the dome's middle lights up bright green inside a
dark green band; in 131 the collar turns orange-yellow and glows, red at its outer edge and tan at its
inner one, a red band runs round the dome and the dome's middle turns a darker brown (ramp 14). The
frame models dome_green_55 and dome_red_131 are the same shapes in those colours (models.cfg:
frame a 55 dome_green_55, frame a 131 dome_red_131).

Origin at the sprite's centre (pixel 12, 14); +Y up the screen, +Z towards the camera.

Polish (2026-10-18): replaces rounds.py's dome() (a dome in a torus).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the
collar's outline in enemy_A.png, and the whole sprite), --preview <prefix>.
"""
import math
import os
import sys

import bmesh
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
import tyrkit as k  # noqa: E402

# The collar's outline: a superellipse round RING_CENTRE, an ellipse above its middle and fuller
# below (rows 19-23 are wider than rows 3-7).
RING_CENTRE = (0.0, 0.5)
RING_A, RING_B = 12.0, 10.5
RING_POWER_TOP, RING_POWER_BOTTOM = 2.1, 2.35
# The collar's inner edge, down into the groove, and the dome's foot: ellipses round DOME_CENTRE.
DOME_CENTRE = (0.3, 0.6)
INNER_A, INNER_B = 9.6, 8.3
DOME_A, DOME_B = 9.25, 7.95
GROOVE_Z = 0.6          # the groove's floor, where the dome rises
DOME_H = 6.0            # the dome's height above it
DOME_FULLNESS = 0.85    # its profile: radius cos(phi) ** this (fuller than an ellipse near its foot)
DOME_INNER = 0.78       # the blink frames' middle: within this fraction of the dome's radius
# The collar's cross-section from its outline (t = 0) to its inner edge (t = 1): (t, z), a rounded
# top a little nearer the outside.
RING_PROFILE = [(0.0, 0.0), (0.0, 0.3), (0.025, 0.75), (0.07, 1.3), (0.14, 1.8), (0.25, 2.2), (0.4, 2.42),
                (0.55, 2.45), (0.68, 2.33), (0.8, 2.06), (0.89, 1.72), (0.95, 1.36), (0.985, 1.05), (1.0, 0.82)]
RING_OUTER_T = 0.1      # the blink frame 131's red outer edge: t below this
RING_INNER_T = 0.74     # the inner wall (shaded darker in the sprites): t above this
DOME_STEPS = [0, 8, 16, 24, 32, 40, 48, 56, 64, 72, 80, 86]  # phi (degrees) of the dome's rings
SEGMENTS = 96


def outline_point(a, centre, half_a, half_b, power_top=2.0, power_bottom=2.0, scale=1.0):
    """The point at parameter a on a superellipse round centre (its upper and lower halves of their own
    powers), its size times scale."""
    c, s = math.cos(a), math.sin(a)
    p = power_top if s >= 0 else power_bottom
    return (centre[0] + math.copysign(abs(c) ** (2 / p), c) * half_a * scale,
            centre[1] + math.copysign(abs(s) ** (2 / p), s) * half_b * scale)


def dome_profile():
    """The dome's rings from its foot up: (plan scale, height), with a ring exactly at DOME_INNER."""
    rings = []
    for d in DOME_STEPS:
        phi = math.radians(d)
        rings.append((math.cos(phi) ** DOME_FULLNESS, DOME_H * math.sin(phi)))
    # The lit middle's border: the phi where the scale is DOME_INNER.
    phi = math.acos(DOME_INNER ** (1 / DOME_FULLNESS))
    rings.append((DOME_INNER, DOME_H * math.sin(phi)))
    return sorted(rings, key=lambda r: -r[0])


def turret(name, mats):
    """The collar, the groove and the dome as one mesh of rings round the turret, each ring in one
    material (the colours' borders run along rings)."""
    loops = []  # (points [(x, y, z)], material key)
    angles = [2 * math.pi * i / SEGMENTS for i in range(SEGMENTS)]
    for t, z in RING_PROFILE:
        pts = []
        for a in angles:
            ox, oy = outline_point(a, RING_CENTRE, RING_A, RING_B, RING_POWER_TOP, RING_POWER_BOTTOM)
            ix, iy = outline_point(a, DOME_CENTRE, INNER_A, INNER_B)
            pts.append((ox + (ix - ox) * t, oy + (iy - oy) * t, z))
        key = "ring_outer" if t < RING_OUTER_T else "ring" if t < RING_INNER_T else "ring_inner"
        loops.append((pts, key))
    # The groove's floor, from the collar's inner edge to the dome's foot.
    edge = [outline_point(a, DOME_CENTRE, INNER_A - 0.1, INNER_B - 0.1) for a in angles]
    loops.append(([(x, y, GROOVE_Z) for x, y in edge], "groove"))
    for scale, h in dome_profile():
        pts = [(*outline_point(a, DOME_CENTRE, DOME_A, DOME_B, scale=scale), GROOVE_Z + h) for a in angles]
        loops.append((pts, "dome_outer" if scale > DOME_INNER + 1e-6 else "dome_inner"))

    bm = bmesh.new()
    rings = [[bm.verts.new(p) for p in pts] for pts, _ in loops]
    keys = []
    n = SEGMENTS
    for i in range(len(rings) - 1):
        # The band between two rings takes the material of its outer ring; the collar's inner wall
        # down into the groove is the groove's.
        key = "groove" if loops[i + 1][1] == "groove" else loops[i][1]
        for s in range(n):
            bm.faces.new((rings[i][s], rings[i][(s + 1) % n], rings[i + 1][(s + 1) % n], rings[i + 1][s]))
            keys.append(key)
    apex = bm.verts.new((DOME_CENTRE[0], DOME_CENTRE[1], GROOVE_Z + DOME_H))
    for s in range(n):
        bm.faces.new((rings[-1][s], rings[-1][(s + 1) % n], apex))
        keys.append("dome_inner")
    bottom = bm.verts.new((RING_CENTRE[0], RING_CENTRE[1], 0.0))
    for s in range(n):
        bm.faces.new((rings[0][(s + 1) % n], rings[0][s], bottom))
        keys.append("ring_outer")
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    names = []
    for key in keys:
        if mats[key].name not in names:
            names.append(mats[key].name)
            mesh.materials.append(mats[key])
    for poly, key in zip(mesh.polygons, keys):
        poly.material_index = names.index(mats[key].name)
    k.recalc_normals(obj)
    return k.smooth(obj, 50)


# --- Colours --------------------------------------------------------------------------------------

def glow(name, index, strength, roughness=0.3, metallic=0.0):
    return k.material(name, palette=index, metallic=metallic, roughness=roughness, emission=k.level_palette()[index],
                      emission_strength=strength)


def green():
    ring = glow("domeg_ring", 0xca, 0.8, roughness=0.3)
    dome = k.material("domeg_dome", palette=0x27, metallic=0.1, roughness=0.2)
    return {"ring_outer": ring, "ring": ring, "ring_inner": glow("domeg_ring_inner", 0xc6, 0.55, roughness=0.35),
            "groove": k.material("domeg_groove", palette=0x04, metallic=0.4, roughness=0.5),
            "dome_outer": dome, "dome_inner": dome}


def green_55():
    ring = glow("domeg55_ring", 0xcf, 1.2, roughness=0.25)
    return {"ring_outer": ring, "ring": ring, "ring_inner": glow("domeg55_ring_inner", 0xcb, 0.9),
            "groove": glow("domeg55_groove", 0x26, 0.4, roughness=0.4),
            "dome_outer": glow("domeg55_dome_band", 0x27, 0.25, roughness=0.2, metallic=0.1),
            "dome_inner": glow("domeg55_dome", 0xc7, 0.5, roughness=0.2, metallic=0.1)}


def red():
    ring = k.material("domer_ring", palette=0xea, metallic=0.45, roughness=0.34)
    dome = k.material("domer_dome", palette=0x47, metallic=0.1, roughness=0.2)
    return {"ring_outer": ring, "ring": ring,
            "ring_inner": k.material("domer_ring_inner", palette=0xe6, metallic=0.45, roughness=0.4),
            "groove": k.material("domer_groove", palette=0x04, metallic=0.4, roughness=0.5),
            "dome_outer": dome, "dome_inner": dome}


def red_131():
    return {"ring_outer": glow("domer131_ring_edge", 0x48, 0.6),
            "ring": glow("domer131_ring", 0x7a, 1.5, roughness=0.25),
            "ring_inner": glow("domer131_ring_inner", 0xeb, 0.4, roughness=0.35),
            "groove": glow("domer131_groove", 0x46, 0.6, roughness=0.4),
            "dome_outer": glow("domer131_dome_band", 0x46, 0.5, roughness=0.2, metallic=0.1),
            "dome_inner": k.material("domer131_dome", palette=0xe6, metallic=0.3, roughness=0.2)}


# (model, sprite, colours, the ramps of the collar and dome in that sprite: the turret's own pixels)
FRAMES = [
    ("dome_green", 17, green, (12, 2)),
    ("dome_green_55", 55, green_55, (12, 2, 1)),
    ("dome_red", 93, red, (14, 4)),
    ("dome_red_131", 131, red_131, (7, 4, 14)),
]


# --- Checking -------------------------------------------------------------------------------------

def collar_mask(sheet, sprite, ramps):
    """The turret's own pixels in the sprite (its collar's and dome's ramps) and everything they
    enclose (the dark groove), without the ground the sprite paints round it."""
    from sprite_profile import sprite_indices
    indices = sprite_indices(sheet, sprite)
    h, w = len(indices), len(indices[0])
    own = [[v is not None and v >> 4 in ramps for v in row] for row in indices]
    outside = [[False] * w for _ in range(h)]
    todo = [(x, y) for y in range(h) for x in range(w) if (x in (0, w - 1) or y in (0, h - 1)) and not own[y][x]]
    for x, y in todo:
        outside[y][x] = True
    while todo:
        x, y = todo.pop()
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < w and 0 <= ny < h and not outside[ny][nx] and not own[ny][nx]:
                outside[ny][nx] = True
                todo.append((nx, ny))
    return [[not outside[y][x] for x in range(w)] for y in range(h)]


def top_coverage(w, h, supersample=4):
    """The model's top view at the sprite's resolution: rows of bools (as tyrkit.check_silhouette)."""
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.film_transparent = True
    scene.render.resolution_x, scene.render.resolution_y = w * supersample, h * supersample
    scene.render.resolution_percentage = 100
    data = bpy.data.cameras.new("collar_check")
    data.type = "ORTHO"
    data.ortho_scale = max(w, h)
    cam = bpy.data.objects.new("collar_check", data)
    cam.location = (0, 0, 100)
    scene.collection.objects.link(cam)
    scene.camera = cam
    path = os.path.join(bpy.app.tempdir or "/tmp", "domes_collar.png")
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    image = bpy.data.images.load(path)
    rw, rh = image.size
    pixels = list(image.pixels)
    covered = [[False] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            alpha = 0.0
            for sy in range(supersample):
                for sx in range(supersample):
                    px, py = x * supersample + sx, rh - 1 - (y * supersample + sy)
                    alpha += pixels[(py * rw + px) * 4 + 3]
            covered[y][x] = alpha / supersample ** 2 > 0.5
    bpy.data.objects.remove(cam)
    bpy.data.images.remove(image)
    return covered


def check_collar(sheet, sprite, ramps):
    mask = collar_mask(sheet, sprite, ramps)
    h, w = len(mask), len(mask[0])
    covered = top_coverage(w, h)
    both = sum(covered[y][x] and mask[y][x] for y in range(h) for x in range(w))
    either = sum(covered[y][x] or mask[y][x] for y in range(h) for x in range(w))
    print("collar outline overlap: %.3f" % (both / max(either, 1)))
    for y in range(h):
        print("".join("#" if covered[y][x] and mask[y][x] else "+" if covered[y][x] else "-" if mask[y][x] else "."
                      for x in range(w)))
    return both / max(either, 1)


def triangles(obj):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    mesh = obj.evaluated_get(depsgraph).to_mesh()
    mesh.calc_loop_triangles()
    count = len(mesh.loop_triangles)
    obj.evaluated_get(depsgraph).to_mesh_clear()
    return count


def build():
    options = k.args()
    outdir = options.get("outdir", os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "enemies"))
    for name, sprite, colours, ramps in FRAMES:
        k.reset()
        obj = turret(name, colours())
        print("== %s (A %d): %d triangles, %d materials" % (name, sprite, triangles(obj), len(obj.data.materials)))
        if "check" in options:
            sheet = os.path.join(options["check"], "enemy_A.png")
            check_collar(sheet, sprite, ramps)
            k.check_silhouette(sheet, sprite)  # the whole sprite, its painted ground included
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        k.export(os.path.join(outdir, name + ".glb"))
        if "preview" in options:
            k.preview(options["preview"] + name)


if __name__ == "__main__":
    build()
