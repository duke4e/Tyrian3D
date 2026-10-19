"""IXMUCANE's and SAWBLADES' glass city (sheet R sprites 1 and 3 above 39 and 41, 2x2 each: one 48 x 56 picture;
ground layer; enemies 291, 292 above 289, 290; not animated), polished (2026-10-19; it replaces wave3_af_domes.py's
small_dome(), a city of random blocks under a dark shell). models.cfg: model glass_city_tl / glass_city_tr /
glass_city_bl / glass_city_br ... origin; sprite r 1 glass_city_tl yaw=0 height=-4, sprite r 3 glass_city_tr yaw=0
height=-4, sprite r 39 glass_city_bl yaw=0 height=-4, sprite r 41 glass_city_br yaw=0 height=-4. The levels always
put the four together (event 6 each: 291 at (x, y - 28), 292 at (x + 24, y - 28), 289 at (x, y), 290 at (x + 24, y);
IXMUCANE's events 2736 and 3044, SAWBLADES' 104, 188 and on, sometimes two domes side by side, 48 pixels apart).
None of these sprites is another sprite's pixels mirrored or recoloured.

As the sprites and their 4x upscales draw it: a round glass dome, 37 pixels across (columns 6-42 of rows 9-45,
round the picture's pixel (24.5, 27.2)), standing on the levels' dark brown dirt (the map's: every pixel outside the
dome is dirt or the dome's drawn shadow, left out; the 3D ground shows the dirt, the game casts the shadow). Its
foot is a dark rim; through the glass a city of blue-grey blocks (ramp 6, blue ramps 3 and 8 for a few): a tall
blue block up the screen from the middle (columns 23-28 of rows 13-21), a broad lit block at the upper left
(columns 13-22 of rows 12-22, under the glint), blocks either side of the middle, a broad block at the lower right
with a red lamp (pixel (29, 32)), a round building at the bottom left of the middle (the upscale's curved roof,
columns 16-23 of rows 30-38), low blocks round the edge, dark streets between; the glass darkens towards its rim
(nearly black there, as glass seen at a grazing angle), a bright white glint up and to the left (pixel (18.4,
17.6)) and a pale crescent of reflected light along its lower right edge (columns 34-41 of rows 29-42).

Built as such a colony, nicer than the sprite but in its layout and shades: a dark steel collar round the dome's
foot (its top lit), a floor of dark streets inside it, the city's buildings standing on it (each a bevelled block,
its roof inside a low parapet, rooftop units and lit skylights on the larger ones, lit windows in rows down their
fronts, set-back upper storeys on the tall ones, an antenna on the tallest, a domed round hall, the red lamp on its
mast), all of them kept well under the glass; the glass a thin shell (a superellipse profile, fuller than a
half-ellipsoid), see-through over the city, darkening in bands towards its foot and dimmer over its lower half (as
the sprite shades it), the glint and the crescent thin films lying on it in its own palette shades, lit a little
(emission), as the sun from the upper left puts them there.
The glass is a single sheet without thickness (the game draws both its sides: the view into the dome passes it
twice, near and far). The collar reaches SKIRT below the ground (z = 0), so the dome stands on the terrain with
height=-4 or without it.

Built whole round the picture's middle and cut along the sprites' edges into the four pieces (polish_arch.py's
cut(): the pieces keep the whole's shading across the cuts; the glass is cut open, without caps, so no wall shows
through it where the pieces meet), each moved so its sprite's centre is its origin.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the ground (z = 0); the
whole's origin is the corner where the four sprites meet: P(c, r) turns the picture's pixel edges (column c, row r)
into these coordinates (x = c - 24, y = 28 - r).

Replaces wave3_af_domes.py's small dome: remove SMALL, S_CENTRE, S_RADIUS, S_HEIGHT, S_Z0, small_mask(),
small_dome(), S_PIECES and its a.pieced("glass_city", ...) line; city(), roof_picker() and aa_lens() stay (the big
purple dome uses them).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes of the
whole and of each piece against the dome's pixels in enemy_R.png), --preview <prefix> (the whole's and each piece's
top and 3/4 views), --only <piece,...>.
"""
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_arch import cut  # noqa: E402  (polish_machine_kit.cut without its material indices shifted twice)

