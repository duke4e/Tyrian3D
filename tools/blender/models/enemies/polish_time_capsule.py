"""TIME WAR's blue capsule in the sky (sheet 9: 16 18 above 54 56 above 244 246 above 92 94, 2x2 each, one 48 x 112
picture) and its pulsing glass (frames 168 170 / 206 208 / 282 284 and 250 252 / 126 128 / 130 132); polished
(2026-10-22, round 36), rebuilt as a metal frame with glass panels (2026-10-23, round 38: round 36's was a heightfield
painted from the pixels, its glass pixel blocks). It replaced wave3_aj_capsule.py.

Where the level puts it (TIME WAR t100, event 15, the sky; episode 4's enemies 645-652, link 29, moving down with dat3
1): the eight pieces two by two, 645 646 at (100, -84), (124, -84), 647 648 28 pixels lower, 649 650 (244 246: the
sheet keeps them apart from the rest) lower still, 651 652 (92 94) at the bottom. Armour 255; no damaged look; nothing
launched. 645-648, 651 and 652 animate for ever (animate 1, 20 frames): 16 16 16 16 16 168 x5 250 x5 168 x5 (18 170
252 170, 54 206 126 206, 56 208 128 208, 92 282 130 282, 94 284 132 284); 649 and 650 don't. The frames change only
the blue glass of the dome (16 18, and 54 56's rows 0-19) and of the channel down the tail (92 94): two and about four
shades lighter, a slow pulse; the windows, the panes and the lamps (244 246) stay. They are frame models of this
capsule (the same solids, their dome and channel glass in the frame's shades): no other enemy, launched ones
included, shows them. No other sprite is these pixels mirrored, turned or in other ramps (the capsule is its own
mirror image in outline, but lit from the upper left); episode 6 has no TIME WAR wave.

As the sprites and their 4x upscales draw it (the picture's columns and rows; lit from the upper left): a long capsule
lying along the screen, its nose up (columns 0-47, rows 1-111; full width over rows 28-90, a rounded nose and a
tapering tail); a glossy blue glass dome over its front (rows 1-45: ramp 9, a bright highlight at its upper left) in
two halves either side of a grey spine (columns 18-29) with a darker panel down its lower part (rows 17-44); a grey
collar round the dome's rim (rows 33-50, lowest in the middle); under it the spine's block (columns 16-31 of rows
50-58); a band of windows (rows 53-72): a curved glass window on either side (columns 1-11 and 36-46) and in the
middle a raised block of small panes in grey frames (columns 15-34 of rows 58-72); two small blue lamps under it (rows
74-76 and 79-81); grey brackets either side (columns 3-14 and 33-44 of rows 74-84); the grey tail (rows 84-111) with a
seam down either side (columns 12 and 35) and a blue glass channel down its middle (columns 20-27) between two rails
to its tip.

Built (polish_sheet9_solids): the hull a turned solid (its outline fitted to the sprite's: a superellipse nose and tail
on a straight middle, its section round), built TALL as round as the sprite paints it and flattened to FLAT of that,
its built normals kept, so the camera sees a round capsule while it stays 0-13.9 high (round 36's: 0-14.2). On it,
each a solid of its own: the dome's two glass halves (1.4 thick, bevelled), the spine (a strap 2.2 thick with its
lower panel sunk in it), the collar (a band 1.8 thick), the spine's block, the side windows (glass sunk in frames),
the pane block (a frame 2.0 thick with twelve glass panes sunk in it), the lamps (glass domes in sockets), the
brackets, the tail's side plates (their edges the seams) and the channel (glass between two rails). Materials by part
(palette indices of the sprite's ramps): the hull 0x06, frames 0x08, the spine 0x09, its sunk panel 0x04, rails and
sockets 0x05, the tail plates 0x07, the cuts 0x02; glass (a coated glass, metallic 0.45 and roughness 0.12, so that it
mirrors the sky and the sun): the dome and the channel 0x98 glowing 0.12 (frames 168...: 0x9a, 0.2; 250...: 0x9c,
0.32), the side windows 0x98 (0.12), the panes 0x99 (0.14), the lamps 0x9c (0.45, turned domes).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera (z 0: the sky's
plane). The whole's origin is the picture's middle (column 24, row 56): column c's left edge is x = c - 24, row r's top
edge y = 56 - r; the pieces' origins (-12 / 12, 42 / 14 / -14 / -42) (models.cfg origin).

models.cfg: the eight model and sprite lines stay (the glows too), and the twelve frame models' model and frame lines
(time_capsule_<frame> ... origin; frame 9 <frame> time_capsule_<frame>) stay as they are.

Replaces round 36's version of this script (its heightfield and painter, polish_sheet9_kit); wave3_aj_capsule.py is
already gone.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each piece's outline as the
camera sees it against its sprite's pixels), --preview <prefix> (the whole: top and 3/4 views; --pieces 1: each
piece), --only <name,...>.
"""
import math
import os
import sys

