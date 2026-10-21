"""CORAL's small starfish (sheet T sprite 89, 2x2: 24 x 28 pixels; enemy 1212 of episode 5, not animated: its only
frame is 89; armour 20). Polished (2026-10-21, round 24); it replaces wave3_v_sea.py's coral_starlet (its starfish()
reduced). CORAL sends it 19 times: 13 on the sea floor (ground events, type 10, t 3576-4500) and 6 high in the water
(sky events, type 15, t 5620-6300). No other enemy, launched ones included, shows T 89; no sprite in any sheet is its
pixels mirrored, turned or in other ramps (the starfish thrown in CORAL, T 127, is a bigger star of its own).

As the sprite and its 4x upscale draw it: a little tan starfish (ramp 1, 0x14-0x1c) a little above the sprite's middle
(columns 7-16 of rows 7-16, its disc at column 11.5, row 11.5), five short blunt arms: one straight up the screen (to
row 7), two out to the sides almost level (to columns 7 and 16 of row 11), two down and out (to columns 8 and 15 of row
16), the lower ones the longest; lit along the arms' ridges (0x1a-0x1c), darker down their flanks and towards the
lower left (0x14-0x16), a pale knob in the middle and on the right arm.

Built as such a creature lying on the floor: a heightfield over its plan, the plan the union of five tapering arms
(rounded tips) round a disc (polish_coral_manta.split_contour cuts the grid along it), the top a dome over each arm and
the disc blended smoothly (a soft maximum), a ridge along each arm, two small knobs (tubercles) along each ridge and a
bigger one in the middle, the edge meeting the floor, the underside flat on it. Painted in ramp 1's shades by how much
each part faces up and the sun, a little mottled (smooth noise), the knobs a shade lighter (their own zone): bands cut
along smooth contours (split_contour again), the rim at most a shade darker than just inside it (the dark edge left to
the light). The normals are the heightfield's own (by differences; level at the rim), so the small dome reads round.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the floor; origin at the
sprite's centre (pixel 12, 14): column c is x = c + 0.5 - 12, row r is y = 13.5 - r. It lies from z 0 (its base) to
about 2.

models.cfg: model coral_starlet enemies/coral_starlet.glb origin; sprite t 89 coral_starlet yaw=0 height=-4 (origin
and height=-4 lay it on the sea floor, on the terrain's relief too; in the sky events it floats 4 pixels under the sky
enemies' height). Replaces wave3_v_sea.py's coral_starlet (its @v.model("coral_starlet", ...) registration and the
coral_starlet() function; starfish() stays, coral_starfish uses it) and wave3_v_art.py's STARLET (read only by that
registration): remove them so that they don't overwrite this model.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouette against T 89
in enemy_T.png), --preview <prefix> (top and 3/4 views).
"""
import math
import os
import sys

import bmesh
import bpy
import mathutils.noise as noise
import numpy as np
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_coral_manta import split_contour  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402

CENTRE = (0.0, 2.0)           # the disc's middle (column 11.5, row 11.5)
DISC = (3.05, 2.0)            # its radius and height
# The arms: direction (degrees, 0 = right, counter-clockwise), length from the middle to the tip's outer edge,
# half-width at the root and at the tip, the ridge's height at the root and at the tip.
ARMS = [(90.0, 5.1, 1.95, 0.9, 1.55, 0.6), (171.0, 5.05, 1.9, 0.85, 1.45, 0.55), (234.0, 5.7, 2.0, 0.9, 1.45, 0.52),
        (305.0, 5.7, 2.0, 0.9, 1.45, 0.52), (8.0, 5.05, 1.9, 0.85, 1.45, 0.55)]
BLEND = 0.38                  # the soft maximum's blending (pixels of height)
RIDGE = 0.18                  # the ridge along each arm
KNOBS = [0.36, 0.7]           # tubercles along each arm (fractions of its length)
KNOB = (0.34, 0.2)            # their radius and height (smaller towards the tips)
CENTRE_KNOB = (0.55, 0.3)
GRID = 0.34
LIGHT = Vector((-0.6, 0.6, 1.0)).normalized()
MOTTLE = (0.55, 0.9)          # the mottling: how much (in shades), how many pixels across
# shades (lowest value, palette index of ramp 1)
BANDS = [(-99, 0x14), (3.6, 0x15), (4.6, 0x16), (5.6, 0x17), (6.6, 0x18), (7.6, 0x19), (8.6, 0x1a), (9.6, 0x1b)]
KNOB_BANDS = [(-99, 0x18), (6.4, 0x19), (7.6, 0x1b), (8.8, 0x1c)]
KNOB_EDGE = 0.1               # the knobs' painted edge (their height)
RIM_DARK = 1.1                # the rim at most this many shades darker than just inside it
FINISH = dict(metallic=0.08, roughness=0.55)


