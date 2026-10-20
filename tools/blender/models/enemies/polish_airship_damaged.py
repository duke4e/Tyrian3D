"""SAVARA's grey airship damaged (models zeppelin_11, 13, 47, 49, 51, 53, 85, 87, 89, 91, 123, 125, 127, 129, 162,
164, 166): each piece's dgr, the sprite 8 further on (I 11 13 / 47-53 / 85-91 / 123-129 / 162-166 of 3 5 / 39-45 /
77-83 / 115-121 / 154-158), which the game puts in a piece's place when it is shot to pieces (SAVARA, SAVARA V,
SAVARA Y); models.cfg: model zeppelin_<sprite> enemies/zeppelin_<sprite>.glb origin; sprite i <sprite>
zeppelin_<sprite> yaw=0 (as before). Polished 2026-10-20; it replaces wave3_ao_zeppelin.py (the old airship pitted
along the sprite's pixels) and wave3_ao_art.py's ZEP and ZEP_DMG.

The airship is polish_airship.py's (its builders imported, unchanged), built whole, damaged as the damaged sprites
draw it, and cut into the same seventeen pieces at the same origins, so that a damaged piece meets its neighbours,
damaged or not: nothing moves at the pieces' edges but the bite, which fades out before it reaches the nose's row.

What the damaged sprites draw differently, read pixel by pixel into DAMAGE below (the 96 x 140 picture's rows 10-119):
- the envelope torn open in three deep wounds, a small one on its upper right (rows 59-79), one on its left (rows
  66-91) and a long one down its lower middle (rows 77-118), the burnt framework in them glowing red, and a bite out
  of its lower left edge (rows 95-117), where the outline is pulled in up to six pixels; scorched fabric round them;
- the fan's blades gone (stubs left on the hub), the duct holed and scorched on both sides of its back (rows
  12-27), a burn on the cowl's right shoulder (rows 29-38), the gate's crossbar holed (rows 43-49), both gun mounts
  scorched (rows 55-61), the left pod's front end scorched (rows 82-89), the right pod torn off below its band (row
  80; rows 81-107 empty).
How: the envelope is meshed finer over the wounds, cut along the wounds' ragged outlines (the map blurred, with
noise) and the fabric inside them taken away; its torn edges are charred, drooping into the holes, a strip of char
giving the fabric its thickness there, and scorched round them; inside, the envelope's lower skin is black. Under the
wounds lies the airship's framework (ring frames and girders as lattice beams a little below the fabric), burnt
black and glowing red where the sprites draw red, broken in the long wound. The net's ropes and knots are gone over
the wounds and charred near them. The other parts are scorched (their faces painted, the burns pressed in a little)
where the sprites draw them darker; the right pod's barrel and muzzle are gone and its body ends in a jagged, glowing
break.

Coordinates as in polish_airship.py (built about X = 0, moved onto the picture's axis at the end); pixel (c, r) of
the picture covers X c - 48.5..c - 47.5, y 69 - r..70 - r.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes of the whole
and of each piece against enemy_I.png), --preview <prefix>, --only <model,...>, --whole <file.glb>.
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
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
import polish_airship as pa  # noqa: E402

PIECES = [("zeppelin_%d" % (s + 8), s + 8, box) for _, s, box in pa.PIECES]

# --- The damage map -------------------------------------------------------------------------------------------------
# Each pixel of the damaged picture against the intact one (rows DAMAGE_ROW on, 96 columns): ' ' empty in both, '.' as
# it was, '-' gone, 'c' black (burnt, torn open), 's' scorched (two or more shades darker), 'g' grey but changed (torn
# fabric), 'e' a dark red glow, 'E' a bright one (the burning framework, embers).
DAMAGE_ROW = 10
DAMAGE = [
    "                                         ...............",
    "                                      .....................",
    "                                    ......................s..",
    "                                  ........................sss..",
    "                                ......E...................sss....",
    "                               .cssEEsss..................sscs..c.",
    "                              ..ssccssss...................sccs.sc",
    "                             ..sccccsss.... .......... ....scccscsc.",
    "                            ..cccccsssc...................ccccccc.c..",
    "                           ..ssccccscc..   ...........   ..ccccccE....",
    "                           ...ccss.c .     ...........     ..cccc.....",
    "                          .......c.---     ...........       ..cccc....",
    "                          ...sscc.----     ...........       --.cccc...",
    "                         ...sscc.------    ...........      ----.ccc....",
    "                         ...scc..-------   ...........     ------.cc....",
    "                          ..cc.  -------   ...........    ------- .....",
    "                        ....c.    -------  ...........   --------   ....",
    "                        ....c.     ------...............--------   .....",
    "                        .....       --.....................---      .....",
    "                        .....       .....................gc..       .....",
    "                        ....---   ......................gsscc..     -....",
    "                        ....----........................gssccc...-----...",
    "                        ....---.........................gsscccc.c.----...",
    "                        ... - ...........................scccccc.c.---...",
    "                        ...  ............................sccccccc.c.--...",
    "                        ... ............................gscccccccc.c.-...",
    "                        ................................c..cccccccc.g....",
    "                        ................................c...ssgssss.g....",
    "                        ................................c...s....ggg.....",
    "                        .................................................",
    "                       ...................................................",
    "                       ...................................................",
    "                      .....................................................",
    "                      ..........................EE.........................",
    "                     ..........................sss..........................",
    "              ............................ssssssscccsscs...........................",
    "            .............................sss..sccccsssss .................... ..... .",
    "           ..............................Es.ssccccsEsss. .............................",
    "          .................................sssccc.csss.. ..............................",
    "         ....      ........................ .s cc.sE. ........................      ....",
    "      .......     ......................... ..    ... .........................     .......",
    "      .........   ............................ .  .............................   .........",
    "      .........   ............................ ...... .........................   .........",
    "      ........................................ ...... .....................................",
    "  ............................................ ................................................",
    "  .....................................................................................sEEE....",
    "  ....EEss..............................................................................ssss...",
    "  ..scEscc...............................................................................scccc.",
    "  .cccEscc...............................................................................scccc.",
    "  .cccEss.......................................................ggg.............. ......sscccc.",
    "  ...EE........................................................gscss..................ccss.....",
    "  ............ ............................... ...............gscccccg................ cs...c.",
    "  .........    ...............................................scccccecg...........    .c.......",
    "  .........    ............................. .................sccecceccs..........    .........",
    "  .........    ...............................................scceccececs.........    .........",
    "  ........    ................................................sccEccececcc.........    ........",
    "  ........    .......gsssg....................................sceEecececccc........    ........",
    " ...........  ......gssssssg..................................sccEeeececcccg.......  ...........",
    " ...........  .....gssssccssg................................gccceeeEeeccccc.......  ...........",
    "............  .....ssscccccsg...............................gsccceeceeeccccc.......  ...........",
    "............  .....ssccccccgg...............................ssccceeeeceecccg.......  ...........",
    "........ ...  .....gsccscccggg............... .. ..........gssccceccececccg........  ...........",
    "............  ......scsscccsggs............................gsssceecccccccg.........  ....ssc....",
    "............  .....gscsccccssssg...........................ggssseecscccg...........  ...ccsc....",
    "............  .....sscccccesgsss............................ggssssssssg............  ...cccc....",
    "............  .....ssccsseecssss.............................ggg.gsssg.............  ....sE.....",
    "............  .....scccsceccssscs............................ggg..ggg..............  ....s......",
    "............  .....sccssccssssgsss........gg................gsssg..................  ....s......",
    "............  .....ssscccssscsgssss......gssg...............sssss..................  ....gcc....",
    "............  .....sscccsscscsgsscss......ssggsgsss.g.......sscccssg...............  ...ggscc.c.",
    "..........    .....gssccsccscssssscss...gssssssssssssssssg..sscccssss..............    .ssscc cc",
    "..........    ......gccccccscsssscccsg...gsccccccsssscccsssgsscccccccc.............    .ccsccc--",
    ".....gsc.     .......scccccsccssccccsg....sccccccccsccsccccccsscccccccs............     .cccc- -",
    "....cssc.     .......ssscecEcecscccss.....sccccccccsccsccccccsceeeccccsg...........     ------ -",
    "....ccsc.     .......gscsecEceccccsg.....scccccssscsccsccccccsceeeeecccc...........     ------ -",
    "....ccsc.     .......ssceecececccsg....sscccccccsccssssccccccsccceeeeccc...........     ------ -",
    "....cccc.     .......ssceecececcsg....ssccssssccsccsccccccscscccccceeccc...........     ------ -",
    "....cccc.     .......ssccecececcs....ssccsggsssssscsccccccsccssceccceeccggg........     --------",
    " ...cccc.     .......ssccececccc....gsscssssssssssssssccccsccccceecceecggcgg.......     --------",
    " ...c....     .......gsccececccs.....sscecccsss..ggg.gssscscccccceeeccccgccgc......     --- ----",
    " ........     ........sccceecccs....scceecscss...gsssss.ssgsccccccccccccccccc......     --------",
    " ........     ......gssccccccccs....scceeccsss..gsssssccecsccsccccceccccccccc......     --------",
    " ......       .....gssccccccccss....seceeccsss..ssssscccccccccccccccccggcccc.......       ------",
    "   ....       .....scccccscccsss...sseeeccsssssssscccccccccceeeecccccccccccc.......       ----",
    "   ....       .....scccccsssg.ss..sscecsccssssscsscccc-ccccceeeccc-cgccccgcc.......       ----",
    "   ....       .cg..scccccsssgsss.ssseesssccssssccsccc--cccccEeeccc-cgccccccc.......       ----",
    "   ....       .ccs.sccccss.ssssssceEecsggsccsgsscccccccccccEEecccccccccgcccc.......       ----",
    "   ....       -cccccccccss...gsscceEecs..sccsssssssscccscecEEEeeccccccc.ccccg......       ----",
    "  .....       ---cccccccsg....gsceEEcsg..sssgsscccccccssceeeEEEEccccccccccccc......       -----",
    ".......       ----ccccccs......gsccecs...gssssscccccccssceeeEeeeEeecccccccccc......       ------",
    ".......       ----cccccsg.......gscesss...sgssscccceeecccceeeeeeeeeeccccccccc......       ------",
    ".......       -----cccsg.........gsscsss.ggg.sssssscceecccccccccceeeecccccccc......       ------",
    ".......       ------ccc...........sccccss.gggssccceeeEEeeecccsccccccccccccccc......       ------",
    ".......        -----cccg...........sssssgg..g.ssccceeEEEEeeccsssccccccccc.ccc.....        ------",
    ".... ..        ------ccs.............g.g......sccccceeeeeeecccscccccccccccgsc.....        -- ---",
    ".......        ------cccs.................gssssssscccccceeccecccc-ceccccccgg......        ------",
    "  ... .        ------cccss...............gsssscccsccccccceeeeecccceeecccccg.......        - ---",
    "    ..          -----cccccsssssg........gssssccccscccccsccccceeeecceeccccsg......          --",
    "                -----cccccccccssg.......ssssccccccccccccccccccEeecccccccgg.......",
    "                -----cccccccccsss.......ggssssssssscccccccccceEeccccccccsg.......",
    "                 ---cccccccccccssg......gsssccccccccccccccccccEEc-cccccccc......",
    "                 ---cccccccccccssg.......gsssccccscccsccccccccEeeccccccccc......",
    "                  -ccccccccccccssg........ggggcccscscscecccccceeecccccccccg....",
    "                  -ccccccccccccss..............sssssccceeecccceecggccccccc.....",
    "                  .ccccccccccccs................sssgcceec--ccceccggccgcccc.....",
    "                   .ccccccccccs.....................sseeecccccccg..ccscccc....",
    "                   .ccc.ccssssg.....................gseeeccccccg...csccccc....",
    "                   ..cc..gsssg.......................gceecssgg......gcccc.....",
    "                    .c................................gccsg..........ccc.....",
    "                    .c.......................................................",]


def grid(values, rows=(0, 140), envelope=None):
    """The map as an array (140 x 96): each pixel's value from `values` (class -> value), only in rows
    rows[0]..rows[1] - 1; envelope True/False: only inside/outside the envelope's outline."""
    g = np.zeros((140, 96))
    for i, line in enumerate(DAMAGE):
        r = DAMAGE_ROW + i
        if not rows[0] <= r < rows[1]:
            continue
        for c, ch in enumerate(line):
            if ch in values:
                if envelope is not None:
                    inside = abs(c - 48) < pa.radius(69.5 - r) + 0.5
                    if inside != envelope:
                        continue
                g[r, c] = values[ch]
    return g