# The pieces: (name, sprite, the box it covers in the whole's coordinates (x0, x1, y0, y1)).
PIECES = [("glass_city_tl", 1, (-24.0, 0.0, 0.0, 28.0)), ("glass_city_tr", 3, (0.0, 24.0, 0.0, 28.0)),
          ("glass_city_bl", 39, (-24.0, 0.0, -28.0, 0.0)), ("glass_city_br", 41, (0.0, 24.0, -28.0, 0.0))]
SPRITE_AT = {1: (0, 0), 3: (24, 0), 39: (0, 28), 41: (24, 28)}  # top left corners in the 48 x 56 picture


def P(c, r):
    """A pixel edge of the 48 x 56 picture (column c, row r) in the whole's coordinates."""
    return (c - 24.0, 28.0 - r)


CENTRE = P(24.5, 27.2)                # the dome's middle
R_OUT = 18.4                          # the collar's outer edge (the sprite's dark rim)
SKIRT = -4.0                          # how far the collar reaches below the ground (z = 0)
# The collar's cross-section, from its outer foot in: (radius, z).
COLLAR = [(R_OUT, SKIRT), (R_OUT, 0.0), (R_OUT, 0.55), (R_OUT - 0.18, 1.05), (R_OUT - 0.55, 1.42),
          (R_OUT - 1.0, 1.55), (R_OUT - 1.55, 1.5), (R_OUT - 1.95, 1.25), (R_OUT - 2.1, 0.8), (R_OUT - 2.1, SKIRT)]
FLOOR_R, FLOOR_Z = R_OUT - 2.0, 0.32  # the streets inside it
# The glass: its foot's radius and height (on the collar's top), its height above the foot, its profile's power.
GLASS_R, GLASS_Z0, GLASS_H, GLASS_POWER = R_OUT - 1.05, 1.42, 14.4, 2.25
# Its bands by the share of its foot's radius (seen from above): see-through, dimmer, dark, the rim at its foot.
BANDS = (0.74, 0.87, 0.95)
GLINT = (P(18.4, 17.6), 1.6, 3.1)    # the glint: its middle, its radius and its halo's (seen from above)
CRESCENT = (-80.0, 0.0, 0.85, 0.986, (-56.0, -18.0))  # angles (degrees), radial span, its brightest angles
GAP = 1.6                             # the buildings keep this far under the glass

# The city (pixel edges of the picture: c0, c1, r0, r1; height; roof shade; options). Options: "set" (c0, c1, r0,
# r1, height) a set-back upper storey; "units": how many rooftop units; "sky": lit skylights; "mast": an antenna's
# height above the roof; "lamp": the red lamp at (c, r) on a mast this high.
CITY = [
    # The tall blue block up the screen from the middle, its upper storey set back, an antenna on top.
    (24.4, 28.6, 13.8, 21.4, 9.6, "blue", {"set": (25.0, 28.0, 14.3, 18.6, 11.3), "mast": 1.6}),
    # The broad lit block at the upper left (under the glint), set back too.
    (15.6, 22.8, 15.0, 20.4, 7.2, "light", {"set": (16.3, 22.0, 15.6, 18.9, 8.4), "units": 2, "sky": 2}),
    # The blocks either side of the middle.
    (13.4, 22.8, 21.2, 27.2, 5.8, "mid", {"units": 3, "sky": 2}),
    (23.4, 28.6, 22.0, 27.4, 7.4, "light", {"units": 1, "sky": 1}),
    (29.2, 34.4, 20.2, 27.6, 6.4, "blue", {"units": 2, "sky": 1}),
    # Up the screen at the right.
    (29.2, 33.6, 14.4, 19.4, 4.8, "dark", {"units": 1}),
    (34.4, 37.4, 18.4, 22.6, 3.6, "mid", {"units": 1}),
    # The broad block at the lower right with the red lamp.
    (25.0, 35.2, 28.4, 34.6, 4.6, "mid", {"units": 2, "sky": 2, "lamp": (29.3, 32.2, 1.1)}),
    # Low blocks round the edge.
    (9.8, 13.0, 22.4, 29.6, 3.0, "dark", {"units": 1}),
    (10.6, 15.2, 30.2, 34.4, 2.4, "mid", {}),
    (35.6, 39.4, 23.4, 31.4, 2.8, "dark", {"units": 1}),
    (34.4, 37.2, 32.2, 36.2, 2.2, "mid", {}),
    (23.4, 28.4, 35.8, 40.6, 2.6, "dark", {"units": 1}),
    (29.0, 33.6, 35.4, 39.4, 2.0, "mid", {}),
    (17.6, 21.6, 38.4, 41.0, 1.8, "dark", {}),
    (19.6, 23.4, 12.4, 14.6, 2.6, "mid", {}),
]
HALL = (P(19.6, 34.2), 3.2, 2.3, 1.0)  # the round hall: its middle, radius, wall height, dome height
WINDOW = (0.42, 0.5)                    # a window's width and height
SEED = 291