def arm_frame(arm):
    a = math.radians(arm[0])
    return np.array([math.cos(a), math.sin(a)])


def fields(x, y):
    """(inside: how far inside the plan, roughly in pixels; height of the top; knob field) at arrays x, y."""
    px, py = x - CENTRE[0], y - CENTRE[1]
    r = np.hypot(px, py)
    inside = DISC[0] - r
    rd = np.clip(r / DISC[0], 0.0, 1.0)
    tops = [DISC[1] * np.sqrt(np.maximum(0.0, 1.0 - rd ** 2))]
    knob = CENTRE_KNOB[1] * np.exp(-(r / CENTRE_KNOB[0]) ** 2)
    for arm in ARMS:
        d = arm_frame(arm)
        length, w0, w1, h0, h1 = arm[1:]
        along = px * d[0] + py * d[1]
        t = np.clip(along / (length - w1), 0.0, 1.0)
        cx, cy = t * (length - w1) * d[0], t * (length - w1) * d[1]
        q = np.hypot(px - cx, py - cy)
        w = w0 + (w1 - w0) * t
        inside = np.maximum(inside, w - q)
        h = h0 + (h1 - h0) * t ** 0.9
        prof = np.sqrt(np.maximum(0.0, 1.0 - (q / w) ** 2))
        side = np.abs((px - cx) * -d[1] + (py - cy) * d[0]) / w      # across the arm
        tops.append(h * prof + RIDGE * prof * np.exp(-(side / 0.35) ** 2) * (1.0 - t))
        for f in KNOBS:
            kx, ky = f * (length - w1) * d[0], f * (length - w1) * d[1]
            rr = KNOB[0] * (1.15 - 0.45 * f)
            knob = knob + KNOB[1] * (1.1 - 0.5 * f) * np.exp(-((px - kx) ** 2 + (py - ky) ** 2) / rr ** 2)
    stack = np.stack(tops)
    top = BLEND * np.log(np.sum(np.exp(stack / BLEND), axis=0)) - BLEND * math.log(len(tops))
    top = np.maximum(top, 0.0) * np.clip(inside / 0.35, 0.0, 1.0) ** 0.5
    return inside, top + knob * np.clip(inside / 0.5, 0.0, 1.0), knob


def outward(x, y):
    """The plan's outward direction (level) at arrays x, y: down the inside field's slope."""
    h = 0.02
    gx = (fields(x + h, y)[0] - fields(x - h, y)[0]) / (2 * h)
    gy = (fields(x, y + h)[0] - fields(x, y - h)[0]) / (2 * h)
    n = np.stack([-gx, -gy, np.zeros_like(gx)], axis=1)
    return n / np.maximum(np.linalg.norm(n, axis=1)[:, None], 1e-9)


def normals(x, y):
    h = 0.02
    gx = (fields(x + h, y)[1] - fields(x - h, y)[1]) / (2 * h)
    gy = (fields(x, y + h)[1] - fields(x, y - h)[1]) / (2 * h)
    n = np.stack([-gx, -gy, np.ones_like(gx)], axis=1)
    return n / np.linalg.norm(n, axis=1)[:, None]