def blur(a, sigma):
    """A Gaussian blur of an array (zero outside)."""
    if sigma <= 0:
        return a
    radius = int(math.ceil(sigma * 3))
    kern = np.exp(-np.arange(-radius, radius + 1) ** 2 / (2 * sigma * sigma))
    kern /= kern.sum()
    pad = np.pad(a, radius)
    tmp = sum(kv * np.roll(pad, i - radius, axis=1) for i, kv in enumerate(kern))
    out = sum(kv * np.roll(tmp, i - radius, axis=0) for i, kv in enumerate(kern))
    return out[radius:-radius, radius:-radius]


class Field:
    """A map over the picture (values at the pixels' centres), sampled at (X, y) between them."""

    def __init__(self, a):
        self.a = a

    def __call__(self, x, y):
        u = np.asarray(x, dtype=float) + 48.0
        v = 69.5 - np.asarray(y, dtype=float)
        c0, r0 = np.floor(u).astype(int), np.floor(v).astype(int)
        fu, fv = u - c0, v - r0

        def at(r, c):
            ok = (r >= 0) & (r < 140) & (c >= 0) & (c < 96)
            return np.where(ok, self.a[np.clip(r, 0, 139), np.clip(c, 0, 95)], 0.0)
        return ((1 - fu) * (1 - fv) * at(r0, c0) + fu * (1 - fv) * at(r0, c0 + 1) +
                (1 - fu) * fv * at(r0 + 1, c0) + fu * fv * at(r0 + 1, c0 + 1))


