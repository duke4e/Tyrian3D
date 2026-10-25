"""What is left of the asteroid levels' grey block house once it is destroyed (stage 4 of the clean ground: the wreck
models that stand in for the map's painting of it; sheet P sprites 153 and 155 above 191 and 193), built on
polish_block_house.py. models.cfg: model block_house_tl_wreck / _tr_wreck / _bl_wreck / _br_wreck ... origin; wreck p
153 block_house_tl_wreck, wreck p 155 block_house_tr_wreck, wreck p 191 block_house_bl_wreck, wreck p 193
block_house_br_wreck (one wreck per piece: the live frame models of the hatches don't matter here). The game draws
them where the maps paint the wreck (ASTEROID2, ASTEROID?, ASTCITY, AST. CITY, AST ROCK, ASTEROID1, GREY MOON...), with
the live sprite lines' options (yaw=0 height=-4), at the live pieces' places.

The painting (the same on every map; in the HD tiles and at 1x, in the grey ramp 0 with dark reds of ramp 7): the
block blown open from inside. The roof's back strip (rows 0-6) and its right side (columns 34-42: slabs f, h and m)
still stand, the glacis' foot (rows 48-52) too; everything between is a hole full of torn armour: slabs bent and
curled up out of it (their lit edges the painting's bright curves: along the hole's back, at its right, at its lower
left and lower right), dark cavities, broken concrete, and glowing red fissures in its floor (a cross of them in
columns 16-26 of rows 14-30, another at columns 14-20 of rows 40-46 where the front is broken, short ones at column 12
and 24, a seam at columns 31-34 of rows 42-48); the front's ribs broken away in its middle (columns 12-35 of rows
42-48). The painting lies where the live sprites do (no offset).

Built as the live house (polish_block_house.py's body, slabs, hatches in their wells, conduit, vent and ribs, its
materials; the hatches flush, as in its first frame), then broken: a hole cut through roof, slabs and front (a
jagged outline lofted from a charred floor at FLOOR up through the roof, its walls broken concrete), the slabs and parts
outside it kept; in it torn slabs curled up out of the hole across its rim (thin bent plates, lit on top, dark
under) and the slabs that lay over it fallen in, torn in two or three, bent and tumbled (none in the dark crevice the
painting leaves open, columns 14-24 of rows 9-47), a bent length of the conduit, broken concrete, and the fissures: glowing strips sunk in the floor in their
own dark reds (emission 0.42, under the bloom's white), with a few embers. Cut along the sprites' edges into the
four pieces as the live house is (polish_arch.py's cut()).

Coordinates as polish_block_house.py's: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the floor
(z = 0); the whole's origin is the corner where the four sprites meet; P(c, r) a pixel edge of the 48 x 56 picture.

Options after "--": --outdir <dir> (default assets/models/enemies), --check (the whole's silhouette against the
house's footprint), --preview <prefix>, --only <model,...>.
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
import polish_block_house as live  # noqa: E402
from polish_pyramid_wreck import (cut_piece, Hole, break_with, chunk, crack_cutter, emissive, triangulate)  # noqa: E402

P = live.P
SEED = 191
# The hole: its middle (column, row), radii, power, how jagged its edge is; its floor; its walls (height, scale).
HOLE_AT, HOLE_RADII, HOLE_POWER, HOLE_JAG = (20.4, 25.4), (15.4, 21.4), 2.7, 1.1
FLOOR = 3.2
WALLS = [(FLOOR, 0.84), (FLOOR + 2.0, 0.92), (7.0, 0.97), (live.H + 1.0, 1.0), (16.0, 1.03)]
# The torn slabs curled up out of the hole: (column, row where it lies, heading (degrees), length, width, how far it
# runs flat, the curl's radius and angle, its roll (degrees)).
PLATES = [(15.0, 7.6, 8.0, 10.5, 4.2, 4.0, 3.2, 70.0, -6.0), (30.6, 9.4, 205.0, 8.0, 3.6, 3.5, 2.6, 85.0, 8.0),
          (30.0, 19.6, 150.0, 7.5, 4.4, 2.5, 3.0, 55.0, -10.0), (6.4, 11.6, -30.0, 7.0, 3.4, 2.4, 2.4, 80.0, 6.0),
          (10.4, 36.8, 60.0, 7.5, 4.0, 3.0, 3.4, 60.0, -12.0), (28.2, 37.6, 115.0, 6.5, 3.6, 2.5, 2.8, 65.0, 10.0),
          (22.6, 11.2, 250.0, 5.0, 3.0, 2.0, 2.0, 40.0, 14.0)]
# Plates lying flat-ish in the hole, broken: (column, row, heading, length, width, tilt about their length).
SHARDS = [(13.0, 22.0, 30.0, 5.0, 3.2, 18.0), (27.4, 28.0, -20.0, 4.6, 3.0, -22.0), (9.2, 28.6, 80.0, 4.2, 2.8, 26.0),
          (20.0, 34.6, 10.0, 5.2, 2.6, -14.0), (32.0, 14.6, 95.0, 3.8, 2.6, 30.0)]
# The fissures: (column, row where they start, heading (degrees), length), glowing in the floor.
FISSURES = [(19.0, 14.0, -90.0, 16.5), (17.0, 21.2, 0.0, 9.5), (22.2, 17.2, -88.0, 10.0), (24.6, 26.0, -92.0, 7.5),
            (12.2, 26.0, -90.0, 4.6), (14.0, 43.2, 0.0, 6.6), (17.2, 40.0, -90.0, 6.4), (32.4, 41.8, -82.0, 6.5),
            (26.0, 24.0, 210.0, 4.0), (16.0, 32.0, 150.0, 3.5)]
EMBERS = [(19.4, 18.4), (20.8, 21.0), (18.6, 27.4), (23.6, 23.0), (16.8, 43.4), (32.6, 45.0), (24.8, 30.6),
          (13.0, 27.6)]
CONCRETE = 26                          # broken lumps of the roof in the hole
FILL_STEP = 4.4                        # more torn plates over the hole: how far apart
# The dark crevice the painting shows open, the glowing fissures in it (columns, rows: x0, x1, y0, y1): nothing
# fallen lies there.
CREVICES = [(14.5, 24.0, 9.0, 31.0), (15.0, 21.5, 31.0, 47.0)]


def materials():
    m = live.materials(0x0a)
    m["break"] = k.material("house_break", palette=0x05, metallic=0.2, roughness=0.75)
    m["char"] = k.material("house_char", palette=0x02, metallic=0.1, roughness=0.85)
    m["under"] = k.material("house_under", palette=0x04, metallic=0.35, roughness=0.5)
    m["fissure"] = emissive("house_fissure", 0x74, 0.42)
    m["ember"] = emissive("house_ember", 0x76, 0.3)
    return m


HOLE = Hole(P(*HOLE_AT), HOLE_RADII, HOLE_POWER, SEED, HOLE_JAG, 1.6)


def curled_plate(name, at, heading, roll, length, width, thick, flat, radius, angle, top, under, rest_on, sink=0.2):
    """A torn plate: straight for `flat`, then curled up (an arc of `radius` through `angle` degrees) along its
    length, turned to heading and rolled; set down with its lowest point sunk `sink` into rest_on(x, y) (the
    surface's height there). Its top in `top`, its underside and edges in `under`."""
    pts, ups = [], []
    n_flat = max(1, int(flat / 0.6))
    for i in range(n_flat + 1):
        pts.append(Vector((flat * i / n_flat - flat, 0.0, 0.0)))
        ups.append(Vector((0.0, 0.0, 1.0)))
    arc = min(length - flat, radius * math.radians(angle))
    n_arc = max(2, int(arc / 0.45))
    for i in range(1, n_arc + 1):
        t = arc * i / n_arc / radius
        pts.append(Vector((radius * math.sin(t), 0.0, radius * (1 - math.cos(t)))))
        ups.append(Vector((-math.sin(t), 0.0, math.cos(t))))
    obj = mk.bar(name, pts, ups, width / 2, thick / 2, thick / 2, top, 8, 8.0)
    obj.data.transform(Euler((math.radians(roll), 0.0, math.radians(heading))).to_matrix().to_4x4())
    x, y = at
    low = min(v.co.z for v in obj.data.vertices)
    obj.data.transform(Matrix.Translation((x, y, rest_on(x, y) - low - sink)))
    k.smooth(obj, 40)
    mk.paint(obj, lambda c, n: top if n.z > 0.25 else under)
    return obj


def build_whole(m):
    """The live house (hatches flush) broken: the hole, torn slabs, conduit, concrete, fissures, embers."""
    whole = live.build_whole(m, 0.0)
    # Parts wholly in the hole go, parts wholly outside stay, the rest are cut.
    kept, straddling = [], []
    ring = HOLE.ring(0.0, WALLS[-1][1])
    hx0, hx1 = min(p.x for p in ring), max(p.x for p in ring)
    hy0, hy1 = min(p.y for p in ring), max(p.y for p in ring)
    for obj in whole:
        corners = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
        ds = [HOLE.d(c.x, c.y) for c in corners]
        outside = (max(c.x for c in corners) < hx0 or min(c.x for c in corners) > hx1 or
                   max(c.y for c in corners) < hy0 or min(c.y for c in corners) > hy1)
        if max(ds) < 0.9 and min(c.z for c in corners) > FLOOR:
            bpy.data.objects.remove(obj)
        elif outside:
            kept.append(obj)
        else:
            straddling.append(obj)
    hole = HOLE.cutter("hole", WALLS, m["break"])
    broken_parts = break_with(straddling, hole)
    for obj in broken_parts:
        if obj.name == "house":
            k.smooth(obj, 40)
        else:
            mk.shade(obj, 35)   # (flat faces kept flat, as the live parts are)
    kept += broken_parts
    house = bpy.data.objects["house"]
    broken = mk.slot_of(house, m["break"])
    for poly in house.data.polygons:
        c, r = poly.center.x + 24.0, 28.0 - poly.center.y
        if (poly.material_index == broken and poly.normal.z > 0.7 and poly.center.z < FLOOR + 0.3 and
                any(a - 1.5 <= c <= b + 1.5 and e - 1.5 <= r <= f + 1.5 for a, b, e, f in CREVICES)):
            poly.material_index = mk.slot_of(house, m["char"])   # (the crevice: charred dark)
    bpy.context.view_layer.update()
    debris(kept, m)
    whole = mk.meshes()
    for obj in whole:
        mk.apply(obj)
    bpy.context.view_layer.update()
    return whole


def debris(kept, m):
    rng = random.Random(SEED)
    hit = mk.surface(kept)

    def rest_on(x, y):
        h = hit(x, y)
        return h[0].z if h else 0.0
    # The fissures first (in the floor), then what lies on it: the slabs that lay over the hole fallen into it,
    # torn in two or three, bent and tumbled (stacked where they fall on each other).
    placed = []

    def rest_on_all(x, y):
        h = mk.surface(kept + placed)(x, y)
        return h[0].z if h else 0.0
    for i, (c, r, heading, length) in enumerate(FISSURES):
        x, y = P(c, r)
        z = rest_on(x, y)
        crack_cutter(f"fissure{i}", (x, y), math.radians(heading), length, rng, m["fissure"], 0.7, z - 0.3, z + 0.06)
    for i, (c, r) in enumerate(EMBERS):
        x, y = P(c, r)
        chunk(f"ember{i}", (x, y, rest_on(x, y) - 0.1), rng.uniform(0.45, 0.7), rng, m["ember"], 0.6, 8)
    for i, (c, r, heading, length, width, flat, radius, angle, roll) in enumerate(PLATES):
        placed.append(curled_plate(f"plate{i}", P(c, r), heading, roll, length, width, 0.55, flat, radius, angle,
                                   (m["roof"], m["lit"], m["roof"], m["shade"])[i % 4], m["under"], rest_on, 0.35))
    n = 0
    for spec in live.PANELS:
        x0, x1, y0, y1, _ = live.panel_box(spec)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        if HOLE.d(cx, cy) > 0.95:
            continue
        along_x = (x1 - x0) >= (y1 - y0)
        long_side, short_side = max(x1 - x0, y1 - y0), min(x1 - x0, y1 - y0)
        parts = 1 if long_side < 6 else 2 if long_side < 12 else 3
        for j in range(parts):
            t = (j + 0.5) / parts - 0.5
            px = cx + (t * long_side if along_x else 0.0)
            py = cy + (0.0 if along_x else t * long_side)
            # (fallen a little towards the hole's middle)
            px += (HOLE.centre.x - px) * rng.uniform(0.05, 0.25)
            py += (HOLE.centre.y - py) * rng.uniform(0.05, 0.25)
            length = long_side / parts * rng.uniform(0.75, 1.0)
            c, r = px + 24.0, 28.0 - py
            if any(a <= c <= b and e <= r <= f for a, b, e, f in CREVICES):
                continue
            heading = (0.0 if along_x else 90.0) + rng.uniform(-35, 35) + (180.0 if rng.random() < 0.5 else 0.0)
            placed.append(curled_plate(f"fallen{n}", (px, py), heading, rng.uniform(-28, 28), length,
                                       short_side * rng.uniform(0.7, 0.95), 0.6, length * rng.uniform(0.35, 0.8),
                                       rng.uniform(2.2, 4.0), rng.uniform(15, 70),
                                       (m["roof"], m["shade"], m["lit"], m["roof"], m["wall"])[n % 5], m["under"],
                                       rest_on_all, 0.3))
            n += 1
    # More torn armour over the rest of the hole (outside the crevice), on a jittered grid.
    c = HOLE_AT[0] - HOLE_RADII[0]
    while c < HOLE_AT[0] + HOLE_RADII[0]:
        r = HOLE_AT[1] - HOLE_RADII[1]
        while r < HOLE_AT[1] + HOLE_RADII[1]:
            cc, rr = c + rng.uniform(-1.2, 1.2), r + rng.uniform(-1.2, 1.2)
            x, y = P(cc, rr)
            free = not any(a <= cc <= b and e <= rr <= f for a, b, e, f in CREVICES)
            if HOLE.d(x, y) < 0.82 and free:
                length = rng.uniform(3.2, 5.5)
                placed.append(curled_plate(f"torn{n}", (x, y), rng.uniform(0, 360), rng.uniform(-30, 30), length,
                                           rng.uniform(2.2, 3.4), 0.5, length * rng.uniform(0.3, 0.7),
                                           rng.uniform(1.8, 3.2), rng.uniform(25, 80),
                                           (m["roof"], m["lit"], m["shade"], m["roof"])[n % 4], m["under"],
                                           rest_on_all, 0.3))
                n += 1
            r += FILL_STEP
        c += FILL_STEP
    for i, (c, r, heading, length, width, tilt) in enumerate(SHARDS):
        placed.append(curled_plate(f"shard{i}", P(c, r), heading, tilt, length, width, 0.5, length * 0.6, 3.0, 25.0,
                                   (m["shade"], m["roof"], m["wall"])[i % 3], m["under"], rest_on_all, 0.25))
    # A bent length of the conduit lying across the hole.
    pts = [P(15.0, 30.0), P(16.6, 33.5), P(18.8, 36.2), P(22.0, 37.6), P(25.4, 37.0)]
    path = []
    for i, (x, y) in enumerate(pts):
        path.append((x, y, rest_on(x, y) + 0.45 + 0.6 * math.sin(math.pi * i / (len(pts) - 1))))
    k.smooth(mk.tube("conduit_bent", path, 0.85, m["conduit"], 12), 50)
    # Broken concrete.
    made = 0
    while made < CONCRETE:
        a, t = rng.uniform(0, 2 * math.pi), math.sqrt(rng.uniform(0.05, 1)) * 0.92
        x = HOLE.centre.x + math.cos(a) * t * HOLE.radius(a)
        y = HOLE.centre.y + math.sin(a) * t * HOLE.radius(a)
        mat = (m["wall"], m["break"], m["shade"], m["glacis"], m["roof"])[made % 5]
        chunk(f"concrete{made}", (x, y, rest_on(x, y) - 0.25), rng.uniform(0.9, 2.2), rng, mat, rng.uniform(0.5, 0.8))
        made += 1


PIECES = [(name + "_wreck", sprites, box) for name, sprites, box in live.PIECES]


def build():
    options = k.args()
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    k.reset()
    m = materials()
    whole = build_whole(m)
    print("whole block house wreck: %d triangles, %d objects" % (mk.triangles(whole), len(whole)))
    bpy.context.scene.view_settings.view_transform = "Standard"
    if "check" in options:
        mk.compare("whole wreck (the house's footprint)", mk.coverage(whole, 48, 56), live.house_mask())
    if "preview" in options:
        mk.preview(options["preview"] + "block_house_wreck_whole", whole, size=(48, 56), scale=8, distance=1.8)
    for name, sprites, box in PIECES:
        if only and name not in only:
            continue
        pieces = [p for p in (cut_piece(src, box, m["seam"]) for src in whole) if p is not None]
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
