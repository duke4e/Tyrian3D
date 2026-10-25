"""What is left of MINERS's grey roller and blue tank once they are destroyed (stage 4 of the clean ground: the wreck
models that stand in for the map's painting of them; sheet M sprites 155 beside 157, and 159 beside 161), built on
polish_miners_machines.py (2026-10-25). models.cfg: model miners_roller_l_wreck / miners_roller_r_wreck /
miners_tank_l_wreck / miners_tank_r_wreck enemies/<name>.glb origin; wreck m 155 miners_roller_l_wreck, wreck m 157
miners_roller_r_wreck, wreck m 159 miners_tank_l_wreck, wreck m 161 miners_tank_r_wreck. The game draws them where
MINERS paints the wrecks (each machine four times: the map's own tiles under them), with the live sprite lines'
options (yaw=0 height=-4), at the live pieces' places.

The paintings (MINERS at (480, 3906) and (456, 3962), in the HD tiles and at 1x; columns and rows of the 48 x 28
pictures, the red sand round them the map's):
- The roller: the wheel crushed into a low heap (columns 3-13, rows 8-23: the live wheel stands from row 2), its top
  left lit grey (0x07-0x0a), blue-grey down its left side (0x64-0x67), its right half black (0x00-0x02, ramp 15's
  purple-blacks); the drum gone, a charred scrap and a dull red spark where its middle was (columns 17-21, rows 10-16);
  the block broken down (rows 6-26: its top 5 rows lower), its top a dark broken hollow with blue-grey and grey
  edges, a red-hot ember in it (columns 40-41, rows 13-15, 0x72-0x73), its front still standing (lit bits in rows
  19-25), black rubble spilling out of its left side towards the drum's place (columns 26-32, rows 10-19); the plates
  gone.
- The tank: its outline as the live sprites', the bolster's back end gone (its top from row 4, the live one's from
  row 1) and its right half burnt black from end to end (columns 7-11, rows 8-22); the body's blues two or three shades
  darker (0x30-0x37), a few cyan edges left; black holes burnt through it: at its front left of the middle (columns
  16-21, rows 15-22), a gash at columns 34-35 (rows 14-22), the right end's front corner (columns 40-43, rows 13-17
  and 19-22, a lip of blue between); the rail snapped (columns 21-24 bare), a scrap of it on the sand in front
  (columns 17-18, row 23); the spout dark (0x63-0x64).

The models: polish_miners_machines.py's machines, then broken.
- The roller: the wheel (disc, knobs, hub) crushed (squashed down to 0.4 of its height, leaning over towards the
  block, pressed together along y and crumpled by noise), four knobs blown away, painted by the light in the burnt
  shades (paint_burnt: lit grey 0x08-0x0a, blue-greys 0x69 / 0x64, dark 0x03, near black 0x02; the hub its blue-greys);
  the drum and axle gone (an axle stub bent down out of the hub, a charred torn piece of the drum's shell arched on the
  ground with a dull ember, crumbs); the block battered (its faces cut on a grid and dented by noise), its top cut away
  by a jagged height field falling from the front (z 14.6) to the back (z 9.2), its corners broken lower, a hollow
  sunk into it (black) with an ember glowing in it (0x73 at 0.3, its core 0x75 at 0.36), its left wall torn open
  (along the camera's line of sight, black inside), painted by the light as the wheel; two slabs broken off its left
  side lying tumbled against it, black rubble at its foot, torn plates on its top and the slabs; the plates gone; the
  faces charred (0x01) where a field passes ROLLER_CHAR (the hollow's rim, the block's left side, the wheel's inner
  half: the painting's blacks).
- The tank: the bolster's back end cut off along the camera's line of sight (row 4), the holes cut as exact booleans
  along the camera's line of sight (view prisms: what the camera sees at the painting's black pixels) down to a floor
  over the ground, their walls and floors black (0x30), dull embers in two of them (0x71, 0x72 at 0.2-0.24); the rail
  in two bent halves, the posts kept, a bent scrap of it on the sand in front; the panels and rivets kept where no hole
  is; everything scorched (one level everywhere on the top, two round the holes: blue shades in the tank's own ramps,
  BURNT_TANK).
Each machine cut at x = 0 as the live one (polish_stone_face.view_cut, an upright plane), the cuts closed in char,
each piece moved so that its sprite's centre is its origin (polish_miners_machines.export_pieces).

Coordinates as polish_miners_machines.py's: 1 unit = 1 game pixel; +X right, +Y up the screen, +Z up from the ground
(z = 0); each whole's origin is its picture's middle: the pixel corner (c, r) is (c - 24, 14 - r); the camera sees a
point (x, y, z) at picture y + z tan 20.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir>, --preview <prefix>, --whole
<prefix> (the uncut wrecks as <prefix>miners_<roller|tank>_wreck.glb), --only <name,...>.
"""
import math
import os
import random
import sys