# The envelope's wounds (torn open where the map is black, gone or glowing, over the envelope from row 56 on) and
# the scorch round them; the glow; the wounds spread a little (where the mesh is made finer, the framework is
# built, the lower skin blackened inside).
OPEN = Field(blur(grid({"c": 0.8, "e": 1.0, "E": 1.0, "-": 1.0}, rows=(56, 140), envelope=True), 0.7))
SCORCH = Field(blur(grid({"s": 1.0, "g": 0.7}, rows=(56, 140), envelope=True), 0.9))
GLOW = Field(blur(grid({"e": 0.7, "E": 1.0}, rows=(56, 140), envelope=True), 0.8))
_NEAR = blur(grid({"c": 1.0, "e": 1.0, "E": 1.0, "-": 1.0}, rows=(56, 140), envelope=True), 2.5)
NEAR = Field(_NEAR)
_OPEN = blur(grid({"c": 0.8, "e": 1.0, "E": 1.0, "-": 1.0}, rows=(56, 140), envelope=True), 0.7)
EDGE = Field(blur(((_OPEN > 0.3) & (_OPEN < 0.85)).astype(float), 1.2))   # near the wounds' outlines
INSIDE = Field(blur(grid({"c": 1.0, "e": 1.0, "E": 1.0, "-": 1.0}, rows=(56, 140), envelope=True), 5.0))
WOUND_EDGE = 0.62             # the wound's outline (of the noisy field)
CHAR_EDGE = 0.42              # the fabric charred from here to the outline,
DARK_EDGE = 0.29              # darkly scorched from here,
SCORCH_EDGE = 0.17            # scorched from here
DROOP = 0.9                   # how far the torn edge droops into the hole
THICK = 0.45                  # the fabric's thickness shown at its torn edge
FINE = 0.85                   # the envelope's mesh along the wounds' outlines


def wound(x, y):
    """The wound field at (X, y) (arrays): the map's, its outline ragged."""
    x, y = np.atleast_1d(x), np.atleast_1d(y)
    base = OPEN(x, y)
    rag = np.array([0.15 * noise.noise(Vector((a * 0.65, b * 0.65, 3.1))) +
                    0.07 * noise.noise(Vector((a * 1.9, b * 1.9, 7.7))) for a, b in zip(x, y)])
    return base + rag * np.clip(base * 4.0, 0.0, 1.0)


