"""The cargo pod "812" on the block house of the asteroid levels, and its wreck (sheet P sprites 165 and 167 above 203
and 205 above 241 and 243, 2x2 each: one 48 x 84 picture; the wreck P 169 and 207 in the top pair's place; ground
layer), polished (2026-10-22, round 30; it replaces wave3_w_works.py's crate_whole(), a lofted grey crate painted
pixel for pixel on wave3_w_kit.py's old house, and wave3_ao_works.py's crate_wreck()).

PLACEMENT (the level events, tools/content/tyrevents.py; the enemy data, tools/content/tyrdata.py)

Six enemies, armour 30 each, one frame, not animated, no launches: 343 (P 165, worth 75), 344 (167), 345 (241), 346
(243), 347 (203), 348 (205) in episodes 1-3, 1035-1040 (the same sprites and data) in episode 5. Event 12 ("4-part
enemy") puts 345 (241) at (x, y), 346 (243) at (x + 24, y), 347 (203) at (x, y - 28) and 348 (205) at (x + 24, y - 28),
and with it event 6 puts 343 (165) and 344 (167) at x and x + 24, 56 pixels up the screen (d5 -56): the picture whole,
as the sheet lays it out. ASTEROID1 t6320, ASTEROID2 t6264, ASTCITY t2009 and t2317, AST. CITY t3940; AST ROCK (episode
5) t2148, t2344 and t2372 (event 10, ground2, for the top pair with d5 -57, event 12 with d5 -1: the same layout).
Each time the six share one link: shot, they go together, 343 and 344 turning to their wrecks (dgr 169 and 207 with
dlevel -1: the enemies stay, showing them), the other four dying (the game leaves its slumped wrecks of their models,
tyrian2.c leave_wreck); the maps have the block house's ruin painted under the lower four (tiles 423 424 above 433
434) and plain floor under the top pair. Episode 4's enemies 343 and 344 are other things; no episode 6 level places
the pod (GREY MOON and VAULT take only ASTEROID2's boss block, link 45). No other enemy shows these sprites
(catalog.json, launched enemies too); none is another sprite's pixels mirrored, turned or in other ramps (twins.py:
only P 188, which is P 169's own cells, 188 and 189): no frame models, no twins. The terrain is flat with holes in
ASTEROID1, ASTEROID2, AST. CITY and AST ROCK (tools/terrain/levels.json), stepped by tile classes in ASTCITY.

THE POD

As the sprites and their 4x upscales draw it (columns and rows of the 48 x 84 picture; all of it in the grey ramp 0):
the block house of these levels (P 153 155 above 191 193: its rows 0-52 are rows 28-80 here) with a long container
lying on its roof: the house's lit left edge (columns 4-5) and right edge (column 42) beside the pod, its ribbed front
(rows 71-80) under it, the floor round it the map's; the pod (columns 6-41 of rows 14-55) its back end 14 rows past
the house's back (row 28): its top a corrugated panel (columns 13-33, 0x0a and 0x09 every other column, lit edges
0x0b) with "812" painted along it (0x0c, 0x0d: the 2 at rows 22-29, the 1 at 32-35, the 8 at 39-46), its long sides
chamfered and ribbed every two columns (columns 7-12 lit, 0x08 and 0x09; 34-40 shaded, 0x06 and 0x07), its ends
framed: a lit band at the back (rows 14-18, a dark groove at 19), a lit band over the front (rows 49-52) and the
front's face under it (rows 53-55, 0x07); in front of it on the roof a dark dock (rows 56-69): two clamps against the
pod's foot (columns 19-26 and 28-35 of rows 56-58), two vents (columns 14-21 and 24-31 of rows 59-64: a dark slot
under a lit slat each) parted by a rib, four bolts, a lit lip along its left (column 6), a sill along its front (rows
66-68) with grooves at columns 18 and 27 and lit posts at 16 and 34. The wreck (P 169 207, over rows 14-27): the
back end blown open, two black holes torn into its top (columns 14-18 and 24-36 of rows 19-27, the larger down the
right chamfer), the plating round them dark, lit torn plating between them, an ember (0x70, 0x71) in the larger one,
the back frame cracked at columns 19-22.

Built as such a container on polish_block_house.py's house, for the game's camera (20 degrees from straight down,
from the bottom of the screen: a point at height z shows S(z) = (z - 10) tan 20 pixels further up the screen than one
on the roof, whose own height the house's layout holds, as polish_bronze_pump.py builds on it): every part is laid
out where the sprite draws it and moved down the screen by S of its top (the pod's top 3.6 pixels), its walls
upright. The house is the block house's own (body(), its painting wells() without hatches, ribs()) without its slabs
(the pod and the dock cover its roof; the strips the pod leaves free painted 0x0a as the slabs), its walls reaching 4
pixels under the floor. The pod: its body a cross-section (flat on the roof from x -18 to 18, upright sides 2.4 high,
chamfers ribbed every 2 pixels where the sprite's lit columns are, the top from x -11 to 10, its border strips flat,
between them a corrugation 0.3 deep every 2 pixels) swept along y; its end caps the plain section grown 0.35 (PROUD),
their top edges chamfered (the front's 2.6 pixels, which the camera sees as the sprite's lit band over the front's
upright face; the back's 1.5, lit by the sun as the sprite lights its back edge), bevelled; 10.35 high over the roof
(20.35 over the floor), the camera seeing its back chamfer's foot at row 14 and its front's foot at row 55.5. Painted
by where the faces lie and how they meet the game's light (from the upper left and above): the top 0x0a (crests and
the faces turned to the sun) and 0x09 (valleys, faces turned away), its border strips 0x0b; the left chamfer 0x0a (its
ribs 0x0b and 0x09), the right one 0x08 (0x09, 0x07); the upright sides 0x06 and 0x05; the caps' tops 0x0a, their lit
edges 0x0b and 0x0c, the front's chamfer 0x0c and its face 0x0b and 0x0a (the sun is behind them: they read as the
sprite's darker greys); the number cut along the contour of the sprite's pixels (bilinear over them) as the camera
sees it on the top and painted 0x0d. Under the pod's back end, where it reaches past the house, two trestles and a
beam (0x04, 0x03), where the camera sees all of them in the top pieces' sprites (so that they stay with the wreck).
The dock: boxes (polish_machine_kit, bevelled): the bay's floor 0x02, the lips (0x0a lit, 0x03), the clamps (0x03,
fronts 0x04), the vents (frames 0x03 round black slots 0x01, slats 0x06 lit 0x09 at their left ends), the rib, the
bolts (0x06), the sill's three plates (0x06) and its posts (0x09).

The wreck: the intact pod again, its back end blown open as P 169 and 207 draw it: the two holes cut 7 pixels deep
into the body and the back cap (exact booleans along the sprite's black pixels' outlines, torn by smooth noise; the
meshes rebuilt in a fixed order, canonical(): the boolean returns its result in an order that changes from run to
run), their floors black (0x01), their walls 0x02; the plating round them burnt (0x05, nearer 0x04, along smooth
contours of the distance to the holes); torn plates bent up out of them (0x0a, lit 0x0c, undersides 0x04), scraps
(0x04) and an ember (0x73, emission 0.45 in 0x76) on the larger one's floor; the back cap cracked (a groove).

The whole (and the wreck) is cut along the planes the camera sees as the sprites' edges (polish_stone_face.view_cut:
x = 0 upright; y + S(z) = 0 and 28, leaning back up the screen; the cuts capped 0x03, the pieces keeping the uncut
shading), so that each piece holds what the camera sees in its sprite (the pod's top over the house's back edge in
the top pieces, the wreck's holes in the wreck's), each piece moved so that its sprite's centre is its origin, every
mesh triangulated (polish_k_pod.triangulate) and its parts joined (polish_deli_boss.join).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the floor (z 0, the roof at
10). The whole's origin is the corner where the four lower sprites meet (pixel corner 24, 56 of the picture: the
block house's own origin): E(c, r) is the picture's pixel corner (c, r), (c - 24, 56 - r). The pieces' centres: 165
(-12, 42), 167 (12, 42), 203 (-12, 14), 205 (12, 14), 241 (-12, -14), 243 (12, -14); the wreck's as 165's and 167's.

models.cfg: the model lines stay (cargo_pod_tl / _tr / _ml / _mr / _bl / _br, cargo_pod_wreck_tl / _tr, origin); the
sprite lines of P 165, 167, 203, 205, 241, 243, 169 and 207 get height=-4 (the house on the terrain, as the block house
and the bronze pump stand). Replaces wave3_w_works.py's cargo pod (its section "P 165 167 / 203 205 / 241 243: the
cargo pod": CRATE, crate_ring(), crate_whole() and its kit.pieced("cargo_pod", ...) registration, and the cargo_pod_*
bullet of its docstring) and wave3_ao_works.py's wreck of it (its section "P 169 207: the cargo pod's wreck": CRATE,
CRATE_DMG, SEAM, taper_to_seam(), crate_wreck() and its wkit.pieced("cargo_pod_wreck", ...) registration, and the
cargo_pod_wreck bullet of its docstring); and the pixels only those read: wave3_w_art.py's CRATE, wave3_ao_art.py's
CRATE_DMG.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes as the game's
camera sees them, relative to the roof, of the whole and of each piece against the sprites' pixels, the floor they
paint round the house left out), --preview <prefix> (each piece's top and 3/4 views), --whole <prefix> (the uncut pod
and wreck as <prefix>cargo_pod.glb and <prefix>cargo_pod_wreck.glb), --only <model,...>.
"""
import math
import os
import sys

