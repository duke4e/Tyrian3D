"""What is left of IXMUCANE's and SAWBLADES' big purple glass dome once it is destroyed (stage 4 of the clean ground:
the wreck models that stand in for the map's painting of it; sheet R sprites 5 7 9 above 43 45 47 above 81 83 85),
built on polish_purple_dome.py (2026-10-25), in the way of the small dome's wreck (polish_glass_city_wreck.py).

As the maps paint it at 4x (SAWBLADES c99d83d90898734e at 612-660, 3375-3431, its middle piece at 636, 3403;
IXMUCANE e6f152b03ea0a81a the same): the egg's glass smashed. Its foot still rings the city, purple, a broad band of
it standing up the left side; two jagged teeth of it at the upper left (columns 12-24 of the picture's rows 14-25)
and a tall curved piece standing at the right (columns 44-60 of rows 10-58), the pale crescent of light down its
inner edge; the back between them open to the dirt. The city under it broken down to a dark mass of ruins (its
skyline at rows 24-28, the towers' fronts dark blue-grey), long bright strokes across it (fallen panes of the glass,
their broken edges catching the light: a lightning-like X over columns 18-44 of rows 30-50), a red spark at its middle
(column 35, row 37); dirt where the egg's back was (columns 24-44 above row 30).

Built as the live dome (polish_purple_dome.py's collar, streets, slab towers with their tiers, rims, units,
skylights and windows, its materials), then broken: the egg's back broken away beyond a jagged line (BREACH: the
collar's faces there gone, its broken ends closed; the streets short of it; the towers there down to rubble, rubble
heaped along it); the towers cut down to ruins by a height field of broken floors (RUIN_LOW..RUIN_HIGH on RUIN_CELL
squares, higher where blocks still stand: STANDING; their broken faces flat, in the roofs' shade where they face up),
most windows dark, the beacon and the masts gone; of the glass only its foot left (its inner edge broken jagged:
FOOT), purple, dark beyond the live RIM, the left band and the tall right piece standing higher (TEETH), a bright
film along every broken edge (the live sheen), the live crescent's films kept on the right piece and faint films of
light over it and the left band (LIT_BANDS); the two teeth at the upper left jagged plates of the glass standing
upright (opaque, 0x59: one on the left band, one in the ruins); one curved piece of the glass fallen on the front
ruins; long bright strokes lying across the ruins where the camera sees the painting's (0x5e, opaque, emission 0.2);
chips of glass on the dirt, dark rubble on the streets, a red spark (0x74, emission 0.3) in the middle. The
see-through materials come in the live dome's order (polish_purple_dome.piece: the opaque faces first, then the
purple and the dark glass, then the films). Cut along the sprites' edges into the nine pieces as the live dome.

Coordinates as polish_purple_dome.py's (the whole's origin the picture's middle; P(c, r) a pixel edge). models.cfg:
model purple_dome_tl_wreck enemies/purple_dome_tl_wreck.glb origin (and _tc_, _tr_, _ml_, _mc_, _mr_, _bl_, _bc_,
_br_); wreck r 5 purple_dome_tl_wreck, wreck r 7 purple_dome_tc_wreck, wreck r 9 purple_dome_tr_wreck, wreck r 43
purple_dome_ml_wreck, wreck r 45 purple_dome_mc_wreck, wreck r 47 purple_dome_mr_wreck, wreck r 81
purple_dome_bl_wreck, wreck r 83 purple_dome_bc_wreck, wreck r 85 purple_dome_br_wreck (drawn with the live sprite
lines' options, yaw=0 height=-4, at the live pieces' places).

Options after "--": --outdir <dir> (default assets/models/enemies), --preview <prefix>, --only <model,...>.
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
import polish_purple_dome as live  # noqa: E402
from polish_ixm_dock import Shading  # noqa: E402
from polish_pyramid_wreck import Noise, break_with, chunk, drop_faces, grid, heightfield_cutter  # noqa: E402

P = live.P
SEED = 85
# The ruins: the height the city is cut down to (a rough field over RUIN_CELL squares), higher where blocks stand.
RUIN_LOW, RUIN_HIGH = 2.6, 6.4
RUIN_CELL = 2.6
STANDING = [((-17.0, 12.0), 5.5, 11.0), ((-6.0, 14.0), 4.0, 9.0), ((5.0, 9.0), 4.5, 9.5), ((12.0, 3.0), 3.5, 7.5),
            ((-21.0, 18.0), 4.0, 7.0), ((3.0, 18.0), 4.0, 8.0), ((-9.0, 19.5), 3.0, 6.0)]
# The back broken away (collar, streets, towers and glass) beyond a jagged line in plan, (x, y) from the left foot
# (the egg's 140 degrees) to the right one (62 degrees): the dirt shows there in the painting.
BREACH = [(-34.0, 26.5), (-27.6, 25.0), (-23.0, 22.0), (-16.0, 20.4), (-10.0, 19.0), (-3.0, 17.6), (3.0, 18.0),
          (7.4, 21.0), (10.6, 30.0), (14.0, 42.0)]
BREACH_JAG = 0.7
LIT = 0.18                             # the share of the windows still lit
# The glass left: its foot's inner edge (a share of the foot's radius, with noise) and the pieces standing higher:
# (angle round the egg's middle, degrees from +x counter-clockwise; half width; how far in they reach).
FOOT = (0.935, 0.02)
TEETH = [(22.0, 42.0, 0.7), (146.0, 8.0, 0.76), (186.0, 40.0, 0.78)]
EDGE_W = 0.028                         # the bright film along the broken edges (a share of the foot's radius)
KEEP_BANDS = (0, 1)                    # the live crescent's films kept (CRESCENT's first two: the faint band, the sheen)
# More films on the standing glass (as the live CRESCENT's: angles, radial span, lift, material, taper), so that it
# reads lit purple as painted: the right piece's broad face and the left band.
LIT_BANDS = [(-12.0, 60.0, 0.74, 0.9, 0.03, "halo", 0.8), (0.0, 54.0, 0.78, 0.87, 0.045, "sheen", 0.9),
             (150.0, 226.0, 0.8, 0.92, 0.03, "halo", 0.8)]
# The fallen pieces: (where (column, row) they lie, the glass patch they are (angles, radial span), the tilt of their
# outside from straight up (degrees about x, y, z), how far they sink into what they fall on).
FALLEN = [((24.0, 47.0), (128.0, 146.0, 0.62, 0.84), (30.0, -24.0, 20.0), 0.4)]
# The teeth at the upper left: plates of the glass standing upright (plan x, y of their foot's middle, half width,
# the tip's height, how far the tip leans right): the first on the left band, the second in the ruins.
UPRIGHT = [((-24.4, 21.0), 1.9, 15.5, -0.6), ((-14.8, 17.6), 1.7, 15.0, 0.8)]
# Bright strokes across the ruins (the painting's fallen panes caught edge-on): from and to where the camera sees
# them (columns, rows), their width.
STREAKS = [((14.0, 40.5), (25.5, 36.0), 0.9), ((22.5, 46.5), (33.5, 33.0), 1.0), ((30.5, 31.5), (37.0, 49.0), 0.9),
           ((36.5, 33.5), (42.5, 42.5), 0.75), ((25.0, 39.0), (31.0, 45.5), 0.7)]
CHIPS = 26
SPARK = (35.0, 37.0)
NOISE = Noise(SEED, 1.3)
BREACH_NOISE = Noise(SEED + 9, 1.1)


def breach_y(x):
    """The jagged line beyond which the back is gone (plan y at x)."""
    xs = [p[0] for p in BREACH]
    for (x0, y0), (x1, y1) in zip(BREACH, BREACH[1:]):
        if x0 <= x <= x1:
            y = y0 + (y1 - y0) * (x - x0) / (x1 - x0)
            break
    else:
        y = BREACH[0][1] if x < xs[0] else BREACH[-1][1]
    return y + BREACH_JAG * BREACH_NOISE.fbm(x, 3.0, 2)


def gone(co):
    """Whether a point (plan) lies in the broken-away back."""
    return co.y > breach_y(co.x)


def materials():
    m = live.materials()
    m["window"] = k.material("dome_window_dim", palette=0x89, metallic=0.0, roughness=0.3,
                             emission=k.level_palette()[0x89], emission_strength=0.3)
    m["spark"] = k.material("dome_spark", palette=0x74, metallic=0.0, roughness=0.5,
                            emission=k.level_palette()[0x74], emission_strength=0.3)
    m["streak"] = k.material("dome_streak", palette=0x5e, metallic=0.0, roughness=0.3,
                             emission=k.level_palette()[0x5e], emission_strength=0.2)
    m["shard"] = k.material("dome_shard", palette=0x59, metallic=0.1, roughness=0.25)   # (the standing pieces: opaque)
    m["edge"] = m["sheen"]       # (the broken edges' film: the live sheen, in its place in the blending order)
    m["chip"] = m["glass_purple"]
    return m


def ruin_height(x, y):
    """The height the city is cut down to at (x, y): broken floors, higher round the blocks still standing."""
    i, j = math.floor((x + 40.0) / RUIN_CELL), math.floor((y + 40.0) / RUIN_CELL)
    level = 0.5 + 0.5 * NOISE.lattice(i, j)
    tilt = NOISE.lattice(i + 7, j + 3) * 0.14
    z = RUIN_LOW + (RUIN_HIGH - RUIN_LOW) * level + tilt * (x + 40.0 - (i + 0.5) * RUIN_CELL)
    for (sx, sy), reach, high in STANDING:
        if math.hypot(x - sx, y - sy) < reach:
            z = max(z, high - 0.3 * abs(x - sx) - 0.2 * abs(y - sy) + 0.5 * NOISE.lattice(i + 11, j))
    if y > breach_y(x) - 1.0:          # (the back's towers gone down to rubble)
        z = min(z, 0.2 + max(0.0, breach_y(x) - y) * 2.0)
    return z


def inner_edge(a):
    """The glass's broken inner edge at angle a (radians): a share of its foot's radius."""
    noise = Noise(SEED + 3, 2.0)
    deg = math.degrees(a) % 360.0
    t = FOOT[0] + FOOT[1] * noise.fbm(math.cos(a) * 6, math.sin(a) * 6, 2)
    foot = live.shell_point(0.9999, a)
    if gone(foot):
        return 0.9999
    for at, width, reach in TEETH:
        d = abs((deg - at + 180.0) % 360.0 - 180.0) / width
        if d < 1.0:
            jag = 0.03 * noise(deg * 0.35, 4.0)
            t = min(t, reach + (t - reach) * d ** 1.6 + jag)
    return min(t, 0.99)


def outward(obj):
    centre = Vector((live.EGG_C[0], live.EGG_C[1], live.GLASS_Z0))
    for poly in obj.data.polygons:
        if poly.normal.dot(Vector(poly.center) - centre) < 0:
            poly.flip()
    obj.data.update()


def shell_patch(name, a0, a1, t0, t1, mat, top_edge=None, segments=None, rows=10):
    """A patch of the glass between angles a0..a1 (degrees) and radii t0..t1 (shares of its foot's); top_edge(a) its
    broken inner edge per angle instead of t0. Returns the patch and its inner edge's points."""
    span = a1 - a0
    segments = segments or max(4, int(abs(span) / 1.5))
    verts, faces, edge = [], [], []
    for j in range(segments + 1):
        a = math.radians(a0 + span * j / segments)
        inner = top_edge(a) if top_edge else t0
        for i in range(rows + 1):
            t = inner + (t1 - inner) * i / rows
            verts.append(tuple(live.shell_point(min(t, 0.9999), a)))
        edge.append((a, inner))
    for j in range(segments):
        for i in range(rows):
            p = j * (rows + 1) + i
            faces.append((p, p + 1, p + rows + 2, p + rows + 1))
    obj = k.mesh_object(name, verts, faces, mat)
    outward(obj)
    k.smooth(obj, 80)
    return obj, edge


def edge_film(name, edge, mat):
    """A bright film along a broken edge of the glass, lying on it just outside the edge."""
    verts, faces = [], []
    for j, (a, t) in enumerate(edge):
        verts.append(tuple(live.shell_point(min(t, 0.9999), a, 0.05)))
        verts.append(tuple(live.shell_point(min(t + EDGE_W, 0.9999), a, 0.05)))
        if j:
            p = 2 * j
            faces.append((p - 2, p - 1, p + 1, p))
    obj = k.mesh_object(name, verts, faces, mat)
    outward(obj)
    return obj


def glass_remains(m):
    """The glass's foot with its broken inner edge, the left band, the teeth and the right piece: purple, dark beyond
    the live RIM; a bright film along the broken edge."""
    shell, edge = shell_patch("glassshell", -180.0, 180.0, 0.0, 1.0, m["glass_purple"], inner_edge, 240, 10)
    drop_faces(shell, gone)
    mk.paint(shell, lambda c, n: m["glass_dark"] if live.glass_t(c.x, c.y) > live.RIM else None)
    films, run = [], []
    for e in edge + [(0.0, 1.0)]:
        if e[1] < 0.999:
            run.append(e)
            continue
        if len(run) > 1:
            film = drop_faces(edge_film("glassshell_edge%d" % len(films), run, m["edge"]), gone)
            if film is not None:
                films.append(film)
        run = []
    return [shell] + films


def crescent(m):
    """The live crescent's films that lie on the right piece."""
    saved = live.CRESCENT, live.GLINT
    before = set(mk.meshes())
    try:
        live.CRESCENT = [band for i, band in enumerate(saved[0]) if i in KEEP_BANDS] + LIT_BANDS
        live.GLINT = (saved[1][0], [])
        live.highlights(m)
    finally:
        live.CRESCENT, live.GLINT = saved
    return [f for f in (drop_faces(o, gone) for o in mk.meshes() if o not in before) if f is not None]


def fallen(m, solid):
    """Curved pieces of the glass fallen across the ruins, their outside up (tilted), edged bright."""
    hit = mk.surface(solid)
    noise = Noise(SEED + 5, 0.35)
    for i, ((c, r), (a0, a1, t0, t1), rot, sink) in enumerate(FALLEN):
        jag = lambda a, i=i, t0=t0: t0 + 0.05 * noise(math.cos(a) * 9 + i * 7, math.sin(a) * 9)  # noqa: E731
        piece, edge = shell_patch(f"glassshell_fallen{i}", a0, a1, t0, t1, m["shard"], jag, rows=5)
        rim = edge_film(f"glassshell_fallen{i}_edge", edge, m["edge"])
        tm, am = (t0 + t1) / 2, math.radians((a0 + a1) / 2)
        mid = Vector(live.shell_point(tm, am))
        out = (Vector(live.shell_point(tm, am, 1.0)) - mid).normalized()
        up = Euler([math.radians(v) for v in rot]).to_matrix() @ Vector((0.0, 0.0, 1.0))
        turn = out.rotation_difference(up).to_matrix().to_4x4()
        x, y = P(c, r)
        y -= live.TAN * 5.0            # (where the camera sees it at about the ruins' height)
        h = hit(x, y)
        base = h[0].z if h else 3.0
        for obj in (piece, rim):
            obj.data.transform(Matrix.Translation(-mid))
            obj.data.transform(turn)
        low = min(v.co.z for v in piece.data.vertices)
        for obj in (piece, rim):
            obj.data.transform(Matrix.Translation((x, y, base - low - sink)))


def debris(m, rng):
    """Chips of glass on the dirt round the foot, dark rubble on the streets, the red spark."""
    n = 0
    while n < CHIPS:
        a = rng.uniform(math.radians(30), math.radians(150)) if n < CHIPS * 0.6 else rng.uniform(0, 2 * math.pi)
        r = live.egg_reach(a) + rng.uniform(0.6, 6.5)
        x, y = live.EGG_C[0] + r * math.cos(a), live.EGG_C[1] + r * math.sin(a)
        s = rng.uniform(0.4, 0.9)
        b = rng.uniform(0, 2 * math.pi)
        verts = [(x + s * math.cos(b + q * 2.1 + rng.uniform(-0.3, 0.3)), y + s * math.sin(b + q * 2.1), 0.06)
                 for q in range(3)]
        obj = k.mesh_object(f"glassshell_chip{n}", verts, [(0, 1, 2)], m["chip"])
        if obj.data.polygons[0].normal.z < 0:
            obj.data.polygons[0].flip()
        n += 1
    for i in range(16):
        a = rng.uniform(0, 2 * math.pi)
        t = rng.uniform(0.25, 0.85) * (live.egg_reach(a) - live.FLOOR_IN)
        x, y = live.EGG_C[0] + t * math.cos(a), live.EGG_C[1] + t * math.sin(a)
        chunk(f"rubble{i}", (x, y, live.FLOOR_Z - 0.1), rng.uniform(0.7, 1.5), rng,
              (m["wall"], m["mid"], m["dark"], m["body"])[i % 4], rng.uniform(0.5, 0.8))
    for i in range(12):
        x = -26.0 + 36.0 * (i + rng.uniform(0.1, 0.9)) / 12
        y = breach_y(x) - rng.uniform(0.8, 3.0)
        chunk(f"breach_rubble{i}", (x, y, live.FLOOR_Z - 0.1), rng.uniform(1.0, 2.2), rng,
              (m["wall"], m["dark"], m["body"])[i % 3], rng.uniform(0.45, 0.75))
    # Rubble heaped where the right towers stood, by the right piece.
    for i in range(9):
        x, y = rng.uniform(8.0, 19.0), rng.uniform(4.0, 20.0)
        if live.glass_t(x, y) > 0.8 or gone(Vector((x, y, 0.0))):
            continue
        chunk(f"right_rubble{i}", (x, y, live.FLOOR_Z - 0.1), rng.uniform(1.6, 3.0), rng,
              (m["wall"], m["dark"], m["body"])[i % 3], rng.uniform(0.5, 0.9))
    x, y = P(*SPARK)
    y -= live.TAN * ruin_height(x, y)
    chunk("spark", (x, y, ruin_height(x, y) + 0.1), 0.95, rng, m["spark"], 0.7, 7)


def broken_collar(m):
    """The live collar with the back gone: its faces there deleted, its broken ends closed (the collar's purple)."""
    import bmesh
    obj = live.collar(m)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if gone(f.calc_center_median())], context="FACES")
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    edges = [e for e in bm.edges if e.is_boundary]
    edges.sort(key=lambda e: tuple(sorted((tuple(e.verts[0].co), tuple(e.verts[1].co)))))
    bmesh.ops.holes_fill(bm, edges=edges, sides=0)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(obj.data)
    bm.free()
    k.smooth(obj, 50)
    return obj


