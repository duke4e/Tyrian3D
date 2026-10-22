"""TYRIAN's and TYRIAN X's red works in the rocks (sheet 2: 15, 17 above 53, 55, 2x2 each: one 48 x 56 picture; the top
layer; one frame each), polished (2026-10-23, round 38, the quality redo: rebuilt from solids; round 37's version was
one heightfield of the whole picture painted from the sprite's pixels, which read as flat pixel blocks; that one
replaced wave3_p_ground.py's works_whole(), a steel slab with red rounded boxes, pipes and spheres on grey boulders).

Where the levels put them: TYRIAN (both of its level files) and TYRIAN X at t3200, event 7 (top enemies 42-45 of
episodes 1 and 3, armour 12, link 31): 42 (2 15) at (48, y - 27), 43 (2 17) at (72, y - 27), 44 (2 53) at (48, y + 1),
45 (2 55) at (72, y + 1): the sheet's layout, on background 3's tile grid (columns 2 and 3). They lie exactly over
background 3's tiles 161 162 above 171 172 (map rows 354-355, columns 2-3), which draw the same works wrecked
(blackened, broken, rubble at the lower right) on a cobbled outcrop: the cobbles round the works in the sprites are the
map's own pixels (identical to the tiles' outside the works), so the models leave them out and stand on background 3's
plane (height=-6, as TYRIAN's purple pads and hooded turret do: the top layer is drawn 6 pixels above background 3), and
shooting a piece away leaves the wreck the map draws. (The sprites' darker cobbles at the lower right, columns 38-47 of
rows 28-50, differ from the map's rubble there; they are ground too: left to the map.) None of the four is another
sprite's pixels mirrored, turned or in other ramps; no other enemy, launched ones included, shows them; no episode 6
level brings them (its levels take no TYRIAN waves with the top enemies 42-45).

As the sprites and their 4x upscale draw it (columns and rows of the 48 x 56 picture; lit from the upper left): a dark
steel deck (0x01-0x03) over columns 3-38 of rows 3-50, crowded with machinery: at the top a grey drum lying across
(columns 5-13 of rows 1-6, red caps at its ends) and a dark panel striped with a tan rail (columns 14-30 of rows 3-6),
a grey knob at the top right (columns 30-34 of rows 1-6); a big red block bent down at its left (columns 3-16 of rows
7-16, its top lit pink), a grey block beside it, a red block at the upper right (columns 22-28 of rows 7-15) and a tan
rod right of it (columns 31-32 of rows 6-15); two dark grille boxes (columns 13-19 of rows 11-15 and 17-21) glowing
yellow to orange and red round a white-hot pixel (columns 14-18 of rows 12-14 and 18-20); a red pipe from left of
them along rows 16-17 to column 34, down the right side to row 33 and back along row 28 to column 21, framing a dark
box (columns 20-34 of rows 18-28) with a grey lid, a dark tan panel sunk in it and grey slats at its right; at the
left a tan box (columns 0-10 of rows 15-27) with a red button in a dark socket, a brass strip down its left side and a
brass rail along its foot; under the grilles a grey block and a red block (columns 10-18 of rows 17-29); lower down a
small red block (columns 3-6 of rows 29-34), a tall tan block (columns 6-12 of rows 33-47) beside a grey block and a
red wedge (columns 12-19 of rows 33-47), grey slats and a red bar at the lower right (columns 29-33 of rows 29-48)
with the pipe running into its top, a slot down it and a tan valve, a tan rod at the deck's right edge (columns 36-37
of rows 22-34).

Built as such a machine, each part its own solid standing on the deck (the deck a bevelled plate over the works' own
outline; the blocks bevelled boxes and prisms, the tan block and the red wedge sloping to the front; the drum, the
rods and the rail lathed lying down, the pipe a tube along its path with rounded bends, the knob and the valves
lathed upright, the button a glossy dome in a socket; the tan box, the dark box and the red bar reliefs with their
socket, panel and slot sunk into them; the grilles glowing panels, hottest in the middle, crossed by dark bars, in
their boxes): heights from the deck's top at 1.2 to the big red block's 5.4 (the player's plane is 12 above
background 3). Materials by part from the sprites' own ramps, the shading the geometry's: the deck 0x03, slots and
sockets 0x01, steel 0x04 / 0x06 / 0x08, the red paint 0x48, the button 0x4a, tan 0xa7 / 0xa4 (the sunk panel), the
rods 0xa9, brass 0x18; the grilles glow in their own colours (0x77 0.35, 0x7a 0.45, 0x7d 0.55), the button a little
(0.12).

Built in the picture's plane (x, y as the sprites draw them, z up) and cut there along the sprites' edges
(polish_coral_manta.cut: each piece what its sprite draws; the cuts capped in the part's own material, seen only when
a neighbouring piece is shot away), then sheared along the game camera's line of sight (y - z tan 20, the normals with
it: polish_fleet_walker.shear_to_camera), so that the camera sees every point where the sprites draw it; each piece
moved so that its sprite's middle is its origin, triangulated (polish_k_pod.triangulate) and joined. No booleans, no
random numbers: the same output every run.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera (z 0: background 3's
plane, with height=-6). The whole's origin is its picture's middle (a pixel corner (column c, row r) is x = c - 24,
y = 28 - r); each piece moved so its sprite's middle is its origin (models.cfg origin): 15 (-12, 14), 17 (12, 14),
53 (-12, -14), 55 (12, -14).

models.cfg: the lines stay as they are (model red_works_tl ... origin; sprite 2 15 red_works_tl yaw=0 height=-6
glow=9:0.25:123:4.5:2.5, the grilles' middle 4.5 right of 15's centre and 2.5 down; sprite 2 17, 53, 55 yaw=0
height=-6). The old code (wave3_p_ground.py, wave3_p_art.py's WORKS) went with round 37.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each piece's outline against
its sprite's own pixels, the works' (the cobbles left out)), --preview <prefix>, --only <name,...>.
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
from polish_k_pod import triangulate  # noqa: E402
from polish_deli_boss import join, drop_unused  # noqa: E402
from polish_coral_manta import cut  # noqa: E402
from polish_fleet_walker import shear_to_camera, merge_materials  # noqa: E402
from polish_ring_machine import relief, Region, round_edge, resample  # noqa: E402

# The works' own pixels: inside this outline (pixel corners: column, row); the cobbles round it are background 3's.
OUTLINE = [(4.5, 1.0), (14.0, 1.0), (14.0, 2.5), (30.0, 2.5), (30.0, 0.5), (35.0, 0.5), (35.0, 3.5), (38.5, 3.5),
           (38.5, 50.0), (5.0, 50.0), (5.0, 35.0), (0.5, 35.0), (0.5, 29.5), (0.0, 29.5), (0.0, 15.5), (3.0, 15.5),
           (3.0, 7.0), (4.5, 7.0)]
DECK_TOP, DECK_BEVEL = 1.2, 0.45
PIECES = [("red_works_tl", 15, (-60.0, 0.0, 0.0, 60.0), (-12.0, 14.0), (0, 0)),
          ("red_works_tr", 17, (0.0, 60.0, 0.0, 60.0), (12.0, 14.0), (24, 0)),
          ("red_works_bl", 53, (-60.0, 0.0, -60.0, 0.0), (-12.0, -14.0), (0, 28)),
          ("red_works_br", 55, (0.0, 60.0, -60.0, 0.0), (12.0, -14.0), (24, 28))]


def px(c, r):
    """A pixel corner (column c, row r of the 48 x 56 picture) in the model's coordinates."""
    return (c - 24.0, 28.0 - r)