# The bite out of the lower left edge: how far the outline is pulled in (pixels) by y, the damaged sprite's left
# edge against the intact one's (rows 97-114), faded out before the nose's row (y -42).
BITE = [(-26.0, 0.0), (-27.5, 1.0), (-28.5, 3.0), (-29.5, 4.0), (-30.5, 4.0), (-31.5, 5.0), (-32.5, 6.0),
        (-33.5, 5.5), (-34.5, 6.0), (-35.5, 6.0), (-36.5, 6.0), (-37.5, 5.0), (-38.5, 5.0), (-39.5, 4.6),
        (-40.5, 3.0), (-41.5, 1.2), (-42.2, 0.0)]


def bite(y):
    ys = [b[0] for b in BITE][::-1]
    ds = [b[1] for b in BITE][::-1]
    if y < ys[0] or y > ys[-1]:
        return 0.0
    return float(np.interp(y, ys, ds))


def materials():
    pal = k.level_palette()
    m = pa.materials()

    def mat(name, index, metallic=0.0, roughness=0.5, **kw):
        return k.material("zepd_" + name, palette=index, metallic=metallic, roughness=roughness, **kw)
    m.update({
        "char": mat("char", 0x02, 0.1, 0.9),
        "scorch": mat("scorch", 0x07, 0.05, 0.8),
        "burnt": mat("burnt", 0x05, 0.3, 0.7),
        "ember": mat("ember", 0x73, 0.0, 0.6, emission=pal[0x74], emission_strength=0.5),
        "ember_hot": mat("ember_hot", 0x76, 0.0, 0.5, emission=pal[0x77], emission_strength=0.6),
    })
    return m


# --- The envelope torn open ------------------------------------------------------------------------------------------

def near_rows():
    """The y range where wounds are near (for the finer rings)."""
    rows = np.nonzero(_NEAR.max(axis=1) > 0.05)[0]
    return (69.5 - rows.max() - 1.0, 69.5 - rows.min() + 1.0) if len(rows) else (0.0, 0.0)


_NEAR_Y = None


def step_at(y):
    global _NEAR_Y
    if _NEAR_Y is None:
        _NEAR_Y = near_rows()
    return FINE if _NEAR_Y[0] <= y <= _NEAR_Y[1] else pa.ENV_STEP


def angles_at(y):
    """polish_airship's ring angles, FINE apart where a wound is near."""
    base = pa.ring_angles(y)
    psis = np.linspace(-pa.ENV_TOP, pa.ENV_TOP, 1441)
    pts, _ = pa.surface(y, psis)
    near = EDGE(pts[:, 0], np.full(len(psis), y)) > 0.05
    if not near.any():
        return base
    arc = pa.PERIMETER * max(pa.radius(y), 0.3) / (2 * math.pi)
    step = FINE / arc
    runs, i = [], 0
    while i < len(psis):
        if near[i]:
            j = i
            while j + 1 < len(psis) and near[j + 1]:
                j += 1
            runs.append((psis[i], psis[j]))
            i = j + 1
        else:
            i += 1
    out = [a for a in base if not any(a0 < a < a1 for a0, a1 in runs)]
    for a0, a1 in runs:
        n = max(1, int(math.ceil((a1 - a0) / step)))
        out += [a0 + (a1 - a0) * t / n for t in range(n + 1)]
    out = sorted(set(round(a, 9) for a in out))
    return out


def tear_envelope(obj, m):
    """Cuts the wounds out of the envelope (the bite pulled in first), chars and scorches round them, droops their
    edges, gives them a charred thickness and blackens the lower skin inside."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.normal_update()
    # The bite: the left flank pulled in towards the axis.
    for v in bm.verts:
        if v.co.x < 0:
            d = bite(v.co.y)
            if d > 0:
                r = max(pa.radius(v.co.y), 1e-3)
                v.co.x += d * pa.smoothstep(0.45, 0.98, -v.co.x / r)
    bm.normal_update()
    verts = list(bm.verts)
    w = wound(np.array([v.co.x for v in verts]), np.array([v.co.y for v in verts]))
    values = {}
    for v, wv in zip(verts, w):
        values[v] = float(wv) if v.normal.z > 0.05 else min(float(wv), CHAR_EDGE * 0.95)
    for threshold in (WOUND_EDGE, CHAR_EDGE):
        mk.split_along(bm, values, threshold)
        for v in bm.verts:
            values.setdefault(v, threshold)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    gone = [f for f in bm.faces if sum(values[v] for v in f.verts) / len(f.verts) > WOUND_EDGE + 1e-4]
    bmesh.ops.delete(bm, geom=gone, context="FACES")
    for v in [v for v in bm.verts if not v.link_faces]:
        bm.verts.remove(v)
    bm.normal_update()
    slots = {}

    def slot(key):
        if key not in slots:
            slots[key] = mk.slot_of(obj, m[key])
        return slots[key]
    def banded(v):
        """The wound field for the bands round the holes: noisier than the outline, so they don't follow it."""
        return values[v] + (0.1 * noise.noise(Vector((v.co.x * 1.6, v.co.y * 1.6, 21.0))) +
                            0.05 * noise.noise(Vector((v.co.x * 4.0, v.co.y * 4.0, 33.0))))
    for f in bm.faces:
        c = f.calc_center_median()
        if max(values[v] for v in f.verts) >= CHAR_EDGE - 1e-4 and min(values[v] for v in f.verts) >= CHAR_EDGE - 1e-4:
            f.material_index = slot("char")
            continue
        mean = sum(banded(v) for v in f.verts) / len(f.verts)
        if mean > CHAR_EDGE:
            f.material_index = slot("char")
        elif mean > DARK_EDGE:
            f.material_index = slot("burnt")
        elif mean > SCORCH_EDGE or float(SCORCH(c.x, c.y)) + 0.2 * noise.noise(Vector((c.x, c.y, 41.0))) > 0.62:
            f.material_index = slot("scorch")
        elif f.normal.z < -0.05 and float(INSIDE(c.x, c.y)) > 0.04:
            f.material_index = slot("char")        # the lower skin, seen from inside through the wounds
    # The torn edges droop into the holes.
    for v in bm.verts:
        wv = values[v]
        if wv > SCORCH_EDGE:
            sag = DROOP * pa.smoothstep(SCORCH_EDGE, WOUND_EDGE, wv) ** 1.5
            sag *= 0.75 + 0.5 * (noise.noise(Vector((v.co.x * 0.9, v.co.y * 0.9, 11.0))) + 0.5)
            v.co -= v.normal * sag
    # The thickness at the torn edges: a charred strip inwards from each edge of a hole.
    inner = {}
    edges = [e for e in bm.edges if e.is_boundary and all(abs(values[v] - WOUND_EDGE) < 1e-3 for v in e.verts)]
    for e in edges:
        for v in e.verts:
            if v not in inner:
                inner[v] = bm.verts.new(v.co - v.normal * THICK)
    char = slot("char")
    for e in edges:
        a, b = e.verts
        f = bm.faces.new((a, b, inner[b], inner[a]))
        f.material_index = char
        f.smooth = True
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    return k.smooth(obj, 80)