from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_sheet9_solids as ss  # noqa: E402

LEFT, TOP = -24.0, 56.0
HALF = 24.0                        # the hull's half width over its straight middle
NOSE = (42.441, 41.385, 2.563)     # the outline's ends: superellipses (row of their middle, length, power), fitted
TAIL = (88.423, 23.949, 1.633)
TALL = 1.0                         # the hull's section's height over its half width, as built (round)
FLAT = 0.53                        # ... flattened to this of it
KEEP, ROUNDER = 1.0, 1.0
GAP = 0.45                         # half the gap between neighbouring parts
CORNER = 1.0
GLASS_T, GLASS_BEVEL = 1.4, 0.7    # the dome's glass halves
SPINE = (17.8, 30.2, 46.0, 2.2, 0.9)                 # columns, lowest row, thickness, bevel
SPINE_PANEL = ((20.6, 27.4), (17.4, 43.8), 0.9)      # the sunk panel down its lower part: columns, rows, thickness
# The collar's edges (column, row) from the outline to the middle (mirrored for the right side).
COLLAR_UP = [(0.0, 35.0), (3.0, 38.6), (6.0, 41.0), (9.0, 42.6), (12.0, 43.8), (15.0, 44.6), (18.0, 45.2), (24.0, 45.8)]
COLLAR_LOW = [(0.0, 40.4), (3.0, 43.6), (6.0, 46.2), (9.0, 47.6), (12.0, 48.6), (15.0, 49.2), (18.0, 49.6),
              (24.0, 50.0)]
COLLAR_T = 1.8
BLOCK = ((16.8, 31.2), (50.5, 57.8), 1.9)            # the spine's block: columns, rows, thickness
WINDOW = [(1.2, 53.0), (4.4, 54.4), (8.2, 56.8), (10.8, 60.0), (11.2, 64.5), (11.0, 69.6), (9.4, 71.4), (5.4, 71.4),
          (2.4, 69.4), (1.0, 65.0)]                  # the left side window (mirrored for the right)
WINDOW_FRAME = (1.4, 1.6)                            # its frame: width, thickness
# The pane block: columns, rows, panes across and down, the bars between them, its frame's thickness.
PANES = ((14.6, 33.4), (58.2, 72.0), (4, 3), 0.9, 2.0)
PANE_T = 0.8
LAMPS = [((24.0, 75.3), (3.7, 1.25)), ((24.0, 80.4), (3.7, 1.25))]   # middle (column, row), radii
SOCKET = (0.9, 1.4)                                  # the lamps' sockets: width round them, thickness
BRACKET = [(3.4, 74.6), (14.4, 74.6), (14.4, 77.6), (11.8, 78.2), (11.8, 83.6), (4.4, 83.6), (3.0, 80.0)]
BRACKET_T = 1.8
TAIL_PLATE = (85.2, 12.6, 1.0)                       # the tail's side plates: from row, their inner edge, thickness
CHANNEL = ((20.4, 27.6), 84.0, (1.6, 1.8), 0.8)       # the channel: columns, from row; rails' width, thickness; glass
SMALL = dict(edge=0.7, steps=(0.0, 45.0, 90.0))      # small parts: coarser outlines, their bevel in two strips

