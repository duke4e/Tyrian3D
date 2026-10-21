"""The grey claw ship of SURFACE, CORE, ICE EXIT, ROOST and COLLECTOR (sheet 3 sprites 8 and 10, 2x2: 24 x 21 pixels
in the 24 x 28 cell; top layer; its animation flickers the flames: 8 46 46 46 8 8, and 10 48 48 48 10 10), polished
(2026-10-21; it replaces wave2_h.py's twin_claw(), twin_claw_left() and twin_claw_right()). models.cfg: model
twin_claw_left / twin_claw_right (no origin: see below), sprite 3 8 twin_claw_left yaw=0, sprite 3 10 twin_claw_right
yaw=0, frame 3 46 twin_claw_left_46, frame 3 48 twin_claw_right_48.

Not two halves of one ship: the levels never put 3 8 and 3 10 side by side. They are two enemies (episode 4's 224
and 223, the same craft flying opposite ways): SURFACE (events at 1500-1590), CORE (300-590, 4300-4990) and ICE EXIT
(0-1990) start 223 (3 10) at the screen's left edge (x -24 or 0) and send it right (global moves of its links 10-15:
x speed 1, then x acceleration 8), and 224 (3 8) at the right edge (x 304-344), sent left; ROOST and COLLECTOR only
use 223, from the left. Each flies claws first. The red at the inner edge of each sprite (columns 21-23 of 3 8),
which wave2_h.py took for half of a core shared by the two halves, is the ship's exhaust flame, cut off by the
sprite's edge (in frame 46 it is a short orange spike). 3 10 is 3 8 mirrored left to right pixel for pixel, and 48
is 46 mirrored; no other sprite has their pixels, and no other enemy shows them. So the ship is built once, as 3 8
draws it (claws to the left), and mirrored for 3 10; one model per flame frame. The game centres sky and top
models in height (the old pieces' "origin" put their base on the layer: it is not needed for a whole ship).

As the sprite and its 4x upscale draw 3 8: two curved claws, mirror images of each other about the ship's middle
(row 13, y 0.5 here), reaching left from a hub at the right. Each claw is a glossy gunmetal horn (the grey ramp 0)
tapering to a point at the left edge (column 0), its outer edge arching from the tip up to row 3 (columns 8-17) and
down again to the hub, its inner edge straight along row 8; along it two ridges, the outer one broad (rows 4-5),
the inner one narrower and lighter (row 7), with a dark groove between them (row 6). At the root (columns 14-19) the
claw swells into a rounded knuckle (rows 6-10, the sprite's brightest greys), behind it a small heel (columns 21-22).
A dark spine (columns 18-20) joins the two knuckles, bowed a little to the rear like a bracket, a bright knob in its
middle (column 19 of row 13). In the dark mouth between the knuckles a tongue of fire starts and runs forward
between the claws to its point (columns 4-17 of rows 11-15; red at its edges, orange and yellow inside, hottest by
the hub); behind the spine the exhaust flame (columns 21-23 of rows 12-14). Frame 46 draws the tongue thinner, its
hot spot farther forward, and the exhaust as a short spike.

Built from lofts (tyrkit) as the upscale paints it, the claws curling into the hub: each claw two tapering horns
side by side along curved paths (horn(): their sections ellipses across the path and up, path and radii rounded
together), the broad outer ridge curling down at its root into the heel, the inner ridge swelling into the knuckle
and turning down from it as the spine to the ship's middle (one tube, dark below the knuckle, lit along its upper
left); the groove is the crease where the two horns meet, their sides facing it darker. A dark rounded crease fills
the notch between heel and knuckle; the knob sits where the two halves of the spine meet; a dark throat lies under
the fire's root and a dark nozzle behind the spine. The upper half is built and mirrored about y 0.5. The flames are
lofts whose plans follow the frame's fire pixels, their faces cut into bands of heat sampled from the sprite's
shades (polish_orb_red.band_split), each band glowing in its own palette colour, well under 1 (the game's bloom
adds to them). The flames lie within the hull's height, so every frame has the same bounds. Every mesh is
triangulated before the export (polish_k_pod.triangulate), so --check doesn't change the output.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; origin at the
sprite's centre (pixel 12, 14): column c is x = c + 0.5 - 12, row r is y = 13.5 - r.

Replaces wave2_h.py's twin claw ("# --- 3 8 / 3 10: the twin claw ship": CLAW_TOP, CLAW_FLAME, CLAW_MID_Y, CLAW_Z,
twin_claw(), twin_claw_left(), twin_claw_right()), its two MODELS entries and its docstring lines (sh and
smoothstep then go from its wave2_h_kit import; asteroid_lumpy stays): remove them so that they don't overwrite these
models.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each model's silhouette
against its sprite in enemy_3.png), --preview <prefix>, --only <name,...>.
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
from polish_orb_red import band_split  # noqa: E402
from polish_redjet import Curve  # noqa: E402

AXIS_Y = 0.5            # the ship's middle (row 13): the lower half is the upper one mirrored about it
ZC = 1.9                # the claws' middle plane

# The upper claw (v = y - AXIS_Y, out from the ship's middle): two horns side by side, the broad outer ridge and the
# narrow inner one, a groove where they meet; their middle lines from the tip to the root, (x, v, z over ZC, half-width
# in plan, half-height). The outer ridge curls down at its root into the heel (columns 20-22 of rows 5-8). The inner
# one runs along the claw's straight inner edge (row 8), swells into the knuckle at the root (columns 14-19 of rows
# 6-10) and turns down from it as the spine (columns 18-20, bowed to the rear) to the ship's middle, where the lower
# half's meets it under the knob. Their outlines run through the middles of the sprite's steps (row 7 at column 0, row
# 3 over columns 8-17, row 6 at column 23).
OUTER = [(-12.05, 5.3, 0.0, 0.12, 0.12), (-11.2, 6.0, 0.15, 0.52, 0.5), (-9.6, 6.75, 0.35, 0.9, 0.88),
         (-7.4, 7.5, 0.5, 1.25, 1.28), (-4.6, 8.12, 0.65, 1.58, 1.66), (-1.2, 8.6, 0.75, 1.78, 1.95),
         (2.4, 8.72, 0.8, 1.8, 2.05), (5.6, 8.5, 0.8, 1.72, 2.05), (8.2, 7.85, 0.72, 1.58, 1.9),
         (10.05, 7.0, 0.6, 1.45, 1.75), (10.85, 5.95, 0.45, 1.2, 1.5), (10.85, 5.0, 0.3, 0.95, 1.2)]
INNER = [(-11.75, 5.0, 0.0, 0.12, 0.1), (-10.6, 5.25, 0.1, 0.5, 0.45), (-8.4, 5.5, 0.2, 0.85, 0.75),
         (-5.0, 5.7, 0.3, 1.1, 1.0), (-1.0, 5.75, 0.35, 1.25, 1.15), (1.8, 5.65, 0.45, 1.4, 1.35),
         (4.5, 5.1, 0.75, 2.1, 1.85), (6.2, 4.3, 0.8, 2.08, 1.8), (7.1, 2.8, 0.66, 1.38, 1.38),
         (7.65, 1.35, 0.6, 1.3, 1.32), (7.8, 0.0, 0.6, 1.3, 1.32), (7.8, -0.45, 0.6, 1.3, 1.32)]
SPINE_V = 2.75                  # the inner ridge turns into the dark spine below this v (row 11)
# The dark crease under the heel, between it and the knuckle (column 20 of row 8, columns 19-23 of row 9).
CREASE = ((8.9, 4.3, -0.15), (1.5, 1.2, 0.55))
KNOB = ((7.7, 0.0, 1.5), (1.1, 1.05, 0.9))
# The dark mouth between the knuckles where the tongue of fire starts.
THROAT = ((5.1, 0.0, -0.6), (1.7, 2.3, 0.85))
# The nozzle behind the spine the exhaust comes out of: from, to along x, its radius, its height over ZC.
NOZZLE = (8.55, 9.45, 1.25, 0.45)

# The frames' fire: the shades (index & 15) of their ramp 7 pixels, rows 10-16 (columns 0-23).
FIRE = {
    8: ["........................",
        ".............76.........",
        ".........5578bb86....55.",
        ".....55669a86a9a97...956",
        "....455655544455.....76.",
        "..........444...........",
        "........................"],
    46: ["........................",
         "..........54............",
         ".......64665656......7..",
         ".....766789ab86646...8a8",
         "...........77658.....7..",
         "............65..........",
         "........................"],
}
FIRE_ROW0 = 10
TONGUE_COLUMNS = (3, 18)      # the tongue of fire between the claws; the exhaust is columns 20-23
TONGUE_ROOT = 6.4             # where the tongue starts, inside the mouth (x)
TONGUE_Z = 0.3                # its middle over ZC
EXHAUST_ROOT, EXHAUST_TIP, EXHAUST_Z = 8.7, 12.0, 0.45
# The bands of heat (lowest shade, palette index, emission strength).
FIRE_BANDS = [(-9.0, 0x75, 0.3), (5.6, 0x77, 0.4), (7.4, 0x79, 0.5), (8.9, 0x7a, 0.56), (10.2, 0x7b, 0.62)]

MODELS = [("twin_claw_left", 8, 8, False), ("twin_claw_left_46", 46, 46, False),
          ("twin_claw_right", 10, 8, True), ("twin_claw_right_48", 48, 46, True)]


def materials():
    pal = k.level_palette()

    def steel(name, index, metallic=0.55, roughness=0.3):
        return k.material(name, palette=index, metallic=metallic, roughness=roughness)
    m = {
        "outer": steel("twc_outer", 0x09),
        "inner": steel("twc_inner", 0x0a, 0.55, 0.26),
        "flank": steel("twc_flank", 0x06, 0.5, 0.34),
        "groove": steel("twc_groove", 0x03, 0.45, 0.45),
        "spine": steel("twc_spine", 0x03, 0.55, 0.26),
        "spine_light": steel("twc_spine_light", 0x07, 0.55, 0.22),
        "knob": steel("twc_knob", 0x0c, 0.55, 0.2),
        "deep": steel("twc_deep", 0x02, 0.2, 0.7),
    }
    for _, index, strength in FIRE_BANDS:
        m[("fire", index)] = k.material(f"twc_fire_{index:x}", palette=index, metallic=0.0, roughness=0.3,
                                        emission=pal[index], emission_strength=strength)
    return m


# --- Helpers -----------------------------------------------------------------------------------------------------

def place(obj):
    """Moves an object built at y = v (out from the ship's middle), z over ZC, to y = AXIS_Y + v, z."""
    obj.data.transform(Matrix.Translation((0.0, AXIS_Y, ZC)))
    return obj


def mirror_about(objects, matrix):
    """Copies of objects mirrored by matrix (normals flipped back outwards)."""
    out = []
    for obj in objects:
        copy = obj.copy()
        copy.data = obj.data.copy()
        copy.name = obj.name + "_m"
        bpy.context.scene.collection.objects.link(copy)
        copy.data.transform(matrix)
        copy.data.flip_normals()
        out.append(copy)
    return out


def mirror_in_place(objects, matrix):
    for obj in objects:
        obj.data.transform(matrix)
        obj.data.flip_normals()
        obj.data.update()
    return objects


# --- The claw ----------------------------------------------------------------------------------------------------

def horn(name, controls, mat, segments=18, iterations=2):
    """A horn along controls [(x, y, z, half-width in plan, half-height)]: its path and radii rounded together
    (Chaikin), elliptical sections across the path (in plan) and up, closed to points at its ends. Returns the
    object and its sections' middles (section i's vertices are i * segments ... (i + 1) * segments - 1)."""
    dense = mk.chaikin([tuple(c) for c in controls], iterations, closed=False)
    pts = [Vector(d[:3]) for d in dense]
    rings = []
    for i, p in enumerate(pts):
        a, b = pts[max(i - 1, 0)], pts[min(i + 1, len(pts) - 1)]
        t = Vector((b.x - a.x, b.y - a.y, 0.0)).normalized()
        side = Vector((-t.y, t.x, 0.0))
        r, h = max(dense[i][3], 0.04), max(dense[i][4], 0.04)
        rings.append([p + side * (math.cos(2 * math.pi * j / segments) * r) +
                      Vector((0, 0, math.sin(2 * math.pi * j / segments) * h)) for j in range(segments)])
    # A rounded cap at the root end: the last section shrinking on a quarter circle.
    t1 = (pts[-1] - pts[-2]).normalized()
    t1 = Vector((t1.x, t1.y, 0.0)).normalized()
    last, r, h = pts[-1], dense[-1][3], dense[-1][4]
    side = Vector((-t1.y, t1.x, 0.0))
    for q in (0.35, 0.65, 0.88):
        a = q * math.pi / 2
        c = last + t1 * (math.sin(a) * r * 0.8)
        rings.append([c + side * (math.cos(2 * math.pi * j / segments) * r * math.cos(a)) +
                      Vector((0, 0, math.sin(2 * math.pi * j / segments) * h * math.cos(a))) for j in range(segments)])
    t0 = (pts[1] - pts[0]).normalized()
    obj = k.loft(name, rings[1:], mat, start_point=pts[0] - t0 * 0.05, end_point=last + t1 * r * 0.8)
    centres = [sum(ring, Vector()) / segments for ring in rings[1:]]
    return k.smooth(obj, 60), centres


def paint_sections(obj, centres, segments, pick):
    """mk.paint by the section a face lies on: pick(the section's middle, the face's normal)."""
    slots = {}
    for poly in obj.data.polygons:
        section = min(poly.vertices) // segments
        mat = pick(centres[min(section, len(centres) - 1)], poly.normal)
        if mat is not None:
            if mat.name not in slots:
                slots[mat.name] = mk.slot_of(obj, mat)
            poly.material_index = slots[mat.name]


def claw(m):
    """The upper claw: the outer ridge curling down into the heel, the inner ridge swelling into the knuckle and
    turning down as the spine, the crease between heel and knuckle."""
    outer, _ = horn("outer", OUTER, m["outer"], 18)
    # Facing the groove (towards the middle), down, or steeply out: darker.
    mk.paint(outer, lambda c, n: m["groove"] if n.z < -0.2 else m["flank"] if n.z < 0.42 or
             (n.y < -0.45 and n.z < 0.75) else None)
    inner, centres = horn("inner", INNER, m["inner"], 16)

    def paint_inner(c, n):
        if c.y < SPINE_V:                         # the spine: dark, lit along its upper left
            if n.z < -0.2:
                return m["groove"]
            return m["spine_light"] if n.z > 0.4 and n.x < -0.15 else m["spine"]
        if n.z < -0.2:
            return m["groove"]
        # The side facing the groove darker, fading out over the knuckle.
        if n.z < 0.38 or (n.y > 0.5 + 0.15 * max(0.0, c.x + 1.0) and n.z < 0.8):
            return m["flank"]
        return None
    paint_sections(inner, centres, 16, paint_inner)
    (x, v, z), r = CREASE
    crease = k.smooth(k.ellipsoid("crease", (x, v, z), r, m["groove"], 16, 8), 60)
    return [outer, inner, crease]


def middle(m):
    """The parts on the ship's middle line: the knob, the dark mouth, the nozzle."""
    (x, v, z), r = KNOB
    knob = k.smooth(k.ellipsoid("knob", (x, v, z), r, m["knob"], 20, 10), 70)
    mk.paint(knob, lambda c, n: m["spine"] if n.z < 0.2 else None)
    (x, v, z), r = THROAT
    throat = k.smooth(k.ellipsoid("throat", (x, v, z), r, m["deep"], 24, 12), 80)
    x0, x1, rad, nz = NOZZLE
    prof = [(x0, rad * 0.8), (x0 + 0.3, rad), (x1 - 0.15, rad * 0.95), (x1, rad * 0.7), (x1 - 0.05, rad * 0.45)]
    rings = [[Vector((xx, rr * math.cos(2 * math.pi * j / 16), nz + rr * 0.85 * math.sin(2 * math.pi * j / 16)))
              for j in range(16)] for xx, rr in prof]
    nozzle = k.loft("nozzle", rings, m["deep"], start_point=(x0 - 0.1, 0.0, nz), end_point=(x1 - 0.3, 0.0, nz))
    k.smooth(nozzle, 60)
    return [knob, throat, nozzle]


# --- The fire ----------------------------------------------------------------------------------------------------

def fire_pixels(frame):
    """{(column, row): shade} of the frame's fire."""
    out = {}
    for i, line in enumerate(FIRE[frame]):
        for c, ch in enumerate(line):
            if ch != ".":
                out[(c, FIRE_ROW0 + i)] = int(ch, 16)
    return out


def shade_at(pixels, x, y, cool=3.6, blur=0.4):
    """The fire's shade at (x, y), interpolated between pixel middles (cooler outside the fire), blurred."""
    if blur > 0:
        return sum(shade_at(pixels, x + dx * blur, y + dy * blur, cool, 0.0)
                   for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1))) / 5
    fx, fy = x + 12.0 - 0.5, 13.5 - y
    c0, r0 = math.floor(fx), math.floor(fy)
    tx, ty = fx - c0, fy - r0
    total = 0.0
    for dc, wx in ((0, 1 - tx), (1, tx)):
        for dr, wy in ((0, 1 - ty), (1, ty)):
            total += wx * wy * pixels.get((c0 + dc, r0 + dr), cool)
    return total


