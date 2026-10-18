"""EYESPY's eyeball (sheet 5 sprite 202, 1x1: an 11 x 11 eye in the 12 x 14 cell; in the sky of
EYESPY, DELI RUIN and GLACIER, and dropped in EYESPY and INVADERS, about 100 of them; its animation
202 202 221 221 221 202), polished (2026-10-18; it replaces wave2_h.py's eyespy_eye()). models.cfg:
sprite 5 202 eyespy_eye yaw=aim, frame 5 221 eyespy_eye_221.

As the 4x upscale draws it: a grey-white eyeball (columns 1-11, rows 1-11) in a black outline, its
white lightest at the upper left, a dark iris ring with a black pupil a little below its middle (columns
4-8, rows 6-9: the eye looks down the screen, at the player, and up at the camera), a catchlight on
the iris. In 221 the eye narrows into a lemon (columns 2-10, rows 0-12) whose iris is a tall slit
(columns 5-7, rows 5-10), as a cat's: eyespy_eye_221, the same eye squeezed to that shape.

The models look up the screen (+Y), tilted LOOK_TILT up at the camera: with yaw=aim the game turns
them to look at the player, as the sprite's eye looks down at him. The sclera is a shade lighter
than the sprite's (the game's camera sees much of the eye's side away from its sun), shading darker
towards the rim and the black outline the sprite draws round it; the cornea bulges a little over the
iris, which is glossy so the game's sun puts its catchlight on it. Both frames span the same height (z)
so the game, which centres sky models in height, keeps them in place.

Origin at the sprite's centre (pixel 6, 7); +Y up the screen, +Z towards the camera; the eye's middle
at (0.5, 0.5, 5.5) (columns 1-11, rows 1-11 round pixel 6, 7), its bottom on z = 0.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the
silhouette against enemy_5.png, the eye turned to look down the screen as the sprite does), --preview
<prefix> (the eye turned the same way), --only <name,...>.
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
from polish_balls import Ellipsoid, painted_ball, preview, triangles  # noqa: E402
from polish_sphere_nozzle import smoothstep  # noqa: E402

CENTRE = Vector((0.5, 0.5, 5.5))
LOOK_TILT = 30.0        # degrees from straight up at the camera towards +Y
# The outline: where the normal's z is below OUTLINE_Z; the sclera shades darker below SHADE_Z.
OUTLINE_Z, SHADE_Z = 0.18, 0.45
CORNEA_BULGE = 0.045    # over the iris, in units of the radius
PUPIL_SINK = 0.02

# The frames: (model, sprite, radii (x, y, z), the iris's and the pupil's angular half-sizes across and
# along the look's tilt (degrees), the iris ring's width).
FRAMES = [
    ("eyespy_eye", 202, (5.5, 5.5, 5.5), (28.0, 28.0), (11.0, 11.0), 3.0),
    ("eyespy_eye_221", 221, (4.5, 6.5, 5.5), (14.0, 31.0), (4.5, 17.0), 2.5),
]
RAMP = 0


def look_frame():
    t = math.radians(LOOK_TILT)
    look = Vector((0.0, math.sin(t), math.cos(t)))
    across = Vector((1.0, 0.0, 0.0))
    along = Vector((0.0, math.cos(t), -math.sin(t)))  # towards the top of the iris, seen from the look
    return look, across, along


def iris_distance(d, half):
    """How far d (a unit vector from the eye's middle; the round sphere's direction) is from the look,
    in units of the half-sizes (degrees across and along)."""
    look, across, along = look_frame()
    c = d.dot(look)
    a = math.degrees(math.atan2(d.dot(across), c))
    b = math.degrees(math.atan2(d.dot(along), c))
    if c <= 0:
        return 99.0
    return math.hypot(a / half[0], b / half[1])


class Eye(Ellipsoid):
    """The eyeball: the shape is the ellipsoid; the painted fields read the round sphere's direction
    (kept in self.last) so the iris stays round on the round eye and narrows with the squeezed one."""

    def point(self, d):
        p, n = super().point(d)
        self.last = d
        return p, n


def materials(name):
    def m(key, index, **kw):
        return k.material(f"{name}_{key}", palette=16 * RAMP + index, **kw)
    return {
        "sclera": m("sclera", 0x0c, metallic=0.0, roughness=0.18),
        "sclera_shade": m("sclera_shade", 0x0a, metallic=0.0, roughness=0.22),
        "outline": m("outline", 0x02, metallic=0.0, roughness=0.5),
        "limbus": m("limbus", 0x01, metallic=0.0, roughness=0.12),
        "iris": m("iris", 0x04, metallic=0.0, roughness=0.1),
        "pupil": m("pupil", 0x01, metallic=0.0, roughness=0.06),
    }


def eye(name, radii, iris_half, pupil_half, ring):
    shape = Eye(CENTRE, radii)
    ring_t = 1 - ring / iris_half[1]          # the iris ring's inner edge, in units of the iris

    def iris(p, n):
        return iris_distance(shape.last, iris_half)

    def pupil(p, n):
        return iris_distance(shape.last, pupil_half)

    def rim(p, n):
        return n.z

    def displace(d, p, n):
        r = iris_distance(d, iris_half)
        bulge = CORNEA_BULGE * (1 - smoothstep(0.6, 1.25, r))
        sink = PUPIL_SINK * (1 - smoothstep(0.7, 1.0, iris_distance(d, pupil_half)))
        return min(radii) * (bulge - sink)

    paint = [
        (rim, (OUTLINE_Z, SHADE_Z), ("outline", "sclera_shade", "sclera")),
        (iris, (ring_t, 1.0), ("iris", "limbus", None)),
        (pupil, (1.0,), ("pupil", None)),
    ]
    painted_ball(name, shape, paint, materials(name), displace=displace, smooth_angle=60)


def turned(angle):
    """Turns every mesh about the eye's middle (as yaw turns it in the game: degrees, clockwise seen
    from above)."""
    m = Matrix.Translation(CENTRE) @ Matrix.Rotation(math.radians(-angle), 4, "Z") @ Matrix.Translation(-CENTRE)
    for obj in bpy.context.scene.objects:
        if obj.type == "MESH":
            obj.data.transform(m)


def build():
    options = k.args()
    outdir = options.get("outdir", os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "enemies"))
    only = set(options["only"].split(",")) if "only" in options else None
    for name, sprite, radii, iris_half, pupil_half, ring in FRAMES:
        if only is not None and name not in only:
            continue
        k.reset()
        eye(name, radii, iris_half, pupil_half, ring)
        used = {m.name for obj in bpy.context.scene.objects if obj.type == "MESH" for m in obj.data.materials}
        print("== %s (5 %d): %d triangles, %d materials: %s" % (name, sprite, triangles(), len(used),
                                                             ", ".join(sorted(used))))
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        path = os.path.join(outdir, name + ".glb")
        k.export(path)
        print("%s: %d bytes" % (path, os.path.getsize(path)))
        # The checks and previews show the eye as the game does with the player below it.
        turned(180)
        if "check" in options:
            k.check_silhouette(os.path.join(options["check"], "enemy_5.png"), sprite, large=False)
        if "preview" in options:
            preview(options["preview"] + name, size=(12, 14), distance=0.5)


if __name__ == "__main__":
    build()
