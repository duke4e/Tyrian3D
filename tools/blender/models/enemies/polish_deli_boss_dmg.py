"""DELI's boss damaged (models deli_boss_115, deli_boss_119, deli_boss_121, deli_boss_125, deli_arm_left_damaged,
deli_arm_right_damaged): the dgr sprites the game puts in six pieces' places when they are hit hard (DELI, New Deli,
HARVEST; enemies 400, 402, 403, 405 and the arms 406, 411): T 1 -> 115, 5 -> 119, 7 -> 121, 11 -> 125, 39 -> 153,
49 -> 163; the pieces 3 and 9 between them and the bottom row 41-47 keep their sprites. models.cfg (as before): model
deli_boss_115 / 119 / 121 / 125 enemies/deli_boss_<sprite>.glb origin, model deli_arm_left_damaged /
deli_arm_right_damaged enemies/....glb origin; sprite t <sprite> <model> yaw=0. Polished 2026-10-21; it replaces
wave3_ap_deli.py (the old boss and arms painted by the damaged pixels, pressed in: delete it, nothing else loads it)
and wave3_ap_art.py's BOSS_DMG (only wave3_ap_deli.py reads it).

The machine is polish_deli_boss.py's (its builders imported, unchanged), built whole, damaged as the damaged sprites
draw it and cut into the same pieces at the same origins, so that a damaged piece meets its neighbours, damaged or
not: no surface moves within SEAM of the pieces' edges (the dents fade out over SEAM_FADE; the burnt meshes are cut
along the edges first, so that the cut finds the intact surface there), the cracks stop short of them.

What the damaged sprites draw differently, read pixel by pixel into DAMAGE below (the 144 x 56 picture, its left and
right halves; ' ' empty in both, '.' as it was, '-' gone, 'c' burnt black, 's' scorched (four or more shades darker),
't' darker (red), 'd' dulled (the black and grey parts darker), 'L' lighter (cracks, torn edges), 'x' fire gone out,
'e' 'E' embers (dim, brighter), 'r' fire turned dull red):
- T 119: the fire behind the left grille burnt down to a few embers (rows 2-7); the left shoulder burnt black round its
  vent (columns 48-58 of rows 11-14, scorched round it) and down the frame beside the sphere (columns 48-57 of rows
  16-26); the sphere's glare gone, a crack down its upper left (from column 59 of row 17 to column 54 of row 23) and
  one at its lower right (rows 25-27); the canopy cracked down its middle (columns 69-72 of rows 16-27), its frame bar
  broken.
- T 121: the right grille blown away (rows 1-8, columns 75-90: nothing there but its burnt footing); the right shoulder
  burnt black by the sphere (columns 86-95 of rows 12-20); the sphere's glare gone, split by cracks (across its top,
  rows 18-20; down its middle, rows 22-27; down its right, columns 87-90 of rows 23-27); the canopy's right side
  cracked.
- T 115 / T 153: the left arm's tube scorched over its shoulder (rows 20-27) and burnt black down its outer half
  (columns 4-11 of rows 28-38), the cuff burnt; the eye put out (dull dark red, rows 44-50).
- T 125 / T 163: the right arm burnt black over most of its tube (rows 22-38), the cuff and the pod's top (rows
  39-44); the eye put out (black).
How: burnt faces are cut finer where the burns lie, along smooth, ragged borders (the map blurred, with noise), painted
char and scorch, and pressed in; the shoulders' burns are holes torn through the plate (jagged, charred walls) onto the
charred deck under it; the cracks are jagged strips laid on the spheres and the canopy (a dark gap with a lit edge);
the spheres' glare and light band are dulled to their base; the grille's fire bed sinks and goes dark, a few embers
glowing; the right grille's housing, fire and slats are gone, their footing charred; the eyes' lenses take dead colours.

Coordinates as in polish_deli_boss.py, after its move onto the picture's axis: pixel (c, r) covers x c - 72..c - 71,
y 27 - r..28 - r.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes of the whole
and of each piece against enemy_T.png), --preview <prefix>, --only <model,...>, --whole <file.glb>, --stats 1.
"""
import math
import os
import random
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Vector, noise
from mathutils.bvhtree import BVHTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_deli_boss as db  # noqa: E402
from polish_deli_boss import mk, k  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402