def materials():
    glow = k.level_palette()

    def mat(name, index, metallic=0.4, roughness=0.4, strength=0.0, alpha=None):
        if strength > 0:
            return k.material(name, palette=index, metallic=metallic, roughness=roughness, emission=glow[index],
                              emission_strength=strength, alpha=alpha)
        return k.material(name, palette=index, metallic=metallic, roughness=roughness, alpha=alpha)
    return {
        "collar": mat("city_collar", 0x04, 0.6, 0.35),
        "street": mat("city_street", 0x62, 0.2, 0.6),
        "light": mat("city_roof_light", 0x6b, 0.25, 0.42),
        "mid": mat("city_roof", 0x69, 0.25, 0.45),
        "dark": mat("city_roof_dark", 0x67, 0.25, 0.48),
        "blue": mat("city_roof_blue", 0x3c, 0.25, 0.4),
        "wall": mat("city_wall", 0x65, 0.25, 0.5),
        "window": mat("city_window", 0x89, 0.0, 0.3, strength=1.6),
        "lamp": mat("city_lamp", 0x77, 0.0, 0.25, strength=3.0),
        "glass": mat("city_glass", 0x37, 0.0, 0.08, alpha=0.2),
        "glass_dim": mat("city_glass_dim", 0x64, 0.0, 0.1, alpha=0.42),
        "glass_dark": mat("city_glass_dark", 0x62, 0.0, 0.12, alpha=0.75),
        "glint": mat("city_glint", 0x0f, 0.0, 0.05, strength=2.4, alpha=0.9),
        "sheen": mat("city_sheen", 0x6c, 0.0, 0.08, strength=0.6, alpha=0.45),
        "halo": mat("city_halo", 0x6d, 0.0, 0.08, strength=0.5, alpha=0.3),
    }


# --- Helpers ------------------------------------------------------------------------------------------------------

def glass_height(x, y):
    """The glass's height above (x, y) (its foot's height outside it)."""
    t = math.hypot(x - CENTRE[0], y - CENTRE[1]) / GLASS_R
    if t >= 1:
        return GLASS_Z0
    return GLASS_Z0 + GLASS_H * (1 - t ** GLASS_POWER) ** (1 / GLASS_POWER)


def ring_points(r, z, segments, centre=CENTRE):
    angles = [2 * math.pi * j / segments for j in range(segments)]
    return [Vector((centre[0] + r * math.cos(a), centre[1] + r * math.sin(a), z)) for a in angles]


# --- The parts ----------------------------------------------------------------------------------------------------

def collar(m):
    """The dark steel collar round the dome's foot, its rounded top lit."""
    rings = [ring_points(r, z, 144) for r, z in COLLAR]
    obj = k.loft("collar", rings, m["collar"], cap_start=False, cap_end=False)
    # Closed underneath (a flat ring on the ground), so the cuts can be capped.
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.bridge_loops(bm, edges=[e for e in bm.edges if e.is_boundary])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(obj.data)
    bm.free()
    k.smooth(obj, 50)
    mk.paint(obj, lambda c, n: m["mid"] if n.z > 0.55 and c.z > 1.2 else None)
    return obj


def floor(m):
    """The streets: a flat disc inside the collar."""
    obj = mk.lathe("floor", [(FLOOR_R, 0.0), (FLOOR_R, FLOOR_Z)], CENTRE, m["street"], 96)
    k.smooth(obj, 30)
    return obj


