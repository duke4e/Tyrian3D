"""GYGES' and MISTAKES' violet shell (sheet G sprite 55, 2x2: its 23 x 20 pixels at the top of the 24 x 28 cell; not
animated), polished again (2026-10-23, round 38, the quality redo): rebuilt in place of round 34's version of this
script (one heightfield in the picture's plane painted by the sprite's shades: pixel-stepped edges, blotchy painted
patches) as a carapace of separate smooth solids. models.cfg: model violet_shell enemies/violet_shell.glb and sprite
g 55 violet_shell yaw=0 (both unchanged: drawn centred in height, no origin). No other enemy, launched ones included,
shows G 55; it is no other sprite's pixels mirrored, turned or in other ramps (no upscale exists: built from the
sprite, enlarged).

Where the levels put it (found in round 34, kept): custom events (enemy 0 with the event's sprite, armour 10, link
201, then event 60 makes it special: shooting it sets global flag 1): GYGES' event 51 (the top layer, moving with
background 3) at t1280, 3080, 3480 (x 220, 60, 160) and MISTAKES' event 49 (the ground) at t180 and 480 (x 40, 220).
No episode 6 level makes it.

As the sprite draws it (columns and rows): a violet carapace (ramp 5, outlined in 0x50), symmetric about column 11: a
ribbed dome at its back (columns 6-16, rows 0-9: two light ribs either side of a groove down its middle, darker ones
at its sides), shoulder plates at its sides (columns 1-5 and 17-21, rows 3-12) with a light ridge down them and a
little dark horn on top, a dark band across its middle (rows 9-12) with three red dots (0x43: column 11 of row 9,
columns 10 and 12 of row 10), the front plate under it with a blue gem (ramp 9, columns 9-13 of rows 13-15) in a dark
socket, and two front lobes (rows 16-19) parted by a notch under the gem.

Built from separate smooth solids (polish_sweep_kit), modelled in the picture's plane and sheared along the game
camera's line of sight (y - z tan 20) so the camera sees each where the sprite draws it:
- the carapace under everything (BASE: a loft of superellipse sections down the screen, its rim the outline), mid
  violet, seen between the parts;
- the dome (DOME: half an ellipsoid at the back, 8 high) with four ribs down it (RIBS: the inner pair either side of
  the middle's groove, the outer pair lower, each starting where the dome is wide enough for it, fanning out a
  little to its foot);
- the shoulder plates (SHOULDER: curved plates along the outline, flat-topped, a ridge down each) with their little
  dark horns (HORN), pointing up the screen;
- the band: a dark strip across the middle, the three red dots on it (DOTS: small beads glowing a little);
- the front plate (FRONT: a low swell of the carapace) holding the gem: a dark ring sunk round it, a dark floor under
  it, the gem a smooth lens glowing blue with a hotter core;
- the front lobes (LOBE: curved plates along the outline either side of the notch).
Materials (palette indices; the shading is the geometry's and the game's light, nothing painted from the sprite's
pixels; metallic 0.25 like polish_violet_pincer's violet): the dome and its ribs 0x5a, the shoulder plates 0x58, the
carapace, the front plate and the lobes 0x55, the band 0x53, the socket, its floor and the horns 0x52, the gem 0x94
glowing 0.45 with a core of 0x97 at 0.6, the dots 0x45 glowing 0.35. 8.06 pixels tall with its bottom at z 0 (the round
parts' undersides flattened there): drawn centred on the ground enemies' layer (4 pixels up) it rests on the ground;
on GYGES' top layer it flies as its top enemies do. No random numbers, no booleans: the same GLB every run, with and
without --check.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up; origin at the sprite's centre
(pixel edge 12, 14): continuous column u and row v (pixel (c, r)'s middle at (c + 0.5, r + 0.5)), x = u - 12,
y = 14 - v; its axis at u 11.5 (x -0.5).

Replaces round 34's version of this script (rewritten in place). No old generator code is left to remove (round 34
removed wave3_r_beasts.py, wave3_r_kit.py and wave3_r_art.py).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (its outline as the camera
sees it against the sprite in enemy_G.png), --preview <prefix>.
"""
import math
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
from polish_deli_boss import join, drop_unused  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_sweep_kit import (catmull, resample, section, set_smooth, sweep, ellipsoid, interp, mirrored,  # noqa: E402
                              flatten_below, shear_to_camera)

