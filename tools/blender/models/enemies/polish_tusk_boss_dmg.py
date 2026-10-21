"""The tusked boss damaged (models tusk_boss_162, 164, 168, 170, 200, 208, 240, 242, 244, 246): the dgr sprites the
game puts in ten pieces' places when the boss is hit hard (TYRIAN, TYRIAN X, HOLES, ASSASSIN; its linked pieces
switch together): 10 -> 162, 12 -> 164, 16 -> 168, 18 -> 170, 48 -> 200, 56 -> 208, 88 -> 240, 90 -> 242, 92 -> 244,
94 -> 246; 86, 126 and 130 switch to empty sprites (238, 278, 282), 124 and 132 (dgr 0) are taken away, the jaw 128
switches to 280, its own picture again (model tusk_boss_128); 14, 50, 54 and the core keep their sprites. models.cfg
(as before): model tusk_boss_<sprite> enemies/tusk_boss_<sprite>.glb origin; sprite 4 <sprite> tusk_boss_<sprite>
yaw=0; sprite 4 280 tusk_boss_128 yaw=0. Polished 2026-10-21; it replaces wave3_ao_boss.py (the old boss's relief
over the damaged pixels, pressed in: delete it, nothing else imports it) and wave3_ao_art.py's BOSS_DMG (only
wave3_ao_boss.py reads it).

The boss is polish_tusk_boss.py's (its builders imported, unchanged), built whole, damaged as the damaged sprites
draw it and cut into the same pieces at the same origins, so that a damaged piece meets its neighbours, damaged or
not: no surface moves within SEAM of the pieces' edges (the engines' dents fade out over SEAM_FADE; their faces are
cut along the edges first, so that the cut finds the intact surface there), the holes stay inside their pieces; only
the right wing's tear runs through two pieces (170 and 208), as the sprites' does.

What the damaged sprites draw differently, read pixel by pixel into DAMAGE below (the 120 x 112 picture's rows 0-75;
' ' empty in both, '.' as it was, '-' gone, 'c' burnt black, 's' scorched (four or more shades darker, or another
ramp), 't' darker, 'L' lighter):
- Both claws blown off with their tusks and hooks (the blocks with their panels and arms, the gold plates, the
  sleeves, the tusks and the hooks gone): torn grey scraps of the arms hang from the yokes' shields (columns 24-38 and
  83-97 of rows 57-75), the shields burnt (dark holes at columns 33-38 of rows 57-71 and columns 82-87 of rows 59-63).
- The right cable, the right wing's pod and block shot away and the wing torn off outside columns 104-107 (rows
  18-38), its torn end charred (columns 96-106 of rows 27-46).
- Holes burnt into both engines (columns 25-31 and 89-95 of rows 12-18), burns round them and on the left pylon
  (columns 36-39 of rows 22-27); the left wing's dark block charred and its wing scorched, a hole burnt by its rib
  (columns 18-21 of rows 35-39); the gold scorched dark brown.
How: the parts gone are taken away; the scraps are jagged grey plates (their plans the sprites' scraps) hanging down
under the shields, the tear a jagged cut, their walls charred; the holes are jagged wells sunk into the parts (the
sprites draw them black, not through), their walls and floors charred; the burns: the faces facing up in the burns'
boxes are cut finer and painted along smooth, ragged borders (the map blurred, with seeded noise): steel and the
glossy black charred black (the cuts' dark, one material fewer per piece) or scorched to the darkest grey, gold
charred to 0x11 or scorched to 0x13, red to its darkest; only the engines' round housings are pressed in where
charred (on the flat plates the dents broke up the shading).

Coordinates as in polish_tusk_boss.py, after its move onto the picture's axis: pixel (c, r) covers x c - 60..c - 59,
y 55 - r..56 - r.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes of the whole
and of each piece against enemy_4.png), --preview <prefix>, --only <model,...>, --whole <file.glb>, --stats 1.
"""
import math
import os
import random
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Vector, noise

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_tusk_boss as tb  # noqa: E402
from polish_tusk_boss import mk, k, db  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402

# The damaged pieces: model, sprite, the picture's column and row of its top left corner.
CELLS = [("tusk_boss_162", 162, 0, 0), ("tusk_boss_164", 164, 24, 0), ("tusk_boss_168", 168, 72, 0),
         ("tusk_boss_170", 170, 96, 0), ("tusk_boss_200", 200, 0, 28), ("tusk_boss_208", 208, 96, 28),
         ("tusk_boss_240", 240, 24, 56), ("tusk_boss_242", 242, 48, 56), ("tusk_boss_244", 244, 72, 56),
         ("tusk_boss_246", 246, 96, 56)]
