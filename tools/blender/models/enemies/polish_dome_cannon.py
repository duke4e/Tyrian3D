"""The brown dome with a heavy cannon of the asteroid levels (sheet D: sprite 245, the cannon, above sprite 283, the
dome, 2x2 each: one 24 x 56 picture; ground layer; ASTEROID1, ASTEROID2, ASTCITY and AST. CITY, enemies 287 and 288 of
episodes 1-3, AST ROCK, enemies 1041 and 1042 of episode 5; episode 6 does not use them), polished (2026-10-21; it
replaces wave3_j.py's dome_cannon_whole(), an ellipsoid with lathed black tubes). models.cfg: model dome_cannon_barrel
/ dome_cannon_dome ... origin (unchanged) and model dome_cannon_dome_281 enemies/dome_cannon_dome_281.glb origin (new);
sprite d 245 dome_cannon_barrel yaw=0 height=-4, sprite d 283 dome_cannon_dome yaw=0 height=-4, frame d 281
dome_cannon_dome_281. No other enemy (launched ones included) shows D 245, 281 or 283; none of them is another sprite's
pixels mirrored, turned or in other ramps.

The levels always place the cannon 28 pixels above the dome at the same x (event 6: ASTEROID1's, ASTEROID2's,
ASTCITY's and AST. CITY's dat5 -28 and 0, AST ROCK's -29 and -1), both on the ground layer; they are two enemies (the
cannon's armour 10, the dome's 16), so either can be shot away and leave the other. The dome's animation (283 six
times, 281, 283, 283, 281, then 283 ten times, over and over) flashes its lamps: 281 is 283 with the two pink lamps
orange and yellow (ramp 7 for ramp 4).

As the sprites and their 4x upscales draw it (the grey stone tiles round it are the map's ground, drawn into the
sprites, and the black to its lower right is its shadow on them: both left out):
- the dome (283's columns 0-20 of rows 0-16): brown (ramp 1), straight sided, its south end round, lit at its upper
  left; across its north end a red band (rows 0-3), in the band's middle a tan frame holding two pink lamps one above
  the other (columns 8-12 of rows 1-7); a seam down its south slope (column 10 of rows 8-15), lit, dark either side;
- out of its north side a bronze collar (245's columns 3-17 of rows 20-27), fluted (light and dark stripes along it),
  narrowing at its top (seven pixels wide at row 20);
- the cannon reaching up the screen from it: a dark cradle (columns 3-17 of rows 10-19, its left cheek lit at
  columns 3-6 of rows 14-19) through which the barrel's neck shows (columns 7-13): a grey ring lit at its left (rows
  14-16), a tan ring (row 13) and a red one (row 12); then the barrel's heavy shroud (columns 3-17 of rows 0-9), round,
  black, chrome-lit down its left (columns 6-7) with a glint at its front (column 11 of row 2), its front rounded.

Built whole and cut in two at y = 0 (polish_savara_boss.cut: the pieces keep the whole's shading across the cut and
each face its own winding; the cuts capped black), each piece moved to its sprite's centre and its parts joined
(polish_deli_boss.join). The dome is a solid over its plan (polish_ring_machine.relief()): a superellipsoid, straight
sided and round at its south end as the sprite draws it (its plan a superellipse of power 3, round in section), its
north end under the collar, a skirt below the ground; the band a strap standing proud over its north end, the seam a
rib down its south slope (dark either side), painted along smooth borders: its brown lit at the upper left (0x17),
shaded at the lower right (0x12), 0x15 between, as the sprite draws it; the lamps' frame a raised tan plate following
the dome, the lamps glass lenses with hotter middles, glowing a little (283: 0x48 / 0x4c at 0.2 / 0.3; 281: orange
0x78 / 0x7c at 0.45 / 0.6). The collar is turned about the cannon's axis, fluted (14 flutes), its flutes painted by
how they meet the light (0x19 lit, 0x17, 0x15, the grooves 0x12); the cradle a machined block (polish_machine_kit:
bevelled, a window cut through its top by an exact boolean) standing on the ground round the neck, dark steel, its
top and left cheek lit; the neck's rings turned parts (grey 0x08, lit at its left, tan 0xa5, red 0x43); the shroud a
turned part (its rear flange, its rounded front, a dark bore), painted by how its faces meet the light: black on the
right, steel, lit and chrome (0x02, 0x05, 0x08, 0x0b) towards the upper left, where the sprite draws its highlight.
The cannon's axis rises 5 degrees up the screen; the shroud is its highest part (z 14.1).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the ground (z = 0). The whole's
origin is the middle of the two sprites' shared edge: the cannon's column c, row r edges are (c - 12, 28 - r), the
dome's (c - 12, -r); the pieces are y 0..28 (D 245, moved down 14) and -28..0 (D 283, moved up 14). Drawn at their
origins (origin), on the ground layer 4 pixels up: height=-4 on both sprite lines sets the dome on the terrain (its
skirt reaches 1 pixel below it).

Replaces wave3_j.py's dome cannon: remove its section ("# --- D 245 above D 283: the dome cannon": dome_cannon_whole()
with its @whole("dome_cannon", (24, 56)) registration, dome_cannon_piece() and the two model("dome_cannon_...") lines)
and its lines in the docstring (and "[--whole dome_cannon --preview <prefix>]" in its usage; then wave3_j.py no longer
uses Vector or whole: drop them from its imports), and wave3_j_art.py's D281 (read by nothing). wave3_at_d.py imports
wave3_j.py (kit.quiet_import, for its shell ship): unaffected; wave3_j_kit.py's whole(), piece() and bake() stay
(wave3_j_rocks.py and other kits use them).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the whole's and each piece's
silhouette against the object's own pixels in enemy_D.png, the map's tiles and the shadow left out), --preview
<prefix>, --only <name,...>, --whole <file.glb> (the uncut whole as well), --stats 1.
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
import polish_deli_boss as db  # noqa: E402  (drop_unused, join)
from polish_k_pod import triangulate  # noqa: E402
from polish_ring_machine import ccw, relief  # noqa: E402
from polish_savara_boss import cut  # noqa: E402

AXIS_X = -1.5                   # the dome's and the cannon's middle (columns 10's middle)
LIGHT = Vector((-0.45, 0.45, 0.77)).normalized()   # the game's sun (from the upper left and above)

# --- The dome -------------------------------------------------------------------------------------------------------

# Its plan and shape: a dome over a superellipse (its centre, half-sizes across and along, the plan's power: straight
# sided, its south end round, as the sprite draws it; its north end under the collar), its top; its height at its
# edge, from which the skirt goes on down to DOME_BOTTOM.
DOME_CENTRE, DOME_HALF, DOME_POWER = (-1.5, -6.55), (10.5, 10.45), 3.0
DOME_H = 8.8
DOME_EDGE, DOME_BOTTOM = 0.25, -1.0
# The band across its north end (y from, to), how far it stands proud, its edges' rounding; the lamps' frame (a
# raised plate: x from, to; y from, to; corner radius, how proud); the lamps (x, y, radii in plan, height).
BAND = (-4.2, 0.15, 0.32, 0.25)
FRAME = (-4.25, 0.25, -8.15, -1.05, 1.1, 0.35)
LAMPS = [(-2.0, -2.75, 1.65, 1.15, 0.75), (-2.0, -6.45, 1.75, 1.3, 0.8)]
# The seam down the south slope: x, from y, to y, half-width, how proud; the darker lines either side.
SEAM = (-1.5, -8.0, -16.2, 0.42, 0.3)
SEAM_DARK = 0.95                # the dark strip either side of the seam: this close to its middle
# Paint: the brown by how the dome faces the light (thresholds: dark under, lit over).
DOME_SHADE = (0.6, 0.86)

# --- The cannon -----------------------------------------------------------------------------------------------------

# The axis: at y = 0 its height, and its rise (degrees) up the screen.
AXIS_Z, AXIS_RISE = 6.0, 5.0
# The collar (along the axis: y, radius), its vertical squash, its flutes (how many, how deep).
COLLAR = [(-1.2, 6.7), (1.0, 6.7), (4.4, 6.55), (5.6, 6.05), (6.6, 5.2), (7.4, 4.3), (8.2, 3.6)]
COLLAR_SQUASH = 0.62
FLUTES, FLUTE_DEPTH = 14, 0.055
# The cradle: x from, to; y from, to; its foot (in the ground, as the dome's skirt), its top over the axis, the bevel;
# its window (x from, to; y from, to; its floor under the axis).
CRADLE = (-9.0, 6.0, 8.4, 18.0, DOME_BOTTOM, 3.3, 0.45)
WINDOW = (-5.15, 2.15, 11.35, 16.05, 1.2)
# The neck and its rings (y from, to, radius, colour), the neck's radius.
NECK_R = 3.3
RINGS = [(11.4, 14.0, 3.62, "ring_grey"), (14.0, 15.0, 3.58, "tan"), (15.0, 16.0, 3.58, "ring_red")]
# The shroud (along the axis: y, radius), its vertical squash, the bore's radius.
SHROUD = [(17.7, 3.4), (17.9, 6.9), (18.15, 7.4), (18.85, 7.4), (19.15, 7.1), (25.4, 7.1), (25.65, 7.35),
          (26.35, 7.25), (26.95, 6.75), (27.4, 5.85), (27.72, 4.6), (27.85, 3.35), (27.6, 2.95), (25.5, 2.85)]
SHROUD_SQUASH = 0.8
SHROUD_SHADE = (0.4, 0.74, 0.93)   # black under, steel, lit, chrome over these

# The pieces: model, sprite, box (x0, x1, y0, y1) in the whole's coordinates.
PIECES = [("dome_cannon_barrel", 245, (-12.0, 12.0, 0.0, 28.0)), ("dome_cannon_dome", 283, (-12.0, 12.0, -28.0, 0.0))]
FRAME_281 = ("dome_cannon_dome_281", 281)
# The object's own pixels (the map's tiles and the shadow left out), per sprite row: (first column, last column).
OWN_245 = [(6, 15), (5, 15), (4, 16)] + [(3, 17)] * 17 + [(6, 14), (5, 15), (4, 16)] + [(3, 17)] * 5
OWN_283 = [(0, 20)] * 12 + [(1, 20), (1, 19), (2, 17), (3, 16), (3, 14)] + [None] * 11


def smoothstep(e0, e1, x):
    t = min(1.0, max(0.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


def axis_point(y):
    return Vector((AXIS_X, y, AXIS_Z + y * math.tan(math.radians(AXIS_RISE))))


def axis_dir():
    a = math.radians(AXIS_RISE)
    return Vector((0.0, math.cos(a), math.sin(a)))


# --- Materials --------------------------------------------------------------------------------------------------

def materials(lamps_hot=False):
    pal = k.level_palette()

    def mat(name, index, metallic=0.35, roughness=0.4):
        return k.material(name, palette=index, metallic=metallic, roughness=roughness)

    def glow(name, index, strength, roughness=0.2):
        return k.material(name, palette=index, metallic=0.0, roughness=roughness, emission=pal[index],
                          emission_strength=strength)
    m = {
        "brown_dark": mat("dcannon_brown_dark", 0x12, 0.35, 0.45),
        "brown": mat("dcannon_brown", 0x15, 0.4, 0.4),
        "bronze": mat("dcannon_bronze", 0x17, 0.55, 0.35),
        "brown_lit": mat("dcannon_brown_lit", 0x19, 0.55, 0.32),
        "red": mat("dcannon_red", 0x46, 0.3, 0.38),
        "red_dark": mat("dcannon_red_dark", 0x43, 0.3, 0.42),
        "tan": mat("dcannon_tan", 0xa5, 0.45, 0.35),
        "black": mat("dcannon_black", 0x02, 0.6, 0.35),
        "steel": mat("dcannon_steel", 0x05, 0.7, 0.3),
        "steel_lit": mat("dcannon_steel_lit", 0x08, 0.7, 0.26),
        "chrome": mat("dcannon_chrome", 0x0b, 0.75, 0.2),
    }
    m["ring_grey"] = m["steel_lit"]
    m["ring_red"] = m["red_dark"]
    if lamps_hot:
        m["lamp"] = glow("dcannon_lamp_hot", 0x78, 0.45)
        m["lamp_core"] = glow("dcannon_lamp_core_hot", 0x7c, 0.6)
    else:
        m["lamp"] = glow("dcannon_lamp", 0x48, 0.2)
        m["lamp_core"] = glow("dcannon_lamp_core", 0x4c, 0.3)
    return m


# --- The dome -------------------------------------------------------------------------------------------------------

def band_rise(y):
    y0, y1, proud, r = BAND
    return proud * smoothstep(y0 - r, y0 + r, y) * smoothstep(y1 + r, y1 - r, y)


def seam_field(x, y):
    """Positive on the seam: its half-width less the distance to its middle line (rounded at its ends)."""
    sx, y0, y1, hw, _ = SEAM
    t = min(max(y, y1), y0)
    return hw - math.hypot(x - sx, y - t)


def dome_q(x, y):
    """The superellipse's measure: 0 at the dome's middle, 1 on its edge."""
    (cx, cy), (a, b) = DOME_CENTRE, DOME_HALF
    return (abs(x - cx) / a) ** DOME_POWER + (abs(y - cy) / b) ** DOME_POWER


def dome_plan(samples=144):
    (cx, cy), (a, b) = DOME_CENTRE, DOME_HALF
    p = DOME_POWER
    pts = []
    for i in range(samples):
        t = 2 * math.pi * i / samples
        c, s_ = math.cos(t), math.sin(t)
        pts.append((cx + a * math.copysign(abs(c) ** (2 / p), c), cy + b * math.copysign(abs(s_) ** (2 / p), s_)))
    return pts


def dome_shell(x, y):
    """The dome's own surface (a superellipsoid: round in section), without the band and the seam."""
    q = min(1.0, dome_q(x, y))
    return DOME_EDGE + (DOME_H - DOME_EDGE) * math.sqrt(max(0.0, 1.0 - q ** (2.0 / DOME_POWER)))


