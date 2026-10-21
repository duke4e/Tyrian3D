"""The anchor the maces' chains hang from in GAUNTLET and MACES (sheet A sprites 83 and 85 above 121 and 123, 2x2 each:
one 48 x 56 picture; ground layer; one frame each), polished (2026-10-20; it replaces wave3_q_mace.py's anchor_whole(),
a heightfield block painted from the sprite with a ball and two tori). models.cfg: model mace_anchor_tl / _tr / _bl /
_br ... origin (unchanged); sprite a 83 mace_anchor_tl yaw=0, sprite a 85 mace_anchor_tr yaw=0, sprite a 121
mace_anchor_bl yaw=0, sprite a 123 mace_anchor_br yaw=0 (unchanged: no height=-4, so that the ball stays at the height
of the chain's rings, CHAIN_Z, which hang from it; the walls reach SKIRT under the anchor's foot instead). The levels
put the four together as the sheet does (83 at (x, y - 28), 85 at (x + 24, y - 28), 121 at (x, y), 123 at (x + 24,
y)). None of the four is another sprite's pixels mirrored or in other ramps. No 4x upscale of these sprites exists:
modelled from the original pixels.

As the sprites draw it (columns and rows of the 48 x 56 picture; tans of ramp 1, greys of ramp 0): a heavy block of
wood (columns 9-39 of rows 13-52), split down the middle (a notch in its back edge at columns 21-24, a dark line down
its front at column 21, and right of it a darker recessed strip, columns 22-26); its top (rows 14-40) light, grained
across the screen, a plank's lit edge at row 33 and a seam at row 32, its back corners rounded, its left edge lit
(column 13); its front (rows 41-51) darker, boards across the screen. On its top a dark steel ball (columns 16-29 of
rows 19-31, a white glare at its upper left, columns 20-21 of rows 22-23) sits in a socket whose lit steel rim shows
under its front (rows 29-33), the ball's shadow falling on the wood at its lower right.

Built as such a block of timber: each half a core (a prism of its plan, its front a slope from the top's edge down to
the ground, so that the slanted camera sees it as the sprites draw it) under three planks across its top and four
boards down its front, each plank a little askew (raised or sunk a tenth of a pixel, tilted), gaps between them,
their edges rounded and lit towards the sun; their grain strips across the screen cut into each plank (bisected) and
painted in the sprite's tans; the recessed strip cut down the right half's boards; under it all the walls reach SKIRT
under the foot. The ball is an icosphere painted in the sprite's greys (a dark rim where it turns away, the glare in
bands: polish_balls.painted_ball; a little emission in its own grey, since balls the slanted camera sees read near
black), sunk into the top with its middle at CHAIN_Z, a steel collar round it. Built whole and cut along the sprites'
edges (polish_arch.py's cut(): the pieces keep the whole's shading across the cuts), each piece moved so its sprite's
centre is its origin.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the ground (z = 0); P(c, r)
turns a pixel edge of the picture (column c, row r) into the whole's coordinates (x = c - 24, y = 28 - r).

Replaces wave3_q_mace.py's anchor: remove ANCHOR_ORIGIN, CRATE_H, CRATE_FRONT, JOINT, anchor_whole() (its
@q.whole("anchor", (48, 56)) registration), ANCHOR_PIECES with its loop and place_pieces("anchor", ...), and the
mace_anchor lines of its docstring; wave3_q_art.py's ANCHOR (nothing else reads it). steel(), wood(), shade_paint()
and place_pieces() stay (the mace and the skull chest use them).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes of the whole
and of each piece against enemy_A.png), --preview <prefix> (the whole's and each piece's top and 3/4 views),
--only <model,...>.
"""
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_arch import cut, plane_box  # noqa: E402  (cut: polish_machine_kit.cut without its material indices
#                                                      shifted twice)
from polish_balls import Ellipsoid, painted_ball  # noqa: E402