def windows(name, faces, rng, m, chance):
    """Lit windows in rows on the given walls: faces [(a, b, outward, z0, z1)] (a, b: the wall's ends on the ground
    plane, outward its normal), each window a small quad standing just proud of the wall."""
    verts, polys = [], []
    w, h = WINDOW
    for a, b, out, z0, z1 in faces:
        a, b, out = Vector(a), Vector(b), Vector(out)
        length = (b - a).length
        along = (b - a).normalized()
        count = int((length - 0.6) / 1.05)
        if count < 1:
            continue
        # The quad's corners in an order that makes it face out of the wall.
        corners = ((-w / 2, 0.0), (w / 2, 0.0), (w / 2, h), (-w / 2, h))
        if along.to_3d().cross(Vector((0, 0, 1))).dot(out.to_3d()) < 0:
            corners = tuple(reversed(corners))
        floors = int((z1 - z0 - 0.5) / 1.35)
        for fl in range(floors):
            z = z0 + 0.75 + fl * 1.35
            for i in range(count):
                if rng.random() > chance:
                    continue
                s = (length - (count - 1) * 1.05) / 2 + i * 1.05
                c = a + along * s + out * 0.04
                base = len(verts)
                for du, dz in corners:
                    p = c + along * du
                    verts.append((p.x, p.y, z + dz))
                polys.append((base, base + 1, base + 2, base + 3))
    if not polys:
        return None
    return k.mesh_object(name, verts, polys, m["window"])


def block(name, x0, x1, y0, y1, z0, z1, mat_roof, m, bevel=0.22):
    body = mk.box(name, x0, x1, y0, y1, z0, z1, m["wall"])
    mk.bevel(body, bevel, 2, 35)
    mk.shade(body, 35)
    mk.paint(body, lambda c, n: mat_roof if n.z > 0.8 else None)
    return body


def parapet(name, x0, x1, y0, y1, z, mat):
    """A low rim round a roof's edge."""
    t, h = 0.32, 0.38
    parts = [mk.box(f"{name}_s", x0 + 0.1, x1 - 0.1, y0 + 0.1, y0 + 0.1 + t, z - 0.05, z + h, mat),
             mk.box(f"{name}_n", x0 + 0.1, x1 - 0.1, y1 - 0.1 - t, y1 - 0.1, z - 0.05, z + h, mat),
             mk.box(f"{name}_w", x0 + 0.1, x0 + 0.1 + t, y0 + 0.1 + t, y1 - 0.1 - t, z - 0.05, z + h, mat),
             mk.box(f"{name}_e", x1 - 0.1 - t, x1 - 0.1, y0 + 0.1 + t, y1 - 0.1 - t, z - 0.05, z + h, mat)]
    for p in parts:
        mk.bevel(p, 0.06, 1, 35)
        mk.shade(p, 35)
    return parts


