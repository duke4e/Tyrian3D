"""TORM's big beetle on the top layer, eleven sprites of sheet H that TORM's custom events put together (episode 2,
enemy 0 with the event's sprite, armour 20 the tip and the segments, 60 the body's sides, 40 its middle; 14 beetles,
t 0 to 5790, always the same layout), polished (2026-10-21, round 26; it replaces wave3_ad_torm.py, the beetle of
reliefs painted pixel by pixel). models.cfg: the model lines torm_beetle_tip, _seg1_l, _seg1_r, _seg2_l, _seg2_r, _tl,
_tm, _tr, _bl, _bm, _br (origin) and the sprite lines h 155, 192, 194, 230, 232, 159, 161, 163, 197, 199, 201 (yaw=0)
are unchanged.

The events (event 51: a custom enemy on the top layer, its sprite from shape bank 12, sheet H): 199 at (x, y) with link
L, 197 and 201 at x - 24 and x + 24, 159 161 163 at (x - 24 .. x + 24, y - 24) with link L - 1, 230 232 at (x - 12,
x + 12; y - 40) with L - 2, 192 194 at (x -+ 12, y - 60) with L - 3, 155 at (x, y - 80) with L - 4, each event drawn
over the ones before it. At t + 1 the head's link becomes the body's (event 39): the six body pieces move as one; the
two segments and the tip get the same moves 2, 4 and 6 ticks later (events 20 and 27), so they sway after the head
like a tail, each a link of its own: each segment is whole in its two pieces and the tip on its own. Enemy 0 has one
frame (ani 1), no damaged look (dgr 0) and no guns; the head leaves enemy 396 when it is destroyed; each piece can be
shot away on its own. Nothing else shows these sprites (no episode 6 level takes TORM's waves: GREY MOON takes its boss,
ROOST its map and ground); they are no other sprites' pixels mirrored, turned or in other ramps (twins3 on every
sheet); 159 / 163 and 197 / 201 are near mirror images of each other (the body is its own mirror image about the
picture's column 36), 192 / 194 and 230 / 232 the halves of segments that are their own mirror images about column 37,
not mirrors of each other.

As the eleven sprites draw it (the 72 x 108 picture the events make; no upscale exists: the sheet's pixels): a big
beetle, its head down the screen, in the steel greys of ramp 6 and the greens of ramp 2. At its tail (155) a ribbed
grey spike pointing up the screen, light bands across its lower half, its base under the first segment. Two body
segments (192 194, 230 232, the second bigger), each a green ribbed shell along the middle, a diamond at its rear and
two lobes at its front, with two big silver plates on its sides (bulging shoulders whose outer ends hang down the
screen; the first segment's meet across its back in a strap); each segment's rear drawn over the front of the one
behind it. The body (159 161 163 above 197 199 201): a grey thorax with a pale ring round a grey boss on its back,
glossy green bulbs at its sides, two thin feelers from its rear corners out over the second segment, hooking down at
their tips, two spines from its rear edge up the screen; two long sickle legs from behind the bulbs, out, round and
down to points level with the snout (the bottom row draws their elbows a little further out than the top row); the
head, darker, two red eyes in dark sockets at its top corners, a green nose shield with a pale V and a green mark under
it, two green mouth claws a side hanging beside it, and the long snout tapering to its point, a light ridge down it.

Built as such a creature, whole in four groups (the tip, each segment, the body), each cut along its sprites' edges
into its pieces (polish_coral_manta.cut: the caps the part's inside, the uncut normals kept), each piece moved so that
its sprite's middle is its origin (drawn at their own origins on the top layer they meet again):
- The plates, shells, the tip and the body's core are solids over a region (Solid): a triangular grid cut along a
  contour, its top and flat underside meeting along it, the top rounded down to the rim over a pixel or two, every
  vertex given the analytic normal of the heights. The regions are the sprites' pixels (MAPS: a class map of each
  group, the dark outline pixels the class of their nearest coloured pixel) blurred, so that the outlines follow the
  sprites; the core's outline is traced (CORE_OUTLINE, symmetric). The heights are smooth functions, not the pixels.
- The tip: round sections along y over its sprite's outline, ribbed across its lower half, low at its base under the
  first segment's lip.
- Each segment: a body surface (rising from its front, tucked under the next segment or the thorax, to a lip at its
  rear over the segment behind or the tip; ribbed down its spine; its belly parted into two lobes), the green shell
  showing it where the sprite draws green (reaching a pixel under the plates), the plates lying PLATE_LIFT over it
  where it draws grey, swelling towards their shoulders and drooping at their outer ends, their edges rounded and
  falling straight to their undersides; the first segment's strap a shade darker.
- The body: the core one solid, the thorax and the head domes joined by smooth maxima (the neck the crease between
  them), the snout a ridge tapering to its point (grooves along its sides, a crest down it), brows over the sockets,
  the claws' bases, cheek grooves, the nose shield and the mark raised, the V two pale strokes laid on the shield
  (VEE), two small pits on the snout (the sprite's dark marks); the ring a lathe (a pale rim round a groove and a
  domed boss); the bulbs icospheres; the legs, feelers, spines and claws tubes along traced paths (Catmull-Rom), their
  sections lying flat (the legs' forearms lens-shaped blades, a joint at the elbow), the right ones the left ones
  mirrored about the axis; the eyes small glowing lenses.
- Painted in bands of the sprite's palette indices by the light each face gets (light_value: facing the sun and up;
  a shade or two lighter than the sprite's, as the slanted camera sees them darker), split along smooth contours:
  steel 0x65-0x6e, green 0x23-0x2b; the nose's V 0x2d, the sockets 0x61; the eyes 0x75 and 0x78 glowing (0.55, 0.65),
  the bulbs' brightest band 0x2c glowing a little (0.18).
Heights: the pieces stand from z 0.55 (the tip's underside) to 10.6 (the ring), drawn at their own origins (models.cfg
origin) on the top layer; the anterior parts stand over the posterior ones where the sprites overlap, so the game
camera sees them stacked as the sprites are drawn. Every mesh is triangulated before the export (polish_k_pod
.triangulate): the same output every run, with and without --check.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up; the whole beetle's origin is the
picture's middle (column 36, row 54): column c is x = c + 0.5 - 36, row r is y = 53.5 - r. The body and the tip are
symmetric about x 0.5 (AXIS), the segments about x 1.5 (SEG_AXIS). The pieces' origins (their sprites' middles): 155
(0, 40); 192, 194 (-12, 20), (12, 20); 230, 232 (-12, 0), (12, 0); 159, 161, 163 (-24, -16), (0, -16), (24, -16); 197,
199, 201 (-24, -40), (0, -40), (24, -40). The body's rows meet at y -26 (197-201 are drawn over the last four rows of
159-163; --check compares 159-163 above them).

Replaces wave3_ad_torm.py (all of it: delete it; nothing imports it) and wave3_ad_art.py's TORM_TIP, TORM_SEG1,
TORM_SEG2, TORM_BODY and TORM (only wave3_ad_torm.py reads them). wave3_ad_kit.py stays (wave3_ad.py, wave3_ad_wall.py
and wave3_ad_fall.py use it); its grouped() objects (GROUPS, _render_whole) were the beetle's only.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each piece's silhouette
against its sprite in enemy_H.png), --preview <prefix> (each group's whole: top and 3/4 views; with --pieces 1 each
piece's too), --only <name,...>, --stats 1 (each piece's largest parts).
"""
import math
import os
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_deli_boss import join, drop_unused  # noqa: E402
from polish_coral_manta import cut, split_contour  # noqa: E402
from polish_orb_red import band_split, icosphere  # noqa: E402

LIGHT = Vector((-0.6, 0.6, 1.0)).normalized()   # towards the game's sun
FLAT = LIGHT.z
GRID = 0.5
AXIS = 0.5            # the body's and the tip's mirror axis (the middle of the picture's column 36)
SEG_AXIS = 1.5        # the segments' (column 37)

