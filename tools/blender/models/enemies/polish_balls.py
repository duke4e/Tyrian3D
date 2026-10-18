"""The glossy balls of the asteroid levels, polished (2026-10-18; they replace ball.py's plain spheres).

- ball: sheet M sprite 115 (2x2: an 18 x 17 ball in the 24 x 28 cell; on the ground in ASTEROID?,
  MINEMAZE, GAUNTLET and ** ALE **, about 200 of them), a glossy blue ball. Sheet A sprite 279, the
  brightest frame of A 165's animation, is the same picture.
- ball_dark: sheet A sprites 165 (dark blue; MINEMAZE, MINES, GAUNTLET, MACES, on the ground and in the
  sky), 281 (bronze) and 283 (grey; MINES, MINEMAZE, ASTEROIDS): the same ball five shades darker (A 283
  drawn a little differently, a pixel wider). A 165's animation brightens it, three game frames each:
  165 203 241 279 241 203. Its frames are models of their own: ball_dark_203 (two shades lighter than
  ball_dark), ball_dark_241 (three) and ball itself for 279 (models.cfg: frame a 203 ball_dark_203,
  frame a 241 ball_dark_241, frame a 279 ball).

As the 4x upscales draw it: a glossy ball (the sprite's columns 3-20 and rows 5-21) outlined by a dark
rim, lighter at its upper left than at its lower right, with a white glare above its middle on the left
(columns 8-11, rows 9-12) and a bright crescent inside its rim at the lower right (rows 15-20), where
the light through it gathers, as in a marble. The darker frames keep the glare white but smaller and
the crescent bright.

The models are the ball with that light painted on: the glare (where the game's sun, from above and the
top left, puts its own highlight too), the crescent and the rim; the game's light shades the rest. All
materials are palette colours of ramp 3 (the blue of M 115) without emission: models.cfg colours them
with the sprite's frame (color=sprite: every palette index takes the frame's ramp and keeps its shade),
so one model is the blue, grey, bronze or purple ball. Emission would keep its own colour, so the
side of the ball the game's sun doesn't reach (which its camera sees much of) is lifted with lighter
shades than the sprite's instead (SHADE_LIFT).

- orb_whorl: the purple orbs of the same levels, sheet M sprite 117 (frames 117 119 121 119, four game
  frames each; on the ground in ASTEROID?, MINEMAZE, GAUNTLET and ** ALE **, about 130 of them), which
  models.cfg shows as the ball today. The upscale draws no ball but a coiled shell, like an ammonite: a
  rounded knob above the middle on the left (columns 7-12, rows 8-13 of 117), a dark groove curling
  round it from its left, under it and up its right side, and the shell's outer coil round that, a
  glossy purple (ramp 5) with a dark rim (palette 0x21, nearly black). Its frames swell it: 117 spans
  15 x 16 pixels (columns 4-18, rows 6-21), 119 17 x 18 and 121 19 x 21, each darker and with a wider
  dark rim, so a model per frame: orb_whorl, orb_whorl_119 and orb_whorl_121 (models.cfg: sprite m 117
  orb_whorl yaw=0, frame m 119 orb_whorl_119, frame m 121 orb_whorl_121).

Origin at the sprite's centre (pixel 12, 14); +Y up the screen, +Z towards the camera. The balls stand
on z = 0 (their middle at (0, 0.5), the sprite's columns 3-20 and rows 5-21 round pixel 12, 13.5).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouette
of each model against its sprite), --preview <prefix>, --only <name,...>, --ramp <0-15> (for checks:
the models in another ramp, as color=sprite shows them, written as <name>_r<ramp>.glb).
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


# --- Painted spheres --------------------------------------------------------------------------------

class Ellipsoid:
    def __init__(self, centre, radii):
        self.centre, self.radii = Vector(centre), Vector(radii)

    def point(self, d):
        """The surface's point and normal in the direction d (a unit vector) from the middle."""
        r = self.radii
        p = self.centre + Vector((d.x * r.x, d.y * r.y, d.z * r.z))
        n = Vector((d.x / r.x, d.y / r.y, d.z / r.z)).normalized()
        return p, n


