"""Two of FRUIT's machines in the hexagonal sockets of its floor (sheet %, written x25 in models.cfg; 2x2 sprites of
episode 5, ground enemies), polished (2026-10-22, round 32; they replace wave3_al.py's fruit_hex_pod and
fruit_glyph_swirl).

FRUIT's ground is a honeycomb of blue hexagonal sockets (its map 194753bd5ac5f6cc: every tile holds two of them, a
bevelled rim round a sunken floor, in ramp 3's blues), and both machines are tiles of that map coming alive: the levels
put each exactly on a tile (FRUIT's events 6, "col n.00 row n.00" in tools/content/tyrevents.py), and the socket's
pixels in the lower half of their sprites (columns 4-19, rows 14-27) are the map's own, pixel for pixel. The models are
what the sprites draw in the socket, standing on the floor of the map's socket (models.cfg origin and height=-4: z 0 is
the terrain; FRUIT's map has no heights, so that is its flat ground); the socket itself is the map's and is not
modelled.

- fruit_hex_pod (% 195; enemy 1250, armour 10, 11 events at t 1560-6320, one at a time, always on map tile 101; its
  animation 195 197 197 197 199 199 199 197 195 plays when it fires (animate 2): every 40 game frames it launches one
  of FRUIT's green grapes (' 247, enemy 1261, polish_launched_fruit.py) at the player). The map's tile 101 under it
  is the socket with its floor opened into a dark vent (black and navy, an X across it): what the player sees once the
  pod is shot (and the 3D view's wreck of the model, slumped and burnt). As the sprite and its 4x upscale draw it: a
  round grille filling the socket (columns 6-17 of rows 15-26): eight rounded steel vanes (0x37-0x3a, lit 0x3b) round a
  hub, dark slots between them: wide ones up, down and to the sides (0x35, two pixels wide), narrow black slits on the
  diagonals (0x62); a light bezel round the hub (0x3a, its top edge 0x3d) and in it a lamp (columns 11-12 of rows
  20-21: 0x72-0x76 red in 195, 0x75-0x79 orange-red in 197, 0x7a-0x7e yellow in 199: it heats up as the pod fires).
  Built as such a vent: its dark floor (the slots' navy, the slits' black), a thin collar round its rim, the eight vanes
  (prisms over their plans: annular sectors less the half-widths of the slots on either side, their corners rounded,
  their tops sloping down outwards, bevelled; painted face by face by the light they get), a hub with a squarish
  bevelled top (the bezel, its rim 0x3c) and the lamp on it: a glossy dome glowing in its frame's reds and yellows
  (0.42-0.62 in their own colours), a hot spot towards the sun. The frames 197 and 199 are the same mesh with the
  lamp's materials (frame models: no other enemy shows % 197 or 199).
- fruit_glyph_swirl (% 283; enemy 1254, armour 0: it can't be shot; 7 events at t 1392-6348; its animation 283 x5,
  245 x5, 277 x5, 245 x5, all the time): a glyph in the socket's floor that pulses. 283 is the map's tile 93 pixel for
  pixel (the glyph painted dark in the floor, 0x02-0x04); 245 lights it grey (0x07-0x09), 277 white (0x0d-0x0f), the
  floor round it a shade lighter there (0x3b-0x3c). The glyph: a squiggle like a z with a tail, drawn in single pixels
  (the top stroke at row 18, columns 10-13, then down and back along row 20, down to row 22 and its tail to row 24).
  Built as an inlay of glass in the floor: a flattened tube along the glyph's pixels (a Catmull-Rom curve through
  them), lying in the floor, its ends tapered; dark smoky glass in 283 (0x03), glowing grey (0x08, 0.3) in 245 and
  white (0x0e, 0.5) in 277; in the lit frames a halo of light on the floor round it, two see-through ribbons (light
  blue 0x3c, glowing) under the stroke, the outer wider and fainter. Frame models fruit_glyph_swirl_245 and _277 (no
  other enemy shows % 245 or 277). FRUIT's other two glyph tiles (% 269 and 275, the tree and the hook) are the same
  kind of tile: glyph() would build them from their pixels' paths (not done here: wave3_al.py still builds them).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the floor (z 0); origin at the
sprite's centre (pixel 12, 14): column c is x = c + 0.5 - 12, row r is y = 13.5 - r. The socket's middle is (0, -7).
The pod stands 2.4 high (its lamp's top), the glyph 0.5. Every mesh is triangulated before the export
(polish_k_pod.triangulate: the same output with and without --check); no random numbers, no booleans.

models.cfg: the model lines get origin (model fruit_hex_pod enemies/fruit_hex_pod.glb origin, model fruit_glyph_swirl
enemies/fruit_glyph_swirl.glb origin), the new frame models' lines (model fruit_hex_pod_197 / _199, fruit_glyph_swirl_245
/ _277, enemies/<name>.glb origin) and frame lines (frame x25 197 fruit_hex_pod_197, frame x25 199 fruit_hex_pod_199,
frame x25 245 fruit_glyph_swirl_245, frame x25 277 fruit_glyph_swirl_277); the sprite lines get height=-4 (sprite x25
195 fruit_hex_pod yaw=0 height=-4 glow=7:0.22:118:0:7, sprite x25 283 fruit_glyph_swirl yaw=0 height=-4).

Replaces wave3_al.py's fruit_hex_pod (POD, POD_LAMP, POD_BASE, pod_grille(), fruit_hex_pod() with its @kit.model
registration and its docstring paragraph) and fruit_glyph_swirl (fruit_glyph_swirl() with its @kit.model registration;
glyph_tile() and is_socket() stay for the tree and the hook), and wave3_al_art.py's POD, POD_2, POD_3, GLYPH_W1,
GLYPH_W2 and GLYPH_W3 (only POD and GLYPH_W2 were read, by those two models).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each model's silhouette against
its frame in enemy_x25.png, the map's socket left out: only the pixels the model stands for), --preview <prefix>,
--only <name,...>.
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
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_deli_boss import join  # noqa: E402
from polish_torm_beetle import tube  # noqa: E402

LIGHT = Vector((-0.6, 0.6, 1.0)).normalized()   # towards the game's sun
FLAT = LIGHT.z
SOCKET_C = (0.0, -7.0)            # the socket's middle (columns 4-19, rows 14-27)


def lit(name, index, strength=0.0, metallic=0.0, roughness=0.4, alpha=None):
    pal = k.level_palette()
    extra = dict(emission=pal[index], emission_strength=strength) if strength > 0 else {}
    if alpha is not None:
        extra["alpha"] = alpha
    return k.material(name, palette=index, metallic=metallic, roughness=roughness, **extra)


def light_value(n, base, a=3.2, b=1.2):
    return base + a * (n.dot(LIGHT) - FLAT) + b * (n.z - 1.0)


def band(value, bands):
    key = bands[0][1]
    for lowest, k_ in bands:
        if value >= lowest:
            key = k_
    return key


# --- % 195: the vent pod -----------------------------------------------------------------------------------------------
FLOOR_R, FLOOR_Z = 6.3, 0.06      # the vent's dark floor (a disc on the socket's floor)
HUB_RING = 2.75                   # the floor round the hub darker within this
COLLAR = (5.85, 6.35, 0.55)       # the collar round its rim: inner and outer radius, height
VANE_R = (2.75, 5.95)             # the vanes from the hub to the collar
VANE_Z = (1.42, 1.08)             # their tops at the hub and at the collar
WIDE, NARROW = 1.12, 0.5          # the slots' half-widths: up, down and to the sides; on the diagonals
VANE_BEVEL = 0.32
HUB = (2.25, 1.55, 3.6)           # the hub: half-width, height, its plan's power (squarish, as the sprite's bezel)
BEZEL = (0.42, 0.2)               # its top's rim: width, how much higher than its middle
LAMP = (1.12, 0.78)               # the lamp: radius, height over the hub's top
# The lamp's materials per frame: (body, hot spot) palette indices and emission strengths.
LAMP_FRAMES = {195: ((0x74, 0.42), (0x76, 0.55)), 197: ((0x77, 0.48), (0x79, 0.6)), 199: ((0x7c, 0.52), (0x7e, 0.62))}
STEEL_BANDS = [(-99, 0x36), (4.9, 0x37), (5.6, 0x38), (6.2, 0x3a), (6.75, 0x3b), (7.2, 0x3c)]
STEEL_BASE = 5.95


def pod_materials(frame):
    m = {i: lit(f"pod_{i:02x}", i, metallic=0.3, roughness=0.34) for i in (0x36, 0x37, 0x38, 0x3a, 0x3b, 0x3c)}
    m["floor"] = lit("pod_floor", 0x35, metallic=0.2, roughness=0.6)
    m["slit"] = lit("pod_slit", 0x62, metallic=0.1, roughness=0.7)
    m["ring"] = lit("pod_ring", 0x34, metallic=0.2, roughness=0.6)
    (body, bg), (hot, hg) = LAMP_FRAMES[frame]
    m["lamp"] = lit(f"pod_lamp{frame}", body, bg, roughness=0.12)
    m["hot"] = lit(f"pod_hot{frame}", hot, hg, roughness=0.1)
    return m


def paint_steel(obj, m, base=STEEL_BASE):
    """Each face of a hard steel part by the light it gets (flat faces STEEL_BASE)."""
    mk.paint(obj, lambda c, n: m[band(light_value(n, base), STEEL_BANDS)])
    return obj


def vane_plan(k_):
    """The plan of vane k_ (between the slots at 45 k_ and 45 (k_ + 1) degrees), counter-clockwise: an annular sector
    less the half-widths of the slots on either side (the orthogonal ones wide, the diagonal ones narrow)."""
    g0, g1 = math.radians(45.0 * k_), math.radians(45.0 * (k_ + 1))
    h0 = WIDE if k_ % 2 == 0 else NARROW
    h1 = NARROW if k_ % 2 == 0 else WIDE
    r0, r1 = VANE_R

    def corner(g, h, r, sign):
        t = math.sqrt(max(r * r - h * h, 1e-6))
        u = (math.cos(g), math.sin(g))
        n = (-math.sin(g) * sign, math.cos(g) * sign)
        return (t * u[0] + h * n[0], t * u[1] + h * n[1])

    def angle(p):
        return math.atan2(p[1], p[0])

    a_in, a_out = corner(g0, h0, r0, 1), corner(g0, h0, r1, 1)
    d_out, d_in = corner(g1, h1, r1, -1), corner(g1, h1, r0, -1)
    pts = [a_in, a_out]
    t0, t1 = angle(a_out), angle(d_out)
    if t1 < t0:
        t1 += 2 * math.pi
    for i in range(1, 5):
        t = t0 + (t1 - t0) * i / 5
        pts.append((r1 * math.cos(t), r1 * math.sin(t)))
    pts += [d_out, d_in]
    t0, t1 = angle(d_in), angle(a_in)
    if t0 < t1:
        t0 += 2 * math.pi
    for i in range(1, 3):
        t = t0 + (t1 - t0) * i / 3
        pts.append((r0 * math.cos(t), r0 * math.sin(t)))
    pts = mk.chaikin(pts, 1)
    cx, cy = SOCKET_C
    return [(x + cx, y + cy) for x, y in pts]


def vanes(m):
    out = []
    cx, cy = SOCKET_C
    for k_ in range(8):
        def top(x, y):
            r = math.hypot(x - cx, y - cy)
            t = (r - VANE_R[0]) / (VANE_R[1] - VANE_R[0])
            return VANE_Z[0] + (VANE_Z[1] - VANE_Z[0]) * min(1.0, max(0.0, t))
        obj = mk.wedge(f"vane{k_}", vane_plan(k_), FLOOR_Z, top, m[0x3a])
        mk.bevel(obj, VANE_BEVEL, 2, 30)
        k.smooth(obj, 35)
        paint_steel(obj, m)
        out.append(obj)
    return out


def floor(m):
    """The vent's floor: a disc in rings, painted by where it lies: round the hub navy, in the diagonal slits black, in
    the wide slots the slots' navy."""
    cx, cy = SOCKET_C
    bm = bmesh.new()
    seg = 48
    radii = [0.0, HUB_RING, FLOOR_R]
    rings = []
    for r in radii:
        if r < 1e-6:
            rings.append([bm.verts.new((cx, cy, FLOOR_Z))])
        else:
            rings.append([bm.verts.new((cx + r * math.cos(2 * math.pi * j / seg),
                                        cy + r * math.sin(2 * math.pi * j / seg), FLOOR_Z)) for j in range(seg)])
    for i in range(len(rings) - 1):
        a, b = rings[i], rings[i + 1]
        for j in range(seg):
            jn = (j + 1) % seg
            bm.faces.new((a[0], b[j], b[jn]) if len(a) == 1 else (a[j], b[j], b[jn], a[jn]))
    # a short skirt down to the floor of the map's socket
    outer = rings[-1]
    low = [bm.verts.new((v.co.x, v.co.y, -0.4)) for v in outer]
    for j in range(seg):
        jn = (j + 1) % seg
        bm.faces.new((outer[j], low[j], low[jn], outer[jn]))
    keys = []
    for f in bm.faces:
        c = f.calc_center_median()
        r = math.hypot(c.x - cx, c.y - cy)
        a = math.degrees(math.atan2(c.y - cy, c.x - cx)) % 90.0
        if r < HUB_RING:
            keys.append("ring")
        elif abs(a - 45.0) < 22.5:
            keys.append("slit")
        else:
            keys.append("floor")
    mesh = bpy.data.meshes.new("floor")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("floor", mesh)
    bpy.context.scene.collection.objects.link(obj)
    for key in ("ring", "slit", "floor"):
        mesh.materials.append(m[key])
    order = ["ring", "slit", "floor"]
    for poly, key in zip(mesh.polygons, keys):
        poly.material_index = order.index(key)
    k.recalc_normals(obj)
    return obj