def tear_net(m):
    """The ropes and knots gone over the wounds, charred near them."""
    for obj in [o for o in mk.meshes() if o.name.startswith("net_")]:
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        centres = [f.calc_center_median() for f in bm.faces]
        if not centres:
            bm.free()
            continue
        wv = wound(np.array([c.x for c in centres]), np.array([c.y for c in centres]))
        sv = SCORCH(np.array([c.x for c in centres]), np.array([c.y for c in centres]))
        gone = [f for f, a in zip(bm.faces, wv) if a > CHAR_EDGE + 0.06]
        char = mk.slot_of(obj, m["char"])
        dark = mk.slot_of(obj, m["burnt"])
        for f, a, s in zip(bm.faces, wv, sv):
            if a > DARK_EDGE:
                f.material_index = char
            elif a > SCORCH_EDGE * 0.7 or s > 0.5:
                f.material_index = dark
        bmesh.ops.delete(bm, geom=gone, context="FACES")
        for v in [v for v in bm.verts if not v.link_faces]:
            bm.verts.remove(v)
        bm.to_mesh(obj.data)
        bm.free()
        obj.data.update()


def pull_in(objects):
    """The bite's pull on other things lying on the envelope's left flank (the net)."""
    for obj in objects:
        for v in obj.data.vertices:
            if v.co.x < 0:
                d = bite(v.co.y)
                if d > 0:
                    r = max(pa.radius(v.co.y), 1e-3)
                    v.co.x += d * pa.smoothstep(0.45, 0.98, -v.co.x / r)
        obj.data.update()


# --- The framework inside ---------------------------------------------------------------------------------------------
# Ring frames across the envelope and girders along it, lattice beams (two rails, braces zigzagging between them)
# DEPTH below the fabric, built where a wound lays them open. Some in the long wound are broken, their ends sagging.
FRAMES_Y = (-47.5, -41.0, -34.5, -28.0, -21.5, -15.0, -8.5, -2.0, 4.5, 11.0)
GIRDERS = (-100.0, -84.0, -68.0, -52.0, -36.0, -20.0, -4.0, 12.0, 28.0, 44.0, 60.0, 76.0, 92.0)   # psi, degrees
DEPTH = 2.0
RAIL, RAIL_R, BRACE = 0.62, 0.26, 1.5     # the rails' half-spacing and radius, the braces' pitch


def inside_point(y, psi):
    """A point DEPTH under the envelope (as torn: the bite pulled in) and the envelope's normal there."""
    p, n = pa.surface(y, np.array([psi]))
    p, n = Vector(p[0]), Vector(n[0])
    q = p - n * DEPTH
    if q.x < 0:
        d = bite(q.y)
        if d > 0:
            q.x += d * pa.smoothstep(0.45, 0.98, -p.x / max(pa.radius(p.y), 1e-3))
    return q, n


