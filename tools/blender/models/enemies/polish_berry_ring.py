"""FRUIT's red twin berry in a bevelled grey ring held by four gold prongs (sheet ', written x27 in models.cfg: sprite
169, 2x2; enemy 1226 of episode 5, a sky enemy, one frame; FRUIT's sky events at 0-125 pixels in from either side,
type 15: 60 appearances). Polished (2026-10-21; it replaces wave3_ae.py's berry_ring). No other enemy, launched ones
included, shows the sprite, and it is no other sprite's pixels mirrored, turned or in other ramps, in any sheet.
models.cfg: model berry_ring enemies/berry_ring.glb (unchanged: centred in height, as the game centres sky models),
sprite x27 169 berry_ring yaw=0.

As the sprite and its 4x upscale draw it (columns and rows of the 24 x 28 sprite): a round grey plate 24 pixels
across (rows 2-25, its middle the sprite's centre), dark gunmetal (0x04-0x08), lit along its upper right edge (0x08,
0x0a-0x0c); a groove engraved round it about three pixels in from its edge (the dark and light lines of columns 2-3
and 19-20, rows 3-4 and 21-22); in its middle a square socket with rounded corners (columns 6-17 of rows 8-18) in a
raised frame (columns 5 and 18, rows 7 and 19), filled by a glossy red twin berry: two plump lobes side by side (the
seam at column 12; ramp 7's dark reds 0x72-0x77), the right one a little higher and lit, a pale glint on it (0x4d at
columns 14-15 of rows 11-12), the left one darker, darkest at its lower left; four gold prongs (0x78-0x7a) at the
socket's corners reaching in over the berry (columns 6-7 of rows 8-9, 16-17 of rows 8-9, 7-8 of rows 17-18, 15-16
of rows 17-18), as the claws of a gem's setting.

Built as such a setting: the plate turned round its middle (each ring of its profile a superellipse, round at its
edge and squarer towards the socket: the rounded edge, the top, the engraved groove, the raised frame and its lip,
the socket's walls and floor), painted by the part of the profile its faces lie on (darker in the groove and the
socket, lighter on the lip and the edge's top), metallic; the berry two plump lobes filling the socket (ellipsoids
squarer over their shoulders in plan (LOBE_POWER), their outer sides drawn in towards their feet, as the sprite's
berry narrows to its bottom like a heart, pressed together along the seam, a notch at its top and bottom), of even
triangles, rising over the frame's lip, painted in bands of shade cut along smooth contours
(polish_orb_red.band_split) laid out for the game's slanted camera (VIEW_TILT): lighter towards the upper left (the
game's sun), a glint on each lobe there (the right one's bright, 0x4d, as the sprite's), darker towards the rim and
the seam, every band glowing faintly in its own red (0.16-0.36) so that the berry reads red, not black, from the
slanted camera (the game's bloom adds to it); the prongs gold claws (0x7a, their tops 0x7b, glowing 0.14) rising from
the frame's corners and bending over the lobes' shoulders, their points pressed into them. Its parts are joined into
one mesh, triangulated before the export (polish_k_pod.triangulate: the output is the same with and without --check).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; origin at the
sprite's centre (pixel 12, 14): column c is x = c + 0.5 - 12, row r is y = 13.5 - r. The plate lies from z 0 to 3.5,
the berry rises to z 7.8.

Replaces wave3_ae.py's berry_ring (its section "' 169: the berry in the ring": RING, berry_ring() with its
@kit.model registration, "berry" in its kit.PROTECT line, its docstring paragraph) and wave3_ae_art.py's BUG (read
only by that section): remove them so that they don't overwrite this model.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouette against
enemy_x27.png), --preview <prefix>.
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
from polish_orb_red import band_split, smoothstep  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_twin_claw import horn  # noqa: E402
from polish_deli_boss import join  # noqa: E402

NAME, SPRITE = "berry_ring", 169
VIEW_TILT = 20.0
T = math.radians(VIEW_TILT)
TOWARDS_VIEW = Vector((0.0, -math.sin(T), math.cos(T)))

# The plate's profile from the socket's floor out to its underside: (centre x, centre y, half-width, half-height,
# superellipse power, z, part). The socket and its frame are centred where the sprite draws them (0, 0.5), the edge on
# the sprite's centre.
PROFILE = [
    (0.0, 0.5, 4.5, 4.0, 4.0, 1.2, "floor"),
    (0.0, 0.5, 5.25, 4.75, 4.0, 1.32, "floor"),
    (0.0, 0.5, 5.7, 5.2, 4.5, 1.8, "wall"),
    (0.0, 0.5, 5.95, 5.45, 4.5, 2.95, "wall"),
    (0.0, 0.5, 6.25, 5.78, 4.2, 3.42, "lip"),
    (0.0, 0.5, 6.85, 6.4, 3.6, 3.5, "lip"),
    (0.0, 0.42, 7.5, 7.1, 3.0, 3.2, "plate"),
    (0.0, 0.32, 8.2, 8.0, 2.4, 3.05, "plate"),
    (0.0, 0.22, 8.75, 8.62, 2.1, 3.0, "groove"),
    (0.0, 0.16, 9.15, 9.05, 2.0, 2.62, "groove"),
    (0.0, 0.1, 9.55, 9.48, 2.0, 3.0, "plate"),
    (0.0, 0.0, 10.75, 10.75, 2.0, 2.95, "plate"),
    (0.0, 0.0, 11.45, 11.45, 2.0, 2.62, "rim"),
    (0.0, 0.0, 11.85, 11.85, 2.0, 2.0, "rim"),
    (0.0, 0.0, 12.0, 12.0, 2.0, 1.2, "side"),
    (0.0, 0.0, 11.8, 11.8, 2.0, 0.4, "side"),
    (0.0, 0.0, 11.2, 11.2, 2.0, 0.0, "under"),
]
PLATE_SEGMENTS = 96
PLATE_PAINT = {"floor": 0x04, "wall": 0x03, "lip": 0x08, "plate": 0x06, "groove": 0x04, "rim": 0x07, "side": 0x05,
               "under": 0x03}     # (parts of one palette index share a material)
PLATE_FINISH = dict(metallic=0.4, roughness=0.36)

# The berry's lobes: middle (x, y, z), radii, how much narrower towards the bottom (a fraction of the half-width).
LOBES = [("berry_l", Vector((-2.85, 0.55, 3.9)), (3.55, 5.35, 3.5), 0.42),
         ("berry_r", Vector((2.95, 0.8, 4.1)), (3.4, 5.2, 3.7), 0.42)]
LOBE_POWER = (2.2, 3.0)              # the plan's superellipse power towards the feet and over the shoulders
# The shades (ramp 7, 0-15): the body (at the lower right and at the upper left of each lobe, as the camera sees it),
# the glint (its place in the lobe's view (u, v), radius, peak) of each lobe, the rim (where it darkens, a fraction of
# the lobe's view radius; the shade at the edge), the seam (how near the other lobe it darkens, the shade there).
BODY = (3.6, 5.6)
GLINTS = {"berry_l": ((-0.32, 0.4), 0.26, 2.6), "berry_r": ((-0.28, 0.42), 0.24, 4.8)}
RIM_FROM, RIM_EDGE = 0.7, 2.4
SEAM_NEAR, SEAM_SHADE = 1.1, 2.6
# (lowest shade, palette index, emission strength in its own colour)
BANDS = [(-99.0, 0x72, 0.16), (2.5, 0x73, 0.16), (3.5, 0x74, 0.18), (4.5, 0x75, 0.2), (5.5, 0x76, 0.24),
         (6.5, 0x77, 0.28), (8.0, 0x4d, 0.36)]
BERRY_FINISH = dict(metallic=0.05, roughness=0.16)

# The prongs: base on the frame's lip, tip over the berry's shoulder (x, y), the tip's height over the berry's
# surface there; radius at the base and at the tip.
PRONGS = [((-6.05, 6.05), (-4.45, 4.55)), ((6.05, 6.05), (4.45, 4.55)),
          ((-5.95, -5.0), (-3.6, -3.45)), ((5.95, -5.0), (3.6, -3.45))]
PRONG_LIFT, PRONG_R = 0.08, (0.62, 0.15)
GOLD = [("gold", 0x7a), ("gold_light", 0x7b)]
GOLD_FINISH = dict(metallic=0.65, roughness=0.28)


def materials():
    pal = k.level_palette()
    m = {}
    for part, index in PLATE_PAINT.items():
        m[part] = k.material(f"bring_plate_{index:02x}", palette=index, **PLATE_FINISH)
    for _, index, glow in BANDS:
        m[index] = k.material(f"berry_{index:02x}", palette=index, emission=pal[index], emission_strength=glow,
                              **BERRY_FINISH)
    for name, index in GOLD:
        m[name] = k.material(f"bring_{name}", palette=index, emission=pal[index], emission_strength=0.14,
                             **GOLD_FINISH)
    return m


# --- The plate -------------------------------------------------------------------------------------------------------

def plate(m):
    """The plate turned round its middle: its profile's rings (superellipses), the floor closed to a point."""
    rings = []
    for cx, cy, hw, hh, power, z, _ in PROFILE:
        ring = []
        for j in range(PLATE_SEGMENTS):
            u, v = mk.superellipse_point(2 * math.pi * j / PLATE_SEGMENTS, power)
            # The same angle round for every ring, so that the quads between them stay even.
            ring.append(Vector((cx + hw * u, cy + hh * v, z)))
        rings.append(ring)
    first, last = PROFILE[0], PROFILE[-1]
    obj = k.loft("bring_plate", rings, m["plate"], start_point=(first[0], first[1], first[5]),
                 end_point=(last[0], last[1], last[5]))
    n = PLATE_SEGMENTS
    count = (len(rings) - 1) * n
    slots = {}
    for poly in obj.data.polygons:
        if poly.index < count:      # the quads leading out to a ring are that ring's part
            part = PROFILE[poly.index // n + 1][6]
        elif poly.index < count + n:
            part = "floor"
        else:
            part = "under"
        mat = m[part]
        if mat.name not in slots:
            slots[mat.name] = mk.slot_of(obj, mat)
        poly.material_index = slots[mat.name]
    k.recalc_normals(obj)
    return k.smooth(obj, 50)


# --- The berry -------------------------------------------------------------------------------------------------------

def lobe_power(y):
    """The lobes' plan is squarer over their shoulders (y > 0) than towards their feet."""
    return LOBE_POWER[1] if y > 0 else LOBE_POWER[0]


def plan_scale(x, y):
    """How much further out than a circle the lobes' plan (a superellipse) reaches at (x, y)."""
    h = math.hypot(x, y)
    if h < 1e-9:
        return 1.0
    c, s = abs(x) / h, abs(y) / h
    power = lobe_power(y)
    return (c ** power + s ** power) ** (-1.0 / power)


def lobe_point(centre, radii, taper, d):
    """The lobe's surface point in the direction d (a unit vector): an ellipsoid whose plan is a little squarer (so
    that the lobes fill the socket), its outer side drawn in towards its bottom (taper: the twin berry narrows to its
    foot as a heart does), its side along the seam hardly."""
    rx, ry, rz = radii
    f = plan_scale(d.x, d.y)
    p = Vector((d.x * rx * f, d.y * ry * f, d.z * rz))
    outer = (p.x < 0.0) == (centre.x < 0.0)
    p.x *= 1.0 - (taper if outer else taper * 0.15) * smoothstep(-0.25, 1.0, -d.y)
    return centre + p


def lobe_mesh(name, centre, radii, taper):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=3, radius=1.0)

    def seen(v):
        return v.co.normalized().dot(TOWARDS_VIEW) > -0.3

    edges = [e for e in bm.edges if all(seen(v) for v in e.verts)]
    bmesh.ops.subdivide_edges(bm, edges=edges, cuts=1, use_grid_fill=True)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    for v in bm.verts:
        v.co = lobe_point(centre, radii, taper, v.co.normalized())
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def lobe_shade(name, centre, radii, other, p):
    """The shade (ramp 7) of a lobe at its surface point p, as the slanted camera sees it."""
    rx, ry, rz = radii
    rel = p - centre
    u = rel.x / rx
    v = (rel.y * math.cos(T) + rel.z * math.sin(T)) / math.hypot(ry * math.cos(T), rz * math.sin(T))
    rho = math.hypot(u, v)
    nrm = Vector((rel.x / rx ** 2, rel.y / ry ** 2, rel.z / rz ** 2)).normalized()
    if nrm.dot(TOWARDS_VIEW) < 0.0:
        return BODY[0] - 0.6
    lit = smoothstep(-1.0, 1.0, (-u + v) * 0.70710678)
    s = BODY[0] + (BODY[1] - BODY[0]) * lit
    (gu, gv), gr, peak = GLINTS[name]
    s += peak * math.exp(-((u - gu) ** 2 + (v - gv) ** 2) / gr ** 2)
    s += (RIM_EDGE - s) * smoothstep(RIM_FROM, 1.0, rho)
    # Darker along the seam, where the lobes press together.
    ocentre, oradii = other
    q = p - ocentre
    near = math.sqrt((q.x / oradii[0]) ** 2 + (q.y / oradii[1]) ** 2 + (q.z / oradii[2]) ** 2) - 1.0
    s += (SEAM_SHADE - s) * (1.0 - smoothstep(0.0, SEAM_NEAR * 0.25, near))
    return s


