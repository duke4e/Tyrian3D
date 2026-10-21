"""The big glass globe of DELI, New Deli, BONUS and HARVEST (sheet U, written u in models.cfg: sprites 153, 155 above
191, 193, 2x2 each: one 48 x 56 picture; enemies 241-244 of episodes 1, 3 and 4), polished (2026-10-21; it replaces
wave3_ag.py's globe: an embossed ico-ellipsoid in a plain see-through shell, the green kept in every frame).

The levels put the four together (DELI's and DELIANI's events 15 at 4510-4724, New Deli's at 1010-4724, HARVEST's at
2010-2224, all in the sky; BONUS' events 7 at 4110-4724, on top): 241 (191) at (x, y) and 242 (193) at (x + 24, y),
then 14 ticks later 243 (153) and 244 (155) at the same x, 28 pixels above them, and at once an event 24 (Enemy
Global Animate, dat2 0) on their link, so the four restart their animation together and stay in step. No episode 6
level takes them (VAULT takes BONUS waves, none with the globe). No other enemy shows any of their 40 sprites
(catalog.json), and none is another sprite's pixels mirrored, turned or in other ramps (twins2.py).

As the sprites and their 4x upscales draw it (columns c 0-47 and rows r 0-55 of the 48 x 56 picture): a clear glass
ball (columns 1-45 of rows 4-50) round a green creature. The glass shows only at its rim (a dark green ring, ramp 2
shades 0-2, broad on the right where a crescent of it stands apart: columns 41-45 of rows 19-37, the background
showing through the clear glass between it and the creature at columns 39-40 of rows 23-29) and in a lit crescent
just inside its lower right rim (from row 34 at the right round to row 44 at the bottom, brightest at columns 34-38
of rows 39-42), where the light through the ball gathers, as in a marble. Inside, filling the rest of it, the
creature: dark green (shades 3-6 of ramp 2) with bulging bright green lobes (ramp 12: 0xc3-0xcf), the biggest at
the upper left (columns 13-21 of rows 9-21, white-green in its middle, where the glass also gleams), a small one at
the top (columns 20-25 of rows 9-15), one at the lower right (columns 34-38 of rows 34-38) and a small one low in the
middle (rows 43-46); green bands sweep round its lower half from the left (rows 25-29, 34-38, 40-44), dark creases
between them; its upper right is a dark green mass.

Its 19 frames (one a game tick, 0 1 ... 9 ... 1 0: about half a second a cycle) recolour that picture shade by shade,
the mid tones first (frame 0's shades, as the most common index each takes): 1 nearly the same; 2, 3 and 4 (3 = 4)
the darker greens olive (0xc3 0x26, 0xc4 0x27, 0xc6 0x29), the brightest lobes still green; 5 and 6 the glass's
dark greens grey and blue-grey (0x21 0x01, 0x22 0x62, 0x24 0x64), the creature olive, its brightest parts pale (0x2b,
the highlight pale cyan 0x8b); 7 and 8 the creature blue-grey (0x66, 0x67, 0x6b, 0x8c); 9 the whole ball a smooth
shut shell of pale lavender (ramp 5 only: 0x50-0x5f; its highlight white at the upper left, the same lit crescent at
the lower right). The animation is the ball's look itself (a creature in glass fading to a shut shell and back,
twice a second), not a flicker, so it gets frame models: five looks, each the same geometry with its materials
changed: glass_globe_* (frames 0 and 1), _<frame 2> (2, 3, 4), _<frame 5> (5, 6), _<frame 7> (7, 8), _<frame 9> (9).

Built as a ball of glass round a creature:
- the glass: an ellipsoid of even triangles (22.4 x 23.4 pixels as the sprite draws it, 15.5 high, standing on its
  layer), its unseen underside left out, see-through and glossy, banded by how squarely the game's camera looks at it
  (either way: the far half seen through the near one has the near half's bands behind them): a dark rim (narrow at
  the upper left, broad at the lower right, as the sprite draws it: its width set by the direction from the middle,
  the same for both halves along a line of sight), a lighter band, clear in the middle; and on its near side the lit
  crescent on the inner part of its lower right rim, a soft band round a hot one, glowing faintly. Its
  faces are sorted from the camera's far side to its near side (the game draws see-through materials blended, in the
  order of their materials and then of their triangles, without depth writes or culling; the model does not turn).
  In the shut look (frame 9) it is opaque lavender, hiding the creature.
- the creature: an ellipsoid of two-sided half-widths (19.4 to the left, 16.6 to the right, 19.9 up the screen,
  21.4 down it, 13.6 high) filling the glass but for its dark rim and the clear glass at its right, its surface
  pushed out where the sprite is bright and in where it is dark (the lobes bulging, the creases sunk; kept inside
  the glass), painted with the sprite's shades in bands cut along smooth contours (polish_sphere_nozzle.split_along);
  the painting and the relief are laid out as the sprite draws them seen from VIEW_TILT degrees off straight down
  from the bottom of the screen (the game's camera is 20 degrees off: a point higher than the ball's middle takes
  the sprite's colour from further up the screen), so that the lobes sit where the sprite draws them in the game's
  view. The glowing lobe low on the right lies on the creature's steep flank, where the relief fades: it is a lens
  of its own there (LOBE), facing half way between the surface and the camera, painted in the same bands (brightest
  in its middle). The bands glow in their own colours (look 0: 0.03-0.45; less in the later looks, none in the shut
  one); the glass' crescent 0.04-0.34. Emission stays well under 1 (the game's bloom and the glow halo add to it).
  Its underside is cut away and closed flat.
The whole ball is then cut along the sprites' edges (x = 0, y = 0; the glass, a single surface, cut without caps),
each piece moved so that its sprite's centre is its origin; every mesh is triangulated before export
(polish_k_pod.triangulate), each piece's parts joined into one mesh, its glass faces sorted far side first. The
creature's cuts are closed by caps on an even grid of triangles (cut_creature), painted in the creature's dark and
middle bands (the picture broadly blurred where the camera sees each point, no lighter than CAP_MAX) and shaded with
the creature's normals rather than the flat caps' own: the game draws every batch without culling and a piece that
is fading in (its first frames in sight: render_gpu.c's state->appear) see-through, both sides and without depth
writes, and the pieces fade in at different times, so a neighbour's flat caps (dark, flat-lit, one side catching
the sun) showed through a fading piece as seams down and across the ball, off-centre on the screen most (the game's
camera is a perspective one); so made they read as the creature's inside, as they do when a piece is shot away.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up (towards the camera) from the
layer (z = 0); the whole's origin is the picture's middle (pixel edge 24, 28): column c is x = c + 0.5 - 24, row r is
y = 27.5 - r. The pieces' centres: 153 (-12, 14), 155 (12, 14), 191 (-12, -14), 193 (12, -14).

models.cfg: model glass_globe_tl / _tr / _bl / _br enemies/glass_globe_*.glb origin (unchanged); add the frame models
(model glass_globe_tl_161 enemies/glass_globe_tl_161.glb origin, and so on: tl _161 _233 _241 _246, tr _163 _235 _243
_170, bl _199 _271 _279 _284, br _201 _273 _281 _208) and their frame lines (frame u 161 glass_globe_tl_161, frame u
165 glass_globe_tl_161, frame u 229 glass_globe_tl_161, frame u 233 glass_globe_tl_233, frame u 237
glass_globe_tl_233, frame u 241 glass_globe_tl_241, frame u 91 glass_globe_tl_241, frame u 246 glass_globe_tl_246,
the same for the other pieces); the sprite lines stay (sprite u 153 glass_globe_tl yaw=0 glow=18:0.2 ...: the glow
follows the frames' colour).

Replaces wave3_ag.py's globe: remove its section ("# --- u 153 155 / 191 193: the glass globe": GLOBE, GLOBE_C,
GLOBE_R, globe_whole(), the kit.PROTECT line and the kit.pieced("glass_globe", ...) registration) and the glass_globe
paragraph of its docstring, and wave3_ag_art.py's SPHERE (only that section reads it); wave3_ag_tower.py, which
imports wave3_ag_kit, is not touched.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes of the
whole and of each piece against enemy_U.png), --preview <prefix> (the whole's and each model's top and 3/4 views),
--only <model,...>, --whole <file.glb> (the uncut ball, first look, for looking at).
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
from polish_machine_kit import k, smoothstep  # noqa: E402
import polish_deli_boss as db  # noqa: E402  (join, drop_unused)
from polish_ixm_dock import Shading  # noqa: E402  (normals looked up on the coplanar source triangle)
from polish_k_pod import triangulate  # noqa: E402
from polish_orb_red import band_split  # noqa: E402
from polish_sphere_nozzle import split_along  # noqa: E402
from mathutils.geometry import delaunay_2d_cdt  # noqa: E402

# The pieces: model, the box it covers in the whole (x0, x1, y0, y1), its sprite in each of the ten frames.
PIECES = [("glass_globe_tl", (-24.0, 0.0, 0.0, 28.0), [153, 157, 161, 165, 229, 233, 237, 241, 91, 246]),
          ("glass_globe_tr", (0.0, 24.0, 0.0, 28.0), [155, 159, 163, 167, 231, 235, 239, 243, 93, 170]),
          ("glass_globe_bl", (-24.0, 0.0, -28.0, 0.0), [191, 195, 199, 203, 267, 271, 275, 279, 129, 284]),
          ("glass_globe_br", (0.0, 24.0, -28.0, 0.0), [193, 197, 201, 205, 269, 273, 277, 281, 131, 208])]
CELLS = {153: (0, 0), 155: (24, 0), 191: (0, 28), 193: (24, 28)}
# The looks: the frames (0-9) each shows; the model is named after its first frame's sprite (the first look's
# models are the sprites' own).
LOOK_FRAMES = [(0, 1), (2, 3, 4), (5, 6), (7, 8), (9,)]

VIEW_TILT = 20.0
T = math.radians(VIEW_TILT)
TOWARDS_VIEW = Vector((0.0, -math.sin(T), math.cos(T)))
SCREEN_UP = Vector((0.0, math.cos(T), math.sin(T)))

GLOBE_C, GLOBE_R = Vector((-0.5, 0.5, 15.5)), (22.4, 23.4, 15.5)
GLASS_CUT = 0.62                 # the glass' underside (below this fraction of its height under its middle) left out
# The creature: its middle, its half-widths (left, right; up the screen, down; height): it fills the glass but for
# a dark rim and the clear glass at its right.
CORE_C, CORE_R = Vector((-1.6, 1.2, 15.0)), ((19.4, 16.6), (19.9, 21.4), 13.6)
CORE_CUT = 0.45                  # the creature's underside cut away (and closed flat)
CORE_ROOM = 0.95                 # the creature (its relief too) stays inside this fraction of the glass
CAP_STEP = 1.8                   # the grid the caps of its cuts are triangulated on (pixels)
CAP_BLUR, CAP_MAX = 3.0, 7.0     # the caps' painting: the picture blurred this much, no lighter than this level
RELIEF = (2.3, 0.42, -0.9, 1.9)  # displacement per unit of brightness over the level, its limits (pixels)
# The glowing lobe low on the right, on the creature's steep flank (where the relief fades): a lens on its surface
# where the camera sees the sprite's lobe (x, y), its half-axes (along the screen, across, out), how far it stands
# out, its peak level and its rim's (painted max(the picture, a dome falling from the peak to the rim's level));
# it faces half way between the surface's normal and the camera.
LOBE = ((12.3, -8.2), (4.0, 3.5, 1.05), 0.05, 13.8, 7.0)

# Frame 0's picture, rows 4-50 (row 4 first), its shades as levels 0-e: ramp 2's 0x20 0x21 0x22 0x24 0x25 0x26 (0-5)
# and ramp 12's 0xc3 0xc4 0xc6 0xc7 0xc9 0xca 0xcb 0xce 0xcf (6-e); '.' transparent.
ART = """
....................02333222....................
................024444444443222.................
.............123445555555544443211..............
............23445555555555554443321.............
..........124466666666776555544433321...........
.........0046666666678888855554443332...........
........12346666666778aa98755554443331.0........
.......14532567777788addda86555544433310........
......135653565677788cdedc865555544333310.......
.....2356666566777678ccddc7645555544333210......
.....245667789accdc879acca6445555554433220......
....245667789acddeed8799a654444555544332210.....
....245667789acddeeed7765555554455544434221.....
...1356677789acdddeee9655566665445544444221.....
...1356677789acdddeee9556666666544554444221.....
..12456677789accdddee9566777666654554555321.....
..124566777789accdddd8567777666654555555321.0...
..12456677777899aaccd7567777666653455665331.....
..12456677777789999aa7567777666652356665331.....
.102456677777778888897367777666642366665420.00..
.10245666777777778888406677766653156666642..00..
.1014556667888777776222667766665217777652..000..
.10135566689a988654447366766666446777754..0000..
.2301456678a964446677745666666657887752..11000..
.2311345689744799887773556666698887541.1001000..
.246313458647aa977776644556667ca86410011011010..
.14673134636986666666652455555c753111111110010..
.02556233427766666666664245555c641112222210010..
.02356622327666666666665433554a62112444321012...
..2246762116556666666666533343862124676421012...
..0235777335555555555556666333663159cc9511022...
..022357766345555554457a88822057339ced9410132...
...123357767554444457cdd8871114735cedc721023....
...11253457888666679dec75770.04726cdc8410242....
....123533468a9ccdddc8545760003625ab95200550....
....012354334667786545655752114623665200373.....
.....0122674334444447aa6575545652222100374......
.....001226875543345ad96476664332111012771......
......001225888866789a64554332221100148a2.......
.......100025899aaa985699a975211000259c4........
........110001689999748ddca521000137ac5.........
.........11110036888612854200001359ca4..........
..........11111123553211111112457aca3...........
............11122222433333344589993.............
.............111122333566678888531..............
................111122233333211.................
...................111111111....................
"""
ART_ROW0 = 4

# The creature's bands: (lowest level, role); and each look's (palette index, emission) for every role.
CORE_BANDS = [(-99.0, "k0"), (2.5, "k1"), (4.0, "k2"), (5.5, "k3"), (6.5, "k4"), (7.6, "k5"), (9.4, "k6"),
              (11.0, "k7"), (12.6, "k8")]
CORE_LOOKS = [
    {"k0": (0x22, 0.0), "k1": (0x24, 0.03), "k2": (0x26, 0.05), "k3": (0xc3, 0.1), "k4": (0xc4, 0.14),
     "k5": (0xc6, 0.18), "k6": (0xc9, 0.25), "k7": (0xcb, 0.34), "k8": (0xce, 0.45)},
    {"k0": (0x22, 0.0), "k1": (0x24, 0.0), "k2": (0x26, 0.02), "k3": (0x26, 0.03), "k4": (0x27, 0.04),
     "k5": (0x29, 0.05), "k6": (0xc6, 0.12), "k7": (0xcb, 0.28), "k8": (0xcd, 0.38)},
    {"k0": (0x62, 0.0), "k1": (0x64, 0.0), "k2": (0x04, 0.0), "k3": (0x26, 0.02), "k4": (0x27, 0.03),
     "k5": (0x29, 0.04), "k6": (0x2a, 0.06), "k7": (0x2b, 0.08), "k8": (0x8b, 0.12)},
    {"k0": (0x52, 0.0), "k1": (0x64, 0.0), "k2": (0x04, 0.0), "k3": (0x66, 0.02), "k4": (0x67, 0.03),
     "k5": (0x29, 0.03), "k6": (0x2a, 0.04), "k7": (0x6b, 0.05), "k8": (0x8c, 0.1)},
    {"k0": (0x52, 0.0), "k1": (0x53, 0.0), "k2": (0x55, 0.0), "k3": (0x56, 0.0), "k4": (0x57, 0.0),
     "k5": (0x58, 0.0), "k6": (0x5a, 0.0), "k7": (0x5b, 0.0), "k8": (0x5c, 0.0)},
]
# The glass' bands by how squarely the camera looks at it (lowest value, role), the crescent; each look's (palette
# index, alpha, emission) for them.
# The rim's width by the screen angle: the view factor under which the glass is rim (RIM_S - RIM_SKEW * cos(angle -
# RIM_LIGHT)): narrow at the upper left, broad at the lower right; the mid band MID_W beyond it.
RIM_S, RIM_SKEW, RIM_LIGHT, MID_W = 0.47, 0.14, 120.0, 0.2
GLASS_BANDS = [(-9.0, "rim"), (0.0, "mid"), (MID_W, "clear")]     # by the view factor less the rim's width
CRESCENT_S = (-0.17, -0.12, 0.02, 0.07)         # its band on the rim's inner part (in, full, full, out)
CRESCENT_ANGLE = (-100.0, -86.0, -24.0, -10.0)  # its screen angles (degrees from the right, as the camera sees it)
GLASS_LOOKS = [
    {"rim": (0x21, 0.85, 0.0), "mid": (0x22, 0.34, 0.0), "clear": (0x24, 0.08, 0.0), "crescent": (0xc7, 0.55, 0.18),
     "crescent_hot": (0xcb, 0.8, 0.34)},
    {"rim": (0x21, 0.85, 0.0), "mid": (0x22, 0.34, 0.0), "clear": (0x24, 0.08, 0.0), "crescent": (0xc4, 0.55, 0.12),
     "crescent_hot": (0xc9, 0.8, 0.24)},
    {"rim": (0x01, 0.85, 0.0), "mid": (0x62, 0.4, 0.0), "clear": (0x64, 0.14, 0.0), "crescent": (0x28, 0.55, 0.06),
     "crescent_hot": (0x2b, 0.8, 0.12)},
    {"rim": (0x50, 0.88, 0.0), "mid": (0x52, 0.46, 0.0), "clear": (0x64, 0.2, 0.0), "crescent": (0x68, 0.55, 0.05),
     "crescent_hot": (0x6b, 0.8, 0.1)},
    {"rim": (0x51, 1.0, 0.0), "mid": (0x54, 1.0, 0.02), "clear": (0x57, 1.0, 0.04), "crescent": (0x58, 1.0, 0.04),
     "crescent_hot": (0x5b, 1.0, 0.1)},
]
GLASS_ROLES = ["rim", "mid", "clear", "crescent", "crescent_hot"]
CRESCENT_CUTS = (0.25, 0.65)     # the crescent's soft band from the first, its hot middle from the second


# --- Materials -------------------------------------------------------------------------------------------------------

def look_materials(look):
    """The look's materials by role (the creature's k0-k8, the glass' rim, mid, clear, crescent)."""
    pal = k.level_palette()
    out = {}
    for role, (index, glow) in CORE_LOOKS[look].items():
        kw = dict(emission=pal[index], emission_strength=glow) if glow > 0 else {}
        out[role] = k.material(f"globe{look}_{role}", palette=index, metallic=0.05, roughness=0.28, **kw)
    for role, (index, alpha, glow) in GLASS_LOOKS[look].items():
        kw = dict(emission=pal[index], emission_strength=glow) if glow > 0 else {}
        if alpha < 1.0:
            kw["alpha"] = alpha
        out[role] = k.material(f"globe{look}_{role}", palette=index, metallic=0.1, roughness=0.05 if alpha < 1 else
                               0.18, **kw)
    return out


