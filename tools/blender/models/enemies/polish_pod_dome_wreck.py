"""The wrecks of DELIANI's ground pod (sheet C sprite 163, pod_dome) and of the bolt it launches (C 190, deli_bolt),
stage 4 of the clean ground (2026-10-26): what DELIANI's map (9589732b780e07b0) paints where they stand, which
tools/terrain/make_cleanground.py erases and the game shows as stand-ins (models.cfg "wreck c 163 pod_dome_wreck",
"wreck c 190 deli_bolt_wreck", drawn with the live sprite lines' options: yaw=0; the bolt line's glow is not drawn for
stand-ins).

As the map paints it (one 24 x 28 tile, the same at every place; at 4x in the HD tiles; the tile's column c and row r
are x = c + 0.5 - 12, y = 13.5 - r round its middle): a purple deck plate (0x56) whose round button (the clean ground's
plate shows it whole: a low dome of radius 8.5 in a dark ring) is blown open into a black pit (0x50, HD 0xfe) from the
plate's top edge to its bottom one. Round the pit the button's plating is torn into petals bent up out of it: the
right side broad and purple (columns 17-21) with a dark crack across its middle (row 13), up and right of the middle
a plate with two lit ribs (columns 15-17 of rows 3-9), at the left a plate standing up with a pale glint along its inner
edge (column 7 of rows 9-11) over a black pocket (columns 2-6 of rows 9-15), at the lower left a dark purple strip, at
the lower right a lifted lit plate (columns 13-18 of rows 19-23). In the pit a lit pillar runs up the screen from the
middle to the plate's top edge (columns 10-14 of rows 2-11, dark slots either side of a lighter middle, its foot lit
across); under its foot a red double arrow lies across the pit (rows 10-14, its heads at columns 7 and 16; 0x70-0x73,
the HD 0x70-0x76), under that a pale bracket (0x59-0x5c) bent down at both ends (columns 9-15 of rows 14-17), and
from below it dark claw blades splay out to the plate's corners (down and to the lower left, its tip glinting; small
ones to the upper left and right over the slate corners).

Built once (socket()) and given to both looks in their own frames: the floor of the pit, the button's rim broken into
arcs, six petals of its dome (sectors of the shell, their inner edges torn, swung up about their outer edges), the
pillar (polish_pod_turret.py's cowl, as polish_pod_dome.py uses it, slimmed and painted in the deck's purple: the pod's
cowl left standing in its socket), the bracket (the pod's bar, bent), the red double arrow (glowing dimly in ramp 7,
0x71 0.16, 0x73 0.28, its hot middles 0x75 0.36: well under the bloom's white), the claw blades, a few purple chunks;
the petals, the rim and the pillar scorched round the middle (a field's contours, a shade or two darker in the ramp:
polish_bronze_pump_wreck.scorch_map). Colours are the painting's: ramp 5 (0x50-0x5c), the wine 0xf1 under the arrow.

The frames: the pods drive about and the bolts fall, so the stand-ins' places are where they stood longest and the
painting lies differently under them; the socket is set where it lies under the places the references show (pod
513, 4207: the tile's middle 3 px right of the pod's and 7 px down the screen; bolt 513, 4202, the same tile: 3 right,
12 down), so that where a pod and its bolt stand in together the two sockets fall on each other. Both live models are
centred in height by the game (no origin flag): like pod_dome, each wreck carries a speck at PIN_Z, so that it is tall
enough to be set on the ground (its foot 0.3 over it, as the live pod's).

Coordinates: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the deck (z = 0); origins at the live
sprites' centres (pod_dome: pixel 12, 14 of its 24 x 28 sprite; deli_bolt: pixel 6, 7 of its 12 x 14 one).

models.cfg: model pod_dome_wreck enemies/pod_dome_wreck.glb; wreck c 163 pod_dome_wreck. The bolt is launched by the
pod, so it takes "wreck c 190 none" as the other launched enemies (the ice spike, the white dart): its socket is the
pod's; deli_bolt_wreck (--only deli_bolt_wreck) is not in the game.

Options after "--": --outdir <dir> (default assets/models/enemies), --preview <prefix>, --only <name,...>,
--socket 1 (also socket_wreck.glb: the socket round the tile's middle, for a stand-in set on the tile), --stats 1 (the
triangles part by part).
"""
import math
import os
import sys