PIECES = [(16, 0, 0), (18, 24, 0), (54, 0, 28), (56, 24, 28), (244, 0, 56), (246, 24, 56), (92, 0, 84), (94, 24, 84)]
# The looks: the picture's sprites -> their models (frame 1: 168 ..., frame 2: 250 ...); 244 246 don't animate.
FRAMES = {"base": {16: 16, 18: 18, 54: 54, 56: 56, 244: 244, 246: 246, 92: 92, 94: 94},
          "f1": {16: 168, 18: 170, 54: 206, 56: 208, 92: 282, 94: 284},
          "f2": {16: 250, 18: 252, 54: 126, 56: 128, 92: 130, 94: 132}}
GLASS = {"base": (0x98, 0.12), "f1": (0x9a, 0.2), "f2": (0x9c, 0.32)}    # the dome's and the channel's glass a look
GLASS_FINISH = (0.45, 0.12)        # its metalness and roughness (a coated glass: it mirrors the sky and the sun)


def P(c, r):
    return (c + LEFT, TOP - r)


def row_of(y):
    return TOP - y


def half_width(y):
    """The hull's half width at y (its outline, fitted to the sprite's)."""
    r = row_of(y)
    for (rc, L, p), sense in ((NOSE, -1.0), (TAIL, 1.0)):
        if (r - rc) * sense > 0:
            t = min(1.0, abs(r - rc) / L)
            return HALF * max(0.0, 1.0 - t ** p) ** (1.0 / p)
    return HALF


def hull_z(x, y):
    w = half_width(y)
    if w <= 1e-6:
        return 0.0
    return TALL * w * math.sqrt(max(0.0, 1.0 - (x / w) ** 2))


def hull_normal(x, y, h=0.02):
    """The turned hull's normal at (x, y) (its section a circle: radially out, tilted along its axis by its taper)."""
    w = half_width(y)
    dw = (half_width(y + h) - half_width(y - h)) / (2 * h)
    if w < 0.05:
        return (0.0, math.copysign(1.0, -dw if dw else y), 0.0)
    z = hull_z(x, y)
    return tuple(Vector((max(-1.0, min(1.0, x / w)), -dw, z / w)).normalized())


def materials():
    p = ss.pal
    m = {"body": p("tcap_body", 0x06, 0.3, 0.38), "frame": p("tcap_frame", 0x08, 0.35, 0.32),
         "spine": p("tcap_spine", 0x09, 0.4, 0.3), "recess": p("tcap_recess", 0x04, 0.3, 0.45),
         "rail": p("tcap_rail", 0x05, 0.4, 0.35), "tail": p("tcap_tail", 0x07, 0.3, 0.36),
         "dark": p("tcap_dark", 0x02, 0.2, 0.6),
         "window": p("tcap_window", 0x98, 0.45, 0.14, 0.12), "pane": p("tcap_pane", 0x99, 0.45, 0.14, 0.14),
         "lamp": p("tcap_lamp", 0x9c, 0.0, 0.08, 0.45)}
    for look, (index, glow) in GLASS.items():
        m["glass_" + look] = p("tcap_glass", index, GLASS_FINISH[0], GLASS_FINISH[1], glow)
    return m


# --- Outlines -------------------------------------------------------------------------------------------------------

def outline_left(r0, r1, step=0.5):
    """The hull's left edge (x, y) from row r0 to row r1."""
    n = max(2, int(abs(r1 - r0) / step))
    return [(-half_width(TOP - (r0 + (r1 - r0) * i / n)), TOP - (r0 + (r1 - r0) * i / n)) for i in range(n + 1)]