# --- The picture ---------------------------------------------------------------------------------------------------

def art():
    """ART as levels on the 56 x 48 grid (None where transparent)."""
    grid = [[None] * 48 for _ in range(56)]
    for r, line in enumerate(ART.strip("\n").split("\n")):
        for c, ch in enumerate(line):
            if ch != ".":
                grid[ART_ROW0 + r][c] = int(ch, 16)
    return grid


def blurred(grid, sigma, fill=1.0):
    """The levels blurred (a Gaussian of sigma pixels), transparent pixels counted as fill."""
    r = int(math.ceil(3 * sigma))
    kern = [math.exp(-0.5 * (i / sigma) ** 2) for i in range(-r, r + 1)]
    total = sum(kern)
    kern = [w / total for w in kern]
    a = [[fill if v is None else float(v) for v in row] for row in grid]
    h, w = len(a), len(a[0])
    tmp = [[sum(kern[i + r] * a[y][min(max(x + i, 0), w - 1)] for i in range(-r, r + 1)) for x in range(w)]
           for y in range(h)]
    return [[sum(kern[i + r] * tmp[min(max(y + i, 0), h - 1)][x] for i in range(-r, r + 1)) for x in range(w)]
            for y in range(h)]


def sample(a, x, y):
    """Bilinear sample of a picture grid at the whole's (x, y) (pixel centres at x = c + 0.5 - 24, y = 27.5 - r)."""
    u, v = x + 24.0 - 0.5, 27.5 - y
    h, w = len(a), len(a[0])
    c0, r0 = int(math.floor(u)), int(math.floor(v))
    fu, fv = u - c0, v - r0

    def at(r, c):
        return a[min(max(r, 0), h - 1)][min(max(c, 0), w - 1)]
    return ((1 - fu) * (1 - fv) * at(r0, c0) + fu * (1 - fv) * at(r0, c0 + 1) + (1 - fu) * fv * at(r0 + 1, c0) +
            fu * fv * at(r0 + 1, c0 + 1))