import bmesh
import bpy
import mathutils.noise as noise
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
import polish_pod_turret as pt  # noqa: E402
import polish_pod_dome as pd  # noqa: E402
import polish_jaw_gun_wreck as wk  # noqa: E402  (the shared wreck helpers)
from polish_bronze_pump_wreck import scorch_map  # noqa: E402

# Where the socket's middle (the painted tile's) lies in each look's frame.
MODELS = [("pod_dome_wreck", (3.0, -7.0)), ("deli_bolt_wreck", (3.0, -12.0))]
PIN_Z = pd.PIN_Z
CENTRE = Vector((0.0, 0.3))      # the socket's middle (the tile's, a little up)
RIM = (8.9, 10.8)               # the socket's rim (over the clean ground's button, 8.5 round): its radii in x and y
DOME = 1.3                      # the button's dome over the rim, before it burst

# The rim's arcs that stay (degrees counter-clockwise from +x): from, to, their bead's width and height; the two at
# the sides stand higher, bent up into the cage of dark ribs the painting shows either side of the pillar.
RIM_ARCS = [(-62.0, 50.0, 1.7, 1.75), (96.0, 124.0, 1.3, 0.8), (132.0, 226.0, 1.8, 1.9), (266.0, 286.0, 1.3, 0.8)]
# The petals: from, to (degrees), their inner radius (torn) and outer one (the hinge), how far they are swung up
# (degrees), their top's material.
PETALS = [(8.0, 46.0, 4.6, 8.3, 24.0, "plate"),
          (-40.0, -3.0, 4.9, 8.3, 16.0, "plate"),
          (56.0, 82.0, 5.0, 9.9, 30.0, "plate"),
          (118.0, 152.0, 4.6, 8.4, 58.0, "plate"),
          (204.0, 236.0, 5.6, 8.4, 12.0, "shade"),
          (276.0, 312.0, 4.2, 9.9, 25.0, "lit")]
PETAL_T = 0.45                  # their thickness
RIB_PETAL, RIB_ANGLES = 2, (65.0, 76.0)   # the lit ribs on the upper right petal
# The pillar: polish_pod_turret's cowl scaled (x, y, z) about its back end and moved there (x, y, z).
PILLAR_SCALE, PILLAR_AT = (0.4, 0.8, 0.36), (0.2, 2.3, -0.12)
# The bracket: the pod's bar bent down at both ends (points x, y, z), its radius.
BRACKET = ([(-2.7, -3.1, 0.45), (-2.6, -1.4, 0.95), (-2.2, -0.4, 1.25), (0.4, -0.25, 1.4), (2.8, -0.4, 1.2),
            (3.1, -1.4, 0.9), (3.2, -2.7, 0.45)], 0.42)
# The red double arrow across the pit (plan), its height.
ARROW = [(-5.4, 1.4), (-2.4, 4.0), (-2.7, 2.0), (2.7, 1.95), (2.5, 3.9), (5.4, 1.35), (2.5, -1.3), (2.7, 0.3),
         (-2.7, 0.3), (-2.4, -1.25)]
ARROW_Z = (0.06, 0.42)
HOT = [((-3.6, 1.4, 0.42), (1.2, 0.95, 0.24)), ((3.6, 1.35, 0.42), (1.2, 0.95, 0.24))]
# The claw blades: path (x, y), width at the root and the tip, ridge height at the root and the tip.
BLADES = [([(-1.2, -3.6), (-3.0, -6.0), (-5.4, -8.2), (-7.4, -9.8), (-9.2, -11.4)], 3.6, 1.1, 1.15, 0.4),
          ([(0.8, -4.0), (0.9, -6.8), (0.4, -9.2), (-0.4, -11.0)], 2.8, 0.9, 1.0, 0.4),
          ([(2.8, -4.0), (4.4, -6.0), (6.0, -8.0), (7.4, -9.6)], 2.0, 0.7, 0.7, 0.3),
          ([(-4.4, 6.8), (-6.2, 8.6), (-7.8, 10.4), (-9.2, 11.9)], 2.2, 0.7, 0.75, 0.3),
          ([(4.4, 6.6), (6.2, 8.4), (7.8, 10.0), (9.0, 11.3)], 1.7, 0.6, 0.6, 0.25)]
