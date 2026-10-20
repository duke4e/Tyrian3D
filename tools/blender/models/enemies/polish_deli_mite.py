"""UNDERDELI's small purple crawler with a green window: sheet ^ (x5e in models.cfg) sprite 68, 1x1 (12 x 14 pixels);
enemy 40 (one frame), a ground enemy (ground2 slots) that the level sends down the screen in lines along its edges
(UNDERDELI's events 10-215 and on: x 20 and 240, vy 2). Polished 2026-10-20; it replaces wave3_i.py's deli_mite() (pixel
regions raised into lumps). models.cfg: model deli_mite enemies/deli_mite.glb origin; sprite x5e 68 deli_mite yaw=0
height=-4 (it crawls on the floor: models drawn at their origin stand at the ground enemies' layer, 4 pixels over the
terrain; height=-4 sets it on it).

As the sprite and its 4x upscale draw it (columns and rows of the 12 x 14 sprite; it is symmetric about the middle of
column 6): a round purple carapace (columns 1-11 of rows 0-7), lit at its upper left; in its top a window (columns 5-7
of rows 2-4), green with a purple bar down its middle, framed in light purple (rows 1-3); a pod on either side (columns
1-3 and 9-11 of rows 3-6); a dark band under the carapace (row 7); a bright collar (columns 4-8 of row 8) and a tail
tapering down the screen (columns 4-8 of rows 9-13), lit down its ridge (column 6).

Built as a small lofted carapace with the window's well cut into it (a boolean), the green glass and its bar in it,
the pods, the collar and the tail lathed or lofted; the purples in bands of the light (polish_orb_red.band_split). The
window glows faintly in its own green (emission 0.3: a lit cockpit, under the game's bloom).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the floor (z = 0); origin at the
sprite's centre (pixel edge 6, 7): column c's left edge is x = c - 6, row r's top edge y = 7 - r.

Replaces wave3_i.py's deli_mite(): remove it with its @model("deli_mite", ...) registration and its line in the
docstring, and wave3_i_art.py's S68 (only deli_mite() reads it), so that it doesn't overwrite this model.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouette against
enemy_x5e.png's sprite 68), --preview <prefix>.
"""
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_orb_red import band_split  # noqa: E402

AXIS_X = 0.5                    # symmetric about the middle of column 6


def XE(c):
    return c - 6.0


def YE(r):
    return 7.0 - r


# The carapace along the sprite's rows: (row, half-width, height, superellipse power); its bottom at BASE.
CARAPACE = [(0.15, 1.6, 2.3, 2.2), (0.6, 2.9, 3.4, 2.3), (1.4, 3.7, 4.1, 2.4), (2.6, 4.0, 4.5, 2.5),
            (4.2, 4.05, 4.55, 2.5), (5.6, 3.8, 4.25, 2.5), (6.6, 3.3, 3.7, 2.4), (7.4, 2.6, 3.0, 2.3),
            (7.9, 1.9, 2.4, 2.2)]
BASE = 0.15
WINDOW = (6.5, 3.2, 1.95, 1.8)  # its centre (column, row) and half-width, half-height
WINDOW_FLOOR = 3.3
PODS = [(2.7, 4.7, 1.45, 2.0, 2.3)]  # the left pod: column, row, half-width, half-height, height (mirrored)
COLLAR = (8.35, 2.55, 0.55, 2.1)  # row, radius, half-length, axis height
# The tail: (row, half-width, height) from the collar down to its tip.
TAIL = [(8.6, 2.3, 3.0), (9.6, 2.45, 2.9), (10.6, 2.25, 2.6), (11.6, 1.75, 2.2), (12.6, 1.15, 1.7), (13.5, 0.35, 1.1),
        (13.85, 0.05, 0.8)]
TAIL_GROOVES = [10.15, 11.75]