def dome_top(x, y, d=None):
    """The dome's surface: the shell, the band proud over its north end, the seam down its south slope."""
    z = dome_shell(x, y) + band_rise(y) * smoothstep(0.96, 0.8, dome_q(x, y))
    s = seam_field(x, y)
    if s > 0.0:
        hw, proud = SEAM[3], SEAM[4]
        z += proud * math.sqrt(max(0.0, 1.0 - ((hw - s) / hw) ** 2))
    return z


def shade(x, y, eps=0.2):
    """How much the dome's shell faces the light, by its slope there."""
    gx = (dome_shell(x + eps, y) - dome_shell(x - eps, y)) / (2 * eps)
    gy = (dome_shell(x, y + eps) - dome_shell(x, y - eps)) / (2 * eps)
    return Vector((-gx, -gy, 1.0)).normalized().dot(LIGHT)


def dome(m):
    plan = ccw(dome_plan())

    def paint(x, y, d):
        if band_rise(y) > 0.16 and d > 0.5:
            return "red_dark" if y < BAND[0] + 0.45 else "red"
        if seam_field(x, y) > 0:
            return "brown_lit"
        if seam_field(x, y) > -SEAM_DARK + SEAM[3]:
            return "brown_dark"
        sh = shade(x, y)
        if sh > DOME_SHADE[1]:
            return "bronze"
        if sh < DOME_SHADE[0]:
            return "brown_dark"
        return "brown"

    borders = [(lambda x, y, d: band_rise(y), 0.16), (lambda x, y, d: y - BAND[0] - 0.45, 0.0),
               (lambda x, y, d: seam_field(x, y), 0.0), (lambda x, y, d: seam_field(x, y), -SEAM_DARK + SEAM[3]),
               (lambda x, y, d: shade(x, y), DOME_SHADE[0]), (lambda x, y, d: shade(x, y), DOME_SHADE[1])]
    mats = {key: m[key] for key in ("brown_dark", "brown", "bronze", "brown_lit", "red", "red_dark")}
    obj = relief("dome", [plan], lambda x, y, d: dome_top(x, y), mats, paint=paint, side="brown_dark",
                 bottom=DOME_BOTTOM, spacing=0.5, borders=borders, smooth_angle=55)
    return [obj], dome_top