def materials():
    pal = k.level_palette()

    def m(name, index, metallic, roughness, glow=0.0):
        extra = dict(emission=pal[index], emission_strength=glow) if glow else {}
        return k.material("works_" + name, palette=index, metallic=metallic, roughness=roughness, **extra)
    return {
        "deck": m("deck", 0x03, 0.35, 0.55),
        "dark": m("dark", 0x01, 0.2, 0.7),
        "steel_dark": m("steel_dark", 0x04, 0.45, 0.42),
        "steel": m("steel", 0x06, 0.45, 0.38),
        "steel_light": m("steel_light", 0x08, 0.45, 0.32),
        "knob": m("knob", 0x0a, 0.3, 0.3),
        "red": m("red", 0x48, 0.25, 0.42),
        "button": m("button", 0x4a, 0.2, 0.25, 0.12),
        "tan": m("tan", 0xa8, 0.2, 0.5),
        "tan_dark": m("tan_dark", 0xa5, 0.2, 0.6),
        "rod": m("rod", 0xab, 0.45, 0.32),
        "brass": m("brass", 0x18, 0.5, 0.35),
        "glow_edge": m("glow_edge", 0x77, 0.0, 0.3, 0.4),
        "glow": m("glow", 0x7a, 0.0, 0.25, 0.5),
        "glow_core": m("glow_core", 0x7d, 0.0, 0.2, 0.6),
    }


