"""The slot of IXMUCANE's and SAWBLADES' rock wall burnt out (sheet 8 sprites 163 above 201 above 239: the slot
column's pieces, enemies 109-111, switch to them when hit hard: 277 -> 163, 203 -> 201, 241 -> 239, dlevel 30; the
wall's pieces share a link, so the whole slot switches together), polished (2026-10-21; it replaces wave3_ap_ixm.py,
which damaged wave3_y_wall.py's old slot). models.cfg (the model and sprite lines stay): sprite 8 163
ixm_wall_slot_top_damaged yaw=0 glow=12:0.15:120:-1:18.6, sprite 8 201 ixm_wall_slot_mid_damaged yaw=0, sprite 8 239
ixm_wall_slot_low_damaged yaw=0. No other enemy shows these sprites, and none of them is another sprite's pixels
mirrored, turned or in other ramps.

As the sprites draw it (the column's columns and rows, as polish_ixm_wall_slot.py's): the machine burnt black, the red
of its plating gone but for glowing cracks running through it (reds and oranges of ramp 7: across its back, round the
window (now dark) and down its left side, a hot patch at the right of the bar under it (rows 28-31), cracks down the
stem and across the grille on the cliff); its foot gone below row 56 (the sprite's rows 56-60 empty but for a stub at
the left); the sandstone either side pitted (black holes in the right flank, rows 10-21 and 32-38).

Built as polish_ixm_wall_slot.py's slot (the same rock pipeline with these sprites' rock pixels, ART_DMG: the holes
sink as its clefts do; the same machine, the same cuts into pieces: so the damaged pieces take exactly the intact ones'
places, whichever of them is damaged), and then burnt: the window's pane and core taken out, the foot cut off below the
cliff's row 56.5, the machine's top and front faces cut into a grid GRID wide (bisected along x, y and z; the bevels'
narrow faces left) and painted by the sprite's heat (HEAT: the cracks' shades of ramp 7 under each point, through the
upright wall's mapping of the sprites: the top's row r at y 28 - r, the cliff's row r at z 20 (70.5 - r) / 26), in
bands with smooth borders (polish_orb_red.band_split): charred black (0x70), dull embers (0x72, emission 0.08), red
(0x75, 0.2), orange (0x78, 0.35), hot (0x7b, 0.5). The rock is reduced a little more than the intact slot's
(ROCK_TARGET): the burnt machine holds more triangles.

Replaces wave3_ap_ixm.py (all of it: it exports only these three models) and wave3_ap_art.py's WALL_DMG (only
wave3_ap_ixm.py reads it); with it gone, wave3_y_wall.py's slot_machine() and SLOT_PARTS users go too (see
polish_ixm_wall_slot.py).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the whole column's top view
against the damaged sprites' top rows as the upright wall lays them out), --preview <prefix>, --only <model,...>.
"""
import math
import os
import sys
import time

import bmesh
import bpy
import numpy as np
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
import polish_ixm_wall_slot as ws  # noqa: E402
from polish_orb_red import band_split  # noqa: E402

# The damaged sprites' rock pixels (as polish_ixm_wall_slot.ART: ramp 1's shades, 0 the black holes and clefts).
ART_DMG = """
..00..............000...
.0780............07640..
08a96............6bb840.
88d85............8bba740
8dc65............8bb7624
8a638............8b97645
6642c............6777568
7315b............2366488
85038............4345579
95425............9438777
66853............237bb97
89882............124b495
99885............3008a86
88875............3000416
89965............4300657
79494............3200777
77942............4100577
77402............2000256
54200............0005525
65100............105b936
65000............53aa757
77001............6687667
87512............4564668
98852............5433179
aa973............841027b
99985............9a6349b
98b87............a696389
8a449............8a65468
8506c............5646548
879b5............8756547
85532............6654445
87425............4121225
66645............0000335
56654............0000245
35647............0000266
54648............2000897
64446............0007d88
76633............004bb88
87721............616bcc9
98516............964abb7
7613b............b957765
6408c............a942455
6319c............7741255
6327a............4652155
63279............1453055
54145............2010013
54124............6300355
55323............6642465
65442............6643595
a5420............64424a5
b5410............44413a5
95400............3430285
95400............3520185
95301............3510165
85302............3601265
75302............0601365
76302............0502265
66302............0202255
65302............0002245
55302............1023245
55302............0023235
55102............0124115
54202............0234103
54102............1334112
50001............2335212
000..............2335200
0................335510.
.................045300.
..................0500..
"""