CELLS = [("deli_boss_115", 115, 0, 0), ("deli_boss_119", 119, 48, 0), ("deli_boss_121", 121, 72, 0),
         ("deli_boss_125", 125, 120, 0), ("deli_arm_left_damaged", 153, 0, 28),
         ("deli_arm_right_damaged", 163, 120, 28)]
PIECES = [(name, sprite, db.box_of(col, row)) for name, sprite, col, row in CELLS]
# The whole damaged picture's sprites (for the silhouette check): the damaged six and the intact six between them.
WHOLE_CELLS = [("", 115, 0, 0), ("", 3, 24, 0), ("", 119, 48, 0), ("", 121, 72, 0), ("", 9, 96, 0), ("", 125, 120, 0),
               ("", 153, 0, 28), ("", 41, 24, 28), ("", 43, 48, 28), ("", 45, 72, 28), ("", 47, 96, 28),
               ("", 163, 120, 28)]
SEAMS_X = (-48.0, -24.0, 0.0, 24.0, 48.0)
SEAM, SEAM_FADE = 0.25, 1.4

# --- The damage map ----------------------------------------------------------------------------------------------
DAMAGE_LEFT = [
    '',
    '                                                            ........',
    '                                                          ..xxexex..',
    '                                                         .xxxxxxEee.',
    '                                                        ..xxexxxEee.....',
    '                                                       .xxexxxx.x.......',
    '                                      .......         .eexxxxx..........',
    '                                    .........        ..eexxxx...........',
    '                                   .......................x.............',
    '                                  ......................................',
    '             .....++             .................tt....tc..............',
    '          .........+            ................ssttsttcc.t.............',
    '         ...........            ................ccc.ccccc.c.............',
    '        ............     .......................c.c.c.c...t.............',
    '        ............     .......................ccc.c.tcc...............',
    '        ............     .......................c.s.s...................',
    '        .............    .......................c.ccs...............d.dd',
    '        ........................................c.c.c.t.............d..d',
    '        ........................................cc.ccst.....ddd...ddd.L.',
    '        ........................................c.ccsst..dd.ddddddd..LL.',
    '       ...ttt..ttssssc..........................ctcssc.ddddLddd...d..L..',
    '      ...tcstttttcccsc..........................c.tsc..ddddddd....d..Ldd',
    '     ...tsscstttcccssc..........................tctt..dddddddd....d.LLdL',
    '    .tttssssctttscc....................................ddddddd.........L',
    '    ..ttsssss..tsc..............................t.....ddddddd..........L',
    '   .....sssss...................          ......c.....dddddddLL........L',
    '   .....ssccstt................           ......ct....ddddd.LL.........L',
    '   ....tssccstc......... ......           ......ct.........LLL.........L',
    '   ...sscccct.c........   .......         ..............................',
    '   ..cccccctttt.......    .......         ..............................',
    '   .ccccccctttt......     .......         ..............................',
    '   .cccccccttt.......     .......         ..............................',
    '   .ccccccctc.......                          ..........................',
    '   .cccsccct........                          ..........................',
    '   .ccLsssc.........                          ..........................',
    '   .tLttst..........                           .........................',
    '   .Lccsst..........                           ......................',
    '   ..cccst..........                            .....................',
    '   ..cccc...........                            ....................',
    '   ..t...............                            ..................',
    '     ................                             ................',
    '       ..............                              .............',
    '       ..............',
    '       ..............',
    '       ....L.........',
    '       .....rrrxx....',
    '       ....xrrrx.....',
    '       ....rrrrx.x...',
    '       ....rrrr.xx...',
    '       .....x..rr....',
    '       .............',
    '        ...........',
    '         .........',
    '          ......',
    '',
    '',
]
# The picture's right half (columns 72-143).
DAMAGE_RIGHT = [
    '',
    '   --------',
    '   ----------',
    '   -----------',
    '....x----------',
    '.....x----------',
    '.........e-------         .......',
    '.........xxx-----.        .........',
    '............x---....................',
    '.....................................',
    '......................................               .....',
    '.......................................             .........',
    '..................L.cctc...............            ...........',
    '................t...c.cc......................     ............',
    '...............cc.LLcccc......................     ............',
    '....d.........tcccs.t.cc......................     ............',
    'ddddd.........tsc.scsL.s......................    .............',
    'ddddd.........tsc.c.c.t........................................',
    'ddddd..LL......csscc.ccs.......................................',
    '...d....LL......ssscccct.......................................',
    '.L.d....d.LLL....csscct.........................................',
    'LL.d.....dd.......tt.............................................',
    'L.....LL.ddd.....d..................................ttt...tctst...',
    '....L.LLL.ddd...Ld..................................ctL.ttc.sscs...',
    '......L.LLLLL...L....................................c.scccssccct..',
    '...........LL...L............          ...............c.ccccccccc...',
    '..........LL...LL............           ................cccccccccc..',
    '..........L....L.............           ...... .........ccscsccctc..',
    '.............................         .......   ........tssccccscc..',
    '.............................         .......    ..........tcscscct.',
    '.............................         .......     ..........cscscct.',
    '.............................         .......     .......tttctctcct.',
    '.........................                          ......tttcscscct.',
    '.........................                          .....ttcscst.tc..',
    '.........................                          .....cccccst.....',
    '........................                           .........ctt.....',
    '  ......................                           ...cscccsst......',
    '  .....................                            ..ccsccccs.......',
    '   ....................                            .cccscccst.......',
    '    ..................                            .ccc....tcc......',
    '     ................                             .cc.ssccccct....',
    '       .............                              .c.ssssccccct.',
    '                                                  ..stsssccccct.',
    '                                                  .ttttccc...st.',
    '                                                  .t.......cccs.',
    '                                                  ....xxxxr.ccc.',
    '                                                  ...xxxxx......',
    '                                                  ...xxxxx.x....',
    '                                                  ...xxxx.rx....',
    '                                                  ....x..xx.....',
    '                                                   .............',
    '                                                    ...........',
    '                                                     .........',
    '                                                       ......',
    '',
    '',
]