# --- Solids ----------------------------------------------------------------------------------------------------------

def finish(obj, bevel=0.0, segments=3, angle=30.0, weighted=True, smooth_angle=40.0):
    if bevel > 0:
        mk.bevel(obj, bevel, segments, angle)
    return mk.shade(obj, smooth_angle, weighted)


def block(name, c0, r0, c1, r1, z0, z1, mat, bevel=0.4, segments=2):
    """A bevelled box over the pixel corners (c0, r0) - (c1, r1), from z0 to z1."""
    (x0, y1), (x1, y0) = px(c0, r0), px(c1, r1)
    return finish(mk.box(name, x0, x1, y0, y1, z0, z1, mat), bevel, segments)


def prism(name, pts, z0, z1, mat, bevel=0.4, segments=2):
    """A bevelled prism over an outline of pixel corners (counter-clockwise or not)."""
    poly = [px(c, r) for c, r in pts]
    if sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1])) < 0:
        poly.reverse()
    return finish(mk.prism(name, poly, z0, z1, mat), bevel, segments)


def sloped(name, pts, z0, top, mat, bevel=0.35, segments=2):
    """A bevelled block over an outline of pixel corners whose top is top(c, r) (planes keep its faces flat)."""
    poly = [px(c, r) for c, r in pts]
    if sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1])) < 0:
        poly.reverse()
    obj = mk.wedge(name, poly, z0, lambda x, y: top(x + 24.0, 28.0 - y), mat)
    return finish(obj, bevel, segments)


def lathe_x(name, profile, r_mid, z_axis, mat, segments=24, smooth_angle=50.0):
    """A round part lying across (its axis along x at row r_mid, height z_axis): profile [(column, radius), ...]."""
    y = px(0, r_mid)[1]
    pts = [(c - 24.0, rad) for c, rad in profile]
    obj = k.lathe(name, pts, mat, segments, axis_x=0.0, axis_z=0.0)
    obj.data.transform(Matrix.Translation((0.0, y, z_axis)) @ Matrix.Rotation(-math.pi / 2, 4, "Z"))
    k.recalc_normals(obj)
    return k.smooth(obj, smooth_angle)


def lathe_y(name, profile, c_mid, z_axis, mat, segments=20, smooth_angle=50.0):
    """A round part lying down the screen (its axis along y at column c_mid, height z_axis): profile [(row, radius)]
    from the bottom of the screen up (rows decreasing)."""
    x = px(c_mid, 0)[0]
    pts = sorted([(28.0 - r, rad) for r, rad in profile])
    obj = k.lathe(name, pts, mat, segments, axis_x=x, axis_z=z_axis)
    k.recalc_normals(obj)
    return k.smooth(obj, smooth_angle)


def upright(name, profile, c, r, mat, segments=28, smooth_angle=50.0):
    """A round part standing up at pixel corner (c, r): profile [(radius, z), ...] from its foot up."""
    obj = mk.lathe(name, profile, px(c, r), mat, segments)
    k.recalc_normals(obj)
    return k.smooth(obj, smooth_angle)


def fillet(points, radius, steps=6):
    """A polyline (x, y, z) with its corners rounded (arcs in the corners' planes)."""
    pts = [Vector(p) for p in points]
    out = [pts[0]]
    for i in range(1, len(pts) - 1):
        a, b, c = pts[i - 1], pts[i], pts[i + 1]
        u, w = (a - b).normalized(), (c - b).normalized()
        ang = u.angle(w)
        if ang > math.pi - 1e-3:
            out.append(b)
            continue
        t = radius / math.tan(ang / 2)
        t = min(t, (a - b).length * 0.49, (c - b).length * 0.49)
        p0, p1 = b + u * t, b + w * t
        for j in range(steps + 1):
            s = j / steps
            q0 = p0 + (b - p0) * s
            q1 = b + (p1 - b) * s
            out.append(q0 + (q1 - q0) * s)
    out.append(pts[-1])
    return out