def collar(m):
    ri, ro, h = COLLAR
    rm = (ri + ro) / 2
    w = (ro - ri) / 2
    prof = [(ri, FLOOR_Z), (ri, h - 0.18), (ri + 0.12 * w, h - 0.06), (rm, h), (ro - 0.12 * w, h - 0.06),
            (ro, h - 0.18), (ro, -0.3)]
    # a lathe of a closed profile: rings round the socket's middle
    cx, cy = SOCKET_C
    seg = 48
    rings = [[Vector((cx + r * math.cos(2 * math.pi * j / seg), cy + r * math.sin(2 * math.pi * j / seg), z))
              for j in range(seg)] for r, z in prof]
    verts = [p for ring in rings for p in ring]
    faces = []
    for i in range(len(rings) - 1):
        for j in range(seg):
            jn = (j + 1) % seg
            faces.append((i * seg + j, i * seg + jn, (i + 1) * seg + jn, (i + 1) * seg + j))
    obj = k.mesh_object("collar", verts, faces, m[0x38])
    k.recalc_normals(obj)
    k.smooth(obj, 50)
    paint_steel(obj, m, STEEL_BASE - 0.7)
    return obj


def hub(m):
    hw, h, power = HUB
    bw, bh = BEZEL
    cx, cy = SOCKET_C
    prof = [(hw, 0.0), (hw, h - 0.25), (hw - 0.08, h - 0.08), (hw - 0.22, h + bh), (hw - bw, h + bh - 0.02),
            (hw - bw - 0.12, h), (0.01, h)]
    obj = mk.lathe("hub", prof, (cx, cy), m[0x38], segments=32, power=power)
    k.recalc_normals(obj)
    k.smooth(obj, 40)

    def pick(c, n):
        r = mk.plan_radius(c.x - cx, c.y - cy, power=power)
        if c.z > h - 0.1 and r > hw - bw - 0.15:
            return m[0x3c] if n.dot(LIGHT) > 0.6 else m[0x3b]
        return m[band(light_value(n, STEEL_BASE - 0.4), STEEL_BANDS)]
    mk.paint(obj, pick)
    return obj