PIECES = [(name, sprite, tb.box_of(col, row)) for name, sprite, col, row in CELLS]
# The whole damaged picture (for the silhouette check): the damaged sprites, the four that keep theirs (14, 50, 54
# and the core), the jaw's picture (280 is 128's); 238, 278 and 282 are empty, 124 and 132 taken away.
WHOLE_LAYOUT = [[162, 164, 14, 168, 170], [200, 50, 1, 54, 208], [0, 240, 242, 244, 246], [0, 0, 128, 0, 0]]
SEAMS_X = (-36.0, -12.0, 12.0, 36.0)
SEAMS_Y = (28.0, 0.0, -28.0)
SEAM, SEAM_FADE = 0.25, 1.4


def XF(c):
    """The left edge of the picture's column c in the whole's (final) coordinates."""
    return c - 60.0


def YF(r):
    return 56.0 - r


# --- The damage map ---------------------------------------------------------------------------------------------------
# The 120 x 112 picture's rows 0-75 (below them only the claws' tusks and hooks, gone): ' ' empty in both, '.' as it
# was, '-' gone, '+' new, 'c' burnt black (two shades or less, or the gold's shadow turned to its darkest), 's'
# scorched (four or more shades darker, or another ramp), 't' darker, 'L' lighter (torn edges).
DAMAGE = [
'',
'',
'',
'                     ....                                                                       ....',
'                     ......                                                                   ......',
'                     ........                                                               ........',
'                   ............                        ...........                        .ccs.......-',
'                   ..............                    ...............                    ...scs.......s',
'              .....................                 .................                 .....ttt.......s-----',
'            .........................              ...................              ......t.tt........-------',
'           .........tttt...............           .....................           ........ct.t........--------',
'          .....   .tttstt................         .....................         ......t...cc.t........-   -----',
'         ....      tttccstt................       .....................       ........t.......t.......      ----',
'        ....        ttcccct.................      .....................      .......ttc.......ct.....        ----',
'       ....          ttccttccL........cct...    .........................    .......ttccccccctcst...          ----',
'      ....           t.csccccL........ccct..  .............................  .......ttcccccctttss...           ----',
'      ...            tttcccccL........ccct.. ............................... .......ttccstcctt..tt..            ---',
'     ....            ttccctccL........ccct.. ............................... .......ttcctccctt...t..            ----',
'     ...              ctttc...............................................................sttt.....              ---',
'    ....               ..................................................................tttt.....               ---',
'    ....                .........................................................................                ----',
'    .....                   .................................................................                   -----',
'    .......                  .......t.......................................................                  -------',
'    .........                 .....tc......................................................                 ---------',
'     ..........                ....cct....................................................                -----------',
'     ............               ....ct...................................................               ------------',
'     ..............              ..c....................................................              --------------',
'     ............ct..             .c...................................................             ..--------------',
'     ...........tcsct..            ...................................................            ....c-------------',
'     ............scss....           .................................................           .s.....c------------',
'     ............tss.L.....          ...............................................          ..sc.....c------------',
'     .....ct......LLL........        ...............................................        ....tc.....c------------',
'     .....cst..................      ...............................................      ......scc...ccc-----------',
'     .....ccct...................    ...............................................    ........cscc.ccccc----------',
'     .....cccct..LL.L............................................................................sccccccccc---------',
'      ....tcccc..LcctLL...........................................................................ccccccccs--------',
'       ...tcccc..LccttL...........................................................................cccc.ccss-------',
'        .....tt..tcccttt..........................................................................cccssccc.------',
'               ..tcccctt..........................................................................cc..scc.',
'                .tcctttt.........................................................................ccc..sc.',
'                 .tttLLt.........................................................................ccc....',
'                  .tt.L..........................................................................ccc...',
'                   .c..t.........................................................................ccc..',
'                    ...t........................................................................cccc.',
'                     .t.........................................................................ccc.',
'                      .t........................................................................ccs',
'                       ...........................................................................',
'                        .........................................................................',
'                         .......................................................................',
'                          .....................................................................',
'                           ...................................................................',
'                            .................................................................',
'                             ...............................................................',
'                             ...............................................................',
'                             ...............................................................',
'                             ...............................................................',
'                             ..LLcc.tttttts....t...............................cc.ttc.cct...',
'                 -------      LL...tss.ssss...cc..............................tcc..tcc.ss..      -------',
'                ---------.....L...tccc.ssss..tcL..............................stt..ttttss....------------',
'                --------ctc.ttt..tscccsttsc...LL..............................t.c....ttscc..Lt-----------',
'              ----------cL.LLtt...tscsstL.t...L...............................t.cc..tttccc...t-------------',
'              ----------t.Lttttt..tststLLt....L...............................tttc.tcctccc..tt-------------',
'              ----------ct.sst.ss.tLLLLtt.....................................cccctcct.scccctc-------------',
'              ----------ctc--ssss.tt.LLttt..     .......................     .ccttcct.tstccsssc------------',
'              -----------cc--s.ttt.t..tttt.      .......................      .ct..ccsttsssttttc-----------',
'              -----------cc-ssLttt...ttts.       .......................       .t..tsttcccsssstsc----------',
'              ------------ssts.tsctttssst.       .......................       ....sstccsss--cssc----------',
'              --------------tLss--s.sccst.       .......................       ..ttsttctss----ctc----------',
'              --------------sts---t.cccct.        .....................        ..tcs.tctssccc--------------',
'              ------------------tcL..ccst.         ...................         ..tsc..cttstLc--------------',
'                ---------------tLLL..ccct.         ...................         ..ts..L..tctLc------------',
'                --------------tL++  ..ttt.          .................          ..tc..+   .t.-------------',
'               --------------LL  ++++.....          .................          .....+++   LLcc------------',
'               ---------------                       ...............               ++++   +LLc------------',
'               ---------------                        .............                 ++     .cc------------',
'               ---------------                   .    .............    .                   ---------------',
]


