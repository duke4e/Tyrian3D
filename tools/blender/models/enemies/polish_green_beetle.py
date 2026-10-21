"""The green beetle of MARKERS and CRUSTGATE (sheet V sprite 165, 2x2: 22 x 26 pixels in the 24 x 28 cell; episode 2's
and 6's enemy 814, in the sky, flying down the screen; one frame, not animated), polished (2026-10-21; it replaces
wave3_t_ships.py's green_beetle(), a shell lofted round a faceted gem with a head inflated from the sprite's pixels).
models.cfg: sprite v 165 green_beetle yaw=0 (unchanged).

V 203 is this sprite upside down pixel for pixel (and, as the beetle is symmetric, turned round), but no enemy shows
it; no other sprite has its pixels, and no other enemy shows V 165.

As the sprite and its 4x upscale draw it (columns and rows of the 24 x 28 cell), symmetric about the line between
columns 11 and 12 (x 0): a beetle of glossy green armour (the green ramp 2) with blue gems (ramp 9) and a brown jewel
(ramp 1). Its round body (columns 4-19 of rows 14-25, widest at rows 18-21) carries a big round blue gem in its upper
middle (columns 8-15 of rows 14-21; dark blue, lighter towards its lower left) in a dark green bezel; two blue lobes
low on its sides like wing cases (columns 5-9 and 14-18 of rows 21-25, slanting in towards the bottom) in light green
rims, two small blue studs above them (columns 6 and 17 of row 16), a light green ridge either side of the middle
down from the gem, and between the lobes a small green knob (columns 9-14 of rows 23-25) with two little points
under it (row 26). Above the body the head: a shield (columns 6-17 of rows 2-14: four pixels either side of the
middle, flaring to six at row 11, two small points on its top edge at columns 9-10 and 13-14) with a diamond-shaped
brown socket in its middle (columns 9-14 of rows 7-11, a channel up from it to row 4) holding a round tan jewel
(columns 11-12 of rows 8-9). Either side of the head a broad horn like a crescent (columns 1-6 of rows 1-14),
joined to the shield along a dark groove at rows 6-10 (columns 7 and 16), its upper part curving up and in to a
point (columns 5-6 of row 1), its lower end blunt (row 14); along it a broad outer ridge, lit, and a narrower inner
one.

Built from lofts and painted ellipsoids (tyrkit, polish_balls.painted_ball): the body and the shield lofts of
rounded sections; the big gem, the lobes, the knob and the jewel painted ellipsoids, their light in bands with
smooth borders, the gems and the jewel glowing a little in their own colours (well under 1) so that they don't read
black from the game's slanted camera; the gem's dark bezel and the lobes' light rims rings of round section; each
horn two tapering tubes side by side along the crescent (polish_twin_claw.horn), the groove where they meet, rising
to its point; the socket a thin plate laid into the shield (polish_redjet.facet) under the lens-shaped frame of a
raised bar, the ridges a thin bar each, the points small tapering tubes. The left half's parts are built and
mirrored about x = 0. Every mesh is triangulated before the export (polish_k_pod.triangulate), so --check doesn't
change the output.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; origin at the
sprite's centre (pixel 12, 14): column c is x = c + 0.5 - 12, row r is y = 13.5 - r. A flying object: the game
centres it in height.

Replaces wave3_t_ships.py's green_beetle() (its "# --- V 165: the green beetle" section with the
@model("green_beetle", [165]) registration, and the docstring's lines on it), gem() (only green_beetle() uses it)
and its "import bmesh" (only gem() uses it), and wave3_t_art.py's BEETLE (only green_beetle() reads it; wave1_d.py's
art.BEETLE is wave1_d_art's): remove them so that they don't overwrite this model.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouette against
enemy_V.png sprite 165), --preview <prefix>, --stats 1 (the triangles per part).
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
from polish_balls import Ellipsoid, painted_ball  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_redjet import Curve, chaikin, facet, resample  # noqa: E402
from polish_twin_claw import horn, paint_sections  # noqa: E402

NAME = "green_beetle"

# The body along y: half-width in plan (through the middles of the sprite's steps), the height of its top, of its
# underside.
BODY = Curve([(-12.15, 2.4, 2.4, 1.0), (-11.7, 4.3, 3.3, 0.7), (-11.0, 5.3, 3.9, 0.55), (-10.0, 6.25, 4.4, 0.5),
              (-9.0, 6.95, 4.8, 0.5), (-8.0, 7.45, 5.1, 0.5), (-6.5, 7.65, 5.3, 0.5), (-5.0, 7.55, 5.35, 0.5),
              (-3.8, 7.15, 5.3, 0.5), (-2.6, 6.75, 5.2, 0.55), (-1.6, 6.05, 5.0, 0.6), (-0.6, 5.0, 4.75, 0.75),
              (0.1, 3.8, 4.5, 0.95)])
BODY_Y = (-12.15, 0.1)
BODY_POWER = 2.3
# The big gem (columns 8-15 of rows 14-21): middle, radii; its bezel's radius and thickness.
GEM = Ellipsoid((0.0, -4.0, 4.45), (3.75, 3.75, 2.05))
BEZEL = (3.95, 0.62)
# The left lobe (columns 5-9 of rows 21-25): middle, radii (across, along, up), turned about z (degrees; its long
# axis slanting in to the bottom), tilted out (degrees); its rim's thickness.
LOBE = ((-4.55, -9.45, 3.2), (1.3, 2.75, 1.05), 32.0, 22.0)
LOBE_RIM = 0.42
# The stud above it (column 6 of row 16), the ridge down beside the middle from the gem (columns 8-9 of rows 21-24).
STUD = ((-5.45, -2.4), 0.62)
RIDGE = [(-3.05, -7.0), (-2.75, -8.6), (-2.4, -10.2), (-2.05, -11.2)]
# The knob between the lobes (columns 9-14 of rows 23-25), the two points under it (row 26).
KNOB = ((0.0, -10.25), (1.75, 1.45, 1.05))
POINT = [(-1.35, -11.25, 2.6, 0.62, 0.5), (-1.85, -12.2, 2.2, 0.42, 0.35), (-2.05, -12.85, 2.0, 0.1, 0.1)]

# The shield along y: half-width, the height of its top, of its underside (four pixels either side of the middle,
# flaring to six at row 11).
SHIELD = Curve([(-0.9, 3.6, 4.7, 2.2), (0.0, 4.15, 5.1, 2.1), (1.0, 4.85, 5.5, 2.0), (2.1, 5.6, 5.8, 2.0),
                (3.0, 5.2, 6.0, 2.0), (4.0, 4.75, 6.15, 2.0), (6.0, 4.6, 6.25, 2.0), (7.8, 4.7, 6.2, 2.0),
                (8.7, 4.75, 6.05, 2.1), (9.8, 4.1, 5.7, 2.3), (10.6, 3.4, 5.25, 2.6), (11.0, 2.6, 4.85, 2.8)])
SHIELD_Y = (-0.9, 11.0)
SHIELD_POWER = 2.8
# The two points on its top edge (columns 9-10 and 13-14 of rows 2-3): the left one's middle line.
TOP_POINT = [(-1.55, 9.8, 5.6, 0.85, 0.7), (-1.85, 10.9, 5.75, 0.68, 0.55), (-2.0, 11.6, 5.8, 0.38, 0.32),
             (-2.05, 12.05, 5.82, 0.08, 0.08)]
# The socket: a diamond (columns 9-14 of rows 7-11) and the channel up from it (columns 11-12 of rows 4-6); how deep
# it lies in the shield; the jewel in it (columns 11-12 of rows 8-9).
SOCKET = [(0.0, 2.05), (2.95, 4.85), (1.0, 6.95), (0.95, 9.9), (-0.95, 9.9), (-1.0, 6.95), (-2.95, 4.85)]
SOCKET_SINK = 0.3
JEWEL = Ellipsoid((0.0, 4.7, 0.0), (1.3, 1.4, 0.95))
# The raised frame round the socket, like a lens: from the left top point down round the socket to the V under it
# (rows 10-12) and up again to the right one (the light greens of columns 8-10 and 13-15).
SOCKET_RIM = [(-1.75, 10.15), (-2.45, 9.0), (-3.25, 7.4), (-3.75, 5.6), (-3.45, 4.2), (-2.3, 2.95), (-0.9, 1.8),
              (0.0, 1.3), (0.9, 1.8), (2.3, 2.95), (3.45, 4.2), (3.75, 5.6), (3.25, 7.4), (2.45, 9.0), (1.75, 10.15)]
# The left horn: two ridges side by side along a crescent, (x, y, z, half-width in plan, half-height) from its blunt
# lower end (row 14) to its point (columns 5-6 of row 1).
HORN_OUTER = [(-8.55, -0.55, 2.7, 0.95, 0.85), (-9.45, 1.4, 3.05, 1.35, 1.05), (-9.6, 3.6, 3.5, 1.45, 1.15),
              (-9.5, 5.8, 3.95, 1.45, 1.15), (-9.05, 8.0, 4.45, 1.35, 1.08), (-8.3, 9.9, 4.95, 1.15, 0.95),
              (-7.35, 11.4, 5.35, 0.82, 0.72), (-6.4, 12.45, 5.6, 0.42, 0.4), (-5.95, 12.95, 5.7, 0.08, 0.08)]
HORN_INNER = [(-7.85, 0.4, 3.0, 0.7, 0.65), (-7.9, 2.2, 3.45, 0.95, 0.85), (-6.2, 4.4, 4.15, 1.85, 1.2),
              (-5.75, 6.4, 4.55, 1.95, 1.22), (-6.1, 8.4, 4.85, 1.45, 1.04), (-6.25, 10.3, 5.15, 0.98, 0.8),
              (-6.05, 11.7, 5.45, 0.5, 0.45), (-5.95, 12.6, 5.6, 0.1, 0.1)]


def materials():
    pal = k.level_palette()

    def green(name, index, roughness=0.3):
        return k.material(name, palette=index, metallic=0.35, roughness=roughness)

    def lit(name, index, strength, roughness=0.12, metallic=0.1):
        return k.material(name, palette=index, metallic=metallic, roughness=roughness, emission=pal[index],
                          emission_strength=strength)
    return {
        "body": green("gbt_body", 0x26),
        "shield": green("gbt_shield", 0x27, 0.28),
        "light": green("gbt_light", 0x29, 0.26),
        "dark": green("gbt_dark", 0x23, 0.42),
        "horn": green("gbt_horn", 0x28, 0.28),
        "gem_rim": lit("gbt_gem_rim", 0x93, 0.15),
        "gem": lit("gbt_gem", 0x95, 0.22),
        "gem_light": lit("gbt_gem_light", 0x99, 0.38),
        "gem_core": lit("gbt_gem_core", 0x9c, 0.5),
        "socket": k.material("gbt_socket", palette=0x12, metallic=0.25, roughness=0.5),
        "socket_rim": k.material("gbt_socket_rim", palette=0x11, metallic=0.2, roughness=0.6),
        "jewel": lit("gbt_jewel", 0x17, 0.18, 0.2, 0.3),
        "jewel_light": lit("gbt_jewel_light", 0x1b, 0.35, 0.15, 0.3),
    }


# --- Helpers -----------------------------------------------------------------------------------------------------

def section_top(table, power, x, y):
    """The top of a loft of k.ring sections (half-width, top, underside by y) at (x, y), or None outside it."""
    hw, top, under = table(y)
    if abs(x) >= hw:
        return None
    zc = under + 0.4
    return zc + (top - zc) * (1 - (abs(x) / hw) ** power) ** (1 / power)


def loft_along_y(name, table, y0, y1, power, mat, count=30, segments=36):
    rings = []
    for i in range(count + 1):
        t = i / count
        y = y0 + (y1 - y0) * (0.5 - 0.5 * math.cos(math.pi * t))
        hw, top, under = table(y)
        zc = under + 0.4
        rings.append(k.ring(y, max(hw, 0.08), 1.0, segments, z=zc, top=max(top - zc, 0.1), bottom=0.4, power=power))
    hw, top, under = table(y0)
    start = (0.0, y0 - 0.15, under + 0.6)
    hw, top, under = table(y1)
    end = (0.0, y1 + 0.15, (top + under) / 2)
    obj = k.loft(name, rings[1:-1], mat, start_point=start, end_point=end)
    return k.smooth(obj, 55)


def body_top(x, y):
    return section_top(BODY, BODY_POWER, x, y)


def shield_top(x, y):
    return section_top(SHIELD, SHIELD_POWER, x, y)


def on_surface(points, surface, lift=0.0):
    """(x, y) points lifted onto a surface (z = surface(x, y) + lift)."""
    return [Vector((x, y, (surface(x, y) or 0.0) + lift)) for x, y in points]


def thin_tube(name, points, radius, mat, segments=8, squash=0.75, iterations=1):
    """A thin round bar through 3D points (rounded with Chaikin), closed at its ends."""
    pts = [Vector(p) for p in mk.chaikin([tuple(p) for p in points], iterations, closed=False)] if len(points) > 2 \
        else [Vector(p) for p in points]
    rings = []
    for i, p in enumerate(pts):
        a, b = pts[max(i - 1, 0)], pts[min(i + 1, len(pts) - 1)]
        t = (b - a).normalized()
        side = t.cross(Vector((0, 0, 1)))
        side = side.normalized() if side.length > 1e-6 else Vector((1, 0, 0))
        up = side.cross(t).normalized()
        rings.append([p + side * math.cos(2 * math.pi * j / segments) * radius +
                      up * math.sin(2 * math.pi * j / segments) * radius * squash for j in range(segments)])
    t0, t1 = (pts[1] - pts[0]).normalized(), (pts[-1] - pts[-2]).normalized()
    obj = k.loft(name, rings, mat, start_point=pts[0] - t0 * radius * 0.7, end_point=pts[-1] + t1 * radius * 0.7)
    return k.smooth(obj, 60)


def gem_paint(light_at, light_size, core_size, glare_at, glare_size, rim_z=0.32):
    """painted_ball fields: a darker rim where the gem turns away, a lighter patch (its core lighter still) and a
    small glare."""
    def rim(p, n):
        return n.z

    def light(p, n):
        if n.z <= 0.2:
            return 0.0
        u, v = (p.x - light_at[0]) / light_size[0], (p.y - light_at[1]) / light_size[1]
        return math.exp(-(u * u + v * v))

    def glare(p, n):
        if n.z <= 0.4:
            return 0.0
        u, v = (p.x - glare_at[0]) / glare_size[0], (p.y - glare_at[1]) / glare_size[1]
        return math.exp(-(u * u + v * v))
    return [(rim, (rim_z,), ("rim", "body")),
            (light, (0.45, core_size), (None, "light", "core")),
            (glare, (0.55,), (None, "core"))]


# --- The parts ---------------------------------------------------------------------------------------------------

def body(m):
    obj = loft_along_y("body", BODY, *BODY_Y, BODY_POWER, m["body"], 24, 26)
    mk.paint(obj, lambda c, n: m["dark"] if n.z < 0.3 else None)
    parts = [obj]
    # The big gem, its bezel.
    mats = {"rim": m["gem_rim"], "body": m["gem"], "light": m["gem_light"], "core": m["gem_core"]}
    parts.append(painted_ball("gem", GEM, gem_paint((-0.75, -5.1), (1.9, 1.7), 0.8, (-1.5, -2.6), (0.75, 0.6)), mats,
                              subdivisions=3, smooth_angle=80))
    radius, thick = BEZEL
    cz = GEM.centre.z + 0.15
    bezel = torus("bezel", (GEM.centre.x, GEM.centre.y, cz), radius, thick, m["dark"])
    parts.append(bezel)
    # The left lobe in its rim, the stud, the ridge.
    (x, y, z), radii, turn, tilt = LOBE
    lobe_shape = Ellipsoid((0.0, 0.0, 0.0), radii)
    lmats = {"rim": m["gem_rim"], "body": m["gem"], "light": m["gem_light"], "core": m["gem_core"]}
    lobe = painted_ball("lobe_l", lobe_shape, gem_paint((-0.35, 0.9), (0.9, 1.5), 0.75, (-0.4, 1.4), (0.4, 0.6)),
                        lmats, subdivisions=3, smooth_angle=80)
    place = Matrix.Translation((x, y, z)) @ Matrix.Rotation(math.radians(turn), 4, "Z") @ \
        Matrix.Rotation(math.radians(-tilt), 4, "Y")
    lobe.data.transform(place)
    rim = torus("lobe_rim_l", (0.0, 0.0, 0.1), 1.0, LOBE_RIM, m["light"], scale=(radii[0] + 0.12, radii[1] + 0.12))
    rim.data.transform(place)
    (sx, sy), sr = STUD
    stud = k.smooth(k.ellipsoid("stud_l", (sx, sy, (body_top(sx, sy) or 3.0) - 0.15), (sr, sr, sr * 0.75),
                                m["gem"], 12, 6), 70)
    ridge = thin_tube("ridge_l", on_surface(RIDGE, body_top, -0.05), 0.5, m["light"], 6)
    (kx, ky), kr = KNOB
    knob = painted_ball("knob", Ellipsoid((kx, ky, (body_top(kx, ky) or 3.5) - 0.35), kr),
                        gem_paint((-0.5, ky + 0.6), (0.9, 0.7), 0.7, (-0.6, ky + 0.7), (0.4, 0.35)),
                        {"rim": m["body"], "body": m["light"], "light": m["horn"], "core": m["light"]},
                        subdivisions=2, smooth_angle=80)
    point, _ = horn("point_l", POINT, m["body"], 8)
    return parts + [knob], [lobe, rim, stud, ridge, point]


def torus(name, centre, radius, thick, mat, segments=28, sides=6, scale=None):
    """A ring of round section round a vertical axis (scale: an oval's half-axes in place of the radius)."""
    cx, cy, cz = centre
    sx, sy = scale if scale else (radius, radius)
    verts, faces = [], []
    for j in range(segments):
        a = 2 * math.pi * j / segments
        ca, sa = math.cos(a), math.sin(a)
        for i in range(sides):
            b = 2 * math.pi * i / sides
            verts.append((cx + (sx + thick * math.cos(b)) * ca, cy + (sy + thick * math.cos(b)) * sa,
                          cz + thick * 0.8 * math.sin(b)))
    for j in range(segments):
        for i in range(sides):
            a0, a1 = j * sides + i, j * sides + (i + 1) % sides
            b0, b1 = ((j + 1) % segments) * sides + i, ((j + 1) % segments) * sides + (i + 1) % sides
            faces.append((a0, b0, b1, a1))
    obj = k.mesh_object(name, verts, faces, mat)
    k.recalc_normals(obj)
    return k.smooth(obj, 60)


def shield(m):
    obj = loft_along_y("shield", SHIELD, *SHIELD_Y, SHIELD_POWER, m["shield"], 24, 26)
    mk.paint(obj, lambda c, n: m["dark"] if n.z < 0.32 else None)
    # The socket sunk into it, the jewel, the light rim round its lower half.
    outline = resample(chaikin(SOCKET, 1), 0.5)
    outline = outline if sum(outline[i][0] * outline[(i + 1) % len(outline)][1] -
                             outline[(i + 1) % len(outline)][0] * outline[i][1]
                             for i in range(len(outline))) > 0 else outline[::-1]
    socket = facet("socket", outline, lambda x, y: (shield_top(x, y) or 5.0) - SOCKET_SINK, SOCKET_SINK + 0.12,
                   m["socket"], rim=0.18, steps=2, dome=0.0, dome_rings=1, sink=0.4)
    mk.paint(socket, lambda c, n: m["socket_rim"] if n.z < 0.7 else None)
    jz = (shield_top(JEWEL.centre.x, JEWEL.centre.y) or 6.0) - 0.25
    jewel = painted_ball("jewel", Ellipsoid((JEWEL.centre.x, JEWEL.centre.y, jz), JEWEL.radii),
                         gem_paint((-0.35, 5.1), (0.6, 0.55), 0.7, (-0.4, 5.15), (0.3, 0.3), rim_z=0.25),
                         {"rim": m["socket"], "body": m["jewel"], "light": m["jewel_light"], "core": m["jewel_light"]},
                         subdivisions=2, smooth_angle=80)
    rim = thin_tube("socket_rim", on_surface(SOCKET_RIM, shield_top, -0.12), 0.45, m["light"], 6)
    return [obj, socket, jewel, rim]


def left_head_parts(m):
    point, centres = horn("top_point_l", TOP_POINT, m["shield"], 8)
    outer, oc = horn("horn_outer_l", HORN_OUTER, m["horn"], 12)
    paint_sections(outer, oc, 12, lambda c, n: m["dark"] if n.z < 0.2 else
                   m["light"] if n.x < -0.35 and n.z > 0.35 else None)
    inner, ic = horn("horn_inner_l", HORN_INNER, m["shield"], 10)
    paint_sections(inner, ic, 10, lambda c, n: m["dark"] if n.z < 0.3 or n.x < -0.55 else None)
    return [point, outer, inner]


# --- Building ----------------------------------------------------------------------------------------------------

def mirrored(objects):
    out = []
    for obj in objects:
        copy = obj.copy()
        copy.data = obj.data.copy()
        copy.name = obj.name[:-2] + "_r" if obj.name.endswith("_l") else obj.name + "_r"
        bpy.context.scene.collection.objects.link(copy)
        copy.data.transform(Matrix.Scale(-1, 4, (1, 0, 0)))
        copy.data.flip_normals()
        out.append(copy)
    return out


def build():
    options = k.args()
    out = mk.outdir(options)
    k.reset()
    m = materials()
    middle, left = body(m)
    middle += shield(m)
    left += left_head_parts(m)
    parts = middle + left + mirrored(left)
    triangulate(parts)
    bpy.context.view_layer.update()
    if "stats" in options:
        for obj in parts:
            print("  %-16s %5d triangles" % (obj.name, len(obj.data.polygons)))
    if "check" in options:
        sheet = os.path.join(options["check"], "enemy_V.png")
        mk.compare("green_beetle (V 165)", mk.coverage(parts, 24, 28), k.sprite_mask(sheet, 165))
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    mk.report(NAME, parts, os.path.join(out, NAME + ".glb"))
    if "preview" in options:
        mk.preview(options["preview"] + NAME, parts, distance=0.7)


if __name__ == "__main__":
    build()