def lattice(name, points, normals, mat):
    """A lattice beam along points (the rails either side of the path, in the skin's plane), braces between."""
    rails = ([], [])
    count = len(points)
    for i, (p, n) in enumerate(zip(points, normals)):
        t = (points[min(i + 1, count - 1)] - points[max(i - 1, 0)]).normalized()
        side = t.cross(n).normalized()
        rails[0].append(p + side * RAIL)
        rails[1].append(p - side * RAIL)
    parts = [mk.tube(name + "_a", rails[0], RAIL_R, mat, segments=3),
             mk.tube(name + "_b", rails[1], RAIL_R, mat, segments=3)]
    # braces: from one rail to the other every BRACE along the path
    length = sum((b - a).length for a, b in zip(points, points[1:]))
    steps = max(1, int(length / BRACE))
    cum = [0.0]
    for a, b in zip(points, points[1:]):
        cum.append(cum[-1] + (b - a).length)

    def at(s, rail):
        j = max(0, min(len(cum) - 2, int(np.searchsorted(cum, s) - 1)))
        f = (s - cum[j]) / max(cum[j + 1] - cum[j], 1e-9)
        return rails[rail][j].lerp(rails[rail][j + 1], min(max(f, 0.0), 1.0))
    for i in range(steps):
        s0, s1 = length * i / steps, length * (i + 1) / steps
        parts.append(mk.tube(name + "_brace", [at(s0, i % 2), at(s1, 1 - i % 2)], RAIL_R * 0.75, mat, segments=3))
    obj = parts[0]
    for extra in parts[1:]:
        extra.select_set(True)
    with bpy.context.temp_override(active_object=obj, selected_editable_objects=parts, object=obj):
        bpy.ops.object.join()
    obj.name = name
    k.recalc_normals(obj)
    return k.smooth(obj, 180)


def member_runs(samples, keep):
    """Runs of consecutive samples where keep holds."""
    runs, run = [], []
    for s, ok in zip(samples, keep):
        if ok:
            run.append(s)
        elif run:
            runs.append(run)
            run = []
    if run:
        runs.append(run)
    return [r for r in runs if len(r) >= 3]


def broken(run, rng):
    """A run in the long wound broken where it lies deepest in the hole, its ends sagging (or the run unchanged)."""
    ws = [wound([p.x], [p.y])[0] for p, _ in run]
    length = sum((b[0] - a[0]).length for a, b in zip(run, run[1:]))
    if length < 7.0 or max(ws) < 0.9 or run[0][0].y > -10.0 or rng.random() < 0.3:
        return [run]
    i0 = int(np.argmax(ws))
    gap = 0.9 + 0.6 * rng.random()
    out = []
    for part in (run[:i0], run[i0 + 1:][::-1]):
        kept = [(p, n) for p, n in part if (p - run[i0][0]).length > gap]
        sagged = []
        for p, n in kept:
            d = (p - run[i0][0]).length
            sag = 1.6 * max(0.0, 1 - d / 4.0) ** 2
            sagged.append((p - n * sag, n))
        if len(sagged) >= 3:
            out.append(sagged if part is run[:i0] else sagged[::-1])
    return out


def framework(m):
    rng = random.Random(7)
    members = []
    for y in FRAMES_Y:
        arc = pa.PERIMETER * pa.radius(y) / (2 * math.pi)
        n = int(2 * pa.ENV_TOP * arc / 1.2)
        samples = [inside_point(y, a) for a in np.linspace(-pa.ENV_TOP, pa.ENV_TOP, n)]
        keep = [wound([p.x], [p.y])[0] > 0.22 or NEAR(p.x, p.y) > 0.35 for p, _ in samples]
        members += [("frame_%d" % int(y), r) for r in member_runs(samples, keep)]
    for deg in GIRDERS:
        psi = math.radians(deg)
        samples = [inside_point(y, psi) for y in np.arange(-62.0, 24.0, 1.2)]
        keep = [wound([p.x], [p.y])[0] > 0.22 or NEAR(p.x, p.y) > 0.35 for p, _ in samples]
        members += [("girder_%d" % int(deg), r) for r in member_runs(samples, keep)]
    objs = []
    for i, (name, run) in enumerate(members):
        for j, piece in enumerate(broken(run, rng)):
            objs.append(lattice("%s_%d_%d" % (name, i, j), [p for p, _ in piece], [n for _, n in piece], m["burnt"]))
    for obj in objs:
        ember = mk.slot_of(obj, m["ember"])
        hot = mk.slot_of(obj, m["ember_hot"])
        for poly in obj.data.polygons:
            g = GLOW(poly.center.x, poly.center.y)
            g = float(g) + 0.25 * noise.noise(Vector((poly.center.x * 1.3, poly.center.y * 1.3, 5.0)))
            if g > 0.55:
                poly.material_index = hot
            elif g > 0.2:
                poly.material_index = ember
    # one object
    if not objs:
        return None
    for obj in objs:
        obj.select_set(True)
    with bpy.context.temp_override(active_object=objs[0], selected_editable_objects=objs, object=objs[0]):
        bpy.ops.object.join()
    objs[0].name = "framework"
    return objs[0]


def embers(m):
    """Glowing lumps caught in the framework where the sprites draw the brightest red in the wounds."""
    rng = random.Random(13)
    verts, faces, mats = [], [], []
    for i, line in enumerate(DAMAGE):
        r = DAMAGE_ROW + i
        if r < 56:
            continue
        for c, ch in enumerate(line):
            if ch not in "eE" or rng.random() > (0.55 if ch == "E" else 0.2):
                continue
            x, y = c - 48.0 + rng.uniform(-0.4, 0.4), 69.5 - r + rng.uniform(-0.4, 0.4)
            if wound([x], [y])[0] < WOUND_EDGE + 0.05 or abs(x) >= pa.radius(y) - 1.0:
                continue
            p, n = inside_point(y, pa.psi_at(x, y))
            p = p - n * rng.uniform(0.2, 1.4)
            a, b = pa.frame_of(n)
            rx, ry, rz = rng.uniform(0.45, 0.85), rng.uniform(0.4, 0.75), rng.uniform(0.3, 0.55)
            base = len(verts)
            seg, rings = 5, 3
            for j in range(1, rings):
                t = math.pi * j / rings
                for s in range(seg):
                    u = 2 * math.pi * (s + 0.5 * j) / seg
                    q = (a * (math.cos(u) * math.sin(t) * rx) + b * (math.sin(u) * math.sin(t) * ry) +
                         n * (math.cos(t) * rz))
                    verts.append(p + q * rng.uniform(0.85, 1.15))
            verts.append(p + n * rz)
            verts.append(p - n * rz)
            top, bottom = len(verts) - 2, len(verts) - 1
            for s in range(seg):
                s1 = (s + 1) % seg
                faces.append((top, base + s, base + s1))
                faces.append((base + s, base + seg + s, base + seg + s1, base + s1))
                faces.append((base + seg + s1, base + seg + s, bottom))
                mats += [ch] * 3
    if not verts:
        return None
    obj = k.mesh_object("embers", verts, faces, m["ember"])
    hot = mk.slot_of(obj, m["ember_hot"])
    for poly, ch in zip(obj.data.polygons, mats):
        if ch == "E":
            poly.material_index = hot
    k.recalc_normals(obj)
    return k.smooth(obj, 180)