def materials():
    glow = k.level_palette()

    def mat(name, index, metallic=0.25, roughness=0.32):
        return k.material(name, palette=index, metallic=metallic, roughness=roughness)
    return {
        "dark": mat("mite_dark", 0x52, 0.2, 0.5),
        "shade": mat("mite_shade", 0x55, 0.25, 0.36),
        "purple": mat("mite_purple", 0x57, 0.25, 0.32),
        "lit": mat("mite_lit", 0x59, 0.25, 0.3),
        "light": mat("mite_light", 0x5b, 0.25, 0.26),
        "bright": mat("mite_bright", 0x5d, 0.25, 0.22),
        "glass_dark": k.material("mite_glass_dark", palette=0xc3, metallic=0.1, roughness=0.12, emission=glow[0xc3],
                                 emission_strength=0.25),
        "glass": k.material("mite_glass", palette=0xc6, metallic=0.1, roughness=0.08, emission=glow[0xc6],
                            emission_strength=0.22),
    }


def light_bands(obj, m, levels=(-0.2, 0.35, 0.75, 0.93)):
    """Purple bands by how much a vertex faces the light (from the upper left and above): shade, purple, lit, light."""
    sun = Vector((-0.45, 0.45, 0.77)).normalized()
    values = [v.normal.dot(sun) for v in obj.data.vertices]
    band_split(obj, values, [(-9.0, m["dark"]), (levels[0], m["shade"]), (levels[1], m["purple"]),
                             (levels[2], m["lit"]), (levels[3], m["light"])])
    k.smooth(obj, 60)


def loft_along(name, sections, mat, base, segments=24, end_round=True):
    """A hull along the rows: sections (row, half-width, height, power), flat underneath at base."""
    rings = []
    for r, hw, h, power in sections:
        hh = (h - base) / 2
        rings.append(k.ring(YE(r), max(hw, 0.05), max(hh, 0.05), segments, z=base + hh, x=AXIS_X, power=power))
    first, last = sections[0], sections[-1]
    return k.loft(name, rings, mat, start_point=(AXIS_X, YE(first[0]) + 0.12, base + (first[2] - base) * 0.5),
                  end_point=(AXIS_X, YE(last[0]) - 0.1, base + (last[2] - base) * 0.5))


def carapace(m):
    rows = k.profile([(r, w, h, p) for r, w, h, p in CARAPACE], 0.4)
    body = loft_along("carapace", rows, m["purple"], BASE)
    # The window's well, cut from above.
    c, r, hw, hh = WINDOW
    cx, cy = XE(c), YE(r)
    well = mk.lathe("window_cut", [(1.0, WINDOW_FLOOR), (1.0, 9.0)], (cx, cy), None, 28, squash=(hw, hh), power=2.6)
    mk.boolean(body, well, "DIFFERENCE")
    mk.cleanup(body, dissolve=0.0)
    k.smooth(body, 60)
    light_bands(body, m)

    def pick(cc, n):
        inside = ((cc.x - cx) / (hw + 0.1)) ** 2 + ((cc.y - cy) / (hh + 0.1)) ** 2 < 1.0
        return m["dark"] if inside and cc.z < 4.2 else None
    mk.paint(body, pick)
    # The frame round the window: a light purple ring standing on the carapace.
    frame = mk.lathe("window_frame", [(1.0, WINDOW_FLOOR + 0.5), (1.04, 4.3), (1.12, 4.62), (1.26, 4.66), (1.36, 4.42),
                                      (1.38, 3.9)], (cx, cy), m["light"], 28, squash=(hw, hh), power=2.6)
    k.smooth(frame, 50)
    mk.paint(frame, lambda cc, n: m["bright"] if n.z > 0.75 and cc.y > cy else m["light"] if n.z > 0.2 else m["shade"])
    # The glass: a low green dome, its lower part darker, and the purple bar down its middle.
    glass = mk.dome("window_glass", (cx, cy), (hw + 0.02, hh + 0.02, 0.85), WINDOW_FLOOR + 0.25, m["glass"], 28, 5,
                    power=2.6)
    band_split(glass, [v.co.y - cy for v in glass.data.vertices], [(-9.0, m["glass_dark"]), (-0.55 * hh, m["glass"])])
    k.smooth(glass, 60)
    bar = mk.box("window_bar", cx - 0.34, cx + 0.34, cy - hh * 0.98, cy + hh * 0.3, WINDOW_FLOOR, 4.5, m["lit"])
    mk.bevel(bar, 0.18, 2, 35)
    mk.shade(bar, 35)


