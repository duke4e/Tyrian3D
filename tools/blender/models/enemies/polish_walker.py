"""The blue walker of TYRIAN, HOLES, BONUS, ASSASSIN, TYRIAN X, SAVARA, GYGES and EYESPY, drawn from two sprites of sheet 2
side by side (2x2 each): its left half, 85, and its right half, 87, 24 pixels right of it (enemies 6/7 and 13/14 of
episodes 1, 3 and 5, on the ground and the top layers, 56 or so of each; GYGES and EYESPY show 87 alone once), polished
(2026-10-19; it replaces wave3_p.py's walker). models.cfg: model walker_left / walker_right ... origin; sprite 2 85
walker_left yaw=0, sprite 2 87 walker_right yaw=0. Neither sprite animates (no frame models).

The levels usually put the grabber (2 123 and 125, its own models) 16 pixels below it, on the second ground layer,
as the machine's lower half (TYRIAN, ASSASSIN; 24 pixels in BONUS): the game draws the grabber over the walker, so
its top hides the walker's eye pod there. The pod is kept low (a dome, under the grabber's neck, which stands 6.5
high) so that it hides inside the grabber in 3D too, and shows when the walker comes alone (HOLES).

The walker is built whole and cut along the sprites' edge (x = 0 here) into the two halves, each moved so that its
sprite's centre is its origin (base on the ground): drawn at their own places they meet again, and the cut pieces
keep the whole's shading across the cut (polish_redjet.py's method).

As the 4x upscales draw it (the whole 48 x 28 picture, symmetric about the edge between its columns 22 and 23):
- a grey hull at the back (columns 15-30 of rows 0-9), a steel-blue glass canopy in its top (columns 20-25 of rows
  2-7), lit cyan along its left and lower edges, and a glowing orange vent at its rear edge (row 0);
- on the shoulders two orange lamps (columns 11-13 and 32-34 of rows 2-6), brighter at the back;
- two bright blue fins: a bar from the hull's side out over each shoulder (rows 5-9) and a blade hanging from it
  down the screen to a point (columns 13-15, to row 16), on dark struts with a small orange light on their outer
  side (row 11);
- two long steel-blue legs, each a broad blade from a knuckle at the shoulder (row 5) down the screen, curving in
  to its foot (row 25), an inner ridge beside it ending at row 19;
- a dark neck under the hull (rows 10-17) with a red slit and a small blue light either side of a grey spine;
- at the spine's end a grey dome with a glowing red lens (rows 18-25).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera. The whole's x = 0
is the edge between the sprites (column 24 of the picture), y = 0 its middle (row 14's top edge): a point (column, row)
of the picture's pixel grid is (c - 24, 14 - r) (px()). The walker is built about x = AXIS (the picture's column 23's
left edge), its right half mirroring its left, but for the right leg, which the sprite draws a pixel nearer the middle
(RIGHT_LEG_SHIFT). The parts: reliefs over outlines traced from the sprite (hull, shoulders, struts, neck, the plates
beside the canopy: polish_ring_machine.relief), bars lofted along paths (legs, fins, the spine), turned parts (lamps,
the dome and its lens). The lamps, the vent, the fins, the slits and the lens glow in their own colours.

Replaces wave3_p.py's walker (AX, X(), Y(), walker_labels(), walker_whole(), walker_preview() and the
@model("walker_left") / @model("walker_right") entries): remove them so that they don't overwrite these models.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes of the
whole and of each half against enemy_2.png), --preview <prefix> (the whole's and each half's views).
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
import polish_machine_kit as mk  # noqa: E402
from polish_ring_machine import ccw, chaikin, relief, round_edge  # noqa: E402

AXIS = -1.0
PIECES = [("walker_left", 85, (-24.0, 0.0, -14.0, 14.0)), ("walker_right", 87, (0.0, 24.0, -14.0, 14.0))]


def px(c, r):
    """A point of the whole picture's pixel grid (column, row) in the whole's coordinates."""
    return (c - 24.0, 14.0 - r)


def mirror_c(c):
    """The column mirrored about the walker's axis (the edge between columns 22 and 23)."""
    return 46.0 - c


