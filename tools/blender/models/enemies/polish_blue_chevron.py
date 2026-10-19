"""GEM WAR's and MARKERS' blue chevron (sheet G sprite 163, 2x2: 24 x 23 pixels in the 24 x 28 cell; enemy 809, on
the ground, rising from the bottom of the screen; not animated), polished (2026-10-19; it replaces
wave3_r_beasts.py's blue_chevron(), a hull inflated from the sprite and painted by its shades). models.cfg: sprite
g 163 blue_chevron yaw=0 glow=10:0.2:118:0:1.4 (the eyes' glow added). No other enemy shows this sprite; it is no
other sprite's pixels mirrored or in other ramps.

As the sprite and its 4x upscale draw it, pointing up the screen: an arrowhead of blue armour (ramp 3) in three
tiers that overlap like scales. The nose (rows 4-7), a stepped point; under it two shoulder slabs (rows 8-13) meeting
at a crease down the middle, sloping down to the leading edges, pale cyan rims along their top edges (row 8, ramp
8); in the shadow under their inner corners two slanting red eyes (columns 8-9 and 14-15 of rows 14-16) either side
of a small block with slits (columns 10-13); then the two wing slabs (rows 14-26) sweeping out and down to the
wing tips at the bottom corners, the leading edges straight down from row 17, a lit ridge on each running from
the middle down and out (rows 18-23), the notch between them at the bottom (rows 23-26); red glowing tips at the
wings' corners (columns 0-2 and 21-23 of rows 25-26).

Built as layered armour: each slab a thick plate with rounded edges lying on a tilted plane (higher towards the
crease, polish_redjet.facet), on a low dark body; the rims and ridges rounded bars, the eyes and tips glowing lenses
(emission in their own reds). It stands on the ground (z = 0).

The sprite is symmetric about the line between its columns 11 and 12 (x 0 here). Origin at the sprite's centre
(pixel 12, 14); +Y up the sprite, +Z towards the camera.

Replaces wave3_r_beasts.py's blue_chevron() (its @r.model("blue_chevron", [(163, True)]) function and the
blue_chevron lines of the docstring) and wave3_r_art.py's CHEVRON (nothing else reads it): remove them so that they
don't overwrite this model.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouette against
enemy_G.png), --preview <prefix>.
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
from polish_jets import triangles  # noqa: E402
from polish_redjet import chaikin, facet, resample  # noqa: E402
from polish_squid_ship import catmull, ccw, tube  # noqa: E402

# The plan, 1/3 pixel inside the sprite's outline (left halves, x <= 0): the shoulder slab, the wing slab, the
# nose's two steps, the body under them all.
SHOULDER = [(-0.25, 6.05), (-4.45, 6.05), (-5.6, 4.75), (-8.75, 1.6), (-8.85, 0.75), (-7.9, 0.15), (-4.7, -0.2),
            (-2.3, 0.4), (-0.25, 1.35)]
# The wing slab in two parts either side of the lit ridge (rows 18-23): the main plate up and out of it, the lower
# strip along the notch inside it, a little lower, so that the ridge is the main plate's lit edge.
WING = [(-0.25, 0.4), (-0.25, -3.7), (-6.75, -9.95), (-7.55, -11.75), (-9.4, -12.65), (-11.67, -12.65),
        (-11.67, -3.55), (-8.7, -0.6), (-7.9, 0.5), (-4.0, 0.6)]
WING_STRIP = [(-0.25, -3.3), (-0.25, -8.45), (-2.2, -10.0), (-5.4, -10.55), (-7.7, -11.9), (-7.0, -9.6)]
NOSE = [(0.0, 9.67), (-1.2, 8.5), (-3.55, 6.25), (-3.4, 5.55), (0.0, 5.55)]
NOSE_TOP = [(0.0, 9.25), (-1.0, 8.3), (-2.15, 7.1), (-2.0, 6.65), (0.0, 6.65)]
BODY = [(0.0, 8.0), (-8.2, 0.0), (-11.2, -3.3), (-11.2, -12.2), (-9.0, -12.2), (-0.0, -8.0)]

# The slabs' bottoms: tilted planes z = z0 + gx * (x - x0) + gy * (y - y0) (higher towards the crease and the
# nose); their thickness.
SHOULDER_PLANE = (3.35, 0.2, 0.06, -8.8, 0.0)
SHOULDER_THICK = 1.45
WING_PLANE = (1.25, 0.15, 0.085, -11.67, -12.65)
WING_THICK = 1.35
NOSE_PLANE = (4.7, 0.18, 0.05, -3.5, 5.6)

# The ridge on each wing slab (from the middle down and out), the eyes (centre, radii, the long axis's angle),
# the slit block, the wing tips.
RIDGE = [(-0.7, -3.85), (-2.6, -5.75), (-4.6, -7.75), (-6.45, -9.6)]
EYE = ((-3.0, -1.35), (0.72, 1.45), -63.0)
BLOCK = (-1.85, 1.85, -3.75, 0.85)
TIP = (-10.65, -11.85)


def plane(spec):
    z0, gx, gy, x0, y0 = spec
    return lambda x, y: z0 + gx * (x - x0) + gy * (y - y0)


def mirror(points):
    return [(-x, y) for x, y in points]


def materials():
    pal = k.level_palette()
    return {
        "body": k.material("chevron_body", palette=0x33, metallic=0.3, roughness=0.45),
        "shoulder": k.material("chevron_shoulder", palette=0x38, metallic=0.35, roughness=0.3),
        "wing": k.material("chevron_wing", palette=0x37, metallic=0.35, roughness=0.32),
        "nose": k.material("chevron_nose", palette=0x37, metallic=0.35, roughness=0.3),
        "crest": k.material("chevron_crest", palette=0x3a, metallic=0.35, roughness=0.26),
        "ridge": k.material("chevron_ridge", palette=0x39, metallic=0.35, roughness=0.26),
        "rim": k.material("chevron_rim", palette=0x89, metallic=0.3, roughness=0.24),
        "block": k.material("chevron_block", palette=0x36, metallic=0.35, roughness=0.32),
        "slit": k.material("chevron_slit", palette=0x31, metallic=0.2, roughness=0.6),
        "eye": k.material("chevron_eye", palette=0x74, metallic=0.0, roughness=0.2, emission=pal[0x75],
                          emission_strength=1.4),
        "eye_hot": k.material("chevron_eye_hot", palette=0x77, metallic=0.0, roughness=0.2, emission=pal[0x77],
                              emission_strength=2.0),
        "tip": k.material("chevron_tip", palette=0x75, metallic=0.1, roughness=0.25, emission=pal[0x75],
                          emission_strength=1.2),
        "tip_dark": k.material("chevron_tip_dark", palette=0x62, metallic=0.4, roughness=0.35),
    }


def slab(name, outline, spec, thickness, mat, rim=0.55, dome=0.18, spacing=0.4, rounding=2):
    pts = resample(chaikin(ccw(outline), rounding), spacing)
    return facet(name, pts, plane(spec), thickness, mat, rim=rim, steps=3, dome=dome, dome_rings=2, sink=0.6)


def top_of(spec, thickness, dome=0.0):
    p = plane(spec)
    return lambda x, y: p(x, y) + thickness + dome


def build_left(m):
    """The left half's parts (mirrored afterwards)."""
    parts = []
    parts.append(slab("shoulder_l", SHOULDER, SHOULDER_PLANE, SHOULDER_THICK, m["shoulder"], rim=0.5, dome=0.22,
                      spacing=0.5))
    parts.append(slab("wing_l", WING, WING_PLANE, WING_THICK, m["wing"], rim=0.5, dome=0.2, spacing=0.6, rounding=1))
    parts.append(slab("wing_strip_l", WING_STRIP, WING_PLANE, WING_THICK - 0.45, m["wing"], rim=0.4, dome=0.08,
                      spacing=0.55, rounding=1))
    # The pale rim along the shoulder's top edge, curling a little down the leading edge.
    top = top_of(SHOULDER_PLANE, SHOULDER_THICK)
    rim_line = [(-0.45, 5.72), (-2.4, 5.74), (-4.15, 5.7), (-5.0, 5.05), (-5.6, 4.35)]
    pts = catmull([Vector((x, y, top(x, y) - 0.25)) for x, y in rim_line], 0.3)
    parts.append(tube("rim_l", pts, [0.42] * len(pts), m["rim"], segments=8, squash=0.8))
    # The lit ridge on the wing.
    top = top_of(WING_PLANE, WING_THICK)
    pts = catmull([Vector((x, y, top(x, y) + 0.02)) for x, y in RIDGE], 0.35)
    radii = [0.5 * min(1.0, 0.45 + i / 3, 0.45 + (len(pts) - 1 - i) / 3) for i in range(len(pts))]
    parts.append(tube("ridge_l", pts, [0.72 * r for r in radii], m["ridge"], segments=8, squash=0.7))
    # The eye: a slanting glowing lens in the shadow under the shoulder's inner corner, a hot streak in it.
    (ex, ey), (ra, rb), ang = EYE
    z = top_of(WING_PLANE, WING_THICK)(ex, ey) + 0.15
    turn = Matrix.Translation((ex, ey, z)) @ Matrix.Rotation(math.radians(ang + 90.0), 4, "Z")
    eye = k.ellipsoid("eye_l", (0, 0, 0), (ra, rb, 0.55), m["eye"], 16, 8)
    eye.data.transform(turn)
    parts.append(k.smooth(eye, 60))
    hot = k.ellipsoid("eye_hot_l", (0, 0, 0.32), (ra * 0.45, rb * 0.62, 0.3), m["eye_hot"], 12, 6)
    hot.data.transform(turn)
    parts.append(k.smooth(hot, 60))
    # The wing tip: a red glowing pad at the corner, on a dark claw.
    tx, ty = TIP
    z = top_of(WING_PLANE, WING_THICK)(tx, ty)
    claw = k.ellipsoid("tip_claw_l", (tx - 0.1, ty - 0.1, z - 0.55), (1.35, 1.1, 0.75), m["tip_dark"], 14, 7)
    parts.append(k.smooth(claw, 60))
    pad = k.ellipsoid("tip_l", (tx - 0.2, ty - 0.25, z - 0.15), (1.05, 0.85, 0.55), m["tip"], 14, 7)
    parts.append(k.smooth(pad, 60))
    return parts


