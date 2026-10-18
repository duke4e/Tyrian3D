"""The purple armoured container of TYRIAN, BONUS, HOLES, ASSASSIN, TYRIAN X and SAVARA (sheet 2 sprite 89,
2x2: 24 x 28 pixels, not animated; ground, sky and top layers), polished (2026-10-18; it replaces misc.py's
container(), a plain purple pillow with four boxes across it). models.cfg: sprite 2 89 container yaw=0.

As the 4x upscale draws it: a purple chest (the sprite's ramp 5) whose outline is an octagon (columns 1-23
of rows 0-25: the upper corners cut off by three pixels, the lower ones by six). Its top (rows 1-13) is
level and lit: a raised frame on it, a bar across near its back (row 5) and one across its middle (row 13)
whose ends bend down over the rounded sides, joined by side bars (columns 5 and 18), panels inside it
(columns 6-8 and 15-17); two bright ribs run down its middle (columns 10-11 and 13) from the back over the
top and down the front. Its front (rows 14-25) falls away rounded towards the bottom of the screen, dark,
the ribs running on down it, two glossy knobs on it (columns 7-8 and 16 of rows 19-21). At the back edge
of the top sits a blue light (ramp 3 panes framed in pale teal, ramp 8: columns 9-15 of rows 1-3), split
by two dark bars.

The sprite is symmetric about its column 12 (x 0.5 here): the container is built about x = 0 and moved
there (AXIS_X). Origin at the sprite's centre (pixel 12, 14); +Y up the sprite, +Z towards the camera; it
stands on z = 0 (the game centres it in height in the air and lifts it onto the ground).

Replaces misc.py's container(): remove it (and its call) so that it doesn't overwrite this model.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouette
against enemy_2.png), --preview <prefix>.
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
from polish_jets import Curve  # noqa: E402
from polish_sphere_nozzle import split_along  # noqa: E402

AXIS_X = 0.5

# The body along y (front to back): its plan's half-width (the octagon, the outline two thirds covered),
# its top's height (level from the back to the middle, then falling round towards the front), the
# rounding of its top edges and its foot.
BODY_Y = (-11.67, 12.67)
BODY_HALF = Curve([(-11.67, 5.15), (-10.0, 6.85), (-8.0, 8.85), (-6.2, 10.65), (-5.4, 11.15), (8.6, 11.15),
                   (10.0, 10.65), (11.3, 9.4), (12.67, 8.05)])
BODY_TOP = Curve([(-11.67, 2.1), (-11.2, 3.3), (-10.0, 4.6), (-8.0, 6.25), (-6.0, 7.55), (-4.0, 8.5), (-2.0, 9.15),
                  (0.0, 9.55), (1.5, 9.7), (11.0, 9.75), (12.0, 9.45), (12.67, 8.6)])
EDGE_R, FOOT_Z, FOOT_R = 2.6, 0.25, 0.6

# The frame on the top: the bars across (row 5 near the back, row 13 in the middle; their ends bend
# down the screen over the sides by BAR_BEND), the side bars (columns 5 and 18) between them; their
# radius (round bars, half sunk), the panels inside (columns 6-8 and 15-17).
BAR_BACK, BAR_FRONT, BAR_BEND = 8.55, 0.55, (1.1, 3.2)
SIDE_BAR_X, BAR_R, BAR_SQUASH = 6.5, 0.62, 0.55
PANEL = (2.75, 5.85, 1.45, 7.65)  # x from, x to, y from, y to
# The ribs down the middle (columns 10-11 and 13): x, from y (behind the light) down the front, radius.
RIB_X, RIB_Y, RIB_R = 1.3, (11.0, -10.9), 0.72
# The knobs on the front (columns 7-8 and 16 of rows 19-21): middle (x, y), radius.
KNOB, KNOB_RADII = (4.5, -7.8), (1.0, 1.45, 0.85)
# The light at the back edge (columns 9-15 of rows 1-3): half-width, from y, to y, its top above the
# body's top; its pale frame; the dark bars across it (columns 10 and 14).
LIGHT_HALF, LIGHT_Y, LIGHT_RISE = 3.15, (10.35, 13.45), 0.38
LIGHT_FRAME, DIVIDER_X = 0.42, 2.0


# --- Helpers ----------------------------------------------------------------------------------------

def rounded_section(y, hw, z0, z1, r_top, r_bottom, per_corner=5):
    """The body's cross-section at y: x within hw, z from z0 to z1, the top corners rounded with r_top,
    the bottom ones with r_bottom, counter-clockwise seen from +y."""
    out = []
    corners = [(hw - r_top, z1 - r_top, 0, r_top), (-hw + r_top, z1 - r_top, 90, r_top),
               (-hw + r_bottom, z0 + r_bottom, 180, r_bottom), (hw - r_bottom, z0 + r_bottom, 270, r_bottom)]
    for cx, cz, a0, r in corners:
        for i in range(per_corner + 1):
            a = math.radians(a0 + 90 * i / per_corner)
            out.append(Vector((cx + r * math.cos(a), y, cz + r * math.sin(a))))
    return out


def section(y):
    """The body's half-width, top and top-edge rounding at y (the ends rounded off)."""
    hw, top = BODY_HALF(y), BODY_TOP(y)
    r = min(EDGE_R, (top - FOOT_Z) * 0.45, hw * 0.45)
    return hw, top, r


