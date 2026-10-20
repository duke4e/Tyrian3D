"""UNDERDELI's red-clawed machine in a brick wall: sheet ^ (x5e in models.cfg) sprites 157 (the left), 159 (the middle)
and 161 (the right), 2x2 each: one 72 x 28 picture; enemies 37, 38/45/47 and 39 (one frame each), ground enemies the
level puts side by side on the wall's tiles, 157 at x, 159 at x + 24, 161 at x + 48, at the same y (UNDERDELI's events
384-1280 and on). Polished 2026-10-20; it replaces wave3_i.py's crab_whole() (ellipsoids and raised pixel regions).
models.cfg: model brick_crab_left / _mid / _right ... origin; sprite x5e 157 brick_crab_left yaw=0 height=-4 and so
on (models drawn at their origin stand at the ground enemies' layer, 4 pixels over the terrain: height=-4 sets them on
the wall; the same for the three).

As the sprites and their 4x upscales draw it (columns and rows of the 72 x 28 picture; it is symmetric about the middle
of column 36): in the middle a grey dome (columns 28-45 of rows 2-14), lit at its top, with a red trident on it (three
prongs from row 3, joined at row 7, a stem down to row 11) and a grey chin under its front (columns 31-41 of rows
11-16); either side of it a red ball (columns 23-31 of rows 6-13) and beyond that a grey ball (columns 14-22 of rows
7-16); at the ends big red hooks (columns 5-14 of rows 7-22) curling down and in to their points; under the red balls
grey joints (rows 14-17) and two small red pincers curving in towards each other under the chin (columns 28-34 and
38-44 of rows 18-22). The brick wall round it (rows 0-1 and 23-27 and everything between the parts) is the map's: left
out.

Built whole and cut along the sprites' edges (x = -12 and 12; polish_arch.py's cut(): the pieces keep the whole's
shading across the cuts), each piece moved so its sprite's centre is its origin. The dome is a superellipsoid, the
balls spheres, the hooks and pincers tapering tubes along curved paths; red and grey in bands of the light
(polish_orb_red.band_split), lighter on top so the balls don't read black under the slanted camera; the trident's
strips lie on the dome. The left half is built and mirrored; the dome, its trident and the chin are built whole.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the wall (z = 0); the whole's
origin is the middle of the picture (the middle of 159): column c's left edge is x = c - 36, row r's top edge
y = 14 - r.

Replaces wave3_i.py's crab: remove CRAB, crab_whole(), the w.WHOLES["crab"] entry and the loop registering
brick_crab_left ... _right, the brick_crab line of its docstring (and "crab," in its --whole usage line), and
wave3_i_art.py's CRAB (only crab_whole() reads it), so that they don't overwrite these models.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes of the
whole and of each piece against the crab's own pixels, the wall left out, written below), --preview <prefix>,
--whole <file.glb> (the uncut crab as well, for looking at).
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_arch import cut  # noqa: E402  (polish_machine_kit.cut without its material indices shifted twice)
from polish_orb_red import band_split  # noqa: E402

AXIS_X = 0.5                    # symmetric about the middle of the picture's column 36
MID_C = 36.5
PIECES = [("brick_crab_left", 157, (-36.0, -12.0, -14.0, 14.0)), ("brick_crab_mid", 159, (-12.0, 12.0, -14.0, 14.0)),
          ("brick_crab_right", 161, (12.0, 36.0, -14.0, 14.0))]


def XE(c):
    return c - 36.0


def YE(r):
    return 14.0 - r


def P(c, r):
    return (XE(c), YE(r))


# The crab's own pixels (rows: spans of columns): the brick wall round it left out.
OWN = {2: [(29, 40)], 3: [(29, 43)], 4: [(28, 44)], 5: [(27, 45)], 6: [(25, 48)], 7: [(9, 12), (23, 49), (60, 63)],
       8: [(7, 19), (23, 49), (53, 65)], 9: [(7, 21), (23, 49), (51, 65)], 10: [(6, 66)], 11: [(5, 67)],
       12: [(5, 67)], 13: [(5, 67)], 14: [(5, 30), (33, 39), (43, 67)],
       15: [(5, 12), (17, 21), (23, 29), (33, 39), (43, 49), (51, 56), (60, 67)],
       16: [(5, 10), (22, 29), (34, 38), (43, 50), (61, 67)], 17: [(5, 9), (21, 31), (43, 51), (63, 67)],
       18: [(5, 8), (22, 29), (42, 51), (63, 67)], 19: [(6, 9), (28, 29), (42, 45), (63, 67)],
       20: [(6, 9), (27, 30), (41, 45), (63, 66)], 21: [(7, 10), (28, 32), (40, 45), (62, 65)],
       22: [(9, 10), (29, 34), (38, 44), (61, 63)]}

DOME = (MID_C, 8.4, 8.5, 6.3, 7.0, 2.4)   # centre (column, row), half-width, half-length, height, superellipse power
TRIDENT = [[(33.0, 4.0), (35.4, 6.4), (36.5, 7.4)], [(36.5, 3.2), (36.5, 7.4)], [(40.0, 4.0), (37.6, 6.4), (36.5, 7.4)],
           [(36.5, 7.4), (36.5, 11.4)]]   # its strips' paths (columns, rows); the left and right prongs are mirrors
TRIDENT_W = (0.82, 0.38)        # its strips' half-width and how far they stand
CHIN = [(31.6, 11.6), (MID_C, 11.6), (MID_C, 16.8), (33.4, 16.4), (31.6, 14.6)]  # the left half; mirrored
CHIN_Z = 3.8
RED_BALL = (27.3, 9.6, 2.4, 4.15)   # column, row, centre height, radius (the left one)
GREY_BALL = (18.3, 11.8, 2.0, 4.0)
JOINT = (25.1, 15.8, 1.5, 2.6)
JOINT_ARM = [(25.4, 15.6, 1.7, 1.3), (27.0, 17.0, 1.8, 1.2), (28.2, 17.6, 1.9, 1.15)]
# The hook (the left one): its path (column, row, height, radius) from the grey ball out and down to its point.
HOOK = [(14.8, 10.8, 2.9, 2.8), (12.0, 10.6, 3.3, 3.7), (9.8, 12.0, 3.4, 3.9), (8.4, 14.4, 3.0, 3.3),
        (7.8, 16.8, 2.4, 2.5), (7.8, 19.0, 1.8, 1.85), (8.4, 20.9, 1.3, 1.35), (9.6, 22.5, 0.8, 0.45)]
# The pincer (the left one) under the chin.
PINCER = [(27.9, 16.9, 2.4, 1.55), (28.7, 19.2, 2.3, 1.7), (30.1, 21.0, 2.0, 1.5), (32.3, 22.1, 1.5, 1.05),
          (34.6, 22.7, 0.9, 0.4)]

SUN = Vector((-0.45, 0.45, 0.77)).normalized()


def materials():
    def mat(name, index, metallic=0.5, roughness=0.36):
        return k.material(name, palette=index, metallic=metallic, roughness=roughness)
    return {
        "dark": mat("crab_dark", 0x03, 0.4, 0.5),
        "shade": mat("crab_shade", 0x05, 0.5, 0.42),
        "steel": mat("crab_steel", 0x07, 0.55, 0.36),
        "lit": mat("crab_lit", 0x09, 0.55, 0.32),
        "light": mat("crab_light", 0x0b, 0.55, 0.28),
        "red_dark": mat("crab_red_dark", 0x43, 0.35, 0.34),
        "red": mat("crab_red", 0x46, 0.35, 0.3),
        "red_lit": mat("crab_red_lit", 0x48, 0.3, 0.27),
        "red_light": mat("crab_red_light", 0x4a, 0.3, 0.24),
        "red_hi": mat("crab_red_hi", 0x4c, 0.25, 0.2),
    }


def grey_bands(obj, m, levels=(-0.1, 0.35, 0.7, 0.9)):
    values = [v.normal.dot(SUN) for v in obj.data.vertices]
    band_split(obj, values, [(-9.0, m["dark"]), (levels[0], m["shade"]), (levels[1], m["steel"]),
                             (levels[2], m["lit"]), (levels[3], m["light"])])
    k.smooth(obj, 60)


def red_bands(obj, m, levels=(-0.1, 0.35, 0.72, 0.92)):
    values = [v.normal.dot(SUN) for v in obj.data.vertices]
    band_split(obj, values, [(-9.0, m["red_dark"]), (levels[0], m["red"]), (levels[1], m["red_lit"]),
                             (levels[2], m["red_light"]), (levels[3], m["red_hi"])])
    k.smooth(obj, 60)


def superdome(name, centre, hw, hl, h, power, mat, segments=32, steps=10):
    """Half a superellipsoid on z = 0: plan radii hw (x) and hl (y), height h; power > 2 makes it fuller."""
    cx, cy = centre
    rings = []
    for i in range(steps + 1):
        t = (math.pi / 2) * i / steps
        rr = math.cos(t) ** (2 / power)
        z = h * math.sin(t) ** (2 / power)
        if rr < 1e-3:
            break
        rings.append([Vector((cx + hw * rr * math.cos(2 * math.pi * j / segments),
                              cy + hl * rr * math.sin(2 * math.pi * j / segments), z)) for j in range(segments)])
    return k.loft(name, rings, mat, start_point=(cx, cy, 0.0), end_point=(cx, cy, h))


def dome_height(x, y):
    c, r, hw, hl, h, power = DOME
    cx, cy = P(c, r)
    q = abs((x - cx) / hw) ** power + abs((y - cy) / hl) ** power
    if q >= 1:
        return 0.0
    # On the superellipsoid: (rr)^p + ... with z = h * (1 - q)^(1/p)
    return h * (1 - q) ** (1 / power)


def strip_on_dome(name, path, half_w, up, mat, samples=8):
    """A strip lying on the dome along a path (columns, rows): a loft of flat sections hugging the surface."""
    pts = []
    for (c0, r0), (c1, r1) in zip(path, path[1:]):
        for i in range(samples):
            t = i / samples
            pts.append(P(c0 + (c1 - c0) * t, r0 + (r1 - r0) * t))
    pts.append(P(*path[-1]))
    rings = []
    for i, (x, y) in enumerate(pts):
        a, b = Vector(pts[max(i - 1, 0)]), Vector(pts[min(i + 1, len(pts) - 1)])
        d = (b - a).normalized()
        side = Vector((-d.y, d.x))
        ring = []
        for sx, sz in ((-1, -0.4), (-1, 0.75), (-0.75, 1.0), (0.75, 1.0), (1, 0.75), (1, -0.4)):
            px, py = x + side.x * half_w * sx, y + side.y * half_w * sx
            ring.append(Vector((px, py, dome_height(px, py) + up * sz)))
        rings.append(ring)
    obj = k.loft(name, rings, mat)
    return k.smooth(obj, 50)


def ball(name, centre, radius, mat, segments=22, rings=11):
    obj = k.ellipsoid(name, centre, (radius, radius, radius), mat, segments, rings)
    return obj


def path_tube(name, path, mat, segments=18):
    pts = [(XE(c), YE(r), z, rad) for c, r, z, rad in path]
    return mk.smooth_tube(name, pts, mat, segments, iterations=2)


# --- The parts ---------------------------------------------------------------------------------------------------

def left_half(m):
    """The red ball, the grey ball, the hook, the joint and the pincer (the left ones)."""
    c, r, z, rad = RED_BALL
    rb = ball("red_ball", (XE(c), YE(r), z), rad, m["red"])
    red_bands(rb, m)
    c, r, z, rad = GREY_BALL
    gb = ball("grey_ball", (XE(c), YE(r), z), rad, m["steel"])
    grey_bands(gb, m)
    hook = path_tube("hook", HOOK, m["red"], 16)
    red_bands(hook, m)
    c, r, z, rad = JOINT
    jb = ball("joint", (XE(c), YE(r), z), rad, m["steel"], 16, 8)
    grey_bands(jb, m)
    arm = path_tube("joint_arm", JOINT_ARM, m["steel"], 10)
    grey_bands(arm, m)
    pincer = path_tube("pincer", PINCER, m["red"], 12)
    red_bands(pincer, m)


def middle(m):
    """The dome, the trident on it, the chin under its front."""
    c, r, hw, hl, h, power = DOME
    dome = superdome("dome", P(c, r), hw, hl, h, power, m["steel"])
    k.smooth(dome, 60)
    # Lit at its top, its lower front (under the trident's stem, rows 11-14) in shadow, as the sprite draws it.
    y0, y1 = YE(10.4), YE(12.6)
    values = [v.normal.dot(SUN) - 0.75 * min(1.0, max(0.0, (y0 - v.co.y) / (y0 - y1))) for v in dome.data.vertices]
    band_split(dome, values, [(-9.0, m["dark"]), (0.0, m["shade"]), (0.4, m["steel"]), (0.74, m["lit"]),
                              (0.92, m["light"])])
    k.smooth(dome, 60)
    half_w, up = TRIDENT_W
    for i, path in enumerate(TRIDENT):
        s = strip_on_dome(f"trident{i}", path, half_w, up, m["red_lit"])
        red_bands(s, m, levels=(-0.2, 0.3, 0.7, 0.9))
    hub_x, hub_y = P(MID_C, 7.4)
    hub = mk.dome("trident_hub", (hub_x, hub_y), (1.05, 1.05, 0.5), dome_height(hub_x, hub_y) - 0.15, m["red_lit"],
                  12, 3)
    red_bands(hub, m)
    left = [P(cc, rr) for cc, rr in CHIN]
    right = [(2 * AXIS_X - x, y) for x, y in reversed(left[1:-1])]
    outline = left + right
    area = sum(outline[i][0] * outline[(i + 1) % len(outline)][1] - outline[(i + 1) % len(outline)][0] * outline[i][1]
               for i in range(len(outline)))
    if area < 0:
        outline.reverse()
    chin = mk.wedge("chin", mk.chaikin(outline, 1), 0.0, lambda x, y: CHIN_Z - 0.18 * max(0.0, YE(12.0) - y),
                    m["steel"])
    mk.bevel(chin, 0.9, 3, 30)
    mk.shade(chin, 30)
    groove = mk.box("chin_groove_cut", AXIS_X - 0.25, AXIS_X + 0.25, YE(17.5), YE(12.6), CHIN_Z - 0.7, CHIN_Z + 2.0)
    mk.boolean(chin, groove, "DIFFERENCE")
    mk.cleanup(chin)
    mk.shade(chin, 30)
    mk.paint(chin, lambda cc, n: m["lit"] if n.dot(SUN) > 0.75 else m["steel"] if n.z > 0.5 else
             m["dark"] if n.z < 0.1 else m["shade"])


def mirror_half(objects):
    flip = Matrix.Translation((2 * AXIS_X, 0, 0)) @ Matrix.Scale(-1, 4, (1, 0, 0))
    for obj in objects:
        copy = obj.copy()
        copy.data = obj.data.copy()
        copy.name = obj.name + "_r"
        bpy.context.scene.collection.objects.link(copy)
        copy.data.transform(flip)
        copy.data.flip_normals()
        copy.data.update()


def clip_below(obj, z=0.0):
    if min(v.co.z for v in obj.data.vertices) >= z - 1e-4:
        return
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    res = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-5, plane_co=(0, 0, z),
                                 plane_no=(0, 0, -1), clear_outer=True)
    edges = [e for e in res["geom_cut"] if isinstance(e, bmesh.types.BMEdge) and e.is_valid and e.is_boundary]
    if edges:
        bmesh.ops.holes_fill(bm, edges=edges, sides=0)
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()


def build_whole():
    m = materials()
    left_half(m)
    half = mk.meshes()
    for obj in half:
        mk.apply(obj)
    mirror_half(half)
    middle(m)
    whole = mk.meshes()
    for obj in whole:
        mk.apply(obj)
        clip_below(obj)
    bpy.context.view_layer.update()
    return [o for o in whole if len(o.data.polygons) > 0], m


def own_mask(c0=0, w=72):
    mask = [[False] * 72 for _ in range(28)]
    for r, spans in OWN.items():
        for a, b in spans:
            for c in range(a, b + 1):
                mask[r][c] = True
    return [row[c0:c0 + w] for row in mask]


def build():
    k.reset()
    options = k.args()
    out = mk.outdir(options)
    whole, m = build_whole()
    print("whole brick crab: %d triangles, %d objects" % (mk.triangles(whole), len(whole)))
    if "check" in options:
        mk.compare("whole (x5e 157 + 159 + 161, its own pixels)", mk.coverage(whole, 72, 28), own_mask())
    bpy.context.scene.view_settings.view_transform = "Standard"
    if "preview" in options:
        mk.preview(options["preview"] + "brick_crab_whole", whole, size=(72, 28), scale=10, distance=2.0)
    if "whole" in options:
        mk.export(whole, options["whole"])
    for name, sprite, box in PIECES:
        pieces = [p for p in (cut(src, box, m["dark"]) for src in whole) if p is not None]
        mk.transform(pieces, Matrix.Translation((-(box[0] + box[1]) / 2, 0, 0)))
        bpy.context.view_layer.update()
        for src in whole:
            src.hide_render = True
        if "check" in options:
            c0 = int(box[0] + 36)
            mk.compare("%s (x5e %d, its own pixels)" % (name, sprite), mk.coverage(pieces, 24, 28), own_mask(c0, 24))
        mk.report(name, pieces, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, pieces)
        for obj in pieces:
            bpy.data.objects.remove(obj)
        for src in whole:
            src.hide_render = False


if __name__ == "__main__":
    build()