def nose_row(w):
    """The row where the hull's nose is w wide (half width)."""
    lo, hi = NOSE[0] - NOSE[1], NOSE[0]
    for _ in range(50):
        mid = 0.5 * (lo + hi)
        if half_width(TOP - mid) < w:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def tail_row(w):
    """The row where the hull's tail is w wide (half width)."""
    lo, hi = TAIL[0], TAIL[0] + TAIL[1]
    for _ in range(50):
        mid = 0.5 * (lo + hi)
        if half_width(TOP - mid) > w:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def clip_to_hull(p, margin=0.35):
    x, y = p
    w = max(0.0, half_width(y) - margin)
    return (max(-w, min(w, x)), y)


def mirrored(poly):
    return [(-x, y) for x, y in reversed(poly)]


def shape(points, inset=0.0, corner=CORNER):
    """A part's outline from (column, row) points, kept inside the hull's outline (its edges split first, so only the
    points beyond the outline move), its corners rounded."""
    poly = [P(c, r) for c, r in points]
    if inset:
        poly = ss.inset(poly, inset)
    return ss.round_corners([clip_to_hull(p) for p in ss._dense(poly, 0.4)], corner)


def collar_row(edge, c):
    """The row of a collar edge at column c (between its points)."""
    for (c0, r0), (c1, r1) in zip(edge[:-1], edge[1:]):
        if c0 <= c <= c1:
            return r0 + (r1 - r0) * (c - c0) / (c1 - c0)
    return edge[-1][1]


def canopy_outline():
    """The dome's left glass: from the nose down the outline to the collar, along it to the spine, up the spine."""
    c_sp = SPINE[0]
    r_top = nose_row(24.0 - c_sp)
    pts = outline_left(r_top, COLLAR_UP[0][1])
    pts += [P(c, r) for c, r in COLLAR_UP[1:] if c < c_sp] + [P(c_sp, collar_row(COLLAR_UP, c_sp))]
    pts = ss.inset(ss.dedupe(pts), GAP)
    return ss.round_corners([clip_to_hull(p, 0.5) for p in pts], CORNER)


def band(edge):
    """A collar edge across the hull: from its left end on the outline through the middle to its right end."""
    pts = [P(c, r) for c, r in edge]
    pts[0] = (-half_width(pts[0][1]), pts[0][1])
    return pts + [(-x, y) for x, y in reversed(pts[:-1])]


def collar_outline():
    poly = ss.dedupe(band(COLLAR_UP) + list(reversed(band(COLLAR_LOW))))
    poly = ss.inset(poly, GAP)
    return ss.round_corners([clip_to_hull(p, 0.35) for p in poly], CORNER)


def spine_outline():
    """The spine's strap: down from the nose (its top edge along the nose's outline) to its lowest row."""
    c0, c1, r1, _, _ = SPINE
    nose = []
    for i in range(13):
        c = c1 - (c1 - c0) * i / 12
        nose.append(P(c, nose_row(abs(c + LEFT)) + 0.35))
    pts = [P(c0, r1), P(c1, r1)] + nose
    return ss.round_corners([clip_to_hull(p, 0.35) for p in ss.dedupe(pts)], CORNER)


# --- Parts ----------------------------------------------------------------------------------------------------------

def hull(m, step=1.0, around=36):
    """The hull: sections round its axis (half circles over its outline, flat underneath), lofted from nose to tail;
    its normals the turned surface's."""
    r0 = NOSE[0] - NOSE[1] + 0.02
    r1 = 112.3
    n = int(math.ceil((r1 - r0) / step))
    rows = [r0 + (r1 - r0) * i / n for i in range(n + 1)]
    # finer near the nose's tip
    rows = sorted(set([round(r, 4) for r in rows] + [round(r0 + d, 4) for d in (0.1, 0.25, 0.5)]))
    sections = []
    for r in rows:
        y = TOP - r
        w = max(half_width(y), 0.02)
        sec = []
        for j in range(around + 1):
            a = math.pi * j / around
            sec.append(Vector((w * math.cos(a), y, TALL * w * math.sin(a))))
        sections.append(sec)
    obj = k.loft("tcap_hull", sections, m["body"], start_point=(0.0, TOP - r0 + 0.01, 0.0),
                 end_point=(0.0, TOP - r1, 0.0))
    mesh = obj.data
    mesh.polygons.foreach_set("use_smooth", [True] * len(mesh.polygons))
    cn = []
    for poly in mesh.polygons:
        under = poly.normal.z < -0.9
        for li in poly.loop_indices:
            v = mesh.vertices[mesh.loops[li].vertex_index].co
            cn.append((0.0, 0.0, -1.0) if under else hull_normal(v.x, v.y))
    mesh.normals_split_custom_set(cn)
    mesh.update()
    return obj