def lamps(m, surface):
    """The tan frame on the band's middle (a raised plate following the dome) and its two lamps (glass lenses)."""
    x0, x1, y0, y1, r, proud = FRAME
    ring = mk.rounded_rect_ring(((x0 + x1) / 2, (y0 + y1) / 2), (x1 - x0) / 2, (y1 - y0) / 2, r, 0.0, 40)
    outline = [(p.x, p.y) for p in ring]
    plate = mk.wedge("lamp_frame", outline, 0.0, lambda x, y: surface(x, y) + proud, m["tan"],
                     bottom=lambda x, y: surface(x, y) - 0.6)
    mk.bevel(plate, 0.18, 2, 35)
    mk.shade(plate, 40)
    parts = [plate]
    for i, (lx, ly, rx, ry, h) in enumerate(LAMPS):
        base = surface(lx, ly) + proud - 0.25
        lens = mk.dome("lamp%d" % i, (lx, ly), (rx, ry, h), base, m["lamp"], 24, 6)
        # Its hot middle, a little towards the upper left (where the sprite draws it).
        core = mk.dome("lamp_core%d" % i, (lx - 0.25, ly + 0.15), (rx * 0.55, ry * 0.55, h * 0.45),
                       base + h * 0.62, m["lamp_core"], 16, 4)
        parts += [lens, core]
    return parts