def grid(values):
    """The map as an array (56 x 144): each pixel's value from values (class -> value)."""
    g = np.zeros((56, 144))
    for r in range(56):
        for c, ch in enumerate(DAMAGE_LEFT[r]):
            g[r, c] = values.get(ch, 0.0)
        for c, ch in enumerate(DAMAGE_RIGHT[r]):
            g[r, 72 + c] = values.get(ch, 0.0)
    return g


def cls_at(x, y):
    """The map's class of the pixel under (x, y)."""
    c, r = int(math.floor(x + 72.0)), int(math.floor(28.0 - y))
    if not (0 <= r < 56 and 0 <= c < 144):
        return " "
    line = DAMAGE_LEFT[r] if c < 72 else DAMAGE_RIGHT[r]
    cc = c if c < 72 else c - 72
    return line[cc] if cc < len(line) else " "


def blur(a, sigma):
    """A Gaussian blur of an array (zero outside)."""
    radius = int(math.ceil(sigma * 3))
    kern = np.exp(-np.arange(-radius, radius + 1) ** 2 / (2 * sigma * sigma))
    kern /= kern.sum()
    pad = np.pad(a, radius)
    tmp = sum(kv * np.roll(pad, i - radius, axis=1) for i, kv in enumerate(kern))
    out = sum(kv * np.roll(tmp, i - radius, axis=0) for i, kv in enumerate(kern))
    return out[radius:-radius, radius:-radius]