def plate(name, outer, holes, thick, bevel, mat, side, **kw):
    """A part lying on the hull."""
    return ss.shell_plate(name, outer, holes, hull_z, hull_normal, thick, bevel, mat, side, **kw)


def canopy(m, look):
    left = canopy_outline()
    g = m["glass_" + look]
    return [plate("tcap_canopy_l", left, [], GLASS_T, GLASS_BEVEL, g, m["body"]),
            plate("tcap_canopy_r", mirrored(left), [], GLASS_T, GLASS_BEVEL, g, m["body"])]


def spine(m):
    c0, c1, r1, t, b = SPINE
    (pc0, pc1), (pr0, pr1), pt = SPINE_PANEL
    hole = shape([(pc0, pr0), (pc1, pr0), (pc1, pr1), (pc0, pr1)])
    strap = plate("tcap_spine", spine_outline(), [hole], t, b, m["spine"], m["recess"])
    panel = plate("tcap_spine_panel", ss.inset(hole, -0.3), [], pt, 0.4, m["recess"], m["recess"])
    return [strap, panel]


def collar(m):
    return [plate("tcap_collar", collar_outline(), [], COLLAR_T, 0.8, m["frame"], m["body"])]


def block(m):
    (c0, c1), (r0, r1), t = BLOCK
    return [plate("tcap_block", shape([(c0, r0), (c1, r0), (c1, r1), (c0, r1)]), [], t, 0.8, m["frame"], m["body"])]


def windows(m):
    out = []
    glass = shape(WINDOW, corner=1.2)
    fw, ft = WINDOW_FRAME
    frame = [clip_to_hull(p, 0.35) for p in ss.inset(glass, -fw)]
    hole = ss.inset(glass, -0.35)
    for side, f in (("l", lambda poly: poly), ("r", mirrored)):
        out.append(plate("tcap_wframe_" + side, ss.round_corners(f(frame), CORNER), [f(hole)], ft, 0.35, m["frame"],
                         m["body"], **SMALL))
        out.append(plate("tcap_window_" + side, f(glass), [], PANE_T, 0.4, m["window"], m["body"], **SMALL))
    return out


def pane_block(m):
    (c0, c1), (r0, r1), (nx, ny), bar, t = PANES
    pw = (c1 - c0 - bar * (nx + 1)) / nx
    ph = (r1 - r0 - bar * (ny + 1)) / ny
    holes, panes = [], []
    for j in range(ny):
        for i in range(nx):
            a = c0 + bar + i * (pw + bar)
            b = r0 + bar + j * (ph + bar)
            pane = shape([(a, b), (a + pw, b), (a + pw, b + ph), (a, b + ph)], corner=0.45)
            holes.append(pane)
            panes.append(plate("tcap_pane%d" % (j * nx + i), ss.inset(pane, 0.15), [], PANE_T, 0.3, m["pane"],
                               m["body"], inner=1.2, **SMALL))
    frame = plate("tcap_pane_frame", shape([(c0, r0), (c1, r0), (c1, r1), (c0, r1)]), holes, t, 0.3, m["frame"],
                  m["recess"], **SMALL)
    return [frame] + panes


