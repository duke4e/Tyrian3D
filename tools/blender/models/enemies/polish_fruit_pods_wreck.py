"""FRUIT's vent pod's wreck (sheet % sprite 195, written x25 in models.cfg: its stand-in, what FRUIT's map paints where
the pod stands once it is destroyed, before it comes and where none comes: its tile 101, the vent blown open; 8 of
them), built on polish_fruit_pods.py (2026-10-25, the clean ground's stage 4).

As the map paints it at 4x (FRUIT 194753bd5ac5f6cc, e.g. at 468, 4942; the same tile under FRUIT's orb, x25 233: see
polish_fruit_ground_wreck.py): the socket's floor blown open into a dark pit filling the socket (a hexagon with its
corners left and right as the map's sockets, about 6 pixels round its middle (0, -7), its edge torn and pale where it
catches the light, columns 6-17 of rows 15-26), a black X across it along the diagonals (0x30-0x32: the grille's
diagonal slits torn open, the hub blown out where they cross), four bent blue plates between the X's arms, up, down,
left and right (0x34-0x37: the vanes crushed together in pairs over the wide slots), a small ring lying in the lower
one (the hub's bezel).

The model: the vanes crushed together in pairs into four plates, one in each quarter of the pit between the X's
diagonals (their plans the quarter's, their edges ARM off the diagonals, out to just inside the pit's edge; extruded
from the live vanes' floor and bevelled as polish_fruit_pods.py's vanes, then crumpled: a hump rising from their inner
end, a crease along the crushed slot between the pair, noise, bent down into the X along their edges), sagging a few
degrees into the pit, repainted along smooth contours by the light they get in the live steel bands two shades darker
(0x34-0x39), sooted at their inner ends round the blown-out hub; under them the pit: a dark floor (0x30 along the X,
0x32 elsewhere) and its torn rim, a ragged lip sloping down into the pit from the socket's floor (painted by its light,
0x33-0x39); the hub's bezel lying tilted on the lower plate, a few dark chunks and two faint embers deep in the X (ramp
7's dark reds glowing 0.2-0.28). Flat like the live pod (no shear), joined into one mesh, triangulated. Deterministic:
no random numbers (mathutils' Perlin noise), no booleans.

Also here, for polish_fruit_ground_wreck.py (the orb's wreck, on the same painting): pit(), pit_outline(), pmat(),
tip(), spin(), bits().

The same frame as fruit_hex_pod: origin at the sprite's centre (pixel 12, 14), +Y up the sprite, +Z up from the
socket's floor (z = 0: the terrain, models.cfg origin and height=-4). models.cfg: model fruit_hex_pod_wreck
enemies/fruit_hex_pod_wreck.glb origin; wreck x25 195 fruit_hex_pod_wreck.

Options after "--": --outdir <dir> (default assets/models/enemies), --preview <prefix>.
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
import polish_fruit_pods as live  # noqa: E402
import polish_panel_pills_wreck as wk  # noqa: E402
from polish_jaw_gun_wreck import jagged, rock, ember, ember_material  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_deli_boss import join  # noqa: E402

NAME = "fruit_hex_pod_wreck"
PIT_C = live.SOCKET_C             # the socket's middle (0, -7)
PIT_R = 6.85                      # the pit's outline: a hexagon, corners left and right (as the sockets), jagged
PIT_JAG = (0.32, 0.55)            # its roughness: how far in and out, about how often
PIT_Z = 0.04                      # the pit's floor (just over the terrain)
ARM = 1.05                        # the X's arms: the floor within this of a diagonal is the darkest
LIP = (0.32, 1.15, 0.36)          # the torn rim: its crest this far in from the outline, its foot this far, its height
STEEL = [(-99, 0x34), (4.9, 0x35), (5.6, 0x36), (6.2, 0x37), (6.75, 0x38), (7.2, 0x39)]   # live's bands, 2 darker
LIP_BANDS = [(-99, 0x33), (5.0, 0x35), (5.8, 0x37), (6.6, 0x39)]
# The vanes crushed together in pairs over the wide slots between them: four plates, up, right, down and left of the
# middle (each spans the quarter between two diagonals), their edges ARM from the diagonals (the X between them), from
# LUMP_IN out to LUMP_GAP inside the pit's edge; per plate (towards, degrees): its crest's height, the crease along the
# crushed slot (how deep), how far it sags into the pit (degrees, about its outer edge), a seed for its crumpling.
LUMP_IN, LUMP_GAP = 1.25, 0.75
LUMPS = [(0.0, 1.15, 0.46, 3.0, 2.1), (90.0, 1.05, 0.4, 4.0, 4.7), (180.0, 1.2, 0.5, 2.5, 6.3),
         (270.0, 1.0, 0.42, 3.5, 8.9)]
SOOT_R = 2.3                      # their inner ends sooted (within this of the middle)
BEZEL = ((-0.3, -11.3), 0.95, 0.42, (24.0, -12.0))   # the hub's bezel lying in the lower plates: at, radius, height,
#                                                       its tilt about x and y (degrees)
CHUNKS = [((2.9, -4.4), (0.55, 0.42, 0.34)), ((-3.2, -10.0), (0.5, 0.4, 0.3)), ((-2.6, -3.9), (0.42, 0.36, 0.28)),
          ((3.4, -10.2), (0.46, 0.4, 0.3))]
EMBERS = [((0.9, -6.1), (0.5, 0.42, 0.2)), ((-1.2, -8.0), (0.42, 0.36, 0.18))]   # (at, radii)
EMBER_GLOW = ((0x72, 0.2), (0x74, 0.28))


_MATS = {}


def pmat(index, glow=0.0, metallic=0.3, roughness=0.45):
    """A palette material of the wrecks' own (shared by the parts; glow in its own colour)."""
    key = (index, glow)
    if key not in _MATS:
        extra = dict(emission=k.level_palette()[index], emission_strength=glow) if glow > 0 else {}
        name = "fwreck_%02x" % index if glow <= 0 else "fwreck_%02x_g%d" % (index, int(round(glow * 100)))
        _MATS[key] = k.material(name, palette=index, metallic=metallic, roughness=roughness, **extra)
    return _MATS[key]