def build_middle(m):
    # The low dark body under the slabs.
    outline = BODY + mirror(BODY[1:-1])[::-1]
    pts = resample(chaikin(ccw(outline), 1), 1.0)
    facet("body", pts, lambda x, y: 0.0, 2.2, m["body"], rim=0.6, steps=1, dome=0.1, dome_rings=1, sink=0.0)
    # The nose: two steps, a crest along its middle.
    for name, outline, lift, thick in (("nose", NOSE, 0.0, 1.0), ("nose_top", NOSE_TOP, 0.95, 0.8)):
        whole = outline + mirror(outline[1:-1])[::-1]
        spec = (NOSE_PLANE[0] + lift,) + NOSE_PLANE[1:]
        # The nose's plane rises towards the middle from both sides.
        p = plane(spec)
        base = lambda x, y, p=p: p(-abs(x), y)  # noqa: E731
        facet(name, resample(chaikin(ccw(whole), 2), 0.4), base, thick, m["nose"], rim=0.35, steps=2, dome=0.12,
              dome_rings=1, sink=0.6)
    top = lambda y: NOSE_PLANE[0] + 0.95 + 0.8 + NOSE_PLANE[1] * 3.5 + NOSE_PLANE[2] * (y - NOSE_PLANE[4])  # noqa: E731
    crest = [Vector((0.0, y, top(y) - 0.12)) for y in [6.9 + 2.1 * i / 8 for i in range(9)]]
    tube("crest", crest, [0.32] * 8 + [0.2], m["crest"], segments=8, squash=0.8)
    # The block with slits between the eyes.
    x0, x1, y0, y1 = BLOCK
    wing_top = top_of(WING_PLANE, WING_THICK)
    outline = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    facet("block", resample(chaikin(ccw(outline), 2), 0.35), lambda x, y: wing_top(-abs(x), y) - 0.3, 0.75,
          m["block"], rim=0.35, steps=2, dome=0.08, dome_rings=1, sink=0.5)
    for i, y in enumerate((-0.4, -1.45, -2.5)):
        z = wing_top(-1.0, y) + 0.48
        line = [Vector((x, y, z)) for x in (-1.2, 0.0, 1.2)]
        tube(f"slit{i}", line, [0.24] * 3, m["slit"], segments=6, squash=0.6)


def build():
    options = k.args()
    outdir = options.get("outdir", os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "enemies"))
    k.reset()
    m = materials()
    for part in build_left(m):
        copy = k.mirror_x(part, part.name[:-2] + "_r")
        copy.data.name = copy.name
        k.smooth(copy, 50)
    build_middle(m)
    used = {mat.name for o in bpy.context.scene.objects if o.type == "MESH" for mat in o.data.materials}
    print("== blue_chevron (G 163): %d triangles, %d materials: %s" % (triangles(), len(used), ", ".join(sorted(used))))
    if "check" in options:
        k.check_silhouette(os.path.join(options["check"], "enemy_G.png"), 163)
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    path = os.path.join(outdir, "blue_chevron.glb")
    k.export(path)
    print("%s: %d bytes" % (path, os.path.getsize(path)))
    if "preview" in options:
        k.preview(options["preview"] + "blue_chevron")


if __name__ == "__main__":
    build()