class Field:
    """A map over the picture (values at the pixels' middles), sampled between them."""

    def __init__(self, a):
        self.a = a

    def __call__(self, x, y):
        u, v = x + 71.5, 27.5 - y
        c0, r0 = int(math.floor(u)), int(math.floor(v))
        fu, fv = u - c0, v - r0

        def at(r, c):
            return self.a[r, c] if 0 <= r < 56 and 0 <= c < 144 else 0.0
        return ((1 - fu) * (1 - fv) * at(r0, c0) + fu * (1 - fv) * at(r0, c0 + 1) +
                (1 - fu) * fv * at(r0 + 1, c0) + fu * fv * at(r0 + 1, c0 + 1))


# The burns: black, scorched, darker; the gone right grille's footing black. Blurred a little, then made ragged.
BURN = Field(blur(grid({"c": 1.0, "s": 0.8, "t": 0.5, "-": 1.0}), 0.65))
CHAR, SCORCH = 0.46, 0.2         # charred above this, scorched above that
DENT = {"shoulder": 0.4, "deck": 0.4, "rim": 0.3, "wing": 0.3, "bar": 0.3, "arm_tube": 0.45, "cuff": 0.35,
        "pod": 0.35}
GRID = 1.5                       # how fine the burnt plates are cut


def ragged(x, y, value):
    """The burn field made ragged along its borders (seeded noise: the same every run)."""
    if value <= 0.0:
        return value
    n = 0.13 * noise.noise(Vector((x * 0.7, y * 0.7, 3.3))) + 0.06 * noise.noise(Vector((x * 2.1, y * 2.1, 9.1)))
    return value + n * min(1.0, value * 4.0)


def fade(x, y):
    """1 away from the pieces' edges, 0 within SEAM of them (nothing moves there)."""
    d = min([abs(x - s) for s in SEAMS_X] + [abs(y)])
    return db.smoothstep(SEAM, SEAM_FADE, d)


# The holes torn through the shoulder plates: (object, centre column, row, half-width, half-height, seed).
HOLES = [("shoulder", 53.4, 12.9, 3.7, 1.75, 1), ("shoulder_r", 91.9, 16.0, 2.7, 2.6, 2)]
HOLE_JAG = 0.28
# The cracks (polylines of pixel middles, column and row) laid on the spheres and the canopy; their jags.
CRACKS = {
    "sphere": [[(59.4, 16.6), (59.5, 18.4), (59.2, 20.4), (58.3, 21.5), (57.3, 22.5), (55.6, 23.3), (53.6, 23.5)],
               [(63.0, 24.4), (61.8, 25.5), (60.6, 26.5), (59.5, 27.3)],
               [(59.2, 20.4), (60.6, 21.2), (62.2, 21.6), (63.8, 22.6)],
               [(57.3, 22.5), (57.0, 24.2), (56.0, 25.6), (55.2, 27.3)]],
    "sphere_r": [[(78.8, 17.9), (80.4, 18.5), (82.0, 19.3), (83.6, 20.3), (85.6, 20.6), (87.4, 21.6)],
                 [(82.0, 19.3), (81.0, 21.0), (80.2, 22.6)],
                 [(77.9, 22.1), (79.2, 23.1), (80.7, 24.1), (82.6, 24.3), (84.2, 24.6), (83.1, 26.0), (82.3, 27.3)],
                 [(88.2, 22.6), (88.6, 24.3), (88.4, 25.8), (87.5, 27.2)],
                 [(88.6, 24.3), (89.7, 25.5), (90.1, 26.8)]],
    "canopy": [[(69.6, 16.2), (69.9, 18.4), (69.6, 20.4), (69.1, 21.8), (70.2, 22.6), (71.4, 23.6)],
               [(75.6, 18.8), (74.3, 19.8), (72.9, 21.0), (71.5, 22.1), (70.2, 22.6)]],
}
CRACK_JAG, CRACK_STEP = 0.2, 0.45
CRACK_GAP, CRACK_EDGE = 1.0, 0.6      # the dark gap's width, the lit edge's
# The canopy's frame bar broken (columns).
BAR_BREAK = (69.1, 70.4)
# The left grille's fire bed sunk by this.
FIRE_SINK = 0.45