import bmesh
import bpy
import mathutils.noise as noise
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
import polish_block_house as bh  # noqa: E402
from polish_coral_manta import split_contour  # noqa: E402
from polish_deli_boss import join, drop_unused  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_stone_face import view_cut  # noqa: E402

H = bh.H                                      # the house's roof
TILT = math.tan(math.radians(20.0))           # the camera shows a point this much further up the screen per pixel up
LIGHT = Vector((-0.55, 0.45, 0.7)).normalized()   # towards the game's sun (polish_bronze_pump's)

# The pieces: name, sprite, the part of the picture it shows as the camera sees it at the roof's height (x0, x1, y0,
# y1; None: no neighbour that side), its sprite's centre.
PIECES = [("cargo_pod_tl", 165, (None, 0.0, 28.0, None), (-12.0, 42.0)),
          ("cargo_pod_tr", 167, (0.0, None, 28.0, None), (12.0, 42.0)),
          ("cargo_pod_ml", 203, (None, 0.0, 0.0, 28.0), (-12.0, 14.0)),
          ("cargo_pod_mr", 205, (0.0, None, 0.0, 28.0), (12.0, 14.0)),
          ("cargo_pod_bl", 241, (None, 0.0, None, 0.0), (-12.0, -14.0)),
          ("cargo_pod_br", 243, (0.0, None, None, 0.0), (12.0, -14.0))]
WRECK_PIECES = [("cargo_pod_wreck_tl", 169, (None, 0.0, 28.0, None), (-12.0, 42.0)),
                ("cargo_pod_wreck_tr", 207, (0.0, None, 28.0, None), (12.0, 42.0))]


def E(c, r):
    """A pixel corner (column c, row r) of the 48 x 84 picture in the whole's coordinates."""
    return (c - 24.0, 56.0 - r)


def S(z):
    """How much further up the screen the camera shows a point at height z than one on the roof."""
    return TILT * (z - H)