import bmesh
import bpy
import mathutils.noise as noise
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_jaw_gun_wreck import jagged, ccw, lump, rock, shard, bent_bar, grid_cut  # noqa: E402
from polish_pyramid_wreck import break_with, heightfield_cutter, chunk, block, Noise  # noqa: E402
from polish_bronze_pump_wreck import scorch_map  # noqa: E402
import polish_miners_machines as live  # noqa: E402

TILT = live.TILT
LIGHT = live.LIGHT
P = live.P
SEED = 155

WRECK_PIECES = {key: [(name + "_wreck", sprite, box, centre) for name, sprite, box, centre in specs]
                for key, specs in live.PIECES.items()}


# --- Shared ----------------------------------------------------------------------------------------------------------

def vnoise(p):
    """A noise vector: Perlin noise at three offsets (mathutils.noise.noise_vector is not the same from run to run)."""
    p = Vector(p)
    return Vector((noise.noise(p + Vector((13.1, 0.0, 0.0))), noise.noise(p + Vector((0.0, 27.3, 0.0))),
                   noise.noise(p + Vector((0.0, 0.0, 41.7)))))


def view_prism(name, outline, z0, z1, mat, seed=None, amount=0.35, step=0.6):
    """A prism over an outline [(column, row), ...] of the picture, along the camera's line of sight: it holds what
    the camera sees there between heights z0 and z1 (each point (x, y) of the picture at height z lies at
    y - z tan 20); the outline made jagged by noise if a seed is given."""
    pts = [P(c, r) for c, r in outline]
    if seed is not None:
        pts = jagged(pts, seed, amount, step)
    obj = mk.prism(name, ccw(pts), z0, z1, mat)
    for v in obj.data.vertices:
        v.co.y -= v.co.z * TILT
    obj.data.update()
    return obj


def jag_line(points, seed, amount=0.35, step=0.6):
    """An open line's points roughened as jagged() roughens an outline (its ends kept)."""
    out = []
    for a, b in zip(points, points[1:]):
        a, b = Vector(a), Vector(b)
        d = b - a
        count = max(1, int(round(d.length / step)))
        normal = Vector((d.y, -d.x)).normalized()
        for j in range(count):
            p = a + d * (j / count)
            off = amount * noise.noise(Vector((p.x * 0.9 + seed, p.y * 0.9 - seed, seed * 0.37))) if out else 0.0
            out.append(tuple(p + normal * off))
    out.append(tuple(points[-1]))
    return out


def cut_out(parts, cutter):
    """parts with the cutter's volume cut out of those it reaches (exact booleans, deterministic order; the broken
    faces take the cutter's material); returns the new list."""
    lo, hi = mk.bounds([cutter])

    def reaches(obj):
        a, b = mk.bounds([obj])
        return a.x < hi.x and b.x > lo.x and a.y < hi.y and b.y > lo.y and a.z < hi.z and b.z > lo.z
    hit = [o for o in parts if reaches(o)]
    if not hit:
        data = cutter.data
        bpy.data.objects.remove(cutter)
        bpy.data.meshes.remove(data)
        return parts
    return [o for o in parts if o not in hit] + break_with(hit, cutter)


def clear_normals(obj):
    if obj.data.has_custom_normals:
        with bpy.context.temp_override(object=obj, active_object=obj, selected_editable_objects=[obj]):
            bpy.ops.mesh.customdata_custom_splitnormals_clear()


def remove(objs):
    for obj in objs:
        data = obj.data
        bpy.data.objects.remove(obj)
        if data is not None and data.users == 0:
            bpy.data.meshes.remove(data)


def ember_mat(index, strength):
    return k.material("miners_ember_%d" % int(round(strength * 100)), palette=index, metallic=0.0, roughness=0.8,
                      emission=k.level_palette()[index], emission_strength=strength)


def picture_point(c, r, z):
    """The world point at height z that the camera sees at the picture's (column, row)."""
    x, y = P(c, r)
    return (x, y - z * TILT, z)