def top_z(x, y):
    """The height of the body's top at (x, y), over its rounded edges too."""
    hw, top, r = section(y)
    u = abs(x) - (hw - r)
    if u <= 0:
        return top
    if u >= r:
        return top - r
    return top - r + math.sqrt(r * r - u * u)


def tube(name, points, radius, mat, segments=10, squash=1.0, radii=None):
    """A round tube through 3D points, closed with rounded ends."""
    rings = []
    for i, p in enumerate(points):
        a, b = points[max(i - 1, 0)], points[min(i + 1, len(points) - 1)]
        t = (b - a).normalized()
        side = t.cross(Vector((0, 0, 1)))
        if side.length < 1e-6:
            side = Vector((1, 0, 0))
        side.normalize()
        up = side.cross(t).normalized()
        r = radii[i] if radii else radius
        angles = [2 * math.pi * j / segments for j in range(segments)]
        rings.append([p + (side * math.cos(a) + up * squash * math.sin(a)) * r for a in angles])
    t0 = (points[1] - points[0]).normalized()
    t1 = (points[-1] - points[-2]).normalized()
    r0, r1 = (radii[0], radii[-1]) if radii else (radius, radius)
    obj = k.loft(name, rings, mat, start_point=points[0] - t0 * r0 * 0.7, end_point=points[-1] + t1 * r1 * 0.7)
    return k.smooth(obj, 60)


def on_top(points, sink):
    """Plan points (x, y) lifted onto the body's top, `sink` below it."""
    return [Vector((x, y, top_z(x, y) - sink)) for x, y in points]


# --- The parts ---------------------------------------------------------------------------------------

def front_line(x):
    """Where the lit top ends and the dark front begins: along the middle bar of the frame."""
    u = min(abs(x) / 10.6, 1.0)
    return BAR_FRONT - BAR_BEND[1] * u ** 3


def body(mats):
    """The body: rounded sections along y; its top lit, its front (in front of the frame's middle bar)
    dark, the border cut in along the bar."""
    y0, y1 = BODY_Y
    ys = [y0 + (y1 - y0) * i / 48 for i in range(1, 48)]
    rings = []
    for y in ys:
        hw, top, r = section(y)
        # The ends: the sections shrink on a quarter circle within 0.6 of them.
        d = min(y - y0, y1 - y)
        f = 1.0 if d >= 0.6 else math.sqrt(max(0.0, 1 - (1 - d / 0.6) ** 2))
        shrink = 0.6 * (1 - f)
        rings.append(rounded_section(y, hw - shrink, FOOT_Z + shrink * 0.5, top - shrink, max(r - shrink * 0.5, 0.2),
                                     FOOT_R))
    obj = k.loft("body", rings, None, start_point=(0, y0, (FOOT_Z + BODY_TOP(y0)) / 2),
                 end_point=(0, y1, (FOOT_Z + BODY_TOP(y1)) / 2))
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    field = {v: v.co.y - front_line(v.co.x) for v in bm.verts}
    split_along(bm, field, 0.0)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    front = [sum(field[v] for v in f.verts) / len(f.verts) < 0 for f in bm.faces]
    bm.to_mesh(obj.data)
    bm.free()
    k.recalc_normals(obj)
    obj.data.materials.append(mats["body"])
    obj.data.materials.append(mats["front"])
    for poly, is_front in zip(obj.data.polygons, front):
        poly.material_index = 1 if is_front else 0
    return k.smooth(obj, 50)


def frame(mats):
    """The raised frame on the top: two bars across, bending down over the sides, the side bars."""
    parts = []
    for name, y, bend in (("bar_back", BAR_BACK, BAR_BEND[0]), ("bar_front", BAR_FRONT, BAR_BEND[1])):
        pts = []
        for i in range(41):
            x = -10.6 + 21.2 * i / 40
            u = min(abs(x) / 10.6, 1.0)
            pts.append((x, y - bend * u ** 3))
        parts.append(tube(name, on_top(pts, BAR_R * 0.2), BAR_R, mats["bar"], 10, BAR_SQUASH))
    for side in (-1, 1):
        pts = [(side * SIDE_BAR_X, BAR_FRONT + (BAR_BACK - BAR_FRONT) * i / 12) for i in range(13)]
        parts.append(tube(f"side_bar{side}", on_top(pts, BAR_R * 0.2), BAR_R * 0.85, mats["bar"], 10, BAR_SQUASH))
    # The panels inside the frame, a little proud of the top, their edges rounded.
    x0, x1, y0, y1 = PANEL
    for side in (-1, 1):
        cx, cy = side * (x0 + x1) / 2, (y0 + y1) / 2
        panel = k.box(f"panel{side}", (cx, cy, top_z(cx, cy) + 0.02), (x1 - x0, y1 - y0, 0.36), mats["panel"])
        k.bevel(panel, 0.14, 2)
        parts.append(panel)
    return parts