def outline(points, mirrored=False, smooth=1):
    """An outline given by its left half's points (column, row), closed by their mirror images (or the
    points as given, mirrored)."""
    if mirrored:
        pts = [px(mirror_c(c), r) for c, r in reversed(points)]
    else:
        pts = [px(c, r) for c, r in points]
    return ccw(chaikin(pts, smooth) if smooth else pts)


def symmetric(left):
    """A closed outline from its left half (column, row), from the top middle round to the bottom middle."""
    full = list(left) + [(mirror_c(c), r) for c, r in reversed(left[1:-1])]
    return ccw(chaikin([px(c, r) for c, r in full], 2))


# --- The parts' outlines (column, row of the picture) ------------------------------------------------------------
# The hull: its left half from the rear middle (row 0) round to the front middle (row 9.6).
HULL = [(23.0, 0.12), (16.4, 0.12), (15.0, 0.7), (14.7, 2.2), (14.8, 6.5), (15.6, 8.6), (17.5, 9.6), (23.0, 9.7)]
HULL_Z = (1.2, 7.4, 1.3)          # its underside, top, the rounding of its edges
HULL_CROWN = 0.5                  # the top bulging along the middle
SHOULDER = [(14.9, 1.4), (11.6, 1.2), (10.3, 2.2), (10.0, 4.6), (10.4, 8.8), (12.0, 10.0), (15.2, 9.6)]
SHOULDER_Z = (1.0, 6.2, 1.0)
CANOPY = (19.6, 26.4, 1.7, 7.4)   # columns from, to, rows from, to
PANEL = [(15.6, 0.9), (18.9, 0.9), (19.0, 8.6), (15.9, 8.4)]   # the plates beside it (left one)
PANEL_Z = (4.0, 0.45)             # their underside and edge rounding
PANEL_TOP = HULL_Z[1] + 0.85      # their flat tops
VENT = (19.2, 26.8, 0.7, 2.0)
NECK = [(23.0, 8.9), (16.2, 9.0), (16.0, 11.6), (17.6, 13.4), (18.8, 14.6), (21.0, 15.2), (23.0, 15.3)]
NECK_Z = (0.6, 4.6, 0.9)
STRUT = [(12.0, 9.0), (15.4, 9.0), (15.6, 13.0), (15.2, 16.4), (13.2, 17.2), (12.2, 15.8), (11.9, 12.0)]
STRUT_Z = (0.6, 4.4, 0.8)

# --- The round and bar parts --------------------------------------------------------------------------------------
LAMP = ((12.6, 1.8), (12.6, 6.6), 1.45)        # from, to (column, row) and radius: lying along y on the shoulder
LAMP_Z = 7.4
KNEE = ((8.6, 5.9), 1.3)
RIGHT_LEG_SHIFT = 1.0             # the sprite draws the right leg a pixel nearer the middle than the left's mirror image
# The legs (left; the right one mirrors it): the outer blade's path (column, row, height) and half-widths; the
# inner ridge's likewise.
LEG_OUTER = [(6.8, 7.2, 6.0), (6.1, 9.6, 5.6), (5.9, 13.0, 4.6), (5.9, 16.5, 3.6), (6.3, 19.6, 2.7), (7.1, 22.2, 1.9),
             (8.0, 24.0, 1.4), (8.6, 25.1, 1.2)]
