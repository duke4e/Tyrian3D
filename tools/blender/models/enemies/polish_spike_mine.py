"""The silver spiked mine of MINES, MINEMAZE, GAUNTLET, ASTEROIDS, FLEET and ** ALE ** (sheet A sprite
169, 2x2: a 17 x 16 ball in the 24 x 28 cell; on the ground, in the sky and on the top layer, about 250
of them; its animation 169 207 245, four game frames each, turns it), polished (2026-10-19; it replaces
rounds.py's spike_mine(), a dark ball with fourteen cones). models.cfg: sprite a 169 spike_mine yaw=0
spin=2 (the model turns as the sprite's frames do).

As the 4x upscale draws it: a studded chrome ball (columns 3-19, rows 5-20 of 169, the sprite's greys,
ramp 0), lighter at its upper left, darker at its lower right, its face dotted with bright studs (the
tips of the spikes that point at the viewer and rivets between them, white), and sharp grey spikes
standing out of its outline all round: up (column 11, rows 1-4), to the upper left (columns 2-4,
rows 4-5), left (row 13), right, a long one to the lower right (columns 17-21, rows 19-23), down
(rows 21-23) and shorter ones between them.

The model: a chrome ball, its surface hammered a little (broad soft dents), sixteen chrome spikes
flaring into the ball at their feet, their tips bright, and round rivets on the ball between them.
The spikes' directions follow 169: eight round the ball's middle, their tips where the sprite's spikes
are (those the sprite draws short lie higher or lower on the ball, foreshortened in the top view),
four above them (seen from above as studs on the ball's face) and four below, its feet on the ground.

Chrome mirrors its surroundings, and the game's sky is too dim in its reflections to show that (a
mirror-like steel reads dark there), so the ball carries its mirror image painted on, as a chrome
ball seen from above shows it: the bright sky over its middle, a dark horizon line round it (where
the surface faces about 45 degrees from straight up) and the darker ground below that, in the
sprite's greys; the spikes carry it too (light along their upper sides, dark beneath). The pattern
only depends on how far the surface faces from straight up, so it stays right as the mine turns, and
the dents make the horizon line waver as chrome's does. The tips and the rivets glow a little in
white, as the sprite's studs shine.

Also used by polish_spike_star.py and polish_fin_chevron.py: chrome() (the painted reflection on any
mesh) and join().

Origin at the sprite's centre (pixel 12, 14); +Y up the screen, +Z up from the ground: the mine
stands on the tips of its four lower spikes (z = 0). The ball's middle is at (-0.5, 0.5) (columns
3-19, rows 5-20 round pixel 11.5, 13.5).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the
silhouette against A 169 in <dir>/enemy_A.png), --preview <prefix>.
"""
import math
import os
import sys

import bmesh
import bpy
import mathutils.noise as noise
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402

CENTRE_XY = (-0.5, 0.5)
RADIUS = 8.0
# The hammered surface: broad dents and swellings and smaller ones (pixels of offset, and the noise's
# scale per pixel).
HAMMER = [(0.45, 0.3), (0.16, 0.8)]
# The painted reflection, by how far up the surface faces (its normal's z), from the bottom up:
# (lowest normal z, palette index, metallic, roughness, emission strength in its own grey): the ground
# under the mine, the ground towards the horizon, the horizon line, the sky above it and the sky's
# bright middle.
CHROME = [(-9.0, 0x06, 0.45, 0.3, 0.06), (0.2, 0x08, 0.45, 0.24, 0.08), (0.6, 0x04, 0.5, 0.3, 0.05),
          (0.68, 0x0b, 0.45, 0.18, 0.1), (0.84, 0x0d, 0.4, 0.16, 0.14)]