def building(i, spec, m, rng):
    """A city block: its walls, its roof inside a parapet, rooftop units, skylights, windows, a set-back upper
    storey, an antenna, the red lamp."""
    c0, c1, r0, r1, height, shade, opts = spec
    (x0, y1), (x1, y0) = P(c0, r0), P(c1, r1)
    z0 = FLOOR_Z - 0.05
    limit = min(glass_height(x, y) for x in (x0, x1) for y in (y0, y1)) - GAP
    height = min(height, limit)
    roof = m[shade]
    block(f"b{i}", x0, x1, y0, y1, z0, height, roof, m)
    walls = [((x0, y0), (x1, y0), (0, -1), z0, height), ((x0, y1), (x0, y0), (-1, 0), z0, height),
             ((x1, y0), (x1, y1), (1, 0), z0, height)]
    top_z = height
    top_rect = (x0, x1, y0, y1)
    if "set" in opts:
        s0, s1, q0, q1, sh = opts["set"]
        (sx0, sy1), (sx1, sy0) = P(s0, q0), P(s1, q1)
        sh = min(sh, min(glass_height(x, y) for x in (sx0, sx1) for y in (sy0, sy1)) - GAP)
        block(f"b{i}_top", sx0, sx1, sy0, sy1, height - 0.1, sh, roof, m)
        walls += [((sx0, sy0), (sx1, sy0), (0, -1), height, sh), ((sx0, sy1), (sx0, sy0), (-1, 0), height, sh),
                  ((sx1, sy0), (sx1, sy1), (1, 0), height, sh)]
        top_z, top_rect = sh, (sx0, sx1, sy0, sy1)
    else:
        parapet(f"b{i}_rim", x0, x1, y0, y1, height, roof)
    tx0, tx1, ty0, ty1 = top_rect
    # Rooftop units: small boxes on the roof, kept off its edges.
    for u in range(opts.get("units", 0)):
        w, d = rng.uniform(0.9, 1.6), rng.uniform(0.8, 1.4)
        ux = rng.uniform(tx0 + 0.7, max(tx0 + 0.7, tx1 - 0.7 - w))
        uy = rng.uniform(ty0 + 0.7, max(ty0 + 0.7, ty1 - 0.7 - d))
        uh = rng.uniform(0.45, 0.85)
        unit = mk.box(f"b{i}_unit{u}", ux, ux + w, uy, uy + d, top_z - 0.05, top_z + uh, m["wall"])
        mk.bevel(unit, 0.1, 1, 35)
        mk.shade(unit, 35)
        mk.paint(unit, lambda c, n: m["dark"] if n.z > 0.8 else None)
    # Skylights: lit panes let into the roof.
    for s in range(opts.get("sky", 0)):
        w, d = rng.uniform(0.7, 1.1), rng.uniform(0.6, 0.9)
        sx = rng.uniform(tx0 + 0.6, max(tx0 + 0.6, tx1 - 0.6 - w))
        sy = rng.uniform(ty0 + 0.6, max(ty0 + 0.6, ty1 - 0.6 - d))
        mk.box(f"b{i}_sky{s}", sx, sx + w, sy, sy + d, top_z - 0.05, top_z + 0.06, m["window"])
    if "mast" in opts:
        cx, cy = (tx0 + tx1) / 2, (ty0 + ty1) / 2
        mh = min(opts["mast"], glass_height(cx, cy) - top_z - 0.6)
        k.smooth(mk.tube(f"b{i}_mast", [(cx, cy, top_z - 0.1), (cx, cy, top_z + mh)], 0.16, m["light"], 8), 50)
        mk.ball(f"b{i}_mast_tip", (cx, cy, top_z + mh), (0.28, 0.28, 0.28), m["lamp"], 10, 5)
    if "lamp" in opts:
        lc, lr, lh = opts["lamp"]
        lx, ly = P(lc, lr)
        k.smooth(mk.tube(f"b{i}_lamp_mast", [(lx, ly, height - 0.1), (lx, ly, height + lh)], 0.14, m["collar"], 8), 50)
        mk.ball(f"b{i}_lamp", (lx, ly, height + lh + 0.2), (0.42, 0.42, 0.38), m["lamp"], 12, 6)
    windows(f"b{i}_windows", walls, rng, m, 0.45 if height > 4 else 0.3)


def hall(m):
    """The round hall at the bottom left of the middle: a drum under a shallow dome, a ring of windows."""
    (cx, cy), r, wall_h, dome_h = HALL
    z0 = FLOOR_Z - 0.05
    drum = mk.lathe("hall", [(r, z0), (r, wall_h), (r - 0.25, wall_h + 0.2)], (cx, cy), m["wall"], 40)
    k.smooth(drum, 40)
    mk.dome("hall_dome", (cx, cy), (r - 0.35, r - 0.35, dome_h), wall_h + 0.1, m["light"], 40, 8, power=2.6)
    lantern = mk.lathe("hall_lantern", [(0.75, wall_h + dome_h - 0.2), (0.75, wall_h + dome_h + 0.45),
                                        (0.5, wall_h + dome_h + 0.65)], (cx, cy), m["window"], 16)
    k.smooth(lantern, 40)
    verts, polys = [], []
    for j in range(16):
        a = 2 * math.pi * (j + 0.5) / 16
        if math.sin(a) > 0.55:  # the back, which the camera doesn't see
            continue
        for z in (0.9,):
            if (j + int(z)) % 3 == 0:
                continue
            base = len(verts)
            for da, dz in ((-0.11, 0.0), (0.11, 0.0), (0.11, 0.5), (-0.11, 0.5)):
                verts.append((cx + (r + 0.04) * math.cos(a + da), cy + (r + 0.04) * math.sin(a + da), z + dz))
            polys.append((base, base + 1, base + 2, base + 3))
    win = k.mesh_object("hall_windows", verts, polys, m["window"])
    for poly in win.data.polygons:
        out = Vector((poly.center.x - cx, poly.center.y - cy, 0.0))
        if poly.normal.dot(out) < 0:
            poly.flip()
    return drum