# --- The pod ----------------------------------------------------------------------------------------------------------
X_L, X_R = -18.0, 18.0       # its sides (the outer edges of columns 6 and 41)
X_TL, X_TR = -11.0, 10.0     # its top's edges (columns 13 and 33)
Z_KNEE = H + 2.4             # its upright sides' top, where the chamfers begin
Z_TOP = H + 10.0             # its top
PROUD = 0.35                 # how far the end frames stand out of the body
FRONT_CHAMFER, BACK_CHAMFER = 2.6, 1.5    # how deep the end caps' top edges are chamfered
Y0 = E(0, 55.5)[1]           # its front's foot on the roof (row 55.5)
Y1 = E(0, 14.0)[1] - S(Z_TOP + PROUD - BACK_CHAMFER)   # its back: the camera sees the back chamfer's foot at row 14
FRONT_FRAME = (Y0, Y0 + (51.86 - 48.5))   # the front cap (the camera sees its top over rows 48.5-52.7)
BACK_FRAME = (Y1 - 5.5, Y1)               # the back cap (rows 14-19)
CORRUGATION = 0.3            # the top's ribs: how deep
RIDGES = [-9.5 + 2 * i for i in range(10)]      # their crests (columns 14, 16, ... 32: 0x0a; the valleys 0x09)
RIBS_L = [-15.5, -13.5, -11.5]                   # the chamfers' ribs (columns 8, 10, 12 and 35, 37, 39)
RIBS_R = [11.5, 13.5, 15.5]
RIB_H, RIB_W = 0.3, 0.6

# The number painted on the top, "812" turned along the pod (the sprite's 0x0c and 0x0d pixels, columns 14-31 of rows
# 22-46).
DIGITS_AT = (14, 22)
DIGITS = [
    "...####......##...",
    "..#######....##...",
    "..##..###....##...",
    "..##....###..##...",
    "..##.....##..##...",
    "..###.....##.##...",
    "...##.....#####...",
    "....##......###...",
    "..................",
    "..................",
    ".............##...",
    "..#############...",
    "..#############...",
    "....#........##...",
    "..................",
    "..................",
    "..................",
    "....###...###.....",
    "...############...",
    "..###..###..###...",
    "..##....#....##...",
    "..##....#....##...",
    "..###..###..###...",
    "...############...",
    "....###...###.....",
]


def section():
    """The body's cross-section (x, z), counter-clockwise seen from the front: flat on the roof, upright sides to the
    knees, ribbed chamfers, the top with its border strips and its corrugation."""
    pts = [(X_R, H), (X_R, Z_KNEE)]

    def chamfer(a, b, ribs):
        (ax, az), (bx, bz) = a, b
        d = Vector((bx - ax, bz - az))
        n = Vector((d.y, -d.x)).normalized()       # outward (the outline runs counter-clockwise)
        if n.y < 0:
            n = -n
        lo, hi = min(ax, bx), max(ax, bx)
        xs = sorted({ax, bx} | {min(hi, max(lo, r + o)) for r in ribs for o in (-RIB_W, -RIB_W / 2, 0.0, RIB_W / 2,
                                                                                RIB_W)})
        if ax > bx:
            xs = xs[::-1]
        out = []
        for x in xs:
            t = (x - ax) / (bx - ax)
            z = az + (bz - az) * t
            h = sum(RIB_H * 0.5 * (1 + math.cos(math.pi * (x - r) / RIB_W)) for r in ribs if abs(x - r) < RIB_W)
            out.append((x + n.x * h, z + n.y * h))
        return out
    pts += chamfer((X_R, Z_KNEE), (X_TR, Z_TOP), RIBS_R)[1:]
    # the top, right to left: the border strips flat, the corrugation between them
    top = [(X_TR, Z_TOP)]
    for i, xr in enumerate(reversed(RIDGES)):
        top += [(xr + 0.25, Z_TOP), (xr - 0.25, Z_TOP)]
        if i < len(RIDGES) - 1:
            xv = xr - 1.0
            top += [(xv + 0.25, Z_TOP - CORRUGATION), (xv - 0.25, Z_TOP - CORRUGATION)]
    top.append((X_TL, Z_TOP))
    pts += top[1:]
    pts += chamfer((X_TL, Z_TOP), (X_L, Z_KNEE), RIBS_L)[1:]
    pts += [(X_L, H)]
    return pts


def frame_section(grow):
    """The plain cross-section grown outward by `grow` (its foot on the roof stays there when it grows; a negative
    `grow` shrinks it all round: a frame's opening)."""
    base = [(X_L, H), (X_R, H), (X_R, Z_KNEE), (X_TR, Z_TOP), (X_TL, Z_TOP), (X_L, Z_KNEE)]
    n = len(base)
    out = []
    for i in range(n):
        p, q, r = Vector(base[i - 1]), Vector(base[i]), Vector(base[(i + 1) % n])
        d1, d2 = (q - p).normalized(), (r - q).normalized()
        n1, n2 = Vector((d1.y, -d1.x)), Vector((d2.y, -d2.x))      # outward (the outline runs counter-clockwise)
        if grow > 0 and i == 1:
            n1 = Vector((0.0, 0.0))     # the edge before vertex 1 is the foot
        if grow > 0 and i == 0:
            n2 = Vector((0.0, 0.0))     # the edge after vertex 0 is the foot
        o1, o2 = q + n1 * grow, q + n2 * grow
        den = d1.x * d2.y - d1.y * d2.x
        t = ((o2.x - o1.x) * d2.y - (o2.y - o1.y) * d2.x) / den
        out.append(tuple(o1 + d1 * t))
    return out


def loft_along_y(name, sect, stations, mat, rings=None):
    """A section swept along y through the stations (or given sections, one per station), its ends closed by fans."""
    rings = [[Vector((x, y, z)) for x, z in (sect if rings is None else rings[i])] for i, y in enumerate(stations)]
    first, last = rings[0], rings[-1]
    c0 = sum(first, Vector()) / len(first)
    c1 = sum(last, Vector()) / len(last)
    return k.loft(name, rings, mat, start_point=tuple(c0), end_point=tuple(c1))


