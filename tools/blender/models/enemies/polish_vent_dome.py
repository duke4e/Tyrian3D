"""The vent dome of the asteroid levels (sheet D sprite 241, 2x2: 24 x 28 pixels; ground layer; ASTEROID? (episode 1,
three of them) and AST ROCK (episode 5, thirteen), enemy 456 of episodes 1-5; armour 20; it launches enemy 455 every
20 ticks), polished (2026-10-21; it replaces wave3_j.py's vent_dome(), a heightfield pillow with a glowing tube along
an arc). models.cfg: model vent_dome enemies/vent_dome.glb origin (origin added), new model vent_dome_239
enemies/vent_dome_239.glb origin and vent_dome_243 ... origin; sprite d 241 vent_dome yaw=0 height=-4
glow=12:0.2:116:-0.5:3 (the vent's light); frame d 239 vent_dome_239, frame d 243 vent_dome_243.

Its animation (241 239 243 243 243 239 239 241, animate 2): the vent brightens from red (241: ramp 7's 0x70-0x75) to
orange (239: up to 0x7b, its middle yellow) and white-hot (243: up to 0x7d) and cools again; nothing else changes (two
pixels of the shield's lip darken). No other enemy (launched ones included) shows D 239, 241 or 243, so the two hotter
frames get frame models (the same geometry, the vent's paint hotter).

D 241 is S 277's pixels (green_lamp_bunker, the grey sentry post: polish_green_lamp_bunker.py) in good part (twins3.py:
0.85, ramp 7 for 0): the same squat grey head reaching in from the top of the sprite (columns 4-19 of rows 0-6), the
same big rounded shield of armour against its front bulging down the screen to the ground (columns 4-18 of rows 7-14,
lit along its left edge), the same two pipes from the head over the shield's crown and down its face (columns 10 and
12 of rows 7-15); but on the head's top a plain raised plate between two seams (columns 7 and 15 of rows 0-5) where the
post has its visor, and round the shield's foot, where the post's pipes run on along the ground, a red-hot crescent
vent (rows 12-19: a band hugging the shield's foot, a pixel wide at its ends (columns 3 and 19 of row 12), four at its
front (rows 16-19), its middle the hottest, a dark rim along its outside). The rubble round it, the dark patch to its
right (its shadow, columns 19-23) and the tiles under the vent's front are the map's ground: left out.

So the model is the post's: polish_green_lamp_bunker's head block (HEAD, HEAD_TOP; this script's own top: the plate and
its seams instead of the visor, its bolts left off), its shield (shield(): the quarter of a superellipsoid against the
head, its rivets left off, the vent lies where they were) and its two pipes over the shield (pipe_path(), ending where
they dip into the vent); its materials' greys (0x08, 0x0a, 0x0b, 0x03, 0x07). The vent is a loft along the shield's
foot from one side round the front to the other: each section a trough tucked under the shield's rim, sloping down and
out to a raised rim, wide (WIDE) at the front and narrowing to its ends (TIP), its floor painted in bands of heat along
smooth contours (polish_orb_red.band_split: hottest along the trough's middle at the front, cooler towards its ends and
its edges, the rim dark), glowing a little in its own colours (emission 0.08-0.36 in 241, to 0.5 in 239, 0.6 in 243).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the ground (z = 0); origin at
the sprite's centre (pixel 12, 14): column c is x = c + 0.5 - 12, row r is y = 13.5 - r. Drawn at its origin (origin),
height=-4 on the ground layer: on the terrain (the bunker's model stands on z = 0 as this one).

Replaces wave3_j.py's vent dome: its section "# --- D 241: the vent dome" (vent_dome() with its @model("vent_dome",
...) registration) and the vent_dome bullet of its docstring; wave3_j.py keeps shell_ship and bronze_beetle
(wave3_at_d.py imports wave3_j.py for its shell ship: unaffected).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouette against the dome's
own pixels, written below), --preview <prefix>, --only <model,...>.
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
import polish_green_lamp_bunker as glb  # noqa: E402
from polish_orb_red import band_split  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402

# The dome's own pixels in D 241 (the map's rubble, its shadow and the tiles under the vent left out): '#'.
DOME = """
....################....
....################....
....################....
...#################....
...#################....
...#################....
...#################....
....###############.....
....###############.....
....###############.....
....###############.....
....###############.....
...#################....
...#################....
...#################....
....###############.....
....###############.....
.....#############......
......###########.......
.......#########........
........................
........................
........................
........................
........................
........................
........................
........................
"""

# The head's top: the two seams (x, half width, depth) and the plate between them (how high).
SEAMS = [(-4.5, 0.32, 0.45), (3.5, 0.32, 0.45)]
PLATE_RISE = 0.3
# The vent: along the shield's foot from the angle START (degrees round the shield's middle, 180 its left side) to
# 360 - START, the trough WIDE wide at the front, TIP at its ends; how far it tucks under the shield.
START = 208.0
WIDE, TIP = 4.6, 0.9
TUCK = 0.7
# The frames: (model, sprite, the vent's bands: [(lowest heat, palette index, emission strength)]).
FRAMES = [
    ("vent_dome", 241, [(-9.0, 0x70, 0.08), (0.18, 0x71, 0.12), (0.36, 0x72, 0.2), (0.56, 0x73, 0.28),
                        (0.78, 0x75, 0.36)]),
    ("vent_dome_239", 239, [(-9.0, 0x71, 0.12), (0.18, 0x73, 0.25), (0.36, 0x75, 0.33), (0.56, 0x77, 0.42),
                            (0.78, 0x7a, 0.5)]),
    ("vent_dome_243", 243, [(-9.0, 0x72, 0.15), (0.18, 0x74, 0.3), (0.36, 0x77, 0.4), (0.56, 0x79, 0.5),
                            (0.78, 0x7c, 0.6)]),
]


def materials(bands):
    pal = k.level_palette()
    m = {
        "head": k.material("ventdome_head", palette=0x08, metallic=0.25, roughness=0.5),
        "head_top": k.material("ventdome_head_top", palette=0x0a, metallic=0.25, roughness=0.45),
        "plate": k.material("ventdome_plate", palette=0x09, metallic=0.25, roughness=0.45),
        "shield": k.material("ventdome_shield", palette=0x0b, metallic=0.3, roughness=0.38),
        "seam": k.material("ventdome_seam", palette=0x03, metallic=0.2, roughness=0.6),
        "pipe": k.material("ventdome_pipe", palette=0x0b, metallic=0.55, roughness=0.3),
        "flange": k.material("ventdome_flange", palette=0x07, metallic=0.5, roughness=0.35),
        "rim": k.material("ventdome_rim", palette=0x70, metallic=0.3, roughness=0.45),
    }
    m["heat"] = [(low, k.material("ventdome_heat_%x" % index, palette=index, metallic=0.0, roughness=0.3,
                                  emission=pal[index], emission_strength=glow)) for low, index, glow in bands]
    return m


def head(m):
    """The head: glb's rounded block, its top edges rounded; on its top a plate between two seams cut across it."""
    x0, x1, y0, y1, r = glb.HEAD
    block = mk.prism("head", glb.rounded_outline(x0, x1, y0, y1, r), 0.0, glb.HEAD_TOP, m["head"])
    for i, (sx, hw, depth) in enumerate(SEAMS):
        cutter = mk.box(f"seam_cut{i}", sx - hw, sx + hw, y0 - 1.0, y1 + 1.0, glb.HEAD_TOP - depth, glb.HEAD_TOP + 2.0)
        mk.boolean(block, cutter, "DIFFERENCE")
    mk.cleanup(block)
    mk.bevel(block, 0.32, 2, 40)

    def pick(c, n):
        if any(abs(c.x - sx) < hw + 0.05 for sx, hw, _ in SEAMS) and c.z < glb.HEAD_TOP - 0.1 and n.z > 0.3:
            return m["seam"]
        if n.z > 0.7:
            return m["head_top"]
        return None
    mk.paint(block, pick)
    mk.shade(block, 40)
    # The plate between the seams: a low slab on the top, bevelled, its left edge catching the light.
    (ax, ahw, _), (bx, bhw, _) = SEAMS
    plate = mk.box("plate", ax + ahw + 0.12, bx - bhw - 0.12, y0 + 0.35, y1 - 0.25, glb.HEAD_TOP - 0.2,
                   glb.HEAD_TOP + PLATE_RISE, m["plate"])
    mk.bevel(plate, 0.22, 2, 40)
    mk.paint(plate, lambda c, n: m["head_top"] if n.x < -0.4 and n.z > 0.2 else None)
    mk.shade(plate, 40)