def lamp(m):
    """The lamp: a glossy dome on the hub's top, a hot spot on its side towards the sun."""
    r, h = LAMP
    cx, cy = SOCKET_C
    z0 = HUB[1] - 0.05
    obj = mk.dome("lamp", (cx, cy), (r, r, h), z0, m["lamp"], segments=24, steps=6)
    sun = Vector((LIGHT.x, LIGHT.y, 0.0)).normalized()

    def pick(c, n):
        rel = Vector((c.x - cx, c.y - cy, 0.0))
        towards = rel.dot(sun)
        return m["hot"] if (towards > -0.1 and n.z > 0.55) or n.z > 0.93 else None
    mk.paint(obj, pick)
    return obj


def hex_pod(frame):
    m = pod_materials(frame)
    parts = [floor(m), collar(m), hub(m), lamp(m)] + vanes(m)
    for obj in parts:
        mk.apply(obj)
    triangulate(parts)
    return [join(parts, "pod")]


# --- % 283: the glyph swirl --------------------------------------------------------------------------------------------
# The glyph's pixels in drawing order (column, row), from the top stroke's left end to the tail; the stroke's half-width
# and half-height along it (at the start, the middle and the end).
SWIRL_PATH = [(10, 18), (11, 18), (12, 18), (13, 18), (14, 19), (13, 20), (12, 20), (11, 20), (10, 21), (11, 22),
              (12, 22), (13, 23), (12, 24)]