MATS = {
    "dome": (0x5a, 0.25, 0.28, 0.0),      # the ribbed dome at the back
    "plate": (0x58, 0.25, 0.3, 0.0),      # the shoulder plates
    "front": (0x55, 0.25, 0.3, 0.0),      # the front plate and the lobes
    "body": (0x55, 0.25, 0.34, 0.0),      # the carapace under them
    "band": (0x53, 0.2, 0.4, 0.0),        # the dark band across the middle
    "dark": (0x52, 0.15, 0.45, 0.0),      # the gem's socket, the little horns
    "gem": (0x94, 0.1, 0.12, 0.45),
    "gem_hot": (0x97, 0.0, 0.1, 0.6),
    "dot": (0x45, 0.1, 0.3, 0.35),
}


def materials():
    pal = k.level_palette()
    m = {}
    for key, (index, metallic, roughness, glow) in MATS.items():
        extra = dict(emission=pal[index], emission_strength=glow) if glow > 0 else {}
        m[key] = k.material("vshell_%s" % key, palette=index, metallic=metallic, roughness=roughness, **extra)
    return m


def P(u, v, z=0.0):
    """The sprite's continuous column u and row v (pixel (c, r)'s middle at (c + 0.5, r + 0.5)): x = u - 12,
    y = 14 - v; its axis (column 11's middle) at u 11.5."""
    return Vector((u - 12.0, 14.0 - v, z))


AXIS = 11.5                       # the column it is drawn symmetric about (x -0.5)
# The carapace under everything (row, half-width, height of its top): its rim is the sprite's outline.
BASE = [(2.6, 5.2, 2.6), (4.0, 9.6, 3.0), (6.5, 11.4, 3.3), (10.5, 11.6, 3.4), (13.5, 11.6, 3.3), (16.2, 11.0, 2.8),
        (17.4, 9.4, 2.3)]
DOME = ((11.5, 4.75), (5.9, 4.5), 2.4, 8.0)      # middle, radii, its foot's height, its top
RIBS = [(9.9, 0.9), (13.1, 0.9), (7.4, 0.75), (15.6, 0.75)]   # column, half-width (the inner pair, the outer pair)
# The left shoulder plate and the left front lobe: curved plates along the outline (column, row, top, half-width).
SHOULDER = [(4.7, 3.9, 4.9, 1.3), (3.6, 5.6, 5.3, 2.6), (3.0, 8.2, 5.4, 2.9), (2.9, 10.6, 5.0, 2.7),
            (3.4, 12.6, 4.3, 1.6)]
HORN = [(3.6, 5.2, 4.8, 0.7), (3.4, 4.2, 5.1, 0.5), (3.2, 3.4, 5.2, 0.22)]
FRONT = ((11.5, 14.2), (9.4, 3.1), 2.3, 4.15)    # middle, radii, foot, top
LOBE = [(1.9, 14.8, 3.3, 1.4), (3.2, 16.6, 3.7, 2.1), (5.4, 17.8, 3.8, 2.2), (7.7, 18.2, 3.6, 2.0),
        (9.5, 17.9, 3.2, 1.3)]
GEM = ((11.5, 14.2), (2.45, 1.45), 4.6)          # middle, radii, height
DOTS = [(11.5, 9.7), (10.4, 10.7), (12.6, 10.7)]  # the three red dots on the band