def berry(m):
    objs = []
    for i, (name, centre, radii, taper) in enumerate(LOBES):
        _, ocentre, oradii, _ = LOBES[1 - i]
        obj = lobe_mesh(name, centre, radii, taper)
        values = [lobe_shade(name, centre, radii, (ocentre, oradii), v.co.copy()) for v in obj.data.vertices]
        band_split(obj, values, [(lowest, m[index]) for lowest, index, _ in BANDS])
        k.smooth(obj, 75)
        objs.append(obj)
    return objs


def berry_surface_z(x, y):
    """The berry's top at (x, y), or the socket's floor."""
    best = 1.2
    for _, centre, (rx, ry, rz), taper in LOBES:
        dy = (y - centre.y) / ry
        # The lobe's half-width at this height on this side (its taper).
        outer = ((x - centre.x) < 0.0) == (centre.x < 0.0)
        half = rx * (1.0 - (taper if outer else taper * 0.15) * smoothstep(-0.25, 1.0, -dy)) if abs(dy) < 1 else 0.0
        if half <= 0:
            continue
        dx = (x - centre.x) / half
        power = lobe_power(dy)
        t = 1.0 - (abs(dx) ** power + abs(dy) ** power) ** (2.0 / power)
        if t > 0:
            best = max(best, centre.z + rz * math.sqrt(t))
    return best


