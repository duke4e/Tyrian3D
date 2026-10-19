"""The cage turret of the asteroid levels (sheet D sprite 275, 2x2: 24 x 28 pixels; ground layer; ASTEROID1,
ASTEROID2, ASTEROID?, ASTCITY, AST. CITY and AST ROCK, enemy 271; its animation 275 277 279 277 275), polished
(2026-10-19; it replaces wave3_j.py's cage_turret(), a block with boxes laid on for bars and capsules for lamps).
models.cfg: sprite d 275 cage_turret yaw=0, frame d 277 cage_turret_277, frame d 279 cage_turret_279 (no other enemy
shows sheet D's 277 or 279).

As the sprites and their 4x upscales draw it (the grey tiles round it are the map's, drawn into the sprite, and left
out here): a tan machine (ramp 10) whose top is a cage of thick rounded bars (columns 3-19 of rows 2-17): a block
across the back (rows 2-5), the side bars (columns 3 and 19), two inner bars (columns 7-8 and 14-15) and a cross bar
between them (rows 9-11), a bar across the front (row 16); between them deep windows on a dark steel inside (ramp
6): the upper middle one (columns 9-13 of rows 6-8) with a steel slat across it, the lower middle one (rows 12-15)
with a lens (its glint at column 11, row 14), and the side ones (columns 4-6 and 16-18 of rows 6-15; the darker tan
at their tops, rows 7-8, is the back block's face over them) with steel pipes running out through the side bars
(row 10) to two red lamps on its sides (columns 1-2 and 21-22 of rows 7-13). At the back two steel knobs and a tan
stub between them (columns 5-16 of rows 0-1); in front a lower tan chin (rows 17-19) round a steel collar (columns
9-13 of rows 18-19), and out of it the gun, short and stout (columns 8-14 of rows 20-26), pointing down the screen
and up a little, so that its mouth shows: a dark red bore (columns 10-12 of rows 24-25). The frames fire it: in 277
the lamps light up (to 7b) and the bore glows (to 7d), in 279 brighter (the lamps white in their middles, 7f; the
muzzle's glow spilling over its lip, rows 23-27).

Built as a CAD modeller would: the body a rounded block, its top edge rounded, the windows cut deep into it with
exact booleans (the bars are what is left), the bars' edges rounded, the windows' floors the dark steel inside; the
lens a glass dome in a steel ring; the pipes, the lamps (red glass capsules in steel caps, glowing hottest in a spot
on their middles, up and out), the collar and the gun turned parts; the gun's bore and lip and the lamps take the
frame's colours and glow. One model per frame, the same shapes (279 adds a flash swelling out of the bore). The body
is symmetric about the sprite's column 11 (x = -0.5); the lamps are where the sprite draws them (columns 1-2 and
21-22, so symmetric about x = 0).

Origin at the sprite's centre (pixel 12, 14); +X right, +Y up the sprite, +Z up from the ground (z = 0); column c's
left edge is x = c - 12, row r's top edge y = 14 - r. Tall enough (TOP, more than 7.4) for the game to set it on the
ground (it centres ground models in height on the ground enemies' layer, 4, and lifts them to 0.3 when they would
reach lower).

Replaces wave3_j.py's cage_turret() and LAMP_Z (its @model("cage_turret", [(D, 275, True)]) registration;
wave3_j_art.py's D275 and D279 are not used by it): remove them so that they don't overwrite these models.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each frame's silhouette
against the turret's own pixels, the map's tiles round it left out), --preview <prefix>, --only <name,...>.
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_orb_red import band_split  # noqa: E402

AXIS_X = -0.5
# The body: x0, x1, y0, y1 (columns 3-19, rows 2-17), corner radius; its top, the top edge's rounding; the windows'
# floors (the steel inside) and the rounding of the bars' edges.
BODY = (-9.3, 8.3, -4.0, 12.0, 1.8)
TOP, TOP_BEVEL = 7.6, 1.25
WINDOW_FLOOR, BAR_BEVEL = 3.8, 0.45
# The windows: x0, x1, y0, y1, corner radius (the bars are what is left between them).
WINDOWS = [
    (-3.0, 2.0, 5.0, 8.4, 0.5),     # the upper middle one (columns 9-13, rows 6-8)
    (-3.0, 2.0, -2.1, 2.0, 0.6),    # the lower middle one, the lens (rows 12-15)
    (-8.1, -5.0, -2.1, 8.4, 0.6),   # the left one (columns 4-6, rows 6-15), the top block's front face over it
    (4.0, 7.1, -2.1, 8.4, 0.6),     # the right one (columns 16-18)
]
SLAT = (6.1, 0.7, 0.55)             # a steel slat across the upper window: y, height above the floor, radius
LENS = (AXIS_X, -0.05, 1.5, 1.15)   # centre x, y, radius, height above the window's floor
GLINT = (-0.45, 0.45, 0.42)         # the lens' glint: from its middle (x, y), radius (column 11, row 14)
# The pipes: their height above the window's floor, radius, y (row 10); the lamps: x, from y to y (rows 7-13),
# height, radius.
PIPE_Z, PIPE_R, PIPE_Y = 1.05, 0.72, 3.5
LAMPS = [(-10.0, -0.1, 7.1), (10.0, -0.1, 7.1)]
LAMP_Z, LAMP_R = 3.5, 1.28
# At the back: a lower block behind the body, the stub on it, two steel knobs (columns 5-16 of rows 0-1).
BACK = (-6.4, 5.4, 10.5, 14.0, 5.6)            # x0, x1, y0, y1, top
STUB = (AXIS_X, 14.6, 4.6, 1.45)               # x, the far end's y, height of its axis, radius
KNOBS = [(-4.0, 12.9), (3.0, 12.9)]
# In front: the chin (x0, x1, y0, y1, top; columns 5-17, rows 17-19), the collar round the gun (its centre y, radius,
# thickness), the gun: its axis from the collar, rising GUN_RISE, its profile (distance along it, radius; a little
# flatter than round, GUN_FLAT) up to its mouth, the mouth's bore.
CHIN = (-7.0, 6.0, -6.8, -3.0, 5.2)
COLLAR = (-5.3, 2.55, 0.6)
GUN_START = Vector((AXIS_X, -5.0, 2.85))
GUN_RISE = math.radians(15.0)
GUN = [(0.0, 2.2), (0.5, 2.6), (1.5, 3.1), (2.8, 3.35), (4.2, 3.3), (5.4, 3.0), (6.4, 2.5), (7.0, 1.95)]
GUN_FLAT = 0.92
BORE_R = 1.3

# The frames: (model, sprite, the lamps' (palette index, glow) at their ends, round their middles and in their
# middles, the bore's, the muzzle's lip's, a flash in the muzzle (palette index, glow) or None).
FRAMES = [
    ("cage_turret", 275, [(0x72, 0.45), (0x74, 0.6), (0x76, 0.8)], (0x71, 0.35), None, None),
    ("cage_turret_277", 277, [(0x73, 0.7), (0x77, 1.1), (0x7a, 1.6)], (0x7b, 1.8), (0x76, 1.0), None),
    ("cage_turret_279", 279, [(0x75, 1.0), (0x79, 1.5), (0x7e, 2.4)], (0x7e, 2.6), (0x79, 1.5), (0x7b, 2.2)),
]

# The turret's own pixels (the map's tiles round it left out), by rows: (first row, last row, [(first column, last
# column), ...]).
OWN = [(0, 1, [(5, 16)]), (2, 2, [(4, 17)]), (3, 4, [(3, 18)]), (5, 6, [(2, 19)]), (7, 7, [(2, 19), (21, 21)]),
       (8, 12, [(1, 19), (21, 22)]), (13, 13, [(2, 19), (21, 21)]), (14, 16, [(2, 19)]), (17, 17, [(2, 19)]),
       (18, 19, [(5, 17)]), (20, 20, [(6, 16)]), (21, 25, [(8, 14)]), (26, 26, [(9, 13)])]


def materials(frame):
    glow = k.level_palette()

    def mat(name, index, metallic=0.45, roughness=0.35, strength=0.0, alpha=None):
        if strength > 0:
            return k.material(name, palette=index, metallic=metallic, roughness=roughness, emission=glow[index],
                              emission_strength=strength, alpha=alpha)
        return k.material(name, palette=index, metallic=metallic, roughness=roughness, alpha=alpha)
    _, _, lamps, bore, lip, flash = frame
    m = {
        "tan": mat("cage_tan", 0xaa, 0.25, 0.4),
        "tan_top": mat("cage_tan_top", 0xac, 0.25, 0.36),
        "tan_dark": mat("cage_tan_dark", 0xa7, 0.2, 0.45),
        "inside": mat("cage_inside", 0x62, 0.6, 0.4),
        "steel": mat("cage_steel", 0x67, 0.75, 0.25),
        "steel_light": mat("cage_steel_light", 0x6a, 0.75, 0.2),
        "lens": mat("cage_lens", 0x69, 0.2, 0.05, 0.3),
        "glint": mat("cage_glint", 0x6d, 0.1, 0.05, 0.8),
        "lamp": mat(f"cage_lamp_{lamps[0][0]:x}", lamps[0][0], 0.05, 0.15, lamps[0][1]),
        "lamp_mid": mat(f"cage_lamp_mid_{lamps[1][0]:x}", lamps[1][0], 0.05, 0.15, lamps[1][1]),
        "lamp_core": mat(f"cage_lamp_core_{lamps[2][0]:x}", lamps[2][0], 0.05, 0.15, lamps[2][1]),
        "bore": mat(f"cage_bore_{bore[0]:x}", bore[0], 0.1, 0.4, bore[1]),
    }
    m["lip"] = mat(f"cage_lip_{lip[0]:x}", lip[0], 0.1, 0.3, lip[1]) if lip else m["tan_top"]
    if flash:
        m["flash"] = mat(f"cage_flash_{flash[0]:x}", flash[0], 0.0, 0.3, flash[1])
    return m


def rect(x0, x1, y0, y1, r, segments=48):
    ring = mk.rounded_rect_ring(((x0 + x1) / 2, (y0 + y1) / 2), (x1 - x0) / 2, (y1 - y0) / 2, r, 0.0, segments)
    return [(p.x, p.y) for p in ring]


def inside(window, x, y, grow=0.0):
    x0, x1, y0, y1, _ = window
    return x0 - grow < x < x1 + grow and y0 - grow < y < y1 + grow


# --- The body and its cage -----------------------------------------------------------------------------------------

def body(m):
    """The body: a rounded block, its top edge rounded; the windows cut deep into it (the bars are what is left),
    the bars' edges rounded; the windows' floors the steel inside, their walls darker tan."""
    x0, x1, y0, y1, r = BODY
    obj = mk.prism("body", rect(x0, x1, y0, y1, r, 64), 0.0, TOP, m["tan"])
    mk.bevel(obj, TOP_BEVEL, 4, 30)
    cutters = [mk.prism(f"window{i}", rect(*w), WINDOW_FLOOR, TOP + 5.0, m["inside"]) for i, w in enumerate(WINDOWS)]
    mk.boolean(obj, cutters, "DIFFERENCE")
    mk.cleanup(obj)
    mk.bevel(obj, BAR_BEVEL, 3, 50)
    mk.shade(obj, 35)

    def pick(c, n):
        if any(inside(w, c.x, c.y, 0.05) for w in WINDOWS) and c.z < TOP - BAR_BEVEL - 0.1:
            return m["inside"] if n.z > 0.8 else m["tan_dark"]
        if n.z > 0.55 and c.z > TOP - 1.0:
            return m["tan_top"]
        return None
    mk.paint(obj, pick)
    # Inside: a steel slat across the upper window.
    wx0, wx1, _, _, _ = WINDOWS[0]
    y, h, sr = SLAT
    slat = mk.tube("slat", [(wx0 - 0.3, y, WINDOW_FLOOR + h), (wx1 + 0.3, y, WINDOW_FLOOR + h)], sr,
                   m["steel_light"], 12)
    k.smooth(slat, 50)
    # The back: a lower block behind it, the stub reaching back, the steel knobs.
    bx0, bx1, by0, by1, btop = BACK
    back = mk.prism("back", rect(bx0, bx1, by0, by1, 1.2, 40), 0.0, btop, m["tan"])
    mk.bevel(back, 0.5, 3, 30)
    mk.shade(back, 35)
    mk.paint(back, lambda c, n: m["tan_top"] if n.z > 0.6 else None)
    sx, sy, sz, sr = STUB
    stub = mk.tube("stub", [(sx, by0 + 0.5, sz), (sx, sy - 0.5, sz), (sx, sy, sz)], sr, m["tan"], 18,
                   radii=[sr, sr, sr * 0.7])
    k.smooth(stub, 50)
    mk.paint(stub, lambda c, n: m["tan_top"] if n.z > 0.5 else None)
    for i, (x, y) in enumerate(KNOBS):
        knob = mk.lathe(f"knob{i}", [(1.5, btop - 0.3), (1.5, btop + 0.35), (1.2, btop + 0.9), (0.6, btop + 1.2),
                                     (0.01, btop + 1.28)], (x, y), m["steel_light"], 20)
        k.smooth(knob, 55)


def lens(m):
    """The lens in the lower middle window: a glass dome in a steel ring, a glint on its upper left."""
    x, y, r, h = LENS
    z = WINDOW_FLOOR
    ring = mk.lathe("lens_ring", [(r + 0.15, z - 0.05), (r + 0.55, z + 0.25), (r + 0.5, z + 0.6), (r + 0.05, z + 0.65),
                                  (r - 0.05, z + 0.3)], (x, y), m["steel"], 28)
    k.smooth(ring, 50)
    profile = [(r, z + 0.1)] + [(r * math.cos(a), z + 0.3 + h * math.sin(a))
                                for a in (math.radians(d) for d in (0, 20, 40, 58, 74, 86))] + [(0.01, z + 0.3 + h)]
    dome = mk.lathe("lens", profile, (x, y), m["lens"], 32)
    k.smooth(dome, 60)
    gx, gy, gr = GLINT
    mk.paint(dome, lambda c, n: m["glint"] if math.hypot(c.x - x - gx, c.y - y - gy) < gr and n.z > 0.5 else None)


def pipes_and_lamps(m):
    """The pipes from the side windows out through the side bars to the lamps; the lamps: red glass capsules in steel
    caps on the body's sides."""
    for i, (lx, ly0, ly1) in enumerate(LAMPS):
        side = 1 if lx > 0 else -1
        window = WINDOWS[3] if side > 0 else WINDOWS[2]
        x_in = window[0] if side > 0 else window[1]
        z_in = WINDOW_FLOOR + PIPE_Z
        x_bar = BODY[1] if side > 0 else BODY[0]
        pts = [(x_in - side * 0.3, PIPE_Y, z_in), (x_bar + side * 0.3, PIPE_Y, z_in),
               (lx - side * 0.7, PIPE_Y, LAMP_Z + 0.6), (lx, PIPE_Y, LAMP_Z + 0.2)]
        pipe = mk.smooth_tube(f"pipe{i}", [p + (PIPE_R,) for p in pts], m["steel_light"], 12, 2)
        k.smooth(pipe, 60)
        collar = mk.tube(f"collar{i}", [(x_bar - side * 0.1, PIPE_Y, z_in), (x_bar + side * 0.45, PIPE_Y, z_in)],
                         PIPE_R + 0.3, m["steel"], 14)
        k.smooth(collar, 40)
        # The lamp, glowing hottest in a spot on its middle, up and out (cut along its contours).
        ts = [0.0, 0.06, 0.14, 0.22, 0.3, 0.38, 0.44, 0.5, 0.56, 0.62, 0.7, 0.78, 0.86, 0.94, 1.0]
        ys = [ly0 + (ly1 - ly0) * t for t in ts]
        radii = [LAMP_R * (0.7 + 0.32 * math.sin(math.pi * t) ** 0.5) for t in ts]
        lamp = mk.tube(f"lamp{i}", [(lx, y, LAMP_Z) for y in ys], LAMP_R, m["lamp"], 20, radii=radii)
        hot = Vector((lx + side * 0.45 * LAMP_R, (ly0 + ly1) / 2, LAMP_Z + 0.85 * LAMP_R))
        reach = Vector((2.2, 3.4, 2.2))
        values = [1 - Vector(((v.co.x - hot.x) / reach.x, (v.co.y - hot.y) / reach.y,
                              (v.co.z - hot.z) / reach.z)).length for v in lamp.data.vertices]
        band_split(lamp, values, [(-9.0, m["lamp"]), (0.3, m["lamp_mid"]), (0.62, m["lamp_core"])])
        k.smooth(lamp, 60)
        for j, y in enumerate((ly0, ly1)):
            inward = 1 if j == 0 else -1
            cap = mk.tube(f"lamp_cap{i}{j}", [(lx, y - inward * 0.35, LAMP_Z), (lx, y + inward * 0.45, LAMP_Z)],
                          LAMP_R * 0.85, m["steel"], 16)
            k.smooth(cap, 40)


