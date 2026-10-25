"""What is left of TORM's and BONUS' grey building once it is destroyed (stage 4 of the clean ground: the wreck models
that stand in for the map's painting of it; sheet J sprites 5 and 7 above 43 and 45), built on polish_window_block.py.
models.cfg: model window_block_tl_wreck / _tr_wreck / _bl_wreck / _br_wreck ... origin; wreck j 5 window_block_tl_wreck,
wreck j 7 window_block_tr_wreck, wreck j 43 window_block_bl_wreck, wreck j 45 window_block_br_wreck. The game draws
them where the maps paint the wreck, with the live sprite lines' options (yaw=0 height=-4), at the live pieces'
places.

The painting (TORM's and BONUS' maps paint the same one; in the HD tiles and at 1x, greys of ramp 0, greens of ramp
12, dark reds of ramp 7): the bunker burnt out but standing. The tower still stands with its frame and bars, its
windows' glass broken out (a shard left at the top window's upper left and right, the middle one's lower left, the
bottom one's lower right; the light inside out); its front under the windows (rows 30-36) blown in. The wing at the
left is holed through its panel (columns 5-12 of rows 14-31), red flames licking out of it (columns 7-12 of rows
16-27). The right block's louvres are torn off (a dark hole where they lay, columns 26-31 of rows 14-30), its duct
broken in the middle, its right edge burning down its length (a red seam at columns 36-37 of rows 17-40); the vent
housing and its fins at its back are whole. The plinth's middle has gone (the hatch, the T channel, the pipe:
columns 12-27 of rows 36-44), its front lip broken there, fire at its foot (rows 44-47, columns 7-25); its left vent
and its right end stand. The painting lies where the live sprites do (no offset).

Built as the live building (polish_window_block.py's plinth, its details, the tower, the wing, the right block with
its vent housing, fins and louvres, the duct, its materials), then broken: jagged holes cut into it where the
painting shows them (lofted outlines, their walls broken armour), the parts wholly in them gone, three of the louvres
torn off, the glass broken to shards (dull green, a faint glow left), rubble of armour plate on the plinth and at its
foot, and the fires: small tongues of flame and embers in their own dark reds and oranges, emission 0.3-0.42 (under
the bloom's white), and the burning seam along the right edge.

Coordinates as polish_window_block.py's: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the foliage;
P(c, r) a pixel edge of the 48 x 56 picture (column c, row r), the whole's origin where the four sprites meet.

Options after "--": --outdir <dir> (default assets/models/enemies), --check (the whole's silhouette against the
building's own pixels), --preview <prefix>, --only <model,...>.
"""
import math
import os
import random
import sys

import bpy
from mathutils import Euler, Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
import polish_window_block as live  # noqa: E402
from polish_pyramid_wreck import cut_piece, Hole, break_with, chunk, emissive, triangulate  # noqa: E402

P, X, Y = live.P, live.X, live.Y
SEED = 43
# The holes: (name, middle (column, row), radii, power, jag, their walls [(height, scale), ...] from the floor up).
HOLES = [
    ("wing_hole", (8.7, 22.6), (3.5, 7.8), 2.3, 0.45, [(3.6, 0.8), (6.0, 0.92), (9.0, 1.0), (20.0, 1.04)]),
    ("front_hole", (19.2, 33.4), (5.6, 3.0), 2.4, 0.4, [(3.4, 0.8), (6.0, 0.95), (20.0, 1.02)]),
    ("plinth_hole", (19.6, 40.4), (8.6, 4.6), 2.6, 0.55, [(1.4, 0.78), (3.4, 0.92), (5.5, 1.0), (20.0, 1.04)]),
    ("louvre_hole", (28.5, 23.8), (2.6, 8.2), 3.0, 0.3, [(7.4, 0.82), (9.4, 0.94), (20.0, 1.04)]),
    ("duct_gap", (33.6, 25.4), (3.3, 3.6), 3.0, 0.45, [(10.0, 0.9), (11.2, 1.0), (20.0, 1.03)]),
]
LOUVRES_TORN = ("louvre0", "louvre1", "louvre2")   # gone (louvre3, at the front, hangs on)
# The glass left in each window: polygons in the window's (u, v) (0-1 across, 0-1 down from its top).
SHARDS = [
    [[(0.0, 0.0), (0.58, 0.0), (0.3, 0.18), (0.0, 0.52)], [(0.78, 0.0), (1.0, 0.0), (1.0, 0.36)]],
    [[(0.0, 0.12), (0.22, 0.4), (0.62, 0.62), (0.74, 1.0), (0.0, 1.0)]],
    [[(1.0, 0.38), (1.0, 1.0), (0.42, 1.0), (0.7, 0.72)]],
]
# The fires: (column, row, how many tongues, their height).
FIRES = [(8.4, 20.6, 4, 3.8), (10.2, 24.4, 3, 3.0), (9.4, 17.6, 2, 2.4), (7.4, 26.4, 2, 2.0), (10.6, 45.6, 3, 2.4),
         (14.6, 45.8, 3, 2.8), (19.4, 45.4, 4, 3.0), (23.8, 45.9, 3, 2.2), (36.8, 33.0, 2, 2.0), (36.9, 22.0, 2, 1.8)]