# --- The roller ------------------------------------------------------------------------------------------------------
R = live.WHEEL_R
AXLE_Y = live.AXLE_Y
CRUSH = dict(z=0.45, z_top=0.36, y=0.7, lean=0.18, crumple=1.3)   # the wheel's crush (see crush())
GONE_KNOBS = (3, 4, 9, 10)            # knocked off (blown away)
# The block's broken top: its height falls from BLOCK_TOP[0] at its front to BLOCK_TOP[1] at its back, jagged by
# BLOCK_JAG; its corners broken lower (plan x, y, radius, depth); the hollow in it (picture middle (column, row),
# radii, its floor's height).
BLOCK_TOP = (14.6, 9.2)
BLOCK_JAG = 2.0
CORNERS = [(8.4, -12.0, 3.2, 5.5), (21.0, 6.0, 3.4, 3.0), (8.4, 6.0, 3.0, 2.4), (21.0, -12.0, 2.2, 2.0)]
HOLLOW = ((38.2, 12.4), (5.2, 4.2), 4.4)
EMBER = ((40.6, 14.2), (1.4, 1.0, 0.7))   # the ember in the hollow: picture position, radii
# The block's left wall torn open towards the drum's place (picture outline, floor).
BLOCK_BREACH = ([(31.4, 9.0), (33.6, 8.4), (35.0, 10.4), (34.8, 14.6), (35.2, 18.6), (33.4, 19.6), (31.2, 18.8),
                 (30.6, 14.0)], 2.2)
# The rubble heaped against the block's left side (plan x, y, size, kind).
RUBBLE = [(6.6, -6.2, 2.6, "char"), (3.6, -4.2, 1.8, "dark"), (7.4, 3.4, 2.2, "char"), (4.0, 3.6, 1.4, "char"),
          (7.6, -9.0, 1.8, "char"), (9.2, 4.8, 1.6, "dark")]
# The slabs broken off the block's left side, lying tumbled against it (centre, size, turn (degrees about x, y, z)).
SLABS = [((5.4, -1.2, 0.0), (4.6, 7.2, 1.6), (6.0, -30.0, 6.0)), ((4.0, 3.0, 0.0), (3.2, 4.0, 1.3), (-8.0, -18.0, -14.0))]
# Torn plates: (outline (plan), z, tilt (degrees about x, y), material).
PLATES = [([(12.8, 2.0), (15.8, 2.6), (15.4, 5.0), (12.6, 4.6)], 7.4, (-24.0, 16.0), "plate"),
          ([(4.2, -3.0), (7.2, -3.4), (7.4, -0.8), (4.6, -0.4)], 3.6, (18.0, -34.0), "plate_tint"),
          ([(17.4, -8.4), (19.8, -8.2), (19.6, -6.2), (17.6, -6.4)], 12.4, (30.0, 10.0), "plate_lit")]
# The drum's charred scrap (a torn piece of its shell lying arched on the ground: middle, heading, length, radius),
# its dull ember, crumbs; the axle's stub.
DRUM_SCRAP = ((-5.0, 0.8), 35.0, 4.0, 1.3)
DRUM_EMBER = ((-3.6, -0.6, 0.5), (0.6, 0.5, 0.3))
CRUMBS = [(-7.4, 3.4, 0.6), (-2.6, -2.6, 0.5), (-8.2, -0.8, 0.45)]
AXLE_STUB = [(-14.4, AXLE_Y + 0.4, 4.4, 1.0), (-12.0, AXLE_Y + 0.8, 3.6, 0.9), (-10.2, AXLE_Y + 1.6, 2.0, 0.7)]


def roller_materials():
    m = live.roller_materials()
    mat = live.mat
    m["burnt_grey"] = mat("roller_burnt", 0x05, 0.3, 0.5)
    m["burnt_lit"] = mat("roller_burnt", 0x08, 0.3, 0.45)
    m["burnt_dark"] = mat("roller_burnt", 0x03, 0.25, 0.6)
    m["burnt_blue"] = mat("roller_burnt_blue", 0x66, 0.4, 0.45)
    m["burnt_blue_dark"] = mat("roller_burnt_blue", 0x64, 0.35, 0.5)
    m["char"] = mat("roller_char", 0x01, 0.1, 0.8)
    m["ember"] = ember_mat(0x73, 0.3)
    m["ember_hot"] = ember_mat(0x75, 0.36)
    m["ember_dull"] = ember_mat(0x71, 0.2)
    return m