# The pieces: (name, sprite, the box it covers in the whole's coordinates (x0, x1, y0, y1)).
PIECES = [("mace_anchor_tl", 83, (-24.0, 0.0, 0.0, 28.0)), ("mace_anchor_tr", 85, (0.0, 24.0, 0.0, 28.0)),
          ("mace_anchor_bl", 121, (-24.0, 0.0, -28.0, 0.0)), ("mace_anchor_br", 123, (0.0, 24.0, -28.0, 0.0))]
SPRITE_AT = {83: (0, 0), 85: (24, 0), 121: (0, 28), 123: (24, 28)}  # top left corners in the picture


def P(c, r):
    """A pixel edge of the 48 x 56 picture (column c, row r) in the whole's coordinates."""
    return (c - 24.0, 28.0 - r)


def X(c):
    return c - 24.0


def Y(r):
    return 28.0 - r


CHAIN_Z = 14.0               # the chain rings' height (polish_chain_ring.py): the ball's middle
SKIRT = -4.0                 # how far the walls reach under the foot
TOP = 11.0                   # the top
TOP_EDGE, FOOT = 40.8, 52.6  # the front: from the top's edge (row) down to the ground
BACK, L_EDGE, R_EDGE = 13.1, 9.2, 39.8   # the back edge (row), the sides (columns)
CORNER = 4.0                 # the back corners' radius
# The halves' plans (pixel edges): the split between them, the notch in the back edge.
LEFT = [(L_EDGE, FOOT - 1.3), (L_EDGE, BACK + CORNER), "corner_l", (20.6, BACK), (21.3, 14.7), (21.3, FOOT),
        (L_EDGE + 1.3, FOOT)]
RIGHT = [(21.8, 14.7), (24.9, BACK), "corner_r", (R_EDGE, BACK + CORNER), (R_EDGE, FOOT - 1.3), (R_EDGE - 1.3, FOOT),
         (21.8, FOOT)]
PLANKS = [BACK, 20.6, 32.7, TOP_EDGE]           # the top's planks (rows of their edges)
BOARDS = [TOP_EDGE, 43.8, 46.8, 49.7, FOOT]      # the front's boards
SEAM_W = 0.36                                    # the gaps between the planks and between the boards
PLANK_T, BOARD_T = 1.2, 1.2                      # their thickness
STRIP = (22.3, 26.7, 0.8)                        # the recessed strip down the right half's front: columns, depth
# The ball: its middle (pixel edges: column, row), radii (across, up the screen, height); the glare (its middle's
# offset from the ball's, seen from above, and half-size); the collar round it.
BALL_AT, BALL_R = (23.0, 25.5), (7.0, 7.0, 6.6)
GLARE_AT, GLARE_SIZE = (-2.0, 2.5), 1.55
COLLAR = (6.55, 0.95, 0.8)   # major radius, minor radius, squash in height


def materials():
    def wood(name, index, roughness=0.78):
        return k.material(name, palette=index, metallic=0.0, roughness=roughness)

    def steel(name, index, metallic=0.6, roughness=0.3):
        return k.material(name, palette=index, metallic=metallic, roughness=roughness)
    front = wood("anchor_front", 0x17)
    return {
        "seam": wood("anchor_seam", 0x12, 0.85),
        "front": front,
        "front2": wood("anchor_front2", 0x16),
        "front3": wood("anchor_front3", 0x18),
        "side": front,                      # (the same shade: one material)
        "plank": wood("anchor_plank", 0x1b),
        "plank2": wood("anchor_plank2", 0x1a),
        "plank3": wood("anchor_plank3", 0x1c),
        "lit": wood("anchor_lit", 0x1d, 0.7),
        "collar": steel("anchor_collar", 0x0a, 0.65, 0.28),
        "ball_rim": steel("anchor_ball_rim", 0x03, 0.5, 0.45),
        "ball": k.material("anchor_ball", palette=0x08, metallic=0.5, roughness=0.22, emission=k.level_palette()[0x08],
                           emission_strength=0.12),     # (balls the slanted camera sees read near black)
        "glare": steel("anchor_glare", 0x0b, 0.3, 0.15),
        "glare_mid": steel("anchor_glare_mid", 0x0d, 0.2, 0.12),
        "glare_core": steel("anchor_glare_core", 0x0f, 0.1, 0.1),
    }


