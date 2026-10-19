"""The purple armoured pod shaped like a heater shield, of TYRIAN, HOLES, ASSASSIN, BONUS, TYRIAN X and SAVARA (sheet
2 sprite 127, 2x2: 24 x 28 pixels; enemy 31, in the sky, on the ground and on top; not animated), polished
(2026-10-19; it replaces wave2_f.py's purple_shield(), a hull inflated from the sprite's outline). models.cfg:
sprite 2 127 purple_shield yaw=0 (unchanged). No other enemy shows this sprite; it is no other sprite's pixels
mirrored or in other ramps.

As the sprite and its 4x upscale draw it, point down the screen: a shield of dark purple armour (ramp 5), its top
edge flat (row 0), the shoulders chamfered (rows 1-4), straight sides (rows 4-13) and the lower half tapering to a
short flat point (row 27); a raised border round it, lit on the left. Down its middle: a light blue visor window in
a teal frame set into the top edge (rows 1-3, columns 9-15); a strip of two ribs with a groove between them from the
visor down to the middle window (rows 4-8, columns 10-14), crossing a seam across the upper armour (rows 6-7: the
brow plate above it); the middle window (rows 9-12, columns 10-14): two blue slats with a grey bar between them over
a teal sill, in a dark frame; a lighter chin plate below it (rows 13-20, columns 9-15); seven dark round ports
along the lower half (columns 3-4 and 19-20 of rows 11-13, 4-5 and 18-19 of rows 15-16, 7-8 and 15-16 of rows
18-20, 11-13 of rows 20-21); a blue block at the point, its top edge teal (rows 22-26, columns 9-15), a stud on its
face.

Built as hard-surface armour: the hull lofted from superelliptic sections (a flat dome on a flat bottom), the
border a rounded band along its edge, the brow, the chin plate and the block raised plates lying on it
(polish_redjet.facet), the ribs and the sill rounded bars, the ports dark dishes set into the armour. The windows'
glass glows a little in its own blue (the slanted camera sees it in the hull's shade).

The sprite is symmetric about its column 12 (x 0.5 here): the shield is built about u = 0 and moved there. Origin
at the sprite's centre (pixel 12, 14); +Y up the sprite, +Z towards the camera.

Replaces wave2_f.py's purple_shield() (its @model("purple_shield", "enemy_2", 127) function, the SHIELD art block
above it, which nothing else reads, and the purple_shield line of the docstring): remove them so that they don't
overwrite this model.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouette against
enemy_2.png), --preview <prefix>.
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
from polish_jets import Curve, triangles  # noqa: E402
from polish_redjet import chaikin, end_round, facet, resample  # noqa: E402
from polish_squid_ship import ccw, rounded_rect, tube  # noqa: E402

AXIS_X = 0.5

# The hull's plan (right half, u >= 0, from the top edge's middle round to the point's), 1/3 pixel inside the
# sprite's outline: the flat top edge, the chamfered shoulders, the straight side, the taper to the flat point.
PLAN = [(0.0, 13.67), (3.9, 13.67), (5.6, 13.45), (7.6, 12.95), (8.6, 12.25), (9.6, 11.25), (10.6, 10.25),
        (11.1, 9.4), (11.17, 8.0), (11.17, 1.0), (11.05, 0.1), (10.62, -0.6), (9.2, -3.4), (7.2, -7.4),
        (5.2, -11.4), (4.25, -12.85), (3.4, -13.5), (2.0, -13.67), (0.0, -13.67)]
HULL_TOP = Curve([(-13.7, 2.6), (-11.0, 3.4), (-7.0, 4.3), (-2.0, 4.85), (3.0, 5.0), (8.0, 4.7), (11.5, 4.0),
                  (13.7, 3.2)])
HULL_POWER = 2.3
BORDER_IN, BORDER_RADIUS = 0.7, 0.5       # the raised border: how far inside the edge, its radius

# The ports round the lower half (left ones; u, y, radii across and along their long axis, its angle in degrees
# from +X) and the one at the bottom.
PORTS = [(-8.0, 1.4, 1.0, 1.5, 90.0), (-7.0, -2.0, 1.0, 1.15, 60.0), (-4.0, -5.6, 0.9, 1.4, 62.0)]
BOTTOM_PORT = (0.0, -7.35, 0.85, 1.4)


def half_width_table():
    """The plan's half-width along y (the right half of PLAN, smoothed), as a function."""
    pts = sorted((y, u) for u, y in PLAN)
    ys = sorted({round(y, 3) for y, _ in pts})
    rows = []
    for y in ys:
        rows.append((y, max(u for yy, u in pts if abs(yy - y) < 1e-3)))
    return rows