def ribs(mats):
    """The two bright ribs down the middle, from behind the light over the top and down the front."""
    parts = []
    y0, y1 = RIB_Y
    for side in (-1, 1):
        pts = [(side * RIB_X, y0 + (y1 - y0) * i / 40) for i in range(41)]
        parts.append(tube(f"rib{side}", on_top(pts, RIB_R * 0.22), RIB_R, mats["rib"], 10, 0.55))
    return parts


def knobs(mats):
    """Two glossy knobs on the front."""
    parts = []
    x, y = KNOB
    rx, ry, rz = KNOB_RADII
    for side in (-1, 1):
        cx = side * x
        z = top_z(cx, y)
        knob = k.ellipsoid(f"knob{side}", (cx, y, z - 0.35), (rx, ry, rz + 0.35), mats["knob"], 16, 8)
        parts.append(k.smooth(knob, 60))
    return parts


def light(mats):
    """The blue light at the back edge: glass in a pale frame, two dark bars across it."""
    parts = []
    y0, y1 = LIGHT_Y
    cy = (y0 + y1) / 2
    z_top = top_z(0, 11.0) + LIGHT_RISE
    size = (2 * (LIGHT_HALF + LIGHT_FRAME), y1 - y0 + 2 * LIGHT_FRAME, 2.0)
    frame = k.box("light_frame", (0.0, cy, z_top - 1.0), size, mats["light_frame"])
    k.bevel(frame, 0.3, 2)
    glass = k.box("light_glass", (0.0, cy, z_top - 0.85), (2 * LIGHT_HALF, y1 - y0, 2.0), mats["light"])
    k.bevel(glass, 0.35, 3)
    parts += [frame, glass]
    for side in (-1, 1):
        bar = k.box(f"light_bar{side}", (side * DIVIDER_X, cy, z_top + 0.05), (0.45, y1 - y0 + 0.2, 0.5),
                    mats["divider"])
        k.bevel(bar, 0.12, 2)
        parts.append(bar)
    return parts


def materials():
    pal = k.level_palette()
    return {
        "body": k.material("container_body", palette=0x56, metallic=0.35, roughness=0.32),
        "front": k.material("container_front", palette=0x53, metallic=0.45, roughness=0.22),
        "bar": k.material("container_bar", palette=0x5b, metallic=0.4, roughness=0.28),
        "panel": k.material("container_panel", palette=0x5a, metallic=0.35, roughness=0.3),
        "rib": k.material("container_rib", palette=0x5d, metallic=0.45, roughness=0.24),
        "knob": k.material("container_knob", palette=0x5d, metallic=0.55, roughness=0.14),
        "light": k.material("container_light", palette=0x3b, roughness=0.15, emission=pal[0x3b], emission_strength=0.9),
        "light_frame": k.material("container_light_frame", palette=0x88, metallic=0.3, roughness=0.25,
                                  emission=pal[0x86], emission_strength=0.25),
        "divider": k.material("container_divider", palette=0x80, metallic=0.3, roughness=0.4),
    }


def build_model():
    k.reset()
    mats = materials()
    body(mats)
    frame(mats)
    ribs(mats)
    knobs(mats)
    light(mats)
    for obj in bpy.context.scene.objects:
        if obj.type == "MESH":
            obj.data.transform(Matrix.Translation((AXIS_X, 0, 0)))


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


def build():
    options = k.args()
    outdir = options.get("outdir", os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "enemies"))
    build_model()
    used = {m.name for o in bpy.context.scene.objects if o.type == "MESH" for m in o.data.materials}
    print("== container (2 89): %d triangles, %d materials: %s" % (triangles(), len(used), ", ".join(sorted(used))))
    if "check" in options:
        sheet = options["check"]
        k.check_silhouette(os.path.join(sheet, "enemy_2.png") if os.path.isdir(sheet) else sheet, 89)
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    path = os.path.join(outdir, "container.glb")
    k.export(path)
    print("%s: %.1f KB" % (path, os.path.getsize(path) / 1024))
    if "preview" in options:
        k.preview(options["preview"] + "container")


if __name__ == "__main__":
    build()