def materials():
    m = bh.materials(0x0a)
    m["hatch"] = m["roof"]
    g = {0x0a: m["roof"], 0x0c: m["lit"], 0x07: m["shade"], 0x05: m["groove"], 0x06: m["wall"], 0x04: m["glacis"],
         0x02: m["well"], 0x03: m["seam"], 0x08: m["conduit"]}
    for i in (0x01, 0x09, 0x0b, 0x0d):
        g[i] = k.material("house_grey", palette=i, metallic=0.3, roughness=0.55)
    m["grey"] = g
    m["ember"] = k.material("pod_ember", palette=0x73, metallic=0.0, roughness=0.5,
                            emission=k.level_palette()[0x76], emission_strength=0.45)
    return m


def paint_body(obj, m):
    """The body's faces by where they lie and how they meet the light: the corrugated top 0x0a (crests and the faces
    turned to the sun) and 0x09 (valleys, faces turned away), the left chamfer 0x09 (its ribs' lit faces 0x0a, their
    shaded ones 0x08), the right one 0x07 (0x08, 0x06), the upright sides 0x06 and 0x05, the panels at its ends 0x07."""
    g = m["grey"]

    def pick(c, n):
        if n.z < -0.5:
            return g[0x03]
        if n.y < -0.9:
            return g[0x09]          # the front panel (the sun is behind it: 0x09 reads as the sprite's 0x07)
        if n.y > 0.9:
            return g[0x05]
        d = n.dot(LIGHT)
        if c.z > Z_TOP - CORRUGATION - 0.05 and X_TL - 0.01 <= c.x <= X_TR + 0.01:
            if n.z > 0.97 and (c.x < X_TL + 0.9 or c.x > X_TR - 0.9):
                return g[0x0b]      # the top's border strips, lit (the sprite's 0x0b edges)
            if n.z > 0.97:
                return g[0x0a] if c.z > Z_TOP - CORRUGATION / 2 else g[0x09]
            return g[0x0a] if n.x < 0 else g[0x09]
        if c.z < Z_KNEE - 0.01:
            return g[0x06] if c.x < 0 else g[0x05]
        if c.x < 0:
            return g[0x0b] if d > 0.95 else g[0x0a] if d > 0.78 else g[0x09]
        return g[0x09] if d > 0.3 else g[0x08] if d > 0.08 else g[0x07]
    mk.paint(obj, pick)


def paint_frame(obj, m):
    """An end cap's faces: its top 0x0a, its edges and chamfers turned to the sun 0x0b and 0x0c (the front one, which
    the sun reaches little, 0x0b), its front (in the sun's shadow) 0x0b on the left and 0x0a on the right, its sides
    by the light, its back and underside dark."""
    g = m["grey"]

    def pick(c, n):
        if n.z < -0.5:
            return g[0x03]
        if n.y > 0.85:
            return g[0x05]
        d = n.dot(LIGHT)
        if n.y < -0.85:
            return g[0x0b] if c.x < -6.0 else g[0x0a]
        if n.y < -0.4 and n.z > 0.4:
            return g[0x0c]          # the front's chamfer (the sun reaches it little)
        if n.z > 0.95:
            return g[0x0a]
        if d > 0.85:
            return g[0x0c]
        if d > 0.6:
            return g[0x0b]
        if d > 0.3:
            return g[0x08]
        return g[0x06]
    mk.paint(obj, pick)


def digit_field(x, y):
    """The number's paint (bilinear over the sprite's pixels: 1 on them, 0 off) at a place as the camera sees it."""
    c = x + 24.0 - 0.5 - DIGITS_AT[0]
    r = 56.0 - y - 0.5 - DIGITS_AT[1]
    c0, r0 = int(math.floor(c)), int(math.floor(r))
    tx, ty = c - c0, r - r0

    def at(rr, cc):
        if 0 <= rr < len(DIGITS) and 0 <= cc < len(DIGITS[0]):
            return 1.0 if DIGITS[rr][cc] == "#" else 0.0
        return 0.0
    return ((1 - tx) * (1 - ty) * at(r0, c0) + tx * (1 - ty) * at(r0, c0 + 1) + (1 - tx) * ty * at(r0 + 1, c0) +
            tx * ty * at(r0 + 1, c0 + 1))