# Purple chunks of the plating in the pit: centre, radii, material.
CHUNKS = [((-7.4, 1.4, 0.0), (1.15, 0.9, 0.6), "plate"), ((6.9, -2.4, 0.0), (0.9, 0.8, 0.5), "shade"),
          ((-4.6, -3.0, 0.0), (0.8, 0.7, 0.45), "shade"), ((-6.6, 5.8, 0.0), (0.7, 0.6, 0.4), "dark"),
          ((5.8, 4.8, 0.0), (0.75, 0.6, 0.4), "shade")]
BURN = (Vector((0.2, 1.2, 1.0)), 5.6)    # the scorch's middle and reach


def materials():
    pal = k.level_palette()

    def glow(name, index, strength):
        return k.material(name, palette=index, metallic=0.0, roughness=0.75, emission=pal[index],
                          emission_strength=strength)
    return {
        "pit": k.material("podw_pit", palette=0x50, metallic=0.1, roughness=0.85),
        "dark": k.material("podw_dark", palette=0x52, metallic=0.3, roughness=0.6),
        "shade": k.material("podw_shade", palette=0x54, metallic=0.35, roughness=0.5),
        "plate": k.material("podw_plate", palette=0x56, metallic=0.35, roughness=0.45),
        "lit": k.material("podw_lit", palette=0x58, metallic=0.35, roughness=0.4),
        "edge": k.material("podw_edge", palette=0x5a, metallic=0.45, roughness=0.32),
        "glint": k.material("podw_glint", palette=0x5c, metallic=0.45, roughness=0.28),
        "wine": k.material("podw_wine", palette=0xf1, metallic=0.1, roughness=0.8),
        "ember_dim": glow("podw_ember_dim", 0x71, 0.16),
        "ember": glow("podw_ember", 0x73, 0.3),
        "ember_hot": glow("podw_ember_hot", 0x75, 0.36),
    }


def on_rim(a, r=None):
    """The point on the rim (or at radius r, the rim's shape scaled) at angle a (degrees), in plan."""
    t = math.radians(a)
    s = 1.0 if r is None else r / RIM[0]
    return Vector((CENTRE.x + RIM[0] * s * math.cos(t), CENTRE.y + RIM[1] * s * math.sin(t)))


def dome(r):
    return DOME * max(0.0, 1.0 - (r / RIM[0]) ** 2) + 0.1


def paint_faces(obj, pick):
    """Gives each face the material pick(centre, normal) returns (a key of m), slots added as needed."""
    mk.paint(obj, pick)


def floor(m):
    outline = []
    for i in range(48):
        a = 360.0 * i / 48
        p = on_rim(a, 8.9 + 0.55 * noise.noise(Vector((math.cos(math.radians(a)) * 1.7, math.sin(math.radians(a)) * 1.7,
                                                         4.2))))
        outline.append((p.x, p.y))
    obj = mk.prism("pit_floor", wk.ccw(outline), 0.0, 0.08, m["pit"])
    return obj


