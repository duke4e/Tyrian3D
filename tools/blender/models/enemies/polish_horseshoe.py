"""The grey horseshoe of SURFACE and CORE (sheet 3 sprite 126, 2x2: 24 x 28 pixels; static; sky and top layers;
also INVADERS, ROOST and COLLECTOR; enemies 202 and 1594), polished (2026-10-19; it replaces wave2_g.py's
horseshoe(), a ring inflated from the sprite's outline with tan plates laid on it). models.cfg: sprite 3 126
horseshoe yaw=0.

As the 4x upscale draws it: a horseshoe magnet hanging in the air, its bend at the top. A grey iron core: a band
over the top (rows 0-3, thinner there) bending down into two thick legs (columns 2-7 and 17-22); on each leg a
tan sleeve, the coil (rows 7-13), a black seam above and below it (rows 6 and 14); under the coils the legs end
in heavy grey pole pieces (rows 15-21) that bulge out and lean in towards each other, nearly closing the hole
(a V between them, rows 15-18), lit along their upper left; a short keeper bar with a stud bridges them low down
(columns 9-15 of row 20); their lower ends are two stubby feet (rows 21-23). The hole in the middle (columns 8-16
of rows 4-14) is open: the background shows through.

So it is built as an electromagnet: the core swept along a U, its section a rounded rectangle, wider across the
legs (6 pixels) than over the bend (4); the coils sleeves of tan windings round the legs; the pole pieces two
soft blocks (remeshed and smoothed, as the upscale paints them) with a groove where each joins its leg; the keeper
a bar between their inner faces.

The sprite is symmetric about its column 12 (x = 0.5 here): the parts are built about x = 0, the left ones
mirrored, and moved there (AXIS_X). Origin at the sprite's centre (pixel 12, 14); +Y up the sprite, +Z towards
the camera; the magnet's bottom at z = 0 (the game centres sky objects in height).

Replaces wave2_g.py's horseshoe() (and its @model entry; wave2_g_art.py's E3_126, which nothing else uses): remove
it so that it doesn't overwrite this model.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouette against
enemy_3.png), --preview <prefix>.
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
from polish_machine_kit import k  # noqa: E402

AXIS_X = 0.5
# The core's centre line: the legs at x = +-LEG_X from LEG_FOOT up to BEND_Y, then a half ellipse over the top
# (half-width LEG_X, rising BEND_RISE above BEND_Y).
LEG_X = 7.5
LEG_FOOT = -3.0
BEND_Y = 5.0
BEND_RISE = 7.0
# The core's section: half-width across the band (legs, bend) and half-height, a rounded rectangle (power).
LEG_HALF_W, BEND_HALF_W = 2.75, 1.85
CORE_HALF_H = 1.9
CORE_Z = 2.3                # the core's middle height
CORE_POWER = 3.2
# The coils round the legs: from y0 to y1, a little proud of the core, WINDINGS ridges.
COIL = (0.15, 7.15)
COIL_PROUD = 0.42
WINDINGS = 6
# The pole pieces: (x0, x1, y0, y1) of the left one's block before rounding, its height; how far its inner side
# leans in at the bottom.
POLE = (-10.25, -1.6, -9.6, -0.6)
POLE_TOP = 5.3
# The keeper bar between the pole pieces (y, z, radius) and its stud.
KEEPER = (-6.45, 1.7, 0.95)


def ring_xz(centre, normal, half_w, half_h, power, segments=24):
    """A section round centre: across `normal` (horizontal) half_w, up half_h, a superellipse."""
    pts = []
    up = Vector((0, 0, 1))
    for j in range(segments):
        u, v = mk.superellipse_point(2 * math.pi * j / segments, power)
        pts.append(centre + normal * (u * half_w) + up * (v * half_h))
    return pts


def centre_line(step=1.0):
    """The core's centre line from the left leg's foot over the bend to the right leg's foot, with the band's
    half-width at each point: (point, tangent, half_w)."""
    pts = []
    y = LEG_FOOT
    while y < BEND_Y:
        pts.append((Vector((-LEG_X, y, CORE_Z)), Vector((0, 1, 0)), LEG_HALF_W))
        y += step
    steps = 30
    for i in range(steps + 1):
        a = math.pi - math.pi * i / steps
        p = Vector((LEG_X * math.cos(a), BEND_Y + BEND_RISE * math.sin(a), CORE_Z))
        t = Vector((-LEG_X * math.sin(a), BEND_RISE * math.cos(a), 0)).normalized()
        t = -t  # along the line from left to right
        # Narrower over the top of the bend.
        f = math.sin(a) ** 2
        pts.append((p, t, LEG_HALF_W + (BEND_HALF_W - LEG_HALF_W) * f))
    y = BEND_Y - step
    while y >= LEG_FOOT - 1e-6:
        pts.append((Vector((LEG_X, y, CORE_Z)), Vector((0, -1, 0)), LEG_HALF_W))
        y -= step
    return pts


def core(m):
    rings = []
    for p, t, hw in centre_line():
        normal = Vector((t.y, -t.x, 0)).normalized()  # to the outside of the U
        rings.append(ring_xz(p, normal, hw, CORE_HALF_H, CORE_POWER, 20))
    body = k.loft("core", rings, m["core"])
    k.smooth(body, 50)
    mk.paint(body, lambda c, n: m["core_top"] if n.z > 0.75 else None)
    return body


def coil(m, side):
    """The coil round a leg: a sleeve of WINDINGS rounded ridges with grooves between, ends stepping down."""
    x = side * LEG_X
    y0, y1 = COIL
    rings = []
    count = WINDINGS * 4
    for i in range(count + 1):
        t = i / count
        y = y0 + (y1 - y0) * t
        ridge = 0.5 - 0.5 * math.cos(2 * math.pi * WINDINGS * t)  # 0 in the grooves, 1 on the ridges
        proud = COIL_PROUD * (0.55 + 0.45 * ridge)
        end = min(1.0, min(t, 1 - t) * count / 1.5)  # the ends step down to the core
        proud *= 0.35 + 0.65 * end
        rings.append(ring_xz(Vector((x, y, CORE_Z)), Vector((side, 0, 0)), LEG_HALF_W + proud, CORE_HALF_H + proud,
                             CORE_POWER, 20))
    # Built up the leg: its sections run along +y.
    sleeve = k.loft(f"coil{side}", rings, m["coil"])
    # The grooves darker (by how proud the surface is there).

    def pick(c, n):
        t = (c.y - y0) / (y1 - y0)
        ridge = 0.5 - 0.5 * math.cos(2 * math.pi * WINDINGS * t)
        return m["coil_groove"] if ridge < 0.22 else None
    mk.paint(sleeve, pick)
    k.smooth(sleeve, 60)
    # Dark seams where the coil meets the core (the sprite's black rows 6 and 14).
    for y in (y0 - 0.15, y1 + 0.15):
        rings = [ring_xz(Vector((x, y + dy, CORE_Z)), Vector((side, 0, 0)), LEG_HALF_W + 0.12, CORE_HALF_H + 0.12,
                         CORE_POWER, 20) for dy in (-0.2, 0.2)]
        seam = k.loft(f"seam{side}_{y:.1f}", rings, m["seam"])
        k.smooth(seam, 60)


# The left pole piece from where it takes the leg (top) down to its foot: (y, left edge x, right edge x, height).
# Its inner side bulges in towards the middle (closing the hole to a V) and it lowers towards its foot.
POLE_SECTIONS = [(-0.55, -10.25, -3.7, 5.25), (-1.6, -10.35, -2.55, 5.3), (-3.0, -10.4, -1.3, 5.2),
                 (-4.4, -10.35, -0.75, 5.0), (-5.6, -10.25, -1.05, 4.75), (-6.9, -10.0, -2.15, 4.4),
                 (-7.9, -9.6, -3.15, 4.0), (-8.9, -8.95, -3.7, 3.45)]
POLE_FOOT = -9.7            # where the foot's rounded end reaches
POLE_POWER = 3.0


def pole(m):
    """The left pole piece: lofted down the screen through rounded-box sections that follow its outline in the
    sprite, its foot's end rounded; a groove across it below the coil, where it is clamped to the leg."""
    sections = []
    pts = mk.chaikin([(y, x0, x1, h) for y, x0, x1, h in POLE_SECTIONS], 2, closed=False)
    for y, x0, x1, h in pts:
        sections.append((y, (x0 + x1) / 2, (x1 - x0) / 2, h))
    # The foot's end rounded over its last pixel.
    y_end, cx_end, hw_end, h_end = sections[-1]
    for i in range(1, 5):
        a = (math.pi / 2) * i / 5
        f = math.cos(a)
        sections.append((y_end + (POLE_FOOT - y_end) * math.sin(a), cx_end, hw_end * (0.35 + 0.65 * f),
                         h_end * (0.55 + 0.45 * f)))
    rings = []
    for y, cx, hw, h in sections:
        ring = []
        for j in range(24):
            u, v = mk.superellipse_point(2 * math.pi * j / 24, POLE_POWER)
            ring.append(Vector((cx + u * hw, y, h / 2 + v * h / 2)))
        rings.append(ring)
    y0, cx0, hw0, h0 = sections[0]
    block = k.loft("pole", rings, m["pole"], start_point=(cx0, y0, h0 / 2),
                   end_point=(sections[-1][1], POLE_FOOT, sections[-1][3] / 2))
    k.smooth(block, 60)
    mk.paint(block, lambda c, n: m["pole_top"] if n.z > 0.8 else None)
    # A dark band round it below the coil, where it is clamped to the leg.
    clamp = []
    for y in (-1.25, -1.85):
        ring = []
        y_, x0, x1, h = POLE_SECTIONS[1]
        for j in range(24):
            u, v = mk.superellipse_point(2 * math.pi * j / 24, POLE_POWER)
            ring.append(Vector(((x0 + x1) / 2 + u * ((x1 - x0) / 2 + 0.12), y, h / 2 + v * (h / 2 + 0.12))))
        clamp.append(ring)
    band = k.loft("pole_band", clamp, m["seam"])
    k.smooth(band, 60)
    return block