def painted_ball(name, shape, paint, mats, subdivisions=5, displace=None, smooth_angle=80):
    """An icosphere mapped onto shape (point(d) -> point, normal), its faces cut along the borders of
    the painted fields so the colours meet along smooth lines. paint: [(field(point, normal) -> value,
    borders ascending, keys: one per band from the lowest up, a key of mats or None to keep what the
    fields before gave)]; later fields paint over earlier ones. displace(d, point, normal) -> how far
    to move the point out along its normal, optional."""
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subdivisions, radius=1.0)
    for field, borders, _ in paint:
        for t in borders:
            split_along(bm, {v: field(*shape.point(v.co.normalized())) for v in bm.verts}, t)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    kinds = []
    for f in bm.faces:
        d = f.calc_center_median().normalized()
        p, n = shape.point(d)
        kind = None
        for field, borders, keys in paint:
            value = field(p, n)
            band = sum(value > t for t in borders)
            if keys[band] is not None:
                kind = keys[band]
        kinds.append(kind)
    for v in bm.verts:
        d = v.co.normalized()
        p, n = shape.point(d)
        v.co = p + (n * displace(d, p, n) if displace is not None else Vector())
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    names = []
    for kind in kinds:
        if mats[kind].name not in names:
            names.append(mats[kind].name)
            mesh.materials.append(mats[kind])
    for poly, kind in zip(mesh.polygons, kinds):
        poly.material_index = names.index(mats[kind].name)
    k.recalc_normals(obj)
    return k.smooth(obj, smooth_angle)


def gauss(u, v):
    return math.exp(-u * u - v * v)


def angle_off(a, b):
    """a - b in degrees, wrapped to -180..180."""
    return (a - b + 180.0) % 360.0 - 180.0


# --- The balls ----------------------------------------------------------------------------------------

BALL = Ellipsoid((0.0, 0.5, 8.75), (9.0, 8.5, 8.75))

# The dark rim where the ball turns away from the camera (its normal's z below RIM: the sprite's
# outermost pixel); the glare: its middle and half-sizes seen from above (the white of columns 8-11,
# rows 9-12), a rounded oblong (GLARE_POWER) shrunk by the frame's glare scale, its soft edge in
# thin bands; the crescent: round the direction CRESCENT_AT seen from above (degrees from +X),
# CRESCENT_SPREAD either side, its middle where the normal's z is CRESCENT_Z, CRESCENT_WIDTH either
# side (rows 15-20, brightest at columns 14-17).
RIM = 0.33
GLARE, GLARE_SIZE, GLARE_POWER = Vector((-2.1, 2.5)), Vector((2.6, 2.0)), 2.4
CRESCENT_AT, CRESCENT_SPREAD = -58.0, 36.0
CRESCENT_Z, CRESCENT_WIDTH = 0.48, 0.15
# The game's camera sees much of the ball's side away from its sun: the body is a shade lighter than
# the sprite's (SHADE_LIFT) and the rim only RIM_DARK shades darker than the sprite's body. The
# crescent, on that side, glows a little in white (CRESCENT_GLOW: its outer band and core), the colour
# of the light it stands for; white is the lightest shade of every ramp, so color=sprite needs no
# other colour of it.
SHADE_LIFT = 1
RIM_DARK = 5
CRESCENT_GLOW = (0.12, 0.3)
WHITE = (205, 205, 205)

# The frames: (model, sheet:sprite, the sprite's body shade, the glare's shades (edge, middle, core)
# and scale, the crescent's shades (outer, core) and scale).
BALL_FRAMES = [
    ("ball", "M:115", 10, (12, 14, 15), 1.0, (12, 14), 1.0),
    ("ball_dark_241", "A:241", 8, (11, 13, 15), 0.82, (11, 13), 0.95),
    ("ball_dark_203", "A:203", 7, (11, 13, 15), 0.74, (10, 13), 0.9),
    ("ball_dark", "A:165", 5, (10, 13, 15), 0.56, (9, 13), 0.8),
]
BALL_RAMP = 3
# The light the sprites are drawn in: from the upper left and above.
SPRITE_LIGHT = Vector((-0.55, 0.62, 0.56)).normalized()


def ball_paint(glare_scale, crescent_scale):
    def rim(p, n):
        return n.z

    def glare(p, n):
        if n.z <= 0.3:
            return 0.0
        u = abs(p.x - GLARE.x) / (GLARE_SIZE.x * glare_scale)
        v = abs(p.y - GLARE.y) / (GLARE_SIZE.y * glare_scale)
        return math.exp(-(u ** GLARE_POWER + v ** GLARE_POWER))

    def crescent(p, n):
        if n.z <= 0:
            return 0.0
        a = math.degrees(math.atan2(p.y - BALL.centre.y, p.x - BALL.centre.x))
        return gauss(angle_off(a, CRESCENT_AT) / (CRESCENT_SPREAD * crescent_scale),
                     (n.z - CRESCENT_Z) / (CRESCENT_WIDTH * crescent_scale))

    return [
        (rim, (RIM,), ("rim", "body")),
        (crescent, (0.25, 0.62), (None, "crescent", "crescent_core")),
        (glare, (0.24, 0.38, 0.54), (None, "glare", "glare_mid", "glare_core")),
    ]