# --- The sprites' pixels -----------------------------------------------------------------------------------------
# Class maps of the four groups the events put together, one character a pixel (the 72 x 108 picture's rows and
# columns; each map's top left given): t the tip; p a segment's grey plates, g its green shell; in the body c the
# thorax, head and snout, e the eyes, n the green marks on the head, b the bulbs, l the legs, f the feelers, s the
# spines, m the mouth claws. The dark outline pixels are the class of the nearest coloured pixel.
MAPS = {
    "tip": (0, 24, [
        "............t...........", "...........ttt..........", "...........ttt..........", "..........ttttt.........",
        "..........ttttt.........", "..........ttttt.........", ".........ttttttt........", ".........ttttttt........",
        ".........ttttttt........", "........ttttttttt.......", "........ttttttttt.......", ".......ttttttttttt......",
        ".......ttttttttttt......", "......ttttttttttttt.....", "......ttttttttttttt.....", ".....ttttttttttttttt....",
        "....ttttttttttttttttt...", "....ttttttttttttttttt...", "...ttttttttttttttttttt..", "...ttttttttttttttttttt..",
        "...ttttttttttttttttttt..", "...ttttttttttttttttttt..", "...ttttttttttttttttttt..", "...ttttttttttttttttttt..",
        "...ttttttttttttttttttt..", "....ttttttttttttttttt...", ".....ttttt....tttttt....", "......ttt......tttt.....",
    ]),
    "seg1": (20, 12, [
        "................................................", "........................ggg.....................",
        "......................ggggggg...................", ".....................ggggggggg..................",
        "................ppppgggggggggggpppp.............", "..............ppppppgggggggggggpppppp...........",
        "............pppppppgggggggggggggppppppp.........", "...........pppppppgggggggggggggggppppppp........",
        "..........pppppppgggggggggggggggggppppppp.......", ".........pppppppgggggggggggggggggggppppppp......",
        "........pppppppppgggggggggggggggggppppppppp.....", ".......pppppppppppgggggggggggggggppppppppppp....",
        ".......pppppppppppppppgggggggppppppppppppppp....", "......pppppppppppppppppgggggppppppppppppppppp...",
        "......ppppppppppppppppppppppppppppppppppppppp...", "......ppppppppppppppppppppppppppppppppppppppp...",
        "......ppppppppppppppppppppppppppppppppppppppp...", "......ppppppppppppppppppppppppppppppppppppppp...",
        "......pppppppppppppppppgggggppppppppppppppppp...", ".......pppppppppppppgggggggggggppppppppppppp....",
        "........ppppppppppgggggggggggggggpppppppppp.....", ".............pppgggggggggggggggggggppp..........",
        ".............ggggggggggggggggggggggggg..........", "............ggggggggggggggggggggggggggg.........",
        "............ggggggggggggggggggggggggggg.........", ".............ggggggggggggggggggggggggg..........",
        "..............ggggggggg.....ggggggggg...........", "................ggggg.........ggggg.............",
    ]),
    "seg2": (40, 12, [
        ".......................gggg.....................", "....................ggggggggggg.................",
        "..................ggggggggggggggg...............", ".................ggggggggggggggggg..............",
        "............ppppgggggggggggggggggggpppp.........", "..........ppppppgggggggggggggggggggpppppp.......",
        "........pppppppgggggggggggggggggggggppppppp.....", ".......pppppppgggggggggggggggggggggggppppppp....",
        "......pppppppgggggggggggggggggggggggggppppppp...", ".....pppppppgggggggggggggggggggggggggggppppppp..",
        "....pppppppppgggggggggggggggggggggggggppppppppp.", "...pppppppppppgggggggggggggggggggggggppppppppppp",
        "...pppppppppppppppgggggggggggggggppppppppppppppp", "..pppppppppppppppppgggggggggggggpppppppppppppppp",
        "..ppppppppppppppppppgggggggggggppppppppppppppppp", "..ppppppppppppppppppgggggggggggppppppppppppppppp",
        "..ppppppppppppppppppgggggggggggppppppppppppppppp", "..ppppppppppppppppppgggggggggggppppppppppppppppp",
        "..pppppppppppppppppgggggggggggggpppppppppppppppp", "...pppppppppppppgggggggggggggggggggppppppppppppp",
        "....ppppppppppgggggggggggggggggggggggpppppppppp.", ".........pppgggggggggggggggggggggggggggppp......",
        ".........ggggggggggggggggggggggggggggggggg......", "........ggggggggggggggggggggggggggggggggggg.....",
        "........ggggggggggggggggggggggggggggggggggg.....", ".........ggggggggggggggggggggggggggggggggg......",
        "..........ggggggggg.....gggg....ggggggggg.......", "............ggggg........gg.......ggggg.........",
    ]),
    "body": (56, 0, [
        "........................................................................",
        ".............................ss...........ss............................",
        "...........ffffffffffff......sss.........sss......ffffffffffff..........",
        ".........ffffffffffffffff.....sss.......sss.....ffffffffffffffff........",
        "........fffffffffffffffffff....sss.....sss....fffffffffffffffffff.......",
        ".......ffff.......ffffffffff...ssss...ssss...ffffffffff.......ffff......",
        ".......ff............ffffffff...ssss.ssss...ffffffff............ff......",
        ".......................fffffff..ssss.ssss..fffffff......................",
        "........................llcccccccccccccccccccccll.......................",
        "............llllllll.....ccccccccccccccccccccccc.....llllllll...........",
        "...........llllllllll....ccccccccccccccccccccccc....llllllllll..........",
        "...........lllllllllll...bbcccccccccccccccccccbb...lllllllllll..........",
        "..........lllllllllllllbbbbcccccccccccccccccccbbbblllllllllllll.........",
        "..........lllllllllllllbbbbcccccccccccccccccccbbbblllllllllllll.........",
        "..........llllllllllllllbbbbcccccccccccccccccbbbbllllllllllllll.........",
        ".........lllllllllllllllbbbbcccccccccccccccccbbbblllllllllllllll........",
        ".........lllllllllllllllbbbbbcccccccccccccccbbbbblllllllllllllll........",
        ".........llllllll...lllbbbbbbcccccccccccccccbbbbbblll...llllllll........",
        "........llllllll.....bbbbbbbbcccccccccccccccbbbbbbbb.....llllllll.......",
        "........lllllll......bbbbbbbcccccccccccccccccbbbbbbb......lllllll.......",
        ".......lllllll.......bbbbbbbcccccccccccccccccbbbbbbb.......lllllll......",
        ".......llllll.........bbbbbbccccccccccccccccccbbbbb.........llllll......",
        ".......lllll............ccccccccccccccccccccccccc............lllll......",
        "......llllll............ccccccccnncccnncccccccccc............llllll.....",
        "...llllllll..........mmcccceeeeccccccccccceeecccccmm..........llllllll..",
        "...llllllll.........mmmcccccceeeccccccccceeeecccccmmm.........llllllll..",
        "...lllllll..........mmmmccccccecccccccccccccccccccmmm..........lllllll..",
        "...lllllll.........mmmmmccccccccccnnnccccccccccccmmmmm.........lllllll..",
        "....llllll.........mmmmmcccccccccnnnnncccccccccccmmmmm.........llllll...",
        "....llllll........mmmm..mmmccccccnnnnnccccccccmmm..mmmm........llllll...",
        "....llllll........mmm...mmmmmccccnnnnnccccccmmmmm...mmm........llllll...",
        ".....lllll........mmm...mmmm.ccccnnnnnnccccc.mmmm...mmm........lllll....",
        ".....lllll........mmm...mmm..ccccnnnnncccccc..mmm...mmm........lllll....",
        ".....lllll........mm....mmm..ccccccccccccccc..mmm....mm........lllll....",
        "......llll........m.....mmm..ccccnnnnccccccc..mmm.....m........llll.....",
        "......lllll..............m..ccccccccnnccccccc..m..............lllll.....",
        ".......llll.................cccccccccnccccccc.................llll......",
        ".......lllll................ccccccccccccccccc................lllll......",
        "........llll................ccccccccccccccccc................llll.......",
        "........lllll...............ccccccccccccccccc...............lllll.......",
        ".........lllll..............ccccccccccccccccc..............lllll........",
        "..........lllll.............ccccccccccccccccc.............lllll.........",
        "............llll.............ccccccccccccccc.............llll...........",
        "..............................ccccccccccccc.............................",
        "................................ccccccccc...............................",
        "................................ccccccccc...............................",
        ".................................ccccccc................................",
        ".................................ccccccc................................",
        "..................................ccccc.................................",
        "...................................ccc..................................",
        "....................................c...................................",
        "........................................................................",
    ]),
}


# --- Numbers -----------------------------------------------------------------------------------------------------

