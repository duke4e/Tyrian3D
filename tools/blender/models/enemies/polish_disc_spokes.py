"""The bronze pod of MINERS (sheet L sprite 281, 2x2: a 24 x 24 disc in the 24 x 28 cell; its
animation 281, 283, 283, 246, 246), polished (2026-10-18; it replaces later_episodes.py's disc with
spokes). models.cfg: sprite l 281 disc_spokes, frame l 283 disc_spokes_283, frame l 246
disc_spokes_246.

As the 4x upscale draws it: a domed bronze pod whose top is cut into eight segments by dark grooves,
four arms along the axes (columns 9-14 and rows 11-16 of the sprite, narrower near the middle) and four wedges in the quarters
between them, closed round a red gem in the middle (281). The wedges then draw back from the middle
(283: to about 7 pixels out, 246: 8.5) and open a red glowing X into the pod, the gem turning orange
and then yellow-white.

Origin at the disc's centre (the sprite's pixel 12, 14); +Y up the sprite, +Z towards the camera.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <enemy_L.png> (the
silhouette of each frame), --preview <prefix>.
"""
import math
import os
import sys

import bmesh
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
from polish_sphere_nozzle import smoothstep, split_along  # noqa: E402

RADIUS = 12.0           # the disc, its outline included
TOP_RADIUS = 11.3       # where the top's heightfield meets the rounded rim
# The arms taper towards the middle: half as wide as ARM_WIDTH_0 + ARM_WIDTH_SLOPE * the distance
# out (the sprite's columns 9-14 at the rim, 10-13 near the gem).
ARM_WIDTH_0, ARM_WIDTH_SLOPE = 1.8, 0.15
GEM_RADIUS = 2.9        # the gem in the middle (columns 9-14, rows 11-16 less the grooves)
GROOVE = 0.32           # half the width of the grooves between the segments
RIM_Z, DOME = 1.7, 3.3  # the dome: its height at the rim and how much higher it is in the middle
ARM_RAISE, WEDGE_RAISE = 0.55, 0.75  # the segments' rounded tops above the grooves' floors
GROOVE_DEPTH = 0.3      # the grooves' floors below the dome
ARM_START_OPEN = 4.0    # while the pod is open, the arms begin this far out
PIT_DEPTH = 1.5         # the open X: its floor below the dome

# The frames: (model name, sprite, how far the wedges are drawn back (0: closed), the gem's palette
# indices from its middle out with their emission strengths, the X's floor from its middle out).
FRAMES = [
    ("disc_spokes", 281, 0.0, [(0x77, 0.8), (0x75, 0.55), (0x73, 0.3)], []),
    ("disc_spokes_283", 283, 7.2, [(0x79, 1.8), (0x77, 1.4), (0x76, 1.1)],
     [(0x76, 1.5), (0x75, 1.15), (0x73, 0.8)]),
    ("disc_spokes_246", 246, 8.4, [(0x7e, 2.6), (0x7c, 2.1), (0x7a, 1.7)],
     [(0x77, 1.8), (0x76, 1.35), (0x74, 0.95)]),
]
GEM_BANDS = (1.1, 2.0)          # the gem's rings: radii where its colour changes
FLOOR_BANDS = (4.6, 6.3)       # the X's floor: radii where its colour changes


def dome(r):
    return RIM_Z + DOME * math.sqrt(max(0.0, 1 - (r / (RADIUS + 0.8)) ** 2))


def cross(x, y):
    """Negative on the arms, positive on the wedges: how far the point is past the arms' edges."""
    across, along = min(abs(x), abs(y)), max(abs(x), abs(y))
    return (across - ARM_WIDTH_0 - ARM_WIDTH_SLOPE * along) / math.sqrt(1 + ARM_WIDTH_SLOPE ** 2)


def arm_start(open_to):
    """Where the arms begin: at the gem, or, while the pod is open, short of it (the X joins round it)."""
    return ARM_START_OPEN if open_to > 0 else GEM_RADIUS


