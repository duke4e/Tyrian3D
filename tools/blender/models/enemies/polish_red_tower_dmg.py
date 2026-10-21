"""DELI's and New Deli's tall red tower damaged (sheet C 91 above 129 above 93 above 131: the dgr sprites of 77, 115, 17
and 55, enemies 240, 239, 238 and 237; dlevel -1: when any piece of a linked tower is destroyed, all four switch to
these together and stay as its wreck; VAULT's lone base, link 0, just explodes), polished (2026-10-21; it replaces
wave3_ao_deli.py's tower_damaged_whole() and tower_damaged_piece(): wave3_x_tower.py's old tower with its head cut off,
a lathed black cone on it and holes pressed in pixel by pixel). models.cfg: model red_tower_dmg_head / _vents / _shaft
/ _base ... origin (unchanged); sprite c 91 red_tower_dmg_head yaw=0 height=-4 and the same for 129, 93 and 131.

The tower is polish_red_tower.py's (its builders imported, unchanged), built whole and upright, damaged as the
damaged sprites draw it (pixel diffs of 91 / 129 / 93 / 131 against 77 / 115 / 17 / 55; they have no upscale:
modelled from the enlarged originals), then leaned, cut under the floor and into the same pieces at the same origins
as the intact tower, so that any damaged piece meets any intact one: the bodies across the pieces' cuts (the shaft at
row 56, the base at row 84) do not move within FADE of them and keep their cut faces (checked in the game-camera view
with mixed pieces). No sprite of any sheet is these mirrored, turned or in other ramps.

What the damaged sprites draw differently:
- 91: the head blown off: of the dome, the skirt and the cup only a hollow stump of the neck is left, standing in the
  crown, black, its sides lit (columns 8 and 16), its torn top ragged (rows 21-24, highest over its front right), a
  shard of its wall standing up as a thin spike (columns 12-14 of rows 16-20);
- 129: the crown's top rim burnt black and broken (rows 0-4); the vents dead (their 115 dark red, unlit); holes blown
  into the upper bulb's left (columns 4-9 of rows 17-24) and right (columns 16-19 of rows 17-22), debris lit at their
  edges;
- 93: a bite out of the shaft's top left (its outline gone at columns 5-7 of rows 1-4) and a crack below it, the
  same holes in the lower bulb (rows 13-20), a hole in the base's top (columns 10-14 of rows 22-27);
- 131: a crack down the base's top left (columns 9-10 of rows 0-3) and one across the hatch (columns 12-17 of rows
  6-12).
How: the stump is a hollow shell (polish_red_tower.patch) round a ragged top edge with the spike in it, char black
(0x01, rough) mottled with 0x03 outside and char inside, its sides 0x08 / 0x05, its torn edge bare 0x09; the crown's
rim crumpled in by noise and painted char with grey shards (0x08); the vents' ember material swapped for its dark red
(0x43); holes and cracks are fields in the picture's coordinates (the camera sees the upright front face on: x and the
row): the faces the camera sees in them are cut finer once, their points pressed in along their normals (1.3 pixels
in the bulbs' holes, a bite of 2.3, the cracks 0.4); then all those faces are cut along the paint's contours
(polish_machine_kit.split_along) and painted char in the holes and cracks, scorched (0x03) round them and sooted round
them and in streaks running down the shaft and the bulbs (every grey two shades darker: 0x0a to 0x08, 0x09 to 0x07,
0x08 to 0x05; the reds to 0x46 and 0x43).

Coordinates as in polish_red_tower.py (the upright frame: x right, y back, z up the axis; the picture's row r at the
height H(r)).

Replaces wave3_ao_deli.py: delete it (only the tower's damaged look is left in it since round 19: deli_painter(),
holes_of(), TOWER, T_INT, T_DMG, tower_damaged_whole() with its x.whole("tower_damaged", ...) registration,
tower_damaged_piece() and the model loop; nothing imports it); and wave3_ao_art.py's TOWER_DMG with its comment (only
T_DMG reads it). wave3_ao_kit.py stays (wave3_ao_works.py and wave3_ar_kit.py import it).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the whole's and each piece's
silhouette as the game's camera sees it against the damaged sprites in enemy_C.png, the floor left out), --preview
<prefix>, --only <name,...>, --whole <file.glb> (the leaned uncut damaged tower), --stats 1.
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Vector, noise

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_red_tower as rt  # noqa: E402
from polish_red_tower import mk, k, H, ROW  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402

C20 = rt.C20

# The damaged pieces: the intact piece they replace, model, damaged sprite.
PIECES = [("red_tower_head", "red_tower_dmg_head", 91), ("red_tower_vents", "red_tower_dmg_vents", 129),
          ("red_tower_shaft", "red_tower_dmg_shaft", 93), ("red_tower_base", "red_tower_dmg_base", 131)]
CUT_ROWS = (56.0, 84.0)                       # where the pieces meet across a body: nothing moves within FADE of them
FADE = (1.0, 1.8)

# --- The damage, in the picture's coordinates (x, row) ----------------------------------------------------------------
# Holes blown into the bulbs and the shaft: centre, radii, how deep (pressed in), how ragged.
PITS = [((-5.5, 48.6), (2.6, 2.9), 1.3, 0.35),     # the upper bulb's left (C 129 rows 18-24)
        ((4.9, 48.0), (1.3, 2.3), 0.9, 0.3),       # its right (columns 16-17)
        ((-6.5, 58.7), (2.3, 2.1), 2.3, 0.3),      # the bite out of the shaft's top left (C 93 rows 1-4)
        ((-5.5, 71.6), (2.6, 2.9), 1.3, 0.35),     # the lower bulb's left (C 93 rows 13-19)
        ((4.9, 71.5), (1.3, 2.2), 0.9, 0.3),       # its right
        ((1.3, 80.9), (2.1, 2.4), 1.1, 0.3)]       # the base's top (C 93 rows 22-27)
# Cracks: polylines, half-width, depth.
CRACKS = [([(-4.4, 56.9), (-3.9, 58.2), (-4.2, 59.6), (-3.6, 61.0)], 0.32, 0.35),   # down from the bite
          ([(-1.5, 85.2), (-1.9, 86.3), (-1.6, 87.8)], 0.35, 0.4),                  # the base's top left (C 131)
          ([(0.6, 90.2), (1.9, 91.4), (2.6, 92.6), (3.9, 94.0), (4.6, 95.6)], 0.35, 0.4)]   # across the hatch
SOOT = 1.6                                    # soot round each hole and crack: this much wider
# Soot streaks run down the shaft and the bulbs from the holes and the blast (painted only): polylines, half-width.
STREAKS = [([(-3.3, 56.4), (-3.7, 60.2), (-3.1, 64.6)], 1.05), ([(2.7, 56.8), (3.0, 61.6)], 0.7),
           ([(-5.8, 50.8), (-6.0, 53.9)], 0.95), ([(-5.6, 73.8), (-5.3, 76.9)], 0.95),
           ([(4.8, 50.2), (4.6, 53.0)], 0.6),
           ([(4.8, 73.6), (4.6, 76.4)], 0.6), ([(1.3, 82.9), (1.7, 83.7)], 0.8)]
CHAR_AT, SCORCH_AT, SOOT_AT = 0.3, 0.1, 0.32   # the paint's contours: char black, scorched, sooted
# The crown's top rim burnt and broken (C 129 rows 0-4): rows, how far it crumples in, how ragged.
RIM = (27.9, 31.2, 0.75)
# The stump of the head (C 91 rows 16-27): a hollow tube torn off over the crown, a shard of its wall bent up.
STUMP = (5.4, 4.6, 28.9, 0.4)                # outer and inner radius, its foot (in the crown's opening), x of its axis
SPIKE = (math.asin(1.1 / 5.4), 0.2, 16.3)     # its angle from the front, half-width (radians), the row of its tip
SEED = 91


def materials():
    m = rt.materials()
    m["char"] = k.material("rtowd_char", palette=0x01, metallic=0.1, roughness=0.85)
    return m


# What each material becomes under soot: every shade two darker (no new shade brought in).
SOOT_OF = {"rtow_greyc@12": "ga", "rtow_greya@10": "g8", "rtow_grey9@9": "g7", "rtow_grey8@8": "g5",
           "rtow_grey7@7": "g5", "rtow_grey5@5": "g3", "rtow_red9@73": "r6", "rtow_red7@71": "r3",
           "rtow_red6@70": "r3"}


def smoothstep(e0, e1, x):
    t = min(1.0, max(0.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


def ragged(x, row, seed, scale=1.6):
    return noise.noise(Vector((x * scale + 17.3 * seed, row * scale - 5.1 * seed, 0.37 * seed)))


def seg_distance(p, a, b):
    ab = b - a
    t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-9)))
    return (p - (a + ab * t)).length


def fields(x, row):
    """(how deep in a hole or crack 0..1 with its depth, soot 0..1) at a picture point."""
    best, depth, soot = 0.0, 0.0, 0.0
    for i, ((cx, cy), (rx, ry), d, jag) in enumerate(PITS):
        e = math.hypot((x - cx) / rx, (row - cy) / ry)
        f = 1.0 - e + jag * ragged(x, row, i + 1)
        if f > best:
            best, depth = f, d
        soot = max(soot, 1.0 - e / SOOT + 0.25 * ragged(x, row, i + 11, 0.9))
    p = Vector((x, row))
    for i, (pts, half, d) in enumerate(CRACKS):
        dist = min(seg_distance(p, Vector(a), Vector(b)) for a, b in zip(pts, pts[1:]))
        f = 1.0 - dist / half + 0.3 * ragged(x, row, i + 31, 3.0)
        if f > best:
            best, depth = f, d
        soot = max(soot, 1.0 - dist / (half * 4.0) + 0.25 * ragged(x, row, i + 41, 1.2))
    for i, (pts, half) in enumerate(STREAKS):
        dist = min(seg_distance(p, Vector(a), Vector(b)) for a, b in zip(pts, pts[1:]))
        soot = max(soot, 1.0 - dist / half + 0.35 * ragged(x, row, i + 51, 1.4))
    return best, depth, soot


def fade(row):
    """0 within FADE[0] rows of the pieces' cuts across the bodies, 1 beyond FADE[1]."""
    return min(smoothstep(FADE[0], FADE[1], abs(row - c)) for c in CUT_ROWS)


