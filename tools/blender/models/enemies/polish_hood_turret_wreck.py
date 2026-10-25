"""The wreck of TYRIAN's hooded turret in the rocks (sheet 2 sprite 153's stand-in: what TYRIAN's background 3 map
ad33fadb8ad32f83 paints where hood_turret rides, before it comes and once it is destroyed; 14 places, all the same
painting), built on polish_hood_turret.py (2026-10-25, the clean ground's stage 5: the top enemies riding background 3).

As the map paints it (its HD tiles at 4x; sprite-centred coordinates, +y up the screen): the turret blown out of the
rocks, a crater where it sat: a black hole (x -9..8, y -4..8) full of red molten lumps (0x70-0x75 round dark reds
0x40-0x43, the band's and the eye's remains), its rim the broken cobbles; across its top a bent light-grey bar
(0x0c-0x0e: the hood's ridge, x -8..1 at y 9-10); round it the claws' torn pieces, bronze with pink lit tops (0x18-0x1c,
0xa3-0xa7, 0x4d-0x4f): a heap along the top (x -8..5, y 11-14), a piece on the left rim (x -11..-9, y 1-7) with a
white-hot spark, one on the right rim (x 6..9, y 1-5), the chin's broken block at the bottom (x -4..1, y -4..-9), a
grey plate of the hood at the lower right (x 5..9, y -1..-5). The hood, the band, the cheeks and the black boulders are
gone. (The coordinates are read at the first place, 660, 9619; at the others the painting lies 0-2 pixels lower, the
riders' logged places jittering: the model is moved PAINT_DY down, to the middle of that.)

The model: the live pit's dark plate (polish_hood_turret.pit's material and skirt) cut to the crater's jagged outline,
a low lip of shattered rock round it (a ring of faces rising from the floor to a noisy crest and down below the plane,
soot inside, dark grey outside), the molten lumps (polish_jaw_gun_wreck.ember: a dark-red rim round a hotter core,
0x72 at 0.22 and 0x75 at 0.38) and charred dark-red chunks of the band in it; the live claws' tips (polish_hood_turret's
claw paths, their bronze from the same split) cut off and thrown onto the rims, the bent ridge a bar of the ridge's
light grey, the chin a broken block, bronze and tan rubble along the top, a grey shard of the hood. Lower than the live
turret (its crest 2.2 over the plane, the live hood's 9.6).

The same frame as hood_turret: 1 unit = 1 game pixel, origin at the sprite's centre (pixel 12, 14), +X right, +Y up
the screen, +Z up from background 3's plane (z = 0; the sprite line's height=-6 sets it there); origin flag as the live
model's line. models.cfg: model hood_turret_wreck enemies/hood_turret_wreck.glb origin; wreck 2 153 hood_turret_wreck
(drawn with sprite 2 153's options: yaw=0 height=-6; its glow= option is not drawn for stand-ins).

Options after "--": --outdir <dir> (default assets/models/enemies), --preview <prefix>.
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
from polish_orb_red import band_split  # noqa: E402
import polish_hood_turret as live  # noqa: E402
import polish_panel_pills_wreck as wk  # noqa: E402
from polish_jaw_gun_wreck import ember, ember_material, jagged, ccw, bent_bar, rock, shard  # noqa: E402

# The painting lies at the 14 places 0 to 2 pixels lower than at the first (660, 9619), where these measures are read:
# the wreck is moved down by the middle of that.
PAINT_DY = -1.0
# The crater: its outline (before roughening), the floor's height, the lip: its rings out from the hole's edge
# (offset, height), the crest's noise.
CRATER = [(-4.5, 8.2), (-1.0, 8.5), (3.0, 8.1), (5.4, 6.8), (6.6, 4.0), (7.0, 1.4), (8.2, 0.2), (6.8, -1.3),
          (4.0, -2.5), (1.0, -3.4), (-2.0, -3.9), (-5.0, -3.6), (-7.0, -2.0), (-8.2, 0.0), (-9.2, 1.6), (-8.7, 4.0),
          (-7.7, 6.2), (-6.4, 7.5)]
CRATER_SEED, CRATER_JAG = 4.3, 0.4
FLOOR_Z = 0.25
LIP = [(0.0, FLOOR_Z), (0.25, 0.85), (0.6, 1.15), (1.0, 0.75), (1.5, 0.2), (2.0, -0.35)]
LIP_NOISE = 0.45
# The molten lumps (centre, radii, rim glow, core glow) and the charred chunks of the band (centre, radii).
EMBERS = [((-4.6, 3.9, 0.25), (2.0, 1.6, 0.7), "dim", "hot"), ((-1.4, 5.4, 0.25), (1.8, 1.4, 0.65), "dim", "hot"),
          ((1.7, 4.8, 0.25), (1.9, 1.5, 0.7), "dim", "hot"), ((4.3, 2.9, 0.25), (1.5, 1.5, 0.6), "dim", "hot"),
          ((-5.4, 0.6, 0.25), (1.6, 1.4, 0.6), "dim", "hot"), ((-2.1, 1.8, 0.25), (1.9, 1.5, 0.7), "dim", "hot"),
          ((1.3, 1.6, 0.25), (1.9, 1.5, 0.7), "dim", "hot"), ((3.9, -0.1, 0.25), (1.5, 1.3, 0.55), "dim", "hot"),
          ((-3.5, -1.9, 0.25), (1.6, 1.3, 0.55), "dim", "hot"), ((0.0, -1.5, 0.25), (1.6, 1.3, 0.55), "dim", "hot"),
          ((-0.3, 3.4, 0.2), (1.2, 1.0, 0.5), "dim", "dim"), ((3.1, 2.3, 0.2), (1.1, 1.0, 0.45), "dim", "dim"),
          ((-3.6, 0.2, 0.2), (1.1, 0.9, 0.45), "dim", "dim"), ((-6.6, 3.0, 0.2), (1.1, 1.2, 0.5), "dim", "dim"),
          ((2.4, -1.2, 0.2), (1.0, 0.8, 0.4), "dim", "dim")]
GLOWS = {"dim": (0x73, 0.25), "hot": (0x75, 0.4)}
CHUNKS = [((-7.2, 2.6, 0.3), (1.1, 1.0, 0.6)), ((-0.4, 3.4, 0.3), (0.8, 0.7, 0.55)), ((5.6, 1.4, 0.3), (0.9, 0.9, 0.5)),
          ((-1.8, -0.2, 0.3), (0.8, 0.7, 0.5)), ((-6.4, 5.8, 0.3), (1.0, 0.8, 0.5)), ((3.2, 6.6, 0.3), (1.0, 0.8, 0.5))]
# Broken cobbles heaved up on the lip (centre, radii, material).
COBBLES = [((-9.9, 5.4, 0.1), (2.0, 1.7, 1.1), "grey"), ((-7.4, 8.8, 0.1), (1.9, 1.3, 1.0), "rock"),
           ((5.4, 8.8, 0.1), (2.1, 1.4, 1.05), "grey"), ((8.0, 6.6, 0.1), (1.6, 1.7, 1.0), "rock"),
           ((9.6, -1.6, 0.1), (1.7, 1.6, 0.9), "grey"), ((-10.2, -1.0, 0.1), (1.6, 1.8, 0.95), "rock"),
           ((-7.2, -4.6, 0.1), (2.0, 1.4, 0.9), "grey"), ((4.0, -4.6, 0.1), (2.0, 1.3, 0.85), "rock"),
           ((-11.0, 2.4, 0.1), (1.3, 1.6, 0.8), "grey"), ((2.4, 9.8, 0.1), (1.6, 1.0, 0.8), "rock"),
           ((7.2, -4.2, 0.1), (1.4, 1.2, 0.8), "grey"), ((-4.6, -5.6, 0.1), (1.4, 1.0, 0.7), "rock"),
           ((10.0, 3.0, 0.1), (1.2, 1.5, 0.8), "grey"), ((-1.0, 9.6, 0.1), (1.2, 0.9, 0.7), "grey")]
# The bent ridge across the crater's top (x, y, z), its radius.
RIDGE = [(-8.8, 8.7, 0.7), (-6.8, 9.5, 1.45), (-4.2, 9.5, 1.55), (-1.8, 9.95, 1.2), (0.6, 10.6, 0.6)]
RIDGE_R = 0.5
# The claws' tips thrown onto the rims: which claw (0 left, 1 right), where its tip's root lands (x, y), its heading
# (degrees: the tip's direction in plan), its tilt up (degrees), and how much of the claw (from this share of its
# length).
TIPS = [(0, (-10.0, 6.8), -96.0, 6.0, 0.45), (1, (7.7, 5.0), -80.0, 5.0, 0.45), (0, (-1.6, -4.3), -60.0, 4.0, 0.55)]
TIP_SQUASH = 0.42               # (crushed flat: the live claws' sections are 4 across)
# The rubble along the top and round the rims (centre, radii, material).
RUBBLE = [((-6.6, 12.0, 0.2), (2.0, 1.5, 1.0), "bronze"), ((-3.8, 12.7, 0.2), (1.8, 1.3, 0.95), "tan"),
          ((-1.0, 12.2, 0.2), (1.6, 1.3, 0.85), "tan_dark"), ((1.8, 12.4, 0.2), (1.9, 1.4, 0.95), "bronze"),
          ((4.4, 11.6, 0.1), (1.4, 1.2, 0.7), "tan"), ((-9.4, 1.8, 0.1), (1.1, 1.2, 0.75), "tan_dark"),
          ((8.4, 1.9, 0.1), (1.0, 1.1, 0.65), "tan"), ((-2.6, -8.0, 0.0), (1.8, 1.3, 0.7), "tan_dark"),
          ((0.6, -7.4, 0.0), (1.2, 1.0, 0.55), "tan"), ((-5.0, 10.8, 0.1), (1.0, 0.8, 0.6), "pink"),
          ((0.4, 11.2, 0.1), (0.9, 0.7, 0.55), "grey")]
# The chin's broken block at the crater's lower edge: x0, x1, y0, y1, height, its tilt about x and y (degrees).
CHIN = (-4.3, 1.1, -6.6, -4.0, 1.5, (14.0, -8.0))
# The hood's grey plate at the lower right: outline, z, thickness, tilt.
PLATE = ([(4.6, -1.3), (8.5, -0.7), (8.9, -3.5), (5.6, -4.6)], 0.35, 0.45, (10.0, -14.0))
SPARK = ((-10.3, 4.8, 1.35), (0.42, 0.38, 0.3))


def materials():
    m = live.materials(live.FRAMES[0][2])
    m["soot"] = k.material("hoodwreck_soot", palette=0x10, metallic=0.1, roughness=0.9)
    m["rock"] = k.material("hoodwreck_rock", palette=0x05, metallic=0.1, roughness=0.75)
    m["burnt"] = k.material("hoodwreck_burnt_red", palette=0x41, metallic=0.2, roughness=0.7)
    m["bronze"] = k.material("hoodwreck_bronze", palette=0x19, metallic=0.6, roughness=0.35)
    m["tan"] = k.material("hoodwreck_tan", palette=0xa6, metallic=0.3, roughness=0.5)
    m["tan_dark"] = k.material("hoodwreck_tan_dark", palette=0xa4, metallic=0.3, roughness=0.55)
    m["pink"] = k.material("hoodwreck_pink", palette=0x4d, metallic=0.3, roughness=0.35)
    m["grey"] = k.material("hoodwreck_cobble", palette=0x07, metallic=0.1, roughness=0.6)
    for key, (index, strength) in GLOWS.items():
        m[key] = ember_material(index, strength)
    m["bronze_dark"] = k.material("hood_bronze", palette=0x16, metallic=0.7, roughness=0.3)
    return m


def crater_outline():
    return ccw(jagged(CRATER, CRATER_SEED, CRATER_JAG, 0.6))


def floor(m, outline):
    """The crater's floor: the live pit's dark plate, cut to the crater's outline, its skirt going down."""
    plate = mk.prism("crater_floor", outline, -live.SKIRT, FLOOR_Z, m["pit"])
    mk.shade(plate, 35)
    return plate


