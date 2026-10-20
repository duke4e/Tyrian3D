"""EYESPY's green eyeball (sheet 5 sprite 79, 2x2: a 21-pixel ball in the 24 x 28 cell; sky and top layers of
EYESPY, DELI RUIN, GLACIER and INVADERS, enemy 340, about 40 of them; its animation shows 79 throughout),
polished (2026-10-20; it replaces wave3_l.py's green_eye(), a plain dark green ball). models.cfg: sprite 5 79
green_eye yaw=aim (unchanged).

As the sprite and its 4x upscale draw it: a glossy green eyeball (ramp 2; columns 2-22, rows 2-22: its middle
at pixel 12.5, 12.5) in a near-black outline, lightest at its upper left (a white glare, rows 6-9), with a big
iris below its middle, looking down the screen at the player and up at the camera: the iris (columns 6-19,
rows 10-21) sits in a groove, dark along its upper rim (row 10: the groove's wall in shadow) and lit along its
lower right (rows 16-20: the wall facing the light); inside it a mid-green iris, lighter flecks round a black
pupil (rows 14-17, columns 11-15) and a glint on the iris at the pupil's upper left.

The model: an eyeball (a ball painted as polish_balls.painted_ball paints them, its faces split finer round
the iris: painted_eye) whose sclera is a shade lighter than the sprite's and glows a little in its own green
(the game's slanted camera sees much of the ball's side away from its sun, which reads near black otherwise),
shading darker to a dark rim where it turns away from the camera (the sprite's outline). The iris is a disc
LOOK_TILT from straight up at the camera, sunk in a groove (the limbus: its walls modelled, so the game's sun
lights its lower side and shades its upper one, as the sprite draws them, whichever way the eye turns), the
cornea bulging over it, glossy so the sun puts its glint on it; the iris painted with fibres of a lighter green
and, round the pupil, a ring of lighter flecks with a wavy edge; the pupil sunk a little and glossy black. No
glare is painted: the eye turns (yaw=aim), a painted light would turn with it; the sun's highlight on the wet
sclera stands for the sprite's glare.

The model looks up the screen (+Y), tilted LOOK_TILT up at the camera: with yaw=aim the game turns it to look
at the player, as the sprite's eye looks down at him. The game turns a model about the sprite's centre (the
origin): the eyeball's middle is at (-0.5, -1.5), so that turned to look straight down the screen (yaw 180, the
player below it) it is where the sprite draws it (0.5, 1.5), and off by at most 1.2 pixels while the player
is within 45 degrees of straight below (the previous model, centred where the sprite is, was 3.2 pixels off).

Origin at the sprite's centre (pixel 12, 14); +Y up the screen, +Z towards the camera (the game centres sky
models in height: the eye's middle is at z = 0).

Replaces wave3_l.py's green_eye() (its @model("green_eye", 79) function and the green_eye line of its
docstring) and the unused GREEN_EYE art in wave3_l_art.py: remove them so that they don't overwrite this model.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouette
against enemy_5.png, the eye turned to look down the screen as the sprite does), --preview <prefix> (the eye
turned the same way), --only green_eye.
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
from polish_balls import Ellipsoid, preview, triangles  # noqa: E402
from polish_sphere_nozzle import smoothstep, split_along  # noqa: E402

CENTRE = Vector((-0.5, -1.5, 0.0))
RADIUS = 10.45
LOOK_TILT = 32.0        # degrees from straight up at the camera towards +Y
# The rim: the dark outline where the normal's z is below OUTLINE_Z, the sclera shading darker below SHADE_Z.
OUTLINE_Z, SHADE_Z = 0.16, 0.42
# Round the look (degrees from it): the pupil, the lighter ring of flecks round it (its edge wavy: FLECK_WAVE
# degrees either way, FLECK_LOBES waves round it), the iris, the groove (the limbus, between its inner and outer
# edge, its floor GROOVE_DEPTH below the ball, a dark line along its floor between FLOOR) and the sclera beyond.
PUPIL, FLECKS, IRIS = 12.5, 16.5, 33.5
FLECK_WAVE, FLECK_LOBES = 1.6, 9
GROOVE = (33.5, 41.5)
FLOOR = (36.3, 38.7)
GROOVE_DEPTH = 0.075    # in units of the radius
CORNEA_BULGE = 0.03     # over the iris, in units of the radius
PUPIL_SINK = 0.012
# The iris's fibres (a shade lighter): how many round it, how much of each turn they fill, and how unevenly
# they are spaced (a phase wobble, FIBRE_WOBBLE radians at FIBRE_LOBES lobes round the iris).
FIBRES, FIBRE_WIDTH = 21, 0.36
FIBRE_WOBBLE, FIBRE_LOBES = 0.9, 3
REFINE = (PUPIL - 1.0, IRIS + 0.5)   # the faces of the ball between these (degrees from the look) split once more
RAMP = 2


def materials():
    pal = k.level_palette()

    def m(key, shade, glow=0.0, **kw):
        index = 16 * RAMP + shade
        if glow:
            kw.update(emission=pal[index], emission_strength=glow)
        return k.material(f"geye_{key}", palette=index, **kw)
    return {
        "sclera": m("sclera", 0x0a, 0.3, metallic=0.0, roughness=0.22),
        "sclera_shade": m("sclera_shade", 0x08, 0.22, metallic=0.0, roughness=0.25),
        "outline": m("outline", 0x04, 0.0, metallic=0.0, roughness=0.45),
        "groove": m("groove", 0x08, 0.0, metallic=0.0, roughness=0.25),
        "limbus": m("limbus", 0x03, 0.0, metallic=0.0, roughness=0.3),
        "iris": m("iris", 0x07, 0.25, metallic=0.0, roughness=0.1),
        "fibre": m("fibre", 0x08, 0.28, metallic=0.0, roughness=0.1),
        "flecks": m("flecks", 0x09, 0.32, metallic=0.0, roughness=0.1),
        "pupil": m("pupil", 0x01, 0.0, metallic=0.0, roughness=0.05),
    }


def look_frame():
    t = math.radians(LOOK_TILT)
    look = Vector((0.0, math.sin(t), math.cos(t)))
    across = Vector((1.0, 0.0, 0.0))
    along = look.cross(across).normalized()
    return look, across, along


def from_look(d):
    """The angle of the direction d (a unit vector from the eye's middle) from the look (degrees), and its angle
    round the look (radians)."""
    look, across, along = look_frame()
    c = max(-1.0, min(1.0, d.dot(look)))
    return math.degrees(math.acos(c)), math.atan2(d.dot(along), d.dot(across))


def painted_eye(name, shape, paint, mats, displace, refine, subdivisions=5, smooth_angle=60):
    """polish_balls.painted_ball, its icosphere's faces split once more where refine(direction) holds at their
    corners (round the iris: its fibres' edges finer)."""
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subdivisions, radius=1.0)
    edges = [e for e in bm.edges if all(refine(v.co.normalized()) for v in e.verts)]
    bmesh.ops.subdivide_edges(bm, edges=edges, cuts=1, use_grid_fill=True)
    for v in bm.verts:
        v.co = v.co.normalized()
    for field, borders, _ in paint:
        for t in borders:
            split_along(bm, {v: field(*shape.point(v.co.normalized())) for v in bm.verts}, t)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    kinds = []
    for f in bm.faces:
        p, n = shape.point(f.calc_center_median().normalized())
        kind = None
        for field, borders, keys in paint:
            band = sum(field(p, n) > t for t in borders)
            if keys[band] is not None:
                kind = keys[band]
        kinds.append(kind)
    names = []
    for kind in kinds:
        if mats[kind].name not in names:
            names.append(mats[kind].name)
    for f, kind in zip(bm.faces, kinds):
        f.material_index = names.index(mats[kind].name)
    for v in bm.verts:
        d = v.co.normalized()
        p, n = shape.point(d)
        v.co = p + n * displace(d, p, n)
    # The slivers where a painted border passes through a corner: welded away.
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=2e-3)
    bmesh.ops.dissolve_degenerate(bm, dist=2e-3, edges=bm.edges[:])
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    for key in names:
        mesh.materials.append(next(m for m in mats.values() if m.name == key))
    k.recalc_normals(obj)
    return k.smooth(obj, smooth_angle)


