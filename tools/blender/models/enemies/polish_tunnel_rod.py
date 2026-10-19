"""?TUNNEL?'s mechanical rod lying on the ground, drawn from two sprites of sheet 5 (2x2 each): its upper half, 55
(knob, flanges, a cowl over two red lights), 28 pixels above its lower half, 93 (the ribbed tail with its pointed
end) (enemies 74 and 75 of episode 4, on the ground, the pairs at x 90 and 208; 56 of each), polished (2026-10-19;
it replaces wave1_b.py's rod_top() and rod_tail()). models.cfg: model rod_top / rod_tail ... origin; sprite 5 55
rod_top yaw=0, sprite 5 93 rod_tail yaw=0. Their animations (55 999, 93 999) only take them away when they fire.

The rod is built whole, its tail down the screen, and cut along the sprites' edge (y = 0 here) into the two pieces,
each moved so that its sprite's centre is its origin (base on the ground): drawn at their own places they meet
again, and the cut pieces keep the whole's shading across the cut (polish_redjet.py's method).

As the 4x upscales draw it (the whole 24 x 56 picture, its axis down column 11):
- a rounded knob at the top (rows 0-4 of 55, seven pixels across), grooved;
- a broad flange under it (rows 5-8, eleven across), its upper rim lit, and a narrow neck (rows 9-12);
- a cowl over the rod's shoulders (rows 13-19, seventeen across at its widest): a hood sloping down to its outer
  ends, its front cut into two bays either side of a keel down the middle; in the bays two red lights glow
  (rows 17-22, the left one white-hot at its middle, column 8 of row 19);
- the spine between the lights, a light ridge down its top, and a second flange (rows 24-26);
- in 93 a bright collar (row 2) between two dark grooves (rows 3 and 9), a segment, the ribbed part with the light
  ridge down its top (rows 10-13), a third flange (rows 14-16), and a bulb (rows 19-24) narrowing to the point
  (row 27), shallow flutes twisting round it.

The rod is a body turned round its axis (lying along y at the height AXIS_Z, its sections a little flatter than
round, SQUASH, so that it rests on its flanges); the cowl and the lights are reliefs over outlines traced from the
sprite (polish_ring_machine.relief). Colours: the sprite's greys (ramp 0) and reds (ramp 7, glowing).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera. The whole's
y = 0 is the edge between the sprites: 55's pixel (column, row) is (c - 12, 28 - r) (top()), 93's (c - 12, -r);
the axis runs along x = AXIS_X (column 11's middle).

Replaces wave1_b.py's rod_top() and rod_tail() (with ROD_AXIS_X, ROD_Z, ROD_SQUASH and their MODELS entries):
remove them so that they don't overwrite these models.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes of the
whole and of each piece against enemy_5.png), --preview <prefix> (the whole's and each piece's views).
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
import polish_machine_kit as mk  # noqa: E402
from polish_ring_machine import ccw, chaikin, relief, round_edge  # noqa: E402

AXIS_X, AXIS_Z = -0.5, 4.45
SQUASH = 0.82

# The pieces: (model, sprite, the box it covers in the whole (x0, x1, y0, y1)).
PIECES = [("rod_top", 55, (-12.0, 12.0, 0.0, 28.0)), ("rod_tail", 93, (-12.0, 12.0, -28.0, 0.0))]


def top(c, r):
    """A point of 55's pixel grid (column, row) in the whole's coordinates."""
    return (c - 12.0, 28.0 - r)


# --- The body turned round the axis ---------------------------------------------------------------------------
# Its radius in plan along y (a third of a pixel inside the sprites' outlines), from the tail's point up to the
# knob; steps where flanges, collars and grooves begin.
PROFILE = [
    (-27.7, 0.0), (-27.45, 0.5), (-26.9, 1.15), (-26.1, 1.85), (-25.3, 2.55), (-24.5, 3.15), (-23.5, 3.65),
    (-22.5, 3.92), (-21.5, 4.0), (-20.5, 3.9), (-19.7, 3.55), (-19.15, 3.0),                  # the bulb
    (-18.7, 2.85), (-17.4, 2.85),                                                             # rows 17-18
    (-17.15, 3.25), (-16.85, 4.1), (-16.45, 4.35), (-14.55, 4.35), (-14.15, 4.0), (-13.85, 3.0),  # the flange
    (-13.5, 3.05), (-10.6, 3.05),                                                             # the ribbed part
    (-10.3, 2.55), (-9.5, 2.35), (-8.85, 2.6),                                                # a groove
    (-8.6, 3.15), (-8.1, 3.35), (-4.9, 3.35), (-4.35, 3.15),                                  # the segment
    (-3.95, 2.55), (-3.5, 2.4), (-3.1, 2.6),                                                  # a groove
    (-2.95, 3.6), (-2.75, 4.4), (-2.25, 4.4), (-2.05, 3.6),                                   # the collar
    (-1.8, 3.0), (0.3, 3.15),
    (0.85, 3.4), (1.1, 4.8), (1.45, 5.3), (3.6, 5.3), (3.95, 4.8), (4.2, 3.0),                # the lower flange
    (4.5, 2.6), (8.0, 2.6), (8.5, 2.8), (15.0, 2.8),                                          # under the cowl
    (15.5, 2.7), (17.5, 2.9), (18.8, 3.1),                                                    # the neck
    (19.0, 3.3), (19.25, 4.8), (19.6, 5.3), (22.4, 5.3), (22.75, 4.8), (23.0, 3.4),           # the flange
    (23.3, 3.0), (24.0, 3.3), (25.0, 3.4), (26.0, 3.25), (26.8, 2.8), (27.4, 2.0), (27.75, 1.1), (27.9, 0.0)]
# The parts' colours along y: (y from, y to, key).
BANDS = [(-30.0, -19.15, "bulb"), (-17.15, -13.85, "light"), (-10.3, -8.85, "dark"), (-3.95, -3.1, "dark"),
         (-2.95, -2.05, "light"), (0.85, 4.2, "light"), (19.0, 23.0, "light"), (23.0, 30.0, "knob")]
# The flutes twisting round the bulb and the point: how many, how far along the axis one turns once, their
# depth (a share of the radius) and where they fade in.
FLUTES, LEAD, FLUTE_DEPTH, FLUTE_TOP = 3, 14.0, 0.11, (-19.6, -18.6)
FLUTE_PAINT = 0.55       # the flutes' dark floors: where they sink more than this share of their depth
# The light ridge down the top: (y from, y to).
RIDGES = [(-13.6, -10.2), (4.3, 8.8)]
# The grooves round the knob: (y, half-width).
KNOB_GROOVES = [(24.15, 0.22), (25.6, 0.2)]

# --- The cowl and the lights (outlines as (column, row) of 55) --------------------------------------------------
COWL_RIGHT = [(11.5, 12.3), (16.4, 12.8), (17.8, 13.8), (19.1, 14.9), (19.7, 16.4), (19.8, 18.5), (19.4, 19.9),
              (17.4, 20.1), (16.6, 18.5), (16.2, 16.8), (13.1, 16.8), (12.9, 19.4), (12.1, 20.5), (11.5, 20.6)]
COWL = COWL_RIGHT + [(23.0 - c, r) for c, r in reversed(COWL_RIGHT[1:-1])]   # symmetric about column 11's middle
COWL_TOP, COWL_FALL, COWL_RIM = AXIS_Z + 3.0, 0.024, 1.0   # its crest, how it falls to the sides, its edge's rounding
KEEL = (11.4, 7.6, 1.6)          # the keel falls this much from y 11.4 to its tip (y 7.6)
VENT_L = [(5.8, 16.3), (9.9, 16.3), (10.0, 23.0), (8.0, 23.2), (7.8, 20.2), (5.7, 19.9)]
VENT_R = [(23.0 - c, r) for c, r in VENT_L]
VENT_TOP = AXIS_Z + 0.9
HOT = [((8.5, 19.5), 0.75), ((14.5, 19.1), -0.1)]  # the lights' hot cores: (column, row) of 55, radius (the
                                                    # right one only warm, as the sprite's is dimmer)
WARM = 0.55                      # the warmer ring round each core


# --- Helpers --------------------------------------------------------------------------------------------------

def dense_profile():
    """PROFILE with points every half pixel between its steps (smooth slopes), the bulb finer."""
    out = []
    for (y0, r0), (y1, r1) in zip(PROFILE, PROFILE[1:]):
        step = 0.35 if y0 < -18.0 else 0.6
        count = max(1, int(math.ceil((y1 - y0) / step)))
        for i in range(count):
            t = i / count
            out.append((y0 + (y1 - y0) * t, r0 + (r1 - r0) * t))
    out.append(PROFILE[-1])
    return out


def radius(y):
    for (y0, r0), (y1, r1) in zip(PROFILE, PROFILE[1:]):
        if y0 <= y <= y1:
            return r0 + (r1 - r0) * (y - y0) / max(y1 - y0, 1e-9)
    return 0.0


def surface_z(y, dx=0.0):
    r = radius(y)
    return AXIS_Z + SQUASH * math.sqrt(max(r * r - dx * dx, 0.0))


def flute(y, a):
    """How far (0-1) the bulb's surface sinks at y and angle a: rounded grooves twisting round it."""
    if y > FLUTE_TOP[1]:
        return 0.0
    fade = 1.0 - mk.smoothstep(FLUTE_TOP[0], FLUTE_TOP[1], y)
    u = (a * FLUTES / (2 * math.pi) + y / LEAD) % 1.0
    return fade * max(0.0, math.sin(math.pi * min(u / 0.45, 1.0))) if u < 0.45 else 0.0