HALF = Curve(half_width_table())
Y_TOP, Y_BOTTOM = 13.67, -13.67


def half_width(y):
    if y >= Y_TOP or y <= Y_BOTTOM:
        return 0.0
    hw = HALF(y)
    # The top and bottom edges are flat: round the corners off within half a pixel of them.
    return hw * end_round(y, Y_BOTTOM, Y_TOP, 0.55, 0.55)


def hull_top(u, y):
    hw = half_width(y)
    if hw <= 0.05 or abs(u) >= hw:
        return 0.0
    return HULL_TOP(y) * (1 - (abs(u) / hw) ** HULL_POWER) ** (1 / HULL_POWER)


def materials():
    pal = k.level_palette()
    return {
        "hull": k.material("pshield_hull", palette=0x54, metallic=0.35, roughness=0.34),
        "border": k.material("pshield_border", palette=0x56, metallic=0.35, roughness=0.3),
        "brow": k.material("pshield_brow", palette=0x56, metallic=0.35, roughness=0.3),
        "rib": k.material("pshield_rib", palette=0x5a, metallic=0.35, roughness=0.28),
        "chin": k.material("pshield_chin", palette=0x59, metallic=0.35, roughness=0.3),
        "dark": k.material("pshield_dark", palette=0x52, metallic=0.25, roughness=0.5),
        "port": k.material("pshield_port", palette=0x50, metallic=0.2, roughness=0.6),
        "glass": k.material("pshield_glass", palette=0x3b, metallic=0.1, roughness=0.12, emission=pal[0x3a],
                            emission_strength=0.45),
        "teal": k.material("pshield_teal", palette=0x86, metallic=0.3, roughness=0.26),
        "bar": k.material("pshield_bar", palette=0x66, metallic=0.4, roughness=0.3),
        "block": k.material("pshield_block", palette=0x37, metallic=0.3, roughness=0.28, emission=pal[0x36],
                            emission_strength=0.2),
        "trim": k.material("pshield_trim", palette=0x84, metallic=0.3, roughness=0.26),
        "stud": k.material("pshield_stud", palette=0x68, metallic=0.5, roughness=0.25),
    }


# --- The hull -------------------------------------------------------------------------------------------------

def hull(m):
    ys = [Y_TOP - 0.01] + [Y_TOP - 0.06 - (Y_TOP - Y_BOTTOM - 0.12) * i / 40 for i in range(41)] + [Y_BOTTOM + 0.01]
    ys = sorted(set(round(y, 4) for y in ys), reverse=True)
    rings = []
    for y in ys:
        hw = max(half_width(y), 0.05)
        rings.append(k.ring(y, hw, 1.0, 28, z=0.0, top=max(HULL_TOP(y) * min(1.0, hw / 1.5), 0.05), bottom=0.02,
                            power=HULL_POWER))
    rings.reverse()
    body = k.loft("hull", rings, m["hull"], start_point=(0, Y_BOTTOM, 0.0), end_point=(0, Y_TOP, 0.0))
    k.smooth(body, 50)
    # The raised border along the edge (all round but the top edge's middle, where the visor sits).
    outline = plan_outline(BORDER_IN, spacing=0.8)
    path = []
    for u, y in outline:
        path.append(Vector((u, y, hull_top(u, y) + 0.05)))
    path.append(path[0])
    tube("border", path, [BORDER_RADIUS] * len(path), m["border"], segments=6, squash=0.75)
    return body