def pods(m):
    for i, (c, r, hw, hh, h) in enumerate(PODS):
        pod = k.ellipsoid(f"pod{i}", (XE(c), YE(r), BASE + h * 0.42), (hw, hh, h * 0.62), m["purple"], 18, 9)
        k.smooth(pod, 70)
        light_bands(pod, m)


def tail(m):
    """The collar between carapace and tail; the tail tapering down the screen, two grooves round it."""
    r, rad, half, axis = COLLAR
    rings = []
    for t, f in ((-1.0, 0.82), (-0.6, 1.0), (0.6, 1.0), (1.0, 0.82)):
        rings.append(k.ring(YE(r + t * half), rad * f, rad * f * 0.85, 24, z=axis, x=AXIS_X))
    collar = k.loft("collar", rings, m["bright"])
    k.smooth(collar, 50)
    sun = Vector((-0.45, 0.45, 0.77)).normalized()
    band_split(collar, [v.normal.dot(sun) for v in collar.data.vertices],
               [(-9.0, m["shade"]), (0.0, m["light"]), (0.6, m["bright"])])
    k.smooth(collar, 50)
    sections = [(r, w, h, 2.3) for r, w, h in TAIL]
    body = loft_along("tail", k.profile(sections, 0.3), m["purple"], BASE, segments=22)
    k.smooth(body, 60)
    light_bands(body, m)
    for i, rr in enumerate(TAIL_GROOVES):
        w = next(w for r0, w, h in reversed(TAIL) if r0 <= rr)
        groove = k.loft(f"tail_groove{i}", [k.ring(YE(rr + d), w * 0.98 + 0.08, 1.05, 22, z=BASE + 1.1, x=AXIS_X,
                                                   top=1.32 * (0.95 - 0.05 * i), bottom=0.9) for d in (-0.14, 0.14)],
                        m["shade"])
        k.smooth(groove, 40)


def clip_below(obj, z):
    """Cuts an object off below z, closing the cut (nothing reaches under the floor)."""
    import bmesh
    if min(v.co.z for v in obj.data.vertices) >= z - 1e-4:
        return
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    res = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-5, plane_co=(0, 0, z),
                                 plane_no=(0, 0, -1), clear_outer=True)
    edges = [e for e in res["geom_cut"] if isinstance(e, bmesh.types.BMEdge) and e.is_valid and e.is_boundary]
    if edges:
        bmesh.ops.holes_fill(bm, edges=edges, sides=0)
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()


def build():
    k.reset()
    options = k.args()
    m = materials()
    carapace(m)
    pods(m)
    left = [o for o in mk.meshes() if o.name.startswith("pod")]
    for obj in left:  # the right pod: the left one mirrored about the middle
        copy = obj.copy()
        copy.data = obj.data.copy()
        copy.name = obj.name + "_r"
        bpy.context.scene.collection.objects.link(copy)
        copy.data.transform(Matrix.Translation((2 * AXIS_X, 0, 0)) @ Matrix.Scale(-1, 4, (1, 0, 0)))
        copy.data.flip_normals()
    tail(m)
    parts = mk.meshes()
    for obj in parts:
        mk.apply(obj)
        clip_below(obj, 0.0)
    bpy.context.view_layer.update()
    if "check" in options:
        mask = k.sprite_mask(os.path.join(options["check"], "enemy_x5e.png"), 68, large=False)
        mk.compare("deli_mite (x5e 68)", mk.coverage(parts, 12, 14), mask)
    bpy.context.scene.view_settings.view_transform = "Standard"
    mk.report("deli_mite", parts, os.path.join(mk.outdir(options), "deli_mite.glb"))
    if "preview" in options:
        mk.preview(options["preview"] + "deli_mite", parts, size=(12, 14), scale=32)


if __name__ == "__main__":
    build()