def seen_at(co):
    """Where the game's camera sees a point, in the picture's (x, y): a point higher than the ball's middle further up
    the screen."""
    return co.x, co.y + (co.z - GLOBE_C.z) * math.tan(T)


# --- Shapes ----------------------------------------------------------------------------------------------------------

def ellipsoid_bm(centre, radii, subdivisions, finer=None):
    """An ellipsoid of even triangles (an icosphere scaled), once more subdivided where finer(unit direction) holds.
    radii (x, y, z), each a number or (on the - side, on the + side)."""
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subdivisions, radius=1.0)
    if finer is not None:
        edges = [e for e in bm.edges if all(finer(v.co.normalized()) for v in e.verts)]
        bmesh.ops.subdivide_edges(bm, edges=edges, cuts=1, use_grid_fill=True)
        bmesh.ops.triangulate(bm, faces=bm.faces[:])
    two = [r if isinstance(r, tuple) else (r, r) for r in radii]
    for v in bm.verts:
        n = v.co.normalized()
        v.co = Vector([c + d * (r[1] if d > 0 else r[0]) for c, d, r in zip(centre, n, two)])
    return bm


def two_sided_normal(co, centre, radii):
    """The normal of an ellipsoid of two-sided radii (ellipsoid_bm's) at a point on it."""
    d = co - centre
    two = [r if isinstance(r, tuple) else (r, r) for r in radii]
    r = [rr[1] if dd > 0 else rr[0] for dd, rr in zip(d, two)]
    return Vector((d.x / r[0] ** 2, d.y / r[1] ** 2, d.z / r[2] ** 2)).normalized()