def grid(values):
    """The map as an array (112 x 120): each pixel's value from values (class -> value)."""
    g = np.zeros((112, 120))
    for r, line in enumerate(DAMAGE):
        for c, ch in enumerate(line):
            g[r, c] = values.get(ch, 0.0)
    return g


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
    """A map over the picture (values at the pixels' middles: pixel (c, r) at x = c - 59.5, y = 55.5 - r), sampled
    between them."""

    def __init__(self, a):
        self.a = a

    def __call__(self, x, y):
        u, v = x + 59.5, 55.5 - y
        c0, r0 = int(math.floor(u)), int(math.floor(v))
        fu, fv = u - c0, v - r0

        def at(r, c):
            return self.a[r, c] if 0 <= r < 112 and 0 <= c < 120 else 0.0
        return ((1 - fu) * (1 - fv) * at(r0, c0) + fu * (1 - fv) * at(r0, c0 + 1) +
                (1 - fu) * fv * at(r0 + 1, c0) + fu * fv * at(r0 + 1, c0 + 1))


# The burns: black, scorched, darker; where parts were torn away, charred. Blurred a little, then made ragged.
BURN = Field(blur(grid({"c": 1.0, "s": 0.75, "t": 0.42, "-": 0.9}), 0.7))
CHAR, SCORCH = 0.46, 0.2         # charred above this, scorched above that
GRID = 1.4                       # how fine the burnt faces are cut
# The burnt objects (name prefixes) and how far their burns are pressed in (only the engines' round housings: on the
# flat plates the dents broke up the shading; the holes there are cut).
DENT = {"wing": 0.0, "yoke": 0.0, "engine": 0.35, "pylon": 0.0, "tip_block": 0.0, "collar": 0.0,
        "side_plate": 0.0, "root": 0.0, "floor": 0.0, "hull": 0.0, "cable": 0.0, "tip_pod": 0.0}


def ragged(x, y, value):
    """The burn field made ragged along its borders (seeded noise: the same every run)."""
    if value <= 0.0:
        return value
    n = 0.13 * noise.noise(Vector((x * 0.7, y * 0.7, 4.1))) + 0.06 * noise.noise(Vector((x * 2.1, y * 2.1, 7.7)))
    return value + n * min(1.0, value * 4.0)


def fade(x, y):
    """1 away from the pieces' edges, 0 within SEAM of them (nothing moves there)."""
    d = min([abs(x - s) for s in SEAMS_X] + [abs(y - s) for s in SEAMS_Y])
    return tb.smoothstep(SEAM, SEAM_FADE, d)


# --- What is shot away ---------------------------------------------------------------------------------------------
# Gone with the claws (both sides): the blocks, their panels and frames, the gold plates, the sleeves, tusks, hooks;
# gone on the right: the cable, the wing tip's pod and block.
GONE = ["claw", "claw_frame0", "claw_frame1", "claw_panel0", "claw_panel1", "claw_gold", "sleeve", "tusk", "hook",
        "claw_arm"]