def lip(m, outline):
    """The crater's lip: rings of faces out from the outline (LIP: offset, height), the crest wandering by noise;
    soot inside the crest, the rock's dark grey outside it."""
    n = len(outline)
    pts = [Vector(p) for p in outline]
    normals = []
    for i in range(n):
        d = pts[(i + 1) % n] - pts[i - 1]
        normals.append(Vector((d.y, -d.x)).normalized())   # (outward for a counter-clockwise outline)
    rows = []
    for j, (off, z) in enumerate(LIP):
        row = []
        for i in range(n):
            p = pts[i] + normals[i] * off * (1.0 + 0.25 * wk.perlin(pts[i].x * 0.4, pts[i].y * 0.4, 2.0))
            dz = 0.0
            if 0 < j < len(LIP) - 1:
                dz = LIP_NOISE * wk.fbm(p.x * 0.45 + 7.0, p.y * 0.45 - 3.0, 0.5 * j, 2)
            row.append((p.x, p.y, z + dz))
        rows.append(row)
    verts = [v for row in rows for v in row]
    faces = []
    for j in range(len(rows) - 1):
        for i in range(n):
            a, b = j * n + i, j * n + (i + 1) % n
            faces.append((a, b, b + n, a + n))
    obj = k.mesh_object("crater_lip", verts, faces, m["pit"])
    obj.data.materials.append(m["soot"])
    obj.data.materials.append(m["rock"])
    for poly in obj.data.polygons:
        ring = min(poly.vertices) // n
        poly.material_index = 0 if ring <= 1 else 1 if ring <= 3 else 2
    k.recalc_normals(obj)
    for poly in obj.data.polygons:   # (all facing up and out of the hole)
        if poly.normal.z < 0:
            poly.flip()
    mk.shade(obj, 50)
    return obj


