"""The grey sentry post of the asteroid levels (sheet S sprite 277, 2x2: 24 x 28 pixels; ground layer; ASTEROID1,
ASTEROID2, ASTEROID?, ASTCITY, AST. CITY, GREY MOON; enemies 325 and 1566; its animation 277 277 277 125 125 277
277 11), polished (2026-10-19; it replaces wave3_u.py's green_lamp_bunker(), a block with a heightfield half dome
and a green bar). models.cfg: sprite s 277 green_lamp_bunker yaw=0 glow=7:0.2:201:0:-10.5 (the lamp's light),
frame s 125 green_lamp_bunker_125, frame s 11 green_lamp_bunker_11.

As the 4x upscale draws it: at the back a squat grey head (columns 4-19 of rows 0-6) whose flat top carries a
visor, a dark frame round a window (columns 9-14 of rows 1-5) where a green lamp shines; against the head's front
a big rounded shield of grey armour bulging down the screen to the ground (columns 4-18 of rows 7-14, a half disc
seen from above, lit along its left edge); two pipes leave the head over the shield's crown, run down its face
and on along the ground to flanges (columns 10 and 12, rows 7-23), and a third leaves the shield's foot on the
right (column 16, rows 14-22). Rivets round the shield's foot, bolts beside the visor and straps on the pipes are
added (the sprite is too small for them).

The rubble round it is the map's ground: the asteroid maps lay a wrecked post there (ASTEROID1's tile 385, under
every one of these), and the 3D view erases the pixels the sprite shares with it (assets/terrain/<map>.era), so
the model is the post alone, standing on z = 0; the dark patch right of it and under the shield's front (columns
17-22 of rows 5-22, rows 15-22) is its shadow, which the game casts itself.

The animation only works the lamp: in 277 its lower half glows dim green under the grey glass (rows 4-5), in 125
the whole window blazes light green (rows 2-5), in 11 it is out (grey glass). One model per frame, the same
geometry with the window's materials changed: green_lamp_bunker (277), green_lamp_bunker_125 and
green_lamp_bunker_11 (frames that change only colours share their bounds, so the game places them alike).

Origin at the sprite's centre (pixel 12, 14); +Y up the sprite, +Z up from the ground (z = 0).

Replaces wave3_u.py's green_lamp_bunker() and grey_mats() (and wave3_u_art.py's BUNKER and BUNKER_ON, which
nothing else uses): remove them so that they don't overwrite these models.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouette against
the post's own pixels, written below), --preview <prefix>.
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402

# The post's own pixels in S 277 (the rubble and the cast shadow left out): '#'.
POST = """
....################....
....################....
....################....
....################....
....################....
....################....
....################....
....###############.....
....###############.....
....###############.....
....###############.....
....###############.....
....##############......
....#############.......
.....###########........
.........#.#....#.......
.........#.#....#.......
.........#.#....#.......
.........#.#....#.......
.........#.#....#.......
.........#.#....#.......
.........#.#....#.......
........###.#...#.......
........###.##..........
........................
........................
........................
........................
"""

# The head: a rounded block (plan x0, x1, y0, y1, corner radius), its top at HEAD_TOP.
HEAD = (-7.95, 7.95, 7.0, 13.9, 1.4)
HEAD_TOP = 8.2
# The visor on the head's top: its dark frame (x0, x1, y0, y1), the window sunk in it (x0, x1, y0, y1) and how
# deep; the window's glass in two bands, the front one (towards the shield) where the lamp shows dimly.
FRAME = (-4.05, 4.05, 7.55, 13.15)
WINDOW = (-3.05, 3.05, 8.05, 12.6)
WINDOW_DEPTH = 0.75
LAMP_SPLIT = 10.0           # y between the window's front band (the lamp in 277) and its back band
# The shield: a quarter of an ellipsoid against the head's front (centre x, y; half-width, depth, height),
# fuller than an ellipse (POWER), standing on the ground.
SHIELD = (-0.45, 7.0, 7.55, 7.75, 5.9)
SHIELD_POWER = 2.8
# The pipes: x of the two over the shield (columns 10 and 12) and of the one from its foot (column 16), their
# radius, where they end on the ground (y) with a flange.
PIPES = (-1.5, 0.5)
PIPE_SIDE = 4.5
PIPE_R = 0.55
PIPE_END = -8.7

# The frames: (model, sprite, the window's front band and back band: (palette index, emission strength or 0)).
FRAMES = [
    ("green_lamp_bunker", 277, (0xc5, 1.1), (0x07, 0.0)),
    ("green_lamp_bunker_125", 125, (0xcf, 2.6), (0xcb, 2.2)),
    ("green_lamp_bunker_11", 11, (0x07, 0.0), (0x08, 0.0)),
]


def materials(front, back):
    glow = k.level_palette()
    m = {
        "head": k.material("lampbunker_head", palette=0x08, metallic=0.25, roughness=0.5),
        "head_top": k.material("lampbunker_head_top", palette=0x0a, metallic=0.25, roughness=0.45),
        "shield": k.material("lampbunker_shield", palette=0x0b, metallic=0.3, roughness=0.38),
        "frame": k.material("lampbunker_frame", palette=0x04, metallic=0.3, roughness=0.5),
        "seam": k.material("lampbunker_seam", palette=0x03, metallic=0.2, roughness=0.6),
        "pipe": k.material("lampbunker_pipe", palette=0x0b, metallic=0.55, roughness=0.3),
        "flange": k.material("lampbunker_flange", palette=0x07, metallic=0.5, roughness=0.35),
    }
    for key, (index, strength) in (("front", front), ("back", back)):
        if strength > 0:
            m[key] = k.material(f"lampbunker_lamp_{index:x}", palette=index, metallic=0.0, roughness=0.15,
                                emission=glow[index], emission_strength=strength)
        else:
            m[key] = k.material(f"lampbunker_glass_{index:x}", palette=index, metallic=0.4, roughness=0.08)
    return m


def rounded_outline(x0, x1, y0, y1, r, segments=72):
    pts = mk.rounded_rect_ring(((x0 + x1) / 2, (y0 + y1) / 2), (x1 - x0) / 2, (y1 - y0) / 2, r, 0.0, segments)
    return [(p.x, p.y) for p in pts]


def head(m):
    """The head: a rounded block, its top edges rounded, the visor's window sunk into its top; the frame round
    the window painted dark, the window's floor the glass (two bands)."""
    x0, x1, y0, y1, r = HEAD
    block = mk.prism("head", rounded_outline(x0, x1, y0, y1, r), 0.0, HEAD_TOP, m["head"])
    wx0, wx1, wy0, wy1 = WINDOW
    cutter = mk.box("window_cut", wx0, wx1, wy0, wy1, HEAD_TOP - WINDOW_DEPTH, HEAD_TOP + 2.0)
    mk.boolean(block, cutter, "DIFFERENCE")
    mk.cleanup(block)
    mk.bevel(block, 0.32, 2, 40)
    fx0, fx1, fy0, fy1 = FRAME

    def pick(c, n):
        inside_frame = fx0 < c.x < fx1 and fy0 < c.y < fy1
        if inside_frame and c.z < HEAD_TOP - WINDOW_DEPTH + 0.05 and n.z > 0.9:
            return m["front"] if c.y < LAMP_SPLIT else m["back"]
        if inside_frame and c.z > HEAD_TOP - WINDOW_DEPTH - 0.05:
            return m["frame"]
        if n.z > 0.7:
            return m["head_top"]
        return None
    # The top split along the frame's edges (so the frame and the top paint apart) and the window's floor
    # along y = LAMP_SPLIT (its two bands).
    bm = bmesh.new()
    bm.from_mesh(block.data)
    cuts = [((fx0, 0, 0), (1, 0, 0)), ((fx1, 0, 0), (1, 0, 0)), ((0, fy0, 0), (0, 1, 0)), ((0, fy1, 0), (0, 1, 0)),
            ((0, LAMP_SPLIT, 0), (0, 1, 0))]
    for co, no in cuts:
        top = [f for f in bm.faces if f.normal.z > 0.9]
        geom = list({v for f in top for v in f.verts}) + list({e for f in top for e in f.edges}) + top
        bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-5, plane_co=co, plane_no=no)
    bm.to_mesh(block.data)
    bm.free()
    mk.paint(block, pick)
    mk.shade(block, 40)
    # A lip of glass bulging a little in the window, so the lamp catches the sun: a low lens.
    lens_profile = [(1.0, 0.0), (1.0, 0.12), (0.86, 0.3), (0.62, 0.4), (0.0, 0.45)]
    cx, cy = (wx0 + wx1) / 2, (wy0 + wy1) / 2
    hw, hd = (wx1 - wx0) / 2 - 0.25, (wy1 - wy0) / 2 - 0.25
    rings = []
    for s, dz in lens_profile:
        ring = mk.rounded_rect_ring((cx, cy), max(0.05, hw * s), max(0.05, hd * s), 0.9 * s + 0.05,
                                    HEAD_TOP - WINDOW_DEPTH + 0.02 + dz, 48)
        rings.append(ring)
    lens = k.loft("lens", rings, m["back"], cap_start=False, end_point=(cx, cy, HEAD_TOP - WINDOW_DEPTH + 0.5))
    bm = bmesh.new()
    bm.from_mesh(lens.data)
    mk.split_along(bm, {v: v.co.y for v in bm.verts}, LAMP_SPLIT)
    bm.to_mesh(lens.data)
    bm.free()
    mk.paint(lens, lambda c, n: m["front"] if c.y < LAMP_SPLIT else m["back"])
    k.smooth(lens, 60)
    # Two bolts either side of the visor on the head's top.
    for x in (-5.9, 5.9):
        for y in (9.0, 11.9):
            mk.ball(f"bolt{x}_{y}", (x, y, HEAD_TOP - 0.02), (0.36, 0.36, 0.2), m["flange"], 10, 5)