STROKE_W = (0.34, 0.5, 0.36)
STROKE_H = (0.2, 0.3, 0.22)
STROKE_Z = 0.16
HALO_Z = 0.12                     # the halo's ribbons this high over the floor (the inner one a little higher)
# Per frame: (the stroke's palette index, emission strength); the halo's (index, strength, alpha) inner and outer, or
# None.
GLYPH_FRAMES = {
    283: ((0x03, 0.0), None),
    245: ((0x08, 0.3), ((0x3c, 0.22, 0.28, 1.05), (0x3b, 0.14, 0.16, 1.7))),
    277: ((0x0e, 0.5), ((0x3c, 0.36, 0.38, 1.1), (0x3c, 0.22, 0.22, 1.85))),
}


def pixel_xy(c, r):
    return (c + 0.5 - 12.0, 13.5 - r)


def stations(path, widths, heights, z):
    """Tube stations along a path of pixels: its two ends drawn out half a pixel, the widths and heights interpolated
    from the start through the middle to the end."""
    pts = [pixel_xy(c, r) for c, r in path]
    (x0, y0), (x1, y1) = pts[0], pts[1]
    d = math.hypot(x1 - x0, y1 - y0)
    start = (x0 - (x1 - x0) / d * 0.45, y0 - (y1 - y0) / d * 0.45)
    (x0, y0), (x1, y1) = pts[-1], pts[-2]
    d = math.hypot(x1 - x0, y1 - y0)
    end = (x0 - (x1 - x0) / d * 0.45, y0 - (y1 - y0) / d * 0.45)
    pts = [start] + pts + [end]
    out = []
    n = len(pts)
    for i, (x, y) in enumerate(pts):
        t = i / (n - 1)
        if t < 0.5:
            w = widths[0] + (widths[1] - widths[0]) * (t / 0.5)
            h = heights[0] + (heights[1] - heights[0]) * (t / 0.5)
        else:
            w = widths[1] + (widths[2] - widths[1]) * ((t - 0.5) / 0.5)
            h = heights[1] + (heights[2] - heights[1]) * ((t - 0.5) / 0.5)
        taper = min(1.0, i / 1.0, (n - 1 - i) / 1.0)
        out.append((x, y, z, max(0.05, w * (0.35 + 0.65 * taper)), max(0.05, h * (0.4 + 0.6 * taper)), 2.0))
    return out