def roller_burnt(m):
    """material name -> charred (where the scorch field passes ROLLER_CHAR): every material but the embers'."""
    return {mat.name: (m["char"],) for key, mat in m.items() if not key.startswith("ember")}


ROLLER_CHAR = 0.75


def paint_burnt(obj, m, seed=0.0, lift=0.0):
    """Faces painted by the light they get, in the burnt shades (the painting's): lit grey, blue-grey, dark
    blue-grey, dark grey, near black; a little noise moves faces between bands."""
    def pick(c, n):
        d = n.dot(LIGHT) + lift + 0.12 * noise.noise(Vector((c.x * 0.8 + seed, c.y * 0.8, c.z * 0.8)))
        if d > 0.93:
            return m["grey"]
        if d > 0.8:
            return m["burnt_lit"]
        if d > 0.58:
            return m["blue_grey"] if noise.noise(Vector((c.x * 0.5, c.y * 0.5 + seed, c.z))) > 0 else m["burnt_grey"]
        if d > 0.3:
            return m["burnt_blue_dark"]
        if d > -0.05:
            return m["burnt_dark"]
        return m["rubber"]
    mk.paint(obj, pick)
    return obj


def batter(obj, amount, seed, freq=0.45, min_z=0.4):
    """Dents a part: its vertices (over min_z) pushed by noise."""
    for v in obj.data.vertices:
        if v.co.z < min_z:
            continue
        d = vnoise(Vector((v.co.x * freq + seed, v.co.y * freq, v.co.z * freq)))
        v.co += d * amount * min(1.0, (v.co.z - min_z) / 1.5)
    obj.data.update()
    return obj


def crush(co):
    """Where a point of the live wheel lies once the wheel is crushed: squashed down (its top more), pressed together
    along y round the axle's place, leaning over towards the block (+x), crumpled (two octaves of noise)."""
    t = max(0.0, min(1.0, co.z / (2 * R)))
    z = co.z * (CRUSH["z"] - (CRUSH["z"] - CRUSH["z_top"]) * t * t)
    y = AXLE_Y + (co.y - AXLE_Y) * CRUSH["y"]
    x = co.x + CRUSH["lean"] * co.z
    p = Vector((co.x * 0.2 + 4.1, co.y * 0.2, co.z * 0.2))
    d = vnoise(p) + 0.45 * vnoise(p * 2.3 + Vector((7.7, 1.3, -2.9)))
    lift = min(1.0, co.z / 3.0)          # (its foot stays on the ground)
    return Vector((x + d.x * CRUSH["crumple"] * 0.6, y + d.y * CRUSH["crumple"],
                   max(0.0, z + d.z * CRUSH["crumple"] * lift)))


def roller_field(co):
    """The roller's scorch: one level nearly everywhere, two round the block's hollow and breach, over its back and
    the wheel's inner half (the painting's blacks); the wheel's lit top left and the block's front less."""
    c, r = co.x + 24.0, 14.0 - (co.y + co.z * TILT)        # where the camera sees the point
    v = 0.5 + 0.22 * roller_field.noise.fbm(c * 0.7, r * 0.7, 2)
    (hc, hr), (rx, ry), _ = HOLLOW
    v += 0.45 * math.exp(-(((c - hc) / (rx + 2.0)) ** 2 + ((r - hr) / (ry + 2.0)) ** 2))
    v += 0.45 * math.exp(-(((c - 31.0) / 3.5) ** 2 + ((r - 14.0) / 6.0) ** 2))   # the block's left side
    v += 0.55 * math.exp(-(((c - 12.4) / 2.8) ** 2 + ((r - 15.0) / 6.0) ** 2))  # the wheel's inner half
    v -= 0.35 * math.exp(-(((c - 6.0) / 3.0) ** 2 + ((r - 11.0) / 3.5) ** 2))   # the wheel's lit top left
    v -= 0.3 * math.exp(-(((c - 41.0) / 3.0) ** 2 + ((r - 21.5) / 2.5) ** 2))   # the block's front right
    return v


roller_field.noise = Noise(SEED + 7, 1.6)