def shell_point(t, a, lift=0.0):
    """The point on the glass at plan radius t (a share of its foot's radius) and angle a (radians), lifted along
    the shell's normal."""
    r = t * GLASS_R
    x, y = CENTRE[0] + r * math.cos(a), CENTRE[1] + r * math.sin(a)
    z = glass_height(x, y)
    # The normal of the superellipse profile (r/R)^p + (h/H)^p = 1 there.
    p = GLASS_POWER
    h = max(z - GLASS_Z0, 1e-4)
    nr = p * t ** (p - 1) / GLASS_R
    nz = p * (h / GLASS_H) ** (p - 1) / GLASS_H
    n = Vector((nr * math.cos(a), nr * math.sin(a), nz)).normalized()
    return Vector((x, y, z)) + n * lift


def glass(m):
    """The glass shell: a superellipse profile from its foot on the collar up to its crown, one-sided; its rings
    laid on the bands' edges (it darkens towards its foot in bands)."""
    # Plan radii of the rings (shares of the foot's radius), from the foot in; the bands' edges among them.
    ts = [1.0, 0.995, 0.985, 0.97, BANDS[2], 0.93, 0.91, BANDS[1], 0.84, 0.8, BANDS[0], 0.68, 0.6, 0.5, 0.38, 0.24,
          0.1]
    segments = 128
    rings = [[shell_point(t, 2 * math.pi * j / segments) for j in range(segments)] for t in ts]
    shell = k.loft("glassshell", rings, m["glass"], cap_start=False,
                   end_point=(CENTRE[0], CENTRE[1], GLASS_Z0 + GLASS_H))
    k.smooth(shell, 60)
    b0, b1, b2 = BANDS

    def pick(c, n):
        t = math.hypot(c.x - CENTRE[0], c.y - CENTRE[1]) / GLASS_R
        if t > b1:
            return m["glass_dark"]
        if t > b0:
            return m["glass_dim"]
        # The glass's lower half, turned away from the sun and towards the camera, dimmer (as the sprite shades it).
        a = math.degrees(math.atan2(c.y - CENTRE[1], c.x - CENTRE[0]))
        if t > 0.42 and -150.0 < a < -30.0:
            return m["glass_dim"]
        return None
    mk.paint(shell, pick)
    return shell


def overlay(name, points_of, rows, cols, mat):
    """A thin film lying on the glass: a grid of points_of(u, v) (u, v in 0..1), its faces facing out."""
    verts = [points_of(i / rows, j / cols) for i in range(rows + 1) for j in range(cols + 1)]
    faces = []
    for i in range(rows):
        for j in range(cols):
            a = i * (cols + 1) + j
            faces.append((a, a + 1, a + cols + 2, a + cols + 1))
    obj = k.mesh_object(name, verts, faces, mat)
    for poly in obj.data.polygons:
        out = Vector(poly.center) - Vector((CENTRE[0], CENTRE[1], GLASS_Z0))
        if poly.normal.dot(out) < 0:
            poly.flip()
    obj.data.update()
    k.smooth(obj, 80)
    return obj


def highlights(m):
    """The glint up and to the left (a white lens in a paler halo) and the crescent of light along the lower right
    edge (a pale band, white in its middle), films lying on the glass. Their names sort after the glass shell's, so
    that their materials follow the glass's in the model (the game draws a model's see-through materials in that
    order, without sorting them: the films blend over the glass, the halo first, the white last)."""
    (gx, gy), r_glint, r_halo = GLINT
    a_g = math.atan2(gy - CENTRE[1], gx - CENTRE[0])
    t_g = math.hypot(gx - CENTRE[0], gy - CENTRE[1]) / GLASS_R

    def lens(radius, lift):
        def at(u, v):
            # Polar round the glint's middle, in plan, then onto the glass.
            rr, a = radius * u, 2 * math.pi * v
            x, y = gx + rr * math.cos(a), gy + rr * math.sin(a) * 0.92
            t = math.hypot(x - CENTRE[0], y - CENTRE[1]) / GLASS_R
            return shell_point(t, math.atan2(y - CENTRE[1], x - CENTRE[0]), lift)
        return at
    overlay("glassshell_a_halo", lens(r_halo, 0.03), 5, 40, m["halo"])
    overlay("glassshell_b_sheen", lens((r_glint + r_halo) / 2, 0.045), 4, 40, m["sheen"])
    overlay("glassshell_c_glint", lens(r_glint, 0.06), 4, 40, m["glint"])
    a0, a1, t0, t1, (c0, c1) = CRESCENT

    def band(lo, hi, w0, w1, lift):
        """A crescent between the angles lo and hi (degrees), its radial span narrowing to its ends."""
        def at(u, v):
            a = math.radians(lo + (hi - lo) * v)
            taper = math.sin(math.pi * v) ** 0.7
            mid = (w0 + w1) / 2
            half = (w1 - w0) / 2 * taper
            t = mid + (u - 0.5) * 2 * half
            return shell_point(t, a, lift)
        return at
    overlay("glassshell_b_crescent", band(a0, a1, t0, t1, 0.03), 4, 48, m["sheen"])
    mid = (t0 + t1) / 2 + 0.012
    overlay("glassshell_c_core", band(c0, c1, mid - 0.018, mid + 0.018, 0.06), 2, 24, m["glint"])