def inside_glass(co, room):
    """co pulled back inside room times the glass (along the line from the glass' middle) if it lies outside."""
    d = co - GLOBE_C
    q = math.sqrt((d.x / GLOBE_R[0]) ** 2 + (d.y / GLOBE_R[1]) ** 2 + (d.z / GLOBE_R[2]) ** 2)
    return co if q <= room else GLOBE_C + d * (room / q)


def ellipsoid_normal(co, centre, radii):
    d = co - centre
    return Vector((d.x / radii[0] ** 2, d.y / radii[1] ** 2, d.z / radii[2] ** 2)).normalized()


def to_object(name, bm, mats, roles):
    """A bmesh as an object, its faces given the materials of their roles (a list per face)."""
    order = []
    for role in roles:
        if role not in order:
            order.append(role)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    for role in order:
        mesh.materials.append(mats[role])
    mesh.polygons.foreach_set("material_index", [order.index(r) for r in roles])
    k.recalc_normals(obj)
    return obj


_PAINTING = []


def painting():
    """The picture blurred for the relief (soft), for the bands (sharp) and for the caps of the cuts (broad)."""
    if not _PAINTING:
        grid = art()
        _PAINTING.extend((blurred(grid, 1.6), blurred(grid, 0.82), blurred(grid, CAP_BLUR)))
    return _PAINTING