def reset_materials():
    _MATS.clear()


def pit_outline(seed=1.7, radius=PIT_R, centre=PIT_C):
    """The pit's outline (counter-clockwise): a hexagon with its corners left and right, its corners cut a little,
    roughened by noise."""
    cx, cy = centre
    pts = []
    for i in range(6):
        a0, a1 = math.radians(60 * i), math.radians(60 * (i + 1))
        p0 = Vector((cx + radius * math.cos(a0), cy + radius * math.sin(a0)))
        p1 = Vector((cx + radius * math.cos(a1), cy + radius * math.sin(a1)))
        pts.append(tuple(p0 + (p1 - p0) * 0.12))
        pts.append(tuple(p0 + (p1 - p0) * 0.88))
    return jagged(pts, seed, *PIT_JAG)


def shrink(outline, by, centre=PIT_C):
    """The outline moved in towards the middle by `by` pixels (along the rays from the middle)."""
    c = Vector(centre)
    out = []
    for p in outline:
        d = Vector(p) - c
        out.append(tuple(c + d * max(0.05, (d.length - by) / d.length)))
    return out


def on_arm(x, y, centre=PIT_C, arm=ARM):
    """Whether a point lies on the X's arms (within arm of a diagonal through the middle)."""
    dx, dy = x - centre[0], y - centre[1]
    return min(abs(dx - dy), abs(dx + dy)) / math.sqrt(2.0) < arm


def pit(seed=1.7, crest_noise=0.35):
    """The blown-open socket: its dark floor (the X's arms the darkest) and the torn rim round it, a ragged lip from
    the outline (on the socket's floor) up to a crest and down into the pit. Returns [floor, lip]."""
    outline = pit_outline(seed)
    crest = shrink(outline, LIP[0])
    foot = shrink(outline, LIP[1])
    cx, cy = PIT_C
    # the floor: a fan in rings from the middle out to under the lip's foot
    bm = bmesh.new()
    mid = bm.verts.new((cx, cy, PIT_Z))
    rings = []
    for f in (0.3, 0.55, 0.8, 1.0):
        ring = []
        for p in foot:
            d = Vector(p) - Vector((cx, cy))
            q = Vector((cx, cy)) + d * f
            ring.append(bm.verts.new((q.x, q.y, PIT_Z)))
        rings.append(ring)
    n = len(foot)
    for j in range(n):
        bm.faces.new((mid, rings[0][j], rings[0][(j + 1) % n]))
    for a, b in zip(rings, rings[1:]):
        for j in range(n):
            jn = (j + 1) % n
            bm.faces.new((a[j], b[j], b[jn], a[jn]))
    mesh = bpy.data.meshes.new("pit_floor")
    bm.to_mesh(mesh)
    bm.free()
    floor = bpy.data.objects.new("pit_floor", mesh)
    bpy.context.scene.collection.objects.link(floor)
    floor.data.materials.append(pmat(0x32, metallic=0.1, roughness=0.8))
    k.recalc_normals(floor)
    mk.paint(floor, lambda c, nn: pmat(0x30, metallic=0.1, roughness=0.8) if on_arm(c.x, c.y) else None)
    # the lip: outline (on the socket's floor, under it a skirt) - crest - foot
    verts, faces = [], []
    for i, (p, q, r) in enumerate(zip(outline, crest, foot)):
        h = LIP[2] * (1.0 + crest_noise * wk.perlin(p[0] * 0.8 + seed, p[1] * 0.8, 0.3))
        verts += [(p[0], p[1], -0.3), (p[0], p[1], 0.06), (q[0], q[1], h), (r[0], r[1], PIT_Z - 0.02)]
    for i in range(n):
        a, b = 4 * i, 4 * ((i + 1) % n)
        for s in range(3):
            faces.append((a + s, b + s, b + s + 1, a + s + 1))
    lip = k.mesh_object("pit_lip", verts, faces, pmat(0x35))
    k.recalc_normals(lip)
    k.smooth(lip, 50)
    mk.paint(lip, lambda c, nn: pmat(live.band(live.light_value(nn, 5.9), LIP_BANDS)))
    return [floor, lip]


