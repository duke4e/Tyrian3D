"""Data cube (the coins sheet's sprites 159 and 191, value 1: the cubes that carry the game's messages; 2x2, 24 x 28
pixels; about 80 of them in the levels), polished (2026-10-20; it replaces datacube.py's frame of square bars round a
grey box and ball). models.cfg: sprite coins 159/191 datacube spin=3 color=sprite glow.

The cubes' animations cycle colours: 159 161 163 161 159 in ramp 10 (tan), then 197 199 (ramp 10 darker) and 201
(ramp 1), 235 (ramp 4), 237 239 (ramp 7), 273 275 277 (ramp 12, green); 191 193 195 in ramp 9 (blue), then 229
(ramp 3), 231 233 (ramp 8), 269 271 (ramp 0, grey) and 273. They are one cube drawn in several ramps, its shades
moved (191 is 159 two to four shades lighter): one grey model, which color=sprite gives each frame's ramp (the
game takes the ramp most of the frame's pixels are in). No frame models.

As the sprite and its 4x upscales draw it: a glass cube seen from above and to one side, 20 x 22 pixels (columns
2-21, rows 3-24): its edges bright (the lightest shades), its glass a lighter tint of the colour, the edges behind
the glass darker, seen through it.

Built as a glass cube in a metal frame standing on a corner (so that from above it shows three faces round a
middle corner, a hexagon, whichever way it turns; 13.4 pixels along an edge, about as wide as the sprite's cube
and a little shorter): the frame is a cube with its faces cut out (booleans), its edges rounded (bevel); the glass
is a see-through cube inside it (GLASS_ALPHA; the game draws see-through materials without shadows and from both
sides, so the light reaches the core and the far panes tint it too); in the middle a core, a smaller cube with a
raised chip on each face, the data, held by thin struts from its corners to the frame's (a cube in a cube).
Palette shades of ramp 0 without emission (polish_item_kit), a middle set for the cycle's ramps (lighter ones
wash ramps 4 and 7 out, darker ones lose ramp 9's blue): color=sprite gives them the frame's ramp; the
models.cfg glow lights the cube in that ramp.

The cube's middle is the origin (the sprite's centre, where the sprite draws its cube too), so that it turns in
place.

Options after "--": --outdir <dir> (default assets/models/items), --check <sheets dir> (the silhouette against
coins.png), --preview <prefix>, --only <name,...>, --ramp <0-15> (built in that ramp, written as _r<ramp>).
"""
import os
import sys

import bmesh
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_item_kit as kit  # noqa: E402
from polish_item_kit import k  # noqa: E402

# The cube's edge and its frame's bars' width; the bars' rounding (bevel width).
EDGE, BAR, ROUND = 13.4, 1.25, 0.3
# The glass: inside the frame, its faces GLASS_IN under the frame's faces; see-through.
GLASS_IN, GLASS_ALPHA = 0.35, 0.55
# The core: a cube CORE across, its edges rounded; a chip CHIP across and CHIP_H high on each of its faces; struts
# STRUT thick from its corners to the frame's (a cube in a cube: the data's lattice).
CORE, CORE_ROUND, CHIP, CHIP_H, STRUT = 4.6, 0.45, 2.8, 0.16, 0.42
SHADES = {"frame": 13, "glass": 10, "core": 11, "chip": 13}
FINISH = {"frame": dict(metallic=0.3, roughness=0.25), "glass": dict(metallic=0.0, roughness=0.08, alpha=GLASS_ALPHA),
          "core": dict(metallic=0.3, roughness=0.3), "chip": dict(metallic=0.3, roughness=0.2)}


def frame(mat):
    """The frame: a cube with a hole through each pair of faces, its edges rounded."""
    h = EDGE / 2
    obj = kit.prism_box("frame", -h, h, -h, h, -h, h, mat)
    inner = h - BAR
    cuts = [kit.prism_box("cut_z", -inner, inner, -inner, inner, -h - 1, h + 1, mat),
            kit.prism_box("cut_x", -h - 1, h + 1, -inner, inner, -inner, inner, mat),
            kit.prism_box("cut_y", -inner, inner, -h - 1, h + 1, -inner, inner, mat)]
    kit.boolean(obj, cuts, "DIFFERENCE")
    kit.bevel(obj, ROUND, segments=2, angle=30.0)
    return kit.weighted(obj, 35.0)


def strut(a, b, mat):
    """A thin square bar from a to b, its edges turned along the cube's diagonal."""
    d = (b - a).normalized()
    side = d.cross(Vector((0.0, 0.0, 1.0)) if abs(d.z) < 0.9 else Vector((1.0, 0.0, 0.0))).normalized()
    up = d.cross(side).normalized()
    w = STRUT / 2
    corners = [side * w + up * w, -side * w + up * w, -side * w - up * w, side * w - up * w]
    bm = bmesh.new()
    lo = [bm.verts.new(a + q) for q in corners]
    hi = [bm.verts.new(b + q) for q in corners]
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
    bm.faces.new(lo)
    bm.faces.new(hi)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return kit.flat_shade(kit.from_bmesh("strut", bm, mat))


def build():
    opts = kit.options()
    ramp, _ = kit.ramp_of(opts)
    if not kit.wanted(opts, "datacube"):
        return
    k.reset()
    mats = {key: kit.shade(f"datacube_{key}", v, ramp, **FINISH[key]) for key, v in SHADES.items()}
    parts = [frame(mats["frame"])]
    g = EDGE / 2 - GLASS_IN
    parts.append(kit.flat_shade(kit.prism_box("glass", -g, g, -g, g, -g, g, mats["glass"])))
    c = CORE / 2
    core = kit.prism_box("core", -c, c, -c, c, -c, c, mats["core"])
    kit.bevel(core, CORE_ROUND, segments=2, angle=30.0)
    parts.append(kit.weighted(core, 35.0))
    chip = CHIP / 2
    for axis in range(3):
        for sign in (-1, 1):
            lo = [-chip, -chip, -chip]
            hi = [chip, chip, chip]
            lo[axis], hi[axis] = (c - 0.1, c + CHIP_H) if sign > 0 else (-c - CHIP_H, -c + 0.1)
            plate = kit.prism_box("chip", lo[0], hi[0], lo[1], hi[1], lo[2], hi[2], mats["chip"])
            kit.bevel(plate, 0.08, segments=1, angle=30.0)
            parts.append(kit.flat_shade(plate))
    corner_in, corner_out = c - CORE_ROUND * 0.6, EDGE / 2 - BAR * 0.6
    for sx in (-1, 1):
        for sy in (-1, 1):
            for sz in (-1, 1):
                a = Vector((sx, sy, sz)) * corner_in
                b = Vector((sx, sy, sz)) * corner_out
                parts.append(strut(a, b, mats["core"]))
    # On a corner: the diagonal (1, 1, 1) turned up towards the camera.
    turn = Vector((1, 1, 1)).rotation_difference(Vector((0, 0, 1))).to_matrix().to_4x4()
    kit.transform(parts, turn)
    kit.finish(opts, "datacube", parts, 191, large=True, distance=0.8)


if __name__ == "__main__":
    build()