def creature(mats):
    """The creature: an ellipsoid pushed out where the picture is bright, painted in its bands."""
    soft, sharp, _ = painting()
    bm = ellipsoid_bm(CORE_C, CORE_R, 4, finer=lambda n: n.dot(TOWARDS_VIEW) > 0.0)
    for v in bm.verts:
        v.co = inside_glass(v.co, CORE_ROOM)
    # Its unseen underside cut away and closed flat.
    z_cut = CORE_C.z - CORE_CUT * CORE_R[2]
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-5, plane_co=(0, 0, z_cut),
                           plane_no=(0, 0, -1), clear_outer=True)
    open_edges = [e for e in bm.edges if len(e.link_faces) == 1]
    bmesh.ops.holes_fill(bm, edges=open_edges, sides=0)
    # The relief: out along the ellipsoid's normal by the picture's brightness where the camera sees the point,
    # fading out towards the creature's outline as the camera sees it and on its flat underside.
    gain, level, lo, hi = RELIEF
    for v in bm.verts:
        if v.co.z < z_cut + 0.05:
            continue
        n = two_sided_normal(v.co, CORE_C, CORE_R)
        x, y = seen_at(v.co)
        d = gain * (sample(soft, x, y) / 14.0 - level)
        d = max(lo, min(hi, d)) * smoothstep(0.05, 0.4, n.dot(TOWARDS_VIEW)) * smoothstep(z_cut + 0.5, z_cut + 3.0,
                                                                                            v.co.z)
        v.co = inside_glass(v.co + n * d, CORE_ROOM)
    bm.normal_update()
    # The bands, cut along the picture's contours.
    values = {v: sample(sharp, *seen_at(v.co)) for v in bm.verts}
    for lowest, _ in CORE_BANDS[1:]:
        split_along(bm, values, lowest)
    roles = []
    for f in bm.faces:
        if f.normal.z < -0.9 and f.calc_center_median().z < z_cut + 0.1:
            roles.append("k0")            # the flat underside
            continue
        value = sum(values.get(v, 0.0) for v in f.verts) / len(f.verts)
        roles.append(max((band for band in CORE_BANDS if value >= band[0]), key=lambda band: band[0])[1])
    obj = to_object("creature", bm, mats, roles)
    k.smooth(obj, 70.0)
    lens = lobe(obj, sharp, mats)
    return db.join([obj, lens], "creature")


def lobe(body, sharp, mats):
    """The glowing lobe low on the right: a flattened ellipsoid standing out of the creature where the camera sees the
    sprite's lobe, facing out along the surface there, painted in the creature's bands (brightest in its middle)."""
    (tx, ty), (a, b, c), stand, peak, rim = LOBE
    best = None
    for v in body.data.vertices:
        if v.normal.dot(TOWARDS_VIEW) < 0.15:
            continue
        x, y = seen_at(v.co)
        d = (x - tx) ** 2 + (y - ty) ** 2
        if best is None or d < best[0]:
            best = (d, v.co.copy(), v.normal.copy())
    _, at, normal = best
    up = (normal + TOWARDS_VIEW).normalized()
    across = up.cross(SCREEN_UP).normalized()          # along the screen's x on the surface
    along = up.cross(across).normalized()
    if across.x < 0:
        across = -across
    frame = Matrix((across, along, up)).transposed().to_4x4()
    obj = k.ellipsoid("lobe", (0.0, 0.0, 0.0), (a, b, c), mats["k8"], 24, 12)
    local = [v.co.copy() for v in obj.data.vertices]
    obj.data.transform(Matrix.Translation(at + normal * stand) @ frame)
    for v in obj.data.vertices:
        v.co = inside_glass(v.co, CORE_ROOM)
    obj.data.update()
    k.recalc_normals(obj)
    values = []
    for v, q in zip(obj.data.vertices, local):
        r2 = (q.x / a) ** 2 + (q.y / b) ** 2
        values.append(max(sample(sharp, *seen_at(v.co)), peak - (peak - rim) * r2))
    band_split(obj, values, [(lowest, mats[role]) for lowest, role in CORE_BANDS])
    return k.smooth(obj, 70.0)