def shield(m):
    """glb's shield, its rivets left off (the vent lies round its foot)."""
    before = set(bpy.data.objects)
    glb.shield(m)
    for obj in set(bpy.data.objects) - before:
        if obj.name.startswith("rivet"):
            data = obj.data
            bpy.data.objects.remove(obj)
            bpy.data.meshes.remove(data)


def pipes(m):
    """glb's two pipes over the shield's crown and down its face, ending where they dip into the vent."""
    for i, x in enumerate(glb.PIPES):
        pts = [p for p in glb.pipe_path(x, glb.SHIELD[1] + 0.6, glb.shield_z(x, glb.SHIELD[1]) + 0.9) if p[1] > -0.4]
        last = pts[-1]
        pts.append((x, last[1] - 0.9, max(0.6, last[2] - 1.0), glb.PIPE_R))   # down into the trough
        tube = mk.smooth_tube(f"pipe{i}", pts, m["pipe"], 10)
        k.smooth(tube, 70)
    # Straps holding the two pipes to the shield (glb's).
    for j, y in enumerate((5.2, 2.3)):
        z = max(glb.shield_z(glb.PIPES[0], y), glb.shield_z(glb.PIPES[1], y))
        strap = mk.box(f"strap{j}", glb.PIPES[0] - 1.0, glb.PIPES[1] + 1.0, y - 0.35, y + 0.35, z - 0.2,
                       z + 2 * glb.PIPE_R + 0.25, m["flange"])
        mk.bevel(strap, 0.15, 2, 40)


