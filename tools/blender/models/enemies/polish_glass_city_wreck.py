"""What is left of IXMUCANE's and SAWBLADES' glass city once it is destroyed (stage 4 of the clean ground: the wreck
models that stand in for the map's painting of it; sheet R sprites 1 and 3 above 39 and 41), built on
polish_glass_city.py. models.cfg: model glass_city_tl_wreck / _tr_wreck / _bl_wreck / _br_wreck ... origin; wreck r 1
glass_city_tl_wreck, wreck r 3 glass_city_tr_wreck, wreck r 39 glass_city_bl_wreck, wreck r 41 glass_city_br_wreck.
The game draws them where the maps paint the wreck, with the live sprite lines' options (yaw=0 height=-4), at the live
pieces' places.

The painting (IXMUCANE's and SAWBLADES' maps paint the same one; in the HD tiles and at 1x): the dome's glass smashed.
Its dark collar still rings the city (the same pixels as the live sprite's, a shade lighter: the sprite draws its
shadow over them), and its glass is gone but for jagged remains: bright broken edges of it standing round the inside
of the collar and across the city (the painting's white and pale grey strokes: columns 15-22 of rows 12-18, columns
16-23 of rows 28-36), and the pale crescent of light along its lower right edge still on a big piece left standing
there (columns 34-42 of rows 29-42). The city under it is broken and dark, its blue blocks still standing in the
middle (columns 16-30 of rows 13-27), a few of its windows still lit (the painting's cyan); dark blue chips of glass
lie scattered on the dirt up the screen from the dome (rows 0-8). The painting lies a pixel higher up the screen
than the live sprites (PAINT_DY), as the pyramid's does.

Built as the live dome (polish_glass_city.py's collar, floor of streets, the city's blocks with their parapets,
rooftop units, skylights, windows, mast and lamp, the round hall, its materials; the same see-through glass shades),
then broken: the city's blocks cut down to jagged ruins (a height field of broken floors over them, higher where the blue
blocks stand, their broken faces dark), most of their windows dark, the lamp out; of the glass shell only its foot
left, its top edge broken jagged (higher round the lower right, where the crescent's piece stands, and in a few tall
teeth), a pale bright film along every broken edge (the painting's strokes), the crescent's films kept on its piece;
three big curved pieces of the shell fallen into the city, edged the same way, and chips of glass on the dirt round
the collar. The see-through materials come in the live dome's order (the shell first, then the films over it: the
game draws a model's see-through materials in that order).

Coordinates as polish_glass_city.py's: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the ground; the
whole's origin is the corner where the four sprites meet; P(c, r) a pixel edge of the 48 x 56 picture.

Options after "--": --outdir <dir> (default assets/models/enemies), --check (the whole's silhouette against the
dome's footprint), --preview <prefix>, --only <model,...>.
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
import polish_glass_city as live  # noqa: E402
from polish_pyramid_wreck import (Noise, break_with, chunk, cut_piece, drop_faces, emissive, grid,  # noqa: E402
                                  heightfield_cutter, triangulate)

P = live.P
SEED = 39
PAINT_DY = 1.0                         # the painting lies this much higher up the screen than the live sprites
# The ruins: the height the city is cut down to (a rough field), higher round the blue blocks that still stand.
RUIN_LOW, RUIN_HIGH = 2.0, 4.8         # the field's range
RUIN_CELL = 2.3                        # the broken floors' squares
STANDING = [((26.5, 17.5), 4.0, 7.6), ((20.5, 22.0), 3.5, 5.4), ((31.5, 23.5), 3.0, 5.0)]  # (middle, reach, height)
LIT = 0.22                             # the share of the windows still lit
# The glass left: its foot's band (the share of the shell's foot radius it reaches in to, with noise), the piece
# standing round the lower right (angles, degrees, and how far in it reaches), the teeth (angle, width, reach).
FOOT = (0.875, 0.05)
CRESCENT_PIECE = (-95.0, 8.0, 0.5)
TEETH = [(118.0, 9.0, 0.6), (162.0, 7.0, 0.68), (205.0, 10.0, 0.55), (62.0, 6.0, 0.72), (30.0, 5.0, 0.8)]
EDGE_W = 0.03                         # the bright film along the broken edges (a share of the foot's radius)
# The fallen pieces: (where (column, row), the shell patch they are (angle from-to, plan radius from-to), the tilt of
# their outside (degrees about x, y, z, from straight up), how far they are sunk into what they fall on).
FALLEN = [((18.0, 15.4), (120.0, 146.0, 0.62, 0.93), (28.0, -18.0, 0.0), 0.3),
          ((19.4, 31.4), (200.0, 222.0, 0.6, 0.92), (-22.0, 14.0, 0.0), 0.3),
          ((28.6, 30.4), (-15.0, 8.0, 0.64, 0.94), (18.0, 24.0, 0.0), 0.3),
          ((14.6, 24.0), (160.0, 180.0, 0.66, 0.95), (8.0, -32.0, 0.0), 0.3)]
CHIPS = 22                             # chips of glass on the dirt (up the screen from the dome mostly)
SPARKS = [(22.4, 20.2), (27.4, 15.6), (17.6, 26.4), (30.8, 25.8)]   # lights still alight in the ruins


def materials():
    m = live.materials()
    glow = k.level_palette()
    m["window"] = emissive("city_window_dim", 0x89, 0.35, 0.0, 0.3)
    m["lamp"] = k.material("city_lamp_out", palette=0x73, metallic=0.2, roughness=0.4)
    m["edge"] = k.material("city_glass_edge", palette=0x6d, metallic=0.0, roughness=0.1, emission=glow[0x6d],
                           emission_strength=0.3, alpha=0.9)
    m["chip"] = k.material("city_glass_chip", palette=0x33, metallic=0.0, roughness=0.15, alpha=0.8)
    return m


NOISE = Noise(SEED, 1.3)


def ruin_height(x, y):
    """The height the city is cut down to at (x, y) (the live frame, before the whole is moved up PAINT_DY): broken
    floors, a height for every RUIN_CELL square (a little rough), higher round the blocks still standing."""
    c, r = x + 24.0, 28.0 - y - PAINT_DY
    i, j = math.floor(c / RUIN_CELL), math.floor(r / RUIN_CELL)
    level = 0.5 + 0.5 * NOISE.lattice(i, j)
    tilt = NOISE.lattice(i + 7, j + 3) * 0.12
    z = RUIN_LOW + (RUIN_HIGH - RUIN_LOW) * level + tilt * (c - (i + 0.5) * RUIN_CELL)
    for (sc, sr), reach, high in STANDING:
        # (a broken top a little lower towards one side, not a dome)
        if math.hypot(c - sc, r - sr) < reach:
            z = max(z, high - 0.25 * abs(c - sc) - 0.15 * (r - sr) + 0.4 * NOISE.lattice(i + 11, j))
    return z


def shell_patch(name, a0, a1, t0, t1, mat, top_edge=None, segments=None, rows=10):
    """A patch of the glass shell between angles a0..a1 (degrees) and plan radii t0..t1 (shares of the foot's);
    top_edge(a) gives the patch's inner edge per angle instead of t0 (a broken edge). Returns the patch and its inner
    edge's points."""
    span = a1 - a0
    segments = segments or max(4, int(abs(span) / 1.6))
    verts, faces, edge = [], [], []
    for j in range(segments + 1):
        a = math.radians(a0 + span * j / segments)
        inner = top_edge(a) if top_edge else t0
        for i in range(rows + 1):
            t = inner + (t1 - inner) * i / rows
            verts.append(tuple(live.shell_point(t, a)))
        edge.append((a, inner))
    for j in range(segments):
        for i in range(rows):
            p = j * (rows + 1) + i
            faces.append((p, p + 1, p + rows + 2, p + rows + 1))
    obj = k.mesh_object(name, verts, faces, mat)
    for poly in obj.data.polygons:
        out = Vector(poly.center) - Vector((live.CENTRE[0], live.CENTRE[1], live.GLASS_Z0))
        if poly.normal.dot(out) < 0:
            poly.flip()
    obj.data.update()
    k.smooth(obj, 80)
    return obj, edge


def edge_film(name, edge, mat):
    """A bright film along a broken edge of the glass: a strip just inside the edge, lying on the shell."""
    verts, faces = [], []
    for j, (a, t) in enumerate(edge):
        verts.append(tuple(live.shell_point(t, a, 0.04)))
        verts.append(tuple(live.shell_point(min(t + EDGE_W, 1.0), a, 0.04)))
        if j:
            p = 2 * j
            faces.append((p - 2, p - 1, p + 1, p))
    obj = k.mesh_object(name, verts, faces, mat)
    for poly in obj.data.polygons:
        out = Vector(poly.center) - Vector((live.CENTRE[0], live.CENTRE[1], live.GLASS_Z0))
        if poly.normal.dot(out) < 0:
            poly.flip()
    obj.data.update()
    return obj


def glass_remains(m):
    """The shell's foot with its broken top edge, the crescent's piece and the teeth, in the live shell's bands;
    the bright films along the broken edges; the crescent's films."""
    noise = Noise(SEED + 3, 2.2)
    b0, b1, b2 = live.BANDS

    def inner(a):
        deg = math.degrees(a)
        t = FOOT[0] + FOOT[1] * noise.fbm(math.cos(a) * 6, math.sin(a) * 6, 2)
        lo, hi, reach = CRESCENT_PIECE
        if lo <= ((deg + 180) % 360) - 180 <= hi:
            f = min(((deg + 180) % 360 - 180 - lo) / 12.0, (hi - ((deg + 180) % 360 - 180)) / 12.0, 1.0)
            t = min(t, t - (t - reach) * f + 0.04 * noise(deg * 0.3, 1.0))
        for at, width, reach in TEETH:
            d = abs((deg - at + 180) % 360 - 180) / width
            if d < 1:
                t = min(t, reach + (t - reach) * d ** 1.5)
        return min(t, 0.99)
    shell, edge = shell_patch("glassshell", -180.0, 180.0, 0.0, 1.0, m["glass"], inner, 180, 10)

    def pick(c, n):
        t = math.hypot(c.x - live.CENTRE[0], c.y - live.CENTRE[1]) / live.GLASS_R
        if t > b1:
            return m["glass_dark"]
        if t > b0:
            return m["glass_dim"]
        return m["glass_dim"] if c.y < live.CENTRE[1] else None
    mk.paint(shell, pick)
    films = [edge_film("glassshell_d_edge", edge, m["edge"])]
    return [shell] + films


def build_whole(m):
    solid, shells = live.build_whole(m)
    # Of the live glass only the crescent's films stay (on its standing piece); the shell is built again, broken.
    keep_films = ("glassshell_b_crescent", "glassshell_c_core")
    for obj in shells:
        if obj.name not in keep_films:
            bpy.data.objects.remove(obj)
    films = [bpy.data.objects[n] for n in keep_films]
    for obj in films:
        obj.data.materials.clear()
        obj.data.materials.append(m["sheen"] if obj.name.endswith("crescent") else m["edge"])
    # The city cut down to ruins.
    city = [o for o in solid if o.name not in ("collar", "floor")]
    windows = [o for o in city if o.name.endswith("_windows")]
    blocks = [o for o in city if o not in windows]
    xs = grid(-22.0, 22.0, -22.0, 22.0, 0.6, 0.6)
    ys = grid(-24.0, 22.0, -24.0, 22.0, 0.6, 0.6)
    cutter = heightfield_cutter("ruin", xs, ys, ruin_height, 30.0, m["mid"])
    ruins = break_with(blocks, cutter)
    roofs = {m[key].name for key in ("light", "mid", "dark", "blue")}
    for obj in ruins:
        # The broken floors in the block's own roof colour (the blue blocks stay blue).
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
    rng = random.Random(SEED)
    for obj in windows:
        drop_faces(obj, lambda co: co.z > ruin_height(co.x, co.y) - 0.1 or rng.random() > LIT)
    remains = glass_remains(m)
    bpy.context.view_layer.update()
    fallen(m, [o for o in mk.meshes() if not o.name.startswith("glassshell")])
    debris(m)
    whole = mk.meshes()
    for obj in whole:
        mk.apply(obj)
        obj.data.transform(Matrix.Translation((0.0, PAINT_DY, 0.0)))
    bpy.context.view_layer.update()
    return whole


def fallen(m, solid):
    """Big curved pieces of the shell fallen into the city (panels from its steeper part, their edges broken),
    lying tilted on the ruins with their outside up, edged bright."""
    hit = mk.surface(solid)
    noise = Noise(SEED + 5, 0.35)
    for i, ((c, r), (a0, a1, t0, t1), rot, sink) in enumerate(FALLEN):
        jag = lambda a, i=i, t0=t0: t0 + 0.06 * noise(math.cos(a) * 9 + i * 7, math.sin(a) * 9)  # noqa: E731
        piece, edge = shell_patch(f"glassshell_fallen{i}", a0, a1, t0, t1, m["glass_dim"], jag, rows=5)
        rim = edge_film(f"glassshell_e_fallen{i}", edge, m["edge"])
        tm, am = (t0 + t1) / 2, math.radians((a0 + a1) / 2)
        mid = Vector(live.shell_point(tm, am))
        out = (Vector(live.shell_point(tm, am, 1.0)) - mid).normalized()
        up = Euler([math.radians(v) for v in rot]).to_matrix() @ Vector((0.0, 0.0, 1.0))
        turn = out.rotation_difference(up).to_matrix().to_4x4()
        x, y = P(c, r + PAINT_DY)   # (the live frame: the whole is moved up afterwards)
        h = hit(x, y)
        base = h[0].z if h else 0.5
        for obj in (piece, rim):
            obj.data.transform(Matrix.Translation(-mid))
            obj.data.transform(turn)
        low = min(v.co.z for v in piece.data.vertices)
        for obj in (piece, rim):
            obj.data.transform(Matrix.Translation((x, y, base - low - sink)))


def debris(m):
    """Chips of glass on the dirt round the collar, broken blocks on the streets, the lights left alight."""
    rng = random.Random(SEED + 1)
    n = 0
    while n < CHIPS:
        a = rng.uniform(math.radians(20), math.radians(200)) if n < CHIPS * 0.7 else rng.uniform(0, 2 * math.pi)
        r = live.R_OUT + rng.uniform(0.8, 7.5)
        x, y = live.CENTRE[0] + r * math.cos(a), live.CENTRE[1] + r * math.sin(a)
        s = rng.uniform(0.35, 0.8)
        b = rng.uniform(0, 2 * math.pi)
        verts = [(x + s * math.cos(b + q * 2.1 + rng.uniform(-0.3, 0.3)), y + s * math.sin(b + q * 2.1), 0.06)
                 for q in range(3)]
        obj = k.mesh_object(f"glassshell_f_chip{n}", verts, [(0, 1, 2)], m["chip"])
        if obj.data.polygons[0].normal.z < 0:
            obj.data.polygons[0].flip()
        n += 1
    for i in range(14):
        a, t = rng.uniform(0, 2 * math.pi), rng.uniform(0.2, 0.85) * live.FLOOR_R
        x, y = live.CENTRE[0] + t * math.cos(a), live.CENTRE[1] + t * math.sin(a)
        chunk(f"rubble{i}", (x, y, live.FLOOR_Z - 0.1), rng.uniform(0.6, 1.3), rng,
              (m["wall"], m["mid"], m["dark"], m["blue"])[i % 4], rng.uniform(0.5, 0.8))
    for i, (c, r) in enumerate(SPARKS):
        x, y = P(c, r + PAINT_DY)   # (the live frame: the whole is moved up afterwards)
        chunk(f"spark{i}", (x, y, ruin_height(x, y) - 0.15), 0.5, rng, m["window"], 0.6, 7)


def dome_mask():
    return [[math.hypot(c + 0.5 - 24.0 - live.CENTRE[0], 28.0 - r - 0.5 - live.CENTRE[1] - PAINT_DY) < live.R_OUT
             for c in range(48)] for r in range(56)]


PIECES = [(name + "_wreck", sprite, box) for name, sprite, box in live.PIECES]


def build():
    options = k.args()
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    k.reset()
    m = materials()
    whole = build_whole(m)
    print("whole glass city wreck: %d triangles, %d objects" % (mk.triangles(whole), len(whole)))
    bpy.context.scene.view_settings.view_transform = "Standard"
    if "check" in options:
        mk.compare("whole wreck (the dome's footprint)", mk.coverage(whole, 48, 56), dome_mask())
    if "preview" in options:
        mk.preview(options["preview"] + "glass_city_wreck_whole", whole, size=(48, 56), scale=8, distance=1.8)
    solid = [o for o in whole if not o.name.startswith("glassshell")]
    shells = [o for o in whole if o.name.startswith("glassshell")]
    for name, sprite, box in PIECES:
        if only and name not in only:
            continue
        pieces = [p for p in (cut_piece(src, box, m["collar"]) for src in solid) if p is not None]
        pieces += [p for p in (live.cut_open(src, box) for src in shells) if p is not None]
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