def pipe(name, path_cr, z_axis, radius, mat, segments=16):
    """A tube along a path of pixel corners (column, row) at height z_axis, its bends rounded, its ends capped."""
    pts = [(*px(c, r), z_axis) for c, r in path_cr]
    dense = fillet(pts, radius * 1.6, 8)
    obj = mk.tube(name, [tuple(p) for p in dense], radius, mat, segments)
    k.recalc_normals(obj)
    return k.smooth(obj, 60.0)


def plate_relief(name, outer, holes, top, rim, mats, key, side, bottom=0.0, spacing=0.4, hole_floor=None,
                 hole_rim=0.4, band=1.0):
    """A slab over an outline (pixel corners) with holes sunk into it: its top at `top`, rounding over `rim` at its
    outer edge down to `bottom`, and at each hole's edge down to hole_floor (the hole's own parts lie in it)."""
    outer_m = [px(c, r) for c, r in outer]
    holes_m = [[px(c, r) for c, r in h] for h in holes]
    outer_region = Region([outer_m])
    hole_regions = [Region([h]) for h in holes_m]

    def height(x, y, d):
        do = float(outer_region.distance([(x, y)])[0])
        dh = min([float(hr.distance([(x, y)])[0]) for hr in hole_regions] or [99.0])
        if dh < do and hole_floor is not None:
            return hole_floor + (top - hole_floor) * round_edge(dh, hole_rim)
        return bottom + (top - bottom) * round_edge(do, rim)
    polys = [ccw(outer_m)] + [ccw(h) for h in holes_m]
    obj = relief(name, polys, height, mats, paint=lambda x, y, d: key, side=side, bottom=bottom, spacing=spacing,
                 smooth_angle=45.0, band=band)
    return obj


def ccw(points):
    area = sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(points, points[1:] + points[:1]))
    return list(points) if area > 0 else list(reversed(points))


def rect(c0, r0, c1, r1, corner=0.0, steps=5):
    """A rectangle of pixel corners (counter-clockwise in the model), its corners rounded: corner a radius or four
    (top left, top right, bottom right, bottom left)."""
    radii = corner if isinstance(corner, (tuple, list)) else (corner,) * 4
    (x0, y1), (x1, y0) = px(c0, r0), px(c1, r1)
    tl, tr, br, bl = radii
    out = []
    for (cx, cy, rad, a0) in ((x1 - br, y0 + br, br, -90.0), (x1 - tr, y1 - tr, tr, 0.0), (x0 + tl, y1 - tl, tl, 90.0),
                              (x0 + bl, y0 + bl, bl, 180.0)):
        n = steps if rad > 0 else 0
        for i in range(n + 1):
            a = math.radians(a0 + 90.0 * i / max(n, 1))
            out.append((cx + rad * math.cos(a) + 24.0, 28.0 - (cy + rad * math.sin(a))))
    clean = []
    for p_ in out:
        if not clean or math.dist(clean[-1], p_) > 1e-6:
            clean.append(p_)
    return clean


def ellipse(cc, rr, rc, rrad, n=40):
    return [(cc + rc * math.cos(2 * math.pi * i / n), rr + rrad * math.sin(2 * math.pi * i / n)) for i in range(n)]


# --- The parts ---------------------------------------------------------------------------------------------------------

def deck(m):
    poly = [px(c, r) for c, r in OUTLINE]
    obj = mk.prism("deck", ccw(poly), -0.4, DECK_TOP, m["deck"])
    return finish(obj, DECK_BEVEL, 2)