# The machine's heat as the damaged sprites draw it (columns 5-16 of rows 0-63): ramp 7's shade (0-c), ramp 4's pinks a
# third of theirs, '-' black, '.' nothing.
HEAT = """
............
............
-..........-
-..........-
------------
----1503332-
----0836664-
--01499aba52
------012317
-----068753a
-0--0-2c7647
-00-1--8a644
-00-3--28832
-00-3--00552
02114--01341
-0--4--00041
0---43220052
1---2-----72
3---10--0-62
450-10--0073
17601---0-73
00880----051
-01a3----021
0012a-----23
301161----22
30103-----22
401220----22
401230---033
401243333233
201256444533
10125a776522
001257110002
--0026210--1
--002560---1
--00174----0
--02450-----
--0320------
--12--------
-0010-------
----10-----0
---012----00
--02220---21
-01310---320
-242----1500
053----24000
-30---120--0
02---0433210
00---0------
----0444442-
----0----0--
----012221--
------------
--------000-
---------00-
---------00-
----------0-
-0010-...-0-
-0100.....1-
-0-........-
--.........-
-..........-
-..........-
-..........-
...........-
"""
HEAT_COL0 = 5
FOOT_CUT = 56.5              # the foot is gone below the cliff's row 56.5
GRID = 0.85                  # the burnt faces are cut into a grid this fine before they are painted (the bevels' narrow
GRID_MIN_AREA = 0.3          # faces, smaller than this, are left: their corners carry the paint)
ROCK_TARGET = 3400           # the rock's triangles per piece (polish_ixm_wall_slot's 4200: the burnt machine has more)
# The heat's bands: (lowest heat, palette index, emission strength).
EMBERS = [(-99.0, 0x70, 0.0), (1.6, 0x72, 0.08), (3.6, 0x75, 0.2), (6.0, 0x78, 0.35), (8.6, 0x7b, 0.5)]


def heat_field():
    rows = HEAT.strip("\n").split("\n")
    a = np.zeros((len(rows), len(rows[0])))
    for r, line in enumerate(rows):
        for c, ch in enumerate(line):
            a[r, c] = int(ch, 16) if ch not in "-." else 0.0
    # A little soft: the cracks a pixel wide spread a little over the faces round them.
    return ws_blur(a, 0.45)


def ws_blur(a, sigma):
    r = int(math.ceil(3 * sigma))
    kern = np.exp(-0.5 * (np.arange(-r, r + 1) / sigma) ** 2)
    kern /= kern.sum()
    out = a
    for axis in (0, 1):
        pad = [(0, 0), (0, 0)]
        pad[axis] = (r, r)
        p = np.pad(out, pad, mode="edge")
        acc = np.zeros_like(out)
        for i, w in enumerate(kern):
            acc += w * (p[i:i + out.shape[0], :] if axis == 0 else p[:, i:i + out.shape[1]])
        out = acc
    return out


def heat_at(field, co):
    """The heat under a point of the machine: the top's sprite pixel (x, y) or, on the cliff's front, the face's."""
    x, y, z = co
    u = x + 12.0 - HEAT_COL0
    if y < ws.CLIFF + 0.9 and z < ws.TOP - 0.3:
        v = 70.5 - 26.0 * z / ws.HEIGHT
    else:
        v = 28.0 - y
    rows, cols = field.shape
    uu, vv = u - 0.5, v - 0.5
    c0, r0 = int(math.floor(uu)), int(math.floor(vv))
    fu, fv = uu - c0, vv - r0

    def at(r, c):
        return field[min(max(r, 0), rows - 1), min(max(c, 0), cols - 1)]
    return ((1 - fu) * (1 - fv) * at(r0, c0) + fu * (1 - fv) * at(r0, c0 + 1) + (1 - fu) * fv * at(r0 + 1, c0) +
            fu * fv * at(r0 + 1, c0 + 1))