GONE_RIGHT = ["cable_r", "tip_pod_r", "tip_block_r"]
# What is left of the claws' arms: torn scraps of grey plate hanging from the yokes' shields, under them (plans as
# the damaged sprites draw them, jagged; their top).
SCRAPS = {"scrap": [(25.0, 57.8), (31.6, 57.8), (33.6, 62.0), (35.8, 64.4), (35.6, 67.4), (37.4, 69.0), (37.6, 71.8),
                    (33.6, 72.8), (30.6, 72.4), (29.6, 71.0), (31.0, 69.2), (28.4, 68.6), (27.6, 67.0), (26.0, 66.6),
                    (24.4, 65.8), (23.8, 62.8)],
          "scrap_r": [(88.0, 57.0), (91.6, 57.2), (94.2, 59.0), (94.8, 62.6), (96.6, 64.6), (97.0, 67.8),
                      (94.6, 68.2), (93.2, 72.0), (93.6, 74.6), (90.4, 74.8), (87.2, 73.8), (84.8, 75.0),
                      (82.8, 72.6), (83.6, 68.2), (85.0, 65.6), (87.4, 62.4)]}
SCRAP_JAG, SCRAP_TOP, SCRAP_HANG = 0.35, tb.ZC + 3.0, 0.22    # (hanging: how much they fall per row down)
# The right wing torn off outside this line (column, row from its top down; jagged).
TEAR = [(104.6, 18.0), (104.2, 26.0), (103.8, 28.6), (104.8, 31.2), (105.8, 32.8), (106.6, 34.2), (107.0, 36.4),
        (106.8, 38.4), (109.0, 41.0), (112.0, 46.0)]
TEAR_JAG = 0.3
# The holes blasted in: (object, centre column, row, half-width, half-height, how deep, seed); the sprites draw them
# burnt black, not through.
HOLES = [("engine", 28.2, 14.6, 2.9, 2.6, 2.4, 1), ("engine_r", 91.8, 15.0, 3.4, 2.0, 2.4, 2),
         ("yoke", 34.4, 58.8, 1.5, 1.3, 1.1, 3), ("yoke", 36.6, 67.8, 1.5, 2.2, 1.1, 4),
         ("yoke_r", 84.4, 60.8, 1.7, 1.9, 1.1, 5), ("wing_rib", 19.6, 37.0, 1.7, 1.9, 1.3, 6)]
HOLE_JAG = 0.28


def materials():
    m = tb.materials()

    def mat(name, index, metallic=0.2, roughness=0.6):
        return k.material("tuskd_" + name, palette=index, metallic=metallic, roughness=roughness)
    m.update({
        "char": m["core"],             # the steel burnt black: the cuts' dark (one material fewer per piece)
        "char_gold": mat("char_gold", 0x11, 0.1, 0.8),
        "scorch_gold": mat("scorch_gold", 0x13, 0.25, 0.6),
        "scrap": mat("scrap", 0x03, 0.15, 0.75),           # the torn plates' dull dark grey (the sprites' 0x01-0x05)
        "scrap_lit": mat("scrap_lit", 0x05, 0.2, 0.6),
    })
    return m


def objects(names):
    return [bpy.data.objects[n] for n in names if n in bpy.data.objects]


def prefixed(prefixes):
    """The whole's meshes whose names (without a .001 suffix) start with one of the prefixes."""
    return [o for o in mk.meshes() if o.name.split(".")[0].startswith(tuple(prefixes))]


def jagged_ring(c, r, rx, ry, seed, n=14, jag=HOLE_JAG):
    rng = random.Random(seed)
    x0, y0 = XF(c), YF(r)
    return [(x0 + rx * (1.0 + rng.uniform(-jag, jag)) * math.cos(2 * math.pi * i / n),
             y0 + ry * (1.0 + rng.uniform(-jag, jag)) * math.sin(2 * math.pi * i / n)) for i in range(n)]