def tip(obj, angle_deg, pivot_r, degrees, centre=PIT_C):
    """Tips an object about the horizontal line tangent to the circle pivot_r round the middle at angle_deg: its
    inner end goes down (degrees > 0)."""
    a = math.radians(angle_deg)
    axis = Vector((-math.sin(a), math.cos(a), 0.0))
    pivot = Vector((centre[0] + pivot_r * math.cos(a), centre[1] + pivot_r * math.sin(a), 0.0))
    obj.data.transform(Matrix.Translation(pivot) @ Matrix.Rotation(math.radians(-degrees), 4, axis) @
                       Matrix.Translation(-pivot))


def spin(obj, degrees, centre=PIT_C):
    """Turns an object about the vertical through the middle."""
    c = Vector((centre[0], centre[1], 0.0))
    obj.data.transform(Matrix.Translation(c) @ Matrix.Rotation(math.radians(degrees), 4, "Z") @ Matrix.Translation(-c))


def pit_radius(angle_deg, radius=PIT_R):
    """How far the pit's hexagon (before roughening) reaches at an angle round its middle."""
    a = angle_deg % 60.0 - 30.0
    return radius * math.cos(math.radians(30.0)) / math.cos(math.radians(a))


def lump_plan(towards, seed, arm=ARM, centre=PIT_C):
    """A plate's plan (counter-clockwise): the quarter of the pit between the diagonals either side of `towards`, its
    edges `arm` off the diagonals, from LUMP_IN out to LUMP_GAP inside the pit's edge, rounded and roughened."""
    c = Vector(centre)
    a0, a1 = math.radians(towards - 45.0), math.radians(towards + 45.0)
    u0, u1 = Vector((math.cos(a0), math.sin(a0))), Vector((math.cos(a1), math.sin(a1)))
    n0, n1 = Vector((-u0.y, u0.x)), Vector((u1.y, -u1.x))

    def angle(p):
        return math.degrees(math.atan2(p.y - c.y, p.x - c.x))

    def edge(u, n):
        s_in = math.sqrt(max(LUMP_IN ** 2 - arm ** 2, 0.01))
        pts, s = [], s_in
        while True:
            p = c + n * arm + u * s
            if (p - c).length > pit_radius(angle(p)) - LUMP_GAP:
                break
            pts.append(p)
            s += 0.5
        return pts
    e0, e1 = edge(u0, n0), edge(u1, n1)
    t0, t1 = angle(e0[-1]), angle(e1[-1])
    if t1 < t0:
        t1 += 360.0
    arc = []
    steps = max(2, int((t1 - t0) / 6.0))
    for i in range(1, steps):
        t = t0 + (t1 - t0) * i / steps
        r = pit_radius(t) - LUMP_GAP
        arc.append(c + Vector((math.cos(math.radians(t)), math.sin(math.radians(t)))) * r)
    pts = [tuple(p) for p in e0 + arc + e1[::-1]]
    pts = mk.chaikin(pts, 1)
    return jagged(pts, seed, 0.16, 0.5)