def fire_loft(name, stations, z_mid, mat, tip, root):
    """A soft flame body through stations (x, y middle, half-width) along x, round in section (its height a share
    of its width), closed to points at tip and root."""
    rings = []
    for x, yc, hw in stations:
        hz = 0.6 * hw + 0.2
        ring = []
        for j in range(20):
            a = 2 * math.pi * j / 20
            ring.append(Vector((x, yc + hw * math.cos(a), z_mid + hz * math.sin(a))))
        rings.append(ring)
    if stations[0][0] > stations[-1][0]:
        rings = rings[::-1]
        tip, root = root, tip
    return k.smooth(k.loft(name, rings, mat, start_point=tip, end_point=root), 80)


def columns_of(pixels, c0, c1):
    """Per column of the fire: (x, the middle y, the half-width) of its pixels."""
    out = []
    for c in range(c0, c1 + 1):
        rows = [r for (cc, r) in pixels if cc == c]
        if not rows:
            continue
        top, bottom = 14.0 - min(rows), 13.0 - max(rows)
        out.append((c + 0.5 - 12.0, (top + bottom) / 2, (top - bottom) / 2))
    return out


def smoothed(stations, passes=2):
    for _ in range(passes):
        out = [stations[0]]
        for a, b, c in zip(stations, stations[1:], stations[2:]):
            out.append((b[0], (a[1] + 2 * b[1] + c[1]) / 4, (a[2] + 2 * b[2] + c[2]) / 4))
        out.append(stations[-1])
        stations = out
    return stations