def materials():
    pal = k.level_palette()
    m = db.materials()

    def mat(name, index, metallic=0.2, roughness=0.6, glow=0.0):
        if glow > 0:
            return k.material("delid_" + name, palette=index, metallic=metallic, roughness=roughness,
                              emission=pal[index], emission_strength=glow)
        return k.material("delid_" + name, palette=index, metallic=metallic, roughness=roughness)
    m.update({
        "char": mat("char", 0x40, 0.05, 0.9),
        "scorch": mat("scorch", 0x42, 0.15, 0.7),
        "crack": mat("crack", 0x0b, 0.3, 0.3, glow=0.16),
        "ember": mat("ember", 0x74, 0.0, 0.6, glow=0.4),
        "ember_hot": mat("ember_hot", 0x77, 0.0, 0.5, glow=0.55),
        "eye_dead": mat("eye_dead", 0x43, 0.2, 0.4, glow=0.05),
        "eye_dead_hot": mat("eye_dead_hot", 0x46, 0.2, 0.3, glow=0.08),
    })
    return m


def objects(prefixes):
    """The whole's meshes whose names (without a Blender .001 suffix) start with one of the prefixes."""
    return [o for o in mk.meshes() if o.name.split(".")[0].startswith(tuple(prefixes))]


def remove(obj):
    data = obj.data
    bpy.data.objects.remove(obj)
    if data.users == 0:
        bpy.data.meshes.remove(data)


def swap(obj, old, new):
    """Gives the faces of material old the material new."""
    names = [mm.name for mm in obj.data.materials]
    if old.name not in names:
        return
    i_old = names.index(old.name)
    i_new = mk.slot_of(obj, new)
    for poly in obj.data.polygons:
        if poly.material_index == i_old:
            poly.material_index = i_new


# --- The grilles ---------------------------------------------------------------------------------------------------

def grilles(m):
    """The right grille blown away (its housing, fire and slats gone); the left one's fire burnt down: its bed sunk,
    dark, glowing only where the sprite still draws embers."""
    for obj in objects(["grille_housing_r", "grille_fire_r"]) + [o for o in mk.meshes() if o.name.startswith("slat")
                                                                  and o.name.endswith("_r")]:
        remove(obj)
    fire = bpy.data.objects["grille_fire"]
    for v in fire.data.vertices:
        if v.co.z > db.FIRE_Z - 0.4:
            v.co.z -= FIRE_SINK
    fire.data.update()
    core, ember, hot = (mk.slot_of(fire, m[n]) for n in ("core", "ember", "ember_hot"))
    for poly in fire.data.polygons:
        ch = cls_at(poly.center.x, poly.center.y)
        poly.material_index = hot if ch == "E" else ember if ch == "e" else core
    # its other materials no face uses any more are dropped at the cut (drop_unused)


# --- The holes and the burns -------------------------------------------------------------------------------------

def jagged(c, r, rx, ry, seed, n=14):
    rng = random.Random(seed)
    x0, y0 = c - 72.0, 28.0 - r
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        f = 1.0 + rng.uniform(-HOLE_JAG, HOLE_JAG)
        pts.append((x0 + rx * f * math.cos(a), y0 + ry * f * math.sin(a)))
    return pts


def holes(m):
    """The burns on the shoulders torn through the plate: jagged holes, their walls charred."""
    for name, c, r, rx, ry, seed in HOLES:
        obj = bpy.data.objects[name]
        cutter = mk.prism(f"{name}_hole", mk.chaikin(jagged(c, r, rx, ry, seed), 1), db.DECK_TOP - 2.5, 20.0, m["char"])
        mk.boolean(obj, cutter, "DIFFERENCE")
        mk.cleanup(obj, dissolve=0.0)