def base(m):
    vs = [BASE[0][0] + (BASE[-1][0] - BASE[0][0]) * i / 30 for i in range(31)]
    rings = []
    seg = 32
    for v in vs:
        hw, top = interp(BASE, v)
        ring = []
        for j in range(seg):
            x, z = section(j, seg, hw, top, 0.0, power=2.6)
            ring.append(P(AXIS + x, v, max(z, 0.0)))
        rings.append(ring)
    obj = k.loft("base", rings, m["body"], start_point=P(AXIS, vs[0] - 0.4, 1.0), end_point=P(AXIS, vs[-1] + 0.4, 0.8))
    return set_smooth(obj)


def band(m):
    """The dark band across the middle, between the dome and the shoulders and the front plate: a strip on the
    carapace."""
    path, secs = [], []
    for j in range(15):
        f = j / 14
        u = 3.6 + (AXIS - 3.6) * 2 * f
        v = 10.9 + 0.5 * abs(2 * f - 1) ** 2
        hw, top = interp(BASE, v)
        q = min(1.0, abs(u - AXIS) / hw)
        z = top * (1 - q ** 2.6) ** (1 / 2.6)
        path.append(P(u, v, z - 0.15))
        w = math.sin(math.pi * (0.03 + 0.94 * f)) ** 0.3
        secs.append((1.75 * w, 0.4 * w + 0.05, 0.35))
    return [sweep("band", path, secs, m["band"], segments=12, up=(0.0, 0.0, 1.0))]


def dome_z(u, v):
    (cu, cv), (ru, rv), foot, top = DOME
    q = ((u - cu) / ru) ** 2 + ((v - cv) / rv) ** 2
    return foot + (top - foot) * math.sqrt(max(0.0, 1.0 - q))


def dome(m):
    (cu, cv), (ru, rv), foot, top = DOME
    rings = []
    count, around = 12, 32
    for i in range(1, count):
        a = 0.5 * math.pi * i / count            # from the top down
        r, z = math.sin(a), math.cos(a)
        rings.append([P(cu + ru * r * math.cos(2 * math.pi * j / around),
                        cv + rv * r * math.sin(2 * math.pi * j / around), foot + (top - foot) * z)
                      for j in range(around)])
    rings.append([P(cu + ru * math.cos(2 * math.pi * j / around), cv + rv * math.sin(2 * math.pi * j / around),
                    foot - 0.6) for j in range(around)])
    obj = k.loft("dome", list(reversed(rings)), m["dome"], start_point=P(cu, cv, foot - 0.6), end_point=P(cu, cv, top))
    objs = [set_smooth(obj)]
    for i, (u, hw) in enumerate(RIBS):
        # each rib down the dome from where the dome is wide enough for it to its foot, fanning out a little
        v0 = cv - rv * math.sqrt(max(0.0, 1.0 - ((u - cu) / ru) ** 2)) * 0.9
        v1 = cv + rv * 0.8
        path, secs = [], []
        for j in range(12):
            f = j / 11
            v = v0 + (v1 - v0) * f
            uu = u + (u - cu) * 0.18 * f
            path.append(P(uu, v, dome_z(uu, v) - 0.12))
            w = math.sin(math.pi * (0.04 + 0.92 * f)) ** 0.45
            secs.append((hw * w, 0.42 * w + 0.05, 0.5))
        objs.append(sweep("rib_%d" % i, path, secs, m["dome"], segments=10))
    return objs


def plate_along(name, spec, mat, ridge=0.0, segments=16, power=3.4):
    """A curved plate along the outline: spec (column, row, height of its top, half-width) points, smoothed; its
    sections lens-shaped, standing on the carapace."""
    pts = resample(catmull(spec, 6), 18)
    path, secs = [], []
    for u, v, top, w in pts:
        _, foot = interp(BASE, v)
        path.append(P(u, v, foot - 0.4))
        secs.append((w, top - foot + 0.4, 0.6))
    return sweep(name, path, secs, mat, segments=segments, power=power, ridge=ridge)