def lamps(m):
    out = []
    w, t = SOCKET
    for i, ((c, r), (rx, ry)) in enumerate(LAMPS):
        x, y = P(c, r)
        lens = ss.ellipse_arc((x, y), (rx, ry), 0.0, 360.0, 0.3)[:-1]
        sock = ss.ellipse_arc((x, y), (rx + w, ry + w), 0.0, 360.0, 0.3)[:-1]
        out.append(plate("tcap_socket%d" % i, sock, [ss.inset(lens, -0.2)], t, 0.3, m["rail"], m["recess"], **SMALL))
        prof = [(rx, -0.4), (rx, 0.5), (rx * 0.93, 1.0), (rx * 0.78, 1.45), (rx * 0.5, 1.75), (0.001, 1.85)]
        out.append(ss.turned_on("tcap_lamp%d" % i, (x, y, hull_z(x, y)), hull_normal(x, y), prof, m["lamp"],
                                segments=32, smooth=60.0, squash=(1.0, ry / rx)))
    return out


def brackets(m):
    left = shape(BRACKET)
    return [plate("tcap_bracket_l", left, [], BRACKET_T, 0.7, m["frame"], m["body"], **SMALL),
            plate("tcap_bracket_r", mirrored(left), [], BRACKET_T, 0.7, m["frame"], m["body"], **SMALL)]


def tail_plates(m):
    r0, c_in, t = TAIL_PLATE
    x_in = c_in + LEFT
    # from the seam's top down along it to the outline, up the outline back to the top
    r_end = tail_row(abs(x_in))
    pts = [P(c_in, r0)] + [(x_in, TOP - (r0 + (r_end - r0) * i / 20)) for i in range(1, 20)]
    pts += outline_left(r_end, r0)
    left = ss.inset(ss.dedupe(pts), GAP)
    left = ss.round_corners([clip_to_hull(p, 0.45) for p in left], CORNER)
    return [plate("tcap_tail_l", left, [], t, 0.6, m["tail"], m["body"]),
            plate("tcap_tail_r", mirrored(left), [], t, 0.6, m["tail"], m["body"])]


def channel(m, look):
    (c0, c1), r0, (rw, rt), gt = CHANNEL
    r1 = 112.4
    out = []
    for side, (a, b) in (("l", (c0 - rw, c0)), ("r", (c1, c1 + rw))):
        rail = shape([(a, r0), (b, r0), (b, r1), (a, r1)], corner=0.6)
        out.append(plate("tcap_rail_" + side, rail, [], rt, 0.5, m["rail"], m["recess"]))
    glass = shape([(c0 + 0.25, r0 + 0.3), (c1 - 0.25, r0 + 0.3), (c1 - 0.25, r1), (c0 + 0.25, r1)], corner=0.8)
    out.append(plate("tcap_channel", glass, [], gt, 0.4, m["glass_" + look], m["recess"]))
    return out


def whole(m, look="base"):
    parts = [hull(m)]
    parts += canopy(m, look) + spine(m) + collar(m) + block(m) + windows(m) + pane_block(m) + lamps(m)
    parts += brackets(m) + tail_plates(m) + channel(m, look)
    return parts


def pieces(look):
    out = []
    for s, c0, r0 in PIECES:
        if s not in FRAMES[look]:
            continue
        x0, y1 = LEFT + c0, TOP - r0
        out.append(("time_capsule_%d" % FRAMES[look][s], s, (x0, x0 + 24.0, y1 - 28.0, y1), (c0 - 12.0, 42.0 - r0),
                    None))
    return out


def build():
    options = k.args()
    only = set(options["only"].split(",")) if "only" in options else None
    sheet = os.path.join(options["check"], "enemy_9.png") if "check" in options else None
    for look in ("base", "f1", "f2"):
        todo = [p for p in pieces(look) if only is None or p[0] in only]
        if not todo:
            continue
        k.reset()
        m = materials()
        parts = whole(m, look)
        ss.flatten(parts, FLAT, KEEP, ROUNDER)
        if "preview" in options and look == "base":
            ss.whole_preview(options["preview"] + "time_capsule", parts, (52, 116))
        ss.export_pieces(parts, todo, m["dark"], options, sheet if look == "base" else None)


if __name__ == "__main__":
    build()