def claw_tips(m):
    """The live claws' tips, cut off at a share of their length and thrown onto the rims: each turned to its heading
    and tilted, its root on the ground."""
    out = []
    for i, (which, at, heading, tilt, share) in enumerate(TIPS):
        path = live.CLAWS[which]
        bar = mk.smooth_tube(f"claw_tip{i}", path, m["band"], 14)
        ys = [p[1] for p in path]
        tip_y = ys[0] + (ys[-1] - ys[0]) * live.CLAW_TIP_FROM
        values = [(tip_y - v.co.y) * 10.0 if v.co.y < tip_y else min(0.0, 0.5 - v.normal.z) for v in bar.data.vertices]
        band_split(bar, values, [(-9.0, m["pink"]), (-0.32, m["burnt"]), (0.0, m["bronze"])])
        mk.apply(bar)
        # Cut where the tip begins: what lies above (towards the claw's root) is gone.
        cut_y = ys[0] + (ys[-1] - ys[0]) * share
        gone = wk.split_piece(bar, (0.0, cut_y, 0.0), (0.0, 1.0, 0.0), m["burnt"], f"claw_gone{i}")
        if gone is not None:
            bpy.data.objects.remove(gone)
        # Its root to the origin, turned so that it points along the heading, tilted up, then moved to its place.
        root = Vector((path[0][0] + (path[-1][0] - path[0][0]) * share, cut_y, 0.0))
        direction = Vector((path[-1][0] - root.x, path[-1][1] - root.y, 0.0))
        spin = heading - math.degrees(math.atan2(direction.y, direction.x))
        bar.data.transform(Matrix.Scale(TIP_SQUASH, 4, (0.0, 0.0, 1.0)))
        low = min(v.co.z for v in bar.data.vertices)
        bar.data.transform(Matrix.Translation((at[0], at[1], -low + 0.05)) @
                           Matrix.Rotation(math.radians(spin), 4, "Z") @ Matrix.Translation(-root))
        h = math.radians(heading)
        wk.turn([bar], (at[0], at[1], 0.0), (-math.sin(h), math.cos(h), 0.0), -tilt)
        k.smooth(bar, 60)
        out.append(bar)
    return out