def drum(m):
    """The grey drum lying across the top left, its red end caps, two grooves round it."""
    z = 2.55
    body = lathe_x("drum", [(6.2, 0.01), (6.25, 2.3), (6.6, 2.55), (8.9, 2.55), (9.15, 2.3), (9.55, 2.3), (9.8, 2.55),
                            (12.3, 2.55), (12.7, 2.3), (12.75, 0.01)], 3.9, z, m["steel_light"], 22)
    caps = []
    for name, c0, c1 in (("drum_cap_l", 4.9, 6.6), ("drum_cap_r", 12.4, 13.9)):
        caps.append(lathe_x(name, [(c0, 0.01), (c0 + 0.02, 2.1), (c0 + 0.35, 2.7), (c1 - 0.35, 2.7), (c1 - 0.02, 2.1),
                                   (c1, 0.01)], 3.9, z, m["red"], 22))
    cradle = block("drum_cradle", 5.6, 1.6, 13.4, 6.4, 0.6, 1.9, m["steel_dark"], 0.3)
    return [body, cradle] + caps


def rail_panel(m):
    """The dark panel striped with a tan rail along it, brass collars on the rail."""
    panel = block("rail_panel", 14.0, 2.6, 30.0, 6.5, 0.6, 2.6, m["steel_dark"], 0.35)
    rail = lathe_x("rail", [(14.6, 0.01), (14.65, 0.62), (29.35, 0.62), (29.4, 0.01)], 4.1, 2.75, m["rod"], 14)
    collars = []
    for i, c in enumerate((18.5, 22.5, 26.5)):
        collars.append(lathe_x("rail_collar_%d" % i, [(c - 0.45, 0.01), (c - 0.43, 0.75), (c + 0.43, 0.75),
                                                       (c + 0.45, 0.01)], 4.1, 2.75, m["brass"], 14))
    lower = block("rail_lip", 14.4, 5.0, 29.6, 6.3, 2.4, 2.9, m["steel"], 0.2, 2)
    return [panel, rail, lower] + collars


def knob(m):
    """The grey knob at the top right: a short post with a rounded head on a dark foot."""
    foot = upright("knob_foot", [(2.45, 0.6), (2.45, 1.9), (2.2, 2.2), (0.01, 2.2)], 32.5, 3.4, m["steel_dark"])
    post = upright("knob", [(1.75, 1.5), (1.75, 3.3), (1.6, 3.85), (1.2, 4.3), (0.6, 4.55), (0.01, 4.6)], 32.5, 3.1,
                   m["knob"], 24)
    return [foot, post]


def red_blocks(m):
    """The big red block bent down at the left (its upper arm and the part under it), the red block at the upper
    right (two layers), the small red block at the left, the red blocks under the grilles."""
    arm = rect(3.2, 7.2, 16.6, 11.6, (2.8, 0.6, 0.6, 0.5), 8)
    out = [prism("red_arm", arm, 0.6, 5.4, m["red"], 0.9)]
    out.append(block("red_arm_low", 3.2, 11.2, 9.7, 16.1, 0.6, 4.5, m["red"], 0.85))
    out.append(block("red_ur_top", 22.0, 7.3, 28.7, 11.5, 0.6, 5.2, m["red"], 0.85))
    out.append(block("red_ur_low", 22.0, 11.3, 28.7, 15.5, 0.6, 4.6, m["red"], 0.85))
    out.append(block("red_small", 3.0, 29.4, 6.9, 33.9, 0.0, 3.0, m["red"], 0.7))
    out.append(block("red_under_l", 11.0, 21.2, 14.8, 28.7, 0.6, 4.6, m["red"], 0.75))
    out.append(block("red_under_r", 14.9, 21.2, 18.9, 28.7, 0.6, 4.4, m["red"], 0.75))
    return out


def grey_blocks(m):
    out = [block("grey_beside", 9.6, 11.4, 13.3, 15.3, 0.6, 3.8, m["steel"], 0.35)]
    out.append(block("grey_under", 10.0, 17.5, 13.4, 21.2, 0.6, 3.6, m["steel"], 0.35))
    out.append(block("grey_ur", 28.7, 7.4, 30.8, 15.4, 0.6, 2.5, m["steel_dark"], 0.3))
    out.append(block("grey_box_left", 19.4, 17.8, 22.5, 27.4, 0.6, 3.0, m["steel"], 0.3))
    out.append(block("grey_low_a", 12.4, 33.0, 15.4, 39.5, 0.6, 3.6, m["steel_light"], 0.35))
    out.append(block("grey_low_b", 15.6, 33.0, 18.6, 39.5, 0.6, 3.6, m["steel_light"], 0.35))
    out.append(block("slat_low_a", 29.3, 29.4, 31.3, 32.9, 0.6, 3.0, m["steel_light"], 0.3))
    out.append(block("slat_low_b", 31.5, 29.4, 33.5, 32.9, 0.6, 3.0, m["steel_light"], 0.3))
    return out