def plan(points):
    """An outline given as (column, row) points of 55, its corners rounded once."""
    return ccw(chaikin([top(c, r) for c, r in points], 1))


# --- The parts ------------------------------------------------------------------------------------------------

def body(m, segments=40):
    profile = dense_profile()
    rings = []
    for y, r in profile:
        ring = []
        for j in range(segments):
            a = 2 * math.pi * j / segments
            rr = max(r, 1e-3) * (1.0 - FLUTE_DEPTH * flute(y, a))
            ring.append(Vector((AXIS_X + rr * math.cos(a), y, AXIS_Z + SQUASH * rr * math.sin(a))))
        rings.append(ring)
    obj = k.loft("body", rings[1:-1], m["steel"], start_point=(AXIS_X, profile[0][0], AXIS_Z),
                 end_point=(AXIS_X, profile[-1][0], AXIS_Z))
    # The flutes' floors dark, cut in along the groove's contour.
    def groove(co):
        return flute(co.y, math.atan2((co.z - AXIS_Z) / SQUASH, co.x - AXIS_X))

    bm = bmesh.new()
    bm.from_mesh(obj.data)
    mk.split_along(bm, {v: groove(v.co) for v in bm.verts}, FLUTE_PAINT)
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
    bm.to_mesh(obj.data)
    bm.free()
    keys = ["steel"]
    for poly in obj.data.polygons:
        c = poly.center
        key = "steel"
        for y0, y1, band in BANDS:
            if y0 <= c.y <= y1:
                key = band
        if key == "bulb" and groove(c) > FLUTE_PAINT:
            key = "dark"
        if key not in keys:
            keys.append(key)
            obj.data.materials.append(m[key])
        poly.material_index = keys.index(key)
    return k.smooth(obj, 50)