# --- The cannon -----------------------------------------------------------------------------------------------------

def turned(name, profile, squash, mat, segments=40, flutes=0, depth=0.0):
    """A part turned about the cannon's axis: profile [(y along the axis, radius)], its sections squashed vertically;
    flutes: ridges along it (their depth a fraction of the radius)."""
    d = axis_dir()
    side = Vector((1.0, 0.0, 0.0))
    up = d.cross(side).normalized() * -1.0 if d.cross(side).z < 0 else d.cross(side).normalized()
    rings = []
    for y, r in profile:
        c = axis_point(y)
        ring = []
        for j in range(segments):
            a = 2 * math.pi * j / segments
            rr = r * (1.0 + depth * math.cos(flutes * a)) if flutes else r
            ring.append(c + side * math.sin(a) * rr + up * math.cos(a) * rr * squash)
        rings.append(ring)
    first, last = profile[0], profile[-1]
    obj = k.loft(name, rings, mat, start_point=axis_point(first[0]), end_point=axis_point(last[0]))
    return obj


def light_paint(obj, bands, keys, keep=None):
    """Paints faces by how they meet the light (bands: ascending thresholds, keys: one more than bands)."""
    def pick(c, n):
        if keep is not None and keep(c, n):
            return None
        v = n.dot(LIGHT)
        key = keys[0]
        for t, kk in zip(bands, keys[1:]):
            if v > t:
                key = kk
        return key
    slots = {}
    for poly in obj.data.polygons:
        key = pick(poly.center, poly.normal)
        if key is None:
            continue
        if key not in slots:
            slots[key] = mk.slot_of(obj, key)
        poly.material_index = slots[key]