# The spikes: (heading in the top view, degrees counter-clockwise from +X; elevation above the
# ball's middle, degrees; the tip's distance from the ball's middle). The eight round the middle
# are 169's spikes (up, upper left, left, lower left, down, the long one to the lower right, right,
# upper right); four above them and four below, the mine's feet (FEET).
SPIKES = [
    (90.0, 2.0, 12.2), (137.0, 6.0, 12.0), (182.0, -2.0, 11.6), (225.0, 34.0, 12.0),
    (270.0, -28.0, 12.0), (315.0, -4.0, 12.8), (0.0, 26.0, 11.8), (45.0, 40.0, 11.8),
    (20.0, 64.0, 11.8), (110.0, 60.0, 11.8), (200.0, 63.0, 11.8), (290.0, 60.0, 11.8),
    (68.0, -50.0, 11.8), (158.0, -50.0, 11.8), (248.0, -50.0, 11.8), (338.0, -50.0, 11.8),
]
FEET = (12, 13, 14, 15)
# A spike: a cone rising out of the ball (CONE_BASE: its radius at the surface), a little concave, its
# foot flaring into the ball in a fillet (FILLET: its radius at the surface and how high it runs up
# the cone), its tip rounded; the bright tip TIP long.
CONE_BASE = 1.75
FILLET = (2.45, 0.9)
TIP = 1.3
# The rivets: round heads on the ball wherever the spikes leave room (at least RIVET_GAP degrees
# from every spike's axis and from each other), RIVET_RADIUS wide, RIVET_HEIGHT high.
RIVET_GAP, RIVET_RADIUS, RIVET_HEIGHT = 25.0, 0.8, 0.48


def direction(heading, elevation):
    a, e = math.radians(heading), math.radians(elevation)
    return Vector((math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)))


def centre():
    """The ball's middle: high enough that the feet's tips stand on z = 0."""
    lowest = min(SPIKES[i][2] * math.sin(math.radians(SPIKES[i][1])) for i in FEET)
    return Vector((CENTRE_XY[0], CENTRE_XY[1], -lowest))


def hammer(d):
    """The hammered surface's offset (pixels) in the direction d (a unit vector)."""
    return sum(size * noise.noise(d * (RADIUS * scale) + Vector((3.1 + i, 7.3, 1.7 - i)))
               for i, (size, scale) in enumerate(HAMMER))


def materials():
    pal = k.level_palette()
    m = {"chrome": [(lowest, k.material(f"mine_chrome_{index:02x}", palette=index, metallic=metallic,
                                         roughness=roughness, emission=pal[index], emission_strength=glow))
                    for lowest, index, metallic, roughness, glow in CHROME]}
    m["tip"] = k.material("mine_tip", palette=0x0e, metallic=0.3, roughness=0.15, emission=pal[0x0e],
                          emission_strength=0.35)
    m["rivet"] = k.material("mine_rivet", palette=0x0d, metallic=0.45, roughness=0.16, emission=pal[0x0d],
                            emission_strength=0.14)
    return m


def chrome(name, bm, bands, override=None):
    """A mesh object from a bmesh whose faces take the material of their band of the normal's z (bands:
    [(lowest normal z, material)] ascending: a painted reflection), the faces cut along the bands'
    borders first (contours of the vertex normals' z, so they run smoothly); override(face) may
    return another material for a face instead."""
    bm.normal_update()
    values = {v: v.normal.z for v in bm.verts}
    borders = [lowest for lowest, _ in bands[1:]]
    for t in borders:
        mk.split_along(bm, values, t)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    picks = []
    for f in bm.faces:
        mat = override(f) if override is not None else None
        if mat is None:
            mean = sum(values[v] for v in f.verts) / len(f.verts)
            mat = bands[sum(mean > t for t in borders)][1]
        picks.append(mat)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    names = []
    for mat in picks:
        if mat.name not in names:
            names.append(mat.name)
            mesh.materials.append(mat)
    for poly, mat in zip(mesh.polygons, picks):
        poly.material_index = names.index(mat.name)
    k.recalc_normals(obj)
    return obj


def ball(m, c):
    """An icosphere, finer on the side the cameras see, hammered, painted with the reflection."""
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=3, radius=1.0)
    seen = [e for e in bm.edges if all(v.co.normalized().z > -0.2 for v in e.verts)]
    bmesh.ops.subdivide_edges(bm, edges=seen, cuts=1, use_grid_fill=True)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    for v in bm.verts:
        d = v.co.normalized()
        v.co = c + d * (RADIUS + hammer(d))
    return k.smooth(chrome("ball", bm, m["chrome"]), 70)