def keeper(m):
    y, z, r = KEEPER
    x0, x1 = -2.6, 2.6
    rings = [[Vector((x, y + r * math.cos(2 * math.pi * j / 16), z + r * math.sin(2 * math.pi * j / 16)))
              for j in range(16)] for x in (x0, x1)]
    bar = k.loft("keeper", rings, m["keeper"])
    k.smooth(bar, 50)
    mk.ball("stud", (0.0, y, z + r * 0.6), (0.85, 0.8, 0.7), m["stud"], 16, 8)


def materials():
    return {
        "core": k.material("horseshoe_core", palette=0x06, metallic=0.6, roughness=0.3),
        "core_top": k.material("horseshoe_core_top", palette=0x08, metallic=0.6, roughness=0.28),
        "coil": k.material("horseshoe_coil", palette=0x18, metallic=0.55, roughness=0.32),
        "coil_groove": k.material("horseshoe_coil_groove", palette=0x15, metallic=0.5, roughness=0.4),
        "seam": k.material("horseshoe_seam", palette=0x01, metallic=0.3, roughness=0.6),
        "pole": k.material("horseshoe_pole", palette=0x07, metallic=0.6, roughness=0.28),
        "pole_top": k.material("horseshoe_pole_top", palette=0x09, metallic=0.6, roughness=0.25),
        "keeper": k.material("horseshoe_keeper", palette=0x04, metallic=0.6, roughness=0.35),
        "stud": k.material("horseshoe_stud", palette=0x0b, metallic=0.7, roughness=0.2),
    }


def build():
    k.reset()
    options = k.args()
    m = materials()
    core(m)
    for side in (-1, 1):
        coil(m, side)
    left = pole(m)
    k.mirror_x(left, "pole_right")
    k.mirror_x(bpy.data.objects["pole_band"], "pole_band_right")
    keeper(m)
    parts = mk.meshes()
    for obj in parts:
        mk.apply(obj)
    bottom = min(v.co.z for obj in parts for v in obj.data.vertices)
    mk.transform(parts, Matrix.Translation((AXIS_X, 0, -bottom)))  # its lowest point on z = 0
    bpy.context.view_layer.update()
    if "check" in options:
        mask = k.sprite_mask(os.path.join(options["check"], "enemy_3.png"), 126)
        mk.compare("horseshoe (3 126)", mk.coverage(parts, 24, 28), mask)
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    out = mk.outdir(options)
    mk.report("horseshoe", parts, os.path.join(out, "horseshoe.glb"))
    if "preview" in options:
        mk.preview(options["preview"] + "horseshoe", parts)


if __name__ == "__main__":
    build()