def shield_z(x, y):
    """The shield's surface height at (x, y) (0 outside it)."""
    cx, cy, rx, ry, rz = SHIELD
    if y > cy:
        y = cy
    u = abs((x - cx) / rx) ** SHIELD_POWER + abs((y - cy) / ry) ** SHIELD_POWER
    if u >= 1:
        return 0.0
    return rz * (1 - u) ** (1 / SHIELD_POWER)


def shield(m):
    """The shield: a quarter of a full ellipsoid against the head's front, a seam round its foot; cut just behind
    the head's front face (the rest would be inside the head)."""
    cx, cy, rx, ry, rz = SHIELD
    profile = []
    steps = 16
    for i in range(steps + 1):
        t = (math.pi / 2) * i / steps
        profile.append((max(1e-3, math.cos(t) ** (2 / SHIELD_POWER)), math.sin(t) ** (2 / SHIELD_POWER)))
    rings = []
    segments = 72
    for s, h in profile:
        ring = []
        for j in range(segments):
            u, v = mk.superellipse_point(2 * math.pi * j / segments, SHIELD_POWER)
            ring.append(Vector((cx + rx * s * u, cy + ry * s * v, rz * h)))
        rings.append(ring)
    # A low rim round the foot (the seam where the armour meets the ground).
    foot = [[Vector((cx + (p.x - cx) * 1.03, cy + (p.y - cy) * 1.03, 0.0)) for p in rings[0]]]
    body = k.loft("shield", foot + rings, m["shield"], start_point=(cx, cy, 0.0), end_point=(cx, cy, rz))
    bm = bmesh.new()
    bm.from_mesh(body.data)
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-5, plane_co=(0, cy + 0.4, 0),
                           plane_no=(0, 1, 0), clear_outer=True)
    bm.to_mesh(body.data)
    bm.free()
    mk.paint(body, lambda c, n: m["seam"] if c.z < 0.35 else None)
    k.smooth(body, 50)
    # Rivets round its foot, a little above the seam (left out where the pipes come down).
    count = 13
    for i in range(count):
        a = math.pi * (0.06 + 0.88 * i / (count - 1))   # round the front half, from the left to the right
        u, v = mk.superellipse_point(-a, SHIELD_POWER)
        x, y = cx + rx * 0.965 * u, cy + ry * 0.965 * v
        if any(abs(x - px) < 1.0 for px in PIPES + (PIPE_SIDE,)):
            continue
        z = shield_z(x, y) + 0.05
        mk.ball(f"rivet{i}", (x, y, max(z, 0.6)), (0.3, 0.3, 0.22), m["flange"], 10, 5)