def jagged_path(points, seed, jag, step=0.9):
    """A path (pixel edges) resampled every step and jagged sideways (seeded)."""
    rng = random.Random(seed)
    pts = [(XF(c), YF(r)) for c, r in points]
    dense = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        n = max(1, int(round(math.hypot(x1 - x0, y1 - y0) / step)))
        dense += [(x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n) for i in range(n)]
    dense.append(pts[-1])
    out = []
    for i, (x, y) in enumerate(dense):
        a, b = dense[max(i - 1, 0)], dense[min(i + 1, len(dense) - 1)]
        tx, ty = b[0] - a[0], b[1] - a[1]
        length = math.hypot(tx, ty) or 1.0
        o = rng.uniform(-jag, jag) if 0 < i < len(dense) - 1 else 0.0
        out.append((x - ty / length * o, y + tx / length * o))
    return out


def shoot_away(m):
    for name in GONE:
        for obj in objects([name, name + "_r"]):
            tb.remove(obj)
    for obj in objects(GONE_RIGHT):
        tb.remove(obj)


def scraps(m):
    """The torn scraps of the claws' arms: jagged grey plates under the shields, their torn walls charred."""
    for i, (name, outline) in enumerate(sorted(SCRAPS.items())):
        pts = tb.ccw(jagged_path(outline + outline[:1], 20 + i, SCRAP_JAG, step=0.8)[:-1])
        y_top = max(p[1] for p in pts)
        body = tb.plate(name, pts, [lambda x, y: SCRAP_TOP - SCRAP_HANG * (y_top - y)], m["scrap"], bevel=0.3,
                        segments=2, bottom=tb.ZC - 3.6)
        mk.paint(body, lambda c, n: m["scrap_lit"] if n.dot(Vector((-0.55, 0.45, 0.7)).normalized()) > 0.78 else
                 m["scrap"] if n.z > 0.5 else m["char"])


def tear_wing(m):
    """The right wing torn off outside the tear line: its plates cut along it, the torn walls charred."""
    path = jagged_path(TEAR, 31, TEAR_JAG, step=0.8)
    outline = tb.ccw(path + [(XF(130.0), YF(56.0)), (XF(130.0), YF(18.0))])
    for name in ("wing_r", "wing_rib_r", "wing_low_r"):
        obj = bpy.data.objects[name]
        cutter = mk.prism(name + "_tear", outline, -20.0, 30.0, m["char"])
        mk.boolean(obj, cutter, "DIFFERENCE")
        mk.cleanup(obj, dissolve=0.0)
        tb.ngons_to_triangles(obj)
        k.smooth(obj, 35)


def holes(m):
    """The holes blasted into the engines, the yokes' feet and the left wing: jagged, their walls charred."""
    for name, c, r, rx, ry, depth, seed in HOLES:
        obj = bpy.data.objects[name]
        ring = mk.chaikin(jagged_ring(c, r, rx, ry, seed), 1)
        bpy.context.view_layer.update()
        hit = mk.surface([obj])
        h = hit(XF(c), YF(r))
        top = h[0].z if h else 10.0
        z0 = top - depth if depth is not None else -20.0
        cutter = mk.prism(f"{name}_hole{seed}", tb.ccw(ring), z0, 40.0, m["char"])
        mk.boolean(obj, cutter, "DIFFERENCE")
        mk.cleanup(obj, dissolve=0.0)
        tb.ngons_to_triangles(obj)


# --- The burns ---------------------------------------------------------------------------------------------------
BOXES = None


def burn_regions():
    """The burns' boxes (x0, x1, y0, y1): the bounds of each connected patch of the field (4-connected pixels over
    0.04), a pixel wider."""
    mask = BURN.a > 0.04
    seen = np.zeros_like(mask)
    boxes = []
    for r0 in range(112):
        for c0 in range(120):
            if not mask[r0, c0] or seen[r0, c0]:
                continue
            stack, cells = [(r0, c0)], []
            seen[r0, c0] = True
            while stack:
                r, c = stack.pop()
                cells.append((r, c))
                for rr, cc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                    if 0 <= rr < 112 and 0 <= cc < 120 and mask[rr, cc] and not seen[rr, cc]:
                        seen[rr, cc] = True
                        stack.append((rr, cc))
            rs = [r for r, _ in cells]
            cs = [c for _, c in cells]
            boxes.append((min(cs) - 60.0 - 1.0, max(cs) - 59.0 + 1.0, 56.0 - max(rs) - 2.0, 56.0 - min(rs) + 1.0))
    return boxes


def refine(bm, step, skip=()):
    """Cuts the faces facing up in the burns' boxes until their edges are under step (edges halved, up to four times),
    so that the burns can be painted and pressed in along smooth borders (polish_deli_boss_dmg.py's)."""
    global BOXES
    if BOXES is None:
        BOXES = burn_regions()
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
            c = f.calc_center_median()
            if max([BURN(c.x, c.y)] + [BURN(v.co.x, v.co.y) for v in f.verts]) < 0.02:
                continue
            for e in f.edges:
                if e.calc_length() > step:
                    edges.add(e)
        if not edges:
            break
        bmesh.ops.subdivide_edges(bm, edges=list(edges), cuts=1, use_grid_fill=False)
        bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3])