def fire(m, frame):
    """The tongue of fire between the claws and the exhaust behind the spine, painted in bands of heat."""
    pixels = fire_pixels(frame)
    parts = []
    # The tongue: from inside the mouth forward to its point.
    cols = smoothed(columns_of(pixels, *TONGUE_COLUMNS))
    table = Curve([(x, yc, hw * 0.9) for x, yc, hw in cols])
    x0, x1 = cols[0][0], cols[-1][0]
    stations = [(x, *table(x)) for x in [x0 + (x1 - x0) * i / (2 * len(cols)) for i in range(2 * len(cols) + 1)]]
    root_y = stations[-1][1]
    stations.append((TONGUE_ROOT - 0.3, AXIS_Y + 0.15 * (root_y - AXIS_Y), stations[-1][2] * 0.9))
    first = stations[0]
    tip = (first[0] - 0.85, first[1] - 0.1, ZC + TONGUE_Z)
    root = (TONGUE_ROOT, AXIS_Y, ZC + TONGUE_Z)
    tongue = fire_loft("tongue", stations, ZC + TONGUE_Z, m[("fire", 0x75)], tip, root)
    parts.append(tongue)
    # The exhaust: out of the nozzle to the sprite's edge.
    cols = columns_of(pixels, 20, 23)
    stations = [(EXHAUST_ROOT + 0.25, AXIS_Y, 0.95)] + [(x, AXIS_Y + 0.5 * (yc - AXIS_Y), hw * 0.85)
                                                       for x, yc, hw in cols if x < EXHAUST_TIP - 0.2]
    exhaust = fire_loft("exhaust", stations, ZC + EXHAUST_Z, m[("fire", 0x75)], (EXHAUST_ROOT, AXIS_Y, ZC + EXHAUST_Z),
                        (EXHAUST_TIP, AXIS_Y, ZC + EXHAUST_Z))
    parts.append(exhaust)
    bands = [(lowest, m[("fire", index)]) for lowest, index, _ in FIRE_BANDS]
    for obj in parts:
        heat = []
        for v in obj.data.vertices:
            s = shade_at(pixels, v.co.x, v.co.y)
            heat.append(s + 0.8 * max(0.0, v.co.z - ZC - TONGUE_Z))   # its top a little hotter
        band_split(obj, heat, bands)
        k.smooth(obj, 80)
    return parts