def collar(m):
    """The fluted bronze collar round the cannon's root: its flutes' crests lit or not by the light, the grooves
    dark."""
    profile = []
    for (y0, r0), (y1, r1) in zip(COLLAR, COLLAR[1:]):
        n = max(1, int(math.ceil((y1 - y0) / 0.6)))
        for i in range(n):
            t = i / n
            profile.append((y0 + (y1 - y0) * t, r0 + (r1 - r0) * t))
    profile.append(COLLAR[-1])
    obj = turned("collar", profile, COLLAR_SQUASH, m["bronze"], 56, FLUTES, FLUTE_DEPTH)
    k.smooth(obj, 50)
    segments = 56
    slots = {}
    for poly in obj.data.polygons:
        band, j = divmod(poly.index, segments)
        if band >= len(profile) - 1:
            continue
        a = 2 * math.pi * (j + 0.5) / segments
        crest = math.cos(FLUTES * a)
        v = poly.normal.dot(LIGHT)
        key = ("brown" if v > 0.6 else "brown_dark") if crest < -0.5 else \
            "brown_lit" if v > 0.82 else "bronze" if v > 0.5 else "brown"
        if key not in slots:
            slots[key] = mk.slot_of(obj, m[key])
        poly.material_index = slots[key]
    return [obj]


def cradle(m):
    """The cradle round the neck: a bevelled block, a window cut through its top over the neck; dark steel, its top
    and its left cheek lit."""
    x0, x1, y0, y1, bottom, over, bev = CRADLE
    top_at = lambda x, y: axis_point(y).z + over  # noqa: E731
    body = mk.wedge("cradle", [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], bottom, top_at, m["black"])
    mk.bevel(body, bev, 3, 35)
    wx0, wx1, wy0, wy1, below = WINDOW
    window = mk.wedge("cradle_window", [(wx0, wy0), (wx1, wy0), (wx1, wy1), (wx0, wy1)], 0.0,
                      lambda x, y: top_at(x, y) + 3.0, m["black"], bottom=lambda x, y: axis_point(y).z - below)
    mk.boolean(body, window, "DIFFERENCE")
    mk.cleanup(body)
    mk.shade(body, 35)

    def pick(c, n):
        v = n.dot(LIGHT)
        inner = wx0 - 0.05 < c.x < wx1 + 0.05 and wy0 - 0.05 < c.y < wy1 + 0.05 and c.z < top_at(c.x, c.y) - 0.05
        if inner:
            return m["black"]
        if v > 0.85:
            return m["steel_lit"]
        if v > 0.55:
            return m["steel"]
        return m["black"]
    mk.paint(body, pick)
    return [body]