def ridges(m):
    """The light ridge down the rod's top, a dark groove either side of it."""
    for i, (y0, y1) in enumerate(RIDGES):
        steps = max(4, int((y1 - y0) / 0.4))
        pts = [Vector((AXIS_X, y0 + (y1 - y0) * s / steps, 0)) for s in range(steps + 1)]
        for p in pts:
            p.z = surface_z(p.y) + 0.05
        rings = []
        for n, p in enumerate(pts):
            f = min(1.0, (p.y - y0) / 0.6, (y1 - p.y) / 0.6)
            f = max(math.sqrt(max(0.0, 1 - (1 - f) ** 2)), 0.15)
            rings.append(k.ring(p.y, 0.55 * f, 1.0, 12, z=p.z - 0.25, x=AXIS_X, top=0.25 + 0.4 * f, bottom=0.3))
        k.smooth(k.loft("ridge%d" % i, rings, m["light"]), 50)
        for side in (-1, 1):
            groove = [Vector((AXIS_X + side * 0.85, p.y, surface_z(p.y, 0.85) - 0.02)) for p in pts[1:-1]]
            mk.tube("ridge_groove%d%d" % (i, side), groove, 0.22, m["dark"], 6)


def knob(m):
    """Two dark grooves round the knob."""
    for n, (y, half) in enumerate(KNOB_GROOVES):
        r = radius(y)
        prof = [(y - half, r - 0.15), (y - half * 0.4, r + 0.04), (y + half * 0.4, r + 0.04), (y + half, r - 0.15)]
        k.smooth(k.lathe("knob_groove%d" % n, prof, m["dark"], 40, axis_x=AXIS_X, axis_z=AXIS_Z, squash=SQUASH), 40)