def broken_floor(m):
    """The streets inside the collar, short of the broken-away back (their outline along the breach)."""
    pts = []
    for j in range(live.SEGMENTS):
        p = live.egg_point(2 * math.pi * j / live.SEGMENTS, live.FLOOR_IN, 0.0)
        pts.append((p.x, min(p.y, breach_y(p.x) - 0.6)))
    area = sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(pts, pts[1:] + pts[:1]))
    obj = mk.prism("floor", pts if area > 0 else pts[::-1], 0.0, live.FLOOR_Z, m["street"])
    k.smooth(obj, 30)
    return obj


def upright(m):
    """The two teeth at the upper left: jagged plates of the glass standing upright (facing down the screen, leaning
    a little), their foot in the ruins or on the left band, their left edges lit."""
    from polish_jaw_gun_wreck import jagged
    for i, ((x, y), half, tip, lean) in enumerate(UPRIGHT):
        z0 = ruin_height(x, y) - 1.2 if i else live.GLASS_Z0
        outline = jagged([(x - half, z0), (x + half, z0), (x + half * 0.5, z0 + (tip - z0) * 0.55),
                          (x + 0.3 * half + lean, tip), (x - half * 0.6, z0 + (tip - z0) * 0.6)], 5.0 + i, 0.25, 0.7)
        area = sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(outline, outline[1:] + outline[:1]))
        plate = mk.prism(f"tooth{i}", outline if area > 0 else outline[::-1], y - 0.2, y + 0.2, m["shard"], axis="y")
        pivot = Vector((x, y, z0))
        plate.data.transform(Matrix.Translation(pivot) @ Matrix.Rotation(math.radians(-28.0), 4, "X") @
                             Matrix.Translation(-pivot))
        mk.paint(plate, lambda c, n: m["light"] if n.x < -0.6 else None)
        mk.shade(plate, 30)