# --- Building ----------------------------------------------------------------------------------------------------

def build_model(frame, mirror):
    k.reset()
    m = materials()
    upper = claw(m)
    for obj in upper:
        place(obj)
    lower = mirror_about(upper, Matrix.Translation((0, AXIS_Y, 0)) @ Matrix.Scale(-1, 4, (0, 1, 0)) @
                         Matrix.Translation((0, -AXIS_Y, 0)))
    mids = middle(m)
    for obj in mids:
        place(obj)
    parts = upper + lower + mids + fire(m, frame)
    if mirror:
        mirror_in_place(parts, Matrix.Scale(-1, 4, (1, 0, 0)))
    triangulate(parts)
    bpy.context.view_layer.update()
    return parts


def build():
    options = k.args()
    out = mk.outdir(options)
    only = set(options["only"].split(",")) if "only" in options else None
    for name, sprite, frame, mirror in MODELS:
        if only and name not in only:
            continue
        parts = build_model(frame, mirror)
        if "check" in options:
            sheet = os.path.join(options["check"], "enemy_3.png")
            mk.compare("%s (3 %d)" % (name, sprite), mk.coverage(parts, 24, 28), k.sprite_mask(sheet, sprite))
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        mk.report(name, parts, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, parts, distance=0.7)


if __name__ == "__main__":
    build()