def region(x, y, open_to):
    """gem, groove, arm, wedge or pit (the open X)."""
    r = math.hypot(x, y)
    g = GROOVE
    if r < GEM_RADIUS - g:
        return "gem"
    if open_to <= 0 and r < GEM_RADIUS + g:
        return "groove"
    c = cross(x, y)
    if abs(c) < g:
        return "groove" if open_to <= 0 or r > open_to - g or c < 0 else "wall"
    if c < 0:
        start = arm_start(open_to)
        return "arm" if r > start + g else "wall" if r > start - g else "pit"
    if open_to <= 0:
        return "wedge"
    return "wedge" if r > open_to + g else "wall" if r > open_to - g else "pit"


def pit_floor(r, open_to):
    return dome(r) - PIT_DEPTH + 0.3 * smoothstep(GEM_RADIUS, open_to, r)


def height(x, y, open_to):
    """The top's height: the dome, the segments raised from the grooves' floors with rounded edges,
    the open X sunk into it."""
    r = math.hypot(x, y)
    base = dome(r)
    g = GROOVE
    kind = region(x, y, open_to)
    t = min(1.0, r / (GEM_RADIUS - g))
    if kind == "gem":
        if open_to > 0:  # a glowing bulb rising out of the X's floor
            return pit_floor(r, open_to) + 1.9 * math.sqrt(max(0.0, 1 - t * t))
        return base - 0.35 + 0.75 * math.sqrt(max(0.0, 1 - t * t))
    if kind == "pit":
        return pit_floor(r, open_to)
    c = cross(x, y)
    if kind in ("groove", "wall"):
        if open_to <= 0:
            return base - GROOVE_DEPTH
        # The walls down into the X: from the grooves' floor at the segments' edges to the X's floor.
        sides = smoothstep(-g, g, c) * smoothstep(open_to + g, open_to - g, r)
        ends = smoothstep(arm_start(open_to) + g, arm_start(open_to) - g, r) if c < -g else 0.0
        q = max(sides, ends)
        return base - GROOVE_DEPTH + (pit_floor(r, open_to) - base + GROOVE_DEPTH) * q
    # The distance to the segment's edges (pixels): its grooves, the X's and the rim.
    if kind == "arm":
        d = min(abs(c), r - arm_start(open_to), TOP_RADIUS + 0.6 - r) - g
        raise_by = ARM_RAISE
    else:
        inner = r - open_to if open_to > 0 else 99.0
        d = min(abs(c), inner, TOP_RADIUS + 0.6 - r) - g
        raise_by = WEDGE_RAISE
    s = smoothstep(0.0, 1.5, d)
    return base - GROOVE_DEPTH + (GROOVE_DEPTH + raise_by) * math.sqrt(s)


def top_grid(bm, rings=64, segments=160):
    """A polar grid over the top (rings to TOP_RADIUS), flat; its vertices in rings, outermost last."""
    centre = bm.verts.new((0.0, 0.0, 0.0))
    grid = []
    for i in range(1, rings + 1):
        r = TOP_RADIUS * (i / rings) ** 0.85
        grid.append([bm.verts.new((r * math.cos(2 * math.pi * j / segments), r * math.sin(2 * math.pi * j / segments),
                                   0.0)) for j in range(segments)])
    for j in range(segments):
        bm.faces.new((centre, grid[0][j], grid[0][(j + 1) % segments]))
    for a, b in zip(grid, grid[1:]):
        for j in range(segments):
            bm.faces.new((a[j], b[j], b[(j + 1) % segments], a[(j + 1) % segments]))
    return grid[-1]


