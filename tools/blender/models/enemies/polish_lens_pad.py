"""The grey lens pad of TORM and BONUS (sheet J sprite 77, 2x2: 24 x 28 pixels; enemy 749 of episode 2, ground layer,
each one alone; its animation 77 79 81 81 81 79 79 79 79 79 77 plays as it fires) and its damaged look (J 41, which the
game shows once the pad is shot down to its dlevel), polished (2026-10-21; it replaces wave3_m_ground.py's lens_pad(), a
pillow block with a hoop and an ellipsoid lens, and wave3_ap_torm.py's lens_pad_damaged, built from it). models.cfg:
model lens_pad / lens_pad_79 / lens_pad_81 / lens_pad_damaged enemies/lens_pad*.glb origin; sprite j 77 lens_pad yaw=0
height=-4; frame j 79 lens_pad_79; frame j 81 lens_pad_81 (no other enemy shows J 79 or 81); sprite j 41 lens_pad_damaged
yaw=0 height=-4. No other sprite has their pixels mirrored, turned or in other ramps.

As the sprite and its 4x upscale draw it (the pad fills columns 3-20 of rows 15-26, the cell's lower half; the dark
green pixels round it, 0x20-0x23, and row 27 are the foliage's shadow, the map's): a squat grey puck, its top a thick
rounded rim (columns 3-20 of rows 15-23; lit at its back left, 0x0b-0x0d, mid grey 0x08-0x09 round it, its front face
darker, 0x04-0x07, a light spot at its right, 0x0b) round a green lens set in it (columns 8-15 of rows 17-21: ramp 12,
brightest above its middle, 0xcc-0xcf, a dark streak across its lower part and its lower edge, 0x21-0x23, as the upscale
draws it: a glossy lens with a dark slit); under the rim a dark groove (row 24, 0x03-0x04) and the base's side (row 25,
0x02-0x09, lighter to the right), black where it meets the ground (row 26). The frames: 79 and 81 are 77's pad drawn 1
and 2 pixels lower (81's foot cut off by the cell's edge: the pad sinks into the ground), the lens brighter (79: 0xc1-0xcf,
the streak gone; 81: 0xc3-0xcf, bright all over); 79 and 77 again as it rises. One model per frame: lens_pad (77),
lens_pad_79 (the pad 1 pixel lower) and lens_pad_81 (2 pixels lower), each with its lens' own colours and glow. The
damaged look (J 41): the same pad blackened by fire (0x01), grey left only where the sprite keeps it (the rim's left
and back, bits of its front: 0x04-0x0c), its lens smashed flat, dark glass with green splinters glowing in it
(0xc0-0xc9, where the sprite draws them).

Built for the game's slanted camera as the sprite lays the pad out: seen from straight above it covers the sprite's
pixels; its back (up the screen) is steep, its front a sloping apron, so that the camera sees the rim's front face, the
groove and the base as the sprite draws them. The pad is a loft of ovals (each a superellipse with its own depth up and
down the screen) through a profile from its foot round the rim's bulge, over its crest and down into the socket; the
lens a glossy dome in the socket, cut along smooth contours (polish_orb_red.band_split) into bands of its brightness,
which glow in their own green (0.1-0.6, the game's bloom adds), the streak a dark arc across its lower part (in 77).
The greys follow the sprite's: the rim's top light grey (the game's sun lights its back left, where the sprite does),
its side darker below its widest line, the groove dark, the foot black.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the ground (z = 0); origin at the
sprite's centre (pixel 12, 14): column c is x = c + 0.5 - 12, row r is y = 13.5 - r. The pad's middle is x = 0; its top
oval's middle y = -5.5 (the lens, rows 17-21); its foot reaches y = -13 (row 26) at the front.

Where it stands: drawn at its origin (models.cfg origin), height=-4 sets its foot on the terrain (as the other polished
ground models of TORM do: the window block, the jaw guns); the frames sink into it.

Replaces wave3_m_ground.py's lens_pad(): its section ("# --- J 77: the lens pad", the @model("lens_pad", [(J, 77, True)])
registration and lens_pad()) and lens_pad's paragraph in its docstring; and wave3_ap_torm.py's lens pad: its section
("# --- J 77 -> 41: the lens pad": the @w.model("lens_pad_damaged", [(J, 41, True)]) registration and
lens_pad_damaged()) and its docstring paragraph (the gun's damaged look stays: it uses ground.gun_whole and
ground.GUN_ORIGIN); and the pixels only those read: wave3_m_art.py's J77 (wave3_ap_torm.py reads ground.art.J77 for the
pad only) and wave3_ap_art.py's J77_DMG. wave3_at_j.py (quiet_import("wave3_m_ground")) uses the eye orb only.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each frame's silhouette
against enemy_J.png), --preview <prefix>, --only <name,...>.
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
from polish_machine_kit import k, smoothstep  # noqa: E402
from polish_orb_red import band_split  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402

# The frames: (model, sprite, how far the pad is sunk, the lens' bands: (lowest brightness, palette index, glow)).
FRAMES = [
    ("lens_pad", 77, 0.0, [(-9.0, 0x23, 0.06), (0.1, 0xc1, 0.14), (0.3, 0xc3, 0.2), (0.48, 0xc6, 0.28),
                           (0.66, 0xc9, 0.36), (0.82, 0xcc, 0.45)]),
    ("lens_pad_79", 79, 1.0, [(-9.0, 0xc1, 0.16), (0.12, 0xc3, 0.22), (0.3, 0xc5, 0.3), (0.48, 0xc8, 0.38),
                              (0.66, 0xcb, 0.46), (0.82, 0xce, 0.54)]),
    ("lens_pad_81", 81, 2.0, [(-9.0, 0xc4, 0.26), (0.12, 0xc7, 0.34), (0.3, 0xca, 0.42), (0.48, 0xcc, 0.48),
                              (0.66, 0xce, 0.55), (0.82, 0xcf, 0.6)]),
]

# The pad's profile from its foot (outside, z = 0) round the rim and over its crest into the socket: (z, half-width,
# y of its front edge (down the screen), y of its back edge, power of the oval). The foot's apron runs down to row 26
# at the front; the back is steep (row 15).
PROFILE = [
    (0.0, 8.45, -13.0, -1.55, 2.6),
    (0.7, 8.55, -12.65, -1.5, 2.6),
    (1.65, 8.45, -12.0, -1.42, 2.6),  # the base's top
    (2.05, 8.1, -11.55, -1.38, 2.6),  # the groove
    (2.45, 8.2, -11.35, -1.35, 2.6),
    (3.05, 8.75, -11.1, -1.3, 2.7),   # the rim's bulge
    (3.75, 9.05, -10.8, -1.18, 2.8),
    (4.45, 9.1, -10.45, -1.08, 2.8),  # the rim's widest
    (5.05, 8.85, -10.0, -1.05, 2.8),
    (5.55, 8.3, -9.55, -1.15, 2.7),
    (5.9, 7.4, -9.15, -1.45, 2.6),    # the crest
    (5.98, 6.4, -8.9, -1.85, 2.5),
    (5.78, 5.55, -8.6, -2.3, 2.4),
    (5.3, 5.0, -8.35, -2.62, 2.3),    # the socket's lip
    (4.75, 4.7, -8.2, -2.8, 2.25),
    (4.2, 4.45, -8.05, -2.95, 2.2),   # the socket's wall
    (3.8, 4.1, -7.85, -3.15, 2.2),    # its floor's edge
]
FLOOR = (0.0, -5.5, 3.7)              # the socket floor's middle (the loft's end)
# The bands of the profile's rows the greys follow (index of the first row of each part).
GROOVE_ROWS = (2, 4)                  # rows 2-3: the groove
TOP_ROW = 7                           # from the rim's widest ring up: its top (lighter), below it its side
SOCKET_ROW = 13                       # from here in: the socket

# The damaged look (J 41): its pixels (columns 2-21 of rows 15-27, palette indices; ".." none): ramp 0 greys, the
# lens' green splinters (ramp 12) and dark glass (ramp 2).
DAMAGED = [
    ".. .. .. .. .. 01 01 01 01 01 01 01 01 01 01 .. .. .. .. ..",
    ".. .. .. 01 01 09 04 01 01 0b 08 08 08 08 06 01 01 .. .. ..",
    ".. .. 01 08 0c 0b 04 c0 22 c2 01 01 20 06 04 02 01 01 .. ..",
    ".. 01 07 0a 0c 06 c0 c1 c9 22 01 01 01 22 01 01 02 01 01 ..",
    ".. 01 06 08 07 01 20 20 c5 01 01 01 c4 c0 01 01 03 03 01 ..",
    ".. 01 01 02 01 01 20 01 23 01 21 c4 c7 c1 01 01 02 05 01 ..",
    ".. 01 01 01 01 01 07 01 01 01 22 01 21 01 01 01 01 08 01 ..",
    ".. 01 01 01 02 08 05 07 07 07 01 08 0a 02 01 01 01 0a 01 ..",
    ".. 01 01 01 09 04 05 05 05 03 01 07 03 08 01 01 01 08 01 ..",
    ".. .. 01 01 06 03 04 02 02 01 01 05 01 01 05 01 01 01 .. ..",
    ".. .. .. 01 01 02 04 05 05 04 01 04 06 07 09 01 01 .. .. ..",
    ".. .. .. 01 01 01 01 01 01 01 01 01 01 01 01 01 01 .. .. ..",
    ".. .. .. 01 04 01 .. 01 04 01 01 01 01 .. 01 02 01 .. .. ..",
]
DAMAGED_ROW, DAMAGED_COL = 15, 2
# Its greys (the sprite's shade blurred, cut into these bands: lowest shade, palette index), its lens squashed to this
# share of its height, its splinters (the green pixels blurred above SPLINTER: dim and bright, their glow).
BURNT = [(-9.0, 0x01), (2.2, 0x03), (3.9, 0x05), (5.6, 0x07), (7.3, 0x09)]
SMASHED = 0.45
SPLINTER = 0.32
SPLINTER_MATS = [(0xc2, 0.15), (0xc6, 0.3)]

# The lens: its middle, radii (x, y, z); the bright spot (its middle in the top view and falloff), the dark streak in
# 77 (an arc: its middle, radius, half-width, how dark, its span either side of straight down, degrees).
LENS = ((0.0, -5.5, 3.85), (4.3, 2.75, 1.6))
SPOT = ((-0.3, -4.8), (3.6, 2.4))
STREAK = ((0.6, -3.4), 3.3, 0.55, 0.9, 52.0)


def materials():
    def grey(name, index, metallic=0.35, roughness=0.34):
        return k.material(name, palette=index, metallic=metallic, roughness=roughness)
    return {
        "foot": grey("lpad_foot", 0x02, 0.3, 0.6),
        "base": grey("lpad_base", 0x05, 0.35, 0.45),
        "groove": grey("lpad_groove", 0x03, 0.3, 0.5),
        "wall": grey("lpad_wall", 0x08),
        "top": grey("lpad_top", 0x0a, 0.35, 0.3),
        "socket": grey("lpad_socket", 0x04, 0.3, 0.45),
        "floor": grey("lpad_floor", 0x01, 0.2, 0.6),
    }


def lens_materials(bands):
    pal = k.level_palette()
    return [(lowest, k.material(f"lpad_lens_{index:x}", palette=index, metallic=0.1, roughness=0.08,
                                emission=pal[index], emission_strength=strength))
            for lowest, index, strength in bands]


def oval(z, hw, yf, yb, power, segments=96):
    """A superellipse at height z: half-width hw, from yf (front, down the screen) to yb (back); counter-clockwise."""
    cy, hf, hb = (yf + yb) / 2, (yb - yf) / 2, (yb - yf) / 2
    pts = []
    for j in range(segments):
        a = 2 * math.pi * j / segments
        u, v = mk.superellipse_point(a, power)
        pts.append(Vector((hw * u, cy + (hb if v > 0 else hf) * v, z)))
    return pts


def pad(m, sink):
    rings = [oval(z - sink, hw, yf, yb, p) for z, hw, yf, yb, p in PROFILE]
    fx, fy, fz = FLOOR
    obj = k.loft("pad", rings, m["top"], start_point=(0.0, (PROFILE[0][2] + PROFILE[0][3]) / 2, -sink),
                 end_point=(fx, fy, fz - sink))
    k.smooth(obj, 50)
    n = len(rings[0])
    for name in ("foot", "base", "groove", "wall", "socket", "floor"):
        mk.slot_of(obj, m[name])
    slots = {mk.slot_of(obj, m[name]): name for name in m}
    index = {name: s for s, name in slots.items()}

    def pick(poly):
        row = poly.index // n
        c = poly.center
        if poly.index >= (len(rings) - 1) * n:      # the caps: the foot's underside, the socket's floor
            return "floor" if c.z - (-sink) > 1.0 else "foot"
        if row >= SOCKET_ROW:
            return "socket" if row < len(rings) - 2 else "floor"
        if row == 0:
            return "foot"
        if GROOVE_ROWS[0] <= row < GROOVE_ROWS[1]:
            return "groove"
        if row < GROOVE_ROWS[0]:
            return "base"
        # The rim's side below its widest ring, its top above it (the game's sun lights its back left, as the sprite's
        # 0x0b-0x0d there).
        return "wall" if row < TOP_ROW else "top"
    for poly in obj.data.polygons:
        poly.material_index = index[pick(poly)]
    return obj


def lens(bands, sink, streak):
    """The glossy lens in the socket: an ellipsoid (its lower part inside the pad), cut into bands of brightness."""
    (cx, cy, cz), (rx, ry, rz) = LENS
    obj = k.ellipsoid("lens", (cx, cy, cz - sink), (rx, ry, rz), None, 48, 24)
    (sx, sy), (fx, fy) = SPOT
    (ax, ay), radius, half, dark, span = STREAK

    def value(p):
        u, v = (p.x - sx) / fx, (p.y - sy) / fy
        b = 0.95 * math.exp(-0.8 * (u * u + v * v))
        top = (p.z - (cz - sink)) / rz
        b *= smoothstep(-0.2, 0.7, top)                 # darker down its sides, where it meets the socket
        if streak:
            d = math.hypot(p.x - ax, p.y - ay)
            ang = math.degrees(math.atan2(p.y - ay, p.x - ax))
            along = 1.0 - smoothstep(span - 14.0, span + 4.0, abs(((ang + 90.0) + 180.0) % 360.0 - 180.0))
            b -= dark * along * math.exp(-((d - radius) / half) ** 2)
            b -= 0.45 * (1.0 - smoothstep(cy - 2.3, cy - 1.3, p.y)) * (p.y < cy)   # its lower edge dark
        return b
    band_split(obj, [value(v.co) for v in obj.data.vertices], bands)
    k.recalc_normals(obj)
    return k.smooth(obj, 80)


def damaged_fields():
    """The damaged sprite's greys (shade, blurred; the burnt black 1) and its splinters (1 where green, blurred), as
    samplers at whole coordinates."""
    import numpy as np
    from polish_rock_arch import fill_outside
    grey = np.full((28, 24), np.nan)
    green = np.zeros((28, 24))
    green_shade = np.zeros((28, 24))
    for i, line in enumerate(DAMAGED):
        for j, tok in enumerate(line.split()):
            if tok == "..":
                continue
            v, r, c = int(tok, 16), DAMAGED_ROW + i, DAMAGED_COL + j
            if v >> 4 == 0xc:
                green[r, c], green_shade[r, c], grey[r, c] = 1.0, v & 15, 1.0
            elif v >> 4 == 0:
                grey[r, c] = v & 15
            else:
                grey[r, c] = 1.0
    grey = fill_outside(grey)

    def blur(a, sigma=0.6):
        r = 2
        kernel = np.exp(-0.5 * (np.arange(-r, r + 1) / sigma) ** 2)
        kernel /= kernel.sum()
        for axis in (0, 1):
            p = np.pad(a, [(r, r) if ax == axis else (0, 0) for ax in (0, 1)], mode="edge")
            a = sum(w * np.take(p, range(i, i + a.shape[axis]), axis=axis) for i, w in enumerate(kernel))
        return a
    grey, green = blur(grey), blur(green)

    def at(a, x, y):
        u, v = x + 12.0 - 0.5, 13.5 - y
        c0, r0 = int(math.floor(u)), int(math.floor(v))
        fu, fv = u - c0, v - r0
        def px(r, c):
            return a[min(max(r, 0), 27), min(max(c, 0), 23)]
        return ((1 - fu) * (1 - fv) * px(r0, c0) + fu * (1 - fv) * px(r0, c0 + 1) + (1 - fu) * fv * px(r0 + 1, c0) +
                fu * fv * px(r0 + 1, c0 + 1))
    return (lambda x, y: at(grey, x, y)), (lambda x, y: at(green, x, y))


def prune(obj):
    """Drops the material slots no face uses any more (the faces' indices moved to match)."""
    mesh = obj.data
    used = sorted({p.material_index for p in mesh.polygons})
    mats = [mesh.materials[i] for i in used]
    remap = {old: new for new, old in enumerate(used)}
    indices = [remap[p.material_index] for p in mesh.polygons]
    mesh.materials.clear()
    for mat in mats:
        mesh.materials.append(mat)
    mesh.polygons.foreach_set("material_index", indices)
    mesh.update()
    return obj


def build_damaged():
    """The pad blackened, its greys where the damaged sprite keeps them; the lens smashed flat, dark with splinters."""
    k.reset()
    m = materials()
    obj = pad(m, 0.0)
    grey, green = damaged_fields()
    burnt = {index: k.material(f"lpad_burnt_{index:x}", palette=index, metallic=0.25, roughness=0.6)
             for _, index in BURNT}

    def pick(c, n):
        s = grey(c.x, c.y)
        if n.z < -0.5:
            s = min(s, 2.0)
        index = BURNT[0][1]
        for lowest, i in BURNT:
            if s >= lowest:
                index = i
        return burnt[index]
    mk.paint(obj, pick)
    prune(obj)
    # The lens, squashed down onto its foot, dark glass, its splinters glowing.
    (cx, cy, cz), (rx, ry, rz) = LENS
    glass = k.ellipsoid("lens", (cx, cy, cz), (rx, ry, rz * SMASHED), None, 48, 24)
    dark = k.material("lpad_glass", palette=0x20, metallic=0.2, roughness=0.15)
    pal = k.level_palette()
    sparks = [k.material(f"lpad_splinter_{i:x}", palette=i, metallic=0.1, roughness=0.1, emission=pal[i],
                         emission_strength=strength) for i, strength in SPLINTER_MATS]
    band_split(glass, [green(v.co.x, v.co.y) for v in glass.data.vertices],
               [(-9.0, dark), (SPLINTER, sparks[0]), (SPLINTER + 0.25, sparks[1])])
    k.recalc_normals(glass)
    k.smooth(glass, 80)
    return triangulate([obj, glass])


def build_frame(name, sink, bands, streak):
    k.reset()
    m = materials()
    parts = [pad(m, sink), lens(lens_materials(bands), sink, streak)]
    return triangulate(parts)


def mask_of(sheet, sprite):
    """The sprite's own pixels: the foliage's shadow round it (ramp 2 pixels on its outline) and row 27 (the ground
    under it) left out; the lens' dark streak (ramp 2 inside it) kept."""
    from sprite_profile import sprite_indices
    idx = sprite_indices(sheet, sprite)
    h, w = len(idx), len(idx[0])

    def at(r, c):
        return idx[r][c] if 0 <= r < h and 0 <= c < w else None

    def ground(r, c):
        v = idx[r][c]
        return v >> 4 == 2 and any(at(r + dr, c + dc) is None for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)))
    return [[idx[r][c] is not None and r < 27 and not ground(r, c) for c in range(w)] for r in range(h)]


def build():
    options = k.args()
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    for name, sprite, sink, bands in FRAMES + [("lens_pad_damaged", 41, 0.0, None)]:
        if only and name not in only:
            continue
        parts = build_damaged() if sprite == 41 else build_frame(name, sink, bands, sprite == 77)
        bpy.context.view_layer.update()
        if "check" in options:
            sheet = os.path.join(options["check"], "enemy_J.png")
            sys.path.insert(0, os.path.join(HERE, "..", ".."))
            mk.compare("%s (J %d, the pad's own pixels)" % (name, sprite), mk.coverage(parts, 24, 28),
                       mask_of(sheet, sprite))
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        mk.report(name, parts, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, parts, distance=0.6)


if __name__ == "__main__":
    build()