def front(m):
    """The chin, the collar and the gun: a stout rounded barrel, its mouth a lip round a bore (they take the frame's
    glow)."""
    x0, x1, y0, y1, top = CHIN
    chin = mk.prism("chin", rect(x0, x1, y0, y1, 1.6, 40), 0.0, top, m["tan"])
    mk.bevel(chin, 1.0, 3, 30)
    mk.shade(chin, 35)
    mk.paint(chin, lambda c, n: m["tan_top"] if n.z > 0.6 else None)
    d = Vector((0.0, -math.cos(GUN_RISE), math.sin(GUN_RISE)))
    side = Vector((1.0, 0.0, 0.0))
    up = side.cross(d).normalized()
    if up.z < 0:
        up = -up
    seg = 28

    def ring(t, r):
        c = GUN_START + d * t
        return [c + (side * math.cos(2 * math.pi * j / seg) + up * GUN_FLAT * math.sin(2 * math.pi * j / seg)) * r
                for j in range(seg)]
    collar_c, collar_r, collar_t = COLLAR
    t_collar = (GUN_START.y - collar_c) / math.cos(GUN_RISE)
    collar = mk.tube("collar", [tuple(GUN_START + d * (t_collar - collar_t)),
                                tuple(GUN_START + d * (t_collar + collar_t))], collar_r, m["steel"], 28)
    k.smooth(collar, 40)
    rings = [ring(t, r) for t, r in GUN]
    end = GUN[-1][0]
    # The mouth: the lip turns in to the bore and down it.
    rings += [ring(end - 0.05, BORE_R + 0.3), ring(end - 0.2, BORE_R), ring(end - 1.6, BORE_R * 0.9)]
    gun = k.loft("gun", rings, m["tan"], start_point=tuple(GUN_START - d * 0.2),
                 end_point=tuple(GUN_START + d * (end - 1.6)))
    k.smooth(gun, 50)

    def pick(c, n):
        t = (Vector(c) - GUN_START).dot(d)
        radial = (Vector(c) - (GUN_START + d * t)).length
        if t > end - 1.7 and radial < BORE_R + 0.05:
            return m["bore"]
        if t > end - 0.45:
            return m["lip"]
        if n.z > 0.75:
            return m["tan_top"]
        return None
    mk.paint(gun, pick)
    return d, end