def drum_scrap(m):
    """A torn piece of the drum's shell lying arched on the ground (a C section lofted along its length)."""
    (x0, y0), heading, length, radius = DRUM_SCRAP
    rings = []
    n, arc = 9, 12
    for i in range(n + 1):
        u = (i / n - 0.5) * length
        squeeze = 1.0 - 0.25 * abs(2 * i / n - 1) ** 2      # (its torn ends lower)
        ring = []
        for j in range(arc + 1):
            a = math.pi * (0.08 + 0.84 * j / arc)
            ring.append(Vector((u, radius * math.cos(a), radius * math.sin(a) * 0.5 * squeeze)))
        for j in range(arc, -1, -1):
            a = math.pi * (0.08 + 0.84 * j / arc)
            ring.append(Vector((u, (radius - 0.4) * math.cos(a), max(0.0, (radius - 0.4) * math.sin(a) * 0.5 *
                                                                      squeeze))))
        rings.append(ring)
    obj = k.loft("drum_scrap", rings, m["char"])
    for v in obj.data.vertices:
        d = vnoise(Vector((v.co.x * 0.7 + 2.0, v.co.y * 0.7, v.co.z * 0.7)))
        v.co += d * 0.25
        v.co.z = max(0.0, v.co.z - 0.35)
    obj.data.transform(Matrix.Translation((x0, y0, 0.0)) @ Matrix.Rotation(math.radians(heading), 4, "Z"))
    k.recalc_normals(obj)
    k.smooth(obj, 50)
    parts = [obj]
    (x, y, z), radii = DRUM_EMBER
    e = lump("drum_ember", (x, y, z * 0.5), radii, m["ember_dull"], 3.3, 0.2, 1)
    k.smooth(e, 70)
    parts.append(e)
    for i, (x, y, size) in enumerate(CRUMBS):
        parts.append(rock("drum_crumb%d" % i, (x, y, 0.0), (size * 1.4, size, size * 0.7), m["char"], 11.0 + 1.7 * i,
                          flat=0.0))
    return parts


def crushed_wheel(m):
    parts = live.wheel(m)        # disc, knobs 0-13, hub
    keep = []
    for obj in parts:
        if obj.name.startswith("knob") and int(obj.name[4:]) in GONE_KNOBS:
            remove([obj])
            continue
        keep.append(obj)
    for obj in keep:
        mk.apply(obj)
        clear_normals(obj)
        for v in obj.data.vertices:
            v.co = crush(v.co)
        obj.data.update()
        k.recalc_normals(obj)
        if obj.name == "hub":
            live.paint_light(obj, m["burnt_blue"], m["blue_grey"], m["burnt_blue_dark"])
        else:
            paint_burnt(obj, m, 1.7)
        k.smooth(obj, 50)
    # the axle's stub bent down out of the hub, the drum's charred scrap and its dull ember on the ground
    keep.append(bent_bar("axle_stub", AXLE_STUB, 1.0, m["burnt_dark"]))
    return keep + drum_scrap(m)


def block_top(x, y):
    """The block's broken top: falling from the front to the back, jagged, its corners broken lower, the hollow sunk
    into it."""
    t = (y - live.BLOCK_FRONT) / (live.BLOCK_BACK - live.BLOCK_FRONT)
    z = BLOCK_TOP[0] + (BLOCK_TOP[1] - BLOCK_TOP[0]) * t
    z += BLOCK_JAG * block_top.noise.fbm(x * 0.6, y * 0.6, 3)
    for cx, cy, rad, depth in CORNERS:
        z -= depth * math.exp(-((x - cx) ** 2 + (y - cy) ** 2) / rad ** 2)
    # the hollow, where the camera sees it at the height of its rim
    (hc, hr), (rx, ry), floor = HOLLOW
    zr = z
    c, r = x + 24.0, 14.0 - (y + zr * TILT)
    q = math.hypot((c - hc) / rx, (r - hr) / ry) + 0.15 * block_top.noise(x * 1.3 + 5.0, y * 1.3)
    if q < 1.0:
        z = min(z, floor + (zr - floor) * (q ** 4))
    return max(z, 1.0)


block_top.noise = Noise(SEED + 3, 1.0)


def slab_block(name, centre, size, rot, mat):
    return block(name, centre, size, rot, mat, bevel=0.2, sink=0.3)