def streaks(m):
    """Long bright strokes lying across the ruins where the camera sees the painting's (opaque, faintly lit)."""
    for i, ((c0, r0), (c1, r1), w) in enumerate(STREAKS):
        pts = []
        for c, r in ((c0, r0), (c1, r1)):
            sx, sy = P(c, r)
            z = 0.0
            for _ in range(4):             # (where the camera sees it: on the ruins under that point)
                z = ruin_height(sx, sy - live.TAN * z) + 0.25
            pts.append(Vector((sx, sy - live.TAN * z, z)))
        d = (pts[1] - pts[0])
        across = Vector((-d.y, d.x, 0.0)).normalized() * (w / 2)
        verts = [pts[0] - across, pts[0] + across, pts[1] + across * 0.4, pts[1] - across * 0.4]
        top = [tuple(v) for v in verts] + [tuple(v - Vector((0, 0, 0.3))) for v in verts]
        faces = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
        obj = k.mesh_object(f"streak{i}", top, faces, m["streak"])
        k.recalc_normals(obj)


def build_whole(m):
    rng = random.Random(live.SEED)
    broken_collar(m)
    broken_floor(m)
    for i, spec in enumerate(live.TOWERS):
        live.tower(i, spec, m, rng)
    for obj in mk.meshes():
        mk.apply(obj)
    # The beacon and the masts gone with the towers' tops.
    for obj in [o for o in mk.meshes() if o.name.endswith(("_mast", "_mast_tip", "_beacon", "_beacon_mast"))]:
        data = obj.data
        bpy.data.objects.remove(obj)
        bpy.data.meshes.remove(data)
    city = [o for o in mk.meshes() if o.name not in ("collar", "floor")]
    windows = [o for o in city if o.name.endswith("_windows")]
    blocks = [o for o in city if o not in windows]
    xs = grid(-34.0, 30.0, -34.0, 30.0, 1.05, 1.05)
    ys = grid(-26.0, 36.0, -26.0, 36.0, 1.05, 1.05)
    cutter = heightfield_cutter("ruin", xs, ys, ruin_height, 40.0, m["mid"])
    ruins = break_with(blocks, cutter)
    roofs = {m[key].name for key in ("light", "mid", "dark", "body")}
    for obj in ruins:
        names = [mt.name for mt in obj.data.materials]
        roof = next((i for i, nm in enumerate(names) if nm in roofs and nm != m["mid"].name), None)
        broken = names.index(m["mid"].name) if m["mid"].name in names else None
        k.smooth(obj, 35)
        if broken is not None:
            for poly in obj.data.polygons:
                if poly.material_index == broken:
                    poly.use_smooth = False   # (the broken faces flat: rough, not pillowy)
                    if roof is not None and poly.normal.z > 0.5:
                        poly.material_index = roof
    wrng = random.Random(SEED)
    for obj in windows:
        drop_faces(obj, lambda co: co.z > ruin_height(co.x, co.y) - 0.1 or wrng.random() > LIT)
    solids = [o for o in mk.meshes()]
    bpy.context.view_layer.update()
    shells = glass_remains(m) + crescent(m)
    fallen(m, solids)
    upright(m)
    streaks(m)
    debris(m, random.Random(SEED + 1))
    bpy.context.view_layer.update()
    solids = [o for o in mk.meshes() if not o.name.startswith("glassshell")]
    shells = [o for o in mk.meshes() if o.name.startswith("glassshell")]
    for obj in solids + shells:
        mk.apply(obj)
    return solids, shells


PIECES = [(name + "_wreck", sprite, box) for name, sprite, box in live.PIECES]


def build():
    options = k.args()
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    k.reset()
    m = materials()
    solids, shells = build_whole(m)
    whole = solids + shells
    print("whole purple dome wreck: %d triangles, %d objects" % (mk.triangles(whole), len(whole)))
    bpy.context.scene.view_settings.view_transform = "Standard"
    if "preview" in options:
        mk.preview(options["preview"] + "purple_dome_wreck_whole", whole, size=(72, 84), scale=8, distance=2.4)
    shadings = {src.name: Shading(src) for src in shells}
    for name, sprite, box in PIECES:
        if only and name not in only:
            continue
        obj = live.piece(solids, shells, shadings, name, box, m)
        for src in whole:
            src.hide_render = True
        mk.report(name, [obj], os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, [obj])
        bpy.data.objects.remove(obj)
        for src in whole:
            src.hide_render = False


if __name__ == "__main__":
    build()