# --- The other parts scorched -------------------------------------------------------------------------------------

def part_fields(rows, cols=(0, 96)):
    """Black, scorched and glowing fields of the map in a window (rows, cols)."""
    def windowed(values, sigma):
        g = grid(values, rows=rows)
        g[:, :cols[0]] = 0.0
        g[:, cols[1]:] = 0.0
        return Field(blur(g, sigma))
    return (windowed({"c": 1.0}, 0.6), windowed({"s": 1.0, "g": 0.6}, 0.7), windowed({"e": 0.7, "E": 1.0}, 0.6))


def burn(names, m, rows, cols=(0, 96), dent=0.6, red=False, subdivide=1, up=-0.2):
    """Paints the named objects' faces that face up where the map is black (pressed in by dent), scorched or
    glowing in the window (rows, cols); subdivide: the faces there cut that many times first."""
    black, scorched, glow = part_fields(rows, cols)
    for obj in [o for o in mk.meshes() if o.name in names]:
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bm.normal_update()
        for _ in range(subdivide):
            faces = [f for f in bm.faces for c in [f.calc_center_median()] if f.normal.z > up and
                     max(black(c.x, c.y), scorched(c.x, c.y), glow(c.x, c.y)) > 0.08]
            edges = list({e for f in faces for e in f.edges})
            if edges:
                bmesh.ops.subdivide_edges(bm, edges=edges, cuts=1, use_grid_fill=True)
            bm.normal_update()
        char = mk.slot_of(obj, m["char"])
        scorch = mk.slot_of(obj, m["char" if red else "scorch"])
        ember = mk.slot_of(obj, m["ember"])
        for f in bm.faces:
            if f.normal.z <= up:
                continue
            c = f.calc_center_median()
            b = float(black(c.x, c.y)) + 0.15 * noise.noise(Vector((c.x * 1.1, c.y * 1.1, 2.0)))
            if glow(c.x, c.y) > 0.45:
                f.material_index = ember
            elif b > 0.45:
                f.material_index = char
            elif b > 0.25 or scorched(c.x, c.y) > 0.4:
                f.material_index = scorch
        if dent:
            for v in bm.verts:
                if v.normal.z > up:
                    v.co -= v.normal * dent * min(1.0, float(black(v.co.x, v.co.y)) * 1.4)
        bm.to_mesh(obj.data)
        bm.free()
        obj.data.update()


def torn_gun(m):
    """The right pod torn off below its band: its barrel and muzzle gone, its body, bands and pipes broken off at
    row 80 in a jagged edge, charred, embers in the break."""
    for name in ("gun_barrel_r", "gun_barrel_ring_r", "gun_muzzle_r", "gun_bore_r", "gun_fire_r", "gun_fire_ring_r",
                 "gun_band2_r"):
        obj = bpy.data.objects.get(name)
        if obj:
            bpy.data.objects.remove(obj)
    cut_y = -10.3
    rng = random.Random(3)
    for name in ("gun_body_r", "gun_pipe_side_r"):
        obj = bpy.data.objects[name]
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        # a finer grid near the break, then the part below it gone
        for y in (cut_y + 2.4, cut_y + 1.2):
            bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-5,
                                   plane_co=(0, y, 0), plane_no=(0, 1, 0))
        res = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-5,
                                     plane_co=(0, cut_y, 0), plane_no=(0, -1, 0), clear_outer=True)
        rim = [e for e in res["geom_cut"] if isinstance(e, bmesh.types.BMEdge) and e.is_valid and e.is_boundary]
        char = mk.slot_of(obj, m["char"])
        if rim:
            filled = bmesh.ops.holes_fill(bm, edges=rim, sides=0)
            for f in filled["faces"]:
                f.material_index = char
        # the break jagged: the rim pushed up and down, the faces near it charred
        for v in bm.verts:
            if v.co.y < cut_y + 0.05:
                v.co.y += rng.uniform(-0.2, 1.4)
        for f in bm.faces:
            if f.calc_center_median().y < cut_y + 2.6:
                f.material_index = char
        bm.to_mesh(obj.data)
        bm.free()
        obj.data.update()
    # embers in the break
    body = bpy.data.objects["gun_body_r"]
    gx = -pa.GUN_X
    for i in range(5):
        a = 2 * math.pi * (i + rng.random() * 0.5) / 5
        r = rng.uniform(1.2, 3.2)
        e = k.ellipsoid("gun_ember_%d" % i, (gx + r * math.cos(a), cut_y + 0.5, pa.GUN_Z + r * math.sin(a)),
                        (0.55, 0.4, 0.55), m["ember_hot" if i % 2 else "ember"], 8, 4)
        k.smooth(e, 60)
    return body