# The fires' glowing beds: (column, row, radii (columns, rows)).
BEDS = [(9.0, 21.8, (2.0, 4.6)), (17.0, 45.6, (8.0, 1.3)), (19.4, 41.0, (3.0, 1.8))]
EMBERS = [(7.4, 25.6), (11.2, 21.4), (16.4, 41.0), (21.8, 39.4), (18.6, 44.8), (26.2, 44.6), (36.4, 38.2),
          (29.0, 22.0), (28.2, 27.6), (20.2, 34.4)]
SEAM = (36.7, 16.8, 40.6)              # the burning seam down the right edge: column, rows from-to
# Rubble of armour: (column, row) spots and how many chunks round each.
RUBBLE = [(9.4, 46.0, 4), (16.0, 46.6, 4), (22.6, 46.2, 3), (27.0, 47.0, 3), (17.0, 40.0, 5), (22.4, 40.6, 5),
          (8.6, 23.0, 4), (19.0, 33.6, 5), (28.4, 21.0, 4), (28.4, 27.0, 4), (39.0, 30.0, 2), (5.2, 32.4, 2)]


def materials():
    m = live.materials()
    m["break"] = k.material("wblock_break", palette=0x04, metallic=0.35, roughness=0.6)
    m["glass"] = emissive("wblock_glass_broken", 0xc5, 0.16, 0.0, 0.3)
    m["flame"] = emissive("wblock_flame", 0x75, 0.42, 0.0, 0.5)
    m["ember"] = emissive("wblock_ember", 0x77, 0.3, 0.0, 0.5)
    return m


def carve(objects, hole, walls, mat):
    """Cuts a hole into the objects it reaches (exact booleans); objects wholly inside it above its floor go.
    Returns the objects left."""
    ring = hole.ring(0.0, max(sc for _, sc in walls))
    hx0, hx1 = min(p.x for p in ring), max(p.x for p in ring)
    hy0, hy1 = min(p.y for p in ring), max(p.y for p in ring)
    floor = walls[0][0]
    kept, reached = [], []
    for obj in objects:
        corners = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
        if (max(c.x for c in corners) < hx0 or min(c.x for c in corners) > hx1 or
                max(c.y for c in corners) < hy0 or min(c.y for c in corners) > hy1):
            kept.append(obj)
        elif max(hole.d(c.x, c.y) for c in corners) < 0.9 and min(c.z for c in corners) > floor:
            bpy.data.objects.remove(obj)
        else:
            reached.append(obj)
    cutter = hole.cutter("cutter", walls, mat, 0.4)
    for obj in break_with(reached, cutter):
        mk.shade(obj, 35)   # (flat faces kept flat, as the live parts are)
        kept.append(obj)
    return kept


def shards(m):
    """The glass left in the windows: the SHARDS polygons lying where the panes lay, dull green."""
    made = []
    for i, polys in enumerate(SHARDS):
        c0, c1, r0, r1 = live.WINDOWS[i]
        x0, x1, y0, y1 = live.box_of(c0, c1, r0, r1)
        rl, rt, rr, rb = live.REVEAL
        x0, x1, y0, y1 = x0 + rl - 0.05, x1 - rr + 0.05, y0 + rb - 0.05, y1 - rt + 0.05
        z = live.T_H - live.WIN_D + 0.06
        for j, poly in enumerate(polys):
            verts = [(x0 + (x1 - x0) * u, y1 - (y1 - y0) * v, z) for u, v in poly]
            obj = k.mesh_object(f"shard{i}_{j}", verts, [tuple(range(len(verts)))], m["glass"])
            if obj.data.polygons[0].normal.z < 0:
                obj.data.polygons[0].flip()
            made.append(obj)
    return made


def build_whole(m):
    whole = live.build_whole(m)
    panes = shards(m)
    parts = [o for o in whole if o.name not in LOUVRES_TORN]
    for obj in [o for o in whole if o.name in LOUVRES_TORN]:
        bpy.data.objects.remove(obj)
    for name, centre, radii, power, jag, walls in HOLES:
        hole = Hole(P(*centre), radii, power, SEED + len(name), jag, 0.9)
        parts = carve(parts, hole, walls, m["break"])
    bpy.context.view_layer.update()
    fires(parts + panes, m)
    whole = mk.meshes()
    for obj in whole:
        mk.apply(obj)
    bpy.context.view_layer.update()
    return whole