def pipe_path(x, start_y, start_z):
    """A pipe from (x, start_y, start_z) over the shield's face (just above it) to the ground and along it to
    its flange."""
    pts = [(x, start_y, start_z, PIPE_R)]
    y = SHIELD[1] - 0.3
    while y > -0.5:
        pts.append((x, y, max(shield_z(x, y), 0.0) + PIPE_R + 0.05, PIPE_R))
        y -= 1.3
    pts += [(x, -1.6, PIPE_R + 0.15, PIPE_R), (x, -4.0, PIPE_R + 0.3, PIPE_R),
            (x, PIPE_END + 0.6, PIPE_R + 0.3, PIPE_R), (x, PIPE_END, PIPE_R + 0.3, PIPE_R)]
    return pts


def pipes(m):
    for i, x in enumerate(PIPES):
        tube = mk.smooth_tube(f"pipe{i}", pipe_path(x, SHIELD[1] + 0.6, shield_z(x, SHIELD[1]) + 0.9), m["pipe"], 10)
        k.smooth(tube, 70)
    # The pipe from the shield's foot on the right: out of its face low down, to the ground.
    y_out = -0.2
    while shield_z(PIPE_SIDE, y_out) < 1.4:
        y_out += 0.1
    r = PIPE_R * 0.9
    pts = [(PIPE_SIDE, y_out + 0.3, shield_z(PIPE_SIDE, y_out + 0.3) - 0.2, r),
           (PIPE_SIDE, y_out - 0.5, PIPE_R + 0.3, r), (PIPE_SIDE, y_out - 1.6, r, r), (PIPE_SIDE, -5.0, r + 0.27, r),
           (PIPE_SIDE, PIPE_END + 0.6, r + 0.27, r), (PIPE_SIDE, PIPE_END, r + 0.27, r)]
    k.smooth(mk.smooth_tube("pipe_side", pts, m["pipe"], 10), 70)
    # Flanges where the pipes end, bolted to the ground; straps holding the two pipes to the shield.
    for i, x in enumerate(PIPES + (PIPE_SIDE,)):
        r = PIPE_R * (1.0 if i < 2 else 0.9)
        prof = [(PIPE_END + 0.75, 0.0), (PIPE_END + 0.75, r + 0.3), (PIPE_END - 0.05, r + 0.3), (PIPE_END - 0.05, 0.0)]
        rings = [[Vector((x + rr * math.cos(2 * math.pi * j / 16), yy, r + 0.3 + rr * math.sin(2 * math.pi * j / 16)))
                  for j in range(16)] for yy, rr in prof if rr > 0]
        flange = k.loft(f"flange{i}", rings, m["flange"])
        k.smooth(flange, 40)
        mk.box(f"foot{i}", x - r - 0.45, x + r + 0.45, PIPE_END - 0.35, PIPE_END + 0.35, 0.0, 0.3, m["flange"])
    for j, y in enumerate((5.2, 2.3)):
        z = max(shield_z(PIPES[0], y), shield_z(PIPES[1], y))
        strap = mk.box(f"strap{j}", PIPES[0] - 1.0, PIPES[1] + 1.0, y - 0.35, y + 0.35, z - 0.2, z + 2 * PIPE_R + 0.25,
                       m["flange"])
        mk.bevel(strap, 0.15, 2, 40)


def clip_below_ground(objects):
    """Cuts away whatever reaches below the ground (z < 0), hidden there anyway, so the bounds start at 0."""
    for obj in objects:
        mk.apply(obj)
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        if min(v.co.z for v in bm.verts) < -1e-4:
            bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-5, plane_co=(0, 0, 0),
                                   plane_no=(0, 0, -1), clear_outer=True)
            bm.to_mesh(obj.data)
        bm.free()


def post_mask():
    return [[c == "#" for c in line] for line in POST.strip().splitlines()]


def build():
    options = k.args()
    out = mk.outdir(options)
    for name, sprite, front, back in FRAMES:
        k.reset()
        m = materials(front, back)
        head(m)
        shield(m)
        pipes(m)
        parts = mk.meshes()
        clip_below_ground(parts)
        if "check" in options:
            mk.compare("%s (S %d, the post's own pixels)" % (name, sprite), mk.coverage(parts, 24, 28), post_mask())
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        mk.report(name, parts, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, parts)


if __name__ == "__main__":
    build()