def paint_digits(obj, m):
    """The number on the top: the top's faces cut along the paint's contour (the camera's view: each point at its
    place plus S(z) up the screen), the faces inside it 0x0c."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    vals = {v: (digit_field(v.co.x, v.co.y + S(v.co.z)) - 0.5 if v.co.z > Z_TOP - CORRUGATION - 0.05 else -1.0)
            for v in bm.verts}
    tops = [f for f in bm.faces if f.normal.z > 0.3 and f.calc_center_median().z > Z_TOP - CORRUGATION - 0.05]
    faces = split_contour(bm, {"d": vals}, "d", 0.0, tops)
    slot = mk.slot_of(obj, m["grey"][0x0d])
    for f in faces:
        if f.is_valid and sum(vals[v] for v in f.verts) / len(f.verts) > 1e-9:
            f.material_index = slot
    bm.to_mesh(obj.data)
    bm.free()


def end_cap(name, y_out, y_in, chamfer, mat):
    """An end of the pod: its frame's section (grown by PROUD) swept from y_out (the pod's end) to y_in, its top edge at
    the end chamfered `chamfer` deep (the section's top lowered there, its corners sliding down the side chamfers)."""
    full = frame_section(PROUD)
    low = list(full)
    for top, side in ((3, 2), (4, 5)):
        p, q = Vector(full[top]), Vector(full[side])
        low[top] = tuple(p + (q - p) * (chamfer / (p.y - q.y)))
    step = 1.0 if y_in > y_out else -1.0
    y_mid = y_out + step * chamfer
    rings = [low, full, full] if abs(y_in - y_mid) > 0.05 else [low, full]
    ys = [y_out, y_mid, y_in] if len(rings) == 3 else [y_out, y_in]
    if step < 0:
        rings, ys = rings[::-1], ys[::-1]
    return loft_along_y(name, [], ys, mat, rings)


def pod(m):
    """The pod: the corrugated body between its two end caps, their top edges chamfered (the front's 2.6 pixels, so
    that the camera sees it as the sprite's lit band over the front, the back's 1.5, lit by the sun)."""
    g = m["grey"]
    parts = []
    y_a, y_b = FRONT_FRAME[1] - 0.6, BACK_FRAME[0] + 0.6
    stations = [y_a]
    y = 5.5
    while y < y_b:
        stations.append(y)
        y += 0.5
    stations.append(y_b)
    stations = sorted(set(round(s, 4) for s in stations if y_a <= s <= y_b))
    body = loft_along_y("pod_body", section(), stations, g[0x09])
    paint_body(body, m)
    paint_digits(body, m)
    k.smooth(body, 20)
    parts.append(body)
    for name, y_out, y_in, chamfer in (("pod_frame_front", FRONT_FRAME[0], FRONT_FRAME[1], FRONT_CHAMFER),
                                       ("pod_frame_back", BACK_FRAME[1], BACK_FRAME[0], BACK_CHAMFER)):
        cap = end_cap(name, y_out, y_in, chamfer, g[0x0a])
        mk.bevel(cap, 0.28, 2, 35)
        mk.shade(cap, 35)
        paint_frame(cap, m)
        parts.append(cap)
    return parts


# --- The dock in front of it ----------------------------------------------------------------------------------------

def block(name, x0, x1, y0, y1, z0, z1, mat, bevel=0.0):
    """A box, moved down the screen by S(its top) (the camera then sees its top where the sprite draws it)."""
    s = S(z1)
    obj = mk.box(name, x0, x1, y0 - s, y1 - s, z0, z1, mat)
    if bevel > 0:
        mk.bevel(obj, bevel, 2, 35)
    mk.shade(obj, 35)
    return obj


def paint_lit(obj, top, lit, dark, front=None, under=None):
    def pick(c, n):
        if n.z < -0.5:
            return under or dark
        if n.z > 0.9:
            return top
        if n.y < -0.7 and front is not None:
            return front
        d = n.dot(LIGHT)
        return lit if d > 0.45 else dark
    mk.paint(obj, pick)
    return obj


def dock(m):
    """The dock in front of the pod (rows 56-69): a dark bay on the roof, a lit lip along its left and a dark one along
    its right, two clamps against the pod's foot, two vents (a dark slot under a slat each) parted by a rib, four
    bolts, and along its front a sill in three plates with a lit post either side."""
    g = m["grey"]
    parts = []
    y_front = E(0, 66.0)[1]
    parts.append(paint_lit(block("dock_floor", -17.4, 17.4, y_front, Y0 + 0.2, H - 0.3, H + 0.12, g[0x02]),
                           g[0x02], g[0x02], g[0x02]))
    parts.append(paint_lit(block("dock_lip_l", X_L - 0.4, X_L + 0.6, E(0, 69.0)[1], Y0 + 0.2, H - 0.3, H + 0.8,
                                 g[0x0a], 0.25), g[0x0a], g[0x0c], g[0x06]))
    parts.append(paint_lit(block("dock_lip_r", X_R - 0.6, X_R + 0.4, E(0, 69.0)[1], Y0 + 0.2, H - 0.3, H + 0.6,
                                 g[0x03], 0.25), g[0x03], g[0x04], g[0x02]))
    # the clamps against the pod's foot (columns 19-26 and 28-35 of rows 56-58)
    for i, (c0, c1) in enumerate(((19, 27), (28, 36))):
        x0, x1 = E(c0, 0)[0], E(c1, 0)[0]
        parts.append(paint_lit(block("dock_clamp%d" % i, x0, x1, E(0, 58.8)[1], Y0 + 0.1, H - 0.2, H + 2.0, g[0x03],
                                     0.3), g[0x03], g[0x05], g[0x02], front=g[0x04]))
    # the vents (columns 14-21 and 24-31 of rows 59-64): a dark frame round a black slot, a slat across its top
    for i, (c0, c1) in enumerate(((14, 22), (24, 32))):
        x0, x1 = E(c0, 0)[0], E(c1, 0)[0]
        ya, yb = E(0, 65.0)[1], E(0, 59.0)[1]
        parts.append(paint_lit(block("vent%d" % i, x0, x1, ya, yb, H - 0.2, H + 0.75, g[0x03], 0.2),
                               g[0x03], g[0x04], g[0x02]))
        parts.append(paint_lit(block("vent%d_slot" % i, x0 + 0.6, x1 - 0.6, ya + 0.6, yb - 0.6, H + 0.7, H + 0.8,
                                     g[0x01]), g[0x01], g[0x01], g[0x01]))
        slat = block("vent%d_slat" % i, x0 + 0.7, x1 - 0.7, E(0, 62.0)[1], E(0, 61.0)[1], H + 0.7, H + 1.25, g[0x06],
                     0.2)
        mk.paint(slat, lambda c, n, x0=x0: g[0x09] if (c.x < x0 + 1.6 and n.z > -0.5) else
                 (g[0x06] if n.z > 0.3 or n.dot(LIGHT) > 0.4 else g[0x04]))
        parts.append(slat)
    parts.append(paint_lit(block("vent_rib", E(22, 0)[0] + 0.15, E(24, 0)[0] - 0.15, E(0, 65.0)[1], E(0, 59.0)[1],
                                 H - 0.2, H + 0.6, g[0x04], 0.2), g[0x05], g[0x05], g[0x03]))
    for i, (c, r) in enumerate(((11, 62), (9, 63), (34, 62), (36, 63))):
        x, y = E(c + 0.5, r + 0.5)
        bolt = mk.dome("dock_bolt%d" % i, (x, y - S(H + 0.5)), (0.35, 0.35, 0.35), H + 0.12, g[0x06], 10, 3)
        parts.append(bolt)
    # the sill (rows 66-68): three plates, a groove at columns 18 and 27; a lit post at columns 16 and 34
    ya, yb = E(0, 69.0)[1], E(0, 66.0)[1]
    for i, (x0, x1) in enumerate(((-17.4, E(18, 0)[0]), (E(19, 0)[0], E(27, 0)[0]), (E(28, 0)[0], 17.4))):
        parts.append(paint_lit(block("sill%d" % i, x0 + 0.1, x1 - 0.1, ya, yb, H - 0.3, H + 0.55, g[0x06], 0.2),
                               g[0x06], g[0x08], g[0x04], front=g[0x05]))
    for i, c in enumerate((16, 34)):
        x0, x1 = E(c, 0)[0], E(c + 1, 0)[0]
        parts.append(paint_lit(block("sill_post%d" % i, x0, x1, ya + 0.3, yb - 0.3, H - 0.3, H + 1.0, g[0x08], 0.2),
                               g[0x09], g[0x0a], g[0x05]))
    return parts


# --- The cradle under its back end, and the house ---------------------------------------------------------------------

# The trestles stand where the camera sees all of them in the top pieces' sprites (y + S(z) over 28 down to the
# walls' foot), so that they stay with the back end when the pod's front pieces are shot away.
CRADLE_Y = (28.0 - S(bh.SKIRT) + 0.2, 37.0)


def cradle(m):
    """Two trestles and a beam under the pod's back end, where it reaches past the house (the camera sees them only
    past its sides)."""
    g = m["grey"]
    parts = []
    for i, (x0, x1) in enumerate(((-15.5, -10.5), (10.5, 15.5))):
        obj = mk.box("cradle%d" % i, x0, x1, CRADLE_Y[0], CRADLE_Y[1], bh.SKIRT, H, g[0x04])
        mk.bevel(obj, 0.4, 2, 35)
        mk.shade(obj, 35)
        parts.append(paint_lit(obj, g[0x04], g[0x05], g[0x03]))
    beam = mk.box("cradle_beam", -15.5, 15.5, CRADLE_Y[0] + 0.8, CRADLE_Y[1] - 0.8, H - 2.0, H, g[0x03])
    mk.bevel(beam, 0.3, 2, 35)
    mk.shade(beam, 35)
    parts.append(paint_lit(beam, g[0x04], g[0x05], g[0x03]))
    return parts


def house(m):
    """polish_block_house's house without its slabs (the pod and the dock cover the roof): its body, its rounded edge
    and its ribbed glacis; the roof's strips the pod leaves free 0x0a as the slabs."""
    m = dict(m)
    m["groove"] = m["roof"]
    bh.body(m)
    bh.wells(m, {})
    bh.ribs(m)
    return [o for o in mk.meshes()]


# --- The wreck (P 169 207: the pod's back end blown open) ----------------------------------------------------------
# The holes (the wreck's black pixels, columns and rows of the picture as the camera sees them on the pod's top), the
# torn plating between them (lit), the ember in the larger one, the back frame cracked.
HOLES = [
    # the left hole (columns 14-18 of rows 21-27)
    [(16.0, 20.6), (17.4, 21.2), (18.2, 22.6), (19.0, 23.6), (19.2, 25.4), (18.9, 27.2), (18.6, 28.6), (16.0, 28.6),
     (15.2, 27.6), (14.3, 26.2), (14.0, 24.6), (14.8, 23.4), (15.0, 21.8)],
    # the right one, from the top's right part down its chamfer (columns 24-36 of rows 19-27)
    [(28.0, 18.6), (29.6, 19.4), (30.4, 21.0), (32.2, 20.6), (33.4, 19.2), (35.0, 19.6), (36.2, 21.0), (37.0, 23.0),
     (37.2, 25.2), (37.0, 28.6), (31.0, 28.6), (29.6, 27.4), (28.4, 28.6), (24.2, 28.6), (23.6, 27.2), (23.8, 24.6),
     (25.2, 23.6), (26.8, 23.0), (27.4, 21.4)],
]
HOLE_FLOOR = H + 3.0        # how deep they reach into the pod
EMBER = (26.5, 26.8)        # the ember in the right hole (the sprite's 0x70 and 0x71 at column 26 of rows 26-27)
# Torn plates bent up round the holes' rims (column, row of their roots, their direction in degrees, length, width).
FLAPS = [(20.5, 22.0, 200.0, 2.4, 1.5), (21.5, 25.8, 180.0, 2.2, 1.4), (27.8, 22.2, 100.0, 1.8, 1.4),
         (31.0, 20.6, 80.0, 1.8, 1.3), (25.0, 23.4, 135.0, 1.6, 1.2), (16.4, 21.0, 70.0, 1.6, 1.1)]
CRACK = [(19.4, 14.6), (20.6, 16.2), (21.0, 18.2), (21.6, 19.6)]   # the crack in the back frame
SCORCH = 1.6                # how far round the holes the plating is burnt


def canonical(obj):
    """polish_powerups_specials.canonical: the object's mesh rebuilt in a fixed order (its vertices by position, each
    face starting at its smallest corner, the faces by their corners), for the exact boolean returns its result in an
    order that changes from run to run."""
    me = obj.data

    def key(co):
        return (round(co.x, 5), round(co.y, 5), round(co.z, 5))
    faces = []
    for poly in me.polygons:
        corners = [key(me.vertices[i].co) for i in poly.vertices]
        start = corners.index(min(corners))
        faces.append((corners[start:] + corners[:start], poly.material_index))
    faces.sort()
    verts = sorted({c for corners, _ in faces for c in corners})
    index = {c: i for i, c in enumerate(verts)}
    mesh = bpy.data.meshes.new(me.name)
    mesh.from_pydata(verts, [], [[index[c] for c in corners] for corners, _ in faces])
    for mat in me.materials:
        mesh.materials.append(mat)
    for poly, (_, material) in zip(mesh.polygons, faces):
        poly.material_index = material
    obj.data = mesh
    bpy.data.meshes.remove(me)
    return obj


def ragged(points, seed, amount=0.35):
    """A hole's outline (picture columns and rows) as the whole's points on the pod's top, resampled every 0.4 pixels
    and torn: moved in and out by smooth noise."""
    p = [Vector(E(c, r)) for c, r in points]
    out = []
    for i in range(len(p)):
        a, b = p[i], p[(i + 1) % len(p)]
        steps = max(1, int((b - a).length / 0.4))
        for j in range(steps):
            q = a.lerp(b, j / steps)
            out.append(q)
    centre = sum(out, Vector((0.0, 0.0))) / len(out)
    torn = []
    for i, q in enumerate(out):
        d = (q - centre).normalized()
        w = noise.noise(Vector((q.x * 0.9, q.y * 0.9, seed)))
        torn.append(q + d * amount * w)
    return [(q.x, q.y - S(Z_TOP)) for q in torn]


def wreck(parts, m):
    """The pod's back end blown open as P 169 and 207 draw it: two holes torn into its top (the larger one down its
    right chamfer), black inside (0x01, their walls 0x02), the plating round them burnt (0x05, 0x04) and torn plates
    bent up out of them (0x0a, lit 0x0c, their undersides 0x04), an ember in the larger one (0x73, glowing), the back
    frame cracked."""
    g = m["grey"]
    black = g[0x01]
    body = next(o for o in parts if o.name == "pod_body")
    back = next(o for o in parts if o.name == "pod_frame_back")
    for obj in (body, back):
        for i, hole in enumerate(HOLES):
            cutter = mk.prism("hole%d" % i, ragged(hole, 3.0 + i), HOLE_FLOOR, Z_TOP + 3.0, black)
            mk.boolean(obj, cutter, "DIFFERENCE")
        if obj is back:
            pts = [Vector((E(c, r)[0], E(c, r)[1] - S(Z_TOP))) for c, r in CRACK]
            for j, (a, b) in enumerate(zip(pts, pts[1:])):
                d = (b - a).normalized()
                nrm = Vector((-d.y, d.x)) * 0.32
                outline = [tuple(a - nrm), tuple(b - nrm), tuple(b + nrm), tuple(a + nrm)]
                cutter = mk.prism("crack%d" % j, outline, Z_TOP - 1.2, Z_TOP + 3.0, black)
                mk.boolean(obj, cutter, "DIFFERENCE")
        mk.cleanup(obj, dissolve=0.0)
        canonical(obj)
    # the holes' insides: black floors, dark walls; the plating round them burnt (cut along smooth contours of how far
    # a point lies from the holes)
    holes = [[Vector(p) for p in ragged(h, 3.0 + i)] for i, h in enumerate(HOLES)]

    def hole_distance(x, y):
        q = Vector((x, y))
        best = 1e9
        for poly in holes:
            for a, b in zip(poly, poly[1:] + poly[:1]):
                ab = b - a
                t = max(0.0, min(1.0, (q - a).dot(ab) / max(ab.length_squared, 1e-12)))
                best = min(best, (a + ab * t - q).length)
        return best
    for obj in (body, back):
        names = [mt.name for mt in obj.data.materials]
        if black.name in names:
            black_slot = names.index(black.name)
            for poly in obj.data.polygons:
                if poly.material_index == black_slot and poly.normal.z < 0.5:
                    poly.material_index = mk.slot_of(obj, g[0x02])
    bm = bmesh.new()
    bm.from_mesh(body.data)
    dist = {v: hole_distance(v.co.x, v.co.y) for v in bm.verts}
    black_slot = [mt.name for mt in body.data.materials].index(black.name)
    for reach, index in ((SCORCH, 0x05), (SCORCH * 0.45, 0x04)):
        field = {v: (reach - dist[v] if v.co.z > Z_TOP - 1.0 else -1.0) for v in bm.verts}
        tops = [f for f in bm.faces if f.normal.z > 0.3 and f.material_index != black_slot]
        faces = split_contour(bm, {"f": field, "d": dist}, "f", 0.0, tops)
        dist = {v: dist[v] if v in dist else hole_distance(v.co.x, v.co.y) for v in bm.verts}
        slot = mk.slot_of(body, g[index])
        for f in faces:
            if f.is_valid and f.normal.z > 0.3 and sum(field.get(v, -1.0) for v in f.verts) / len(f.verts) > 1e-9:
                f.material_index = slot
    bm.to_mesh(body.data)
    bm.free()
    for obj in (body, back):
        k.smooth(obj, 20)
    # torn plates bent up out of the holes
    for i, (c, r, ang, length, width) in enumerate(FLAPS):
        x, y = E(c, r)
        root = Vector((x, y - S(Z_TOP), Z_TOP - 0.15))
        a = math.radians(ang)
        d = Vector((math.cos(a), math.sin(a), 0.0))
        side = Vector((-d.y, d.x, 0.0)) * (width / 2)
        rise = 0.55 + 0.25 * (i % 3)
        tip = root + d * length * math.cos(rise) + Vector((0.0, 0.0, length * math.sin(rise)))
        bm = bmesh.new()
        t = 0.16
        corners = [root - side, root + side, tip + side * 0.6, tip - side * 0.6]
        lo = [bm.verts.new(p) for p in corners]
        up = Vector((0.0, 0.0, t))
        hi = [bm.verts.new(p + up) for p in corners]
        bm.faces.new(lo[::-1])
        bm.faces.new(hi)
        for j in range(4):
            q = (j + 1) % 4
            bm.faces.new((lo[j], lo[q], hi[q], hi[j]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        mesh = bpy.data.meshes.new("flap%d" % i)
        bm.to_mesh(mesh)
        bm.free()
        flap = bpy.data.objects.new("flap%d" % i, mesh)
        bpy.context.scene.collection.objects.link(flap)
        flap.data.materials.append(g[0x0a])
        paint_lit(flap, g[0x0a], g[0x0c], g[0x06], under=g[0x04])
        parts.append(flap)
    # the ember on the larger hole's floor
    x, y = E(*EMBER)
    ember = mk.ball("ember", (x, y - S(HOLE_FLOOR), HOLE_FLOOR + 0.35), (0.9, 0.7, 0.45), m["ember"], 10, 6)
    parts.append(ember)
    for i, (c, r, s) in enumerate(((17.0, 25.5, 0.7), (16.0, 27.0, 0.55), (33.5, 24.0, 0.8), (30.5, 26.5, 0.6),
                                   (35.0, 26.5, 0.55))):
        x, y = E(c, r)
        chunk = mk.ball("scrap%d" % i, (x, y - S(HOLE_FLOOR), HOLE_FLOOR + s * 0.4), (s, s * 0.8, s * 0.55),
                        g[0x04], 8, 4)
        parts.append(chunk)
    for obj in parts:
        mk.apply(obj)
    return parts


# --- Build ----------------------------------------------------------------------------------------------------------

def build_whole(m):
    parts = house(m)
    parts += pod(m)
    parts += dock(m)
    parts += cradle(m)
    for obj in parts:
        mk.apply(obj)
    bpy.context.view_layer.update()
    return parts


def view_coverage(objects, w, h, corner):
    """Which pixels of a w x h window (its top left corner at `corner`, in the objects' coordinates) the game's camera
    sees the objects at, relative to the roof (rows of bools): a ray down its line of sight through each pixel."""
    depsgraph = bpy.context.evaluated_depsgraph_get()
    trees = [BVHTree.FromObject(o, depsgraph) for o in objects]
    d = Vector((0.0, TILT, -1.0)).normalized()
    out = []
    for r in range(h):
        row = []
        for c in range(w):
            x, yv = corner[0] + c + 0.5, corner[1] - (r + 0.5)
            z0 = 140.0
            origin = Vector((x, yv - (z0 - H) * TILT, z0))
            row.append(any(t.ray_cast(origin, d)[0] is not None for t in trees))
        out.append(row)
    return out


def pod_mask(sheets, sprites, rows=3):
    """The sprites' pixels placed as the levels place them (48 x 28 rows each row of two), the floor the sprites paint
    round the house (left of column 4, right of column 42, below row 80) left out."""
    mask = [[False] * 48 for _ in range(28 * rows)]
    for i, sprite in enumerate(sprites):
        part = k.sprite_mask(os.path.join(sheets, "enemy_P.png"), sprite)
        ox, oy = (i % 2) * 24, (i // 2) * 28
        for y in range(28):
            for x in range(24):
                if part[y][x]:
                    mask[oy + y][ox + x] = True
    for r in range(len(mask)):
        for c in range(48):
            if c < 4 or c > 42 or r > 80:
                mask[r][c] = False
    return mask


def pod_piece_mask(sheets, sprite, centre):
    """A piece's sprite's pixels, the floor the sprites paint round the house left out."""
    part = k.sprite_mask(os.path.join(sheets, "enemy_P.png"), sprite)
    c0, r0 = int(centre[0] - 12 + 24), int(56 - centre[1] - 14)
    return [[part[y][x] and 4 <= c0 + x <= 42 and r0 + y <= 80 for x in range(24)] for y in range(28)]


def export(parts, name, options, mask=None, label=""):
    out = mk.outdir(options)
    drop_unused(parts)
    triangulate(parts)
    parts = [join(parts, name)]
    parts[0].data.name = name
    bpy.context.scene.view_settings.view_transform = "Standard"
    mk.report(name, parts, os.path.join(out, name + ".glb"))
    if "preview" in options:
        mk.preview(options["preview"] + name, parts)
    for obj in parts:
        data = obj.data
        bpy.data.objects.remove(obj)
        if data.users == 0:
            bpy.data.meshes.remove(data)


def build():
    options = k.args()
    only = options["only"].split(",") if "only" in options else None
    sheets = options.get("check")
    k.reset()
    m = materials()
    whole = build_whole(m)
    triangulate(whole)
    print("whole cargo pod: %d triangles, %d objects" % (mk.triangles(whole), len(whole)))
    if sheets:
        mk.compare("whole pod as the camera sees it (P 165 167 / 203 205 / 241 243, the floor left out)",
                   view_coverage(whole, 48, 84, E(0, 0)), pod_mask(sheets, [165, 167, 203, 205, 241, 243]))
    if "whole" in options:
        mk.export(whole, options["whole"] + "cargo_pod.glb")
    cap = m["grey"][0x03]

    def pieces(whole, specs):
        for name, sprite, box, centre in specs:
            if only and name not in only:
                continue
            parts = [p for p in (view_cut(src, box, cap, H) for src in whole) if p is not None]
            mk.transform(parts, Matrix.Translation((-centre[0], -centre[1], 0.0)))
            bpy.context.view_layer.update()
            for src in whole:
                src.hide_render = True
            if sheets:
                mk.compare("%s (P %d) as the camera sees it" % (name, sprite),
                           view_coverage(parts, 24, 28, (-12.0, 14.0)), pod_piece_mask(sheets, sprite, centre))
            export(parts, name, options)
            for src in whole:
                src.hide_render = False
    pieces(whole, PIECES)
    if only and not any(name in only for name, _, _, _ in WRECK_PIECES):
        return
    # the wreck: the intact pod again, its back end blown open, cut the same way
    k.reset()
    m = materials()
    cap = m["grey"][0x03]
    whole = wreck(build_whole(m), m)
    triangulate(whole)
    print("whole wreck: %d triangles" % mk.triangles(whole))
    if "whole" in options:
        mk.export(whole, options["whole"] + "cargo_pod_wreck.glb")
    pieces(whole, WRECK_PIECES)


if __name__ == "__main__":
    build()