LEG_OUTER_W = [1.75, 1.75, 1.7, 1.65, 1.5, 1.25, 0.95, 0.55]
LEG_INNER = [(9.2, 6.6, 6.3), (9.0, 9.5, 5.8), (8.9, 13.0, 4.9), (8.9, 16.2, 4.1), (8.9, 18.6, 3.5), (8.9, 19.7, 3.3)]
LEG_INNER_W = [1.45, 1.45, 1.4, 1.3, 0.85, 0.2]
# The fins: the bar from the hull's side over the shoulder (column, row, height) and the blade hanging from it.
FIN_BAR = [(17.6, 5.7, 7.3), (15.6, 6.2, 8.3), (13.2, 7.4, 8.4), (10.4, 8.2, 7.6)]
FIN_BAR_W = [0.95, 1.2, 1.4, 1.2]
FIN_BLADE = [(14.0, 7.6, 8.2), (14.1, 10.0, 7.2), (14.1, 12.6, 6.2), (14.0, 14.8, 5.3), (13.8, 16.6, 4.6)]
FIN_BLADE_W = [1.25, 1.2, 1.1, 0.85, 0.25]
STRUT_LIGHT = ((11.9, 11.6), 0.65)
# The neck's lights: the red slits and the blue lights (column from, to, row from, to).
SLIT = (19.6, 20.7, 10.4, 13.8)
BLUE_LIGHT = ((18.5, 11.3), 0.6)
SPINE = [(23.0, 8.6, 5.0), (23.0, 11.0, 4.9), (23.0, 14.0, 4.4), (23.0, 16.6, 3.8), (23.0, 18.2, 3.5)]
DOME = ((23.0, 21.6), 3.75, 4.6)  # middle (column, row), radius in plan, height
LENS = ((23.0, 21.0), 2.05)       # the red lens on the dome's top: middle, radius


# --- Helpers ------------------------------------------------------------------------------------------------------

def path3(points, mirrored=False, shift=0.0):
    """3D points (column, row, height), optionally mirrored (and then moved shift columns to the left)."""
    out = []
    for c, r, z in points:
        x, y = px(mirror_c(c) - shift if mirrored else c, r)
        out.append(Vector((x, y, z)))
    return out