def grilles(m):
    """The two glowing grilles in their dark boxes: a pillow glowing hottest in its middle, two dark bars across."""
    out = []
    for i, (r0, r1) in enumerate(((11.0, 15.4), (17.4, 21.5))):
        out.append(plate_relief("grille_box_%d" % i, rect(13.1, r0, 19.5, r1, 0.5),
                                [rect(13.55, r0 + 0.45, 19.05, r1 - 0.45, 0.3)], 5.0, 0.4, m, "steel_dark",
                                "steel_dark", bottom=0.6, spacing=0.42, hole_floor=3.9, hole_rim=0.3, band=0.8))
        cr0, cr1 = r0 + 0.5, r1 - 0.5
        cc0, cc1 = 13.6, 19.0
        poly = [px(c, r) for c, r in rect(cc0, cr0, cc1, cr1, 0.3)]

        def h(x, y, d):
            return 3.9 + 0.95 * round_edge(d, 1.2)

        def paint(x, y, d):
            return "glow_edge" if d < 0.3 else "glow" if d < 0.8 else "glow_core"
        out.append(relief("grille_%d" % i, [ccw(poly)], h, m, paint=paint, side="glow_edge", bottom=3.0,
                          spacing=0.34, borders=[(lambda x, y, d: d, 0.3), (lambda x, y, d: d, 0.8)],
                          smooth_angle=60.0, band=1.2))
        r = (cr0 + cr1) / 2
        out.append(lathe_x("grille_bar_%d" % i, [(13.5, 0.01), (13.55, 0.18), (19.05, 0.18), (19.1, 0.01)], r, 4.95,
                           m["steel_dark"], 8))
    return out


def pipes(m):
    """The red pipe: from left of the grilles along rows 16-17 to column 34.4, down the right side into the red bar,
    and its branch back along row 28 to column 21; flanges at its ends."""
    z, rad = 2.3, 0.98
    out = [pipe("pipe_main", [(10.4, 16.6), (34.4, 16.6), (34.4, 33.6)], z, rad, m["red"]),
           pipe("pipe_branch", [(20.8, 28.3), (34.2, 28.3)], z, rad * 0.95, m["red"])]
    out.append(lathe_x("pipe_flange", [(10.0, 0.01), (10.05, 1.25), (10.95, 1.25), (11.0, 0.01)], 16.6, z, m["red"],
                       18))
    out.append(lathe_x("pipe_flange_b", [(20.4, 0.01), (20.45, 1.2), (21.25, 1.2), (21.3, 0.01)], 28.3, z,
                       m["steel_light"], 18))
    return out


def tan_box(m):
    """The tan box at the left: a slab with a round socket sunk in it (a red button in it), a brass strip down its
    left side and a brass rail along its foot."""
    socket = ellipse(5.25, 23.2, 3.55, 3.5, 44)
    out = [plate_relief("tan_box", rect(0.75, 15.6, 10.35, 27.2, 0.8), [socket], 4.3, 1.0, m, "tan", "tan",
                        bottom=0.0, spacing=0.5, hole_floor=2.6, hole_rim=0.45, band=1.1)]
    floor = mk.prism("tan_socket", ccw([px(c, r) for c, r in ellipse(5.25, 23.2, 3.7, 3.65, 44)]), 0.4, 2.65,
                     m["dark"])
    out.append(mk.shade(floor, 40, False))
    x, y = px(5.2, 23.0)
    out.append(mk.dome("button", (x, y), (2.45, 2.4, 2.4), 2.55, m["button"], 22, 7, power=2.2))
    out.append(block("brass_strip", 0.0, 15.4, 0.95, 29.4, 0.0, 4.0, m["brass"], 0.35))
    out.append(lathe_x("brass_rail", [(0.0, 0.01), (0.05, 0.7), (10.3, 0.7), (10.35, 0.01)], 27.9, 1.1, m["brass"],
                       14))
    return out