def rim_arc(name, a0, a1, width, height, m, seed):
    """An arc of the button's rim: a rounded bead along the rim, torn off at its ends."""
    steps = max(4, int(abs(a1 - a0) / 6))
    rings = []
    for i in range(steps + 1):
        t = i / steps
        a = a0 + (a1 - a0) * t
        end = min(1.0, t / 0.12, (1.0 - t) / 0.12)
        f = (0.35 + 0.65 * math.sqrt(max(end, 0.0))) * (1.0 + 0.18 * noise.noise(Vector((a * 0.07, seed, 1.3))))
        c = on_rim(a)
        u = Vector((math.cos(math.radians(a)), math.sin(math.radians(a)), 0.0))
        ring = []
        for j in range(8):
            b = math.pi * j / 7
            ring.append(Vector((c.x, c.y, 0.0)) + u * (math.cos(b) * width / 2 * f) +
                        Vector((0, 0, 0.04 + math.sin(b) ** 0.8 * height * f)))
        rings.append(ring)
    obj = k.loft(name, rings, m["plate"])
    tall = height > 1.2   # (a rib of the cage: dark, its inner face lit)
    paint_faces(obj, lambda c, n: (m["dark"] if tall else m["plate"]) if n.z > 0.75 else
                m["dark"] if n.dot(Vector((c.x - CENTRE.x, c.y - CENTRE.y, 0.0)).normalized()) > 0 else
                (m["lit"] if tall else m["shade"]))
    mk.shade(obj, 40)
    return obj


def petal(name, a0, a1, r0, r1, lift, top, m, seed):
    """A petal of the button's dome: the sector of its shell between a0 and a1 from r0 (its inner edge, torn) out to r1,
    swung up by lift degrees about its outer edge (the hinge on the rim)."""
    na = max(4, int(round((a1 - a0) / 5.0)) + 1)
    nr = 4
    bm = bmesh.new()
    grid_t, grid_b = [], []
    for i in range(na):
        a = a0 + (a1 - a0) * i / (na - 1)
        torn = r0 + 0.75 * noise.noise(Vector((a * 0.11, seed * 1.7, 0.4))) + 0.35 * math.sin(a * 0.9 + seed)
        torn = min(torn, r1 - 1.6)
        row_t, row_b = [], []
        for j in range(nr):
            r = torn + (r1 - torn) * j / (nr - 1)
            p = on_rim(a, r)
            z = dome(r)
            row_b.append(bm.verts.new((p.x, p.y, z)))
            row_t.append(bm.verts.new((p.x, p.y, z + PETAL_T)))
        grid_t.append(row_t)
        grid_b.append(row_b)
    faces = {"top": [], "bottom": [], "inner": [], "side": []}
    for i in range(na - 1):
        for j in range(nr - 1):
            faces["top"].append(bm.faces.new((grid_t[i][j], grid_t[i + 1][j], grid_t[i + 1][j + 1], grid_t[i][j + 1])))
            faces["bottom"].append(bm.faces.new((grid_b[i][j], grid_b[i][j + 1], grid_b[i + 1][j + 1], grid_b[i + 1][j])))
    for i in range(na - 1):  # the torn inner edge and the outer one
        faces["inner"].append(bm.faces.new((grid_b[i][0], grid_b[i + 1][0], grid_t[i + 1][0], grid_t[i][0])))
        faces["side"].append(bm.faces.new((grid_t[i][nr - 1], grid_t[i + 1][nr - 1], grid_b[i + 1][nr - 1],
                                           grid_b[i][nr - 1])))
    for j in range(nr - 1):  # the two cut sides
        faces["side"].append(bm.faces.new((grid_t[0][j], grid_t[0][j + 1], grid_b[0][j + 1], grid_b[0][j])))
        faces["side"].append(bm.faces.new((grid_b[na - 1][j], grid_b[na - 1][j + 1], grid_t[na - 1][j + 1],
                                           grid_t[na - 1][j])))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    keys = {"top": top, "bottom": "dark", "inner": "lit" if lift > 40 else "edge", "side": "shade"}
    slots = {}
    for group, fs in faces.items():
        mat = m[keys[group]]
        if mat.name not in slots:
            obj.data.materials.append(mat)
            slots[mat.name] = len(obj.data.materials) - 1
        for f in fs:
            f.material_index = slots[mat.name]
    bm.to_mesh(mesh)
    bm.free()
    am = math.radians((a0 + a1) / 2)
    hinge = on_rim((a0 + a1) / 2, r1)
    axis = Vector((-math.sin(am), math.cos(am), 0.0))
    turn = Matrix.Translation((hinge.x, hinge.y, dome(r1))) @ Matrix.Rotation(math.radians(lift), 4, axis) @ \
        Matrix.Translation((-hinge.x, -hinge.y, -dome(r1)))
    obj.data.transform(turn)
    obj.data.update()
    mk.shade(obj, 35)
    made = [obj]
    if name == "petal%d" % RIB_PETAL:  # two lit ribs along it
        for n, a in enumerate(RIB_ANGLES):
            pts = []
            for t in (0.12, 0.4, 0.68, 0.92):
                r = r0 + 0.6 + (r1 - r0 - 1.0) * t
                p = on_rim(a, r)
                pts.append(turn @ Vector((p.x, p.y, dome(r) + PETAL_T + 0.12)))
            rib = mk.tube(f"{name}_rib{n}", pts, 0.34, m["lit"], 8)
            k.smooth(rib, 50)
            made.append(rib)
    if lift > 40:  # the glint along its torn inner edge
        pts = []
        for t in (0.15, 0.45, 0.75):
            a = a0 + (a1 - a0) * (0.25 + 0.5 * t)
            p = on_rim(a, r0 + 0.25)
            pts.append(turn @ Vector((p.x, p.y, dome(r0) + PETAL_T + 0.05)))
        glint = mk.tube(f"{name}_glint", pts, 0.2, m["glint"], 6)
        k.smooth(glint, 50)
        made.append(glint)
    return made