def screen_angle(n):
    """The direction (degrees from the right, counter-clockwise) a point of the ball lies in from its middle, as the
    camera sees it (the same for the near and the far side along one line of sight)."""
    return math.degrees(math.atan2(n.dot(SCREEN_UP), n.x))


def rim_field(n):
    """How squarely the camera looks at the glass (either way) less the rim's width there: under 0 the rim."""
    rim = RIM_S - RIM_SKEW * math.cos(math.radians(screen_angle(n) - RIM_LIGHT))
    return abs(n.dot(TOWARDS_VIEW)) - rim


def crescent_value(n):
    """How much a point of the glass (its normal n) lies in the lit crescent inside its lower right rim, as the camera
    sees it (0-1; only on the near side)."""
    if n.dot(TOWARDS_VIEW) <= 0.0:
        return 0.0
    f = rim_field(n)
    a0, a1, a2, a3 = CRESCENT_S
    across = smoothstep(a0, a1, f) * (1.0 - smoothstep(a2, a3, f))
    angle = screen_angle(n)
    b0, b1, b2, b3 = CRESCENT_ANGLE
    along = smoothstep(b0, b1, angle) * (1.0 - smoothstep(b2, b3, angle))
    return across * along


def glass(mats):
    """The glass: an ellipsoid shell, its underside left out, banded by how squarely the camera looks at it, the
    crescent on its near side."""
    bm = ellipsoid_bm(GLOBE_C, GLOBE_R, 4, finer=lambda n: n.dot(TOWARDS_VIEW) > -0.1 and
                      abs(n.dot(TOWARDS_VIEW)) < 0.8 and n.z > -0.4)
    z_cut = GLOBE_C.z - GLASS_CUT * GLOBE_R[2]
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-5, plane_co=(0, 0, z_cut),
                           plane_no=(0, 0, -1), clear_outer=True)
    field = {v: rim_field(ellipsoid_normal(v.co, GLOBE_C, GLOBE_R)) for v in bm.verts}
    for lowest, _ in GLASS_BANDS[1:]:
        split_along(bm, field, lowest)
    cres = {v: crescent_value(ellipsoid_normal(v.co, GLOBE_C, GLOBE_R)) for v in bm.verts}
    for cut_at in CRESCENT_CUTS:
        split_along(bm, cres, cut_at)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    roles = []
    for f in bm.faces:
        n = ellipsoid_normal(f.calc_center_median(), GLOBE_C, GLOBE_R)
        c = sum(cres.get(v, crescent_value(ellipsoid_normal(v.co, GLOBE_C, GLOBE_R))) for v in f.verts) / len(f.verts)
        if c >= CRESCENT_CUTS[1]:
            roles.append("crescent_hot")
            continue
        if c >= CRESCENT_CUTS[0]:
            roles.append("crescent")
            continue
        s = rim_field(n)
        roles.append(max((band for band in GLASS_BANDS if s >= band[0]), key=lambda band: band[0])[1])
    obj = to_object("glass", bm, mats, roles)
    return k.smooth(obj, 80.0)


# --- Cutting and the pieces ------------------------------------------------------------------------------------------

def cut_open(source, box_xy):
    """The part of a single surface (no inside to close) inside box (x0, x1, y0, y1), its normals the uncut one's."""
    x0, x1, y0, y1 = box_xy
    obj = source.copy()
    obj.data = source.data.copy()
    bpy.context.scene.collection.objects.link(obj)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    planes = (((x0, 0, 0), (-1, 0, 0)), ((x1, 0, 0), (1, 0, 0)), ((0, y0, 0), (0, -1, 0)), ((0, y1, 0), (0, 1, 0)))
    for co, no in planes:
        bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-6, plane_co=co, plane_no=no,
                               clear_outer=True)
    if not bm.faces:
        bm.free()
        bpy.data.objects.remove(obj)
        return None
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def band_of(value):
    return max((band for band in CORE_BANDS if value >= band[0]), key=lambda band: band[0])[1]