def dark_box(m):
    """The dark box in the pipe's frame: a slab with the tan panel sunk in it, its grey lid with a knob on it and its
    grey slats."""
    out = [plate_relief("dark_box", rect(22.4, 17.8, 33.6, 27.6, 0.4), [rect(23.1, 21.0, 29.5, 27.0, 0.25)], 2.9,
                        0.4, m, "steel_dark", "steel_dark", bottom=0.6, spacing=0.45, hole_floor=2.0, hole_rim=0.3,
                        band=0.8)]
    out.append(block("tan_panel", 23.0, 20.9, 29.6, 27.1, 0.6, 2.05, m["tan_dark"], 0.2, 2))
    out.append(block("lid", 22.7, 18.2, 29.4, 20.7, 2.5, 3.4, m["steel_light"], 0.3))
    out.append(lathe_x("lid_knob", [(24.2, 0.01), (24.25, 0.65), (27.6, 0.65), (27.65, 0.01)], 19.4, 3.55,
                       m["steel_dark"], 14))
    for i, r in enumerate((20.4, 22.1, 23.8, 25.5)):
        out.append(block("slat_%d" % i, 29.8, r, 33.3, r + 1.25, 2.4, 3.3, m["steel_light"], 0.22, 2))
    return out


def rods(m):
    out = [lathe_y("rod_ur", [(15.6, 0.01), (15.55, 0.8), (6.65, 0.8), (6.6, 0.01)], 31.8, 1.95, m["rod"], 16)]
    out.append(lathe_y("rod_right", [(34.4, 0.01), (34.35, 0.78), (21.85, 0.78), (21.8, 0.01)], 36.8, 1.85, m["rod"],
                       16))
    for name, r in (("rod_ur_clip_a", 8.4), ("rod_ur_clip_b", 13.6)):
        out.append(block(name, 30.9, r - 0.5, 32.7, r + 0.5, 0.6, 2.2, m["steel_dark"], 0.2, 2))
    return out


def lower_left(m):
    """The tall tan block (its top sloping down to the front), the red wedge beside it, the small red valve."""
    out = [block("tan_tall", 6.6, 33.1, 12.3, 40.9, 0.6, 4.6, m["tan"], 0.7)]
    out.append(pyramid("tan_tall_front", 6.6, 40.6, 12.3, 47.4, 0.6, 2.1, 4.1, m["tan"]))

    def red_top(c, r):
        return 4.4 if r < 42.2 else 4.4 - (r - 42.2) * (4.4 - 1.7) / (47.5 - 42.2)
    out.append(sloped("red_wedge", [(12.4, 39.7), (19.5, 39.7), (19.5, 44.6), (18.0, 47.5), (13.9, 47.5),
                                    (12.4, 44.6)], 0.6, red_top, m["red"], 0.4))
    out.append(upright("red_valve", [(0.75, 0.6), (0.75, 2.2), (0.55, 2.6), (0.01, 2.7)], 20.0, 44.9, m["red"]))
    # The brass bar under the red blocks (row 30), the tan rod across to the red bar (row 45), the grey ledge at the
    # lower left (rows 33-35).
    out.append(lathe_x("brass_bar", [(11.8, 0.01), (11.85, 0.62), (17.95, 0.62), (18.0, 0.01)], 30.3, 1.6,
                       m["brass"], 14))
    out.append(lathe_x("rod_low", [(20.9, 0.01), (20.95, 0.5), (29.1, 0.5), (29.15, 0.01)], 45.4, 1.75, m["rod"], 14))
    out.append(block("ledge", 0.7, 33.5, 6.5, 35.0, 0.0, 1.7, m["steel"], 0.3))
    return out


def pyramid(name, c0, r0, c1, r1, z0, z1, apex, mat, bevel=0.3):
    """A block over the pixel corners (c0, r0) - (c1, r1) standing from z0 to z1, under a pyramid rising to `apex`
    over its middle (four faces: the sprite's X)."""
    import bmesh
    (x0, y1), (x1, y0) = px(c0, r0), px(c1, r1)
    xm, ym = (x0 + x1) / 2, (y0 + y1) / 2
    bm = bmesh.new()
    low = [bm.verts.new(p) for p in ((x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0))]
    mid = [bm.verts.new(p) for p in ((x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1))]
    top = bm.verts.new((xm, ym, apex))
    bm.faces.new(list(reversed(low)))
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new((low[i], low[j], mid[j], mid[i]))
        bm.faces.new((mid[i], mid[j], top))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.data.materials.append(mat)
    return finish(obj, bevel, 2, angle=20.0)