def smooth_path(points, widths, step=0.35):
    """Catmull-Rom through the points, the widths alongside."""
    pts = [Vector(p) for p in points]
    out, ws = [], []
    for s in range(len(pts) - 1):
        p0, p1 = pts[max(s - 1, 0)], pts[s]
        p2, p3 = pts[s + 1], pts[min(s + 2, len(pts) - 1)]
        count = max(1, int(round((p2 - p1).length / step)))
        for j in range(count):
            t = j / count
            t2, t3 = t * t, t * t * t
            out.append(0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 +
                              (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
            ws.append(widths[s] + (widths[s + 1] - widths[s]) * t)
    out.append(pts[-1])
    ws.append(widths[-1])
    return out, ws


def blade(name, points, widths, height, mat, power=2.6, segments=12, flat=0.55, step=0.6):
    """A bar along a path: rounded-rectangle sections, half-width as given, half-height height * width
    share (flat), closed at both ends."""
    path, ws = smooth_path(points, widths, step)
    rings = []
    n = len(path)
    for i, p in enumerate(path):
        t = (path[min(i + 1, n - 1)] - path[max(i - 1, 0)]).normalized()
        across = t.cross(Vector((0, 0, 1)))
        if across.length < 1e-6:
            across = Vector((1, 0, 0))
        across.normalize()
        up = across.cross(t).normalized()
        if up.z < 0:
            up = -up
        w = max(ws[i], 0.03)
        h = max(height * (flat + (1 - flat) * ws[i] / max(widths)), 0.03)
        ring = []
        for j in range(segments):
            u, v = mk.superellipse_point(2 * math.pi * j / segments, power)
            ring.append(p + across * u * w + up * v * h)
        rings.append(ring)
    obj = k.loft(name, rings, mat, start_point=path[0] - (path[1] - path[0]).normalized() * 0.2,
                 end_point=path[-1] + (path[-1] - path[-2]).normalized() * 0.15)
    return k.smooth(obj, 55)


# --- The parts ----------------------------------------------------------------------------------------------------

def hull(m):
    poly = symmetric(HULL)
    bottom, top, rnd = HULL_Z
    cx = AXIS

    def height(x, y, d):
        crown = HULL_CROWN * (1 - min(1.0, ((x - cx) / 8.5) ** 2))
        return top + crown - rnd + rnd * round_edge(d, rnd)

    return relief("hull", [poly], height, m, paint=lambda x, y, d: "hull_dark" if d < 0.25 else "hull", side="hull_dark",
                  bottom=bottom, spacing=0.55, band=1.6, borders=[(lambda x, y, d: d, 0.25)])


def hull_height(x, y):
    crown = HULL_CROWN * (1 - min(1.0, ((x - AXIS) / 8.5) ** 2))
    return HULL_Z[1] + crown


def panels(m):
    """Raised plates either side of the canopy, flat-topped."""
    out = []
    for mirrored in (False, True):
        poly = outline(PANEL, mirrored)
        bottom, rnd = PANEL_Z

        def height(x, y, d):
            return PANEL_TOP - rnd + rnd * round_edge(d, rnd)
        out.append(relief("panel", [poly], height, m, paint=lambda x, y, d: "panel", side="hull_dark", bottom=bottom,
                          spacing=0.45, band=1.0))
    return out


def canopy(m):
    """The glass canopy set in the hull's top, a dark frame round it, lit cyan along its left and lower edges."""
    c0, c1, r0, r1 = CANOPY
    (x0, y1), (x1, y0) = px(c0, r0), px(c1, r1)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    hw, hh = (x1 - x0) / 2, (y1 - y0) / 2
    frame = mk.rounded_rect_ring((cx, cy), hw + 0.45, hh + 0.45, 1.1, 0.0, 64)
    glass = mk.rounded_rect_ring((cx, cy), hw, hh, 0.9, 0.0, 64)
    out = []
    # The frame: a low dark rim on the hull.
    rings = [(frame, -0.4), (frame, 0.18), ([Vector((cx + (p.x - cx) * 0.97, cy + (p.y - cy) * 0.97, 0)) for p in frame], 0.28),
             (glass, 0.28), (glass, 0.1)]
    verts, faces = [], []
    for pts, dz in rings:
        for p in pts:
            verts.append(Vector((p.x, p.y, hull_height(p.x, p.y) + dz)))
    n = len(frame)
    for r in range(len(rings) - 1):
        for j in range(n):
            a, b = r * n + j, r * n + (j + 1) % n
            faces.append((a, b, b + n, a + n))
    rim = k.mesh_object("canopy_frame", verts, faces, m["hull_dark"])
    k.recalc_normals(rim)
    out.append(k.smooth(rim, 50))
    # The glass: a low dome inside the frame, its edge band cyan where the sprite lights it.
    rows = 6
    verts, faces = [], []
    for i in range(rows + 1):
        f = 1.0 - i / rows
        for p in glass:
            q = Vector((cx + (p.x - cx) * f, cy + (p.y - cy) * f, 0))
            verts.append(Vector((q.x, q.y, hull_height(q.x, q.y) + 0.1 + 0.75 * math.sqrt(max(0.0, 1 - f * f)))))
    for i in range(rows):
        for j in range(n):
            a, b = i * n + j, i * n + (j + 1) % n
            faces.append((a, b, b + n, a + n))
    g = k.mesh_object("canopy", verts, faces, m["glass"])
    k.recalc_normals(g)
    out.append(k.smooth(g, 60))
    # The glint along its left and lower edges: a thin bar following the glass's edge, from its upper left round
    # the lower left corner to its lower right.
    inset, r = 0.55, 0.75
    pts = []
    for i in range(9):  # down the left edge
        y = cy + (hh - inset - r) * (1 - 2 * i / 8) * 0.85 + 0.0
        pts.append((cx - hw + inset, y))
    for i in range(1, 7):  # round the corner
        a = math.radians(180 + 90 * i / 6)
        pts.append((cx - hw + inset + r + r * math.cos(a), cy - hh + inset + r + r * math.sin(a)))
    for i in range(1, 7):  # along the bottom
        pts.append((cx - hw + inset + r + (2 * hw - 2 * inset - 2 * r) * 0.8 * i / 6, cy - hh + inset))
    path = [Vector((x, y, hull_height(x, y) + 0.1 + 0.75 * math.sqrt(max(0.0, 1 - (max(abs(x - cx) / hw, abs(y - cy) / hh)) ** 2)) + 0.05))
            for x, y in pts]
    out.append(k.smooth(mk.tube("canopy_glint", path, 0.32, m["glare"], 8), 60))
    return out


def vent(m):
    """The orange vent at the hull's rear edge: glowing slats in a dark slot."""
    c0, c1, r0, r1 = VENT
    (x0, y1), (x1, y0) = px(c0, r0), px(c1, r1)
    zt = hull_height((x0 + x1) / 2, y0)
    slot = mk.box("vent_slot", x0, x1, y0, y1, zt - 1.0, zt + 0.3, m["hull_dark"])
    mk.bevel(slot, 0.2, 2, 35.0)
    slats = []
    count = 7
    for i in range(count):
        x = x0 + 0.6 + (x1 - x0 - 1.2) * i / (count - 1)
        s_ = mk.box("vent_slat%d" % i, x - 0.3, x + 0.3, y0 + 0.2, y1 - 0.2, zt - 0.2, zt + 0.5, m["lamp"])
        mk.bevel(s_, 0.12, 1, 35.0)
        slats.append(s_)
    return [slot] + slats


def shoulders(m):
    out = []
    for mirrored in (False, True):
        bottom, top, rnd = SHOULDER_Z
        s = relief("shoulder", [outline(SHOULDER, mirrored)], lambda x, y, d: top - rnd + rnd * round_edge(d, rnd), m,
                   paint=lambda x, y, d: "hull", side="hull_dark", bottom=bottom, spacing=0.45, band=1.4)
        out.append(s)
        bottom, top, rnd = STRUT_Z
        out.append(relief("strut", [outline(STRUT, mirrored)], lambda x, y, d: top - rnd + rnd * round_edge(d, rnd), m,
                          paint=lambda x, y, d: "dark", side="dark", bottom=bottom, spacing=0.45, band=1.2))
    return out


def neck(m):
    bottom, top, rnd = NECK_Z
    obj = relief("neck", [symmetric(NECK)], lambda x, y, d: top - rnd + rnd * round_edge(d, rnd), m,
                 paint=lambda x, y, d: "dark", side="dark", bottom=bottom, spacing=0.45, band=1.3)
    # The grey spine from under the hull to the dome.
    spine = blade("spine", path3(SPINE), [1.2, 1.15, 1.05, 1.0, 0.95], 0.75, m["hull"], power=2.4)
    lights = []
    for mirrored in (False, True):
        c0, c1, r0, r1 = SLIT
        if mirrored:
            c0, c1 = mirror_c(c1), mirror_c(c0)
        (x0, y1), (x1, y0) = px(c0, r0), px(c1, r1)
        slit = mk.box("slit", x0, x1, y0, y1, NECK_Z[1] - 0.8, NECK_Z[1] + 0.12, m["red"])
        mk.bevel(slit, 0.25, 2, 35.0)
        mk.shade(slit, 40.0)
        lights.append(slit)
        (c, r), rad = BLUE_LIGHT
        x, y = px(mirror_c(c) if mirrored else c, r)
        lights.append(mk.ball("blue_light", (x, y, NECK_Z[1] - 0.1), (rad, rad * 1.3, 0.45), m["leg_light"], 14, 7))
    return [obj, spine] + lights


def lamps(m):
    out = []
    for mirrored in (False, True):
        (c0, r0), (c1, r1), rad = LAMP
        if mirrored:
            c0, c1 = mirror_c(c0), mirror_c(c1)
        (x0, y0), (x1, y1) = px(c0, r0), px(c1, r1)
        prof = []
        length = y0 - y1
        for i in range(17):
            t = i / 16
            a = (math.pi / 2) * min(1.0, min(t, 1 - t) / 0.22)
            prof.append((y1 + length * t, max(rad * math.sin(a) ** 0.6, 0.02)))
        lamp = k.lathe("lamp", prof, m["lamp"], 16, axis_x=x0, axis_z=LAMP_Z)
        lamp.data.materials.append(m["lamp_red"])
        for poly in lamp.data.polygons:
            if poly.center.y < y1 + length * 0.45:
                poly.material_index = 1
        out.append(k.smooth(lamp, 50))
        collar = k.lathe("lamp_collar", [(y1 + length * 0.36, rad + 0.05), (y1 + length * 0.4, rad + 0.25),
                                          (y1 + length * 0.5, rad + 0.25), (y1 + length * 0.54, rad + 0.05)],
                         m["dark"], 20, axis_x=x0, axis_z=LAMP_Z)
        out.append(k.smooth(collar, 40))
    return out


def fins(m):
    out = []
    for mirrored in (False, True):
        out.append(blade("fin_bar", path3(FIN_BAR, mirrored), FIN_BAR_W, 0.7, m["fin"], power=3.0))
        out.append(blade("fin_blade", path3(FIN_BLADE, mirrored), FIN_BLADE_W, 0.55, m["fin"], power=3.0))
        (c, r), rad = STRUT_LIGHT
        x, y = px(mirror_c(c) if mirrored else c, r)
        out.append(mk.ball("strut_light", (x, y, STRUT_Z[1] - 0.6), (rad, rad, rad), m["lamp"], 12, 6))
    for obj in out:
        if obj.data.materials and obj.data.materials[0] == m["fin"]:
            mk.paint(obj, lambda c, n: m["fin_light"] if n.z > 0.75 else None)
    return out


def legs(m):
    out = []
    for mirrored in (False, True):
        shift = RIGHT_LEG_SHIFT if mirrored else 0.0
        outer = blade("leg_outer", path3(LEG_OUTER, mirrored, shift), LEG_OUTER_W, 1.0, m["leg"], power=2.4, segments=14)
        inner = blade("leg_inner", path3(LEG_INNER, mirrored, shift), LEG_INNER_W, 0.85, m["leg"], power=2.4, segments=12)
        for obj in (outer, inner):
            mk.paint(obj, lambda c, n, mirrored=mirrored: m["leg_light"] if n.z > 0.55 and (n.x > 0.15) != mirrored
                     else m["leg_dark"] if n.z < 0.2 else None)
        out += [outer, inner]
        (c, r), rad = KNEE
        x, y = px(mirror_c(c) - shift if mirrored else c, r)
        out.append(mk.ball("knee", (x, y, 6.4), (rad, rad * 1.1, rad * 0.9), m["leg_light"], 16, 8))
    return out


def dome(m):
    (c, r), rad, height = DOME
    x, y = px(c, r)
    d = mk.dome("dome", (x, y), (rad, rad, height), 0.0, m["hull"], 32, 9)
    mk.paint(d, lambda cc, n: m["hull_dark"] if n.z < 0.25 else None)
    (lc, lr), lrad = LENS
    lx, ly = px(lc, lr)
    # The lens: a red glowing cap on the dome's top, its hot spot at the upper left.
    lens = mk.ball("lens", (lx, ly, height - 0.55), (lrad, lrad, 0.95), m["red"], 22, 10)
    hot = mk.ball("lens_hot", (lx - 0.65, ly + 0.6, height + 0.12), (0.7, 0.6, 0.22), m["red_hot"], 14, 7)
    rim = k.lathe("lens_rim", [(-0.35, lrad + 0.05), (-0.2, lrad + 0.35), (0.2, lrad + 0.35), (0.35, lrad + 0.05)],
                  m["dark"], 32)
    rim.data.transform(Matrix.Translation((lx, ly, height - 0.6)) @ Matrix.Rotation(math.radians(90), 4, "X"))
    k.smooth(rim, 40)
    return [d, lens, hot, rim]


def materials():
    pal = k.level_palette()
    steel = dict(metallic=0.55, roughness=0.3)
    return {
        "hull": k.material("walker_hull", palette=0x08, **steel),
        "panel": k.material("walker_panel", palette=0x0a, **steel),
        "hull_dark": k.material("walker_hull_dark", palette=0x04, **steel),
        "dark": k.material("walker_dark", palette=0x03, metallic=0.45, roughness=0.4),
        "glass": k.material("walker_glass", palette=0x3a, metallic=0.3, roughness=0.08),
        "glare": k.material("walker_glare", palette=0x88, metallic=0.2, roughness=0.08, emission=pal[0x85],
                            emission_strength=0.4),
        "lamp": k.material("walker_lamp", palette=0x79, metallic=0.05, roughness=0.3, emission=pal[0x79],
                           emission_strength=1.3),
        "lamp_red": k.material("walker_lamp_red", palette=0x75, metallic=0.05, roughness=0.3, emission=pal[0x75],
                               emission_strength=1.0),
        "fin": k.material("walker_fin", palette=0x9b, metallic=0.3, roughness=0.22, emission=pal[0x9a],
                          emission_strength=0.45),
        "fin_light": k.material("walker_fin_light", palette=0x9d, metallic=0.3, roughness=0.2, emission=pal[0x9c],
                                emission_strength=0.5),
        "leg": k.material("walker_leg", palette=0x38, metallic=0.5, roughness=0.3),
        "leg_light": k.material("walker_leg_light", palette=0x3b, metallic=0.5, roughness=0.26),
        "leg_dark": k.material("walker_leg_dark", palette=0x65, metallic=0.45, roughness=0.36),
        "red": k.material("walker_red", palette=0x76, metallic=0.1, roughness=0.2, emission=pal[0x76],
                          emission_strength=1.1),
        "red_hot": k.material("walker_red_hot", palette=0x7b, metallic=0.0, roughness=0.15, emission=pal[0x7b],
                              emission_strength=1.6),
    }


# --- Build --------------------------------------------------------------------------------------------------------

def whole_mask(sheet):
    left, right = k.sprite_mask(sheet, 85), k.sprite_mask(sheet, 87)
    return [a + b for a, b in zip(left, right)]


def build_whole():
    k.reset()
    m = materials()
    hull(m)
    panels(m)
    canopy(m)
    vent(m)
    shoulders(m)
    neck(m)
    lamps(m)
    fins(m)
    legs(m)
    dome(m)
    whole = mk.meshes()
    for obj in whole:
        mk.apply(obj)
    return whole, m


def build():
    options = k.args()
    outdir = mk.outdir(options)
    sheets = options.get("check")
    sheet = (os.path.join(sheets, "enemy_2.png") if os.path.isdir(sheets) else sheets) if sheets else None
    whole, m = build_whole()
    low, high = mk.bounds(whole)
    print("== whole walker (2 85 | 87): %d triangles, %d objects, %d materials, x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f" % (
        mk.triangles(whole), len(whole), len(mk.materials_of(whole)), low.x, high.x, low.y, high.y, low.z, high.z))
    if sheet:
        mk.compare("whole (2 85 | 87)", mk.coverage(whole, 48, 28), whole_mask(sheet))
    if "preview" in options:
        mk.preview(options["preview"] + "walker_whole", whole, size=(48, 28), scale=10, distance=1.6)
    for name, sprite, box in PIECES:
        pieces = [p for p in (mk.cut(src, box, m["dark"]) for src in whole) if p is not None]
        mk.transform(pieces, Matrix.Translation((-(box[0] + box[1]) / 2, 0.0, 0.0)))
        for o in whole:
            o.hide_render = True
        if sheet:
            mk.compare("%s (2 %d)" % (name, sprite), mk.coverage(pieces, 24, 28), k.sprite_mask(sheet, sprite))
        bpy.context.view_layer.update()
        mk.report(name, pieces, os.path.join(outdir, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, pieces)
        for o in pieces:
            bpy.data.objects.remove(o)
        for o in whole:
            o.hide_render = False


if __name__ == "__main__":
    build()