def plan_outline(inset, spacing=0.45):
    """The whole plan (both halves), counter-clockwise, `inset` inside the hull's edge."""
    right = [(u, y) for u, y in PLAN]
    whole = right + [(-u, y) for u, y in reversed(right[1:-1])]
    whole = ccw(whole)
    pts = resample(chaikin(whole, 2), spacing)
    out = []
    n = len(pts)
    for i in range(n):
        p0, p1 = Vector(pts[i - 1]), Vector(pts[(i + 1) % n])
        t = (p1 - p0).normalized()
        inward = Vector((-t.y, t.x))
        q = Vector(pts[i]) + inward * inset
        out.append((q.x, q.y))
    return out


# --- The armour plates ----------------------------------------------------------------------------------------

def brow(m):
    """The brow plate over the upper armour, from the shoulders down to the seam (rows 6-7)."""
    seam_y = 7.0
    outline = [(u, max(y, seam_y)) for u, y in plan_outline(BORDER_IN + 0.8, spacing=0.6) if y > seam_y + 0.05]
    pts = resample(chaikin(ccw(outline), 2), 0.6)
    facet("brow", pts, lambda x, y: hull_top(x, y) - 0.02, 0.75, m["brow"], rim=0.45, steps=2, dome=0.05,
          dome_rings=1, sink=0.4)


def brow_top(u, y):
    return hull_top(u, y) + (0.73 if y > 7.45 else 0.0)


def spine(m):
    """The strip of two ribs from the visor down to the middle window (rows 4-8), a groove between them."""
    for side in (-1, 1):
        u = side * 0.95
        line = [Vector((u, y, max(hull_top(u, y) + 0.3, brow_top(u, y) + 0.05))) for y in [10.6 - 5.5 * i / 14
                                                                                             for i in range(15)]]
        # Smooth the step where the strip leaves the brow.
        zs = [p.z for p in line]
        for _ in range(3):
            zs = [zs[0]] + [(zs[i - 1] + 2 * zs[i] + zs[i + 1]) / 4 for i in range(1, len(zs) - 1)] + [zs[-1]]
        line = [Vector((p.x, p.y, z)) for p, z in zip(line, zs)]
        tube(f"rib{side}", line, [0.78] * len(line), m["rib"], segments=10, squash=0.75)


def visor(m):
    """The visor window in the top edge (rows 1-3): blue glass in a teal frame."""
    base = lambda x, y: hull_top(x, min(y, 13.0)) - 0.1  # noqa: E731
    facet("visor_frame", resample(rounded_rect(-3.35, 3.35, 10.25, 13.6, 0.8), 0.5), base, 1.0, m["teal"], rim=0.35,
          steps=2, dome=0.0, dome_rings=1, sink=0.4)
    facet("visor_glass", resample(rounded_rect(-2.45, 2.45, 10.85, 13.1, 0.55), 0.45), base, 1.22, m["glass"],
          rim=0.25, steps=2, dome=0.08, dome_rings=1, sink=0.4)


def window(m):
    """The middle window (rows 9-12): a dark frame, two blue slats with a grey bar between them, a teal sill."""
    floor = lambda x, y: hull_top(0.0, y) - 0.05  # noqa: E731
    facet("window_frame", resample(rounded_rect(-2.75, 2.75, 0.85, 5.2, 0.7), 0.5), floor, 0.55, m["dark"], rim=0.3,
          steps=2, dome=0.0, dome_rings=1, sink=0.4)
    for name, y0, y1, mat, h in (("slat_top", 3.75, 4.75, "glass", 0.72), ("slat_low", 1.95, 2.95, "glass", 0.72),
                                 ("slat_bar", 2.95, 3.75, "bar", 0.62)):
        facet(name, resample(rounded_rect(-2.15, 2.15, y0, y1, 0.3), 0.45), floor, h, m[mat], rim=0.2, steps=2,
              dome=0.03, dome_rings=1, sink=0.3)
    sill = [Vector((u, 1.3, hull_top(u, 1.3) + 0.62)) for u in [-2.35 + 4.7 * i / 8 for i in range(9)]]
    tube("sill", sill, [0.42] * len(sill), m["teal"], segments=8, squash=0.75)