def ball_materials(prefix, body, glare, crescent, ramp):
    keys = {
        "body": min(15, body + SHADE_LIFT), "rim": max(0, body - RIM_DARK),
        "glare": glare[0], "glare_mid": glare[1], "glare_core": glare[2],
        "crescent": crescent[0], "crescent_core": crescent[1],
    }
    finish = {"body": dict(metallic=0.0, roughness=0.28), "rim": dict(metallic=0.0, roughness=0.55),
              "crescent": dict(metallic=0.0, roughness=0.15, emission=WHITE, emission_strength=CRESCENT_GLOW[0]),
              "crescent_core": dict(metallic=0.0, roughness=0.15, emission=WHITE,
                                    emission_strength=CRESCENT_GLOW[1])}
    return {key: k.material(f"{prefix}_{key}", palette=16 * ramp + s,
                            **finish.get(key, dict(metallic=0.0, roughness=0.15)))
            for key, s in keys.items()}


def ball(name, body, glare, glare_scale, crescent, crescent_scale, ramp):
    painted_ball(name, BALL, ball_paint(glare_scale, crescent_scale), ball_materials(name, body, glare, crescent, ramp))


# --- The whorled orb (M 117) ------------------------------------------------------------------------------

# The frames: (model, sheet:sprite, the orb's middle (x, y) and radii (its outline included), how many
# shades darker than 117 it is, how much wider its dark rim is (in units of the radius)).
ORB_FRAMES = [
    ("orb_whorl", "M:117", (-0.5, 0.0), (7.5, 8.0, 7.0), 0, 0.0),
    ("orb_whorl_119", "M:119", (-0.5, 0.0), (8.5, 9.0, 7.9), 2, 0.06),
    ("orb_whorl_121", "M:121", (-0.5, 0.5), (9.5, 10.5, 8.9), 3, 0.16),
]
ORB_RAMP = 5
ORB_OUTLINE = 0x21     # the sprite's outline: nearly black (ramp 2 shade 1)
# The coil, in the orb's top view scaled to a unit circle (u, v): the knob, raised KNOB_RISE (in units of
# the radius) within KNOB_RADIUS of KNOB; its highlight at HIGHLIGHT; the groove round it, from GROOVE_START
# (degrees round the knob from +X) clockwise, GROOVE_RADIUS from the knob growing by GROOVE_GROWTH a
# half turn, GROOVE_WIDTH wide and GROOVE_DEPTH deep, fading in over its first GROOVE_FADE_IN radians
# and out between GROOVE_FADE_OUT; the outer coil's crest RIDGE_RADIUS from the knob, RIDGE_WIDTH wide,
# brightest round RIDGE_BRIGHT (degrees, the lower right).
KNOB, KNOB_RADIUS, KNOB_RISE = Vector((-0.2, 0.28)), 0.6, 0.085
HIGHLIGHT, HIGHLIGHT_SIZE = Vector((-0.22, 0.37)), 0.17
GROOVE_START, GROOVE_RADIUS, GROOVE_GROWTH = 50.0, 0.47, 0.07
GROOVE_WIDTH, GROOVE_DEPTH = 0.15, 0.12
GROOVE_FADE_IN, GROOVE_FADE_OUT = 0.35, (2.3, 3.9)
RIDGE_RADIUS, RIDGE_WIDTH, RIDGE_BRIGHT = 0.8, 0.17, -45.0
ORB_OUTLINE_Z = 0.36   # the outline: where the normal's z is below this
ORB_RIM_Z = (0.4, 0.62)  # the darker band inside it: shading in between


class Coil:
    """The whorl's fields at a point of the orb seen from above (u, v: scaled to the unit circle)."""

    def __init__(self, centre, radii):
        self.centre, self.radii = Vector(centre), Vector(radii)

    def uv(self, p):
        return Vector(((p.x - self.centre.x) / self.radii.x, (p.y - self.centre.y) / self.radii.y))

    def knob(self, q):
        return smoothstep(KNOB_RADIUS, KNOB_RADIUS * 0.3, (q - KNOB).length)

    def groove(self, q):
        d = q - KNOB
        turn = math.radians((GROOVE_START - math.degrees(math.atan2(d.y, d.x))) % 360.0)
        radius = GROOVE_RADIUS + GROOVE_GROWTH * turn / math.pi
        fade = smoothstep(0.0, GROOVE_FADE_IN, turn) * (1 - smoothstep(*GROOVE_FADE_OUT, turn))
        return fade * math.exp(-((d.length - radius) / GROOVE_WIDTH) ** 2)

    def ridge(self, q):
        d = q - KNOB
        a = math.degrees(math.atan2(d.y, d.x))
        bright = 0.35 + 0.65 * math.exp(-(angle_off(a, RIDGE_BRIGHT) / 55.0) ** 2)
        return bright * math.exp(-((d.length - RIDGE_RADIUS) / RIDGE_WIDTH) ** 2)

    def highlight(self, q):
        return math.exp(-((q - HIGHLIGHT).length / HIGHLIGHT_SIZE) ** 2)