def broken_block(m):
    parts = live.block(m)        # body, plates
    for obj in [o for o in parts if o.name.startswith("plate")]:
        parts.remove(obj)
        remove([obj])
    body = parts[0]
    mk.apply(body)
    clear_normals(body)
    grid_cut(body, 1.5, ("x", "y", "z"))
    batter(body, 0.55, 3.0)
    k.recalc_normals(body)
    b = live.BLOCK
    xs = [round(b["x0"] - 0.6 + i * 0.5, 4) for i in range(int((b["x1"] - b["x0"] + 1.2) / 0.5) + 2)]
    ys = [round(live.BLOCK_FRONT - 0.6 + j * 0.5, 4)
          for j in range(int((live.BLOCK_BACK - live.BLOCK_FRONT + 1.2) / 0.5) + 2)]
    cutter = heightfield_cutter("block_top", xs, ys, block_top, 40.0, m["burnt_blue_dark"])
    parts = break_with([body], cutter)
    outline, floor = BLOCK_BREACH
    parts = cut_out(parts, view_prism("block_breach", outline, floor, 40.0, m["char"], SEED * 0.31, 0.5))
    body = parts[0]
    # painted by the light, the hollow black
    (hc, hr), (rx, ry), hfloor = HOLLOW
    paint_burnt(body, m, 4.2, -0.06)
    mk.paint(body, lambda c, n: m["char"] if (math.hypot((c.x + 24.0 - hc) / rx, (14.0 - c.y - c.z * TILT - hr) / ry)
                                              < 0.9 and c.z < BLOCK_TOP[0] - 4.0) else None)
    mk.shade(body, 30)
    # the ember in the hollow, a hotter core
    (c, r), (ex, ey, ez) = EMBER
    x, y, z = picture_point(c, r, hfloor)
    parts.append(lump("block_ember", (x, y, hfloor + 0.2), (ex, ey, ez), m["ember"], 5.1, 0.25, 2))
    parts.append(lump("block_ember_core", (x + 0.2, y + 0.1, hfloor + 0.5), (ex * 0.5, ey * 0.5, ez * 0.7),
                      m["ember_hot"], 6.7, 0.2, 1))
    for obj in parts[-2:]:
        k.smooth(obj, 70)
    # the rubble against its left side, the torn plates
    rng = random.Random(SEED + 1)
    mats = {"char": m["char"], "dark": m["burnt_dark"], "grey": m["burnt_grey"]}
    for i, (centre, size, rot) in enumerate(SLABS):
        obj = slab_block("slab%d" % i, centre, size, rot, m["burnt_dark"])
        grid_cut(obj, 1.2, ("x", "y", "z"))
        batter(obj, 0.3, 9.0 + i, 0.6, -9.0)
        k.recalc_normals(obj)
        paint_burnt(obj, m, 6.0 + i, -0.2)
        mk.shade(obj, 30)
        parts.append(obj)
    for i, (x, y, size, kind) in enumerate(RUBBLE):
        obj = chunk("rubble%d" % i, (x, y, 0.0), size, rng, mats[kind], flat=0.6)
        mk.shade(obj, 30)
        parts.append(obj)
    for i, (outline, z, tilt, key) in enumerate(PLATES):
        plate = shard("torn_plate%d" % i, outline, z, 0.3, m[key], tilt)
        mk.paint(plate, lambda c, n: m["burnt_dark"] if n.dot(LIGHT) < 0.3 else None)
        parts.append(plate)
    return parts


def roller_wreck(m):
    return crushed_wheel(m) + broken_block(m)


# --- The tank --------------------------------------------------------------------------------------------------------
# The holes burnt through it (picture outlines, their floors' heights), its bolster's back end (cut off up the screen
# from the outline's row), the panels blown off, the rail's halves, the scrap on the sand.
TANK_HOLES = [
    ("bolster_hole", [(6.8, 8.2), (9.0, 7.6), (12.0, 7.8), (13.0, 12.0), (12.8, 17.0), (13.0, 22.8), (9.4, 23.2),
                      (6.8, 22.6), (7.2, 17.0), (6.6, 12.4)], 1.0),
    ("front_hole", [(16.4, 14.6), (18.8, 13.8), (21.6, 14.8), (22.0, 18.0), (21.6, 22.0), (18.6, 22.6), (15.8, 21.8),
                    (15.9, 18.2)], 2.0),
    ("gash", [(33.4, 13.4), (35.2, 12.8), (36.6, 14.2), (36.4, 18.0), (36.6, 22.0), (34.6, 22.6), (33.2, 20.4),
              (33.6, 17.0)], 2.0),
    ("end", [(39.4, 13.2), (42.4, 12.8), (44.8, 13.4), (45.0, 17.0), (44.0, 18.0), (45.0, 19.0), (44.8, 22.8),
             (42.2, 23.0), (39.4, 22.6), (39.0, 18.0)], 1.4),
]
BOLSTER_CUT = [(3.0, 4.2), (5.4, 3.6), (7.6, 4.1), (9.8, 3.8), (12.2, 4.4), (12.2, -4.0), (3.0, -4.0)]
TANK_EMBERS = [("front_hole", (18.8, 18.6), (0.9, 0.7, 0.4), 0x72, 0.24),
               ("end", (42.0, 20.8), (0.7, 0.6, 0.35), 0x71, 0.2)]