def chin(m):
    """The lighter chin plate below the window (rows 13-20), a little narrower towards its foot."""
    outline = [(-3.45, 0.55), (3.45, 0.55), (3.3, -3.4), (2.6, -6.15), (-2.6, -6.15), (-3.3, -3.4)]
    pts = resample(chaikin(ccw(outline), 2), 0.5)
    return facet("chin", pts, lambda x, y: hull_top(x, y) - 0.02, 0.85, m["chin"], rim=0.45, steps=3, dome=0.15,
                 dome_rings=2, sink=0.4)


def ports(m):
    """The dark ports round the lower half: sockets, dark dishes sunk in the armour."""
    specs = [(u, y, a, b, ang) for u, y, a, b, ang in PORTS] + [(-u, y, a, b, 180.0 - ang) for u, y, a, b, ang in PORTS]
    u, y, a, b = BOTTOM_PORT
    specs.append((u, y, a, b, 0.0))
    for i, (u, y, ra, rb, ang) in enumerate(specs):
        t = math.radians(ang)
        along = Vector((math.cos(t), math.sin(t)))
        across = Vector((-along.y, along.x))
        hole = [(u + along.x * rb * math.cos(s_) + across.x * ra * math.sin(s_),
                 y + along.y * rb * math.cos(s_) + across.y * ra * math.sin(s_))
                for s_ in [2 * math.pi * j / 14 for j in range(14)]]
        facet(f"port{i}", ccw(hole), lambda x, y: hull_top(x, y) - 0.1, 0.22, m["port"], rim=0.1, steps=1,
              dome=-0.06, dome_rings=1, sink=0.3)


def block(m):
    """The blue block at the point (rows 22-26), its top edge teal, a stud on its face."""
    outline = resample(rounded_rect(-3.1, 3.1, -13.05, -9.35, 0.7), 0.45)
    base = lambda x, y: hull_top(x, y) - 0.05  # noqa: E731
    # Its top slopes down towards the point, so that its face looks down the screen and up.
    blk = facet("block", outline, lambda x, y: base(x, y) + 0.45 * (y + 13.05) / 3.7, 0.9, m["block"], rim=0.35,
                steps=2, dome=0.05, dome_rings=1, sink=0.5)
    trim = [Vector((u, -9.75, base(u, -9.75) + 0.45 * 3.3 / 3.7 + 1.0))
            for u in [-2.75 + 5.5 * i / 8 for i in range(9)]]
    tube("trim", trim, [0.42] * len(trim), m["trim"], segments=8, squash=0.75)
    z = base(0.0, -11.5) + 0.45 * 1.55 / 3.7 + 0.95
    k.smooth(k.ellipsoid("stud", (0.0, -11.5, z), (0.48, 0.48, 0.3), m["stud"], 12, 6), 60)
    return blk


# --- Build ----------------------------------------------------------------------------------------------------

def build():
    options = k.args()
    outdir = options.get("outdir", os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "enemies"))
    k.reset()
    m = materials()
    hull(m)
    brow(m)
    spine(m)
    visor(m)
    window(m)
    chin(m)
    ports(m)
    block(m)
    for obj in bpy.context.scene.objects:
        if obj.type == "MESH":
            obj.data.transform(Matrix.Translation((AXIS_X, 0.0, 0.0)))
    used = {mat.name for o in bpy.context.scene.objects if o.type == "MESH" for mat in o.data.materials}
    print("== purple_shield (2 127): %d triangles, %d materials: %s" % (triangles(), len(used),
                                                                       ", ".join(sorted(used))))
    if "check" in options:
        k.check_silhouette(os.path.join(options["check"], "enemy_2.png"), 127)
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    path = os.path.join(outdir, "purple_shield.glb")
    k.export(path)
    print("%s: %d bytes" % (path, os.path.getsize(path)))
    if "preview" in options:
        k.preview(options["preview"] + "purple_shield")


if __name__ == "__main__":
    build()