def blade_stubs(m):
    """The fan's blades broken off near the hub: short stubs, their ends jagged and charred."""
    rng = random.Random(11)
    out = []
    for i in range(pa.BLADES):
        phi0 = 2 * math.pi * i / pa.BLADES
        tip = rng.uniform(5.2, 8.6)
        rings = []
        for rho in (pa.BLADE_ROOT, 4.2, tip - 0.7, tip):
            f = (rho - pa.BLADE_ROOT) / (pa.BLADE_TIP - pa.BLADE_ROOT)
            chord = 4.2 + 3.0 * f ** 0.8
            pitch = math.radians(30.0 - 12.0 * f)
            thick = 0.75 - 0.38 * f
            er = pa.FX * math.cos(phi0) + pa.FB * math.sin(phi0)
            et = -pa.FX * math.sin(phi0) + pa.FB * math.cos(phi0)
            along = et * math.cos(pitch) + pa.FA * math.sin(pitch)
            normal = -et * math.sin(pitch) + pa.FA * math.cos(pitch)
            ring = []
            for j in range(12):
                a = 2 * math.pi * j / 12
                u, v = math.cos(a), math.sin(a)
                d = 0.3 * chord / 6.0 * (1 - u * u) + v * thick / 2 * (0.35 + 0.65 * math.sqrt(max(0.0, 1 - u * u)))
                jag = rng.uniform(-0.9, 0.6) if rho == tip else 0.0
                ring.append(pa.FAN_C + er * (rho + jag) + along * (u * chord / 2) + normal * d)
            rings.append(ring)
        obj = k.loft("blade_stub_%d" % i, rings, m["blade"])
        char = mk.slot_of(obj, m["char"])
        for poly in obj.data.polygons:
            if (poly.center - pa.FAN_C).length > tip - 1.0:
                poly.material_index = char
        out.append(k.smooth(obj, 50))
    return out


# --- Build ---------------------------------------------------------------------------------------------------------

def build_whole():
    m = materials()
    pa.envelope(m, step_at, angles_at)
    pa.net(m)
    pa.cowl(m)
    pa.duct(m)
    pa.fan_hub(m)
    blade_stubs(m)
    pa.bridge(m)
    pa.duct_boots(m)
    pa.frames(m)
    pa.mirror_x(pa.gun(m))
    tear_envelope(bpy.data.objects["envelope"], m)
    pull_in([o for o in mk.meshes() if o.name.startswith("net_")])
    tear_net(m)
    framework(m)
    embers(m)
    # the duct holed and scorched either side of its back, the cowl's right shoulder burnt, the gate's crossbar
    # holed, the mounts scorched, the left pod's front end scorched
    burn({"duct"}, m, (10, 29), dent=0.9, red=True, subdivide=1, up=0.05)
    burn({"cowl", "cowl_rim", "cowl_seam_r", "duct_boot_r", "hub_fairing"}, m, (28, 40), cols=(52, 96), dent=0.7,
         subdivide=0)
    burn({"gate_bar", "gate_stem", "gate_leg_in_l", "gate_leg_in_r", "gate_leg_out_l", "gate_leg_out_r",
          "bracket_l", "bracket_r", "bracket_prong_l", "bracket_prong_r"}, m, (42, 51), dent=0.4, red=True,
         subdivide=0)
    burn({"gun_mount", "gun_mount_r", "gun_cap", "gun_cap_r", "gun_strut", "gun_strut_r", "gun_rod", "gun_rod_r"},
         m, (54, 63), dent=0.3, red=True, subdivide=1)
    burn({"gun_body", "gun_band2", "gun_barrel"}, m, (81, 91), cols=(0, 12), dent=0.2, subdivide=1)
    burn({"gun_body_r", "gun_band_r", "gun_pipe_side_r", "gun_pipe_top_r"}, m, (70, 82), cols=(84, 96), dent=0.3,
         subdivide=1)
    torn_gun(m)
    whole = mk.meshes()
    pa.shift(whole)
    bpy.context.view_layer.update()
    return whole, m


def whole_mask(sheet):
    mask = [[False] * 96 for _ in range(140)]
    for _, sprite, box in PIECES:
        c0, r0 = pa.cell_of(box)
        part = k.sprite_mask(sheet, sprite)
        for y in range(28):
            for x in range(24):
                if part[y][x]:
                    mask[r0 + y][c0 + x] = True
    return mask


def build():
    k.reset()
    options = k.args()
    pa.STATS = "stats" in options
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    whole, m = build_whole()
    print("whole damaged airship: %d triangles, %d objects" % (mk.triangles(whole), len(whole)))
    sheet = os.path.join(options["check"], "enemy_I.png") if "check" in options else None
    if sheet:
        mk.compare("whole damaged (I 11 13 / 47-53 / 85-91 / 123-129 / 162-166)", mk.coverage(whole, 96, 140),
                   whole_mask(sheet))
    bpy.context.scene.view_settings.view_transform = "Standard"
    if "preview" in options:
        mk.preview(options["preview"] + "zeppelin_damaged_whole", whole, size=(96, 140), scale=6, distance=4.0)
    if "whole" in options:
        mk.export(whole, options["whole"])
    pieces = [p for p in PIECES if not only or p[0] in only]
    pa.export_pieces(whole, m, pieces, out, sheet, options.get("preview"))


if __name__ == "__main__":
    build()