GONE_PANELS = ("panel01", "panel13", "panel04")        # blown off (the rivets all melted away)
PANEL_PRESS = 0.25                                      # the others pressed down (their height over the top kept)
RAIL_HALVES = [[(-11.2, 0.0, 0.0), (-6.0, 0.0, 0.0), (-3.9, 0.15, 0.25), (-3.0, 0.5, 0.9)],
               [(0.4, -0.3, -0.9), (1.4, 0.0, -0.2), (6.0, 0.0, 0.0), (18.4, 0.0, 0.0)]]
RAIL_SCRAP = [(-7.4, -10.0, 0.35), (-6.2, -9.6, 0.5), (-5.0, -10.1, 0.35)]
TANK_SHARDS = [(-4.8, -11.0, 0.9, 20.0, "char"), (12.6, -10.6, 0.7, -30.0, "char"), (21.0, -4.6, 0.8, 50.0, "char"),
               (-19.2, 9.4, 0.8, 10.0, "char")]


def tank_materials():
    m = live.tank_materials()
    mat = live.mat
    # (burnt paint is matte: the live blues' finish would mirror the sky grey over the dark shades)
    m["matte_blue"] = mat("tank_burnt", 0x37, 0.15, 0.6)
    m["matte_dark"] = mat("tank_burnt", 0x34, 0.12, 0.65)
    m["burnt"] = mat("tank_burnt", 0x31, 0.1, 0.7)
    m["char"] = mat("tank_char", 0x30, 0.05, 0.85)
    m["rail_burnt"] = mat("tank_rail_burnt", 0xa4, 0.4, 0.45)
    return m


def tank_burnt(m):
    """material name -> (one, two, three levels burnt)."""
    blue, dark, burnt, char = m["matte_blue"], m["matte_dark"], m["burnt"], m["char"]
    return {m["blue"].name: (dark, burnt, char), m["blue_lit"].name: (blue, dark, burnt),
            m["blue_dark"].name: (burnt, burnt, char), m["cyan"].name: (blue, dark, burnt),
            m["rivet"].name: (dark, burnt, char),
            m["black"].name: (m["seam"], m["seam"], char), m["black_lit"].name: (m["black"], m["seam"], char),
            m["seam"].name: (m["seam"], char, char), m["rail"].name: (m["rail_burnt"],) * 3,
            m["rail_lit"].name: (m["rail"], m["rail_burnt"], m["rail_burnt"])}


def tank_field(co):
    """The tank's scorch: one level everywhere, blotches of two (low-frequency noise), two and three (soot) round the
    holes."""
    c, r = co.x + 24.0, 14.0 - (co.y + co.z * TILT)
    v = 0.5 + 0.36 * tank_field.noise.fbm(c * 0.45, r * 0.45, 2)
    for _, outline, _ in TANK_HOLES:
        hc = sum(p[0] for p in outline) / len(outline)
        hr = sum(p[1] for p in outline) / len(outline)
        v += 0.7 * math.exp(-(((c - hc) / 4.6) ** 2 + ((r - hr) / 6.0) ** 2))
    return v


tank_field.noise = Noise(SEED + 11, 1.8)