def starlet(m):
    """The starfish: its top a heightfield over the plan, its underside flat on the floor; painted."""
    xs = np.arange(-6.5, 6.5 + 1e-6, GRID)
    ys = np.arange(-5.0, 8.0 + 1e-6, GRID)
    X, Y = np.meshgrid(xs, ys)
    inside = fields(X.ravel(), Y.ravel())[0].reshape(X.shape)
    bm = bmesh.new()
    verts = {}
    for j in range(len(ys)):
        for i in range(len(xs)):
            if inside[j, i] > -2 * GRID:
                verts[i, j] = bm.verts.new((float(xs[i]), float(ys[j]), 0.0))
    for j in range(len(ys) - 1):
        for i in range(len(xs) - 1):
            corner = [(i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)]
            if not all(c in verts for c in corner) or max(inside[c[1], c[0]] for c in corner) <= 0:
                continue
            a, b, c, e = (verts[q] for q in corner)
            if (i + j) % 2 == 0:
                bm.faces.new((a, b, c))
                bm.faces.new((a, c, e))
            else:
                bm.faces.new((a, b, e))
                bm.faces.new((b, c, e))
    vals = {"in": {}}
    for v in bm.verts:
        vals["in"][v] = float(fields(np.array([v.co.x]), np.array([v.co.y]))[0][0])
    split_contour(bm, vals, "in", 0.0)
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if sum(vals["in"][v] for v in f.verts) / len(f.verts) < 0],
                     context="FACES")
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    verts = list(bm.verts)
    x = np.array([v.co.x for v in verts])
    y = np.array([v.co.y for v in verts])
    _, top, knob = fields(x, y)
    nn = normals(x, y)
    out = outward(x, y)
    rim = {v for v in verts if vals["in"][v] <= 1e-6}
    vals["knob"], vals["shade"], vals["n"] = {}, {}, {}
    for v, z, kv, n, o in zip(verts, top, knob, nn, out):
        n = Vector(n)
        if v in rim:
            v.co.z = 0.0
            n = Vector(o)
        else:
            v.co.z = float(z)
        mottle = MOTTLE[0] * noise.noise(Vector((v.co.x / MOTTLE[1], v.co.y / MOTTLE[1], 3.3)))
        vals["shade"][v] = (6.7 + 3.0 * (n.dot(LIGHT) - LIGHT.z) + 3.4 * (n.z - 0.75) + 1.2 * v.co.z / DISC[1] +
                            mottle)
        vals["knob"][v] = float(kv)
        vals["n"][v] = n
    # (the rim no more than a little darker than just inside it: the dark edge comes from the light, not in steps)
    for v in rim:
        inner = [w for e in v.link_edges for w in e.verts if w is not v and w not in rim]
        if inner:
            vals["shade"][v] = max(vals["shade"][v], sum(vals["shade"][w] for w in inner) / len(inner) - RIM_DARK)
    # the knobs, then the shades within each
    faces = split_contour(bm, vals, "knob", KNOB_EDGE)
    zone = {f: sum(vals["knob"][v] for v in f.verts) / len(f.verts) > KNOB_EDGE for f in faces}
    for is_knob, bands in ((False, BANDS), (True, KNOB_BANDS)):
        zf = {f for f in zone if zone[f] == is_knob and f.is_valid}
        for lowest, _ in bands[1:]:
            zf = split_contour(bm, vals, "shade", lowest, zf)
        for f in zf:
            zone[f] = is_knob
    slots = []
    for f in bm.faces:
        bands = KNOB_BANDS if zone.get(f) else BANDS
        value = sum(vals["shade"][v] for v in f.verts) / len(f.verts)
        key = bands[0][1]
        for lowest, i in bands:
            if value >= lowest:
                key = i
        key = ("knob", key) if zone.get(f) else key
        if key not in slots:
            slots.append(key)
        f.material_index = slots.index(key)
    normals_of = [vals["n"][v] for v in bm.verts]
    # the underside: the rim's loop closed flat
    boundary = [e for e in bm.edges if e.is_boundary]
    under = bmesh.ops.holes_fill(bm, edges=boundary, sides=0)["faces"]
    under_key = BANDS[0][1]
    if under_key not in slots:
        slots.append(under_key)
    for f in under:
        f.material_index = slots.index(under_key)
    bm.normal_update()
    mesh = bpy.data.meshes.new("starlet")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("starlet", mesh)
    bpy.context.scene.collection.objects.link(obj)
    for key in slots:
        mesh.materials.append(m[key])
    for p in mesh.polygons:
        p.use_smooth = True
    mesh.normals_split_custom_set_from_vertices([tuple(n) for n in normals_of])
    return obj


def materials():
    m = {}
    for _, i in BANDS:
        m[i] = k.material("starlet", palette=i, **FINISH)
    for _, i in KNOB_BANDS:
        m["knob", i] = m.get(i) or k.material("starlet", palette=i, **FINISH)
    return m


def build():
    options = k.args()
    out = mk.outdir(options)
    k.reset()
    m = materials()
    obj = starlet(m)
    triangulate([obj])
    obj.name = obj.data.name = "coral_starlet"
    if "check" in options:
        sheets = options["check"]
        sheet = os.path.join(sheets, "enemy_T.png") if os.path.isdir(sheets) else sheets
        mk.compare("coral_starlet (T 89)", mk.coverage([obj], 24, 28), k.sprite_mask(sheet, 89))
    bpy.context.scene.view_settings.view_transform = "Standard"
    mk.report("coral_starlet", [obj], os.path.join(out, "coral_starlet.glb"))
    if "preview" in options:
        mk.preview(options["preview"] + "coral_starlet", [obj])


if __name__ == "__main__":
    build()
