"""The steel chevron with the red fins of FLEET and THE CORE (sheet K sprite 207, 2x2: 24 x 24 pixels in the
24 x 28 cell; top layer, about 80 of them; not animated), polished (2026-10-19; it replaces
wave3_o_machines.py's fin_chevron(), a lumpy grey V with two red loft fins). models.cfg: sprite k 207
fin_chevron yaw=0.

As the sprite and its 4x upscale draw it: a grey steel V pointing down the screen. Its lower part is
a broad plate (rows 15-26) narrowing in 45 degree sides to a flat front (columns 8-15 of row 26),
its top light grey, its front edge bevelled (rows 24-25, darker), and in its middle a vent: a U of
dark slot (columns 10-13 of rows 19-22) round a short block, a bright frame either side of it and a
bright ledge under it (row 23). Two tall prongs rise from the plate's ends (columns 0-4 and 19-23, up
to row 3), their outer sides upright, their inner sides slanting out to their points, darker than
the plate, their inner edges lit. In the V between them lie two glossy red fins (the sprite's ramp 7:
columns 3-10 and 12-19 of rows 8-17), each a broad blade leaning out from the V's bottom to the prong
beside it, a glowing streak along its inner edge (shades 8-13), a dark gap between the two (columns
11-12) and a dark slot at their feet (row 18).

The model: the steel body as a CAD part (polish_machine_kit.py): the plate's plan extruded, its front
chamfered; the prongs wedges whose tops rise towards their points and towards their outer sides (so
they face down the screen and inwards, darker than the plate in the sun from the top left, as the
sprite draws them), joined to it; its edges rounded; the vent and the fins' slot cut into its top, a
block standing in the vent and a ledge under it. The steel is painted as polished steel shows the sky
(polish_spike_mine.py's chrome: the bands of the surface's slope, a dark line where it turns away),
lit by the game's sun. The fins are glossy red blades lofted through the sprite's rows along their
leaning axes (straight: the sprite's fin middles lie on a line 27 degrees from upright), rounded in
section, their roots in the slot, their outer edges against the prongs; they glow red, brighter along
their inner edges where the sprite's streaks run (painted in bands cut along smooth contours).

Origin at the sprite's centre (pixel 12, 14); +Y up the screen, +Z towards the camera; the body stands
on z = 0 (the game centres top-layer objects in height). The sprite is symmetric about its column
edge 12 (x = 0), the model too.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the
silhouette against K 207 in <dir>/enemy_K.png), --preview <prefix>.
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
import polish_flame_drop as fire  # noqa: E402  (its monotone curves)
from polish_spike_mine import join  # noqa: E402

# The plate's plan (pixel edges: the front, row 26's bottom; the 45 degree sides up to the plate's
# ends, row 19; up the prongs' outer sides to the V's bottom, row 15's top) and its height.
PLATE = [(-4.0, -13.0), (4.0, -13.0), (12.0, -5.0), (12.0, -1.0), (-12.0, -1.0), (-12.0, -5.0)]
HEIGHT = 3.0
# The front chamfer (rows 24-25): the top falls from HEIGHT at y = CHAMFER[0] to HEIGHT - CHAMFER[1]
# at the front (y = -13).
CHAMFER = (-10.4, 1.5)
# The right prong's plan (the left one its mirror image): from its foot (a little into the plate) up
# its outer side to its point (row 3), down its inner side through the inner edges of the sprite's
# prong pixels to the V's bottom; its top a plane through its inner foot (at HEIGHT), its outer foot
# (PRONG_OUTER above HEIGHT) and its point (PRONG_RISE above HEIGHT).
PRONG = [(6.6, -1.6), (12.0, -1.6), (12.0, 10.2), (11.75, 11.0), (11.25, 10.6), (10.5, 8.5), (6.6, -1.0)]
PRONG_OUTER, PRONG_RISE = 0.7, 3.3
BEVEL = 0.5
# The vent (columns 9-14 of rows 19-23): the slot (x half-width, y from, y to, depth), the block in it
# (x half-width, y from, y to, its top below HEIGHT), the ledge under it (x half-width, y from, y to,
# its height above HEIGHT).
SLOT = (2.05, -9.2, -4.4, 1.3)
BLOCK = (1.0, -8.1, -5.0, 0.3)
LEDGE = (2.7, -10.25, -9.35, 0.3)
# The fins' slot in the top (row 18 and above): x half-width, y from, y to, depth.
FIN_SLOT = (5.6, -5.0, -0.5, 1.6)
# The left fin (the right one its mirror image): its middle at y is FIN_AXIS[0] + FIN_AXIS[1] * y (the
# sprite's fin pixels' middles, the right one's mirrored, fitted); its half-width across the screen
# row by row (y, half-width), closed at its root in the slot and past its top row; its axis' height
# at its root and its top end, its upper and lower half-heights (fractions of the half-width), its
# roundness (a superellipse's power).
FIN_AXIS = (-4.27, -0.517)
FIN_HALF = [(-4.8, 0.0), (-4.3, 1.5), (-3.5, 2.3), (-2.5, 2.85), (-1.0, 3.2), (0.5, 3.4), (2.0, 3.3), (3.5, 2.95),
            (4.5, 2.5), (5.3, 1.85), (5.85, 1.0), (6.1, 0.0)]
FIN_Z = (2.0, 4.4)
FIN_UP, FIN_DOWN, FIN_POWER = 0.72, 0.45, 2.3
# The fin's paint: the streak along its inner edge, a ridge of brightness across it (its middle and
# width, in fractions of the half-width towards the V's middle), strongest about STREAK_Y (and that
# wide), fading out at its ends; its bands (warm, hot); its outer side dark (beyond OUTER across).
STREAK_ACROSS, STREAK_WIDTH = 0.36, 0.27
STREAK_Y, STREAK_SPREAD = 0.8, 2.8
STREAK_BANDS = (0.32, 0.7)
OUTER = 0.62

# The steel's bands of the surface's normal z (lowest, palette index, metallic, roughness, emission):
# the walls, a dark line, the bevels and the top.
STEEL = [(-9.0, 0x04, 0.45, 0.4, 0.04), (0.35, 0x06, 0.45, 0.32, 0.05), (0.62, 0x03, 0.5, 0.35, 0.03),
         (0.72, 0x0b, 0.45, 0.24, 0.07), (0.93, 0x09, 0.45, 0.26, 0.06)]


def materials():
    pal = k.level_palette()
    m = {"steel": [(lowest, k.material(f"chevron_steel_{index:02x}", palette=index, metallic=metallic,
                                       roughness=roughness, emission=pal[index], emission_strength=glow))
                   for lowest, index, metallic, roughness, glow in STEEL],
         "dark": k.material("chevron_dark", palette=0x02, metallic=0.3, roughness=0.5),
         # The prongs' tops, darker than the plate's as the sprite draws them.
         "prong": k.material("chevron_prong", palette=0x07, metallic=0.45, roughness=0.28, emission=pal[0x07],
                             emission_strength=0.05)}
    for key, index, glow in (("fin_dark", 0x72, 0.3), ("fin", 0x75, 0.45), ("fin_warm", 0x78, 0.8),
                             ("fin_hot", 0x7b, 1.2)):
        m[key] = k.material(f"chevron_{key}", palette=index, metallic=0.1, roughness=0.2, emission=pal[index],
                            emission_strength=glow)
    return m


def steel_band(m, n):
    return m["steel"][sum(n.z > lowest for lowest, _ in m["steel"][1:])][1]


def body(m):
    plate = mk.prism("body", PLATE, 0.0, HEIGHT + 1.0, m["steel"][-1][1])
    # The front chamfer and the flat top: a side profile (y, z) extruded across.
    y0, drop = CHAMFER
    slope = drop / (y0 + 13.0)
    side = [(-14.0, -1.0), (14.0, -1.0), (14.0, HEIGHT), (y0, HEIGHT), (-14.0, HEIGHT - drop - slope)]
    mk.boolean(plate, mk.prism("chamfer", side, -20.0, 20.0, axis="x"))
    for s in (1, -1):
        outline = [(s * x, y) for x, y in PRONG]
        if s < 0:
            outline.reverse()
        top = mk.plane((s * 6.6, -1.0, HEIGHT), (s * 12.0, -1.0, HEIGHT + PRONG_OUTER),
                       (s * 11.75, 11.0, HEIGHT + PRONG_RISE))
        prong = mk.wedge(f"prong{s}", outline, 0.0, top, m["steel"][-1][1])
        mk.boolean(plate, prong, "UNION")
    # The vent's slot and the fins' slot.
    hw, ya, yb, depth = SLOT
    mk.boolean(plate, mk.box("vent", -hw, hw, ya, yb, HEIGHT - depth, HEIGHT + 2.0, m["dark"]), "DIFFERENCE")
    hw, ya, yb, depth = FIN_SLOT
    mk.boolean(plate, mk.box("finslot", -hw, hw, ya, yb, HEIGHT - depth, HEIGHT + 3.0, m["dark"]), "DIFFERENCE")
    mk.cleanup(plate)
    mk.bevel(plate, BEVEL, 2, 25)
    floor = HEIGHT - 0.3

    def pick(p, n):
        in_vent = abs(p.x) < SLOT[0] + 0.05 and SLOT[1] - 0.05 < p.y < SLOT[2] + 0.05
        in_slot = abs(p.x) < FIN_SLOT[0] + 0.05 and FIN_SLOT[1] - 0.05 < p.y < FIN_SLOT[2] + 0.05
        if p.z < floor and (in_vent or in_slot):
            return m["dark"]
        if p.y > -0.6 and abs(p.x) > 6.9 and n.z > 0.93:
            return m["prong"]
        return steel_band(m, n)
    mk.paint(plate, pick)
    mk.shade(plate, 35)
    # The block in the vent and the ledge under it.
    hw, ya, yb, below = BLOCK
    block = mk.box("block", -hw, hw, ya, yb, HEIGHT - SLOT[3] - 0.1, HEIGHT - below, m["steel"][-1][1])
    hw, ya, yb, up = LEDGE
    ledge = mk.box("ledge", -hw, hw, ya, yb, HEIGHT - 0.4, HEIGHT + up, m["steel"][-1][1])
    for part, width in ((block, 0.22), (ledge, 0.14)):
        mk.bevel(part, width, 2, 35)
        mk.paint(part, lambda p, n: steel_band(m, n))
        mk.shade(part, 35)


def paint_fields(obj, layers):
    """Gives the faces of obj materials by fields over its surface, each layer (field(point, normal),
    borders ascending, materials: one per band, None to keep the earlier layers') painting over the
    earlier ones; the faces are cut along every border first, so the colours meet along smooth
    contours, and each face takes the band of its corners' mean value (the cuts' own)."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    kept = []
    for field, borders, _ in layers:
        bm.normal_update()
        values = {v: field(v.co, v.normal) for v in bm.verts}
        for t in borders:
            mk.split_along(bm, values, t)
        kept.append(values)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    bm.normal_update()
    for (field, _, _), values in zip(layers, kept):   # corners made by the later layers' cuts
        for v in bm.verts:
            if v not in values:
                values[v] = field(v.co, v.normal)
    picks = []
    for f in bm.faces:
        mat = None
        for (_, borders, mats), values in zip(layers, kept):
            mean = sum(values[v] for v in f.verts) / len(f.verts)
            band = mats[sum(mean > t for t in borders)]
            if band is not None:
                mat = band
        picks.append(mat)
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.materials.clear()
    names = []
    for mat in picks:
        if mat.name not in names:
            names.append(mat.name)
            obj.data.materials.append(mat)
    for poly, mat in zip(obj.data.polygons, picks):
        poly.material_index = names.index(mat.name)
    return obj