def ribbon(name, path, half_width, z, mat):
    """A flat ribbon along the path's curve (polish_torm_beetle.tube's curve, flattened to nothing high), its ends
    rounded: a halo of light on the floor."""
    st = [(x, y, z, half_width, 0.02, 2.0) for x, y, *_ in stations(path, (1, 1, 1), (1, 1, 1), z)]
    obj = tube(name, st, mat, segments=10)
    for v in obj.data.vertices:
        v.co.z = z
    obj.data.update()
    return obj


def glyph(frame, path=SWIRL_PATH):
    (index, glow), halos = GLYPH_FRAMES[frame]
    m = {"stroke": lit(f"glyph_stroke{frame}", index, glow, metallic=0.2, roughness=0.15)}
    parts = []
    stroke = tube("stroke", stations(path, STROKE_W, STROKE_H, STROKE_Z), m["stroke"], segments=12)
    k.smooth(stroke, 70)
    parts.append(stroke)
    if halos:
        # the outer, fainter ribbon first (drawn first: the game draws see-through faces in the order of their
        # materials), then the inner one
        for i, (h_index, h_glow, alpha, hw) in reversed(list(enumerate(halos))):
            mat = lit(f"glyph_halo{frame}_{i}", h_index, h_glow, roughness=0.5, alpha=alpha)
            parts.append(ribbon(f"halo{i}", path, hw, HALO_Z + 0.02 * (1 - i), mat))
    for obj in parts:
        mk.apply(obj)
    triangulate(parts)
    if len(parts) > 1:
        # see-through layers last (the outer before the inner), the stroke first
        return [join(parts, "glyph")]
    return parts