def burn_regions():
    """The burns' boxes (x0, x1, y0, y1): the bounds of each connected patch of the field (4-connected pixels over
    0.04), a pixel wider."""
    mask = BURN.a > 0.04
    seen = np.zeros_like(mask)
    boxes = []
    for r0 in range(56):
        for c0 in range(144):
            if not mask[r0, c0] or seen[r0, c0]:
                continue
            stack, cells = [(r0, c0)], []
            seen[r0, c0] = True
            while stack:
                r, c = stack.pop()
                cells.append((r, c))
                for rr, cc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                    if 0 <= rr < 56 and 0 <= cc < 144 and mask[rr, cc] and not seen[rr, cc]:
                        seen[rr, cc] = True
                        stack.append((rr, cc))
            rs = [r for r, _ in cells]
            cs = [c for _, c in cells]
            boxes.append((min(cs) - 72.0 - 1.0, max(cs) - 71.0 + 1.0, 28.0 - max(rs) - 2.0, 28.0 - min(rs) + 1.0))
    return boxes


BOXES = None


def refine(bm, step, skip=(), covered=None):
    """Cuts the faces the camera sees in the burns' boxes until their edges are under step (edges halved, up to four
    times), so that the burns can be painted and pressed in; the rest of the mesh (and faces of the material slots
    skip: the dark cuts, and those covered(centre) says something lies over) is left as it is."""
    global BOXES
    if BOXES is None:
        BOXES = burn_regions()
    # First a coarse grid across the boxes (the long faces of the plates' tops broken up), then the edges halved.
    bm.normal_update()
    for x0, x1, y0, y1 in BOXES:
        for axis, lo, hi in ((0, x0, x1), (1, y0, y1)):
            n = max(1, int(math.ceil((hi - lo) / (2.5 * step))))
            for i in range(1, n):
                v = lo + (hi - lo) * i / n
                faces = []
                for f in bm.faces:
                    if f.normal.z < 0.2 or f.material_index in skip:
                        continue
                    xs = [vv.co.x for vv in f.verts]
                    ys = [vv.co.y for vv in f.verts]
                    if max(xs) < x0 or min(xs) > x1 or max(ys) < y0 or min(ys) > y1:
                        continue
                    if (min(xs) < v < max(xs)) if axis == 0 else (min(ys) < v < max(ys)):
                        faces.append(f)
                if faces:
                    geom = (list({e for f in faces for e in f.edges}) + list({vv for f in faces for vv in f.verts}) +
                            faces)
                    bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-5, plane_co=(v, 0, 0) if axis == 0 else (0, v, 0),
                                           plane_no=(1, 0, 0) if axis == 0 else (0, 1, 0))
                    bm.normal_update()
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    for _ in range(4):
        bm.normal_update()
        edges = set()
        for f in bm.faces:
            if f.normal.z < 0.2 or f.material_index in skip:
                continue
            xs = [v.co.x for v in f.verts]
            ys = [v.co.y for v in f.verts]
            if not any(min(xs) < x1 and max(xs) > x0 and min(ys) < y1 and max(ys) > y0 for x0, x1, y0, y1 in BOXES):
                continue
            c = f.calc_center_median()
            if max([BURN(c.x, c.y)] + [BURN(v.co.x, v.co.y) for v in f.verts]) < 0.02:
                continue
            if covered is not None and covered(c):
                continue
            for e in f.edges:
                if e.calc_length() > step:
                    edges.add(e)
        if not edges:
            break
        bmesh.ops.subdivide_edges(bm, edges=list(edges), cuts=1, use_grid_fill=False)
        bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3])


def cover_test(obj):
    """covered(point): whether another part lies over the point (a ray cast straight up meets it)."""
    depsgraph = bpy.context.evaluated_depsgraph_get()
    trees = [BVHTree.FromObject(o, depsgraph) for o in mk.meshes() if o is not obj]

    def covered(p):
        start = Vector((p.x, p.y, p.z + 0.05))
        return any(t.ray_cast(start, Vector((0, 0, 1)), 30.0)[0] is not None for t in trees)
    return covered