def fill_cap(bm, edges, axis, at, outward):
    """Closes the hole a cut on the plane (axis 0: x = at, 1: y = at) left, bounded by edges, with an even grid of
    triangles (a constrained Delaunay triangulation of the boundary and grid points CAP_STEP apart inside it, so the
    painting can follow the picture across it), its faces looking along outward."""
    verts = []
    for e in edges:
        for v in e.verts:
            if v not in verts:
                verts.append(v)
    index = {v: i for i, v in enumerate(verts)}
    other = 1 - axis

    def uv(co):
        return Vector((co[other], co.z))
    pts = [uv(v.co) for v in verts]
    segments = [(index[e.verts[0]], index[e.verts[1]]) for e in edges]

    def inside(p):
        hit = False
        for a, b in segments:
            pa, pb = pts[a], pts[b]
            if (pa.y > p.y) != (pb.y > p.y) and p.x < pa.x + (p.y - pa.y) * (pb.x - pa.x) / (pb.y - pa.y):
                hit = not hit
        return hit

    def clearance(p):
        best = 1e9
        for a, b in segments:
            pa, pb = pts[a], pts[b]
            d = pb - pa
            f = 0.0 if d.length_squared < 1e-12 else max(0.0, min(1.0, (p - pa).dot(d) / d.length_squared))
            best = min(best, (p - (pa + d * f)).length)
        return best
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts)))
    grid = []
    nu, nv = int((hi.x - lo.x) / CAP_STEP) + 1, int((hi.y - lo.y) / CAP_STEP) + 1
    for j in range(nv + 1):
        for i in range(nu + 1):
            p = Vector((lo.x + i * CAP_STEP + (CAP_STEP / 2 if j % 2 else 0.0), lo.y + j * CAP_STEP))
            if inside(p) and clearance(p) > CAP_STEP * 0.4:
                grid.append(p)
    out_co, _, out_faces, orig_verts, _, _ = delaunay_2d_cdt(pts + grid, segments, [], 0, 1e-6)
    made = []
    for i, co in enumerate(out_co):
        src = orig_verts[i]
        if src and src[0] < len(verts):
            made.append(verts[src[0]])
        else:
            p3 = [0.0, 0.0, co.y]
            p3[axis], p3[other] = at, co.x
            made.append(bm.verts.new(p3))
    faces = []
    for f in out_faces:
        centre = sum((out_co[i] for i in f), Vector((0.0, 0.0))) / len(f)
        if not inside(centre):
            continue
        ring = [made[i] for i in f]
        if len(set(ring)) < 3:
            continue
        try:
            face = bm.faces.new(ring)
        except ValueError:
            continue
        face.normal_update()
        if face.normal.dot(Vector(outward)) < 0:
            face.normal_flip()
        faces.append(face)
    return faces


def split_faces_along(bm, faces, values, threshold):
    """polish_sphere_nozzle.split_along for some faces only: cuts them along the contour where the vertex values
    cross threshold."""
    made = set()
    edges, seen = [], set()
    for f in faces:                  # in a fixed order (a set's would follow the memory addresses)
        for e in f.edges:
            if e not in seen:
                seen.add(e)
                edges.append(e)
    for e in edges:
        a, b = e.verts
        fa, fb = values[a], values[b]
        if (fa - threshold) * (fb - threshold) < 0:
            _, v = bmesh.utils.edge_split(e, a, (threshold - fa) / (fb - fa))
            values[v] = threshold
            made.add(v)
    out = []
    for f in faces:
        ends = [v for v in f.verts if v in made]
        if len(ends) == 2 and not any(ends[1] in e.verts for e in ends[0].link_edges):
            out.extend(bmesh.utils.face_split(f, ends[0], ends[1])[0:1])
        out.append(f)
    return out


def cut_creature(source, box, mats, shading):
    """The part of the creature inside box (x0, x1, y0, y1). Its cuts are closed by caps painted in the creature's
    dark and middle bands (the picture blurred broadly where the camera sees each point, no lighter than CAP_MAX) and
    shaded as the creature is (each point the ellipsoid's normal there, not the flat cap's): the game draws every
    batch without culling and a piece fading in see-through, both sides and without depth writes, so a neighbour's
    flat caps (dark, flat-lit, one side catching the sun) showed through it as seams down and across the ball (x = 0,
    y = 0); so painted they read as the creature's inside, from any side of the screen. The surface keeps the uncut
    one's normals (Shading)."""
    x0, x1, y0, y1 = box
    obj = source.copy()
    obj.data = source.data.copy()
    bpy.context.scene.collection.objects.link(obj)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    planes = (((x0, 0, 0), (-1, 0, 0), 0, x0), ((x1, 0, 0), (1, 0, 0), 0, x1), ((0, y0, 0), (0, -1, 0), 1, y0),
              ((0, y1, 0), (0, 1, 0), 1, y1))
    for co, no, axis, at in planes:
        if not bm.faces:
            break
        result = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-6, plane_co=co,
                                        plane_no=no, clear_outer=True)
        edges = [e for e in result["geom_cut"] if isinstance(e, bmesh.types.BMEdge) and e.is_valid and
                 len(e.link_faces) == 1]
        if edges:
            fill_cap(bm, edges, axis, at, no)
    if not bm.faces:
        bm.free()
        bpy.data.objects.remove(obj)
        return None
    sides = [(0, x0), (0, x1), (1, y0), (1, y1)]
    caps = [f for f in bm.faces if any(all(abs(v.co[axis] - at) < 1e-4 for v in f.verts) for axis, at in sides)]
    broad = painting()[2]
    values = {v: min(CAP_MAX, sample(broad, *seen_at(v.co))) for f in caps for v in f.verts}
    for lowest, _ in CORE_BANDS[1:]:
        caps = split_faces_along(bm, caps, values, lowest)
    slots = {role: mk.slot_of(obj, mats[role]) for _, role in CORE_BANDS}
    cap_set = set(caps)
    for f in caps:
        f.material_index = slots[band_of(sum(values[v] for v in f.verts) / len(f.verts))]
        f.smooth = True
    bm.normal_update()
    bm.faces.index_update()
    cap_ids = {f.index for f in cap_set}
    bm.to_mesh(obj.data)
    bm.free()
    mesh = obj.data
    normals = []
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            co = mesh.vertices[mesh.loops[li].vertex_index].co
            if poly.index in cap_ids:
                n = two_sided_normal(co, CORE_C, CORE_R)
            else:
                n = shading.normal(co, poly.normal)
            normals.append(tuple(n if n is not None else poly.normal))
    mesh.normals_split_custom_set(normals)
    return obj