# --- Helpers --------------------------------------------------------------------------------------------------------

def outline(points):
    """Pixel-edge points (c, r), with "corner_l" / "corner_r" standing for the back corners' arcs, to the whole's
    (x, y), counter-clockwise seen from above."""
    pts = []
    for p in points:
        if p == "corner_l":      # from the left side up round to the back edge
            cx, cr = L_EDGE + CORNER, BACK + CORNER
            for i in range(1, 8):
                a = math.radians(180 + 90 * i / 8)
                pts.append(P(cx + CORNER * math.cos(a), cr + CORNER * math.sin(a)))
        elif p == "corner_r":    # from the back edge round to the right side
            cx, cr = R_EDGE - CORNER, BACK + CORNER
            for i in range(1, 8):
                a = math.radians(270 + 90 * i / 8)
                pts.append(P(cx + CORNER * math.cos(a), cr + CORNER * math.sin(a)))
        else:
            pts.append(P(*p))
    area = sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(pts, pts[1:] + pts[:1]))
    return pts if area > 0 else pts[::-1]


def front_z(y):
    """The front's slope: TOP at the top's edge, 0 at the foot."""
    return TOP * (y - Y(FOOT)) / (Y(TOP_EDGE) - Y(FOOT))


FRONT_N = Vector((0.0, -TOP, Y(TOP_EDGE) - Y(FOOT))).normalized()   # out of the front, down the screen and up


def front_cutter(name, c0, c1, r0, r1, depth):
    """A prism along x cutting depth into the front between rows r0 and r1 (columns c0-c1)."""
    ya, yb = Y(r0), Y(r1)
    pa, pb = Vector((0.0, ya, front_z(ya))), Vector((0.0, yb, front_z(yb)))
    profile = [tuple((pa - FRONT_N * depth).yz), tuple((pa + FRONT_N * 3.0).yz), tuple((pb + FRONT_N * 3.0).yz),
               tuple((pb - FRONT_N * depth).yz)]
    return mk.prism(name, profile, X(c0), X(c1), axis="x")


# --- The parts ------------------------------------------------------------------------------------------------------

def plane_above(name, bottom, size=60.0):
    """Everything over the plane z = bottom(x, y) (a thick slab along it), for intersecting with."""
    return mk.wedge(name, [(-size, -size), (size, -size), (size, size), (-size, size)], 0.0,
                    lambda x, y: bottom(x, y) + 400.0, bottom=bottom)


def grain(obj, rows, shades, rng, sloped=False):
    """Splits a plank's faces into strips across the screen (the grain, between rows: pixel edges) and paints its
    top (or its front, sloped) strip by strip in shades drawn from shades."""
    r0, r1 = rows
    cuts, r = [], r0 + rng.uniform(0.3, 0.9)
    while r < r1 - 0.25:
        cuts.append(r)
        r += rng.uniform(0.45, 1.4)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    for rc in cuts:
        bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-5, plane_co=(0, Y(rc), 0),
                               plane_no=(0, 1, 0))
    bm.to_mesh(obj.data)
    bm.free()
    bands = [rng.choice(shades) for _ in range(len(cuts) + 1)]

    def pick(c, n):
        facing = (n.y < -0.3 and n.z > 0.2) if sloped else n.z > 0.9
        if not facing:
            return None
        rr = 28.0 - c.y
        return bands[sum(rr > rc for rc in cuts)]
    mk.paint(obj, pick)