def orb_whorl(name, centre, radii, darker, rim_wider, ramp):
    shape = Ellipsoid((centre[0], centre[1], radii[2]), radii)
    coil = Coil(centre, radii)
    seen = lambda n: smoothstep(0.15, 0.45, n.z)  # noqa: E731  the relief fades out down the sides
    scale = (radii[0] + radii[1]) / 2

    def displace(d, p, n):
        q = coil.uv(p)
        return scale * seen(n) * (KNOB_RISE * coil.knob(q) - GROOVE_DEPTH * coil.groove(q) +
                                  0.03 * coil.ridge(q))

    def shade(p, n):
        """The sprite's shade (0-15 of ramp 5) at this point."""
        q = coil.uv(p)
        lit = n.dot(SPRITE_LIGHT)
        value = (8.0 + 0.9 * lit + 1.8 * coil.knob(q) + 3.8 * coil.highlight(q) - 4.2 * coil.groove(q) +
                 3.2 * coil.ridge(q))
        rim = 1 - smoothstep(ORB_RIM_Z[0] + rim_wider, ORB_RIM_Z[1] + rim_wider, n.z)
        return value * seen(n) + 7.0 * (1 - seen(n)) - 3.5 * rim - darker

    def outline(p, n):
        return n.z

    shades = list(range(3, 15))
    paint = [(shade, [s - 0.5 for s in shades[1:]], ["s%d" % s for s in shades]),
             (outline, (ORB_OUTLINE_Z + rim_wider * 0.5,), ("outline", None))]
    mats = {"s%d" % s: k.material(f"{name}_{s:x}", palette=16 * ramp + s, metallic=0.0,
                                  roughness=0.55 if s < 9 else 0.3 if s < 11 else 0.2,
                                  emission=k.level_palette()[16 * ramp + s], emission_strength=0.3)
            for s in shades}
    mats["outline"] = k.material(f"{name}_outline", palette=ORB_OUTLINE, metallic=0.0, roughness=0.5)
    painted_ball(name, shape, paint, mats, displace=displace, smooth_angle=70)


# --- Build ----------------------------------------------------------------------------------------------

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


def preview(prefix, size=(24, 28), distance=1.0):
    """The top view (framed like the sprite) and a three-quarter view, as tyrkit.preview, the
    three-quarter camera brought nearer for small models (distance: its distance's scale)."""
    scene = bpy.context.scene
    k.preview(prefix, size)
    if distance != 1.0:
        cam = bpy.data.objects["3q"]
        cam.location = cam.location * distance
        scene.camera = cam
        scene.render.filepath = prefix + "_3q.png"
        bpy.ops.render.render(write_still=True)


def models():
    out = []
    for name, sprite, body, glare, scale, crescent, crescent_scale in BALL_FRAMES:
        out.append((name, sprite, lambda ramp, a=(name, body, glare, scale, crescent, crescent_scale): ball(*a, ramp=ramp),
                    BALL_RAMP))
    for name, sprite, centre, radii, darker, rim_wider in ORB_FRAMES:
        out.append((name, sprite, lambda ramp, a=(name, centre, radii, darker, rim_wider): orb_whorl(*a, ramp=ramp),
                    ORB_RAMP))
    return out


def build():
    options = k.args()
    outdir = options.get("outdir", os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "enemies"))
    only = set(options["only"].split(",")) if "only" in options else None
    recolour = int(options["ramp"]) if "ramp" in options else None
    for name, sprite, make, ramp in models():
        if only is not None and name not in only:
            continue
        k.reset()
        make(recolour if recolour is not None else ramp)
        used = {m.name for obj in bpy.context.scene.objects if obj.type == "MESH" for m in obj.data.materials}
        print("== %s (%s): %d triangles, %d materials: %s" % (name, sprite, triangles(), len(used),
                                                               ", ".join(sorted(used))))
        if "check" in options:
            sheet, index = sprite.split(":")
            k.check_silhouette(os.path.join(options["check"], "enemy_%s.png" % sheet), int(index))
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        path = os.path.join(outdir, name + ("_r%d" % recolour if recolour is not None else "") + ".glb")
        k.export(path)
        print("%s: %d bytes" % (path, os.path.getsize(path)))
        if "preview" in options:
            preview(options["preview"] + name)


if __name__ == "__main__":
    build()