def sstep(e0, e1, x):
    t = np.clip((np.asarray(x, float) - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def curve(points, v):
    """Catmull-Rom through [(key, value)] (keys ascending or descending), clamped at its ends; v an array."""
    if points[0][0] > points[-1][0]:
        points = points[::-1]
    keys = np.array([p[0] for p in points], float)
    vals = np.array([p[1] for p in points], float)
    v = np.atleast_1d(np.asarray(v, float))
    n = len(points)
    i = np.clip(np.searchsorted(keys, v) - 1, 0, n - 2)
    a, b = keys[i], keys[i + 1]
    t = np.clip((v - a) / (b - a), 0.0, 1.0)
    p0 = vals[np.maximum(i - 1, 0)]
    p1, p2 = vals[i], vals[i + 1]
    p3 = vals[np.minimum(i + 2, n - 1)]
    out = 0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t +
                 (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3)
    out = np.where(v <= keys[0], vals[0], np.where(v >= keys[-1], vals[-1], out))
    return out


def smax(a, b, k_=1.0):
    """A smooth maximum (polynomial, over k_)."""
    h = np.clip(0.5 + 0.5 * (a - b) / k_, 0.0, 1.0)
    return a * h + b * (1 - h) + k_ * h * (1 - h)


# --- Fields from the maps ----------------------------------------------------------------------------------------

class Field:
    """The pixels of some classes of a map, blurred (a Gaussian of sigma pixels): 0 outside, 1 inside, at any (x, y);
    fill: picture column and row ranges (inclusive) counted in as well."""

    def __init__(self, group, classes, sigma=0.65, fill=()):
        r0, c0, rows = MAPS[group]
        pad = 6
        h, w = len(rows), len(rows[0])
        m = np.zeros((h + 2 * pad, w + 2 * pad))
        for r, row in enumerate(rows):
            for c, ch in enumerate(row):
                if ch in classes:
                    m[r + pad, c + pad] = 1.0
        self.r0, self.c0 = r0 - pad, c0 - pad
        for ca, cb, ra, rb in fill:
            m[ra - self.r0:rb - self.r0 + 1, ca - self.c0:cb - self.c0 + 1] = 1.0
        if sigma > 0:
            rad = int(math.ceil(3 * sigma))
            t = np.arange(-rad, rad + 1)
            ker = np.exp(-t * t / (2 * sigma * sigma))
            ker /= ker.sum()
            m = np.apply_along_axis(lambda v: np.convolve(v, ker, mode="same"), 0, m)
            m = np.apply_along_axis(lambda v: np.convolve(v, ker, mode="same"), 1, m)
        self.m = m

    def __call__(self, x, y):
        x = np.atleast_1d(np.asarray(x, float))
        y = np.atleast_1d(np.asarray(y, float))
        fc = x + 35.5 - self.c0
        fr = 53.5 - y - self.r0
        h, w = self.m.shape
        c0 = np.clip(np.floor(fc).astype(int), 0, w - 2)
        r0 = np.clip(np.floor(fr).astype(int), 0, h - 2)
        tc = np.clip(fc - c0, 0.0, 1.0)
        tr = np.clip(fr - r0, 0.0, 1.0)
        m = self.m
        return (m[r0, c0] * (1 - tc) * (1 - tr) + m[r0, c0 + 1] * tc * (1 - tr) + m[r0 + 1, c0] * (1 - tc) * tr +
                m[r0 + 1, c0 + 1] * tc * tr)


# --- Solids over a region ----------------------------------------------------------------------------------------

class Solid:
    """A solid over the region where f(x, y) > 0: a triangular grid over bbox cut along the contour, its top and
    bottom meeting along it. shape() sets their heights from top(x, y, d), bottom(x, y, d) and rim(x, y) (d: how far
    in from the contour; within `radius` of it the top falls to the rim height and the bottom rises to it on quarter
    circles) and gives every vertex its normal (by differences of those heights; on the contour, outwards)."""

    def __init__(self, f, bbox, spacing=GRID):
        self.f = f
        x0, x1, y0, y1 = bbox
        dy = spacing * math.sqrt(3) / 2
        nj = int(math.ceil((y1 - y0) / dy)) + 1
        ni = int(math.ceil((x1 - x0) / spacing)) + 2
        bm = bmesh.new()
        grid = {}
        pts = []
        for j in range(nj):
            for i in range(ni):
                pts.append((x0 + i * spacing + (spacing / 2 if j % 2 else 0.0), y0 + j * dy))
        pts = np.array(pts)
        fv = f(pts[:, 0], pts[:, 1])
        # onto the contour where a point is near it (no slivers along it): a Newton step along the field's gradient
        h = 0.02
        gx = (f(pts[:, 0] + h, pts[:, 1]) - f(pts[:, 0] - h, pts[:, 1])) / (2 * h)
        gy = (f(pts[:, 0], pts[:, 1] + h) - f(pts[:, 0], pts[:, 1] - h)) / (2 * h)
        g2 = np.maximum(gx * gx + gy * gy, 1e-9)
        near = np.abs(fv) < 0.28 * spacing * np.sqrt(g2)
        pts[near, 0] -= fv[near] * gx[near] / g2[near]
        pts[near, 1] -= fv[near] * gy[near] / g2[near]
        fv[near] = 0.0
        values = {}
        for idx, (p, v) in enumerate(zip(pts, fv)):
            j, i = divmod(idx, ni)
            vert = bm.verts.new((float(p[0]), float(p[1]), 0.0))
            grid[i, j] = vert
            values[vert] = float(v)
        for j in range(nj - 1):
            for i in range(ni - 1):
                if j % 2 == 0:
                    tris = [((i, j), (i + 1, j), (i, j + 1)), ((i + 1, j), (i + 1, j + 1), (i, j + 1))]
                else:
                    tris = [((i, j), (i + 1, j), (i + 1, j + 1)), ((i, j), (i + 1, j + 1), (i, j + 1))]
                for tri in tris:
                    vs = [grid[q] for q in tri]
                    if max(values[v] for v in vs) <= 0.0:
                        continue
                    bm.faces.new(vs)
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
        vals = {"f": values}
        split_contour(bm, vals, "f", 0.0)
        gone = [fc for fc in bm.faces if float(f([fc.calc_center_median().x], [fc.calc_center_median().y])[0]) <= 0.0]
        bmesh.ops.delete(bm, geom=gone, context="FACES")
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
        self.bm = bm
        self.vals = {"f": {v: vals["f"].get(v, 0.0) for v in bm.verts}}
        rim_edges = [e for e in bm.edges if len(e.link_faces) == 1]
        self.rim = {v for e in rim_edges for v in e.verts}
        self.seg_a = np.array([[e.verts[0].co.x, e.verts[0].co.y] for e in rim_edges])
        self.seg_b = np.array([[e.verts[1].co.x, e.verts[1].co.y] for e in rim_edges])
        self.tops = set(bm.faces)

    def dist(self, x, y):
        """Distances from points to the contour."""
        x = np.atleast_1d(np.asarray(x, float))
        y = np.atleast_1d(np.asarray(y, float))
        a, b = self.seg_a, self.seg_b
        dx, dy = b[:, 0] - a[:, 0], b[:, 1] - a[:, 1]
        l2 = np.maximum(dx * dx + dy * dy, 1e-12)
        out = np.empty(len(x))
        for s in range(0, len(x), 2048):
            px, py = x[s:s + 2048, None], y[s:s + 2048, None]
            t = np.clip(((px - a[:, 0]) * dx + (py - a[:, 1]) * dy) / l2, 0.0, 1.0)
            cx, cy = a[:, 0] + t * dx, a[:, 1] + t * dy
            out[s:s + 2048] = np.sqrt(((px - cx) ** 2 + (py - cy) ** 2).min(axis=1))
        return out

    def shape(self, top, bottom, rim, radius=1.0, bottom_radius=None):
        bm = self.bm
        rb = radius if bottom_radius is None else bottom_radius
        inner = [v for v in bm.verts if v not in self.rim]
        rim_v = [v for v in bm.verts if v in self.rim]

        def edge(d, r):
            if r <= 0:
                return np.ones_like(d)
            dd = np.minimum(d, r)
            return np.sqrt(np.maximum(0.0, dd * (2 * r - dd))) / r

        def z_of(x, y, which):
            d = self.dist(x, y)
            zr = rim(x, y)
            if which == 0:
                return zr + (top(x, y, d) - zr) * edge(d, radius)
            return zr - (zr - bottom(x, y, d)) * edge(d, rb)

        under = {v: bm.verts.new(v.co) for v in inner}
        for v in rim_v:
            under[v] = v
        bottoms = []
        for fc in [f for f in bm.faces if f in self.tops]:   # (in the mesh's order: the same every run)
            if all(v in self.rim for v in fc.verts):
                continue
            bottoms.append(bm.faces.new([under[v] for v in reversed(fc.verts)]))
        self.bottoms = set(bottoms)
        normal = {}
        h = 0.03
        for group, which in ((inner, 0), ([under[v] for v in inner], 1)):
            if not group:
                continue
            x = np.array([v.co.x for v in group])
            y = np.array([v.co.y for v in group])
            z = z_of(x, y, which)
            zx = (z_of(x + h, y, which) - z_of(x - h, y, which)) / (2 * h)
            zy = (z_of(x, y + h, which) - z_of(x, y - h, which)) / (2 * h)
            for v, zz, a, b in zip(group, z, zx, zy):
                v.co.z = float(zz)
                n = Vector((-a, -b, 1.0)) if which == 0 else Vector((a, b, -1.0))
                normal[v] = n.normalized()
        if rim_v:
            x = np.array([v.co.x for v in rim_v])
            y = np.array([v.co.y for v in rim_v])
            zr = rim(x, y)
            gx = (self.f(x + h, y) - self.f(x - h, y)) / (2 * h)
            gy = (self.f(x, y + h) - self.f(x, y - h)) / (2 * h)
            for v, zz, a, b in zip(rim_v, zr, gx, gy):
                v.co.z = float(zz)
                n = Vector((-a, -b, 0.0))
                normal[v] = n.normalized() if n.length > 1e-9 else Vector((0, 0, 1))
        self.vals["n"] = normal
        for name in list(self.vals):
            if name != "n":
                d = self.vals[name]
                for v in inner:
                    d[under[v]] = d.get(v, 0.0)
        self.under = under
        # the underside, seldom seen, in larger faces (its nearly flat parts merged, the rim's edges kept)
        bot = {fc for fc in self.bottoms if fc.is_valid}
        inner_edges = [e for e in bm.edges
                       if e.link_faces and all(fc in bot for fc in e.link_faces) and
                       not all(v in self.rim for v in e.verts)]
        bm.normal_update()
        bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(3.0), verts=[], edges=inner_edges)
        self.bottoms = {fc for fc in bm.faces if fc not in self.tops}
        self.tops = {fc for fc in self.tops if fc.is_valid}

    def field(self, name, fn):
        """Stores a field's values at the vertices (fn(x, y, z, normal) on arrays)."""
        verts = list(self.bm.verts)
        x = np.array([v.co.x for v in verts])
        y = np.array([v.co.y for v in verts])
        z = np.array([v.co.z for v in verts])
        n = np.array([tuple(self.vals["n"].get(v, Vector((0, 0, 1)))) for v in verts])
        values = fn(x, y, z, n)
        self.vals[name] = {v: float(a) for v, a in zip(verts, values)}

    def paint(self, zones, default, under_key):
        """zones [(zone field name or None, value field name, bands [(lowest, material key)])]: the top's faces cut
        along the zones' borders (field > 0 inside; earlier zones win) and their bands; the underside under_key.
        default: the (value field, bands) of faces in no zone."""
        faces = {fc for fc in self.tops if fc.is_valid}
        for zname, _, _ in zones:
            if zname:
                faces = split_contour(self.bm, self.vals, zname, 0.0, faces)
        zone_of = {}
        for fc in faces:
            zone_of[fc] = len(zones)
            for zi, (zname, _, _) in enumerate(zones):
                if zname and sum(self.vals[zname][v] for v in fc.verts) / len(fc.verts) > 0:
                    zone_of[fc] = zi
                    break
        plans = [(vf, bands) for _, vf, bands in zones] + [default]
        for zi, (vf, bands) in enumerate(plans):
            zf = {fc for fc in zone_of if zone_of[fc] == zi and fc.is_valid}
            for lowest, _ in bands[1:]:
                zf = split_contour(self.bm, self.vals, vf, lowest, zf)
            for fc in zf:
                zone_of[fc] = zi
        self.keys = {}
        for fc in self.bm.faces:
            zi = zone_of.get(fc)
            if zi is None:
                self.keys[fc] = under_key
                continue
            vf, bands = plans[zi]
            value = sum(self.vals[vf][v] for v in fc.verts) / len(fc.verts)
            key = bands[0][1]
            for lowest, mat in bands:
                if value >= lowest:
                    key = mat
            self.keys[fc] = key

    def finish(self, name, m):
        bm = self.bm
        verts = list(bm.verts)
        normals = [self.vals["n"].get(v, Vector((0, 0, 1))) for v in verts]
        slots = []
        for fc in bm.faces:
            key = self.keys.get(fc)
            if key not in slots:
                slots.append(key)
            fc.material_index = slots.index(key)
        mesh = bpy.data.meshes.new(name)
        bm.to_mesh(mesh)
        bm.free()
        obj = bpy.data.objects.new(name, mesh)
        bpy.context.scene.collection.objects.link(obj)
        for key in slots:
            mesh.materials.append(m[key])
        for p in mesh.polygons:
            p.use_smooth = True
        mesh.normals_split_custom_set_from_vertices([tuple(n.normalized()) for n in normals])
        return obj


def light_value(base, a=3.0, b=2.0):
    """A shade value from a normal: base where it faces straight up, more towards the sun, less away and down."""
    L = np.array(tuple(LIGHT))

    def fn(x, y, z, n):
        return base + a * (n @ L - FLAT) + b * (n[:, 2] - 1.0)
    return fn


# --- Materials ---------------------------------------------------------------------------------------------------
# The shades every part is painted in, by the light its faces get (light_value): the steel greys of ramp 6 and the
# greens of ramp 2, a shade or two lighter than the sprite's (the slanted camera sees them darker).
STEEL_BANDS = [(-99, 0x65), (3.4, 0x67), (4.5, 0x69), (5.4, 0x6b), (6.3, 0x6c), (7.0, 0x6d), (7.7, 0x6e)]
GREEN_BANDS = [(-99, 0x23), (3.8, 0x25), (4.9, 0x27), (5.9, 0x29), (6.8, 0x2b)]
GREYS = tuple(k_ for _, k_ in STEEL_BANDS)
GREENS = tuple(k_ for _, k_ in GREEN_BANDS)


def materials():
    pal = k.level_palette()
    m = {}
    for i in GREYS:
        m[i] = k.material("beetle_steel", palette=i, metallic=0.3, roughness=0.36)
    for i in GREENS:
        m[i] = k.material("beetle_shell", palette=i, metallic=0.2, roughness=0.3)
    m["socket"] = k.material("beetle_socket", palette=0x61, metallic=0.1, roughness=0.6)
    m["vee"] = k.material("beetle_shell", palette=0x2d, metallic=0.2, roughness=0.3)
    m["eye"] = k.material("beetle_eye", palette=0x75, metallic=0.0, roughness=0.2, emission=pal[0x75],
                          emission_strength=0.55)
    m["eye_hot"] = k.material("beetle_eye_hot", palette=0x78, metallic=0.0, roughness=0.2, emission=pal[0x78],
                              emission_strength=0.65)
    m["bulb_glow"] = k.material("beetle_bulb", palette=0x2c, metallic=0.1, roughness=0.22, emission=pal[0x2c],
                                emission_strength=0.18)
    return m


# --- The tip (H 155) ---------------------------------------------------------------------------------------------
# A ribbed grey spike pointing up the screen, socketed under the first segment's rear lip: round sections over y
# (TIP_W: their half-width; TIP_Z: the height of their sides, TIP_H their top over that), ribbed across its lower half
# where the sprite draws light bands (TIP_RIBS: y, height); the outline the sprite's pixels, its edge rounded.
TIP_W = [(25.5, 10.0), (30.0, 10.0), (34.0, 9.9), (36.5, 9.2), (40.0, 7.3), (44.0, 5.2), (48.0, 3.3), (51.0, 1.9),
         (53.7, 0.5)]
TIP_Z = [(25.5, 1.6), (34.0, 2.0), (44.0, 2.4), (53.7, 2.9)]
TIP_H = [(25.5, 1.2), (30.0, 1.9), (33.0, 2.8), (36.5, 3.3), (41.0, 3.1), (46.0, 2.4), (50.0, 1.5), (53.7, 0.3)]
TIP_LIGHT = 6.1
TIP_UNDER = 1.1     # the underside this far under the sides (flat, rounded up to them)
TIP_RIBS = [(39.6, 0.32), (37.6, 0.36), (35.6, 0.36), (32.7, 0.32)]
TIP_RIB_W = 0.55


def tip(m):
    field = Field("tip", "t")
    s = Solid(lambda x, y: field(x, y) - 0.5, (-11.0, 12.0, 25.5, 54.6), spacing=0.62)

    def ribs(y):
        return sum(hgt * np.exp(-((y - c) / TIP_RIB_W) ** 2) for c, hgt in TIP_RIBS)

    def top(x, y, d=None):
        t = np.clip(1.0 - ((x - AXIS) / curve(TIP_W, y)) ** 2, 0.0, 1.0)
        return curve(TIP_Z, y) + curve(TIP_H, y) * t ** 0.55 + ribs(y) * t ** 2

    def bottom(x, y, d):
        return curve(TIP_Z, y) - TIP_UNDER

    s.shape(top, bottom, lambda x, y: top(x, y) - 0.45, radius=0.8, bottom_radius=0.8)
    s.field("v", lambda x, y, z, n: light_value(TIP_LIGHT)(x, y, z, n) + 2.2 * ribs(y))
    s.paint([], ("v", STEEL_BANDS), 0x65)
    obj = s.finish("tip", m)
    obj["cap"] = 0x67
    return [obj]


# --- The segments (H 192 beside 194, 230 beside 232) --------------------------------------------------------------
# Each a ribbed green body segment with two big grey plates lying on its sides (the first segment's meeting across its
# back in a strap). The body: a rounded surface over the segment (BODY_Z at its sides, rising to its spine along y as
# exp(-BODY_FALL (u / width)^2), u = x - SEG_AXIS), ribbed across its spine, its belly parted by a groove into two
# lobes; it rises from its front (tucked under the next segment or the thorax) to a lip at its rear over the segment
# behind it (or the tip). The shell shows it where the sprite draws it green (its pixels, reaching a pixel under the
# plates); the plates lie PLATE_LIFT over it where the sprite draws them grey, swelling (bumps) and drooping (DROOP)
# towards their outer ends, their edges rounded down (PLATE_DROP over PLATE_ROUND) and falling straight to their flat
# undersides.


SEGMENTS = {
    "seg1": dict(
        spine=[(5.5, 3.6), (8.0, 4.4), (11.0, 5.3), (14.0, 6.2), (17.0, 6.8), (20.0, 7.3), (23.0, 7.8), (26.0, 8.0),
               (28.5, 7.6), (31.0, 6.7), (33.2, 5.7), (34.2, 5.2)],
        width=[(5.5, 13.5), (10.0, 13.5), (14.0, 13.0), (18.0, 12.5), (22.0, 12.5), (25.0, 12.0), (28.0, 10.0),
               (30.5, 7.0), (32.5, 4.0), (34.2, 2.0)],
        ribs=[28.3, 25.8, 23.4], groove=(12.5, 1.2, 0.55), strap=(15.0, 21.0, 6.5),
        bumps=[(-13.0, 21.5, 7.5, 6.5, 0.9), (13.0, 21.5, 7.5, 6.5, 0.9)],
        bbox=(-23.0, 25.0, 5.0, 34.6)),
    "seg2": dict(
        spine=[(-14.5, 3.6), (-11.0, 4.6), (-8.0, 5.6), (-5.0, 6.6), (-2.0, 7.3), (1.0, 7.9), (4.0, 8.4), (7.0, 8.3),
               (9.5, 7.6), (11.5, 6.7), (13.3, 5.8), (14.3, 5.3)],
        width=[(-14.5, 15.0), (-6.0, 15.0), (0.0, 15.0), (5.0, 15.0), (8.0, 14.0), (10.5, 11.0), (12.5, 7.5),
               (13.8, 4.0), (14.5, 2.2)],
        ribs=[9.6, 7.6, 5.6, 3.6, 1.6, -0.4, -2.4], groove=(-7.0, 1.3, 0.6),
        bumps=[(-15.0, 2.5, 8.5, 7.5, 1.0), (15.0, 2.5, 8.5, 7.5, 1.0)],
        bbox=(-24.5, 25.5, -15.0, 14.6)),
}
SEG_GRID = 0.65      # the plates' grid
SHELL_GRID = 0.7
BODY_Z = 2.5           # the body's sides
BODY_FALL = 1.25       # its section: exp(-BODY_FALL (u / WIDTH)^2)
SHELL_LEVEL = 0.22     # the shell reaches this far under the plates (its pixels blurred more, a lower level)
SHELL_DROP = (0.6, 1.3, 0.9)   # its edge rounds down this much along the plates, this much along the outline, over
SHELL_UNDER = 1.2      # its underside (flat) this far under 2.5
RIB = (0.26, 0.6)      # the ribs' height and half-width
PLATE_LIFT = 1.45      # the plates over the body
PLATE_DROP = 1.0       # their edges round down this much
PLATE_ROUND = 1.8      # over this many pixels in from the outline
DROOP = (1.3, 6.0)     # their outer ends droop this much, over this many pixels outside the body's width
PLATE_FOOT = 1.2       # their flat undersides
STRAP_SHADE = 1.1      # the first segment's strap darker by this
GREEN_BASE = 5.9
PLATE_LIGHT = 6.7


def segment(m, name):
    p = SEGMENTS[name]
    all_ = Field(name, "gp")
    green_dil = Field(name, "g", sigma=1.2)
    plates = Field(name, "p", sigma=1.05)

    def ribs(y):
        return sum(RIB[0] * np.exp(-((y - c) / RIB[1]) ** 2) for c in p["ribs"])

    def body(x, y):
        u = np.abs(x - SEG_AXIS)
        w = curve(p["width"], y)
        t = np.exp(-BODY_FALL * (u / w) ** 2)
        return BODY_Z + (curve(p["spine"], y) - BODY_Z) * t, t

    def shell_top(x, y, d):
        z, t = body(x, y)
        u = np.abs(x - SEG_AXIS)
        gy, gw, gd = p["groove"]
        return z + ribs(y) * t ** 2 - gd * np.exp(-(u / gw) ** 2) * sstep(gy + 2.5, gy, y)

    def shell_rim(x, y):
        by_plate = np.clip((plates(x, y) - 0.08) / 0.3, 0.0, 1.0)
        drop = SHELL_DROP[1] + (SHELL_DROP[0] - SHELL_DROP[1]) * by_plate
        return shell_top(x, y, None) - drop

    def shell_bottom(x, y, d):
        return np.full_like(x, 2.5 - SHELL_UNDER)

    sh = Solid(lambda x, y: np.minimum(green_dil(x, y) - SHELL_LEVEL, all_(x, y) - 0.5), p["bbox"],
               spacing=SHELL_GRID)
    sh.shape(shell_top, shell_bottom, shell_rim, radius=SHELL_DROP[2], bottom_radius=0.8)
    sh.field("v", lambda x, y, z, n: light_value(GREEN_BASE)(x, y, z, n) + 2.5 * ribs(y))
    sh.paint([], ("v", GREEN_BANDS), 0x23)
    shell = sh.finish(name + "_shell", m)
    shell["cap"] = 0x25

    def plate_top(x, y, d):
        z, t = body(x, y)
        u = np.abs(x - SEG_AXIS)
        w = curve(p["width"], y)
        z = z + PLATE_LIFT - DROOP[0] * sstep(w - 1.0, w + DROOP[1], u)
        for cu, cy, rx, ry, hgt in p["bumps"]:
            z = z + hgt * np.exp(-((x - SEG_AXIS - cu) / rx) ** 2 - ((y - cy) / ry) ** 2)
        return z

    def plate_rim(x, y):
        return plate_top(x, y, None) - PLATE_DROP

    def plate_bottom(x, y, d):
        return np.full_like(x, PLATE_FOOT)

    pl = Solid(lambda x, y: plates(x, y) - 0.5, p["bbox"], spacing=SEG_GRID)
    pl.shape(plate_top, plate_bottom, plate_rim, radius=PLATE_ROUND, bottom_radius=0.7)

    def plate_light(x, y, z, n):
        v = light_value(PLATE_LIGHT)(x, y, z, n)
        if p.get("strap"):   # the strap between the first segment's plates a shade darker, as the sprite draws it
            y0, y1, uw = p["strap"]
            v = v - STRAP_SHADE * sstep(uw + 1.5, uw - 1.5, np.abs(x - SEG_AXIS)) * sstep(y0, y0 + 1.0, y) * \
                sstep(y1, y1 - 1.0, y)
        return v
    pl.field("v", plate_light)
    pl.paint([], ("v", STEEL_BANDS), 0x65)
    plate = pl.finish(name + "_plates", m)
    plate["cap"] = 0x67
    return [shell, plate]


# --- The body (H 159, 161, 163 above 197, 199, 201) ----------------------------------------------------------------
# One creature cut into its six sprites: the thorax (a flat-topped shield, the pale ring on its back), the head (two
# red eyes in dark sockets at its top corners, the green nose shield and a green mark under it on its front) and the
# long snout tapering to its point; the green bulbs at the thorax's sides; the sickle legs from behind the bulbs, out,
# round and down to points level with the snout; the feelers from the thorax's rear corners out over the second
# segment, hooking down at their tips; two spines from its rear edge up the screen over that segment's shell; two
# green mouth claws a side, hanging beside the head. u = x - AXIS.
# The core's outline: its half-width over y (traced from the sprite), under the thorax's rear edge; its edges rounded
# down CORE_DROP over CORE_ROUND, its underside flat at CORE_FOOT.
CORE_OUTLINE = [(-10.0, 12.3), (-11.0, 11.9), (-13.0, 11.6), (-18.0, 11.5), (-22.5, 11.6), (-24.0, 12.3),
                (-25.5, 13.0), (-27.5, 13.4), (-29.5, 12.8), (-30.8, 11.6), (-31.8, 9.8), (-33.0, 8.4), (-35.5, 8.0),
                (-38.0, 8.2), (-41.5, 8.4), (-43.5, 8.1), (-44.5, 7.6), (-45.5, 6.6), (-46.5, 5.5), (-47.5, 4.7),
                (-48.5, 4.0), (-49.5, 3.3), (-50.5, 2.6), (-51.5, 1.7), (-52.5, 0.8), (-53.3, 0.0), (-54.0, -1.0)]
CORE_TOP = -10.0                     # the thorax's rear edge (y), its corners rounded over CORE_CORNER
CORE_CORNER = 1.6
# The core's domes: the thorax and the head (middle (u, y), radii, height over CORE_ZB, the dome's top flatness), the
# snout a ridge along y (its height and half-width over y), joined by smooth maxima (the neck the crease where the
# thorax's front meets the head's back).
THORAX = ((0.0, -17.2), (13.0, 8.2), 7.5, 0.55)
HEAD = ((0.0, -28.3), (14.2, 5.0), 5.8, 0.6)
SNOUT_H = [(-29.0, 5.6), (-32.0, 5.4), (-36.0, 4.8), (-40.0, 4.0), (-44.0, 3.1), (-47.5, 2.3), (-50.5, 1.5),
           (-53.3, 0.8)]
SNOUT_W = [(-29.0, 10.5), (-32.0, 10.0), (-36.0, 9.6), (-42.0, 9.6), (-45.0, 8.2), (-48.0, 5.6), (-51.0, 3.4),
           (-53.3, 1.6)]
BROWS = (7.3, -25.3, 2.6, 0.9, 0.45)   # a ridge over each socket: |u|, y, radii, height
CHEEK_BULGE = (10.6, -29.6, 2.4, 2.0, 0.6)   # the claws' bases: |u|, y, radii, height
CORE_ZB = 2.0
CORE_DROP, CORE_ROUND = 1.0, 1.4
CORE_FOOT = 1.4
SOCKETS = (7.5, -27.4, 2.3, 1.45, 1.0)   # the eye sockets: |u|, y, radii, depth
EYES = (7.5, -27.45, 1.2, 0.8)      # the eyes: |u|, y, radius, height
SOCKET_ZONE = 0.42                  # the dark round the eyes where the sockets are deeper than this share
NOSE = (0.0, -31.8, 2.8, 3.2, 0.55)  # the nose shield (an oval scale): u, y, half-sizes, height
MARK = (0.0, -37.3, 2.1, 1.3, 0.3)   # the green mark under it
VEE = ((-1.75, -30.0), (0.0, -33.5), 0.42, 0.16)   # the nose's pale V: a stroke from (u, y) to (u, y), mirrored;
#                                                   its half-width and half-height
CHEEKS = [((-9.0, -28.4), (-11.0, -31.0))]  # grooves from the sockets down to the claws' roots (u, y), mirrored
CHEEK_DEPTH, CHEEK_W = 0.4, 0.5
SNOUT_CREST = (1.6, 0.35, -33.0, -36.0)
NOSTRILS = (5.4, -39.6, 0.8, 1.1, 0.32)
SNOUT_GROOVES = (6.7, 0.6, 0.32, -32.0, -44.5)   # along the snout's sides: |u|, half-width, depth, from y to y
DOTS = [(-3.0, -25.4), (4.0, -25.4)]   # the green dots between the eyes (x, y)
RING = (AXIS, -19.5)                # the ring on the thorax's back: its middle (x, y)
RING_PROFILE = [(6.7, -0.9), (6.55, 0.0), (6.2, 0.75), (5.6, 1.15), (5.0, 1.25), (4.45, 1.05), (4.15, 0.55),
                (3.85, 0.35), (3.55, 0.5), (3.0, 0.85), (2.0, 1.1), (1.0, 1.22), (0.0, 1.25)]
RING_GROOVE = (3.6, 4.3)
CORE_LIGHT = 5.6
HEAD_SHADE = 0.9     # the head a shade darker than the thorax
RIDGE_LIGHT = 0.6    # the snout's ridge lighter
BULBS = [((-11.0, -18.7, 5.6), (4.5, 5.1, 3.1)), ((12.0, -18.7, 5.6), (4.5, 5.1, 3.1))]
BULB_BANDS = [(-99, 0x23), (3.8, 0x25), (4.9, 0x27), (5.9, 0x29), (6.6, 0x2b), (7.15, "bulb_glow")]
# The left leg, feeler, spine and claws: stations (x, y, z, half-width in plan, half-height); the right ones are their
# mirror images about AXIS.
LEG = [(-13.2, -17.2, 5.4, 2.4, 1.8, 2.0), (-15.2, -15.9, 6.2, 3.1, 1.95, 2.0), (-17.6, -15.0, 6.8, 3.9, 2.05, 2.0),
       (-21.0, -14.9, 7.2, 3.8, 2.05, 2.0), (-23.2, -15.5, 7.15, 3.6, 2.0, 2.0), (-24.2, -17.6, 6.95, 2.8, 1.7, 2.0),
       (-24.7, -20.2, 6.6, 3.2, 1.85, 1.8), (-25.5, -22.6, 6.2, 3.0, 1.8, 1.7), (-26.5, -24.4, 5.8, 2.85, 1.75, 1.7),
       (-27.6, -25.6, 5.5, 2.9, 1.75, 1.7), (-29.2, -27.0, 5.2, 3.05, 1.72, 1.7), (-29.6, -28.8, 4.9, 3.1, 1.7, 1.7),
       (-29.4, -31.0, 4.6, 3.05, 1.65, 1.7), (-29.0, -33.2, 4.3, 2.85, 1.55, 1.7), (-28.4, -35.4, 3.9, 2.55, 1.4, 1.7),
       (-27.5, -37.6, 3.5, 2.2, 1.25, 1.7), (-26.4, -39.6, 3.2, 2.0, 1.1, 1.7), (-25.2, -41.4, 2.95, 1.9, 0.95, 1.7),
       (-23.9, -42.9, 2.75, 1.7, 0.8, 1.7), (-22.8, -43.9, 2.6, 1.1, 0.55, 1.7), (-22.0, -44.5, 2.55, 0.25, 0.2, 1.7)]
FEELER = [(-8.2, -9.9, 7.9, 1.8, 1.35), (-9.8, -8.6, 8.3, 2.2, 1.3), (-11.8, -7.4, 8.5, 2.3, 1.25),
          (-14.0, -6.4, 8.6, 2.1, 1.1), (-16.5, -5.8, 8.4, 1.6, 0.95), (-19.0, -5.45, 8.2, 1.3, 0.9),
          (-22.0, -5.35, 8.0, 1.2, 0.88), (-24.5, -5.5, 7.7, 1.15, 0.85), (-26.2, -6.0, 7.3, 1.1, 0.8),
          (-27.4, -6.9, 6.9, 1.05, 0.78), (-27.9, -8.0, 6.5, 0.8, 0.6), (-28.0, -8.9, 6.3, 0.2, 0.2)]
SPINE = [(-1.6, -10.4, 7.9, 1.5, 1.1), (-2.4, -8.7, 8.8, 1.5, 1.0), (-3.3, -7.1, 9.4, 1.4, 0.9),
         (-4.4, -5.6, 9.8, 1.15, 0.78), (-5.5, -4.2, 10.0, 0.8, 0.58), (-6.3, -3.0, 10.1, 0.25, 0.2)]
CLAW_OUTER = [(-12.6, -25.8, 4.9, 1.3, 1.1), (-14.0, -27.4, 4.5, 1.9, 1.25), (-14.9, -29.4, 4.0, 2.1, 1.2),
              (-16.0, -31.4, 3.5, 1.7, 1.0), (-16.9, -33.4, 3.1, 1.35, 0.8), (-17.5, -35.2, 2.8, 0.9, 0.55),
              (-17.9, -36.7, 2.65, 0.2, 0.2)]
CLAW_INNER = [(-8.2, -31.0, 5.0, 1.3, 1.0), (-9.7, -32.3, 4.4, 1.35, 0.95), (-10.3, -33.8, 3.9, 1.2, 0.8),
              (-10.6, -35.4, 3.5, 0.95, 0.6), (-10.7, -37.3, 3.2, 0.2, 0.15)]


def mirrored(stations):
    return [(2 * AXIS - st[0],) + tuple(st[1:]) for st in stations]


def densify(stations, step=0.6):
    """Catmull-Rom through the stations (all their values together), points about step pixels apart."""
    pts = [np.array(s, float) for s in stations]
    out = []
    for i in range(len(pts) - 1):
        p0, p1, p2 = pts[max(i - 1, 0)], pts[i], pts[i + 1]
        p3 = pts[min(i + 2, len(pts) - 1)]
        n = max(1, int(math.ceil(np.linalg.norm(p2[:3] - p1[:3]) / step)))
        for j in range(n):
            t = j / n
            out.append(0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t +
                              (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(pts[-1])
    return out


def tube(name, stations, mat, segments=14, power=2.0):
    """A tube through stations (x, y, z, half-width across its path in plan, half-height[, power]), its sections
    superellipses lying flat (their width level; power 2 an ellipse, less a lens), closed to points at its ends."""
    dense = densify([tuple(st) + (() if len(st) > 5 else (power,)) for st in stations])
    rings = []
    pts = [Vector(tuple(d[:3])) for d in dense]
    for i, d in enumerate(dense):
        t = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        side = t.cross(Vector((0.0, 0.0, 1.0)))
        side = side.normalized() if side.length > 1e-6 else Vector((1.0, 0.0, 0.0))
        up = side.cross(t).normalized()
        ring = []
        for j in range(segments):
            a = 2 * math.pi * j / segments
            c, s_ = math.cos(a), math.sin(a)
            pw = d[5]
            px = math.copysign(abs(c) ** (2 / pw), c) * max(d[3], 0.03)
            pz = math.copysign(abs(s_) ** (2 / pw), s_) * max(d[4], 0.03)
            ring.append(pts[i] + side * px + up * pz)
        rings.append(ring)
    first = pts[0] - (pts[1] - pts[0]).normalized() * 0.15
    last = pts[-1] + (pts[-1] - pts[-2]).normalized() * 0.1
    return k.loft(name, rings[1:-1], mat, start_point=first, end_point=last)


def paint_light(obj, m, bands, base, a=3.0, b=2.0):
    """band_split by how a part's vertices face the sun and up (light_value), then smooth shading."""
    mesh = obj.data
    L = Vector(LIGHT)
    values = [base + a * (Vector(v.normal).dot(L) - FLAT) + b * (v.normal.z - 1.0) for v in mesh.vertices]
    band_split(obj, values, [(lo, m[key]) for lo, key in bands])
    k.smooth(obj, 80)
    return obj


def seg_dist(u, y, a0, a1, b0, b1):
    """Distance from (|u|, y) to the segment (a0, a1)-(b0, b1) (mirrored about the axis: a0, b0 are |u| as well as
    negative values, which are taken as they are)."""
    uu = np.abs(u)
    ax, ay, bx, by = abs(a0), a1, abs(b0), b1
    dx, dy = bx - ax, by - ay
    t = np.clip(((uu - ax) * dx + (y - ay) * dy) / (dx * dx + dy * dy), 0.0, 1.0)
    return np.hypot(uu - ax - t * dx, y - ay - t * dy)


def smin(a, b, k_=1.0):
    return -smax(-a, -b, k_)


def core_region(x, y):
    """Inside the thorax, head and snout: within CORE_OUTLINE's half-width of the axis, under the rear edge."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    return smin(curve(CORE_OUTLINE, y) - np.abs(x - AXIS), CORE_TOP - y, CORE_CORNER)


def core(m):

    def lobe(x, y, spec):
        (cu, cy), (rx, ry), hgt, flat = spec
        q = np.sqrt(((x - AXIS - cu) / rx) ** 2 + ((y - cy) / ry) ** 2)
        return CORE_ZB + hgt * np.clip(1.0 - q * q, 0.0, 1.0) ** flat

    def base(x, y):
        u = np.abs(x - AXIS)
        sw = curve(SNOUT_W, y)
        snout = CORE_ZB + curve(SNOUT_H, y) * np.clip(1.0 - (u / sw) ** 2, 0.0, 1.0) ** 0.75
        snout = np.where(y > -29.0, CORE_ZB, snout)
        z = smax(smax(lobe(x, y, THORAX), lobe(x, y, HEAD), 0.7), snout, 1.6)
        edge = sstep(0.0, 1.6, curve(CORE_OUTLINE, y) - u)    # (the details fade out at the outline)
        bu, by, br1, br2, bh = BROWS
        z += bh * np.exp(-((u - bu) / br1) ** 2 - ((y - by) / br2) ** 2) * edge
        su, sy, sr1, sr2, sd = SOCKETS
        z -= sd * np.exp(-((u - su) / sr1) ** 2 - ((y - sy) / sr2) ** 2) * edge
        cu, cy, cr1, cr2, chh = CHEEK_BULGE
        z += chh * np.exp(-((u - cu) / cr1) ** 2 - ((y - cy) / cr2) ** 2) * edge
        nu, ny, nw, nh, nz = NOSE
        r2 = ((x - AXIS - nu) / nw) ** 2 + ((y - ny) / nh) ** 2
        z += nz * sstep(1.0, 0.55, r2)
        mu, my, mw, mh, mz = MARK
        r2 = ((x - AXIS - mu) / mw) ** 2 + ((y - my) / mh) ** 2
        z += mz * sstep(1.0, 0.5, r2)
        for (a0, a1), (b0, b1) in CHEEKS:
            z -= CHEEK_DEPTH * np.exp(-(seg_dist(u, y, a0, a1, b0, b1) / CHEEK_W) ** 2) * edge
        cw, ch, c0, c1 = SNOUT_CREST
        z += ch * np.exp(-(u / cw) ** 2) * sstep(c0, c1, y)
        tu, ty, tr1, tr2, td = NOSTRILS
        z -= td * np.exp(-((u - tu) / tr1) ** 2 - ((y - ty) / tr2) ** 2) * edge
        gu, gw, gd, g0, g1 = SNOUT_GROOVES
        z -= gd * np.exp(-((u - gu) / gw) ** 2) * sstep(g0 + 1.5, g0 - 1.0, y) * sstep(g1 - 1.5, g1 + 1.0, y) * edge
        return z

    s = Solid(core_region, (-14.5, 15.5, -54.0, -9.5), spacing=0.68)
    s.shape(lambda x, y, d: base(x, y), lambda x, y, d: np.full_like(x, CORE_FOOT),
            lambda x, y: base(x, y) - CORE_DROP, radius=CORE_ROUND, bottom_radius=0.8)

    def core_light(x, y, z, n):
        head = HEAD_SHADE * sstep(-23.5, -25.5, y) * sstep(-36.0, -32.0, y)
        ridge = RIDGE_LIGHT * np.exp(-((x - AXIS) / 1.8) ** 2) * sstep(-33.0, -37.0, y)
        return light_value(CORE_LIGHT)(x, y, z, n) - head + ridge
    s.field("v", core_light)
    s.field("green_v", light_value(GREEN_BASE - 0.2))

    def nose_zone(x, y, z, n):
        nu, ny, nw, nh, _ = NOSE
        mu, my, mw, mh, _ = MARK
        r1 = ((x - AXIS - nu) / nw) ** 2 + ((y - ny) / nh) ** 2
        r2 = ((x - AXIS - mu) / mw) ** 2 + ((y - my) / mh) ** 2
        return 0.92 - np.minimum(r1, r2)
    s.field("nose", nose_zone)

    def socket_zone(x, y, z, n):
        su, sy, sr1, sr2, _ = SOCKETS
        return np.exp(-((np.abs(x - AXIS) - su) / sr1) ** 2 - ((y - sy) / sr2) ** 2) - SOCKET_ZONE
    s.field("socket", socket_zone)
    s.paint([("socket", "v", [(-99, "socket")]), ("nose", "green_v", GREEN_BANDS)], ("v", STEEL_BANDS), 0x65)
    obj = s.finish("core", m)
    obj["cap"] = 0x67
    return obj, base


def ring(m, base):
    cx, cy = RING
    z0 = float(base(np.array([cx]), np.array([cy]))[0]) - 0.2
    prof = [(r, z0 + dz) for r, dz in RING_PROFILE]
    obj = mk.lathe("ring", prof, (cx, cy), m[0x6c], segments=36)
    k.smooth(obj, 50)
    g0, g1 = RING_GROOVE

    def pick(c, n):
        r = math.hypot(c.x - cx, c.y - cy)
        light = 3.0 * (n.dot(LIGHT) - FLAT) + 2.0 * (n.z - 1.0)
        if g0 <= r <= g1:
            return m[0x65] if light < -0.6 else m[0x67]
        if r < g0:
            return m[0x69] if light < -1.2 else m[0x6b] if light < -0.2 else m[0x6c]
        return m[0x6b] if light < -1.2 else m[0x6c] if light < -0.4 else m[0x6d] if light < 0.25 else m[0x6e]
    mk.paint(obj, pick)
    obj["cap"] = 0x65
    return obj


def body(m):
    core_obj, base = core(m)
    parts = [core_obj, ring(m, base)]
    for i, (centre, radii) in enumerate(BULBS):
        b = icosphere("bulb%d" % i, centre, radii, subdivisions=3)
        b.data.materials.append(m[0x29])
        paint_light(b, m, BULB_BANDS, GREEN_BASE + 1.2)
        b["cap"] = 0x25
        parts.append(b)
    for name, stations, mat, bands, light, cap, segments in (
            ("leg", LEG, 0x6b, STEEL_BANDS, 6.3, 0x67, 12), ("feeler", FEELER, 0x6b, STEEL_BANDS, 6.3, 0x67, 10),
            ("spine", SPINE, 0x6b, STEEL_BANDS, 6.4, 0x67, 10),
            ("claw", CLAW_OUTER, 0x29, GREEN_BANDS, GREEN_BASE + 0.3, 0x25, 10),
            ("claw_in", CLAW_INNER, 0x29, GREEN_BANDS, GREEN_BASE + 0.3, 0x25, 10)):
        for side, st in (("l", stations), ("r", mirrored(stations))):
            obj = tube("%s_%s" % (name, side), st, m[mat], segments=segments)
            paint_light(obj, m, bands, light)
            obj["cap"] = cap
            parts.append(obj)
    eu, ey, er, eh = EYES
    for side in (-1, 1):
        ex = AXIS + side * eu
        ez = float(base(np.array([ex]), np.array([ey]))[0])
        eye = mk.ball("eye%d" % side, (ex, ey, ez - 0.15), (er, er * 0.95, eh), m["eye"], 16, 8)
        hot = mk.ball("eye_hot%d" % side, (ex - 0.25, ey + 0.15, ez + 0.25), (er * 0.5, er * 0.45, eh * 0.55),
                      m["eye_hot"], 12, 6)
        for o in (eye, hot):
            o["cap"] = "socket"
            parts.append(o)
    (a0, a1), (b0, b1), vw, vh = VEE
    for side in (-1, 1):
        pts = []
        for t in np.linspace(0.0, 1.0, 6):
            vx = AXIS + side * (abs(a0) + (abs(b0) - abs(a0)) * t)
            vy = a1 + (b1 - a1) * t
            vz = float(base(np.array([vx]), np.array([vy]))[0])
            pts.append((vx, vy, vz + 0.02, vw * (1.0 if t < 0.85 else 0.6), vh))
        vee = tube("vee%d" % side, pts, m["vee"], segments=8)
        k.smooth(vee, 60)
        vee["cap"] = "vee"
        parts.append(vee)
    for i, (dx, dy) in enumerate(DOTS):
        dz = float(base(np.array([dx]), np.array([dy]))[0])
        dot = mk.ball("dot%d" % i, (dx, dy, dz - 0.1), (0.75, 0.6, 0.45), m[0x2b], 10, 6)
        dot["cap"] = 0x25
        parts.append(dot)
    return parts


# --- Building ----------------------------------------------------------------------------------------------------
# The pieces: name, sprite, group, the box cut out of the whole (x0, x1, y0, y1, in the whole's coordinates: the
# 72 x 108 picture's middle), the sprite's middle (the piece's origin). The body's rows meet at the top of 197-201
# (y -26: drawn over the last four rows of 159-163); the segments are cut down their middle (x 0).
BIG = 200.0
PIECES = [
    ("torm_beetle_tip", 155, "tip", (-BIG, BIG, -BIG, BIG), (0.0, 40.0)),
    ("torm_beetle_seg1_l", 192, "seg1", (-BIG, 0.0, -BIG, BIG), (-12.0, 20.0)),
    ("torm_beetle_seg1_r", 194, "seg1", (0.0, BIG, -BIG, BIG), (12.0, 20.0)),
    ("torm_beetle_seg2_l", 230, "seg2", (-BIG, 0.0, -BIG, BIG), (-12.0, 0.0)),
    ("torm_beetle_seg2_r", 232, "seg2", (0.0, BIG, -BIG, BIG), (12.0, 0.0)),
    ("torm_beetle_tl", 159, "body", (-BIG, -12.0, -26.0, BIG), (-24.0, -16.0)),
    ("torm_beetle_tm", 161, "body", (-12.0, 12.0, -26.0, BIG), (0.0, -16.0)),
    ("torm_beetle_tr", 163, "body", (12.0, BIG, -26.0, BIG), (24.0, -16.0)),
    ("torm_beetle_bl", 197, "body", (-BIG, -12.0, -BIG, -26.0), (-24.0, -40.0)),
    ("torm_beetle_bm", 199, "body", (-12.0, 12.0, -BIG, -26.0), (0.0, -40.0)),
    ("torm_beetle_br", 201, "body", (12.0, BIG, -BIG, -26.0), (24.0, -40.0)),
]
# The top row's last four rows are drawn over by the bottom row's sprites: their silhouettes are compared above that.
HIDDEN_ROWS = {159: 24, 161: 24, 163: 24}
BUILDERS = {"tip": tip, "seg1": lambda m: segment(m, "seg1"), "seg2": lambda m: segment(m, "seg2"), "body": body}


def build_group(group):
    k.reset()
    m = materials()
    objs = BUILDERS[group](m)
    triangulate(objs)
    return objs, m


def build():
    options = k.args()
    out = mk.outdir(options)
    only = set(options["only"].split(",")) if "only" in options else None
    sheet = None
    if "check" in options:
        sheet = os.path.join(options["check"], "enemy_H.png")
    for group in BUILDERS:
        pieces = [p for p in PIECES if p[2] == group and (not only or p[0] in only)]
        if not pieces and "preview" not in options:
            continue
        whole, m = build_group(group)
        bpy.context.scene.view_settings.view_transform = "Standard"
        low, high = mk.bounds(whole)
        print("== %s whole: %d triangles, x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f" % (
            group, mk.triangles(whole), low.x, high.x, low.y, high.y, low.z, high.z))
        if "preview" in options:
            cx, cy = (low.x + high.x) / 2, (low.y + high.y) / 2
            size = (int(math.ceil(high.x - low.x)) + 4, int(math.ceil(high.y - low.y)) + 4)
            mk.preview(options["preview"] + group, whole, size=size, scale=12, distance=1.6, centre=(cx, cy))
        bpy.context.view_layer.update()   # (the previews moved the parts and back: their bounds again)
        for name, sprite, _, box, (cx, cy) in pieces:
            parts = [p for p in (cut(src, box, m[src.get("cap", 0x67)]) for src in whole) if p is not None]
            drop_unused(parts)
            mk.transform(parts, Matrix.Translation((-cx, -cy, 0)))
            bpy.context.view_layer.update()
            triangulate(parts)
            if "stats" in options:
                for obj in sorted(parts, key=lambda o: -mk.triangles([o]))[:10]:
                    print("    %-22s %6d" % (obj.name, mk.triangles([obj])))
            parts = [join(parts, name)]
            parts[0].data.name = name
            for src in whole:
                src.hide_render = True
            if sheet:
                covered, mask = mk.coverage(parts, 24, 28), k.sprite_mask(sheet, sprite)
                if sprite in HIDDEN_ROWS:   # (rows the next sprites are drawn over)
                    covered, mask = covered[:HIDDEN_ROWS[sprite]], mask[:HIDDEN_ROWS[sprite]]
                mk.compare("%s (H %d)" % (name, sprite), covered, mask)
            mk.report(name, parts, os.path.join(out, name + ".glb"))
            if "preview" in options and options.get("pieces") == "1":
                mk.preview(options["preview"] + name, parts)
            for obj in parts:
                bpy.data.objects.remove(obj)
            for src in whole:
                src.hide_render = False


if __name__ == "__main__":
    build()