def half(name, plan, m, rng, strip=False):
    """A half of the block: a core under its planks and boards; on its top three planks across the screen, on its
    front (a slope down to the ground) four boards, each a little askew, grained; the recessed strip down its front
    (strip)."""
    shape = outline(plan)
    sink = BOARD_T / FRONT_N.z            # the board's thickness, measured straight down
    core = mk.prism(name + "_core", shape, SKIRT, TOP - PLANK_T, m["seam"])
    mk.boolean(core, plane_box(name + "_core_front", lambda x, y: front_z(y) - sink), "INTERSECT")
    mk.cleanup(core)
    mk.bevel(core, 0.3, 1, 30)
    mk.shade(core, 35)
    cs = [c for c, r in (p for p in plan if not isinstance(p, str))]
    c0, c1 = min(cs) - 1.0, max(cs) + 1.0
    xm = X((c0 + c1) / 2)
    tops = [m["plank"], m["plank2"], m["plank3"]]
    fronts = [m["front"], m["front2"], m["front3"]]
    gap = SEAM_W / 2
    for i, (ra, rb) in enumerate(zip(PLANKS, PLANKS[1:])):
        lift, tilt = rng.uniform(-0.12, 0.14), rng.uniform(-0.012, 0.012)
        plank = mk.wedge(f"{name}_plank{i}", shape, TOP - PLANK_T - 0.3,
                         lambda x, y, lift=lift, tilt=tilt: TOP + lift + tilt * (x - xm), m["plank"])
        ya = Y(ra + (gap if i > 0 else -1.0))
        yb = Y(rb - (gap if i < len(PLANKS) - 2 else 0.0))
        mk.boolean(plank, mk.box(f"{name}_plank{i}_band", X(c0), X(c1), yb, ya, SKIRT - 1.0, TOP + 3.0), "INTERSECT")
        if i == len(PLANKS) - 2:          # the last one ends on the front's slope
            mk.boolean(plank, plane_box(f"{name}_plank{i}_front", lambda x, y: front_z(y) + 0.6), "INTERSECT")
        mk.cleanup(plank)
        grain(plank, (ra, rb), tops, rng)
        mk.bevel(plank, 0.32, 2, 30)
        mk.shade(plank, 35)
        mk.paint(plank, lambda c, n: (m["lit"] if (n.y > 0.25 or n.x < -0.25) else m["side"])
                 if 0.25 < n.z < 0.9 else m["side"] if n.z <= 0.25 else None)
    for j, (ra, rb) in enumerate(zip(BOARDS, BOARDS[1:])):
        lift = rng.uniform(-0.1, 0.16)
        board = mk.prism(f"{name}_board{j}", shape, SKIRT - 1.0, TOP + 2.0, m["front"])
        mk.boolean(board, plane_box(f"{name}_board{j}_top", lambda x, y, lift=lift: front_z(y) + lift), "INTERSECT")
        mk.boolean(board, plane_above(f"{name}_board{j}_back", lambda x, y: front_z(y) - sink - 0.4), "INTERSECT")
        ya = Y(ra + (gap if j > 0 else 0.15))
        yb = Y(rb - (gap if j < len(BOARDS) - 2 else -2.0))
        mk.boolean(board, mk.box(f"{name}_board{j}_band", X(c0), X(c1), yb, ya, SKIRT - 2.0, TOP + 3.0), "INTERSECT")
        if strip:
            s0, s1, depth = STRIP
            mk.boolean(board, front_cutter(f"{name}_board{j}_strip", s0, s1, TOP_EDGE - 0.5, FOOT + 3.0, depth),
                       "DIFFERENCE")
        mk.cleanup(board)
        grain(board, (ra, rb), fronts, rng, sloped=True)
        mk.bevel(board, 0.28, 2, 30)
        mk.shade(board, 35)

        def board_pick(c, n):
            if strip and X(STRIP[0]) - 0.05 < c.x < X(STRIP[1]) + 0.05 and c.z < front_z(c.y) - 0.3 * STRIP[2]:
                return m["seam"]               # the recessed strip
            if 0.25 < n.z and not (n.y < -0.3 and n.z > 0.2) and n.z < 0.9:
                return m["lit"] if (n.y > 0.25 or n.x < -0.25) else m["side"]
            if n.z <= 0.25 and not (n.y < -0.3):
                return m["side"]
            return None
        mk.paint(board, board_pick)
    return core