def near(x, row, margin=0.4):
    """Whether a picture point is within margin of any hole or crack (where faces are cut finer)."""
    for (cx, cy), (rx, ry), _, _ in PITS:
        if abs(x - cx) < rx * 1.2 + margin and abs(row - cy) < ry * 1.2 + margin:
            return True
    for pts, half, _ in CRACKS:
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        if min(xs) - margin < x < max(xs) + margin and min(ys) - margin < row < max(ys) + margin:
            return True
    return False


def picture(co):
    """Where the camera sees an upright point on the picture: (x, row)."""
    return co.x, ROW(co.z)


def seen(n):
    """Faces and points the camera can see (the upright front: towards -y)."""
    return n.y < 0.3


def damage(obj, m, refine=1, step=0.6):
    """Holes, cracks and soot where the damaged sprites draw them, on the parts of an object the camera sees: the faces
    in the holes cut finer and their points pressed in along their normals (none within FADE of the pieces' cuts),
    the faces cut along the paint's contours (polish_machine_kit.split_along), then painted char black in the holes,
    scorched round them, sooted (two shades darker) round them and in the streaks."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    for _ in range(refine):
        bm.faces.ensure_lookup_table()
        faces = [f for f in bm.faces if seen(f.normal) and near(*picture(f.calc_center_median()))]
        edges = {e for f in faces for e in f.edges if e.calc_length() > step}
        if not edges:
            break
        bmesh.ops.subdivide_edges(bm, edges=list(edges), cuts=1, use_grid_fill=True)
    bm.normal_update()
    for v in bm.verts:
        if not seen(v.normal):
            continue
        f, d, _ = fields(v.co.x, ROW(v.co.z))
        if f > 0.0 and d > 0.0:
            v.co -= v.normal * d * smoothstep(0.05, 0.6, f) * fade(ROW(v.co.z))
    bm.normal_update()
    seen_verts = {v for v in bm.verts if seen(v.normal)}

    def values(which):
        return {v: (fields(v.co.x, ROW(v.co.z))[which] if v in seen_verts else -1.0) for v in bm.verts}
    for which, threshold in ((2, SOOT_AT), (0, SCORCH_AT), (0, CHAR_AT)):
        vals = values(which)
        made = mk.split_along(bm, vals, threshold)
        seen_verts |= {v for v in made if v.is_valid}
    char = mk.slot_of(obj, m["char"])
    scorch = mk.slot_of(obj, m["g3"])
    names = [mat.name for mat in obj.data.materials]
    sooted = {names.index(name): mk.slot_of(obj, m[key]) for name, key in SOOT_OF.items() if name in names}
    for f in bm.faces:
        if not seen(f.normal):
            continue
        c = f.calc_center_median()
        fv, _, sv = fields(c.x, ROW(c.z))
        if fv > CHAR_AT:
            f.material_index = char
        elif fv > SCORCH_AT:
            f.material_index = scorch
        elif sv > SOOT_AT and f.material_index in sooted:
            f.material_index = sooted[f.material_index]
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    k.smooth(obj, 35)
    return obj


def break_rim(crown, m):
    """The crown's top rim burnt black and crumpled in (C 129 rows 0-4): its points there pressed in by a ragged amount,
    its faces char black but for a few grey shards."""
    r0, r1, depth = RIM
    bm = bmesh.new()
    bm.from_mesh(crown.data)
    bm.normal_update()
    for v in bm.verts:
        row = ROW(v.co.z)
        if row > r1:
            continue
        w = 1.0 - smoothstep(r1 - 1.6, r1, row)
        az = math.atan2(v.co.x, -v.co.y)
        amount = depth * w * (0.55 + 0.45 * noise.noise(Vector((az * 2.3, row * 0.9, 3.1))))
        radial = Vector((v.co.x, v.co.y, 0.0))
        if radial.length > 1e-6:
            v.co -= radial.normalized() * amount * 0.6
        v.co.z -= amount * 0.7 * C20 * w
    char = mk.slot_of(crown, m["char"])
    shard = mk.slot_of(crown, m["g8"])
    for f in bm.faces:
        c = f.calc_center_median()
        row = ROW(c.z)
        if row < r1 - 0.4 * (1.0 + noise.noise(Vector((c.x * 1.3, c.y * 1.3, 7.7)))):
            az = math.atan2(c.x, -c.y)
            f.material_index = shard if noise.noise(Vector((az * 3.1, row * 1.7, 11.0))) > 0.32 else char
    bm.to_mesh(crown.data)
    bm.free()
    crown.data.update()
    k.smooth(crown, 32)
    return crown


def kill_vents(objs, m):
    """The vents dead: their ember out (the back plates dark red)."""
    vent = m["vent"].name
    for obj in objs:
        names = [mat.name for mat in obj.data.materials]
        if vent in names:
            i = names.index(vent)
            obj.data.materials[i] = m["r3"]
    return objs


def angdiff(a, b):
    return math.atan2(math.sin(a - b), math.cos(a - b))


def stump_top(az):
    """The row of the stump's torn top at an angle from the front: highest over its front right, lower round the sides,
    ragged, the spike at SPIKE."""
    base = 21.3 + 2.9 * smoothstep(0.75, 1.5, abs(angdiff(az, 0.4)))
    jag = 0.55 * noise.noise(Vector((math.cos(az) * 2.2, math.sin(az) * 2.2, 5.3))) + \
        0.3 * noise.noise(Vector((math.cos(az) * 6.1, math.sin(az) * 6.1, 9.1)))
    a, width, tip = SPIKE
    spike = (base - tip) * math.exp(-(angdiff(az, a) / width) ** 4)
    return base + jag - spike


def stump(m):
    """The head blown off (C 91): what is left of its neck, a hollow tube standing in the crown's opening, torn off in a
    ragged edge, a shard of its wall standing up as a spike; burnt black outside, char inside, the torn edge bare
    metal."""
    r_out, r_in, foot, cx = STUMP

    def surf(u, v):
        az = -math.pi + 2 * math.pi * u
        top = stump_top(az)
        row = top + (foot - top) * v ** 0.8
        return Vector((cx + r_out * math.sin(az), -r_out * math.cos(az), H(row)))
    def outer(c, n):
        side = abs(c.x - cx) / r_out
        mottle = noise.noise(Vector((c.x * 0.9, c.y * 0.9, c.z * 0.9)))
        if side > 0.72 + 0.12 * mottle:
            return m["g8"] if n.dot(rt.LIGHT) > 0.0 else m["g5"]     # its sides lit, as C 91 draws them
        return m["char"] if mottle > -0.2 else m["g3"]
    tube = rt.patch("stump", surf, 96, 10, 0.0, r_out - r_in, (m["g5"], m["char"], m["g9"]), paint_outer=outer)
    k.smooth(tube, 40)
    return [tube]


def build_whole(m):
    """The damaged tower's parts, upright, by piece (the intact piece's name)."""
    pieces = rt.build_tower(m)
    rt.remove(pieces["red_tower_head"])
    pieces["red_tower_head"] = stump(m)
    vents = pieces["red_tower_vents"]
    for obj in vents:
        if obj.name == "crown":
            break_rim(obj, m)
    kill_vents(vents, m)
    for name in ("red_tower_vents", "red_tower_shaft", "red_tower_base"):
        for obj in pieces[name]:
            if obj.name.split(".")[0] in ("upper_bulb", "shaft_top", "shaft", "lower_bulb", "base_top", "base"):
                damage(obj, m)
    return pieces


def build():
    options = k.args()
    only = options["only"].split(",") if "only" in options else None
    want = lambda name: not only or name in only  # noqa: E731
    sheet = os.path.join(options["check"], "enemy_C.png") if "check" in options else None
    k.reset()
    m = materials()
    pieces = rt.finish(build_whole(m), m)
    masks = {s: rt.own_mask(sheet, s, base=(s == 131)) for _, _, s in PIECES} if sheet else {}
    if sheet:
        everything = [o for objs in pieces.values() for o in objs]
        mk.compare("whole damaged tower (C 91 above 129 above 93 above 131), as the game's camera sees it",
                   rt.view_coverage(everything, 112, 0.0), masks[91] + masks[129] + masks[93] + masks[131])
    if "preview" in options:
        everything = [o for objs in pieces.values() for o in objs]
        bpy.context.scene.view_settings.view_transform = "Standard"
        mk.preview(options["preview"] + "red_tower_dmg_whole", everything, size=(28, 112), scale=6, distance=2.8)
    if "whole" in options:
        everything = [o for objs in pieces.values() for o in objs]
        triangulate(everything)
        mk.export(everything, options["whole"])
    for intact, name, sprite in PIECES:
        objs = pieces.pop(intact)
        if not want(name):
            rt.remove(objs)
            continue
        yc = [p[4] for p in rt.PIECES if p[0] == intact][0]
        for rest in pieces.values():
            for o in rest:
                o.hide_render = True
        rt.export_piece(objs, name, yc, options, masks.get(sprite), "C %d" % sprite)
        for rest in pieces.values():
            for o in rest:
                o.hide_render = False


if __name__ == "__main__":
    build()