def floor_plates(m):
    """Low steel plates on the deck's empty middle (the sprite's slightly lighter panels there)."""
    return [block("floor_plate", 22.4, 33.4, 28.3, 44.0, 0.6, 1.65, m["steel_dark"], 0.35, 2),
            block("floor_plate_b", 7.2, 29.4, 10.6, 32.6, 0.6, 1.6, m["steel_dark"], 0.3, 2)]


def red_bar(m):
    """The red bar at the lower right: a slab with a slot sunk down it (a grey bar in it) and a tan valve on it."""
    slot = rect(31.45, 34.8, 33.35, 41.1, 0.25)
    out = [plate_relief("red_bar", rect(29.0, 33.0, 33.7, 48.4, 0.7), [slot], 4.2, 0.8, m, "red", "red", bottom=0.6,
                        spacing=0.4, hole_floor=1.9, hole_rim=0.3, band=0.9)]
    out.append(block("red_bar_slot", 31.3, 34.65, 33.5, 41.25, 0.6, 1.95, m["dark"], 0.1, 1))
    out.append(block("red_bar_rod", 31.95, 35.3, 32.85, 40.5, 1.5, 3.2, m["steel_light"], 0.25, 2))
    out.append(upright("valve", [(1.25, 3.9), (1.25, 4.6), (1.05, 4.95), (0.5, 5.15), (0.01, 5.2)], 31.7, 45.1,
                       m["rod"]))
    return out


def build_whole(m):
    parts = [deck(m)]
    for fn in (drum, rail_panel, knob, red_blocks, grey_blocks, grilles, pipes, tan_box, dark_box, rods, lower_left,
               floor_plates, red_bar):
        parts += fn(m)
    bpy.context.view_layer.update()
    return parts


# --- Pieces ------------------------------------------------------------------------------------------------------------

def own_mask(sheet, sprite, c0, r0):
    """The sprite's own pixels (the works', inside OUTLINE: the cobbles left out), rows of bools."""
    mask = k.sprite_mask(sheet, sprite)
    region = Region([ccw([px(c, r) for c, r in OUTLINE])])
    out = []
    for j in range(28):
        pts = [px(c0 + i + 0.5, r0 + j + 0.5) for i in range(24)]
        inside = region.inside(pts)
        out.append([bool(mask[j][i] and inside[i]) for i in range(24)])
    return out


def build():
    options = k.args()
    out = mk.outdir(options)
    only = set(options["only"].split(",")) if "only" in options else None
    k.reset()
    bpy.context.scene.view_settings.view_transform = "Standard"
    m = materials()
    whole = build_whole(m)
    if "stats" in options:
        for obj in sorted(whole, key=lambda o: -mk.triangles([o])):
            print("    %-22s %6d" % (obj.name, mk.triangles([obj])))
        print("    total %d" % mk.triangles(whole))
    sheet = os.path.join(options["check"], "enemy_2.png") if "check" in options else None
    for name, sprite, box, origin, (c0, r0) in PIECES:
        if only is not None and name not in only:
            continue
        parts = []
        for src in whole:
            cap = src.data.materials[0] if src.data.materials else m["deck"]
            piece = cut(src, box, cap)
            if piece is not None:
                piece.name = src.name + "_" + name
                parts.append(piece)
        drop_unused(parts)
        for src in whole:
            src.hide_render = True
        if sheet:
            mk.compare("%s (2 %d, as the camera sees it; the works' own pixels)" % (name, sprite),
                       mk.coverage(parts, 24, 28, centre=origin), own_mask(sheet, sprite, c0, r0))
        shear_to_camera(parts)
        mk.transform(parts, Matrix.Translation((-origin[0], -origin[1], 0.0)))
        bpy.context.view_layer.update()
        triangulate(parts)
        obj = join(parts, name)
        obj.data.name = name
        merge_materials(obj, 15)
        mk.report(name, [obj], os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, [obj])
        bpy.data.objects.remove(obj)
        for src in whole:
            src.hide_render = False


if __name__ == "__main__":
    build()