def neck(m):
    """The barrel's neck through the cradle, and its three rings in the window."""
    parts = [turned("neck", [(6.0, NECK_R), (18.2, NECK_R)], 0.92, m["black"], 32)]
    k.smooth(parts[0], 50)
    for i, (y0, y1, r, key) in enumerate(RINGS):
        prof = [(y0, NECK_R - 0.1), (y0 + 0.02, r - 0.12), (y0 + 0.15, r), (y1 - 0.15, r), (y1 - 0.02, r - 0.12),
                (y1, NECK_R - 0.1)]
        ring = turned("ring%d" % i, prof, 0.92, m[key], 40)
        k.smooth(ring, 50)
        if key == "ring_grey":
            light_paint(ring, [0.5, 0.85], [m["black"], m["steel"], m["steel_lit"]])
        parts.append(ring)
    return parts


def shroud(m):
    """The barrel's shroud: turned, its rear flange, its rounded front, a dark bore; black on its right, chrome-lit on
    its left."""
    obj = turned("shroud", SHROUD, SHROUD_SQUASH, m["black"], 48)
    k.smooth(obj, 40)
    bore_r = SHROUD[-3][1] + 0.05

    def keep(c, n):
        return (c - axis_point(c.y)).length < bore_r and c.y > 25.0   # the bore stays black
    light_paint(obj, SHROUD_SHADE, [m["black"], m["steel"], m["steel_lit"], m["chrome"]], keep)
    return [obj]


# --- Build ----------------------------------------------------------------------------------------------------------

def build_whole(lamps_hot=False):
    m = materials(lamps_hot)
    dome_parts, surface = dome(m)
    parts = dome_parts + lamps(m, surface) + collar(m) + cradle(m) + neck(m) + shroud(m)
    for obj in parts:
        mk.apply(obj)
    bpy.context.view_layer.update()
    return parts, m


def own_mask(rows):
    out = []
    for r in rows:
        row = [False] * 24
        if r is not None:
            for c in range(r[0], r[1] + 1):
                row[c] = True
        out.append(row)
    return out


def export_piece(whole, m, name, box, options, mask, label):
    out = mk.outdir(options)
    parts = [p for p in (cut(src, box, m["black"]) for src in whole) if p is not None]
    db.drop_unused(parts)
    mk.transform(parts, Matrix.Translation((-(box[0] + box[1]) / 2, -(box[2] + box[3]) / 2, 0)))
    bpy.context.view_layer.update()
    triangulate(parts)
    if "stats" in options:
        for obj in sorted(parts, key=lambda o: -mk.triangles([o])):
            print("    %-16s %6d" % (obj.name, mk.triangles([obj])))
    parts = [db.join(parts, name)]
    parts[0].data.name = name
    for src in whole:
        src.hide_render = True
    if mask is not None:
        mk.compare("%s (%s, its own pixels)" % (name, label), mk.coverage(parts, 24, 28), mask)
    bpy.context.scene.view_settings.view_transform = "Standard"
    mk.report(name, parts, os.path.join(out, name + ".glb"))
    if "preview" in options:
        mk.preview(options["preview"] + name, parts)
    for obj in parts:
        data = obj.data
        bpy.data.objects.remove(obj)
        if data.users == 0:
            bpy.data.meshes.remove(data)
    for src in whole:
        src.hide_render = False


def build():
    options = k.args()
    only = options["only"].split(",") if "only" in options else None
    check = "check" in options
    masks = {245: own_mask(OWN_245), 283: own_mask(OWN_283), 281: own_mask(OWN_283)} if check else {}
    for hot in (False, True):
        k.reset()
        whole, m = build_whole(hot)
        if not hot:
            if "stats" in options:
                for obj in sorted(whole, key=lambda o: -mk.triangles([o])):
                    print("    %-16s %6d" % (obj.name, mk.triangles([obj])))
            if check:
                both = masks[245] + masks[283]
                mk.compare("whole (D 245 above D 283, their own pixels)", mk.coverage(whole, 24, 56, (0.0, 0.0)),
                           both)
            if "preview" in options:
                mk.preview(options["preview"] + "dome_cannon_whole", whole, size=(24, 56), scale=12, distance=1.6)
            if "whole" in options:
                triangulate(whole)
                mk.export(whole, options["whole"])
            for name, sprite, box in PIECES:
                if not only or name in only:
                    export_piece(whole, m, name, box, options, masks.get(sprite), "D %d" % sprite)
        else:
            name, sprite = FRAME_281
            if not only or name in only:
                export_piece(whole, m, name, PIECES[1][2], options, masks.get(sprite), "D %d" % sprite)


if __name__ == "__main__":
    build()