def fires(solid, m):
    """Rubble, the fires' tongues and embers, the burning seam down the right edge."""
    rng = random.Random(SEED)
    hit = mk.surface(solid)

    def ground(c, r):
        x, y = P(c, r)
        h = hit(x, y)
        return Vector((x, y, h[0].z if h else 0.0))
    n = 0
    for c, r, count in RUBBLE:
        for _ in range(count):
            cc, rr = c + rng.uniform(-1.8, 1.8), r + rng.uniform(-1.2, 1.2)
            mat = (m["wall"], m["rim"], m["deck"], m["dark"], m["break"], m["top"])[n % 6]
            chunk(f"rubble{n}", ground(cc, rr) - Vector((0, 0, 0.25)), rng.uniform(1.0, 2.2), rng, mat,
                  rng.uniform(0.4, 0.75), 8)
            n += 1
    n = 0
    for c, r, count, height in FIRES:
        # Low tongues of fire: glowing lumps heaped up a little, a hotter one on top.
        for _ in range(count):
            cc, rr = c + rng.uniform(-1.0, 1.0), r + rng.uniform(-0.8, 0.8)
            base = ground(cc, rr) - Vector((0, 0, 0.25))
            chunk(f"flame{n}", base, height * rng.uniform(0.45, 0.6), rng, m["flame"], 0.55, 9)
            chunk(f"flame{n}_hot", base + Vector((0, 0, height * 0.2)), height * 0.25, rng, m["ember"], 0.6, 7)
            n += 1
    for i, (c, r) in enumerate(EMBERS):
        chunk(f"ember{i}", ground(c, r) - Vector((0, 0, 0.1)), rng.uniform(0.45, 0.7), rng, m["ember"], 0.6, 8)
    for i, (c, r, (rc, rr)) in enumerate(BEDS):
        # A bed of embers: flat glowing lumps packed over an oval.
        for j in range(int(rc * rr * 1.0) + 3):
            a, t = rng.uniform(0, 2 * math.pi), math.sqrt(rng.uniform(0, 1))
            cc, rw = c + math.cos(a) * t * rc, r + math.sin(a) * t * rr
            chunk(f"bed{i}_{j}", ground(cc, rw) - Vector((0, 0, 0.2)), rng.uniform(1.0, 1.9), rng,
                  (m["flame"], m["ember"])[j % 2], 0.35, 7)
    # The seam: a glowing strip lying in the chamfer down the right block's right edge, broken in places.
    c, r0, r1 = SEAM
    x = X(c)
    y = Y(r0)
    i = 0
    while y > Y(r1):
        length = rng.uniform(1.6, 3.4)
        ya, yb = y, max(y - length, Y(r1))
        za = ground(c, 28.0 - ya).z
        zb = ground(c, 28.0 - yb).z
        verts = [(x - 0.55, ya, za + 0.18), (x + 0.5, ya, za - 0.3), (x + 0.5, yb, zb - 0.3), (x - 0.55, yb, zb + 0.18),
                 (x - 0.55, ya, za - 0.6), (x + 0.5, ya, za - 0.9), (x + 0.5, yb, zb - 0.9), (x - 0.55, yb, zb - 0.6)]
        faces = [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
        k.recalc_normals(k.mesh_object(f"seam{i}", verts, faces, m["flame"]))
        y = yb - rng.uniform(0.25, 0.7)
        i += 1


PIECES = [(name + "_wreck", sprites, box) for name, sprites, box in live.PIECES]


def build():
    options = k.args()
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    k.reset()
    m = materials()
    whole = build_whole(m)
    print("whole window block wreck: %d triangles, %d objects" % (mk.triangles(whole), len(whole)))
    bpy.context.scene.view_settings.view_transform = "Standard"
    if "check" in options:
        mk.compare("whole wreck (the building's own pixels)", mk.coverage(whole, 48, 56), live.own_mask())
    if "preview" in options:
        mk.preview(options["preview"] + "window_block_wreck_whole", whole, size=(48, 56), scale=8, distance=1.8)
    for name, sprites, box in PIECES:
        if only and name not in only:
            continue
        pieces = [p for p in (cut_piece(src, box, m["wall"]) for src in whole) if p is not None]
        mk.transform(pieces, Matrix.Translation((-(box[0] + box[1]) / 2, -(box[2] + box[3]) / 2, 0)))
        triangulate(pieces)
        bpy.context.view_layer.update()
        for src in whole:
            src.hide_render = True
        mk.report(name, pieces, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, pieces)
        for obj in pieces:
            bpy.data.objects.remove(obj)
        for src in whole:
            src.hide_render = False


if __name__ == "__main__":
    build()