FAMILY = {"gold": ("char_gold", "scorch_gold"), "brown": ("char_gold", "scorch_gold"),
          "steel": ("char", "steel_dark"), "black": ("char", "steel_dark"), "red": ("char", "red_dark")}


def burn(obj, m, dent, cut=True):
    """Paints the burns on an object (its faces facing up, by the family of their material: gold chars dark brown,
    steel black), along smooth ragged borders, and presses the charred parts in (not near the pieces' edges)."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    names = [mm.name if mm is not None else "" for mm in obj.data.materials]
    skip = {i for i, n in enumerate(names) if n == m["core"].name or n.startswith("tuskd_")}
    if cut:
        refine(bm, GRID, skip)
    else:
        bmesh.ops.triangulate(bm, faces=bm.faces[:])
    values = {v: ragged(v.co.x, v.co.y, BURN(v.co.x, v.co.y)) for v in bm.verts}
    for threshold in (SCORCH, CHAR):
        mk.split_along(bm, values, threshold)
        for v in bm.verts:
            values.setdefault(v, threshold)
    bm.normal_update()
    slots = {}

    def slot(name):
        if name not in slots:
            slots[name] = mk.slot_of(obj, m[name])
        return slots[name]
    for f in bm.faces:
        if f.material_index in skip or f.normal.z < -0.35:
            continue
        name = names[f.material_index] if f.material_index < len(names) else ""
        family = next((fam for key, fam in FAMILY.items() if name.startswith("tusk_" + key)), None)
        if family is None:
            continue
        value = sum(values[v] for v in f.verts) / len(f.verts)
        if value > CHAR:
            f.material_index = slot(family[0])
        elif value > SCORCH:
            f.material_index = slot(family[1])
    if dent:
        for co, no in [((s, 0, 0), (1, 0, 0)) for s in SEAMS_X] + [((0, s, 0), (0, 1, 0)) for s in SEAMS_Y]:
            res = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-5, plane_co=co,
                                         plane_no=no)
            for v in res["geom_cut"]:
                if isinstance(v, bmesh.types.BMVert) and v not in values:
                    values[v] = 0.0
        bm.normal_update()
        for v in bm.verts:
            value = values.get(v, 0.0)
            if value > CHAR and v.normal.z > -0.35:
                v.co -= v.normal * dent * tb.smoothstep(CHAR, 0.95, value) * fade(v.co.x, v.co.y)
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    k.smooth(obj, 40)


def burns(m):
    for prefix, dent in DENT.items():
        for obj in prefixed([prefix]):
            if obj.name.startswith("hull") or obj.name.startswith("cable") or obj.name.startswith("tip_pod"):
                burn(obj, m, 0.0, cut=False)
            else:
                burn(obj, m, dent, cut=True)


# --- Build -----------------------------------------------------------------------------------------------------------

def build_whole():
    m = materials()
    whole, _ = tb.build_whole(m)
    shoot_away(m)
    scraps(m)
    tear_wing(m)
    holes(m)
    burns(m)
    bpy.context.view_layer.update()
    whole = [o for o in mk.meshes() if len(o.data.polygons) > 0]
    return whole, m


def build():
    k.reset()
    options = k.args()
    whole, m = build_whole()
    print("whole damaged boss: %d triangles, %d objects" % (mk.triangles(whole), len(whole)))
    sheet = os.path.join(options["check"], "enemy_4.png") if "check" in options else None
    if sheet:
        mk.compare("whole damaged (4 162 164 14 168 170 / 200 50 1 54 208 / - 240-246 / jaw)",
                   mk.coverage(whole, 120, 112), tb.whole_mask(sheet, WHOLE_LAYOUT))
    bpy.context.scene.view_settings.view_transform = "Standard"
    if "preview" in options:
        mk.preview(options["preview"] + "tusk_boss_damaged_whole", whole, size=(120, 112), scale=8, distance=3.2)
    if "whole" in options:
        triangulate(whole)
        mk.export(whole, options["whole"])
    if options.get("only") != "none":
        db.export_pieces(whole, m, PIECES, options, sheet, label="4")


if __name__ == "__main__":
    build()