def shoulder(m):
    objs = [plate_along("shoulder", SHOULDER, m["plate"], ridge=0.35)]
    pts = resample(catmull(HORN, 4), 8)
    objs.append(sweep("horn", [P(u, v, z) for u, v, z, w in pts], [(w, w, w * 0.8) for u, v, z, w in pts], m["dark"],
                      segments=10, end=P(3.15, 2.9, 5.15)))
    return objs


def lobe(m):
    return [plate_along("lobe", LOBE, m["front"], ridge=0.15)]


def front(m):
    (cu, cv), (ru, rv), foot, top = FRONT
    objs = [ellipsoid("front", P(cu, cv, foot), (ru, rv, top - foot), m["front"], 12, 28)]
    (gu, gv), (gx, gy), gz = GEM
    # the gem's socket: a dark ring round it, sunk into the plate
    ring = []
    for j in range(25):
        a = 2 * math.pi * j / 24
        ring.append(P(gu + (gx + 0.45) * math.cos(a), gv + (gy + 0.4) * math.sin(a), gz - 0.05))
    path = ring[:-1]
    rings = []
    tube_r = 0.6
    n = len(path)
    seg = 8
    for i, p in enumerate(path):
        t = (path[(i + 1) % n] - path[i - 1]).normalized()
        out = Vector((t.y, -t.x, 0.0)).normalized()
        up = Vector((0, 0, 1))
        rings.append([p + out * (tube_r * math.cos(2 * math.pi * q / seg)) +
                      up * (tube_r * 0.8 * math.sin(2 * math.pi * q / seg)) for q in range(seg)])
    verts = [v for r in rings for v in r]
    faces = []
    for i in range(n):
        for q in range(seg):
            a, b = i * seg + q, i * seg + (q + 1) % seg
            c, d = ((i + 1) % n) * seg + (q + 1) % seg, ((i + 1) % n) * seg + q
            faces.append((a, b, c, d))
    sock = k.mesh_object("gem_socket", verts, faces, m["dark"])
    k.recalc_normals(sock)
    objs.append(set_smooth(sock))
    floor = ellipsoid("gem_floor", P(gu, gv, gz - 0.55), (gx + 0.5, gy + 0.45, 0.45), m["dark"], 8, 20)
    objs.append(floor)
    objs.append(ellipsoid("gem", P(gu, gv, gz - 0.1), (gx, gy, 0.95), m["gem"], 10, 28))
    objs.append(ellipsoid("gem_hot", P(gu - 0.45, gv - 0.25, gz + 0.55), (gx * 0.42, gy * 0.42, 0.32), m["gem_hot"],
                          8, 18))
    return objs


def dots(m):
    objs = []
    for i, (u, v) in enumerate(DOTS):
        hw, top = interp(BASE, v)
        objs.append(ellipsoid("dot_%d" % i, P(u, v, top + 0.3), (0.62, 0.62, 0.45), m["dot"], 8, 16))
    return objs


def build():
    options = k.args()
    out = mk.outdir(options)
    k.reset()
    m = materials()
    left = shoulder(m) + lobe(m)
    parts = [base(m)] + band(m) + dome(m) + left + mirrored(left, AXIS - 12.0) + front(m) + dots(m)
    flatten_below(parts)
    bpy.context.scene.view_settings.view_transform = "Standard"
    if "check" in options:
        sheets = options["check"]
        sheet = os.path.join(sheets, "enemy_G.png") if os.path.isdir(sheets) else sheets
        bpy.context.view_layer.update()
        mk.compare("violet_shell (G 55), as the camera sees it", mk.coverage(parts, 24, 28), k.sprite_mask(sheet, 55))
    shear_to_camera(parts)
    triangulate(parts)
    model = join(parts, "violet_shell")
    drop_unused([model])
    mk.report("violet_shell", [model], os.path.join(out, "violet_shell.glb"))
    if "preview" in options:
        mk.preview(options["preview"] + "violet_shell", [model])


if __name__ == "__main__":
    build()