def reorder(obj, key):
    """Rebuilds a mesh with its faces in the order of key(polygon) (the game draws see-through faces in their order),
    keeping its corner normals, materials and smoothing."""
    mesh = obj.data
    order = sorted(range(len(mesh.polygons)), key=lambda i: key(mesh.polygons[i]))
    verts = [v.co.copy() for v in mesh.vertices]
    polys = [list(mesh.polygons[i].vertices) for i in order]
    mats = [mesh.polygons[i].material_index for i in order]
    smooth = [mesh.polygons[i].use_smooth for i in order]
    normals = []
    for i in order:
        normals += [tuple(mesh.corner_normals[li].vector) for li in mesh.polygons[i].loop_indices]
    new = bpy.data.meshes.new(mesh.name)
    new.from_pydata(verts, [], polys)
    for mat in mesh.materials:
        new.materials.append(mat)
    new.polygons.foreach_set("material_index", mats)
    new.polygons.foreach_set("use_smooth", smooth)
    new.normals_split_custom_set(normals)
    old_name = mesh.name
    obj.data = new
    bpy.data.meshes.remove(mesh)
    new.name = old_name
    return obj


def piece(whole, name, box, mats, shadings):
    """One piece: the creature cut and capped, the glass cut open, moved to its sprite's centre, triangulated, joined,
    its glass faces far side first."""
    creature_src, glass_src = whole
    parts = []
    core = cut_creature(creature_src, box, mats, shadings["creature"])
    if core is not None:
        parts.append(core)
    shell = cut_open(glass_src, box)
    if shell is not None:
        mesh = shell.data
        shading = shadings["glass"]
        normals = []
        for poly in mesh.polygons:
            for li in poly.loop_indices:
                n = shading.normal(mesh.vertices[mesh.loops[li].vertex_index].co, poly.normal)
                normals.append(tuple(n if n is not None else poly.normal))
        mesh.normals_split_custom_set(normals)
        parts.append(shell)
    db.drop_unused(parts)
    centre = Vector(((box[0] + box[1]) / 2, (box[2] + box[3]) / 2, 0.0))
    mk.transform(parts, Matrix.Translation(-centre))
    bpy.context.view_layer.update()
    triangulate(parts)
    obj = db.join(parts, name)
    obj.data.name = name
    roles = {m.name: role for role, m in mats.items()}
    glass_slots = {i for i, m in enumerate(obj.data.materials) if roles[m.name] in GLASS_ROLES}
    view_centre = GLOBE_C - centre

    def key(poly):
        if poly.material_index not in glass_slots:
            return (0, 0.0)
        return (1, (poly.center - view_centre).dot(TOWARDS_VIEW))
    return reorder(obj, key)


def whole_mask(sheet):
    mask = [[False] * 48 for _ in range(56)]
    for sprite, (col, row) in CELLS.items():
        part = k.sprite_mask(sheet, sprite)
        for y in range(28):
            for x in range(24):
                if part[y][x]:
                    mask[row + y][col + x] = True
    return mask


def opaque_coverage(objects, w, h):
    """The top view's coverage with the see-through materials made opaque for it (the ball's own outline)."""
    saved = []
    for m in {m for obj in objects for m in obj.data.materials}:
        bsdf = m.node_tree.nodes["Principled BSDF"]
        saved.append((m, bsdf.inputs["Alpha"].default_value, m.surface_render_method))
        bsdf.inputs["Alpha"].default_value = 1.0
        m.surface_render_method = "DITHERED"
    covered = mk.coverage(objects, w, h)
    for m, alpha, method in saved:
        m.node_tree.nodes["Principled BSDF"].inputs["Alpha"].default_value = alpha
        m.surface_render_method = method
    return covered


def build():
    k.reset()
    options = k.args()
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    looks = [look_materials(i) for i in range(len(LOOK_FRAMES))]
    whole = [creature(looks[0]), glass(looks[0])]
    for obj in whole:
        mk.apply(obj)
    bpy.context.view_layer.update()
    print("whole globe: %d triangles (creature %d, glass %d)" % (mk.triangles(whole), mk.triangles(whole[:1]),
                                                                  mk.triangles(whole[1:])))
    sheet = os.path.join(options["check"], "enemy_U.png") if "check" in options else None
    if sheet:
        mk.compare("whole (u 153 155 / 191 193)", opaque_coverage(whole, 48, 56), whole_mask(sheet))
    bpy.context.scene.view_settings.view_transform = "Standard"
    if "preview" in options:
        mk.preview(options["preview"] + "glass_globe_whole", whole, size=(48, 56), scale=10, distance=1.6)
    if "whole" in options:
        triangulate(whole)
        mk.export(whole, options["whole"])
    if only == ["none"]:
        return
    shadings = {"glass": Shading(whole[1]), "creature": Shading(whole[0])}
    for name, box, frames in PIECES:
        names = [name] + ["%s_%d" % (name, frames[f[0]]) for f in LOOK_FRAMES[1:]]
        if only and not any(n in only for n in names):
            continue
        obj = piece(whole, name, box, looks[0], shadings)
        for src in whole:
            src.hide_render = True
        if sheet:
            mk.compare("%s (u %d)" % (name, frames[0]), opaque_coverage([obj], 24, 28), k.sprite_mask(sheet, frames[0]))
        roles = {m.name: role for role, m in looks[0].items()}
        slot_roles = [roles[m.name] for m in obj.data.materials]
        for look, model in enumerate(names):
            # The look's materials in the same slots (the geometry is the same in every look).
            for i, role in enumerate(slot_roles):
                obj.data.materials[i] = looks[look][role]
            if only and model not in only:
                continue
            mk.report(model, [obj], os.path.join(out, model + ".glb"))
            if "preview" in options:
                mk.preview(options["preview"] + model, [obj], scale=20, distance=0.9)
        bpy.data.objects.remove(obj)
        for src in whole:
            src.hide_render = False


if __name__ == "__main__":
    build()