def pod(name, open_to, mats):
    bm = bmesh.new()
    outer = top_grid(bm)
    # The borders between the segments first, on the flat grid, so that they run straight and round.
    radii = (GEM_RADIUS - GROOVE, GEM_RADIUS + GROOVE) + GEM_BANDS
    if open_to > 0:
        start = arm_start(open_to)
        radii += (start - GROOVE, start + GROOVE, open_to - GROOVE, open_to + GROOVE) + FLOOR_BANDS
    for t in radii:
        split_along(bm, {v: math.hypot(v.co.x, v.co.y) for v in bm.verts}, t)
    for t in (-GROOVE, GROOVE):
        split_along(bm, {v: cross(v.co.x, v.co.y) for v in bm.verts}, t)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])

    # The rim (rounded down to the ground) and the bottom, from the top's outer ring.
    rim_profile = [(TOP_RADIUS + 0.35, -0.12), (TOP_RADIUS + 0.62, -0.42), (RADIUS - 0.05, -0.9), (RADIUS, -1.5),
                   (RADIUS - 0.05, -dome(TOP_RADIUS) + 0.5), (RADIUS - 0.5, -dome(TOP_RADIUS))]
    top_edge_z = height(TOP_RADIUS, 0.0, open_to)
    previous = outer
    rims = []
    for r, dz in rim_profile:
        ring = []
        for v in outer:
            a = math.atan2(v.co.y, v.co.x)
            ring.append(bm.verts.new((r * math.cos(a), r * math.sin(a), top_edge_z + dz)))
        for j in range(len(ring)):
            bm.faces.new((previous[j], ring[j], ring[(j + 1) % len(ring)], previous[(j + 1) % len(ring)]))
        rims.append(ring)
        previous = ring
    bottom = bm.verts.new((0.0, 0.0, top_edge_z - dome(TOP_RADIUS)))
    for j in range(len(previous)):
        bm.faces.new((previous[j], bottom, previous[(j + 1) % len(previous)]))

    # The top's relief.
    rim_verts = {v for ring in rims for v in ring} | {bottom}
    for v in bm.verts:
        if v not in rim_verts:
            v.co.z = height(v.co.x, v.co.y, open_to)

    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    slots = []
    for poly in mesh.polygons:
        c = poly.center
        if poly.normal.z < 0.2 and math.hypot(c.x, c.y) > TOP_RADIUS + 0.2:
            key = "rim"
        else:
            kind = region(c.x, c.y, open_to)
            r = math.hypot(c.x, c.y)
            if kind == "gem":
                key = ("gem", sum(r > b for b in GEM_BANDS))
            elif kind == "pit":
                key = ("pit", sum(r > b for b in FLOOR_BANDS))
            elif kind == "wall":
                key = "wall"
            else:
                key = kind
        mat = mats[key]
        if mat.name not in [m.name for m in mesh.materials]:
            mesh.materials.append(mat)
        slots.append([m.name for m in mesh.materials].index(mat.name))
    for poly, slot in zip(mesh.polygons, slots):
        poly.material_index = slot
    k.recalc_normals(obj)
    # Faces lying flat with their neighbours merged, the borders between colours kept.
    mod = obj.modifiers.new("dissolve", "DECIMATE")
    mod.decimate_type = "DISSOLVE"
    mod.angle_limit = math.radians(3.5)
    mod.delimit = {"MATERIAL"}
    return k.smooth(obj, 40)


def materials(gem, pit):
    m = {
        "arm": k.material("dspokes_arm", palette=0x13, metallic=0.45, roughness=0.36),
        "wedge": k.material("dspokes_wedge", palette=0x16, metallic=0.45, roughness=0.3),
        # The X's walls: the sprite's dark red edge round it, lit from below.
        "wall": k.material("dspokes_wall", palette=0x71, roughness=0.5, emission=k.level_palette()[0x72],
                           emission_strength=0.6),
        "groove": k.material("dspokes_groove", palette=0x11, metallic=0.3, roughness=0.6),
        "rim": k.material("dspokes_rim", palette=0x12, metallic=0.4, roughness=0.45),
    }
    for i, (index, glow) in enumerate(gem):
        m[("gem", i)] = k.material(f"dspokes_gem_{index:x}", palette=index, roughness=0.25,
                                   emission=k.level_palette()[index], emission_strength=glow)
    for i, (index, glow) in enumerate(pit):
        m[("pit", i)] = k.material(f"dspokes_pit_{index:x}", palette=index, roughness=0.5,
                                   emission=k.level_palette()[index], emission_strength=glow)
    return m


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
    for name, sprite, open_to, gem, pit in FRAMES:
        k.reset()
        obj = pod(name, open_to, materials(gem, pit))
        print("== %s (L %d): %d triangles, %d materials" % (name, sprite, triangles(obj), len(obj.data.materials)))
        if "check" in options:
            k.check_silhouette(options["check"], sprite)
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        k.export(os.path.join(outdir, name + ".glb"))
        if "preview" in options:
            k.preview(options["preview"] + name)


if __name__ == "__main__":
    build()