def pillar(m):
    """The pod's cowl left standing in the pit: polish_pod_turret.cowl() slimmed, in the deck's purple."""
    parts = pt.cowl({"cowl": m["plate"], "slot": m["pit"], "rib": m["lit"]})
    y0 = pt.COWL_Y[0]
    sx, sy, sz = PILLAR_SCALE
    turn = Matrix.Translation(PILLAR_AT) @ Matrix.Diagonal((sx, sy, sz, 1.0)) @ Matrix.Translation((0.0, -y0, 0.0))
    for obj in parts:
        obj.data.transform(turn)
        obj.data.update()
        dec = obj.modifiers.new("fewer", "DECIMATE")  # (built for a 10-pixel cowl; this one is 3 across)
        dec.ratio = 0.4
        mk.apply(obj)
    # Its foot lit across (the painting's lit cap at row 11).
    foot = mk.tube("pillar_foot", [(PILLAR_AT[0] - 1.5, PILLAR_AT[1] + 0.25, 0.95),
                                   (PILLAR_AT[0] + 1.6, PILLAR_AT[1] + 0.25, 0.95)], 0.36, m["edge"], 8)
    k.smooth(foot, 50)
    return parts + [foot]


def blade(name, path, w0, w1, h0, h1, m):
    """A claw blade lying on the deck: tapering along its path, a ridge along its middle."""
    dense = mk.chaikin([(x, y) for x, y in path], 2, closed=False)
    lengths = [0.0]
    for a, b in zip(dense, dense[1:]):
        lengths.append(lengths[-1] + math.dist(a, b))
    total = lengths[-1]
    rings = []
    for i, (x, y) in enumerate(dense):
        t = lengths[i] / total
        a, b = Vector(dense[max(i - 1, 0)]), Vector(dense[min(i + 1, len(dense) - 1)])
        d = (b - a).normalized()
        side = Vector((-d.y, d.x))
        w = (w0 + (w1 - w0) * t ** 0.8) / 2
        h = h0 + (h1 - h0) * t
        p = Vector((x, y))
        rings.append([Vector((*(p + side * w), 0.05)), Vector((*(p + side * w * 0.2), h)),
                      Vector((*(p - side * w * 0.35), h * 0.85)), Vector((*(p - side * w), 0.05))])
    tip = Vector(dense[-1]) + (Vector(dense[-1]) - Vector(dense[-2])).normalized() * 0.5
    obj = k.loft(name, rings, m["dark"], end_point=(tip.x, tip.y, 0.1))
    paint_faces(obj, lambda c, n: m["shade"] if n.z > 0.5 and n.x < 0.1 and n.y > -0.3 else None)
    mk.shade(obj, 30)
    return obj