def cowl(m):
    """The hood over the rod's shoulders, sloping down to its outer ends, the keel falling to its tip."""
    k0, k1, drop = KEEL

    def crest(x, y):
        z = COWL_TOP - COWL_FALL * (x - AXIS_X) ** 2
        z -= drop * mk.smoothstep(k0, k1, y) * (1.0 - mk.smoothstep(1.6, 2.6, abs(x - AXIS_X)))
        return z

    def height(x, y, d):
        return crest(x, y) - COWL_RIM + COWL_RIM * round_edge(d, COWL_RIM)

    def paint(x, y, d):
        return "cowl_side" if d < 0.3 else "cowl"

    borders = [(lambda x, y, d: d, 0.3)]
    return relief("cowl", [plan(COWL)], height, m, paint=paint, side="cowl_side", bottom=0.6, borders=borders,
                  spacing=0.4, band=1.6)


def vents(m):
    """The red lights in the cowl's bays, white-hot at their cores."""
    hot = [(top(c, r), rad) for (c, r), rad in HOT]

    def heat(x, y):
        return max(rad - math.hypot(x - hx, y - hy) for (hx, hy), rad in hot)

    def paint(x, y, d):
        h = heat(x, y)
        return "vent_hot" if h > 0 else "vent_warm" if h > -WARM else "vent"

    for name, points in (("vent_l", VENT_L), ("vent_r", VENT_R)):
        relief(name, [plan(points)], lambda x, y, d: VENT_TOP - 0.5 + 0.5 * round_edge(d, 0.5), m, paint=paint,
               side="vent_side", bottom=0.6, borders=[(lambda x, y, d: heat(x, y), 0.0),
                                                      (lambda x, y, d: heat(x, y), -WARM)], spacing=0.35)


def materials():
    pal = k.level_palette()
    steel = dict(metallic=0.55, roughness=0.32)
    return {
        "steel": k.material("rod_steel", palette=0x08, **steel),
        "light": k.material("rod_light", palette=0x0b, metallic=0.6, roughness=0.26),
        "bulb": k.material("rod_bulb", palette=0x09, **steel),
        "knob": k.material("rod_knob", palette=0x09, **steel),
        "dark": k.material("rod_dark", palette=0x02, metallic=0.3, roughness=0.55),
        "cowl": k.material("rod_cowl", palette=0x09, **steel),
        "cowl_side": k.material("rod_cowl_side", palette=0x05, **steel),
        "vent": k.material("rod_vent", palette=0x75, metallic=0.1, roughness=0.35, emission=pal[0x74],
                           emission_strength=1.0),
        "vent_warm": k.material("rod_vent_warm", palette=0x77, metallic=0.05, roughness=0.32, emission=pal[0x77],
                                emission_strength=1.3),
        "vent_hot": k.material("rod_vent_hot", palette=0x7b, metallic=0.0, roughness=0.3, emission=pal[0x7b],
                               emission_strength=1.6),
        "vent_side": k.material("rod_vent_side", palette=0x72, metallic=0.1, roughness=0.4, emission=pal[0x72],
                                emission_strength=0.6),
    }


# --- Build ----------------------------------------------------------------------------------------------------

def whole_mask(sheet):
    return k.sprite_mask(sheet, 55) + k.sprite_mask(sheet, 93)


def build_whole():
    k.reset()
    m = materials()
    body(m)
    ridges(m)
    knob(m)
    cowl(m)
    vents(m)
    whole = mk.meshes()
    for obj in whole:
        mk.apply(obj)
    return whole, m


def build():
    options = k.args()
    outdir = mk.outdir(options)
    sheets = options.get("check")
    sheet = (os.path.join(sheets, "enemy_5.png") if os.path.isdir(sheets) else sheets) if sheets else None
    whole, m = build_whole()
    low, high = mk.bounds(whole)
    print("== whole rod (5 55 above 93): %d triangles, %d objects, %d materials, x %.2f..%.2f y %.2f..%.2f "
          "z %.2f..%.2f" % (mk.triangles(whole), len(whole), len(mk.materials_of(whole)), low.x, high.x, low.y, high.y,
                            low.z, high.z))
    if sheet:
        mk.compare("whole (5 55 above 93)", mk.coverage(whole, 24, 56), whole_mask(sheet))
    if "preview" in options:
        mk.preview(options["preview"] + "rod_whole", whole, size=(24, 56), scale=10, distance=1.6)
    for name, sprite, box in PIECES:
        pieces = [p for p in (mk.cut(src, box, m["dark"]) for src in whole) if p is not None]
        mk.transform(pieces, Matrix.Translation((0.0, -(box[2] + box[3]) / 2, 0.0)))
        for o in whole:
            o.hide_render = True
        if sheet:
            mk.compare("%s (5 %d)" % (name, sprite), mk.coverage(pieces, 24, 28), k.sprite_mask(sheet, sprite))
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