def chin(m):
    x0, x1, y0, y1, h, tilt = CHIN
    block = mk.box("chin_block", x0, x1, y0, y1, -0.5, h, m["tan_dark"])
    mk.bevel(block, 0.45, 2, 30)
    mk.shade(block, 35)
    mk.paint(block, lambda c, n: m["pink"] if n.z > 0.5 and c.y > (y0 + y1) / 2 else None)
    c = Vector(((x0 + x1) / 2, (y0 + y1) / 2, 0.0))
    block.data.transform(Matrix.Translation(c) @ Matrix.Rotation(math.radians(tilt[0]), 4, "X") @
                         Matrix.Rotation(math.radians(tilt[1]), 4, "Y") @ Matrix.Translation(-c))
    return block


def char(obj, field, darker, by_name, m, levels=(0.42, 0.9)):
    """Burns an object face by face: each face's material taken one step darker (darker: material key -> key) for
    every level the field passes at its middle."""
    for poly in obj.data.polygons:
        value = field(poly.center)
        steps = sum(1 for t in levels if value > t)
        mat = obj.data.materials[poly.material_index]
        key = by_name.get(mat.name)
        for _ in range(steps):
            key = darker.get(key, key)
        if key is not None and m[key] is not mat:
            poly.material_index = mk.slot_of(obj, m[key])