# --- The prongs ------------------------------------------------------------------------------------------------------

def prongs(m):
    out = []
    for i, ((bx, by), (tx, ty)) in enumerate(PRONGS):
        z0 = 3.3
        z1 = berry_surface_z(tx, ty) + PRONG_LIFT
        # A claw: rising from the lip's corner, bending over the lobe's shoulder and pressing its point into it.
        top = z1 + 0.45
        r0, r1 = PRONG_R

        def at(f, z, r):
            return (bx + (tx - bx) * f, by + (ty - by) * f, z, r, r * 0.8)
        controls = [at(0.0, z0, r0), at(0.12, top - 0.35, r0 * 0.85), at(0.55, top + 0.1, (r0 + r1) * 0.45),
                    at(1.0, z1, r1)]
        # horn() runs from its tip to its root: reversed
        obj, _ = horn(f"bring_prong{i}", list(reversed(controls)), m["gold"], 10)
        mk.paint(obj, lambda c, n: m["gold_light"] if n.z > 0.6 else None)
        out.append(obj)
    return out


def build_model():
    m = materials()
    parts = [plate(m)] + berry(m) + prongs(m)
    for obj in parts:
        mk.apply(obj)
    bpy.context.view_layer.update()
    return parts


def build():
    k.reset()
    options = k.args()
    out = mk.outdir(options)
    parts = build_model()
    triangulate(parts)  # the same split every run (with and without --check)
    parts = [join(parts, NAME)]
    if "check" in options:
        sheets = options["check"]
        sheet = os.path.join(sheets, "enemy_x27.png") if os.path.isdir(sheets) else sheets
        mk.compare("%s (x27 %d)" % (NAME, SPRITE), mk.coverage(parts, 24, 28), k.sprite_mask(sheet, SPRITE))
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    mk.report(NAME, parts, os.path.join(out, NAME + ".glb"))
    if "preview" in options:
        mk.preview(options["preview"] + NAME, parts, scale=20, distance=0.6)


if __name__ == "__main__":
    build()