def drop_bottom(obj):
    """Deletes the faces facing straight down (under the floor: never seen)."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.normal.z < -0.99], context="FACES")
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    return obj


def lump(name, towards, crest, crease, sag, seed, m_steel, centre=PIT_C):
    """A plate of two vanes crushed together: its plan extruded and bevelled as the live vanes, its top crumpled (a
    hump from its inner end, a crease along the crushed slot, noise), sagging into the pit, repainted by its light."""
    cx, cy = centre
    plan = lump_plan(towards, seed)
    obj = mk.prism(name, plan, live.FLOOR_Z, 1.0, m_steel)
    mk.bevel(obj, live.VANE_BEVEL, 2, 30)
    drop_bottom(obj)
    wk.grid_cut(obj, 0.6, min_nz=0.3)
    d = Vector((math.cos(math.radians(towards)), math.sin(math.radians(towards))))
    outer = pit_radius(towards) - LUMP_GAP

    a0, a1 = math.radians(towards - 45.0), math.radians(towards + 45.0)

    def top(x, y):
        rel = Vector((x - cx, y - cy))
        t = min(1.0, max(0.0, (rel.length - LUMP_IN) / (outer - LUMP_IN)))
        hump = 0.45 + (crest - 0.45) * math.sin(math.pi * min(1.0, 0.25 + 0.95 * t)) ** 0.7
        across = abs(rel.x * d.y - rel.y * d.x)
        fold = crease * math.exp(-(across / 0.9) ** 2) * mk.smoothstep(0.1, 0.5, t)
        # (bent down into the X along its edges: a pillow)
        edge = min(abs(rel.x * math.sin(a) - rel.y * math.cos(a)) for a in (a0, a1)) - ARM
        pillow = 0.3 + 0.7 * mk.smoothstep(-0.1, 1.5, edge)
        return max(0.2, (hump - fold) * pillow + 0.2 * wk.fbm(x * 0.75 + seed, y * 0.75 - seed, 0.5))
    for v in obj.data.vertices:
        v.co.z = live.FLOOR_Z + (v.co.z - live.FLOOR_Z) / (1.0 - live.FLOOR_Z) * (top(v.co.x, v.co.y) - live.FLOOR_Z)
    obj.data.update()
    tip(obj, towards, outer, sag)
    k.recalc_normals(obj)
    k.smooth(obj, 50)
    # painted by the light it gets now along smooth contours (live's steel bands, two shades darker); sooted
    # towards the blown-out hub
    from polish_orb_red import band_split
    band_split(obj, [live.light_value(Vector(v.normal), live.STEEL_BASE) for v in obj.data.vertices],
               [(lo, pmat(index)) for lo, index in STEEL])
    mk.paint(obj, lambda c, n: pmat(0x10, metallic=0.2, roughness=0.8)
             if math.hypot(c.x - cx, c.y - cy) < SOOT_R and n.z > 0.3 else None)
    k.smooth(obj, 50)
    return obj


def crushed_vanes():
    m = live.pod_materials(195)
    out = [lump(f"plate{i}", *spec, m[0x3a]) for i, spec in enumerate(LUMPS)]
    wk.clip_below(out, 0.0)
    return out


def bezel():
    """The hub's bezel, knocked off and lying in the lower plates: a squarish puck, its middle dark (where the lamp
    sat)."""
    (x, y), r, h, (tx, ty) = BEZEL
    prof = [(r, 0.0), (r, h - 0.1), (r - 0.12, h), (0.42, h), (0.36, h - 0.18), (0.01, h - 0.18)]
    obj = mk.lathe("bezel", prof, (x, y), pmat(0x37), segments=20, power=3.0)
    k.recalc_normals(obj)
    k.smooth(obj, 40)
    mk.paint(obj, lambda c, n: pmat(0x31) if math.hypot(c.x - x, c.y - y) < 0.4 and n.z > 0.5 else
             pmat(live.band(live.light_value(n, live.STEEL_BASE - 0.3), STEEL)))
    c = Vector((x, y, 0.0))
    obj.data.transform(Matrix.Translation(c + Vector((0, 0, 0.55))) @ Matrix.Rotation(math.radians(tx), 4, "X") @
                       Matrix.Rotation(math.radians(ty), 4, "Y") @ Matrix.Translation(-c))
    return obj


def bits(prefix="pod", embers=True):
    """A few dark chunks and (embers) two faint embers deep in the X."""
    out = []
    for i, ((x, y), radii) in enumerate(CHUNKS):
        out.append(rock(f"{prefix}_chunk{i}", (x, y, PIT_Z), radii, pmat(0x33), 3.0 + 1.7 * i))
    glow = [ember_material(idx, s) for idx, s in EMBER_GLOW] if embers else []
    for i, ((x, y), radii) in enumerate(EMBERS if embers else []):
        out += ember(f"{prefix}_ember{i}", (x, y, PIT_Z), radii, glow, 7.0 + 2.3 * i)
    wk.clip_below(out, 0.0)
    return out


def build_wreck():
    reset_materials()
    parts = pit() + crushed_vanes() + [bezel()] + bits()
    for obj in parts:
        mk.apply(obj)
    triangulate(parts)
    obj = join(parts, NAME)
    obj.data.name = NAME
    return obj


def build():
    options = k.args()
    k.reset()
    obj = build_wreck()
    wk.drop_unused([obj])
    bpy.context.scene.view_settings.view_transform = "Standard"
    mk.report(NAME, [obj], os.path.join(mk.outdir(options), NAME + ".glb"))
    if "preview" in options:
        mk.preview(options["preview"] + NAME, [obj], size=(24, 28), scale=16, distance=0.45)


if __name__ == "__main__":
    build()