def spike_profile(length):
    """(distance from the ball's middle, radius) from the root up to the tip."""
    r = RADIUS
    out = [(r - 1.0, 0.0), (r - 1.0, FILLET[0] - 0.3), (r - 0.35, FILLET[0])]
    cone = length - r
    for i in range(1, 3):  # the fillet: a quarter circle from the surface into the cone's side
        a = (math.pi / 2) * i / 3
        h = FILLET[1] * math.sin(a)
        out.append((r + h, CONE_BASE * (1 - h / cone) ** 1.2 + (FILLET[0] - CONE_BASE) * (1 - math.sin(a)) ** 1.6))
    start = r + FILLET[1]
    for i in range(1, 5):
        y = start + (length - start) * i / 5
        out.append((y, CONE_BASE * (1 - (y - r) / cone) ** 1.2))
    out[-1] = (length - 0.32, 0.2)
    out += [(length - 0.12, 0.1), (length, 0.0)]
    return out


def spike(name, m, c, d, length):
    """A spike along d, painted with the reflection as the ball is (the fillet runs on into the
    ball's bands), its tip bright."""
    obj = k.lathe(name, spike_profile(length), None, segments=12)
    turn = Vector((0, 1, 0)).rotation_difference(d).to_matrix().to_4x4()
    obj.data.transform(Matrix.Translation(c) @ turn)
    k.recalc_normals(obj)
    k.smooth(obj, 50)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bpy.data.objects.remove(obj)
    tip = lambda f: m["tip"] if (f.calc_center_median() - c).dot(d) > length - TIP else None  # noqa: E731
    return k.smooth(chrome(name, bm, m["chrome"], tip), 50)


def rivet_directions(spikes):
    """Evenly spread directions (a Fibonacci sphere) that keep RIVET_GAP from the spikes and each
    other, on the part of the ball the cameras see."""
    out = []
    count = 160
    golden = math.pi * (3 - math.sqrt(5))
    for i in range(count):
        z = 1 - 2 * (i + 0.5) / count
        r = math.sqrt(1 - z * z)
        d = Vector((r * math.cos(golden * i), r * math.sin(golden * i), z))
        if d.z < -0.25:
            continue
        if all(math.degrees(d.angle(s)) >= RIVET_GAP for s in spikes) and \
                all(math.degrees(d.angle(o)) >= RIVET_GAP * 0.8 for o in out):
            out.append(d)
    return out


def rivet(name, m, c, d):
    profile = [(RADIUS - 0.3, 0.0), (RADIUS - 0.3, RIVET_RADIUS)]
    for i in range(1, 5):
        a = (math.pi / 2) * i / 5
        profile.append((RADIUS + RIVET_HEIGHT * math.sin(a), RIVET_RADIUS * math.cos(a)))
    profile.append((RADIUS + RIVET_HEIGHT, 0.0))
    obj = k.lathe(name, profile, m["rivet"], segments=9)
    turn = Vector((0, 1, 0)).rotation_difference(d).to_matrix().to_4x4()
    obj.data.transform(Matrix.Translation(c + d * hammer(d)) @ turn)
    k.recalc_normals(obj)
    return k.smooth(obj, 60)


def mine(m):
    c = centre()
    ball(m, c)
    dirs = [direction(h, e) for h, e, _ in SPIKES]
    for i, ((_, _, length), d) in enumerate(zip(SPIKES, dirs)):
        spike(f"spike{i}", m, c, d, length)
    rivets = rivet_directions(dirs)
    for i, d in enumerate(rivets):
        rivet(f"rivet{i}", m, c, d)
    print("ball's middle at (%.2f, %.2f, %.2f), %d spikes, %d rivets" % (*c, len(SPIKES), len(rivets)))


def join(name, parts):
    """The parts as one object (one mesh: fewer primitives in the .glb)."""
    with bpy.context.temp_override(selected_editable_objects=parts, active_object=parts[0], object=parts[0]):
        bpy.ops.object.join()
    parts[0].name = name
    return parts[0]


def build():
    options = k.args()
    k.reset()
    mine(materials())
    parts = [join("spike_mine", mk.meshes())]
    if "check" in options:
        k.check_silhouette(os.path.join(options["check"], "enemy_A.png"), 169)
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    mk.report("spike_mine", parts, os.path.join(mk.outdir(options), "spike_mine.glb"))
    if "preview" in options:
        mk.preview(options["preview"] + "spike_mine", parts)


if __name__ == "__main__":
    build()