def tank_wreck(m):
    parts = live.tank(m)
    # panels blown off, the rail in two bent halves (the posts kept)
    for obj in [o for o in parts if o.name in GONE_PANELS or o.name == "rail" or o.name.startswith("rivet")]:
        parts.remove(obj)
        remove([obj])
    ry, rz = live.BODY_BACK - 1.1, live.BODY["h"] + 1.3
    for i, half in enumerate(RAIL_HALVES):
        bar = bent_bar("rail_half%d" % i, [(x, ry + dy, rz + dz, 0.65) for x, dy, dz in half], 0.65, m["rail"])
        live.paint_light(bar, m["rail"], m["rail_lit"], m["rail"], lit_at=0.4)
        parts.append(bar)
    for obj in parts:
        mk.apply(obj)
        if obj.name.startswith("panel"):   # (pressed down nearly flush with the top, dented)
            clear_normals(obj)
            top = live.BODY["h"]
            for v in obj.data.vertices:
                v.co.z = top + (v.co.z - top) * PANEL_PRESS
            batter(obj, 0.18, 2.0 + obj.name.count("1"), 0.7, top - 1.0)
            k.recalc_normals(obj)
            mk.shade(obj, 35)
    # the bolster's back end gone (along the camera's line of sight)
    back = jag_line([P(c, r) for c, r in BOLSTER_CUT[:5]], SEED * 0.07, 0.35, 0.6)
    outline = back + [P(c, r) for c, r in BOLSTER_CUT[5:]]
    cutter = mk.prism("bolster_back", ccw(outline), -1.0, 40.0, m["burnt"])
    for v in cutter.data.vertices:
        v.co.y -= v.co.z * TILT
    cutter.data.update()
    bolster = [o for o in parts if o.name == "bolster"]
    parts = [o for o in parts if o.name != "bolster"] + break_with(bolster, cutter)
    # the holes, black
    for i, (name, outline, floor) in enumerate(TANK_HOLES):
        parts = cut_out(parts, view_prism(name, outline, floor, 40.0, m["char"], SEED * 0.21 + i * 1.7, 0.6, 0.5))
    for obj in parts:
        step = 1.25 if obj.name in ("tank_body", "bolster") else 1.6 if obj.name.startswith("panel") else None
        scorch_map(obj, tank_field, tank_burnt(m), levels=(0.25, 0.62, 0.92), step=step)
        if obj.name in ("tank_body", "bolster"):
            mk.shade(obj, 35)
    for name, (c, r), radii, index, glow in TANK_EMBERS:
        floor = next(f for n, _, f in TANK_HOLES if n == name)
        x, y, z = picture_point(c, r, floor)
        e = lump("ember_" + name, (x, y, floor + 0.15), radii, ember_mat(index, glow), 2.7 + c * 0.1, 0.25, 2)
        k.smooth(e, 70)
        parts.append(e)
    # a scrap of the rail and charred shards on the sand
    parts.append(bent_bar("rail_scrap", [(x, y, 0.32, rr) for x, y, rr in RAIL_SCRAP], 0.4, m["rail_burnt"]))
    for i, (x, y, size, heading, key) in enumerate(TANK_SHARDS):
        obj = rock("tank_shard%d" % i, (x, y, 0.0), (size, size * 0.7, size * 0.45), m[key], 21.0 + 1.9 * i)
        obj.data.transform(Matrix.Translation((x, y, 0)) @ Matrix.Rotation(math.radians(heading), 4, "Z") @
                           Matrix.Translation((-x, -y, 0)))
        parts.append(obj)
    return parts


# --- Build -----------------------------------------------------------------------------------------------------------

def build():
    options = k.args()
    only = options["only"].split(",") if "only" in options else None
    sheets = options.get("check")
    for key, builder, materials, burnt, field, cap in (
            ("roller", roller_wreck, roller_materials, roller_burnt, roller_field, "char"),
            ("tank", tank_wreck, tank_materials, None, None, "char")):
        if only and not any(n in only for n, *_ in WRECK_PIECES[key]):
            continue
        k.reset()
        bpy.context.scene.view_settings.view_transform = "Standard"
        m = materials()
        whole = builder(m)
        for obj in whole:
            mk.apply(obj)
        if burnt is not None:
            remap = burnt(m)
            for obj in whole:
                scorch_map(obj, field, remap, levels=(ROLLER_CHAR,),
                           step=1.0 if obj.name.startswith("wheel") else None)
        for obj in whole:
            k.recalc_normals(obj)
        bpy.context.view_layer.update()
        print("%s wreck: %d triangles, %d objects" % (key, mk.triangles(whole), len(whole)))
        if "whole" in options:
            mk.export(whole, options["whole"] + "miners_%s_wreck.glb" % key)
            mk.preview(options["whole"] + "miners_%s_wreck" % key, whole, size=(48, 28), scale=12, distance=1.2)
        live.export_pieces(whole, WRECK_PIECES[key], m[cap], options, sheets)


if __name__ == "__main__":
    build()