def flash(m, d, end):
    """279's flash: a glowing bulb swelling out of the bore."""
    centre = GUN_START + d * (end - 0.45)
    bulb = k.ellipsoid("flash", tuple(centre), (BORE_R * 0.95, 0.9, BORE_R * 0.95 * GUN_FLAT), m["flash"], 18, 10)
    # Turned so that its short axis (y) lies along the gun's.
    turn = Matrix.Translation(centre) @ Matrix.Rotation(-GUN_RISE, 4, "X") @ Matrix.Translation(-centre)
    bulb.data.transform(turn)
    k.smooth(bulb, 60)


def own_mask():
    mask = [[False] * 24 for _ in range(28)]
    for r0, r1, spans in OWN:
        for r in range(r0, r1 + 1):
            for c0, c1 in spans:
                for c in range(c0, c1 + 1):
                    mask[r][c] = True
    return mask


def build():
    options = k.args()
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    for frame in FRAMES:
        name, sprite = frame[0], frame[1]
        if only and name not in only:
            continue
        k.reset()
        m = materials(frame)
        body(m)
        lens(m)
        pipes_and_lamps(m)
        d, end = front(m)
        if "flash" in m:
            flash(m, d, end)
        parts = mk.meshes()
        for obj in parts:
            mk.apply(obj)
        bpy.context.view_layer.update()
        if "check" in options:
            mk.compare("%s (D %d, its own pixels)" % (name, sprite), mk.coverage(parts, 24, 28), own_mask())
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        mk.report(name, parts, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, parts)


if __name__ == "__main__":
    build()