def burn(obj, m, dent, cut=True):
    """Paints the burns on an object (the faces the camera sees), along smooth ragged borders, and presses them in."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    skip = {i for i, mm in enumerate(obj.data.materials) if mm is not None and mm.name == m["core"].name}
    if cut:
        refine(bm, GRID, skip, cover_test(obj))
    else:
        bmesh.ops.triangulate(bm, faces=bm.faces[:])
    values = {v: ragged(v.co.x, v.co.y, BURN(v.co.x, v.co.y)) for v in bm.verts}
    for threshold in ((SCORCH, CHAR) if not cut else (CHAR,)):   # the plates' scorch follows their faces
        mk.split_along(bm, values, threshold)
        for v in bm.verts:
            values.setdefault(v, threshold)
    bm.normal_update()
    char = mk.slot_of(obj, m["char"])
    scorch = mk.slot_of(obj, m["scorch"])
    keep = {mk.slot_of(obj, m[n]) for n in ("core",)}
    for f in bm.faces:
        if f.material_index in keep or f.normal.z < -0.35:
            continue
        value = sum(values[v] for v in f.verts) / len(f.verts)
        if value > CHAR:
            f.material_index = char
        elif value > SCORCH:
            f.material_index = scorch
    if dent:
        # cut along the pieces' edges first, so that no face spans one: the edges' vertices stay where they were and
        # the cut there finds the intact surface
        for co, no in [((s, 0, 0), (1, 0, 0)) for s in SEAMS_X] + [((0, 0, 0), (0, 1, 0))]:
            res = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-5, plane_co=co,
                                         plane_no=no)
            for v in res["geom_cut"]:
                if isinstance(v, bmesh.types.BMVert) and v not in values:
                    values[v] = 0.0
        bm.normal_update()
        for v in bm.verts:
            value = values.get(v, 0.0)
            if value > 0.05 and v.normal.z > -0.35:
                v.co -= v.normal * dent * db.smoothstep(0.1, 0.9, value) * fade(v.co.x, v.co.y)
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    k.smooth(obj, 40)


def burns(m):
    for prefix, dent in DENT.items():
        for obj in objects([prefix]):
            dense = prefix in ("arm_tube", "cuff", "pod", "rim")
            burn(obj, m, dent, cut=not dense)


# --- The cracks, the dulled spheres, the broken bar, the dead eyes -------------------------------------------------

def crack_path(points, seed):
    """A crack's line (pixel middles) in the whole's coordinates, resampled every CRACK_STEP and jagged; points too near
    the pieces' edges are left out."""
    rng = random.Random(seed)
    pts = [(c + 0.5 - 72.0, 28.0 - (r + 0.5)) for c, r in points]
    dense = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        n = max(1, int(round(math.hypot(x1 - x0, y1 - y0) / CRACK_STEP)))
        dense += [(x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n) for i in range(n)]
    dense.append(pts[-1])
    out = [dense[0]]
    for i in range(1, len(dense) - 1):
        tx, ty = dense[i + 1][0] - dense[i - 1][0], dense[i + 1][1] - dense[i - 1][1]
        length = math.hypot(tx, ty) or 1.0
        o = rng.uniform(-CRACK_JAG, CRACK_JAG)
        out.append((dense[i][0] - ty / length * o, dense[i][1] + tx / length * o))
    out.append(dense[-1])
    return [p for p in out if fade(*p) > 0.6]


def strip(name, path, hit, width, lift, shift, mat):
    """A strip along a path (x, y) dropped onto a surface (hit: ray cast down), width across it (tapering to its ends),
    lifted along the surface's normal, moved shift towards the upper left."""
    verts, faces = [], []
    pts = []
    for x, y in path:
        h = hit(x - shift * 0.6, y + shift * 0.8)
        if h is not None:
            pts.append(h)
    if len(pts) < 2:
        return None
    n = len(pts)
    for i, (p, nrm) in enumerate(pts):
        t = (pts[min(i + 1, n - 1)][0] - pts[max(i - 1, 0)][0])
        t = (t - nrm * t.dot(nrm)).normalized()
        side = t.cross(nrm).normalized()
        w = width * (0.35 + 0.65 * min(1.0, i / 2.0, (n - 1 - i) / 2.0)) / 2
        verts += [p + nrm * lift + side * w, p + nrm * lift - side * w]
    for i in range(n - 1):
        faces.append((2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2))
    obj = k.mesh_object(name, verts, faces, mat)
    k.recalc_normals(obj)
    for poly in obj.data.polygons:      # facing up
        if poly.normal.z < 0:
            obj.data.flip_normals()
            break
    return k.smooth(obj, 60)