def build():
    options = k.args()
    k.reset()
    m = materials()
    outline = crater_outline()
    floor(m, outline)
    lip(m, outline)
    for i, (centre, radii, rim, core) in enumerate(EMBERS):
        ember(f"molten{i}", centre, radii, (m[rim], m[core]), 21.0 + 1.7 * i)
    for i, (centre, radii) in enumerate(CHUNKS):
        rock(f"band_chunk{i}", centre, radii, m["burnt" if i % 2 == 0 else "soot"], 31.0 + i, flat=0.0)
    for i, (centre, radii, key) in enumerate(COBBLES):
        rock(f"cobble{i}", centre, radii, m[key], 61.0 + 1.9 * i, flat=0.0)
    bent_bar("ridge_bar", RIDGE, RIDGE_R, m["ridge"], 10)
    claw_tips(m)
    chin(m)
    for i, (centre, radii, key) in enumerate(RUBBLE):
        rock(f"rubble{i}", centre, radii, m[key], 41.0 + 1.3 * i, flat=0.0)
    outline_p, z, thick, tilt = PLATE
    shard("hood_plate", outline_p, z, thick, m["hood_lit"], tilt)
    ember("spark", SPARK[0], SPARK[1], (m["dim"], m["hot"]), 57.0)
    parts = mk.meshes()
    for obj in parts:
        mk.apply(obj)
    # The rubble and the bronze near the crater burnt darker (the crater's heat).
    centre = Vector((-0.8, 2.2, 0.0))

    def heat(co):
        d = Vector(((co.x - centre.x) / 9.0, (co.y - centre.y) / 7.5, 0.0)).length
        return 0.75 * math.exp(-2.0 * max(0.0, d - 0.55) ** 2) - 0.2 + 0.2 * wk.perlin(co.x * 0.6, co.y * 0.6, 1.3)
    darker = {"tan": "tan_dark", "tan_dark": "soot", "bronze": "bronze_dark", "bronze_dark": "soot",
              "pink": "burnt", "burnt": "soot", "grey": "rock", "rock": "soot"}
    by_name = {mat.name: key for key, mat in m.items()}
    for obj in parts:
        if obj.name.startswith(("rubble", "claw_tip", "chin_block")):
            char(obj, heat, darker, by_name, m)
        elif obj.name.startswith("cobble"):   # (the heaved cobbles sooted on their crater side only)
            char(obj, lambda co: heat(co) - 0.25, darker, by_name, m, levels=(0.42,))
    mk.transform(mk.meshes(), Matrix.Translation((0.0, PAINT_DY, 0.0)))
    wk.clip_below(mk.meshes(), -live.SKIRT)
    wk.finish("hood_turret_wreck", options)


if __name__ == "__main__":
    build()