def arrow(m):
    """The red double arrow across the pit, glowing dimly, on a scorch of dark wine."""
    outline = wk.ccw(ARROW)
    under = mk.prism("arrow_scorch", wk.ccw([(1.22 * x, 0.9 + 1.3 * (y - 0.9)) for x, y in ARROW]), 0.04, 0.12,
                     m["wine"])
    obj = mk.prism("arrow", outline, ARROW_Z[0], ARROW_Z[1], m["ember"])
    mk.bevel(obj, 0.12, 1, 35)
    mk.apply(obj)
    paint_faces(obj, lambda c, n: m["ember"] if n.z > 0.6 else m["ember_dim"])
    made = [under, obj]
    for i, (c, r) in enumerate(HOT):
        hot = wk.lump(f"arrow_hot{i}", c, r, m["ember_hot"], 7.3 + i, 0.2, 2)
        k.smooth(hot, 60)
        made.append(hot)
    return made


def scorch_field(co):
    c, reach = BURN
    d = (Vector(co) - c).length / reach
    return math.exp(-d * d) + 0.14 * noise.noise(Vector(co) * 0.6 + Vector((2.3, -1.1, 0.7)))


def socket(m):
    """The broken socket round its middle (the painted tile's: x, y 0)."""
    made = [floor(m)]
    for i, (a0, a1, width, height) in enumerate(RIM_ARCS):
        made.append(rim_arc(f"rim{i}", a0, a1, width, height, m, 3.1 + i))
    for i, (a0, a1, r0, r1, lift, top) in enumerate(PETALS):
        made += petal(f"petal{i}", a0, a1, r0, r1, lift, top, m, 1.7 + 0.9 * i)
    made += pillar(m)
    points, radius = BRACKET
    made.append(wk.bent_bar("bracket", points, radius, m["edge"], 8))
    made += arrow(m)
    for i, (path, w0, w1, h0, h1) in enumerate(BLADES):
        made.append(blade(f"blade{i}", path, w0, w1, h0, h1, m))
    for i, (c, radii, key) in enumerate(CHUNKS):
        made.append(wk.rock(f"chunk{i}", c, radii, m[key], 11.0 + 1.7 * i))
    for obj in made:
        mk.apply(obj)
        wk.clip_below(obj, 0.0)
    remap = {m["plate"].name: (m["shade"], m["dark"]), m["lit"].name: (m["plate"], m["shade"]),
             m["edge"].name: (m["lit"], m["plate"]), m["shade"].name: (m["dark"], m["pit"])}
    for obj in made:
        if obj.name.startswith(("rim", "petal", "cowl", "rib", "slot")):
            scorch_map(obj, scorch_field, remap, levels=(0.55, 0.85), step=1.6 if obj.name.startswith("petal") else None)
            wk.reshade(obj, 35)
    return made


def pin(m):
    e = 0.001
    return k.mesh_object("pin", [(0, 0, PIN_Z), (e, 0, PIN_Z), (0, e, PIN_Z)], [(0, 1, 2)], m["pit"])


def build():
    options = k.args()
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    # (The bolt's only when asked for: the game gives the launched bolt no wreck.)
    models = [mm for mm in MODELS if mm[0] != "deli_bolt_wreck" or (only and mm[0] in only)]
    models += [("socket_wreck", (0.0, 0.0))] if options.get("socket") == "1" else []
    for name, (dx, dy) in models:
        if only and name not in only:
            continue
        k.reset()
        bpy.context.scene.view_settings.view_transform = "Standard"
        m = materials()
        parts = socket(m)
        mk.transform(parts, Matrix.Translation((dx, dy, 0.0)))
        parts.append(pin(m))
        parts = [o for o in parts if len(o.data.polygons) > 0]
        bpy.context.view_layer.update()
        if options.get("stats") == "1":
            for obj in sorted(parts, key=lambda o: -mk.triangles([o])):
                print("   %-16s %6d triangles" % (obj.name, mk.triangles([obj])))
        mk.report(name, parts, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, parts, centre=(dx, dy))


if __name__ == "__main__":
    build()