def ball(m):
    """The steel ball, its middle at the chains' height: a dark rim where it turns away, the glare in bands."""
    c = Vector((X(BALL_AT[0]), Y(BALL_AT[1]), CHAIN_Z))
    shape = Ellipsoid(c, BALL_R)
    gx, gy = c.x + GLARE_AT[0], c.y + GLARE_AT[1]

    def rim(p, n):
        return n.z

    def glare(p, n):
        if n.z <= 0.3:
            return 0.0
        return math.exp(-(((p.x - gx) / GLARE_SIZE) ** 2 + ((p.y - gy) / GLARE_SIZE) ** 2))
    paint = [(rim, (0.28,), ("ball_rim", "ball")),
             (glare, (0.22, 0.45, 0.72), (None, "glare", "glare_mid", "glare_core"))]
    obj = painted_ball("ball", shape, paint, m, subdivisions=4)
    # The collar of the socket round it, on the top.
    collar = mk.tube("collar", [(c.x + COLLAR[0] * math.cos(2 * math.pi * i / 48),
                                 c.y + COLLAR[0] * math.sin(2 * math.pi * i / 48), TOP + 0.25) for i in range(49)],
                     COLLAR[1], m["collar"], 12)
    for v in collar.data.vertices:        # flattened a little: a ring lying on the wood
        v.co.z = TOP + 0.25 + (v.co.z - TOP - 0.25) * COLLAR[2]
    k.smooth(collar, 60)
    mk.paint(collar, lambda cc, n: m["ball_rim"] if n.z < -0.2 else None)
    return obj


# --- Build ----------------------------------------------------------------------------------------------------------

def build_whole(m):
    rng = random.Random(83)
    half("left", LEFT, m, rng)
    half("right", RIGHT, m, rng, strip=True)
    ball(m)
    whole = mk.meshes()
    for obj in whole:
        mk.apply(obj)
    bpy.context.view_layer.update()
    return whole


def whole_mask(sheet):
    mask = [[False] * 48 for _ in range(56)]
    for sprite, (c0, r0) in SPRITE_AT.items():
        part = k.sprite_mask(sheet, sprite)
        for y in range(28):
            for x in range(24):
                if part[y][x]:
                    mask[r0 + y][c0 + x] = True
    return mask


def build():
    options = k.args()
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    k.reset()
    m = materials()
    whole = build_whole(m)
    print("whole anchor: %d triangles, %d objects" % (mk.triangles(whole), len(whole)))
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    sheet = os.path.join(options["check"], "enemy_A.png") if "check" in options else None
    if sheet:
        mk.compare("whole (A 83 + 85 above 121 + 123)", mk.coverage(whole, 48, 56), whole_mask(sheet))
    if "preview" in options:
        mk.preview(options["preview"] + "mace_anchor_whole", whole, size=(48, 56), scale=8, distance=1.8)
    for name, sprite, box in PIECES:
        if only and name not in only:
            continue
        pieces = [p for p in (cut(src, box, m["seam"]) for src in whole) if p is not None]
        mk.transform(pieces, Matrix.Translation((-(box[0] + box[1]) / 2, -(box[2] + box[3]) / 2, 0)))
        bpy.context.view_layer.update()
        for src in whole:
            src.hide_render = True
        if sheet:
            mk.compare("%s (A %d)" % (name, sprite), mk.coverage(pieces, 24, 28), k.sprite_mask(sheet, sprite))
        mk.report(name, pieces, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, pieces)
        for obj in pieces:
            bpy.data.objects.remove(obj)
        for src in whole:
            src.hide_render = False


if __name__ == "__main__":
    build()