class Eye(Ellipsoid):
    """The eyeball; it keeps the direction of the last point asked for (self.last) for the painted fields."""

    def point(self, d):
        p, n = super().point(d)
        self.last = d
        return p, n


def eye():
    shape = Eye(CENTRE, (RADIUS, RADIUS, RADIUS))

    def rim(p, n):
        return n.z

    def round_look(p, n):
        return from_look(shape.last)[0]

    def fibres(p, n):
        """Above 0 on a fibre (between the pupil and the iris's edge)."""
        a, phi = from_look(shape.last)
        if not PUPIL < a < IRIS:
            return -1.0
        # The fibres curl a little as they run out, as an iris's do.
        wave = math.cos(FIBRES * phi + FIBRE_WOBBLE * math.sin(FIBRE_LOBES * phi) + 0.06 * (a - FLECKS))
        return wave - math.cos(math.pi * FIBRE_WIDTH)

    def flecks(p, n):
        """Below FLECKS on the ring of flecks round the pupil (the pupil is painted over it)."""
        a, phi = from_look(shape.last)
        return a - FLECK_WAVE * math.cos(FLECK_LOBES * phi + 1.1 * math.sin(2 * phi + 0.5))

    def displace(d, p, n):
        a, _ = from_look(d)
        bulge = CORNEA_BULGE * (1 - smoothstep(IRIS - 9.0, IRIS, a))
        sink = PUPIL_SINK * (1 - smoothstep(PUPIL - 2.0, PUPIL + 1.0, a))
        g0, g1 = GROOVE
        mid, half = (g0 + g1) / 2, (g1 - g0) / 2
        groove = GROOVE_DEPTH * max(0.0, 1 - ((a - mid) / half) ** 2)
        return RADIUS * (bulge - sink - groove)

    def iris_area(d):
        return REFINE[0] < from_look(d)[0] < REFINE[1]

    paint = [
        (rim, (OUTLINE_Z, SHADE_Z), ("outline", "sclera_shade", "sclera")),
        (round_look, (IRIS, FLOOR[0], FLOOR[1], GROOVE[1]), ("iris", "groove", "limbus", "groove", None)),
        (fibres, (0.0,), (None, "fibre")),
        (flecks, (FLECKS,), ("flecks", None)),
        (round_look, (PUPIL,), ("pupil", None)),
    ]
    painted_eye("green_eye", shape, paint, materials(), displace, iris_area)


def turned(angle):
    """Turns every mesh about the origin as yaw turns it in the game (degrees, clockwise seen from above)."""
    m = Matrix.Rotation(math.radians(-angle), 4, "Z")
    for obj in bpy.context.scene.objects:
        if obj.type == "MESH":
            obj.data.transform(m)
            obj.data.update()


def build():
    options = k.args()
    outdir = options.get("outdir", os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "enemies"))
    only = set(options["only"].split(",")) if "only" in options else None
    if only is not None and "green_eye" not in only:
        return
    k.reset()
    eye()
    used = {m.name for obj in bpy.context.scene.objects if obj.type == "MESH" for m in obj.data.materials}
    print("== green_eye (5 79): %d triangles, %d materials: %s" % (triangles(), len(used), ", ".join(sorted(used))))
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    path = os.path.join(outdir, "green_eye.glb")
    k.export(path)
    print("%s: %d bytes" % (path, os.path.getsize(path)))
    # The checks and previews show the eye as the game does with the player straight below it.
    turned(180)
    if "check" in options:
        k.check_silhouette(os.path.join(options["check"], "enemy_5.png"), 79)
    if "preview" in options:
        preview(options["preview"] + "green_eye", distance=0.6)


if __name__ == "__main__":
    build()