def cracks(m):
    seed = 10
    for target, lines in CRACKS.items():
        obj = bpy.data.objects[target]
        bpy.context.view_layer.update()
        hit = mk.surface([obj])
        for i, line in enumerate(lines):
            seed += 1
            path = crack_path(line, seed)
            strip(f"{target}_crack{i}_gap", path, hit, CRACK_GAP, 0.04, 0.0, m["core"])
            strip(f"{target}_crack{i}", path, hit, CRACK_EDGE, 0.08, 0.14, m["crack"])


def dull(m):
    """The spheres' glare and light band gone: their faces take the base."""
    for obj in objects(["sphere"]):
        if "crack" in obj.name:
            continue
        swap(obj, m["sphere_glare"], m["sphere"])
        swap(obj, m["sphere_mid"], m["sphere"])


def break_bar(m):
    """The canopy's frame bar broken: a gap cut out of it, its ends capped dark."""
    obj = bpy.data.objects["canopy_bar"]
    a, b = BAR_BREAK[0] - 72.0, BAR_BREAK[1] - 72.0
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    for x, no in ((a, (1, 0, 0)), (b, (-1, 0, 0))):
        res = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-5, plane_co=(x, 0, 0),
                                     plane_no=no)
    gone = [f for f in bm.faces if a < f.calc_center_median().x < b]
    bmesh.ops.delete(bm, geom=gone, context="FACES")
    for v in [v for v in bm.verts if not v.link_faces]:
        bm.verts.remove(v)
    rim = [e for e in bm.edges if e.is_boundary]
    char = mk.slot_of(obj, m["char"])
    if rim:
        filled = bmesh.ops.holes_fill(bm, edges=rim, sides=0)
        for f in filled["faces"]:
            f.material_index = char
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()


def eyes(m):
    """The eyes put out: the left lens dull dark red (its glint faint), the right one black."""
    left, right = bpy.data.objects["eye"], bpy.data.objects["eye_r"]
    swap(left, m["eye_rim"], m["char"])
    swap(left, m["eye"], m["eye_dead"])
    swap(left, m["eye_hot"], m["eye_dead_hot"])
    swap(right, m["eye_rim"], m["char"])
    swap(right, m["eye"], m["char"])
    swap(right, m["eye_hot"], m["eye_dead"])


# --- Build -----------------------------------------------------------------------------------------------------------

def build_whole():
    m = materials()
    whole, _ = db.build_whole(m)
    grilles(m)
    holes(m)
    burns(m)
    cracks(m)
    dull(m)
    break_bar(m)
    eyes(m)
    bpy.context.view_layer.update()
    whole = [o for o in mk.meshes() if len(o.data.polygons) > 0]
    return whole, m


def build():
    k.reset()
    options = k.args()
    whole, m = build_whole()
    print("whole damaged boss: %d triangles, %d objects" % (mk.triangles(whole), len(whole)))
    sheet = os.path.join(options["check"], "enemy_T.png") if "check" in options else None
    if sheet:
        mk.compare("whole damaged (T 115 3 119 121 9 125 above 153 41-47 163)", mk.coverage(whole, 144, 56),
                   db.whole_mask(sheet, WHOLE_CELLS))
    bpy.context.scene.view_settings.view_transform = "Standard"
    if "preview" in options:
        mk.preview(options["preview"] + "deli_boss_damaged_whole", whole, size=(144, 56), scale=8, distance=3.2)
    if "whole" in options:
        triangulate(whole)
        mk.export(whole, options["whole"])
    if options.get("only") != "none":
        db.export_pieces(whole, m, PIECES, options, sheet)


if __name__ == "__main__":
    build()