# --- Build -------------------------------------------------------------------------------------------------------------

MODELS = [
    # name, sprite, builder
    ("fruit_hex_pod", 195, lambda: hex_pod(195)),
    ("fruit_hex_pod_197", 197, lambda: hex_pod(197)),
    ("fruit_hex_pod_199", 199, lambda: hex_pod(199)),
    ("fruit_glyph_swirl", 283, lambda: glyph(283)),
    ("fruit_glyph_swirl_245", 245, lambda: glyph(245)),
    ("fruit_glyph_swirl_277", 277, lambda: glyph(277)),
]


def check(options, name, sprite, objects):
    """The silhouette against the sprite's pixels the model stands for: the grille's (within its round floor) for the
    pod, the glyph's (not ramp 3, the socket's blues) for the glyph (its halo, see-through, left out)."""
    if "check" not in options:
        return
    sheet = os.path.join(options["check"], "enemy_x25.png")
    from sprite_profile import sprite_indices
    rows = sprite_indices(sheet, sprite, True)
    cx, cy = SOCKET_C
    mask = []
    for r, row in enumerate(rows):
        line = []
        for c, v in enumerate(row):
            x, y = c + 0.5 - 12, 13.5 - r
            if v is None:
                line.append(False)
            elif name.startswith("fruit_hex_pod"):
                line.append(math.hypot(x - cx, y - cy) < 6.2)
            else:
                line.append(v >> 4 != 3)
        mask.append(line)
    shown = []
    for obj in objects:
        copy = obj.copy()
        copy.data = obj.data.copy()
        bpy.context.scene.collection.objects.link(copy)
        bm = bmesh.new()
        bm.from_mesh(copy.data)
        clear = [f for f in bm.faces if copy.data.materials[f.material_index].surface_render_method == "BLENDED"]
        bmesh.ops.delete(bm, geom=clear, context="FACES")
        bm.to_mesh(copy.data)
        bm.free()
        shown.append(copy)
    for obj in objects:
        obj.hide_render = True
    mk.compare("%s (x25 %d)" % (name, sprite), mk.coverage(shown, 24, 28), mask)
    for obj in objects:
        obj.hide_render = False
    for copy in shown:
        mesh = copy.data
        bpy.data.objects.remove(copy)
        bpy.data.meshes.remove(mesh)


def build():
    options = k.args()
    out = mk.outdir(options)
    only = set(options["only"].split(",")) if "only" in options else None
    for name, sprite, make in MODELS:
        if only is not None and name not in only:
            continue
        k.reset()
        objects = make()
        for obj in objects:
            obj.name = name
            obj.data.name = name
        bpy.context.view_layer.update()
        check(options, name, sprite, [o for o in objects])
        bpy.context.scene.view_settings.view_transform = "Standard"
        mk.report(name, objects, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, objects, size=(24, 28), scale=16, distance=0.45)


if __name__ == "__main__":
    build()
