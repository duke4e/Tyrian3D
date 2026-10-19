"""The violet pincer of GYGES, MISTAKES and CRUSTGATE (sheet G sprite 121, 2x2: 24 x 27 pixels; enemy 184, in the sky;
its animation plays when it fires: 121 123 123 123 125 125 125 123 123 123 121), polished (2026-10-19; it replaces
wave3_r_beasts.py's violet_pincer() and wave3_at_g.py's violet_pincer_<sprite> frames). models.cfg: sprite g 121
violet_pincer yaw=0, frame g 123 violet_pincer_123, frame g 125 violet_pincer_125 (all three unchanged). No other
enemy shows these sprites; they are no other sprites' pixels mirrored or in other ramps.

As the sprites and their 4x upscales draw it: a glossy violet ball of a head (ramp 5; rows 0-8, columns 7-17), a pale
highlight at its upper left; from its lower sides two arms hang in an arch, each of two bulging segments (the upper
one, rows 9-14, reaching out and down; the lower one, rows 15-19, hanging down at the sprite's sides) with dark
joints between them, ending in a golden fang (ramp 1, rows 20-25) that runs down and curls in to its point. When it
fires it closes its arms and its head charges: in 123 the arms swing in by a pixel (the upper segments about their
shoulders, the lower segments and fangs a pixel in) and the head's highlight turns white; in 125 the upper segments
are two pixels in, the lower ones and the fangs three, and the whole head glows a pale violet. One model per frame:
the head painted with its frame's light (glowing in its own colours as it charges), the arms posed as the frame
draws them; all three span the same bounds, so the game, which centres sky models in height, keeps them in place.

The head: a painted ball (polish_balls): its body, a highlight in bands and a darker rim. The arms: each segment a
bead lofted between its two joints (fattest past its middle, a little flattened), dark knobs at the joints, the
fangs tapering tubes along curved paths, glossy gold.

The sprite is symmetric about its column 12 (x 0.5 here): the creature is built about u = 0 and moved there. Origin
at the sprite's centre (pixel 12, 14); +Y up the sprite, +Z towards the camera.

Replaces wave3_r_beasts.py's violet_pincer() (its @r.model("violet_pincer", [(121, True)]) function and its
docstring lines; wave3_r_art.py's PINCER and PINCER_MID, which nothing reads) and wave3_at_g.py's
violet_pincer_closed() and the loop registering violet_pincer_123 and _125 (the tusk beetle there stays): remove
them so that they don't overwrite these models. (wave3_at_g.py's violet_pincer_closed calls
wave3_r_beasts.violet_pincer(): both go together.)

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each frame's silhouette
against its sprite in enemy_G.png), --preview <prefix>, --only <name,...>.
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
from polish_squid_ship import catmull, tube  # noqa: E402

AXIS_X = 0.5

HEAD = Ellipsoid((0.0, 9.05, 5.6), (5.1, 4.6, 4.6))
# The left arm's joints (u, y, z): the shoulder under the head, the elbow, the wrist; the fang's path from the
# wrist to its point. Per frame, how far in (towards the axis) the elbow, the wrist and the fang move.
SHOULDER = Vector((-3.15, 4.75, 4.6))
ELBOW = Vector((-7.05, -0.85, 3.9))
WRIST = Vector((-8.05, -5.95, 3.4))
FANG = [Vector((-8.05, -5.6, 3.4)), Vector((-8.45, -7.6, 3.05)), Vector((-8.35, -9.4, 2.7)),
        Vector((-7.6, -10.9, 2.4)), Vector((-6.2, -11.9, 2.15)), Vector((-4.4, -12.3, 2.0))]
UPPER_RADII = (3.45, 2.7)     # the upper segment's fattest half-width (in plan) and half-height
LOWER_RADII = (3.5, 2.75)
FANG_ROOT = 1.85

# The frames: (model, sprite, (elbow, wrist, fang) moved in by, the head's light: (highlight's size, shades of its
# body, its mid band, its light band and its core, and their emission strengths)).
FRAMES = [
    ("violet_pincer", 121, (0.0, 0.0, 0.0),
     (1.0, (0x57, 0x5a, 0x5d, 0x5f), (0.12, 0.2, 0.35, 0.6))),
    ("violet_pincer_123", 123, (1.0, 1.0, 1.0),
     (1.3, (0x58, 0x5b, 0x5e, 0x5f), (0.2, 0.4, 0.75, 1.1))),
    ("violet_pincer_125", 125, (2.0, 3.0, 3.1),
     (2.4, (0x5a, 0x5d, 0x5e, 0x5f), (0.45, 0.8, 1.15, 1.5))),
]
HIGHLIGHT = Vector((-0.9, 10.15))      # the highlight's middle in the top view (columns 10-12 of rows 3-4)
HIGHLIGHT_SIZE = Vector((1.6, 1.35))
RIM_Z = 0.32                          # the head darker where its normal's z is below this


def materials(shades, glows):
    pal = k.level_palette()
    m = {
        "segment": k.material("pincer_segment", palette=0x58, metallic=0.3, roughness=0.24),
        "joint": k.material("pincer_joint", palette=0x53, metallic=0.25, roughness=0.4),
        "gold": k.material("pincer_gold", palette=0x1c, metallic=0.15, roughness=0.2),
        "head_rim": k.material("pincer_head_rim", palette=0x55, metallic=0.2, roughness=0.3),
    }
    for key, index, glow in zip(("head", "head_mid", "head_light", "head_core"), shades, glows):
        m[key] = k.material(f"pincer_{key}_{index:x}", palette=index, metallic=0.15, roughness=0.14,
                            emission=pal[index], emission_strength=glow)
    return m


# --- The head ---------------------------------------------------------------------------------------------------

def head(m, size):
    def light(p, n):
        if n.z < 0.0:
            return 0.0
        q = Vector(((p.x - HIGHLIGHT.x) / (HIGHLIGHT_SIZE.x * size), (p.y - HIGHLIGHT.y) / (HIGHLIGHT_SIZE.y * size)))
        return math.exp(-q.length_squared) * smoothstep(0.0, 0.5, n.z)

    def rim(p, n):
        return n.z

    paint = [
        (rim, (RIM_Z,), ("head_rim", "head")),
        (light, (0.2, 0.48, 0.78), (None, "head_mid", "head_light", "head_core")),
    ]
    painted_ball("head", HEAD, paint, m, subdivisions=5, smooth_angle=70)


# --- The arms ---------------------------------------------------------------------------------------------------

def bead(name, p0, p1, radii, mat, rings=14, segments=20, bulge=0.55):
    """A segment lofted from joint p0 to joint p1: round in section (radii: half-width across in plan and
    half-height), fattest a little past its middle, closing to the joints."""
    axis = p1 - p0
    t_dir = axis.normalized()
    side = t_dir.cross(Vector((0, 0, 1))).normalized()
    up = side.cross(t_dir).normalized()
    out = []
    for i in range(rings + 1):
        t = i / rings
        f = math.sin(math.pi * min(1.0, t / (2 * bulge) if t < bulge else 0.5 + (t - bulge) / (2 * (1 - bulge))))
        f = max(f, 0.0) ** 0.45
        c = p0 + axis * t
        ring = []
        for j in range(segments):
            a = 2 * math.pi * j / segments
            ring.append(c + side * (math.cos(a) * radii[0] * f) + up * (math.sin(a) * radii[1] * f))
        out.append(ring)
    obj = k.loft(name, out[1:-1], mat, start_point=p0 + t_dir * 0.05, end_point=p1 - t_dir * 0.05)
    return k.smooth(obj, 60)


def arm(m, moves):
    """The left arm, posed: its elbow, wrist and fang moved in by `moves`."""
    e_in, w_in, f_in = moves
    elbow = ELBOW + Vector((e_in, 0.0, 0.0))
    wrist = WRIST + Vector((w_in, 0.0, 0.0))
    parts = []
    parts.append(bead("upper_l", SHOULDER + Vector((0.35, 0.75, 0.2)), elbow + Vector((0.15, -0.35, 0.0)),
                      UPPER_RADII, m["segment"]))
    parts.append(bead("lower_l", elbow + Vector((0.1, 0.45, 0.0)), wrist + Vector((0.1, -0.2, 0.0)), LOWER_RADII,
                      m["segment"]))
    for name, p, r in (("shoulder_l", SHOULDER, 1.15), ("elbow_l", elbow, 1.05), ("wrist_l", wrist, 1.05)):
        parts.append(k.smooth(k.ellipsoid(name, tuple(p), (r, r * 0.95, r * 0.85), m["joint"], 14, 7), 60))
    # The fang: from the wrist down and curling in to its point, tapering.
    pts = []
    for i, p in enumerate(FANG):
        t = i / (len(FANG) - 1)
        shift = w_in + (f_in - w_in) * t
        pts.append(p + Vector((shift, 0.0, 0.0)))
    path = catmull(pts, 0.3)
    n = len(path)
    radii = [FANG_ROOT * (1 - (i / (n - 1)) ** 2.0) ** 0.75 + 0.05 for i in range(n)]
    parts.append(tube("fang_l", path, radii, m["gold"], segments=12, squash=0.8))
    return parts


def build_model(moves, light):
    k.reset()
    size, shades, glows = light
    m = materials(shades, glows)
    head(m, size)
    for part in arm(m, moves):
        copy = k.mirror_x(part, part.name[:-2] + "_r")
        copy.data.name = copy.name
        k.smooth(copy, 60)
    for obj in bpy.context.scene.objects:
        if obj.type == "MESH":
            obj.data.transform(Matrix.Translation((AXIS_X, 0.0, 0.0)))


def bounds():
    vs = [obj.matrix_world @ v.co for obj in bpy.context.scene.objects if obj.type == "MESH" for v in obj.data.vertices]
    return [min(v[i] for v in vs) for i in range(3)], [max(v[i] for v in vs) for i in range(3)]


def build():
    options = k.args()
    outdir = options.get("outdir", os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "enemies"))
    only = set(options["only"].split(",")) if "only" in options else None
    for name, sprite, moves, light in FRAMES:
        if only is not None and name not in only:
            continue
        build_model(moves, light)
        used = {m.name for obj in bpy.context.scene.objects if obj.type == "MESH" for m in obj.data.materials}
        low, high = bounds()
        print("== %s (G %d): %d triangles, %d materials, x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f: %s" % (
            name, sprite, triangles(), len(used), low[0], high[0], low[1], high[1], low[2], high[2],
            ", ".join(sorted(used))))
        if "check" in options:
            k.check_silhouette(os.path.join(options["check"], "enemy_G.png"), sprite)
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        path = os.path.join(outdir, name + ".glb")
        k.export(path)
        print("%s: %d bytes" % (path, os.path.getsize(path)))
        if "preview" in options:
            preview(options["preview"] + name)


if __name__ == "__main__":
    build()