def foot(a):
    """The shield's foot outline at angle a (degrees round its middle) and its outward normal there (plan)."""
    cx, cy, rx, ry, _ = glb.SHIELD
    t = math.radians(a)
    u, v = mk.superellipse_point(t, glb.SHIELD_POWER)
    p = Vector((cx + rx * u, cy + ry * v))
    q = Vector(mk.superellipse_point(t + 0.002, glb.SHIELD_POWER))
    tangent = Vector((rx * (q[0] - u), ry * (q[1] - v))).normalized()
    normal = Vector((tangent.y, -tangent.x))
    if normal.dot(p - Vector((cx, cy))) < 0:
        normal = -normal
    return p, normal


def vent(m):
    """The crescent vent: a trough round the shield's foot, tucked under its rim, sloping out to a dark raised rim;
    wide at the front, narrowing to its ends; painted in bands of heat."""
    steps = 64
    rings, heat = [], []
    # The section (outward distance as a fraction of the width, height, how hot): from under the shield out.
    section = [(-TUCK, 1.6, 0.0), (0.0, 1.05, 0.15), (0.18, 0.72, 0.55), (0.42, 0.52, 1.0), (0.66, 0.5, 0.85),
               (0.84, 0.62, 0.45), (0.95, 0.88, 0.05), (1.04, 0.95, -0.5), (1.12, 0.7, -0.5), (1.18, 0.0, -0.5),
               (0.2, -0.05, -0.5), (-TUCK, -0.05, 0.0)]
    for i in range(steps + 1):
        a = START + (540.0 - 2 * START) * i / steps   # from the left side round the front to the right
        p, n = foot(a)
        f = math.sin(math.pi * i / steps)            # 0 at the ends, 1 at the front
        w = TIP + (WIDE - TIP) * f ** 1.4
        ring, hh = [], []
        for s, z, h in section:
            q = p + n * (s * w if s >= 0 else s)    # (the tuck under the shield a fixed distance)
            ring.append(Vector((q.x, q.y, z * (0.75 + 0.25 * f))))
            hh.append(h * (0.35 + 0.65 * f) if h > 0 else h)
        rings.append(ring)
        heat.append(hh)
    obj = k.loft("vent", rings, m["rim"], cap_start=True, cap_end=True)
    # The vertex values: the loft's vertices are the rings' points in order, then its two cap centres.
    values = [h for hh in heat for h in hh]
    values += [-0.5] * (len(obj.data.vertices) - len(values))
    bands = [(-9.0, m["rim"])] + [(max(low, 0.0) + 0.02, mat) for low, mat in m["heat"]]
    band_split(obj, values, bands)
    k.smooth(obj, 50)
    return obj


def clip_below_ground(objects):
    glb.clip_below_ground(objects)


def dome_mask():
    return [[c == "#" for c in line] for line in DOME.strip().splitlines()]


def build():
    options = k.args()
    only = options["only"].split(",") if "only" in options else None
    for name, sprite, bands in FRAMES:
        if only and name not in only:
            continue
        k.reset()
        m = materials(bands)
        head(m)
        shield(m)
        pipes(m)
        vent(m)
        parts = mk.meshes()
        clip_below_ground(parts)
        for obj in parts:
            mk.apply(obj)
        triangulate(parts)
        if "check" in options:
            mk.compare("%s (D %d, the dome's own pixels)" % (name, sprite), mk.coverage(parts, 24, 28), dome_mask())
        bpy.context.scene.view_settings.view_transform = "Standard"
        mk.report(name, parts, os.path.join(mk.outdir(options), name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, parts)


if __name__ == "__main__":
    build()
