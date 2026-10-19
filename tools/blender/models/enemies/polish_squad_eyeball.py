"""The white eyeball of SQUADRON's marching rows and TIME WAR (sheet L sprite 117, 1x1: an 11 x 11 eye in the 12 x 14
cell; enemies 671 on top and 723 on the ground; not animated), polished (2026-10-19; it replaces wave3_z_small.py's
squad_eyeball()). models.cfg: sprite l 117 squad_eyeball yaw=aim (it was yaw=0). No other enemy shows this sprite.

L 117 is EYESPY's eyeball (sheet 5 sprite 202, polish_eyespy_eye.py) one row lower, its white the same shade for shade
(92 of its 97 pixels), its iris a different one: not 202's grey ring round a black pupil but a blue iris (ramp 3,
columns 4-8 of rows 7-10), dark at its rim (0x31-0x36), lighter inside (0x38-0x3b) and lightest at its middle (0x3d),
with no black pupil: a glassy blue eye. So this is polish_eyespy_eye's eye (its shape, its sclera shading darker
towards the rim and the black outline the sprite draws round it, its cornea bulging over the iris), not modelled
again: built with that script's Eye and iris_distance, its iris painted blue as L 117 draws it.

As polish_eyespy_eye's models, the eye looks up the screen (+Y), tilted LOOK_TILT up at the camera: with yaw=aim the
game turns it to look at the player, as EYESPY's eyeballs do; the sprite's eye looks down the screen, where the
player usually is. (With yaw=0 it would look up the screen, away from the player: keep yaw=aim with this model.)

Origin at the sprite's centre (pixel 6, 7); +Y up the screen, +Z towards the camera; the eye's middle at
(0.5, -0.5, 5.5) (columns 1-11, rows 2-12 round pixel 6, 7), its bottom on z = 0.

Replaces wave3_z_small.py's squad_eyeball() (its @kit.model("squad_eyeball", ...) function, the EYE = kit.frame("EYE",
...) line and the squad_eyeball line of its docstring; wave3_z_art.py's EYE, which only it reads): remove them so that
they don't overwrite this model.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouette against
enemy_L.png, the eye turned to look down the screen as the sprite does), --preview <prefix> (turned the same way).
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
import polish_eyespy_eye as ee  # noqa: E402
from polish_balls import painted_ball, preview, triangles  # noqa: E402
from polish_sphere_nozzle import smoothstep  # noqa: E402

CENTRE = Vector((0.5, -0.5, 5.5))
RADII = (5.5, 5.5, 5.5)
# The iris: its angular half-sizes (degrees, as 202's); within it the bands from its rim in: the dark rim, the
# blue, the lighter blue, the light middle (fractions of the iris's radius).
IRIS_HALF = (28.0, 28.0)
RING, INNER, MIDDLE = 0.8, 0.55, 0.26


def materials():
    pal = k.level_palette()

    def m(key, index, **kw):
        return k.material(f"squad_eye_{key}", palette=index, **kw)
    return {
        "sclera": m("sclera", 0x0c, metallic=0.0, roughness=0.18),
        "sclera_shade": m("sclera_shade", 0x0a, metallic=0.0, roughness=0.22),
        "outline": m("outline", 0x02, metallic=0.0, roughness=0.5),
        "limbus": m("limbus", 0x33, metallic=0.0, roughness=0.12),
        "iris": m("iris", 0x37, metallic=0.0, roughness=0.1, emission=pal[0x37], emission_strength=0.25),
        "iris_light": m("iris_light", 0x3a, metallic=0.0, roughness=0.08, emission=pal[0x3a], emission_strength=0.35),
        "iris_middle": m("iris_middle", 0x3d, metallic=0.0, roughness=0.06, emission=pal[0x3d], emission_strength=0.45),
    }


def eye():
    shape = ee.Eye(CENTRE, RADII)

    def iris(p, n):
        return ee.iris_distance(shape.last, IRIS_HALF)

    def rim(p, n):
        return n.z

    def displace(d, p, n):
        r = ee.iris_distance(d, IRIS_HALF)
        return min(RADII) * ee.CORNEA_BULGE * (1 - smoothstep(0.6, 1.25, r))

    paint = [
        (rim, (ee.OUTLINE_Z, ee.SHADE_Z), ("outline", "sclera_shade", "sclera")),
        (iris, (MIDDLE, INNER, RING, 1.0), ("iris_middle", "iris_light", "iris", "limbus", None)),
    ]
    painted_ball("squad_eyeball", shape, paint, materials(), displace=displace, smooth_angle=60)


def turned(angle):
    """Turns every mesh about the eye's middle (degrees, clockwise seen from above), as yaw does in the game."""
    m = Matrix.Translation(CENTRE) @ Matrix.Rotation(math.radians(-angle), 4, "Z") @ Matrix.Translation(-CENTRE)
    for obj in bpy.context.scene.objects:
        if obj.type == "MESH":
            obj.data.transform(m)


def build():
    options = k.args()
    outdir = options.get("outdir", os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "enemies"))
    k.reset()
    eye()
    used = {mat.name for obj in bpy.context.scene.objects if obj.type == "MESH" for mat in obj.data.materials}
    print("== squad_eyeball (L 117): %d triangles, %d materials: %s" % (triangles(), len(used),
                                                                       ", ".join(sorted(used))))
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    path = os.path.join(outdir, "squad_eyeball.glb")
    k.export(path)
    print("%s: %d bytes" % (path, os.path.getsize(path)))
    # The checks and previews show the eye as the game does with the player below it.
    turned(180)
    if "check" in options:
        k.check_silhouette(os.path.join(options["check"], "enemy_L.png"), 117, large=False)
    if "preview" in options:
        preview(options["preview"] + "squad_eyeball", size=(12, 14), distance=0.5)


if __name__ == "__main__":
    build()