def grid_cut(obj):
    """Cuts the faces that face up or down the screen's front (the top and the cliff's front) into a GRID-wide grid."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    lo, hi = Vector(obj.bound_box[0]), Vector(obj.bound_box[6])
    for axis in range(3):
        n = Vector((1.0 if axis == 0 else 0.0, 1.0 if axis == 1 else 0.0, 1.0 if axis == 2 else 0.0))
        start = math.floor(lo[axis] / GRID) * GRID
        steps = int(math.ceil((hi[axis] - start) / GRID)) + 1
        for i in range(1, steps):
            value = start + i * GRID
            faces = [f for f in bm.faces if f.calc_area() > GRID_MIN_AREA and
                     ((f.normal.z > 0.7 and axis != 2) or (f.normal.y < -0.7 and axis != 1))]
            faces = [f for f in faces if min(v.co[axis] for v in f.verts) < value < max(v.co[axis] for v in f.verts)]
            if not faces:
                continue
            edges = list({e for f in faces for e in f.edges})
            verts = list({v for f in faces for v in f.verts})
            bmesh.ops.bisect_plane(bm, geom=verts + edges + faces, dist=1e-5, plane_co=n * value, plane_no=n)
            bm.normal_update()
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    return obj


def burn(parts, m, field):
    """The machine burnt: its parts cut into the grid and painted by the heat in bands (charred to hot)."""
    for obj in parts:
        grid_cut(obj)
        values = [heat_at(field, v.co) for v in obj.data.vertices]
        band_split(obj, values, [(lowest, m["ember"][index]) for lowest, index, _ in EMBERS])
        mk.shade(obj, 35)


def damaged_machine(m):
    """polish_ixm_wall_slot's machine without its window's pane and core, its foot cut off below FOOT_CUT."""
    parts = ws.machine(m)
    keep = []
    for obj in parts:
        if obj.name.startswith(("pane", "core")):
            bpy.data.objects.remove(obj)
            continue
        if obj.name.startswith("foot"):
            cut = mk.box("foot_cut", -20.0, 20.0, -30.0, 30.0, ws.CR(FOOT_CUT), 40.0)
            mk.boolean(obj, cut, "INTERSECT")
        keep.append(obj)
    return keep


def materials():
    m = ws.materials()
    pal = k.level_palette()
    m["ember"] = {index: k.material(f"slot_ember_{index:02x}", palette=index, metallic=0.0 if glow == 0 else 0.1,
                                    roughness=0.85 if glow == 0 else 0.5, emission=pal[index] if glow > 0 else None,
                                    emission_strength=glow) for _, index, glow in EMBERS}
    m["dark"] = m["ember"][0x70]
    return m


def top_mask(sheet):
    full = k.sprite_mask(sheet, 163) + k.sprite_mask(sheet, 201) + k.sprite_mask(sheet, 239)
    rows = [[False] * 24 for _ in range(84)]
    for r in range(45):
        rows[14 + r] = list(full[r])
    for row in range(84):
        yc = 42.0 - (row + 0.5)
        if not ws.CLIFF - 2.5 <= yc <= ws.rw.BACK[0] + ws.rw.BACK[1]:
            rows[row] = [False] * 24
    return rows


def build():
    options = k.args()
    k.reset()
    bpy.context.scene.view_settings.view_transform = "Standard"
    m = materials()
    t0 = time.time()
    rock = ws.prepare(m, ART_DMG)
    coarse = rock[0]
    parts = damaged_machine(m)
    burn(parts, m, heat_field())
    print("whole: rock %d triangles, machine %d (%.1f s)" % (len(coarse.data.polygons), mk.triangles(parts),
                                                            time.time() - t0))
    if "check" in options:
        mk.compare("whole damaged slot column (8 163 above 201 above 239, the top's pixels as the upright wall lays "
                   "them out)", mk.coverage([coarse] + parts, 24, 84),
                   top_mask(os.path.join(options["check"], "enemy_8.png")))
    if "preview" in options:
        mk.preview(options["preview"] + "ixm_wall_slot_damaged_whole", [coarse] + parts, size=(24, 84), scale=8,
                   distance=2.0)
    pieces = [(name, (dmg,), keep, centre) for (name, _, keep, centre), dmg in zip(ws.PIECES, (163, 201, 239))]
    ws.export_pieces(options, m, rock, parts, pieces, suffix="_damaged", target=ROCK_TARGET)


if __name__ == "__main__":
    build()