def fin(m, side):
    """The left fin (side -1) or its mirror image (side 1): lofted through horizontal sections up the
    screen (the sprite's rows), rounded lenses on a rising axis, painted by where across it a face is."""
    ys = [y for y, _ in FIN_HALF]
    half = fire.monotone(ys, [w for _, w in FIN_HALF])
    y0, y1 = ys[0], ys[-1]

    def middle(y):
        return FIN_AXIS[0] + FIN_AXIS[1] * y

    def axis_z(y):
        return FIN_Z[0] + (FIN_Z[1] - FIN_Z[0]) * (y - y0) / (y1 - y0)
    rings = []
    steps = 32
    for i in range(1, steps):
        y = y0 + (y1 - y0) * (1 - math.cos(math.pi * i / steps)) / 2   # finer at the ends
        w = max(half(y), 0.05)
        rings.append(k.ring(y, w, 1.0, 22, z=axis_z(y), x=middle(y), top=w * FIN_UP, bottom=w * FIN_DOWN,
                            power=FIN_POWER))
    obj = k.loft("fin", rings, m["fin"], start_point=(middle(y0), y0, axis_z(y0)),
                 end_point=(middle(y1), y1, axis_z(y1)))

    def across(p):   # towards +x: the V's middle
        return (p.x - middle(p.y)) / max(half(min(max(p.y, y0), y1)), 0.4)

    def streak(p, n):
        along = mk.smoothstep(-4.3, -2.6, p.y) * mk.smoothstep(5.4, 3.6, p.y)
        strength = 0.55 + 0.45 * math.exp(-((p.y - STREAK_Y) / STREAK_SPREAD) ** 2)
        return math.exp(-((across(p) - STREAK_ACROSS) / STREAK_WIDTH) ** 2) * strength * along * \
            mk.smoothstep(0.05, 0.3, n.z)

    paint_fields(obj, [
        (lambda p, n: -across(p), (OUTER,), (m["fin"], m["fin_dark"])),
        (streak, STREAK_BANDS, (None, m["fin_warm"], m["fin_hot"])),
        (lambda p, n: n.z, (0.12,), (m["fin_dark"], None)),
    ])
    if side > 0:
        obj.data.transform(Matrix.Scale(-1, 4, (1, 0, 0)))
        obj.data.flip_normals()
    k.recalc_normals(obj)
    return k.smooth(obj, 60)


def build():
    options = k.args()
    k.reset()
    m = materials()
    body(m)
    fin(m, -1)
    fin(m, 1)
    parts = [join("fin_chevron", mk.meshes())]
    if "check" in options:
        k.check_silhouette(os.path.join(options["check"], "enemy_K.png"), 207)
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    mk.report("fin_chevron", parts, os.path.join(mk.outdir(options), "fin_chevron.glb"))
    if "preview" in options:
        mk.preview(options["preview"] + "fin_chevron", parts)


if __name__ == "__main__":
    build()