# --- Build --------------------------------------------------------------------------------------------------------

def build_whole(m):
    collar(m)
    floor(m)
    rng = random.Random(SEED)
    for i, spec in enumerate(CITY):
        building(i, spec, m, rng)
    hall(m)
    solid = mk.meshes()
    for obj in solid:
        mk.apply(obj)
    shells = [glass(m)]
    before = set(mk.meshes())
    highlights(m)
    shells += [o for o in mk.meshes() if o not in before]
    bpy.context.view_layer.update()
    return solid, shells


def dome_mask():
    """The dome's pixels: within its rim's circle (the drawn dirt and shadow left out)."""
    return [[math.hypot(c + 0.5 - 24.0 - CENTRE[0], 28.0 - r - 0.5 - CENTRE[1]) < R_OUT for c in range(48)]
            for r in range(56)]


def piece_mask(sprite):
    c0, r0 = SPRITE_AT[sprite]
    whole = dome_mask()
    return [row[c0:c0 + 24] for row in whole[r0:r0 + 28]]


def cut_open(source, box_xy):
    """The part of an open shell inside the box, its cuts left open (no caps), its shading the whole's."""
    x0, x1, y0, y1 = box_xy
    obj = source.copy()
    obj.data = source.data.copy()
    bpy.context.scene.collection.objects.link(obj)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    planes = (((x0, 0, 0), (-1, 0, 0)), ((x1, 0, 0), (1, 0, 0)), ((0, y0, 0), (0, -1, 0)), ((0, y1, 0), (0, 1, 0)))
    for co, no in planes:
        if not bm.faces:
            break
        bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-6, plane_co=co, plane_no=no,
                               clear_outer=True)
    if not bm.faces:
        bm.free()
        bpy.data.objects.remove(obj)
        return None
    bm.to_mesh(obj.data)
    bm.free()
    shading = mk.NormalSource(source)
    mesh = obj.data
    normals = []
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            n = shading.normal(mesh.vertices[mesh.loops[li].vertex_index].co, poly.center)
            normals.append(tuple(n if n is not None else poly.normal))
    mesh.normals_split_custom_set(normals)
    return obj


def build():
    options = k.args()
    out = mk.outdir(options)
    k.reset()
    m = materials()
    solid, shells = build_whole(m)
    whole = solid + shells
    print("whole glass city: %d triangles, %d objects" % (mk.triangles(whole), len(whole)))
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    if "check" in options:
        mk.compare("whole (R 1 + 3 above 39 + 41, the dome)", mk.coverage(whole, 48, 56), dome_mask())
    if "preview" in options:
        mk.preview(options["preview"] + "glass_city_whole", whole, size=(48, 56), scale=8, distance=1.8)
    only = options["only"].split(",") if "only" in options else None
    for name, sprite, box in PIECES:
        if only and name not in only:
            continue
        pieces = [p for p in (cut(src, box, m["collar"]) for src in solid) if p is not None]
        pieces += [p for p in (cut_open(src, box) for src in shells) if p is not None]
        mk.transform(pieces, Matrix.Translation((-(box[0] + box[1]) / 2, -(box[2] + box[3]) / 2, 0)))
        bpy.context.view_layer.update()
        for src in whole:
            src.hide_render = True
        if "check" in options:
            mk.compare("%s (R %d)" % (name, sprite), mk.coverage(pieces, 24, 28), piece_mask(sprite))
        mk.report(name, pieces, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, pieces)
        for obj in pieces:
            bpy.data.objects.remove(obj)
        for src in whole:
            src.hide_render = False


if __name__ == "__main__":
    build()
